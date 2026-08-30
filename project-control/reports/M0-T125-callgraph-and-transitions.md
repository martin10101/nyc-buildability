# M0-T125 — Launch-to-next-task call graph, complete transition inventory, and operating surfaces (D-024-R383)

Producer: supervisor-stabilization-surveyor (read-only analysis spawn; report content returned to
the orchestrator for capture — the readonly_agent_guard denies file writes to non-roster spawns).
Analyzed identity: HEAD 13cd59731561e02c51adddf662a1669c602466f4 (branch control/D-024-fable-codex-loop).
Preserved live evidence read as plain files only: audit.jsonl (53 records, runtime key 33dfa57d...) and
worker transcript 0835bb80-0f2e-451f-882d-0b37df6d77d5.jsonl (97 events). The sqlite journal was NOT
opened (D-024-R374). No supervisor subcommand was executed; the CLI parser was introspected by pure
import (`build_parser()`), which performs no I/O.

## A. The complete launch-to-next-task call graph (per-edge, file:line)

### A.1 `start` CLI entry -> pre-dispatch gate
1.  `cli.main` -> `build_parser()` (cli.py:3165) -> `cmd_start` (cli.py:2867).
2.  `cmd_start` -> `start_gate.bounded_mode_gate` (cli.py:2876; start_gate.py:61-91): limited-auto
    without `--owner-enable-bounded-auto` => typed refusal `refused_mode` exit 16, sealed by
    `seal_owner_gate_refusal` (start_gate.py:438-465) into the audit chain with no lock/journal.
3.  `_open_runtime` (operator_channel_cli.open_runtime, operator_channel_cli.py:38-45):
    runtime dir = `%LOCALAPPDATA%/NYCBuildabilitySupervisor/<sha256(checkout)>` via
    `durable_state.runtime_dir_for` (durable_state.py:94-105); NOTE `--checkout` defaults to
    `pathlib.Path.cwd()` (cli.py:3175) — the addressed journal is cwd-dependent.
4.  `SingleInstanceLock` (cli.py:2883) -> manifest verification `verify_manifest_with_config`
    (cli.py:2892-2905; absent `--manifest` => manifest_ok False) -> `journal.integrity_check()`
    (cli.py:2906) -> `audit.verify_chain()` (cli.py:2907).
5.  `start_gate.dispatch_inputs_missing` (cli.py:2908; start_gate.py:422-435): the six named
    dispatch inputs are `--claude-executable --codex-executable --task-packet --config
    --model-selection --manifest`. `--worktree` is NOT in this set (see defect D14).
6.  `start_gate.load_task_packet` (cli.py:2916; start_gate.py:130-138) ->
    `start_gate.live_revalidation` (cli.py:2918-2921; start_gate.py:141-232) ->
    `recovery_probes.run_live_probes` (recovery_probes.py:862-917): 12 probes; STEP_PROBES
    (recovery_probes.py:921-925) answer 9 of the 12 `recovery.REVALIDATION_STEPS`
    (recovery.py:232-245); FOLDED_PROBES `config_identity`/`surviving_children`/`shell_routing`
    (recovery_probes.py:936-937) are ANDed into `controller_manifest` and (limited-auto only,
    start_gate.py:228-231) `cli_capability_manifest`.
7.  `recovery.recover_boot` (cli.py:2926; recovery.py:475-536): lock -> `account_for_children`
    (recovery.py:155-178) -> `pending_effects` -> `classify` (recovery.py:290-362). The
    classification NEVER takes a state-machine transition (no `machine.transition` exists in
    recovery.py) and never reads the journal's `current_state` — a HALTED journal classifies
    SAFE_CHECKPOINT (proven live: audit seq 32 at a HALTED journal).
8.  Gate ladder in `cmd_start` (cli.py:2963-3017): missing inputs -> `stale_state` exit 13;
    unreadable packet; classification != SAFE_CHECKPOINT -> `recovery_refusal`;
    `safe_but_forbidden`/`deadline_restored` + `deadline_blocks_dispatch` (start_gate.py:282-314);
    containment precondition (cli.py:2933, containment_precondition cli.py:2462) -> exit on
    non-job-object hosts. Only then `_run_loop` (cli.py:3027).

