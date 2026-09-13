# G1 GATE REPORT — M4-T013

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent data-contract-verifier agent.

**Task:** M4-T013 — D-045 B2 research: street-width / mapped-street official-source research
**Reviewed SHA:** 05b5721f (material commit); HEAD advanced with control-plane records only — verified.
**Reviewer:** independent G1 (read-only). Producer: official-source-researcher.
**Task type:** RESEARCH + registry-draft only (no connector code).

## VERDICT: **PASS** (2 advisory corrections, 0 blocking)

Every load-bearing claim the future B2 connector packet will stand on reproduced against the live official source, in several cases byte-exact. The single most important honesty claim — that the DCM `Streetwidth` field carries **no field-level definition** in the official metadata, so the mapped-width interpretation is held as an open question rather than asserted — is confirmed true against the live metadata PDF. No ambiguity is resolved by assumption. Prohibition rows respected. Scope is clean.

---

## What I verified LIVE (vs. accepted from report)

### S1 — Authoritative source identified — VERIFIED LIVE
**ArcGIS layer** `DCM_Street_Center_Line/FeatureServer/0` (services5.arcgis.com/GfwWNkhOj9bNBqoJ), fetched `?f=json` today. Byte-match to report/registry E5:
- name `DCM_Street_Center_Line`; geometryType `esriGeometryPolyline`; wkid **102718 / latestWkid 2263**; maxRecordCount **2000**; currentVersion **12**; capabilities `Query,Extract`; formats `JSON, geoJSON, PBF`; supportsPagination **true**; `dataLastEditDate` **1764617995374** (identical to the value in the report/draft = 2025-12-01Z).
- `Streetwidth` = `esriFieldTypeString`, length **50** ✓. Mapped-street-status fields `Feat_Type` and `Feat_status` present ✓.
- **Keyless** confirmed — anonymous fetch succeeded.

**SODA `g6zj-tzgn`**, fetched `api/views` today. Byte-match to report E1:
- id `g6zj-tzgn`, name `DCM_StreetCenterLine`, attribution DCP, category City Government.
- `rowsUpdatedAt` **1714764762** (2024-05-03), `viewLastModified` **1730492547** (2024-11-01), `createdAt` 2020-05-29, `publicationDate` 2023-09-28 — all match. Custom **Update Frequency = "Monthly"** ✓. Columns `streetwidt/feat_type/feat_statu` present ✓.
- **Staleness claim holds**: rows ~2024-05 + view ~2024-11 against a "Monthly" label = ~16 months stale as of 2026-09, while ArcGIS shows a 2025-12 edit. Correctly characterized as fallback.

*Accepted from report (not independently re-fetched):* the arcgis.com `owner:DCP_GIS` search (E4). Corroborated indirectly — the service lives on the same `services5.arcgis.com/GfwWNkhOj9bNBqoJ` org that hosts the DCP_GIS-owned MapPLUTO layer already verified in `pluto-mappluto.json`. Not a defect.

### S2 — Width semantics pinned — VERIFIED LIVE, including the honesty crux
I byte-read the official DCM metadata PDF (`s-media.nyc.gov/.../dcm_street_centerline.pdf`) via the PDF reader:
- Summary verbatim: *"Citywide street center-line features representing official street names and widths shown on the Official City Map of New York City. Dataset last updated: October 31, 2025."* — exact.
- Use limitations verbatim: *"Digital City Map (DCM) data changes often and is updated monthly… for informational purposes only. DCP does not warranty the completeness, accuracy, content, or fitness…"* — exact.
- Spatial Reference WKID 102718 / LatestWKID 2263, NAD_1983_StatePlane_New_York_Long_Island_FIPS_3104_Feet — exact. Object count **53986**; Publication 2025-10-31 — exact.
- **`Field Streetwidt`: the metadata lists ONLY Alias / Data type String / Width 50 / Precision / Scale — NO "Field description", NO "Description source", NO "List of values".** This directly confirms the report's central S2 honesty claim. By contrast `Feat_Type`, `Route_Type`, `Record_ST`, `Paper_ST` etc. all DO carry full field descriptions (also byte-matching the registry's byte-verified block).

**Free-text width domain** — I re-ran the grouped-count query live. Top-of-distribution matched exactly: `60`=19074, `80`=8658, `n/a`=2954, `Unknown`=1404, `>80`=368, `>75`=364, `Width Irregular`=45, `~60`=62, `~80`=40, `75`=470. The report's low-frequency classes (ranges `60-75`=18, `74-75.3`=1) fall below my top-40 window; not contradicted, and non-load-bearing since the free-text/straddling-75 finding is already proven by the values I confirmed.

**Ambiguity handling:** OQ-1 (exact geometric width definition), OQ-3 (fail-closed policy per class) are genuinely left OPEN and explicitly routed to a rule/legal decision. The mapped-vs-paved distinction rests on (a) the "Official City Map" framing (byte-verified) + (b) empirical divergence — stated honestly, not asserted as a field definition. **No ambiguity resolved by assumption.**

