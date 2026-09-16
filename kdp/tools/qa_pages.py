#!/usr/bin/env python3
"""Quality checks for colouring-book line art before it goes into the book.

Requires Pillow. Everything else is standard library.

Usage:
    python3 qa_pages.py --self-test
    python3 qa_pages.py kdp/pages/approved
    python3 qa_pages.py kdp/pages/approved --json
    python3 qa_pages.py one_page.png

Exit status 0 when every page passes, 1 when any page fails, 2 on a usage
problem. Warnings do not change the exit status.

These checks catch the mechanical failures. They cannot see that an owl has
three legs, so a human still reviews every page.

Checks, per page:

  RESOLUTION   The image must reach 300 DPI at its placed size on the page.
  GREYSCALE    Line art is black on white. A little grey at the edges of
               strokes is normal anti-aliasing; large grey areas are shading,
               which cannot be coloured over.
  INK          Ink coverage must sit in a sensible band. Far too little means a
               near-blank page, far too much means a heavy or filled-in page.
  BORDER       A white margin must surround the art, so nothing collides with
               the page margin or crosses the trim.
  CLOSURE      White reachable from the border by flood fill is background.
               Enclosed white regions are colourable. If almost nothing is
               enclosed, the outlines are open and colour will leak.
  REGIONS      Enclosed regions must be countable and large enough to colour.
  DUPLICATES   No two pages may be near-identical (perceptual hash distance).
"""

import argparse
import json
import os
import sys
from collections import deque

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("Pillow is required: pip3 install pillow", file=sys.stderr)
    raise SystemExit(2)

# ---------------------------------------------------------------- thresholds

# The book's page geometry. Keep in step with build_interior.py.
PLACED_W_IN = 7.125
PLACED_H_IN = 9.5
MIN_DPI = 300

# A pixel is "ink" at or below this, "paper" at or above the other.
INK_MAX = 100
PAPER_MIN = 200

DEFAULTS = {
    # Share of pixels allowed to be mid-grey (anti-aliasing lives here).
    "max_grey_fraction": 0.06,
    # Ink coverage band, as a share of all pixels.
    "min_ink_fraction": 0.02,
    "max_ink_fraction": 0.35,
    # White border required around the art, as a share of the short edge.
    "border_fraction": 0.015,
    # Of all paper pixels, at least this share must be enclosed rather than
    # reachable from the border. Low values mean outlines are open.
    "min_enclosed_share": 0.25,
    # Colourable regions per page.
    "min_regions": 8,
    "max_regions": 400,
    # Smallest colourable region, in millimetres of equivalent width.
    "min_region_mm": 4.0,
    # Ignore specks below this many pixels when counting regions.
    "speck_px": 64,
    # Perceptual hash distance below which two pages are "near-duplicates".
    "dup_distance": 6,
}

MM_PER_INCH = 25.4


class Finding(object):
    def __init__(self, page, check, severity, message):
        self.page = page
        self.check = check
        self.severity = severity  # "error" or "warning"
        self.message = message

    def as_dict(self):
        return {"page": self.page, "check": self.check,
                "severity": self.severity, "message": self.message}

    def __repr__(self):
        return "%s %s %s: %s" % (self.severity.upper(), self.page, self.check, self.message)


# ---------------------------------------------------------------- primitives

def load_grey(path):
    img = Image.open(path)
    if img.mode != "L":
        img = img.convert("L")
    return img


def classify(img, ink_max=INK_MAX, paper_min=PAPER_MIN):
    """Return (width, height, ink_mask, paper_mask) as flat bytearrays."""
    w, h = img.size
    px = img.tobytes()
    ink = bytearray(w * h)
    paper = bytearray(w * h)
    grey = 0
    for i, v in enumerate(px):
        if v <= ink_max:
            ink[i] = 1
        elif v >= paper_min:
            paper[i] = 1
        else:
            grey += 1
    return w, h, ink, paper, grey


def flood_from_border(w, h, paper):
    """Mark paper pixels reachable from the image border (4-connected).

    Returns a bytearray where 1 = background (outside the art).
    """
    seen = bytearray(w * h)
    q = deque()

    def push(x, y):
        i = y * w + x
        if paper[i] and not seen[i]:
            seen[i] = 1
            q.append(i)

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)

    while q:
        i = q.popleft()
        x = i % w
        y = i // w
        if x > 0:
            j = i - 1
            if paper[j] and not seen[j]:
                seen[j] = 1
                q.append(j)
        if x < w - 1:
            j = i + 1
            if paper[j] and not seen[j]:
                seen[j] = 1
                q.append(j)
        if y > 0:
            j = i - w
            if paper[j] and not seen[j]:
                seen[j] = 1
                q.append(j)
        if y < h - 1:
            j = i + w
            if paper[j] and not seen[j]:
                seen[j] = 1
                q.append(j)
    return seen


