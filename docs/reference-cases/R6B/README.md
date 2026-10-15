# R6B reference cases

These are worked examples of the R6B zoning limits, kept in their own files, apart from any program
output. They exist so that later tests of the program can take their expected values from a case file
and never from a program run. This is step R0 of the R6B results work order
(`docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md`).

## What a reference case is, and what it is worth

Each case was prepared by an AI helper that took no part in writing the program's rules. The helper
worked only from a sealed folder: pinned law-text captures and the lot's recorded official facts, with
no access to the program. Each case was then recomputed by a second AI, independently, from the same
sealed folder.

That agreement, between two AI answers, is not on its own proof of anything. Each case is written so a
person can follow it with the law text and a calculator: every value gives the facts it used and where
they came from, the law quoted with its capture, why the rule applies, the arithmetic step by step, and
the expected value. Every case is a draft reading of the law. It is **not professionally reviewed** and
it is not a statement that any lot complies with anything.

Nothing in a case comes from a program run: not a value, not a column, not a sentence. The work order's
"Program today" and "First screen" columns stay in the work order.

## The cases

| File | What it covers |
|---|---|
| `cases/real-lot.json` + `real-lot.md` | The real lot, 215-16 Northern Boulevard, Queens (BBL 4073340070): floor area, heights, coverage, units, lot type, frontages, street widths, rear yard and setback (work order table A, rows L1 to L15). |
| `cases/interior-lots.json` + `interior-lots.md` | Four made-up interior lots, chosen to show the floor-area arithmetic and the dwelling-unit rounding threshold, plus the interior-lot coverage reading (table B: P1, P3, P4, P5 and the interior-coverage reading). |
| `cases/corner-reach.json` + `corner-reach.md` | How far a corner lot reaches from each street line and from the corner point: the real lot and three made-up rectangles C1, C2 and C3 (table C). |
| `cases/suffix.json` + `suffix.md` | Whether the sections that list the R6 group reach the suffixed R6B district, through ZR 11-25 (table D: ZR 23-362, 23-52, 23-344, and ZR 23-22 and 23-432 which list R6B directly). |
| `cases/step-p1-worked.json` + `step-p1-worked.md` | The rows worked from the step-P1 captures (task M4-T027): the ZR 12-10 corner, interior, through and lot-area definitions, special density areas, ZR 23-342 and ZR 23-363. It covers three made-up corner lots (100 by 100, 150 by 100, 200 by 120), a 40-by-100 interior lot, a 40-by-200 through lot, and special density areas (section 5 gaps K1, K2, K4, K11). |
| `cases/overlay-reading.json` + `overlay-reading.md` | The commercial-overlay reading worked from the step-P2 captures (task M4-T028): for the benchmark lot with its C2-2 overlay beside the same lot without the overlay, which district's bulk governs and by what route, floor area ratio, lot coverage, dwelling units, base and building heights, the setback, street-wall location, rear yard, which paragraphs of ZR 34-111, 34-24, 35-632 and 35-631 apply, what ZR 35-633 adds, and the sections and defined terms the overlay texts point to that are not captured (section 5 gap K9). |
| `cases/step-p3-worked.json` + `step-p3-worked.md` | The readings worked from the law text captured by task M4-T029 and read independently in step P3 (task M4-T030): the ZR 12-10 lot-line, lot-width and lot-depth definitions for the real lot and a made-up interior lot; the rear yard beyond the corner (the real lot and a made-up 150-by-100 corner lot), the interior lot (ZR 23-342) and the through lot (the rear-yard equivalent of ZR 23-343); ZR 23-436 and ZR 35-633 for the real lot; ZR 34-21 and ZR 34-111 versus ZR 34-112; the Manhattan Core and the Special Downtown Brooklyn District; from what level heights are measured and the base plane; ZR 23-434 and the different maximum of ZR 23-362(b); the definition of "residence, or residential"; and the base of the floor-area shares in ZR 23-231 and ZR 23-232 (section 8; backlog row DB-170 item (a)). |
| `cases/step-p4-worked.json` + `step-p4-worked.md` | The readings worked from the law text captured by task M4-T031 and read independently in step P4 (task M4-T032): ZR 34-22 and its sections 34-221 to 34-224, and ZR 34-23 and its sections 34-231 to 34-233, for a residential building in a C2-2 district mapped within R6B; with those read, whether the floor area ratio, the lot coverage and the rear yard are the same as plain R6B, and whether any captured overlay text speaks of lot coverage; ZR 35-22 and ZR 35-62, 35-63, 35-641, 35-642 and 35-643; the definitions of a mixed building, lot coverage, the five yards and the street wall, curb level and prevailing street wall frontage; what may stand in a required rear yard; large sites and qualifying residential sites; whether ZR 34-111's exceptions reach C2-2 within R6B; dwelling units and qualifying housing and the ZR 23-52 factors, with a worked unit count for a made-up 100-by-100 lot; and ZR 23-441, 23-442 and 23-443 (section 8; backlog row DB-170 item (a)). |
| `cases/step-p5-worked.json` + `step-p5-worked.md` | The readings worked from the 46 texts captured by tasks M4-T033 and M4-T034 and read independently in step P5 (task M4-T035): the mixed-building floor-area sections ZR 35-30 to 35-33 (with ZR 35-31's shared-floor-area rule) and the floor-area-ratio definition, worked for a made-up mixed building of shops below standard residences; ZR 23-24 and the ZR 34-23 page (ZR 34-231 to 34-233); the ZR 12-10 definitions of a fully electrified building, an ultra-low-energy building, a building and a story; the fourteen parking, loading-berth and bicycle-parking sections and what each of seven development options' parking, loading and bicycle line may say; and the benchmark lot's rear yard read from ZR 23-342 and ZR 23-344 (backlog rows DB-184 first piece and DB-185 (b)). |
| `cases/step-p6-worked.json` + `step-p6-worked.md` | One independent hand-worked example of a first building option in R6B, read independently in step P6 (task M4-T037): whether a building may be lower than the minimum base height (ZR 23-431, 23-432, 23-436 and ZR 35-631 to 35-633); a footprint and floors worked by hand for a made-up interior lot of 100 by 100 ft and for the recorded corner lot (the lot coverage by portion; the rear-yard, street-wall and ground-elevation variants where a property fact is missing); what a floor schedule must list; and the arithmetic of the preliminary apartment estimate on the owner's starting values, kept apart from the legal dwelling-unit ceiling. Both worked buildings are a plain stack, every storey the same plan - the method of the example, an assumption, not a rule of law and not a recommendation. |
| `cases/short-block-rear-yard.json` + `short-block-rear-yard.md` | The two independent readings of ZR 23-344(b) (the short dimension of a block) and 23-344(c)(3), read independently in step P7 (task M5-T176): what 23-344(b) measures and whether "less than 230 feet" is strict and how "within 100 feet of such street line" is measured; 23-344(c) and (c)(3); how ZR 23-342, 23-343 and 23-344(a)/(b)/(c) fit together; ten made-up boundary cases M1 to M10; and the real lot (215-16 Northern Boulevard, lot 70 of block 7334) under Z1 (lot 70 alone) and Z2 (lots 70 and 1 together) on each measurement basis, with the bounding streets, their widths and the ALLEY. A value or yes/no is recorded only where both readings agree on the same basis; every disagreement, every not-known reading and the measurement basis the captured text does not fix stay not settled; no unconditional "no rear yard" is recorded for the real lot. |
| `cases/placement-building-b.json` + `placement-building-b.md` | The two independent readings of where the three-storey Building B (20,150 sq ft zoning floor area, 10-ft floor-to-floor) sits on lot 70 of block 7334 (215-16 Northern Boulevard, Queens) under Z1 (lot 70 alone) and how its floor area divides, read independently in step P8 (task M5-T177): the plate as zoning floor area per storey (20,150 / 3 = 6,716.67; no gross-up, exclusions or wall-thickness conversion worked, the physical floor plate not checked); the footprint on the printed-tax-map basis (100.76 x 66.66 = 6,716.66) reconciled with the plate within the readers' +/- 0.5 sq ft; the placement and the offsets to each lot line on that basis, with the city-map (GIS) outline used only as a conflict check; the lot coverage (maximum by portion) and the rear yard as far as both readings take them; and the area allocation at the one stated 60 percent apartment-area share (apartment 12,090 / other 8,060 of 20,150; 4,030 / 2,686.67 per storey). A value or figure is recorded only where both readings agree on the same basis; every disagreement or unresolved basis stays not settled with the kind of its gap; the placement is an illustration, not a design, and no human verdict is entered. |
| `cases/benchmark-options-2-3-6-7.json` + `benchmark-options-2-3-6-7.md` | The agreed worked values of four of the eleven development options for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner), read independently twice per option and confirmed by an independent comparer (task M5-T184): option 2 (qualifying affordable housing, incl. the Universal Affordability Preference), option 3 (qualifying senior housing), option 6 (residences with a community facility) and option 7 (a community facility alone). It records option 2's maximum residential floor area 24,180 sq ft (2.40 x 10,075), the 4,030 sq ft of affordable floor area a UAP development needs to reach 2.40, heights 30/45/65 ft and 35 dwelling units; option 3's 24,180 sq ft, 30/45/65 ft and the removal of the 680 dwelling-unit factor; and options 6 and 7's community-facility FAR 2.00 / 20,150 sq ft, the agreed corner-lot coverage of 80 percent (the interior/through rate and the whole-lot footprint stay not settled, since the lot spans a corner portion and a strip beyond the 100-foot corner reach), heights 30/45/55 ft, and the front/side/rear-yard and combination rules. A value or figure is recorded only where both readings of that option agree on the same value and the same basis, confirmed by the comparer, and the cited section is captured in `docs/research/zr-snapshots/v1`; every disagreement, unresolved basis, eligibility and missing fact stays not known with the kind of its gap. No row decides eligibility (qualifying affordable or senior housing, or community-facility use permission); every option-2 and option-3 figure is worked on the assumption that the building qualifies. Options 5, 8 and 9-10 rest on sections not yet captured and are named as owed (capture task M3-T010). |
| `cases/benchmark-options-5-8-9-10.json` + `benchmark-options-5-8-9-10.md` | The agreed worked values of four more of the eleven development options for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner), read independently twice per option family and confirmed by the same independent comparer as `benchmark-options-2-3-6-7` (task M5-T185): option 5 (ground-floor shops with residences above), option 8 (two buildings on one lot / a divided lot - both meanings) and options 9-10 (shared housing; parking and the transit zone). It records option 5's commercial FAR 2.00 (33-121) and residential FAR 2.00/2.40 (23-22), the combined greatest-single-use cap of 2.00 / 20,150 sq ft (35-31), the 29-unit all-residential baseline, heights 30/45/55 ft and the Use Group VI retail; option 8 meaning A's shared 20,150 sq ft / 29 units with no gain and the 40-foot separation between unconnected buildings (23-371), and meaning B's 10,075 sq ft per half / 20,150 total with 15 units per half, subdivision recorded as a legal act (12-10); and options 9-10's residential FAR 2.00 / 20,150 sq ft, the 680 dwelling-unit factor read as not applying to rooming units (23-51, a draft), Outer Transit Zone parking of zero for rooming units (25-221), and the unchanged 30/45/55 ft envelope. A value or figure is recorded only where both readings of that option family agree on the same value and the same basis, confirmed by the comparer, and the cited section is captured in `docs/research/zr-snapshots/v1` (the 20 captured by task M3-T010 plus the earlier captures); the storey limit (one reading only), the commercial rear yard, the aggregate +1 unit of meaning B, whether the 23-12 minimum binds the halves (one reading only) and the rooming-versus-dwelling classification stay not known with the kind of each gap. No row decides eligibility or use permission, and neither meaning of option 8 (owner question N1) nor option 10 (owner question N2) is decided; options 4 and 11 are named as owed. |

