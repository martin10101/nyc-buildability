# Lane B — Data and site facts: queue

Ordered: take the top unblocked item. Built from `docs/lanes/RECONCILIATION.md` (partial and missing items only) under the derived lane plan `docs/lanes/PARALLEL_BUILD_PLAN.md`. Each item becomes one ledger task `M<x>-T<n>` that cites D-090 and the plan ID; its "Done when" is the plan's text unless marked *derived*. Waves: 1 foundations · 2 Milestone 1 + 2 · 3 breadth and parity (plan §11b: never delays Milestone 1). Owned by Lane C (the integrator); lane B never edits it and, under `docs/lanes/`, updates only `docs/lanes/status/B.md` and its own `docs/lanes/requests/B-<n>.md`.

Nothing here starts before the owner's GO (D-090-R007).

| # | Plan ID | Task | Done when | Depends on | Blocked by | Wave | Size |
|---|---|---|---|---|---|---|---|
| B-01 | M1-20, C-3, C-7, C-8, C-9 | Record the benchmark lot 215-16 Northern Blvd (BBL 4073340070) with provenance (dataset, query, date): PLUTO (version pinned), MapPLUTO 2263 geometry, DTM outline, ZTLDB + zoning features (R6B / C2-2), DCM widths for Northern Blvd and 215 Pl, building footprint, DOB jobs / certificate of occupancy, flood zone, E-designation, landmarks, transit zone, recorded zoning-lot documents (flag only) | *derived:* Recorded fixtures exist for every competitor-review §A item that has an official source; the benchmark_lot fixture moves those values from expected_unverified to recorded where they agree; disagreements logged; first live-call task (Lane B only, never in Wave 0) | — | — | 1 | M |
| B-02 | M1-07 | Measurement ranks and source labels in the property facts (site_fact v1): survey entered / city records / approximate — tax map / entered / assumed / unknown; each result can carry its weakest input's label | M1-07: Every input shows its status and source | M5-T125 contracts | — | 1 | M |
| B-03 | M1-13 | Single-lot site geometry: frontage per street along the outside edges, lot type (corner / interior / through) from the outline, depth, area checked against the outline, labeled "Approximate — tax map" unless surveyed | M1-13: No measurement has to be typed for Pilot A | B-01 | — | 1 | L |
| B-04 | M1-13 | Street width per frontage from the mapped City Map width; unknown width → both the wide- and narrow-street results, marked "Needs street width" (§4) | *derived:* Every frontage carries a sourced width or "Needs street width"; never a silent narrow default | B-03 | — | 1 | M |
| B-05 | M2-07 | Existing zoning floor area from a DOB filing or certificate of occupancy, or an entered assumption; never DOF building area; recorded area shown for reference only | M2-07: Existing floor area is never taken from DOF building area | B-01 | — | 2 | M |
| B-06 | C-7 | Pin and show data versions; flag "Out of date" when a source is behind | *derived:* C-7 data side passes | — | — | 1 | S |
| B-07 | M2-05 | Multi-lot site math: combined outline with shared lines removed, outside frontage, lot type from the combined outline, same-block + touching check with the reason, condo base lots in the lot choice | M2-05: Selecting 1, 2 or all lots updates the outline, frontage, lot type and area correctly on test fixtures | B-03 | — | 2 | L |
| B-08 | M2-00 | Wallabout records: permits, ACRIS (flag only), DTM, PLUTO billing row, ZTLDB for lots 32 and 33, street widths | M2-00: Findings recorded with sources | — | — | 2 | S |
| B-09 | L-11 | §8a hidden-issue flags group by group, each with a "Check needed" fallback when the source is missing: existing building; zoning-lot history (flag only, P-2); map-based rules; site shape and street | *derived:* Each §8a item is a flag, an opportunity or "Check needed" — never a guess | B-01 | — | 2→3 | L |
| B-10 | C-8 | One transit/parking-zone source applied identically to every option | *derived:* C-8 passes | B-01 | — | 2 | S |
| B-11 | §11b | Parity data: unused floor area on the lot (needs B-05), neighbors' unused floor area, 485-x zones, comparable sales of similar type and size — every figure sourced and dated | *derived:* §11b data rows done with sources | B-05 | — | 3 | L |

## Blocked by owner or reviewer

- none

