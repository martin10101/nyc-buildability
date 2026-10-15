# The agreed worked values of options 2 (qualifying affordable housing), 3 (qualifying senior housing), 6 (residences with a community facility) and 7 (a community facility alone) for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner), read independently twice per option and confirmed by an independent comparer - a value only where both readings agree on the same value and the same basis and the cited section is captured

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: D-094 R007, R075, R084, R102; task M5-T184. The worked values of options 2, 3, 6 and 7 on the benchmark lot, from two independent readings per option plus an independent comparer, as the single source the report, the option comparison and any later engine take their expected values from (never from a program run); options 5, 8 and 9-10 are named as owed..

The worked values of four of the eleven development options for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner lot; recorded lot area 10,075 sq ft, administrative_record; the GIS outline 10,387.99 sq ft is display-only and never mixed into a floor-area figure). Each option was read independently by two AI helpers (option 2: provenance -19 and -20; option 3: -21 and -22; options 6 and 7: -23 and -24) and the three reading pairs were checked by an independent comparer (-25). A value or figure is recorded only where both readings of that option give it on the same value and the same basis, confirmed by the comparer, and the cited section is captured in docs/research/zr-snapshots/v1; where they differ, where one says not known, or where the captured text does not settle a point, the row stays not known with the kind of its gap. No row decides eligibility (qualifying affordable or senior housing, or community-facility use permission); every option-2 and option-3 figure is worked on the assumption that the building qualifies. No value comes from a program run; no human verdict is entered; a tax lot is not a zoning lot; every quantity carries exactly one of the nine measurement bases and no two bases are mixed in one figure. The settled values include option 2's maximum residential floor area 24,180 sq ft (2.40 x 10,075), the 4,030 sq ft of affordable floor area a UAP development needs to reach 2.40, heights 30/45/65 ft and 35 dwelling units; option 3's 24,180 sq ft, 30/45/65 ft and the removal of the 680 dwelling-unit factor; and options 6 and 7's community-facility FAR 2.00 / 20,150 sq ft, coverage 80/60, heights 30/45/55 ft, and the yard and combination rules. Options 5, 8 and 9-10 rest on sections not yet captured and wait for capture task M3-T010; they are out of this task.

## What this case is worth

Read independently by two AI helpers per option (a first reading and a second AI reading of each option) and confirmed by a third, independent comparer; their agreement alone is not proof. It is a draft reading of the law by AI helpers, not professionally reviewed, and is not a statement that anything complies, is buildable, is optimal or is feasible. Each reader had read access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law captures, the settled reference cases, the evidence records and the law library), read no program output, and some readers read official Zoning Resolution pages live; the comparer read both readings and opened the captures and official pages. Where the two readings of an option differ, where one says not known, or where the captured text does not settle a point, the row says so and names both readings and the kind of its gap. Every value stays conditional on the zoning lot (Z1), the lot-area basis and eligibility, which no reading decided.

- Prepared by: Three AI helpers that took no part in writing the program's rules read the options from a detached, read-only checkout of this repository at commit bb5c02b9 (reading A of each option family): option 2 reading A (provenance/return-independent-hand-calculation-19.md), option 3 reading A (-21.md) and options 6-7 reading A (-23.md). Each read no program output; some read official Zoning Resolution pages live.
- Checked by: A second, independent AI read each option family (reading B: option 2 -20.md, option 3 -22.md, options 6-7 -24.md), and an independent comparer read all three pairs and opened the captures and official pages (-25.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Benchmark lot | 215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070): a corner lot of Northern Boulevard (wide) and 215 Place (narrow), R6B with a C2-2 overlay | the readers' lot facts and settled reference case real-lot.json |
| Recorded lot area | 10,075 sq ft | NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04) |
| Zoning lot (Z1) | lot 70 alone is assumed to be the zoning lot | evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact |
| Option 1 baseline (settled) | standard residences: FAR 2.00 / 20,150 sq ft / 29 dwelling units / 30-45-55 ft | settled reference case real-lot.json (rows L1, L3, L6) and step-p6-worked |

## Rows

### opt2-max-residential-fa - Option 2 - maximum residential floor area (qualifying affordable housing)

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))
- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "Separate maximum #residential# #floor area ratios# are set forth for #zoning lots# containing standard #residences# and #zoning lots# containing #qualifying affordable housing# or #qualifying senior housing#."
  - From the captured table, district R6B: qualifying_affordable_or_senior_housing = 2.40.

Why the rule applies: ZR 23-22 sets the maximum residential floor area ratio for R6B: 2.00 for standard residences and 2.40 for qualifying affordable or senior housing; the R6B row carries no footnote, so the within-100-ft-of-a-wide-street columns do not apply. 2.40 x the recorded lot area gives the maximum residential floor area, on the assumption that the building qualifies.

Working, step by step:

- Maximum residential floor area: 2.40 (qualifying R6B FAR) x 10,075 (recorded lot area) = 24,180

Expected value: 24,180 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-19.md (24,180 sq ft = 2.40 x 10,075; 23-22 R6B qualifying column); return-independent-hand-calculation-20.md (24,180 sq ft = 2.40 x 10,075; 23-22 R6B qualifying column); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a legal maximum floor area on the recorded lot area under Z1 (lot 70 alone); it is not an achievable or built figure and the 2.40 is reached only with the affordable floor area of opt2-uap-affordable-fa. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Recorded lot area = 10,075 sq ft (basis: administrative_record).
- Maximum residential floor area = 24,180 sq ft (basis: derived).

### opt2-uap-affordable-fa - Option 2 - affordable floor area needed to reach 2.40 under the Universal Affordability Preference

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 27-111 (General definitions (Administration of Affordable Housing)) - captured.
  - Capture: snapshot `zr-27-111`, file `docs/research/zr-snapshots/v1/zr-27-111.snapshot.json`.
  - Content digest: `39001532bb58c2dc84c42b5c52b02f7849b0fdd04c3f6f3730313d66a30e6214`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-111.
  - Quoted: "The #residential# #floor area ratio# in a #UAP development# may exceed that for standard #residences# set forth in Section 23-22 (Floor Area Regulations for R6 Through R12 Districts) only by the amount of #affordable housing# provided"

Why the rule applies: ZR 27-111 provides that a UAP development's residential floor area ratio may exceed the standard 2.00 of ZR 23-22 only by the amount of affordable housing provided; so reaching 2.40 requires affordable floor area equal to (2.40 - 2.00) x the recorded lot area.

Working, step by step:

- FAR increment above the standard 2.00: 2.40 (qualifying FAR) - 2.00 (standard FAR) = 0.40
- Affordable floor area to reach 2.40: 0.40 (FAR increment) x 10,075 (recorded lot area) = 4,030

Expected value: 4,030 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-19.md (4,030 sq ft = 0.40 x 10,075; 27-111 UAP, exceed 2.00 only by the affordable housing provided); return-independent-hand-calculation-20.md (4,030 sq ft = 0.40 x 10,075; 27-111 UAP, exceed 2.00 only by the affordable housing provided); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the affordable floor area that the UAP route requires to reach 2.40; it is not the affordable share of any particular building and names no income band. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Affordable floor area to reach 2.40 = 4,030 sq ft (basis: derived).

### opt2-heights - Option 2 - minimum base, maximum base and maximum building height (qualifying)

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table."
  - From the captured table, district R6B: min_base_height_ft = 30; qualifying_max_base_height_ft = 45; qualifying_max_building_height_ft = 65.

Why the rule applies: ZR 23-432 sets, for R6B qualifying affordable or senior housing, a minimum base height of 30 ft, a maximum base height of 45 ft and a maximum building height of 65 ft (the R6B row carries no footnote, so street width does not change them).

Expected value: 30 ft minimum base height / 45 ft maximum base height / 65 ft maximum building height

Where this stands in the independent reading: return-independent-hand-calculation-19.md (30 / 45 / 65 ft; 23-432 R6B qualifying column); return-independent-hand-calculation-20.md (30 / 45 / 65 ft; 23-432 R6B qualifying column); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the legal height envelope; the base heights match option 1 and only the maximum building height rises (55 to 65 ft). This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Minimum base height = 30 ft (basis: law).
- Maximum base height = 45 ft (basis: law).
- Maximum building height = 65 ft (basis: law).

