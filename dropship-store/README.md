# Storefront

A working, testable storefront built from two JSON files. Standard library Python, no dependencies, nothing to install.

```bash
python3 build.py            # render dist/
python3 build.py --check    # list missing business details, build nothing
NODE_PATH=/opt/node22/lib/node_modules node verify.js   # drive it in a real browser
```

## Two rules this build enforces mechanically

**Missing business details are never invented.** Any `null` in `data/brand.json` or `data/product.json` renders as a loud `[MISSING: field]` marker on the page, is listed by `--check`, and makes the build print that the store is not launch-ready. A returns policy with an invented address is worse than one with a visible gap, because the gap gets fixed and the invention ships to a customer.

**Checkout is never faked.** While `brand.payments.provider` is null, the checkout button is disabled and says why. `verify.js` fails the build if a live checkout button ever appears without a configured provider. A store that looks like it can take money it cannot take is the one defect here that could actually harm someone.

## Current state

The data files hold a structural placeholder, not a product. Real content lands once the owner selects from the research shortlist. 16 business details are outstanding; `--check` lists them.

## Verification

`verify.js` serves `dist/` and drives it in Chromium at desktop and 390px mobile. It checks internal links, heading structure, variant price switching, cart quantity maths, the disabled checkout, mobile horizontal overflow, the collapsed nav, and 44px tap targets. It writes mobile screenshots to `screenshots/`.

Last run: **14/14 passed**. It has already caught one real bug, a specs table forcing horizontal scroll at 390px, which is now fixed.
