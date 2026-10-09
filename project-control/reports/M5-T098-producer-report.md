# M5-T098 producer report — D-087 3D-1c: massing truth-object pre-wiring hardening (DB-061 a-d)

Producer: `3d-massing-engineer` (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t098` (branch `task/M5-T098-massing-prewiring`).
Claim-seam base: `2e0b2351`. Contract seam: `64fce622`.
Directives: D-087 (R001/R002/R003/R009), D-066 (R001).

## Scope delivered (exactly the allowed paths)

- `services/api/app/scenario/massing_model.py` — lot-ring NYC EPSG:2263 range check
  (reuses the B0 `NYC_2263_*` constants), shapely GEOS boundary wrap, documented
  no-content-dedupe on the output-size check.
- `services/api/tests/scenario/test_massing_model.py` — 11 ADDED tests (y-only
  magnitude, lot-CRS refusals, GEOS wrap, charge ordering, scope); one FORCED minimal
  reconciliation to an existing T088 test (deviation 1 below).
- `project-control/reports/M5-T098-producer-report.md` — this report.

`git diff --stat`: 2 files, +261 / −5. No forbidden path touched (`proposal.py` used
read-only as a public import; no route/app/web/cad/requirements change). Zero new
dependencies (functools is stdlib; GEOSException / NYC_2263_* are from already-admitted
shapely / the B0 proposal module). Module stays unwired (no production importer).

## What changed in the module (reference anchors, not verbatim)

1. Imports: added `functools`, `from shapely.errors import GEOSException`, and the four
   `NYC_2263_X/Y_MIN/MAX` constants from `.proposal` (extending the existing read-only
   proposal import — the "reuse the NYC_2263 constants" the packet names at proposal.py
   L72-75, the single source of truth also used by the B0 footprint check).
2. `_wrap_geos_errors` decorator (new) on `build_massing_model`: any `GEOSException`
   escaping the shapely engine on a build path becomes a typed `MassingModelError`
   (`reason="geometry_engine_error"`). A `MassingModelError` (a `ValueError`) is not a
   `GEOSException`, so typed refusals pass through unwrapped. `build_from_generated_option`
   is covered transitively (it delegates to `build_massing_model`).
3. `_require_lot_ring_in_nyc_bounds(ring)` (new), called in `_lot_polygon` right after
   `_prepare_ring` and before any shapely construct: a lot vertex outside
   `[NYC_2263_X_MIN, X_MAX] x [Y_MIN, Y_MAX]` refuses `MassingModelError`
   (`reason="lot_ring_out_of_nyc_bounds"`, `field="lot_ring"`). This is the same range
   check B0 applies to the proposal footprint; the lot arrives as a separate argument B0
   never sees, so without it a 4326 / metric lot mislabels downstream as
   `footprint_outside_lot`.
4. `_check_output_size` docstring: documents that the total INTENTIONALLY does not
   content-dedupe (DB-061 f / G3-A3) — each floor emits its own prism; only the
   triangulation WORK is deduped, never the emitted vertex COUNT.
5. Module docstring: added an M5-T098 paragraph describing the two new guards. Honesty
   vocabulary preserved (no "permitted/approved/maximum allowed" wording;
   `test_as5_module_has_no_permitted_or_maximum_allowed_wording` passes).

## Commands run (verbatim; explicit cwd)

### Ruff — [OBSERVED] PASS
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t098\services\api`
`python -m ruff check .`
→ `All checks passed!`

### Full suite — [OBSERVED] PASS (54 pre-existing + 11 added = 65)
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t098\services\api`
`python -m pytest tests/scenario/test_massing_model.py -q`
→ `65 passed in 0.62s`
(Local Python 3.11; CI is 3.12. The suite is deterministic/offline — no runner-sensitive
values changed; goldens unchanged, see AS-5.)

### Modularity — [OBSERVED] PASS (0 failures)
cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t098`
`python tools/modularity_check.py --check`
→ `selected 488 files; failures 0; warnings 26`; massing_model.py is a `review_signal`
WARN ("consider the module boundary before growing it further"), NOT a failure. Cohesion
justification (carries forward the G3-recorded one): the module has ONE responsibility —
the deterministic massing truth object and its fail-closed section-10 guards; the new lot
NYC-range check and the GEOS boundary wrap belong to that same guard family, not a
separable concern. File is 894 lines total.

## Per-acceptance-scenario evidence

### AS-1 (y-axis bound; mutant MD reddens) — [OBSERVED] PASS
- Added `test_t098_as1_y_only_magnitude_violation_is_refused`: a small-x / over-bound-y
  ring (`[[0, 1e8+1], ...]`) is refused `coordinate_out_of_range` at `f[0]` via
  `_prepare_ring` (the bound is CRS-agnostic and lives there; the build paths
  NYC-range-gate at a far tighter bound first). Added
  `test_t098_as1_y_only_magnitude_bound_is_inclusive` (y == 1e8 accepted).
- Mutation MD (drop `or abs(y) > MAX_COORD_ABS`): see mutation table — REDDENED
  (`DID NOT RAISE`).

### AS-2 (lot CRS range; removing the check reddens) — [OBSERVED] PASS
- Added `test_t098_as2_lot_ring_in_4326_degrees_is_refused_naming_lot_ring`,
  `..._in_metres_is_refused_naming_lot_ring`, `..._reuses_the_b0_footprint_bounds`
  (each asserts `reason="lot_ring_out_of_nyc_bounds"`, `field="lot_ring"`), and
  `..._in_range_lot_is_unaffected_golden_unchanged` (in-NYC lot → the accepted golden
  `sha256:b7fa98…5133b`, no behaviour change).
- Mutation (remove the check): see mutation table — all three REDDENED, the removal
  reproducing exactly the `footprint_outside_lot` mislabel the check prevents.

### AS-3 (typed errors; spy proves the wrap) — [OBSERVED] PASS
- Added `test_t098_as3_geos_exception_is_wrapped_as_massing_error` (monkeypatches
  `mm.Polygon` to raise `GEOSException`, asserts a `MassingModelError`
  `reason="geometry_engine_error"` and that the spied construct really ran),
  `..._generated_option_path_also_wraps_geos` (the generated-option entry path),
  and `..._typed_refusal_passes_through_the_geos_wrap_unchanged` (a real
  `footprint_outside_lot` refusal is not swallowed/re-wrapped). Proven via a spy, not a
  real GEOS crash, per the packet.
- Mutation (remove `@_wrap_geos_errors`): see mutation table — REDDENED (raw untyped
  `shapely.errors.GEOSException` escaped both build paths).

### AS-4 (charge ordering; mutant ME reddens) — [OBSERVED] PASS
- Added `test_t098_as4_scan_units_charged_before_the_inner_scan`: a regular octagon with
  `_WorkBudget(n-3)` overspends exactly at the `m-3` charge; a `_point_in_triangle` spy
  proves 0 inner-scan calls (charge-before). Mutant ME makes this `n-3 = 5`.
- Mutation ME (move `budget.charge(m-3, field)` after the inner scan): see mutation table
  — REDDENED (`assert 5 == 0`).

### AS-5 (no behaviour change + scope) — [OBSERVED] PASS
- Both accepted goldens unchanged: `sha256:b7fa98…5133b` (1-floor RECT) and
  `sha256:e23b5c…a6c5` (5-floor) still assert green; the 54 pre-existing tests pass
  (one had a forced minimal edit — deviation 1). Added
  `test_t098_as5_module_imports_no_route_or_web_and_no_new_dependency` (AST import-root
  allowlist + no fastapi/route/app.main/app.api/app.cad/http-client string). Zero new
  dependencies; unwired; exactly the 3 allowed paths (`git status` clean otherwise).

## Mutation table (all four required mutations REDDEN)

Method: back up module → apply one mutation → run the targeted added test(s) → observe
red → restore from backup. Restore verified (final suite `65 passed`, ruff clean).

| # | Mutation | Target test(s) | Observed result |
|---|---|---|---|
| MD | drop `or abs(y) > MAX_COORD_ABS` in `_prepare_ring` | `test_t098_as1_y_only_magnitude_violation_is_refused` | `Failed: DID NOT RAISE MassingModelError` — REDDENED |
| lot-range | replace `_require_lot_ring_in_nyc_bounds(ring)` with `pass` | `test_t098_as2_...4326`, `...metres`, `...reuses_the_b0_footprint_bounds` | 3 FAILED; reason became `footprint_outside_lot` not `lot_ring_out_of_nyc_bounds` — REDDENED (mislabel reproduced) |
| GEOS-wrap | remove `@_wrap_geos_errors` from `build_massing_model` | `test_t098_as3_geos_exception_is_wrapped_as_massing_error`, `..._generated_option_path_also_wraps_geos` | 2 FAILED; raw `shapely.errors.GEOSException` escaped uncaught — REDDENED |
| ME | move `budget.charge(m-3, field)` to AFTER the inner `any(_point_in_triangle...)` scan | `test_t098_as4_scan_units_charged_before_the_inner_scan` | `assert 5 == 0` — REDDENED (inner scan ran n-3 times before the charge) |

## Deviations

1. FORCED minimal edit to an existing test (deviation from "only ADD tests"), fully
   disclosed. `test_t088_as4_coordinate_magnitude_bound_is_inclusive` built a lot at
   ±`MAX_COORD_ABS` (±1e8) and asserted it BUILDS successfully. A ±1e8 lot is precisely
   the wrong-CRS/out-of-range case AS-2 now refuses (its corners at −1e8 are below
   `NYC_2263_X_MIN`, and +1e8 is above `X_MAX`), so with the required NYC lot check that
   assertion can no longer hold — the two binding requirements (AS-2 vs. this one
   assertion) are irreconcilable. Resolution: the test's other coverage is preserved
   byte-for-byte; ONLY the "±1e8 lot builds" lines (3 lines) were replaced with an
   equivalent magnitude-bound-inclusive proof on `_prepare_ring` directly (a coordinate
   exactly AT 1e8 is accepted) — CRS-agnostic, where the magnitude bound actually lives.
   The subsequent `lot[1] = [1e8+0.5, ...]` refusal (asserts `coordinate_out_of_range`,
   `lot_ring[1]`) and the `_prepare_ring([[1e9,...]])` refusal are UNCHANGED and still
   pass, because `_prepare_ring`'s magnitude check fires before the NYC check. Net: no
   loss of magnitude-bound coverage; the ±1e8 lot's former build-success (a latent bug
   this task fixes) is the only behaviour retired. Reviewers should confirm this
   reconciliation is acceptable; it is the minimal change that satisfies AS-2 without
   leaving a red existing test.

