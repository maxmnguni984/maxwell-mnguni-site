# maxwell-mnguni-site

Portfolio and direct-booking site for Maxwell Mnguni — Vancouver BC model,
athlete, and tugboat deckhand. The site exists to convert a stranger into a
booking enquiry, so treat conversion, load speed, and credibility as the
things that matter.

## Stack

Single hand-written `index.html` (~43 KB) with all CSS and JS inline. No build
step, no framework, no package manager, no dependencies. Deployed on Vercel at
https://maxwell-mnguni.vercel.app/

Preview locally by opening `index.html` in a browser, or:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

Deploy by pushing to the default branch — Vercel builds from the repo.

## Layout of index.html

| Lines (approx) | What |
| --- | --- |
| `<head>` | Meta, OG/Twitter cards, `@font-face`, preloads |
| `<style>` | Every rule. Design tokens live in `:root` |
| `#about` | Bio + `Specifications` table (height, waist, shoe, etc.) + stat counters |
| `#digitals` | Image plates, lightbox |
| `#instagram` | Grid linking out to @maxwellmnguni |
| `#contact` | Booking block — `mailto:` links |
| `<script type="application/ld+json">` | `Person` schema for SEO |
| `<script>` | Preloader, nav, scroll reveal, lightbox, stat counters |

## Assets

Images are `.webp`, fonts are self-hosted `.woff2` (Archivo Black, Instrument
Serif italic, IBM Plex Sans 300/400/500, IBM Plex Mono 400/500). Everything
sits flat in the repo root — no `assets/` directory. `threequarter.webp` is the
hero and the OG image; it is preloaded with `fetchpriority="high"`.
`maxwell-mnguni-compcard.jpg` is the downloadable comp card.

## Design tokens

Defined in `:root`. Use them; never hard-code a hex value.

```
--hull #0D1316   page background      --bone #EFEDE6   text
--tide #18242A   raised surface       --buoy #F0511E   accent, CTAs
--steel #233238  borders/scroll       --fog  #8E9691   muted text
```

Typography: `--display` (Archivo Black, uppercase headings), `--serif`
(Instrument Serif italic, accents inside headings), `--body` (IBM Plex Sans),
`--mono` (IBM Plex Mono, eyebrows and labels). Motion uses `--ease`.

## Conventions

- Keep it one file. Splitting into separate CSS/JS costs a round trip and buys
  nothing at this size.
- No external CDN, no analytics script, no web font from Google — everything is
  self-hosted so the page stays fast and private.
- Every image needs explicit `width`/`height` and, below the fold,
  `loading="lazy"`.
- Sections are revealed on scroll via `IntersectionObserver`. New sections need
  the matching class or they stay invisible.
- Respect `prefers-reduced-motion`.

## Facts that appear in several places at once

Changing any of these means changing them everywhere:

- Booking email `maxmnguni984@gmail.com` — nav CTA, `#contact`, footer, JSON-LD
- Canonical URL and OG URL — swap both if a custom domain is added
- Specs table (Aug 2026): 5'7" / 170 cm, 145 lb / 66 kg, waist 30–32",
  medium shirt, 9.5 US shoe, age 20
- Red Bull Log Drivers 2026 win, field of 128 (`data-to="128"` counter)
- Socials: instagram.com/maxwellmnguni, tiktok.com/@maxwellmnguni

## After any change

Check on a 375px-wide viewport as well as desktop, confirm the preloader still
clears, and confirm the JSON-LD still parses.
