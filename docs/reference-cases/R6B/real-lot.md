# The real lot: 215-16 Northern Boulevard, Queens (BBL 4073340070)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: A.

An independent, by-hand reading of the R6B zoning limits for one real lot, 215-16 Northern Boulevard in Queens (BBL 4073340070). A C2-2 commercial overlay is recorded; the overlay's own rules are not read here. Every value below comes from the law text and the lot's recorded facts, never from a program run.

## What this case is worth

Prepared by an AI helper and recomputed by a second AI; their agreement alone is not proof. It is a draft reading of the law, not professionally reviewed, and is not a statement that anything complies. It is one lot. Most sections were read from the same captures the rules were written from, so an error in a capture would be shared; four sections (ZR 23-22, 23-432, 23-362 and 23-52) were also read on the official page on 2026-10-06. The corner-lot definition it uses (ZR 12-10) and ZR 23-342 are now captured (task M4-T025) and were read independently by two step-P1 readings (see cases/step-p1-worked.json).

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of pinned law-text captures and the lot's recorded facts, with no access to the program.
- Checked by: A second AI recomputed the arithmetic and the geometry independently from the same sealed folder. Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070 (recorded official response), field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Lot area (city record) | 10,075 sq ft | NYC PLUTO row for BBL 4073340070, field lotarea; units square feet per the PLUTO data dictionary |
| Lot front (city record) | 100.76 ft | NYC PLUTO row for BBL 4073340070, field lotfront |
| Lot depth (city record) | 100.00 ft | NYC PLUTO row for BBL 4073340070, field lotdepth |
| Split-zone record | no (splitzone false) | NYC PLUTO row for BBL 4073340070, field splitzone |
| Tax-map outline area (alternate) | about 10,388 sq ft | MapPLUTO polygon for BBL 4073340070, Shape__Area 10,387.99; a drawing measure |
| Northern Boulevard mapped width | 100 ft | NYC DCM street centerline OBJECTID 53832, Streetwidth (City Map width as served) |
| 215 Place mapped width | 60 ft | NYC DCM street centerline OBJECTID 11453, Streetwidth (City Map width as served) |
| Lot outline | five vertices P0..P4 in EPSG:2263 US survey feet | Recorded MapPLUTO polygon for BBL 4073340070; approximate tax-map boundary |

## Rows

### L1 - Maximum residential floor area, standard residences

Facts used:

- Floor area ratio for R6B standard residences = 2.00 (source: ZR 23-22, R6B row)
- Lot area = 10,075 sq ft (source: city record (PLUTO lotarea))

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: The lot is in an R6B district; ZR 23-22 sets the maximum residential floor area ratio for R6B at 2.00 for standard residences, and the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area, standard: 2.00 (floor area ratio for R6B standard residences (ZR 23-22)) x 10,075 (lot area, city record (sq ft)) = 20,150

Expected value: 20,150 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(c): '2.00 x 10,075 = 20,150 sf'.

What this row does not establish: It uses the city-record lot area of 10,075 sq ft. A second figure, the tax-map outline area of about 10,388 sq ft, differs by about 3 percent; the outline area is a drawing measure and is never used in a floor-area calculation. This is one tax lot and does not prove the zoning lot.

### L2 - Maximum residential floor area, qualifying affordable or senior housing

Facts used:

- Floor area ratio for R6B qualifying housing = 2.40 (source: ZR 23-22, R6B row)
- Lot area = 10,075 sq ft (source: city record (PLUTO lotarea))

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: qualifying_affordable_or_senior_housing = 2.40.

Why the rule applies: ZR 23-22 sets a separate, higher floor area ratio of 2.40 for an R6B zoning lot containing qualifying affordable or qualifying senior housing; the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area, qualifying housing: 2.40 (floor area ratio for R6B qualifying housing (ZR 23-22)) x 10,075 (lot area, city record (sq ft)) = 24,180