Each case is kept twice from one source: a structured data file under `cases/` that a test can load, and
a page rendered from it that a person can read. The helper returns are kept unchanged under
`provenance/`: the two first-round returns, the two step-P1 readings, the two step-P2
commercial-overlay readings, the two step-P3 readings, the two step-P4 readings, the two step-P5
readings, the two step-P6 readings, the two step-P7 readings, the two step-P8 readings, and the six
step-P9 option readings (two each for options 2, 3 and 6-7) with the independent comparer. The
step-P9 readers worked from a detached, read-only checkout of the repository at commit bb5c02b9 - the
pinned law captures, the settled reference cases, the evidence records and the law library - reading
no program output; some read official Zoning Resolution pages live. This was not a sealed folder in
the step-P7/P8 sense.

## Law text: what steps P1 and P2 captured, and what the readers did not have

**Step P1** (task M4-T025) captured the law text these cases waited for, and task M4-T027 worked the
rows from it (see `cases/step-p1-worked.json`): the ZR 12-10 definitions of a corner, interior and
through lot and of lot area; the ZR 12-10 definition of special density areas; **ZR 23-342** (rear
yard requirements); and **ZR 23-363** (special coverage rules for some interior and through lots). The
rows that were "not known" for want of that text now cite the captured snapshots.

