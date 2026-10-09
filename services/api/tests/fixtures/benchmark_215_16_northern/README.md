# Benchmark lot 215-16 Northern Blvd, Queens — recorded official data (B-01)

BBL **4073340070** (borough 4, block 7334, lot 70). Queue item B-01 (Lane B; plan IDs M1-20, C-3, C-7,
C-8, C-9; directive D-090, owner GO D-090-R015). Benchmark: competitor review section A,
`docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`.

- **Capture:** 29 official responses on 2026-09-30 between 06:08 and 06:23 UTC. Python `urllib`
  GET, keyless, one request per file, sequential, at least 2.5 s apart. Each body is stored
  byte-for-byte as returned.
- **Provenance:** `MANIFEST.json` lists, for each file, the dataset, source id, exact URL,
  `retrieved_at` (UTC), HTTP `Date` and `Last-Modified`, status (all 200), byte count and sha256.
  `capture_notes` lists the 503 and timeout attempts, which were retried; none of those bodies
  is stored.
- **Query shapes:** each connector-backed URL comes from that connector's own URL builder
  (`MANIFEST.json` field `connector`), so replaying these files runs the real code path. DOB and
  ACRIS have no connector. Their URLs follow the documented shapes (field `documented_in`),
  with a `$select` that leaves out personal-name columns.
- **Integrity:** `services/api/tests/connectors/test_benchmark_215_16_northern_fixtures.py`
  re-hashes every file and rebuilds every connector URL. `.gitattributes` (`-text`) keeps the
  bytes exact. The two ArcGIS count bodies end in CRLF as served.

## Data versions at capture (C-7)

| Source | Version / freshness recorded |
|---|---|
| PLUTO `64uk-42ks` | row `version` = **26v2**; HTTP Last-Modified 2026-08-24T20:20:51Z |
| MapPLUTO (DCP_GIS `MAPPLUTO`) | feature `Version` = **26v2**; layer `dataLastEditDate` 2026-09-09T15:30:24Z |
| ZTLDB `fdkv-4t4z` | `rowsUpdatedAt` 2026-04-05T18:46:56Z. The ZTLDB connector's freshness check flags it as older than its 45-day threshold (177.5 days when replayed) |
| Zoning features `nyzd` / `nyco` | `dataLastEditDate` 2026-08-17T18:14:20Z / 2026-08-17T18:16:28Z |
| DOF Digital Tax Map | layer `dataLastEditDate` 2026-09-29T08:18:20Z; the lot feature's `EFFECTIVE_TAX_YEAR` = "2017-2018" |
| DCM street center line | `dataLastEditDate` 2025-12-01T19:39:55Z |
| Building footprints `5zhs-2jue` | `dataLastEditDate` 2026-09-27T02:17:02Z |
| DOB / ACRIS SODA datasets | HTTP Last-Modified per file in `MANIFEST.json` (for example `ic3t-wcy2` 2026-09-29, `pkdm-hqz6` 2026-09-29, ACRIS 2026-09-08) |

The competitor report used PLUTO 24v4 (review page 88).

## Comparison with competitor review section A

Verdicts: **agrees**, **differs** (with the numbers), or **not recorded** (with the reason).
Values are quoted as served. Geometry figures are planar EPSG:2263 computations on the recorded
MapPLUTO ring. They are reference readings for this comparison, not product outputs (B-03 owns
site geometry).

