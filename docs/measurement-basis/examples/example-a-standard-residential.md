# Example A - a made-up standard R6B residential walk-up (no allowances taken)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/scenario/measurement_basis/measurement_basis_render.py` from `<example>.json`; edit the data file and re-render. See `../MEASUREMENT_BASIS.md`.

Mixed-use example: no.

This layout is made up - a deliberately simple example, not a real property and not a detailed or permit-ready design. Every dimension is stated so each area can be recomputed. The maximum floor area the law allows is used only as a limit to check the layout against, never as the measured space.

This is a draft reading of the law and a guideline by an AI; it is not professionally reviewed and is not a legal or professional determination. Each statistic links to its source text (ADR-007).

## The building in this example

A made-up four-storey R6B walk-up: four identical 40 ft x 50 ft floors, two apartments per floor reached off a shared corridor, one stair that passes through every floor, no elevator, no lobby, no cellar and no parking. No ZR 23-23 allowance condition is shown, so every above-grade component counts in full under zoning. On each floor the components, the exterior wall ring among them, add up to exactly the 2,000 sq ft outline.

Design choices (floor plate, number of floors, room sizes) are made up for this example and are editable; they are not validated here. The per-floor statement lets the fit be checked floor by floor.

## The floors and the fit (every floor adds up to its outline)

| Floor | Count | Outside outline (sq ft) | Components on the floor (sq ft) | Difference |
|---|---|---|---|---|
| Typical residential floor (one of four identical) | 4 | 2,000 | 2,000 | 0 |

On every floor the components listed in the schedule - the exterior wall ring among them - add up to exactly the floor's stated outside outline (difference zero), so the building fits.

## One area schedule (measured from the layout)

