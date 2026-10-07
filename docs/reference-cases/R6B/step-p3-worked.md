# Worked from the step-P3 captures: lot lines, rear yards, ZR 23-436, ZR 34-21, special density areas, the base plane, eligible sites and "residence, or residential"

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: section 8 (capture the missing law text, then read it independently); backlog row DB-170 item (a).

The R6B reference-case readings that waited for the law text captured by task M4-T029 (27 texts), now read independently in step P3: the ZR 12-10 lot-line, lot-width and lot-depth definitions applied to the real lot and a made-up interior lot; the rear yard beyond the corner of the real lot and a made-up corner lot, the interior lot under ZR 23-342 and the through lot under the rear-yard equivalent of ZR 23-343; ZR 23-436 and ZR 35-633 for the real lot; ZR 34-21 and ZR 34-111 versus ZR 34-112; the Manhattan Core and the Special Downtown Brooklyn District; from what level heights are measured and the base plane; ZR 23-434 and the different maximum of ZR 23-362(b); the definition of "residence, or residential"; and the base of the floor-area shares in ZR 23-231 and ZR 23-232. A value or a yes/no is recorded only where both readings give it on the same basis; otherwise the row is not known with both readings named. Every value comes from the two independent readings and the law text, never from a program run.

## What this case is worth

Prepared by one AI helper and read again, independently, by a second AI, each working alone from the sealed step-P3 folder; their agreement alone is not proof. It is a draft reading of the law, not professionally reviewed, and is not a statement that anything complies. The real lot is 215-16 Northern Boulevard in Queens; the interior, through and corner lots are made up, chosen to show the lot-line, rear-yard and rear-yard-equivalent readings. Where the two readings differ, or one holds an answer subject to a text they did not have, the row says so and names both readings.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of the step-P3 law-text captures (without their notes), the real lot's recorded official facts and outline, and three made-up lots, with no access to the program (reading 1: provenance/return-independent-hand-calculation-7.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-8.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| District (made-up lots) | R6B, no overlay | the examples' stated district |
| Real lot | 215-16 Northern Boulevard, Queens (QN, borough code 4), BBL 4073340070 | NYC PLUTO row for BBL 4073340070 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Street widths | Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) | NYC DCM street centerlines; cases/real-lot.json row L11 |
| Made-up interior lot | 40 ft on the street by 100 ft deep, R6B | the readings' made-up interior lot |
| Made-up through lot | 40 ft wide by 200 ft deep between two opposite streets, R6B | the readings' made-up through lot |
| Made-up corner lot | 150 ft on street A by 100 ft on street B, R6B | the readings' made-up corner lot |
| Real lot special-district fields | none recorded (spdist1, spdist2, spdist3 absent from the served row) | NYC PLUTO row for BBL 4073340070, as served |

## Rows

### real-lot-lot-lines - The real lot's lot lines: which are front, which side, and whether there is a rear lot line

Facts used:

- Lot outline = five vertices in EPSG:2263 US survey feet (source: recorded MapPLUTO polygon for BBL 4073340070)
- Street frontages = Northern Boulevard and 215 Place (source: the recorded outline and DCM centerlines)
- Interior angle where the two street lines meet = about 89.7 degrees (source: both readings, from the outline (return-independent-hand-calculation-7.md Q1a; return-independent-hand-calculation-8.md Q1a))

Law relied on:

- ZR 12-10 (Definitions (front lot line)) - captured.
  - Capture: snapshot `zr-12-10-lot-line-front`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-line-front.snapshot.json`.
  - Content digest: `6bd9212cbb4ffb4671c692c92f6b265a1ab60e114778925048bc66b3a6cdbbbc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "front lot line" is a #street line#"
- ZR 12-10 (Definitions (street line)) - captured.
  - Capture: snapshot `zr-12-10-street-line`, file `docs/research/zr-snapshots/v1/zr-12-10-street-line.snapshot.json`.
  - Content digest: `20495a0325bef1576623272bd4c4628ce994edf9decd7da3214a7f3708b65a5f`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "street line" is a #lot line# separating a #street# from other land"
- ZR 12-10 (Definitions (rear lot line)) - captured.
  - Capture: snapshot `zr-12-10-lot-line-rear`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-line-rear.snapshot.json`.
  - Content digest: `d34da91dcfa8392e655806a06204621c80175de99a034d983b978cb73e45c86b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "rear lot line" is any #lot line# of a #zoning lot# except a #front lot line#, which is parallel or within 45 degrees of being parallel to, and does not intersect, any #street line# bounding such #zoning lot#"
- ZR 12-10 (Definitions (side lot line)) - captured.
  - Capture: snapshot `zr-12-10-lot-line-side`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-line-side.snapshot.json`.
  - Content digest: `5ba11f6adfc47e15f68c20ca93e4dc5e053458725796eb74c8deb0ced8c67221`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "side lot line" is any #lot line# which is not a #front lot line# or a #rear lot line#"

Why the rule applies: The lot adjoins the intersection of Northern Boulevard and 215 Place (a corner lot). Each lot line on a street is a front lot line (ZR 12-10 front lot line and street line). A rear lot line must be parallel-or-within-45-degrees and must not intersect any street line bounding the lot; each of the two interior edges meets one of the two street lines at its outer end, so neither is a rear lot line, and each, being neither front nor rear, is a side lot line.

Expected value: corner lot with two front lot lines (the Northern Boulevard edge and the 215 Place edge), two side lot lines (the two interior edges), and no rear lot line

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q1a (two front lot lines, two side lot lines, no rear lot line) and return-independent-hand-calculation-8.md Q1a (same); both readings classify the lines the same way on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: Both readings flag that the captured text does not define "intersect": if a shared endpoint did not count as intersecting, an interior edge could be argued to be a rear lot line. On the natural reading (endpoint contact is intersecting) both reach no rear lot line. It uses the approximate tax-map outline, not a survey.

### real-lot-lot-depth - The real lot's lot depth

Facts used:

- Northern Boulevard front to its opposite side lot line = about 99.98 ft (mean) (source: both readings, from the outline (return-independent-hand-calculation-7.md Q1b; return-independent-hand-calculation-8.md Q1b))
- 215 Place front to its opposite side lot line = about 103.90 ft (mean) (source: both readings, from the outline (return-independent-hand-calculation-7.md Q1b; return-independent-hand-calculation-8.md Q1b))

Law relied on:

- ZR 12-10 (Definitions (lot depth)) - captured.
  - Capture: snapshot `zr-12-10-lot-depth`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-depth.snapshot.json`.
  - Content digest: `442b1fbe2814c50a6c5142ccaf08d9293f52bbd63390170178c2b0b91fb6d711`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "In the case of a #corner lot#, the #lot depth# is the greater of the mean horizontal distances between the #front lot lines# and the respective #side lot line# opposite each"

