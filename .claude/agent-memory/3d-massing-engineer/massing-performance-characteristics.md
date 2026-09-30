---
name: massing-performance-characteristics
description: Measured CPU costs of the B0 proposal validator, the ear clipper and mesh JSON size, plus shapely overflow behaviour - for sizing bounds and budgets
metadata:
  type: project
---

Measured on the owner's PC (Python 3.11.9, numpy 2.3.3, shapely 2.0.7), 2026-09-24. Timings are machine-specific.

- `_point_in_triangle` costs about 4 us per call in pure Python.
- Ear clipping, as implemented in massing_model: a convex 999-gon needs 496k point tests (about 2 s). A
  998-vertex spiral needs 3.9M point tests (about 19 s). Spirals are the practical worst-case family.
  The least possible charge for an n-ring is `(n-2)(n-1)/2 - 1` (exact, used for up-front refusal).
- B0 `proposal.validate_proposed_massing`: `_ring_is_simple` is O(n^2) per outline, about 2.6 s for one
  1000-position outline. 500 levels with distinct outlines would take about 20 minutes, and this runs BEFORE
  any massing bound.
- Mesh JSON is about 63 bytes per vertex: 104k vertices came to 6.5 MB, and 2000 rect floors to 1.16 MB.
- Finite ~1e154 lot coordinates make the shapely centroid empty and raise `shapely.errors.GEOSException`
  (not ValueError). Guard the magnitude before shapely sees it.

**Why:** these numbers set MAX_TRIANGULATION_WORK (2e6), MAX_TOTAL_MESH_VERTICES (100k) and MAX_COORD_ABS (1e8)
in M5-T088.
**How to apply:** when sizing a new bound, or when wiring user geometry. Re-measure before relying on the
absolute timings.

Related: [[massing-test-fixture-lessons]]