### S3 — Capture procedure — RE-RUNNABLE (I executed the SODA URLs myself)
The SODA metadata, sample, W-100-St, and grouped-domain queries in §6/Evidence index all executed successfully as written. ArcGIS query template is standard REST with correct paging (`orderByFields=OBJECTID ASC` + `resultOffset`, `exceededTransferLimit`), correct two-CRS discipline (measure in 2263, `f=geojson&outSR=4326` display-only), sha256+timestamp recording. Keyless posture stated; nothing routed to owner. Thin-client sized (KB-scale, maxRecordCount 2000 rules out bulk).

### S4 — Geoclient comparison — HONEST, kill justified
Confirmed the in-repo fixture `G01_address_documented_example.json` (314 W 100 St, BBL 1018887502): `streetStatus":"2"`, **`streetWidth":"30"`, `streetWidthMaximum":"30"`** — exact. Confirmed live DCM W 100 St Manhattan = two Mapped_St/City_St segments at `60` and `100`. The 30-vs-60 divergence is real and reproduces the pilot. Kill-for-legal-use verdict (paved/roadbed ≠ mapped, point ≠ geometry, systematic under-report near 75 ft) is justified by the cited evidence; advisory cross-check role preserved, not discarded. Comparison table states tradeoffs on authority/granularity/semantics/failure modes rather than hiding them.

### S5 — Registry draft posture — MATCHES M2-T009
`dcm-street-centerline.json` (two records: arcgis primary + soda fallback) mirrors the key structure of `pluto-mappluto.json` (source_id, agency, official_url, api_dataset_identifier, authentication, rate_limits, update_frequency, geographic_coverage, fields_available, terms, connector=PLAN ONLY, known_limitations, fallback_source, open_questions). `draft_status` explicitly NON-FINAL on both records. No invented registry mechanism; consistent with the report.

### S6 — Research-only scope — CLEAN
`git show 05b5721f --stat` = 7 files, +471/-0: the research report, the registry draft, the evidence map, and four `.claude/agent-memory/` files only. No `services/api/**`, `apps/web/**`, `packages/**`, fixtures, deps, or schema. `git diff 05b5721f..HEAD --stat` = control-plane only (`reports/M4-T013.json`, `state.json`, `tasks/M4-T013.json`). Confirmed within `allowed_paths`.

### Prohibition rows
- **D-045-R009** (scope-limit / no promotion / no compliance language): PASS. No rule promoted; the fail-closed-to-narrow recommendation is explicitly routed to OQ-3 as a ZR-grounded rule/legal decision "needs G6-class review," not decided here. The cited ZR 12-10 snapshot is itself `extraction_status: extracted_draft`, `raw_html_verified: false`, needs-G6 — the report treats it as a snapshot, not a determination. No compliance declaration anywhere.
- **D-046-R002** (disjointness): PASS. This task's `allowed_paths` are `project-control/reports/M4-T013-street-width-research.md` + `docs/research/source-registry-drafts` — zero overlap with any rules dir.

---

## Advisory corrections (non-blocking)

1. **Sibling-task ID inconsistency in control records (orchestrator-authored, not the deliverable).** The task packet/progress wording references "parallel with M4-T012" (written before the wave re-point) while `M4-T013-evidence-map.json` (D-046-R001/R002 rows) says "in parallel with **M4-T014**." This does not affect M4-T013's own disjointness (its paths touch no rules dir), but the orchestrator should reconcile which sibling is meant before citing it as D-046 evidence.
   - ORCHESTRATOR RECONCILIATION (recorded at preservation time): the packet's inputs line was authored BEFORE B-023 re-pointed the rules lane from M4-T012 to M4-T014; the ACTUAL wave-1 partner is **M4-T014** (M4-T012 is blocked with a clean worktree and no live producer). The evidence map is correct; the ledger progress log now carries this reconciliation.

2. **ArcGIS field-count wording.** The registry note states "18 fields on layer 0"; the live layer exposes 17 named attribute fields + `Shape__Length` = 18 total (defensible, but the count silently includes the geometry-length field). Minor; consider clarifying "17 attributes + Shape__Length" at connector-build time. Also note the shapefile/PDF truncates the alias to `Streetwidt` while the live ArcGIS field is `Streetwidth` — already flagged by the report's cross-channel-divergence note.

## Not independently re-verified (report is honest about each)
E2 (LION "narrowest paved width" wording — report flags search-derived, OQ-7), E8 (Geosupport UPG appendix — report flags not byte-read), E4 (owner:DCP_GIS search — corroborated via shared org URL). None are load-bearing beyond what the report already marks open.

**Recommendation to orchestrator:** record **G1 PASS**. The two advisory items are non-blocking and may be carried as notes into the later B2 connector packet.
