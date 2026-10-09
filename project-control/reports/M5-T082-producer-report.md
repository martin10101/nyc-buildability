# M5-T082 producer report - D-087 3D-1: deterministic massing truth object

Producer: 3d-massing-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t082`, branch `task/M5-T082-massing-model`,
contract head `f9bfd54d37c981e938185e3ae09ea9ad85f415f3` (verified at start).

Design authority: `docs/3D_MASSING_ENGINE_ARCHITECTURE.md` sections 2-4, 10. Inputs
read read-only: `app/scenario/proposal.py` + `contract.py` (B0 contract),
`app/scenario/max_envelope.py` `as_dict` shape, `app/scenario/derivation.py`
(`LotContext`, digest style), `app/connectors/mappluto_geometry_arcgis.py` (canonical
ring convention: OPEN vertex cycles, exterior CCW).

Files changed (only the three allowed paths):
- `services/api/app/scenario/massing_model.py` (new module; 584 code lines)
- `services/api/tests/scenario/test_massing_model.py` (26 tests)
- `project-control/reports/M5-T082-producer-report.md` (this report)

## Per-acceptance-scenario evidence

### AS-1 (truth object: declared frame + deterministic golden)
`MassingModel.as_dict` (massing_model.py:401) emits `generator_version`
"massing-1.0.0", `geometry_version`, `coverage_status` "conditional", and the full
coordinate frame from `_crs_frame` (massing_model.py:536): `crs` EPSG:2263, `authority`
(NAD83 New York Long Island, US survey feet), `horizontal_unit`/`vertical_unit`
`us_survey_foot`, `axis_order` `easting_northing`, `local_origin` near the parcel
centroid (`_local_origin`, massing_model.py:530), the exact world->local transform
(`world_to_local.offset == [-ox,-oy,0]`), and `precision_grid_ft` (1e-6). Provenance
carries the input digests (`_digest`, massing_model.py:375) and the passed-through
proposal provenance. `to_json` (massing_model.py:418) is strict (`allow_nan=False`)
and sorted; `content_hash` (massing_model.py:424) is the golden sha256.
Tests: `test_as1_declares_full_coordinate_frame`,
`test_as1_json_serializable_and_deterministic_golden` (golden pinned
`sha256:b7fa9862...27c5133b` on the exact-coordinate rectangle fixture; also asserts
two independent builds hash-equal), `test_as1_local_origin_near_parcel_centroid`
(test file lines 145-179).

### AS-2 (mesh correctness + reversed-winding mutation)
`_build_prism` (massing_model.py:313) builds each floor band as an independent closed
prism: top cap from the CCW ear-clip (`_triangulate`, massing_model.py:236) -> +z
normal; bottom cap reversed -> -z normal; one outward-wound side quad per ring edge
`(bi,bj,tj)+(bi,tj,ti)`. `_prepare_ring` (massing_model.py:176) collapses collinear
straight vertices so caps and walls share the same boundary and ear clipping always
finds a strict-convex ear (concave-safe). Signed volume is reduced in LOCAL coords
(numpy einsum, massing_model.py:355) for conditioning; > 0 confirms outward winding.
Tests: `test_as2_every_prism_closed_outward_and_nondegenerate` (rectangle, concave
L-shape, 5-floor: closed manifold via directed-edge-uniqueness, volume > 0, every
triangle 3D-area > 1e-9), `test_as2_cap_triangulation_area_equals_polygon_area`
(triangulated cap area == shapely area within 1e-9 relative for RECT=2400 and
L=3000), `test_as2_volume_equals_area_times_height` (within 1e-9 relative),
`test_as2_concave_lshape_triangulates_without_spanning_the_notch` (n-2 triangles),
and `test_as2_reversed_face_winding_is_detected` (test file lines 182-260).

### AS-3 (plates + metrics + swapped-height mutation)
Per-floor plate area is the shapely area of the authoritative 2263 world ring
(`_build_prism`, massing_model.py:357). `build_massing_model` (massing_model.py:555)
sums plate areas into `metrics.gross_floor_area_sq_ft` and floor heights into
`metrics.total_height_ft`; each plate records `elevation_ft` from the cumulative
stack (`_expand_floor_stack`, massing_model.py:445). Tests:
`test_as3_plate_areas_match_shapely_2263_area`, `test_as3_metrics_reconcile_with_plates`,
`test_as3_five_floor_plate_elevations` (exact cumulative sequence for distinct heights
[12,11,13,10,14]), `test_as3_swapping_two_floor_heights_changes_the_model` (content
hash + elevations differ) (test file lines 265-305).

### AS-4 (fail-closed; nothing clipped)
`MassingModelError` (massing_model.py:112) carries a machine-readable `reason`. Refusals:
`footprint_outside_lot` (containment via `lot.buffer(tol).contains(floor)`, never clipped
- massing_model.py:601), `lot_has_holes`/`self_intersection` (`_lot_polygon`,
massing_model.py:514), `non_finite`, `over_cap_vertices`, `invalid_source`
(`_prepare_ring`), `non_positive_height` (`_expand_floor_stack`), `no_generated_candidate`
(`build_from_generated_option`). B0 validation runs first as fail-closed defense
(massing_model.py:577). Tests: `test_as4_footprint_outside_lot_is_refused_not_clipped`,
`_lot_with_hole_`, `_self_intersecting_footprint_`, `_non_finite_coordinate_`,
`_over_cap_vertices_`, `_non_positive_height_`, `_nothing_is_clipped_on_valid_input`
(test file lines 310-388).

### AS-5 (honesty + scope)
Only two building labels exist: `proposed` ("Proposed - not a city record") and
`generated_option` ("Generated building option") (`_LAYER_FOR_SOURCE`/`_DISCLOSURE_FOR_SOURCE`,
massing_model.py:93,97). `test_as5_module_has_no_permitted_or_maximum_allowed_wording`
scans the module source and asserts none of permitted/approved/maximum-allowed appear.
`test_as5_generated_option_path_from_max_envelope_as_dict` builds from the engine's
`as_dict` shape (pulling `candidate`); `test_as5_generated_option_no_candidate_is_typed_refusal`
proves a None candidate is a typed refusal, never a fabricated building. `max_envelope.py`
and every route are byte-untouched (git status below); zero new dependencies (stdlib +
admitted shapely/numpy + `app.scenario.proposal` only) (test file lines 393-448).

## Self-check command output (verbatim)

cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t082\services\api`:
```
$ python -m ruff check .
All checks passed!
```
```
$ python -m pytest tests/scenario/test_massing_model.py -q
..........................                                               [100%]
26 passed in 0.38s
```
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t082`:
```
$ python tools/modularity_check.py --check
selected 483 files; failures 0; warnings 22
```
massing_model.py is NOT in the warnings list (584 code lines, under the 600 WARN
threshold). Python 3.11.9; shapely 2.0.7; numpy 2.3.3 (all already admitted).

## Mutation record (named mutations, red/green)

1. Reverse one face winding - edited `_build_prism` side quad
   `tris.append((bi, bj, tj))` -> `(bi, tj, bj)`:
   `test_as2_every_prism_closed_outward_and_nondegenerate` -> `3 failed` (RED, closure
   `_is_closed_manifold` returns False); reverted -> `3 passed` (GREEN).
2. Swap two floor heights - edited `_expand_floor_stack` sort to `reverse=True`
   (mis-orders the floor-height stack): `test_as3_five_floor_plate_elevations` ->
   `1 failed` (RED, "At index 1 diff: 14.0 != 12.0"); reverted -> `2 passed` (GREEN).

Both mutations were applied via sed and reverted exactly; final source carries no
`MUTANT`/`reverse=True` residue (grep confirmed), and the full suite is green post-revert.

## git status (only allowed paths)
```
 M services/api/app/scenario/massing_model.py
 M services/api/tests/scenario/test_massing_model.py
 M project-control/reports/M5-T082-producer-report.md
