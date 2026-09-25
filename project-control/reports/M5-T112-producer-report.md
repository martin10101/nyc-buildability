# M5-T112 producer report — D-087 massing_model split (DB-079 a, b)

- Task: M5-T112 (backend, milestone M5). Directive refs: D-087 (R001/R002/R003/R009), D-066 (R001).
- Producer: 3d-massing-engineer (orchestrator-dispatched subagent).
- Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t112` (branch `task/M5-T112-massing-split`).
- Claim-seam commit (verified `rev-parse HEAD` before edits): `275ef85f05ca43a9cd2fd59a5ccdfa3b80cd3021`.
- Scope: split `services/api/app/scenario/massing_model.py` (797 SLOC / 994 physical, near the
  1000 hard cap) into three focused modules behind a compatibility facade; make the concave-safe
  ear-clipping triangulator a public reusable API; fix the DB-079 (b) B0-OverflowError field label.
  Every other output byte-identical.

## Files written (all within allowed_paths; test_massing_model.py deliberately NOT touched)

- `services/api/app/scenario/massing_model.py` — the compatibility facade + builder orchestration
  + the DB-079 (b) fix (was 797 SLOC → now 450).
- `services/api/app/scenario/massing_guards.py` — NEW (172 SLOC): input boundary.
- `services/api/app/scenario/massing_triangulation.py` — NEW (234 SLOC): ring prep + triangulator + public API.
- `services/api/app/scenario/massing_mesh.py` — NEW (91 SLOC): prism/plate/mesh construction.
- `services/api/tests/scenario/test_massing_split_equivalence.py` — NEW: golden equivalence + DB-079 (b).
- `services/api/tests/scenario/test_massing_triangulation.py` — NEW: the public triangulator's tests.
- `project-control/reports/M5-T112-producer-report.md` — this report.

`test_massing_model.py` was left byte-identical (the DB-079 (b) test lives in the equivalence file);
it passes UNCHANGED through the facade, as does `test_scene_assembler.py` and `test_scene_api.py`.

## Module map (what moved where)

| Symbol | Claim-seam home | New home | Notes |
|---|---|---|---|
| `MassingModelError` | massing_model | **massing_guards** | typed refusal; re-exported |
| `_preview`, `MAX_ECHO_CHARS` | massing_model | **massing_guards** | bounded echo |
| `_is_finite_number` | massing_model | **massing_guards** | out-of-float-range int → non-finite |
| `MAX_COORD_ABS` | massing_model | **massing_guards** | magnitude bound |
| `_wrap_geos_errors` | massing_model | **massing_guards** | shapely boundary → typed |
| `_require_raw_vertices_in_nyc_bounds` | massing_model | **massing_guards** | NYC 2263 range |
| NYC_2263_* re-export | massing_model | **massing_guards** | single source = proposal |
| `_locate_overflow_field` (+ `_is_out_of_float_range_int`, `_outline_holds_overflow`) | — | **massing_guards** | NEW, DB-079 (b) |
| `_q`, `_QUANT_DECIMALS` | massing_model | **massing_triangulation** | coordinate quantiser |
| `_signed_area`, `_cross3`, `_point_in_triangle` | massing_model | **massing_triangulation** | geometry primitives |
| `_prepare_ring` | massing_model | **massing_triangulation** | ring preparation |
| `_WorkBudget`, `_min_ear_clip_work`, `MAX_TRIANGULATION_WORK` | massing_model | **massing_triangulation** | work budget |
| `_triangulate` | massing_model | **massing_triangulation** | ear clip (internal) |
| `Triangulation`, `triangulate_polygon` | — | **massing_triangulation** | NEW public reusable API (DB-082 a) |
| `_PrismMesh`, `_build_prism` | massing_model | **massing_mesh** | prism/plate mesh |
| builder orchestration (`build_massing_model`, `build_from_generated_option`, `_triangulate_distinct`, `_check_floor_cap`, `_expand_floor_stack`, `_check_output_size`, `_lot_polygon`, `_local_origin`, `_crs_frame`, `_digest`, `_canonical_block`, `_passthrough_provenance`, `MassingModel`, `_Floor`), CRS/source/version constants | massing_model | **massing_model (facade)** | kept in the facade |

Import DAG (no cycle): `proposal → massing_guards → massing_triangulation → massing_mesh → massing_model`.
The facade `from . import` of the siblings is level-1 (relative), so `test_t098_as5`'s absolute-import
allow-list check still passes (facade absolute roots ⊆ {hashlib, json, collections, dataclasses,
typing, shapely, __future__}).

### Why the builder orchestration stays in the facade (design note, not a deviation)

The accepted `test_massing_model.py` monkeypatches names ON the facade module object and drives the
builder through them: `mm._triangulate`, `mm._build_prism` (heavy_work fixture), `mm.MAX_TOTAL_FLOORS`,
`mm.MAX_TOTAL_MESH_VERTICES`, `mm.MAX_TRIANGULATION_WORK`, and `mm.Polygon`. For a `monkeypatch.setattr(mm, X, …)`
to take effect, the builder must resolve `X` from the FACADE's own globals at call time. So the builder
pipeline that references those names is kept in `massing_model.py` and consumes the split primitives as
re-exported facade globals. This preserves the exact call graph (zero behaviour change) while the three
reusable responsibilities (guards / triangulation / mesh) move to their own modules. The facade is 450
SLOC — well under the 600 warning threshold. Low-level primitives that are only invoked THROUGH the
already-resolved builder (`_build_prism`'s own `Polygon`, etc.) live in the submodules; the only
patched-Polygon tests raise at the first construction (`_lot_polygon`, in the facade), so they pass.

## Acceptance-scenario evidence

- **AS-1 (split + facade).** `massing_model.py` 450 SLOC (facade + builder), `massing_guards.py` 172,
  `massing_triangulation.py` 234, `massing_mesh.py` 91 — each < 600, each one responsibility. No circular
  import (DAG above; `python -c import` of the facade succeeds — all 813 tests import it). Every public
  name `scene_assembler.py`/tests import still imports from `massing_model` (re-exports verified by the
  813-test run).
- **AS-2 (equivalence).** Golden digests captured from the facade at the claim seam over the corpus
  (script `capture_golden.py`) and re-captured after the split; a byte `diff` shows EXACTLY ONE changed
  line — the DB-079 (b) level-outline field. `test_massing_model.py` (unchanged) + `test_scene_assembler.py`
  + `test_scene_api.py` pass (136 in that subset; 813 in the full suite). See equivalence table below.
- **AS-3 (public triangulator).** `triangulate_polygon(points, field, *, budget=None) -> Triangulation`
  (ring in; prepared CCW ring + CCW index triples out; the same `_WorkBudget` and the same typed
  `MassingModelError` refusals). `test_massing_triangulation.py`: convex square/octagon, concave L & U,
  collinear collapse, budget refusal, self-touching + too-few refusals, indices-into-prepared-ring;
  triangle-area-sum == polygon-area within `1e-9·area`. 10 named mutations reddened (table below).
- **AS-4 (DB-079 b).** The B0 `OverflowError` arm now sets `field=_locate_overflow_field(proposed_massing)`.
  Footprint overflow → `proposed_massing.outline` (UNCHANGED); a level-outline overflow →
  `proposed_massing.levels[<pos>].outline` (the fix). `test_db079b_level_outline_overflow_names_the_level_field`
  pins both; mutation M10 (revert the locator to the constant) reddens it. Message and `reason` (`non_finite`)
  are unchanged; only `field` moves.
- **AS-5 (scope).** Zero new dependencies (facade absolute roots ⊆ allow-list; guards adds only stdlib +
  `shapely.errors`; triangulation stdlib-only; mesh `numpy`+`shapely` already admitted). No route/app/main
  change. `ruff check .` clean; `modularity_check --check` exit 0; exactly the allowed paths modified.

## Equivalence table (claim seam → after split)

Successes — `content_hash` (sha256 over canonical `as_dict`), ALL byte-identical:

| case | digest (before == after) |
|---|---|
| rect | `sha256:b7fa9862…c5133b` (matches the accepted M5-T082 golden) |
| lshape | `sha256:f9c731b9…81a963` |
| ushape | `sha256:ff30bf8d…ad7582` |
| comb | `sha256:f5c661e6…343d60` |
| five_floor | `sha256:e23b5cbc…48a6c5` (matches the accepted M5-T088 golden) |
| multi_level_shared_outline | `sha256:6185b4e8…b6ea59` |
| generated_option | `sha256:67ae9323…64efad` |

Refusals — `(reason, field, message)`; ALL byte-identical EXCEPT the one DB-079 (b) row:

| case | reason | field before → after |
|---|---|---|
| footprint_outside_lot | footprint_outside_lot | `proposed_massing.levels[0].outline` (unchanged) |
| lot_too_few_vertices | invalid_source | `lot_ring` (unchanged) |
| non_finite_nan_lot | non_finite | `lot_ring[1]` (unchanged) |
| over_cap_vertices | over_cap_vertices | `lot_ring` (unchanged) |
| non_positive_height | invalid_source | `proposed_massing.levels[0].floor_to_floor_ft` (unchanged) |
| lot_out_of_nyc_bounds_4326 | lot_ring_out_of_nyc_bounds | `lot_ring` (unchanged) |
| keyhole_self_intersection | self_intersection | `lot_ring` (unchanged) |
| near_overflow_lot_1e154 | coordinate_out_of_range | `lot_ring[0]` (unchanged) |
| no_generated_candidate | no_generated_candidate | `max_envelope.candidate` (unchanged) |
| footprint_overflow_bigint | non_finite | `proposed_massing.outline` (unchanged) |
| **level_outline_overflow_bigint** | non_finite | **`proposed_massing.outline` → `proposed_massing.levels[0].outline`** (DB-079 b) |

Verbatim `diff` (claim-seam golden vs after-split golden):

```
20c20
<       "proposed_massing.outline",
---
>       "proposed_massing.levels[0].outline",
```

## Mutation table (in-process, consuming-namespace; NOT committed)

All baselines PASS; every mutant RED (detected). Runner: scratch `mutation_runner.py`.

| id | mutation (consuming namespace) | target test | mutant |
|---|---|---|---|
| M1 | `massing_triangulation._point_in_triangle` → `False` | test_area_sum…[concave_l/u] | RED |
| M2 | `massing_triangulation._cross3` → nonzero const (no collinear collapse) | test_exactly_collinear_vertices_collapse | RED |
| M3 | `massing_triangulation._WorkBudget.charge` → no-op | test_work_budget_overspend_is_refused | RED |
| M4 | `massing_triangulation._prepare_ring` w/o duplicate-vertex check | test_self_touching_ring_fails_closed | RED (message changes) |
| M5 | `massing_triangulation._prepare_ring` w/o `<3` guard | test_too_few_distinct_vertices… | RED (message changes) |
| M6 | `massing_triangulation._triangulate` drops the last triangle | test_returns_triangulation / convex area | RED |
| M7 | `massing_triangulation.MAX_TRIANGULATION_WORK` → 10 | test_budget_admits_a_realistic_ring | RED |
| M8 | `massing_triangulation._prepare_ring` re-appends the closing duplicate | test_indices_reference_prepared_ring | RED |
| M9 | `massing_model.GEOMETRY_VERSION` → 2 | test_success_content_hash[rect] (equivalence) | RED |
| M10 | `massing_model._locate_overflow_field` → const `"proposed_massing.outline"` | test_db079b_level_outline_overflow | RED |

Locator unit-probe: footprint-overflow → `proposed_massing.outline`; level-overflow → `proposed_massing.levels[0].outline`.

## Commands (explicit cwd; verbatim tails)

- [OBSERVED] cwd `services/api`: `python -m ruff check .` → `All checks passed!` (exit 0).
- [OBSERVED] cwd `services/api`: `python -m pytest tests/scenario -q` → `813 passed in 17.96s`.
- [OBSERVED] cwd `services/api`: `python -m pytest tests/scenario/test_massing_model.py tests/scenario/test_scene_assembler.py tests/scenario/test_scene_api.py -q` → `136 passed`.
- [OBSERVED] cwd `services/api`: `python -m pytest tests/scenario/test_massing_split_equivalence.py tests/scenario/test_massing_triangulation.py -q` → `30 passed`.
- [OBSERVED] cwd repo root: `python tools/modularity_check.py --check` → `selected 502 files; failures 0; warnings 26` (exit 0; massing_model.py no longer flagged — dropped below the justify threshold).
- [OBSERVED] SLOC (tools/modularity_check.source_lines): facade 450, guards 172, triangulation 234, mesh 91 (WARN=600, HARD=1000).

## Deviations

- The DB-079 (b) test was placed in `test_massing_split_equivalence.py` (which I own) rather than
  appended to the accepted `test_massing_model.py`, so the 1406-line accepted test file stays byte-identical
  (lowest risk for AS-2). The packet permitted editing `test_massing_model.py` only "if a DB-079 (b) test
  belongs there"; it is fully covered in the equivalence file, so I left the accepted file untouched.
- The builder orchestration remains in the facade (design note above) rather than moving into `massing_mesh.py`.
  This is required by the accepted tests' monkeypatch-on-facade contract; it is not an expansion of the
  facade's responsibility beyond "assemble the truth object", and the facade is 450 SLOC.

## OPEN QUESTIONS (owner asleep — recommended answers)

1. **DB-079 (b) scope: outline-only vs also `floor_to_floor_ft`.** `_locate_overflow_field` names only
   OUTLINE overflows (footprint + per-level outlines). A huge-integer `floor_to_floor_ft` (a JSON int
   literal ≳10**309) ALSO trips B0's `OverflowError`; the locator does not name it and falls back to the
   `proposed_massing.outline` default (UNCHANGED from the claim-seam behaviour). I scoped to outlines
   deliberately: the fixed refusal message says "carries a **coordinate**", which is honest for an outline
   vertex but would mislabel a height, and DB-079 (b) names "the level outline" specifically. **Recommendation:**
   accept the outline-only scope; if a precise `floor_to_floor_ft` label is wanted later, it needs a message
   variant and is a separate discovery (below), not this packet.
2. **Should `triangulate_polygon` be re-exported from the facade?** I did not add it to the facade (it is a
   NEW API consumed directly from `massing_triangulation` by DB-082 a). The facade `__all__` is unchanged
   (the accepted public surface). **Recommendation:** keep it in `massing_triangulation` only.

## DISCOVERIES (D-069 — route to docs/DISCOVERY_BACKLOG.md at the seam; not fixed here)

- **D-OBS (DB-079 residual):** the B0 `OverflowError` refusal message is a fixed "carries a coordinate…"
  string and its `field` is now outline-accurate, but a huge-integer `floor_to_floor_ft` overflow is still
  labelled `proposed_massing.outline` with a "coordinate" message (both slightly imprecise; still fails
  closed as `non_finite`). Realistic only from an unbounded JSON-int route input; unchanged from claim seam.
  Route to the next massing/proposal touch (relates to the carried-forward DB-079 (c) proposal.py:250 echo).
- **DB-082 (a) is now unblocked:** `triangulate_polygon` is the documented reusable triangulator the GLB
  cap export should call instead of its fan-from-vertex-0. Not consumed here (app/cad is forbidden scope).

## Requested status

Geometry implementation is submitted for independent mathematical and visual review; requested status:
awaiting_gate.

END-OF-REPORT
