# M1-T007 fixtures — DOB NOW Open Data family

All fixtures retrieved live by the producer (official-source-researcher) on **2026-07-17, 07:45–08:05 UTC**, tokenless, from `data.cityofnewyork.us` (Socrata/NYC Open Data). Requests were throttled (2 s sleeps, `$limit` ≤ 2 on record fetches). The server clock cross-reference: the attachment-probe response header carried `Date: Fri, 17 Jul 2026 07:56:52 GMT`.

Two fixture classes — do not confuse them:

- **VERBATIM** — byte-for-byte curl output, unedited.
- **EXTRACT** — field subset of a larger verbatim response, produced by the recorded Python snippet; every retained *value* is verbatim, but the file is NOT the full server response (full `api/views` responses are 8–210 KB each and are re-fetchable live at G1).

## Verbatim SODA record fixtures

| File | Command (all prefixed `curl -s`) |
| --- | --- |
| `sample_<4x4>.json` (11 files) | `"https://data.cityofnewyork.us/resource/<4x4>.json?$limit=2"` |
| `query_w9ak-ipjd_bbl-eq_1004410016.json` | `"https://data.cityofnewyork.us/resource/w9ak-ipjd.json?bbl=1004410016&$limit=2&$select=job_filing_number,filing_status,house_no,street_name,borough,block,lot,bin,bbl,job_type,filing_date"` |
| `query_rbx6-tga4_bbl-numeric-where_1004410016.json` | `"https://data.cityofnewyork.us/resource/rbx6-tga4.json?$where=bbl=1004410016&$limit=2&$select=job_filing_number,work_permit,bin,bbl,borough,block,lot,house_no,street_name,issued_date"` |
| `query_rbx6-tga4_select-bbl-serialization.json` | `"https://data.cityofnewyork.us/resource/rbx6-tga4.json?$select=bbl,bin,block,lot&$limit=2"` |
| `query_pkdm-hqz6_bin_1006014_nomatch.json` | `"https://data.cityofnewyork.us/resource/pkdm-hqz6.json?bin=1006014&$limit=2"` → `[]` |
| `query_pkdm-hqz6_bin_1001905_positive.json` | `"https://data.cityofnewyork.us/resource/pkdm-hqz6.json?bin=1001905&$limit=1"` |
| `query_xubg-57si_bin_1006014_nomatch.json` | `"https://data.cityofnewyork.us/resource/xubg-57si.json?bin=1006014&$limit=2&$select=bin,house_no,street_name,borough,block,lot,cycle,filing_type,current_status,filing_date"` → `[]` |
| `query_xubg-57si_bin_1014176_positive.json` | `"https://data.cityofnewyork.us/resource/xubg-57si.json?bin=1014176&$limit=1&$select=bin,house_no,street_name,borough,block,lot,cycle,filing_type,current_status,filing_date"` |
| `query_52dp-yji6_bin-number_1006014_positive.json` | `"https://data.cityofnewyork.us/resource/52dp-yji6.json?$where=bin_number=1006014&$limit=2"` |
| `query_e5aq-a4j2_bad-column_http400.json` | `"https://data.cityofnewyork.us/resource/e5aq-a4j2.json?bin=1006014&$limit=2&$select=...,filing_date"` — deliberate retention: `filing_date` does not exist on e5aq-a4j2 → HTTP 400 `query.soql.no-such-column` (schema-drift failure signature; the error body enumerates the real columns) |
| `query_e5aq-a4j2_bin_1006014_nomatch.json` | `"https://data.cityofnewyork.us/resource/e5aq-a4j2.json?bin=1006014&$limit=2&$select=bin,borough,house_number,street_name,block,lot,bbl,device_number,device_status,periodic_latest_inspection"` → `[]` |
| `query_e5aq-a4j2_bin_1001627_positive.json` | `"https://data.cityofnewyork.us/resource/e5aq-a4j2.json?bin=1001627&$limit=1"` |

BIN `1006014` (418 East 14 Street, Manhattan, block 441 lot 16, BBL 1004410016) was taken from the observed `sample_w9ak-ipjd.json` record — not guessed — and cross-probed across the family (positive in rbx6-tga4 and 52dp-yji6; empty in pkdm-hqz6, xubg-57si, e5aq-a4j2). Positive-control BINs for the empty datasets came from each dataset's own `$limit=2` sample (1001905, 1014176, 1001627).

## Extract fixtures (field subsets; retained values verbatim)

- `catalog_dob-now_results_extract.json` — from TWO catalog queries returning identical 21-dataset result sets:
  - `curl -s "https://api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&search_context=data.cityofnewyork.us&q=DOB%20NOW&limit=30"` (271,217 bytes)
  - `curl -s "https://data.cityofnewyork.us/api/catalog/v1?q=DOB%20NOW&limit=30"` (271,219 bytes)
  - Kept per result: `resource.id`, `resource.name`, `resource.type`, `resource.attribution`, `resource.provenance`.
- `views_metadata_extract_16_datasets.json` — from 16 × `curl -s "https://data.cityofnewyork.us/api/views/<4x4>.json"` (HTTP 200 each; sizes 8,307–210,284 bytes). Kept: id, name, attribution, assetType, category, newBackend, provenance, createdAt/rowsUpdatedAt (raw epoch **and** UTC conversion by `datetime.fromtimestamp(v, timezone.utc)`), publicationDate, viewLastModified, `metadata.custom_fields` (Update Frequency / Automation), attachments (filename + assetId), full description, and the full `columns` array reduced to `fieldName`/`name`/`dataTypeName` per column. Column inventories come from this channel, NEVER from record keys (SODA omits nulls per record).
- `row_counts_core6.json` — from 6 × `curl -s "https://data.cityofnewyork.us/resource/<4x4>.json?$select=count(*)%20as%20n"`.

## Other probes recorded (not saved as files here; outputs quoted in the findings doc)

- Data-dictionary attachment probe: `curl -s -I "https://data.cityofnewyork.us/api/views/w9ak-ipjd/files/978bdfe8-11c3-4839-9515-7f36a83e219d?download=true&filename=DOB_NOW_Build_Job_Application_Filings_Data_Dictionary.xlsx"` → HTTP 200, `Content-Type: application/octet-stream`, `Content-Length: 74405`, `ETag: "978bdfe8-..."`.
- nyc.gov bot wall: `curl -s -o /dev/null -w "%{http_code}" "https://www.nyc.gov/site/buildings/industry/dob-now.page"` → **HTTP 403** (recorded attempt, per policy).
- data.gov mirror: `curl -s -L "https://catalog.data.gov/dataset/dob-now-build-job-application-filings"` → HTTP 200 (113,507 bytes); raw-HTML grep confirmed the literal string `w9ak-ipjd` (2 hits) and title `City of New York - DOB NOW: Build – Job Application Filings`. `catalog.data.gov/api/3/action/package_search` returned HTTP 404 (CKAN action API not available at that path on 2026-07-17).
- SODA paging authority: `curl -s "https://dev.socrata.com/docs/queries/limit.html"` → HTTP 200; verbatim: "The LIMIT parameter controls the total number of rows returned, and it defaults to 1,000 records per request" and "Version 2.0 endpoints have a maximum $limit of 50,000; Version 2.1 and 3.0 endpoints have no maximum". (`/docs/paging` and `/docs/paging.html` are HTTP 404 → site restructure recorded.)
