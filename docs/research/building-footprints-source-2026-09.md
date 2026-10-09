# NYC Building Footprints + Heights — official source recon (M5-T087, D-087)

**Task:** M5-T087 (D-087-R003 3D existing-buildings). Source recon for a LATER connector packet and
its G1 data-contract review. **No connector code here.** Deterministic code will calculate; this note
only records what the official sources say, with exact URLs and retrieval timestamps.

**Retrieved_at (all live probes below):** 2026-09-24 UTC (single research session).
**Probe budget used:** 8 small metadata/sample requests, each ≤5 rows; nothing bulk-downloaded. Raw
responses kept in a scratch temp dir OUTSIDE any repository (not committed; thin-client policy).

**Method / honesty rules:** every field meaning, unit, datum, cadence and term below is quoted or
paraphrased from an official publisher page (NYC Open Data SODA metadata JSON, the City of New York
official metadata dictionary, or the OTI ArcGIS REST service JSON). Anything I did NOT read in an
official source is labelled **INFERENCE** or listed under "Could not verify". Nothing was taken from a
third-party blog.

---

## 0. Recommendation (one line)

Use the **NYC "BUILDING" (Building Footprints) dataset**, owner **Office of Technology and Innovation
(OTI)**, via the **OTI ArcGIS REST feature service `BUILDING_view/FeatureServer/0`** as the primary
connector channel (it can return geometry pre-reprojected to **EPSG:2263** via `outSR`, aligning with
the MapPLUTO measurement chain), with the **NYC Open Data SODA dataset `5zhs-2jue`** as the second
channel. Join footprints to a MapPLUTO lot on **`MAPPLUTO_BBL`** (DOF billing BBL); use **`BASE_BBL`**
for "physically on this tax lot". 3D extrusion: base_z = `GROUND_ELEVATION` (NAVD88 ft), roof_z =
`GROUND_ELEVATION` + `HEIGHT_ROOF` (`HEIGHT_ROOF` is height ABOVE GROUND, not above sea level).

---

## 1. Dataset identity (AS-1)

| Item | Value | Source (retrieved 2026-09-24) |
|---|---|---|
| Dataset name | **BUILDING** (a.k.a. "Building Footprints") | SODA `name`; ArcGIS layer `name` |
| Owning agency | **NYC Office of Technology and Innovation (OTI)** (formerly DOITT) | SODA `attribution` = "Office of Technology and Innovation (OTI)"; metadata custom field Agency = OTI |
| NYC Open Data id | **`5zhs-2jue`** | `https://data.cityofnewyork.us/api/views/5zhs-2jue.json` |
| SODA data endpoint | `https://data.cityofnewyork.us/resource/5zhs-2jue.json` | same |
| SODA schema/metadata | `https://data.cityofnewyork.us/api/views/5zhs-2jue.json` | same |
| OTI ArcGIS service (public) | `https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer` (layer **0**) | City metadata dictionary "Links: Building — REST service"; layer JSON `.../BUILDING_view/FeatureServer/0?f=json` |
| Official data dictionary | City of New York metadata: `https://raw.githubusercontent.com/CityOfNewYork/nyc-geo-metadata/main/Metadata/Metadata_BuildingFootprints.md` (linked from the dataset description) | SODA `description` + fetched raw |
| Companion dataset | OTI also publishes buildings as **Building Centroid Points** (`BUILDING_P_view`) — points, not footprints; not used for extrusion | City metadata dictionary "Links: Building Centroid Points" |

**Same ArcGIS org** (`services6.arcgis.com/yG5s3afENB5iO9fj`) as the DOF Digital Tax Map already in
`docs/SOURCE_ACCESS_REGISTRY.md` §11.1 — the OTI/DOF NYCMaps hub.

**Note on the State mirror:** `data.ny.gov` id `nqwf-w8eh` is a NY State Open Data mirror, NOT the
primary NYC publisher. Use the NYC OTI channels above as machine provenance.

