# Lane E — Outputs and parity: status

Updated by lane E only, after every task (lane prompts, shared rules).

Refreshed 2026-10-03 from the PR record by the integrator (status words only; descriptions unchanged).

| | |
|---|---|
| **State** | E-03 (DXF from results geometry) merged (#268, 2026-10-03). E-07 (§5c-2 location and zoning maps) merged (#286, 2026-10-02). E-01 merged (#263, 2026-09-30) earlier |
| **Done** | E-03 (DXF from the same geometry and style table): lot + envelope layers, feet 1:1, not-a-survey note, behind `LANE_E_ENABLED` (off); rebased onto 4306bb60, reviewed PASS, merged (#268, 2026-10-03). · E-07: `services/api/app/drawings/maps/` — server-made vector SVG **location map** (subject lot + OTI building footprints, lot labelled by BBL) and **zoning map** (subject lot + DCP `nyzd` district boundaries, each labelled by its `ZONEDIST` symbol, with the official use-limitation, ±20 ft accuracy and NYC-Open-Data attribution notes). Built on the E-01 kit (shared style table — 3 new AREA kinds `subject_lot`/`zoning_district`/`building_footprint`; shared geometry, svg, furniture). EPSG:2263 only; fail-closed adapter; recorded-fixture snapshots + C-4 label/geometry tests; **no raster base map** (no imagery licence confirmed — vector city data only). Behind `LANE_E_ENABLED` (off). Sources + licences: `docs/samples/maps/README.md`. · E-01: `services/api/app/drawings/kit/` (site plan + massing) |
| **Next** | E-02 (PDF converter trial) — next, but its WeasyPrint runtime question is an owner item; E-04 waits on E-02. E-03 (DXF) merged (#268, 2026-10-03); E-01b/Q8 unchanged. |
| **Blocked by** | E-01b (section drawing): owner question Q8 |
| **Open owner questions** | Q8 — whether the section view falls under the expansion hold. (E-07: optional aerial/street base map deferred until an imagery licence is confirmed from the publisher's own page) |

E-R108 (D-090-R108): the results `scope` now prints on the site plan and DXF notes — label, tax lot, assumed conditions, whole-site and the two settled remaining-capacity strings (branch `lane-e/E-R108-scope-on-drawings`, in review).

2026-10-04 maps step 4 (D-090-R124): the REAL 215-16 Northern `map_context` document, built OFFLINE from the recorded replay through the existing `build_map_context`, committed as a drawings fixture (`services/api/tests/drawings/maps/fixtures/recorded_215_16_northern.json`: subject BBL 4073340070, one `nyzd` R6B zoning district, two OTI footprints, README attribution/accuracy/use-limitation notes), with its location + zoning SVG snapshots rendered through the EXISTING renderers and a byte-drift test. Tests, fixtures and snapshots only — no renderer behaviour change. Built + tested on recorded data; NOT independently reviewed; behind `LANE_E_ENABLED` (off). Branch `lane-e/E-maps-step-4-northern-map-context`.

2026-10-04 (integrator, status words only): #419 merged; #420 (DXF invariant tests accept real-engine fixtures) merged.
