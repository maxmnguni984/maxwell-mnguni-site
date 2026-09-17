#!/usr/bin/env python3
"""Generate the storefront from data/store.json and data/products.json.

Standard library only.

Design rule that matters more than any other here: the generator NEVER invents a
business detail. Where store.json says REQUIRED_FROM_OWNER or null, the page
renders a visible "not yet supplied" callout instead of plausible-sounding text.
A shipping policy that confidently states a delivery window nobody has verified
is worse than no policy at all, because customers rely on it and chargebacks
follow.

While any required field is missing, every page carries a DRAFT banner and
`--check-publishable` exits non-zero.

Usage:
    python3 build_store.py                       # build to store/dist
    python3 build_store.py --out /tmp/preview
    python3 build_store.py --check-publishable   # exit 1 if not ready to publish
    python3 build_store.py --self-test
"""

import argparse
import html
import json
import os
import shutil
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.dirname(HERE)
DATA_DIR = os.path.join(STORE_DIR, "data")
ASSETS_DIR = os.path.join(STORE_DIR, "assets")
DEFAULT_OUT = os.path.join(STORE_DIR, "dist")

PLACEHOLDER = "REQUIRED_FROM_OWNER"
TODAY = date.today().isoformat()


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def missing(value):
    return value is None or value == PLACEHOLDER


def tbd(label):
    """A visible gap, never filled with invention."""
    return ('<div class="tbd"><strong>Not yet supplied:</strong> %s. '
            'This must come from the owner before the store can be published.</div>'
            % e(label))


# ------------------------------------------------------------------ chrome

def nav_links(base):
    return [
        (base + "index.html", "Home"),
        (base + "product.html", "Shop"),
        (base + "pages/about.html", "About"),
        (base + "pages/contact.html", "Contact"),
    ]


def head(title, description, base, brand, draft):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="robots" content="noindex, nofollow">
<link rel="stylesheet" href="%sassets/css/store.css">
</head>
<body>
%s""" % (e(title), e(description), base, draft_banner(draft))


def draft_banner(draft):
    if not draft:
        return ""
    return ('<div class="draft-banner"><strong>DRAFT BUILD.</strong> '
            'This store is not live and cannot take orders. Product data, '
            'business details or both are still placeholders. Nothing on this '
            'page is an offer for sale.</div>\n')


def header(base, brand):
    links = "".join('<a href="%s">%s</a>' % (u, e(t)) for u, t in nav_links(base))
    name = brand.get("name")
    display = e(name) if not missing(name) else "Store name pending"
    return """<header class="site-header">
  <div class="wrap header-inner">
    <a class="logo" href="%sindex.html">%s</a>
    <button class="nav-toggle" data-nav-toggle aria-expanded="false" aria-label="Menu">&#9776;</button>
    <nav class="nav" data-nav>
      %s
      <a class="cart-link" href="%scart.html">Cart <span class="cart-count" data-cart-count hidden>0</span></a>
    </nav>
  </div>
</header>
<main>
""" % (base, display, links, base)


def footer(base, store, draft):
    brand = store["brand"]
    legal = store["legal"]
    contact = store["contact"]
    name = brand.get("name")
    display = e(name) if not missing(name) else "This store"

    entity = legal.get("entity_name")
    entity_line = (e(entity) if not missing(entity)
                   else "Legal entity not yet supplied")
    email = contact.get("support_email")
    email_line = ('<a href="mailto:%s">%s</a>' % (e(email), e(email))
                  if not missing(email) else "Support email not yet supplied")

    return """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h4>%s</h4>
        <p>%s</p>
      </div>
      <div>
        <h4>Shop</h4>
        <ul>
          <li><a href="%sproduct.html">Product</a></li>
          <li><a href="%scart.html">Cart</a></li>
          <li><a href="%spages/contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Information</h4>
        <ul>
          <li><a href="%spages/shipping.html">Shipping</a></li>
          <li><a href="%spages/returns.html">Returns and refunds</a></li>
          <li><a href="%spages/privacy.html">Privacy</a></li>
          <li><a href="%spages/terms.html">Terms of service</a></li>
        </ul>
      </div>
    </div>
    <div class="colophon">
      <p>%s &middot; %s</p>
      <p>%s</p>
    </div>
  </div>
