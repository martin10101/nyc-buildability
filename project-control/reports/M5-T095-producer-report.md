# M5-T095 producer report — proposal-validation time budget (closes M5-T088 F-HIGH-1)

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t095` (branch
`task/M5-T095-proposal-validation-budget`), reset to claim-seam `a749d995` before work.
Local Python 3.11.9, shapely 2.0.7 (CI is 3.12 — commands routed accordingly below).

## What changed (allowed paths only)

1. `services/api/app/scenario/proposal.py`
   - New request-level bound `MAX_TOTAL_OUTLINE_POSITIONS = 20000` (added to `__all__`) and
     helpers `_outline_position_count` / `_check_total_positions`; `validate_proposed_massing`
     now calls `_check_total_positions(block)` immediately after the `isinstance(block, dict)`
     guard and **before** `_validate_outline`, so an oversized request is refused before any
     per-outline geometry runs.
   - `_ring_is_simple` keeps conditions (1) zero-length edge and (2) 180-degree reversal spike
     as the cheap `O(n)` scans (byte-identical to phase B0), and delegates condition (3)
     (non-adjacent edge self-intersection) to the new `_ring_boundary_is_simple`, which decides
     it with shapely `Polygon(...).is_valid` (GEOS sweepline, ~`O(n log n)`), replacing the
     former hand-rolled all-pairs `O(n^2)` scan.
   - Removed the now-unused `_orientation` / `_on_segment` / `_segments_intersect` helpers (they
     served only the all-pairs loop; `derivation.py` keeps its own independent copies, verified).
   - Added `from shapely.errors import GEOSException` and `from shapely.geometry import Polygon`
     (already-admitted package — no requirements change). Docstring updated to match.
   - Public surface preserved exactly: `validate_proposed_massing`, `ProposedMassingError`, all
     existing `MAX_*` constants and every refusal field/message are unchanged; the only addition
     is the new `MAX_TOTAL_OUTLINE_POSITIONS` constant.

2. `services/api/tests/scenario/test_proposal_validation_budget.py` — replaces the seeded
   placeholder. 18 tests covering AS-1..AS-5, incl. a self-contained copy of the pre-M5-T095
   predicate (`_all_pairs_ring_is_simple`) used both as the equivalence oracle and as the
   "restore the all-pairs loop" mutant.

3. `project-control/reports/M5-T095-producer-report.md` — this report.

## Design decision: hybrid check, empirically chosen for decision identity

A standalone probe (scratch, not committed) compared the old predicate against three shapely
candidates over **400,000 random rings** across all required categories:

- Pure `LinearRing.is_simple`/`is_valid` and pure `Polygon.is_valid` each **disagreed** with the
  old check on ~0.006% of cases — always **consecutive-duplicate vertices** (zero-length edges),
  which shapely silently tolerates but the old condition (1) rejects.
- The **hybrid** (keep O(n) conditions 1+2 exactly; shapely only for condition 3) had **ZERO
  disagreements** across 360,000 cases (74,546 True / 285,454 False — both answers well
  exercised), for all three shapely predicates. `Polygon.is_valid` was chosen to match the
  precedent already trusted for the lot in `massing_model.py`.

## Measurements (this PC, Python 3.11.9, shapely 2.0.7) [OBSERVED]

cwd `services/api`, via a scratch harness on `PYTHONPATH=services/api`.

| Quantity | Value |
|---|---|
| old all-pairs `_ring_is_simple`, one 999-distinct-vertex ring | **1377 ms** |
| new shapely `_ring_is_simple`, same ring | **10.3 ms** (~133x faster) |
| all-pairs non-adjacent pairwise segment tests at n=999 | **497,502** ( = 999*996/2 ) |
| new shapely `Polygon` constructions at n=999 | **1** (O(1) per outline) |
| BEFORE worst allowed request (501 outlines x 1000 positions), 20x OBSERVED = 23.8 s | **~597 s (~9.9 min)** [OBSERVED 20x, linear extrapolation x25] |
| AFTER worst allowed request (20,000 positions) as 20x1000 | **53 ms** |
| AFTER worst allowed request (20,000 positions) as 500x40 | **87 ms** |

The `MAX_OUTLINE_VERTICES = 1000` ceiling **includes** the closing vertex, so the largest ring the
simplicity check ever sees through the public validator is **999 distinct** vertices; all worst-case
numbers use that. Net: worst single validator-valid request drops from ~10 minutes to <0.1 s
(~4 orders of magnitude), and per-outline simplicity from `O(n^2)` to ~`O(n log n)`.

## Per-acceptance-scenario evidence

Commands run from `services/api` unless noted. All [OBSERVED] on this PC (Py 3.11); the identical
commands run in CI on Py 3.12.

### AS-1 — total-positions bound refuses before any simplicity check [OBSERVED]
- `test_over_budget_request_is_refused_typed`: a 21,000-position request raises
  `ProposedMassingError(field="proposed_massing")` naming `MAX_TOTAL_OUTLINE_POSITIONS`.
- `test_total_bound_refuses_before_any_simplicity_check`: a spy wrapping `_ring_is_simple` shows
  **call_count == 0** when the oversized request is refused (bound fires first).
- `test_total_bound_boundary_is_pinned`: exactly `MAX_TOTAL_OUTLINE_POSITIONS` (20,000) positions
  passes the total check; **20,001** raises. Boundary pinned (`>` refuses, `==` passes).
- `test_total_bound_sums_footprint_and_all_level_outlines`: footprint + one level, each just over
  half the bound, together exceed it and are refused (the sum is what is bounded).
- `test_position_count_ignores_malformed_outlines`: `_outline_position_count` returns 0 for
  malformed shapes so the aggregate bound never masks an existing typed field error.
- **Mutation (AS-1):** `test_removing_the_total_bound_reddens_the_zero_call_guard` — with
  `_check_total_positions` monkeypatched to a no-op, the same request DOES reach the per-outline
  simplicity check (spy call_count > 0), so the zero-call guard reddens. Confirmed OBSERVED.

### AS-2 — bounded simplicity, measured, mutation guard [OBSERVED]
- `test_worst_case_simplicity_does_no_pairwise_python_work`: at the max ring (999 vtx) the new
  check builds exactly **1** shapely polygon and performs **0** Python pairwise segment tests
  (`<= WORK_BUDGET_PAIRWISE_TESTS = 50,000`).
- `test_worst_case_simplicity_wall_time_bounded`: new `_ring_is_simple(999-gon)` completes in
  `< 0.5 s` (measured ~10 ms; ~50x margin).
- `test_worst_case_allowed_request_validates_quickly`: 20 outlines x 999 (the 20,000-position
  worst case) validate geometry in `< 2.0 s` (measured ~53 ms).
- **Mutation (AS-2):** `test_restoring_all_pairs_loop_reddens_work_count_guard` — the all-pairs
  predicate on the same ring performs **497,502** pairwise tests (`= n*(n-3)/2`), far above the
  50,000 work budget the shapely check satisfies at 0. Restoring the all-pairs loop reddens the
  work-count guard. (The old scan also took ~1.38 s, which exceeds the 0.5 s wall-time guard.)

### AS-3 — decision identity [OBSERVED]
- Standalone probe: **360,000** cases, 0 disagreements (hybrid), all categories.
- Committed regression corpus (deterministic seeds): `test_fuzz_equivalence_small_and_targeted`
  = **24,000** mixed cases (random, small-grid, convex, bow-tie, self-touch, collinear overlap,
  spike, near-degenerate, collinear-flat, consecutive/ non-adjacent repeats, vertex-on-edge),
  both True and False outcomes exercised; `test_fuzz_equivalence_medium_and_extreme_rings` =
  **150** rings of 60..300 vtx + **3** at 999 vtx; `test_known_shapes_decided_identically` = 6
  canonical shapes. Every case: `proposal._ring_is_simple(r) == _all_pairs_ring_is_simple(r)`.
  **Total committed corpus size = 24,159 rings. Disagreements = 0.**
- Every existing consumer test passes UNCHANGED: full documented suite = **312 passed** (see
  Commands). No disagreement was found; none had to be disclosed or ruled on.

### AS-4 — fail closed; shapely exceptions never escape untyped [OBSERVED]
- `test_shapely_exception_never_escapes_from_ring_check`: `Polygon` patched to raise
  `GEOSException` -> `_ring_is_simple` returns `False` (fails closed), no escape.
- `test_shapely_exception_surfaces_as_typed_refusal_through_public_api`: through
  `validate_proposed_massing` the GEOS error becomes the typed
  `ProposedMassingError(field="proposed_massing.outline", "self-intersecting")`, never a raw
  `GEOSException`.
- `test_non_finite_and_degenerate_keep_their_typed_refusals`: a NaN coordinate and a bow-tie keep
  their exact pre-change typed refusals.

### AS-5 — scope [OBSERVED]
- `test_public_surface_and_valid_block_unchanged`: `ProposedMassingError` is a `ValueError`;
  all documented `MAX_*` names + `validate_proposed_massing` + `ProposedMassingError` in
  `__all__`; a valid block validates to `None`.
- `test_no_new_dependency_only_admitted_shapely`: the simplicity check uses
  `shapely.geometry.Polygon` (admitted); no requirements/lockfile change; no network in code or
  tests. `git status` shows exactly the three allowed paths changed.

## Commands (cwd noted; verbatim tails) [OBSERVED]

```
# cwd: services/api
$ python -m ruff check .
All checks passed!