Why the rule applies: ZR 12-10 sets a corner lot's lot depth as the greater of the two mean horizontal distances between each front lot line and its opposite side lot line. The Northern Boulevard front to its opposite side is about 99.98 feet and the 215 Place front to its opposite side is about 103.90 feet; the greater is about 103.90 feet.

Expected value: about 103.9 feet (the corner-lot method: the greater of the two front-to-opposite-side mean distances, about 99.98 feet and about 103.90 feet)

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q1b (greater of 99.98 and 103.90 = 103.9 ft) and return-independent-hand-calculation-8.md Q1b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: Measured from the approximate tax-map outline, not a survey. The city record lists a tabular lot depth of 100.0 feet, which differs; the corner-lot method gives a single number only, not a depth per frontage.

### real-lot-lot-width - The real lot's lot width

Facts used:

- The two side lot lines = adjacent and about perpendicular (they meet at about 89.7 degrees), not opposite or parallel (source: both readings, from the outline (return-independent-hand-calculation-7.md Q1b; return-independent-hand-calculation-8.md Q1b))

Law relied on:

- ZR 12-10 (Definitions (lot width)) - captured.
  - Capture: snapshot `zr-12-10-lot-width`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-width.snapshot.json`.
  - Content digest: `35e17792ba3b7333edde3cc195c7f5fa4851398404b104c4c3cd766092c10f25`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: ""Lot width" is the mean horizontal distance between the #side lot lines# of a #zoning lot#"

Why the rule applies: ZR 12-10 sets lot width as the mean horizontal distance between the side lot lines. On this corner lot the two side lot lines are adjacent and about perpendicular, not two opposite lines, so the "mean horizontal distance between" them is not defined by the captured words.

Expected value: not known. The two side lot lines of this corner lot are adjacent and about perpendicular, not opposite or parallel, and the captured ZR 12-10 lot-width definition gives no method for a lot whose side lot lines are not opposite one another, so the lot width is not known. Both readings reach this same not-known result (return-independent-hand-calculation-7.md Q1b and return-independent-hand-calculation-8.md Q1b).

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q1b (lot width not known for a two-frontage corner lot) and return-independent-hand-calculation-8.md Q1b (same); both reach this not-known result on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It gives no lot width. The PLUTO "lotfront" of 100.76 feet is a frontage field, not the ZR lot width.

### interior-40x100-lot-dimensions - The made-up interior lot (40 ft by 100 ft): lot width and lot depth

Facts used:

- Lot = a made-up interior lot, 40 ft on the street by 100 ft deep (source: the readings' made-up interior lot)

Law relied on:

- ZR 12-10 (Definitions (front lot line)) - captured.
  - Capture: snapshot `zr-12-10-lot-line-front`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-line-front.snapshot.json`.
  - Content digest: `6bd9212cbb4ffb4671c692c92f6b265a1ab60e114778925048bc66b3a6cdbbbc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "front lot line" is a #street line#"
- ZR 12-10 (Definitions (lot width)) - captured.
  - Capture: snapshot `zr-12-10-lot-width`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-width.snapshot.json`.
  - Content digest: `35e17792ba3b7333edde3cc195c7f5fa4851398404b104c4c3cd766092c10f25`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: ""Lot width" is the mean horizontal distance between the #side lot lines# of a #zoning lot#"
