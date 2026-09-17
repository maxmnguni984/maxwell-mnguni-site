#!/usr/bin/env python3
"""Emit a Shopify import pack from the same data that builds the local store.

Standard library only.

WHY: the owner wants Shopify, but Shopify needs a paid plan and an account, and
spend authorization is zero. So the store is built locally and this script
produces everything Shopify needs, in Shopify's own formats. When a plan is
approved, the work imports rather than being redone.

Produces, in store/dist-shopify/:
  products.csv        Shopify's product import format, one row per variant
  pages/*.html        Page body HTML for Online Store > Pages
  policies/*.txt      Policy text for Settings > Policies
  IMPORT.md           Exactly what to do with each file, in order

Usage:
    python3 shopify_export.py
    python3 shopify_export.py --out /tmp/pack
    python3 shopify_export.py --self-test
"""

import argparse
import csv
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.dirname(HERE)
DATA_DIR = os.path.join(STORE_DIR, "data")
DEFAULT_OUT = os.path.join(STORE_DIR, "dist-shopify")
PLACEHOLDER = "REQUIRED_FROM_OWNER"

sys.path.insert(0, HERE)
import build_store as bs  # noqa: E402  (shares the page builders and gap logic)

# Shopify's product CSV header, in the order its importer expects.
COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type",
    "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value",
    "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode",
    "Image Src", "Image Position", "Image Alt Text", "Gift Card",
    "SEO Title", "SEO Description", "Status",
]


def body_html(product):
    """The product description, as Shopify stores it: a fragment, not a page."""
    parts = []
    if product.get("summary"):
        parts.append("<p>%s</p>" % bs.e(product["summary"]))
    benefits = product.get("benefits", [])
    if benefits:
        parts.append("<ul>")
        for b in benefits:
            if isinstance(b, dict):
                title = bs.e(b.get("title", ""))
                body = bs.e(b.get("body", ""))
                parts.append("<li><strong>%s</strong> %s</li>" % (title, body) if body
                             else "<li>%s</li>" % title)
            else:
                parts.append("<li>%s</li>" % bs.e(b))
        parts.append("</ul>")
    specs = product.get("specs", {})
    if specs:
        parts.append("<h3>Specifications</h3><ul>")
        for k, v in specs.items():
            parts.append("<li><strong>%s:</strong> %s</li>" % (bs.e(k), bs.e(v)))
        parts.append("</ul>")
    faqs = product.get("faqs", [])
    if faqs:
        parts.append("<h3>Questions</h3>")
        for f in faqs:
            parts.append("<p><strong>%s</strong><br>%s</p>" % (bs.e(f["q"]), bs.e(f["a"])))
    return "".join(parts)


def seo_description(product):
    text = re.sub(r"<[^>]+>", " ", product.get("summary", "") or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:320]