### A.2 `_run_loop` assembly (cli.py:2638-2864)
9.  Packet load (2641); `repo = args.repo or checkout` (2642); `worktree = args.worktree or repo`
    (2643); **launch-seam packet binding** `launch_seam.evaluate_packet_worktree_binding`
    (2652-2656; launch_seam.py:201-231) — refuses `cwd_primary_checkout` / `cwd_mismatch` when the
    packet declares a worktree and the bound one differs (the live 2026-08-30 exit-11 refusal).
10. Config/selection load + cross-validate (2657-2659); `production_task_authority` (2661,
    2617-2635: documented_test_commands wired); run_id default `run_<checkout_key[:12]>` (2664);
    `StateMachine` (2665); IDLE->PREFLIGHT `start_command` ONLY when state == IDLE (2670-2672).
11. `RunnerConfig` (2685-2693): cwd=worktree, `expected_worktree`=worktree,
    `primary_checkout`=checkout, max_turns=args.max_turns (default 12), timeout=args.unit_timeout
    (default 900). `ClaudeRunner(..., journal=journal)` (2699) — child pid accounting live.
12. `CodexReviewer` (2700-2704: repo=str(repo), schema codex_decision.schema.json, timeout =
    args.unit_timeout); `EvidenceCollector(repo_root=str(repo))` (2705); `CircuitBreakers`
    (2707); `RunBudgetLedger(...).start()` (2717-2726) — durable, BEFORE the loop's state gate
    (defect D13); `ResourceSampler` (2735); `ApprovalBroker` (2743); `RotationThresholds` (2749,
    rotation.py:112 default 400_000); orchestrator-role launch probe (2761-2771, worker role gets
    none); worker-turnover channel (2776-2786); `GuardrailBridgeIntegration` (2796-2805);
    `SupervisedLoop` (2807-2863; note: `head_sha`/`origin_main_sha` are NOT passed — default "");
    finally `loop.run(args.prompt)` (2864).

### A.3 One cycle (`SupervisedLoop.run_cycle`, loop.py:1455-2220)
13. `_guard` = `machine.assert_can_act` (1512; state_machine.py:533-539: blocked in
    WAIT_FOR_OWNER/PAUSED_RECOVERY/EMERGENCY_STOPPED/HALTED).
14. Entry-state check vs CYCLE_ENTRY_STATES = {PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING}
    (1516-1522; 181). Breakers: supervisor_cycles_per_task (1527), resource gauges (1537),
    PREFLIGHT->START_CLAUDE `preflight_pass` (1546), claude_runs_per_task (1550),
    model_calls_per_task/day (1568).
15. **Worker unit**: `runner.run_unit(prompt, permission_handler=...)` (1585-1586).
    Inside run_unit (claude_runner.py:1175-1480):
    - contract append: `contract_appended = CHECKPOINT_CONTRACT_SENTINEL not in prompt` (1199);
      `with_checkpoint_contract` (1200; contract text 906-934 INCLUDES the folded R294 native
      block at 931); `native_tools_appended = NATIVE_TOOLS_SENTINEL not in prompt` computed
      AFTER the contract append (1205) => always False on a fresh prompt (defect D4);
    - `build_argv` (1207; 348-391: `-p --input-format/--output-format stream-json --verbose
      --max-turns N --permission-mode manual --permission-prompt-tool stdio [--model M]
      [--resume ID only if capability verified]`);
    - **pre-Popen launch seam, unconditional** (1224-1235; launch_seam.enforce_launch 305-323:
      cwd binding 234-266, ceiling 269-302 — ROTATE/REFUSE both surface as RunnerError here);
    - `Popen` (1261) inside a Job Object container (1260, adopt 1266);
      `_record_launched_worker` journals (pid, start_token) BEFORE any byte is written
      (1271, 1482-1545: unwritable record => kill + refuse, orphan-live named honestly);
    - stdio loop (1313-1356): first user turn + extra turns; per-event session-id first-wins with
      conflict detection (1335-1342); `control_request` answered via broker handler (1343-1348,
      broker_permission_handler 1846-1905); unit ends when every written turn has its terminal
      `result` (1349-1356); stdin close + 30 s grace (267, 1384) else `graceful_close_failed`;
      wall watchdog 900 s tree-terminates (1280-1297);
    - `_settle_worker_record` clears the child record ONLY on a verified exit (1421, 1547-1568);
    - `extract_checkpoint` (1425; 725-780: exactly ONE checkpoint; conflicting duplicate and
      multiple distinct ids REFUSED, never chosen between);
    - `inspect_stream` (1437-1439; 689-722): model verification on every event + context_tokens =
      PEAK per-event sum of every `*token*` field — the CLI's cumulative terminal `result` usage
      wins, so the number is cumulative usage, not live context (defect D5);
    - `_audit_run` appends `claude_unit_completed` (1479, 1600-1629) — i.e. BEFORE the loop's
      claude_process_started transition below (defect D6).
