# DOB legacy / non-DOB-NOW source fixtures (M1-T008, research evidence)

Captured live, tokenless, from `https://data.cityofnewyork.us` (catalog sweeps via
`https://api.us.socrata.com`) by the M1-T008 producer (official-source-researcher) on
**2026-07-17**, in two same-day sessions:

- **Bulk capture, ~10:55–11:05 UTC** — authoritative timestamps are embedded in the committed
  artifacts themselves: `catalog_dob_sweep_extract.json` `_retrieved_utc` 10:55Z; `views_metadata_extract_17_datasets.json`
  10:56Z; `query_log_counts_and_ranges.txt` 11:01:25–11:01:58 UTC; `query_log_key_probes.txt`
  11:02:53–11:03:03 UTC; `query_log_cross_channel_bin1006014.txt` 11:03:54 UTC;
  `response_headers_3h2n-5cm9_count.txt` server `Date:` 11:04:48 GMT.
- **Re-verification, ~16:15–16:21 UTC** — several `sample_*.json`/`query_*.json` response bodies
  were re-captured in this session. The plain JSON bodies embed no timestamps, so their capture
  time is a producer statement, not verifiable from the committed bytes.

An earlier revision of this README claimed a single "16:15–16:21 UTC" capture window and
"26 files, ~77 KB"; both claims were wrong and are corrected here.

**Provenance classes** (per-file below):

- **verbatim** — an unedited HTTP response body exactly as returned by the API
  (all `sample_*.json` and `query_*.json` files).
- **producer-assembled extract** — JSON assembled by the producer from verbatim responses:
  content values are copied from the responses, but the file adds `_retrieved_utc` /
  `_source_url_pattern` keys and projects/filters fields (the two `*_extract.json` files).
- **producer-assembled log** — annotated probe transcript: per probe, the exact URL, HTTP status,
  and verbatim response body, wrapped in producer annotations and `date -u` stamps
  (the three `query_log_*.txt` files); plus one raw response-header capture (`response_headers_*.txt`).

Full analysis: `docs/research/dob-legacy-sources.md`. Directory contents: **44 files =
43 fixture files (146,865 bytes, ~143 KB — byte-for-byte unchanged by the documentation rework)
+ this README**. The directory total varies with the README itself: the G1 review measured
152,100 bytes including the pre-rework 5,235-byte README; state fixtures-only vs directory-total
explicitly when citing sizes. All KB-scale per the low-storage policy.

## Samples — verbatim (`sample_<4x4>.json` — `resource/<4x4>.json?$limit=2`)

### In-scope datasets

| File | Dataset | Why kept |
| --- | --- | --- |
| sample_ipu4-2q9a.json | DOB Permit Issuance | mangled field names (`bin__`, `job__`), MM/DD/YYYY text dates, zero-padded 5-digit block/lot, null-omitted `bbl` |
| sample_ic3t-wcy2.json | DOB Job Application Filings | zoning-relevant numerics, `$`-prefixed cost strings, MM/DD/YYYY text dates |
| sample_bs8b-p36w.json | DOB Certificate Of Occupancy | duplicate `bin_number`/`bin` columns, `location` complex type, `:@computed_region_*` columns |
| sample_bty7-2jhb.json | Historical DOB Permit Issuance | ISO-format dates inside `text` columns; unpadded block/lot (differs from ipu4-2q9a) |
| sample_g76y-dcqj.json | DOB After Hour Variance Permits | `checkbox` type → JSON booleans; DOB NOW-format `workpermitnumber` |
| sample_855j-jady.json | DOB Safety Violations | composite `violation_number`, number-typed block/lot/bbl, future `cycle_end_date` |
| sample_3h2n-5cm9.json | DOB Violations | **literal TEST RECORD** (`house_number:"TEST"`, `street:"RECORD"`, block/lot `99999`), YYYYMMDD text dates, padded value blobs |
| sample_6bgk-3dad.json | DOB ECB Violations | boro as digit, 4-digit lot padding, YYYYMMDD text dates, `penality_imposed` [sic] |
| sample_eabe-havv.json | DOB Complaints Received | MM/DD/YYYY `date_entered` + `YYYYMMDDHHMMSS` `dobrundate` in one record |
| sample_6v9u-ndjg.json | Building Complaint Disposition Codes | 2-column lookup table |
| sample_bf97-mjsy.json | Construction-Related Incidents (DOB Incident Database; **not** a BIS dataset) | per-incident `fatality`/`injury` counts, `address_bbl` 10-digit text, title-case `boro` |
| sample_e98g-f8hy_empty.json | Property Data (BIS) — Now Retired | dataset is now EMPTY: `[]` (row count 0 confirmed in `query_log_counts_and_ranges.txt`) |
| sample_e98g-f8hy.json | Property Data (BIS) — Now Retired | **byte-identical duplicate of `sample_e98g-f8hy_empty.json`** (both are the 3-byte body `[]`): an earlier-named capture of the same request, retained as-is per the rework directive; treat `sample_e98g-f8hy_empty.json` as canonical |

