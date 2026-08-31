# M0-T126 design record - durable checkpoint design + one-identity defect corrections

Producer: supervisor-stabilization-producer. Window: D-024 Amendment 22 (R372-R394).
Built on control-branch tip HEAD 1bb773531bbb3283211de28ffdaf374467e994ab, in the isolated
worktree agent-af926a5886c3c4ab3. NO live launch, NO supervisor CLI write verb, NO clear-recovery,
NO restart, journal never opened (R374/R375 preserved). All work inside the M0-T126 allowed_paths.

This record is the design map. The producer report (M0-T126-producer-report.md) carries the exact
commands and pass/fail counts. All claims here are backed by tests that run green.

## 0. Completion status (read first)

ALL 17 register defects (D1-D17) are corrected at this one frozen identity, per R385. Seven-property
foundations 1-5 implemented and wired; 6-7 realized via next_task exactly-once + the fail-closed
extract_checkpoint. G4 corrections 1-4 all satisfied, including correction 3's verdict-persistence and
campaign-advancement interruption rows. The command-document tooth is CI-wired. Removal-sensitive
and adversarial coverage over the preserved artifacts includes R388 and the full R387 sixteen-scenario
minimum. No defect is deferred. The only work NOT run in-window is the ~3h13m R247 recertification
(test_agent_supervisor_golden_run.py's slow recert), which the packet assigns to M0-T127 (budget note
O2); every FAST golden_run class passes. The gates and orchestrator judge acceptance.

FRESH-REMEDIATION PASS (D-024-R395, this identity). The G3 FAIL and G4 required corrections were
remediated in one fresh-producer pass:
- G3-1: property-1 orientation is now wired into the ROTATED path. loop_turnover.with_reorientation
  front-loads the rotated=True orientation packet (cadence + allowed_paths + exact-required-output)
  onto the S11.3 handoff via orientation.oriented_reorientation_prompt, using a sized budget the loop
  now holds (loop._turn_budget, wired from cli net-zero). Proven at DISPATCH level by
  loop::RotatedOrientationDispatchTests (asserts the successor's actual prompt carries all three;
  removal-sensitive with no budget), not just the module branch.