Expected value: 24,180 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(c): '2.40 x 10,075 = 24,180 sf'.

What this row does not establish: Whether this lot may use the 2.40 ratio depends on eligibility rules for qualifying affordable or qualifying senior housing, which are not in the captured text; this row shows only the arithmetic if the 2.40 ratio applies.

### L3 - Heights, standard residences

Facts used:

- District = R6B (source: city record)
- R6B height row footnote = none (source: ZR 23-432 R6B row carries no footnote)

Law relied on:

- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum building height shall be as set forth in the following table"
  - From the captured table, district R6B: min_base_height_ft = 30; standard_max_base_height_ft = 45; standard_max_building_height_ft = 55.

Why the rule applies: ZR 23-432 sets, for the R6B row, a minimum base height, a maximum base height and a maximum building height; the R6B row carries no footnote, so a wide or narrow street does not change them.

Expected value: minimum base 30 ft; maximum base 45 ft; maximum building 55 ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(d): 'Min base height 30 ft. Standard: max base 45 ft, max building 55 ft.'

What this row does not establish: These are the district's table limits, not the property's confirmed maximum; another height rule not read here could lower them. How height is measured on the lot (the base plane for R6-R12) is not in the captured text.

### L4 - Heights, qualifying affordable or senior housing

Facts used:

- District = R6B (source: city record)
- R6B height row footnote = none (source: ZR 23-432 R6B row carries no footnote)

Law relied on:

- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum building height shall be as set forth in the following table"
  - From the captured table, district R6B: min_base_height_ft = 30; qualifying_max_base_height_ft = 45; qualifying_max_building_height_ft = 65.

Why the rule applies: ZR 23-432 sets separate maximum base and building heights for an R6B zoning lot containing qualifying affordable or qualifying senior housing; the minimum base height is the same.

Expected value: minimum base 30 ft; maximum base 45 ft; maximum building 65 ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(d): 'Qualifying affordable/senior: max base 45 ft, max building 65 ft.'

What this row does not establish: These are the district's table limits, not the property's confirmed maximum. Eligibility for qualifying housing, and how height is measured on the lot, are not in the captured text.

### L5 - Maximum lot coverage

Facts used:

- Lot type = corner (source: two street frontages meeting at 89.7 degrees (row L9))
- Reach from the 215 Place street line = 103.93 ft (source: return 2, Q1(a): a strip about 3.93 ft wide, about 390 sq ft, lies beyond 100 ft)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"
- ZR 12-10 (Definitions (lot, corner)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#"

Why the rule applies: ZR 23-362(a) gives corner lots 100 percent and interior or through lots 80 percent; the captured ZR 12-10 corner-lot definition limits the 100-percent corner-lot rule to the portion within 100 feet of each street line. Part of this lot lies beyond 100 feet of the 215 Place street line, so it is a corner-lot portion plus a remaining interior-lot portion.

Expected value: not known. No single whole-lot coverage figure. The corner-lot 100-percent rule covers only the part of the lot within 100 feet of each street line; this lot reaches 103.93 feet from the 215 Place street line (a strip about 3.93 feet wide, about 390 square feet), so the whole lot is not the corner-lot portion. Both step-P1 readings read it per portion: the corner-lot portion has a maximum residential lot coverage of 100 percent and the remaining interior-lot portion 80 percent.

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(e), and return-independent-hand-calculation-2.md, Q1(a)-(b); the per-portion reading is confirmed by both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q2a).

What this row does not establish: It gives no whole-lot coverage percentage and does not settle the corner-lot portion to the square foot (the two step-P1 readings give about 9,998 and 9,997.6 square feet for the corner portion, resting on the approximate outline and a one-foot street-line tolerance).

### L6 - Maximum dwelling units, standard residences

Facts used:

- Maximum residential floor area, standard = 20,150 sq ft (source: row L1)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor; for standard multiple-dwelling residences the factor is 680, and a fraction of three-quarters or more counts as one unit, otherwise it is dropped.

