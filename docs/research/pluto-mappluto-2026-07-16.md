# M1-T001 — Official-Source Research: PLUTO / MapPLUTO

- **Task:** M1-T001 — Official-source research: PLUTO / MapPLUTO
- **Producer agent:** official-source-researcher
- **Retrieval date for all sources:** 2026-07-16 (unless noted)
- **Evidence basis:** This report is written from orchestrator-captured evidence in `project-control/reports/M1-T001-fetch-evidence.md` (sections E1–E7, all fetched/searched live on 2026-07-16), per the ADR-005 / 2026-07-15 evidence-capture directive, because the producer sandbox denied all network tools (see `project-control/reports/M1-T001-producer-report.md` §3 history). Each claim below cites the evidence section (E1–E7) plus the underlying official URL.
- **Discipline:** Claims that come only from a search-result summary or a summarizer paraphrase — rather than a verbatim quote or a directly read document — are marked **[NEEDS G1 RE-VERIFICATION]**. Nothing unverified is presented as fact. Anything unknown is listed in §8 Open Questions.

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
  - The evidence's summarizer reported "Last Updated: August 26, 2026 / Publication Date: July 30, 2026" — **future-dated relative to the retrieval date; almost certainly a misconversion of raw unix timestamps.** **[NEEDS G1 RE-VERIFICATION]** — read `createdAt` / `rowsUpdatedAt` / `publicationDate` directly from the raw JSON (Open Question OQ-1).
- **SODA resource endpoint is live**: `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1` returned a valid JSON record on 2026-07-16 (E2). The record's **`version` field value is `"26v1"`** — the Open Data tabular channel currently serves the same version as the DCP bulk release.
- 73 fields were present on the sampled record (verbatim list in §4.2 below). SODA omits null fields per record, so this is a floor, not the full column set (OQ-2).

### 2.2 NYC Open Data — MapPLUTO entry `f888-ni5f` (VERIFIED, pointer-only)

- Dataset metadata fetch: `https://data.cityofnewyork.us/api/views/f888-ni5f.json` (E3, retrieved 2026-07-16).
  - Name: "Primary Land Use Tax Lot Output - Map (MapPLUTO)"; ID **`f888-ni5f`**; attribution DCP.
  - Description (quoted in E3): "Comprehensive land use and geographic data at the tax lot level in GIS format... merged with tax lot features from the Department of Finance's Digital Tax Map, clipped to shoreline."
  - **viewType/displayType: `href`** — an attachment/external-link entry, **not** a tabular SODA resource. Update frequency metadata: "Quarterly".
  - Attachments listed on the portal: `PLUTODD22v3.pdf`, `PlutoReadme22v3.pdf` — **stale 22v3 documents** while the current release is 26v1 (channel-lag finding, see §5).
  - Raw timestamps: created/rowsUpdated/publication all 1374771826/1374771872 (2013-07-25) — href datasets do not update row timestamps; version currency must come from the DCP channel.
  - The URL the href entry points to was not captured — **[NEEDS G1 RE-VERIFICATION]** (OQ-9).

### 2.3 DCP bulk release — README and data dictionary PDFs (VERIFIED for README; dictionary URL search-verified)

- **Official PLUTO README 26v1** directly fetched and read (pages 1–8): `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_readme.pdf` (342 KB PDF; E4, retrieved 2026-07-16). Header: "PLUTO README DOCUMENT — May 2026 (26v1)". Opening: "The Primary Land Use Tax Lot Output (PLUTO™) data file contains extensive land use and geographic data at the tax lot level in an ASCII comma-delimited file." Fields are derived from data maintained by DCP, DOF, DCAS, and LPC.
- **Official PLUTO data dictionary 26v1**: "PLUTO DATA DICTIONARY May 2026 (26v1)" at `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` (E5). The version+date come from a **search-result title string**, not a direct fetch — **[NEEDS G1 RE-VERIFICATION]** and field-level extraction still to do (OQ-5).

### 2.4 DCP web page and archive (search-evidenced only — bot-protected to this session)

