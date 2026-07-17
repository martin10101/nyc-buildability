# M1-T008 — Official-Source Research: DOB-wide legacy and non-DOB-NOW sources

- **Task:** M1-T008 (research-only; scope BOUND by `project-control/reports/M1-T007-owner-connector-directives.md` §6; PRD §8.1 families "BIS or equivalent historical property records", "Certificates of Occupancy", "DOB violations and complaints")
- **Producer:** official-source-researcher
- **All retrievals:** 2026-07-17, 16:15–16:21 UTC, live, tokenless, from `data.cityofnewyork.us` (server-time anchor: `eabe-havv` metadata `rowsUpdatedAt` epoch 1784304931 = 2026-07-17T16:15:31Z, refreshed seconds before capture)
- **Fixtures:** `services/api/tests/fixtures/dob_legacy/` (verbatim SODA responses; exact URLs in that directory's README)
- **Terminology guard (owner directive):** `bf97-mjsy` is the **DOB Incident Database** source (Construction-Related Incidents). It is **not** a BIS dataset and is never described as BIS anywhere in this document.
- **Scope:** the five BIS-family datasets (`ipu4-2q9a`, `ic3t-wcy2`, `bs8b-p36w`, `e98g-f8hy`, `bty7-2jhb`) + the three non-DOB-NOW/non-BIS DOB sources flagged out of M1-T007 (`bf97-mjsy`, `g76y-dcqj`, `855j-jady`) + the DOB-wide legacy violations/complaints datasets required by PRD §8.1 and surfaced by catalog discovery (`3h2n-5cm9`, `6bgk-3dad`, `eabe-havv`, `6v9u-ndjg`). Research only — no connector code.

## 1. Executive summary

12 datasets researched with live schema/sample evidence; 4 additional candidates examined and rejected (§8). Highest-impact findings for connector design:

1. **`ic3t-wcy2` (BIS Job Application Filings) has systemic BBL-column pollution:** 884,315 of 2,715,651 rows (32.6%) carry a **7-character value (a BIN) in the `bbl` column**; 29,120 more are null. Observed directly on the M1-T007 anchor building: two rows of the *same job* return `bbl:"1006014"` (the BIN) and `bbl:"1004410016"` (fixture `query_ic3t-wcy2_bin1006014_bbl-pollution.json`). BBL from this dataset is untrustworthy without format+borocode validation.
2. **`e98g-f8hy` (Property Data (BIS) — Now Retired) is now EMPTY:** `$select=count(*)` → **0 rows**; `$limit=2` → `[]`; yet `rowsUpdatedAt` = 2026-07-15 (the truncation itself was the "update"). There is **no Open Data replacement for the BIS property master** — a permanent channel gap (§6).
3. **`g76y-dcqj` (After Hour Variance Permits) is stale ~3.25 years despite stating "Daily/Automation: Yes":** `rowsUpdatedAt` = 2023-04-18T19:48:11Z; max `variance_start_date_time` = 2024-01-12. A 28-result catalog probe for "after hour variance" found **no successor dataset** → AHV coverage gap from ~2023-04 to present.
4. **Cross-dataset violation duplication is PROVEN, not just documented:** DOB's own dataset notes say "some violations are duplicated in both data sets"; observed concretely — 3h2n-5cm9 (`violation_number "00614"`, `issue_date "20180406"`, type LBLVIO) and 855j-jady (`violation_number "040618LBLVIO00614"`, ISO issue date 2018-04-06) are the same violation; 855j's composite key = `MMDDYY + type + number`. Dedup is mandatory before counting violations.
5. **Legacy date encodings are a minefield:** YYYYMMDD text (3h2n, 6bgk), MM/DD/YYYY text (ipu4, ic3t, eabe), **two formats in one column** (ipu4 `issuance_date` min `01/01/2007` / max `2020-06-05`), `YYYYMMDDHHMMSS` (`eabe.dobrundate`), ISO-in-text (bty7), plus garbage values in official date fields: 3h2n `issue_date` min `"000000"` / max `"Y9990120"`; bs8b `c_o_issue_date` max **2105-11-05** (future-dated CO).
6. **Explicit TEST records exist in production data:** 3h2n-5cm9's first sample row is `house_number:"TEST"`, `street:"RECORD"`, block/lot `"99999"`, comment "DELETED BY CES ON 06/21/91 BECAUSE TEST RECORD" (fixture `sample_3h2n-5cm9.json`).
7. **Block/lot padding is inconsistent across the legacy family:** 5-digit block + 5-digit lot (`00441`/`00016`, ipu4/ic3t/3h2n), 5-digit block + **4-digit** lot (`00441`/`0016`, 6bgk), unpadded (bty7 `4905`/`1`), number-typed unpadded (855j `5042`/`7504`). Same physical lot, three encodings observed.
8. **The two-channel model is confirmed end-to-end on one real building** (BIN 1006014, 418 East 14 St, Manhattan, BBL 1004410016): BIS permit (2002) + BIS job + BIS violations (1994–2018) + ECB summonses (2006–2007) + complaints (1999–2019) here, DOB NOW filings/permits (2023) in M1-T007 — neither channel alone is a complete DOB history.

## 2. S1 — Discovery and live-verified identity

### 2.1 Catalog discovery (recorded queries, both 2026-07-17 ~16:15 UTC)

- `https://data.cityofnewyork.us/api/catalog/v1?q=DOB&limit=100&search_context=data.cityofnewyork.us` → HTTP 200, resultSetSize **82**
- `https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB&limit=100` → HTTP 200, resultSetSize **82**, identical ID set (order differs)

The 82 results contain: the 11 DOB NOW family datasets (M1-T007, unchanged), the 12 in-scope datasets below, the 4 rejected candidates (§8), one `href` asset (`4hxk-b29t` Sustainability Compliance Map), the LL84 energy-disclosure series (out of scope: energy benchmarking, not permit/property history — candidates for a later sustainability task), and non-DOB agency noise (HPD/DCP/DOHMH/OATH…).

### 2.2 Identity of the 12 in-scope datasets

Each verified via `https://data.cityofnewyork.us/api/views/<4x4>.json`, 2026-07-17 ~16:16 UTC (HTTP 200). All 12: `assetType: dataset`, `newBackend: true` (SODA 2.1 → no `$limit` maximum), `provenance: official`, agency custom-field "Department of Buildings (DOB)". Rows counted via `resource/<4x4>.json?$select=count(*)` at 16:17 UTC.

| ID | Official name | Cols | Rows | Update Frequency (stated) | Automation | rowsUpdatedAt (UTC) | Freshness verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ipu4-2q9a | DOB Permit Issuance | 60 | 3,989,420 | Daily | Yes | 2026-07-16T23:27:02Z | fresh |
| ic3t-wcy2 | DOB Job Application Filings | 95 | 2,715,651 | Daily | Yes | 2026-07-16T21:41:30Z | fresh |
| bs8b-p36w | DOB Certificate Of Occupancy | 30 | 143,003 | Daily | Yes | 2026-07-16T20:31:30Z | fresh (fixed window, corrections ongoing) |
| e98g-f8hy | Property Data (Buildings Information System) - Now Retired | 11 | **0** | As needed | No | 2026-07-15T16:22:19Z | **retired AND emptied** |
| bty7-2jhb | Historical DOB Permit Issuance | 60 | 2,428,526 | Historical data | No | 2018-08-07T14:34:20Z | frozen by design |
| bf97-mjsy | Construction-Related Incidents | 20 | 1,326 | Daily | Yes | 2026-07-16T18:46:16Z | fresh |
| g76y-dcqj | DOB After Hour Variance Permits | 24 | 255,300 | Daily | Yes | **2023-04-18T19:48:11Z** | **stale ~3.25 y — stated cadence contradicted** |
| 855j-jady | DOB Safety Violations | 24 | 1,099,638 | Daily | Yes | 2026-07-16T18:07:08Z | fresh |
| 3h2n-5cm9 | DOB Violations | 18 | 2,475,595 | Every weekday | Yes | 2026-07-16T17:40:22Z | fresh |
| 6bgk-3dad | DOB ECB Violations | 46 | 1,823,837 | Every weekday | Yes | 2026-07-16T17:00:37Z | fresh |
| eabe-havv | DOB Complaints Received | 15 | 3,108,970 | Daily | Yes | 2026-07-17T16:15:31Z | fresh (refreshed during this session) |
| 6v9u-ndjg | Building Complaint Disposition Codes | 2 | 160 | As needed | No | 2017-02-08T18:30:25Z | static lookup (acceptable) |

Every dataset has an official data-dictionary XLSX attachment (filenames + assetIds captured in the views responses; e.g. `DD_DOB_Violations_2019-03-19.xlsx` assetId `09445410-995e-40ad-aa44-37049d1f4e4d`); `eabe-havv` additionally attaches `DOBComplaints_complaint_category_list.pdf` (assetId `dc709ed2-7af1-429c-92c9-71ec3a4c23fa`). XLSX/PDF content extraction is deferred to a cloud environment (same OQ class as M1-T007 OQ-2; Socrata attachment API serves octet-stream).

### 2.3 Official boundary statements (verbatim, from `api/views` descriptions, 2026-07-17)

- `3h2n-5cm9`: "This data set includes older civil penalties (commonly referred to as “DOB Violations”) that were issued by the Department of Buildings (DOB) in the Buildings Information System (BIS). For newer civil penalties, see the [855j-jady] DOB Safety Violations data set (**note: some violations are duplicated in both data sets**). Separately, summonses that are issued by DOB but adjudicated by OATH/ECB are in the [6bgk-3dad] DOB ECB Violations data set."
- `855j-jady`: "This data set includes newer civil penalties … that were **issued or payable in DOB NOW**. For older civil penalties, see the [3h2n-5cm9] DOB Violations data set (note: some violations are duplicated in both data sets)."
- `6bgk-3dad`: "This data set includes summonses issued by the Department of Buildings that are **adjudicated by OATH/ECB**."
- `ic3t-wcy2`: "contains all job applications submitted through the Borough Offices, through eFiling, or through the HUB, which have a **'Latest Action Date' since January 1, 2000**. This dataset does not include jobs submitted through DOB NOW."
- `bs8b-p36w` (description, longer form): COs "issued from 7/12/2012 to March 2021"; for later COs see pkdm-hqz6 (M1-T007).
- `e98g-f8hy`: "This dataset is being replaced. Please visit: [ipu4-2q9a] for DOB permit data" — but ipu4-2q9a is permit data, **not** a property-master replacement; the property master has no Open Data successor.
- `bty7-2jhb`: "permits issued … from 1989 to 2013 … DOB Permit Issuance has since been updated to incorporate this date range, and **this historical dataset is now redundant**."
- `g76y-dcqj`: "List of all after-hours variances issued in DOB NOW" (a DOB NOW-module output researched here per owner directive §6).
- `bf97-mjsy`: "This dataset includes construction-related incidents recorded in through the **Department of Buildings (DOB) Incident Database**." [sic] — system of record is the DOB Incident Database.
- `eabe-havv`: "This is the **universe of complaints** received by Department of Buildings (DOB). It includes complaints that come from 311 or that are entered into the system by DOB staff." (Description also links a complaint-category PDF on `www1.nyc.gov` — 403-walled channel, OQ-3.)

## 3. Per-source field evidence (S1/S7 — all from live `api/views` columns arrays + `$limit=2` samples; nothing guessed)

### 3.1 BIS permit/job/CO family

**`ipu4-2q9a` DOB Permit Issuance (60 cols).** Mangled underscore field names are official: `bin__`, `house__`, `job__`, `job_doc___`, `permit_sequence__`, `permittee_s_phone__`, `permittee_s_license__`. All date fields `text` (observed `"06/17/2020"`); only `dobrundate` is `calendar_date`. `bbl` is `number` and **nullable while block/lot are populated** — 119,673 rows (3.0%) have null `bbl` (`$where=bbl is null`, 16:19 UTC); the very first sample record omits `bbl` (SODA null-omission). Block/lot zero-padded 5-digit (`"06861"`, `"00067"`). Borough UPPER (`"BROOKLYN"`, `"MANHATTAN"`). `special_district_1/2` present. Coverage observed via LIKE probes: 2,985 rows `issuance_date like '%/1989'`; 4,380 rows `like '%/2026'` → issuance coverage 1989→present (backfill of the bty7-2jhb range confirmed). WARNING: lexicographic `min/max(issuance_date)` returned `01/01/2007`/`2020-06-05` — **useless as a date range** (MM/DD/YYYY sorts by month; and an ISO-format stray value surfaces as "max"), and direct proof that this text column mixes two date formats.

**`ic3t-wcy2` DOB Job Application Filings (95 cols).** The zoning-relevant legacy dataset: number-typed `existing_zoning_sqft`, `proposed_zoning_sqft`, `enlargement_sq_footage`, `street_frontage`, `existingno_of_stories`, `proposed_no_of_stories`, `existing_height`, `proposed_height`; text `existing_dwelling_units`/`proposed_dwelling_units`; `zoning_dist1/2/3`, `special_district_1/2`, `landmarked`, `little_e` (E-designation flag), `city_owned`, `loft_board`, `adult_estab`, `building_class`. Money as `$`-prefixed strings (`"initial_cost":"$37300.00"`). Dates MM/DD/YYYY text. `bbl` text with the §1-1 pollution (32.6% BIN-in-BBL). Job key `job__` 9-digit borough-prefixed (`"440673852"`, `"103208002"`); `doc__` zero-padded (`"01"`). Coverage: actions since 2000-01-01 by official statement; LIKE probes: 48,159 rows `latest_action_date like '%/2000'`, 8,941 `like '%/2026'`.

**`bs8b-p36w` DOB Certificate Of Occupancy (30 cols).** Has BOTH `bin_number` and `bin` (same value `"2102454"` observed in one record), plus Socrata platform columns: `location` (complex type with nested `human_address` JSON-string) and five `:@computed_region_*` number columns — the only dataset in this scope with them (they are Socrata-derived, not DOB facts; exclude from provenance-bearing facts). `c_o_issue_date` is a true `calendar_date`: min 2012-07-12 (matches the official window start exactly), **max 2105-11-05 — future-dated garbage in an official field**. Borough title case (`"Bronx"`). Block/lot 5-digit padded. `bbl` text 10-digit. No-match behavior: `bin=1006014` → HTTP 200 `[]`.

**`e98g-f8hy` Property Data (BIS) — Now Retired (11 cols).** Columns are permit-shaped (`permit_bin` number, `permit_application_job_number` number, dates `calendar_date`) — but the dataset now returns **zero rows** (count 0; `$limit=2` → `[]`, fixture `sample_e98g-f8hy_empty.json`). Disposition: **never connect; record as evidence that the BIS property master left Open Data.**

**`bty7-2jhb` Historical DOB Permit Issuance (60 cols).** Same logical shape as ipu4-2q9a but with CLEAN field names (`bin`, `job`, `permit_sequence`) and ISO-format dates inside `text` columns (`"2013-04-24T00:00:00"`); `min/max(issuance_date)` = 1989-05-11 → 2013-04-24, matching the stated 1989–2013 window. Block/lot UNPADDED (`"4905"`, `"1"`). Frozen since 2018-08-07; officially "now redundant" (ipu4-2q9a backfill confirmed by the 1989 LIKE probe above). Disposition: **never connect** (keep as a reconciliation cross-check candidate only if an ipu4 backfill defect is ever suspected).

### 3.2 Violations, summonses, complaints (M2 risk-fact family)

**`3h2n-5cm9` DOB Violations (18 cols; BIS-channel civil penalties).** ALL columns text, including `issue_date` (YYYYMMDD, e.g. `"19940901"`; garbage observed: min `"000000"`, max `"Y9990120"`). `boro` is a DIGIT (`"1"`, `"5"`) — third borough encoding in the DOB universe (vs "Manhattan"/"MANHATTAN"). No lat/long, no BBL column — keys are `bin` + `boro`/`block`/`lot` (5-digit padded). `bin` can be ABSENT (the TEST record omits it). Primary key `isn_dob_bis_viol`; composite `number` field (`"V103188E1391F/03"`); `ecb_number` cross-references 6bgk-3dad. `violation_category` encodes active/dismissed with `*` convention: `V*-DOB VIOLATION - DISMISSED` 1,164,687 / `V*-…Resolved` 673,489 / `V-DOB VIOLATION - ACTIVE` 556,639 / work-without-permit and unserved-ECB variants (group-by, 16:19 UTC). `violation_type` values carry embedded whitespace padding (`"E-ELEVATOR       …ELEVATORREQUIRED"`). Contains literal TEST records (§1-6).

**`6bgk-3dad` DOB ECB Violations (46 cols; OATH/ECB-adjudicated summonses).** Dates YYYYMMDD text (`hearing_date "20090413"`); `hearing_time` unpadded text (`"830"`). `boro` digit; lot 4-digit padded (`"0016"`) — differs from its sibling 3h2n (5-digit `"00016"`) for the SAME lot. Official misspelling `penality_imposed` (number) — field-map exactly, do not "fix". 10 repeated `infraction_code{n}`/`section_law_description{n}` column pairs (denormalized law citations, whitespace-padded, e.g. `"28-301.1 … FAILURE TO MAINTAIN…"`). `dob_violation_number` links toward DOB violation numbering; `respondent_*` PII-adjacent fields present (owner/respondent names and addresses — treat per §17 log-redaction rules). Penalty amounts number-typed (`penality_imposed`, `amount_paid`, `balance_due`).

**`855j-jady` DOB Safety Violations (24 cols; DOB NOW-channel civil penalties).** True `calendar_date` issue dates; number-typed `block`/`lot`/`bbl`/`community_board`; `violation_number` is composite `VIO-…-{cycle}-{seq}` or `MMDDYY+TYPE+NNNNN` (both observed: `"VIO-FTC-PS-UNSAFE-202712-0181058"`, `"040618LBLVIO00614"`). `violation_issue_date` min **1989-10-12** despite the "newer civil penalties" description — old BIS-era violations that became *payable in DOB NOW* are included → date alone does NOT partition 3h2n vs 855j; dedup by violation identity is required (§1-4). `device_type` group-by (16:19 UTC): Boiler 443,832; Elevators 262,889; AEUHAZ 163,669; Gas Piping - LL152 110,668; Benchmarking - LL84 61,730; Facades 18,704; Energy Grade - LL33 15,833; Retro-Commissioning - LL87 14,144; Retaining Walls 2,441; Emergency Power 1,315; Sprinklers 1,275; GHG Emissions - LL97 918 (0 null device_type) — i.e., this dataset is ALSO the civil-penalty ledger for the sustainability local laws (LL84/33/87/97/152), directly relevant to feasibility risk flags. Future `cycle_end_date` values are semantically valid (compliance-cycle end, `"2027-12-31"` observed).

**`eabe-havv` DOB Complaints Received (15 cols).** **No BBL, no block/lot, no borough column** — property keys are `bin` + `house_number`/`house_street` + `community_board` (borough only derivable from BIN 1st digit / community_board 1st digit / `unit` strings like `"BKLYN"`). `date_entered`/`disposition_date`/`inspection_date` MM/DD/YYYY text; `dobrundate` is `YYYYMMDDHHMMSS` text (`"20260716000000"`) and — decisive for versioning — `count(distinct dobrundate)` = **1**: the whole 3.1M-row dataset carries a single run-date, i.e. **daily full-snapshot replacement semantics**, so per-record change tracking must be done by our ingestion diffing, not by source timestamps. Coverage probes: 22,523 rows `date_entered like '%/1989'`; 70,398 `like '%/2026'` → complaints back to at least 1989, actively growing. `complaint_category` and `disposition_code` are code values (`"1X"`, `"I2"`, `"L2"`).

**`6v9u-ndjg` Building Complaint Disposition Codes (2 cols, 160 rows, static).** Lookup `code`→`disposition`. Join proven live: `?code=I2` → `"NO VIOLATION WARRANTED FOR COMPLAINT AT TIME OF INSPECTION"` — resolves the `disposition_code` values observed in eabe-havv for the anchor building. Frozen 2017 ("As needed"); category codes for `complaint_category` are in the eabe PDF attachment / 403-walled nyc.gov PDF (OQ-3) — the 2-col table covers dispositions only.

### 3.3 Non-BIS, non-DOB-NOW flagged sources

**`bf97-mjsy` Construction-Related Incidents — system of record: DOB Incident Database (20 cols).** Re-verified this session (metadata 16:16 UTC; count + min/max 16:17–16:18 UTC): 1,326 rows; `incident_date_mm_dd_yyyy` (a true `calendar_date` despite the name) min 2024-01-03 / max 2026-07-14; `rowsUpdatedAt` 2026-07-16 — matches the M1-T007 C1v2 disposition exactly, no drift. Keys: `bin` text 7-digit; `address_bbl` text 10-digit; `boro` title case; per-incident `fatality`/`injury` counts. No-match behavior: `bin=1006014` → HTTP 200 `[]`. Classification unchanged per owner C1v2: **documented secondary/future source feeding the M2 property-history/risk fact stage** — small, short window (2024→), but a direct site-risk signal.

**`g76y-dcqj` DOB After Hour Variance Permits (24 cols).** DOB NOW-module output (description §2.3), flagged out of M1-T007 into this task. Schema notable: only `checkbox`-typed columns in the DOB universe so far (`residence_200ft`, `enclosed_work`, `demolition`, `crane_use` → JSON `true`/`false`); DOB NOW-format `workpermitnumber` (`"X00605810-I1-SF"`); separate `ahv_permit_number` namespace (`"X3901086"`); `variancetype`/`reasonforvariance` categorical text. **Stale:** stated Daily/Yes but rowsUpdatedAt 2023-04-18; variance dates end 2024-01-12 (renewals booked ahead of the freeze); no successor dataset found (catalog probe `q=after hour variance`, 28 results, 16:19 UTC — only g76y-dcqj is relevant). Disposition: connect late, label **historical AHV coverage ending ~2023-04/2024-01**, and monitor for revival; AHV activity is a construction-intensity signal, not a property-profile fact.

## 4. S1/S4 — Cross-channel join proof on one real building (BIN 1006014 / BBL 1004410016, 418 East 14 Street, Manhattan, block 441 lot 16 — same anchor as M1-T007)

All queries 2026-07-17 16:19 UTC (fixtures re-captured 16:21 UTC):

| Dataset | Query | Result |
| --- | --- | --- |
| ipu4-2q9a | `bin__=1006014` | 1 permit: job `103208002`, A2, EW, ISSUED `10/07/2002`, block `00441` lot `00016`, `bbl "1004410016"`, `"MANHATTAN"` |
| ic3t-wcy2 | `bin__=1006014` | 2 rows, same job `103208002`: one with `bbl:"1006014"` (BIN-in-BBL pollution), one with `bbl:"1004410016"` |
| bs8b-p36w | `bin=1006014` | `[]` (no CO in the 2012–2021 window — legitimate for an older building; valid no-match) |
| 3h2n-5cm9 | `bin=1006014` | violations `19940901`(LL6291, dismissed), `19970916`(LL6291, dismissed), `20180406`(LBLVIO, **ACTIVE**) |
| 6bgk-3dad | `bin=1006014` | ECB summonses `20060605`(ACTIVE), `20070403`, `20070703` — lot serialized `0016` (4-digit) |
| eabe-havv | `bin=1006014` | complaints `04/29/1999`, `11/10/2005`, `12/30/2019` (all CLOSED, disposition `I2`) |
| 855j-jady | `bin=1006014` | 1 violation `040618LBLVIO00614` = the SAME 2018 LBLVIO violation as in 3h2n-5cm9 (duplication proof) |
| bf97-mjsy | `bin=1006014` | `[]` (valid no-match) |

Combined with M1-T007 (same BIN: DOB NOW filing `M00855935-I1` 2023, permit `M00855935-I1-SG`, boiler compliance filings): **a single building's DOB history spans both channels and five decades of encodings.** BIN fan-out remains the primary join strategy (eabe-havv and 3h2n-5cm9 have no reliable/any BBL; ic3t's BBL is polluted); BBL is corroboration-only in the legacy family, weaker than in DOB NOW.