### opt2-max-dwelling-units - Option 2 - maximum number of dwelling units (qualifying affordable housing)

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 23-52(b) (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."

Why the rule applies: ZR 23-52(b) divides the maximum residential floor area by the dwelling-unit factor 680 (qualifying affordable housing is not a 23-52(a) no-factor case); a fraction of three-quarters or more counts as one dwelling unit, otherwise it is dropped. This matches the settled real-lot row L7 (reviewer-ruled M4-T024).

Working, step by step:

- Maximum dwelling units: 24,180 (qualifying residential floor area) / 680 (dwelling-unit factor) = 35.55...; a fraction below three-quarters is dropped -> 35

Expected value: 35 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-19.md (35 = 24,180 / 680 = 35.56, fraction 0.56 dropped; 23-52(b); matches settled real-lot L7); return-independent-hand-calculation-20.md (35 = 24,180 / 680 = 35.56, fraction 0.56 dropped; 23-52(b); matches settled real-lot L7); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a legal maximum unit count on the qualifying floor area; it is not a proposed unit mix and names no unit sizes. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Maximum dwelling units = 35 units (basis: derived).

### opt2-setback-above-base - Option 2 - setback above the maximum base height

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-433 (Setback requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet shall be provided from any #street wall# fronting on a #narrow street#."

Why the rule applies: ZR 23-433 requires a setback at least 10 ft deep from any street wall fronting a wide street and at least 15 ft deep from any street wall fronting a narrow street, for portions of the street wall above the 45-ft maximum base height; it becomes operative because the qualifying building may reach 65 ft.

Expected value: 10 ft from a wide-street street wall / 15 ft from a narrow-street street wall, for portions above the 45 ft maximum base height

Where this stands in the independent reading: return-independent-hand-calculation-19.md (10 ft wide / 15 ft narrow above 45 ft; 23-433); return-independent-hand-calculation-20.md (10 ft wide / 15 ft narrow above 45 ft; 23-433); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the setback depths above the base height; it is not a street-wall position and 23-433(a)-(c) allow reductions not worked here. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Setback from a wide-street street wall = 10 ft (basis: law).
- Setback from a narrow-street street wall = 15 ft (basis: law).

### opt2-rear-yard - Option 2 - rear yard on the corner lot

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-344(a) (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less."

Why the rule applies: ZR 23-344(a) requires no rear yard within 100 feet of the point of intersection of two street lines intersecting at 135 degrees or less; the Northern Boulevard / 215 Place corner is about 90 degrees, so the corner portion is waived and the depth beyond 100 feet turns on the building type and lot width the readers did not have.

Expected value: No rear yard is required within 100 feet of the corner (ZR 23-344(a)); beyond 100 feet the depth is not known. Per zoning lot, under Z1 (lot 70 alone).

Where this stands in the independent reading: return-independent-hand-calculation-19.md (no rear yard within 100 ft of the corner per 23-344(a); beyond 100 ft not known; unchanged from option 1); return-independent-hand-calculation-20.md (no rear yard within 100 ft of the corner per 23-344(a); beyond 100 ft not known; unchanged from option 1); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records the rear yard with its condition and the Z1 zoning-lot scope and enters no unconditional 'no rear yard'; the depth beyond 100 feet stays open. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt2-lot-coverage - Option 2 - whole-lot residential lot coverage

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."

Why the rule applies: ZR 23-362 sets the maximum residential lot coverage by portion (100 percent for the corner portion within 100 feet of each street line, 80 percent for any interior or through portion beyond), so there is no single whole-lot figure; the two readings agree it is not one number.

Expected value: not known. Not known as a single whole-lot percentage, on the recorded lot area under Z1 (lot 70 alone). ZR 23-362 gives a per-portion maximum (100 percent corner within 100 feet of each street line; 80 percent for any remaining interior or through portion), not one whole-lot figure, and both readings read it by portion. KIND OF GAP: unresolved law - the captured text sets a per-portion maximum, not a single whole-lot percentage; the actual coverage also depends on the building's footprint, a design input.

Where this stands in the independent reading: return-independent-hand-calculation-19.md (both read the coverage by portion, 100 percent corner / 80 percent interior, and leave the whole-lot figure not known); return-independent-hand-calculation-20.md (both read the coverage by portion, 100 percent corner / 80 percent interior, and leave the whole-lot figure not known); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the whole-lot coverage is not a single figure; it is not the lot's actual coverage. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt2-affordable-share - Option 2 - affordable share / income terms

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 27-111 (General definitions (Administration of Affordable Housing)) - captured.
  - Capture: snapshot `zr-27-111`, file `docs/research/zr-snapshots/v1/zr-27-111.snapshot.json`.
  - Content digest: `39001532bb58c2dc84c42b5c52b02f7849b0fdd04c3f6f3730313d66a30e6214`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-111.
  - Quoted: "The #residential# #floor area ratio# in a #UAP development# may exceed that for standard #residences# set forth in Section 23-22 (Floor Area Regulations for R6 Through R12 Districts) only by the amount of #affordable housing# provided"

Why the rule applies: ZR 27-111 ties the share and income terms of affordable housing to the chosen pathway (UAP vs a regulatory-agreement route) and to HPD requirements; the two readings agree there is no single number without the pathway.

Expected value: not known. Not known as a single number. The affordable share and income band depend on the chosen pathway (UAP, or a 27-131 Mandatory Inclusionary Housing route if the lot is in an MIH area, or a regulatory-agreement route) and on HPD requirements. KIND OF GAP: a missing fact about the property - the qualifying pathway and the executed affordable housing regulatory agreement / HPD permit notice, which come from HPD, not a zoning lookup.

Where this stands in the independent reading: return-independent-hand-calculation-19.md (both leave the affordable share not known without the pathway); return-independent-hand-calculation-20.md (both leave the affordable share not known without the pathway); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the affordable share is not a single number here; it names no income band. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt2-mih-area-membership - Option 2 - Mandatory Inclusionary Housing area membership

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 27-111 (General definitions (Administration of Affordable Housing)) - captured.
  - Capture: snapshot `zr-27-111`, file `docs/research/zr-snapshots/v1/zr-27-111.snapshot.json`.
  - Content digest: `39001532bb58c2dc84c42b5c52b02f7849b0fdd04c3f6f3730313d66a30e6214`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-7/27-111.
  - Quoted: "The locations of #Mandatory Inclusionary Housing areas# are identified in APPENDIX F of this Resolution or in Special Purpose Districts, as applicable."

Why the rule applies: ZR 27-111 provides that the locations of Mandatory Inclusionary Housing areas are identified in Appendix F or in Special Purpose Districts; whether this lot is in an MIH area is a recorded value read from Appendix F / the Zoning Map, not from the captured text.

Expected value: not known. Not known from the captured text. Whether the lot is inside a Mandatory Inclusionary Housing area gates the UAP route versus the 27-131 MIH route; ZR 27-111 says MIH-area locations are identified in Appendix F, and the captured Appendix F snapshot is a pointer to the borough maps, not the Queens boundary maps themselves. KIND OF GAP: a missing fact about the property - MIH-area membership, a recorded value from Appendix F / DCP ZoLa; MapPLUTO does not flag it.

Where this stands in the independent reading: return-independent-hand-calculation-19.md (both record MIH-area membership as a recorded Appendix F value, not a reading of the captured text); return-independent-hand-calculation-20.md (both record MIH-area membership as a recorded Appendix F value, not a reading of the captured text); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that MIH-area membership is a recorded value not settled here; it is not a finding that the lot is in or out of an MIH area. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt2-vs-option-1 - Option 2 - what it adds over option 1 (standard residences)

Facts used:

- Option 1 baseline (settled) = FAR 2.00 / 20,150 sq ft / 29 dwelling units / 30-45-55 ft (source: settled reference case real-lot.json (rows L1, L3, L6) and step-p6-worked)

Law relied on:

- none cited

Why the rule applies: Compared with the settled option-1 baseline (FAR 2.00, 20,150 sq ft, 29 dwelling units, 30/45/55 ft), option 2 adds floor area, building height and dwelling units; the envelope items (coverage, rear yard, side yard, setback) are unchanged.

Working, step by step:

- Added floor area: 24,180 (qualifying floor area) - 20,150 (standard floor area) = 4,030
- Added building height: 65 (qualifying max building height) - 55 (standard max building height) = 10
- Added dwelling units: 35 (qualifying dwelling units) - 29 (standard dwelling units) = 6

Expected value: Over the settled option-1 baseline, option 2 adds +4,030 sq ft of residential floor area (20,150 to 24,180), +10 ft of maximum building height (55 to 65) and +6 dwelling units (29 to 35); the base heights, coverage, rear yard, side yard and setback rules are unchanged. The price of the bonus is at least 4,030 sq ft of affordable floor area (opt2-uap-affordable-fa) under a qualifying pathway.

Where this stands in the independent reading: return-independent-hand-calculation-19.md (both compare option 2 to the settled option-1 baseline: +4,030 FA, +10 ft, +6 DU, envelope unchanged); return-independent-hand-calculation-20.md (both compare option 2 to the settled option-1 baseline: +4,030 FA, +10 ft, +6 DU, envelope unchanged); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It compares the two options on the same basis; the added units depend on the qualifying floor area being the dividend. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt3-max-residential-fa - Option 3 - maximum residential floor area (qualifying senior housing)

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))
- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "Separate maximum #residential# #floor area ratios# are set forth for #zoning lots# containing standard #residences# and #zoning lots# containing #qualifying affordable housing# or #qualifying senior housing#."
  - From the captured table, district R6B: qualifying_affordable_or_senior_housing = 2.40.

Why the rule applies: ZR 23-22 sets the R6B qualifying-affordable-or-senior-housing floor area ratio at 2.40 (the R6B row carries no footnote); 2.40 x the recorded lot area gives the maximum residential floor area, on the assumption that the building qualifies as senior housing.

Working, step by step:

- Maximum residential floor area: 2.40 (qualifying R6B FAR) x 10,075 (recorded lot area) = 24,180

Expected value: 24,180 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-21.md (24,180 sq ft = 2.40 x 10,075; 23-22 R6B qualifying column); return-independent-hand-calculation-22.md (24,180 sq ft = 2.40 x 10,075; 23-22 R6B qualifying column); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a legal maximum floor area on the recorded lot area under Z1 (lot 70 alone); it is not an achievable or built figure. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Recorded lot area = 10,075 sq ft (basis: administrative_record).
- Maximum residential floor area = 24,180 sq ft (basis: derived).

### opt3-heights - Option 3 - minimum base, maximum base and maximum building height (qualifying)

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table."
  - From the captured table, district R6B: min_base_height_ft = 30; qualifying_max_base_height_ft = 45; qualifying_max_building_height_ft = 65.

Why the rule applies: ZR 23-432 sets, for the R6B qualifying column, a minimum base height of 30 ft, a maximum base height of 45 ft and a maximum building height of 65 ft; the R6B row carries no footnote.

Expected value: 30 ft minimum base height / 45 ft maximum base height / 65 ft maximum building height

Where this stands in the independent reading: return-independent-hand-calculation-21.md (30 / 45 / 65 ft; 23-432 R6B qualifying column); return-independent-hand-calculation-22.md (30 / 45 / 65 ft; 23-432 R6B qualifying column); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the legal height envelope; the base heights match option 1 and only the maximum building height rises (55 to 65 ft). This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Minimum base height = 30 ft (basis: law).
- Maximum base height = 45 ft (basis: law).
- Maximum building height = 65 ft (basis: law).

### opt3-dwelling-unit-factor - Option 3 - dwelling-unit factor (qualifying senior housing)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-52(a) (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "there shall be no applicable #dwelling unit# factor:"
- ZR 23-52(a)(2) (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "(2) #qualifying senior housing#"

Why the rule applies: ZR 23-52(a) lists types of multiple dwelling residences for which there is no applicable dwelling-unit factor, and (a)(2) names qualifying senior housing; so the 680 factor of (b) does not apply to a qualifying senior building.

Expected value: none - the 680 dwelling-unit factor does not apply to qualifying senior housing

Where this stands in the independent reading: return-independent-hand-calculation-21.md (both read 23-52(a)(2): qualifying senior housing is a no-factor case, so the 680 factor does not apply); return-independent-hand-calculation-22.md (both read 23-52(a)(2): qualifying senior housing is a no-factor case, so the 680 factor does not apply); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states that no dwelling-unit factor applies; it does not itself set a unit count (see opt3-max-dwelling-units). This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt3-max-dwelling-units - Option 3 - maximum number of dwelling units (qualifying senior housing)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-52(a)(2) (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "there shall be no applicable #dwelling unit# factor:"

Why the rule applies: ZR 23-52 sets the unit count by dividing the maximum residential floor area by the applicable factor, but 23-52(a)(2) gives qualifying senior housing no factor, so 23-52 yields no number; no captured provision caps the units of a no-factor senior case.

Expected value: not known. Not known. ZR 23-52(a)(2) removes the 680 dwelling-unit factor for qualifying senior housing, so 23-52 produces no numeric unit limit; the two readings differ on how to say this (reading A: no numeric limit set by 23-52; reading B: not known - another provision may govern) and neither found a captured provision that caps no-factor senior units. KIND OF GAP: unresolved law - the captured text sets no dwelling-unit number for a no-factor senior case, and whether any other density provision binds the unit count is a text the readers did not have.

Where this stands in the independent reading: return-independent-hand-calculation-21.md (the two readings differ: reading A no numeric limit, reading B not known - another rule may govern; neither found a captured cap); return-independent-hand-calculation-22.md (the two readings differ: reading A no numeric limit, reading B not known - another rule may govern; neither found a captured cap); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the senior unit count is not set by the captured text; the 35-unit figure of option 2 is the affordable 680-factor count and is not carried here. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt3-airs-accessory-space - Option 3 - accessory social and welfare space for an AIRS

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (affordable independent residence for seniors) (Definition: affordable independent residence for seniors) - captured.
  - Capture: snapshot `zr-12-10-affordable-independent-residence-for-seniors`, file `docs/research/zr-snapshots/v1/zr-12-10-affordable-independent-residence-for-seniors.snapshot.json`.
  - Content digest: `05677e98cf7e7d216d085f0e581b2c0b10f3b397b19e752b1e068553ec778616`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Floor space in an amount not less than four percent of the total #floor area# of such #affordable independent residence for seniors# shall be allocated to such #accessory# facilities."

Why the rule applies: The ZR 12-10 definition of an affordable independent residence for seniors requires floor space of not less than four percent of the total floor area for accessory social and welfare facilities.

Expected value: not less than four percent of the total floor area allocated to accessory social and welfare facilities (for an affordable independent residence for seniors)

Where this stands in the independent reading: return-independent-hand-calculation-21.md (both quote the 12-10 AIRS definition: not less than four percent of the total floor area for accessory social/welfare facilities); return-independent-hand-calculation-22.md (both quote the 12-10 AIRS definition: not less than four percent of the total floor area for accessory social/welfare facilities); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states an AIRS program requirement from the definition; it does not decide that the building is an AIRS. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Accessory social and welfare space = 4 percent of total floor area (basis: law).

### opt3-senior-definitions - Option 3 - what qualifying senior housing is (AIRS or LTCF)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (qualifying senior housing) (Definition: qualifying senior housing) - captured.
  - Capture: snapshot `zr-12-10-qualifying-senior-housing`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-senior-housing.snapshot.json`.
  - Content digest: `dba97ae9511f1f7624bb3c4f45a5b0d835c5dc5dae7e5ee062cb933e720a3947`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(a) #affordable independent residences for seniors#; or"
- ZR 12-10 (affordable independent residence for seniors) (Definition: affordable independent residence for seniors) - captured.
  - Capture: snapshot `zr-12-10-affordable-independent-residence-for-seniors`, file `docs/research/zr-snapshots/v1/zr-12-10-affordable-independent-residence-for-seniors.snapshot.json`.
  - Content digest: `05677e98cf7e7d216d085f0e581b2c0b10f3b397b19e752b1e068553ec778616`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "at least 90 percent of the #dwelling units# allocated to #affordable independent residences for seniors# are each occupied by at least one person who is 62 years of age or over"
- ZR 12-10 (long-term care facility) (Definition: long-term care facility) - captured.
  - Capture: snapshot `zr-12-10-long-term-care-facility`, file `docs/research/zr-snapshots/v1/zr-12-10-long-term-care-facility.snapshot.json`.
  - Content digest: `00d7ecd45e33d4f745d25b4ecfcee721454fcbc3e985ff362c4b862f59500286`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #community facility use# that has secured appropriate certificate of authority or licensure by the New York State Department of Health"

Why the rule applies: ZR 12-10 defines qualifying senior housing as either an affordable independent residence for seniors (AIRS) or a long-term care facility (LTCF); the AIRS and LTCF definitions set the eligibility conditions (a legal determination not made here).

Expected value: Qualifying senior housing is (a) an affordable independent residence for seniors (AIRS) or (b) a long-term care facility (LTCF). AIRS: at least 90 percent of the allocated dwelling units occupied by a person 62 or over, income-restricted to 60 percent of the income index under an affordable housing regulatory agreement. LTCF: a community-facility use licensed by the New York State Department of Health. Definitions only.

Where this stands in the independent reading: return-independent-hand-calculation-21.md (both quote the 12-10 definitions of qualifying senior housing, AIRS and LTCF; eligibility is a legal determination not made here); return-independent-hand-calculation-22.md (both quote the 12-10 definitions of qualifying senior housing, AIRS and LTCF; eligibility is a legal determination not made here); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records the definitions; it decides no eligibility - whether the building meets the AIRS or LTCF conditions is a legal and agency determination not made here. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt3-setback-above-base - Option 3 - setback above the maximum base height

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-433 (Setback requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet shall be provided from any #street wall# fronting on a #narrow street#."

Why the rule applies: ZR 23-433 requires a setback at least 10 ft deep from a wide-street street wall and at least 15 ft deep from a narrow-street street wall, for portions above the 45-ft maximum base height, operative because the qualifying building may reach 65 ft.

Expected value: 10 ft from a wide-street street wall / 15 ft from a narrow-street street wall, for portions above the 45 ft maximum base height

Where this stands in the independent reading: return-independent-hand-calculation-21.md (10 ft wide / 15 ft narrow above 45 ft; 23-433; unchanged from option 1); return-independent-hand-calculation-22.md (10 ft wide / 15 ft narrow above 45 ft; 23-433; unchanged from option 1); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the setback depths above the base height; it is not a street-wall position. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Setback from a wide-street street wall = 10 ft (basis: law).
- Setback from a narrow-street street wall = 15 ft (basis: law).

### opt3-side-yard - Option 3 - side yard

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-335(b) (Side yard requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-335`, file `docs/research/zr-snapshots/v1/zr-23-335.snapshot.json`.
  - Content digest: `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335.
  - Quoted: "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."

Why the rule applies: ZR 23-335(b) requires no side yards for the building type here, but if any open area is provided along a side lot line it must have a minimum width of five feet.

Expected value: none required; a minimum width of five feet if any open area is provided along a side lot line

Where this stands in the independent reading: return-independent-hand-calculation-21.md (no side yard required, five-foot minimum if provided; 23-335(b); unchanged from option 1); return-independent-hand-calculation-22.md (no side yard required, five-foot minimum if provided; 23-335(b); unchanged from option 1); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the side-yard rule; it is unchanged from option 1. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Minimum open-area width along a side lot line = 5 ft (basis: law).

### opt3-vs-option-1 - Option 3 - what it adds over option 1 (standard residences)

Facts used:

- Option 1 baseline (settled) = FAR 2.00 / 20,150 sq ft / 29 dwelling units / 30-45-55 ft (source: settled reference case real-lot.json (rows L1, L3, L6) and step-p6-worked)

Law relied on:

- none cited

Why the rule applies: Compared with the settled option-1 baseline, option 3 adds floor area and building height and removes the 680 dwelling-unit factor; the base heights and the envelope rules are unchanged.

Working, step by step:

- Added floor area: 24,180 (qualifying floor area) - 20,150 (standard floor area) = 4,030
- Added building height: 65 (qualifying max building height) - 55 (standard max building height) = 10

Expected value: Over the settled option-1 baseline, option 3 adds +4,030 sq ft of residential floor area (20,150 to 24,180) and +10 ft of maximum building height (55 to 65), and the 680 dwelling-unit factor is removed (opt3-dwelling-unit-factor); the base heights, coverage, rear yard, side yard and setback rules are unchanged. The price is the senior-housing program conditions, which the case decides nothing about.

Where this stands in the independent reading: return-independent-hand-calculation-21.md (both compare option 3 to the settled option-1 baseline: +4,030 FA, +10 ft, 680 factor removed, envelope unchanged); return-independent-hand-calculation-22.md (both compare option 3 to the settled option-1 baseline: +4,030 FA, +10 ft, 680 factor removed, envelope unchanged); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It compares the two options on the same basis; it decides no senior-housing eligibility. This case decides no eligibility: whether the building is qualifying affordable or qualifying senior housing is a legal determination not made here, and the figure is worked on the assumption that the building qualifies. A draft reading by AI helpers, not professionally reviewed.

### opt6-cf-far - Options 6 and 7 - community-facility floor area ratio (R6B)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-11 (Maximum Floor Area Ratio and Lot Coverage for Community Facilities) - captured.
  - Capture: snapshot `zr-24-11`, file `docs/research/zr-snapshots/v1/zr-24-11.snapshot.json`.
  - Content digest: `7ac0234975425e65cd327b114e25c4ed9bb8356d4fc79b6237ef7cb3c2227254`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11.
  - Quoted: "the maximum #floor area ratio# and maximum percent of #lot coverage# for a #community facility# #use# shall not exceed the #floor area ratio# and #lot coverage# set forth in the table in this Section."

Why the rule applies: ZR 24-11 sets the maximum community-facility floor area ratio and lot coverage from the table in that Section; the R6B contextual row of that table (read directly from the capture's plural 'tables' structure, which the checker's singular table-assertion cannot read) gives a community-facility FAR of 2.00.

Expected value: 2.00 FAR

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-11 R6B contextual row: community-facility FAR 2.00; the number lives in the capture's plural 'tables' structure, reviewer-eyeballed); return-independent-hand-calculation-24.md (both read 24-11 R6B contextual row: community-facility FAR 2.00; the number lives in the capture's plural 'tables' structure, reviewer-eyeballed); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a legal community-facility floor area ratio; the 2.00 lives in the 24-11 R6B contextual table row, recorded here as an operand with the enabling sentence quoted, because the checker's table-assertion reads only a singular 'table' key. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Community-facility floor area ratio (R6B) = 2.00 FAR (basis: law).

### opt6-cf-max-fa - Options 6 and 7 - community-facility maximum floor area

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 24-11 (Maximum Floor Area Ratio and Lot Coverage for Community Facilities) - captured.
  - Capture: snapshot `zr-24-11`, file `docs/research/zr-snapshots/v1/zr-24-11.snapshot.json`.
  - Content digest: `7ac0234975425e65cd327b114e25c4ed9bb8356d4fc79b6237ef7cb3c2227254`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11.
  - Quoted: "the maximum #floor area ratio# and maximum percent of #lot coverage# for a #community facility# #use# shall not exceed the #floor area ratio# and #lot coverage# set forth in the table in this Section."

Why the rule applies: ZR 24-11 caps the community-facility floor area at the community-facility FAR times the lot area; 2.00 x the recorded lot area gives the maximum community-facility floor area.

Working, step by step:

- Community-facility maximum floor area: 2.00 (community-facility FAR) x 10,075 (recorded lot area) = 20,150

Expected value: 20,150 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-23.md (20,150 sq ft = 2.00 x 10,075; 24-11 R6B contextual row); return-independent-hand-calculation-24.md (20,150 sq ft = 2.00 x 10,075; 24-11 R6B contextual row); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a legal maximum community-facility floor area on the recorded lot area under Z1 (lot 70 alone). A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Recorded lot area = 10,075 sq ft (basis: administrative_record).
- Community-facility maximum floor area = 20,150 sq ft (basis: derived).

### opt6-combined-cap - Option 6 - combined floor area ratio ceiling (community facility plus residences)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-161 (Community facility and residential uses) - captured.
  - Capture: snapshot `zr-24-161`, file `docs/research/zr-snapshots/v1/zr-24-161.snapshot.json`.
  - Content digest: `8b2e5f9a5a61c363dad0db22a40a79bed5697ecd7a4bc9f798d4abbdd60b131a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-161.
  - Quoted: "the maximum #floor area ratio# permitted for a #community facility# #use# shall be as set forth in Section 24-11, inclusive, and the maximum #floor area ratio# permitted for a #residential use# shall be as set forth in Article II, Chapter 3, provided the total of all such #floor area ratios# does not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#."

Why the rule applies: ZR 24-161 permits the community-facility FAR of 24-11 and the residential FAR of Article II Chapter 3 on the same zoning lot, provided the total does not exceed the greatest FAR permitted for any single use; here both are 2.00, so the combined ceiling is 2.00 (rising to 2.40 only if the residential use qualifies as affordable or senior housing).

Expected value: 2.00 FAR combined - the greatest single-use floor area ratio (community facility 2.00, residences 2.00); it rises to 2.40 only if the residential use qualifies as affordable or senior housing

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-161: total does not exceed the greatest single-use FAR; here 2.00, no stacking); return-independent-hand-calculation-24.md (both read 24-161: total does not exceed the greatest single-use FAR; here 2.00, no stacking); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the combined ceiling; the residential portion only reaches 2.40 if the housing qualifies, which the case decides nothing about. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Combined floor area ratio ceiling (standard residences) = 2.00 FAR (basis: law).

### opt6-combined-max-fa - Option 6 - combined maximum total floor area (standard)

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 24-161 (Community facility and residential uses) - captured.
  - Capture: snapshot `zr-24-161`, file `docs/research/zr-snapshots/v1/zr-24-161.snapshot.json`.
  - Content digest: `8b2e5f9a5a61c363dad0db22a40a79bed5697ecd7a4bc9f798d4abbdd60b131a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-161.
  - Quoted: "the maximum #floor area ratio# permitted for a #community facility# #use# shall be as set forth in Section 24-11, inclusive, and the maximum #floor area ratio# permitted for a #residential use# shall be as set forth in Article II, Chapter 3, provided the total of all such #floor area ratios# does not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#."

Why the rule applies: ZR 24-161's greatest-single-use ceiling (2.00 here) x the recorded lot area gives the combined maximum total floor area for a standard mixed building.

Working, step by step:

- Combined maximum total floor area: 2.00 (combined FAR ceiling) x 10,075 (recorded lot area) = 20,150

Expected value: 20,150 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-23.md (20,150 sq ft = 2.00 x 10,075; 24-161 greatest single use); return-independent-hand-calculation-24.md (20,150 sq ft = 2.00 x 10,075; 24-161 greatest single use); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the combined maximum total floor area for a standard mixed building on the recorded lot area under Z1; the split between the two uses is a design input. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Combined maximum total floor area (standard) = 20,150 sq ft (basis: derived).

### opt6-dwelling-units - Option 6 - number of dwelling units (mixed building)

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 23-52(b) (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."

Why the rule applies: In a mixed building the residential dwelling units come from the residential floor area divided by 680 (ZR 23-52(b)); the residential floor area falls as the community-facility floor area grows, so the unit count depends on the chosen split and is bounded at the all-residential case (20,150 / 680 = 29.6 -> 29).

Expected value: not known. Not known as a single number. The dwelling units are the residential floor area divided by 680 (ZR 23-52(b)); the residential floor area depends on how much of the 20,150 sq ft combined ceiling is taken by the community-facility use, so the unit count is bounded at 29 (the all-residential case, 20,150 / 680 = 29.6 -> 29) and falls as the community facility grows. Both readings agree it is at most 29 and depends on the split. KIND OF GAP: a missing fact about the property - the chosen split of floor area between residential and community-facility use, a design input the readers did not have.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both: at most 29, 20,150 / 680 = 29.6 -> 29 if the community facility is 0, falling as the community-facility share grows; the split is a design input); return-independent-hand-calculation-24.md (both: at most 29, 20,150 / 680 = 29.6 -> 29 if the community facility is 0, falling as the community-facility share grows; the split is a design input); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the mixed-building unit count is bounded at 29 and not a single number; it is not a proposed unit mix. A draft reading by AI helpers, not professionally reviewed.

### opt7-dwelling-units - Option 7 - number of dwelling units (community facility alone)

Facts used:

- Option 7 is a community facility alone = no residences (source: both readings (return-independent-hand-calculation-23.md and return-independent-hand-calculation-24.md): option 7 is a pure community-facility building with no dwelling units)

Law relied on:

- none cited

Why the rule applies: Option 7 is a community facility alone with no residences, so there are no dwelling units; the 29-unit option-1 figure does not apply.

Expected value: No dwelling units - option 7 is a community facility alone (no residences)

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both: option 7 is a pure community facility; zero dwelling units); return-independent-hand-calculation-24.md (both: option 7 is a pure community facility; zero dwelling units); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that a community facility alone has no dwelling units; it decides no community-facility use permission. A draft reading by AI helpers, not professionally reviewed.

### opt67-cf-lot-coverage - Options 6 and 7 - community-facility lot coverage (corner / interior)

Facts used:

- Lot type = corner lot (source: settled reference case real-lot.json / step-p3-worked)

Law relied on:

- ZR 24-11 (Maximum Floor Area Ratio and Lot Coverage for Community Facilities) - captured.
  - Capture: snapshot `zr-24-11`, file `docs/research/zr-snapshots/v1/zr-24-11.snapshot.json`.
  - Content digest: `7ac0234975425e65cd327b114e25c4ed9bb8356d4fc79b6237ef7cb3c2227254`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11.
  - Quoted: "the maximum #floor area ratio# and maximum percent of #lot coverage# for a #community facility# #use# shall not exceed the #floor area ratio# and #lot coverage# set forth in the table in this Section."

Why the rule applies: ZR 24-11's R6B contextual table row sets the maximum community-facility lot coverage at 80 percent on the corner portion and 60 percent on the interior/through portion (read from the capture's plural 'tables' structure).

Expected value: 80 percent on the corner portion / 60 percent on the interior or through portion

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-11 R6B contextual row: corner 80 percent, interior 60 percent; the numbers live in the capture's plural 'tables' structure, reviewer-eyeballed); return-independent-hand-calculation-24.md (both read 24-11 R6B contextual row: corner 80 percent, interior 60 percent; the numbers live in the capture's plural 'tables' structure, reviewer-eyeballed); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the permitted community-facility lot-coverage maxima by portion; these are lower than the residential 100 / 80 of ZR 23-362. The 80 / 60 live in the 24-11 table row, reviewer-eyeballed. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Corner-portion community-facility lot coverage = 80 percent (basis: law).
- Interior/through-portion community-facility lot coverage = 60 percent (basis: law).

### opt67-cf-max-footprint - Options 6 and 7 - community-facility maximum footprint by portion

Facts used:

- Recorded lot area = 10,075 sq ft (source: NYC PLUTO lotarea for BBL 4073340070 (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure (evidence record NB-04))

Law relied on:

- ZR 24-11 (Maximum Floor Area Ratio and Lot Coverage for Community Facilities) - captured.
  - Capture: snapshot `zr-24-11`, file `docs/research/zr-snapshots/v1/zr-24-11.snapshot.json`.
  - Content digest: `7ac0234975425e65cd327b114e25c4ed9bb8356d4fc79b6237ef7cb3c2227254`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-11.
  - Quoted: "the maximum #floor area ratio# and maximum percent of #lot coverage# for a #community facility# #use# shall not exceed the #floor area ratio# and #lot coverage# set forth in the table in this Section."

Why the rule applies: Applying the 24-11 community-facility lot-coverage maxima to the recorded lot area gives the maximum footprint per level: 0.80 x the lot area on the corner portion, 0.60 x the lot area on the interior portion.

Working, step by step:

- Corner-portion maximum footprint: 0.80 (corner lot-coverage fraction) x 10,075 (recorded lot area) = 8,060
- Interior-portion maximum footprint: 0.60 (interior lot-coverage fraction) x 10,075 (recorded lot area) = 6,045

Expected value: 8,060 sq ft on the corner portion (0.80 x 10,075) and 6,045 sq ft on the interior or through portion (0.60 x 10,075), per level

Where this stands in the independent reading: return-independent-hand-calculation-23.md (8,060 = 0.80 x 10,075; 6,045 = 0.60 x 10,075; 24-11 lot-coverage maxima on the recorded lot area); return-independent-hand-calculation-24.md (8,060 = 0.80 x 10,075; 6,045 = 0.60 x 10,075; 24-11 lot-coverage maxima on the recorded lot area); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the permitted maximum footprint per level by portion on the recorded lot area under Z1; it is not a built footprint. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Corner-portion maximum footprint = 8,060 sq ft (basis: derived).
- Interior/through-portion maximum footprint = 6,045 sq ft (basis: derived).

### opt67-mixed-level-coverage - Option 6 - lot coverage on a level with both uses

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-163 (Lot coverage for mixed buildings) - captured.
  - Capture: snapshot `zr-24-163`, file `docs/research/zr-snapshots/v1/zr-24-163.snapshot.json`.
  - Content digest: `e46e7a1a2bdc7b3e64121c1ded3461ee3b54f8f5ba222348c0bad16dbce4c6be`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-163.
  - Quoted: "Where different maximum percentages of #lot coverage# apply to #residential# and #community facility# #uses#, the higher #lot coverage# shall be applied to any level containing both such #uses#."

Why the rule applies: ZR 24-163 provides that where different lot-coverage maxima apply to residential and community-facility uses, the higher lot coverage applies to any level containing both uses.

Expected value: On a level that contains both residential and community-facility use, the higher lot coverage (the residential maximum) applies (ZR 24-163)

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-163: the higher lot coverage applies to a mixed level); return-independent-hand-calculation-24.md (both read 24-163: the higher lot coverage applies to a mixed level); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the mixed-level lot-coverage rule for a mixed building; it is not a built coverage. A draft reading by AI helpers, not professionally reviewed.

### opt67-heights - Options 6 and 7 - minimum base, maximum base and maximum building height (standard)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-04(b)(1) (Applicability of Article II, Chapter 3 bulk regulations) - captured.
  - Capture: snapshot `zr-24-04`, file `docs/research/zr-snapshots/v1/zr-24-04.snapshot.json`.
  - Content digest: `a871089d803220ce9c5dd32e0aaafb16f0e8a9b70e12b9e3823ded0e2337eec3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-04.
  - Quoted: "In R6 through R12 Districts with a letter suffix, the height and setback regulations of Section 23-43 (Height and Setback Requirements in R6 Through R12 Districts), inclusive, shall be applied to all #buildings# in accordance with the applicable #Residence District# regulations."
- ZR 23-432 (Height and setback requirements) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table."
  - From the captured table, district R6B: min_base_height_ft = 30; standard_max_base_height_ft = 45; standard_max_building_height_ft = 55.

Why the rule applies: ZR 24-04(b)(1) applies the Section 23-43 height-and-setback chain to community-facility buildings in R6-R12 districts with a letter suffix; the R6B standard row of ZR 23-432 then gives 30 ft minimum base, 45 ft maximum base and 55 ft maximum building height.

Expected value: 30 ft minimum base height / 45 ft maximum base height / 55 ft maximum building height (the same R6B standard envelope as option 1, via ZR 24-04(b)(1))

Where this stands in the independent reading: return-independent-hand-calculation-23.md (30 / 45 / 55 ft; 24-04(b)(1) routes R6B community facility to 23-432 R6B standard row); return-independent-hand-calculation-24.md (30 / 45 / 55 ft; 24-04(b)(1) routes R6B community facility to 23-432 R6B standard row); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the legal height envelope for a community-facility or mixed building; it matches option 1's standard envelope. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Minimum base height = 30 ft (basis: law).
- Maximum base height = 45 ft (basis: law).
- Maximum building height = 55 ft (basis: law).

### opt67-setback-above-base - Options 6 and 7 - setback above the maximum base height

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-433 (Setback requirements for R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet shall be provided from any #street wall# fronting on a #narrow street#."

Why the rule applies: Through ZR 24-04(b)(1)'s routing into the 23-43 chain, ZR 23-433 requires a setback at least 10 ft deep from a wide-street street wall and at least 15 ft deep from a narrow-street street wall for portions above the maximum base height.

Expected value: 10 ft from a wide-street street wall / 15 ft from a narrow-street street wall, for portions above the 45 ft maximum base height (via ZR 24-04(b)(1))

Where this stands in the independent reading: return-independent-hand-calculation-23.md (10 ft wide / 15 ft narrow above 45 ft; 23-433 via 24-04(b)(1)); return-independent-hand-calculation-24.md (10 ft wide / 15 ft narrow above 45 ft; 23-433 via 24-04(b)(1)); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the setback depths above the base height; at 55 ft the setback is operative above 45 ft. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Setback from a wide-street street wall = 10 ft (basis: law).
- Setback from a narrow-street street wall = 15 ft (basis: law).

### opt67-cf-front-yard - Options 6 and 7 - community-facility front yard

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-34 (Front yards for community facilities) - captured.
  - Capture: snapshot `zr-24-34`, file `docs/research/zr-snapshots/v1/zr-24-34.snapshot.json`.
  - Content digest: `558e53e8d8737f0e2f2644d009a1705128d3b3b9423ec43dbc22399219cc2a73`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-34.
  - Quoted: "In the districts indicated, #front yards# shall be provided as set forth in the following table"

Why the rule applies: ZR 24-34 sets community-facility front yards for R1 through R5 districts only; R6B is not among the districts indicated, so no community-facility front yard is required.

Expected value: none required - ZR 24-34 sets community-facility front yards for R1 through R5 districts only, and R6B is not listed

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-34: the front-yard table is for R1-R5; R6B is not listed, so no front yard); return-independent-hand-calculation-24.md (both read 24-34: the front-yard table is for R1-R5; R6B is not listed, so no front yard); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states that no community-facility front yard is required in R6B. A draft reading by AI helpers, not professionally reviewed.

### opt67-cf-side-yard - Options 6 and 7 - community-facility side yard

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-35(b) (Side yards for community facilities) - captured.
  - Capture: snapshot `zr-24-35`, file `docs/research/zr-snapshots/v1/zr-24-35.snapshot.json`.
  - Content digest: `d411068fdbd6883e76c167666b9731ec796dd85481b0d1f28a47482c2076da12`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-35.
  - Quoted: "In the districts indicated, no #side yards# are required. However, if any open area extending along a #side lot line# is provided at any level, it shall be at least eight feet wide."

Why the rule applies: ZR 24-35(b) requires no side yards for community facilities in R6-R12, but any open area along a side lot line must be at least eight feet wide.

Expected value: none required; any open area provided along a side lot line must be at least eight feet wide (vs five feet for residences under ZR 23-335)

Where this stands in the independent reading: return-independent-hand-calculation-23.md (no community-facility side yard required, eight-foot minimum if provided; 24-35(b)); return-independent-hand-calculation-24.md (no community-facility side yard required, eight-foot minimum if provided; 24-35(b)); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the community-facility side-yard rule; the residential yards of ZR 23-30 may be substituted via ZR 24-04(c), not worked here. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Minimum open-area width along a side lot line = 8 ft (basis: law).

### opt67-cf-rear-yard - Options 6 and 7 - community-facility rear yard

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)

Law relied on:

- ZR 24-36 (Rear yards for community facilities) - captured.
  - Capture: snapshot `zr-24-36`, file `docs/research/zr-snapshots/v1/zr-24-36.snapshot.json`.
  - Content digest: `126f4af0c07ef7c3c0385d4caacc51160e112798f883030a3f258cff8f87b14c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-36.
  - Quoted: "a #rear yard# with a depth of not less than 30 feet shall be provided at every #rear lot line# on any #zoning lot#"

Why the rule applies: ZR 24-36 requires a rear yard of not less than 30 feet at every rear lot line on the zoning lot, subject to the corner waiver of ZR 24-391 (see opt67-corner-rear-yard-waiver).

Expected value: A rear yard of not less than 30 feet is required at every rear lot line, per zoning lot under Z1 (lot 70 alone), subject to the corner waiver within 100 feet of the corner (see opt67-corner-rear-yard-waiver).

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-36: 30 ft rear yard at every rear lot line, subject to 24-37/38/39); return-independent-hand-calculation-24.md (both read 24-36: 30 ft rear yard at every rear lot line, subject to 24-37/38/39); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records the rear-yard requirement with its zoning-lot scope and the corner waiver condition; it enters no unconditional 'no rear yard'. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Community-facility rear-yard depth = 30 ft (basis: law).

### opt67-corner-rear-yard-waiver - Options 6 and 7 - corner rear-yard waiver

Facts used:

- Zoning lot (Z1) = lot 70 alone is assumed to be the zoning lot (source: evidence record NB-01 (a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70; the instruments are unread, so the zoning lot is not confirmed) - a condition, not a fact)
- Corner angle = about 90 degrees (source: the Northern Boulevard / 215 Place corner, settled reference case real-lot / step-p3-worked)

Law relied on:

- ZR 24-391 (Rear yard modifications for corner lots) - captured.
  - Capture: snapshot `zr-24-391`, file `docs/research/zr-snapshots/v1/zr-24-391.snapshot.json`.
  - Content digest: `406296d6a2fb91432162f9f7b86022902da4dbf17eb38cd8873dcfba2023f376`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-391.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less."

Why the rule applies: ZR 24-391 provides that no rear yard is required within 100 feet of the point of intersection of two street lines intersecting at 135 degrees or less; the corner here is about 90 degrees, so the waiver applies to the corner portion.

Expected value: No rear yard is required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less (ZR 24-391); the Northern Boulevard / 215 Place corner is about 90 degrees, so the waiver applies to the corner portion, per zoning lot under Z1 (lot 70 alone). The portion beyond 100 feet is not waived.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-391: no rear yard within 100 ft of a <=135-degree corner; here about 90 degrees); return-independent-hand-calculation-24.md (both read 24-391: no rear yard within 100 ft of a <=135-degree corner; here about 90 degrees); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records the corner waiver with its within-100-feet-of-a-135-degree-or-less-corner condition and the Z1 zoning-lot scope; it enters no unconditional 'no rear yard'. A draft reading by AI helpers, not professionally reviewed.

### opt67-cf-rear-yard-obstruction - Options 6 and 7 - community-facility obstruction permitted in a rear yard

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-33(b)(2) (Permitted Obstructions in Required Yards or Rear Yard Equivalents) - captured.
  - Capture: snapshot `zr-24-33`, file `docs/research/zr-snapshots/v1/zr-24-33.snapshot.json`.
  - Content digest: `a356bfd584fc7ce5cd4a49baa16693be44b91ea0ccbca70a13767ccb7853fa1d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-33.
  - Quoted: "provided that the height of such #building# shall not exceed one #story#, nor in any event 23 feet above #curb level#"

Why the rule applies: ZR 24-33(b)(2) permits a one-storey community-facility building in a required rear yard, provided its height does not exceed one storey nor 23 feet above curb level (subject to district limits on which community-facility uses qualify beyond 100 feet of a wide street).

Expected value: A one-storey community-facility building (height not exceeding one storey, nor 23 feet above curb level) is a permitted obstruction in a required rear yard (ZR 24-33(b)(2))

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-33(b)(2): a one-storey, <=23 ft community-facility building is a permitted rear-yard obstruction); return-independent-hand-calculation-24.md (both read 24-33(b)(2): a one-storey, <=23 ft community-facility building is a permitted rear-yard obstruction); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states a permitted obstruction; the district conditions on which community-facility uses qualify beyond 100 feet of a wide street are named in ZR 24-33 and not worked here. A draft reading by AI helpers, not professionally reviewed.

