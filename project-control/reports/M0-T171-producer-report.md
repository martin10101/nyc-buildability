# Producer report — M0-T171 (D-091 TW1): atomic review-slot reservation

Producer: backend-engineer. Worktree: /root/project/w-M0-T171, branch task/M0-T171-review-slots.
Claim-seam base: 12364237f7f32aa0bb3d7916ca31a93371f7283d.
HEAD after work: 6217ca98f308dc058f07bd2203223d5447d7f383 (differs from claim-seam).

## Files changed (only the two allowed material paths)
- tools/agent_supervisor/review_slots.py — replaces the 1-line placeholder (468 lines total, < WARN 600).
- tools/test_agent_supervisor_review_slots.py — new (303 lines).
(Producer report itself NOT written to project-control/ — orchestrator-only per dispatch step 5/7.)

## Objective
Close M0-T170 G3/G4 review note 1: `run_budget.admit_review_or_combine` is a pure, stateless
check and cannot stop a TOCTOU where two lanes both read `global_active==1` and both start a 3rd
process. This module makes count + decision + reservation ONE atomic step under an exclusive file
lock in the runtime directory. Nothing in the loop calls it yet (TW2 wires it).

## Design
- `ReviewSlots.try_reserve(lane)` runs entirely under `_SlotLock`: read live reservations, compute
  global_active/lane_active, call the unmodified `admit_review_or_combine`, and — only if admitted —
  write the new `Reservation` to the state file BEFORE releasing the lock. A second process cannot
  observe the pre-reservation count, so two can never both take the last of 2 global slots nor
  exceed 1 per lane. Also a `reserve()` context manager (reserve-before-spawn / release-after-exit)
  and `release()`.
- `_SlotLock` mirrors locking.py: `O_CREAT|O_EXCL` acquisition, retry-to-deadline so real contenders
  serialize (not fail), and the SAME `locking.probe_process` stale-scan takeover (temp + os.replace +
  re-read-confirm) so a crashed lock-holder is reclaimed and a live one is never stolen; an
  unassessable holder makes the wait time out → fail closed.
- Reservations carry pid + process-start token (`locking.process_start_token`). `reservation_owner_alive`
  prunes a provably-dead or reused-pid owner on read (never counted, never double-counted — the prune
  is persisted); an owner whose liveness cannot be determined is KEPT (fail closed: never free a
  possibly-live slot). Reused by both the registry and the lock's stale-scan.
- Fail closed everywhere: any lock error, any unreadable/malformed/non-record state file, and any
  write failure REFUSE with no slot (returned as a SlotGrant admitted=False carrying the reason_code,
  matching admit_review_or_combine's no-raise style). Missing state file = empty/fresh; present but
  unreadable = refuse (mirrors run_budget/durable_state). Bounds supplied by caller (immutable config).
- No dependency added; no edit to run_budget.py/resource_sampling.py/loop.py; no loop started;
  cross-platform (O_EXCL, os.replace, fsync, probe_process all have Windows branches).

## Tests (one class per acceptance scenario), exit codes at HEAD 6217ca98
- pytest tools/test_agent_supervisor_review_slots.py → 13 passed (exit 0).
- PRIMARY: two admitted, third refused (concurrency_limit_reached, scope global) while both held,
  release frees one; context-manager release; idempotent release.
- RACE: REAL separate OS processes (subprocess + file barrier; winners hold until released). 6 racers
  / 2 global slots → exactly 2 win; 6 racers / one shared lane, lane_limit 1 → exactly 1 wins.
- PER-LANE: a lane at lane_limit 1 is refused (scope "lane") while a global slot is free; another
  lane takes it.
- FAILURE/RECLAIM: corrupt JSON, non-record JSON, and a malformed reservation entry all fail closed
  (slot_state_unreadable); a lock error (directory at lock path, 0.2s timeout) fails closed
  (slot_lock_timeout); reused-pid, invalid-pid, and a REAL dead-child reservation are reclaimed and
  never double-counted (asserts on-disk ghost removed and active()==1, never 2).

## Repeated runs (flakiness)
- Full new suite: 6 consecutive passes, then 3 more post-fix = 9 clean runs.
- Race tests alone: 8 runs surfaced 1 failure → diagnosed as a TEST-HARNESS read race (parent read a
  result_<idx> file a child had created but not finished writing → int('')); product logic was
  verified correct by a standalone harness (120 races: global winners always exactly 2, per-lane
  always exactly 1, zero double-takes, no child stderr). Fixed the harness to write the result file
  atomically (temp + os.replace). After the fix: race-only 20/20 pass, full suite 3/3, plus the
  standalone 120-race harness clean.

## Adjacent suites + checks (exit 0)
- resource_fit + bounded_mode + bounded_contracts (the run_budget/resource consumers): 167 passed,
  48 subtests.
- ruff check on both new files: All checks passed (exit 0).
- python3 tools/modularity_check.py --check: exit 0 (new files not in the warn list; all warnings
  pre-existing).

## Assumptions / limitations
- The real-process race uses subprocess + a filesystem barrier rather than multiprocessing, because
  the suite runs on windows-latest in CI (per M0-T170-G3G4.md) where fork is unavailable and
  spawn+pytest re-import of a test-module worker is fragile; subprocess behaves identically on both.
- `_SlotLock` uses O_EXCL (per the dispatch's "mirror locking.py"), whose lock file the OS does NOT
  auto-release on process death; a crashed lock-holder is handled by the mirrored stale takeover, and
  an unassessable holder fails closed at timeout. (fcntl/flock would auto-release but was not chosen,
  to stay faithful to locking.py and cross-platform.)
- Recertification note (packet risk): this is a tools/agent_supervisor/** edit, so it invalidates the
  frozen certification; the one recertification task runs after all D-091 code tasks.

Requested status: awaiting_gate (G0,G2,G3,G4,G5; reviewers code-reviewer, security-reviewer,
control-plane-verifier, directive-compliance-verifier).
END-OF-REPORT