Failure signature re-confirmed on the legacy channel: `ipu4-2q9a.json?$select=not_a_real_column` → HTTP 400 `query.soql.no-such-column` with full column enumeration in the error body (fixture `query_ipu4-2q9a_bad-column_http400.json`) — same drift-detection contract as PLUTO/DOB NOW.

## 5. S3 — Auth, rate limits, pagination

- All 12 datasets served tokenless over HTTPS with HTTP 200; no 401/403/429 observed across ~60 requests in 6 minutes (16:15–16:21 UTC).
- Tokenless requests share a pooled IP throttle; an app token lifts it (official: `dev.socrata.com/docs/app-tokens`, evidenced at M1-T001 E7; token acquisition remains a HUMAN_ACTIONS item). Production connectors must use a token.
- `$limit` default 1,000; all 12 are `newBackend: true` (SODA 2.1) → no `$limit` maximum (official: `dev.socrata.com/docs/queries/limit.html`, verbatim capture at M1-T007 §5). Stable pagination requires `$order` (use `:id`).
- SoQL observed working on these datasets this session: `count(*)`, `min`/`max`, `like`, `is null`, `group`, `length()`, `count(distinct …)` — the LIKE/length probes in §3 are reusable as cheap data-quality monitors.

## 6. S4 — Channel-coverage labeling (per directive §5)

