# M0-T145 G0 readiness (definition-of-ready) — 2026-09-06

Administrative G0 recorded by the orchestrator for the D-032 first live limited-auto loop queue
(queue position 1). Packet completeness verified:

- **Objective**: bounded and precise — close the M0-T109 G5 MEDIUM residual (braced-variable
  assignment-fronted nested shell laundered past `_launches_nested_shell` because
  `_SEGMENT_CHARS` tears the braced form before `_effective_command_token`).
- **Allowed paths** (3): `.claude/hooks/readonly_agent_guard.py`,
  `tools/test_readonly_agent_guard_powershell.py`,
  `project-control/reports/M0-T145-guard-brace-residual.md` — disjoint from M0-T025's scope
  (no overlapping files; safe for the same run queue).
- **Gates**: G0, G2, G3, G4, G5 — appropriate for a security-guard change.
- **Directive refs**: D-001:ALL cited; registry evaluation `ok: true`, applicable set empty,
  no missing/invalid/unresolved refs at claim time.
- **Baseline**: worktree `wt-m0t145` (branch `task/M0-T145-brace-guard`) at the certified
  candidate `e0dd4a3a` so the producer starts from the M0-T109-hardened guard.
- **Origin**: pre-existing residual found by the M0-T109 G5 review (not a regression);
  tracked in backlog since seq 81.

Verdict: PASS — ready to claim for the supervised-loop producer.