### Stage C / candidate datasets (examined in §7/§8 of the research doc)

| File | Dataset | Why kept |
| --- | --- | --- |
| sample_i296-73x5.json | DOB Stalled Construction Sites | Stage C secondary source: BIN-keyed, complaint-linked, `dobrundate` snapshot column |
| sample_iz2q-9x8d.json | DOB Cellular Antenna Filings | REJECTED candidate: BIS filing shape; frozen 2024-01-02 despite stated "Daily" |
| sample_nyis-y4yr.json | DOB Sign Application Filings | REJECTED candidate: BIS filing shape incl. sign geometry; frozen 2024-01-03 |
| sample_ndq3-kuef.json | DOB Disciplinary Actions | REJECTED candidate: 7 columns, no BIN/BBL/address — cannot attach to a property |
| sample_t8hj-ruu2.json | DOB License Info | REJECTED candidate: licensee-keyed, not property-keyed |

## Targeted queries — verbatim (`query_*.json`)

Exact URLs recorded at capture unless noted (prefix `https://data.cityofnewyork.us/resource/`).
`$` characters in URLs were shell-escaped at capture; spaces encoded as `%20`.

| File | URL / provenance note | Evidence |
| --- | --- | --- |
| query_ipu4-2q9a_bin1006014_positive.json | `ipu4-2q9a.json?bin__=1006014&$select=job__,job_type,permit_type,permit_status,issuance_date,block,lot,bbl,borough&$limit=3` | BIS permit exists for the M1-T007 anchor building |
| query_ic3t-wcy2_bin1006014_bbl-pollution.json | `ic3t-wcy2.json?bin__=1006014&$select=job__,job_type,job_status_descrp,latest_action_date,block,lot,bbl,borough,zoning_dist1&$limit=3` | **7-digit BIN value stored in `bbl` column** on one row of the same job |
| query_bs8b-p36w_bin1006014_nomatch.json | `bs8b-p36w.json?bin=1006014&$select=job_number,c_o_issue_date,issue_type,bin,bbl&$limit=3` | HTTP 200 `[]` valid no-match |
| query_3h2n-5cm9_bin1006014_positive.json | `3h2n-5cm9.json?bin=1006014&$select=violation_number,issue_date,violation_type_code,violation_category,block,lot,boro&$limit=3` | BIS violations 1994→2018 incl. LBLVIO `00614` @ `20180406` |
| query_6bgk-3dad_bin1006014_positive.json | `6bgk-3dad.json?bin=1006014&$select=ecb_violation_number,issue_date,violation_type,ecb_violation_status,dob_violation_number,block,lot,boro&$limit=3` | ECB summonses for same building; 4-digit lot `0016` |
| query_eabe-havv_bin1006014_positive.json | `eabe-havv.json?bin=1006014&$select=complaint_number,status,date_entered,complaint_category,disposition_code&$limit=3` | complaints 1999→2019 same building |
| query_855j-jady_bin1006014_dup-of-3h2n.json | `855j-jady.json?bin=1006014&$select=violation_number,violation_issue_date,violation_type,violation_status,bbl&$limit=3` | **same violation duplicated across 3h2n-5cm9 and 855j-jady** (`040618LBLVIO00614` = `20180406`+`LBLVIO`+`00614`) |
| query_bf97-mjsy_bin1006014_nomatch.json | `bf97-mjsy.json?bin=1006014&$limit=3` | HTTP 200 `[]` valid no-match |
| query_ipu4-2q9a_bad-column_http400.json | `ipu4-2q9a.json?$select=not_a_real_column&$limit=1` | HTTP 400 `query.soql.no-such-column` schema-drift signature |
| query_ic3t-wcy2_bbl-length-distribution.json | `ic3t-wcy2.json?$select=length(bbl) as len,count(*) as n&$group=len&$order=n DESC&$limit=8` | pollution scale: 1,802,216 len-10; **884,315 len-7**; 29,120 null |
| query_855j-jady_device-type-groups.json | `855j-jady.json?$select=device_type,count(*) as n&$group=device_type&$order=n DESC&$limit=12` | covers Boiler/Elevators/AEUHAZ/LL152/LL84/Facades/LL33/LL87/… |
| query_bs8b-p36w_minmax_co-issue-date_future-garbage.json | `bs8b-p36w.json?$select=min(c_o_issue_date) as lo,max(c_o_issue_date) as hi` | max = **2105-11-05** (future-dated garbage in official calendar_date) |
| query_3h2n-5cm9_minmax_issue-date_garbage.json | `3h2n-5cm9.json?$select=min(issue_date) as lo,max(issue_date) as hi` | min `000000`, max `Y9990120` — non-date garbage in text date column |
| query_ipu4-2q9a_minmax_issuance-date_mixed-formats.json | `ipu4-2q9a.json?$select=min(issuance_date) as lo,max(issuance_date) as hi` | min `01/01/2007` (MM/DD/YYYY) vs max `2020-06-05` (ISO) — **two formats in one column** |
| query_3h2n-5cm9_with_ecb_number.json | provenance note: 3h2n-5cm9 row filtered on ECB cross-reference `ecb_number=34254160K` (exact URL not logged at capture; bulk-capture session) | 3h2n side of the ECB join pair; carries `issue_date "19390711"` — a **mis-keyed year** (see pair below) |
| query_6bgk-3dad_ecb_34254160K_join.json | provenance note: `6bgk-3dad.json?ecb_violation_number=34254160K`-shaped query (exact URL not logged at capture; bulk-capture session) | 6bgk side of the ECB join pair: same violation with `issue_date "20000711"` — proves 3h2n's `19390711` is a year mis-key (MMDDYY `071139`/`071100` confusion) and proves the `ecb_number`↔`ecb_violation_number` cross-reference |
| query_ic3t-wcy2_bin_1006014_select.json | provenance note: `ic3t-wcy2.json?bin__=1006014&$select=job__,doc__,job_type,job_status_descrp,latest_action_date,pre__filing_date,borough,block,lot,bin__,bbl` (exact URL reconstructed from the response fields; earlier `$select` variant, superseded by `query_ic3t-wcy2_bin1006014_bbl-pollution.json` but retained — it shows the same BBL-pollution pair) | earlier capture of the two-row pollution proof |
| query_ipu4-2q9a_bin_1006014_select.json | provenance note: `ipu4-2q9a.json?bin__=1006014&$select=job__,job_doc___,work_type,permit_type,permit_status,filing_date,issuance_date,borough,block,lot,bin__,bbl` (exact URL reconstructed from the response fields; earlier `$select` variant of the positive BIN probe) | earlier capture of the anchor-building permit |
| query_ic3t-wcy2_bin_0000000_nomatch.json | provenance note: `ic3t-wcy2.json?bin__=0000000`-shaped probe (exact URL not logged at capture) | HTTP 200 `[]` — a syntactically valid but nonexistent BIN returns a valid empty result, not an error |

