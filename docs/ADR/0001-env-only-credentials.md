# ADR-0001: Env-Only Credentials

**Status:** Accepted
**Date:** 2026-09-10
**Scope:** `kim-agents` public monorepo

## Context

Agent scripts loaded secrets inconsistently: hardcoded absolute host paths
(e.g. `/home/faiz/.config/...`) alongside prose-only references, with no
shared convention and no `.env` support. Hardcoded paths break on any other
machine. Committed secrets would leak on a public repo. Token values were
found in `pm/memory/` chat logs — proof that anything outside `.gitignore`
eventually leaks.

## Decision

1. **Env-only.** Every secret reaches code via environment variable. Never a
   hardcoded path, never a committed value.
2. **Shared `KIM_` prefix.** All vars start with `KIM_` so ownership is
   obvious and collisions are cheap to avoid.
3. **Stdlib `.env` loader.** One 5-line `_load_dotenv()` per script, no
   `python-dotenv` dependency. Local dev drops a `.env` next to the repo
   root; production exports real env vars. Loader never overrides an already
   exported var (`setdefault` semantics).
4. **File-path vars for key files, not inline JSON.** `KIM_GOOGLE_SHEETS_KEY_FILE`
   points at a local JSON path. Keeps `.env` small and keeps key rotation a
   file swap.

Canonical vars:

| Var | Consumer | Notes |
|---|---|---|
| `KIM_GOOGLE_SHEETS_KEY_FILE` | `accountant/scripts/google_sheets.py` | Path to service-account JSON, never the JSON itself |
| `KIM_NOTION_API_KEY` | future | Documented, no consumer yet |
| `KIM_STOCKBIT_EXODUS_TOKEN` | future | Market-data layer, documented only |
| `KIM_STOCKBIT_CARINA_TOKEN` | future | Brokerage layer, ~8h TTL, documented only |

## Consequences

- `accountant` and `quant` scripts fail fast with the missing var name when
  unset — no traceback leak, no silent default.
- `.env.example` lists all five vars with placeholder values; real `.env`
  stays gitignored and local-only.
- `**/memory/`, `migration-backups/`, `*.pem`, `*credentials*.json` stay
  excluded from the public tree — chat logs already contained live bot
  tokens once.
- Upgrade path: past ~10 vars or team rotation needs, move to
  `python-dotenv` + a secret manager. `ponytail:` comment in each loader
  marks this ceiling.
