# M0-T125 — G4 report (independent qa-engineer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

# G4 (QA) Gate Report — M0-T125

**Task:** M0-T125 — launch-to-next-task call graph, transition/surface enumeration, ten-class defect search (pre-code, D-024-R383/R384)
**Reviewed identity:** HEAD `9a48ee6` / evidence commit `915d73d` (reports self-declare analyzed identity `13cd5973`; see Observation O1)
**Reviewer:** qa-engineer (independent, read-only + read-only pytest)
**Artifacts under review:** `project-control/reports/M0-T125-callgraph-and-transitions.md`, `project-control/reports/M0-T125-defect-register.md`

---

## (a) VERDICT: **PASS** — with 4 numbered required corrections (blocking for M0-T126 coverage acceptance, NOT for M0-T125's own gate)

Every live-evidence citation reproduces exactly (0 mismatches). Every test-suite claim reproduces (64/91/42, both packs runbook-text-free, workload_sizing zero-consumer). All 17 defects carry real, spot-checkable `file:line` evidence and removal-sensitive test implications. The register is an accurate, load-bearing pre-code deliverable. The required corrections are R387-coverage gaps the register does not fully anchor; they must be carried into the M0-T126 test/coverage design so the sixteen-scenario minimum is actually reachable.

**Required corrections (carried to M0-T126):**
1. **Codex CONTINUE outcome (R387 scenario 5, "HALT and CONTINUE"):** only HALT_UNSAFE exists in the preserved artifacts (audit seq 27-30); the auto-forward edge (POLICY→FORWARD `tier_auto`, callgraph row 36) is "not yet exercised live." No defect anchors it. M0-T126 must synthesize a CONTINUE fixture (no preserved replay exists) with a removal-sensitive assertion.
2. **Duplicate and stale Codex verdicts (R387 scenario 6):** the register hooks *missing* (codex_unavailable_ask) and *malformed* (validate_decision unknown-field) verdicts, and notes verdict↔checkpoint-id correlation as Checked-and-CLEAN, but names **no** removal-sensitive scenario for a *duplicate* or *stale* verdict. M0-T126 must build fixtures around that correlation guard so it is proven removal-sensitive.
3. **Interruption matrix tail (R387 scenario 9):** D6 anchors crash-injection at three points (post-Popen, partial-stream, checkpoint-in-stream-before-extract) and D10 anchors the forwarding boundary, but "immediately before/after **verdict persistence**" and "before/after **campaign advancement**" have no dedicated hook (advancement does not yet exist — see D9). M0-T126 must add these interruption rows once next-task selection is implemented.
4. **Advancement-dependent scenarios (R387 scenarios 8, 10 and R388):** exactly-once task advancement, next-task selection/dispatch, and consecutive simulated advancements are all gated on D9's not-yet-existing machinery. The register acknowledges this for D9/R388; the correction is to make that dependency explicit for scenarios 8 and 10 too — they are **fresh implementation + fresh design**, not preserved-artifact replays.

None of these invalidate the register's accuracy; they are downstream coverage-design obligations, which is exactly what the task asked me to surface.

---

## (b) Live-evidence verification table (every claim, VERIFIED / MISMATCH + actual)

