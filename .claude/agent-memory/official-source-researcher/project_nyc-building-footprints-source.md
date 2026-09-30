---
name: nyc-building-footprints-source
description: Official NYC building footprints + heights source — dataset id, height/datum semantics, MapPLUTO join key, CRS per channel
metadata:
  type: project
---

NYC existing-building footprints WITH heights = NYC Open Data dataset **`5zhs-2jue`**
("BUILDING"), owner **OTI** (formerly DOITT). Verified live 2026-09-24 for M5-T087 (D-087
3D existing buildings). Companion OTI ArcGIS service:
`services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0`
(same org as the DOF Digital Tax Map §11.1). Authoritative dictionary =
`CityOfNewYork/nyc-geo-metadata/Metadata/Metadata_BuildingFootprints.md` (SODA metadata has
NO description for the height/BBL fields).

**Why:** never guess field meaning/unit/datum before a connector; these are the settled facts.

**How to apply (key facts, all cited in `docs/research/building-footprints-source-2026-09.md`):**
- `HEIGHT_ROOF`/`HEIGHTROOF` = roof height ABOVE GROUND, NOT above sea level; 0/NULL = unknown
  (never extrude a zero box). `GROUND_ELEVATION`/`GROUNDELEV` = lowest ground-level elevation,
  **NAVD88** (modern captures). roof_z = ground + roof. Unit = feet is INFERENCE (US-foot CRS +
  foot prose; no explicit per-field unit tag — residual RQ-1).
- **Join to MapPLUTO on `MAPPLUTO_BBL` (DOF billing BBL)**, not `BASE_BBL`. `BASE_BBL` = physical
  tax lot. Condo: MAPPLUTO_BBL lands in **7501-7599** (confirmed live) and MapPLUTO holds the
  polygon only there — matches [[in-regime-accept-mechanics]] MapPLUTO connector CONDO_BILLING_LOT.
  `BIN` is not unique (million-BINs + split dup); use `DOITT_ID` for per-footprint identity.
- **CRS per channel:** source 2263; ArcGIS default 3857; SODA `the_geom` 4326. Neither API serves
  2263 by default — but **ArcGIS `outSR=2263` works** (verified) → aligns to the MapPLUTO 2263
  measurement chain. `SHAPE_AREA`/`SHAPE_LENGTH` = "Do not use" (Web-Mercator, not preserving).
- ArcGIS layer: `maxRecordCount=2000`, paging mandatory (envelope query tripped
  exceededTransferLimit at 5 rows); geometryType polygon; keyless. Neighbours = spatial
  `esriGeometryEnvelope`/lot-polygon `spatialRel=esriSpatialRelIntersects`.
- Cadence: weekly public release of daily OTI edits; licence = NYC Open Data Terms (SODA license
  none set). Capture threshold: buildings >400 sq ft AND >12 ft; placeholders `FEATURE_CODE=1003`.
- FEAT_CODE: 2100 Building, 5100 Under Construction, 5110 Garage, 2110 Skybridge, 1003 Placeholder.
