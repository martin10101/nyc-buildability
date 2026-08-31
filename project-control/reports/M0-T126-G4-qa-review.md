# M0-T126 — G4 report (independent qa-engineer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the unnamed roster qa-engineer spawn,
reviewed at the frozen identity e029c8a (detached checkout in its own isolated worktree).
Verdict PASS with 3 required corrections (report accuracy: test-count drift 395->391,
a non-existent test citation in design-record section 6, scenario-6 duplicate-half
attribution) - blocking for the acceptance evidence record per gate-verdict semantics.
Bundled with the G3 FAIL corrections into one fresh-producer remediation pass (R395).
The reviewer's QA memory note was preserved from its ephemeral worktree into
.claude/agent-memory/qa-engineer/.

---VERBATIM-BEGIN---
All verification complete. Here is my G4 gate report.

---

# G4 (QA) Gate Report — M0-T126

**Task:** M0-T126 — durable checkpoint design (7 properties) + all 17 register defect corrections + adversarial replay coverage + simulated multi-unit advancement (D-024-R372..R388)
**Reviewed identity:** `e029c8ab58c4c0ac1a68f97e43319a474124b12d` (detached checkout in my isolated worktree; confirmed via `git rev-parse`)
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). No file writes outside `.claude/agent-memory/qa-engineer/`; no git write / project_control / supervisor-CLI-write; the live runtime dir and sqlite journal were never opened.
**Environment:** Python 3.11.9, pytest 8.4.2, ruff 0.13.0 (matches producer).

## (a) VERDICT: PASS — with 3 numbered required corrections (report-accuracy only; NOT coverage or functional gaps)

Every load-bearing claim reproduces at `e029c8a`: the seven-property design is implemented and wired into the live cli dispatch path; all 17 register defects are corrected at this one identity; G4 corrections 1–4 and the full R387 sixteen-scenario matrix are present, substantive, and removal-sensitive; every fixture number traces exactly to the preserved artifacts; the full suite (2980 passed, 2 skipped), the 8 defect packs (391 passed), the fast golden subset (27 passed), modularity (failures 0), the command-doc tooth (exit 0, 12/0), and ruff (clean) all reproduce. The three orchestrator-flagged static-analysis items are confirmed false positives. The required corrections are report-text inaccuracies that must be fixed for report reproducibility before final acceptance; none of them reduce coverage.

**Required corrections (report accuracy — blocking for a clean evidence record, not for coverage):**
1. **Test-count drift.** `M0-T126-producer-report.md`, `-design-record.md §0`, and `producer-return-2.md` state per-pack counts summing to **395** (next_task 19, loop 121). The frozen identity collects/passes **391** (next_task **18**, loop **118**; the other six packs match). Correct the reports to 391 / next_task 18 / loop 118 so the numbers reproduce.
2. **Non-existent test citation.** Design-record §6 cites `next_task::…::test_crash_at_advancement_boundary_is_exactly_once` — no test exists under that name. The actual crash-at-boundary tests are `ConsecutiveAdvancementTests::test_crash_AFTER_campaign_advancement_is_exactly_once` and `ExactlyOnceAdvancementTests::test_advancement_survives_a_crash_restart_without_doubling`. Fix the citation.
3. **Scenario-6 mapping imprecision.** Design-record §5 maps "stale/**duplicate** decisions" to `CodexStaleVerdictTests`, but that class only proves the STALE correlation guard. The **duplicate**-verdict-no-double-advance half is proven in `next_task` (`test_duplicate_advancement_in_same_process_is_noop`, `test_crash_AFTER_verdict_persistence_never_re_advances`). Attribute the duplicate half correctly so correction 2's coverage map is accurate.

## (b) Reconciled exact test counts

The 4-test discrepancy is explained exactly: the producer over-counted **next_task by 1** (claimed 19, actual 18) and **loop by 3** (claimed 121, actual 118). The orchestrator's combined run (391) matches the frozen identity; the producer's 395 measured a transient worktree, not `e029c8a`. No required test node is missing (all correction 1–4 and R387 nodes are present).

| Pack | Producer claim | Reproduced (collect / `-q` run) |
|---|---|---|
| next_task | 19 | **18** passed |
| command_docs | 17 | 17 passed |
| orientation | 10 | 10 passed |
| checkpoint_journey | 22 | 22 passed |
| recovery | 63 | 63 passed |
| launch_seam | 69 | 69 passed |
| loop | 121 | **118** passed |
| runner | 74 | 74 passed |
| **8-pack combined** | **395** | **391 passed, 0 failed, 0 skipped** in 48s |
| Full suite excl. golden | 2980 passed, 2 skipped | **2980 passed, 2 skipped** in 213s (2 skips are pre-existing env skipif: claude/codex not on PATH) |
| Fast golden subset | 27 passed | **27 passed, 15 deselected** in 12s |
| modularity_check --check | failures 0 | **failures 0** (selected 335 files; producer said 330 — count differs, failures 0 holds) |
| supervisor_command_doc_check | exit 0, 12, 0 drift | **exit 0; 12 commands; 0 failures** |
| ruff (touched prod + test files) | clean | **All checks passed!** |
| reports ASCII | pure ASCII | **0 non-ASCII bytes** in both |

