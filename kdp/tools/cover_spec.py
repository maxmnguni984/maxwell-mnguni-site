#!/usr/bin/env python3
"""Cover, spine and printing-cost arithmetic for the KDP paperback.

Standard library only.

Usage:
    python3 cover_spec.py --pages 86
    python3 cover_spec.py --pages 86 --price 11.99 --json
    python3 cover_spec.py --self-test

Every constant below is marked with how much it can be trusted. The values
flagged UNVERIFIED come from secondary sources because kdp.amazon.com is
unreachable from the build environment. Re-check them against the official
pages before any file is final or any price is set:

  Printing cost:  https://kdp.amazon.com/en_US/help/topic/G201834340
  Trim and bleed: https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
  Cover template: KDP's own cover template generator for the final page count

Nothing here is a promise about what Amazon will charge. It is arithmetic on
inputs that must be confirmed.
"""

import argparse
import json
import sys

# --------------------------------------------------------------- constants

TRIM_W_IN = 8.5           # DECIDED with the owner
TRIM_H_IN = 11.0          # DECIDED with the owner
COVER_BLEED_IN = 0.125    # UNVERIFIED: secondary source
WHITE_PAPER_SPINE_PER_PAGE = 0.002252   # UNVERIFIED: secondary source
CREAM_PAPER_SPINE_PER_PAGE = 0.0025     # UNVERIFIED: secondary source

# Interior margins. The minimums are UNVERIFIED (secondary sources); the values
# we actually use are deliberately larger, for colouring comfort.
MIN_OUTSIDE_IN = 0.25
MIN_GUTTER_UNDER_150_IN = 0.375
USE_GUTTER_IN = 0.75
USE_OUTSIDE_IN = 0.625
USE_TOP_IN = 0.75
USE_BOTTOM_IN = 0.75

# US large-trim black-ink printing. Both UNVERIFIED: secondary source.
FIXED_COST_LARGE_TRIM_USD = 0.85
PER_PAGE_BW_USD = 0.012
LARGE_TRIM_THRESHOLD_SQIN = 6.12 * 9.0   # KDP's large-trim boundary, UNVERIFIED

ROYALTY_RATE_STANDARD = 0.60   # UNVERIFIED: secondary source
KDP_MIN_PAGES = 24             # UNVERIFIED: secondary source
KDP_MAX_PAGES_BW = 828         # UNVERIFIED: secondary source

MIN_DPI = 300

UNVERIFIED_NOTE = (
    "Printing cost, royalty rate, margin minimums, bleed and the spine "
    "multiplier are taken from secondary sources because kdp.amazon.com is "
    "blocked from this environment. Confirm each against KDP's own pages "
    "before setting a price or uploading a final file."
)


def placed_image_size():
    """The usable area for artwork, in inches, given the chosen margins."""
    w = TRIM_W_IN - USE_GUTTER_IN - USE_OUTSIDE_IN
    h = TRIM_H_IN - USE_TOP_IN - USE_BOTTOM_IN
    # Keep the placement at exactly 3:4 so a 3:4 generation is never cropped.
    if w / h > 0.75:
        w = h * 0.75
    else:
        h = w / 0.75
    return round(w, 4), round(h, 4)


def spine_width(pages, paper="white"):
    per = WHITE_PAPER_SPINE_PER_PAGE if paper == "white" else CREAM_PAPER_SPINE_PER_PAGE
    return round(pages * per, 4)


def cover_size(pages, paper="white"):
    spine = spine_width(pages, paper)
    width = TRIM_W_IN * 2 + spine + COVER_BLEED_IN * 2
    height = TRIM_H_IN + COVER_BLEED_IN * 2
    return round(width, 4), round(height, 4), spine


def printing_cost(pages, trim_w=TRIM_W_IN, trim_h=TRIM_H_IN):
    """US, black ink, standard paperback. Large trim only, which 8.5x11 is."""
    large = (trim_w * trim_h) > LARGE_TRIM_THRESHOLD_SQIN
    if not large:
        raise ValueError("this helper only covers large-trim books; %sx%s is not"
                         % (trim_w, trim_h))
    return round(FIXED_COST_LARGE_TRIM_USD + pages * PER_PAGE_BW_USD, 4)


def royalty(list_price, pages):
    cost = printing_cost(pages)
    gross = list_price - cost
    return round(ROYALTY_RATE_STANDARD * gross, 4), cost


def min_list_price(pages):
    """The lowest price at which the 60% royalty is not negative."""
    return round(printing_cost(pages) / ROYALTY_RATE_STANDARD, 2)


