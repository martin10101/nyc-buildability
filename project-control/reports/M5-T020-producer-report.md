# M5-T020 producer report — MapPLUTO lot-outline 4326 transport + flag-gated route + contract

Task: M5-T020 (D-040-R001 server half). Producer: backend-engineer.
Worktree: `worktree-agent-a831ffc855c2cce45` (isolated; reset to packet commit `a5e5e408`).
Date: 2026-09-12. Python sandbox: 3.11.9 (CI runs 3.12 — see Deviations).

## 1. What was built (per file)

All 12 changed paths are within the packet's `allowed_paths`; the byte-immutable
authoritative connector (`mappluto_geometry_arcgis.py`) and `config.py` are
untouched (S4, proven below).

- **`services/api/app/connectors/mappluto_lot_outline.py`** (NEW, ~415 lines) — the
  display-only 4326 transport module. Imports the authoritative connector's PUBLIC
  discipline (`SERVICE_ROOT`, `LAYER_NAME`, `OUT_FIELDS`, `MAX_FEATURES_PER_LOT`,
  `SOURCE_ID`, `BOUNDARY_TOLERANCE_FT`, `_condo_classification`,
  `DisallowedRequestError`) and `normalize_bbl` from `app.connectors.bbl` — by
  IMPORT, never copy-paste-fork, never edit. `build_outline_query_url` mirrors
  `build_lot_query_url`'s injection discipline (BBL only from `normalize_bbl`;
  canonical-form guard; `int()`-interpolated where clause) but appends
  `&f=geojson&outSR=4326`. `parse_lot_outline` classifies the four honest outcomes,
  builds the typed envelope, and `build_lot_outline` validates it against the
  bundled contract before return. Injected `fetch` seam (default = live keyless GET;
  tests inject fixtures). NO area/dimension/measurement anywhere; no `shapely` import.
- **`services/api/app/api/v1/lot_geometry.py`** (NEW, ~210 lines) — `GET
  /api/v1/properties/{bbl}/lot-geometry`, body-less, `include_in_schema=False`,
  flag-gated on the EXISTING `internal_rule_eval_enabled` helper (generic 404 when
  off), `X-Correlation-ID` on every non-404 response, injected fetch seam
  (`get_lot_outline_fetcher`), typed outcomes → honest 200s, faults → typed 5xx,
  renderer-parity `_assert_json_safe` before send.
- **`services/api/app/main.py`** — additive `include_router(lot_geometry_v1_router)`
  only (documented comment mirrors the other internal routes).
- **`packages/contracts/schemas/v1/lot_geometry.schema.json`** + **`services/api/app/_contract_schemas/v1/lot_geometry.schema.json`**
  — NEW closed contract (`additionalProperties:false`), byte-identical copies
  (sha256 `8c55a6a6…`; verified in `test_s6_bundled_schema_is_byte_identical_to_canonical`).
- **`packages/contracts/generated/lot_geometry.ts`** — generated via the repo
  generator's shared emission functions (see Deviations for the entrypoint note).
- **`packages/contracts/fixtures/valid/lot_geometry/`** — 7 valid example envelopes
  (one per outcome incl. Polygon/MultiPolygon/condo-billing single_lot), each
  produced by the connector and contract-validated at generation time.
- **`services/api/tests/fixtures/mappluto_lot_outline/`** — 6 live-captured raw
  fixtures + 2 documented synthetic negatives + `MANIFEST.json`.
- **`services/api/tests/connectors/test_mappluto_lot_outline.py`** + **`services/api/tests/api/test_lot_geometry_api.py`** — the offline acceptance packs.
- **`docs/research/source-registry-drafts/pluto-mappluto.json`** — additive
  `display_outline_usage` block on the `nyc-dcp-mappluto-arcgis` record + a second
  `last_successful_ingestion` capture date.

## 2. Outline envelope field schema (contract `lot_geometry@1.0.0`, closed)

Root (all required unless noted): `contract_version` (`"1.0.0"`), `document_kind`
(`"lot_outline"`), `bbl` (common `bbl`), `outcome`
(`single_lot|no_outline|multiple_features|invalid_geometry`), `display_only`
(`true` const), `crs` (`"EPSG:4326"` const), `geometry` (Polygon | MultiPolygon |
null — non-null ONLY on `single_lot`), `feature_count` (int ≥0), `review_required`
(bool), `no_outline_reason` (`condo_unit_lot_no_polygon|no_feature_for_bbl|null`),
`condo_classification` (`{classification, condo_no, note}` mirrored verbatim from
`_condo_classification`), `lot_identity` (`{boro_code,borough,block,lot,condo_no}` |
null), `source` (`{source_id, service_root, layer, endpoint, dataset_version,
retrieved_at}`), `accuracy_note`, `attribution`, `disclaimer`, `notes` (string[]).
Optional `_expected_failure` is fixture-only (README convention; the builder never
emits it). GeoJSON `$defs`: `position` (`[lng,lat]`, exactly 2), `linear_ring`
(≥4 positions), `polygon_geometry`, `multipolygon_geometry`, `outline_geometry`.