Fast-golden selection method: hand-picked classes (TwoUnit 6 + InjectedFault 5 + WatcherCapture 4 + WatcherLabeling 7 + WatcherPassivity 3 + WatcherStartEpilogue 1 + EpochRotation 1 = 27). The excluded 15 classes are the ~3h13m R247 recert (correctly budgeted to M0-T127); I did not run them.

## (c) R387 sixteen-scenario matrix audit

Every scenario's named test node exists (collection) and asserts the scenario's substance (read). Corrections 1–4 all satisfied.

| # | Scenario | Test node(s) | Status |
|---|---|---|---|
| 1 | fresh + rotated orientation | orientation::FreshVsRotatedTests (+RequiredElementsTests, front-loaded, cadence) | VERIFIED |
| 2 | consuming every working turn | checkpoint_journey::TurnExhaustionReplayTests (12-turn replay) | VERIFIED |
| 3 | early/incremental/incomplete/final checkpoints | checkpoint_journey::TurnBudgetTests (7) + TurnExhaustionReplayTests | VERIFIED |
| 4 | missing/malformed/duplicate/contradictory checkpoints | checkpoint_journey::test_exhausted_stream_has_no_valid_checkpoint + runner extract suite | VERIFIED |
| 5 | Codex HALT **and CONTINUE** (corr 1) | checkpoint_journey::CodexContinueVerdictTests (3; removal-sensitive on missing next_claude_prompt) | VERIFIED |
| 6 | missing/malformed/**duplicate/stale** verdicts (corr 2) | checkpoint_journey::CodexStaleVerdictTests (stale) + next_task duplicate-advance tests | VERIFIED (see req. corr. 3 for mapping) |
| 7 | Codex review failure + success | CodexContinueVerdictTests + existing codex suite | VERIFIED |
| 8 | exactly-once task advancement (corr 4, D9) | next_task::ExactlyOnceAdvancementTests (5) | VERIFIED |
| 9 | interruption before/after checkpoint, forwarding, verdict persistence, advancement (corr 3) | sub-matrix below | VERIFIED (all rows) |
| 10 | next-task selection + dispatch (corr 4, D9) | next_task::SelectionTests (5) | VERIFIED (selection live-tested; dispatch simulated — see obs.) |
| 11 | rotation before provider contact | checkpoint_journey::LiveVsCumulativeTokensTests (ceiling consumes live) | VERIFIED |
| 12 | provider crash/refusal/quota/context/restart | LiveVsCumulative + recovery/crash packs | VERIFIED |
| 13 | worktree isolation + primary-checkout refusal | launch_seam::CliRepoBindingGateD2 (5) + CliWorktreeGate | VERIFIED |
| 14 | preserve audit/budgets/owner-gates/pending-effects | loop::BetweenCycleIntentStopTests + bounded_mode/crash packs | VERIFIED |
| 15 | command-document validation | command_docs suite (17) + CI tooth | VERIFIED |
| 16/R388 | consecutive advancements, no human intervention | next_task::ConsecutiveAdvancementTests (5) | VERIFIED |

**Scenario-9 sub-matrix (correction 3, all rows present):** recovery::CrashBoundaryTests `test_d6_crash_immediately_after_popen_is_ambiguous` / `…after_partial_stream…` / `…checkpoint_in_stream_before_extract…` + reconciled control `test_d6_reconciled_dispatch_is_not_ambiguous`; loop::CrossProcessForwardResumeD10Tests (forwarding boundary); next_task `test_crash_BEFORE_verdict_persistence_…` / `test_crash_AFTER_verdict_persistence_never_re_advances` / `test_crash_BEFORE_campaign_advancement_loses_no_work` / `test_crash_AFTER_campaign_advancement_is_exactly_once`; loop::BetweenCycleIntentStopTests. **Both halves of correction 3 (verdict persistence + campaign advancement, before/after each) are present.**

## (d) Removal-sensitivity binding table (load-bearing tests)

| Correction | Binding test + assertion | Code seam | Fails if reverted? |
|---|---|---|---|
| **D3 12/12 replay** | checkpoint_journey::test_exhausted_stream_has_no_valid_checkpoint → `extract_checkpoint(events)` raises code `missing_checkpoint`; test_old_fixed_bound… asserts `budget.total_turns > 12` | claude_runner.extract_checkpoint (S14 fail-closed); turn_budget sized 33; wired cli.py:2677 `sized_max_turns` | YES — if missing were treated as success, or budget sized ≤12, both fail |
| **D5 live-vs-cumulative + exact-400k** | test_ceiling_consumes_live_when_known asserts `(72546, True, "live")`; test_adversarial_exactly_at_ceiling_flags asserts tokens≥400000, known | loop.py:555 `_ceiling_context_tokens` prefers live; consumed at loop.py:972-978 rotation `ceiling_tokens >= threshold` | YES — reverting to cumulative returns 694251/"cumulative" → assertion fails |
| **D10 cross-process resume** | loop::test_forwarded_bytes_are_dispatched_on_the_next_start asserts fresh loop2 on same durable journal receives `TASK: M0-T036`, `assertNotIn("GENERIC DEFAULT")`; consumed-exactly-once; advancing cycle id | loop.run persists `next_unit_prompt/<run_id>`, consumes on CLAUDE_RUNNING entry | YES — without the resume branch loop2 dispatches the generic default (the bug); assertion fails |
| **R388 consecutive + crash-at-boundary** | next_task::test_three_consecutive_advancements_exactly_once_each (M0-T200→201→202, each newly_recorded once, exhausts); test_crash_AFTER_campaign_advancement_is_exactly_once (reopen → newly_recorded False, selects M0-T201) | next_task.record_advancement over `compare_and_swap_state` (durable `BEGIN IMMEDIATE`, expected=None single-winner) | YES — a non-CAS write returns newly_recorded True on the post-reopen replay → double-advance; assertion fails |

**R388 substance (duty 6):** the three advancements run in a pure loop with no human intervention; each records exactly once (CAS single-winner); `test_contradictory_later_output_never_re_advances` and `test_crash_AFTER_verdict_persistence_never_re_advances` prove no false acceptance. The crash-at-boundary uses `reopen()` = close all handles + fresh `DurableJournal(...).open()` on the same sqlite file — a genuine process-death simulation (fresh objects + journal re-open reading durable state), not an in-process exception. Confirmed `compare_and_swap_state` is a real atomic `BEGIN IMMEDIATE` transaction (durable_state.py:397).

## (e) Fixture-fidelity results (all trace exactly to preserved originals)

Preserved worker transcript `…wt-m0t107\0835bb80-…jsonl`: **97 events, 36 assistant, 12 distinct message ids, all 36 stop_reason=tool_use**, final assistant usage cache_read **67935** + creation **3962** + output **647** + input 2 = **72546** live (peak per-turn). All match the task's stated values and the fixture.

Preserved audit `preserved-artifacts\audit.jsonl`: **53 records**; seq 50 contains **694251** (cumulative); seq 21 contains **604772** (rotation origin — also present at seq 24, confirming the G3 seq-21 citation fix); seq 8 = 622599; seq 40 = 640224. All match `m0t107_journey_facts.json`.

D5 numbers trace: fixture live 72546 = the real turn-12 usage sum; cumulative 694251 = the real terminal result event. `live_context_tokens()` excludes `type==result` and takes the peak turn (turn 12), correctly yielding 72546. Note (not a defect): the stream fixture's intermediate turns 1–11 carry synthetic monotonic-ramp usage (turn 12 is the real peak); the file is honestly labeled "Derived," and only the two load-bearing figures + the 12-turn count are load-bearing, all of which match the originals.

## (f) New defects / observations

No functional defects and no fabricated evidence found. The 3 required corrections in (a) are report-text accuracy. Non-blocking observations:

- **O1 — D9 advancement/selection is simulation-only (correct scope).** Only `plan_close_run` (COMPLETE→IDLE `run_closed`) is wired into cli.py:2687 and fires the real transition. `record_advancement`/`select_next_packet`/`advance_and_select` are exactly-once CAS machinery tested only in simulation; live auto-dispatch of the next selected packet is deliberately reserved to the R393 owner-authorized live commissioning journey. This aligns with the amendment ("full autonomy may not be declared from tests/simulations") — not a gap.
- **O2 — adversarial-exactly-at-ceiling test scope.** `test_adversarial_exactly_at_ceiling_flags` asserts the helper returns ≥400000/known, not the loop's rotation decision at the boundary. The loop comparison uses `>=` (loop.py:978) so 400000 would flag; end-to-end boundary rotation is exercised in the loop pack rather than this unit. Minor naming imprecision only.
- **O3 — static-analysis flags are false positives (confirmed).** loop.py `_ceiling_context_tokens` (def 555, called 972/1644), command_docs.py `_strip_trailing_comment` (def 234, called 220 inside a function body), claude_runner.py live_ctx (assigned 1472, stored into RunResult 1509-1510) are all valid module-level forward references resolved at call time and executed by passing tests. Producer's rebuttal is correct.
- **O4 — property-3 reserved turn is soft.** The reserved final turn is realized as a budget reservation (RESERVED_FINAL_TURNS=1) plus an orientation instruction, not a hard runtime block on tool use — consistent with the amendment's "wherever technically enforceable."
- **O5 — modularity file count** reported 335 selected vs producer's 330 (frozen tree has more tracked files); failures 0 holds regardless.
- **O6 — 2 skips** in the full suite are pre-existing environmental `skipif` (claude/codex not on PATH), unchanged from the M0-T125 baseline; not introduced by this task.

**Requested gate result:** PASS with 3 numbered required corrections (report accuracy). All commands above are reproducible at `e029c8a`. Recorded to QA memory at `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a0c33e04bda060c8a\.claude\agent-memory\qa-engineer\supervisor-gate-reproduction.md`.

Note for the orchestrator: I reached the frozen identity by `git checkout --detach e029c8a` inside my own isolated worktree (my worktree HEAD was `d8b3899`, an ancestor); the orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