- ZR 12-10 (Definitions (lot depth)) - captured.
  - Capture: snapshot `zr-12-10-lot-depth`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-depth.snapshot.json`.
  - Content digest: `442b1fbe2814c50a6c5142ccaf08d9293f52bbd63390170178c2b0b91fb6d711`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: ""Lot depth" is the mean horizontal distance between the #front lot line# and #rear lot line# of a #zoning lot#"

Why the rule applies: For a one-street interior lot, the 40-foot street edge is the front lot line (ZR 12-10 front lot line); the opposite 40-foot edge is parallel and touches no street line, so it is the rear lot line; the two 100-foot edges are side lot lines. Lot width is the mean distance between the side lot lines (40 feet) and lot depth is the mean distance between the front and rear lot lines (100 feet).

Expected value: lot width 40 feet; lot depth 100 feet (front lot line = the 40-foot street edge; rear lot line = the opposite 40-foot edge; side lot lines = the two 100-foot edges)

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q1c (width 40 ft, depth 100 ft) and return-independent-hand-calculation-8.md Q1c (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: A made-up lot, not a real property. It assumes the stated 40-by-100 dimensions with one street on the 40-foot side.

### interior-40x100-rear-yard - The made-up interior lot (40 ft by 100 ft): rear yard

Facts used:

- Lot width = 40 feet (source: the made-up interior lot (row interior-40x100-lot-dimensions))
- Lot depth = 100 feet (not less than 95 feet, so not a shallow lot) (source: the made-up interior lot)

Law relied on:

- ZR 23-342 (Rear yard requirements (detached and zero lot line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#"
- ZR 23-342 (Rear yard requirements (semi-detached and attached buildings, 40 feet or greater)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "for #zoning lots# with a #lot width# of 40 feet or greater, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided."

Why the rule applies: ZR 23-342 sets the interior-lot rear yard by building type and lot width. At a lot width of 40 feet the semi-detached or attached branch is the 40-feet-or-greater case, which gives the same depth as the detached or zero-lot-line branch; the less-than-40-feet (30-foot) branch does not apply. The lot is 100 feet deep, not less than 95 feet, so the shallow-lot reduction does not apply.

Expected value: a rear yard of not less than 20 feet for the building or portions at or below 75 feet, and 30 feet above 75 feet; at a lot width of 40 feet this is the same for a detached or zero-lot-line building and for a semi-detached or attached building, and the shallow-lot reduction does not apply (depth 100 feet is not less than 95 feet)

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q2b (20 ft at or below 75 ft, 30 ft above, for both building-type branches at width 40) and return-independent-hand-calculation-8.md Q2b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: A made-up lot, not a real property. Which depth applies depends on the building height relative to 75 feet, a design choice; the 20-versus-30-foot distinction between building types is immaterial only because the lot width is exactly 40 feet.

### through-40x200-rear-yard-equivalent - The made-up through lot (40 ft wide, 200 ft between the two streets): rear yard equivalent, depth and location

Facts used:

- Lot = a made-up through lot, 40 ft wide by 200 ft deep between two opposite streets (source: the readings' made-up through lot)
- Maximum depth = 200 feet (not less than 110 feet, and 190 feet or more, so a standard lot) (source: the made-up through lot)

Law relied on:

- ZR 23-343 (Rear yard equivalent requirements (exception for short through lots)) - captured.
  - Capture: snapshot `zr-23-343`, file `docs/research/zr-snapshots/v1/zr-23-343.snapshot.json`.
  - Content digest: `b4440929d887fa5eba92db8ad881bdf84b04d3283b988026ab58ff6865221680`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-343.
  - Quoted: "to any #through lots# that extend less than 110 feet in maximum depth from #street# to #street#"
- ZR 23-343 (Rear yard equivalent requirements (depth, standard lots)) - captured.
  - Capture: snapshot `zr-23-343`, file `docs/research/zr-snapshots/v1/zr-23-343.snapshot.json`.
  - Content digest: `b4440929d887fa5eba92db8ad881bdf84b04d3283b988026ab58ff6865221680`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-343.
  - Quoted: "On any #through lot# that is 190 feet or more in maximum depth from #street# to #street#, for #buildings# or portions thereof at or below a height of 75 feet, a #rear yard equivalent# consisting of an open area with a minimum depth of 40 feet shall be provided, and above a height of 75 feet, where permitted, a #rear yard equivalent# of 60 feet shall be provided."
- ZR 23-343 (Rear yard equivalent requirements (standard location)) - captured.
  - Capture: snapshot `zr-23-343`, file `docs/research/zr-snapshots/v1/zr-23-343.snapshot.json`.
  - Content digest: `b4440929d887fa5eba92db8ad881bdf84b04d3283b988026ab58ff6865221680`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-343.
  - Quoted: "A #rear yard equivalent# shall be provided midway, or within 10 feet of being midway, between the two #street lines# upon which such #through lot# fronts."

Why the rule applies: ZR 23-343 governs the through-lot rear yard equivalent. The lot is 200 feet deep: it is not exempt (the exemption is for through lots under 110 feet), and 190 feet or more makes it a standard lot (no shallow-lot reduction). For a standard through lot the rear yard equivalent is an open area with a minimum depth of 40 feet at or below 75 feet and 60 feet above 75 feet, located midway, or within 10 feet of midway, between the two street lines.

Expected value: a rear yard equivalent (open area) with a minimum depth of 40 feet for parts at or below 75 feet and 60 feet above 75 feet, located midway, or within 10 feet of being midway, between the two street lines; the lot is not exempt (not under 110 feet) and is a standard lot (190 feet or more, so no shallow-lot reduction), and the alternative locations of ZR 23-343(c)(2) are not available to a plain R6B lot

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q2c (40 ft at or below 75 ft, 60 ft above, midway within 10 ft; not exempt, standard lot) and return-independent-hand-calculation-8.md Q2c (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: A made-up lot, not a real property. Which depth applies depends on the building height relative to 75 feet. Both readings note they could not test the "large sites" and block-occupying exemptions of ZR 23-343(a) because "large sites" is a defined term they did not have and the block-frontage facts are not given.

### real-lot-rear-yard-beyond-corner - The real lot's rear yard beyond the corner

Facts used:

- Farthest point from the corner point = about 144.6 ft (source: both readings, from the outline (return-independent-hand-calculation-7.md Q2a; return-independent-hand-calculation-8.md Q2a))
- Side lot line reach beyond 100 ft of the 215 Place street line = a small portion (about the far few feet near the inner corner) (source: both readings (return-independent-hand-calculation-7.md Q2a; return-independent-hand-calculation-8.md Q2a))

Law relied on:

- ZR 23-344 (Additional rear yard modifications (within 100 feet of corners)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less"
- ZR 23-344 (Additional rear yard modifications (beyond 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply along such #rear lot line#"
- ZR 23-344 (Additional rear yard modifications (R6 through R12, side-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#"
- ZR 23-344 (Additional rear yard modifications (rear-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "a #rear yard# shall be provided in accordance with Section 23-342 (Rear yard requirements), where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#"

Why the rule applies: ZR 23-344(a) requires no rear yard within 100 feet of the corner point (the street lines meet at about 89.7 degrees, 135 or less), which covers most of the lot. Beyond that, ZR 23-344(c) treats the portion of a side lot line beyond 100 feet of the street line it intersects as a rear lot line; both readings find only a small portion beyond 100 feet of the 215 Place street line. Along such a deemed rear lot line, in R6 through R12 districts, no rear yard is required where it coincides with a neighbour's side lot line, but one (per ZR 23-342) is required where it coincides with a neighbour's rear lot line.

Expected value: not known. Within 100 feet of the corner point no rear yard is required. Beyond that, a small portion of a side lot line beyond 100 feet of the 215 Place street line is deemed a rear lot line, and whether a rear yard is required there is not settled: it needs the adjoining zoning lot's lot-line type (ZR 23-344(c)(1) versus (c)(3)), and for any depth the building type and height and the lot width (itself not known); the overlay yard rule ZR 34-23 was not available either. Both readings reach this same not-known result (return-independent-hand-calculation-7.md Q2a and return-independent-hand-calculation-8.md Q2a).

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q2a (no rear yard within 100 ft of the corner; beyond, not known) and return-independent-hand-calculation-8.md Q2a (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It gives no rear-yard requirement beyond the corner. It needs the neighbouring lot-line type, the building type and height, and (for the overlay) ZR 34-23, none of which the readers had; it uses the approximate tax-map outline.

### corner-150x100-rear-yard-beyond-corner - The made-up corner lot (150 ft on street A by 100 ft on street B): rear yard beyond the corner

Facts used:

- Lot = a made-up corner rectangle, 150 ft on street A by 100 ft on street B, street lines meeting at a right angle (source: the readings' made-up corner lot)
- Portion beyond 100 feet of street B's line = a 50-foot stretch of the far (150-foot) side lot line (source: both readings (return-independent-hand-calculation-7.md Q2d; return-independent-hand-calculation-8.md Q2d))

Law relied on:

- ZR 23-344 (Additional rear yard modifications (within 100 feet of corners)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less"
- ZR 23-344 (Additional rear yard modifications (beyond 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply along such #rear lot line#"
- ZR 23-344 (Additional rear yard modifications (R6 through R12, side-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#"

Why the rule applies: ZR 23-344(a) waives the rear yard within 100 feet of the corner point (the streets meet at a right angle, 135 or less). Beyond that, ZR 23-344(c) treats the portion of a side lot line beyond 100 feet of the street line it intersects as a rear lot line; both readings find the far (150-foot) side lot line has a 50-foot stretch (from 100 to 150 feet) beyond 100 feet of street B's line. Along it, whether a rear yard is required turns on the adjoining lot's lot-line type.

Expected value: not known. Within 100 feet of the corner point no rear yard is required. Beyond that, the 50-foot stretch of the far side lot line (from 100 to 150 feet of street B's line) is a deemed rear lot line, and whether a rear yard is required there is not settled: it needs the adjoining zoning lot's lot-line type (ZR 23-344(c)(1) versus (c)(3)), and for any depth (20 or 30 feet per ZR 23-342) the building type, height and lot width. Both readings reach this same not-known result (return-independent-hand-calculation-7.md Q2d and return-independent-hand-calculation-8.md Q2d).

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q2d (no rear yard within 100 ft of the corner; beyond, a 50-ft deemed rear lot line, not known) and return-independent-hand-calculation-8.md Q2d (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: A made-up lot, not a real property. It gives no rear-yard requirement beyond the corner; that needs the neighbouring lot-line type, the building type, height and lot width.

### zr-23-436-paragraphs - Which paragraphs of ZR 23-436 bind a new all-residential building on the real lot

Facts used:

- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Street widths = Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) (source: NYC DCM street centerlines; cases/real-lot.json row L11)
- Building = a new all-residential building (source: the subject of both readings)

Law relied on:

- ZR 23-436 (Additional height and setback provisions (scope)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "In the districts indicated, the following additional regulations shall apply"
- ZR 23-436 (Additional height and setback provisions (a) existing buildings) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "Existing buildings may be vertically #enlarged# by up to one story or 15 feet without regard to the #street wall# location requirements of Section 23-431."
- ZR 23-436 (Additional height and setback provisions (b) through lots) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "On #through lots# which extend less than 190 feet in maximum depth from #street# to #street#, the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage."
- ZR 23-436 (Additional height and setback provisions (c) corner lots) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "On #corner lots#, or portions thereof, the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one of the #street# frontages bounding the #corner lot# is a #wide street# and the other a #narrow street#, the #street wall# location rules shall be applied along the #wide street# frontage"
- ZR 34-24 (Modification of Height and Setback Regulations (R6 through R12 equivalency)) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied"
- ZR 12-10 (Definitions (wide street)) - captured.
  - Capture: snapshot `zr-12-10`, file `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`.
  - Content digest: `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A 'wide street' is any street 75 feet or more in width"
