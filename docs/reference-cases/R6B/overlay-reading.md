# The commercial-overlay reading: a residential building on the benchmark lot, R6B with a C2-2 overlay, beside the same lot without the overlay

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: section 5 gap K9; section 9 table A (the overlay column that waited for step P2).

An independent reading of the captured C2-2 commercial-overlay law text (step P2, task M4-T026) for the benchmark lot, 215-16 Northern Boulevard in Queens (BBL 4073340070). Each row compares the lot as recorded (district R6B with a C2-2 overlay) against the same lot without the overlay (plain R6B), for a new all-residential building. A value or a yes/no is recorded only where both step-P2 readings give it on the same basis; otherwise the row is 'not known' with the reason and both readings named. Every value comes from the law text and the lot's recorded facts, never from a program run.

## What this case is worth

Prepared by one AI helper and read again, independently, by a second AI, each working alone from the sealed step-P2 folder; their agreement alone is not proof. It is a draft reading of the law, not professionally reviewed, and is not a statement that anything complies. It reads the captured overlay text only; where the overlay text points to a section the repository does not hold, the row says what stays not known.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of the pinned step-P2 overlay law-text captures (without their notes) and the lot's recorded official facts and outline, with no access to the program (reading 1: provenance/return-independent-hand-calculation-5.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-6.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Benchmark lot | 215-16 Northern Boulevard, Queens (QN, borough code 4), BBL 4073340070 | NYC PLUTO row for BBL 4073340070 |
| Lot type | corner (two street frontages meeting at about 89.7 degrees) | the recorded outline and DCM centerlines; cases/real-lot.json row L9 |
| Street widths | Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) | NYC DCM street centerlines; cases/real-lot.json row L11 |
| Building | a new all-residential building (not a mixed building) | the subject of both readings |
| Lot area | two recorded figures that differ: 10,075 sq ft (PLUTO) and about 10,388 sq ft (MapPLUTO outline) | NYC PLUTO field lotarea and the MapPLUTO polygon Shape__Area |

## Rows

### bulk-regulations - Which district's bulk regulations apply to a residential building, and by what route

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "In the districts indicated, the #bulk# regulations of Article II, Chapter 3, shall apply to all #residential buildings# in accordance with the provisions of this Section, except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls."
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "In the districts indicated, the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "(a) on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter suffix shall apply; and"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "(b) on non-#qualifying residential sites#, where such districts are mapped within R1 or R2 Districts, the #bulk# regulations for R3-2 Districts shall apply."

Why the rule applies: The lot has a C2-2 overlay mapped within an R6B district. ZR 34-11 applies the Article II, Chapter 3, bulk regulations to residential buildings in the commercial districts; ZR 34-111 (whose district list includes C2-2) applies the bulk of the surrounding Residence District, with two exceptions - (a) only where mapped within R1 through R5 Districts, (b) only within R1 or R2 Districts. R6B is neither, so neither exception applies and the surrounding R6B district's bulk governs. Both readings read this on the same route.

