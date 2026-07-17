<!-- VERBATIM producer return (official-source-researcher, 2026-07-17), preserved by the orchestrator per the report-preservation rule. Transport entity-decoding only (&amp; decoded to & in the two $limit/$order query strings); no other alteration. Supersedes the v1 disposition in M1-T007-C1v2 sequence: owner re-opened C1 as C1v2 requiring an evidence-backed disposition (description, fields, keys, coverage, product relationship), not a catalog-completion exclusion. The producer authored the edit; the orchestrator applied it mechanically (harness worktree isolation) on branch task/M1-T007-dob-now-research. -->

C1v2 disposition for `bf97-mjsy` complete. All research was live, tokenless, on data.cityofnewyork.us, retrieved 2026-07-17.

## a. Exact file path

`C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T007\docs\research\M1-T007-dob-now-sources.md`

## b. Exact unique old_string (verbatim, occurs once, end of the §2.1 sentence on line 44)

```
bf97-mjsy Construction-Related Incidents is likewise DOB-attributed but fed by the DOB Incident Database, not a DOB NOW module — description verbatim: "This dataset includes construction-related incidents recorded in through the Department of Buildings (DOB) Incident Database." [sic], identity live-verified via https://data.cityofnewyork.us/api/views/bf97-mjsy.json HTTP 200 retrieved 2026-07-17 — out of scope here, flagged for the BIS/legacy task; two HPD datasets are noise).
```

## c. Exact new_string

```
bf97-mjsy Construction-Related Incidents is DOB-attributed but not a DOB NOW-module output — evidence-backed disposition in the dedicated paragraph below; two HPD datasets are noise).

**bf97-mjsy — Construction-Related Incidents: evidence-backed disposition (C1v2).** All claims below live-verified 2026-07-17, tokenless, via `https://data.cityofnewyork.us/api/views/bf97-mjsy.json` (metadata) and `https://data.cityofnewyork.us/resource/bf97-mjsy.json` (SODA), all HTTP 200.

- **What it is:** official name "Construction-Related Incidents", attribution "Department of Buildings (DOB)", `provenance: official`, `newBackend: true`; description verbatim: "This dataset includes construction-related incidents recorded in through the Department of Buildings (DOB) Incident Database." [sic]. Created 2024-10-16 (createdAt 1729098863), custom fields: Date Made Public "11/21/2024", Update Frequency "Daily", Automation "Yes", "The underlying data changes second-to-second in the system of record."; `rowsUpdatedAt` 2026-07-16T18:46:16Z (epoch 1784227576) — same-day freshness as the DOB NOW family. Official data dictionary attached ("Construction-Related Incidents_Data Dictionary.xlsx", assetId b40d4ef0-d572-4a05-9195-2c01617af0c2; XLSX not content-extracted, same OQ-2 constraint as §2.3).
- **Keys (20-column array + `$limit=2&$order=incident_date_mm_dd_yyyy DESC` sample, observed verbatim):** `bin` text, 7-digit borough-leading ("3000370", "4000542"); `address_bbl` text, 10-digit zero-padded ("3001497503", "4000717501"); `boro` title case ("Brooklyn", "Queens"); `block`/`lot` text, NOT zero-padded ("149"/"7503", "71"/"7501" — condo billing lots in the 75xx range, same semantics as §3.2); address `addressnumber` + `street`; plus `address_zipcode`, `address_latitude`/`address_longitude` (text), community district, council district, `address_censustract2020`, `address_nta2020`. Key formats match the family conventions in §3.2, so it joins cleanly to a BIN/BBL-keyed profile via the §3.4 BIN-primary/BBL-corroboration strategy.
- **Fact fields:** `accident_report_id` (number), `incident_date_mm_dd_yyyy` (calendar_date, ISO serialization "2026-07-14T00:00:00.000"), `record_type_description` (text; "Incident" observed), `check2_description` (incident category text; "Other Construction Related" observed), `fatality` (number), `injury` (number).
- **Size and coverage:** `$select=count(*)` → 1,326 rows; `$select=min/max(incident_date_mm_dd_yyyy)` → 2024-01-03T00:00:00.000 to 2026-07-14T00:00:00.000 (retrieved 2026-07-17) — a short window opening ~January 2024, consistent with the 2024-11-21 publication date.
- **Why not in the DOB NOW connector family:** its stated system of record is the "DOB Incident Database" (description verbatim above), not a DOB NOW: Build / Safety / Electrical module, and it carries no `job_filing_number` / `work_permit` keys, so it cannot participate in the family's filing→permit→device join graph (§3.3).
- **Value to the property-history product:** material, not noise — per-BIN construction-incident history with injury/fatality counts and incident dates is a direct site-history/risk signal for a development-feasibility profile, and the observed BIN/BBL formats make the join trivial.
- **Classification: documented secondary/future source** — assigned to M1-T008 (DOB-wide/BIS-legacy official-source research) for full G1 research treatment, feeding a subsequent M2 property-history/risk fact-connector stage; reason: it is valuable and joinable, but its system of record sits outside this task's DOB NOW-module scope, and its small size (1,326 rows) and short coverage window (incidents from 2024-01-03 only) make it a supplementary risk-signal feed rather than a first-stage core profile fact source.
```

## d. Live evidence gathered (all retrieved 2026-07-17)

**1. `https://data.cityofnewyork.us/api/views/bf97-mjsy.json` — HTTP 200 (Python urllib, UA-spoofed, tokenless):**
- `name`: "Construction-Related Incidents"; `attribution`: "Department of Buildings (DOB)"; `id`: bf97-mjsy; `assetType`: dataset; `newBackend`: True; `provenance`: official
- `createdAt`: 1729098863 = 2024-10-16T17:14:23Z; `rowsUpdatedAt`: 1784227576 = 2026-07-16T18:46:16Z
- `description` verbatim: `'This dataset includes construction-related incidents recorded in through the Department of Buildings (DOB) Incident Database.'` (the "recorded in through" typo is in the source)
- Custom fields: Automation "Yes"; Update Frequency Details "The underlying data changes second-to-second in the system of record."; Date Made Public "11/21/2024"; Update Frequency "Daily"; Data Change Frequency "Daily"; Agency "Department of Buildings (DOB)"
- Attachment: "Construction-Related Incidents_Data Dictionary.xlsx", assetId b40d4ef0-d572-4a05-9195-2c01617af0c2
- Full 20-column array (fieldName | display name | type): `bin`|BIN|text; `accident_report_id`|Accident Report ID|number; `incident_date_mm_dd_yyyy`|Incident Date|calendar_date; `record_type_description`|Record Type Description|text; `check2_description`|Check2 Description|text; `fatality`|Fatality|number; `injury`|Injury|number; `addressnumber`|House Number|text; `street`|Street Name|text; `boro`|Borough|text; `block`|Block|text; `lot`|Lot|text; `address_zipcode`|Postcode|text; `address_latitude`|Latitude|text; `address_longitude`|Longitude|text; `address_communitydistrict`|Community Board|text; `address_citycouncildistrict`|Council District|text; `address_bbl`|BBL|text; `address_censustract2020`|Census Tract (2020)|text; `address_nta2020`|Neighborhood Tabulation Area (NTA) (2020)|text. BIN: yes. BBL: yes (`address_bbl`). Borough/block/lot: yes (`boro`/`block`/`lot`). Address: yes (`addressnumber`/`street`).

