# M1-T003 — Producer report (official-source-researcher)

- **Task:** M1-T003 — Official-source research: NYC GIS Zoning Features + Zoning Tax Lot Database
- **Producer:** official-source-researcher
- **Date:** 2026-07-16 (all retrievals)
- **Status requested:** `awaiting_gate` (G1 data-contract-verifier live re-verification + G3)
- **Report path:** `project-control/reports/M1-T003-producer-report.md`

## 1. Deliverables produced (only files written; no existing file modified)

1. `docs/research/zoning-features-ztldb-2026-07-16.md` — full findings: executive summary, S1–S5 sections, fixture-pack proposal (12 ZTLDB + 10 zoning-features fixtures), 11-item OPEN QUESTIONS ledger, source register Z1–Z14 with per-evidence URLs.
2. `docs/research/source-registry-drafts/zoning-features.json` — 2 records (ArcGIS primary channel; Socrata FileGDB blob snapshot channel), all 18 PRD §8.2 fields, open_questions arrays.
3. `docs/research/source-registry-drafts/ztldb.json` — 1 record (SODA `fdkv-4t4z`), all 18 fields, health_status `degraded_suspected` with evidence.

## 2. Scenario evidence (S1–S5)

### S1 (normal) — channel enumeration, every channel live-evidenced
- Socrata catalog API searched 4 ways (`q=zoning`, `zoning features`, `"Zoning GIS Data"`, `zoning shapefile`) → dataset IDs pinned by ID + attribution: **`fdkv-4t4z`** (ZTLDB, tabular) and **`mm69-vrje`** (Zoning GIS Data: Geodatabase, blobby; blob `nycgiszoningfeatures_fgdb.zip`, 3,298,048 bytes).
- SODA verified live: `resource/fdkv-4t4z.json?$limit=1` returned verbatim record `{"borough_code":"1","tax_block":"1","tax_lot":"10","bbl":"1000010010","zoning_district_1":"R3-2","zoning_district_2":"C4-1","special_district_1":"GI","zoning_map_number":"16A","zoning_map_code":"Y"}`; `$select=count(bbl)` → `857951`.
- ArcGIS: item search `owner:DCP_GIS AND title:zoning` bound nyzd/nyzma items to `services5.arcgis.com/GfwWNkhOj9bNBqoJ`; **all six services fetched live** (nyzd, nyco, nysp, nysp_sd, nylh, nyzma — service roots + layer 0 schemas + sample/count queries). Nothing asserted from memory; the four hypothesized service names came from the official attachment file names and were each confirmed by live fetch.
- data.gov mirrors fetched for both products (cross-channel corroboration).
- No shapefile or per-layer Socrata datasets found (absence documented, OQ-2).

### S2 (boundary) — version/release model
- Verbatim cadence from the official nyzd metadata PDF (direct 4-page read from s-media): *"The downloadable zoning data will be updated on the last Monday of every month."* ZTLDB: *"updated on a monthly basis"* (Socrata description + dictionary).
- Versioning: zoning features = YYYYMM ("Current version: 202604" verbatim in `mm69-vrje` description); ZTLDB pinned by dictionary SOURCE DATASETS (DTM 2026-06-09 + Zoning Features 2026-05-20); ArcGIS carries no label — all six layers observed dataLastEditDate 2026-07-01.
- PLUTO relationship documented: GIS Zoning Features → ZTLDB → PLUTO monthly zoning-attribute minors; PLUTO 26v1 input "NYC GIS Zoning Features 2026-03-31" matches the nyzd metadata vintage (citation 3/31/2026, adoptions through 3/26/2026).

### S3 (missing/ambiguous) — fields, units, CRS, split lots
- ZTLDB: authoritative 16-column inventory from the `api/views` columns array + the official data dictionary **read directly, all 11 pages** (s-media). Split-lot representation fully documented verbatim: ZD1–4 ordered by descending percentage of lot area; 10% feature-assignment rule; overlay 10%-of-lot OR 50%-of-overlay rule; SD '/' tie rule; PARK caveat; ZD1 <10% underwater-lot logic change (2019-12-31); blank semantics; appendices A–D value domains.
- CRS: EPSG:2263 (wkid 102718/latestWkid 2263) verified on all six live services AND in the official nyzd metadata; ±20 ft horizontal accuracy statement captured.
- Schema was never inferred from record keys; the live sample's omitted-blank-keys behavior is documented as a hazard.
- All unknowns ledgered (11 OQs), none guessed.