Working, step by step:

- maximum dwelling units, standard: 20,150 (maximum residential floor area, standard (sq ft), from row L1) / 680 (dwelling-unit factor (ZR 23-52(b))) = 29.63...; a fraction below three-quarters is dropped -> 29

Expected value: 29 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(g): '20,150/680 = 29.63 -> frac 0.63 <0.75 -> 29 DU'.

What this row does not establish: It is the legal unit limit for a new all-residential building and rests on the standard floor area (row L1), hence on the city-record lot area. Whether the lot is in a special density area, where the factor does not apply, is not settled by the captured text.

### L7 - Maximum dwelling units, qualifying affordable housing

Facts used:

- Maximum residential floor area, qualifying housing = 24,180 sq ft (source: row L2)
- Dwelling-unit factor = 680 (source: ZR 23-52(b); qualifying affordable housing is not in the ZR 23-52(a) no-factor list)

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: If the housing qualifies for the 2.40 ratio, ZR 23-52 divides the qualifying residential floor area of row L2 by the dwelling-unit factor; qualifying affordable housing is not in the ZR 23-52(a) list that has no factor, so the factor is 680, and a fraction below three-quarters is dropped.

Working, step by step:

- maximum dwelling units, qualifying affordable housing: 24,180 (maximum residential floor area, qualifying housing (sq ft), from row L2) / 680 (dwelling-unit factor (ZR 23-52(b))) = 35.55...; a fraction below three-quarters is dropped -> 35

Expected value: 35 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(g): 'Qualifying AFFORDABLE (24,180 sf): 24,180/680 = 35.56 -> 35 DU', with Task 3 item 9 (the eligibility definition is not in the sealed folder).

What this row does not establish: Whether this lot's housing qualifies for the 2.40 ratio depends on eligibility rules for qualifying affordable housing, which are not in the captured text; this row shows the arithmetic only if the housing qualifies.

### L8 - Maximum dwelling units, qualifying senior housing

Facts used:

- Housing type = qualifying senior housing (source: ZR 23-52(a)(2))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "there shall be no applicable dwelling unit factor"
- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "(2) qualifying senior housing"

Why the rule applies: ZR 23-52(a)(2) gives qualifying senior housing no applicable dwelling-unit factor, so the maximum number of units is not determined by this division.

Expected value: not known. ZR 23-52(a)(2) gives qualifying senior housing no applicable dwelling-unit factor, so the maximum number of units is not set by this division; the captured text does not settle a number.

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(g): 'Qualifying SENIOR housing: 23-52(a)(2) gives no applicable dwelling unit factor -> DU count NOT determined by this formula'.

What this row does not establish: It gives no unit count for qualifying senior housing; another rule, not read here, would govern.

### L9 - Lot type

Facts used:

- Street frontages = Northern Boulevard (edge P1-P2) and 215 Place (edge P2-P3) (source: recorded outline and DCM centerlines)
- Interior angle at the lot corner = 89.7 degrees (source: return 1, Task 1(a)/(b), from the outline)

Law relied on:

- ZR 12-10 (Definitions (lot, corner)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle formed by the extensions of the #street lines#"

Why the rule applies: The lot adjoins the intersection of two streets and the interior angle formed by the street lines is 89.7 degrees, which is 135 degrees or less, so under the captured ZR 12-10 corner-lot definition it is a corner lot.

Expected value: corner

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(a): 'LOT TYPE = CORNER LOT ... 89.7 deg <= 135 deg -> corner lot confirmed'; both step-P1 readings confirm the corner classification (return-independent-hand-calculation-3.md and -4.md, Q1a).

What this row does not establish: The classification uses the approximate tax-map outline. The PLUTO lottype code is not relied on, because its meaning is not given in the sealed folder.

### L10 - Frontages

Facts used:

- Edge P1-P2 (Northern Boulevard) = 103.9 ft (source: recorded outline, return 1 Task 1(a))
- Edge P2-P3 (215 Place) = 100.0 ft (source: recorded outline, return 1 Task 1(a))

Law relied on:

- none cited

Why the rule applies: Frontage is the length of each lot line that lies along a street, measured from the recorded outline.

Expected value: Northern Boulevard 103.9 ft; 215 Place 100.0 ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(a): 'Northern Boulevard = 103.9 ft (edge P1->P2); cross street 215 Place = 100.0 ft (edge P2->P3)'.

What this row does not establish: Measured from the approximate tax-map outline. The city property record lists a lot front of 100.76 ft, which differs; neither is a survey.

### L11 - Street widths

Facts used:

- Northern Boulevard mapped width = 100 ft (source: DCM centerline OBJECTID 53832, Streetwidth)
- 215 Place mapped width = 60 ft (source: DCM centerline OBJECTID 11453, Streetwidth)

Law relied on:

- ZR 12-10 (Definitions) - captured.
  - Capture: snapshot `zr-12-10`, file `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`.
  - Content digest: `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A 'wide street' is any street 75 feet or more in width"
- ZR 12-10 (Definitions) - captured.
  - Capture: snapshot `zr-12-10`, file `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`.
  - Content digest: `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A 'narrow street' is any street less than 75 feet wide"

Why the rule applies: ZR 12-10 defines a wide street as 75 feet or more and a narrow street as less than 75 feet. Northern Boulevard's mapped width is 100 feet (wide) and 215 Place's is 60 feet (narrow). The R6B rows of the floor-area and height tables carry no footnote, so wide versus narrow does not change the R6B floor area or height.

Expected value: Northern Boulevard is a wide street (100 ft); 215 Place is a narrow street (60 ft); this does not change the R6B floor area or height

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(b): 'Northern Boulevard mapped Streetwidth = 100 -> WIDE. Cross street mapped Streetwidth = 60 -> NARROW.'

What this row does not establish: The mapped width is the City Map width as served (a free-text field). Wide versus narrow changes only the ZR 23-433 setback depth (row L13), not the R6B floor area, base height or building height.

### L12 - Rear yard

Facts used:

- Angle of the two street lines = 89.7 degrees (source: return 1 Task 1(b))
- Farthest point from the corner point = 144.60 ft (source: return 2 Q1(c): part of the lot lies beyond 100 ft of the corner point)

Law relied on:

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

Why the rule applies: ZR 23-344(a) requires no rear yard within 100 feet of the point where two street lines meet at 135 degrees or less (here 89.7 degrees); that waiver covers only the area within 100 feet of the corner point. ZR 23-342 requires a rear yard only on the interior-lot portion, and part of this lot lies beyond 100 feet of the corner, so what is required there is not settled by the captured text.

Expected value: not known. Within 100 feet of the corner point no rear yard is required (ZR 23-344(a)); but the far corner of the lot is 144.60 feet from the corner point, so part of the lot lies beyond that 100-foot reach, and whether a rear yard is required there is not settled. ZR 23-342 is now captured, but the depth it sets depends on the building type and lot width (not given); the first and step-P1 readers did not have the ZR 12-10 side- and rear-lot-line definitions, and both step-P1 readings read it the same way (no rear yard within 100 feet of the corner; beyond, not known). Those definitions were since captured (task M4-T029) and read in step P3 (cases/step-p3-worked.json), where both step-P3 readings again read the beyond-100-foot rear yard as not known (it needs the adjoining lot-line type and the building type, height and lot width, and the overlay yard rule ZR 34-23 was not available).

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(f), and return-independent-hand-calculation-2.md, Q1(c); confirmed by both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q3a).

What this row does not establish: It gives no rear-yard requirement for the part of the lot beyond 100 feet of the corner; that needs neighbouring lot-line data, the building type and lot width, and the ZR 12-10 lot-line definitions the earlier readers did not have (now captured and read in cases/step-p3-worked.json).

