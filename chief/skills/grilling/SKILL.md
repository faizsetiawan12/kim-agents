---
name: grilling
description: |
  Relentless round-based interrogation using a decision-tree frontier to stress-test a plan, decision, or idea.
---

# Grilling

Interview the user relentlessly using a decision-tree model until reaching a shared understanding.

## Operating Principles

- Map all decisions as a **decision tree** where each node represents a choice.
- Work the tree in **rounds**. The **frontier** contains every decision whose prerequisites are settled.
- Ask the complete frontier in each round, formatting questions with Q1, Q2, etc., along with a recommended answer (`➡️`).
- Discover facts yourself using available tools and repo inspection; do not ask the user for factual data you can look up.
- The session concludes when the frontier is empty and the user approves the converged premises.

Refer to `grill-me` for full phase details and design review workflow.
