# Scoring rubric and hard rejection gates

Applied by the Research Lead after all four worker handoffs exist for a
product. Gates first, score second. A high score can never override a gate.

## Hard gates

Any `fail` = REJECTED, score not computed. Any `unknown` = HOLD, cannot be a
finalist until resolved.

| Gate | Fails if | Evaluated from |
|---|---|---|
| G1 Category | Product is in the excluded list in `brief.md` | discovery |
| G2 IP | Brand, character, patent or trademark risk observed, or the product is a recognisable clone of a branded item | economics-risk |
| G3 Safety / claims | Selling it requires health, medical, safety or efficacy claims, or there is a plausible injury risk, or a CPSC recall on the same product type | economics-risk |
| G4 Platform policy | Prohibited or restricted on Shopify, Meta or TikTok policy pages | economics-risk |
| G5 Delivery | No supplier offers tracked US delivery within the `brief.md` limit (default 12 days) | supplier-research |
| G6 Economics | Base-case contribution margin below $12 or below 35% of net price, or pessimistic-case contribution margin below $0 | economics-risk (`unit_econ.py`) |
| G7 Evidence floor | Fewer than two independent evidence types for demand, or any key economic input is UNKNOWN | lead |
| G8 Price band | Realistic selling price outside the `brief.md` band (default $25 to $60) | competitor-research |

## Score (0 to 100) for products that pass every gate

Each criterion is scored 1 to 5, multiplied by its weight, and the total is
divided by 5 so the maximum is 100.

| Criterion | Weight | 5 | 3 | 1 |
|---|---|---|---|---|
| Demand durability | 20 | At least 2 years of consistent signals, non-seasonal | 6 to 24 months, mild seasonality | Single spike under 6 months |
| Base-case margin | 15 | At least $25 and at least 55% | $18 to $25 or 45% to 55% | $12 to $15 or 35% to 40% |
| Demonstration value | 15 | Problem and solution visible in under 5 seconds of video | Needs one sentence of context | Needs explanation |
| Differentiation credibility | 10 | Clear underserved complaint we can address in content or bundle | Minor angle | Me-too |
| Competition gap | 10 | Few competent stores, weak listings | Several competent stores | Saturated, visible price war |
| Supplier quality | 10 | At least 2 suppliers, verified shipping, 3 or fewer variants | 2 suppliers, claims only | 1 supplier, all claims |
| Operational simplicity | 10 | Light, durable, 3 or fewer variants, no sizing | Some variants or mild fragility | Fragile, oversized, sizing, many variants |
| Channel fit (organic short-form) | 10 | Native to TikTok and Reels formats, easy UGC | Workable with effort | Needs paid reach to explain |

## Confidence

Confidence (low / med / high) is reported next to the score and never folded
into it. It reflects how much of the scoring rests on FACT entries versus
ESTIMATE and ASSUMPTION entries.

## Finalist rule

Finalist = passes all eight gates AND score at least 65 AND confidence at
least medium. Zero, one or two finalists is an acceptable outcome. The report
must say why each non-finalist was rejected or held.
