# M0-T036 Phase 5 shadow pilot — run log and findings (live, appended per run)

- Pilot lifecycle: M0-T035 acceptance-readiness verification (fit assessment:
  `../M0-T036-phase5-shadow-fit.md`); controller = dedicated read-only checkout
  `C:\SupervisorController` (owner-created 2026-08-04) at the task branch; config +
  model_selection owner-placed, doctor-validated (codex allowlist gpt-5.6-sol/terra,
  claude account-default, shadow-only boot).
- Every run: shadow mode, forwarded NOTHING, Job-Object containment, session id recorded,
  audit chain intact. Runtime evidence preserved verbatim per run under `runtime-runN/`;
  parked runtime dirs retained on the host (never deleted).

## Runs

| Run | run_id | Outcome | Owner touches | Root cause |
|---|---|---|---|---|
| 1 | run_m0t035_shadow_pilot | S4.5 stop `missing_checkpoint`; PAUSED_RECOVERY | 1/2 (in budget) | Operator prompt lacked the S8.3 checkpoint contract; worker answered in prose |
| 2 | run_m0t035_shadow_pilot_r2 | Refused before acting: `IllegalTransitionError` PAUSED_RECOVERY → act | n/a (no cycle) | F-2: no CLI exit from PAUSED_RECOVERY |
| 3 | run_m0t035_shadow_pilot_r3 | S4.5 stop `invalid_checkpoint` (status vocabulary); PAUSED_RECOVERY | 1/2 (in budget) | Checkpoint emitted but `status: awaiting_gate` is not in the S8.3 unit vocabulary (IN_PROGRESS/UNIT_COMPLETE/BLOCKED/READY/FAILED); prompt bug |
| 4 | run_m0t035_shadow_pilot_r4 | S4.5 stop, worker exited without a valid checkpoint; PAUSED_RECOVERY | 1/2 (in budget) | F-3: checkpoint text lost to the timeout kill (see below) |

## Findings (decision-packet inputs)

- **F-1 (validated design): fail-closed core works live.** Missing/invalid checkpoints were
  refused, counted as synchronous stops, and parked in recovery; shadow forwarded nothing in
  any run; audit chain stayed intact; limited-auto untouched.
- **F-2 (completeness defect): `PAUSED_RECOVERY` has no operator exit.** The state machine
  defines `PAUSED_RECOVERY → PREFLIGHT` on trigger `owner_cleared_pause`, but no CLI command
  fires it (`resume` clears only the manual-pause flag). Today's only path is parking the
  journal and starting fresh — which loses run continuity. Needs a CLI recovery-clear command.
- **F-3 (runner defect, audit-confirmed): every unit runs to the full 900 s wall.** In
  `claude_runner.run()`, nothing ends the stream-json session after the final turn: stdin is
  closed only after the stdout read loop, and the loop only ends when the process exits, so the
  watchdog tree-terminates every unit at exactly `timeout_seconds` (three runs: dispatch →
  unit-completed = 900.0 s, `timed_out: True`, returncode 0). Whether the final checkpoint text
  survived termination is flush-timing luck: run 3 captured it, runs 1 and 4 lost it. Fix
  dispatched 2026-08-04: end the read loop on the final turn's `result` event (stdin stays open
  until then for control_responses), bounded-grace close, wall watchdog unchanged.
- **F-4 (usability): the operator must hand-author the S8.3 checkpoint contract into the unit
  prompt.** Nothing injects the checkpoint schema or the status vocabulary automatically; three
  of four run failures trace to this. Recommendation: the supervisor should append a canonical
  checkpoint-contract instruction block to every dispatched unit prompt.
- **F-5 (recorded per owner directive, D-007-R561/R562):** tzdata hidden runtime dependency —
  RESOLVED-BY-ADMISSION; recommend doctor/preflight verify timezone-database resolvability so a
  fresh machine fails at setup, not at its first wake (no build work now).

## Touch-budget accounting so far

Each completed cycle recorded exactly 1 would-be synchronous stop (the checkpoint rejection),
within the ≤2 budget. No stop was a policy false-positive: every stop was a true defect signal
(F-3/F-4). The budget is a measurement and authorizes nothing.
