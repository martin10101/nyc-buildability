# M0-T059 (P2) — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Producer evidence (backend-engineer, worktree `agent-adc6ed…`),
integrated onto `control/session15-acceptance` by cherry-pick (core `a644db45` + companion `a30abaf7`) at HEAD
`9c01612`. Independent confirmation is G3 code-review + G5 security-review; empty-set D-010 DCV row at accept.

## Deliverable → evidence
- **`clear_child_record` removes only `(pid, start_token)` (M0-T053 G5 finding 5 / activation-checklist P2).**
  In `recovery.py`, `clear_child_record(journal, *, pid, start_token="")` now filters out ONLY the entry
  matching `(pid, start_token)` (Mapping-guarded, `int(pid)`/`str(start_token)` compares), leaving every other
  recorded child intact — closing the whole-key wipe that fails OPEN on the no-duplicate-workers invariant
  (R347) the moment a second child is recorded (e.g. M0-T056's successor-launch seam). New helper
  `recorded_start_token_for(journal, pid)` recovers the launch-time token from the durable record (it cannot be
  re-derived from an exited pid). The sole production caller `_settle_worker_record` (`claude_runner.py`) looks
  up the token and passes `pid=process.pid, start_token=…`.
- **Companion fix (orchestrator-authorized scope expansion).** The signature change necessarily broke a 1-arg
  monkeypatch spy in `test_agent_supervisor_start_reentry.py` (a direct dependent; not in the 20-module freeze
  list but in the full-pytest CI job). Producer STOP-and-reported; orchestrator added that one test file to
  allowed_paths; the 2-line fix makes the spy `spy_clear(journal, **kwargs)` forward to the new-signature
  `real_clear`. No production behavior widened.

## Test evidence (integrated HEAD 9c01612)
- **M0-T039 freeze baseline (20-module unittest):** `Ran 1188 tests … OK (skipped=2)`, 0 failures, Python 3.11.9
  (base 1185 P1+P6 + 3 new: P2-SC1/SC2/SC3). ≥1165 satisfied.
- **CI supervisor-bridge parity (full pytest `tools/test_agent_supervisor_*.py`):** `1506 passed, 2 skipped`,
  0 failures — `test_agent_supervisor_start_reentry` GREEN under the new signature (`Ran 16 … OK`; was
  `FAILED (errors=1)` before the companion fix).
- **Lint:** `ruff 0.13.0` on all four changed py files → **All checks passed** (no new lint).
- **Non-vacuity (producer, reproduced):** reverting the whole-key wipe makes P2-SC1/SC2/SC3 all FAIL
  (`FAILED (failures=3)`); restoring → green. The guard is load-bearing.

## Scope discipline
`git diff --name-only 9239cc3 9c01612` (P2 deliverable) = exactly the amended allowed_paths: `recovery.py`,
`claude_runner.py`, `test_agent_supervisor_recovery.py`, `test_agent_supervisor_start_reentry.py`, producer
report. Supervisor-freeze respected (defect-only; minimal signature ripple to the sole caller + the one
dependent test).

## Verdict
Scoped P2 correction implemented, fail-closed, covered, non-vacuous; the full 36-module suite (incl.
start_reentry) is green. **PASS** (self_check; independent confirmation is G3 + G5).