</footer>
<script src="%sassets/js/store.js"></script>
</body>
</html>
""" % (display, email_line, base, base, base, base, base, base, base,
       entity_line,
       "Build date %s" % TODAY,
       ("This is a draft build. It is not a live shop and cannot accept orders."
        if draft else e("&copy; %s %s" % (brand.get("founded_year", ""), name or ""))),
       base)


def store_config_script(store, base):
    ship = store["shipping"]
    cfg = {
        "base": base,
        "currencySymbol": store["currency"]["symbol"],
        "shipping": {"flatRate": ship.get("flat_rate")},
        "checkout": {"provider": store["checkout"].get("provider"),
                     "testMode": store["checkout"].get("test_mode", True)},
    }
    return "<script>window.STORE=%s;</script>\n" % json.dumps(cfg)


# ------------------------------------------------------------------ pages

def build_home(store, products, base, draft):
    brand = store["brand"]
    name = brand.get("name")
    tagline = brand.get("tagline")

    hero_title = e(name) if not missing(name) else "Store name pending"
    hero_sub = (e(tagline) if not missing(tagline)
                else "Brand positioning is written once a product is selected.")

    p = products[0] if products else None
    if p and not p.get("placeholder"):
        cta = ('<a class="btn" href="%sproduct.html">Shop %s &mdash; %s%.2f</a>'
               % (base, e(p["title"]), store["currency"]["symbol"], p["price"]))
        feature = "".join(
            '<div class="card"><h3>%s</h3><p>%s</p></div>' % (e(b.get("title", "")), e(b.get("body", "")))
            for b in p.get("benefits", [])[:3])
    else:
        cta = '<a class="btn btn-secondary" href="%sproduct.html">View product page</a>' % base
        feature = ('<div class="card"><h3>Product not yet selected</h3>'
                   '<p>The ranked shortlist is prepared. The owner chooses the '
                   'product, and this page fills from that choice. Nothing here '
                   'is a claim about a real item.</p></div>')

    body = """<section class="hero">
  <div class="wrap">
    <h1>%s</h1>
    <p>%s</p>
    %s
  </div>
</section>
<section class="section">
  <div class="wrap">
    <h2>Why this product</h2>
    <p class="lede">Every claim on this page has to be something we can stand behind. Until a product is selected and a sample inspected, this section stays honest about being empty.</p>
    <div class="grid grid-3">%s</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <h2>What you should know before ordering</h2>
    <div class="grid grid-3">
      <div class="card"><h3>Shipping</h3><p>%s</p></div>
      <div class="card"><h3>Returns</h3><p>%s</p></div>
      <div class="card"><h3>Questions</h3><p>%s</p></div>
    </div>
  </div>
