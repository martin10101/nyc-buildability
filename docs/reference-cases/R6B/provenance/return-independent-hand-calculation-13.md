# Independent reading from the step-P6 sealed folder, reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-09, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - all 185 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, one made-up interior lot of 100 ft by 100 ft in plain R6B with every fact stated, 34 answers settled by earlier readings (copied word for word from the reference cases and given as settled, so completed readings are reused and not worked again), and three starting values chosen by the owner (marked as assumptions) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1 of the step-P6 pair; a value is recorded in a step-P6 reference-case row only where this reading and reading 2 (return-independent-hand-calculation-14.md) give the same answer on the same basis.

---

PART 1 of 8

This is a DRAFT reading of captured New York City Zoning Resolution text by an AI reader. It is NOT legal advice and NOT a professional review. I give no verdict that any building or lot complies with the law.

ONE HARD RULE — obeyed. I worked only from the sealed folder (read-only). I did not open, list or search anything under /root/project; I opened no web page and ran no web search; I wrote only inside my own scratch folder (two small arithmetic/geometry scripts); I wrote no agent memory.

FILES I READ (sealed-p6):
facts/: made_up_lot.json, starting_values_chosen_by_the_owner.json, settled_by_earlier_readings.json, lot_facts_pluto.json, lot_outline_epsg2263.json, streets_dcm_centerlines.json, zoning_nyco_query_C2-2.json, zoning_nyzd_query_R6B.json (all 8).
law/: zr-23-43, zr-23-431, zr-23-432, zr-23-433, zr-23-436, zr-35-62, zr-35-63, zr-35-631, zr-35-632, zr-35-633, zr-12-10-base-plane, zr-12-10-curb-level, zr-12-10-story, zr-12-10-building, zr-12-10-street-wall, zr-23-22, zr-23-362, zr-23-363, zr-23-34, zr-23-341, zr-23-342, zr-23-343, zr-23-344, zr-23-322, zr-23-335, zr-23-52, zr-12-10-lot-corner, zr-12-10-lot-interior, zr-12-10-prevailing-street-wall-frontage, zr-12-10-aggregate-width-of-street-walls, zr-12-10-lot-line-front, zr-12-10-lot-line-rear, zr-12-10-lot-line-side, zr-12-10-yard-rear. I listed INDEX.json by directory listing but did not read its body.
Marks: [F] fact, [S] settled sheet, [A] owner assumption / fixed method, [C] calculation/conclusion from quoted text, [?] NOT KNOWN.

Q1. MAY A BUILDING BE LOWER THAN THE MINIMUM BASE HEIGHT?

Q1a — R6B heights for standard residences (from the table in zr-23-432, R6B row):
[C] Minimum base height = 30 ft; maximum base height (standard residences) = 45 ft; maximum height of buildings (standard residences) = 55 ft. (zr-23-432 `table`, R6B row: min_base 30, standard_max_base 45, standard_max_building 55. The R6B row carries NO footnote, unlike the plain-R6 rows.)
[C] Measured from: the base plane. zr-23-43: "The height of all #buildings or other structures# shall be measured from the #base plane#." zr-23-432 caption: "MINIMUM BASE HEIGHT, MAXIMUM BASE HEIGHT, AND MAXIMUM BUILDING HEIGHTS". [S] settled: height-measured-from-base-plane.
[C] At/above the maximum base height: zr-23-432: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided at a height not lower than the minimum base height or higher than the maximum base height in accordance with Section 23-433." zr-23-433: "a setback with a depth of at least 10 feet ... from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet ... fronting on a #narrow street#."

Q1b — Is a new building whose WHOLE height is below the minimum base height permitted?
(i) Plain R6B: [C] YES by the words. Two provisions speak to it and they AGREE.
 - zr-23-436(e): "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights." Conditions it attaches: the building (or portion) must be "developed or enlarged" and must "not exceed such minimum base heights." A new building developed below 30 ft meets both, so the 30-ft minimum does not apply to it.
 - zr-23-431(b)(1)/(2): the street wall must "extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less." "Whichever is less" means a building shorter than 30 ft need only carry its street wall to its own height, not to 30 ft.
 Agreement: both remove any floor at the minimum base height for a below-30-ft building. No captured provision in this set forbids a building below 30 ft.

(ii) C2-2 overlay mapped within R6B: [C] YES, and the two provisions again agree.
 - Routing: R6B is an R6-through-R12 equivalency, so zr-35-63 governs (not zr-35-62, which by its title/body is "Commercial Districts With R1 Through R5 Equivalency" and does not reach R6B). zr-35-63 sends street-wall location to 35-631 and height/setback to 35-632; zr-35-632(a): "The minimum base height, maximum base height and maximum #building# height shall be as set forth in the table in Section 23-432 for the applicable #Residence District#" (so the same R6B 30/45/55). [S] overlay base-and-building-height confirms 30/45/55 unchanged.
 - zr-35-633: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows: (a) ... references to ... Section 23-431 shall be superseded by those of Section 35-631". Paragraph (e) of 23-436 is NOT excepted, so 23-436(e) (minimum base height does not apply to buildings not exceeding it) applies in the overlay.
 - zr-35-631(b): "...shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less." Same "whichever is less."
 Agreement: both say a below-30-ft building is permitted.

