# Storefront

A complete, working storefront built from data files. It runs with no server, no
account, no subscription and no outbound requests.

## Why local rather than Shopify

The owner chose Shopify, but Shopify needs a paid plan and spend authorization
is zero. So the store is built here and `shopify_export.py` produces everything
Shopify needs in Shopify's own formats. Approving a plan turns this into an
import, not a rebuild.

## Commands

```
python3 store/tools/build_store.py            # build to store/dist
python3 store/tools/build_store.py --check-publishable   # exit 1 while blockers remain
python3 store/tools/verify_store.py           # links, mobile, prices, secrets, a11y
node     store/tools/test_cart.js             # cart logic
python3 store/tools/shopify_export.py         # Shopify import pack
```

Every tool has `--self-test`.

To look at it: `python3 -m http.server 8000 --directory store/dist`

## The rule that shapes this build

The generator never invents a business detail. Any field in `data/store.json`
set to `REQUIRED_FROM_OWNER` renders as a visible "not yet supplied" callout,
every page carries a DRAFT banner, and `--check-publishable` fails.

A shipping policy stating a delivery window nobody verified is worse than no
policy, because customers rely on it and chargebacks follow. So the build
refuses to produce one.

## Structure

| Path | Purpose |
|---|---|
| `data/store.json` | Business details. Placeholders are deliberate. |
| `data/products.json` | Products. Currently a placeholder awaiting selection. |
| `assets/` | CSS and JS. No frameworks, no CDN, no trackers. |
| `tools/` | Generator, verifier, cart tests, Shopify exporter. |
| `dist/` | Generated. Not edited by hand. |
| `dist-shopify/` | Generated Shopify pack. |

## Current state

Draft. 17 blockers, listed by `build_store.py`. The largest is that no product
is selected yet.
