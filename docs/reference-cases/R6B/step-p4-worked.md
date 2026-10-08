# Worked from the step-P4 captures: ZR 34-22 and 34-23 and their sections; ZR 35-22 and ZR 35-62 to 35-643; lot coverage and the yards as defined; the street wall; large and qualifying residential sites; dwelling units and qualifying housing; and ZR 23-44

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: section 8 (capture the missing law text, then read it independently); backlog row DB-170 item (a).

The R6B reference-case readings that waited for the law text captured by task M4-T031 (38 texts), now read independently in step P4: ZR 34-22 and its sections 34-221 to 34-224, and ZR 34-23 and its sections 34-231 to 34-233, for a residential building in a C2-2 district mapped within R6B; with those read, whether the floor area ratio, the lot coverage and the rear yard are the same as plain R6B, and whether any captured overlay text speaks of lot coverage; ZR 35-22 and ZR 35-62, 35-63, 35-641, 35-642 and 35-643; the definitions of a mixed building, lot coverage, the five yards and the street wall, curb level and prevailing street wall frontage; what may stand in a required rear yard; large sites and qualifying residential sites; whether ZR 34-111's exceptions reach C2-2 within R6B; dwelling units and qualifying housing and the ZR 23-52 factors, with a worked unit count for a made-up 100-by-100 lot; and ZR 23-441, 23-442 and 23-443. A value or a yes/no is recorded only where both readings give it on the same basis; otherwise the row is not known with both readings named. Every value comes from the two independent readings and the law text, never from a program run.

## What this case is worth

Prepared by one AI helper and read again, independently, by a second AI, each working alone from the sealed step-P4 folder; their agreement alone is not proof. It is a draft reading of the law, not professionally reviewed, and is not a statement that anything complies. It reads the newly captured text (ZR 34-22 and 34-23 and their sections, ZR 35-22 and 35-62 to 35-643, ZR 23-44 and its sections, and the lot-coverage, yard, street-wall, large-site, qualifying-residential-site, dwelling-unit and qualifying-housing definitions) for the benchmark lot and two made-up lots; where the two readings differ, or one holds an answer subject to a text the readers did not have, the row says so and names both readings.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of all 110 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, and two made-up lots, with no access to the program (reading 1: provenance/return-independent-hand-calculation-9.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-10.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Building | a new all-residential building (not a mixed building) | the subject of both readings |
| Lot type | corner (two street frontages meeting at about 89.7 degrees) | the recorded outline and DCM centerlines; cases/real-lot.json row L9 |
| Street widths | Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) | NYC DCM street centerlines; cases/real-lot.json row L11 |
| Borough and community district | Queens (QN, borough code 4), Community District 11 (PLUTO cd 411) | NYC PLUTO row for BBL 4073340070, fields borough, borocode and cd |
| Lot area | about 10,075 sq ft (PLUTO) and about 10,388 sq ft (MapPLUTO outline) | NYC PLUTO field lotarea and the MapPLUTO polygon Shape__Area |
| Made-up interior lot | 100 ft by 100 ft (10,000 sq ft), plain R6B, one street, standard residences | the readings' made-up interior 100-by-100 lot (made_up_lots.json) |

## Rows

### zr-34-22-sections - What each of ZR 34-221 to 34-224 does, and whether it reaches a residential building in a C2-2 district mapped within R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Building = a new all-residential building (not a mixed building) (source: the subject of both readings)

Law relied on:

- ZR 34-22 (Modification of Floor Area Regulations) - captured.
  - Capture: snapshot `zr-34-22`, file `docs/research/zr-snapshots/v1/zr-34-22.snapshot.json`.
  - Content digest: `8f4ad6f49de8ef67218e1b6b60bd929e2a42fc9c9504a9d0ffa3c6f367bfd248`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-22.
  - Quoted: "the #floor area# and #open space# regulations as set forth in Section 23-20"
- ZR 34-221 (Maximum floor area ratio) - captured.
  - Capture: snapshot `zr-34-221`, file `docs/research/zr-snapshots/v1/zr-34-221.snapshot.json`.
  - Content digest: `32320c4a304b9e86a8c0a025100d8085ba1317f4944762dbb4bf59dc8c5a6c7b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-221.
  - Quoted: "the maximum #floor area ratio# on a #zoning lot# shall be the applicable maximum #floor area ratio# permitted pursuant to the provisions of Article II, Chapter 3"
- ZR 34-221 (Maximum floor area ratio) - captured.
  - Capture: snapshot `zr-34-221`, file `docs/research/zr-snapshots/v1/zr-34-221.snapshot.json`.
  - Content digest: `32320c4a304b9e86a8c0a025100d8085ba1317f4944762dbb4bf59dc8c5a6c7b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-221.
  - Quoted: "However, for #Commercial Districts# with a #residential equivalent# of an R10 or R11 District with a letter suffix, no #floor area# bonuses for #public plazas# or #arcades# shall be permitted."
- ZR 34-222 (Change of use) - captured.
  - Capture: snapshot `zr-34-222`, file `docs/research/zr-snapshots/v1/zr-34-222.snapshot.json`.
  - Content digest: `74f7e35a4d62809e63142d0c790929d58b1c15841c7cfe7ae3a79f82273f9318`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-222.
  - Quoted: "A non-#residential use# occupying a #building#, or portion thereof, that was in existence on December 15, 1961, may be changed to a #residential use# and the regulations pertaining to maximum #floor area ratio# shall not apply to such change of #use#."
- ZR 34-223 (Floor area bonus for a public plaza) - captured.
  - Capture: snapshot `zr-34-223`, file `docs/research/zr-snapshots/v1/zr-34-223.snapshot.json`.
  - Content digest: `f3eee67bf9d539f36902787f727fd30436abdb3c7b5eb7e2fffb148f26e9ff18`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-223.
  - Quoted: "C4-6 C4-7 C4-11 C4-12 C5 C6-4 C6-5 C6-6 C6-7 C6-8 C6-9 C6-11 C6-12"
- ZR 34-224 (Floor area bonus for an arcade) - captured.
  - Capture: snapshot `zr-34-224`, file `docs/research/zr-snapshots/v1/zr-34-224.snapshot.json`.
  - Content digest: `5e4f6e77c0934f66647f9fa155ea1c6b348277dea1708fbe653f5fd9746af721`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-224.
  - Quoted: "C4-6 C4-7 C4-11 C4-12 C5-1 C5-2 C5-4 C6-4 C6-5 C6-8 C6-11 C6-12"

Why the rule applies: ZR 34-22 is the header that routes to its four sub-sections. For a new all-residential building in C2-2 within R6B: ZR 34-221 sets the maximum floor area ratio to the Article II, Chapter 3 figure and allows only the ZR 34-223 and 34-224 bonuses; its R10/R11-letter-suffix carve-out does not touch R6B. ZR 34-222 governs a change of use of a building in existence on December 15, 1961, not a new building. ZR 34-223 (public plaza) and 34-224 (arcade) list only C4/C5/C6 districts, so their district lists omit C2-2.

Expected value: ZR 34-221 applies and keeps the floor area ratio at the Article II, Chapter 3 (R6B) figure, allowing only the ZR 34-223 and 34-224 bonuses, with its R10/R11-letter-suffix carve-out not touching R6B; ZR 34-222 (change of use of a building in existence on December 15, 1961) does not reach a new building; ZR 34-223 (public-plaza bonus) and ZR 34-224 (arcade bonus) do not apply, because their district lists omit C2-2. So none of ZR 34-221 to 34-224 changes the maximum residential floor area ratio or the buildable floor area for a new all-residential building in C2-2 within R6B

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q1 (34-221 keeps the Article II Ch 3 FAR; 34-222 change-of-use only; 34-223/224 exclude C2-2) and return-independent-hand-calculation-10.md Q1 (same, section by section); both read the four sub-sections the same way on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads only ZR 34-221 to 34-224; the floor-area figure itself is not asserted here. It says nothing complies.

### zr-34-23-sections - What each of ZR 34-231 to 34-233 does (front yard, side yard, change of use), and that none speaks of the rear yard

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Building = a new all-residential building (not a mixed building) (source: the subject of both readings)

Law relied on:

- ZR 34-23 (Modification of Yard and Open Area Regulations) - captured.
  - Capture: snapshot `zr-34-23`, file `docs/research/zr-snapshots/v1/zr-34-23.snapshot.json`.
  - Content digest: `4f6975364cc414188005c5270c41d9b3a420d36dde8339fb325cf1701646f97d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-23.
  - Quoted: "34-23 Modification of Yard and Open Area Regulations"
- ZR 34-231 (Modification of front yard requirements) - captured.
  - Capture: snapshot `zr-34-231`, file `docs/research/zr-snapshots/v1/zr-34-231.snapshot.json`.
  - Content digest: `df20f8891b079072dd9ead1aa47df1188df132760344cccba361c9dbe57d5ed8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231.
  - Quoted: "In the districts indicated, no #front yard# shall be required for any #residential building#."
