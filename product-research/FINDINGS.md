# Dropshipping product research: complete findings

**Status: research complete on structure, one candidate hunt still running.
Nothing has been purchased, ordered, published, or sent to any supplier.
Spend authorisation remains zero.**

Date: 2026-09-17 · Repository: `product-research/` · Branch: `claude/charming-planck-p6h2kd`

---

## 0. The one-paragraph version

Across roughly 109 screened products and four research rounds, **no product has
cleared the gates**. The reason is not bad luck in product selection, and after
this round it is possible to say what it actually is: two independent
arithmetic constraints — the cost of buying a customer, and the cost of moving
a single parcel across a border — both close off dropshipping below about
**$129 retail**, and above that the products that survive the price-floor test
are rare enough that four rounds have not found one. The grooming shear, the
only product taken to a full verdict, is **REJECTED** on four independent
grounds. The most valuable output of this project so far is not a product; it
is a set of screens that kill bad candidates cheaply, and two corrected
arithmetic errors that were making every candidate look better than it was.

---

## 1. Evidence standard, stated first because it limits everything

**No web page has been opened in this session.** Direct fetching is blocked at
the network layer. I verified this personally rather than accepting an agent's
report: `example.com` returns 403 at the CONNECT tunnel. Agents logged 62 and 16
consecutive refusals across 60+ hosts including every patent database, every
trademark register, every court-records service, CBP, the Federal Register,
Amazon, Walmart, and the carriers' own rate PDFs.

**Subagent web search is exhausted** at 200 of 200 calls. The main session
retains search capacity, which is now the only research channel left.

Labels used throughout:

| Label | Meaning |
|---|---|
| **VERIFIED\*** | Attributed to a named primary document via a search extract. The page was never opened. **One notch below** reading it. |
| **FACT-via-summary** | The search tool summarised a real page and reported the figure. I did not see the page. |
| **CLAIM** | An interested party asserts it — suppliers, platforms, sourcing agents, course sellers. |
| **PLATFORM-SYNTHESIZED** | An auto-generated marketplace SEO page wrote it. **Unusable** — nobody is accountable for it. |
| **ESTIMATE** | Derived. Method shown. |
| **UNKNOWN** | Could not be established. Not filled with a plausible number. |

One agent initially concluded that total fetch blockage meant nothing further
was knowable. A later agent corrected it: WebSearch routes server-side and
returns substantive summarised page content, so research remained possible at
one confidence step below a page read. That correction is why this document
exists at all.

---

## 2. Corrections to my own earlier statements

Listed because each one changed a conclusion you were given.

| # | What I said | What is true |
|---|---|---|
| 1 | A 12.2% contribution is "a loss at any acquisition cost" | **False.** Contribution is **+$7.14**, so break-even CAC is $7.14. It is a loss at any *reachable* CAC — $7.14 needs 12.18% of clicks to convert — but a positive break-even CAC exists, as it must whenever contribution is positive. |
| 2 | Relaxing the gate to 35% "would revive the citrus press and the litter box cabinet" | **False.** Under the corrected model they land at **33.7%** and **2.8%**. The cabinet misses by 32 points. The claim was made on the pre-correction model and never recomputed. |
| 3 | A sensitivity table "passes at several FOB and postage combinations" | **False.** Exactly one cell passed. I wrote the conclusion from expectation rather than from the output printed directly above it. |
| 4 | "I've saved the full screen with all sources to the repo" | **Not yet true when said.** The file was written immediately afterwards. |
| 5 | The bulk hunt produced "1 survivor" | **Not a survivor.** All three verification lenses failed to execute. See §8. |

---

## 3. The economics, defined

### Definition of net

**Net revenue = retail price − discounts actually given.** It excludes sales
tax, which is collected for a state and was never yours. It excludes shipping
revenue unless you charge it, in which case it is added to net revenue and the
outbound cost charged separately, so the two never silently cancel.

### The formula, with dollars