Directive §5: until BIS-family reconciliation exists, UI results must say "DOB NOW channel coverage", never "complete DOB records". With this research, per-family labels become:

| Fact family | BIS/legacy channel | DOB NOW channel | Gaps that remain even with BOTH connected |
| --- | --- | --- | --- |
| Job filings | ic3t-wcy2 (actions since 2000-01-01) | w9ak-ipjd (+electrical/elevator/LAA) | jobs with no action since 2000 (BIS-web only); per-work-type migration dates (OQ-1/T007) |
| Permits | ipu4-2q9a (issued 1989→present for BIS-channel permits) | rbx6-tga4 (+dm9a-ab7w, kfp4-dz4h, xxbr-ypig) | pre-1989 permits (paper/microfilm); bty7-2jhb adds nothing (redundant) |
| Certificates of Occupancy | bs8b-p36w (2012-07-12→March 2021) | pkdm-hqz6 (since ~March 2021) | **pre-2012-07 COs — only scanned images in BIS web/DOB NOW portal, no dataset** |
| Civil penalties ("DOB Violations") | 3h2n-5cm9 (BIS-issued, 1988→present observed) | 855j-jady (issued/payable in DOB NOW; includes migrated 1989+ items) | none by date — but **overlap requires dedup**, not union |
| OATH/ECB summonses | 6bgk-3dad (single dataset for both eras; 2009/2006 observed, range unquantified — text dates) | (same dataset) | hearing outcomes deeper than fields provided → OATH datasets (separate agency, out of scope) |
| Complaints | eabe-havv ("universe of complaints", 1989→present observed) | (same dataset per official description) | category-code meanings pending dictionary/PDF extraction (OQ-3) |
| After-hours variances | — | g76y-dcqj **frozen ~2023-04** | **AHV activity 2023-04→present has NO Open Data source** |
| Construction incidents | — (separate system: DOB Incident Database) | — | bf97-mjsy covers 2024-01→present only; earlier incidents have no dataset |
| BIS property master (existing-building profile) | e98g-f8hy **EMPTY** | — | **no Open Data source**; existing-building facts must come from PLUTO/Geoclient/COs, or browser-grade BIS web (bot-walled) |
| Stalled sites | i296-73x5 (currently-active list, daily) | — | historical stall spells not retained (current-status snapshot) |