**Step P2** (task M4-T026) captured the eight commercial-overlay sections - **ZR 34-11**, **ZR
34-111**, **ZR 34-24**, **ZR 35-53**, **ZR 35-63**, **ZR 35-631**, **ZR 35-632** and **ZR 35-633** -
and task M4-T028 worked the overlay reading from them (see `cases/overlay-reading.json`). Both readings
find the C2-2 overlay changes only the street-wall location rule (from the R6B line-up of ZR 23-431(a)
to the percentage rule of ZR 35-631(b)) and leaves the floor area ratio, lot coverage, dwelling units,
base and building heights, the setback and the all-residential rear yard the same as plain R6B.

The list below is the law text the readers did NOT have when they made these readings (on 2026-10-06
and 2026-10-07). Wherever a case file says a text is "not captured" or "uncaptured", it means exactly
that: it was not captured when that reading was made, so the readers did not have it. A text on the
list may be captured later without having been read for these cases; `docs/research/zr-snapshots/v1/`
shows what is captured now. Capturing a text changes no row on its own: a row changes only when two
independent readings of the new text are made, under the rule in the next section. These cases name
each such item and record the affected value as "not known" where the text is needed for a number:

- **ZR 23-343** (rear yard equivalent requirements) - the rear yard for a through lot.
- **ZR 23-434** (eligible sites) - the 65/50-percent lot-coverage branch of ZR 23-362(b).
- The **ZR 12-10** definitions of *front lot line*, *rear lot line*, *side lot line* and *lot width* -
  needed to identify a rear lot line and to set a rear-yard depth.
