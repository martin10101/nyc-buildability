---
name: nyc-source-verification-techniques
description: Working verification channels and blockers for NYC official sources (nyc.gov 403, s-media OK, WebFetch-PDF-cache trick, Socrata/ArcGIS raw APIs)
metadata:
  type: reference
---

Verified during M1-T001 G1 (2026-07-16). Techniques that work from this sandbox for G1 source verification:

- **nyc.gov / apps.nyc.gov pages: HTTP 403** to curl (any UA) and WebFetch — bot protection serves a challenge shell. Page-level claims (bulk zip URLs, file sizes) need a browser-capable session. Do not guess URLs.
- **s-media.nyc.gov IS fetchable** (DCP PDFs: pluto_readme.pdf, pluto_datadictionary.pdf, meta_mappluto.pdf all live there).
- **WebFetch on a PDF fails to summarize but saves the binary** to `C:\Users\MLFLL\.claude\projects\...\tool-results\webfetch-*.pdf` — then use Read with `pages` to extract verbatim text. This is the reliable way to read official PDFs.
- **Socrata raw metadata:** `data.cityofnewyork.us/api/views/<id>.json` gives raw unix timestamps (convert yourself — WebFetch summarizer misconverted them once), full `columns` array (fieldName list), `metadata.accessPoints` (href targets), attachments. Catalog search: `api.us.socrata.com/api/catalog/v1?domains=data.cityofnewyork.us&q=...`.
- **ArcGIS verification chain:** `arcgis.com/sharing/rest/search?q=...&f=json` → item `?f=json` (owner/orgId) → `portals/<orgId>?f=json` (org name; NYC DCP = "NYC DCP Mapping Portal", orgId GfwWNkhOj9bNBqoJ, urlKey DCP) → FeatureServer `?f=json` + `/0/query` for a live record.
- **catalog.data.gov** dataset pages are fetchable and federate NYC metadata (but often just point back to nyc.gov landing pages). CKAN package_show slugs may 404; use the HTML page via WebFetch.
- **Bash /tmp paths don't map to native Windows Python** — pipe curl to `python -c` via stdin instead of writing temp files.
- SODA gotcha found: `$select`ed number columns (e.g. bbl) serialize as `"1000010100.00000000"` — normalization required in connectors.

Added during M1-T002 G1 (2026-07-16):
- **Socrata checkbox columns serialize as JSON booleans** (PLUTO splitzone/irrlotcode/mih_opt*/zmcode); SoQL predicate must be `col=true` — `col='Y'` returns 400 `query.soql.type-mismatch` (a NON-drift 400, distinct from `query.soql.no-such-column`).
- The bbl decimal-tail serialization (`"1000010100.00000000"`) appears on FULL records too, not just `$select` projections (also `appbbl`).
- source_fact v1 schema has no `additionalProperties` keyword → additive provenance keys are legal; validate emitted facts with Draft202012Validator + referencing Registry over source_fact+common.
- ArcGIS MAPPLUTO FeatureServer `/0/query?where=BBL=...&outFields=...` is a cheap second-official-presentation cross-check for individual PLUTO records (values matched SODA exactly for 1000010100).

Added during M1-T004 G1 (2026-07-16, ZR portal):
- **ZR portal Drupal AJAX endpoints:** markup `href="/nojs/get/amendment/section/{id}"` 404s to plain GET; the working form is `/ajax/get/amendment/section/{id}?_wrapper_format=drupal_ajax` with header `X-Requested-With: XMLHttpRequest` → 200 JSON command array whose `insert` payload is a per-section amendment-history table (Effective Date | ULURP/CPC Report | Project Name | Action | Notes | Description). Section-entity IDs are a third ID namespace (≠ node IDs).
- **council.nyc.gov and legistar.council.nyc.gov are automation-accessible** (200 to curl) — official adoption records reachable despite www.nyc.gov 403. Legistar detail pages give matter status ("Adopted") + ULURP numbers. `a030-cpc.nyc.gov/html/cpc/report.aspx?num=<ULURP>` 302s to the CPC report PDF on www1.nyc.gov → 403 (browser needed for the PDF itself, but the redirect leaks the canonical PDF URL).
- ZR portal greps: section numbers inside cross-refs are wrapped `<a class="sec-link-inline"><span>NN-NN</span></a>` — a grep for "FROM 66-11" fails; grep the left context instead. "FROM" prefix has 5 variants (FROM / FROM SECTION / FROM Section / FROM: / double-space).
- Drupal `/index.php/` prefix is a valid front-controller alias for HTML routes (200) but 404 for `/sites/default/files/` static assets — explains summarizer-transferred prefix errors.
- Drupal pagers: grep for `title="Go to last page"` — producers who only read visible pager numbers understate feed depth (recently-adopted: visible 0–8, actual last page 30).

Added during M1-T003 G1 (2026-07-16):
- **Socrata blobby datasets:** createdAt/rowsUpdatedAt/publicationDate are frozen at upload time, but `viewLastModified` DOES move when the blob/description changes — it is the usable change-polling signal (seen on mm69-vrje: frozen 2013 triple, viewLastModified 2026-05-26).
- **ArcGIS hosted layers: `maxRecordCount` can be LESS than the live feature count** (DCP nysp cap 92 vs 95 features; nysp_sd 317 vs 336) — unpaged queries silently truncate; always compare `returnCountOnly=true` against the cap.
- Socrata column descriptions can carry semantics absent from the official PDF dictionary (fdkv-4t4z zoning_district_1 may hold ZR section numbers for some Queens lots; bbl description has the corrected example the PDF typos). Always read both.
