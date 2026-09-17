# Product research

Bounded funnel to find one physical product a solo founder can source, brand and sell profitably in the US.

## Constraints carried forward

| Constraint | Value | Where it came from |
|---|---|---|
| Market | US, general consumer | Owner decision |
| Retail band | $79 to $149 | Below $79 the gates cannot be met; above $149 the audience narrows |
| Weight | Under 1 kg preferred, over 3 kg disqualified | Domestic last-mile postage is the dominant cost |
| Ex-factory target | 15-20% of retail at 500 units | What the gates require once duty, freight and fulfilment land |
| Fulfilment | Bulk import by sea, US third-party warehouse, domestic parcel | Owner decision |
| Marketing | Paid social from day one | Owner decision |
| Gates | Contribution >= $20 AND >= 45% of net price; break-even ROAS <= 2.2 | Set when paid-ads-first was chosen |

Hard exclusions: ingestibles, health or therapeutic claims, skin cosmetics, lithium batteries, mains plugs, companion apps or cloud dependencies, blades as primary function, branded or licensed goods, adult, children's products under CPSC rules.

## Missing constraints, flagged

1. **Spend authorisation is zero.** A first bulk order is roughly $10,000 to $15,000 plus around $517 a month in warehouse minimums. Nothing here is actionable until a real number is set.
2. **No infrastructure exists.** No warehouse, no store, no customs broker.
3. **No timeline given.**

## What is here

| Path | Contents |
|---|---|
| `scripts/unit_econ.py` | Full-stack unit economics with base, downside and severe scenarios |
| `products/_example.yaml` | A worked example exercising the calculator. Not a real candidate |
| `templates/supplier-inquiry.md` | Twelve-question supplier inquiry. Draft, unsent |

## The calculator

```bash
python3 scripts/unit_econ.py products/<candidate>.yaml --sensitivity
```

It models the whole stack: ex-factory, tooling amortisation, packaging, inbound freight, duty, customs entry, inspection, warehouse receiving, storage, pick and pack, outbound postage, payment and platform fees, returns, defects and chargebacks.

Three things it does deliberately:

**Returns are not a flat percentage of revenue.** A return costs the outbound postage already spent, often the return postage, the payment fee, and whatever the unit loses in resale value. Modelling it as a refund alone understates it badly for a physical good.

**Downside scenarios move together.** A real bad outcome is not one input going wrong. The factory price comes in high *and* the defect rate is worse than promised *and* returns run hot *and* the discount needed to convert is deeper. The scenarios correlate these.

**It says plainly when a business depends on nothing going wrong.** The worked example clears every gate in the base case at 52% margin and $46 contribution, then fails the downside. That is the difference between a markup and a profit, and it is the trap this whole project exists to avoid.

## Ground rules

- An advertised supplier price is not a quote.
- A search snippet does not establish legal clearance or certification.
- Market-size reports and supplier listings are not evidence of demand.
- Advertising activity, including affiliate creator posts, is never evidence of sales.
- Facts, supplier claims, estimates and unknowns stay separated.