### S4 (conflict) — cross-channel discrepancies
1. **ZTLDB Socrata stall:** rows last updated 2026-04-05 (raw 1775414816) vs Monthly/Automation=Yes; corroborated by data.gov (checked 2026-07-07, still April 5); DCP's own dictionary references June 2026 sources → bulk channel ahead of SODA. Priority order + mandatory staleness guard recommended.
2. **Zoning-features blob lag:** Socrata description "Current version: 202604" vs ArcGIS layers edited 2026-07-01; blobby timestamps frozen at 2013-01-29.
3. **Documentation defects recorded:** dictionary BBL example typo (5158287501 vs Socrata's corrected 3158287501); "two character borough code" vs 1-char max length; nysp_sd description references nonexistent SUBSUB attribute; corrupted nysp_sd copyright string.
4. Recommended PRD §8 priority order per product is in report §5.5 (ArcGIS primary for geometries; SODA primary for ZTLDB with cross-checks).

### S5 (failure) — bot-protected/dead endpoints
- `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features` → **HTTP 403 Forbidden**, recorded live 2026-07-16 (URL authenticity established independently via the `mm69-vrje` description link). Other nyc.gov page URLs left as search-evidenced **[NEEDS G1 RE-VERIFICATION]**; no download URLs guessed (OQ-1/OQ-2).
- Socrata attachment API served the ZTLDB dictionary as `application/octet-stream` (summarizer-unparseable); worked around via the s-media copy of the same document (direct PDF read) — both channels documented.

## 3. Exact fetches (all 2026-07-16, producer session)

Socrata catalog ×4; `api/views/fdkv-4t4z.json` ×2; `resource/fdkv-4t4z.json?$limit=1`; `?$select=count(bbl)`; `api/views/mm69-vrje.json` ×2; ArcGIS services directory; ArcGIS item search; six `FeatureServer?f=pjson`; six `FeatureServer/0?f=pjson`; `nyzd/0/query` (sample, count); `nyco/0/query` (count); s-media `zoningtaxlotdatabase_datadictionary.pdf` (11 pages read); s-media `nyzd_metadata.pdf` (4 pages read); nyc.gov gis-zoning-features (403); `catalog.data.gov` ×2; WebSearch ×3. Full URL register with per-evidence usage: report §9 (Z1–Z14).

## 4. Tool denial disclosure

- Mid-task, a `Bash` invocation (file copy of the fetched PDF + python epoch conversions) was **permission-denied**: "Permission to use Bash has been denied." Prior to the denial, one python run machine-converted the four key Socrata timestamps (1375120531, 1775414816, 1720205634, 1359482950 → §2 of the findings doc). After the denial: PDFs were read via the Read tool on the WebFetch-saved files (no shell needed), and the eight ArcGIS epoch-ms values were converted by manual arithmetic anchored to the machine-verified 1775414816 = 2026-04-05T18:46:56Z. These manual conversions are flagged **OQ-9** for G1 spot-check. The denial did not block any deliverable; status remains `awaiting_gate`, not `blocked`.

## 5. Assumptions

None. Every unknown is in the OQ ledger (11 items); the only inferential step taken — probing the four unverified ArcGIS service names derived from official attachment file names — was converted to fact by live fetches before use.

## 6. Limitations

- nyc.gov page contents (download file names, shapefile variant, archive listing) unverifiable from this environment (403) — OQ-1/OQ-2.
- Five of six layer metadata PDFs not content-extracted (existence + assetIds verified) — OQ-5.
- Feature counts captured for nyzd/nyco only; nysp/nysp_sd/nylh/nyzma counts deferred to connector build.
- ZTLDB staleness root cause not determinable from public metadata — OQ-3.
- No dataset downloads performed (low-storage rule); local footprint of this task: two WebFetch-cached PDFs (~430 KB) in the session tool-results cache, zero repo binaries.

## 7. Security/provenance impact

Research-only; no code, secrets, or schema changes. Findings materially affect provenance design: ZTLDB has no per-record version field; ArcGIS has no version label; both need derived version stamping — recorded in the registry drafts.

## 8. Recommended follow-up tasks

1. Browser-capable capture of the two BYTES pages (closes OQ-1/OQ-2; same session can close M1-T001 OQ-4/OQ-10 residuals).
2. Monthly-boundary observation job (late July 2026): does `fdkv-4t4z` rowsUpdatedAt move on/after the last Monday (2026-07-27)? Does `mm69-vrje` description advance past 202604? (OQ-3/OQ-4.)
3. Connector-build tasks per §7 of the findings doc (zoning-features-arcgis importer; ztldb-soda connector with staleness guard; conflict-engine three-way zoning cross-check).
4. Extraction pass over the five remaining layer metadata PDFs (OQ-5, OQ-7).
