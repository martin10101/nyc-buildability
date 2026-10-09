# M0-T126 — G4 DELTA report (independent qa-engineer, read-only + read-only pytest) — VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31 by the SAME independent qa-engineer identity
that recorded the G4 PASS-with-3-corrections at e029c8a, re-attesting its corrections plus the
delta coverage at the remediation identity 2d46fb0. DELTA VERDICT: PASS, no residual required
corrections — counts reproduce exactly (8-pack 401; full suite excl. golden 2990/2; fast golden
27), both prior report defects fixed and verified by collection, all 10 new remediation tests
green and removal-sensitive at the live production seams. Recorded as gate G4 PASS at the new
identity.

---VERBATIM-BEGIN---
All re-attestation items verified. Here is my delta gate report.

---

# G4 (QA) Delta Re-Attestation — M0-T126

**Task:** M0-T126 (same task; new identity after fresh remediation of my 3 corrections + the G3 defects)
**Reviewed identity:** `2d46fb02fe26dce7901da35bce89854fa5148700` (detached checkout in my isolated worktree). **Material stability confirmed:** `git diff 2d46fb0 eee8ef0 -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` is empty — material content == branch tip.
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). No writes outside `.claude/agent-memory/qa-engineer/`; no git-write/project_control/supervisor-CLI-write; live runtime dir and journal never opened.
**Environment:** Python 3.11.9, pytest 8.4.2, ruff 0.13.0.

## DELTA VERDICT: PASS — all 3 prior corrections resolved; delta coverage genuine; no new findings

## Per-correction status

**G4-1 (test-count accuracy) — RESOLVED.** Reproduced at `2d46fb0`:
- 8-pack combined: **401 passed, 0 failed, 0 skipped** (60s). Per-pack collection: next_task **18**, command_docs **17**, orientation **13**, checkpoint_journey **25**, recovery **63**, launch_seam **69**, loop **122**, runner **74** = 401 — every number matches the producer claim and the orchestrator's 401.
- Full suite excl. golden: **2990 passed, 2 skipped** (255s) — matches.
- Fast golden subset: **27 passed, 15 deselected** (15s) — matches; re-run at this identity because loop.py production changed → no regression.
- Report text now carries these exact values: producer-report L19 explicitly records "next_task 18 not 19, loop base 118 not 121", L29 "401 passed", L33 "2990 passed, 2 skipped"; design-record L50-52 lists the full per-pack breakdown = 401. **The reports now reproduce.**

**G4-2 (crash-at-boundary citation) — RESOLVED.** Design-record §6 (L230-231) now cites the two real nodes: `next_task::ConsecutiveAdvancementTests::test_crash_AFTER_campaign_advancement_is_exactly_once` and `next_task::ExactlyOnceAdvancementTests::test_advancement_survives_a_crash_restart_without_doubling`. Both verified present in collection. The phantom `test_crash_at_advancement_boundary_is_exactly_once` is gone.

**G4-3 (scenario-6 attribution) — RESOLVED.** Design-record §5 scenario-6 (L194) now splits: STALE half → `checkpoint_journey::CodexStaleVerdictTests` (correlation guard removal-sensitive); DUPLICATE half → `next_task::ExactlyOnceAdvancementTests::test_duplicate_advancement_in_same_process_is_noop` + `ConsecutiveAdvancementTests::test_crash_AFTER_verdict_persistence_never_re_advances`. Both cited nodes exist; attribution is accurate.

## Delta coverage (the four new classes — exist, green, removal-sensitive by binding)

Ran all 10 new tests verbosely → **10 passed** (loop +4, orientation +3, checkpoint_journey +3; accounts for 391→401).

| Class | Tests | Binds | Removal-sensitivity | Production seam verified |
|---|---|---|---|---|
| loop::**RotatedOrientationDispatchTests** | 2 | G3-1: rotated worker's *dispatched* prompt (`runner.prompts[1]`) carries ORIENTATION_SENTINEL, "ROTATED successor", CHECKPOINT CADENCE, `by turn {early}`, `{total} turns total`, RELEVANT FILES, `tools/agent_supervisor`, EXACT REQUIRED OUTPUT | `test_without_a_budget_the_rotated_prompt_is_not_enriched`: turn_budget=None → handoff present but NO orientation packet (the exact G3-1 gap) | `loop._turn_budget` (loop.py:681) → `loop_turnover.with_reorientation` (352) reads it → `orientation.oriented_reorientation_prompt` (208) front-loads `rotated=True` packet; returns unchanged when None/oversized |
| loop::**ReservedTurnInjectionDispatchTests** | 2 | G3-2: the reserved-turn demand is injected as a real follow-up user turn via `run_unit(extra_turns=...)`; asserts `runner.extra_turns_seen==[reserved_turn_injection(budget)]`, exactly one demand with "RESERVED FINAL TURN"/"Emit your mandatory checkpoint NOW"/"do NOT start any new tool call" | `test_no_injection_without_a_budget`: turn_budget=None → `extra_turns_seen==[()]` (the preserved 12/12 shape) | loop.py:1635-1637 passes `extra_turns=tb.reserved_turn_injection(self._turn_budget)`; claude_runner.py:1347-1349 writes each extra turn as a genuine stdin `user_message` (`expected_results += 1`) |
| orientation::**RotatedReorientationTests** | 3 | G3-1 unit: `oriented_reorientation_prompt` enriches with cadence/paths/required-output | `test_no_budget_returns_the_handoff_unchanged`, `test_oversized_budget_returns_the_handoff_unchanged` | orientation.py:226 `if not dispatchable: return reoriented_prompt` |
| checkpoint_journey::**ReservedTurnInjectionTests** | 3 | G3-2 unit: dispatchable → exactly one honest demand; forbids further tool use; demands honest incomplete-but-resumable | `test_none_and_oversized_yield_no_injection` | turn_budget.py:293-305 `reserved_turn_injection` → () for None/non-dispatchable |

Both G3-1 and G3-2 are genuinely wired into the live production path (not prompt-text-only or helper-only): the rotated orientation reaches the successor's actual dispatched prompt, and the reserved-turn demand is delivered as a real provider follow-up turn through the pre-existing `extra_turns` stdin channel. The removal-sensitive boundary tests would fail if either wiring were reverted.

## Regression / tooling at `2d46fb0`
- modularity_check --check: **failures 0** (335 files; loop.py grew 2030→2034, well under 2088; cli/claude_runner net-zero at limit).
- ruff on the 5 changed production files + 3 changed test files: **All checks passed!**
- supervisor_command_doc_check: **exit 0, 12 commands, 0 failures** (G3-3 runbook regeneration validates clean).
- Both report files: **0 non-ASCII bytes**.

## New findings
None. All three of my prior corrections are resolved with reproducible evidence, the delta's new coverage is real and removal-sensitive, and there are no regressions. The property-3 "soft enforcement" limitation (the `--max-turns` model can't hard-block a worker from spending its reserved turn on a tool call; exhaustion fail-closed is the backstop) is honestly disclosed in design-record §8 / producer-return-3 — consistent with the amendment's "wherever technically enforceable."

**Requested gate result at the new identity:** **PASS** (no residual required corrections). All commands reproduce at `2d46fb0` (materially identical to branch tip `eee8ef0`).

Note for the orchestrator: I reached `2d46fb0` via `git checkout --detach` in my own isolated worktree (I had to remove my earlier untracked memory files first — restored now; `.claude/agent-memory/qa-engineer/supervisor-gate-reproduction.md` is tracked at this identity, and I re-created the `MEMORY.md` index). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