- G3-2: the reserved final turn is now technically injected. loop.py's run_unit call passes
  turn_budget.reserved_turn_injection(self._turn_budget) as extra_turns, delivering the mandatory
  "emit the checkpoint NOW - do not run any other tool" demand as an ACTUAL follow-up user turn
  through the provider's stdin channel (claude_runner run_unit extra_turns), not prompt-text only.
  Removal-sensitive: no budget -> empty extra_turns (the preserved 12/12 shape). The fail-closed
  exhaustion net (missing_checkpoint -> PAUSED_RECOVERY) is untouched. NOTE for the orchestrator: the
  acceptance evidence-map R378 row (M0-T126-evidence-map.json, outside this task's allowed_paths) now
  describes a REAL injection - reconcile it from the verified code (loop.py run_unit extra_turns +
  turn_budget.reserved_turn_injection), not the prior text.
- G3-3: the D15 runbook regeneration is complete. Section 1 digests were RECOMPUTED from the live
  sources (readable this session): protected-config raw A1F99501...1436, LF-normalized 4c67875b...e75f,
  model-selection FCBBF70F...DD2B (matches M0-T113 sec5). Section 5 (and 6/7/8/10/11) now write and
  reference the manifest at the certified OUTSIDE-the-tree location
  ($env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json). Section 11
  is regenerated to the current D-024 campaign (branch control/D-024-fable-codex-loop), replacing the
  retired M0-T063 identities; --run-id is omitted rather than invented. The tooth stays exit 0 (12
  commands) and LivingRunbookTests + test_runbook_has_a_pinned_start_command pass.
- G4-1/2/3: report test counts re-measured at THIS tree; the design-record test citations corrected
  (see sec 5 scenario 6 and sec 6).

Full verification at the final identity: 2990 supervisor tests pass excl. golden, 2 pre-existing skips (8 defect
packs re-measured: next_task 18, command_docs 17, orientation 13, checkpoint_journey 25, recovery 63,
launch_seam 69, loop 122, runner 74 = 401 combined) + all fast golden_run classes (27) pass, 2
pre-existing skips; ruff clean on every touched file; modularity failures 0 (cli.py 2953/2953 and
claude_runner.py 1383/1383 net-zero; loop.py 2034/2088); the command-document tooth exits 0.

## 1. Seven-property mapping (property -> mechanism -> file:line -> removal-sensitive test)

| Prop | Mechanism | Location | Removal-sensitive test |
|---|---|---|---|
| 1 front-loaded orientation (fresh AND rotated) | FRESH: build_orientation_packet / with_orientation / oriented_first_prompt wired at first dispatch. ROTATED (G3-1): oriented_reorientation_prompt front-loads the same rotated=True packet onto the S11.3 reorientation handoff via loop_turnover.with_reorientation, using the loop's sized budget | orientation.py; cli.py _run_loop (fresh call site); loop_turnover.with_reorientation + loop.py:2766/2883 (rotated call sites); loop._turn_budget wired from cli | orientation::RequiredElementsTests + RotatedReorientationTests; loop::RotatedOrientationDispatchTests (the DISPATCHED rotated prompt carries cadence+allowed_paths+required-output; removal-sensitive: no budget -> not enriched) |
| 2 early + incremental checkpoint | early_checkpoint_by, incremental_checkpoint_every sized from the budget and surfaced in the orientation cadence | turn_budget.size_turn_budget; orientation cadence block | checkpoint_journey::TurnBudgetTests::test_early_and_incremental_cadence_within_working_turns; orientation::test_cadence_names_early_incremental_and_reserved_final_turn |
| 3 reserved final turn (technically injected, G3-2) | RESERVED_FINAL_TURNS always 1; total = working + reserved. The reserved turn is OCCUPIED by an actual follow-up user turn (turn_budget.reserved_turn_injection) delivered through run_unit's extra_turns stdin channel at loop.py:1619 - not prompt-text only. The orientation cadence still names the reserved turn; the injection enforces the emission demand at the boundary | turn_budget.py (reserved_turn_message / reserved_turn_injection); loop.py run_unit call (extra_turns); loop._turn_budget | checkpoint_journey::ReservedTurnInjectionTests; loop::ReservedTurnInjectionDispatchTests (removal-sensitive: no budget -> empty extra_turns, the preserved 12/12 shape); checkpoint_journey::test_cohesive_reserves_a_final_turn / test_ceiling_clamp_preserves_reserved_final_turn |
| 4 honest incomplete-but-resumable | the 12/12 exhaustion replays to missing_checkpoint (never success); the sized budget exceeds the fixed 12 that starved the unit | claude_runner.extract_checkpoint (pre-existing, S14); fixtures/m0t107_stream_d5.json | checkpoint_journey::TurnExhaustionReplayTests::test_exhausted_stream_has_no_valid_checkpoint |
| 5 workload-sized turns under hard ceiling | size_turn_budget + TurnAllowances (per-class), HARD_TURN_CEILING; sized total replaces max_turns | turn_budget.py; cli.py sized_max_turns -> RunnerConfig.max_turns | checkpoint_journey::test_class_sizes_differ_not_a_single_raised_constant; ::test_total_never_exceeds_the_hard_ceiling |
| 6 fail-closed on incomplete emission | extract_checkpoint refuses missing/conflicting/multiple; a not-OK unit lands PAUSED_RECOVERY | claude_runner.extract_checkpoint; loop not-OK path (pre-existing) | checkpoint_journey::TurnExhaustionReplayTests; existing runner/loop suites |
| 7 exactly-once persistence + forwarding | record_advancement over compare_and_swap_state (single-winner); crash/restart re-attempt returns the stored record | next_task.record_advancement / advance_and_select | next_task::ExactlyOnceAdvancementTests::test_advancement_survives_a_crash_restart_without_doubling; ::test_contradictory_later_output_never_re_advances |

## 2. Turn-allowance table and the documented hard safety ceiling

Per-class working turns (turn_budget.TurnAllowances defaults), each plus exactly 1 reserved final
turn, all clamped to HARD_TURN_CEILING = 40:

| Class | Working turns | + reserved | Total | Rationale |
|---|---|---|---|---|
| main-session | 8 | 1 | 9 | quick/frequent-decision work; smallest productive allowance |
| cohesive-subagent | 32 | 1 | 33 | the preferred self-contained unit the fixed 12 starved (default dispatch class) |
| unknown-recon-first | 6 | 1 | 7 | cheapest bounded recon step before committing more |
| oversized-split-at-seams | (not dispatchable) | - | 0 | must be split before dispatch; never enlarged |

HARD_TURN_CEILING rationale (R380): a bounded unit is bounded; work needing more turns is oversized
and must be SPLIT (the same principle workload_classifier applies), never handed a larger single
unit. 40 is set well above the largest class allowance (33) so the CLASS sizes the unit, not the
ceiling; the ceiling only catches a config override or a future class table that would mint an
unbounded unit, and caps worst-case per-unit provider spend. It is a SAFETY ceiling, not a target -
nothing sizes up to it. This is NOT "merely raising the fixed max_turns": the value is derived from
the structural workload class, distinct per class (proven by test_class_sizes_differ...), and always
below the hard ceiling. cli._run_loop builds max_turns from the sized budget, defaulting the
classification to cohesive-subagent (a bounded task packet dispatched to a supervised worker is that
size by construction) unless the packet declares a workload_class.

## 3. Seventeen-defect correction map (defect -> change -> test)

- D1 presented-command drift: command_docs validation tooth (extract presented supervisor commands,
  dry-run against build_parser + dispatch_inputs_missing + pinned flags); CI entry
  supervisor_command_doc_check.py wired into ci.yml supervisor-bridge job. Test:
  test_agent_supervisor_command_docs.py::ValidationTests (removal-sensitive on each pinned flag).
- D2 --repo primary-checkout leak: launch_seam.evaluate_repo_binding + enforce_launch_bindings;
  cli._run_loop refuses repo==primary_checkout when the packet declares an isolated worktree. Test:
  launch_seam::CliRepoBindingGateD2. SEED-A LABEL: this is DCV discrepancy 1 (the evidence/review
  half of the cycle-2 leakage class); the worker cwd was already seam-bound, this closes the repo half.
- D3 fixed 12-turn / sizing unwired: turn_budget + orientation, wired into cli (sized max_turns +
  front-loaded orientation for FRESH and, via the rotation seam, ROTATED workers - G3-1). The reserved
  final turn is technically injected as a follow-up user turn (G3-2, turn_budget.reserved_turn_injection
  through run_unit extra_turns). Test: checkpoint_journey::TurnBudgetTests + TurnExhaustionReplayTests
  (the preserved 12/12 replay fails the old design and passes the new via an honest missing-checkpoint);
  loop::RotatedOrientationDispatchTests + ReservedTurnInjectionDispatchTests.
- D4 degenerate native_tools flag: renamed field RunResult.native_tools_guidance_present and compute
  it as sentinel-PRESENCE on the dispatched bytes AFTER both appends (claude_runner.py run_unit ~1231;
  RunResult field + audit key renamed). Test: test_agent_supervisor_runner.py::NativeToolsPresenceD4Tests
  (three shapes: fresh, old-contract, pre-seeded - all present; removal-sensitive on the fresh shape).
- D5 cumulative-vs-live tokens: claude_runner.live_context_tokens (peak per-turn, excluding the
  cumulative terminal result event) + RunResult.live_context_tokens field; loop._ceiling_context_tokens
  prefers the live figure; both recorded. Test: checkpoint_journey::LiveVsCumulativeTokensTests (live
  72546 vs cumulative 694251; ceiling consumes live; adversarial at exactly 400000).
- D6 journal-order inversion / START_CLAUDE rest: journal a dispatch-intent record at dispatch and
  reconcile it on unit return (loop.run_cycle around run_unit: recovery.record_dispatch_intent /
  reconcile_dispatch_intent); recovery.classify returns AMBIGUOUS_EFFECT (reason_code
  unit_dispatch_unreconciled) when the intent is unreconciled at recovery, so a crash mid-unit
  reconciles before re-dispatch instead of treating a determined-dead child as SAFE. Additive: fires
  only when the marker is present. Tests: test_agent_supervisor_recovery.py::CrashBoundaryTests three
  crash-injection rows (immediately-after-Popen, after-partial-stream, checkpoint-in-stream-before-
  extract) + a reconciled-control test.
- D7 dead safe_auto_resume / misleading epilogue: (a) cli.cmd_start epilogue now annotates
  `resume permitted` on an operator-typed start carrying --owner-enable-bounded-auto (the per-launch
  enable is honored by the mode gate, not by recovery); (b) recovery.classify's safe_auto_resume
  branch is documented as R595-GATED / unreachable-until-activation (recovery.py, the final SAFE
  return). Both presentation-only; no gate behavior changed (D7 is presentation, not gate logic).
- D8 PREPARE_ROTATION strand: loop routes ROTATE_SESSION through the rotation seam (rotation_pending
  + ROTATE_SESSION_REASON, cycle_closed -> PREFLIGHT); rotate_session added to
  session_continuity.CONTEXT_SHEDDING_REASONS so the pre-first-dispatch seam sheds it at the proven
  seam. Test: loop::test_rotate_session_routes_through_the_seam_not_prepare_rotation.
- D9 COMPLETE strand / no next-task selection: next_task.py (plan_close_run fires the existing
  run_closed edge; select_next_packet; record_advancement exactly-once; advance_and_select). cli
  closes a COMPLETE journal to IDLE on the next start. Test: next_task suite (all classes) +
  ConsecutiveAdvancementTests (R388).
- D10 forwarded CONTINUE prompt loss across process boundaries: loop.run persists a durable
  next-unit-prompt pointer on every forward (_persist_next_unit_prompt, keyed next_unit_prompt/<run_id>)
  and, on CLAUDE_RUNNING entry, consumes it EXACTLY ONCE (_consume_next_unit_prompt) to dispatch the
  forwarded bytes instead of the generic default; the forward message-id cycle number is journal-
  advancing (cycle_base offset), so a cross-process re-decision mints a DISTINCT id and is not dead-
  ended by duplicate_suppressed. Tests: test_agent_supervisor_loop.py::CrossProcessForwardResumeD10Tests
  (dispatch forwarded bytes on next start - removal-sensitive; consumed exactly once; advancing cycle
  number). The golden restart row (golden_run.py) was updated to the certified single-cycle shape: it
  previously "passed" only because the D10 bug dead-ended the second start via duplicate_suppressed.
- D11 no between-cycle stop/pause read: loop._intent_stop at the between-cycle seam reads
  stop_intent.StopIntents + effective_intent and stops before the next dispatch. Test:
  loop::BetweenCycleIntentStopTests.
- D12 graceful-stop no consumer: folded into D11's between-cycle intent gate (graceful blocks the
  next dispatch via may_dispatch_new_work). Test: same class (test_graceful_stop_blocks_the_next_dispatch,
  test_a_run_stops_when_an_intent_is_set).