def page_budget(designs, front_matter=4, single_sided=True):
    """Interior page count for a given number of designs.

    Single-sided means a blank reverse behind every design, which is what stops
    marker bleed ruining the page behind. KDP counts both sides of a leaf.
    """
    body = designs * (2 if single_sided else 1)
    total = front_matter + body
    if total % 2:
        total += 1   # a book must have an even page count
    return total


def report(pages, price=None, paper="white", designs=None):
    cover_w, cover_h, spine = cover_size(pages, paper)
    img_w, img_h = placed_image_size()
    cost = printing_cost(pages)
    out = {
        "pages": pages,
        "trim_in": [TRIM_W_IN, TRIM_H_IN],
        "paper": paper,
        "interior": {
            "margins_in": {"gutter": USE_GUTTER_IN, "outside": USE_OUTSIDE_IN,
                           "top": USE_TOP_IN, "bottom": USE_BOTTOM_IN},
            "minimums_in": {"outside": MIN_OUTSIDE_IN,
                            "gutter_under_150_pages": MIN_GUTTER_UNDER_150_IN},
            "placed_image_in": [img_w, img_h],
            "placed_image_px_at_300dpi": [int(round(img_w * MIN_DPI)),
                                          int(round(img_h * MIN_DPI))],
            "bleed": "none",
        },
        "cover": {
            "spine_in": spine,
            "full_wrap_in": [cover_w, cover_h],
            "full_wrap_px_at_300dpi": [int(round(cover_w * MIN_DPI)),
                                       int(round(cover_h * MIN_DPI))],
            "bleed_in": COVER_BLEED_IN,
        },
        "economics": {
            "printing_cost_usd": cost,
            "min_list_price_usd": min_list_price(pages),
            "royalty_rate": ROYALTY_RATE_STANDARD,
        },
        "status": "UNVERIFIED",
        "note": UNVERIFIED_NOTE,
    }
    if designs is not None:
        out["designs"] = designs
    if price is not None:
        r, _ = royalty(price, pages)
        out["economics"]["list_price_usd"] = price
        out["economics"]["royalty_usd"] = r
    if pages < KDP_MIN_PAGES:
        out["warnings"] = ["page count %d is below the %d-page minimum"
                           % (pages, KDP_MIN_PAGES)]
    if pages > KDP_MAX_PAGES_BW:
        out.setdefault("warnings", []).append(
            "page count %d is above the %d-page maximum" % (pages, KDP_MAX_PAGES_BW))
    return out


def render(r):
    lines = []
    lines.append("Book: %.1f x %.1f in, %d pages, %s paper"
                 % (r["trim_in"][0], r["trim_in"][1], r["pages"], r["paper"]))
    if "designs" in r:
        lines.append("Designs: %d, single-sided with a blank reverse" % r["designs"])
    lines.append("")
    i = r["interior"]
    lines.append("Interior")
    lines.append("  margins        gutter %.3f, outside %.3f, top %.3f, bottom %.3f in"
                 % (i["margins_in"]["gutter"], i["margins_in"]["outside"],
                    i["margins_in"]["top"], i["margins_in"]["bottom"]))
    lines.append("  minimums       outside %.3f, gutter %.3f in (UNVERIFIED)"
                 % (i["minimums_in"]["outside"], i["minimums_in"]["gutter_under_150_pages"]))
    lines.append("  placed art     %.3f x %.3f in  =  %d x %d px at 300 DPI"
                 % (i["placed_image_in"][0], i["placed_image_in"][1],
                    i["placed_image_px_at_300dpi"][0], i["placed_image_px_at_300dpi"][1]))
    lines.append("  bleed          none")
    lines.append("")
    c = r["cover"]
    lines.append("Cover (full wrap)")
    lines.append("  spine          %.4f in" % c["spine_in"])
    lines.append("  size           %.3f x %.3f in  =  %d x %d px at 300 DPI"
                 % (c["full_wrap_in"][0], c["full_wrap_in"][1],
                    c["full_wrap_px_at_300dpi"][0], c["full_wrap_px_at_300dpi"][1]))
    lines.append("  bleed          %.3f in on every side" % c["bleed_in"])
    lines.append("")
    e = r["economics"]
    lines.append("Economics (UNVERIFIED inputs)")
    lines.append("  printing cost  $%.2f" % e["printing_cost_usd"])
    lines.append("  min list price $%.2f  (below this the 60%% royalty goes negative)"
                 % e["min_list_price_usd"])
    if "list_price_usd" in e:
        lines.append("  at $%.2f       royalty $%.2f per copy"
                     % (e["list_price_usd"], e["royalty_usd"]))
    else:
        lines.append("")
        lines.append("  price  printing  royalty")
        for p in (8.99, 9.99, 10.99, 11.99, 12.99):
            ro, co = royalty(p, r["pages"])
            lines.append("  $%-5.2f $%-8.2f $%.2f" % (p, co, ro))
    for w in r.get("warnings", []):
        lines.append("")
        lines.append("WARNING: %s" % w)
    lines.append("")
    lines.append(UNVERIFIED_NOTE)
    return "\n".join(lines)


