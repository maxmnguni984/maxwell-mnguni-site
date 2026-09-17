---
run_id: 2026-09-17-r2
agent: lead
date: 2026-09-17
status: complete
confidence: medium
scope: the three candidates previously rejected on margin alone
---
# Relaxing the gate to 35% does not revive them. I was wrong about that.

## The correction first

In `dropship-research/runs/2026-09-17-r1/FINAL-shortlist.md` I wrote:

> Moving the gate to 35% and a break-even of 2.9 would revive the citrus press
> and the litter box cabinet.

**That is false.** Re-run under the corrected model, at the conditional 35%
threshold you authorised:

| Candidate | Contribution | % of net | Band |
|---|---:|---:|---|
| Cast-iron citrus press @ $79 | $23.99 | **33.7%** | below both |
| Pet stroller @ $149 | $10.91 | **8.1%** | below both |
| Litter box cabinet @ $149 | $3.74 | **2.8%** | below both |

The citrus press misses the conditional floor by 1.3 points. The other two are
not close to it and never were — the litter box cabinet is off by 32 points.

The earlier claim was made on the pre-correction model, which understated
returns and costed postage on mass rather than volume. It should have been
recomputed before it was written down. Flagging it because you were asked to
choose a threshold partly on the strength of it.

## Where the money actually goes

For both heavy candidates, **US domestic postage is larger than the entire
landed cost** — larger than making the product in China, shipping it across the
Pacific, clearing customs and receiving it into a warehouse, combined.

| | Landed cost | Outbound postage | Net price |
|---|---:|---:|---:|
| Litter box cabinet | $43.17 | **$49.58** | $134.10 |
| Pet stroller | $39.58 | **$44.42** | $134.10 |
| Citrus press @ $79 | $16.36 | $16.12 | $71.10 |

And both bill on **volume, not mass**. The pet stroller weighs 8 kg and is
billed at 15.84 kg. Its carton is the product as far as the carrier is
concerned.

Returns compound it. A returned stroller costs $22.69 a unit averaged across all
units shipped, because the refund, two lots of postage on a bulky box, the
processor's fee and a 45% resale recovery all land at once.

## The one that survives, and the condition attached

The cast-iron citrus press clears **band A at $99**: $40.28 contribution, 45.2%
of net, break-even ROAS 2.21. At $79 it fails both bands.

So the entire question is whether an unknown brand can hold $99 against an
observed comparable at **$72.19** — a 37% premium, to a cold-traffic buyer, with
no reviews and no brand. That is the same shape of problem that killed the paw
cleaner, which needed a 100% premium. Smaller in degree, identical in kind.

It also carries an unresolved legal question that decides it outright: **whether
Section 232 steel duty at 50% applies to cast iron.** If it does, the product
fails at $99 and needs $119, which is a 65% premium to the incumbent.

And it does not survive its own downside: contribution falls to $17.48, band
NEITHER. At a $25 acquisition cost the downside case loses $7.52 an order.

## What "conditional" would actually have meant, priced

Since the citrus press at $79 is the closest thing to a band B candidate the
project has produced, here is what selling it at 33.7% looks like with
advertising costed, rather than described as roughly breaking even:

| Acquisition cost per order | Base | Downside |
|---|---:|---:|
| $15 | +$8.99 | −$12.08 |
| $25 | −$1.01 | −$22.08 |
| $40 | −$16.01 | −$37.08 |
| $60 | −$36.01 | −$57.08 |

Break-even CAC is $23.99 in the base case and $2.92 in the downside. For
advertising to pay for itself at a $0.87 cost per click, **3.63% of visitors
must buy** in the base case and **29.8%** in the downside. A 2% conversion rate
is already an optimistic figure for cold paid traffic to an unknown brand.

That is what a 33.7% product means in practice. Not break-even — a business that
requires a conversion rate nobody has demonstrated.

## Upfront cash and quantity

| Candidate | Upfront cash | Units | MOQ | Orders to recover |
|---|---:|---:|---:|---:|
| Citrus press @ $99 | $9,179.51 | 500 | 500 | 228 of 500 |
| Citrus press @ $79 | $9,179.51 | 500 | 500 | 383 of 500 |
| Pet stroller | $9,653.26 | 300 | 300 | 885 of 300 — **more orders than units** |
| Litter box cabinet | $11,177.20 | 300 | 300 | 2,989 of 300 — **impossible** |

The last two lines are the clearest statement of the result: you cannot sell
your way out of those orders, because each order recovers less than 1/300th of
what the order cost.

## Evidence quality: LOW for all four

No supplier has quoted anything. No HTS code has been classified. No rate card
exists. Ex-factory prices are estimates from material mass. The retail anchor is
one observed comparable. Every number above inherits that.

## What must be verified before any of this is actionable

1. **Does Section 232 apply to cast iron?** This one question decides the only
   surviving candidate. A customs broker answers it for a few hundred dollars.
2. **An 8-digit HTS classification** for the specific item, before the spec is
   finalised rather than after.
3. **One factory quote at 500 units FOB.** $10.50 is an estimate from material
   mass. Every downstream figure moves with it.
4. **One negotiated 3PL rate card.** Published postage is an upper bound of
   unknown tightness, and at 4 kg it is the second largest cost line.
5. **Whether $99 holds against $72.19.** This is a demand question, not a
   sourcing one, and it is the one the seven-day test is designed to answer.
