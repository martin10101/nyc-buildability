# The reach of a corner lot (the real lot and three made-up rectangles)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: C.

How far a corner lot reaches from each street line and from the corner point, which decides whether the 100-percent corner coverage and the rear-yard waiver cover the whole lot. It covers the real lot (215-16 Northern Boulevard) and three made-up rectangles C1, C2 and C3. Every value comes from measurements of the recorded outline (or the chosen rectangle sizes) and the law text, never from a program run.

## What this case is worth

Prepared by an AI helper and recomputed by a second AI; their agreement alone is not proof. The real lot's reaches are measured from the approximate tax-map outline; C1, C2 and C3 are made-up rectangles chosen to show the corner-lot-portion and rear-yard thresholds. It is a draft reading, not professionally reviewed. The corner-lot-portion definition it uses (ZR 12-10) and ZR 23-342 are now captured (task M4-T025); the step-P1 readings worked their own made-up corner lots in cases/step-p1-worked.json.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of pinned law-text captures and the lot's recorded facts, with no access to the program.
- Checked by: A second AI recomputed the arithmetic and the geometry independently from the same sealed folder. Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Real lot outline | five vertices P0..P4 in EPSG:2263 feet | recorded MapPLUTO polygon for BBL 4073340070 |
| Real lot street lines | Northern Boulevard (P1-P2) and 215 Place (P2-P3) | recorded outline and DCM centerlines |
| C1 | 40 ft x 100 ft rectangle, 4,000 sq ft | made up for this example |
| C2 | 60 ft x 80 ft rectangle, 4,800 sq ft | made up for this example |
| C3 | 150 ft x 100 ft rectangle, 15,000 sq ft | made up for this example |

## Rows

### real-lot-reach - The real lot: how far it reaches from each street line and from the corner

Facts used:

- Lot outline = five vertices P0..P4 in EPSG:2263 feet (source: recorded MapPLUTO polygon)
- Street lines = Northern Boulevard (edge P1-P2) and 215 Place (edge P2-P3) (source: recorded outline and DCM centerlines)
- Corner point = P2 (source: the meeting of the two street lines)

Law relied on:

- none cited

Why the rule applies: These reaches decide whether the whole lot is the corner-lot portion (within 100 feet of each street line) and whether the rear-yard waiver (within 100 feet of the corner point) covers the whole lot.

Expected value: from the Northern Boulevard street line the lot reaches at most 99.97 ft; from the 215 Place street line at most 103.93 ft; from the corner point at most 144.60 ft. The whole lot is within 100 ft of the Northern Boulevard street line but not of the 215 Place street line (a strip about 3.93 ft wide, about 390 sq ft, lies beyond), and not within 100 ft of the corner point (about 2,560 sq ft lies beyond)

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q1(a)-(c).

What this row does not establish: These are measurements from the approximate tax-map outline (the strip and wedge areas are grid approximations), not a survey; by themselves they give no coverage percentage or rear-yard requirement.

### real-lot-coverage - The real lot: lot coverage for the whole lot

Facts used:

- Reach from the 215 Place street line = 103.93 ft (source: return 2 Q1(a): about 390 sq ft lies beyond 100 ft)

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

Why the rule applies: The 100-percent corner-lot rule (ZR 23-362(a)) covers only the captured ZR 12-10 corner-lot portion, within 100 feet of each street line; part of this lot lies beyond 100 feet of the 215 Place street line, so it is a corner-lot portion plus a remaining interior-lot portion.

Expected value: not known. The lot reaches 103.93 feet from the 215 Place street line, so it is not wholly within the corner-lot portion and there is no single whole-lot coverage figure. Both step-P1 readings read it per portion: the corner-lot portion has a maximum residential lot coverage of 100 percent and the remaining interior-lot portion 80 percent.

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q1(a)-(b), and the work order's table C ('not known'); the per-portion reading is confirmed by both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q2a).

What this row does not establish: It gives no whole-lot coverage percentage; the two step-P1 readings give about 9,998 and 9,997.6 square feet for the corner portion, resting on the approximate outline and a one-foot street-line tolerance.

