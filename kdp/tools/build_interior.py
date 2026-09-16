#!/usr/bin/env python3
"""Build the print-ready interior PDF for the colouring book.

Requires Pillow and reportlab. Geometry comes from cover_spec.py so there is one
source of truth for the page layout.

Usage:
    python3 build_interior.py --self-test
    python3 build_interior.py --pages kdp/pages/approved --out kdp/build/interior.pdf
    python3 build_interior.py --pages kdp/pages/approved --out interior.pdf --title "..." \
        --author "..." --year 2026
    python3 build_interior.py --check kdp/build/interior.pdf

What it produces, in order:

  1. Title page          (typeset, no art)
  2. Blank
  3. Copyright page      (typeset, includes the AI-generation statement)
  4. Blank
  5. Colour test page    (swatch boxes, a real convenience for markers)
  6. Blank
  7..  One design per leaf: the artwork on the front, a blank reverse.

Single-sided printing is deliberate. A blank reverse is the direct answer to the
most common complaint about this category: markers bleeding through and ruining
the design on the other side.

Mirrored margins: the gutter is on the left of a right-hand (odd) page and on
the right of a left-hand (even) page, so no design is swallowed by the binding.

The interior is a no-bleed file. Artwork never reaches the trim edge.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("Pillow is required: pip3 install pillow", file=sys.stderr)
    raise SystemExit(2)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError:  # pragma: no cover
    print("reportlab is required: pip3 install reportlab", file=sys.stderr)
    raise SystemExit(2)

import cover_spec as spec

PT_PER_IN = 72.0
PAGE_W_PT = spec.TRIM_W_IN * PT_PER_IN
PAGE_H_PT = spec.TRIM_H_IN * PT_PER_IN

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

AI_STATEMENT = (
    "The illustrations in this book were created with the assistance of "
    "generative artificial intelligence tools, then reviewed, selected and "
    "prepared for print by the author."
)


def find_pages(folder):
    if not os.path.isdir(folder):
        raise ValueError("not a folder: %s" % folder)
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith(IMAGE_EXTS))
    if not names:
        raise ValueError("no page images found in %s" % folder)
    return [os.path.join(folder, n) for n in names]


def placement(page_index_1based):
    """Return (x_pt, y_pt, w_pt, h_pt) for the artwork on this page.

    Odd pages are right-hand pages, so their gutter is on the left.
    """
    art_w_in, art_h_in = spec.placed_image_size()
    gutter_left = (page_index_1based % 2 == 1)
    if gutter_left:
        x_in = spec.USE_GUTTER_IN
    else:
        x_in = spec.USE_OUTSIDE_IN
    # Centre the art vertically inside the top and bottom margins.
    usable_h = spec.TRIM_H_IN - spec.USE_TOP_IN - spec.USE_BOTTOM_IN
    y_in = spec.USE_BOTTOM_IN + (usable_h - art_h_in) / 2.0
    return (x_in * PT_PER_IN, y_in * PT_PER_IN,
            art_w_in * PT_PER_IN, art_h_in * PT_PER_IN)


def effective_dpi(path):
    with Image.open(path) as im:
        w, h = im.size
    art_w_in, art_h_in = spec.placed_image_size()
    return min(w / art_w_in, h / art_h_in), (w, h)


def _text_page(c, lines, start_y_in=7.0, leading=22, size=12, font="Helvetica",
               centre=True):
    c.setFont(font, size)
    y = start_y_in * PT_PER_IN
    for line in lines:
        if not line:
            y -= leading
            continue
        if centre:
            c.drawCentredString(PAGE_W_PT / 2.0, y, line)
        else:
            c.drawString(spec.USE_GUTTER_IN * PT_PER_IN, y, line)
        y -= leading


def _colour_test_page(c):
    """A grid of empty boxes for testing pens before committing to a design."""
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W_PT / 2.0, (spec.TRIM_H_IN - 1.25) * PT_PER_IN,
                        "Colour Test Page")
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W_PT / 2.0, (spec.TRIM_H_IN - 1.6) * PT_PER_IN,
                        "Try your pencils and markers here before you start a design.")

    cols, rows = 5, 8
    art_w_in, _ = spec.placed_image_size()
    left = spec.USE_GUTTER_IN
    box_w = art_w_in / cols
    box_h = 0.85
    top = spec.TRIM_H_IN - 2.2
    c.setLineWidth(0.75)
    for r in range(rows):
        for col in range(cols):
            x = (left + col * box_w) * PT_PER_IN
            y = (top - (r + 1) * box_h) * PT_PER_IN
            c.rect(x + 3, y + 3, box_w * PT_PER_IN - 6, box_h * PT_PER_IN - 6,
                   stroke=1, fill=0)


def build(pages, out_path, title="Untitled", author="", year=2026,
          front_matter=True, verbose=True):
    """Write the interior PDF. Returns a summary dict."""
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    c = canvas.Canvas(out_path, pagesize=(PAGE_W_PT, PAGE_H_PT))
    c.setTitle(title)
    if author:
        c.setAuthor(author)

    page_no = 0
    low_dpi = []

    def blank():
        nonlocal page_no
        page_no += 1
        c.showPage()

    if front_matter:
        # 1. Title
        page_no += 1
        _text_page(c, [title], start_y_in=6.8, size=26, font="Helvetica-Bold")
        if author:
            _text_page(c, [author], start_y_in=6.0, size=14)
        c.showPage()
        blank()  # 2

        # 3. Copyright
        page_no += 1
        lines = [
            "%s" % title,
            "",
            ("Copyright (c) %d %s" % (year, author)) if author else
            ("Copyright (c) %d" % year),
            "All rights reserved.",
            "",
            "No part of this book may be reproduced or transmitted in any form",
            "without the written permission of the copyright holder.",
            "",
        ]
        _text_page(c, lines, start_y_in=7.0, size=10)
        # The AI statement, wrapped by hand so it does not depend on a wrapper.
        _text_page(c, [
            "A note on how this book was made:",
            "",
            "The illustrations in this book were created with the assistance",
            "of generative artificial intelligence tools, then reviewed,",
            "selected and prepared for print by the author.",
        ], start_y_in=4.6, size=10)
        c.showPage()
        blank()  # 4

        # 5. Colour test
        page_no += 1
        _colour_test_page(c)
        c.showPage()
        blank()  # 6

    for path in pages:
        page_no += 1
        dpi, (pw, ph) = effective_dpi(path)
        if dpi < spec.MIN_DPI:
            low_dpi.append((os.path.basename(path), round(dpi, 1), pw, ph))
        x, y, w, h = placement(page_no)
        c.drawImage(ImageReader(path), x, y, width=w, height=h,
                    preserveAspectRatio=True, anchor="c", mask=None)
        c.showPage()
        blank()

    c.save()

    summary = {
        "out": out_path,
        "designs": len(pages),
        "pages": page_no,
        "page_size_in": [spec.TRIM_W_IN, spec.TRIM_H_IN],
        "low_dpi": low_dpi,
    }

    if verbose:
        print("wrote %s" % out_path)
        print("  designs        %d" % summary["designs"])
        print("  pages          %d" % summary["pages"])
        print("  page size      %.1f x %.1f in" % (spec.TRIM_W_IN, spec.TRIM_H_IN))
        art_w, art_h = spec.placed_image_size()
        print("  placed art     %.3f x %.3f in, gutter mirrored" % (art_w, art_h))
        if low_dpi:
            print("")
            for name, dpi, pw, ph in low_dpi:
                print("  ERROR %s is %dx%d, only %.0f DPI at placed size"
                      % (name, pw, ph, dpi))
        else:
            print("  resolution     every page at or above %d DPI" % spec.MIN_DPI)
    return summary


def check(pdf_path, verbose=True):
    """Re-read a built PDF and report its page count and page size.

    Parses the file directly rather than depending on a PDF library. The files
    this script writes are uncompressed at the object level, so the page tree
    and every MediaBox are readable as plain bytes. If a future file is built
    with object streams this returns None rather than a wrong answer.
    """
    import re

    with open(pdf_path, "rb") as fh:
        raw = fh.read()

    if b"/ObjStm" in raw:
        if verbose:
            print("%s uses compressed object streams; this checker cannot read it"
                  % pdf_path, file=sys.stderr)
        return None

    page_objects = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    counts = [int(m) for m in re.findall(rb"/Count\s+(\d+)", raw)]
    boxes = set()
    for m in re.findall(rb"/MediaBox\s*\[([^\]]*)\]", raw):
        nums = [float(x) for x in m.split()]
        if len(nums) == 4:
            boxes.add((round(nums[2] - nums[0], 2), round(nums[3] - nums[1], 2)))

    pages = max(counts) if counts else page_objects
    result = {"pages": pages, "page_objects": page_objects,
              "page_sizes_pt": sorted(boxes), "errors": []}

    expect = (round(PAGE_W_PT, 2), round(PAGE_H_PT, 2))
    if result["page_sizes_pt"] != [expect]:
        result["errors"].append(
            "expected every page to be %.2f x %.2f pt, found %s"
            % (expect[0], expect[1], result["page_sizes_pt"] or "none"))
    if pages % 2:
        result["errors"].append(
            "page count %d is odd; a book must have an even page count" % pages)
    if counts and page_objects != pages:
        result["errors"].append(
            "the page tree says %d pages but %d page objects were found"
            % (pages, page_objects))

    if verbose:
        print("%s" % pdf_path)
        print("  pages          %d" % result["pages"])
        for w, h in result["page_sizes_pt"]:
            print("  page size      %.2f x %.2f pt  (%.3f x %.3f in)"
                  % (w, h, w / PT_PER_IN, h / PT_PER_IN))
        for e in result["errors"]:
            print("  ERROR %s" % e)
        if not result["errors"]:
            print("  structure      correct trim size, even page count")
    return result


def self_test():
    import tempfile
    failures = []

    with tempfile.TemporaryDirectory() as tmp:
        pages_dir = os.path.join(tmp, "pages")
        os.makedirs(pages_dir)
        art_w, art_h = spec.placed_image_size()
        px_w = int(round(art_w * spec.MIN_DPI))
        px_h = int(round(art_h * spec.MIN_DPI))
        for i in range(3):
            img = Image.new("L", (px_w, px_h), 255)
            img.save(os.path.join(pages_dir, "p%02d.png" % i))

        found = find_pages(pages_dir)
        if len(found) != 3:
            failures.append("find_pages should return 3 images, got %d" % len(found))

        out = os.path.join(tmp, "interior.pdf")
        s = build(found, out, title="Test Book", author="Tester", year=2026,
                  verbose=False)

        # 6 pages of front matter + 3 designs x 2 = 12
        if s["pages"] != 12:
            failures.append("expected 12 pages, got %d" % s["pages"])
        if s["pages"] % 2:
            failures.append("page count must be even")
        if s["low_dpi"]:
            failures.append("correctly sized pages should not be flagged low-DPI: %s"
                            % s["low_dpi"])
        if not os.path.exists(out) or os.path.getsize(out) < 1000:
            failures.append("the PDF was not written, or is suspiciously small")

        # Without front matter: 3 designs x 2 = 6
        out2 = os.path.join(tmp, "nofm.pdf")
        s2 = build(found, out2, front_matter=False, verbose=False)
        if s2["pages"] != 6:
            failures.append("without front matter expected 6 pages, got %d" % s2["pages"])

        # A small image is caught.
        small_dir = os.path.join(tmp, "small")
        os.makedirs(small_dir)
        Image.new("L", (600, 800), 255).save(os.path.join(small_dir, "s.png"))
        s3 = build(find_pages(small_dir), os.path.join(tmp, "small.pdf"), verbose=False)
        if not s3["low_dpi"]:
            failures.append("a 600x800 page should be reported as low-DPI")

        # Gutter mirroring: odd pages sit further right than even pages.
        x_odd = placement(7)[0]
        x_even = placement(8)[0]
        if not x_odd > x_even:
            failures.append("odd (right-hand) pages should have the larger left "
                            "offset, got odd=%.1f even=%.1f" % (x_odd, x_even))
        # The art must fit inside the trim on both sides.
        for idx in (7, 8):
            x, y, w, h = placement(idx)
            if x < 0 or x + w > PAGE_W_PT + 1e-6:
                failures.append("page %d art runs off the page horizontally" % idx)
            if y < 0 or y + h > PAGE_H_PT + 1e-6:
                failures.append("page %d art runs off the page vertically" % idx)
            # And must clear the smaller of the two horizontal margins.
            if x < spec.USE_OUTSIDE_IN * PT_PER_IN - 1e-6:
                failures.append("page %d art breaks the outside margin" % idx)

        # An empty folder is refused rather than silently building nothing.
        empty = os.path.join(tmp, "empty")
        os.makedirs(empty)
        try:
            find_pages(empty)
            failures.append("an empty folder should raise ValueError")
        except ValueError:
            pass

        # The check pass must agree with the build.
        chk = check(out, verbose=False)
        if chk is None:
            failures.append("check() could not read a PDF this script just wrote")
        else:
            if chk["pages"] != s["pages"]:
                failures.append("check() saw %d pages, build reported %d"
                                % (chk["pages"], s["pages"]))
            expect = (round(PAGE_W_PT, 2), round(PAGE_H_PT, 2))
            if chk["page_sizes_pt"] != [expect]:
                failures.append("check() page size %s, expected %s"
                                % (chk["page_sizes_pt"], [expect]))
            if chk["errors"]:
                failures.append("check() reported errors on a good file: %s"
                                % "; ".join(chk["errors"]))

        # check() must notice a wrong trim size rather than pass it through.
        from reportlab.pdfgen import canvas as _canvas
        bad = os.path.join(tmp, "bad_trim.pdf")
        bc = _canvas.Canvas(bad, pagesize=(612, 1008))  # 8.5 x 14 in
        bc.showPage()
        bc.showPage()
        bc.save()
        bad_chk = check(bad, verbose=False)
        if not bad_chk or not any("MediaBox" in e or "expected every page" in e
                                  for e in bad_chk["errors"]):
            failures.append("check() should reject a PDF with the wrong trim size")

        # And an odd page count.
        odd = os.path.join(tmp, "odd.pdf")
        oc = _canvas.Canvas(odd, pagesize=(PAGE_W_PT, PAGE_H_PT))
        oc.showPage()
        oc.save()
        odd_chk = check(odd, verbose=False)
        if not odd_chk or not any("odd" in e for e in odd_chk["errors"]):
            failures.append("check() should reject an odd page count")

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("build_interior.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the interior PDF.")
    ap.add_argument("--pages", help="folder of approved page images")
    ap.add_argument("--out", default="kdp/build/interior.pdf")
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--author", default="")
    ap.add_argument("--year", type=int, default=2026)
    ap.add_argument("--no-front-matter", action="store_true")
    ap.add_argument("--check", help="inspect an existing PDF instead of building")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.check:
        return 0 if check(args.check) is not None else 2
    if not args.pages:
        ap.error("give --pages, --check or --self-test")
        return 2

    try:
        found = find_pages(args.pages)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    s = build(found, args.out, title=args.title, author=args.author,
              year=args.year, front_matter=not args.no_front_matter)
    return 1 if s["low_dpi"] else 0


if __name__ == "__main__":
    sys.exit(main())
