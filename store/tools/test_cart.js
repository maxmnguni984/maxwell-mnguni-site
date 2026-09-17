/* Cart logic tests for assets/js/store.js, run under plain Node.
 *
 *   node store/tools/test_cart.js
 *
 * store.js is written for a browser, so this provides the smallest DOM and
 * storage shim that lets it boot, then exercises the cart through the
 * window.StoreCart handle it exposes.
 *
 * The cart is the one piece of this store that holds a customer's money-facing
 * state, so it gets tested rather than eyeballed. The storage-failure case
 * matters especially: in a private window localStorage throws, and a cart that
 * throws away a customer's basket at checkout is a lost sale.
 */

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const SRC = path.join(__dirname, "..", "assets", "js", "store.js");

let failures = [];
function check(name, cond, detail) {
  if (cond) return;
  failures.push(detail ? name + " — " + detail : name);
}
function eq(name, got, want) {
  check(name, got === want, "got " + JSON.stringify(got) + ", expected " + JSON.stringify(want));
}

/* ------------------------------------------------------------ shims */

function makeStorage(opts) {
  opts = opts || {};
  const map = new Map();
  return {
    getItem(k) {
      if (opts.throwOnRead) throw new Error("storage disabled");
      return map.has(k) ? map.get(k) : null;
    },
    setItem(k, v) {
      if (opts.throwOnWrite) throw new Error("storage disabled");
      map.set(k, String(v));
    },
    removeItem(k) { map.delete(k); },
    _map: map
  };
}

function makeElement(tag) {
  return {
    tagName: tag || "div",
    _attrs: {},
    _listeners: {},
    classList: { add() {}, remove() {}, toggle() { return false; }, contains() { return false; } },
    style: {},
    hidden: false,
    textContent: "",
    innerHTML: "",
    value: "1",
    disabled: false,
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; },
    addEventListener(t, fn) { (this._listeners[t] = this._listeners[t] || []).push(fn); },
    removeEventListener() {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    dispatchEvent() { return true; }
  };
}

function makeContext(storage) {
  const doc = {
    readyState: "complete",
    _listeners: {},
    querySelector() { return null; },
    querySelectorAll() { return []; },
    addEventListener(t, fn) { (this._listeners[t] = this._listeners[t] || []).push(fn); },
    dispatchEvent() { return true; },
    createElement: makeElement
  };
  const win = {
    localStorage: storage,
    setTimeout: (fn) => fn,
    CustomEvent: function (type, init) { this.type = type; this.detail = init && init.detail; },
    STORE: { base: "", currencySymbol: "$", shipping: { flatRate: 0 }, checkout: { provider: null } }
  };
  win.window = win;
  win.document = doc;
  win.console = console;
  return vm.createContext(win);
}

function boot(storage) {
  const ctx = makeContext(storage);
  vm.runInContext(fs.readFileSync(SRC, "utf8"), ctx, { filename: "store.js" });
  if (!ctx.StoreCart) throw new Error("store.js did not expose window.StoreCart");
  return ctx.StoreCart;
}

/* ------------------------------------------------------------ fixtures */

const ITEM_A = {
  handle: "widget", title: "Widget", variantId: "black", variantLabel: "Black",
  priceCents: 3999, qty: 1, url: "product.html"
};
const ITEM_A_WHITE = Object.assign({}, ITEM_A, { variantId: "white", variantLabel: "White" });
const ITEM_B = {
  handle: "gadget", title: "Gadget", variantId: null, variantLabel: null,
  priceCents: 2499, qty: 2, url: "product.html"
};

/* ------------------------------------------------------------ tests */

// 1. Empty cart.
let cart = boot(makeStorage());
eq("empty cart count", cart.count(), 0);
eq("empty cart subtotal", cart.subtotal(), 0);
check("empty cart reads as array", Array.isArray(cart.read()));

// 2. Add one item.
cart.add(Object.assign({}, ITEM_A));
eq("count after one add", cart.count(), 1);
eq("subtotal after one add", cart.subtotal(), 3999);

// 3. Adding the same variant merges rather than duplicating.
cart.add(Object.assign({}, ITEM_A, { qty: 2 }));
eq("lines after re-adding same variant", cart.read().length, 1);
eq("quantity merged", cart.read()[0].qty, 3);
eq("subtotal after merge", cart.subtotal(), 3999 * 3);

