# M5-T027 producer report — D-059 step-1 dependable-answers fixes

Task: `M5-T027`. Contract head: `7150edef`. Directive refs: `D-059:D-059-R001,D-059-R002,
D-059-R003,D-059-R011` (+ `D-046:D-046-R001,D-046-R002` concurrency). Producer:
`backend-engineer` (unnamed worktree spawn, `wt-m5t027`).

Commit: one commit, message prefixed `M5-T027 producer: ` (a commit cannot embed its own
final sha, since the sha is a hash of the commit's content including this file — the
exact sha is reported verbatim in the producer's RETURN to the orchestrator, and is
whatever `git log -1 --format=%H` shows at the tip of worktree `wt-m5t027` after this
report was written).

## Files changed (git diff --stat)

```
services/api/app/scenario/builder.py               |  41 +++--
services/api/app/scenario/constants.py             | 169 +++++++++++++++++----
services/api/app/scenario/unused_floor_area.py     | 154 ++++++++++++++++++-
services/api/tests/scenario/test_scenario_foundation.py | 106 +++++++++++++
services/api/tests/scenario/test_unused_floor_area.py   | 141 +++++++++++++++--
5 files changed, 554 insertions(+), 57 deletions(-)
```

Exactly the 5 code/test files inside `allowed_paths` were touched (plus this report, the
6th). `test_scenario_contract.py` was read but needed no edit (no hardcoded R5/23-21/
coverage-matrix text lives there). No file outside `allowed_paths` was edited; no
`packages/**`, `connectors/**`, `rules/**`, `apps/web/**` touch.

## Per-scenario status (S1–S5)

- **S1 `zero_with_buildings_fail_closed` — PASS.** Reproduced verbatim (one building,
  `bldgarea` 0, `numbldgs` 1, positive cap) in
  `test_s1_zero_with_positive_numbldgs_fails_closed_red_on_old`
  (`test_unused_floor_area.py`): `state=not_computable`, value `null`,
  `not_computable_reason=existing_building_area_unusable`, section
  `professional_review_required=True` (and document root `True` via the existing
  OR-semantics in `builder.py::_assemble`), original zero + numbldgs=1 basis visible in
  `section["assumptions"]`. **RED confirmed against the pre-fix code**: I swapped the
  working tree's `unused_floor_area.py` for the `HEAD` (pre-fix, `7150edef`) copy via
  `git show HEAD:services/api/app/scenario/unused_floor_area.py` and re-ran the 5 new
  fail-closed tests — all 5 failed (`computed`/`15000.0` instead of `not_computable`/
  `null`), confirming the old code did exactly what the reviewer reported (`5 failed, 1
  passed` — the 1 pass was the established-vacancy case, correctly unaffected). Restored
  the fixed file (byte-identical to the pre-swap working tree, confirmed via
  `git diff --stat`) before committing.
- **S2 `vacancy_established_vs_unknown_zero` — PASS.**
  `test_s1_established_vacancy_zero_existing_area_is_usable_and_computed` (renamed/
  corrected from the miscast `test_s1_vacant_lot_zero_existing_area_is_usable_and_computed`,
  which previously supplied `bldgarea=0` with NO `numbldgs` fact at all and asserted
  `computed` — exactly the miscast case the directive named) now supplies
  `numbldgs={"value": 0.0, "coverage_status": "conditional"}` and asserts `computed`/full
  cap. `test_s1_zero_with_absent_numbldgs_fails_closed`,
  `test_s1_zero_with_unusable_numbldgs_coverage_fails_closed[data_conflict|unsupported]`,
  and `test_s1_zero_with_nonnumeric_numbldgs_fails_closed` cover absent/unusable-coverage/
  non-numeric `numbldgs` — all fail closed to `existing_building_area_unusable`.
- **S3 `recorded_data_comparison_wording` — PASS.** `UNUSED_FLOOR_AREA_LABEL` and
  `UNUSED_FLOOR_AREA_SCOPE_NOTE` (`constants.py`) rewritten: no longer call the result
  "a zoning floor-area difference"; state PLUTO `bldgarea` is a recorded-data comparison
  (gross, condo semantics differ), not a confirmed ZR 12-10 zoning-floor-area figure;
  name the rights-calculation preconditions (compatible existing zoning-floor-area input +
  confirmed zoning-lot extent). Verified with `test_s6_no_forbidden_nouns_and_no_verified_
  compliant_language` (unchanged, still passes) plus a standalone forbidden-word scan (see
  Self-checks) confirming no "verified"/"compliant"/forbidden-noun leakage in the new text.