16. Session persistence (loop.py:1594-1608): `sc.record_provider_session` with
    context_tokens/usage_known; ambiguous id => dropped + cleared (1609-1619).
17. START_CLAUDE->CLAUDE_RUNNING `claude_process_started` committed AFTER run_unit returns
    (1620-1625) — the durable journal rests at START_CLAUDE for the entire unit.
18. Not-OK unit (1627-1731): pending external effects -> PAUSED_RECOVERY `ambiguous_effect`;
    worker-turnover seam (1685-1700); guardrail seam (1708-1725); else PAUSED_RECOVERY
    `no_valid_checkpoint` (1726-1731) — the live counted stop (audit seq 52/53).
19. Containment enforcement (1748-1799): degraded or unverified-in-job => PAUSED_RECOVERY.
20. CHECKPOINT_RECEIVED `valid_checkpoint_received` (1801-1805); no-progress breaker on repeated
    checkpoint id (1815-1831); rotation flagging `_flag_rotation_if_needed` (1851; 931-968:
    context_tokens >= threshold => durable rotation_pending + reason, S11.2 flag-only).
21. Post-rotation gates (1866-1872; loop_turnover.post_rotation_gates 176-240: READY gate +
    successor-identity check, armed-gate fallback surviving a crash).
22. COLLECT_EVIDENCE `checkpoint_validated` (1875) -> `build_packet` via `_collect` (1879,
    2266-2279; evidence.py:334, bounds 16 KiB/section, 256 KiB/packet, evidence.py:44-47) ->
    CODEX_REVIEW `evidence_packet_built` (1893).
23. **Codex review**: per-checkpoint review breaker (1903), model-call breakers (1917),
    `reviewer.review(packet, expected_task_id, expected_checkpoint_id)` (1926-1928;
    codex_reviewer.py:489-583): fresh read-only process per attempt (argv 91-128:
    `exec -C <repo> -m <model> --ephemeral --ignore-user-config --strict-config --sandbox
    read-only --json --output-schema --output-last-message -`), <=3 attempts carrying the prior
    validation error, `validate_decision` (196-245: six decisions, per-decision required fields,
    unknown-field rejection, correlation to task+checkpoint id). Failure -> WAIT_FOR_OWNER
    `codex_unavailable_ask` (1943-1951).
24. **Verdict handling** (1953-2063): decision_received -> decision_schema_valid ->
    POLICY_CHECK; HARD_DENY/DENY_AND_HALT -> PAUSED_RECOVERY `deny_and_halt` (1988);
    DENY_AND_CONTINUE -> PREFLIGHT `cycle_closed` (2004); HALT_UNSAFE -> HALTED (2012);
    STOP_FOR_OWNER -> WAIT_FOR_OWNER (2022); ROTATE_SESSION -> PREPARE_ROTATION (2035, then the
    run STOPS — defect D8); COMPLETE -> COMPLETE (2041, defect D9); REVISE ticks
    consecutive_revision_loops (2056).
25. **Forwarding** (2078-2262): deterministic body `build_forwarded_prompt`
    (codex_reviewer.py:663-700), approval digest (2092; pending_prompt.approval_digest);
    shadow records a ShadowPlan and closes the cycle (2096-2127); limited-auto takes `tier_auto`
    -> FORWARD_PROMPT -> `_send_forward` (2155-2167); supervised parks the prompt at
    WAIT_FOR_OWNER with the covered instruction (2170-2212). `_send_forward` ->
    `forward_exactly_once` (2329-2346) -> `_forward_outbox` (2378-2436): enqueue -> mark_sent;
    duplicate => `duplicate_suppressed`; crash-window unsent row is RESUMED with its own bytes.
    prompt_forwarded -> CLAUDE_RUNNING (2246).

### A.4 Multi-unit continuation, rotation, turnover (`run`, loop.py:2600-2750)
26. Budget restore + pre-check (2610-2621); FORWARD_PROMPT cross-process resume
    `_resume_approved_forward` (2628-2643; 2466-2586: emergency-stop check, last-trigger check,
    sealed-audit digest cross-check `verify_approved_digest_against_audit`, covered-instruction
    reconstruction, external-write breakers, exactly-once resume-forward).
