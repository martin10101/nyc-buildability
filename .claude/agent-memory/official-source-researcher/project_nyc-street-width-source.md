---
name: nyc-street-width-source
description: The authoritative NYC mapped-street-width source (DCM Street Center Line) and its free-text-width trap, for the ZR wide-street (75 ft) rule input
metadata:
  type: project
---

NYC street-width / mapped-street official source, settled in M4-T013 research (2026-09-13):

- **The mapped (legal) street width source is DCP's Digital City Map (DCM) - Street Center Line.**
  Two keyless official channels: ArcGIS `DCM_Street_Center_Line/FeatureServer/0` on the DCP_GIS
  portal `services5.arcgis.com/GfwWNkhOj9bNBqoJ` (RECOMMENDED PRIMARY - fresh, EPSG:2263, geoJSON,
  polyline geometry, maxRecordCount 2000, item 9ce5b83f139748f29eb92cdabeb29398) and the SODA
  dataset `g6zj-tzgn` (fallback/corroboration).
- **SODA g6zj-tzgn is STALE despite a "Monthly" label**: rowsUpdatedAt 2024-05-03 / viewLastModified
  2024-11-01, while ArcGIS dataLastEditDate is 2025-12-01 and the s-media metadata says "last updated
  October 31, 2025". Prefer ArcGIS for currency; poll viewLastModified if using SODA.
- **CENTRAL TRAP - `Streetwidt`/`Streetwidth` is FREE TEXT, not numeric.** Domain includes ranges
  (`60-75`), inequalities (`>75`), approximations (`~60`), prose (`Probably between 80 - 90`),
  `Width Irregular`, `n/a` (2954), `Unknown` (1404), and `Unknown but <75/>75`. Many straddle the ZR
  12-10 75-ft cutoff. The official metadata gives NO field-level definition of the width concept -
  only the dataset-level "widths shown on the Official City Map" framing (mapped, not paved).
- **Geoclient/Geosupport per-address `streetWidth` is KILLED for legal use** - it is the paved/roadbed
  width from LION (W 100 St = 30 vs DCM mapped 60), point-not-geometry, cannot answer the within-100ft
  test. Advisory cross-check only. (Already recorded in `geoclient.json` registry draft.)
- **Consumer** = `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`
  (ZR 23-22 wide-street conditional FAR). It needs mapped width >= 75 ft PLUS geometry (footnote 1's
  "within 100 ft of a wide street, or portions thereof" is a lot-geometry x street-geometry x 100-ft
  buffer computation, a separate downstream task - fronting width alone can't answer it).

**Why:** M4-T013 (D-045-R003 B2) resolved the "street-width source not chosen" gap; report at
`project-control/reports/M4-T013-street-width-research.md`, drafts at
`docs/research/source-registry-drafts/dcm-street-centerline.json`. Builds on the pilot
`docs/research/street-width-source-pilot-2026-09-11.md`.

**How to apply:** For any street-width rule input, use DCM (ArcGIS primary), parse the free-text
width conservatively and FAIL CLOSED TO NARROW on any ambiguity (wide-street only raises FAR, so
under-claiming is the safe direction). Never use Geoclient streetWidth as the legal answer. See
[[nyc-source-fetch-channels]] for the DCP_GIS ArcGIS + s-media PDF fetch techniques used here.
