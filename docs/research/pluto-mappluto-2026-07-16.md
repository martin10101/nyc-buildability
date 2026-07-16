# M1-T001 — Official-Source Research: PLUTO / MapPLUTO

- **Task:** M1-T001 — Official-source research: PLUTO / MapPLUTO
- **Producer agent:** official-source-researcher
- **Retrieval date for all sources:** 2026-07-16 (unless noted)
- **Evidence basis:** This report is written from orchestrator-captured evidence in `project-control/reports/M1-T001-fetch-evidence.md` (sections E1–E7, all fetched/searched live on 2026-07-16), per the ADR-005 / 2026-07-15 evidence-capture directive, because the producer sandbox denied all network tools (see `project-control/reports/M1-T001-producer-report.md` §3 history). Each claim below cites the evidence section (E1–E7) plus the underlying official URL.
- **Discipline:** Claims that come only from a search-result summary or a summarizer paraphrase — rather than a verbatim quote or a directly read document — are marked **[NEEDS G1 RE-VERIFICATION]**. Nothing unverified is presented as fact. Anything unknown is listed in §8 Open Questions.
- **Post-G1 status (2026-07-16):** the G1 data-contract-verifier independently live-verified this document (`project-control/reports/M1-T001-G1-verification.md`, verdict PASS) and corrections C1–C6 from that report were applied in place by the orchestrator. Markers below that say **[RESOLVED AT G1 — see G1 report §…]** were re-verified directly against official sources by the reviewer; the only items still open are OQ-4 (exact bulk zip URLs/sizes) and OQ-10 residual (exact .gdb/borough-shapefile file names), both blocked by nyc.gov bot protection and deliberately not guessed.

---

## 1. Executive summary

| Product | What it is | Verified distribution channels (2026-07-16) | Current version | Recommended role |
|---|---|---|---|---|
| **PLUTO** (Primary Land Use Tax Lot Output) | Tabular land-use/geographic data, one record per tax lot (condos: one record per condominium complex), 70+ fields, CSV | NYC Open Data tabular dataset **`64uk-42ks`** with a **live SODA resource endpoint** (E1, E2); DCP bulk CSV release documented by the official README (E4) | **26v1** (observed live in the SODA `version` field, E2; matches "May 2026 (26v1)" README header, E4) | **Primary property-facts source** for the citywide profile. Consume via SODA API; bulk CSV fallback |
| **MapPLUTO** | PLUTO attributes merged with DCP-modified DOF Digital Tax Map lot geometry, GIS formats, clipped to shoreline (unclipped variant exists) | NYC Open Data entry **`f888-ni5f`** is **href-type (external pointer), NOT a tabular SODA resource** (E3); real distribution is DCP bulk FileGDB/shapefile via BYTES of the BIG APPLE (E4, E6) | 26v1 per DCP README (E4); the `f888-ni5f` portal attachments are **stale at 22v3** (E3) | **Primary geometry source**, consumed as DCP bulk FileGDB (shoreline-clipped) into PostGIS |

Release model (official README 26v1, E4, verbatim basis): **major updates quarterly (all fields), minor updates monthly (zoning attributes only)**; versions named like `24v1` (major) and `24v1.1`, `24v1.2` (minor).

---

## 2. S1 — Distribution channels, identifiers, formats

### 2.1 NYC Open Data — PLUTO tabular dataset `64uk-42ks` (VERIFIED, live)

