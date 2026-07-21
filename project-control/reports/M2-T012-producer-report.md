# M2-T012 — Producer report

Task: **M2-T012 Profile integration of wave connectors + spatial results (single contract 1.4.0 update).**
Producer: orchestrator (lead-only, owner directive 2026-07-21). Status: **implementation complete;
submitted to independent gates at the frozen submit SHA below.**

## Submission summary

ONE coordinated **contract 1.4.0** update carries the accepted connector-wave and spatial-intersection
facts into the canonical property profile, published through the accepted M2-T010 derivation tooling.
Additive-only: every 1.0.0–1.3.0 payload still validates; the builder now declares 1.4.0 and a
PLUTO-only build emits no 1.4.0 key. Uncertainty is never collapsed and nothing is ever `Verified`.

- **Frozen submit SHA:** this report's commit on `task/M2-T012-profile` (resolve live with
  `git -C .claude/worktrees/M2-T012-profile rev-parse HEAD`; the exact 40-char SHA is recorded in the
  orchestrator's frozen-SHA evidence packet). Parent lineage: `ac7cc3e` (session-resume checkpoint) →
  `cabe419` (origin/main `047d31c` integration) → prior accepted work.
- **origin/main integrated:** `047d31cda0f76c07ca62339ae42dd9f19f0afac0` (clean merge at `cabe419`).

## What was built (contract 1.4.0)

### 1. Three additive top-level profile keys, each with full provenance
- **`zoning_features`** — per-layer RETRIEVAL facts for the six DCP GIS zoning-features layers
  (M2-T007), CITYWIDE reference data (explicitly NOT lot-level determinations). Each `layers[]` entry
  carries `layer` + `provenance_ref` + `coverage_status` (`conditional`, or `unsupported` on a drift
  signal) plus open pass-through keys.
- **`lot_geometry`** — per-BBL MapPLUTO tax-lot geometry facts (M2-T009) with `outcome` +
  `provenance_ref`; the geometry-validity taxonomy is preserved, never a legal boundary certification.
- **`spatial_intersection`** — the M2-T013 facts-with-uncertainty substrate: exact geometric results,
  boundary distances, split-share RANGES, positional-uncertainty classes, professional-review flags,
  `coverage_note`, and `provenance_refs`. The engine-internal `coverage_audits` diagnostic is
  EXCLUDED (owner amendment invariant 6); uncertainty is never collapsed into a definitive assignment.

Implementation: new module `services/api/app/profile/wave_integration.py` maps the accepted
connector/engine RESULTS (read-only, duck-typed) into the three sections plus canonical `source_fact`
provenance records; `build_property_profile` gained three additive optional params
(`lot_geometry` / `zoning_features` / `spatial_intersection`, default None → PLUTO-only build
byte-unchanged). `_assert_provenance_integrity` was extended to the three new provenance_ref sites
(the backend is the integrity authority for live data — PRD s9/s19).

### 2. Fourth (geometric) evidence stream — through the EXISTING conflict shape
`app.profile.zoning_crosscheck.geometric_zoning_observations()` emits a geometric `zonedist1`
observation ONLY when the lot is `single_district_confident`; fed to `crosscheck_lot_zoning` via
`external_observations`, a geometric value disagreeing with the ZTLDB/PLUTO `zonedist1` becomes a
typed `conflict` (`resolution='unresolved'`) in the existing `conflicts` array and — on the critical
column — gates `analysis_readiness` through the existing M2-T004 machinery. Uncertain lots emit no
collapsing value (uncertainty preserved).

### 3. Contract 1.4.0 published through the M2-T010 derivation tooling
- `packages/contracts/schemas/v1/property_profile.schema.json`: appended `"1.4.0"` to the closed
  `contract_version` enum + the three optional keys (all within the `validate_contracts.py` keyword
  subset; required ⊆ properties house rule honored).
- `python services/api/scripts/sync_contract_schemas.py` → byte-identical bundle in
  `services/api/app/_contract_schemas/v1/` (backend `SUPPORTED_CONTRACT_VERSIONS` now derives 1.4.0
  live).
- `python packages/contracts/scripts/generate_ts_types.py` → regenerated
  `packages/contracts/generated/property_profile.ts` + the marker-delimited web
  `SUPPORTED_CONTRACT_VERSIONS` block in `apps/web/src/lib/contract.ts`.
