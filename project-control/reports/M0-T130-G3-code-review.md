# M0-T130 G3 code review (VERBATIM reviewer return; saved unmodified by the orchestrator per the report-preservation rule)

Reviewer: independent unnamed code-reviewer roster spawn (read-only). Reviewed identity
HEAD `eb552586` (implementation content byte-identical to `20bfa449`). Verdict: FAIL
(C1/C2 blocking). Recorded by orchestrator 2026-08-31.

---VERBATIM-BEGIN---
I now have complete, reproducible evidence. Here is my G3 report.

---

# G3 Independent Code Review — M0-T130 (reserved-turn delivery fix)

**Task:** M0-T130 — reserved-turn delivery defect fix (D-024 Amendment 28, R420–R424; AD-093 qualifying evidence = journey-3 reproduced `absorbed_mid_turn`)
**Reviewed identity:** HEAD `eb552586` (implementation content is byte-identical to `20bfa449`; the HEAD commit adds only control-plane G0/G2/claim scaffolding)
**Reviewer role:** independent, read-only (ADR-005). Producer = `orchestrator-defect-runner`.
**Scope reviewed:** `tools/agent_supervisor/claude_runner.py`, `tools/test_agent_supervisor_runner.py`, `project-control/reports/M0-T130-reserved-turn-fix.md` (+ cross-checks of loop.py/turn_budget.py callers, the G2 self-check, and the CI wiring).

## 1. What the change does (verified against the diff)

- New pure helper `checkpoint_question_decided(events)` beside `extract_checkpoint` (claude_runner.py:801): returns `False` only for `missing_checkpoint`; `True` for a valid checkpoint or any of the three "candidate exists" error codes (`invalid_checkpoint`, `conflicting_duplicate_checkpoint`, `multiple_distinct_checkpoints`).
- In `run_unit` (claude_runner.py:1360–1421): `extra_turns` are no longer written at launch. They are held in `pending_turns` and each is written only after a prior turn's terminal `result`, and only while `checkpoint_question_decided(events)` is `False`. Completion latches on `results_seen >= expected_results and not pending_turns`.
- loop.py:1635 call site and `turn_budget.reserved_turn_injection` are unchanged; production passes at most one reserved turn (empty when no budget -> identical to pre-fix behavior).

## 2. Correctness assessment (logic is sound)

I traced every edge case named in the review brief; the runtime logic is correct:

