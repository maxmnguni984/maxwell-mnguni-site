# Research brief: 2026-09-17-us-round2

Second discovery sweep. The owner reviewed round one's shortlist and asked for
new products, so none of round one's thirteen candidates may be re-proposed.

| Field | Value |
|---|---|
| Market | United States, general consumer, USD |
| Platform | Shopify target, built locally first |
| Spend authorization | **ZERO** |
| Marketing | Paid ads from day one, plus organic |
| Delivery limit | 12 days tracked to a US address |
| Discovery cap | 16 candidates across two sweeps |
| Excluded | Branded or licensed goods; supplements; cosmetics; medical or health-claim devices; mains-powered or lithium-battery electronics; weapons; kids' toys and baby products; anything needing FDA, FCC or CPSC certification |
| Also excluded | Every dedupe_key in `exclude-dedupe-keys.txt` |

## What round one taught us, now enforced as hard filters

Round one produced thirteen candidates and only one cleared every gate. The
failures were not random; they clustered, and the clusters are now entry
requirements rather than things discovered late.

**1. Price floor raised from $25 to $30.** Four of thirteen died because
observed retail sat under the $25 floor. The maximum landed cost a product can
bear is about 39% of selling price once paid acquisition is funded, so a low
price leaves nothing to buy the goods with. At $30 that ceiling is $11.51; at
$45 it is $17.93. Candidates whose observed retail midpoint is below $30 are
dropped, not flagged.

**2. Light and compact is now mandatory.** Landed cost includes freight. A 15 lb
weighted blanket and a rigid drying rack both died on shipping volume alone.
Target under 1 kg, and it must pack flat or compress. A rigid item that cannot
fold is rejected regardless of how good it looks.

**3. Demonstration value of at least 4 out of 5.** Paid ads run from day one. A
product whose benefit cannot be shown in five silent seconds is the wrong bet,
and round one's yoga mat was rejected on that alone.

**4. Avoid product types whose name matches a design patent.** Round one found
two design patents titled almost exactly "adjustable over the sink dish drying
rack". Where a product category is defined by one distinctive ornamental form,
IP risk is structural. Prefer categories with many visually different designs.

**5. Prefer a product with a specific, quotable failure mode.** The trunk
organizer ranked first partly because buyers complain in precise language about
flimsy bases and plastic buckles. That is what makes a differentiation claim
credible instead of invented.

## Method, unchanged and non-negotiable

The network proxy is an allowlist permitting only github.com,
raw.githubusercontent.com, api.github.com and pypi.org. WebFetch and curl are
useless. Domain-scoped WebSearch is the only channel. Walmart-scoped queries
carrying an explicit price term work; Amazon-scoped price queries mostly do not.

Every claim is graded. Nothing is invented. Demand remains unverifiable, so
candidates are ranked on price-band fit, shipping physics, demonstration value,
complaint specificity and risk exposure.

## Filter F7 added mid-round, 2026-09-17

Sweep A returned a non-electric bidet attachment that scored highest of the four
on 75.0, ahead of every rival. Its own record said the price basis was
`ASSUMPTION`: the figures came from an aggregated search answer and could not be
matched to any listing URL.

Everything downstream is computed from price. The landed-cost ceiling is price
times roughly 0.39, and break-even cost per acquisition falls straight out of
it. Ranking an unverified price as though it were measured is how a store gets
built on a number nobody checked.

So `screen.py` now rejects any candidate whose price basis is assumption-grade,
and the rule is tested rather than remembered. The bidet also carried a
`PLATFORM_POLICY` flag for advertising restrictions around genital-hygiene
imagery, which would have been a second problem for a paid-ads-first store.

## Filters F8 added and weight parsing fixed, 2026-09-17

**F8, injury recalls.** Sweep B returned an expandable garden hose carrying a
2025 CPSC recall of "burst-proof" hoses citing 222 burst reports and 29
injuries. It was rejected, but only because its price was out of band. Had it
been $50 it would have passed with a merely poor risk score. A safety record
should not be something a score can outweigh, so an injury recall is now a hard
filter. Back-checked against round one: it independently catches the resistance
bands.

**Weight parsing was broken.** Both sweeps recorded weight in a nested
`weight_and_pack_form` field that the parser did not read, so the weight filter
never fired on a single candidate and was effectively inert for the whole round.
Now fixed, it also catches the garden hose at 1.4 kg. An admitted-uncertain
weight now scores below a confirmed one rather than passing silently, because an
unconfirmed weight is not the same thing as a light product.
