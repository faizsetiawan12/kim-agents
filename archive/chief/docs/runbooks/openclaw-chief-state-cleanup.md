# Runbook: OpenClaw Chief State Cleanup

## Goal

Resolve stale local OpenClaw state without deleting ambiguous data first.

## Procedure

1. Back up `~/.openclaw`.
2. Run `openclaw doctor`.
3. Review doctor warnings for orphan agent directories, missing transcripts, and
   heartbeat-owned sessions.
4. Run any available cleanup command in dry-run mode first.
5. Archive ambiguous state before deletion.
6. Re-run `openclaw doctor`.

## Acceptance

Doctor no longer reports stale `main` agent state, missing Chief transcripts, or
a heartbeat-owned `agent:chief:main` session.
