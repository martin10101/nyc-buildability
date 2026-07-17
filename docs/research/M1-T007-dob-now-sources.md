# M1-T007 — Official-Source Research: DOB NOW Open Data family

- **Task:** M1-T007 (research-only; PRD §8.1 mandatory family)
- **Producer:** official-source-researcher
- **All retrievals:** 2026-07-17, 07:45–08:05 UTC, live, tokenless, throttled (server-clock anchor: attachment probe response header `Date: Fri, 17 Jul 2026 07:56:52 GMT`)
- **Fixtures:** `docs/research/fixtures/m1-t007/` (verbatim SODA responses + labeled extracts; retrieval commands in the fixtures README)
- **Registry drafts:** `docs/research/source-registry-drafts/dob-now.json`
- **Scope guard:** DOB NOW family ONLY. Legacy BIS datasets appear here solely as evidenced RULE-OUTS (§6); BIS research is the next task.

## 1. Executive summary

The DOB NOW family on NYC Open Data (`data.cityofnewyork.us`) consists of **11 live Socrata tabular datasets**, all attributed to the Department of Buildings (DOB), all `provenance: official`, all on the Socrata new backend (SODA 2.1 → no `$limit` maximum), all with official data-dictionary XLSX attachments, and all — on 2026-07-17 — showing `rowsUpdatedAt` of 2026-07-16, consistent with their stated Daily / Every-weekday automation. No staleness was observed anywhere in the family (contrast: M1-T003 found a 3-month ZTLDB stall).

**Recommended core for M2 property-profile facts (6):**

| ID | Name | Rows (2026-07-17) | Role |
| --- | --- | --- | --- |
| `w9ak-ipjd` | DOB NOW: Build — Job Application Filings | 930,325 | job filings (non-electrical/elevator/LAA) |
| `rbx6-tga4` | DOB NOW: Build — Approved Permits | 969,467 | approved construction permits |
| `pkdm-hqz6` | DOB NOW: Certificate of Occupancy | 79,236 | COs issued since ~March 2021 |
| `xubg-57si` | DOB NOW: Safety — Facades Compliance Filings | 86,683 | FISP/facade filings |
| `52dp-yji6` | DOB NOW: Safety Boiler | 871,266 | annual boiler compliance |
| `e5aq-a4j2` | DOB NOW Elevator Safety Compliance | 120,137 | elevator device inspection/compliance |

**Secondary family members (5, verified but lower priority for the property profile):** `dm9a-ab7w` (Electrical Permit Applications), `xmmq-y7za` (Electrical Permit Details — child of dm9a-ab7w via `job_filing_number`, NO location fields of its own), `kfp4-dz4h` (Build Elevator Permit Applications), `juyv-2jek` (Build Elevator Device Details — child of kfp4-dz4h via `job_filing_number`, one row per device), `xxbr-ypig` (Build — Limited Alteration Applications).

