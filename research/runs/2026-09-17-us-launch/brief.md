# Research brief: 2026-09-17-us-launch

| Field | Value | Source |
|---|---|---|
| Run ID | 2026-09-17-us-launch | |
| Date started | 2026-09-17 | |
| Market | United States, general consumer, USD | Owner, 2026-09-17 |
| Store platform | Shopify (target); built locally first, see note | Owner, 2026-09-17 |
| Spend authorization | **ZERO.** Nothing may be bought, ordered, subscribed, deployed or launched. | Owner, 2026-09-17 |
| Marketing | Paid ads from day one, plus organic short-form | Owner, 2026-09-17 |
| Selling price band | $25 to $60 | Carried from earlier session |
| Delivery limit | 12 days tracked to a US address | Carried from earlier session |
| Discovery cap | 15 candidates | Lead |
| Deep-research cap | 4 products | Lead |
| Finalist cap | 3 | Lead |
| Enabled paid tools | none | Owner |

## Excluded categories

Branded or licensed goods; supplements; cosmetics and skincare; medical or
health-claim devices; mains-powered or lithium-battery electronics; weapons and
knives; children's toys and baby products; anything requiring FDA, FCC or CPSC
certification.

## Marketing note: paid ads from day one

The owner selected paid ads from day one **and** organic. This changes the
ranking weights: break-even ROAS and creative potential matter more than they
would for an organic-only launch. A product that cannot support a viable
break-even ROAS is rejected even if it looks good organically.

Paid ads cannot actually be launched under zero spend authorization. Ad drafts
and budgets are prepared and held for approval.

## Platform note: Shopify under zero budget

Shopify requires a paid plan and an account, neither of which exists. So:

1. A complete, working storefront is built locally in this repository and can be
   opened and tested now.
2. Alongside it, a Shopify import pack is produced: products CSV in Shopify's
   own column format, page content, policy text and theme copy.
3. When the owner approves a Shopify plan, the pack imports directly. Nothing
   is rebuilt.

## Known source limitations, verified 2026-09-17

The environment's network proxy refuses CONNECT to amazon.com, aliexpress.com,
cjdropshipping.com, reddit.com, trends.google.com, facebook.com, shopify.com,
etsy.com, walmart.com, ebay.com, temu.com and alibaba.com. Every one returns
HTTP 403 at the tunnel, for WebFetch, curl and a headless browser alike.

Consequence: agents cannot read marketplace or supplier pages directly. They use
the server-side WebSearch tool, whose results carry URLs and snippet text but
are second-hand. **Every claim sourced this way is labelled as a search-snippet
observation, not a page read.** This is a real reduction in evidence quality and
is stated in the final report rather than hidden.

Nothing is invented to fill the gap. Where a figure cannot be obtained, it is
recorded as UNKNOWN with the reason.