Single-unit fulfilment, one order. Worked at $69 retail with placeholder
supplier costs:

```
  retail price                                   $69.00
  less discounts given (10%)                     -$6.90
  = NET REVENUE                                  $62.10

  less product cost (supplier, 1 unit)          -$14.00
  less shipping, supplier to customer            -$7.00
  less neutral-packaging surcharge               -$0.50
  less import duty on $14.00 declared             -$3.28
  less per-parcel clearance fee                  -$5.00
  = FULFILMENT COST                              $15.78

  less customer support per order                -$1.00
  less payment processing                        -$2.10

  refund allowance    = 10.0% x (net + payment fee + return shipping - recovery)   -$6.42
  defect allowance    =  3.0% x (product + shipping + duty + clearance)            -$0.88
  chargeback allowance=  1.0% x (net + $15.00 fee)                                 -$0.77
  = LOSS ALLOWANCES                               $8.07

  CONTRIBUTION BEFORE ADVERTISING                $21.15   = 34.1% of net
  BREAK-EVEN CAC (the same number, by definition) $21.15
  BREAK-EVEN ROAS                                  2.94
```

### Why contribution and break-even CAC are the same number

Advertising is paid out of contribution. If you spend exactly the contribution
to acquire the customer, you break even. **There is nothing else it could be.**
It follows that whenever contribution is positive, a positive break-even CAC
exists — the question is never whether one exists, only whether it is reachable.

### The thresholds

| Threshold | Break-even ROAS | Meaning |
|---|---:|---|
| **45%, preferred** | 2.22 | For each $1 of net revenue, 45 cents is available to buy the customer and keep |
| **35%, conditional** | 2.86 | Investigated to show what the stricter screen excludes. Not an endorsement |

Both also require **contribution ≥ $20 in absolute dollars**, because a
percentage on a small ticket gives a break-even CAC too low to buy any traffic:
45% of a $30 order is $13.50, which at $0.87 a click needs 6.4% of visitors to
buy. **§6 shows that the $20 floor is itself far too low.**

### What the model does not do

- **No repeat purchase, anywhere.** There is no lifetime-value multiplier in the
  code and there will not be one until measured repeat data exists. Every figure
  is a first order standing alone.
- **No advertising inside contribution**, for the reason above. Profit and loss
  is reported across labelled acquisition-cost scenarios instead.
- **Founder's time is modelled but kept outside contribution**, so contribution
  stays comparable across candidates while a product that only works by paying
  yourself nothing remains visible as one.

---

## 4. Two arithmetic errors that were flattering every candidate

Measured by `scripts/model_check.py`, which reimplements the old formulas
alongside the new ones. Not asserted.

**Error 1: returns never reversed the refunded revenue.** The old formula
charged `landed × (1 − resellable)`, treating a return as a loss of unsold
goods. A return is a *refund*: money back, outbound postage already spent,
usually a share of return postage, the processor usually keeps its fee, and
someone inspects and restocks.

| | old | corrected |
|---|---:|---:|
| Return cost per unit shipped | $1.95 | **$7.33** |

**Error 2: chargebacks double-counted.** The old formula charged
`landed + fulfilment` again on a chargeback, although both were already
subtracted for every unit shipped. In a chargeback the customer keeps the goods
and you lose the money: the loss is the revenue plus the fee. Overstated $0.15.

**Net effect: 5.87 margin points.** The worked example moves from 51.2% to
45.3% — the difference between comfortably clearing a 45% gate and sitting
exactly on it, applied retroactively to every candidate previously assessed.

**Also fixed:** return postage did not move in the downside case (it was copied
before the scenario multipliers ran).

**Also added, all previously missing:** dimensional weight (a 0.4 kg product in
a 40×30×25 cm box bills at **6.00 kg** — $28 postage against $8 assumed), cargo
insurance, FX slippage between deposit and balance, per-order customer support,
and tooling as a dutiable assist.

---

## 5. The fulfilment reality: de minimis, and the parcel tax

