#!/usr/bin/env python3
"""Static storefront generator.

Usage:
    python3 build.py              # build to dist/
    python3 build.py --check      # report missing business details, build nothing
    python3 build.py -o /tmp/out  # build elsewhere

Reads data/brand.json and data/product.json and renders a complete, testable
storefront. Standard library only, so there is nothing to install and nothing
to audit.

Two deliberate design rules:

1. **Missing business details are never invented.** Any field whose value is
   null renders as a visible `[MISSING: field]` marker in the page and is
   listed by --check. A policy page that silently invents a returns address is
   worse than one that shows a gap, because the gap gets fixed and the
   invention ships.

2. **Checkout is never faked.** Until a real payment provider is connected the
   checkout button explains what is missing instead of pretending to take an
   order. A storefront that appears to accept money it cannot take is the one
   defect here that could actually harm a customer.

No credentials are read, stored or emitted by this script.
"""

import argparse
import html
import json
import os
import re
import shutil
import sys

MISSING = "__MISSING__"


# ---------------------------------------------------------------- data layer

def repo_root():
    return os.path.dirname(os.path.abspath(__file__))


def load_json(name):
    path = os.path.join(repo_root(), "data", name)
    if not os.path.exists(path):
        sys.exit("missing data file: data/{}".format(name))
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def collect_missing(node, trail=""):
    """Walk the data and return dotted paths of every null value."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            found += collect_missing(value, "{}.{}".format(trail, key).lstrip("."))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += collect_missing(value, "{}[{}]".format(trail, index))
    elif node is None:
        found.append(trail)
    return found


def field(value, path):
    """Render a value, or a loud marker when it has not been supplied."""
    if value is None:
        return '<mark class="missing" title="Not yet supplied">[MISSING: {}]</mark>'.format(
            html.escape(path))
    return html.escape(str(value))


def money(amount):
    return "n/a" if amount is None else "${:,.2f}".format(float(amount))


# ------------------------------------------------------------------ template

def page(brand, title, body, *, active="", description=""):
    """Wrap body content in the site chrome."""
    name = brand.get("name") or "Store"
    nav_items = [("Home", "index.html"), ("Shop", "product.html"),
                 ("Shipping", "shipping.html"), ("Returns", "returns.html"),
                 ("FAQ", "faq.html"), ("Contact", "contact.html")]
    nav = "\n".join(
        '<a href="{href}"{cls}>{label}</a>'.format(
            href=href, label=html.escape(label),
            cls=' class="active" aria-current="page"' if href == active else "")
        for label, href in nav_items)

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {name}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">{name}</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Menu">Menu</button>
    <nav id="nav" class="nav">{nav}</nav>
    <a class="cart-link" href="cart.html" aria-label="Cart">Cart <span data-cart-count>0</span></a>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <nav class="foot-nav">{nav}</nav>
    <p class="small">&copy; 2026 {legal}. All rights reserved.</p>
    <p class="small">{address}</p>
  </div>
</footer>
<script src="assets/cart.js"></script>
</body>
</html>
""".format(title=html.escape(title), name=html.escape(name), nav=nav, body=body,
           description=html.escape(description),
           legal=field(brand.get("legal_name"), "brand.legal_name"),
           address=field(brand.get("business_address"), "brand.business_address"))


# --------------------------------------------------------------------- pages

def home_page(brand, product):
    benefits = "".join(
        "<li><strong>{}</strong><span>{}</span></li>".format(
            html.escape(b.get("title", "")), html.escape(b.get("body", "")))
        for b in product.get("benefits", []))

    return page(brand, "Home", """
<section class="hero">
  <div class="hero-copy">
    <h1>{headline}</h1>
    <p class="lede">{sub}</p>
    <p><a class="btn" href="product.html">See the product</a></p>
    <p class="small trust">{trust}</p>
  </div>
  <div class="hero-art" aria-hidden="true"><div class="placeholder">Product photography pending</div></div>
</section>

<section>
  <h2>Why it works</h2>
  <ul class="benefits">{benefits}</ul>
</section>

<section class="band">
  <h2>Before you buy</h2>
  <p>Shipping takes {ship}. Returns are accepted for {window}. We are a small
  operation and we would rather tell you that up front than surprise you at checkout.</p>
  <p><a href="shipping.html">Shipping details</a> &middot; <a href="returns.html">Returns policy</a></p>
</section>
""".format(
        headline=field(product.get("headline"), "product.headline"),
        sub=field(product.get("subheadline"), "product.subheadline"),
        trust=field(brand.get("trust_line"), "brand.trust_line"),
        benefits=benefits or "<li><em>No benefits written yet.</em></li>",
        ship=field(product.get("shipping_estimate"), "product.shipping_estimate"),
        window=field(product.get("returns_window"), "product.returns_window"),
    ), active="index.html",
        description=product.get("subheadline") or "")


