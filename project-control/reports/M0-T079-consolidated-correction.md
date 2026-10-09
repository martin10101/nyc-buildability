# M0-T079 consolidated correction set (one round; no drip-feed)

Issued by the orchestrator after the COMPLETE T079 review set (G2 self-check, G3 code,
G4 integration, G5 security) at frozen identity `c52613f` / task commit `e830c4b`
(tools/agent_supervisor tree `0175f40e`). Verdicts: G3 PASS-with-corrections, G4
PASS-with-correction, **G5 FAIL (2 must-fix)**. Per D-023-R016/R017 this is ONE consolidated
correction, not a stream. The producer applies all of C1–C9 in the wt-m0t079 worktree; the
orchestrator then re-freezes and re-reviews the corrected identity (focused re-review of both
must-fix items plus a full G5 re-pass, and re-run of the full supervisor suite).

## Must-fix (block acceptance)

- **C1 (G5 M1) — budget self-reset via missing/malformed record.** `RunBudgetLedger.start()`
  (run_budget.py:277) treats a deleted record, a non-Mapping record, and an intact record with
  `started_at_epoch: null` all as a fresh start — resetting elapsed, wiping tallies, and skipping
  the `budget_conflict` digest check. Fix: distinguish "no record at all" (legitimate first launch)
  from "a record exists but is unreadable/malformed" (fail closed with a typed `BudgetError`, mapped
  to `stale_state`); a present run-budget key whose payload is not a well-formed started record must
  REFUSE, never fresh-start. Audit both the refusal and any first-launch. Add tests for all three
  corruption shapes proving refusal (not fresh budget).
- **C2 (G5 M2) — credential leak through probe evidence.** The probe report attached to the emitted
  payload (cli.py:2966) carries raw `git remote get-url` output (recovery_probes.py:363,385-390)
  and is printed with a bare `json.dumps` (cli.py:1742). Route the emitted payload through the
  package's mandatory `redact_structure` before printing (the same redaction audit_log.append and
  evidence.py already apply), OR redact at the probe-evidence source. Prove with a PAT-bearing remote
  that the token never reaches stdout/stderr in either `--json` or human mode.

## Important (required rework; blocking-for-acceptance per gate-verdict semantics)

- **C3 (G5 I1) — synthesized-argv enable replay.** Add `--owner-enable-bounded-auto` (and any future
  bounded-mode enable) to a deny set enforced by `assert_argv_safe` (process.py:133-171) so a
  scheduler-invoked synthesized argv (turnover_adapters._orchestrator_argv) can never carry the
  enable. This is the containment-side fix and lives in process.py — do NOT edit turnover_adapters.py
  (M0-T080 owns that file); the deny-set in the shared safety checker covers it.