Labeling rule for M2: once Stage A of §7 lands, per-building DOB history may be labeled "BIS + DOB NOW channel coverage (records since 1989/2000 by family)" with the gap column above surfaced as explicit unsupported/missing coverage; "complete DOB records" remains impossible and must never be claimed.

## 7. S5 — Staged connector priority recommendation (per directive §4)

Rationale anchor: directive §4 puts w9ak-ipjd + rbx6-tga4 + pkdm-hqz6 first for the DOB property-history view; directive §5 makes BIS reconciliation the precondition for honest labeling. Therefore:

- **Stage A — complete the two-channel history spine (immediately after or alongside the first DOB NOW connectors):** `ic3t-wcy2`, `ipu4-2q9a`, `bs8b-p36w`. These are the legacy twins of the three first-priority DOB NOW datasets; without them every DOB fact must carry the weaker "DOB NOW channel" label. Mandatory parser hardening from this research: BIN-primary fan-out; BBL format+borocode validation (reject 7-char BBLs → recompute from boro/block/lot); zero-padding normalization (5/5, 5/4, unpadded variants); MM/DD/YYYY + mixed-format date parsing; `$`-currency strip; TEST-record quarantine (`block='99999'` + `house_number='TEST'`); future-date rejection window (2105 CO observed); `:@computed_region_*`/`location` exclusion from provenance facts.
- **Stage B — risk-fact family (M2 risk stage, after Stage A):** `6bgk-3dad`, `855j-jady`, `3h2n-5cm9` as one dedup-aware violations connector (order within stage: 6bgk first — richest adjudication facts; then 855j+3h2n together, since neither is meaningful alone given proven duplication), plus `eabe-havv` with the `6v9u-ndjg` lookup embedded as a seeded reference table. YYYYMMDD parsers, digit-boro mapping, `Y999…`/`000000` garbage-date quarantine, snapshot-diff versioning for eabe (single `dobrundate` proof), PII-aware handling of 6bgk respondent fields.
- **Stage C — secondary/contextual (contract now, connect when M2 risk UI needs them):** `bf97-mjsy` (per owner C1v2: documented secondary/future; injuries/fatalities per BIN), `i296-73x5` (active stalled-site flag; current-status snapshot), `g76y-dcqj` (historical AHV only; hard-label the 2023 staleness; poll metadata for revival).
- **Never connect:** `bty7-2jhb` (officially redundant; range confirmed inside ipu4-2q9a), `e98g-f8hy` (empty).

