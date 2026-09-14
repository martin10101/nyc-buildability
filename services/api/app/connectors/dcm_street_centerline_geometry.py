"""B3 placeholder (M4-T020): DCM centerline geometry parse-and-expose sibling module.

Seeded at contract time (gate content-identity fail-closed rule requires tracked
allowed_paths files). Implemented by the M4-T020 producer per the packet contract:
typed esriGeometryPolyline parsing, CRS fail-closed EPSG:2263 (wkid 102718),
validity taxonomy, provenance passthrough. The accepted transport module
``dcm_street_centerline_arcgis`` stays byte-immutable and is reused by import only.
"""
