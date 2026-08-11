# M0-T060 (P3) — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Producer evidence (backend-engineer, worktree `agent-a8aae5c7…`),
integrated onto `control/session15-acceptance` by cherry-pick (deliverable `674e44c` + report `4c3e447`) at HEAD
`a9eb1b7`. Independent confirmation is G3 code-review + G5 security-review; empty-set D-010 DCV row at accept.

## Deliverable → evidence
- **Achieved per-cycle containment `!= job_object` STOP (M0-T053 G5 R4 half / activation-checklist P3).** In
  `loop.py SupervisedLoop.run_cycle`, on the OTHERWISE-OK path (the only path that would PROCEED), a cycle whose
  `run_result.containment != CONTAINMENT_JOB_OBJECT` now transitions `→ PAUSED_RECOVERY` (`unsafe_condition`) and
  `return stop("containment_degraded", …)` with an explicit recorded reason + a `TOUCH_SYNCHRONOUS_STOP` owner
  touch — instead of merely recording the degradation on the `claude_process_started` transition. A cycle
  reporting `job_object` proceeds unchanged. Seam confirmed IN-SCOPE (loop.py); the `state_machine.py` scope wall
  was NOT hit (it holds only the transition record, not the decision).
- **Ordering (disclosed & correct).** Placed AFTER the S14 checkpoint/effect reconciliation so a paramount
  `ambiguous_effect` / `no_valid_checkpoint` stop is never masked by this one. The producer's initial pre-reconciliation
  placement rippled one OUT-OF-SCOPE adversarial test (`test_agent_supervisor_adversarial`
  `test_the_loop_refuses_to_retry_a_unit_with_a_pending_effect`, expecting `ambiguous_effect`); the producer did NOT
  edit that test — it moved the guard onto the otherwise-OK path so the adversarial expectation holds naturally.

## Test evidence (integrated HEAD a9eb1b7)
- **M0-T039 freeze baseline (20-module unittest):** `Ran 1191 tests … OK (skipped=2)`, 0 failures, Python 3.11.9
  (base 1188 + 3 new: P3-SC1/SC2 + process_group case). ≥1165 satisfied.
- **CI supervisor-bridge parity (full pytest `tools/test_agent_supervisor_*.py`):** `1509 passed, 2 skipped`,
  0 failures — the out-of-scope adversarial test is GREEN (no ripple in the final placement).
- **Lint:** `ruff 0.13.0` reports 3 errors in loop.py (F401 `re`, F401 `.evidence.STOP_FOR_OWNER`, F841 `record`)
  — all **pre-existing** at base `20b82ea` (identical 3), **not introduced by P3**; and CI ruff runs only in
  `services/api` (tools/ not linted). No new lint.
- **Non-vacuity (producer, reproduced):** neutralizing the STOP guard (`if False and …`) makes P3-SC2 (and the
  process_group case) FAIL (`'' != 'containment_degraded'`) while P3-SC1 passes; restoring → green.

## Scope discipline
`git diff --name-only 20b82ea a9eb1b7` (P3 deliverable) = exactly `loop.py`, `test_agent_supervisor_loop.py`,
`M0-T060-producer-report.md`. Supervisor-freeze respected (defect-only; single fail-closed stop; no other loop
behavior changed).

## Verdict
Scoped P3 correction implemented, fail-closed, covered, non-vacuous; correctly ordered after the paramount
effect/checkpoint stops; full 36-module suite green. **PASS** (self_check; independent confirmation is G3 + G5).
