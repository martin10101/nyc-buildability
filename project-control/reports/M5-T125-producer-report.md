# M5-T125 — producer report: Wave 0 contracts v1 + benchmark fixtures

| | |
|---|---|
| Task | M5-T125 (D-090 Wave 0, Prompt 0 step 5; D-090-R002, R003, R004, R009, R010) |
| Worktree / branch | `/root/project/w-M5-T125` / `lane-c/M5-T125-contracts-v1` (base `8a813bdd`) |
| Producer | orchestrator-dispatched producer (no git write, no ledger CLI, no npm/npx/node, no network) |
| Change type | **New files only.** No existing schema, fixture, generated file, README or script was edited. |

## 1. Files added (45)

Schemas (6), `packages/contracts/schemas/v1/`:
`site_fact.schema.json`, `study.schema.json`, `results.schema.json`, `report_model.schema.json`,
`export_record.schema.json`, `benchmark_lot.schema.json`.

Fixtures (39), `packages/contracts/fixtures/{valid,invalid}/<stem>/`:

| Stem | Valid | Invalid (each carries `_expected_failure`) |
|---|---|---|
| site_fact | `wallabout_base_lot_32_lot_area_unknown`, `synthetic_lot_area_approximate_tax_map`, `synthetic_street_width_entered`, `synthetic_existing_zoning_floor_area_assumed` | `unknown_encoded_as_zero`, `unknown_without_blocks`, `label_does_not_match_rank`, `existing_zfa_from_recorded_building_area` |
| study | `synthetic_corner_lot_two_options`, `synthetic_copied_from_export_existing_zfa_unknown` | `selection_statement_reworded`, `goal_other_without_text`, `site_fact_unknown_encoded_as_zero`, `revision_one_with_parent` |
| results | `synthetic_all_answers_available`, `synthetic_envelope_not_available_existing_building` | `status_strip_four_items`, `not_available_without_reason`, `shortfall_reason_not_computed`, `unit_estimate_without_formula`, `existing_building_headline_reworded` |
| report_model | `synthetic_full_report` | `floor_area_reminder_reworded`, `missing_floor_by_floor_sheet`, `preliminary_sheet_unmarked`, `calculation_row_not_read_from_results` |
| export_record | `synthetic_pdf_export` | `read_only_false`, `restore_policy_restores_results`, `format_dwg` |
| benchmark_lot | `northern_blvd_215_16_queens_4073340070`, `wallabout_298_brooklyn_3022647515`, `pilot_a_placeholder` | `reviewed_without_review_record`, `recorded_without_fixture_hash`, `review_value_marked_recorded`, `placeholder_with_invented_values`, `expected_value_without_source`, `missing_check_c12` |

Plus this report. Every invalid fixture is a valid fixture with exactly one defect (except
`existing_zfa_from_recorded_building_area`, built fresh; a copy with `kind: city_filing` validates clean).

## 2. Conventions followed

- Draft 2020-12, `$id` = `https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/<stem>.schema.json`,
  relative `$ref`s (`common.schema.json#/$defs/bbl`, `…/date_time`, `…/non_empty_string`, `…/digest_sha256`,
  `…/borough_name`); no remote `$ref`.
- `contract_version`: `{"type":"string","enum":["1.0.0"]}` with the house "CLOSED enum" description.
- `additionalProperties: false` on every object; optional fixture-only `_expected_failure` at each root (scenario/lot_geometry convention).
- Only the validator's keyword subset (no `if/then`, `not`, `contains`, `uniqueItems`, `prefixItems`): conditionals are
  `oneOf`/`anyOf` + `const`; "key present, null when not applicable" is used so absence is visible (source_fact style).
- New schemas cross-reference each other: study → site_fact; results → site_fact (`measurement_known`), study (`goal`);
  report_model / benchmark_lot → results (`unit`, `zr_section`, `exception_label`); export_record → study, site_fact (`source`), results (`rule_version`).
- Synthetic fixtures use BBLs `5999999999` / `5999999998` (the existing no-lot BBL) and `test-fixture-synthetic` ids/datasets.

## 3. Design decisions, traced to the plan (`docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`)