- ZR 34-232 (Modification of side yard requirements) - captured.
  - Capture: snapshot `zr-34-232`, file `docs/research/zr-snapshots/v1/zr-34-232.snapshot.json`.
  - Content digest: `9cf83f8d9c3fa6f594fa3be1e1d65651713c1809254fd08e60e527daa09c61b2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232.
  - Quoted: "In the districts indicated, no #side yard# shall be required for any #residential building#. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#. The allowances for permitted obstructions in any #yard# or #rear yard equivalent# set forth in Sections 23-311 and 23-312 shall be permitted in such open areas."
- ZR 34-233 (Change of use) - captured.
  - Capture: snapshot `zr-34-233`, file `docs/research/zr-snapshots/v1/zr-34-233.snapshot.json`.
  - Content digest: `0668220dd22e4dfe7af33972f7197839a1f662432f55a37322376d46e12a5815`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-233.
  - Quoted: "A non-#residential use# occupying a #building#, or portion thereof, that was in existence on December 15, 1961, may be changed to a #residential use# and the regulations pertaining to minimum required #open space ratio# shall not apply to such change of #use#."

Why the rule applies: ZR 34-23 is a header (Modification of Yard and Open Area Regulations). Its captured sub-sections are ZR 34-231 (front yard), 34-232 (side yard) and 34-233 (change of use for the open space ratio). Each reader read these three for a new all-residential building: 34-231 and 34-232 remove the required front and side yard; 34-233 is a change of use of a pre-December-15-1961 building, which a new building is not; none of the three speaks of the rear yard.

Expected value: ZR 34-23 is a header. Of its captured sub-sections: 34-231 requires no front yard for any residential building; 34-232 requires no side yard (any side open area provided must be at least five feet wide, with the ZR 23-311 and 23-312 obstructions allowed there); 34-233 is a change of use of a building in existence on December 15, 1961 (minimum open space ratio), which does not reach a new building. None of the captured ZR 34-23 sub-sections speaks of the rear yard

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q2 (34-231 no front yard, 34-232 no side yard, 34-233 change-of-use; no 34-23 rear-yard section) and return-independent-hand-calculation-10.md Q2 (same); both read the captured sub-sections the same way on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The capture of ZR 34-23 holds only its title line, so reading 9 (return-independent-hand-calculation-9.md) flags that the complete list of ZR 34-23 sub-sections is not confirmed by the folder, while reading 10 (return-independent-hand-calculation-10.md) reads the captured 34-231/232/233 as the complete set; that difference is recorded in the rear-yard row. It says nothing complies.

Superseded by: step-p5-worked#zr-34-23-page (kept as the record of what the earlier readers could settle; the current answer is in the named row(s)).

### floor-area-ratio - Floor area ratio, with ZR 34-22 read: is it the same as plain R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Qualifying-housing status = none recorded (source: no qualifying affordable or senior housing fact in the lot's record)

Law relied on:

- ZR 34-221 (Maximum floor area ratio) - captured.
  - Capture: snapshot `zr-34-221`, file `docs/research/zr-snapshots/v1/zr-34-221.snapshot.json`.
  - Content digest: `32320c4a304b9e86a8c0a025100d8085ba1317f4944762dbb4bf59dc8c5a6c7b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-221.
  - Quoted: "the maximum #floor area ratio# on a #zoning lot# shall be the applicable maximum #floor area ratio# permitted pursuant to the provisions of Article II, Chapter 3"
- ZR 34-223 (Floor area bonus for a public plaza) - captured.
  - Capture: snapshot `zr-34-223`, file `docs/research/zr-snapshots/v1/zr-34-223.snapshot.json`.
  - Content digest: `f3eee67bf9d539f36902787f727fd30436abdb3c7b5eb7e2fffb148f26e9ff18`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-223.
  - Quoted: "C4-6 C4-7 C4-11 C4-12 C5 C6-4 C6-5 C6-6 C6-7 C6-8 C6-9 C6-11 C6-12"
- ZR 34-224 (Floor area bonus for an arcade) - captured.
  - Capture: snapshot `zr-34-224`, file `docs/research/zr-snapshots/v1/zr-34-224.snapshot.json`.
  - Content digest: `5e4f6e77c0934f66647f9fa155ea1c6b348277dea1708fbe653f5fd9746af721`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-224.
  - Quoted: "C4-6 C4-7 C4-11 C4-12 C5-1 C5-2 C5-4 C6-4 C6-5 C6-8 C6-11 C6-12"
- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum #residential# #floor area ratio# shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.
- ZR 34-21 (General Provisions) - captured.
  - Capture: snapshot `zr-34-21`, file `docs/research/zr-snapshots/v1/zr-34-21.snapshot.json`.
  - Content digest: `6da11080e5d4012f0f9e771595e3e9434a8cafc6fdd5aa02f517d33d929e09b8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-21.
  - Quoted: "are modified by the provisions of Sections 34-22 (Modification of Floor Area Regulations), 34-23 (Modification of Yard Regulations) and 34-24"
- ZR 34-11 (General Provisions) - captured.
  - Capture: snapshot `zr-34-11`, file `docs/research/zr-snapshots/v1/zr-34-11.snapshot.json`.
  - Content digest: `e54be53bf114e18e830ec36f526b2d2df6fcb4ce32d56f8327b2b172f071a3fc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-11.
  - Quoted: "except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls"

Why the rule applies: ZR 34-221 pegs the maximum residential floor area ratio to the Article II, Chapter 3 value, which for R6B is the ZR 23-22 figure (2.00 for standard residences); the public-plaza (34-223) and arcade (34-224) bonuses exclude C2-2 by their district lists, and ZR 34-222 is change-of-use only. The step-P2 overlay reading held the floor area ratio subject to ZR 34-21 through 34-23 (texts the step-P2 readers did not have); ZR 34-21 routes, ZR 34-22 sets the floor area and ZR 34-23 the yards, and none modifies the floor area ratio, so the condition is resolved.

Expected value: same as plain R6B: with ZR 34-22 and its sections read, the maximum residential floor area ratio is the R6B value of ZR 23-22 (2.00 for standard residences); ZR 34-221 pegs it to the Article II, Chapter 3 figure, ZR 34-222 is change-of-use only, and the ZR 34-223 public-plaza and ZR 34-224 arcade bonuses exclude C2-2 by their district lists. This resolves the step-P2 overlay reading's condition (it held the floor area ratio subject to ZR 34-21 through 34-23, which the step-P2 readers did not have): those sections are now read and none modifies the floor area ratio, so the overlay does not change it

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q1/Q3 (34-221 keeps the R6B 2.00; 34-223/224 exclude C2-2; FAR same as plain R6B) and return-independent-hand-calculation-10.md Q1/Q3 (same, no change); both agree the overlay does not change the floor area ratio, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The separate 2.40 floor area ratio for qualifying affordable or senior housing needs a qualifying-housing fact not recorded (reading 9 names the 2.40 figure from the ZR 23-22 R6B row); the choice between 2.00 and 2.40 is not settled by the facts. It asserts no floor-area figure and says nothing complies.