27. **Pre-first-dispatch ceiling seam** `_rotate_over_ceiling_before_first_dispatch` (2653;
    970-1056): durable rotation_pending with a context-shedding reason OR known-over telemetry
    (via launch_seam.evaluate_ceiling) => shed the recorded session (clear continuity record,
    drop resume binding, consume flag, audit `over_ceiling_session_shed`) — live-proven audit
    seq 48 (fired on the flag alone: `shed_context_tokens: null`, `known_over_ceiling: false`,
    because the pre-T123 legacy continuity record carries no token key,
    session_continuity.py:148-160).
28. Cycle loop (2654-2738): budget between cycles (2658); shadow single-shot (2668); prompt
    handoff = `result.forward.sent_prompt` (2685-2691 — in-process only, defect D10);
    between-cycle rotation seam (2702-2732): `_rotate_at_seam` (1118-1233) — return-to-pinned
    probe, strict availability (pause `_pause_model_unavailable` 1235; orchestrator-role
    quota-exhausted chain walk `_switch_at_seam` 1284; chain exhausted `stop_chain_exhausted`
    loop_turnover.py:284) — then the FULL S11.3 turnover (`loop_turnover.full_turnover` 91-126:
    seam facts, safety state via `broker.owner_unanswered_asks`, `sc.decide_continuity`
    (session_continuity.py:289-354: resume only with positive same-model proof + verified
    capability + non-context-shedding reason; else reorientation naming a closed reason),
    `_seam.execute`, then ACTUATION `actuate_resume` (141-173, carrying ceiling telemetry into
    the runner) or session forgetting; `with_reorientation` (351-362) prepends the FULL handoff
    to the next prompt); restart_attempts breaker on relaunch (2717).
    Exhaustion of max_cycles => `stopped="max_cycles_reached"` (2737-2738), final state
    CLAUDE_RUNNING when the last cycle forwarded.

