# Global preferences

These apply to every project unless a project's own CLAUDE.md says otherwise.
A project-level file always wins.

## Default posture

I build and publish small apps and sites. The goal of almost every session is
a working thing at a real URL, not a design document. Bias toward shipping:
get something deployed early and improve it in place, rather than polishing
locally for hours before anyone can see it.

When I ask for an app, assume I want it live. Ask about hosting once, then
remember the answer for that project by writing it into the project's
CLAUDE.md.

## Stack defaults

Reach for the simplest thing that survives contact with real users:

- **Static site or landing page** — hand-written HTML/CSS, no build step. It
  loads instantly and never breaks in two years.
- **Interactive app** — Vite + React + TypeScript. Tailwind if the design is
  conventional, plain CSS with custom properties if it is not.
- **Needs a backend** — Supabase. Postgres, auth, and storage without running
  a server.
- **Needs payments** — Stripe. Payment Links for anything simple; Checkout
  when it needs to be embedded.
- **Hosting** — Vercel by default.

Do not add a framework, a state library, an ORM, or a component library
without a reason you can say out loud. "It might scale" is not a reason.

## Code

- TypeScript over JavaScript for anything with more than one file.
- Handle the error case. A `catch` that only logs is not handling it — decide
  what the user sees.
- No secrets in the repo, ever. Environment variables, and a `.env.example`
  that documents the names without the values.
- Write the comment when the code is doing something non-obvious. Skip it when
  the code already says it.
- Match the file you are editing. Its conventions beat mine.

## Before telling me something works

Run it. A change that has not been executed is a guess. For a UI change, load
the page; for an API, call it; for a build, build it. If you could not run it,
say so plainly instead of hedging.

If tests fail, show me the output. Do not summarize a failure as "minor".

## Publishing

Never deploy to production without saying so first. Preview deploys are fine
unprompted.

Before any production deploy, confirm: the build passes, no secrets are in the
diff, and the page works at 375px wide. Say what the URL will be.

## Git

- Never commit to `main` directly. Branch first.
- Commit messages: a subject line that says what changed and why, and a body
  when the reason is not obvious. No emoji.
- Do not push unless I ask.

## Talking to me

Lead with the answer. Skip the preamble and the recap of what I just asked.
If you are stuck, say what you tried and what you need. If I am wrong about
something technical, say so directly — I would rather hear it now than debug
it later.