### lot-coverage - Lot coverage, with ZR 34-22 and 34-23 read: is it the same as plain R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 Districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent"
- ZR 34-111 (Residential bulk regulations in Cl or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
- ZR 34-22 (Modification of Floor Area Regulations) - captured.
  - Capture: snapshot `zr-34-22`, file `docs/research/zr-snapshots/v1/zr-34-22.snapshot.json`.
  - Content digest: `8f4ad6f49de8ef67218e1b6b60bd929e2a42fc9c9504a9d0ffa3c6f367bfd248`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-22.
  - Quoted: "the #floor area# and #open space# regulations as set forth in Section 23-20"

Why the rule applies: No captured overlay section (ZR 34-11, 34-111, 34-22, 34-221 to 34-224, 34-23, 34-231 to 34-233 or 34-24) states a lot-coverage rule; ZR 34-22 speaks of the floor area and open space regulations, not lot coverage. Lot coverage follows the surrounding R6B rule ZR 23-362 (ZR 34-111 applies the surrounding Residence District's bulk). The step-P2 overlay reading held lot coverage subject to ZR 34-21 through 34-23; those sections are now read and none speaks of lot coverage.

Expected value: same as plain R6B: no captured overlay section (ZR 34-11, 34-111, 34-22, 34-221 to 34-224, 34-23, 34-231 to 34-233 or 34-24) states a lot-coverage rule; lot coverage is set by the R6B ZR 23-362 (80 percent for interior or through lots, 100 percent for corner lots). This resolves the step-P2 overlay reading's condition (it held lot coverage subject to ZR 34-21 through 34-23, which the step-P2 readers did not have): those sections are now read and none speaks of lot coverage, so the overlay does not change it

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q3 (overlay states no lot-coverage rule; 23-362 governs) and return-independent-hand-calculation-10.md Q3 (same); both agree the overlay adds no lot-coverage rule, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It asserts no whole-lot coverage percentage for the benchmark lot. The whole-lot corner-coverage reading stays per portion and not known: cases/real-lot.json row L5, cases/corner-reach.json row real-lot-coverage, and the corner-coverage rows of cases/step-p1-worked.json keep their not-known per-portion value, and this row does not change them. It says nothing complies.

### rear-yard - Rear yard for an all-residential building, with ZR 34-23 read: is it the same as plain R6B

Facts used:

- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Building = a new all-residential building (not a mixed building) (source: the subject of both readings)

Law relied on:

- ZR 34-231 (Modification of front yard requirements) - captured.
  - Capture: snapshot `zr-34-231`, file `docs/research/zr-snapshots/v1/zr-34-231.snapshot.json`.
  - Content digest: `df20f8891b079072dd9ead1aa47df1188df132760344cccba361c9dbe57d5ed8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231.
  - Quoted: "In the districts indicated, no #front yard# shall be required for any #residential building#."
- ZR 34-232 (Modification of side yard requirements) - captured.
  - Capture: snapshot `zr-34-232`, file `docs/research/zr-snapshots/v1/zr-34-232.snapshot.json`.
  - Content digest: `9cf83f8d9c3fa6f594fa3be1e1d65651713c1809254fd08e60e527daa09c61b2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232.
  - Quoted: "In the districts indicated, no #side yard# shall be required for any #residential building#."
- ZR 34-233 (Change of use) - captured.
  - Capture: snapshot `zr-34-233`, file `docs/research/zr-snapshots/v1/zr-34-233.snapshot.json`.
  - Content digest: `0668220dd22e4dfe7af33972f7197839a1f662432f55a37322376d46e12a5815`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-233.
  - Quoted: "the regulations pertaining to minimum required #open space ratio# shall not apply to such change of #use#."
- ZR 35-53 (Modification of Rear Yard Requirements) - captured.
  - Capture: snapshot `zr-35-53`, file `docs/research/zr-snapshots/v1/zr-35-53.snapshot.json`.
  - Content digest: `755aa5113e8ea050c21e41355448ed20d88610eeaadaea256a92c23611629ceb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-53.
  - Quoted: "for a #residential# portion of a #mixed building#, the required #residential# #rear yard# shall be provided at the floor level of the lowest #story"
- ZR 23-344 (Additional rear yard modifications) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less"

Why the rule applies: None of ZR 34-23's captured sub-sections modifies the rear yard (34-231 is front yard, 34-232 side yard, 34-233 change of use for the open space ratio). The only overlay rear-yard text, ZR 35-53, reaches only a residential portion of a mixed building; an all-residential building is not a mixed building. So the rear yard follows the R6B rules (ZR 23-342/23-343/23-344); for this corner lot ZR 23-344(a) requires no rear yard within 100 feet of the corner (the street lines meet at about 89.7 degrees).

Expected value: same as plain R6B for an all-residential building: none of ZR 34-23's captured sub-sections (34-231 front yard, 34-232 side yard, 34-233 change of use) modifies the rear yard, and the Chapter-5 rear-yard modifier ZR 35-53 reaches only a residential portion of a mixed building, which an all-residential building is not; so the rear yard follows the R6B rules (ZR 23-342/23-343/23-344), and for this corner lot ZR 23-344(a) requires no rear yard within 100 feet of the corner. This resolves the step-P2 overlay reading's condition (it held the rear yard subject to ZR 34-21 through 34-23), subject to one caveat reading 9 (return-independent-hand-calculation-9.md) raises and reading 10 (return-independent-hand-calculation-10.md) does not: the capture of ZR 34-23 holds only its title line, so reading 9 cannot rule out an ZR 34-23 sub-section the folder did not hold that would modify the rear yard, while reading 10 reads the captured 34-231/232/233 as the complete set and treats the no-rear-yard-modifier result as settled

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q2/Q3 (no 34-23 rear-yard section; 35-53 is mixed-building only; rear yard same as plain R6B, subject to the completeness caveat) and return-independent-hand-calculation-10.md Q2/Q3 (same, treated as settled); both reach same as plain R6B, and reading 9 holds it subject to the ZR 34-23 completeness caveat (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: Beyond 100 feet of the corner the rear-yard outcome is not known (cases/real-lot.json row L12, cases/step-p3-worked.json row real-lot-rear-yard-beyond-corner); this row does not re-answer it. Reading 9's completeness caveat (the full ZR 34-23 sub-section list is not confirmed by the folder) is the only open point. It says nothing complies.

### overlay-text-on-lot-coverage - Whether any captured Chapter-4 overlay text speaks of lot coverage

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 34-22 (Modification of Floor Area Regulations) - captured.
  - Capture: snapshot `zr-34-22`, file `docs/research/zr-snapshots/v1/zr-34-22.snapshot.json`.
  - Content digest: `8f4ad6f49de8ef67218e1b6b60bd929e2a42fc9c9504a9d0ffa3c6f367bfd248`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-22.
  - Quoted: "the #floor area# and #open space# regulations as set forth in Section 23-20"
- ZR 34-231 (Modification of front yard requirements) - captured.
  - Capture: snapshot `zr-34-231`, file `docs/research/zr-snapshots/v1/zr-34-231.snapshot.json`.
  - Content digest: `df20f8891b079072dd9ead1aa47df1188df132760344cccba361c9dbe57d5ed8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231.
  - Quoted: "no #front yard# shall be required for any #residential building#."
- ZR 34-232 (Modification of side yard requirements) - captured.
  - Capture: snapshot `zr-34-232`, file `docs/research/zr-snapshots/v1/zr-34-232.snapshot.json`.
  - Content digest: `9cf83f8d9c3fa6f594fa3be1e1d65651713c1809254fd08e60e527daa09c61b2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232.
  - Quoted: "no #side yard# shall be required for any #residential building#."
- ZR 34-233 (Change of use) - captured.
  - Capture: snapshot `zr-34-233`, file `docs/research/zr-snapshots/v1/zr-34-233.snapshot.json`.
  - Content digest: `0668220dd22e4dfe7af33972f7197839a1f662432f55a37322376d46e12a5815`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-233.
  - Quoted: "the regulations pertaining to minimum required #open space ratio# shall not apply to such change of #use#."

Why the rule applies: Reading each captured Chapter-4 overlay section for the word 'lot coverage': ZR 34-22 speaks of the floor area and open space regulations; ZR 34-221/222 of the maximum floor area ratio; ZR 34-231 of the front yard; ZR 34-232 of the side yard; ZR 34-233 of the open space ratio; none uses the term lot coverage. The captured mentions of lot coverage sit in sections (ZR 23-362, 23-441, 23-442, 35-641, 35-642) that do not reach an all-residential R6B building.

Expected value: no: no captured Chapter-4 overlay section speaks of lot coverage. ZR 34-22 speaks of the floor area and open space regulations; 34-221/222 of the maximum floor area ratio; 34-231 of the front yard; 34-232 of the side yard; 34-233 of the open space ratio; none uses the term lot coverage. For this lot, lot coverage comes only from the underlying R6B ZR 23-362

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q3 (no overlay text mentions lot coverage at all) and return-independent-hand-calculation-10.md Q3 (same); both agree no captured overlay text speaks of lot coverage, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the captured overlay sections only; it asserts no coverage percentage for this lot. It says nothing complies.

### zr-35-sections - ZR 35-22, 35-62, 35-63, 35-641, 35-642 and 35-643: to which buildings each applies, and whether it reaches an all-residential building in C2-2 within R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Building = a new all-residential building (not a mixed building) (source: the subject of both readings)
- Borough and community district = Queens (QN, borough code 4), Community District 11 (PLUTO cd 411) (source: NYC PLUTO row for BBL 4073340070, fields borough, borocode and cd)

Law relied on:

- ZR 35-22 (Residential Bulk Regulations in C1 or C2 Districts Whose Bulk Is Governed by Surrounding Residence District) - captured.
  - Capture: snapshot `zr-35-22`, file `docs/research/zr-snapshots/v1/zr-35-22.snapshot.json`.
  - Content digest: `6db63c4167963dc1b0771f7224a3d722082de162d51a264c30419960bdb706c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-22.
  - Quoted: "the #bulk# regulations for the #Residence Districts# within which such #Commercial Districts# are mapped apply to #residential# portions of #buildings#, except that:"
- ZR 35-62 (Height and Setback Requirements in Commercial Districts With R1 Through R5 Equivalency) - captured.
  - Capture: snapshot `zr-35-62`, file `docs/research/zr-snapshots/v1/zr-35-62.snapshot.json`.
  - Content digest: `2d5b82e080118005897e7419b4bcd042cbccdc686d6dd0d646f7c813f6d63848`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-62.
  - Quoted: "In #Commercial Districts# mapped within, or with a #residential equivalent# of an R1 through R5 District, for the purposes of applying the provisions of Section 23-42"
- ZR 35-63 (Height and Setback Requirements in Commercial Districts with R6 Through R12 Equivalency) - captured.
  - Capture: snapshot `zr-35-63`, file `docs/research/zr-snapshots/v1/zr-35-63.snapshot.json`.
  - Content digest: `77ff1923e3d3607202964541eb29e714b7cbaa9ab6dde7ddd9ccfbbd032ebe72`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-63.
  - Quoted: "In #Commercial Districts# mapped within, or with a #residential equivalent# of R6 through R12 Districts, the #street wall# location of a #building# shall be as set forth in Section 35-631, and the height and setback provisions shall be as set forth in Section 35-632."
- ZR 35-641 (Special tower provisions) - captured.
  - Capture: snapshot `zr-35-641`, file `docs/research/zr-snapshots/v1/zr-35-641.snapshot.json`.
  - Content digest: `1d28feb26cb696b4357eb965b0c3a871b875b6b3d58342dbfb8722427888d494`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-641.
  - Quoted: "(a) In #Commercial Districts# mapped within, or with a #residential equivalent# of, an R9D or R10X District, the provisions of paragraph (a) of Section 23-441 shall apply."
- ZR 35-641 (Special tower provisions) - captured.
  - Capture: snapshot `zr-35-641`, file `docs/research/zr-snapshots/v1/zr-35-641.snapshot.json`.
  - Content digest: `1d28feb26cb696b4357eb965b0c3a871b875b6b3d58342dbfb8722427888d494`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-641.
  - Quoted: "(b) In C1 or C2 Districts mapped within R9 or R10 Districts without a letter suffix, or in C1-8, C1-9, C2-7 or C2-8 Districts, for #mixed buildings# that meet the criteria of paragraph (b) of Section 23-441"
- ZR 35-642 (Special Height and Setback Provisions for Certain Areas) - captured.
  - Capture: snapshot `zr-35-642`, file `docs/research/zr-snapshots/v1/zr-35-642.snapshot.json`.
  - Content digest: `4d82c16e642acdb759d0e1f0cfdfd43ce1d886745b9be6903e052185366ac491`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-642.
  - Quoted: "In Community District 6 in the Borough of Manhattan, for #buildings# #developed# or #enlarged# with towers in #Commercial Districts# mapped within R10 Districts located east of First Avenue and north of East 51st Street"
- ZR 35-643 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-35-643`, file `docs/research/zr-snapshots/v1/zr-35-643.snapshot.json`.
  - Content digest: `dcc6dc7b99112028720388b1c895641fbbdfddb760c66e1f989a684b003989b1`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-643.
  - Quoted: "For #zoning lots# or portions thereof within 100 feet of a #street line# along a #transportation-infrastructure-adjacent frontage#, the following shall apply:"
- ZR 34-24 (Modification of Height and Setback Regulations) - captured.
  - Capture: snapshot `zr-34-24`, file `docs/research/zr-snapshots/v1/zr-34-24.snapshot.json`.
  - Content digest: `0cc3f02617a47639611221737cd0cc7ebfec8a7754346a212e6af88fdfa55630`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-24.
  - Quoted: "the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied;"
- ZR 12-10 (Definitions - mixed building) - captured.
  - Capture: snapshot `zr-12-10-mixed-building`, file `docs/research/zr-snapshots/v1/zr-12-10-mixed-building.snapshot.json`.
  - Content digest: `6eb9a38952df680333bf54add4cd40a9428e338c1177e1dfe7ee35f35c9727e0`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #building# in a #Commercial District# used partly for #residential use# and partly for #community facility# or #commercial use#."

Why the rule applies: Each section is read by its own district words. ZR 35-63 reaches a C2-2 (R6-R12 equivalency) building's height and setback, and ZR 34-24(b)(1) directs it. ZR 35-62 is for R1 through R5 equivalency. ZR 35-641's tower modifications are for R9D/R10X, or C1/C2 within R9/R10 without a letter suffix or C1-8/C1-9/C2-7/C2-8 for mixed buildings. ZR 35-642 names out-of-borough geographies. ZR 35-22 applies the surrounding R6B bulk to residential portions, which for an all-residential building is the whole building; whether ZR 35-22 (Chapter 5) or ZR 34-111 (Chapter 4) formally governs is not settled by the captured text. ZR 35-643(a) turns on a transportation-infrastructure-adjacent frontage not in the record.

Expected value: Of the named Chapter-5 sections, only ZR 35-63 clearly reaches a new all-residential building in C2-2 within R6B, and only for its height and setback (via ZR 34-24(b)(1)). ZR 35-62 does not apply (R1 through R5 equivalency). ZR 35-641 does not apply (its tower modifications are for R9D or R10X, or for C1/C2 within R9 or R10 without a letter suffix or C1-8, C1-9, C2-7 or C2-8, and for mixed buildings - none matches C2-2 within R6B). ZR 35-642 does not apply (it names Manhattan Community District 6, Brooklyn Community Districts 8, 9, 3, 5 and 16, and Bronx Community District 1; the lot is in Queens). ZR 35-22 applies the surrounding R6B bulk to the residential portions of buildings and so reaches an all-residential building's bulk in substance; whether ZR 35-22 (Chapter 5) formally governs an all-residential building, or whether ZR 34-111 (Chapter 4) governs and ZR 35-22 governs only mixed or community-facility buildings, is not known (the Chapter-5 scope provision was not in the folder), though the effect is the same R6B bulk either way - both readings. ZR 35-643(a) is not known: it applies to a zoning lot within 100 feet of a street line along a transportation-infrastructure-adjacent frontage, and whether the lot has such a frontage is not in the record - both readings

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q4 (only 35-63 reaches; 35-62/641/642 no; 35-22 formal section not known; 35-643(a) not known) and return-independent-hand-calculation-10.md Q4 (same); both read the sections the same way, and both leave 35-22's governing chapter and 35-643(a) not known (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It settles which sections reach the building, not the height and setback numbers (those come from ZR 35-632 and ZR 23-432). A mixed building (partly commercial or community facility) is not an all-residential building. It says nothing complies.

### mixed-building-definition - The definition of a mixed building

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - mixed building) - captured.
  - Capture: snapshot `zr-12-10-mixed-building`, file `docs/research/zr-snapshots/v1/zr-12-10-mixed-building.snapshot.json`.
  - Content digest: `6eb9a38952df680333bf54add4cd40a9428e338c1177e1dfe7ee35f35c9727e0`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #building# in a #Commercial District# used partly for #residential use# and partly for #community facility# or #commercial use#."

Why the rule applies: ZR 12-10 defines a mixed building as a building in a Commercial District used partly for residential use and partly for community facility or commercial use. So an all-residential building is not a mixed building, and a provision keyed to mixed buildings does not reach it by its words.

Expected value: a mixed building is a building in a Commercial District used partly for residential use and partly for community facility or commercial use; so an all-residential building is not a mixed building, and a provision keyed to mixed buildings does not reach it by its words

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q4 (mixed-building definition; an all-residential building is not one) and return-independent-hand-calculation-10.md Q4 (same); both read the definition the same way on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the definition only; it decides nothing about any particular building's use mix. It says nothing complies.

### lot-coverage-definition - The definition of lot coverage: what it counts and what it leaves out

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - lot coverage) - captured.
  - Capture: snapshot `zr-12-10-lot-coverage`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-coverage.snapshot.json`.
  - Content digest: `f5aabef6e32b83c013eb95142a44de3880b03781bd2ef88ddd15bd770d2df1cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is that portion of a #zoning lot# which, when viewed directly from above, would be covered by a #building# or any part of a #building#. However, for purposes of computing a #height factor#, any portion of such #building# covered by a roof which qualifies as #open space#, or any terrace, balcony, breeze way, or porch or portion thereof not included in the #floor area# of a #building#, shall not be included in #lot coverage#."
- ZR 12-10 (Definitions - lot coverage) - captured.
  - Capture: snapshot `zr-12-10-lot-coverage`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-coverage.snapshot.json`.
  - Content digest: `f5aabef6e32b83c013eb95142a44de3880b03781bd2ef88ddd15bd770d2df1cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "When a #height factor# is not computed for a #residential building# or #residential# portion of a #building#, obstructions permitted pursuant to Section 23-341 (Permitted obstructions in required yards or rear yard equivalents) shall not be included in #lot coverage#, except that the portion of any balcony which does not project from the face of the #building# shall be counted as #lot coverage#."

Why the rule applies: ZR 12-10 defines lot coverage by what, viewed from above, a building covers, with two sets of exclusions - one for computing a height factor and one for a residential building where no height factor is computed.

Expected value: lot coverage is the portion of a zoning lot that, viewed directly from above, would be covered by a building or any part of a building. It leaves out, when computing a height factor, any building portion under a roof that qualifies as open space and any terrace, balcony, breezeway or porch not included in floor area; and, when no height factor is computed for a residential building, the obstructions permitted under ZR 23-341, except that the portion of a balcony that does not project from the face of the building is counted. The definition states no maximum percentage (that is ZR 23-362)

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q5 (lot coverage counts the above-view footprint, with the height-factor and no-height-factor exclusions) and return-independent-hand-calculation-10.md Q5 (same); both read the definition the same way on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The definition's worked example (a 20,000-square-foot lot split into a corner portion at 100 percent and an interior portion at 70 percent) is illustrative text, not the R6B maxima and not a reading of this lot's coverage (reading 10). Height factor and open space are defined terms the readers did not have, so the exclusions cannot be fully worked. It says nothing complies.

### yard-definitions - The five yard definitions (yard, rear yard, rear yard equivalent, front yard, side yard)

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - yard) - captured.
  - Capture: snapshot `zr-12-10-yard`, file `docs/research/zr-snapshots/v1/zr-12-10-yard.snapshot.json`.
  - Content digest: `3b8a755c416fc527fa90816dfda316726ab17d2117b8f75b5453af6d8fde62ce`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is that portion of a #zoning lot# extending open and unobstructed from the lowest level to the sky along the entire length of a #lot line#, and from the #lot line# for a depth or width set forth in the applicable district #yard# regulations."
- ZR 12-10 (Definitions - yard, rear) - captured.
  - Capture: snapshot `zr-12-10-yard-rear`, file `docs/research/zr-snapshots/v1/zr-12-10-yard-rear.snapshot.json`.
  - Content digest: `917264446f1ad123d8f2442836d5c885211efb36bdfff50b63099897ae26f330`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #yard# extending for the full length of a #rear lot line#."
- ZR 12-10 (Definitions - yard equivalent, rear) - captured.
  - Capture: snapshot `zr-12-10-yard-equivalent-rear`, file `docs/research/zr-snapshots/v1/zr-12-10-yard-equivalent-rear.snapshot.json`.
  - Content digest: `13950498ce5a59c313c2e844981cb8c0e63d86e49527cd5ee2c111a6d4eb181c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is an open area which may be required on a #through lot# as an alternative to a required #rear yard#."
- ZR 12-10 (Definitions - yard, front) - captured.
  - Capture: snapshot `zr-12-10-yard-front`, file `docs/research/zr-snapshots/v1/zr-12-10-yard-front.snapshot.json`.
  - Content digest: `4f3d63b9a3556d2eaeaea0695827ad705575989d8f170cb1f56acabf9c90336b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "In the case of a #corner lot#, any #yard# extending along the full length of a #street line# shall be considered a #front yard#."
- ZR 12-10 (Definitions - yard, side) - captured.
  - Capture: snapshot `zr-12-10-yard-side`, file `docs/research/zr-snapshots/v1/zr-12-10-yard-side.snapshot.json`.
  - Content digest: `c82d9349697937925973a12ac171fe7fe158c0d5a9d3feeb9e7799b3bee481d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #yard# extending along a #side lot line# from the required #front yard# (or from the #front lot line# if no #front yard# is required) to the required #rear yard# (or to the #rear lot line#, if no #rear yard# is required). In the case of a #corner lot#, any #yard# which is not a #front yard# shall be considered a #side yard#."

Why the rule applies: ZR 12-10 defines the five yard terms the overlay and R6B yard rules use; they are read verbatim.

Expected value: A yard extends open and unobstructed from the lowest level to the sky along the entire length of a lot line, for a depth or width set by the applicable district yard regulations. A rear yard is a yard extending for the full length of a rear lot line. A rear yard equivalent is an open area that may be required on a through lot as an alternative to a required rear yard. A front yard is a yard along the full length of a front lot line, and on a corner lot any yard along the full length of a street line is a front yard. A side yard is a yard along a side lot line between the required front yard (or front lot line) and the required rear yard (or rear lot line), and on a corner lot any yard that is not a front yard is a side yard

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q5 (the five yard definitions, read verbatim) and return-independent-hand-calculation-10.md Q5 (same); both read the same words on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the definitions only; it sets no yard depth or width (those are the applicable district yard regulations). It says nothing complies.

### rear-yard-obstructions - What may stand in a required rear yard or rear yard equivalent of a residential building in R6B (a list, applied to nothing)

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)

Law relied on:

- ZR 23-341 (Permitted obstructions in required rear yards or rear yard equivalents) - captured.
  - Capture: snapshot `zr-23-341`, file `docs/research/zr-snapshots/v1/zr-23-341.snapshot.json`.
  - Content digest: `2cd7b875428bc0e28f72b8aed83f35653cf51ccbdfe91cbee5274acfe0b5426d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-341.
  - Quoted: "the obstructions set forth in Sections 23-311 and 23-312, as well as the following obstructions shall be permitted within any required #rear yard# or #rear yard equivalent#."
- ZR 23-341 (Permitted obstructions in required rear yards or rear yard equivalents) - captured.
  - Capture: snapshot `zr-23-341`, file `docs/research/zr-snapshots/v1/zr-23-341.snapshot.json`.
  - Content digest: `2cd7b875428bc0e28f72b8aed83f35653cf51ccbdfe91cbee5274acfe0b5426d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-341.
  - Quoted: "such #zoning lot# is located in an R6 through R12 Districts other than R6B, R7B or R8B Districts;"
- ZR 23-311 (Permitted obstructions in all yards, courts and open areas) - captured.
  - Capture: snapshot `zr-23-311`, file `docs/research/zr-snapshots/v1/zr-23-311.snapshot.json`.
  - Content digest: `effc083cce7405c15250314095c82dd40a944c155a662a8b36933f4d62b28f6a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-311.
  - Quoted: "In all #Residence Districts#, the following obstructions shall be permitted within any required #yard#, #rear yard equivalent#, #court# or other required open area."
- ZR 23-312 (Additional permitted obstructions generally permitted in all yards) - captured.
  - Capture: snapshot `zr-23-312`, file `docs/research/zr-snapshots/v1/zr-23-312.snapshot.json`.
  - Content digest: `c0475ada314e9b14e0753c30ee67f33534b899e99fbae19e02e9ccc55a4a1f3a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-312.
  - Quoted: "In all #Residence Districts#, the obstructions set forth in Section 23-311 (Permitted obstructions in all yards, courts and open areas), as well as the following obstructions, shall be permitted within any #yard# or #rear yard equivalent#:"

Why the rule applies: ZR 23-341 lists what may stand in a required rear yard or rear yard equivalent and brings in the obstructions of ZR 23-311 and 23-312; this row lists the items, applied to no building. One item, ZR 23-341(b)(3), is barred in R6B by its own words (it is for R6 through R12 districts other than R6B, R7B or R8B).

Expected value: From ZR 23-341, the obstructions of ZR 23-311 and ZR 23-312 plus 23-341's own list are permitted in a required rear yard or rear yard equivalent. ZR 23-341's own list: breezeways; fire escapes; non-commercial accessory greenhouses (one story or 15 feet, up to 25 percent of a required rear yard); recreational or drying-yard equipment; sheds and similar accessory storage structures (up to 10 feet); accessory solar energy systems (roof and canopy height limits); water-conserving devices in buildings existing before May 20, 1966; unenclosed balconies (subject to ZR 23-62); accessory off-street parking (height limits by residence type); for qualifying senior housing, certain residential-use building portions, which by item (b)(3)(i)'s own words are not available in R6B; and, for single- or two-family residences, residential-use building portions (height and one-third-of-rear-yard limits). ZR 23-311 adds accessory mechanical equipment, arbors or trellises, awnings, bicycle or micromobility parking, canopies, chimneys, eaves and gutters, electric-vehicle charging, flagpoles, qualifying exterior wall thickness, accessibility ramps or lifts, solar energy systems, open terraces or porches, and window sills. ZR 23-312 adds unenclosed balconies (not in side yards or within five feet of a side or rear lot line), fences, fire escapes, single/two-family overhangs, open accessory parking in a side or rear yard, front-yard parking, energy-infrastructure and accessory mechanical equipment (size and height limits), steps, above-grade accessory swimming pools (not in a front yard) and walls. This is the list only; it is applied to no building

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q5 (the 23-341 + 23-311 + 23-312 list; 23-341(b)(3) excludes R6B) and return-independent-hand-calculation-10.md Q5 (same list; 23-341(b)(3) barred in R6B); both give the same list on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It is the list of permitted obstructions only, applied to no building; several items carry size, height or building-type limits read from their own words, and some point to Section 23-62 (balconies), which the readers did not have. It says nothing complies.

### street-wall-definitions - The definitions of a street wall, curb level and a prevailing street wall frontage

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - street wall) - captured.
  - Capture: snapshot `zr-12-10-street-wall`, file `docs/research/zr-snapshots/v1/zr-12-10-street-wall.snapshot.json`.
  - Content digest: `0c6534be69d43c7fc941b164ff56281497638a50b23a43ccdd6f2ae48f3be70b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a wall or portion of a wall of a #building# facing a #street#."
- ZR 12-10 (Definitions - curb level) - captured.
  - Capture: snapshot `zr-12-10-curb-level`, file `docs/research/zr-snapshots/v1/zr-12-10-curb-level.snapshot.json`.
  - Content digest: `bd456f6c46c3bc77d50eeee5b0630f13e095657a8ff5f5936cced52dd402733e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the mean level of the curb adjoining a #zoning lot#. On #corner lots#, #curb level# is the average of the mean levels of the adjoining curbs on intersecting #streets"