| Section A item | Expected | Recorded (file → field) | Verdict |
|---|---|---|---|
| Lot area | 10,075 sq ft | PLUTO `lotarea` "10075" | **agrees** |
| Lot area (outline) | 10,075 sq ft | MapPLUTO 26v2 polygon: `Shape__Area` 10387.988…; the planar area of the ring is 10,387.99 sq ft | **differs:** +312.99 sq ft (+3.11 %) |
| Lot dimensions | about 100.8 × 100 ft | PLUTO `lotfront` "100.7600000", `lotdepth` "100.0000000". DOB BIS A3 job 440655961 (BIN 4623241) `job_description`: "CORNER LOT, FRONTAGE ON 215 PLACE:100', FRONTAGE ON NORTHERN BLVD:100.76'" | **agrees** (100.76 × 100) |
| Lot dimensions (outline) | about 100.8 × 100 ft | MapPLUTO ring edges: 103.88 ft (north, facing Northern Blvd), 99.98 ft (east, facing 215 Place), 99.98 ft (west), 101.71 + 2.22 ft (south) | **differs:** the Northern Blvd side is 103.88 ft, not 100.76 ft |
| Corner lot (215 Place & Northern Blvd) | corner | Recorded DCM segments: Northern Boulevard (OBJECTID 53832) centerline runs parallel to the north edge at about 51.0 ft; 215 Place (OBJECTID 11453) centerline about 28.8 ft from the east edge. DOB A3 440655961 text says "CORNER LOT". PLUTO `lottype` "3" is a code; the data dictionary appendix is not captured in the repo, so it is not interpreted here | **agrees** (DOB filing text + frontage on two intersecting mapped streets); the product classification is B-03 |
| Zoning district | R6B | PLUTO `zonedist1` "R6B"; ZTLDB `zoning_district_1` "R6B"; `nyzd` polygon OBJECTID 3201 (ZONEDIST R6B) contains the whole lot polygon; PLUTO `splitzone` false | **agrees** |
| Commercial overlay | C2-2 | PLUTO `overlay1` "C2-2"; ZTLDB `commercial_overlay_1` "C2-2"; `nyco` polygon OBJECTID 5082 (OVERLAY C2-2) contains the whole lot polygon | **agrees** |
| Max residential FAR 2.00 / 2.40 | ZR 23-22 | PLUTO `residfar` "2.00000000000", `affresfar` "2.40000000000" (`facilfar` 2.0, `commfar` 0.0 as published) | **agrees.** These are DCP's informational PLUTO columns; the legal value stays with the ZR rule (Lane A) |
| Max floor area 20,150 / 24,180 sq ft | FAR × lot area | Not a city field. 2.0 × PLUTO `lotarea` 10,075 = 20,150 and 2.4 × 10,075 = 24,180 | **agrees on the PLUTO lot area.** On the MapPLUTO polygon area (10,387.99) the same arithmetic gives 20,775.98 / 24,931.17 |
| Heights, lot coverage, rear yard, dwelling units | ZR 23-432, 23-362, 23-344(a), 23-52 | Zoning Resolution values, not city data | **not recorded:** no city dataset states them (Lane A rules) |
| Existing building: stories | 5 | PLUTO `numfloors` "5.0000000"; DOB BIS NB 440608941 `proposed_no_of_stories` "5" | **agrees** |
| Existing building: floor area | about 54,488 sq ft | PLUTO `bldgarea` "54488" (DOF building area; `resarea` 30539, `comarea` = `retailarea` 13948) | **agrees** as recorded building area. This is not zoning floor area; see disagreement 3 |
| Existing building: apartments | 38 | PLUTO `unitsres` "38"; DOB NOW CO 4623241-0000001 `number_of_dwelling_units` "38"; BIS NB 440608941 `proposed_dwelling_units` "38" | **agrees** |
| Existing building: store | 1 | PLUTO `unitstotal` "39" − `unitsres` "38" = 1 non-residential unit; `retailarea` 13948 | **agrees by arithmetic** (no field names a "store") |
| Existing FAR | about 5.4 | PLUTO `builtfar` "5.41000000000" | **agrees**, but it rests on DOF building area. The DOB NB filing gives 39,934 sq ft zoning floor area (disagreement 3) |
| Zoning-lot records | ZL description + certificate, dated 2016, recorded 2022 | ACRIS Legals (lot 70) → Master: `doc_type` "CERT" (`document_date` 2016-08-04) and "ZONE" (2016-08-09), both `recorded_datetime` 2022-02-08; also "DECL" (2022-03-16, recorded 2022-03-22) | **agrees on the dates.** Flag only: the document-type codes are not interpreted (the ACRIS code list is not a registered source) and the documents themselves are not read |
| To verify: parking / transit zone | — | PLUTO `transitzone` "Outer Transit Zone" | **recorded** (C-8 input for B-10); what it means for parking is a rules question |
| To verify: ground-floor commercial required | — | ZR question | **not recorded:** no city dataset |
| To verify: unit cap with affordable bonus | — | ZR question | **not recorded:** no city dataset |
| To verify: FRESH eligibility | — | — | **not recorded:** no connector or source registered |
| Flood zone X (review §C / p.10) | zone X | PLUTO row has no `firm07_flag` or `pfirm15_flag` (both columns exist in the 108-column schema; SODA omits nulls) | **not recorded (zone letter).** PLUTO carries no FIRM 2007 / PFIRM 2015 flag for the lot. No FEMA flood-map connector or source is registered to confirm "X" |
| E-designation check (review §C) | checked | PLUTO has no `edesignum` (null). DOB BIS rows for BIN 4623241 and DOB NOW rows have `little_e` "N" / "No" | **agrees:** no E-designation recorded. The dedicated E-designation dataset `mzjp-98aw` is not recorded (shapefile; no connector) |
| Landmark / historic district | — | PLUTO has no `landmark` or `histdist` (null); DOB BIS `landmarked` "N" | **recorded:** none. LPC datasets are not recorded (no connector or registered id) |
| Special district / limited height | — | PLUTO has no `spdist1` or `ltdheight`; ZTLDB has no special district | **recorded:** none |
| Street widths (review: not stated; benchmark open item) | — | DCM `Streetwidth`: Northern Boulevard "100" (OBJECTID 53832, `Route_Type` Mjr_st); 215 Place "60" (OBJECTID 11453). Also in the envelope: 215 Street "60" (×3), 45 Road "50" | **recorded** (new) |