- Dataset metadata fetch: `https://data.cityofnewyork.us/api/views/64uk-42ks.json` (E1, retrieved 2026-07-16).
  - Name: "Primary Land Use Tax Lot Output (PLUTO)"; ID **`64uk-42ks`**; attribution "Department of City Planning (DCP)"; category "City Government"; viewType tabular/table; provenance "Official"; created 2020-02-12.
  - Description (quoted in E1): "Extensive land use and geographic data at the tax lot level in comma-separated values (CSV) file format. The PLUTO files contain more than seventy fields derived from data maintained by city agencies."
  - Raw timestamps **[RESOLVED AT G1 — see G1 report §1.1]**: `createdAt` 1581533291 = 2020-02-12T18:48:11Z; `rowsUpdatedAt` 1779997848 = **2026-05-28T19:50:48Z**; `publicationDate` 1779987139 = 2026-05-28T16:52:19Z — consistent with the May 2026 (26v1) release. (The evidence summarizer's "August 26, 2026 / July 30, 2026" reading was a misconversion, exactly as suspected.) Socrata metadata timestamps ARE usable as freshness signals on this dataset; keep `version`-field polling as the primary signal.
- **SODA resource endpoint is live**: `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1` returned a valid JSON record on 2026-07-16 (E2). The record's **`version` field value is `"26v1"`** — the Open Data tabular channel currently serves the same version as the DCP bulk release.
- 73 fields were present on the sampled record (verbatim list in §4.2 below). SODA omits null fields per record, so this is a floor, not the full column set (OQ-2).

### 2.2 NYC Open Data — MapPLUTO entry `f888-ni5f` (VERIFIED, pointer-only)

- Dataset metadata fetch: `https://data.cityofnewyork.us/api/views/f888-ni5f.json` (E3, retrieved 2026-07-16).
  - Name: "Primary Land Use Tax Lot Output - Map (MapPLUTO)"; ID **`f888-ni5f`**; attribution DCP.
  - Description (quoted in E3): "Comprehensive land use and geographic data at the tax lot level in GIS format... merged with tax lot features from the Department of Finance's Digital Tax Map, clipped to shoreline."
  - **viewType/displayType: `href`** — an attachment/external-link entry, **not** a tabular SODA resource. Update frequency metadata: "Quarterly".
  - Attachments listed on the portal: `PLUTODD22v3.pdf`, `PlutoReadme22v3.pdf` — **stale 22v3 documents** while the current release is 26v1 (channel-lag finding, see §5).
  - Raw timestamps: created/rowsUpdated/publication all 1374771826/1374771872 (2013-07-25) — href datasets do not update row timestamps; version currency must come from the DCP channel.
  - The URL the href entry points to **[RESOLVED AT G1 — OQ-9]**: `metadata.accessPoints["web site"]` = `http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page`.

### 2.3 DCP bulk release — README and data dictionary PDFs (VERIFIED for README; dictionary URL search-verified)

- **Official PLUTO README 26v1** directly fetched and read (pages 1–8): `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_readme.pdf` (342 KB PDF; E4, retrieved 2026-07-16). Header: "PLUTO README DOCUMENT — May 2026 (26v1)". Opening: "The Primary Land Use Tax Lot Output (PLUTO™) data file contains extensive land use and geographic data at the tax lot level in an ASCII comma-delimited file." Fields are derived from data maintained by DCP, DOF, DCAS, and LPC.
- **Official PLUTO data dictionary 26v1**: "PLUTO DATA DICTIONARY May 2026 (26v1)" at `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` (E5). **[RESOLVED AT G1 — see G1 report §1.3]**: the reviewer fetched and read the PDF directly (605 KB; header verbatim "PLUTO DATA DICTIONARY — May 2026 (26v1)") and verified units/null conventions for the key property-profile fields (see §4.3/§4.6 updates below).

### 2.4 DCP web page and archive (search-evidenced only — bot-protected to this session)

- Current DCP page: `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` (search-result title: "PLUTO, MapPLUTO and PLUTO Change File"); legacy URL `https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page` still resolves in search (E6). **nyc.gov 403 independently confirmed at G1** (curl with browser UA and WebFetch both blocked — bot protection, not a producer error; G1 report §1.5). Exact download `.zip` URLs and file sizes remain OPEN (OQ-4 residual) — they require a browser-capable session and must not be guessed.
- MapPLUTO bulk formats **[PARTIALLY RESOLVED AT G1 — see G1 report §1.5]**: the official `meta_mappluto.pdf` (497.7 KB) was read directly — title "MapPLUTO 26v1 - Shoreline Clipped"; confirms DTM-derived tax-lot polygon geometry, the shoreline-clipped variant ("does not contain lots completely or partially underwater"), the **PLUTO Only non-geographic table** (PLUTO records without a DTM lot), DCP Mapping Lots, and condo unit lots 1001–6999 vs **billing lots 7501–7599** with base-lot ("FKA") merge behavior. FileGDB + shapefile family confirmed via metadata + data.gov ("ESRI Shapefile"). Exact archive file names for clipped/unclipped and borough shapefiles remain OPEN (OQ-10 residual).
- Archive **[PARTIALLY RESOLVED AT G1]**: official archive page identified at `https://www.nyc.gov/site/planning/data-maps/open-data/bytes-archive.page` ("BYTES of the BIG APPLE — Archive"); page contents unfetchable from this environment (403).
- Build pipeline **[RESOLVED WITH CORRECTION AT G1 — C3]**: `https://github.com/NYCPlanning/db-pluto` exists but is **archived since 2023-07-13**; the active official build repository is `https://github.com/NYCPlanning/data-engineering`. Do not cite db-pluto as authoritative for current field derivations.

### 2.5 ArcGIS channel (VERIFIED AT G1 — official endpoint identified; C4)

- **[RESOLVED AT G1 — see G1 report §1.4]**: official feature service verified live via ArcGIS Online REST search/item/portal APIs (2026-07-16):
  - **Endpoint:** `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (layer 0 "MAPPLUTO", `esriGeometryPolygon`).
  - **Owner:** `DCP_GIS`, org "NYC DCP Mapping Portal" (urlKey `DCP`); item modified 2026-05-27; matches Hub item `DCP::mappluto-1`.
  - **Layer:** 103 fields (PascalCase: ZoneDist1–4, Overlay1–2, SPDist1–3, LtdHeight, SplitZone, …), spatialReference `wkid 102718 / latestWkid 2263` (EPSG:2263 NAD83 NY-Long Island ftUS), **`maxRecordCount 2000`**.
  - Live query returned `{"Version": "26v1", "BBL": 1000010100}` — serves the current release.
- Role: `maxRecordCount 2000` rules it out as the citywide-import primary (~850k+ lots ≈ 430 paged requests); use as the **verified secondary/per-lot query channel**; DCP bulk FileGDB remains the citywide-import primary.

---

## 3. S2 — PLUTO vs MapPLUTO; version scheme; archiving

### 3.1 Product distinction (README 26v1, E4)

- **PLUTO** = attribute file: "extensive land use and geographic data at the tax lot level in an ASCII comma-delimited file" (E4, verbatim).
- **MapPLUTO** = PLUTO + geometry: "City Planning also merges the PLUTO data with the DCP modified version of the DOF's Digital tax map to create MapPLUTO for use with various geographic information systems." (E4, verbatim). The Open Data description adds "merged with tax lot features from the Department of Finance's Digital Tax Map, clipped to shoreline" (E3).

### 3.2 Version scheme and release cadence (README 26v1, E4 — verbatim)

> "There are two types of PLUTO updates: major and minor. Major updates occur quarterly, and all fields are updated. A major update is represented first digit in the version number after 'v', for example 24v1. Minor updates are released monthly between major updates and only include updates to the zoning attributes. A minor release is represented by the decimal after the version number – 24v1.1, 24v1.2, etc."

- Fields updated in **minor (monthly) releases**: ZoneDist1–4, Overlay1–2, SPDist1–3, LtdHeight, SplitZone, ResidFAR, CommFAR, FacilFAR, ZoneMap, ZMCode, TaxMap, EDesigNum (E4).
- **Current version: 26v1** ("May 2026 (26v1)" README header, E4; independently observed as the `version` value in the live SODA record, E2).
- **Change tracking:** "The changes made to a tax lot record are records in PLUTOChangeFile\<ver\>.csv, which is available as part of the MapPLUTO download on BYTES of the BIG APPLE." (E4, verbatim). **[RESOLVED AT G1 — C6]:** the PLUTO Change File is ALSO its own tabular Socrata dataset **`qt5r-nqxp`** (attribution DCP; `rowsUpdatedAt` 2026-05-28T19:39:30Z — same release day as PLUTO), a verified companion channel.

### 3.3 Underlying data vintages — DATES OF DATA table (README 26v1, E4)

| Input source | Date of data (26v1) |
|---|---|
| DCP E-Designations | 2026-04-01 |
| DCP Zoning Map Index | 2019-07-01 |
| City Owned/Leased | 2025-03-31 |
| NYC GIS Zoning Features | 2026-03-31 |
| Political/Admin Districts 26A | 2026-04-01 |
| Geosupport version 26A | 2026-04-01 |
| DOF Digital Tax Map (DTM) | 2026-04-03 |
| DOF CAMA | 2026-03-02 |
| DOF PTS | 2026-03-30 |
| Parks GreenThumb | 2026-04-14 |
| LPC Landmark + Historic District Building DB | 2026-02-03 |
| LPC Individual Landmarks | 2026-02-02 |
| OTI Building Footprint Centroids | 2026-03-29 |

Provenance implication: a PLUTO fact's effective date is bounded by the per-input vintage above, not the release date. Connectors must store the PLUTO `version` value with every fact (it is a field on every SODA record, E2).

Note: PLUTO 26v1 was built on **Geosupport 26A**, while the M0-T002 report found Geosupport/PAD **26B** current as of 2026-07-14 — cross-source version skew the conflict engine must expect (cross-reference: `docs/research/M0-T002-geoclient-address-resolution.md`).

### 3.4 New in 26v1 (README, E4)

- New fields vs 25v4: **MIHOption1–4** (Mandatory Inclusionary Housing option flags), **TrnstZone** (Transit Zone classification), **AffResFAR** (max affordable residential FAR), **ManuFAR** (max manufacturing FAR). New zoning district value **C6-12**. City of Yes-related FAR updates were noted in the 25v2 change history. (E4.)
- The live SODA record already carries `affresfar`, `mnffar`, and `transitzone` columns (E2), corroborating the 26v1 schema on the Open Data channel. Note the SODA column for ManuFAR appears as `mnffar` — exact mapping of README field names to SODA column names needs the dictionary pass (OQ-5).

### 3.5 Archiving

- Prior versions are stated to be retrievable from the DCP website (BYTES of the BIG APPLE archive) (E6). **[PARTIALLY RESOLVED AT G1]:** archive page URL identified — `https://www.nyc.gov/site/planning/data-maps/open-data/bytes-archive.page`; page contents (per-version file links) remain unfetchable from this environment (nyc.gov 403; OQ-4 residual).

---

## 4. S3 — Fields, units, null semantics, BBL/condo handling

### 4.1 Authoritative data dictionary

- `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` — "PLUTO DATA DICTIONARY May 2026 (26v1)" **[RESOLVED AT G1 — direct PDF read; G1 report §1.3]**. Key field-level verifications (dictionary pages in parentheses):
  - **LotArea** (p.21): "Total area of the tax lot, expressed in **square feet** rounded to the nearest integer." Includes street beds for "paper streets"; zero PTS values substituted from DTM geometric area with `DCPEdited=1`.
  - **LotFront / LotDepth** (p.29): frontage/depth "measured in **feet**", format Numeric 9999.99.
  - **NumFloors** (p.28): full + partial floors of the tallest building (fractional values possible); "If the NUMBER OF FLOORS is null and the NUMBER OF BUILDINGS is greater than zero, then NUMBER OF FLOORS is not available for the tax lot."
  - **BBL** (p.38): borough code + block zero-padded to 5 + lot zero-padded to 4 = 10 digits; "For condominiums, the BBL is for the billing lot."
  - **BldgArea** (p.22): "total gross area in **square feet**, except for condominium measurements which... are **net square footage not gross**"; explicitly a rough estimate that is **NOT ZR §12-10 zoning floor area**.
  - **YearBuilt** (p.34–35): "If Year Built is null or 0, then the value is unknown"; decade-accurate caveat; ~26k historic-district buildings LPC-corrected (`DCPEdited=1`).
  - **AssessLand/AssessTot/ExemptTot** (p.33–34): DOF dollar values; tentative (mid-Jan) vs final (~May 25) roll selection rule.
  - **ResidFAR/CommFAR/FacilFAR** (p.36–37): based on ZoneDist1 (fallthrough ZoneDist2–4), **exclusive of bonuses** — informational, never a substitute for the rules engine.
  - **CondoNo** (p.39): unique within a borough. **BoroCode** (p.38): 1=MN 2=BX 3=BK 4=QN 5=SI; Marble Hill BoroCode 1, Rikers BoroCode 2 (legal borough).
  - Code-list appendices B–D (BldgClass, LandUse, SPDist, LtdHeight meanings) remain extractable from the same verified PDF at connector-build time (OQ-5 residual).

### 4.2 Fields observed live on the SODA channel (E2, verbatim list, 2026-07-16)

73 fields returned for one sampled record at `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1`:

```
borough, block, lot, cd, ct2010, cb2010, schooldist, council, zipcode, firecomp,
policeprct, healtharea, sanitboro, sanitsub, address, zonedist1, splitzone,
bldgclass, landuse, easements, ownername, lotarea, bldgarea, comarea, resarea,
officearea, retailarea, garagearea, strgearea, factryarea, otherarea, areasource,
numbldgs, numfloors, unitsres, unitstotal, lotfront, lotdepth, bldgfront,
bldgdepth, ext, proxcode, irrlotcode, lottype, bsmtcode, assessland, assesstot,
exempttot, yearbuilt, yearalter1, yearalter2, builtfar, residfar, commfar,
facilfar, affresfar, mnffar, borocode, bbl, tract2010, xcoord, ycoord, latitude,
longitude, zonemap, sanborn, taxmap, plutomapid, version, sanitdistrict,
healthcenterdistrict, bct2020, bctcb2020, transitzone
```

**Critical caveat (E2):** the sampled record did **not** surface `zonedist2`–`zonedist4`, `overlay1`–`overlay2`, `spdist1`–`spdist3`, `ltdheight`, `landmark`, `histdist`, `appbbl`, `condono`, etc. — **SODA omits null fields per record**. A connector must never infer schema from record keys.

**[RESOLVED AT G1 — full column inventory; G1 report §1.2, C5]:** the `/api/views/64uk-42ks.json` `columns` array contains **108 columns**. All questioned fields exist as SODA columns: `zonedist2-4`, `overlay1-2`, `spdist1-3`, `ltdheight`, `landmark`, `histdist`, `appbbl`, `condono`, `bldgclass`, plus `edesignum`, `zmcode`, `appdate`, `ownertype`. The MIH columns are **`mih_opt1`–`mih_opt4`** (not "mihoption1-4"). Additional columns beyond the 73-field sample: `geom` (the tabular dataset carries a geometry column), `firm07_flag`, `pfirm15_flag`, `dcpedited`, `notes`, and eight per-input date columns — `basempdate`, `dcasdate`, `edesigdate`, `landmkdate`, `masdate`, `polidate`, `rpaddate`, `zoningdate` — which are per-record input-vintage provenance fields directly useful for the provenance contract.

### 4.3 Null/placeholder conventions (verified so far)

- **NumFloors** (README 26v1, E4, verbatim): "NUMBER OF FLOORS (NumFloors) has been modified to show \<null\> for values of zero and for other values of less than one." The dictionary (p.28) adds: null with `NumBldgs > 0` means "not available".
- **YearBuilt** (dictionary p.34–35, verified at G1): "If Year Built is null or 0, then the value is unknown."
- **LotArea** (dictionary p.21, verified at G1): zero PTS values are substituted with the DTM geometric area and flagged `DCPEdited=1`.
- Remaining code-list conventions (`areasource`/`lottype`/`proxcode`/`bsmtcode` meanings): in the verified dictionary appendices, extraction deferred to connector build (OQ-5 residual).

### 4.4 Condominium / billing-BBL semantics (README 26v1, E4, verbatim)

> "PLUTO data contain one record per condominium complex instead of records for each condominium unit tax lot... The Condominium Complex record is assigned the 'billing' tax lot number when one exists. When the 'billing' tax lot number has not yet been assigned by DOF, the lowest tax lot number within the tax block of the Condominium Complex is assigned."

- APPBBL logic changed in the 25v1.1→25v2 range: condo lots without a direct APPBBL now inherit from an associated condo unit lot (E4).
- Consequence for the platform: a user-supplied condo-unit BBL will **not** match a PLUTO record directly; resolution must go through the billing BBL (Geoclient returns `condominiumBillingBbl` — see M0-T002 report §2.6), and record counts per block will differ from DOF unit-lot counts.

### 4.5 Geographic idiosyncrasies (README 26v1, E4)

- **Marble Hill** is legally in Manhattan but serviced by the Bronx; **Rikers Island** is legally in the Bronx but serviced by Queens. Borough-code joins against other datasets must anticipate these.

### 4.6 Coordinates

- The SODA record carries `xcoord`, `ycoord`, `latitude`, `longitude` (E2). **[RESOLVED AT G1 — C5]:** the dictionary (p.39–40) states verbatim "The XY coordinates are expressed in the **New York-Long Island State Plane coordinate system**" (no EPSG code given in the dictionary itself); the official ArcGIS MapPLUTO service reports `wkid 102718 / latestWkid 2263`, i.e. **EPSG:2263** (NAD83 NY-Long Island, US survey feet). If coordinates are unavailable from Geosupport they are calculated from the lot centroid constrained to lot boundaries.

### 4.7 Official disclaimer (README 26v1, E4, verbatim)

> "PLUTO is being provided by the Department of City Planning (DCP) on DCP's website for informational purposes only. DCP does not warranty the completeness, accuracy, content, or fitness for any particular purpose or use..."

---

## 5. S4 — Channel discrepancies and recommended priority order (PRD §8)

### 5.1 Observed cross-channel discrepancies (evidence-based)

1. **Stale portal attachments (channel lag):** the `f888-ni5f` MapPLUTO Open Data entry still lists `PLUTODD22v3.pdf` / `PlutoReadme22v3.pdf` while the current release is 26v1 (E3 vs E4). The Open Data attachment channel for documentation is roughly 3.5 years behind DCP's own site. Current dictionaries live at `s-media.nyc.gov` (E4/E5).
2. **href timestamps are dead:** `f888-ni5f` raw created/rowsUpdated timestamps are frozen at 2013-07-25 (E3) — version currency for MapPLUTO cannot be monitored from Socrata metadata; it must come from the DCP channel (or the per-record `version` field of the PLUTO SODA dataset as a proxy).
3. **Tabular channel is current:** the PLUTO SODA endpoint serves `version = "26v1"` (E2), matching the DCP release (E4) — no version lag observed on the tabular channel on 2026-07-16. Whether monthly **minor** releases (26v1.1, …) propagate to `64uk-42ks`, and how fast, is unobserved (OQ-6).
4. **Socrata metadata timestamps** on `64uk-42ks` **[RESOLVED AT G1 — C2]**: raw values verified (`rowsUpdatedAt` 2026-05-28T19:50:48Z, matching the 26v1 release); the earlier future-dated reading was a summarizer misconversion. Metadata timestamps are usable as a secondary freshness signal; `version`-field polling remains primary.

### 5.2 Recommended priority order (argued from evidence, per PRD §8 tiers)

**PLUTO tabular facts:**
1. **SODA API** — `https://data.cityofnewyork.us/resource/64uk-42ks.json` (PRD tier 2; no tier-1 dedicated API exists for PLUTO). Live, version-current (26v1), filterable per-BBL, and carries the `version` field per record for provenance (E2). Use an **`X-App-Token`** header when available: without a token, requests "are throttled by IP address and share a common pool"; with a token, Socrata does "not throttle API requests... unless those requests are determined to be abusive or malicious"; throttled requests return HTTP 429; token via `X-App-Token` header (preferred) or `$$app_token` param (E7, `https://dev.socrata.com/docs/app-tokens`).
2. **DCP bulk CSV** (PRD tier 3) — for full-city imports and for reproducible version pinning (archive of prior versions), per the README's release model (E4) and the archive statement (partially resolved at G1: archive page URL identified; exact zip URLs = OQ-4 residual). Bulk import must run on a Render worker per the low-storage policy; never on the owner's PC.

**MapPLUTO geometry:**
1. **DCP bulk File Geodatabase, shoreline-clipped** (PRD tier 3) — the verified full-fidelity official channel for citywide import; there is no tabular SODA resource for MapPLUTO (E3; confirmed at G1 via the Socrata catalog API). Clipped variant confirmed by the official `meta_mappluto.pdf` ("MapPLUTO 26v1 - Shoreline Clipped"); exact archive file names for clipped/unclipped/borough shapefiles remain open (OQ-10 residual). Shoreline-clipped is the appropriate default for zoning-analysis area computations, with the unclipped variant only if riparian-lot edge cases demand it.
2. **ArcGIS feature service — VERIFIED at G1 (C4)**: `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` (DCP_GIS, 26v1, EPSG:2263, `maxRecordCount 2000`). Use as the **secondary/per-lot query channel**; the 2000-record cap rules it out as the citywide-import primary.
3. **NYC Open Data `f888-ni5f`** — treat strictly as a catalog **pointer**, never as a data or documentation channel (stale attachments, dead timestamps; E3). Its href target (verified at G1): `http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page`.

**Freshness monitoring:** poll the PLUTO SODA `version` field (cheap `$select=version&$limit=1` style query) rather than Socrata metadata timestamps, given discrepancies 2 and 4 above.

---

## 6. Proposed contract-test fixture pack (to capture at connector build time)

All fixtures are raw, unmodified responses stored with request URL, headers (minus token), and retrieval timestamp. KB-scale only; no dataset downloads.

| # | Fixture | Request | Asserts |
|---|---|---|---|
| F1 | single-lot normal | `/resource/64uk-42ks.json?bbl=<known 10-digit BBL>` | one record; `version` present; key property-profile fields typed as expected |
| F2 | condo billing-BBL | query a known condo complex billing BBL and a unit BBL | complex record found via billing BBL; unit BBL returns 0 records (per E4 condo semantics) |
| F3 | no-match | `?bbl=<syntactically valid, nonexistent>` | empty JSON array `[]` |
| F4 | null-field omission | a lot known to have no overlays/special districts | absent keys (not null values) — schema must come from dictionary, not record |
| F5 | multi-district lot | a known split-zone lot | `splitzone` flag; `zonedist2` present |
| F6 | pagination | `$limit=1000&$offset=...` over one block | stable ordering with `$order=bbl`; no dupes/gaps |
| F7 | rate limit | tokenless burst (only in an isolated test) | HTTP 429 shape captured (per E7) |
| F8 | schema drift | `/api/views/64uk-42ks.json` columns array snapshot | column list diff vs stored contract |
| F9 | version/provenance | `$select=version&$limit=1` | version string format `^\d{2}v\d+(\.\d+)?$`; recorded per ingestion |
| F10 | Marble Hill / Rikers | the two idiosyncratic geographies (E4) | borough fields behave as documented |
| F11 | MapPLUTO bulk manifest | HEAD/metadata of the DCP FileGDB download (Render worker) | size, version in file name, checksum recorded |
| F12 | BBL numeric serialization (G1 finding, C6) | `$select=bbl&$order=bbl&$limit=2` | `$select`ed BBL returns `"1000010100.00000000"` (Socrata number type with trailing decimals) — connector MUST normalize number-typed BBLs to 10-digit strings |
| F13 | schema-drift error shape (G1 finding) | `$select=nonexistent_col` | HTTP 400 with JSON body `errorCode: "query.soql.no-such-column"` — the schema-drift failure signature |
| F14 | change-file companion (G1 finding, C6) | `/resource/qt5r-nqxp.json?$limit=1` | PLUTO Change File dataset live; column-level format inspection at connector build |

---

## 7. Connector implementation plan (plan only — no code in this task)

1. **`pluto-soda` connector (facts):** per-BBL and per-block SODA queries against `64uk-42ks` with `X-App-Token` from secrets; store raw record + `version` + retrieval timestamp in `raw_source_records` / `property_source_facts`; schema-drift check against the `api/views` columns array on every scheduled run.
2. **`mappluto-bulk` importer (geometry):** quarterly Render worker job: stream DCP shoreline-clipped FileGDB → bounded temp space → PostGIS (`tax_lot_geometries`) → upload original archive to Supabase Storage (`gis-imports`) → delete temp files (low-storage policy). Version pinned from the release file name + README.
3. **Freshness monitor:** poll SODA `version`; alert on major/minor version change; cross-check against DCP README version at each quarterly boundary.

---

## 8. OPEN QUESTIONS — post-G1 ledger (G1 report §3; corrections C1–C6 applied 2026-07-16)

| # | Question | Post-G1 status |
|---|---|---|
| OQ-1 | Raw Socrata timestamps for `64uk-42ks` | **RESOLVED** — createdAt 2020-02-12; rowsUpdatedAt 2026-05-28T19:50:48Z; publicationDate 2026-05-28T16:52:19Z (§2.1) |
| OQ-2 | Full SODA column list | **RESOLVED** — 108 columns enumerated; all questioned fields exist; MIH columns are `mih_opt1-4` (§4.2) |
| OQ-3 | Official ArcGIS feature-service endpoint | **RESOLVED** — DCP_GIS FeatureServer verified live, 26v1, EPSG:2263, maxRecordCount 2000 (§2.5) |
| OQ-4 | Exact bulk download `.zip` URLs and file sizes | **STILL OPEN (narrowed)** — archive page URL identified (`.../bytes-archive.page`); zip URLs/sizes need a browser-capable session vs nyc.gov 403; must not be guessed |
| OQ-5 | Field-level units/null conventions | **SUBSTANTIALLY RESOLVED** — key property-profile fields verified from the 26v1 dictionary (§4.1); code-list appendices (BldgClass, LandUse, SPDist, LtdHeight, AreaSource/LotType/ProxCode/BsmtCode) extractable at connector build |
| OQ-6 | Minor-release propagation lag to SODA | **STILL OPEN (baseline set)** — 26v1 unchanged on SODA as of 2026-07-16 (rows updated 2026-05-28); observe across a minor-release boundary |
| OQ-7 | Dictionary direct-fetch confirmation | **RESOLVED** — direct PDF read; header "PLUTO DATA DICTIONARY — May 2026 (26v1)" |
| OQ-8 | NYC Open Data terms for automated access | **RESOLVED** — terms verified at `opendata.cityofnewyork.us/overview`: no warranty; NYC.gov Terms of Use + Privacy Policy apply; no prohibition on automated API access; agency-specific terms may add constraints |
| OQ-9 | `f888-ni5f` href target | **RESOLVED** — `metadata.accessPoints["web site"]` = `http://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page` |
| OQ-10 | MapPLUTO variant file names / `meta_mappluto.pdf` contents | **PARTIALLY RESOLVED** — official metadata PDF read ("MapPLUTO 26v1 - Shoreline Clipped"; PLUTO-Only table; condo unit-lot 1001–6999 / billing-lot 7501–7599). Residual: exact `.gdb`/borough-shapefile archive file names (needs the nyc.gov page) |
| OQ-11 | `PLUTOChangeFile<ver>.csv` location/format | **RESOLVED (location)** — Socrata dataset `qt5r-nqxp` + ships with MapPLUTO bulk; column-level inspection at connector build |

**Legitimately still open after G1: OQ-4 residual and OQ-10 residual (both nyc.gov-403-bound), plus the OQ-6 observation window.**

---

## 9. Source register (all evidence captured 2026-07-16 by the orchestrator; see `project-control/reports/M1-T001-fetch-evidence.md`)

| Evidence | Official URL | Access method | Used for |
|---|---|---|---|
| E1 | `https://data.cityofnewyork.us/api/views/64uk-42ks.json` | live fetch (summarizer-mediated) | PLUTO dataset ID, name, attribution, description; timestamps flagged OQ-1 |
| E2 | `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1` | live fetch, verbatim record | SODA endpoint liveness, `version=26v1`, 73-field sample, null-omission behavior |
| E3 | `https://data.cityofnewyork.us/api/views/f888-ni5f.json` | live fetch | MapPLUTO href-type entry, quarterly, stale 22v3 attachments, dead timestamps |
| E4 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_readme.pdf` | direct PDF read (pages 1–8) | release model, version naming, condo/billing BBL, Marble Hill/Rikers, DATES OF DATA, 26v1 new fields, NumFloors null convention, disclaimer, PLUTOChangeFile |
| E5 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` | search-result title (producer); **direct PDF read at G1** | data dictionary 26v1 — RESOLVED at G1 (units/null conventions verified, §4.1) |
| E6 | `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change`; `https://github.com/NYCPlanning/db-pluto` (**archived 2023-07-13**; active repo `NYCPlanning/data-engineering`); `https://hub.arcgis.com/datasets/DCP::mappluto-1/about` | search evidence; nyc.gov 403 confirmed twice; ArcGIS REST verified at G1 | DCP page (403-bound), formats (confirmed via `meta_mappluto.pdf`), archive page URL, build pipeline (corrected, C3), ArcGIS endpoint (verified, C4) |
| E7 | `https://dev.socrata.com/docs/app-tokens` | live fetch (re-verified verbatim at G1) | app-token-optional throttling model, X-App-Token header, HTTP 429 |

Post-G1 additions (verified by the G1 reviewer 2026-07-16; full URL index in `project-control/reports/M1-T001-G1-verification.md` §7): `meta_mappluto.pdf` (MapPLUTO 26v1 Shoreline Clipped metadata), MAPPLUTO FeatureServer REST endpoint, `catalog.data.gov` MapPLUTO entry, `opendata.cityofnewyork.us/overview` terms, Socrata catalog API (no tabular MapPLUTO; `qt5r-nqxp` change file), BYTES archive page URL.