### L13 - Setback above the base

Facts used:

- Northern Boulevard = wide street (source: row L11)
- 215 Place = narrow street (source: row L11)

Law relied on:

- ZR 23-433 (Standard setback regulations) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any street wall fronting on a wide street, and a setback with a depth of at least 15 feet shall be provided from any street wall fronting on a narrow street"

Why the rule applies: ZR 23-433 requires, between the minimum and maximum base heights, a setback of at least 10 feet from a street wall on a wide street and at least 15 feet on a narrow street. Northern Boulevard is wide and 215 Place is narrow.

Expected value: 10 ft on the wide street (Northern Boulevard); 15 ft on the narrow street (215 Place)

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(d): '>=10 ft deep from any street wall on a WIDE street (Northern Blvd) and >=15 ft deep from any street wall on a NARROW street (215 Place)'.

What this row does not establish: The setback is not modelled on the lot here. Its depth may be reduced by one foot for each foot the street wall sits behind the street line, but not below seven feet (ZR 23-433(a)), and is optional under ZR 23-433(c).

### L14 - Ordinary rear-yard depth

Facts used:

- Governing section = ZR 23-342 (now captured, task M4-T025) (source: docs/research/zr-snapshots/v1/zr-23-342.snapshot.json)

Law relied on:

- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "shall be provided on #interior lots# in accordance with this Section"
- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "for #zoning lots# with a #lot width# of less than 40 feet, a #rear yard# with a depth of not less than 30 feet"

Why the rule applies: The ordinary rear-yard depth for an interior lot is set by ZR 23-342 (now captured); it is not less than 20 feet or not less than 30 feet depending on the building type (detached or zero-lot-line, or semi-detached or attached) and the lot width (less than 40 feet, or 40 feet or greater).

Expected value: not known. ZR 23-342 is now captured, but the ordinary rear-yard depth it sets depends on the building type and the lot width, which are not given for this lot, so the depth is not known. Both step-P1 readings read the captured ZR 23-342 the same way (20 or 30 feet depending on building type and lot width, not given).

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 1(f) and Task 3 item 4: 'ZR 23-342 is NOT in the packet; baseline depth NOT KNOWN from captured text'; with ZR 23-342 now captured, both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q3) read the depth as 20 or 30 feet depending on building type and lot width, not given.

What this row does not establish: It gives no rear-yard depth for this lot; the captured ZR 23-342 sets 20 or 30 feet by building type and lot width, which are not given.

### L15 - Building option, floor plates, floors

Facts used:

- Independent worked example = none (source: no building option was worked by hand)

Law relied on:

- none cited

Why the rule applies: A building option, its floor plates and its floor stack need a settled footprint; coverage (row L5), the rear yard (row L12) and the setback (row L13) are not settled here, and there is no independent worked example for a building option.

Expected value: not known. There is no independent worked example for a building option, and it would need a settled footprint, which depends on coverage (row L5), the rear yard (row L12) and the setback (row L13), none of them settled here.

Where this stands in the independent reading: Work order table A, row L15: 'Building option, floor plates, floors -> no independent example -> none'.

What this row does not establish: It gives no floor-plate area, floor count or building massing.

## What this case does not establish

- It does not read the C2-2 commercial overlay; every residential figure here is the residential reading only. The overlay is read independently in cases/overlay-reading.json, where both step-P2 readings find it changes only the street-wall location rule and leaves the floor area ratio, lot coverage, dwelling units, base and building heights, the setback and the all-residential rear yard the same as plain R6B; no value in this case changes.
- It does not prove the zoning lot; it is a tax-lot-only reading.
- It does not settle lot coverage, the rear yard beyond the corner area, the ordinary rear-yard depth, or any building massing.
- It is not a professional or legal determination and does not say the lot complies with anything.

## Sources