- Current DCP page: `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` (search-result title: "PLUTO, MapPLUTO and PLUTO Change File"); legacy URL `https://www.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page` still resolves in search (E6). **nyc.gov and apps.nyc.gov content-api returned HTTP 403 to the evidence session's WebFetch** (bot protection), so all page-level claims (download links, exact file sizes, archive links) are **[NEEDS G1 RE-VERIFICATION]** (OQ-4).
- MapPLUTO bulk formats, from search summary plus the `meta_mappluto.pdf` title (E6): ESRI shapefile and File Geodatabase; **Shoreline Clipped** (`Mappluto/Mappluto.gdb`) and **Unclipped water-included** (`Mapplutounclipped/Mapplutounclipped.gdb`); a borough shapefile distribution exists. **[NEEDS G1 RE-VERIFICATION]** (search-summary basis).
- Archive: "All previously released versions of this data are available on the DCP Website: BYTES of the BIG APPLE" (E6, search summary). Exact archive URL not captured — **[NEEDS G1 RE-VERIFICATION]** (OQ-4).
- Official build pipeline is open source: `https://github.com/NYCPlanning/db-pluto` with docs at `https://nycplanning.github.io/db-pluto/` (E6, search evidence). **[NEEDS G1 RE-VERIFICATION]** before citing as authoritative for field derivations.

### 2.5 ArcGIS channel (UNVERIFIED)

- An ArcGIS Hub item exists (`https://hub.arcgis.com/datasets/DCP::mappluto-1/about`) but the page is JS-rendered and the underlying feature-service endpoint was **not verified** (E6). Do **not** treat an ArcGIS feature service as an available channel until G1 or a follow-up capture confirms the REST endpoint (OQ-3).

---

## 3. S2 — PLUTO vs MapPLUTO; version scheme; archiving

### 3.1 Product distinction (README 26v1, E4)

- **PLUTO** = attribute file: "extensive land use and geographic data at the tax lot level in an ASCII comma-delimited file" (E4, verbatim).
- **MapPLUTO** = PLUTO + geometry: "City Planning also merges the PLUTO data with the DCP modified version of the DOF's Digital tax map to create MapPLUTO for use with various geographic information systems." (E4, verbatim). The Open Data description adds "merged with tax lot features from the Department of Finance's Digital Tax Map, clipped to shoreline" (E3).

### 3.2 Version scheme and release cadence (README 26v1, E4 — verbatim)

> "There are two types of PLUTO updates: major and minor. Major updates occur quarterly, and all fields are updated. A major update is represented first digit in the version number after 'v', for example 24v1. Minor updates are released monthly between major updates and only include updates to the zoning attributes. A minor release is represented by the decimal after the version number – 24v1.1, 24v1.2, etc."

- Fields updated in **minor (monthly) releases**: ZoneDist1–4, Overlay1–2, SPDist1–3, LtdHeight, SplitZone, ResidFAR, CommFAR, FacilFAR, ZoneMap, ZMCode, TaxMap, EDesigNum (E4).
- **Current version: 26v1** ("May 2026 (26v1)" README header, E4; independently observed as the `version` value in the live SODA record, E2).
- **Change tracking:** "The changes made to a tax lot record are records in PLUTOChangeFile\<ver\>.csv, which is available as part of the MapPLUTO download on BYTES of the BIG APPLE." (E4, verbatim).

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

- Prior versions are stated to be retrievable from the DCP website (BYTES of the BIG APPLE archive) (E6, search summary) — **[NEEDS G1 RE-VERIFICATION]**, exact archive URL not yet captured (OQ-4).

---

## 4. S3 — Fields, units, null semantics, BBL/condo handling

### 4.1 Authoritative data dictionary

- `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` — "PLUTO DATA DICTIONARY May 2026 (26v1)" (E5; title search-verified, **[NEEDS G1 RE-VERIFICATION]** by direct fetch). This is the authoritative reference for per-field definitions, units, and null/placeholder conventions. **Field-level extraction has not yet been performed** — see OQ-5 for the exact field list that requires it. No units are asserted in this report that the captured evidence does not state.

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