- `app.profile.contract.VERSION_INTRODUCED` registers the three keys at 1.4.0;
  `app.profile.builder.PROFILE_CONTRACT_VERSION = "1.4.0"`.
- Rejected-exemplar fixture `contract_version_unknown.json` advanced `1.4.0 → 1.5.0` (a
  NEVER-PUBLISHED rejection exemplar — unrelated to the owner STOP condition on real 1.5.0
  publication).

## Acceptance scenarios PI-S1 … PI-S8 (evidence)

| Scenario | Evidence |
|---|---|
| PI-S1 primary integration | `tests/profile/test_wave_integration.py::test_pi_s1_...` — 1.4.0 profile carries all three streams; every provenance_ref resolves; schema-validates |
| PI-S2 uncertainty preservation | `...::test_pi_s2_...` — `lot_overall_class` + `pair_class` + share RANGE all present; no `assigned_district`; `coverage_note` disclaims Verified |
| PI-S3 conflict (4th stream) | `...::test_pi_s3_geometric_disagreement_...` (+ agreement + uncertain-no-emit) — typed unresolved conflict; gates `blocked_data_conflict` |
| PI-S4 back-compat | `...::test_pi_s4_...` (3 tests) + existing `test_property_contract.py::test_s7_*` — 1.0.0–1.3.0 fixtures validate; wave payload misdeclaring 1.3.0 rejected |
| PI-S5 drift tooling | `...::test_pi_s5_...` (live SUPPORTED_CONTRACT_VERSIONS + VERSION_INTRODUCED; declaring-below-emitted red path per key) + generator tests + `contracts-typegen --check` |
| PI-S6 carried defects | `tests/connectors/test_m2_t012_carried_defects.py` (8 tests) + 2 in-place fixes — see per-defect table below |
| PI-S7 missing data | `...::test_pi_s7_...` (3 tests) — no_feature → not_applicable; review → professional_review_required; absent wave data invents nothing |
| PI-S8 regression | full API suite **590 passed**; contracts / typegen / schema-bundle / smoke green (self-check below) |

## PI-S6 — carried LOW-defect fixes (each with evidence)

| Defect | Fix | Evidence |
|---|---|---|
| M2-T007 G1 D1 (out_fields footgun) | explicit `outFields` omitting the object-id field → typed `disallowed_request` (not upstream blame), in `zoning_features_arcgis.build_query_url` | `test_m2t007_g1d1_out_fields_omitting_object_id_is_disallowed_request` |
| M2-T007 G3/G4 D1 (untested drift signals) | assert `missing_editing_info` + `page_missing_spatial_reference` emitted (test-only) | `test_m2t007_g3d1_missing_editing_info_...`, `..._page_missing_spatial_reference_...` |
| M2-T007 G3/G4 D2 (test-name mismatch) | renamed `..._propagates_into_extraction_result` → `..._into_query_result` + removed dead `page` load, in `test_zoning_features_arcgis.py` | `tests/connectors/test_zoning_features_arcgis.py::test_s9_added_field_signal_propagates_into_query_result` |
| M2-T007 G3/G4 D3 (count==cap default-page) | test extract_layer(nylh) at DEFAULT page_size, count 14 == cap 14 → one page | `test_m2t007_g3d3_count_equals_cap_extracts_in_one_page_at_default_page_size` |
| M2-T008 G3/G4 D1 (check_columns_for_drift TypeError) | filter columns to string `fieldName` so `sorted()` never mixes `None` + str, in `ztldb_soda.check_columns_for_drift` | `test_m2t008_g3d1_check_columns_for_drift_tolerates_doubly_malformed_metadata` |
| M2-T008 G3/G4 O2 (SOCRATA_APP_TOKEN hermeticity) | autouse fixture clears ambient `SOCRATA_APP_TOKEN`, in `test_ztldb_soda.py` | `test_ztldb_soda.py::_hermetic_app_token` (autouse; whole module) |
| M2-T009 G4 D1 (top-level metadata spatialReference) | assert TOP-LEVEL `spatialReference` (not only `extent`), in `mappluto_geometry_arcgis.fetch_layer_metadata` | `test_m2t009_g4d1_wrong_top_level_spatial_reference_is_typed_wrong_crs` |
| M2-T009 metadata-TTL-cache option | opt-in `metadata_cache_ttl_seconds` on `ResilientMapPlutoGeometryClient` (default OFF → unchanged) | `test_m2t009_metadata_ttl_cache_reuses_metadata_...`, `..._off_by_default_refetches_metadata` |

