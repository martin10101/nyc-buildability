---
name: oti-building-footprints-facts
description: Verified live behaviour of the OTI BUILDING_view ArcGIS layer (footprints/heights) - error shape, metadata endpoint, ground-elevation definition conflict, unit gap, null heights
metadata:
  type: project
---

Verified live 2026-09-24 (M5-T089 connector work):

- Shapefile short names (HEIGHTROOF, GROUNDELEV) in outFields return **HTTP 200 with an ArcGIS error object (code 400)**, not an HTTP 400 status. Refuse both shapes.
- Layer publishes in 102100/3857; `outSR=2263` returns 102718/2263. Empty query pages omit `spatialReference` and `geometryType`; non-empty pages carry them.
- The service's formal FGDC metadata is at `.../BUILDING_view/FeatureServer/0/metadata` (XML, ~35 KB). It has attribute definitions but **no unit tag** for HEIGHT_ROOF / GROUND_ELEVATION and never mentions NAVD88. So the feet unit remains an inference (RQ-1).
- GROUND_ELEVATION definition conflict: City dictionary says "lowest elevation at building ground level"; FGDC says "interpolated at the building centroid" from a 2010 LiDAR DTM. Keep both visible.
- `HEIGHT_ROOF IS NULL` matched zero features. Missing heights are published as 0 in practice; still type NULL.
- Placeholder (FEATURE_CODE 1003) footprints can carry dummy-looking BBLs (lot 9999) and a null ground.
- Every response carries `x-esri-org-request-units-per-min: usage=N;max=28800`.

**Why:** these contradict or sharpen the M5-T087 recon wording; future footprint/3D work will hit them.
**How to apply:** when reviewing or extending building_footprints_arcgis.py or wiring it into massing, trust these over the recon's "HTTP 400" wording and don't claim an official unit. Related: [[source-accuracy-facts]]