- **S4 `labels_from_evaluation` — PASS.** `test_as_r003_low_density_r5_derives_coverage_
  and_section_labels` (canonical R5/23-21 fixture) and
  `test_as_r003_higher_density_r6_r12_derives_coverage_and_section_labels` (a new R6-R12/
  R9A/23-22 fixture built from the real `r6_r12_residential_far.rule.json` rule_id/
  citation/FAR values) in `test_scenario_foundation.py` assert `cap_label` and
  `reasons[0]` name the section the rule ACTUALLY cited (23-21 vs 23-22, never both) and
  the `coverage_matrix` `residential_far_cap` row's `governs` text names the ACTUAL
  evaluated family ("(R5)" vs "(R6-R12)"), never a hardcoded one. The universal
  "non-R5" phrasing is gone from `higher_density_bulk_tower`'s `governs` text
  (`constants.py`); the higher-density test also asserts no row's `governs` text contains
  "non-r5" (case-insensitive).
- **S5 `scope_schema_and_regression` — PASS**, see Self-checks below. `git diff` scope
  confirmed above; `services/api/tests/scenario` and the rest of `services/api/tests`
  green (one pre-existing, unrelated failure documented below); ruff clean; modularity
  0 failures; `packages/contracts/schemas/v1/scenario.schema.json` untouched (byte-
  identical, `test_s6_both_schema_copies_are_byte_identical` passes); zero new
  dependencies (no `requirements*`/`pyproject.toml` touch — both are in `forbidden_paths`
  and I did not need them).

## Per-requirement evidence

- **D-059-R001** (recorded-data semantics): `services/api/app/scenario/constants.py`
  `UNUSED_FLOOR_AREA_LABEL` / `UNUSED_FLOOR_AREA_SCOPE_NOTE` rewritten to present the
  `bldgarea`-minus-cap subtraction as "a RECORDED-DATA COMPARISON, not a ZR 12-10 zoning
  floor-area difference"; states PLUTO `bldgarea` is "not a confirmed existing ZR 12-10
  zoning floor area figure" and that "a development-rights determination would
  additionally require a compatible, supported existing zoning-floor-area input and a
  confirmed zoning-lot extent." Tests: `test_unused_floor_area.py` (existing S6
  forbidden-language test unchanged and still green; `test_s1_computed_normal_remainder`
  etc. assert the new label verbatim via `section["label"] == UNUSED_FLOOR_AREA_LABEL`).
  Web presentation surface is explicitly out of scope for this task (`apps/web/**` is
  `forbidden_paths`) — see Limitations.
- **D-059-R002** (bldgarea-zero fail-closed): `services/api/app/scenario/
  unused_floor_area.py` adds `_numbldgs_fact` / `_vacancy_basis` /
  `_zero_with_buildings_assumptions` and a new branch (b2) in
  `build_unused_floor_area_section`: a `bldgarea` fact value of exactly `0.0` is consumed
  as a usable zero ONLY when the SAME profile's `numbldgs` fact establishes vacancy
  (present, usable `coverage_status`, value exactly `0`); otherwise it routes to the
  EXISTING typed reason `existing_building_area_unusable` (no new enum value — verified
  `services/api/app/scenario/models.py` was not touched, not in `allowed_paths`), with
  `professional_review_required=True` at the section level and the original zero +
  numbldgs basis carried as two `assumptions` records. Tests: the 5 new/corrected tests in
  `test_unused_floor_area.py` listed under S1/S2 above, proven RED against the pre-fix
  code (see S1 evidence).
- **D-059-R003** (labels from actual evaluation): `constants.py` — `COVERAGE_MATRIX`'s
  `residential_far_cap` row `governs` text no longer hardcodes `"(R5)"` (now
  family-agnostic by default); `coverage_matrix_rows(cap_rule_id)` derives the
  `"(R5)"` / `"(R6-R12)"` / etc. suffix from the ACTUAL evaluated rule's `rule_id` via
  `_residential_far_family_label` (a pure string transform of the
  `<stem>-residential-far` naming convention used by every `residential_far`
  ruleset file — verified against all four: `r5-residential-far`,
  `r6-r12-residential-far`, `r1-r2-r3-residential-far`, `r2x-r4-residential-far`, see
  Self-checks). `higher_density_bulk_tower`'s `"(non-R5)"` phrasing removed. New
  `draft_cap_label(section_reference)` and `preliminary_cap_reason(section_reference)`
  functions build the cap label / `reasons[0]` text from the rule's OWN cited section
  (`cap_provenance["citations"][0]["section"]`, read via the new
  `builder.py::_cap_citation_section`), never a hardcoded `"ZR 23-21"`. `builder.py`'s
  `_assemble` and the preliminary branch of `build_scenario` now call these derived
  forms instead of the old `C.DRAFT_CAP_LABEL` / hardcoded reasons string. Tests: the two
  new `test_as_r003_*` tests in `test_scenario_foundation.py` (low-density R5 + higher-
  density R6-R12), asserting the derivation both ways (23-21 vs 23-22, "(R5)" vs
  "(R6-R12)", and that neither section number/family name leaks into the other outcome).
