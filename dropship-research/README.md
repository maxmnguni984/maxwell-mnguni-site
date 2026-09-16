# Dropship product research team (5 agents, Claude Code)

A file-based, auditable research system. Run `claude` **from this folder** so `.claude/agents` and `.claude/skills` load.

## Run a research batch
```
claude                       # inside dropship-research/
/research-lead 2026-09-16-r1 # Lead executes Steps 0-6 from .claude/skills/research-lead/SKILL.md
python3 scripts/validate.py --check-urls   # after the run
```
Outputs land in `runs/<run-id>/shortlist.md` and `data/products/<id>/verdict.md`. Approval asks land in `approvals/requests.md`.

## First-time setup (Phase 0.5, nothing paid, no accounts)
1. Python 3.8+ and git. No packages needed (`scripts/` are stdlib-only).
2. Run the source-reachability check described in `runs/_setup/source-check.md` and fill in the table.
3. Optional, inspected third-party skill for review mining (MIT):
   `git clone --depth 1 https://github.com/coreyhaines31/marketingskills /tmp/ms && cp -r /tmp/ms/skills/customer-research .claude/skills/`
   Re-read `.claude/skills/customer-research/SKILL.md` after copying; it has no scripts or network calls as of 2026-09-16.
4. Optional, later (Phase 4): Playwright MCP for public JS pages, Lead-only: `claude mcp add playwright npx @playwright/mcp@latest`. Do not give it to subagents.

## Manual inputs
Pages that block fetching (Amazon, AliExpress, TikTok Creative Center, Meta Ad Library) go through `inputs/` as pasted text or screenshots. See `inputs/README.md`.

## Folder map
See `CLAUDE.md`.

## Verifying evidence URLs
`python3 scripts/validate.py --check-urls` resolves every cited URL. A URL that returns 404/410 is an **error** (a dead or wrong citation). A URL the machine cannot reach at all because outbound HTTPS is proxied or blocked is a **warning**, so a sandboxed run never misreads a network block as a fabricated source. Run the URL check from a machine with open outbound HTTPS before trusting a clean result.

## Worked example
`templates/examples/econ-inputs.example.yaml` plus `economics-calc.example.md` show the calculator's input shape and output. The base case there was hand-checked to the cent on 2026-09-16: net price 30.60, goods 10.60, payment fee 1.19, refund loss 2.06, chargeback loss 0.28, contribution 16.47 (53.8%), break-even ROAS 1.86, 7 orders to recover a 100 USD test.
