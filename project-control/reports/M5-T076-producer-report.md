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

---

## [ORCH-HARVEST] Authorized-orchestrator harvest transcript (2026-09-23, cwd services/api, wt-m5t076)

- `python -m ruff check .` → **All checks passed!** (exit 0).
- `python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q`
  → **40 passed** — every [PREDICTED PASS — pytest harvest below] row above is hereby elevated
  to OBSERVED. Identity: in-wt commit cherry-picked to b8dc1044, ALL-MATCH x5 (LF-normalized).
  CI on the pushed head is the remaining backstop; max_envelope.py byte-untouched (its blob is
  unchanged across the material — the AS-4 bound held).

---

## Rework (G3 F1–F5)

The G3 review (`project-control/reports/M5-T076-G3.md`) returned **FAIL** with five required
corrections. This section appends the rework; nothing above is rewritten. Same producer
(backend-engineer), base `672c5743` (the G3-FAIL seam). Hard bounds re-verified below:
`max_envelope.py` byte-untouched, route still unmounted, no new dependency, the display-only
`mappluto_lot_outline` still never imported (now asserted directly by a test, not inferred).

### F3 disclosures the original submission owed and did not make

Stated plainly, before the fix list:

1. **The original submission proved AS-2 on a SYNTHETIC rectangle, not on a recorded fixture.**
   Both test files built the same inline axis-aligned rectangle (`_RECT_ESRI`) and labelled it with
   BBL `1008350041` — which is the BBL of the *recorded* fixture `MPG02_lot_single_1008350041.json`.
   No recorded fixture was read. That was a real gap against the packet's binding TESTS clause, and
   the original report did not flag it as a deviation. It should have.
2. **The packet's F01/MPG02 "fitted-candidate-reachable" premise is FALSE.** The recorded MPG02 lot
   (Empire State Building) is a 6-vertex NON-axis-aligned polygon. Run end to end it derives
   successfully (6 authoritative segments, recorded provenance) and the engine then honestly
   refuses placement — `lot_geometry_unsupported`, reason "the lot-line geometry is not an
   axis-aligned rectangle (a diagonal or zero-length segment); unsupported for candidate placement
   in slice 1". The named proof fixture cannot produce the named proof. That path is now asserted
   by name (`test_recorded_single_lot_derives_but_is_honestly_unfittable`) rather than uncovered.
3. **The AS-2 fitted proof is FIXTURE-CONDITIONAL.** It holds for the synthetic rectangular class
   only — the one class the accepted engine can fit (`_lot_rectangle`: axis-aligned ring whose bbox
   area matches the recorded area at rel_tol 1e-9). It does NOT show that real NYC lots fit; the
   NYC grid is rotated in EPSG:2263, so derived-but-unfittable is the dominant real-world outcome.
   `test_derived_path_yields_fitted_candidate`'s docstring now says this in the test itself.
   (The evidence map carries the same overstatement — F6 — but it is outside this packet's allowed
   paths, so it is left for the orchestrator, not silently edited.)

### Per-fix summary

- **F1 (MAJOR, fixed)** — `max_envelope_api.py:361-384`: the derivation hop is now wrapped in the
  route's standard `try/except Exception` →
  `logger.error("max_envelope_v1 unexpected_error stage=derive_lot_geometry correlation_id=%s")` +
  `_internal_error_500(correlation_id)`, matching the registry guard (`:340`) and engine guard
  (`:447`). The provider resolution sits inside the guard too. Test:
  `tests/api/test_max_envelope_api.py:643 test_500_when_the_lot_geometry_provider_raises_unexpectedly`
  injects a provider raising `ValueError` and asserts the TYPED `(500, "internal_error")` body, the
  `X-Correlation-ID` header, matrix membership, and that neither the exception message nor the type
  leaks. MUTATION-VERIFIED: with the guard removed the test fails
  `assert (500, None) == (500, 'internal_error')` — the bare Starlette 500 the review reproduced.
