# M0-T089 — G0 readiness (administrative)

Task: D-024 B2 — subagent telemetry breadth + read-only shadow status + carried M0-T088 bundle.
Recorded by: orchestrator (G0 administrative class). Date: 2026-08-25.

- Dependency M0-T088 ACCEPTED (frozen content `23f0d80`, material identity `356d0f47`,
  acceptance commit `316cd8e`, checkpoint CP-D024-M0-T088 `9037bb3`). Campaign record seq 2
  names M0-T089 as NEXT with the carried findings bundle spelled out.
- Packet extended pre-claim by the orchestrator (matching the M0-T088 precedent): the five
  carried M0-T088 gate-round items added to outputs; `tools/test_agent_supervisor_telemetry_core.py`
  added to allowed_paths (two bundle items — the per-step naming fix and its test updates, and the
  test-helper determinism fix — necessarily touch that file).
- Packet valid: `evaluate_task_refs` ok:True, applicable=34, cited=34, missing=[] (identical set
  to M0-T088).
- Bootstrap Gate 0 (D-024-R125..R128) remains passed for this session: primary cwd ==
  `git rev-parse --show-toplevel` == `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; branch
  `control/D-024-fable-codex-loop`; `/mcp` reported "No MCP servers configured" at session start
  (recorded in M0-T088-G0-readiness.md); unchanged cwd/branch since.
- Supervisor-freeze (AD-093 + D-024 recognition): qualifying evidence = **D-024-R100** (Phase B,
  explicitly listed in D-024), present in the packet objective; citation duty carries to every
  commit touching `tools/agent_supervisor/**`.
- B1 foundation on file: telemetry_records/redaction/journal/ingest at `23f0d80` identity;
  capability matrix documents subagentStatusLine payload shape (official-docs, fetched 2026-08-25)
  and hooks event set for 2.1.220; SDK remains absent-by-policy (skip-not-install).
- Scope posture unchanged from M0-T088 G0: `tools/agent_supervisor` overlaps M0-T080 (D-023,
  round-3 review, own worktree `wt-m0t080`, own branch); reconciliation deferred to Phase D by
  the campaign plan. No claimed task holds a write lease on this branch/worktree.
- Blockers: none referencing M0-T089.

Result: PASS — backlog → ready to claim.