- **Multiple `extra_turns`:** each written one-at-a-time only after the prior result; re-evaluated for decidedness at each idle point; a mid-sequence checkpoint clears the remaining pending turns (moot). Correct.
- **`result` in the same chunk as later events:** injection writes mid-inner-loop; the break condition is re-checked only after the whole chunk drains, and `expected_results` is bumped at write time, so the loop correctly waits for the injected turn's own result. No premature break. Correct.
- **`checkpoint_question_decided` vs the three error codes:** sound. Injecting after any existing candidate can only produce a `conflicting_duplicate`/`multiple_distinct` refusal in `extract_checkpoint`, so skipping injection when a candidate already exists is the right call and fails fast honestly. Matches `test_checkpoint_question_decided_vocabulary`.
- **`control_request` / stdin lifetime:** stdin is closed only in the `finally` block, reached only after the loop breaks, and the break requires `not pending_turns`. Therefore stdin is guaranteed open while any pending turn is still to be written. Correct.
- **Graceful-close / tree-termination accounting:** untouched by this change; `graceful_close_failed` and the watchdog wall-timeout paths are unchanged. Correct.
- **Removal-sensitivity:** the absorption test is genuinely red-on-mutant (reverting to launch-time writes makes `absorbs_early_second_prompt` yield `expected_results=2 > results_seen=1`, ride the 15 s test wall, and fail the `ok`/`timed_out`/`elapsed<10`/`len==1` assertions — matching the producer's recorded "1 failed/3 passed, missing_checkpoint after the merged result"). The decidedness-skip, injection-as-own-turn, and fast-fail tests are each removal-sensitive. Verified by trace.
- **Repurposed test is honest:** `SessionCloseTests::test_a_checkpoint_in_the_first_result_skips_the_reserved_turn` changes the assertion from 2 results to 1 because the old two-results behavior *was* the defect (both prompts written at launch). The "extra turn delivered as its own turn" behavior it used to cover is preserved by the new `test_reserved_turn_is_injected_when_the_first_result_lacks_one` (asserts 2 results via `no_checkpoint_then_checkpoint`). Not evidence-weakening.

**Runner pack re-run (independent):** `python -m pytest tools/test_agent_supervisor_runner.py -q` -> **78 passed in 11.74 s**. Confirmed green.

## 3. Blocking defects

### C1 — `python tools/modularity_check.py --check` FAILS at the reviewed identity (exit 1). Severity: HIGH (blocking; breaks a wired CI gate)

Reproduced twice at HEAD `eb552586`:

```
$ python tools/modularity_check.py --check ; echo REAL_EXIT=$?
selected 335 files; failures 1; warnings 11
  FAIL baseline_growth: tools/agent_supervisor/claude_runner.py (1400) - grandfathered oversized file grew materially without a reviewed exception
REAL_EXIT=1
```

Arithmetic (from modularity_check.py:50-51, 348-349, 420-427): baseline `1258` (modularity_baseline.json:21) -> material-growth limit `1258 + max(50, int(1258*0.10)) = 1383`. Current SLOC `1400` > `1383` -> FAIL. The fix added net +34 raw lines (`git show 20bfa449 --numstat` -> `41 7`), tipping the file from under the limit (~1366-1380 pre-change) to 17 SLOC over it. This checker is a hard CI gate: `.github/workflows/ci.yml:565: run: python3 tools/modularity_check.py --check`. The branch therefore fails CI as delivered.

Resolution note for the orchestrator: getting under 1383 by trimming is hard because the +34 lines are mostly load-bearing code plus a ~12-line explanatory comment (comments are not counted as SLOC, so removing them won't help much). The standard fix is a reviewed baseline update in `tools/modularity_baseline.json` (or a path-exact expiring exception in `tools/modularity_exceptions.json`) with a recorded cohesion justification — **both paths are OUTSIDE this task's `allowed_paths`** (claude_runner.py, the runner test, and the one report), so landing this cleanly requires a task-scope amendment. The added code is cohesive with the file's existing responsibility (Claude worker stream/adapter + checkpoint extraction), so a cohesion justification is defensible — but it must actually be recorded and the checker must pass.

### C2 — Self-check / report / commit falsely assert modularity PASS. Severity: HIGH (blocking; evidence integrity)

Three artifacts claim the opposite of the reproducible result:
- `M0-T130-G2-self-check.md` (lines 17-19): "`modularity_check --check` 0 failures (claude_runner.py baseline-tracked, +~45 SLOC...)"
- `M0-T130-reserved-turn-fix.md` s3: "`modularity_check --check`: PASS (0 failures; ...+~45 SLOC)"
- commit `20bfa449` message: "modularity 0 failures"

At the reviewed identity the checker returns **1 failure / exit 1**. The "+~45 SLOC" figure is also wrong against what the checker measures: growth over the recorded baseline is **142 SLOC** (1258->1400), not ~45 (the producer appears to have counted only this diff's net additions, missing the cumulative drift from prior supervisor tasks that the baseline mechanism measures against). These false PASS claims must be corrected, and the underlying failure resolved, before acceptance. Per gate protocol a change that fails a required CI gate is not passable.

## 4. Non-blocking observations

- **O1 (residual #1 phrasing).** Residual #1 states that if the CLI's max-turns semantics are cumulative and a worker truly exhausts every turn, the injected reserved turn "may be refused by the CLI — landing in the fast honest-failure path, not a hang." This is accurate only if the refusal emits a terminal `result`. If the exhausted CLI silently swallows the idle-injected reserved turn (no result, stream left open), then `expected_results (2) > results_seen (1)` persists and the unit still rides the 900 s wall watchdog into a counted tree-termination. That worst case is genuinely narrower and safer than the original defect (the worker is no longer truncated; turn 1 completed), and it is watchdog-bounded — not an infinite hang or a false success — but it is not strictly "not a hang." The fake fixtures (`never_checkpoint` emits a result per prompt) do not exercise this silent-refusal sub-case, consistent with it being unmeasured. Recommend tightening residual #1's wording to state the watchdog-bounded wall-ride sub-case explicitly. Not blocking.
- **O2 (whole-suite figure).** The 3,039-passed whole-supervisor-suite figure was not independently re-run (per instruction, not to be re-run at scale). The runner pack (78) is independently confirmed green; the whole-suite claim is plausible given the localized change but is accepted on recorded evidence only.

## 5. Scope

The implementation commit touches exactly the three `allowed_paths`, and the behavior change is confined to `run_unit` + the new helper (verified via `git show --numstat`; loop.py/turn_budget.py callers unchanged). Scope of *edits* is clean. However — see C1 — the change as delivered cannot pass CI within that scope, because the modularity remediation necessarily touches `modularity_baseline.json`/`modularity_exceptions.json`, which are outside the packet's `allowed_paths`.

## 6. Verdict rationale

The runtime fix is well-designed, correctly handles the enumerated edge cases, is honestly tested (including a real red-on-mutant), and its repurposed test is a legitimate semantics change rather than evidence-weakening. But at the frozen reviewed identity the change **fails a required CI gate** (`modularity_check --check`, exit 1) and the producer's G2 self-check, fix report, and commit message all **falsely assert that gate passed**. Both must be resolved (C1: make the checker pass, via a reviewed baseline/exception update that will require a scope amendment; C2: correct the false evidence).

Required corrections, both blocking:
- **C1 (HIGH):** Resolve the `modularity_check --check` exit-1 failure on `tools/agent_supervisor/claude_runner.py` (1400 SLOC > 1383 limit) via a reviewed baseline update or path-exact expiring exception with a recorded cohesion justification; this needs a task-scope amendment (target file is outside `allowed_paths`). Re-run the checker to exit 0.
- **C2 (HIGH):** Correct the false "modularity 0 failures / PASS" claims in `M0-T130-G2-self-check.md`, `M0-T130-reserved-turn-fix.md` s3, and (as an amendment note) the commit record; fix the "+~45 SLOC" figure to reflect the checker's baseline-relative growth.

VERDICT: FAIL
---VERBATIM-END---
