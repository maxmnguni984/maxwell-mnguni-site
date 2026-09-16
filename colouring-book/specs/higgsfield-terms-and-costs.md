# Higgsfield: rights, costs and production risks

Accessed 2026-09-16.

**Access limitation, stated up front:** `higgsfield.ai` is blocked by this session's network egress proxy, so I could not read the Terms of Use or the pricing page myself. Everything about licensing below comes from search-engine summaries of those pages, not from my own read. It is marked `UNVERIFIED` and **you must confirm it in a browser before publishing.** What I could verify directly is your authenticated account through the Higgsfield API.

---

## 1. Commercial rights — the question the whole project rests on

| Finding | Confidence |
|---|---|
| Terms of Use §4.4 reportedly reads: *"Company does not claim ownership of any of your Inputs or Outputs, nor does it restrict your commercial use of Outputs."* | UNVERIFIED, consistent across four independent summaries |
| Rights in exported outputs survive cancellation or account deletion, and may be transferred or sublicensed | UNVERIFIED |
| No tier distinction. Commercial rights flow from the Terms to all users; there is no separate commercial licence to buy. Free, Plus and Ultra differ on watermark and credits, not licensing | UNVERIFIED |
| Print-on-demand and books are not prohibited. The restriction is on commercially exploiting the Service itself, not downstream use of outputs | UNVERIFIED |
| You bear responsibility for outputs not infringing third-party copyright, trademark or likeness. No IP indemnity found | UNVERIFIED |
| Outputs may not be used to train or fine-tune any machine learning model | UNVERIFIED |

Source for all of the above: https://higgsfield.ai/terms-of-use-agreement and https://higgsfield.ai/creator-hub/help-center/account/who-owns-my-generations-and-can-i-use-them-commercially

**Context worth knowing:** a July 2026 Terms update drew public criticism over a perpetual, worldwide, sublicensable licence Higgsfield takes over user content. It was revised effective 2026-08-27 for existing users. Source: https://higgsfield.ai/blog/terms-of-use-privacy-policy-update

**Action before any bulk generation:** open the Terms in a browser, confirm §4.4 verbatim, and save a dated PDF into `specs/`. That dated copy is your evidence of the licence you published under, and it costs five minutes.

### A separate point about copyright, which is not a Higgsfield matter

Under current US Copyright Office practice, purely AI-generated images may not be copyrightable by you. Higgsfield granting you the right to sell an image is a different thing from you owning enforceable copyright in it. Practically: you can publish and sell the book, but your ability to stop someone copying the artwork is limited. This is not a legal opinion, and it does not block the project.

## 2. The watermark risk — the most dangerous item in this document

| Finding | Confidence |
|---|---|
| Free-credit generations carry a Higgsfield watermark. Paid-credit generations are clean | UNVERIFIED |
| There is no toggle. If paid credits run out, generation silently falls back to free credits and re-watermarks the output | UNVERIFIED |
| The Terms reportedly reserve the right to embed machine-readable watermarks, secure metadata, or C2PA provenance signals | UNVERIFIED |

Source: https://higgsfield.ai/creator-hub/help-center/credits-and-usage/watermark-and-how-to-remove

**Why this matters more than anything else here.** A watermark that slips into one page of a 40-page book is not a small defect. It reaches print, it reaches customers, and it triggers returns and one-star reviews. The balance is currently 9.92 credits, which is close enough to zero that a silent fallback is a live possibility rather than a theoretical one.

**Two mitigations, both mandatory in this project:**
1. Top the account up before generating, and never let the balance approach zero mid-batch.
2. Inspect every single generated file for a watermark before it enters `art/final/`. This becomes an explicit item in the page inspection checklist, not an afterthought.

## 3. Credit cost per image — verified on your account

Measured 2026-09-16 with the `get_cost` preflight, which submits no job and spends nothing. Aspect ratio 3:4.