**Critical caveat (E2):** the sampled record did **not** surface `zonedist2`–`zonedist4`, `overlay1`–`overlay2`, `spdist1`–`spdist3`, `ltdheight`, `landmark`, `histdist`, `appbbl`, `condono`, etc. — **SODA omits null fields per record**. These fields are known to exist in PLUTO from the README's minor-release field list (E4) and its condo/APPBBL discussion (E4). The full column set must be taken from the `/api/views/64uk-42ks.json` `columns` array and the data dictionary, not from a single record (OQ-2). A connector must never infer schema from record keys.

### 4.3 Null/placeholder conventions (verified so far)

- **NumFloors** (README 26v1, E4, verbatim): "NUMBER OF FLOORS (NumFloors) has been modified to show \<null\> for values of zero and for other values of less than one."
- All other per-field null/placeholder conventions (e.g., YearBuilt=0 handling, LotArea zero/placeholder semantics, borough-code conventions): pending data-dictionary extraction — **not asserted** (OQ-5).

### 4.4 Condominium / billing-BBL semantics (README 26v1, E4, verbatim)

> "PLUTO data contain one record per condominium complex instead of records for each condominium unit tax lot... The Condominium Complex record is assigned the 'billing' tax lot number when one exists. When the 'billing' tax lot number has not yet been assigned by DOF, the lowest tax lot number within the tax block of the Condominium Complex is assigned."

- APPBBL logic changed in the 25v1.1→25v2 range: condo lots without a direct APPBBL now inherit from an associated condo unit lot (E4).
- Consequence for the platform: a user-supplied condo-unit BBL will **not** match a PLUTO record directly; resolution must go through the billing BBL (Geoclient returns `condominiumBillingBbl` — see M0-T002 report §2.6), and record counts per block will differ from DOF unit-lot counts.

### 4.5 Geographic idiosyncrasies (README 26v1, E4)

- **Marble Hill** is legally in Manhattan but serviced by the Bronx; **Rikers Island** is legally in the Bronx but serviced by Queens. Borough-code joins against other datasets must anticipate these.

### 4.6 Coordinates

