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
  a within-bound `repr` verbatim, else the first 120 chars + a compact `...<+N chars>` marker. In round 1
  this was applied to these caller-input echoes: the non-finite vertex echo in `_prepare_ring`, the
  height/count echoes in `_expand_floor_stack`, the `source` echo in `build_massing_model`, and the
  engine-exception echo in the wrap. (ROUND 2 CORRECTION: the round-1 phrase "every caller-input echo" was an
  over-claim flagged by G3 ADVISORY-1 and G4 ADVISORY-2 - the re-echoed B0 error at the validation boundary
  and the generated-option no-candidate `detail` were NOT yet bounded; the Round 2 section below closes both,
  so the exact and complete bounded set is stated there.) A 200,000-char vertex string now yields a bounded
  (<=300 char) refusal that does NOT contain the full
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

---

## Round 2 — one bounded round of required corrections (G3 ADVISORY-1, G4 ADVISORY-1/2, G5 MED-1/LOW-1/INFO)

Round 1 PASSED all three gates (G3 geospatial, G4 qa, G5 security). Their advisories are BEFORE-WIRING
preconditions for the scene packet M5-T107 (which feeds USER geometry into `build_massing_model`), so the
orchestrator folded them into ONE bounded corrections round. This round touches EXACTLY the same two code
files plus this report; `proposal.py:250` stays FORBIDDEN (its `{vertex!r}` echo remains the wiring packet's
D-OBS-2 root); no public name or signature changed (only `_is_finite_number`, `_preview`, the B0
`try/except` body, `build_from_generated_option`'s no-candidate branch, and the module docstring — all
private/internal); the two accepted goldens stay byte-identical. Parent: `51f50aa1` (integration head, which
already contains round-1 material `966cca75` and the three review reports).

### Per-item closure

1. **G5 MED-1 (huge-integer coordinate → untyped OverflowError, BOTH public paths).** A JSON integer literal
   beyond the float range (`10**400`, any int ≳10**309) made `math.isfinite(bigint)` raise `OverflowError`.
   - LOT path: `_is_finite_number` now treats an out-of-float-range int as non-finite (a `try/except
     OverflowError` around `math.isfinite`), so the existing `non_finite` refusal fires (reason `non_finite`,
     field `lot_ring[0]`). A finite float like `1e300` is unaffected (still hits the magnitude bound).
   - FOOTPRINT path: the huge int overflows B0's OWN finiteness check (`proposal._is_real_number` →
     `math.isfinite`), which raises `OverflowError` (not a `ProposedMassingError`), so the existing
     `except ProposedMassingError` never saw it. Added an `except OverflowError` arm on the B0 validation
     `try/except` that types it as the same `non_finite` refusal (field `proposed_massing.outline`). This is
     in massing_model, NOT proposal.py. Both paths now fail closed as typed `MassingModelError`.
   - Tests: `test_t106r2_huge_int_lot_vertex_is_typed_non_finite`,
     `test_t106r2_huge_int_footprint_vertex_is_typed_non_finite`. Each has its OWN reddening mutation (below).

2. **G5 LOW-1 = G3 ADVISORY-1(B) (the B0 re-echo `{exc}` at the validation boundary was unbounded).** A
   200,000-char footprint vertex made B0 produce a ~200,000-char message (`proposal.py:250 {vertex!r}`),
   which `build_massing_model` re-echoed unbounded. Changed the re-echo to `{_preview(exc)}` — bounded.
   Test: `test_t106r2_b0_error_echo_is_bounded` (200k footprint vertex → message ≤300 chars, pasted value
   truncated, `chars>` marker present). Root `proposal.py:250` stays out of scope (D-OBS-2, wiring packet).

3. **G3 ADVISORY-1(A) = G4 ADVISORY-2 (the no-candidate `detail` echo was raw `{detail or ''}`).**
   `build_from_generated_option`'s no-candidate branch now bounds the engine-sourced detail with
   `_preview(detail)`; a short valid detail is still surfaced. Test:
   `test_t106r2_no_candidate_detail_echo_is_bounded` (200k detail → ≤300 chars; a short detail still appears).

4. **G4 ADVISORY-1 (AS-2 only exercised TopologicalError, so a narrowed catch could ship green).** Added a
   SECOND, distinct sibling test using `GeometryTypeError` — a genuine `ShapelyError` that is neither a
   `GEOSException` NOR a `TopologicalError` (asserted in the test). Narrowing the wrap to
   `except (GEOSException, TopologicalError)` now reddens. Production code is unchanged (it already caught the
   `ShapelyError` base); this is a test-adequacy pin. Test:
   `test_t106r2_second_non_geos_shapely_sibling_is_also_wrapped`.

5. **G5 INFO (`_preview` could itself raise on a hostile/deep `repr`).** `_preview` now wraps `repr(value)`
   in `try/except Exception` and returns the fixed `<unrepresentable value>` placeholder, so it never raises.
   Test: `test_t106r2_preview_never_raises_when_repr_raises` (a hostile `__repr__` → RuntimeError, and a
   self-recursive `__repr__` → RecursionError, both → the placeholder; a normal value still previews verbatim).

