---
subject: Mid-tier smart ring, sold under the Vyra Health brand
date: 2026-09-17
status: complete
confidence: medium-high on the patent findings, medium elsewhere
verdict: no-go as a generic white-label; two narrow conditional paths exist
---
# Should Vyra Health sell a mid-tier smart ring?

**Short answer: not as a generic white-label.** The unit economics are the best of any product assessed in this project. Everything else about it is wrong.

A caveat on sourcing: every relevant primary domain was blocked from this environment, including the International Trade Commission, the Federal Register, Customs rulings, the FDA and patent databases. The findings below come from search-result summaries of those pages, not from pages read directly. Confidence is noted per claim, and the items that would change the answer are listed at the end as checks rather than conclusions.

---

## Why the economics tease

A smart ring weighs 3 to 5 grams. Against the weight-price frontier established earlier in this project, that puts US last-mile postage around $8 and sea freight at pennies per unit. At a $199 retail against a plausible $40 to $60 factory cost, it clears every economic gate that roughly 40 other products failed today.

This is precisely the shape the analysis converged on: light, high value, cheap to make, visually distinctive. That is exactly why the category is already occupied and defended.

## The patent position

### What happened

| Item | Finding |
|---|---|
| Investigation | ITC Inv. No. **337-TA-1398**, "Certain Smart Wearable Devices, Systems, and Components Thereof" |
| Complainants | Ouraring, Inc. and Ōura Health Oy |
| Filed / instituted | 13 March 2024 / April 2024 |
| Respondents | Ultrahuman (India), RingConn (China), Circular (France) |
| Patents asserted | **US 11,868,178** and **US 11,868,179**, both "Wearable computing device" |
| Final determination | **21 August 2025**, Section 337 violation found |
| Basis | Infringement of one or more of claims 1, 2 and 12 to 14 of the '178 patent |
| Remedy | **Limited** exclusion order plus cease-and-desist orders |
| Effective | 21 October 2025, after Presidential review |

### The crucial distinction

It is a **limited** exclusion order, not a general one. It binds only the named respondents, their affiliates, parents, subsidiaries, successors and assigns. **An unrelated importer's goods are not excluded merchandise on their face.** No evidence was found that a general exclusion order was sought or issued, though that conclusion rests on absence of reporting rather than on the order text, which could not be read directly.

So the common fear, that the ITC blocks all smart ring imports, is **not true**.

### Why that does not help much

The risk is not the border. It is that **importing and selling an infringing article is itself direct infringement** under 35 U.S.C. §271(a). White-labelling is not a shield. It makes you the named defendant, because you are the US entity with a US address and findable assets. "The factory said it was fine" is an indemnity claim against a Chinese entity, not a defence.

And the asserted claim reads on standard construction. The '178 covers a ring with an **external housing and a separate internal housing forming a cavity** containing a curved battery, circuit board and sensors. That is how nearly every mid-tier Chinese ring is built.

### The enforcement pattern

Oura has pursued essentially every meaningful entrant since March 2024:

| Company | Outcome |
|---|---|
| Circular | Licensed, 25 June 2024, royalties to Oura |
| RingConn | Settled 21 October 2025, the day the ban took effect. Multi-year royalty licence. ITC modified the order and rescinded the cease-and-desist as to RingConn on 12 December 2025 |
| Ultrahuman | Banned. Lost stay attempts at both the ITC and the Federal Circuit. Appeal still pending |
| Samsung, Reebok, Zepp, Nexxbase | Second ITC complaint filed 18 November 2025, instituted 18 December 2025, plus district court cases in the Eastern District of Texas |
| Zepp / Amazfit | Reported settled 21 August 2026 |
| Nexxbase | Reportedly out of the US market |
| OMATE | Reported licensed |

No evidence was found of Oura suing or filing Amazon takedowns against generic, no-name sellers. Every documented action targets a named, branded competitor with real market presence. **Treat that as descriptive, not protective.** A Vyra-branded ring at any volume is exactly the kind of findable target this campaign has consistently pursued, and Oura's stated posture is licensing rather than banning, which means the realistic outcome is a demand letter rather than a seizure.

Ultrahuman, a funded company, spent eighteen months and a Federal Circuit appeal to re-enter the US, and only succeeded by physically redesigning the product.

