# M5-T116 producer report — D-087 export-service pre-mount hardening (DB-082 a, c, f, g, h)

- Task: M5-T116 (backend). Producer: backend-engineer (orchestrator-dispatched subagent).
- Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t116`, branch `task/M5-T116-export-glb-concave`.
- Parent (claim seam): `c375457cfbe996454cf63a0554f7aa6f31bc0c94`. This is the sole task commit;
  its sha is reported in the producer return.
- Files changed (only allowed paths):
  - `services/api/app/cad/export_service.py`
  - `services/api/tests/cad/test_export_service.py`
  - `project-control/reports/M5-T116-producer-report.md`
- Directives: D-087 (R001/R002/R003/R006/R009), D-083-R001, D-066-R001. Route stays UNMOUNTED;
  `app/main.py` untouched; zero new dependencies (stdlib + already-admitted only); no network.

## What changed (by DB-082 rider)

### (a) Concave-safe GLB caps via the public triangulator
`_build_prism_mesh` (export_service.py:381) now builds the bottom and top caps from
`app.scenario.massing_triangulation.triangulate_polygon` (imported READ-ONLY) instead of the
vertex-0 fan. Call site: export_service.py:403 `triangulate_polygon(footprint, field="building_ring")`.
- The triangulator returns the PREPARED CCW ring (closing dup dropped, exactly-collinear vertices
  collapsed, oriented CCW) + CCW triangle index triples INTO that ring. Both caps AND the side walls
  use that SAME prepared ring, so caps and walls share one boundary and one winding.
- Winding kept outward as `glb_writer` expects: bottom cap faces -z (the CCW-from-above triangles
  are reversed: `[a, c, b]`), top cap faces +z (kept, on the top ring: `[n+a, n+b, n+c]`).
- Its typed `MassingModelError` is mapped to the service's ONE reconciled refusal shape by
  `_reconcile_triangulation` (export_service.py:319), caught in `_render_glb`
  (export_service.py:477). The detail is server-built from the fixed `reason` code only; the
  triangulator's own message (which can interpolate a caller coordinate/vertex) is discarded
  (DB-059 (h)).

Where the footprint is range-/finiteness-checked BEFORE triangulation (packet requirement):
1. Service `_coerce_footprint` (export_service.py:~296): pair-shape + numeric coercion (hostile
   `__float__`/`TypeError`/`ValueError`/`OverflowError` → `non_numeric_coordinate`), drops the
   closing duplicate, requires ≥3 distinct vertices.
2. Triangulator `_prepare_ring` (massing_triangulation.py): **finiteness** `_is_finite_number(x)`/
   `_is_finite_number(y)` at massing_triangulation.py:114-117; **coordinate magnitude bound**
   `abs(x) > MAX_COORD_ABS` (1e8) at :118-122; **vertex cap** `MAX_OUTLINE_VERTICES` (1000) at
   :102-105; duplicate-vertex → `self_intersection` at :136-139.
3. The **lot-only NYC range check** (`_require_raw_vertices_in_nyc_bounds`) is DELIBERATELY OMITTED
   on the footprint path: `nyc_range_check` defaults `False` (massing_triangulation.py:81) and the
   docstring at :283-285 states the omission — this matches **M5-T112 G5 INFO-1 / DB-084 (d)** (a
   footprint reaching the exporter is expected B0/NYC-validated upstream).
4. The GLB writer re-validates independently: local-coordinate bound `MAX_LOCAL_COORD_ABS_FT`
   (100 000 ft) at glb_writer.py:393-399, finiteness `_real` at :261-273, degeneracy
   `_check_triangles` at :430-444, frame-origin bound `_check_frame`.

### (c) Fallback filename token re-allowlisted
A single choke point `_allowlist_token` (export_service.py:205) is used by BOTH `build_filename_token`
and the new `_sanitize_fallback_token` (export_service.py:226), so the two allowlist paths can never
drift. `build_export` now re-allowlists the fallback before `content_disposition`
(export_service.py:547: `token = _sanitize_fallback_token(fallback_token)`); a fallback that
allowlists to nothing uses the caller-free `_DEFAULT_TOKEN`.

### (f) Four-field screen coverage (tests)
The claim-word and length screens are now tested over ALL FOUR caller text fields
(`address`, `bbl`, `generated_at`, `generator_version`) via `es._TEXT_FIELDS` parametrization, with a
mandatory mutation that narrows the set to `("address",)` and shows the other three slip through
(the exact former coverage gap, M5-T109 G4 A1 / DCV F2). Code was already correct; this closes the
test debt.

### (g) Floor-cap edge pinned
`test_floor_cap_edge_2000_accepted_2001_refused`: exactly `MAX_FLOORS` (2000) renders, 2001 refuses
`floor_cap_exceeded`; mutation lowers `MAX_FLOORS` to 1999 and shows the legal 2000-floor export then
refuses.

### (h) Docstring fix
The module docstring GLB-DEDUPE bullet (export_service.py:37-41) now discloses the dedupe in
`ExportResult.provenance['glb_massing']` and explicitly states it is NOT in the file's
`asset.extras` (M5-T109 G3 A4). A new CONCAVE-SAFE GLB CAPS bullet documents the triangulator use.

## GLB before/after (scope disclosure)
- Convex fixture (`_BUILDING`, a CCW rectangle) GLB sha256:
  - before: `2bcfd4c825b2eceba37633ee78e80cd1ab6dba67a409f7a8f4ded54d08277046`
  - after:  `146797d2c585aded91ad98657f81598971bc85e6139f99f7696b9a03daf8c52c`
  - length unchanged (1680 bytes). ONLY the cap triangle INDEX triples change (ear-clip produces a
    fan from the last vertex, not vertex 0); vertex POSITIONS and the walls are identical because a
    CCW convex rectangle's prepared ring equals its input order (pinned by
    `test_convex_prepared_ring_is_unchanged_so_only_the_triangulation_differs`). This is exactly the
    "convex output may change only where the triangulation differs" allowance.
- DXF and PDF outputs: byte-identical (they never route through `_build_prism_mesh`).
- Owner samples (`test_cad_owner_samples.py`): byte-identical and PASS unchanged. Note its
  `example-massing.glb` is a synthetic box assembled in the test via `write_glb` directly — it does
  NOT use `_build_prism_mesh`, so my change cannot affect that golden.

## Mutation table (each guard proven load-bearing)
| # | Guard | Mutation (type) | Observed |
|---|-------|-----------------|----------|
| 1 | (a) concave caps | SOURCE: caps reverted to vertex-0 fan | `test_glb_caps_lie_inside...[L]` and `[U]` FAILED (|area| 4200 vs 3000 for U — fan over-counts); `[convex]` still passed. Restored. |
| 2 | (a) concave caps | in-process: `es.triangulate_polygon`→fan over the prepared ring | `test_vertex0_fan_mutation_reddens_for_a_concave_footprint` PASS (mutant area>footprint or centroid outside) |
| 3 | (a) refusal reconcile | in-process: neuter `es._reconcile_triangulation` | `test_glb_triangulation_refusal_mutation_reddens` PASS (raw `MassingModelError` escapes vs a redacted refusal) |
| 4 | (c) fallback allowlist | in-process: `es._sanitize_fallback_token`→identity | `test_fallback_token_re_allowlist_mutation_reddens` PASS (raw quote leaks into filename) |
| 5 | (f) four-field screen | in-process: `es._TEXT_FIELDS`→`("address",)` | `test_text_field_set_narrowing_reddens_the_non_address_fields` PASS (bbl/generated_at/generator_version slip through) |
| 6 | (g) floor-cap edge | in-process: `es.MAX_FLOORS`→1999 | `test_floor_cap_edge_mutation_reddens` PASS (legal 2000-floor export refuses) |

Existing mutations preserved and still green (ring_cap, floor_cap, text_cap, claim_word_screen,
filename_token).

## Self-checks (explicit cwd; each [OBSERVED])
- cwd `services/api`: `python -m ruff check .` → [OBSERVED] `All checks passed!`
- cwd `services/api`: `python -m pytest tests/cad -q` → [OBSERVED] `458 passed in 4.73s` (was 435;
  +23 new; `test_cad_owner_samples.py` included and unchanged).
- cwd repo root: `python tools/modularity_check.py --check` → [OBSERVED] exit 0 (only pre-existing
  warnings on unrelated files: `max_envelope.py`, `tools/agent_supervisor/*`; `export_service.py`
  is not flagged).
- Env: Python 3.11.9, ruff 0.13.0. Full exec + local test run available this session.

## Per-AS evidence
- AS-1 (concave GLB caps): `test_glb_caps_lie_inside_the_footprint_and_sum_to_its_area[L|U|convex]`
  (area-sum + containment + winding oracle computed IN the test), `test_concave_footprint_export_produces_valid_glb`,
  and mutations #1 (source) and #2 (in-process). PASS.
- AS-2 (refusals): `test_self_intersecting_footprint_is_a_reconciled_typed_refusal`,
  `test_triangulator_refusal_reason_is_reconciled_without_caller_text`, the pre-existing
  `test_reconciled_refusal_never_echoes_a_hostile_coordinate` (now via the triangulation path →
  `coordinate_out_of_range`, no coordinate echoed), mutation #3. Upstream range-check location stated
  above. PASS.
- AS-3 (fallback token): `test_fallback_token_is_re_allowlisted_before_content_disposition`,
  `test_empty_fallback_uses_the_server_default`, mutation #4. PASS.
- AS-4 (screens + edges): `test_claim_word_screen_covers_every_caller_text_field[4]`,
  `test_length_screen_covers_every_caller_text_field[4]`, `test_floor_cap_edge_2000_accepted_2001_refused`,
  mutations #5 and #6. PASS.
- AS-5 (scope): DXF/PDF/owner-samples byte-identical (owner-samples test PASS); docstring fixed;
  zero new dependencies; route UNMOUNTED (`app/main.py` untouched); ruff clean; modularity exit 0;
  only the three allowed paths changed.

## Deviations
None. The `_coerce_footprint` guard is kept (it runs before the triangulator) to preserve the
`non_numeric_coordinate` reject code for the hostile-`__float__` case.

## OPEN QUESTIONS (owner asleep; recommended answers)
- OQ-1: The GLB footprint effective vertex cap now drops from the service's 10 000 raw-ring cap to
  the triangulator's `MAX_OUTLINE_VERTICES` = 1000 (a 1001–10000-vertex footprint that previously
  rendered via the fan is now a typed `over_cap_vertices` refusal). RECOMMEND: accept as a
  fail-closed narrowing — realistic NYC footprints are far under 1000 vertices, and the shared
  outline cap is the right single source of truth. No code change needed; disclosed here and in the
  test module docstring.
- OQ-2: A true crossed bowtie (edges cross, no repeated vertex) is not detected by ear-clipping
  alone and may still yield a mesh; the reachable typed refusals are duplicate-vertex/non-simple
  (`self_intersection`), `coordinate_out_of_range`, `non_finite`, `over_cap_vertices`, and (proven by
  a patched mutant) `triangulation_budget_exceeded`. RECOMMEND: this is a `triangulate_polygon`
  property owned by M5-T112, not this packet; recorded as a DISCOVERY (DB below) for the PKT-H mount
  to weigh a pre-simplicity check if bowtie inputs are ever reachable. Route is UNMOUNTED, so no
  live exposure now.

## DISCOVERIES (route to docs/DISCOVERY_BACKLOG.md at the seam; not fixed in-packet)
- D-a: `triangulate_polygon` (ear-clipping) does not reject every self-intersecting polygon — a
  crossed bowtie with distinct vertices can triangulate without a stall (empirically confirmed:
  `[(0,0),(60,60),(60,0),(0,60)]` and `[(0,0),(40,0),(0,40),(40,40)]` are NOT refused; a
  duplicate-vertex ring IS refused `self_intersection`). Owned by M5-T112 / massing_triangulation;
  relevant to the PKT-H GLB mount if untrusted footprint geometry can be a bowtie. Ties to DB-084.
- D-b: Effective GLB footprint vertex cap is now 1000 (the outline cap), below the service's 10 000
  raw-ring cap (OQ-1). Fail-closed; disclosed.

END-OF-REPORT
