# M0-T125 — G3 report (independent code-reviewer, read-only) — VERBATIM agent return (transport entity-decoding only)

I have completed all required verifications. Compiling the G3 gate report.

---

# G3 GATE REPORT — M0-T125 (pre-code call-graph + ten-class defect register)

Reviewer: independent G3 (code-reviewer role, read-only). Reviewed identity: HEAD `9a48ee6` (evidence commit `915d73d`). Producer-analyzed identity: `13cd5973`. I confirmed by `git diff --stat 13cd5973 HEAD` that **no `tools/agent_supervisor/**` production source changed** between the analyzed and reviewed identities — only the two report files, the evidence-map JSON, `state.json`, and the task file. Every `file:line` citation therefore resolves identically at HEAD. Pure-import introspection confirmed the state machine has **29 states / 94 edges / 76 triggers**, matching the report's header. The task changed no handwritten production code (two new `.md` deliverables under `path_free_governance`), so the modularity seven-answer check is N/A.

## (a) VERDICT: PASS (with a numbered advisory-corrections list)

All 17 defects reproduce against the cited source; all 7 unreachable-DEFECT reachability claims reproduce under my own trigger sweep; the §C.2 command re-derivation and its five silent defaults reproduce against the live parser/seam contract; the D4 seed-c refutation is confirmed in both code and the preserved transcript; and the four spot-checked clean-list items are genuinely clean. I found **no missed in-scope defect** and no refuted claim. The analysis is sound and correctly feeds M0-T126. The corrections below are immaterial line-number/attribution nits that do not invalidate any finding; I record them so M0-T126 carries accurate citations.

Advisory corrections (non-blocking):
1. D9 / §B row 39: the `decision_complete` transition call is at loop.py:**2041-2042** (report says 2041 — the trigger literal is on 2042). Immaterial.
2. D5: the cumulative value **604,772** is recorded at audit **seq 21** (the unit); the `rotation_pending_flagged` event is **seq 24**. The report attributes "604,772 (seq 24)"; the number originates one unit earlier. Substance (rotation fired because 604,772 ≥ 400,000) is correct.
3. D3: I measured the first user prompt at **2,237** content chars vs the report's "2,176 chars"; both confirm ~2.2k = default `--prompt` + folded contract with zero orientation. Minor measurement variance.
4. D7: report enumerates the durable False-writers as "broker.py:702; remote_approvals.py:293/306"; the remote_approvals writes are at **295/307**, and there are additional False/`display`-only occurrences (loop.py:486 `to_dict`, cli.py:2941 `payload`) that are report-serialization dicts, not journal writes. The core claim (no durable True-writer ⇒ `safe_auto_resume` dead) stands.

## (b) D1–D17 confirmation table (own evidence)

