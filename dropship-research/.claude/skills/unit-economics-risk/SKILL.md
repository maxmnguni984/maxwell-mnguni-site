---
name: unit-economics-risk
description: Method for scenario unit economics (contribution, break-even CAC and ROAS) and the five-category risk register, including the CPSC recall query, IP screening and platform-policy checklist. Use when building or reviewing a product's economics file.
---
# Unit economics & risk method

## Definitions (use these exactly)
- **Contribution per order** = price − discount − product cost − inbound shipping − duty − packaging − payment fee − expected refund loss − expected chargeback loss. It excludes the Shopify plan fee and your time.
- **Payment fee** = price_after_discount × `payment_fee_pct`/100 + `payment_fee_fixed_usd`.
- **Expected refund loss** = `refund_rate_pct`/100 × (price_after_discount + goods cost), i.e. you lose the revenue and the unit.
- **Expected chargeback loss** = `chargeback_rate_pct`/100 × (price_after_discount + goods cost + `chargeback_fee_usd`).
- **Break-even CAC** = contribution per order. Spend more than this to acquire a customer and the order loses money.
- **Break-even ROAS** = price_after_discount ÷ contribution per order. Below this return on ad spend, paid traffic loses money.
- **Orders to recover a 100 USD test** = ceil(100 ÷ contribution).
- Organic CAC is 0 USD in the base case by assumption; the break-even figures exist so a later paid test has a threshold, not because ads are planned.

## Scenario inputs file
Write `data/products/<id>/econ-inputs.yaml`:
```yaml
product_id: P-0007
scenarios:
  pessimistic: {price_usd: 29.00, product_cost_usd: 7.80, shipping_cost_usd: 4.50, duty_rate_pct: 10, discount_rate_pct: 15, refund_rate_pct: 8, chargeback_rate_pct: 1.0, packaging_usd: 0.50}
  base:        {price_usd: 34.00, product_cost_usd: 6.90, shipping_cost_usd: 3.20, duty_rate_pct: 0,  discount_rate_pct: 10, refund_rate_pct: 5, chargeback_rate_pct: 0.5, packaging_usd: 0.50}
  optimistic:  {price_usd: 39.00, product_cost_usd: 6.20, shipping_cost_usd: 2.60, duty_rate_pct: 0,  discount_rate_pct: 5,  refund_rate_pct: 3, chargeback_rate_pct: 0.3, packaging_usd: 0.50}
labels:
  price_usd: "ESTIMATE — median of competitor band, E-0007-C-02"
  product_cost_usd: "CLAIM — supplier #2 listing, E-0007-S-01"
  duty_rate_pct: "UNKNOWN — 2025 US low-value import change; pessimistic placeholder only"
```
Any omitted key falls back to `config/fees.yaml`. The Lead then runs `python3 scripts/econ.py data/products/<id>/econ-inputs.yaml` which writes `economics-calc.md` next to it. Never hand-write the results table.

## Sensitivities (the calculator prints these)
Base case with shipping +3.00 USD, and base case with price −5.00 USD. If either turns contribution negative, say so in the Summary.

## Risk register — how to research each category
1. **IP**: search `site:patents.google.com <product function>` and look for a design/utility patent covering the exact mechanism; check whether the product carries a brand name, character, logo or a recognisable trade dress. A look-alike of a named brand is `fatal`.
2. **Product safety**: query the CPSC recall API (no key needed):
   `https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallTitle=<term>` — use `RecallTitle` and `RecallDescription` exactly; other parameter names silently return the whole database, and there is no pagination. Also consider materials, heat, food contact, choking hazard for small parts, and load-bearing failure.
3. **Misleading claims**: if the product only sells with a health, medical, weight-loss or performance claim, that is a `fatal` G0 problem under the brief. Say which claim would be needed.
4. **Platform restrictions**: check the Shopify Payments prohibited-businesses list, TikTok's commerce/ad policies and Meta's commerce policies for the category. Cite the policy page you read.
5. **Operational**: fragile, heavy or bulky (shipping cost risk), many variants (wrong-item returns), strong seasonality (a cliff after the season), long processing times.

Severity: `fatal` (do not proceed), `high` (needs mitigation before a test), `med`, `low`. Evidence or `UNKNOWN` on every row; never write "no risk found" when you simply could not check — write `UNKNOWN` and queue a manual check.

## Gate outlook
After the register, state plainly which of G1, G2, G4, G6 this product is likely to pass or fail and why. The Lead makes the final gate call.