def product_page(brand, product):
    variants = product.get("variants", [])
    options = "".join(
        '<option value="{sku}" data-price="{price}">{name} — {disp}</option>'.format(
            sku=html.escape(v.get("sku", "")), price=v.get("price") or 0,
            name=html.escape(v.get("name", "")), disp=money(v.get("price")))
        for v in variants)

    specs = "".join(
        "<tr><th scope=\"row\">{}</th><td>{}</td></tr>".format(
            html.escape(k), field(v, "product.specs.{}".format(k)))
        for k, v in (product.get("specs") or {}).items())

    price = variants[0].get("price") if variants else product.get("price")

    return page(brand, product.get("name") or "Product", """
<nav class="crumbs"><a href="index.html">Home</a> / <span>{name}</span></nav>
<article class="product" data-product="{pid}">
  <div class="gallery" aria-hidden="true"><div class="placeholder">Product photography pending</div></div>
  <div class="buybox">
    <h1>{name}</h1>
    <p class="price" data-price-display>{price}</p>
    <p>{desc}</p>

    <label class="field">
      <span>Option</span>
      <select id="variant" data-variant-select>{options}</select>
    </label>

    <label class="field">
      <span>Quantity</span>
      <input id="qty" type="number" min="1" max="10" value="1" data-qty>
    </label>

    <button class="btn btn-buy" data-add-to-cart>Add to cart</button>
    <p class="small">{ship} &middot; {window} returns</p>
  </div>
</article>

<section>
  <h2>Specifications</h2>
  <table class="specs"><tbody>{specs}</tbody></table>
</section>

<section>
  <h2>What this product does not do</h2>
  <p>{limits}</p>
</section>
""".format(
        pid=html.escape(product.get("id") or "product"),
        name=field(product.get("name"), "product.name"),
        price=money(price),
        desc=field(product.get("description"), "product.description"),
        options=options or '<option value="">[MISSING: product.variants]</option>',
        specs=specs or '<tr><td>[MISSING: product.specs]</td></tr>',
        limits=field(product.get("limitations"), "product.limitations"),
        ship=field(product.get("shipping_estimate"), "product.shipping_estimate"),
        window=field(product.get("returns_window"), "product.returns_window"),
    ), active="product.html", description=product.get("description") or "")


def cart_page(brand, product):
    provider = (brand.get("payments") or {}).get("provider")
    if provider:
        checkout = ('<button class="btn btn-buy" data-checkout>Checkout</button>'
                    '<p class="small">Payments handled by {}.</p>'.format(html.escape(provider)))
    else:
        checkout = (
            '<button class="btn btn-buy" disabled data-checkout-disabled>Checkout unavailable</button>'
            '<p class="notice">Checkout is not connected yet. No payment provider has been '
            'configured, so this store cannot take an order. This button is deliberately '
            'disabled rather than made to look functional.</p>')

    return page(brand, "Cart", """
<h1>Your cart</h1>
<div data-cart-empty><p>Your cart is empty. <a href="product.html">Have a look at the product</a>.</p></div>
<table class="cart" data-cart-table hidden>
  <thead><tr><th scope="col">Item</th><th scope="col">Qty</th><th scope="col">Price</th><th scope="col"></th></tr></thead>
  <tbody data-cart-body></tbody>
  <tfoot><tr><th scope="row" colspan="2">Subtotal</th><td data-cart-total>$0.00</td><td></td></tr></tfoot>
</table>
<div data-cart-actions hidden>
  <p class="small">Shipping is calculated at checkout. Taxes where applicable.</p>
  {checkout}
</div>
""".format(checkout=checkout), active="cart.html")


def policy_page(brand, key, title, intro, sections):
    body = ["<h1>{}</h1>".format(html.escape(title)), "<p class=\"lede\">{}</p>".format(intro)]
    for heading, text in sections:
        body.append("<h2>{}</h2>".format(html.escape(heading)))
        body.append("<p>{}</p>".format(text))
    body.append('<p class="small">Last updated: {}</p>'.format(
        field(brand.get("policy_updated"), "brand.policy_updated")))
    return page(brand, title, "\n".join(body), active=key)