2. Reason-vocabulary addition: introduced one new typed reason
   `lot_ring_out_of_nyc_bounds` (distinct from the overflow-guard `coordinate_out_of_range`
   and from `footprint_outside_lot`) so a UX packet surfacing reasons (DB-061 e) can tell
   a wrong-CRS lot apart from a magnitude overflow and from a misplaced footprint. No new
   dependency; honest, self-descriptive.

## Assumptions / limitations

- The four `NYC_2263_*` constants are imported from `proposal.py`. They are module-level
  public names (no leading underscore) and are NOT in proposal.py's `__all__`. The packet
  binds "reuse the NYC_2263 constants" and points at proposal.py L72-75; M5-T095 is
  changing proposal.py's validation TIME BUDGET with an unchanged public surface and does
  not touch these domain range constants (stable since M5-T048). Reuse (single source of
  truth) was chosen over a local duplicate to avoid drift; if a reviewer prefers, a local
  mirror is a trivial swap. Low integration risk noted.
- Local runs are Python 3.11; CI runs 3.12. The suite is deterministic and offline, and no
  runner-sensitive numeric output changed (goldens identical), so behaviour is not
  runner-dependent. CI on the pushed head is the authoritative 3.12 evidence.
- The module remains UNWIRED (no route / GLB export); these are before-wiring guards only.

## DISCOVERIES (routed to the orchestrator; NOT fixed in-packet)

- D1 (from deviation 1): the accepted T088 fixture `test_t088_as4_coordinate_magnitude_bound_is_inclusive`
  encoded a ±1e8 lot building successfully — a latent expression of the DB-061(c) /
  G5 F-LOW-2 wrong-CRS-lot gap. This packet corrects it. If the orchestrator wants the
  magnitude-inclusivity of the LOT-ARGUMENT boundary retested independently of the NYC
  gate, that is inherently untestable through the lot path now (the NYC gate is tighter);
  it lives correctly on `_prepare_ring`. No further action needed — recorded for the
  DB-061 seam sweep.
- D2 (DB-061 b residual, non-blocking): the ME charge-ordering guard is now pinned. The
  broader G4 ADVISORY-2 note that the up-front `least > MAX` refusal is the real runaway
  guard still holds; nothing to change.
- No new product/domain defect found. DB-061 (e) precedence and (f) no-dedupe are now
  documented in-module; (a)-(d) implemented and mutation-pinned.

## Requested status

Geometry implementation is submitted for independent mathematical and visual review;
requested status: awaiting_gate.

END-OF-REPORT
