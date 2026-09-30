---
name: mappluto-recorded-fixture-geometry-facts
description: Verified shapes of the recorded MapPLUTO geometry fixtures (MPG02/06/07) and why real NYC lots almost never fit the max-envelope engine's axis-aligned-rectangle-only placement
metadata:
  type: project
---

Facts measured through the real `analyze_lot_geometry` over `services/api/tests/fixtures/mappluto_geometry/` (2026-09-23, M5-T076 rework):

- **MPG02_lot_single_1008350041** (Empire State Building) — canonical: 1 polygon, **6-vertex NON-axis-aligned** exterior ring, no holes, area 97113.69 sq ft, `Version` "26v1". It is the packet-named "fitted-candidate-reachable" fixture but it CANNOT fit: `max_envelope._lot_rectangle` places only an axis-aligned ring whose bbox area equals the recorded area (rel_tol 1e-9), so the route returns the honest `lot_geometry_unsupported` with reason "the lot-line geometry is not an axis-aligned rectangle (a diagonal or zero-length segment); unsupported for candidate placement in slice 1".
- **MPG06_lot_holes_1000010010** (Governors Island) — 1 polygon, 320-vertex exterior + two hole rings totalling **143 vertices**, vertex-disjoint from the exterior. The exterior-only cut yields exactly 320 segments.
- **MPG07_lot_multipolygon_4142600001** (Queens, shoreline-clipped) — assessment **valid**, 2 polygons, **3130** exterior vertices — over `ROUTE_MAX_LOT_LINE_SEGMENTS` (800). A real recorded lot hits our own cap, so an over-cap class must never be typed `invalid_geometry`.
- Canonical rings are OPEN cycles of two-decimal coordinate STRINGS; nesting is `canonical = [polygon...]`, `polygon = [exterior_ring, *hole_rings]`, `ring = [[x, y]...]`.

**Why:** the derived-but-unfittable path (rotated NYC grid in EPSG:2263) is the dominant real-world outcome, and the T076 G3 review failed the first submission partly for proving reachability on a synthetic rectangle labelled with MPG02's BBL.

**How to apply:** any "real lot fits" claim on this engine is fixture-conditional — say so; exercise the recorded packs, not an inline rectangle, whenever a packet binds tests to them; and check whether a "bad geometry" classification is actually OUR cap before blaming official data. See [[socrata-pluto-gotchas]].
