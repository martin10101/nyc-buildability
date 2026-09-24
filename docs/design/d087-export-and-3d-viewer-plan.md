# D-087 export wiring and 3D viewer plan (M5-T099, PLAN-1)

Status: DESIGN NOTE. This document PROPOSES; it authorizes nothing. Every packet it lists is
contracted later by the orchestrator under the normal G0-G7 gates. It changes no code, no route, no
dependency. Task-id note: the packet labels below (`PKT-A` ...) are workstream labels only; the
orchestrator assigns ledger `M<x>-T<n>` ids when it contracts them (`.claude/rules/expansion-agent-dispatch-hold.md` §3).

Authority to build this family: owner directive **D-087** (§2.3 scoped release of the expansion hold
for 3D building-and-lot massing, CAD/DXF export, phase-C PDF blueprint read/write). Honesty vocabulary:
**D-083**. Every boundary in **D-087-R009** stands (gates, dependency security, Tier D, PR #241 never
merged, the unmounted max-envelope route, thin-client limits, D-051 fail-closed).

Line anchors below were read at worktree head `2957e40d` (the M5-T099 claim seam). The code graph is
advisory (D-066-R001); every consumer claim here was re-verified in source by grep, not the cached graph
(the graph fingerprint is stale against this reset worktree; see the producer report).

---

## 0. Current truth (what exists, what does not)

Seven D-087 building blocks are **accepted and UNWIRED**. Grep across `services/api` (producer report,
command 4) confirms every block is imported only by its own test, with ONE production import:
`services/api/app/cad/pdf_sheet_writer.py:54  from app.cad.dxf_writer import CLAIM_CLASS_WORDS`. No
block is reachable from `app/main.py`; no download or scene route exists.

Honest capability limits carried into every packet below:

- The architect-sheet PDF reader **reads 0 of 6 real architect drawings** (M5-T093 corpus trial: all
  six refuse at the cross-reference-stream stage before any page content; `docs/research/architect-corpus-reader-trial-2026-09.md`
  headline). Real-file reading is FUTURE work (PKT-K/C1). Nobody may tell the owner real architect PDFs
  can be read today.
- The `POST /api/v1/max-envelope` route **ships UNMOUNTED** (`services/api/app/api/v1/max_envelope_api.py:10`).
  Its mount preconditions (§7) are listed, never relaxed.
- The writers produce DXF/PDF/GLB **only inside tests**; there is no HTTP path to a download yet.

### 0.1 Packets already in flight (contracted, claimed at wave-4/5/6 seams; NOT yet accepted)

These lock specific files; every future packet in §5 that touches the same file is sequenced AFTER the
in-flight packet is accepted (D-087-R002 no-interference).

| In-flight | Scope | Files locked | Riders it closes |
|---|---|---|---|
| M5-T094 | Split the sheet reader before C1 growth (facade kept) | `app/drawings/sheet_reader.py`, `+sheet_objects.py`, `+sheet_interpreter.py`, `tests/drawings/test_sheet_reader_split_equivalence.py` | DB-055 (b),(m) |
| M5-T095 | Bound proposal.py all-pairs simplicity check + total-positions cap | `app/scenario/proposal.py`, `tests/scenario/test_proposal_validation_budget.py` | DB-061 (g) / F-HIGH-1 |
| M5-T096 | DXF STYLE/VPORT tables + stdlib allowlist test + owner-openable CAD samples & README | `app/cad/dxf_writer.py`, `tests/cad/test_dxf_writer.py`, `tests/cad/test_cad_owner_samples.py`, `docs/samples/cad/**` | DB-057 (a),(b),(f) |
| M5-T097 | dxf_reader hardening + committed writer->reader round trip | `app/drawings/dxf_reader.py`, `tests/drawings/test_dxf_reader.py`, `tests/drawings/test_dxf_roundtrip.py` | DB-057 (h),(i),(j),(l),(m),(n) |
| M5-T098 | massing_model before-wiring hardening (y-only, LOT 2263 range, GEOS wrap) | `app/scenario/massing_model.py`, `tests/scenario/test_massing_model.py` | DB-061 (a),(b),(c),(d),(f) |
| M5-T100 | footprint connector riders (logger, missing-geom test, wrong_crs, year 0) | `app/connectors/building_footprints_arcgis.py`, `tests/connectors/test_building_footprints_arcgis.py` | DB-058 (e),(h),(l),(m) |

`sheet_interpreter.py`, `sheet_objects.py`, `test_dxf_roundtrip.py` are 1-line placeholder seeds at
`2957e40d`; STYLE/VPORT is not yet in `dxf_writer.py`; `sheet_reader.py` is still 1096 SLOC monolithic
(near the 1000 hard cap — `modularity_check` flags it). These are the in-flight packets, not accepted
state.

---

## 1. Inventory of the accepted, unwired blocks (AS-1)

Every entry: public API (file:line, worktree `2957e40d`), the reviewed limits, and consumers.

### 1.1 `app/cad/dxf_writer.py` (787 SLOC) — AutoCAD-openable site plan + 3DFACE massing

- Entry: `build_site_plan_document(lot, building, floor_heights, *, base_elevation=0.0) -> DxfDocument`
  (`:665`); `render_site_plan_dxf(...) -> str` (`:775`); `serialize_document(doc) -> str` (`:573`).
  Byte-identical output for identical input (`:783`).
- Format: `$ACADVER = AC1009` (R12, simplest hand-writable target), `$INSUNITS = 21`
  (`INSUNITS_US_SURVEY_FEET = 21`, `:79`) per `docs/research/dxf-format-reference-2026-09.md` §0.
  Layers `LOT / BUILDING_OUTLINE / MASSING_3D / ANNOTATION` (`:97-114`).
