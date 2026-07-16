# M1-T001 — G1 Source and Data-Contract Gate Verification

- **Task:** M1-T001 — Official-source research: PLUTO / MapPLUTO
- **Gate:** G1 (source and data-contract)
- **Reviewer:** data-contract-verifier (independent; did not produce the work)
- **Review date / retrieval date for all live verifications:** 2026-07-16
- **Verdict:** **PASS** (with 6 required corrections listed in §4; none invalidates the producer's findings)
- **Method:** Independent live verification against official sources (Socrata `api/views` raw JSON, live SODA queries, DCP PDFs on `s-media.nyc.gov`, ArcGIS Online REST API, data.gov CKAN, NYC Open Data terms page). No dataset files downloaded; metadata, JSON APIs, PDFs, and HTML only. No connector code exists yet (research task); SODA behavior spot-tests were run live against the official endpoint.

Artifacts reviewed:
- `docs/research/pluto-mappluto-2026-07-16.md`
- `docs/research/source-registry-drafts/pluto-mappluto.json`
- `project-control/reports/M1-T001-producer-report.md`
- `project-control/reports/M1-T001-fetch-evidence.md` (E1–E7)
- `project-control/tasks/M1-T001.json` (S1–S5)

---

## 1. Mandatory live verifications (owner's list)

### 1.1 Raw Socrata metadata timestamps for `64uk-42ks` — VERIFIED, suspicion resolved

Fetched `https://data.cityofnewyork.us/api/views/64uk-42ks.json` (2026-07-16) and converted the raw unix integers myself:

| Field | Raw value | UTC |
|---|---|---|
| `createdAt` | 1581533291 | 2020-02-12T18:48:11Z |
| `rowsUpdatedAt` | 1779997848 | **2026-05-28T19:50:48Z** |
| `publicationDate` | 1779987139 | 2026-05-28T16:52:19Z |
| `viewLastModified` | 1779997241 | 2026-05-28T19:40:41Z |

The stored evidence's summarizer reading ("Last Updated: August 26, 2026 / Publication Date: July 30, 2026") was **wrong** — a summarizer misconversion, exactly as the producer suspected and flagged. Actual values are plausible: rows last updated 2026-05-28, consistent with the May 2026 (26v1) release. Also confirmed: `provenance: official`, `viewType: tabular`. **OQ-1 RESOLVED.**

Observation for OQ-6: as of 2026-07-16 the SODA channel still serves `version = "26v1"` with rows last updated 2026-05-28 — no monthly minor release has propagated in ~7 weeks (either none was published to this channel or minor releases lag; OQ-6 remains open but now has a baseline observation).

### 1.2 Complete column list — VERIFIED: 108 columns; all questioned fields exist

The `columns` array of `api/views/64uk-42ks.json` contains **108 fieldNames** (vs the 73-field single-record sample). All fields the producer flagged as unconfirmed **do exist as SODA columns**: `zonedist2`, `zonedist3`, `zonedist4`, `overlay1`, `overlay2`, `spdist1`, `spdist2`, `spdist3`, `ltdheight`, `landmark`, `histdist`, `appbbl`, `condono`, `bldgclass`, plus `edesignum`, `zmcode`, `appdate`, `ownertype`.

Fields in the columns array not mentioned in the deliverables: `firm07_flag`, `pfirm15_flag`, `dcpedited`, `notes`, `geom` (the tabular dataset carries a geometry column), and per-input date columns `basempdate`, `dcasdate`, `edesigdate`, `landmkdate`, `masdate`, `polidate`, `rpaddate`, `zoningdate` (per-record input-vintage provenance — directly useful for the provenance contract).

**Discrepancy found:** the MIH columns are **`mih_opt1`, `mih_opt2`, `mih_opt3`, `mih_opt4`** — NOT `mihoption1`–`mihoption4` as listed in the registry draft's `dictionary_known_fields_not_in_sample` (see Correction C1). The producer's caveat "a connector must never infer schema from record keys" is validated. **OQ-2 RESOLVED.**

### 1.3 Field units and null semantics — VERIFIED from the official 26v1 data dictionary (direct PDF read)

Fetched `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` (605 KB) and read the field-definition pages directly. Title header verbatim: **"PLUTO DATA DICTIONARY — May 2026 (26v1)"** (OQ-5/OQ-7 dictionary identity confirmed).

| Field | Verified (verbatim basis, dictionary pages in parentheses) |
|---|---|
| **LotArea** (p.21) | "Total area of the tax lot, expressed in **square feet** rounded to the nearest integer." Includes street beds for "paper streets". If PTS has zero, DCP substitutes the DTM geometric area and sets DCPEdited=1. |
| **LotFront / LotDepth** (p.29) | "The tax lot's frontage measured in **feet**." / "The tax lot's depth measured in **feet**." Format Numeric 9999.99. |
| **NumFloors** (p.28) | "The number of full and partial floors starting from the ground floor, for the tallest building on the tax lot" (partial floors give fractional values, e.g. 2.5). Above-ground basements and parking/farm/playground roofs excluded. "If the NUMBER OF FLOORS is null and the NUMBER OF BUILDINGS is greater than zero, then NUMBER OF FLOORS is not available for the tax lot." (Complements the README rule: null shown for zero and values < 1.) |
| **BBL** (p.38) | "A concatenation of the borough code, tax block and tax lot" — 1 digit + block zero-padded to 5 + lot zero-padded to 4 = 10 digits. "**For condominiums, the BBL is for the billing lot.**" Examples verified (1000160100, 3158287501). |
| **BldgArea** (p.22) | "The total gross area in **square feet**, except for condominium measurements which come from the Condo Declaration and are **net square footage not gross**." Population order of preference 1–4 documented; AreaSource identifies the method; "rough estimate... does not necessarily take into account all the criteria for calculating floor area as defined in section 12-10 of the Zoning Resolution" — i.e., **BldgArea is NOT zoning floor area**. |
| **YearBuilt** (p.34–35) | 4-digit year construction completed; decade-accurate caveat; ~26,000 historic-district buildings replaced with LPC date-high values (DCPEdited=1). Null convention verbatim: "**If Year Built is null or 0, then the value is unknown.**" |
| **AssessLand / AssessTot / ExemptTot** (p.33–34) | Dollar assessed values from DOF PTS; tentative roll (mid-January) vs final roll (~May 25) selection rule documented; assessed as of January 5. |
| **XCoord / YCoord** (p.39–40) | "The XY coordinates are expressed in the **New York-Long Island State Plane coordinate system**." If not available from Geosupport, calculated from the lot centroid constrained to lot boundaries. (The dictionary entry does not state an EPSG code; the official ArcGIS MapPLUTO service reports `wkid 102718 / latestWkid 2263`, i.e. EPSG:2263 NAD83 NY-Long Island ftUS — see §1.4.) |
| **BoroCode** (p.38) | 1=MN, 2=BX, 3=BK, 4=QN, 5=SI; Marble Hill BoroCode 1; Rikers BoroCode 2 (legal borough, not service borough) — matches the producer's idiosyncrasy note. |
| **ResidFAR/CommFAR/FacilFAR** (p.36–37) | Based on ZoneDist1 (falls through ZoneDist2–4 if ZoneDist1 disallows the use); **exclusive of bonuses**; ZR §23-20/§33-12/§24-11 pointers; AffResFAR is the affordable-housing FAR reference. Confirms these are informational, not a substitute for the rules engine. |
| **CondoNo** (p.39) | "Condominium numbers are unique within a borough." |

**OQ-5 substantially RESOLVED** for the key property-profile fields (full code-list appendices B–D remain available in the same PDF for connector-build time). **OQ-7 RESOLVED.**

### 1.4 ArcGIS feature service for MapPLUTO — VERIFIED (official endpoint identified)

Via ArcGIS Online REST search + item + portal APIs (2026-07-16):

- **Endpoint:** `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (layer 0 "MAPPLUTO")
- **Owner:** `DCP_GIS`, orgId `GfwWNkhOj9bNBqoJ` = **"NYC DCP Mapping Portal"**, urlKey `DCP` (matches the Hub item `DCP::mappluto-1`); item `accessInformation`: "NYC Department of City Planning (DCP)"; item modified 2026-05-27.
- **Layer verified live:** `esriGeometryPolygon`, **103 fields** (ZoneDist1–4, Overlay1–2, SPDist1–3, LtdHeight, SplitZone, etc., PascalCase names), spatialReference `wkid 102718 / latestWkid 2263`, `maxRecordCount 2000`.
- **Sample query returned:** `{"Version": "26v1", "BBL": 1000010100}` — the service serves the **current 26v1** release.

**OQ-3 RESOLVED.** Note: `maxRecordCount=2000` makes this a per-lot/per-area query channel, not a full-city import channel (~850k+ lots would need ~430 paged requests); the bulk FileGDB remains the right primary for citywide geometry import. The registry should add this endpoint as a verified secondary/query channel (Correction C4).

### 1.5 DCP bulk-download page and archive — PARTIALLY VERIFIED; exact file URLs remain open

- `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` returns **HTTP 403** to both curl (with and without browser UA — serves a challenge shell) and WebFetch from this environment, same as the orchestrator's session. Bot protection confirmed, not a producer error.
- **Archive page URL identified via search:** `https://www.nyc.gov/site/planning/data-maps/open-data/bytes-archive.page` ("BYTES of the BIG APPLE — Archive") — official domain, page itself unfetchable from here.
- **data.gov cross-check:** `catalog.data.gov/dataset/primary-land-use-tax-lot-output-map-mappluto` lists exactly one resource, `http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page`, and the Socrata landing page `f888-ni5f` — i.e., the federal catalog also points at the protected DCP page; no direct file URLs are published there. Its description confirms "GIS format (ESRI Shapefile)".
- **Official MapPLUTO metadata PDF read directly** (`https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/meta_mappluto.pdf`, 497.7 KB): title **"MapPLUTO 26v1 - Shoreline Clipped"**; confirms the shoreline-clipped variant ("does not contain lots completely or partially underwater"), DTM-derived Tax Lot Polygon geometry, the **PLUTO Only non-geographic table** for PLUTO records without a DTM lot, DCP Mapping Lots (malls/traffic islands/built streets through parks), condo unit lots 1001–6999 vs **billing lots 7501–7599** with base-lot ("FKA") merge behavior, credits "NYC Department of City Planning, Information Technology Division", and the same informational-purposes disclaimer.

**Verified:** formats include FileGDB + shapefile family (metadata + data.gov), clipped 26v1 variant confirmed by official metadata; archive page URL identified. **Still open (OQ-4 residual):** exact download `.zip` URLs, file sizes, unclipped/borough-shapefile file names — require a browser-capable session against nyc.gov. Do NOT guess these.

### 1.6 Sweep of all [NEEDS G1 RE-VERIFICATION] markers

| Marker (doc location) | Status after live verification |
|---|---|
| §2.1 suspect timestamps (OQ-1) | **RESOLVED** — real values 2026-05-28; summarizer was wrong (§1.1) |
| §2.2 `f888-ni5f` href target (OQ-9) | **RESOLVED** — `metadata.accessPoints["web site"] = http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page`; also verified stale attachments `PLUTODD22v3.pdf`/`PlutoReadme22v3.pdf` and frozen 2013-07-25 created/rowsUpdated timestamps (viewLastModified 2024-10-30) |
| §2.3 data dictionary URL/version (E5, OQ-7) | **RESOLVED** — direct PDF read, "PLUTO DATA DICTIONARY May 2026 (26v1)" (§1.3) |
| §2.4 DCP page + formats + archive (OQ-4, OQ-10) | **PARTIALLY RESOLVED** — page exists (403-protected), archive URL identified, clipped-26v1/FileGDB/shapefile confirmed via official metadata PDF + data.gov; exact zip URLs/sizes and unclipped/borough file names still open |
| §2.4 `db-pluto` build pipeline | **VERIFIED WITH CORRECTION** — repo exists but is **archived since 2023-07-13**; active official repo is `https://github.com/NYCPlanning/data-engineering` (Correction C3) |
| §2.5 ArcGIS channel (OQ-3) | **RESOLVED** — official endpoint verified live (§1.4) |
| §3.5 archive statement | **PARTIALLY RESOLVED** — archive page URL identified; contents unverified (nyc.gov 403) |

### 1.7 Registry draft check (PRD §8.2) — PASS with corrections

Both records contain all PRD §8.2 fields (source ID, agency, name, official URL, source type, API/dataset identifier, authentication, rate limits, update frequency, geographic coverage, fields available, terms/usage notes, connector implementation, last successful ingestion, latest source version, health status, known limitations, fallback source) plus `open_questions`. Nulls used where unknown (`last_successful_ingestion: null`, `rate_limits: null` for bulk). `health_status: "unverified"` is honest.

- **One invented value found:** `dictionary_known_fields_not_in_sample` lists `"mihoption1"`–`"mihoption4"` as if they were SODA fieldNames; actual columns are `mih_opt1`–`mih_opt4`. The other names in that list (`zonedist2`…`condono`, `edesignum`, `zmcode`) all match the verified columns array exactly. Minor defect D1 / Correction C1.
- Rate-limit/auth text re-verified verbatim against `https://dev.socrata.com/docs/app-tokens` (2026-07-16): tokenless requests "come from a shared pool via IP address"; tokened requests not throttled "unless... abusive or malicious"; throttled → "status code 429"; `X-App-Token` header preferred, `$$app_token` param alternative. Registry text accurate.
- `open_questions` arrays were accurate at submission; after this review most are resolved (see §3) and should be updated at rework/acceptance.

### 1.8 Low-storage policy and priority-order consistency — PASS

- The research doc never downloads nor instructs downloading citywide datasets locally: bulk import is specified as a Render worker job with bounded temp space, Supabase Storage upload, and temp cleanup (§7 of the doc); fixtures are KB-scale; F11 is HEAD/metadata-only on a Render worker.
- Priority order (PLUTO via SODA with bulk CSV fallback; MapPLUTO via DCP bulk FileGDB clipped; `f888-ni5f` as pointer only) is consistent with the evidence and with PRD §8 tiers. With the ArcGIS service now verified, it becomes a legitimate secondary per-lot query channel for MapPLUTO (maxRecordCount 2000 rules it out as the citywide import primary) — recommend recording it as verified-secondary, not primary (Correction C4).
- This review itself downloaded no dataset files. Two official PDFs (~1.1 MB total) were cached by the WebFetch harness outside the repository; no large or persistent artifacts were written to the repo or owner-visible locations.

## 2. Additional live spot-tests (connector scenario preview, run against the official endpoint 2026-07-16)

| Test | Request | Actual result |
|---|---|---|
| Version/provenance probe | `/resource/64uk-42ks.json?$select=version&$limit=1` | `[{"version":"26v1"}]` — F9 fixture design validated |
| No-match | `/resource/64uk-42ks.json?bbl=9999999999` | `[]` (empty array) — F3 validated |
| Pagination + ordering | `$select=bbl&$order=bbl&$limit=2&$offset=1` | Stable ordered results — **but BBL serialized as `"1000010100.00000000"`** (Socrata number type with trailing decimals). New normalization hazard; must be handled in the connector (Correction C6) |
| Schema-drift / bad column | `$select=nonexistent_col` | **HTTP 400**, JSON error body `errorCode: "query.soql.no-such-column"` — usable as the schema-drift failure signature |

New channel discovered during verification: **PLUTO Change File is its own tabular Socrata dataset `qt5r-nqxp`** (attribution DCP, rowsUpdatedAt 2026-05-28T19:39:30Z — same release day as PLUTO). This resolves OQ-11's "location" half without touching the bulk download.

## 3. Open-questions ledger after G1 (OQ-1..OQ-11)

| OQ | Status | Resolution / residual |
|---|---|---|
| OQ-1 | **RESOLVED** | rowsUpdatedAt 2026-05-28T19:50:48Z; publicationDate 2026-05-28T16:52:19Z; createdAt 2020-02-12. Socrata metadata timestamps are usable for freshness signals on this dataset (keep `version`-field polling as primary) |
| OQ-2 | **RESOLVED** | 108 columns enumerated from the columns array; all questioned fields present; MIH columns are `mih_opt1-4` |
| OQ-3 | **RESOLVED** | Official DCP_GIS FeatureServer verified live, serving 26v1, EPSG 2263, maxRecordCount 2000 |
| OQ-4 | **STILL OPEN (narrowed)** | Archive page URL identified (`.../bytes-archive.page`); page + exact zip URLs/sizes need a browser-capable session (nyc.gov 403 to non-browser clients confirmed twice) |
| OQ-5 | **SUBSTANTIALLY RESOLVED** | Units/null conventions for all key property-profile fields verified from the 26v1 dictionary (§1.3); code-list appendices (BldgClass, LandUse, SPDist, LtdHeight) extractable at connector-build time from the same verified PDF |
| OQ-6 | **STILL OPEN (baseline set)** | 26v1 still current on SODA 2026-07-16 with rows last updated 2026-05-28; observe across a minor-release boundary |
| OQ-7 | **RESOLVED** | Dictionary directly fetched and read; "May 2026 (26v1)" header confirmed |
| OQ-8 | **RESOLVED** | NYC Open Data terms verified (opendata.cityofnewyork.us/overview): no warranty; users agree to NYC.gov Terms of Use + Privacy Policy; no prohibition on automated access via the API; agency-specific terms may add constraints |
| OQ-9 | **RESOLVED** | href target = `http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page` |
| OQ-10 | **PARTIALLY RESOLVED** | Official `meta_mappluto.pdf` (26v1, Shoreline Clipped) read: PLUTO-Only table, DCP Mapping Lots, condo unit-lot 1001–6999 / billing-lot 7501–7599 semantics; feature-service CRS EPSG 2263. Residual: exact `.gdb` archive file names, unclipped variant file name, borough-shapefile listing (needs the nyc.gov page) |
| OQ-11 | **RESOLVED (location)** | PLUTO Change File = Socrata dataset `qt5r-nqxp` (tabular, DCP) + ships with MapPLUTO bulk per README; column-level format inspection deferred to connector build |

## 4. Required corrections (all minor; exact locations)

1. **C1 — `docs/research/source-registry-drafts/pluto-mappluto.json`, record 1, `fields_available.dictionary_known_fields_not_in_sample`:** replace `"mihoption1", "mihoption2", "mihoption3", "mihoption4"` with `"mih_opt1", "mih_opt2", "mih_opt3", "mih_opt4"` (verified SODA fieldNames). This was the only invented value found (defect D1, minor).
2. **C2 — research doc §2.1 and §5.1(4) and OQ-1 row:** replace the suspect-timestamp caveat with the verified values (createdAt 2020-02-12T18:48:11Z; rowsUpdatedAt 2026-05-28T19:50:48Z; publicationDate 2026-05-28T16:52:19Z) and drop "do not use for freshness monitoring until re-verified" from the registry `known_limitations` (keep version-field polling as the primary freshness signal).
3. **C3 — research doc §2.4 and §9 (E6 row):** `NYCPlanning/db-pluto` is **archived (2023-07-13)**; the active official build repository is `https://github.com/NYCPlanning/data-engineering`. Update before anyone cites db-pluto as authoritative.
4. **C4 — research doc §2.5/§5.2 and registry record 2 (`fallback_source`, `open_questions`):** record the verified ArcGIS endpoint `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (owner DCP_GIS = "NYC DCP Mapping Portal"; layer 0 polygon; 103 fields; Version 26v1; wkid 102718/2263; maxRecordCount 2000) as the verified fallback/per-lot query channel; keep bulk FileGDB as citywide-import primary.
5. **C5 — research doc §4.2/§4.6 and registry record 1:** update the column inventory to the verified 108-column set, noting `geom` and the eight per-input date columns (`basempdate`, `dcasdate`, `edesigdate`, `landmkdate`, `masdate`, `polidate`, `rpaddate`, `zoningdate`) as per-record provenance fields, plus `firm07_flag`, `pfirm15_flag`, `dcpedited`, `notes`, `ownertype`, `appdate`. XCoord/YCoord CRS: "New York-Long Island State Plane" (dictionary verbatim); EPSG 2263 confirmed for the ArcGIS service side.
6. **C6 — research doc §6 (fixture pack) and registry `known_limitations`:** add the BBL numeric-serialization hazard — `$select`ed BBL returns `"1000010100.00000000"`; connector must normalize Socrata number-typed BBLs to 10-digit strings. Also add PLUTO Change File dataset `qt5r-nqxp` as a verified companion channel (updates OQ-11).

## 5. Defects

- **D1 (minor, factual):** guessed SODA fieldNames `mihoption1-4` in the registry draft (see C1). Everything else the producer asserted as fact verified true; everything uncertain was correctly flagged and is now resolved or narrowed as recorded above.

No critical or major defects. No provenance violations. No low-storage violations.

## 6. Recommendation for G3

PASS this G1 with corrections C1–C6 applied by a producer/rework pass (or by the orchestrator as an editorial fixup, since all corrected values are recorded here with evidence). G3 (independent walkthrough) should:
1. Confirm the corrected documents read coherently against this report,
2. Re-run the four SODA spot-tests in §2 as its normal/boundary/missing/failure cases (exact requests given),
3. Treat OQ-4 residual (exact bulk zip URLs) and OQ-10 residual (gdb file names) as the only legitimately open items — they require a browser session against nyc.gov and must not be guessed,
4. Verify no citywide data was written locally (nothing in the repo; two official PDFs ~1.1 MB in the harness WebFetch cache only).

## 7. Evidence URL index (all retrieved 2026-07-16 by this reviewer)

| # | URL | What it verified |
|---|---|---|
| V1 | `https://data.cityofnewyork.us/api/views/64uk-42ks.json` | Raw timestamps; 108-column array; provenance=official |
| V2 | `https://data.cityofnewyork.us/resource/64uk-42ks.json` (`$select=version`, `bbl=9999999999`, `$order=bbl&$limit=2&$offset=1`, `$select=nonexistent_col`) | version=26v1; no-match `[]`; pagination; 400 error shape; BBL serialization hazard |
| V3 | `https://data.cityofnewyork.us/api/views/f888-ni5f.json` | href type; accessPoints target; stale 22v3 attachments; frozen 2013 timestamps |
| V4 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` | 26v1 dictionary; units/null conventions for key fields (pages 1–2, 21–22, 28–29, 33–40 read directly) |
| V5 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/meta_mappluto.pdf` | "MapPLUTO 26v1 - Shoreline Clipped" official metadata; PLUTO-Only table; condo lot-number ranges |
| V6 | `https://www.arcgis.com/sharing/rest/search`, `.../content/items/1564ace0b4f44318ac39920737f9bd07`, `.../portals/GfwWNkhOj9bNBqoJ`, `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (+`/0`, +`/0/query`) | Official DCP ArcGIS feature service, org identity, live 26v1 record |
| V7 | `https://catalog.data.gov/dataset/primary-land-use-tax-lot-output-map-mappluto` | Federal catalog resource pointer; "ESRI Shapefile" format statement |
| V8 | `https://opendata.cityofnewyork.us/overview/` | NYC Open Data terms of use (OQ-8) |
| V9 | `https://github.com/NYCPlanning/db-pluto` | Repo archived 2023-07-13; successor `NYCPlanning/data-engineering` |
| V10 | `https://dev.socrata.com/docs/app-tokens` | Token/throttling/429/X-App-Token claims re-verified verbatim |
| V11 | `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` | HTTP 403 to curl and WebFetch (bot protection confirmed independently) |
| V12 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=mappluto` | No tabular MapPLUTO SODA resource exists (confirms producer); discovered `qt5r-nqxp` PLUTO Change File |
| V13 | WebSearch (BYTES archive) | Archive page URL `https://www.nyc.gov/site/planning/data-maps/open-data/bytes-archive.page` (page itself unfetchable from this environment) |
