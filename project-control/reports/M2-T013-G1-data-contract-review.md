<!-- Preserved VERBATIM by the orchestrator from the data-contract-verifier agent return, 2026-07-21 (transport entity-decoding only: &gt; &lt; &amp; decoded). -->

Independent verification complete. The one load-bearing `documented` figure is corroborated by current official DCP material ("estimated horizontal accuracy of +/- 20 feet"; "not intended for determining zoning at the individual tax lot level"), matching the connector's cited nyzd metadata and the ZTLDB-as-lot-authority design.

---

# G1 Gate Report — M2-T013 Spatial-Intersection Engine

**Gate:** G1 (source & data-contract) · **Task:** M2-T013 · **Review SHA:** 59dbe65 (branch task/M2-T013-spatial) · **Reviewer:** data-contract-verifier (independent; did not implement) · **Date:** 2026-07-21

**VERDICT: PASS**

## Method
Read policy.py, adapter.py, models.py, plus engine.py/geometry.py/crosscheck.py to confirm connector consumption and null semantics; cross-read the three consumed connectors (mappluto_geometry_arcgis.py, zoning_features_arcgis.py, ztldb_soda.py) read-only for field shapes; verified V1/V2 evidence vs advisory §2.1; independently ran ruff + pytest + git diff and corroborated the nyzd accuracy figure against live official DCP material.

## G1 checklist results

1. **Field mapping — CONFIRMED, no invented fields.**
   - Lot: `adapter.lot_input_from_result` reads `geometry.canonical_geometry` / `geometry.status` (GeometryAssessment fields exist) and maps `LotGeometryResult.outcome` (`single_feature`/`no_feature`/`multiple_features`) correctly.
   - Districts: `_LAYER_LABEL_FIELDS` (nyzd=ZONEDIST, nyco=OVERLAY, nysp=SDLBL/SDNAME, nysp_sd=SUBDIST_LBL/SUBDIST/SPLBL/SPNAME, nylh=LHLBL/LHNAME, nyzma=ULURPNO/STATUS/PROJECT_NAME) — every field exists in the connector's `LAYER_SPECS`. Falls back to `layer:oid` when label absent.
   - ZTLDB: adapter passes `zoning_assignment` through unmodified; `crosscheck` reads `zoning_districts` list `{position,value}` in position order (position 1 = `zoning_district_1` = greatest area per connector line 300) and filters blank `value` (correct "not divided" semantics). Vintage from `source_freshness["rows_updated_at"]` via `SourceFreshness.to_dict()`=`asdict` — key exists.

2. **Units/CRS — CONFIRMED, no degrees path.** District esri geometries canonicalized via the accepted `analyze_lot_geometry(..., crs=dict(CRS_STAMP))` (EPSG:2263 US survey feet); lot arrives pre-canonicalized; engine converts both through `canonical_to_shapely`. Band erode/dilate = `shape.buffer(-/+band_ft)` in feet, areas planar (`.area` on 2263). `assert_geometry_pins` fails closed unless shapely==2.0.7 / GEOS 3.11.4.

3. **Accuracy provenance (V1/V2) — CONFIRMED, honest, matches advisory §2.1 exactly.** nyzd = `documented` +/-20 ft with a real citation (nyzd_metadata.pdf Data Quality section, research line 149, G1-confirmed); nyco/nysp/nysp_sd/nylh/nyzma and MapPLUTO lot = `assumed` +/-20 ft. V1 (MapPLUTO metadata publishes NO positional-accuracy figure) and V2 (nysp per-layer PDF has none extractable; other mirrors 403) are recorded honestly, not guessed, and kept `assumed` (fail-safe direction via the 2x-band sensitivity trigger). Spot-check: the single `documented` basis is nyzd and it carries a citation; unknown-layer fallback returns `assumed`. `SourceAccuracy.__post_init__` enforces basis∈{documented,assumed} and value>0.

4. **No contract/schema change — CONFIRMED.** `git diff --name-only origin/main...HEAD`: zero edits under packages/contracts/**, services/api/app/_contract_schemas/**, services/api/app/profile/**, or services/api/app/connectors/**. Changes are confined to app/spatial/**, tests/spatial/**, docs/research/**, and orchestrator-owned project-control ledger artifacts. models.py is engine-internal dataclasses (docstring states it must not define/mutate a contract).

5. **Null/absent semantics — CONFIRMED, typed, never fabricated.** Lot canonical None / review_required / non-intersectable status → `_invalid_lot_record` (LOT_INVALID_GEOMETRY_REVIEW, professional_review_required, no assignment). Absent ZTLDB (`no_record`/no districts) → XCHK_ZTLDB_ABSENT, display_upgrade "none", geometry-only capped at conditional-in-review. Invalid district geometry is recorded and routed to review, never dropped.

6. **Provenance persistence — CONFIRMED.** Every pair stamps lot/district `accuracy` (`as_dict`), `band_ft`, `combination_rule`, `feature_ref` (layer/object_id/source_normalized_digest/retrieved_at). Record stamps `accuracy_records` (all distinct inputs), `policy` (policy_snapshot incl. POLICY_VERSION="M2-T013-spatial-policy-1"), and `provenance` incl. shapely/GEOS versions + lot digests.

## Executable evidence (independently run)
- `shapely 2.0.7 / geos 3.11.4` (matches pins)
- `python -m ruff check app/spatial` → **All checks passed!** (0 findings)
- `python -m pytest tests/spatial -q` → **26 passed in 0.58s**
- `grep -i verified app/spatial` → only docstrings ("NOT a Verified determination") and the `verified_at` provenance timestamp; **no code path emits a Verified label/coverage status** (SI-CF5/SI-S9 hold).
- Official cross-check: DCP GIS Zoning Features metadata states "estimated horizontal accuracy of +/- 20 feet" and "not intended for determining zoning at the individual tax lot level" — corroborates the nyzd `documented` figure and the ZTLDB-as-primary-lot-authority design.

## Blocking findings
None.

## Non-blocking observations (not G1 defects)
- Producer identity: packet `producer_agent`=orchestrator and the V1/V2 metadata verification was performed by the lead session, under an owner-authorized 2026-07-21 sequencing exception. Producer↔reviewer independence is a G3/G4 concern, not G1; flagged only so the orchestrator preserves independence at the downstream gates.
- V1/V2 prove a negative (officials publish no figure) that cannot be exhaustively closed in-task; the `assumed` basis + 2x-band fail-safe is the correct conservative resolution and an eventual per-source `documented` upgrade would only reduce review triggers.

## Relevant paths
- `...\.claude\worktrees\M2-T013-spatial\services\api\app\spatial\{policy,adapter,models,engine,geometry,crosscheck}.py`
- `...\.claude\worktrees\M2-T013-spatial\docs\research\M2-T013-accuracy-verification.md`
- `...\.claude\worktrees\M2-T013-spatial\project-control\reports\M2-T013-geospatial-policy-advisory.md` (§2.1)

Sources:
- [NYC GIS Zoning Features (DCP resource)](https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features)
- [Zoning Districts (NYZD) metadata PDF](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf)
- [NYC GIS Zoning Features (open-data download page)](https://www.nyc.gov/site/planning/data-maps/open-data/dwn-gis-zoning.page)
