# M5-T108 producer report — D-087 PKT-F: DXF import service + UNMOUNTED import route

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t108` (branch `task/M5-T108-dxf-import`).
Claim-seam base: `110894295ec97c1d7cb87deb3421a628b526b66b`.

## Files written (allowed_paths only)

- `services/api/app/drawings/dxf_import.py` — pure import service (candidates → roles → draft); no route, no I/O, no persistence.
- `services/api/app/api/v1/dxf_import_api.py` — the UNMOUNTED, double-flag-gated import route (two endpoints).
- `services/api/tests/drawings/test_dxf_import.py` — service acceptance pack (18 tests).
- `services/api/tests/drawings/test_dxf_import_api.py` — route acceptance pack (23 tests).
- `project-control/reports/M5-T108-producer-report.md` — this report.

`git status --short` shows exactly these 4 code files modified (report added). No forbidden path touched: `dxf_reader.py`, `sheet_*.py`, `pdf_object_streams.py`, `app/drawings/__init__.py`, `app/scenario/*`, `app/cad/*`, `app/documents/*`, `app/main.py`, `config.py`, and requirements are all unchanged.

## API shape (candidates → roles → draft)

The request BODY is always the raw ASCII DXF upload (bounded streaming, content-type + magic-byte gated). Role/unit assignments are QUERY PARAMS because the body is the file.

- `POST /api/v1/dxf-import/candidates` — lists the closed rings as candidates: `{index, entity_type, layer(escaped), vertex_count, measured{units, bbox_width, bbox_height, perimeter, area}}` in the DECLARED units, plus `declared_units`, escaped `acad_version`, a `disclosure` of every non-candidate primitive (open polylines, lines, faces, text, disclosed-unknown types, skipped sections), a plain honesty `notice`, and `X-Correlation-ID`.
- `POST /api/v1/dxf-import/draft?building_outline=<idx>&floors=<n>&floor_to_floor_ft=<ft>&author=<s>&{confirmed_units=<unit> | known_length_ft=<ft>&measured_length=<u>}[&property_line=<idx>&street_frontage=<idx>]` — builds a `proposed_massing` DRAFT from the assigned building-outline ring (closure made explicit, coordinates unit-scaled), a single user-supplied level (the 2-D drawing carries no height), an empty exterior-wall list, and `provenance.kind="proposed"`; runs it through the SAME `validate_proposed_massing`. On success returns `{proposed_massing(validated block), provenance{input_class, precision, label, declared_units, confirmed_units, unit_scale_ft_per_unit, scale_source, assigned_roles, acad_version(escaped), author(escaped)}, discrepancies[], correlation_id}`. Property-line / street-frontage roles are recorded and echoed but do not feed the massing block (footprint-only draft).

Two unit-confirmation mechanisms, exactly one required (neither/both → typed `ambiguous_units`): a feet-family `confirmed_units` name (fixed exact scale) OR a `known_length_ft` + `measured_length` pair (empirical scale from a real-world dimension). A declared unit differing from the confirmed one is a `units_mismatch` DISCREPANCY: shown, the confirmed unit still drives the scale, never auto-reconciled.

Status/state matrix (single source of truth `DXF_IMPORT_STATUS_STATE_MATRIX`): `(200,None)`, `(404,None)`, `(413,payload_too_large)`, `(415,unsupported_media_type)`, `(422,validation_error)`, `(429,rate_limited)`, `(503,deadline_exceeded)`, `(500,internal_error)`.

## Per-AS evidence

- **AS-1 (parse-time controls).** (b) raw ceiling BEFORE materialization via the reused T053 `_declared_content_length` fast path + `_read_body_within_ceiling` streamed accumulator → `test_over_ceiling_upload_refused_413`, `test_over_ceiling_streamed_refused_413`. (d) content-type + magic-byte + binary-sentinel gate `sniff_dxf_media` → `test_binary_dxf_refused_415`, `test_wrong_content_type_refused_415`, service `test_sniff_*`. Clamp: `_IMPORT_DXF_LIMITS` is a fixed reviewed `DxfLimits(max_bytes=MAX_BODY_BYTES)`, never request-derived → `test_seam_passes_fixed_reviewed_limits`. (c) `read_dxf` runs off the event loop in `run_in_threadpool` under `asyncio.wait_for(READ_DEADLINE_SECONDS)` → `test_read_job_deadline_503`; per-caller `_RateLimiter` (stdlib, monotonic, thread-safe) → `test_rate_limit_429`. Each control has a reddening mutation (see table).
- **AS-2 (candidates → roles → draft).** Closed rings listed with layer + measured dims → `test_candidates_list_closed_rings_with_measured_dimensions`; open polyline disclosed, not a candidate → `test_open_polyline_is_disclosed_not_a_candidate`; draft only from assigned roles + confirmed units through `validate_proposed_massing` → `test_draft_built_from_roles_and_confirmed_units`, `test_draft_200`; discrepancy shown not reconciled → `test_units_mismatch_is_shown_never_reconciled`, `test_draft_shows_discrepancy_not_reconciled`; ambiguous/unsupported units, bad candidate index, out-of-bounds ring all refuse typed → `test_ambiguous_units_refused`, `test_unsupported_units_refused`, `test_bad_candidate_index_refused`, `test_out_of_bounds_ring_refused_by_the_contract`, route `test_out_of_bounds_ring_422`.
- **AS-3 (honesty + provenance).** `precision="imported drawing - not survey-confirmed"` (D-083-R006), `label="Proposed - not a city record"`; no positive claim word (`permitted`/`approved`/`maximum allowed`/`as of right`/`demonstrated maximum`) anywhere in the draft → `test_draft_provenance_is_honest_and_not_upgraded`, route `test_draft_200`. The service sets provenance once and calls nothing that upgrades it.
- **AS-4 (untrusted drawing text).** Every drawing string (layer, `$ACADVER`, TEXT) escaped via `_escape_drawing_text` (control chars → `\xNN`) and length-bounded before output; reader-refusal detail bounded/escaped; only exact bytes reach `read_dxf` → `test_drawing_text_is_escaped_on_output`, `test_sniff_*`. Logging is correlation-id only (no caller/drawing text on any log line).
- **AS-5 (persists nothing + scope).** No storage import or write anywhere; `app/main.py` untouched; route ABSENT from the real app + its OpenAPI → `test_route_is_unmounted_in_the_real_app`; zero new dependencies (stdlib + already-admitted fastapi/shapely via the contract); exactly the allowed paths; `modularity_check --check` exit 0; two identical draft requests return equal bodies (no accumulated state) → `test_no_persistence_state_between_requests`.

## DB-070 (a)-(e) / DB-057 (k) closure table

| Rider | Requirement | Disposition |
|---|---|---|
| DB-070 (a) | control chars kept in TEXT/layer/$ACADVER — consumer must escape on output, never log raw | CLOSED — `_escape_drawing_text` escapes every drawing string before it enters a response; logs carry only the correlation id. `test_drawing_text_is_escaped_on_output`. |
| DB-070 (b) | refusal detail must not reflect raw/unbounded content | CLOSED — reader-refusal detail routed through `_escape_drawing_text`; route refusal messages bounded by the reused `_bounded_message`. |
| DB-070 (c) | small digit cap on group codes (defense in depth) | DEFERRED to `dxf_reader.py` (read-only here; a reader change is required and forbidden in this packet). Mitigation stands: the reader bounds a group-code line to `max_line_chars` (clamped ≤ 65_536) so CPython's int-digit limit governs. Recorded for the next reader touch (DISCOVERY). |
| DB-070 (d) | only exact bytes accepted; `DxfLimits` never built from untrusted input | CLOSED — `sniff_dxf_media` admits only ASCII DXF (binary sentinel refused) then the exact bytes reach `read_dxf`; `_IMPORT_DXF_LIMITS` is a fixed module constant. `test_seam_passes_fixed_reviewed_limits`, `test_binary_dxf_refused_415`. |
| DB-070 (e) | run `read_dxf` off the request thread in a cancellable job with a deadline + upload byte limit | CLOSED — `run_in_threadpool` + `asyncio.wait_for(READ_DEADLINE_SECONDS)` + `MAX_BODY_BYTES` ceiling. `test_read_job_deadline_503`. Note: a CPython thread is not force-killed; the clamped limits bound the work it can do before returning (disclosed). |
| DB-057 (k) | import `DxfLimits` clamp at the seam | CLOSED — the seam passes the fixed reviewed `_IMPORT_DXF_LIMITS`; the reader additionally hard-clamps every field via `_LIMIT_CEILINGS`. `test_seam_passes_fixed_reviewed_limits`, `test_mutation_clamp_uses_module_constant`. |
| DB-061 (i) | off-loop cancellable job + per-request deadline + per-caller rate limit at the route | CLOSED — deadline (above) + `_RateLimiter`. `test_rate_limit_429`. |

## Mutation table (every new guard reddens; consuming-namespace mutation)

| Guard | Guarding test | Reddening mutation |
|---|---|---|
| Upload ceiling (b) | `test_over_ceiling_upload_refused_413` | `test_mutation_ceiling_guard` — patch `mod.MAX_BODY_BYTES` huge → over-original body no longer 413s. |
| Media/magic-byte (d) | `test_binary_dxf_refused_415` | `test_mutation_media_guard` — patch `mod.sniff_dxf_media`→None → binary reaches `read_dxf`, becomes 422 not 415. |
| Seam clamp (d / DB-057 k) | `test_seam_passes_fixed_reviewed_limits` | `test_mutation_clamp_uses_module_constant` — swap `mod._IMPORT_DXF_LIMITS` → captured limits follow the constant. |
| Read deadline (c) | `test_read_job_deadline_503` | `test_mutation_deadline_guard` — generous deadline over the same slow read → no 503. |
| Rate limit (c) | `test_rate_limit_429` | `test_mutation_rate_limit_guard` — inject an always-allow limiter → no 429. |
| Massing-contract call (AS-2) | `test_out_of_bounds_ring_refused_by_the_contract` | `test_mutation_validate_contract_is_actually_called` — patch `svc.validate_proposed_massing`→no-op → out-of-bounds ring passes. |
| Output escaping (AS-4) | `test_drawing_text_is_escaped_on_output` | `test_mutation_escape_is_actually_applied` — patch `svc._escape_drawing_text`→identity → raw control char reaches the layer. |
| Closed-flag candidate gate (AS-2) | `test_open_polyline_is_disclosed_not_a_candidate` | `test_mutation_closed_flag_gates_candidates` — patch `svc._closed_ring_candidates` to take all → open ring lists. |
| Ambiguous-units gate (AS-2) | `test_ambiguous_units_refused` | `test_mutation_ambiguous_units_guard` — patch `svc._resolve_scale` to accept → both-mechanisms case passes. |

## Commands (explicit cwd; verbatim tails) — all [OBSERVED]

- cwd `services/api`: `python -m ruff check app/drawings/dxf_import.py app/api/v1/dxf_import_api.py tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py` → `All checks passed!`
- cwd `services/api`: `python -m ruff check .` → `Found 4 errors.` — all 4 are E501 in SIBLING placeholder files (`app/api/v1/export_api.py`, `app/api/v1/scene_api.py`, `app/cad/export_service.py`, `app/scenario/scene_assembler.py`), owned by the parallel PKT-D/PKT-E packets (M5-T106/M5-T107); MY files are clean. Resolves at integration when each producer replaces its own placeholder. [OBSERVED]
- cwd `services/api`: `python -m pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py -q` → `41 passed in 2.94s`
- cwd `services/api`: `python -m pytest tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q` → `61 passed in 2.94s` (unchanged, green)
- cwd repo root: `python tools/modularity_check.py --check` → `exit=0`
- New-module SLOC: `dxf_import.py` 509 total lines / `dxf_import_api.py` 407; neither flagged by `modularity_check --report` (below WARN 600).

Local Python is 3.11.9 (ruff/pyproject target 3.12). Code is 3.11-runnable and py312-clean under ruff.

## Deviations

1. **Second gating flag defined locally.** Plan section 2 requires a caller-supplied-geometry WRITE/import path to carry a dedicated default-off flag IN ADDITION to `INTERNAL_RULE_EVAL_ENABLED`. `config.py` is outside this packet's allowed_paths, so `DXF_IMPORT_ENABLED` is declared in `dxf_import_api.py` with the same fail-safe explicit-true-token semantics; its canonical registration in `config.py` belongs to the PKT-H mount seam. Both flags must be true to reach a handler; either absent/unknown → generic 404. This is strictly MORE conservative (never easier to reach). The packet's "UNMOUNTED ROUTE" input names only `INTERNAL_RULE_EVAL_ENABLED`; the second flag is defense in depth per the plan, not a relaxation.
2. **No shared per-caller rate limiter existed to reuse.** The mechanisms the packet cites (`lot_geometry.py` / `properties.py` "rate_limited") map UPSTREAM connector throttling (SODA 429/503), not a per-caller ROUTE limiter. A minimal stdlib `_RateLimiter` (monotonic fixed window, thread-safe) is implemented in the route — zero new dependencies, per the "never a new package" constraint. Injectable via `get_rate_limiter()` for tests.
3. **DB-070 (c) not applied at the seam** — it needs a `dxf_reader.py` change (forbidden here); recorded for the next reader touch. Existing mitigation (`max_line_chars` + int-digit limit) stands.
4. **Roles beyond building_outline are contextual.** `validate_proposed_massing` consumes only outline/levels/walls/provenance, so property-line / street-frontage assignments are recorded and echoed but do not enter the massing block (footprint-only draft). A later track (PKT-L) can consume them.

## DISCOVERIES (for the orchestrator to record in docs/DISCOVERY_BACKLOG.md)

- **DISC-A (units family / CRS scope).** The draft supports FEET-FAMILY confirmed units only (feet, us_survey_feet, inches, us_survey_inches, yards — all exact rational feet). Metre/other-unit conversion into a frame labelled EPSG:2263 US survey feet would assert a CRS/units interpretation this phase does not prove (SURVEY_DOCUMENT_FORMAT_POLICY: "Never auto-derive georeferenced boundaries from DXF without proven CRS/units handling"); such units refuse typed or must use the empirical known-dimension path. us_survey_feet vs international feet (~2 ppm) are both treated as 1.0 for a draft. Full metre support + georeferencing (placing a local-origin drawing into state plane) is future work (PKT-L / a proven-conversion packet).
- **DISC-B (policy vs directive reconciliation).** `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md` sets DXF to CONVERT/DEFER-initial ("do NOT accept DXF as a parsed geometry source yet"). D-087-R006 (owner, 2026-09-24, scoped release §2.3) authorizes the parsed DXF import path via the accepted hardened `read_dxf`, and the design honors the policy's core constraint: units are USER-confirmed (not auto-trusted), CRS is NOT auto-derived (an ungeoreferenced drawing fails the massing contract's NYC-bounds check and is surfaced as a discrepancy, never auto-corrected), and nothing is labelled a record. Suggest updating the survey policy's DXF row to reference D-087/PKT-F.
- **DISC-C (DB-070 (c) carry-forward).** The small group-code digit cap remains for the next `dxf_reader.py` touch (see closure table).
- **DISC-D (2-D drawing has no height).** A DXF footprint carries no vertical dimension, so the draft REQUIRES the user to supply `floors` + `floor_to_floor_ft`; the service never invents a height (honesty). Recorded so a future UI surfaces this clearly.

---

# Round 2 (rework) — consolidated fix for G4 F1, G5 MEDIUM 1, and advisories

Producer: backend-engineer (orchestrator-dispatched subagent).
Base (parent) commit: `51f50aa147c0675c0e2669614349487ef715c112` (integration head; contains round-1
material `2df81013` + the three review reports). ONE new commit on top; only the 5 allowed files.
The whole failure surface was inventoried first (from `M5-T108-G3.md`, `M5-T108-G4.md`,
`M5-T108-G5.md`) and fixed as ONE bounded change. dxf_reader.py and everything else untouched.

## Per-finding closure

1. **G5 MEDIUM 1 (BLOCKING) — non-finite measured dimensions → untyped 500. CLOSED.**
   - Service (`dxf_import.py`): added `_measured_is_finite`; `list_candidates` now measures each
     ring, and if any numeric measured value is non-finite (a huge-but-finite ring like `1e300`
     whose shoelace products / bbox span overflow to `inf`) returns a typed
     `ImportRefusal(reason="coordinate_out_of_range", field="building_outline")` → the route maps
     it to a 422 WITH a correlation id (new reason token; `_refusal_response` already routes any
     non-`unsupported_media_type` reason to 422/validation_error).
   - Route (`dxf_import_api.py`): added `_guard_finite_response` — a defense-in-depth PRE-RENDER
     guard mirroring `proposal_validation.py`'s `json.dumps(..., allow_nan=False)`, called before
     BOTH 200 returns. Any non-finite value in a response body becomes the typed
     `(500, "internal_error")` WITH a correlation id instead of a bare Starlette 500 raised during
     render. `import json` added.
   - Tests: service `test_overflow_coordinates_refuse_typed_never_non_finite`; route
     `test_overflow_coordinates_typed_4xx_never_500` (422, never 500, has X-Correlation-ID) and
     `test_non_finite_body_becomes_typed_500_with_correlation_id`. Reddening mutations below.
2. **G4 F1 (BLOCKING) — draft never proves it uses the USER-ASSIGNED ring. CLOSED.**
   - Extracted `_select_ring(rings, index)` seam in `dxf_import.py`; `build_draft` uses it.
   - Tests: service `test_draft_uses_the_user_assigned_ring_not_ring0_or_largest` and route
     `test_draft_uses_the_user_assigned_ring` — TWO distinct closed in-bounds rings, ring A the
     LARGER, `building_outline=1`; assert `outline.vertices[0] == [990000.0, 200000.0]` (ring B's
     first vertex, scaled). Two reddening mutations (always-ring-0 and largest-ring) below; both
     yield ring A `[985000.0, 195000.0]` and fail the guard test.
3. **G4 A1 — known-dimension scale-guard coverage. CLOSED.**
   `test_known_dimension_scale_guard_refuses_bad_values`: `measured_length` 0 / negative / nan /
   inf and `known_length_ft` 0 / negative / inf each → `ImportRefusal(unsupported_units)`. Also
   catches the (previously surviving) mutant that drops the finite/strictly-positive guard.
4. **G4 A2 — reader-refusal detail control-char escaping. CLOSED.**
   `test_reader_refusal_detail_with_control_char_is_escaped` + mutation
   `test_mutation_refusal_detail_escaping`.
5. **G4 A3 — exactly-at-ceiling boundary. CLOSED.**
   `test_upload_exactly_at_ceiling_accepted_plus_one_refused`: a body of exactly `MAX_BODY_BYTES`
   passes the ceiling (reaches the reader → 422), `MAX_BODY_BYTES + 1` → 413.
6. **G3 A2 — isinstance disclosure counts + fixture. CLOSED.**
   Disclosure now uses `isinstance` against the imported `LinePrimitive` / `FacePrimitive` /
   `TextPrimitive` (not `type(p).__name__`). `test_disclosure_counts_line_face_text_by_isinstance`
   with a LINE, a 3DFACE and a TEXT.
7. **G3 A6 — three test gaps. CLOSED.**
   - `(500, "internal_error")` now asserted in `test_status_state_matrix_is_the_documented_set`.
   - `test_disclosed_unknown_and_skipped_sections_are_escaped` (control-char names → `\xNN`).
   - `degenerate_closed_rings` disclosure count added; a CLOSED polyline with < 3 vertices is now
     DISCLOSED, never silently absent — `test_degenerate_closed_ring_is_disclosed_not_silently_absent`.

OUT OF SCOPE (unchanged, correctly deferred to the PKT-H mount): G3 A1/A3/A4/A5, G5 LOW 2/LOW 3,
DB-070 (c). No new discoveries this round.

## Round 2 mutation table (consuming-namespace; each asserts the FLIPPED outcome)

| # | Finding | Guarding test | Reddening mutation | Flip |
|---|---|---|---|---|
| 1 | G4 F1 | `test_draft_uses_the_user_assigned_ring_not_ring0_or_largest` | `test_mutation_ring_selection_always_ring0` (`svc._select_ring`→rings[0]) | vertices[0] ring A `[985000,195000]` ≠ ring B `[990000,200000]` |
| 2 | G4 F1 | (same) | `test_mutation_ring_selection_largest_ring` (`svc._select_ring`→max-area) | vertices[0] ring A (larger) ≠ ring B |
| 3 | G5 MED 1 svc | `test_overflow_coordinates_refuse_typed_never_non_finite` | `test_mutation_overflow_finiteness_guard` (`svc._measured_is_finite`→True) | `ok=True` w/ non-finite area vs typed refusal |
| 4 | G5 MED 1 route | `test_non_finite_body_becomes_typed_500_with_correlation_id` | `test_mutation_pre_render_finiteness_guard` (`mod._guard_finite_response`→None) | bare 500 no X-Correlation-ID vs typed (500,internal_error) with id |
| 5 | G4 A2 | `test_reader_refusal_detail_with_control_char_is_escaped` | `test_mutation_refusal_detail_escaping` (`svc._escape_drawing_text`→identity) | raw `\x01` present vs `\x01` escaped |

## Round 2 commands (explicit cwd; verbatim tails) — all [OBSERVED]

- cwd `services/api`: `python -m ruff check .` → `All checks passed!`
- cwd `services/api`: `python -m pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q` → `118 passed in 10.62s` (round 1 was 102: +16 new tests; import+api 41→57; reader+roundtrip 61 unchanged/green).
- cwd `services/api`: `python -m pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_import_api.py -q` → `57 passed in 5.38s`.
- cwd repo root: `python tools/modularity_check.py --check` → `failures 0; warnings 27` / `EXIT=0` (neither dxf_import.py nor dxf_import_api.py is in the warning list).
- New-file SLOC: `dxf_import.py` 559 lines / `dxf_import_api.py` 432 lines — both under WARN 600.

### Local-toolchain note (NOT a defect; unchanged from round 1)
`cd services/api && python -m pytest tests/drawings -q` (the whole directory) reports 3 COLLECTION
errors in unrelated files — `test_pdf_object_streams.py`, `test_sheet_reader.py`,
`test_sheet_reader_split_equivalence.py` — because they import `app/documents/units.py`, whose
line 276 uses Python 3.12 PEP 695 generic syntax (`def _match_unit[UnitT: enum.Enum](`) that the
sandbox's local Python 3.11.9 cannot parse. Those files and `app/documents/units.py` are outside
this packet's scope and untouched; the errors are present at the base commit and are the documented
sandbox-3.11-vs-repo-3.12 artifact. CI runs 3.12 and collects them; all three G3/G4/G5 reviewers ran
the four in-scope DXF files explicitly for the same reason. [OBSERVED]

## Round 2 deviations

None beyond round 1's deviations (all still stand). No new dependencies; the route stays
`include_in_schema=False` and absent from the real app + OpenAPI (`test_route_is_unmounted_in_the_real_app`);
persists nothing.

END-OF-REPORT
