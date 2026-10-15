# M5-T182 producer report - the pure placement and area-allocation computation modules

Builder: backend-engineer. Claim head: `dc3a2276653ee17542ba626bcd925a065963f62b`
(`task/wave26-envelope-constraints`). Two pure, self-contained scenario-layer modules plus their unit
tests; no wiring, no document change, no benchmark, no records (M5-T172b wires them later).

## What changed

- `services/api/app/scenario/three_answers/placement.py` (was a one-line placeholder): `build_placement(...)`
  returns a contract-1.5.0 `$defs.building_placement` dict. From the stated facts it computes the plate
  (zoning floor area per storey), the plan depth and footprint on the printed-tax-map basis, the footprint
  outline polygon (every vertex derived), the tax-map back clearance and the city-map (GIS) conflict
  figures, and the method / basis / measure const / conversion-statement const / checks / conditions /
  not_checked. A placed placement carries the outline; the unplaced state returns a withheld placement with
  NO outline. Public: `build_placement`, `compute_placement_geometry`, `plate_area_sqft`,
  `PlacementGeometry`, and the consts `ILLUSTRATIVE_LABEL`, `AREA_MEASURE`, `PLATE_CONVERSION_STATEMENT`,
  `PRINTED_TAX_MAP_BASIS`, `GIS_BASIS`, `RECONCILE_TOLERANCE_SQFT`.
- `services/api/app/scenario/three_answers/area_allocation.py` (was a placeholder): `build_area_allocation(...)`
  returns a contract-1.5.0 `$defs.area_allocation` dict - one stated share (0.60) applied to the residential
  floor area, split into apartment / other totals, carrying the label / measure / conversion consts;
  `fitted` follows the placement status. `per_storey_area(...)` gives the per-storey figures. Returns None
  when the floor area is missing. Public also: `STATED_APARTMENT_SHARE`, `SHARE_MIN`, `SHARE_MAX`.
- `services/api/tests/scenario/three_answers/test_placement.py` (new): 27 tests.
- `services/api/tests/scenario/three_answers/test_area_allocation.py` (new): 27 tests.
- `project-control/reports/M5-T182-producer-report.md` (this report).

Both modules import ONLY `dataclasses` / `decimal`; they import NOTHING from `three_way_document.py`,
`geometry.py`, `first_option_results.py`, `envelope_constraints.py` or any result/drawing/route module
(RISK A1 / G3 import-set check met). `three_answers/__init__.py` is untouched; tests import the modules
directly. The footprint outline is built as plain schema dicts (`$defs.polygon`: closed ring, 5 points).

## Source of every number (no program run)

All expected values come ONLY from the settled worked example
`docs/reference-cases/R6B/cases/placement-building-b.json` (step P8, M5-T177 accepted) and its rendered
`placement-building-b.md`, re-derived by the arithmetic below; never from a program run. Agreement of two
AI readings is not proof. The modules revise no evidence record (NB-03/NB-04/NB-06 read-only, unchanged).

- plate = 20,150 / 3 = **6,716.67** (row `plate`).
- plan depth = 20,150/3 / 100.76 = **66.66**; footprint = 66.66 x 100.76 = **6,716.66**; reconciles to the
  plate within the readers' +/-0.5 (0.01 apart), never forced into one figure (row `footprint-tax-map`).
- tax-map back clearance = 100 - 66.66 = **33.34** (row `placement-tax-map`); the three street/side touches
  are 0 ft.
- GIS conflict (check only): gis plan depth = 20,150/3 / 103.88 = **64.66**; gis back clearance = 99.97 -
  64.66 = **35.31** (NOT the stale 33.32; RISK A4 confirmed against row `gis-conflict-check`); frontage
  conflict = 103.88 - 100.76 = **3.12**. Carried as a `contradicted_record` condition naming both bases,
  resolved by neither.
- area allocation at 0.60: apartment 20,150 x 0.60 = **12,090.00** total / **4,030.00** per storey; other
  20,150 - 12,090 = **8,060.00** total / **2,686.67** per storey; total **20,150.00**; apartment + other =
  total; per-storey figures sum to the plate (4,030.00 + 2,686.67 = 6,716.67) (row `area-allocation`).

