# ADR: OpenClaw Chief Governance Boundary

## Status

Accepted

## Decision

KIM Chief Bot is a planner/governor agent. Chief owns agent governance,
workspace documentation, role boundaries, and routing. Engineer owns infrastructure,
runtime operations, coding, builds, and broad tool execution. Future Quant owns
market analysis, signals, strategy, and trading domain work.

Chief must not perform execution work by default. Temporary tool widening
requires explicit founder approval for the specific task.

## Context

The previous Chief workspace duplicated role and channel policy across multiple
docs. Some files said Chief could post in Chat, Trading, or Market Monitor while
others prohibited it. Chief also inherited broad global tool defaults while
being connected to Telegram.

## Consequences

- `AGENTS.md` is the canonical operating policy.
- `SOUL.md`, `USER.md`, and `TOOLS.md` must not redefine operating rules.
- Chief can remain useful in planning and coordination without becoming an
  execution surface.