- **F2 (MAJOR, fixed)** — `max_envelope_api.py:162-180` (`_should_derive_lot_geometry`, guard at
  `:172-176`): derivation
  now runs ONLY when `lot_line_segments` is ABSENT, `None`, or an EMPTY LIST. Any other type stays
  on the typed-refusal path, so `_build_lot_context`'s `lot.lot_line_segments must be an array` 422
  survives with or without a BBL. Tests:
  `test_malformed_segments_refuse_identically_with_and_without_a_bbl` (parametrized over
  `"abc" / 42 / {...} / True`) asserts the with-BBL and without-BBL responses are the SAME typed 422
  body modulo correlation id, field `lot.lot_line_segments`, and that the provider is neither
  resolved nor called; `test_absent_or_null_segments_with_a_bbl_still_derive` asserts all three
  "no geometry supplied" shapes still derive and fit. MUTATION-VERIFIED: restoring the old guard
  turns the with-BBL case into `200` (`assert (200, None) == (422, 'validation_error')`).
- **F3 (MAJOR, fixed)** — the RECORDED packs are now exercised, through the real analyzer and the
  real route:
  - `MPG02_lot_single_1008350041.json` — unit
    (`test_recorded_single_lot_fixture_derives_its_real_exterior_ring`: 6 segments, closed ring,
    real 2263 magnitudes, recorded `Version` "26v1") and route
    (`test_recorded_single_lot_derives_but_is_honestly_unfittable`: derived outcome `derived` AND
    the honest `lot_geometry_unsupported` placement whose detail is asserted EQUAL to the engine's
    own verbatim reason, with no derivation reason appended since there was no derivation failure).
  - `MPG06_lot_holes_1000010010.json` — `test_recorded_holed_lot_excludes_every_hole_vertex`: the
    canonical form is one 320-vertex exterior ring + two hole rings totalling 143 vertices; the
    derivation cuts exactly 320 segments whose endpoint set EQUALS the exterior vertex set and is
    disjoint from all 143 hole vertices. MUTATION-VERIFIED: walking all rings instead of
    `polygon[0]` yields 463 segments and reddens it.
  - `MPG07_lot_multipolygon_4142600001.json` — unit + route over-cap classification (see F4).
  - Both recorded-fixture loaders assert the pack is still `classification == "raw"` and a `live `
    capture, so a synthetic substitution can never pass as recorded evidence.
- **F4 (MODERATE, fixed)** — over-cap is now a DISTINCT outcome, not `invalid_geometry`:
  `LotGeometryDerivationOutcome.GEOMETRY_OVER_CAP` (`lot_geometry_derivation.py:99`).
  `_exterior_ring_segments` (`:144-181`) returns `(segments, reason)` where the reason is
  `_RING_DEGENERATE` or `_RING_OVER_CAP` (`:138-141`), and `derive_lot_line_segments` (`:273-291`) emits
  separate details. The over-cap detail states the official data is NOT at fault: "the official
  MapPLUTO geometry for this BBL is valid, but its exterior ring(s) yield more lot-line segments
  than this route's cap allows (800); the official data is not at fault - our own cap is the
  binding constraint - so no lot geometry is derived (never a truncated ring)". Fail-closed is
  unchanged (segments `None`, provenance `None`, reason carried into the placement detail). Tests:
  the recorded MPG07 case (valid assessment, 2 polygons, 3130 exterior vertices → over-cap at 800,
  and DERIVED at cap 4000 — proving the source is fine), the renamed
  `test_over_cap_ring_is_fail_closed_and_typed_apart_from_invalid`,
  `test_over_cap_and_unusable_geometry_never_conflate_the_two_causes`,
  `test_ring_cutter_reports_degenerate_and_over_cap_separately` (the defensive degenerate branch,
  asserted on the private cutter because an assessment-valid degenerate ring cannot be produced
  through the real analyzer), and the route-level
  `test_recorded_multipolygon_is_reported_over_cap_not_invalid`. MUTATION-VERIFIED: routing
  over-cap back to `INVALID_GEOMETRY` reddens the recorded-fixture test.
