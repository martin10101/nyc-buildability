# Worked from the step-P5 captures: the mixed-building floor-area sections ZR 35-30 to 35-33 with the shared-floor-area rule; the floor-area-ratio definition; ZR 23-24 and the ZR 34-23 page; the ZR 12-10 energy, building and story definitions; the parking, loading and bicycle sections and a line per development option; and the benchmark lot's rear yard read from ZR 23-342 and 23-344

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: backlog row DB-184 (first piece) and DB-185 (b); owner directive D-090 R291, R513, R516, R526, R548.

The R6B reference-case readings of the 46 Zoning Resolution texts captured by tasks M4-T033 and M4-T034, read independently in step P5 by two AI helpers working alone from a sealed folder: the mixed-building floor-area sections ZR 35-30 to 35-33 (with ZR 35-31's shared-floor-area rule) and the floor-area-ratio definition, worked for a made-up mixed building of shops below standard residences; ZR 23-24 and the ZR 34-23 page (ZR 34-231 to 34-233); the ZR 12-10 definitions of a fully electrified building, an ultra-low-energy building, a building and a story; the fourteen parking, loading-berth and bicycle-parking sections and what each of seven development options' parking, loading and bicycle line may say; and the benchmark lot's rear yard read from ZR 23-342 and ZR 23-344. A value or a yes/no is recorded only where both readings give it on the same basis; otherwise the row is not known or not sure with both readings named and what would settle it. Every value comes from the two independent readings and the law text, never from a program run.

## What this case is worth

Read independently by two AI helpers, each working alone from the sealed step-P5 folder; their agreement alone is not proof. It is a draft reading of the law by an AI helper, not professionally reviewed, and is not a statement that anything complies. A second AI read the same sealed folder and worked the same questions. Where the two readings differ, or one holds an answer subject to a text or a fact the readers did not have, the row says so and names both readings; where the text does not settle a point the row says not sure or not known and names what would settle it. A figure taken from one dataset, such as the served transit-zone value, is a recorded value, not a rule.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of all 156 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, two made-up lots and one made-up mixed building, with no access to the program (reading 1: provenance/return-independent-hand-calculation-11.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same questions (reading 2: provenance/return-independent-hand-calculation-12.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Made-up mixed building | a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) | the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property |
| Made-up interior lot | 100 ft by 100 ft (10,000 sq ft), plain R6B, one street, standard residences | the readings' made-up interior 100-by-100 lot (made_up_lots.json) |
| Served transit zone | Outer Transit Zone (a recorded value, not a rule) | NYC PLUTO row for BBL 4073340070, field transitzone |
| Lot type | corner (two street frontages, Northern Boulevard and 215 Place, meeting at about 89.7 degrees) | the recorded outline and DCM centerlines; cases/real-lot.json row L9 |

## Rows

### mixed-use-sections - What each of ZR 35-30, 35-31, 35-32 and 35-33 says, and whether it reaches a building of shops below standard residences in a C2-2 district mapped within R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-30 (Applicability of floor area and open space regulations) - captured.
  - Capture: snapshot `zr-35-30`, file `docs/research/zr-snapshots/v1/zr-35-30.snapshot.json`.
  - Content digest: `b1102df91cae9eaeced5f6a7bae0519c9e8db24a2c2df64654cbaa086fce2def`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-30.
  - Quoted: "35-30 APPLICABILITY OF FLOOR AREA AND OPEN SPACE REGULATIONS"
- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "In the districts indicated, the provisions of this Section shall apply to any #zoning lot# subject to the provisions of this Chapter."
- ZR 35-32 (Maximum Floor Area for Mixed Buildings on Qualifying Residential Sites) - captured.
  - Capture: snapshot `zr-35-32`, file `docs/research/zr-snapshots/v1/zr-35-32.snapshot.json`.
  - Content digest: `d1aad127c4ea150d3d6c388dbb40b5699c46912673f97c3a2b4723273e03c42a`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-32.
  - Quoted: "On #qualifying residential sites#, subject to the individual maximum #floor area ratios# for #commercial#, #community facility# and #residential uses#, the maximum #floor area ratio# for a #zoning lot# with #buildings# containing #residential# and non-#residential uses#, shall be as set forth in this Section."
- ZR 35-33 (Maximum Floor Area ... Community Facility Use in Certain Districts) - captured.
  - Capture: snapshot `zr-35-33`, file `docs/research/zr-snapshots/v1/zr-35-33.snapshot.json`.
  - Content digest: `de947f0a4270dafcc9a34c4f8e8728b5365e88520e23946efce8fd45c86ef8e4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-33.
  - Quoted: "In C1 and C2 Districts mapped within R6 Districts without a letter suffix, and in R7-1 Districts, the provisions of this Section shall apply to any #zoning lot# where #residential# and #community facility# #uses# are located within the same #building#."

Why the rule applies: ZR 35-30 is a title-only umbrella heading; its operative rules live in ZR 35-31 to 35-33. ZR 35-31 (districts C1 to C6) governs the floor area of any commercial-district zoning lot and so reaches the C2-2 overlay. ZR 35-32 applies only on qualifying residential sites, which a C2-2 overlay mapped within R6B is not (that term reaches R1 to R5, C1/C2/C4 mapped within R1 to R5, or M1 paired with R1 to R5). ZR 35-33 applies to C1 or C2 mapped within R6 WITHOUT a letter suffix (or R7-1) for residential-and-community-facility buildings; R6B carries the letter suffix 'B' and the made-up building has commercial, not community-facility, use.

Expected value: ZR 35-30 is a title-only umbrella heading (no operative rule of its own). ZR 35-31 governs this building's floor area (a C1 to C6 section reaching the C2-2 overlay). ZR 35-32 does not reach it, because it applies only on qualifying residential sites and this C2-2 overlay within R6B is not one; reading 11 notes full confirmation would turn on the R1-to-R5 mapping, which the facts show is R6B. ZR 35-33 does not reach it on two grounds: it is for C1 or C2 mapped within R6 WITHOUT a letter suffix (and R6B has the 'B' suffix), and it is for residential-and-community-facility buildings, while this building has commercial (shop) use. So ZR 35-31 is the governing floor-area section

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1a (35-30 umbrella; 35-31 governs; 35-32 qualifying-residential-site only; 35-33 R6-no-suffix community-facility only) and return-independent-hand-calculation-12.md Q1a (same, section by section); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads which section governs the floor area; it asserts no floor-area figure. It says nothing complies.

### mixed-use-floor-area-combination - How the floor areas of the uses of a mixed building combine: a maximum for each use, a maximum for the whole, or both

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "The maximum #floor area ratio# permitted for a #commercial# or #community facility# #use# shall be as set forth in Article III, Chapter 3, and the maximum #floor area ratio# permitted for a #residential use# shall be as set forth in Article II, Chapter 3"
- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "The total of all such #floor area ratios# shall not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#, except where explicitly stated otherwise."
- ZR 23-20 (Floor Area Regulations) - captured.
  - Capture: snapshot `zr-23-20`, file `docs/research/zr-snapshots/v1/zr-23-20.snapshot.json`.
  - Content digest: `0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20.
  - Quoted: "The total of all such #floor area ratios# shall not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#."

Why the rule applies: ZR 35-31 sets a separate maximum floor area ratio for each use (commercial or community facility to Article III, Chapter 3; residential to Article II, Chapter 3) and a single combined cap for the whole zoning lot (the total of the use floor area ratios may not exceed the greatest one permitted for any single use). ZR 23-20 states the same for multi-use zoning lots.

Expected value: Both: a separate maximum floor area ratio for each use AND one combined cap for the whole zoning lot. Each use has its own maximum floor area ratio (commercial or community facility per Article III, Chapter 3; residential per Article II, Chapter 3), and the total of all the use floor area ratios may not exceed the greatest floor area ratio permitted for any single use on the zoning lot (ZR 35-31, and ZR 23-20 in the same words)

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1b (per-use maximum plus a combined cap; 23-20 the same) and return-independent-hand-calculation-12.md Q1b (both: a separate maximum for each use and one combined cap); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states how the caps combine, not any figure. It says nothing complies.

### shared-floor-area-rule - The rule on floor area shared by several uses, and the base of the proportion as the text words it

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "Where #floor area# in a #building# is shared by multiple #uses#, the #floor area# for such shared portion shall be attributed to each #use# proportionately, based on the percentage each #use# occupies of the total #floor area# of the #zoning lot# less any shared #floor area#."
- ZR 23-20 (Floor Area Regulations) - captured.
  - Capture: snapshot `zr-23-20`, file `docs/research/zr-snapshots/v1/zr-23-20.snapshot.json`.
  - Content digest: `0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20.
  - Quoted: "Where #floor area# in a #building# is shared by multiple #uses#, the #floor area# for such shared portion shall be attributed to each #use# proportionately, based on the percentage each #use# occupies of the total #floor area# of the #zoning lot#, less any shared #floor area#."

Why the rule applies: ZR 35-31 (and ZR 23-20 in almost identical words) attributes shared floor area to each use proportionately, and names the base of the proportion: the percentage each use occupies of the total floor area of the zoning lot less the shared floor area.

Expected value: Shared floor area is attributed to each use proportionately. The text names the base of the proportion: each use as a percentage of the total floor area of the zoning lot LESS any shared floor area (ZR 35-31; ZR 23-20 in the same words, with a comma before 'less'). So the base is the total floor area minus the shared floor area, not the full total

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1c (attributed proportionately; base = total floor area of the zoning lot less shared; base is named) and return-independent-hand-calculation-12.md Q1c (same; the base is named; a full-total base is not what the words allow); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the attribution rule and its base; it computes nothing here. It says nothing complies.

### made-up-mixed-shared-attribution - The made-up mixed building worked by hand: the 400 sq ft shared portion attributed to each use

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "the #floor area# for such shared portion shall be attributed to each #use# proportionately, based on the percentage each #use# occupies of the total #floor area# of the #zoning lot# less any shared #floor area#"

Why the rule applies: Worked from ZR 35-31's own words for the made-up mixed building: the base is the total floor area of the zoning lot less the shared portion = 20,500 - 400 = 20,100 sq ft; each use's percentage of that base is its exclusive floor area (commercial 4,200; residential 15,900); the 400 shared sq ft is split in those proportions. No value comes from a program run.

Expected value: Commercial gets 400 x (4,200 / 20,100) = 83.58 sq ft; residential gets 400 x (15,900 / 20,100) = 316.42 sq ft (sum 400.00). So the commercial attributed total is 4,200 + 83.58 = 4,283.58 sq ft and the residential attributed total is 15,900 + 316.42 = 16,216.42 sq ft (sum 20,500.00). The base is the total floor area less the shared 400, per ZR 35-31

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1d(i) (base 20,100; commercial 83.58, residential 316.42; totals 4,283.58 and 16,216.42) and return-independent-hand-calculation-12.md Q1d(i) (same figures; the 'less shared' base distributes the full 400); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It is worked by hand from ZR 35-31 for a made-up building, not a real property, and not from a program run. It says nothing complies.

### made-up-mixed-residential-far - The made-up mixed building: the residential floor area ratio and floor area the text gives, and where from

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "the maximum #floor area ratio# permitted for a #residential use# shall be as set forth in Article II, Chapter 3"
- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum #residential# #floor area ratio# shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: ZR 35-31 sends the residential floor area ratio to Article II, Chapter 3, i.e. ZR 23-22; its R6B row for standard residences is 2.00. The maximum residential floor area is the floor area ratio times the lot area (2.00 x 10,000). The R6B row carries no within-100-feet-of-a-wide-street footnote.

Working, step by step:

- maximum residential floor area (floor area ratio x lot area): 2.00 (floor area ratio (R6B standard residences, ZR 23-22)) x 10,000 (lot area (square feet)) = 20,000

Expected value: The residential floor area ratio is 2.00 (ZR 23-22, R6B standard residences, reached through ZR 35-31's reference to Article II, Chapter 3), so the maximum residential floor area is 2.00 x 10,000 = 20,000 sq ft. The residential attributed figure (16,216.42 sq ft) is under 20,000 sq ft

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1d(ii) (residential FAR 2.00 via 35-31 to Article II Ch 3 / 23-22; 2.00 x 10,000 = 20,000; attributed 16,216.42 is under it) and return-independent-hand-calculation-12.md Q1d(ii) (same, 23-22 via 35-22/34-111; 20,000 sq ft); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It gives the legal maximum residential floor area, not a design and not a verdict. It says nothing complies.

### made-up-mixed-commercial-far - The made-up mixed building: the commercial floor area ratio (both readers say which text they did not have)

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "The maximum #floor area ratio# permitted for a #commercial# or #community facility# #use# shall be as set forth in Article III, Chapter 3"

Why the rule applies: ZR 35-31 sends the commercial floor area ratio to Article III, Chapter 3. Both readers say that Article III, Chapter 3 (the commercial-district maximum floor area ratio, e.g. ZR 33-12 / 33-121) was not in their folder, so the maximum commercial floor area ratio cannot be read.

Expected value: not known. ZR 35-31 sends the commercial floor area ratio to Article III, Chapter 3, which both readers say they did not have (reading 11 and reading 12 both name Article III, Chapter 3 as not in the folder). So the maximum commercial floor area ratio is not known; it would be settled by Article III, Chapter 3 (the commercial-district maximum floor area ratio).

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1d(iii)/Q8 (commercial FAR not known; Article III, Chapter 3 not in the folder) and return-independent-hand-calculation-12.md Q1d(iii)/Q8 (same; STOP at not known, Article III Ch 3 not in folder); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It names what would settle the commercial floor area ratio; it reads no figure. It says nothing complies.

### made-up-mixed-whole-building-max - The made-up mixed building: the maximum for the building as a whole

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "The total of all such #floor area ratios# shall not exceed the greatest #floor area ratio# permitted for any such #use# on the #zoning lot#, except where explicitly stated otherwise."

Why the rule applies: ZR 35-31's whole-lot cap is the greatest floor area ratio permitted for any single use on the zoning lot, i.e. the greater of the residential floor area ratio (2.00) and the commercial floor area ratio. The commercial floor area ratio is not known (Article III, Chapter 3 not in the folder), so the greatest permitted, and the whole-building maximum, cannot be read.

Expected value: not known. The whole-lot cap is the greatest floor area ratio permitted for any single use (ZR 35-31). That is the greater of the residential 2.00 and the commercial floor area ratio, which is not known because Article III, Chapter 3 is not in the folder (both readings). So the cap is at least 2.00 but its exact value is not known; it would be settled by Article III, Chapter 3. The building's own total is 20,500 / 10,000 = 2.05, but whether that is at or under the cap cannot be read.

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q1d(iv) (whole-lot cap = greater of 2.00 and the unknown commercial FAR; not known; 2.05 actual) and return-independent-hand-calculation-12.md Q1d(iv) (same; greatest permitted not known, Article III Ch 3 not in folder); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It names what would settle the whole-building maximum; it reaches no figure and gives no verdict. It says nothing complies.

### floor-area-ratio-definition - The definition of floor area ratio

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - floor area ratio) - captured.
  - Capture: snapshot `zr-12-10-floor-area-ratio`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area-ratio.snapshot.json`.
  - Content digest: `11e7a3dc9f57ba1718ec5edfebb7aeb0fa6e61698228f70a170c1649d354c8d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the total #floor area# on a #zoning lot#, divided by the #lot area# of that #zoning lot#"
- ZR 12-10 (Definitions - floor area ratio) - captured.
  - Capture: snapshot `zr-12-10-floor-area-ratio`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area-ratio.snapshot.json`.
  - Content digest: `11e7a3dc9f57ba1718ec5edfebb7aeb0fa6e61698228f70a170c1649d354c8d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "a #zoning lot# of 10,000 square feet with a #building# containing 20,000 square feet of #floor area# has a #floor area ratio# of 2.0"

Why the rule applies: ZR 12-10 defines floor area ratio as the total floor area on a zoning lot divided by the lot area of that zoning lot (the sum of the floor areas where there are two or more buildings), and gives the worked example of a 10,000-square-foot lot with 20,000 square feet of floor area at a ratio of 2.0.

Expected value: Floor area ratio is the total floor area on a zoning lot divided by the lot area of that zoning lot (the sum of the buildings' floor areas, divided by the lot area, where there is more than one building). The definition's own example is a 10,000-square-foot lot with a building of 20,000 square feet of floor area at a floor area ratio of 2.0

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q2a (FAR = total floor area / lot area; the example) and return-independent-hand-calculation-12.md Q2 (FAR = total floor area / lot area; the definition's example); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the definition; what counts as floor area turns on the long ZR 12-10 floor-area inclusion and exclusion list. It says nothing complies.

### floor-area-ratio-made-up-100x100 - Whether 'floor area = ratio x lot area' is settled for the made-up 100 ft by 100 ft lot

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one street, standard residences (source: the readings' made-up interior 100-by-100 lot (made_up_lots.json))

Law relied on:

- ZR 12-10 (Definitions - floor area ratio) - captured.
  - Capture: snapshot `zr-12-10-floor-area-ratio`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area-ratio.snapshot.json`.
  - Content digest: `11e7a3dc9f57ba1718ec5edfebb7aeb0fa6e61698228f70a170c1649d354c8d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the total #floor area# on a #zoning lot#, divided by the #lot area# of that #zoning lot#"
- ZR 23-22 (Floor Area Regulations for R6 Through R12 Districts) - captured.
  - Capture: snapshot `zr-23-22`, file `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json`.
  - Content digest: `943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22.
  - Quoted: "the maximum #residential# #floor area ratio# shall be as set forth in the following table"
  - From the captured table, district R6B: standard_residences = 2.00.

Why the rule applies: With the floor-area-ratio definition in hand, the rearrangement is exact: floor area ratio = total floor area / lot area, so maximum total floor area = maximum floor area ratio x lot area. For the made-up 100-by-100 lot (10,000 sq ft, plain R6B standard residences, floor area ratio 2.00 from ZR 23-22) that is 2.00 x 10,000 = 20,000 sq ft, the definition's own worked example.

Working, step by step:

- maximum residential floor area (floor area ratio x lot area): 2.00 (floor area ratio (R6B standard residences, ZR 23-22)) x 10,000 (lot area (square feet)) = 20,000

Expected value: Yes, settled. With the floor-area-ratio definition now had, floor area = ratio x lot area is exact: 2.00 x 10,000 = 20,000 sq ft of maximum residential floor area for the made-up 100-by-100 lot, matching the definition's own worked example. This is the floor-area-ratio definition the step-P4 readers did not have (which held the step-P4 unit-count row cases/step-p4-worked.json row made-up-100x100-units subject to it); the step-P5 readers had it and confirm the floor-area basis. This row settles only the floor area, not the dwelling-unit count

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q2b (floor area = ratio x lot area settled; 2.00 x 10,000 = 20,000; the definition settles the arithmetic) and return-independent-hand-calculation-12.md Q2 (settled by the text; 2.00 x 10,000 = 20,000; no word leaves the arithmetic open); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It settles the floor area for the made-up 100-by-100 lot, not the dwelling-unit count: the count stays at cases/step-p4-worked.json row made-up-100x100-units (29, held by the step-P4 readers), which neither step-P5 reading re-works. It is a made-up lot, not a real property. It says nothing complies.

### zr-23-24-reach - ZR 23-24: what its own text holds, and what it leaves to sections the readers did not have

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 23-24 (Special Provisions for Certain Areas) - captured.
  - Capture: snapshot `zr-23-24`, file `docs/research/zr-snapshots/v1/zr-23-24.snapshot.json`.
  - Content digest: `9849955d356a8d28c4cfd5d8c493ba4bf40177650c352c8ffa53284a7fa043b1`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-24.
  - Quoted: "23-24 Special Provisions for Certain Areas"
- ZR 23-20 (Floor Area Regulations) - captured.
  - Capture: snapshot `zr-23-20`, file `docs/research/zr-snapshots/v1/zr-23-20.snapshot.json`.
  - Content digest: `0685a2e4e7002830a1c007dea23ac68c5c441f1a32eeb2e37b78000c5765d7cc`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-20.
  - Quoted: "Special rules governing certain areas are set forth in Section 23-24."

Why the rule applies: The ZR 23-24 capture holds only its title line; ZR 23-20 points to it ('Special rules governing certain areas are set forth in Section 23-24'). Its operative rules live in numbered subsections (23-241 and following) that the readers did not have, so whether it reaches the lot cannot be read.

Expected value: not known. ZR 23-24 by its own captured words is a title-only heading and states no district, area or lot. Its operative subsections (ZR 23-241 and following) are not in the folder (the readers did not have them), so whether any special-area rule under ZR 23-24 reaches this R6B lot with its C2-2 overlay is not known. It would be settled by the ZR 23-24 subsections (ZR 23-241 and following). Both readings reach this not-known result.

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q3 (23-24 header only; children 23-241/242/243 not in folder; not known) and return-independent-hand-calculation-12.md Q3 (same; title-only heading; subsections not in the folder); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It names what would settle ZR 23-24's reach; it reaches no conclusion. It says nothing complies.

### zr-34-23-page - The page of ZR 34-23 with ZR 34-231 to 34-233 (front yard, side yard, change of use), and whether any speaks of the rear yard

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Building = a new all-residential building in the C2-2 overlay (source: the subject of the readings' yard question)

Law relied on:

- ZR 34-23 (Modification of Yard and Open Area Regulations) - captured.
  - Capture: snapshot `zr-34-23`, file `docs/research/zr-snapshots/v1/zr-34-23.snapshot.json`.
  - Content digest: `4f6975364cc414188005c5270c41d9b3a420d36dde8339fb325cf1701646f97d`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-23.
  - Quoted: "34-23 Modification of Yard and Open Area Regulations"
- ZR 34-23-contents (Contents of ZR 34-23) - captured.
  - Capture: snapshot `zr-34-23-contents`, file `docs/research/zr-snapshots/v1/zr-34-23-contents.snapshot.json`.
  - Content digest: `6ebe91583ff11f7958110fb4961437d87331a218a7c98965b0fe54e6df747351`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4.
  - Quoted: "34-233 Change of use"
- ZR 34-231 (Modification of front yard requirements) - captured.
  - Capture: snapshot `zr-34-231`, file `docs/research/zr-snapshots/v1/zr-34-231.snapshot.json`.
  - Content digest: `df20f8891b079072dd9ead1aa47df1188df132760344cccba361c9dbe57d5ed8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-231.
  - Quoted: "In the districts indicated, no #front yard# shall be required for any #residential building#."
- ZR 34-232 (Modification of side yard requirements) - captured.
  - Capture: snapshot `zr-34-232`, file `docs/research/zr-snapshots/v1/zr-34-232.snapshot.json`.
  - Content digest: `9cf83f8d9c3fa6f594fa3be1e1d65651713c1809254fd08e60e527daa09c61b2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-232.
  - Quoted: "In the districts indicated, no #side yard# shall be required for any #residential building#. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."
- ZR 34-233 (Change of use) - captured.
  - Capture: snapshot `zr-34-233`, file `docs/research/zr-snapshots/v1/zr-34-233.snapshot.json`.
  - Content digest: `0668220dd22e4dfe7af33972f7197839a1f662432f55a37322376d46e12a5815`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-4/34-233.
  - Quoted: "A non-#residential use# occupying a #building#, or portion thereof, that was in existence on December 15, 1961, may be changed to a #residential use# and the regulations pertaining to minimum required #open space ratio# shall not apply to such change of #use#."

Why the rule applies: ZR 34-23 is a header; the ZR 34-23 contents capture lists exactly three subsections (ZR 34-231 front yard, 34-232 side yard, 34-233 change of use), which both readers read as the complete set. ZR 34-231 removes the front yard and 34-232 the side yard for a residential building; 34-233 is a change of use of a pre-December-15-1961 building (open space ratio). None speaks of the rear yard.

Expected value: ZR 34-23 is a header, and its contents capture lists exactly three subsections, which both readers read as the complete set: ZR 34-231 requires no front yard for a residential building; ZR 34-232 requires no side yard (any provided side open area must be at least five feet wide); ZR 34-233 is a change of use of a building in existence on December 15, 1961 (open space ratio), which does not reach a new building. None of the three speaks of the rear yard. The step-P5 readers both had the ZR 34-23 contents capture and read it as the complete list, resolving the completeness caveat reading 9 raised in step P4

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q4 (34-23 contents = 34-231/232/233; front, side, change of use; none is a rear-yard section) and return-independent-hand-calculation-12.md Q4 (34-23-contents lists exactly three; no rear-yard subsection); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the ZR 34-23 page; it sets no yard depth. For the rear yard of an all-residential building it leaves the result to the R6B rules. It says nothing complies.

### benchmark-rear-yard-23-342-23-344 - The benchmark lot's rear yard, read from ZR 23-342 and ZR 23-344: the corner, the angle, the reach, where no rear yard is required, and the part beyond 100 feet

Facts used:

- Lot type = corner (two street frontages, Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: the recorded outline and DCM centerlines; cases/real-lot.json row L9)
- Farthest point from the corner point = about 144.60 ft (both readings; reading 11 vertex v0, reading 12 vertex P0) (source: both readings from the recorded outline (return-independent-hand-calculation-11.md Q5a; return-independent-hand-calculation-12.md Q5a))
- Street lines = Northern Boulevard and 215 Place, meeting at the corner point at about 89.7 degrees (source: both readings from the outline and DCM centerlines (return-independent-hand-calculation-11.md Q5a; return-independent-hand-calculation-12.md Q5a))
- Reach from each street line = readings differ: reading 11 finds the lot reaches about 101 to 103 ft from each street line (a small sliver of the west edge beyond 100 ft of the Northern Boulevard line); reading 12 finds about 100 ft from the Northern Boulevard line (no west-edge sliver) and about 104 ft from the 215 Place line (source: the two readings (return-independent-hand-calculation-11.md Q5a; return-independent-hand-calculation-12.md Q5a))

Law relied on:

- ZR 23-344 (Additional rear yard modifications (within 100 feet of corners)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less."
- ZR 23-344 (Additional rear yard modifications (beyond 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply along such #rear lot line#"
- ZR 23-344 (Additional rear yard modifications (R6-R12, side-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#."
- ZR 23-344 (Additional rear yard modifications (rear-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "a #rear yard# shall be provided in accordance with Section 23-342 (Rear yard requirements), where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#."
- ZR 23-342 (Rear yard requirements) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#"
- ZR 12-10 (Definitions - corner lot) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."
- ZR 12-10 (Definitions - rear yard) - captured.
  - Capture: snapshot `zr-12-10-yard-rear`, file `docs/research/zr-snapshots/v1/zr-12-10-yard-rear.snapshot.json`.
  - Content digest: `917264446f1ad123d8f2442836d5c885211efb36bdfff50b63099897ae26f330`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #yard# extending for the full length of a #rear lot line#."
- ZR 12-10 (Definitions - rear lot line) - captured.
  - Capture: snapshot `zr-12-10-lot-line-rear`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-line-rear.snapshot.json`.
  - Content digest: `d34da91dcfa8392e655806a06204621c80175de99a034d983b978cb73e45c86b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is any #lot line# of a #zoning lot# except a #front lot line#, which is parallel or within 45 degrees of being parallel to, and does not intersect, any #street line# bounding such #zoning lot#."

Why the rule applies: The two street lines meet at the corner point at about 89.7 degrees (135 or less), so ZR 23-344(a) requires no rear yard within 100 feet of the corner point. Beyond 100 feet a rear yard attaches only to a rear lot line; under the ZR 12-10 base definition this corner lot has none (each non-street edge intersects a street line), and ZR 23-344(c) constructs a rear lot line only along the portion of a side lot line beyond 100 feet of the street line it intersects. Where such a deemed rear lot line meets an adjoining lot's rear lot line a 20-foot rear yard (ZR 23-342) is required; where it meets an adjoining lot's side lot line none is required (ZR 23-344(c)(3)); which it is turns on the adjoining zoning lots, which the readers did not have.

Expected value: not known. Within 100 feet of the corner point no rear yard is required: the two street lines (Northern Boulevard and 215 Place) meet at about 89.7 degrees, which is 135 or less, so ZR 23-344(a) applies. Beyond 100 feet the result is not known. The readers differ on the geometry: reading 11 finds small slivers beyond 100 feet of a street line on both non-street edges (the west edge reaches about 101 ft from the Northern Boulevard line), while reading 12 finds the west edge reaches only about 100 ft from the Northern Boulevard line (no sliver) and only the far roughly 4-foot tip of the south edge lies beyond 100 feet of the 215 Place line. Both agree that along any such deemed rear lot line (ZR 23-344(c)) whether a 20-foot rear yard (ZR 23-342) is required turns on the adjoining zoning lot's lot-line type (ZR 23-344(c)(1) rear-lot-line coincidence versus (c)(3) side-lot-line coincidence), which the readers did not have. The standing not-known for the part beyond the corner is held by cases/step-p3-worked.json row real-lot-rear-yard-beyond-corner; this row does not re-answer it. It would be settled by the adjoining zoning lots' lot-line types.

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q5 (no rear yard within 100 ft of the ~90-degree corner; beyond, deemed rear lot lines on the far slivers, not known on the adjoining lots) and return-independent-hand-calculation-12.md Q5 (same; no rear yard within 100 ft of P2; the far ~4-ft tip of E3 a deemed rear lot line, (c)(3) vs (c)(1) turns on the neighbour, not known); the readings differ on whether the west edge reaches beyond 100 ft of the Northern Boulevard line; both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It gives no rear-yard requirement beyond the corner (that turns on the adjoining zoning lots' lot-line types, which the readers did not have, and the readings differ on the far-edge reach). It changes no program output and no fixture, and it uses the approximate recorded outline. It says nothing complies.

### fully-electrified-building-definition - The 'fully electrified building' definition: every condition, the evidence it needs, and whether a proposed building can be one

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - fully electrified building) - captured.
  - Capture: snapshot `zr-12-10-fully-electrified-building`, file `docs/research/zr-snapshots/v1/zr-12-10-fully-electrified-building.snapshot.json`.
  - Content digest: `2ea4afe29ec1037695e8df5e6d90bd313e611b3db2949b61cc9e115ceac9321c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #building# existing on December 6, 2023 which complies with the requirements of Local Law 154 of 2021, as such requirements would apply to a new #building# where an application for the approval of construction documents is submitted to the Commissioner of Buildings after July 1, 2027."

Why the rule applies: ZR 12-10 defines a fully electrified building by two conditions: the building existed on December 6, 2023, and it complies with Local Law 154 of 2021 as that law would apply to a new building filing construction documents after July 1, 2027. A building that does not yet exist did not exist on December 6, 2023.

Expected value: Two conditions: (1) the building EXISTED on December 6, 2023 - evidence: a proof of existence on that date, such as a certificate of occupancy predating it; and (2) it complies with Local Law 154 of 2021 as that law would apply to a new building filing construction documents after July 1, 2027 - evidence: a Local Law 154 compliance filing. The substance of Local Law 154 was not in the folder. A new, only-proposed building cannot be a fully electrified building, because it did not exist on December 6, 2023. An owner's or user's statement does not establish either condition

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q6a/Q6c (existing on 12/6/2023 + LL154 compliance; a new building cannot be one) and return-independent-hand-calculation-12.md Q6(a)/(c) (existing 12/6/2023, LL154-compliant; a new proposed building cannot be one); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the definition's conditions and the evidence each needs; the substance of Local Law 154 was not in the folder. It says nothing complies.

### ultra-low-energy-building-definition - The 'ultra-low-energy building' definition: every condition, the evidence it needs, and whether a proposed building can be one

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "shall refer to a #building# which complies with requirements for ultra-low-energy usage. At time of application for plan approval to the Commissioner of Buildings, materials shall be submitted demonstrating:"
- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "that such #building# shall comply with the requirements of Local Law 154 of 2021"
- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "energy performance that exceeds by at least 15 percent the energy performance of such a #building# if designed and constructed according to an approved modeling method set forth in the New York City Energy Conservation Code."
- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "that a registered design professional has verified that the proposed design will meet the requirements of this definition"
- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "No final certificate of occupancy shall be issued for such a #building# until a report prepared by a registered design professional has been submitted to the Commissioner of Buildings verifying that the #building# has completed and successfully passed the inspections, commissioning, and testing"

Why the rule applies: ZR 12-10 writes the ultra-low-energy building around materials submitted at plan approval: Local Law 154 compliance; an energy-performance target (net-zero for buildings of three stories or less, otherwise at least 15 percent better than the New York City Energy Conservation Code model); a registered design professional's verification of the design; and prepared inspection, commissioning and airtightness-testing plans. No final certificate of occupancy issues until a registered design professional reports the building passed those inspections, commissioning and testing. The made-up building is four stories, so the at-least-15-percent path (not the net-zero path) would apply if pursued.

Expected value: The conditions, each with the evidence it needs: (1) Local Law 154 of 2021 compliance - a filing; (2) an energy-performance target - for buildings of three stories or less a net-zero energy building producing on-site renewable energy at least equal to its needs, and for all other buildings energy performance at least 15 percent better than the New York City Energy Conservation Code model - a measured or modelled performance; (3) a registered design professional's verification that the proposed design will meet the definition - a professional's statement; and (4) prepared inspection, equipment-commissioning and airtightness-testing plans - a filing; and before any final certificate of occupancy, a registered design professional's report that the building passed those inspections, commissioning and testing. A new, only-proposed building CAN be put forward as ultra-low-energy at plan approval, but is only finally confirmed by the post-construction report at the final certificate of occupancy. An owner's or user's statement does not establish eligibility; the registered design professional's verification does. The made-up four-storey building would take the at-least-15-percent path, not the net-zero path

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q6a/Q6c (plan-approval materials, LL154, net-zero or 15 percent, RDP verification, test plans, final-CO report; provisional at plan approval, confirmed at CO) and return-independent-hand-calculation-12.md Q6(a)/(c) (same conditions and evidence; provisional at plan approval, confirmed by the post-construction report); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the definition's conditions and evidence; the substance of Local Law 154 and the New York City Energy Conservation Code were not in the folder, and the definition's internal paragraph labels do not line up with its numbered items (both readings flag this). It says nothing complies.

### energy-floor-area-exclusion - The 5 percent of floor area the floor-area definition leaves out for a fully electrified or ultra-low-energy building

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - floor area (exclusion 15)) - captured.
  - Capture: snapshot `zr-12-10-floor-area`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area.snapshot.json`.
  - Content digest: `e14ecafcb5f27861fbfb73264f1d9000b14cac0a5679642dfa8e278d10c1d6f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "floor space within a #fully electrified building# or an #ultra low energy building#, of an amount equivalent to five percent of the #floor area# located within such #building#, and exclusive of any floor space otherwise excluded from #floor area#"

Why the rule applies: The ZR 12-10 floor-area definition excludes, for a fully electrified building or an ultra-low-energy building, floor space equivalent to five percent of the floor area within the building, on top of any other exclusion.

Expected value: A qualifying fully electrified building or ultra-low-energy building may exclude from floor area an amount equal to five percent of the floor area within the building, on top of any floor space otherwise excluded (ZR 12-10 floor-area exclusion 15). The exclusion depends on the building first qualifying under one of the two energy definitions

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q6b (5 percent of the floor area excluded for such buildings) and return-independent-hand-calculation-12.md Q6(b) (floor-area exclusion (15): five percent of the floor area within the building); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the exclusion; it rests on the building qualifying under the energy definitions, which turn on Local Law 154 not in the folder. It says nothing complies.

### proposed-building-energy-eligibility - Whether a building that is only proposed can be treated as a fully electrified or ultra-low-energy building

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 12-10 (Definitions - fully electrified building) - captured.
  - Capture: snapshot `zr-12-10-fully-electrified-building`, file `docs/research/zr-snapshots/v1/zr-12-10-fully-electrified-building.snapshot.json`.
  - Content digest: `2ea4afe29ec1037695e8df5e6d90bd313e611b3db2949b61cc9e115ceac9321c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is a #building# existing on December 6, 2023"
- ZR 12-10 (Definitions - ultra-low-energy building) - captured.
  - Capture: snapshot `zr-12-10-ultra-low-energy-building`, file `docs/research/zr-snapshots/v1/zr-12-10-ultra-low-energy-building.snapshot.json`.
  - Content digest: `8a1d64182201fb1085b90b07b6ba35daa1c675388499ab5530e49420f0380203`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "At time of application for plan approval to the Commissioner of Buildings, materials shall be submitted demonstrating:"

Why the rule applies: A fully electrified building must have existed on December 6, 2023, which a new proposed building did not. An ultra-low-energy building is assessed from materials at plan approval and confirmed by a post-construction report, so a proposed building can be put forward as one at plan approval but not finally confirmed until after construction.

Expected value: Fully electrified building: NO - a new, only-proposed building cannot be one, because the definition requires a building existing on December 6, 2023. Ultra-low-energy building: provisionally YES at plan approval - the definition is written around materials submitted at plan approval and a registered design professional's verification of the proposed design - but only finally confirmed by the registered design professional's post-construction report before the final certificate of occupancy. A proposed status supports only a conditional result, never a settled one

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q6c (fully electrified no; ultra-low-energy provisional at plan approval, confirmed at CO) and return-independent-hand-calculation-12.md Q6(c) (same; fully electrified no, ultra-low-energy provisional then confirmed at CO); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads when each kind can be claimed; it confirms nothing about any particular building. It says nothing complies.

### building-and-story-definitions - What the definitions of a building and of a story add

Facts used:

- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 12-10 (Definitions - building) - captured.
  - Capture: snapshot `zr-12-10-building`, file `docs/research/zr-snapshots/v1/zr-12-10-building.snapshot.json`.
  - Content digest: `4eb81613913417c2737b593a7c9443ee45ba09f8905d095fc8ab700b86bcdacf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "provides all the vertical circulation and exit systems required for such #building# by the New York City Building Code without reliance on other #buildings#"
- ZR 12-10 (Definitions - building) - captured.
  - Capture: snapshot `zr-12-10-building`, file `docs/research/zr-snapshots/v1/zr-12-10-building.snapshot.json`.
  - Content digest: `4eb81613913417c2737b593a7c9443ee45ba09f8905d095fc8ab700b86bcdacf`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is bounded by open area or #fire walls#"
- ZR 12-10 (Definitions - story) - captured.
  - Capture: snapshot `zr-12-10-story`, file `docs/research/zr-snapshots/v1/zr-12-10-story.snapshot.json`.
  - Content digest: `def60901f65bc02fa1bfffe85e60a25222f42198b2db1cd85dbdd115c94cfe98`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is that part of a #building# between the surface of a floor"
- ZR 12-10 (Definitions - story) - captured.
  - Capture: snapshot `zr-12-10-story`, file `docs/research/zr-snapshots/v1/zr-12-10-story.snapshot.json`.
  - Content digest: `def60901f65bc02fa1bfffe85e60a25222f42198b2db1cd85dbdd115c94cfe98`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "a #cellar# shall not be considered a #story#. Furthermore, attic space that is not #floor area# pursuant to Section 12-10 (DEFINITIONS) shall not be considered a #story#"

Why the rule applies: ZR 12-10's 'building' definition (its own vertical circulation, exits and fire-protection systems, bounded by open area or fire walls) decides when structures count as one building or several, which matters for the floor-area-ratio rule that sums the floor areas of two or more buildings on one zoning lot. ZR 12-10's 'story' excludes a cellar and non-floor-area attic space.

Expected value: The 'building' definition (its own required vertical circulation, exits and fire-protection systems, bounded by open area or fire walls) decides when structures count as one building or several, which matters because the floor-area-ratio definition sums the floor areas of two or more buildings on one zoning lot; the made-up mixed building is one building, so its 20,500 sq ft is one floor-area total. The 'story' definition excludes a cellar and non-floor-area attic space, so the made-up building (four floors, no cellar) is four stories; because it is more than three stories, the ultra-low-energy at-least-15-percent path, not the net-zero path, would apply if pursued

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q6d (building = one floor-area total; story excludes cellar/attic; four stories) and return-independent-hand-calculation-12.md Q6(d) (building is one structure; story excludes cellar/attic; four stories); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads the two definitions and what they add; it decides nothing about any particular building's systems. It says nothing complies.

### parking-loading-bicycle-sections - Parking, loading berths and bicycle parking, section by section

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 25-02 (Applicability) - captured.
  - Capture: snapshot `zr-25-02`, file `docs/research/zr-snapshots/v1/zr-25-02.snapshot.json`.
  - Content digest: `0865a02c1c479558866064f28c6bd4fe8f8c7985060fe490e7bfb069ce9c3a76`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-02.
  - Quoted: "the regulations of this Chapter on permitted or required #accessory# off-street parking spaces and #accessory# bicycle parking spaces apply to #residences#, #community facility# #uses# or #commercial# #uses#"
- ZR 25-20 (Required accessory off-street parking spaces for residences) - captured.
  - Capture: snapshot `zr-25-20`, file `docs/research/zr-snapshots/v1/zr-25-20.snapshot.json`.
  - Content digest: `666f0d241ef5ac95e22a94f67626636305c2d92caff3bc48f0de250d588f8d07`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-20.
  - Quoted: "Separate requirements are set forth for #zoning lots# in the #Inner Transit Zone# pursuant to Section 25-21, inclusive, the #Outer Transit Zone#, pursuant to Section 25-22, inclusive, and beyond the #Greater Transit Zone#, pursuant to Section 25-23, inclusive."
- ZR 25-211 (General provisions (Inner Transit Zone)) - captured.
  - Capture: snapshot `zr-25-211`, file `docs/research/zr-snapshots/v1/zr-25-211.snapshot.json`.
  - Content digest: `59439d66be5065f6b1ecec8fa9b261a78b9a633732a23f1e1a8da2345ca253b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-211.
  - Quoted: "within the #Inner Transit Zone#, no #accessory# off-street parking spaces shall be required for #dwelling units# or #rooming units# created after December 5, 2024."
- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "within the #Outer Transit Zone#, #accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222. No #accessory# off-street parking spaces shall be required for #rooming units# created as part of a #development# or #enlargement# after March 22, 2016."
- ZR 25-231 (General provisions (beyond the Greater Transit Zone)) - captured.
  - Capture: snapshot `zr-25-231`, file `docs/research/zr-snapshots/v1/zr-25-231.snapshot.json`.
  - Content digest: `8dc7f3d9f4542188435199dfc128cee02bd5ff81b2b3b6133a8b0dc6dc322a6e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-231.
  - Quoted: "No #accessory# off-street parking spaces shall be required for #rooming units# created as part of a #development# or #enlargement# after March 22, 2016."
- ZR 25-80 (Bicycle parking) - captured.
  - Capture: snapshot `zr-25-80`, file `docs/research/zr-snapshots/v1/zr-25-80.snapshot.json`.
  - Content digest: `0861298a6d1e23cc8b4d86c052bca9847c1994f94dd4f8b5c226b1db8cf0e415`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-80.
  - Quoted: "(d) new #dwelling units# in #buildings# or #building segments# constructed after April 22, 2009;"
- ZR 25-81 (Required Bicycle Parking Spaces) - captured.
  - Capture: snapshot `zr-25-81`, file `docs/research/zr-snapshots/v1/zr-25-81.snapshot.json`.
  - Content digest: `e32e804c4395901dc61814f535bddc153d99b9e6cddb7fc4e179db942d3a506c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-81.
  - Quoted: "25-81 Required Bicycle Parking Spaces"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 36-21 (General Provisions (commercial/community-facility parking)) - captured.
  - Capture: snapshot `zr-36-21`, file `docs/research/zr-snapshots/v1/zr-36-21.snapshot.json`.
  - Content digest: `47b2295cbd17b6649f7e9d0554af4d9f62dce54487fefa515c39dec7ecf35537`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21.
  - Quoted: "#accessory# off-street parking spaces, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section for all #developments# after December 15, 1961, for the #commercial# or #community facility# #uses# listed in the table."
- ZR 36-31 (General Provisions (residences in commercial districts)) - captured.
  - Capture: snapshot `zr-36-31`, file `docs/research/zr-snapshots/v1/zr-36-31.snapshot.json`.
  - Content digest: `0f2195e8c9723a235bf7a50b216c6e2cfc06a9c620ae42ee0545d03408bebc6e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-31.
  - Quoted: "#accessory# off-street parking spaces shall be required for #residences# in accordance with the regulations of the #Residence District# such #Commercial District# is mapped within"
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 36-70 (Bicycle parking (commercial districts)) - captured.
  - Capture: snapshot `zr-36-70`, file `docs/research/zr-snapshots/v1/zr-36-70.snapshot.json`.
  - Content digest: `54d01fe44b2bca12a5beb4c5a0853e58b83d43f41b07b12e1fb4719100cc463b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-70.
  - Quoted: "(d) new #dwelling units# in #buildings# or #building segments# constructed after April 22, 2009;"
- ZR 36-71 (Required Bicycle Parking Spaces) - captured.
  - Capture: snapshot `zr-36-71`, file `docs/research/zr-snapshots/v1/zr-36-71.snapshot.json`.
  - Content digest: `17863a1d094c05e0c887f0405a0f8eb3fb5388931987b04df82be813ed81c7a8`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-71.
  - Quoted: "36-71 Required Bicycle Parking Spaces"
- ZR 36-711 (Enclosed bicycle parking spaces (commercial districts)) - captured.
  - Capture: snapshot `zr-36-711`, file `docs/research/zr-snapshots/v1/zr-36-711.snapshot.json`.
  - Content digest: `20414c33264558f386cb58ac6d73a1685b73e4fb35618e6b3463016e7eb43310`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711.
  - Quoted: "Use Groups not specified above, and all other #commercial# #uses# not otherwise listed"

Why the rule applies: Read section by section: ZR 25-02 scopes Chapter 5 parking and bicycle parking to residences, community-facility and commercial uses; ZR 25-20 routes residence parking by transit geography (Inner 25-21, Outer 25-22, beyond 25-23); ZR 25-211 requires none in the Inner Transit Zone for units created after December 5, 2024; ZR 25-221 requires parking for new Outer-Transit-Zone dwelling units per 25-222 and none for new rooming units; ZR 25-231 the same beyond the Greater Transit Zone; ZR 25-80 lists the bicycle-parking triggers; ZR 25-81/25-811 give the residential and community-facility bicycle table and a 10-dwelling-unit waiver; ZR 36-21 the commercial and community-facility parking table; ZR 36-31 sends residences in commercial districts to the surrounding residence district; ZR 36-62 the loading-berth table; and ZR 36-70/36-71/36-711 the commercial, community-facility and residential bicycle table.

Expected value: Section by section, from the captured words: ZR 25-02 applies Chapter 5 parking and bicycle parking to residences, community-facility and commercial uses. ZR 25-20 routes residence parking by geography (Inner 25-21, Outer 25-22, beyond the Greater Transit Zone 25-23). ZR 25-211: in the Inner Transit Zone no parking for units created after December 5, 2024. ZR 25-221: in the Outer Transit Zone parking is required for new dwelling units (per the missing 25-222) and none for new rooming units (after March 22, 2016). ZR 25-231: the same beyond the Greater Transit Zone (per the missing 25-232). ZR 25-80 lists the bicycle triggers (developments, 50-percent enlargements, conversions, new dwelling units after April 22, 2009, large parking facilities). ZR 25-81/25-811 give the residential bicycle rate (1 per two dwelling units; affordable independent residences for seniors 1 per 10,000 square feet) and waive buildings of 10 dwelling units or less. ZR 36-21 is the commercial and community-facility parking table; ZR 36-31 sends residences in commercial districts to the surrounding residence district (and waives parking for qualifying residential sites in the Greater Transit Zone). ZR 36-62 is the loading-berth table; ZR 36-70/36-71/36-711 the commercial, community-facility and residential bicycle table

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7a (section by section) and return-independent-hand-calculation-12.md Q7(a) (section by section); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It reads what each section says, not what applies to any option; the applicability per option is in the option rows. It says nothing complies.

### transit-zone-value - What the served transit-zone value is, and whether the captured definitions let it settle the zone

Facts used:

- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 12-10 (Definitions - Outer Transit Zone) - captured.
  - Capture: snapshot `zr-12-10-transit-zone-outer`, file `docs/research/zr-snapshots/v1/zr-12-10-transit-zone-outer.snapshot.json`.
  - Content digest: `692690b9e28d8f8109fb417494ee9264485cee084f54b7868daf98bda1110b6b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "a half-mile of other #mass transit stations#, as defined in Section 66-11 (Definitions)."
- ZR 12-10 (Definitions - Outer Transit Zone) - captured.
  - Capture: snapshot `zr-12-10-transit-zone-outer`, file `docs/research/zr-snapshots/v1/zr-12-10-transit-zone-outer.snapshot.json`.
  - Content digest: `692690b9e28d8f8109fb417494ee9264485cee084f54b7868daf98bda1110b6b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "In the event of a conflict between the textual description of the boundary and that on ZoLa, the text shall control."
- ZR 12-10 (Definitions - Greater Transit Zone) - captured.
  - Capture: snapshot `zr-12-10-transit-zone-greater`, file `docs/research/zr-snapshots/v1/zr-12-10-transit-zone-greater.snapshot.json`.
  - Content digest: `cff5de653d176344b1083f9ad330201ebcd67dcacd82eb655758bd4f133e19bb`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "(c) within the #Outer Transit Zone#."

Why the rule applies: The served value (a recorded PLUTO attribute) is Outer Transit Zone. The ZR 12-10 definitions tie the actual boundary to the Department of City Planning's ZoLa map, to APPENDIX I and to distances from mass transit stations defined in Section 66-11 - none of which was in the folder - and say the text controls on conflict. So the captured definitions do not independently confirm the zone; the Greater Transit Zone includes the Outer Transit Zone.

Expected value: The served transit-zone value is Outer Transit Zone, a recorded PLUTO attribute (a recorded value, not a rule). The captured ZR 12-10 definitions do NOT independently settle the zone: they rest on the Department of City Planning's ZoLa map, APPENDIX I and Section 66-11, none of which was in the folder, and they say the text controls on conflict. Taken as the recorded fact, the Outer Transit Zone is within the Greater Transit Zone. The zone would be settled from the law only with APPENDIX I, the ZoLa boundary and Section 66-11

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b (served value Outer Transit Zone; definitions rest on ZoLa/APPENDIX I/66-11 not in folder; cannot confirm from the text) and return-independent-hand-calculation-12.md Q7(b) (same; the served value is a recorded attribute the definitions do not independently confirm); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: The served value is a recorded figure, not a rule; the captured law does not confirm it. It says nothing complies.

### option-standard-residences - The option of standard residences: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 25-811 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#buildings# or #building segments# containing 10 #dwelling units# or less"

Why the rule applies: On the served Outer-Transit-Zone lot, ZR 36-31 sends residence parking to ZR 25-20, and ZR 25-221 requires parking for dwelling units created after December 5, 2024 per the missing ZR 25-222. Residences are not a listed use in the ZR 36-62 loading table. ZR 25-80/25-811 require bicycle parking at 1 per two dwelling units, waived for buildings of 10 dwelling units or less.

Expected value: Parking: required, but the number is not known - ZR 25-221 (Outer Transit Zone) requires parking for dwelling units created after December 5, 2024 per ZR 25-222, which the readers did not have. Loading: no captured section requires an off-street loading berth for a residence - reading 12 reads this as not required (residences are not a listed use in the ZR 36-62 loading table and ZR 25-02 scopes Chapter 5 to parking and bicycle parking only), while reading 11 reaches the same 'no captured requirement' but holds that whether a residential loading section outside the folder exists is not known. Bicycle: required for a development (ZR 25-80), at 1 per two dwelling units (ZR 25-811), with the count not known (the dwelling-unit count is not given) and waived for a building of 10 dwelling units or less

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(1) (parking required, amount not known; loading not in captured text; bicycle 1 per two DU, count not known) and return-independent-hand-calculation-12.md Q7(b)(1) (parking required per 25-222 missing; loading not required; bicycle 1 per 2 DU, count not known); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### option-qualifying-affordable-housing - The option of qualifying affordable housing: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 25-811 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#buildings# or #building segments# containing 10 #dwelling units# or less"

Why the rule applies: Qualifying affordable housing is a residential use: ZR 25-221 requires Outer-Transit-Zone parking per the missing ZR 25-222 (and any affordable reduction is in sections not in the folder); residences are not in the ZR 36-62 loading table; ZR 25-811 gives 1 per two dwelling units, waived at 10 dwelling units or less.

Expected value: Parking: required, number not known - ZR 25-221 per ZR 25-222 (not in the folder), and any affordable-specific reduction would be in sections not in the folder. Loading: no captured section requires an off-street loading berth for a residence - reading 12 reads this as not required (residences are not a listed use in the ZR 36-62 loading table and ZR 25-02 scopes Chapter 5 to parking and bicycle parking only), while reading 11 reaches the same 'no captured requirement' but holds that whether a residential loading section outside the folder exists is not known. Bicycle: 1 per two dwelling units (ZR 25-811), count not known, waived at 10 dwelling units or less

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(2) (parking required, amount not known; loading not in captured text; bicycle 1 per two DU) and return-independent-hand-calculation-12.md Q7(b)(2) (parking per 25-222 missing and any affordable reduction; loading not required; bicycle 1 per 2 DU); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### option-qualifying-senior-housing - The option of qualifying senior housing: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces (seniors)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#Affordable independent residences for seniors# listed under Use Group II"
- ZR 25-811 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#buildings# or #building segments# containing 10 #dwelling units# or less"

Why the rule applies: Qualifying senior housing may be affordable independent residences for seniors (a residential use) or a long-term care facility (a community-facility use). For the residential form ZR 25-221 requires parking per the missing ZR 25-222; residences are not in the ZR 36-62 loading table; ZR 25-811 gives seniors 1 per 10,000 square feet of floor area.

Expected value: Parking: required, number not known - for affordable independent residences for seniors ZR 25-221 requires parking per ZR 25-222 (not in the folder, and a senior reduction is in sections not in the folder); a long-term care facility would be a community-facility use under ZR 36-21 by its use group, not known. Loading: no captured section requires an off-street loading berth for a residence - reading 12 reads this as not required (residences are not a listed use in the ZR 36-62 loading table and ZR 25-02 scopes Chapter 5 to parking and bicycle parking only), while reading 11 reaches the same 'no captured requirement' but holds that whether a residential loading section outside the folder exists is not known. (a long-term care facility could fall in the ZR 36-62 hospital loading category, not known which use group or size.) Bicycle: affordable independent residences for seniors at 1 per 10,000 square feet of floor area (ZR 25-811), count not known (the floor area is not given)

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(3) (parking required per 25-222 missing; loading not in captured text; bicycle 1 per 10,000 sq ft for seniors, count not known) and return-independent-hand-calculation-12.md Q7(b)(3) (same; a long-term care facility would be use-group dependent, not known); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### option-shops-below-residences - The option of shops below residences (the made-up mixed building): parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)
- Made-up mixed building = a made-up building, shops below standard residences, in a C2-2 overlay mapped within R6B; lot area 10,000 sq ft; four storeys, no cellar; floor areas: shop 4,200, residential 15,900 (900 lobby/stair/elevator serving the residences plus 5,000 on each of floors 2-4), shared vestibule/corridor/refuse 400; building total 20,500 (all floor area) (source: the readings' made-up mixed building (made_up_lots.json); said to be made up, not a real property)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 36-21 (General Provisions (commercial/community-facility parking)) - captured.
  - Capture: snapshot `zr-36-21`, file `docs/research/zr-snapshots/v1/zr-36-21.snapshot.json`.
  - Content digest: `47b2295cbd17b6649f7e9d0554af4d9f62dce54487fefa515c39dec7ecf35537`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21.
  - Quoted: "#accessory# off-street parking spaces, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section for all #developments# after December 15, 1961, for the #commercial# or #community facility# #uses# listed in the table."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 36-62 (Required Accessory Off-street Loading Berths (first bracket)) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "First 8,000 sq. ft.: None"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 36-711 (Enclosed bicycle parking spaces (commercial)) - captured.
  - Capture: snapshot `zr-36-711`, file `docs/research/zr-snapshots/v1/zr-36-711.snapshot.json`.
  - Content digest: `20414c33264558f386cb58ac6d73a1685b73e4fb35618e6b3463016e7eb43310`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711.
  - Quoted: "Use Groups not specified above, and all other #commercial# #uses# not otherwise listed"
- ZR 36-711 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-36-711`, file `docs/research/zr-snapshots/v1/zr-36-711.snapshot.json`.
  - Content digest: `20414c33264558f386cb58ac6d73a1685b73e4fb35618e6b3463016e7eb43310`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711.
  - Quoted: "all other #community facility# or #commercial# #uses# not otherwise listed in the table where the number of required bicycle parking spaces is three or less"

Why the rule applies: The residential part follows ZR 25-221 (per the missing ZR 25-222); the commercial (shop) part follows the ZR 36-21 C2-2 table, whose rate turns on the shop's parking requirement category / use group (the Use Group tables not in the folder) and the small-lot waivers 36-23/36-24/36-25 (not in the folder). For loading, the ZR 36-62 C2-in-R6 column's first bracket is None up to 8,000 square feet, and the shop is 4,200 square feet. For bicycle, a 4,200-square-foot shop computes below one at the ZR 36-711 commercial rates and is waived at three or less.

Expected value: Parking: residential part required but not known (ZR 25-221 per the missing ZR 25-222); commercial part not known (ZR 36-21 C2-2 table, but the shop's parking requirement category / use group and the waivers ZR 36-23/36-24/36-25 are not in the folder). Loading: residential part not required by any captured section (as in the standard-residences row); commercial part - the ZR 36-62 C2-in-R6 column's first bracket is None up to 8,000 square feet, so a 4,200-square-foot shop needs zero loading berths, though the exact use group is not given. Bicycle: residential part 1 per two dwelling units (ZR 25-811), count not known, waived at 10 dwelling units or less; commercial part - a 4,200-square-foot shop computes below one at the ZR 36-711 commercial rates and is waived where the number is three or less (none), with the exact use group not given

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(4) (residential parking required amount not known; commercial parking not known; shop loading none under 8,000 sq ft; shop bicycle waived/none) and return-independent-hand-calculation-12.md Q7(b)(4) (same; residential per 25-222 missing; commercial PRC/use group and 36-25 not in folder; shop loading zero; shop bicycle computes to none); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### option-residences-with-community-facility - The option of residences with a community facility: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 36-21 (General Provisions (commercial/community-facility parking)) - captured.
  - Capture: snapshot `zr-36-21`, file `docs/research/zr-snapshots/v1/zr-36-21.snapshot.json`.
  - Content digest: `47b2295cbd17b6649f7e9d0554af4d9f62dce54487fefa515c39dec7ecf35537`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21.
  - Quoted: "#accessory# off-street parking spaces, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section for all #developments# after December 15, 1961, for the #commercial# or #community facility# #uses# listed in the table."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 25-811 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#buildings# or #building segments# containing 10 #dwelling units# or less"
- ZR 36-711 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-36-711`, file `docs/research/zr-snapshots/v1/zr-36-711.snapshot.json`.
  - Content digest: `20414c33264558f386cb58ac6d73a1685b73e4fb35618e6b3463016e7eb43310`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711.
  - Quoted: "all other #community facility# or #commercial# #uses# not otherwise listed in the table where the number of required bicycle parking spaces is three or less"

Why the rule applies: The residential part follows ZR 25-221 (per the missing ZR 25-222); the community-facility part follows ZR 36-21 by its use group (not given). Residences are not in the ZR 36-62 loading table; a community-facility use is listed only for a few categories (e.g. hospitals). Bicycle parking follows the ZR 25-811 and 36-711 rows by use group.

Expected value: Parking: residential part required but not known (ZR 25-221 per the missing ZR 25-222); community-facility part not known (ZR 36-21 by its specific use group and size, not given). Loading: residential part not required by any captured section; community-facility part not known (ZR 36-62 lists only a few community-facility categories, and the use group is not given). Bicycle: residential part 1 per two dwelling units (ZR 25-811), count not known, waived at 10 dwelling units or less; community-facility part not known (the ZR 25-811 / 36-711 community-facility rows turn on the use group and size)

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(5) (residential parking required amount not known; community-facility parking/loading/bicycle use-group dependent, not known) and return-independent-hand-calculation-12.md Q7(b)(5) (same); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### option-community-facility-alone - The option of a community facility alone: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 36-21 (General Provisions (commercial/community-facility parking)) - captured.
  - Capture: snapshot `zr-36-21`, file `docs/research/zr-snapshots/v1/zr-36-21.snapshot.json`.
  - Content digest: `47b2295cbd17b6649f7e9d0554af4d9f62dce54487fefa515c39dec7ecf35537`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-21.
  - Quoted: "#accessory# off-street parking spaces, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section for all #developments# after December 15, 1961, for the #commercial# or #community facility# #uses# listed in the table."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 36-711 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-36-711`, file `docs/research/zr-snapshots/v1/zr-36-711.snapshot.json`.
  - Content digest: `20414c33264558f386cb58ac6d73a1685b73e4fb35618e6b3463016e7eb43310`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-711.
  - Quoted: "all other #community facility# or #commercial# #uses# not otherwise listed in the table where the number of required bicycle parking spaces is three or less"

Why the rule applies: A community facility's parking follows the ZR 36-21 C2-2 table by its use group / parking requirement category (e.g. schools None, libraries 1 per 800); its loading follows ZR 36-62 only for the few listed community-facility categories; its bicycle parking follows the ZR 25-811 / 36-711 community-facility rows. All turn on the specific use group and size, which are not given.

Expected value: Parking: not known - ZR 36-21 (C2-2 table) sets the rate by the specific community-facility use group / parking requirement category and size, which are not given (a school would be None, a library 1 per 800, but the use and size are not stated). Loading: not known - ZR 36-62 lists only a few community-facility categories (e.g. hospitals, court houses, prisons), so it turns on the use group and size, not given. Bicycle: not known - the ZR 25-811 / 36-711 community-facility rows turn on the use group and size, with a waiver where the number is three or less. Each is not yet checked because the community-facility use and size are not given

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(6) (parking/loading/bicycle use-group dependent, not known; a school would be None) and return-independent-hand-calculation-12.md Q7(b)(6) (same; use group and size not given); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It names the missing fact (the specific community-facility use and size), gives no count, and never says the option is feasible. It says nothing complies.

### option-rooming-units - The option of rooming units: parking, loading berths, bicycle parking

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)
- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "No #accessory# off-street parking spaces shall be required for #rooming units# created as part of a #development# or #enlargement# after March 22, 2016."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces (rooming equivalence)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "three #rooming units# shall be considered the equivalent of one #dwelling unit#"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"
- ZR 25-811 (Enclosed bicycle parking spaces (waiver)) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "#buildings# or #building segments# containing 10 #dwelling units# or less"

Why the rule applies: ZR 25-221 requires no accessory off-street parking for rooming units created after March 22, 2016 (a new building is such a development). Residences are not in the ZR 36-62 loading table. ZR 25-811 applies the 1-per-two-dwelling-units rate with three rooming units counted as one dwelling unit, waived for 10 dwelling units or less.

Expected value: Parking: NOT required - ZR 25-221 requires no accessory off-street parking for rooming units created as part of a development after March 22, 2016 (a new building is such a development). Loading: no captured section requires an off-street loading berth for a residence - reading 12 reads this as not required (residences are not a listed use in the ZR 36-62 loading table and ZR 25-02 scopes Chapter 5 to parking and bicycle parking only), while reading 11 reaches the same 'no captured requirement' but holds that whether a residential loading section outside the folder exists is not known. Bicycle: required for a development (ZR 25-80), at 1 per two dwelling units with three rooming units counted as one dwelling unit (ZR 25-811), count not known (the number of rooming units is not given), waived at the 10-dwelling-unit-equivalent threshold

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7b(7) (rooming-unit parking not required; loading not in captured text; bicycle 1 per 6 rooming units, count not known) and return-independent-hand-calculation-12.md Q7(b)(7) (parking not required; loading not required; bicycle with rooming equivalence, count not known); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It states which provision applies, never a count, and never that the option is feasible. It says nothing complies.

### parking-loading-bicycle-line-per-option - What each development option's parking, loading and bicycle line MAY say today, and what it MAY NOT say

Facts used:

- Served transit zone = Outer Transit Zone (a recorded value, not a rule) (source: NYC PLUTO row for BBL 4073340070, field transitzone)

Law relied on:

- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "#accessory# off-street parking spaces shall be required for #dwelling units# created as part of a #development# or #enlargement# after December 5, 2024, in accordance with the provisions of Section 25-222."
- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "No #accessory# off-street parking spaces shall be required for #rooming units# created as part of a #development# or #enlargement# after March 22, 2016."
- ZR 36-62 (Required Accessory Off-street Loading Berths) - captured.
  - Capture: snapshot `zr-36-62`, file `docs/research/zr-snapshots/v1/zr-36-62.snapshot.json`.
  - Content digest: `2656568642f6718df8bb9ae4d14fd2d8144d885b3b7cfd3c3873d59a0f8cd4b7`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-6/36-62.
  - Quoted: "#accessory# off-street loading berths, open or enclosed, shall be provided in conformity with the requirements set forth in the table in this Section"
- ZR 25-811 (Enclosed bicycle parking spaces) - captured.
  - Capture: snapshot `zr-25-811`, file `docs/research/zr-snapshots/v1/zr-25-811.snapshot.json`.
  - Content digest: `fe55907253151346aacc3f0bef4e0f37b65204c0ad206c0d3edb4970c0ad473b`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-811.
  - Quoted: "All other types of #residences# listed under Use Group II, except #affordable independent residences for seniors#"

Why the rule applies: From the option rows only, a line may state the applicability resolved from a captured provision, or 'not yet checked' / 'not sure' naming the missing fact; it may not give a count, declare an option feasible, or turn a question of law into a preference.

Expected value: What a line MAY say today, per option: standard residences, qualifying affordable housing, qualifying senior housing, residences with a community facility - parking required but the number not yet checked (ZR 25-222 not in the folder), no captured loading requirement for the residential part, bicycle parking required but the count not yet checked; shops below residences - residential parking required (number not yet checked) and commercial parking not yet checked (use group and waivers not in the folder), the shop's loading zero under 8,000 square feet, the shop's bicycle parking none; a community facility alone - parking, loading and bicycle all not yet checked (the use group and size are not given); rooming units - parking not required, no captured residential loading requirement, bicycle required (count not yet checked). What a line MAY NOT say: it may not say 'none required' where the readings do not both say so, it may not give a count, and it may not call the option feasible or turn a question of law into a preference

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q7 (the resolved-or-not-yet-checked applicability per option) and return-independent-hand-calculation-12.md Q7 (same, drawn from the option answers only); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It draws only on the option answers; it gives no count and declares no option feasible. It says nothing complies.

### sections-and-facts-not-had - What both readers did not have (with what stays not known), and what each reader did not read

Facts used:

- none (this row rests on the law text alone)

Law relied on:

- ZR 35-31 (Maximum Floor Area Ratio) - captured.
  - Capture: snapshot `zr-35-31`, file `docs/research/zr-snapshots/v1/zr-35-31.snapshot.json`.
  - Content digest: `65e29c688be2f04b8963b87bc564afb16539c497b19b1219f58a0cf8edad80fe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31.
  - Quoted: "shall be as set forth in Article III, Chapter 3"
- ZR 25-221 (General provisions (Outer Transit Zone)) - captured.
  - Capture: snapshot `zr-25-221`, file `docs/research/zr-snapshots/v1/zr-25-221.snapshot.json`.
  - Content digest: `21327ea6aaadc6bc2d5da320a9f7d34351c4552e4636689303b4678be6499b97`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-5/25-221.
  - Quoted: "in accordance with the provisions of Section 25-222"

Why the rule applies: Both readings name, in their Q8 lists, the texts and facts outside their folder; each names separately the folder texts it chose not to read.

Expected value: Both readers did not have: Article III, Chapter 3 (the commercial-district maximum floor area ratio, e.g. ZR 33-12 / 33-121) - so the made-up building's commercial floor area ratio and whole-building maximum stay not known; the ZR 23-24 subsections (ZR 23-241 and following) - so ZR 23-24's reach stays not known; ZR 25-222 and ZR 25-232 (the dwelling-unit parking numbers) - so the residential parking counts stay not known; the Use Group tables - so the commercial and community-facility parking, loading and bicycle rates stay not known; the parking waivers ZR 36-23, 36-24 and 36-25; Section 66-11, APPENDIX I and the ZoLa boundary - so the transit zone cannot be confirmed from the law; and Local Law 154 of 2021 with the New York City Energy Conservation Code and Building Code - so the energy requirements' substance stays not known. Facts both readers did not have: the adjoining zoning lots' lot-line types (so the rear yard beyond the corner stays not known) and the block's bounding dimensions. Separately, reading 11 (return-independent-hand-calculation-11.md) did not read the folder's ZR 12-10 lot-coverage capture (not needed for the rear-yard question); reading 12 (return-independent-hand-calculation-12.md) read every capture each question named

Where this stands in the independent reading: return-independent-hand-calculation-11.md Q8 (Article III Ch 3; 23-24 subsections; 25-222/25-232; Use Group tables; 36-23/24/25; 66-11/APPENDIX I/ZoLa; LL154/codes; adjoining lots; block dimensions) and return-independent-hand-calculation-12.md Q8 (same decisive missing items; read every capture each question named); both readings reach this on the same basis (return-independent-hand-calculation-11.md and return-independent-hand-calculation-12.md).

What this row does not establish: It lists only what both readers name as outside the folder, and what each chose not to read; it draws no conclusion. It says nothing complies.

## What this case does not establish

- It records a value or a yes/no only where both readings agree on the same basis; where they differ, where one holds an answer subject to a text or a fact the readers did not have, or where neither settles a point, the row says so and names both readings.
- The made-up mixed building and the made-up 100-by-100 lot are not real properties; their figures are worked by hand from the text, not from a program run. The commercial floor area ratio and the whole-building maximum stay not known because Article III, Chapter 3 was not in the folder.
- The benchmark lot's rear yard beyond 100 feet of the corner stays not known (the adjoining zoning lots' lot-line types were not in the folder); the standing not-known for that part is held by cases/step-p3-worked.json row real-lot-rear-yard-beyond-corner, which this case does not re-answer, and this case changes no program output and no fixture.
- It is not a professional or legal determination and does not say anything complies.

## Sources

- The step-P5 reading 1: provenance/return-independent-hand-calculation-11.md
- The step-P5 reading 2: provenance/return-independent-hand-calculation-12.md
- The sealed folder given to each helper: all 156 pinned law-text captures (without the notes describing how the program encoded them), the benchmark lot's recorded official facts and outline, two made-up lots and one made-up mixed building, with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-08 | Case created (step P5, task M4-T035) from the two independent readings of the step-P5 sealed folder (provenance/return-independent-hand-calculation-11.md and -12.md). It holds the readings of the 46 texts captured by tasks M4-T033 and M4-T034: the mixed-building floor-area sections ZR 35-30 to 35-33 and the floor-area-ratio definition, ZR 23-24 and the ZR 34-23 page, the ZR 12-10 energy, building and story definitions, the parking, loading and bicycle sections, and the benchmark lot's rear yard from ZR 23-342 and 23-344. A value is recorded only where both readings agree on the same basis. The row zr-34-23-page gives the current reading of the ZR 34-23 page (the ZR 34-23 contents capture read as the complete three-subsection list), which supersedes cases/step-p4-worked.json row zr-34-23-sections. | rules-engineer (M4-T035) |