---

## 2. Field schema — the fields the 3D use needs (AS-1)

The **authoritative field meanings** come from the City metadata dictionary (§1); the **SODA
`api/views` columns array** supplies per-column `dataTypeName`; the **ArcGIS layer JSON** supplies esri
field types. The SODA metadata leaves the height/BBL fields WITHOUT a description — meanings below are
the dictionary's, quoted.

| SODA fieldName | Shapefile/ArcGIS name | SODA type / esri type | Meaning (City dictionary, verbatim/paraphrase) | Unit | Vertical datum |
|---|---|---|---|---|---|
| `the_geom` | `SHAPE` | multipolygon / esriGeometryPolygon | "Building outline as a single outer polygon ring collected in New York Long Island State Plane and published in Web Mercator." | n/a | n/a |
| `height_roof` | `HEIGHTROOF` | number / esriFieldTypeDouble | **"The height of the roof above the ground elevation, not height above sea level."** Zero or NULL ⇒ "this information was not available." | feet (see unit note) | RELATIVE to ground (a delta; datum-independent) |
| `ground_elevation` | `GROUNDELEV` | number / esriFieldTypeInteger | **"Lowest Elevation at the building ground level. Calculated from LiDAR or photogrammetrically."** | feet (see unit note) | **NAVD88** (dictionary note: "when collected photogrammetrically or from modern sources this value is based on the North American Vertical Datum of 1988"); older/other-source values' datum unstated |
| `bin` | `BIN` | number / esriFieldTypeInteger | Building Identification Number; first digit = borough (1 MN,2 BX,3 BK,4 QN,5 SI); "million BINs" (e.g. 1000000) = unassigned/unknown. Dictionary note: **"not unique"** (BINs duplicated across split geometries). | id (coded) | n/a |
| `base_bbl` | `BASE_BBL` | text / esriFieldTypeString | "Borough, block, and lot number for the tax lot that the footprint is **physically located within**." Note: buildings occasionally associated with a lot they are not physically within (agency sync); "only numbers allowed" though text-typed. | BBL (10-digit) | n/a |
| `mappluto_bbl` | `MPLUTO_BBL` | text / esriFieldTypeString | **"Borough, block, and lot number to be used for joining the building footprints data to DCP's MapPLUTO data, which aggregates data for condominium buildings using DOF's billing BBL. For non-condominium buildings the billing BBL is the same as the BASE_BBL. For condominium buildings the billing BBL may be the same for multiple buildings on different physical tax lots if they are part of the same billing unit."** | BBL (10-digit) | n/a |
| `construction_year` | `CNSTRCT_YR` | number / esriFieldTypeInteger | "The year construction of the building was completed." Zero/NULL ⇒ not available. (Pre-2017 from DOF RPAD; post-2017 from imagery/city systems.) | year | n/a |
| `feature_code` | `FEAT_CODE` | number / esriFieldTypeSmallInteger | Type of building. Values: 1000 Parking; 1001 Gas Station Canopy; 1002 Storage Tank; 1003 Placeholder (triangle for permitted bldg); 1004 Auxiliary Structure; 1005 Temporary Structure; 1006 Cantilevered Building; **2100 Building**; 2110 Skybridge; **5100 Building Under Construction**; **5110 Garage**. | coded | n/a |
| `geom_source` | `GEOM_SOURCE` | text / esriFieldTypeString | Reference source: "Photogrammetric" (stereo-compilation, most accurate, ASPRS-conformant) vs "Other (Manual)" (heads-up digitized / plan-approximated, less accurate). | text | n/a |
| `last_edited_date` | `LSTMODDATE` | date | "Feature last modified date." | timestamp | n/a |
| `last_status_type` | `LSTSTATTYPE` | text | "Feature last status type" (Demolition, Alteration, Geometry, Initialization, Correction, Marked for Construction, Marked For Demolition, Constructed). | text | n/a |
| `doitt_id` | `DOITT_ID` | number / esriFieldTypeInteger | "Consistent unique identifier assigned by OTI (formerly DOITT)." Dictionary: use this, not OBJECTID, as the stable per-building key. | id | n/a |
| `name` | `NAME` | text | Building name; "has not been actively maintained since the original creation of this dataset." | text | n/a |
| `shape_area` / `shape_length` | `SHAPE_AREA` / `SHAPE_LEN` (also `Shape__Area`/`Shape__Length`) | number / esriFieldTypeDouble | **"Do not use.** This value is auto-generated by the system in Web Mercator which is not area/length preserving." | (do not use) | n/a |
| — | `OBJECTID` | esriFieldTypeOID | "Synthetic key populated by internal software. Use DOITT_ID instead for a consistent key." | id | n/a |

