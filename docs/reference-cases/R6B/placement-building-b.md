# The two independent readings of where the three-storey Building B sits on lot 70 of block 7334 (215-16 Northern Boulevard, Queens) under Z1 (lot 70 alone) and how its floor area divides, written into the R6B reference cases as one case: the plate as zoning floor area per storey, the footprint on the printed-tax-map basis reconciled with the plate, the placement and offsets on that basis with the city-map (GIS) outline as a conflict check only, the lot coverage and rear yard as far as both readings take them, and the area allocation at the one stated 60 percent apartment-area share - a value only where both readings agree on the same basis

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: D-094 R043, R044, R076, R082, R091, R092; work order D-094 v3, task M5-T177; the footprint, placement and area allocation of Building B worked independently from source facts and quoted law before the report, the drawing (M5-T173) and the engine (M5-T172) consume it.

The footprint, placement and area allocation of the three-storey Building B (20,150 sq ft zoning floor area, 10-ft floor-to-floor) on lot 70 of block 7334, read independently in step P8 by two AI helpers working alone from a sealed folder (the 189 pinned law captures without their notes, the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, the stated facts of Building B and the stated measure, and eighteen answers settled by earlier readings - the earlier footprint answer real-building-b left out on purpose), with no access to the program, the repository or the web. It records the plate as zoning floor area per storey (20,150 / 3 = 6,716.67), the footprint on the printed-tax-map basis (100.76 x 66.66 = 6,716.66) reconciled with the plate within the readers' +/- 0.5 sq ft, the placement and offsets under Z1 on that basis with the city-map (GIS) outline used only as a conflict check, the lot coverage (maximum by portion) and the rear yard as far as both readings take them, and the area allocation at the one stated 60 percent apartment-area share. A value or figure is recorded only where both readings give it on the same words and the same basis; every disagreement or unresolved basis stays not settled, naming both readings and the kind of its gap (a missing fact about the property, or unresolved law). The placement is an illustration, not a design; the plate is zoning floor area per storey, no gross-up, exclusions or wall-thickness conversion worked, and the physical floor plate is not checked. No value comes from a program run; no human verdict is entered; a tax lot is not a zoning lot; every quantity carries exactly one of the nine measurement bases and no two bases are mixed in one figure.

## What this case is worth

Read independently by two AI helpers, each working alone from the sealed step-P8 folder (reading 1 a geospatial-engineer, reading 2 a scenario-optimization-engineer); their agreement alone is not proof. It is a draft reading of the law and an illustrative placement by an AI helper, not professionally reviewed, and is not a statement that anything complies, is buildable, is optimal or is feasible. A second AI read the same sealed folder and worked the same questions. Where the two readings differ, where one says not known, or where the captured text does not settle a point, the row says so and names both readings and the kind of its gap. The placement, the lot coverage and the rear yard stay conditional on the measurement basis, the zoning lot (Z1) and the neighbouring lots' records, which no reading had.

- Prepared by: An AI helper (a geospatial-engineer) that took no part in writing the program's rules, working only from a sealed folder - the 189 pinned law-text captures (without their notes), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, the stated facts of Building B and the stated measure, and eighteen answers settled by earlier readings (the earlier footprint answer real-building-b left out on purpose) - with no access to the program (reading 1: provenance/return-independent-hand-calculation-17.md).
- Checked by: A second, independent AI (a scenario-optimization-engineer) read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-18.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Real lot | 215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070): a corner lot of Northern Boulevard and 215 Place, R6B with a C2-2 overlay | the readers' lot facts and cases/real-lot.json |
| Building B | a stated three-storey all-residential building: 20,150 sq ft zoning floor area, 10-ft floor-to-floor, 30 ft high | building_b_and_the_stated_measure.json (stated facts) |
| The stated measure | plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked; the physical floor plate is not checked | building_b_and_the_stated_measure.json (verbatim) |
| The one stated share | 60 percent apartment area, the low end of a 60-75% assumption, applied to the proposed building's residential floor area | building_b_and_the_stated_measure.json (M0-T193 item 9; share_low 0.60) |
| The placement basis (A1) | place Building B on the printed-tax-map basis; the city-map (GIS) outline is a conflict check only | building_b_and_the_stated_measure.json (stated placement rule) |
| Z1 | lot 70 alone is the zoning lot (whether lots 1 and 70 are one zoning lot is not known) | building_b_and_the_stated_measure.json (stated condition) |
| Eighteen settled answers | eighteen answers settled by earlier readings, given to the step-P8 readers as settled (copied word for word, not re-worked); the earlier footprint answer real-building-b was left out on purpose | settled_by_earlier_readings.json; the step-p3-worked, corner-reach, step-p4-worked, step-p6-worked and short-block-rear-yard reference-case rows |

