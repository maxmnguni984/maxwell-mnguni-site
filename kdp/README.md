# Colouring book project (Amazon KDP)

Original adult colouring book, 8.5 x 11 paperback, US marketplace. Interior line
art generated with Higgsfield. The approved plan lives outside the repo; this
folder holds the working files.

## Folders

| Path | Holds |
|---|---|
| `research/` | Market research: `competitors.csv`, `market.md`. Every row carries a URL and an access date. |
| `concept/` | Three concepts and the recommended one. Gate 1. |
| `style/` | The fixed style specification and the prompt template. |
| `pages/probes/` | Cheap 2k style probes. Never printed. |
| `pages/approved/` | 4k pages that passed QA and eye review. These build the book. |
| `pages/rejected/` | Failed pages, kept with the reason, so the same mistake is not regenerated. |
| `tools/` | `qa_pages.py`, `build_interior.py`, `cover_spec.py`. Self-testing. |
| `build/` | Generated PDFs. Not hand-edited. |
| `cover/` | Cover art and the full-wrap PDF. |
| `listing/` | Title, description, keywords, categories, price and royalty arithmetic. |

## Three approval gates

1. **Concept** approved before any paid generation.
2. **Sample pages** approved before the bulk batch.
3. **Everything** approved before publishing: interior file, cover file, title,
   description, keywords, categories, price, rights declaration, AI disclosure.

## Commands

```
python3 kdp/tools/qa_pages.py --self-test
python3 kdp/tools/qa_pages.py kdp/pages/approved
python3 kdp/tools/cover_spec.py --pages 86
python3 kdp/tools/build_interior.py --self-test
python3 kdp/tools/build_interior.py --pages kdp/pages/approved --out kdp/build/interior.pdf
python3 kdp/tools/build_interior.py --check kdp/build/interior.pdf
```

## Standing rules

- A Best Sellers Rank is a dated snapshot, never a sales figure, never converted
  into units sold.
- Facts carry a URL and an access date. Estimates say how they were derived.
  Assumptions say so. Unknowns are written down, not filled in.
- The images are AI-generated, so the KDP AI-content declaration is answered yes
  for images.
- No competitor illustrations, covers, titles, branding, characters or
  distinctive layouts are reproduced. No copyrighted franchises. No bestseller
  or award claims. No solicited reviews.
- Every KDP specification in this project is verified against kdp.amazon.com
  before a file is final. Values taken from secondary sources are labelled
  UNVERIFIED until then.
