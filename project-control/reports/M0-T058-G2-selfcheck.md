# M0-T058 (P1) — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Producer evidence (backend-engineer, worktree
`agent-a7b03bbed…`), integrated onto `control/session15-acceptance` by cherry-pick at HEAD `7c935f2`
(byte-identical deliverable to the producer commit `c3bf21b2`). Independent confirmation is G3 code-review +
G5 security-review at this material identity; the empty-set D-010 DCV row is recorded at accept.

## Deliverable → evidence
- **Verify-the-termination-you-assert (M0-T053 G5 finding 4 / activation-checklist P1).** In
  `ClaudeRunner._record_launched_worker`'s `record_launched_child`-failed except block
  (`claude_runner.py`): the boolean from `container.terminate_all()` is now **captured** (`killed`), a
  **bounded** `process.wait(timeout=CHILD_KILL_REAP_SECONDS=10.0)` reap check is added (`reaped`), and when
  the kill is **unverified** (`not (killed or reaped)`) a **distinct** `RunnerError("child_record_unwritable_orphan_live")`
  is raised whose message states a LIVE ORPHAN may survive — instead of the generic `child_record_unwritable`
  which wrongly implies termination. Verified-kill path keeps the original `child_record_unwritable`.
  The distinct code is consumed generically (cli.py renders `exc.code`/`exc.message`; no string-branch routing),
  so no downstream routing change was needed.

## Test evidence
- **M0-T039 freeze baseline (20-module unittest):** `Ran 1178 tests … OK (skipped=2)`, 0 failures, Python
  3.11.9 — above the ≥1165 bar (base 1175 + 3 new: `test_p1_sc1_verified_kill_keeps_the_original_reason`,
  `test_p1_sc2_unverified_kill_reports_a_possible_live_orphan`, `test_p1_sc3_the_reap_wait_is_bounded_and_never_hangs`).
  Reproduced by the orchestrator at integrated HEAD `7c935f2`.
- **CI supervisor-bridge parity (full pytest `tools/test_agent_supervisor_*.py`):** `1496 passed, 2 skipped`
  at `7c935f2` (base 1493 + 3). No regression in the other 16 modules.
- **Lint:** `ruff 0.13.0` (CI-matching) on the two changed files → **All checks passed** (no new lint).
- **Non-vacuity (producer, reproduced):** neutralizing the guard (`if False and not (killed or reaped)`) makes
  **P1-SC2 FAIL** (`'child_record_unwritable' != 'child_record_unwritable_orphan_live'`) while SC1/SC3 pass;
  restoring the guard → green. The guard is load-bearing.

## Scope discipline
`git diff --name-only 4083d2c 7c935f2` = exactly the three `allowed_paths`
(`tools/agent_supervisor/claude_runner.py`, `tools/test_agent_supervisor_runner.py`,
`project-control/reports/M0-T058-producer-report.md`). Supervisor-freeze respected (defect-only; no redesign).

## Verdict
Scoped P1 correction implemented, fail-closed, covered, non-vacuous. **PASS** (self_check; independent
confirmation is G3 + G5).