### De minimis is gone, and it survived the Supreme Court ruling

This is the fact most likely to be got wrong, because the reasoning is subtle.

| Date | Instrument | Effect |
|---|---|---|
| 2025-05-02 | EO 14256 (IEEPA) | Suspended for China and Hong Kong |
| 2025-07-04 | OBBBA (H.R.1) — **a statute** | Terminates the exemption from **2027-07-01** |
| 2025-08-29 | EO 14324 | Extended **worldwide** |
| 2025-08-29 | — | **Entry Type 86 dies**; ACE rejects filings |
| 2026-02-20 | *Learning Resources v. Trump*, 6–3 | **IEEPA does not authorise tariffs.** Struck the reciprocal and fentanyl measures. Did **not** touch Section 232 or 301 |
| 2026-06-24 | CBP IFRs **91 FR 37789** / **91 FR 37801** | Indefinite suspension **re-grounded on CBP's own 19 U.S.C. 1321 + TFTEA authority — explicitly not IEEPA** |

CBP re-grounded the suspension on independent authority *before* the ruling
could unwind it. Anyone who read that the Supreme Court struck down the tariffs
may reasonably assume the $800 threshold returned. **It did not.** There is no
longer any value floor below which a commercial parcel enters free.

### The per-parcel fee stack is the actual killer

Government fees are trivial. Carrier fees are **floor-driven** — indifferent to
how small the parcel is.

| Charge | Figure | Label |
|---|---:|---|
| ECCF fee, per air waybill | ~$1.38 | VERIFIED\*, 19 CFR 24.23(b)(4)(i) |
| MPF, informal automated | $2.77 from 2026-10-01 | VERIFIED\* |
| **FedEx disbursement, 2026** | **greater of $17.50 or 2.5%** | VERIFIED\*, raised in 2026 from $15.00 / 2% |
| **UPS disbursement** | **3.5%, min $14.00** | VERIFIED\* |
| Standalone broker informal entry | $50–150 | CLAIM |

**A trap worth naming:** in the express channel the ECCF fee applies **in lieu
of** the informal MPF. Charging both is a common spreadsheet error worth ~$1.40
a parcel.

**The asymmetry that decides everything.** On a $25 parcel carrying ~$10 of
duty, FedEx's fee is not 2.5% of $10 — it is the **$17.50 floor**, which is 70%
of the value of the goods. A bulk importer spreads one entry over 500 units. A
dropshipper pays it 500 times. **That is the trade for zero inventory cash.**
Model **$20.00 per parcel**.

### Duty, and the unknown I could not close

Duty is assessed on **transaction value — what you pay the supplier, not your
retail price.** Undervaluation is the classic dropshipping failure, and **you**
carry the false-declaration exposure as the party causing the importation, not
the supplier.

| Layer | Rate | Status |
|---|---:|---|
| MFN, HTS **8213.00.9000** (scissors, over $1.75/dozen) | 3¢ each + 3% | VERIFIED\* |
| Section 301 forced-labour, China | +12.5% | In force since 2026-07-24 |
| Section 301 legacy Lists 1–4A | +0%, 7.5% or 25% | Guidance points to **7.5%** for consumer subheadings; **not confirmed for 8213** |
| Section 232 steel derivative | +0% or up to +50% | **UNRESOLVED.** BIS added **407 HTS codes** effective 2025-08-18; whether 8213 is among them could not be checked |
| IEEPA reciprocal and fentanyl | 0% | Struck down 2026-02-20 |
| Section 122, 10% global | 0% | Expired 2026-07-24 by the statute's own 150-day cap |

- **Defensible floor: 15.5%** — confirmed layers only
- **Central: 40.5%** — if 8213 sits on List 3
- **Ceiling: ~90%** — if it is also a steel derivative. For a forged stainless
  product that is a live possibility, not a tail risk

**That range is wider than the entire gross margin.** Two sources close it —
the USTR 301 tariff tool and CSMS 65936570 — and both are blocked from here.