## 3. Capture transcript (recorded-official, S5)

Endpoint shape (all 6): `…/MAPPLUTO/FeatureServer/0/query?where=BBL%3D<int>&outFields=<10-field subset>&orderByFields=OBJECTID%20ASC&resultRecordCount=10&resultOffset=0&f=geojson&outSR=4326`
(keyless GET, `Accept: application/json`). Live-verified `crs.properties.name ==
"EPSG:4326"`, coordinates `[lng,lat]`, per-feature `Version == "26v2"`.

| fixture | BBL | captured (UTC) | HTTP | features | geom | sha256 |
|---|---|---|---|---|---|---|
| LOT01 single | 1008350041 | 2026-09-12T13:45:07Z | 200 | 1 | Polygon | `9e5e1261…` |
| LOT02 no-feature | 5999999999 | 2026-09-12T13:45:08Z | 200 | 0 | — | `1ce7eb45…` |
| LOT03 condo billing | 1000157501 | 2026-09-12T13:45:11Z | 200 | 1 | Polygon | `2c74f51c…` |
| LOT04 condo unit | 1000151001 | 2026-09-12T13:45:12Z | 200 | 0 | — | `1ce7eb45…` |
| LOT05 holes | 1000010010 | 2026-09-12T13:45:13Z | 200 | 1 | Polygon(3 rings) | `859bacb7…` |
| LOT06 multipolygon | 4142600001 | 2026-09-12T13:45:14Z | 200 | 1 | MultiPolygon | `28a79e78…` |

LOT02 and LOT04 share one sha256 (byte-identical empty FeatureCollections;
distinguished by BBL/condo classification, not body — same precedent as M2-T009
MPG03/MPG05). Two SYNTHETIC negatives (classification `synthetic`, `derived_from`
LOT01, documented in MANIFEST — the service does not emit these for a real lot):
LOT80 (`geometry:null` → invalid_geometry, sha256 `ab72a8fe…`), LOT96 (two features
one BBL → multiple_features, sha256 `205ef0ae…`). **No 4326 byte was derived from
the authoritative 2263 fixtures.** Full sha256s + a re-runnable capture procedure
are in `services/api/tests/fixtures/mappluto_lot_outline/MANIFEST.json`;
`test_fixture_bytes_match_manifest_sha256` re-hashes every fixture against it.

## 4. Display-only boundary argument (S4)

The 4326 geometry is TRANSPORT FOR DISPLAY only. The envelope stamps
`display_only=true`, `crs="EPSG:4326"`, the ±20 ft accuracy note (drawn from the
immutable `BOUNDARY_TOLERANCE_FT`), and NYC DCP attribution on EVERY outcome. The
module computes no area/dimension and imports no `shapely`
(`test_module_computes_no_area_and_does_not_import_shapely` greps the source for
`import shapely`, `compute_area`, `area_sq_ft`, `.area`). The authoritative EPSG:2263
connector remains the sole owner of measurement/digests/provenance and is byte-
unchanged: `git diff --stat a5e5e408 -- …/mappluto_geometry_arcgis.py …/config.py`
is EMPTY.

## 5. S1–S6 → test mapping

- **S1** single_lot 200: `test_s1_single_lot_200` (contract-valid, X-Correlation-ID,
  provenance incl. Version 26v2, display markers) + connector
  `test_single_lot_bbl_1008350041_details`, `test_single_lot_coordinates_are_plausible_nyc_lnglat`.
- **S2** all typed outcomes honest: `test_s2_typed_outcomes_are_honest_200`
  (parametrized 7 fixtures) + connector `test_outcome_is_typed_and_contract_valid`,
  `test_condo_billing_lot_surfaces_merged_complex_caveat`,
  `test_condo_unit_lot_is_honest_no_outline_not_error`,
  `test_multiple_features_is_review_never_first_pick`,
  `test_invalid_geometry_is_typed_outcome_not_500`.
- **S3** route posture: `test_s3_flag_off_is_generic_404_no_leak`,
  `test_s3_flag_unknown_token_is_disabled`, `test_s3_malformed_bbl_is_422_with_correlation`,
  `test_s3_get_only_post_is_405`, `test_s3_not_in_openapi` + connector URL-injection
  tests (`test_url_builder_emits_geojson_4326_and_int_where_clause`,
  `test_url_builder_refuses_non_canonical_bbl`).
