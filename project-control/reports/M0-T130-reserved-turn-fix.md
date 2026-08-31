# M0-T130 — reserved-turn delivery fix: deferred injection at genuine idle + robust unit completion (D-024-R420..R424)

Producer: orchestrator (`orchestrator-defect-runner`, M0-T108 orchestrator-as-producer
precedent authorized by Amendment 28 R420). Base identity `6b7000b7` on
`control/D-024-fable-codex-loop`, primary checkout, single writer. AD-093 qualifying
evidence: the journey-3 REPRODUCED DEFECT (`M0-T107-commissioning-journey-3.md`) —
installed Claude Code 2.1.251 absorbed the pre-queued reserved-final-turn prompt
mid-turn (queue event `absorbed_mid_turn`, 2026-08-31T18:35:01Z), truncating the live
worker's working phase AND riding the 900s wall watchdog into a counted stop.

## 1. The change (tools/agent_supervisor/claude_runner.py, `run_unit`)

1. **Deferred injection (R421).** `extra_turns` are no longer written at launch. They
   are held `pending`, and each is written only at GENUINE IDLE — after the prior
   written turn's terminal `result` event — and only while the drained stream has not
   already decided the checkpoint question. The reserved demand therefore can never be
   absorbed into the in-flight working turn, and a worker whose first result already
   carries its checkpoint never receives (or spends) the reserved turn at all.
2. **Decidedness helper (R421).** New module function `checkpoint_question_decided`:
   only a stream with NO checkpoint candidate (`missing_checkpoint`) warrants the
   injection; a valid, invalid, or conflicting candidate is already decided — one more
   demanded turn could only add a conflicting duplicate (`extract_checkpoint` refuses
   to choose between candidates by design).
3. **Robust completion latch (R422).** `unit_complete` now latches when every WRITTEN
   prompt has its terminal result AND nothing is left to inject. A worker that answered
   everything never rides the wall watchdog; the watchdog (`timeout_seconds`, 900s in
   production) remains solely for genuinely runaway units, and the graceful-close /
   tree-termination accounting is unchanged.

Net mechanical change: ~30 lines in `run_unit` + one helper. No CLI flag, no schema,
no journal key, no broker/allowlist, no loop.py/turn_budget.py change (the injection
CONTENT and the sizing are untouched — only the DELIVERY moment moved into the runner,
where the turn boundary is actually observable).

## 2. Coverage (tools/test_agent_supervisor_runner.py; R423)

New fake-CLI modes derive from the journey-3 measurement (no new provider launches):
`absorbs_early_second_prompt` reproduces the measured absorption (two early prompts ->
ONE merged no-checkpoint result, session open — the wall-ride shape);
`no_checkpoint_then_checkpoint`; `never_checkpoint`.

| Path | Test | Removal-sensitive against |
|---|---|---|
| absorption can no longer occur | `ReservedTurnDeliveryTests::test_an_absorbing_cli_never_sees_an_early_second_prompt` | reverting to launch-time writes (mutant run below) |
| checkpoint-in-first-result skips the reserved turn (1 result) | `SessionCloseTests::test_a_checkpoint_in_the_first_result_skips_the_reserved_turn` (repurposed from the pre-fix two-results test, whose asserted behavior this task deliberately changes) | injection-always regression |
| injection delivered as its OWN turn when the first result lacks a checkpoint | `ReservedTurnDeliveryTests::test_reserved_turn_is_injected_when_the_first_result_lacks_one` | dropping the injection |
| honest FAST failure when the reserved turn still yields nothing | `ReservedTurnDeliveryTests::test_no_checkpoint_after_the_reserved_turn_fails_fast` | the wall-ride defect (R422) |
| runaway unit still wall-terminates | `SessionCloseTests::test_the_wall_watchdog_still_owns_the_runaway_unit` (pre-existing, unchanged) | watchdog regression |
| decidedness vocabulary | `ReservedTurnDeliveryTests::test_checkpoint_question_decided_vocabulary` | helper semantics drift |

**Red-on-mutant proof (G2):** temporarily restoring the launch-time writes made
`test_an_absorbing_cli_never_sees_an_early_second_prompt` FAIL with exactly the live
shape (`missing_checkpoint` after the merged result; wall path) — 1 failed / 3 passed —
then the mutant was reverted and the pack returned green.

## 3. Self-check results (G2)

- `tools/test_agent_supervisor_runner.py`: **78 passed** (74 prior + 4 new; 1
  repurposed in place; no test removed — the one deliberately changed assertion is the
  fixed behavior itself, disclosed above).
- Whole supervisor suite (all `tools/test_agent_supervisor*.py`, one process): recorded
  in the commit/gate evidence (expected 3,039 = 3,035 baseline + 4 new; reconciliation
  in the G2 gate record).
- `ruff check` on both touched files: clean. Command-doc tooth: exit 0 (no flag or
  command shape changed).
- `modularity_check --check` — **CORRECTED after G3-C1/C2 (the original claim here was
  FALSE):** at the reviewed identity the checker FAILED (exit 1, `baseline_growth`:
  claude_runner.py 1400 SLOC > limit 1383 = baseline 1258 + 10%; this diff's ~20 new
  SLOC tipped 142 SLOC of cumulative certified growth over the threshold). The
  producer's original run masked the exit code behind a shell pipe (`--check | tail`)
  and misread ruff's "All checks passed!" as covering the modularity tooth — an
  evidence-handling error, corrected here. Remediation (G3-C1, scope amendment adding
  `tools/modularity_exceptions.json` to allowed_paths): a path-exact expiring FILE
  exception (max_lines 1410, baseline_sloc 1400, expires 2026-11-25) with the cohesion
  justification the G3 review endorsed; the checker now reports **failures 0, exit 0**
  (re-run unpiped). A module split is the recorded follow-up on the next substantial
  growth.

## 4. Honest residuals

1. **CLI max-turns semantics across a second written turn** (cumulative-per-session vs
   per-run reset) remains UNMEASURED. Under either semantic this fix strictly improves
   on the absorbed shape: the healthy path cannot be truncated. Sub-cases when a worker
   truly exhausts every turn (G3-O1 precision): if the exhausted CLI answers the
   injected reserved turn with a terminal result (with or without a checkpoint), the
   unit ends FAST and honestly; if it silently swallows the injected prompt (no result,
   stream open), the unit still rides the 900s wall watchdog into a WATCHDOG-BOUNDED
   tree-termination — narrower and safer than the original defect (turn 1 completed;
   no truncation; never a false success), but a wall ride nonetheless. The fixtures do
   not exercise the silent-swallow sub-case (consistent with it being unmeasured); the
   next owner-typed journey measures the real semantics live.
2. The absorption fixture is a FAKE reproducing the measured 2.1.251 behavior (derived
   from the journey-3 queue events); it is not a recorded live-CLI fixture. R286/R287
   stand: any future CLI upgrade is an admission event that re-measures this.
3. This is a supervisor change: the `tools/agent_supervisor` tree hash moves —
   R247 recertification (golden + whole suite + record-manifest/verify-controller +
   doctor) re-runs at the new frozen identity after acceptance (R424) before the
   commissioning command is re-presented.