</section>
""" % (hero_title, hero_sub, cta, feature,
       shipping_summary(store), returns_summary(store), contact_summary(store))

    return (head(hero_title, hero_sub, base, brand, draft)
            + store_config_script(store, base) + header(base, brand)
            + body + footer(base, store, draft))


def shipping_summary(store):
    s = store["shipping"]
    if missing(s.get("transit_days_max")) or missing(s.get("carrier")):
        return ("Delivery times are not published yet because no supplier quote "
                "has been verified. We will not promise a window we cannot meet.")
    return ("Ships to the United States, %s to %s days in transit after "
            "processing, tracked via %s."
            % (s["transit_days_min"], s["transit_days_max"], e(s["carrier"])))


def returns_summary(store):
    r = store["returns"]
    who = r.get("who_pays_return_shipping")
    if missing(who):
        return ("A %d day return window. Who pays return shipping is not settled "
                "yet, so it is not stated here." % r["window_days"])
    return ("%d days to return an unused item in its original packaging. "
            "Return shipping paid by %s. Refunds go back to the original payment "
            "method within %d working days of arrival."
            % (r["window_days"], e(who), r["refund_processing_days"]))


def contact_summary(store):
    c = store["contact"]
    if missing(c.get("support_email")):
        return "A support address has not been set up yet."
    return ("Email %s. We aim to reply within %d hours, %s."
            % (e(c["support_email"]), c["response_target_hours"], e(c["support_hours"])))


def build_product(store, products, base, draft):
    brand = store["brand"]
    sym = store["currency"]["symbol"]
    p = products[0] if products else None

    if p is None:
        inner = '<div class="wrap"><div class="empty"><p>No product configured.</p></div></div>'
        return (head("Product", "", base, brand, draft) + store_config_script(store, base)
                + header(base, brand) + inner + footer(base, store, draft))

    is_placeholder = bool(p.get("placeholder"))
    available = bool(p.get("available")) and not is_placeholder

    images = p.get("images", [])
    if images:
        main = '<img src="%s%s" alt="%s">' % (base, e(images[0]["src"]), e(images[0].get("alt", "")))
        thumbs = "".join(
            '<button type="button" data-gallery-thumb data-src="%s%s" data-alt="%s" '
            'aria-current="%s"><img src="%s%s" alt=""></button>'
            % (base, e(im["src"]), e(im.get("alt", "")),
               "true" if i == 0 else "false", base, e(im["src"]))
            for i, im in enumerate(images))
        thumbs = '<div class="thumbs">%s</div>' % thumbs
    else:
        main = ('<div class="gallery-placeholder">No product photography yet.<br>'
                'Images will be our own or properly licensed. We do not use a '
                'supplier’s catalogue photos without permission.</div>')
        thumbs = ""

    benefits = "".join("<li>%s</li>" % e(b.get("title", "") if isinstance(b, dict) else b)
                       for b in p.get("benefits", []))
    benefits = '<ul class="benefits">%s</ul>' % benefits if benefits else ""

    variants = p.get("variants", [])
    if variants:
        opts = "".join(
            '<button type="button" data-variant="%s" data-variant-label="%s" '
            'data-variant-price="%s" aria-pressed="false"%s>%s</button>'
            % (e(v["id"]), e(v["label"]), v.get("price", p["price"]),
               "" if v.get("available", True) else " disabled", e(v["label"]))
            for v in variants)
        variant_block = ('<div class="variant-group"><label>%s</label>'
                         '<div class="variant-options">%s</div></div>'
                         % (e(p.get("variant_label", "Options")), opts))
    else:
        variant_block = ""

    specs = p.get("specs", {})
    spec_rows = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(k), e(v))
                        for k, v in specs.items())
    spec_block = ('<h2>Specifications</h2><table class="spec-table">%s</table>' % spec_rows
                  if spec_rows else "")

    faqs = p.get("faqs", [])
    faq_block = ""
    if faqs:
        faq_block = "<h2>Questions</h2>" + "".join(
            '<details class="faq"><summary>%s</summary><p>%s</p></details>'
            % (e(f["q"]), e(f["a"])) for f in faqs)

    compare = ('<span class="compare">%s%.2f</span>' % (sym, p["compare_at_price"])
               if p.get("compare_at_price") else "")

    if is_placeholder:
        notice = ('<div class="notice"><strong>No product is selected yet.</strong> '
                  'This page is the working template. The price shown is a modelling '
                  'figure from the economics work, not an offer. It fills with real '
                  'content once the owner picks from the ranked shortlist and a '
                  'supplier quote confirms the landed cost.</div>')
    elif not available:
        notice = ('<div class="notice">This product is not available to order yet.</div>')
    else:
        notice = ""

    body = """<div class="wrap">
  <div class="product">
    <div>
      <div class="gallery-main" data-gallery-main>%s</div>
      %s
    </div>
    <div>
      <h1>%s</h1>
      <p class="subtitle">%s</p>
      <div class="price-row">
        <span class="price" data-price-display>%s%.2f</span>%s
      </div>
      %s
      %s
      <form data-product-form data-handle="%s" data-title="%s" data-price="%s"
            data-available="%s" data-url="%sproduct.html">
        %s
        <div class="qty-row">
          <div class="qty">
            <button type="button" data-qty-dec aria-label="Decrease quantity">&minus;</button>
            <input type="number" value="1" min="1" max="99" data-qty-input aria-label="Quantity">
            <button type="button" data-qty-inc aria-label="Increase quantity">+</button>
          </div>
        </div>
        <button class="btn btn-block" type="submit" data-add-to-cart%s>%s</button>
        <p role="status" data-add-feedback></p>
      </form>
      <div class="ship-note"><strong>Shipping.</strong> %s</div>
      <div class="ship-note"><strong>Returns.</strong> %s</div>
    </div>
  </div>
  <div class="prose">%s%s</div>
