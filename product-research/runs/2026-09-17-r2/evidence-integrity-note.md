---
run_id: 2026-09-17-r2
date: 2026-09-17
scope: a result that must not be reported as a finding
---
# The bulk hunt's "one survivor" did not survive. It was never tested.

## What the run reported

40 products screened, 9 self-advanced, **1 survived adversarial verification**:
the backyard chicken flock triage kit.

## What actually happened

All three verification lenses on that candidate failed to execute. The
session's WebSearch budget was exhausted — **200 of 200 calls** — before those
agents started, and direct fetching is blocked at the network layer. The agents
reported it themselves, in their own words:

> "TOOLING FAILURE — THIS LENS WAS NOT ACTUALLY RUN. I could not verify a single
> price. Treat this as 'not tested', NOT as 'survived'."

> "INABILITY TO CHECK — NOT CLEARANCE. I performed zero successful IP searches
> this run."

Three lenses, zero external evidence obtained between them. The candidate
"survived" only because the scoring rule counts a low-confidence refutation as
non-fatal, and all three votes were low-confidence **because nothing ran**.

A pipeline that cannot tell "passed a test" from "the test did not execute" will
manufacture a recommendation out of a tooling failure. That is exactly the
failure mode this project exists to avoid, so the result is recorded as
**UNTESTED**, not as a survivor, and the candidate is not carried forward on the
strength of it.

The agents deserve credit for flagging it rather than producing plausible output.

## What the same run did establish, on working searches

The eight candidates killed before the budget ran out were killed on real
evidence, and two of them matter:

- **The grooming shear was independently killed on PRICE FLOOR and on DEMAND AND
  ACQUISITION** by this run, having been rejected separately by the dedicated
  sourcing run. Two hunts, different agents, different queries, same verdict.
- **Every one of the nine advancing candidates that was actually tested failed
  the acquisition lens.** Not the price lens, not IP — acquisition. That is the
  same wall the CPA arithmetic predicts, found empirically.

## Standing evidence limits for this project

1. **No web page has been opened in this session.** Direct fetching is blocked at
   the network layer; `example.com` returns 403 at the CONNECT tunnel, verified
   directly rather than taken on report.
2. **Subagent WebSearch is exhausted** at 200 of 200 calls. Later agents in any
   running workflow may have no research capability at all, so each agent's
   notes must be audited for tooling failures before its output is trusted.
3. The main session retains search capacity, which is now the only research
   channel left.

Anything produced from here without a stated source is a model prior, not a
finding, and must be labelled as such.