All connector touches are ONLY for these enumerated carried defects (per the packet's connector/resilience
scope condition), disclosed per-defect above.

## Self-check evidence (local, worktree; Python 3.11.9, jsonschema 4.26.0, shapely 2.0.7)

- `ruff check .` (services/api) → **All checks passed**
- `python -m pytest -q` (services/api) → **590 passed**
- `python .github/scripts/validate_contracts.py` → 6 schemas, **0 failures** (all fixtures incl. the
  advanced rejected exemplar)
- `python packages/contracts/scripts/generate_ts_types.py --check` → generated TS + client version
  block up to date
- `python services/api/scripts/sync_contract_schemas.py --check` → runtime bundle byte-identical
- `python -m pytest packages/contracts/scripts/tests -q` → **14 passed**
- `python -m pytest .github/scripts/tests -q` → **24 passed**
- `python scripts/exact_install_smoke.py` → positive smoke OK (validate_profile on valid fixture)

The **web** jobs (lint / typecheck / build / vitest, Node-only) are not runnable on the thin client;
they run on CI. The biggest web risk — the generated types + client version block — is covered by the
locally-run `contracts-typegen --check`; the web version-assertion tests were updated in lockstep
(`contract-versions.test.ts`, `validate-profile.test.ts`).

## Scope decisions & disclosures

- **Web validator not extended for the new sections.** The web `validateProfileDocument` already
  tolerates undocumented extra keys (its own test proves it), and rendering the new facts is a
  SEPARATE frontend task (forbidden path `apps/web/src/components/**`). The correct minimal web change
  is the generated types + version block + version-assertion test updates. No unrenderable
  section validators/aliases were added.
- **`validate_contracts.py` referential-integrity follow-up (out of file scope).** CI's
  `profile_provenance_invariant` still checks only the pre-1.4.0 fixture ref sites; the three new
  sites are enforced by the backend (`_assert_provenance_integrity`) and by unit tests. Extending
  `.github/scripts/validate_contracts.py` to the new fixture sites is a recommended companion change
  in a `.github/`-scoped task.
- **Endpoint unchanged.** No live multi-connector orchestration was wired (that needs credentials —
  out of scope); the integration lands in builder+contract and is fixture/unit-tested.
  `services/api/app/api/v1/**` was not touched (no new typed error surface required).

## Files changed (all within allowed_paths)

Contracts/schema: `packages/contracts/schemas/v1/property_profile.schema.json`,
`services/api/app/_contract_schemas/v1/property_profile.schema.json` (sync tooling),
`packages/contracts/generated/property_profile.ts`, `apps/web/src/lib/contract.ts`,
`packages/contracts/README.md`, `packages/contracts/fixtures/invalid/property_profile/contract_version_unknown.json`.
Backend: `services/api/app/profile/wave_integration.py` (new), `builder.py`, `contract.py`,
`zoning_crosscheck.py`; carried-defect connector touches in `connectors/zoning_features_arcgis.py`,
`connectors/mappluto_geometry_arcgis.py`, `connectors/ztldb_soda.py`.
Tests: `tests/profile/test_wave_integration.py` (new), `tests/connectors/test_m2_t012_carried_defects.py`
(new), plus version/defect updates in `tests/api/test_property_contract.py`,
`tests/api/test_properties_v1.py`, `tests/api/test_contract_schema_packaging.py`,
`tests/profile/test_data_semantics.py`, `tests/connectors/test_zoning_features_arcgis.py`,
`tests/connectors/test_ztldb_soda.py`, `packages/contracts/scripts/tests/test_generate_ts_types.py`.

## Blockers

**None.** All dependencies (M2-T010, M2-T011, M2-T013) accepted; the fixture-based integration needs
no credentials.

## Gate status

Submitting to the independent gates (**G1 data-contract-verifier, G3 code-reviewer, G5
security-reviewer**) at the frozen submit SHA. No reviewer has yet been dispatched at submit time; the
orchestrator dispatches each once at the frozen SHA with a small exact evidence packet and records the
gates. **Not accepted; no merge; awaiting owner review of the frozen-SHA evidence packet.**
