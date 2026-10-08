# Example B - a made-up R6B building where ZR 23-23 allowance conditions are shown

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/scenario/measurement_basis/measurement_basis_render.py` from `<example>.json`; edit the data file and re-render. See `../MEASUREMENT_BASIS.md`.

Mixed-use example: no.

This layout is made up - a deliberately simple example, not a real property and not a detailed or permit-ready design. Every dimension is stated so each area can be recomputed. The maximum floor area the law allows is used only as a limit to check the layout against, never as the measured space.

This is a draft reading of the law and a guideline by an AI; it is not professionally reviewed and is not a legal or professional determination. Each statistic links to its source text (ADR-007).

## The building in this example

A made-up five-storey R6B elevator building: four identical typical residential floors (three apartments each, reached off a corridor) over a ground floor that holds the lobby, an amenity/laundry room, a refuse room, a building mechanical room, a bike/parking room and one apartment, plus a partial cellar used only for storage. The stair and the elevator pass through the ground floor and every typical floor. Some ZR 23-23 conditions are shown and the allowances are taken; the corridor's daylighting criterion and the parking condition are NOT shown, so those spaces count. On every floor the components, the exterior wall ring among them, add up to exactly the floor's stated outline (ground and typical 40 x 66 = 2,640 sq ft; cellar 40 x 50 = 2,000 sq ft). This made-up layout places 13 dwelling units by design.

Design choices are made up and editable; the allowances shown here are illustrative, not validated. The five above-grade floors are drawn as equal floorplates for simplicity; a real R6B building (45 ft maximum base height, 55 ft maximum building height) would set back the floors above the base height, so equal floors are an assumption.

## The floors and the fit (every floor adds up to its outline)

| Floor | Count | Outside outline (sq ft) | Components on the floor (sq ft) | Difference |
|---|---|---|---|---|
| Partial cellar (storage only, not used for dwelling) | 1 | 2,000 | 2,000 | 0 |
| Ground floor (lobby, services and one apartment) | 1 | 2,640 | 2,640 | 0 |
| Typical residential floor (one of four identical) | 4 | 2,640 | 2,640 | 0 |

On every floor the components listed in the schedule - the exterior wall ring among them - add up to exactly the floor's stated outside outline (difference zero), so the building fits.

## One area schedule (measured from the layout)

| Component | Portion | Measured area (sq ft) | How measured | Under zoning floor area | Under HPD dwelling-unit area |
|---|---|---|---|---|---|
| Apartment net interior floor (rooms within the units) | residential | 7,420 | Finished room areas within the demising walls, from the stated room sizes. | Counts in full (ZR 12-10 floor area (gross floor space used for dwelling)) | Counts (inside a dwelling unit) - Measured within the perimeter walls to the finished face; this is the unit area. |
| Interior partitions within the apartments (non-demising) | residential | 360 | Footprint of the non-demising partition walls inside the units. | Counts in full (ZR 12-10 floor area (gross floor space)) | Counts (inside a dwelling unit) - Internal partitions sit inside the measured perimeter and are included; the model must not subtract all apartment walls. |
| Demising / party-wall thickness (between units and unit-to-corridor) | residential | 528 | Footprint of the demising wall thickness. | Counts in full (ZR 12-10 floor area (measured to exterior/centre lines; gross)) | Excluded - Integral components of demising partitions are excluded from unit area (measured to the finished face). |
| Exterior wall thickness (perimeter ring) | residential | 1,040 | Outer footprint minus the inner (clear) footprint, over the stated floors. | Counts in full (ZR 12-10 floor area (measured from the exterior faces of exterior walls)) | Excluded - Integral components of exterior walls are excluded from unit area. |
| Shared corridors | residential | 1,120 | Corridor width times length, over the stated floors. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-232 (corridor floor-area provisions); ZR 12-10 exclusion); condition: 50% may be exempted with the termination/daylighting/outdoor-access criteria; another 50% where the corridor is no more than 100 ft; the provisions may combine [shown] | Excluded - Circulation between units; not within a dwelling unit. |
| Stairs / stairwells | residential | 960 | Stair footprint over the stated floors. | Counts in full (ZR 12-10 floor area (stairwells at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Elevator shaft | residential | 280 | Shaft footprint over the levels it passes. | Counts in full (ZR 12-10 floor area (elevator shafts at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Mechanical and plumbing chases | residential | 120 | Chase footprint, counted across the floors. | Counts in full (ZR 12-10 floor area (gross floor space; not accessory-mechanical rooms)) | Excluded - All mechanical and plumbing chases are excluded from unit area. |
| Ground-floor lobby / entry | residential | 300 | Lobby footprint. | Counts in full (ZR 12-10 floor area; ZR 23-231 (amenity exclusion does NOT cover circulation)) | Excluded - Shared entry/circulation; not within a dwelling unit. |
| Amenity and laundry room (residents) | residential | 360 | Room footprint on the ground floor. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-231 (amenity floor-area provisions)); condition: accessible to residents and not circulation; capped at 5% of the building's residential floor area [shown] | Excluded - A shared amenity; not within a dwelling unit. |
| Refuse storage / disposal room | residential | 72 | Room footprint on the ground floor. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-233 (refuse floor-area provisions)); condition: up to three square feet per dwelling unit (13 units here = 39 sq ft cap) [shown] | Excluded - A shared service room; not within a dwelling unit. |
| Building mechanical room | residential | 240 | Room footprint on the ground floor. | Excluded only if the stated condition is shown (ZR 12-10 floor area (accessory mechanical equipment)); condition: the room is accessory mechanical-equipment floor space, plus the minimum access [shown] | Excluded - Not within a dwelling unit. |
| Cellar storage (not used for dwelling) | residential | 2,000 | Cellar footprint. | Excluded only if the stated condition is shown (ZR 12-10 floor area (cellar space, unless used for dwelling)); condition: the cellar is not used for dwelling purposes [shown] | Excluded - Not within a dwelling unit. |
| Bike/parking room (does not meet the parking exclusion) | residential | 400 | Room footprint on the ground floor. | Excluded only if the stated condition is shown (ZR 12-10 floor area (accessory off-street parking exclusion)); condition: accessory group parking not more than 23 ft above curb level [NOT shown -> the space counts] | Excluded - Not within a dwelling unit. |

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
- ZR 23-231 (Floor area provisions for amenities) - captured law.
  - Capture: snapshot `zr-23-231`, digest `81eb95e85b333eb86a0fc55413c78567d0b72d7ba9656041f77457f2263b49d6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-231 (last amended 2024-12-05).
  - Quoted: "Floor space in a building allocated to residential amenities may be exempted from the definition of floor area, in an amount not to exceed five percent of the residential floor area of the building"