- Honesty (already emitted): `PROPOSED_LABEL = "PROPOSED - NOT A CITY RECORD"` (`:117`),
  `GENERATOR_NOTE = "GENERATED BUILDING OPTION - ..."` (`:119`), `CRS_UNITS_NOTE` (`:118`), written on the
  ANNOTATION layer. Claim-word screen `CLAIM_CLASS_WORDS` (`:124`), `_assert_no_claim_words` (`:604`).
- Limits (fail-closed, checked before allocation, `:684-704`): `MAX_ENTITIES = 50_000` (`:144`),
  `MAX_RING_VERTICES = 10_000` (`:147`), `MAX_FLOORS = 2_000` (`:152`), `MAX_COORD_ABS = 1e8` (`:159`).
  Typed `DxfValidationError(code, message, field)` (`:184`), `DxfSanitizationError` (`:196`);
  `_sanitize_value` (`:229`) strips control chars from group values.
- Consumers: `app/cad/pdf_sheet_writer.py:54` imports `CLAIM_CLASS_WORDS`. No route. Test:
  `tests/cad/test_dxf_writer.py`.

### 1.2 `app/cad/glb_writer.py` (597 SLOC) — zero-dependency glTF 2.0 binary

- Entry: `write_glb(meshes: Sequence[GlbMesh], frame: GlbLocalFrame) -> bytes` (`:578`). Inputs
  `GlbMesh(name, positions, indices, base_color)` (`:240`), `GlbLocalFrame(origin_easting_ft,
  origin_northing_ft, origin_elevation_ft)` (`:226`).
- CRS: `SOURCE_CRS = "EPSG:2263"`, `SOURCE_UNIT = "US survey foot"` (`:128-129`);
  `US_SURVEY_FOOT_TO_METRE = 1200/3937` exactly (`:131`, NOT 0.3048); declared `AXIS_MAPPING`
  `{gltfX:+east, gltfY:+up, gltfZ:-north}` (`:135`). Media type `model/gltf-binary` (`:115`).
- Honesty: `PROPOSED_LABEL = "Proposed - not a city record"` (`:141`), `GENERATOR` (`:142`);
  `CLAIM_CLASS_WORDS` (`:146`) barred from caller mesh names.
- Limits: `MAX_MESHES = 1_000` (`:164`), `MAX_TOTAL_VERTICES = 500_000` (`:166`),
  `MAX_TOTAL_INDICES = 1_500_000` (`:168`), `MAX_LOCAL_COORD_ABS_FT = 100_000` (`:170`),
  `MESH_NAME_MAX = 64` (`:176`); output capped at the uint32 bound (`:595`). Typed
  `GlbValidationError(code, message, field)` (`:212`); `REFUSAL_CODES` frozenset (`:181`). NOTE: this
  writer RAISES on invalid input (contrast the PDF writer, which returns a refusal VALUE) — reconcile at
  the consumer (DB-059 (e)).
- Consumers: none in production. Test: `tests/cad/test_glb_writer.py`.

### 1.3 `app/cad/pdf_sheet_writer.py` (506 SLOC) — deterministic PDF 1.4 site plan

- Entry: `render_site_plan_pdf(spec: SitePlanInput) -> bytes | SitePlanRefusal` (`:160`, never raises).
  `SitePlanInput(lot_ring, building_ring, address, bbl, generated_at, generator_version)` (`:109`) —
  `generated_at`/`generator_version` are caller-supplied provenance strings, never a clock (`:114-116`).
  `SitePlanRefusal(reject_code, detail)` (`:127`) with `to_payload()` (`:134`).
- Scale: `choose_scale(width_ft, height_ft) -> float | None` (`:146`) picks the tightest standard scale.
- Security surface: `_screen_caller_text` (`:224`) + `_claim_key`/`_CLAIM_SEPARATOR_RUN` (`:221,252`)
  screen claim words; `_escape_pdf_text` (`:424`) / `_ascii_sanitise` (`:442`) escape strings.
- Limits: `_MAX_RING_VERTICES = 1024` (`:87`, tighter than the DXF writer), `_MAX_COORD_ABS = 1e8` (`:90`).
- KNOWN RIDERS (DB-053): `_validate_ring` (`:260`) and `_num` (`:447`) can RAISE on a malformed vertex /
  non-finite input (docstring promises never-raises); no claim-word screen on the caller title-block
  address/bbl; escaper fixture covers only balanced parens. Close in PKT-B1 before wiring untrusted text.
- Consumers: none in production. Test: `tests/cad/test_pdf_sheet_writer.py`.

### 1.4 `app/drawings/dxf_reader.py` (641 SLOC) — strict-subset DXF reader

- Entry: `read_dxf(data: bytes | str, *, limits=DEFAULT_LIMITS) -> DxfReadResult` (`:622`, never raises;
  every failure is a typed `DxfRefusal` VALUE, `:257`). Success: `DxfDocument(ok, units, acad_version,
  primitives, disclosed_unknown, skipped_sections, entity_count)` (`:237`). Primitives: `LinePrimitive`
  (`:193`), `PolylinePrimitive` (`:203`), `FacePrimitive` (`:217`), `TextPrimitive` (`:226`).
  `DxfReadResult = DxfDocument | DxfRefusal` (`:268`).
- Units are REPORTED, never assumed: `DxfUnits(code, name, source)` (`:182`).
- Limits: `DxfLimits(max_bytes=8MiB, max_lines=2_000_000, max_line_chars=4096, max_entities=200_000,
  max_vertices=100_000)` (`:156-170`); injectable for tests, production uses `DEFAULT_LIMITS` (`:178`).
