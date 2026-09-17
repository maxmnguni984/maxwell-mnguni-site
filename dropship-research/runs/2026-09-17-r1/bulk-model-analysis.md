---
run_id: 2026-09-17-r1
agent: lead
date: 2026-09-17
status: partial
confidence: medium
---
# Bulk import changes which products are viable

The owner has moved from per-order dropshipping to bulk ordering with US warehousing. That replaces air freight with sea, which is the single biggest change to the economics in this project so far.

## What air freight was doing

Freight is billed on **chargeable weight**, the greater of actual and volumetric. Priced that way at $6/kg, air freight killed six of eight candidates from discovery round two, including the discovery agent's own top pick and the candidate with the best demand evidence in the entire project.

| Candidate | Air freight per unit | Contribution | Verdict |
|---|---|---|---|
| Hand-press espresso, 0.34 kg | $3.00 | $46.09 at 58% | Passed |
| Manual burr grinder, 0.6 kg | $4.80 | $45.65 at 57% | Passed |
| Cast-iron citrus press, 4 kg | $24.00 | $23.94 at 30% | Failed, ROAS 3.35 |
| Telescopic pole pruner | $54.00 | −$7.74 | Failed |
| Rooftop cargo bag | $48.00 | −$11.08 | Failed |
| Pet stroller, 15 kg volumetric | $90.00 | −$36.92 | Failed |

Only the two lightest products survived, and they survived across the whole $4 to $10 per kg band. Under air freight, **weight was the binding constraint, not price, demand or competition.**

## What bulk does to that

Two things improve at once. Factory tier pricing at 300 to 1,000 units beats single-unit dropship pricing, modelled here at about 65%. And sea freight is billed per cubic metre rather than per chargeable kilo, which changes the arithmetic for dense goods completely.

Rather than guess at a sea rate we do not have, the question is inverted: **what freight cost per unit can each product afford, and what does that imply per cubic metre?**

Duty at 37.5% on goods, US pick-pack and domestic outbound at $6 per order.

| Candidate | Bulk ex-factory | Max affordable freight | CBM per unit | Implied $/CBM ceiling |
|---|---|---|---|---|
| Hand-press espresso | $10.50 | $13.74 | 0.002 | $6,871 |
| **Cast-iron citrus press** | $10.50 | $13.74 | 0.004 | **$3,436** |
| Rooftop cargo bag | $11.00 | $9.12 | 0.020 | $456 |
| Telescopic pole pruner | $13.00 | $13.06 | 0.030 | $435 |
| Push reel mower | $17.00 | $16.61 | 0.060 | $277 |
| Pet stroller | $17.50 | $15.93 | 0.080 | $199 |
| Litter box cabinet | $19.00 | $13.86 | 0.090 | $154 |

## Reading this table

The ceiling is what the product can pay per cubic metre before the gates fail. Sea LCL China to US West Coast is commonly quoted in the low hundreds per cubic metre, **which is unverified and is exactly what the logistics agent is checking now.**

If that holds:

- **Dense products revive comfortably.** The cast-iron citrus press can absorb roughly $3,400 per cubic metre, an order of magnitude above any plausible rate. It was killed by air freight purely because cast iron is heavy per unit, and sea freight does not care about weight in the same way. This is the product the change most benefits.
- **Mid-bulk products probably revive.** Cargo bag and pole pruner sit around $435 to $456, which should clear a typical LCL rate with room.
- **Very bulky products stay marginal.** The litter box cabinet at $154 and the pet stroller at $199 have little headroom. A rate at the top of the range, or the LCL minimum-charge rule that bills the greater of one cubic metre or 1,000 kg, could still sink them.

## What this does not change

Bulk ordering fixes freight. It does not fix:

- **Patents.** The dog carrier backpack is still rejected: K9 Sport Sack holds US 11,272,685 and is actively suing. Enforcement does not care how you ship.
- **Price floors.** The eleven products rejected for retailing below $50 are still too cheap to fund paid advertising.
- **Capital.** Bulk means paying a factory months before the first customer pays you. The cash conversion cycle is now a real constraint and is being measured.
- **The flat-fee tariff question.** Still unresolved, though a commercial container entry is a different customs path from a postal parcel, and whether the flat per-parcel fee applies at all to containerised cargo is a specific question now being checked.

## Status

Three agents running: sea freight rates and the bulk cost model, a third discovery run scoped to products that were previously uneconomic only because of air freight, and a sourcing-channel ladder covering 1688, Yiwu, sourcing agents and factory-versus-trading-company pricing.

**Nothing has been spent, and spend authorisation remains zero.** Bulk ordering is a sourcing model being researched, not a purchase being made.
