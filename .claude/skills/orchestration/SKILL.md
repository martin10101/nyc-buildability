---
description: Route for safe parallel / multi-agent orchestration — mechanisms, agent roster, concurrency limits, review independence, sequential integration, and the owner-authority boundary. Use before dispatching agents in parallel or planning a review wave.
---

This is a router, not a copy of the policy. The authoritative document is
`.claude/ORCHESTRATION_POLICY.md`; read it before any parallel or multi-agent execution. It does not
override `CLAUDE.md`, the gates, ADR-005, or an active owner hold.

Key boundaries (full detail lives in the policy — do not restate it elsewhere):
- Describe spawn/message/coordinate/teardown only via the active runtime's current capabilities; never
  hard-code a specific tool name or version.
- Producers write only inside their packet's allowed paths in their own worktree; the six reviewer/
  verifier/auditor roles are operationally read-only and return report content to the orchestrator.
- Only the orchestrator runs `tools/project_control.py`, git, and `gh`, and integrates branches.
- Review at a frozen SHA; producer ≠ reviewer; any commit after review invalidates that review.
- Give each reviewer a small exact packet (task criteria + frozen SHA/diff + named modules/tests) —
  never "read the whole repo"; a lone producer for a single task only duplicates context/tokens.
- Stop and return to the owner before merging, accepting, checkpointing, changing a public contract,
  making a security/policy exception, touching a forbidden path, or releasing/dispatching a held task.