- ZR 23-233 (Floor area provisions for refuse storage and disposal) - captured law.
  - Capture: snapshot `zr-23-233`, digest `36b8c7da8a4d8359ff7fae9d6f5ecd0cb928971da128c76ac8dc1d04994a7710`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-233 (last amended 2024-12-05).
  - Quoted: "Floor space in a building allocated to refuse storage and disposal may be exempted from the definition of floor area in an amount not to exceed a maximum of three square feet per dwelling unit in the building"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "floor space used for accessory mechanical equipment. Such exclusion shall also include the minimum necessary floor space to provide for necessary maintenance and access to such equipment"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "cellar space, except where such space is used for dwelling purposes"
- ZR 12-10 (Definitions - floor area) - captured law.
  - Capture: snapshot `zr-12-10-floor-area`, digest `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10 (last amended 2024-12-05).
  - Quoted: "within group parking facilities located not more than 23 feet above curb level, except where such floor space used for accessory parking is contained within a public parking garage"

## The two areas, worked out separately, then reconciled

- Residential zoning floor area (sum of what counts under zoning): 12,001 sq ft.
- Total HPD dwelling-unit area (sum of what counts under HPD): 7,780 sq ft.

Reconciliation - every square foot of the difference, by component (nothing is deducted twice):

| From | Component | Amount (sq ft) |
|---|---|---|
| Residential zoning floor area | (start) | 12,001 |
| - counts for zoning but not HPD | demising-partitions | -528 |
| - counts for zoning but not HPD | exterior-walls | -1,040 |
| - counts for zoning but not HPD | corridor | -560 |
| - counts for zoning but not HPD | stair | -960 |
| - counts for zoning but not HPD | elevator | -280 |
| - counts for zoning but not HPD | chases | -120 |
| - counts for zoning but not HPD | lobby | -300 |
| - counts for zoning but not HPD | refuse | -33 |
| - counts for zoning but not HPD | parking-room | -400 |
| = Total HPD dwelling-unit area | (end) | 7,780 |

Ratio for this example = total HPD-measured dwelling-unit area (7,780) / residential zoning floor area (12,001) = 0.6483.

This ratio belongs to THIS made-up example only. Two or three examples cannot establish a typical figure; no percentage is validated here.

## Shared floor area between the uses (ZR 23-20)

A single-use residential building: no floor area is shared between uses, so the ZR 23-20 proportional attribution does not apply here.

## The legal unit cap (a separate figure)

- Maximum residential floor area allowed: 13,000 sq ft (ZR 23-52).
- Divided by the dwelling-unit factor 680: 19.1176 -> 19 dwelling units (ZR 23-52 rounding).
- The density ceiling is a separate figure, not derived from the physical estimate. The measured residential zoning floor area (12,001 sq ft) differs from the 13,000 sq ft the stated FAR would allow.

## What this example shows

- ZR 23-23 allowances are conditional: the amenity and refuse allowances are taken only because their conditions are shown; the parking room counts because its condition is not met; the corridor is 56 ft so only the length-based 50 percent is exempt.
- Spaces already out of zoning (mechanical room, cellar) are not deducted again for HPD - nothing is deducted twice.
- Every floor fits: on each floor the components, the exterior wall ring among them, add up to exactly the floor's stated outside outline.

## What this example does not show

- It does not establish a typical ratio or validate any percentage.
- The withdrawn 0.6022 ratio of the earlier version was computed on an 'outer ring proxy' with no stated floor outline; this rebuilt version states every floor and gives 0.6483.
- It is not a legal or professional determination.

## Sources

- The ZR law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION, read 2026-10-07 at the official HPD site.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Example created for the measurement basis record. | scenario-optimization-engineer |
| 2026-10-07 | Rebuilt so that every floor has a stated outside outline and the components on each floor add up to it exactly (the earlier version used an 'outer ring proxy' and stated no floor outline, so its fit could not be checked). The ratio changes as a consequence: the earlier 0.6022 is WITHDRAWN; the rebuilt building gives residential zoning floor area 12,001, HPD 7,780, ratio 0.6483. | scenario-optimization-engineer |

