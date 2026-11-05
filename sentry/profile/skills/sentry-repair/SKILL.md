---
name: sentry-repair
description: Mandatory workflow for KIM Sentry incident repair and operational code changes.
---
Read the incident and affected repository instructions. Load and follow these skills explicitly:
1. diagnosing-bugs: reproduce the exact failure before proposing a cause.
2. implement and tdd: use an isolated NEW git worktree for every code repair. The user preapproves selecting tests at existing public interfaces. Ask only if expected product behavior is unclear.
3. code-review: pin the original base commit; give two independent reviewers the full diff and incident requirements. One reviews Standards, one Spec. Resolve blockers.
4. file-pr: open the repair PR, reference its incident issue.
5. babysit-pr: handle verified findings and CI failures. Stop after repeated unrelated infrastructure failure.
The user explicitly permits automatic merge and deployment for reversible operational repairs after tests and both reviews pass. This overrides babysit-pr's ask-before-merge default. Verify actual recovery and roll back if verification fails. Establish the rollback before deploying. Never infer live readiness from tests alone.
Require approval for trading decisions/orders, credential changes, permanent data deletion, or spending. Preserve every other active worktree. KATMA and kim-data integration are deferred to another session.
Create one GitHub incident issue per code-repair incident and reuse it for retries. Existing incident id belongs in every repair artifact. Persist evidence as issue/PR links, commit ids, test commands and actual outcomes. Do not claim success without application-level verification.
At most two unsuccessful AI repair attempts per incident, enforced by the supervisor. Read /health for the budget; never reset it yourself. Use /pause_repairs when the user asks to stop automatic repairs.
Do not execute retro, ask-matt, to-spec, or to-tickets. Do not change installed skills automatically. Scheduled cards/status are code-generated, never reformatted by a model.

A supervisor-provided evidence.approval grants only its recorded scope for that incident. Preserve its limits. The owner can record this with /approve_repair <incident ID> <exact action>; a fresh two-attempt budget requires the explicit new-budget option.
