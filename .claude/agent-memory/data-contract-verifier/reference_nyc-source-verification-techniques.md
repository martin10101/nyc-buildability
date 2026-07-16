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
