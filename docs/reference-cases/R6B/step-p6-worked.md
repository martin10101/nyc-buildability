# Worked from the step-P6 readings: one independent hand-worked example of a first building option in R6B - whether a building may be lower than the minimum base height; a footprint and floors worked by hand for a made-up interior lot and for the recorded corner lot (lot coverage by portion; variants where a property fact is missing); what a floor schedule must list; and the arithmetic of the preliminary apartment estimate on the owner's starting values, kept apart from the legal dwelling-unit ceiling

GENERATED FILE - do not edit by hand. Produced by `services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from `cases/<case>.json`; edit the data file and re-render. See `README.md`.

Work order table: backlog: the first building shape, the floor schedule and the preliminary apartment estimate; owner directive D-090 R291, R519, R545, R650, R651, R664, R686 to R690, R699, R700.

One independent hand-worked example of a FIRST BUILDING OPTION in R6B, read independently in step P6 by two AI helpers working alone from a sealed folder (all 185 pinned law captures without their notes; the benchmark lot's recorded facts and outline; one made-up interior lot of 100 ft by 100 ft in plain R6B; 34 earlier answers given as settled; and three starting values chosen by the owner, marked as assumptions), with no access to the program, the repository or the web. It settles, from captured text, whether a building may be wholly below the minimum base height (yes, in plain R6B and under a C2-2 overlay); it works, by hand, the yards, the footprint, the floor stack and the floor schedule for the made-up lot and the real lot (lot coverage by portion; the rear-yard, street-wall and ground-elevation variants where a property fact is missing); and it works the preliminary apartment estimate on the owner's starting values, kept apart from the legal dwelling-unit ceiling. Both worked buildings are a plain stack (every storey the same plan) - the METHOD OF THE EXAMPLE given in the readers' brief, an assumption, not a rule of law, not the owner's decision and not a recommendation of what to build; both stay at or below the maximum base height, so no storey above the base is counted and no setback is worked. A value or a yes/no is recorded only where both readings give it on the same basis; otherwise the row is not known or not sure, with both readings named, the kind of its gap, and what would settle it. Every value comes from the two independent readings and the law text, never from a program run.

## What this case is worth

Read independently by two AI helpers, each working alone from the sealed step-P6 folder; their agreement alone is not proof. It is a draft reading of the law by AI helpers, not professionally reviewed, and is not a statement that anything complies. A second AI read the same sealed folder and worked the same eight questions. Where the two readings differ, or one holds an answer subject to a text or a fact the readers did not have, the row says so and names both readings; where the text does not settle a point the row says not sure or not known and names what would settle it. The worked buildings are a plain stack by the method of the example, an assumption; the floor-to-floor height, the share range and the apartment size are starting assumptions chosen by the owner, not law and not measured.

- Prepared by: An AI helper that took no part in writing the program's rules, working only from a sealed folder of all 185 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, one made-up interior lot, 34 earlier answers given as settled and three starting values chosen by the owner, with no access to the program (reading 1: provenance/return-independent-hand-calculation-13.md).
- Checked by: A second, independent AI read the same sealed folder and worked the same eight questions (reading 2: provenance/return-independent-hand-calculation-14.md). Agreement between two AI answers alone is not proof.

## The facts this case uses

| Fact | Value | Where it comes from |
|---|---|---|
| Zoning district | R6B | NYC PLUTO row for BBL 4073340070, field zonedist1 |
| Commercial overlay | C2-2 | NYC PLUTO row for BBL 4073340070, field overlay1 |
| Made-up interior lot | 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant, standard residences; each side neighbour's street wall on the street line and 35 ft high | the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property |
| Real lot | 215-16 Northern Boulevard, Queens (BBL 4073340070): a corner lot, R6B with a C2-2 overlay | cases/real-lot.json; the recorded outline and DCM centerlines |
| Floor-to-floor height | 10 ft (a starting assumption chosen by the owner) | starting_values_chosen_by_the_owner.json |
| Owner's apartment-estimate values | share 0.60 to 0.75 and apartment size 700 sq ft (each a preliminary assumption) | starting_values_chosen_by_the_owner.json |

## Rows

### min-base-height-plain-r6b - Whether a new building whose whole height is below the minimum base height is permitted in plain R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Minimum base height (R6B standard residences) = 30 ft (settled, given to the readers as settled) (source: cases/real-lot.json row L3 (settled sheet))

Law relied on:

- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."

Why the rule applies: ZR 23-436(e) expressly disapplies the minimum base height of ZR 23-432 to a building that is developed or enlarged and does not exceed that minimum, and ZR 23-431(b) requires the street wall only to 'at least the minimum base height ... or the height of the #building#, whichever is less'. A new building developed below 30 ft meets both, so no provision sets a floor it fails.

Expected value: Yes - permitted in plain R6B. A new building whose whole height is below the 30 ft minimum base height is permitted: ZR 23-436(e) disapplies the minimum base height to a building 'developed or enlarged' that does 'not exceed such minimum base heights', and ZR 23-431(b)'s 'whichever is less' lets the street wall rise only to the building's own height. The two provisions agree. The condition ZR 23-436(e) attaches is that the building be developed or enlarged and not exceed the minimum base height; reading 14 adds that the defined term 'developed' is not in the folder, so the exemption rests on the ordinary reading of a newly built building as developed.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q1b(i) (YES; 23-436(e) and the 'whichever is less' of 23-431(b); the two agree) and return-independent-hand-calculation-14.md Q1b(i) (YES; 23-436(e); the term 'developed' is undefined in the folder, the ordinary reading supports it). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It is a draft reading of the law by AI helpers, not professionally reviewed. It reads what the captured text permits; it is not a statement that any building complies, and it enters no human verdict. Reading 14 notes the defined term 'developed' was not in the folder.

### min-base-height-overlay - Whether such a building is permitted in a C2-2 overlay mapped within R6B

Facts used:

- Zoning district = R6B (source: NYC PLUTO row for BBL 4073340070, field zonedist1)
- Commercial overlay = C2-2 (source: NYC PLUTO row for BBL 4073340070, field overlay1)

Law relied on:

- ZR 35-632 (Maximum height of buildings and setback regulations (height table)) - captured.
  - Capture: snapshot `zr-35-632`, file `docs/research/zr-snapshots/v1/zr-35-632.snapshot.json`.
  - Content digest: `8105cc331eee4ed882e04466814928f6047618f5ba66a260f5c415a29630ad10`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-632.
  - Quoted: "The minimum base height, maximum base height and maximum #building# height shall be as set forth in the table in Section 23-432 for the applicable #Residence District#."
- ZR 35-633 (Additional height and setback provisions (overlay)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows:"
- ZR 35-633 (Additional height and setback provisions (street-wall supersession)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and"
- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 35-631 (Street wall location (percentage-based rules, overlay)) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."

Why the rule applies: A C2-2 overlay within R6B is an R6-through-R12 equivalency, so ZR 35-63 governs: ZR 35-632(a) sends the heights to the ZR 23-432 table (the same 30/45/55), and ZR 35-633 applies the ZR 23-436 additional regulations, excepting only the ZR 23-431 street-wall reference (superseded by 35-631). Paragraph (e) of 23-436 is not excepted, so the minimum-base-height exemption reaches the overlay building; 35-631(b) carries the same 'whichever is less'.

Expected value: Yes - permitted in a C2-2 overlay mapped within R6B. ZR 35-632(a) gives the same 30/45/55 ft from the ZR 23-432 table; ZR 35-633 applies ZR 23-436 (its paragraph (e) is not excepted), so the minimum-base-height exemption of 23-436(e) reaches the overlay building; and ZR 35-631(b) carries the same 'whichever is less' for the street wall. The two provisions agree with the plain-R6B result. Both readings note ZR 35-62 is not the applicable section (it governs R1 to R5 equivalency).

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q1b(ii) (YES; 35-63 routing; 35-633 keeps 23-436(e); 35-631(b) 'whichever is less') and return-independent-hand-calculation-14.md Q1b(ii) (YES; 23-432 via 35-632 and 23-436(e) via 35-633 agree; 35-62 not applicable). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It is a draft reading of the law by AI helpers, not professionally reviewed. It says nothing complies and enters no human verdict.

### min-base-height-street-wall - What the street-wall words then require of a building below the minimum base height

Facts used:

- Building below the minimum base height = a new building whose whole height is under 30 ft (source: the subject of Q1c in both readings)

Law relied on:

- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."
- ZR 35-631 (Street wall location (percentage-based rules, overlay)) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."

Why the rule applies: ZR 23-431(b) (plain R6B) and ZR 35-631(b) (the overlay) require the street wall to extend to 'at least the minimum base height ... or the height of the #building#, whichever is less'. For a building below 30 ft the lesser value is the building's own height, so the wall rises only to that height. Where it stands horizontally turns on ZR 23-431(a)/(b) and on whether a prevailing street wall frontage exists.

Expected value: The street wall need rise only to the building's own height, not to 30 ft, because 'whichever is less' picks the building height for a building below the minimum base height (ZR 23-431(b); ZR 35-631(b) in the overlay). Both readings agree on this. Where the street wall must stand horizontally is not settled here: it turns on the line-up rule of ZR 23-431(a) or the percentage rule of 23-431(b) / 35-631(b) and on whether a prevailing street wall frontage exists, which the readers could not confirm.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q1c (the wall rises only to the building height; the line-up and percentage rules place it) and return-independent-hand-calculation-14.md Q1c (same; the exact horizontal location is not known without the prevailing-frontage block data). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads to what height the street wall must rise (the building's own height); the exact horizontal location it leaves not settled, naming what would settle it. It is a draft reading by AI helpers, not professionally reviewed, and says nothing complies.

### min-base-height-wide-narrow - Whether anything turns on a wide versus a narrow street for a building at or below the maximum base height

Facts used:

- R6B height table = no wide/narrow footnote on the R6B row (source: cases/real-lot.json row L11 (settled); ZR 23-432)

Law relied on:

- ZR 23-432 (Height and setback requirements (setback above the maximum base height)) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided at a height not lower than the minimum base height or higher than the maximum base height in accordance with Section 23-433."
- ZR 23-433 (Standard setback provisions (wide and narrow streets)) - captured.
  - Capture: snapshot `zr-23-433`, file `docs/research/zr-snapshots/v1/zr-23-433.snapshot.json`.
  - Content digest: `4fecf4d26719a00ed0eaeb1e0e7e714f891e7fff154ded306b04e29167ef1afe`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-433.
  - Quoted: "a setback with a depth of at least 10 feet shall be provided from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet shall be provided from any #street wall# fronting on a #narrow street#."
- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."

Why the rule applies: The R6B heights of ZR 23-432 carry no within-100-feet-of-a-wide-street footnote, so they do not change with wide or narrow. The 10 ft (wide) / 15 ft (narrow) setback of ZR 23-433 is triggered only for portions above the maximum base height, which a building at or below it never reaches. The street-wall horizontal location of ZR 23-431(b) does turn on wide (within 8 ft) versus narrow (within 10 ft).

Expected value: The R6B height numbers (30/45/55 ft) do not depend on wide versus narrow: the R6B table row carries no footnote. The above-maximum-base setback of ZR 23-433 (10 ft wide, 15 ft narrow) is never triggered by a building at or below the maximum base height. What does turn on wide versus narrow is the street-wall horizontal location (within 8 ft on a wide street, within 10 ft on a narrow street, ZR 23-431(b)). Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q1d (heights no footnote; setback only above max base; location distances turn on wide/narrow) and return-independent-hand-calculation-14.md Q1d (same; the below-max-base street-wall location depends on wide/narrow). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads which rules turn on wide versus narrow; it sets no height or distance for any building. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### min-base-height-least-height-or-storeys - Whether any captured provision sets a least height or a least number of storeys

Facts used:

- Captured height sections read = ZR 23-43, 23-431, 23-432, 23-433, 23-436; ZR 35-62, 35-63, 35-631, 35-632, 35-633 (source: the sections both readings read for Q1)

Law relied on:

- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."

Why the rule applies: ZR 23-436(e) removes the minimum-base-height floor for a below-minimum building, and no section among the captured height and street-wall sections states a minimum building height or a minimum number of storeys for standard residences.

Expected value: No captured provision sets a least height or a least number of storeys for standard residences. Both readings searched the captured height and street-wall sections and found none; a rule outside the readers' folder is not ruled out.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q1c (no minimum-storeys rule in the captured texts; a rule outside the folder not ruled out) and return-independent-hand-calculation-14.md Q1b (no captured section states a minimum building height or storey count). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records that no captured provision sets a least height or storey count; it does not rule out a provision the readers did not have. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### made-up-front-yard - The made-up lot: the front yard

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)

Law relied on:

- ZR 23-322 (Front yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-322`, file `docs/research/zr-snapshots/v1/zr-23-322.snapshot.json`.
  - Content digest: `2a5af75847b73f8238936cbc9818eef0b76102e588be741254604d0a2d8c2c3e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322.
  - Quoted: "In the districts indicated, no #front yard# requirements shall apply."

Why the rule applies: ZR 23-322 removes the front-yard requirement in R6 through R12 districts, so no front yard is required and the building may stand on the front (street) lot line.

Expected value: No front yard is required (ZR 23-322, 'no #front yard# requirements shall apply'); the building may stand on the street line. Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q2b (none required; depth 0 ft) and return-independent-hand-calculation-14.md Q2b (none required). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads one yard rule for a made-up lot; it says nothing complies. The made-up lot describes no real property; the example checks a method.

### made-up-side-yard - The made-up lot: the side yards

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)

Law relied on:

- ZR 23-335 (Side yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-335`, file `docs/research/zr-snapshots/v1/zr-23-335.snapshot.json`.
  - Content digest: `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335.
  - Quoted: "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."

Why the rule applies: ZR 23-335(b) requires no side yard for a multi-family residence; only paragraph (a)'s two 5-ft side yards are for single- or two-family detached residences, which this building is not. Any open area along a side lot line, if provided, must be at least 5 ft wide.

Expected value: No side yard is required (ZR 23-335(b)); any open area provided along a side lot line must be at least five feet wide. Both readings agree, and both note paragraph (a)'s 5-ft side yards are only for single- or two-family detached residences, which this building is not.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q2b (none required; (a) is detached-only; >=5 ft if provided) and return-independent-hand-calculation-14.md Q2b (same). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads one yard rule for a made-up lot; it says nothing complies. The made-up lot describes no real property; the example checks a method.

### made-up-rear-yard - The made-up lot: the rear yard

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)
- Settled 40-by-100 rear yard = 20 ft at or below 75 ft (settled, given as settled) (source: cases/step-p3-worked.json row interior-40x100-rear-yard (settled sheet))

Law relied on:

- ZR 23-342 (Rear yard requirements (detached and zero-lot-line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided"
- ZR 23-342 (Rear yard requirements (lot width 40 feet or greater)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "for #zoning lots# with a #lot width# of 40 feet or greater, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#"
- ZR 23-342 (Rear yard requirements (shallow lots)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "the provisions of this Section may be modified where an #interior lot# is less than 95 feet deep at any point"

Why the rule applies: ZR 23-342 sets the rear yard: 20 ft at or below 75 ft for detached or zero-lot-line buildings (a)(1) and for semi-detached or attached buildings on a lot 40 ft wide or greater (a)(2)(ii). The lot is 100 ft wide (>=40) and 100 ft deep (not less than 95), so 20 ft applies under either building type and the shallow-lot reduction (b) does not apply.

Expected value: A rear yard of 20 ft at or below 75 ft (30 ft above 75 ft) is required (ZR 23-342). At a lot width of 100 ft (>=40) both the detached path (a)(1) and the semi-detached or attached path (a)(2)(ii) give 20 ft, and the shallow-lot reduction (b) does not apply because the lot is 100 ft deep (not less than 95 ft). Both readings agree, and both note it matches the settled 40-by-100 answer of 20 ft.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q2b (20 ft at/below 75 ft; either building type; no shallow reduction; matches settled) and return-independent-hand-calculation-14.md Q2b (20 ft; both paths at >=40 ft width; (b) does not apply at 100 ft depth). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads the ordinary rear-yard depth for a made-up lot; it says nothing complies. The made-up lot describes no real property; the example checks a method.

### made-up-street-wall - The made-up lot: where the street wall must or may stand, given the stated neighbours

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)
- Stated neighbours = each side neighbour's street wall is on the street line and is 35 ft high (source: the readers' made-up lot facts (made_up_lot.json))

Law relied on:

- ZR 23-431 (Street wall location (line-up rules)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "In R6B, R7B, and R8B Districts, the #street wall# of a #building# shall be located no closer to the #street line# than the closest #street wall#, or portion thereof, nor further from the #street line# than the furthest #street wall#, or portion thereof, of an existing adjacent #building# on the same or an adjoining #zoning lot# located on the same #street# frontage. Eligible adjacent #buildings# shall be located within 15 feet of the #street line#, within 25 feet of the subject #building#, and have a height that exceeds 35 feet."

Why the rule applies: ZR 23-431(a)'s line-up rule binds R6B, but an eligible adjacent building must 'have a height that exceeds 35 feet'. The stated neighbours are 35 ft high; 35 does not exceed 35, so they are not eligible adjacent buildings and fix no line-up range. The fall-back to paragraph (b) turns on whether a prevailing street wall frontage exists, which needs the neighbours' street-wall widths, not in the made-up facts.

Expected value: not known. Not known where the street wall must stand. Both readings read that the stated neighbours, at exactly 35 ft high, do NOT count under ZR 23-431(a)'s eligibility test (an eligible adjacent building must 'have a height that exceeds 35 feet'; 35 does not exceed 35), so the line-up rule fixes no required place; and the fall-back to the percentage rule of paragraph (b) turns on whether a prevailing street wall frontage exists, which needs the neighbours' street-wall widths that the made-up facts do not give. KIND OF GAP: a missing fact about the property (the neighbouring buildings' street-wall widths, which would come from a record of the neighbouring buildings). This comes from the made-up facts sitting on the 35-ft threshold - a limit of the example, not a finding about any property. For the worked buildings below, the method places the street wall on the street line (no front yard forbids it), flagged there as the method's choice, not a mandate.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q2b (the 35-ft neighbours do not exceed 35 ft, so not eligible; prevailing frontage not confirmable; placement not known) and return-independent-hand-calculation-14.md Q2b (same; 35 does not exceed 35 feet; required location not known). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records that the required street-wall place is not known and why; it enters no value. A draft reading by AI helpers, not professionally reviewed; it says nothing complies. The made-up lot describes no real property; the example checks a method.

### made-up-footprint-a - The made-up lot: the footprint of the widest building (building A), with the limit binding each edge

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)

Law relied on:

- ZR 23-322 (Front yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-322`, file `docs/research/zr-snapshots/v1/zr-23-322.snapshot.json`.
  - Content digest: `2a5af75847b73f8238936cbc9818eef0b76102e588be741254604d0a2d8c2c3e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322.
  - Quoted: "In the districts indicated, no #front yard# requirements shall apply."
- ZR 23-335 (Side yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-335`, file `docs/research/zr-snapshots/v1/zr-23-335.snapshot.json`.
  - Content digest: `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335.
  - Quoted: "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."
- ZR 23-342 (Rear yard requirements (detached and zero-lot-line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided"
- ZR 23-362 (Maximum lot coverage in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."

Why the rule applies: The widest footprint runs the full 100 ft frontage (front edge on the street line, no front yard; side edges on the side lot lines, no side yard) and 80 ft deep, the depth that both the 20 ft rear yard (100 - 20 = 80) and the 80 percent lot coverage (0.80 x 10,000 = 8,000 = 100 x 80) allow.

Expected value: The widest footprint is 100 ft (frontage) by 80 ft (depth) = 8,000 sq ft. The front edge is bound by the street line (no front yard, ZR 23-322, and the street-wall location of ZR 23-431); each side edge by the side lot line (no side yard, ZR 23-335(b)); and the rear edge by both the 20 ft rear yard (ZR 23-342, giving depth 80 ft) and the 80 percent lot coverage (ZR 23-362, 0.80 x 10,000 = 8,000 = 100 x 80), which bind the rear edge at the same 80 ft. Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q2c (100 x 80 = 8,000; each edge's binding limit; rear bound by rear yard and coverage together) and return-independent-hand-calculation-14.md Q2c (same sides, area and binding limits). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads the widest footprint for a made-up lot by hand; the street-wall horizontal place rests on the method's choice (see made-up-street-wall). It says nothing complies. The made-up lot describes no real property; the example checks a method.

### made-up-building-a - The made-up lot, building A storey by storey (the widest footprint stacked to the floor-area maximum)

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)
- Floor-to-floor height = 10 ft (a starting assumption chosen by the owner) (source: starting_values_chosen_by_the_owner.json)
- Maximum floor area = 20,000 sq ft (settled) (source: cases/step-p5-worked.json row floor-area-ratio-made-up-100x100 (settled sheet))

Law relied on:

- ZR 23-322 (Front yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-322`, file `docs/research/zr-snapshots/v1/zr-23-322.snapshot.json`.
  - Content digest: `2a5af75847b73f8238936cbc9818eef0b76102e588be741254604d0a2d8c2c3e`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-322.
  - Quoted: "In the districts indicated, no #front yard# requirements shall apply."
