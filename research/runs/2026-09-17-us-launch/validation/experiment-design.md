# Validation experiment design

Written 2026-09-17. Applies to whichever product the owner selects. Every
figure below is computed by `research/tools/cost_ceiling.py`, not asserted.

**Nothing here has been run. Every paid stage needs written approval, and
current spend authorization is zero.**

## The number everything hangs on

Break-even cost per acquisition equals contribution margin per order. At the
base-case assumptions, and assuming the product is sourced exactly at its
landed-cost ceiling:

| Product | Price | Break-even CPA | Landed cost ceiling |
|---|---:|---:|---:|
| Laptop stand | $30.46 | $10.97 | $11.71 |
| Trunk organizer | $34.99 | $12.60 | $13.65 |
| Dish rack | $35.00 | $12.60 | $13.65 |
| Vacuum bags | $25.00 | $9.00 | $9.37 |

Read that carefully. A break-even CPA of $12.60 is demanding for cold US paid
traffic on a first store with no pixel history, no reviews and no brand. It is
not impossible. It is not comfortable either, and the plan should not pretend
otherwise.

## What a small budget can and cannot prove

This is the part usually skipped, so it goes first.

To observe enough conversions to say anything reliable about conversion rate,
at the trunk organizer's break-even CPA, and generously assuming the CPA lands
exactly at break-even rather than above it:

| Conversions observed | Spend required | Margin of error on the rate |
|---:|---:|---:|
| 5 | $63 | about ±45% |
| 10 | $126 | about ±32% |
| 30 | $378 | about ±18% |
| 100 | $1,260 | about ±10% |

So a $150 test **cannot** tell you whether the product converts profitably. At
ten conversions the error bar is wider than the difference between a winner and
a loser. Anyone who tells you $150 validates a product is selling you
something.

What a small budget genuinely can measure, because these need impressions
rather than conversions:

- Whether the creative earns attention: hold rate, thumb-stop rate.
- What it costs to buy a click: CPM and cost per click.
- Whether the click survives the landing page: bounce and add-to-cart rate.

Those are leading indicators. They kill bad products cheaply, which is their
real job. They do not confirm good ones.

## Stage 0: organic, $0, before any money moves

Runs first because it costs nothing and answers the cheapest question.

- Post 6 to 8 short vertical videos over 14 days across TikTok, Reels and
  Shorts, built on the differentiation angle the competitor agent identified
  from real complaint language.
- Every video is our own footage of a product we physically hold. No supplier
  stock footage, no competitor clips, no staged demonstration that overstates
  what the product does.

**Proceed to Stage 1 only if:** at least one video passes 10,000 views, or the
average passes 1,500. **Stop if:** the average is under 500 after six posts.
That is the market saying the angle does not land, and paid traffic will not
fix a message nobody wants.

Stage 0 requires a sample in hand, which is approval item 3.

## Stage 1: paid creative test, $150 cap

**Purpose: find out what attention costs. Not whether the product sells.**

- $150 total. Three creatives, $10 per day each, five days.
- One audience, broad, no manual interest stacking. With this budget, narrow
  targeting only guarantees too little data.
- Traffic or engagement objective, not conversions. There is not enough volume
  for a conversion objective to optimise against.

Success, judged per creative:
- Cost per click at or under $1.00
- Click-through rate at or above 1.0%
- Three-second video hold rate at or above 20%
- Add-to-cart rate at or above 4% of landing page sessions

Stop immediately if:
- Cost per click exceeds $2.00 after $50 spent on a creative
- Any advertising policy rejection or account flag
- Zero add-to-carts after 300 landing page sessions
- Cumulative spend reaches $150, whatever the result

## Stage 2: conversion test, $400 cap, separate approval

Only entered if Stage 1 passes, and only with a fresh written approval. This is
the stage that costs real money, so it gets its own decision.

- $400 total across 10 to 14 days on the winning creative.
- Conversion objective, optimising for purchase.
- Target: 30 or more conversions, which is the smallest number carrying an error
  bar under about ±18%.

Success: cost per acquisition at or below $12.60 with the product landed at or
under its ceiling, sustained across the final five days rather than in one
lucky spike.

Stop if: CPA exceeds $25 after $200 spent, any policy strike occurs, supplier
processing exceeds five days, or the refund rate exceeds 10% on the orders
received.

## What could make the whole test invalid

Stated up front, because a test that cannot fail is not a test.

1. **No verified supplier cost.** If the real landed cost exceeds the ceiling,
   a passing test still means a loss on every order. The supplier quote must
   land before Stage 2, not after.
2. **No sample inspected.** Selling a product nobody has held produces refunds
   that arrive weeks after the test looks successful.
3. **Delivery time unverified.** The 12-day tracked promise is currently
   unproven. Slow delivery converts fine and refunds later.
4. **Small numbers lie.** Stage 1 measures attention only. Treating a good CPC
   as proof of a winner is the single most common way this goes wrong.

## Total exposure if every stage is approved

| Item | Cap |
|---|---:|
| Sample order | $30 |
| Stage 1 creative test | $150 |
| Stage 2 conversion test | $400 |
| Shopify plan, one month | to be confirmed |
| Domain, one year | to be confirmed |
| **Total** | **about $580 plus platform costs** |

Each line is a separate approval. None is authorized now.