- KNOWN RIDERS (DB-057, closing in in-flight M5-T097): `_to_pairs` splits on `str.splitlines()`
  (over-splits); `max_lines` enforced only after full materialization; `DxfLimits` has no upper clamp;
  the str branch skips binary/non-ASCII checks; missing `$INSUNITS` 22/23/24.
- Consumers: none in production. Tests: `tests/drawings/test_dxf_reader.py`, `test_dxf_roundtrip.py`
  (placeholder at `2957e40d`).

### 1.5 `app/drawings/sheet_reader.py` (1096 SLOC) — architect-sheet vector PDF reader

- Entry: `read_sheet(data: bytes|bytearray|memoryview, *, flatten_tolerance=DEFAULT) -> SheetDocument |
  SheetRefusal` (`:333`, never raises; all-or-nothing per document). `flatten_tolerance` is the DECLARED
  max chord error recorded on every page.
- Reuses `read_object_table` from the accepted survey PDF pipeline (a SECOND consumer — must NOT be
  widened by C1; DB-055 (k)).
- LIMIT (blocking, real): refuses PDF 1.5+ **cross-reference streams / object streams**, so it reads
  0/6 real architect drawings (M5-T093). Modularity: 1096 SLOC over the JUSTIFY band — the split
  (M5-T094) must land before any C1 growth (DB-055 (b)).
- Consumers: none in production. Tests: `tests/drawings/test_sheet_reader.py`, `_split_equivalence.py`
  (placeholder).

### 1.6 `app/scenario/massing_model.py` (825 SLOC) — versioned massing truth object

- Entry: `build_massing_model(*, lot_ring, proposed_massing, source=SOURCE_PROPOSED, scenario_id,
  property_geometry_version_id, rule_release_id) -> MassingModel` (`:654`); `build_from_generated_option(*,
  lot_ring, max_envelope, ...) -> MassingModel` (`:770`) — refuses (never fabricates) when the engine
  emits no candidate (`:788-794`).
- Output: `MassingModel` (`:449`) with `as_dict()` (`:464`), `to_json()` (deterministic, no NaN, `:481`),
  `content_hash()` (sha256 golden, `:487`). Honest `source` label ∈ {`proposed`, `generated_option`}
  (`:667`). CRS frame `_crs_frame` (`:635`): canonical world 2263, `world_to_local = subtract_local_origin`.
- Fail-closed: B0 validation via `validate_proposed_massing` (`:676`); every floor footprint contained
  within the lot + `FOOTPRINT_OUTSIDE_LOT_TOL_FT`, refused never clipped (`:694-706`); typed
  `MassingModelError(reason, field)` (`:134`).
- KNOWN RIDERS: pre-wiring hardening in in-flight M5-T098 (DB-061 a/b/c/d/f); wiring riders (vertical
  unit explicit, coincident interface caps, party-wall, string coords) DB-054 (k)-(o).
- Consumers: none in production. Test: `tests/scenario/test_massing_model.py`.

### 1.7 `app/connectors/building_footprints_arcgis.py` (1075 SLOC) — OTI footprint + height connector

- Entry: `fetch_context_buildings(*, envelope=None, polygon=None, site_ground_elevation_ft=None,
  subject_bbl=None, page_size=None, transport=urllib_transport, timeout=30.0, max_attempts=3, ...,
  correlation_id=None, budget=None) -> ContextBuildingsResult` (`:1017`, never raises; input validated
  before any I/O; metadata validated before any page). Channel: OTI ArcGIS `BUILDING_view/FeatureServer/0`,
  geometry pre-reprojected to EPSG:2263 via `outSR` (`docs/research/building-footprints-source-2026-09.md` §0).
- Types: `ContextBuilding` (`:279`), `FootprintRefusal(error_type, message, correlation_id, detail,
  request_url, retrieved_at, raw_digest)` (`:318`), `ContextBuildingsResult(status ok|refused, ...)`
  (`:331`) with the provenance quintuple `provenance()` (`:357`). Typed errors: `SchemaDriftError`
  (`:226`), `WrongCRSError` (`:232`), `RateLimitedError`, `SourceTimeoutError`, `PagingPathologyError`.
- Geometry: `parse_footprint_geometry` (`:747`), `classify_query_relation` (`:797`). Height/base:
  `base_z = GROUND_ELEVATION` (NAVD88 ft), `roof_z = GROUND_ELEVATION + HEIGHT_ROOF`
  (research §0). `HEIGHT_ROOF` feet is an INFERENCE (no per-field unit tag).
- KNOWN RIDERS: M5-T100 (in flight) closes (e),(h),(l),(m); wiring riders DB-058 (a)-(d),(f),(g)
  (escape-on-render, vertex/byte caps, deadline, datum choice, source_registry).
- Consumers: none in production. Test: `tests/connectors/test_building_footprints_arcgis.py`.

---

## 2. The export API contract (AS-2)

A single flag-gated export surface turns a stored/derived massing (proposed or generated option) into a
downloadable DXF, PDF site plan, or GLB, via the accepted writers. Built in two layers: a pure
**export service** module (no route) + an **UNMOUNTED** route module, mirroring the accepted
`max_envelope_api` / M5-T059 pattern (router asserted ABSENT from OpenAPI until a later mount seam).

- **Flag-gating.** Reuse `INTERNAL_RULE_EVAL_ENABLED` (the class the sibling internal routes use);
  `include_in_schema=False`; absent/empty/unknown flag -> a generic `404` byte-indistinguishable from an
  unmounted path (the accepted sentinel; `app/api/v1/lot_geometry.py:100`). A caller-supplied-geometry
  WRITE/import path additionally needs a dedicated default-off flag (mirror
  `app/main.py:203-218` site-definition: registration flag AND handler flag).
