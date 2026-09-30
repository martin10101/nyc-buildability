---
name: mappluto-geometry-connector-crs
description: MapPLUTO ArcGIS geometry connector facts — endpoint, f=geojson/outSR support, and the 2263-only-refuses-reprojection design that blocks direct web-map use
metadata:
  type: project
---

The MapPLUTO parcel-geometry connector (`services/api/app/connectors/mappluto_geometry_arcgis.py`, task M2-T009) already returns per-BBL tax-lot polygon geometry, but in a form NOT directly usable by a web map.

**Why:** the connector is deliberately EPSG:2263-only (wkid 102718 / latestWkid 2263, US survey feet). `require_authoritative_crs` raises `WrongCRSError` for anything else, area is computed only in projected feet, and the docstring states "No reprojection happens in this module." Its output is a canonical feet-coordinate form + digests, not GeoJSON lng/lat. MapLibre GL JS needs EPSG:4326 GeoJSON.

**How to apply:** any web lot-outline / map work must add a reprojection or 4326-GeoJSON emission path. The official service DOES support `f=geojson` and `outSR` (live `.../MAPPLUTO/FeatureServer/0` reports supportedQueryFormats "JSON, geoJSON, PBF"; currentVersion 12, layer 0 polygon, maxRecordCount 2000, keyless). So the service can return `f=geojson&outSR=4326` directly — but keep the authoritative 2263 path for area/canonical digests; do not let a reprojected transport replace the 2263 provenance. Service root: `https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer`. SOURCE_ID `nyc-dcp-mappluto-arcgis`. Condo unit lots (1001-6999) have NO polygon; billing lots (7501-7599) carry the merged complex polygon. See also [[nyc-source-fetch-channels]].