Measured quantities, each on one basis:

- Maximum height of a rear-yard community-facility obstruction = 23 ft above curb level (basis: law).

### opt67-no-fa-gain - Options 6 and 7 - no floor-area gain over option 1

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-162 (Community facility and residential uses in certain districts) - captured.
  - Capture: snapshot `zr-24-162`, file `docs/research/zr-snapshots/v1/zr-24-162.snapshot.json`.
  - Content digest: `c1ba39e96f622b6390957539364b90f1fdff64f35e01d83a2a47185f71ab8cd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-162.
  - Quoted: "In the districts indicated, except R4-1, R4A, R4B, R5D, R6A, R6B and R6D Districts, the provisions of this Section shall apply to any #zoning lot# containing #community facility# and #residential use#."
- ZR 35-33 (Maximum Floor Area for Mixed Buildings with Community Facility Use) - captured.
  - Capture: snapshot `zr-35-33`, file `docs/research/zr-snapshots/v1/zr-35-33.snapshot.json`.
  - Content digest: `de947f0a4270dafcc9a34c4f8e8728b5365e88520e23946efce8fd45c86ef8e4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33.
  - Quoted: "In C1 and C2 Districts mapped within R6 Districts without a letter suffix, and in R7-1 Districts, the provisions of this Section shall apply to any #zoning lot# where #residential# and #community facility# #uses# are located within the same #building#."

