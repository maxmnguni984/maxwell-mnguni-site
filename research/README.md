# Dropshipping product research system

Five agents, one coordinator, plain files. Read `RULES.md` and `rubric.md`
first. The plan this implements is summarised in `.claude/skills/research-run/SKILL.md`.

## One-time setup on your machine (Phase 0a)

Nothing here needs an account or a paid tool. The only install is the
Playwright MCP server, which the discovery and competitor agents use for
JavaScript-only pages (Google Trends, Meta Ad Library, TikTok Creative Center).

```
claude --version                      # 2.1.x or newer
claude mcp add playwright npx @playwright/mcp@latest
claude mcp list                       # playwright should show as connected
```

The agent files also declare Playwright inline in their frontmatter, so the
`claude mcp add` step is optional but makes first-run diagnostics easier.

Smoke test before the first pilot (run inside Claude Code in this repo):

1. Ask the `product-discovery` agent to open the Meta Ad Library search page
   and Google Trends for one keyword and report what it sees.
2. WebFetch one Amazon Best Sellers category page and one Shopify store's
   `/products.json`.

Record any failure as a known limitation in the run's `brief.md`.

Note: the Claude Code remote (web) environment used to build this system
blocks most research domains at the network proxy. Run pilots locally, or in
an environment whose network policy is unrestricted.

## Running a research cycle

```
/research-run
```

The lead (main session) creates `runs/<date>-<name>/` from `runs/_template/`,
launches the four worker agents in order, validates every handoff with
`tools/validate.py`, applies `rubric.md`, and writes `report.md`.

## Tools

```
python3 research/tools/unit_econ.py --demo          # worked example
python3 research/tools/unit_econ.py --self-test     # arithmetic check
python3 research/tools/unit_econ.py --input in.json # real run
python3 research/tools/validate.py research/runs/<run>
python3 research/tools/validate.py --self-test
```

Both scripts use only the Python standard library.
