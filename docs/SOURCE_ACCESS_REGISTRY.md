# Canonical Source Access Registry

**Status:** Canonical per-source access-governance record (task M2-T011, owner directive 2026-07-20).
**Relationship to other artifacts:** `docs/research/source-registry-drafts/*.json` remain the raw research
artifacts; `docs/research/*.md` hold the full evidence chains. This file is the single governance view of
HOW each external source may be accessed. It contains no facts that are not already evidenced in the
repository; anything not yet evidenced is marked **to verify at G1**. Nothing here was re-researched from
the live web for this document.
**Compiled:** 2026-07-20 (from accepted repository research; per-source "last policy verification" dates
below are the dates the official pages were actually read in accepted research sessions).

## Governance rules (apply to every source)

1. **ZoLa is NOT a production API.** The ZoLa browser interface (zola.planning.nyc.gov, DCP's web mapping
   application) is a presentation layer for human users. This platform must never scrape or depend on the
   ZoLa interface. The production sources are the underlying official datasets and services recorded below
   (GIS Zoning Features ArcGIS services, ZTLDB, PLUTO/MapPLUTO, etc.). ZoLa may be used by humans for manual
   cross-checks only, and any such cross-check is recorded as a secondary presentation, never as machine
   provenance.
2. **No permanence, pricing, or SLA assumptions.** No free government service in this registry is assumed to
   be permanently free, unlimited, stable, versioned, or covered by any service-level agreement. Only the
   documented commitments cited per source are recorded; where an official page publishes no limit or no
   cadence, the registry says "none published" rather than inventing one. Observed behavior (e.g. a stalled
   monthly update) is recorded as observation with its date, not as a contract.
3. **Two-staleness rule (owner, 2026-07-17).** Source-dataset freshness (how old the official publication
   is) and transport staleness (whether we served a cache/last-known-good copy) are independent dimensions
   and are never merged. Every implemented connector stamps them separately (contract 1.3.0).
4. **Access-mode taxonomy** used below: `API (live request)` | `bulk file download` | `authorized document
   download` | `HTML corpus ingestion` | `reference-only`.
5. **Socrata platform baseline (applies to every SODA source below).** Authentication is not required; an
   application token (`X-App-Token`, env `SOCRATA_APP_TOKEN`) is optional and recommended. Published
   rate-limit statement (dev.socrata.com/docs/app-tokens, verified 2026-07-16, M1-T001 E7): tokenless
   requests share an IP-throttled common pool; tokened requests are "not throttled unless requests are
   determined abusive or malicious"; **no numeric quota is published**; the throttle signal is HTTP 429 with
   no documented body shape and no documented Retry-After guarantee. Schema-drift signature: HTTP 400 with
   `errorCode query.soql.no-such-column`. SODA omits null fields per record — schema always comes from the
   `/api/views/<id>.json` columns array, never from record keys.

---

## 1. PLUTO — NYC Open Data SODA (implemented connector)

| Field | Record |
|---|---|
| Official source | NYC DCP, Primary Land Use Tax Lot Output (PLUTO), NYC Open Data dataset `64uk-42ks` |
| Endpoint URLs | Data: `https://data.cityofnewyork.us/resource/64uk-42ks.json` — Metadata/schema: `https://data.cityofnewyork.us/api/views/64uk-42ks.json` |
| Access mode | API (live request), per-BBL bounded queries; bulk fallback is the DCP BYTES CSV release (see section 4 notes) |
| Authentication | None required; optional Socrata app token (platform baseline above); token never logged, never in payloads |
| Published quota / rate limits | None published numerically — official statement is the Socrata platform baseline (dev.socrata.com/docs/app-tokens, verified 2026-07-16) |
| Retrieval / refresh cadence | Source: major release quarterly, minor release monthly (zoning attributes only) per official README 26v1. Platform retrieval: on-demand per analysis, cached (TTL) by the resilience layer |
| Source freshness signal | Primary: per-record `version` field (e.g. `26v1`). Secondary: Socrata `rowsUpdatedAt` (observed 2026-05-28T19:50:48Z, consistent with 26v1). Minor-release propagation lag to SODA unobserved (draft OQ-6) |
| Schema / file version | 108-column inventory pinned from the api/views columns array (fixture F08, captured 2026-07-16); per-run drift check `check_columns_for_drift` |
| Terms / attribution links | DCP informational-purposes-only disclaimer (README 26v1); NYC Open Data terms (opendata.cityofnewyork.us/overview): no warranty, NYC.gov Terms of Use + Privacy Policy apply, no prohibition on automated API access (verified at M1-T001 G1) |
| Last policy verification | 2026-07-16 (M1-T001 G1). Re-verify at this task's G1 (TC-S6) |
| Outage / last-known-good behavior | Implemented (M1-T009 `ResilientPlutoFetcher`): typed errors (rate_limited / timeout / source_unavailable / schema_drift), bounded jittered retry with exact Retry-After honoring, circuit breaker, TTL cache, last-known-good serve with VISIBLE typed staleness; budget-exceeded never masked by LKG |
| Suitability | Live requests: YES (per-BBL). Scheduled ingestion: planned citywide bulk import belongs to the DCP bulk channel, not this API (maxRecordCount-free but ~860k rows; paging plan exists, F11 deferred). Reference-only: no |

