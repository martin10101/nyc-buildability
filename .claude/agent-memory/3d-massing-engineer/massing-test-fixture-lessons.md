---
name: massing-test-fixture-lessons
description: Which massing fixtures actually discriminate mutants (non-star concave, non-integer coords, exact Fraction volumes) and how to inject mutants into the consuming namespace
metadata:
  type: feedback
---

Massing/triangulation tests only bite if the fixture can tell a wrong algorithm from a right one.

- An L-shape is star-shaped, so a naive fan passes every check on it. Use a non-star U or comb, and add a check
  that a fan from EVERY start vertex over-covers the shape (this proves the fixture is still valid).
  Signed-area sums cannot detect a fan (fan signed areas always sum to the polygon area). Use abs-area, CCW
  orientation per triangle, `covers` per triangle, or cap-face normal signs.
- Integer EPSG:2263 coordinates make world-coordinate and local-coordinate volume identical, so a "drop the
  local origin" mutant survives. Use non-integer coordinates, a non-integer lot centroid and z up to ~1000 ft,
  then compare against the exact rational volume (`fractions.Fraction` shoelace x height) within 1e-6.
  The world error is about 1e-2 at those magnitudes; the local error is at grid rounding (about 5e-7).
- Index-based closure checks still pass on a fan. Add a per-face cap-normal check.
- To mutate the consuming namespace: use a pytest `-p` plugin that `spec_from_file_location`s the mutated copy
  as `app.scenario.massing_model`, puts it in `sys.modules`, and sets it on the `app.scenario` package before
  collection. Use a fresh interpreter per mutant, and run a BASELINE injection of the unmutated copy first.
- For bounds that must refuse "before heavy work", use a spy fixture that monkeypatches `mm._triangulate` /
  `mm._build_prism` (the builder resolves them as module globals at call time) and assert zero calls.
  Otherwise a removed up-front check stays green when a later check raises the same reason.

**Why:** the M5-T082 G4 review found 4 surviving mutants (fan, CW, collinear, world-volume) behind green tests;
M5-T088 closed them this way (2026-09-24).
**How to apply:** any new geometry guard or fixture in massing / GLB / DXF work.

Related: [[massing-performance-characteristics]]
