# Independent reading from the step-P6 sealed folder, reading 2 (provenance)

What this is: one of two independent readings made on 2026-10-09, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - all 185 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, one made-up interior lot of 100 ft by 100 ft in plain R6B with every fact stated, 34 answers settled by earlier readings (copied word for word from the reference cases and given as settled, so completed readings are reused and not worked again), and three starting values chosen by the owner (marked as assumptions) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2 of the step-P6 pair; a value is recorded in a step-P6 reference-case row only where this reading and reading 1 (return-independent-hand-calculation-13.md) give the same answer on the same basis.

---

PART 1 of 6

This is a DRAFT reading of captured New York City Zoning Resolution text by an AI reader. It is not legal advice and not a professional review. It gives no verdict that any building or lot complies with the law. I obeyed the one hard rule: I worked only from the sealed folder `.../scratchpad/sealed-p6`, opened nothing under `/root/project`, ran no web search and opened no web page, and wrote only in my own scratch folder.

FILES I READ (sealed-p6):
facts/: made_up_lot.json, starting_values_chosen_by_the_owner.json, settled_by_earlier_readings.json, lot_facts_pluto.json, lot_outline_epsg2263.json, streets_dcm_centerlines.json, zoning_nyzd_query_R6B.json, zoning_nyco_query_C2-2.json.
law/: zr-23-43, zr-23-431, zr-23-432, zr-23-433, zr-23-436, zr-35-62, zr-35-63, zr-35-631, zr-35-632, zr-35-633, zr-23-34, zr-23-322, zr-23-335, zr-23-342, zr-23-343, zr-23-344, zr-23-362, zr-23-363, zr-23-52, zr-23-22, zr-12-10-street-wall, zr-12-10-base-plane, zr-12-10-curb-level, zr-12-10-story, zr-12-10-building, zr-12-10-floor-area-ratio, zr-12-10-lot-coverage, zr-12-10-yard, zr-12-10-yard-front, zr-12-10-yard-side, zr-12-10-yard-rear, zr-12-10-prevailing-street-wall-frontage, zr-12-10-aggregate-width-of-street-walls, zr-12-10-lot-corner, zr-12-10-lot-interior, zr-12-10-lot-line-front, zr-12-10-lot-line-rear, zr-12-10-lot-line-side, zr-12-10-dwelling-unit. (Every law quote below carries its file name.)

Q1. MAY A BUILDING BE LOWER THAN THE MINIMUM BASE HEIGHT?

Q1a — R6B numbers and from where measured.
[C, zr-23-432 table, R6B row] minimum base height 30 ft; maximum base height 45 ft (standard residences); maximum height of buildings 55 ft (standard residences). The R6B row carries no footnote, so these do not vary by wide/narrow street.
[C, zr-23-43] "The height of all #buildings or other structures# shall be measured from the #base plane#." [S: settled "height-measured-from-base-plane"] confirms 23-432's heights are measured from the base plane.
[C, zr-12-10-base-plane] "The 'base plane' is a plane from which the height of a #building or other structure# is measured... For #buildings#... within 100 feet of a #street line#, the level of the #base plane# is any level between #curb level# and #street wall line level#."
What must happen at/above the maximum base height: [C, zr-23-432] "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided at a height not lower than the minimum base height or higher than the maximum base height in accordance with Section 23-433." [C, zr-23-433] that setback is "at least 10 feet... from any #street wall# fronting on a #wide street#, and ... at least 15 feet ... fronting on a #narrow street#."

Q1b — Is a building whose WHOLE height is below the minimum base height permitted?
(i) Plain R6B — YES. [C, zr-23-436] paragraph (e): "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights." A new building built below 30 ft is #developed# and does not exceed the minimum base height, so the minimum-base-height provision does not apply to it. Conditions it attaches: the building must be (1) #developed# or #enlarged#, and (2) not exceed the minimum base height. Two provisions speak to it and they AGREE: zr-23-432 states a minimum base height only as the floor of the setback/street-wall regime (not as a minimum building height), and zr-23-436(e) expressly disapplies that minimum to a below-minimum new building. [?] The term #developed# is not defined in the folder (pointer: 23-436(e) "#developed# or #enlarged#"); the ordinary reading (a newly built building is developed) supports the exemption, but the defined meaning is NOT KNOWN.
(ii) C2-2 overlay within R6B — YES. [C, zr-35-632] "(a) ... The minimum base height, maximum base height and maximum #building# height shall be as set forth in the table in Section 23-432 for the applicable #Residence District#." [C, zr-35-633] "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows: (a) references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631." So 23-436(e) still reaches the overlay building via 35-633; the same exemption applies. [C, zr-35-62] is NOT the applicable section (it governs Commercial Districts with R1–R5 equivalency; an R6B/C2-2-within-R6B site is R6-R12 equivalency, governed by 35-63). The two routes (23-432 via 35-632; 23-436(e) via 35-633) agree with the plain-R6B result.
[?] No captured section states a minimum building height or minimum number of storeys for standard residences; I found none in the texts read, so there is no least height beyond the (disapplied) minimum base height.