### A.5 Recovery / restart channels (cross-process)
29. PAUSED_RECOVERY -> PREFLIGHT: `clear-recovery` (cli.py:1848-1889, transition at 1877).
30. WAIT_FOR_OWNER (held prompt) -> FORWARD_PROMPT: `resume-pending-prompt` (cli.py:1892-2045,
    digest-bound, covered-instruction verification 1982-2004, transition at 2009,
    `approve_pending_prompt` keeps the bytes for a later start's forward).
31. WAIT_FOR_OWNER (question) -> PREFLIGHT: `resume-after-answer`
    (restart_channel.owner_answer_resume 325-341); HALTED -> IDLE: `owner-restart` (310-322);
    EMERGENCY_STOPPED -> IDLE: `acknowledge-emergency-stop` (token-confirmed). All share
    `evaluate_preconditions` (202-262: emergency flag, exact source state, open asks, pending
    effects, surviving children, recorded SAFE_CHECKPOINT classification with
    provider_identity_drift named separately) and `_fire_edge` (270-307) under the lock.
32. Durable flags (not transitions): `pause`/`resume` (cli.py:1814-1845), `stop [--clear]`
    (2048-2068), `emergency-stop` (2071-2100: terminates recorded children, cancels wakes, sets
    the flag, revokes remote approvals — it does NOT transition the state machine),
    `graceful-stop` (operator_channel_cli; writes stop_intent.GRACEFUL_STOP_KEY — consumed
    ONLY by operator_status display, defect D12).

## B. Complete state-transition inventory (state_machine.py:127-401 — 29 states, 94 edges)

Reachability legend: R = production caller exists (file:line); UD = unreachable by design on this
build (R595/shadow-only, or substituted by another mechanism, as documented in-table); XD =
unreachable-DEFECT (a needed edge with no caller — see the register).

| # | Edge (trigger) | Calling surface | Class |
|---|---|---|---|
| 1 | IDLE->PREFLIGHT start_command | cli.py:2671 | R (live seq 2, 37) |
| 2 | IDLE->RECOVER_BOOT discontinuity_detected | none — recover_boot() runs as a pre-dispatch FUNCTION (cli.py:2926) and never journals RECOVER_BOOT entry | UD (documented S11.5 shape; the state is never entered as a state) |
| 3-6 | RECOVER_BOOT-> PREFLIGHT / RECONCILE_EXTERNAL_EFFECT / PAUSED_RECOVERY / USAGE_LIMIT_WAIT (recovery_safe_checkpoint / recovery_ambiguous_effect / recovery_unsafe_or_drifted / recovery_restores_deadline) | recovery.py CLASSIFICATION_TRIGGER (64-68) NAMES them; no machine.transition call | UD (classification is advisory; gates enforced in cmd_start) |
| 7-8 | RECONCILE->PREFLIGHT effect_proven_reconciled; RECONCILE->PAUSED effect_unprovable | recovery.reconcile_effect (381-411) returns verdicts; no transition caller | UD |
| 9 | PREFLIGHT->START_CLAUDE preflight_pass | loop.py:1546 | R (live seq 4/20/39/49) |
| 10 | PREFLIGHT->PAUSED controller_integrity_failure | none (manifest failure refuses in cmd_start pre-transition) | UD |
| 11 | PREFLIGHT->WAIT preflight_requires_owner | none | UD |
| 12 | PREFLIGHT->HALTED preflight_fatal | none | UD |
| 13 | START_CLAUDE->CLAUDE_RUNNING claude_process_started | loop.py:1621 (post-unit — defect D6) | R (live seq 9/22/41/51) |
| 14 | START_CLAUDE->HALTED claude_start_failed | none (a Popen failure raises before any transition) | XD (crash-window START_CLAUDE strandable only via B-018 re-entry) |
| 15 | CLAUDE_RUNNING->CHECKPOINT_RECEIVED valid_checkpoint_received | loop.py:1801 | R (live seq 23) |
| 16 | CLAUDE_RUNNING->ROTATION_PENDING rotation_threshold_crossed | none — replaced by the durable rotation_pending FLAG (rotation.observe_mid_unit 497-519); the S7 state is dead | UD (flag substitution; note the state + edge 21/22 are dead weight) |
| 17 | CLAUDE_RUNNING->USAGE_LIMIT_WAIT usage_limit_notice | none | UD (limit signals classified fail-closed; no live-verified shape, claude_runner.py:201-224) |
| 18,22,51,58,62,67,71,76,79,83,90 | *->EMERGENCY_STOPPED owner_emergency_stop (11 edges) | none — cmd_emergency_stop (cli.py:2071) sets the durable FLAG without transitioning | UD (flag substitution; consequence: EMERGENCY_STOPPED is never ENTERED, so edge 93 can never fire in production) |
| 19 | CLAUDE_RUNNING->PAUSED unsafe_condition | loop.py:1553,1666,1691,1713,1726,1758,1790; loop_turnover.py:256 | R (live seq 10/42/52) |
| 20 | CLAUDE_RUNNING->HALTED unrecoverable_worker_failure | none | UD |
| 21 | ROTATION_PENDING->CHECKPOINT_RECEIVED unit_reached_terminal_checkpoint | none (state never entered) | UD |
| 23 | CHECKPOINT_RECEIVED->COLLECT_EVIDENCE checkpoint_validated | loop.py:1875 | R (live seq 25) |
| 24 | CHECKPOINT_RECEIVED->PREPARE_ROTATION rotation_pending_set | none (rotation runs at the run() seam without these states) | UD |
| 25 | CHECKPOINT_RECEIVED->PAUSED checkpoint_unsafe | loop.py:1823 (no-progress breaker), 1870 (post-rotation gates) | R |
| 26 | COLLECT->CODEX evidence_packet_built | loop.py:1893 | R (live seq 26) |
| 27 | COLLECT->WAIT evidence_incomplete_ask | loop.py:1881 | R |
| 28 | COLLECT->PAUSED suspected_secret_leak | none (packet build refuses internally) | UD |
| 29 | CODEX->VALIDATE decision_received | loop.py:1954 | R (live seq 28) |
| 30 | CODEX->USAGE_LIMIT_WAIT codex_rate_limited | none | UD |
| 31 | CODEX->WAIT codex_unavailable_ask | loop.py:1943 | R |
| 32 | CODEX->PAUSED unsafe_condition | loop.py:1905 (review breaker) | R |
| 33 | VALIDATE->POLICY decision_schema_valid | loop.py:1958 | R (live seq 29) |
| 34 | VALIDATE->CODEX decision_invalid_bounded_retry | none — the reviewer retries INTERNALLY (codex_reviewer.py:523-583) without state transitions | UD (mechanism substitution) |
| 35 | VALIDATE->HALTED decision_invalid_repeatedly | none — exhaustion surfaces as codex_unavailable_ask (loop.py:1935-1951) | UD |
| 36 | POLICY->FORWARD tier_auto | loop.py:2156 (limited-auto only) | R (not yet exercised live) |
| 37 | POLICY->WAIT tier_ask_blocking | loop.py:2022,2067,2170 | R |
| 38 | POLICY->PREPARE_ROTATION decision_rotate_session | loop.py:2035 | R — but the TARGET then strands (D8) |
| 39 | POLICY->COMPLETE decision_complete | loop.py:2041 | R — target strands (D9) |
| 40 | POLICY->PAUSED deny_and_halt | loop.py:1988 | R |
| 41 | POLICY->HALTED decision_halt_unsafe | loop.py:2012 | R (live seq 30) |
| 42 | POLICY->PREFLIGHT cycle_closed | loop.py:2004,2058,2118,2139 | R |
| 43 | FORWARD->CLAUDE_RUNNING prompt_forwarded | loop.py:2246, 2573 | R |
| 44 | PREPARE_ROTATION->VERIFY_HANDOFF handoff_generated | none | XD (D8: no exit from PREPARE_ROTATION exists anywhere) |
| 45 | PREPARE_ROTATION->PAUSED unsafe_rotation_point | none (rotation.py:645 is a record string, not a transition) | XD (part of D8) |
| 46-48 | VERIFY_HANDOFF exits (handoff_verified / handoff_rejected_retry / handoff_rejected_ask) | none (handoff.py:235 / cli.py:2337 are verification-record strings) | UD (state unenterable while 44 is dead) |
| 49 | START_FRESH_SESSION->CLAUDE_RUNNING new_session_ready | none | UD |
| 50,52 | USAGE_LIMIT_WAIT-> SCHEDULED_RESUME / PAUSED (durable_trigger_created / reset_time_unusable) | none | UD (resume_scheduler manages deadlines as durable keys, not states) |
| 53-55 | SCHEDULED_RESUME exits | none | UD |
| 56 | WAIT->PREFLIGHT owner_answer_validated | restart_channel.owner_answer_resume (325-341) | R |
| 57 | WAIT->FORWARD owner_approved_pending_prompt | cli.py:2009 | R |
| 59 | WAIT->COMPLETE owner_closed_stage | none | UD |
| 60 | WAIT->HALTED owner_halt | none | UD |
| 61 | PAUSED->PREFLIGHT owner_cleared_pause | cli.py:1877 | R (live seq 15/44) |
| 63 | PAUSED->HALTED owner_halt | none | UD |
| 64-68 | GRACEFUL_STOPPING family (graceful_stop_intent_set / recovery_finds_graceful_stop / graceful_stop_landed / +2) | none — graceful-stop writes the intent key; NOTHING consumes it (D12) | XD for 64/65 (the intent exists with no consumer); UD for the rest |
| 69-72 | AWAIT_CHILDREN family | none | UD (R595) |
| 73-76 | CODEX_OUTAGE_BACKOFF family (codex_transient_failure / outage_retry_due / outage_blocked_with_handoff / emergency) | none — transient Codex failure currently lands WAIT_FOR_OWNER via edge 31 | UD (mechanism substitution) |
| 77-80 | NO_ELIGIBLE_WORK family | none | UD (no task-selection machinery exists — see D9) |
| 81-91 | GUARDRAIL_BRIDGE / REPRESENT_FABLE families | none — refusal seam records intent only (loop.py:1708-1725) | UD (R595, documented at state_machine.py:74-84) |
| 92 | COMPLETE->IDLE run_closed | none | XD (D9 — a COMPLETE journal is permanently stranded) |
| 93 | EMERGENCY_STOPPED->IDLE owner_explicit_restart | restart_channel (acknowledge-emergency-stop) | R as code, but the SOURCE state is unenterable in production (see edges 18 et al.) |
| 94 | HALTED->IDLE owner_explicit_restart | restart_channel.owner_restart (310-322) | R (live seq 34) |

Totals: 26 R, 61 UD, 7 XD (14, 44, 45, 64, 65, 92, and the 93-source contradiction counted once).

## C. Operating surfaces

### C.1 CLI subcommands (introspected from `build_parser()`; argparse contract)
Common to every verb: `--checkout` (DEFAULT = invocation cwd — cli.py:3175), `--runtime-base`,
`--json`. Argparse-REQUIRED marked *.

| Verb | Own arguments |
|---|---|
| doctor | --config --model-selection --manifest --live --claude-executable |
| status | (common only) |
| replay | [fixture] --corpus --repo |
| start | --mode{shadow,supervised,limited-auto}=shadow --manifest --claude-executable --codex-executable --task-packet --config --model-selection --repo --worktree --branch --stage --run-id --prompt="Report a structured checkpoint for the current authorized stage." --max-cycles=1 --max-turns=12 --unit-timeout=900 --owner-touch-budget=2 --approve-prompt-digest[] --context-rotation-threshold --expected-worker-model --session-role{orchestrator} --owner-enable-bounded-auto --run-wall-clock-seconds --repin-cli-identity --require-remote-reachable --authorize-turnover-actuation. NOTE: argparse requires NOTHING; dispatch requires the six start_gate inputs + (packet-declared) --worktree at the seam. |
| orchestrator-watchdog | *--exhaustion-signal --orchestrator-launcher-arg[] --handoff-reference --safe-checkpoint-id --current-model --config --claude-executable |
| pending-approvals / revoke-all | (common only) |
| verify-controller | --manifest --config |
| record-manifest | *--config --out |
| pause / resume / clear-recovery / recovery-status / schedule-status / cancel-scheduled-resume / emergency-stop / export-handoff / owner-restart / resume-after-answer | (common only) |
| stop | --clear |
| graceful-stop | --reason --clear |
| ask | [question] --codex-executable --config --model-selection --window=90 --show --resubmit |
| resume-pending-prompt | *--approve-prompt-digest |
| approve-once / deny | *request_id *displayed_digest |
| acknowledge-emergency-stop | --acknowledge-emergency-stop --confirm-emergency-token |
| autostart-plan / install-autostart / uninstall-autostart | --kind{wake,boot} --launcher --launcher-arg[] --working-dir --at-utc (+install/uninstall: --confirm-plan-digest --xml-path --schtasks) |
| set-codex-model / set-claude-model | *model_name --config --model-selection --at-checkpoint |
| codex | nested verbs new/continue/show/promote/close (codex_channel_cli.py:167-221; provider args + --window; *text / *thread_id / *message_id) |
| telegram | nested verbs (telegram_sink_cli.register_telegram_verbs) |

### C.2 Owner-presented commands vs the parser/seam contract (argument-by-argument)
| Source | Command | Verdict |
|---|---|---|
| M0-T124 §4 item 1 | clear-recovery --checkout ctl24 | MATCH (proven live, seq 44) |
| M0-T124 §4 item 2 | start --mode limited-auto --owner-enable-bounded-auto --claude-executable --codex-executable --task-packet --config --model-selection --manifest | **DRIFT (proven):** parser accepts (zero argparse-required args) but the T123 seam refuses `cwd_primary_checkout` — no `--worktree` while the packet declares one. Superseded by §5. |
| M0-T124 §5 corrected | same + --worktree wt-m0t107 | DISPATCHABLE (proven live 19:35Z). **Residual silent defaults:** no `--checkout` (journal addressed = cwd — a different invocation directory silently addresses a different runtime/journal and derives a different default run id); no `--repo` (repo=checkout=ctl24: evidence git-facts, Codex `-C`, TaskAuthority repo_root bind to the PRIMARY checkout — defect D2); no `--branch` (branch probe unpinned, recovery_probes.py:142-165 passes any branch); no `--stage` (falls back to packet `status` = "claimed"); no `--max-cycles` (=1: single unit per start — multi-unit operation then depends on cross-start continuation, defect D10). |
| M0-T107-cycle2 (item-3 certified start, T113 era) | same shape as §4 (no --worktree) | Dispatched pre-T123; the SAME shape post-T123 refuses — the presented command was never re-derived after the seam change (systemic root of D1). |
| M0-T113 §1 items 10-12, §5 A3-A5, §6 steps 1-4 | record-manifest --config --out; verify-controller --manifest [--config]; doctor [--live --claude-executable] | MATCH. Note live practice stores the manifest OUTSIDE the repo (%LOCALAPPDATA%/ctl24-activation/), while runbook §5 writes it INSIDE the tree (drift D15). |
| Runbook §2/§9 | status / recovery-status / pending-approvals / stop --checkout <wt> | MATCH; the §2 warning about cwd-defaulted --checkout is accurate (cli.py:3175). |
| Runbook §9a table | clear-recovery / resume-pending-prompt --approve-prompt-digest / resume-after-answer / owner-restart / acknowledge-emergency-stop --acknowledge-emergency-stop --confirm-emergency-token | MATCH (restart_channel + cli surfaces exist with exactly these flags). |
| Runbook §11 | supervised start (full shape incl. --repo --worktree --branch --stage --run-id --max-cycles) | MATCH in shape; content stale (M0-T063-era identities/digests — D15). |

### C.3 Durable-state keys on the journey (journal `set_state`/`get_state` surfaces)
current_state, last_trigger (state_machine.py:440-441); claude_session_identity
(claude_runner.py:421); provider_session_continuity (session_continuity.py:51 — carries
context_tokens/usage_known since M0-T123; legacy records read token-unknown); rotation_pending +
rotation_pending_reason (rotation.py:446-451); job_size_class; pending_prompt/<run_id>
(pending_prompt.py:98); shadow_plan/<run>/<cycle>; model_substitution/<run_id> (loop.py:921);
session_handoff/<run_id> (loop.py:1079); launched_child_processes (recovery.py:72);
interrupted_turn_capability_probe, last_recovery_outcome (recovery.py:73-74); emergency_stop,
manual_pause, resume_not_before_utc (resume_scheduler keys); owner_gate_open, limited_auto_enabled
(recovery.py:70-71 — the latter has ONLY False-writers: broker.py:702, remote_approvals.py:293/306);
graceful_stop_intent (stop_intent.py:35 — display-only consumer); run-budget + breaker tallies
(run_budget ledger); outbox rows + asks + effects (durable_state.py:596-694, 506-584).

### C.4 Audit events observed on the live journey (audit.jsonl, seq order)
recover_boot; state_transition; run_budget_started/resumed; approval_deferred;
claude_unit_completed; owner_touch_recorded; approval_owner_denied; cli_identity_repinned;
rotation_pending_flagged; codex_review_decision; operator_owner_restart;
over_ceiling_session_shed. Ordering caveat: claude_unit_completed precedes the
claude_process_started transition for the same unit (seq 8/9, 40/41, 50/51 — defect D6);
`verify_chain` checks sequence/digest continuity only (audit_log.py:1-30), so the chain is intact
and no machine consumer reads cross-event timestamp order.

### C.5 Fixed bounds inventory (class-6 map: bound -> exhaustion behavior)
| Bound | Value / source | On exhaustion |
|---|---|---|
| max_turns | 12 (claude_runner.py:306; cli.py:3256) | CLI stops mid-work; missing checkpoint -> S14 counted stop -> PAUSED_RECOVERY (live-proven 12/12) |
| unit_timeout | 900 s (cli.py:3258) | watchdog tree-terminate -> timed_out -> S14 stop |
| close grace | 30 s (claude_runner.py:267) | graceful_close_failed -> not OK -> S14 stop |
| kill-reap wait | 10 s (claude_runner.py:276) | orphan-live refusal named honestly |
| max_cycles | 1 default (cli.py:3254) | stopped=max_cycles_reached at CLAUDE_RUNNING (feeds D10) |
| owner-touch budget | 2 (loop.py:150) | measurement only; excess -> owner disposition |
| review attempts | 3 (codex_reviewer.py:474) | schema_retry_exhausted -> WAIT_FOR_OWNER |
| review timeout | args.unit_timeout=900 (cli.py:2704; module default 600 unused there) | attempt discarded, rerun fresh |
| model probe timeout | 120 s (cli.py:314) | model unavailable (fail-closed pause) |
| breakers (cycles/runs/model-calls/writes/invalid/no-progress/revisions/restarts/reviews-per-checkpoint) | config.limits via CircuitBreakers | synchronous pause / cycle_closed, tallies durable across restarts |
| evidence bounds | 16 KiB section / 256 KiB packet (evidence.py:44-47) | truncation marked, oversize refused |
| wall clock | optional --run-wall-clock-seconds (no default/ceiling) | budget_exhausted between cycles only |
| rotation ceiling | 400,000 (rotation.py:112; launch_seam.py:55) | flag mid-unit; shed pre-dispatch; ROTATE/REFUSE at resume |
