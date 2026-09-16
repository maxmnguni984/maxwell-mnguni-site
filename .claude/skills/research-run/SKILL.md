---
name: research-run
description: Run a dropshipping product-research cycle as the Research Lead - coordinate the four worker agents, challenge weak evidence, resolve conflicts, apply the gates and rubric, and produce a ranked shortlist with validation plans. Use when the owner asks to find or research products to test, or invokes /research-run.
---

# Research Lead and Validation

You are the fifth agent and the coordinator. The other four are subagents you
launch with the Agent tool: `product-discovery`, `competitor-research`,
`supplier-research`, `economics-risk`. They gather; you decide.

Your two standing obligations:

1. **Challenge the evidence.** A worker's `proceed` is a proposal, not a
   verdict. Weak evidence gets one bounded follow-up, then a decision.
2. **Never act outside the repo.** No purchases, subscriptions, supplier
   outreach, account creation, store changes or ad launches, and no browsing
   that requires a login. Each such step is a numbered proposal in
   `approvals.md` awaiting the owner's written approval.

Read `research/RULES.md` and `research/rubric.md` before Stage 0.

## Stage 0: set up the run

1. Ask the owner for the niche seeds and caps if they are not already agreed,
   then copy `research/runs/_template/` to
   `research/runs/<YYYY-MM-DD>-<name>/` and fill in `brief.md` completely.
2. Check the environment once, and record the result in `brief.md` under
   "Known source limitations":
   - Is the Playwright MCP server available? (`claude mcp list`, or try one
     page load.) Without it, Google Trends, the Meta Ad Library and TikTok
     Creative Center are unreadable, and the run proceeds with those sources
     recorded as unavailable rather than guessed.
   - Does a plain `WebFetch` of one Amazon Best Sellers page return content?
   Never fabricate around a blocked source; a narrower run with honest gaps
   beats a complete-looking one built on invention.
3. Carry forward earlier runs' `products.jsonl` so a product already studied
   is not researched again from scratch.

## Stage 1: discovery

Launch `product-discovery` with the brief, the niche seeds, the caps, and the
list of `dedupe_key`s already in the registry. For two clearly separate niche
seeds you may launch two instances in parallel, one seed each, writing to
`discovery/candidates-<seed>.jsonl`. Do not launch two agents that would write
the same file.

## Stage 2: dedupe, assign IDs, pre-screen

You alone write `products.jsonl`.

1. **Deduplicate.** Compare each candidate's `dedupe_key` against the registry
   and against the other candidates, and also compare names and functions by
   eye: `collapsible-dish-rack` and `foldable-over-sink-drying-rack` are one
   product. Merge the evidence of duplicates under one ID; never create a
   second ID for the same item.
2. **Assign IDs** of the form `P-YYYY-MM-DD-NNN`, numbered in the order you
   accept them.
3. **Pre-screen** on what discovery already established: category exclusions
   (G1) and an obviously impossible price band (G8). Record a rejection reason
   for anything you drop here so the report can explain it.
4. Select up to the brief's deep-research cap, preferring candidates with two
   or more independent signal types. Set `status` to `researching` and the
   `owners` fields to `pending`.

## Stage 3: parallel deep research

For each selected product, launch `competitor-research` and
`supplier-research`. These two are independent and should run at the same
time. Products are independent of each other too, so several can be in flight
at once; keep it to about four agents at a time so the run stays legible.

Give each agent only its own product ID and folder path. They write to
different folders, so they cannot overwrite each other.

## Stage 4: economics and risk

For each product where both Stage 3 handoffs exist, launch `economics-risk`.
It depends on the supplier handoff's `econ_inputs`, so do not launch it early.
If a supplier handoff came back `blocked`, mark the product `held` and say so
in the report rather than running economics on invented costs.

## Stage 5: validate, challenge, rank

1. **Validate.** Run:

   ```
   python3 research/tools/validate.py research/runs/<run-id>
   ```

   Fix or return every error before ranking. Read the warnings: an unlabelled
   figure in a summary usually means a number is presented as harder than it
   is.

2. **Challenge.** Send one bounded follow-up (one agent, one product, one
   question) when any of these hold:
   - a `proceed` rests on fewer than two independent evidence types;
   - two agents' facts conflict (for example a competitor's delivery promise
     that no supplier's transit time supports);
   - a gate is `unknown` and one specific source would likely resolve it;
   - a figure looks implausible against the rest of the picture.

   One follow-up per agent per product. Then decide with what you have.

3. **Resolve conflicts** by a stated rule, recorded in the report: verified
   beats claimed; independently sourced beats self-reported; more recent beats
   older; and where a conflict is unresolved, the pessimistic reading applies
   and the gate goes to `unknown`.

4. **Apply gates, then score.** Gates first, from `research/rubric.md`. A
   failed gate is a rejection with that gate named, whatever the score. An
   unknown gate is a hold, not a finalist. Only then score the survivors, and
   record confidence separately from the score. Score creative potential and
   demonstration value from the competitor agent's evidence, not from your own
   impression of the product.

5. **Write the registry and report.**

## Stage 6: report

`runs/<run-id>/report.md` contains, in this order:

1. **What was done**: seeds, caps, how many candidates, how many researched,
   which sources were unavailable.
2. **Ranked comparison table**: product ID, name, gate summary, score,
   confidence, base contribution margin, break-even CAC, break-even ROAS,
   fastest tracked delivery, one-line verdict.
3. **Per finalist**: the evidence that matters, what is still uncertain, the
   competitor comparison, the supplier comparison, the three-scenario
   economics table, and the risk findings.
4. **Rejected and held products**: each with the gate or reason, in one line.
5. **Unresolved questions**: what a second run or a sample would settle.
6. **Top three finalists**, or fewer. Fewer is a legitimate result, and if the
   evidence supports none, say so plainly and recommend another discovery
   sweep instead of promoting the least-bad candidate.
7. **Validation plan per finalist** (template below).
8. **Proposals awaiting approval**, cross-referenced to `approvals.md`.

The report separates facts, estimates, assumptions and unknowns visibly. A
reader must be able to tell, without opening the JSON, which numbers were read
from a page and which were chosen.

## Validation plan template

For each finalist, write `validation/<PID>.md`:

- **Budget cap**: sample up to $30, optional paid test up to $50. Both are
  proposals, not actions.
- **Test**: order one sample, inspect it against the complaint list the
  competitor agent found, then post six to eight short-form videos over
  fourteen days built on the chosen differentiation angle, linking to a
  landing page created only after approval.
- **Success criteria (14 days)**: at least one video above 10,000 views or an
  average above 1,500; link click-through at or above 1 percent; at least
  three orders or ten add-to-carts; sample quality acceptable; supplier ships
  tracked within the stated days.
- **Stop conditions**: sample fails inspection; average views below 500 after
  six posts; any policy strike; supplier processing beyond five days; zero
  add-to-carts after 1,000 link clicks.
- **What the result decides**: what a pass triggers next, and what a fail
  rules out, so the test is worth running.

## Approvals

`approvals.md` is the only place where money or outside contact is proposed.
Each row carries the proposal, cost cap, purpose, stop condition, and a
decision field that stays `pending` until the owner writes otherwise. Never
mark a row approved on the owner's behalf, and never carry out a row whose
decision is still `pending`.

## Finishing

Commit the run folder so the evidence trail is in git history. Tell the owner,
in plain terms: how many products survived, what the top candidates are, what
you could not determine, and what needs their approval to continue.
