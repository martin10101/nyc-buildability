# M5-T087 producer report — official building-footprint + height source research (D-087)

**Task:** M5-T087 (research, docs-only). **Producer:** official-source-researcher.
**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t087` (branch `task/M5-T087-footprints-research`).
**Contract head verified:** `git rev-parse HEAD` = `46cc1e6a258024ae8ce023ce17af97538d85b398` on
`task/M5-T087-footprints-research` (checked before work; matches dispatch).
**Deliverable:** `docs/research/building-footprints-source-2026-09.md` (placeholder replaced) + this report.
**Evidence-status legend:** [OBSERVED] = read from a live official response this session (2026-09-24 UTC);
[INFERENCE] = derived, labelled; [BLOCKED] = could not verify, routed to G1.

## What was researched (one evidence pass)

Primary source identified and settled: the **NYC "BUILDING" (Building Footprints) dataset**, owner
**OTI**, NYC Open Data id **`5zhs-2jue`**, plus its OTI ArcGIS REST service
`BUILDING_view/FeatureServer/0` and the City of New York official metadata dictionary
(`nyc-geo-metadata/Metadata/Metadata_BuildingFootprints.md`). All field meanings, units, datum, CRS,
access limits, cadence, licence and quality limits are recorded in the note with exact URLs +
retrieved_at 2026-09-24.

Commands run (explicit cwd = scratch temp dir OUTSIDE any repo:
`…/scratchpad/m5t087`), each HTTP 200, each ≤5 rows:
- [OBSERVED] `GET https://data.cityofnewyork.us/api/views/5zhs-2jue.json` → name=BUILDING,
  attribution=OTI, id=5zhs-2jue, rowsUpdatedAt=2026-09-21T06:40:23Z, license=none, 16 columns.
- [OBSERVED] `GET https://raw.githubusercontent.com/CityOfNewYork/nyc-geo-metadata/main/Metadata/Metadata_BuildingFootprints.md`
  → authoritative field dictionary (heights, datum, BBL join, FEAT_CODE list, cadence, terms, accuracy).
- [OBSERVED] `GET …/BUILDING_view/FeatureServer/0?f=json` → geometryType=esriGeometryPolygon,
  maxRecordCount=2000, supportsPagination=true, SR wkid 102100/3857, dataLastEditDate=2026-09-20,
  15 fields with esri types, capabilities=Query,Extract.
- [OBSERVED] SODA 1-row sample → the_geom in EPSG:4326; ground_elevation=197, height_roof=33.49,
  feature_code=2100, base_bbl==mappluto_bbl==2033800084 (non-condo equality).
- [OBSERVED] SODA condo-mismatch (`$where=mappluto_bbl != base_bbl`, 4 rows) → every mismatch maps
  BASE_BBL → MAPPLUTO_BBL in the **7501–7599** billing-lot range (5070380001→5070387501, etc.).
- [OBSERVED] ArcGIS attribute query `where=MAPPLUTO_BBL='2033800084'` → 1 feature (join shape works).
- [OBSERVED] ArcGIS spatial envelope (`esriGeometryEnvelope`, `spatialRel=Intersects`, inSR=4326) →
  5 footprints across 5 different BASE_BBLs, `exceededTransferLimit=true` (neighbours shape works;
  paging mandatory).
- [OBSERVED] ArcGIS query `outSR=2263` → geometry returned in wkid 102718/latestWkid 2263, coords
  ≈ (1020200.22, 267307.25) US survey feet (clean alignment to the MapPLUTO measurement chain).

Raw responses stored in the scratch temp dir only (not committed; thin-client policy).

## Per-acceptance-scenario evidence

- **AS-1 (identity + schema):** PASS. Dataset id `5zhs-2jue`, owner OTI; every 3D-needed field
  (`the_geom`, `HEIGHT_ROOF`, `GROUND_ELEVATION`, `BIN`, `BASE_BBL`, `MAPPLUTO_BBL`, `CONSTRUCTION_YEAR`,
  `FEATURE_CODE`, `GEOM_SOURCE`, `DOITT_ID`) with official meaning, type, unit and datum in note §2,
  each cited to an official URL + retrieved_at 2026-09-24. Height semantics settled: `HEIGHT_ROOF` =
  "height of the roof above the ground elevation, not height above sea level" [OBSERVED, dictionary];
  `GROUND_ELEVATION` = "Lowest Elevation at the building ground level … based on NAVD88" [OBSERVED];
  ground elevation is NOT included in HEIGHT_ROOF (roof_z = ground + roof). Unit=feet is [INFERENCE]
  (RQ-1, note §7) since no explicit per-field unit tag is published.