```

## Deviations
- None from scope. No route/web/main.py change; `max_envelope.py`/`proposal.py`/
  `contract.py` read-only (imported `validate_proposed_massing`, `ProposedMassingError`,
  `MAX_OUTLINE_VERTICES` from proposal - read-only use, no edit).

## Discoveries (DISCOVERIES; route to backlog, not fixed here)
- ADAPTER DECISION (recorded per work order): the B0 proposal contract DOES carry
  per-floor heights (`levels[].floor_count` x `levels[].floor_to_floor_ft`), so no
  separate typed floor-stack input was needed; `_expand_floor_stack` expands levels
  into an explicit per-floor band stack (z from 0). Per-level `outline` (setback/tower
  bands) is supported: a level's own footprint is triangulated for its floors.
- The canonical mappluto ring is an OPEN, exterior-CCW vertex cycle while the B0
  proposal outline is EXPLICITLY closed (`vertices[0]==vertices[-1]`); `_prepare_ring`
  normalizes both (drops any closing duplicate, reorients to CCW). If a future wiring
  packet feeds the connector's already-quantized string coordinates, they must be
  parsed to floats before this module (it requires numeric [x,y]).
- Independent closed prisms per floor band mean adjacent floors carry two coincident
  interface caps (top of k, bottom of k+1). This is correct for a floor-plate solid
  stack and keeps per-prism closure tests clean; a future welded/watertight
  whole-building mesh (for GLB export) would merge these - a later packet concern.
- Meshes store authoritative world 2263 coordinates; the local origin + exact
  transform are metadata for a renderer to subtract near-origin (section 3). The
  golden sha256 is pinned on the exact-coordinate rectangle fixture; a wiring packet
  adding real (non-round) MapPLUTO coordinates should pin its own golden and watch
  cross-runner float determinism at NYC magnitudes (mitigated here by 6-dp
  quantization to the declared precision grid).

END-OF-REPORT