def product_rows(product, store, published):
    """One row per variant; images continue on extra rows, as Shopify expects."""
    rows = []
    handle = product["handle"]
    variants = product.get("variants") or [{
        "id": "default", "label": "Default Title",
        "price": product["price"], "available": product.get("available", False),
        "sku": product.get("sku", ""),
    }]
    option_name = product.get("variant_label", "Title") if product.get("variants") else "Title"
    images = product.get("images", [])

    for i, v in enumerate(variants):
        first = (i == 0)
        row = {c: "" for c in COLUMNS}
        row["Handle"] = handle
        if first:
            row["Title"] = product["title"]
            row["Body (HTML)"] = body_html(product)
            row["Vendor"] = (store["brand"].get("name")
                             if store["brand"].get("name") != PLACEHOLDER else "")
            row["Type"] = product.get("type", "")
            row["Tags"] = ", ".join(product.get("tags", []))
            row["SEO Title"] = product.get("seo_title", product["title"])[:70]
            row["SEO Description"] = seo_description(product)
            row["Gift Card"] = "FALSE"
        row["Published"] = "TRUE" if published else "FALSE"
        row["Status"] = "active" if published else "draft"
        row["Option1 Name"] = option_name
        row["Option1 Value"] = v.get("label", "Default Title")
        row["Variant SKU"] = v.get("sku", product.get("sku", ""))
        row["Variant Grams"] = str(v.get("grams", product.get("grams", "")) or "")
        row["Variant Inventory Tracker"] = ""
        row["Variant Inventory Qty"] = "0"
        # "continue" means the storefront keeps selling when stock hits zero,
        # which is what a dropshipper wants: there is no stock to count.
        row["Variant Inventory Policy"] = "continue"
        row["Variant Fulfillment Service"] = "manual"
        row["Variant Price"] = "%.2f" % float(v.get("price", product["price"]))
        cap = v.get("compare_at_price", product.get("compare_at_price"))
        row["Variant Compare At Price"] = "%.2f" % float(cap) if cap else ""
        row["Variant Requires Shipping"] = "TRUE"
        row["Variant Taxable"] = "TRUE"
        if first and images:
            row["Image Src"] = images[0].get("shopify_src", images[0].get("src", ""))
            row["Image Position"] = "1"
            row["Image Alt Text"] = images[0].get("alt", "")
        rows.append(row)

    for n, im in enumerate(images[1:], start=2):
        row = {c: "" for c in COLUMNS}
        row["Handle"] = handle
        row["Image Src"] = im.get("shopify_src", im.get("src", ""))
        row["Image Position"] = str(n)
        row["Image Alt Text"] = im.get("alt", "")
        rows.append(row)

    return rows


def strip_chrome(page_html):
    """Shopify pages take a body fragment, not a whole document."""
    m = re.search(r'<div class="prose">(.*?)</div>\s*</div>', page_html, re.S)
    if m:
        body = m.group(1)
    else:
        m2 = re.search(r"<main>(.*?)</main>", page_html, re.S)
        body = m2.group(1) if m2 else page_html
    # The page title becomes Shopify's own title field, so drop the h1.
    body = re.sub(r"<h1\b[^>]*>.*?</h1>", "", body, flags=re.S)
    return body.strip()