- ZR 23-335 (Side yard requirements for R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-335`, file `docs/research/zr-snapshots/v1/zr-23-335.snapshot.json`.
  - Content digest: `31b67b9d47eca82cb93e1b06db908b20f1ad7f159c2b4306d78248e5fb02fcf2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-335.
  - Quoted: "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#."
- ZR 23-342 (Rear yard requirements (detached and zero-lot-line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided"
- ZR 23-362 (Maximum lot coverage in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."
- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 23-43 (Height and setback requirements in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."

Why the rule applies: Building A is the widest footprint (8,000 sq ft) stacked at 10 ft per storey until the next storey would pass the 20,000 sq ft maximum floor area: two storeys (16,000 sq ft) fit, a third (24,000) would not. Its 20 ft height is below the 30 ft minimum base height, which ZR 23-436(e) permits, so no setback is worked and the method then calls for building B. Heights are measured from the base plane (ZR 23-43), here the curb level.

Expected value: Building A is two storeys of 8,000 sq ft = 16,000 sq ft total, with 4,000 sq ft of floor area left unused against the 20,000 sq ft maximum; its height is 20 ft. 20 ft is BELOW the 30 ft minimum base height (permitted, ZR 23-436(e); the street wall need rise only to 20 ft), and below the 45 ft maximum base and 55 ft maximum building height, so no setback is worked. Because building A is below the minimum base height, the method of the example calls for building B. The figures as numbers are in the block below. Both readings give the same storey table, total, unused and height.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q3a (2 storeys; 16,000 total; 4,000 unused; 20 ft; below min base; calls for B) and return-independent-hand-calculation-14.md Q3a (same storey table, total, unused and height). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: Both buildings are a plain stack, every storey the same plan: this shape is the method of the example, an assumption chosen in the readers' brief, not a rule of law, not a decision of the owner and not a recommendation of what to build. Both buildings stay at or below the maximum base height, so no storey above the base is counted and no setback is worked. The floor-to-floor height of 10 ft is a starting assumption chosen by the owner, not validated, not measured and not law. It checks a method; it says nothing complies. The made-up lot describes no real property; the example checks a method.

Six steps as numbers (made-up lot, building A (the widest; a plain stack, every storey the same plan)):

- Property inputs: maximum floor area 20000 sq ft; floor-to-floor height 10 ft; minimum base height 30 ft.
- Footprint: 100 ft frontage x 80 ft depth; area 8000 sq ft.
- Storeys:
  - Storey 1: floor-to-floor 10 ft; top 10 ft above the base plane; plan area 8000 sq ft; floor area 8000 sq ft; running total 8000 sq ft.
  - Storey 2: floor-to-floor 10 ft; top 20 ft above the base plane; plan area 8000 sq ft; floor area 8000 sq ft; running total 16000 sq ft.
- Total floor area 16000 sq ft; floor area left unused 4000 sq ft; building height 20 ft; 2 storeys.
- Each figure above is marked a legal requirement or a chosen design assumption:
  - maximum floor area: a legal requirement (the floor area ratio of ZR 23-22 (R6B standard residences, 2.00) times the lot area).
  - footprint bound by the yards and lot coverage: a legal requirement (the yard sections (ZR 23-322, 23-335, 23-342) and the lot coverage of ZR 23-362).
  - floor-to-floor height 10 ft: a chosen design assumption (a starting value chosen by the owner, not validated, not measured and not law).
  - the same-plan stack: a chosen design assumption (the method of the example in the readers' brief, an assumption, not a rule of law).
  - storey count and building height: a chosen design assumption (a result of the chosen stack and the 10 ft floor-to-floor height).
  - total floor area and floor area left unused: a chosen design assumption (a result of the chosen stack against the legal maximum floor area).

### made-up-building-b - The made-up lot, building B storey by storey (the fewest storeys reaching the minimum base height)

Facts used:

- Made-up interior lot = 100 ft by 100 ft (10,000 sq ft), plain R6B, one 60-ft street, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (source: the readers' made-up interior lot (made_up_lot.json); said to be made up, not a real property)
- Floor-to-floor height = 10 ft (a starting assumption chosen by the owner) (source: starting_values_chosen_by_the_owner.json)
- Maximum floor area = 20,000 sq ft (settled) (source: cases/step-p5-worked.json row floor-area-ratio-made-up-100x100 (settled sheet))

Law relied on:

- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."
- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 23-43 (Height and setback requirements in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."

Why the rule applies: Because building A is below the minimum base height, the method works building B: the fewest 10-ft storeys whose top reaches at least 30 ft is three (top 30 ft; two storeys reach only 20 ft). Spreading the whole 20,000 sq ft maximum over three storeys gives a plan of 20,000 / 3 = 6,666.67 sq ft (100 ft wide by 66.67 ft deep), inside building A's footprint.

Expected value: Building B is three storeys of 6,666.67 sq ft (plan = 20,000 / 3), 20,000 sq ft total with nothing unused, reaching 30 ft = the minimum base height. The plan (100 ft wide by 66.67 ft deep) lies inside building A's 100 by 80 footprint; its street wall on the street line rises to 30 ft, meeting 'at least the minimum base height ... or the height of the #building#, whichever is less' (ZR 23-431(b)). 30 ft is at or below the 45 ft maximum base, so no setback is worked. The figures as numbers are in the block below. Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q3b (3 storeys; plan 6,666.67 = 20,000/3; 30 ft; inside A) and return-independent-hand-calculation-14.md Q3b (same plan, storeys, total and height). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: Both buildings are a plain stack, every storey the same plan: this shape is the method of the example, an assumption chosen in the readers' brief, not a rule of law, not a decision of the owner and not a recommendation of what to build. Both buildings stay at or below the maximum base height, so no storey above the base is counted and no setback is worked. The floor-to-floor height of 10 ft is a starting assumption chosen by the owner, not validated, not measured and not law. It checks a method; it says nothing complies. The made-up lot describes no real property; the example checks a method.

Six steps as numbers (made-up lot, building B (to the minimum base height; a plain stack, every storey the same plan)):

- Property inputs: maximum floor area 20000 sq ft; floor-to-floor height 10 ft; minimum base height 30 ft.
- Footprint: 100 ft frontage x 66.67 ft depth (plan = 20,000 / 3); area 6666.67 sq ft.
- Storeys:
  - Storey 1: floor-to-floor 10 ft; top 10 ft above the base plane; plan area 6666.67 sq ft; floor area 6666.67 sq ft; running total 6666.67 sq ft.
  - Storey 2: floor-to-floor 10 ft; top 20 ft above the base plane; plan area 6666.67 sq ft; floor area 6666.67 sq ft; running total 13333.33 sq ft.
  - Storey 3: floor-to-floor 10 ft; top 30 ft above the base plane; plan area 6666.67 sq ft; floor area 6666.67 sq ft; running total 20000.00 sq ft.
- Total floor area 20000 sq ft; floor area left unused 0 sq ft; building height 30 ft; 3 storeys.
- Each figure above is marked a legal requirement or a chosen design assumption:
  - maximum floor area: a legal requirement (the floor area ratio of ZR 23-22 (R6B standard residences, 2.00) times the lot area).
  - footprint bound by the yards and lot coverage: a legal requirement (the yard sections (ZR 23-322, 23-335, 23-342) and the lot coverage of ZR 23-362).
  - floor-to-floor height 10 ft: a chosen design assumption (a starting value chosen by the owner, not validated, not measured and not law).
  - the same-plan stack: a chosen design assumption (the method of the example in the readers' brief, an assumption, not a rule of law).
  - storey count and building height: a chosen design assumption (a result of the chosen stack and the 10 ft floor-to-floor height).
  - total floor area and floor area left unused: a chosen design assumption (a result of the chosen stack against the legal maximum floor area).
  - plan area = maximum floor area / storeys: a chosen design assumption (a result of spreading the whole legal maximum floor area over the fewest storeys that reach the minimum base height).

### floor-schedule-contents - What a floor schedule must list so a reader can check such a building against each limit

Facts used:

- The buildings worked = building A and building B on the made-up and real lots (source: the worked rows of this case)

Law relied on:

- ZR 23-432 (Height and setback requirements (setback above the maximum base height)) - captured.
  - Capture: snapshot `zr-23-432`, file `docs/research/zr-snapshots/v1/zr-23-432.snapshot.json`.
  - Content digest: `9fab7be8940498b076f7a88dfdd170d9003907e69cefae62305daf807037c68c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432.
  - Quoted: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided at a height not lower than the minimum base height or higher than the maximum base height in accordance with Section 23-433."
- ZR 23-362 (Maximum lot coverage in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."
- ZR 23-342 (Rear yard requirements (detached and zero-lot-line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided"
- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."

Why the rule applies: The columns both readings needed to check a building by hand name the limit each lets a reader check: the storey count and the floor-to-floor height build the running top elevation; the top of each storey above the base plane checks the minimum base (30), maximum base (45) and maximum building (55) heights and whether a setback is triggered; the plan dimensions and footprint check lot coverage, the side and rear yards and the street-wall location; the floor area per storey and the running total check the floor-area maximum and the unused floor area.

Expected value: A floor schedule must list, as both readings name: (1) the storey number and total count; (2) the floor-to-floor height per storey; (3) the height of each storey's top above the base plane (checks the minimum base 30, maximum base 45 and maximum building 55 heights and any setback trigger); (4) the plan dimensions and footprint area (checks lot coverage, the side and rear yards and the street-wall location); (5) the floor area per storey (the per-floor contribution to the floor-area ratio); (6) the running total floor area (checks the maximum floor area and the unused floor area); and (7) the street-wall distance from the street line and the height to which it rises (checks the ZR 23-431 / 35-631 location). Both readings list these same lines.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q3c (storey count; f2f; top above base plane; plan and footprint; floor area per storey; running total; street-wall distance and rear-yard depth) and return-independent-hand-calculation-14.md Q3c (the same columns, each with the limit it lets a reader check). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It lists what a floor schedule must carry; it builds no schedule and checks no building. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-lot-coverage-by-portion - The real lot's lot coverage by portion: the corner-lot portion and the rest, each as both readings measured it

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)

Law relied on:

- ZR 12-10 (Definitions - corner lot (the corner-lot portion)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."
- ZR 23-362 (Maximum lot coverage in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."

Why the rule applies: ZR 12-10 divides the corner lot: the corner-lot portion is within 100 ft of each intersecting street line, the rest is an interior-lot portion. ZR 23-362(a) allows 100 percent coverage on the corner portion and 80 percent on the interior portion. The two readers measured the outline themselves and reached slightly different portion areas, and there is no single whole-lot coverage figure.

Expected value: not known. Not known as a single whole-lot figure; the coverage is read by portion and the two readers' measured areas differ. The corner-lot portion (within 100 ft of both street lines, at 100 percent): reading 13 measures 9,997.60 sq ft, reading 14 measures 9,997.46 sq ft. The remaining interior-lot portion (the strip beyond 100 ft of the 215 Place line, at 80 percent): reading 13 measures 390.39 sq ft (allowing 312.31 sq ft of building), reading 14 measures 390.52 sq ft (allowing 312.42 sq ft). The footprint the portions allow is therefore about 10,310 sq ft (reading 13: 10,309.91; reading 14: 10,309.88) - no single figure. The whole-lot coverage stays not known at cases/corner-reach.json row real-lot-coverage, which this row does not re-answer. KIND OF GAP: the corner/interior split is read, but the exact areas rest on each reader's own measurement of the outline, which differ; a surveyed outline would settle the measured areas.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q4b (corner 9,997.60 at 100%; strip 390.39 at 80% = 312.31; total allowed 10,309.91) and return-independent-hand-calculation-14.md Q4b (corner 9,997.46 at 100%; strip 390.52 at 80% = 312.42; total allowed 10,309.88); the per-portion rule agrees, the measured areas differ. Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records both readers' per-portion areas; it enters no single whole-lot coverage figure (that stays not known at corner-reach#real-lot-coverage). A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-lot-recorded-vs-measured-area - The real lot: the recorded lot area against the area measured from the outline, and what follows for building A

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)

Law relied on:

- ZR 12-10 (Definitions - floor area ratio) - captured.
  - Capture: snapshot `zr-12-10-floor-area-ratio`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area-ratio.snapshot.json`.
  - Content digest: `11e7a3dc9f57ba1718ec5edfebb7aeb0fa6e61698228f70a170c1649d354c8d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the total #floor area# on a #zoning lot#, divided by the #lot area# of that #zoning lot#"

Why the rule applies: The maximum floor area rests on the RECORDED lot area (ZR 12-10 floor area ratio times lot area: 2.00 x 10,075 = 20,150), while each reader's footprint rests on the area MEASURED from the recorded outline, which both readers compute as 10,387.99 sq ft - larger than the recorded 10,075. Both readings use the recorded area for floor area and the measured geometry for the footprint, and neither corrects the other.

Expected value: Two recorded inputs conflict and both readings show it: the RECORDED lot area is 10,075 sq ft (giving the maximum floor area 2.00 x 10,075 = 20,150 sq ft), while the area MEASURED from the recorded outline is 10,387.99 sq ft (both readings), about 312.99 sq ft (roughly 3.1 percent) larger. Both readings use the recorded 10,075 for the floor area and the measured outline for the footprint, and neither area is corrected or called the right one. What follows for building A: because the measured footprint (about 10,310 sq ft) is more than half the 20,150 sq ft maximum, a second storey would pass the maximum, so the method gives building A one storey under either reading. The conflict between the two recorded inputs stays visible.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q4b (measured 10,387.99 vs recorded 10,075; +3.1%; recorded used for floor area) and return-independent-hand-calculation-14.md Q4b (measured 10,387.99 equals the served Shape__Area; exceeds the recorded lotarea by about 313 sq ft; recorded used for floor area). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records a conflict between two recorded inputs and leaves both standing; it corrects neither and calls neither right. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-lot-rear-yard-variants - The real lot: the rear yard beyond the corner area, with the missing fact that would select each variant

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Adjoining zoning lots' lot-line types = not in the readers' folder (source: the readers' fact sheet (lot_facts_pluto.json))

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
- ZR 23-344 (Additional rear yard modifications (rear-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "a #rear yard# shall be provided in accordance with Section 23-342 (Rear yard requirements), where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#."
- ZR 23-344 (Additional rear yard modifications (R6-R12, side-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#."
- ZR 23-342 (Rear yard requirements (detached and zero-lot-line buildings)) - captured.
  - Capture: snapshot `zr-23-342`, file `docs/research/zr-snapshots/v1/zr-23-342.snapshot.json`.
  - Content digest: `1fece34420276aae6ca35f83b23929cea060b6cfee8871dbcea95edf44fb69c6`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-342.
  - Quoted: "For #detached# and #zero lot line buildings#, for #buildings# or portions thereof at or below a height of 75 feet, as measured from #base plane#, a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# on any #zoning lot#, and for portions above 75 feet, where permitted, a #rear yard# with a depth of 30 feet shall be provided"

Why the rule applies: ZR 23-344(a) requires no rear yard within 100 ft of the roughly 89.7-degree corner. Beyond 100 ft of the street line, ZR 23-344(c) deems the far portion of a side lot line a rear lot line, and then the rear yard turns on the adjoining lot: a 20 ft rear yard (ZR 23-342) where the deemed rear lot line coincides with a neighbour's rear lot line (c)(1), or none where it coincides with a neighbour's side lot line (c)(3). Which one applies needs the adjoining lots' lot-line types, not in the folder.

Expected value: not known. Not known; the rear yard beyond the corner area stays not known. Within 100 ft of the corner no rear yard is required (ZR 23-344(a); the corner angle is about 89.7 degrees). Beyond 100 ft of the 215 Place line a short portion of a side lot line is deemed a rear lot line (ZR 23-344(c)), and then two variants follow, by content: where that deemed rear lot line coincides with a NEIGHBOUR'S REAR lot line, a 20 ft rear yard is required (ZR 23-344(c)(1), ZR 23-342); where it coincides with a NEIGHBOUR'S SIDE lot line, no rear yard is required (ZR 23-344(c)(3)). (The two readings attach the labels V1 and V2 to these two variants in opposite order, so the variants are described here by content, not by label.) KIND OF GAP: a missing fact about the property - the adjoining zoning lots' lot-line types along that segment, which would come from a survey, a deed or a record of the neighbouring lots. The readings also carry a known dispute from the earlier readers about which edge lies beyond 100 ft (held not known on the settled sheet). No variant is the answer.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q4c (within 100 ft none; beyond, a deemed rear lot line; neighbour side lot line -> no rear yard, neighbour rear lot line -> 20 ft; selector not known) and return-independent-hand-calculation-14.md Q4c (same two variants and selector; the far-edge geometry itself disputed between the earlier readers). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records the rear yard beyond the corner as not known and names the missing fact; no variant is presented as the answer. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-lot-street-wall - The real lot: where the street wall must or may stand, and whether it changes the footprint

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Street-wall rule that applies = the percentage rule of ZR 35-631(b) (settled) (source: cases/overlay-reading.json row street-wall-location (settled sheet))

Law relied on:

- ZR 35-631 (Street wall location (percentage-based rules, overlay)) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."
- ZR 23-436 (Additional height and setback provisions (corner lots, one frontage)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "On #corner lots#, or portions thereof, the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one of the #street# frontages bounding the #corner lot# is a #wide street# and the other a #narrow street#, the #street wall# location rules shall be applied along the #wide street# frontage;"
- ZR 35-633 (Additional height and setback provisions (street-wall supersession)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and"
- ZR 35-633 (Additional height and setback provisions (one-frontage corner clause)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage."
- ZR 23-431 (Street wall location (line-up rules)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "In R6B, R7B, and R8B Districts, the #street wall# of a #building# shall be located no closer to the #street line# than the closest #street wall#, or portion thereof, nor further from the #street line# than the furthest #street wall#, or portion thereof, of an existing adjacent #building# on the same or an adjoining #zoning lot# located on the same #street# frontage. Eligible adjacent #buildings# shall be located within 15 feet of the #street line#, within 25 feet of the subject #building#, and have a height that exceeds 35 feet."

Why the rule applies: ZR 23-436(c) (via the ZR 35-633(a) supersession to 35-631) makes the street-wall location mandatory along only one frontage, the wide Northern Boulevard. The percentage rule of ZR 35-631(b) puts at least 70 percent of the aggregate street-wall width within 8 ft of the street line; the widest building stands on the line. Along 215 Place the location is not mandatory unless the ZR 35-633(b) whole-block commercial-mapping condition holds, which the readers could not confirm; and the prevailing-frontage fall-back is optional and needs neighbour data.

Expected value: The street-wall location is mandatory along the wide Northern Boulevard frontage (ZR 23-436(c) via ZR 35-633(a); the percentage rule of ZR 35-631(b)); the widest building places its wall on that street line, so at least 70 percent lies within 8 ft, satisfied at the line. Along the narrow 215 Place frontage the location is not mandatory, UNLESS a Commercial District is mapped along the entire 215 Place block frontage (ZR 35-633(b)) - which the readers could not confirm. The prevailing-frontage fall-back of ZR 23-431(a) is optional ('may be applied') and needs neighbour street-wall data the readers did not have. Both readings agree the street wall creates NO footprint-changing variant: the widest building stands on the street lines either way. The condition raised by both readings (the 215 Place mandatory question and the prevailing frontage) is stated in this value and does not change the widest footprint.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q4d (mandatory on Northern Boulevard; on the line; 215 Place not mandatory; prevailing frontage optional, so no footprint variant) and return-independent-hand-calculation-14.md Q4d (same; the 215 Place duty turns on whole-block commercial mapping, not known, but does not change the footprint). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads which frontage binds and that no footprint-changing street-wall variant arises; whether the street wall is also mandatory along 215 Place it leaves not known. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-lot-ground-elevations - The real lot: what the missing ground elevations leave open, and what they do not

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Ground / curb elevations = not in the readers' folder (source: the readers' fact sheet; cases/step-p3-worked.json row base-plane-real-lot (settled))

Law relied on:

- ZR 23-43 (Height and setback requirements in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."
- ZR 12-10 (Definitions - base plane (within 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "the level of the #base plane# is any level between #curb level# and #street wall line level#"
- ZR 12-10 (Definitions - base plane (beyond 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Beyond 100 feet of a #street line#, the level of the #base plane# is the average elevation of the final grade adjoining the #building# or #building segment#"

Why the rule applies: Heights are measured from the base plane (ZR 23-43). The base-plane elevation needs curb level, street-wall-line level and adjoining final grade (ZR 12-10 base plane), none in the folder, so the absolute elevations are undetermined; but the heights ABOVE the base plane are fixed because they are all measured from it.

Expected value: What the missing ground elevations leave open: the absolute elevation of the base plane (the datum from which 30/45/55 ft are measured), because curb level, street-wall-line level and adjoining final grade are not in the folder (ZR 12-10 base plane); so the absolute top elevations and the exact slab heights above grade are undetermined. What they do NOT leave open: the heights ABOVE the base plane - the 30 ft minimum base, 45 ft maximum base, 55 ft maximum building, and the storey counts at 10 ft floor-to-floor - which are fixed regardless of the datum, because they are all measured from the base plane (ZR 23-43). Both readings agree. The base-plane datum itself stays not known at cases/step-p3-worked.json row base-plane-real-lot, which this row does not re-answer.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q4e (datum not known; relative heights fixed from the base plane) and return-independent-hand-calculation-14.md Q4e (same; absolute elevation open, the relative tests hold). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It reads what the missing elevations leave open and what they fix; the base-plane datum stays not known at step-p3-worked#base-plane-real-lot. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### real-building-a - The real lot, building A storey by storey (the widest footprint; its exact area differs between the readings)

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Floor-to-floor height = 10 ft (a starting assumption chosen by the owner) (source: starting_values_chosen_by_the_owner.json)

Law relied on:

- ZR 23-362 (Maximum lot coverage in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-362`, file `docs/research/zr-snapshots/v1/zr-23-362.snapshot.json`.
  - Content digest: `f8370a389af6ffde27b0991b456868be6d9312a67df07e8c5864ea193b40acd9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-362.
  - Quoted: "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."
- ZR 35-631 (Street wall location (percentage-based rules, overlay)) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."
- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 23-43 (Height and setback requirements in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."

Why the rule applies: Building A is the widest footprint (the lot-coverage-allowed area) stacked at 10 ft. Because that footprint (about 10,310 sq ft) is more than half the 20,150 sq ft maximum floor area, a second storey would pass the maximum, so building A is one storey under either reading. Its 10 ft height is below the 30 ft minimum base height (permitted, ZR 23-436(e)), so no setback is worked and the method calls for building B. The two readers' measured footprints differ, so the footprint and the one-storey floor area are held as both figures, not smoothed.

Expected value: Building A is ONE storey, height 10 ft, which is BELOW the 30 ft minimum base height (permitted, ZR 23-436(e); the street wall need rise only to 10 ft), below the 45 ft maximum base and 55 ft maximum building, so no setback is worked; because it is below the minimum base height the method calls for building B. The storey count (1), the height (10 ft) and the below-minimum-base result are the same under both readings and under every rear-yard variant. The exact footprint and one-storey floor area are NOT a single figure: reading 13 measures 10,309.91 sq ft (9,840.09 sq ft unused against the 20,150 maximum), reading 14 measures 10,309.88 sq ft (9,840.12 unused); the rear-yard variant beyond the corner would reduce the footprint further, and that part stays not known. Both figures are held in the block below.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q5 V1 (1 storey; footprint 10,309.91; below min base; calls for B) and return-independent-hand-calculation-14.md Q5 (1 storey; footprint 10,309.88; below min base; calls for B); the storey count agrees, the measured footprint differs. Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: Both buildings are a plain stack, every storey the same plan: this shape is the method of the example, an assumption chosen in the readers' brief, not a rule of law, not a decision of the owner and not a recommendation of what to build. Both buildings stay at or below the maximum base height, so no storey above the base is counted and no setback is worked. The floor-to-floor height of 10 ft is a starting assumption chosen by the owner, not validated, not measured and not law. It checks a method; it says nothing complies. The exact footprint and floor area differ between the two readings and under the rear-yard variant, so no single figure is entered; a surveyed outline and the adjoining lot-line types would settle them.

Six steps as numbers (real lot, building A (the widest; a plain stack; the footprint differs between the two readings)):

- Property inputs: maximum floor area 20150 sq ft; floor-to-floor height 10 ft; minimum base height 30 ft.
- Footprint: the lot-coverage-allowed footprint (corner portion at 100% plus the interior strip at 80%); reading 13: 10,309.91 sq ft, reading 14: 10,309.88 sq ft; area 10309.91 (reading 13) / 10309.88 (reading 14) sq ft.
- Storeys:
  - Storey 1: floor-to-floor 10 ft; top 10 ft above the base plane; plan area 10309.91 (reading 13) / 10309.88 (reading 14) sq ft; floor area 10309.91 (reading 13) / 10309.88 (reading 14) sq ft; running total 10309.91 (reading 13) / 10309.88 (reading 14) sq ft.
- Total floor area 10309.91 (reading 13) / 10309.88 (reading 14) sq ft; floor area left unused 9840.09 (reading 13) / 9840.12 (reading 14) sq ft; building height 10 ft; 1 storeys.
- Each figure above is marked a legal requirement or a chosen design assumption:
  - maximum floor area: a legal requirement (the floor area ratio of ZR 23-22 (R6B standard residences, 2.00) times the lot area).
  - footprint bound by the yards and lot coverage: a legal requirement (the yard sections (ZR 23-322, 23-335, 23-342) and the lot coverage of ZR 23-362).
  - floor-to-floor height 10 ft: a chosen design assumption (a starting value chosen by the owner, not validated, not measured and not law).
  - the same-plan stack: a chosen design assumption (the method of the example in the readers' brief, an assumption, not a rule of law).
  - storey count and building height: a chosen design assumption (a result of the chosen stack and the 10 ft floor-to-floor height).
  - total floor area and floor area left unused: a chosen design assumption (a result of the chosen stack against the legal maximum floor area).

### real-building-b - The real lot, building B storey by storey (the fewest storeys reaching the minimum base height; the same under every variant)

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Floor-to-floor height = 10 ft (a starting assumption chosen by the owner) (source: starting_values_chosen_by_the_owner.json)

Law relied on:

- ZR 23-431 (Street wall location (percentage-based rules, wide streets)) - captured.
  - Capture: snapshot `zr-23-431`, file `docs/research/zr-snapshots/v1/zr-23-431.snapshot.json`.
  - Content digest: `fb2d094dd06ce10b406485932357a39384a357db92a0a1670b56091c36698c69`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-431.
  - Quoted: "Along #wide streets#, at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less."
- ZR 35-631 (Street wall location (percentage-based rules, overlay)) - captured.
  - Capture: snapshot `zr-35-631`, file `docs/research/zr-snapshots/v1/zr-35-631.snapshot.json`.
  - Content digest: `816bc74770e48596144479c24adf382082d0ebf3392dabd0ef5745f844a928f9`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-631.
  - Quoted: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less."
- ZR 23-436 (Additional height and setback provisions (minimum base height)) - captured.
  - Capture: snapshot `zr-23-436`, file `docs/research/zr-snapshots/v1/zr-23-436.snapshot.json`.
  - Content digest: `06259c32014c35341ee2b0dce3ec6476b4a7c91b2266b545f5556f3498d1312c`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-436.
  - Quoted: "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights."
- ZR 23-43 (Height and setback requirements in R6 through R12 districts) - captured.
  - Capture: snapshot `zr-23-43`, file `docs/research/zr-snapshots/v1/zr-23-43.snapshot.json`.
  - Content digest: `f5a7cf614d946db4c55bc40168c75f81607707bc087503b22c2343145db41061`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-43.
  - Quoted: "The height of all #buildings or other structures# shall be measured from the #base plane#."

Why the rule applies: Because building A is below the minimum base height, the method works building B: the fewest 10-ft storeys whose top reaches at least 30 ft is three. Spreading the whole 20,150 sq ft maximum over three storeys gives a plan of 20,150 / 3 = 6,716.67 sq ft (about 103.9 ft along Northern Boulevard by about 64.66 ft deep), kept within the corner-lot portion and inside building A's footprint. Building B uses the maximum floor area, not the footprint, so it is the same under every variant.

Expected value: Building B is three storeys of 6,716.67 sq ft (plan = 20,150 / 3), 20,150 sq ft total with nothing unused, reaching 30 ft = the minimum base height. The plan (about 103.9 ft along Northern Boulevard by about 64.66 ft deep) stays within the corner-lot portion and inside building A's footprint; its street wall on the Northern Boulevard street line rises to 30 ft, meeting ZR 35-631(b) 'whichever is less'. 30 ft is at or below the 45 ft maximum base, so no setback is worked. Building B is the SAME under every rear-yard and street-wall variant, because it uses the maximum floor area, not the footprint. The figures as numbers are in the block below; both readings agree exactly.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q5 (3 storeys; plan 6,716.67 = 20,150/3; 30 ft; same under every variant) and return-independent-hand-calculation-14.md Q5 (same plan, storeys, total and height; the same under every variant). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: Both buildings are a plain stack, every storey the same plan: this shape is the method of the example, an assumption chosen in the readers' brief, not a rule of law, not a decision of the owner and not a recommendation of what to build. Both buildings stay at or below the maximum base height, so no storey above the base is counted and no setback is worked. The floor-to-floor height of 10 ft is a starting assumption chosen by the owner, not validated, not measured and not law. It checks a method; it says nothing complies.

Six steps as numbers (real lot, building B (to the minimum base height; a plain stack, every storey the same plan)):

- Property inputs: maximum floor area 20150 sq ft; floor-to-floor height 10 ft; minimum base height 30 ft.
- Footprint: about 103.9 ft along the Northern Boulevard frontage x about 64.66 ft deep (plan = 20,150 / 3), kept within the corner-lot portion; area 6716.67 sq ft.
- Storeys:
  - Storey 1: floor-to-floor 10 ft; top 10 ft above the base plane; plan area 6716.67 sq ft; floor area 6716.67 sq ft; running total 6716.67 sq ft.
  - Storey 2: floor-to-floor 10 ft; top 20 ft above the base plane; plan area 6716.67 sq ft; floor area 6716.67 sq ft; running total 13433.33 sq ft.
  - Storey 3: floor-to-floor 10 ft; top 30 ft above the base plane; plan area 6716.67 sq ft; floor area 6716.67 sq ft; running total 20150.00 sq ft.
- Total floor area 20150 sq ft; floor area left unused 0 sq ft; building height 30 ft; 3 storeys.
- Each figure above is marked a legal requirement or a chosen design assumption:
  - maximum floor area: a legal requirement (the floor area ratio of ZR 23-22 (R6B standard residences, 2.00) times the lot area).
  - footprint bound by the yards and lot coverage: a legal requirement (the yard sections (ZR 23-322, 23-335, 23-342) and the lot coverage of ZR 23-362).
  - floor-to-floor height 10 ft: a chosen design assumption (a starting value chosen by the owner, not validated, not measured and not law).
  - the same-plan stack: a chosen design assumption (the method of the example in the readers' brief, an assumption, not a rule of law).
  - storey count and building height: a chosen design assumption (a result of the chosen stack and the 10 ft floor-to-floor height).
  - total floor area and floor area left unused: a chosen design assumption (a result of the chosen stack against the legal maximum floor area).
  - plan area = maximum floor area / storeys: a chosen design assumption (a result of spreading the whole legal maximum floor area over the fewest storeys that reach the minimum base height).

### made-up-estimate-a - The made-up lot, building A: the preliminary apartment estimate (arithmetic on the owner's starting assumptions)

Facts used:

- Owner's starting values = share of residential floor area inside apartments 0.60 to 0.75 (a preliminary assumption); starting apartment size 700 sq ft (a preliminary assumption) (source: starting_values_chosen_by_the_owner.json)
- Residential floor area the building holds = 16,000 sq ft (source: this case row made-up-building-a (the stacked floor area))

Law relied on:

- none cited

Why the rule applies: The estimate is arithmetic on the owner's starting assumptions, kept apart from the legal dwelling-unit ceiling: the residential floor area the building holds (16,000 sq ft) times the share range 0.60 and 0.75, divided by the 700 sq ft apartment size, to two decimals, with the whole numbers just below and just above. It is not law and no value comes from a program run.

Expected value: Preliminary apartment estimate for made-up building A (16,000 sq ft of floor area): at the 0.60 share, 16,000 x 0.60 / 700 = 13.71 (whole numbers 13 below, 14 above); at the 0.75 share, 16,000 x 0.75 / 700 = 17.14 (17 below, 18 above). The share range 0.60 to 0.75 and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner. The figures as numbers are in the block below. Both readings give the same two quotients and whole numbers.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6a (16,000 -> 13.71 -> 13/14 and 17.14 -> 17/18) and return-independent-hand-calculation-14.md Q6a (the same two quotients and whole numbers). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: These figures are arithmetic on the owner's starting assumptions, kept apart from the legal dwelling-unit ceiling, which is a separate row. The share range 0.60 to 0.75 and the apartment size 700 sq ft are each a preliminary assumption chosen by the owner, not law and not measured. The two quotients are shown to two decimals with the whole numbers just below and just above; no rounding to a whole number is made, because no rounding rule was given. They are not a ceiling, not checked against real buildings and say nothing complies.

Six steps as numbers (made-up lot, building A):

- Residential floor area the building holds: 16000 sq ft.
- Share range 0.60 to 0.75 (a preliminary assumption); apartment size 700 sq ft (a preliminary assumption).
- At the 0.60 share: quotient 13.71 (whole numbers 13 below, 14 above).
- At the 0.75 share: quotient 17.14 (whole numbers 17 below, 18 above).
- Each figure above is marked a legal requirement or a chosen design assumption:
  - residential floor area the building holds: a chosen design assumption (a result of the chosen same-plan stack, not a legal requirement).
  - share range 0.60 to 0.75: a chosen design assumption (a preliminary assumption chosen by the owner, an unvalidated sensitivity range, not law).
  - apartment size 700 sq ft: a chosen design assumption (a preliminary assumption chosen by the owner, not measured and not law).

### made-up-estimate-b - The made-up lot, building B: the preliminary apartment estimate

Facts used:

- Owner's starting values = share of residential floor area inside apartments 0.60 to 0.75 (a preliminary assumption); starting apartment size 700 sq ft (a preliminary assumption) (source: starting_values_chosen_by_the_owner.json)
- Residential floor area the building holds = 20,000 sq ft (source: this case row made-up-building-b (the stacked floor area))

Law relied on:

- none cited

Why the rule applies: The estimate is arithmetic on the owner's starting assumptions, kept apart from the legal ceiling: 20,000 sq ft of floor area times 0.60 and 0.75, divided by 700, to two decimals with the whole numbers below and above.

Expected value: Preliminary apartment estimate for made-up building B (20,000 sq ft of floor area): at 0.60, 20,000 x 0.60 / 700 = 17.14 (17 below, 18 above); at 0.75, 20,000 x 0.75 / 700 = 21.43 (21 below, 22 above). The share range and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner. The figures as numbers are in the block below. Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6a (20,000 -> 17.14 -> 17/18 and 21.43 -> 21/22) and return-independent-hand-calculation-14.md Q6a (same). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: These figures are arithmetic on the owner's starting assumptions, kept apart from the legal dwelling-unit ceiling, which is a separate row. The share range 0.60 to 0.75 and the apartment size 700 sq ft are each a preliminary assumption chosen by the owner, not law and not measured. The two quotients are shown to two decimals with the whole numbers just below and just above; no rounding to a whole number is made, because no rounding rule was given. They are not a ceiling, not checked against real buildings and say nothing complies.

Six steps as numbers (made-up lot, building B):

- Residential floor area the building holds: 20000 sq ft.
- Share range 0.60 to 0.75 (a preliminary assumption); apartment size 700 sq ft (a preliminary assumption).
- At the 0.60 share: quotient 17.14 (whole numbers 17 below, 18 above).
- At the 0.75 share: quotient 21.43 (whole numbers 21 below, 22 above).
- Each figure above is marked a legal requirement or a chosen design assumption:
  - residential floor area the building holds: a chosen design assumption (a result of the chosen same-plan stack, not a legal requirement).
  - share range 0.60 to 0.75: a chosen design assumption (a preliminary assumption chosen by the owner, an unvalidated sensitivity range, not law).
  - apartment size 700 sq ft: a chosen design assumption (a preliminary assumption chosen by the owner, not measured and not law).

### real-estimate-a - The real lot, building A: the preliminary apartment estimate (the floor area differs between the readings)

Facts used:

- Owner's starting values = share of residential floor area inside apartments 0.60 to 0.75 (a preliminary assumption); starting apartment size 700 sq ft (a preliminary assumption) (source: starting_values_chosen_by_the_owner.json)
- Residential floor area the building holds = about 10,310 sq ft (reading 13: 10,309.91; reading 14: 10,309.88) (source: this case row real-building-a (the stacked floor area))

Law relied on:

- none cited

Why the rule applies: The estimate is arithmetic on the owner's starting assumptions: the floor area building A holds (about 10,310 sq ft; the two readers' measured footprints differ) times 0.60 and 0.75, divided by 700, to two decimals. The two readers' floor areas differ, but both give the same two quotients to two decimals.

Expected value: Preliminary apartment estimate for real building A (floor area about 10,310 sq ft; reading 13 10,309.91, reading 14 10,309.88): at 0.60, floor area x 0.60 / 700 = 8.84 (8 below, 9 above); at 0.75, floor area x 0.75 / 700 = 11.05 (11 below, 12 above). Both readers' floor areas, though they differ, give the same two quotients to two decimals; both floor areas are held in the block below. These rest on the no-rear-yard footprint; the rear-yard variant beyond the corner would lower the floor area and the estimate slightly, and that part stays not known. The share range and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6a (real A 10,309.91 -> 8.84 -> 8/9 and 11.05 -> 11/12) and return-independent-hand-calculation-14.md Q6a (real A 10,309.88 -> 8.84 -> 8/9 and 11.05 -> 11/12); the floor areas differ, the two-decimal quotients agree. Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: These figures are arithmetic on the owner's starting assumptions, kept apart from the legal dwelling-unit ceiling, which is a separate row. The share range 0.60 to 0.75 and the apartment size 700 sq ft are each a preliminary assumption chosen by the owner, not law and not measured. The two quotients are shown to two decimals with the whole numbers just below and just above; no rounding to a whole number is made, because no rounding rule was given. They are not a ceiling, not checked against real buildings and say nothing complies. The rear-yard variant beyond the corner would lower the floor area and the estimate; that part stays not known.

Six steps as numbers (real lot, building A):

- Residential floor area the building holds: 10309.91 (reading 13) / 10309.88 (reading 14) sq ft.
- Share range 0.60 to 0.75 (a preliminary assumption); apartment size 700 sq ft (a preliminary assumption).
- At the 0.60 share: quotient 8.84 (whole numbers 8 below, 9 above).
- At the 0.75 share: quotient 11.05 (whole numbers 11 below, 12 above).
- Each figure above is marked a legal requirement or a chosen design assumption:
  - residential floor area the building holds: a chosen design assumption (a result of the chosen same-plan stack, not a legal requirement).
  - share range 0.60 to 0.75: a chosen design assumption (a preliminary assumption chosen by the owner, an unvalidated sensitivity range, not law).
  - apartment size 700 sq ft: a chosen design assumption (a preliminary assumption chosen by the owner, not measured and not law).

### real-estimate-b - The real lot, building B: the preliminary apartment estimate

Facts used:

- Owner's starting values = share of residential floor area inside apartments 0.60 to 0.75 (a preliminary assumption); starting apartment size 700 sq ft (a preliminary assumption) (source: starting_values_chosen_by_the_owner.json)
- Residential floor area the building holds = 20,150 sq ft (source: this case row real-building-b (the stacked floor area))

Law relied on:

- none cited

Why the rule applies: The estimate is arithmetic on the owner's starting assumptions: 20,150 sq ft of floor area times 0.60 and 0.75, divided by 700, to two decimals with the whole numbers below and above.

Expected value: Preliminary apartment estimate for real building B (20,150 sq ft of floor area): at 0.60, 20,150 x 0.60 / 700 = 17.27 (17 below, 18 above); at 0.75, 20,150 x 0.75 / 700 = 21.59 (21 below, 22 above). The share range and the 700 sq ft apartment size are each a preliminary assumption chosen by the owner. The figures as numbers are in the block below. Both readings agree.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6a (real B 20,150 -> 17.27 -> 17/18 and 21.59 -> 21/22) and return-independent-hand-calculation-14.md Q6a (same). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: These figures are arithmetic on the owner's starting assumptions, kept apart from the legal dwelling-unit ceiling, which is a separate row. The share range 0.60 to 0.75 and the apartment size 700 sq ft are each a preliminary assumption chosen by the owner, not law and not measured. The two quotients are shown to two decimals with the whole numbers just below and just above; no rounding to a whole number is made, because no rounding rule was given. They are not a ceiling, not checked against real buildings and say nothing complies.

Six steps as numbers (real lot, building B):

- Residential floor area the building holds: 20150 sq ft.
- Share range 0.60 to 0.75 (a preliminary assumption); apartment size 700 sq ft (a preliminary assumption).
- At the 0.60 share: quotient 17.27 (whole numbers 17 below, 18 above).
- At the 0.75 share: quotient 21.59 (whole numbers 21 below, 22 above).
- Each figure above is marked a legal requirement or a chosen design assumption:
  - residential floor area the building holds: a chosen design assumption (a result of the chosen same-plan stack, not a legal requirement).
  - share range 0.60 to 0.75: a chosen design assumption (a preliminary assumption chosen by the owner, an unvalidated sensitivity range, not law).
  - apartment size 700 sq ft: a chosen design assumption (a preliminary assumption chosen by the owner, not measured and not law).

### made-up-unit-limit - The made-up lot: the legal ceiling on dwelling units (the current answer, superseding the step-P4 conditional unit count, kept apart from the estimate)

Facts used:

- Maximum floor area = 20,000 sq ft (settled) (source: cases/step-p5-worked.json row floor-area-ratio-made-up-100x100 (settled sheet))
- Dwelling-unit factor = 680 (settled) (source: cases/step-p4-worked.json row dwelling-unit-factors (settled sheet))
- Earlier conditional count = 29 dwelling units, but only conditionally (source: cases/step-p4-worked.json row made-up-100x100-units (now superseded by this row))

Law relied on:

- ZR 23-52 (Maximum number of dwelling units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor"
- ZR 23-52 (Maximum number of dwelling units (factor 680)) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."

Why the rule applies: ZR 23-52 divides the maximum residential floor area by the dwelling-unit factor (680 for standard residences), and a fraction of three-quarters or more counts as one dwelling unit. For the made-up lot, 20,000 / 680 = 29.41; the fraction 0.41 is below three-quarters, so 29. This is the current answer to the made-up lot's dwelling-unit ceiling and supersedes the step-P4 row made-up-100x100-units; it is a legal ceiling, separate from the preliminary estimate.

Working, step by step:

- legal dwelling-unit ceiling (maximum floor area / factor): 20,000 (maximum residential floor area (square feet)) / 680 (dwelling-unit factor (ZR 23-52)) = 29.41...; a fraction below three-quarters is dropped -> 29

Expected value: 29 dwelling units (ZR 23-52: 20,000 / 680 = 29.41; the fraction 0.41 is below three-quarters, so 29), subject to one remaining condition. The step-P4 row made-up-100x100-units held 29 'but only conditionally' and attached two conditions, which this row updates: (first) the condition both step-P4 readings attached - that the definition of floor area ratio (floor area = ratio x lot area) was outside their folder - has since been settled by step-p5-worked#floor-area-ratio-made-up-100x100 (2.00 x 10,000 = 20,000 sq ft), which both step-P6 readers were given as settled, so the 20,000 sq ft floor area no longer rests on an assumption; (second) the condition reading 10 attached - 'that the building is one containing multiple dwelling residences, a term the readers did not have' (as the step-P4 row words it) - was not read by reading 13 or reading 14 (the multiple-dwelling-residence definition was in the step-P6 folder but neither reading read it), so it was not examined and still stands as a condition of the 29. The 29 therefore holds subject to the building being a multiple dwelling residence.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6b (made-up 20,000 / 680 = 29.41 -> 29) and return-independent-hand-calculation-14.md Q6b (same); the step-P4 row made-up-100x100-units and its reading-10 second condition; the settled step-p5-worked#floor-area-ratio-made-up-100x100. Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It gives the current legal dwelling-unit ceiling for the made-up lot (29, subject to the remaining multiple-dwelling-residence condition), superseding the step-P4 row made-up-100x100-units; it is kept apart from the preliminary estimate and says nothing complies. The made-up lot describes no real property; the example checks a method.

### real-unit-limit - The real lot: the legal dwelling-unit ceiling, which RESTATES cases/real-lot.json row L6 (the current answer, kept unchanged) for step 5 of the six-step comparison

Facts used:

- Maximum residential floor area = 20,150 sq ft (settled) (source: cases/real-lot.json row L1 (settled sheet))
- Dwelling-unit ceiling = 29 (the current answer, restated from row L6) (source: cases/real-lot.json row L6 (the current answer, kept unchanged))
- Dwelling-unit factor = 680 (settled) (source: cases/step-p4-worked.json row dwelling-unit-factors (settled sheet))

Law relied on:

- ZR 23-52 (Maximum number of dwelling units) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor"
- ZR 23-52 (Maximum number of dwelling units (factor 680)) - captured.
  - Capture: snapshot `zr-23-52`, file `docs/research/zr-snapshots/v1/zr-23-52.snapshot.json`.
  - Content digest: `f48f1ddc189866ea7fae015edb983411c6de5032d0f9ce98a47cdca4d7b908ac`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52.
  - Quoted: "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#."

Why the rule applies: This row restates the real lot's legal dwelling-unit ceiling for step 5 of the six-step comparison; it does not read it afresh. The current answer stays at cases/real-lot.json row L6, which other tasks read; its figure (29) is restated here mechanically, and a test pins this figure to the live value of row L6 so the two can never disagree. ZR 23-52 divides the maximum residential floor area by the factor 680 (20,150 / 680 = 29.63; the fraction 0.63 is below three-quarters, so 29).

Working, step by step:

- legal dwelling-unit ceiling (maximum floor area / factor): 20,150 (maximum residential floor area (square feet)) / 680 (dwelling-unit factor (ZR 23-52)) = 29.63...; a fraction below three-quarters is dropped -> 29

Expected value: 29 dwelling units

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q6b (real lot = 29; 20,150 / 680 = 29.63 -> 29; settled at real-lot#L6) and return-independent-hand-calculation-14.md Q6b (same; settled at real-lot#L6). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It restates the current answer held by cases/real-lot.json row L6 (which remains the current answer and is kept unchanged, because other tasks read it) for step 5 of the comparison; its figure is pinned by a test to the live value of row L6 so the two can never disagree. It is kept apart from the estimate and says nothing complies.

### both-readers-did-not-have - What both readers did not have (a text outside their folder that an answer waits on)

Facts used:

- Both readings' lists of texts not had = the Q7 lists of both readings (source: return-independent-hand-calculation-13.md Q7 and return-independent-hand-calculation-14.md Q7)

Law relied on:

- ZR 12-10 (Definitions - base plane (within 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "the level of the #base plane# is any level between #curb level# and #street wall line level#"

Why the rule applies: Both readings name, each in its own Q7, the same texts as outside their folder; this list holds ONLY what BOTH name, so each item is one the readers did not have, with the answer it leaves open.

Expected value: The readers did not have (an item is here only where BOTH readings name it): (1) the ZR 12-10 term 'street wall line level' - keeps the real lot's base-plane datum not known; (2) the adjoining final-grade / ground elevations the base-plane definition needs beyond 100 ft - keeps the base-plane datum not known; (3) ZR 23-434 (height and setback modifications for eligible sites) - not relied on, no eligible-site figure is used; (4) ZR 23-435 (towers) - not relied on, no tower figure is used; (5) the ZR 12-10 term 'outer court' - affects only recess geometry, which the simple walls worked do not use. The readers did not have these texts; a text the readers did not have may be captured later.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q7 (street wall line level; base-plane grade inputs; ZR 23-434; ZR 23-435; outer court) and return-independent-hand-calculation-14.md Q7 (the same five among its longer list); the list here holds only what both name. Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It lists only what both readers did not have; it draws no conclusion from the absence beyond naming the answer each leaves open. A draft reading by AI helpers, not professionally reviewed.

### real-lot-missing-facts - The missing facts about the real lot, each with the variant it selects and its kind of gap

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)
- Both readings' lists of missing facts = the Q7 fact lists of both readings (source: return-independent-hand-calculation-13.md Q7 and return-independent-hand-calculation-14.md Q7)

Law relied on:

- ZR 23-344 (Additional rear yard modifications (rear-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "a #rear yard# shall be provided in accordance with Section 23-342 (Rear yard requirements), where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#."
- ZR 23-344 (Additional rear yard modifications (R6-R12, side-lot-line coincidence)) - captured.
  - Capture: snapshot `zr-23-344`, file `docs/research/zr-snapshots/v1/zr-23-344.snapshot.json`.
  - Content digest: `91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344.
  - Quoted: "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#."
- ZR 35-633 (Additional height and setback provisions (one-frontage corner clause)) - captured.
  - Capture: snapshot `zr-35-633`, file `docs/research/zr-snapshots/v1/zr-35-633.snapshot.json`.
  - Content digest: `4f5b0635ad96a2eaf403c5e6d824be211b1c61a545274579cb0ee891e40d0ad3`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-633.
  - Quoted: "for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage."
- ZR 12-10 (Definitions - base plane (beyond 100 feet of a street line)) - captured.
  - Capture: snapshot `zr-12-10-base-plane`, file `docs/research/zr-snapshots/v1/zr-12-10-base-plane.snapshot.json`.
  - Content digest: `f57cd9b62e591236908fe65163f7162605e03ca8604c5c4e6fe4e48a4f56eae2`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "Beyond 100 feet of a #street line#, the level of the #base plane# is the average elevation of the final grade adjoining the #building# or #building segment#"

Why the rule applies: Both readings name the same missing facts about the real lot and the variant each would select: the adjoining lot-line types (the rear yard beyond the corner), the neighbouring street walls (the prevailing frontage), and the ground elevations (the base-plane datum). Each is a missing fact about the property, not unresolved law.

Expected value: The missing facts about the real lot, each a missing fact about the property (KIND OF GAP), with where it would come from and what it selects: (1) the adjoining zoning lots' lot-line types along the deemed rear lot line (from a survey, a deed or a record of the neighbouring lots) -> selects the rear yard beyond the corner (a neighbour's rear lot line gives a 20 ft rear yard, a neighbour's side lot line gives none); (2) the neighbouring buildings' street-wall widths and distances (from a record of the neighbouring buildings) -> whether a prevailing street wall frontage exists, which is optional and does not change the widest footprint; (3) the ground / curb / grade elevations (from a survey) -> the base-plane datum (the absolute heights, not the relative ones). Both readings also carry a known dispute from the earlier readers about the far-west geometry (which side-lot-line portion lies beyond 100 ft), held not known on the settled sheet. None is replaced by a default.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q7 (adjoining lot-line types; neighbouring street walls; ground elevations; the far-west geometry) and return-independent-hand-calculation-14.md Q7 (the same facts, each with the variant it selects). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It names the missing facts and what each selects; it fills none with a default and settles no variant. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### settled-answer-contradicted - Whether either reader found a captured text to contradict a settled answer

Facts used:

- Both readings' Q7 check of the settled answers = both readings report NONE (source: return-independent-hand-calculation-13.md Q7 and return-independent-hand-calculation-14.md Q7)

Law relied on:

- ZR 12-10 (Definitions - floor area ratio) - captured.
  - Capture: snapshot `zr-12-10-floor-area-ratio`, file `docs/research/zr-snapshots/v1/zr-12-10-floor-area-ratio.snapshot.json`.
  - Content digest: `11e7a3dc9f57ba1718ec5edfebb7aeb0fa6e61698228f70a170c1649d354c8d4`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "is the total #floor area# on a #zoning lot#, divided by the #lot area# of that #zoning lot#"

Why the rule applies: Each reading was given 34 earlier answers as settled and each checked, in its Q7, whether any text it opened contradicted a settled answer. Both report none: every text each opened agreed with the settled answers it relied on.

Expected value: Neither reader found a captured text to contradict a settled answer. Both readings report NONE in their Q7: every text each opened (for example the floor-area-ratio definition, the R6B heights, the corner/interior coverage split, the dwelling-unit factor and the street-wall sections) agreed with the settled answers it relied on.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q7 (settled answers a text contradicted: NONE) and return-independent-hand-calculation-14.md Q7 (NONE; every text opened agrees with the settled answers). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It records that no settled answer was contradicted; it re-works no settled answer. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

### six-steps-closing - The closing row: every step on which the two readings differ, and every missing fact, with its kind and what would settle it

Facts used:

- Zoning district / overlay = R6B with a C2-2 overlay (source: NYC PLUTO row for BBL 4073340070, fields zonedist1 and overlay1)
- Lot type = corner (Northern Boulevard and 215 Place, meeting at about 89.7 degrees) (source: cases/real-lot.json row L9 (settled sheet))
- Recorded lot area / maximum floor area = lot area 10,075 sq ft; maximum floor area 20,150 sq ft (source: cases/real-lot.json row L1 (settled sheet))
- Measured outline area = 10,387.99 sq ft (both readings' shoelace of the recorded outline) (source: return-independent-hand-calculation-13.md Q4b and return-independent-hand-calculation-14.md Q4b)

Law relied on:

- ZR 12-10 (Definitions - corner lot (the corner-lot portion)) - captured.
  - Capture: snapshot `zr-12-10-lot-corner`, file `docs/research/zr-snapshots/v1/zr-12-10-lot-corner.snapshot.json`.
  - Content digest: `86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58`.
  - Official page: https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10.
  - Quoted: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."

Why the rule applies: For the six-step comparison the owner asked for (property inputs; footprint; each floor's area and height; total floor area; legal unit limit; the separate preliminary estimate), this row collects the steps where the two readings differ and the missing facts, each with its kind.

Expected value: Steps on which the two readings DIFFER (both figures are held, named, in the rows above; no single figure): (a) the real lot's footprint - the corner-lot portion (reading 13 9,997.60 sq ft, reading 14 9,997.46), the interior strip (reading 13 390.39, reading 14 390.52) and the footprint the portions allow (reading 13 10,309.91, reading 14 10,309.88); KIND: each reader's own measurement of the recorded outline, which a surveyed outline would settle; this flows into building A's one-storey floor area and its estimate, which the readings hold as both figures. (b) which side-lot-line portion lies beyond 100 ft of a street line (the far-west geometry), a dispute carried from the earlier readers; KIND: each reader's own measurement, settled by a surveyed outline. MISSING FACTS (each a missing fact about the property): the adjoining zoning lots' lot-line types (selects the rear yard beyond the corner; from a survey, a deed or a record of the neighbouring lots); the neighbouring buildings' street walls (whether a prevailing street wall frontage exists; from a record of the neighbouring buildings); and the ground elevations (the base-plane datum; from a survey). All six steps are present as rows for each lot and each building (property inputs; footprint; each storey's area and height; total floor area; the legal unit limit as a separate row; the preliminary estimate as a separate row); the readings agree on every step not listed here.

Where this stands in the independent reading: return-independent-hand-calculation-13.md Q7 and Q8 (the differences and missing facts) and return-independent-hand-calculation-14.md Q7 and Q8 (the same differences and missing facts). Both readings reach this on the same basis (both readings: return-independent-hand-calculation-13.md and return-independent-hand-calculation-14.md).

What this row does not establish: It collects the differences and missing facts for a later comparison; it settles none of them and enters no human verdict. A draft reading by AI helpers, not professionally reviewed; it says nothing complies.

## What this case does not establish

- It records a value or a yes/no only where both readings agree on the same basis; where they differ, where one holds an answer subject to a text or a fact the readers did not have, or where neither settles a point, the row says so and names both readings.
- Both worked buildings are a plain stack (every storey the same plan): this is the method of the example given in the readers' brief, an assumption, not a rule of law, not a decision of the owner and not a recommendation of what to build. Both stay at or below the maximum base height, so no storey above the base is counted and no setback is worked.
- The floor-to-floor height of 10 ft, the share range 0.60 to 0.75 and the apartment size of 700 sq ft are starting assumptions chosen by the owner, not validated, not measured and not law; the apartment size and the share range carry the label 'preliminary assumption' wherever they appear. The estimate's figures are arithmetic on those assumptions, kept in rows of their own, apart from every legal limit, and never rounded to a whole-number count.
- The made-up lot describes no real property; the example checks a method. For the real lot the footprint and building A's floor area differ between the two readings and under the rear-yard variant, so no single figure is entered; the rear yard beyond the corner, the base-plane datum and the prevailing frontage stay not known.
- It is not a professional or legal determination and does not say anything complies; no human verdict is entered anywhere.

## Sources

- The step-P6 reading 1: provenance/return-independent-hand-calculation-13.md
- The step-P6 reading 2: provenance/return-independent-hand-calculation-14.md
- The sealed folder given to each helper: all 185 pinned law-text captures (without the notes describing how the program encoded them), the benchmark lot's recorded official facts and outline, one made-up interior lot of 100 ft by 100 ft, 34 answers settled by earlier readings (copied word for word from the reference cases and given as settled) and three starting values chosen by the owner (marked as assumptions), with no program access.
- The law captures under docs/research/zr-snapshots/v1/, each pinned by its content digest.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-10-09 | Case created (step P6, task M4-T037) from the two independent readings of the step-P6 sealed folder (provenance/return-independent-hand-calculation-13.md and -14.md): one hand-worked example of a first building option. A value is recorded only where both readings agree on the same basis. The row real-building-a and real-building-b give the current worked example of a building option for the real lot, which supersedes cases/real-lot.json row L15 (building option, floor plates, floors), whose not-known rested on there being no independent worked example. | rules-engineer (M4-T037) |

