# Worked from the step-P1 captures: made-up lots, rear yard and special density areas

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: section 5 gaps K1, K2, K4, K11; section 8 (worked from the new text, as in step R0).

The reference-case rows that waited for step P1, now worked from the law text captured by task M4-T025: the ZR 12-10 corner, interior, through and lot-area definitions, the ZR 12-10 special-density-areas definition, ZR 23-342 (rear yard) and ZR 23-363 (special coverage rules). It covers three made-up corner lots (the step-P1 readings' C1, C2 and C3), a made-up 40-by-100 interior lot, a made-up 40-by-200 through lot, and special density areas. Every value comes from the two independent readings and the law text, never from a program run. A value is recorded only where both readings give the same value on the same basis.

## What this case is worth

Prepared by one AI helper and read again, independently, by a second AI, each working alone from the sealed step-P1 folder; their agreement alone is not proof. It is a draft reading of the law, not professionally reviewed, and is not a statement that anything complies. The made-up lots are not real properties; they are chosen to show the corner-portion partition, the interior and through coverage reading, and the rear-yard reach.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of the step-P1 law-text captures and the lot's recorded facts, with no access to the program (reading 1: provenance/return-independent-hand-calculation-3.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-4.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| District (made-up lots) | R6B, no overlay | the examples' stated district |
| Benchmark lot borough | Queens (QN, borough code 4), BBL 4073340070 | NYC PLUTO row for BBL 4073340070, fields borough and borocode |
| Benchmark lot special-district fields | none recorded (spdist1, spdist2, spdist3 absent from the served row) | NYC PLUTO row for BBL 4073340070, as served |

## Rows

### lot-area-definition - What ZR 12-10 means by lot area

Facts used:

- Benchmark lot area, city record (tabular) = 10,075 sq ft (source: NYC PLUTO row for BBL 4073340070, field lotarea)
- Benchmark lot area, outline measure = about 10,388 sq ft (source: MapPLUTO polygon for BBL 4073340070, Shape__Area 10,387.99)

Law relied on:

- ZR 12-10 (Definitions (lot area)) - captured.
  - Capture: snapshot `zr-12-10-lot-area`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-area.snapshot.json`.
  - Content digest: `5fe518c6a26a01ea746d3e92f986a71410f739e6ecb2f3e345c62f852e863db6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the area of a #zoning lot#"

Why the rule applies: ZR 12-10 defines lot area as the area of a zoning lot. Both step-P1 readings read this verbatim and both note that the two recorded official figures for the benchmark lot (the PLUTO tabular lot area of 10,075 square feet and the MapPLUTO outline area of about 10,388 square feet) differ by about 3 percent.

Expected value: the area of a zoning lot

Where this stands in the independent reading: return-independent-hand-calculation-3.md (facts used, 'Lot area' = 'the area of a #zoning lot#'; the 10,075 vs 10,388 discrepancy) and return-independent-hand-calculation-4.md ('A DISCREPANCY TO CARRY THROUGHOUT'); both read ZR 12-10 lot area as the area of a zoning lot.

What this row does not establish: It does not settle which recorded figure is the operative lot area: the two official figures differ by about 3 percent, a tax lot need not equal a zoning lot, and the captured text does not reconcile them, so the operative lot-area figure for the benchmark lot is not known.

### corner-100x100-coverage - Made-up corner lot C1 (100 ft by 100 ft): maximum lot coverage

Facts used:

- Lot = a made-up rectangle, 100 ft on street A by 100 ft on street B, both sides street lines meeting at 90 degrees (source: the step-P1 readings' lot C1)

Law relied on:

- ZR 12-10 (Definitions (lot, corner)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"

Why the rule applies: The two adjacent sides are street lines meeting at 90 degrees (135 or less), so it is a corner lot under ZR 12-10. The corner-lot portion is the part within 100 feet of each street line; the lot reaches only 100 feet from each street line, so the whole lot is the corner-lot portion, and ZR 23-362(a) gives corner lots 100 percent. The geometry shows the corner provision covers the whole lot.

Working, step by step:

- lot area: 100 (frontage on street A (ft)) x 100 (frontage on street B (ft)) = 10,000
- corner-lot portion (within 100 ft of each street line): 100 (100 ft from street line B (ft)) x 100 (100 ft from street line A (ft)) = 10,000

Expected value: 100 percent

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q1c/Q2b C1 (corner portion = the entire lot = 10,000 sq ft; 100 percent whole lot) and return-independent-hand-calculation-4.md, Q1c/Q2b C1 (same); both agree.

What this row does not establish: A made-up rectangle, not a real property. The 100 percent is the residential lot-coverage maximum for a corner lot and rests on the whole lot being the ZR 12-10 corner-lot portion.

### corner-150x100-coverage - Made-up corner lot C2 (150 ft on street A by 100 ft on street B): maximum lot coverage

Facts used:

- Lot = a made-up rectangle, 150 ft on street A by 100 ft on street B, both adjacent sides street lines meeting at 90 degrees (source: the step-P1 readings' lot C2)

Law relied on:

- ZR 12-10 (Definitions (lot, corner)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"

Why the rule applies: A corner lot (90 degrees). The corner-lot portion is within 100 feet of each street line: 100 feet along street A by 100 feet deep, which is 10,000 square feet at 100 percent (ZR 23-362(a)). The strip from 100 to 150 feet along street A (5,000 square feet) is a remaining portion that adjoins only one street, so under ZR 12-10 it takes interior-lot regulations, at 80 percent. Because two provisions apply to different portions, there is no single whole-lot figure.

Working, step by step:

- lot area: 150 (frontage on street A (ft)) x 100 (frontage on street B (ft)) = 15,000
- corner-lot portion (100 ft along A by 100 ft deep): 100 (100 ft along street A (ft)) x 100 (100 ft deep from street A (ft)) = 10,000
- remaining interior-lot portion (lot area minus corner portion): 15,000 (lot area (sq ft)) - 10,000 (corner-lot portion (sq ft)) = 5,000

Expected value: not known. No single whole-lot coverage figure: the corner-lot portion (within 100 feet of each street line, 10,000 square feet) has a maximum residential lot coverage of 100 percent, and the remaining interior-lot portion (5,000 square feet) has 80 percent. Both readings give this per-portion reading on the same basis (ZR 12-10 corner-lot portion with ZR 23-362(a)).

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q1c/Q2b C2 (corner portion 10,000 sq ft at 100 percent; remaining 5,000 sq ft interior at 80 percent) and return-independent-hand-calculation-4.md, Q1c/Q2b C2 (same); both agree, per portion.

What this row does not establish: A made-up rectangle. It gives the coverage per portion (100 percent and 80 percent), not a single whole-lot figure.

### corner-150x100-rear-yard - Made-up corner lot C2 (150 by 100): rear yard

Facts used:

- Lot = a made-up corner rectangle, 150 ft by 100 ft, street lines meeting at 90 degrees (source: the step-P1 readings' lot C2)

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

Why the rule applies: Within 100 feet of the corner point no rear yard is required (ZR 23-344(a); 90 degrees is 135 or less). Beyond 100 feet of a street line the beyond-portion of a side lot line is treated as a rear lot line (ZR 23-344(c)), and whether a rear yard is then required there, and its depth under ZR 23-342, depends on the neighbouring lot lines, the building type and the lot width.

Expected value: not known. Within 100 feet of the corner point no rear yard is required; beyond that the rear-yard outcome is not settled. It needs the neighbouring lot-line configuration (ZR 23-344(c)(1) versus (c)(3)) and, for any required depth, the building type and lot width (ZR 23-342), none of which are given, and the ZR 12-10 side-/rear-lot-line definitions are not captured. Both readings reach this same not-known result.

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q3b (C2/C3: no rear yard within 100 ft of the corner; beyond, depth and requirement not known) and return-independent-hand-calculation-4.md, Q3b (same); both agree it is not known beyond the corner.

What this row does not establish: A made-up rectangle. It does not settle the rear yard beyond 100 feet of the corner point, nor any depth.

### corner-200x120-coverage - Made-up corner lot C3 (200 ft on street A by 120 ft on street B): maximum lot coverage

Facts used:

- Lot = a made-up rectangle, 200 ft on street A by 120 ft on street B, both adjacent sides street lines meeting at 90 degrees (source: the step-P1 readings' lot C3)

Law relied on:

- ZR 12-10 (Definitions (lot, corner)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"

Why the rule applies: A corner lot (90 degrees). The corner-lot portion is within 100 feet of each street line: 100 feet by 100 feet, which is 10,000 square feet at 100 percent (ZR 23-362(a)). The remaining 14,000 square feet (an L-shape beyond 100 feet of one or both street lines) adjoins at most one street, so under ZR 12-10 it takes interior-lot regulations, at 80 percent. Because two provisions apply to different portions, there is no single whole-lot figure.

Working, step by step:

- lot area: 200 (frontage on street A (ft)) x 120 (frontage on street B (ft)) = 24,000
- corner-lot portion (100 ft by 100 ft): 100 (100 ft along street A (ft)) x 100 (100 ft along street B (ft)) = 10,000
- remaining interior-lot portion (lot area minus corner portion): 24,000 (lot area (sq ft)) - 10,000 (corner-lot portion (sq ft)) = 14,000

Expected value: not known. No single whole-lot coverage figure: the corner-lot portion (within 100 feet of each street line, 10,000 square feet) has a maximum residential lot coverage of 100 percent, and the remaining interior-lot portion (14,000 square feet) has 80 percent. Both readings give this per-portion reading on the same basis (ZR 12-10 corner-lot portion with ZR 23-362(a)).

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q1c/Q2b C3 (corner portion 10,000 sq ft at 100 percent; remaining 14,000 sq ft interior at 80 percent) and return-independent-hand-calculation-4.md, Q1c/Q2b C3 (same); both agree, per portion.

What this row does not establish: A made-up rectangle. It gives the coverage per portion (100 percent and 80 percent), not a single whole-lot figure.

### corner-200x120-rear-yard - Made-up corner lot C3 (200 by 120): rear yard

Facts used:

- Lot = a made-up corner rectangle, 200 ft by 120 ft, street lines meeting at 90 degrees (source: the step-P1 readings' lot C3)

Law relied on:

- ZR 23-344 (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less"
- ZR 23-344 (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no rear yard shall be required where such rear lot line coincides with a side lot line of an adjoining zoning lot"

Why the rule applies: Within 100 feet of the corner point no rear yard is required (ZR 23-344(a)). Beyond 100 feet of a street line the beyond-portion of a side lot line is treated as a rear lot line (ZR 23-344(c)); along it, in R6 through R12 districts, no rear yard is required where it coincides with a neighbour's side lot line, but one is required where it coincides with a neighbour's rear lot line, and any depth is set by ZR 23-342.

Expected value: not known. Within 100 feet of the corner point no rear yard is required; beyond that the rear-yard outcome is not settled. It needs the neighbouring lot-line configuration (ZR 23-344(c)(1) versus (c)(3)) and, for any required depth, the building type and lot width (ZR 23-342), none of which are given, and the ZR 12-10 side-/rear-lot-line definitions are not captured. Both readings reach this same not-known result.

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q3b (C2/C3) and return-independent-hand-calculation-4.md, Q3b (C2/C3); both agree it is not known beyond the corner.

What this row does not establish: A made-up rectangle. It does not settle the rear yard beyond 100 feet of the corner point, nor any depth.

### interior-40x100-coverage - Made-up interior lot (40 ft by 100 ft), R6B: maximum lot coverage, and whether ZR 23-363 changes it

Facts used:

- Lot = a made-up interior lot, 40 ft by 100 ft, R6B, no overlay (source: chosen for this example)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"
- ZR 23-363 (Special rules for certain interior or through lots) - captured.
  - Capture: snapshot `zr-23-363`, file `docs/research/zr-snapshots/v1/zr-23-363.snapshot.json`.
  - Content digest: `7ff320d2f18feec7cc53f609c066d09ac349a714b83c6dbd014e2cb51932ab34`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-363.
  - Quoted: "may be increased in accordance with the provisions of this Section"
- ZR 23-363 (Special rules for certain interior or through lots) - captured.
  - Capture: snapshot `zr-23-363`, file `docs/research/zr-snapshots/v1/zr-23-363.snapshot.json`.
  - Content digest: `7ff320d2f18feec7cc53f609c066d09ac349a714b83c6dbd014e2cb51932ab34`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-363.
  - Quoted: "is less than 95 feet for #interior lots# or 190 feet for #through lots#"

Why the rule applies: ZR 23-362(a) gives interior lots a maximum residential lot coverage of 80 percent. ZR 23-363 may only increase that maximum, and only under one of its triggers: a shallow lot less than 95 feet deep, a portion within 100 feet of a qualifying street corner, or a front lot line on the short dimension of the block. On the bare 40-by-100 facts the lot is 100 feet deep (not less than 95 feet), and the corner-proximity and short-dimension facts are not given, so ZR 23-363 does not change the 80 percent on these facts.

Expected value: 80 percent

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q2c interior lot ('23-362 base = 80%'; '23-363 does NOT change the 80%' on the bare facts) and return-independent-hand-calculation-4.md, Q2c interior lot (same); both agree 80 percent.

What this row does not establish: ZR 23-363 could raise the 80 percent - to as much as 90 percent for a shallow lot (less than 95 feet deep, if the shallow condition existed on December 15, 1961), or to 100 percent for a portion within 100 feet of a qualifying street corner, or where the front lot line is on the block's short dimension. Those facts (which dimension is the depth, the 1961 history, the lot's location, the block's dimensions) are not given, so whether ZR 23-363 would raise it is not known.

### interior-40x100-rear-yard - Made-up interior lot (40 ft by 100 ft), R6B: rear yard

Facts used:

- Lot = a made-up interior lot, 40 ft by 100 ft, R6B (source: chosen for this example)

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
  - Quoted: "a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line#"
- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "for #zoning lots# with a #lot width# of less than 40 feet, a #rear yard# with a depth of not less than 30 feet"

Why the rule applies: ZR 23-342 requires a rear yard on an interior lot at every rear lot line; its depth depends on the building type (detached or zero-lot-line, or semi-detached or attached) and the lot width (less than 40 feet, or 40 feet or greater).

Expected value: not known. The two step-P1 readings do not settle the depth on the same basis. Reading 1 (return-independent-hand-calculation-3.md, Q3b) leaves the depth not known, because the building type is not given and it is not stated which of the two dimensions is the lot width. Reading 2 (return-independent-hand-calculation-4.md, Q3b), taking the 40-foot dimension as the lot width, reads ZR 23-342 to give a 20-foot rear yard at or below 75 feet of height (30 feet above), because at a lot width of 40 feet both building-type branches give 20 feet. Because the two readings differ and rest on different assumptions, no value is recorded; it stays not known.

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q3b (40x100 interior: depth NOT KNOWN) and return-independent-hand-calculation-4.md, Q3b (40x100 interior: 20 ft at or below 75 ft, assuming 40 ft is the lot width); the two differ, so the row is not known.

What this row does not establish: No rear-yard depth is settled; it would need the building type and a stated lot width. ZR 23-344(a)'s corner waiver does not apply to an interior lot (it has no two intersecting street lines) absent corner facts, and the ZR 12-10 lot-width and rear-lot-line definitions are not captured.

### through-40x200-coverage - Made-up through lot (40 ft wide, 200 ft between the two streets), R6B: maximum lot coverage

Facts used:

- Lot = a made-up through lot, 40 ft wide by 200 ft deep between two opposite parallel streets, R6B (source: chosen for this example)

Law relied on:

- ZR 12-10 (Definitions (lot, through)) - captured.
  - Capture: snapshot `zr-12-10-lot-through`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-through.snapshot.json`.
  - Content digest: `d71f24ad1ff0875e639ff40f99f76f61dce4df4f440c8fa3c792704262435a0d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "adjoins two #street lines# opposite to each other and parallel or within 45 degrees of being parallel to each other"
- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"
- ZR 23-363 (Special rules for certain interior or through lots) - captured.
  - Capture: snapshot `zr-23-363`, file `docs/research/zr-snapshots/v1/zr-23-363.snapshot.json`.
  - Content digest: `7ff320d2f18feec7cc53f609c066d09ac349a714b83c6dbd014e2cb51932ab34`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-363.
  - Quoted: "is less than 95 feet for #interior lots# or 190 feet for #through lots#"

Why the rule applies: A lot adjoining two opposite, roughly parallel streets is a through lot (ZR 12-10). ZR 23-362(a) gives through lots a maximum residential lot coverage of 80 percent. ZR 23-363 may only increase it; a 200-foot-deep through lot is not shallow (not less than 190 feet deep), and the corner-proximity and short-dimension facts are not given, so ZR 23-363 does not change the 80 percent on these facts.

Expected value: 80 percent

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q2c through lot ('23-362 base = 80%'; '23-363 does not change 80% on the bare facts') and return-independent-hand-calculation-4.md, Q2c through lot ('23-362(a) gives 80%'; not shallow at 200 ft; '23-363 does NOT change the 80%'); both agree 80 percent.

What this row does not establish: ZR 23-363 could raise the 80 percent under its triggers (a shallow through lot less than 190 feet deep, a portion within 100 feet of a qualifying corner, or a front lot line on the block's short dimension), but those facts are not given, so whether it would raise it is not known. It gives no through-lot rear yard (that is the separate ZR 23-343, not captured).

### through-40x200-rear-yard - Made-up through lot (40 by 200), R6B: rear yard

Facts used:

- Lot = a made-up through lot, 40 ft wide by 200 ft deep, R6B (source: chosen for this example)

Law relied on:

- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "shall be provided on #interior lots# in accordance with this Section"
- ZR 23-363 (Special rules for certain interior or through lots) - captured.
  - Capture: snapshot `zr-23-363`, file `docs/research/zr-snapshots/v1/zr-23-363.snapshot.json`.
  - Content digest: `7ff320d2f18feec7cc53f609c066d09ac349a714b83c6dbd014e2cb51932ab34`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-363.
  - Quoted: "the #rear yard equivalent# modifications for shallow #through lots# set forth in Section 23-343"

Why the rule applies: ZR 23-342 provides rear yards only on interior lots, not through lots. The through-lot requirement is the rear-yard equivalent of ZR 23-343, which the captured ZR 23-363 names, but ZR 23-343 is itself not captured.

Expected value: not known. The captured text (ZR 23-342 and ZR 23-344) does not state a through lot's rear-yard requirement; the governing rule is the rear-yard equivalent of ZR 23-343, which is named by the captured ZR 23-363 but is itself not captured, so the requirement is not known. Both readings reach this same not-known result.

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q3c (through lot: rear-yard equivalent of 23-343, not captured, NOT KNOWN) and return-independent-hand-calculation-4.md, Q3c (same); both agree it is not known.

What this row does not establish: It gives no rear-yard-equivalent requirement for the through lot; that waits for ZR 23-343. ZR 23-344(a)'s corner waiver does not apply to a pure through lot (its two streets are opposite and parallel, not intersecting).

### special-density-areas-list - What the ZR 12-10 definition of special density areas lists

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions (special density areas)) - captured.
  - Capture: snapshot `zr-12-10-special-density-areas`, file `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json`.
  - Content digest: `e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "shall refer to special geographies where unique density regulations apply to #residential# #developments# or #enlargements#"
- ZR 12-10 (Definitions (special density areas)) - captured.
  - Capture: snapshot `zr-12-10-special-density-areas`, file `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json`.
  - Content digest: `e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(a) the #Manhattan Core#; and"
- ZR 12-10 (Definitions (special density areas)) - captured.
  - Capture: snapshot `zr-12-10-special-density-areas`, file `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json`.
  - Content digest: `e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(b) the #Special Downtown Brooklyn District#."

Why the rule applies: ZR 12-10 defines special density areas as special geographies where unique density regulations apply to residential developments or enlargements, and lists two: (a) the Manhattan Core and (b) the Special Downtown Brooklyn District. Both step-P1 readings read this verbatim.

Expected value: the definition lists two special density areas: (a) the Manhattan Core and (b) the Special Downtown Brooklyn District

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q4a ('lists exactly two: (a) the Manhattan Core; (b) the Special Downtown Brooklyn District') and return-independent-hand-calculation-4.md, Q4a (same list); both agree.

What this row does not establish: One reading notes the 'shall include' wording may be non-exhaustive while the other treats the list as closed to these two, so whether the list is exhaustive is not settled. The captured text does not give the geographic boundaries of the Manhattan Core or the Special Downtown Brooklyn District.

### special-density-real-lot - Whether the benchmark lot is in a special density area, from its recorded facts

Facts used:

- Benchmark lot borough = Queens (QN, borough code 4), BBL 4073340070 (source: NYC PLUTO row for BBL 4073340070, fields borough and borocode)
- Benchmark lot special-district fields = none recorded (spdist1, spdist2, spdist3 absent from the served row) (source: NYC PLUTO row for BBL 4073340070, as served)

Law relied on:

- ZR 12-10 (Definitions (special density areas)) - captured.
  - Capture: snapshot `zr-12-10-special-density-areas`, file `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json`.
  - Content digest: `e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "shall refer to special geographies where unique density regulations apply to #residential# #developments# or #enlargements#"

Why the rule applies: The ZR 12-10 definition lists only the Manhattan Core and the Special Downtown Brooklyn District, both named for other boroughs; the benchmark lot's recorded facts place it in Queens with no special-district value, which both readings read as strongly implying it is in neither, but the captured text does not give the geographic boundaries of either listed area.

Expected value: not known. The benchmark lot's recorded facts (borough Queens, no special-district field) and the two listed areas (the Manhattan Core, the Special Downtown Brooklyn District) strongly imply the lot is in neither, but the captured text does not give the geographic boundaries of those areas, so membership cannot be settled from the captured text. Both readings reach this same conclusion and neither settles it.

Where this stands in the independent reading: return-independent-hand-calculation-3.md, Q4b and return-independent-hand-calculation-4.md, Q4b; both read the Queens location as strongly implying the lot is in neither area but say it cannot be closed without the captured boundary definitions.

What this row does not establish: It does not place the lot inside or outside a special density area definitively; that needs the captured boundary definitions of the Manhattan Core and the Special Downtown Brooklyn District.

## What this case does not establish

- The corner lots, the interior lot and the through lot are made up; they do not describe any real property.
- It records a value only where both readings agree on the same basis; where they differ or do not settle a point, the row stays not known and names both readings.
- It does not read the C2-2 commercial overlay or any special-purpose-district rule; the rear-yard depth, the through-lot rear-yard equivalent (ZR 23-343) and the lot-line definitions are not available.
- It is not a professional or legal determination and does not say anything complies.

## Sources

- The step-P1 reading 1: provenance/return-independent-hand-calculation-3.md
- The step-P1 reading 2: provenance/return-independent-hand-calculation-4.md
- The sealed folder given to each helper: the pinned ZR step-P1 captures (without the notes describing how the program encoded them) and the lot's recorded official facts, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Case created (step P1, task M4-T027) from the two independent readings of the step-P1 sealed folder (provenance/return-independent-hand-calculation-3.md and -4.md). It holds the rows that waited for the law text captured by task M4-T025: the ZR 12-10 corner/interior/through/lot-area and special-density-areas definitions, ZR 23-342 and ZR 23-363. A value is recorded only where both readings agree on the same basis. | rules-engineer (M4-T027) |