- D13 budget-before-gate: cli._run_loop calls machine.assert_can_act() BEFORE budget_ledger.start(),
  so a start over a HALTED/PAUSED journal refuses without mutating durable budget. Covered by the
  existing bounded_mode/crash/recovery packs (all green after the reorder).
- D14 argparse requires nothing: the command-doc tooth pins --checkout/--repo/--branch/--worktree/
  --max-cycles and requires the six dispatch inputs on every presented start. Test:
  command_docs::ValidationTests::test_removing_each_pinned_flag_fails.
- D15 runbook drift: docs/CONTROLLER_UPDATE_RUNBOOK.md FULLY regenerated (G3-3). Section 1 digests
  RECOMPUTED from the live sources this session (protected-config raw A1F99501...1436 + LF-normalized
  4c67875b...e75f; model-selection FCBBF70F...DD2B; all match M0-T113 sec5). Section 5 (and 6/7/8/10/11)
  write/reference the manifest at the certified outside-the-tree location
  ($env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json, M0-T113 sec1
  item 10). Section 11 regenerated to the current D-024 campaign (branch control/D-024-fable-codex-loop),
  retired M0-T063 identities removed, --run-id omitted (never invented), --checkout still pinned. The
  CI tooth validates every runbook command (exit 0, 12 commands). Test:
  command_docs::LivingRunbookTests::test_runbook_presented_commands_all_pass +
  test_runbook_has_a_pinned_start_command.
