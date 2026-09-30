---
name: mappluto-4326-and-contract-gen-reuse
description: MapPLUTO FeatureServer f=geojson&outSR=4326 response shape + how to add a new packages/contracts artifact when the generator script is out of allowed_paths
metadata:
  type: project
---

MapPLUTO ArcGIS lot-outline transport facts and contract-generator reuse (M5-T020, D-040-R001, 2026-09-12).

**MapPLUTO FeatureServer `f=geojson&outSR=4326`** (keyless, `services5.arcgis.com/GfwWNkhOj9bNBqoJ/.../MAPPLUTO/FeatureServer/0/query`):
- Returns a GeoJSON `FeatureCollection` with `crs:{type:name,properties:{name:"EPSG:4326"}}` and `features:[{type:Feature,id,geometry:{type:Polygon|MultiPolygon,coordinates},properties:{OBJECTID,BBL,BoroCode,Borough,Block,Lot,CondoNo,Version,Shape__Area,Shape__Length}}]`. Coordinates are `[lng,lat]` (verified Empire State 1008350041 → lng≈-73.98, lat≈40.74). Per-feature release `Version` was `"26v2"` on capture day.
- A nonexistent BBL AND a condo UNIT lot (1001-6999) both return byte-identical EMPTY FeatureCollections (`{"type":"FeatureCollection","crs":...,"features":[]}`) → distinguish by BBL/condo classification, not the body. Condo BILLING lot 7501-7599 returns the merged-complex polygon. (Same empty-body-shared-sha precedent as the 2263 MPG03/MPG05 fixtures.)
- multiple_features and null/invalid geometry cannot be live-captured (service never emits them for a real lot) → make documented `synthetic` fixtures `derived_from` a raw capture (the M2-T009 MPG96/MPG80 precedent). Never derive 4326 bytes from the 2263 fixtures.
- Reuse the byte-immutable `mappluto_geometry_arcgis.py` public discipline by IMPORT: `SERVICE_ROOT/LAYER_NAME/OUT_FIELDS/MAX_FEATURES_PER_LOT/SOURCE_ID/BOUNDARY_TOLERANCE_FT`, the private-but-authoritative `_condo_classification`, and `DisallowedRequestError`; `normalize_bbl` from `app.connectors.bbl`. Display-only: no shapely, no area from 4326 coords (2263 path owns measurement). See [[socrata-pluto-gotchas]].

**Adding a `packages/contracts` artifact when the generator script is NOT in your allowed_paths:** `packages/contracts/scripts/generate_ts_types.py` has per-artifact `generate_X()/check_X()/write_X()` + a per-artifact `X_NAMED_DEFS` map, and `main()` only `--check`s the artifacts it knows. If you can't edit it, generate your `.ts` by IMPORTING its shared emission funcs (`Resolver`, `emit_named_defs(schemas, MY_NAMED_DEFS)`, `object_expr(root, resolver, 0, MY_NAMED_DEFS)`) in the exact style of `generate_scenario()` — byte-identical to a wired entrypoint. CONSEQUENCE: your `.ts` and your two schema copies are NOT drift-checked by the existing `generate_ts_types.py --check` / `sync_contract_schemas.py --check` (both have hardcoded file lists). Enforce byte-identity of the canonical vs `app/_contract_schemas/v1/` copy in your OWN test, and flag wiring the entrypoint + CI as a follow-up. Runtime contract validation mirrors `app.scenario.contract`: load bundled schema from package `app._contract_schemas.v1` via `importlib.resources` + jsonschema `Draft202012Validator` with a `referencing` Registry.

**Env:** `tests/contracts/test_contract_serializers.py::test_serializer_imported_exactly_at_the_profile_write_boundary` FAILS on Python 3.11 (sandbox) because it `ast.parse`s every `app/**` file and `app/documents/units.py:276` uses PEP 695 generics (`def f[T]()`, needs 3.12). Pre-existing, passes on CI's 3.12. See [[m2t015-python312-and-gate-lessons]] (user auto-memory).
