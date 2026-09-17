---
run_id: 2026-09-17-r1
agent: lead
date: 2026-09-17
status: complete
confidence: medium
decision: no_candidate_clears
---
# Final shortlist: no candidate clears the gates

Three discovery rounds, five research agents, roughly 40 products screened. **Nothing passes.** That is the finding, and it is worth more than a product I would have to talk you into.

## A correction against my own working

In the sensitivity run I printed a summary claiming the citrus press works at "FOB at or under $15 and postage at or under $12" at $79, and at several combinations at $99. **The table directly above that text contradicted it.** Exactly one cell passes: $99 retail, $12 free-on-board, $8 postage. Everything else fails.

I wrote the conclusion from expectation rather than from the output. The table is right and the sentence was wrong. Flagging it because the same error, uncaught, is how a business case gets built on a number nobody checked.

## What actually kills every candidate

The gates are contribution of at least $20, at least 45% of net price, and break-even return on ad spend at or under 2.2. The margin gate is what fails, and the reason is cumulative rather than any single line:

For a $99 product at a $22 factory price:

| Line | Cost |
|---|---|
| Goods, free on board | $22.00 |
| Duty at 23.4% | $5.15 |
| Sea freight | $7.00 |
| Entry, brokerage, bond, fees amortised | $2.60 |
| Pick, pack and storage | $3.00 |
| Packaging | $0.50 |
| **Before a parcel moves** | **$40.25** |
| US last mile, 6 kg | $13 to $22 |
| **Total** | **$53 to $62** |

That is 54 to 63% of retail before a single advertising dollar. The 45% margin requirement cannot survive it.

## The candidates, and where each died

| Product | Died on |
|---|---|
| Dog paw cleaner bundle | Market ceiling $24 against a $45 gate minimum |
| Car seat gap filler | US Patent 8,267,291, Federal Circuit litigation |
| Reusable pet hair roller | Enforced utility patent, 320+ Amazon takedowns |
| Dog carrier backpack | K9 Sport Sack, US 11,272,685, actively suing |
| Smokeless fire pit | Solo Brands, two patents, sued Coleman and City Bonfires |
| Squirrel-proof feeder | Brome's patented mechanism is the entire product |
| Manual burr grinder | Comandante design patent family, proceedings against Kingrinder |
| Hand-press espresso maker | 2026 CPSC recall, 107 hot-liquid reports, 27 burn injuries |
| Cast-iron citrus press | Margin. Passes only at $99 with $12 FOB and $8 postage |
| Pet stroller | Margin. Fails at $149 even on aggressive negotiated postage |
| Litter box cabinet | Margin. 18 kg costs $24 to $54 in last-mile alone |
| Rooftop cargo bag, pole pruner, reel mower, hose reel, dog bath, deck box, compost tumbler, hitch carrier, kitchen cart | Margin, price floor, or freight |
| Eleven further products | Retail below the $50 floor |

## The two patterns worth keeping

**The best demos sit on enforced patents.** Six products died this way. It is not coincidence: a product that demonstrates instantly on camera is a product worth patenting and worth defending. Any future candidate with a great five-second demo should be assumed patented until a search says otherwise.

**Weight is punished at every stage, and the last stage is the worst.** Sea freight made the China leg trivial, $0.55 to $11 a unit. Then US last-mile charges $13 to $54 for the same box. The citrus press pays $7 to cross the Pacific and up to $22 to cross Ohio. Bulk ordering did not solve the weight problem, it relocated it.

## What the evidence says the product must look like

Working backwards from every failure, the surviving shape is narrow and specific:

| Attribute | Requirement | Why |
|---|---|---|
| Weight | **Under 1 kg** | Last mile is the binding cost. Under 1 kg it is about $8, at 18 kg it is $54 |
| Factory price | **At or under 15% of retail** | Duty, freight, handling and fees consume the rest |
| Retail | **$79 to $149** | Below this, contribution cannot reach $20 |
| Intellectual property | No live utility patent, distinct appearance | Six deaths already |
| Safety | No pressure, heat, load-bearing or ingestion | The espresso press died here |
| Demo | Instant and visual | Paid traffic requires it |

Exactly one product in this entire project met the first three: the hand-press espresso maker at 0.34 kg. It cleared the economics comfortably, at $46 contribution and 58% margin, and died on a recall history and an unresolved patent instead.

That is not a coincidence either. **Light, high-value, cheap to make, visually striking** describes a product category that others have already found and protected.

## The decision this leaves

Four honest options.

**1. Hunt specifically for light, high-value products.** Under 1 kg, $79 to $149, factory price under 15% of retail. A narrow brief, but it is the only shape the arithmetic supports, and no round has searched for it directly.

**2. Relax the margin gate.** The 45% threshold, which is break-even return on ad spend of 2.2, is strict for a first product. Real stores survive at 2.5 to 3.0 on repeat purchase and larger baskets. Neither is modelled here. Moving the gate to 35% and a break-even of 2.9 would revive the citrus press and the litter box cabinet. **It would also mean accepting that early orders roughly break even and the business depends on repeat purchase that has not been demonstrated.**

**3. Return to organic-first.** The gate drops to $12 and 35%, and most rejected candidates clear it. Slower, free, and contradicts the paid-ads decision.

**4. Accept the structural finding.** Single-item physical goods from China, sold on paid advertising from day one by a solo operator, is genuinely hard in 2026. Duty has replaced de minimis, postage is up about 16% year on year, and the well-demoing products are patented.

**My recommendation is one, with two as a deliberate fallback.** The light high-value brief has never been run, and it is where the one product that cleared the economics came from. If that round also comes back empty, that is the answer to option four and worth knowing.

## What is built and waiting

The storefront is complete and passing all 14 browser checks. The Shopify exporter works. Brand, copy and policies are the only remaining build work and they need a product first.

**Nothing has been spent. Spend authorisation remains zero.**

## The three checks that would settle this fastest

1. **One factory quote.** 500 units, free on board, for any shortlisted item. Every cost figure in this project is an estimate from material mass. Nobody has quoted anything.
2. **One 3PL rate card.** Negotiated parcel rates by weight. This single number moves the citrus press between fail and pass.
3. **One customs classification.** The tariff code decides whether duty is 23% or 41%, and whether cast iron triggers steel duty at 50%.
