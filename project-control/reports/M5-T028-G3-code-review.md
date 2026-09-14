# G3 Code Review Report — M5-T028

> Saved VERBATIM by the orchestrator from the code-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

- Gate ID: G3
- Task ID: M5-T028
- Reviewer: code-reviewer (independent, read-only)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t028`)
- Result: **PASS**
- Clean environment/worktree used: primary checkout, read-only, no writes made. Reviewed content identity pinned at material commit `7e7cd85e` (cherry-picked onto integration head `99f9b277`).

## Identity note (HEAD drift during review — control-plane only)

At review start `git rev-parse HEAD` = `99f9b277` (matches the pinned review head). Partway through the review, HEAD advanced to `e514117681c9cffc7fdff9c741f111506cc7a421` via four commits (`3abd7b66`, `88ad3a9f`, `386222dc`, `e5141176`) — all M5-T027 G5/accept bookkeeping (a **different, already-accepted task**). `git diff 99f9b277 e5141176 --name-only` touches only: two directive `verification.json` files, `M5-T027-G5.json` + its report, `state.json`, `M4-T021.json`, and `M5-T028.json`. The only touch inside my review scope is `project-control/tasks/M5-T028.json`, and its diff is exactly one line — appending `"security-reviewer"` to `reviewer_agents` (a roster correction mirroring the same fix applied to M5-T027/M4-T021) plus an `updated_at` timestamp bump; `allowed_paths`, `forbidden_paths`, `acceptance_scenarios`, and `directive_refs` are byte-unchanged. This is a control-plane-only commit per the reviewer instructions; the reviewed source/test content identity (material commit `7e7cd85e`) is unaffected. All findings below are verified against that content, present unchanged at the final HEAD.

Material commit `7e7cd85e` touches exactly 11 files: `derive.py`, `breakeven.py`, `comparison.py`, `ranking.py`, `sensitivity.py`, their five test files, and `M5-T028-producer-report.md` — matching `allowed_paths` exactly (`git show 7e7cd85e --stat`, confirmed).

## Acceptance criteria reviewed

S1–S4 of `project-control/tasks/M5-T028.json`; the six judge items in the review packet; D-059-R003, D-046-R001, D-046-R002.

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-059-R003 | 7e7cd85e (11 files, cherry-picked onto 99f9b277) | PASS | Grep of all five modules for `23-21`/`23-22` shows the literal string appears only in comments, docstrings, and as an argument to build a documented backward-compatible legacy constant (`X_LABEL = _x_label("23-21")`) that is proven unread by any live path (`grep -rln` across `services/api` outside `scenario/`+its tests = empty; `scenario_analysis.py` never imports these constants). Every one of the 10 live emission call sites (`derive.py:309,530`; `breakeven.py:604,807`; `comparison.py:293(via 531/676),428(via 636),535,680`; `ranking.py:440,460,576`; `sensitivity.py:468,490,613`) calls `_x_label(_cap_section_reference(scenario_document))` with the live per-request document. `_cap_section_reference` (derive.py:106) reuses `builder._cap_citation_section` (the accepted M5-T027 seam, builder.py:355) unmodified. Traced two surfaces end-to-end (derive.py, comparison.py) from call site → helper → emitted string. Fallback is a generic, section-agnostic clause in all five modules when `cap_provenance`/citation is absent — never a default to 23-21 (verified in source and by `test_d059_r003_derived_range_label_is_generic_with_no_cap_provenance`). Reran `pytest services/api/tests/scenario -q` → **443 passed** (matches producer claim exactly, includes 12 new tests). |
| D-046-R001 (scale-up: ≥1 concurrent producer where disjoint ready work exists) | n/a to a single task's source diff | UNVERIFIABLE from code review | This is a campaign-dispatch-record requirement, not something a single task's file diff can prove or disprove. Outside G3 code-review scope; belongs to the directive-compliance-verifier's evidence (dispatch/progress-log record across the campaign), not this task's `allowed_paths`. |
| D-046-R002 (disjointness — no concurrent overlapping-scope dispatch) | 7e7cd85e | PASS (code-level evidence only) | M5-T028's `forbidden_paths` correctly excludes M5-T027's own files (`constants.py`, `builder.py`) and M4-T021's connector lane (`services/api/app/connectors/**`), and the actual diff never touches them (`git diff 2231227a 99f9b277 --name-only` confirms). Scope is disjoint by construction, as the packet's own `path_notes` state. Full dispatch-record verification (were two producers ever run concurrently with overlapping paths) is outside what a single task's diff can establish and is directive-compliance-verifier territory. |

## Steps independently executed

- `git rev-parse HEAD` (99f9b277 at start; drift explained above).
- `git show 7e7cd85e --stat` — confirmed 11-file scope.
- `git diff 2231227a 99f9b277 --name-only` and per-file `git diff 2231227a 99f9b277 -- <file>` for all five production modules — full prose diff read for S3.
- `grep -rn "23-21" / "23-22"` across the five modules (both loose and combined) — completeness check for item 1.
- `grep -rn "DERIVED_RANGE_LABEL\|THRESHOLD_LABEL\|COMPARISON_LABEL\|RANKING_LABEL\|SENSITIVITY_LABEL\|_METRIC_LABELS"` across `services/api/app/` and `services/api/app/api/v1/scenario_analysis.py` — confirmed legacy constants are not read on any live path.
- Read `builder.py:355-368` (`_cap_citation_section`) to confirm the reused seam's semantics.
- Read all five modules' call sites of `_cap_section_reference`/`_x_label(...)` to confirm live wiring (item 2).
- Read `test_as7_module_imports_are_contract_free` (breakeven) / `test_as7_module_imports_only_allowed_dependencies` (comparison) verbatim; confirmed `ranking.py`/`sensitivity.py`/`derive.py` test files carry no equivalent import-boundary test.
- Read `comparison.py::_metric_delta` (428-495) and its two call sites (293/531/676, 636) to verify the optional 4th parameter is always explicitly supplied on the live path and only defaults in isolated unit calls; read the two pre-existing 3-arg tests (`test_as4_percent_delta_against_zero_baseline_is_not_computable`, `test_as4_absent_or_nonfinite_baseline_metric_is_not_computable`) — neither asserts on `metric_label`.
- Read the new `test_d059_r003_*` tests in all five test files; verified expected section strings (`23-21`/`23-22`) against the real ruleset files (`grep "\"section\"" r6_r12_residential_far.rule.json r5_residential_far.rule.json` → line 20 in each, `23-22`/`23-21`) — not tautologically derived from the code under test.
- Ran `python -m pytest services/api/tests/scenario -q` → **443 passed** (matches).
- Ran `python -m pytest services/api/tests/scenario/test_scenario_contract.py -q` → **28 passed** (matches).
- Ran `cd services/api && python -m ruff check .` → **All checks passed** (matches).
- Ran `python tools/modularity_check.py --check` (from repo root) → **selected 405 files; failures 0; warnings 17** (matches producer claim; `breakeven.py` warning confirmed pre-existing — file was already 784 lines, above the 750 "justify" threshold, at the base commit `2231227a`, before this task added 29 net lines).
- Diffed `services/api/tests/scenario/_support.py` and `test_scenario_foundation.py` (2231227a→99f9b277) → empty, confirming the shared test fixtures the new tests' local `_r6_r12_rule_evaluation()` helper mirrors were not touched.
- Confirmed via `grep` that `services/api/app/api/v1/scenario_analysis.py` imports and calls all five live functions (`analyze_scenario_sensitivity`, `rank_scenario_assumption_sets`, `compare_scenario_assumption_sets`, `find_scenario_threshold`, and transitively `derive_practical_usable_range`).

## Expected versus actual

All producer-report claims (443/443, 28/28, ruff clean, modularity 0 failures/17 warnings, 11-file scope, both call sites in `_metric_delta`, section values 23-21/23-22 from the ruleset files) were independently reproduced and matched exactly. No discrepancy found between the producer's narrated evidence and the actual repository/test state.

## Evidence paths

`project-control/reports/M5-T028-producer-report.md`; `services/api/app/scenario/{derive,breakeven,comparison,ranking,sensitivity}.py`; `services/api/tests/scenario/test_scenario_{derive,breakeven,comparison,ranking,sensitivity}.py`; `services/api/app/scenario/builder.py:355-368`; `services/api/app/rules/rulesets/{r5_residential_far,r6_r12_residential_far}.rule.json:20`.

## Human-style walkthrough findings

N/A — backend, non-UI task.

## Regression/security/provenance findings

None. Provenance prose (DRAFT labelling, "transported VERBATIM," typed-assumption language, "NOT gross/net/sellable/feasible," "NOT Verified") is byte-identical to the pre-fix text apart from the section-reference clause in all five modules — verified by direct diff read for each file, not by trusting the producer's stated byte-comparison script output.

## Ruling on item 3 (routing the shared extraction through `.derive` instead of `.builder`)

**Verdict: respects the intent of the boundary test — not a violation.** Reasoning:
1. The two pre-existing AS-7 tests (`test_scenario_breakeven.py::test_as7_module_imports_are_contract_free`, `test_scenario_comparison.py::test_as7_module_imports_only_allowed_dependencies`) are, by their own docstrings, an **allowlist** ("Only stdlib + .derive + .constants + ._json_safety" / "imports only stdlib + .derive + .constants + ._json_safety"), not a general "must be dependency-graph-isolated from builder" rule. `.derive` is explicitly a sanctioned collaborator for both modules.
2. `derive.py` carries no equivalent import-boundary test forbidding `from .builder import ...` (confirmed empty grep against `test_scenario_derive.py`), so extending `derive.py`'s own import surface by one pure, read-only, side-effect-free helper (`_cap_citation_section`) does not violate anything binding on `derive.py` itself.
3. There is no dependency cycle: `builder.py` imports only `.constants`, `.models`, `.unused_floor_area`, none of which import back from `derive`/`breakeven`/`comparison`/`ranking`/`sensitivity` — confirmed by grep. The layering stays one-directional (builder → derive → siblings).
4. The task packet itself mandated **reusing** the M5-T027 seam "rather than introducing a second mechanism" — duplicating `_cap_citation_section`'s extraction logic five times, or bypassing `.derive` to import `.builder` directly into `breakeven.py`/`comparison.py` (which the AS-7 tests would literally fail), were the two worse alternatives. Centralizing the derivation once in `.derive` — the module every sibling already legitimately depends on — is the correct DRY resolution consistent with both the packet's mandate and the tests' own allowlist.

Advisory (non-blocking): the AS-7 tests are literal substring checks on a module's own source text, not an AST/import-graph transitive-closure check, so they cannot by construction detect a deep transitive reach into `builder`. This task did not exploit that gap in bad faith (the reuse is narrow — one pure function — and openly disclosed in both the producer report and in-code comments), but a future reviewer relying on AS-7 to guarantee zero-builder-dependency-graph should know it only checks the direct import line. Recommend (not required here) hardening AS-7 to an AST-based transitive check in a future task if that stronger guarantee is actually wanted.

## Other advisory findings (non-blocking)

- **A1** — `_r6_r12_rule_evaluation()` is duplicated near-verbatim across all five new test files (`test_scenario_derive.py`, `test_scenario_breakeven.py`, `test_scenario_comparison.py`, `test_scenario_ranking.py`, `test_scenario_sensitivity.py`), each an independent copy of `test_scenario_foundation.py`'s own helper. This is disclosed and forced by scope (`test_scenario_foundation.py` is outside `allowed_paths`), so it is a defensible scope-boundary consequence, not sloppiness — but it is a five-way maintenance liability if the R6-R12 fixture shape ever changes. Consider a follow-up task to promote a shared helper into `tests/scenario/_support.py`.
- **A2** — the in-code comments on the five backward-compatible legacy constants (`DERIVED_RANGE_LABEL`, `THRESHOLD_LABEL`, `COMPARISON_LABEL`, `RANKING_LABEL`, `SENSITIVITY_LABEL`) describe "a small set of consumers OUTSIDE this task's allowed_paths that import [X] directly (scenario/__init__.py's re-export)" — but `grep -rln` across `services/api` outside the `scenario/` package and its own tests found **zero** actual external importers today; the only "consumer" is the `__init__.py` re-export/`__all__` facade itself. Harmless (the constants are still correct, unused legacy aliases, not a functional defect), but the comment slightly overstates present usage.
- **A3** — the `contracts-typegen` and `contracts-schema-bundle` CI jobs (Node-based) were not independently executed in this sandbox (not in the documented/authorized command set). Risk assessed low: no `packages/**` file is in the diff, no response field/enum was added, removed, or retyped — only string label *content* changed — and the Python-side contract suite (28/28) passed. Flagging as not independently executed rather than asserting pass.

## Defects

None found. No hardcoded "ZR 23-21" section assertion remains in any of the five modules on any live path (item 1: PASS). Derivation correctness traced end-to-end with correct fail-safe (generic, never-23-21) fallback (item 2: PASS). The `.derive`-routing design decision respects the boundary tests' intent (item 3: PASS, see ruling above). The `_metric_delta` optional 4th parameter weakens no existing assertion — the two 3-arg tests never examine `metric_label`, and the live call site always supplies the argument explicitly (item 4: PASS). Provenance prose is byte-identical apart from the section clause across all five modules (item 5: PASS). No tautological tests, no new dependency, `packages/**` untouched, ruff clean, modularity 0 failures (item 6: PASS).

## Required rework

None.

## Reviewer conclusion

**PASS.** All six judged items verified independently against source and reproduced test runs at the pinned content identity (material commit `7e7cd85e`, integration head `99f9b277`, unaffected by subsequent control-plane-only commits through `e5141176`). D-059-R003 is genuinely closed across all five live-wired modules with correct fail-safe behavior; D-046-R002 is satisfied by construction at the code level (D-046-R001 is a campaign-dispatch fact outside this review's evidence and is left UNVERIFIABLE here for the directive-compliance-verifier). No blocking findings; three non-blocking advisories recorded (A1–A3) plus the explicit, non-blocking ruling on item 3.
