# D-040-R001 research deliverable — MapPLUTO lot-outline terrain (verbatim)

Orchestrator preservation note: returned by the official-source-researcher agent
("MapPLUTO research for R001") on 2026-09-12 and preserved verbatim below (transport
entity-decoding only). This is the research-first deliverable D-040-R001 mandates before
contracting the Packet-3 lot-outline work; the future connector/web/dependency packets
pin this report.

---

Research complete. Full report follows.

---

# Research report — D-040-R001 lot-outline increment (design-spec Packet 3)

Scope: facts to contract a MapPLUTO parcel-geometry path from BBL → lot outline on the address confirm card with MapLibre GL JS. Today 2026-09-12. No repo files written (memory-only, allowed).

## PART A — What already exists (repo inventory)

**A1. The MapPLUTO geometry connector already exists and returns polygon geometry by BBL** — `services/api/app/connectors/mappluto_geometry_arcgis.py` (2183 lines, task M2-T009, accepted; G1 report `project-control/reports/M2-T009-G1-data-contract-review.md`).

- Endpoint: `SERVICE_ROOT` = `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services`, `LAYER_NAME` = `MAPPLUTO`, layer 0 (`mappluto_geometry_arcgis.py:188-189`). Keyless.
- Query pattern: `build_lot_query_url` emits exactly one URL — `where=BBL%3D<int>&outFields=<10-field subset>&orderByFields=OBJECTID%20ASC&resultRecordCount=10&resultOffset=0&f=json` (`:1105-1128`). BBL comes only from `normalize_bbl`; callers cannot inject URLs/where-clauses.
- Geometry: returned in **esriJSON `rings`**, parsed at `fetch_lot_geometry` via `feature.get("geometry")` (`:1752`). `returnGeometry` is not set → ArcGIS default true, so polygon rings ARE returned. Output is normalized to a canonical feet-coordinate form + three digests (raw/original/normalized).
- CRS: **EPSG:2263 only** (wkid 102718 / latestWkid 2263, US survey feet). `require_authoritative_crs` raises `WrongCRSError` for anything else; area computed only in projected feet; docstring: "No reprojection happens in this module" (`:26-33, 471-489`).
- Fields fetched (`OUT_FIELDS`, `:233-244`): OBJECTID, BBL, BoroCode, Borough, Block, Lot, CondoNo, Version, Shape__Area, Shape__Length. **No lat/lon, no GeoJSON output.**
- source_registry: **no applied `source_registry` record exists in the repo.** The connector self-declares `SOURCE_ID="nyc-dcp-mappluto-arcgis"` (`:182`); a draft lives at `docs/research/source-registry-drafts/pluto-mappluto.json`; the fixture manifest `services/api/tests/fixtures/mappluto_geometry/MANIFEST.json:4` records the same source_id. Packet must confirm/apply the actual registry record.
- Fixtures: 34 fixtures under `services/api/tests/fixtures/mappluto_geometry/` (7 live-captured MPG01–MPG07 incl. Empire State single lot, Governors Island holes, Queens multipolygon; rest synthetic negatives). Tests: `services/api/tests/connectors/test_mappluto_geometry_arcgis.py`.

**What is MISSING for the confirm-card outline:** (1) geometry is 2263 feet, but MapLibre needs **EPSG:4326 lng/lat GeoJSON** — no 4326/GeoJSON emission path exists and the module refuses reprojection by design; (2) **no HTTP API route exposes lot geometry to the web** (the connector is consumed by `app/profile/wave_integration.py` and `app/spatial/`, not by a public `/v1` endpoint I could find); (3) no GeoJSON contract in `packages/contracts`.

**A2. Confirm card + map rendering in apps/web.** `apps/web/src/components/address/AddressConfirmCard.tsx` (M5-T016, 242 lines). Today the lot outline is an honest **placeholder** — `data-testid="lot-outline-placeholder"` at `:141-145` ("A parcel outline is not drawn here yet … Open the city's ZoLa map"). ZoLa deep-link is `https://zola.planning.nyc.gov/bbl/<10-digit-bbl>` built only from a client-re-validated BBL (`:36, :122-139`). **No map library is present anywhere in apps/web** — grep for `maplibre|mapbox|leaflet|geojson` across `apps/web` returned zero hits. This is a greenfield map addition. Constraint noted in the card's design lineage: D-040-R004 prohibits any dependency change to `apps/web/package.json` for the Next.js security item, but MapLibre admission is separate (see Part C).

**A3. Design-spec Packet 3 (`docs/design/address-entry-confirm-design-spec.md:124`), quoted verbatim:**
> "**Packet 3 (later increment, explicitly deferred) — real lot outline.** The lot outline is a **placeholder** in Packets 1–2: MapPLUTO geometry integration is not in scope here (the existing Confirm card already declares geometry 'not yet retrieved,' `ConfirmScreen.tsx:213-219`). Until then the honest stand-in is the ZoLa link (which shows the real, key-free outline) plus copy … Packet 3 renders the DCP/MapPLUTO geometry with MapLibre GL JS per `.claude/rules/3d-ui-expansion.md` when that connector lands; it is on the owner-review expansion hold and must not be planned or started here."

