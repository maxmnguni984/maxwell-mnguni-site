# Prompt template

Every page uses this template unchanged except for the `{SUBJECT}` slot and the
`{COMPOSITION}` slot. Building prompts any other way is how style drift gets
into a book.

## Template

```
Black and white line art for an adult colouring book page.

Subject: {SUBJECT}

Composition: {COMPOSITION}

Style: clean vector-like ink outlines, uniform line weight throughout, pure
black lines on a pure white background. Every shape is fully enclosed by an
unbroken outline so it can be filled with colour. Medium detail: between 25 and
50 distinct colourable regions, each large enough to fill with a pencil. Decorative
pattern work is drawn as outlined shapes, never as solid fill or texture.

The image is centred with a clear white margin on all four sides. Nothing
touches or crosses the edge of the image.

Absolutely no: shading, greyscale, hatching, cross-hatching, stippling,
gradients, drop shadows, solid black fills, colour of any kind, photographic
realism, three-dimensional rendering, text, lettering, numbers, signatures,
watermarks, logos, borders that touch the image edge, sketchy or broken lines,
double lines, or open unclosed outlines.
```

## Slot guidance

**`{SUBJECT}`** names what is drawn, generically. It describes a thing, not a
style borrowed from a person or a book.

- Good: "a barn owl perched on a flowering dogwood branch, its wing feathers
  filled with concentric teardrop patterns"
- Bad: "an owl in the style of [artist]" — never name a living artist
- Bad: "like the owl on the cover of [title]" — never reference a competing book

**`{COMPOSITION}`** fixes the layout so pages vary in subject without varying in
feel. Pick one per page and rotate them across the book:

- "the subject centred, filling most of the frame, on a plain white background"
- "the subject centred within a circular mandala of radial geometric pattern"
- "the subject centred inside a rectangular decorative border of repeating
  botanical motifs"
- "the subject arranged as a symmetrical radial mandala, its forms repeating
  eight times around the centre"

## Rules that bind every prompt

- No copyrighted or trademarked character, franchise, brand, logo or mascot.
- No living artist named, and no competing title or series referenced.
- No real person's likeness.
- Subjects are common natural and geometric forms, which are not ownable.

## Page log

Every generated page is recorded in `kdp/pages/page-log.csv` with its page
number, subject, composition, the exact prompt, the model settings, the job ID,
the credit cost, and the QA verdict. That log is what makes a regeneration
reproducible and the spend auditable.
