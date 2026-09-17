/* Storefront behaviour: cart, variants, gallery, mobile nav.
   No dependencies, no external requests, no tracking.

   The cart lives in localStorage. Every read and write is wrapped, because
   storage throws in private windows and in embedded previews, and a store that
   blanks out when storage is unavailable is worse than one that quietly
   degrades to an in-memory cart for the session. */

(function () {
  "use strict";

  var CART_KEY = "store.cart.v1";

  /* Storage state. In a private window, with site data blocked, or inside an
     embedded preview, localStorage can throw on read, on write, or on both.
     Once either direction fails we stop trusting storage for the rest of the
     session and keep the basket in memory instead.

     Falling back on write alone is not enough: if reads throw but writes
     succeed, every read returns nothing and the customer watches their basket
     empty itself. So the fallback latches. */
  var storageOk = true;
  var memoryCart = [];

  function disableStorage() {
    storageOk = false;
  }

  function readCart() {
    if (!storageOk) return memoryCart;
    try {
      var raw = window.localStorage.getItem(CART_KEY);
      if (!raw) return [];
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) {
      // A JSON error means corrupt data, which we can clear and carry on from.
      // A storage error means the mechanism itself is unavailable.
      if (e instanceof SyntaxError) {
        try { window.localStorage.removeItem(CART_KEY); } catch (e2) { disableStorage(); }
        return storageOk ? [] : memoryCart;
      }
      disableStorage();
      return memoryCart;
    }
  }

  function writeCart(items) {
    if (storageOk) {
      try {
        window.localStorage.setItem(CART_KEY, JSON.stringify(items));
      } catch (e) {
        disableStorage();
      }
    }
    if (!storageOk) memoryCart = items;
    updateCartCount();
    document.dispatchEvent(new CustomEvent("cart:changed", { detail: items }));
  }

  /* ------------------------------------------------------------ money */

  function money(cents) {
    var symbol = (window.STORE && window.STORE.currencySymbol) || "$";
    return symbol + (cents / 100).toFixed(2);
  }

  function toCents(value) {
    return Math.round(Number(value) * 100);
  }

  /* ------------------------------------------------------------ cart ops */

  function lineKey(item) {
    return item.handle + "::" + (item.variantId || "default");
  }

  function addToCart(item) {
    var items = readCart().slice();
    var key = lineKey(item);
    var existing = null;
    for (var i = 0; i < items.length; i++) {
      if (lineKey(items[i]) === key) { existing = items[i]; break; }
    }
    if (existing) {
      existing.qty = Math.min(99, existing.qty + item.qty);
    } else {
      items.push(item);
    }
    writeCart(items);
    return items;
  }

  function setQty(key, qty) {
    var items = readCart().slice();
    var out = [];
    for (var i = 0; i < items.length; i++) {
      if (lineKey(items[i]) === key) {
        if (qty > 0) { items[i].qty = Math.min(99, qty); out.push(items[i]); }
      } else {
        out.push(items[i]);
      }
    }
    writeCart(out);
    return out;
  }

  function removeLine(key) { return setQty(key, 0); }

  function cartCount() {
    return readCart().reduce(function (n, i) { return n + i.qty; }, 0);
  }

  function cartSubtotalCents() {
    return readCart().reduce(function (n, i) { return n + i.priceCents * i.qty; }, 0);
  }

  function updateCartCount() {
    var els = document.querySelectorAll("[data-cart-count]");
    var n = cartCount();
    for (var i = 0; i < els.length; i++) {
      els[i].textContent = String(n);
      els[i].hidden = n === 0;
    }
  }

  /* ------------------------------------------------------------ mobile nav */

  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ------------------------------------------------------------ gallery */

  function initGallery() {
    var main = document.querySelector("[data-gallery-main]");
    var thumbs = document.querySelectorAll("[data-gallery-thumb]");
    if (!main || !thumbs.length) return;
    for (var i = 0; i < thumbs.length; i++) {
      (function (btn) {
        btn.addEventListener("click", function () {
          var src = btn.getAttribute("data-src");
          var alt = btn.getAttribute("data-alt") || "";
          main.innerHTML = '<img src="' + src + '" alt="' + alt + '">';
          for (var j = 0; j < thumbs.length; j++) {
            thumbs[j].setAttribute("aria-current", thumbs[j] === btn ? "true" : "false");
          }
        });
      })(thumbs[i]);
    }
  }

  /* ------------------------------------------------------------ product */

  function initProduct() {
    var form = document.querySelector("[data-product-form]");
    if (!form) return;

    var handle = form.getAttribute("data-handle");
    var title = form.getAttribute("data-title");
    var basePrice = toCents(form.getAttribute("data-price"));
    var available = form.getAttribute("data-available") === "true";

    var selected = { id: null, label: null, priceCents: basePrice };

    var priceEl = document.querySelector("[data-price-display]");
    var addBtn = form.querySelector("[data-add-to-cart]");
    var feedback = document.querySelector("[data-add-feedback]");

    var optionButtons = form.querySelectorAll("[data-variant]");
    if (optionButtons.length) {
      var choose = function (btn) {
        for (var j = 0; j < optionButtons.length; j++) {
          optionButtons[j].setAttribute("aria-pressed", optionButtons[j] === btn ? "true" : "false");
        }
        selected.id = btn.getAttribute("data-variant");
        selected.label = btn.getAttribute("data-variant-label");
        var vp = btn.getAttribute("data-variant-price");
        selected.priceCents = vp ? toCents(vp) : basePrice;
        if (priceEl) priceEl.textContent = money(selected.priceCents);
        if (addBtn && available) addBtn.disabled = false;
      };
      for (var i = 0; i < optionButtons.length; i++) {
        (function (btn) {
          btn.addEventListener("click", function () { choose(btn); });
        })(optionButtons[i]);
      }
      // Preselect the first in-stock variant so the page is usable immediately.
      for (var k = 0; k < optionButtons.length; k++) {
        if (!optionButtons[k].disabled) { choose(optionButtons[k]); break; }
      }
    }

    var qtyInput = form.querySelector("[data-qty-input]");
    var dec = form.querySelector("[data-qty-dec]");
    var inc = form.querySelector("[data-qty-inc]");
    function currentQty() {
      var n = parseInt(qtyInput ? qtyInput.value : "1", 10);
      return isNaN(n) || n < 1 ? 1 : Math.min(99, n);
    }
    if (dec) dec.addEventListener("click", function () {
      if (qtyInput) qtyInput.value = String(Math.max(1, currentQty() - 1));
    });
    if (inc) inc.addEventListener("click", function () {
      if (qtyInput) qtyInput.value = String(Math.min(99, currentQty() + 1));
    });
    if (qtyInput) qtyInput.addEventListener("change", function () {
      qtyInput.value = String(currentQty());
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!available) return;
      if (optionButtons.length && !selected.id) {
        if (feedback) feedback.textContent = "Choose an option first.";
        return;
      }
      addToCart({
        handle: handle,
        title: title,
        variantId: selected.id,
        variantLabel: selected.label,
        priceCents: selected.priceCents,
        qty: currentQty(),
        url: form.getAttribute("data-url") || ""
      });
      if (feedback) {
        feedback.textContent = "Added to cart.";
        window.setTimeout(function () { feedback.textContent = ""; }, 4000);
      }
    });
  }

  /* ------------------------------------------------------------ cart page */

  function renderCart() {
    var root = document.querySelector("[data-cart-root]");
    if (!root) return;
    var items = readCart();

    if (!items.length) {
      root.innerHTML =
        '<div class="empty"><p>Your cart is empty.</p>' +
        '<p><a class="btn btn-secondary" href="' +
        ((window.STORE && window.STORE.base) || "") + 'index.html">Continue shopping</a></p></div>';
      return;
    }

    var rows = "";
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      var key = lineKey(it);
      rows +=
        '<tr>' +
        '<td><div class="cart-item-title">' + escapeHtml(it.title) + '</div>' +
        (it.variantLabel ? '<div class="cart-item-variant">' + escapeHtml(it.variantLabel) + '</div>' : '') +
        '<button class="link-btn" data-remove="' + escapeAttr(key) + '">Remove</button></td>' +
        '<td>' + money(it.priceCents) + '</td>' +
        '<td><div class="qty"><button type="button" data-line-dec="' + escapeAttr(key) + '" aria-label="Decrease quantity">&minus;</button>' +
        '<input type="number" min="1" max="99" value="' + it.qty + '" data-line-qty="' + escapeAttr(key) + '" aria-label="Quantity">' +
        '<button type="button" data-line-inc="' + escapeAttr(key) + '" aria-label="Increase quantity">+</button></div></td>' +
        '<td>' + money(it.priceCents * it.qty) + '</td>' +
        '</tr>';
    }

    var subtotal = cartSubtotalCents();
    var shipping = (window.STORE && window.STORE.shipping) || null;
    var shippingLine = "Calculated at checkout";
    if (shipping && shipping.flatRate === 0) shippingLine = "Free";
    else if (shipping && typeof shipping.flatRate === "number") shippingLine = money(toCents(shipping.flatRate));

    root.innerHTML =
      '<table class="cart-table"><thead><tr>' +
      '<th>Item</th><th>Price</th><th>Quantity</th><th>Total</th>' +
      '</tr></thead><tbody>' + rows + '</tbody></table>' +
      '<div class="totals">' +
      '<div><span>Subtotal</span><span>' + money(subtotal) + '</span></div>' +
      '<div><span>Shipping</span><span>' + shippingLine + '</span></div>' +
      '<div class="grand"><span>Total</span><span>' + money(subtotal) + '</span></div>' +
      '</div>' +
      checkoutBlock();

    bindCartRows(root);
  }

  function checkoutBlock() {
    var cfg = (window.STORE && window.STORE.checkout) || {};
    if (!cfg.provider) {
      return '<div class="notice"><strong>Checkout is not connected.</strong> ' +
        'No payment provider is configured for this build, so no order can be ' +
        'placed and no card details are collected anywhere on this site. The ' +
        'cart above is fully functional and its totals are real. Connecting a ' +
        'payment provider requires an account and a subscription, which need ' +
        'the owner’s approval.</div>' +
        '<button class="btn btn-block" disabled>Checkout unavailable</button>';
    }
    return '<button class="btn btn-block" data-checkout>Proceed to checkout</button>';
  }

  function bindCartRows(root) {
    function each(sel, fn) {
      var els = root.querySelectorAll(sel);
      for (var i = 0; i < els.length; i++) fn(els[i]);
    }
    each("[data-remove]", function (el) {
      el.addEventListener("click", function () {
        removeLine(el.getAttribute("data-remove"));
        renderCart();
      });
    });
    each("[data-line-dec]", function (el) {
      el.addEventListener("click", function () {
        var key = el.getAttribute("data-line-dec");
        var line = find(key);
        if (line) { setQty(key, line.qty - 1); renderCart(); }
      });
    });
    each("[data-line-inc]", function (el) {
      el.addEventListener("click", function () {
        var key = el.getAttribute("data-line-inc");
        var line = find(key);
        if (line) { setQty(key, line.qty + 1); renderCart(); }
      });
    });
    each("[data-line-qty]", function (el) {
      el.addEventListener("change", function () {
        var n = parseInt(el.value, 10);
        setQty(el.getAttribute("data-line-qty"), isNaN(n) || n < 1 ? 1 : n);
        renderCart();
      });
    });
  }

  function find(key) {
    var items = readCart();
    for (var i = 0; i < items.length; i++) {
      if (lineKey(items[i]) === key) return items[i];
    }
    return null;
  }

  /* ------------------------------------------------------------ escaping */

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function escapeAttr(s) { return escapeHtml(s); }

  /* ------------------------------------------------------------ boot */

  function init() {
    initNav();
    initGallery();
    initProduct();
    updateCartCount();
    renderCart();
    document.addEventListener("cart:changed", function () {
      if (document.querySelector("[data-cart-root]")) renderCart();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Exposed for the verification harness.
  window.StoreCart = {
    read: readCart, write: writeCart, add: addToCart, setQty: setQty,
    remove: removeLine, count: cartCount, subtotal: cartSubtotalCents,
    money: money, lineKey: lineKey
  };
})();