| # | Claim (source) | Result | Actual value observed |
|---|---|---|---|
| L1 | seq 48 `shed_context_tokens: null` | VERIFIED | `"shed_context_tokens":null` (seq 48) |
| L2 | seq 48 `known_over_ceiling: false` | VERIFIED | `"known_over_ceiling":false`; also `pending_flag_consumed:true`, `ceiling:400000`, shed sid `798d2f00…` |
| L3 | seq 50 `context_tokens: 694251` | VERIFIED | `"context_tokens":694251` |
| L4 | seq 50 `native_tools_guidance_appended: false` | VERIFIED | `"native_tools_guidance_appended":false` |
| L5 | seq 50 `checkpoint_contract_appended: true` | VERIFIED | `"checkpoint_contract_appended":true` |
| L6 | seq 50/51 ordering inversion (completed before started; started ts later) | VERIFIED | seq 50 `claude_unit_completed` ts 19:37:48.163Z precedes seq 51 `claude_process_started` (START_CLAUDE→CLAUDE_RUNNING) ts 19:37:48.178Z |
| L7 | seq 52/53 counted stop + touch | VERIFIED | seq 52 `unsafe_condition` CLAUDE_RUNNING→PAUSED_RECOVERY, reason `missing_checkpoint`; seq 53 `owner_touch_recorded` basis S14, `counted:true`, `no_valid_checkpoint` |
| L8 | seq 8/40 prior same-class stops | VERIFIED | seq 8 `claude_unit_completed` err `missing_checkpoint` (ctx 622599, 3 owner denies); seq 40 `claude_unit_completed` err `missing_checkpoint` (ctx 640224) |
| L9 | seq 32-33 budget-start against HALTED journal (D13) | VERIFIED | seq 32 recover_boot `SAFE_CHECKPOINT` (03:01:47.424Z); seq 33 `run_budget_started` key `run_budget/run_33dfa57d54db` started_at 03:01:47.433Z; no preflight/start follows until seq 34 owner-restart — a refused start that mutated durable budget |
| L10 | D6 journal-order inversion also at seq 8/9, 21/22, 40/41 | VERIFIED | 8(ts .667)<9(.683); 21(.912)<22(.932); 40(.656)<41(.668) — completed precedes started each time |
| T1 | transcript = 97 events | VERIFIED | 97 (assistant 36, user 23, attachment 23, atis-latch 7, last-prompt 6, queue-operation 2) |
| T2 | 36 assistant events | VERIFIED | 36 |
| T3 | ALL assistant stop_reason values | VERIFIED | all 36 = `tool_use` (no other value present) |
| T4 | exactly 12 distinct assistant message ids | VERIFIED | 12 distinct ids (msg_011CeZVd…→…GhdQb) → 12 turns = 12/12 max_turns |
| T5 | first user prompt = 2,176 chars | VERIFIED | len = 2176 |
| T6 | first prompt carries `CHECKPOINT CONTRACT (S8.3)` sentinel | VERIFIED | present (begins at char ~64) |
| T7 | first prompt carries `NATIVE-TOOL PREFERENCE (D-024-R294)` sentinel | VERIFIED | present (tail is native-tool guidance text) |
| T8 | final usage cache_read 67,935 + creation 3,962 + output 647 | VERIFIED | last assistant usage: cache_read_input_tokens 67935, cache_creation_input_tokens 3962, output_tokens 647 (sum ≈ 72,544 live vs 694,251 cumulative → substantiates D5) |
| T9 | D3 "tools Glob/Grep/Read only", no checkpoint JSON, ~2m24s | VERIFIED | tool_use: Glob 5, Grep 10, Read 7 (22, all read-only); 0 checkpoint-JSON markers in assistant text; span 19:35:22.293Z→19:37:46.890Z = ~2m24.6s |

**Live-evidence result: 19/19 VERIFIED, 0 MISMATCH.**

---

## (c) Test-run outputs

| Command | Register claim | Actual | Result |
|---|---|---|---|
| `python -m pytest tools/test_agent_supervisor_launch_seam.py -q` | 64 tests | `64 passed in 58.91s` | VERIFIED (64) |
| `python -m pytest tools/test_agent_supervisor_bounded_mode.py -q` | 91 tests | `91 passed in 12.10s` | VERIFIED (91) |
| `python -m pytest tools/test_agent_supervisor_golden_run.py -q` | passes (no count claimed) | `42 passed in 11616.50s (3:13:36)` exit 0 | VERIFIED (passes) |

Environment: Python 3.11.9 (all three packs collected and passed cleanly; no PEP-695 collection failure in these packs).

**Grep confirmations:**
- Neither `test_agent_supervisor_launch_seam.py` nor `test_agent_supervisor_bounded_mode.py` references `M0-T124`, `CONTROLLER_UPDATE_RUNBOOK`, `runbook`, `owner-presented`, or `M0-T107-amendment20` (0 matches each) → D17 claim "none reads M0-T124/runbook command text" VERIFIED.
- **D3 workload_sizing zero-consumers VERIFIED:** within `tools/agent_supervisor/*.py`, `workload_sizing` is imported by **no production module** (grep returned only `workload_classifier` imports). `workload_classifier` is imported by exactly `refusal_bridge.py:61`, `spawn_decision.py:30`, `startup_overhead.py:29`, `subagent_contracts.py:41` — the four modules the register names. `workload_sizing` is imported only by two **test** files (`test_agent_supervisor_bounded_contracts.py:37`, `test_agent_supervisor_runtime_supervision.py:48`) — i.e., the sizing machinery is unwired from the live launch/loop path.

---

## (d) Per-defect test-implication adequacy + R387 gap list

**Adequacy = does the stated test implication make the M0-T126 fix removal-sensitive?**

