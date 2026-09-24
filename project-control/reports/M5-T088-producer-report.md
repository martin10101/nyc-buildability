# M5-T088 producer report - massing truth-object hardening (DB-054 a-j)

- Task: M5-T088 (D-087 3D-1b). Producer: 3d-massing-engineer (orchestrator-dispatched subagent).
- Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t088`, branch `task/M5-T088-massing-hardening`.
- Parent (contract/claim seam): `114e5e56e158d6f263e58a314c383ea62ee7eff4`. Commit: ONE commit on top of it
  (its sha is reported in the orchestrator return; a file cannot carry its own commit sha).
- Guard at start [OBSERVED]: `git rev-parse --show-toplevel` = `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t088`;
  HEAD = 114e5e56...; `git status --short` clean. Accepted module blob at parent = `255de6ec` (== the blob G4 reviewed).
- Local: Python 3.11.9, numpy 2.3.3, shapely 2.0.7. CI (3.12) on the pushed head is the authority.

## IMPLEMENTATION

Files changed (exactly the allowed paths):

| File | LF-normalized sha256 | git blob |
|---|---|---|
| `services/api/app/scenario/massing_model.py` | `6c70e29e1169ebf26dae6fd5a1bd159accc7a0d26a6b21e2dfac8e0f90c50a64` | `42545728` |
| `services/api/tests/scenario/test_massing_model.py` | `d57e0dee776a2e460aecc2d05b9e7d4e1d7455951fff8cc28bbe6a8669323343` | `c55e2cd7` |
| `project-control/reports/M5-T088-producer-report.md` | this file | - |

Module changes (`massing_model.py`):
- New resource-bound constants (never legal values), `:114-129`: `MAX_COORD_ABS = 1e8` (mirrors the DXF/PDF
  writers), `MAX_TOTAL_MESH_VERTICES = 100_000`, `MAX_TRIANGULATION_WORK = 2_000_000`.
- Coordinate magnitude bound on EVERY ring in `_prepare_ring`, `:225-229` -> `coordinate_out_of_range`, field `<ring>[i]`.
- `_WorkBudget` `:264-280`, `_min_ear_clip_work` `:283-287` (exact least charge `(n-2)(n-1)/2 - 1`), metered
  `_triangulate(ring, field, budget=None)` `:290-344`: 1 unit per candidate (`:319`), the convex candidate's
  worst-case scan `m-3` charged BEFORE the scan (`:326`). The algorithm and its output are unchanged.
- `_check_floor_cap` `:508-518` -> `over_cap_floors` (message names floors), called right after B0 validation
  `:683`, before any ring is prepared. The old in-loop check (reason `over_cap_vertices`) is removed.
- `_expand_floor_stack` `:521-574` no longer triangulates; per-level rings are content-deduped (tuple key).
- `_check_output_size` `:577-585` -> `over_cap_output_vertices`, called `:691` before containment/triangulation.
- `_triangulate_distinct` `:588-604`: each DISTINCT ring once under ONE shared per-request budget; refuses up front
  (`:598`) when the summed least work already exceeds the budget.
- Builder order `:682-713`: source -> B0 -> floor cap -> lot ring (magnitude) -> footprint/per-level prep ->
  output ceiling -> containment (unchanged semantics, content-keyed dedupe) -> triangulation -> prisms.
- Docstrings: module `:34-50`, `_lot_polygon` `:613-619` (the `interiors` branch is marked defensive/unreachable).

Tests (`test_massing_model.py`): 26 -> 54 tests. New fixtures `USHAPE :83`, `COMB :95`, `NONINT_LOT :112`,
`NONINT :118`, `_regular :130`, `_spiral :140`, `_block :156`, `_stack :166`; independent helpers `_shoelace :244`,
`_exact_area :253` (Fraction, exact), `_cap_faces_face_outward :264`; spy fixture `heavy_work :282` (counts
`_triangulate` / `_build_prism` calls resolved through the module namespace).

## Evidence per acceptance scenario

**AS-1 (concave)** [OBSERVED]
- U (area 4800) and comb (area 4820) are non-star-shaped: `test_t088_as1_fixture_is_not_star_shaped_so_every_fan_over_covers`
  `:617-631` proves a fan from EVERY start vertex over-covers them (the L-shape cannot discriminate).
- Joined the cap-area (`:386-397`, ids ushape/comb), closure (`:352-372`, ids ushape/comb, plus the new per-face
  cap-normal check) and triangle-count (`:408-419`, renamed `test_as2_concave_ring_triangulates_without_spanning_the_notch`,
  now CCW + `covers` per triangle) parametrizations.
- Mutation M1 (naive fan) reddens all six U/comb params (not only the golden) - table below.

**AS-2 (orientation + collinear)** [OBSERVED]
- `test_t088_as2_clockwise_rings_normalize_to_ccw` `:639-659` (cw_lot / cw_footprint / cw_both): emitted lot
  and footprint rings CCW, closed, outward caps, volume 36000, plate 3000. M2 reddens all three.
- `test_t088_as2_exact_collinear_vertex_collapses` `:662-669`: a midpoint on a footprint edge and on a lot edge
  collapse; mesh byte-equal to the plain rect's. M3 reddens it.
- `test_t088_as2_near_collinear_vertex_is_kept_not_repaired` `:672-682`: 0.001 ft off-line is kept (exact-only collapse).

**AS-3 (containment boundary)** [OBSERVED]
- `test_t088_as3_footprint_just_outside_the_lot_is_refused` `:690-697` (0.5 ft and 0.001 ft east overhang) ->
  `footprint_outside_lot`. M4 (tol 1e-6 -> 50) reddens both.
- On-lot-line pinned: `test_t088_as3_footprint_on_the_lot_line_is_accepted` `:700-707` (zero-lot-line corner footprint,
  and a footprint identical to the lot) accepted, not clipped.

**AS-4 (bounds, typed, before heavy work)** [OBSERVED]
- Magnitude: `test_t088_as4_near_overflow_lot_ring_is_a_typed_refusal` `:715-726` (+ `heavy_work == Counter()`);
  inclusive boundary + footprint path `test_t088_as4_coordinate_magnitude_bound_is_inclusive` `:729-743`.
- Floors: `test_t088_as4_floor_cap_refusal_names_floors` `:746-753` (2500 floors -> `over_cap_floors`, message
  "2500 floors", zero heavy work); boundary `:756-762`.
- Output vertices: `test_t088_as4_output_vertex_ceiling_refuses_before_meshing` `:765-772` (2000 floors x 26-gon =
  104000 > 100000, zero heavy work); boundary `:775-781`.
- Triangulation: `test_t088_as4_triangulation_budget_meters_the_ear_scan` `:787-800` (default budget triangulates
  the 82-vertex spiral exactly; `2 x least` refuses mid-scan); `test_t088_as4_triangulation_budget_through_the_builder`
  `:803-818` (budget `least-1` -> refused with zero `_triangulate` calls; `2 x least` -> refused after one metered
  call and zero prisms); `test_t088_as4_budget_admits_realistic_outlines` `:821-835` (4 max-size convex outlines fit;
  a 200-gon builds; 3 identical per-level outlines triangulate ONCE).
- Real-constant probe (outside the suite; `probe_budget.py` in the scratch dir):
  ```
  MAX_TRIANGULATION_WORK 2000000
  convex_999: n=999 least=497502 triangulated 997 tris units_spent=497502 s=1.52
  spiral_998: n=998 least=496505 refused triangulation_budget_exceeded units_spent=2000099 s=4.23
  ```
  Pre-fix, the same 998-vertex spiral ran to completion in 19.2 s (3,900,819 point tests) on this machine.

**AS-5 (conditioning + scope)** [OBSERVED]
- `test_t088_as5_non_integer_volume_is_reduced_about_the_local_origin` `:851-870`: 91 floors of a non-integer concave
  footprint (z to ~1234 ft) in a non-integer-origin lot; every volume within 1e-6 of the EXACT rational volume
  (area x height via `Fraction`); a fixture-validity assertion proves a world-coordinate reduction misses by > 1e-6.
  M5 reddens it. Probe (pre-fix module, one floor): local error 4.6e-7 (grid rounding) vs world error 3.1e-5 at
  z=0, 5.1e-4 at z=120, 2.4e-2 at z=1234.6.
- Lot-with-hole test repaired honestly: renamed `test_as4_lot_ring_with_too_few_vertices_is_refused` `:483-491`
  (reason pinned to `invalid_source`) + new `test_t088_as5_keyhole_lot_ring_pinching_a_hole_is_refused` `:494-508`
  (a keyhole ring is the only way one ring encodes a hole -> `self_intersection`, field `lot_ring`).
- DB-054 (g) multi-floor golden: `test_t088_as5_five_floor_stack_golden` `:873-881`,
  `sha256:e23b5cbcca6ea7defee4b04c6bac51a94d4c26b5e643e2af923d29d1c248a6c5`.
- Zero new dependencies (tests add stdlib `fractions` and the admitted `numpy`); no route, API, main.py, web, or
  requirements change; `grep` finds no importer of `massing_model` besides its test (not wired).

## Output-byte identity (golden NOT re-anchored) [OBSERVED]

The RECT golden `b7fa9862...` is unchanged. `identity.py` built every valid fixture with the accepted module
(blob 255de6ec) and with the new module and compared `to_json()` bytes:

```
rect           identical=True    lshape         identical=True    five_floor     identical=True
ushape         identical=True    comb           identical=True    cw_both        identical=True
collinear      identical=True    nonint         identical=True    setback_levels identical=True
spiral         identical=True    regular200     identical=True    2000_floors    identical=True
```

The new test file run against the ACCEPTED module: `9 failed, 45 passed` - exactly the nine bound tests fail
(the bounds are new); every fixture test (U/comb, CW, collinear, containment, non-integer, goldens) passes on the
accepted module, confirming G4's finding that those gaps were coverage, not defects.

## Mutation table (consuming namespace, fresh interpreter per mutant) [OBSERVED]

Method: `mutate.py` (scratch, outside the repo) applies one exact single-occurrence edit to a COPY of the module,
a `-p inject_mutant` pytest plugin loads it as `app.scenario.massing_model` into `sys.modules` and onto the
`app.scenario` package before collection (so both the test's `mm` and the builder's own globals resolve to the
mutant), then runs the real test file. BASELINE (unmutated copy) = 54 passed. The repo file is never edited.
Restore = the unmutated module: the documented pytest run below is GREEN (54 passed).

| Mutant | Edit | Result | Reddened (named tests) |
|---|---|---|---|
| BASELINE | none | GREEN 54 passed | - |
| M1 naive fan | `_triangulate` returns `(0,i,i+1)` fan | RED 11 | closure/cap-area/concave-count [ushape],[comb] x6, RECT golden, five-floor golden, near-collinear, 2 budget |
| M2 drop CW normalization | `if False: parsed.reverse()` | RED 3 | clockwise_rings [cw_lot],[cw_footprint],[cw_both] |
| M3 drop collinear collapse | `if False: continue` | RED 1 | exact_collinear_vertex_collapses |
| M4 tolerance 1e-6 -> 50 | constant | RED 2 | just_outside_the_lot [half_foot],[thousandth] |
| M5 world-coordinate volume | drop `- ox`, `- oy` | RED 1 | non_integer_volume_is_reduced_about_the_local_origin |
| M6 remove magnitude bound | `if False:` | RED 2 | near_overflow_lot_ring, coordinate_magnitude_bound_is_inclusive |
| M7a remove budget (up front) | `if False:` at `:598` | RED 1 | triangulation_budget_through_the_builder |
| M7b remove budget (metering) | `if False:` in `charge` | RED 2 | budget_meters_the_ear_scan, budget_through_the_builder |
| M7c remove budget entirely | both | RED 2 | same two |
| M8 remove floor cap | delete `_check_floor_cap(...)` call | RED 2 | floor_cap_refusal_names_floors, floor_cap_boundary |
| M9 remove output ceiling | delete `_check_output_size(...)` call | RED 2 | output_vertex_ceiling_refuses_before_meshing, _boundary |
| M10 floor cap `>` -> `>=` | off-by-one | RED 2 | floor_cap_boundary, output_vertex_ceiling_refuses_before_meshing |
| M11 output ceiling `>` -> `>=` | off-by-one | RED 1 | output_vertex_ceiling_boundary |
| M12 magnitude `>` -> `>=` | off-by-one | RED 1 | coordinate_magnitude_bound_is_inclusive |
| M13 reverse bottom cap (T082 guard) | `(a, b, c)` | RED 14 | accepted closure/volume/golden guards still bite |

Harness output, final settled source (`mutation_run_final.txt`), summary lines verbatim:
```
BASELINE: GREEN (exit 0) 54 passed in 1.46s
M1_naive_fan: RED (exit 1) 11 failed, 43 passed in 1.12s
M2_drop_cw_normalization: RED (exit 1) 3 failed, 51 passed in 1.29s
M3_drop_collinear_collapse: RED (exit 1) 1 failed, 53 passed in 1.37s
M4_tolerance_50: RED (exit 1) 2 failed, 52 passed in 1.34s
M5_world_coordinate_volume: RED (exit 1) 1 failed, 53 passed in 1.38s
M6_remove_magnitude_bound: RED (exit 1) 2 failed, 52 passed, 2 warnings in 1.31s
M7a_remove_budget_upfront: RED (exit 1) 1 failed, 53 passed in 1.33s
M7b_remove_budget_metering: RED (exit 1) 2 failed, 52 passed in 1.43s
M7c_remove_budget_entirely: RED (exit 1) 2 failed, 52 passed in 1.51s
M8_remove_floor_cap: RED (exit 1) 2 failed, 52 passed in 2.57s
M9_remove_output_vertex_ceiling: RED (exit 1) 2 failed, 52 passed in 3.03s
M10_floor_cap_off_by_one: RED (exit 1) 2 failed, 52 passed in 1.22s
M11_output_ceiling_off_by_one: RED (exit 1) 1 failed, 53 passed in 1.24s
M12_magnitude_off_by_one: RED (exit 1) 1 failed, 53 passed in 1.27s
M13_reverse_bottom_cap_T082: RED (exit 1) 14 failed, 40 passed in 0.99s
```

Reproduce (any reviewer): the plugin body is five statements - `spec_from_file_location("app.scenario.massing_model",
MUTANT_PATH)`, `module_from_spec`, `sys.modules[...] = mod`, `exec_module`, `app.scenario.massing_model = mod`;
run `python -m pytest tests/scenario/test_massing_model.py -q -p inject_mutant -p no:cacheprovider` from
`services/api` with `PYTHONPATH=<plugin dir>;<services/api>` and `MUTANT_PATH=<mutated copy>`.

## Self-checks (verbatim)

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t088\services\api`: `python -m ruff check .`
```
All checks passed!
ruff exit=0
```