**Explicit rule-outs (legacy/BIS or superseded — NEXT task's family):** `ipu4-2q9a`, `ic3t-wcy2`, `bs8b-p36w`, `e98g-f8hy`, `bty7-2jhb` (§6, each with verbatim official boundary statements).

**Highest-impact findings for connector design:**
1. `rbx6-tga4` can carry the placeholder text `"Permit is no"` / `"Permit is not yet issued"` **inside the `job_filing_number` and `work_permit` join-key columns** (observed verbatim, §4.3) — key-format validation is mandatory.
2. Borough casing is inconsistent **across datasets for the same property** (`"Manhattan"` in w9ak-ipjd vs `"MANHATTAN"` in rbx6-tga4, same BBL, observed) — normalize before matching.
3. `bbl` is `text` in some datasets and `number` in others; `xubg-57si` has **no BBL at all** (BIN + borough/block/lot only) and `52dp-yji6` has **only `bin_number`** (no BBL, no address, no borough).
4. Two datasets carry non-ISO date strings in `text` columns (`"02/22/2018 00:00:00"`, `"02/15/22 11:08:46 AM"`) alongside ISO `floating_timestamp` columns.

## 2. S1 — Discovery and live-verified identity of every family dataset

### 2.1 Catalog discovery (recorded queries)

Two independent catalog queries on 2026-07-17 returned **identical 21-dataset result sets** (extract fixture `catalog_dob-now_results_extract.json`):

- `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB%20NOW&limit=30` → HTTP 200, resultSetSize 21
- `https://data.cityofnewyork.us/api/catalog/v1?q=DOB%20NOW&limit=30` → HTTP 200, resultSetSize 21

11 results carry the "DOB NOW" prefix and DOB attribution (the family); 5 are legacy/BIS-era DOB datasets (ruled out in §6); the remaining 5 are non-family hits (g76y-dcqj After Hour Variance Permits and 855j-jady DOB Safety Violations are DOB but not DOB NOW-module datasets — out of scope here, flagged for the BIS/legacy task; bf97-mjsy Construction-Related Incidents is DOB-attributed but not a DOB NOW-module output — evidence-backed disposition in the dedicated paragraph below; two HPD datasets are noise).

**bf97-mjsy — Construction-Related Incidents: evidence-backed disposition (C1v2).** All claims below live-verified 2026-07-17, tokenless, via `https://data.cityofnewyork.us/api/views/bf97-mjsy.json` (metadata) and `https://data.cityofnewyork.us/resource/bf97-mjsy.json` (SODA), all HTTP 200.

- **What it is:** official name "Construction-Related Incidents", attribution "Department of Buildings (DOB)", `provenance: official`, `newBackend: true`; description verbatim: "This dataset includes construction-related incidents recorded in through the Department of Buildings (DOB) Incident Database." [sic]. Created 2024-10-16 (createdAt 1729098863), custom fields: Date Made Public "11/21/2024", Update Frequency "Daily", Automation "Yes", "The underlying data changes second-to-second in the system of record."; `rowsUpdatedAt` 2026-07-16T18:46:16Z (epoch 1784227576) — same-day freshness as the DOB NOW family. Official data dictionary attached ("Construction-Related Incidents_Data Dictionary.xlsx", assetId b40d4ef0-d572-4a05-9195-2c01617af0c2; XLSX not content-extracted, same OQ-2 constraint as §2.3).
- **Keys (20-column array + `$limit=2&$order=incident_date_mm_dd_yyyy DESC` sample, observed verbatim):** `bin` text, 7-digit borough-leading ("3000370", "4000542"); `address_bbl` text, 10-digit zero-padded ("3001497503", "4000717501"); `boro` title case ("Brooklyn", "Queens"); `block` text, observed without zero-padding ("149", "71"); `lot` text ("7503", "7501" — condo billing lots in the 75xx range, same semantics as §3.2; both observed lots are naturally four digits, so padding behavior for shorter lot numbers is NOT established by these samples); address `addressnumber` + `street`; plus `address_zipcode`, `address_latitude`/`address_longitude` (text), community district, council district, `address_censustract2020`, `address_nta2020`. Observed BIN and BBL formats appear compatible with the normalized property-profile keys, subject to connector validation, normalization, and mismatch handling (two sampled records; §3.4 BIN-primary/BBL-corroboration strategy would apply).
- **Fact fields:** `accident_report_id` (number), `incident_date_mm_dd_yyyy` (calendar_date, ISO serialization "2026-07-14T00:00:00.000"), `record_type_description` (text; "Incident" observed), `check2_description` (incident category text; "Other Construction Related" observed), `fatality` (number), `injury` (number).
- **Size and coverage:** `$select=count(*)` → 1,326 rows; `$select=min/max(incident_date_mm_dd_yyyy)` → 2024-01-03T00:00:00.000 to 2026-07-14T00:00:00.000 (retrieved 2026-07-17) — a short window opening ~January 2024, consistent with the 2024-11-21 publication date.
- **Why not in the DOB NOW connector family:** its stated system of record is the "DOB Incident Database" (description verbatim above), not a DOB NOW: Build / Safety / Electrical module, and it carries no `job_filing_number` / `work_permit` keys, so it cannot participate in the family's filing→permit→device join graph (§3.3).
- **Value to the property-history product:** material, not noise — per-BIN construction-incident history with injury/fatality counts and incident dates is a direct site-history/risk signal for a development-feasibility profile; observed BIN and BBL formats appear compatible with the normalized property-profile keys, subject to connector validation, normalization, and mismatch handling.
- **Classification: documented secondary/future source** — assigned to M1-T008 (DOB-wide/BIS-legacy official-source research) for full G1 research treatment, feeding a subsequent M2 property-history/risk fact-connector stage; reason: it is valuable and apparently joinable (subject to connector validation), but its system of record sits outside this task's DOB NOW-module scope, and its small size (1,326 rows) and short coverage window (incidents from 2024-01-03 only) make it a supplementary risk-signal feed rather than a first-stage core profile fact source.

### 2.2 Live identity of the 11 family datasets

Each verified via `https://data.cityofnewyork.us/api/views/<4x4>.json` on 2026-07-17 (HTTP 200; extract fixture `views_metadata_extract_16_datasets.json` retains verbatim values incl. raw epochs). All 11: `assetType: dataset` (tabular), `newBackend: true`, `provenance: official`, attribution "Department of Buildings (DOB)", agency custom-field "Department of Buildings (DOB)".

| ID | Official name | Cols | Created (UTC) | Update Frequency (custom field) | Automation | rowsUpdatedAt (UTC) |
| --- | --- | --- | --- | --- | --- | --- |
| w9ak-ipjd | DOB NOW: Build — Job Application Filings | 95 | 2016-05-26 | Daily | Yes | 2026-07-16T20:23:19Z |
| rbx6-tga4 | DOB NOW: Build — Approved Permits | 46 | 2016-05-26 | Daily | Yes | 2026-07-16T18:42:18Z |
| pkdm-hqz6 | DOB NOW: Certificate of Occupancy | 24 | 2022-05-17 | Daily | Yes | 2026-07-16T20:01:40Z |
| xubg-57si | DOB NOW: Safety — Facades Compliance Filings | 40 | 2016-09-09 | **Every weekday** | Yes | 2026-07-16T17:31:05Z |
| 52dp-yji6 | DOB NOW: Safety Boiler | 21 | 2017-09-14 | Daily | Yes | 2026-07-16T19:59:02Z |
| e5aq-a4j2 | DOB NOW Elevator Safety Compliance | 24 | 2023-01-27 | Daily ("underlying data changes second-to-second in the system of record") | Yes | 2026-07-16T20:32:59Z |
| xxbr-ypig | DOB NOW: Build — Limited Alteration Applications | 26 | 2021-10-25 | Daily | Yes | 2026-07-16T18:35:04Z |
| dm9a-ab7w | DOB NOW: Electrical Permit Applications | 83 | 2019-04-17 | Daily | Yes | 2026-07-16T21:48:38Z |
| xmmq-y7za | DOB NOW: Electrical Permit Details | 40 | 2019-04-17 | Daily | Yes | 2026-07-16T20:05:30Z |
| kfp4-dz4h | DOB NOW: Build Elevator Permit Applications | 82 | 2019-10-03 | Daily | Yes | 2026-07-16T16:32:00Z |
| juyv-2jek | DOB NOW: Build Elevator Device Details | 167 | 2019-10-03 | Daily | Yes | 2026-07-16T14:16:44Z |

SODA liveness proven for all 11 via `resource/<4x4>.json?$limit=2` (verbatim fixtures `sample_<4x4>.json`, HTTP 200, 2 records each).

### 2.3 Official data dictionaries (identified, not yet content-extracted)

Every family dataset has an official data-dictionary **XLSX** attachment in `metadata.attachments` (filenames + assetIds captured in the views extract). Attachment download pattern verified live once: `https://data.cityofnewyork.us/api/views/w9ak-ipjd/files/978bdfe8-11c3-4839-9515-7f36a83e219d?download=true&filename=...` → HTTP 200, `application/octet-stream`, 74,405 bytes. XLSX content extraction is **not** performed in this task (binary parsing; no local heavy tooling per low-storage policy) → **OQ-2**. Note the M1-T003 s-media PDF workaround does not directly apply: these are XLSX, and no s-media twin was identified for DOB documents (DOB is not DCP) → also OQ-2.

### 2.4 Family completeness cross-checks

- `w9ak-ipjd` description (verbatim): "List of most job filings filed in DOB NOW. This dataset does not include certain types of job. For Electrical jobs, use https://data.cityofnewyork.us/browse?Data-Collection_Data-Collection=DOB+NOW+Electrical+Permits+Data. Elevator and LAA jobs will also be published separately."
- `rbx6-tga4` description (verbatim): "List of all approved construction permits in DOB NOW except for Electrical [dm9a-ab7w], Elevator [kfp4-dz4h], and Limited Alteration Application (LAA) [xxbr-ypig] which have their own datasets." — the exception links are the other family members, confirming closure of the permit-side family.
- data.gov mirror exists for the flagship dataset: `catalog.data.gov/dataset/dob-now-build-job-application-filings` → HTTP 200; raw-HTML grep matched literal `w9ak-ipjd` (summarizer not used; memory guard applied). CKAN action API (`/api/3/action/package_search`) returned HTTP 404 on 2026-07-17 — mirror checks must use dataset pages, not the action API.
- DOB NOW: Safety datasets for facades/boilers/elevators all exist and are the three Safety members above (packet's "as applicable" satisfied). No DOB NOW "Safety — Cranes/Derricks" or gas datasets surfaced in the 21-result catalog set; absence recorded (OQ-6).

## 3. S2 — BBL/BIN join semantics (all observed, never guessed)

### 3.1 Identifier fields per dataset (from live `api/views` columns arrays; types verbatim)

| Dataset | BBL | BIN | Borough/Block/Lot | Address | Geo extras |
| --- | --- | --- | --- | --- | --- |
| w9ak-ipjd | `bbl` text | `bin` text | `borough`,`block`,`lot` text | `house_no`,`street_name` | `latitude`,`longitude` **text**, `council_district`, `census_tract`, `nta` |
| rbx6-tga4 | `bbl` **number** | `bin` text | `borough`,`block`,`lot` text | `house_no`,`street_name` | `latitude`,`longitude` number, `community_board`,`council_district`,`census_tract` number, `nta` text |
| pkdm-hqz6 | `bbl` text | `bin` text | `borough`,`block`,`lot` text | `house_no`,`street_name` | `latitude`,`longitude` number, `citycouncildistrict` text, `censustract2010` number, `ntaname` text |
| xubg-57si | **none** | `bin` text | `borough`,`block`,`lot` text | `house_no`,`street_name` | none |
| 52dp-yji6 | **none** | `bin_number` **number** | **none** | **none** | none |
| e5aq-a4j2 | `bbl` text | `bin` text | `borough`,`block`,`lot` text | `house_number`,`street_name` | `latitude`,`longitude` number, `communitydistrict`,`citycouncildistrict`,`censustract`,`ntaname` text |
| xxbr-ypig | `bbl` **number** | `location_bin` text | `location_borough_name` text (no block/lot) | `location_house_no`,`location_street_name` | `latitude`,`longitude` number |
| dm9a-ab7w | `gis_bbl` text | `bin` text | `borough`,`block`,`lot` text | `house_number`,`street_name` | `gis_latitude`,`gis_longitude`,`gis_council_district`,`gis_census_tract`,`gis_nta_name` text |
| xmmq-y7za | **none** | **none** | none | none | child table — join `job_filing_number` → dm9a-ab7w |
| kfp4-dz4h | `bbl` text | `bin` text | `borough`,`block`,`lot` text | `house_number`,`street_name` | `latitude`,`longitude` number, `community_district_number`,`city_council_district`,`census_tract`,`bbl`,`nta_name` |
| juyv-2jek | **none** | **none** | none | `physical_address` text only | child table — join `job_filing_number` → kfp4-dz4h; `device_id`; `bis_nyc_device_id` (legacy device cross-ref) |

Field-name drift across the family is real and must be mapped per dataset: `house_no` vs `house_number` vs `location_house_no`; `bin` vs `bin_number` vs `location_bin`; `bbl` vs `gis_bbl`; `council_district` vs `citycouncildistrict` vs `city_council_district` vs `gis_council_district`.

### 3.2 Observed value formats (verbatim from fixtures)

- **BBL:** 10-digit, zero-padded, `{borocode 1}{block 5}{lot 4}` — observed `"1004410016"` (w9ak-ipjd, text), `"4051980021"` (rbx6-tga4, number), `"1001747505"` (pkdm-hqz6), `"1001490006"` (e5aq-a4j2), `"5031737504"` (xxbr-ypig, number), `"3031310023"` (dm9a-ab7w `gis_bbl`), `"1007987501"` (kfp4-dz4h). Consistent with PLUTO/ZTLDB BBL composition (M1-T001/T003).
- **Number-typed BBL serialization (rbx6-tga4):** `$select=bbl,bin,block,lot&$limit=2` returned `{"bbl":"4051980021","bin":"4117367","block":"5198","lot":"21"}` — **no trailing-decimal artifact observed** (fixture `query_rbx6-tga4_select-bbl-serialization.json`). This differs from PLUTO's observed `"1000010100.00000000"` under `$select` (M1-T001 G1 finding C6). Do NOT generalize from one probe: the connector must still normalize defensively (OQ-3).
- **Block/lot are NOT zero-padded** where split out: `block "441"`, `lot "16"` (w9ak-ipjd/rbx6-tga4); condo billing lots observed in the 75xx range (`7505` pkdm-hqz6, `7501` xubg-57si/kfp4-dz4h) — condo semantics as in PLUTO.
- **BIN:** 7-digit, first digit = borough code — observed `1006014`, `4117367`, `1001905`, `1014176`, `1043866`, `1001627`, `5122289`, `3425456`. `52dp-yji6` serializes its number-typed `bin_number` as `"1043866"` (string in JSON, no decimals observed).
- **Borough values (inconsistent casing/format across datasets, same property):** `"Manhattan"` (w9ak-ipjd) vs `"MANHATTAN"` (rbx6-tga4) — both observed for BBL 1004410016 in the cross-probe fixtures; also `"QUEENS"`,`"BROOKLYN"` (upper) vs `"Staten Island"` (title case, xxbr-ypig `location_borough_name`). Case-insensitive normalization to borocode required.
- **Dates:** primary event dates are ISO floating_timestamps (`"2023-04-10T00:00:00.000"`), BUT `52dp-yji6.inspection_date` is text `"02/22/2018 00:00:00"` (MM/DD/YYYY) and `pkdm-hqz6.c_of_o_issuance_date` is text `"02/15/22 11:08:46 AM"` (2-digit year + AM/PM) — per-field parsers required.

### 3.3 Cross-dataset join proof (single real property, BIN 1006014 / BBL 1004410016)

Taken from the observed w9ak-ipjd sample (418 East 14 Street, Manhattan, block 441, lot 16), then cross-probed:

1. `w9ak-ipjd?bbl=1004410016` → 2 filings incl. `M00855935-I1` ("LOC Issued", Alteration, filed 2023-04-10).
2. `rbx6-tga4?$where=bbl=1004410016` (numeric) → the **same** `job_filing_number M00855935-I1` with `work_permit "M00855935-I1-SG"`, issued 2023-07-05 → **filing→permit join key is `job_filing_number`; permit ID = job_filing_number + work-type suffix**.
3. `52dp-yji6?$where=bin_number=1006014` → boiler compliance filings (boiler_id `10000021095Y0001`, report_status "Accepted") → **BIN join works into Safety Boiler**.
4. `pkdm-hqz6?bin=1006014` → `[]`; `xubg-57si?bin=1006014` → `[]`; `e5aq-a4j2?bin=1006014` → `[]` (valid no-match responses; positives proven separately with each dataset's own observed BINs 1001905 / 1014176 / 1001627). Empty result = `[]` with HTTP 200 — the connector must treat this as "no records", not an error.
5. **`job_filing_number` format observed:** `{borough letter M|B|Q|S|X}{8 digits}-I1` for initial filings; `-I1-EL` suffix on electrical (`B00334201-I1-EL`); juyv-2jek description states PAA rows get a `P1` suffix. Child tables (xmmq-y7za, juyv-2jek) join ONLY via `job_filing_number` (+ `device_id` for devices).

### 3.4 Property-profile join strategy (recommendation)

BIN is the only key present in ALL location-bearing family datasets (BBL missing from xubg-57si and 52dp-yji6) → property-profile DOB NOW lookups should fan out on **BIN primarily** (from Geoclient/PLUTO resolution) with **BBL as corroboration** where present, then reconcile borough/block/lot text against the canonical lot. Address strings are display-grade only (observed embedded multi-space: `"EAST   14 STREET"`).

## 4. S3 — Freshness: stated cadence vs observed rowsUpdatedAt

- Stated: `Update Frequency: Daily` + `Automation: Yes` on 10 of 11; `Every weekday` on xubg-57si.
- Observed on 2026-07-17: **all 11 datasets have `rowsUpdatedAt` within the previous 24 h** (2026-07-16 14:16Z–21:48Z; raw epochs preserved in the views extract, converted with `datetime.fromtimestamp(..., timezone.utc)` — machine conversion, no manual arithmetic).
- **Verdict: no `degraded_suspected` flag anywhere in the DOB NOW family** (M1-T003 ZTLDB precedent checked and not triggered). 2026-07-16 was a Thursday; the weekday-cadence xubg-57si value is consistent.
- Monitoring plan: `rowsUpdatedAt` is meaningful for these tabular datasets (agent-memory rule) — poll it per run; alert if age > 3 days (business-day tolerant). There is no per-record version field in the samples; per-record vintage must be stamped from retrieval time + `rowsUpdatedAt` (registry drafts note this).

## 5. Failure/limit behaviors observed (for the contract-test pack)

- **Schema drift signature:** requesting a nonexistent column (`filing_date` on e5aq-a4j2) → HTTP 400, `query.soql.no-such-column`, and the error body enumerates the dataset's actual columns (verbatim fixture `query_e5aq-a4j2_bad-column_http400.json`). Same signature class as the PLUTO G1 finding.
- **Pagination/limits (official Socrata docs, retrieved 2026-07-17):** `$limit` defaults to 1,000; "Version 2.0 endpoints have a maximum $limit of 50,000; Version 2.1 and 3.0 endpoints have no maximum" (dev.socrata.com/docs/queries/limit.html, verbatim). All 11 datasets are `newBackend: true` (2.1). Stable paging requires `$order` (use `:id`). Note: `dev.socrata.com/docs/paging(.html)` now 404s — cite the LIMIT clause page.
- **Rate limits/auth:** tokenless requests are IP-throttled in a shared pool; app token lifts throttling (dev.socrata.com/docs/app-tokens, evidenced at M1-T001 E7; token acquisition remains HUMAN_ACTIONS §7). All research here ran tokenless without hitting HTTP 429.
- **nyc.gov bot wall (recorded attempt):** `https://www.nyc.gov/site/buildings/industry/dob-now.page` → HTTP 403 on 2026-07-17 → DOB NOW module rollout dates/phase-in schedule not confirmable from this environment (OQ-1).

## 6. S4 — Explicit rule-outs (plausible-but-wrong / deprecated datasets)

All five verified live via `api/views` on 2026-07-17 (same extract fixture); each is OUT of the DOB NOW family and belongs to the legacy/BIS research task:

1. **`ipu4-2q9a` DOB Permit Issuance** — verbatim description: "**Note: This dataset only includes permits issued in the Buildings Information System (BIS), most current permits are now issued in DOB NOW -- see the DOB NOW: Build – Approved Permits [rbx6-tga4] dataset.**" Rows updated 2026-07-16 (still live — BIS is not dead, just a different family).
2. **`ic3t-wcy2` DOB Job Application Filings** — verbatim: "This dataset does not include jobs submitted through DOB NOW. See the DOB NOW: Build – Job Application Filings [w9ak-ipjd] dataset for DOB NOW jobs." Rows updated 2026-07-16.
3. **`bs8b-p36w` DOB Certificate Of Occupancy** — verbatim: "contains all Certificates of Occupancy issued from 7/12/2012 to March 2021 ... For COs issued since March 2021, see DOB NOW: Certificate of Occupancy [pkdm-hqz6]." Rows updated 2026-07-16 (still-updating legacy window).
4. **`e98g-f8hy` Property Data (Buildings Information System) - Now Retired** — verbatim: "This dataset is being replaced. Please visit ... ipu4-2q9a for DOB permit data" — retired BIS product; name itself carries "Now Retired".
5. **`bty7-2jhb` Historical DOB Permit Issuance** — verbatim: "DOB Permit Issuance has since been updated to incorporate this date range, and this historical dataset is now redundant." `Update Frequency: Historical data`, `Automation: No`, rowsUpdatedAt frozen 2018-08-07 — redundant by DOB's own statement.

### 6.1 Relationship of the DOB NOW family to permit-issuance data (required by packet)

NYC permit/job/CO data is **split across two live systems by filing channel, not by date alone**:

- **Job filings:** BIS-channel jobs → `ic3t-wcy2`; DOB NOW jobs → `w9ak-ipjd` (electrical/elevator/LAA jobs in their own DOB NOW datasets). Both update daily; a complete per-property job history REQUIRES both families.
- **Permits:** BIS-issued permits → `ipu4-2q9a`; DOB NOW-approved permits → `rbx6-tga4` (+ dm9a-ab7w electrical, kfp4-dz4h elevator, xxbr-ypig LAA). DOB's own note says "most current permits are now issued in DOB NOW."
- **COs:** clean official date boundary — `bs8b-p36w` up to March 2021, `pkdm-hqz6` since. Observed nuance: pkdm-hqz6 `job_filing_name "120954770"` is a 9-digit BIS-style job number — the DOB NOW CO module issues COs for jobs that originated in BIS, so CO records do not imply a DOB NOW job filing exists.
- The per-work-type phase-in schedule of DOB NOW (which work types moved when) is on 403-walled nyc.gov pages → OQ-1. The M2 conflict engine must therefore treat "no DOB NOW record" as *channel-dependent absence*, never as "no activity" — the BIS family must be researched (next task) before DOB facts are labeled complete.

### 6.2 Cross-channel/data-quality discrepancies recorded (not corrected)

1. **Join-key pollution (rbx6-tga4):** first sample record has `job_filing_number: "Permit is no"` and `work_permit: "Permit is not yet issued"` with `permit_status: "Signed-off"` (verbatim fixture `sample_rbx6-tga4.json`) — placeholder prose truncated to 12 chars inside the key column. Connector must validate key format `^[A-Z]\d{8}-` and route violations to review, and must not assume every row of "Approved Permits" carries an issued permit ID.
2. **Borough casing inconsistency across datasets for the same BBL** (§3.2).
3. **Non-ISO date strings in text columns** (§3.2, boiler + CO issuance).
4. **Documentation defects (verbatim):** juyv-2jek description says "The collection includes all **electrical** applications submitted ... since December 11, 2017" inside the *elevator* device dataset (copy/paste error; the same sentence dates the DOB NOW launch of that module); pkdm-hqz6 description typo "anbd"; e5aq-a4j2 description typo "inspetion". Recorded for the G1 reviewer; the December 11, 2017 module-launch date should be treated as unverified for elevators (OQ-1).
5. **Facades filings predate DOB NOW:** xubg-57si (a "DOB NOW" dataset) contains `filing_date "2011-05-13"` (cycle 7, observed) — migrated legacy FISP cycles are included; coverage depth of pre-DOB NOW cycles unquantified (OQ-4).
6. **e5aq-a4j2 vs juyv-2jek device universes:** e5aq (compliance) has `device_number` (e.g. `1P14518`), juyv (build) has `device_id`/`bis_nyc_device_id` — whether these share a namespace is unverified (OQ-5).

## 7. Proposed contract-test fixture pack (per ACCEPTANCE_SCENARIO_STANDARD connector pack)

Captured now under `docs/research/fixtures/m1-t007/` (fixtures 1–5 already exist); remainder at connector build:

1. Real official response: `sample_<4x4>.json` ×11 (verbatim, 2 records each). ✔
2. No-match: `query_pkdm-hqz6_bin_1006014_nomatch.json`, `query_xubg-57si_bin_1006014_nomatch.json`, `query_e5aq-a4j2_bin_1006014_nomatch.json` (HTTP 200 `[]`). ✔
3. Schema-drift/failure signature: `query_e5aq-a4j2_bad-column_http400.json` (HTTP 400 `query.soql.no-such-column`). ✔
4. Join fixtures: `query_w9ak-ipjd_bbl-eq_*.json` + `query_rbx6-tga4_bbl-numeric-where_*.json` (same job both sides). ✔
5. Serialization: `query_rbx6-tga4_select-bbl-serialization.json`. ✔
6. At build: pagination fixture (`$limit`/`$offset`/`$order=:id` page pair), HTTP 429 rate-limit capture (cannot be forced politely now), ambiguous/multi-match per-BIN fixture, key-pollution rejection fixture derived from §6.2-1, per-field date-parser fixtures (boiler + CO issuance strings), provenance/retrieval-timestamp assertions.

## 8. Connector implementation plan (PLAN ONLY — no code in this task)

Per-BIN (primary) and per-BBL (corroboration) SODA queries with app token from secrets; per-dataset field maps (naming drift §3.1); borough normalization to borocode; join-key format validation; per-field date parsers; empty-array = no-facts; schema-drift check each scheduled run comparing the `api/views` columns array against the stored inventory (drift signature HTTP 400 handled as hard alert); freshness monitor on `rowsUpdatedAt` (>3 business days → degraded); raw records + retrieval timestamp + `rowsUpdatedAt` persisted to `raw_source_records`/`property_source_facts`. Child tables (xmmq-y7za, juyv-2jek) fetched only by `job_filing_number` fan-out from their parents. All ingestion on Render workers; nothing citywide is downloaded locally.

## 9. OPEN QUESTIONS ledger

| OQ | Question | Why it can't be answered now | Owner action needed |
| --- | --- | --- | --- |
| OQ-1 | DOB NOW per-work-type rollout/phase-in dates (when each job/permit type stopped being filed in BIS), incl. verification of the "December 11, 2017" module-launch sentence found in a defective description | nyc.gov 403 to non-browser sessions (recorded: `www.nyc.gov/site/buildings/industry/dob-now.page` → 403, 2026-07-17) | Browser-capable capture session (same session can close M1-T001/T003 OQ backlog) |
| OQ-2 | Content extraction of the 11 official data-dictionary XLSX attachments (field definitions, value domains, null semantics beyond observation) | XLSX binary; attachment API serves octet-stream; no s-media twin known for DOB docs; local parsing tooling deferred (low-storage) | Run extraction on Codespaces/Render at connector build; assetIds already captured |
| OQ-3 | Whether number-typed `bbl` (rbx6-tga4, xxbr-ypig) / `bin_number` (52dp-yji6) ever serialize with decimal artifacts under `$select` aggregation/casting paths | Single-probe evidence only (no artifact observed); PLUTO precedent (C6) proves the platform can do it | None — connector normalizes defensively; add contract test |
| OQ-4 | Depth/completeness of migrated pre-DOB NOW facades cycles in xubg-57si (observed cycle-7 filing dated 2011) | Not stated in description; dictionary is OQ-2 | Dictionary extraction + per-cycle count queries at connector build |
| OQ-5 | Device-ID namespace relationship between e5aq-a4j2 `device_number` and juyv-2jek `device_id`/`bis_nyc_device_id` | Not documented in descriptions | Dictionary extraction (OQ-2) + sampled join experiment |
| OQ-6 | Whether additional DOB NOW Safety modules (e.g. gas piping, cranes, retaining walls, parking structures) publish Open Data datasets not matching the "DOB NOW" catalog search | Catalog search is name-based; a differently-named dataset would not surface | Category-browse pass (`browse?Data-Collection`…) in the BIS/legacy task or at G1 |
| OQ-7 | Socrata app token (removes shared-pool throttling for production connectors) | Requires owner account action | Already tracked as HUMAN_ACTIONS §7 (M1-T001) — reconfirmed needed here |

## 10. Source register (every channel fetched live by the producer, 2026-07-17)

| # | URL | Result | Used for |
| --- | --- | --- | --- |
| D1 | `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB%20NOW&limit=30` | 200, 21 results | discovery |
| D2 | `https://data.cityofnewyork.us/api/catalog/v1?q=DOB%20NOW&limit=30` | 200, identical 21 | discovery corroboration |
| D3 | `https://data.cityofnewyork.us/api/views/<4x4>.json` ×16 (11 family + 5 rule-outs) | 200 each | identity, columns, cadence, attachments, descriptions |
| D4 | `https://data.cityofnewyork.us/resource/<4x4>.json?$limit=2` ×11 | 200 each | verbatim samples, null-omission behavior |
| D5 | Targeted SODA queries ×11 (fixtures README) | 200 ×10, 400 ×1 (deliberate) | join semantics, no-match, serialization, drift signature |
| D6 | `.../resource/<4x4>.json?$select=count(*) as n` ×6 | 200 | scale |
| D7 | `https://data.cityofnewyork.us/api/views/w9ak-ipjd/files/978bdfe8-...` (HEAD) | 200, octet-stream, 74,405 B | attachment channel proof |
| D8 | `https://www.nyc.gov/site/buildings/industry/dob-now.page` | **403** | recorded bot-wall attempt (OQ-1) |
| D9 | `https://catalog.data.gov/dataset/dob-now-build-job-application-filings` | 200; raw grep hit `w9ak-ipjd` | mirror corroboration |
| D10 | `https://catalog.data.gov/api/3/action/package_search?...` | **404** | recorded dead channel |
| D11 | `https://dev.socrata.com/docs/queries/limit.html` | 200 | pagination limits verbatim |
| D12 | `https://dev.socrata.com/docs/paging` and `/docs/paging.html` | **404 ×2** | recorded doc restructure |
| D13 | `https://dev.socrata.com/docs/app-tokens` | not re-fetched; cited from accepted M1-T001 evidence E7 | auth/rate limits |
