# KIM Sentry

Infrastructure reliability and operational recovery across KIM. Products own their processing and correctness checks. KATMA-specific integration is deferred.

## Runtime
Hermes profile: `~/.hermes/profiles/sentry/`. Its `SOUL.md` and `skills/sentry-repair/SKILL.md` define the approved repair workflow. Private memory stays in that profile; job history and repair budgets live in its runtime database.

## Boundaries
- Code generates scheduled reports, status, arithmetic, incident state and notifications; scheduled delivery bypasses models.
- AI interprets requests, investigates failures and develops repairs.
- Every code repair uses a NEW worktree and an incident issue, with tests and independent Standards/Spec reviews before PR merge.
- Reversible operational merge/deployment and verified rollback are preauthorized. Trading decisions/orders, credential changes, permanent deletion and spending require approval.
- Two unsuccessful AI attempts per incident; the supervisor owns this persisted budget. Preserve other worktrees and other profiles.

## Context
Read `../PLAYBOOK.md` for KIM roles, `../../AGENTS.md` for product boundaries, and `~/.claude/rules/agent-architecture.md` for output/memory rules. The user's newer explicit approval boundaries override older shared playbook authority.
