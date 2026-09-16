# KDP requirements for this book

Accessed 2026-09-16. Marketplace: Amazon.com. Format: paperback, black ink on white paper, 8.5 x 11 in.

**Confidence labels used throughout this project**
- `VERIFIED*` — text returned from the official kdp.amazon.com help page cited. Not eyeball-confirmed on the live page, because `kdp.amazon.com` is blocked by this session's network egress proxy.
- `UNVERIFIED` — could not be confirmed from an official source. Never used as a basis for pricing or file specs.

---

## Trim, margins, bleed

| Item | Value | Confidence | Source |
|---|---|---|---|
| Trim 8.5 x 11 in available for paperback | Yes | VERIFIED* | [Trim Size, Bleed, and Margins](https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6) |
| Classed as large trim | Yes, large trim is wider than 6.12 in or taller than 9 in | VERIFIED* | same |
| Outside, top, bottom margin, no bleed | 0.25 in minimum | VERIFIED* | same |
| Outside, top, bottom margin, with bleed | 0.375 in minimum | VERIFIED* | same |
| Gutter, 24 to 150 pages | 0.375 in | VERIFIED* | same |
| Gutter, 151 to 300 pages | 0.5 in | VERIFIED* | same |
| Bleed amount | 0.125 in on top, bottom and outer edge only, never the gutter | VERIFIED* | same |
| Document size with bleed | Trim + 0.125 in width, + 0.25 in height. So 8.625 x 11.25 | VERIFIED* | same |

**Decision for this book: no bleed.** The art sits inside a white margin, which is normal for colouring books, removes a whole class of trim error, and means the document is exactly 8.5 x 11.

### Our page geometry

| Item | Value |
|---|---|
| Document page | 8.5 x 11 in |
| Gutter | 0.5 in (chosen above the 0.375 in minimum for comfort) |
| Outer, top, bottom margin | 0.5 in (chosen above the 0.25 in minimum) |
| Art box | 7.5 x 10 in, which is exactly 3:4 |
| Art box at 300 DPI | 2250 x 3000 px minimum |
| Art box at 600 DPI | 4500 x 6000 px |

The 3:4 art box matches a native Higgsfield aspect ratio, so no generated image is ever stretched or cropped to fit.

## Interior file