- ZR 12-10 (Definitions - prevailing street wall frontage) - captured.
  - Capture: snapshot `zr-12-10-prevailing-street-wall-frontage`, file `docs/research/zr-snapshots/v1/zr-12-10-prevailing-street-wall-frontage.snapshot.json`.
  - Content digest: `1dbe67004a22ae8a31af1543d43a8310d82333ec1e254c4e0eb9d5d10d9c2354`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "shall refer to #block# frontages where, within 150 feet of the #street wall# of a subject #building#, at least half of the #aggregate width of street walls# on the same side of the #block# are within two feet of the average distance of such #street walls# from the #street line#. The total #aggregate width of street walls# shall not be less than 100 feet."

Why the rule applies: ZR 12-10 defines a street wall, curb level and a prevailing street wall frontage, the terms the street-wall location rules use; they are read verbatim.

Expected value: A street wall is a wall or portion of a wall of a building facing a street. Curb level is the mean level of the curb adjoining a zoning lot; on corner lots it is the average of the mean levels of the adjoining curbs on the intersecting streets (and, for regulating yards on corner lots, the highest of those mean levels). A prevailing street wall frontage refers to block frontages where, within 150 feet of the street wall of a subject building, at least half of the aggregate width of street walls on the same side of the block are within two feet of the average distance of such street walls from the street line, with a total aggregate width of street walls not less than 100 feet

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q6 (the street-wall, curb-level and prevailing-street-wall-frontage definitions, read verbatim) and return-independent-hand-calculation-10.md Q6 (same); both read the same words on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the definitions only; whether the real lot has a prevailing street wall frontage is the next row. It says nothing complies.

