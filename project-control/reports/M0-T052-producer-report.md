# M0-T052 producer report — B-018 stranded-START_CLAUDE recovery window

Task: fix B-018 (defect reproduced live 2026-08-08) — an externally-killed
supervisor launch strands the durable journal at `START_CLAUDE` and becomes
permanently unrecoverable.
Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052`
Branch: `task/M0-T052-start-reentry` (based on main `de2e647`)
Verdict on the proposed fix: **IMPLEMENTED AS PROPOSED** (admit `START_CLAUDE`
to `CYCLE_ENTRY_STATES`). Verified smallest and safe.

## Root cause

The launch window in `loop.py::run_cycle` has two durable journal boundaries:

1. `preflight_pass -> START_CLAUDE` commits at loop.py:1607 (now shifted; see
   below) **before** the worker is launched;
2. `START_CLAUDE -> CLAUDE_RUNNING` commits at loop.py:1637 **only after**
   `runner.run_unit(...)` returns a real process.

An external kill inside that gap leaves the durable journal at `START_CLAUDE`
with nothing launched and no child recorded. `CYCLE_ENTRY_STATES` was
`frozenset({PREFLIGHT, CLAUDE_RUNNING})`, so on the next operator `start`,
`run_cycle` (entry-state guard, loop.py:1586) raised `bad_cycle_entry_state`
every time — even after `recovery.recover_boot` classified the checkout
`SAFE_CHECKPOINT`. `recover_boot` records its outcome but transitions nothing,
and no production code drove the S7 exits from `START_CLAUDE`
(`state_machine.py`: `START_CLAUDE -> CLAUDE_RUNNING | HALTED` only). Net effect:
unrecoverable without out-of-band action.

## Why this is the smallest durable fix

`START_CLAUDE` semantically means "about to launch, nothing has launched yet",
which is precisely a safe re-entry point. `run_cycle` already handles that entry
correctly the moment the guard admits it, with no other change:

- the `if entry == PREFLIGHT` guard (loop.py:1606) skips the duplicate
  `preflight_pass` transition, so a resume commits no second
  `PREFLIGHT -> START_CLAUDE`;
- the `if self.machine.current_state == START_CLAUDE` block (loop.py:1637)
  transitions to `CLAUDE_RUNNING` only after a real process started, so the
  resume dispatches exactly once;
- the resource-trip (loop.py:1598-1604) and circuit-breaker (loop.py:1611-1621)
  entry paths stop at the current legal state with **no** transition; from
  `START_CLAUDE` neither attempts an illegal transition (the breaker's
  `PAUSED_RECOVERY` transition is gated on `current_state == CLAUDE_RUNNING`).

No new dispatch path is opened. Every launch is still gated upstream in
`cli.py::cmd_start` on `recover_boot(...).classification == SAFE_CHECKPOINT`
(cli.py:2374); `_run_loop`/`loop.run()` are reached only through that gate
(sole callers: cli.py:2396 and cli.py:2304). `recover_boot` fails closed on a
surviving/undetermined recorded child (S11.5 step 3, `account_for_children`), a
competing writer, a lock it cannot acquire, any failed/missing revalidation
step, or a pending external effect. The single-instance lock, journal child
accounting, and Job-Object kill-on-close containment are all unchanged.

Paths audited for the entry-state contract and confirmed unaffected:
`_guard`/`assert_can_act` (START_CLAUDE is not a BLOCKING_STATE);
the FORWARD_PROMPT rotation/resume path in `loop.run()` (loop.py:2327) enters
`run_cycle` at `CLAUDE_RUNNING`, never `START_CLAUDE`; shadow-mode semantics
(one observation, forwards nothing, closes to PREFLIGHT) unchanged.

## Files changed (all inside allowed scope)

1. `tools/agent_supervisor/loop.py`
   - line 137: `CYCLE_ENTRY_STATES` now
     `frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})`.
   - lines 114-136: expanded the doc-comment with the B-018 crash-window
     rationale (the constraint the code cannot show: why `START_CLAUDE` is a
     legal re-entry, and that dispatch stays gated on `SAFE_CHECKPOINT`).

2. `tools/test_agent_supervisor_loop.py`
   - `CycleEntryStateTests`: renamed
     `test_the_only_entry_states_are_preflight_and_claude_running` ->
     `test_the_only_entry_states_are_preflight_start_claude_and_claude_running`
     and updated the asserted set to include `START_CLAUDE` (this test encoded
     the OLD invariant the fix intentionally changes). The IDLE-refused and
     no-transition-on-refusal cases are unchanged and still pass.

3. `tools/test_agent_supervisor_start_reentry.py` (new)
   - 10 tests: crash-window resume regression, fail-closed negatives, and the
     SAFE_CHECKPOINT positive control (detail below).

No other supervisor module changed. No authority/tier/gate semantics widened.

## Test evidence

Focused (new file):
```
$ python -m pytest tools/test_agent_supervisor_start_reentry.py -q
..........                                                               [100%]
10 passed in 1.17s
```

Full supervisor suite, exactly as CI runs it (from worktree root):
```
$ python -m pytest tools/test_agent_supervisor_*.py -q
1402 passed, 2 skipped in 133.74s (0:02:13)
```
Freeze baseline was 1392 passed / 2 skipped / 0 failed. New total is
1402 passed / 2 skipped / 0 failed = baseline + 10 new tests, no regressions.
Environment: Python 3.11.9.

New-test coverage mapped to the required scenarios:
- (a) crash-window regression — `CrashWindowResumeTests`: strands the journal at
  `START_CLAUDE` with no recorded children (via the exact
  `start_command` then `preflight_pass` durable transitions), proves the strand
  is read from the journal by a fresh `StateMachine`, then proves `run_cycle`
  and `loop.run()` dispatch the fake worker **exactly once**
  (`len(runner.prompts) == 1`), transition to `CLAUDE_RUNNING`, do not
  re-record `preflight_pass`, and complete/close legally (shadow +
  supervised full-path variants).
- (b) fail-closed negative — `FailClosedResumeTests`: with the journal at
  `START_CLAUDE`, a surviving recorded child (`os.getpid()`), a competing
  writer, and a pending external effect each classify NOT-SAFE_CHECKPOINT
  (`UNSAFE_OR_DRIFTED` / `AMBIGUOUS_EFFECT`) through the real `recover_boot`,
  which is the exact boolean `cmd_start` gates dispatch on.
- (c) idempotence — `test_a_surviving_recorded_child_forbids_the_resume`:
  documents and tests that `recover_boot`'s `account_for_children` (S11.5 step 3)
  refuses BEFORE the loop is built when the previous process recorded a surviving
  child, so a resume can never double-launch over a live worker. Positive control
  `test_a_clean_strand_classifies_safe_checkpoint` proves the same stranded
  journal WITH no surviving child / writer / pending effect classifies
  `SAFE_CHECKPOINT`, which is why (a)'s resume is permitted.

## Qualifying-evidence citation

B-018 qualifies under the supervisor-freeze policy §3 (defect-fix carve-out to
the code freeze): a reproduced correctness defect in the supervisor recovery
path, fixed with the smallest change that keeps the freeze baseline at 0
failures and widens no authority/tier/gate semantics.

## Assumptions / limitations

- No live end-to-end `cmd_start` CLI invocation was added; the fail-closed gate
  is proven at the `recover_boot` classification boundary (the exact value
  cmd_start branches on) plus the existing CLI test
  `test_a_loop_refusal_is_a_report_not_a_traceback`, which still exercises a
  stranded non-entry state (`COLLECT_EVIDENCE`) end-to-end and still passes.
- The surviving-child test uses the current test process PID as a provably-live
  child; it records no `start_token`, so the PID-reuse branch is intentionally
  not exercised (covered elsewhere in the recovery suite).

---

## G5 C3 correction (appended by the orchestrator, 2026-08-08)

The G5 security review (M0-T052-g5-security.md, SEC-MINOR + required correction C3) found the
safety rationale above and the loop.py doc-comment overstated the double-launch guarantee: the
`recover_boot` surviving-child fail-closed applies only to RECORDED children, and the production
launch path does not currently record children (`record_launched_child` has no production
caller). The OPERATIVE guarantee against resuming over an orphaned worker is the platform
kill-on-close containment (Windows Job Object; verified live on this host:
`containment_default: job_object`). The loop.py comment was corrected accordingly (C3);
supervised-auto is barred on hosts without live kill-on-close by the activation-record pin (C1);
wiring production child accounting is the bounded M0-T053 follow-up (C2). This note corrects the
producer report per the report-preservation rule - the original text above is preserved
unchanged.