Why the rule applies: Because ZR 24-162 excepts R6B from its community-facility floor-area reduction and ZR 35-33 applies only to C1/C2 mapped in R6 districts without a letter suffix, neither tightening governs this R6B lot; the plain 24-161 greatest-single-use ceiling (2.00) equals the residential 2.00, so option 6/7 adds no floor area over option 1.

Expected value: No floor-area gain over option 1: the R6B community-facility FAR (2.00, ZR 24-11) equals the R6B residential FAR (2.00, ZR 23-22), and the combination ceiling (ZR 24-161) is the greatest single use, 2.00. The reductions of ZR 24-162 and ZR 35-33 both pass R6B by, so neither lowers the community-facility share. The total stays 20,150 sq ft.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both: community-facility FAR 2.00 equals residential 2.00, so no gain; 24-162 excepts R6B and 35-33 applies only to un-suffixed R6); return-independent-hand-calculation-24.md (both: community-facility FAR 2.00 equals residential 2.00, so no gain; 24-162 excepts R6B and 35-33 applies only to un-suffixed R6); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states that the community-facility option adds no floor area over option 1 on this R6B lot; a CPC special permit (ZR 74-903) that the readers did not have could modify the community-facility FAR. A draft reading by AI helpers, not professionally reviewed.

### opt67-24-162-not-applicable - Options 6 and 7 - ZR 24-162 community-facility reduction not applicable

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 24-162 (Community facility and residential uses in certain districts) - captured.
  - Capture: snapshot `zr-24-162`, file `docs/research/zr-snapshots/v1/zr-24-162.snapshot.json`.
  - Content digest: `c1ba39e96f622b6390957539364b90f1fdff64f35e01d83a2a47185f71ab8cd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-4/24-162.
  - Quoted: "In the districts indicated, except R4-1, R4A, R4B, R5D, R6A, R6B and R6D Districts, the provisions of this Section shall apply to any #zoning lot# containing #community facility# and #residential use#."

Why the rule applies: ZR 24-162 lists R6B among the districts it excepts, so its Column A/B community-facility floor-area reduction does not govern this lot.

Expected value: Not applicable to R6B: ZR 24-162 lists R6B among the excepted districts, so its Column A/B community-facility floor-area reduction does not govern this lot.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 24-162: R6B is an excepted district, so the reduction is not applicable); return-independent-hand-calculation-24.md (both read 24-162: R6B is an excepted district, so the reduction is not applicable); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the 24-162 reduction is not applicable to R6B. A draft reading by AI helpers, not professionally reviewed.

### opt67-35-33-not-applicable - Options 6 and 7 - ZR 35-33 mixed-building tightening not applicable

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 35-33 (Maximum Floor Area for Mixed Buildings with Community Facility Use) - captured.
  - Capture: snapshot `zr-35-33`, file `docs/research/zr-snapshots/v1/zr-35-33.snapshot.json`.
  - Content digest: `de947f0a4270dafcc9a34c4f8e8728b5365e88520e23946efce8fd45c86ef8e4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33.
  - Quoted: "In C1 and C2 Districts mapped within R6 Districts without a letter suffix, and in R7-1 Districts, the provisions of this Section shall apply to any #zoning lot# where #residential# and #community facility# #uses# are located within the same #building#."

