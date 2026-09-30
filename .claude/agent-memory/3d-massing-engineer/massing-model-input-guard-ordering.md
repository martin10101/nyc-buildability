---
name: massing-model-input-guard-ordering
description: The fail-closed input-guard precedence in massing_model._prepare_ring and how to add a lot-only range check without breaking accepted tests
metadata:
  type: project
---

`services/api/app/scenario/massing_model.py` `_prepare_ring` guards run in a FIXED
precedence that accepted tests depend on: per-vertex (structure → non-finite →
magnitude `coordinate_out_of_range`) → optional lot NYC range check → close-dup drop →
duplicate check → `< 3` → orient CCW → collinear collapse → `< 3` collapsed.

**Why:** The lot ring is the ONE ring B0 (`app.scenario.proposal.validate_proposed_massing`)
never validates, so massing_model must range-check it itself. Two non-obvious ordering
constraints, each pinned by an accepted test:
1. The NYC range check must run on the RAW vertices BEFORE the collinear collapse
   (DB-069 a) — an out-of-range collinear spike (e.g. x=2e6 on a straight edge) is
   collapsed away and never seen if you check the collapsed ring.
2. But it must run AFTER the whole magnitude pass — `test_t088_as4_coordinate_magnitude_bound_is_inclusive`
   builds a ±1e8 lot and asserts a LATER over-1e8 vertex refuses `coordinate_out_of_range`/`lot_ring[1]`.
   A per-vertex NYC check fires on vertex[0] (also out of NYC) first and breaks that test.
   The fix is a SECOND pass: collect `raw` (x,y) in the magnitude loop, then
   `if nyc_range_check: _require_raw_vertices_in_nyc_bounds(raw, field)` — magnitude wins,
   NYC still pre-collapse.

**How to apply:** Enable the lot check via the keyword-only `_prepare_ring(..., nyc_range_check=True)`
(only `_lot_polygon` passes True; footprint/per-level rings are B0-range-checked upstream and
pass False — the direct `_prepare_ring` tests at 1e8 rely on that). Keep the refusal
`reason="lot_ring_out_of_nyc_bounds"`, `field="lot_ring"` (not indexed) — accepted T098
tests assert exactly `field == "lot_ring"`. NYC bounds are `proposal.NYC_2263_{X,Y}_{MIN,MAX}`
(900000/1100000 easting, 100000/300000 northing, US survey feet) — single source of truth,
never redefine. See [[massing-model-inprocess-mutation-harness]].