## 2. NYC GIS Zoning Features — DCP ArcGIS services (implemented connector)

| Field | Record |
|---|---|
| Official source | NYC DCP, GIS Zoning Features: six ArcGIS Online feature services under owner DCP_GIS — `nyzd`, `nyco`, `nysp`, `nysp_sd`, `nylh`, `nyzma` |
| Endpoint URLs | `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/<layer>/FeatureServer/0` (pinned root; layer allowlist in the connector). Companion citywide FileGDB blob: `https://data.cityofnewyork.us/api/views/mm69-vrje.json` (zip ~3.15 MB) |
| Access mode | API (live request), bounded allowlisted queries with mandatory deterministic paging; bulk file download (mm69-vrje FileGDB zip) as the snapshot channel |
| Authentication | None (anonymous queries verified live 2026-07-16 on all six services); keyless — no credential exists to leak |
| Published quota / rate limits | None published. Per-request page caps are published in service metadata (`maxRecordCount`): nyzd 2000, nyco 2000, nysp 92, nysp_sd 317, nylh 14, nyzma 1292 (fetched live 2026-07-16). CAP-EXCEEDANCE HAZARD: live feature counts EXCEED the cap on nysp/nysp_sd/nyzma — unpaged reads silently truncate; paging is mandatory on every layer |
| Retrieval / refresh cadence | Source: monthly — official verbatim (nyzd_metadata.pdf): "The downloadable zoning data will be updated on the last Monday of every month." Platform retrieval: on-demand bounded queries + planned monthly Render-worker extraction (follow-up task; B-001 persistence blocker stands) |
| Source freshness signal | `editingInfo.dataLastEditDate` per layer (all six observed 2026-07-01, re-observed identical 2026-07-20); no version label on the ArcGIS channel (draft OQ-6). Blob channel: `viewLastModified` (live signal) + description version string (`Current version: 202604` — lags) + content hash |
| Schema / file version | Per-layer field inventories pinned in `LAYER_SPECS` and cross-checked against fixtures ZF01a-f (live capture 2026-07-20); CRS pinned wkid 102718 / latestWkid 2263 (EPSG:2263) and validated before any coordinate use |
| Terms / attribution links | DCP informational-purposes-only disclaimer (nyzd metadata PDF, verified by direct read 2026-07-16); data "freely available to all New York City agencies and the public". OFFICIAL USE LIMITATION (verbatim): "These features are not intended for determining zoning at the individual tax lot level" — lot-level assignment belongs to ZTLDB/PLUTO. Horizontal accuracy ± 20 ft (official Data Quality statement) — near-boundary conclusions typed uncertain |
| Last policy verification | 2026-07-16 (metadata PDF + services); freshness re-observed 2026-07-20 (M2-T007 capture). Re-verify at this task's G1 (TC-S6) |
| Outage / last-known-good behavior | Implemented (M2-T007 `ResilientZoningFeaturesClient`): typed taxonomy incl. `upstream_error` for the live-verified ArcGIS error-object-with-HTTP-200 behavior (fixture ZF06), `paging_pathology` (repeated id / duplicate page / zero progress / page budget / count mismatch), circuit breaker, TTL cache, LKG with truthful transport staleness, per-analysis budget, Retry-After honoring |
| Suitability | Live requests: YES (bounded queries). Scheduled ingestion: YES (planned monthly paged extraction; blob snapshot channel for reproducibility). Reference-only: no. NOT suitable for lot-level zoning determination (official use limitation above) |

## 3. NYC Zoning Tax Lot Database (ZTLDB) — SODA `fdkv-4t4z` (implemented connector)

