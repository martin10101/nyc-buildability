# M0-T090 — G0 readiness (administrative)

**Task:** D-024 C1: bounded subagent contracts + structural workload sizing
**Recorded by:** orchestrator (administrative gate class) · 2026-08-26 UTC
**Session:** `session_01HfptKuEs3RDxaxsSHJjc7t`, branch `control/D-024-fable-codex-loop`

## Bootstrap Gate 0 (D-024-R125–R128)

- Verified this session before any write (recorded in `M0-T100-G0-readiness.md`): primary cwd IS
  this worktree root; branch `control/D-024-fable-codex-loop`; MCP roster empty. Unchanged since.

## Authorization chain

- Campaign `D-024-fable-codex-loop` seq 4 **NEXT = M0-T090** (machine-validated record).
- Owner directive D-027-R011 (2026-08-26) explicitly orders this continuation after M0-T100
  acceptance — M0-T100 is **accepted** (commit `b18fb20`, checkpoint `CP-D027-M0-T100`, pushed).
- Supervisor-freeze qualifying evidence: **D-024-R101** (Phase C) — cited in the packet objective;
  commits will cite it (freeze rule §3).

## Packet readiness

- Dependency `M0-T088` **accepted**. Task `backlog`, no producer, no blockers.
- `evaluate_task_refs`: ok=true; applicable == cited == 46 requirement ids (D-024:ALL resolution);
  `missing_ids: []`, `invalid_refs: []` — no selective citation.
- Scope: `tools/agent_supervisor`, `tools/test_agent_supervisor_bounded_contracts.py`,
  `project-control/reports/M0-T090-bounded-contracts.md`. Forbidden paths intact.
- Carried advisory bundle (named in campaign NEXT, applied where this task touches the relevant
  modules): G3-M1 (completed-first eviction-order isolation test in telemetry_sdk), G5-NIT-1
  (dash-encoded home mask into the cross-fixture class scan), G5-NIT-2 (dash-username
  first-segment limitation, documented). G5-MIN-1 is standing guidance for the future
  live-canary task (no public real-capture fixture planned here).
- Gates: G0 (this record) → G2 → independent G3 (code-reviewer) + G4 (qa-engineer) +
  G5 (security-reviewer) + DCV at the frozen identity → accept → advance the campaign record.
- Standing restrictions honored: NO worker-facing token quota/countdown/conserve-tokens pressure
  ever (D-024-R045); supervisor stays SHADOW-ONLY (R595/D-024 §18); never merge PR #241;
  suite-baseline duty applies (supervisor tree WILL change → re-establish the frozen baseline).

**G0 verdict: PASS — packet ready to claim.**