END OF PART 1

PART 2 of 6

Q1c — If permitted, what do the street-wall words then require?
Height the street wall must rise to: [C, zr-23-431(b)(1)] along wide streets "at least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less"; [C, zr-23-431(b)(2)] along narrow streets the same but "within 10 feet." So for a building below the minimum base height the street wall need only extend to the HEIGHT OF THE BUILDING ("whichever is less"), not to 30 ft. The same "whichever is less" clause appears in the overlay rule [C, zr-35-631(b)].
Where it must stand: horizontally, under R6B's line-up rule [C, zr-23-431(a)] the wall is located "no closer... nor further... than ... an existing adjacent #building#"; under the percentage rule [C, zr-23-431(b)] within 8 ft (wide) / 10 ft (narrow) of the street line for ≥70% of the aggregate width. [?] Which of (a)/(b) governs turns on whether a #prevailing street wall frontage# exists (block data), so the exact required horizontal location is NOT KNOWN without that.
Least height / least number of storeys: [?] none found — see Q1b.

Q1d — Does anything depend on wide vs narrow, for a building at/below the maximum base height?
[C, zr-23-432] the R6B base/building heights carry no wide/narrow footnote, so they do not change. [C, zr-23-433] the 10 ft (wide) / 15 ft (narrow) setback is triggered only "For portions of a #building# #street wall# that exceed the maximum base height" — a building at/below the maximum base height has no such portion, so the setback does not apply and its wide/narrow split does not bite. The dependency that DOES apply to the base portion is the street-wall horizontal location: [C, zr-23-431] "Such provisions shall apply to the portion of a #street wall# located below the maximum base height and before the required setback," and within that, (b)(1) wide = within 8 ft, (b)(2) narrow = within 10 ft, with recess limits of 10 ft (wide) vs 15 ft (narrow). So YES: for the below-max-base portion the street-wall location rule depends on wide vs narrow.

Q2. THE MADE-UP LOT (plain R6B interior lot, 100 ft × 100 ft, one 60-ft-wide street, level ground at curb level) — THE LIMITS.