def enclosed_regions(w, h, paper, background, speck_px):
    """Sizes of white regions not reachable from the border."""
    seen = bytearray(w * h)
    sizes = []
    for start in range(w * h):
        if not paper[start] or background[start] or seen[start]:
            continue
        seen[start] = 1
        q = deque([start])
        size = 0
        while q:
            i = q.popleft()
            size += 1
            x = i % w
            y = i // w
            if x > 0:
                j = i - 1
                if paper[j] and not background[j] and not seen[j]:
                    seen[j] = 1
                    q.append(j)
            if x < w - 1:
                j = i + 1
                if paper[j] and not background[j] and not seen[j]:
                    seen[j] = 1
                    q.append(j)
            if y > 0:
                j = i - w
                if paper[j] and not background[j] and not seen[j]:
                    seen[j] = 1
                    q.append(j)
            if y < h - 1:
                j = i + w
                if paper[j] and not background[j] and not seen[j]:
                    seen[j] = 1
                    q.append(j)
        if size >= speck_px:
            sizes.append(size)
    return sizes


def ahash(img, size=16):
    """Average hash, as an integer. Small and good enough for near-duplicates."""
    small = img.resize((size, size), Image.BILINEAR)
    px = small.tobytes()
    mean = sum(px) / float(len(px))
    bits = 0
    for i, v in enumerate(px):
        if v >= mean:
            bits |= (1 << i)
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


# ---------------------------------------------------------------- the checks

def check_page(path, cfg=None, downscale_to=1200):
    """Run every per-page check. Returns (findings, stats)."""
    cfg = dict(DEFAULTS, **(cfg or {}))
    name = os.path.basename(path)
    findings = []

    img = load_grey(path)
    full_w, full_h = img.size

    # RESOLUTION, measured on the real pixel dimensions.
    dpi_w = full_w / PLACED_W_IN
    dpi_h = full_h / PLACED_H_IN
    dpi = min(dpi_w, dpi_h)
    if dpi < MIN_DPI:
        findings.append(Finding(
            name, "RESOLUTION", "error",
            "%dx%d gives %.0f DPI at %.3f x %.3f in; %d DPI is the minimum"
            % (full_w, full_h, dpi, PLACED_W_IN, PLACED_H_IN, MIN_DPI)))

    aspect = full_w / float(full_h)
    want = PLACED_W_IN / PLACED_H_IN
    if abs(aspect - want) > 0.02:
        findings.append(Finding(
            name, "ASPECT", "warning",
            "aspect %.3f differs from the %.3f page area, so the image will be "
            "cropped or letterboxed" % (aspect, want)))

    # Everything else runs on a downscaled copy: the geometry is the same and
    # a 4k page would otherwise take minutes in pure Python.
    scale = 1.0
    if max(full_w, full_h) > downscale_to:
        scale = downscale_to / float(max(full_w, full_h))
        img_s = img.resize((max(1, int(full_w * scale)), max(1, int(full_h * scale))),
                           Image.LANCZOS)
    else:
        img_s = img

    w, h, ink, paper, grey = classify(img_s)
    total = w * h

    grey_fraction = grey / float(total)
    ink_fraction = sum(ink) / float(total)

    # GREYSCALE. Downscaling adds anti-aliasing of its own, so the threshold is
    # relaxed in proportion to how much we shrank the image.
    grey_budget = cfg["max_grey_fraction"] * (1.0 + (1.0 - scale) * 2.0)
    if grey_fraction > grey_budget:
        findings.append(Finding(
            name, "GREYSCALE", "error",
            "%.1f%% of pixels are mid-grey (budget %.1f%%): the page carries "
            "shading or texture rather than pure line art"
            % (grey_fraction * 100, grey_budget * 100)))

    # INK
    if ink_fraction < cfg["min_ink_fraction"]:
        findings.append(Finding(
            name, "INK", "error",
            "ink coverage %.2f%% is below %.2f%%: the page is nearly blank"
            % (ink_fraction * 100, cfg["min_ink_fraction"] * 100)))
    elif ink_fraction > cfg["max_ink_fraction"]:
        findings.append(Finding(
            name, "INK", "error",
            "ink coverage %.2f%% is above %.2f%%: the page is too heavy to colour"
            % (ink_fraction * 100, cfg["max_ink_fraction"] * 100)))

    # BORDER
    band = max(1, int(min(w, h) * cfg["border_fraction"]))
    touching = 0
    for y in range(h):
        for x in range(w):
            if x < band or x >= w - band or y < band or y >= h - band:
                if ink[y * w + x]:
                    touching += 1
    if touching > band * 4:
        findings.append(Finding(
            name, "BORDER", "error",
            "%d ink pixels sit in the outer %d-pixel border: the art reaches the "
            "image edge and will collide with the page margin" % (touching, band)))

    # CLOSURE and REGIONS
    background = flood_from_border(w, h, paper)
    paper_total = sum(paper)
    bg_total = sum(background)
    enclosed_total = paper_total - bg_total
    enclosed_share = (enclosed_total / float(paper_total)) if paper_total else 0.0

    sizes = enclosed_regions(w, h, paper, background, cfg["speck_px"])
    region_count = len(sizes)

    if enclosed_share < cfg["min_enclosed_share"]:
        findings.append(Finding(
            name, "CLOSURE", "error",
            "only %.1f%% of white is enclosed (minimum %.1f%%): outlines are open, "
            "so colour will leak between shapes"
            % (enclosed_share * 100, cfg["min_enclosed_share"] * 100)))

    if region_count < cfg["min_regions"]:
        findings.append(Finding(
            name, "REGIONS", "error",
            "%d colourable regions is below the minimum of %d"
            % (region_count, cfg["min_regions"])))
    elif region_count > cfg["max_regions"]:
        findings.append(Finding(
            name, "REGIONS", "warning",
            "%d colourable regions is above %d: the page may be denser than the "
            "medium-detail brief" % (region_count, cfg["max_regions"])))

    # Region size, converted back to millimetres at print size.
    px_per_mm = (full_w / (PLACED_W_IN * MM_PER_INCH)) * scale
    min_area_px = (cfg["min_region_mm"] * px_per_mm) ** 2
    tiny = [s for s in sizes if s < min_area_px]
    if tiny and region_count:
        share = len(tiny) / float(region_count)
        severity = "error" if share > 0.25 else "warning"
        findings.append(Finding(
            name, "REGIONS", severity,
            "%d of %d regions are smaller than %.1f mm across and cannot be "
            "coloured" % (len(tiny), region_count, cfg["min_region_mm"])))

    stats = {
        "page": name,
        "pixels": [full_w, full_h],
        "dpi_at_placed_size": round(dpi, 1),
        "grey_fraction": round(grey_fraction, 5),
        "ink_fraction": round(ink_fraction, 5),
        "enclosed_share": round(enclosed_share, 4),
        "regions": region_count,
        "regions_too_small": len(tiny),
        "hash": ahash(img_s),
    }
    return findings, stats


