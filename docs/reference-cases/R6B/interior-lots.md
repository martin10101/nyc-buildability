# Made-up interior lots (R6B, no overlay, standard residences)

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: B.

Four made-up interior lots in an R6B district with no overlay and standard residences, chosen to show the floor-area arithmetic and the dwelling-unit rounding threshold, plus the interior-lot coverage reading. Every value comes from the law text and the chosen lot sizes, never from a program run.

## What this case is worth

Prepared by an AI helper and recomputed by a second AI; their agreement alone is not proof. These are made-up lots, not a real property, and this is a draft reading of the law, not professionally reviewed. The floor-area and dwelling-unit sections were read from the captures and also on the official page on 2026-10-06 (ZR 23-22, 23-52, 23-362).

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of pinned law-text captures and the lot's recorded facts, with no access to the program.
- Checked by: A second AI recomputed the arithmetic and the geometry independently from the same sealed folder. Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| District | R6B | the example's stated district |
| Overlay | none | the example has no overlay |
| Residences | standard | the example uses standard residences |

## Rows

### P1-floor-area - Maximum residential floor area (2.00 x lot area)

Facts used:

- Floor area ratio for R6B standard residences = 2.00 (source: ZR 23-22, R6B row)
- Lot area (made up) = 5,000 sq ft (source: a chosen lot size for this example)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: A made-up R6B interior lot with standard residences; ZR 23-22 sets the floor area ratio for R6B at 2.00, and the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area: 2.00 (floor area ratio for R6B standard residences (ZR 23-22)) x 5,000 (lot area (made up, sq ft)) = 10,000

Expected value: 10,000 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P1: '5,000 | 10,000 sf'.

What this row does not establish: A made-up lot, to show the arithmetic and the unit-count threshold; it is not a real property.

### P1-units - Maximum dwelling units (floor area / 680)

Facts used:

- Maximum residential floor area = 10,000 sq ft (source: row P1-floor-area)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor 680; a fraction of three-quarters or more counts as one unit, otherwise it is dropped.

Working, step by step:

- maximum dwelling units: 10,000 (maximum residential floor area (sq ft), from row P1-floor-area) / 680 (dwelling-unit factor (ZR 23-52(b))) = 14.70...; a fraction below three-quarters is dropped -> 14

Expected value: 14 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P1.

What this row does not establish: A made-up lot; it shows the dwelling-unit rounding, not a real property's limit.

### P3-floor-area - Maximum residential floor area (2.00 x lot area)

Facts used:

- Floor area ratio for R6B standard residences = 2.00 (source: ZR 23-22, R6B row)
- Lot area (made up) = 5,350 sq ft (source: a chosen lot size for this example)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: A made-up R6B interior lot with standard residences; ZR 23-22 sets the floor area ratio for R6B at 2.00, and the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area: 2.00 (floor area ratio for R6B standard residences (ZR 23-22)) x 5,350 (lot area (made up, sq ft)) = 10,700

Expected value: 10,700 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P3: '5,350 | 10,700 sf'.

What this row does not establish: A made-up lot, to show the arithmetic and the unit-count threshold; it is not a real property.

### P3-units - Maximum dwelling units (floor area / 680)

Facts used:

- Maximum residential floor area = 10,700 sq ft (source: row P3-floor-area)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor 680; a fraction of three-quarters or more counts as one unit, otherwise it is dropped.

Working, step by step:

- maximum dwelling units: 10,700 (maximum residential floor area (sq ft), from row P3-floor-area) / 680 (dwelling-unit factor (ZR 23-52(b))) = 15.73...; a fraction below three-quarters is dropped -> 15

Expected value: 15 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P3.

What this row does not establish: A made-up lot; it shows the dwelling-unit rounding, not a real property's limit.

### P4-floor-area - Maximum residential floor area (2.00 x lot area)

Facts used:

- Floor area ratio for R6B standard residences = 2.00 (source: ZR 23-22, R6B row)
- Lot area (made up) = 5,360 sq ft (source: a chosen lot size for this example)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: A made-up R6B interior lot with standard residences; ZR 23-22 sets the floor area ratio for R6B at 2.00, and the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area: 2.00 (floor area ratio for R6B standard residences (ZR 23-22)) x 5,360 (lot area (made up, sq ft)) = 10,720

