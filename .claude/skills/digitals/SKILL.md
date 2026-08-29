---
name: digitals
description: Add, swap, or retire photos on the portfolio site and keep it fast. Use when new shots come in, when updating digitals, the hero, the Instagram grid, the comp card, or the specs table.
---

# Updating the site's images and facts

Everything lives in `index.html` and flat files in the repo root. Read
`CLAUDE.md` first for the layout and design tokens.

## Preparing a new image

Source photos are far too large to ship. Convert before committing:

```bash
# Portrait plate for #digitals — 1400px wide is plenty
cwebp -q 82 -resize 1400 0 source.jpg -o newshot.webp

# Square tile for the Instagram grid
cwebp -q 80 -resize 600 600 source.jpg -o newtile.webp
```

Target under 250 KB for a plate, under 90 KB for a tile. Check with
`ls -lh *.webp` and compare against the existing files — if a new one is an
outlier, compress it harder. Name files after what they show
(`frontal`, `physique`, `threequarter`), lowercase, no dates, no spaces.

## Adding it to the page

Copy the markup of an existing plate rather than writing new markup, then:

- Set `src`, and write a real `alt` describing the shot — not "model photo".
- Set explicit `width` and `height` matching the actual pixels, so the layout
  does not shift while it loads.
- Add `loading="lazy"` to anything below the fold. The hero must **not** be
  lazy.
- Confirm the scroll-reveal class is present, or the new plate never appears.
- If it goes in the lightbox, check the caption and that arrow keys still walk
  the full set.

## Changing the hero

`threequarter.webp` is the hero, the OG image, and the preload target. Swapping
it means updating all three: the `<img>`, the `og:image` meta, and the
`<link rel="preload">`. Miss the preload and the largest paint gets slower;
miss the OG tag and every link shared to Instagram or a client shows the old
face.

## Retiring a shot

Delete the file and its markup together. An orphaned `.webp` in the repo is
dead weight; an `<img>` pointing at a deleted file is a broken page.

Keep the digitals set tight. Eight strong frames book more work than twenty
that include three weak ones — cut the weakest whenever a better one lands.

## Comp card

`maxwell-mnguni-compcard.jpg` is linked from the nav, `#about`, `#contact`, and
the footer. Replacing it means keeping the same filename, or updating four
links. Re-export it whenever the specs change, and check it is still legible
printed at 5x7.

## Specs and facts

The `Specifications` table in `#about` is dated ("Aug 2026"). Update the date
whenever a number changes. Height, weight, waist, and shoe get checked on set —
keep them honest. The `data-to="128"` counter and the Red Bull line are load-
bearing credibility; do not round or embellish them.

## Before pushing

- View at 375px and at desktop width
- Confirm the preloader clears and nothing sits invisible
- `python3 -m http.server 8000` and click every lightbox and nav link
- Confirm the JSON-LD block still parses