## Rows

### plate - The plate (zoning floor area per storey): 20,150 sq ft zoning floor area / 3 storeys

Facts used:

- Building B zoning floor area = 20,150 sq ft (source: building_b_and_the_stated_measure.json (stated; = 2.00 FAR x 10,075 recorded lot area per settled step-p6-worked#real-lot-recorded-vs-measured-area))
- Storeys = 3 (source: building_b_and_the_stated_measure.json (stated))
- The stated measure = plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked; the physical floor plate is not checked (source: building_b_and_the_stated_measure.json (the stated measure, verbatim))

Law relied on:

- none cited

Why the rule applies: The stated measure defines the plate as the building's zoning floor area divided by the number of storeys; it is a stated design input, not a rule calculation, so no law governs the division.

Working, step by step:

- Plate per storey: 20,150 (zoning floor area) / 3 (storeys) = 6,716.67 (rounded to two decimal places)

Expected value: 6,716.67 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q2 (20,150 / 3 = 6,716.67); return-independent-hand-calculation-18.md Q2 (20,150 / 3 = 6,716.67); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked; the physical floor plate is not checked (see physical-plate-not-checked). It is not a dwelling-unit count and establishes no compliance or feasibility. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Plate (zoning floor area per storey) = 6,716.67 sq ft (basis: derived).

### physical-plate-not-checked - The physical floor plate (gross-up, exclusions, wall thickness)

Facts used:

- The stated measure = the physical floor plate is not checked (source: building_b_and_the_stated_measure.json (the stated measure, verbatim))

Law relied on:

- none cited

Why the rule applies: The stated measure records the plate only as zoning floor area per storey and states the physical floor plate (gross-up, exclusions, wall thickness) is not checked; neither reading worked a physical plate.

Expected value: not known. Not known. Both readings record the plate only as zoning floor area per storey (20,150 / 3 = 6,716.67) and neither worked the physical floor plate: no gross-up, no excluded areas and no wall-thickness conversion (plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked). KIND OF GAP: a missing fact about the property - the gross-up factor, the areas excluded from floor area and the wall thicknesses, which would come from an architectural floor plan.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q2/Part 3 (physical plate not checked); return-independent-hand-calculation-18.md Q2 (physical plate not checked); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It records that the physical floor plate is not checked; it is not a statement about any plan. A draft reading by AI helpers, not professionally reviewed.

### footprint-tax-map - The footprint figure on the printed-tax-map basis: 100.76 ft frontage x 66.66 ft plan depth = 6,716.66 sq ft, reconciled with the plate

Facts used:

- Tax-map frontage (lot 70 on Northern Boulevard) = 100.76 ft (source: printed_tax_map_labels.json (= PLUTO lotfront))
- Tax-map depth = 100 ft (source: printed_tax_map_labels.json (= PLUTO lotdepth))
- The plate = 6,716.67 sq ft (zoning floor area per storey) (source: this case, row plate)

Law relied on:

- none cited

Why the rule applies: The stated placement makes the footprint a rectangle as wide as the full Northern Boulevard frontage and as deep as the plate needs; the depth and the footprint follow by arithmetic from the tax-map frontage and the plate.

Working, step by step:

- Plan depth the plate needs: 6,716.6667 (plate (zoning floor area per storey)) / 100.76 (tax-map frontage) = 66.66 (rounded to two decimal places)
- Footprint (rounded plan depth x frontage): 66.66 (plan depth) x 100.76 (tax-map frontage) = 6,716.66 (rounded to two decimal places)

Expected value: 6,716.66 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q3 (66.66 ft; 66.66 x 100.76 = 6,716.66, 0.01 under the plate); return-independent-hand-calculation-18.md Q3 (66.66 ft; 66.66 x 100.76 = 6,716.66, 0.01 under the plate); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked. The footprint figure (6,716.66) and the plate (6,716.67) are separate quantities, each on its own exact recompute, reconciled within the readers' +/- 0.5 sq ft tolerance (0.01 sq ft apart) and never forced into one figure. It is not a physical floor plate and establishes no compliance. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Plan depth (printed-tax-map basis) = 66.66 ft (basis: derived).
- Tax-map frontage = 100.76 ft (basis: printed_tax_map).
- Footprint (printed-tax-map basis) = 6,716.66 sq ft (basis: derived).
- Plate (zoning floor area per storey) = 6,716.67 sq ft (basis: derived).

### placement-tax-map - The placement on the printed-tax-map basis (A1) under Z1 (lot 70 alone): the lot lines the footprint touches and the offsets

Facts used:

- Lot 70's lot lines = corner lot: two front lot lines (Northern Boulevard, 215 Place), two side lot lines, no rear lot line (source: settled step-p3-worked#real-lot-lot-lines (given to the readers as settled))
- Tax-map frontage x depth = 100.76 ft x 100 ft (source: printed_tax_map_labels.json)
- Z1 = lot 70 alone is the zoning lot (source: building_b_and_the_stated_measure.json (stated condition; whether lots 1 and 70 are one zoning lot is not known))
- The placement = wall on the Northern Boulevard street line for the full frontage, one corner at the street-line intersection, one wall along 215 Place, depth = the plate's depth (source: the stated design choice (building_b_and_the_stated_measure.json))

Law relied on:

- ZR 23-322 (Front yard requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-322`, file `docs/research/zr-snapshots/v1/zr-23-322.snapshot.json`.
  - Content digest: `2a5af75847b73f8238936cbc9818eef0b76102e588be741254604d0a2d8c2c3e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322.
  - Quoted: "In the districts indicated, no #front yard# requirements shall apply."
- ZR 23-335 (Side yard requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-335`, file `docs/research/zr-snapshots/v1/zr-23-335.snapshot.json`.
  - Content digest: `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335.
  - Quoted: "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."

Why the rule applies: The stated placement puts the building on the street lines; the settled lot-lines reading fixes which lines are front, side and that there is no rear lot line; ZR 23-322 permits standing on the street line (no front yard) and ZR 23-335(b) sets the five-foot minimum for any open area along a side lot line.

Working, step by step:

- Clearance to the lot line opposite Northern Boulevard: 100 (tax-map depth) - 66.66 (building depth) = 33.34

Expected value: On the printed-tax-map basis, under Z1 (lot 70 alone), the footprint touches three of the four lot lines at 0 ft: the Northern Boulevard front lot line (the full 100.76 ft), the 215 Place front lot line (for the 66.66 ft depth) and the side lot line shared with lot 1 (for the 66.66 ft depth). It clears the back side lot line opposite Northern Boulevard by 33.34 ft (100 - 66.66), leaving a back open strip 100.76 ft x 33.34 ft, wider than the five feet that any open area along a side lot line must have (ZR 23-335(b)). It stands on the street lines, which ZR 23-322 permits (no front yard required). This is an illustrative placement on the printed-tax-map basis, not a design and not a compliance finding.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q3/Q4 (touches NB, 215 Place and the lot-1 side line at 0 ft; 33.34 ft to the back line); return-independent-hand-calculation-18.md Q3/Q4 (same touches; 33.34 ft to the back line); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It is an illustrative placement on the printed-tax-map basis under Z1 (lot 70 alone); it is not a design, not a dwelling layout and not a finding that the building complies, is buildable or is feasible. The city-map (GIS) outline gives different offsets (see gis-conflict-check). A tax lot is not a zoning lot. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Clearance to the lot line opposite Northern Boulevard = 33.34 ft (basis: derived).
- Touch along the Northern Boulevard front lot line = 0 ft (basis: derived).
- Touch along the 215 Place front lot line = 0 ft (basis: derived).
- Touch along the lot-1 side lot line = 0 ft (basis: derived).

### gis-conflict-check - Conflict check: the city-map (GIS) outline figures beside the printed-tax-map figures (used only as a conflict check, never mixed)

Facts used:

- GIS lot-70 outline = EPSG:2263 ring; measured area 10,387.99 sq ft (source: block_7334_lot_outlines_epsg2263.json)
- Tax-map rectangle = 100.76 ft x 100 ft = 10,076 sq ft (source: printed_tax_map_labels.json / derived)

Law relied on:

- none cited

Why the rule applies: The stated placement basis (A1) is the printed tax map; the city-map (GIS) outline is used only as a conflict check. The two outlines disagree on the frontage and the area, so the derived figures differ; the folder holds no survey or deed to choose between them.

Working, step by step:

- Frontage conflict (GIS - tax map): 103.88 (GIS Northern Boulevard frontage) - 100.76 (tax-map frontage) = 3.12
- Plan-depth conflict (tax map - GIS): 66.66 (tax-map plan depth) - 64.66 (GIS plan depth) = 2.00
- Back-clearance conflict (GIS - tax map): 35.31 (GIS back clearance) - 33.34 (tax-map back clearance) = 1.97

Expected value: not known. Not known as a single figure. On the printed-tax-map basis the Northern Boulevard frontage is 100.76 ft, the depth 100 ft, the plan depth 66.66 ft, the clearance to the back line 33.34 ft and the footprint share 66.66 percent of the 10,076 sq ft tax rectangle. On the city-map (GIS) outline the frontage is 103.88 ft (+3.12), the depth back from Northern Boulevard 99.97 ft (-0.03), the plan depth 64.66 ft (-2.00), the clearance to the back line 35.31 ft (+1.97) and the footprint share 64.66 percent of the 10,387.99 sq ft outline (-2.0 percentage points); the three touching distances stay 0 ft on both bases. The two bases are not reconciled into one figure and neither reading chooses between them. KIND OF GAP: a missing fact about the property - the folder holds no survey or deed to resolve the about 3.1 ft frontage and about 313 sq ft area conflict (10,075 recorded / 10,076 tax rectangle / 10,387.99 GIS); a surveyed outline would settle it.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q5 (GIS frontage 103.88, depth 99.97, plan depth 64.66, back clearance 35.31, share 64.66%); return-independent-hand-calculation-18.md Q5 (GIS frontage 103.879 -> 103.88 to the hundredth, depth 99.97, plan depth 64.66, back clearance 35.31, share 64.66%); both show the two bases side by side and neither chooses between them; both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: The conflict check never mixes two bases in one figure and chooses no basis; it does not resolve which outline is correct. A tax lot is not a zoning lot. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- GIS Northern Boulevard frontage = 103.88 ft (basis: gis).
- GIS depth back from Northern Boulevard = 99.97 ft (basis: gis).
- GIS measured lot area = 10,387.99 sq ft (basis: gis).
- GIS plan depth the plate needs = 64.66 ft (basis: derived).
- GIS clearance to the back line = 35.31 ft (basis: derived).
- GIS footprint share of the outline = 64.66 % (basis: derived).
- Tax-map footprint share of the tax rectangle = 66.66 % (basis: derived).

### lot-coverage-max - The maximum residential lot coverage for this corner lot, by portion

Facts used:

- Lot type = corner lot (source: settled step-p3-worked#real-lot-lot-lines)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."
- ZR 12-10 (Definition: corner lot (the corner portion)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."

Why the rule applies: ZR 23-362(a) sets the maximum residential lot coverage (80 percent for interior or through lots, 100 percent for corner lots); the ZR 12-10 corner-lot definition fixes which portion of a corner lot is the corner portion and which is left for interior or through treatment.

Expected value: On the printed-tax-map basis, under Z1 (lot 70 alone), the maximum residential lot coverage is read by portion: 100 percent for the corner-lot portion (the part within 100 feet of both street lines, ZR 23-362(a) with the ZR 12-10 corner-lot definition) and 80 percent for any remaining interior or through portion (the strip beyond 100 feet of the 215 Place street line). It is not a single whole-lot percentage (see lot-coverage-whole-lot).

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q1d/Q4d; return-independent-hand-calculation-18.md Q1d/Q4d; both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It states the permitted maxima by portion; it is not the lot's actual coverage (see lot-coverage-whole-lot) and no finding that the placement complies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Corner-lot portion maximum = 100 % (basis: law).
- Interior/through portion maximum = 80 % (basis: law).

### lot-coverage-whole-lot - The real lot's whole-lot residential lot coverage under Z1

Facts used:

- Footprint = 6,716.66 sq ft (printed-tax-map basis) (source: this case, row footprint-tax-map)
- Conflicting lot areas = 10,075 recorded (PLUTO) / 10,076 tax rectangle / 10,387.99 GIS (source: pluto_rows_lots_70_and_1.json; printed_tax_map_labels.json; block_7334_lot_outlines_epsg2263.json)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."

Why the rule applies: ZR 23-362(a) with the ZR 12-10 corner-lot definition makes the maximum a per-portion maximum, not a whole-lot figure; the footprint's whole-lot share depends on which lot area governs, and the folder's recorded, tax-rectangle and GIS areas conflict.

Expected value: not known. Not known as a single whole-lot figure, on the printed-tax-map basis under Z1 (lot 70 alone). Both readings read the coverage by portion, not as one percentage, following the settled step-p6-worked#real-lot-coverage-by-portion (the two earlier readers' outline measurements differ). The footprint share itself is per basis: 66.66 percent of the 10,076 sq ft tax rectangle (both readings) and 64.66 percent of the 10,387.99 sq ft GIS outline; reading 2 also gives 66.67 percent of the 10,075 sq ft recorded lot area, a basis reading 1 does not use. KIND OF GAP: a missing fact about the property - a surveyed outline to resolve the conflicting lot areas (10,075 recorded / 10,076 tax rectangle / 10,387.99 GIS), which the folder does not fix.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q4d (66.66% of 10,076); return-independent-hand-calculation-18.md Q4d (66.67% of 10,075; 66.66% of 10,076); both read the coverage by portion and leave the whole-lot figure not known; both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It records that the whole-lot coverage is not known as a single figure; it chooses no lot area. A tax lot is not a zoning lot. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Footprint share of the tax rectangle = 66.66 % (basis: derived).
- Footprint share of the GIS outline = 64.66 % (basis: derived).

### rear-yard - The rear yard for Building B on lot 70 under Z1

Facts used:

- Lot 70 has no rear lot line = corner lot, no rear lot line (source: settled step-p3-worked#real-lot-lot-lines)
- Z1 = lot 70 alone is the zoning lot (source: building_b_and_the_stated_measure.json)
- Settled Z1 rear-yard reading = not known (source: settled short-block-rear-yard#real-lot-z1-rear-yard)

Law relied on:

- ZR 23-344(a) (Additional rear yard modifications (within 100 feet of corners)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less."
- ZR 23-344(c) (Additional rear yard modifications (the deemed rear lot line)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line#"

Why the rule applies: ZR 23-344 modifies the rear-yard requirement on corner lots; its (a), (b) and (c) turn on the measurement basis, the short-dimension question and the adjoining lot-line kind, which the readers could not fix for lot 70 under Z1.

Expected value: not known. Not known under Z1 (lot 70 alone), on the printed-tax-map basis. Both readings carry the settled step-p7 reading short-block-rear-yard#real-lot-z1-rear-yard, which is not known: on the street-line/tax-map basis the Northern Boulevard frontage is read as a short dimension of a block, so ZR 23-344(b) waives the rear yard within 100 feet of the Northern Boulevard street line; on the centreline basis the result rests on ZR 23-344(a) (no rear yard within 100 feet of the roughly 90-degree corner), the settled no-rear-lot-line finding and ZR 23-344(c) for the strip beyond 100 feet. The stated placement is only 66.66 feet deep from Northern Boulevard, so it lies within 100 feet of that street line; but the building spans the full frontage and sits on the side lot line opposite 215 Place, the portion of which beyond 100 feet of the 215 Place street line is deemed a rear lot line (ZR 23-344(c)), and whether the building may touch there turns on the adjoining zoning lot's lot-line kind. KIND OF GAP: unresolved law (the governing measurement basis, see gis-conflict-check) and a missing fact about the property (the adjoining zoning lot's lot-line kind, from a survey, a deed or the neighbouring lots' records). No unconditional 'no rear yard' is recorded: every reading above names its basis and its conditions and quotes ZR 23-344.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q1c/Q4c (carries settled short-block-rear-yard#real-lot-z1-rear-yard; the placement assumes no rear yard constrains the 66.66 ft footprint, the deemed-rear-lot-line touch not known); return-independent-hand-calculation-18.md Q1c/Q4c (same); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It records the rear yard as not known under Z1 and enters no unconditional 'no rear yard'; it is not a finding that the placement complies. A tax lot is not a zoning lot. A draft reading by AI helpers, not professionally reviewed.

### area-allocation - The area allocation at the one stated 60 percent apartment-area share: apartment area and other building area, per storey and in total

Facts used:

- Zoning floor area (all residential) = 20,150 sq ft (= residential floor area) (source: building_b_and_the_stated_measure.json)
- The one stated share = 60 percent apartment area (the low end of a 60-75% assumption; an assumption, not a measurement) (source: building_b_and_the_stated_measure.json (the stated share; M0-T193 item 9))

Law relied on:

- none cited

Why the rule applies: The stated measure makes the allocation a stated share of the building's residential floor area; it is a stated design assumption, not a rule calculation, so no law governs the split.

Working, step by step:

- Apartment area, total: 20,150 (zoning floor area) x 0.60 (stated apartment share) = 12,090.00 (rounded to two decimal places)
- Other building area, total (= total - apartment): 20,150 (zoning floor area) - 12,090 (apartment area total) = 8,060.00 (rounded to two decimal places)
- Apartment area, per storey: 12,090 (apartment area total) / 3 (storeys) = 4,030.00 (rounded to two decimal places)
- Other building area, per storey: 8,060 (other building area total) / 3 (storeys) = 2,686.67 (rounded to two decimal places)

Expected value: At the one stated 60 percent apartment-area share, applied to the proposed building's residential floor area (all residential, so the 20,150 sq ft zoning floor area): apartment area 12,090.00 sq ft in total and 4,030.00 sq ft per storey; other building area (core, circulation, walls, services) 8,060.00 sq ft in total and 2,686.67 sq ft per storey. Apartment plus other equals the total (12,090.00 + 8,060.00 = 20,150.00) and the per-storey figures sum to the plate (4,030.00 + 2,686.67 = 6,716.67). The 60 percent is a stated assumption, not a measurement.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q6 (12,090 / 4,030; 8,060 / 2,686.67); return-independent-hand-calculation-18.md Q6 (12,090 / 4,030; 8,060 / 2,686.67); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It is an illustration at one stated assumption; it establishes no dwelling-unit count, no net or rentable area, no physical floor plate, no layout, and no compliance or feasibility. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Apartment area, total = 12,090.00 sq ft (basis: derived).
- Other building area, total = 8,060.00 sq ft (basis: derived).
- Apartment area, per storey = 4,030.00 sq ft (basis: derived).
- Other building area, per storey = 2,686.67 sq ft (basis: derived).

### both-readers-did-not-have - The texts both readers did not have (pointed to by the law they used), and what stays conditional

Facts used:

- The texts the readers did not have = compiled from both readings' Q7 (source: return-independent-hand-calculation-17.md Q7 and return-independent-hand-calculation-18.md Q7)

Law relied on:

- none cited

Why the rule applies: A list headed 'both readers did not have' holds only a text that both readings say they did not have; where only one reading names a missing text, it is recorded with that reading named, not on the joint list.

Expected value: Both readings worked from the same sealed folder, and there is no text that both readings say they did not have, so the joint list is empty. The per-reading observations are: reading 2 names the 'outer court' definition, the Mandatory Inclusionary Housing and UAP terms, and the New York City Administrative Code as not in the folder (each not load-bearing for this flush-wall placement); reading 1 names no text as outside the folder, and instead marks ZR 23-341, ZR 23-343 and ZR 23-434 as in the folder but not read by reading 1, and takes the prevailing-street-wall-frontage definition from the settled sheet. The short-dimension-of-a-block definition is in the folder and was not read by reading 1 for a quote. Each such text is recorded with the reading that named it; none is on the joint 'both readers did not have' list.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q7 (names no text as outside the folder; marks ZR 23-341/23-343/23-434 not read); return-independent-hand-calculation-18.md Q7 (names outer court, MIH/UAP, the Administrative Code as not in the folder); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It lists per-reading missing-text observations and keeps the joint list to texts both readings name, which here is none; it is about texts, not facts (see real-lot-missing-facts). A draft reading by AI helpers, not professionally reviewed.

### real-lot-missing-facts - The facts about the real lot that both readings did not have, and the kind of each gap

Facts used:

- The missing facts = compiled from both readings' Q7 (source: return-independent-hand-calculation-17.md Q7 and return-independent-hand-calculation-18.md Q7)

Law relied on:

- none cited

Why the rule applies: The placement, the lot coverage and the rear yard each turned on a fact about the real lot that the readers did not have; each gap is a missing fact about the property.

Expected value: Both readings record the same missing facts about the real lot, each a missing fact about the property: (1) no survey, deed or zoning-lot description for lot 70 or any neighbour, so the adjoining zoning lot's lot-line kind for ZR 23-344(c) is not known and the Z1 zoning-lot identity is a stated condition, not a fact; (2) the printed-tax-map rectangle (10,076 sq ft), the recorded PLUTO lot area (10,075 sq ft) and the GIS-measured outline (10,387.99 sq ft) conflict by about 313 sq ft, which a surveyed outline would settle; (3) no ground elevations, base plane or curb level, so any height-from-base-plane check is unverifiable (nothing here turned on it, the building being below the base height). Reading 1 also records (reading 1) that whether a Commercial District is mapped along the entire 215 Place block frontage is not known; reading 2 also records (reading 2) the surveyed corner angle and the block's south-west / ALLEY edge as not known.

Where this stands in the independent reading: return-independent-hand-calculation-17.md Q7; return-independent-hand-calculation-18.md Q7 (both record these missing facts); both readings on the same basis (both readings: return-independent-hand-calculation-17.md and return-independent-hand-calculation-18.md).

What this row does not establish: It lists missing facts; it fills none with a guess or a typical value. A draft reading by AI helpers, not professionally reviewed.

## What this case does not establish

- It records a value or figure only where both readings agree on the same words and the same basis; where they differ, where one says not known, or where the captured text does not settle a point, the row says so, names both readings and states the kind of its gap.
- The placement is an illustration on the printed-tax-map basis under Z1 (lot 70 alone), not a design and not a dwelling layout; no row reads as 'complies', 'buildable', 'optimal' or 'feasible', and no human verdict is entered.
- The plate is zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion is worked, and the physical floor plate is not checked; the footprint figure and the plate are separate quantities each on its own exact recompute, reconciled within the readers' +/- 0.5 sq ft and never forced into one figure.
- The city-map (GIS) outline is used only as a conflict check; the two bases are never mixed in one figure and no reading chooses between them; the lot coverage (whole lot) and the rear yard stay not known; a tax lot is not a zoning lot.
- Every quantity carries exactly one of the nine measurement bases and no two bases are mixed in one figure; no value comes from a program run; agreement between two AI readings is not proof; it is not a professional or legal determination.

## Sources

- The step-P8 reading 1: provenance/return-independent-hand-calculation-17.md
- The step-P8 reading 2: provenance/return-independent-hand-calculation-18.md
- The sealed folder given to each helper (sealed-p8 on the private build server): the 189 pinned law-text captures (without the notes describing how the program encoded them), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, the stated facts of Building B and the stated measure, and eighteen answers settled by earlier readings (copied word for word and given as settled; the earlier footprint answer real-building-b left out on purpose), with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-14 | Case created (step P8, task M5-T177) from the two independent readings of the step-P8 sealed folder (provenance/return-independent-hand-calculation-17.md and -18.md): the footprint, placement and area allocation of Building B on lot 70 under Z1. A value is recorded only where both readings agree on the same basis; every disagreement or unresolved basis stays not settled with the kind of its gap. The plate is zoning floor area per storey (no physical-plate conversion worked); placement is on the printed-tax-map basis with the city-map outline a conflict check only; the area allocation uses the one stated 60 percent apartment-area share. No value comes from a program run; no human verdict is entered. | rules-engineer (M5-T177) |