| ID | Verdict | My one-line evidence |
|---|---|---|
| D1 | CONFIRMED | Parser has zero argparse-required `start` args (all defaults, cli.py:3223-3262); §5 command carries 5 silent defaults (re-derived in (d)); systemic root = presented commands not derived from arg/seam contract. |
| D2 | CONFIRMED | cli.py:2642 `repo = Path(args.repo or checkout).resolve()`; repo binds `EvidenceCollector` (2705), `CodexReviewer(repo=…)` (2701), `production_task_authority(repo_root=…)` (2662) — all to the primary checkout when `--repo` absent. |
| D3 | CONFIRMED | `--max-turns` default 12 (cli.py:3256), `max_turns:int=12` (claude_runner.py:306); preserved transcript = 36 assistant events ALL `stop_reason:tool_use`, only Glob/Grep/Read, no `checkpoint_id` emitted; `workload_sizing`/`workload_classifier` not wired into the loop path. |
| D4 | CONFIRMED (seed c REFUTED as stated) | `native_tools_appended` computed at claude_runner.py:1205 AFTER `with_checkpoint_contract` (1200); contract text folds `NATIVE_TOOLS_GUIDANCE` (line 931) which carries the sentinel (896), so flag is always False on a fresh prompt though guidance IS present. Transcript first user event (idx 4) contains BOTH sentinels; audit records `native_tools_guidance_appended:false` (3×). |
| D5 | CONFIRMED | Audit seq 50 `context_tokens=694,251`; transcript peak per-event live sum = **72,546** (2+67,935+3,962+647). ~9.6× overcount consumed as live context by rotation flag (fired seq 24) and `evaluate_ceiling` at every resume. |
| D6 | CONFIRMED | Audit ordering `claude_unit_completed` BEFORE `claude_process_started` at seq 8→9, 21→22, 40→41, 50→51; transition committed post-`run_unit` (loop.py:1620-1625); durable state rests at START_CLAUDE for whole unit ⇒ B-018 re-dispatch hazard. |
| D7 | CONFIRMED | recovery.py:349 gates on durable `limited_auto_enabled`; safe_auto_resume branch (358-362, resume_permitted=True) reachable only if flag True; all durable writers write False (broker.py:702; remote_approvals.py:295/307; cli.py:1529/1675/2437). Dead code, correct under R595 but undocumented. |
| D8 | CONFIRMED (HIGH) | loop.py:2035 enters PREPARE_ROTATION then `return stop("rotate_session",…)`; no exit trigger has a caller (sweep below); PREPARE_ROTATION ∉ CYCLE_ENTRY_STATES (loop.py:181) ⇒ next start raises bad_cycle_entry_state; ROTATE_SESSION is schema-legal ⇒ one verdict permanently strands. |
| D9 | CONFIRMED (HIGH) | loop.py:2041 enters COMPLETE then stops; `run_closed` has zero callers; COMPLETE ∉ CYCLE_ENTRY_STATES; NO_ELIGIBLE_WORK triggers (`no_eligible_authorized_work`/`idle_recheck_due`) caller-less; no `next_task/select_next/next_packet` surface exists (grep empty). |
| D10 | CONFIRMED (HIGH) | Next-cycle prompt is the in-process local `prompt = result.forward.sent_prompt` (loop.py:2691); run() resumes only FORWARD_PROMPT (loop.py:2628), no CLAUDE_RUNNING branch; `unsent_outbound()` returns only unsent rows (durable_state.py:616) so a SENT row is never re-read; start_index resets to 1 (loop.py:2605). |
| D11 | CONFIRMED | Between-cycle gates are only `_budget_stop()` (loop.py:2658) + rotation seam (2702); EMERGENCY_STOP_KEY read only inside `_resume_approved_forward` (loop.py:2485); no `stop_intent` import in loop.py. |
| D12 | CONFIRMED | GRACEFUL_STOP_KEY written stop_intent.py:87/104, read only in stop_intent.py:65 (`effective_intent`); `effective_intent` imported/called only by operator_status.py:134 (display); GRACEFUL_STOPPING edges caller-less; not in loop or recovery blocking-reasons. |
| D13 | CONFIRMED | `budget_ledger.start()` at cli.py:2726 runs in `_run_loop` BEFORE run_cycle's `assert_can_act`; `classify` never reads `current_state` (recovery.py:290-362); live seq 32-33 = run_budget_started against HALTED then loop refused. |
| D14 | CONFIRMED | `dispatch_inputs_missing` lists exactly six inputs (start_gate.py:424-434), `--worktree` absent; argparse requires nothing for start; missing `--worktree` on a packet-declaring launch refused by deeper seam (exit 11 unsafe) not the missing-inputs listing (exit 13). |
| D15 | CONFIRMED (code-side); digest VALUES UNVERIFIED by me | Structural claim reproduces: RunbookHygieneTests (test_agent_supervisor_manifest_binding.py:491-528) only checks PowerShell hygiene, never re-derives digests; I did not open CONTROLLER_UPDATE_RUNBOOK.md to compare the specific stale digest hex — see (g). |
| D16 | CONFIRMED | (i) seq 48 `over_ceiling_session_shed` with `context_tokens:null, known_over_ceiling:false` — shed keyed on leftover flag alone; `evaluate_ceiling` REFUSES unknown telemetry (launch_seam.py:289-294) so bounded exposure. (ii) determined-dead child records cleared only by launching runner's settle (no GC) — fail-safe noise. |
| D17 | CONFIRMED | No test parses presented command docs against parser/seam; launch_seam tests (64) cover refusal codes, bounded_mode tests (91) drive cmd_start with named inputs; the only runbook-reading test checks caret/placeholder hygiene, not arg completeness. |

