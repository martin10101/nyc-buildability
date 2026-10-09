# M5-T121 producer report — D-087 PKT-L: PDF sheet import service (phase C2/C3)

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t121` (branch `task/M5-T121-pdf-sheet-import-service`).
Claim-seam base: `a990de06cfa9f6087725c66e6e2adafc12e92c0d`.

## Files written (allowed_paths only)

- `services/api/app/drawings/sheet_import.py` (NEW) — pure PDF sheet import service (candidates → user roles + a service-measured edge scale → validated draft + provenance). No route, no I/O, no persistence.
- `services/api/tests/drawings/test_sheet_import.py` (NEW) — offline acceptance pack (31 tests incl. 8 reddening mutations).
- `project-control/reports/M5-T121-producer-report.md` — this report.

`git status --short` shows exactly the two code files modified (report added). No forbidden path touched: `dxf_import.py`, every `sheet_*` reader module, `pdf_object_streams.py`, `app/scenario/*`, `app/documents/*`, `app/api/*`, `app/main.py`, `app/cad/*`, `tests/api/*`, `apps/`, `packages/`, `docs/`, `requirements*`, `.github/` all unchanged. Zero new dependencies.

## Public API

Functions:
- `list_candidates(doc: SheetDocument | SheetRefusal, page_index: int) -> CandidatesResult | ImportRefusal` — lists the chosen page's CLOSED polylines (>= 3 points) as candidates addressed by their STABLE polyline index, measured in sheet units; bounded display (largest area first, capped), total disclosed; page disclosure + escaped scale notes.
- `build_draft(doc: SheetDocument | SheetRefusal, page_index: int, assignment: RoleAssignment) -> DraftResult | ImportRefusal` — builds a `proposed_massing` DRAFT from the user-assigned building-outline ring, scaled by a scale the SERVICE measures from one user-named edge, through `validate_proposed_massing`; plus a separate provenance block.

Types (defined locally, MIRRORING the dxf_import shapes; their fields differ — page index, a service-measured edge scale, and NO client-supplied measurement):
- `RoleAssignment(building_outline, floors, floor_to_floor_ft, author, scale_candidate, scale_edge, known_length_ft, property_line=None, street_frontage=None)` — DELIBERATELY has no `measured_length` / client-measurement field.
- `Candidate(index, vertex_count, measured)` — `index` is the STABLE polyline index on the page.
- `CandidatesResult(ok, page_index, page_count, user_unit, unit_name, total_closed_rings, candidates, scale_notes, disclosure)`.
- `DraftResult(ok, proposed_massing, provenance)`.
- `ImportRefusal(ok, reason, detail, field=None)`.

Refusal reasons (closed vocabulary): `unreadable_pdf`, `page_out_of_range`, `coordinate_out_of_range`, `bad_candidate`, `bad_edge`, `invalid_scale`, `draft_invalid`.

## Reused dxf_import PUBLIC names (that module is READ-ONLY, never modified)

- `measured_dimensions` (function) — the ring bbox/perimeter/area geometry fits verbatim; imported and reused.
- `DRAFT_SOURCE_LABEL` = "Proposed - not a city record" — reused (identical honesty vocabulary).
- `DRAFT_INPUT_PRECISION` = "imported drawing - not survey-confirmed" — reused.
- `BUILDING_OUTLINE` / `PROPERTY_LINE` / `STREET_FRONTAGE` — reused role-name constants.
- `MAX_DRAWING_TEXT_CHARS` — reused bound.

NOT reused (this module's own, because the values/shapes differ): `DRAFT_INPUT_CLASS = "imported_pdf"` (dxf's is `"imported_drawing"`), `EDITOR_VERSION = "pdf-sheet-import/1"`, `_escape_drawing_text` (the DXF helper is private — the SAME rule is reimplemented locally with its own tests per the packet), and every dataclass.

## Bounds declared

- `MAX_LISTED_CANDIDATES = 200` — the display cap; the TOTAL closed-ring count is always disclosed (`total_closed_rings`); assignment in `build_draft` validates against EVERY closed ring by stable index, so the display cap never hides an assignable ring.
- `MAX_SCALE_NOTES = 50` — scale reference notes are capped; each is escaped + length-bounded (`MAX_DRAWING_TEXT_CHARS = 200`).
- `MAX_KNOWN_LENGTH_FT = 1_000_000.0` — the user-named real-world edge length must be finite, strictly positive and below this.
- `MIN_SCALE_FT_PER_UNIT = 1e-9` / `MAX_SCALE_FT_PER_UNIT = 1e9` — the resolved feet-per-unit scale must be finite and within these; outside refuses `invalid_scale`.

## Per-AS evidence

- **AS-1 (candidates).** Closed rings only, addressed by STABLE polyline index (not a re-numbered 0..k), largest area first, total disclosed, measured in sheet units → `test_candidates_list_closed_rings_by_stable_index_measured_in_sheet_units`. Open polyline disclosed not a candidate → `test_open_polyline_is_disclosed_not_a_candidate`; degenerate (<3-point) closed ring disclosed, never silently absent → `test_degenerate_closed_ring_is_disclosed_not_silently_absent`. Page disclosure (text runs, images, shading/inline-image skip counts) → `test_page_disclosure_counts_text_images_and_skip_counts`. Scale notes listed escaped and NEVER parsed → `test_scale_notes_are_listed_escaped_and_never_parsed`. Out-of-range page and no-closed-ring page are honest typed results → `test_page_out_of_range_is_an_honest_typed_result`, `test_no_closed_ring_page_is_an_honest_typed_result`. Reader refusal → typed escaped `unreadable_pdf` → `test_reader_refusal_maps_to_typed_import_refusal_escaped`. Overflow (huge-but-finite) coords refuse `coordinate_out_of_range`, never emit non-finite (the M5-T108 G5 MEDIUM 1 lesson) → `test_overflow_coordinates_refuse_typed_never_non_finite`.
- **AS-2 (scale).** One user-named edge + real length; the SERVICE measures the edge (exact arithmetic: edge 40 sheet units, known 80 ft → scale 2.0, outline scaled onto _RING) → `test_scale_is_measured_from_geometry_exact_arithmetic`. No client-measurement channel exists on the type → `test_role_assignment_has_no_client_measurement_channel`. Invalid known length (0 / negative / nan / inf / over-bound), bad edge index, degenerate (zero-length) edge, and a non-closed-ring scale candidate each refuse typed → `test_invalid_known_length_refused_typed`, `test_bad_scale_edge_refused_typed`, `test_degenerate_scale_edge_refused_typed`, `test_bad_scale_candidate_refused_typed`.
- **AS-3 (draft).** The ASSIGNED ring scaled with explicit closure through `validate_proposed_massing`, kind stays `'proposed'` → `test_draft_built_from_assigned_ring_scaled_with_explicit_closure`. The draft proves it uses the USER-ASSIGNED ring, not the first / largest (the M5-T108 G4 F1 lesson) — two distinct in-bounds rings, ring A larger at stable index 0, `building_outline=1` → outline is ring B → `test_draft_uses_the_user_assigned_ring_not_first_or_largest`. A contract violation (near-origin local ring) is a typed `draft_invalid` naming the outline field → `test_out_of_bounds_local_ring_refused_by_the_contract`; a bad outline index → `bad_candidate` → `test_bad_building_outline_index_refused_typed`.
- **AS-4 (honesty + provenance).** `input_class="imported_pdf"`, precision / label / page index / frame note / scale inputs / roles all present; no permit / approved / maximum-allowed wording → `test_provenance_block_is_complete_and_honest`. Precision never upgraded (asserted literal; mutant flips it) → same test + `test_mutation_precision_not_upgraded`. Every drawing-derived string escaped and bounded (author, scale notes) → `test_author_drawing_string_is_escaped_in_provenance`, `test_scale_notes_are_listed_escaped_and_never_parsed`.
- **AS-5 (scope).** Pure — module imports only `math`, `dataclasses`, `dxf_import`, `sheet_primitives`, `app.scenario.proposal` (no open/socket/db/network anywhere); two identical calls return equal bodies → `test_no_persistence_two_identical_calls_are_equal`. Zero new deps; unmounted (no route/main change); dxf_import, the reader modules and app/scenario untouched; ruff clean; modularity exit 0; exactly the allowed paths.

## Mutation table (every guard reddens; consuming-namespace mutation asserting the FLIPPED outcome)

| # | AS | Guard | Guarding test | Reddening mutation |
|---|---|---|---|---|
| 1 | AS-1 | closed-ring gate | `test_open_polyline_is_disclosed_not_a_candidate` | `test_mutation_closed_flag_gates_candidates` — `svc._closed_ring_candidates`→all polylines → open ring lists |
| 2 | AS-1 | finiteness guard | `test_overflow_coordinates_refuse_typed_never_non_finite` | `test_mutation_overflow_finiteness_guard` — `svc._measured_is_finite`→True → non-finite area listed |
| 3 | AS-1/AS-4 | output escaping | `test_scale_notes_are_listed_escaped_and_never_parsed` | `test_mutation_scale_note_escaping` — `svc._escape_drawing_text`→identity → raw `\x01` in a scale note |
| 4 | AS-2 | service edge measurement | `test_scale_is_measured_from_geometry_exact_arithmetic` | `test_mutation_edge_is_service_measured_not_supplied` — `svc._measure_edge`→80.0 (a supplied value) → scale 1.0 → `draft_invalid` |
| 5 | AS-2 | known-length guard | `test_invalid_known_length_refused_typed` | `test_mutation_known_length_guard` — `svc._resolve_scale`→lax (no validity check) → known_length_ft=0 accepted |
| 6 | AS-3 | ring selection (first) | `test_draft_uses_the_user_assigned_ring_not_first_or_largest` | `test_mutation_ring_selection_always_first` — `svc._select_ring`→rings[0] → ring A |
| 7 | AS-3 | ring selection (largest) | (same) | `test_mutation_ring_selection_largest` — `svc._select_ring`→max-area → ring A |
| 8 | AS-4 | precision honesty | `test_provenance_block_is_complete_and_honest` | `test_mutation_precision_not_upgraded` — `svc.DRAFT_INPUT_PRECISION`→"survey-confirmed - authoritative" |

## Commands (explicit cwd; verbatim tails) — all [OBSERVED] (local Python 3.11.9; CI py312 is authoritative)

- cwd `services/api`: `python -m ruff check .` → `All checks passed!`
- cwd `services/api`: `python -m pytest tests/drawings/test_sheet_import.py -q` → `31 passed in 1.12s`
- cwd `services/api`: `python -m pytest tests/drawings/test_dxf_import.py tests/drawings/test_dxf_reader.py tests/drawings/test_dxf_roundtrip.py -q` → `90 passed in 2.97s` (forbidden DXF suites unchanged/green — no regression)
- cwd repo root: `python tools/modularity_check.py --check` → `failures 0; warnings 27` / `EXIT=0` (sheet_import.py is NOT in the warning list)

### LOCAL PYTHON note (NOT a defect)
This pack deliberately imports ONLY the public reader value types from `app.drawings.sheet_primitives` (which imports nothing from `app.documents`) and builds every fixture by KEYWORD — it never imports `read_sheet`. So the whole file collects and runs on the sandbox's local Python 3.11.9 WITHOUT the 3.12 PEP 695 collection trap; the orchestrator's `shim311` fallback was not needed. This also satisfies the CONCURRENCY constraint (M5-T120 is editing the reader modules): no reader-internal helper or another test module is imported. CI (3.12) is the authority.

## Deviations

1. **Candidate addressing by STABLE polyline index (a design choice over the DXF re-numbering).** DXF re-numbers candidates 0..k; the packet says PDF candidates are "addressed by their stable polyline index on that page", so `Candidate.index` is the polyline's position in `page.polylines`. The display list is bounded (largest first, capped) but `build_draft` validates the assigned index against ALL closed rings by stable index, so the display cap never makes an assignable ring unreachable. Strictly more honest; never easier to build an invalid draft.
2. **No client-supplied measurement field.** The DXF known-dimension path carries a client `measured_length`; PKT-L requires the SERVICE to measure the named edge itself, so `RoleAssignment` has NO `measured_length`. `_measure_edge` measures the geometry; `test_role_assignment_has_no_client_measurement_channel` proves the type offers no such channel and the mutation table (row 4) proves the geometric measurement is load-bearing.
3. **Draft outline stays in the LOCAL scaled sheet frame and must pass the unchanged `validate_proposed_massing` NYC-2263-bounds check** — identical to the DXF precedent. A genuinely local (near-origin) sheet frame therefore fails `draft_invalid` and is surfaced, never georeferenced; the provenance `frame_note` discloses the local frame. Actual alignment/translation into state plane is the later C2 "alignment to the mapped lot" step (see OPEN QUESTIONS 1).

## OPEN QUESTIONS (owner asleep — recommended answers; orchestrator decides/queues)

1. **Local-frame vs the NYC-2263 contract (the real product tension).** Reusing `validate_proposed_massing` unchanged forces the SCALED sheet outline to fall inside NY state plane bounds, yet a real architect sheet is a LOCAL frame (small coordinates) — so a real, un-aligned sheet draft would `draft_invalid` today. This mirrors the accepted DXF behavior exactly (DXF DISC-A/B). **Recommendation:** keep the honest reuse here (draft is disclosed as a local frame; alignment is a later step), and treat the actual sheet→state-plane translation (a fit/offset the user confirms against the mapped lot) as the next C2 alignment packet — do NOT weaken the massing contract's bounds check. Recorded as a DISCOVERY.
2. **`kind` vs the phased-plan wording.** The phased plan says C3 provenance `kind=imported_pdf`, but the B0 contract requires `provenance.kind == "proposed"` (a proposed building is the THIRD input class). The packet objective resolves this: the massing block's `kind` stays `"proposed"`; the SEPARATE provenance block carries `input_class="imported_pdf"`. Implemented exactly that way. **Recommendation:** no change; the phased-plan line is shorthand for the input_class, not the contract kind.

## DISCOVERIES (for the orchestrator to record in docs/DISCOVERY_BACKLOG.md at the seam)

- **DISC-A (sheet→state-plane alignment is the missing C2 step).** The draft is a LOCAL scaled sheet frame; to become a real proposal aligned to the mapped lot it needs a user-confirmed translation/fit into EPSG:2263 (with any discrepancy shown, never auto-reconciled — phase-C C2 wording). Until then, only sheet frames whose scaled coordinates already fall in NYC bounds pass the contract. Same tension as DXF DISC-A/B.
- **DISC-B (mount seam owns the route + rate limit + pre-render finiteness guard).** This packet is UNMOUNTED and pure. A later mount packet must add the flag-gated route, a per-caller rate limiter, an `allow_nan=False` pre-render guard, and body/upload ceilings — exactly the PKT-H items the DXF mount carries. The service already refuses non-finite measured dimensions typed, so the route only needs the defense-in-depth pre-render guard.
- **DISC-C (scale-note extraction is disclosure-only by design).** Printed scale notes ("SCALE: 1/8\"=1'-0\"") are listed escaped as reference only and never parsed. A future assist could OFFER a printed scale as a suggestion the user still confirms against a measured edge, but must never auto-apply it (the measured edge stays authoritative). Recorded for C4 (ask-only-what-is-unresolved).

## AS-5 scope confirmation

Pure, offline, unmounted; zero new dependencies; the module imports only stdlib + already-admitted internal modules; exactly the three allowed paths changed; `dxf_import.py`, the reader modules and `app/scenario` are untouched; ruff clean; modularity exit 0.

END-OF-REPORT
