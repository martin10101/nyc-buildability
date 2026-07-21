---
paths:
  - "services/api/app/spatial/**"
  - "services/api/app/geo/**"
  - "**/*.geojson"
---
# Geospatial rule — loads only for spatial engine / geometry work

PostGIS + Shapely are the canonical authority for parcel geometry, district/overlay intersections,
and split-lot conditions. Browser 3D only renders canonical geometry; it never mutates the source.

- Validate CRS and units on every geometry; repair invalid geometry explicitly and record it.
- Zoning assignment must model **positional uncertainty** (documented vs assumed tolerances) and a
  split-share range — emit facts-with-uncertainty; **never collapse uncertainty** and never label a
  geometric assignment "Verified" on its own.
- Geometry versions must be reproducible: same inputs + same geometry version → same result.
- Cover the geospatial acceptance pack (`docs/ACCEPTANCE_SCENARIO_STANDARD.md`): point inside /
  outside / boundary-touch, lot crossing two districts, invalid-geometry repair, CRS validation,
  geometry-version reproducibility.
- The accepted M2-T013 spatial-intersection engine (`services/api/app/spatial/`) is the reference
  substrate; consume its domain models read-only.