| Defect | Sev | Live/code re-verified | Test implication removal-sensitive? | QA note |
|---|---|---|---|---|
| D1 command-derivation drift | HIGH | via D14/D17 (dispatch set) | YES | command-document tooth fails on any doc↔parser drift; strong |
| D2 `--repo` primary-checkout leak | HIGH | code cited (cli.py:2642/2700/2705) | YES | replay fixture from preserved packet; adequate |
| D3 fixed 12-turn / sizing unwired | HIGH | **VERIFIED live** (12/12; workload_sizing 0 consumers) | YES | 12/12 replay must fail old design, pass new; strong |
| D4 degenerate native flag | MED | **VERIFIED live** (sentinel present, flag false) | YES | 3-shape assertion (fresh/old/pre-seeded); adequate; seed c correctly REFUTED |
| D5 cumulative vs live tokens | HIGH | **VERIFIED live** (694,251 vs ~72.5k) | YES | separate-recording + exact-400k adversarial; strong |
| D6 journal-order inversion / START_CLAUDE rest | MED | **VERIFIED live** (4 seq pairs) | YES | 3 crash-injection points; adequate (feeds scenario 9) |
| D7 dead `safe_auto_resume` | LOW | code re-verified (only False writers to durable key) | YES (golden epilogue assert) | minor line-offset 293/306→295/307 (identity diff); substance holds |
| D8 PREPARE_ROTATION strand | HIGH | **code re-verified** (loop.py:2035/2038 enter+stop; exits only defined in state_machine, no caller) | YES | adversarial ROTATE_SESSION → next start must dispatch; strong |
| D9 COMPLETE strand / no next-task selection | HIGH | **code re-verified** (`run_closed` only at state_machine.py:395, 0 callers; COMPLETE ∉ CYCLE_ENTRY_STATES) | YES | correctly flags R388 impossible until built |
| D10 forwarded-prompt loss / dup-id | HIGH | code cited | YES | cross-process resume + dup re-decision; adequate |
| D11 no between-cycle stop/pause read | MED | code cited | YES | flag-set-between-cycles must stop; adequate |
| D12 graceful-stop no consumer | MED | code cited | YES | mid-run + at-rest cases; adequate |
| D13 budget-before-gate | LOW/MED | **VERIFIED live** (seq 32-33) | YES | start-over-HALTED asserts zero budget mutation; strong |
| D14 argparse requires nothing | MED | code cited (dispatch set excludes --worktree) | YES | dispatch-required enumeration; joint with D1 |
| D15 runbook drift | LOW | doc-digest cited | YES (under D1 tooth) | adequate |
| D16 legacy durable records | LOW | (i) VERIFIED via seq 48 `shed_context_tokens:null` | YES | legacy-record fixtures; adequate, bounded |
| D17 no test consumes presented commands | MED | **VERIFIED** (both packs runbook-free) | YES | the tooth IS the removal-sensitive test |

All 17 test implications are removal-sensitive as stated. No defect's implication is inadequate.

**R387 sixteen-scenario reachability** (list read from source-022-amendment.md lines 86-114; 15 bullets + the R388 consecutive-advancements paragraph; "fresh + rotated" in bullet 1 supplies the 16th sub-scenario):

