---
name: source-accuracy-facts
description: What positional-accuracy figures are documented vs assumed for zoning-features, MapPLUTO, ZTLDB; where the citations live
metadata:
  type: project
---

Documented vs assumed positional accuracy (checked 2026-07-20 for the M2-T013 advisory):

- DOCUMENTED: nyzd (zoning districts) horizontal accuracy is +/- 20 ft, official nyzd_metadata.pdf (Z11), quoted verbatim in docs/research/zoning-features-ztldb-2026-07-16.md line 149; glyph question resolved at G1 (OQ-10).
- NOT DOCUMENTED in repo: any accuracy figure for MapPLUTO/DTM lot geometry (docs/research/pluto-mappluto-2026-07-16.md has only the general disclaimer; lineage = DCP-modified DOF Digital Tax Map, line 72). M2-T009's use of 20 ft for lots is an ANALOGY assumption (module comment, mappluto_geometry_arcgis.py lines 203-208).
- NOT DOCUMENTED: per-layer accuracy for nyco/nysp/nysp_sd/nylh/nyzma (research OQ-5 still open — five metadata PDFs unread).
- ZTLDB carries NO percentage columns (16-column schema, ztldb_soda.py lines 178-195); only ordered zoning_district_1..4 (greatest-area-first since 2019-12-31) — geometric split percentages must be computed by us; ZTLDB gives ordering/set cross-check only. ZTLDB Socrata rows possibly frozen at 2026-04-05 (OQ-3 open) while nyzd refreshes monthly — vintage skew must be checked before calling a disagreement a conflict.
- Official use limitation: zoning features "are not intended for determining zoning at the individual tax lot level" (zoning_features_arcgis.py lines 56-58) — ZTLDB is DCP's official lot-level assignment product.

**Why:** every tolerance/uncertainty policy for the M2-T013 intersection engine must distinguish documented accuracy from assumed accuracy (owner directive 2026-07-20: never hide source accuracy behind one arbitrary tolerance).
**How to apply:** cite these exact lines when writing tolerance provenance; treat the MapPLUTO figure as requiring source verification until the DTM/MapPLUTO metadata is read.