- **Request bounds.** Bounded-streaming raw-byte ceiling (reuse the accepted T053 primitives). `format`
  enum ∈ {`dxf`,`pdf`,`glb`}. Geometry is validated against the writer whose caps are tightest for that
  format (PDF ring 1024 < DXF 10_000; the service refuses over the applicable cap, never silently
  truncates). Floors ≤ 2000. Every caller text field (address, bbl, generator_version) is length-capped
  BEFORE it reaches a writer (DB-059 (a); DB-053 (c) title-block screen). The writer-side DB-059 (a) fix
  itself lands in PKT-B1; this service cap is defense in depth [ORCH-CORRECTED per M5-T099 G3 advisory 2].
- **Response types + Content-Disposition.** DXF: `Content-Type: image/vnd.dxf`,
  `Content-Disposition: attachment; filename="site-plan-<token>.dxf"`, body = ASCII DXF text.
  PDF: `application/pdf`, attachment `.pdf`. GLB: `model/gltf-binary` (`glb_writer.GLB_MEDIA_TYPE`),
  attachment `.glb`. Every non-disabled response carries a server-generated `X-Correlation-ID`.
- **Filename safety — MANDATORY PKT-D acceptance criterion [ORCH-CORRECTED per M5-T099 G5 F1].** `<token>`
  is built SERVER-SIDE from an allowlist: only `[A-Za-z0-9._-]` survives (every CR/LF, quote, `;` and any
  other character is dropped), length-capped, derived from the validated bbl and the deterministic
  `generated_at`. Raw caller text NEVER reaches a response-header value. Any non-ASCII rendering uses the
  RFC 6266 / RFC 5987 `filename*=UTF-8''…` form alongside the ASCII `filename`. A test proves that a
  caller value carrying `"`, `;`, CR/LF or non-ASCII cannot break, split or spoof the header.
- **Typed refusals.** One uniform refusal JSON `{reject_code, detail}` at the service boundary that
  surfaces each writer's own code: DXF `DxfValidationError.code`, PDF `SitePlanRefusal.reject_code`, GLB
  `REFUSAL_CODES`. The service RECONCILES the GLB writer (raises) against the PDF writer (returns a value)
  into one typed refusal (DB-059 (e)); it must catch `GlbValidationError`/`DxfValidationError` and NOT
  echo the caller-supplied name/text in the refusal (DB-059 (h) redact; GLB errors echo the name today).
- **Provenance.** Each file carries the accepted embedded provenance (DXF ANNOTATION layer; PDF title
  block; GLB `asset.generator`). The service records source scenario id,
  `property_geometry_version_id`, `rule_release_id`, and the caller `generated_at` (deterministic, never a
  clock).
- **Honesty labels (D-083).** `source` ∈ {`proposed` -> "Proposed - not a city record",
  `generated_option` -> "Generated building option"}. NEVER "approved" / "permitted" / "maximum allowed
  building" / "demonstrated maximum". The shared claim-word screen (PKT-A) bars those words in any
  caller-supplied name or title-block string, using a separator-collapsing key so `As_of_right` /
  `Maximum_allowed` cannot slip through (DB-059 (b)).
- **Time & size budgets.** A per-request wall-clock deadline, enforced by running the writer OFF the event
  loop in a cancellable job, plus a per-caller RATE LIMIT at the route — DB-061 (i), the M5-T088 G5 fix (b),
  still REQUIRED even with the in-process bounds [ORCH-CORRECTED per M5-T099 G3 B1]; output caps enforced by the writers
  (DXF `MAX_ENTITIES` 50_000; GLB 500_000 verts / 1_500_000 indices / uint32 total; PDF ring 1024).
  Over budget -> a typed refusal, never a partial file. Cap the RAW caller input length before
  normalization (DB-057 (d); `dxf_writer._normalize_ring` coerces to a list before the edge cap) and
  clamp `DxfLimits` at the seam (DB-057 (k)).
- **Logging.** Server-generated correlation id only (never the caller's raw id, or strip control chars —
  DB-058 (d)); log the exception class + a length-bounded sanitized message at error level; NO
  upstream/caller text ever reaches a log line.
- **Escaping.** The writers already escape (`dxf_writer._sanitize_value`, `pdf_sheet_writer._escape_pdf_text`,
  GLB ASCII-only names); the service adds the length cap and claim-word screen ahead of them.

### 2.1 The 3D scene payload contract

A flag-gated scene route (same posture, UNMOUNTED until the mount seam) returns a renderer-agnostic
payload the web viewer draws and never becomes the source of.

- **Shape.** The `MassingModel.as_dict()` object (`massing_model.py:464`): `source`, `disclosure`,
  `coordinate_reference_system` (with `world_to_local`), `parcel`, `building_layer`, `meshes`, `plates`,
  `metrics`, `provenance` — PLUS a `context_buildings` layer assembled from
  `fetch_context_buildings` (each `ContextBuilding` with attributes ESCAPED on render — DB-058 (a) — and a
  `base_z` derived from `GROUND_ELEVATION` under ONE declared vertical datum, chosen knowingly by the
  scene assembler — DB-058 (f), DB-053 (f)). Optionally an accompanying GLB (via `write_glb`) for direct
  three.js loading.
- **Coordinate frame.** Canonical EPSG:2263 US survey feet server-side; local origin =
  `massing_model._local_origin` / `_crs_frame` (`world_to_local = subtract_local_origin`). The GLB path
  is already in local metres via `glb_writer.AXIS_MAPPING` + `US_SURVEY_FOOT_TO_METRE = 1200/3937`. Make
  the vertical unit explicit in the payload (DB-054 (k)).