**site_fact** (§3 step 3–4, §4, §9, M1-07)
- `key` enum (lot_area, lot_frontage, lot_depth, lot_type, zoning_district, commercial_overlay, street_width, existing_zoning_floor_area) — §3 steps 3–4. `street` required non-null for frontage/street width ("frontage on each street"). `lot_bbl` null = combined site value (§4 multi-lot).
- `measurement {rank,label}`: six ranks, label tied one-to-one by `const` pairs. Labels "Survey (entered)", "City records", "Approximate — tax map", "Unknown — enter" are §4 verbatim; **"Entered" / "Assumed" are my wording** (M1-07 status names; the plan gives none).
- **Unknown never 0** (§9): known ranks need non-null value + non-null source + empty `blocks`; `unknown` needs value/unit null and non-empty `blocks`; lot area, frontage, depth, street width are `exclusiveMinimum 0`.
- `source {kind, dataset, dataset_version, retrieved_at, query_ref, document_ref, statement}` (lane plan §5 "source, dataset version and date"); rank↔kind tied (city_records ← city_dataset|city_filing; approximate ← tax_map_computation; …).
- `existing_zoning_floor_area` accepts only city_filing / architect_entry / assumption sources — PLUTO/DOF building area cannot enter (§3 step 4, §8, M2-07).
- `editable` (§3 step 3). Optional `source.provenance_refs` links to `source_fact` provenance ids so this display summary never competes with the canonical PRD §9 record (backend-api rule "never fork a competing schema").

**study** (§3 steps 1–2, 4, 6; §5; §9; M1-09, M1-11)
- `property {bbl,address}`; `lots[] {bbl, approximate_lot_area_sq_ft, size_measurement, selected}` (null size ⇔ rank unknown).
- `lot_selection {mode all|subset, statement const "Based on the lots you selected — the app does not verify the zoning lot", combination single_lot|offered|not_offered+reason}` (§3 step 2, §8).
- `site.facts[]` = `$ref site_fact` (shared site, §9). `options[] {option_id, name, addon_selection[{addon_id,on}], goal (most_residential_floor_area|most_total_floor_area|other+text), program[], floor_to_floor_heights {ground, typical: {height_ft, basis stated_default|entered, statement}, per_floor_overrides}, assumptions[], existing_building_plan}`.
- **Added beyond the brief:** `existing_building_plan` (no_existing_building|keep|remove — §3 step 4, needed for §5 answer 1) and `origin` (new | copied_from_export+export_id — §9 "Start a new study from this").
- `revision {number, created_at, parent}`: revision 1 ⇔ parent null. `selected_option_id` ∈ options is a store-side check (not expressible).

**results** (§3 step 4, §5, §5a, §5b, §5c, §9, §11b; M1-14, M1-25; checks C-2..C-12)
- `answers.{floor_area_allowance, permitted_envelope, building_option}` each `oneOf` available `{values[{key,label,value,unit,zr_sections≥1,sources≥1,exception_label}], measurement (weakest input, §4)}` | `not_available {reason, reason_kind}` (§5 three conditions, §8).
- `exception_label` single enum/null = "at most one per row" (§5a item 3). `with_approvals_label` const/null (§5).
- `remaining_floor_area` (available with the existing-ZFA fact id | not_available | not_applicable) — §3 step 4.
- `shortfall` none | `{sq_ft>0, reasons[{text, computed_from≥1, values≥1}]}` | not_available (§5 answer 3; C-2, C-11).
- `addon_gains[] {group A|B|C|D1, on, relative_to const current_selection, requires, gain}` (D2 never has a number, §5/§6); `best_combination {goal ($ref study goal), selected_addon_ids, excluded[{addon_id, reason}], goal_value_sf}`.
- `completeness_line`, `status_strip` 1..3 items (§5a-1), `notices_count` (§5a-6), `floor_by_floor[]` (§5, uses from the §5c style table), `floor_stack`, `existing_building` (none | present {keep, partial_rebuild, full_rebuild each available|not_available; `headline` pattern of the §5b sentence; `larger_than_allowed_flag` = §8 wording}), `unit_estimate {value, formula, factor, rounding_rule, zr_sections}` (§11b; C-12).
- `geometry` {crs local_feet|EPSG:2263, units feet, measurement (drives the DXF note), lot_outline, yards[required|not_required], setback_lines_per_level, envelope.tiers, floor_plates} (§5c-1, §4 "Coordinates").
- `rule_versions[]` reuses the repo's rule status vocabulary (discovered|extracted_draft|needs_review|published).
- **Added:** `out_of_date` + reason, `depends_on_fact_ids` (§9 invalidation), `lot_selection_statement` (C-9).
- Note: the §8 flag wording ("The existing building is larger …") differs by one word from review C-3; the plan wins.