def self_test():
    failures = []

    # Placed art is exactly 3:4 and fits inside the margins.
    w, h = placed_image_size()
    if abs(w / h - 0.75) > 1e-6:
        failures.append("placed art should be exactly 3:4, got %.6f" % (w / h))
    if w > TRIM_W_IN - USE_GUTTER_IN - USE_OUTSIDE_IN + 1e-9:
        failures.append("placed art is wider than the usable width")
    if h > TRIM_H_IN - USE_TOP_IN - USE_BOTTOM_IN + 1e-9:
        failures.append("placed art is taller than the usable height")
    if w * MIN_DPI > 2560 or w * MIN_DPI < 2000:
        failures.append("placed width of %.3f in implies %d px, which looks wrong"
                        % (w, int(w * MIN_DPI)))

    # Margins clear the stated minimums.
    if USE_OUTSIDE_IN < MIN_OUTSIDE_IN or USE_GUTTER_IN < MIN_GUTTER_UNDER_150_IN:
        failures.append("chosen margins fall below the stated minimums")

    # Spine and cover, hand-checked for 86 pages on white paper:
    #   spine = 86 * 0.002252 = 0.193672
    #   width = 8.5*2 + 0.193672 + 0.25 = 17.443672
    #   height = 11 + 0.25 = 11.25
    cw, ch, sp = cover_size(86, "white")
    for name, got, want in (("spine", sp, 0.1937), ("cover width", cw, 17.4437),
                            ("cover height", ch, 11.25)):
        if abs(got - want) > 0.001:
            failures.append("%s: got %.4f, expected %.4f" % (name, got, want))

    # Printing cost, hand-checked: 0.85 + 86*0.012 = 0.85 + 1.032 = 1.882
    cost = printing_cost(86)
    if abs(cost - 1.882) > 1e-6:
        failures.append("printing cost: got %.4f, expected 1.882" % cost)

    # Royalty, hand-checked: 0.6 * (9.99 - 1.882) = 0.6 * 8.108 = 4.8648
    r, _ = royalty(9.99, 86)
    if abs(r - 4.8648) > 1e-6:
        failures.append("royalty at $9.99: got %.4f, expected 4.8648" % r)

    # Minimum viable price: 1.882 / 0.6 = 3.1367 -> 3.14
    if abs(min_list_price(86) - 3.14) > 0.005:
        failures.append("min list price: got %.2f, expected 3.14" % min_list_price(86))

    # A price below the printing cost gives a negative royalty, not a crash.
    neg, _ = royalty(1.00, 86)
    if neg >= 0:
        failures.append("a $1.00 price should give a negative royalty")

    # Page budget: 40 designs single-sided plus 4 front matter = 84, already even.
    if page_budget(40) != 84:
        failures.append("page_budget(40) should be 84, got %d" % page_budget(40))
    # 41 designs -> 4 + 82 = 86, even.
    if page_budget(41) != 86:
        failures.append("page_budget(41) should be 86, got %d" % page_budget(41))
    # An odd total is rounded up to even: 3 front matter + 40 = 43 -> 44.
    if page_budget(20, front_matter=3) % 2 != 0:
        failures.append("page counts must always come out even")

    # Thin books are flagged, not silently accepted.
    if "warnings" not in report(10):
        failures.append("a 10-page book should raise a minimum-page-count warning")

    # A small trim is refused rather than costed with the wrong constants.
    try:
        printing_cost(86, 5.0, 8.0)
        failures.append("a small trim should raise ValueError")
    except ValueError:
        pass

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("cover_spec.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Cover, spine and cost arithmetic.")
    ap.add_argument("--pages", type=int, help="interior page count")
    ap.add_argument("--designs", type=int, help="number of designs, to derive the page count")
    ap.add_argument("--price", type=float, help="list price in USD")
    ap.add_argument("--paper", choices=["white", "cream"], default="white")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    pages = args.pages
    if pages is None and args.designs is not None:
        pages = page_budget(args.designs)
    if pages is None:
        ap.error("give --pages, --designs or --self-test")
        return 2

    r = report(pages, args.price, args.paper, args.designs)
    print(json.dumps(r, indent=2) if args.json else render(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