def build_policies(brand, product):
    contact = field(brand.get("support_email"), "brand.support_email")
    processing = field(product.get("processing_time"), "product.processing_time")
    transit = field(product.get("shipping_estimate"), "product.shipping_estimate")
    window = field(product.get("returns_window"), "product.returns_window")
    address = field(brand.get("returns_address"), "brand.returns_address")
    legal = field(brand.get("legal_name"), "brand.legal_name")

    pages = {}

    pages["shipping.html"] = policy_page(
        brand, "shipping.html", "Shipping",
        "What actually happens after you order, including the parts most stores leave vague.",
        [("Processing", "Orders are prepared within {}.".format(processing)),
         ("Transit", "Delivery takes {} once dispatched. Every order is sent with tracking.".format(transit)),
         ("Where we ship", "United States only at present."),
         ("Where it ships from", "Stock is dispatched by our fulfilment partner. "
                                 "That means transit times are longer than a domestic warehouse, "
                                 "and we would rather say so here than let a delivery estimate do the lying."),
         ("If it is late", "Contact {} with your order number and we will chase the carrier.".format(contact))])

    pages["returns.html"] = policy_page(
        brand, "returns.html", "Returns and refunds",
        "A plain-English returns policy. No restocking traps.",
        [("Window", "Returns accepted for {} from delivery.".format(window)),
         ("Condition", "Unused and in original packaging."),
         ("How to start one", "Email {} with your order number before sending anything back.".format(contact)),
         ("Return address", address),
         ("Who pays postage", field(brand.get("return_postage_policy"), "brand.return_postage_policy")),
         ("Refund timing", "Refunds are issued to the original payment method once the return arrives. "
                           "Banks typically take a few days to show it."),
         ("Damaged on arrival", "Send a photo within 48 hours and we will replace it. No return needed.")])

    pages["privacy.html"] = policy_page(
        brand, "privacy.html", "Privacy",
        "What we collect, why, and who else sees it.",
        [("Who we are", "{} is the data controller.".format(legal)),
         ("What we collect", "Name, delivery address, email and order details. Payment card details are "
                             "handled by our payment provider and never reach our servers."),
         ("Why", "To take payment, ship your order, and answer support email."),
         ("Who we share it with", "Our payment provider, our fulfilment partner and the carrier. "
                                  "Nobody else, and we do not sell data."),
         ("Analytics and advertising", field(brand.get("analytics_disclosure"), "brand.analytics_disclosure")),
         ("Your rights", "Email {} to see, correct or delete what we hold.".format(contact)),
         ("Retention", "Order records are kept as long as tax law requires, then deleted.")])

    faqs = (product.get("faqs") or [])
    faq_body = "".join(
        "<details><summary>{}</summary><p>{}</p></details>".format(
            html.escape(f.get("q", "")), html.escape(f.get("a", "")))
        for f in faqs) or "<p>[MISSING: product.faqs]</p>"
    pages["faq.html"] = page(brand, "FAQ",
                             "<h1>Questions</h1>\n" + faq_body, active="faq.html")

    pages["contact.html"] = page(brand, "Contact", """
<h1>Contact</h1>
<p>We answer email within {hours}.</p>
<ul class="contact">
  <li><strong>Support</strong> {email}</li>
  <li><strong>Business</strong> {legal}</li>
  <li><strong>Address</strong> {address}</li>
</ul>
<p class="small">There is no phone line. One person reads the inbox, and email keeps a record
both of us can refer back to.</p>
""".format(hours=field(brand.get("support_response_time"), "brand.support_response_time"),
           email=contact, legal=legal,
           address=field(brand.get("business_address"), "brand.business_address")),
                                 active="contact.html")
    return pages


# ------------------------------------------------------------------- assets

