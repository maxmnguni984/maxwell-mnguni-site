---
run_id: 2026-09-17-r2
agent: lead
date: 2026-09-17
status: draft
confidence: high
scope: what to verify, in what order, at what cost
---
# Validation sequence: cheapest killing question first

**Nothing here has been executed. No supplier has been contacted, no page
published, no advertising run, no order placed. Spend authorisation remains
zero and every line below needs your approval individually.**

## The ordering principle

Across four research rounds the project's expensive mistakes have all had the
same shape: an assumption carried forward because checking it felt like a later
step. So this sequence is ordered by **cost of the check divided by the number
of conclusions it settles**, not by the order a founder naturally wants to do
things in.

Concretely: a customs classification costs a few hundred dollars and can kill a
product outright. A demand test costs $300 and takes a week. Doing the demand
test first risks spending a week validating demand for a product that a tariff
line makes unsellable.

## Step 0, before any money: the two questions that are free

Both are desk work, already partly done, and both can eliminate a candidate.

| Check | Cost | Kills the candidate if |
|---|---|---|
| Live patent on the core mechanism | $0, search | A granted US utility or design patent covers the mechanism, or there is enforcement history |
| Hazard class and recall history | $0, CPSC search | The product class has a recall record, or involves pressure, heat, load-bearing or ingestion |

Six candidates have died on the first and one on the second. Neither requires
anyone's approval and neither costs anything.

## Step 1: customs classification — the highest return per dollar available

**Cost: roughly $200 to $400 for a licensed customs broker's opinion. Needs your approval.**

The duty stack now runs 20 to 45% of the free-on-board price. It is the third
largest cost line after goods and postage, and it is the only one that can
change by a factor of two on a question of fact rather than negotiation.

For the current front-runner, the cast-iron citrus press, one question decides
the product: **does Section 232 steel duty at 50% apply to cast iron?**

| Section 232 applies | Verdict at $99 |
|---|---|
| No, 23.4% consumer stack | Band A, 45.2% |
| Yes, roughly 63% | Fails at $99, needs $119 — a 65% premium to a $72.19 incumbent |

**Stop/go: if Section 232 applies, stop.** Do not proceed to samples, do not
run a demand test. The price the product would need is further above the
incumbent than the paw cleaner's premium, which was rejected on exactly that
ground.

## Step 2: one factory quote, before anything is built

**Cost: $0 to send. Needs your approval because it is supplier contact.**

Every cost figure in this project is an estimate from material mass. Nobody has
quoted anything. `templates/supplier-inquiry.md` is drafted and ready; it asks
for packed carton dimensions as its single most important commercial answer,
because the model now bills postage on volume and a supplier who packs the same
product 20% smaller is cheaper on every unit forever.

Send to three suppliers separately, never as a group, never with a price anchor.

**Stop/go: if the median of three quotes is more than 35% above the modelled
ex-factory, the candidate returns to the model before anything else happens.**
Re-run `scripts/unit_econ.py` with the real number rather than arguing with it.

## Step 3: one negotiated third-party warehouse rate card

**Cost: $0 to request. Needs your approval because it is outreach.**

Published postage is an upper bound of unknown tightness. Negotiated rates
commonly run 40 to 55% below published, and postage is the largest or second
largest cost line for every candidate the project has produced. For the two
heavy revival candidates it exceeded their entire landed cost.

This single document moves several candidates between fail and pass, and it is
free to ask for.

**Stop/go: none.** This is an input, not a gate. But no candidate should be
funded on published rates when the real ones are obtainable for an email.

## Step 4: samples, and only then

**Cost: sample price plus shipping, per supplier. Needs your approval.**

Only after steps 1 to 3 have produced real numbers. A sample tells you what you
are actually buying; it cannot tell you whether the tariff line is affordable or
whether anyone wants it.

The sample inspection checklist has to be built from the **recurring complaints
in competitor reviews** for the specific product, so that each check maps to a
failure mode customers actually report. That research has not been done for any
current candidate and must be done before the checklist is written. Writing a
generic checklist would defeat its purpose.

## Step 5: the demand test

**Cost: $300, seven days. Needs your approval. Design is complete in
`templates/demand-test.md`.**

A real pre-order taking a refundable deposit, about 300 cold clicks, with the
decision rule pre-registered before a dollar is spent:

| Payers at ~300 clicks | Verdict |
|---|---|
| 0 | Hard kill — true rate below 0.99% at 95% confidence |
| 1 to 2 | Fail — a dead product at 0.5% produces at least one sale 77.8% of the time |
| 3 to 4 | Inconclusive — extend to ~500 clicks |
| 5 or more | Pass — 1.8% false-pass rate, 71.8% power against a viable 2% product |

**The test is far better at disproving demand than proving it, and it is
deliberately designed that way.** Three hundred visitors with no purchases rules
out any conversion rate at or above 1%, which is enough to cancel a five-figure
order. A pass is provisional and authorises a second larger test or a smaller
first order, never a full production run.

## Where the demand test sits relative to the economics

For a candidate at the conditional 35% threshold, the demand test has to clear a
**higher bar**, and this is the part that is easy to miss. Break-even
conversion rate is cost per click divided by contribution:

| Contribution | At $0.87 CPC, visitors who must buy |
|---|---|
| $40.28 (citrus press at $99, band A) | 2.16% |
| $23.99 (citrus press at $79, 33.7%) | 3.63% |
| $17.48 (citrus press at $99, downside) | 4.98% |

A 2% conversion rate is already optimistic for cold traffic to an unknown brand.
So a lower-margin candidate does not merely earn less per order — **it requires
a conversion rate further outside what the test is powered to detect.** At 300
clicks the test can confidently distinguish "dead" from "roughly 2%". It cannot
confirm 3.6%, and a candidate needing 3.6% is one the seven-day budget cannot
validate at all.

That is the concrete reason the 45% target is worth keeping as the preferred
one, stated as arithmetic rather than as a preference.

## Total spend to a defensible go/no-go

| Step | Cost | Needs approval |
|---|---:|---|
| 0. Patent and safety screen | $0 | no |
| 1. Customs classification | $200–400 | yes |
| 2. Three supplier quotes | $0 | yes, supplier contact |
| 3. Warehouse rate card | $0 | yes, outreach |
| 4. Samples, three suppliers | ~$150–300 | yes |
| 5. Demand test | $300 | yes |
| **Total** | **$650–1,000** | |

Against a first order of roughly $9,000 to $11,000. The sequence is designed so
that the cheapest checks can kill the candidate before the expensive ones run.