- The geographic **boundary definitions** of the *Manhattan Core* and the *Special Downtown Brooklyn
  District* - needed to place a lot in or out of a special density area.
- The **base plane** and height-measurement rule for R6 through R12 districts.
- The sections the **step P2** overlay readings point to that the readers did not have: **ZR 34-21**,
  **ZR 34-22** and **ZR 34-23** (exceptions to applicability of Residence District controls, pointed
  to by ZR 34-11); **ZR 36-64** (special-area height and setback); **ZR 35-71** (the optional
  sky-exposure-plane envelope); **ZR 35-64** (additional height and setback); **ZR 23-435** (towers);
  and **ZR 23-436** (the additional height and setback regulations that ZR 35-633 brings in) - so what
  ZR 35-633 adds stays "not known". Also not among what the readers had: **ZR 23-41** (permitted obstructions, inside
  the mixed-building rule of ZR 35-53) and the defined terms *Manhattan Core*, *mixed building* and
  *prevailing street wall frontage*.

**Step P3** (task M4-T029) captured the law text the earlier readings waited for (27 texts), and task
M4-T030 read it independently (see `cases/step-p3-worked.json`). The step-P3 readers had, among the
newly captured text: the **ZR 12-10** definitions of a *front*, *rear* and *side lot line*, *lot
width*, *lot depth*, *street line* and *zoning lot*; **ZR 23-343** (the through-lot rear-yard
equivalent); **ZR 23-436** and the way **ZR 35-633** brings it in; **ZR 34-21** and **ZR 34-112**; the
**Manhattan Core** and **Special Downtown Brooklyn District** definitions; the **base plane**; **ZR
23-434** (eligible sites); and the definition of *residence, or residential*. With that text the
step-P3 rows settle the lot lines and lot depth of the real lot, the interior lot's width, depth and
rear yard, the through lot's rear-yard equivalent, which paragraph of ZR 23-436 binds a new building on
the real lot, ZR 35-633(a), ZR 34-21's routing, ZR 34-111 over ZR 34-112, the Manhattan Core (not in
it), from what level heights are measured, and the ZR 23-434 and ZR 23-362(b) scope; others stay not
known (the real lot's lot width and its rear yard beyond the corner, the base-plane elevation, ZR
35-633(b)). The step-P3 readings' passing remark that the standard coverage for this corner lot is 100
percent did not work the corner-lot-portion rule and is **not** a reading of whole-lot coverage, so the
coverage rows (real-lot L5, corner-reach real-lot-coverage, and the corner-coverage rows of
step-p1-worked) are unchanged.

