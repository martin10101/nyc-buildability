# DOF sales — Bayside, Queens — recorded official data (B-11, comparable sales)

Queue item **B-11** (Lane B; plan `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` section 11b
"Comparable sales"; directive D-090). Dataset: DOF **NYC Citywide Annualized Calendar Sales
Update** (NYC Open Data `w2pb-icbu`, publisher Department of Finance). Research note with the
official metadata URL, sha256 and the verbatim field descriptions relied on:
`docs/research/dof-sales-comparables-2026-10-02.md`.

Subject: **215-16 Northern Boulevard**, Bayside, Queens, BBL **4073340070** (the B-01
benchmark lot).

- **Capture:** 3 responses on **2026-10-02 UTC**. `curl` GET, keyless, one request per file.
  Each body is stored byte-for-byte as returned.
- **Provenance:** `MANIFEST.json` lists, for each file, the dataset id, source id, the exact
  URL, `retrieved_at` (from the HTTP `Date` header), the HTTP `Last-Modified`, the dataset
  data vintage (`X-SODA2-Truth-Last-Modified`), the HTTP status, byte count and sha256.
- **Query shapes:** the two resource-query URLs are the exact strings
  `app.connectors.dof_sales_soda` builds (`build_by_bbl_url` / `build_candidates_url`); the
  metadata URL is the publisher's `api/views` endpoint.
- **Integrity:** `services/api/tests/connectors/test_dof_sales_fixtures.py` re-hashes every
  file and rebuilds the two connector URLs. `.gitattributes` (`-text`) keeps the bytes exact.

## What is here

| File | Rows | Finding |
|---|---|---|
| `dof_sales_api_views_w2pb-icbu.json` | — | Dataset metadata: 29 columns, their types and the publisher's verbatim descriptions (the only source of field meaning). |
| `dof_sales_w2pb-icbu_bbl_4073340070.json` | 1 | The subject's own recorded sale: a **$0 transfer** (2018-01-18) of the pre-redevelopment store building (K1, "22 STORE BUILDINGS", gross 5,091 sq ft). Stale vs the current PLUTO use (D6, 38 units) — recorded faithfully, not interpreted. |
| `dof_sales_w2pb-icbu_bayside_22_store_buildings.json` | 12 | Candidate "similar type" rows (same DOF neighborhood BAYSIDE + `building_class_category` "22 STORE BUILDINGS"). Real edge cases: a **null `bbl`** row, several **$0 transfers**, and rows with **`gross_square_feet` = 0** (size not recorded). |

## Boundaries (recorded, never crossed here)

- **Not a valuation.** The rows carry the publisher's recorded `sale_price` and `sale_date`;
  this pack and its tests compute no average, no price-per-square-foot and no estimate.
- **A $0 sale price** is, per the official `sale_date` field description, "a transfer of
  ownership without a cash consideration" — a non-arms-length transfer, not a market sale.
- **"Similar type and size"** is a product choice. The disclosed default filter
  (`app.profile.parity.comparable_sales`) is surfaced verbatim; confirming it is an open
  owner question (`docs/lanes/status/B.md`), never decided here.