# cwd: services/api
$ python -m pytest tests/scenario/test_proposal_validation_budget.py -q
18 passed in 12.92s

# cwd: services/api  (documented full command)
$ python -m pytest tests/scenario/test_scenario_proposal.py \
    tests/scenario/test_proposal_validation_budget.py \
    tests/scenario/test_scenario_derivation.py tests/scenario/test_max_envelope.py \
    tests/api/test_proposal_validation_api.py tests/api/test_proposal_checks_api.py \
    tests/api/test_max_envelope_api.py -q
312 passed in 26.83s

# cwd: repo root
$ python tools/modularity_check.py --check
selected 488 files; failures 0; warnings 26   (EXIT=0; no warning for proposal.py)
```

## Mutation table

| Mutation | Guard that reddens | Observed |
|---|---|---|
| Remove `_check_total_positions` (drop the total bound) | `test_removing_the_total_bound_reddens_the_zero_call_guard` (`_ring_is_simple` spy call_count goes 0 -> >0) | reddens [OBSERVED] |
| Restore the all-pairs `O(n^2)` loop | `test_restoring_all_pairs_loop_reddens_work_count_guard` (pairwise tests 497,502 > 50,000 budget) + the 0.5 s wall-time guard | reddens [OBSERVED] |

## Deviations / assumptions
- The task title says "`O(n log n)`-class simplicity check". Implemented as shapely GEOS polygon
  validity (a sweepline), which is that class; conditions (1)+(2) remain O(n) and unchanged.
- `MAX_TOTAL_OUTLINE_POSITIONS = 20000` is a new value chosen far above any hand-authored
  proposal (e.g. 20 detailed 999-vtx outlines, or 500 x 40-vtx) and far below the runaway region;
  it is additive and does not refuse any existing fixture (312 consumer tests pass unchanged).
- `MAX_TOTAL_OUTLINE_POSITIONS` added to `__all__` for consistency with the module's other
  exported `MAX_*` bounds; this is additive and changes no existing name.
- Worst-case numbers use 999 distinct vertices (the true max through the public validator, since
  `MAX_OUTLINE_VERTICES` counts the closing vertex).

## DISCOVERIES (out of scope — not fixed in-packet; for docs/DISCOVERY_BACKLOG.md)
1. `derivation.py` (`app/scenario/derivation.py:314-363`) carries its OWN copy of the same
   hand-rolled `_orientation`/`_on_segment`/`_segments_intersect` all-pairs simplicity logic
   (used in `derive_proposal`). It has the same `O(n^2)` shape but is bounded by the already
   validated `proposed_massing` (re-validated on entry). If derivation is ever run on larger or
   less-trusted geometry, it should adopt the same shapely check; a shared geometry helper module
   would remove the duplication. Forbidden path here — route to a derivation-touching packet.
2. DB-034(a) is now addressed for `proposal.py`. The route-level defence (M5-T088 G5 fix (b): run
   validation in a cancellable job with a per-request wall-clock timeout + rate limit) is still
   required at the public-exposure packet — the in-process bound reduces but does not remove the
   need for it once user geometry is wired.

END-OF-REPORT