## 8. S6 — Candidates examined and REJECTED (evidence-based, no padding)

All examined via live `api/views` metadata + columns arrays, 2026-07-17 ~16:16–16:20 UTC:

1. **`t8hj-ruu2` DOB License Info** — REJECTED for this scope. Entity is the *licensee* (person/business): key columns `license_type`, `license_number`, `last_name`, `business_*`; the `bin`/`bbl` number columns geocode the licensee's business address, not a regulated property. Fresh daily, but it contributes no property-profile or property-risk fact. (Possible far-future use: permit-party enrichment.)
2. **`ndq3-kuef` DOB Disciplinary Actions** — REJECTED. 7 columns (`year`,`date`,`license_type`,`license_no`,`name`,`company`,`disposition`): professional-conduct actions with **no BIN/BBL/address columns at all** — cannot attach to a property.
3. **`iz2q-9x8d` DOB Cellular Antenna Filings** — REJECTED as a standalone connector. BIS-channel antenna job-filing slice (`job__`/`bin__`/`block`/`lot` shape); `rowsUpdatedAt` frozen **2024-01-02** despite stated "Daily/Yes"; antenna work is marginal to development feasibility. Whether its rows also appear in ic3t-wcy2 was NOT verified (recorded as unknown, not assumed).
4. **`nyis-y4yr` DOB Sign Application Filings** — REJECTED for M2. Same BIS filing shape (72 cols incl. sign geometry); `rowsUpdatedAt` frozen **2024-01-03** despite stated "Daily/Yes"; signage filings are not a feasibility input for the current product scope.

