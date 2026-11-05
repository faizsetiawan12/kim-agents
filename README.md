# kim-agents

Public monorepo of KIM agent workspaces.

## Agents

- `pm/` — work management (WhatsApp, Notion).
- `ops/` — infrastructure, pipelines, Kotrade operations.
- `growth/` — commercial outreach (idle/standby).
- `accountant/` — frozen reference. Live copy: `~/.hermes/profiles/kim-accountant/` (moved 2026-11-01; see `accountant/MOVED.md`).
- `archive/chief/`, `archive/quant/` — retired workspaces.

Shared context: `GLOSSARY.md` (domain terms), `PLAYBOOK.md` (roles, authority).

Runtime note: deleting an agent through its runtime CLI **prunes the workspace directory** (it moves to `~/.Trash`). Restore tracked files with `git restore --worktree <agent>` and untracked files from Trash.

## Setup

```bash
cp .env.example .env   # fill values, never commit .env
git config core.hooksPath .githooks   # run the PM tests before every commit
```

| Var | Used by |
|---|---|
| `KIM_GOOGLE_SHEETS_KEY_FILE` | accountant (Hermes) Sheets reader (path to service-account JSON) |
| `KIM_LEADS_SHEET_ID` | parked leads reader only — not wired to any agent (`leads/README.md`) |
| `KIM_NOTION_API_KEY` | future Notion consumer |
| `KIM_STOCKBIT_EXODUS_TOKEN` | future market-data consumer |
| `KIM_STOCKBIT_CARINA_TOKEN` | future brokerage consumer |

Convention: `docs/ADR/0001-env-only-credentials.md`.

## What stays local

`memory/`, `migration-backups/`, `.env`, key JSON files — never pushed.
