---
product_id: P-0001
run_id: 2026-09-17-r1
agent: lead
date: 2026-09-17
status: complete
confidence: medium
decision: rejected
reject_reason: "No viable price exists. Gates require $49+ retail with all-in delivered cost under $18; the market ceiling is about $24, set by the brand leader's own equivalent kit."
---
# Verdict: dog paw cleaner bundle — REJECTED

## Decision

Reject at the specified price and fulfilment model. The product is not disqualified by intellectual property, safety, demand or platform policy. It is disqualified by arithmetic: **the price the economics demand and the price the market will bear do not overlap.**

This is not a close call, and it is not a failure of the research. The evidence arrived, it was consistent across three independent agents, and it says no.

## Gates

| Gate | Result | Reason |
|---|---|---|
| G0 category | PASS | Not excluded. Sellable as a cleaning tool with no health claim |
| G1 IP and legal | **PASS, conditional** | Far better than feared. See below |
| G2 safety | PASS | No recall found. Mould and material risks are manageable with specification |
| G3 delivery | **FAIL** | 12 days tracked requires US warehousing, which means buying inventory. Not authorised |
| G4 economics | **FAIL** | Passes only at $49 retail with all-in delivered cost at or under $18 |
| G5 demand | PASS | Best dated evidence in the run: 2021 to 2023 across three unrelated accounts plus editorial |
| G6 platform | PASS | Pet supplies permitted by Shopify Payments, Meta and TikTok. Restriction is claim-driven, not category-driven |
| G7 paid viability | **FAIL** | Break-even ROAS 2.71 in the mid case against a 2.2 cap |

## The arithmetic that decides it

Modelled with `scripts/econ.py` using the supplier agent's own cost ranges, and including the US pick-pack and outbound costs that the original 38% rule left out.

| Scenario | Contribution | Margin | BE ROAS | Verdict |
|---|---|---|---|---|
| $49 retail, best case costs ($18 all-in) | $20.50 | 46.5% | 2.15 | PASS, barely |
| $49 retail, mid case ($22 all-in) | $16.28 | 36.9% | 2.71 | FAIL |
| $49 retail, worst case ($30.70 all-in) | $7.10 | 16.1% | 6.21 | FAIL badly |
| $34 retail, mid costs | $3.92 | 12.8% | 7.81 | FAIL |
| $29 retail, mid costs | −$0.20 | −0.8% | n/a | Loses money per order |
| $24 retail, matching the Dexas kit | −$4.33 | −20.0% | n/a | Loses money badly |

The viable window is **$49 retail with all-in delivered cost at or under $18**, and only the best case reaches it.

## Why that window cannot be used

**The market ceiling is about $24, and it is set by the brand leader selling our exact bundle.**

Dexas already ships a paw washer, bathing brush and microfibre towel as one SKU at roughly $24. The standalone cup retails $18.99 at MudBay and $7.50 to $12.99 at Walmart. Three targeted price-bracket searches found **no manual paw-cleaning kit anywhere above about $25**.

So a $49 kit asks a cold-traffic buyer to pay roughly double the brand leader's price for the same three components, against an incumbent with tens of thousands of reviews and shelf presence at every major US pet retailer. The absence of any kit between $25 and $45 is evidence that the rung does not hold weight, not that nobody has tried standing on it.

Two agents flagged this independently and unprompted. The supplier agent raised it as outside its remit but too large to omit. That convergence is worth more than either report alone.

## What changed since the brief was written: de minimis is gone

The single most consequential finding of the run has nothing to do with paw cleaners.

The US $800 de minimis exemption was withdrawn for China and Hong Kong in May 2025, suspended worldwide in August 2025, and permanently repealed effective July 2027. **In 2026 essentially every parcel from every country is dutiable regardless of value.** Reported rates vary and do not reconcile across sources: roughly 30% via commercial carriers, about 37.5% effective for China, and for postal parcels 54% or a **$100 flat fee**.

That last figure is the dangerous one. If a $100 per-parcel flat fee applies to postal shipments, per-order China-direct dropshipping is not marginal for a $49 product, it is dead by a factor of five. **This is unverified and it is the highest-priority manual check in this project**, because it does not merely reject this product. It undermines the per-order dropshipping model itself.

## The intellectual property picture, which is better than expected

Worth recording clearly, because the product was chosen partly on IP grounds and the competitor agent's finding looked alarming.

The category leader holds **design patent D799,126**, granted 2017, covering ornamental appearance only. A visually distinct cup does not infringe it. No paw-cleaner patent litigation and no Amazon enforcement action was found anywhere in the category, and the one Dexas patent suit on record concerned cutting boards. The prior-art field is old and dense, including Paw Plunger's US 7,302,915 with 2005 priority, which also demolishes the "The Original" claim as a matter of fact.

The real exposure is narrower: **US 11,696,567**, in force to about 2039, claims a cup body made of soft material with soft spikes on the inner wall. That reads onto the cheap all-silicone cup most dropship suppliers ship, and not obviously onto the rigid-cup-plus-bristle-insert architecture. No enforcement was found.

So this was **not** the car seat gap filler situation. Had the economics worked, the IP path was a sourcing decision plus a narrow freedom-to-operate opinion. That is worth knowing for the next candidate.

## The opening we found and cannot take

The most repeated complaint is not cleaning power. It is tipping, spillage and needing a third hand: dogs kicking the cup over, muddy water across the porch, owners holding the cup between their feet. No competitor has solved it.

Filling that gap requires a wide non-slip base or catch tray, a secure one-handed grip, and a sealing lid so dirty water can be carried and dumped. **None of that exists off the shelf.** It is a manufacturing brief, not a sourcing brief, and it means tooling, minimum order quantities and inventory capital.

That is a real business. It is not the business that was authorised, and it should not be started by accident.

## What this says about the strategy, not just the product

Three constraints are mutually exclusive, and the paw cleaner is just where they collided first:

1. **Paid ads from day one** force contribution of at least $20 per order, which needs roughly $45 retail
2. **Viral problem-solver products** retail at $10 to $30, which is where their demand comes from
3. **Post-de-minimis import costs** have risen sharply and now apply to every parcel

Any two can be satisfied. All three cannot. Testing another product in the same category will reproduce this result, because the constraint is structural rather than specific to paw cleaners.

## Manual checks, in priority order

1. **Is a $100 flat per-parcel postal fee in force as of September 2026?** This decides whether per-order dropshipping works at all. A customs broker answers it in one call.
2. Open Amazon and record the top ten prices for "dog paw cleaner bundle". If kits cluster under $30, this verdict is confirmed from the demand side too.
3. One real DDP freight quote for 500 kits, stating chargeable weight, the divisor used, and whether duty is included. Only needed if the strategy changes rather than the product.