(Also examined, NOT rejected: `i296-73x5` DOB Stalled Construction Sites — 8 cols, BIN-keyed, complaint-linked, fresh daily → classified Stage C secondary, §7.)

## 9. Proposed contract-test fixture pack

Captured now under `services/api/tests/fixtures/dob_legacy/` (26 files, ~77 KB, verbatim; URL-per-file table in its README): 11 samples (incl. the empty e98g-f8hy and the 3h2n TEST record), 6 positive BIN-join probes on one real building, 2 valid no-match probes, the BIN-in-BBL pollution pair, the 3h2n↔855j duplication pair, the HTTP 400 drift signature, and 4 aggregate probes evidencing pollution scale, device-type coverage, and garbage/mixed date values. At connector build add: pagination pair (`$order=:id`), HTTP 429 capture (cannot be forced politely), per-field date-parser cases (YYYYMMDD, MM/DD/YYYY, mixed-column, YYYYMMDDHHMMSS), TEST-record quarantine case, future-date rejection case, eabe snapshot-diff case, and provenance/retrieval-timestamp assertions per the connector scenario pack standard.

## 10. OPEN QUESTIONS ledger

| OQ | Question | Why unanswered | Action |
| --- | --- | --- | --- |
| OQ-1 | Content of the 12 data-dictionary XLSX attachments (value domains, null semantics beyond observation — esp. 3h2n `violation_type_code`, eabe `complaint_category`, 6bgk infraction codes) | Binary attachments; octet-stream API; low-storage policy defers parsing | Extract on Codespaces/Render at connector build (assetIds captured) |
| OQ-2 | Precise era boundary between 3h2n-5cm9 and 855j-jady (issuance date does NOT partition them; "payable in DOB NOW" is the stated rule) | Not derivable from metadata; dictionary may specify | OQ-1 extraction + dedup-key experiment at connector build |
| OQ-3 | Complaint category code list (`bis_complaint_disposition_codes.pdf` on `www1.nyc.gov` is 403-walled; the Socrata PDF attachment serves octet-stream) | nyc.gov bot wall (memory-documented channel behavior) | Browser-capable capture session, or cloud-side attachment extraction with OQ-1 |
| OQ-4 | Why g76y-dcqj froze in 2023 and where post-2023 AHV data lives (DOB NOW portal shows AHVs interactively; no dataset found) | No successor in catalog (28-result probe recorded); nyc.gov 403 | Browser capture of DOB announcements; monitor catalog; possible DOB open-data request |
| OQ-5 | Whether iz2q-9x8d/nyis-y4yr rows are subsets of ic3t-wcy2 (affects nothing now; both rejected) | Not probed (out of scope after rejection) | Only if signage/antenna ever enters product scope |
| OQ-6 | 6bgk-3dad full issue_date range (text YYYYMMDD with garbage min `"0"`) | Garbage values corrupt min/max; LIKE-decade sweep not run (request budget) | Year-bucket LIKE sweep at connector build |
| OQ-7 | Socrata app token for production (reconfirmed needed) | Owner account action | Already tracked (HUMAN_ACTIONS §7, M1-T001) |