def export(out_dir=DEFAULT_OUT, verbose=True):
    store, prod = bs.load()
    products = prod.get("products", [])
    gaps = bs.find_gaps(store, prod)
    draft = bool(gaps)
    published = not draft

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(os.path.join(out_dir, "pages"))
    os.makedirs(os.path.join(out_dir, "policies"))

    # products.csv
    rows = []
    for p in products:
        if p.get("placeholder"):
            continue
        rows.extend(product_rows(p, store, published))

    csv_path = os.path.join(out_dir, "products.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # Pages and policies, reusing the same builders the local store uses, so the
    # two can never drift apart.
    page_builders = {
        "about": bs.build_about,
        "contact": bs.build_contact,
    }
    policy_builders = {
        "shipping-policy": bs.build_shipping,
        "refund-policy": bs.build_returns,
        "privacy-policy": bs.build_privacy,
        "terms-of-service": bs.build_terms,
    }
    for name, fn in page_builders.items():
        with open(os.path.join(out_dir, "pages", name + ".html"), "w", encoding="utf-8") as fh:
            fh.write(strip_chrome(fn(store, "", draft)))
    for name, fn in policy_builders.items():
        with open(os.path.join(out_dir, "policies", name + ".html"), "w", encoding="utf-8") as fh:
            fh.write(strip_chrome(fn(store, "", draft)))

    with open(os.path.join(out_dir, "IMPORT.md"), "w", encoding="utf-8") as fh:
        fh.write(import_instructions(store, rows, gaps))

    if verbose:
        print("wrote Shopify pack to %s" % out_dir)
        print("  products.csv   %d row(s) across %d product(s)"
              % (len(rows), len([p for p in products if not p.get("placeholder")])))
        print("  pages          %d" % len(page_builders))
        print("  policies       %d" % len(policy_builders))
        print("  status         %s" % ("DRAFT, products import unpublished" if draft
                                       else "ready to publish"))
        if gaps:
            print("")
            print("%d blocker(s) still open; see IMPORT.md" % len(gaps))
    return {"out": out_dir, "rows": len(rows), "draft": draft, "gaps": gaps}


def import_instructions(store, rows, gaps):
    blockers = "\n".join("- %s" % g for g in gaps) or "- none"
    status = ("Products import as **draft** and are not visible to shoppers, "
              "because blockers remain." if gaps else
              "Products import as **active**.")
    return """# Shopify import pack

Generated from `store/data/store.json` and `store/data/products.json`, the same
data that builds the local storefront. Regenerate with:

```
python3 store/tools/shopify_export.py
```

%s

## Open blockers

%s

Nothing here should be imported into a live shop until those are closed. A
shipping policy with an unverified delivery window causes refunds and
chargebacks; that is the reason the local build refuses to call itself
publishable.

## Order of work

1. **Create the store.** Requires a paid plan. This needs the owner's approval;
   it is proposal 1 in the run's `approvals.md`.

2. **Products.** Shopify admin, Products, Import, upload `products.csv`.
   Preview the mapping before confirming. Every variant row uses inventory
   policy `continue`, which is what a dropshipper wants: there is no stock to
   count and the storefront should not block a sale.

3. **Images.** The CSV's image column holds local paths. Shopify needs public
   URLs, so either upload the images in the product editor after import, or put
   them in Files first and paste the resulting URLs into the CSV before
   importing.

4. **Pages.** Online Store, Pages, Add page. Paste each file from `pages/` into
   the HTML view. The filename is the handle; give it a matching title.

5. **Policies.** Settings, Policies. Paste each file from `policies/` into the
   matching field. Shopify links these automatically at checkout, which is why
   they belong here rather than as ordinary pages.

6. **Shipping.** Settings, Shipping and delivery. The rates must match what the
   shipping policy states. If they disagree, the policy is the promise the
   customer relies on and the one that will be enforced against you.

7. **Payments.** Settings, Payments. Until this is connected, no order can
   complete. Use Shopify's test mode ("Bogus Gateway") to place an end-to-end
   test order before going live.

8. **Checks before launch.** Place a test order through checkout in test mode.
   Confirm the confirmation email, the tax line, the shipping rate, and that
   the policy links at checkout resolve.

## What this pack deliberately does not contain

- No theme file. The local build is a working reference for layout and copy,
  not a Shopify theme. Rebuilding it as Liquid is a separate decision.
- No analytics or pixel IDs. None exist yet, and a placeholder ID silently
  collects nothing while appearing to work.
- No credentials of any kind. No API key, token or password appears in this
  pack or in the repository.
""" % (status, blockers)


def self_test():
    import tempfile
    failures = []

    store, prod = bs.load()

    # A realistic product exercises variants, images and FAQs.
    p = {
        "handle": "test-widget", "title": "Test Widget", "subtitle": "sub",
        "price": 39.99, "compare_at_price": 49.99, "sku": "TW-1",
        "available": True, "grams": 640,
        "summary": "A summary with <b>markup</b> & an ampersand.",
        "benefits": [{"title": "Fast", "body": "Very"}, "Plain benefit"],
        "specs": {"Material": "Steel"},
        "variant_label": "Colour",
        "variants": [
            {"id": "black", "label": "Black", "price": 39.99, "available": True, "sku": "TW-1-B"},
            {"id": "white", "label": "White", "price": 42.99, "available": True, "sku": "TW-1-W"},
        ],
        "images": [{"src": "assets/img/a.jpg", "alt": "front"},
                   {"src": "assets/img/b.jpg", "alt": "back"}],
        "faqs": [{"q": "Does it fit?", "a": "Yes."}],
    }

    rows = product_rows(p, store, published=True)

    # 2 variants + 1 extra image row
    if len(rows) != 3:
        failures.append("expected 3 rows (2 variants + 1 extra image), got %d" % len(rows))

    if rows[0]["Title"] != "Test Widget":
        failures.append("first row must carry the title")
    if rows[1]["Title"] != "":
        failures.append("only the first variant row carries product-level fields")
    if rows[0]["Option1 Name"] != "Colour":
        failures.append("option name should come from variant_label, got %r" % rows[0]["Option1 Name"])
    if rows[0]["Option1 Value"] != "Black" or rows[1]["Option1 Value"] != "White":
        failures.append("variant labels are wrong")
    if rows[1]["Variant Price"] != "42.99":
        failures.append("per-variant price override lost, got %r" % rows[1]["Variant Price"])
    if rows[0]["Variant Compare At Price"] != "49.99":
        failures.append("compare-at price lost")
    if rows[0]["Variant SKU"] != "TW-1-B":
        failures.append("variant SKU lost")
    if rows[0]["Variant Inventory Policy"] != "continue":
        failures.append("dropshipping needs inventory policy 'continue'")
    if rows[2]["Handle"] != "test-widget" or rows[2]["Image Position"] != "2":
        failures.append("the extra image row is malformed")
    if rows[2]["Title"] != "":
        failures.append("an image-only row must not repeat product fields")

    # Body HTML must escape, not leak, user markup.
    if "<b>markup</b>" in rows[0]["Body (HTML)"]:
        failures.append("summary markup should be escaped, not passed through")
    if "&amp;" not in rows[0]["Body (HTML)"]:
        failures.append("ampersand should be escaped in the body")
    if "Plain benefit" not in rows[0]["Body (HTML)"]:
        failures.append("string benefits should appear in the body")
    if "Steel" not in rows[0]["Body (HTML)"]:
        failures.append("specs should appear in the body")
    if "Does it fit?" not in rows[0]["Body (HTML)"]:
        failures.append("FAQs should appear in the body")

    # Draft products must import unpublished.
    draft_rows = product_rows(p, store, published=False)
    if draft_rows[0]["Published"] != "FALSE" or draft_rows[0]["Status"] != "draft":
        failures.append("an unpublishable build must produce draft, unpublished products")

    # A product with no variants still produces a valid single row.
    simple = dict(p)
    simple.pop("variants")
    simple.pop("images")
    srows = product_rows(simple, store, published=True)
    if len(srows) != 1:
        failures.append("a variantless product should make exactly 1 row, got %d" % len(srows))
    if srows[0]["Option1 Value"] != "Default Title":
        failures.append("Shopify expects 'Default Title' for a variantless product")

    # The CSV must round-trip through a real parser with the exact header.
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS)
    w.writeheader()
    for row in rows:
        w.writerow(row)
    buf.seek(0)
    parsed = list(csv.DictReader(buf))
    if len(parsed) != len(rows):
        failures.append("CSV round trip lost rows")
    if parsed and list(parsed[0].keys()) != COLUMNS:
        failures.append("CSV header does not match Shopify's expected columns")
    if parsed and parsed[0]["Body (HTML)"] != rows[0]["Body (HTML)"]:
        failures.append("CSV round trip mangled the body HTML")

    # End-to-end export against the shipped placeholder data.
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "pack")
        r = export(out, verbose=False)
        if not r["draft"]:
            failures.append("placeholder data must export as draft")
        for rel in ("products.csv", "IMPORT.md",
                    "pages/about.html", "pages/contact.html",
                    "policies/shipping-policy.html", "policies/refund-policy.html",
                    "policies/privacy-policy.html", "policies/terms-of-service.html"):
            if not os.path.exists(os.path.join(out, rel)):
                failures.append("export is missing %s" % rel)
        with open(os.path.join(out, "policies/shipping-policy.html"), encoding="utf-8") as fh:
            ship = fh.read()
        if "<html" in ship.lower():
            failures.append("policy files must be body fragments, not whole documents")
        if "<h1" in ship.lower():
            failures.append("policy fragments should not carry an h1; Shopify supplies the title")
        if PLACEHOLDER in ship:
            failures.append("a placeholder token leaked into the policy text")
        with open(os.path.join(out, "products.csv"), encoding="utf-8") as fh:
            head = fh.readline().strip()
        if head != ",".join(COLUMNS):
            failures.append("products.csv header is not Shopify's column order")

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("shopify_export.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit a Shopify import pack.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    export(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