| Field | Record |
|---|---|
| Official source | NYC DCP, Zoning Tax Lot Database, NYC Open Data dataset `fdkv-4t4z` |
| Endpoint URLs | Data: `https://data.cityofnewyork.us/resource/fdkv-4t4z.json` — Metadata/schema: `https://data.cityofnewyork.us/api/views/fdkv-4t4z.json` |
| Access mode | API (live request), per-BBL bounded queries + bounded deterministic multi-page scan (`scan_rows`); full 857k-row sync is a future Render-worker task |
| Authentication | None required; optional Socrata app token (platform baseline) |
| Published quota / rate limits | None published numerically — Socrata platform baseline applies (verified 2026-07-16) |
| Retrieval / refresh cadence | Source: stated Monthly (dataset description + custom fields, Automation Yes). **Observed violation:** `rowsUpdatedAt` stuck at 2026-04-05T18:46:56Z on 2026-07-16 AND still on 2026-07-20 (~3.5 months; two monthly boundaries missed; draft OQ-3 — escalation to DCPOpendata@planning.nyc.gov warranted; recorded as observation, not contract) |
| Source freshness signal | Socrata `rowsUpdatedAt` only (no version column, no per-record version field). Connector freshness guard: threshold 45 days, emits `source_stale_suspected=true` (fires on every live fetch while the stall persists); dataset_version label `socrata-rows-<rowsUpdatedAt RFC3339>` |
| Schema / file version | 16-column inventory pinned from the api/views columns array (fixture ZT08) and matching the official data dictionary (s-media, all 11 pages read 2026-07-16); per-run drift check |
| Terms / attribution links | DCP informational-purposes-only disclaimer (data dictionary verbatim); NYC Open Data terms as verified at M1-T001 |
| Last policy verification | 2026-07-16 (dictionary + Socrata metadata); staleness re-confirmed 2026-07-20 (M2-T008 capture). Re-verify at this task's G1 (TC-S6) |
| Outage / last-known-good behavior | Implemented (M2-T008 `ResilientZtldbFetcher`): typed taxonomy (incl. no_record as a RESULT, not an error), breaker/cache/LKG/budget, Retry-After honoring, transport staleness stamped separately from source staleness (two-staleness rule); split-lot ordering, slash-tie special districts, PARK caveat, four presence states preserved |
| Suitability | Live requests: YES (per-BBL; currently serves data that is officially stale-suspected — surfaced, never hidden). Scheduled ingestion: future monthly paged sync (bulk BYTES CSV channel is currently NEWER than the SODA rows — dictionary source dates June 2026). Reference-only: no |

## 4. MapPLUTO — tax-lot geometry (implemented connector on ArcGIS; bulk channel planned)

| Field | Record |
|---|---|
| Official source | NYC DCP, MapPLUTO. Two channels: (a) official DCP_GIS ArcGIS feature service `MAPPLUTO/FeatureServer` layer 0; (b) DCP bulk GIS release (shoreline-clipped FileGDB + shapefiles) via BYTES of the BIG APPLE |
| Endpoint URLs | ArcGIS: `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer` — Bulk: `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` (exact zip URLs unverified: nyc.gov returns HTTP 403 to non-browser clients, confirmed twice — **to verify at G1 / browser session**; never guessed). NYC Open Data `f888-ni5f` is a catalog HREF POINTER only, not a data channel |
| Access mode | API (live request) for per-lot geometry (ArcGIS); bulk file download (FileGDB) for the future citywide import |
| Authentication | None (keyless public feature service; verified at connector build 2026-07-20). Bulk page is bot-walled (403) — human browser session required to enumerate download URLs |
| Published quota / rate limits | None published. `maxRecordCount` 2000 published in service metadata bounds every response and rules the ArcGIS channel out as citywide-import primary (~860k lots) |
| Retrieval / refresh cadence | Source: PLUTO release model (major quarterly, minor monthly zoning attributes). Platform: on-demand per-BBL geometry queries; citywide import deferred (blockers B-001/B-002) |
| Source freshness signal | Per-feature `Version` attribute (26v1 observed on every live-captured feature 2026-07-20) + `editingInfo.dataLastEditDate` (2026-05-27T14:36:18Z observed, consistent with 26v1). Portal entry f888-ni5f carries STALE 22v3 attachments and frozen 2013 timestamps — never used for freshness |
| Schema / file version | 103 PascalCase fields pinned in fixture MPG01_meta.json (live 2026-07-20); connector contracts a bounded outFields subset; CRS wkid 102718 / latestWkid 2263 validated before coordinate math; bulk FileGDB internal schema inspection at first import (**to verify at G1 of the import task**) |
| Terms / attribution links | DCP informational-purposes-only disclaimer (README 26v1 / meta_mappluto.pdf). Official ± 20 ft horizontal-accuracy statement for the DCP production chain — spatial conclusions near boundaries typed `boundary_uncertain`. Not a legal boundary survey |
| Last policy verification | 2026-07-16 (M1-T001 G1, meta_mappluto.pdf); live service re-verified 2026-07-20 (M2-T009 capture). Re-verify at this task's G1 (TC-S6) |
| Outage / last-known-good behavior | Implemented (M2-T009 resilient client): typed outcomes for zero/one/multiple features (multiple = review-required), `wrong_crs` gate, geometry-validity taxonomy with no-silent-repair (original + normalized digests kept separately, repair method + shapely/GEOS versions recorded), breaker/cache/LKG/budget, Retry-After honoring |
| Suitability | Live requests: YES (per-lot geometry). Scheduled ingestion: bulk FileGDB on a Render worker is the citywide-import primary (future task; low-storage policy — never on the owner PC). Reference-only: no |