- **S4** authoritative 2263 untouched + no measurement:
  `test_module_computes_no_area_and_does_not_import_shapely` + the empty git diff above.
- **S5** recorded-official fixtures: `test_fixture_bytes_match_manifest_sha256`,
  `test_synthetic_fixtures_declare_derivation_and_raw_do_not`; whole suite offline
  via the injected seam.
- **S6** contract + regression + renderer parity: `test_s6_emitted_pairs_are_in_the_matrix`,
  `test_s6_bundled_schema_is_byte_identical_to_canonical`, `_validate_contract` +
  `_assert_renderer_parity_safe` on every 200 body; both schema copies byte-identical;
  full connectors+api suites green; `modularity_check --check` exit 0.

## 6. Real command output

```
$ python -m pytest services/api/tests/connectors -q
486 passed in 2.08s
$ python -m pytest services/api/tests/api -q
417 passed in 13.94s
$ python -m pytest services/api/tests/connectors/test_mappluto_lot_outline.py services/api/tests/api/test_lot_geometry_api.py -q
67 passed in 2.60s
$ python tools/modularity_check.py --check   ; echo exit=$?
exit=0   (only pre-existing tools/* review-signal WARNINGS; my two source modules are well under limits)
$ python -m ruff check <5 new/edited source+test files>
All checks passed!
$ python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.
$ python packages/contracts/scripts/generate_ts_types.py --check
OK: property_profile / client block / rule_evaluation / scenario / survey_evidence all up to date.
$ git diff --stat a5e5e408 -- .../mappluto_geometry_arcgis.py .../config.py
(empty — forbidden paths byte-unchanged)
```

## 7. Deviations / limitations (disclosed)

1. **TS generator entrypoint not wired (out of allowed_paths).** `packages/contracts/scripts/generate_ts_types.py`
   is NOT in this packet's `allowed_paths`, so I could not add a
   `generate_lot_geometry()/check_lot_geometry()` entrypoint to it. I generated
   `lot_geometry.ts` by IMPORTING that script's own shared emission functions
   (`Resolver`, `emit_named_defs`, `object_expr`) with a `LOT_GEOM_NAMED_DEFS` map
   in the exact style of `generate_scenario()`, so the output is what a wired
   entrypoint would produce. CONSEQUENCE: the existing `generate_ts_types.py --check`
   does NOT yet drift-check `lot_geometry.ts` (it still passes for the 5 artifacts it
   knows). FOLLOW-UP (recommend a small contract-scoped task): wire the
   `lot_geometry` entrypoint + CI drift check into the generator. The generation
   script used is preserved in the session scratchpad
   (`scratchpad/gen_lot_geometry_ts.py`).
2. **`sync_contract_schemas.py` does not cover lot_geometry (out of scope).** Its
   hardcoded `SCHEMA_FILES` tuple (4 files) is not editable here, so the two
   `lot_geometry.schema.json` copies are not guarded by that CI job. I enforce
   byte-identity in-suite instead (`test_s6_bundled_schema_is_byte_identical_to_canonical`).
   Same recommended follow-up as (1).
3. **One pre-existing contracts test fails ONLY on Python 3.11 (not my code).**
   `tests/contracts/test_contract_serializers.py::test_serializer_imported_exactly_at_the_profile_write_boundary`
   `ast.parse()`s every `app/**` module; `app/documents/units.py:276` uses PEP 695
   generic syntax (`def _match_unit[UnitT: enum.Enum]`, from accepted task M2-T015)
   which Python 3.11 cannot parse. This file predates my packet (commit `561d2899`)
   and is outside my scope; the test passes on CI's Python 3.12. All 903 tests under
   my scope (connectors+api) pass on 3.11.
4. **Live-transport resilience is minimal.** `default_fetch` is a plain bounded
   urllib GET (no retry/circuit/LKG). The endpoint is internal + flag-gated and the
   whole test suite runs offline via the injected seam; wrapping the outline transport
   in `app.resilience` (as the authoritative connector does) is a reasonable follow-up.
5. **Synthetic negatives.** multiple_features and invalid_geometry cannot be
   live-captured (the real service never emits them for a valid lot), so LOT80/LOT96
   are documented `synthetic` derivations of the raw LOT01 capture — the exact
   M2-T009 fixture-pack precedent (MPG96/MPG80-88). Disclosed in the MANIFEST.

## 8. Not done here (correctly out of scope)

MapLibre GL JS dependency admission and the `apps/web` lot-outline rendering are the
follow-on packets named in the packet (this is the SERVER half). `config.py` (no new
flag) and the authoritative 2263 connector were deliberately not touched.