Rounding is round-half-up to two decimals via `Decimal` (the reading's `round_half_up_2dp`).

## Input-state table (one test per input state)

### placement.py

| input | state | outcome | test that pins it |
|---|---|---|---|
| zfa + storeys + frontage + lot_depth present, `placed=True` | all present | placed dict; plate 6,716.67; depth 66.66; footprint 6,716.66 | `test_s1_*`, `test_s2_placed_carries_outline_and_the_fixed_fields` |
| outline vertices | present | closed rectangle, each vertex from frontage/depth/touches; area 6,716.66 reconciles to plate | `test_s2_outline_vertices_are_derived_from_frontage_and_depth`, `test_s2_outline_area_reconciles_with_the_plate` |
| placed dict | present | conforms to `$defs.building_placement` | `test_s2_placed_validates_against_the_contract` |
| `placed=False` | unplaced | withheld, NO outline, carries method/basis/measure/conversion | `test_s3_withheld_has_no_outline_and_validates` |
| withheld + injected outline key | invalid | schema rejects it (withheld branch forbids `outline`) | `test_s3_withheld_with_an_outline_is_rejected_by_the_schema` |
| gis frontage + gis depth present | present | 64.66 / 35.31 / 3.12 derived; conflict condition names 33.34 and 35.31 and 3.12 | `test_s6_offsets_derived_on_each_basis`, `test_s6_conflict_condition_names_both_bases_and_resolves_neither` |
| gis inputs absent | absent | no conflict invented (gis fields None) | `test_s6_without_gis_inputs_no_conflict_is_invented` |
| any apartment-plan key (unit_count/rooms/walls/core/stair/elevator...) | injected | schema rejects it | `test_s7_an_apartment_plan_key_is_rejected` (7 params) |
| consts | fixed | equal the schema consts byte-for-byte | `test_s7_consts_match_the_schema_byte_for_byte` |
| both dicts | fixed | carry conversion const; physical floor plate in not_checked | `test_s8_physical_floor_plate_is_listed_not_checked` |
| zfa / storeys / frontage / lot_depth = None, `placed=True` | a fact missing | held back -> withheld, no outline | `test_a_missing_fact_withholds_the_placement` (4 params) |
| `plate_area_sqft(None, 3)` / `(zfa, None)` | a fact missing | None | `test_plate_is_none_when_a_fact_is_missing` |
| frontage = 0.0 | a real zero (not missing) | ValueError, fails closed (no truthiness test treats 0 as missing) | `test_a_real_zero_frontage_is_a_value_not_a_missing_fact` |

### area_allocation.py

| input | state | outcome | test that pins it |
|---|---|---|---|
| residential floor area present, default share | present | share 0.60; apartment 12,090.00; other 8,060.00; total 20,150.00 | `test_s4_split_totals`, `test_s4_the_default_share_is_the_stated_low_end` |
| the totals | present | apartment + other = total | `test_s4_apartment_plus_other_equals_total` |
| per-storey | present | 4,030.00 / 2,686.67; sum to plate 6,716.67 | `test_s4_per_storey_figures_sum_to_the_plate` |
| other-area 8,060 vs coverage bound 8,060 | two bases | equal numerals, different quantity/basis; never summed/equated/carried as one; no coverage key or symbol | `test_s5_two_8060_figures_are_equal_numerals_on_different_bases`, `test_s5_the_allocation_never_carries_a_coverage_figure`, `test_s5_the_module_computes_no_coverage` |
| placement_status placed / withheld / None / other | each | fitted True only for "placed" (equality, not truthiness) | `test_fitted_follows_the_placement_status` (4 params) |
| placed / unplaced allocation | present | conforms to `$defs.area_allocation`; emitted placed-or-not | `test_s7_placed_allocation_validates`, `test_s7_unplaced_allocation_validates_and_is_emitted` |
| any apartment-plan key | injected | schema rejects it | `test_s7_an_apartment_plan_key_is_rejected` (7 params) |
| fitted=True forced with a withheld placement | broken combo | cross-key rule flags `allocation_fitted_without_placement` | `test_s7_fitted_true_with_a_withheld_placement_is_refused_by_the_cross_key_rule` |
| the modules' own output in a document | valid | passes `results_way_violations` | `test_s7_the_modules_own_output_passes_the_cross_key_rule` |
| consts / measure / conversion | fixed | match the schema; G-14 text carried | `test_s7_consts_match_the_schema_byte_for_byte`, `test_s8_carries_the_measure_and_conversion_statement` |
| residential floor area = None | missing | None (held back; alternative carries no allocation) | `test_a_missing_floor_area_holds_the_allocation_back` |
| `per_storey_area(None, 3)` / `(total, None)` | missing | None | `test_per_storey_is_none_when_a_fact_is_missing` |
| share 0.50 or 0.80 | outside 0.60-0.75 | ValueError, fails closed | `test_a_share_outside_the_contract_bound_fails_closed` |

### Truthiness audit (THREE RULES #1 - no truthiness test on an optional fact)

Every optional-fact guard is an explicit `is None` or a value comparison; none is a bare truthiness test:
`plate_area_sqft` (`zoning_floor_area_sqft is None or storeys is None`); `compute_placement_geometry`
(`plate is None or frontage_ft is None or lot_depth_ft is None`, then value guard `frontage_ft <= 0`, then
`gis_frontage_ft is not None and gis_depth_ft is not None`, then `gis_frontage_ft <= 0`);
`build_placement` branches on the geometry object being `None`; `build_area_allocation`
(`residential_floor_area_sqft is None`, bound check `not SHARE_MIN <= share <= SHARE_MAX`,
`fitted = placement_status == "placed"`); `per_storey_area` (`total_sqft is None or storeys is None`, value
guard `storeys <= 0`). `test_a_real_zero_frontage_is_a_value_not_a_missing_fact` pins that a real 0 is read
as a value, never as missing.

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

| # | command | exit | result |
|---|---|---|---|
| 1 | `cd services/api && ruff check .` | 0 | All checks passed! |
| 2 | `pytest -q tests/scenario/three_answers/test_placement.py` | 0 | 27 passed in 0.77s |
| 3 | `pytest -q tests/scenario/three_answers/test_area_allocation.py` | 0 | 27 passed in 0.68s |
| 4 | `.github/scripts/validate_contracts.py` | 0 | Checked 23 schema file(s); 0 failure(s). |
| 5 | `pytest -q .github/scripts/tests/test_validate_contracts.py` | 0 | 24 passed in 5.82s |
| 6 | `tools/modularity_check.py --check` | 0 | selected 807 files; failures 0; warnings 33 (none for the two new files) |
| 7 | `scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS: 10525 file(s), each owned by exactly one lane |

Lock note: the documented two-file run
(`pytest ... test_placement.py test_area_allocation.py`) wrapped in
`flock /root/project/lanes-runtime/heavy-run.lock` could not complete - the shared heavy-run lock was held
throughout by a concurrent neighbour's heavy run (M5-T170). Per the rule the lock wraps a pytest run of
MORE than one file; I therefore ran each file as a SINGLE-file run (rows 2 and 3), which the rule does not
gate on the lock. Both are green. I did NOT run the whole api suite (the independent check runs it once).

## Mutation proofs (one per decisive boundary; restored after each; full files re-run green)

1. plate boundary (S1) - `plate_area_sqft` divisor `storeys` -> `storeys + 1`:
   `test_s1_plate_is_zoning_floor_area_per_storey` FAILED `assert 5037.5 == 6716.67`. Restored.
2. GIS-basis offset boundary (S6; RISK A4) - `gis_plan_depth = plate_full / gis_frontage_ft` ->
   `/ frontage_ft` (wrong frontage): `test_s6_offsets_derived_on_each_basis` FAILED `assert 66.66 == 64.66`
   (gis back clearance collapsed to 33.31, near the stale 33.32 RISK A4 warns of). Restored.
3. area-split share boundary (S4) - `STATED_APARTMENT_SHARE = 0.60` -> `0.65`: `test_s4_split_totals`
   FAILED `assert 0.65 == 0.6` and `test_s4_the_default_share_is_the_stated_low_end` FAILED. Restored.

After all three were restored: `test_placement.py` 27 passed, `test_area_allocation.py` 27 passed, ruff
clean on both modules.

## What I could not check / limits

- The two-file run under the heavy-run lock (see the lock note) - deferred to single-file runs and to CI /
  the independent check, which runs the full suite once.
- No wiring, benchmark regeneration, document/print, register or record work - out of scope by design
  (M5-T172b, after M5-T169 + M5-T170). The modules are reachable from no reported result yet.
- Primary sources: I opened and cross-checked the settled worked example
  `placement-building-b.json` and its rendered `.md` (step P8) row by row for every figure above. I did not
  re-open the ZR snapshots line by line; the modules quote section numbers (ZR 23-322, 23-335, 23-362,
  12-10, 23-344) only as plain readings carried from the settled case, and they revise no evidence record
  (NB-03/NB-04/NB-06 are read-only here and unchanged).
- Interface churn (RISK A2): the signatures are minimal and contract-$def-driven; if M5-T172b needs a
  different shape, re-opening these files is a scope correction for the orchestrator.