## (c) XD reachability sweep (my own grep results)

Sweep: `grep` each trigger literal across `tools/agent_supervisor/`, excluding `state_machine.py` (definition) and `__pycache__`. Zero production `machine.transition(...)` caller ⇒ XD confirmed.

| Edge | Trigger | My sweep result | Verdict |
|---|---|---|---|
| 14 | `claude_start_failed` | zero matches anywhere but state_machine.py + its pyc | CONFIRMED XD |
| 44 | `handoff_generated` | zero matches | CONFIRMED XD |
| 45 | `unsafe_rotation_point` | one match, rotation.py:645 — a `RotationError(...)` string argument, NOT a transition (read confirmed) | CONFIRMED XD |
| 64 | `graceful_stop_intent_set` | zero matches | CONFIRMED XD |
| 65 | `recovery_finds_graceful_stop` | zero matches | CONFIRMED XD |
| 92 | `run_closed` | zero matches | CONFIRMED XD |
| 93-source | `owner_emergency_stop` never a transition trigger (only in interrupt-permission lists: cli.py:905, policy.py:88, rotation.py:457); `grep 'transition(.*EMERGENCY_STOPPED'` in loop/cli/recovery = empty ⇒ EMERGENCY_STOPPED is never entered; yet `owner_explicit_restart` wires EMERGENCY_STOPPED→IDLE at restart_channel.py:384 | CONFIRMED — edge is R-as-code, source state unenterable |

I also independently confirmed the register's live-reachability (R) citations against the preserved audit: edges 1 (seq 2/37), 9 (4/20/39/49), 13 (9/22/41/51), 15 (23), 19 (10/42/52), 23 (25), 26 (26), 29 (28), 33 (29), 41 (30), 61 (15/44), 94 (34) all appear with the stated from→to/policy_result. This cross-check gives high confidence in the whole reachability table.

## (d) §C.2 presented-command re-derivation

Parser defaults read from cli.py: `--checkout` default = `str(Path.cwd())` (3175); `--repo` default None → `repo = args.repo or checkout` (2642); `--worktree` default None → `worktree = args.worktree or repo` (2643); `--branch` default None → authority `branch=args.branch or ""` (2663); `--stage` default None → `stage=args.stage or packet.get("status")` (2663); `--max-cycles` type int default **1** (3254); `--max-turns` default 12 (3256); `--unit-timeout` default 900.0 (3258).

- §4 item 1 `clear-recovery --checkout ctl24` → **MATCH** (valid verb; `--checkout` is a common arg).
- §4 item 2 `start …` (no `--worktree`) → **DRIFT confirmed**: parser accepts (zero required start args) but `evaluate_packet_worktree_binding` (cli.py:2652-2656) raises LoopError `cwd_primary_checkout` (launch_seam.py:256-261) when the packet declares a worktree and the bound one is the primary checkout. Superseded by §5.
- §5 corrected (`+ --worktree wt-m0t107`) → **DISPATCHABLE with five silent defaults, all re-derived**:
  1. no `--checkout` → journal/runtime addressed by cwd (3175) + run_id `run_{checkout_key(checkout)[:12]}` (2664) is cwd-derived — CONFIRMED.
  2. no `--repo` → repo=checkout; evidence/Codex-`-C`/TaskAuthority bind to primary checkout (D2) — CONFIRMED.
  3. no `--branch` → `branch=""` (2663), branch probe unpinned — CONFIRMED.
  4. no `--stage` → falls back to `packet.status` (2663) — CONFIRMED.
  5. no `--max-cycles` → 1 (3254), single unit ⇒ multi-unit depends on cross-start continuation (D10) — CONFIRMED.

All five silent defaults reproduce exactly as the register states.

## (e) D4 seed-c refutation check

Code half: confirmed the flag is computed after the contract append and the contract embeds the native sentinel (see D4 row + (b)). Transcript half: the first user event is at line index 4 (indices 0-3 are `queue-operation`/attachment scaffolding); its content is 2,237 chars and contains BOTH `CHECKPOINT CONTRACT (S8.3)` and `NATIVE-TOOL PREFERENCE (D-024-R294)` plus the default prompt line. Audit records `native_tools_guidance_appended:false` (3×) with `checkpoint_contract_appended:true` (4×). Therefore the flag is degenerate and the guidance WAS delivered — seed c is correctly REFUTED as stated, and the append-only correction to journey-2 §5 (the +12-line diff at HEAD) is warranted.