- **Refusals / honesty / logging / escaping.** Same discipline as §2, including the off-event-loop
  cancellable job, the per-request deadline and the rate limit (DB-061 (i)) [ORCH-CORRECTED per M5-T099 G3 B1]. MultiPolygon footprints with
  courtyard holes are DISCLOSED or REFUSED, never silently dropped (DB-053 (g); the massing prism builder
  takes one ring). Coincident stacked-prism interface caps are deduped or disclosed for GLB export
  (DB-054 (m)).
- **No live exposure.** Both route modules ship UNMOUNTED (asserted absent from OpenAPI); nothing here
  reaches `app/main.py` until PKT-H (the mount packet) [label ORCH-CORRECTED per M5-T099 G5 F4].

---

## 3. The web 3D viewer design (AS-3)

Stack (admitted / rule-mandated): `three 0.186.0` + `@react-three/fiber 9.7.0` (`apps/web/package.json:18,23`),
Drei only if separately admitted, glTF/GLB for runtime models (`.claude/rules/3d-ui-expansion.md` 5).
Never build WebGL from scratch (rule 6); AI prose never defines geometry (rules 8-9); producer/reviewer
separation and visual/math/perf/a11y/human-journey evidence are G3/G4 evidence (rules 10-11).

- **Data path.** The viewer calls the flag-gated scene route -> receives the scene JSON (+ optional GLB)
  -> renders. GLB loads through three's `GLTFLoader`; JSON meshes become `BufferGeometry`. The
  disclosure/label (`Proposed - not a city record` / `Generated building option`) is shown as a caption,
  driven by `MassingModel.disclosure`, never re-authored client-side.
- **Coordinate frames.** Prefer the server GLB, which is already local metres (2263 ft -> m by the GLB
  writer). If the JSON mesh path is used, the viewer converts with the SAME `1200/3937` constant and
  `AXIS_MAPPING`; the plan makes the GLB writer the single canonical converter so the viewer never
  re-derives the CRS.
- **Performance limits.** Bounded by the writer caps already enforced server-side (≤ 1000 meshes,
  ≤ 500_000 vertices); one scene at a time; instanced meshes for context buildings; dispose GL resources
  on unmount (the accepted `map-runtime` pattern); lazy-load the viewer chunk.
- **Non-visual text alternative.** A keyboard-accessible, announced text panel listing the SAME numbers
  the model shows — parcel bbl, building-option label, floor count, floor-to-floor heights, footprint
  area, context-building count — so the 3D canvas is not the only source of the facts.
- **CSP + external resources [ORCH-CORRECTED per M5-T099 G5 F3].** PKT-I names the viewer route's
  Content-Security-Policy (`script-src`, `worker-src`, and a `connect-src` limited to the app's own API
  origin). Server GLBs are self-contained (one embedded binary buffer; no external buffer or texture URIs),
  and the viewer configures `GLTFLoader` so it never fetches an external resource. Option 1 in §3.1 brings a
  WASM physics engine whose use would need a `wasm-unsafe-eval` CSP relaxation — an input to the PKT-G
  owner decision.
- **Print behaviour.** A WebGL canvas does not print reliably; the print path shows the text alternative
  plus the accepted PDF site plan (from the export route), not a blank canvas.
- **CI-only web testing.** No local npm/npx/node (thin client; `.claude/rules/CODING_RULES.md`). vitest +
  jsdom; read only the FAIL summary lines (MapLibre/WebGL `getContext` noise is not the failure). Add a
  test that pins `three=0.186.0` / `@react-three/fiber=9.7.0` and rejects range characters in
  `apps/web/package.json` (DB-062 (f)). The human-journey walkthrough (Playwright + independent reviewer)
  is G3 acceptance evidence.

### 3.1 The `@types/three` decision — OWNER's to make (DB-062 (a)); this plan chooses NEITHER

`three@0.186.0` ships no type declarations. Two paths, laid out with trade-offs:

- **Option 1 — admit `@types/three`** as a dev dependency under the FULL dependency-security policy
  (exact pin, ≥ 7-day age / 604800 s, zero advisories at every severity, registry-integrity match, a G5
  provenance review, a GitHub-generated lockfile, audits on every change; D-087-R009/R011 unchanged, no
  waiver).
  - PRO: complete, maintained typings for the whole three API surface; low ongoing maintenance; tracks
    the admitted `three` version.
  - CON: it pulls about six runtime dependencies INCLUDING a WASM physics engine
    (`@dimforge/rapier3d-compat`) that our use does not need (DB-062 (a)); larger supply-chain surface;
    every lock regeneration must re-verify the floating `@types/webxr '*'` range through the age gate
    and audit (DB-062 (d)); if that WASM were ever loaded it would need a `wasm-unsafe-eval` CSP
    relaxation (§3) [ORCH-CORRECTED per M5-T099 G5 F3].
- **Option 2 — a reviewed LOCAL declaration file** (`.d.ts`) covering ONLY the three API surface we use
  (Scene, PerspectiveCamera, WebGLRenderer, BufferGeometry, Mesh, GLTFLoader, a few materials).
  - PRO: zero new dependencies; no WASM; minimal supply-chain surface; exact-scoped to what we import.
  - CON: hand-maintained; must be updated whenever we use a new three API or bump `three`; risk of drift
    from the upstream types; is security-sensitive and needs independent (Tier B) review.

The orchestrator records the owner's ruling in PKT-G, then contracts either the admission packet
(Option 1) or the declaration-file packet (Option 2).

---

## 4. The AutoCAD round trip (AS / objective 4)

