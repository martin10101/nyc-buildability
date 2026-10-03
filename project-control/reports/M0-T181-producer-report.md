# M0-T181 producer report

Task: supervisor-bridge Windows CI repair (DB-111), owner directive D-090-R093 /
D-090-R094. Producer: backend-engineer, isolated worktree, branch `producer/M0-T181`
from the claim-seam head `ec87eb6b`. Convergence analysis:
`project-control/reports/M0-T181-convergence-record.md`.

## Files changed (vs claim-seam `ec87eb6b`)

- `tools/agent_supervisor/mrl_descendants.py` — Failure B cause. Added
  `creation_token_to_ordinal`, `_probe_creation_ordinal`, `CreationOrdinal`; extended
  `descendants_of` and `prove_zero_descendants` with optional `root_start` +
  `creation_ordinal` so a process created before the root is pruned (with its subtree)
  rather than counted via a reused-pid stale parent. Backward compatible (defaults =
  prior behaviour). Module docstring corrected (the pid-reuse hazard documented).
- `tools/agent_supervisor/mrl_one_shot.py` — the in-scope worker caller. Captures the
  worker's creation ordinal while alive (right after `Popen`) and threads `root_start`
  into `prove_zero_descendants`.
- `tools/test_agent_supervisor_mrl_one_shot.py` — the failing test now mirrors the
  production caller (real briefly-running child, `root_start` captured while alive);
  two new mutation-proof tests for the exclusion and the fail-closed-on-unknown path.
- `tools/test_agent_supervisor_review_slots.py` — Failure A, TEST HARNESS ONLY. Race
  worker emits reason codes (`admitted` / `refused:<code>` / `barrier_timeout`);
  `_run_race` counts only `admitted`, accepts only `refused:concurrency_limit_reached`
  as a legitimate non-winner, and fails loudly on any other outcome; one shared window
  sizes the race, barrier budget derived (90 s = 60 s parent window + 30 s lock
  allowance). `tools/agent_supervisor/review_slots.py` (production) UNCHANGED.

`git diff --name-only ec87eb6b` = exactly those four files; no forbidden path touched
(no `.github/**`, no pytest config, no other supervisor module/test, no project-control
task/state/gate/blocker, no frozen evidence file edited).

## Checks (each with its DIRECT exit code; venv python 3.12.3, pytest 9.0.3)

- `python -m pytest -q tools/test_agent_supervisor_review_slots.py tools/test_agent_supervisor_mrl_one_shot.py -p no:cacheprovider` → `83 passed, 2 subtests passed in 8.19s` — **EXIT=0**
- `python -m pytest -q tools/test_agent_supervisor_mrl_one_shot_review.py -p no:cacheprovider` (consumer of touched `mrl_descendants`) → `81 passed in 24.87s` — **EXIT=0**
- `python tools/supervisor_command_doc_check.py` → `11 presented command(s) checked; 0 failure(s)` — **EXIT=0**
- `python3 tools/modularity_check.py --check` → `692 files; failures 0; warnings 29` (no warning on the changed files) — **EXIT=0**
- `ruff check tools/agent_supervisor/{mrl_descendants,mrl_one_shot,process}.py tools/test_agent_supervisor_{review_slots,mrl_one_shot}.py` → `All checks passed!` — **EXIT=0**
  (A whole-dir `ruff check tools/agent_supervisor` reports 3 PRE-EXISTING issues in
  `github_flow.py` (E402 ×2) and `rotation.py` (F401) — both untouched by this task and
  outside allowed_paths; the supervisor-bridge CI job runs pytest, not ruff on tools/.)

## Safety and concurrency assertions — before/after (none removed or loosened)

`tools/test_agent_supervisor_review_slots.py` — the full assertion set is byte-identical
before and after (only line numbers shifted; verified by grepping `self.assert`/`assert`
on HEAD vs the working tree — same list):
- Race invariant PRESERVED EXACTLY: `assertEqual(winners, 2)` + `assertLessEqual(len(ReviewSlots(self.dir).active()), 2)` (global), `assertEqual(winners, 1)` (per-lane). A `self.fail(...)` loud-fault branch is ADDED (strengthening), not a loosening.
- Fail-closed slot errors kept: `slot_state_unreadable` (corrupt / non-record / malformed entry), `slot_lock_timeout` (directory-at-lock-path; persistent Windows delete-pending), `slot_lock_error` (non-sharing OSError; POSIX PermissionError), reused-pid reclaim, dead-process reclaim, idempotent release — all unchanged.
- Primary/per-lane admission + `active()` counts — unchanged.

`tools/test_agent_supervisor_mrl_one_shot.py` — descendants/proof assertions kept:
- `test_descendants_of_walks_the_whole_tree_and_skips_self_parents`, `_finds_an_orphan_whose_parent_already_exited`, `_prove_zero_descendants_waits_for_the_settle_window`, `_gives_up_after_the_window_with_the_remaining_pids`, `_reports_an_unobservable_table`, `test_real_process_table_sees_this_interpreter_alive` — all unchanged (pin settle window, give-up-with-remaining, unobservable=unavailable, no-start-time orphan-visible behaviour).
- `test_real_process_table_proves_a_reaped_child_gone` — final assertion UNCHANGED (`proven is True and remaining == ()`); only the child body + `root_start` capture added to mirror production.
- NEW: `test_reused_pid_orphan_before_root_is_not_a_descendant_but_a_real_child_is` (asserts guarded-excludes AND un-guarded-counts — the guard is load-bearing) and `test_descendant_with_unknown_creation_time_is_kept_fail_closed`.

## R094 statement (explicit)

No test was deleted, skipped, xfail-marked, or renamed away. No assertion was loosened
(every assertEqual/assertTrue/assert in the two test files is kept or strengthened —
listed above). No retry loop, rerun plugin, `--reruns`, sleep-and-retry, or
try-again-on-failure was added anywhere (added-line scan for
skip/xfail/rerun/retry/flaky/pytest.mark = NONE). No `.github/**` and no pytest
configuration (pytest.ini/pyproject/conftest) was changed. ONE timeout changed: the
race worker's barrier go-deadline (30 s → 90 s), and ONLY because the trace proves the
old 30 s value IS the cause (shorter than the parent's 60 s readiness window) and the
new value is DERIVED from a stated budget (parent readiness window 60 s + lock-
serialization allowance 30 s) — see convergence record §2. The racer `lock_timeout_s`
and hold stay 30 s (not implicated). No settle window changed for failure B.

## tools/agent_supervisor/** changed? YES — M0-T179 recertification consequence

`tools/agent_supervisor/mrl_descendants.py` and `tools/agent_supervisor/mrl_one_shot.py`
changed → the M0-T179 Linux supervisor certification is VOIDED; this takes the D-091
recertification path (recorded, not a bar — R093 authorized fixing the cause). The
supervisor tree hash changes and the `M0-T039-supervisor-freeze.md` suite baseline
(≥ 1165 tests, 0 failures) must be re-established under the standard gates. Failure A
changed TEST FILES ONLY (`review_slots.py` production untouched). Supervisor-freeze §2
qualifying evidence for the `tools/agent_supervisor/**` change: a reproduced defect
(DB-111 — four frozen windows-latest failures) + an owner-directive requirement
(D-090-R093), cited in the commit messages.