END OF PART 1.

PART 2 of 8

Q1c — If such a building is permitted, what do the street-wall words then require?
[C] To what height the street wall must rise: only to the building's own height. The street wall "shall ... extend to at least the minimum base height specified in Section 23-432, or the height of the #building#, whichever is less" (zr-23-431(b)(1)/(2); zr-35-631(b) in the overlay). For a building below 30 ft the lesser value is the building height, so the street wall must rise to the full building height and no more.
[C] Where it must stand:
 - Plain R6B: zr-23-431(a) "Line-up rules" govern R6B, R7B, R8B: "the #street wall# of a #building# shall be located no closer to the #street line# than the closest #street wall# ... nor further ... than the furthest #street wall# ... of an existing adjacent #building# ... Eligible adjacent #buildings# shall be located within 15 feet of the #street line#, within 25 feet of the subject #building#, and have a height that exceeds 35 feet." The "however" clause lets paragraph (b) percentage rules apply where there is no prevailing street wall frontage.
 - Overlay C2-2: the line-up rule is superseded by zr-35-631 (per 35-633(a)); zr-35-631(b): "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line#".
[C]/[?] Does any captured provision set a least height or least number of storeys? No. zr-23-436(e) removes the minimum-base-height floor for such a building, and no section among zr-23-43/431/432/433/436 or zr-35-62/63/631/632/633 states a minimum building height or a minimum number of storeys. [?] NOT KNOWN of any minimum-storeys rule — none exists in the captured texts; a rule outside this folder is not ruled out.

Q1d — Does anything depend on wide vs narrow street for a building at/below the maximum base height? [C] Quoting:
 - The setback (zr-23-433) DOES turn on wide/narrow ("at least 10 feet ... fronting on a #wide street#, and ... at least 15 feet ... fronting on a #narrow street#") but it applies only to "portions of a #building# #street wall# that exceed the maximum base height" (zr-23-432); a building at/below the maximum base height never triggers it.
 - The street-wall horizontal location DOES turn on wide/narrow under zr-23-431(b): "(1) Along #wide streets#, at least 70 percent ... within eight feet of the #street line# ... recesses deeper than 10 feet along a #wide street# or 15 feet along a #narrow street# ...; (2) Along #narrow streets#, at least 70 percent ... within 10 feet of the #street line# ... recesses deeper than 15 feet ..." This part of the street wall sits below the maximum base height, so it applies to a below-max-base building when paragraph (b) governs.
 - zr-35-631(b) in the overlay states a single "within eight feet" with no wide/narrow split, except the recess-depth clause ("deeper than 10 feet along a #wide street#, or 15 feet along a #narrow street#").
 - R6B heights do NOT depend on wide/narrow: the zr-23-432 R6B row carries no footnote 1/2, whereas footnotes 1/2 ("within 100 feet of a #wide street#" / "beyond 100 feet") split other districts' rows.
[C] Answer Q1: a building below the minimum base height is permitted in both plain R6B and in a C2-2 overlay within R6B; its street wall rises only to its own height and sits where 23-431 (plain) / 35-631 (overlay) place it; no captured text sets a least height or least storeys; wide/narrow affects the street-wall location distances (and the above-max-base setback, which such a building never reaches), not the R6B heights.

Q2. THE MADE-UP LOT (interior 100 ft × 100 ft, plain R6B, one 60-ft street, level ground at curb level) — THE LIMITS.

