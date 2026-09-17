---
run_id: 2026-09-17-r2
agent: lead
date: 2026-09-17
status: complete
confidence: high
scope: methodology
---
# The model was wrong in the founder's favour, twice

Before either threshold could be applied, the calculator had to be fixed. Two of
the problems were arithmetic errors, not missing line items, and both erred in
the same direction: they made products look more profitable than they are.

Everything below is measured by `scripts/model_check.py`, which reimplements the
old formulas alongside the new ones. It is not an assertion.

## Error 1: returns never reversed the refunded revenue

The old formula charged a return `landed x (1 - resellable)`. That treats a
return as though you lose only the unsold goods. A return is a **refund**: the
money goes back, the outbound postage is already spent, you usually pay a share
of the return postage, the processor usually keeps its fee, and someone has to
inspect and restock the unit. What you get back is the unit itself, worth its
landed cost, and only for the resellable share.

| | old | corrected |
|---|---:|---:|
| Return cost per unit shipped, worked example | $1.95 | **$7.33** |

Understated by **$5.38 a unit** on an $89.10 net price.

## Error 2: chargebacks were double-counted

The old formula charged `landed + fulfilment` again on a chargeback, although
both are already subtracted for every unit shipped. In a chargeback the customer
keeps the goods and you lose the money: the loss is the revenue plus the fee.

| | old | corrected |
|---|---:|---:|
| Chargeback cost per unit shipped | $0.57 | **$0.42** |

Overstated by $0.15. Small, and worth fixing because a model that is wrong in
both directions at once cannot be reasoned about.

## What the two corrections do together

| Worked example, identical inputs | contribution | % of net |
|---|---:|---:|
| Old loss formulas | $45.58 | 51.2% |
| **Corrected** | **$40.35** | **45.3%** |

**5.87 margin points.** That is the difference between comfortably clearing a
45% gate and sitting exactly on it, and it applies to every candidate previously
assessed.

## Inconsistency: return postage did not move in the downside

Return postage was copied from outbound postage *before* the scenario
multipliers ran, so a downside case that raised outbound postage by 25% left
return postage at base. Fixed; both now move together.

## Gap 1: dimensional weight, which turns out to matter most

US domestic parcels bill on the **greater of actual and volumetric weight**. The
old model costed postage on mass alone, which flatters exactly the product that
looks cheapest to ship.

| | actual | volumetric | billed | postage |
|---|---:|---:|---:|---:|
| 0.4 kg product in a 40x30x25 cm box | 0.40 kg | 6.00 kg | **6.00 kg** | **$28.00** vs $8.00 assumed |
| Pet stroller | 8.00 kg | 15.84 kg | **15.84 kg** | $44.42 |
| Litter box cabinet | 16.00 kg | 18.00 kg | **18.00 kg** | $49.58 |

This single correction is what removes the two heavy revival candidates from
contention, and it is the reason the supplier inquiry asks for packed carton
dimensions rather than unit weight.

## Gap 2: three real cash costs that were simply absent

| Line | Basis | Worked example |
|---|---|---:|
| Cargo insurance | 0.40% of goods, freight and duty | $0.08 |
| FX slippage | 2.0% on the 70% balance payment | $0.22 |
| Customer support | helpdesk seat and per-order handling | $0.50 |

Small individually, 0.91 margin points together, and all three are real money.

## Gap 3: duty base

Tooling paid to a factory is an assist and is generally part of transaction
value, so it is now dutiable by default, as is factory-supplied retail
packaging. Domestic mailers are not.

## Deliberate choice: the founder's time stays outside contribution

Time is modelled at a stated rate per order and reported as a **separate shadow
line**, never inside contribution. Two reasons: contribution has to stay
comparable across candidates, and a product that only works if you pay yourself
nothing should be visible as one rather than hidden by a plausible hourly rate.

## What the model still does not do

- **No repeat purchase, anywhere.** Every figure is a first order standing alone.
  There is no lifetime-value multiplier in the code and there will not be one
  until measured repeat data exists.
- **No advertising inside contribution.** Advertising is paid out of contribution,
  which is why contribution and break-even CAC are the same number. Profit and
  loss is reported across labelled acquisition-cost scenarios instead, because
  no CAC has been measured for any of these products.
- **Postage rests on a fitted published rate**, not a negotiated rate card:
  `$6.56 + $2.39 per billable kg`, fitted to five published points between
  0.25 kg and 6.5 kg with a maximum error of $0.28. Negotiated third-party
  warehouse rates commonly run 40 to 55% below published. **No rate card has
  been obtained**, so every postage figure here is an upper bound of unknown
  tightness. For the two heavy candidates the rule is extrapolated past the
  fitted range, which is flagged in their specs.
