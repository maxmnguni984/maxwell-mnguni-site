---
product_id: P-0000
agent: supplier
run_id: <run-id>
date: <YYYY-MM-DD>
status: complete
confidence: medium
fetch_count: 0
time_minutes: 0
flags: []            # add sample_required when triggered
requests_for_lead: []
---
# <Product name> — supplier & fulfillment

## Summary
<= 5 lines: best supplier option, landed cost range, delivery range vs cap, tracking, whether a sample is required and why.

## Suppliers
| # | Supplier / listing | Platform | Unit cost (USD) @ qty | Ship cost to US | Stated processing | Stated delivery to US | Tracking | Returns | Quality signals (rating, orders, review photos) | MOQ | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|

All numbers above are CLAIM unless marked FACT with a corroborating E-id.

## Landed cost (per unit, product + shipping to US)
- best case: <USD> (CLAIM/ESTIMATE, from supplier #)
- worst case: <USD>
- delivery range (pessimistic end): <days>; delivery_meets_cap: yes | no | unknown
- variants / SKUs that matter:
- packaging / branding options:

## Sample decision
- sample_required: true | false
- triggers hit: safety-relevant (heat, food contact, load-bearing) / quality complaints / variant ambiguity / no review photos
- estimated sample landed cost: <USD>  → if required, add a `purchase` row request in Requests

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
- approval request: purchase — sample of <product> from supplier # — est <USD>
