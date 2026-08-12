# GATE REPORT — M0-T056 (G2 producer self-check)

- **Task:** M0-T056 — R595 production turnover actuation
- **Gate:** G2 (producer self-check; recorded by the orchestrator with role `self_check`; never counts as independent review)
- **Producer:** backend-engineer
- **Reviewed identity:** content_manifest_sha256 `9306071de8fd2013dc15452581c8a4616725a0d545db8fffc531c56a94396d48` at HEAD `44f27999e0cd6aee4c42c0a4100578730a0608f5`
- **Reviewed code identity (provenance):** `a90ac19` (byte-identical to HEAD across the 6 allowed_paths files).

## Producer self-check evidence (from producer report §3, §5)

1. **Freeze baseline re-established, 0 failures.**
   - `python -m pytest tools/test_agent_supervisor_*.py -q` → **1525 passed, 2 skipped, 0 failed** (includes the new `tools/test_agent_supervisor_r595_actuation.py`, 19 tests).
   - `python -m unittest` (the M0-T039 20-module baseline) → **Ran 1191 tests, OK (skipped=2), 0 failed**.
   - M0-T039 freeze bar = "≥ 1165 tests, 0 failures" → re-established.
2. **New tests are non-vacuous** and drive real `run_cycle` / real controller seams (confirmed by the G3 delta review, TEETH section). 19 tests cover AS-1..AS-4, AS-6, and the M0-T060 `containment_verified_in_job` fail-closed gate.
3. **Lint:** `ruff 0.13.0` — the changed files introduce zero new findings; pre-existing F401s are on untouched lines and present on base `0d42953`. `tools/agent_supervisor/**` is not CI-ruff-gated (CI ruff runs `working-directory: services/api`).
4. **Scope clean.** Only the 5 supervisor files changed (+ this report). `turnover_controller.py` / `turnover_adapters.py` / `model_turnover.py` reused UNCHANGED (zero diff, R357). `recovery.py` byte-unchanged (M0-T059 not triggered). No forbidden path touched (services/api, apps/web, packages/contracts, C:/SupervisorController/config.toml).
5. **Fail-closed / no-other-hold-moved** verified at the diff level (producer report §5): protected config/ACLs, command/path/credential protections, LIMITED-AUTO refused-by-name, push/GitHub/five-borough/history-rewrite/evidence-deletion all untouched; successor model hard-pinned to claude-opus-4-8/xhigh.

## Not self-approvable
Per principle 7 / ADR-005 this self-check does not accept the task. AS-5 (the isolated live continuous proof, R349) is deliberately NOT run in the sandbox (C1 gate hard-refuses on POSIX) and is owner-run on a Windows/job_object host per producer report §7.

**VERDICT: PASS (self-check).**