cwd `...\wt-m5t088\services\api`: `python -m pytest tests/scenario/test_massing_model.py -q`
```
......................................................                   [100%]
54 passed in 2.47s
pytest exit=0
```

cwd `...\wt-m5t088` (root): `python tools/modularity_check.py --check`
```
selected 486 files; failures 0; warnings 24
  warn symbol_ceiling: apps/web/src/lib/surveyReview/types.ts - many top-level symbols (approximate count); a signal, not a verdict
  warn review_signal: services/api/app/api/v1/outline_bridge.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/api/v1/scenario_analysis.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/connectors/dcm_street_centerline_arcgis.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/connectors/dtm_condo_soda.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: services/api/app/connectors/mappluto_geometry_arcgis.py - many top-level symbols; a signal, not a verdict
  warn review_signal: services/api/app/connectors/wide_street_buffer_engine.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/drawings/sheet_reader.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: services/api/app/rules/integration.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/breakeven.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/massing_model.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: services/api/app/scenario/max_envelope.py - above the justification threshold; record a cohesion justification in review
  warn symbol_ceiling: tools/agent_supervisor/cli.py - many top-level symbols; a signal, not a verdict
  warn review_signal: tools/agent_supervisor/codex_reviewer.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/durable_state.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/evidence.py - above the warning threshold; consider the module boundary before growing it further
  warn review_signal: tools/agent_supervisor/gate_wave.py - above the justification threshold; record a cohesion justification in review
  warn review_signal: tools/agent_supervisor/next_task.py - above the warning threshold; consider the module boundary before growing it further
  warn symbol_ceiling: tools/agent_supervisor/policy.py - many top-level symbols; a signal, not a verdict
  warn review_signal: tools/agent_supervisor/process.py - above the warning threshold; consider the module boundary before growing it further
modularity exit=0
```
(The tool prints 20 of its 24 warnings. Baseline at the parent was `failures 0; warnings 23`; the +1 is
massing_model.py.)