Q2a — taken from the settled sheet (each named):
[S] Maximum floor area ratio = 2.00 and maximum floor area = 20,000 sq ft (settled: floor-area-ratio-made-up-100x100 — "2.00 x 10,000 = 20,000 sq ft"; and floor-area-ratio-definition).
[S] Maximum lot coverage, interior lot = 80 percent (settled: interior-coverage).
[S] Minimum base height 30 ft, maximum base height 45 ft, maximum building height 55 ft for standard residences in R6B (settled: real-lot#L3 — these are the R6B district values, so they apply to this R6B lot), measured from the base plane (settled: height-measured-from-base-plane).
[S] Dwelling-unit factor = 680; a fraction of three-quarters or more counts as one dwelling unit (settled: dwelling-unit-factors).

END OF PART 2.

PART 3 of 8

Q2b — worked from the text for the made-up lot (what the sheet does not hold for this lot):
Facts used: [F] interior lot, rectangle 100 ft (frontage) × 100 ft (depth), one 60-ft street on one 100-ft side, level ground at curb level, vacant; each side neighbour's street wall stands on the street line for its full width and is 35 ft high; the rear neighbour's rear lot line is this lot's rear lot line for the full 100 ft (made_up_lot.json).

Front yard: [C] none required. zr-23-322 (R6-R12): "In the districts indicated, no #front yard# requirements shall apply." So depth = 0 ft; the building may stand on the front (street) lot line.

Side yards: [C] none required. zr-23-335(b) "All other #buildings#": "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet". (Paragraph (a)'s two 5-ft side yards are only for single-/two-family DETACHED residences, which this apartment building is not.) So required side-yard depth = 0 ft; any side open area, if provided, must be ≥ 5 ft.

Rear yard for an interior lot 100 ft wide × 100 ft deep: [C] 20 ft at/below 75 ft; 30 ft above 75 ft — the same figure the 40-ft-wide sheet answer gives, by the words. zr-23-342(a)(1) (detached/zero-lot-line): "for #buildings# or portions thereof at or below a height of 75 feet ... a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# ... and for portions above 75 feet ... 30 feet". zr-23-342(a)(2)(ii) (semi-detached/attached, lot width 40 ft or greater): same "not less than 20 feet" ≤75 ft, "30 feet" above. Lot width 100 ≥ 40, so either building type gives 20 ft. The shallow-lot reduction (zr-23-342(b)) does not apply: depth 100 ft is not less than 95 ft. [S] this matches the settled 40×100 rear-yard answer (20 ft / 30 ft), which noted the same for all building types and no shallow reduction.

Where the street wall must or may stand (plain-R6B words, given the neighbours): [C]/[?] The governing rule is zr-23-431(a) line-up. But the neighbours are 35 ft high, and an eligible adjacent building must "have a height that exceeds 35 feet" (zr-23-431(a)). 35 does not exceed 35, so the two neighbours are NOT eligible adjacent buildings. With no eligible adjacent building, paragraph (a) names no "closest" or "furthest" wall and so fixes no required range; it does not forbid the street wall on the street line. The "however" clause then allows paragraph (b) "where ... #street wall# surrounding the subject #building# do not have a #prevailing street wall frontage#." Whether a prevailing street wall frontage exists (zr-12-10-prevailing-street-wall-frontage: ≥100 ft aggregate width, ≥half within 2 ft of the average distance) cannot be confirmed: the neighbours' street-wall WIDTHS/lot widths are not stated (made_up_lot.json gives their set-back = 0 ft and height, not widths). [?] NOT KNOWN: the exact mandated street-wall placement, because the eligibility test turns on ">35 ft" (not met) and the fall-back to (b) turns on prevailing-frontage data not in the facts. For the fixed method I place building A's street wall ON the street line (0 ft), which no captured word forbids; I flag this as the method's choice, not a mandate.

Q2c — THE FOOTPRINT of building A (made-up lot):
[A]/[C] Sides and place: a rectangle 100 ft (frontage, running from side lot line to side lot line) × 80 ft (depth, from the street line inward), placed with its street wall on the front/street lot line and its two long sides on the two side lot lines.
[C] Area = 100 × 80 = 8,000 sq ft.
[C] Which limit binds each edge:
 - Front edge (100 ft): the street-wall location / front (street) lot line — street wall on the street line (zr-23-322 no front yard; zr-23-431 location).
 - Two side edges (80 ft each): the side lot lines — no side yard required (zr-23-335(b)).
 - Rear edge (100 ft): bound SIMULTANEOUSLY by the rear yard and the lot coverage. Rear yard 20 ft (zr-23-342(a)) gives depth 100 − 20 = 80 ft; 80 % lot coverage (settled; zr-23-362(a)) gives 0.80 × 10,000 = 8,000 sq ft = 100 × 80, the same 80-ft depth. Both bind the rear edge at 80 ft.

END OF PART 3.

PART 4 of 8

Q3. THE MADE-UP LOT, THE TWO BUILDINGS. [A] floor-to-floor = 10 ft; [A] simplification: every square foot of every floor counts as floor area (nothing exempt). [C] Base plane = curb level = the level ground (zr-12-10-base-plane: "the level of the #base plane# is any level between #curb level# and #street wall line level#"; the ground and curb are at one level per made_up_lot.json), so heights are measured from the ground datum (0 ft).

Q3a — BUILDING A (footprint 8,000 sq ft, plan unchanged each storey):
Storey | f2f | top above base plane | plan (ft) | plan area | floor area | running total
1 | 10 | 10 ft | 100 × 80 | 8,000 | 8,000 | 8,000
2 | 10 | 20 ft | 100 × 80 | 8,000 | 8,000 | 16,000
[C] A third storey would bring the total to 24,000 > 20,000 (the maximum), so building A stops at 2 storeys.
[C] Total floor area 16,000 vs maximum 20,000 → floor area left unused = 4,000 sq ft.
[C] Height = 20 ft. Number of storeys = 2 (zr-12-10-story: a story is between a floor surface and the ceiling above; no cellar here, so 2 floors = 2 stories).
[C] Lot coverage used = 8,000 / 10,000 = 80 % = the 80 % maximum.
[C] Yards left vs required: front 0 vs 0 required; side 0 vs 0 required; rear 100 − 80 = 20 ft vs 20 ft required (exactly met).
[C] Height vs heights: 20 ft is BELOW the minimum base height (30 ft). Per Q1b this is permitted (zr-23-436(e)); the street wall need rise only to 20 ft (its own height). 20 ft < 45 ft maximum base and < 55 ft maximum building. No setback is called for (nothing exceeds the 45-ft maximum base height). Because A is below the minimum base height, the fixed method calls for building B.

Q3b — BUILDING B (to the minimum base height):
[A]/[C] Smallest number of storeys whose top reaches ≥ 30 ft at 10 ft each: 3 storeys (top 30 ft; 2 storeys would be only 20 ft). Plan area = maximum floor area / number of storeys = 20,000 / 3 = 6,666.67 sq ft per storey; 3 × 6,666.67 = 20,000 = the whole maximum floor area.
Storey | f2f | top | plan (ft) | plan area | floor area | running total
1 | 10 | 10 ft | 100 × 66.667 | 6,666.67 | 6,666.67 | 6,666.67
2 | 10 | 20 ft | 100 × 66.667 | 6,666.67 | 6,666.67 | 13,333.33
3 | 10 | 30 ft | 100 × 66.667 | 6,666.67 | 6,666.67 | 20,000.00
[C] One plan: 100 ft wide (full frontage, side lot line to side lot line) × 66.67 ft deep, street wall on the street line. It lies inside building A's 100 × 80 footprint (66.67 ≤ 80; 100 = 100). Street-wall words: the street wall stands on the street line (as A) along the full 100 ft and rises to 30 ft = the minimum base height = the building height, satisfying "extend to at least the minimum base height ... or the height of the #building#, whichever is less" (zr-23-431(b)); the same eligibility caveat from Q2b applies (neighbours not >35 ft).
[C] Comparisons: total 20,000 = maximum (0 unused). Height 30 ft = minimum base height; ≤ 45 max base; ≤ 55 max building; no setback (30 < 45). Lot coverage 6,666.67 / 10,000 = 66.67 % ≤ 80 %. Rear yard 100 − 66.67 = 33.33 ft ≥ 20 ft. Front 0, side 0.

Q3c — WHAT A FLOOR SCHEDULE MUST LIST (only what my working needed), column → limit it lets a reader check:
 - Storey number / count → number of storeys; with f2f, the building height → maximum building height (55) and whether a setback is triggered.
 - Floor-to-floor height (per storey) → the running top elevation.
 - Height of the storey's top above the base plane → minimum base height (30), maximum base height (45), maximum building height (55), setback trigger.
 - Plan width × depth, and footprint area → lot coverage (80 %), side-yard (0 / ≥5 ft if provided), rear-yard depth, street-wall location.
 - Floor area per storey → the per-floor contribution to FAR.
 - Running total floor area → maximum floor area / FAR cap (20,000) and the unused floor area.
 - Street-wall distance from the street line (per storey) → the street-wall location rule (zr-23-431 / 35-631).
 - Rear-yard depth (lot depth − plan depth) → the rear-yard requirement (zr-23-342).

END OF PART 4.

PART 5 of 8

Q4. THE REAL LOT (BBL 4073340070: R6B with a C2-2 overlay) — THE LIMITS.

Q4a — taken from the settled sheet (each named):
[S] R6B rules govern the bulk of an all-residential building here (overlay-reading bulk-regulations: reached by zr-34-11 and zr-34-111).
[S] Maximum floor area ratio = 2.00 (floor-area-ratio with 34-22 read); maximum residential floor area = 20,150 sq ft (real-lot#L1; = 2.00 × recorded lotarea 10,075).
[S] Heights: minimum base 30 ft, maximum base 45 ft, maximum building 55 ft (real-lot#L3; overlay base-and-building-height — unchanged by the overlay).
[S] Setback above the base: 10 ft on the wide street (Northern Boulevard), 15 ft on the narrow street (215 Place) (real-lot#L13; overlay setback-above-base).
[S] Lot type = corner (real-lot#L9); lot lines = two front lot lines (Northern Blvd, 215 Place), two side lot lines, no rear lot line (real-lot-lot-lines); frontages Northern Boulevard 103.9 ft and 215 Place 100.0 ft (real-lot#L10); street widths Northern Boulevard wide (100 ft), 215 Place narrow (60 ft), which does not change the R6B floor area or height (real-lot#L11).
[S] Reach: at most 99.97 ft from the Northern Boulevard street line, at most 103.93 ft from the 215 Place street line, at most 144.60 ft from the corner; the whole lot is within 100 ft of Northern Boulevard but a ~3.93-ft strip (~390 sq ft) lies beyond 100 ft of 215 Place, and ~2,560 sq ft lies beyond 100 ft of the corner (corner-reach real-lot-reach).
[S] No front yard and no side yard is required (rear-yard with 34-23 read; 34-231 no front yard; 34-232 no side yard).
[S] Street-wall rule that applies and along which frontage: the overlay percentage rule zr-35-631(b) (≥70 % of aggregate street-wall width within 8 ft of the street line), mandatory along the WIDE Northern Boulevard frontage only (street-wall-location; zr-23-436-paragraphs — only (c) binds; zr-35-633-paragraphs — 35-633(a) applies).
[S] NOT KNOWN, with reasons: the rear yard beyond the corner area (benchmark-rear-yard — turns on the adjoining zoning lots' lot-line types); the whole-lot lot coverage (corner-reach real-lot-coverage — no single figure; corner portion 100 %, remaining interior portion 80 %); the base plane (base-plane-real-lot — all elevation inputs missing); the neighbouring street walls / whether a prevailing street wall frontage exists (real-lot-prevailing-frontage — no neighbouring-building data).

Q4b — THE LOT COVERAGE BY PORTION.
Words that divide the lot: zr-12-10-lot-corner: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable." zr-12-10-lot-interior: "An #interior lot# is any #zoning lot# neither a #corner lot# nor a #through lot#." Coverage values: zr-23-362(a): "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." (zr-23-363 can raise interior coverage only via shallow-lot / corner / short-dimension provisions; see Q4c/§23-363(b) within 100 ft of corners = 100 %, which here coincides with the corner portion.)

[C] My geometry (outline, EPSG:2263 feet; vertices P0..P4; corner at P2 where the two street lines meet at 89.69°):
 - Edge lengths: P0-P1 99.976 (west side lot line), P1-P2 103.879 (Northern Blvd front), P2-P3 99.976 (215 Place front), P3-P4 101.709 + P4-P0 2.224 (south side lot line). Shoelace area = 10,387.99 sq ft (equals the served Shape__Area 10,387.99).
 - Distances from the 215 Place street line: P2 0, P3 0, P4 101.71, P0 103.93, P1 103.88 → a strip near the west/south edge lies beyond 100 ft.
 - Corner-lot portion (within 100 ft of 215 Place — and the whole lot is already within 100 ft of Northern Blvd, max 99.975 ft) = 9,997.60 sq ft. Interior-lot portion (strip beyond 100 ft of 215 Place) = 390.39 sq ft (matches settled ~390). Sum 10,387.99.
 - Sides of the strip: ~3.93 ft deep, ~100 ft long along the west edge, tapering (a thin wedge against P0-P1-P4).
[C] Building each portion allows: corner portion 100 % × 9,997.60 = 9,997.60 sq ft; interior strip 80 % × 390.39 = 312.31 sq ft; TOTAL maximum footprint = 10,309.91 sq ft.
[C] Measured vs recorded: shoelace 10,387.99 sq ft vs recorded PLUTO lotarea 10,075 (≈ +3.1 %). Per the fixed method I use the RECORDED 10,075 for floor area (FAR cap 2.00 × 10,075 = 20,150, matching settled), and my MEASURED geometry for lot coverage/footprint.

END OF PART 5.

PART 6 of 8

Q4c — THE REAR YARD BEYOND THE CORNER AREA (do not settle; work each variant).
Words: zr-23-344(a): "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." (The corner angle is 89.69° ≤ 135°, so within 100 ft of the corner no rear yard is required.) zr-23-344(c): "for #interior# or #through lot# portions of #corner lots# ... the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply: (1) ... a #rear yard# shall be provided in accordance with Section 23-342 ..., where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#; ... (3) In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#." zr-23-342(a)(1)/(2): rear yard 20 ft at/below 75 ft. zr-23-343 (rear-yard EQUIVALENT) applies to #through lots#; the remaining portion here is an interior-lot portion, so 23-343 does not apply [C].

[C] My geometry: the whole lot is within 100 ft of the Northern Boulevard line (max 99.975 ft), so the west side lot line (which intersects Northern Blvd) has essentially NO portion beyond 100 ft (this agrees with settled reading 12; it differs from reading 11, which found a ~101-ft sliver — I flag this as the readers' known geometry disagreement, held not-known on the settled sheet, not a contradiction). The south side lot line (which intersects the 215 Place line) HAS a ~3.93-ft-long portion beyond 100 ft of 215 Place (near P0); that portion is a deemed rear lot line under 23-344(c).

Variants along that deemed rear lot line (the ~3.93-ft south-edge segment beyond 100 ft of 215 Place):
 - V1: the deemed rear lot line COINCIDES WITH A SIDE LOT LINE of the adjoining zoning lot → zr-23-344(c)(3): NO rear yard required. Selected if the neighbour's lot line there is a side lot line.
 - V2: the deemed rear lot line COINCIDES WITH A REAR LOT LINE of the adjoining zoning lot → zr-23-344(c)(1): a 20-ft rear yard (zr-23-342) along that deemed rear lot line. Place/depth: a band ~20 ft deep along the ~3.93-ft deemed rear lot line (~79 sq ft) near P0, kept open. Selected if the neighbour's lot line there is a rear lot line.
[?] Missing fact that selects V1 vs V2: the lot-line type of the adjoining zoning lot along that segment (no record of the adjoining lots' lot lines — lot_facts_pluto.json "not_in_this_folder"). I do not settle it.

Q4d — THE STREET WALL (building A), along each street.
Words: zr-35-631(b): "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height ... or the height of the #building#, whichever is less. Up to 30 percent ... may be recessed beyond eight feet ...". Mandatory along ONE frontage only: zr-23-436(c): "On #corner lots# ... the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one ... is a #wide street# and the other a #narrow street#, the ... rules shall be applied along the #wide street# frontage" — i.e., along NORTHERN BOULEVARD; and zr-35-633(a) supersedes the 23-431 reference with 35-631. zr-12-10-aggregate-width-of-street-walls: the aggregate width is "the sum of the maximum widths of all #street walls# ... within 50 feet of a #street line#."
[C] Along Northern Boulevard (wide, mandatory): ≥70 % of building A's Northern-Blvd street-wall width must lie within 8 ft of the Northern Blvd street line and rise to at least 30 ft or the building height, whichever is less. Building A presses its wall onto the street line (0 ft), so 100 % lies within 8 ft — satisfied at the line.
[C] Along 215 Place (narrow): the street-wall location rule is NOT mandatory (only one frontage binds); building A may stand on the 215 Place street line (no front yard). 
[?]/[C] The "may be applied" fall-back where a #prevailing street wall frontage# exists (zr-35-631(b) closing clause, zr-23-431(a)) is NOT KNOWN — the neighbouring street walls are not in the folder (settled real-lot-prevailing-frontage) — but it is optional ("may"), so it does not change the widest footprint (the wall sits on the street line either way). The 35-633(b) one-frontage clause (whether a Commercial District is mapped along the entire block frontage) is also NOT KNOWN (settled 35-633-paragraphs); it does not change building A's placement on the line. So the street wall creates NO footprint-changing variant.

Q4e — THE HEIGHTS and the missing ground elevations (two lines):
[?] What they leave open: the base-plane ELEVATION (datum) from which 30/45/55 ft are measured is not known — curb level, street-wall-line level, and adjoining final grade are all absent (settled base-plane-real-lot; zr-12-10-base-plane / zr-12-10-curb-level), so the absolute top elevations and the exact slab heights above grade are undetermined.
[C] What they do NOT leave open: the heights ABOVE the base plane themselves — 30 ft minimum base, 45 ft maximum base, 55 ft maximum building, and 2-/3-storey counts at 10 ft floor-to-floor — are fixed regardless of the datum, because they are all measured FROM the base plane.

END OF PART 6.

PART 7 of 8

Q5. THE REAL LOT, THE TWO BUILDINGS (per variant). [A] 10-ft floor-to-floor, every sq ft counts. FAR cap floor area = 20,150 sq ft [S]. The only footprint-changing variants are V1/V2 of Q4c (the street wall of Q4d adds none). 

V1 (deemed rear lot line coincides with a neighbour's SIDE lot line → no rear yard beyond the corner):
[C] Footprint of building A = corner portion at 100 % (9,997.60) + interior strip at 80 % (312.31) = 10,309.91 sq ft.
 Edges and binding limit: Northern Blvd edge → street-wall location on the street line (zr-35-631(b)); 215 Place edge → the 215 Place street line (no front yard, location not mandatory here); west side edge → west side lot line (no side yard); south side edge → south side lot line, 100 % coverage within 100 ft of the corner, 80 % on the ~390 sq ft strip beyond 100 ft of 215 Place (no rear yard in V1).
[C] Building A storey table (plan constant = footprint):
 Storey 1 | 10 ft | top 10 ft | ~10,309.91 sq ft | floor area 10,309.91 | total 10,309.91.
 A second storey would total 20,619.82 > 20,150, so building A = 1 storey.
[C] Comparisons: total floor area 10,309.91 vs maximum 20,150 → unused 9,840.09. Height 10 ft (1 storey). Lot coverage used = corner 100 % + strip 80 % (the portion maxima). Yards: front 0 (both streets); side 0; rear 0 required (V1). Height 10 ft is BELOW the minimum base height 30 ft → permitted (Q1b, zr-23-436(e)); street wall rises only to 10 ft; 10 < 45 max base and < 55 max building; no setback. Because A is below the minimum base height, the method calls for building B. (This 1-storey mega-footprint is the mechanical result of "widest footprint, stack until the FAR cap"; I report it as-is.)

V2 (deemed rear lot line coincides with a neighbour's REAR lot line → a 20-ft rear yard along the ~3.93-ft deemed rear lot line near P0):
[C] Footprint of building A ≈ 10,309.91 − ~63 sq ft (the part of the ~79-sq-ft, 20-ft-deep rear-yard band that falls in the corner portion, which V1 had covered at 100 %) ≈ 10,246 sq ft (approximate; the split of the band between the corner and strip portions is geometry-sensitive). Binding limits as V1, plus the deemed-rear-lot-line rear yard on the south edge near P0.
[C] Building A storey table: 1 storey ≈ 10,246 sq ft, top 10 ft; a second storey (≈20,492) > 20,150, so still 1 storey. Unused ≈ 9,904. All other comparisons as V1 (height 10 ft below minimum base height; no setback; triggers building B).

[C] V1 and V2 give effectively the SAME building A (1 storey, below the minimum base height); the footprint differs only by ~63 sq ft of open rear yard near the far corner. Both remain 1 storey because each footprint (10,310 / ~10,246) exceeds 10,075 = half the 20,150 FAR cap.

BUILDING B (identical under V1 and V2 — it uses the whole FAR cap, not the footprint):
[C] Smallest storey count whose top ≥ 30 ft at 10 ft = 3 storeys (top 30 ft). Plan area = 20,150 / 3 = 6,716.67 sq ft per storey; 3 × 6,716.67 = 20,150.
 Storey 1 | top 10 | 6,716.67 | total 6,716.67
 Storey 2 | top 20 | 6,716.67 | total 13,433.33
 Storey 3 | top 30 | 6,716.67 | total 20,150.00
[C] One plan: ~103.9 ft wide along Northern Boulevard (street wall on the Northern Blvd street line) × ~64.66 ft deep (6,716.67 / 103.9). It lies inside building A's footprint (A covers nearly the whole lot; depth 64.66 ≤ ~100 ft). Street-wall words: the full Northern-Blvd wall on the line → ≥70 % within 8 ft satisfied (zr-35-631(b)); rises to 30 ft = minimum base height = building height. Comparisons: total 20,150 = maximum (0 unused); height 30 ft = minimum base; ≤45 max base, ≤55 max building; no setback (30 < 45); within-100-ft-of-corner so no rear yard binds this plan.
[C] Figures the SAME under every variant: maximum floor area 20,150; heights 30/45/55; building B (3 storeys, 20,150 sq ft, ~103.9 × 64.66); the dwelling-unit ceiling 29 (Q6b); the no-front-yard/no-side-yard results. DIFFERING by variant: building A's footprint and its one-storey floor area (10,309.91 in V1, ~10,246 in V2) and the presence/absence of the small rear yard near P0.

END OF PART 7.

PART 8 of 8

Q6. PRELIMINARY APARTMENT ESTIMATE (arithmetic on owner assumptions; NOT law). [A] F = residential floor area the building holds; estimate F×0.60/700 and F×0.75/700, two decimals, unrounded; whole numbers just below and just above; no rounding rule chosen.

Q6a:
 - MADE-UP A (F = 16,000): 16,000×0.60/700 = 13.71 → below 13, above 14. 16,000×0.75/700 = 17.14 → below 17, above 18.
 - MADE-UP B (F = 20,000): ×0.60 = 17.14 → 17 / 18. ×0.75 = 21.43 → 21 / 22.
 - REAL A V1 (F = 10,309.91): ×0.60/700 = 8.84 → 8 / 9. ×0.75/700 = 11.05 → 11 / 12.
 - REAL A V2 (F ≈ 10,246): ×0.60/700 ≈ 8.78 → 8 / 9. ×0.75/700 ≈ 10.98 → 10 / 11. (Approximate; depends on the V2 footprint.)
 - REAL B (F = 20,150): ×0.60/700 = 17.27 → 17 / 18. ×0.75/700 = 21.59 → 21 / 22.

Q6b — greatest number of dwelling units the law allows (a legal ceiling, kept apart from Q6a):
[S] Factor 680; fraction ≥ three-quarters counts as one (dwelling-unit-factors; zr-23-52(b): "the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters ... shall be considered to be one #dwelling unit#"). zr-23-52 opening: maximum DUs = maximum residential floor area permitted on the zoning lot ÷ factor.
 - Real lot: [S] = 29 (real-lot#L6). Check: 20,150 / 680 = 29.63; fraction 0.63 < 0.75 → 29.
 - Made-up lot (worked from the settled factor and the settled made-up floor area 20,000): 20,000 / 680 = 29.41; fraction 0.41 < 0.75 → 29 dwelling units [C].
Each estimate end at or under the ceiling (29)? YES for every building: made-up A 13–18, made-up B 17–22, real A 8–12, real B 17–22 — all ≤ 29. The Q6a figures are an estimate on assumptions; the 29 is the legal ceiling; they are not the same thing.

Q7. WHAT IS MISSING.
Sections/defined terms the texts point to but the folder does not hold (pointing words ≤25 words; which answer stays open):
 - #street wall line level# (zr-12-10-base-plane: "any level between #curb level# and #street wall line level#") — no definition captured → base-plane elevation stays NOT KNOWN (real lot; Q4e).
 - #base plane# inputs "average elevation of the final grade adjoining the #building#" (zr-12-10-base-plane) — needs grade elevations not in the folder → real-lot datum NOT KNOWN.
 - zr-23-434 "Height and setback modifications for eligible sites" (referenced by zr-23-362(b), zr-35-632(b)) — not read/needed; eligible-site coverage (65/50 %) not used.
 - zr-23-435 towers, zr-23-413 dormers/obstructions, zr-23-311/23-312 obstructions (referenced by 23-43, 23-433, 23-341) — not captured in full / not needed; no answer turns on them.
 - #outer court# (zr-23-431(b), zr-35-631) — not defined in folder; affects only recess geometry, not my footprints.
Missing FACTS about the real lot that an answer turned on, and the variant each selects:
 - The adjoining zoning lot's lot-line type along the south-edge segment beyond 100 ft of 215 Place → selects Q4c/Q5 V1 (side lot line → no rear yard) vs V2 (rear lot line → 20-ft rear yard).
 - The neighbouring buildings' street-wall widths/distances (and block data) → whether a #prevailing street wall frontage# exists (the optional 35-631/23-431(a) fall-back); does not change the widest footprint.
 - Ground/curb elevations → the base-plane datum (Q4e).
 - The west-edge geometry near 100 ft of Northern Boulevard: my computation finds the whole lot within 100 ft (max 99.975 ft, agreeing with settled reading 12); reading 11's ~101-ft sliver would add a second tiny deemed-rear-lot-line segment — held not-known on the settled sheet.
Texts named in Q1–Q6 I chose NOT to read (relied on the settled sheet for their content): zr-12-10-lot-coverage, zr-12-10-floor-area, zr-12-10-floor-area-ratio, zr-12-10-yard, zr-12-10-yard-front, zr-12-10-yard-side, zr-12-10-lot-depth, zr-12-10-lot-width (the settled sheet supplies the lot-coverage, floor-area-ratio and yard definitions I used). 
Settled answers a text I opened seemed to contradict: NONE. My outline geometry agrees with the settled reach figures (99.97 / 103.93 ft; ~390-sq-ft strip) and with settled reading 12 on the west edge; no opened text contradicted any settled answer.

Q8. ONE-LINE SUMMARIES.
Q1: A building below the minimum base height is permitted in plain R6B and in a C2-2 overlay within R6B (zr-23-436(e); "whichever is less" in zr-23-431(b)/35-631(b)); its street wall rises only to its own height, wide/narrow affects street-wall location not R6B heights, and no captured text sets a least height or storeys.
Q2: Made-up R6B 100×100 — FAR 2.0 / 20,000 sq ft, 80 % interior coverage, 30/45/55 ft from the base plane, DU factor 680 [S]; no front yard, no side yard, 20-ft rear yard [C]; footprint of A = 100 × 80 = 8,000 sq ft; street-wall placement partly NOT KNOWN because the 35-ft neighbours do not "exceed 35 feet".
Q3: Building A = 2 storeys, 20 ft, 16,000 sq ft (4,000 unused), below the minimum base height; building B = 3 storeys, 30 ft, 20,000 sq ft, 100 × 66.67 inside A.
Q4: Real lot — R6B bulk, FAR 2.0 / 20,150, 30/45/55, 10/15-ft setbacks, corner lot, no front/side yard, street wall mandatory on Northern Boulevard (35-631(b)); whole-lot coverage NOT KNOWN (corner 100 % / interior 80 %); rear yard beyond the corner, base plane, and prevailing frontage NOT KNOWN.
Q4b: Corner portion 9,997.60 sq ft (100 %) + interior strip 390.39 sq ft (80 %) → maximum footprint 10,309.91 sq ft; measured area 10,387.99 vs recorded 10,075 (floor area uses 10,075 → 20,150).
Q4c: Beyond the corner — V1 (neighbour side lot line) no rear yard; V2 (neighbour rear lot line) 20-ft rear yard on the ~3.93-ft deemed rear lot line near P0; selector NOT KNOWN.
Q4d: Street wall ≥70 % within 8 ft of the Northern Boulevard street line (on the line for the widest footprint); not mandatory on 215 Place; prevailing-frontage option NOT KNOWN but "may", so no footprint variant.
Q4e: Missing elevations leave the base-plane datum (absolute heights) NOT KNOWN; they do not change the 30/45/55 ft and storey counts measured from the base plane.
Q5: Both variants give building A = 1 storey (~10,310 V1 / ~10,246 V2, below the minimum base height) and the same building B = 3 storeys, 30 ft, 20,150 sq ft (~103.9 × 64.66 on Northern Boulevard).
Q6: Estimates — A/B made-up 13.71/17.14 and 17.14/21.43; real A 8.84/11.05 (V1); real B 17.27/21.59; dwelling-unit ceiling = 29 on each lot, and every estimate end is ≤ 29.
Q7: Chief gaps — the adjoining lot-line types (V1/V2), the neighbouring street walls (prevailing frontage), and the ground elevations (base-plane datum); no opened text contradicted the settled sheet.

END-OF-REPORT