From both step-P3 readings' own summary of what they still did not have, the step-P3 readers lacked (an
item is on this list only where BOTH readings name it): **ZR 34-22** (modification of floor area) and
**ZR 34-23** (modification of yards), both named by ZR 34-21; **Article X, Chapter 1** (the Special
Downtown Brooklyn District regulations); and the defined terms *large sites*,
*transportation-infrastructure-adjacent frontage*, *residential floor area*, *short dimension of a
block*, *curb level*, *street wall line level*, *rear wall line level*, and the qualifying-housing terms
(*qualifying affordable housing*, *qualifying senior housing*, *UAP developments*, *Mandatory
Inclusionary Housing areas*, *residential equivalent*) that select the ZR 23-432 height columns. They
also did not have the adjoining zoning lots' lot-line types (needed for the rear yard beyond the corner)
or the site's elevation and grade data (needed for the base plane). The two readings differ on a few
pointers, so those are recorded as differences, not as the agreed list: reading 8 names **ZR 23-34**
(inclusive) and further defined terms; reading 7 names **ZR 23-44** (inclusive) and **ZR 23-341** /
**23-311** / **23-312**. Reading 8 records that ZR 35-62, **35-64**, **35-71** and **36-64** were in the
readers' folder (both had them; reading 7 did not read some of them), so they are NOT on the step-P3
"did not have" list; the exact height and setback numbers stay not known for the undefined
qualifying-housing terms above. As before, a text the readers did not have may be captured later;
`docs/research/zr-snapshots/v1/` shows what is captured now.

**Step P4** (task M4-T031) captured the law text the overlay and earlier readings waited for (38
texts), and task M4-T032 read it independently (see `cases/step-p4-worked.json`). The step-P4 readers
had, among the newly captured text: **ZR 34-22** and its sections **34-221** to **34-224**, and **ZR
34-23** and its sections **34-231** to **34-233** (the floor-area and yard modifications the step-P2
and step-P3 readers did not have); **ZR 35-22** and **ZR 35-62**, **35-63**, **35-641**, **35-642** and
**35-643**; **ZR 23-44** and **ZR 23-441**, **23-442** and **23-443**; **ZR 23-341**, **23-311** and
**23-312** (permitted obstructions); and the **ZR 12-10** definitions of a *mixed building*, *lot
coverage*, the five *yards*, a *street wall*, *curb level*, a *prevailing street wall frontage*, a
*large site*, a *qualifying residential site*, a *dwelling unit*, *qualifying affordable housing*,
*qualifying senior housing* and *special density areas*. With that text the step-P4 rows settle that
none of ZR 34-22 or 34-23 changes the floor area ratio, the lot coverage or the rear yard from plain
R6B (so the three overlay-reading rows held subject to ZR 34-21 through 34-23 are superseded by the
step-P4 rows), that no captured overlay text speaks of lot coverage, that of the Chapter-5 sections
only ZR 35-63 reaches an all-residential building (height and setback), that neither ZR 34-111
exception reaches C2-2 within R6B, that neither the real lot nor the made-up 100-by-100 lot is a large
site and that a C2-2-in-R6B lot is not a qualifying residential site, and the ZR 23-52 dwelling-unit
factors (680 standard, 680 qualifying affordable, none for qualifying senior), with a conditional
worked count of 29 units for the made-up 100-by-100 lot.