**Unit note (residual RQ-1 — see §7):** the City dictionary carries **no explicit per-field unit tag**
for `HEIGHT_ROOF` / `GROUND_ELEVATION`. **feet** is strongly supported and used here because (a) the
horizontal CRS is US foot / EPSG:2263, (b) the dictionary prose is uniformly in feet ("taller than 12
feet", "less than 60 feet tall", "±2 feet accuracy"), and (c) live sample magnitudes are foot-scale
(below). Treat "feet (US foot)" as **well-supported INFERENCE**, not an explicitly tagged field unit.

**Live value sanity check (SODA sample, 1 row, BIN 2019299, Bronx):** `ground_elevation`=197,
`height_roof`=33.49, `construction_year`=1910, `feature_code`=2100 (Building), `geom_source`=
Photogrammetric, `base_bbl`=`mappluto_bbl`=`2033800084` (non-condo ⇒ equal). Values are foot-scale and
internally consistent (a ~33 ft ~1910 building on ~197 ft NAVD88 ground). Absolute roof elevation =
197 + 33.49 = 230.49 ft NAVD88 (INFERENCE — the arithmetic the dictionary text implies, not a stored
field).

---

## 3. CRS + geometry type per channel (AS-2)

| Channel | Geometry type | CRS returned | Evidence |
|---|---|---|---|
| Source collection | polygon (single outer ring) | **EPSG:2263** (NY State Plane LI East, NAD83, US foot) | City dictionary "Horizontal Coordinate System … epsg:2263"; "collected in New York Long Island State Plane" |
| ArcGIS `BUILDING_view/FeatureServer/0` (default) | `esriGeometryPolygon` | **wkid 102100 / latestWkid 3857** (Web Mercator) | layer JSON `extent.spatialReference` |
| ArcGIS query with `outSR=2263` | `esriGeometryPolygon` | **wkid 102718 / latestWkid 2263** (US survey feet) — service reprojects on request | live probe D: returned `spatialReference {wkid:102718, latestWkid:2263}`, coords ≈ (1020200.22, 267307.25) |
| SODA `5zhs-2jue` `the_geom` | GeoJSON `MultiPolygon` | **EPSG:4326** (WGS84 lon/lat) | live sample: `the_geom.coordinates` ≈ [-73.8700, 40.9003] |
| NYC Open Data shapefile / geojson download | polygon | **EPSG:4326** | City dictionary "NYC Open Data … shapefile: 4326, geojson: 4326" |

**Load-bearing CRS finding for the connector:** NEITHER public API channel serves the original
**EPSG:2263** by default (ArcGIS default 3857, SODA 4326). The MapPLUTO measurement connector
(`mappluto_geometry_arcgis.py`) requires `EXPECTED_WKID=102718 / EXPECTED_LATEST_WKID=2263` and refuses
any other CRS. Two alignment options: (1) **request `outSR=2263` from the ArcGIS service** (verified
working — probe D), so footprints arrive in the same projected-feet CRS; or (2) reproject 4326/3857 →
2263 in-process. Both reproject FROM a Web-Mercator/WGS84 publication, so coordinates carry the
publication transform, not the original 2263 precision — acceptable for **3D display/massing**, but
recompute area in 2263 and treat as display-grade (see §6 quality limits). Matches the DTM note in
`SOURCE_ACCESS_REGISTRY.md` §11.1 (that channel is 3857, "validate/reproject before overlay").

---

## 4. Access channels + limits (AS-2)

**Channel A — OTI ArcGIS REST (recommended primary).**
- Endpoint: `https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0/query`
- Auth: none (anonymous HTTP 200 verified live on all probes; keyless — no credential to leak).
- Layer JSON facts (live): `objectIdField=OBJECTID`, `maxRecordCount=2000`, `supportsPagination=true`,
  `supportsStatistics=true`, `geometryType=esriGeometryPolygon`, `capabilities=Query,Extract`,
  `currentVersion=12`. **CAP HAZARD:** `maxRecordCount=2000`; the neighbours probe returned
  `exceededTransferLimit=true` at only 5 rows requested — **deterministic paging (`resultOffset`/
  `resultRecordCount` with `orderByFields`) is mandatory** on any area query, exactly like the M2-T009
  MapPLUTO connector.
- Rate limits: none published numerically (same as the DTM ArcGIS channel §11.1; expect an
  `x-esri-org-request-units-per-min` header — **to re-verify at connector G1**).
- Freshness signal: `editingInfo.dataLastEditDate` (live = 2026-09-20T02:16:01Z);
  `schemaLastEditDate` = 2025-10-10T16:10:42Z.

**Channel B — NYC Open Data SODA `5zhs-2jue`.**
- Endpoints: data `…/resource/5zhs-2jue.json`, schema `…/api/views/5zhs-2jue.json`.
- Socrata platform baseline (per `SOURCE_ACCESS_REGISTRY.md` governance rule 5): auth optional
  (`X-App-Token`), no numeric published quota, 429 throttle signal, SODA omits null fields per record —
  schema comes from the `api/views` columns array, never from record keys.
- Geometry returned in EPSG:4326 (reproject to 2263 before any overlay with the DCP chain).
- Freshness signal: `rowsUpdatedAt` (live = 2026-09-21T06:40:23Z).

**Channel C — bulk download (deferred, human-gated).**
- NYCMaps hub `https://nycmaps-nyc.hub.arcgis.com/datasets/nyc::building/about` and NYC Open Data export
  (shapefile/geojson/FileGDB). Exact download URLs behind the hub/nyc.gov are **to verify at G1 via a
  human browser session** (the `www.nyc.gov`/portal bot-wall convention in the registry's cross-source
  notes; never guessed). Citywide bulk import is a future cloud-worker task (thin-client policy — never
  on the owner PC), not needed for the per-lot 3D use.

### Request shapes (all verified live, ≤5 rows)

1. **Footprints physically on ONE tax lot** (ArcGIS attribute):
   `where=BASE_BBL='<10-digit-bbl>'&outFields=BIN,BASE_BBL,MAPPLUTO_BBL,HEIGHT_ROOF,GROUND_ELEVATION,CONSTRUCTION_YEAR,FEATURE_CODE,GEOM_SOURCE&returnGeometry=true&outSR=2263&f=json`
   (SODA equivalent: `?$where=base_bbl='<bbl>'`).
2. **Footprints for a MapPLUTO lot incl. condo aggregation** (ArcGIS attribute): same but
   `where=MAPPLUTO_BBL='<billing-bbl>'`. Probe B returned 1 feature for `MAPPLUTO_BBL='2033800084'`.
3. **One BBL PLUS its neighbours** (ArcGIS spatial envelope — the robust "neighbours" shape):
   `geometry={"xmin":..,"ymin":..,"xmax":..,"ymax":..,"spatialReference":{"wkid":4326}}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=...&returnGeometry=true&outSR=2263&f=json`.
   Probe C over a ~250 ft box returned 5 footprints across **five different BASE_BBLs**
   (2033790028, 2033800086, 2033730020, 2033800015, 2033790098) with `exceededTransferLimit=true` —
   i.e. it captures the subject lot's footprints and the surrounding lots' footprints in one call.
   For a precise neighbour set, pass the **subject lot polygon** (from MapPLUTO, buffered a few feet)
   as the `geometry` with `spatialRel=esriSpatialRelIntersects` instead of a bbox. Paging mandatory.

---

## 5. Join rule to MapPLUTO (AS-2) — settled

**Rule:** to attach footprints to a MapPLUTO tax-lot polygon, join **`MAPPLUTO_BBL` (footprints) →
`BBL` (MapPLUTO)**. The dictionary states `MAPPLUTO_BBL` is exactly "the … number to be used for
joining … to DCP's MapPLUTO data, which aggregates … condominium buildings using DOF's billing BBL."

- **Non-condominium:** `MAPPLUTO_BBL == BASE_BBL` (dictionary; confirmed by the non-condo sample where
  both = `2033800084`).
- **Condominium:** `MAPPLUTO_BBL` = the DOF **billing BBL**; multiple physical buildings on different
  `BASE_BBL`s can share one `MAPPLUTO_BBL`. **Empirically confirmed** (SODA probe A, condo mismatches):
  `BASE_BBL 5070380001 → MAPPLUTO_BBL 5070387501`; `5023800455 → 5023807502`;
  `4068150020 → 4068157501`; `4039160255 → 4039167504`. Every billing lot lands in **7501–7599** —
  exactly the `CONDO_BILLING_LOT_MIN/MAX` (7501/7599) the MapPLUTO connector already encodes, and
  MapPLUTO carries the polygon ONLY on the billing lot (unit lots 1001–6999 have no polygon). So
  `MAPPLUTO_BBL` is the correct and only reliable key to reach a condo's MapPLUTO geometry.
- **`BASE_BBL`** answers a different question ("which tax lot is this footprint physically on") and is
  the right key for the address-lot's own buildings; but for the geometry join (and for condos) use
  `MAPPLUTO_BBL`. Caveat from the dictionary: a footprint may sit on a lot it is not physically within
  (agency sync); surface such disagreements, never silently trust.
- **Keys are text, digits-only, 10-digit** BBL (borough+block+lot), matching `normalize_bbl`
  conventions; `BIN` is the per-building key but **not unique** (million-BINs + split-geometry
  duplication) — use `DOITT_ID` as the stable per-footprint identity.

---

## 6. Cadence, licence, known quality limits (AS-3)

**Update cadence / last-updated.**
- City dictionary Publication Dates: **"Last Update: Weekly"**, metadata dated **10/09/2025**, and
  "Features are updated daily by OTI staff and released publicly on NYC Open Data and NYCMaps."
- SODA custom fields: **Update Frequency = Weekly**, Automation = No, Date Made Public = 5/3/2016.
- Observed freshness (live 2026-09-24): SODA `rowsUpdatedAt` = **2026-09-21T06:40:23Z**; ArcGIS
  `dataLastEditDate` = **2026-09-20T02:16:01Z** — both within days of research; actively maintained.
- **Ambiguity (record honestly):** the dictionary says both "Weekly" (public release) and "daily"
  (internal edits); the Socrata custom field says Weekly. Record cadence as **weekly public release of
  daily internal edits**; stamp the observed `rowsUpdatedAt`/`dataLastEditDate` per fetch, never a
  contract (governance rule 2).

**Licence / terms.**
- SODA `license` = **none set** (no license object; `licenseId` null). Governing terms are the **NYC
  Open Data Terms of Use** (`https://opendata.cityofnewyork.us/overview/#termsofuse`), which the City
  dictionary names under "Use Limitations". Access Rights = **Public**. No permanence/pricing/SLA is
  promised (governance rule 2). No prohibition on automated API access on the Socrata/ArcGIS channels.
- Provenance tier: official City agency data (OTI) — controlling machine provenance, unlike ZoLa/UpCodes
  presentation/third-party layers.

**Known quality limits (load-bearing for 3D).**
1. **Missing heights:** `HEIGHT_ROOF` = 0 or NULL means "not available" (historically left zero/NULL
   when no source). A connector must treat 0/NULL as UNKNOWN height, never extrude a zero-height box —
   surface "height unknown", never fabricate.
2. **Capture threshold / completeness:** captured = "All buildings >400 sq. feet and taller than 12
   feet" plus others with BINs. Small/short structures are excluded — the footprint set is not every
   physical structure.
3. **Placeholder geometry:** where no visual/plan info exists, OTI inserts a small triangle with
   `FEATURE_CODE = 1003 (Placeholder)`. Filter these (and choose which FEAT_CODEs to render, e.g. keep
   2100 Building / 5100 Under Construction / 5110 Garage) before 3D extrusion.
4. **`SHAPE_AREA` / `SHAPE_LENGTH` = "Do not use"** (auto-generated in Web Mercator; not
   area/length-preserving). Recompute area in EPSG:2263 if needed.
5. **Positional accuracy:** photogrammetric features (`GEOM_SOURCE=Photogrammetric`) ≈ **±2 ft**
   (ASPRS Class 1 horizontal / Class 2 vertical); "Other (Manual)" features are less accurate. Height
   from Cyclomedia direct measurement only for buildings **< 60 ft** tall.
6. **`BIN` not unique / million-BINs:** dummy BINs (1000000, 2000000, …) mark unknown/unassigned;
   split geometries duplicate a BIN. Use `DOITT_ID` for per-footprint identity.
7. **`BASE_BBL` occasionally off-lot** (agency sync); a footprint's BBL may not be the lot it sits on.
8. **CRS mismatch** with the DCP chain (see §3): default channels are 3857/4326, not 2263.

---

## 7. Could NOT verify / residuals (honest gaps)

- **RQ-1 explicit height unit tag:** no per-field "units: feet" tag exists in the City dictionary or
  SODA metadata for `HEIGHT_ROOF`/`GROUND_ELEVATION`. "feet (US foot)" is well-supported INFERENCE
  (US-foot CRS + foot-based prose + foot-scale samples), not an explicitly tagged unit. Resolve at
  connector G1 (e.g., confirm against the NYCMaps hub item page or an OTI planimetrics spec).
- **RQ-2 vertical datum coverage:** NAVD88 is stated for `GROUND_ELEVATION` "when collected
  photogrammetrically or from modern sources"; the datum of older/other-source values is not stated.
  `HEIGHT_ROOF` is a relative delta (above ground), so datum-independent, but depends on the same
  ground reference.
- **RQ-3 SODA sync semantics:** whether `5zhs-2jue` is a live mirror of the ArcGIS service or a
  periodic snapshot is not documented; observed `rowsUpdatedAt` (SODA) and `dataLastEditDate` (ArcGIS)
  differ by ~1 day. Prefer the ArcGIS channel for freshest edits + `outSR=2263`; treat SODA as the
  secondary/verification channel.
- **RQ-4 ArcGIS rate-limit header:** not captured this session (no `-i`); expect
  `x-esri-org-request-units-per-min` like the DTM channel — capture at connector G1.
- **RQ-5 bulk download URLs:** exact NYCMaps-hub / nyc.gov FileGDB-shapefile URLs are behind the
  hub/bot-wall — **to verify at G1 via a human browser session**, never guessed (registry cross-source
  note). Not needed for the per-lot 3D use.
- **RQ-6 `GLOBALID`:** the City dictionary lists a `GLOBALID` UUID "not published in all datasets"; it
  is ABSENT from both the SODA `5zhs-2jue` columns and the ArcGIS `BUILDING_view/0` fields observed —
  so this channel has no GLOBALID; use `DOITT_ID`.

---

## 8. Provenance — raw responses captured (scratch, not committed)

All fetched live 2026-09-24 UTC; HTTP 200 on every request; stored in the session scratch temp dir
outside any repository (thin-client policy — not committed). Reproduce with the URLs/params below.

| # | What | URL / params |
|---|---|---|
| views | SODA metadata (schema, agency, cadence, freshness) | `GET https://data.cityofnewyork.us/api/views/5zhs-2jue.json` |
| meta | City official dictionary | `GET https://raw.githubusercontent.com/CityOfNewYork/nyc-geo-metadata/main/Metadata/Metadata_BuildingFootprints.md` |
| layer0 | ArcGIS layer JSON (maxRecordCount, paging, SR, fields, editingInfo) | `GET https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0?f=json` |
| sample1 | SODA 1-row sample (field values, 4326 geometry) | `GET …/resource/5zhs-2jue.json?$limit=1` |
| condo | SODA condo-mismatch (join proof) | `GET …/resource/5zhs-2jue.json?$select=base_bbl,mappluto_bbl,bin,feature_code&$where=mappluto_bbl != base_bbl&$limit=4` |
| attr | ArcGIS attribute join (one MAPPLUTO_BBL) | `…/BUILDING_view/FeatureServer/0/query?where=MAPPLUTO_BBL='2033800084'&outFields=…&returnGeometry=false&resultRecordCount=5&f=json` |
| envelope | ArcGIS spatial neighbours (envelope intersects) | `…/query?geometry={bbox 4326}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&resultRecordCount=5&f=json` |
| outSR | ArcGIS `outSR=2263` alignment proof | `…/query?where=BIN=2019299&returnGeometry=true&outSR=2263&resultRecordCount=1&f=json` → SR wkid 102718/2263 |

## 9. Proposed contract-test pack (for the future connector's G1)

Deterministic, offline, fixture-driven (mirror the M2-T009 MapPLUTO connector pattern):
- **Schema pin:** cross-check a pinned field inventory (names + esri/SODA types from layer0/views) — any
  add/remove/retype = `schema_drift`, never guessed around.
- **CRS gate:** refuse any SR != wkid 102718/2263 for measurement; assert `outSR=2263` fixture returns
  102718/2263; assert SODA geometry is 4326 and is reprojected before overlay.
- **Height semantics:** `HEIGHT_ROOF` 0/NULL ⇒ typed "height_unknown" (never a zero box); roof_z =
  `GROUND_ELEVATION` + `HEIGHT_ROOF`; both stamped unit=feet, `GROUND_ELEVATION` datum=NAVD88(+caveat).
- **FEAT_CODE filter:** placeholder (1003) and chosen non-render codes excluded/flagged.
- **Join tests:** non-condo `MAPPLUTO_BBL==BASE_BBL`; condo `MAPPLUTO_BBL` in 7501–7599 and equal for
  multiple `BASE_BBL`s (fixture from probe A); join to MapPLUTO uses `MAPPLUTO_BBL`.
- **Paging:** `maxRecordCount=2000` + `exceededTransferLimit` ⇒ mandatory deterministic paging;
  neighbours envelope fixture asserts multi-BBL result.
- **Provenance:** stamp source id, dataset id (`5zhs-2jue` / ArcGIS service), request URL, retrieved_at,
  `dataLastEditDate`/`rowsUpdatedAt`, raw-body digest; two-staleness rule (source vs transport).
- **Failure taxonomy:** ArcGIS error-object-with-HTTP-200, 429, timeout, malformed body, wrong SR,
  off-lot BASE_BBL disagreement surfaced (not silently trusted).

---

*Recon only. No connector code, no legal interpretation. Field meanings quoted from the City of New
York official metadata dictionary and OTI service/Socrata metadata; inferences labelled; residuals
listed for connector G1.*