### DDP hides the cost; DDU destroys the customer

Under DDU the customer who paid $79 receives a separate demand for ~$10 duty
plus a $17.50 disbursement fee — **35% of what they already paid** — days later,
from a company they never transacted with, as a condition of release. On cold
paid traffic that is a chargeback, a refund and a bad review, usually all three.

A refused parcel is worse than a lost sale: goods gone, freight gone, duty
already advanced, return cost deducted, customer refunded, and the acquisition
cost already spent. **Roughly a 2.5× loss on the unit.**

DDP is commercially better and informationally worse: "$12 DDP shipping" bundles
duty, ECCF, brokerage, freight and margin into one unauditable number.

---

## 6. The price floor, reached twice from different directions

### Line 1: what a customer costs

| Benchmark | Figure |
|---|---:|
| Median cost per purchase | **$49.04** |
| Median CPA, all industries | $38.19–$38.99 |
| Ecommerce average CPA | $29.99 |
| Meta / Google / TikTok | $42 / $38 / $51 |
| **Median DTC Meta purchase ROAS** | **2.96** |

All FACT-via-summary. Contribution **is** break-even CAC, so contribution must
clear roughly **$50** to have headroom above these.

| Retail | Net | Contribution @45% | Beats $49.04? |
|---|---:|---:|---|
| $69 | $62.10 | $27.95 | no |
| $89 | $80.10 | $36.05 | no |
| $99 | $89.10 | $40.10 | marginal |
| **$129** | $116.10 | **$52.25** | **yes** |
| $149 | $134.10 | $60.34 | yes |

### Line 2: what a parcel costs

Budget: `goods × 1.405 (duty) + shipping ≤ ceiling − $20 parcel tax`

| Retail | Ceiling @45% | Left for goods + shipping | Max goods at $8 shipping | |
|---|---:|---:|---:|---|
| $69 | $24.56 | $4.56 | **none** | impossible |
| $89 | $32.09 | $12.09 | $2.91 | tight |
| $99 | $35.85 | $15.85 | $5.59 | tight |
| **$129** | $47.14 | $27.14 | **$13.63** | workable |
| $149 | $54.67 | $34.67 | $18.98 | workable |
| $179 | $65.96 | $45.96 | $27.02 | workable |

### The convergence

Two arguments sharing **no inputs** — one about ad auctions, one about customs
and carrier tariffs — land on the same number.

> **Dropshipping below $129 retail is arithmetically closed in 2026.**

That is a structural finding, not a sourcing failure. It is also why the $69
shear was never going to work regardless of which supplier was found.

### Meta deleted the targeting that trade products depend on

Job title, industry and company size targeting are gone; ad sets still relying
on them stopped delivering **15 January 2026**. A product whose buyer is defined
by their occupation is no longer reachable on paid social. This removes an
entire class of candidate — professional and trade tools — that four rounds had
been treating as promising.

---

## 7. Verdict on the 7.5in professional pet grooming shear: **REJECT**

Not a hold. Four independent grounds, any one sufficient.

### 7.1 The spec sheet is the commodity spec

| Product | Price | Claimed spec |
|---|---:|---|
| Unique Bargains 7.5in curved | $11.99 | Walmart |
| **Laazar Professional 7.5in curved** | **$22.27** | "Tension Adjustable", "440C JAPANESE STAINLESS STEEL", leather case |
| **JASON 7.5in curved** | **$29.99** | "Japanese 440C stainless steel, manually forged", ergonomic handle |
| Chris Christensen Classic 7.5in | UNKNOWN | "Convex blade... Made From 440C Japanese Steel" |

$69 asks a groomer to pay a **130% premium over a listing whose copy is
word-for-word identical**, with no brand. The competitor nobody flagged is the
worst: **Chris Christensen** is a name every groomer knows, selling the identical
claimed spec. Geib markets its Entrée line as "a low cost, high quality shear
with a convex edge" — the proposed product's entire pitch, from a legacy brand.