### real-lot-rear-yard - The real lot: rear yard beyond the corner area

Facts used:

- Farthest point from the corner point = 144.60 ft (source: return 2 Q1(c))

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

Why the rule applies: ZR 23-344(a) waives the rear yard within 100 feet of the corner point; the far corner is 144.60 feet away, so part of the lot lies beyond that reach, where ZR 23-342 may require a rear yard on the interior-lot portion.

Expected value: not known. Within 100 feet of the corner point no rear yard is required; the far corner is 144.60 feet away, so part of the lot lies beyond, and what is required there is not settled. ZR 23-342 is now captured, but the depth it sets needs the building type and lot width (not given); the first and step-P1 readers did not have the ZR 12-10 side- and rear-lot-line definitions, and both step-P1 readings read it the same way. Those definitions were since captured (task M4-T029) and read in step P3 (cases/step-p3-worked.json), where both step-P3 readings read, beyond 100 feet of the 215 Place street line, a small portion of a side lot line deemed a rear lot line, with whether a rear yard is required there still not known.

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q1(c), and the work order's table C ('not known beyond the corner area'); confirmed by both step-P1 readings (return-independent-hand-calculation-3.md and -4.md, Q3a).

What this row does not establish: It does not give a rear-yard requirement beyond 100 feet of the corner point; that needs the neighbouring lot lines, the building type and lot width, and the ZR 12-10 lot-line definitions the earlier readers did not have (now captured and read in cases/step-p3-worked.json).

### C1-reach - C1 (40 ft x 100 ft, 4,000 sq ft): reach from each street line and the corner

Facts used:

- Lot = a made-up rectangle, 40 ft on street A by 100 ft on street B (source: chosen for this example)

Law relied on:

- none cited

Why the rule applies: For a rectangle, the farthest reach from street line A is the opposite (B) dimension and from street line B the A dimension; the farthest point from the corner is the diagonal.

Working, step by step:

- diagonal to the far corner: the square root of 40 (frontage on street A (ft)) squared plus 100 (frontage on street B (ft)) squared = 107.70

Expected value: farthest reach 100.00 ft from street line A and 40.00 ft from street line B, so the whole lot is within 100 ft of each street line; the diagonal to the far corner is 107.70 ft, so the whole lot is not within 100 ft of the corner point

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C1.

What this row does not establish: A made-up rectangle, not a real property.

### C1-coverage - C1: lot coverage for the whole lot

Facts used:

- Within 100 ft of each street line = yes (whole lot) (source: row C1-reach)

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

Why the rule applies: The whole lot is within 100 feet of each street line, so it is entirely the ZR 12-10 corner-lot portion, and ZR 23-362(a) gives corner lots 100 percent.

Expected value: 100 percent

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C1(i).

What this row does not establish: It relies on the captured ZR 12-10 corner-lot-portion definition; it is a made-up rectangle, not a real property.

### C1-rear-yard - C1: rear yard beyond the corner area

Facts used:

- Diagonal to the far corner = 107.70 ft (source: row C1-reach: beyond 100 ft of the corner point)

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

Why the rule applies: Within 100 feet of the corner no rear yard is required (ZR 23-344(a); 90 degrees is 135 or less); the diagonal is 107.70 feet, so part of the lot lies beyond 100 feet of the corner, where ZR 23-342 may require a rear yard on the interior-lot portion.

Expected value: not known. A part of the lot lies beyond 100 feet of the corner point (the diagonal is 107.70 feet), and whether a rear yard is required there is not settled. ZR 23-342 is now captured, but the depth it sets needs the building type and lot width (not given), and whether a yard is required there needs the neighbouring lot lines (not available).

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C1(ii).

What this row does not establish: It does not settle the rear yard beyond the corner area; that needs the neighbouring lot lines, the building type and lot width.

### C2-reach - C2 (60 ft x 80 ft, 4,800 sq ft): reach from each street line and the corner

Facts used:

- Lot = a made-up rectangle, 60 ft on street A by 80 ft on street B (source: chosen for this example)

Law relied on:

- none cited

Why the rule applies: The farthest reach from street line A is the B dimension and from street line B the A dimension; the farthest point from the corner is the diagonal.

Working, step by step:

- diagonal to the far corner: the square root of 60 (frontage on street A (ft)) squared plus 80 (frontage on street B (ft)) squared = 100.00

Expected value: farthest reach 80.00 ft from street line A and 60.00 ft from street line B, so the whole lot is within 100 ft of each street line; the diagonal to the far corner is 100.00 ft, exactly on the limit, so the whole lot is within 100 ft of the corner point

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C2.

What this row does not establish: A made-up rectangle, not a real property; the result turns on the diagonal being exactly 100 ft.

### C2-coverage - C2: lot coverage for the whole lot

Facts used:

- Within 100 ft of each street line = yes (whole lot) (source: row C2-reach)

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

Why the rule applies: The whole lot is within 100 feet of each street line, so it is entirely the ZR 12-10 corner-lot portion, and ZR 23-362(a) gives corner lots 100 percent.

Expected value: 100 percent

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C2(i).

What this row does not establish: It relies on the captured ZR 12-10 corner-lot-portion definition; it is a made-up rectangle, not a real property.

### C2-rear-yard - C2: rear yard

Facts used:

- Within 100 ft of the corner point = yes (whole lot; diagonal 100.00 ft) (source: row C2-reach)

Law relied on:

- ZR 23-344 (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less"

Why the rule applies: The whole lot is within 100 feet of the corner point (the diagonal is exactly 100.00 feet), so ZR 23-344(a) waives the rear yard over the entire lot.

Expected value: no rear yard required anywhere on the lot

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C2(ii): 'whole lot within 100 ft of the corner -> 23-344(a) waives it over the entire lot -> NO rear yard required anywhere. Fully settled by the packet.'

What this row does not establish: A made-up rectangle; the result holds because the diagonal is exactly 100 ft.

### C3-reach - C3 (150 ft x 100 ft, 15,000 sq ft): reach from each street line and the corner

Facts used:

- Lot = a made-up rectangle, 150 ft on street A by 100 ft on street B (source: chosen for this example)

Law relied on:

- none cited

Why the rule applies: The lot reaches 150 feet from street line B, 50 feet beyond the 100-foot corner-lot-portion limit; that 50-foot strip runs the length of the street-B frontage; the farthest point from the corner is the diagonal.

Working, step by step:

- width of the strip beyond the 100-foot limit: 150 (farthest reach from street line B (ft)) - 100 (corner-lot-portion limit (ft)) = 50
- area of the strip beyond the limit: 50 (strip width (ft)) x 100 (length of the street-B frontage (ft)) = 5,000
- diagonal to the far corner: the square root of 150 (frontage on street A (ft)) squared plus 100 (frontage on street B (ft)) squared = 180.28

Expected value: farthest reach 100.00 ft from street line A (within 100 ft) and 150.00 ft from street line B (a strip 50 ft wide, 5,000 sq ft, lies beyond 100 ft); the diagonal to the far corner is 180.28 ft, so the whole lot is not within 100 ft of the corner point

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C3.

What this row does not establish: A made-up rectangle, not a real property.

### C3-coverage - C3: lot coverage for the whole lot

Facts used:

- Strip beyond 100 ft of street line B = 50 ft wide, 5,000 sq ft (source: row C3-reach)

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

Why the rule applies: The near part within 100 feet of each street line is the corner-lot portion (100 percent), while the 50-foot strip beyond 100 feet of street line B is an interior-lot portion (80 percent); ZR 23-362 as captured does not partition the lot.

Expected value: not known. No single whole-lot coverage figure: the part within 100 feet of each street line is the corner-lot portion (100 percent) and the 50-foot strip beyond 100 feet of street line B is an interior-lot portion (80 percent). The captured ZR 23-362 does not partition the lot; the ZR 12-10 corner-lot-portion definition is now captured and both step-P1 readings read a 150-by-100 corner lot the same way (corner portion 100 percent, remaining interior 80 percent).

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C3(i); the step-P1 readings' lot C2 (150 by 100) reads the same (return-independent-hand-calculation-3.md and -4.md, Q2b; see cases/step-p1-worked.json).

What this row does not establish: It gives no single whole-lot coverage percentage.

### C3-rear-yard - C3: rear yard beyond the corner area

Facts used:

- Strip beyond 100 ft of street line B = 50 ft wide (source: row C3-reach)

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
- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "shall be provided on #interior lots# in accordance with this Section"

Why the rule applies: Within 100 feet of the corner no rear yard is required (ZR 23-344(a)); beyond 100 feet of the street line the side-lot-line portion is treated as a rear lot line (ZR 23-344(c)), and whether a rear yard is then required depends on whether that line coincides with a neighbour's lot line and, for any depth, on ZR 23-342.

Expected value: not known. Along the 50-foot strip beyond 100 feet of the street line, whether a rear yard is required depends on the neighbouring lot lines (ZR 23-344(c)(1) and (c)(3)), which are not available, so it is not known. Any required depth is set by ZR 23-342 (now captured) but depends on the building type and lot width, not given. Within 100 feet of the corner, ZR 23-344(a) waives it.

Where this stands in the independent reading: return-independent-hand-calculation-2.md, Q2 C3(ii).

What this row does not establish: It does not settle the rear yard along the strip beyond the corner-lot portion; that needs the neighbouring lot lines, the building type and lot width.

## What this case does not establish

- The real lot's reaches are measured from an approximate outline, not a survey; the strip and wedge areas are grid approximations.
- C1, C2 and C3 are made-up rectangles, not real properties.
- It relies on the ZR 12-10 corner-lot-portion definition (now captured, task M4-T025).
- It is not a professional or legal determination.

## Sources

- The independent hand-calculation, follow-up (tables C and D): provenance/return-independent-hand-calculation-2.md
- The independent hand-calculation, first round: provenance/return-independent-hand-calculation-1.md
- The two step-P1 readings that confirm the corner-portion and coverage rows from the newly captured text: provenance/return-independent-hand-calculation-3.md and provenance/return-independent-hand-calculation-4.md.
- The sealed folder given to the helper: the pinned ZR captures (without the notes describing how the program encoded them) and the lot's recorded official facts, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-06 | Case created from the independent hand-calculation returns (step R0). | rules-engineer (M4-T024) |
| 2026-10-07 | Rows real-lot-coverage, C1-coverage, C2-coverage and C3-coverage: expected values unchanged (real-lot-coverage and C3-coverage stay not known; C1-coverage and C2-coverage stay 100 percent). The ZR 12-10 corner-lot-portion definition is now captured (task M4-T025), so their citation changes from not-captured to the captured snapshot zr-12-10-lot-corner. The two step-P1 readings read the same corner-lot-portion method and the same per-portion 100/80 coverage (their own made-up corner lots are in cases/step-p1-worked.json). Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | Rows real-lot-rear-yard, C1-rear-yard and C3-rear-yard: expected values unchanged (not known beyond the corner). ZR 23-342 is now captured (task M4-T025); a captured ZR 23-342 citation is added and the reason records that the depth it sets needs the building type and lot width (not given) and the ZR 12-10 side-/rear-lot-line definitions are not captured. Reason: newly captured text. | rules-engineer (M4-T027) |
| 2026-10-07 | Row real-lot-rear-yard: expected value unchanged (not known beyond the corner). The ZR 12-10 side- and rear-lot-line definitions were captured by task M4-T029 and read independently in step P3 (cases/step-p3-worked.json); the row's wording is brought from 'not captured' into 'the readers did not have' form and points to the step-P3 reading, which both step-P3 readings support. Rows C1-rear-yard and C3-rear-yard are unchanged: the step-P3 readers worked a made-up 150-by-100 corner lot (recorded in cases/step-p3-worked.json), not a 40-by-100 corner lot, and neither C1-rear-yard nor C3-rear-yard carries 'not captured' wording. Reason: corrected evidence - the text is now captured and read. | rules-engineer (M4-T030) |