- ZR 12-10 (Definitions (narrow street)) - captured.
  - Capture: snapshot `zr-12-10`, file `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`.
  - Content digest: `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A 'narrow street' is any street less than 75 feet wide"

Why the rule applies: For a residential building in the C2-2 overlay, ZR 34-24(b)(1) applies the ZR 35-63 modifications, which bring in ZR 23-436 (via ZR 35-633, with the ZR 23-431 reference read as ZR 35-631). Reading ZR 23-436 paragraph by paragraph for a new all-residential building on this corner lot: (a) is for existing buildings vertically enlarged (not this building); (b) is for through lots (this is a corner lot); (c) is for corner lots and binds; (d) is for lots keeping existing street walls unaltered (nothing is kept). Northern Boulevard is a wide street (100 feet) and 215 Place a narrow street (60 feet), so under (c) the street-wall location is mandatory along the wide Northern Boulevard frontage.

Expected value: of ZR 23-436's paragraphs only (c) binds a new all-residential building on this corner lot: the street-wall location is mandatory along one frontage, and because Northern Boulevard is wide and 215 Place narrow, along the wide Northern Boulevard frontage (read as ZR 35-631 per ZR 35-633(a)); (a) does not apply (it is for existing buildings vertically enlarged), (b) does not apply (it is for through lots), and (d) does not apply (no existing street wall is kept unaltered); (e), (f) and (g) depend on facts the readers did not have or on design choices

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q3b (only (c) binds; (a),(b),(d) do not apply; (e),(f),(g) conditional or not known) and return-independent-hand-calculation-8.md Q3b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: Paragraph (e) depends on the chosen building height against the minimum base height (30 feet), (f) on whether the lot is in a Landmarks Preservation Commission Historic District (a fact the readers did not have), and (g) on whether a continuous sidewalk widening is provided (a design choice); none is settled. The underlying height and setback numbers come from ZR 35-632 and ZR 23-432, not from ZR 23-436.

### zr-35-633-paragraphs - ZR 35-633 paragraphs (a) and (b) for the real lot

Facts used:

- Lot type = corner (two street frontages) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Commercial-overlay block-frontage extent = not recorded (source: the C2-2 overlay record does not establish block-frontage coverage)

Law relied on:

- ZR 35-633 (Additional height and setback provisions (scope)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows:"
- ZR 35-633 (Additional height and setback provisions (a)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and"
- ZR 35-633 (Additional height and setback provisions (b)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage."

Why the rule applies: ZR 35-633 brings in ZR 23-436 with two exceptions. Paragraph (a) supersedes any reference to ZR 23-431's street-wall location with ZR 35-631, so on the real lot the street-wall location (ZR 23-436(c)) is read as ZR 35-631. Paragraph (b) is a corner-lot clause for a zoning lot bounded by only one street line along a frontage where a Commercial District is mapped along the entire block frontage; whether that condition holds here is not in the record.

Expected value: ZR 35-633(a) applies: references to ZR 23-431's street-wall location are superseded by ZR 35-631. ZR 35-633(b)'s corner-lot one-frontage clause is not known on the recorded facts, because whether a Commercial District is mapped along the entire block frontage (and which frontage is bounded by only one street line) is not in the record - both readings

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q3c ((a) applies; (b) not known, block-frontage extent not in the folder) and return-independent-hand-calculation-8.md Q3c ((a) applies; (b) not known, entire-block-frontage coverage and single-street-line condition not in the folder); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It gives no additional height or setback number; the ZR 35-633(b) corner-lot clause cannot be applied without the overlay's block-frontage extent, which the readers did not have.

### zr-34-21-routing - What ZR 34-21 does, and what stays open without ZR 34-22 and ZR 34-23

Facts used:

- District and overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Building = a residential building (source: the subject of both readings)

Law relied on:

- ZR 34-21 (General Provisions) - captured.
  - Capture: snapshot `zr-34-21`, file `docs/research/zr-snapshots/v1/zr-34-21.snapshot.json`.
  - Content digest: `6da11080e5d4012f0f9e771595e3e9434a8cafc6fdd5aa02f517d33d929e09b8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-21.
  - Quoted: "the #bulk# regulations applicable to #residential buildings# as set forth in Section 34-11 (General Provisions) are modified by the provisions of Sections 34-22 (Modification of Floor Area Regulations), 34-23 (Modification of Yard Regulations) and 34-24 (Modification of Height and Setback Regulations). The purpose of these modifications is to make the regulations set forth in Article II, Chapter 3, applicable to #Commercial Districts#."
- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"

Why the rule applies: By its own words ZR 34-21 modifies nothing directly; it is a routing provision that names ZR 34-22 (floor area), ZR 34-23 (yards) and ZR 34-24 (height and setback) as the sections that carry any modification, and it does not name the dwelling-unit rule. Of those three, only ZR 34-24 was available to the readers.

Expected value: ZR 34-21 itself modifies nothing; it routes the residential-building bulk to ZR 34-22 (floor area), ZR 34-23 (yards) and ZR 34-24 (height and setback), and does not name the dwelling-unit rule. The readers did not have ZR 34-22 or ZR 34-23, so how the overlay modifies the floor area (and any lot coverage) and the yards stays open (not settled); ZR 34-21 does not itself change the dwelling-unit rule

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q4a/Q4b (34-21 routes to 34-22/34-23/34-24, changes nothing itself; 34-22 and 34-23 not had, so floor area and yards stay not known) and return-independent-hand-calculation-8.md Q4a/Q4b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: The readers did not have ZR 34-22 or ZR 34-23, so the floor-area and yard modifications for the overlay cannot be read; this leaves the overlay's effect on the rear yard (cases/real-lot.json row L12) and on floor area conditional.

### zr-34-111-governs - Whether ZR 34-112 or ZR 34-111 governs a C2-2 district mapped within R6B

Facts used:

- Overlay and surrounding district = C2-2 overlay mapped within R6B (source: NYC PLUTO row for BBL 4073340070, fields overlay1 and zonedist1)

Law relied on:

- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District (district line)) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5"
- ZR 34-111 (Residential bulk regulations in C1 or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "In the districts indicated, the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 34-112 (Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6 Districts (district line)) - captured.
  - Capture: snapshot `zr-34-112`, file `docs/research/zr-snapshots/v1/zr-34-112.snapshot.json`.
  - Content digest: `19e8c488831398c112a19306b72f6112454cf42ec184cc05f2f1235dc36c857f`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-112.
  - Quoted: "C1-6 C1-7 C1-8 C1-9 C2-6 C2-7 C2-8 C3 C4 C5 C6"
- ZR 34-112 (Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6 Districts) - captured.
  - Capture: snapshot `zr-34-112`, file `docs/research/zr-snapshots/v1/zr-34-112.snapshot.json`.
  - Content digest: `19e8c488831398c112a19306b72f6112454cf42ec184cc05f2f1235dc36c857f`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-112.
  - Quoted: "In the districts indicated, the applicable #bulk# regulations are the #bulk# regulations for the #residential equivalent# of the #Commercial District# as set forth in the following table"

Why the rule applies: C2-2 appears in ZR 34-111's district line and not in ZR 34-112's. So for a C2-2 overlay mapped within R6B, ZR 34-111 governs and applies the bulk regulations of the surrounding Residence District (R6B); ZR 34-112's residential-equivalent table does not reach C2-2. ZR 34-111's exceptions (a) and (b) are limited to R1 through R5 and to R1 or R2 districts, so neither applies to R6B.

Expected value: ZR 34-111 governs, not ZR 34-112: C2-2 is listed in ZR 34-111 (whose rule is the bulk regulations of the surrounding Residence District, here R6B), and is not listed in ZR 34-112 (the residential-equivalent table), and ZR 34-111's exceptions (a) and (b) do not reach R6B

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q4c (34-111 governs, C2-2 in 34-111's list, not 34-112's) and return-independent-hand-calculation-8.md Q4c (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It settles only which section governs the bulk; the surrounding R6B bulk regulations themselves are read in the plain-R6B and overlay-reading cases.

### manhattan-core - Whether the real lot is in the Manhattan Core

Facts used:

- Borough = Queens (QN, borough code 4), Community District 411 (source: NYC PLUTO row for BBL 4073340070, fields borough, borocode and cd)

Law relied on:

- ZR 12-10 (Definitions (Manhattan Core)) - captured.
  - Capture: snapshot `zr-12-10-manhattan-core`, file `docs/research/zr-snapshots/v1/zr-12-10-manhattan-core.snapshot.json`.
  - Content digest: `2c04132a96a435146c01f3c0a0578ea26520b10c2c5d1a894470ba8a47c59c56`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The "Manhattan Core" is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8."

Why the rule applies: ZR 12-10 defines the Manhattan Core as the area within Manhattan Community Districts 1 through 8. The lot is in Queens, so it cannot be within a Manhattan community district.

Expected value: no: the real lot is not in the Manhattan Core, because it is in Queens, not within Manhattan Community Districts 1 through 8

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q5 (settled no; Queens, not Manhattan CDs 1-8) and return-independent-hand-calculation-8.md Q5 (settled no); both settle this the same way on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It settles only that the lot is not in the Manhattan Core; the density regulations of the Manhattan Core are not in the captured text.

### special-downtown-brooklyn-district - Whether the real lot is in the Special Downtown Brooklyn District

Facts used:

- Borough = Queens (QN, borough code 4) (source: NYC PLUTO row for BBL 4073340070, fields borough and borocode)
- Special-district fields = none recorded (spdist1, spdist2, spdist3 absent from the served row) (source: NYC PLUTO row for BBL 4073340070, as served)

Law relied on:

- ZR 12-10 (Definitions (Special Downtown Brooklyn District)) - captured.
  - Capture: snapshot `zr-12-10-special-downtown-brooklyn-district`, file `docs/research/zr-snapshots/v1/zr-12-10-special-downtown-brooklyn-district.snapshot.json`.
  - Content digest: `ae66c93e8ec466de81587358a332c40c15fd500fc4f34ae4102c11ab43d7dd2d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The "Special Downtown Brooklyn District" is a Special Purpose District designated by the letters "DB" in which special regulations set forth in Article X, Chapter 1, apply."

Why the rule applies: ZR 12-10 identifies the Special Downtown Brooklyn District by the zoning-map letters "DB" and points its regulations to Article X, Chapter 1. The lot is in Queens and carries no special-district designation, so on the recorded facts it is outside the district; the definition itself states no geographic boundary in words (it points to the map letters and Article X, Chapter 1, which the readers did not have).

Expected value: outside the Special Downtown Brooklyn District on the recorded facts (the lot is in Queens and the record carries no special-district designation). Reading 8 (return-independent-hand-calculation-8.md) holds this subject to a text the readers did not have - the district's boundary is set by the map letters "DB" and Article X, Chapter 1, which the readers did not have - while reading 7 (return-independent-hand-calculation-7.md) treats the exclusion as settled, because that boundary is not needed to place a Queens lot with no special-district designation outside a "DB" district

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q5 (settled: outside; Queens, no DB designation) and return-independent-hand-calculation-8.md Q5 (outside on the recorded facts, but the definition's boundary is in Article X, Chapter 1, which the readers did not have); both reach "outside", and one holds it subject to a text the readers did not have, named here per the rule (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: The precise "DB" boundary is set by the zoning map and Article X, Chapter 1, which the readers did not have; reading 8 holds the exclusion subject to that text while reading 7 treats it as settled. The density regulations of the district are not in the captured text.

### height-measured-from-base-plane - From what level heights are measured

Facts used:

- District = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)

Law relied on:

- ZR 23-43 (Height and Setback Requirements in R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."
- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table"

Why the rule applies: ZR 23-43 states that the height of all buildings or other structures is measured from the base plane, and ZR 23-432 sets the minimum base height, maximum base height and maximum building height in its table. So those table heights are measured from the base plane.

Expected value: from the base plane: ZR 23-43 measures the height of all buildings or other structures from the base plane, and the minimum base height, maximum base height and maximum building height of ZR 23-432 are measured from it

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q6a (base heights and building height measured from the base plane, per 23-43) and return-independent-hand-calculation-8.md Q6a (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It settles only the datum (the base plane); it gives no base-plane elevation for the lot (that is the next row) and no above-grade height in feet.

### base-plane-real-lot - What is known of the base plane for the real lot

Facts used:

- Planimetric position = within and, near the inner corner, just beyond 100 feet of a street line; the lot is a corner lot (source: derivable from the recorded outline and street lines)
- Curb level, street-wall-line level, final grade, rear-wall-line level, slope, street-wall width, lot coverage = none recorded (source: no elevation or grade data, and these are building-design choices, in the lot's record)

Law relied on:

- ZR 12-10 (Definitions (base plane)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "For #buildings#, portions of #buildings# with #street walls# at least 15 feet in width, or #building segments# within 100 feet of a #street line#, the level of the #base plane# is any level between #curb level# and #street wall line level#. Beyond 100 feet of a #street line#, the level of the #base plane# is the average elevation of the final grade adjoining the #building# or #building segment#, determined in the manner prescribed by the New York City Building Code for adjoining grade elevation."

Why the rule applies: The base-plane definition depends on whether a building or segment is within or beyond 100 feet of a street line (a geometry fact derivable from the outline) and then on elevations - curb level and street-wall-line level within 100 feet, or the average final grade beyond 100 feet - plus street-wall width, the sloping-plane option and lot coverage. Only the planimetric inputs are in or derivable from the record; every elevation and design input is not.

Expected value: not known. Only the planimetric inputs (within or beyond 100 feet of a street line; corner-lot status) are in or derivable from the record. Every elevation input - curb level, street-wall-line level, the average final grade adjoining the building, the rear-wall-line level and slope - and the street-wall width and lot coverage are not in the record or are building-design choices, so the base-plane elevation for the lot is not known. Both readings reach this same not-known result (return-independent-hand-calculation-7.md Q6b and return-independent-hand-calculation-8.md Q6b).

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q6b (base-plane elevation not known; curb level and adjoining final grades missing) and return-independent-hand-calculation-8.md Q6b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It gives no base-plane elevation; that needs curb level and the adjoining final-grade elevations, which the readers did not have, and depends on the building's street walls and lot coverage.

### zr-23-434-eligible-sites - To which zoning lots ZR 23-434 applies, and whether it reaches R6B

Facts used:

- District = R6B (an R6 district with the letter suffix B) (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Lot area = about 10,075 sq ft (city record); about 10,388 sq ft (outline) (source: NYC PLUTO field lotarea and the MapPLUTO polygon Shape__Area)

Law relied on:

- ZR 23-434 (Height and setback modifications for eligible sites) - captured.
  - Capture: snapshot `zr-23-434`, file `docs/research/zr-snapshots/v1/zr-23-434.snapshot.json`.
  - Content digest: `d880eea8c10cb2d2f69e131e7a6f25b5b2abefceba804dbc20f2ebfe4c8e50f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-434.
  - Quoted: "In the districts indicated, without a letter suffix, for #zoning lots# that meet the criteria of paragraph (a) of this Section, the height and setback modifications set forth in paragraph (b) may be applied."
- ZR 23-434 (Height and setback modifications for eligible sites (eligible sites)) - captured.
  - Capture: snapshot `zr-23-434`, file `docs/research/zr-snapshots/v1/zr-23-434.snapshot.json`.
  - Content digest: `d880eea8c10cb2d2f69e131e7a6f25b5b2abefceba804dbc20f2ebfe4c8e50f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-434.
  - Quoted: "The provisions of this Section shall apply to #zoning lots# that meet at least one of the following criteria:"
- ZR 23-434 (Height and setback modifications for eligible sites (lot-area criterion)) - captured.
  - Capture: snapshot `zr-23-434`, file `docs/research/zr-snapshots/v1/zr-23-434.snapshot.json`.
  - Content digest: `d880eea8c10cb2d2f69e131e7a6f25b5b2abefceba804dbc20f2ebfe4c8e50f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-434.
  - Quoted: "#zoning lots# that have a #lot area# of at least 20,000 square feet or occupy an entire #block#"

Why the rule applies: ZR 23-434 applies only in the R6 through R12 districts without a letter suffix, to zoning lots meeting at least one criterion of its paragraph (a) (the "eligible sites", defined inline in that paragraph, not as a separate ZR 12-10 term). R6B has the letter suffix B, so ZR 23-434 does not reach it; the lot also does not meet the 20,000-square-foot criterion.

Expected value: ZR 23-434 applies only to R6 through R12 zoning lots without a letter suffix that meet at least one criterion of its paragraph (a) "eligible sites" (defined inline in the section, not as a separate ZR 12-10 term); it does not reach R6B, which has the letter suffix B, and the real lot also does not meet the 20,000-square-foot criterion

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q7a (R6-R12 without a letter suffix, meeting a paragraph-(a) criterion; eligible sites defined inline) and return-independent-hand-calculation-8.md Q7a (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: Some of the paragraph-(a) criteria use terms the readers did not have (for example "transportation-infrastructure-adjacent frontage"); those do not change the result, which is barred for R6B by the letter suffix.

### zr-23-362b-eligible-sites - To which zoning lots the different maximum of ZR 23-362(b) applies

Facts used:

- District = R6B (suffixed) (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Lot area = about 10,075 sq ft (city record) (source: NYC PLUTO field lotarea)
- Lot type = corner (source: cases/real-lot.json row L9)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts (eligible sites)) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "In the districts indicated, for #zoning lots# with #buildings# utilizing the eligible site provisions of Section 23-434 (Height and setback modifications for eligible sites), the maximum #residential# #lot coverage# of the entire site shall be:"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts (65 percent)) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "65 percent on #zoning lots# with a #lot area# of 30,000 square feet or more that are not #large sites#"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts (standard lots)) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent"

Why the rule applies: ZR 23-362(b)'s lower maximum lot coverage (65 percent, or 50 percent on large sites) applies only to zoning lots whose buildings utilize the ZR 23-434 eligible-site provisions, not to every 30,000-square-foot lot; a lot must both be at least 30,000 square feet and be using ZR 23-434 (and not be a large site) to get 65 percent. Because ZR 23-434 is unavailable in R6B and the real lot is far below the thresholds, ZR 23-362(b) does not apply to the real lot.

Expected value: ZR 23-362(b)'s different maximum (65 percent, or 50 percent on large sites) applies only to zoning lots whose buildings utilize the ZR 23-434 eligible-site provisions - not to every lot of 30,000 square feet or more; it does not reach the real lot, because ZR 23-434 is unavailable in suffixed R6B and the lot is far below the 20,000- and 30,000-square-foot thresholds

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q7b/Q7c (b) applies only to lots using 23-434, not every 30,000-sq-ft lot; not the real lot) and return-independent-hand-calculation-8.md Q7b/Q7c (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: This row does not read the real lot's whole-lot lot coverage. Both readings say in passing, in their eligible-sites answer (Q7c), that "the standard coverage of ZR 23-362(a) for this corner lot is 100 percent" (return-independent-hand-calculation-7.md Q7c: "the applicable maximum residential lot coverage is 23-362(a) - 100% for this corner lot"; return-independent-hand-calculation-8.md Q7c: "the real lot's lot coverage is governed by the STANDARD zr-23-362(a) ... it is a corner lot, so 100%"). Neither worked the corner-lot-portion rule there, although both quote that rule and both measure the lot at about 103.9 feet from the 215 Place street line; those sentences are passing remarks, not a reading of whole-lot coverage. The whole-lot corner-coverage reading stays per portion and not known: cases/real-lot.json row L5, cases/corner-reach.json row real-lot-coverage, and the corner-coverage rows of cases/step-p1-worked.json keep their not-known per-portion value.

### residence-residential-definition - The definition of "residence" and "residential"

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions (residence)) - captured.
  - Capture: snapshot `zr-12-10-residence-or-residential`, file `docs/research/zr-snapshots/v1/zr-12-10-residence-or-residential.snapshot.json`.
  - Content digest: `fffb54b13ef4afde340b09d1f075474f2b096a5ed367fca78b3758d1fb7b593b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "A "residence" is one or more #dwelling units# or #rooming units#, including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas."
- ZR 12-10 (Definitions (residential)) - captured.
  - Capture: snapshot `zr-12-10-residence-or-residential`, file `docs/research/zr-snapshots/v1/zr-12-10-residence-or-residential.snapshot.json`.
  - Content digest: `fffb54b13ef4afde340b09d1f075474f2b096a5ed367fca78b3758d1fb7b593b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: ""Residential" means pertaining to a #residence#."

