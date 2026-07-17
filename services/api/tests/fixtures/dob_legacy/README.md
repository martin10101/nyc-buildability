# DOB legacy / non-DOB-NOW source fixtures (M1-T008, research evidence)

Captured live, tokenless, from `https://data.cityofnewyork.us` on **2026-07-17, 16:15–16:21 UTC**
by the M1-T008 producer (official-source-researcher). Every file is a VERBATIM HTTP response body
(no editing). Full analysis: `docs/research/dob-legacy-sources.md`. All files are KB-scale
(directory total ~77 KB) per the low-storage policy.

## Samples (`sample_<4x4>.json` — `resource/<4x4>.json?$limit=2`)

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
| sample_e98g-f8hy_empty.json | Property Data (BIS) — Now Retired | dataset is now EMPTY: `[]` (row count 0 confirmed separately) |

## Targeted queries (`query_*.json` — exact URLs)

| File | URL (prefix `https://data.cityofnewyork.us/resource/`) | Evidence |
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

`$` characters in URLs were shell-escaped at capture; spaces encoded as `%20`.