### 7.2 Break-even sits below every published benchmark

Contribution $22.29 → break-even ROAS **3.10**, against a **median DTC Meta ROAS
of 2.96**. At the median outcome the founder loses $1.02 an order before taking
a salary. The cheapest published CPA benchmark exceeds the ceiling by 35%. And
the buyer is defined by occupation, which Meta no longer targets.

### 7.3 Differentiation: no reason to buy

The obvious wedge — bundling the recurring sharpening cost — is occupied. Shear
Integrity offers "FREE Lifetime Sharpening (with a UPS Pre-Paid Return Label)";
Magix a free first sharpening; subscriptions run at $48–49/month. A new entrant
arriving with free sharpening arrives third.

The one genuinely unserved gap — a **loaner shear during the 7-to-14-day
sharpening turnaround** — is real and documented, and unaffordable: premium
convex sharpening is $35 plus ~$15 round-trip shipping against a $22.29
contribution. One service event is negative margin before any loaner exists.

The buyer is documented as price-resistant by their own trade press. *Groomer to
Groomer*: groomers are "unwilling or unable to pay the $30 or more for shear
sharpening that beauty salons pay."

### 7.4 As a dropship product it is worse

A dropshipped generic shear is the identical object the customer can buy
themselves, same marketplace, same delivery time, for $22–30.

### 7.5 Intellectual property: NOT CLEARED

The screen returned **COULD_NOT_CHECK**. Zero patent or trademark databases
reached — 62 refused attempts. No claim set, legal status, maintenance-fee
record or assignment was read.

**This is preliminary screening, not legal clearance.** Documents to pull first
if it ever revives, all with **unverified** assignee and status:

| Number | Title | Why it matters |
|---|---|---|
| US9421690 / US9724835 / US10029376 | Ergonomic cutting shears | Three-member family; goes to the offset handle. Continuation practice is a mild signal of intent to enforce |
| USD1019319 | Scissor design patent, Chinese-held | Design patents are the instrument most used in marketplace takedowns |
| US11938645 | Cutting implement | Goes to the convex edge |
| US8756818 | Shear tension device | Goes to the tension mechanism |

Ubiquity of a feature is an **invalidity** argument, not a non-infringement one,
and it costs money to make.

### 7.6 On price and quality

Nothing here infers quality from price, and nothing infers it from a stamped
material grade. **"440C Japanese stainless" appears on the $22.27 listing and on
the $69.99 listing alike**, which is precisely why the label carries no
information. What it evidences is what a seller is willing to claim.

| | What settles it |
|---|---|
| **Evidence** | independent review counts, order counts, seller history, third-party test reports, return-rate data |
| **Seller claim** | material grade, hardness figure, "forged", "hand-honed", country of origin |
| **Only a sample settles** | actual HRC hardness, actual steel composition, edge geometry and retention, pivot tolerance, finish |

A cheaper shear is **not proven worse. It is unproven either way**, and only a
physical sample with a hardness or composition test resolves it.

### 7.7 Supplier shortlist, for the record

Screened from public listings only; nobody was contacted.

- **Shortlisted:** Pingyang Yonghe Scissor Co., Ltd. — the only named company
  passing the catalogue-breadth test (scissors only), naming shear-specific
  steels a trader would not know to name (ATS-314, VG-10, powder steels), with
  an owned domain and a trade-show exhibitor entry, and openly listing the cheap
  substitute (9Cr18) alongside 440C.
- **Do not shortlist:** Guangzhou Mackay (a hair-brush factory reselling
  scissors); Zhangjiagang Haiba (four incompatible founding dates,
  self-describes as trading, "Hitachi SUS 440c" mashes three steel-naming
  systems); Zhangjiagang Weida (546+ products across office and household
  scissors — a volume stamping house, structurally wrong for hand-honed convex).