## Producer-assembled extracts (`*_extract.json` — NOT verbatim bodies)

| File | Source + structure | Evidence |
| --- | --- | --- |
| catalog_dob_sweep_extract.json | `_retrieved_utc` 2026-07-17T10:55Z. Assembled from two catalog queries against `api.us.socrata.com/api/catalog/v1` (exact URLs embedded in the file): `q=DOB&only=dataset&limit=150` → resultSetSize **71** (43 DOB-attributed results extracted) and `q="Department of Buildings"&only=dataset&limit=150` → resultSetSize **342** (34 DOB-attributed extracted). Values copied verbatim from the responses; the file itself is a producer projection (id/name/attribution/updatedAt per result) with added `_retrieved_utc` | discovery evidence for §2.1 of the research doc |
| views_metadata_extract_17_datasets.json | `_retrieved_utc` 2026-07-17T10:56Z; `_source_url_pattern` `https://data.cityofnewyork.us/api/views/<id>.json`. Assembled from 17 `api/views` responses (12 in-scope + 5 candidates); per dataset a projection of identity/cadence/description/columns metadata, with producer-added `*_iso` conveniences (e.g. `rowsUpdatedAt` epoch → ISO). Records eabe-havv `rowsUpdatedAt` = **2026-07-16T16:49:33Z** (epoch 1784220573) — the authoritative committed value; the 2026-07-17T16:15:31Z refresh cited in earlier doc revisions came from the uncommitted re-verification session | identity/cadence/freshness evidence for §2.2/§8 |