// 4. A different variant of the same product is its own line.
cart.add(Object.assign({}, ITEM_A_WHITE));
eq("different variant makes a new line", cart.read().length, 2);
eq("count across variants", cart.count(), 4);

// 5. A different product is its own line, and quantity is respected.
cart.add(Object.assign({}, ITEM_B));
eq("lines with second product", cart.read().length, 3);
eq("count with second product", cart.count(), 6);
eq("subtotal with second product", cart.subtotal(), 3999 * 3 + 3999 + 2499 * 2);

// 6. Quantity edits.
const keyA = cart.lineKey(ITEM_A);
cart.setQty(keyA, 1);
eq("setQty reduces the line", cart.read().find((i) => cart.lineKey(i) === keyA).qty, 1);

// 7. Setting quantity to zero removes the line, it does not leave a ghost.
cart.setQty(keyA, 0);
check("zero quantity removes the line", !cart.read().some((i) => cart.lineKey(i) === keyA));
eq("lines after removal", cart.read().length, 2);

// 8. Explicit remove.
cart.remove(cart.lineKey(ITEM_B));
eq("lines after remove", cart.read().length, 1);

// 9. Quantity is capped, so a fat finger cannot order 10,000 units.
cart.add(Object.assign({}, ITEM_B, { qty: 99 }));
cart.add(Object.assign({}, ITEM_B, { qty: 99 }));
const capped = cart.read().find((i) => i.handle === "gadget");
eq("quantity is capped at 99", capped.qty, 99);

// 10. Money formatting.
eq("money formats cents", cart.money(3999), "$39.99");
eq("money formats zero", cart.money(0), "$0.00");
eq("money formats a round figure", cart.money(4000), "$40.00");
eq("money formats a large figure", cart.money(123456), "$1234.56");

// 11. Subtotal arithmetic is exact in integer cents, no float drift.
let exact = boot(makeStorage());
for (let i = 0; i < 3; i++) {
  exact.add({ handle: "p" + i, title: "P" + i, variantId: null, priceCents: 1010, qty: 1 });
}
eq("three items at $10.10 total exactly $30.30", exact.subtotal(), 3030);
eq("and format without drift", exact.money(exact.subtotal()), "$30.30");

// 12. Persistence across a page load: a new boot on the same storage sees the cart.
const shared = makeStorage();
const first = boot(shared);
first.add(Object.assign({}, ITEM_A));
const second = boot(shared);
eq("cart survives a page load", second.count(), 1);
eq("and its subtotal", second.subtotal(), 3999);

// 13. Storage that throws on write must not lose the basket for this session.
const noWrite = boot(makeStorage({ throwOnWrite: true }));
noWrite.add(Object.assign({}, ITEM_A));
eq("cart still works when storage writes throw", noWrite.count(), 1);
noWrite.add(Object.assign({}, ITEM_B));
eq("and keeps accumulating in memory", noWrite.count(), 3);

// 14. Storage that throws on read must not crash the page.
let readThrew = false;
try {
  const noRead = boot(makeStorage({ throwOnRead: true }));
  noRead.add(Object.assign({}, ITEM_A));
  eq("cart works when storage reads throw", noRead.count(), 1);
} catch (err) {
  readThrew = true;
}
check("a throwing storage read must not crash boot", !readThrew);

// 15. Corrupt stored data is ignored rather than crashing the store.
const corrupt = makeStorage();
corrupt.setItem("store.cart.v1", "{not json at all");
let corruptOk = true;
try {
  const c = boot(corrupt);
  eq("corrupt cart data reads as empty", c.count(), 0);
} catch (err) {
  corruptOk = false;
}
check("corrupt storage must not crash boot", corruptOk);

// 16. Stored data of the wrong shape is ignored too.
const wrongShape = makeStorage();
wrongShape.setItem("store.cart.v1", '{"nope":true}');
const w = boot(wrongShape);
eq("non-array cart data reads as empty", w.count(), 0);

/* ------------------------------------------------------------ report */

if (failures.length) {
  console.log("CART TESTS FAILED");
  failures.forEach((f) => console.log("  - " + f));
  process.exit(1);
}
console.log("test_cart.js: all 16 cart checks passed");
