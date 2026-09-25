# M5-T106 producer report — D-087 massing pre-wiring 2 (DB-069 a-d; DB-061 b)

Producer: 3d-massing-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t106` (branch `task/M5-T106-massing-prewiring-2`).
Claim seam / parent: `110894295ec97c1d7cb87deb3421a628b526b66b`.
Files changed (exactly the allowed paths):
- `services/api/app/scenario/massing_model.py`
- `services/api/tests/scenario/test_massing_model.py`
- `project-control/reports/M5-T106-producer-report.md` (this file)

Scope: `git diff --stat` = 2 code files (+282 / -41); no forbidden path (proposal.py, scene_assembler.py,
the cad writers, connectors, api routes, app/main.py, requirements, apps/, packages/, .github/ all untouched).
No public name or signature changed — the parallel M5-T107 scene assembler codes against the same public
API (`build_massing_model`, `build_from_generated_option`, `MassingModel`, `MassingModelError`, the
`SOURCE_*`/`GENERATOR_VERSION`/`GEOMETRY_VERSION` constants). The only signature touched is the PRIVATE
`_prepare_ring`, which gained a keyword-only `nyc_range_check: bool = False` (default preserves all existing
callers). Unwired: `grep` confirms the only importer of the module is `tests/scenario/test_massing_model.py`
(no production importer). Zero new dependencies (import change is `shapely.errors.GEOSException` →
`shapely.errors.ShapelyError`, both from the already-admitted shapely).

## Per-acceptance-scenario evidence

- AS-1 (raw range check) — PASS. The lot NYC EPSG:2263 range check now runs on the RAW vertices in
  `_prepare_ring` (`_require_raw_vertices_in_nyc_bounds(raw, field)`, called with `nyc_range_check=True`
  from `_lot_polygon`), AFTER the whole magnitude pass but BEFORE the collinear collapse. An out-of-range
  collinear spike (x=2e6 on a straight edge, under the 1e8 magnitude bound) is refused
  `lot_ring_out_of_nyc_bounds` (field `lot_ring`) instead of being silently collapsed away and never checked
  (`test_t106_as1_out_of_range_collinear_spike_in_lot_is_refused`). The magnitude-first ordering is preserved:
  a ~1e154 overflow lot still refuses `coordinate_out_of_range`/`lot_ring[0]`
  (`test_t106_as1_near_overflow_lot_still_refuses_magnitude_first`, and the accepted
  `test_t088_as4_near_overflow_lot_ring_is_a_typed_refusal` still green). Mutation `raw_after_collapse`
  (check the COLLAPSED ring) → RED.

- AS-2 (typed shapely errors) — PASS. `_wrap_geos_errors` now catches `shapely.errors.ShapelyError` (the
  shapely base class), so `GEOSException` AND its non-GEOS siblings (`TopologicalError`, `GeometryTypeError`,
  `DimensionError`, ...) become typed `geometry_engine_error`. A non-GEOS `TopologicalError` raised on a
  build path is wrapped (`test_t106_as2_non_geos_shapely_error_is_wrapped`, which also asserts the sibling
  is genuinely a `ShapelyError` but NOT a `GEOSException`). The wrap stays selective — a `MassingModelError`
  (a `ValueError`, disjoint from `ShapelyError`) passes through unwrapped with its own reason
  (`test_t106_as2_typed_refusal_still_passes_through_the_widened_wrap`; accepted
  `test_t098_as3_*` still green: GEOSException is a ShapelyError subclass so it is still caught). The module
  and decorator docstrings are corrected to the exact truth. Mutation `geos_only` (`except GEOSException`) → RED.

- AS-3 (probes) — PASS. Two new probes close the M5-T098 G4 ADVISORY-A gap:
  `test_t106_as3_lot_in_x_range_out_of_y_range_is_refused` (all vertices in the X range, out of the Y range)
  and `test_t106_as3_lot_later_vertex_out_of_range_is_refused` (vertex[0]/[1] in range, a later vertex out).
  Both refuse `lot_ring_out_of_nyc_bounds`/`lot_ring`. Mutation `drop_y` (drop the `and NYC_Y_MIN <= y <= ...`
  clause) → RED via the in-X/out-of-Y probe; mutation `vertex0_only` (`for x, y in vertices[:1]`) → RED via
  the later-vertex probe.

- AS-4 (bounded echoes) — PASS. A new `_preview(value, limit=MAX_ECHO_CHARS)` (MAX_ECHO_CHARS=120) returns
  a within-bound `repr` verbatim, else the first 120 chars + a compact `...<+N chars>` marker. Applied to
  every caller-input echo: the non-finite vertex echo in `_prepare_ring`, the height/count echoes in
  `_expand_floor_stack`, the `source` echo in `build_massing_model`, and the engine-exception echo in the
  wrap. A 200,000-char vertex string now yields a bounded (<=300 char) refusal that does NOT contain the full
  pasted value (`test_t106_as4_lot_vertex_refusal_echo_is_bounded`); the `source` echo is bounded the same
  way (`test_t106_as4_invalid_source_refusal_echo_is_bounded`); `_preview` is transparent for small values so
  valid-input messages and the goldens are unchanged (`test_t106_as4_preview_is_transparent_for_small_values`).
  Mutation `unbounded_echo` (`if True: return text`, i.e. always the raw repr) → RED (both echo tests).

- AS-5 (DB-061 b, mutant ME) — PASS (already pinned; re-confirmed). The scan-unit charge order is pinned by
  the accepted `test_t098_as4_scan_units_charged_before_the_inner_scan` (counts `_point_in_triangle` calls:
  0 when the `m-3` charge is BEFORE the inner scan). Mutant ME (charge the `m-3` units AFTER the scan) → RED
  ("assert 5 == 0"; the 5-candidate scan ran before the overspend). No new test added: ME is behaviour-
  distinguishable and already killed by the existing test, so DB-061 (b) is discharged. (The M5-T088 G4
  "behaviour-free" characterization of ME was superseded by T098's finer pit-call discriminator.)

- AS-6 (scope) — PASS. Both accepted goldens are byte-identical
  (`sha256:b7fa9862...5133b` 1-floor RECT, `sha256:e23b5cbc...a6c5` 5-floor stack) — asserted in the existing
  `test_as1_json_serializable_and_deterministic_golden`, `test_t088_as5_five_floor_stack_golden`,
  `test_t098_as2_in_range_lot_is_unaffected_golden_unchanged`, and a new `test_t106_as6_valid_input_goldens_byte_identical`.
  The full `tests/scenario` suite is 722 passed (was 720 accepted + 10 added − 8... net: all green, existing
  tests unchanged apart from added tests; no existing test edited). Zero new deps; unwired; exactly the
  allowed paths; `modularity_check --check` exit 0.

## DB-069 (a)-(d) closure table

| Rider | Source finding | Closure | Guard / test |
|---|---|---|---|
| DB-069 (a) | G3 ADVISORY-1: lot NYC check ran on the collinear-collapsed ring; a collinear spike (x=2e6) escaped | CLOSED | raw-vertex check before collapse; `test_t106_as1_*`; mutant `raw_after_collapse` RED |
| DB-069 (b) | G3 ADVISORY-2 = G5 F-LOW-1: `_wrap_geos_errors` caught only `GEOSException`; siblings escaped untyped; docstrings over-claimed | CLOSED | `except ShapelyError`; docstrings corrected; `test_t106_as2_non_geos_shapely_error_is_wrapped`; mutant `geos_only` RED |
| DB-069 (c) | G4 ADVISORY-A: the lot check's Y clause and later vertices were under-probed | CLOSED | in-X/out-of-Y + later-vertex-out probes; mutants `drop_y`, `vertex0_only` RED |
| DB-069 (d) | G5 F-LOW-2: refusal messages echoed raw caller input unbounded (200k char → 200,055 char message) | CLOSED | `_preview`/`MAX_ECHO_CHARS` on every caller-input echo; `test_t106_as4_*`; mutant `unbounded_echo` RED |
| DB-061 (b) | G4 ADVISORY-2 (mutant ME): charge-before-vs-after indistinguishable | DISCHARGED (T098) | existing `test_t098_as4_*`; ME re-confirmed RED in-process |
| DB-069 (e) | NYC_2263_* imported from proposal.py though outside its `__all__` | NOTE only (unchanged; proposal.py forbidden) | explicit import is unaffected by `__all__`; single source of truth |
| DB-069 (f) | exclusive-bound / check-after-Polygon mutants survive but behaviour-free | NOTE only | generous unit guards; immaterial (matches T098 G4 ADVISORY-B) |

## Mutation table (in-process, mutate the consuming namespace; one fresh interpreter per mutant)

Harness: text-mutate a copy of `massing_model.py`, inject into `sys.modules["app.scenario.massing_model"]`
+ set the `app.scenario` attr BEFORE the test imports, purge every `*massing_model*` sys.modules key, run
the exact target test(s). Baseline (unmutated source injected) is GREEN (faithful harness); every mutant RED.

| Mutant | Change (consuming namespace) | Target test | Result |
|---|---|---|---|
| baseline | none (harness faithfulness) | all 10 t106 tests + `test_t098_as4_*` | GREEN — 11 passed |
| raw_after_collapse | NYC check on the COLLAPSED `ring`, not raw | `test_t106_as1_out_of_range_collinear_spike_in_lot_is_refused` | RED |
| geos_only | `except GEOSException` (not ShapelyError) | `test_t106_as2_non_geos_shapely_error_is_wrapped` | RED |
| drop_y | drop `and NYC_2263_Y_MIN <= y <= NYC_2263_Y_MAX` | `test_t106_as3_lot_in_x_range_out_of_y_range_is_refused` | RED |
| vertex0_only | `for x, y in vertices[:1]` | `test_t106_as3_lot_later_vertex_out_of_range_is_refused` | RED |
| unbounded_echo | `_preview` always returns raw `repr` | `test_t106_as4_lot_vertex_refusal_echo_is_bounded` + `_invalid_source_*` | RED (2 failed) |
| me_charge_after | charge `m-3` AFTER the inner scan | `test_t098_as4_scan_units_charged_before_the_inner_scan` | RED |

## Commands (explicit cwd; [OBSERVED] verbatim tails)

- [OBSERVED] cwd `services/api`: `python -m ruff check app/scenario/massing_model.py tests/scenario/test_massing_model.py` → `All checks passed!`
- [OBSERVED] cwd `services/api`: `python -m ruff check .` → `Found 6 errors` — ALL 6 are pre-existing E501 in
  FORBIDDEN placeholder files seeded for the parallel packets (`app/api/v1/dxf_import_api.py`,
  `app/api/v1/export_api.py`, `app/api/v1/scene_api.py`, `app/cad/export_service.py`,
  `app/drawings/dxf_import.py`, `app/scenario/scene_assembler.py`). None is a M5-T106 file; my two files are
  clean. These belong to M5-T107/T108/T109 and are out of my scope.
- [OBSERVED] cwd `services/api`: `python -m pytest tests/scenario -q` → `722 passed in 20.67s`.
- [OBSERVED] cwd repo root: `python tools/modularity_check.py --check` → `selected 497 files; failures 0;
  warnings 27` … `EXIT=0`. `massing_model.py` is a `review_signal` warning ("above the justification
  threshold; record a cohesion justification in review") — warning only, not a failure (see cohesion note).
- [OBSERVED] cwd `services/api`: mutation harness — baseline `11 passed` (VERDICT OK); `raw_after_collapse`,
  `geos_only`, `drop_y`, `vertex0_only`, `unbounded_echo` (2 failed), `me_charge_after` each `pytest_rc=1`
  RED (VERDICT OK).
- [OBSERVED] cwd repo root: `code_graph/query.py --no-regen impact` → `STALE ... refusing to serve` (parallel
  packets changed files); the unwired conclusion is verified directly in source instead:
  `grep -rn massing_model app/` = NONE (no production importer); the only importer tree-wide is
  `tests/scenario/test_massing_model.py`.

## Modularity cohesion note

`massing_model.py` is 958 lines (SLOC above the 750 justification threshold, under the 1000 hard cap;
`modularity_check --check` exit 0, warning only). The file is a single cohesive responsibility: the
deterministic server-side massing truth object — its coordinate frame, ring preparation + fail-closed input
guards, ear-clipping triangulation, prism-mesh construction, provenance, and the two builders. The M5-T106
delta is +~64 lines of the same responsibility (a raw-vertex range guard, a widened engine-error boundary,
and a bounded-echo helper for the module's own refusal messages) — no new domain, storage, serialization,
external I/O, CLI/API or presentation concern was introduced. A split would separate the guards from the
builder that is their sole caller and would break the golden-content cohesion; it is not warranted in this
before-wiring packet and would exceed its scope. Recommend revisiting the module boundary only if a future
packet adds a genuinely new responsibility (e.g. mesh export) rather than growing this one.

## Deviations

- None to accepted behaviour. No existing test was edited (unlike M5-T098, which had to force-edit
  `test_t088_as4_coordinate_magnitude_bound_is_inclusive`). That test's `lot[1]=1e8+0.5` →
  `coordinate_out_of_range`/`lot_ring[1]` assertion is PRESERVED because the new lot NYC check is a second
  pass AFTER the whole magnitude pass, so a later-vertex magnitude violation still wins (verified: 722 passed).
- `_require_lot_ring_in_nyc_bounds` (M5-T098's post-collapse helper) was replaced by
  `_require_raw_vertices_in_nyc_bounds` (raw, pre-collapse). Same reason string and `field="lot_ring"`, so all
  accepted T098 lot-range tests pass unchanged; it is private and had no other caller.

## DISCOVERIES (for the orchestrator to record in docs/DISCOVERY_BACKLOG.md; not fixed in-packet)

- D-OBS-1 (scope-neighbor, non-blocking): six FORBIDDEN placeholder files seeded at the wave-10 contract seam
  for M5-T107/T108/T109 (dxf_import_api, export_api, scene_api, export_service, dxf_import, scene_assembler)
  each trip ruff E501 on their one-line docstring (>100 chars). They fail the api ruff job at the seam head;
  the respective producers must replace them. Flagged so a full-tree ruff run is not misread as this packet's.
- D-OBS-2 (wiring precondition, carry-forward): the same unbounded-`repr` echo pattern DB-069 (d) fixes here
  still exists upstream at `proposal.py:250` (`got {vertex!r}`) and is FORBIDDEN in this packet. The PKT-E /
  connector wiring packet that feeds untrusted user/MapPLUTO geometry should apply the same bounded preview
  there (paired note already in M5-T098 G5). Also still open for the wiring packet: DB-061 (i) route-level
  cancellable job + wall-clock timeout + rate limit, and tenant/auth on the three provenance ids.
- D-OBS-3 (advisory, non-blocking): the code-graph cache was STALE at this seam (parallel packets), so
  `query.py --no-regen impact` could not serve; the unwired conclusion was verified in source. If the
  orchestrator wants a fresh graph-backed impact record for the M5-T107 wiring, regenerate at the accept seam.

END-OF-REPORT
