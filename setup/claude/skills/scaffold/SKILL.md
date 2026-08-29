---
name: scaffold
description: Start a new app or site with a minimal, sane setup instead of a bloated template. Use when starting a new project, creating an app from scratch, setting up a repo, or asked what stack to use.
---

# Starting something new

The first hour decides how the next month feels. Start small — it is easy to
add a dependency later and painful to remove one.

## Pick the smallest thing that works

| What it is | Use |
| --- | --- |
| Landing page, portfolio, one-pager | A single hand-written `index.html`. No build step. |
| Marketing site, a few pages | Astro, or plain HTML if there are fewer than five pages. |
| Interactive app | `npm create vite@latest -- --template react-ts` |
| App with users, data, or auth | Vite + React + Supabase |
| Something that takes payments | Add Stripe. Payment Links first; Checkout when it must be embedded. |

Skip Next.js unless server rendering, route handlers, or its image pipeline
are actually needed. For a client-side app on a static host it is weight
without benefit.

## First commit, before writing features

- `git init`, and a first commit with the empty scaffold so the initial diff
  is readable.
- `.gitignore` covering `node_modules/`, `.env*` (but not `.env.example`),
  `dist/`, `.DS_Store`, `.vercel/`.
- `.env.example` listing every variable name with a comment, no values.
- `README.md` with what it is, how to run it, and how to deploy it. Three
  sections, written before you forget.
- A `CLAUDE.md` recording the decisions made here — stack, hosting, and why —
  so the next session does not re-litigate them.

## Structure

Start flat. `src/` with files in it. Add directories when a directory has an
obvious name and more than three things belong in it, not before. A five-file
project inside `components/atoms/` is somebody's cargo cult.

Name files after what they are. `BookingForm.tsx`, not `Form2.tsx`.

## Set up deployment on day one

Connect the repo to Vercel before there is anything to show. A project that
deploys from the first commit stays deployable; a project that gets its first
deploy in week three spends a day fixing build errors that accumulated
invisibly.

Get a preview URL working, then build features against it.

## Do not

- Add a state management library before there is state to manage.
- Add a testing framework before there is behaviour worth testing — then do
  add one, and test the logic that would cost money if it broke.
- Copy a starter template with forty dependencies. You will not read them, and
  you will inherit every decision the author made for a different project.
- Set up Docker for something that is a static site.