## The regulatory picture, which is better than expected

### FDA got materially easier in January 2026

FDA finalised revised **General Wellness: Policy for Low Risk Devices** on **6 January 2026**. Non-invasive wearables may now sense, estimate or infer physiologic parameters, **expressly including blood pressure, blood oxygen, blood glucose, heart rate and heart rate variability**, and still be treated as general wellness products, provided they are non-invasive, are not intended to diagnose or treat disease, do not substitute for a cleared device, and **never reference a specific disease or diagnostic threshold** in any labelling or promotion. FDA names smart rings among the covered types.

What still needs clearance: any claim tied to a named condition, atrial fibrillation notification in particular, anything using a diagnostic threshold, and anything positioned as replacing a cleared device.

Two live exceptions worth respecting:
- **Blood pressure** remains the most enforcement-exposed metric. FDA issued draft guidance on cuffless non-invasive blood pressure devices on 23 January 2026, and took a warning-letter position in mid-2025.
- **Glucose is the one to refuse outright.** FDA issued a safety communication on 21 February 2024 warning consumers not to use smartwatches or smart rings claiming non-invasive glucose measurement, stating that **no such device has ever been authorised**. Some Chinese rings advertise it. If the sourced ring or its app claims glucose, do not sell it.

Movano Health's Evie Ring obtained 510(k) clearance for pulse oximetry, which proves the pathway is open for a ring if a clinical claim is ever wanted.

### Lithium batteries are routine

A ring cell is roughly 15 to 25 mAh, well under one watt-hour. It ships as **UN3481, lithium-ion contained in equipment**, air packing instruction **PI 967 Section II**, comfortably inside the thresholds of under 20 Wh per cell and 100 Wh per battery.

**UN 38.3 testing is mandatory and applies to all transport modes**, including ground, and to batteries installed in a device. Missing documentation is a common cause of shipments being held at customs. You need the test summary and a safety data sheet before the first container moves. Carriers impose rules stricter than the IATA baseline, so confirm with the carrier rather than assuming.

Not a blocker, but note it sits alongside **FCC equipment authorisation** for the Bluetooth radio, which is mandatory and commonly missed by first-time importers.

## The two risks that are hardest to manage

### You would not own the product

A white-labelled ring is a sensor and a radio. Everything the customer actually bought, the sleep staging, readiness scores, history and trends, lives in the manufacturer's app and backend. You would have no source code, no escrow, and no ability to keep the service running if the manufacturer walks away or is cut off.

The precedent is concrete. Humane discontinued its AI Pin on **28 February 2025 and shut down the cloud service at noon the same day**, remotely bricking every $699 device with no refunds outside the normal return window. Pebble, Coin, Ringly and WiseWear all ended the same way, and the last two were smart-jewellery companies specifically.

Note the asymmetry in the Oura cases: when Ultrahuman and RingConn were banned, existing owners kept their apps, because both were funded companies that chose to keep serving customers. A small Shenzhen manufacturer that loses its US channel has no such incentive, and **you would hold the US warranty and consumer-protection obligations for a dead product**.

### Chinese data routing is a live and escalating exposure

- A **Department of Justice rule effective 8 April 2025** restricts bulk transfer of sensitive personal data, expressly including health and biometric data, to countries of concern including China. A US brand routing customers' health telemetry to a Chinese backend is the fact pattern this rule addresses. This needs specialist counsel, and it is the item most likely to be overlooked.
- **Washington's My Health My Data Act** regulates consumer health data outside HIPAA and carries a private right of action. The first class action was filed 10 February 2025 and was still pending in May 2026. Connecticut, Nevada and New York have similar laws without the private right of action.
- The **FTC Health Breach Notification Rule** covers wearable fitness trackers, with civil penalties reported at $53,088 per violation. A white-labeller using the manufacturer's app may have no visibility into a breach while still carrying the duty to notify.
- Senators have urged the FCC to add Chinese-linked health wearables, including fitness trackers, to its **Covered List** of prohibited equipment. **If that happens the sourcing strategy dies regardless of how well everything else is handled, and it cannot be mitigated.**

## Market structure

