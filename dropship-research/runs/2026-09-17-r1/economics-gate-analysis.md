---
run_id: 2026-09-17-r1
agent: lead
date: 2026-09-17
status: complete
confidence: high
---
# Gate analysis: is the brief internally consistent?

Computed with `scripts/econ.py` against `config/fees.yaml`. This is arithmetic, not opinion, and it does not depend on any supplier data we do not have.

## The question

Discovery returned candidates whose observed retail prices mostly sit at or below the brief's $25 floor. The paid-ads gates require contribution of at least $20 **and** at least 45% of net price, with break-even ROAS at or below 2.2. Rather than guess at supplier costs we do not have, I inverted the problem: **at each retail price, what is the largest landed cost that still clears the gates?**

## Result

Fees applied: 2.9% + $0.30 payment, 10% discount, 5% refund, 0.5% chargeback at a $15 fee, $0.50 packaging. All from `config/fees.yaml`, all labelled ASSUMPTION there.

| Retail price | Max landed cost that still passes | As % of retail |
|---|---|---|
| $25 | **impossible** | fails even at zero cost of goods |
| $29 | $2.85 | 10% |
| $35 | $7.54 | 22% |
| $39 | $10.66 | 27% |
| $45 | $15.35 | 34% |
| $49 | $18.43 | 38% |
| $55 | $20.80 | 38% |
| $60 | $22.76 | 38% |
| $79 | $30.24 | 38% |

Worked examples on the lead candidate, a dog paw cleaner:

| Retail | Landed | Contribution | Margin | BE ROAS | Verdict |
|---|---|---|---|---|---|
| $29 | $11.00 | $11.40 | 44% | 2.29 | FAIL |
| $29 | $8.00 | $14.57 | 56% | 1.79 | FAIL, contribution floor |
| $39 | $11.00 | $19.64 | 56% | 1.79 | FAIL, misses $20 by $0.36 |
| $49 | $13.00 | $25.78 | 58% | 1.71 | PASS |
| $59 | $15.00 | $31.91 | 60% | 1.66 | PASS |

## What this means

**The brief as written has no viable product.** Three requirements are mutually exclusive:

1. Paid ads from day one, which forces contribution of at least $20 per order
2. A $25 to $60 price band
3. Viral problem-solver products, which discovery found retail at $15 to $32

At $25 the gates cannot be met even if the goods were free, because the payment fee, expected refund loss and chargeback provision alone exceed the headroom. The band only opens up at about **$45 retail**, and above roughly $49 the binding constraint settles at a landed cost of **38% of retail**.

Nine of the fourteen candidates discovery returned have observed retail prices below the $25 floor. Only one, the pull-out cabinet organiser at $25 to $45, sits cleanly inside the band, and it carries heavy shipping and installation friction.

This is not a reason to lower the gate. The gate is what stops us launching a store that loses money on every paid order. It is a reason to change one of the other three inputs.

## Options, with the trade-off stated

| Option | What changes | Cost of taking it |
|---|---|---|
| **A. Raise the price band to $45 to $89** | Product universe shifts from viral gadgets to mid-ticket home goods | Harder to demo in five seconds; higher ad cost per click; different competitive set |
| **B. Bundle to reach $45 or more** | Keep a proven candidate, sell it as a three-item kit | Landed cost must stay under 38% of retail across the whole kit; more SKUs to source and ship |
| **C. Switch to organic-first** | Contribution floor drops back to $12 and 35%, which most candidates clear | Slower, depends on creative reach rather than budget; owner explicitly chose paid ads |
| **D. Accept lower margin on paid** | Lower the gate | Rejected. It converts a disciplined test into a guaranteed loss per order |

Options A and B are compatible with the owner's stated preference for paid ads. Option C is the safest commercially but contradicts the stated brief. Option D is not on the table.

## The separate blocker: delivery

Independent of price, discovery flagged that the brief's **12-day tracked US delivery cap looks incompatible with China-direct dropshipping**. Trade sources put ePacket China to US at roughly 22 days in 2026 (E47, unverified, page not opened). Meeting 12 days tracked realistically requires either a US-based third-party logistics partner or a supplier with US warehousing, and both mean buying stock up front rather than dropshipping it.

That is a change to the business model, not the product list, and it needs resolving before product selection matters. It is also unverified: the supporting pages could not be opened from this environment, so it belongs in the manual-check queue rather than being treated as settled fact.

## Recommendation

Do not run supplier or competitor research yet. Running it against products that fail the gate arithmetically would burn effort on a foregone conclusion. Resolve the price band and the delivery model first, then research the candidates that survive.