- **D-059-R011** (external fact — PLUTO zero-with-buildings rule): re-verified the
  connector's own source note at `services/api/app/connectors/pluto_soda.py:201-202`
  ("BldgArea: condo values are net not gross, and NOT ZR 12-10 zoning floor area -
  informational fact") and the sibling documented pattern for `numfloors`
  (`pluto_soda.py:784-791`, "NumFloors null with NumBldgs > 0 = 'not available'", citing
  the 26v1 data dictionary p.28) as the connector-side precedent this fix mirrors for
  `bldgarea`. The connector itself is `forbidden_paths` (out of scope for this task); the
  dictionary rule is applied at the scenario layer (`unused_floor_area.py`) per the task's
  explicit scoping. No conflicting evidence found; source citation is unchanged from the
  directive capture (`source-001.md#review-document-verbatim`, PLUTO dictionary 22v1 at
  nyc.gov vs the repo connector's 26v1 source notes — same distinction, re-verified).

## Self-checks (documented commands, run from the worktree root unless noted)

1. `python -m pytest services/api/tests/scenario -q`
   → `431 passed in 1.74s` (re-run after restoring the fixed file post RED-verification
   swap; see S1 evidence for the intermediate RED run).
2. `python -m pytest services/api/tests -q --ignore=tests/documents` (run from
   `services/api`)
   → `1 failed, 2435 passed in 39.65s`. The 1 failure
   (`tests/contracts/test_contract_serializers.py::
   test_serializer_imported_exactly_at_the_profile_write_boundary`) and the 15
   `tests/documents/*` collection errors (excluded above) are **pre-existing and
   unrelated**: they all trace to `services/api/app/documents/units.py:276`'s PEP 695
   generic-function syntax (`def _match_unit[UnitT: enum.Enum](`), which requires Python
   3.12; the sandbox runs Python 3.11.9 (`python --version` confirmed) and no 3.12
   interpreter is available (`py -0` lists only 3.11/3.13, no 3.12). Confirmed
   pre-existing and untouched by this task: `git status --porcelain=v1
   services/api/app/documents/units.py` is empty (no local changes) and this task's
   `allowed_paths`/`forbidden_paths` never reference `app/documents/**`. This matches a
   previously-documented project finding (Python 3.11 sandbox vs. repo's required 3.12
   for PEP 695 syntax; CI runs 3.12 and is unaffected). `python -m pytest services/api/
   tests -q` (full, unfiltered) reproduces the same 15 collection errors plus the 1
   failure, all in `tests/documents`/`tests/contracts` — zero failures anywhere touching
   `app/scenario/**` or `tests/scenario/**`.
3. `cd services/api && python -m ruff check .` → `All checks passed!` (then `cd` back to
   the worktree root before step 4, per the cwd-persistence note).
4. `python tools/modularity_check.py --check` → `selected 405 files; failures 0; warnings
   17`. All 17 warnings are pre-existing, on files this task never touched (`apps/web/src/
   lib/surveyReview/types.ts`, `api/v1/scenario_analysis.py`, `connectors/
   dcm_street_centerline_arcgis.py`, `connectors/mappluto_geometry_arcgis.py`,
   `scenario/breakeven.py`, six `tools/agent_supervisor/*.py` files,
   `tools/context_benchmark.py`) — 0 failures, 0 new warnings from this change's 3 touched
   `app/scenario/*` files.
5. Standalone forbidden-language scan (documents S3/R001 compliance beyond the existing
   pytest assertion): ran a short Python snippet importing `app.scenario.constants` and
   checking `UNUSED_FLOOR_AREA_LABEL`, `UNUSED_FLOOR_AREA_SCOPE_NOTE`,
   `UNUSED_FLOOR_AREA_OVER_BUILT_STATEMENT`, `UNUSED_FLOOR_AREA_FORMULA`, and
   `zoning_lot_extent_assumption()`'s `rationale`/`value` against `"maximum buildable
   area"`, `"remaining development rights"`, `"remaining capacity"`, `"verified"`,
   `"compliant"` (case-insensitive substrings) → `OK C1-scoped clean` (all 6 strings
   pass). Also printed `coverage_matrix_rows(rule_id)` for all four residential_far
   `rule_id`s to confirm the family-label derivation: `r5-residential-far` → `"(R5)"`,
   `r6-r12-residential-far` → `"(R6-R12)"`, `r1-r2-r3-residential-far` →
   `"(R1-R2-R3)"`, `r2x-r4-residential-far` → `"(R2X-R4)"`.

## Assumptions / design decisions

- **`DRAFT_CAP_LABEL` retained as a module constant** (byte-identical to
  `draft_cap_label("23-21")`) solely because `services/api/app/scenario/derive.py` (its
  malformed-input fallback), `services/api/app/scenario/__init__.py` (re-export), and
  `services/api/tests/scenario/test_scenario_derive.py` (two exact-equality fixture
  assertions) import/consume it directly and are **not** in this task's `allowed_paths`.
  The LIVE builder path (`builder.py`'s `_assemble` and the preliminary branch) no longer
  reads this constant for any real request — it always calls `C.draft_cap_label(
  cap_section)` with the actual per-request citation. The constant happens to stay
  correct for every one of those three out-of-scope consumers because their shared
  fixture (`_support.canonical_rule_evaluation()`, the R5/23-21 fixture) is the same one
  `DRAFT_CAP_LABEL` was computed from — verified no divergence is possible by inspection
  (`grep -rn DRAFT_CAP_LABEL` over `services/api`, reported in this report's evidence
  section for R003).
- **`assumptions` (not a new `inputs` field) carries the zero-with-buildings basis.**
  `packages/contracts/schemas/v1/scenario.schema.json`'s `unused_floor_area_inputs` is
  `additionalProperties: false` with exactly two fixed sub-objects (no room for a
  `numbldgs` field) and `packages/**` is `forbidden_paths` (zero schema changes, per the
  task's explicit constraint). `assumptions` is the existing, schema-open, generic
  machine-readable-basis channel (`items: {$ref: "#/$defs/assumption"}`, an open
  `assumption_type` label, no schema-enforced state-based cardinality) already used for
  the `zoning_lot_extent` assumption — I added two records of a new `assumption_type`
  (`"not_computable_basis"`) here rather than inventing a schema-incompatible field.
  `inputs.existing_building_floor_area.value_sq_ft` stays `null` on this path, consistent
  with every other `existing_building_area_unusable` outcome (never a new precedent for
  that specific field).
- **`professional_review_required=True`** on the new zero-with-buildings branch (unlike
  the pre-existing generic-unusable branch, which stays `False`) — taken directly from
  the task prompt's literal wording ("section `professional_review_required` true") and
  S1's acceptance text ("section professional_review flag set"); this also escalates the
  document root flag via the existing OR-semantics in `_assemble` (unchanged code).

## Limitations (disclosed)

- **Web presentation (R001's third surface) is out of scope for this task.**
  `apps/web/**` is `forbidden_paths` and the task explicitly said "no e2e edits." The
  scenario-document fields (`cap_label`, `unused_draft_zoning_floor_area.label`/
  `.scope_note`) now carry the corrected wording verbatim, so any web surface that
  displays those fields verbatim inherits the fix automatically; a web surface that
  independently hardcodes similar language (not verified in this task) would need its own
  follow-up.
- **`packages/contracts/schemas/v1/scenario.schema.json`'s own description text** (e.g.
  `"cap_label"`'s description and the top-level document description) still says "ZR
  23-21" / "R5 residential-FAR family" — this is prose in a `forbidden_paths` file and
  was already flagged as an out-of-scope candidate follow-up in the task's own
  `path_notes` ("Contract-schema prose in scenario.schema.json also carries the old
  zoning-floor-area framing - OUT of scope here (contracts forbidden)"). Not touched.
- **`_residential_far_family_label`'s naming-convention derivation** (`<stem>-
  residential-far` → uppercase stem) is a generic string transform verified against all
  four rulesets that exist today (`r5`, `r6-r12`, `r1-r2-r3`, `r2x-r4`); it fails closed
  (returns `None`, family-agnostic fallback text) for any `rule_id` that does not match
  the convention, so a future non-conforming rule_id would not mislabel — it would just
  omit the family suffix, never guess a wrong one.
- The Python-3.11-vs-3.12 sandbox gap (self-check 2) is a pre-existing environment
  condition unrelated to this task's scope; documented for transparency, not something I
  attempted to fix (out of `allowed_paths`, and CI runs the correct Python version per
  prior project findings).

## Requested status

`awaiting_gate`.