## Producer-assembled logs (`*.txt` — annotated probe transcripts, NOT single verbatim bodies)

Each `query_log_*.txt` entry records the exact URL, HTTP status, and verbatim response body,
bracketed by `date -u` stamps (first/last line of the file).

| File | Window (UTC, embedded) | Evidence |
| --- | --- | --- |
| query_log_counts_and_ranges.txt | 11:01:25–11:01:58 | `count(*)` for all 17 datasets (incl. e98g-f8hy **0**); raw min/max ranges (bs8b future `2105-11-05`; 855j `1989-10-12→2026-07-15`; g76y ending `2024-01-12`; bf97 `2024-01-03→2026-07-14`; bty7 `1989-05-11→2013-04-24`; 3h2n/6bgk garbage min); successful `cast_ipu4` probe `min/max(issuance_date::floating_timestamp)` → **1989-05-11 → 2026-07-15** |
| query_log_key_probes.txt | 11:02:53–11:03:03 | ic3t BIN-in-BBL sample; ipu4 `bbl IS NOT NULL` count 3,869,747; bs8b post-2021 count 12,795 + future-CO count 1; range-filtered probes **3h2n 19011215→20260715 (31 garbage rows outside 1900–2026)** and **6bgk 19101004→20260714 (64 garbage rows)**; successful `eabe_cast_range` → **1988-12-30 → 2026-07-16**; **HTTP 500 `internal-error`** (tag `c4361147-3ff1-4403-b992-78910fb4c383`) on `ic3t_cast_range` — server-side cast aggregation can fail on the 95-column dataset; i296 latest-snapshot count 148 |
| query_log_cross_channel_bin1006014.txt | 11:03:54 | per-dataset BIN 1006014 totals: ic3t 2, ipu4 1, eabe **17**, 3h2n 3, 6bgk **6**, 855j 1, bs8b 0, g76y 0; ic3t LIKE probes `%/1999`→0, `%/2026`→8,941 |
| response_headers_3h2n-5cm9_count.txt | server `Date:` 11:04:48 GMT | verbatim response headers of a `3h2n-5cm9.json?$select=count(*)` request: `X-SODA2-Fields`/`X-SODA2-Types` contract headers, `Last-Modified: Thu, 16 Jul 2026 17:40:22 GMT` (matches the views-extract `rowsUpdatedAt` for 3h2n), fedramp region header — the bulk-session server-time anchor |