Why the rule applies: ZR 35-33 applies only to C1 and C2 districts mapped within R6 districts without a letter suffix (and R7-1); R6B carries the B suffix, so 35-33 does not govern.

Expected value: Not applicable to R6B: ZR 35-33 applies only to C1 and C2 districts mapped within R6 districts without a letter suffix (and R7-1), and R6B carries the B suffix.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 35-33: it governs un-suffixed R6 only, so it is not applicable to R6B); return-independent-hand-calculation-24.md (both read 35-33: it governs un-suffixed R6 only, so it is not applicable to R6B); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the 35-33 mixed-building tightening is not applicable to R6B. A draft reading by AI helpers, not professionally reviewed.

### opt67-use-group-iii - Options 6 and 7 - a community facility is a Use Group III use

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 22-13 (Use Group III) - captured.
  - Capture: snapshot `zr-22-13`, file `docs/research/zr-snapshots/v1/zr-22-13.snapshot.json`.
  - Content digest: `918b04dff74ec3887d9cca957ccb7975f5397f62a59d5ca7317df8f0571afeb2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-13.
  - Quoted: "Use Group III consists of #uses# that provide educational, religious, health and other essential services."
- ZR 32-131 (Use Group III - general use allowances) - captured.
  - Capture: snapshot `zr-32-131`, file `docs/research/zr-snapshots/v1/zr-32-131.snapshot.json`.
  - Content digest: `568c257513253c16251d32f93097558ad857b026a68ddaf3b3b0e736dcebc35c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-131.
  - Quoted: "The following tables include #uses# classified as Use Group III and set forth their allowances by #Commercial District#."