- The independent hand-calculation, first round: provenance/return-independent-hand-calculation-1.md
- The independent hand-calculation, follow-up (tables C and D): provenance/return-independent-hand-calculation-2.md
- The two step-P1 readings that confirm the corner, coverage and rear-yard rows from the newly captured text: provenance/return-independent-hand-calculation-3.md and provenance/return-independent-hand-calculation-4.md.
- The sealed folder given to the helper: the pinned ZR captures (without the notes describing how the program encoded them) and the lot's recorded official facts, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-06 | Case created from the independent hand-calculation returns (step R0). | rules-engineer (M4-T024) |
| 2026-10-06 | Row L7 (maximum dwelling units, qualifying affordable housing) changed from not known to 35, a value that holds only if the housing qualifies, as rows L2 and L4 are (24,180 / 680 = 35.56, a fraction below three-quarters dropped, so 35). Reason: a corrected reading. The helper's return (Task 1(g)) and the work order's independent value both give 35; the 'not known' sits in the program's first-screen column, which these cases do not copy. Ruled by an independent reviewer (project-control/reports/M4-T024-L7-ruling.md). | rules-engineer (M4-T024) |
| 2026-10-07 | Row L9 (lot type): expected value unchanged (corner). The ZR 12-10 corner-lot definition is now captured (task M4-T025), so the citation changes from not-captured to the captured snapshot zr-12-10-lot-corner, and both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q1a) independently confirm the corner classification. Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | Row L5 (maximum lot coverage): expected value unchanged (not known as a single whole-lot figure). The ZR 12-10 corner-lot-portion definition is now captured (task M4-T025); the citation changes from not-captured to the captured snapshot zr-12-10-lot-corner, and the reason now records that both step-P1 readings read the lot as a corner-lot portion (100 percent) plus a remaining interior-lot portion (80 percent), with no single whole-lot figure. Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | Row L12 (rear yard): expected value unchanged (not known). ZR 23-342 is now captured (task M4-T025); a captured ZR 23-342 citation is added and the reason records that both step-P1 readings read no rear yard within 100 feet of the corner (ZR 23-344(a)) and the beyond-100-feet outcome and its depth as not known. Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | Row L14 (ordinary rear-yard depth): expected value unchanged (not known). ZR 23-342 is now captured (task M4-T025), so the citation changes from not-captured to the captured snapshot zr-23-342; the reason now records that the depth ZR 23-342 sets depends on the building type and lot width, which are not given, so the depth for this lot is still not known. Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | No expected value changed. The C2-2 overlay has now been read independently in step P2 (task M4-T028, cases/overlay-reading.json); the first 'does not establish' item is extended to point to that reading, which finds the overlay changes only the street-wall location rule and leaves the floor area ratio, lot coverage, dwelling units, base and building heights, the setback and the all-residential rear yard the same as plain R6B. Both step-P2 readings support this. No row value changes; in particular row L5 (lot coverage) stays not known for its per-portion reason. Reason: a corrected reading (the overlay reading now exists). | rules-engineer (M4-T028) |
| 2026-10-07 | Row L12 (rear yard): expected value unchanged (not known beyond the corner). The ZR 12-10 side- and rear-lot-line definitions were captured by task M4-T029 and read independently in step P3 (cases/step-p3-worked.json); the row's wording is brought from 'not captured' into 'the readers did not have' form and records that both step-P3 readings again read the beyond-100-foot rear yard as not known. Row L5 (lot coverage) is unchanged and stays not known for its per-portion reason - the step-P3 readings' passing remark that the standard coverage for this corner lot is 100 percent did not work the corner-lot-portion rule and is not a reading of whole-lot coverage. Row L14 (ordinary rear-yard depth) is unchanged and stays not known (it carries no 'not captured' wording; the step-P3 readings also find the real lot's lot width itself not known). Reason: corrected evidence - the text is now captured and read. | rules-engineer (M4-T030) |