From both step-P4 readings' own summary of what they still did not have, the step-P4 readers lacked (an
item is on this list only where BOTH readings name it): the definition of *floor area ratio* (needed to
turn a ratio into a square-foot floor area, so the made-up lot's count is held conditional on it); the
R6 or R6B *front-yard* and *side-yard* requirement sections (so whether the overlay's removal of the
front and side yard changes plain R6B is not known); the defined term
*transportation-infrastructure-adjacent frontage*; **Section 23-381**; **Section 23-62**; the *Greater
Transit Zone* and *Outer Transit Zone* definitions (both note these are moot for the R6B reading); and
the neighbouring buildings' street-wall data, the mapped street lines and any adjacent-district
boundary for the real lot (so whether the lot has a prevailing street wall frontage, and whether ZR
23-443(a), (b) or (d) reach it, stay not known); and the Chapter-5 scope or heading section (named by
reading 9 in its Q4 and reading 10 in its list), needed to say whether ZR 35-22 or ZR 34-111 formally
governs an all-residential building. The two readings differ on some pointers, so those are
recorded as differences, not as the agreed list: reading 9 names that the full ZR 34-23 sub-section
list is not confirmed by the folder and the defined terms *Limited Height District*, *aggregate width
of street walls*, *block* and *short dimension of a block*; reading 10 names the defined terms
*multiple dwelling residence*, *height factor* and *open space*. Most
other texts the readings point to (including ZR 34-22 and 34-23 and all the definitions above) were in
the step-P4 folder - all 110 pinned captures were - so they are NOT on the step-P4 "did not have" list;
each reading also lists, separately, the texts that were in its folder and that it chose not to read.

**Step P5** (tasks M4-T033 and M4-T034) captured the 46 texts the mixed-building, energy and
parking readings waited for, and task M4-T035 read them independently (see `cases/step-p5-worked.json`).
The step-P5 readers had, among the newly captured text: the mixed-building floor-area sections **ZR
35-30**, **35-31**, **35-32** and **35-33** (with ZR 35-31's shared-floor-area rule) and the **ZR
12-10** definition of *floor area ratio*; the **ZR 12-10** energy definitions *fully electrified
building* and *ultra-low-energy building* with *building* and *story*; **ZR 23-24** and the **ZR 34-23**
contents (ZR 34-231 to 34-233); the fourteen parking, loading-berth and bicycle-parking sections (**ZR
25-02**, **25-20**, **25-211**, **25-221**, **25-231**, **25-80**, **25-81**, **25-811**, **36-21**,
**36-31**, **36-62**, **36-70**, **36-71**, **36-711**); and **ZR 23-342** and **ZR 23-344** for the
benchmark lot's rear yard. With that text the step-P5 rows settle that ZR 35-31 governs the made-up
mixed building's floor area (not ZR 35-32 or 35-33), how the use floor areas combine and how the 400
shared square feet split, the residential floor area ratio and floor area (2.00 and 20,000 square
feet), that the ZR 34-23 page carries only the front-yard, side-yard and change-of-use subsections
(none a rear yard, with the ZR 34-23 contents capture now read as the complete list - which supersedes
the step-P4 row zr-34-23-sections), the two energy definitions and the 5-percent floor-area exclusion,
and that within 100 feet of the benchmark lot's roughly 89.7-degree corner no rear yard is required.

From both step-P5 readings' own summary of what they still did not have, the step-P5 readers lacked (an
item is on this list only where BOTH readings name it): **Article III, Chapter 3** (the commercial-
district maximum floor area ratio, e.g. ZR 33-12 / 33-121 - so the made-up building's commercial floor
area ratio and whole-building maximum stay not known); the **ZR 23-24 subsections** (ZR 23-241 and
following - so ZR 23-24's reach stays not known); **ZR 25-222** and **ZR 25-232** (the dwelling-unit
parking numbers - so the residential parking counts stay not known); the **Use Group tables** (so the
commercial and community-facility parking, loading and bicycle rates stay not known); the parking
waivers **ZR 36-23**, **36-24** and **36-25**; **Section 66-11**, **APPENDIX I** and the **ZoLa**
boundary (so the transit zone cannot be confirmed from the law); and **Local Law 154 of 2021** with the
New York City Energy Conservation Code and Building Code (so the energy requirements' substance stays
not known). As facts, not law, both readers also lacked the adjoining zoning lots' lot-line types (so
the benchmark lot's rear yard beyond the corner stays not known) and the block's bounding dimensions.
Each reading also lists, separately, the folder texts it chose not to read: reading 11 did not read the
ZR 12-10 lot-coverage capture (not needed for the rear-yard question), and reading 12 read every capture
each question named. A text the readers did not have may be captured later; `docs/research/zr-snapshots/v1/`
shows what is captured now.

**Step P6** (task M4-T037) is one independent hand-worked example of a first building option, read
independently by two AI helpers (readings 13 and 14) working alone from a sealed folder of all 185 pinned
law captures without their notes, the benchmark lot's recorded facts and outline, one made-up interior
lot of 100 by 100 ft in plain R6B, and three starting values chosen by the owner (the 10-ft
floor-to-floor height, the 0.60-to-0.75 share range and the 700-square-foot apartment size, marked as
assumptions). The step-P6 readers were **given 34 earlier answers as settled** - copied word for word
from the reference cases (the floor-area-ratio definition and the made-up floor area, the interior and
corner coverage, the R6B heights measured from the base plane, the dwelling-unit factor, the real lot's
floor area, heights, lot type, frontages, street widths, setback and reach, and the standing not-known
rows) - so completed readings are reused and not worked again. With that, the step-P6 rows settle, from
captured text, that a building wholly below the 30-ft minimum base height is permitted in plain R6B and
under a C2-2 overlay (ZR 23-436(e); the "whichever is less" of ZR 23-431(b) and 35-631(b)); they work
the yards, the widest footprint, the floor stack and the floor schedule for the made-up lot and the real
lot; and they keep the preliminary apartment estimate (arithmetic on the owner's starting values) apart
from the legal dwelling-unit ceiling. Both worked buildings are a plain stack, every storey the same plan
- the method of the example, an assumption, not a rule of law, not the owner's decision and not a
recommendation of what to build. The step-P6 example of a building option for the real lot supersedes
`cases/real-lot.json` row L15.

From both step-P6 readings' own summary of what they still did not have, the step-P6 readers lacked (an
item is on this list only where BOTH readings name it): the ZR 12-10 term **street wall line level** and
the adjoining final-grade / ground elevations the base-plane definition needs (so the real lot's
base-plane datum stays not known); **ZR 23-434** (eligible sites) and **ZR 23-435** (towers), neither
relied on; and the ZR 12-10 term **outer court** (affects only recess geometry, not the simple walls
worked). As facts, not law, both readers also lacked the adjoining zoning lots' lot-line types (so the
real lot's rear yard beyond the corner stays not known), the neighbouring buildings' street walls (so a
prevailing street wall frontage cannot be confirmed) and the ground elevations. The two readers measured
the recorded outline themselves and reached slightly different corner-portion and interior-strip areas,
so the real lot's whole-lot coverage, footprint and building A's one-storey floor area are held as both
figures, not smoothed. A text the readers did not have may be captured later; `docs/research/zr-snapshots/v1/`
shows what is captured now.

**Step P7** (task M5-T176) is the two independent readings of ZR 23-344(b) (the short dimension of a
block) and 23-344(c)(3), read independently by two AI helpers (readings 15 and 16) working alone from a
sealed folder of the 189 pinned law captures without their notes, the block-7334 lot outlines, the DCM
centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, and ten
made-up boundary cases M1 to M10. The step-P7 readers were **given four earlier answers as settled** -
copied word for word from the reference cases (used here for lot 70's lot lines, from
`cases/step-p3-worked.json`, and for lot 70's reach, from `cases/corner-reach.json`) - so completed
readings are reused and not worked again. With that, the step-P7 rows settle, from captured text, what
23-344(b) measures and that "less than 230 feet" is strict; which lots 23-344(c) reaches, what becomes a
rear lot line and that (c)(1) versus (c)(3) turns on the adjoining lot's lot-line kind plus the subject
lot's own district (not the neighbour's district); that a public park can bound a block and a private way
cannot; and that more than one 23-344 modification can apply to one lot and (b) is not barred on a corner
lot. They keep **not settled** the measurement basis for the short dimension, the method of measuring
"within 100 feet", the exact-100-ft edge, the method for a non-rectangular block, and the overlap of (b)
and (c), because the captured text does not fix them; and for the real lot they keep the rear-yard answer
conditional on the measurement basis, the zoning lot (Z1 vs Z2) and the neighbouring lots' records, so no
unconditional "no rear yard" is recorded.

From both step-P7 readings' own summary of what they still did not have, the step-P7 readers lacked, as
facts not law (an item is on this list only where BOTH readings name it): an authoritative measurement
basis - a survey - for the side-street separation; a zoning-lot description, deed or Declaration deciding
whether lots 70 and 1 are one zoning lot; the zoning and lot-line kinds of the other lots on the block;
and the status of the ALLEY and the SW-end bounding feature. Each reading also named outside-folder texts
of its own: reading 1 a "block frontage"/"frontage" definition; reading 2 a general "lot line"
definition, ZR 23-38 and ZR 23-72, and the full text of ZR 34-23. Reading 2 reads R6B as within "R6
through R12" and flags it a point a professional must confirm, because the captured 23-344 text does not
separately enumerate the letter-suffix districts (R6A/R6B); reading 1 reads R6B as within R6 through R12
without raising the point. ZR 11-25, which bears on whether R6B is within "R6 through R12", was in the
sealed folder and was not read by reading 1 or by reading 2. The two readers measured the block themselves and
reached different centreline separations (260.02 ft and about 261.0 ft, both above 230 ft), so the real
lot's short-dimension determination stays basis-dependent and not settled. A text the readers did not have
may be captured later; `docs/research/zr-snapshots/v1/` shows what is captured now.

**Step P8** (task M5-T177) is the two independent readings of where the three-storey Building B (20,150
sq ft zoning floor area, 10-ft floor-to-floor) sits on lot 70 of block 7334 under Z1 (lot 70 alone) and
how its floor area divides, read independently by two AI helpers (readings 17 and 18) working alone from a
sealed folder of the 189 pinned law captures without their notes, the block-7334 lot outlines, the DCM
centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, and the
stated facts of Building B and the stated measure. The step-P8 readers were **given eighteen earlier
answers as settled** - copied word for word from the reference cases (lot 70's lot lines and depth, its
reach, the yard, lot-coverage and street-wall definitions and readings, the R6B/overlay base-height and
street-wall readings, the lot-coverage-by-portion and recorded-vs-measured-area readings, and the step-P7
bounding-streets and Z1 rear-yard readings) - so completed readings are reused and not worked again; the
earlier footprint answer (`step-p6-worked#real-building-b`) was **left out on purpose**, so each reader
worked the footprint afresh. With that, the step-P8 rows settle, on the same basis for both readings, the
plate as zoning floor area per storey (20,150 / 3 = 6,716.67; no gross-up, exclusions or wall-thickness
conversion worked, the physical floor plate not checked), the footprint on the printed-tax-map basis
(100.76 x 66.66 = 6,716.66, 0.01 sq ft under the plate, within the readers' +/- 0.5 sq ft and never forced
into one figure), the placement and the offsets to each lot line under Z1 on that basis (it touches the
Northern Boulevard, 215 Place and lot-1 lines at 0 ft and clears the back side lot line by 33.34 ft), the
maximum lot coverage by portion (100 percent corner / 80 percent interior), and the area allocation at the
one stated 60 percent apartment-area share (apartment 12,090 / other 8,060 of 20,150; 4,030 / 2,686.67 per
storey). They keep **not settled**, each with the kind of its gap, the whole-lot lot coverage (read by
portion; the governing lot area conflicts - 10,075 recorded / 10,076 tax rectangle / 10,387.99 GIS), the
rear yard under Z1 (the measurement basis and the adjoining lot-line kind are unresolved; no unconditional
"no rear yard" is recorded), and the printed-tax-map/city-map (GIS) conflict (the city-map outline is used
only as a conflict check and the two bases are never mixed in one figure). The placement is an illustration
on the printed-tax-map basis, not a design and not a compliance finding; a tax lot is not a zoning lot.

From both step-P8 readings' Q7, there is no text that both readings say they did not have, so the joint
"did not have" list is empty: reading 2 names the *outer court* definition, the *Mandatory Inclusionary
Housing* and *UAP* terms and the New York City Administrative Code as not in its folder (each not
load-bearing for this flush-wall placement); reading 1 names no text as outside the folder and instead
marks **ZR 23-341**, **ZR 23-343** and **ZR 23-434** as in the folder but not read by reading 1, taking the
prevailing-street-wall-frontage definition from the settled sheet; the *short dimension of a block*
definition is in the folder and was not read by reading 1 for a quote. As facts, not law, both readers
lacked the same real-lot facts: no survey, deed or zoning-lot description for lot 70 or any neighbour (so
the adjoining zoning lot's lot-line kind for ZR 23-344(c) is not known and Z1 is a stated condition, not a
fact); a surveyed outline to resolve the about 313 sq ft area conflict; and the ground elevations, base
plane and curb level (nothing here turned on them, the building being below the base height). Reading 1
also records that whether a Commercial District is mapped along the entire 215 Place block frontage is not
known; reading 2 also records the surveyed corner angle and the block's south-west / ALLEY edge as not
known. A text the readers did not have may be captured later; `docs/research/zr-snapshots/v1/` shows what
is captured now.

## The rule for changing an expected value

An expected value in a case changes only with a recorded reason, written in the case's change log:

- **corrected evidence** (a recorded fact was wrong and is corrected);
- **a corrected reading** of the law text; or
- **a change in the law** itself.

A disagreement between a case and the program is never, on its own, a reason to change the case. It is
**investigated on both sides**: the case's reading and the program's reading are both examined, and the
side that is wrong is corrected for a recorded reason.

## How a test uses a case

A later test reads a row's expected value by its case id and row id through the loader in
`services/api/tests/rules/reference_cases/`. The checker and test there also recompute every arithmetic
step from the operands in the data file, compare each cited capture's digest with the live capture file,
confirm the quoted words are in the capture, and prove that no case file carries a program result. None
of that code imports the rule engine, the scenario engine or any program output.
