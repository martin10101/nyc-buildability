# Benchmark window pack — 215-16 Northern Boulevard (BBL 4073340070)

Recorded official ArcGIS responses for the **map data around the lot** that the report's
site-context maps draw (task M5-T154; owner directive D-090 rows R936/R937; backlog DB-222). The
owner read the report's site drawing as "a rectangle on an angle" with "no reference to where he
is"; this pack is the recorded data that lets the report show the lot among its neighbours.

Keyless, read-only, one-time capture (ruling Y11). No key, account or email address was used, and
**no owner-name or any other personal field was requested or stored.** Tests and the browser-test
harness **replay these bytes only** — no network call is made.

## The three recordings (this pack)

| File | Layer | Window | Count |
|---|---|---|---|
| `mappluto_window_lots_4073340070_plus400ft.json` | MapPLUTO neighbouring tax lots | lot bbox **+ 400 ft** | 201 features (200 neighbours after the subject BBL is excluded) |
| `building_footprints_window_4073340070_plus400ft.json` | OTI Building Footprints | lot bbox **+ 400 ft** | 263 footprints |
| `dcm_street_centerline_window_4073340070_plus1000ft.json` | DCP Digital City Map street centre lines | lot bbox **+ 1,000 ft** | 35 segments |

Each file is pinned byte-for-byte by its SHA-256 and request URL in `MANIFEST.json`;
`.gitattributes` (`* -text`) forbids line-ending conversion so the digests stay valid on every
platform. The request URLs are exactly what the connectors build, so a test asserting the built URL
against the MANIFEST proves the byte-exact query.

## What this pack reuses from the base pack (`../benchmark_215_16_northern`)

This window pack **extends** the base 215-16 Northern pack. Two kinds of response are NOT duplicated
here because the base pack already pins them byte-for-byte and their URLs are identical:

1. **The subject lot's per-BBL MapPLUTO geometry** (`mappluto_lot_4073340070_epsg2263.json`). The
   report provider fetches it to size the two windows (its bounding box ± the paddings) and to draw
   the subject outline (the measurement-grade EPSG:2263 outline, ruling Y5). The window query also
   returns the subject lot, which is verified byte-identical to this per-BBL geometry, so the two
   agree to 0.00 ft.
2. **Each layer's service metadata** (`mappluto_layer_metadata.json`,
   `building_footprints_layer_metadata.json`, `dcm_layer_metadata.json`). Every connector fetches
   its layer-0 metadata (field/geometry-type/CRS/maxRecordCount gate and the dataset edit date for
   provenance) before any page. At capture, the live metadata was verified byte-identical to the
   base pack for MapPLUTO and DCM; the building-footprints layer's queried field schema was
   identical (only its `editingInfo` edit date moved), so the base pack's recording stays a faithful
   replay.

The replay helper (`services/api/tests/spatial/_northern_window_replay.py`) and the harness entry
point (`app.api.v1.report_context.recorded_pack_provider`) both serve a requested URL from this
pack first and fall back to the base pack, so binding to this one folder is enough.

## CRS and units

Every coordinate is **EPSG:2263** (NAD83 / New York Long Island, US survey feet) — the authoritative
measurement CRS (`inSR=2263` / `outSR=2263`). Nothing is reprojected. The maps are approximate (the
city tax map), never a boundary survey.
