---
product_id: P-0000
agent: lead
run_id: <run-id>
date: <YYYY-MM-DD>
status: complete
confidence: medium
fetch_count: 0
time_minutes: 0
flags: []
requests_for_lead: []
decision: finalist | hold | rejected
adjusted_score: 0
---
# <Product name> — verdict

## Decision
One paragraph: decision, the deciding factor, and the single biggest uncertainty.

## Challenge log
| Check | Result | Note |
|---|---|---|
| Spot-checked >= 2 evidence URLs per agent file | pass/fail | which E-ids |
| FACTs without E-id downgraded | n downgraded | |
| Conflicts resolved (pessimistic unless corroborated) | | |
| Single-source demand claims downgraded | | |

## Gates
| Gate | Result (PASS/FAIL/UNKNOWN) | Reason | Source |
|---|---|---|---|
| G0 category | | | |
| G1 IP & legal | | | |
| G2 safety | | | |
| G3 delivery | | | |
| G4 economics | | | |
| G5 demand | | | |
| G6 platform | | | |

## Score (only if all gates PASS)
| Criterion | Weight | Score 0-10 | Weighted | Reason |
|---|---|---|---|---|
| demand_strength | 20 | | | |
| demo_creative_potential | 20 | | | |
| base_economics | 20 | | | |
| differentiation_credibility | 15 | | | |
| supplier_confidence | 15 | | | |
| competition_intensity_inverse | 10 | | | |
| **raw total** | 100 | | | |
| confidence multiplier | | | | high 1.0 / medium 0.85 / low 0.7 |
| **adjusted score** | | | | |

## Evidence and uncertainty
- strongest evidence:
- weakest link:
- unresolved questions:

## Validation plan (finalists only)
- step 1: approval request `purchase` — 1 sample from supplier #, est <USD>
- step 2: on receipt, 5 short demo videos over 10 days (TikTok + Reels), one product page
- budget cap: sample + <= 50 USD optional boost; total <= 100 USD
- success criteria: >= 2 orders at target price OR >= 2% link CTR with >= 3k combined views
- stop conditions: cap spent, 10 days elapsed, or quality issue on sample
- approvals needed before anything happens: rows <ids> in approvals/requests.md

## Rejection reason (rejected/hold only)
