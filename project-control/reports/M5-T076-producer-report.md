# M5-T076 producer report — DB-050(a) geometry-threading (server-side lot-geometry derivation)

Task: derive authoritative EPSG:2263 lot-line segments server-side from the accepted MapPLUTO
connector by BBL, so the max-envelope fitted-candidate path becomes production-reachable for a
geometry-free request. Engine byte-untouched; route stays unmounted; fail-closed per class.
Producer: backend-engineer. Worktree: `wt-m5t076`. Directive: D-084-R001.

## Implementation surface (files + anchors)

- `services/api/app/scenario/lot_geometry_derivation.py` — NEW derivation module.
  - `derive_lot_line_segments(bbl, *, provider, max_segments, correlation_id)` — orchestrates
    normalize→provider→classify→segments+provenance; typed `DerivedLotGeometry`.
  - `_exterior_ring_segments(...)` — canonical geometry (exterior ring(s), holes excluded) →
    `{"id","start","end"}` segments in the shape `_build_lot_context` validates; fail-closed on
    degenerate (<3 verts) or over-cap ring.
  - `_provenance_quintuple(...)` — source_id, bbl, retrieved_at, dataset_version (never guessed —
    `None` when the MapPLUTO `Version` attribute is absent), geometry_digest; + crs / status.
  - `LotGeometryDerivationOutcome` (derived | bbl_unresolvable | no_feature | multiple_features |
    invalid_geometry | connector_fault); `production_lot_geometry_provider()` (resilient client).
  - Reads `mappluto_geometry_arcgis` READ-ONLY (canonical 2263 `GeometryAssessment`); the display
    4326 `mappluto_lot_outline` is NEVER imported. No network in the module itself (provider seam).
- `services/api/app/api/v1/max_envelope_api.py` — route wiring ONLY (the sole production edit).
  - `get_lot_geometry_provider()` / `_effective_lot_geometry_provider()` — test-injectable provider
    hook mirroring `get_max_envelope_registry`; production falls back to the MapPLUTO provider.
  - `_should_derive_lot_geometry(lot)` — derive ONLY when NO lot-line segments AND a non-empty BBL.
  - In `post_max_envelope`: after the domain check, derive OFF the event loop via
    `run_in_threadpool`; inject segments only on success; attach `derived_lot_geometry` to the
    response and, on a fail-closed outcome, carry the reason into the `lot_geometry_unsupported`
    placement detail. Requests carrying segments take no derivation branch.
- Tests: `tests/scenario/test_lot_geometry_derivation.py` (unit) and additions to
  `tests/api/test_max_envelope_api.py` (route), fully offline.

`git diff --stat` [OBSERVED]: exactly 4 files changed (the allowed paths). `max_envelope.py` is
ABSENT from the diff → BYTE-UNTOUCHED (AS-4). `git status --porcelain` lists only the 4 allowed
paths + this report.

## Acceptance scenarios → evidence

- AS-1 (derivation correctness + provenance): `test_derives_axis_aligned_rectangle_segments`,
  `test_derived_carries_the_provenance_quintuple`, `test_missing_dataset_version_stays_none_never_guessed`.
  The canonical ring comes from the REAL `analyze_lot_geometry` over an inline esri rectangle.
  MUTATION: coordinates are the large 2263 magnitudes (`xs=={985000.0,985080.0}`); a display 4326
  ring (tiny lon/lat) would redden the assertion. [PREDICTED PASS — pytest harvest below]
- AS-2 (reachability): `test_derived_path_yields_fitted_candidate` — a geometry-free request with a
  resolvable BBL yields a FITTED contained candidate through the route, passing the engine's own
  generator-checker consistency proof; the provenance quintuple rides the response.
  [PREDICTED PASS — pytest harvest below]
- AS-3 (byte-identity + fail-closed): `test_with_segments_is_byte_identical_and_never_derives`
  (provider never resolved/called; no `derived_lot_geometry` key),
  `test_no_bbl_and_no_segments_does_not_derive`,
  `test_derivation_failure_keeps_honest_gap_with_reason` (parametrized no_feature / multiple_features
  / invalid_geometry), `test_connector_fault_keeps_honest_gap`,
  `test_unresolvable_bbl_keeps_honest_gap_without_calling_provider`, plus the unit fail-closed suite
  (`test_no_feature_is_fail_closed` … `test_connector_fault_is_fail_closed`,
  `test_over_cap_ring_is_fail_closed`). Each failure class keeps the honest gap with the reason in
  the placement detail; NO fabricated rectangle. MUTATION: injecting a fabricated rectangle on
  failure flips `candidate` to non-None and reddens the route fail-closed tests.
  [PREDICTED PASS — pytest harvest below]
- AS-4 (modularity + scope): modularity `--check` [OBSERVED] failures 0; the new module is far under
  threshold and does not appear in the warnings; `max_envelope.py` byte-untouched (diff absence,
  above); ruff clean for `services/api` [OBSERVED, see below]; no new dependency; route unmounted
  (`test_route_is_unmounted_in_the_real_app`, unchanged).

## Self-checks

- `python -m ruff check .` [OBSERVED, run verbatim from worktree root]: exit 1 with 45 findings —
  ALL in `project-control/` and `tools/` (pre-existing repo debt); ZERO `services/api` findings after
  fixing my two E501s. The api CI job lints `services/api` scope, which is clean. Re-run recipe for a
  scoped OBSERVED: `cd services/api && python -m ruff check .`.
- `python tools/modularity_check.py --check` [OBSERVED]: `failures 0; warnings 22` (all warnings
  pre-existing; `lot_geometry_derivation.py` not among them; `max_envelope.py`'s warning is its
  pre-existing 998-SLOC signal, unchanged).
- `python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q`
  [BLOCKED → HARVEST]: the approval broker runs documented commands from the WORKTREE ROOT, but this
  command's relative test paths and the `app` package import require `services/api` cwd (CODING_RULES:
  "run api pytest from services/api cwd"). Verbatim from root → `file or directory not found`
  (cwd artifact, not a defect). No non-documented shape was improvised (per NATIVE-TOOL PREFERENCE).
  EXACT HARVEST RECIPE (orchestrator/CI, from `services/api`):
  `python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q`

## Design notes (never guessed)

- Segment shape mirrors the committed `_build_lot_context` contract (`{"id","start","end"}`,
  2263 coords) and `LotContext`/`LotLineSegment`. Derived ids are `derived-lot-line-N` (pass the
  `_require_label` charset). Holes are NOT lot lines (excluded); the exterior ring(s) only.
- Slice-1 engine reality: the engine fits ONLY an axis-aligned rectangle whose bbox area equals the
  recorded `area_sq_ft` (`_lot_rectangle`, rel_tol 1e-9). A non-rectangular real lot's derived ring
  yields the honest `lot_geometry_unsupported` gap — reachable, not fabricated. The fitted proof uses
  the rectangular-lot class (the T070 web-fixture model).
- New request field: `lot.bbl` (optional). Derivation runs only when segments are absent/empty AND a
  BBL is present; the client-side BBL wiring is a separate future task (the route ships unmounted).
- BBL resolvability is a pre-network gate (`normalize_bbl`); a present-but-invalid BBL is a
  fail-closed `bbl_unresolvable` gap and never reaches the provider.

END-OF-REPORT