D-040-R001 (`project-control/directives/D-040-scoped-unblocks/requirements.json:11`) releases the hold for exactly this increment; `.claude/rules/3d-ui-expansion.md:5` mandates MapLibre GL JS for maps.

## PART B — Official sources (web research)

**B1. Live MapPLUTO ArcGIS FeatureServer** — verified 2026-09-12 against `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0?f=json`:
- name "MAPPLUTO"; currentVersion **12**; geometryType `esriGeometryPolygon`; spatialReference **wkid 102718 / latestWkid 2263**; maxRecordCount **2000**; supportsPagination true; capabilities "Query"; owner NYC DCP Information Technology Division.
- **Output formats: "JSON, geoJSON, PBF"** — so `f=geojson` IS supported.
- Query-by-BBL: `.../FeatureServer/0/query?where=BBL=<n>&outFields=...&f=geojson` (or `f=json`); pagination via resultRecordCount/resultOffset. Auth: none (keyless).
- The ArcGIS query API supports `outSR=4326` to reproject output to WGS84 lng/lat (standard ArcGIS REST parameter; the layer's native SR is 2263). MapLibre consumes 4326 GeoJSON directly.
- MapPLUTO release version string (e.g. "26v1") is carried in the per-feature `Version` field, not the layer JSON; NYC DCP's dataset page notes a May 2026 publication with 2025 parcel data ([nyc.gov MapPLUTO page](https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change)). Update cadence: roughly semiannual DCP releases; the connector already tracks freshness via `editingInfo.dataLastEditDate`.
- Terms/attribution: NYC DCP data is provided "for informational purposes only" (the connector already carries the DCP disclaimer, `:78`); attribution to NYC Department of City Planning is expected on any map display.

**B2. Known lot-outline limitations (already handled by the connector, must surface in UI):**
- Condo billing/unit BBL quirk: **unit lots 1001–6999 carry NO polygon**; billing lots 7501–7599 carry the merged complex polygon (`_condo_classification`, `:1643-1682`; fixtures MPG04/MPG05). A unit-lot BBL returns an empty result → confirm card must show honest "no outline for this unit lot" rather than a blank/misleading map.
- Multipart lots: true multipolygons occur (shoreline-clipped parcels, e.g. Queens BBL 4142600001, fixture MPG07) → renderer must handle MultiPolygon, not just Polygon.
- Water/edge lots and holes: holed polygons occur (Governors Island 1000010010, fixture MPG06). ±20 ft horizontal accuracy is the source's own statement (`BOUNDARY_TOLERANCE_FT`, `:210-215`) — an outline is approximate, reinforcing the design's "a pin would mislead" honesty posture.
- The connector types `multiple_features`, `no_feature`, `review_required`, `invalid_geometry` outcomes — the map UI must render each honestly (no silent first-pick, no fabricated outline).

## PART C — MapLibre GL JS dependency-security prep

**C1. Versions and age gate (repo rule: admitted version must be ≥ 604800 s / 7 complete days old as of 2026-09-12):**
- Current stable: **maplibre-gl 6.9.0**, published ~2026-09-09/10 (≈2–3 days old) → **FAILS age gate.**
- 6.8.0, published ~2026-09-07 (≈5 days) → **FAILS.**
- **6.7.0, published 2026-09-02 (≈10 days) → PASSES age gate** and is the newest admission candidate today. (6.6.0 ~2026-08-24 and earlier also pass.)
- Exact npm publish timestamps must be pulled from the registry at admission time (the gate needs the 604800 s-precise `time[version]` value; my dates are from GitHub releases + npm search and should be re-verified mechanically). Sources: [npm maplibre-gl versions](https://www.npmjs.com/package/maplibre-gl?activeTab=versions), [GitHub releases](https://github.com/maplibre/maplibre-gl-js/releases).

**C2. Advisories:** Snyk reports **no known vulnerabilities** for maplibre-gl at any severity across 6.7.0/6.8.0/6.9.0 ([Snyk](https://security.snyk.io/package/npm/maplibre-gl)). One historical advisory, **CVE-2026-85061** (zero-click XSS via map attribution HTML sanitization), was **fixed in 6.4.1** ([FORSMILE writeup](https://forsmile.jp/en/articles/maplibre-gl-js-cve-2026-85061-xss-20260904)); 6.7.0 includes that fix. A later DOM-sanitization hardening (iframe/srcdoc) shipped in 6.9.0 — not a published CVE, but note it is absent from 6.7.0; the packet's G5 review should weigh this against the age gate.
- License: **BSD-3-Clause** (permissive; fine for this repo).
- Transitive footprint: maplibre-gl pulls a non-trivial dependency tree (historically ~20–30 transitive packages: `@mapbox/*` tile/geometry utils, `geojson-vt`, `potpack`, `earcut`, `gl-matrix`, etc.). **Each transitive package must independently pass the age + advisory + exact-pin + integrity gates** — this is a material admission cost and the single biggest reason to weigh C3. The exact tree must be enumerated from `package-lock.json` at admission (no fabricated count).

**C3. No-new-dependency alternative (inline SVG from GeoJSON):** Feasible. The outline is a static, non-interactive shape; an inline `<svg><polygon>`/`<path>` computed from the parcel GeoJSON (fit to a viewBox, no basemap) needs **zero new dependencies**, sidesteps the entire MapLibre + transitive age/advisory gate, and satisfies "draw the real lot outline." **What is lost vs the spec:** no basemap/orthophoto context, no pan/zoom, no north/scale, no surrounding-parcel context — the outline floats without geographic reference. The design spec (`.claude/rules/3d-ui-expansion.md:5`) explicitly names MapLibre for maps, so an SVG-only outline is a **reduced-scope variant**, not spec-complete; it would need an owner/design note. A pragmatic middle path: ship the SVG outline first (no dependency, honest, fast) and treat MapLibre as a follow-up once 6.7.0+ clears admission — but that is a packetization decision for the orchestrator.

## PACKET IMPLICATIONS

**Connector task must add:**
1. A 4326-GeoJSON emission path for the lot outline — either request `f=geojson&outSR=4326` from the service, or reproject the canonical 2263 geometry to 4326. **Critical constraint:** keep the authoritative 2263 path for area/canonical digests/provenance intact; a reprojected transport must NOT replace 2263 provenance (the module's `WrongCRSError` discipline and area-in-feet-only guarantee must survive). Reprojection introduces a new, separately-tested output; add fixtures for the 4326 form.
2. A public API route exposing lot geometry by BBL to the web (none exists today) — with the existing typed outcomes (`no_feature`/`multiple_features`/`review_required`/`invalid_geometry`) mapped to honest UI states, behind `INTERNAL_RULE_EVAL_ENABLED`.
3. A GeoJSON/geometry contract in `packages/contracts` (additive, versioned) plus a `source_registry` record for `nyc-dcp-mappluto-arcgis` (currently only a draft + connector self-declaration exist).

**Web task must add:**
1. Lot-outline rendering on `AddressConfirmCard.tsx`, replacing the `lot-outline-placeholder` block (`:141-145`), fed by the new API route.
2. Handle MultiPolygon, holes, empty (condo unit lot), and review-required outcomes honestly; keep the ZoLa link and ±20 ft/approximate-outline copy.
3. Either add MapLibre GL JS (per 3d-ui rule) or the SVG fallback (C3). Flag the Render/flag posture: ships behind the same feature flag.

**Dependency-admission facts:**
- Package `maplibre-gl@6.7.0` — the newest version ≥7 days old as of 2026-09-12 (published ~2026-09-02); 6.8.0/6.9.0 FAIL the age gate today.
- Advisories: none current (Snyk clean); CVE-2026-85061 fixed in 6.4.1 (present in 6.7.0). License BSD-3-Clause.
- G5 provenance review required (new package). All ~20–30 transitive deps must each pass age + advisory + exact-pin + integrity gates — enumerate from the lockfile at admission; re-verify all publish timestamps mechanically against the npm registry.

**No-new-dependency alternative tradeoff:** inline SVG polygon from GeoJSON draws the real outline with zero dependency-admission cost and no age-gate wait, but loses the basemap, geographic context, and pan/zoom the MapLibre spec calls for — spec-reduced, needs a design/owner note.

**Assumptions/limitations:** MapLibre exact publish timestamps and the transitive-dependency count were not verified against the live npm registry API (blocked from running npm here) — the packet's `/dependency-security` step must confirm them. No API route for lot geometry was found via grep; the packet should confirm before assuming a new route is needed. I ran no repo tooling (read-only research scope).

Sources:
- [MapPLUTO FeatureServer/0 (live)](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0) — accessed 2026-09-12
- [NYC DCP MapPLUTO dataset page](https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change) — accessed 2026-09-12
- [npm maplibre-gl versions](https://www.npmjs.com/package/maplibre-gl?activeTab=versions) — accessed 2026-09-12
- [GitHub maplibre-gl-js releases](https://github.com/maplibre/maplibre-gl-js/releases) — accessed 2026-09-12
- [Snyk maplibre-gl advisories](https://security.snyk.io/package/npm/maplibre-gl) — accessed 2026-09-12
- [CVE-2026-85061 writeup (fixed in 6.4.1)](https://forsmile.jp/en/articles/maplibre-gl-js-cve-2026-85061-xss-20260904) — accessed 2026-09-12