- **Export side (works today at module level).** DXF out is R12/AC1009, `$INSUNITS 21`, which AutoCAD
  opens natively and can `Save As` DWG — so DXF serves the "middleman" import goal under D-087-R004's DXF
  reading of R008. The owner-openable sample DXF/PDF/GLB + plain-English README (in-flight M5-T096) is the
  documented AutoCAD-open check that closes D-087-R004's owner-check requirement; the committed
  writer->reader round trip (in-flight M5-T097) closes D-087-R006's round-trip requirement.
- **Import side (FUTURE — PKT-F) [label ORCH-CORRECTED per M5-T099 G5 F4].** An architect's DXF -> `read_dxf` (accepted; hardened by M5-T097) reads
  the strict subset (LINE / LWPOLYLINE / POLYLINE / 3DFACE / TEXT) -> PKT-F maps closed rings to a
  `proposed_massing` DRAFT and runs it through the SAME `validate_proposed_massing` contract. C-track
  honesty binds (D-087-R005): the USER confirms which polylines are building outline / property line /
  street frontage; units are confirmed against a known dimension; discrepancies are shown, never
  auto-reconciled; nothing is labelled a city record.
- **Import parse-time controls — PKT-F acceptance criteria [ORCH-CORRECTED per M5-T099 G5 F2(b)-(e)].**
  (b) A raw HTTP upload ceiling enforced by the accepted T053 bounded-streaming primitives BEFORE the body is
  materialized (the `DxfLimits` clamp fires only inside `read_dxf`, after buffering). (c) The parse runs OFF
  the event loop in a cancellable job under a per-request wall-clock deadline, with the route's rate limit
  (DB-061 (i)). (d) A content-type + magic-byte check on the upload (ASCII DXF only; the binary-DXF sentinel
  refused). (e) The import path persists NOTHING: it maps to an in-memory proposal DRAFT (no storage, no RLS
  surface); if persistence is ever added, it comes in its own gated packet with a private bucket, tenant RLS
  and a size cap.
- **What stays later:** native DWG read/write (D-087-R007, owner licensing/payment decision — STOPPED,
  Tier D — until the owner rules; DXF is the path meanwhile); curved/arc/spline entities beyond the strict
  subset; block/xref resolution.

---

## 5. Ordered packet breakdown (AS-4)

All packets below are PROPOSALS to be contracted later as `M<x>-T<n>` under G0/G2/G3/G4/G5 (web packets
add the G3 human-journey walkthrough as acceptance evidence). Each depends first on the in-flight packet
that locks the same file (§0.1). Within each parallel batch the `allowed_paths` are pairwise disjoint at
FILE level (D-087-R002). Route MODULES ship UNMOUNTED; `app/main.py` edits are isolated in single mount
packets so route-registration serializes on that one hot file.

### Batch 1 — pre-wiring hardening (parallel; after the in-flight packet on the same file is accepted)

| Pkt | Files (allowed_paths) | Depends on | Gates | Riders closed |
|---|---|---|---|---|
| PKT-A shared claim-word module | `app/cad/claim_words.py` (new), `app/cad/dxf_writer.py`, `app/cad/glb_writer.py`, `app/cad/pdf_sheet_writer.py`, `tests/cad/test_claim_words.py`, `tests/cad/test_dxf_writer.py`, `tests/cad/test_glb_writer.py`, `tests/cad/test_pdf_sheet_writer.py` | M5-T096 (dxf_writer/test_dxf_writer) | G0,G2,G3,G4,G5 | DB-059 (b),(c); DB-053 (c) (screen adopts the shared key) |
| PKT-B1 PDF writer wiring-hardening | `app/cad/pdf_sheet_writer.py`, `tests/cad/test_pdf_sheet_writer.py` | PKT-A (same file → sequences after A) | G0,G2,G3,G4,G5 | DB-053 (a),(b),(d); DB-059 (a),(d) |
| PKT-C connector wiring-hardening + source_registry | `app/connectors/building_footprints_arcgis.py`, `tests/connectors/test_building_footprints_arcgis.py`, the `source_registry` record | M5-T100 (same file) | G0,G2,G3,G4,G5 | DB-058 (a),(b),(c),(d),(f),(g); DB-053 (e-resolved note),(f),(h) |
| PKT-K (C1) real-file PDF resolver | `app/drawings/pdf_object_streams.py` (new; does NOT widen `read_object_table`), `app/drawings/sheet_reader.py` (facade wiring), `tests/drawings/test_sheet_reader.py`, `tests/drawings/test_pdf_object_streams.py` | M5-T094 (split) + M5-T097 | G0,G2,G3,G4,G5 | DB-055 (g),(k),(l),(a),(e),(i),(f) |

PKT-A and PKT-B1 both touch `pdf_sheet_writer.py`/`test_pdf_sheet_writer.py`, so they SERIALIZE (A then
B1); PKT-A/PKT-C/PKT-K are pairwise file-disjoint and run in parallel. (If the orchestrator prefers, the
PKT-A rewire of `pdf_sheet_writer` can be folded into PKT-B1 to shorten the chain.)

**Mandatory PKT-K acceptance criterion [ORCH-CORRECTED per M5-T099 G5 F2(a)].** Widening the reader to
PDF 1.5+ object and cross-reference streams adds zlib inflation of attacker-controlled streams. PKT-K must
carry an ABSOLUTE inflated-bytes cap AND an inflate-ratio guard on every object/xref stream, charged before
the inflated bytes are materialized and sharing the document-wide decoded-bytes budget, each with a
mutation that reddens. It also truncates the XObject `/name` echo in refusal details with `_preview`
(DB-055 (f); the M5-T094 G5 advisory A1).

### Batch 2 — export & scene services + UNMOUNTED routes (parallel; file-disjoint)