## (f) Clean-list spot-checks (items 1, 2, 3, 12)

- Item 1 (launch_seam.py) — CLEAN confirmed: `evaluate_cwd` folds Windows path forms via `same_path` and names the primary-checkout case specifically (254-266); `evaluate_ceiling` uses exact-at-ceiling `>=` (296) and REFUSES unknown telemetry (289-294); `enforce_launch` is the single routed decision (305-323); pre-Popen call is unconditional (claude_runner.py:1224-1235).
- Item 2 (in-process exactly-once forwarding, loop.py:2388-2436) — CLEAN confirmed: enqueue → on `duplicate_outbound` resume the unsent row's own bytes (2414-2422) or `duplicate_suppressed` if already sent (2411-2413); `mark_sent` only after the row exists (2429). D10 is correctly scoped to the CROSS-process boundary only.
- Item 3 (`extract_checkpoint`, claude_runner.py:725-780) — CLEAN confirmed: `conflicting_duplicate_checkpoint` refused (755-759), `multiple_distinct_checkpoints` refused rather than last-wins (762-771), `missing_checkpoint` never treated as success (745-749).
- Item 12 (bounded-mode gate, start_gate.py:61-91) — CLEAN confirmed: refuses both directions by name — mode-without-enable (`limited_auto_not_enabled`, 73-81) and enable-without-gated-mode (`owner_enable_without_gated_mode`, 82-90).

## (g) Coverage gaps / new defects / UNVERIFIED

Coverage assessment against the Amendment-22 journey (launch, orientation, checkpoint emission, Codex review, verdicts, exactly-once advancement, next-task selection, rotation, recovery, multi-unit): every seam is addressed by at least one defect or a clean-list finding. Notably, the register correctly isolates the **only two** POLICY_CHECK verdict targets that lack any operator exit (PREPARE_ROTATION/D8, COMPLETE/D9) while HALTED (owner-restart, edge 94) and PAUSED_RECOVERY (clear-recovery, edge 61) remain recoverable — I verified those exits exist. I found **no missed in-scope defect** within the ten classes.

Minor observations (already substantially covered, not new defects): (a) the run-BUDGET identity is also cwd-derived via `run_id` (cli.py:2664/3244-3250), so a wrong-directory invocation silently starts a fresh budget rather than resuming — folded into D1's "different runtime and run id"; (b) checkpoint-design property R378 (reserved emission turn) has no current mechanism at all — folded into D3's correction. Neither warrants a separate register row.

UNVERIFIED (read-only limits, with reason):
1. **D15 specific digest hex values** (`6aef12a9…`/`A1F99501…`, `0e2432c0…`/`FCBBF70F…`) and §11 stale identities — I did not open `docs/CONTROLLER_UPDATE_RUNBOOK.md` or the M0-T113 report to byte-compare digests; I confirmed only the code-side structural claim (the runbook-reading test checks hygiene, not arg/digest correctness). D15 is LOW/presentation and does not gate M0-T126's code design.
2. **The exit-11 live refusal text** in `M0-T107-amendment20-start-refusal.md` and the exact §4/§5 wording of `M0-T124` — I did not open those report files; instead I independently verified the CODE that produces exit-11 (`evaluate_cwd`→`CWD_PRIMARY_CHECKOUT`, raised at cli.py:2655-2656) and re-derived §C.2 from the live parser. The mechanism is confirmed; the quoted report prose is trusted, not reproduced.
3. **Live runtime behavior** — not executed (supervisor CLI prohibited, R374/R375). All live claims were verified against the preserved `audit.jsonl` (53 records) and transcript (97 events) read as plain files, which fully corroborated the numeric/ordering claims.

These UNVERIFIED items are documentary/presentation-tier and do not affect any HIGH/MEDIUM code-side defect that drives the M0-T126 implementation.

---

Report file paths reviewed (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T125-callgraph-and-transitions.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T125-defect-register.md`

**G3 verdict: PASS** (analysis reproduces in full; four advisory citation corrections listed; no defect refuted, no in-scope defect missed).