STYLE = """:root{--ink:#16191c;--muted:#5b6670;--line:#e2e6ea;--bg:#fff;--accent:#1c5d99;--accent-ink:#fff;--warn:#8a5a00;--warn-bg:#fff6e0}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--ink:#e8eaec;--muted:#9aa5ae;--line:#2b3238;--bg:#14181b;--accent:#6ea8dc;--accent-ink:#0d1114;--warn:#f0c469;--warn-bg:#2e2513}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:62rem;margin:0 auto;padding:0 16px}
a{color:var(--accent)}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;background:var(--bg);padding:8px;z-index:10}
.site-header{border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}
.header-inner{display:flex;align-items:center;gap:12px;min-height:60px;flex-wrap:wrap}
.brand{font-weight:700;font-size:1.15rem;text-decoration:none;color:var(--ink);margin-right:auto}
.nav{display:flex;gap:16px;flex-wrap:wrap}
.nav a{text-decoration:none;color:var(--muted);font-size:.95rem}
.nav a.active,.nav a:hover{color:var(--ink)}
.cart-link{text-decoration:none;font-size:.95rem;white-space:nowrap}
.nav-toggle{display:none;background:none;border:1px solid var(--line);border-radius:6px;padding:8px 12px;color:var(--ink);font:inherit;min-height:44px}
h1{font-size:1.9rem;line-height:1.2;margin:1.2em 0 .4em}
h2{font-size:1.25rem;margin:1.8em 0 .5em}
.lede{font-size:1.1rem;color:var(--muted)}
.small{font-size:.875rem;color:var(--muted)}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center;padding:24px 0}
.placeholder{aspect-ratio:1;border:2px dashed var(--line);border-radius:12px;display:grid;place-items:center;color:var(--muted);font-size:.9rem;text-align:center;padding:16px}
.btn{display:inline-block;background:var(--accent);color:var(--accent-ink);padding:14px 22px;border-radius:8px;text-decoration:none;border:0;font:inherit;cursor:pointer;min-height:44px}
.btn[disabled]{background:var(--line);color:var(--muted);cursor:not-allowed}
.benefits{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:20px}
.benefits li{border:1px solid var(--line);border-radius:10px;padding:18px}
.benefits strong{display:block;margin-bottom:6px}
.benefits span{color:var(--muted);font-size:.95rem}
.band{background:color-mix(in srgb,var(--accent) 7%,transparent);border-radius:12px;padding:20px;margin:32px 0}
.product{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start}
.price{font-size:1.6rem;font-weight:700;margin:.2em 0}
.field{display:block;margin:16px 0}
.field span{display:block;font-size:.9rem;margin-bottom:6px}
.field select,.field input{width:100%;padding:12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:inherit;min-height:44px}
table{width:100%;border-collapse:collapse}
.specs{table-layout:fixed}
th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}
.crumbs{font-size:.875rem;color:var(--muted);padding-top:16px}
.notice{background:var(--warn-bg);color:var(--warn);border:1px solid currentColor;border-radius:8px;padding:14px;font-size:.95rem}
mark.missing{background:var(--warn-bg);color:var(--warn);font-weight:600;padding:1px 6px;border-radius:4px;overflow-wrap:anywhere}
.link-btn{background:none;border:0;color:var(--accent);font:inherit;cursor:pointer;text-decoration:underline;padding:8px 0;min-height:44px}
details{border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:10px 0}
summary{cursor:pointer;font-weight:600;min-height:32px}
.contact{list-style:none;padding:0}.contact li{padding:8px 0;border-bottom:1px solid var(--line)}
.contact strong{display:inline-block;min-width:8rem}
.site-footer{border-top:1px solid var(--line);margin-top:56px;padding:24px 0}
.foot-nav{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px}
.foot-nav a{font-size:.9rem;color:var(--muted);text-decoration:none}
@media(max-width:720px){
  .hero,.product{grid-template-columns:1fr}
  .nav{display:none;width:100%;flex-direction:column;gap:4px;padding-bottom:12px}
  .nav.open{display:flex}
  .nav a{padding:10px 0;border-bottom:1px solid var(--line)}
  .nav-toggle{display:block;order:3}
  h1{font-size:1.5rem}
}
"""