Why the rule applies: ZR 12-10 defines a residence as one or more dwelling units or rooming units, including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas, and excluding transient accommodations, non-profit hospital staff dwellings and community-facility or dormitory-type accommodations; "residential" means pertaining to a residence.

Expected value: a "residence" is one or more dwelling units or rooming units, including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas (and excluding transient accommodations, non-profit hospital staff dwellings, and community-facility or dormitory-type accommodations); "residential" means pertaining to a residence

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q8a (residence and residential definitions, read verbatim) and return-independent-hand-calculation-8.md Q8a (same); both read the same words on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: The sub-terms "dwelling unit" and "rooming unit" are defined terms the readers did not have, so the precise content of those two is not fixed by the captured text.

### floor-area-share-bases - The base of the share in ZR 23-231 and in ZR 23-232

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-23 (Special Floor Area Provisions for Multiple Dwelling Residences) - captured.
  - Capture: snapshot `zr-23-23`, file `docs/research/zr-snapshots/v1/zr-23-23.snapshot.json`.
  - Content digest: `6dd17af023030a301d6ebcea5f7a18322a57e7b37a6f6d72406cc6f49054961f`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-23.
  - Quoted: "floor space allocated to #building# amenities, corridors, refuse storage or disposal, or access to elevated ground floor #dwelling units# may be exempted from the definition of #floor area# pursuant to Section 12-10, provided that the provisions of this Section, inclusive, are met"
- ZR 23-231 (Floor area provisions for amenities) - captured.
  - Capture: snapshot `zr-23-231`, file `docs/research/zr-snapshots/v1/zr-23-231.snapshot.json`.
  - Content digest: `81eb95e85b333eb86a0fc55413c78567d0b72d7ba9656041f77457f2263b49d6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-231.
  - Quoted: "Floor space in a #building# allocated to #residential# amenities may be exempted from the definition of #floor area#, in an amount not to exceed five percent of the #residential floor area# of the #building#."
- ZR 23-232 (Floor area provisions for corridors) - captured.
  - Capture: snapshot `zr-23-232`, file `docs/research/zr-snapshots/v1/zr-23-232.snapshot.json`.
  - Content digest: `0a79cda6656d8d0c32a10e052cdf5e4b668297af1c411180331139401fc13ad2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-232.
  - Quoted: "Fifty percent of the floor space of a corridor may be exempted from the definition of #floor area#"

