# OpenClaw Chief Workspace Spec

## Purpose

`workspace-chief` defines KIM Chief Bot, the planning and governance agent for
Kodja Investment Management's AI team.

## Workspace Contract

- `AGENTS.md` owns operating policy.
- `SOUL.md` owns voice and stance.
- `USER.md` owns stable KIM context.
- `TOOLS.md` owns tool and system references.
- `IDENTITY.md` owns display identity.
- `HEARTBEAT.md` owns periodic check-in behavior.
- `MEMORY.md` owns curated durable memory.

## Runtime Contract

Chief should have explicit planner-only tools, KIM Telegram allowlist access, and
role-bound skills. Execution work routes to Engineer.

## Privacy Contract

Workspace docs must not store secrets, raw transcripts, raw Telegram identifiers,
environment-file paths, or auth hints.