### real-lot-prevailing-frontage - Whether the real lot has a prevailing street wall frontage, and what would have to be known to say

Facts used:

- Lot type = corner (two street frontages meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Street widths = Northern Boulevard 100 ft (wide); 215 Place 60 ft (narrow) (source: NYC DCM street centerlines; cases/real-lot.json row L11)
- Neighbouring-building street-wall data = none recorded (source: the folder holds the subject lot's outline and the street centerlines and widths only)

Law relied on:

- ZR 12-10 (Definitions - prevailing street wall frontage) - captured.
  - Capture: snapshot `zr-12-10-prevailing-street-wall-frontage`, file `docs/research/zr-snapshots/v1/zr-12-10-prevailing-street-wall-frontage.snapshot.json`.
  - Content digest: `1dbe67004a22ae8a31af1543d43a8310d82333ec1e254c4e0eb9d5d10d9c2354`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "the distance of each #street wall# segment, with a width of at least five feet, from the #street line# shall be multiplied by its width. The sum of the products thus obtained, divided by total length of #aggregate width of street walls# within the 150-foot selection, shall result in the average distance."

Why the rule applies: To say whether the real lot has a prevailing street wall frontage, one must know, for each block frontage within 150 feet of the subject building's street wall and on the same side of the block, each neighbouring building's street-wall segments of at least five feet, their widths and their distances from the street line - enough to compute the width-weighted average distance, test the greater-than-50-percent-within-two-feet condition, and confirm the aggregate width is at least 100 feet. The folder holds only the subject lot's outline and the street centerlines and widths (so the street line is approximable); it holds no neighbouring-building data.

Expected value: not known. Whether the real lot has a prevailing street wall frontage is not known. The definition needs, for the block frontages within 150 feet of the subject building's street wall and on the same side of the block, each neighbouring building's street-wall segments (at least five feet wide), their widths and their distances from the street line, to compute the width-weighted average distance, test whether more than 50 percent of the aggregate width is within two feet of it, and confirm the aggregate width is at least 100 feet. The folder holds only the subject lot's outline and the street centerlines and widths, and no neighbouring-building data (reading 9 also names the aggregate-width-of-street-walls and block definitions as ones the readers did not have), so the point is not known. Both readings reach this same not-known result (return-independent-hand-calculation-9.md Q6 and return-independent-hand-calculation-10.md Q6).

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q6 (prevailing street wall frontage not known; no neighbouring-building data) and return-independent-hand-calculation-10.md Q6 (same); both reach this not-known result on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It gives no street-wall line. The subject lot's own frontages and the street lines are derivable, but the neighbouring-building street-wall facts the definition needs are not in the folder. It says nothing complies.

### large-site - Large site: the definition, and whether the real lot and the made-up 100-by-100 lot are large sites

Facts used:

- Lot area = about 10,075 sq ft (PLUTO) and about 10,388 sq ft (MapPLUTO outline) (source: NYC PLUTO field lotarea and the MapPLUTO polygon Shape__Area)
- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one street, standard residences (source: the readings' made-up interior 100-by-100 lot (made_up_lots.json))

Law relied on:

- ZR 12-10 (Definitions - large site) - captured.
  - Capture: snapshot `zr-12-10-large-site`, file `docs/research/zr-snapshots/v1/zr-12-10-large-site.snapshot.json`.
  - Content digest: `b066662c437f811714e053143092a14ff397bfc7a6fa31acbb37b0c38b575965`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is either a single #zoning lot# with a #lot area# of at least 1.5 acres, or two or more #zoning lots# under single fee ownership or alternate ownership arrangements that are contiguous or would be contiguous but for their separation by a #street# with a #lot area# of at least 1.5 acres."

Why the rule applies: ZR 12-10 defines a large site as a single zoning lot of at least 1.5 acres, or two or more commonly held contiguous (or street-separated) zoning lots totalling at least 1.5 acres. 1.5 acres is 1.5 times 43,560 square feet, which is 65,340 square feet. The real lot (about 10,075 to 10,388 square feet) and the made-up 100-by-100 lot (10,000 square feet) are each far below that.

Working, step by step:

- 1.5 acres in square feet: 1.5 (acres) x 43,560 (square feet per acre) = 65,340

Expected value: a large site is either a single zoning lot with a lot area of at least 1.5 acres (1.5 x 43,560 = 65,340 square feet) or two or more commonly held contiguous (or street-separated) zoning lots with a combined lot area of at least 1.5 acres. The real lot (about 10,075 square feet by the city record, about 10,388 square feet by the outline) and the made-up interior 100-by-100 lot (10,000 square feet) are each far below 65,340 square feet, so neither is a large site as a single zoning lot; the multi-lot branch also needs a combined area of at least 1.5 acres, which the recorded facts do not meet

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q7 (large site = 1.5 acres = 65,340 sq ft; neither lot qualifies) and return-independent-hand-calculation-10.md Q7 (same); both agree neither lot is a large site, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the single-lot test on the recorded areas; the multi-lot branch's ownership and contiguity facts are not in the folder, but that branch also needs a combined 1.5 acres, which the recorded facts do not meet. It says nothing complies.

### qualifying-residential-site - Qualifying residential site: the definition, and whether a C2-2-in-R6B lot can be one

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 12-10 (Definitions - qualifying residential site) - captured.
  - Capture: snapshot `zr-12-10-qualifying-residential-site`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-residential-site.snapshot.json`.
  - Content digest: `310807a9d82fd3681b829430c548d66c6c40edb5c534db4dec5060db330a16a5`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(a) in an R1 through R5 District, that:"
- ZR 12-10 (Definitions - qualifying residential site) - captured.
  - Capture: snapshot `zr-12-10-qualifying-residential-site`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-residential-site.snapshot.json`.
  - Content digest: `310807a9d82fd3681b829430c548d66c6c40edb5c534db4dec5060db330a16a5`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(b) in a C1, C2 or C4 District mapped within, or with a #residential equivalent# of, an R1 through R5 District:"
- ZR 12-10 (Definitions - qualifying residential site) - captured.
  - Capture: snapshot `zr-12-10-qualifying-residential-site`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-residential-site.snapshot.json`.
  - Content digest: `310807a9d82fd3681b829430c548d66c6c40edb5c534db4dec5060db330a16a5`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(c) in an M1 District paired with an R1 through R5 District."

Why the rule applies: Every branch of the qualifying-residential-site definition requires an R1 through R5 setting: paragraph (a) a lot in an R1 through R5 District, paragraph (b) a C1, C2 or C4 District mapped within or with a residential equivalent of an R1 through R5 District, and paragraph (c) an M1 District paired with an R1 through R5 District. The deciding fact is the lot's surrounding Residence District, recorded as R6B (an R6 district), with the C2-2 overlay mapped within R6B; R6B falls outside every branch.

Expected value: no: every branch of the definition requires an R1 through R5 setting - paragraph (a) a lot in an R1 through R5 District, paragraph (b) a C1, C2 or C4 District mapped within or with a residential equivalent of an R1 through R5 District, and paragraph (c) an M1 District paired with an R1 through R5 District. The deciding fact is the lot's surrounding Residence District, recorded as R6B (an R6 district) with the C2-2 overlay mapped within it; R6B falls outside every branch, so a C2-2-in-R6B lot (and a plain R6B lot) is not a qualifying residential site. The further criteria inside the branches (minimum lot area, Greater Transit Zone, wide-street or short-block frontage, community-facility floor space) never need to be reached

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q7 (every branch needs R1-R5; R6B lot is not a qualifying residential site) and return-independent-hand-calculation-10.md Q7 (same); both agree on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It settles only that the lot is not a qualifying residential site; the Greater Transit Zone and Outer Transit Zone definitions (which bound one criterion) were not in the folder but are not needed once the R1-R5 gate fails. It says nothing complies.

### zr-34-111-exceptions - Whether the two exceptions of ZR 34-111 reach a C2-2 overlay mapped within R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 34-111 (Residential bulk regulations in Cl or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "(a) on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter suffix shall apply; and"
- ZR 34-111 (Residential bulk regulations in Cl or C2 Districts whose bulk is governed by surrounding Residence District) - captured.
  - Capture: snapshot `zr-34-111`, file `docs/research/zr-snapshots/v1/zr-34-111.snapshot.json`.
  - Content digest: `5a71b0d973f9e78d24fcd325418abc47cfc53cda4cca0de6320c0624aeaa1acf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-111.
  - Quoted: "(b) on non-#qualifying residential sites#, where such districts are mapped within R1 or R2 Districts, the #bulk# regulations for R3-2 Districts shall apply."

Why the rule applies: ZR 34-111's exception (a) applies only on qualifying residential sites within the Greater Transit Zone where such districts are mapped within R1 through R5 Districts; exception (b) only where such districts are mapped within R1 or R2 Districts. The C2-2 overlay here is mapped within R6B (an R6 district), outside both, and the lot is not a qualifying residential site, so neither exception operates and the general rule of ZR 34-111 (the surrounding R6B bulk) governs.

Expected value: no: ZR 34-111's exception (a) applies only on qualifying residential sites within the Greater Transit Zone where such districts are mapped within R1 through R5 Districts, and exception (b) only where such districts are mapped within R1 or R2 Districts. The C2-2 overlay here is mapped within R6B (an R6 district), outside both, and the lot is not a qualifying residential site; so neither exception reaches it and the general rule of ZR 34-111 governs - the bulk regulations of the surrounding R6B district apply

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q7 (neither 34-111(a) nor (b) reaches C2-2 in R6B) and return-independent-hand-calculation-10.md Q7 (same); both agree neither exception reaches the lot, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: Which section governs the bulk (ZR 34-111 rather than ZR 34-112) is read in cases/step-p3-worked.json row zr-34-111-governs; this row adds that neither of ZR 34-111's exceptions reaches C2-2 within R6B, read now with the qualifying-residential-site definition (this case's qualifying-residential-site row) that the step-P3 readers did not have. It says nothing complies.

### dwelling-unit-and-qualifying-housing-definitions - The definitions of a dwelling unit, qualifying affordable housing and qualifying senior housing

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - dwelling unit) - captured.
  - Capture: snapshot `zr-12-10-dwelling-unit`, file `docs/research/zr-snapshots/v1/zr-12-10-dwelling-unit.snapshot.json`.
  - Content digest: `2987569b30a2ee84dd18bdf52b92be13eb864eab07a0d13f0ec5afe56f94f1c1`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "contains at least one #room# in a #residential building#, #residential# portion of a #building#, or #non-profit hospital staff dwelling#, and is arranged, designed, used or intended for use by one or more persons living together and maintaining a common household, and which #dwelling unit# includes lawful cooking space and lawful sanitary facilities reserved for the occupants thereof."
- ZR 12-10 (Definitions - qualifying affordable housing) - captured.
  - Capture: snapshot `zr-12-10-qualifying-affordable-housing`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-affordable-housing.snapshot.json`.
  - Content digest: `637b1b09ed49280c9ccfa3c2c32ddf27a10eedcbb96f57cb59e532dacb29d3ca`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(a) #MIH developments# in #Mandatory Inclusionary Housing areas#;"
- ZR 12-10 (Definitions - qualifying senior housing) - captured.
  - Capture: snapshot `zr-12-10-qualifying-senior-housing`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-senior-housing.snapshot.json`.
  - Content digest: `dba97ae9511f1f7624bb3c4f45a5b0d835c5dc5dae7e5ee062cb933e720a3947`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(a) #affordable independent residences for seniors#; or"

Why the rule applies: ZR 12-10 defines a dwelling unit, qualifying affordable housing and qualifying senior housing; they are read verbatim.

Expected value: A dwelling unit contains at least one room in a residential building or residential portion of a building (or a non-profit hospital staff dwelling), arranged for one or more persons living together as a common household, with lawful cooking space and lawful sanitary facilities reserved for the occupants; where a regulation applies to dwelling units in a building for residences other than single- or two-family residences, it also applies to rooming units unless stated. Qualifying affordable housing includes MIH developments in Mandatory Inclusionary Housing areas, UAP developments, or buildings subject to an affordable housing regulatory agreement. Qualifying senior housing includes affordable independent residences for seniors or long-term care facilities

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q8 (the dwelling-unit, qualifying-affordable and qualifying-senior definitions) and return-independent-hand-calculation-10.md Q8 (same); both read the same words on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The sub-terms (room, MIH developments, UAP developments, affordable housing regulatory agreement, affordable independent residences for seniors, long-term care facilities) are defined terms the readers did not have, so their precise content is not fixed by the captured text. It says nothing complies.

### dwelling-unit-factors - The ZR 23-52 dwelling-unit factor for standard residences, for qualifying affordable housing and for qualifying senior housing

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."
- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "there shall be no applicable #dwelling unit# factor:"
- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "(2) #qualifying senior housing#; or"
- ZR 12-10 (Definitions - special density areas) - captured.
  - Capture: snapshot `zr-12-10-special-density-areas`, file `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json`.
  - Content digest: `e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Special density areas# shall include:"

Why the rule applies: ZR 23-52 divides the maximum residential floor area by a dwelling-unit factor. For standard residences the factor is 680 (paragraph (b)). Qualifying affordable housing is not in the no-factor list (a), so it falls under paragraph (b), factor 680. Qualifying senior housing is in the no-factor list (paragraph (a)(2)), so there is no applicable factor. There is also no applicable factor in special density areas (paragraph (a)(1)), which ZR 12-10 defines as the Manhattan Core and the Special Downtown Brooklyn District.

Expected value: For standard residences the ZR 23-52 dwelling-unit factor is 680 (paragraph (b)); a fraction of three-quarters or more counts as one dwelling unit. For qualifying affordable housing ZR 23-52 sets no separate factor - it is not in the no-factor list (a), so it falls under paragraph (b), factor 680. For qualifying senior housing there is no applicable dwelling-unit factor (paragraph (a)(2)). There is also no applicable factor for developments or enlargements in special density areas (paragraph (a)(1)), which ZR 12-10 defines as the Manhattan Core and the Special Downtown Brooklyn District

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q8 (680 standard; 680 qualifying affordable; no factor for qualifying senior; no factor in special density areas) and return-independent-hand-calculation-10.md Q8 (same); both read the factors the same way on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It gives the factors only, not a count for any lot; qualifying affordable and qualifying senior housing are defined terms the readers did not have. It says nothing complies.

### made-up-100x100-units - The worked dwelling-unit count for the made-up interior 100-by-100 lot (standard residences, R6B), with the condition both readings attach

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one street, standard residences (source: the readings' made-up interior 100-by-100 lot (made_up_lots.json))
- Special density area = none (a plain R6B lot, not the Manhattan Core or Special Downtown Brooklyn District) (source: the made-up lot's stated district; cases/step-p3-worked.json rows manhattan-core and special-downtown-brooklyn-district)
- Residence type = standard residences (a multiple-dwelling residence, not a conversion) (source: the readings' made-up 100-by-100 lot)

Law relied on:

- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum #residential# #floor area ratio# shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.
- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."

Why the rule applies: Both readings take the R6B standard-residence floor area ratio of 2.00 (ZR 23-22), multiply by the 10,000-square-foot lot area to get the maximum residential floor area (this step assumes the ordinary meaning of floor area ratio), then divide by the ZR 23-52 factor of 680, dropping a fraction below three-quarters. The lot is a plain R6B lot, not in a special density area, and the residences are standard, so the no-factor cases of ZR 23-52(a) do not apply.

Working, step by step:

- maximum residential floor area (floor area ratio x lot area): 2.00 (floor area ratio (R6B standard residences, ZR 23-22)) x 10,000 (lot area (square feet)) = 20,000
- dwelling units (floor area / factor, ZR 23-52): 20,000 (maximum residential floor area (square feet)) / 680 (dwelling unit factor) = 29.41...; a fraction below three-quarters is dropped -> 29

Expected value: 29 dwelling units, but only conditionally. Both readings take the R6B standard-residence floor area ratio of 2.00 (ZR 23-22) and, assuming the ordinary meaning of floor area ratio (floor area = ratio x lot area), get a maximum residential floor area of 2.00 x 10,000 = 20,000 square feet, then divide by the ZR 23-52 factor of 680 to get 20,000 / 680 = 29.41..., where a fraction below three-quarters is dropped, so 29. The condition both readings attach: the definition of floor area ratio (that an FAR of 2.00 means floor area = 2.00 x lot area) was not in the folder, so on the strict captured text alone the square-foot floor area and the count are not known, and the 29 holds only on the ordinary meaning of floor area ratio. Reading 10 (return-independent-hand-calculation-10.md) attaches a second condition - that the building is one containing multiple dwelling residences, a term the readers did not have

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q8 (29 units conditionally: FAR 2.00 x 10,000 = 20,000; 20,000 / 680 = 29.41 -> 29; conditional on the floor-area-ratio definition the readers did not have) and return-independent-hand-calculation-10.md Q8 (same 29, conditional on the floor-area-ratio meaning and on 'multiple dwelling residence'); both reach 29 on the same basis and both attach the floor-area-ratio-definition condition (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The count is conditional on the definition of floor area ratio, which the readers did not have; on the strict captured text the count is not known. It is a made-up lot, not a real property. The real lot's count is not worked here: its lot area is recorded two ways (about 10,075 and about 10,388 square feet) and the same floor-area-ratio-definition gap applies. It says nothing complies.

### zr-23-441-reach - ZR 23-441 (special tower provisions): can it reach a new building on the real R6B lot, and which fact decides

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)

Law relied on:

- ZR 23-441 (Special tower provisions) - captured.
  - Capture: snapshot `zr-23-441`, file `docs/research/zr-snapshots/v1/zr-23-441.snapshot.json`.
  - Content digest: `d012fd47ce5d3eb385b971bbd3e4a079760b135becac8a444bb5f554dc999759`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-441.
  - Quoted: "In R9D and R10X Districts, the minimum #lot coverage# of a tower above the maximum base height shall be 33 percent of the #lot area# of the #zoning lot#."
- ZR 23-441 (Special tower provisions) - captured.
  - Capture: snapshot `zr-23-441`, file `docs/research/zr-snapshots/v1/zr-23-441.snapshot.json`.
  - Content digest: `d012fd47ce5d3eb385b971bbd3e4a079760b135becac8a444bb5f554dc999759`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-441.
  - Quoted: "In R9 or R10 districts without a letter suffix, the following tower-on-a-base provisions shall apply to #buildings# where:"
- ZR 23-441 (Special tower provisions) - captured.
  - Capture: snapshot `zr-23-441`, file `docs/research/zr-snapshots/v1/zr-23-441.snapshot.json`.
  - Content digest: `d012fd47ce5d3eb385b971bbd3e4a079760b135becac8a444bb5f554dc999759`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-441.
  - Quoted: "No towers shall be permitted on any #building# located wholly or partly in a #Residence District#, that is within 100 feet of a #public park# with an area of one acre or more"

Why the rule applies: ZR 23-441 modifies the tower provisions of ZR 23-435 only in R9D and R10X Districts (paragraph (a)) and in R9 or R10 Districts without a letter suffix (paragraph (b)); the deciding fact is the district, recorded as R6B, which is neither. Paragraph (c) bars towers within 100 feet of a public park of one acre or more, but it bites only where a tower is permitted at all, and no tower form (ZR 23-435) reaches an R6B lot on this text.

Expected value: no: ZR 23-441 modifies the tower provisions of ZR 23-435 only in R9D and R10X Districts (paragraph (a)) and in R9 or R10 Districts without a letter suffix (paragraph (b)); the deciding fact is the district, recorded as R6B, which is none of these, so 23-441(a) and (b) do not reach the lot. Paragraph (c) bars towers within 100 feet of a public park of one acre or more; whether the lot is near such a park is not in the record, but it is moot because no tower form (ZR 23-435) reaches an R6B lot on this text

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q9 (23-441 does not reach R6B; deciding fact is the district; the park clause is moot) and return-independent-hand-calculation-10.md Q9 (same); both agree it does not reach the lot, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: The park-proximity fact for paragraph (c) is not in the folder, but it is moot; the row decides only that ZR 23-441 does not reach an R6B lot. It says nothing complies.

### zr-23-442-reach - ZR 23-442 (special provisions for certain community districts): can it reach the real lot, and which fact decides

Facts used:

- Borough and community district = Queens (QN, borough code 4), Community District 11 (PLUTO cd 411) (source: NYC PLUTO row for BBL 4073340070, fields borough, borocode and cd)

Law relied on:

- ZR 23-442 (Special provisions for certain community districts) - captured.
  - Capture: snapshot `zr-23-442`, file `docs/research/zr-snapshots/v1/zr-23-442.snapshot.json`.
  - Content digest: `c6e45275dcb7ff1f0d9f53213266eb6a2ce2410594100014bf1edbe9b82e9efb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-442.
  - Quoted: "In R8 Districts without a letter suffix in the portion of Community District 9 in the Borough of Manhattan located north of West 125th Street"
- ZR 23-442 (Special provisions for certain community districts) - captured.
  - Capture: snapshot `zr-23-442`, file `docs/research/zr-snapshots/v1/zr-23-442.snapshot.json`.
  - Content digest: `c6e45275dcb7ff1f0d9f53213266eb6a2ce2410594100014bf1edbe9b82e9efb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-442.
  - Quoted: "In Community District 6 in the Borough of Manhattan, in R10 Districts located east of First Avenue and north of East 51st Street"

Why the rule applies: ZR 23-442 applies only in named geographies - Manhattan Community District 9 (north of West 125th Street) and Community District 6 (east of First Avenue, north of East 51st Street), and Brooklyn Community Districts 8 and 9 (Eastern Parkway) and Community District 9 (a named block). The deciding fact is the borough and community district, recorded as Queens, Community District 11, which is none of them.

Expected value: no: ZR 23-442 applies only in the named geographies - Manhattan Community District 9 (north of West 125th Street) and Community District 6 (east of First Avenue, north of East 51st Street), and Brooklyn Community Districts 8 and 9 (Eastern Parkway) and Community District 9 (a named block). The deciding fact is the borough and community district, recorded as Queens, Community District 11, which is none of them, so ZR 23-442 does not reach the lot

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q9 (23-442 names non-Queens community districts; deciding fact is the community district) and return-independent-hand-calculation-10.md Q9 (same); both agree it does not reach the lot, on the same basis (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It reads the geographies only; it decides nothing about any lot in the named districts. It says nothing complies.

### zr-23-443-reach - ZR 23-443 (special provisions in other geographies), each paragraph: can it reach the real lot, and which fact decides

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Limited-height-district field = ltdheight absent from the served PLUTO row (source: NYC PLUTO row for BBL 4073340070, as served)
- Adjacent R1-R5 district boundary = not recorded (source: the zoning query returns only R6B and C2-2 features, no adjacent-district boundary)

Law relied on:

- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "In all districts, where a #building# adjoining a #public park# utilizes the provisions of Section 23-381"
- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "For #zoning lots# or portions thereof within 100 feet of a #street line# along a #transportation-infrastructure-adjacent frontage#, the following shall apply:"
- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "In the #Limited Height Districts#, the underlying height and setback regulations for the zoning district shall apply, except that:"
- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "Where a #lot line# of a #zoning lot# located in an R6 through R12 District coincides with the district boundary of an R1 through R5 District"

Why the rule applies: ZR 23-443 has four paragraphs. (a) is for a zoning lot adjoining a public park that uses Section 23-381; (b) for a zoning lot within 100 feet of a street line along a transportation-infrastructure-adjacent frontage; (c) for Limited Height Districts; (d) where an R6 through R12 lot line coincides with an R1 through R5 district boundary. Each turns on a fact that is missing or that the two readings read differently.

Expected value: not known. Whether any paragraph of ZR 23-443 can reach the real lot is not settled. (a) adjoining a public park and using Section 23-381: not known - no park-adjacency fact, and Section 23-381 was not in the folder (both readings). (b) within 100 feet of a street line along a transportation-infrastructure-adjacent frontage: not known - the defined term was not in the folder and no fact states such a frontage (both readings). (c) Limited Height Districts: the two readings differ - reading 9 (return-independent-hand-calculation-9.md Q9) reads it as not known because the PLUTO 'ltdheight' field is absent from the served row, while reading 10 (return-independent-hand-calculation-10.md Q9) reads it as not applying on the recorded facts because no limited-height district is recorded; because the readings differ, it stays not known. (d) where a lot line of this R6 through R12 lot coincides with the district boundary of an R1 through R5 District: not known - whether any lot line of the lot coincides with an adjacent R1-R5 district boundary is not in the record (both readings).

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q9 (23-443 (a)/(b)/(d) not known; (c) read as not known on the absent ltdheight field) and return-independent-hand-calculation-10.md Q9 ((a)/(b)/(d) not known; (c) read as not applying on the recorded facts); the readings agree (a)/(b)/(d) are not known and differ on (c), so the row stays not known naming both (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: It gives no height or setback for the lot. Each paragraph turns on a fact that is missing (park adjacency, transportation-infrastructure-adjacent frontage, adjacent R1-R5 boundary) or that the two readings read differently (the Limited Height District paragraph). It says nothing complies.

### sections-and-facts-not-had - Every section, defined term and fact both readings say they did not have, what stays not known because of it, and separately what each reading says it did not read

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 23-52 (Maximum Number of Dwelling Units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor"
- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "within 100 feet of a #street line# along a #transportation-infrastructure-adjacent frontage"
- ZR 23-443 (Special provisions in other geographies) - captured.
  - Capture: snapshot `zr-23-443`, file `docs/research/zr-snapshots/v1/zr-23-443.snapshot.json`.
  - Content digest: `9bfaedb3409ce1e6af2f6f2918c9ddd2a028d7241eae4ec60abcfbb62f2f165a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-443.
  - Quoted: "where a #building# adjoining a #public park# utilizes the provisions of Section 23-381"
- ZR 23-341 (Permitted obstructions in required rear yards or rear yard equivalents) - captured.
  - Capture: snapshot `zr-23-341`, file `docs/research/zr-snapshots/v1/zr-23-341.snapshot.json`.
  - Content digest: `2cd7b875428bc0e28f72b8aed83f35653cf51ccbdfe91cbee5274acfe0b5426d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-341.
  - Quoted: "Balconies, unenclosed, subject to the provisions of Section 23-62;"
- ZR 12-10 (Definitions - qualifying residential site) - captured.
  - Capture: snapshot `zr-12-10-qualifying-residential-site`, file `docs/research/zr-snapshots/v1/zr-12-10-qualifying-residential-site.snapshot.json`.
  - Content digest: `310807a9d82fd3681b829430c548d66c6c40edb5c534db4dec5060db330a16a5`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is located within the #Greater Transit Zone"

Why the rule applies: The captured texts the readings worked point to further sections, defined terms and facts the readers did not have; this row names the items both readings name (the agreed list) and what stays not known because of them, and records separately the texts each reading says were in its folder and that it chose not to read.

Expected value: Named by both readings as not had: the definition of floor area ratio (pointed to by ZR 23-52 and ZR 23-22, needed to turn a ratio into a square-foot floor area); the R6 or R6B front-yard requirement section and the side-yard requirement section (so whether the overlay's removal of the front and side yard changes plain R6B is not known); the defined term transportation-infrastructure-adjacent frontage (ZR 23-443(b), ZR 35-643(a)); Section 23-381 (ZR 23-443(a)); Section 23-62 (balconies, ZR 23-341); the defined terms Greater Transit Zone and Outer Transit Zone (both note these are moot for the R6B reading); the neighbouring buildings' street-wall data, the mapped street lines and any adjacent-district boundary for the real lot; and the Chapter-5 scope or heading section (named by reading 9 in its Q4 and reading 10 in its list), needed to say whether ZR 35-22 (Chapter 5) or ZR 34-111 (Chapter 4) formally governs an all-residential building (the effect is the same R6B bulk either way). What stays not known because of them: the made-up 100-by-100 lot's square-foot floor area and dwelling-unit count (held conditional on the floor-area-ratio definition); whether the overlay's no-front-yard and no-side-yard rules change plain R6B; whether the real lot has a prevailing street wall frontage; and whether ZR 23-443(a), (b) or (d) reach the lot. The two readings differ on some pointers, so these are noted, not recorded as the agreed list: reading 9 (return-independent-hand-calculation-9.md) additionally names that the full ZR 34-23 sub-section list is not confirmed by the folder and the defined terms Limited Height District, aggregate width of street walls, block and short dimension of a block; reading 10 (return-independent-hand-calculation-10.md) additionally names the defined terms multiple dwelling residence, height factor and open space. Separately, each reading lists texts that were in its folder and that it chose not to read: reading 9 did not read, among others, ZR 11-23, 11-25, several ZR 12-10 definitions (wide and narrow street, base plane, the lot-line and lot-dimension definitions, street line, zoning lot, Manhattan Core, Special Downtown Brooklyn District, qualifying exterior wall thickness), ZR 23-21, 23-23 and 23-231 to 23-234, 23-363, the 23-41 obstruction sections, 23-42 and its 23-421 to 23-424 sub-sections, 23-433, 23-434, 23-435, 23-436, 34-113, 35-632, 35-633, 35-71, 36-64, 54-40 and 54-41 (it read the ZR 23-432 R6B row but not every other row of that table); reading 10 did not read a similar set, additionally naming ZR 34-112 and not naming some of reading 9's ZR 12-10 items. These are texts that reading did not read, not texts the readers did not have

Where this stands in the independent reading: return-independent-hand-calculation-9.md Q10 (the texts, terms and facts not had, and the separate not-read list) and return-independent-hand-calculation-10.md Q10 (the same, with its own not-read list); both name these as not had; the differences and each reading's not-read list are recorded as such (return-independent-hand-calculation-9.md and return-independent-hand-calculation-10.md).

What this row does not establish: This is the list of items both readings name as not had; it is not a claim that the repository holds no other related text (the folder held all 110 pinned captures, and many of the named texts were among them but each reading chose not to read them). The one-reading-only pointers and each reading's not-read list are recorded as differences, not as the agreed list. It says nothing complies.

## What this case does not establish

- It records a value or a yes/no only where both readings agree on the same basis; where they differ, where one holds an answer subject to a text the readers did not have, or where neither settles a point, the row says so and names both readings.
- The made-up 100-by-100 lot is not a real property; its dwelling-unit count is held conditional on the floor-area-ratio definition the readers did not have.
- It asserts no whole-lot coverage percentage: the overlay-reading lot-coverage answer it carries forward is that the overlay adds no coverage rule, not a reading of this lot's whole-lot coverage (cases/real-lot.json row L5 and the corner-coverage rows stay not known).
- It is not a professional or legal determination and does not say anything complies.

## Sources

- The step-P4 reading 1: provenance/return-independent-hand-calculation-9.md
- The step-P4 reading 2: provenance/return-independent-hand-calculation-10.md
- The sealed folder given to each helper: all 110 pinned law-text captures (without the notes describing how the program encoded them), the benchmark lot's recorded official facts and outline, and two made-up lots, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-07 | Case created (step P4, task M4-T032) from the two independent readings of the step-P4 sealed folder (provenance/return-independent-hand-calculation-9.md and -10.md). It holds the readings of the law text captured by task M4-T031 - ZR 34-22 and 34-23 and their sections, ZR 35-22 and ZR 35-62 to 35-643, ZR 23-44 and its sections, and the lot-coverage, yard, street-wall, large-site, qualifying-residential-site, dwelling-unit and qualifying-housing definitions. A value or a yes/no is recorded only where both readings agree on the same basis. The rows floor-area-ratio, lot-coverage and rear-yard give the current answer to the overlay reading's three results held subject to ZR 34-21 through 34-23, which are marked superseded_by these rows in cases/overlay-reading.json. | rules-engineer (M4-T032) |
| 2026-10-07 | Round 2 (review note F1): row sections-and-facts-not-had - the Chapter-5 scope or heading section is moved from the reading-10-only pointers into the list both readings name as not in their folder, because reading 9 names it too (return-independent-hand-calculation-9.md Q4: 'the Chapter-5 scope/heading is not in the folder') and reading 10 names it in its Q10 list and Q4; recording it as reading-10-only understated what both readings say. No expected value or kind changed in any row; the row zr-35-sections already recorded the governing-chapter point as 'both readings' and is left as it is. Reason: a corrected reading - the agreed list must hold only, and all of, what both readings name. | rules-engineer (M4-T032) |
| 2026-10-08 | Step P5 (task M4-T035): row zr-34-23-sections is marked superseded_by cases/step-p5-worked.json row zr-34-23-page, which holds the current reading of the ZR 34-23 page. The step-P5 readers both had the ZR 34-23 contents capture (which the step-P4 reading 9 did not) and read it as the complete three-subsection list (ZR 34-231, 34-232, 34-233), resolving reading 9's completeness caveat; the conclusion is unchanged (front yard, side yard, change of use; none speaks of the rear yard). Kept as the historical record, and the loader no longer hands it out as current. No expected value or kind changed. Reason: a corrected reading - one current expected answer per question. | rules-engineer (M4-T035) |

