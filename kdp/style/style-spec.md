# Style specification

Fixed once, reused verbatim on every page, so the book reads as one book rather
than forty unrelated images. Changing anything here after the sample gate means
regenerating everything, so it is settled at Gate 2 and then frozen.

## Visual rules

| Property | Requirement | Why |
|---|---|---|
| Colour | Pure black on pure white only | Anything else prints grey and cannot be coloured over |
| Shading | None: no hatching, stippling, gradients, drop shadows or fills | Grey areas are the single most common complaint about AI colouring books |
| Stroke weight | Uniform, about 8 to 14 px at 4k (roughly 0.6 to 1.1 mm printed) | Thin lines disappear in print and defeat older eyes |
| Closure | Every region fully enclosed | Open outlines leak on digital fill and look wrong with markers |
| Detail | 25 to 50 fillable regions per page | The medium-detail band the audience asked for |
| Smallest region | No narrower than about 4 mm printed (47 px at 300 DPI) | Below that it cannot be coloured with a pencil, let alone a marker |
| Composition | Subject centred, white margin inside the image edge | Keeps art clear of the page margin and the gutter |
| Edges | Nothing touches or crosses the image border | Keeps the interior a no-bleed file |
| Text | None anywhere in the image | Page titles are typeset, not generated |

## Generation settings

Frozen after the probe round:

| Setting | Value |
|---|---|
| Model | `gpt_image_2_5` |
| Aspect ratio | `3:4` (matches the 7.125 x 9.5 in placement exactly) |
| Resolution | `4k` |
| Quality | `high` |
| Background | `opaque` |
| Cost | 4.5 credits per image, preflighted |

Probes only: `2k` / `medium` at 1.5 credits. Probe output is never printed; it
exists to choose a treatment cheaply.

## The three treatments to probe

One subject, three readings, so the choice is made on evidence rather than
taste in the abstract:

1. **Botanical-led.** Realistic plant and animal forms, with pattern used as
   fill inside the shapes.
2. **Mandala-led.** Radial symmetry dominant, the animal or plant emerging from
   the geometry.
3. **Panel.** A clean subject centred inside a decorative geometric border.

## Known failure modes

Checked on every page. The first six are caught mechanically by
`kdp/tools/qa_pages.py`; the rest need eyes.

Mechanical:
- Grey or anti-aliased mid-tones beyond the edge-softening threshold
- Ink coverage outside the expected band (a near-empty or near-black page)
- Regions left open, found by flood-filling from the border
- Regions too small to colour
- Resolution below 300 DPI at placed size
- Near-duplicate pages, by perceptual hash

By eye:
- Animal anatomy: leg and eye counts, joints that bend the wrong way, paws and
  hooves that dissolve
- Symmetry that is almost but not quite right, which reads as a mistake
- Areas of noise masquerading as detail
- Compositions that are simply unpleasant to colour