Extra sanity [OBSERVED]: `python -m pytest tests/scenario -q` (cwd services/api) -> `683 passed in 23.08s`.
CI 3.12 on the pushed head [BLOCKED locally -> harvest]: run the three documented commands in the api CI job.

## Modularity - cohesion justification

`massing_model.py` grows 584 -> 663 SLOC (warn 600, justify 750; not new, not in the baseline, no failure). It
stays one responsibility: validate inputs -> triangulate -> build prisms -> assemble the truth object. Every line
added is an input bound of that same pipeline, not a new concern. The allowed paths grant no new module, so no
split here. Recommended split before any further growth: see Discovery 3.

## Deviations, assumptions, limitations

- Bound values are resource ceilings I chose (not legal values): 1e8 mirrors the writers; 100,000 vertices measured
  at ~6.5 MB of JSON (104,000 vertices -> 6.51 MB); 2,000,000 work units fits four max-size convex outlines and
  took 4.23 s to the refusal on this machine. The orchestrator or reviewers may tune them; tests read the constants.
- Behaviour deltas (all requested or neutral): floor-cap reason `over_cap_vertices` -> `over_cap_floors`, checked
  up front; containment now runs BEFORE triangulation (an input both outside the lot and not triangulable would
  now report `footprint_outside_lot`; B0 already refuses non-simple outlines); identical per-level outlines are
  triangulated once. Output bytes are identical on every valid fixture (table above).
