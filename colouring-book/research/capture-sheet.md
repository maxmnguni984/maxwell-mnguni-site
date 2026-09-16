# Amazon capture sheet — kids' colouring books, ages 4 to 8

**Why you are doing this and not me:** `www.amazon.com` is blocked by this session's network proxy. I confirmed it directly. Anything I wrote about ranks, prices or review counts without your captures would be a secondhand guess, and guesses are exactly what this project is meant to avoid.

**Time needed:** about 30 minutes. **Date your captures.** Fill in the date at the top of each section, because a Best Sellers Rank is only meaningful as a snapshot of a moment.

---

## How to capture

For each URL below, either:
- **Paste text** — select the page, copy, and save it as `inputs/captures/<name>-<YYYY-MM-DD>.txt`, or
- **Screenshot** — save as `inputs/captures/<name>-<YYYY-MM-DD>.png`.

Raw paste is more useful than a tidy summary. I would rather have the mess and extract it myself than have you filter something out.

If a page will not load or shows something different from what I describe, write that down. A blocked or changed page is a real finding, not a failure.

---

## Part 1 — Bestseller lists

Capture date: `__________`

| # | What | URL | Saved as |
|---|---|---|---|
| 1 | Best Sellers, Children's Coloring Books | https://www.amazon.com/Best-Sellers-Childrens-Coloring-Books/zgbs/books/3374 | `bestsellers-childrens-coloring-<date>` |
| 2 | New Releases, same category | https://www.amazon.com/gp/new-releases/books/3374 | `newreleases-childrens-coloring-<date>` |
| 3 | Best Sellers, Children's Activity Books | https://www.amazon.com/Best-Sellers-Books-Childrens-Activity-Books/zgbs/books/3204 | `bestsellers-childrens-activity-<date>` |

Scroll far enough to catch the top 20 in each. The ranking numbers matter, so include them.

## Part 2 — Searches

Capture date: `__________`

| # | Search term | URL | Saved as |
|---|---|---|---|
| 4 | coloring books for kids ages 4-8 | https://www.amazon.com/s?k=coloring+books+for+kids+ages+4-8 | `search-kids-4-8-<date>` |
| 5 | bold and easy coloring book kids | https://www.amazon.com/s?k=bold+and+easy+coloring+book+kids | `search-bold-easy-<date>` |
| 6 | big coloring book for toddlers | https://www.amazon.com/s?k=big+coloring+book+for+toddlers | `search-toddlers-<date>` |

From the search pages I mainly want: which titles keep reappearing, the price spread, and how sponsored versus organic results differ.

## Part 3 — Detail pages for the top 10 to 15 books

Capture date: `__________`

Pick the books that appear repeatedly across Parts 1 and 2. For each, open its detail page and capture the whole thing, including the "Product details" block and the reviews section.

Save as `inputs/captures/book-<short-name>-<date>.txt`.

What I need off each page, though a raw paste gets me all of it:

| Field | Where it is |
|---|---|
| Full title and subtitle | Top of page |
| Author or brand | Under the title |
| Price, paperback | Buy box |
| Best Sellers Rank, all categories listed | Product details block, near the bottom |
| Review count and star average | Under the title |
| Publication date | Product details |
| Page count | Product details |
| Trim size / dimensions | Product details |
| Whether it says single-sided | Description or reviews |

## Part 4 — Complaints, the most valuable part

Capture date: `__________`

For each of your top 10 books, open the reviews and filter to **1, 2 and 3 stars**. There is a "See all reviews" link, then a star filter on the left.

Save as `inputs/captures/reviews-<short-name>-<date>.txt`.

Grab 5 to 10 negative reviews per book, verbatim. Do not summarise them. The exact wording is what tells us what parents actually resent, and phrases repeat across books in a way that summaries hide.

Things I will be counting: bleed-through from double-sided printing, lines that do not meet so colour escapes, designs too detailed for the stated age, thin or faint lines, paper too thin, page count lower than advertised, images repeated inside the same book, and cheap or misleading covers.

---

## Part 5 — Two numbers from KDP, for pricing

Capture date: `__________`

These I genuinely cannot reach, and the third-party sources contradict each other, so I will not price the book off them.

1. Open **https://kdp.amazon.com/en_US/royalty-calculator**
2. Set: marketplace **Amazon.com**, **Paperback**, **Black & white interior with white paper**, trim **8.5 x 11 in**, page count **84**.
3. Write down the **printing cost** it shows: `$__________`
4. Set a list price of **$7.99** and write down the **royalty**: `$__________`

That single printing-cost figure resolves the disputed $0.012 versus $0.015 per page and locks the whole pricing model.

---

## When you are done

Tell me the captures are in `inputs/captures/` and I will build `research/market.md`: one row per book with its source URL and your capture date, a theme ranking, the price spread, and a complaint frequency count. Ranks will be recorded as dated snapshots. I will not convert a rank into a sales estimate, because that conversion is not something anyone outside Amazon can do honestly.
