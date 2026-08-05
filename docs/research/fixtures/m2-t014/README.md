# M2-T014 fixtures — survey/official-document source research

Small, representative, verbatim extracts only (thin-client disk budget; no bulk downloads).
All retrievals live on **2026-08-05 UTC** (server-clock anchor from response `Date`/`Last-Modified`
headers; local session date 2026-08-04). Retrieval commands below are reproducible.

| File | Source | Retrieval command (verbatim) | HTTP |
|---|---|---|---|
| `dtm_taxlot_query_1000010010.json` | DOF DTM ArcGIS FeatureServer, TAX_LOT_POLYGON layer 0, per-BBL query | `curl "https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer/0/query?where=BBL='1000010010'&outFields=BBL,BORO,BLOCK,LOT,LOT_NOTE,EFFECTIVE_TAX_YEAR&returnGeometry=false&f=json"` | 200 |
| `dtm_taxlot_query_headers.txt` | same request, response headers | `curl -D <file> ...` (same URL) | 200 |
| `dtm_taxlot_layer0_meta.json` | DOF DTM ArcGIS FeatureServer, TAX_LOT_POLYGON layer 0 metadata | `curl "https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/DTM_ETL_DAILY_view/FeatureServer/0?f=pjson"` | 200 |
| `acris_viewer_307_headers.txt` | ACRIS Document Search viewer (records the anti-automation redirect) | `curl -D - "https://a836-acris.nyc.gov/DS/DocumentSearch/Index"` | 307 → BandwidthPolicy |

## Key evidence captured verbatim

- **DTM per-BBL query** returns `{"BBL":"1000010010","BORO":"1","BLOCK":1,"LOT":10,"LOT_NOTE":null,"EFFECTIVE_TAX_YEAR":"2026-2027"}`,
  `spatialReference wkid 102100 / latestWkid 3857` (EPSG:3857 Web Mercator — NOT the DCP EPSG:2263 used by
  MapPLUTO/Zoning Features; CRS must be validated before any coordinate math), anonymous (no token) access.
- **DTM response headers** publish a rate signal: `x-esri-org-request-units-per-min: usage=23;max=28800`
  and `Last-Modified: Tue, 04 Aug 2026 14:27:51 GMT` (a real freshness signal on the read-only replica).
- **ACRIS viewer** `HTTP/1.1 307 Moved Temporarily` → `Location: https://a836-acris.nyc.gov/BandwidthPolicy/ACRIS-BW-POL.html`
  — the register actively detects/blocks automated capture (see the inventory doc §4 for the verbatim policy).
