# Machine setup

This directory configures **Claude Code itself**, not the website in the rest
of this repo. It lives here so it is version-controlled and survives a laptop
rebuild. If it grows, move it to its own repo — nothing here depends on the
site.

## Install

On your own machine, after cloning:

```bash
bash setup/install.sh
```

Then start a new Claude Code session. Verify with `claude doctor`.

Re-running is safe. Anything the script would replace is copied to
`~/.claude/backup-<timestamp>/` first, and an existing `settings.json` is never
overwritten — it is left alone and the new one is written beside it as
`settings.json.new` for you to merge by hand.

## What it installs

| File | Where it lands | What it does |
| --- | --- | --- |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Preferences applied to every project: ship-first posture, stack defaults, deploy rules, how to talk to you. A project's own `CLAUDE.md` overrides it. |
| `claude/settings.json` | `~/.claude/settings.json` | Pre-approves the safe commands that otherwise prompt every session (builds, tests, git reads). Denies force-push, `sudo`, `curl \| sh`, and reading `.env` files or SSH keys. |
| `claude/statusline.sh` | `~/.claude/statusline.sh` | Status line showing directory, git branch with a `*` when dirty, and the model. |
| `claude/skills/scaffold/` | `~/.claude/skills/scaffold/` | Starting a new project without inheriting forty dependencies. |
| `claude/skills/ship/` | `~/.claude/skills/ship/` | Getting an app to a live URL: pre-flight checks, host gotchas, what to verify after, how to read a broken build. |
| `claude/skills/debug/` | `~/.claude/skills/debug/` | Finding the actual cause instead of guessing at fixes, and the shapes common bugs take. |
| `claude/skills/supabase/` | `~/.claude/skills/supabase/` | Postgres, auth, storage: which key goes where, row level security, migrations that survive real data. |
| `claude/skills/stripe/` | `~/.claude/skills/stripe/` | Taking payments without double-charging anyone: server-side pricing, webhook verification, idempotent fulfilment. |

The skills are global, so they load in every project. They cover a project's
whole life: start it, build it, fix it, take money in it, put it live.

Nothing here is specific to the website in the rest of this repo. That site's
own tooling lives in `.claude/skills/` at the repo root and only loads when
working in this repo — it never appears in your other projects.

## Editing

Change the files here, commit, and re-run `install.sh`. Do not edit
`~/.claude/` directly — those edits are not tracked and get overwritten on the
next install.
