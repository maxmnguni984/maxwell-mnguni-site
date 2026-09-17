# Discovery report — run 2026-09-17-us-launch

Written by the Implementation Lead from the discovery agent's returned findings.
The agent could not write this file itself (subagents return findings as text),
so its content is persisted here. The agent's structured output is in
`discovery/candidates.jsonl`.

## Method, and what it cost us

Every commerce and research domain is refused by this environment's network
proxy at the CONNECT layer. The proxy is an allowlist, not a blocklist: only
github.com, raw.githubusercontent.com, api.github.com and pypi.org are
reachable. WebFetch, curl and a headless browser fail identically.

So every figure below comes from `WebSearch` scoped with `allowed_domains` to
one authoritative domain per query. That returns search-result snippets and a
synthesised summary, not a page anyone opened. **This is a real reduction in
evidence quality.** Every evidence entry is typed `search` rather than
`marketplace`, and every candidate carries a `SEARCH_SNIPPET_ONLY` flag, so the
weakness travels with the data instead of being lost in a footnote.

Amazon-scoped queries returned listings but almost never usable price text,
because its prices render client-side. Walmart-scoped queries with an explicit
price term in the query string worked, so Walmart became the pricing proxy.
Prices are therefore US retail comparables, not Amazon prices specifically.

27 of 30 permitted searches were used.

## What could not be obtained at all

- **Google Trends curves.** trends.google.com is blocked and every mirror found
  was an AI-generated content farm. No trend claim is made at fact level.
- **Meta Ad Library and TikTok Creative Center.** Unreachable.
- **Reddit and forum discussion.** Unreachable.
- **Review counts and rating distributions.** Complaint themes are obtainable;
  complaint frequency is not.
- **Sales volume, Best Sellers Rank, revenue.** Every tool that would show these
  is blocked.

Consequence, stated plainly: **`demand_verdict` is `unknown` for all 13
candidates.** The rule in `RULES.md` requires two independent signal types over
six months before demand may be called sustained, and only one signal type was
available. Seasonality is `UNKNOWN` throughout. Nothing was invented to cover
this.

## Candidates

13 produced against a cap of 15, each with at least two evidence entries. The
agent spent its budget on evidence depth rather than reaching the numeric cap,
which was the right call.

Comfortably inside the $25 to $60 band on the best available pricing:
collapsible car trunk organizer, adjustable aluminium laptop stand, adult
weighted blanket, cooling gel memory foam pillow, collapsible clothes drying
rack.

Below the band on observed retail, kept and flagged rather than silently
dropped: dog car seatbelt harness, compression packing cubes, self-cleaning
slicker brush, magnetic tool wristband.

Price only obtainable at category level, flagged assumption-grade: over-sink
dish rack, yoga mat, manual vacuum compression bags.

## Dropped before entering the file

Shower squeegee, garlic peeler, microfiber wash mitt, single-unit silicone
lids and non-slip stair treads all returned $5 to $15 pricing with no premium
variant found, so they failed the price band before any write-up. An insulated
tumbler two-pack produced a price range but no citable per-product URL, so it
was dropped rather than given a fabricated citation.

## Product-scope warning carried forward

The vacuum storage bag candidate is the **manual hand-pump** variant only. The
same search surfaced a USB-rechargeable cordless-pump version, which the brief
excludes as lithium-battery electronics. This distinction is recorded in the
candidate entry and repeated in every downstream agent brief.

## Safety finding worth its own line

A cpsc.gov-scoped search found a recurring recall pattern for resistance bands
with door anchors: five separate recalls and incidents between 2011 and 2026
for handles or anchors detaching and striking users, including about 95,000
units in a 2020 SPRI recall. Combined with $16.99 retail, that candidate is
rejected on two independent grounds.

CPSC checks were run for only 3 of 13 categories before the search budget was
committed elsewhere. The remaining 10 are marked `UNKNOWN` for recall history,
**not** assumed clean. The four products taken forward are all being checked by
the economics and risk agent.

## Lead's assessment

Two corrections to how this shortlist should be read.

**Bulk and weight are decisive, and discovery did not weight them.** The maximum
landed cost a product can bear includes its shipping. At these prices that
ceiling is roughly 39% of the selling price, about $12 to $16 per unit. A 15 lb
weighted blanket or a rigid drying rack plausibly consumes that in freight
alone. Two otherwise reasonable candidates fail on physics rather than on
demand.

**Demand is unverified for every candidate, so selection cannot rest on it.**
The shortlist is therefore ranked on what this environment can actually
establish: price-band fit, demonstration value for paid creative, safety and
recall exposure, shipping profile, and headroom against the cost ceiling. The
owner should know that a normally central input is missing, rather than be
shown a confident ranking that quietly lacks it.