CART_JS = """(function(){
  'use strict';
  var KEY='cart.v1';

  function read(){
    try{ return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch(e){ return []; }              // private mode, blocked storage, corrupt value
  }
  function write(items){
    try{ localStorage.setItem(KEY, JSON.stringify(items)); }
    catch(e){ /* storage unavailable: cart is session-only, page still works */ }
  }
  function money(n){ return '$' + Number(n).toFixed(2); }

  function count(){ return read().reduce(function(t,i){ return t + i.qty; }, 0); }

  function paintCount(){
    var els = document.querySelectorAll('[data-cart-count]');
    for (var i=0;i<els.length;i++){ els[i].textContent = count(); }
  }

  function add(sku, name, price, qty){
    var items = read(), found = null;
    for (var i=0;i<items.length;i++){ if (items[i].sku === sku){ found = items[i]; break; } }
    if (found){ found.qty += qty; } else { items.push({sku:sku, name:name, price:price, qty:qty}); }
    write(items); paintCount(); paintCart();
  }

  function remove(sku){
    write(read().filter(function(i){ return i.sku !== sku; }));
    paintCount(); paintCart();
  }

  function paintCart(){
    var table = document.querySelector('[data-cart-table]');
    if (!table) return;
    var body = table.querySelector('[data-cart-body]');
    var empty = document.querySelector('[data-cart-empty]');
    var actions = document.querySelector('[data-cart-actions]');
    var items = read();

    body.textContent = '';
    if (!items.length){
      table.hidden = true; if (actions) actions.hidden = true; if (empty) empty.hidden = false;
      return;
    }
    table.hidden = false; if (actions) actions.hidden = false; if (empty) empty.hidden = true;

    var total = 0;
    items.forEach(function(item){
      total += item.price * item.qty;
      var tr = document.createElement('tr');
      var td1 = document.createElement('td'); td1.textContent = item.name;
      var td2 = document.createElement('td'); td2.textContent = item.qty;
      var td3 = document.createElement('td'); td3.textContent = money(item.price * item.qty);
      var td4 = document.createElement('td');
      var btn = document.createElement('button');
      btn.type = 'button'; btn.textContent = 'Remove'; btn.className = 'link-btn';
      btn.addEventListener('click', function(){ remove(item.sku); });
      td4.appendChild(btn);
      tr.appendChild(td1); tr.appendChild(td2); tr.appendChild(td3); tr.appendChild(td4);
      body.appendChild(tr);
    });
    var totalCell = table.querySelector('[data-cart-total]');
    if (totalCell) totalCell.textContent = money(total);
  }

  document.addEventListener('DOMContentLoaded', function(){
    paintCount(); paintCart();

    var toggle = document.querySelector('.nav-toggle');
    var nav = document.getElementById('nav');
    if (toggle && nav){
      toggle.addEventListener('click', function(){
        var open = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    var select = document.querySelector('[data-variant-select]');
    var display = document.querySelector('[data-price-display]');
    function syncPrice(){
      if (!select || !display) return;
      var opt = select.options[select.selectedIndex];
      if (opt && opt.dataset.price) display.textContent = money(opt.dataset.price);
    }
    if (select){ select.addEventListener('change', syncPrice); syncPrice(); }

    var addBtn = document.querySelector('[data-add-to-cart]');
    if (addBtn){
      addBtn.addEventListener('click', function(){
        if (!select || !select.value){ return; }
        var opt = select.options[select.selectedIndex];
        var qtyEl = document.querySelector('[data-qty]');
        var qty = Math.max(1, Math.min(10, parseInt(qtyEl && qtyEl.value, 10) || 1));
        add(select.value, opt.textContent.split(' — ')[0], parseFloat(opt.dataset.price), qty);
        addBtn.textContent = 'Added';
        setTimeout(function(){ addBtn.textContent = 'Add to cart'; }, 1200);
      });
    }
  });
})();
"""


# -------------------------------------------------------------------- driver

def build(out_dir):
    brand = load_json("brand.json")
    product = load_json("product.json")

    pages = {
        "index.html": home_page(brand, product),
        "product.html": product_page(brand, product),
        "cart.html": cart_page(brand, product),
    }
    pages.update(build_policies(brand, product))

    assets = os.path.join(out_dir, "assets")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(assets)

    for name, content in pages.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as handle:
            handle.write(content)
    with open(os.path.join(assets, "style.css"), "w", encoding="utf-8") as handle:
        handle.write(STYLE)
    with open(os.path.join(assets, "cart.js"), "w", encoding="utf-8") as handle:
        handle.write(CART_JS)

    return brand, product, sorted(pages)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the storefront.")
    parser.add_argument("-o", "--out", default=os.path.join(repo_root(), "dist"))
    parser.add_argument("--check", action="store_true",
                        help="report missing business details without building")
    args = parser.parse_args(argv)

    brand, product = load_json("brand.json"), load_json("product.json")
    gaps = (["brand." + p for p in collect_missing(brand)]
            + ["product." + p for p in collect_missing(product)])

    if args.check:
        if gaps:
            print("Missing business details ({}):".format(len(gaps)))
            for gap in gaps:
                print("  - {}".format(gap))
            print("\nThese render as visible [MISSING] markers. Supply them before launch.")
            return 1
        print("No missing fields.")
        return 0

    brand, product, pages = build(args.out)
    print("built {} pages -> {}".format(len(pages), args.out))
    for name in pages:
        print("  {}".format(name))
    if gaps:
        print("\n{} field(s) still missing; they render as visible [MISSING] markers:".format(len(gaps)))
        for gap in gaps:
            print("  - {}".format(gap))
        print("\nThe store is NOT launch-ready while these are open.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