- **A new evidence category:** much supplier "data" came from
  **PLATFORM-SYNTHESIZED** Alibaba SEO landing pages writing marketing copy
  about its own sellers with the fluency of a sourcing report. Worse than CLAIM,
  because a supplier claim at least tells you what someone will be held to.

---

## 8. What was screened, and what killed it

Roughly **109 products** across four rounds.

| Round | Screened | Advanced | Survived |
|---|---:|---:|---:|
| 1, dropship-research | ~40 | 0 | 0 |
| 2, bounded funnel | 21 | 0 | 0 |
| 3, dual-threshold hunt | 40 | 9 | **0 tested** (see below) |
| 4, dropship candidates | 8 of 24 so far | 0 | 0 |

### Causes of death

| Cause | Approx. count | Note |
|---|---:|---|
| **Price floor / marketplace clone** | ~45 | The dominant killer. Kills on **spec-sheet identity**, not category |
| **Acquisition** | 9 | Every round-3 candidate actually tested died here |
| Weight or dimensional weight | ~12 | US last mile, not the ocean leg |
| Enforced patents | ~8 | Always on the products with the best five-second demos |
| Retail below the floor | ~11 | Too cheap to fund paid advertising |
| Safety / hazard class | 2 | Including a CPSC recall history in the same class and price band |

### The round-3 "survivor" that was not

The run reported one survivor. **All three of its verification lenses failed to
execute** — session WebSearch hit 200 of 200 and fetching is blocked. The agents
said so themselves:

> "TOOLING FAILURE — THIS LENS WAS NOT ACTUALLY RUN... Treat this as 'not
> tested', NOT as 'survived'."

It scored as a survivor only because the rule treats a low-confidence refutation
as non-fatal, and all three votes were low-confidence **because nothing ran**. A
pipeline that cannot distinguish "passed the test" from "the test did not
execute" will manufacture a recommendation out of a tooling failure. Recorded as
**UNTESTED** and not carried forward.

### Patterns worth keeping

1. **The best demos sit on enforced patents.** A product that demonstrates
   instantly on camera is worth patenting and worth defending. Assume patented
   until a search says otherwise.
2. **The price floor kills on spec-sheet identity.** Search the clone using the
   product's *spec-sheet language*, not its category name, **before** proposing
   anything. This is the single highest-yield screen in the project.
3. **The supplier is often the competitor.** In round 4, one manufacturer sells
   the identical item direct to your customer on Amazon, eBay and its own store
   at $107–167. Not a third party cloning — the supplier itself.
4. **Weight is punished at the last mile, not the first.** Sea freight made the
   China leg nearly free; US domestic postage then charged $13–54 for the same
   box. Bulk ordering relocated the problem rather than solving it.
5. **A regulatory or certification barrier cuts both ways.** It keeps clones
   out and keeps you out.

---

## 9. The US-domestic alternative, assessed honestly

A US distributor with a dropship programme removes duty, the parcel tax, the
three-week transit and the missing return address at once. It does not survive
contact with the ad auction.

Distributors price for pallets, not single-unit pick-and-pack, so they recover
it: a **$3.50 per-order fee** at one, branded packaging gated behind a
**$99.99/month** tier at another, or simply in the goods price. The result is
roughly **50% gross margin**, where cold-start paid acquisition needs
**70–80%**. **The gap is the whole business.**

Four honest exits, in order of how much they change:

1. **A higher price point.** CAC is broadly absolute while contribution is
   proportional. At $180 retail on the same 50% structure, contribution is ~$75
   rather than ~$29, and the required cold conversion rate falls to about 2.2% —
   at least inside the range of the possible.
2. **A consumable tail.** A product with repeat purchase can survive a
   first-order loss. A shear bought once every few years cannot.
3. **Not paid acquisition.** Domestic dropship economics are survivable at 50%
   gross margin when CAC is near zero. They are not survivable against an
   auction.
4. **Buying stock on terms.** Wholesale marketplaces offering low minimums and
   net-60 (CLAIM, unverified) would let goods sell before they are paid for.
   That is not dropshipping, but it addresses the real constraint — no
   five-figure outlay — far better than dropshipping does, and it restores the
   margin.