- **C4 (G5 I2) — per-day tally decay.** `check()` must not declare a per-day counter exhausted from a
  stale peak after the UTC day rolls. Evaluate per-day counters against the current day (reuse the
  injected clock's `utc_day_for`); a resumed run on a new day gets its per-day allowance back while
  per-run counters stay monotonic. Test the day-roll case.
- **C5 (G5 I3 + I4) — typed refusals for corrupt persisted state.** `run_live_probes` must run ALL
  probes even when one raises (no first-raise abort; collect per-probe failures). `RunBudget.from_dict`
  bare `float()` and `restore_counters`' unvalidated names must raise `BudgetError` (typed), and
  cmd_start's except clause must map every such corruption to a typed refusal — never a bare traceback
  / exit 1. Tests: raising probe, corrupt wall_clock, unknown tally name.
- **C6 (G5 I5) — audit the tamper/breaker/refused events.** Emit hash-chained audit events for:
  `budget_conflict` (the budget-tamper signal), circuit-breaker trips invoked with `trigger=""`
  (currently unrecorded), and `refused_mode` bounded-mode launches under the R033 hold. Follow the
  containment-refusal precedent (cli.py:3013).
- **C7 (G5 I6 + G4 F1) — missing-input refusal exits 0.** The `if not dispatchable:` branch
  (cli.py:2971) must return a typed refusal exit code (not 0) OR the exit-code contract `doctor`
  prints must explicitly document the missing-input=0 and manifest-halt=1 carve-outs. Given the
  bounded-mode danger (an unattended launcher reads 0 as success), prefer the typed refusal; amend the
  pinned test (test_agent_supervisor_loop.py:1146) accordingly and confirm genuine dispatch still
  exits 0.
- **C8 (G3 I1) — probe reads a never-maintained ledger field.** `probe_task_authority`
  (recovery_probes.py:252-257) fails closed on the task record's free-form `blockers` list, which the
  control plane never maintains. Read the authoritative `project-control/blockers/B-*.json` with
  `status in ("open","")` matched to the task id, exactly as `accept()` does (project_control.py:1176).
  Prove: a task carrying a resolved blocker id dispatches; a task with a live open blocker record
  refuses.
- **C9 (G3 I2 / G5 I7) — deadline_restored refuses on expired deadlines.** Gate on the `outstanding`
  fact `probe_scheduled_deadlines` already computes against the clock (recovery_probes.py:542-547),
  not on the mere presence of `resume_not_before_utc`. An already-expired deadline must not refuse
  dispatch (`assert_may_contact_provider` already permits provider contact once it passes). Harden the
  probe's ISO comparison to parse instants rather than compare strings lexicographically (the G5 minor
  that becomes load-bearing here). Test expired vs outstanding.

## Also fix while in these files (load-bearing minors)

- **C10 (G3 I3) — provider-CLI drift latch.** `cli_executable_identity` has no re-pin/clear path; a
  routine CLI auto-update bricks every subsequent start with no remedy but deleting the journal. Add an
  owner-visible re-pin (a documented CLI subcommand or an explicit `--repin-cli-identity` flag that
  records the new identity with provenance). Do not weaken drift DETECTION.
- **C11 (G3 I4) — permanent budget-exhaustion trap.** Because `--run-id` defaults per-checkout, a run
  that hit a per-run counter limit strands every future start on that checkout. At minimum: the
  `budget_exhausted` message must name `--run-id` as the way to start a fresh run, `--run-id` must gain
  help text, and correct the stale `circuit_breakers.py:57-64` "units-per-run, never resets" comment
  that C1/C4 make untrue. Consider whether a deliberately-new run should require an explicit new id.
- **C12 — the small hygiene minors:** import `DurableJournal` in start_gate.py (or use a string
  annotation) so `get_type_hints` works; broaden the R037 source-scan test to cover loop.py/cli.py and
  a leading-underscore/`DEFAULT_*`/`*_CAP` ceiling name (G3 M-2); guard `_REVISE_SAFE_RESETS` with a
  subset-of-RESET_ON_PROGRESS assertion (G4 F2); correct the stale "limited-auto not implemented" docs
  in README.md:11/269 (remote_approvals.py:308 is M0-T080's to fix — leave it). Note in the report
  which minors you deferred and why.

## Deferred to the owner checkpoint (host acts — not this task)

- Journal-DB ACL hardening (`%LOCALAPPDATA%\NYCBuildabilitySupervisor`): the G5 threat-model item.
  M1's code fix (C1) removes the exploit; ACL hardening raises the bar further and is a protected-host
  act for the final owner checkpoint, tracked in D-023-campaign-findings.md.

## Re-review contract

After the producer applies C1–C12 and re-runs the full supervisor suite (must stay ≥1707/0/2 or
higher with the new tests), the orchestrator re-freezes and dispatches: a full independent G5 re-pass
(must clear both must-fix), a focused G3 re-check of C1/C5/C8/C9's changed surface, and a G4 re-run of
the full tree. Only then G2 re-record and acceptance. No acceptance while any must-fix is open
(directive-compliance skill §5; gate-verdict semantics).
