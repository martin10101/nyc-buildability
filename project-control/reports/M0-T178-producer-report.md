# M0-T178 producer report — dual-review conductor refuses equal combining and Claude reviewer models

Task: M0-T178 (D-091 / DB-103). Worktree `/root/project/w-M0-T178`, branch
`task/M0-T178-equal-model-refusal`. Qualifying evidence: DB-103; D-091-R001, D-091-R007
(`.claude/rules/supervisor-freeze.md` §2/§3 evidence-citation duty).

## What changed (allowed_paths only)

1. `tools/agent_supervisor/dual_review.py`
   - New preflight guard `_check_combiner_distinct_from_claude()`, called from
     `_preflight(...)` AFTER `_check_claude_reviewer_model()` and BEFORE
     `_check_codex_reviewer_model()` — the same pre-process refusal point as the allowlist
     checks, which runs before `_acquire_slot()` and before any reviewer/combiner process.
   - Refuses fail-closed (via the existing `_refuse(...)` -> `_unverified(...)` outcome, no
     slot, no process) when:
     - the combining model equals the Claude reviewer model -> `review_models_not_distinct`;
     - either model is empty -> `review_models_unset` (defensive "either empty" guard; empties
       are also caught earlier at `combiner_model_unset` / `claude_reviewer_model_unset`).
   - A reviewer that does not expose `.model` (`None`) defers to its own review-time guard,
     mirroring `_check_claude_reviewer_model` (nothing to compare). Different, allowlisted
     models proceed exactly as before. Windows/Linux identical (pure string comparison; no OS
     calls). No change to `review_combiner.py` / `claude_reviewer.py`.
   - Module docstring "Models resolved before any process" bullet updated to state the
     distinct-model requirement.

2. `tools/test_agent_supervisor_dual_review.py`
   - New `Scenario7CombinerDiffersFromClaudeReviewer(ConductorBase)` with four tests and a
     local `_assert_refused_before_process` helper (asserts fakes not called + no slot).

3. `docs/D091_LINUX_COMMISSIONING.md` step 5
   - "future improvement" paragraph replaced: the code now refuses equal/empty models; the
     read-only tomllib check stays as a pre-start confirmation / backstop. The combining-model
     sentence also notes the distinct-model refusal. Other steps unchanged.

4. `project-control/reports/M0-T178-producer-report.md` (this file).

## Acceptance scenarios -> tests -> results

| Scenario (packet) | Test | Result |
|---|---|---|
| equal: combiner == claude reviewer model -> refused before any process, no slot | `test_equal_combiner_and_claude_models_refused_before_any_process` (code `review_models_not_distinct`) | PASS |
| empty: either model empty -> refused before any process | `test_empty_combining_model_refused_before_any_process` (`combiner_model_unset`); `test_empty_claude_reviewer_model_refused_before_any_process` (`claude_reviewer_model_unset`) | PASS |
| proceed: different allowlisted models proceed exactly as before | `test_different_allowlisted_models_proceed_unchanged` (both reviews run, verdict PASS, CONTINUE) | PASS |
| mutation: removing the equality check turns the equal-models test red | see mutation evidence below | confirmed RED -> restored |

Each refusal test asserts `codex.calls == 0`, `claude.calls == 0`, `combiner_runner.calls == 0`
and `len(slots.active()) == 0` — proving the refusal happens before any spawn or slot reservation.

## Mutation evidence

Neutralized the equality branch (`if combiner_model == reviewer_model:` ->
`if False and combiner_model == reviewer_model:  # MUTATION: check removed`) and ran the
equal-models test:

```
FAILED tools/test_agent_supervisor_dual_review.py::Scenario7CombinerDiffersFromClaudeReviewer::test_equal_combiner_and_claude_models_refused_before_any_process
  tools/test_agent_supervisor_dual_review.py:589: in _assert_refused_before_process
    self.assertFalse(result.ok)
  E   AssertionError: True is not false
1 failed in 0.58s   (PYTEST_EXIT=1)
```

With the check removed the conductor proceeded (returned an ok outcome; both reviews would
run) — the test caught it. Check restored to `if combiner_model == reviewer_model:`; the
four-file self-check suite is green again (below).

## Exact commands and exit codes

- Baseline (before edits), four self-check files:
  `python -m pytest -q -p no:cacheprovider tools/test_agent_supervisor_dual_review.py
  tools/test_agent_supervisor_review_combiner.py tools/test_agent_supervisor_claude_reviewer.py
  tools/test_agent_supervisor_review_slots.py` -> `107 passed, 2 subtests passed` (exit 0).
- After edits (same four files) -> `111 passed, 2 subtests passed` (exit 0).
- New class only: `...::Scenario7CombinerDiffersFromClaudeReviewer` -> `4 passed` (exit 0).
- Mutation run (equal-models test) -> `1 failed` (exit 1); after restore, four files ->
  `111 passed, 2 subtests passed` (exit 0).
- Broad regression: `python -m pytest -q -p no:cacheprovider -rf tools/test_agent_supervisor_*.py`
  -> `43 failed, 3941 passed, 26 skipped, 11379 subtests passed` (exit 1). The 43 failures are
  pre-existing, environment/platform-specific tests this change does NOT cause: `grep -l dual_review
  tools/test_agent_supervisor_*.py` shows ONLY `test_agent_supervisor_dual_review.py` imports the
  changed module, and that suite is fully green (111 passed, incl. the 4 new tests). None of the
  failing files import `dual_review`. The failures are real-process / live / Windows-path tests
  that cannot run on this Linux sandbox: `model_chain` (10 — `RealProcess*`/`CrashResume*`/
  `ChainExhaustion*`), `mrl_exec_chain` (12), `golden_run` (7), `loop` (3 — `test_a_real_child_
  process_drives_a_shadow_cycle`, two CLI-start scenarios), `launch_seam` (3 — e.g. `test_AS3_
  windows_drive_case_and_slashes`), `os_acl` (3 — icacls/system32-powershell), plus
  `native_adapter`, `telemetry_core`, `capability_probe`, `checkpoint_envelope`, `event_bus`
  (1 each). No dual-review / combiner / reviewer / model-distinctness test failed. The full
  >=1165-test freeze baseline runs in CI (Linux + the gates).
- Ruff: `ruff check tools/agent_supervisor/dual_review.py tools/test_agent_supervisor_dual_review.py`
  -> `All checks passed!` (exit 0).
- Modularity: `python3 tools/modularity_check.py --check` -> `failures 0` (exit 0, direct code);
  `dual_review.py` not flagged.

pytest run via `/root/project/lanes-runtime/venv/bin/python` (system python3 has no pytest);
ruff via `/root/project/lanes-runtime/venv/bin/ruff`.

## Notes / limitations

- No live supervisor start, no systemd-run/systemctl, no RealProcess classes, no network — the
  conductor is driven against the existing in-process fakes + the real `ReviewCombiner` /
  `ReviewSlots`, per the suite's design.
- This is an additive pre-process refusal + a new test class + docs; it changes the
  `tools/agent_supervisor/` tree hash, so the freeze suite baseline must be re-established under
  the standard gates (`.claude/rules/supervisor-freeze.md` §4) in CI.
- No change to `review_combiner.py` / `claude_reviewer.py`; reviewer-independence by identity
  and the orchestrator's sole authority (ADR-005) are untouched.