## 5. Geoclient v2 — address/BBL/BIN resolution (researched; credential required; no connector yet)

| Field | Record |
|---|---|
| Official source | NYC Office of Technology and Innovation (OTI), Geoclient v2, backed by DCP Geosupport |
| Endpoint URLs | Base: `https://api.nyc.gov/geoclient/v2` (address, address point, bbl, bin, blockface, intersection, place, search, streetcode, normalize, version endpoints per User Guide v2.0.4) |
| Access mode | API (live request) |
| Authentication | REQUIRED: free subscription key from the NYC API Developers Portal (`https://api-portal.nyc.gov/`, product "Geoclient User", subscription "Geoclient - v2"; v1 deprecated), sent as `Ocp-Apim-Subscription-Key` header. Key acquisition is a HUMAN action (owner account); recorded in HUMAN_ACTIONS |
| Published quota / rate limits | **None published on any unauthenticated page** (verified 2026-07-14, M0-T002). Azure APIM products typically display quotas after sign-in — record the actual quota when the key is obtained (**to verify at credential acquisition / G1**). A third-party figure (2,500/min, 500k/day) exists but is UNVERIFIED and must not be relied on |
| Retrieval / refresh cadence | Source: Geosupport release cadence (versioned releases, e.g. 26A/26B); `/v2/version` reports the loaded Geosupport release — use in health checks. Platform: live per-analysis resolution calls |
| Source freshness signal | `/v2/version` endpoint (Geosupport release + PAD version). Known skew class: PLUTO 26v1 built on Geosupport 26A while 26B is current (recorded at M1-T001) |
| Schema / file version | Documented response examples captured in M0-T002; full field-by-field fixture capture requires a live keyed call (**to verify at connector build G1**); no zoning-district designation field appears in documented examples (only `dcpZoningMap` sheet number) |
| Terms / attribution links | Public endpoint "freely available to the public on the NYC API Developers Portal" (User Guide section 7). Portal terms shown at sign-up (**record at credential acquisition**) |
| Last policy verification | 2026-07-14 (M0-T002). Re-verify at credential acquisition and connector G1 |
| Outage / last-known-good behavior | PLANNED: same shared-transport resilience pattern (typed errors, bounded retry, breaker, budget); Azure APIM 401 body shape unknown until a keyed call (fixture F14 planned). Fallback source: GeoSearch (`https://geosearch.planninglabs.nyc/v2/`, keyless, rate limits none published, autocomplete-grade) and DCP Geoservice (registration required — **to verify**) |
| Suitability | Live requests: YES (primary address resolution once the key exists). Scheduled ingestion: no. Reference-only: until the subscription key is obtained, this source is reference-only — a blocker exists for the human credential step |

## 6. DOB NOW — Open Data SODA family (researched M1-T007; connectors planned)

All family members share the Socrata platform baseline (auth optional, no numeric published quota, 429
throttle signal, SODA 2.1 paging: `$limit` default 1,000, no maximum on 2.1, stable paging requires
`$order` — dev.socrata.com/docs/queries/limit.html, retrieved 2026-07-17). All verified live 2026-07-17;
policy re-verification due at each connector's G1.

