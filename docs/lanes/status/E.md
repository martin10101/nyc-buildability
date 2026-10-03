# Lane E — Outputs and parity: status

Updated by lane E only, after every task (lane prompts, shared rules).

Refreshed 2026-10-03 from the PR record by the integrator (status words only; descriptions unchanged).

| | |
|---|---|
| **State** | E-07 (§5c-2 location and zoning maps) merged (#286, 2026-10-02). E-01 merged (#263, 2026-09-30) earlier |
| **Done** | E-07: `services/api/app/drawings/maps/` — server-made vector SVG **location map** (subject lot + OTI building footprints, lot labelled by BBL) and **zoning map** (subject lot + DCP `nyzd` district boundaries, each labelled by its `ZONEDIST` symbol, with the official use-limitation, ±20 ft accuracy and NYC-Open-Data attribution notes). Built on the E-01 kit (shared style table — 3 new AREA kinds `subject_lot`/`zoning_district`/`building_footprint`; shared geometry, svg, furniture). EPSG:2263 only; fail-closed adapter; recorded-fixture snapshots + C-4 label/geometry tests; **no raster base map** (no imagery licence confirmed — vector city data only). Behind `LANE_E_ENABLED` (off). Sources + licences: `docs/samples/maps/README.md`. · E-01: `services/api/app/drawings/kit/` (site plan + massing) |
| **Next** | E-02 (PDF converter trial); E-03 (DXF from the same geometry and style table) is open as a draft (#268, stacked on #263) — rebase after #353 (A-04 slice 1) merges |
| **Blocked by** | E-01b (section drawing): owner question Q8 |
| **Open owner questions** | Q8 — whether the section view falls under the expansion hold. (E-07: optional aerial/street base map deferred until an imagery licence is confirmed from the publisher's own page) |
