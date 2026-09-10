# kim-agents

Public monorepo of KIM agent workspaces.

## Agents

- `accountant/` — bookkeeping and Sheets reporting.
- `chief/` — governance and routing front door.
- `ops/` — infrastructure, pipelines, Kotrade operations.
- `pm/` — work management (Tasks & Timeline).
- `quant/` — quantitative research and backtest specification.

Shared context: `CONTEXT.md` (domain terms), `PLAYBOOK.md` (roles, authority).

## Setup

```bash
cp .env.example .env   # fill values, never commit .env
```

| Var | Used by |
|---|---|
| `KIM_GOOGLE_SHEETS_KEY_FILE` | accountant Sheets client (path to service-account JSON) |
| `KIM_NOTION_API_KEY` | future Notion consumer |
| `KIM_STOCKBIT_EXODUS_TOKEN` | future market-data consumer |
| `KIM_STOCKBIT_CARINA_TOKEN` | future brokerage consumer |

Convention: `docs/ADR/0001-env-only-credentials.md`.

## What stays local

`memory/`, `migration-backups/`, `.env`, key JSON files — never pushed.
