# M0-T126 — DCV verification report (independent directive-compliance-verifier, read-only) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the unnamed roster directive-compliance-verifier
spawn. VERDICT: ALL 18 applicable rows SATISFIED at frozen material identity 2d46fb0 (branch tip
6b1d6d1 at review; material diff empty). Six numbered observations, none blocking: (1) G2 not yet
recorded — the expected in-flight state, closed by the orchestrator before accept; (2) carried O4
(one producer-recomputed runbook digest not independently recomputable from the sandbox); (3)
immaterial line drift 1619->1637; (4) return-2 immutable pre-remediation counts correct by design;
(5) runbook wt-m0t063 residuals in sections OUTSIDE the register's D15 scope; (6) harness
transparency note (validator EXIT=0 authoritative). Verification rows written to
verification.json from this report; G2 recorded next; then accept.

---VERBATIM-BEGIN---
I have now verified all 18 rows against primary evidence at the frozen identity. Control-plane harness is green (test_project_control 23 passed, test_directive_reminder 12 passed, validator `--check` exit 0). Here is my DCV record.

---

# DCV REPORT — Task M0-T126 (D-024 Amendment 22/23, 18 applicable rows)

## VERDICT: **PASS** — ALL 18 applicable requirement rows SATISFIED

**Reviewed identity:** frozen material commit `2d46fb0`. Branch tip HEAD = `6b1d6d1`. Content identity verified: `git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` is EMPTY; the 5 commits `2d46fb0..HEAD` touch only control-plane files (reports/gates/state/agent-memory). Submit `reviewed_sha` `fa1dadd`, G3 `eee8ef0`, G4 `b2a8058` are each content-identical to `2d46fb0` for allowed_paths (all in-window diffs empty). Registry integrity: `validate_directive_compliance.py --check` = **exit 0** (source digests match; amendments 22/23 present).

I am not the producer (producer = `supervisor-stabilization-producer`; I am `directive-compliance-verifier`). Every row below was judged on primary evidence I reproduced, not on the producer/gate claims.

## Row-by-row verdicts

