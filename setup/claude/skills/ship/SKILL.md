---
name: ship
description: Take an app from local code to a live URL, and verify it actually works once deployed. Use when asked to deploy, publish, ship, push live, put something on the internet, set up hosting, or fix a broken deployment.
---

# Shipping

A deploy is not done when the CLI prints a URL. It is done when the URL loads
the thing you built. Always finish by opening it.

## Pre-flight

Do all of these before deploying. Each one has cost somebody a bad afternoon:

1. **Build locally first.** `npm run build`, or whatever the project uses. A
   build that fails in CI after a five-minute queue is a build you could have
   failed in ten seconds.
2. **Check the diff for secrets.** `git diff --staged` and look. API keys,
   tokens, `.env` files, connection strings with passwords. A key pushed to a
   public repo is compromised the moment it lands — rotate it, don't just
   delete the commit.
3. **Confirm every environment variable the app reads is set on the host.**
   Missing env vars are the single most common cause of "works locally, blank
   page in production". Grep the source for `process.env` and
   `import.meta.env` and check each name against the host's dashboard.
4. **Check it at 375px wide.** Most traffic is a phone.
5. **Know which environment you are deploying to.** Preview is free to get
   wrong. Production is not — say so before you push to it.

## Deploying

**Vercel** — connect the git repo and let pushes deploy. Pushing a branch gives
a preview URL; the default branch goes to production. Use `vercel --prod` only
for a one-off outside git. Framework detection is usually right, but a static
site with no build step needs the build command left empty rather than set to
something that will fail.

**Netlify** — same shape. Watch the publish directory: `dist` for Vite, `build`
for Create React App, the repo root for a plain HTML site. Pointing it at the
wrong directory produces a 404 that looks like a broken deploy.

**Static with no framework** — no build step. Do not let a host invent one.

## After deploying

1. Load the URL. Not the dashboard's green checkmark — the actual page.
2. Open the browser console and look for errors. A page that renders but
   throws on every interaction is still broken.
3. Click the primary action. The thing the app exists to do.
4. Check one page on a phone-width viewport.
5. Report the real URL.

## When a deploy breaks

Read the build log before changing anything. The first error is the real one;
everything after it is fallout.

- **Blank page, no build error** — almost always a missing environment
  variable, or an asset path that assumed a different base URL.
- **404 on every route but the index** — a client-side router without the
  host's rewrite rule. Add the catch-all.
- **Works locally, fails in CI** — usually case-sensitivity. macOS does not
  care that you imported `./Button` when the file is `button.tsx`; Linux does.
- **Module not found** — a dependency in `devDependencies` that production
  needs, or a lockfile that was not committed.

## Custom domains

Adding a domain is not just DNS. Also update, in the code: the canonical link,
the Open Graph and Twitter `url` and `image` tags, any absolute URLs in
structured data, and the sitemap. Missing these means every link shared
anywhere still points at the old address.

Set up the apex-to-www redirect (or the reverse) so only one of them is
canonical. Wait for the certificate before announcing anything.

## Never

- Deploy to production without saying so first.
- Commit a secret to make a build pass.
- Disable type checking or linting to get green. Fix the error.
- Report a URL you have not loaded.
