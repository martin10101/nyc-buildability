# M1-T003 — G1 Source and Data-Contract Gate Verification

- **Task:** M1-T003 — Official-source research: NYC GIS Zoning Features + Zoning Tax Lot Database (ZTLDB)
- **Gate:** G1 (source and data-contract)
- **Reviewer:** data-contract-verifier (independent; did not produce the work)
- **Review date / retrieval date for all live verifications:** 2026-07-16
- **Verdict:** **PASS** (with 7 required corrections listed in §5; none invalidates the producer's findings; no guessed claim found)
- **Method:** Independent live re-verification against official sources (Socrata `api/views` raw JSON, live SODA queries, ArcGIS Online REST search/item/service APIs, direct page-by-page reads of both s-media.nyc.gov PDFs, data.gov CKAN pages, live nyc.gov status checks). All epoch conversions re-done with real code (Python `datetime.fromtimestamp`, UTC). No dataset files downloaded; KB-scale requests only. Producer conclusions read LAST, after acceptance criteria and deliverables.

Artifacts reviewed:
- `project-control/tasks/M1-T003.json` (S1–S5 — starting point)
- `docs/research/zoning-features-ztldb-2026-07-16.md`
- `docs/research/source-registry-drafts/zoning-features.json` (2 records)
- `docs/research/source-registry-drafts/ztldb.json` (1 record)
- `project-control/reports/M1-T003-producer-report.md` (read last)

---

## 1. Mandatory live verifications (owner's list)

### 1.1 ArcGIS DCP_GIS services — ALL SIX VERIFIED LIVE; every claimed value matches

Fetched all six service roots and layer-0 definitions on `services5.arcgis.com/GfwWNkhOj9bNBqoJ` (2026-07-16):

| Layer | Live? | Geometry | SR wkid/latestWkid | maxRecordCount (claimed → actual) | Count (claimed → actual) | dataLastEditDate raw ms (claimed → actual) |
|---|---|---|---|---|---|---|
| nyzd | YES | polygon | 102718/2263 ✓ | 2000 → 2000 ✓ | 5,416 → **5,416** ✓ | 1782912288115 → 1782912288115 ✓ |
| nyco | YES | polygon | 102718/2263 ✓ | 2000 → 2000 ✓ | 9,623 → **9,623** ✓ | 1782912829636 → 1782912829636 ✓ |
| nysp | YES | polygon | 102718/2263 ✓ | 92 → 92 ✓ | not claimed → **95** (new) | 1782912605345 → 1782912605345 ✓ |
| nysp_sd | YES | polygon | 102718/2263 ✓ | 317 → 317 ✓ | not claimed → **336** (new) | 1782912514806 → 1782912514806 ✓ |
| nylh | YES | polygon | 102718/2263 ✓ | 14 → 14 ✓ | not claimed → **14** (new) | 1782912700015 → 1782912700015 ✓ |
| nyzma | YES | polygon | 102718/2263 ✓ | 1292 → 1292 ✓ | not claimed → **1,414** (new) | 1782912214592 → 1782912214592 ✓ |

- Item→service binding re-verified: ArcGIS item search `owner:DCP_GIS AND title:zoning` returned "Zoning Districts (NYZD)" item `788dcf4c61e34757bad1e015cb5f4111` and "Zoning Map Amendments (NYZMA)" item `d432de08f4f5477db101bb2f3dbe1f65`, both owner **DCP_GIS**, both pointing at the claimed service URLs. The `v_Zoning_Districts_NYZD` view item (`085766ab072342558dffb7d438c4ec09`) is also owner DCP_GIS, modified 1722958957000 = **2024-08-06T15:42:37Z** (producer's "≈2024-08-06" correct).
- Layer-0 field schemas match the registry draft **exactly**, including `SPNAME` aliased "SDNAME" on nysp_sd, the eight nysp_sd `SUBDIST/SUB_AREA_NM/SUBDIST_LBL/SUBAREA_LBL/SUBAREA_OTR` fields, `ZONEDIST` String 15, `OVERLAY` String 15 alias "Commercial Overlay", nyzma `EFFECTIVE` esriFieldTypeDate / `STATUS` String 15 / `ULURPNO` 50 / `LUCATS` 10 / `PROJECT_NAME` 100.
- **nysp_sd SUBSUB-vs-SUBAREA_* mismatch CONFIRMED:** live service description verbatim "...Any further subdistrict divisions are named in the SUBSUB attribute." while the live schema has no SUBSUB field (SUBAREA_* fields instead). The corrupted copyright string ("YC Department of City Planning, Technical Review Division; Columbia University's...") also confirmed verbatim.
- Sample query re-run: `nyzd/0/query?where=ZONEDIST='R3-2'&outFields=*&resultRecordCount=1` → OBJECTID 86, ZONEDIST "R3-2", Shape__Area 837150.6837310791, Shape__Length 4012.048764655896, 1 polygon ring, SR 102718/2263 — byte-for-byte consistent with the producer's Z10. No-match probe `where=ZONEDIST='XX'` → `"features": []`.
- **New finding (Correction C3):** live counts exceed the per-request cap on three layers — nysp 95 > cap 92, nysp_sd 336 > cap 317, nyzma 1,414 > cap 1292; nylh is exactly at its cap (14). An unpaged query silently truncates on these layers; the caps look pinned near an earlier vintage's feature counts. The registry's "connector must page generically" holds and becomes mandatory even for the "small" layers.

### 1.2 The eight manually-converted epoch timestamps (OQ-9) — ALL CORRECT; RESOLVED

The producer's Bash was denied mid-task and the ArcGIS epoch-ms values were converted by hand (flagged OQ-9). I re-converted every timestamp appearing in the deliverables with Python (`datetime.fromtimestamp(ms/1000, timezone.utc)`), live-refetching each raw value first:

| Raw value | Producer's manual conversion | My machine conversion | Match |
|---|---|---|---|
| 1782912288115 (nyzd) | ≈2026-07-01T13:24:48Z | 2026-07-01T13:24:48.115Z | ✓ |
| 1782912829636 (nyco) | ≈2026-07-01T13:33:49Z | 2026-07-01T13:33:49.636Z | ✓ |
| 1782912605345 (nysp) | ≈2026-07-01T13:30:05Z | 2026-07-01T13:30:05.345Z | ✓ |
| 1782912514806 (nysp_sd) | ≈2026-07-01T13:28:34Z | 2026-07-01T13:28:34.806Z | ✓ |
| 1782912700015 (nylh) | ≈2026-07-01T13:31:40Z | 2026-07-01T13:31:40.015Z | ✓ |
| 1782912214592 (nyzma) | ≈2026-07-01T13:23:34Z | 2026-07-01T13:23:34.592Z | ✓ |
| 1722958957000 (v_Zoning item modified) | ≈2024-08-06 | 2024-08-06T15:42:37Z | ✓ |
| 1359482950 (mm69-vrje frozen s-epoch) | 2013-01-29T18:09:10Z | 2013-01-29T18:09:10Z | ✓ |

Also re-verified the machine-converted Socrata seconds-epochs: 1375120531 = 2013-07-29T17:55:31Z; **1775414816 = 2026-04-05T18:46:56Z**; 1720205634 = 2024-07-05T18:53:54Z. The M1-T001 class of misconversion error is **absent** here. **OQ-9 RESOLVED** (Correction C6 removes the caveats). The "all six layers edited 2026-07-01 ~13:23–13:34 UTC coordinated refresh" claim is exactly right.

### 1.3 Socrata blob `mm69-vrje` — VERIFIED, plus one missed live signal

`https://data.cityofnewyork.us/api/views/mm69-vrje.json` (2026-07-16):
- viewType **blobby**, displayType blob ✓; blobFilename **`nycgiszoningfeatures_fgdb.zip`** ✓; blobFileSize **3,298,048** ✓; blobMimeType application/zip; attribution DCP ✓.
- Description verbatim confirmed, including the six-class list, the BYTES link `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features`, and **"Current version: 202604"** ✓.
- All six PDF attachments present with **exactly** the claimed assetIds (nyzd ee770e89-…, nyco f1459cd0-…, nysp f11a7a91-…, nysp_sd 0ff3fd30-…, nylh f83f6f43-…, nyzma 8d4c40d4-…) ✓.
- createdAt = rowsUpdatedAt = publicationDate = 1359482950 = 2013-01-29T18:09:10Z (frozen) ✓.
- **Missed signal (Correction C2):** `viewLastModified` = 1779809507 = **2026-05-26T15:31:47Z** — NOT frozen. It matches data.gov's "Dataset Last Updated: May 26, 2026" and is the day after the last Monday of May 2026 (2026-05-25). This is the best candidate blob-change polling signal for OQ-4, and it suggests the blob likely DID update ~2026-05-26 while the description string still reads 202604 — strengthening the producer's own "description string may itself be stale" hypothesis.
- data.gov mirror re-fetched: "Current version: 202604", last checked May 26 2026, single resource `https://data.cityofnewyork.us/download/mm69-vrje/application/zip` — all as claimed.

### 1.4 ZTLDB `fdkv-4t4z` — VERIFIED including the headline staleness finding

`https://data.cityofnewyork.us/api/views/fdkv-4t4z.json` (2026-07-16):
- Name/ID/attribution/viewType tabular/provenance official ✓. Custom fields: Update Frequency **Monthly**, Data Change Frequency Monthly, Automation **Yes**, Date Made Public 9/13/2021 ✓. Attachment `zoningtaxlotdatabase_datadictionary.pdf` assetId f0b9c61f-bb72-40a0-8ec9-e8a422f4b39a ✓.
- **Columns array = exactly 16 columns**, names and types matching the registry draft one-for-one (borough_code/tax_block/tax_lot/bbl number; the twelve zoning text columns) ✓.
- **Raw `rowsUpdatedAt` = 1775414816 = 2026-04-05T18:46:56Z — the ~3.4-month staleness against a Monthly/Automation=Yes cadence is REAL** (my own conversion, not the producer's). `viewLastModified` 1775414699 = 2026-04-05T18:44:59Z corroborates. Independent cross-check: data.gov ZTLDB page still says "Last Updated: April 05, 2026" with catalog last checked **July 07, 2026 9:22 PM**. The headline finding and the `degraded_suspected` health status are **justified by evidence**.
- Live SODA: `$limit=1` returned the **identical verbatim record** claimed (bbl 1000010010, ZD1 R3-2 + ZD2 C4-1 split, SD1 GI, map 16A code Y; blank fields omitted as keys; numbers serialized as strings) ✓. Row count re-run both ways: `$select=count(*)` → 857951 and `$select=count(bbl)` → **857,951** ✓.
- **Value-domain nuance the producer missed (Correction C4):** the Socrata `zoning_district_1` column description states the field holds the zoning district classification *"or in a limited number of cases the Zoning Resolution section number that pertains to special requirements for selected properties in Queens"*. Neither the dictionary PDF's ZD1 entry nor Appendix B mentions this — parsers must not treat Appendix B as a closed value set for ZD1.
- **Incomplete "verbatim" description quote (Correction C1):** the actual dataset description contains a final sentence the producer omitted: *"All previously released versions of this data are available on the \<a href="https://www.nyc.gov/content/planning/pages/resources/datasets/zoning-map-index"\>DCP Website: BYTES of the BIG APPLE\</a\>."* This is material: it is an **officially-linked BYTES archive pointer for ZTLDB** (the producer had only a search-evidenced page URL for ZTLDB). The link target is the *zoning-map-index* page — an odd target (possibly a DCP mis-link) — record as-is, do not guess. I verified live that this URL also returns HTTP 403 to non-browser clients.

### 1.5 ZTLDB data dictionary PDF — read directly, all 11 pages; every headline verbatim CONFIRMED

`https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/zoningtaxlotdatabase_datadictionary.pdf` (251 KB, fetched and read page-by-page by this reviewer):

| Claim | Verified against the PDF |
|---|---|
| 10% rule verbatim | p.1 OVERVIEW: "DCP assigns a zoning feature (includes zoning districts, special districts, and limited height districts) to a tax lot if 10% or more of the tax lot is covered by the zoning feature." ✓ |
| Overlay 10%/50% rule verbatim | p.1: "For commercial overlays, a tax lot is assigned a value if 10% or more of the tax lot is covered by the commercial overlay and/or 50% or more of the commercial overlay feature is within the tax lot." ✓ (field entries pp.5–6 repeat the "at least 10% ... or at least 50% ..." form) |
| SOURCE DATASETS | p.1: "Department of Finance Digital Tax Map — June 9, 2026; Department of City Planning NYC GIS Zoning Features — May 20, 2026" ✓ — confirms the DCP bulk release is NEWER than the Socrata rows |
| ZD1–4 descending-area split-lot semantics | pp.4–5: ZD1 "greatest percentage of the tax lot's area"; ZD2 "second greatest"; ZD3 "third greatest"; ZD4 "fourth greatest"; "If the tax lot is not divided by a zoning boundary line, the field is blank" (ZD2; analogous for ZD3/ZD4); lot-98 part A/B/C/D worked examples ✓ |
| ZD1 2019-12-31 logic change | p.1 CHANGE HISTORY December 31, 2019: "...the zoning district classification occupying the greatest percentage of a tax lot's area is assigned to Zoning District 1, even if the percentage is under 10%." ✓ (underwater-lot rationale verbatim) |
| PARK caveat | p.2 (Sept 7, 2018) and p.4 (ZD1 entry): PARK / BALL FIELD / PLAYGROUND / PUBLIC SPACES consolidated to single value PARK; "Lots designated as PARK should not be used to calculate the amount of open space in an area." ✓ |
| "/" special-district tie rule | p.6, Special District 1: "If the greatest percentage is occupied by two special purpose districts that overlap each other and cover the same percentage of the lot, Special District 1 contains the abbreviation for both special purpose districts, with the abbreviations separated by '/'." ✓ (same for SD2) |
| **BBL example typo** | p.4 verbatim: "Brooklyn Borough Code 3, Tax Block 15828, Tax Lot 7501 would be stored as **5158287501**." — typo CONFIRMED in the PDF. The Socrata `bbl` column description carries the corrected "...would be stored as 3158287501." — both halves of the producer's claim verified ✓ |
| Borough Code 1-char vs "two character" | p.2 Maximum Length "1 character"; p.3 Description "This field contains a two character borough code." — internal inconsistency CONFIRMED ✓; Marble Hill/Rikers legal-borough NOTE verbatim ✓ |
| Appendices A–D | Appendix A abbreviations 125th…WP incl. GI = "Special Governors Island District" ✓; Appendix B R1-1–R10H / C1-6–C8-4 / M1-1–M3-2A / M1-1/R5–M1-9A/R12 / BPC / PARK ✓; Appendix C exactly C1-1…C1-5, C2-1…C2-5 ✓; Appendix D LH-1, LH-1A (Upper East Side), LH-2*, LH-3* with "*There are currently no districts with these designations" ✓ |
| Disclaimer | p.2 verbatim as quoted ✓ |
| Zoning Map Code 'Y' semantics | p.7 verbatim ✓ |

### 1.6 nyzd metadata PDF — read directly, all 4 pages; cadence and CRS claims CONFIRMED

`https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf` (178.4 KB, direct read):
- **"The downloadable zoning data will be updated on the last Monday of every month. Updates will include recent zoning changes adopted by City Council."** — verbatim in Legal constraints ✓ (the Limitations-of-use block has the shorter "will be updated monthly" variant).
- **"These features are not intended for determining zoning at the individual tax lot level."** — verbatim ✓ (product-boundary warning confirmed).
- Spatial Reference: Projected, `NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet`, **WKID 102718, latestWkid 2263**, reference system identifier **2263 / EPSG** ✓.
- Data Quality: "The data were developed using DCP's Tax Block Base Map Files, DOITT's NYC Map planimetric street centerlines and 2006 orthophotos... The estimated horizontal accuracy is [±] 20 feet." — semantics and magnitude CONFIRMED; my independent extraction ALSO renders the sign glyph imperfectly ("< / 20 feet"), so the ambiguity is a PDF-text-extraction artifact, not a content doubt. **OQ-10 resolved as ±20 ft semantics** (Correction C7).
- Vintage: citation creation/publication date **3/31/2026**; "The date of the most recent City Council adoptions included in this data is 3/26/2026."; metadata Last update **2026-04-09** (last modified in ArcGIS 2026-04-09 11:17:04) — all three ✓, consistent with PLUTO 26v1's DATES OF DATA input "NYC GIS Zoning Features 2026-03-31" (M1-T001 accepted finding).
- Contact `DCPOpendata@planning.nyc.gov` ✓; status "under development" ✓; distribution format "File Geodatabase Feature Class" ✓; "The data is freely available to all New York City agencies and the public." ✓; ZONEDIST String 15 "Zoning district designation" ✓; Shape_Length/Shape_Area "internal units" ✓.

### 1.7 nyc.gov 403 discipline (S5) — CONFIRMED; nothing 403-bound was asserted

- `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features` → **HTTP 403** re-confirmed live by this reviewer (matches producer Z12; URL authenticity independently established via the mm69-vrje description link).
- `https://www.nyc.gov/content/planning/pages/resources/datasets/zoning-map-index` (the ZTLDB description's archive link, found in §1.4) → **HTTP 403** likewise.
- Swept the research doc for [NEEDS G1 RE-VERIFICATION] markers: exactly two content locations (§2.5: legacy `dwn-gis-zoning.page`; ZTLDB page `datasets/zoning-taxlot-database`; plus the Z14 register row describing them). Both are page-existence pointers only; no content claim was made from either; both legitimately remain open (browser-capable session needed). **No 403-bound claim was promoted to fact anywhere in the deliverables.**

### 1.8 Registry drafts (PRD §8.2) — PASS

- Both JSON files parse cleanly (validated with `json.load`). All three records carry all 18 PRD §8.2 fields (source ID → fallback source) plus `open_questions` (19 keys each).
- Nulls used where unknown: `last_successful_ingestion: null` (all records); `rate_limits.published_limit: null` (ArcGIS record — correct; Esri publishes no numeric limit for hosted feature services).
- **`health_status: "degraded_suspected"` for ZTLDB is justified by evidence I independently reproduced** (raw epoch conversion + data.gov corroboration + dictionary source-dates showing the bulk channel ahead). `"unverified"` for both zoning-features records is honest (no ingestion has run).
- Every factual value in the drafts traced back to a source I re-verified: service names, item IDs, maxRecordCounts, feature counts, SR, field lists with types/lengths/aliases, assetIds, blob name/size, "Current version: 202604", cadence verbatims, 16-column semantics, appendix value sets, BBL typo note, PARK caveat, ZD1 logic-change note. **No invented value found** (the M1-T001 D1 class of defect is absent).
- Low-storage: no dataset downloads by producer or reviewer; this review cached two official PDFs (~430 KB) in the harness WebFetch cache outside the repo; zero repo binaries.

---

## 2. Independent scenario walkthrough (S1–S5 from the task packet)

| Scenario | Expected | Actual (this reviewer's independent run) | Result |
|---|---|---|---|
| S1 normal — channel enumeration | Every channel evidenced by live fetch/direct read; IDs pinned by ID + attribution | Both dataset IDs re-verified live with DCP attribution; all six ArcGIS services re-fetched; data.gov mirrors re-fetched; my own catalog spot-check (`q=zoning shapefile`) also surfaced no shapefile/per-layer Socrata variant | PASS |
| S2 boundary — version/release model | Verbatim cadence; current version observed; PLUTO relationship | "Last Monday of every month" read directly from the PDF by me; "Current version: 202604" in live description; dataLastEditDate 2026-07-01 ×6 re-fetched raw and re-converted; 26v1↔2026-03-31 vintage chain consistent | PASS |
| S3 missing/ambiguous — fields/units/CRS/split lots | Field inventory from official metadata, not record keys; unknowns ledgered; CRS evidenced | 16 SODA columns from the columns array = dictionary fields 1:1; all six layer schemas re-fetched; EPSG:2263 from both live services and official metadata; split-lot ZD1–4 semantics verified verbatim from the PDF; blank-key omission observed live; unknowns in an 11-item OQ ledger | PASS |
| S4 conflict — cross-channel discrepancies | Discrepancies surfaced with evidence + priority order | ZTLDB staleness independently reproduced (raw epoch + data.gov + dictionary source dates); blob-vs-ArcGIS lag confirmed (and sharpened by the viewLastModified find, C2); four documentation defects all confirmed verbatim (BBL typo, 2-char/1-char, SUBSUB, corrupted copyright); priority order consistent with PRD §8 tiers and with the evidence | PASS |
| S5 failure — bot-protected endpoints | 403s recorded honestly as OQ items; nothing promoted to fact | Both nyc.gov URLs return 403 to this reviewer too; the two [NEEDS G1 RE-VERIFICATION] markers are the only search-evidenced items and carry no content claims | PASS |

## 3. Reproduction commands (all runnable as-is)

```
# ZTLDB metadata, columns, timestamps
curl -s "https://data.cityofnewyork.us/api/views/fdkv-4t4z.json"
# Live SODA sample + counts
curl -s "https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$limit=1"
curl -s "https://data.cityofnewyork.us/resource/fdkv-4t4z.json?$select=count(*)"
# Blob dataset
curl -s "https://data.cityofnewyork.us/api/views/mm69-vrje.json"
# Six ArcGIS services (repeat per svc in nyzd nyco nysp nysp_sd nylh nyzma)
curl -s "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer?f=pjson"
curl -s "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0?f=pjson"
curl -s "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0/query?where=1%3D1&returnCountOnly=true&f=pjson"
curl -s "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/nyzd/FeatureServer/0/query?where=ZONEDIST%3D%27R3-2%27&outFields=*&resultRecordCount=1&f=pjson"
# Epoch conversion (example)
python -c "import datetime;print(datetime.datetime.fromtimestamp(1782912288115/1000,datetime.timezone.utc))"
# Item ownership
curl -s "https://www.arcgis.com/sharing/rest/search?q=owner:DCP_GIS%20AND%20title:zoning&f=json&num=20"
# PDFs (WebFetch caches the binary; then Read with pages)
#   https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/zoningtaxlotdatabase_datadictionary.pdf
#   https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf
# 403 checks
curl -s -o /dev/null -w "%{http_code}" "https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features"
curl -s -o /dev/null -w "%{http_code}" "https://www.nyc.gov/content/planning/pages/resources/datasets/zoning-map-index"
```

## 4. Open-questions ledger after G1 (OQ-1..OQ-11)

| OQ | Status after this review | Notes |
|---|---|---|
| OQ-1 | **STILL OPEN (narrowed)** | nyc.gov 403 re-confirmed live twice by this reviewer. New: the ZTLDB dataset description itself links a BYTES archive page (`.../datasets/zoning-map-index`) — officially evidenced URL, also 403 (C1). Browser session still required for file URLs |
| OQ-2 | **STILL OPEN** | My independent catalog spot-check also found no shapefile/per-layer Socrata variant; consistent with producer's 4 searches |
| OQ-3 | **STILL OPEN — but the observation is VERIFIED** | Staleness independently reproduced from raw epoch + data.gov + dictionary source dates. Cause unknowable from public metadata; monthly-boundary observation (2026-07-27) is the right next step |
| OQ-4 | **STILL OPEN (narrowed)** | New signal found: `viewLastModified` = 2026-05-26T15:31:47Z moves on blobby datasets (C2) — poll it plus the description string plus content hash |
| OQ-5 | **STILL OPEN** | Five layer-metadata PDFs verified to exist (assetIds re-confirmed); content extraction legitimately deferred |
| OQ-6 | **STILL OPEN** | dataLastEditDate + retrieval timestamp proposal is sound; confirm lockstep with YYYYMM at a release boundary |
| OQ-7 | **STILL OPEN** | nyzma value domains need nyzma_metadata.pdf + sampling |
| OQ-8 | **STILL OPEN** | "/"-combined SD serialization fixture at connector build |
| OQ-9 | **RESOLVED** | All eight manual epoch conversions machine-re-verified correct to the second (§1.2); remove caveats (C6) |
| OQ-10 | **RESOLVED (semantics)** | ±20 ft estimated horizontal accuracy confirmed; sign-glyph ambiguity is an extraction artifact present in my independent read too (C7) |
| OQ-11 | **STILL OPEN** | f=geojson / resultOffset behavior untested — correctly deferred to ZF-F4; note C3 raises its priority (three layers page-truncate) |

## 5. Required corrections (proposed for orchestrator/producer application; none invalidates the findings)

1. **C1 — research doc §2.1 and §2.5; `ztldb.json` `fallback_source`/`open_questions`:** the `fdkv-4t4z` description "verbatim" quote is incomplete — append its final sentence: "All previously released versions of this data are available on the [DCP Website: BYTES of the BIG APPLE](https://www.nyc.gov/content/planning/pages/resources/datasets/zoning-map-index)." Record this as the officially-linked ZTLDB archive pointer (HTTP 403 to non-browser clients, verified 2026-07-16); note the odd link target (zoning-map-index) as-is without guessing intent. The search-evidenced `datasets/zoning-taxlot-database` URL keeps its [NEEDS G1 RE-VERIFICATION] marker.
2. **C2 — research doc §2.2/§5.2/§5.3; `zoning-features.json` record 2 (`known_limitations`, OQ-4):** add `viewLastModified` = 1779809507 = 2026-05-26T15:31:47Z (live 2026-07-16) — NOT frozen at 2013, matches data.gov "Dataset Last Updated: May 26, 2026", and is the day after the last Monday of May 2026. Use it as the primary blob-change polling signal; it implies the blob likely updated ~2026-05-26 while the description still says 202604 (strengthens the stale-description hypothesis).
3. **C3 — research doc §2.3; `zoning-features.json` record 1 (`fields_available.feature_counts`, `known_limitations`):** add live counts (2026-07-16, this review): nysp **95**, nysp_sd **336**, nylh **14**, nyzma **1,414** — and the hazard that counts EXCEED maxRecordCount on nysp (95>92), nysp_sd (336>317), and nyzma (1414>1292), with nylh exactly at cap: an unpaged request silently truncates. Paging is mandatory on every layer, not only nyzd/nyco.
4. **C4 — `ztldb.json` `fields_available.columns` (zoning_district_1) and `known_limitations`; research doc §4.1:** add the Socrata column-description caveat that `zoning_district_1` may contain "the Zoning Resolution section number that pertains to special requirements for selected properties in Queens" — Appendix B is not a closed value set for ZD1; parser/validator must tolerate ZR section-number values.
5. **C5 (trivial) — research doc §4.2 (nyzma):** the live service description verbatim begins "Outlines **or** for all zoning changes adopted and proposed since January 1, 2002." (source typo the producer's quote silently cleaned) and includes a third sentence: "Selected city-initiated text amendments to the Zoning Resolution since 2002 that have discrete geographical boundaries may be included." — materially relevant to `pending_land_use_actions` scope; quote in full.
6. **C6 — research doc §2.3 note + §8 OQ-9 row; `zoning-features.json` record 1 `update_frequency`:** mark OQ-9 RESOLVED (all eight conversions machine-verified correct, §1.2 of this report) and drop the "manual epoch conversion, OQ-9" caveats.
7. **C7 — research doc §4.3 + §8 OQ-10 row; `zoning-features.json` record 1 `fields_available.accuracy`:** mark OQ-10 resolved: "estimated horizontal accuracy ±20 feet" semantics confirmed by an independent direct read; the sign-glyph ambiguity is a PDF-extraction artifact, not a content uncertainty.

## 6. Defects

**None material.** No guessed schema, endpoint, unit, or value found anywhere in the three deliverables. The only quality issues are C1 (incomplete verbatim quote that hid an officially-linked archive URL) and C5 (silently cleaned typo + truncated quote in a "verbatim" service description) — both minor documentation-fidelity defects, not factual errors. Everything the producer flagged as uncertain was genuinely uncertain; everything asserted as fact re-verified true.

## 7. Recommendation for G3

PASS this G1 with corrections C1–C7 applied by an orchestrator editorial fixup or producer rework (all corrected values are recorded here with evidence). G3 should:
1. Confirm the corrected documents read coherently against this report.
2. Re-run as its normal/boundary/missing/failure cases: the ZTLDB `$limit=1` sample, the nyzd count + R3-2 sample query, the `ZONEDIST='XX'` no-match, and one nyc.gov 403 check (exact commands in §3).
3. Treat OQ-1/OQ-2 (BYTES page contents/shapefile variant, browser session needed) and the monthly-boundary observations (OQ-3 on/after 2026-07-27; OQ-4 via viewLastModified) as the legitimately open items — they must not be guessed.
4. Verify no large or persistent artifacts were written locally (producer ~430 KB and reviewer ~430 KB of PDFs live only in the harness WebFetch cache; zero repo binaries).

## 8. Evidence URL index (all retrieved 2026-07-16 by this reviewer)

| # | URL | What it verified |
|---|---|---|
| V1 | `https://data.cityofnewyork.us/api/views/fdkv-4t4z.json` | 16 columns; raw timestamps (rowsUpdatedAt 1775414816); custom fields; attachment assetId; full description incl. archive link (C1); bbl column corrected example 3158287501; ZD1 Queens ZR-section caveat (C4) |
| V2 | `https://data.cityofnewyork.us/resource/fdkv-4t4z.json` (`$limit=1`, `$select=count(*)`, `$select=count(bbl)`) | verbatim sample record; blank-key omission; string serialization; 857,951 rows |
| V3 | `https://data.cityofnewyork.us/api/views/mm69-vrje.json` | blobby; nycgiszoningfeatures_fgdb.zip 3,298,048 B; "Current version: 202604"; frozen 2013 triple; viewLastModified 2026-05-26 (C2); six attachments/assetIds |
| V4 | `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/{nyzd,nyco,nysp,nysp_sd,nylh,nyzma}/FeatureServer` `?f=pjson`, `/0?f=pjson`, `/0/query` (counts ×6, R3-2 sample, XX no-match) | service identity, SR 102718/2263, maxRecordCounts, schemas, editingInfo raw ms ×6, counts (incl. cap-exceedance C3), descriptions (SUBSUB mismatch, corrupted copyright, nyzma third sentence C5) |
| V5 | `https://www.arcgis.com/sharing/rest/search?q=owner:DCP_GIS AND title:zoning` + `/content/items/085766ab072342558dffb7d438c4ec09` | DCP_GIS ownership of nyzd/nyzma items (IDs match); v_Zoning view item modified 2024-08-06T15:42:37Z |
| V6 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/zoningtaxlotdatabase_datadictionary.pdf` (251 KB, all 11 pages read) | 10%/50% rules; ZD1–4 split semantics; SOURCE DATASETS 2026-06-09/2026-05-20; change history; "/" tie rule; PARK caveat; 5158287501 typo; 1-char/2-char inconsistency; Appendices A–D; disclaimer |
| V7 | `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/nyzd_metadata.pdf` (178.4 KB, all 4 pages read) | "last Monday of every month"; not-for-lot-level warning; WKID 102718/latestWkid 2263/EPSG 2263; ±20 ft accuracy; 3/31/2026 vintage; 3/26/2026 adoptions; 2026-04-09 metadata update; DCPOpendata contact |
| V8 | `https://catalog.data.gov/dataset/zoning-gis-data-geodatabase` | 202604 version echo; last checked May 26 2026; download endpoint `data.cityofnewyork.us/download/mm69-vrje/application/zip` |
| V9 | `https://catalog.data.gov/dataset/nyc-zoning-tax-lot-database` | "Last Updated: April 05, 2026"; catalog last checked 2026-07-07 21:22 — independent staleness corroboration |
| V10 | `https://www.nyc.gov/content/planning/pages/resources/datasets/gis-zoning-features` and `.../zoning-map-index` | HTTP 403 ×2 (bot protection re-confirmed; S5 discipline validated) |
| V11 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=zoning shapefile` | independent spot-check: no shapefile/per-layer zoning-features Socrata dataset (OQ-2 consistent) |