**report_model** (§3 step 7, §5a, §5c, §9; M1-16, M1-19, M1-22, M1-24)
- `results_ref {results_id, study_id, option_id, revision, results_digest}`; `identification_line {option_name, revision, date, text "X · revision N · YYYY-MM-DD"}`.
- **`sheets` is an object keyed by sheet, not an array** (deviation from the brief's `sheets[]`): the validator has no `contains`/`uniqueItems`, so only an object can enforce M1-22 "the PDF contains every listed sheet". `page_order` gives sequence; drawing sheets may be not_available with one line (M1-16); `dob_style_preliminary` optional, marking const "Preliminary — not for filing".
- `standing_notices {shown_once const true, page_order, not_dob_approval, floor_area_reminder const (§5a item 2 verbatim), zoning_lot_not_verified const, district_incomplete|null, additional[]}`.
- `calculation_rows[]` available `{row_id, label, value, unit, zr_section|null, source, reads, exception_label}` | not_available `{reason, reads}`. Every figure carries a `reads` pointer `{document results|study|report_model, pointer}` (§5c-5; C-4/C-5) — study is needed because lot area is a site fact, not a result.

**export_record** (§3 step 7, §9 historical exports; M1-19): `format pdf|xlsx|dxf`, `inputs {study ($ref study), study_digest}`, `sources[]` (site_fact source), `rule_versions[]`, `results {results_id, results_digest, snapshot_ref}`, `read_only const true`, `restore_policy const "copy_inputs_only"`.

**benchmark_lot** (§9a-6, §11; review §A/§D; D-090-R002, R010)
- `purpose benchmark|pilot|multi_lot_pilot`; `identity` object | null (null ⇒ no expected values and ≥1 open item).
- `expected_values[] {key, label, value number|string|null, unit, source {kind, ref, sha256, pointer, cited_in, quote}, verification_state, review, note}`.
- `verification_state` adds **`pending`** to the brief's list (the brief itself requires "pending" for Wallabout plan facts). State↔source tied: expected_unverified ← competitor_review|zoning_resolution|public_record; recorded ← recorded_fixture (path pattern + file SHA-256 + pointer required); **reviewed requires a `review {reviewer, reviewed_at, record_ref}`** — nothing can be marked reviewed without one (R010).
- `checks[]` exactly 12, each id `const`-tied to its review §D title; `applicability applies|not_applicable|pending` (+reason unless applies); `pass_when` = review text verbatim.
- `recorded_fixtures[] {path, sha256 (raw-bytes hex, MANIFEST convention), dataset, retrieved_at (timestamp|date|null), note}`; added `reference_documents[]` (path+SHA-256 of the review and plan) and `basis`.

## 4. Benchmark fixtures

1. **215-16 Northern Blvd** (`4073340070`): 31 values from review §A, all `expected_unverified`, `ref` = the review's Source cell verbatim ("Public records; report p. 5", "Report p. 5–6 (verify in ZoLa)", "ZR 23-22", "ZR 23-432", "ZR 23-362", "ZR 23-344(a)", "ZR 23-52", "Report p. 5; public records", "ACRIS entries via PropertyShark"), `quote` = the Expected cell verbatim, `cited_in` = review §A. Kind follows the cell's first-named source (public_record vs competitor_review). The 54,488 sq ft is keyed `existing_building_recorded_floor_area` with a note that it is not zoning floor area. The four "To verify" items + 4 more are open items; C-1..C-12 all `applies`. Review SHA-256 `893fbe9f…bb53` (matches D-090).
2. **298 Wallabout** (billing `3022647515` → `3022640032`, `3022640033`): 16 `recorded` values (condo 1313, key 301313, billing BBL, 2 base lots, 14 / 6 unit lots, block 2264, polygon counts 1/1/0, CONDO_FLAG C/C, outline outcomes) each cited by path + SHA-256 + pointer; 8 recorded files listed (3 DTM captures — hashes equal the MANIFEST's — MANIFEST, 2 lot_geometry fixtures, `test_dtm_condo_soda.py`, the condo research doc). R7-1, the 2001 rezoning, the 2005 7-story/20-unit building, the 2023 stop-work order and street widths (null) are `pending` + open items. No area/dimension computed from the 4326 outlines. Checks all `pending` (the plan does not say which checks gate Pilot B).
3. **Pilot A placeholder**: identity null, no values, checks pending (Q1), open_items `["Owner decision Q1: pilot lot and verifier"]`.

## 5. Verification (run in the worktree)

`python3 .github/scripts/validate_contracts.py` → exit 0:
```
meta-schema engines : stdlib-structural + jsonschema 4.10.3
instance engines    : stdlib mini-validator + jsonschema 4.10.3 (cross-checked)
NOTE: legacy jsonschema RefResolver in use ('referencing' not importable); remote $ref fetching is blocked -- any store miss fails closed.
Checked 17 schema file(s); 0 failure(s).
```
148 `OK` lines, 0 `FAIL`, no validator disagreement; all 6 new schemas OK; new fixtures: site_fact 4 valid / 4 invalid rejected, study 2/4, results 2/5, report_model 1/4, export_record 1/3, benchmark_lot 3/6.
The same run with `jsonschema` blocked (stdlib-only mode, as a runner without it) also ends `Checked 17 schema file(s); 0 failure(s).`

`python3 packages/contracts/scripts/generate_ts_types.py --check` → exit 0 (all six "OK: … up to date" / "matches" lines).
`python3 services/api/scripts/sync_contract_schemas.py --check` → exit 0 ("OK: runtime-bundled contract schemas are byte-identical to the canonical source.").
`python3 .github/scripts/secret_scan.py` → "secret-scan: PASS -- no findings" (scans untracked files too).
Coherence self-check (scratchpad script): every report `reads` pointer resolves to the same value in the results/study fixtures; report and export `results_digest` and `study_digest` equal the canonical-json-1 digests of those fixtures; floor rows sum to the 10,000 sq ft allowance and equal the floor plates.
`git status --short`: only `??` entries under `packages/contracts/schemas/v1/` (6 files) and `packages/contracts/fixtures/{valid,invalid}/<6 new stems>/`, plus this report.

## 6. Deliberately not done

- No TypeScript typegen or runtime-bundle registration (`generate_ts_types.py`, `sync_contract_schemas.py`, `apps/web/src/lib/contract.ts`): the lane that first consumes a schema adds it (G0 packet). No consumer exists yet.
- `packages/contracts/README.md` not updated (outside allowed_paths; it still lists these contracts as not stubbed) — follow-up for Lane C.
- The pytest suites that load every schema (`.github/scripts/tests`, `services/api/tests/contracts`, `…/scenario`) were not run locally (pytest is not installed); they only build `$id` registries, which the validator already exercises. CI runs them.
- Cross-field rules outside the keyword subset are left to consumers and stated in descriptions: `selected_option_id` ∈ options, unique check ids, ZFA = gross − deductions, pointer resolution, ZR section existence (C-7).
- No live city calls; nothing marked reviewed; all rule versions in fixtures are `needs_review`.

## 7. Findings for the integrator

- Plan §11 lists "lot 33 as a base lot" as unconfirmed, but the recorded DTM condo response (research §3.3; `test_dtm_condo_soda.py`) lists lot 33 as a base lot of condo 1313 — plan wording to reconcile (recorded as an open item).
- For 215-16 Northern the review's 54,488 sq ft is recorded building area; M2-08 ("path 1 keeps more floor area than path 3") will need an established or entered existing zoning floor area.
- R7-1 for both Wallabout base lots is observed in the condo research doc §7 (ZTLDB, 2026-09-18) but no recorded zoning fixture exists; kept `pending` as instructed.
