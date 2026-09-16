# Market research: adult nature and mandala colouring books

Status: **NOT STARTED** — blocked. See "Access limitation" below.

Marketplace: Amazon.com (US). Format studied: paperback, 8.5 x 11 and nearby
trims. Date range of observations: (fill when collected.)

## Access limitation

`amazon.com` and `kdp.amazon.com` are refused by this environment's network
proxy at the CONNECT layer (HTTP 403), verified by direct request. WebFetch,
curl and a headless browser fail identically, so no Amazon page can be read
from this session. This file stays empty rather than being filled from memory.

Resolve by one of: running the session locally; setting the environment's
network policy to unrestricted; or the owner pasting listing pages in, recorded
with the date and the owner named as the source.

## How rows are recorded

One row per competing book in `competitors.csv`. Rules:

- `url` and `accessed` are mandatory. A row without both is not a fact.
- `bsr_value` is stored with `bsr_category` and `bsr_captured_at`. A Best
  Sellers Rank is a snapshot of position at a moment. It is **not** a sales
  figure and is never converted into units sold or revenue.
- `review_count` and `avg_rating` are read from the page, not estimated.
- `source_type` is `listing` (read directly), `search` (from a results page) or
  `owner_supplied` (pasted in by the owner, who is then the cited source).

## Sections to complete

1. **Price distribution** — observed list prices by page count and trim.
2. **Page counts and structure** — single- or double-sided, blank reverse,
   front matter, design count.
3. **Themes present** — what subjects are saturated, what is thin.
4. **Complaints** — quoted from one- and two-star reviews, with the review URL
   and date. Expected recurring themes in this category, to be confirmed or
   refuted by evidence rather than assumed: marker bleed-through, designs lost
   in the gutter, lines too thin, double-sided printing, and malformed
   AI-generated anatomy.
5. **Gap analysis** — intersections of subject, difficulty and format with
   visible demand and thin or poorly executed supply.
6. **Unknowns** — what could not be determined and why.
