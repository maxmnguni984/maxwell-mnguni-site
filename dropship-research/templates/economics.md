---
product_id: P-0000
agent: economics
run_id: <run-id>
date: <YYYY-MM-DD>
status: complete
confidence: medium
fetch_count: 0
time_minutes: 0
flags: []            # add fatal_risk:<category> when any risk is fatal
requests_for_lead: []
---
# <Product name> — unit economics & risk

## Summary
<= 5 lines: base-case contribution and margin, break-even CAC/ROAS, the worst risk and its severity, gate outlook.

## Scenario inputs (also written to econ-inputs.yaml; the Lead runs scripts/econ.py)
| Input | Pessimistic | Base | Optimistic | Label | Source |
|---|---|---|---|---|---|
| price_usd | | | | FACT/ESTIMATE | competitor.md E-ids |
| product_cost_usd | | | | CLAIM | supplier.md E-ids |
| shipping_cost_usd | | | | CLAIM | supplier.md E-ids |
| duty_rate_pct | | | | UNKNOWN until cited | cite current CBP rule |
| discount_rate_pct | | | | ASSUMPTION | config/fees.yaml |
| refund_rate_pct | | | | ASSUMPTION | config/fees.yaml |
| chargeback_rate_pct | | | | ASSUMPTION | config/fees.yaml |

## Results (paste from economics-calc.md after the Lead runs econ.py; do not compute by hand)
See `economics-calc.md`.

## Risk register
| Category | Finding | Severity (fatal/high/med/low) | Evidence or UNKNOWN |
|---|---|---|---|
| IP (brand, patent, licensed look-alike) | | | |
| Product safety (CPSC recalls, materials, heat, choking) | | | |
| Misleading-claims exposure (does selling it require health/performance claims?) | | | |
| Platform restrictions (Shopify Payments, TikTok, Meta) | | | |
| Operational (fragile, heavy, variants, seasonality cliff) | | | |

## Facts

## Estimates

## Assumptions

## Unknowns
- UNAVAILABLE: ...

## Evidence
| E-id | URL | Accessed | Type | What it shows (<= 25 words) | Confidence |
|---|---|---|---|---|---|

## Flags / Risks

## Requests