6. **Docstring + AS-4 wording (state the exact truth).** The module docstring (`:60-73`) now documents the
   OverflowError→non_finite fix on both paths, and states the COMPLETE, exact set of caller-input echoes this
   module bounds (rejected lot/footprint vertex, `source`, floor height, the re-echoed B0 error, and the
   generated-option placement-gap detail) plus that `_preview` never raises — dropping the round-1 universal
   over-claim. The round-1 AS-4 bullet above is corrected with a "ROUND 2 CORRECTION" note. Note: caller ints
   that are NOT arbitrary-length geometry (e.g. a `level_index`) are outside DB-069(d)'s named echo set and
   outside this round's scope; the docstring no longer claims "every" echo, only the enumerated set.

### Mutation table (round 2 — in-process, one fresh interpreter per mutant; consuming-namespace injection)

Harness: text-mutate a copy of `massing_model.py`, inject into `sys.modules["app.scenario.massing_model"]`
and set the `app.scenario` attr BEFORE the test module's by-value imports resolve, purge every
`*massing_model*` key, run the exact target test(s). Baseline (unmutated inject) GREEN across the 6 new tests
(faithful harness); every mutant RED on its specific assertion.

| Mutant | Change (consuming namespace) | Target test | Result |
|---|---|---|---|
| baseline | none (harness faithfulness) | all 6 round-2 tests | GREEN — 6 passed |
| medlot | `_is_finite_number` reverts to unguarded `math.isfinite` | `test_t106r2_huge_int_lot_vertex_is_typed_non_finite` | RED — `E OverflowError: int too large to convert to float` escapes |
| medfoot | B0 `except OverflowError` arm catches `ZeroDivisionError` instead | `test_t106r2_huge_int_footprint_vertex_is_typed_non_finite` | RED — `E OverflowError: int too large to convert to float` escapes |
| low1echo | re-echo reverts to `{exc}` (raw) | `test_t106r2_b0_error_echo_is_bounded` | RED — message ~200k chars / pasted value present |
| detail | no-candidate reverts to `{detail or ''}` (raw) | `test_t106r2_no_candidate_detail_echo_is_bounded` | RED — message ~200k chars |
| sibling | wrap narrows to `except (GEOSException, TopologicalError)` | `test_t106r2_second_non_geos_shapely_sibling_is_also_wrapped` | RED — `GeometryTypeError` escapes untyped |
| preview | `_preview` drops the `try/except` (raw `repr(value)`) | `test_t106r2_preview_never_raises_when_repr_raises` | RED — `repr` raises out of `_preview` |

### Commands (explicit cwd; [OBSERVED] verbatim tails)

- [OBSERVED] cwd `services/api`: `python -m ruff check app/scenario/massing_model.py tests/scenario/test_massing_model.py` → `All checks passed!` (rc 0).
- [OBSERVED] cwd `services/api`: `python -m ruff check .` → `All checks passed!` (rc 0) — the round-1 D-OBS-1
  placeholder E501s are resolved at HEAD; the full api tree is clean.
- [OBSERVED] cwd `services/api`: `python -m pytest tests/scenario -q` → `728 passed in 39.51s` (round-1
  baseline 722 + 6 added; no existing test edited — `git diff --numstat` on the test file = `160  0`).
- [OBSERVED] cwd repo root: `python tools/modularity_check.py --check` → `selected 497 files; failures 0;
  warnings 27`, DIRECT_EXIT=0. `massing_model.py` remains a `review_signal` warning (above the justification
  threshold, UNDER the 1000-line hard cap), same class as round 1.
- [OBSERVED] cwd `services/api`: round-2 mutation harness — `baseline` `6 passed` (VERDICT OK); `medlot`,
  `medfoot`, `low1echo`, `detail`, `sibling`, `preview` each `pytest_rc=1` RED (VERDICT OK); `medlot`/`medfoot`
  confirmed to fail via `E OverflowError: int too large to convert to float` escaping.
- Goldens byte-identical: `test_t106_as6_valid_input_goldens_byte_identical` asserts both accepted hashes
  (`sha256:b7fa9862…5133b` 1-floor RECT, `sha256:e23b5cbc…a6c5` 5-floor stack) and PASSES in the 728-green run.

### Modularity cohesion note (round 2 update)

`massing_model.py` grew from 958 to 994 lines (raw; ~797 non-blank/non-comment) — still a `review_signal`
warning (above the justification threshold, UNDER the 1000-line hard cap), `modularity_check --check` exit 0.
The +36 lines are the same single responsibility (the deterministic massing truth object): completing the
typed input boundary for out-of-float-range integers, bounding two residual refusal echoes, and hardening the
echo-preview helper — no new domain, storage, serialization, external I/O, CLI/API or presentation concern.
The file is now ~6 lines from the hard cap; the next packet that adds a genuinely new responsibility (e.g.
mesh export) should split along the guards / builder / mesh boundary with a compatibility facade rather than
grow this module further.

### Scope / out-of-scope confirmation

Done: exactly items 1-6 above. NOT done (per the packet's OUT OF SCOPE): `proposal.py:250` (forbidden;
D-OBS-2 root for the wiring packet); the immaterial boundary survivors (inclusive NYC max; echo bound ±1;
echo `<=`/`<` at exactly-limit — all behaviour-free, matching the accepted DB-069(f) note); any refactor.

END-OF-REPORT