The mid-tier is compressing from both ends. Amazfit cut the Helio from $299 to $199 and made its subscription free for life. RingConn Gen 2 Air sits at $199. Oura is at $399 to $499 plus a $5.99 monthly membership, and Samsung's Galaxy Ring at $399.99.

"No subscription" is already the commodity differentiator, led by RingConn, Amazfit and Ultrahuman simultaneously. There is no positioning left in that phrase.

**Sizing is the operational tax.** It is the number one driver of returns in this category, ahead of battery life or features. Every major maker ships a free sizing kit, so it is table stakes rather than a differentiator. It converts a one-step purchase into a two-step funnel with drop-off in the gap, and RingConn treats kits as non-refundable consumables. A returned worn ring is a hygiene problem that probably cannot be restocked at full value. No credible published return-rate figure exists for smart rings; treat any number quoted elsewhere as unsourced.

## The two paths that could actually work

**1. Source from an existing Oura licensee.** RingConn, Circular, OMATE and Zepp are all reported as licensed or settled. Get **written confirmation that the licence covers rings sold under the Vyra brand**, because licences are normally drafted to cover the licensee's own branded products and almost certainly do not travel to a third-party white-label by default. Pair it with an IP indemnity backed by a US-enforceable entity or escrow.

**2. Source a unibody ring.** Customs ruling **H354023, dated 6 March 2026**, held that Ultrahuman's redesigned Ring Pro, built around an **integrally formed housing tube**, falls outside the exclusion order, because it does not practise all limitations of the '178 claims, **a point Oura itself conceded**. Customs reserved the right to demand CT scans and manufacturing records to verify the construction, so the manufacturer must supply that evidence. This is a real, documented safe harbour, but it is narrow: it addresses one patent, and Oura holds others.

On either path, treat these as hard gates before committing capital:

- Written continuity terms for the app and backend: notice period, code escrow, data export, right to migrate. A generic manufacturer will refuse. That refusal is the answer.
- US-hosted data, or at minimum no bulk US health data to China, with counsel on the DOJ rule.
- Marketing copy reviewed line by line against the January 2026 wellness guidance. Strip every atrial fibrillation, blood pressure and glucose claim.
- UN 38.3 summary, safety data sheet and FCC ID in hand before the first shipment.
- Sizing kit modelled as a real cost and a real funnel step.

## The one thing that could change the answer

Samsung challenged the '178 patent at the Patent Trial and Appeal Board in **PGR2024-00030**, filed 31 May 2024, challenging claims 1 to 18. Institution was granted 6 December 2024 on a finding that the claims were more likely than not obvious.

**The final outcome is reported inconsistently.** One docket summary says the decision found the claims unpatentable and is on appeal. Two others say Samsung failed to show claims 1 to 17 unpatentable. A Bloomberg Law headline reading "Samsung Fails to Invalidate Patent" concerns **US 11,188,124**, a different Oura patent, so these may be separate proceedings being conflated.

**If claims 1 to 18 of the '178 are in fact cancelled and that survives appeal, Oura's moat and the 337-TA-1398 order both collapse, and this becomes a different business case.** That is a single docket check, not a research project, and it should be the first thing done if this category is pursued.

## Other unresolved items

- Whether a general exclusion order exists in any of the newer investigations. If one does, the verdict moves from risky to impossible. Verify from the order text on the ITC's EDIS system.
- The docket number for Oura's second ITC complaint. Sources conflict between 337-TA-1477 and 337-TA-1478, and the latter is more reliably Samsung's counter-complaint against Oura.
- Oura's full patent inventory. Only US 11,868,178, 11,868,179 and 11,188,124 were confirmed. Several other numbers surfaced but could not be verified for assignee, title or grant date and are deliberately not listed here.
- Section 301 tariff treatment and customs valuation for Chinese-origin wearables, which materially affects the unit economics quoted at the top.

## Bottom line

The margin on a $150 to $300 white-label ring does not cover the cost of a single patent demand letter, and you would be buying a business whose core asset, the app, belongs to someone else.

If the Vyra Health brand is the thing worth preserving, the lower-risk versions are becoming an authorised dealer for an established ring, which removes the patent exposure entirely at the cost of thinner margins, or selling into the category without selling the ring itself.
