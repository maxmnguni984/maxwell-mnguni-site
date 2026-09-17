# Demand test: measuring buying intent, not interest

**Status: design only. No ads have been run, no page published, no money spent.**

Product-agnostic. Fill in the product once the funnel names one.

---

## The uncomfortable finding first

**$300 cannot buy a reliable estimate of your conversion rate.** About 300 visitors is enough to *kill* a bad idea confidently, and enough to apply a crude pass rule. It is nowhere near enough to distinguish a 1% conversion rate from a 2% one. Anyone promising more from that budget is selling something.

That asymmetry is the whole strategy. **Design the test to kill, and treat any pass as provisional.**

---

## Why a real pre-order, and not the cheaper options

Ranked by what each actually proves.

| Method | Cost | What it proves | How it misleads |
|---|---|---|---|
| **Real pre-order, money taken** | Platform plus ad spend | Genuine willingness to part with money at a stated price. The measured event *is* the thing being forecast | Small sample. Six sales is an honest count but a wide range as a rate |
| Concierge fulfilment of a few orders | Near zero plus goods | Real money *and* real post-purchase satisfaction | Buyers are usually warm contacts. Social obligation contaminates it |
| Selling one unit on a marketplace | Listing fee plus a unit | Real purchase with the platform's trust substituting for your missing brand | The marketplace supplies intent you did not create. Flatters the number |
| Paid ads to a product page | $150 to $300 | Cold-audience cost per action. This is the traffic engine, not the proof | You may be testing your creative rather than your product |
| Fake door, checkout stops at payment | $10 to $50 plus ads | Intent at the moment of payment. Strong relative signal | Systematically overstates. One documented case went from 16.5% click-through to 2.47% conversion, a 6.7x gap |
| Crowdfunding | Weeks of work | Real money at scale | Not cheap or fast. Technology category succeeds about 20% of the time |
| **Waitlist or email capture** | Near zero | That a headline is interesting enough to trade an email for | **Measures curiosity, not intent. See below** |
| Survey, "would you buy this?" | Near zero | Very little | Stated intent overstates behaviour with a measured, published bias |

### The waitlist trap, stated plainly

Published estimates of what fraction of waitlist signups become buyers span **1% to 85%**. That is a factor of 85. It is not a benchmark, it is noise, and no measured study of it for physical consumer goods could be found.

This is precisely the number founders assume. Anyone multiplying "2,000 signups times 20%" has invented the 20%. **Treat a free email signup as worth zero until your own data says otherwise.**

### The intent-behaviour gap is real and measured

This is the best-evidenced material available, and unlike the ecommerce benchmarks it comes from peer-reviewed literature rather than vendors selling conversion software.

- **Sheeran (2002)**, a meta-analysis of 10 meta-analyses covering 422 studies and 82,107 participants: intentions account for **28% of the variance** in behaviour. People translate good intentions into action about **53% of the time**.
- **Webb and Sheeran (2006)**: experimentally changing intentions by a medium-to-large amount produced only a small-to-medium change in behaviour. Intention moves far more easily than behaviour.
- **Murphy et al. (2005)**, Environmental and Resource Economics, meta-analysis of 28 stated-preference studies: the **median ratio of hypothetical to actual willingness-to-pay is 1.35**, with severe positive skew. Notably lower than the folk belief of two to three times, but with a long tail. Their finding that **choice-based elicitation reduces the bias** is the actionable part: make people choose and pay, not rate.
- **Morwitz, Steckel and Gupta**: intentions predict purchase **better for existing products than for new ones**, which is exactly the wrong direction for validating something novel.

A fake-door click is a *weaker* signal than stated intent, because it costs nothing and takes under a second.

---

## The design

**Budget $300, seven days, goal is a defensible go or no-go on a five-figure production run.**

A real pre-order page charging a **refundable deposit**. Not a fake door. Taking actual money is what converts the test from "would you?" into "did you?", and the Murphy result is explicit that real-consequence mechanisms reduce hypothetical bias. A refundable deposit costs you nothing if refunded.

| Item | Cost |
|---|---|
| Cold paid social, US prospecting | $240 |
| Payment page plus domain | $25 to $45 |
| Ad creatives, made yourself | $0 |
| Reserve | ~$15 |

### Traffic maths

Target **about 300 clicks**. Below roughly 250 the test loses its ability to discriminate.

| Channel assumption | $240 buys |
|---|---|
| $0.87 per click, blended ecommerce | ~276 clicks |
| $1.00 per click, TikTok | ~240 clicks |
| $1.72 per click, Meta all-industry | ~140 clicks, too few |

Cross-checked against impression cost: 300 clicks at a 1.5% link click-through needs about 20,000 impressions, costing roughly $183 at TikTok's $9.16 per thousand or about $322 at Meta's US $16.08. **At this budget TikTok is the more viable channel**, with the caveat that its audience skews younger.

Note that platform cost figures come from third-party vendor panels that disagree with each other by two to three times. **Verify with your own first $50 of spend before trusting any of them.**

### Page requirements, because this is where the confound lives

A rough-looking store biases the result **downward**, which makes a false negative more likely than founders expect.

