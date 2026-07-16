# M1-T003 — Official-Source Research: NYC GIS Zoning Features + NYC Zoning Tax Lot Database (ZTLDB)

- **Task:** M1-T003 — Official-source research: NYC GIS Zoning Features + Zoning Tax Lot Database
- **Producer agent:** official-source-researcher
- **Retrieval date for all sources:** 2026-07-16 (unless noted)
- **Evidence basis:** All claims below were verified by the producer via live fetches on 2026-07-16 (Socrata metadata/SODA endpoints, ArcGIS REST services, s-media.nyc.gov PDFs read directly page-by-page, catalog.data.gov mirrors). The evidence register in §9 lists every URL. The producer sandbox had working network tools this run; the only tool denial was a local `Bash` denial mid-task (used for file copy + epoch conversion — see §8 OQ-9 and the producer report §4).
- **Discipline:** Claims that come only from a search-result listing — rather than a live fetch or a directly read official document — are marked **[NEEDS G1 RE-VERIFICATION]**. Nothing unverified is presented as fact. Unknowns are in the §8 OPEN QUESTIONS ledger.

---

## 1. Executive summary

| Product | What it is | Verified distribution channels (2026-07-16) | Current version observed | Recommended role |
|---|---|---|---|---|
| **NYC GIS Zoning Features** | DCP's six citywide zoning polygon feature classes: zoning districts (nyzd), commercial overlay districts (nyco), special purpose districts (nysp), special purpose subdistricts (nysp_sd), limited height districts (nylh), zoning map amendments (nyzma) | **ArcGIS feature services** under verified DCP_GIS org (`services5.arcgis.com/GfwWNkhOj9bNBqoJ`) — all six layers verified live (Z7–Z10); **NYC Open Data blob `mm69-vrje`** "Zoning GIS Data: Geodatabase" (FileGDB zip, 3,298,048 bytes, with all six official layer-metadata PDFs attached) (Z6); DCP BYTES page (nyc.gov — 403, Z12); data.gov mirror (Z13) | ArcGIS: all six layers data-last-edited **2026-07-01** (freshest); Socrata blob description: **"Current version: 202604"** (April 2026) — channel lag, see §5 | **Primary geometry source for zoning districts/overlays/special districts.** Layer sizes are small (nyzd 5,416 features; nyco 9,623), so ArcGIS paged import is feasible as the citywide-import primary — unlike MapPLUTO |
| **NYC Zoning Tax Lot Database (ZTLDB)** | Tax-lot-level zoning assignment table: DOF Digital Tax Map lots × NYC GIS Zoning Features (10%/50% assignment rules), one row per tax lot, 16 columns, CSV | **NYC Open Data tabular dataset `fdkv-4t4z`** with live SODA endpoint (Z2–Z4; 857,951 rows on 2026-07-16); official data dictionary read directly from `s-media.nyc.gov` (Z5); DCP BYTES CSV (nyc.gov — 403-bound); data.gov mirror (Z13) | Socrata rows last updated **2026-04-05** (raw `rowsUpdatedAt` 1775414816) despite "Monthly" cadence; the current s-media dictionary cites source data **DTM 2026-06-09 + Zoning Features 2026-05-20** — the DCP bulk release is newer than the Socrata rows (§5) | **Primary tabular lot→zoning assignment source** (split-lot ordering semantics are official here), consumed via SODA, but with a mandatory freshness cross-check against PLUTO zoning attributes and nyzd spatial intersection because of the observed staleness |

Release cadence (official, verbatim): nyzd metadata PDF (Z11): *"The downloadable zoning data will be updated on the last Monday of every month. Updates will include recent zoning changes adopted by City Council."* ZTLDB Socrata description (Z2): *"The Database is updated on a monthly basis to reflect rezoning and corrections to the file."*

**Product-boundary warning (official, verbatim, Z11):** the zoning-features metadata states *"These features are not intended for determining zoning at the individual tax lot level."* Lot-level zoning assignment is the ZTLDB's job (and PLUTO's, derived from it). The platform must respect this division: geometry product for mapping/split-geometry work; ZTLDB/PLUTO for lot-level district lists; the conflict engine compares all three.

---

## 2. S1 — Distribution channels, identifiers, formats

### 2.1 NYC Open Data — ZTLDB tabular dataset `fdkv-4t4z` (VERIFIED, live)

- Metadata fetch: `https://data.cityofnewyork.us/api/views/fdkv-4t4z.json` (Z2, retrieved 2026-07-16).
  - Name "NYC Zoning Tax Lot Database"; ID **`fdkv-4t4z`**; attribution "Department of City Planning (DCP)"; viewType tabular / displayType table; provenance "official"; category "City Government".
  - Description (verbatim): *"The Zoning Tax Lot Database is a comma-separated values (CSV) file that contains up-to-date zoning by parcel. The Database includes the zoning designations and zoning map associated with a specific tax block and lot. The Database is updated on a monthly basis to reflect rezoning and corrections to the file."*
  - Custom fields: Update Frequency **Monthly**; Data Change Frequency Monthly; Automation **Yes**; Date Made Public 9/13/2021; Agency DCP.
  - Raw timestamps: `createdAt` 1375120531 = 2013-07-29T17:55:31Z; `rowsUpdatedAt` **1775414816 = 2026-04-05T18:46:56Z**; `publicationDate` 1720205634 = 2024-07-05T18:53:54Z (machine-converted before the Bash denial; see §8 OQ-9 for the conversion-method note).
  - Attachment: `zoningtaxlotdatabase_datadictionary.pdf`, assetId `f0b9c61f-bb72-40a0-8ec9-e8a422f4b39a` (Z2).
  - **Full authoritative SODA column inventory: 16 columns** (from the `api/views` columns array, NOT from record keys): `borough_code` (number), `tax_block` (number), `tax_lot` (number), `bbl` (number), `zoning_district_1` … `zoning_district_4` (text), `commercial_overlay_1`, `commercial_overlay_2` (text), `special_district_1` … `special_district_3` (text), `limited_height_district` (text), `zoning_map_number` (text), `zoning_map_code` (text). Portal column descriptions match the official dictionary (§4) except one example discrepancy noted in §5.4.