| Req | Verdict | Primary evidence reproduced (file / field / observed value) |
|---|---|---|
| **R372** | SATISFIED | `source-022-amendment.md` L54-121 verbatim owner text authorizes EXACTLY ONE bounded window. `tasks/M0-T126.json` in-regime: `directive_regime_version=1.0`, `directive_refs=[{D-024,ALL}]`, `directive_regime_entered_at=2026-08-30T21:07:19Z`; step 2 after M0-T125. No live launch: preserved journal still `PAUSED_RECOVERY`, audit 53 records unchanged. |
| **R373** | SATISFIED | `M0-T126-design-record.md` §1/§3/§5 maps every journey seam→mechanism→test. Code exists at frozen id: `orientation.py` (launch/orient), `next_task.py` (advancement/selection), `loop.py:2551-2562/2792` (D10 cross-process forward). Tail defects D8/D9/D10 corrected (verified in code + tests). |
| **R374** | SATISFIED | LIVE preserved dir `…\33dfa57d…\`: `audit.jsonl` = **53** records; sqlite (read-only `mode=ro&immutable=1`) `state_kv.current_state="PAUSED_RECOVERY"`, `transitions`=**22**, `effects`/`outbox`/`inbox`=**0**. `wt-m0t107` clean at `796e18f`. Transcript `0835bb80….jsonl` = **97** lines. Fixture values match preserved originals (see R386). |
| **R375** | SATISFIED | `gh pr view 241` = state **OPEN**, updatedAt **2026-08-20** (pre-window, untouched). `git diff 1bb7735 2d46fb0 -- broker.py` EMPTY. `recovery.py:462-475` R595-gated `safe_auto_resume` preserved as UNREACHABLE; new dispatch-intent guard (`recovery.py:433`) makes recovery MORE conservative (AMBIGUOUS_EFFECT). No journal mutation (R374 counts intact); no policy weakening. |
| **R376** | SATISFIED | `orientation.py:93-167 build_orientation_packet` renders all 6 elements (TASK/lineage/WORKTREE/CURRENT PROGRESS/RELEVANT FILES/EXACT REQUIRED OUTPUT). Wired FRESH `cli.py:2903 oriented_first_prompt`; ROTATED `loop_turnover.py:372 oriented_reorientation_prompt` via `with_reorientation`, invoked at `loop.py:2783,2900`. Dispatch test `RotatedOrientationDispatchTests` (loop pack **122 passed**) asserts `runner.prompts[1]` carries the packet + removal-sensitive no-budget control. |
| **R377** | SATISFIED | Cadence (`early_checkpoint_by`, `incremental_checkpoint_every`) sized from budget, surfaced in packet L137-150. `TurnBudgetTests::test_early_and_incremental_cadence_within_working_turns` (checkpoint_journey **25 passed**). |
| **R378** | SATISFIED | `turn_budget.py:293 reserved_turn_injection` → `loop.py:1637 extra_turns=` → `claude_runner.py:1347 write(user_message(turn))` (real stdin follow-up turn). Demand forbids new tool use (`turn_budget.py:283-290`). `ReservedTurnInjectionDispatchTests` asserts `runner.extra_turns_seen[0]==reserved_turn_injection(budget)`; removal-sensitive no-budget→`()`. Evidence-map R378 row is corrected (honest "wherever technically enforceable" hedge; matches design §8) — no residual overclaim. |
| **R379** | SATISFIED | `extract_checkpoint` refuses missing/malformed; advancement requires a Codex-reviewed checkpoint_id (`next_task.py:203-206`). `TurnExhaustionReplayTests::test_exhausted_stream_has_no_valid_checkpoint` + `test_old_fixed_bound_would_pass_new_design_fails_honestly` (12/12→missing, never success). |
| **R380** | SATISFIED | `turn_budget.py:66 HARD_TURN_CEILING=40`; working sized per class `working_turns_for` (L241), `total=min(uncapped,40)` (L243). NOT raising max_turns: `test_class_sizes_differ_not_a_single_raised_constant` + `test_total_never_exceeds_the_hard_ceiling` + `test_allowance_over_ceiling_fails_closed`. |
| **R381** | SATISFIED | Fail-closed: extract refuses missing/conflicting/multiple; not-OK unit → PAUSED_RECOVERY; forwarding failure leaves next-unit-prompt pointer unconsumed. `TurnExhaustionReplayTests` (checkpoint_journey pack green). |
| **R382** | SATISFIED | `next_task.py:217 record_advancement` over `compare_and_swap_state(key,None,record)` single-winner; `select_next_packet` skips advanced (L312). D10 pointer consumed exactly once (`loop.py:2562/2792`). `ExactlyOnceAdvancementTests::test_advancement_survives_a_crash_restart_without_doubling` + `test_contradictory_later_output_never_re_advances` (next_task **18 passed**). |
| **R385** | SATISFIED | All 17 defects (D1-D17) at ONE lineage ending `2d46fb0` (e029c8a is ancestor; D15 completed in remediation). Spot-reproduced: **D2** `launch_seam.py:242 evaluate_repo_binding`+`CliRepoBindingGateD2`; **D9** `next_task.py` machinery (18 passed); **D10** `_persist/_consume_next_unit_prompt`+`CrossProcessForwardResumeD10Tests`; **D15** runbook §1 digests regenerated, §5 manifest outside-tree, §11 current campaign, tooth 12/0. 8 packs **401 passed** reproduced; `modularity_check --check`=0 failures. |
| **R386** | SATISFIED | Fixtures derived from preserved copies. Verified vs preserved originals: audit `seq 21 context_tokens=604772`, `seq 50 context_tokens=694251`; transcript final usage `2+3962+67935+647=72546` (12 distinct assistant ids). `m0t107_journey_facts.json` records these exactly. Live originals untouched (R374). |
| **R387** | SATISFIED | design-record §5 16-scenario + §9 sub-matrix → real nodes. Collected/exist: scenario-5 `CodexContinueVerdictTests` (3); scenario-6 `CodexStaleVerdictTests` (3) + `next_task…test_duplicate_advancement_in_same_process_is_noop`; scenario-9 `CrashBoundaryTests::test_d6_*` (4) + `CrossProcessForwardResumeD10Tests` (3) + next_task crash BEFORE/AFTER verdict/campaign (4). All in packs run green. |
| **R388** | SATISFIED | `ConsecutiveAdvancementTests::test_three_consecutive_advancements_exactly_once_each` (M0-T200→201→202, each `newly_recorded` once, no dup/lost/false/unsafe) + `test_crash_AFTER_campaign_advancement_is_exactly_once`. Reproduced: `pytest test_agent_supervisor_next_task.py` = **18 passed**. |
| **R389** | SATISFIED (see Disc. 1) | Gates recorded PASS at frozen id: G0 `reviewer=orchestrator`; G3 `reviewer=code-reviewer` `reviewed_sha=eee8ef0`; G4 `reviewer=qa-engineer` `reviewed_sha=b2a8058`. Producer `supervisor-stabilization-producer` ≠ every reviewer. Honest FAIL→delta chain: FAIL report `M0-T126-G3-code-review.md` (16257 bytes) STILL EXISTS beside delta PASS. |
| **R395** | SATISFIED | Patch #1 `M0-T126-worktree.patch` sha256 **1a2c2865…5328** (216236 B) = expected; patch #2 `M0-T126-remediation.patch` sha256 **2025bb14…d905** (64445 B) = expected. return-2: original context patch-captured + RETIRED (no resume). return-3: FRESH producer (base 767b833, new worktree) oriented from durable artifacts, patch-captured + retired. |
| **R396** | SATISFIED | return-2 L19 "Not under context pressure (~14.4M tokens remaining); completed the full R385 list"; orchestrator seam note "R396 valve not tripped". return-3 = bounded single pass. Procedural, consistent, uncontradicted. |

## Discrepancies / observations (numbered)

1. **G2 gate not yet on record (non-blocking; orchestrator action).** `tasks/M0-T126.json` `required_gates=[G0,G2,G3,G4]`, but there is no `project-control/gates/M0-T126-G2.json` and no G2 entry in `state.json`. This is the normal in-flight state (task `status=awaiting_gate`): G2 (self-check) and the DCV record itself are the closing steps the orchestrator records before `accept()`, and `accept()` enforces the required-gate set. This is NOT a producer defect and does not weaken any of the 18 rows; the substantive independent reviews (G3/G4) are complete and honest. R389 is SATISFIED on that substance; the orchestrator must still record G2 + this DCV before acceptance.
2. **O4 (carried by G3 delta, non-blocking).** Runbook §1 LF-normalized digest `4c67875b24be66c3…e75f` is a producer-recomputed value I could NOT independently recompute from my sandbox (it requires hashing the owner-local protected config). The two register-named digests are present and consistent: raw `A1F995016B541B9D…1436` (runbook L18) and model-selection `FCBBF70F553AE115…DD2B` (L21). Flagged for the record; does not fail D15/R385.
3. **Minor line-number drift (immaterial).** design-record §1/§3 and producer-return-3 cite `loop.py:1619` for the extra_turns injection call; at the frozen identity it is `loop.py:1637` (same function, `run_unit` call). The mechanism is present and verified; no evidentiary impact.
4. **Immutable pre-remediation counts in return-2 (not a defect).** `M0-T126-producer-return-2.md` L39 carries pre-remediation per-pack counts (next_task 19, loop 121, orientation 10, checkpoint_journey 22). The FINAL corrected counts (next_task 18, command_docs 17, orientation 13, checkpoint_journey 25, recovery 63, launch_seam 69, loop 122, runner 74 = **401**) are in the design record / return-3, and I independently reproduced all eight (18+17+13+25+63+69+122+74=401). return-2 is an immutable historical capture; correct by design.
5. **Runbook `wt-m0t063` residuals (out of D15 scope).** `docs/CONTROLLER_UPDATE_RUNBOOK.md` sections 2-10 still use `wt-m0t063` in status/stop/verify EXAMPLES (L22,33,44,131,147,160-162,212). The register's D15 correction is scoped to §1/§5/§11 (all resolved: digests, outside-tree manifest, §11 current-campaign start command `--checkout C:\SupervisorController`, `--run-id` omitted). The only §11 "M0-T063" hit is explanatory prose (L224). Consistent with the independent G3 delta verdict.
6. **Harness note (transparency).** `tools/test_directive_compliance.py` did not finish within the 5-min sandbox timeout (heavy 473 KB registry digest work); the authoritative registry-integrity gate `validate_directive_compliance.py --check` = **exit 0**. `test_project_control.py` = 23 passed; `test_directive_reminder.py` = 12 passed.

## Exact commands run (read-only)

- `git rev-parse HEAD` → `6b1d6d1…`; `git diff 2d46fb0 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` (empty); `git merge-base --is-ancestor` (2d46fb0, 6b1d6d1 both ancestors); `git log --oneline 2d46fb0..HEAD`; `git diff --stat 1bb7735 2d46fb0 …`; `git diff 1bb7735 2d46fb0 -- broker.py` (empty); `git diff fa1dadd 2d46fb0 -- …` (empty).
- `python tools/validate_directive_compliance.py --check` → exit 0.
- Read-only sqlite: `sqlite3.connect("file:…supervisor_journal.sqlite3?mode=ro&immutable=1")` → transitions 22, effects/outbox/inbox 0, current_state PAUSED_RECOVERY; `wc -l audit.jsonl`=53, transcript=97.
- `gh pr view 241 --json state,updatedAt` → OPEN / 2026-08-20.
- `sha256sum` on both `M0-T126-*.patch` (both match expected).
- Python parse of preserved audit.jsonl (seq21=604772, seq50=694251) and transcript final usage (72546, 12 assistant ids); parse of `m0t107_journey_facts.json`.
- `pytest`: next_task (18), orientation+checkpoint_journey+command_docs (55), loop (122), recovery+launch_seam+runner (206) = **401**; `--collect-only` for R387 nodes.
- `python tools/supervisor_command_doc_check.py` → 12 commands, 0 failures; `python tools/modularity_check.py --check` → 0 failures; `test_project_control.py` 23 passed; `test_directive_reminder.py` 12 passed.
- Grep/Read of `recovery.py:420-475`, `orientation.py`, `loop_turnover.py:330-379`, `turn_budget.py:236-306`, `next_task.py`, `CONTROLLER_UPDATE_RUNBOOK.md`.

No writes were made outside my agent-memory scope; no `project_control.py`/git-write/`gh`-write/supervisor-write verb was run; the live runtime sqlite journal was opened read-only (`mode=ro&immutable=1`) only.

**Recommendation to orchestrator:** record this DCV as **PASS** for the 18-row applicable set into `verification.json`, then record the pending **G2** self-check before `accept()`. Relevant primary-evidence paths (all absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\{source-022-amendment.md,source-023-amendment.md,requirements.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T126-{design-record.md,evidence-map.json,producer-return-2.md,producer-return-3.md,G3-code-review.md,G3-code-review-delta.md,G4-qa-review-delta.md}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\{orientation.py,turn_budget.py,loop.py,loop_turnover.py,next_task.py,recovery.py,claude_runner.py,launch_seam.py}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\{m0t107_stream_d5.json,m0t107_journey_facts.json}`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\CONTROLLER_UPDATE_RUNBOOK.md`
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\33dfa57d54dbc5d11d55dd8bab9248280e6568ef0e50002ba04a38543967a7ed\` (preserved journal, read-only)
- `C:\Users\MLFLL\AppData\Local\Temp\claude\C--Users-MLFLL-Downloads-nyc-zoning-ctl24\656fa6dd-51a2-4fcb-9016-c75c1ac1a23c\scratchpad\M0-T126-{worktree,remediation}.patch`
---VERBATIM-END---
