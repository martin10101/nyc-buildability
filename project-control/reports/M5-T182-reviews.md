# M5-T182 reviews (every return kept unchanged)

- One build round: builder commit 9b902d20 (backend-engineer, worktree), integrated as the cherry-pick db590413 (5 files, all inside the 5 allowed paths; LF sha256 equal to the builder's return). Placement and area-allocation computation modules only (M5-T172 part A); not wired into the results document, the register or the benchmark.
- Independent pre-integration check (ci-evidence-verifier) at 9b902d20: scope, digests, ruff, both test files (27 + 27 passed), contracts, modularity, lanes and records all green; its whole-api run could not start because the heavy-run lock was held by the owner's preview, which the orchestrator had started inside the lock by mistake (fixed: the preview restarted outside the lock). The orchestrator then ran the whole api suite at 9b902d20 under the lock: 9830 passed, 8 skipped, exit 0 (session-2026-10-15a/wholeapi-M5-T182-9b902d20.log).
- G2 orchestrator self-check at db590413: the five files equal the builder's digests; the modules import only the standard library (no engine module M5-T170 edits); lane coverage PASS; CI run 38690604095 at 86ae6cbb (the integration head) 21 of 21 jobs success.
- G1 data-contract-verifier at db590413: PASS, no required correction; every value recomputed independently from placement-building-b.json (plate 6,716.67; footprint 100.76 x 66.66 = 6,716.66; back clearance 33.34 on the printed tax map and 35.31 on the city map outline as a conflict check only; allocation 12,090 + 8,060 = 20,150 at the one stated 60 % share); the output dicts validate against results.schema.json 1.5.0; one basis each; the measure statement and the zoning-lot condition carried.
- G3 code-reviewer at db590413: PASS, no required correction; two advisories (no guard for a non-positive lot depth, as there is for the frontage; the docstring's 'exactly' for sums at sub-cent inputs).
- G4 qa-engineer at db590413: PASS, no required correction; scenarios reproduced, six mutation probes caught; one advisory identity note (forbidden paths changed in the range only by other tasks' contract commits, none by this task's commit).
- The advisories are recorded for the wiring task M5-T172 (its packet will carry them); none changes a value.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

I have everything I need. All independent recomputes match the reference case, the code, and the test pins; both output dicts validate against the bundled schema (byte-identical to the contracts copy); scope and imports are clean; 54 focused tests pass. Here is my G1 report.

---

# G1 data-contract review — M5-T182 (data-contract-verifier)

I am an AI agent, not a human or professional reviewer. Read-only; wrote no repo file, ran no git/`project_control` write. Reviewed the pinned cherry-pick `db590413` in `/root/project/w-wave20`, extracted to `/tmp/claude-0/t182-review-g1`. All expected values taken only from `docs/reference-cases/R6B/cases/placement-building-b.json`, never a program run.

## VERDICT: PASS

## Value table (value — settled row — my independent recompute — code value — holds?)

All figures below reconcile across all four columns. "Code" = actual output of `compute_placement_geometry` / `build_placement` / `build_area_allocation`; "recompute" = my own Decimal round-half-up arithmetic from the reference facts (20,150 sqft ZFA, 3 storeys, tax 100.76×100, GIS 103.88×99.97, share 0.60).

| Value | row | recompute | code | holds |
|---|---|---|---|---|
| Plate (ZFA/storey) | plate | 6716.67 | 6716.67 | yes |
| Plan depth | footprint-tax-map | 66.66 | 66.66 | yes |
| Footprint | footprint-tax-map | 6716.66 | 6716.66 | yes |
| Outline area (shoelace) | footprint-tax-map | 6716.66 | 6716.66 | yes |
| Tax back clearance | placement-tax-map | 33.34 | 33.34 | yes |
| Tax rectangle | gis-conflict | 10076.0 | 10076.0 | yes |
| Footprint share % | lot-coverage-whole-lot | 66.66 | 66.66 | yes |
| GIS plan depth | gis-conflict | 64.66 | 64.66 | yes |
| GIS back clearance | gis-conflict | 35.31 | 35.31 | yes (not stale 33.32) |
| Frontage conflict | gis-conflict | 3.12 | 3.12 | yes |
| Apartment total | area-allocation | 12090.00 | 12090.0 | yes |
| Other total | area-allocation | 8060.00 | 8060.0 | yes |
| Total | area-allocation | 20150.00 | 20150.0 | yes |
| apt + other == total | area-allocation | 20150.0 | — | yes |
| Apt per storey | area-allocation | 4030.00 | 4030.0 (helper) | yes |
| Other per storey | area-allocation | 2686.67 | 2686.67 (helper) | yes |
| per-storey sum == plate | area-allocation | 6716.67 | — | yes |

The plate/footprint are kept as separate recomputes 0.01 sqft apart, reconciled within ±0.5, never forced equal (code raises if >0.5). The `plate_full` (20150/3) is carried at full precision into the depth division, matching the reference's `6716.6667` operand.

## What I checked (reproducible)

1. **Independent recompute** (`/root/project/lanes-runtime/venv/bin/python`, Decimal ROUND_HALF_UP): every value above matches the reference case and the code.
2. **Schema conformance**: validated placed-placement, withheld-placement, and area_allocation dicts against the bundled `app/_contract_schemas/v1/results.schema.json` via `jsonschema` Draft202012 — **0 errors each**. The bundled schema is byte-identical (LF-normalized `diff`) to `packages/contracts/schemas/v1/results.schema.json`; both define `building_placement`/`area_allocation` at contract **1.5.0**.
3. **One basis, no mixing**: placement carries exactly one basis field `printed_tax_map` (one of the nine `QUANTITY_BASES`, which the schema enum equals). GIS figures appear only as prose inside a `contradicted_record` condition — never in a basis-tagged field; the two bases are never summed or chosen. `area_allocation` has no basis property in the schema and emits none (correct).
4. **Measure statement**: both modules emit `measure="residential_floor_area"` and the G-14 `conversion_statement` byte-exact with the schema consts (test `test_s7_consts_match_the_schema_byte_for_byte`, reproduced).
5. **Zoning-lot condition (Z1, lot 70 alone)**: carried as an `unchecked_condition` ("If this lot alone is the zoning lot…"). GIS conflict carried and resolved by neither (settled_by a survey/deed).
6. **No plan keys**: no unit count, room, core, stair, elevator, or wall key; `additionalProperties:false` rejects any (parametrized tests reproduced).
7. **Withheld / fitted**: `placed=False` (or any missing fact — ZFA/storeys/frontage/depth, each `is None`, not truthiness) yields status `withheld` with no `outline` key; a real 0 frontage raises (fails closed). `fitted == (placement_status=="placed")` by equality, parametrized over placed/withheld/None/other.
8. **8,060 no-conflation (G-10)**: `0.80×10,075 = 8,060` (coverage bound) equals the other-area total numerically but on a different basis; the allocation module emits/sums/equates no coverage figure (`__all__` has no "coverage" symbol).
9. **Scope & isolation**: exactly the 5 allowed_paths changed; no forbidden path (schema, `__init__.py`, reference-cases, evidence-records) touched. Both modules import only stdlib (`dataclasses`, `decimal`, `__future__`) — nothing from `three_way_document`/`geometry`/`first_option_results`/`envelope_constraints`, as claimed.
10. **Tests**: the two focused files pass under the lanes venv (`flock`-serialized): **54 passed in 0.93s**. Whole-api green at builder commit is recorded in `wholeapi-M5-T182-9b902d20.log` (9830 passed, 8 skipped) — I did not re-run the full suite (CI's job; serialized-run policy).
11. **Directive bearing**: R044 (every outline vertex derived, no typed-in coordinate) and R092/G-14 (fixed measure statement) are satisfied in the data contract. The full per-requirement directive pass is the `directive-compliance-verifier`'s role, not this G1 data-contract review.

## Observations (ADVISORY, no correction required)

- **A1 (advisory):** `area_allocation` emits totals only; the reference row's per-storey figures (4,030.00 / 2,686.67) are produced only by the exported `per_storey_area` helper (tested, sums to plate), not in the dict — correct, since the 1.5.0 schema carries no per-storey field. Downstream wiring (M5-T172) is where per-storey display is consumed.
- **A2 (advisory):** placement `measure` is the fixed const `residential_floor_area` while the plate is zoning-floor-area/storey; for Building B these coincide (all-residential), and the const is schema-mandated, so this is correct for the benchmark.

## Could not check
- Live wiring into the results document/register/benchmark — out of scope by design (M5-T172 does it later); not part of this task.
- Full-suite rerun on current HEAD — relied on the recorded builder-commit log and CI per policy.

END-OF-REPORT

## G3 (code-reviewer)

I have everything needed. All checks reproduced independently. Here is my gate report.

---

# G3 Gate Report — M5-T182 (code-reviewer share)

**Task:** M5-T182 — pure illustrative placement + area-allocation modules (`services/api/app/scenario/three_answers/placement.py`, `area_allocation.py` + unit tests). **Reviewed SHA:** `db590413` (cherry-pick of builder `9b902d20`) on `task/wave26-envelope-constraints`. I am an AI agent; this is not a human or professional review.

**Identity note:** the 4 task files are byte-identical between `db590413` and the live worktree HEAD (`86ae6cb`) — verified by `git diff db590413 HEAD -- <path>` (empty). I ran checks against the live worktree; results apply to the reviewed SHA.

## Verdict: PASS (two ADVISORY notes, non-blocking)

## What I checked (reproduced)

- **Correctness vs the sole numeric source** (`placement-building-b.json`, step P8). Independently recomputed every value from the facts (no module import): plate 6716.67; plan_depth 66.66; footprint 6716.66; tax back clearance 33.34; tax rectangle 10076; footprint share 66.66; shoelace outline area 6716.66; GIS plan depth 64.66; **GIS back clearance 35.31** (the judge's correction, not stale 33.32); frontage conflict 3.12; allocation apartment 12090.00 / other 8060.00 / total 20150.00; per-storey 4030.00 + 2686.67 = 6716.67 plate. All match the settled reading and the module output.
- **Interface for M5-T172.** `build_placement(*, placed, zfa, storeys, frontage, lot_depth, gis_frontage, gis_depth)` → placed/withheld dict; `build_area_allocation(*, residential_floor_area_sqft, placement_status, share)` → dict or None. Keyword-only, defensible. Returned shapes validated against contract 1.5.0 `$defs.building_placement` / `$defs.area_allocation` (bundled `app._contract_schemas/v1` confirmed byte-identical to `packages/contracts/schemas/v1` for every relevant `$def`). Placed keys = status/label/outline/method/basis/measure/conversion_statement/checks/conditions/not_checked; withheld correctly omits `outline`; alloc carries the 8 required keys. `fitted` follows `placement_status == "placed"` (equality, tested across placed/withheld/None/other).
- **Missing/unknown held back (no default, no truthiness on a fact).** Every optional fact is read with `is None`; a real `0.0` frontage raises (not silently withheld). Confirmed by `test_a_missing_fact_withholds_the_placement` (4-way), `test_a_real_zero_frontage_is_a_value_not_a_missing_fact`, `test_fitted_follows_the_placement_status`, `test_a_missing_floor_area_holds_the_allocation_back`.
- **Import isolation.** Production modules import stdlib only (`dataclasses`, `decimal`, `__future__`). Nothing from `three_way_document.py`, `geometry.py`, `first_option_results.py`, `envelope_constraints.py`. Diff touches exactly the 5 allowed paths; no forbidden path (incl. `__init__.py`, schemas) touched.
- **Modularity.** `python tools/modularity_check.py --check` → **failures 0**; neither new module (340 / 114 lines) appears in warnings. Single, clear responsibilities; no mixed I/O/clock/AI.
- **Rounding/Decimal discipline.** `_round2` uses `Decimal(str(v)).quantize(0.01, ROUND_HALF_UP)`. Plate carried at full precision for the depth division (matches the reading's 6716.6667 operand); footprint uses the rounded depth; outline area is **measured** by shoelace and reconciled within 0.5 sq ft, not forced equal to the plate (0.01 apart). Way-rule enforces apartment+other=total within 0.01.
- **Plain user texts.** Scanned all returned dicts for internal names (task/record ids, "reference case", "captured", "snapshot", "benchmark", file names) → **NONE**. Check prose cites ZR sections only (per-stat links, as the design contract wants), with the "not a determination / buildable / feasible" disclaimer.
- **Ruff.** `python -m ruff check` on the 4 files → All checks passed.
- **Tests.** `pytest` on both files → **54 passed**. Every test is non-vacuous (see below). Whole-api green is per the provided CI log (`9b902d20`: 9830 passed, 8 skipped); I reproduced the two focused suites.

## Test quality (each would fail on its guarded defect)

All 54 bite. Strongest anti-defect tests: `test_s1_footprint_reconciles...not_forced_equal` (would fail if footprint were set = plate); `test_s2_outline_vertices_are_derived` + `test_s2_outline_area_reconciles` (shoelace-measured, catches a typed-in/wrong vertex, R044); `test_s6_offsets...` pinning **35.31**; the zero-frontage and fitted-equality tests (catch a truthiness substitution); `test_s7_fitted_true_with_withheld...refused_by_cross_key_rule` (exercises the way-rule the module itself never triggers). **No vacuous test.** Weakest-but-valid: `test_s5_two_8060_figures_are_equal_numerals` mostly documents the 8,060 coincidence, but still pins `other_area==8060`; conflation prevention is separately covered by the "never carries a coverage figure" / "computes no coverage" tests.

## Findings

1. **ADVISORY — asymmetric dimension guard.** `compute_placement_geometry` raises on `frontage_ft <= 0` but has **no `lot_depth_ft <= 0` guard** (nor `gis_depth_ft`). A zero/negative depth would not fail closed: `tax_back_clearance` goes negative and `footprint_share = ... if tax_rectangle else 0.0` silently returns 0.0 (a truthiness guard on the derived rectangle). The `None`-missing path is correct and the worked example is unaffected, but for M5-T172 robustness add a symmetric positive-dimension guard. (`placement.py` ~L148, L160.)
2. **ADVISORY — "exactly" overstates for sub-cent inputs.** `area_allocation.py` docstring claims `apartment + other = total exactly`. `other = round2(rfa − apartment)`, `total = round2(rfa)`; for a residential floor area with >2 decimals the sum can differ from `total` by up to 0.01 (reproduced: rfa=10000.005 → diff 0.01). The way-rule's 0.01 tolerance covers it, so no functional defect — only reword to "within the display rounding" or state the 2-dp precondition.

Note (not a finding): hard-coded 5-ft / 100% / 80% values appear only as narrative citing ZR 23-335(b) / 23-362 / 12-10, matching the settled reading; they drive no calculation.

## What I could not check

- The full 9830-test api suite (relied on the provided `9b902d20` CI log plus my focused 54-test run; the 4 files are identical at HEAD).
- The separate directive-compliance verification of D-094 R044/R092 (owner-directive pass belongs to `directive-compliance-verifier`, not this G3 share).

END-OF-REPORT

## G4 (qa-engineer)

I have everything needed. All checks reproduce green, all 6 mutations are caught, every pinned value re-derives from the settled case, and the task's own commit respects every forbidden path. Here is my gate report.

---

# M5-T182 G4 gate report (qa-engineer, independent review)

**Verdict: PASS**

I am an AI agent performing an independent, read-only QA review (not a human or professional review). I did not produce this task. Reviewed at pinned commit `db590413` (cherry-pick of builder `9b902d20`; claim head `dc3a2276`), in a `git archive` copy under `/tmp/claude-0/t182-review-g4/`. Expected values taken only from `docs/reference-cases/R6B/cases/placement-building-b.json` (step P8), never a program run.

## Commands run (lanes venv 3.12, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, from services/api; direct exit codes)

| # | command | exit | result |
|---|---|---|---|
| 1 | `python -m ruff check .` | 0 | All checks passed! |
| 2 | `pytest test_placement.py` | 0 | 27 passed |
| 3 | `pytest test_area_allocation.py` | 0 | 27 passed |
| 4 | `flock heavy-run.lock pytest tests/scenario/three_answers` | 0 | **580 passed, 2 skipped** in 46.37s (whole dir, incl. both new files + all neighbours; no regression) |

The lock was free; the whole-directory heavy run completed (the producer could not run it — lock then held by the preview server). Whole-api suite is green at builder head per `wholeapi-M5-T182-9b902d20.log` (9830 passed, 8 skipped, EXIT 0); that is CI's job, not my share.

## Scenario coverage (packet S1–S8)

| S | how I tested | result | exit |
|---|---|---|---|
| S1 plate+footprint reconcile | `test_s1_*` + independent re-derive | plate 6716.67, depth 66.66, footprint 6716.66 (0.01 under plate, within 0.5, not forced equal) | 0 |
| S2 placed outline, every vertex derived + shoelace-reconciled | `test_s2_*` + mutation 3 | closed rectangle from frontage/depth/touches; measured area 6716.66; mutation 3 proves the reconcile guard | 0 |
| S3 withheld, no outline | `test_s3_*` + mutation 4 | status withheld, outline key absent, schema rejects an injected outline | 0 |
| S4 area split | `test_s4_*` | apt 12090.00/4030.00, other 8060.00/2686.67, total 20150.00; per-storey sum = plate 6716.67 | 0 |
| S5 8060 no-conflation (G-10) | `test_s5_*` | other-total 8060 vs coverage bound 0.80×10075=8060 — equal numerals, different bases; module emits no coverage symbol | 0 |
| S6 offsets both bases | `test_s6_*` + mutation 3 | tax back 33.34 vs GIS 35.31 (NOT 33.32), frontage conflict 3.12; carried as contradicted_record, resolved by neither | 0 |
| S7 schema + no plan keys + fitted-true-withheld refused | `test_s7_*` + mutation 5 | both dicts conform to $defs; 7 plan keys rejected; cross-key rule `allocation_fitted_without_placement` fires | 0 |
| S8 fixed measure (G-14) | `test_s8_*` | conversion_statement byte-exact; physical floor plate in not_checked; plate never returned as physical plate | 0 |

Every pinned value independently re-derived (Decimal round_half_up_2dp) from the settled case — all match. G-14 statement is byte-exact with the work order; GIS back clearance 35.31 = 99.97−64.66, matching the judge's correction (return-spec-M5-T172 finding 1), not the stale 33.32.

## My own mutation probes (copy; each failed ≥1 test; restored, md5 back to original)

1. plate divided by fixed 2 → `test_s1_plate...`, `test_s1_plan_depth...` FAILED (plate 10075; reconcile guard also fired). ✓
2. share 0.65 → `test_s4_split_totals`, `test_s4_the_default_share...` FAILED. ✓
3. GIS frontage as footprint basis → `test_s1_plan_depth...`, `test_s1_footprint_reconciles...`, `test_s2_outline_vertices...` FAILED (footprint 6515.14, no reconcile). ✓
4. withheld placement carrying an outline → `test_s3_withheld_has_no_outline_and_validates` FAILED. ✓
5. fitted always true → 5 tests FAILED incl. cross-key `allocation_fitted_without_placement`. ✓
6. missing frontage defaulted to 100.76 → `test_a_missing_fact_withholds_the_placement[frontage None]` FAILED (placed, not withheld). ✓

## Forbidden-path discipline

M5-T182's **own** commit `db590413` (vs parent) touches exactly the 5 allowed_paths — no forbidden path. Builder `9b902d20` (parent = claim head `dc3a2276`) touches the same 5; all 5 material files are byte-identical between `9b902d20` and `db590413` (cherry-pick preserved content). Imports are stdlib only (`dataclasses`, `decimal`, `__future__`) — full isolation from `three_way_document.py`/`geometry.py`/`first_option_results.py`/`envelope_constraints.py` (RISK A1 met). Live `modularity_check --check` exit 0, no warning for either new module (340/114 lines, focused).

## Directive requirements (behavioral check in my scope)

- **D-094-R044** (never invent geometry; drawings from calculated source-based geometry): applicable to M5-T182; satisfied — every outline vertex is an arithmetic expression of derived depth/frontage/touches, area shoelace-measured and reconciled to the plate (mutation 3 proves enforcement).
- **D-094-R092** (compatible area measures; zoning floor area never auto-treated as physical floor plate): applicable to M5-T182; satisfied — both modules carry `measure="residential_floor_area"` and the G-14 conversion statement; physical floor plate listed not_checked.

(The full per-requirement in-regime pass is the directive-compliance-verifier's, recorded in verification.json.)

## Findings

- **F1 (ADVISORY, identity note).** The literal check "every forbidden path byte-identical between `dc3a2276` and `db590413`" does NOT hold at the two-commit *range*: `docs/reference-cases/**` and `services/api/app/drawings/kit/area_allocation.py` differ. These come from **disjoint peer commits** `dec38ebf` (M5-T183) and `d0f15242` (M5-T184), not from M5-T182. The task's own change is clean. No correction needed; recommend the orchestrator record the disjoint-peer context in the frozen-head accept assembly.

## What I could not check
- Full services/api suite (my heavy share is scoped to `tests/scenario/three_answers`; whole-api is CI/precheck — green at builder head per the log).
- I did not re-open the ZR snapshots line by line; the modules quote section numbers only as plain readings carried from the settled case, which revises no evidence record (NB-03/NB-04/NB-06 unchanged).

No REQUIRED defects. Verdict: **PASS** (with the F1 advisory identity note).

END-OF-REPORT
