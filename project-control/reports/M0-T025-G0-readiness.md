# M0-T025 G0 readiness (definition-of-ready) — 2026-09-06

Administrative G0 recorded by the orchestrator for the D-032 first live limited-auto loop queue
(queue position 2). Packet completeness verified:

- **Objective**: bounded and precise — path-containment validation for the directive manifest's
  `requirements_file` / `verification_file` references so they cannot resolve outside the
  directive's own directory, preserving current fail-closed behavior (LOW-1 hardening).
- **Allowed paths** (4): `tools/directive_registry.py`, `tools/validate_directive_compliance.py`,
  `tools/test_directive_compliance.py`, `project-control/reports/M0-T025-producer-report.md` —
  disjoint from M0-T145's scope (no overlapping files; safe for the same run queue).
- **Gates**: G0, G2, G3, G4, G5 — appropriate for a control-plane hardening change.
- **Directive refs**: D-002:ALL cited; registry evaluation `ok: true`, applicable set empty,
  no missing/invalid/unresolved refs at claim time.
- **Baseline**: worktree `wt-m0t025` (branch `task/M0-T025-path-containment`) at the certified
  candidate `e0dd4a3a` (carries the current registry/validator code including D-032).
- **Note**: long-standing backlog hardening item; explicitly "not a blocker for the first wave" —
  a good bounded commissioning workload.

Verdict: PASS — ready to claim for the supervised-loop producer.
