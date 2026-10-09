# Gate Report

> Saved VERBATIM by the orchestrator from the qa-engineer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

- Gate ID: G4 (test-adequacy)
- Task ID: M5-T027
- Reviewer: qa-engineer (independent, read-only)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t027`)
- Result: **PASS**
- Clean environment/worktree used: Reviewer session HEAD was `d8b3899f` (isolated worktree, not the pinned review head). Per skill instructions I did not rely on the worktree's live tree — I read all pinned content via `git show 5cccf467:<path>` (shared object store) and executed all commands against a `git archive 5cccf467` extraction (`scratchpad/review-extract`), plus a second `git archive b57998a6^` extraction of the pre-fix parent (`scratchpad/review-parent-extract`) for independent red-on-old reproduction. No writes were made anywhere outside `scratchpad/` and `.claude/agent-memory/qa-engineer/`; no `project_control.py`/git/gh state-changing command was run.

## Content-identity check (first)

- `git rev-parse HEAD` in the assigned worktree = `d8b3899f61efa6620e18a26541ced96020f5bef9` (≠ pinned `5cccf467`), confirming the isolated-worktree case named in the task brief.
- All three named commits resolve in the shared object store: `5cccf4677a8a54e375329658ed678be5483208d` (submission commit), `bb1b37b820cab4b88ad8d0f7a9ece3ec1a6a74a1` (integration/cherry-pick commit), `b57998a6c5881ceee4caf5136d646780d1764f4f` (producer commit).
- Blob-hash identity confirmed for every in-scope file across producer commit → integration commit → pinned review head (all three identical):
  - `services/api/app/scenario/unused_floor_area.py` → `df52e5d9...`
  - `services/api/app/scenario/constants.py` → `6ab50664...`
  - `services/api/app/scenario/builder.py` → `b7610a29...`
  - `services/api/tests/scenario/test_unused_floor_area.py` → `839e6a0c...`
  - `services/api/tests/scenario/test_scenario_foundation.py` → `bdfb0a17...`
  - Producer commit `git show --stat b57998a6`: exactly the 5 code/test files + the producer report inside `allowed_paths`; `test_scenario_contract.py` blob unchanged (`19f30ed8...` before and after).
  - `packages/contracts/schemas/v1/scenario.schema.json` blob unchanged (`f8f3d0d5...` before/after — zero schema-change confirmed, not just claimed).
  - `services/api/app/scenario/models.py` blob unchanged (`986550b4...` before/after — no new enum value, confirmed).
- "Cherry-pick b57998a6, byte-identical" claim in the bb1b37b8 commit message: **verified true** for the scope files (the bb1b37b8 diff itself shows only `state.json`/`M4-T021.json` changed — the M5-T027 payload landed via its parent 77558eb5, whose file blobs are byte-identical to b57998a6's).

## Acceptance criteria reviewed

S1–S5 of `project-control/tasks/M5-T027.json`, cross-checked against D-059-R001/R002/R003/R011 (`requirements.json`). My checklist per the orchestrator's assignment: (1) derive the zero-handling decision table myself and verify branch coverage; (2) independently establish red-on-old (not trust the claim); (3) audit the corrected miscast vacancy test for weakened/removed assertions; (4) audit R003 label tests for non-tautology; (5) isolation/hygiene/count reconciliation.

## My own derived decision table (from `unused_floor_area.py` at 5cccf467, not from the report)

| # | Condition | Outcome | Covered by |
|---|---|---|---|
| 1 | no positive draft cap (`cap_value` non-positive/None/NaN) | `NOT_COMPUTABLE` / `NO_DRAFT_FAR_CAP`, PRR=False | `test_s5_no_cap_paths_are_no_draft_far_cap` (6 rule-evaluation variants), `test_s5_section_is_present_on_degenerate_empty_inputs`, `test_direct_pure_function_zero_cap_is_no_draft_far_cap` |
| 2 | cap present, no bldgarea fact / fact value null | `NOT_COMPUTABLE` / `MISSING_EXISTING_BUILDING_AREA`, PRR=False | `test_s4a_missing_existing_area_fact_is_not_computable` (both no-fact and fact-with-null-value sub-cases) |
| 3 | cap present, fact present, coverage_status unusable OR non-numeric/negative value (non-zero) | `NOT_COMPUTABLE` / `EXISTING_BUILDING_AREA_UNUSABLE`, PRR=False | `test_s4b_unusable_existing_area_echoes_coverage_status` (`data_conflict`,`unsupported`), `test_s4b_present_but_nonnumeric_value_is_unusable` (`"9000"`, `-1.0`, `nan`) |
| 4a | bldgarea==0, usable coverage, numbldgs present+usable+==0 (established vacancy) | falls through to COMPUTED path, value=cap | `test_s1_established_vacancy_zero_existing_area_is_usable_and_computed` |
| 4b-i | bldgarea==0, numbldgs present+usable+**positive** | `NOT_COMPUTABLE` / `EXISTING_BUILDING_AREA_UNUSABLE`, PRR=True (both levels), 2 assumptions | `test_s1_zero_with_positive_numbldgs_fails_closed_red_on_old` |
| 4b-ii | bldgarea==0, numbldgs **absent** | same as above | `test_s1_zero_with_absent_numbldgs_fails_closed` |
| 4b-iii | bldgarea==0, numbldgs present but coverage_status unusable | same as above | `test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[data_conflict\|unsupported]` |
| 4b-iv | bldgarea==0, numbldgs present+usable coverage but **non-numeric value** | same as above | `test_s1_zero_with_nonnumeric_numbldgs_fails_closed` |
| 5a | bldgarea>0 (or vacancy-established 0), value = cap − area < 0 | `OVER_BUILT`, PRR=True (both) | `test_s2_over_built_honest_negative` |
| 5b | value ≥ 0 | `COMPUTED` | `test_s1_computed_normal_remainder`, `test_s3_zero_boundary_is_computed_not_over_built` (boundary value==0), `test_s1_fractional_remainder_is_unrounded` |

**All branches of the S1/S2-relevant decision table are covered.** No uncovered blocking branch found.

**NB-1 (non-blocking):** `_zero_with_buildings_assumptions`'s three internal message-text branches ("not present" / "positive count" / "not usable") are reachable via 4 distinct outer conditions, but one intra-branch permutation is untested: numbldgs present with a **usable coverage_status and a negative numeric value** (e.g. `-1`) takes the same "not usable (coverage_status or value)" wording branch as the tested non-numeric-value case, and a **boolean** numbldgs value (`True`/`False`) is routed by `isinstance(..., bool)` into the "not present" wording branch even though it was technically present — both are pure rationale-text nuances, not state-machine branches (outcome is identical NOT_COMPUTABLE/EXISTING_BUILDING_AREA_UNUSABLE/PRR=True in every case, already proven by the 4 tested variants). Not blocking: PLUTO's `numbldgs` field is not going to emit a boolean, and the negative-value case is functionally identical to the tested non-numeric case.

## Red-on-old verdict (independently reproduced, not trusted from the report)

Reproduced `git show b57998a6^:services/api/app/scenario/unused_floor_area.py` and diffed it against the fixed version. The OLD module has **no** `_numbldgs_fact`/`_vacancy_basis`/`_zero_with_buildings_assumptions` functions and no "(b2)" branch at all — any `existing_area == 0.0` with usable coverage status fell straight through to the COMPUTED/OVER_BUILT block, i.e. `value = cap - 0 = cap`, always COMPUTED for any positive cap, `not_computable_reason=None`, `professional_review_required=False`. `numbldgs` was never read.

I then physically swapped the OLD `unused_floor_area.py` into a copy of the pinned-head tree (module-only swap; NEW tests/builder/constants kept) and ran `tests/scenario/test_unused_floor_area.py`:

```
5 failed, 26 passed in 0.78s
FAILED test_s1_zero_with_positive_numbldgs_fails_closed_red_on_old
FAILED test_s1_zero_with_absent_numbldgs_fails_closed
FAILED test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[data_conflict]
FAILED test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[unsupported]
FAILED test_s1_zero_with_nonnumeric_numbldgs_fails_closed
```

This is an exact, independently-reproduced match to the producer's claimed "5 failed, 1 passed" (my run reports the same 5 failures against 26 total collected in the file, i.e. all other tests including the corrected vacancy test passed — consistent). Every one of the 5 new test items is **genuinely red-on-old**:

| New test | Old-code actual result | New assertion | Genuinely red-on-old? |
|---|---|---|---|
| `test_s1_zero_with_positive_numbldgs_fails_closed_red_on_old` | `computed`, value=cap, PRR=False, 1 assumption | `not_computable`/null/`existing_building_area_unusable`/PRR=True/2 assumptions | YES |
| `test_s1_zero_with_absent_numbldgs_fails_closed` | same as above | same as above | YES |
| `test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[data_conflict]` | same as above | same as above | YES |
| `test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[unsupported]` | same as above | same as above | YES |
| `test_s1_zero_with_nonnumeric_numbldgs_fails_closed` | same as above | same as above | YES |

I additionally spot-checked the R003 side the same way (not required by the "5 fail-closed tests" claim, but strengthens confidence): swapping OLD `constants.py`+`builder.py` into the pinned tree and running the 2 new `test_as_r003_*` tests in `test_scenario_foundation.py` gives `test_as_r003_low_density_r5_derives_coverage_and_section_labels` **PASSED** (expected — R5/23-21 was already correct under the old hardcoded scheme) and `test_as_r003_higher_density_r6_r12_derives_coverage_and_section_labels` **FAILED** (`AssertionError: '23-22' not in '...under ZR 23-21...'`) — confirming the higher-density test is a genuine regression-catching test for the R6-R12 stale-label defect, not a rename-only or tautological addition.

## Corrected miscast test audit (no weakened/removed assertions)

Diffed `test_unused_floor_area.py` against its immediate parent (`b57998a6^`). The old `test_s1_vacant_lot_zero_existing_area_is_usable_and_computed` called `profile_with_bldgarea(0.0)` with **no numbldgs fact at all** — under the fixed code this fixture would now fail closed, so simply renaming it would have broken the test. The diff shows it is genuinely fixed, not merely renamed: the fixture call became `profile_with_bldgarea(0.0, numbldgs=_vacant_numbldgs())`, i.e. it now actually establishes vacancy. Every original assertion in the test body (`state == COMPUTED`, `value == cap`, `not_computable_reason is None`, `existing_building_floor_area.value_sq_ft == 0.0`, `professional_review_required is False` at section and document level) is present unchanged in the new version — the diff shows only docstring/fixture-construction lines added, zero assertion lines removed or altered. No assertion anywhere in the diff was weakened or deleted; every change to `test_unused_floor_area.py` (`132 insertions, 9 deletions` per `git diff --stat` against the parent) is additive except the 9-line fixture-construction edit inside this one test, which is the vacancy-establishing correction itself. `test_scenario_foundation.py`'s diff against its parent is purely additive (two new tests + one new helper function, zero deletions of existing lines).

## R003 label-derivation test audit (real, non-tautological)

Read `_r6_r12_rule_evaluation()` in `test_scenario_foundation.py`: it builds a rule_evaluation trace with `rule_id = "r6-r12-residential-far"` and citation `section = "23-22"`, `snapshot_id = "zr-23-22"`. Cross-checked against the actual ruleset file `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` at 5cccf467: `"rule_id": "r6-r12-residential-far"` and `"section": "23-22"` — the fixture's values are not fabricated, they match the real rule. Both new tests assert against **hand-written literal strings** (`"draft max residential zoning floor area (R5)"`, `"draft max residential zoning floor area (R6-R12)"`, substring checks for `"23-21"`/`"23-22"`) — they never call `constants.draft_cap_label(...)` or `constants.coverage_matrix_rows(...)` to generate the expected value and then compare it to itself, so they are not tautological. The higher-density test additionally asserts negative space (`"23-21" not in document["cap_label"]`, `"R5" not in cap_row["governs"]`, no `"non-r5"` string survives anywhere in the coverage matrix), which is a meaningful defect-catching assertion, independently confirmed red-on-old above. One low-density (R5, canonical fixture) and one higher-density (R6-R12/R9A) district are both exercised, satisfying the packet's "at least one low-density and one higher-density district" requirement.

## Isolation / hygiene / count audit

- **Offline:** grepped all 5 touched files for network-call patterns (`requests.`, `httpx`, `urlopen`, `socket.`, bare `http(s)://`) — the only hit is a literal string value (`request_url="https://zoningresolution.planning.nyc.gov/..."`) inside a fixture's provenance dict field, not an executed network call. No import of an HTTP client anywhere in scope.
- **No shared mutable state / order-independence:** `tests/scenario/_support.py`'s `profile()` returns `copy.deepcopy(PROFILE)` and `canonical_rule_evaluation()` re-parses fresh JSON from disk on every call; `profile_with_bldgarea()` (in the edited test file) builds a fresh dict via `S.profile()` each call and `zoning_lot_extent_assumption()` in `constants.py` is documented and confirmed to return "a FRESH dict each call" — no test can leak mutated state into another. I ran the new/edited files both in isolation (31/38 items) and inside the full 431-item suite with identical pass counts, consistent with order-independence; no dedicated random-order plugin was available in the sandbox to force-shuffle, so this is inference from source inspection plus consistent isolated-vs-combined results, not a formal shuffle run.
- **Count reconciliation (independently executed, not trusted):**

  | Suite | Pre-fix (`b57998a6^`) | Pinned head (`5cccf467`) | Δ |
  |---|---|---|---|
  | `tests/scenario` (full) | 424 passed | **431 passed** | +7 |
  | `tests/scenario/test_scenario_contract.py` | n/a (unchanged file) | **28 passed** | 0 |
  | `tests/scenario/test_unused_floor_area.py` | 26 passed | 31 passed | +5 (matches producer's "5 new fail-closed tests"; the 6th changed test — the vacancy fixture — is a correction, not a net-new item, since it replaces the old miscast test 1-for-1) |
  | `tests/scenario/test_scenario_foundation.py` | 36 passed | 38 passed | +2 (matches the 2 new R003 derivation tests) |

  424 + 5 + 2 = 431 — reconciles exactly. Producer's claimed counts (431 scenario, 28 contract, "5 new fail-closed tests") are all independently confirmed correct.

## Steps independently executed

1. `python -m pytest services/api/tests/scenario -q` against `git archive 5cccf467` extraction → `431 passed in 3.20s`.
2. `python -m pytest services/api/tests/scenario/test_scenario_contract.py -q` → `28 passed in 0.22s`.
3. `cd services/api && python -m ruff check .` (ruff 0.13.0, matches CI-pinned version) → `All checks passed!`.
4. `python -m pytest services/api/tests/scenario/test_unused_floor_area.py -v` (pinned head) → 31 items, all PASSED (enumerated in transcript).
5. Module-only swap of pre-fix `unused_floor_area.py` into the pinned-head tree, re-ran `test_unused_floor_area.py` → `5 failed, 26 passed`, confirming red-on-old for all 5 new tests (transcript captured above).
6. `constants.py`+`builder.py`-only swap of pre-fix versions into the pinned-head tree, ran the 2 `test_as_r003_*` tests with `-k r003` → low-density PASSED, higher-density FAILED (`23-22 not in ...23-21...`), confirming red-on-old for the R6-R12 derivation test.
7. Baseline counts on `b57998a6^` (`git archive` extraction of the parent): `tests/scenario` → 424 passed; `test_scenario_foundation.py` → 36 passed; `test_unused_floor_area.py` → 26 passed.
8. Blob-hash (`git rev-parse <sha>:<path>`) identity checks across b57998a6 / 77558eb5 / bb1b37b8 / 5cccf467 for all 5 code/test files, `scenario.schema.json`, and `models.py`.
9. `git show --stat` on the producer commit and the integration commit to confirm scope.
10. `git diff --no-index` of old-vs-new for `unused_floor_area.py`, `constants.py`/`builder.py` (via a separate diff of `builder.py`), and both edited test files, read in full.
11. Grep-based offline check and schema inspection (`unused_floor_area_inputs` closed-shape confirmation) on the extracted tree.

Not independently executed (outside the explicitly authorized command list / outside G4 test-adequacy scope): the full `services/api/tests` suite, `tools/modularity_check.py --check`, and full directive-compliance verification of D-046-R001/R002 and D-059-R011's connector-source citation accuracy (`pluto_soda.py:201-202`/`:784-791` — that file is `forbidden_paths` for this task; I did not open it). These are producer-report claims I did not reproduce; they are not part of my assigned test-adequacy checklist and are properly the domain of the code-reviewer (G3, modularity) and the `directive-compliance-verifier` (full requirement verification.json) respectively. Flagging as **UNVERIFIABLE-BY-ME**, not FAIL, since my mandate was test adequacy specifically.

## Expected versus actual

Expected (per S1–S5 and the orchestrator's 5-point checklist): every zero-handling branch covered, all new tests genuinely red-on-old, the miscast test genuinely fixed with no weakened assertions, R003 tests real and non-tautological across both density tiers, and offline/order-independent/correctly-counted tests. Actual: all of the above independently confirmed true, with one non-blocking gap (NB-1) in message-text-branch coverage that does not affect any observable state-machine outcome.

## Regression/security/provenance findings

None. `models.py` and `scenario.schema.json` byte-identical before/after (no new enum, no schema change — both were forbidden_paths). Original recorded zero and numbldgs basis are traceable via the `assumptions` channel on the new fail-closed path, satisfying the provenance requirement. No new dependency, no e2e edit, no file outside `allowed_paths` touched.

## Defects

None blocking.

## Findings

- **F-none (no blocking findings).**
- **NB-1:** `_zero_with_buildings_assumptions`'s rationale-text branch for a negative-numeric or boolean `numbldgs` value is untested (see decision-table note above); functionally identical outcome to already-tested variants, cosmetic-only, not state-affecting. Suggest (non-blocking) a follow-up parametrize case if this module is touched again.
- **NB-2:** I could not independently verify D-059-R011's specific line-number citations into `pluto_soda.py:201-202`/`:784-791` (forbidden_paths for this task) or run the full `services/api/tests`/`modularity_check.py` commands (outside my authorized command list for this review) — these fall to the `directive-compliance-verifier` and code-reviewer/G3 respectively, not a gap in test-adequacy coverage.

## Required rework

None.

## Reviewer conclusion

Test adequacy for M5-T027 is independently verified, not merely trusted from the producer's claims. I derived the zero-handling decision table directly from the fixed module and confirmed every branch (including the 4 distinct fail-closed sub-cases: positive numbldgs, absent numbldgs, unusable-coverage numbldgs, non-numeric numbldgs) has an explicit test, with the pre-existing computed/over-built/missing/unusable/no-cap paths all remaining covered and passing (431/431, 28/28). I physically reproduced red-on-old by swapping the pre-fix module into the fixed tree and re-running — all 5 new fail-closed tests failed exactly as claimed, and I additionally red-on-old-confirmed the R6-R12 label-derivation test the same way. I diffed the corrected miscast vacancy test against its parent and found it now genuinely establishes vacancy (not just a rename) with zero assertions weakened or removed anywhere in either edited test file. The R003 label tests assert hand-written literal strings against both a low-density and a real higher-density (R6-R12, cross-checked against the actual ruleset file) district, so they are non-tautological and defect-catching. Tests are offline, free of shared mutable state, and my independently-executed counts (431 scenario, 28 contract, +5/+2 deltas reconciling to +7) match the producer's claims exactly.

**Verdict: PASS.**
