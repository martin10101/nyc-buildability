# Example C - a made-up mixed-use building (retail ground floor, residences above)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/scenario/measurement_basis/measurement_basis_render.py` from `<example>.json`; edit the data file and re-render. See `../MEASUREMENT_BASIS.md`.

Mixed-use example: yes.

This layout is made up - a deliberately simple example, not a real property and not a detailed or permit-ready design. Every dimension is stated so each area can be recomputed. The maximum floor area the law allows is used only as a limit to check the layout against, never as the measured space.

This is a draft reading of the law and a guideline by an AI; it is not professionally reviewed and is not a legal or professional determination. Each statistic links to its source text (ADR-007).

## The building in this example

A made-up five-storey mixed-use building: a retail ground floor (sales floor, a back room and the retail's own walls) beside a residential lobby, a shared utility room and the residential core, with four identical residential floors above (two apartments each, reached off a corridor). The stair and the elevator pass through the ground floor and every residential floor. The apartment estimate uses only the RESIDENTIAL portion's zoning floor area, including the counted residential circulation; the retail floor is not added to it, and the shared utility room is attributed under ZR 23-20 rather than added. On every floor the components, the exterior wall ring among them, add up to exactly the floor's stated outline (ground 44 x 70 = 3,080 sq ft; residential 44 x 58 = 2,552 sq ft).

Design choices are made up and editable. Each component is marked exclusive to one use (residential or commercial) or shared; how the mixed building combines its residential and commercial floor areas is itself a question of law not settled here.

## The floors and the fit (every floor adds up to its outline)

| Floor | Count | Outside outline (sq ft) | Components on the floor (sq ft) | Difference |
|---|---|---|---|---|
| Ground floor (retail, residential lobby, shared utility, core) | 1 | 3,080 | 3,080 | 0 |
| Typical residential floor (one of four identical) | 4 | 2,552 | 2,552 | 0 |

On every floor the components listed in the schedule - the exterior wall ring among them - add up to exactly the floor's stated outside outline (difference zero), so the building fits.

## One area schedule (measured from the layout)

| Component | Portion | Measured area (sq ft) | How measured | Under zoning floor area | Under HPD dwelling-unit area |
|---|---|---|---|---|---|
| Apartment net interior floor (rooms within the units) | residential | 6,880 | Finished room areas within the demising walls, from the stated room sizes. | Counts in full (ZR 12-10 floor area (gross floor space used for dwelling)) | Counts (inside a dwelling unit) - Measured within the perimeter walls to the finished face; this is the unit area. |
| Interior partitions within the apartments (non-demising) | residential | 240 | Footprint of the non-demising partition walls inside the units. | Counts in full (ZR 12-10 floor area (gross floor space)) | Counts (inside a dwelling unit) - Internal partitions sit inside the measured perimeter and are included; the model must not subtract all apartment walls. |
| Demising / party-wall thickness (between units and unit-to-corridor) | residential | 384 | Footprint of the demising wall thickness. | Counts in full (ZR 12-10 floor area (measured to exterior/centre lines; gross)) | Excluded - Integral components of demising partitions are excluded from unit area (measured to the finished face). |
| Exterior wall thickness (perimeter ring) | residential | 904 | Outer footprint minus the inner (clear) footprint, over the stated floors. | Counts in full (ZR 12-10 floor area (measured from the exterior faces of exterior walls)) | Excluded - Integral components of exterior walls are excluded from unit area. |
| Shared corridors | residential | 880 | Corridor width times length, over the stated floors. | Excluded only if the stated condition is shown (ZR 23-23 / ZR 23-232 (corridor floor-area provisions); ZR 12-10 exclusion); condition: 50% may be exempted with the termination/daylighting/outdoor-access criteria; another 50% where the corridor is no more than 100 ft; the provisions may combine [shown] | Excluded - Circulation between units; not within a dwelling unit. |
| Stairs / stairwells | residential | 900 | Stair footprint over the stated floors. | Counts in full (ZR 12-10 floor area (stairwells at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Elevator shaft | residential | 280 | Shaft footprint over the levels it passes. | Counts in full (ZR 12-10 floor area (elevator shafts at each floor, except as excluded)) | Excluded - Shared vertical circulation; not within a dwelling unit. |
| Mechanical and plumbing chases | residential | 100 | Chase footprint, counted across the floors. | Counts in full (ZR 12-10 floor area (gross floor space; not accessory-mechanical rooms)) | Excluded - All mechanical and plumbing chases are excluded from unit area. |
| Ground-floor lobby / entry | residential | 300 | Lobby footprint. | Counts in full (ZR 12-10 floor area; ZR 23-231 (amenity exclusion does NOT cover circulation)) | Excluded - Shared entry/circulation; not within a dwelling unit. |
| Shared utility / service room (serves both the shop and the residences) | shared | 120 | Ground-floor room footprint. | Not part of the residential portion (Shared floor area; ZR 23-20 proportional attribution); condition: shared between the residential and commercial uses; attributed proportionately under ZR 23-20, not added to the residential exclusive zoning floor area here [NOT shown -> the space counts] | Excluded - A shared service room; not within a dwelling unit. |
| Retail sales floor (commercial) | non_residential | 1,600 | Ground-floor retail footprint. | Not part of the residential portion (Commercial floor area (its own FAR calculation)); condition: belongs to the commercial portion; counted in the commercial floor-area calculation, not the residential portion [NOT shown -> the space counts] | Excluded - Not a residential dwelling unit. |
| Retail exterior/demising walls (commercial) | non_residential | 300 | Retail wall footprint. | Not part of the residential portion (Commercial floor area); condition: part of the commercial portion [NOT shown -> the space counts] | Excluded - Not a residential dwelling unit. |
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
- ZR 23-20 (Floor area regulations) - captured law.
  - Capture: snapshot `zr-23-20`, digest `0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20 (last amended 2024-12-05).
  - Quoted: "Where floor area in a building is shared by multiple uses, the floor area for such shared portion shall be attributed to each use proportionately, based on the percentage each use occupies of the total floor area of the zoning lot, less any shared floor area"

## The two areas, worked out separately, then reconciled

- Residential zoning floor area (sum of what counts under zoning): 10,428 sq ft.
- Total HPD dwelling-unit area (sum of what counts under HPD): 7,120 sq ft.

Reconciliation - every square foot of the difference, by component (nothing is deducted twice):

| From | Component | Amount (sq ft) |
|---|---|---|
| Residential zoning floor area | (start) | 10,428 |
| - counts for zoning but not HPD | demising-partitions | -384 |
| - counts for zoning but not HPD | exterior-walls | -904 |
| - counts for zoning but not HPD | corridor | -440 |
| - counts for zoning but not HPD | stair | -900 |
| - counts for zoning but not HPD | elevator | -280 |
| - counts for zoning but not HPD | chases | -100 |
| - counts for zoning but not HPD | lobby | -300 |
| = Total HPD dwelling-unit area | (end) | 7,120 |

Ratio for this example = total HPD-measured dwelling-unit area (7,120) / residential zoning floor area (10,428) = 0.6828.

This ratio belongs to THIS made-up example only. Two or three examples cannot establish a typical figure; no percentage is validated here.

## Shared floor area between the uses (ZR 23-20)

One small component (the 120 sq ft shared utility room) is shared between the shop and the residences. Under ZR 23-20 its floor area is attributed to each use by that use's share of the total floor area of the zoning lot, less the shared floor area.

- Residential exclusive zoning floor area: 10,428 sq ft.
- Commercial exclusive floor area: 2,300 sq ft.
- Shared floor area: 120 sq ft (shared-utility).
- Total floor area of the zoning lot: 12,848 sq ft; less the shared floor area, the attribution base is 12,728 sq ft.
- Residential share = residential exclusive / base = 0.8193.
- Attributed to the residential use (ZR 23-20): 98.32 sq ft; to the commercial use: 21.68 sq ft.

Quoted (ZR 23-20, capture `zr-23-20`, digest `0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`): "Where floor area in a building is shared by multiple uses, the floor area for such shared portion shall be attributed to each use proportionately, based on the percentage each use occupies of the total floor area of the zoning lot, less any shared floor area"

CONDITIONAL. ZR 23-20 gives the proportional attribution quoted above; ZR 35-31 is now captured and read (M4-T035 step P5) and carries the same attribution plus a separate maximum floor area ratio for each use and one combined whole-lot cap. The effect of this 98.32 sq ft on the residential figure stays WITHHELD because the maximum commercial floor area ratio (Article III, Chapter 3) is still not captured (DB-188), so the whole-building maximum cannot be read, and whether the attributed shared floor area is ADDED to the residential figure the estimate uses is a question of law, not an owner's preference. The ratio below uses the residential EXCLUSIVE floor area (10,428 sq ft) only; the attribution is shown but not added.

## The legal unit cap (a separate figure)

- Maximum residential floor area allowed: 11,000 sq ft (ZR 23-52).
- Divided by the dwelling-unit factor 680: 16.1765 -> 16 dwelling units (ZR 23-52 rounding).
- The residential density ceiling is a separate figure, not derived from the physical estimate, and uses only the residential floor area; the retail floor area is not added. The measured residential zoning floor area (10,428 sq ft) differs from the 11,000 sq ft the stated FAR would allow.

## What this example shows

- A mixed-use estimate uses the residential portion's zoning floor area, including the counted residential circulation and support space - not the whole building's and not the shop floor's.
- Every component is marked exclusive to one use or shared; the one shared component (the utility room) is attributed proportionately under ZR 23-20 on a separate reconciliation line.
- Every floor fits: on each floor the components, the exterior wall ring among them, add up to exactly the floor's stated outside outline.

## What this example does not show

- It does not establish a typical ratio or validate any percentage.
- It does not settle how the mixed building combines its residential and commercial floor areas: ZR 35-31 is now captured and read (M4-T035 step P5), but the shared-space attribution's effect on the residential figure stays withheld because the maximum commercial floor area ratio (Article III, Chapter 3) is still not captured (DB-188) and whether the attributed shared floor area is added to the residential figure is a question of law.
- The withdrawn 0.6676 ratio of the earlier version was computed on a floor that did not fit (1,743 sq ft of components on a 1,260 sq ft outline); this rebuilt version gives 0.6828.
- It is not a legal or professional determination.

## Sources

- The ZR law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.
- HPD Design Guidelines for New Construction, 2026 edition, UNIT AREA CALCULATION, read 2026-10-07 at the official HPD site.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Example created for the measurement basis record. | scenario-optimization-engineer |
| 2026-10-07 | Rebuilt so that every floor has a stated outside outline and the components on each floor add up to it exactly. The earlier version listed 1,743 sq ft of components on an upper floor whose stated outline was 1,260 sq ft (the apartment rooms alone filled the inside outline) and stated no ground-floor outline. The earlier 0.6676 ratio is WITHDRAWN; the rebuilt building gives residential exclusive zoning floor area 10,428, HPD 7,120, ratio 0.6828. A shared utility room and the ZR 23-20 attribution line were added. | scenario-optimization-engineer |
| 2026-10-08 | Corrected two now-false statements after ZR 35-31 was captured and read (M4-T035 step P5, a dependency of M5-T135): what_it_does_not_show[1] and shared_floor_area.conditional_note no longer say ZR 35-31 is 'not captured yet' or withheld until it is captured. They now state the effect on the residential figure stays withheld/conditional because the maximum commercial floor area ratio (Article III, Chapter 3) is still not captured (DB-188) and whether the attributed shared floor area is added to the residential figure is a question of law. NO figure changed: the ratio stays 0.6828 and the attribution stays 98.32 sq ft residential / 21.68 commercial. | scenario-optimization-engineer |