## Disagreements and new facts (logged, not resolved)

1. **Lot area and outline.** PLUTO says 10,075 sq ft (100.76 × 100). The MapPLUTO 26v2 polygon measures
   10,387.99 sq ft, with a 103.88 ft side on Northern Blvd. The competitor's floor plans match the
   MapPLUTO polygon, not the tax-record lot size. The review, section B, pages 18-22, says: "Plans are
   about 103'-10" wide on a 100.8 ft lot, with a 10,388 sq ft floor plate on a 10,075 sq ft lot". The
   DOF DTM outline's 5 vertices coincide with the MapPLUTO outline's (EPSG:4326 coordinates equal
   within 1e-8 degrees). Under its connector contract the DTM outline is display-only and is not
   measured here.
2. **Buildings and BINs.** The footprint layer shows BIN 4616079 (`HEIGHT_ROOF` 60, `CONSTRUCTION_YEAR`
   2026, `LAST_STATUS_TYPE` Constructed, 99.98 % inside the lot) and BIN 4157401 (roof 24, 1961,
   1.9 % inside the lot; `BASE_BBL` still 4073340070). DOB records BIN 4616079 as a 1-story
   commercial building. It was demolished: DM 421909750 was signed off 11/18/2022. DOB records the
   existing 5-story building as **BIN 4623241**: NB 440608941, `proposed_height` "55". Its CO was
   issued 06/03/26. The footprint roof height (60) and the DOB proposed height (55) differ; neither
   is interpreted here.
3. **Existing floor area (C-3, B-05).** DOB BIS NB 440608941 states `proposed_zoning_sqft` "39934"
   and `total_construction_floor_area` "45388". PLUTO `bldgarea` is 54,488. The DOB NOW CO row
   carries no floor area. 39,934 sq ft is the filing's proposed zoning floor area (permit stage,
   `fully_permitted` 04/23/2024), not a CO statement. Per plan, 54,488 (DOF building area) must
   never be used as zoning floor area.
4. **Zoning lot (C-9).** The ACRIS CERT and ZONE documents recorded 2022-02-08 and the PLUTO
   apportionment (`appbbl` 4073340001, `appdate` 2017-04-07) suggest the zoning lot may not equal
   tax lot 70. Flag only: not verified.
5. **ZTLDB age.** Rows were last updated 2026-04-05, older than PLUTO 26v2 and the zoning-features
   layers (2026-08-17). The values still agree.
6. **Data quality.** The `ic3t-wcy2` response for BIN 4157401 carries repeated rows (for example job
   421803891 appears 3 times) and describes the old lot 1 building. Dedupe before counting jobs.

## Replay on recorded data (observed 2026-09-30)

These files were replayed offline through the connectors (injected transport) during capture:

- PLUTO `fetch_by_bbl` → `ok` (76 facts)
- ZTLDB `fetch_by_bbl` → `ok`, with the freshness warning above
- `fetch_lot_geometry` → `ok`
- `query_features` → 185 / 762 features, not transfer-limited
- DCM `fetch_street_segments(envelope=…)` → the 6 segments above
- `fetch_context_buildings(polygon=…)` → both footprints `partial_overlap`

`app.spatial.live_provider.build_live_substrate` returns `lot_overall_class` =
**`boundary_uncertain`** with `professional_review_required` = True:

- R6B OBJECTID 3201 and C2-2 OBJECTID 5082 are both `near_boundary_uncertain`. Their share point
  is 1.0 and their share min is 0.609 / 0.1265, because the district boundaries run along the lot
  lines inside the ±20 ft band.
- The ZTLDB cross-check is "agreement", with a possible vintage skew.

The M1-20 journey on this lot therefore needs the documented near-boundary handling. That result
is expected, not a data fault.

## Not recorded (no connector or registered source)

- FEMA flood zone letter.
- E-designation dataset `mzjp-98aw` (listed in `docs/research/zoning-features-ztldb-2026-07-16.md`
  as a shapefile; no connector).
- DCP transit-zone datasets `6ztr-wgff` / `dpnc-b2hd` / `vhqf-adkz` (ids only; PLUTO `transitzone`
  recorded instead).
- LPC landmark datasets.
- FRESH zones.
- ACRIS document images and the ACRIS document-code list.
- Geoclient address resolution (needs a key; not needed because the BBL is known).
- PLUTO `api/views` column snapshot (228 KB; the pinned row `version` is enough here).
