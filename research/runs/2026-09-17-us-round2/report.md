# Round 2 shortlist — run 2026-09-17-us-round2

Two discovery sweeps over separate category clusters, ten candidates, screened
mechanically by `research/tools/screen.py`. All figures dated 2026-09-17.

## Recommendation

**The packable foldable travel daypack.** It ranks first not because it is the
most exciting product in the set, but because it is the only one whose evidence
actually holds up on every dimension that matters:

- **Weight is a confirmed fact**, 0.6 lb, roughly 0.27 kg. Every other candidate
  has an estimated weight. Freight is the input most likely to break the
  landed-cost ceiling, and this is the only candidate where it is measured.
- **Price is corroborated**, $33.99 to $40.33 across more than one listing,
  rather than a single data point.
- **The complaint is specific and quotable**: "the top zipper unzipped and broke
  before they even used it." That is the raw material for a credible
  differentiation claim. Four of the seven survivors have no complaint evidence
  at all.
- **Best possible shipping profile.** A packable bag is soft, light and folds
  into itself. Nothing in this set ships more cheaply.

At $37.16 the maximum landed cost is $14.58 and break-even cost per acquisition
is $13.11.

## Ranked survivors

| # | Product | Price | Max landed | Demo | Weight | Score | Evidence gaps |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Packable travel daypack | $37.16 | $14.58 | 4 | 0.27 kg FACT | 49.6 | none material |
| 2 | Magnetic car phone mount | $34.91 | $13.62 | 5 | under 1 kg est | 46.3 | complaints are competitor-level, not product-level |
| 3 | Packable gym duffel | $49.86 | $20.01 | 4 | ~0.9 kg est | 42.0 | single-source price, no complaints, no recall check |
| 4 | Self-cooling pet gel mat | $35.00 | $13.65 | 4 | ~0.7 kg est | 37.8 | single-source price |
| 5 | Waterproof mattress protector | $45.88 | $18.31 | 4 | under 1 kg est | 37.3 | single-source price, no complaints, sleep-category returns risk |
| 6 | Foldable tabletop easel | $36.98 | $14.50 | 4 | ~0.8 kg est | 33.5 | single-source price, category mostly sits under $30 |
| 7 | Zippered underbed storage set | $39.99 | $15.79 | 4 | uncertain | 32.7 | single-source price, weight may breach the cap |

## Rejected, with the filter that caught each

- **Expandable garden hose.** Failed four filters at once. Out of price band at
  $73.94, estimated 1.4 kg, rigid, and carrying a 2025 CPSC recall of
  "burst-proof" hoses citing 222 burst reports and 29 injuries. The recall alone
  is disqualifying.
- **Non-electric bidet attachment.** Scored highest of all ten on first pass,
  then failed on price evidence: its own record marked the price ASSUMPTION,
  taken from an aggregated answer with no listing behind it. It also carried an
  advertising-policy flag for genital-hygiene imagery.
- **Retractable clothesline reel.** Rigid wall-mounted reel; does not pack flat.
  It is also load-bearing, which the round 2 safety steer warns against.

## Three tooling fixes this round forced

Each was found by running the screen on real data, not by inspection.

1. **Assumption-grade prices are now rejected outright.** The bidet outscored
   every rival on a price nobody could verify. The landed-cost ceiling and
   break-even CPA are both computed from price, so an unverified price puts the
   whole case on sand.
2. **Recalls citing injury are now a hard filter, not a score input.** The
   garden hose only escaped on price. Had it been $50 it would have passed with
   a merely poor risk score, despite 29 reported injuries. Back-checked: this
   filter independently catches round one's resistance bands.
3. **Weight parsing was broken, so the weight filter was inert.** Both sweeps
   recorded weight in a nested field the parser did not read, meaning no
   candidate was ever weight-checked. With it fixed, the garden hose fails on
   weight too, and an admitted-uncertain weight now scores below a confirmed one
   instead of passing silently.

## Competitor research on the top two, and the wall it hit

Both products now have real complaint evidence. It is good evidence, and it
points somewhere uncomfortable.

### Packable travel daypack

Competitors run $29.99 to $44.95 across Walmart, Target and REI, so our $33.99
to $40.33 sits comfortably inside the band. Four distinct product-level
complaint sources yielded well over ten separate complaints:

- The top zipper unzips or breaks before first use.
- The zipper tears away from the bag body within months.
- Straps break off within weeks.
- Seams fail within days, at multiple points.
- The ultralight fabric has "virtually no abrasion resistance"; one reviewer
  called it "a fancy shopping bag with a zipper".

Read that list again. These are not one fixable flaw in one bad product. They
describe a whole category that is structurally flimsy, because ultralight
packable bags are made cheaply by default. Buy a generic one and you inherit
every complaint above, then pay for advertising to send people to it.

### Magnetic car phone mount

Competitors run $24.99 to $39.99. Complaints: magnets too weak to hold the phone
at all, the magnetic top plate separating from the base, vent clips too loose so
the whole thing falls to the floor, and the clip cracking within a month.

Three specific risks, all real:

- **MagSafe is a live Apple trademark.** It must never appear in our title,
  store name or advertising. Two competitors put it directly in their listing
  titles. That is a pattern to avoid, not to copy.
- **Credit-card demagnetisation** is a genuine and independently raised consumer
  concern, which means a packaging warning, never an advertising claim.
- **Distracted-driving optics.** Creative must not show a driver interacting
  with a phone in a moving vehicle.

No CPSC recall was found for passive magnetic mounts, but that rests on a single
query and is recorded as inconclusive rather than clean. Pacemaker interference
was not checked and remains open.

### The finding that matters

For **both** products, two of the three differentiation angles are labelled
`requires_product_change`: reinforced zipper tracks and bar-tacked strap anchors
for the bag, a stronger magnet array and a locking vent clip for the mount.

Only one angle per product is testable in content alone.

So the thing that would make either product work is not positioning, not copy,
and not creative. It is sourcing a unit genuinely better than the category
default. **And supplier quality is precisely what cannot be verified from this
environment.**

That is the wall. Round one hit it on landed cost; round two hits it on product
quality, from a different direction. More desk research will not move it. A
sample in hand will, and it is the cheapest unblocking step available.

## What is still unknown

Unchanged from round one and not fixable from this environment: supplier landed
cost, verified delivery time, real demand data, review counts and competitor ad
activity. Four of seven survivors also lack complaint evidence, because both
sweeps spent their search budget on price discovery.

Gate G7, the evidence floor, therefore still fails on every candidate. As in
round one, this is a recommendation of direction, not a validated winner.

## Note on the price floor

Raising the floor from $25 to $30 removed roughly twenty product types across
the two sweeps: silicone kitchen goods, velvet hangers, dusters, car trash cans,
beach blankets, toiletry bags and most desk accessories. The desk and home
office cluster came back empty entirely.

That is the filter working as designed, but it is worth knowing the cost. If the
shortlist is too thin, the honest lever is to widen the band rather than lower
the evidence standard.
