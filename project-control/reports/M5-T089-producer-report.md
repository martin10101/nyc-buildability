# M5-T089 producer report - official NYC building-footprint + height connector

- **Task:** M5-T089 (D-087-R001/R002/R003/R009, D-066-R001). Producer: geospatial-engineer
  (orchestrator-dispatched subagent). Requested status: **awaiting_gate**.
- **Worktree / branch:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t089`, `task/M5-T089-footprint-connector`.
- **Base (parent):** `114e5e56e158d6f263e58a314c383ea62ee7eff4` (verified: toplevel = wt-m5t089, HEAD = base, clean).
- **Commit:** one commit on top of the base, containing only the allowed paths. Its sha cannot
  be written inside itself; it is in the producer's return message.
- **Authority read:** `docs/research/building-footprints-source-2026-09.md`,
  `project-control/reports/M5-T087-G1.md`, `project-control/reports/M5-T087-G3.md`;
  conventions from `services/api/app/connectors/mappluto_geometry_arcgis.py` (read-only, not edited).

## IMPLEMENTATION

| File (allowed path) | Lines | sha256 (LF-normalized) |
|---|---|---|
| `services/api/app/connectors/building_footprints_arcgis.py` | 1075 (891 SLOC) | `1f0299c4f7aa79bdb2a89c02502dcf8856cf63e235aa7ed8c35a855f26a11307` |
| `services/api/tests/connectors/test_building_footprints_arcgis.py` | 834 | `f9d961553f4d8f82dd80f95626e8b767ef6f31a9964da478fa7921e8a4967ca5` |
| `services/api/tests/fixtures/building_footprints/README.md` (placeholder replaced) | 65 | `b6bb3c160445927dff1552dde80233193cd8d8cece87beaea333dd1b8b8ca012` |
| `services/api/tests/fixtures/building_footprints/MANIFEST.json` | 112 | `6d87f25c60660b3a3edaeb63383e3c67e6887c8d0c83d18273636b19701b6d05` |
| `services/api/tests/fixtures/building_footprints/*.json` - 11 recorded bodies | - | see fixture table |
| `project-control/reports/M5-T089-producer-report.md` (this file) | - | - |

What the connector does (module docstring lines 1-49 state the contract):

- Public API: `fetch_context_buildings(*, envelope | polygon, site_ground_elevation_ft, subject_bbl, page_size, transport, ...)`
  (connector:1017) returns `ContextBuildingsResult` (connector:331) with status `ok` or
  `refused`; it never raises (connector:1065). Also public: `build_query_url` (connector:510),
  `build_metadata_url` (506), `parse_footprint_geometry` (747), `classify_query_relation` (797).
- Transport = the MapPLUTO connector's shared engine `app.resilience.transport.request_with_retry`
  + `standard_retry_hooks` + `jittered_retry_after_delay` (connector:564-593), keyless, only the
  `Accept` header, stdlib `urllib` default transport.
- Metadata first (connector:616-671): layer name BUILDING, esriGeometryPolygon, OBJECTID, the 12
  LONG fields with pinned esri types (connector:113), maxRecordCount, supportsPagination +
  supportsOrderBy; publication CRS change and missing editingInfo are visible drift signals.
- Paging (connector:978-1014): `resultOffset` = records collected, `orderByFields=OBJECTID ASC`,
  page size = min(caller, 2000, layer maxRecordCount); refusals on over-page count, repeated
  OBJECTIDs, empty page claiming more data, page ceiling 50, more than 2000 footprints.
- Typed record `ContextBuilding` (connector:279): keys (DOITT_ID, BIN, BASE_BBL, MAPPLUTO_BBL),
  verbatim 2263 parts/holes, `height_roof_ft`, `ground_elevation_ft` (as published),
  `relative_base_z_ft = ground - site_ground` (connector:915), `relative_roof_z_ft`
  (connector:916), gaps, flags, verbatim attributes + esri geometry + digest, and the unit /
  datum labels (`HEIGHT_UNIT_BASIS` connector:148 keeps the RQ-1 INFERENCE label;
  `GROUND_DATUM_BASIS` connector:158).
- Written multipart/holes policy `FOOTPRINT_GEOMETRY_POLICY` (connector:166-181), applied by
  `parse_footprint_geometry` (connector:747-794).

CRS and units: horizontal EPSG:2263 (wkid 102718 / latestWkid 2263, US survey feet), obtained by
`outSR=2263` from a layer published in 102100/3857 - display/massing grade, not survey grade.
Vertical: HEIGHT_ROOF = roof height above ground (relative); GROUND_ELEVATION = as published,
NAVD88 per the City dictionary with its caveat (RQ-2); both labelled feet as an INFERENCE (RQ-1).

## Self-checks (verbatim)

[OBSERVED] cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t089\services\api`: `python -m ruff check .`

```
All checks passed!
exit=0
```

[OBSERVED] cwd `...\wt-m5t089\services\api`: `python -m pytest tests/connectors/test_building_footprints_arcgis.py -q`

```
........................................................................ [ 65%]
......................................                                   [100%]
110 passed in 2.57s
exit=0
```

[OBSERVED] cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t089`: `python tools/modularity_check.py --check`

```
selected 486 files; failures 0; warnings 25
  warn symbol_ceiling: apps/web/src/lib/surveyReview/types.ts - many top-level symbols (approximate count); a signal, not a verdict
  warn review_signal: services/api/app/api/v1/outline_bridge.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/api/v1/scenario_analysis.py - above the warning threshold; consider the module boundary before growing it further
  warn symbol_ceiling: services/api/app/connectors/building_footprints_arcgis.py - many top-level symbols; a signal, not a verdict
  warn review_signal: services/api/app/connectors/building_footprints_arcgis.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/connectors/dcm_street_centerline_arcgis.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/connectors/dtm_condo_soda.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: services/api/app/connectors/mappluto_geometry_arcgis.py - many top-level symbols; a signal, not a verdict
  warn review_signal: services/api/app/connectors/wide_street_buffer_engine.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/drawings/sheet_reader.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/rules/integration.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/breakeven.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/max_envelope.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: tools/agent_supervisor/cli.py - many top-level symbols; a signal, not a verdict
  warn review_signal: tools/agent_supervisor/codex_reviewer.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/durable_state.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/evidence.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/gate_wave.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/next_task.py - above the warning threshold; consider the module boundary before growing it further
  warn symbol_ceiling: tools/agent_supervisor/policy.py - many top-level symbols; a signal, not a verdict
exit=0
```

Extra [OBSERVED] (cwd `...\services\api`): `python -m pytest tests/connectors -q -p no:cacheprovider`
-> `1029 passed in 28.06s` (no collateral in sibling connector suites); the new suite with
`-W error` -> `110 passed`. Local Python is 3.11.9; CI (3.12) is the authority -
[PREDICTED] green on CI; harvest recipe: the api CI job at the integrated head
(`ruff check .` then pytest).

**Modularity cohesion justification (policy s3/s11):** the module is ONE responsibility - a single
read-only official-source connector (request building, response validation, typed parse of one
layer). It has 891 SLOC and 49 top-level symbols: above the 750 justification threshold and the
40-symbol signal, below the 1,000 hard limit. The size comes from the contract surface the packet
requires (a typed error per refusal class, the written policy strings, typed gap readers), in
line with the peer connector `dcm_street_centerline_arcgis.py` (902 SLOC). The packet allows one
production path, so a split was not in scope; a later split (for example, moving the geometry
policy into its own module behind a facade) is possible without changing the public names.

## Per-scenario evidence

**AS-1 request contract** - [OBSERVED]
- URL builder `_query_url` connector:522-544: `where=1=1`, geometry, `inSR=2263`,
  `spatialRel=esriSpatialRelIntersects`, LONG `outFields`, `returnGeometry=true`, `outSR=2263`,
  `orderByFields=OBJECTID ASC`, `resultRecordCount`, `resultOffset`, `f=json`.
- test:167 every recorded query URL in MANIFEST.json is reproduced byte-for-byte by the builder;
  test:189 (envelope + polygon) asserts outSR/inSR 2263, intersects, the long names, no short
  names, no `*`, ordered paging; test:209 pins the field types against the recorded layer JSON;
  test:217 paging follows `exceededTransferLimit` (metadata, page 1, page 2 in order; 3
  buildings); test:226 page size capped by the layer maxRecordCount; test:255 / test:266 invalid
  envelopes, polygons and caller parameters are refused before any I/O (transport never called).

**AS-2 parse + datum + policy** - [OBSERVED]
- test:276 recorded pages parse into typed records with verbatim 2263 rings, verbatim attributes
  and geometry, keys, heights, year, label, source, last-edited time; CRS stamp.
- test:303 `relative_base_z_ft` exact on the fixture: site ground 197 -> 0.0 / 0.0 / -2.0
  (grounds 197 / 197 / 195); site ground 195.5 -> -0.5 / 1.5; relative roof 33.49 and 19.28.
- test:319 units/datum labels keep "INFERENCE" + "RQ-1", NAVD88 + "RQ-2" + the centroid
  definition; test:329 no site ground -> typed gap on every record, never a default.
- test:337 within vs partial overlap on the real envelope; test:346 real lot-polygon query ->
  subject footprint `within` its MapPLUTO lot; test:442 synthetic inside / split / edge touch /
  corner touch / outside -> `within` / `partial_overlap` / `boundary_touch` / `boundary_touch` /
  `disjoint_locally` (touch is never overlap); test:449 server-vs-local disagreement kept + flagged.
- Policy: test:356 real courtyard hole kept on its part (`has_holes`); test:372 multipart keeps
  every part in order; test:412 touching parts kept (`parts_touch`); test:406 eleven unusable
  cases typed (null, not polygon, empty, unclosed, non-finite, collinear, malformed,
  self-intersecting ring, invalid part, no clockwise exterior, hole outside, overlapping parts);
  test:419 an unusable geometry's record is still returned (never dropped).
- test:462 provenance quintuple complete (source ids, request URLs, retrieved_at, dataset last
  edit 2026-09-20T02:16:01Z, response digests = the fixture sha256s); test:478 valid empty result.

**AS-3 honest gaps** - [OBSERVED]
- test:488 real zero height -> `height_roof_zero_not_available` gap, no roof z, ground kept;
  test:505 NULL / 0.0 / negative / text / bool / overflowing heights -> typed gaps.
- test:516 real placeholder (1003) -> placeholder gap + zero height gap + missing ground gap;
  relative base stays None (never the site ground); BBL carried verbatim.
- test:532 real condo: `condo_billing_lot_join` + `mappluto_bbl_differs_from_base_bbl`; join to
  the billing BBL True; seen from the base BBL -> False + `base_bbl_is_subject_but_mappluto_bbl_differs`;
  test:548 real zero height on a condo billing lot carries both.
- test:570 million-BIN, undocumented/missing feature code, unparseable BBLs, missing DOITT_ID,
  zero year, zero/malformed ground, missing edit date -> typed; test:581 every None value has a
  matching gap; test:604 documented feature-code domain.
- Named mutation: defaulting a missing height reddens test:488 and test:505 (M1, M2 below).

**AS-4 fail-closed transport** - [OBSERVED] every refusal carries error type, correlation id,
  failed request URL, time and (when a body arrived) its digest.
- test:633 HTTP 500 x3, 404, 429 x3, timeout x3, network failure x3 -> typed refusals with the
  page URL; test:642 recorded ArcGIS error object -> `upstream_error`, code "400", body digest =
  fixture sha256; test:652 truncated JSON -> `malformed_response` + digest; test:664 wrong shapes.
- test:669 recorded Web-Mercator page (wkid 102100) -> `wrong_crs`; test:677 non-empty page
  without spatialReference -> `wrong_crs`.
- test:685 over-page count (2 features for a 1-feature request) -> `paging_pathology`
  `over_page_count`; test:694 repeated OBJECTIDs; test:700 zero progress; test:709 page ceiling
  and feature cap -> refusals, never truncation.
- test:733 eight schema-drift mutations of the recorded layer JSON -> `schema_drift` before any
  page; test:745 publication-CRS change / missing edit date -> visible drift signals;
  test:757 unknown attribute -> drift signal; test:766 budget exhaustion; test:773 a non-typed
  RuntimeError never escapes (`internal_error`).

**AS-5 scope** - [OBSERVED]
- test:147 fixture pack: every file sha256-pinned (LF-normalized), each <= 16 KB, README lists
  every file + digest; test:788 module imports only stdlib + shapely + `app`; test:801 no other
  `app/` module references the connector (not wired; no route, no `main.py`, no web change);
  test:808 no credential material in the pack; test:816 keyless requests with only the Accept
  header; test:829 replay never reaches the network.
- Zero new dependencies: no requirements/lockfile change (git status shows only allowed paths).
- ruff + modularity clean (above).

## Fixture provenance

Captured once with curl from the official endpoint on 2026-09-24 UTC (keyless). `retrieved_at` =
the HTTP `Date` header. Full request URLs are in `MANIFEST.json`; each query URL is the
connector's own builder output (test:167). Pack total 38,561 bytes of bodies.

| File | Request | HTTP | retrieved_at | Bytes | sha256 |
|---|---|---|---|---|---|
| layer_metadata.json | `FeatureServer/0?f=json` | 200 | 2026-09-24T10:17:08Z | 10897 | bba7e9f9261324daaa275aee3cff5d5b642c54778e1b98a92a53dbbe28810374 |
| subject_2033800084_envelope_p1.json | envelope 1020160,267240,1020230,267325; count 2 offset 0 | 200 | 2026-09-24T10:18:29Z | 4291 | 57540d8f53e34319ac434ae6b1162e7ceb7610f6146e7e599bd5f7a004b40adb |
| subject_2033800084_envelope_p2.json | same; count 2 offset 2 | 200 | 2026-09-24T10:19:44Z | 2680 | 3d69ea840ef87c96adaa3aaaab86e605d2f554a4d55cbe6f38f798e062a95f89 |
| subject_2033800084_lot_polygon.json | MapPLUTO 26v2 lot ring polygon; count 2000 | 200 | 2026-09-24T10:20:22Z | 3539 | 80da5f892a6c638c90153390f4a736bd9a7fbfc62de76c76f4a18311f56e1d5e |
| condo_4068157501_envelope.json | envelope 1036960,202070,1037030,202130 | 200 | 2026-09-24T10:21:13Z | 3757 | 561fc888b846dc4440a0494d70af353fc75ca23d4bc89cfbcccea54ec2af031d |
| courtyard_hole_1011250025_envelope.json | envelope 990980,222312,990990,222322 | 200 | 2026-09-24T10:22:04Z | 3609 | 5a610e063bd66f4e98e6cc5431fa1b1881cb91a84ffe500f69b2578c48854214 |
| placeholder_zero_height_null_ground_envelope.json | envelope 992333,215590,992341,215598 | 200 | 2026-09-24T10:22:41Z | 2477 | 9a1e8357f80a49fea0fd952ef06b1ab533fc4901c0c1d4dbb76928cc661762cd |
| zero_height_condo_2059447501_envelope.json | envelope 1009525,266530,1009540,266545 | 200 | 2026-09-24T10:24:16Z | 2602 | 363497c3c69c9fa3d3891134827bd445ef2a0430e1a25e01551ebdd1b450fb97 |
| empty_result_envelope.json | envelope 990975,222270,990985,222280 | 200 | 2026-09-24T10:24:28Z | 249 | d4c55ec3f7eb63f18cc24133fe664a027e07721fc7d050682096000a7c576c59 |
| subject_2033800084_no_outsr_web_mercator.json | page-1 URL without outSR (replayed) | 200 | 2026-09-24T10:25:11Z | 4331 | 4481b86e5743c5617393fcdae0506cf622e34a7264532fe750faebe578d67d0b |
| short_field_names_error_object.json | page-1 URL with HEIGHTROOF/GROUNDELEV (replayed) | 200 | 2026-09-24T10:25:59Z | 129 | 4b24b6dd1224f463d44f751c89ddcc902759f00650ba8371c1e128801a5ebd30 |

## Mutation table (RED then restore GREEN)

[OBSERVED] cwd `...\services\api`; each mutation = one exact-once replacement in the connector,
run the named test(s), restore the original bytes, re-run. Restored connector sha256
`1f0299c4f7aa79bdb2a89c02502dcf8856cf63e235aa7ed8c35a855f26a11307` (= final file).

| Id | AS | Mutation | Named test(s) | Mutated | Restored |
|---|---|---|---|---|---|
| M1 | AS-3 | zero height passes through as 0.0 (default) | test_as3_zero_height_is_a_typed_gap_never_a_default | RED 1 failed | GREEN 1 passed |
| M2 | AS-3 | NULL height defaulted to 0.0 | test_as3_missing_or_invalid_heights_are_typed_gaps | RED 1 failed, 5 passed | GREEN 6 passed |
| M3 | AS-3 | missing ground replaced by site ground | test_as3_placeholder_and_null_ground_are_typed_gaps | RED 1 failed | GREEN 1 passed |
| M4 | AS-2 | relative base = absolute ground | test_as2_relative_base_z_is_ground_minus_site_ground_exactly | RED 1 failed | GREEN 1 passed |
| M5 | AS-1 | outSR=2263 dropped | test_as1_connector_urls_reproduce..., test_as1_query_uses_outsr_2263... | RED 3 failed | GREEN 3 passed |
| M6 | AS-1 | short name HEIGHTROOF requested | test_as1_query_uses_outsr_2263... | RED 2 failed | GREEN 2 passed |
| M7 | AS-1 | exceededTransferLimit ignored | test_as1_pages_follow_exceeded_transfer_limit... | RED 1 failed | GREEN 1 passed |
| M8 | AS-4 | wrong-CRS gate removed | test_as4_recorded_web_mercator_page_is_refused_as_wrong_crs | RED 1 failed | GREEN 1 passed |
| M9 | AS-4 | over-page check removed | test_as4_over_page_count_is_refused | RED 1 failed | GREEN 1 passed |
| M10 | AS-4 | ArcGIS error object accepted | test_as4_recorded_arcgis_error_object_is_an_upstream_refusal | RED 1 failed | GREEN 1 passed |
| M11 | AS-4 | generic catch removed (exception escapes) | test_as4_unexpected_internal_exception_never_escapes | RED 1 failed | GREEN 1 passed |
| M12 | AS-2 | holes silently filled | test_as2_courtyard_hole_is_kept_on_its_part_and_flagged | RED 1 failed | GREEN 1 passed |
| M13 | AS-2 | multipart reduced to first part | test_as2_multipart_policy_keeps_every_part_in_response_order | RED 1 failed | GREEN 1 passed |
| M14 | AS-2 | boundary touch reported as overlap | test_as2_query_relation_boundary_touch_is_not_overlap | RED 2 failed, 3 passed | GREEN 5 passed |
| M15 | AS-3 | condo billing-lot flag removed | test_as3_condo_billing_lot_join_is_flagged | RED 1 failed | GREEN 1 passed |
| M16 | AS-3 | placeholder not typed as a gap | test_as3_placeholder_and_null_ground_are_typed_gaps | RED 1 failed | GREEN 1 passed |

## Deviations and assumptions

1. **Refusal instead of raise.** `fetch_context_buildings` converts every exception, including a
   non-typed one, into a typed refusal (AS-4 "no exception escapes"). A non-typed exception
   becomes `internal_error` with only its class name recorded. Reviewers may weigh this against
   the risk of hiding a programming error.
2. **Metadata fixture is 10.9 KB**, larger than "a few KB". It is kept byte-exact (not trimmed)
   so its sha256 pins the real response.
3. **Two recorded bodies are replayed against a different URL** (the no-outSR page and the
   short-name error); both are labelled in MANIFEST/README and in the tests.
4. **Fixture format:** raw bodies plus `MANIFEST.json` (digest = file bytes), not the MapPLUTO
   pack's wrapper format.
5. **No resilient client** (cache, breaker, last-known-good) - only the shared bounded-retry
   engine. So no transport-staleness state exists.
6. **Engineering bounds, not source facts:** `MAX_QUERY_SPAN_FT` 5,000 ft, 200 polygon vertices,
   50 pages, 2,000 footprints, coordinate magnitude 5,000,000 ft (the accepted DCM bound).
7. **Relation classes are exact planar geometry** on published coordinates. No tolerance is
   applied even though photogrammetric features are stated as +/- 2 ft; a sliver overlap
   reports as `partial_overlap` with its area.
8. **Zero ground elevation** is kept as published with the flag `ground_elevation_zero_unverified`:
   the source does not say zero means "not available" for this field.
9. **`joins_subject_lot`** compares MAPPLUTO_BBL with the caller's subject BBL (recon section 5).
10. Modularity: above the justification threshold (justification above).

## DISCOVERIES (for docs/DISCOVERY_BACKLOG.md; not fixed in-packet)

1. **Short field names are not an HTTP 400.** Recorded: HTTP 200 carrying an ArcGIS error object
   (`code` 400, "'outFields' parameter is invalid"). The packet and the G1 wording say "return
   HTTP 400". The connector refuses both shapes.
2. **RQ-1 (height unit) still open.** Checked the service's own FGDC metadata
   (`.../BUILDING_view/FeatureServer/0/metadata`, 35,586 bytes, sha256
   `c77366cf5c7d6e0cf414a44b7d4476927494f3833b8633ede63443c12f02e658`, read 2026-09-24, not
   committed) and the ArcGIS item description (it only links to the City dictionary). Neither
   has a unit tag for HEIGHT_ROOF or GROUND_ELEVATION. Feet stays an INFERENCE.
3. **GROUND_ELEVATION definition conflict.** City dictionary: "Lowest Elevation at the building
   ground level." Service FGDC metadata: "an interpolated elevation value at the centroid (center
   point) of the building", from a 2010-LiDAR bare-earth DTM. The FGDC metadata never mentions
   NAVD88. Both are kept visible in `GROUND_DATUM_BASIS`. The wiring packet must pick the site
   ground knowingly; this may matter for G1.
4. **RQ-4 answered.** Every query response carries `x-esri-org-request-units-per-min:
   usage=N;max=28800` and `x-esri-query-request-units: 3`. The connector does not read them.
5. **Missing heights are published as 0, not NULL.** On 2026-09-24 `HEIGHT_ROOF IS NULL`
   returned zero features. The NULL path stays typed and is tested synthetically.
6. **Dummy-looking BBLs on placeholders and zero-height footprints** (for example 1201359999 and
   4201269999: lot 9999, Manhattan block 20135). They pass syntax checks, are carried verbatim,
   and are not interpreted. A MapPLUTO join will probably find no lot.
7. **Holes vs the massing builder (G3 F3 confirmed with real data).** The Dakota footprint
   (BIN 1028637) has a courtyard hole, and `massing_model._lot_polygon` refuses holes. The wiring
   packet must choose a holes-capable prism path or refuse flagged records.
8. **Capture-threshold wording conflict inside the FGDC metadata**: ">500 sq. feet" in `<logic>`
   vs ">400 sq. feet" in `suppInfo` and the City dictionary.
9. **Code graph was stale** at dispatch (`query.py --no-regen impact` -> "STALE (stale
   fingerprint): refusing to serve the cached graph"). No-consumer status was checked in source
   instead and is enforced by test:801.
10. The lot-polygon query returns only the subject footprint, while the envelope returns the
    neighbours too: a "lot plus neighbours" consumer should pass a buffered lot ring or an
    envelope. The connector never buffers; the caller decides.

## Limitations

- CI (Python 3.12) has not run; it is the authority for ruff and pytest.
- Fixture content is a 2026-09-24 snapshot of a weekly-released, daily-edited dataset.
- No live network test by design; transport behaviour is proven with the injected transport only.
