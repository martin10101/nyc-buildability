---
name: massing-crs-range-guards
description: Where the canonical NYC EPSG:2263 range constants live, and how the massing_model magnitude bound vs the NYC-range check interact (a boundary-fixture collision to watch for)
metadata:
  type: project
---

The canonical NYC EPSG:2263 fail-closed unit/range constants are
`NYC_2263_X_MIN/X_MAX/Y_MIN/Y_MAX` in `services/api/app/scenario/proposal.py`
(= [900000, 1100000] x [100000, 300000] US survey feet). They are module-level
public names (no underscore) but NOT in proposal.py's `__all__`. B0
`validate_proposed_massing` uses them to range-check the proposal footprint;
`max_envelope.py` also imports them. Reuse these (import from `.proposal`) rather
than redefining — single source of truth.

**Why:** `massing_model.py` takes the LOT ring as a SEPARATE argument that B0 never
sees. M5-T098 (DB-061 c) added `_require_lot_ring_in_nyc_bounds` in `_lot_polygon`
reusing those constants, so a 4326/metric lot refuses
`MassingModelError(reason="lot_ring_out_of_nyc_bounds", field="lot_ring")` instead of
being mislabelled `footprint_outside_lot` downstream.

**How to apply:** Two distinct coordinate guards coexist in massing_model, in this
order: (1) `MAX_COORD_ABS = 1e8` symmetric magnitude/overflow bound in `_prepare_ring`
(CRS-agnostic, applies to every ring incl. the lot); (2) the tighter NYC-range check
on the lot only. When ADDING a tighter domain-range check to a shared path, first grep
existing tests for boundary fixtures that use OUT-OF-DOMAIN coordinates: T088's
`test_t088_as4_coordinate_magnitude_bound_is_inclusive` built a lot at ±1e8 to test the
magnitude boundary — that ±1e8 lot is exactly the wrong-CRS case the NYC check now
refuses, so the fixture had to move its inclusivity proof onto `_prepare_ring` directly.
shapely `GEOSException` on a build path is wrapped to
`MassingModelError(reason="geometry_engine_error")` via the `_wrap_geos_errors`
decorator on `build_massing_model` (module boundary; prove with a spied/monkeypatched
`mm.Polygon`, never a real GEOS crash).