| Component | Portion | Measured area (sq ft) | How measured | Under zoning floor area | Under HPD dwelling-unit area |
|---|---|---|---|---|---|
| Apartment net interior floor (rooms within the units) | residential | 5,888 | Finished room areas within the demising walls, from the stated room sizes. | Counts in full (ZR 12-10 floor area (gross floor space used for dwelling)) | Counts (inside a dwelling unit) - Measured within the perimeter walls to the finished face; this is the unit area. |
| Interior partitions within the apartments (non-demising) | residential | 144 | Footprint of the non-demising partition walls inside the units. | Counts in full (ZR 12-10 floor area (gross floor space)) | Counts (inside a dwelling unit) - Internal partitions sit inside the measured perimeter and are included; the model must not subtract all apartment walls. |
| Demising / party-wall thickness (between units and unit-to-corridor) | residential | 96 | Footprint of the demising wall thickness. | Counts in full (ZR 12-10 floor area (measured to exterior/centre lines; gross)) | Excluded - Integral components of demising partitions are excluded from unit area (measured to the finished face). |
| Exterior wall thickness (perimeter ring) | residential | 704 | Outer footprint minus the inner (clear) footprint, over the stated floors. | Counts in full (ZR 12-10 floor area (measured from the exterior faces of exterior walls)) | Excluded - Integral components of exterior walls are excluded from unit area. |
| Shared corridors | residential | 480 | Corridor width times length, over the stated floors. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-232 (corridor floor-area provisions); ZR 12-10 exclusion); condition: 50% may be exempted with the termination/daylighting/outdoor-access criteria; another 50% where the corridor is no more than 100 ft; the provisions may combine [NOT shown -> the space counts] | Excluded - Circulation between units; not within a dwelling unit. |
| Stairs / stairwells | residential | 640 | Stair footprint over the stated floors. | Counts in full (ZR 12-10 floor area (stairwells at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Mechanical and plumbing chases | residential | 48 | Chase footprint, counted across the floors. | Counts in full (ZR 12-10 floor area (gross floor space; not accessory-mechanical rooms)) | Excluded - All mechanical and plumbing chases are excluded from unit area. |

Each component appears once. The residential zoning floor area and the HPD dwelling-unit area are summed from this one schedule, each on its own.

## The law and guideline relied on

- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "any other floor space used for dwelling purposes, no matter where located within a building, when not specifically excluded"
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION - guideline, not law. A guideline, not law; it applies to projects developed under HPD loan programs whose design-consultation submission is on or after October 1, 2026.
  - Source: https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction-2026.pdf (edition 2026, read 2026-10-07).
  - Quoted: "Dwelling unit area is measured within the perimeter walls, from the finished face of all exterior walls and demising partitions"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "measured from the exterior faces of exterior walls or from the center lines of walls separating two buildings"
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION - guideline, not law. A guideline, not law; it applies to projects developed under HPD loan programs whose design-consultation submission is on or after October 1, 2026.
  - Source: https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction-2026.pdf (edition 2026, read 2026-10-07).
  - Quoted: "All other structural members — including freestanding columns and columns attached to interior partitions — are included in unit area calculations"
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION - guideline, not law. A guideline, not law; it applies to projects developed under HPD loan programs whose design-consultation submission is on or after October 1, 2026.
  - Source: https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction-2026.pdf (edition 2026, read 2026-10-07).
  - Quoted: "Structural members that are integral components of exterior walls or demising partitions, as well as all mechanical and plumbing chases, are excluded from unit area calculations"
- ZR 23-23 (Special Floor Area Provisions for Multiple Dwelling Residences) - captured law.
  - Capture: snapshot `zr-23-23`, digest `6dd17af023030a301d6ebcea5f7a18322a57e7b37a6f6d72406cc6f49054961f`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-23 (last amended 2024-12-05).
  - Quoted: "floor space allocated to building amenities, corridors, refuse storage or disposal, or access to elevated ground floor dwelling units may be exempted from the definition of floor area pursuant to Section 12-10, provided that the provisions of this Section, inclusive, are met"
- ZR 23-232 (Floor area provisions for corridors) - captured law.
  - Capture: snapshot `zr-23-232`, digest `0a79cda6656d8d0c32a10e052cdf5e4b668297af1c411180331139401fc13ad2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-232 (last amended 2024-12-05).
  - Quoted: "Fifty percent of the floor space of a corridor may be exempted from the definition of floor area"
- ZR 23-232 (Floor area provisions for corridors) - captured law.
  - Capture: snapshot `zr-23-232`, digest `0a79cda6656d8d0c32a10e052cdf5e4b668297af1c411180331139401fc13ad2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-232 (last amended 2024-12-05).
  - Quoted: "where the length of the corridor, as measured from the vertical circulation core to the door of the furthest dwelling unit on the story, does not exceed 100 linear feet"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "floor space in buildings containing multiple dwelling residences allocated to building amenities, corridors, refuse storage or disposal, or access to elevated ground floor dwelling units that is provided in accordance with the provisions of Section 23-23, inclusive"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "elevator shafts or stairwells at each floor, except as specifically excluded in this definition"

## The two areas, worked out separately, then reconciled

- Residential zoning floor area (sum of what counts under zoning): 8,000 sq ft.
- Total HPD dwelling-unit area (sum of what counts under HPD): 6,032 sq ft.

Reconciliation - every square foot of the difference, by component (nothing is deducted twice):

| From | Component | Amount (sq ft) |
|---|---|---|
| Residential zoning floor area | (start) | 8,000 |
| - counts for zoning but not HPD | demising-partitions | -96 |
| - counts for zoning but not HPD | exterior-walls | -704 |
| - counts for zoning but not HPD | corridor | -480 |
| - counts for zoning but not HPD | stair | -640 |
| - counts for zoning but not HPD | chases | -48 |
| = Total HPD dwelling-unit area | (end) | 6,032 |

Ratio for this example = total HPD-measured dwelling-unit area (6,032) / residential zoning floor area (8,000) = 0.7540.

This ratio belongs to THIS made-up example only. Two or three examples cannot establish a typical figure; no percentage is validated here.

## Shared floor area between the uses (ZR 23-20)

A single-use residential building: no floor area is shared between uses, so the ZR 23-20 proportional attribution does not apply here.

## The legal unit cap (a separate figure)

- Maximum residential floor area allowed: 9,000 sq ft (ZR 23-52).
- Divided by the dwelling-unit factor 680: 13.2353 -> 13 dwelling units (ZR 23-52 rounding).
- The density ceiling is a separate figure from the physical estimate; neither is derived from the other. Here the measured residential zoning floor area (8,000 sq ft) is below the 9,000 sq ft the FAR would allow.

## What this example shows

- The residential zoning floor area and the HPD dwelling-unit area are summed SEPARATELY from one schedule, then reconciled with nothing deducted twice.
- Apartment-internal partitions stay in the HPD unit area; only exterior/demising wall thickness, chases and shared circulation leave it.
- The ratio for this example is total HPD-measured dwelling-unit area / residential zoning floor area.

## What this example does not show

- It does not establish a typical ratio; this is one made-up layout.
- It does not validate 700 sq ft, 25 percent, 10 ft or 15 ft.
- It is not a legal or professional determination.

## Sources

- The ZR law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION, read 2026-10-07 at the official HPD site.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Example created for the measurement basis record. | scenario-optimization-engineer |
| 2026-10-07 | Added the per-floor statement (four identical 40x50 floors) so the fit can be checked; the components on each floor add up to the 2,000 sq ft outline. No area or ratio changed (residential zoning floor area 8,000; HPD 6,032; ratio 0.7540). | scenario-optimization-engineer |

