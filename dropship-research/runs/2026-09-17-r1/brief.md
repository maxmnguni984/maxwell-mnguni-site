# Run 2026-09-17-r1 — brief

Confirmed with the owner 2026-09-17.

| Item | Value |
|---|---|
| Market | United States, general consumer, USD |
| Niches | home & kitchen problem-solvers, fitness/recovery accessories, pet, car accessories |
| Price band | 25 to 60 USD |
| Delivery cap | 12 days to US, tracked |
| Platform | **Shopify** (confirmed). Not provisioned: needs a paid plan, spend authorization is zero |
| Marketing | **Paid ads from day one** (Meta, TikTok). Organic is supporting only |
| Spend authorization | **ZERO.** Every spend approved individually |

## What the marketing choice changes

Paid-ads-first is funded out of contribution margin on the very first order, so the economics gate is materially stricter than the organic-first version this system originally carried:

| Gate | Organic-first (v1) | Paid-ads-first (v2) |
|---|---|---|
| Base contribution | >= 12 USD | **>= 20 USD** |
| Base margin | >= 35% | **>= 45%** |
| Break-even ROAS | not gated | **<= 2.2** |

Scoring weights moved too: creative potential 20 -> 25 and base economics 20 -> 25, because with cold paid traffic the creative and the margin headroom are what decide whether the store survives.

**A tension worth naming now.** A 25 to 60 USD price band is tight for cold paid traffic. Contribution of 20 USD at 45% implies a net price near 45 USD, so realistically only the upper half of the band can clear the gate. Products near 25 USD will almost all fail G4. If the shortlist comes back thin, the price band is the first thing to revisit, not the gate.

## Environment constraints, verified 2026-09-17

Direct network requests to amazon.com, aliexpress.com, etsy.com, walmart.com, temu.com, alibaba.com, cjdropshipping.com, reddit.com, trends.google.com, shopify.com, google.com and duckduckgo.com all fail at this session's egress proxy. Only the Anthropic-side WebSearch tool reaches the open web.

Consequences, stated plainly:
- No live price, listing, review or Best-Seller rank can be read first-hand. Search snippets are the ceiling.
- Supplier pages cannot be opened, so supplier costs stay CLAIM and mostly UNKNOWN until the owner checks them.
- Anything that needs a live page becomes a manual-check line in `manual-checks.md`, never a guess.

## Agents

| # | Agent | Status |
|---|---|---|
| 1 | Product Discovery | Running |
| 2 | Customer & Competitor | Queued, needs candidates |
| 3 | Supplier & Fulfillment | Queued, needs candidates |
| 4 | Economics & Risk | Queued, needs 2 and 3 |
| 5 | Implementation Lead | Active (this session) |