Expected value: same as plain R6B: the residential bulk regulations of the surrounding R6B district govern, reached by ZR 34-11 (apply the Article II, Chapter 3, bulk) and ZR 34-111 (the bulk of the Residence District within which the overlay is mapped; neither exception (a) nor (b) reaches R6B)

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q1 (R6B bulk governs; neither 34-111(a) nor (b) applies) and return-independent-hand-calculation-6.md Q1 (same route, same result); both readings agree on the same basis (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: ZR 34-11 also points to Sections 34-21 through 34-24 (exceptions to applicability of Residence District controls), of which only 34-24 is captured, so whether an uncaptured 34-21, 34-22 or 34-23 would modify the residential bulk is not known (reading 1 flags this residual; reading 2 reads the captured route as settled). It is not a professional determination and says nothing complies.

### floor-area-ratio - Floor area ratio: does the overlay change it

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Qualifying-housing status = none recorded (source: no qualifying affordable or senior housing fact in the lot's record)

Law relied on:

- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "In the districts indicated, the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: The overlay routes residential bulk to the R6B regulations (ZR 34-111), so the maximum residential floor area ratio is the R6B value of ZR 23-22 - 2.00 for standard residences. None of the eight captured overlay sections states a floor area ratio or changes the Residence District's; both readings read the captured overlay texts as adding no floor area ratio.

Expected value: same as plain R6B: the captured overlay texts add no floor area ratio; the maximum residential floor area ratio is the R6B value of ZR 23-22 (2.00 for standard residences). This comparison holds subject to the uncaptured ZR 34-21 through 34-23, which ZR 34-11 names as exceptions ('except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of Residence District controls') and which neither reader had: reading 1 (return-independent-hand-calculation-5.md) raised that it cannot exclude an overlay-chapter modification of floor area, lot coverage or yards, while reading 2 (return-independent-hand-calculation-6.md) read the captured route as settled.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q2a/Q2b ('NONE of the captured overlay texts states a FAR'; FAR = R6B 2.00 standard) and return-independent-hand-calculation-6.md Q2a/Q2b (same); both agree the overlay adds no floor area ratio (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The separate 2.40 ratio for qualifying affordable or senior housing needs a qualifying-housing fact not recorded, so the choice between 2.00 and 2.40 is not settled by the facts (both readings). Because ZR 34-11 also points to the uncaptured Sections 34-21 through 34-23 (its named exceptions), an overlay-chapter modification cannot be fully excluded - a caveat reading 1 raised and reading 2 did not, which is why the comparison is recorded subject to it rather than as settled. It asserts no floor-area figure and says nothing complies.

### lot-coverage - Lot coverage: does the overlay change it

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)

Law relied on:

- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "In the districts indicated, the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"

Why the rule applies: The overlay routes residential bulk to the R6B regulations (ZR 34-111), so lot coverage is set by the R6B ZR 23-362. None of the captured overlay texts states a lot-coverage rule or changes the Residence District's; both readings read the captured overlay texts as adding no lot-coverage rule.

Expected value: same as plain R6B: the captured overlay texts add no lot-coverage rule; lot coverage is set by the R6B ZR 23-362. This comparison holds subject to the uncaptured ZR 34-21 through 34-23, which ZR 34-11 names as exceptions ('except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of Residence District controls') and which neither reader had: reading 1 (return-independent-hand-calculation-5.md) raised that it cannot exclude an overlay-chapter modification of floor area, lot coverage or yards, while reading 2 (return-independent-hand-calculation-6.md) read the captured route as settled.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q2a/Q3 (overlay states no lot-coverage rule) and return-independent-hand-calculation-6.md Q2a (same); both agree the overlay adds no lot-coverage rule (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: Both readings separately read the whole lot as a corner lot at 100 percent under ZR 23-362(a), but that single whole-lot figure is not settled: the per-portion reading in cases/real-lot.json row L5 and cases/step-p1-worked.json leaves the benchmark lot's coverage not known as a single whole-lot figure, because part of the lot lies beyond 100 feet of the 215 Place street line. This case therefore asserts no whole-lot coverage percentage and does not change row L5; it records only that the overlay adds no coverage rule. Because ZR 34-11 also points to the uncaptured Sections 34-21 through 34-23 (its named exceptions), an overlay-chapter modification cannot be fully excluded - a caveat reading 1 raised and reading 2 did not, which is why the comparison is recorded subject to it rather than as settled. It says nothing complies.

### dwelling-units - Dwelling units: does the overlay change the limit

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Building type = a multiple-dwelling residence, not a conversion (source: the subject of both readings)
- Special density area = none recorded (Queens; not the Manhattan Core or Special Downtown Brooklyn District) (source: cases/step-p1-worked.json rows special-density-areas-list and special-density-real-lot)

Law relied on:

- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "In the districts indicated, the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: The overlay routes residential bulk to the R6B regulations (ZR 34-111), so the maximum number of dwelling units is set by the R6B ZR 23-52 - the maximum residential floor area divided by the factor 680 for a standard multiple-dwelling residence. None of the captured overlay texts states a dwelling-unit rule; both readings read the captured overlay texts as adding none.

Expected value: same as plain R6B: the captured overlay texts add no dwelling-unit rule; the maximum number of dwelling units is set by the R6B ZR 23-52 (factor 680 for a standard multiple-dwelling residence)

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q2a/Q3 (overlay states no dwelling-unit rule; factor 680) and return-independent-hand-calculation-6.md Q2a (same); both agree the overlay adds no dwelling-unit rule (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The unit count itself is not asserted here: it rests on the maximum residential floor area, which depends on the unresolved lot area (both readings give about 29 units at the PLUTO 10,075 sq ft figure and about 30 at the outline 10,388 sq ft figure). Whether the lot is in a special density area (where no factor applies) is not settled by the captured text. It says nothing complies.

### base-and-building-height - Base heights and building height: does the overlay change them

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- R6B height-row footnote = none (source: ZR 23-432 R6B row carries no footnote)

Law relied on:

- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "(1) the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied;"
- ZR 35-63 (Height and Setback Requirements in Commercial Districts with R6 Through R12 Equivalency) - captured.
  - Capture: snapshot `zr-35-63`, file `docs/research/zr-snapshots/v1/zr-35-63.snapshot.json`.
  - Content digest: `77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63.
  - Quoted: "the #street wall# location of a #building# shall be as set forth in Section 35-631, and the height and setback provisions shall be as set forth in Section 35-632."
- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "The minimum base height, maximum base height and maximum #building# height shall be as set forth in the table in Section 23-432 for the applicable #Residence District#."
- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum building height shall be as set forth in the following table"
  - From the captured table, district R6B: min_base_height_ft = 30; standard_max_base_height_ft = 45; standard_max_building_height_ft = 55.

Why the rule applies: For a C2-2 overlay with R6B (an R6-through-R12 district), ZR 34-24(b)(1) applies the ZR 35-63 modifications; ZR 35-63 sends the height and setback to ZR 35-632; ZR 35-632(a) takes the minimum base height, maximum base height and maximum building height from the ZR 23-432 table for the applicable Residence District (R6B): minimum base 30 ft, maximum base 45 ft, maximum building 55 ft for standard residences. Plain R6B reaches the same ZR 23-432 R6B row through ZR 23-43, so the overlay does not change the base or building heights. Both readings read this on the same route.

Expected value: same as plain R6B: minimum base 30 ft, maximum base 45 ft, maximum building 55 ft (standard residences), reached by ZR 35-632(a) to the same ZR 23-432 R6B row that plain R6B uses; the overlay does not change the base or building heights

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q3a/Q3b (35-632(a) -> 23-432 R6B row = 30/45/55; overlay effect none) and return-independent-hand-calculation-6.md Q3a/Q3b (same); both agree (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The 65-ft maximum building height applies only to qualifying affordable or senior housing, a fact not recorded (both readings). Height is measured from the base plane (ZR 35-63), whose definition is not captured, so absolute above-grade heights are not fixed. ZR 34-24(b)(2) points to the uncaptured Section 36-64 (special-area height and setback), so an extra-area modification cannot be read. It says nothing complies.

### setback-above-base - Setback above the base: does the overlay change it

Facts used:

- Street widths = Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) (source: NYC DCM street centerlines; cases/real-lot.json row L11)

Law relied on:

- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided at a height not lower than the minimum base height or higher than the maximum base height, in accordance with Section 23-433."
- ZR 23-433 (Standard setback regulations) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any street wall fronting on a wide street, and a setback with a depth of at least 15 feet shall be provided from any street wall fronting on a narrow street"

Why the rule applies: ZR 35-632(a) routes the setback above the maximum base height to ZR 23-433, which requires a setback of at least 10 feet from a street wall on a wide street (Northern Boulevard) and at least 15 feet on a narrow street (215 Place). Plain R6B reaches the same ZR 23-433 through ZR 23-43, so the overlay does not change the setback depths. Both readings read this the same way.

Expected value: same as plain R6B: at least 10 ft above the maximum base height on the wide street (Northern Boulevard) and at least 15 ft on the narrow street (215 Place), reached by ZR 35-632(a) to the same ZR 23-433 that plain R6B uses; the overlay does not change the setback depths

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q3c (10 ft wide / 15 ft narrow; overlay effect none on depths) and return-independent-hand-calculation-6.md Q3c (same); both agree (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The setback is not modelled on the lot; ZR 23-433(a) to (d) may reduce or adjust the depths (for example a one-foot-for-one-foot reduction, floor of seven feet). It says nothing complies.

### street-wall-location - Street wall location: does the overlay change it

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Street widths = Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) (source: NYC DCM street centerlines; cases/real-lot.json row L11)

Law relied on:

- ZR 35-63 (Height and Setback Requirements in Commercial Districts with R6 Through R12 Equivalency) - captured.
  - Capture: snapshot `zr-35-63`, file `docs/research/zr-snapshots/v1/zr-35-63.snapshot.json`.
  - Content digest: `77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63.
  - Quoted: "the #street wall# location of a #building# shall be as set forth in Section 35-631"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "For #Commercial Districts# mapped within, or with a #residential equivalent# of, R8 through R12 Districts, when located within the #Manhattan Core#"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."
- ZR 35-633 (Additional height and setback provisions) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and"
- ZR 23-431 (Street wall location requirements) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "In R6B, R7B, and R8B Districts, the #street wall# of a #building# shall be located no closer to the #street line# than the closest #street wall#, or portion thereof, nor further from the #street line# than the furthest #street wall#, or portion thereof, of an existing adjacent #building# on the same or an adjoining #zoning lot# located on the same #street# frontage."

Why the rule applies: Under the overlay, ZR 35-63 sends the street-wall location to ZR 35-631, and ZR 35-633(a) supersedes any ZR 23-431 street-wall reference with ZR 35-631. ZR 35-631's line-up rule (paragraph (a)) is limited to R8 through R12 Districts in the Manhattan Core, so for this R6B lot the percentage rule of paragraph (b) governs - at least 70 percent of the aggregate street-wall width within eight feet of the street line. Plain R6B instead uses ZR 23-431, whose paragraph (a) names R6B and sets a line-up to existing adjacent buildings. So the overlay changes the street-wall location rule. Both readings read this the same way.

Expected value: changed by the overlay: from the R6B line-up rule of ZR 23-431(a) (line up to existing adjacent buildings) to the percentage rule of ZR 35-631(b) (at least 70 percent of the aggregate street-wall width within eight feet of the street line), reached through ZR 35-63 and ZR 35-633(a)

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q4a/Q4c (overlay CHANGES street wall: 23-431(a) line-up -> 35-631(b) percentage, flat 8 ft) and return-independent-hand-calculation-6.md Q4a/Q4c (same); both agree it is changed (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: Whether a prevailing street wall frontage exists (a proviso in both regimes can use it to switch the applicable paragraph) is a defined term not captured and a fact not recorded, so the final street-wall line is not fixed. It says nothing complies.

### rear-yard - Rear yard: does the overlay change it for an all-residential building

Facts used:

- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Building = a new all-residential building (not a mixed building) (source: the subject of both readings)

Law relied on:

- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"
- ZR 35-53 (Modification of Rear Yard Requirements) - captured.
  - Capture: snapshot `zr-35-53`, file `docs/research/zr-snapshots/v1/zr-35-53.snapshot.json`.
  - Content digest: `755aa5113e8ea050c21e41355448ed20d88610eeaadaea256a92c23611629ceb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53.
  - Quoted: "for a #residential# portion of a #mixed building#, the required #residential# #rear yard# shall be provided at the floor level of the lowest #story# used for #dwelling units# or #rooming units#, where any window of such #dwelling units# or #rooming units# faces onto such #rear yard#"
- ZR 23-344 (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less"
- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "shall be provided on #interior lots# in accordance with this Section"

Why the rule applies: The only captured overlay rear-yard text, ZR 35-53, applies by its own words to a residential portion of a mixed building; the subject is a new all-residential building, so ZR 35-53 does not set its rear yard. The rear yard stays the Article II reading: ZR 23-344(a) requires no rear yard within 100 feet of the corner point (the street lines meet at about 89.7 degrees, 135 or less), and ZR 23-342's interior-lot requirement governs beyond that. So the overlay does not change the all-residential rear-yard reading. Both readings read this the same way.

Expected value: same as plain R6B for an all-residential building: the overlay's only rear-yard text, ZR 35-53, reaches only the residential portion of a mixed building, so it does not change the rear yard; within 100 feet of the corner no rear yard is required (ZR 23-344(a)). This comparison holds subject to the uncaptured ZR 34-21 through 34-23, which ZR 34-11 names as exceptions ('except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of Residence District controls') and which neither reader had: reading 1 (return-independent-hand-calculation-5.md) raised that it cannot exclude an overlay-chapter modification of floor area, lot coverage or yards, while reading 2 (return-independent-hand-calculation-6.md) read the captured route as settled.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q5a/Q5b (35-53 reaches only mixed buildings; overlay effect none for an all-residential building) and return-independent-hand-calculation-6.md Q5a/Q5b (same); both agree (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: Beyond 100 feet of the corner the rear-yard outcome is not known (it needs the neighbouring lot-line configuration and, for any depth, the building type and lot width); that is the plain-R6B reading recorded in cases/real-lot.json row L12 and is unchanged here. The defined term mixed building is not captured. Because ZR 34-11 also points to the uncaptured Sections 34-21 through 34-23 (its named exceptions), an overlay-chapter modification cannot be fully excluded - a caveat reading 1 raised and reading 2 did not, which is why the comparison is recorded subject to it rather than as settled. It says nothing complies.

### paragraphs-applicable - Which paragraphs of ZR 34-111, 34-24, 35-632 and 35-631 apply or do not apply to this lot

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- District form = R6B is an R6 district with the letter suffix B (source: the district designation)
- Lot area = about 10,075 to 10,388 sq ft (two recorded figures) (source: cases/real-lot.json; the two figures differ)
- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)

Law relied on:

- ZR 11-25 (District Designations Appended with Suffixes) - captured.
  - Capture: snapshot `zr-11-25`, file `docs/research/zr-snapshots/v1/zr-11-25.snapshot.json`.
  - Content digest: `6843ad22d57d4f59cf422c80b820d1797955c1cecfecf3ee459b68bf139b2b2b`.
  - Official page: https://zr.planning.nyc.gov/entityprint/pdf/node/18433.
  - Quoted: "All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth in express provisions of this Resolution"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "(a) on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter suffix shall apply; and"
- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "(a) In Commercial Districts with R1 through R5 equivalency"
- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "(b) In Commercial Districts with R6 through R12 equivalency"
- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "In #Commercial Districts# mapped within, or with a #residential equivalent# of R6 through R12 without a letter suffix, for #zoning lots# meeting the criteria of paragraph (a) of Section 23-434, the maximum #building# heights may be increased"
- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "In #Commercial Districts# mapped within, or with a #residential equivalent# of R9 through R12 Districts"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "For #Commercial Districts# mapped within, or with a #residential equivalent# of, R8 through R12 Districts, when located within the #Manhattan Core#"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "(b) Percentage-based rules"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "at least 40,000 square feet"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "(d) Articulation allowances"

Why the rule applies: Which paragraph of each overlay height and street-wall section applies to this lot follows from the captured district conditions, with R6B reaching the R6-through-R12 provisions through ZR 11-25. ZR 34-111's exceptions (a) (R1 through R5) and (b) (R1 or R2) do not reach R6B, so its main clause (R6B bulk) applies. ZR 34-24 paragraph (b) (R6 through R12 equivalency) applies and (a) (R1 through R5) does not. ZR 35-632 paragraph (a) governs the heights; (b) does not apply because it is limited to districts without a letter suffix and R6B has the suffix B; (c) does not apply because it is limited to R9 through R12. ZR 35-631 paragraph (b) governs the street wall because (a) is limited to R8 through R12 Districts in the Manhattan Core, (c) needs a lot of at least 40,000 square feet (this lot is about 10,075 to 10,388 square feet), and (d) articulation applies in all districts. Both readings read the same paragraphs as applying or not on the same basis.

Expected value: ZR 34-111: neither exception (a) nor (b) applies (its main clause, R6B bulk, governs). ZR 34-24: paragraph (b), R6 through R12 equivalency, applies; (a), R1 through R5, does not. ZR 35-632: paragraph (a) governs the heights; (b) does not apply (R6B has a letter suffix); (c) does not apply (R9 through R12 only). ZR 35-631: paragraph (b) governs; (a) does not apply (R8 through R12 in the Manhattan Core); (c) does not apply (needs a lot of at least 40,000 square feet); (d) articulation applies in all districts.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q1/Q3a/Q3b/Q4a and return-independent-hand-calculation-6.md Q1/Q3a/Q3b/Q4a; both read the same paragraphs as applying or not on the same basis (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The paragraph selection does not read the uncaptured sections those paragraphs point to (ZR 34-24(b)(2) Section 36-64, (b)(3) Section 35-71, ZR 35-632(b) Section 23-434 and (c) Section 23-435), and does not settle whether a prevailing street wall frontage exists. R6B's reach to the R6-through-R12 provisions is a reading of ZR 11-25, not an express naming of R6B. It says nothing complies.

### section-35-633 - What ZR 35-633 adds

Facts used:

- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Street frontages = two (Northern Boulevard and 215 Place) (source: the recorded outline; cases/real-lot.json row L10)

Law relied on:

- ZR 35-633 (Additional height and setback provisions) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows:"
- ZR 35-633 (Additional height and setback provisions) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and"
- ZR 35-633 (Additional height and setback provisions) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage."

Why the rule applies: ZR 35-633 brings in the additional height and setback regulations of Section 23-436, with the ZR 23-431 street-wall reference swapped for ZR 35-631 and a corner-lot street-wall clause. The step-P2 readers (readings 5 and 6) did not have Section 23-436, so they could not read what those additional provisions require or whether any of them bind this building, and they differ on the corner-lot clause. Section 23-436 was since captured (task M4-T029) and read in step P3 (cases/step-p3-worked.json).

Expected value: not known. What ZR 35-633 adds cannot be settled from the step-P2 readings: it imports the additional height and setback regulations of Section 23-436, which the step-P2 readers (readings 5 and 6) did not have, so their substance and whether they bind this building are not known (both step-P2 readings). The two step-P2 readings also differ on the ZR 35-633(b) corner-lot street-wall clause: reading 1 (return-independent-hand-calculation-5.md Q3d) reads it as not known, because whether a Commercial District is mapped along the entire block frontage is not in the record; reading 2 (return-independent-hand-calculation-6.md Q3d) reads it as not biting on the recorded facts, because the clause is for a zoning lot bounded by only one street line and this lot has two street frontages. The row therefore stays not known and names both readings. Section 23-436 was since captured (task M4-T029) and read in step P3 (cases/step-p3-worked.json), where both step-P3 readings read paragraph (c) as binding (the street wall along the wide Northern Boulevard, via ZR 35-631) and ZR 35-633(a) as applying, while ZR 35-633(b) stays not known.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q3d and return-independent-hand-calculation-6.md Q3d; both read the Section 23-436 substance as not known, and they differ on the ZR 35-633(b) corner-lot clause (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: It gives no additional height or setback requirement from the step-P2 readings; Section 23-436 is the text the step-P2 readers did not have (now captured and read in cases/step-p3-worked.json). It says nothing complies.

### not-captured - Every section and defined term the overlay texts point to that is not captured, and what stays not known

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"
- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "(2) the special height and setback provisions for certain areas set forth in Section 36-64 shall be applied; and"
- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "the provisions set forth in Section 35-71, inclusive, shall be applied"
- ZR 35-63 (Height and Setback Requirements in Commercial Districts with R6 Through R12 Equivalency) - captured.
  - Capture: snapshot `zr-35-63`, file `docs/research/zr-snapshots/v1/zr-35-63.snapshot.json`.
  - Content digest: `77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63.
  - Quoted: "Additional height and setback provisions are set forth in Section 35-633 and Section 35-64, inclusive."
- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "for #zoning lots# meeting the criteria of paragraph (a) of Section 23-434, the maximum #building# heights may be increased"
- ZR 35-632 (Maximum height of buildings and setback regulations) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "towers shall be permitted pursuant to the provisions of Section 23-435"
- ZR 35-633 (Additional height and setback provisions) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "The additional height and setback regulations set forth in Section 23-436 shall apply"
- ZR 35-53 (Modification of Rear Yard Requirements) - captured.
  - Capture: snapshot `zr-35-53`, file `docs/research/zr-snapshots/v1/zr-35-53.snapshot.json`.
  - Content digest: `755aa5113e8ea050c21e41355448ed20d88610eeaadaea256a92c23611629ceb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53.
  - Quoted: "pursuant to Section 23-41 (Permitted Obstructions), inclusive."
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "when located within the #Manhattan Core#"
- ZR 35-631 (Street wall location) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "a #block# with a #prevailing street wall frontage#"
- ZR 35-53 (Modification of Rear Yard Requirements) - captured.
  - Capture: snapshot `zr-35-53`, file `docs/research/zr-snapshots/v1/zr-35-53.snapshot.json`.
  - Content digest: `755aa5113e8ea050c21e41355448ed20d88610eeaadaea256a92c23611629ceb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53.
  - Quoted: "for a #residential# portion of a #mixed building#"

Why the rule applies: The captured overlay texts point to sections and defined terms the repository does not hold; this row names each pointer and what stays not known because of it. Both readings name these as not captured.

Expected value: Not captured, pointed to by the overlay texts: Sections 34-21, 34-22 and 34-23 (ZR 34-11, exceptions to applicability of Residence District controls); Section 36-64 (ZR 34-24(b)(2), special-area height and setback); Section 35-71 (ZR 34-24(b)(3), the optional sky-exposure-plane envelope); Section 35-64 (ZR 35-63, additional height and setback); Section 23-434 (ZR 35-632(b), eligible-site height increase); Section 23-435 (ZR 35-632(c), towers); Section 23-436 (ZR 35-633, additional height and setback); Section 23-41 (ZR 35-53, permitted obstructions); and the defined terms Manhattan Core (ZR 35-631(a)), prevailing street wall frontage (ZR 35-631) and mixed building (ZR 35-53). What stays not known because of them: the substance of ZR 35-633 and Section 23-436 (the additional height and setback), any special-area modification under 36-64, the optional sky-plane envelope under 35-71, and - because ZR 34-11 points to the uncaptured 34-21 through 34-23 - whether an overlay-chapter exception modifies floor area, coverage or the rear yard.

Where this stands in the independent reading: return-independent-hand-calculation-5.md Q6 and return-independent-hand-calculation-6.md Q6; both name these sections and terms as not captured (return-independent-hand-calculation-5.md and return-independent-hand-calculation-6.md).

What this row does not establish: The list is of sections and terms the captured overlay texts name; it is not a claim that the repository holds no other related text. On these facts 36-64, 35-71, 23-434 and 23-435 do not change this lot's reading (they are inapplicable or optional), while Section 23-436 and Sections 34-21 through 34-23 leave the noted points not known. Reading 2 additionally names further uncaptured defined terms (base plane, residential equivalent, aggregate width of street walls, outer court, and the qualifying affordable or senior housing terms) that bound the fine application but do not change which rule governs; reading 1 does not list all of these, so they are noted here, not recorded as the agreed list. It says nothing complies.

## What this case does not establish

- It reads the captured overlay sections only; where they point to an uncaptured section (for example Section 23-436, 36-64, 35-71 or 35-64) the affected point stays not known.
- It records a value or a yes/no only where both readings agree on the same basis; where they differ or do not settle a point, the row stays not known and names both readings.
- It asserts no whole-lot coverage percentage and no dwelling-unit count, and does not change any value in cases/real-lot.json (row L5 stays not known for its per-portion reason).
- It is not a professional or legal determination and does not say the lot complies with anything.

## Sources

- The commercial-overlay reading 1: provenance/return-independent-hand-calculation-5.md
- The commercial-overlay reading 2: provenance/return-independent-hand-calculation-6.md
- The sealed folder given to each helper: the pinned step-P2 law-text captures (the C2-2 overlay sections and the residential bulk sections they route to, without the notes describing how the program encoded them) and the lot's recorded official facts and outline, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Case created (step P2, task M4-T028) from the two independent readings of the commercial-overlay sealed folder (provenance/return-independent-hand-calculation-5.md and -6.md). It records, for the benchmark lot with its C2-2 overlay beside the same lot without the overlay, a value or a yes/no only where both readings agree on the same basis; the row on what ZR 35-633 adds stays not known because the step-P2 readers did not have Section 23-436 and the two readings differ on the corner-lot clause. | rules-engineer (M4-T028) |
| 2026-10-07 | Row section-35-633: expected value unchanged (not known). Section 23-436 was captured by task M4-T029 and read independently in step P3 (cases/step-p3-worked.json); the row's wording is brought from 'not captured' into 'the readers did not have' form and points to the step-P3 reading, which both step-P3 readings support (paragraph (c) binds along the wide Northern Boulevard via ZR 35-631; ZR 35-633(a) applies; ZR 35-633(b) stays not known). The row stays not known for the step-P2 readings, which did not have Section 23-436 and differ on the ZR 35-633(b) corner-lot clause. Reason: corrected evidence - the text is now captured and read. | rules-engineer (M4-T030) |