| R387 scenario | Anchored by | Reachable now? |
|---|---|---|
| 1 Fresh + rotated orientation | D3 (fresh); rotation/`with_reorientation` + D5/D16(i) (rotated) | Fresh: yes. Rotated-orientation *content* adequacy: partial (machinery exists, no defect) |
| 2 Consuming every working turn | D3 (12/12 replay) | YES |
| 3 Early/incremental/incomplete/final checkpoints | D3 (Amdt-22 items 1-5, R379) | YES (new design) |
| 4 Missing/malformed/duplicate/contradictory checkpoints | Checked-CLEAN #3 + live missing (seq 8/40/50) | YES |
| 5 Codex HALT **and CONTINUE** | HALT live (seq 27-30); CONTINUE = row 36 not exercised | **GAP → correction 1** |
| 6 Missing/malformed/**duplicate/stale** Codex verdicts | missing (edge 31), malformed (validate_decision); dup/stale unanchored | **GAP → correction 2** |
| 7 Codex review failure + success | Checked-CLEAN #5 + edge 31 | YES (success = HALT only live) |
| 8 Exactly-once task advancement | D9 (unimplemented) | Only after D9 fix → correction 4 |
| 9 Interruption before/after checkpoint, forwarding, **verdict persistence, advancement** | D6 (checkpoint), D10 (forwarding); verdict/advancement tail unanchored | **Partial GAP → correction 3** |
| 10 Next-task selection + dispatch | D9 (does not exist) | Only after D9 fix → correction 4 |
| 11 Rotation before provider contact | D5 / callgraph #27 (live seq 48) | YES |
| 12 Provider crash/refusal/quota/context/restart | D5 (context), D6/B-018 (restart), Checked-CLEAN #10, #28 (quota, orch-role) | YES (worker-role quota partial) |
| 13 Worktree isolation + primary-checkout refusal every path | D2, D14, Checked-CLEAN #1 (live exit 11) | YES (strong) |
| 14 Preserve audit/budgets/owner-gates/pending-effects | D13, Checked-CLEAN #8/#12, D11/D12 | YES |
| 15 Command-document validation | D1, D14, D15, D17 | YES (strong) |
| R388 consecutive advancements | D9 (impossible until selection exists) | Only after D9 fix → correction 4 |

**R387 GAP LIST (scenarios needing fresh design, not defect/replay-anchored):** scenario 5 CONTINUE outcome; scenario 6 duplicate/stale Codex verdict; scenario 9 tail (verdict-persistence and campaign-advancement interruption rows); scenarios 8/10/R388 (advancement + selection — implementation-gated). These are the exact items the task flagged as examples ("Codex verdict duplication/staleness, interruption matrix rows") and are captured in corrections 1-4.

---

## (e) R388 feasibility ruling: **CONFIRMED — infeasible on the reviewed identity (D9's claim is correct)**

Independently from the code at the reviewed tree:
- `CYCLE_ENTRY_STATES = frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})` (loop.py:181); the entry guard `if entry not in CYCLE_ENTRY_STATES:` raises (loop.py:1516-1519). **COMPLETE is not an entry state** → any start after COMPLETE refuses `bad_cycle_entry_state`.
- `run_closed` (COMPLETE→IDLE) exists **only as the edge definition** at `state_machine.py:395`; grep across the whole `tools/agent_supervisor` package finds **zero callers** in loop.py/cli.py/anywhere → a COMPLETE journal is permanently stranded.
- `decision.decision == "COMPLETE"` enters COMPLETE at loop.py:2040-2047; nothing thereafter closes the run.
- **No next-task/packet-selection surface exists:** no `next_packet` / ledger-walk / packet-selection code in the package; `start` binds exactly one `--task-packet`; the `NO_ELIGIBLE_WORK` family (state_machine.py:337/340; outage_policy dwell) is an idle-dwell, not a *selection+dispatch* surface, and its POLICY_CHECK→NO_ELIGIBLE_WORK trigger has no loop caller.

Therefore R388 ("several consecutive simulated bounded advancements with no human intervention") cannot be satisfied by replaying preserved artifacts; it requires D9's new implementation (an audited close-run surface + a next-packet selection step + exactly-once advancement recording) before any consecutive-advancement test can even be written. The register's D9 statement — "the R388 consecutive-simulated-advancements scenario is IMPOSSIBLE to satisfy until this exists" — is upheld.

---

## (f) New defects / evidence errors found

No fabricated values and no live-evidence mismatches were found. Observations (none blocking M0-T125's gate):

- **O1 — analyzed-vs-reviewed identity nomenclature.** Both reports declare analyzed identity `13cd5973…`; the gate's reviewed identity is `9a48ee6` / evidence `915d73d`. Because M0-T125 changes no production code and every `file:line` I spot-checked (claude_runner.py:1199-1206, loop.py:181/1516/2035/2040, state_machine.py:395, workload_classifier importers, `limited_auto_enabled` writers) reproduces at the current tree, the analysis is materially stable across those commits (control-plane-only difference). Recommend the orchestrator confirm `git diff --stat 13cd5973..9a48ee6 -- tools/agent_supervisor/` is empty when recording the gate, for the record.
- **O2 — golden_run runtime.** `test_agent_supervisor_golden_run.py` took 3h13m wall (42 passed, exit 0). Not a register claim and not a defect, but a real gate-execution cost future reviewers must budget for (recorded to QA memory). Worth a note in the M0-T126 CI-time planning so the recert (R390) budget is realistic.
- **O3 — D7 minor line drift.** The False-writer citations `remote_approvals.py:293/306` land at `295/307` on the reviewed tree (identity offset per O1); the substantive claim (durable `limited_auto_enabled` has only False writers; `safe_auto_resume` unreachable under R595) is confirmed.
- **O4 — D4 mechanism nuance (not an error).** The observable degeneracy is fully live-proven (sentinel present in the 2,176-char prompt, flag `false` at seq 50). The register attributes the fold to contract text "line 931"; I did not need to confirm the exact fold line because the behavior is proven at the audit/transcript layer. The seed-c REFUTATION is correct.

---

### Files referenced (absolute)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T125-defect-register.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T125-callgraph-and-transitions.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\source-022-amendment.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T125.json`
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\33dfa57d54dbc5d11d55dd8bab9248280e6568ef0e50002ba04a38543967a7ed\audit.jsonl`
- `C:\Users\MLFLL\.claude\projects\C--Users-MLFLL-Downloads-nyc-zoning-wt-m0t107\0835bb80-0f2e-451f-882d-0b37df6d77d5.jsonl`
- Code spot-checks: `tools/agent_supervisor/{loop.py, claude_runner.py, state_machine.py, workload_sizing.py, workload_classifier.py}` under `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\`

---

**Requested status:** gate result **PASS** with 4 required corrections carried to M0-T126 (recorded by the orchestrator via `progress --message`, not by editing control files). I made no file writes outside `.claude/agent-memory/qa-engineer/`, ran no git / project_control.py / agent_supervisor subcommand, and never opened the sqlite journal.
