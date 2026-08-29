---
name: debug
description: Track down why an app is broken instead of guessing at fixes. Use when something errors, crashes, hangs, returns the wrong result, works locally but not in production, or worked yesterday and does not today.
---

# Debugging

Most time lost to a bug is lost to fixing the wrong thing confidently. The way
out is to find the smallest reliable reproduction, then read what is actually
happening rather than assuming.

## Order of operations

1. **Reproduce it.** If you cannot make it happen on demand, you cannot know
   you fixed it. A bug that "sometimes" happens needs the condition found
   first — different data, a race, a cold cache, a specific browser.
2. **Read the actual error.** The whole thing, including the stack trace, and
   the *first* error rather than the last. Everything after the first is
   usually fallout. In a browser, open the console and the network tab — a
   failed request is invisible in the UI.
3. **Find the last version that worked.** `git log`, and `git bisect` when the
   window is wide. Knowing the commit that broke it usually means knowing the
   bug.
4. **Narrow it.** Delete or stub half of what runs until the bug disappears,
   then put half back. A bug in 3000 lines is hard; the same bug in 20 lines
   is obvious.
5. **Verify the assumption.** Print or log the value you are certain about.
   The bug lives in the thing you did not bother to check — the shape of the
   API response, whether the env var is actually set, whether the function ran
   at all.

## Only then, fix it

Understand the mechanism before changing code. If you cannot explain why the
bug happens, you cannot know your change fixes it rather than hiding it. Then
re-run the reproduction from step 1 and watch it pass.

## Common shapes

- **Works locally, breaks in production** — an environment difference. Missing
  env var, a `devDependency` production needs, filesystem case-sensitivity
  (Linux cares, macOS does not), or a hard-coded `localhost`.
- **Undefined is not a function / cannot read property of undefined** — async
  ordering. Something is read before it arrives. Follow the value backward to
  where it should have been set.
- **Worked yesterday, nobody changed anything** — something did change: a
  dependency resolved to a new version because the lockfile is not committed,
  an upstream API, an expired token, or a certificate.
- **Fixed it but it still fails** — you are not running what you think.
  Cached build, stale dev server, service worker, browser cache, or a deploy
  that did not land. Hard-reload and confirm the deployed commit hash.
- **Intermittent** — a race, or shared state between things that should be
  independent. Tests that fail only in CI usually run in a different order or
  in parallel.
- **Silent wrong answer** — worse than a crash. Add an assertion at the
  boundary where the data first goes wrong.

## Do not

- Change several things at once. Then you do not know which one mattered.
- Add a `try/catch` that swallows the error to make it go away. That converts
  a loud bug into a silent one.
- Bump a dependency and hope.
- Call something a flake without evidence. "Intermittent" is a symptom, not a
  cause.
- Declare it fixed without re-running the reproduction.
