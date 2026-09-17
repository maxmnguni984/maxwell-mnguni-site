---
run_id: 2026-09-17-r1
agent: discovery
date: 2026-09-17
status: partial
confidence: low
---
# Discovery summary

14 candidates screened. **Only 4 meet the sustained-demand bar on dated, independent, non-commercial signals.** Eight are UNKNOWN or hype and should not be funded on this evidence.

## Evidence quality, stated first

No web page could be opened. WebFetch was blocked on all six domains attempted, including non-retail ones. Every row below rests on search-result titles and URLs plus the search tool's synthesised summaries.

The one piece of genuinely hard dating evidence comes from decoding TikTok video IDs. Those IDs are snowflake IDs whose high bits are a unix timestamp, so `id >> 32` gives a real post date computed locally. That gives creator-independent, dated signals. It says nothing at all about a video's reach: **there is no view count, engagement figure or audience size anywhere in this run.**

Numbers seen in search summaries but sourced to pages that could not be opened, such as "6,000 monthly sales" and "50 million TikTok views", are **not carried forward**. They are UNKNOWN, and the sites hosting them sell sales-estimate reports, so they have a commercial incentive to overstate.

## Candidates

| # | Product | Niche | Demand | Retail observed | 5-sec demo | Fatal or serious flag |
|---|---|---|---|---|---|---|
| 1 | Car seat gap filler | car | **Sustained**, 37-month span | $20-35 | Excellent | **US Patent 8,267,291, actively enforced, Federal Circuit case** |
| 2 | Reusable pet hair roller | pet | **Sustained** | $20-32 | Excellent | **Enforced utility patent, 320+ counterfeit takedowns** |
| 3 | Dog paw cleaner cup | pet | **Sustained**, best date span 2021-2023 | $18-28 | Very good | Below price floor; "Original" brand incumbent |
| 4 | Silicone stretch bowl lids | home | **Sustained** | $9-34 | Moderate | Commoditised; food-contact compliance |
| 5 | Sink sponge caddy | home | Weak, one platform, affiliate-tinged | $12-30 | Weak | $5 category anchor, poor pricing power |
| 6 | Peanut massage ball | fitness | Sustained if affiliate sources accepted | $15-30 | Moderate | **Standard marketing is therapeutic claims — near-exclusion** |
| 7 | Textured foam roller | fitness | UNKNOWN | $20-45 | Poor | Dimensional weight likely fatal |
| 8 | Stretching strap, door anchor | fitness | **Hype**, no organic signal | $15-30 | Good | Injury vector if anchor fails |
| 9 | Cat litter mat | pet | UNKNOWN, seller listings only | $20-40 | Moderate | Bulky, commoditised |
| 10 | Sink splash guard mat | home | UNKNOWN | $12-28 | Good | Only quantitative claim sits behind a blocked page |
| 11 | Rubber carpet rake | pet | UNKNOWN | $16-27 | Excellent | Reveals hair but does not collect it: return risk |
| 12 | Olive oil sprayer | home | UNKNOWN | $15-30 | Good | Documented clogging and leaking; glass in transit |
| 13 | Pull-out cabinet organiser | home | UNKNOWN, leaning hype | **$25-45** | Good | Heavy steel; only candidate inside the price band |
| 14 | Slow feeder dog bowl | pet | UNKNOWN | $10-20 | Moderate | Bloat prevention is a health claim; price too low |

Screened out before listing: automatic pan stirrer, handheld vacuum sealer, electric paw cleaners, vibrating massage balls (all battery or mains); vegetable chopper (live design patents D1008759 and D1066993, plus blade safety); car headrest hooks and resistance bands (price floor and safety).

## Three patterns worth naming

**The best demos carry the worst legal risk.** The three most demo-friendly products found (car seat gap filler, pet hair roller, vegetable chopper) all sit on actively enforced patents. That is not coincidence. A product that demonstrates instantly on camera is a product worth patenting and worth enforcing.

**Health-claim creep is the default in fitness.** Massage ball, foam roller, stretching strap and slow feeder all come with therapeutic marketing as the industry norm. The products themselves pass the exclusion list; the standard sales angle does not.

**The top layer of search results for this market is advertising.** TikTok Shop listings, affiliate roundups and "ranked by real sales" SEO pages dominate. None of it has been counted as evidence of demand.

## Prompt-injection check

Nothing in any result read as instructions aimed at an AI. Seller-authored listing copy and affiliate pages were treated as commercially motivated data, never as guidance.