- A pathological but valid outline (e.g. a 998-vertex spiral) is now refused `triangulation_budget_exceeded`.
  Disclosed fail-closed limit; see Discovery 5.
- The budget tests use a monkeypatched/explicit smaller budget to stay fast; the real-constant worst case is the
  out-of-suite probe above.
- The pre-fix overflow crash on my fixture was an untyped `shapely.errors.GEOSException` (empty centroid), not the
  `ValueError` G5-F1 saw with its probe. Both are untyped; both are now a typed refusal.
- Code graph: `python tools/code_graph/query.py --no-regen impact services/api/app/scenario/massing_model.py`
  returned `STALE (stale fingerprint): refusing to serve the cached graph` at 114e5e56. Importers were verified by
  grep instead (only the test file imports the module).
- Timings come from this machine only.

## DISCOVERIES (for docs/DISCOVERY_BACKLOG.md; not fixed in-packet)

1. B0 validation is itself a CPU sink. `proposal.validate_proposed_massing` runs the O(n^2) `_ring_is_simple` on
   every per-level outline: 2.62 s for ONE 1000-position outline here [OBSERVED]. B0 allows 500 levels, each
   with its own outline -> about 22 min per request [PREDICTED, linear]. This runs before any massing bound.
   Needs a B0-side total-positions bound or a faster simplicity test before user geometry is wired
   (`proposal.py` is outside this packet).