**2. `https://data.cityofnewyork.us/resource/bf97-mjsy.json?$select=count(*)` — HTTP 200:** `[{"count":"1326"}]`

**3. `...?$select=min(incident_date_mm_dd_yyyy) as min_d,max(incident_date_mm_dd_yyyy) as max_d` — HTTP 200:** `[{"min_d":"2024-01-03T00:00:00.000","max_d":"2026-07-14T00:00:00.000"}]` (field name taken from the columns array, not guessed)

**4. `...?$limit=2&$order=incident_date_mm_dd_yyyy DESC` — HTTP 200, 2 rows, key-relevant observed values:**
- Row 1: `bin` "3000370", `address_bbl` "3001497503", `boro` "Brooklyn", `block` "149", `lot` "7503" (condo billing lot), `addressnumber` "9", `street` "DEKALB AVENUE", `incident_date_mm_dd_yyyy` "2026-07-14T00:00:00.000", `record_type_description` "Incident", `check2_description` "Other Construction Related", `fatality` "0", `injury` "1"
- Row 2: `bin` "4000542", `address_bbl` "4000717501", `boro` "Queens", `block` "71", `lot` "7501", `addressnumber` "24-02" (Queens hyphenated house number), `street` "49 AVENUE", `fatality` "0", `injury` "0"
- Observed formats: BBL 10-digit zero-padded text (borocode+block5+lot4 — "3001497503" decomposes to boro 3 / block 00149 / lot 7503, matching the row's `block` "149"/`lot` "7503"); BIN 7-digit borough-leading; block/lot NOT zero-padded; borough title-case. All consistent with the family conventions already recorded in §3.2 of the findings doc.

**Assumptions/limitations:** the XLSX data dictionary was identified but not content-extracted (binary; same OQ-2 low-storage constraint as the rest of the doc). `record_type_description`/`check2_description` value domains were observed from only 2 rows plus the columns array; full domain enumeration belongs to the M1-T008/G1 treatment. No fixture file was written (harness isolation from the task worktree); the verbatim values above are the evidence of record.

## e. Catalog accounting

After the edit, all 21 catalog results remain accounted for: 11 DOB NOW family (§2.2) + 5 legacy/BIS rule-outs (§6) + 2 DOB non-DOB-NOW datasets flagged for the BIS/legacy task (g76y-dcqj, 855j-jady) + 1 bf97-mjsy (now a fully dispositioned documented secondary/future source assigned to M1-T008 → M2 property-history stage) + 2 HPD noise = 21.

**Requested status:** awaiting_gate (C1v2 disposition delivered as a returnable edit; no files outside my agent memory were touched, and no memory update was needed — existing SODA-channel memory already covers the stable learnings here).
