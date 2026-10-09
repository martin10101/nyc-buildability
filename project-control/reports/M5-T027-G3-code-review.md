# Gate Report

> Saved VERBATIM by the orchestrator from the code-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.
> Orchestrator note on the reviewer's material-commit correction: CONFIRMED and adopted —
> the content commit is `77558eb5` (the cherry-pick of producer `b57998a6`); `bb1b37b8` is
> the follow-up integration seam commit carrying only state.json + the M4-T021 deviation
> note. The evidence map's "material_commit" line was corrected accordingly (claim-document
> correction, tagged; the evidence map is outside allowed_paths so material identity is
> unaffected).

- Gate ID: G3
- Task ID: M5-T027
- Reviewer: code-reviewer (independent, unnamed spawn)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t027`)
- Result: **PASS**
- Clean environment/worktree used: primary checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, verified at pinned review head `5cccf467` before inspection. Note: HEAD advanced to `8271331a` during the review (orchestrator opened blocker `B-024`, unrelated to this task — `git log --oneline 5cccf467..8271331a` shows only that one commit). `git merge-base --is-ancestor bb1b37b8 8271331a` confirms the reviewed material commit is still an ancestor and byte-identical at the content level I inspected (`git show <sha>:<path>` used throughout, so content identity is unaffected by the branch tip moving). Identity note recorded per the frozen-head-pattern precedent.

## Acceptance criteria reviewed

`project-control/tasks/M5-T027.json` objective + S1–S5 acceptance scenarios; `project-control/directives/D-059-mvp-review-dependable-answers/requirements.json` R001/R002/R003/R011; `source-001.md` findings 1–3 (verbatim reviewer reproduction); `project-control/reports/M5-T027-producer-report.md` (treated as claims to reproduce, not evidence).

## Material commit identity

- Task packet cites material commit `bb1b37b8` as "cherry-pick of producer commit `b57998a6`, byte-identical."
- `bb1b37b8`'s own diff (`git show --stat bb1b37b8`) touches only `project-control/state.json` and `project-control/tasks/M4-T021.json` — it does **not** contain the scenario-layer changes. The actual content commit is its parent, `77558eb5` ("M5-T027 producer: D-059 step-1 dependable-answers fixes"), which touches exactly `builder.py`, `constants.py`, `unused_floor_area.py`, `test_scenario_foundation.py`, `test_unused_floor_area.py`, and the producer report — matching `allowed_paths` exactly (6 files, no `test_scenario_contract.py` edit needed, confirmed correct: it required no changes).
- `git diff b57998a6 77558eb5` on the five contracted code/test files: **empty** (byte-identical). The only diff between the two commits is the unrelated `D-060` directive-capture files (`project-control/directives/D-060-*`, `index.json`), present in `77558eb5`'s branch ancestry (via parent `d7c22f3e`, a sibling commit on the integration branch) but absent from the producer's isolated-worktree commit `b57998a6` — expected given differing branch histories, not a cherry-pick defect.
- **Verdict: byte-identity confirmed; scope confirmed exact.**

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-059-R001 (recorded-data semantics) | `77558eb5` | PASS | `constants.py:88-112` (`UNUSED_FLOOR_AREA_LABEL`, `UNUSED_FLOOR_AREA_SCOPE_NOTE`) no longer call the result "a zoning floor-area difference"; explicitly states PLUTO `bldgarea` is "not a confirmed existing ZR 12-10 zoning floor area figure", names rights-calculation preconditions (compatible existing zoning-floor-area input + confirmed zoning-lot extent). `grep` confirms no residual "zoning floor-area difference" wording for the `unused_floor_area` surface outside the fixed files (`__init__.py` is a re-export only). Web presentation is honestly disclosed as out-of-scope (`apps/web/**` forbidden). Test `test_s6_no_forbidden_nouns_and_no_verified_compliant_language` (unchanged, still passes) plus my own read of the live strings. |
| D-059-R002 (bldgarea-zero fail-closed) | `77558eb5` | PASS | `unused_floor_area.py:415-444` — new branch (b2): `bldgarea==0.0` routes to `EXISTING_BUILDING_AREA_UNUSABLE` (value `null`, `professional_review_required=True`) unless the *same profile's* `numbldgs` fact establishes vacancy (present, usable coverage, exactly `0`). Verified by direct code inspection AND by independently diffing the pre-fix file (`git show 7150edef:...unused_floor_area.py`): the old code has **zero** references to `numbldgs` and unconditionally treats `existing_area==0.0` as `COMPUTED = cap - 0.0 = cap` — exactly the reviewer's reproduced defect (one building, bldgarea 0, cap 10000 → old code returns `computed=10000`, no reason, no PRR flag). Confirms the producer's RED-on-old claim is accurate without needing to execute the swap myself. |
| D-059-R003 (labels from actual evaluation) | `77558eb5` | PASS (within its own contracted surface; see A1) | `constants.py:256-262` (`COVERAGE_MATRIX` residential_far_cap row is now family-agnostic by default), `constants.py:300-337` (`_residential_far_family_label`/`coverage_matrix_rows` derive the "(R5)"/"(R6-R12)" suffix from the actually-evaluated `rule_id`), `constants.py:34-51`/`157-172` (`draft_cap_label`/`preliminary_cap_reason` derive the ZR section from the rule's own citation via `builder.py:355-367 _cap_citation_section`). Independently verified the R6-R12 test fixture (`test_scenario_foundation.py:420-468`) against the real ruleset file `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json`: R9A standard FAR `7.52` and section `"23-22"` match byte-for-byte — the derivation test is a genuine hand-derived fixture, not a tautology. |
| D-059-R011 (external fact, PLUTO zero-w/-buildings rule) | `77558eb5` | PASS | Producer cites `pluto_soda.py:201-202` (bldgarea condo net/gross + not-ZR-12-10 note) and `pluto_soda.py:784-791` (numfloors sibling precedent, dictionary p.28). Both citations verified accurate by direct read. Minor note: the producer re-cites the directive's already-captured 22v1 URL rather than independently re-fetching the live nyc.gov PDF at consumption time (see A4) — acceptable given sandbox network constraints and no new conflict surfaced. |

## Steps independently executed

1. `git rev-parse HEAD` at session start = `5cccf467` (pinned). Re-checked at session end = `8271331a` (see identity note above; reviewed content unaffected).
2. `git show --stat bb1b37b8`, `git show --stat 77558eb5`, `git log --oneline -15 -- services/api/app/scenario/{unused_floor_area,constants,builder}.py`, `git diff b57998a6 77558eb5` (all 5 contracted files), `git diff 45f63efb 77558eb5 -- packages/`, `git diff 7150edef 77558eb5 -- services/api/pyproject.toml services/api/requirements.in services/api/requirements.txt` — all read-only git inspection.
3. `python -m pytest services/api/tests/scenario -q` → **431 passed** (matches producer's claim exactly).
4. `python -m pytest services/api/tests/scenario/test_scenario_contract.py -q` → **28 passed**.
5. `python -m pytest services/api/tests/scenario/test_scenario_derive.py -q` → **70 passed** (out-of-scope `DRAFT_CAP_LABEL` consumer, confirmed unaffected).
6. `cd services/api && python -m ruff check .` → **All checks passed!**
7. `python tools/modularity_check.py --check` (from repo root) → **selected 405 files; failures 0; warnings 17**, none on `app/scenario/{unused_floor_area,constants,builder}.py`.
8. `cd services/api && python -m pytest tests -q --ignore=tests/documents` → **1 failed, 2435 passed** — matches the producer's claim exactly; the 1 failure (`test_contract_serializers.py::test_serializer_imported_exactly_at_the_profile_write_boundary`) is the pre-existing Python-3.11-vs-3.12 PEP-695 sandbox gap in `app/documents/units.py` (line 276, `def _match_unit[UnitT: enum.Enum](`), confirmed untouched by this task (`git status --porcelain` clean, last touched by an unrelated commit).
9. `git show 7150edef:services/api/app/scenario/unused_floor_area.py` (full file, read-only) to independently confirm the pre-fix code's zero-handling logic and the RED-on-old claim, since a live file-swap-and-rerun was blocked by the reviewer's write guard (correctly — that would be a file write).
10. Grep sweep for residual "23-21"/"(R5)"/"non-R5" across `services/api/app/scenario/*.py` and for "unused_floor_area"/"zoning floor-area difference" wording spread — see Regression findings below.
11. `git diff 7150edef 77558eb5` full-file diffs for both modified test files, confirming purely additive changes (no weakened/removed pre-existing assertions) except the one explicitly-contracted rename/correction of the miscast "vacant lot" test.

## Expected versus actual

All S1–S5 scenarios and R001/R002/R003/R011 behave as contracted. No divergence between the producer's report and the reproduced evidence on any claim I checked.

## Evidence paths

`services/api/app/scenario/unused_floor_area.py`, `services/api/app/scenario/constants.py`, `services/api/app/scenario/builder.py`, `services/api/tests/scenario/test_unused_floor_area.py`, `services/api/tests/scenario/test_scenario_foundation.py`, `services/api/app/connectors/pluto_soda.py` (read-only), `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` (read-only), `project-control/reports/M5-T027-producer-report.md`.

## Regression/security/provenance findings

**A1 (important, non-blocking — recommend immediate follow-up).** The universal hardcoded `"ZR 23-21"` label defect that R003 fixes in `constants.py`/`builder.py` **also exists, unaddressed, in five other scenario-package modules that are wired into the live `scenario_analysis.py` API endpoint** (confirmed: `main.py` mounts `scenario_analysis_v1_router`, which imports `analyze_scenario_sensitivity`, `compare_scenario_assumption_sets`, `find_scenario_threshold`, `rank_scenario_assumption_sets` — all of which route through `derive.py`'s `derive_practical_usable_range`):
  - `services/api/app/scenario/derive.py:82` — `DERIVED_RANGE_LABEL` module constant, **unconditionally** emitted as the `"label"` field of every `derived_practical_usable_range` document (not a fallback — always used), hardcodes `"(ZR 23-21)"` regardless of the actually-evaluated district family.
  - `services/api/app/scenario/breakeven.py:155`, `comparison.py:118,129`, `ranking.py:114`, `sensitivity.py:128` — same hardcoded `"ZR 23-21"` phrasing in reason/label text.

  This is **outside M5-T027's `allowed_paths`** (none of these six files are listed) and outside D-059-R003's own textual scope (which names only `constants.py`/`builder.py`), so it does not constitute a scope violation or invalidate this task's PASS. However, the producer's report discusses only the `DRAFT_CAP_LABEL` legacy-alias risk (verified true and harmless, see below) and does **not** disclose this broader, more materially live instance of the same defect class — even though it sits in the same package the producer was working in and is reachable through a live-wired endpoint. Recommend the orchestrator open an immediate D-059-R003 follow-up task covering `derive.py`/`breakeven.py`/`comparison.py`/`ranking.py`/`sensitivity.py` before treating "R003 resolved" as a complete claim project-wide.

**A2 (minor, non-blocking).** `unused_floor_area.py:184-212` (`_zero_with_buildings_assumptions`) produces the rationale text "numbldgs was not present in the property profile" whenever `raw_numbldgs_value` is `None` — this is correct when the fact is genuinely absent, but the same code path also fires when the fact dict is *present* with an explicit `value: null` (e.g. `{"value": None, "coverage_status": "conditional"}`), which is a different, real data-quality signal (a recorded-but-null value vs. a column that was never populated). This untested edge case produces a technically-inaccurate assumption rationale (though the fail-closed *behavior* itself is correct — value stays `null`, state stays `not_computable`). Consistent with how `bldgarea`'s own case (a) treats "no fact" and "fact present but value null" identically, so this is not a new departure from existing project convention, but worth tightening in a future pass.

**A3 (informational).** `builder.py` is now 969 lines (was ~928 pre-fix), approaching the code-modularity "hard" threshold (1,000 SLOC). `modularity_check.py --check` reports 0 failures and no new warning for this file, so no action is required now, but a future addition to `builder.py` should re-run the checker before growing it further.

**A4 (minor, non-blocking).** D-059-R011 asks the consuming task to "re-verify against the current official dictionary." The producer re-cited the directive's already-captured 22v1 URL/finding rather than independently re-fetching the live nyc.gov PDF at consumption time. Reasonable given sandbox network constraints and the fact that the connector's own source notes corroborate the same distinction; no conflict was found or should have been expected to surface differently.

No hidden defaults, no coercion, no silent uncertainty, no missing provenance, and no incompatible/broken schema contract were found in the contracted surface. `packages/contracts/schemas/v1/scenario.schema.json` is confirmed untouched (`test_s6_both_schema_copies_are_byte_identical` passes; no diff in `77558eb5`'s own stat). Zero new dependencies confirmed (no diff in `pyproject.toml`/`requirements.in`/`requirements.txt`).

## Defects

None blocking.

## Required rework

None required for M5-T027 acceptance. Recommend (not blocking this gate): open a follow-up task for A1 (the five-file `"ZR 23-21"` hardcode surviving in the Compare/ranking/sensitivity/breakeven path, live-wired via `scenario_analysis.py`).

## Reviewer conclusion

The material commit is byte-identical to the producer's own commit on the contracted files, touches exactly the `allowed_paths`, and leaves `forbidden_paths` (including `packages/contracts/**` and the response schema/enum vocabulary) untouched — confirmed by direct diff, not by trusting the producer's stat. All three D-059 correctness fixes (R001 wording, R002 zero-with-buildings fail-closed, R003 evaluation-derived labels) are implemented correctly, fail closed on every ambiguous/malformed `numbldgs` shape I could construct (absent, null-valued, bad coverage_status, non-numeric, negative), and are proven by genuinely hand-derived tests (the R6-R12 fixture's FAR 7.52/section 23-22 independently verified against the real ruleset file) rather than tests that merely echo the code under test. I independently reproduced the RED-on-old claim by reading the pre-fix file directly (the old code has zero `numbldgs` awareness and unconditionally computes `cap - 0.0 = cap` for a zero-area building) rather than accepting the producer's narrative. Full scenario suite (431), contract suite (28), and full `services/api` suite (2435 passed / 1 pre-existing unrelated failure) all reproduced independently and match the producer's report exactly; ruff and modularity checks are clean.

**Verdict: PASS.** A1 is flagged as an important, non-blocking advisory for an immediate follow-up task, since it surfaces that the underlying D-059 finding-3 defect class is only partially resolved project-wide even though M5-T027 itself is complete and correct within its contracted scope.