2. The lot ring has only the 1e8 magnitude bound, with no NYC 2263 unit check. A wrong-CRS lot (for example
   4326 lon/lat) passes it and then fails as `footprint_outside_lot`, which names the wrong cause. The
   connector/wiring packet should add a NYC-bounds unit check (mirroring B0's `NYC_2263_*`).
3. Modularity: `massing_model.py` is at 663 SLOC. Before GLB/wiring growth, split ring preparation, ear clipping
   and the work budget (about 200 SLOC) into `app/scenario/massing_triangulation.py`, keeping a compatibility
   facade. That needs a packet that grants the new path.
4. shapely raises its own `GEOSException` (not a `ValueError`) on degenerate geometry. Any future route that maps
   only `ValueError` or `MassingModelError` to a 4xx would 500 on such a path. The wiring packet should map it
   defensively.
5. The ear clipper scans every remaining vertex per candidate. Testing only reflex vertices (the standard
   optimisation) would cut typical cost a lot and let the budget admit more real shapes. Its triangle order
   may change, so it needs a golden re-anchor in its own packet.
6. G5-F2's "minutes-to-hours" is confirmed in order of magnitude: one 998-vertex spiral took 19.2 s before the fix
   [OBSERVED], so 500 distinct ones would take about 2.7 h [PREDICTED]. It is now capped per request.
7. The packet says the code graph was regenerated at the contract seam, but `--no-regen` reported it STALE at
   114e5e56. Worth checking at the next seam.

Geometry implementation is submitted for independent mathematical and visual review; requested status: awaiting_gate.
