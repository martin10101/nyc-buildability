# Building-footprint recorded fixtures (M5-T089)

Recorded responses from the official NYC OTI **BUILDING** layer (NYC Open Data `5zhs-2jue`),
ArcGIS feature service `https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0`.
Keyless service: no credential exists in this pack.

- **Capture:** `curl -sS` GET, one request per file, on 2026-09-24 UTC by the M5-T089 producer.
  Each body is stored byte-for-byte as returned (single-line JSON, no trailing newline).
- **retrieved_at:** the HTTP `Date` response header of that capture.
- **sha256:** hex over the exact file bytes (= the response body bytes). The test suite
  re-hashes every file (LF-normalized) against `MANIFEST.json`, which carries the full request
  URL of each capture. The connector's own URL builder reproduces those URLs byte-for-byte
  (test `test_as1_connector_urls_reproduce_the_recorded_requests_byte_for_byte`).
- **Offline:** tests read only these files through an injected transport; no test touches
  the network. Failure shapes the live service cannot produce on demand are SYNTHETIC
  in-memory mutations of these recorded bodies, labelled as such in the tests. No synthetic
  file is stored here.
- **Source data freshness at capture:** layer `editingInfo.dataLastEditDate` = 1789870561226
  ms = 2026-09-20T02:16:01Z (also the HTTP `Last-Modified` header of every capture).

## Files

Query URLs share one shape (see `MANIFEST.json` for each full URL): `where=1=1`, the
`geometry` below with `inSR=2263` and `spatialRel=esriSpatialRelIntersects`, the LONG
out-field list `OBJECTID,DOITT_ID,BIN,BASE_BBL,MAPPLUTO_BBL,HEIGHT_ROOF,GROUND_ELEVATION,CONSTRUCTION_YEAR,FEATURE_CODE,GEOM_SOURCE,LAST_EDITED_DATE,LAST_STATUS_TYPE`,
`returnGeometry=true`, `outSR=2263`, `orderByFields=OBJECTID ASC`, `resultRecordCount`,
`resultOffset`, `f=json`.

| File | Request (geometry / paging) | HTTP | retrieved_at (UTC) | Bytes | sha256 |
|---|---|---|---|---|---|
| `layer_metadata.json` | `FeatureServer/0?f=json` (layer metadata) | 200 | 2026-09-24T10:17:08Z | 10897 | `bba7e9f9261324daaa275aee3cff5d5b642c54778e1b98a92a53dbbe28810374` |
| `subject_2033800084_envelope_p1.json` | envelope 1020160,267240,1020230,267325; count 2, offset 0 | 200 | 2026-09-24T10:18:29Z | 4291 | `57540d8f53e34319ac434ae6b1162e7ceb7610f6146e7e599bd5f7a004b40adb` |
| `subject_2033800084_envelope_p2.json` | same envelope; count 2, offset 2 | 200 | 2026-09-24T10:19:44Z | 2680 | `3d69ea840ef87c96adaa3aaaab86e605d2f554a4d55cbe6f38f798e062a95f89` |
| `subject_2033800084_lot_polygon.json` | polygon = MapPLUTO 26v2 lot ring of 2033800084; count 2000 | 200 | 2026-09-24T10:20:22Z | 3539 | `80da5f892a6c638c90153390f4a736bd9a7fbfc62de76c76f4a18311f56e1d5e` |
| `condo_4068157501_envelope.json` | envelope 1036960,202070,1037030,202130; count 2000 | 200 | 2026-09-24T10:21:13Z | 3757 | `561fc888b846dc4440a0494d70af353fc75ca23d4bc89cfbcccea54ec2af031d` |
| `courtyard_hole_1011250025_envelope.json` | envelope 990980,222312,990990,222322; count 2000 | 200 | 2026-09-24T10:22:04Z | 3609 | `5a610e063bd66f4e98e6cc5431fa1b1881cb91a84ffe500f69b2578c48854214` |
| `placeholder_zero_height_null_ground_envelope.json` | envelope 992333,215590,992341,215598; count 2000 | 200 | 2026-09-24T10:22:41Z | 2477 | `9a1e8357f80a49fea0fd952ef06b1ab533fc4901c0c1d4dbb76928cc661762cd` |
| `zero_height_condo_2059447501_envelope.json` | envelope 1009525,266530,1009540,266545; count 2000 | 200 | 2026-09-24T10:24:16Z | 2602 | `363497c3c69c9fa3d3891134827bd445ef2a0430e1a25e01551ebdd1b450fb97` |
| `empty_result_envelope.json` | envelope 990975,222270,990985,222280; count 2000 | 200 | 2026-09-24T10:24:28Z | 249 | `d4c55ec3f7eb63f18cc24133fe664a027e07721fc7d050682096000a7c576c59` |
| `subject_2033800084_no_outsr_web_mercator.json` | page-1 request **without** `outSR` | 200 | 2026-09-24T10:25:11Z | 4331 | `4481b86e5743c5617393fcdae0506cf622e34a7264532fe750faebe578d67d0b` |
| `short_field_names_error_object.json` | page-1 request with shapefile short names `HEIGHTROOF`,`GROUNDELEV` | 200 | 2026-09-24T10:25:59Z | 129 | `4b24b6dd1224f463d44f751c89ddcc902759f00650ba8371c1e128801a5ebd30` |

## What each file proves

- **Lot 2033800084 + neighbours** (the research sample lot): three footprints on three tax lots
  (OBJECTIDs 29471 / 229537 / 794314; ground 197 / 197 / 195), split over two pages with
  `exceededTransferLimit=true` on page 1 - paging and the relative datum.
- **Lot polygon:** the same lot queried with its MapPLUTO lot ring returns only the subject
  footprint (a precise neighbour set needs the ring, not a box).
- **Condo:** three buildings on BASE_BBL 4068150020 share billing MAPPLUTO_BBL 4068157501
  (lot 7501), the recon's condo-join proof.
- **Courtyard hole:** BIN 1028637 has one clockwise exterior and one counterclockwise hole.
- **Placeholder:** FEATURE_CODE 1003 triangle with HEIGHT_ROOF 0 and GROUND_ELEVATION null.
- **Zero height:** a regular building (2100) with HEIGHT_ROOF 0, also on a condo billing lot.
- **Empty result:** a well-formed zero-feature page (no `spatialReference` key).
- **Web Mercator page:** without `outSR` the service answers in wkid 102100 / 3857; replayed
  against the connector's page-1 URL to prove the wrong-CRS refusal (the connector never omits
  `outSR`).
- **Short field names:** the shapefile names return **HTTP 200 carrying an ArcGIS error object**
  (`code` 400, "'outFields' parameter is invalid"), not an HTTP 400 status; replayed to prove
  the error-object refusal (the connector never emits short names).

The MapPLUTO lot ring used for the polygon query was read from the DCP_GIS MAPPLUTO service
(`.../MAPPLUTO/FeatureServer/0/query?where=BBL%3D2033800084&outFields=OBJECTID%2CBBL%2CVersion&returnGeometry=true&f=json`,
2026-09-24, Version 26v2); it is pinned as a constant in the test file, not stored here.