| Item | Value | Confidence | Source |
|---|---|---|---|
| Format | PDF (required if bleed is used; PDF is fine either way) | VERIFIED* | [Paperback Submission Guidelines](https://kdp.amazon.com/en_US/help/topic/G201857950) |
| Image resolution | 300 DPI minimum, 600 DPI recommended | VERIFIED* | same |
| Fonts and images | Must be embedded; flatten transparencies; remove crop marks and template layers | VERIFIED* | same |
| Max file size | 650 MB | VERIFIED* | same |
| Page count, black ink on white | 24 to 828 | VERIFIED* | [Print Options](https://kdp.amazon.com/en_US/help/topic/G201834180) |
| PDF/X or PDF/A required? | No official statement found. KDP says "PDF" | UNVERIFIED | — |
| Paper options, black ink | White, cream, or groundwood. Groundwood is about 5% cheaper per page | VERIFIED* | [Groundwood Paper](https://kdp.amazon.com/en_US/help/topic/G99WKT9FARBGHBJF) |

Ink type cannot be changed after publication (VERIFIED*), so the black-ink-on-white choice is effectively permanent for this title.

## Cover

| Item | Value | Confidence | Source |
|---|---|---|---|
| Format | One PDF, single flattened layer, back + spine + front as one image | VERIFIED* | [Create a Paperback Cover](https://kdp.amazon.com/en_US/help/topic/G201953020) |
| Resolution and colour | 300 DPI minimum, CMYK, fonts embedded | VERIFIED* | same |
| Exact dimensions and spine width | Generate from the official calculator for the final page count | VERIFIED* | https://kdp.amazon.com/cover-calculator |
| Barcode keep-out | 2 x 1.2 in, lower right of the back cover, kept clear of text and art | VERIFIED* | [Barcodes](https://kdp.amazon.com/en_US/help/topic/G5HDYGP4BXLX4RUW) |
| Per-page spine thickness values | Not published in extractable form. Third-party values conflict | UNVERIFIED | — |

The spine width is never hand-calculated for this project. It comes from the Cover Calculator, run against the final page count after the interior is locked.

## AI-generated content disclosure

Quoted verbatim from [Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390), VERIFIED*:

> "We require you to inform us of AI-generated content (text, images, or translations) when you publish a new book or make edits to and republish an existing book through KDP."

> "You are not required to disclose AI-assisted content."

> "You are responsible for verifying that all AI-generated and/or AI-assisted content adheres to all content guidelines, including by complying with all applicable intellectual property rights."

AI-generated images explicitly include cover and interior artwork. AI-generated content is **permitted for sale**; the requirement is disclosure, not prohibition.

**What this means for us, stated plainly:** every illustration in this book is AI-generated. At publish time the honest answer to the AI-content question is **yes, for images**. There is no version of this project where we answer otherwise.

## Content, IP and metadata policy

| Rule | Confidence | Source |
|---|---|---|
| Titles may not contain keywords, genre descriptions, promotional text, or references to other books | VERIFIED* | [Metadata Guidelines](https://kdp.amazon.com/en_US/help/topic/G201097560) |
| Metadata must not produce inaccurate search results; zero tolerance for misleading content | VERIFIED* | [Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390) |
| Keywords: nothing misleading, nothing unrelated; 2 to 3 word phrases recommended | VERIFIED* | [Keywords](https://kdp.amazon.com/en_US/help/topic/G201298500) |
| A named ban on the word "bestseller" in titles | UNVERIFIED — but it falls under the promotional-text prohibition, so we avoid it | — |
| Reading age must be set or children's categories may not apply | VERIFIED* | [Primary Audience and Reading Age](https://kdp.amazon.com/en_US/help/topic/G201506310) |

## Low-content status

Colouring books with frequent blank pages are treated as low content (VERIFIED*, [Low-Content Books](https://kdp.amazon.com/en_US/help/topic/GGE5T76TWKA85DJM)). Consequences:

- No free KDP ISBN, and none is required.
- Not eligible for series.
- Journals, notebooks and planners with frequent blank or lined pages are not accepted for Expanded Distribution. Whether a single-sided colouring book is caught by this is **UNVERIFIED**.

This is the tension in the build: blank reverse pages are the right call for the reader, since they stop marker bleed-through ruining the next design, but they push the book further into low-content territory. The alternative is a light doodle frame on each reverse.

## Printing cost and royalty

| Item | Value | Confidence | Source |
|---|---|---|---|
| Printing cost formula | Fixed cost + (page count x per-page cost) | VERIFIED* | [Printing Cost](https://kdp.amazon.com/en_US/help/topic/G201834340) |
| Official worked example | 300-page black ink, regular trim: $1.00 + (300 x $0.012) = $4.60 | VERIFIED* | same |
| Large-trim fixed cost and per-page rate | Sources conflict: $0.012 vs $0.015 per page, $0.85 vs $1.00 fixed | **UNVERIFIED** | — |
| Royalty formula | (rate x list price) − printing cost; rate is 60% or 50% | VERIFIED* | [Royalty](https://kdp.amazon.com/en_US/help/topic/G201834330) |
| Minimum list price | Set so royalty always covers printing cost | VERIFIED* | same |

**Nothing in this project gets priced off the unverified rates.** The real figure comes from https://kdp.amazon.com/en_US/royalty-calculator, captured in Part 5 of the capture sheet.

## Proofs

| Item | Value | Confidence | Source |
|---|---|---|---|
| Print Previewer must pass before a proof can be ordered | Yes | VERIFIED* | [Proof and Author Copies](https://kdp.amazon.com/en_US/help/topic/G7BBN68RYX5UMDZF) |
| How to order | Book in Draft, Bookshelf, "…" menu, Request Printed Proofs. Up to 5 per order, link by email within 4 hours | VERIFIED* | same |
| Cost | Print cost per copy plus shipping | VERIFIED* | same |
| Proof appearance | Carries a "Not for Resale" watermark and a non-ISBN barcode | VERIFIED* | same |

A physical proof is ordered and inspected before release. Screen preview does not reveal line weight, paper show-through, or how the gutter eats into the art on a bound page.
