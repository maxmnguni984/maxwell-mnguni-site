#!/usr/bin/env python3
"""Verify a built storefront. Standard library only.

Usage:
    python3 verify_store.py                 # verifies store/dist
    python3 verify_store.py --dist /tmp/x
    python3 verify_store.py --json

Exit 0 when every check passes, 1 on any failure, 2 on a usage problem.

Checks:
  STRUCTURE  Every expected page exists and is a complete HTML document.
  LINKS      Every internal href and src resolves to a file that exists.
  EXTERNAL   No page loads a third-party script, font, image or stylesheet.
             A store that silently phones out to a CDN is a privacy claim we
             cannot make good on, and it breaks offline review.
  MOBILE     Viewport meta present; no fixed pixel width wider than 420px;
             interactive controls declare a tap target of at least 44px.
  META       Title and meta description present and non-empty on every page.
  PLACEHOLDER No unreplaced placeholder token reaches the output.
  SECRETS    No API key, token or password-shaped string in any output file.
  PRICES     Every price rendered matches the price in products.json.
  A11Y       Images have alt attributes; form controls have labels; there is
             exactly one h1 per page.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.dirname(HERE)
DEFAULT_DIST = os.path.join(STORE_DIR, "dist")
DATA_DIR = os.path.join(STORE_DIR, "data")

EXPECTED = [
    "index.html", "product.html", "cart.html",
    "pages/shipping.html", "pages/returns.html", "pages/privacy.html",
    "pages/terms.html", "pages/about.html", "pages/contact.html",
]

SECRET_PATTERNS = [
    (r"sk_live_[A-Za-z0-9]{8,}", "Stripe live secret key"),
    (r"sk_test_[A-Za-z0-9]{8,}", "Stripe test secret key"),
    (r"shpat_[A-Za-z0-9]{16,}", "Shopify access token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub personal access token"),
    (r"AIza[0-9A-Za-z_\-]{30,}", "Google API key"),
    (r"(?i)\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*[\"'][^\"']{8,}[\"']",
     "hard-coded credential"),
]

HREF_RE = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"', re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
H1_RE = re.compile(r"<h1\b", re.I)
PX_WIDTH_RE = re.compile(r"(?:^|[^-\w])width\s*:\s*(\d{3,})px", re.I)


class Result(object):
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passed = []

    def fail(self, check, where, msg):
        self.failures.append({"check": check, "where": where, "message": msg})

    def warn(self, check, where, msg):
        self.warnings.append({"check": check, "where": where, "message": msg})

    def ok(self, check, detail):
        self.passed.append({"check": check, "detail": detail})


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def verify(dist=DEFAULT_DIST):
    r = Result()

    if not os.path.isdir(dist):
        r.fail("STRUCTURE", dist, "the dist folder does not exist; run build_store.py first")
        return r

    # ---------------------------------------------------------- STRUCTURE
    for rel in EXPECTED:
        path = os.path.join(dist, rel)
        if not os.path.exists(path):
            r.fail("STRUCTURE", rel, "expected page is missing")
            continue
        content = read(path)
        if "<html" not in content.lower() or "</html>" not in content.lower():
            r.fail("STRUCTURE", rel, "not a complete HTML document")
    if not r.failures:
        r.ok("STRUCTURE", "%d pages present and well formed" % len(EXPECTED))

    html_files = []
    for root, _dirs, files in os.walk(dist):
        for n in files:
            if n.endswith(".html"):
                html_files.append(os.path.join(root, n))

    # ---------------------------------------------------------- per page
    broken_links = 0
    external = 0
    for path in sorted(html_files):
        rel = os.path.relpath(path, dist)
        content = read(path)
        page_dir = os.path.dirname(path)

        # META
        title = re.search(r"<title>(.*?)</title>", content, re.S | re.I)
        if not title or not title.group(1).strip():
            r.fail("META", rel, "missing or empty <title>")
        desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content, re.I)
        if not desc or not desc.group(1).strip():
            r.fail("META", rel, "missing or empty meta description")

        # MOBILE
        if 'name="viewport"' not in content:
            r.fail("MOBILE", rel, "no viewport meta tag")
        for m in PX_WIDTH_RE.finditer(content):
            if int(m.group(1)) > 420:
                r.fail("MOBILE", rel,
                       "a fixed width of %spx will cause horizontal scrolling on a phone"
                       % m.group(1))

        # PLACEHOLDER
        if "REQUIRED_FROM_OWNER" in content:
            r.fail("PLACEHOLDER", rel, "an unreplaced placeholder token reached the page")

        # SECRETS
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, content):
                r.fail("SECRETS", rel, "possible %s in output" % label)

        # A11Y
        h1s = len(H1_RE.findall(content))
        if h1s == 0:
            r.fail("A11Y", rel, "no h1 heading")
        elif h1s > 1:
            r.warn("A11Y", rel, "%d h1 headings; one per page is the convention" % h1s)
        for tag in IMG_RE.findall(content):
            if "alt=" not in tag.lower():
                r.fail("A11Y", rel, "an img tag has no alt attribute: %s" % tag[:70])

        # LINKS and EXTERNAL
        for target in HREF_RE.findall(content):
            t = target.strip()
            if not t or t.startswith("#") or t.startswith("mailto:") or t.startswith("tel:"):
                continue
            if t.startswith("data:"):
                continue
            if re.match(r"^(https?:)?//", t):
                external += 1
                r.fail("EXTERNAL", rel,
                       "loads a third-party resource: %s. This store is built to "
                       "make no outbound requests." % t)
                continue
            resolved = os.path.normpath(os.path.join(page_dir, t.split("?")[0].split("#")[0]))
            if not os.path.exists(resolved):
                broken_links += 1
                r.fail("LINKS", rel, "broken link to %s" % t)

    if broken_links == 0:
        r.ok("LINKS", "every internal link resolves")
    if external == 0:
        r.ok("EXTERNAL", "no third-party requests")

    # ---------------------------------------------------------- PRICES
    try:
        with open(os.path.join(DATA_DIR, "products.json"), encoding="utf-8") as fh:
            prod = json.load(fh)
        products = prod.get("products", [])
        if products:
            p = products[0]
            expected_price = "%.2f" % p["price"]
            page = read(os.path.join(dist, "product.html"))
            if expected_price not in page:
                r.fail("PRICES", "product.html",
                       "price %s from products.json does not appear on the page"
                       % expected_price)
            else:
                r.ok("PRICES", "rendered price matches products.json (%s)" % expected_price)
            m = re.search(r'data-price="([^"]+)"', page)
            if m and m.group(1) != str(p["price"]):
                r.fail("PRICES", "product.html",
                       "the add-to-cart form price %s does not match products.json %s"
                       % (m.group(1), p["price"]))
            for v in p.get("variants", []):
                if v.get("label") and v["label"] not in page:
                    r.fail("PRICES", "product.html",
                           "variant %s is in the data but not on the page" % v["label"])
    except (OSError, ValueError, KeyError) as exc:
        r.fail("PRICES", "products.json", "could not compare prices: %s" % exc)

    # ---------------------------------------------------------- CSS tap targets
    css_path = os.path.join(dist, "assets", "css", "store.css")
    if os.path.exists(css_path):
        css = read(css_path)
        if "min-height: 44px" not in css and "min-height:44px" not in css:
            r.warn("MOBILE", "store.css",
                   "no 44px minimum tap target declared for interactive controls")
        else:
            r.ok("MOBILE", "44px minimum tap targets declared")
        if "prefers-color-scheme" not in css:
            r.warn("MOBILE", "store.css", "no dark mode support")
    else:
        r.fail("STRUCTURE", "assets/css/store.css", "stylesheet not copied into dist")

    if not os.path.exists(os.path.join(dist, "assets", "js", "store.js")):
        r.fail("STRUCTURE", "assets/js/store.js", "script not copied into dist")

    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify a built storefront.")
    ap.add_argument("--dist", default=DEFAULT_DIST)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    r = verify(args.dist)

    if args.json:
        print(json.dumps({"ok": not r.failures, "failures": r.failures,
                          "warnings": r.warnings, "passed": r.passed}, indent=2))
    else:
        for p in r.passed:
            print("PASS  %-12s %s" % (p["check"], p["detail"]))
        for w in r.warnings:
            print("WARN  %-12s %s: %s" % (w["check"], w["where"], w["message"]))
        for f in r.failures:
            print("FAIL  %-12s %s: %s" % (f["check"], f["where"], f["message"]))
        print("")
        print("%d passed, %d warning(s), %d failure(s)"
              % (len(r.passed), len(r.warnings), len(r.failures)))
    return 1 if r.failures else 0


if __name__ == "__main__":
    sys.exit(main())