## 11. Source register (every channel fetched live by the producer, 2026-07-17 16:15–16:21 UTC)

| # | URL | Result | Used for |
| --- | --- | --- | --- |
| D1 | `data.cityofnewyork.us/api/catalog/v1?q=DOB&limit=100&search_context=…` | 200, 82 results | discovery |
| D2 | `api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&…&q=DOB&limit=100` | 200, identical 82 | discovery corroboration |
| D3 | `data.cityofnewyork.us/api/views/<4x4>.json` ×17 (12 in-scope + 5 candidates) | 200 each | identity, columns, cadence, attachments, descriptions |
| D4 | `data.cityofnewyork.us/resource/<4x4>.json?$limit=2` ×12 | 200 each | verbatim samples, null-omission |
| D5 | `resource/<4x4>.json?$select=count(*)` ×12 | 200 each | scale (incl. e98g-f8hy = 0) |
| D6 | min/max aggregates ×8 (see fixtures README + §3) | 200 each | date coverage + garbage-date evidence |
| D7 | LIKE year probes ×6 (ipu4 1989/2026; ic3t 2000/2026; eabe 1989/2026) | 200 each | coverage endpoints for text-date datasets |
| D8 | BIN 1006014 join probes ×8 | 200 each (6 positive, 2 `[]`) | cross-channel continuity, pollution, duplication |
| D9 | `ipu4-2q9a.json?$select=not_a_real_column` | **400** `query.soql.no-such-column` | drift signature |
| D10 | quality quantifiers: ipu4 null-bbl; ic3t length(bbl) groups; 855j device_type groups + null count; eabe distinct dobrundate; 6v9u code=I2 | 200 each | §1/§3 findings |
| D11 | `data.cityofnewyork.us/api/catalog/v1?q=after%20hour%20variance&limit=10` | 200, 28 results, no successor | g76y staleness disposition |
| D12 | `dev.socrata.com/docs/queries/limit.html`, `docs/app-tokens` | cited from accepted M1-T007 §5 / M1-T001 E7 evidence (not re-fetched) | pagination/auth |
