---
run_id: 2026-09-17-r2
date: 2026-09-17
scope: what single-unit US fulfilment actually costs in 2026
confidence: high on structure, LOW on the duty rate
---
# The parcel tax: why dropshipping has a hard price floor now

## Evidence standard for this document

No page was opened. Direct fetching is blocked at the network layer and I
confirmed it myself — `example.com` returns 403 at the CONNECT tunnel. One
agent logged 16 of 16 blocked, another 62 of 62.

WebSearch still returns substantive summarised page content, so findings are
marked **VERIFIED\*** — attributed to a named primary document (CBP, Federal
Register, USTR, eCFR, a carrier's own rate PDF) via a search extract, but the
page itself was never read. That is **one notch below** reading it.

## 1. De minimis is gone, and it survived the Supreme Court ruling

This is the fact most likely to be got wrong, because the reasoning is subtle.

| Date | Instrument | Effect |
|---|---|---|
| 2025-05-02 | EO 14256 (IEEPA) | Suspended for China and Hong Kong |
| 2025-07-04 | OBBBA, H.R.1 — **a statute** | Terminates the exemption from **2027-07-01** |
| 2025-08-29 | EO 14324 | Extended **worldwide** |
| 2025-08-29 | — | **Entry Type 86 dies**; ACE rejects filings |
| 2026-02-20 | *Learning Resources v. Trump*, 6–3 | **IEEPA does not authorise tariffs.** Struck the reciprocal and fentanyl measures. Did **not** touch Section 232 or 301 |
| 2026-06-24 | CBP interim final rules **91 FR 37789** and **91 FR 37801** | Indefinite suspension **re-grounded on CBP's own 19 U.S.C. 1321 + TFTEA authority — explicitly not IEEPA** |

CBP re-grounded the suspension on independent authority *before* the ruling
could unwind it. A founder who read that the Supreme Court struck down the
tariffs may reasonably assume the $800 threshold returned. **It did not.**

There is no longer any value floor below which a commercial parcel enters free.

## 2. The per-parcel fee stack, which is the actual killer

Government fees are trivial. Carrier fees are not, and they are **floor-driven**
— indifferent to how small the parcel is.

| Charge | Figure | Label |
|---|---:|---|
| ECCF fee, per air waybill | ~$1.38 | VERIFIED\*, 19 CFR 24.23(b)(4)(i) |
| MPF, informal automated | $2.77 from 2026-10-01 | VERIFIED\* |
| **FedEx disbursement, 2026** | **greater of $17.50 or 2.5%** | VERIFIED\*, raised in 2026 from $15.00 / 2% |
| **UPS disbursement** | **3.5%, minimum $14.00** | VERIFIED\* |
| Standalone broker informal entry | $50–150 | CLAIM |

**One trap worth naming:** in the express channel the ECCF fee applies **in lieu
of** the informal MPF. Charging both is a common spreadsheet error worth ~$1.40
a parcel.

**The asymmetry that decides everything.** On a $25 parcel carrying ~$10 of
duty, FedEx's fee is not 2.5% of $10 — it is the **$17.50 floor**, which is 70%
of the value of the goods. A bulk importer spreads one entry over 500 units. A
dropshipper pays it 500 times. **Model $20.00 per parcel.**

## 3. The duty rate is the largest remaining unknown, and the range is enormous

Duty is assessed on **transaction value — what you pay the supplier, not your
retail price.**

| Layer | Rate | Status |
|---|---:|---|
| MFN, HTS 8213.00.90 | 3¢ each + 3% | VERIFIED\* |
| Section 301 forced-labour, China | +12.5% | In force since 2026-07-24 |
| Section 301 legacy Lists 1–4A | +0%, 7.5% or 25% | **UNRESOLVED for 8213** |
| Section 232 steel derivative | +0% or up to +50% | **UNRESOLVED for 8213** |
| IEEPA reciprocal and fentanyl | 0% | Struck down 2026-02-20 |
| Section 122 10% global | 0% | Expired 2026-07-24 by the statute's own 150-day cap |

- **Defensible floor: 15.5%** — confirmed layers only.
- **Central case: 40.5%** — if 8213 sits on List 3.
- **Ceiling: ~90%** — if it is also a steel derivative. For a forged stainless
  product that is a live possibility, not a tail risk.

**That range is wider than the entire gross margin.** Two searches — the USTR
301 tariff tool and CSMS 65936570 — would close it.

## 4. DDP hides the cost; DDU destroys the customer

Under DDU the customer who paid $79 gets a separate demand for ~$10 duty plus a
$17.50 disbursement fee — **35% of what they already paid**, days later, from a
company they never transacted with, as a condition of release. On cold paid
traffic that is a chargeback, a refund and a bad review, usually all three.

A refused parcel is worse than a lost sale: goods gone, outbound freight gone,
duty already advanced, return cost deducted, customer refunded, and the
acquisition cost already spent. **Roughly a 2.5x loss on the unit.**

DDP is better commercially and worse informationally. A supplier quoting "$12
DDP shipping" is bundling duty, ECCF, brokerage, freight and margin into one
unauditable number. And if they under-declare to shrink the duty, **the founder
carries the false-declaration exposure, not the supplier**, as the party causing
the importation.

## 5. What is left for the product, after the parcel tax

Budget: `goods x 1.405 (duty) + shipping <= ceiling - $20`

| Retail | Ceiling at 45% | Left for goods + shipping | Max goods at $8 shipping | |
|---|---:|---:|---:|---|
| $69 | $24.56 | $4.56 | **none** | impossible |
| $89 | $32.09 | $12.09 | $2.91 | tight |
| $99 | $35.85 | $15.85 | $5.59 | tight |
| **$129** | $47.14 | $27.14 | **$13.63** | workable |
| $149 | $54.67 | $34.67 | $18.98 | workable |
| $179 | $65.96 | $45.96 | $27.02 | workable |

## 6. Two independent lines converge on the same floor

This is the part worth trusting, because the two arguments share no inputs.

1. **Acquisition.** Median cost per purchase is $49.04, median CPA $38–39.
   Contribution is the break-even CAC, so it must clear roughly $50 — which at
   45% of net means **retail $129 or above**.
2. **Fulfilment.** A fixed ~$20 parcel tax plus duty on goods leaves nothing for
   the product below **retail $129**.

Different evidence, same floor. **Dropshipping below $129 retail is
arithmetically closed in 2026**, and that is a structural finding rather than a
sourcing failure.

## 7. The US-domestic alternative, assessed honestly

A US distributor with a dropship programme removes the duty, the parcel tax, the
3-week transit and the missing return address at once. It does not survive
contact with the ad auction.

Distributors price for pallets, not single-unit pick-and-pack, so they recover
it: a **$3.50 per-order fee** at one, branded packaging gated behind a
**$99.99/month** tier at another, or simply in the goods price. The result is
roughly **50% gross margin**, where paid acquisition on a cold start needs
**70–80%**.

**The gap is the whole business.** Four honest exits, in order of how much they
change:

1. **A higher price point.** CAC is broadly absolute while contribution is
   proportional. At $180 on the same 50% structure, contribution is ~$75 rather
   than ~$29, and the required cold conversion rate falls to about 2.2% — which
   is at least inside the range of the possible.
2. **A consumable tail.** A product with repeat purchase can survive a
   first-order loss. A shear bought once every few years cannot.
3. **Not paid acquisition.** Domestic dropship economics are survivable at 50%
   gross margin when CAC is near zero. They are not survivable against an
   auction.
4. **Buying stock on terms.** Wholesale marketplaces offering low minimums and
   net-60 (CLAIM, unverified) would let goods sell before they are paid for.
   That is not dropshipping, but it addresses the actual constraint — no
   five-figure outlay — far better than dropshipping does, and it restores the
   margin.

## What must be resolved before any money moves

1. **The two duty UNKNOWNs.** The USTR Section 301 tariff search and CSMS
   65936570 (the Section 232 derivative list). This is thirty minutes of work
   against a range wider than the gross margin, and it is the highest-value
   thing anyone could do next.
2. **Whether the carrier consolidates entries** under 19 CFR 128.24. If a
   standalone broker files at $50–150 per parcel instead, nothing in this band
   survives.
3. **Five primary pages a human should actually open**, since none could be read
   here: 91 FR 37789, 91 FR 37801, CSMS 65936570, the UPS import surcharge PDF,
   and the FedEx 2026 surcharge PDF.