- The **Stanford Web Credibility Project**, 2,684 participants evaluating live sites, found "design look" was the single most-mentioned credibility factor, appearing in **46.1% of comments**, ahead of credentials or accuracy.
- Baymard's checkout research attributes **19% of abandonment to not trusting the site with card details**, and **40% to unexpected extra costs**.

So: real photographs, real price, **shipping cost stated on the page**, an explicit "pre-order, ships [date], fully refundable until we ship", a real business name and contact address, recognised payment buttons, and mobile-first layout since about three quarters of the traffic will be phones. Run three creatives at roughly equal spend so one bad video does not kill a good product.

---

## The decision rule, pre-registered

**Write this down before spending anything.** All probabilities below are exact binomial calculations, verified independently rather than taken from a benchmark.

| Payers at ~300 clicks | Verdict | Basis |
|---|---|---|
| **0** | **Hard kill** | With zero events in 300 trials the true rate is below **0.99%** at 95% confidence. Enough to cancel the order |
| **1 to 2** | **Fail, lean no** | A truly dead product at 0.5% still produces at least one sale **77.8%** of the time and at least two **44.3%** of the time. This is not a signal |
| **3 to 4** | **Inconclusive** | Extend with another $150 to reach ~500 clicks before deciding |
| **5 or more** | **Pass** | Only a **1.8%** chance of reaching this if the product is truly dead, while catching a viable 2% product **71.8%** of the time |
| **9 or more** | **Strong pass** | |

### Why these numbers and not the obvious ones

| Threshold | Passes a dead product (0.5%) | Catches a viable one (2%) |
|---|---|---|
| ≥1 payer | 77.8% | 99.8% |
| ≥2 payers | 44.3% | 98.3% |
| ≥3 payers | 19.1% | 94.0% |
| ≥4 payers | 6.5% | 85.1% |
| **≥5 payers** | **1.8%** | **71.8%** |
| ≥6 payers | 0.4% | 55.6% |

The thresholds founders instinctively use, one or two sales, pass a dead product 78% and 44% of the time. Five is where the false-pass rate collapses without losing too much power. At 500 clicks, seven or more gives a 1.4% false pass and 87% power, which is materially better if the budget stretches.

### The kill power is the real value

With zero events in n trials, the 95% upper bound on the true rate is approximately 3 divided by n.

| Result | True rate is at most |
|---|---|
| 0 of 100 | 2.95% |
| 0 of 200 | 1.49% |
| **0 of 300** | **0.99%** |
| 0 of 500 | 0.60% |

A cheap test is far better at disproving demand than proving it. Three hundred visitors with no purchases rules out any rate at or above 1%, which is enough to cancel a five-figure order.

### Why one sale proves nothing

| Observed | Rate | 95% interval |
|---|---|---|
| 1 of 200 | 0.50% | 0.09% to 2.78% |
| 2 of 200 | 1.00% | 0.27% to 3.57% |
| 6 of 300 | 2.00% | 0.92% to 4.29% |
| 20 of 1000 | 2.00% | 1.30% to 3.07% |

One sale in 200 visitors spans "commercially dead" to "above average". And if the true rate is a hopeless 0.5%, seeing at least one sale in 200 visitors happens **63.3%** of the time. A single sale is the *expected* outcome of a dead product.

---

## Measure the whole funnel, not one number

At 300 clicks you have real statistical power at the higher-base-rate steps even where you lack it at the purchase step.

| Step | Expected rate | What 300 clicks gives you |
|---|---|---|
| Link click-through on the ad | 1% to 2.2% | Whether the concept stops the scroll |
| Reach checkout or add to cart | 4.6% to 6% | **Well powered.** 15 of 300 is 5.0%, interval 3.05% to 8.08%, a real measurement |
| Deposit paid | The live question | Underpowered as a rate, usable as a count |
| Refunds within 14 days | — | Qualitative but vital. High refunds mean the purchase was not real |

**One additional fail condition.** If reach-checkout runs above about 5% but deposits are near zero, people want the product and do not trust *you*. Fix the store and retest. Do not cancel the product.

---

## What a pass does and does not authorise

A pass at 300 clicks gives a confidence interval around 2% of roughly 0.9% to 4.3%. That is not a green light for a full production run.

The correct next step is a **second larger test or a smaller first order**, part-funded by the deposits collected. Concierge fulfilment of those first five to ten orders is the natural follow-on, because it tells you whether the delivered object satisfies before committing to full inventory.

---

## Evidence quality, stated honestly

The ecommerce benchmark space is dominated by content that cites other content. Of roughly 25 sources surfaced, only a handful hold original data: Baymard's cart-abandonment meta-analysis of 50 studies, Unbounce's 41,000 landing pages, IRP Commerce, Statista and Triple Whale's 35,000 stores.

The four peer-reviewed papers on the intent-behaviour gap are by a wide margin the most trustworthy evidence here, but they speak to the gap between intention and action rather than to conversion rates.

**The pass/fail thresholds above therefore rest on statistical calculation anchored to a plausible *range* of conversion rates, not on any single published benchmark.** That is the honest construction given what is actually knowable.

Figures that could not be established at all: waitlist-to-purchase conversion, cold paid-social conversion with disclosed methodology, pre-order conversion from cold traffic, and the quantified penalty for an unfinished-looking store. Each is recorded as unknown rather than filled with a plausible number.