Expected value: 10,720 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P4: '5,360 | 10,720 sf'.

What this row does not establish: A made-up lot, to show the arithmetic and the unit-count threshold; it is not a real property.

### P4-units - Maximum dwelling units (floor area / 680)

Facts used:

- Maximum residential floor area = 10,720 sq ft (source: row P4-floor-area)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor 680; a fraction of three-quarters or more counts as one unit, otherwise it is dropped.

Working, step by step:

- maximum dwelling units: 10,720 (maximum residential floor area (sq ft), from row P4-floor-area) / 680 (dwelling-unit factor (ZR 23-52(b))) = 15.76...; a fraction of three-quarters or more counts as one dwelling unit -> 16

Expected value: 16 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P4.

What this row does not establish: A made-up lot; it shows the dwelling-unit rounding, not a real property's limit.

### P5-floor-area - Maximum residential floor area (2.00 x lot area)

Facts used:

- Floor area ratio for R6B standard residences = 2.00 (source: ZR 23-22, R6B row)
- Lot area (made up) = 5,355 sq ft (source: a chosen lot size for this example)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum residential floor area ratio shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: A made-up R6B interior lot with standard residences; ZR 23-22 sets the floor area ratio for R6B at 2.00, and the maximum residential floor area is that ratio times the lot area.

Working, step by step:

- maximum residential floor area: 2.00 (floor area ratio for R6B standard residences (ZR 23-22)) x 5,355 (lot area (made up, sq ft)) = 10,710

Expected value: 10,710 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P5: '5,355 | 10,710 sf'.

What this row does not establish: A made-up lot, to show the arithmetic and the unit-count threshold; it is not a real property.

### P5-units - Maximum dwelling units (floor area / 680)

Facts used:

- Maximum residential floor area = 10,710 sq ft (source: row P5-floor-area)
- Dwelling-unit factor = 680 (source: ZR 23-52(b))

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable dwelling unit factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one dwelling unit"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor 680; a fraction of three-quarters or more counts as one unit, otherwise it is dropped. Lot P5 is the threshold case: 10,710 / 680 = 15.75 exactly, and a fraction equal to three-quarters counts as one unit, so it rounds up to 16.

Working, step by step:

- maximum dwelling units: 10,710 (maximum residential floor area (sq ft), from row P5-floor-area) / 680 (dwelling-unit factor (ZR 23-52(b))) = 15.75; a fraction of three-quarters or more counts as one dwelling unit -> 16

Expected value: 16 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 table, row P5.

What this row does not establish: A made-up lot; it shows the dwelling-unit rounding, not a real property's limit.

### interior-coverage - Maximum lot coverage for an interior lot

Facts used:

- Lot type = interior (made up) (source: a chosen interior lot for this example)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum residential lot coverage for interior lots or through lots shall be 80 percent and the maximum residential lot coverage for corner lots shall be 100 percent"

Why the rule applies: ZR 23-362(a) gives interior and through lots a maximum residential lot coverage of 80 percent.

Expected value: 80 percent

Where this stands in the independent reading: return-independent-hand-calculation-1.md, Task 2 ('80% -> 4,000 sf' for the interior probe), and the work order's table B note that the independent reading gives 80 percent from ZR 23-362(a).

What this row does not establish: ZR 23-363 may change the 80 percent for some interior and through lots and is not captured; a different maximum also applies to lots of 30,000 sq ft or more.

## What this case does not establish

- These lots are made up; they do not describe any real property.
- The 80-percent coverage may be changed by ZR 23-363 (not captured) and does not apply to lots of 30,000 sq ft or more.
- It is not a professional or legal determination.

## Sources

- The independent hand-calculation, first round: provenance/return-independent-hand-calculation-1.md
- The sealed folder given to the helper: the pinned ZR captures (without the notes describing how the program encoded them) and the lot's recorded official facts, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-06 | Case created from the independent hand-calculation returns (step R0). | rules-engineer (M4-T024) |

