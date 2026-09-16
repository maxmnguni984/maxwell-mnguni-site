# Kids' colouring book, ages 4 to 8 — Amazon KDP project

An original colouring book, researched against real Amazon data, illustrated with Higgsfield, published on Amazon.com.

**Brief:** kids aged 4 to 8, bold and simple line art, Amazon.com, budget up to 150 USD, theme chosen from research.

## Where things stand

| Step | State |
|---|---|
| KDP requirements verified | Done, `specs/kdp-requirements.md` |
| Higgsfield rights and costs researched | Done, `specs/higgsfield-terms-and-costs.md`, three blocking items |
| Market research | **Waiting on you**, `research/capture-sheet.md` |
| Concept | Blocked by research |
| Art | Blocked by concept, licence confirmation and top-up |
| Book build | Not started |
| Listing | Not started |

## What needs you next

1. **Capture Amazon data.** Follow `research/capture-sheet.md`, roughly 30 minutes. Amazon.com is blocked from this environment, so I cannot pull ranks, prices or reviews myself, and I will not invent them.
2. **Confirm the Higgsfield licence.** Open the Terms of Use, confirm §4.4 permits commercial use, save a dated PDF into `specs/`. This gates all bulk generation.
3. **Read your credit price.** From your Higgsfield billing page. The API endpoint for pricing is erroring and the pricing page is blocked here.

## Folder map

| Path | Contents |
|---|---|
| `specs/` | Verified KDP requirements, Higgsfield rights and costs |
| `research/` | Capture sheet, then the market analysis |
| `inputs/captures/` | Your pasted Amazon text and screenshots, dated |
| `concepts/` | The three concepts and the chosen one |
| `art/samples/` | Sample pages for approval |
| `art/final/` | Approved pages, watermark-checked |
| `art/rejected/` | Rejected pages with the reason |
| `build/` | Interior PDF, cover PDF |
| `listing/` | Title, description, keywords, categories, royalty maths |
| `approvals/gates.md` | Every gate and every credit spent |
| `scripts/` | Line art cleanup and PDF assembly |

## Ground rules

- A Best Sellers Rank is a dated snapshot of a rank, never a sales figure. Nobody outside Amazon can convert one into the other, and this project will not pretend otherwise.
- Every figure carries a source and a date, or it is labelled unverified.
- Original work only. No franchise, character, mascot or licensed property. No imitation of a competitor's illustrations, cover, title, branding or layout.
- No keyword stuffing, no competitor trademarks, no bestseller claims, no fake reviews.
- Every illustration is AI-generated, so KDP's AI disclosure is answered yes for images. There is no other honest answer.