| Pkt | Files (allowed_paths) | Depends on | Gates | Riders closed |
|---|---|---|---|---|
| PKT-D export service + route (unmounted) | `app/cad/export_service.py` (new), `app/api/v1/export_api.py` (new), `tests/cad/test_export_service.py`, `tests/api/v1/test_export_api.py` | PKT-A, PKT-B1 | G0,G2,G3,G4,G5 | DB-057 (d),(k); DB-059 (e),(h); DB-054 (m) (export dedupe/disclose); DB-061 (i) (job + deadline + rate limit); the §2 filename-safety criterion (mandatory, G5 F1) [ORCH-CORRECTED per M5-T099 G3 B1 / G5 F1] |
| PKT-E scene assembler + route (unmounted) | `app/scenario/scene_assembler.py` (new), `app/api/v1/scene_api.py` (new), `tests/scenario/test_scene_assembler.py`, `tests/api/v1/test_scene_api.py` | PKT-C, M5-T098 | G0,G2,G3,G4,G5 | DB-054 (k),(l),(n),(o); DB-058 (a); DB-061 (i) (job + deadline + rate limit) [ORCH-CORRECTED per M5-T099 G3 B1] |
| PKT-F DXF import service + route (unmounted) | `app/drawings/dxf_import.py` (new), `app/api/v1/dxf_import_api.py` (new), `tests/drawings/test_dxf_import.py`, `tests/api/v1/test_dxf_import_api.py` | M5-T097 | G0,G2,G3,G4,G5 | DB-057 (k) (import DxfLimits clamp); DB-061 (i); the §4 import parse-time controls (b)-(e) [ORCH-CORRECTED per M5-T099 G3 B1 / G5 F2] |

All three are file-disjoint (new modules + own tests) and run in parallel.

### Batch 3 — mount + viewer (serialized where they share a hot file)

| Pkt | Files (allowed_paths) | Depends on | Gates | Riders closed |
|---|---|---|---|---|
| PKT-G `@types/three` OWNER decision → admission OR local .d.ts | decision record; then either the lockfile-admission packet or `apps/web/src/types/three.d.ts` + its use | owner ruling | G0,G2,G5 (dep-security G5 if Option 1) | DB-062 (a) |
| PKT-H product mount packet | `app/main.py` ONLY (include_router export/scene/import behind the flags) | PKT-D, PKT-E, PKT-F | G0,G2,G3,G4,G5 | — (exposure seam; verifies DB-061 (i) on every route before mounting) [ORCH-CORRECTED per M5-T099 G3 B1] |
| PKT-I web 3D viewer | `apps/web/src/components/.../MassingViewer.tsx` + its `__tests__`, viewer lib under `apps/web/src/lib/` | PKT-H (mounted scene route) + PKT-G | G0,G2,G3(HJ),G4,G5 | DB-062 (f) |

PKT-H edits `app/main.py`; PKT-J (§7) also edits it — the two mount packets SERIALIZE on `main.py`.

### Standalone tracks

- **C-track continued — PKT-L (C2 user-confirm):** `app/drawings/` confirm module + tests; units/scale
  confirmed against a known dimension, user confirms line roles, imported geometry enters the proposal
  contract. Depends on PKT-K. Closes DB-055 (c),(d). Gates G0,G2,G3,G4,G5.
- **PKT-M CI glTF-Validator** (CI-side; DB-059 (f)) — runs the Khronos validator on the GLB golden in CI.
  Gates G0,G2,G4.

---

## 6. Rider map — every open DB-053..DB-062 sub-item to exactly one future step (AS-1)

`in-flight` = already contracted (§0.1). `by note` = disclosure/practice only, no code step.