| Dataset | ID | Stated cadence | Freshness signal (observed 2026-07-17) | Suitability |
|---|---|---|---|---|
| Job Application Filings | `w9ak-ipjd` | Daily | rowsUpdatedAt 2026-07-16T20:23:19Z — consistent | Live per-BIN/BBL requests + scheduled ingestion (Stage A) |
| Approved Permits | `rbx6-tga4` | Daily | rowsUpdatedAt 2026-07-16T18:42:18Z | Live + scheduled (Stage A; join-key pollution guard mandatory) |
| Certificate of Occupancy | `pkdm-hqz6` | Daily | rowsUpdatedAt 2026-07-16T20:01:40Z | Live + scheduled (COs since ~March 2021 only) |
| Safety — Facades | `xubg-57si` | Every weekday | rowsUpdatedAt 2026-07-16T17:31:05Z | Scheduled; BIN-only (no BBL column) |
| Safety Boiler | `52dp-yji6` | Daily | rowsUpdatedAt 2026-07-16T19:59:02Z | Scheduled; BIN-only, number-typed |
| Elevator Safety Compliance | `e5aq-a4j2` | Daily | rowsUpdatedAt 2026-07-16T20:32:59Z | Scheduled |
| Build — LAA | `xxbr-ypig` | Daily | rowsUpdatedAt 2026-07-16T18:35:04Z | Secondary (low feasibility signal) |
| Electrical Permits (+child `xmmq-y7za`) | `dm9a-ab7w` | Daily | rowsUpdatedAt 2026-07-16T21:48:38Z | Secondary |
| Elevator Permits (+child `juyv-2jek`) | `kfp4-dz4h` | Daily | rowsUpdatedAt 2026-07-16T16:32:00Z | Secondary |

Shared record fields: endpoints `https://data.cityofnewyork.us/resource/<id>.json` +
`https://data.cityofnewyork.us/api/views/<id>.json`; access mode API (live request) and scheduled
ingestion; terms = NYC Open Data terms, provenance flag `official`; official data-dictionary XLSX
attachments identified per dataset (assetIds in the draft; extraction deferred to a cloud environment —
authorized document download, OQ-2); outage/LKG behavior = shared transport engine + per-connector typed
taxonomy at connector build. Family boundary: DOB NOW channel EXCLUDES all BIS-channel jobs — a complete
DOB history requires the legacy family below (two-channel model proven on BIN 1006014).

## 7. DOB legacy / BIS family — Open Data SODA (researched M1-T008; connectors planned)

Verified live 2026-07-17 (~60+ tokenless requests, no 401/403/429 observed; one HTTP 500 `internal-error`
on a valid cast aggregation against `ic3t-wcy2` — 5xx must be classified separately from the 400 drift
signature). Socrata platform baseline applies. Policy re-verification due at each connector's G1.

| Dataset | ID | Coverage (evidence-bounded) | Suitability |
|---|---|---|---|
| DOB Permit Issuance | `ipu4-2q9a` | 1989-05-11 → present (committed cast probe) | Stage A: live + scheduled |
| DOB Job Application Filings | `ic3t-wcy2` | actions since 2000-01-01 (official statement) | Stage A: live + scheduled; BBL column 32.6% BIN-polluted — BIN-primary joins, BBL format+borocode validation mandatory |
| DOB Certificate Of Occupancy | `bs8b-p36w` | COs 2012-07-12 → March 2021 (official window; future-dated garbage observed: max 2105-11-05) | Stage A: scheduled; pre-2012-07 COs exist only as scanned images (no dataset) |
| DOB Violations | `3h2n-5cm9` | ~1901(mis-key suspect) → 2026 (range-filtered probe) | Scheduled (M2 risk facts); BIN+boro/block/lot keys, no BBL column |
| ECB/OATH Violations | `6bgk-3dad` | joined via `ecb_number` | Scheduled (M2 risk facts) |
| DOB Complaints Received | `eabe-havv` | 1988-12-30 → present (committed cast probe); daily full-snapshot replacement semantics (single `dobrundate`) | Scheduled; BIN-only property keys; change tracking by our ingestion diffing |
| Historical Permit Issuance | `bty7-2jhb` | 1989–2013, frozen 2018, officially redundant | NEVER CONNECT (reconciliation cross-check candidate only) |
| Property master | `e98g-f8hy` | empty / "being replaced"; no Open Data successor | NEVER CONNECT |
| Others examined | `bf97-mjsy`, `g76y-dcqj`, `855j-jady`, rejected candidates | see docs/research/dob-legacy-sources.md sections 3.3/8 | per-source disposition recorded there |

