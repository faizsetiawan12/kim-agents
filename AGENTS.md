# AGENTS.md — kim-agents

Public monorepo of KIM agent workspaces (Delivery, Sentry, Growth, Accountant;
Chief and Quant archived)
plus shared context. See `CONTEXT.md` for domain terms, `PLAYBOOK.md` for
roles and authority.

## Credentials

Env-only. No exceptions.

- Every secret arrives via `KIM_*` env var — never a hardcoded path, never a
  committed value. Full convention: `docs/ADR/0001-env-only-credentials.md`.
- Local dev: copy `.env.example` to `.env`, fill values, keep it gitignored.
- Missing var → fail fast with the var name. No silent default.
- Never print, copy, commit, or store secret values in docs, memory, Git, or chat.

## Entry Protocol

1. Read the per-agent `AGENTS.md` before changing that agent.
2. Keep agent-specific logic in its folder. Shared rules go here or `PLAYBOOK.md`.
3. `**/memory/` and `migration-backups/` are local-only and never pushed.
