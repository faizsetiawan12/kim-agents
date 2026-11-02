# Runbook: OpenClaw Chief Memory Hygiene

## Goal

Keep Chief memory useful without leaking private KIM context.

## Rules

- Store durable summaries only.
- Do not store raw transcripts, secrets, tokens, raw Telegram identifiers,
  environment-file paths, or auth hints.
- Prefer roles and stable decisions over personal identifiers.
- Remove stale or contradictory memory when policy changes.

## Checks

```bash
openclaw memory status
```