## 8. NYC Zoning Resolution — official text portal (researched M1-T004; ingestion planned for M3)

| Field | Record |
|---|---|
| Official source | NYC DCP, Zoning Resolution text portal `https://zoningresolution.planning.nyc.gov/` (alias host `zr.planning.nyc.gov`; each host self-canonical — hostname is connector config) |
| Endpoint URLs | HTML tree: `/article-{roman}/chapter-{n}/{section}`; amendment feed `/recently-adopted` (31 pages); dated complete-PDF snapshots `/zr-downloads`; per-article/per-chapter PDFs under `/sites/default/files/article/...`. **API surface verified ABSENT** (2026-07-16): /jsonapi 404, ?_format=json 406, no Open Data dataset of the text |
| Access mode | HTML corpus ingestion (PRD section-8 tier 4) + bulk file download (dated PDF snapshots). The undocumented per-section entity-print PDF route and the amendment-history AJAX endpoint are OPTIONAL monitored enrichment only (owner directive 2026-07-16) — never the sole truth channel |
| Authentication | None (all pages fetched anonymously 2026-07-16; no 403 on this host, unlike www.nyc.gov) |
| Published quota / rate limits | None published. Observed: Drupal 9 on Pantheon behind Fastly/Varnish; 504 on on-the-fly PDF of the oversized 12-10 node — crawlers must be low-rate and resumable (observation, not a contract) |
| Retrieval / refresh cadence | Source: event-driven per adopted text amendment (no schedule); homepage currency banner ("All text changes approved by the city council as of <date>"); snapshot PDFs at an irregular 3-6 month cadence. Platform: re-crawl triggered by banner-date change or new /recently-adopted entry (plan) |
| Source freshness signal | Homepage banner date (2026-05-20 at research time) + per-section machine-readable `Last Amended` timestamps + newest dated snapshot (AllArticles_23Jun2026) |
| Schema / file version | Not a dataset: structured legal-text corpus (Articles I-XIV, chapters, sections with #CC-NN anchors, 12-10 definitions with per-definition dates, cross-reference hrefs). Banner date is the legal-currency version label; PDF file dates are generation timestamps |
| Terms / attribution links | Official disclaimer (/disclaimer, verbatim captured): distributed "WITHOUT WARRANTIES OF ANY KIND"; changes "MAY OR MAY NOT BE IMMEDIATELY REFLECTED"; DCP may revise the disclaimer at any time. **No official statement that the portal text is the legally authoritative version** (OQ-11 — requires qualified-human review before any `verified` labeling policy relies on it). robots.txt has no content-path disallows |
| Last policy verification | 2026-07-16 (M1-T004 + G1 corrections). Re-verify at M3 ingestion G1 |
| Outage / last-known-good behavior | PLANNED (M3): crawler on Render worker, raw HTML per section to Supabase Storage with retrieval timestamp + banner date + Last Amended stamps; snapshot archiver for dated PDFs; per-release HTML-vs-PDF sampling cross-check. Fallbacks: same-publisher PDF channels; council.nyc.gov / Legistar for amendment-adoption records (verified automation-accessible) |
| Suitability | Live requests: no (corpus, not a query API). Scheduled ingestion: YES (M3). Reference-only until M3 lands |

---

## Cross-source access notes

- **nyc.gov bot wall:** `www.nyc.gov` / `www1.nyc.gov` return HTTP 403 to non-browser clients (confirmed
  repeatedly across tasks). Every bulk-download URL behind that wall is recorded as **to verify at G1 via a
  human browser session** — never guessed, never scraped through evasion.
- **Retry-After and 429 handling** are implemented once in `services/api/app/resilience/transport.py`
  (task M2-T011) and consumed by all connectors; the official grounding is the Socrata 429 statement plus
  RFC 9110 section 10.2.3 generic semantics (header optional, honored exactly when parseable, over-cap
  honored by not retrying).
- **Escalation ledger:** ZTLDB monthly-update stall (section 3) is the only currently observed
  source-cadence violation; owner-visible via the connector's `source_stale_suspected` flag on every fetch.
- **Registry maintenance:** rows change only with cited evidence (a dated official page read, a captured
  fixture, or an accepted research doc). The G1 reviewer for M2-T011 (TC-S6) independently spot-verifies
  quota/terms/attribution links and the last-policy-verification dates against the live official pages.