- The SODA record carries `xcoord`, `ycoord`, `latitude`, `longitude` (E2). The CRS/EPSG for `xcoord`/`ycoord` is **not stated in the captured evidence** and is pending dictionary extraction (OQ-5). (Geosupport uses NAD83 New York–Long Island state plane in feet per the M0-T002 report, and PLUTO 26v1 is built on Geosupport 26A, but the PLUTO dictionary must confirm this for PLUTO's own columns — not asserted here.)

### 4.7 Official disclaimer (README 26v1, E4, verbatim)

> "PLUTO is being provided by the Department of City Planning (DCP) on DCP's website for informational purposes only. DCP does not warranty the completeness, accuracy, content, or fitness for any particular purpose or use..."

---

## 5. S4 — Channel discrepancies and recommended priority order (PRD §8)

### 5.1 Observed cross-channel discrepancies (evidence-based)

1. **Stale portal attachments (channel lag):** the `f888-ni5f` MapPLUTO Open Data entry still lists `PLUTODD22v3.pdf` / `PlutoReadme22v3.pdf` while the current release is 26v1 (E3 vs E4). The Open Data attachment channel for documentation is roughly 3.5 years behind DCP's own site. Current dictionaries live at `s-media.nyc.gov` (E4/E5).
2. **href timestamps are dead:** `f888-ni5f` raw created/rowsUpdated timestamps are frozen at 2013-07-25 (E3) — version currency for MapPLUTO cannot be monitored from Socrata metadata; it must come from the DCP channel (or the per-record `version` field of the PLUTO SODA dataset as a proxy).
3. **Tabular channel is current:** the PLUTO SODA endpoint serves `version = "26v1"` (E2), matching the DCP release (E4) — no version lag observed on the tabular channel on 2026-07-16. Whether monthly **minor** releases (26v1.1, …) propagate to `64uk-42ks`, and how fast, is unobserved (OQ-6).
4. **Suspect Socrata metadata timestamps** on `64uk-42ks` (future-dated summarizer output, E1) — re-verify raw values before using `rowsUpdatedAt` in freshness monitoring (OQ-1).

### 5.2 Recommended priority order (argued from evidence, per PRD §8 tiers)

**PLUTO tabular facts:**
1. **SODA API** — `https://data.cityofnewyork.us/resource/64uk-42ks.json` (PRD tier 2; no tier-1 dedicated API exists for PLUTO). Live, version-current (26v1), filterable per-BBL, and carries the `version` field per record for provenance (E2). Use an **`X-App-Token`** header when available: without a token, requests "are throttled by IP address and share a common pool"; with a token, Socrata does "not throttle API requests... unless those requests are determined to be abusive or malicious"; throttled requests return HTTP 429; token via `X-App-Token` header (preferred) or `$$app_token` param (E7, `https://dev.socrata.com/docs/app-tokens`).
2. **DCP bulk CSV** (PRD tier 3) — for full-city imports and for reproducible version pinning (archive of prior versions), per the README's release model (E4) and the archive statement (E6, [NEEDS G1 RE-VERIFICATION]). Bulk import must run on a Render worker per the low-storage policy; never on the owner's PC.

**MapPLUTO geometry:**
1. **DCP bulk File Geodatabase, shoreline-clipped** (PRD tier 3) — the only verified full-fidelity official channel; there is no tabular SODA resource for MapPLUTO (E3). Clipped vs unclipped variants exist (E6, [NEEDS G1 RE-VERIFICATION] for exact file names/URLs); shoreline-clipped is the appropriate default for zoning-analysis area computations, with the unclipped variant only if riparian-lot edge cases demand it.
2. **ArcGIS feature service** — potential API-tier channel but **unverified** (E6); evaluate at G1/follow-up capture (OQ-3) before it can rank above bulk.
3. **NYC Open Data `f888-ni5f`** — treat strictly as a catalog **pointer**, never as a data or documentation channel (stale attachments, dead timestamps; E3).

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

---

## 7. Connector implementation plan (plan only — no code in this task)

1. **`pluto-soda` connector (facts):** per-BBL and per-block SODA queries against `64uk-42ks` with `X-App-Token` from secrets; store raw record + `version` + retrieval timestamp in `raw_source_records` / `property_source_facts`; schema-drift check against the `api/views` columns array on every scheduled run.
2. **`mappluto-bulk` importer (geometry):** quarterly Render worker job: stream DCP shoreline-clipped FileGDB → bounded temp space → PostGIS (`tax_lot_geometries`) → upload original archive to Supabase Storage (`gis-imports`) → delete temp files (low-storage policy). Version pinned from the release file name + README.
3. **Freshness monitor:** poll SODA `version`; alert on major/minor version change; cross-check against DCP README version at each quarterly boundary.

---

## 8. OPEN QUESTIONS (explicit — nothing below is asserted anywhere above)

| # | Question | Why open | Proposed resolution |
|---|---|---|---|
| OQ-1 | Raw Socrata timestamps (`createdAt`, `rowsUpdatedAt`, `publicationDate`) for `64uk-42ks` | Summarizer reported future-dated values ("Last Updated: August 26, 2026 / Publication Date: July 30, 2026") — implausible vs retrieval date 2026-07-16; likely misconverted unix values (E1) | G1 reviewer reads raw JSON values directly |
| OQ-2 | Full SODA column list for `64uk-42ks` | Single-record sample omits null fields — `zonedist2-4`, `overlay1-2`, `spdist1-3`, `ltdheight`, `landmark`, `histdist`, `appbbl`, `condono` etc. unconfirmed as SODA columns (E2) | Fetch `/api/views/64uk-42ks.json` and enumerate the `columns` array |
| OQ-3 | Official ArcGIS feature-service REST endpoint for MapPLUTO | Hub page is JS-rendered; endpoint never observed (E6) | Follow-up capture from a browser-capable session, or defer; do not use unverified |
| OQ-4 | Exact bulk download URLs, file sizes, and BYTES of the BIG APPLE archive URLs | nyc.gov / apps.nyc.gov content-api returned HTTP 403 to the evidence session (E6) | G1 re-verification via browser or content-api from a permitted network |
| OQ-5 | Field-level units and null/placeholder conventions from the data dictionary — at minimum: `lotarea`/`bldgarea`/`comarea`/`resarea`/`officearea`/`retailarea`/`garagearea`/`strgearea`/`factryarea`/`otherarea` (units), `lotfront`/`lotdepth`/`bldgfront`/`bldgdepth` (units), `assessland`/`assesstot`/`exempttot` (currency basis), `xcoord`/`ycoord` (CRS/EPSG), `yearbuilt`/`yearalter1-2` (zero/placeholder handling), `bldgclass`/`landuse` code lists, `areasource`/`lottype`/`proxcode`/`bsmtcode` code meanings, README-name→SODA-column mapping (e.g., ManuFAR ↔ `mnffar`) | Dictionary located (E5) but only title-verified; no field extraction performed | Follow-up capture task: fetch `pluto_datadictionary.pdf` and extract; or G1 |
| OQ-6 | Do monthly minor releases (26v1.1, …) propagate to the `64uk-42ks` SODA channel, and with what lag? | Not observable from one snapshot | Observe `version` field across a minor-release boundary |
| OQ-7 | Data dictionary direct-fetch confirmation (URL, version header) | E5 is a search-result title string only | Direct fetch at G1 |
| OQ-8 | NYC Open Data portal terms of use for automated access | Only `dev.socrata.com` app-token docs were captured (E7); the NYC-specific terms page was not | Fetch terms page linked from `https://opendata.cityofnewyork.us/` |
| OQ-9 | What URL the `f888-ni5f` href entry points to | Not captured in E3 | Read `metadata.accessPoints`/href from raw `api/views` JSON |
| OQ-10 | MapPLUTO clipped/unclipped exact file names, borough-shapefile availability, `meta_mappluto.pdf` contents | Search-summary basis only (E6) | G1 re-verification with the DCP page |
| OQ-11 | `PLUTOChangeFile<ver>.csv` exact location/format | README states it ships "as part of the MapPLUTO download" (E4); file itself unseen | Inspect at first bulk import |

**Open-question count: 11.**

---

## 9. Source register (all evidence captured 2026-07-16 by the orchestrator; see `project-control/reports/M1-T001-fetch-evidence.md`)

| Evidence | Official URL | Access method | Used for |
|---|---|---|---|
| E1 | `https://data.cityofnewyork.us/api/views/64uk-42ks.json` | live fetch (summarizer-mediated) | PLUTO dataset ID, name, attribution, description; timestamps flagged OQ-1 |
| E2 | `https://data.cityofnewyork.us/resource/64uk-42ks.json?$limit=1` | live fetch, verbatim record | SODA endpoint liveness, `version=26v1`, 73-field sample, null-omission behavior |
| E3 | `https://data.cityofnewyork.us/api/views/f888-ni5f.json` | live fetch | MapPLUTO href-type entry, quarterly, stale 22v3 attachments, dead timestamps |
| E4 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_readme.pdf` | direct PDF read (pages 1–8) | release model, version naming, condo/billing BBL, Marble Hill/Rikers, DATES OF DATA, 26v1 new fields, NumFloors null convention, disclaimer, PLUTOChangeFile |
| E5 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` | search-result title only | data dictionary 26v1 location — [NEEDS G1 RE-VERIFICATION] |
| E6 | `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change`; `https://github.com/NYCPlanning/db-pluto`; `https://hub.arcgis.com/datasets/DCP::mappluto-1/about` | search evidence; nyc.gov 403 to direct fetch | DCP page, formats, archive, build pipeline, ArcGIS item — all [NEEDS G1 RE-VERIFICATION] |
| E7 | `https://dev.socrata.com/docs/app-tokens` | live fetch | app-token-optional throttling model, X-App-Token header, HTTP 429 |