Why the rule applies: ZR 23-23 states no share itself; it routes to its sub-sections. ZR 23-231 exempts up to five percent of "the residential floor area of the building" - its base is named but "residential floor area" is a defined term the readers did not have, so the base is not settled. ZR 23-232 exempts fifty percent of the floor space of a corridor - its base is the corridor's own floor space, which the captured text settles.

Expected value: ZR 23-232's share is based on the corridor's own floor space (fifty percent of the floor space of a corridor), which the captured text settles; ZR 23-231's share is based on "the residential floor area of the building" (five percent of it), a base that is named but not settled, because "residential floor area" is a defined term the readers did not have

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q8b (23-231 base = residential floor area, not settled; 23-232 base = corridor's own floor space, settled) and return-independent-hand-calculation-8.md Q8b (same); both agree on the same basis (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: It computes nothing. "Residential floor area" is a defined term the readers did not have, so the ZR 23-231 base is not settled; ZR 23-233 (three square feet per dwelling unit) and ZR 23-234 (per foot of elevation, capped per building) are absolute allowances, not shares of a floor area.

### sections-and-facts-not-had - Every section, defined term and fact the readings needed and did not have, and what stays not known

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 34-11 (General Provisions (named exceptions)) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"
- ZR 23-343 (Rear yard equivalent requirements (cross-reference)) - captured.
  - Capture: snapshot `zr-23-343`, file `docs/research/zr-snapshots/v1/zr-23-343.snapshot.json`.
  - Content digest: `b4440929d887fa5eba92db8ad881bdf84b04d3283b988026ab58ff6865221680`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-343.
  - Quoted: "except as otherwise provided pursuant to the provisions of Section 23-34, inclusive"
- ZR 12-10 (Definitions (base plane, elevation inputs)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "the level of the #base plane# is any level between #curb level# and #street wall line level#"
- ZR 23-231 (Floor area provisions for amenities (base term)) - captured.
  - Capture: snapshot `zr-23-231`, file `docs/research/zr-snapshots/v1/zr-23-231.snapshot.json`.
  - Content digest: `81eb95e85b333eb86a0fc55413c78567d0b72d7ba9656041f77457f2263b49d6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-231.
  - Quoted: "five percent of the #residential floor area# of the #building#"
- ZR 12-10 (Definitions (Special Downtown Brooklyn District, pointer)) - captured.
  - Capture: snapshot `zr-12-10-special-downtown-brooklyn-district`, file `docs/research/zr-snapshots/v1/zr-12-10-special-downtown-brooklyn-district.snapshot.json`.
  - Content digest: `ae66c93e8ec466de81587358a332c40c15fd500fc4f34ae4102c11ab43d7dd2d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "special regulations set forth in Article X, Chapter 1, apply"

Why the rule applies: The captured texts the readings worked point to further sections and defined terms the readers did not have; this row names them and what stays not known because of them, recording the items both readings name as the agreed list.

Expected value: Named by both readings and not had: Sections 34-22 (modification of floor area) and 34-23 (modification of yards), both pointed to by ZR 34-21/34-11; the Section 23-34 (inclusive) cross-reference in ZR 23-342 and ZR 23-343; Section 36-64 (special-area height and setback) and Section 35-71 (the optional sky-exposure-plane envelope), pointed to by ZR 34-24; Article X, Chapter 1 (the Special Downtown Brooklyn District regulations); and the defined terms "large sites", "transportation-infrastructure-adjacent frontage", "residential floor area", "short dimension of a block", "curb level", "street wall line level" and "rear wall line level". What stays not known because of them: how the overlay modifies floor area and the yards (34-22, 34-23); the base of the ZR 23-231 amenities share ("residential floor area"); the base-plane elevation (curb level and the adjoining final grades); the large-site exemptions and cases; and the precise Special Downtown Brooklyn District boundary. Also absent are the facts the law needs - the adjoining zoning lots' lot-line types (for the rear yard beyond the corner) and the site's elevation and grade data (for the base plane)

Where this stands in the independent reading: return-independent-hand-calculation-7.md Q9 and return-independent-hand-calculation-8.md Q9; both name these sections, terms and facts as not had (return-independent-hand-calculation-7.md and return-independent-hand-calculation-8.md).

What this row does not establish: This is the list of items the captured texts name that the readers did not have; it is not a claim that the repository holds no other related text. Reading 8 additionally names further defined terms (for example "dwelling unit", "rooming unit", "residential equivalent", "street setback line", "building segment" and "abutting buildings") that bound the fine application but do not change which rule governs; reading 7 does not list all of these, so they are noted here, not recorded as the agreed list.

## What this case does not establish

- It records a value or a yes/no only where both readings agree on the same basis; where they differ, where one holds an answer subject to a text the readers did not have, or where neither settles a point, the row says so and names both readings.
- The made-up interior, through and corner lots are not real properties; the real lot's measurements use the approximate tax-map outline, not a survey.
- It does not read the overlay's floor-area or yard modifications (ZR 34-22 and ZR 34-23 were not among the captured texts the readers had), nor the base-plane elevation, nor any whole-lot coverage percentage.
- It is not a professional or legal determination and does not say anything complies.

## Sources

- The step-P3 reading 1: provenance/return-independent-hand-calculation-7.md
- The step-P3 reading 2: provenance/return-independent-hand-calculation-8.md
- The sealed folder given to each helper: the pinned law-text captures (without the notes describing how the program encoded them), the real lot's recorded official facts and outline, and three made-up lots, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Case created (step P3, task M4-T030) from the two independent readings of the step-P3 sealed folder (provenance/return-independent-hand-calculation-7.md and -8.md). It holds the readings that waited for the law text captured by task M4-T029 (the ZR 12-10 lot-line, lot-width and lot-depth definitions, ZR 23-343, ZR 23-436, ZR 34-21, ZR 34-112, the Manhattan Core and Special Downtown Brooklyn District definitions, the base plane, ZR 23-434 and the residence definition). A value or a yes/no is recorded only where both readings agree on the same basis. | rules-engineer (M4-T030) |