</div>
""" % (main, thumbs, e(p["title"]), e(p.get("subtitle", "")), sym, p["price"], compare,
       notice, benefits, e(p["handle"]), e(p["title"]), p["price"],
       "true" if available else "false", base, variant_block,
       "" if available else " disabled",
       "Add to cart" if available else "Not available yet",
       shipping_summary(store), returns_summary(store), spec_block, faq_block)

    return (head(p["title"], p.get("summary", ""), base, brand, draft)
            + store_config_script(store, base) + header(base, brand)
            + body + footer(base, store, draft))


def build_cart(store, base, draft):
    brand = store["brand"]
    body = ('<div class="wrap"><div class="prose"><h1>Your cart</h1></div>'
            '<div data-cart-root></div></div>')
    return (head("Cart", "Your cart", base, brand, draft)
            + store_config_script(store, base) + header(base, brand)
            + body + footer(base, store, draft))


def prose_page(store, base, draft, title, blocks):
    brand = store["brand"]
    body = ('<div class="wrap"><div class="prose"><h1>%s</h1>'
            '<p class="updated">Last updated %s</p>%s</div></div>'
            % (e(title), TODAY, "".join(blocks)))
    return (head(title, title, base, brand, draft)
            + store_config_script(store, base) + header(base, brand)
            + body + footer(base, store, draft))


def build_shipping(store, base, draft):
    s = store["shipping"]
    b = []
    b.append("<h2>Where we ship</h2>")
    b.append("<p>We ship to %s only.</p>" % e(", ".join(s.get("ships_to", []))))

    b.append("<h2>Processing time</h2>")
    if missing(s.get("processing_days_max")):
        b.append(tbd("how long orders take to leave the supplier"))
    else:
        b.append("<p>Orders are processed in %s to %s working days before they ship.</p>"
                 % (s["processing_days_min"], s["processing_days_max"]))

    b.append("<h2>Delivery time</h2>")
    if missing(s.get("transit_days_max")):
        b.append(tbd("verified transit times from the supplier"))
        b.append("<p>We will not publish a delivery estimate until a supplier "
                 "quote confirms it. An unverified promise here is the fastest "
                 "route to refunds and chargebacks.</p>")
    else:
        b.append("<p>After processing, delivery takes %s to %s days.</p>"
                 % (s["transit_days_min"], s["transit_days_max"]))

    b.append("<h2>Cost</h2>")
    if s.get("flat_rate") == 0:
        b.append("<p>Shipping is free on every order.</p>")
    elif s.get("flat_rate"):
        b.append("<p>Shipping is a flat %s%.2f per order.</p>"
                 % (store["currency"]["symbol"], s["flat_rate"]))
    else:
        b.append(tbd("the shipping rate charged to customers"))

    b.append("<h2>Tracking</h2>")
    if s.get("tracking_provided") is None:
        b.append(tbd("whether the supplier provides tracking"))
    elif s["tracking_provided"]:
        b.append("<p>Every order ships with tracking. You receive the number by "
                 "email as soon as the parcel is collected.</p>")
    else:
        b.append("<p>This service does not include tracking.</p>")

    b.append("<h2>Import duties and taxes</h2>")
    if missing(s.get("duties_note")):
        b.append(tbd("who pays import duty, which depends on the supplier's terms"))
        b.append("<p>United States duty-free de minimis treatment ended for all "
                 "countries on 29 August 2025, so imported parcels are dutiable. "
                 "Whether that cost falls to us or to you depends on the supplier "
                 "terms, which are not settled yet.</p>")
    else:
        b.append("<p>%s</p>" % e(s["duties_note"]))

    b.append("<h2>Lost or delayed parcels</h2>")
    b.append("<p>If tracking has not moved for 10 working days, contact us and we "
             "will open an enquiry with the carrier. If a parcel is confirmed lost "
             "we replace it or refund it in full, your choice.</p>")
    return prose_page(store, base, draft, "Shipping", b)


def build_returns(store, base, draft):
    r = store["returns"]
    b = []
    b.append("<h2>Return window</h2>")
    b.append("<p>You have %d days from delivery to request a return.</p>" % r["window_days"])
    b.append("<h2>Condition</h2>")
    b.append("<p>%s</p>" % e(r["condition"]))

    b.append("<h2>Who pays return shipping</h2>")
    if missing(r.get("who_pays_return_shipping")):
        b.append(tbd("who pays return postage"))
    else:
        b.append("<p>Return shipping is paid by %s.</p>" % e(r["who_pays_return_shipping"]))

    b.append("<h2>Where to send it</h2>")
    if missing(r.get("return_address")):
        b.append(tbd("the return address"))
        b.append("<p>Do not send anything back before contacting us. Returns sent "
                 "to an unconfirmed address cannot be refunded.</p>")
    else:
        b.append("<p>%s</p>" % e(r["return_address"]))

    b.append("<h2>Refunds</h2>")
    b.append("<p>%s Refunds are issued within %d working days of the item arriving. "
             "Your bank may take a few days more to show it.</p>"
             % (e(r["refund_method"]), r["refund_processing_days"]))
    if r.get("restocking_fee_pct"):
        b.append("<p>A %d%% restocking fee applies.</p>" % r["restocking_fee_pct"])
    else:
        b.append("<p>There is no restocking fee.</p>")

    b.append("<h2>Damaged or wrong items</h2>")
    b.append("<p>If something arrives damaged or is not what you ordered, email us "
             "a photo within 14 days. We replace or refund it and we pay the "
             "return postage. You are not asked to post a damaged item back "
             "before we act.</p>")
    return prose_page(store, base, draft, "Returns and refunds", b)


def build_privacy(store, base, draft):
    p = store["privacy"]
    c = store["contact"]
    legal = store["legal"]
    b = []
    b.append("<h2>Who we are</h2>")
    if missing(legal.get("entity_name")):
        b.append(tbd("the registered business name and address of the data controller"))
    else:
        b.append("<p>%s, %s.</p>" % (e(legal["entity_name"]), e(legal.get("registered_address"))))

    b.append("<h2>What we collect</h2>")
    b.append("<p>When you order we collect your %s. We collect this because we "
             "cannot deliver an order without it.</p>"
             % e(", ".join(p.get("data_collected", []))))

    b.append("<h2>Payment details</h2>")
    if missing(p.get("payment_processor")):
        b.append(tbd("the payment processor"))
        b.append("<p>No payment provider is connected to this store, so no card "
                 "details are collected anywhere on this site.</p>")
    else:
        b.append("<p>Card details are handled entirely by %s. They never reach our "
                 "servers and we cannot see them.</p>" % e(p["payment_processor"]))

    b.append("<h2>Analytics</h2>")
    if not p.get("analytics_provider"):
        b.append("<p>This site runs no analytics and sets no tracking cookies.</p>")
    else:
        b.append("<p>We use %s to understand how the site is used.</p>"
                 % e(p["analytics_provider"]))

    b.append("<h2>Sharing</h2>")
    b.append("<p>We share your address with the supplier who ships your order, "
             "because otherwise it cannot arrive. We do not sell your data to "
             "anyone, for any purpose.</p>")

    b.append("<h2>How long we keep it</h2>")
    b.append("<p>Order records are kept for %d years to meet tax and accounting "
             "obligations, then deleted.</p>" % p.get("data_retention_years", 7))

    b.append("<h2>Your rights</h2>")
    b.append("<p>You can ask for a copy of your data, ask us to correct it, or ask "
             "us to delete it. Email the address on our contact page and we will "
             "respond within 30 days.</p>")
    return prose_page(store, base, draft, "Privacy", b)


def build_terms(store, base, draft):
    legal = store["legal"]
    b = []
    b.append("<h2>Who you are buying from</h2>")
    if missing(legal.get("entity_name")):
        b.append(tbd("the legal entity behind this store"))
    else:
        b.append("<p>%s, registered in %s.</p>"
                 % (e(legal["entity_name"]), e(legal.get("country"))))
    b.append("<h2>Prices</h2>")
    b.append("<p>Prices are in %s and include any applicable sales tax where we "
             "are required to charge it. We may change prices, but never after you "
             "have placed an order.</p>" % e(store["currency"]["code"]))
    b.append("<h2>Orders</h2>")
    b.append("<p>An order is an offer to buy. We accept it when we send a "
             "confirmation. If we cannot fulfil an order we refund it in full and "
             "tell you why.</p>")
    b.append("<h2>Product descriptions</h2>")
    b.append("<p>We describe products as accurately as we can. We do not make "
             "health, medical or performance claims about anything we sell, and "
             "photographs show the actual item.</p>")
    b.append("<h2>Your statutory rights</h2>")
    b.append("<p>Nothing in these terms reduces the rights you have under "
             "consumer law.</p>")
    return prose_page(store, base, draft, "Terms of service", b)


def build_about(store, base, draft):
    brand = store["brand"]
    b = []
    if missing(brand.get("name")):
        b.append(tbd("the brand name, story and positioning"))
        b.append("<p>Brand positioning is written after a product is selected, so "
                 "that it says something true about a real product rather than "
                 "generic copy that would fit anything.</p>")
    else:
        b.append("<p>%s</p>" % e(brand.get("tagline", "")))
    b.append("<h2>How we work</h2>")
    b.append("<p>We sell a small number of products and we test each one before "
             "listing it. If we have not held a product in our hands, it is not on "
             "this site.</p>")
    b.append("<h2>What we will not do</h2>")
    b.append("<p>We do not publish reviews we did not receive, we do not stage "
             "demonstrations that misrepresent what a product does, and we do not "
             "use other sellers' photography.</p>")
    return prose_page(store, base, draft, "About", b)


def build_contact(store, base, draft):
    c = store["contact"]
    b = []
    if missing(c.get("support_email")):
        b.append(tbd("a customer support email address"))
    else:
        b.append('<p>Email <a href="mailto:%s">%s</a>.</p>'
                 % (e(c["support_email"]), e(c["support_email"])))
        b.append("<p>We aim to reply within %d hours. Support hours are %s.</p>"
                 % (c["response_target_hours"], e(c["support_hours"])))
    b.append("<h2>Before you write</h2>")
    b.append("<p>If your question is about where an order is, please include your "
             "order number. It is the fastest way for us to help.</p>")
    return prose_page(store, base, draft, "Contact", b)


# ------------------------------------------------------------------ driver

def load():
    with open(os.path.join(DATA_DIR, "store.json"), encoding="utf-8") as fh:
        store = json.load(fh)
    with open(os.path.join(DATA_DIR, "products.json"), encoding="utf-8") as fh:
        prod = json.load(fh)
    return store, prod


def find_gaps(store, prod):
    """Every reason this build is not publishable."""
    gaps = []

    def walk(obj, path):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.startswith("_"):
                    continue
                walk(v, path + [k])
        elif obj == PLACEHOLDER:
            gaps.append(".".join(path))

    walk(store, [])
    if prod.get("placeholder"):
        gaps.append("products: no product selected yet")
    for p in prod.get("products", []):
        if p.get("placeholder"):
            continue
        if not p.get("images"):
            gaps.append("products.%s: no product images" % p.get("handle"))
        if not p.get("available"):
            gaps.append("products.%s: marked unavailable" % p.get("handle"))
    if not store["checkout"].get("provider"):
        gaps.append("checkout.provider: no payment provider connected")
    return gaps


def build(out_dir=DEFAULT_OUT, verbose=True):
    store, prod = load()
    products = prod.get("products", [])
    gaps = find_gaps(store, prod)
    draft = bool(gaps)

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(os.path.join(out_dir, "pages"))
    shutil.copytree(ASSETS_DIR, os.path.join(out_dir, "assets"))

    pages = {
        "index.html": build_home(store, products, "", draft),
        "product.html": build_product(store, products, "", draft),
        "cart.html": build_cart(store, "", draft),
        "pages/shipping.html": build_shipping(store, "../", draft),
        "pages/returns.html": build_returns(store, "../", draft),
        "pages/privacy.html": build_privacy(store, "../", draft),
        "pages/terms.html": build_terms(store, "../", draft),
        "pages/about.html": build_about(store, "../", draft),
        "pages/contact.html": build_contact(store, "../", draft),
    }
    for rel, content in pages.items():
        with open(os.path.join(out_dir, rel), "w", encoding="utf-8") as fh:
            fh.write(content)

    if verbose:
        print("built %d pages to %s" % (len(pages), out_dir))
        print("status: %s" % ("DRAFT" if draft else "PUBLISHABLE"))
        if gaps:
            print("")
            print("%d blocker(s) before this can be published:" % len(gaps))
            for g in gaps:
                print("  - %s" % g)
    return {"out": out_dir, "pages": sorted(pages), "draft": draft, "gaps": gaps}


def self_test():
    import tempfile
    failures = []

    store, prod = load()

    # Gap detection must find the seeded placeholders.
    gaps = find_gaps(store, prod)
    if not gaps:
        failures.append("the shipped data files are placeholders, so gaps must be found")
    if not any("brand.name" in g for g in gaps):
        failures.append("brand.name placeholder should be reported as a gap")
    if not any("no product selected" in g for g in gaps):
        failures.append("the placeholder product should be reported as a gap")

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "dist")
        r = build(out, verbose=False)

        if not r["draft"]:
            failures.append("a build with gaps must be marked DRAFT")

        for rel in r["pages"]:
            path = os.path.join(out, rel)
            if not os.path.exists(path):
                failures.append("missing output page %s" % rel)
                continue
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            if "DRAFT BUILD" not in content:
                failures.append("%s is missing the draft banner" % rel)
            if 'name="viewport"' not in content:
                failures.append("%s has no viewport meta tag, so it will not be mobile-ready" % rel)
            if PLACEHOLDER in content:
                failures.append("%s leaks the literal placeholder token into the page" % rel)
            if "<html" not in content or "</html>" not in content:
                failures.append("%s is not a complete HTML document" % rel)

        # Assets must be copied.
        for a in ("assets/css/store.css", "assets/js/store.js"):
            if not os.path.exists(os.path.join(out, a)):
                failures.append("asset not copied: %s" % a)

        # The shipping page must not invent a delivery window.
        with open(os.path.join(out, "pages/shipping.html"), encoding="utf-8") as fh:
            ship = fh.read()
        if "Not yet supplied" not in ship:
            failures.append("shipping page should flag the unverified delivery window")

        # Checkout must be visibly disconnected, not silently broken.
        with open(os.path.join(out, "cart.html"), encoding="utf-8") as fh:
            cart = fh.read()
        if "data-cart-root" not in cart:
            failures.append("cart page is missing its mount point")

        # A completed store must come out publishable.
        full = json.loads(json.dumps(store))
        def fill(obj):
            for k, v in obj.items():
                if isinstance(v, dict):
                    fill(v)
                elif v == PLACEHOLDER:
                    obj[k] = "filled"
        fill(full)
        full["shipping"].update({"processing_days_min": 1, "processing_days_max": 2,
                                 "transit_days_min": 5, "transit_days_max": 9,
                                 "tracking_provided": True})
        full["checkout"]["provider"] = "test-provider"
        full_prod = {"placeholder": False, "products": [{
            "handle": "x", "title": "X", "subtitle": "s", "price": 39.99,
            "available": True, "summary": "s", "benefits": [], "specs": {},
            "variants": [], "images": [{"src": "assets/img/x.jpg", "alt": "x"}],
            "faqs": []}]}
        if find_gaps(full, full_prod):
            failures.append("a fully specified store should report no gaps, got %s"
                            % find_gaps(full, full_prod))

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("build_store.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the storefront.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check-publishable", action="store_true", dest="check")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    r = build(args.out)
    if args.check:
        return 1 if r["draft"] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