def check_duplicates(stats_list, cfg=None):
    cfg = dict(DEFAULTS, **(cfg or {}))
    findings = []
    for i in range(len(stats_list)):
        for j in range(i + 1, len(stats_list)):
            d = hamming(stats_list[i]["hash"], stats_list[j]["hash"])
            if d <= cfg["dup_distance"]:
                findings.append(Finding(
                    stats_list[j]["page"], "DUPLICATES", "error",
                    "is a near-duplicate of %s (hash distance %d)"
                    % (stats_list[i]["page"], d)))
    return findings


def check_folder(path, cfg=None):
    if os.path.isfile(path):
        paths = [path]
    else:
        paths = [os.path.join(path, n) for n in sorted(os.listdir(path))
                 if n.lower().endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff"))]
    findings = []
    stats_list = []
    for p in paths:
        f, s = check_page(p, cfg)
        findings.extend(f)
        stats_list.append(s)
    findings.extend(check_duplicates(stats_list, cfg))
    return findings, stats_list


# ---------------------------------------------------------------- self-test

def _draw_page(w=2138, h=2850, kind="good"):
    """Build a synthetic page with a known defect (or none)."""
    from PIL import ImageDraw
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    stroke = max(6, w // 240)
    margin = int(min(w, h) * 0.08)

    if kind == "blank":
        return img

    if kind == "shaded":
        # A large mid-grey block: shading, which must be rejected.
        d.rectangle([margin, margin, w - margin, h // 2], fill=128)

    if kind == "edge":
        # Ink running along the very edge of the image.
        d.rectangle([0, 0, w - 1, h - 1], outline=0, width=stroke)

    # A grid of closed cells: the "good" page.
    cols, rows = (4, 5) if kind != "dense" else (14, 18)
    cw = (w - 2 * margin) / cols
    ch = (h - 2 * margin) / rows
    for r in range(rows):
        for c in range(cols):
            x0 = margin + c * cw
            y0 = margin + r * ch
            d.rectangle([x0, y0, x0 + cw, y0 + ch], outline=0, width=stroke)

    if kind == "open":
        # Erase one side of every cell so nothing is enclosed.
        for r in range(rows):
            for c in range(cols):
                x0 = margin + c * cw
                y0 = margin + r * ch
                d.rectangle([x0 + stroke, y0 - stroke, x0 + cw - stroke, y0 + stroke],
                            fill=255)
        d.rectangle([margin - stroke * 2, margin - stroke * 2,
                     w - margin + stroke * 2, margin + stroke], fill=255)

    if kind == "heavy":
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0:
                    x0 = margin + c * cw
                    y0 = margin + r * ch
                    d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=0)

    return img


def self_test():
    import tempfile
    failures = []

    def codes(findings, severity=None):
        return set(f.check for f in findings
                   if severity is None or f.severity == severity)

    with tempfile.TemporaryDirectory() as tmp:
        cases = {
            "good": set(),
            "blank": {"INK"},
            "shaded": {"GREYSCALE"},
            "open": {"CLOSURE"},
            "edge": {"BORDER"},
            "heavy": {"INK"},
        }
        for kind, expected in cases.items():
            p = os.path.join(tmp, "%s.png" % kind)
            _draw_page(kind=kind).save(p)
            findings, stats = check_page(p)
            got = codes(findings, "error")
            if kind == "good":
                if got:
                    failures.append("a clean page should pass, got: %s"
                                    % "; ".join(f.message for f in findings
                                               if f.severity == "error"))
            else:
                missing = expected - got
                if missing:
                    failures.append("%s page: expected error(s) %s, got %s"
                                    % (kind, sorted(missing), sorted(got) or "none"))

        # RESOLUTION fires on a small image.
        small = os.path.join(tmp, "small.png")
        _draw_page(w=800, h=1066).save(small)
        findings, _ = check_page(small)
        if "RESOLUTION" not in codes(findings, "error"):
            failures.append("an 800px-wide page should fail RESOLUTION")

        # A correctly sized page must not fire RESOLUTION.
        findings, stats = check_page(os.path.join(tmp, "good.png"))
        if "RESOLUTION" in codes(findings):
            failures.append("a 2138x2850 page should pass RESOLUTION")
        if stats["dpi_at_placed_size"] < 300:
            failures.append("expected at least 300 DPI, got %s"
                            % stats["dpi_at_placed_size"])
        if stats["regions"] < 8:
            failures.append("the grid page should expose at least 8 regions, got %d"
                            % stats["regions"])

        # DUPLICATES fires on two copies of one page.
        dup_dir = os.path.join(tmp, "dups")
        os.makedirs(dup_dir)
        img = _draw_page(kind="good")
        img.save(os.path.join(dup_dir, "a.png"))
        img.save(os.path.join(dup_dir, "b.png"))
        findings, _ = check_folder(dup_dir)
        if "DUPLICATES" not in codes(findings, "error"):
            failures.append("two identical pages should fail DUPLICATES")

        # Two genuinely different pages must not.
        ok_dir = os.path.join(tmp, "ok")
        os.makedirs(ok_dir)
        _draw_page(kind="good").save(os.path.join(ok_dir, "a.png"))
        _draw_page(kind="dense").save(os.path.join(ok_dir, "b.png"))
        findings, _ = check_folder(ok_dir)
        if "DUPLICATES" in codes(findings, "error"):
            failures.append("two different pages should not be flagged as duplicates")

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("qa_pages.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Quality checks for colouring-book line art.")
    ap.add_argument("path", nargs="?", help="a page image or a folder of pages")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.path:
        ap.error("give a page, a folder, or --self-test")
        return 2
    if not os.path.exists(args.path):
        print("no such path: %s" % args.path, file=sys.stderr)
        return 2

    findings, stats = check_folder(args.path)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if args.json:
        print(json.dumps({"ok": not errors,
                          "findings": [f.as_dict() for f in findings],
                          "stats": stats}, indent=2))
    else:
        if not stats:
            print("no page images found in %s" % args.path)
            return 2
        for s in stats:
            print("%-28s %5dx%-5d %6.0f DPI  ink %5.2f%%  regions %3d"
                  % (s["page"], s["pixels"][0], s["pixels"][1],
                     s["dpi_at_placed_size"], s["ink_fraction"] * 100, s["regions"]))
        print("")
        for f in warnings:
            print("WARN  %s [%s] %s" % (f.page, f.check, f.message))
        for f in errors:
            print("ERROR %s [%s] %s" % (f.page, f.check, f.message))
        print("")
        print("%d page(s), %d error(s), %d warning(s)" % (len(stats), len(errors), len(warnings)))
        if not errors:
            print("Mechanical checks passed. A human still reviews every page for "
                  "anatomy, symmetry and colouring comfort.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