- **AS-2 (access + join):** PASS. Channels (ArcGIS primary, SODA secondary, bulk deferred) with limits
  in note §4; three verified request shapes incl. **one BBL + neighbours** (spatial envelope, probe C);
  CRS + geometry type per channel in §3; join rule settled in §5 — join on `MAPPLUTO_BBL` (DOF billing
  BBL) to MapPLUTO, `BASE_BBL` for physical lot, condo aggregation [OBSERVED] via probe A landing in
  7501–7599 (matches the MapPLUTO connector's CONDO_BILLING_LOT range).
- **AS-3 (limits + cadence):** PASS. Cadence = weekly public release of daily internal edits
  [OBSERVED, dictionary + SODA custom fields], last-updated `rowsUpdatedAt` 2026-09-21 /
  `dataLastEditDate` 2026-09-20 [OBSERVED]; licence = NYC Open Data Terms of Use (SODA license none set)
  [OBSERVED]; known quality limits (missing/zero heights, >400 sq ft & >12 ft capture threshold,
  placeholder triangles FEAT_CODE 1003, SHAPE_AREA "do not use", ±2 ft accuracy, BIN non-unique,
  off-lot BASE_BBL, CRS mismatch) in §6; inferences/gaps labelled in §7.
- **AS-4 (scope):** PASS. Docs only; exactly the two allowed_paths changed (see below). No connector
  code, no ledger/git-authority actions, no edits outside the worktree.

## Recommended dataset + key fields (summary table)

| Field (SODA / shapefile) | Meaning | Unit | Datum | Source URL |
|---|---|---|---|---|
| `height_roof` / `HEIGHTROOF` | roof height ABOVE GROUND (not sea level) | feet [INF] | relative to ground | City dictionary (§1 note) |
| `ground_elevation` / `GROUNDELEV` | lowest ground-level elevation | feet [INF] | NAVD88 (modern captures) | City dictionary |
| `bin` / `BIN` | building id (borough-coded; not unique) | id | — | City dictionary + SODA |
| `base_bbl` / `BASE_BBL` | tax lot the footprint is physically on | 10-digit BBL | — | City dictionary + SODA |
| `mappluto_bbl` / `MPLUTO_BBL` | **DOF billing BBL — join key to MapPLUTO** | 10-digit BBL | — | City dictionary + probe A |
| `construction_year` / `CNSTRCT_YR` | year completed (0/NULL=unknown) | year | — | City dictionary |
| `feature_code` / `FEAT_CODE` | building type (2100 Building, 1003 Placeholder, …) | coded | — | City dictionary |
| `the_geom` / `SHAPE` | footprint polygon | — | 2263 source; 3857 ArcGIS / 4326 SODA | City dictionary + probes |

**Join rule:** footprints `MAPPLUTO_BBL` → MapPLUTO `BBL` (billing BBL; condos aggregate to 7501–7599
where MapPLUTO holds the only polygon). Use `BASE_BBL` for physical-lot membership. Neighbours: ArcGIS
spatial `esriGeometryEnvelope`/lot-polygon `spatialRel=esriSpatialRelIntersects`, `outSR=2263`, paged.

## Gaps / could not verify (honest)

RQ-1 no explicit height unit tag (feet is inference); RQ-2 NAVD88 stated for modern captures only;
RQ-3 SODA-vs-ArcGIS sync semantics undocumented (~1 day skew); RQ-4 ArcGIS rate-limit header not
captured this session; RQ-5 bulk FileGDB/shapefile download URLs behind the NYCMaps hub / bot-wall —
[BLOCKED] to verify at G1 via a human browser session, never guessed; RQ-6 no `GLOBALID` on this
channel (use `DOITT_ID`). All routed to the connector's G1. No connector was written; no legal
interpretation made.

## Scope / files changed

- `docs/research/building-footprints-source-2026-09.md` (placeholder replaced)
- `project-control/reports/M5-T087-producer-report.md` (this file)

`git status` shows only these two files. One commit in the worktree:
"M5-T087 unit (D-087 building-footprint source research)".

## DISCOVERIES (D-069 — orchestrator records at the seam; not fixed in-packet)

- The OTI Building Footprints ArcGIS service shares the org (`services6.arcgis.com/yG5s3afENB5iO9fj`)
  and the 3857-default CRS with the DOF Digital Tax Map already in `SOURCE_ACCESS_REGISTRY.md` §11.1 —
  a candidate shared ArcGIS-org transport note. WATCH.
- Building Footprints is a candidate new registry section (§12) once the connector lands; not added
  here (registry is outside allowed_paths).

END-OF-REPORT