---

## 10. What must be verified before any money moves

Ordered by cost per conclusion settled.

| # | Check | Cost | Kills a candidate if |
|---|---|---|---|
| 0 | Patent and hazard screen | $0 | A live patent covers the mechanism, or the class has a recall record |
| 0 | **Marketplace clone search on spec-sheet language** | $0 | The identical spec sells for materially less |
| 1 | **Customs classification** by a licensed broker | $200–400 | The duty stack makes the price unachievable |
| 1 | **Whether the carrier consolidates entries** under 19 CFR 128.24 | $0 | A standalone broker files at $50–150 per parcel — nothing in this band survives |
| 2 | Three supplier quotes | $0 to send | The median lands >35% above the modelled cost |
| 3 | Negotiated 3PL or carrier rate card | $0 to ask | — (an input, not a gate) |
| 4 | Samples, three suppliers | $150–300 | Hardness, composition or finish fails |
| 5 | Demand test, 300 clicks | $300 | Fewer than 5 payers |

**Total to a defensible go/no-go: $650–1,000**, against a first order of roughly
$9,000–11,000 or, under dropshipping, against the ad spend.

### Five primary pages a human should open, since none could be read here

1. **91 FR 37789** and **91 FR 37801** — the operative de minimis rules
2. **CSMS 65936570** — settles the Section 232 steel-derivative question
3. The **USTR Section 301 tariff search** for 8213.00.90
4. The **UPS import surcharge PDF** and the **FedEx 2026 surcharge PDF**
5. **mydhl.express.dhl** surcharges — the DTP fee could not be pinned down at all

### The demand test's decision rule, pre-registered

| Payers at ~300 clicks | Verdict | Basis |
|---|---|---|
| 0 | **Hard kill** | True rate below **0.99%** at 95% confidence |
| 1–2 | Fail | A dead product at 0.5% still produces ≥1 sale **77.8%** of the time |
| 3–4 | Inconclusive | Extend to ~500 clicks |
| **5+** | **Pass** | **1.8%** false-pass rate, **71.8%** power against a viable 2% product |

Exact binomial, independently recomputed. **The test is far better at
disproving demand than proving it, and is designed that way.** A pass
authorises a second larger test or a smaller first order — never a full
production run.

---

## 11. Repository map

| Path | What it is |
|---|---|
| `FINDINGS.md` | This document |
| `scripts/unit_econ.py` | Bulk-import economics, base/downside/severe, dual threshold |
| `scripts/dropship_econ.py` | Single-unit economics; prints the formula with dollars |
| `scripts/ds_sweep.py` | Max affordable **delivered cost** at each retail price |
| `scripts/sweep.py` | Retail × ex-factory band grid, and max affordable ex-factory |
| `scripts/model_check.py` | Verifies identities, **measures** both corrections, edge cases |
| `scripts/compare.py` | Ranks every spec into bands with the decision tables |
| `products/*.yaml` | One spec per candidate, with `must_verify` and evidence quality |
| `runs/2026-09-17-r2/` | Working papers behind each section above |
| `templates/supplier-inquiry.md` | 12 questions, ordered so factory-vs-trader tells come later. **Unsent** |
| `templates/demand-test.md` | The $300 test design and its statistical basis |

---

## 12. Where this leaves it

**No product is recommended.** One is rejected with reasons. The remaining
candidate hunt is running under a gate now validated from two independent
directions, and its results will be appended here.

The honest summary of four rounds: **the constraint is the business model, not
the product search.** Single-product, China-direct, paid-ads-from-day-one, solo,
under $129 retail is arithmetically closed in 2026 — de minimis is gone, the
parcel tax is floor-driven and unavoidable at solo volume, published CPAs exceed
the contribution such products generate, and the categories that survive the
price-floor test are the ones somebody already patented.

That is worth more than a product I would have to talk you into.