| Model | Setting | Credits |
|---|---|---|
| GPT Image 2 | 4k, high | 11 |
| GPT Image 2 | 4k, low | 0.75 |
| GPT Image 2 | 2k, medium | 2 |
| GPT Image 2.5 | 4k, high | 4.5 |
| **GPT Image 2.5** | **4k, medium** | **2** |
| GPT Image 2.5 | 2k, medium | 1.5 |
| Cinema Studio Image 2.5 | 4k | 4 |
| Cinema Studio Image 2.5 | 2k | 2 |

Cost scales with both resolution and quality, and varies enormously between models. GPT Image 2.5 at 4k medium is the working choice at 2 credits per page, with GPT Image 2 at 4k low as a cheaper candidate the sample batch will test.

**Account state, verified:** plan tier `plus`, balance **9.92 credits**, `unlim.available: false`.

**Credit price in dollars: UNKNOWN.** Higgsfield's own `show_plans_and_credits` endpoint is currently returning a server-side schema validation error, so I could not pull authoritative pricing from the API, and the pricing page is blocked. Third-party figures for the Plus plan range from $39 to $59 per month and disagree on included credits. **I will not convert credits to dollars off a disputed number.** You can read the real figure from your account billing page in one look.

Note on "unlimited": it reportedly waives credit cost only for selected models on the Higgsfield web interface. Requests through the API, which is how this project generates, deduct credits at normal rates regardless. Your account shows unlimited unavailable in any case.

## 4. Third-party model policies stack

The Terms reportedly state that where a feature is powered by a third-party model provider, that provider's acceptable-use policies apply in addition, and **where those policies are more restrictive, the more restrictive policies win** (UNVERIFIED, same Terms URL).

GPT Image 2 and 2.5 are OpenAI models routed through Higgsfield, so OpenAI's usage policies stack on top. No commercial prohibition was found in either, but this is the real risk surface for a printed product and it is worth knowing which rules govern before committing 40 pages to one model.

## 5. Output resolution — needs measurement before the trim size is locked

| Finding | Confidence |
|---|---|
| GPT Image 2 and 2.5, Cinema Studio 2.5 and Nano Banana Pro support a 4k setting | VERIFIED, model catalog |
| Higgsfield Soul 2.0 caps at 2k and is unsuitable for print at this size | VERIFIED, model catalog |
| GPT Image 2's documented 4K sizes are 3840x2160 and 2160x3840, and OpenAI treats anything above 2560x1440 as experimental | UNVERIFIED, https://yingtu.ai/en/blog/gpt-image-2-4k-image-generation |
| Actual delivered pixels at 4k, 3:4 | **UNKNOWN — requires one real generation to measure** |

**Why this is a real risk.** Our art box is 7.5 x 10 in, which needs **2250 x 3000 px** at KDP's 300 DPI minimum. If a 4k 3:4 render arrives at roughly 2880 x 3840 we are comfortable. If it arrives at roughly 2160 x 2880 we are just under, and the options become a slightly smaller art box of about 7.2 x 9.6 in, or upscaling.

**Upscaler available on your account, verified:** `bytedance_image_upscale`, targets 2k or 4k. The Topaz upscalers described in some sources are not in this account's image catalog. The upscale path costs extra credits per page and will be priced before use.

The very first item in the sample batch is therefore to **measure the actual pixel dimensions of one generated file**, before anything else is decided.

## 6. Disclosure and attribution

No Higgsfield requirement to attribute Higgsfield or disclose AI use when publishing commercially was found. That is absence of evidence on a blocked page, not confirmation. It is in any case moot for KDP, which requires AI-generated content to be declared regardless of what the image tool asks for.

---

## Open items carried into the build

1. Confirm Terms §4.4 in a browser, save a dated PDF into `specs/`. **Blocking for bulk generation.**
2. Read the credit price from the account billing page. **Blocking for the top-up.**
3. Measure real pixel output at 4k, 3:4. **Blocking for locking the art box.**
4. Watermark check on every generated file, permanently, as a checklist item.
