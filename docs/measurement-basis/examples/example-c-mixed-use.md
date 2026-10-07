# Example C - a made-up mixed-use building (retail ground floor, residences above)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/scenario/measurement_basis/measurement_basis_render.py` from `<example>.json`; edit the data file and re-render. See `../MEASUREMENT_BASIS.md`.

Mixed-use example: yes.

This layout is made up - a deliberately simple example, not a real property and not a detailed or permit-ready design. Every dimension is stated so each area can be recomputed. The maximum floor area the law allows is used only as a limit to check the layout against, never as the measured space.

This is a draft reading of the law and a guideline by an AI; it is not professionally reviewed and is not a legal or professional determination. Each statistic links to its source text (ADR-007).

## The building in this example

A made-up five-storey mixed-use building: a retail ground floor (sales floor, its own walls and a back room) with four residential floors above (two apartments each), served by a shared stair, elevator and a residential lobby. The apartment estimate uses only the RESIDENTIAL portion's zoning floor area, including the counted residential circulation; the retail floor is not added to it.

Design choices are made up and editable. Shared-space allocation between the retail and residential portions is itself an open point.

## One area schedule (measured from the layout)

| Component | Portion | Measured area (sq ft) | How measured | Under zoning floor area | Under HPD dwelling-unit area |
|---|---|---|---|---|---|
| Apartment net interior floor (rooms within the units) | residential | 4,480 | Finished room areas within the demising walls, from the stated room sizes. | Counts in full (ZR 12-10 floor area (gross floor space used for dwelling)) | Counts (inside a dwelling unit) - Measured within the perimeter walls to the finished face; this is the unit area. |
| Interior partitions within the apartments (non-demising) | residential | 140 | Footprint of the non-demising partition walls inside the units. | Counts in full (ZR 12-10 floor area (gross floor space)) | Counts (inside a dwelling unit) - Internal partitions sit inside the measured perimeter and are included; the model must not subtract all apartment walls. |
| Demising / party-wall thickness (between units and unit-to-corridor) | residential | 100 | Footprint of the demising wall thickness. | Counts in full (ZR 12-10 floor area (measured to exterior/centre lines; gross)) | Excluded - Integral components of demising partitions are excluded from unit area (measured to the finished face). |
| Exterior wall thickness (perimeter ring) | residential | 560 | Outer footprint minus the inner (clear) footprint, over the stated floors. | Counts in full (ZR 12-10 floor area (measured from the exterior faces of exterior walls)) | Excluded - Integral components of exterior walls are excluded from unit area. |
| Shared corridors | residential | 800 | Corridor width times length, over the stated floors. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-232 (corridor floor-area provisions); ZR 12-10 exclusion); condition: 50% may be exempted with the termination/daylighting/outdoor-access criteria; another 50% where the corridor is no more than 100 ft; the provisions may combine [shown] | Excluded - Circulation between units; not within a dwelling unit. |
| Stairs / stairwells | residential | 660 | Stair footprint over the stated floors. | Counts in full (ZR 12-10 floor area (stairwells at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Elevator shaft | residential | 240 | Shaft footprint over the levels it passes. | Counts in full (ZR 12-10 floor area (elevator shafts at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Mechanical and plumbing chases | residential | 40 | Chase footprint, counted across the floors. | Counts in full (ZR 12-10 floor area (gross floor space; not accessory-mechanical rooms)) | Excluded - All mechanical and plumbing chases are excluded from unit area. |
| Ground-floor lobby / entry | residential | 300 | Lobby footprint. | Counts in full (ZR 12-10 floor area; ZR 23-231 (amenity exclusion does NOT cover circulation)) | Excluded - Shared entry/circulation; not within a dwelling unit. |
| Retail sales floor (commercial) | non_residential | 2,000 | Ground-floor retail footprint. | Not part of the residential portion (Commercial floor area (its own FAR calculation)); condition: belongs to the commercial portion; counted in the commercial floor-area calculation, not the residential portion [NOT shown -> the space counts] | Excluded - Not a residential dwelling unit. |
| Retail exterior/demising walls (commercial) | non_residential | 150 | Retail wall footprint. | Not part of the residential portion (Commercial floor area); condition: part of the commercial portion [NOT shown -> the space counts] | Excluded - Not a residential dwelling unit. |
| Retail back/storage room (commercial) | non_residential | 400 | Back-room footprint. | Not part of the residential portion (Commercial floor area); condition: part of the commercial portion [NOT shown -> the space counts] | Excluded - Not a residential dwelling unit. |

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
- ZR 23-231 (Floor area provisions for amenities) - captured law.
  - Capture: snapshot `zr-23-231`, digest `81eb95e85b333eb86a0fc55413c78567d0b72d7ba9656041f77457f2263b49d6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-231 (last amended 2024-12-05).
  - Quoted: "amenity space shall not include floor space for circulation through the building, including, corridors or vertical circulation spaces"

## The two areas, worked out separately, then reconciled

- Residential zoning floor area (sum of what counts under zoning): 6,920 sq ft.
- Total HPD dwelling-unit area (sum of what counts under HPD): 4,620 sq ft.

Reconciliation - every square foot of the difference, by component (nothing is deducted twice):

| From | Component | Amount (sq ft) |
|---|---|---|
| Residential zoning floor area | (start) | 6,920 |
| - counts for zoning but not HPD | demising-partitions | -100 |
| - counts for zoning but not HPD | exterior-walls | -560 |
| - counts for zoning but not HPD | corridor | -400 |
| - counts for zoning but not HPD | stair | -660 |
| - counts for zoning but not HPD | elevator | -240 |
| - counts for zoning but not HPD | chases | -40 |
| - counts for zoning but not HPD | lobby | -300 |
| = Total HPD dwelling-unit area | (end) | 4,620 |

Ratio for this example = total HPD-measured dwelling-unit area (4,620) / residential zoning floor area (6,920) = 0.6676.

This ratio belongs to THIS made-up example only. Two or three examples cannot establish a typical figure; no percentage is validated here.

## The legal unit cap (a separate figure)

- Maximum residential floor area allowed: 7,500 sq ft (ZR 23-52).
- Divided by the dwelling-unit factor 680: 11.0294 -> 11 dwelling units (ZR 23-52 rounding).
- The residential density ceiling is a separate figure, not derived from the physical estimate, and uses only the residential floor area; the retail floor area is not added.

## What this example shows

- A mixed-use estimate uses the residential portion's zoning floor area, including the counted residential circulation and support space - not the whole building's and not the shop floor's.
- The retail components appear in the one schedule but do not count toward the residential zoning floor area.
- The two residential areas are summed separately and reconciled.

## What this example does not show

- It does not establish a typical ratio or validate any percentage.
- It does not settle how shared stairs/elevators are allocated between the portions.
- It is not a legal or professional determination.

## Sources

- The ZR law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION, read 2026-10-07 at the official HPD site.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Example created for the measurement basis record. | scenario-optimization-engineer |