Q2a — taken from the settled sheet:
[S, step-p5-worked#floor-area-ratio-made-up-100x100] maximum floor area ratio 2.00 and maximum residential floor area 2.00 × 10,000 = 20,000 sq ft.
[S, interior-lots#interior-coverage] maximum lot coverage of an interior lot 80 percent (= 8,000 sq ft of 10,000).
[S, real-lot#L3] (R6B standard-residence row) minimum base 30 ft, maximum base 45 ft, maximum building 55 ft; [S, step-p3-worked#height-measured-from-base-plane] measured from the base plane.
[F, made_up_lot] the lot and sidewalk are level at curb level, so [C, zr-12-10-base-plane] the base plane here is curb level (= ground); heights are measured from ground.
[S, step-p4-worked#dwelling-unit-factors] the dwelling-unit factor for standard residences is 680 (a fraction of three-quarters or more counts as one unit).

Q2b — worked from the text (what the sheet does not hold for this lot):
Front yard: [C, zr-23-322] "In the districts indicated, no #front yard# requirements shall apply." → no front yard required; depth n/a.
Side yards: [C, zr-23-335(b)] "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet." The building is multi-family standard residences (not single/two-family detached, so not (a)), so no side yard is required; any side open area provided must be ≥5 ft.
Rear yard (interior lot 100 ft wide, 100 ft deep): SAME as the settled 40-ft answer — 20 ft at/below 75 ft. [C, zr-23-342(a)(1)] "For #detached# and #zero lot line buildings#, for #buildings#... at or below a height of 75 feet... a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line#...; and for portions above 75 feet... 30 feet." [C, zr-23-342(a)(2)(ii)] "for #zoning lots# with a #lot width# of 40 feet or greater... at or below a height of 75 feet... not less than 20 feet... and ... above 75 feet... 30 feet." At a 100-ft width (≥40 ft) both the detached path and the semi-detached/attached path give 20 ft at/below 75 ft. [C, zr-23-342(b)] the shallow-lot reduction needs a lot "less than 95 feet deep"; depth is 100 ft (≥95), so it does not apply. → rear yard 20 ft. [S confirmation: step-p3-worked#interior-40x100-rear-yard gives the same 20 ft for the 40-ft lot.]
Street wall (where it must/may stand), given the neighbours: [C, zr-23-431(a)] R6B uses the line-up rule; "Eligible adjacent #buildings# shall be located within 15 feet of the #street line#, within 25 feet of the subject #building#, and have a height that exceeds 35 feet." [F, made_up_lot] each neighbour's street wall is on the street line (0 ft) for its full width and is 35 ft high. [C] 35 ft does NOT "exceed 35 feet", so the stated neighbours are NOT eligible adjacent buildings; the line-up bounds of (a) have no eligible building to fix them. [C, zr-23-431(a)] "However, where the #street wall# surrounding the subject #building# do not have a #prevailing street wall frontage#, the applicable ... regulations of paragraph (b) may be applied" — permissive. [?] Whether a #prevailing street wall frontage# exists needs block data beyond the two immediate neighbours (not in folder). So the REQUIRED street-wall location is NOT KNOWN; but with no eligible neighbour forbidding it, placing the wall on the street line is permissible (and front yard is not required), so the widest building may stand on the street line.

END OF PART 2

PART 3 of 6

Q2c — THE FOOTPRINT of Building A (made-up lot).
[C/A] Sides 100 ft (front, along the street line) × 80 ft (depth); area = 8,000 sq ft. Place: front edge on the street line (front lot line); the two side edges on the two side lot lines; the rear edge parallel to and 20 ft from the rear lot line.
Which limit binds each edge:
- Front edge (100 ft on the street line): no front yard required [zr-23-322]; the street wall may stand on the street line [Q2b]. Bound by the front lot line (street line).
- Each side edge (80 ft on a side lot line): no side yard required [zr-23-335(b)]. Bound by the side lot line.
- Rear edge (100 ft): bound by the 20-ft rear yard [zr-23-342]. Because 100 × 80 = 8,000 = 80% of 10,000, the lot-coverage maximum [zr-23-362(a)] also binds exactly at this edge.

Q3. THE MADE-UP LOT, THE TWO BUILDINGS.
[A] floor-to-floor = 10 ft; [A] every storey the same plan, one above the other; [A] every square foot of every floor counts as floor area.

Q3a — BUILDING A ("the widest"). Footprint 100 × 80 = 8,000 sq ft (Q2c).
Storey | f2f(ft) | top above base plane(ft) | plan(ft) | plan area(sq ft) | floor area(sq ft) | running total
1 | 10 | 10 | 100 × 80 | 8,000 | 8,000 | 8,000
2 | 10 | 20 | 100 × 80 | 8,000 | 8,000 | 16,000
[A] A 3rd storey would bring 24,000 > 20,000, so it is not added.
[C] Total floor area used 16,000 against the maximum 20,000; floor area left unused 4,000. Building height 20 ft; number of storeys 2. [C, zr-12-10-story] with no cellar these four—two floors are 2 stories. Lot coverage used 8,000/10,000 = 80% = the maximum (80%). Yards left: front 0 (none required), side 0 (none required), rear 20 ft (= the 20 ft required). Height 20 ft vs minimum base 30 ft: BELOW the minimum base height — by Q1b(i) this is permitted (zr-23-436(e)), and the street wall need extend only to the building height (20 ft) not 30 ft (zr-23-431(b) "whichever is less"). 20 ft < maximum base 45 ft and < maximum building 55 ft. No setback is called for (no portion exceeds the maximum base height).

Q3b — BUILDING B ("to the minimum base height"); the method calls for it because A (20 ft) is below the minimum base height (30 ft).
[A/C] Smallest number of 10-ft storeys whose top reaches ≥30 ft: 3 storeys (top 30 ft). Plan area = maximum floor area / storeys = 20,000 / 3 = 6,666.67 sq ft, so the whole 20,000 is used. One plan: 100 ft (full frontage, on the street line) × 66.67 ft deep = 6,666.67 sq ft.
Storey | f2f | top(ft) | plan(ft) | area | FA | total
1 | 10 | 10 | 100 × 66.67 | 6,666.67 | 6,666.67 | 6,666.67
2 | 10 | 20 | 100 × 66.67 | 6,666.67 | 6,666.67 | 13,333.33
3 | 10 | 30 | 100 × 66.67 | 6,666.67 | 6,666.67 | 20,000.00
[C] Total floor area 20,000 = maximum; unused 0. Height 30 ft = the minimum base height; ≤ maximum base 45; ≤ maximum building 55; no setback. Lot coverage 6,666.67/10,000 = 66.67% ≤ 80%. Rear yard left 100 − 66.67 = 33.33 ft ≥ 20 ft required; front 0; sides 0. It lies inside Building A's footprint (depth 66.67 ≤ 80, width 100 = 100). Street wall: full 100-ft width on the street line, so it meets the line-up words (on the line) and would meet the percentage words (100% within 8/10 ft), and extends to 30 ft = min(min base 30, height 30) [zr-23-431].

Q3c — WHAT A FLOOR SCHEDULE MUST LIST (only what my working needed), column → the limit it lets a reader check:
- Storey number → total number of storeys.
- Floor-to-floor height (ft) → the height build-up.
- Top of storey above the base plane (ft) → minimum base 30, maximum base 45, maximum building 55; where a setback is triggered.
- Plan dimensions / footprint (ft) → yards (front 23-322, side 23-335, rear 23-342) and street-wall location (23-431).
- Floor area of the storey (sq ft) → the per-floor contribution.
- Running total floor area (sq ft) → maximum floor area 20,000 (FAR 2.00, 23-22).
- Lot coverage (footprint ÷ lot area, %) → 80% maximum (23-362).
- Rear-yard depth left (ft) → 20 ft required (23-342).
- Front/side setback left (ft) → none required (23-322/23-335).
- Street-wall position and the height to which it rises → 23-431 (location; extend to min base height or building height, whichever is less).

END OF PART 3

PART 4 of 6

Q4. THE REAL LOT (BBL 4073340070; R6B with a C2-2 overlay) — THE LIMITS.

Q4a — taken from the settled sheet (naming each):
[S, overlay-reading#bulk-regulations] the R6B residential bulk regulations govern an all-residential building here (via ZR 34-11 and 34-111).
[S, real-lot#L1] maximum residential floor area 20,150 sq ft; [S, step-p4-worked#floor-area-ratio] maximum FAR 2.00, same as plain R6B.
[S, real-lot#L3 / overlay-reading#base-and-building-height] minimum base 30 ft, maximum base 45 ft, maximum building 55 ft (standard residences).
[S, real-lot#L13 / overlay-reading#setback-above-base] setback above the base: 10 ft on the wide street (Northern Boulevard), 15 ft on the narrow street (215 Place).
[S, real-lot#L9] lot type: corner. [S, step-p3-worked#real-lot-lot-lines] two front lot lines (Northern Boulevard and 215 Place edges), two side lot lines (the two interior edges), no rear lot line.
[S, real-lot#L10] frontages Northern Boulevard 103.9 ft; 215 Place 100.0 ft. [S, real-lot#L11] Northern Boulevard is wide (100 ft), 215 Place is narrow (60 ft); this does not change the R6B floor area or height.
[S, corner-reach#real-lot-reach] the lot reaches ≤99.97 ft from the Northern Boulevard line, ≤103.93 ft from the 215 Place line, ≤144.60 ft from the corner; the whole lot is within 100 ft of the Northern Boulevard line but not of the 215 Place line (a strip ~3.93 ft wide, ~390 sq ft, lies beyond) and not within 100 ft of the corner (~2,560 sq ft beyond).
[S, step-p5-worked#zr-34-23-page] no front yard required (ZR 34-231) and no side yard required (ZR 34-232; any side open area ≥5 ft).
[S, overlay-reading#street-wall-location + step-p3-worked#zr-23-436-paragraphs] the street-wall rule that applies is the percentage rule of ZR 35-631(b) (≥70% of the aggregate width within 8 ft of the street line), mandatory along the wide Northern Boulevard frontage (ZR 23-436(c), via 35-633(a)).
Not known (with reasons): [S, corner-reach#real-lot-coverage] whole-lot lot coverage has no single figure (per portion); [S, step-p5-worked#benchmark-rear-yard] the rear yard beyond the corner area (turns on adjoining lot-line types); [S, step-p3-worked#base-plane-real-lot] the base-plane elevation (ground elevations unknown); [S, step-p4-worked#real-lot-prevailing-frontage] whether a prevailing street wall frontage exists (no neighbouring-building data).

Q4b — LOT COVERAGE BY PORTION.
Words that divide the lot: [C, zr-12-10-lot-corner] "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable." [C, zr-23-362(a)] "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." [C, zr-12-10-lot-coverage worked example] mirrors this split (a 100×100 corner portion at 100% and a 100×100 interior portion at a lower percent).
My geometry (from lot_outline_epsg2263.json, EPSG:2263 US survey feet; shown): the ring has vertices P0(1048810.23,216310.44), P1(1048788.63,216408.05), P2(1048889.92,216431.10), P3(1048911.58,216333.50), P4(1048812.40,216310.93). Edge lengths: P0–P1 99.98, P1–P2 103.88 (= Northern Boulevard frontage), P2–P3 99.98 (= 215 Place frontage), P3–P4 101.71, P4–P0 2.22 ft (perimeter 407.76 = the served Shape__Length). The corner point is P2 (farthest vertex P0 is 144.60 ft away, matching the settled reach). Shoelace area = 10,387.99 sq ft. Perpendicular depth from the Northern Boulevard line (P1–P2) ≤ 99.97 ft (whole lot within 100 ft); from the 215 Place line (P2–P3) up to 103.93 ft.
Clipping the lot at 100 ft from the 215 Place line:
- Corner-lot portion (within 100 ft of BOTH street lines): sides are the 103.88-ft Northern Boulevard frontage, the ~99.98-ft 215 Place frontage, the clip line, and the inner side edges; area = 9,997.46 sq ft → at 100% = 9,997.46 sq ft of building.
- Remaining interior-lot portion (the ~3.93-ft-wide strip beyond 100 ft of the 215 Place line, along the west/south edges): area = 390.52 sq ft → at 80% = 312.42 sq ft of building.
- Total building the portions allow = 9,997.46 + 312.42 = 10,309.88 sq ft. (Sum of portions 10,387.99 = total, checks.)
Recorded lot area for floor area: PLUTO lotarea = 10,075 sq ft, giving the settled maximum floor area 20,150 = 2.00 × 10,075. My measured outline area 10,387.99 sq ft equals the served MapPLUTO Shape__Area (10,387.988) but exceeds the PLUTO lotarea by ~313 sq ft (~3.1%). I use 10,075 for floor area, as the settled sheet does, and note the ~313 sq ft discrepancy.

END OF PART 4

PART 5 of 6

Q4c — REAR YARD BEYOND THE CORNER AREA (not settled; I do not settle it).
[C, zr-23-344(a)] "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." [S, benchmark note] the two street lines meet at ~89.7° (≤135°), so within 100 ft of the corner point NO rear yard is required.
Beyond 100 ft of the corner point: [C, zr-23-344(c)] "for #interior# or #through lot# portions of #corner lots#... the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line#" and then (c)(1) "a #rear yard# shall be provided in accordance with Section 23-342... where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#"; (c)(3) "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#." Variants the words allow:
- V1: the deemed rear lot line coincides with an adjoining REAR lot line → a 20-ft rear yard (zr-23-342, at/below 75 ft) is required along that deemed rear lot line (the portion of a side lot line beyond 100 ft of the street line it intersects — the far-west sliver in the ~2,560 sq ft beyond the corner point). Selected by: the adjoining zoning lot presenting a rear lot line there.
- V2: it coincides with an adjoining SIDE lot line → NO rear yard (zr-23-344(c)(3)). Selected by: the adjoining zoning lot presenting a side lot line there.
[?] Which side-lot-line portion is actually beyond 100 ft of a street line is itself NOT KNOWN: the settled note records reader 11 finding small slivers on both non-street edges (west edge ~101 ft from the Northern Boulevard line) and reader 12 finding only the ~4-ft tip of the south edge beyond 100 ft of the 215 Place line. Depth where required: 20 ft (23-342). Missing fact: the adjoining zoning lots' lot-line types (and the exact far-west geometry).

Q4d — THE STREET WALL (real lot).
Along Northern Boulevard (the wide, mandatory frontage): [C, zr-35-631(b)] "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less. Up to 30 percent... may be recessed beyond eight feet..." So ≥70% of the Northern Boulevard frontage must be within 8 ft of that street line; the widest building places it on the line (within 8 ft). [C, zr-35-631(b) "However..."] if the block has a #prevailing street wall frontage# farther from the line, the 23-431(a) line-up may be applied — [?] prevailing frontage NOT KNOWN (no neighbour data).
Along 215 Place (narrow): [C, zr-23-436(c)] on corner lots the 23-431 street-wall location "shall be mandatory along only one #street# frontage," and where one frontage is wide and the other narrow it is applied "along the #wide street# frontage" — so along 215 Place the street-wall location is NOT mandatory, UNLESS [C, zr-35-633(b)] "where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage." [?, S step-p3-worked#zr-35-633-paragraphs] whether a Commercial District is mapped along the entire 215 Place block frontage is NOT KNOWN — variant on that fact. Facts that turn it: neighbouring buildings' street walls (prevailing frontage) and the commercial-mapping of the 215 Place block frontage.

Q4e — THE HEIGHTS: what missing ground elevations leave open.
Line 1 — left open: the ABSOLUTE elevation of the base plane (and therefore of the 30/45/55-ft limits and of every storey top) is not known, because curb level, final grade, street-wall-line and rear-wall-line levels and any slope are not in the folder; and, if different base planes apply to the within-/beyond-100-ft or corner portions, each portion could be a separate building (zr-23-43; zr-12-10-base-plane (c)).
Line 2 — NOT left open: the heights ABOVE the base plane — minimum base 30, maximum base 45, maximum building 55, and each storey top in Q5 — are all measured from the base plane (zr-23-43), so the relative tests (storey count, whether the building is below the minimum base height, whether a setback is triggered) hold regardless of the unknown elevation.

Q5. THE REAL LOT, THE TWO BUILDINGS.
The Q4d street-wall variants do NOT change the footprint: the widest building puts its walls on the street lines either way. Only Q4c changes it, and only in the far-west area beyond 100 ft of the corner point:
- Variant V2 (no rear yard beyond the corner): footprint = the lot-coverage-allowed area = 10,309.88 sq ft (corner portion 9,997.46 at 100% + interior strip 312.42 at 80%).
- Variant V1 (20-ft rear yard along the deemed rear lot line beyond 100 ft): footprint = V2 minus a 20-ft-deep strip along that deemed rear lot line; its exact area is NOT KNOWN (disputed geometry + adjoining lot-line type), but it is well above the area that already limits the building to one storey.
BUILDING A ("widest"), V2 footprint ≈ 10,309.88 sq ft; front wall on the Northern Boulevard street line; side edges on the side lot lines; no front/side yard (34-231/34-232); within 100 ft of the corner no rear yard (23-344(a)). Which limit binds: the corner-portion edges by 100% lot coverage, the strip edge by 80% lot coverage, the front by the street line/35-631(b), the sides by the side lot lines.
Storey | f2f | top(ft) | plan area | FA | total
1 | 10 | 10 | 10,309.88 | 10,309.88 | 10,309.88
[A] a 2nd storey → 20,619.76 > 20,150, not added. Total floor area 10,309.88 vs maximum 20,150; unused 9,840.12. Height 10 ft; 1 storey. Lot coverage used = the allowed maximum (corner 100% + strip 80%). Height 10 ft < minimum base 30 → BELOW (permitted, Q1b(ii), zr-23-436(e) via 35-633); street wall extends only to 10 ft (building height). < max base 45, < max building 55; no setback.
BUILDING B (method calls for it, since A 10 ft < 30 ft): smallest 10-ft storeys reaching ≥30 ft = 3; plan = 20,150/3 = 6,716.67 sq ft (whole maximum used). One plan: ~103.88 ft along the Northern Boulevard frontage × ~64.66 ft deep = 6,716.67 sq ft, kept within the corner-lot portion (within 100 ft of both streets), front wall on the Northern Boulevard street line.
Storey | f2f | top | area | total
1 | 10 | 10 | 6,716.67 | 6,716.67
2 | 10 | 20 | 6,716.67 | 13,433.33
3 | 10 | 30 | 6,716.67 | 20,150.00
Total 20,150 = maximum; unused 0. Height 30 = minimum base; ≤45; ≤55; no setback. Lot coverage within the corner portion (≤100%). Lies inside A's footprint (6,716.67 < 10,309.88). Street wall ≥70% within 8 ft of the Northern Boulevard line (here on the line), extends to 30 ft = min(min base 30, height 30).
Same under EVERY variant: maximum floor area 20,150; heights 30/45/55; the storey counts (A = 1, B = 3); A's height 10 ft, B's plan 6,716.67 sq ft and height 30 ft; the dwelling-unit ceiling. Variant-dependent (and not changing those): A's exact footprint area/shape (the V1 rear-yard strip) and whether the street wall is also mandatory along 215 Place.

END OF PART 5

PART 6 of 6

Q6. PRELIMINARY APARTMENT-ESTIMATE ARITHMETIC (owner assumptions, not law).
[A] share low 0.60, high 0.75; [A] starting apartment size 700 sq ft; [A] all floor area counts, so F (residential floor area the building holds) = total floor area. "Two decimals, unrounded" shown; no rounding-to-a-unit rule is chosen.

Q6a — for every building:
Made-up Building A, F = 16,000:
- 16,000 × 0.60 / 700 = 9,600/700 = 13.714285… = 13.71 → whole below 13, above 14.
- 16,000 × 0.75 / 700 = 12,000/700 = 17.142857… = 17.14 → below 17, above 18.
Made-up Building B, F = 20,000:
- 20,000 × 0.60 / 700 = 12,000/700 = 17.142857… = 17.14 → below 17, above 18.
- 20,000 × 0.75 / 700 = 15,000/700 = 21.428571… = 21.43 → below 21, above 22.
Real Building A, F ≈ 10,309.88 (V2; V1 slightly less, so these are an upper figure):
- 10,309.88 × 0.60 / 700 = 6,185.928/700 = 8.837040 = 8.84 → below 8, above 9.
- 10,309.88 × 0.75 / 700 = 7,732.41/700 = 11.046300 = 11.05 → below 11, above 12.
Real Building B, F = 20,150:
- 20,150 × 0.60 / 700 = 12,090/700 = 17.271428… = 17.27 → below 17, above 18.
- 20,150 × 0.75 / 700 = 15,112.5/700 = 21.589285… = 21.59 → below 21, above 22.

Q6b — greatest number of dwelling units the law allows on each lot (a legal ceiling, kept apart from Q6a):
[S, step-p4-worked#dwelling-unit-factors] factor 680; [C, zr-23-52(b)] "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#." [C, zr-23-52 opening] units = maximum residential floor area / factor.
- Real lot: [S, real-lot#L6] 29 dwelling units. (Check: 20,150/680 = 29.63; fraction 0.63 < 0.75 → 29.)
- Made-up lot: 20,000 / 680 = 29.4117…; fraction 0.41 < 0.75 → 29 dwelling units.
Each building's estimate ends vs that ceiling:
- Made-up A: 13.71–17.14 — both at or under 29. Made-up B: 17.14–21.43 — both under 29.
- Real A: 8.84–11.05 — both under 29. Real B: 17.27–21.59 — both under 29.
Every estimate end lies under the legal ceiling (29 on each lot). The Q6b number is a legal ceiling; the Q6a figures are an estimate on the owner's unvalidated assumptions.

Q7. WHAT IS MISSING.
Sections/defined terms pointed to but not in the folder, and the answer each leaves open:
- #developed# / #development# — zr-23-436(e) "#buildings#... that are #developed# or #enlarged#": leaves Q1b/Q3/Q5 "below minimum base height is permitted" resting on the ordinary reading of "developed", not a defined term.
- #street wall line level#, #rear wall line level#, #building segment#, #abutting buildings# — zr-12-10-base-plane cites them: keeps the base-plane elevation (Q4e) NOT KNOWN.
- Section 23-434 (eligible sites) and 23-435 (towers) — cited by zr-23-43/23-362(b)/35-632: not held; not relied on (no eligible-site/tower claim made).
- Section 23-341 (permitted obstructions) — cited by zr-12-10-lot-coverage and 23-342: not held; the owner "count everything" simplification sidesteps it, so no answer turns on it.
- #outer court# — cited by 23-431(b)/23-433/35-631: not held; affects only recess rules, not the simple walls worked.
- #Mandatory Inclusionary Housing areas#, #UAP developments# — footnotes to 23-22/23-432: not held; not applicable to standard residences here.
- #street setback line# — cited by zr-12-10-yard: not held; no answer turns on it (none assumed present).
- #prevailing street wall frontage# → #aggregate width of street walls# computed over neighbours: definitions held, but the neighbour data is missing (see facts below), keeping Q1c/Q2b/Q4d street-wall location conditional.
Missing FACTS about the real lot, and the variant each selects:
- Adjoining zoning lots' lot-line types at the deemed rear lot line → selects Q4c V1 (adjoining rear lot line → 20-ft rear yard) vs V2 (adjoining side lot line → none).
- Whether a Commercial District is mapped along the entire 215 Place block frontage → selects whether the street wall is also mandatory along 215 Place (zr-35-633(b)).
- Neighbouring buildings' street-wall widths and distances → whether a prevailing street wall frontage exists → whether 23-431(a) line-up "may be applied" instead of 35-631(b).
- Ground elevations (curb level, grade, street-wall-line/rear-wall-line levels, slope) → the absolute base-plane elevation (not the relative heights).
- The exact far-west geometry (whether the west edge exceeds 100 ft from the Northern Boulevard line) → which side-lot-line portion becomes a deemed rear lot line (readings 11 vs 12).
Texts named in Q1–Q6 I chose not to read (none needed for an answer): zr-12-10-lot-depth and zr-12-10-lot-width (depth 100 ft and widths are given as facts), zr-12-10-lot-through and zr-12-10-yard-equivalent-rear (neither lot is a through lot), and zr-12-10-short-dimension-of-a-block (23-344(b)/23-363(c) short-dimension branch is not invoked — the corner-point branch (a) governs).
Settled-sheet answers that an opened text seemed to contradict: NONE. Every text I opened (23-22 FAR 2.00; 23-432 R6B 30/45/55; 23-362 corner 100%/interior 80%; 23-52 factor 680 → 29; 35-631/35-633/23-436 street wall) agrees with the settled answers I relied on.

Q8. ONE-LINE SUMMARY PER QUESTION.
Q1: YES — a new R6B building wholly below the 30-ft minimum base height is permitted (zr-23-436(e), plain and under the C2-2 overlay), its street wall need only rise to the building height, and only the street-wall location (not the height numbers) turns on wide vs narrow.
Q2: Made-up R6B interior lot — FAR 2.00/20,000 sq ft, interior coverage 80%, 30/45/55 ft from the base plane (= curb level), DU factor 680; no front or side yard, 20-ft rear yard; the widest footprint is 100 × 80 = 8,000 sq ft (front on the street line, sides on the side lot lines, rear bound by the 20-ft yard = the 80% coverage cap).
Q3: Building A = 2 storeys, 8,000 sq ft/floor, 16,000 total (4,000 unused), 20 ft — below the minimum base height; Building B = 3 storeys of 6,666.67 sq ft (100 × 66.67), 20,000 total, 30 ft, inside A's footprint with its wall on the street line.
Q4: Real corner lot — R6B bulk, 20,150 sq ft, 30/45/55 ft, no single coverage figure (corner 100% = 9,997.46 sq ft + interior strip 80% = 312.42, total 10,309.88 sq ft of building); 35-631(b) street wall mandatory along wide Northern Boulevard; rear yard beyond the corner, base-plane elevation and prevailing frontage NOT KNOWN.
Q5: Building A = 1 storey ≈ 10,309.88 sq ft, 10 ft — below the minimum base height; Building B = 3 storeys of 6,716.67 sq ft, 20,150 total, 30 ft, wall on the Northern Boulevard line; storey counts/heights are the same under every variant, only A's exact footprint (V1 rear-yard strip) and the 215 Place street-wall duty vary.
Q6: Apartment estimate (F×0.60/700 and F×0.75/700) — made-up A 13.71/17.14, made-up B 17.14/21.43, real A 8.84/11.05, real B 17.27/21.59; the legal ceiling is 29 dwelling units on each lot (made-up 20,000/680→29; real 20,150/680→29), and every estimate end is under it.
Q7: NOT KNOWN items all trace to five missing facts (adjoining lot-line types, 215 Place commercial mapping, neighbour street walls, ground elevations, far-west geometry) and a handful of undefined cross-referenced terms; no opened text contradicts the settled sheet.

END-OF-REPORT
