# M4-T006 — Producer report (rules-engineer)

**Task:** Encode the R5-series height & setback regulations as a DRAFT
(`needs_review`) rule family in the existing rules engine/DSL.
**Producer:** rules-engineer. **Status requested:** awaiting_gate (G0/G2/G3/G4/G5;
G6 qualified-human legal approval remains REQUIRED and is NOT part of this build).
**Frozen-SHA candidate:** `edddbbf` (see "Commits" below).

Producer-only: I did NOT run `tools/project_control.py`, `gh`, git
merge/PR/push, and did not record any gate or self-accept. Work is committed on
the assigned worktree branch.

---

## 1. What shipped (allowed paths only)

### New ZR source snapshots (byte-stable, hash-guarded, packaged)
Canonical `docs/research/zr-snapshots/v1/` + byte-identical bundle
`services/api/app/_zr_snapshots/v1/` (synced via the existing
`scripts/sync_zr_snapshots.py`; no pyproject change — the new files fall under
the already-declared package-data globs):
- `zr-12-10.snapshot.json` — §12-10 wide (≥75 ft) / narrow (<75 ft) street defs
- `zr-23-421.snapshot.json` — §23-421 pitched-roof envelope (R5A: wall 25 / ridge 35 above base plane)
- `zr-23-422.snapshot.json` — §23-422 flat-roof envelope (R5: base 35 / bldg 45; R5B: bldg 35; R5D: bldg 45)
- `zr-23-423.snapshot.json` — §23-423 setback depth (≥10 wide / ≥15 narrow street)
- `zr-23-424.snapshot.json` — §23-424 qualifying-residential-site alternative (base 45 / bldg 55)

Each carries: snapshot_id, section, VERBATIM excerpt (the exact quotes from the
source findings), request URL (zr.planning.nyc.gov), access_date `2026-07-22`,
`section_last_amended 2024-12-05` (City of Yes for Housing Opportunity),
`content_digest_sha256 = sha256(verbatim_excerpt)` (recomputed and verified on
load), `raw_html_verified: false`, `extraction_status: extracted_draft`.

### New rule DSL files (`services/api/app/rules/rulesets/`) — family `residential_height_setback`
Per-district, SEPARATE files, SEPARATE typed constraints, `status: needs_review`,
`effective_from: 2024-12-05`, verified-ineligible:
- `r5_height.rule.json` — R5 flat: `max_base_height` 35, `max_building_height` 45 (street-width independent; no minimum base height stated → documented limitation)
- `r5_setback.rule.json` — R5 §23-423 setback: `required_setback_depth` (10 wide / 15 narrow); `street_width_class` REQUIRED → fail-closed
- `r5a_height.rule.json` — R5A pitched: `max_perimeter_wall_height` 25, `max_building_height` 35 (above base plane); `building_type` REQUIRED → fail-closed; pitched setback = documented limitation
- `r5b_height.rule.json` — R5B flat: `max_building_height` 35 only (no base/setback split)
- `r5d_height.rule.json` — R5D flat: `max_building_height` 45 only (NO setback; encoded SEPARATELY from R5)
- `r5_qrs_height.rule.json` — §23-424 alternative (all 4 variants): `max_base_height` 45, `max_building_height` 55; `qualifying_residential_site` REQUIRED → fail-closed; competes with base-district rules → rule_conflict