| Rider | Disposition |
|---|---|
| DB-053 (a),(b),(c),(d) | (a),(b),(d) PKT-B1; (c) PKT-A/export screen (§2) |
| DB-053 (e) | DISCHARGED by M5-T089 (connector uses live FeatureServer field names) — by note |
| DB-053 (f),(g),(h) | (f) PKT-C/PKT-E vertical-datum rule; (g) PKT-E holes disclose/refuse; (h) by note (INFERENCE, restated DB-058 (j)) |
| DB-053 (i) | PKT-G, Option 1 only: the admission packet argues necessity (dependency-security policy section 5) and gives a maintainer-change assessment covering all six provenance fields; moot under Option 2 [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-053 (j),(k) | by note: (j) contingent — ezdxf is not proposed; any future proposal, even as test tooling, is a NEW package with full G5 admission; (k) moot — every writer targets R12/AC1009 (no OBJECTS section); G1 re-verification only if a writer ever emits R2000+ [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-054 (a)-(j) | DISCHARGED by M5-T088 (massing hardening, accepted) — by note |
| DB-054 (k),(l),(n),(o) | PKT-E (scene/massing wiring) |
| DB-054 (m) | PKT-D (export dedupe/disclose coincident caps) |
| DB-055 (a),(e),(i) | PKT-K (next sheet-reader/test touch) |
| DB-055 (b),(m) | in-flight M5-T094 (split) |
| DB-055 (c),(d) | PKT-L (C2 user-confirm) |
| DB-055 (g),(k),(l) | PKT-K (C1 xref/object-stream resolver) |
| DB-055 (h) | DISCHARGED by M5-T093 (negative real-corpus result) — by note |
| DB-055 (n) | by note (sharpen at next reader touch) |
| DB-055 (f) | PKT-K (truncate the XObject `/name` echo in refusal details with `_preview`; the §5 PKT-K note) [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-055 (j) | by note (LOW wording nit in the M5-T083 evidence map; no code step) [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-056 (a),(b),(c) | PKT-J (max-envelope mount) |
| DB-056 (d) | by note (next control-plane tooling touch; outside D-087 product scope) |
| DB-057 (a),(b),(f) | in-flight M5-T096 |
| DB-057 (h),(i),(j),(l),(m),(n) | in-flight M5-T097 |
| DB-057 (d),(k) | (d) PKT-D raw-length cap; (k) PKT-D + PKT-F DxfLimits clamp at the seam |
| DB-057 (c),(e),(g),(o),(p) | by note |
| DB-058 (e),(h),(l),(m) | in-flight M5-T100 |
| DB-058 (a),(b),(c),(d),(f),(g) | PKT-C (connector wiring); (a) also PKT-E/PKT-I escape-on-render |
| DB-058 (i),(j),(k) | by note |
| DB-059 (a),(d) | PKT-B1 |
| DB-059 (b),(c) | PKT-A (shared claim-word module + drift test) |
| DB-059 (e),(h) | PKT-D (reconcile + redact at the export seam) |
| DB-059 (f) | PKT-M (CI glTF-Validator) |
| DB-059 (g) | by note (next app/cad seam; orchestrator housekeeping) |
| DB-060 (a),(b),(c),(d) | the D-086 accessibility/announcement slice (outside D-087; referenced, not created here) |
| DB-060 (e) | PKT-J (max-envelope mount precondition: candidateIsAdoptable contract-violation guard) |
| DB-060 (f),(g),(h) | by note (next ledger touch / P5 print gate) |
| DB-061 (a),(b),(c),(d),(f) | in-flight M5-T098 |
| DB-061 (e) | by note (the scene/UX packet PKT-E must know resource-bound precedence is check-order) |
| DB-061 (g) | in-flight M5-T095 |
| DB-061 (h) | a derivation packet outside this plan's batches (derivation.py adopts the shared GEOS-backed simplicity check; bounded today by re-validated input) — referenced, not created here [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-061 (i) | SAFETY: PKT-D, PKT-E and PKT-F each run their work off the event loop in a cancellable job under the per-request deadline with a per-caller rate limit; PKT-H verifies it on every route before mounting [ORCH-CORRECTED per M5-T099 G3 B1] |
| DB-062 (a) | PKT-G (owner decision) → PKT-I (viewer) |
| DB-062 (f) | PKT-I (exact-version pin test) |
| DB-062 (b),(c),(d),(e),(g) | by note (any later web dependency change) |

---

## 7. The unmounted max-envelope route — mount preconditions (listed, NOT relaxed)

`POST /api/v1/max-envelope` ships UNMOUNTED (`app/api/v1/max_envelope_api.py:10`). A future **PKT-J**
mounts it (edits `app/main.py` only, serialized with PKT-H). Its preconditions, verbatim from the route
docstring (`:10-36`) and the riders, all still apply:

1. Flag-gated OFF by default (`INTERNAL_RULE_EVAL_ENABLED`; `include_in_schema=False`; absent/unknown ->
   generic 404); a bounded request body (BOUNDED STREAMING, T053 primitives).
2. authn / tenancy / per-user ownership of the supplied lot geometry arrive with the PUBLIC exposure
   packet — recorded as a disposition, NOT implemented; the route is unreachable without the internal flag.
3. The engine is the single entry, called once off the event loop; it runs the accepted checker on its own
   candidate, so a generator-checker inconsistency fails closed (500) rather than shipping a maximum the
   checker refuses.
4. DB-056 (a),(b),(c): the `GEOMETRY_OVER_CAP` route-level `placement.detail` assertion; the `.get`
   belt-and-braces on `placement['detail']`; the scalar-bbl edge guards.
5. DB-060 (e): `candidateIsAdoptable` must honour contract violations before Adopt can appear.
6. D-083: the surface uses "Preliminary development limits" for per-rule ceilings and "Generated building
   option" for a fitted candidate; the demonstrated-maximum class stays WITHHELD (no "maximum allowed
   building").

---

## 8. Open owner decisions (AS / objective 6)

1. **R008 — "the middleman" = DXF?** Working assumption is DXF (AutoCAD opens it natively, saves it as
   DWG). All DXF work proceeds meanwhile; a different answer is recorded as an amendment and re-scopes
   R004 without discarding delivered DXF work.
2. **R007 — native DWG library.** RealDWG / Open Design Alliance (proprietary, paid) or LibreDWG (GPL,
   copyleft) — a licensing/payment decision that STAYS STOPPED (Tier D / Section 20) until the owner
   rules. No DWG library enters any lockfile meanwhile.
3. **`@types/three`** (DB-062 (a)) — admit the typed package (pulls a WASM physics engine + ~6 deps, full
   dependency-security admission) OR a reviewed local declaration file (zero deps, hand-maintained). Both
   options and trade-offs are in §3.1; the owner chooses.
4. **Real architect PDFs.** The reader reads 0 of 6 public federal drawings (all use PDF 1.5+ xref /
   object streams). A few REAL architect PDFs from the owner would let a capture task define the supported
   drawing classes from real files before the C1 reader (PKT-K) is widened.

---

## 9. Boundaries reaffirmed (D-087-R009)

Every gate G0-G7, the dependency-security policy (exact pins, ≥ 7-day age, zero advisories, registry
integrity, G5 provenance for any new package, GitHub-generated lockfile, no waiver), Tier D / Section 20,
PR #241 (never merged), the unmounted max-envelope route and its preconditions, the D-086 sequencing and
preservation prohibitions, the thin-client limits (no local npm; CI is the web authority), and D-051
fail-closed discipline all stand. The July 19-task pack, its 9 contracts, and GDS P1-P8 are reference
input only; every packet above is orchestrator-designed and independently gated.