Why the rule applies: ZR 22-13 classifies community-facility uses (educational, religious, health and other essential services) as Use Group III, permitted in R1 through R12; ZR 32-131 sets how Use Group III uses are allowed in the C2-2 commercial overlay.

Expected value: A community facility is a Use Group III use (educational, religious, health and other essential services), permitted in R1 through R12 (ZR 22-13) and allowed in the C2-2 overlay per ZR 32-131

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both read 22-13 and 32-131: community facility = Use Group III); return-independent-hand-calculation-24.md (both read 22-13 and 32-131: community facility = Use Group III); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It states the use-group classification. This case decides no eligibility: which specific community-facility uses are permitted, and any use permission an agency must grant, are not decided here. A draft reading by AI helpers, not professionally reviewed.

### opt67-which-uses-not-known - Options 6 and 7 - which specific community-facility uses are permitted

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 22-13 (Use Group III) - captured.
  - Capture: snapshot `zr-22-13`, file `docs/research/zr-snapshots/v1/zr-22-13.snapshot.json`.
  - Content digest: `918b04dff74ec3887d9cca957ccb7975f5397f62a59d5ca7317df8f0571afeb2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-2/22-13.
  - Quoted: "Use Group III consists of #uses# that provide educational, religious, health and other essential services."

Why the rule applies: ZR 22-13 names Use Group III and points to Sections 22-131 to 22-135 for the use tables and their as-of-right, size-restricted and special-permit notations; the readers did not have those sub-sections among the captures, so which specific uses are permitted is not known.

Expected value: not known. Not known. ZR 22-13 classifies community facilities as Use Group III and points to ZR 22-131 to 22-135 for the use tables and their as-of-right (nothing), size-restricted (S) and special-permit notations; the readers did not have ZR 22-131 to 22-135 among the captures, so which specific Use Group III uses are permitted as-of-right, size-restricted or by special permit in R6B and the C2-2 overlay is not settled. KIND OF GAP: unresolved law - the Use Group III use tables (ZR 22-131 to 22-135) are a text the readers did not have.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (both name ZR 22-131 to 22-135 as a text they did not have; neither settles which specific uses are permitted); return-independent-hand-calculation-24.md (both name ZR 22-131 to 22-135 as a text they did not have; neither settles which specific uses are permitted); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that which specific community-facility uses are permitted is not known from the captured text. This case decides no eligibility: which specific community-facility uses are permitted, and any use permission an agency must grant, are not decided here. A draft reading by AI helpers, not professionally reviewed.

### opt67-street-wall - Options 6 and 7 - community-facility street-wall routing

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- none cited

Why the rule applies: The two readings route the community-facility street-wall location differently (one cites ZR 23-431, the other ZR 35-631(b) via the C2-2 overlay); for a community-facility-only building the captured text does not fix which routing governs, so the street-wall location is not settled.

Expected value: not known. Not known. The two readings route the community-facility street-wall location through different sections (reading A / the residential readers via ZR 35-631(b) reached through the C2-2 overlay; reading B via ZR 23-431), and for a community-facility-only building the captured text does not fix which routing governs. KIND OF GAP: unresolved law - the captured text does not settle the community-facility-only street-wall routing, and the two readings cite different sections.

Where this stands in the independent reading: return-independent-hand-calculation-23.md (the two readings cite different street-wall sections, ZR 23-431 vs ZR 35-631(b) via the overlay; the routing is not settled by the captured text); return-independent-hand-calculation-24.md (the two readings cite different street-wall sections, ZR 23-431 vs ZR 35-631(b) via the overlay; the routing is not settled by the captured text); both readings agree on the same value and the same basis, confirmed by the comparer return-independent-hand-calculation-25.md.

What this row does not establish: It records that the community-facility street-wall routing is not settled; it is a citation difference the captured text does not resolve. A draft reading by AI helpers, not professionally reviewed.

### both-readers-did-not-have - The sections the readers did not have among the captures (named in prose only)

Facts used:

- Compiled from the comparer = the sections not among the captures (source: return-independent-hand-calculation-25.md part (3))

Law relied on:

- none cited

Why the rule applies: Several sections the readings point to are not among the pinned captures in docs/research/zr-snapshots/v1; the proven convention names them in prose only and records no value on them and cites none of them.

Expected value: The readers did not have these sections among the pinned captures, and no value above rests on them: ZR 23-154 as it existed before 5 December 2024 (the UAP Offsite Option floor-area rate, relevant only to an offsite option, not this generating site; option 2); ZR 23-63 (Required Recreation Space, pointed to inside the AIRS definition - only ZR 23-62 is among the captures; option 3); and ZR 22-131 to 22-135 (the Use Group III use tables) and ZR 74-902 / 74-903 (the City Planning Commission special permit that could modify the community-facility FAR; options 6 and 7). Each is named here in prose only; none is a value basis or a formal citation above.

Where this stands in the independent reading: return-independent-hand-calculation-25.md part (3) lists the sections not among the captures (the independent comparer); the option readings are named per option row.

What this row does not establish: It lists sections the readers did not have among the captures; it is about texts, not facts (see real-lot-missing-facts). A draft reading by AI helpers, not professionally reviewed.

### real-lot-missing-facts - The facts about the real lot that both readings did not have, and the kind of each gap

Facts used:

- Compiled from the comparer and both readings = the missing facts (source: return-independent-hand-calculation-25.md part (5); both option readings)

Law relied on:

- none cited

Why the rule applies: Every option figure above stays conditional on facts about the real lot that the readers did not have; each gap is named with where it would come from.

Expected value: not known. Not known, and left unresolved in every option figure above. (1) The zoning lot: a 2022 ZONE/CERT/DECL is indexed against lots 1 and 70 but the instruments are unread (evidence record NB-01), so whether lot 70 stands alone (Z1) or with lot 1 (about 20,000 sq ft) is not confirmed; every floor-area, dwelling-unit, coverage and combination figure scales with it. (2) The lot-area basis: the recorded 10,075 sq ft and the GIS-measured 10,387.99 sq ft differ by about 3.1 percent (evidence record NB-04); every figure above uses the recorded 10,075 and the two bases are never mixed. (3) Eligibility: whether the building is qualifying affordable or senior housing, and which community-facility uses an agency permits, are legal and agency determinations not made here. KIND OF GAP: a missing fact about the property for (1) and (2) - the recorded zoning-lot instruments, a survey or deed - and unresolved law / an agency determination for (3).

Where this stands in the independent reading: return-independent-hand-calculation-25.md part (5) lists the zoning lot, the lot-area basis and eligibility as unresolved (the independent comparer); the option readings are named per option row.

What this row does not establish: It lists the missing real-lot facts; it fills none with a guess or a typical value; a tax lot is not a zoning lot. A draft reading by AI helpers, not professionally reviewed.

### options-out-of-scope - Options 5, 8 and 9-10 are owed and out of this task

Facts used:

- Compiled from the comparer = the out-of-scope options and why (source: return-independent-hand-calculation-25.md part (3))

Law relied on:

- none cited

Why the rule applies: The eleven development options stay in scope; this case records four of them (2, 3, 6, 7) and names the other seven as owed, so no unavailable option reads as evaluated.

Expected value: Options 5 (shops with residences), 8 (a split lot with two buildings) and 9-10 (shared housing, with and without a parking waiver) are owed and out of this task. Their values rest on sections the readers did not have among the captures (for example ZR 23-51, 23-12, 23-371, 32-421, 33-26 and 33-301) and wait for capture task M3-T010. Recording options 2, 3, 6 and 7 here does not narrow the eleven-option scope.

Where this stands in the independent reading: return-independent-hand-calculation-25.md part (3) names the sections options 5, 8 and 9-10 rest on as not among the captures (the independent comparer); the option readings are named per option row.

What this row does not establish: It names the owed options and why they are out of scope; it records no value for them. A draft reading by AI helpers, not professionally reviewed.

## What this case does not establish

- It records a value or figure only where both readings of an option agree on the same value and the same basis, confirmed by the comparer, and the cited section is captured in docs/research/zr-snapshots/v1; where they differ, where one says not known, or where the captured text does not settle a point, the row says so, names both readings and states the kind of its gap.
- It decides no eligibility: whether the building is qualifying affordable housing or qualifying senior housing, whether the lot is in a Mandatory Inclusionary Housing area, and which community-facility uses an agency permits are legal and agency determinations not made here; every option-2 and option-3 figure is worked on the assumption that the building qualifies.
- No row reads as 'complies', 'buildable', 'optimal' or 'feasible'; no human verdict is entered; the comparer is an adjudicator that confirms agreement, not a third source of values; agreement between two AI readings is not proof.
- Every figure uses the recorded lot area 10,075 sq ft (administrative_record); the GIS outline 10,387.99 sq ft is display-only and is never mixed into a floor-area figure; every quantity carries exactly one of the nine measurement bases and no two bases are mixed in one figure; a tax lot is not a zoning lot and every figure stays conditional on the zoning lot (Z1).
- It records four of the eleven development options (2, 3, 6, 7) and names options 5, 8 and 9-10 as owed; recording four options does not narrow the eleven-option scope, and no value comes from a program run.

## Sources

- Option 2 reading A: provenance/return-independent-hand-calculation-19.md
- Option 2 reading B: provenance/return-independent-hand-calculation-20.md
- Option 3 reading A: provenance/return-independent-hand-calculation-21.md
- Option 3 reading B: provenance/return-independent-hand-calculation-22.md
- Options 6-7 reading A: provenance/return-independent-hand-calculation-23.md
- Options 6-7 reading B: provenance/return-independent-hand-calculation-24.md
- Independent comparer: provenance/return-independent-hand-calculation-25.md
- Each reader worked from a detached, read-only checkout of the repository at commit bb5c02b9 - the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library; each read no program output, and some read official Zoning Resolution pages live. The comparer read both readings and opened captures and official pages.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-15 | Case created (task M5-T184) from two independent readings per option (option 2: provenance -19 and -20; option 3: -21 and -22; options 6 and 7: -23 and -24) and an independent comparer (-25), each worked from a detached read-only checkout at bb5c02b9. A value or figure is recorded for options 2, 3, 6 and 7 only where both readings of that option agree on the same value and the same basis, confirmed by the comparer, and the cited section is captured in docs/research/zr-snapshots/v1; every disagreement, unresolved basis, eligibility and missing fact stays not known. Options 5, 8 and 9-10 are named as owed (they rest on sections not yet captured; capture task M3-T010). No value comes from a program run; no human verdict is entered. | rules-engineer (M5-T184) |