- **SODA resource endpoint live** (Z3): `https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$limit=1` returned on 2026-07-16 (verbatim):
  `[{"borough_code":"1","tax_block":"1","tax_lot":"10","bbl":"1000010010","zoning_district_1":"R3-2","zoning_district_2":"C4-1","special_district_1":"GI","zoning_map_number":"16A","zoning_map_code":"Y"}]`
  — a live split-lot example (ZD1+ZD2 present) in the Special Governors Island District (GI per Appendix A, Z5). **SODA omits blank fields per record** (no `commercial_overlay_*`, `limited_height_district`, `zoning_district_3/4`, `special_district_2/3` keys on this record) — schema must come from the columns array/dictionary, never record keys. Number-typed columns serialize as JSON strings (`"bbl":"1000010010"`).
- **Row count live** (Z4): `?$select=count(bbl)` → `[{"count_bbl":"857951"}]` (2026-07-16).
- There is **no per-record version field** in ZTLDB (unlike PLUTO's `version` column). Freshness monitoring must use `rowsUpdatedAt` — which is precisely the signal showing the staleness problem in §5.1.

### 2.2 NYC Open Data — Zoning GIS Data: Geodatabase `mm69-vrje` (VERIFIED, blob + official metadata attachments)

- Metadata fetch: `https://data.cityofnewyork.us/api/views/mm69-vrje.json` (Z6, retrieved 2026-07-16, description re-fetched verbatim):
  - Name "Zoning GIS Data: Geodatabase"; ID **`mm69-vrje`**; attribution DCP; **viewType `blobby` / displayType `blob`** — a downloadable file, not a SODA resource.
  - Description (verbatim): *"This data set consists of 6 classes of zoning features: zoning districts, special purpose districts, special purpose district subdistricts, limited height districts, commercial overlay districts, and zoning map amendments. All previously released versions of this data are available on the \<a href="https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features"\>DCP Website: BYTES of the BIG APPLE\</a\>. **Current version: 202604**"*
  - Blob: `nycgiszoningfeatures_fgdb.zip`, **3,298,048 bytes** (~3.15 MB — the entire citywide zoning-features FileGDB is only ~3 MB; the low-storage constraint is not stressed by this product).
  - Custom fields: Update Frequency Monthly; Data Change Frequency Monthly; Automation Yes; Date Made Public 9/13/2021.
  - Raw timestamps: createdAt = rowsUpdatedAt = publicationDate = **1359482950 = 2013-01-29T18:09:10Z** — frozen; blobby datasets do not update row timestamps. Version currency must be read from the description string ("Current version: 202604") or the DCP/ArcGIS channels.
  - **Attachments — the six official per-layer metadata PDFs with assetIds** (Z6): `nyzd_metadata.pdf` (ee770e89-09d9-4b47-b0e1-8f543da5dbff), `nyco_metadata.pdf` (f1459cd0-eb93-4085-9bf7-e7198765637e), `nysp_metadata.pdf` (f11a7a91-0dbc-4e39-9c46-6366a4c216ab), `nysp_sd_metadata.pdf` (0ff3fd30-3fee-400f-920d-03435b7b55e0), `nylh_metadata.pdf` (f83f6f43-7538-46d2-871e-c9b6ed82f13b), `nyzma_metadata.pdf` (8d4c40d4-6990-417b-8724-7925ffa9a7b1). These same PDFs are hosted on `s-media.nyc.gov` (nyzd verified by direct read, Z11).
- **No shapefile or per-layer Socrata dataset was found.** Four catalog searches (`q=zoning`, `q=zoning features`, `q="Zoning GIS Data"`, `q=zoning shapefile`; Z1) surfaced no "Zoning GIS Data: Shapefile" and no standalone Zoning Districts / Commercial Overlay / Special Purpose / Limited Height Socrata datasets. A shapefile variant presumably exists on the BYTES page (403-bound) — OQ-2; not asserted.
- Related-but-distinct DCP Socrata entries seen during enumeration (not in scope, recorded for M2): Transit Zones `6ztr-wgff`, Appendix I Transit Zones `dpnc-b2hd`, Greater Transit Zone `vhqf-adkz`, Georeferenced NYC Zoning Maps `mxbm-493w` (raster), Zoning Map Index Section `bpt7-i8t8` / Quartersection `58k2-kgtb`, E-Designations shapefile `mzjp-98aw` (Z1).

### 2.3 ArcGIS feature services — DCP_GIS org (VERIFIED, all six layers live)

ArcGIS Online item search scoped to the M1-T001-verified org owner (Z7): `owner:DCP_GIS AND title:zoning` returned "Zoning Districts (NYZD)" (item 788dcf4c61e34757bad1e015cb5f4111) and "Zoning Map Amendments (NYZMA)" (item d432de08f4f5477db101bb2f3dbe1f65), both owner **DCP_GIS**, pointing at `services5.arcgis.com/GfwWNkhOj9bNBqoJ`. The remaining four service URLs were hypothesized from the official layer names on the `mm69-vrje` attachments (nyco, nysp, nysp_sd, nylh) and **each was verified by a live service fetch** (Z8) — none of the six is asserted from memory:

| Layer | Service root (all `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/...`) | Live? | Geometry | SR (wkid/latestWkid) | maxRecordCount | Feature count (live) | dataLastEditDate (raw ms) |
|---|---|---|---|---|---|---|---|
| Zoning districts | `nyzd/FeatureServer` (layer 0 "nyzd") | YES | polygon | 102718 / **2263** | 2000 | **5,416** (Z10) | 1782912288115 ≈ 2026-07-01T13:24:48Z |
| Commercial overlays | `nyco/FeatureServer` (layer 0 "nyco") | YES | polygon | 102718 / 2263 | 2000 | **9,623** (Z10) | 1782912829636 ≈ 2026-07-01T13:33:49Z |
| Special purpose districts | `nysp/FeatureServer` (layer 0 "nysp") | YES | polygon | 102718 / 2263 | **92** | not queried | 1782912605345 ≈ 2026-07-01T13:30:05Z |
| Special purpose subdistricts | `nysp_sd/FeatureServer` (layer 0 "nysp_sd") | YES | polygon | 102718 / 2263 | **317** | not queried | 1782912514806 ≈ 2026-07-01T13:28:34Z |
| Limited height districts | `nylh/FeatureServer` (layer 0 "nylh") | YES | polygon | 102718 / 2263 | **14** | not queried | 1782912700015 ≈ 2026-07-01T13:31:40Z |
| Zoning map amendments | `nyzma/FeatureServer` (layer 0 "nyzma") | YES | polygon | 102718 / 2263 | 1292 | not queried | 1782912214592 ≈ 2026-07-01T13:23:34Z |

- All six layers were data-last-edited on **2026-07-01 between ~13:23 and ~13:34 UTC** — a coordinated refresh consistent with the monthly release model. (Epoch→UTC conversions for these eight ms values were done manually after the Bash denial, anchored to a machine-verified timestamp; flagged for G1 spot-check, OQ-9.)
- Live data check (Z10): `nyzd/FeatureServer/0/query?where=ZONEDIST='R3-2'&outFields=*&resultRecordCount=1&f=pjson` returned OBJECTID 86, `ZONEDIST "R3-2"`, Shape__Area 837150.68…, Shape__Length 4012.05…, polygon rings present, SR 102718/2263, units esriFeet.
- The `maxRecordCount` values (92/317/14 on the small layers) are per-request page caps; with counts of 5,416 (nyzd) and 9,623 (nyco), **full-layer paged extraction is a handful of requests per layer** — the ArcGIS channel can serve as the citywide-import primary for this product, unlike MapPLUTO (~850k lots).
- Also observed in the services directory (Z8/Z7): `v_Zoning_Districts_NYZD` (a view service, item modified ≈2024-08-06) and various neighborhood rezoning one-offs — **not** the canonical layers; connectors must pin to the six canonical service names above.

### 2.4 Official documentation PDFs (VERIFIED, direct reads)

- **ZTLDB data dictionary** — read directly, all 11 pages (Z5): `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/zoningtaxlotdatabase_datadictionary.pdf` (251 KB; identical file also attached on `fdkv-4t4z`, 264.5 KB served via the Socrata attachment API with content-type octet-stream). Title "ZONING TAX LOT DATABASE" / running header "ZONING TAX LOT DATA DICTIONARY". Contents in §3–§4.
- **nyzd layer metadata** — read directly, all 4 pages (Z11): `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf` (178.4 KB). "Zoning Districts (NYZD)", type "File Geodatabase Feature Class". Contents in §3–§4.
- The other five layer metadata PDFs are **verified to exist** as `mm69-vrje` attachments (assetIds above); their contents were not extracted in this task (OQ-5).

### 2.5 DCP BYTES of the BIG APPLE pages (403-bound — recorded, not guessed)

- `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features` — **HTTP 403 Forbidden recorded live on 2026-07-16** (Z12). This URL is nonetheless confirmed official because the `mm69-vrje` description links to it verbatim (Z6).
- `https://www.nyc.gov/site/planning/data-maps/open-data/dwn-gis-zoning.page` (legacy) — search-evidenced only **[NEEDS G1 RE-VERIFICATION]** (Z14).
- `https://www.nyc.gov/content/planning/pages/resources/datasets/zoning-taxlot-database` (ZTLDB page) — search-evidenced only **[NEEDS G1 RE-VERIFICATION]** (Z14).
- Exact BYTES download file URLs, shapefile variant names, and archive listing: OQ-1/OQ-2 (browser-capable session needed; consistent with M1-T001's nyc.gov experience).

### 2.6 data.gov mirrors (VERIFIED, cross-channel checks)

- `https://catalog.data.gov/dataset/zoning-gis-data-geodatabase` (Z13): mirrors `mm69-vrje`; "represents version 202604"; catalog last checked **2026-05-26**; harvested resource URL `https://data.cityofnewyork.us/download/mm69-vrje/application/zip` (the direct Socrata blob download endpoint).
- `https://catalog.data.gov/dataset/nyc-zoning-tax-lot-database` (Z13): mirrors `fdkv-4t4z`; "Last Updated: April 5, 2026"; **last checked 2026-07-07 at 9:22 PM** — independent corroboration that the Socrata ZTLDB rows were still at the 2026-04-05 state in July (§5.1).

---

## 3. S2 — Version/release model, cadence, and relationship to PLUTO

### 3.1 Cadence (official verbatim)

- nyzd metadata (Z11), Legal constraints: *"Notice To Users: 1. Zoning data changes frequently! The downloadable zoning data will be updated on the last Monday of every month. Updates will include recent zoning changes adopted by City Council. 2. These features are not intended for determining zoning at the individual tax lot level."* Resource Maintenance: *"Update frequency: monthly"*. Summary: *"Zoning districts for New York City. Data is updated monthly."*
- ZTLDB (Z2/Z5): *"The Database is updated on a monthly basis to reflect rezoning and corrections to the file."* Socrata custom fields: Update Frequency Monthly, Automation Yes.

### 3.2 Versioning model

- The zoning-features product is versioned as **YYYYMM** (observed: "Current version: 202604" in the `mm69-vrje` description, Z6; data.gov echoes "version 202604", Z13). Previous versions archived on BYTES (description verbatim, Z6).
- The **ArcGIS channel carries no version label**; its freshness signal is `editingInfo.dataLastEditDate` per layer (all 2026-07-01 as of retrieval — implying the ArcGIS channel is at least at the June-2026 cycle while the Socrata blob description still says 202604; §5.2, OQ-6).
- ZTLDB releases are pinned by the **SOURCE DATASETS block of the dictionary** (Z5, verbatim): *"Department of Finance Digital Tax Map — June 9, 2026; Department of City Planning NYC GIS Zoning Features — May 20, 2026."* There is no version string in the data itself.

### 3.3 Derivation chain and PLUTO relationship

- ZTLDB OVERVIEW (Z5, verbatim): *"The Zoning Tax Lot Database contains all tax lots from the specified version of the Department of Finance's Digital Tax Map. For each tax lot, it specifies the applicable zoning district(s), commercial overlay(s), special purpose district(s), and other zoning related information."* … *"The zoning features are taken from the Department of City Planning NYC GIS Zoning Features."*
- PLUTO's monthly **minor** releases update only zoning attributes (ZoneDist1–4, Overlay1–2, SPDist1–3, LtdHeight, SplitZone, FAR fields, ZoneMap, ZMCode, TaxMap, EDesigNum) — M1-T001 accepted finding (README 26v1). PLUTO 26v1's DATES OF DATA lists input **"NYC GIS Zoning Features 2026-03-31"**, and the nyzd metadata PDF is exactly that vintage: citation creation/publication date 3/31/2026, *"The date of the most recent City Council adoptions included in this data is 3/26/2026"*, metadata last update 2026-04-09 (Z11).
- Chain for the platform: **GIS Zoning Features (monthly, last Monday) → ZTLDB (monthly, DTM × features with 10%/50% rules) → PLUTO zoning attributes (monthly minor releases)**. Each stage lags its input; the conflict engine must treat the three as distinct vintages of the same underlying facts.
- ZTLDB change history (Z5) records methodology changes the connector must know: 2018-09-07 methodology aligned with NYC GIS Zoning Features; parkland consolidated to a single **PARK** value (from PARK / BALL FIELD / PLAYGROUND / PUBLIC SPACES features) with the explicit caveat *"The NYC GIS Zoning Features do not constitute a definitive list of parks in the city. Lots designated as PARK should not be used to calculate the amount of open space in an area"*; special-district abbreviations aligned with GIS Zoning Features. 2019-12-31: **Zoning District 1 logic change** — *"In previous versions, Zoning District 1 was blank if no zoning district covered at least 10% of the lot area. Starting with this version, the zoning district classification occupying the greatest percentage of a tax lot's area is assigned to Zoning District 1, even if the percentage is under 10%"* (large mostly-underwater lots). 2020-07-31: temporary `Notes` field (Inwood rezoning litigation) removed.

---

## 4. S3 — Fields, units, CRS, null semantics, split-lot representation

### 4.1 ZTLDB field inventory (official dictionary, direct read, Z5 — cross-checked against the Socrata columns array, Z2)

| # | Field (dictionary) | SODA column | Max len | Data source (verbatim) | Key semantics (verbatim basis) |
|---|---|---|---|---|---|
| 1 | Borough Code | `borough_code` | 1 char | DOF Digital Tax Map | 1=MN 2=BX 3=BK 4=QN 5=SI. Marble Hill legally Manhattan (code 1); Rikers legally Bronx (code 2) — legal borough governs. (Dictionary body says "two character borough code" while Maximum Length is "1 character" — internal doc inconsistency, §5.4) |
| 2 | Tax Block | `tax_block` | 5 | DOF DTM | unique within borough |
| 3 | Tax Lot | `tax_lot` | 4 | DOF DTM | unique within block |
| 4 | BBL | `bbl` | 10 | DOF DTM | borough code + block zero-padded to 5 + lot zero-padded to 4. *"For condominiums, the BBL is for the billing lot"* (Socrata column description; the PDF's Brooklyn example contains a typo — §5.4) |
| 5–8 | Zoning District 1–4 | `zoning_district_1..4` | 9 each | DCP NYC Zoning Districts | **Split-lot representation:** ZD1 = classification occupying the **greatest percentage of the lot's area** (since 2019-12-31, even if <10%); ZD2/3/4 = second/third/fourth greatest. *"If the tax lot is not divided by a zoning boundary line, the field is blank"* (ZD2; analogous blanks for ZD3/ZD4). PARK consolidation caveat applies. Values: Appendix B — R1-1–R10H residential, C1-6–C8-4 commercial, M1-1–M3-2A manufacturing, M1-1/R5–M1-9A/R12 mixed M/R, BPC, PARK |
| 9–10 | Commercial Overlay 1–2 | `commercial_overlay_1..2` | 4 each | DCP NYC Commercial Overlay Districts | assignment rule (verbatim): *"The commercial overlay district must either cover at least 10% of a tax lot's area or at least 50% of the commercial overlay district must be contained within the tax lot."* CO1 = greatest percentage, CO2 = second. Valid values (Appendix C, verbatim): C1-1…C1-5, C2-1…C2-5 |
| 11–13 | Special District 1–3 | `special_district_1..3` | 6 each | DCP NYC Special Purpose Districts (Zoning) | SD1 = greatest percentage of lot area; **tie/overlap rule (verbatim):** *"If the greatest percentage is occupied by two special purpose districts that overlap each other and cover the same percentage of the lot, Special District 1 contains the abbreviation for both special purpose districts, with the abbreviations separated by '/'."* (same for SD2). Abbreviations: Appendix A (125th, AAM, BNY, BPC, …, GI, …, WP — full table in the PDF) |
| 14 | Limited Height District | `limited_height_district` | 5 | DCP NYC Limited Height Districts (Zoning) | symbols per Appendix D: LH-1, LH-1A (Upper East Side), LH-2*, LH-3* — *"There are currently no districts with these designations"* (LH-2/LH-3) |
| 15 | Zoning Map Number | `zoning_map_number` | 3 | DCP Quartersection Map Index | zoning map associated with the lot |
| 16 | Zoning Map Code | `zoning_map_code` | 1 | DCP Quartersection Map Index | verbatim: *"A code 'Y' indicates that the tax lot may be on the border of two or more Zoning Maps. If the Lot is on the border of two or more Zoning Maps the map number identified in Zoning Map Number is one of the potential Zoning Maps associated with the Tax Lot."* |

**Zoning-feature assignment threshold (OVERVIEW, verbatim, Z5):** *"DCP assigns a zoning feature (includes zoning districts, special districts, and limited height districts) to a tax lot if 10% or more of the tax lot is covered by the zoning feature. For commercial overlays, a tax lot is assigned a value if 10% or more of the tax lot is covered by the commercial overlay and/or 50% or more of the commercial overlay feature is within the tax lot."*

**Null semantics:** blanks mean "not applicable / not split further" (explicit for ZD2–4: not divided by a zoning boundary line). On the SODA channel, blank fields are **omitted keys** on the record (observed live, Z3). No sentinel values documented.

### 4.2 GIS Zoning Features field inventories (live layer schemas, Z9; nyzd semantics from official metadata, Z11)

- **nyzd:** OBJECTID (OID), **ZONEDIST** (String 15 — *"Zoning district designation"*, Z11), Shape__Area, Shape__Length (Double, "internal units" = feet per SR). Service description (verbatim, Z8): *"Polygon features representing the zoning districts. These features are continuous over the entire city. They extend to the city limits on land and out to the US Army Corps of Engineers Pierhead lines over water. Zoning district designations are indicated in the ZONEDIST attribute."*
- **nyco:** OBJECTID, **OVERLAY** (String 15, alias "Commercial Overlay"), Shape__Area/Length. Description (verbatim): *"Polygon features representing the within-tax-block limits for commercial overlay districts, as shown on the DCP zoning maps. Commercial overlay district designations are indicated in the OVERLAY attribute."*
- **nysp:** OBJECTID, **SDNAME** (String 255), **SDLBL** (String 10), Shape__Area/Length. Description: *"…The district designation is indicated in the SDNAME attribute. The abbreviation as shown on the zoning map is indicated in the SDLBL attribute."*
- **nysp_sd:** OBJECTID, **SPNAME** (255), **SPLBL** (10), **SUBDIST** (50), **SUB_AREA_NM** (50), **SUBDIST_LBL** (50), **SUBAREA_LBL** (50), **SUBAREA_OTR** (50), Shape__Area/Length. Description: *"This feature class contains only the internal subdistricts of any special purpose districts that are so subdivided. The main special purpose district name is indicated by the SPNAME attribute, the SUBDIST attribute contains the subdistrict name. Any further subdistrict divisions are named in the SUBSUB attribute."* (Note: description mentions SUBSUB; live schema exposes SUBAREA_* fields — naming drift between description and schema, §5.4.)
- **nylh:** OBJECTID, **LHNAME** (50), **LHLBL** (10), Shape__Area/Length. Description: *"Polygon features representing the Limited Height Districts."*
- **nyzma:** OBJECTID, **EFFECTIVE** (esriFieldTypeDate), **STATUS** (String 15), **ULURPNO** (String 50), **LUCATS** (String 10), **PROJECT_NAME** (String 100), Shape__Area/Length. Description: *"Outlines for all zoning changes adopted and proposed since January 1, 2002. Includes outlines for current Certified rezonings."* — directly relevant to the PRD's pending-land-use-action flags (value domains: OQ-7).

### 4.3 CRS and accuracy (official metadata, Z11 + live services, Z8)

- nyzd metadata Spatial Reference (verbatim fields): Projected, `NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet`, **WKID 102718, latestWkid 2263**, reference system identifier **2263 (EPSG)**. All six live services report the same 102718/2263; query response units `esriFeet`. Identical to MapPLUTO (M1-T001) — no reprojection needed between the two products at import.
- Positional accuracy (Z11, Data Quality): *"The data were developed using DCP's Tax Block Base Map Files, DOITT's NYC Map planimetric street centerlines and 2006 orthophotos as reference sources. Measurements and dimensions for location of zoning features were obtained from DCP zoning maps. The estimated horizontal accuracy is +/- 20 feet."* (± rendering per PDF extraction; glyph-exactness flagged OQ-10.) **A ±20 ft boundary tolerance is material for split-lot edge determinations** — the rules engine must treat near-boundary intersections as uncertain rather than authoritative.
- nyzd metadata also records: distribution format "File Geodatabase Feature Class"; resource status "under development"; processing environment ArcGIS 10.6; source metadata format fgdc.

### 4.4 Disclaimers (verbatim)

- ZTLDB (Z5): *"The Zoning Tax Lot Database is being provided by the Department of City Planning (DCP) on DCP's website for informational purposes only. DCP does not warranty the completeness, accuracy, content, or fitness for any particular purpose or use of the Zoning Tax Lot Database, nor are any such warranties to be implied or inferred with respect to the Zoning Tax Lot Database as furnished on the website."*
- Zoning features (Z11): same DCP informational-purposes-only formula, plus use limitations 1–2 quoted in §1/§3.1.

---

## 5. S4 — Cross-channel discrepancies and recommended PRD §8 priority order

### 5.1 ZTLDB Socrata staleness vs monthly cadence (STRONGEST FINDING)

- Socrata `rowsUpdatedAt` = 2026-04-05T18:46:56Z (Z2) while the stated cadence is **Monthly** with Automation Yes; retrieval date 2026-07-16 → the tabular channel is **~3.4 months stale**.
- Independent corroboration: data.gov's harvester last checked 2026-07-07 and still records "Last Updated: April 5, 2026" (Z13).
- Meanwhile the **current s-media dictionary** cites source data DTM **2026-06-09** + Zoning Features **2026-05-20** (Z5) — i.e., DCP has produced at least one newer ZTLDB release (≈June 2026) that has **not** reached the Socrata rows. The DCP bulk channel is ahead of the Socrata channel.
- Consequence: a connector reading only `fdkv-4t4z` today would serve zoning assignments that can be one or more City Council rezonings behind (e.g., anything adopted after ~March 2026). The freshness monitor must alert on `rowsUpdatedAt` age > ~45 days, and the conflict engine must cross-check ZTLDB values against PLUTO zoning attributes and a live nyzd spatial intersection. Root cause of the stall: OQ-3.

### 5.2 Zoning-features channel lag (ArcGIS ahead of Socrata blob)

- ArcGIS: all six layers data-last-edited **2026-07-01** (Z8/Z9). Socrata `mm69-vrje` description: **"Current version: 202604"** (Z6); data.gov last checked 2026-05-26 still 202604 (Z13). The Socrata blob channel appears 2–3 monthly cycles behind the ArcGIS channel as of 2026-07-16 — OR the description string is not maintained per release while the blob silently updates (blobby timestamps are frozen at 2013, so Socrata metadata cannot distinguish these cases). OQ-4.
- The s-media/attachment `nyzd_metadata.pdf` is itself the **2026-03-31 vintage** (metadata last update 2026-04-09) — official documentation lags the live data by design; per-release currency must come from the data channels, not the metadata PDFs.

### 5.3 Frozen/absent version signals per channel

| Channel | Version signal | Status |
|---|---|---|
| ArcGIS services | none (no version field); `editingInfo.dataLastEditDate` only | freshest observed data; version label must be *derived* (OQ-6) |
| Socrata `mm69-vrje` | "Current version: YYYYMM" inside free-text description; blob timestamps frozen 2013 | weak, possibly stale signal (OQ-4) |
| Socrata `fdkv-4t4z` | `rowsUpdatedAt` only; **no per-record version column** | observed stale (§5.1) |
| s-media dictionary | SOURCE DATASETS dates | authoritative for the current DCP bulk release |
| BYTES pages | unknown (403) | OQ-1 |

### 5.4 Official-documentation inconsistencies (recorded, not corrected)

1. **BBL example typo in the ZTLDB dictionary PDF** (Z5, p.4): *"Brooklyn Borough Code 3, Tax Block 15828, Tax Lot 7501 would be stored as **5158287501**"* — internally inconsistent (Brooklyn = 3; the stored value should begin with 3). The Socrata column description for `bbl` gives the corrected form *"…would be stored as 3158287501"* (Z2). Trust the algorithmic definition (1+5+4 zero-padded), not the PDF example.
2. **Borough Code length**: dictionary body says "two character borough code"; Maximum Length says "1 character"; live data and code table are 1-digit (Z3/Z5).
3. **nysp_sd description vs schema**: service description references a `SUBSUB` attribute; the live schema has `SUBAREA_*` fields instead (Z8/Z9). Alias oddities also present (SPNAME aliased "SDNAME"). Field mapping must use the live schema.
4. **nysp_sd copyright text** is itself corrupted at source ("YC Department of City Planning…" missing the leading N) (Z8) — trivial but demonstrates hand-maintained service metadata.

### 5.5 Recommended priority order (PRD §8 tiers, argued from evidence)

**NYC GIS Zoning Features (geometries):**
1. **ArcGIS feature services** (`nyzd`, `nyco`, `nysp`, `nysp_sd`, `nylh`, `nyzma` under `services5.arcgis.com/GfwWNkhOj9bNBqoJ`) — PRD tier 1 (official API). Freshest channel (2026-07-01), small layers (≤10k features), paged full extraction feasible, EPSG:2263 native, per-layer `dataLastEditDate` for freshness. **Citywide-import primary.**
2. **Socrata blob `mm69-vrje`** (FileGDB zip, 3.15 MB) — PRD tier 3. Use as the **version-labeled snapshot channel** for reproducibility (store the zip in Supabase `gis-imports` per release) once the description-version behavior is understood (OQ-4), and as bulk fallback if ArcGIS is unavailable.
3. **DCP BYTES page** — archive of previous versions (description-confirmed); 403-bound; browser capture needed (OQ-1).

**ZTLDB (lot-level assignments):**
1. **SODA `fdkv-4t4z`** — PRD tier 2. Per-BBL queryable, full official column semantics, X-App-Token discipline as per M1-T001 (Socrata platform behavior already verified there). **Subject to the mandatory staleness guard from §5.1.**
2. **DCP bulk CSV via BYTES** — PRD tier 3; currently *newer* than the SODA channel (dictionary source dates); exact URL 403-bound (OQ-1). Render-worker import only.
3. **Cross-check presentations** (not ingestion channels): PLUTO `zonedist1-4/overlay1-2/spdist1-3/ltdheight` (SODA `64uk-42ks`) and live nyzd/nyco spatial intersections — used by the conflict engine to detect vintage skew among the three presentations.

---

## 6. Proposed contract-test fixture pack (KB-scale; captured at connector build)

All fixtures: raw unmodified responses + request URL + retrieval timestamp; no dataset downloads.

**ZTLDB (`fdkv-4t4z`):**
| # | Fixture | Request | Asserts |
|---|---|---|---|
| ZT-F1 | single-lot normal | `/resource/fdkv-4t4z.json?bbl=<known BBL>` | 1 record; 16-column contract; number-typed values serialized as strings |
| ZT-F2 | split lot | BBL known split (e.g. `1000010010` observed live: ZD1 R3-2 + ZD2 C4-1) | `zoning_district_2` present; ordering semantics documented |
| ZT-F3 | no-match | syntactically valid nonexistent BBL | `[]` |
| ZT-F4 | blank-omission | lot with no overlay/special/LH | keys absent, not null |
| ZT-F5 | overlay lot | known C1/C2 overlay lot | `commercial_overlay_1` in Appendix C value set |
| ZT-F6 | special-district "/" tie | lot with combined SD1 (e.g. two overlapping SPDs) | "/"-joined abbreviation parses to two Appendix A codes |
| ZT-F7 | PARK lot | known parkland lot | ZD1 = "PARK"; connector flags do-not-use-for-open-space caveat |
| ZT-F8 | limited-height lot | e.g. an LH-1A lot | `limited_height_district` in Appendix D set |
| ZT-F9 | pagination | `$order=bbl&$limit=1000&$offset=…` | stable order, no dupes/gaps |
| ZT-F10 | row count/freshness | `$select=count(bbl)` + `api/views` `rowsUpdatedAt` | count baseline (857,951 @ 2026-07-16); staleness alert > 45 days |
| ZT-F11 | schema drift | `api/views/fdkv-4t4z.json` columns snapshot | 16-column diff vs contract; `$select=nonexistent` → HTTP 400 `query.soql.no-such-column` (signature verified on Socrata in M1-T001) |
| ZT-F12 | rate limit | tokenless burst in isolated test | HTTP 429 shape |

**Zoning features (ArcGIS):**
| # | Fixture | Request | Asserts |
|---|---|---|---|
| ZF-F1 | schema snapshot ×6 | `<layer>/FeatureServer/0?f=pjson` | fields array diff vs contract; SR 102718/2263; maxRecordCount recorded |
| ZF-F2 | count baseline ×6 | `returnCountOnly=true` | nyzd 5,416 / nyco 9,623 @ 2026-07-16; alert on large swings |
| ZF-F3 | single feature | `where=ZONEDIST='R3-2'…resultRecordCount=1` | attribute + polygon ring shape (captured live, Z10) |
| ZF-F4 | paging | `resultOffset` sweep on nyco (9,623 > 2000 cap) | exceededTransferLimit behavior; complete extraction |
| ZF-F5 | no-match | `where=ZONEDIST='XX'` | empty features array |
| ZF-F6 | point-in-polygon | geometry intersects query for a golden-property point | correct district; boundary-tolerant handling (±20 ft accuracy) |
| ZF-F7 | freshness | service root `editingInfo.dataLastEditDate` | monthly-refresh monitor; provenance stamp per ingest |
| ZF-F8 | blob manifest | `api/views/mm69-vrje.json` | blobFilename/size + "Current version: YYYYMM" string extraction |
| ZF-F9 | split-lot cross-check | ZTLDB ZD1/ZD2 vs nyzd ∩ MapPLUTO lot polygon for a golden split lot | three-way consistency or explicit conflict record |
| ZF-F10 | nyzma pending-action | query STATUS/EFFECTIVE for a known rezoning | date field decode (esriFieldTypeDate, UTC per service) |

---

## 7. Connector implementation plan (plan only — no code in this task)

1. **`zoning-features-arcgis` importer:** monthly Render worker job pages all six layers (f=json, EPSG:2263) into PostGIS (`zoning_district_geometries`, `commercial_overlay_geometries`, `special_district_geometries` + subdistricts, limited-height, pending `nyzma` → `pending_land_use_actions`); stamps `dataLastEditDate` per layer as source version; stores raw page responses in Supabase Storage.
2. **`zoning-features-blob` snapshotter:** on version-string change in `mm69-vrje`, download the 3 MB FileGDB zip on the worker, store in `gis-imports` for reproducibility.
3. **`ztldb-soda` connector:** per-BBL queries + monthly full sync (857k rows via paged SODA on a worker); staleness guard on `rowsUpdatedAt`; parse "/"-combined special districts; PARK caveat flag.
4. **Conflict engine hook:** compare ZTLDB vs PLUTO zoning attributes vs live nyzd intersection per property; surface vintage skew as `data_conflict` when values differ.

---

## 8. OPEN QUESTIONS ledger

| # | Question | Status / what is needed |
|---|---|---|
| OQ-1 | Exact BYTES download URLs, file names, and archive listing for both products (zoning features fgdb/shapefile zips; ZTLDB CSV zip) | OPEN — nyc.gov 403 recorded live (`/content/planning/pages/resources/datasets/gis-zoning-features`, Z12); page URLs for ZTLDB and legacy zoning page are search-evidenced only; needs browser-capable capture; must not be guessed |
| OQ-2 | Does a shapefile variant of GIS Zoning Features exist (and under what name)? | OPEN — no Socrata shapefile dataset found in 4 catalog searches (Z1); presumed BYTES-only; verify with OQ-1 |
| OQ-3 | Why are ZTLDB Socrata rows frozen at 2026-04-05 despite Monthly/Automation=Yes, while DCP's own dictionary shows a ≈June 2026 build? | OPEN — observe the next monthly boundary; if it persists, contact DCPOpendata@planning.nyc.gov (contact from nyzd metadata, Z11); until resolved, staleness guard mandatory |
| OQ-4 | Does the `mm69-vrje` blob actually update monthly (description says 202604; blobby timestamps frozen 2013)? What is the reliable version-change signal for the blob channel? | OPEN — poll the description string and/or blob content hash across a monthly boundary; data.gov check (2026-05-26) still showed 202604 |
| OQ-5 | Contents of the five unread layer metadata PDFs (nyco, nysp, nysp_sd, nylh, nyzma) — attribute semantics, per-layer accuracy/lineage | OPEN — files verified to exist (s-media + Socrata attachments with assetIds, Z6); extract at connector build or G1 |
| OQ-6 | How to pin a provenance version label for ArcGIS-side ingests (services expose no YYYYMM label) | OPEN — proposal: use `editingInfo.dataLastEditDate` + retrieval timestamp; confirm it moves in lockstep with the BYTES YYYYMM release |
| OQ-7 | nyzma value domains: STATUS values ("Adopted"/"Certified"/other?), LUCATS code list, EFFECTIVE null semantics for pending amendments | OPEN — needs nyzma_metadata.pdf (OQ-5) plus data sampling at connector build |
| OQ-8 | Serialization of "/"-combined special-district values in SODA (6-char max; e.g. which pairs actually occur) | OPEN — capture fixture ZT-F6 at connector build |
| OQ-9 | Eight ArcGIS epoch-ms→UTC conversions were done manually (deterministic arithmetic anchored to the machine-verified `1775414816 = 2026-04-05T18:46:56Z`) because the Bash tool was permission-denied mid-task | OPEN (verification formality) — G1 should spot-check one or two (e.g. 1782912288115 → 2026-07-01T13:24:48Z) |
| OQ-10 | Exact glyphs of the nyzd accuracy statement ("+/- 20 feet" rendered ambiguously in PDF extraction) | OPEN — G1 re-read of `nyzd_metadata.pdf` p.3 |
| OQ-11 | ArcGIS `f=geojson` support and full `resultOffset` paging behavior on these specific services | OPEN — standard AGOL capabilities but not exercised live in this task; test at connector build (ZF-F4) |

---

## 9. Source register (all fetched live by the producer on 2026-07-16)

| Ev | Official URL | Access method | Used for |
|---|---|---|---|
| Z1 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&…` with `q=zoning`, `q=zoning features`, `q="Zoning GIS Data"`, `q=zoning shapefile` | live fetches ×4 | channel enumeration; dataset-ID discovery (`fdkv-4t4z`, `mm69-vrje`, adjacent DCP zoning entries); absence of shapefile/per-layer Socrata datasets |
| Z2 | `https://data.cityofnewyork.us/api/views/fdkv-4t4z.json` | live fetch ×2 (columns pass; attachments/description pass) | ZTLDB identity, verbatim description, custom fields, raw timestamps, 16-column authoritative inventory with descriptions, attachment assetId |
| Z3 | `https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$limit=1` | live fetch, verbatim record | SODA liveness; split-lot live example; blank-key omission; string serialization |
| Z4 | `https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$select=count(bbl)` | live fetch | row count 857,951 |
| Z5 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/zoningtaxlotdatabase_datadictionary.pdf` | **direct PDF read, all 11 pages** (also verified as `fdkv-4t4z` attachment) | overview, 10%/50% rules, SOURCE DATASETS (DTM 2026-06-09; features 2026-05-20), change history, disclaimer, all 16 field definitions, Appendices A–D |
| Z6 | `https://data.cityofnewyork.us/api/views/mm69-vrje.json` | live fetch ×2 (incl. verbatim description) | blob identity, `nycgiszoningfeatures_fgdb.zip` 3,298,048 B, "Current version: 202604", frozen timestamps, six metadata-PDF attachments with assetIds, BYTES link target |
| Z7 | `https://www.arcgis.com/sharing/rest/search?q=owner:DCP_GIS AND title:zoning&f=json` | live fetch | official item→service binding for nyzd/nyzma under DCP_GIS; view-service and transit-zone items |
| Z8 | `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/{nyzd,nyco,nysp,nysp_sd,nylh,nyzma}/FeatureServer?f=pjson` | live fetches ×6 (plus services-directory listing) | service descriptions (verbatim), SR 102718/2263, maxRecordCounts, copyright |
| Z9 | same six + `/0?f=pjson` | live fetches ×6 | complete per-layer field inventories, objectIdField, `editingInfo` raw ms values |
| Z10 | `nyzd/FeatureServer/0/query?where=ZONEDIST='R3-2'…&f=pjson`; `nyzd…returnCountOnly=true`; `nyco…returnCountOnly=true` | live fetches | sample feature (attributes + polygon), counts 5,416 / 9,623 |
| Z11 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf` | **direct PDF read, all 4 pages** | cadence verbatim ("last Monday of every month"), not-for-lot-level warning, CRS (102718/2263, EPSG 2263), ±20 ft accuracy, vintage (2026-03-31 citation; adoptions through 2026-03-26; metadata update 2026-04-09), ZONEDIST field def, DCP contact email |
| Z12 | `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features` | live fetch → **HTTP 403 Forbidden** | BYTES page bot-protection recorded (S5); URL authenticity established via Z6 description link |
| Z13 | `https://catalog.data.gov/dataset/zoning-gis-data-geodatabase`; `https://catalog.data.gov/dataset/nyc-zoning-tax-lot-database` | live fetches | cross-channel corroboration: 202604 blob version (checked 2026-05-26); ZTLDB "April 5, 2026" still current at data.gov check 2026-07-07 |
| Z14 | WebSearch result listings (BYTES page URLs: `dwn-gis-zoning.page`, `datasets/zoning-taxlot-database`; legacy 2018 ZTLDB metadata PDF at nyc.gov/assets) | search-evidenced only | **[NEEDS G1 RE-VERIFICATION]** — page-existence pointers only; no content claims made from these |