- **F5 (MODERATE, fixed)** — `lot_geometry_derivation.py:310-328`: the resilient client is now
  constructed at PROVIDER-RESOLUTION time (which the route performs on the event loop) and the
  returned closure constructs nothing; the DB-039(i) doctrine comment mirrors
  `proposal_checks_api.py:218-220`. Test:
  `test_production_provider_builds_its_client_on_resolution_not_per_call` (a stub client counts
  constructions: one after two resolutions, zero more across closure calls). MUTATION-VERIFIED:
  moving construction back inside the closure reddens it (`[] == ['constructed']`).
- **F7 (MINOR advisory, fixed)** — the two overstating test claims:
  `test_with_segments_is_byte_identical_and_never_derives` now injects the provider through a
  getter spy and asserts `resolutions == []` as well as `calls == []`, so its "NEVER resolved or
  called" claim is actually proven; and the AS-1 display-connector comment is relabelled as the
  INDIRECT magnitude proxy it is, pointing at the new DIRECT
  `test_module_never_imports_the_display_only_outline_connector` (AST-parses the module's own import
  list and asserts no `mappluto_lot_outline`, plus that the 2263 connector IS imported).
- **F6 and F8: NOT attempted, by instruction.** F6's evidence-map wording and the web client's
  missing `lot.bbl` are outside this packet's allowed paths (the disclosure duty is discharged in
  prose above). F8's request-scoped budget is a mount-seam decision (DB-045(b)/B-001), not a change
  made here.

### Self-checks (all OBSERVED in the worktree, cwd `services/api` unless noted)

```
$ python -m ruff check .
All checks passed!

$ python -m pytest tests/scenario/test_lot_geometry_derivation.py tests/api/test_max_envelope_api.py -q
55 passed in 3.24s

$ python tools/modularity_check.py --check        # cwd = repo root
selected 476 files; failures 0; warnings 22

$ python -m pytest tests/api tests/scenario -q     # wider regression, not required by the packet
1320 passed in 36.20s
```

(40 → 55 tests in the two packs: +15 new; two existing tests renamed/strengthened, none removed.)

### Bounds re-verified

```
$ git diff 672c5743 -- services/api/app/scenario/max_envelope.py | wc -c
0
$ git rev-parse 672c5743:services/api/app/scenario/max_envelope.py
f0abf88479d078d8ec7e88d4c2b1942fd69c040d
$ git hash-object services/api/app/scenario/max_envelope.py
f0abf88479d078d8ec7e88d4c2b1942fd69c040d
```

Engine BYTE-UNTOUCHED (AS-4). Route still UNMOUNTED
(`test_route_is_unmounted_in_the_real_app` unchanged and passing). No new dependency: the only new
imports are stdlib `ast`, `json`, `pathlib` in the two TEST files. `mappluto_lot_outline` is still
never imported — now asserted directly. `git diff --numstat` touches exactly the four code paths:
`max_envelope_api.py` 35/13, `lot_geometry_derivation.py` 66/27, `test_max_envelope_api.py` 219/8,
`test_lot_geometry_derivation.py` 262/13.

### Limitations and honest residue

- The five mutation checks above were run in a THROWAWAY scratchpad harness that edited the file,
  ran pytest, and restored from a byte-copy; both production files were verified identical to their
  pre-mutation copies afterwards (`diff -q` → no output). No mutation is present in the commit.
- Derived-but-unfittable remains the dominant real-world outcome until the engine supports
  non-axis-aligned lots. This packet makes that outcome HONEST and covered; it does not fix it.
- `GEOMETRY_OVER_CAP` is a new value in the `derived_lot_geometry.outcome` vocabulary. Nothing
  consumes that block yet (the route is unmounted and the web client does not send `lot.bbl`), so
  there is no consumer to update; a future consumer must treat it as distinct from
  `invalid_geometry`.
- The `_RING_DEGENERATE` branch is defensive: no recorded or synthetic fixture produces a canonical
  geometry that is both assessment-valid and degenerate, so it is asserted at the private-helper
  level rather than end to end.

END-OF-REPORT (rework)