- D16 legacy durable records / dead-child sweep: (i) the recorded session token is the LIVE figure
  (folded into D5's re-recording via _ceiling_context_tokens), so a legacy no-token record stays
  read-unknown/fail-closed; (ii) recovery.sweep_dead_child_records archives DETERMINED-DEAD child
  records with provenance to ARCHIVED_DEAD_CHILDREN_KEY at recover_boot time (after classify; never
  touches surviving/undetermined records). Test:
  test_agent_supervisor_recovery.py::CrashBoundaryTests::test_d16_determined_dead_child_is_archived_with_provenance.
- D17 no test consumes presented commands: the tooth IS that test (offline + CI). Test:
  the whole command_docs suite + the CI step.

## 4. G3 citation corrections (bound in this design record; the register is immutable)

- D9 enter-COMPLETE is loop.py:2041-2042 (decision_complete). Confirmed against the reviewed source.
- The 604,772 rotation figure originates at audit seq 21 (not seq 24). The derived fixture
  m0t107_journey_facts.json records rotation_figure 604772 at rotation_figure_seq 21.
- D7 False-writers are remote_approvals.py:295/307 (the register's 293/306 were the pre-identity
  offset; G4 O3 flagged this). D7 IS corrected (Section 3): the safe_auto_resume branch is documented
  R595-gated citing remote_approvals.py:295/307, and the cli epilogue annotates operator starts.

## 5. R387 sixteen-scenario matrix (scenario -> fixture -> test node)

| # | Scenario | Fixture / source | Test node |
|---|---|---|---|
| 1 | fresh + rotated orientation | (synthesized OrientationInputs) + real rotation seam | orientation::FreshVsRotatedTests + RotatedReorientationTests (module); loop::RotatedOrientationDispatchTests (the DISPATCHED rotated prompt, G3-1) |
| 2 | consuming every working turn | m0t107_stream_d5.json (12 turns) | checkpoint_journey::TurnExhaustionReplayTests |
| 3 | early/incremental/incomplete/final checkpoints | turn_budget cadence + m0t107_stream_d5 | checkpoint_journey::TurnBudgetTests + TurnExhaustionReplayTests |
| 4 | missing/malformed/duplicate/contradictory checkpoints | m0t107_stream_d5 (missing) + extract_checkpoint suite (pre-existing) | checkpoint_journey::test_exhausted_stream_has_no_valid_checkpoint; runner suite |
| 5 | Codex HALT and CONTINUE (G4 corr 1) | synthesized CONTINUE decision (no preserved replay) | checkpoint_journey::CodexContinueVerdictTests (removal-sensitive on next_claude_prompt) |
| 6 | missing/malformed/duplicate/STALE Codex verdicts (G4 corr 2) | synthesized stale/duplicate decisions + real journal CAS | STALE half: checkpoint_journey::CodexStaleVerdictTests (correlation guard removal-sensitive); DUPLICATE half: next_task::ExactlyOnceAdvancementTests::test_duplicate_advancement_in_same_process_is_noop + ConsecutiveAdvancementTests::test_crash_AFTER_verdict_persistence_never_re_advances (a duplicate verdict never double-advances) |
| 7 | Codex review failure + success | synthesized decisions + pre-existing codex suite | checkpoint_journey::CodexContinueVerdictTests + existing |
| 8 | exactly-once task advancement (G4 corr 4, D9-gated) | real journal CAS | next_task::ExactlyOnceAdvancementTests |
| 9 | interruption before/after checkpoint, forwarding, verdict persistence, advancement (G4 corr 3) | real journal crash/restart | see the scenario-9 sub-matrix below |
| 10 | next-task selection + dispatch (G4 corr 4, D9-gated) | ordered packet list | next_task::SelectionTests |
| 11 | rotation before provider contact | (D5 ceiling) | checkpoint_journey::LiveVsCumulativeTokensTests (ceiling consumes live) |
| 12 | provider crash/refusal/quota/context/restart | D5 context + pre-existing crash/recovery suites | checkpoint_journey::LiveVsCumulative + existing packs |
| 13 | worktree isolation + primary-checkout refusal every path | (D2 + pre-existing worktree binding) | launch_seam::CliRepoBindingGateD2 + CliWorktreeGate |
| 14 | preserve audit/budgets/owner-gates/pending-effects | D13 (assert before budget) + intent gate | existing bounded_mode/crash packs; loop::BetweenCycleIntentStopTests |
| 15 | command-document validation | runbook + README | command_docs suite + CI step |
| 16/R388 | consecutive advancements, no human intervention | real journal | next_task::ConsecutiveAdvancementTests |

### Scenario 9 sub-matrix (interruption rows, G4 correction 3 both halves)

| Interruption point | Test node |
|---|---|
| immediately after Popen (before stream) | recovery::CrashBoundaryTests::test_d6_crash_immediately_after_popen_is_ambiguous |
| after partial stream (no checkpoint) | recovery::test_d6_crash_after_partial_stream_is_ambiguous |
| checkpoint-in-stream before extract | recovery::test_d6_crash_checkpoint_in_stream_before_extract_is_ambiguous |
| (control) reconciled unit is SAFE, not AMBIGUOUS | recovery::test_d6_reconciled_dispatch_is_not_ambiguous |
| Codex forwarding boundary (cross-process) | loop::CrossProcessForwardResumeD10Tests (3 tests) |
| BEFORE verdict persistence | next_task::test_crash_BEFORE_verdict_persistence_re_obtains_no_double_advance |
| AFTER verdict persistence | next_task::test_crash_AFTER_verdict_persistence_never_re_advances |
| BEFORE campaign advancement | next_task::test_crash_BEFORE_campaign_advancement_loses_no_work |
| AFTER campaign advancement | next_task::test_crash_AFTER_campaign_advancement_is_exactly_once |
| between-cycle owner intent | loop::BetweenCycleIntentStopTests |

## 6. R388 simulation evidence

next_task::ConsecutiveAdvancementTests::test_three_consecutive_advancements_exactly_once_each drives
three consecutive simulated bounded advancements (M0-T200 -> M0-T201 -> M0-T202) with NO human
intervention: advance_and_select records each advancement exactly once (newly_recorded True the first
time), selects the next un-advanced packet, and terminates at NO_ELIGIBLE_WORK. No duplicate (each
is_advanced exactly once), no lost work (order M0-T200, M0-T201, M0-T202), no false acceptance (a
contradictory checkpoint id for an already-advanced task loses the CAS and returns the stored fact).
The crash-at-boundary case is proven by two nodes:
next_task::ConsecutiveAdvancementTests::test_crash_AFTER_campaign_advancement_is_exactly_once and
next_task::ExactlyOnceAdvancementTests::test_advancement_survives_a_crash_restart_without_doubling -
advance A, CRASH (reopen the durable journal), re-run advance_and_select for A -> newly_recorded
False and B is selected (exactly-once across the boundary).

## 7. D5 must-have + D3 must-have (explicit)

- D5: fixtures/m0t107_stream_d5.json (derived byte-faithfully from the preserved transcript's real
  final usage: input 2 + cache_creation 3962 + cache_read 67935 + output 647 = 72546 live; terminal
  result event carries the cumulative 694251). live_context_tokens returns 72546; inspect_stream
  cumulative returns 694251; recorded separately; _ceiling_context_tokens consumes the live figure;
  adversarial case at exactly 400000 flags.
- D3: the same fixture replays the preserved 12/12 exhaustion; extract_checkpoint raises
  missing_checkpoint (the old fixed-bound design's honest failure), and the new sized budget (33 >
  12) with a reserved final turn is what prevents the starve.

## 8. Residual limitations

- NO register defect is deferred: all 17 (D1-D17) are corrected at this identity.
- Property 3 (G3-2) scope: the reserved-final-turn demand is injected as a real follow-up user turn on
  the provider's stdin channel (run_unit extra_turns), delivered up-front and processed after the
  primary prompt's working turns - it OCCUPIES the reserved turn and forces the emission demand. With
  the `--max-turns` streaming model the supervisor cannot HARD-block a worker from spending a turn on a
  tool call, so this is enforcement "wherever technically enforceable" (the amendment's exact wording),
  strictly stronger than the prior prompt-text-only reservation; the fail-closed exhaustion net
  (missing_checkpoint -> PAUSED_RECOVERY, TurnExhaustionReplayTests) remains the backstop and is
  unchanged.
- The ~3h13m R247 recertification (test_agent_supervisor_golden_run.py's slow recert) was NOT run
  in-window; the packet assigns it to M0-T127 (budget note O2). Every FAST golden_run class passes
  (27 tests).
- Modularity ceilings: claude_runner.py (1383/1383) and cli.py (2953/2953) remain at their EXACT
  baseline+10% limit (0 headroom); the remediation kept both net-zero - the rotated-orientation and
  reserved-turn logic went into orientation.py / turn_budget.py / loop_turnover.py and loop.py (2034/
  2088, 54 headroom). The cli._turn_budget wiring was appended to an existing SupervisedLoop argument
  line (net-zero physical SLOC). A future substantial change to claude_runner.py/cli.py will still need
  a reviewed tools/modularity_exceptions.json entry or a decomposition (that file is not in this task's
  allowed_paths).
- D6 uses the "journal a dispatch-intent -> AMBIGUOUS_EFFECT" option (not the "commit CLAUDE_RUNNING
  at launch" option); both are register-sanctioned. The classify branch is ADDITIVE (fires only on an
  unreconciled intent), so no existing crash/recovery test changed behavior.
- The D4 append-only note on M0-T107-amendment20-live-journey-2.md is the ORCHESTRATOR's job per the
  packet and was not touched.
- runner: Any in SupervisedLoop is intentional structural typing (the loop is tested with FakeRunner
  and rebinds via with_model/getattr); it is deliberately not narrowed to ClaudeRunner.

## 9. Preservation and prohibitions (R374/R375)

The live runtime dir (%LOCALAPPDATA%\NYCBuildabilitySupervisor\) and journal were never opened; the
sqlite journal was not read. All fixtures were derived from the orchestrator-staged verbatim COPIES and
the readable preserved transcript, scanned for secrets (repo is PUBLIC; no sk-/ghp- tokens found;
absolute paths acceptable). For the G3-3 section-1 digest regeneration the two PROTECTED CONFIG files
(C:\Program Files\SupervisorConfig\config.toml and C:\SupervisorController\model_selection.toml) were
READ (bytes only, to recompute SHA-256) - these are NOT the runtime dir and the read is read-only; no
config was modified. No live launch, no supervisor CLI write verb, no clear-recovery, no restart, no
repin, no PR #241 touch, no policy weakening, no owner-gate change, no R595/bounded-mode gate change.
The G3-2 reserved-turn injection adds a follow-up user turn to run_unit but changes NO gate, owner
approval, or exhaustion-safety behavior. D7's fix is presentation/annotation only (epilogue text + a
documentation comment) and changes no gate behavior; D6's classify branch is additive and fires only on
an unreconciled dispatch intent.
