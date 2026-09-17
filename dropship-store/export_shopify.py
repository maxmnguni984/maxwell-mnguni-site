#!/usr/bin/env python3
"""Export data/product.json to a Shopify-importable product CSV.

Usage:
    python3 export_shopify.py                 # writes dist/shopify-products.csv
    python3 export_shopify.py -o out.csv
    python3 export_shopify.py --validate      # check only, write nothing

Format notes, verified 2026-09-17 against Shopify's help documentation
(https://help.shopify.com/en/manual/products/import-export/using-csv):

  - `Title` is the only universally required column. `Handle` becomes required
    as soon as a product has variants, which ours does.
  - **Column headers are case-sensitive.** `Handle`, not `handle`.
  - The file must be UTF-8 and under 15 MB.
  - A product with N variants occupies N rows. The first row carries the
    product-level fields; subsequent rows repeat only the Handle and the
    variant fields, leaving product-level cells empty.

The header set below is the documented standard set. Shopify's own sample
template is the authoritative list and could not be downloaded from this
environment, so **validate one import into a draft product before trusting a
bulk run**. That check is in the launch checklist rather than assumed here.

Nothing in this script reads or writes credentials.
"""

import argparse
import csv
import json
import os
import re
import sys

COLUMNS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags",
    "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value", "Variant SKU", "Variant Grams",
    "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
    "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price",
    "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src",
    "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description",
    "Status",
]

HANDLE_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def repo_root():
    return os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = os.path.join(repo_root(), "data", name)
    if not os.path.exists(path):
        sys.exit("missing data file: data/{}".format(name))
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def handle_from(text):
    """Shopify handles: lowercase letters, digits and hyphens only."""
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "product"


def body_html(product):
    """Build the product description. Only uses supplied copy; invents nothing."""
    parts = []
    if product.get("description"):
        parts.append("<p>{}</p>".format(product["description"]))

    benefits = [b for b in product.get("benefits", []) if b.get("title")]
    if benefits:
        parts.append("<ul>" + "".join(
            "<li><strong>{}</strong> {}</li>".format(b.get("title", ""), b.get("body", ""))
            for b in benefits) + "</ul>")

    specs = {k: v for k, v in (product.get("specs") or {}).items() if v is not None}
    if specs:
        parts.append("<h3>Specifications</h3><ul>" + "".join(
            "<li><strong>{}:</strong> {}</li>".format(k, v) for k, v in specs.items()) + "</ul>")

    if product.get("limitations"):
        parts.append("<h3>What this does not do</h3><p>{}</p>".format(product["limitations"]))

    return "".join(parts)


def rows_for(product, brand):
    handle = product.get("handle") or handle_from(product.get("name"))
    variants = product.get("variants") or []
    if not variants:
        sys.exit("product.json has no variants; nothing to export")

    option_name = product.get("option_name") or "Size"
    rows = []
    for index, variant in enumerate(variants):
        row = {column: "" for column in COLUMNS}
        row["Handle"] = handle
        row["Option1 Name"] = option_name
        row["Option1 Value"] = variant.get("name") or "Default Title"
        row["Variant SKU"] = variant.get("sku") or ""
        row["Variant Price"] = ("" if variant.get("price") is None
                                else "{:.2f}".format(float(variant["price"])))
        if variant.get("compare_at_price") is not None:
            row["Variant Compare At Price"] = "{:.2f}".format(float(variant["compare_at_price"]))
        row["Variant Grams"] = variant.get("grams") or ""
        # Dropshipped stock is not tracked in Shopify and must stay sellable.
        row["Variant Inventory Tracker"] = ""
        row["Variant Inventory Policy"] = "continue"
        row["Variant Fulfillment Service"] = "manual"
        row["Variant Requires Shipping"] = "TRUE"
        row["Variant Taxable"] = "TRUE"

        if index == 0:
            row["Title"] = product.get("name") or ""
            row["Body (HTML)"] = body_html(product)
            row["Vendor"] = brand.get("name") or ""
            row["Product Category"] = product.get("shopify_category") or ""
            row["Type"] = product.get("type") or ""
            row["Tags"] = ", ".join(product.get("tags") or [])
            row["Published"] = "FALSE"      # draft until the owner approves
            row["Gift Card"] = "FALSE"
            row["SEO Title"] = product.get("seo_title") or ""
            row["SEO Description"] = product.get("seo_description") or ""
            row["Status"] = "draft"         # never import straight to active
        rows.append(row)
    return handle, rows


def validate(product, brand, handle, rows):
    """Return a list of problems that would break or embarrass an import."""
    problems = []

    if not product.get("name"):
        problems.append("Title is empty; Shopify requires it")
    if not HANDLE_OK.match(handle):
        problems.append("Handle '{}' is not lowercase-alphanumeric-with-hyphens".format(handle))

    seen = set()
    for row in rows:
        sku = row["Variant SKU"]
        if not sku:
            problems.append("a variant has no SKU")
        elif sku in seen:
            problems.append("duplicate variant SKU: {}".format(sku))
        else:
            seen.add(sku)
        if not row["Variant Price"]:
            problems.append("variant {} has no price".format(sku or "?"))

    # Claims that would need evidence or a live account behind them.
    if any(row["Variant Compare At Price"] for row in rows):
        problems.append(
            "Compare At Price is set: this displays as a discount and must reflect a real "
            "former price, not an invented one")
    if not product.get("images"):
        problems.append("no images: Image Src is empty, so products import without photography")

    unresolved = [k for k, v in (product.get("specs") or {}).items() if v is None]
    if unresolved:
        problems.append("specs still unsupplied: {}".format(", ".join(unresolved)))
    if not brand.get("name"):
        problems.append("brand.name is empty, so Vendor will be blank")

    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export a Shopify product CSV.")
    parser.add_argument("-o", "--out",
                        default=os.path.join(repo_root(), "dist", "shopify-products.csv"))
    parser.add_argument("--validate", action="store_true", help="check only, write nothing")
    args = parser.parse_args(argv)

    product, brand = load("product.json"), load("brand.json")
    handle, rows = rows_for(product, brand)
    problems = validate(product, brand, handle, rows)

    if args.validate:
        if problems:
            print("{} problem(s) before this CSV is safe to import:".format(len(problems)))
            for problem in problems:
                print("  - {}".format(problem))
            return 1
        print("CSV validates: {} variant row(s) for handle '{}'.".format(len(rows), handle))
        return 0

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as handle_out:
        writer = csv.DictWriter(handle_out, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print("wrote {} ({} variant rows, handle '{}')".format(args.out, len(rows), handle))
    print("Status=draft and Published=FALSE, so an import cannot put this on sale by accident.")
    if problems:
        print("\n{} problem(s) to resolve before importing:".format(len(problems)))
        for problem in problems:
            print("  - {}".format(problem))
    return 0


if __name__ == "__main__":
    sys.exit(main())
