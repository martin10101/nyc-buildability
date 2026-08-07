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
| 5 | run_m0t035_shadow_pilot_r5 | Worker unit PERFECT on the F-3 fix (~2 min, schema-valid checkpoint validated + correlated; evidence packet bounded + digest-bound). Codex review failed 3/3 attempts → `review_unavailable`, WAIT_FOR_OWNER | 1/2 (in budget; blocking_ask) | F-6: provider rejects the decision schema (`allOf` not permitted); F-7: adapter masked it as `missing_decision_file` |
| 6 | run_m0t035_shadow_pilot_r6 | **FULL CYCLE COMPLETE.** Preflight verified → worker checkpoint `cp-m0t035-accept-ready-r6` schema-valid, validated, correlated → bounded digest-bound evidence packet → live Codex decision **COMPLETE** (model gpt-5.6-sol, attempt 1, returncode 0, no self-report mismatch, selection digest recorded) → stage evidenced complete with the 4 gate records + packet as evidence_refs → `stopped=stage_complete`, final state COMPLETE, ends AT the gate ("This never merges or accepts anything") | **0/2** (no would-be stop) | — |

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
- **F-6 (adapter defect, live-confirmed run 5): the provider rejects the decision schema.**
  `codex exec --output-schema` fails HTTP 400: "Invalid schema for response_format
  'codex_output_schema': 'allOf' is not permitted" — `codex_decision.schema.json` uses `allOf`
  for per-decision conditional requireds, outside the OpenAI strict structured-output subset.
  Every review attempt turn-failed; the fallback chain could not help (same schema). Fix
  dispatched 2026-08-04: flatten the schema to the accepted subset; `validate_decision`
  (already the in-code S9 authority) absorbs any constraint the old schema alone carried.
- **F-7 (reporting defect): the provider rejection was masked.** The adapter reported
  `missing_decision_file` and defaulted returncode 0 in the failure outcome; the real child
  returncode (1) and the `turn.failed` provider error never reached the audit. Fix in the same
  unit: distinguish provider rejection from a genuinely absent file; record the bounded,
  redacted provider error and the real returncode per attempt.
- **F-5 (recorded per owner directive, D-007-R561/R562):** tzdata hidden runtime dependency —
  RESOLVED-BY-ADMISSION; recommend doctor/preflight verify timezone-database resolvability so a
  fresh machine fails at setup, not at its first wake (no build work now).

## Touch-budget accounting so far

Each completed cycle recorded exactly 1 would-be synchronous stop (the checkpoint rejection),
within the ≤2 budget. No stop was a policy false-positive: every stop was a true defect signal
(F-3/F-4). The budget is a measurement and authorizes nothing.

## Erratum (2026-08-04, appended per the G4 QA review's required correction — append-only, history preserved)

The run-4 root-cause line above and F-3's "run 3 captured it, runs 1 and 4 lost it" sentence are
WRONG on the checkpoint-survival detail. Run 4's own audit chain records checkpoint_id
`cp-m0t035-accept-ready-r4` with an empty error_category — the checkpoint SURVIVED and validated;
the S4.5 stop was driven by `timed_out=true` (the fail-closed rule that a timed-out unit is never
OK), not by checkpoint loss. Run 3 is the inverse (checkpoint present but invalid). Corrected
account: all three pre-fix runs rode the 900 s wall (F-3 stands, live-validated by runs 5/6);
run 1 lost/never produced a checkpoint, run 3's was invalid, run 4's was valid but the unit's
timeout made the run un-OK. The SessionCloseTests docstring repeats the old wording — cosmetic,
noted for V1.1.