No DSL schema change was needed — the existing constructs (per-district rules,
`param_select` maps, required-input fail-closed, `exceptions` with
`professional_review_required`, `uncertainty_policy`, `effective_from`, and the
registry's same-family `detect_conflicts`) express the whole family. The evaluator
core, the property-analysis integration, `r5_residential_far.rule.json`, and every
canonical contract are UNCHANGED.

### Tests + matrix
- `services/api/tests/rules/test_r5_height_setback.py` — 45 tests (AS-1..AS-6 + NC-1..NC-7)
- `project-control/reports/M4-T006-input-readiness-matrix.md` — every condition → exact canonical field path + readiness + fail-closed outcome

---

## 2. Self-checks — exact commands + actual outputs

All from `services/api` (thin-client: Python only; no AI in evaluation).

```
$ python -m ruff check .
All checks passed!

$ python scripts/sync_zr_snapshots.py --check
OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (6 file(s)).

$ python -m pytest tests/rules/test_r5_height_setback.py -q
45 passed in 1.11s

$ python -m pytest tests/rules/test_zr_snapshot_bundle.py tests/rules/test_installed_deployability.py -q
8 passed in 0.28s

$ python -m pytest -q          # full services/api suite
926 passed in 35.92s
```

### Installed-wheel deployability — command + environment limitation (disclosed)
The literal `pip install --no-deps .` could NOT be executed in this environment:

```
$ python -m pip install --no-deps --no-build-isolation --target <tmp> .
ERROR: Package 'nyc-buildability-api' requires a different Python: 3.11.9 not in '>=3.12'

$ py -3.13 -m pip install --no-deps --no-build-isolation --target <tmp> .
Unable to create process using '...Python313\python.exe --version': The system cannot find the file specified.
```

The only local interpreter that runs is Python 3.11.9, which is BELOW the
project's `requires-python >=3.12`; the 3.13 launcher is broken (missing exe).
This is an environment limitation, not a packaging gap. Deployability is instead
proven by the guard tests that exercise the EXACT wheel resolution mechanism
(`importlib.resources`) and the package-data declarations, all green above:
- `test_installed_deployability.py` — asserts pyproject declares
  `app._zr_snapshots.v1 = ["*.snapshot.json"]` and `app.rules = ["rulesets/*.rule.json", ...]`
  AND that each glob matches shipped files (my 5 new snapshots + 6 new rules are under those globs).
- `test_zr_snapshot_bundle.py` — loads snapshots through `importlib.resources`
  (the site-packages path a wheel uses) and asserts the default `SnapshotStore()`
  resolves to the PACKAGED `app/_zr_snapshots/v1` dir with all 6 snapshots.
- `test_r5_height_setback.py::test_as6_family_loads_from_default_packaged_registry`
  — a default `RuleRegistry()` (packaged snapshots + packaged rulesets) loads all
  6 family rules and evaluates `r5-height`.

Recommendation for the gate: re-run `pip install --no-deps ./services/api` on the
CI 3.12 image (the `api` job) to capture the byte-for-byte install log; the
mechanism it would exercise is already covered green here.

---

## 3. Acceptance scenarios + negative controls → proving test (file:line)

File: `services/api/tests/rules/test_r5_height_setback.py`

| Scenario | Proving test(s) | Line |
|---|---|---|
| AS-1 per-variant confident, min/max preserved, separate constraints | `test_as1_r5_height_confident_base_and_building_separate` | 68 |
| AS-1 (setback min depth by street) | `test_as1_r5_setback_confident_min_depth_by_street` (wide/narrow) | 83 |
| AS-1 (R5A wall+ridge separate) | `test_as1_r5a_pitched_confident_wall_and_ridge_separate` | 91 |
| AS-1 (R5B / R5D) | `test_as1_r5b_confident_building_height_only`, `test_as1_r5d_confident_building_height_no_setback` | 99, 105 |
| AS-1 (conditional never verified) | `test_as1_conditional_never_verified_for_every_variant` | 113 |
| AS-2 provenance fidelity | `test_as2_every_emitted_dimension_traces_to_snapshot_provenance`, `test_as2_setback_carries_all_three_citations` | 131, 144 |
| AS-2 tampered / absent snapshot fails closed | `test_as2_tampered_snapshot_fails_closed`, `test_as2_absent_snapshot_fails_closed` | 152, 167 |
| AS-3 effective-date boundary | `test_as3_before_amendment_not_effective`, `test_as3_on_amendment_date_effective` | 189, 205 |
| AS-4 determinism byte-identical | `test_as4_determinism_byte_identical` | 216 |
| AS-5 never-Verified / draft lifecycle | `test_as5_every_family_rule_is_needs_review_and_verified_ineligible`, `test_as5_family_coverage_is_conditional_never_verified` | 227, 236 |
| AS-6 installed-wheel deployability | `test_as6_family_loads_from_default_packaged_registry`, `test_as6_every_family_rule_file_validates_via_dsl_loader` | 246, 258 |
| NC-1 district-variant non-inheritance | `test_nc1_variant_value_not_applied_to_another`, `test_nc1_unknown_r5_variant_is_unsupported_not_nearest` | 280, 289 |
| NC-2 wide/narrow/UNKNOWN street | `test_nc2_missing_street_width_fails_closed`, `test_nc2_invalid_street_class_fails_closed` | 303, 310 |
| NC-3 special-district / overlay | `test_nc3_overlay_or_special_district_downgrades_never_silent_base`, `test_nc3_historic_district_downgrades` | 326, 333 |
| NC-4 building/ground-floor unavailable | `test_nc4_building_type_unavailable_fails_closed`, `test_nc4_qualifying_site_geography_unavailable_fails_closed` | 342, 349 |
| NC-5 missing input | `test_nc5_missing_district_fails_closed` | 361 |
| NC-6 contradictory input | `test_nc6_conflicting_district_signals_data_conflict`, `test_nc6_uncertain_geometry_professional_review` | 372, 386 |
| NC-7 mutually-exclusive rules → rule_conflict, no value | `test_nc7_base_and_qrs_rules_conflict_no_value`, `test_nc7_conflict_is_order_independent`, `test_nc7_no_conflict_for_ordinary_r5` | 403, 414, 422 |

---

## 4. Guardrail confirmations

- **Per-district, no family-wide default:** each of R5/R5A/R5B/R5D is its own rule
  file with `in_set` applicability on the exact district string; no `R5*` default;
  no shared dimensions. NC-1 proves a value for one variant is never applied to
  another and an unknown variant is `not_applicable` (never nearest-mapped).
- **Separate typed constraints w/ min & max:** base height, building height,
  perimeter-wall height, and setback are separate named outputs (not one collapsed
  number, never labeled envelope/feasible/massing). MAX caps are encoded; where the
  source states NO minimum (R5 base height) it is a documented limitation, never a
  fabricated zero.
- **Fail-closed inputs:** street width (no canonical field) → `r5-setback` PRR, no
  value; building type (no canonical field) → `r5a-height` PRR (also the
  flat-vs-pitched selection failing closed); qualifying-residential-site geography →
  `r5-qrs-height` PRR; special-district/overlay present → PRR with recorded
  exception (the base value is surfaced only with a PRR flag, never as a silent
  final value).
- **rule_conflict:** reuses the registry's existing `detect_conflicts` /
  `detect_rule_conflicts` shape; the §23-424 alternative competes with the
  base-district height rules for `max_base_height`/`max_building_height` →
  deterministic, order-independent conflict with NO selected value (NC-7).
- **Never Verified:** every rule `needs_review`, `verified_eligible=false`,
  coverage tops out at `conditional`; `effective_from 2024-12-05`.
- **No forbidden edits:** evaluator core, property-analysis integration,
  `r5_residential_far.rule.json`, canonical contracts, `apps/web`, 3D/UI, and
  yards/lot-coverage/parking are all untouched (full suite green confirms no
  regression: 926 passed).
- **Legacy numbering avoided:** encoded the City-of-Yes §23-42 series
  (§23-421/422/423/424), NOT the stale §23-66x Quality-Housing numbering.

---

## 5. Deviations from the source findings / assumptions (disclosed)

1. **No snapshot for §23-42 / §23-426 / §23-44 / §23-425.** The findings supply a
   verbatim quote only for §23-421/422/423/424 and §12-10. §23-42 (series parent)
   and the override sections (§23-426 historic, §23-44 overlay/special, §23-425
   large-site) were given as descriptions, not verbatim text, so no snapshot was
   fabricated for them. The override contexts are implemented as
   `professional_review_required` exceptions with `citation_ref: null`, naming the
   section in the exception description and recording it as a limitation. A
   follow-up capture of verbatim §23-426/§23-44/§23-425 text would let these
   exceptions carry snapshot provenance.
2. **§23-423 depth & §12-10 defs captured as researcher reading, not byte-verified
   verbatim.** The 10/15-ft depths and the 75-ft threshold are the
   official-source-researcher capture; snapshots carry `raw_html_verified: false` /
   `extraction_status: extracted_draft` and an explicit needs_review note — mirroring
   the existing `zr-23-21` snapshot discipline. Byte-level raw-HTML verbatim
   confirmation is a G6/verification item, not weakened.
3. **§23-422 district-to-statement association.** The three "In the district
   indicated…" statements are associated with R5 / R5B / R5D by the researcher's
   reading; the snapshot's `table.table_note` records this as a needs_review item
   pending raw-HTML row confirmation.
4. **Override-context values are surfaced, not suppressed.** When
   overlay/special/historic/large-site is present, the computed base value remains
   in `outputs` but coverage is downgraded to `professional_review_required` with a
   recorded exception — the evaluator's sanctioned "surface, never silently trust"
   mechanism (same pattern as the accepted FAR rule). This satisfies "never the
   silent base value": coverage is the authoritative signal and it screams PRR.
5. **`historic_district` / `large_site` have no canonical field.** They are optional
   booleans that downgrade only when a caller supplies `true`; when absent the
   override is a documented limitation (not silently cleared).

No value outside the source findings was invented; no forbidden path was crossed;
no pre-amendment (height-factor/legacy QH) value was carried forward.

---

## 6. Commits (worktree branch)

- `3f9d6aa` — capture R5 height/setback ZR section snapshots (23-421/422/423/424, 12-10)
- `efef508` — encode R5-series height/setback DRAFT rule family (6 rule files)
- `edddbbf` — AS-1..AS-6 + NC-1..NC-7 test pack (45 tests) + input-readiness matrix

**Frozen-SHA candidate: `edddbbf`.**

## 7. Blockers
None. G6 qualified-human legal approval remains REQUIRED before any
publication/verification/final acceptance and is intentionally NOT part of this
build.
