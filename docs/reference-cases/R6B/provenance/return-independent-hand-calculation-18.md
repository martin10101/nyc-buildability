# Independent reading from the step-P8 sealed folder, reading 2 (provenance)

What this is: one of two independent readings made on 2026-10-14, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the 189 pinned law-text captures (without their notes), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, the stated facts of Building B and the stated measure, and EIGHTEEN answers settled by earlier readings (copied word for word and given as settled, so completed readings are reused and not worked again; the earlier footprint answer real-building-b was left out on purpose) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2 of the step-P8 pair (a scenario-optimization-engineer); a value is recorded in the placement-building-b reference case only where this reading and reading 1 (return-independent-hand-calculation-17.md) give the same answer on the same basis.

---

INDEPENDENT HAND READING — 215-16 Northern Boulevard (block 7334, lot 70, BBL 4073340070), R6B with C2-2 overlay, condition Z1 (lot 70 alone is the zoning lot).

This is a DRAFT reading of captured law text by an AI. It is NOT legal advice and NOT a professional zoning review. No verdict is given that any building or lot complies.

THE ONE HARD RULE — obeyed. I read only files inside the sealed folder .../sealed-p8 and wrote only inside .../reader-p8-2 (two small python helpers for arithmetic/geometry). I opened no web page, ran no web search, and opened nothing else under /root/project.

FILES I READ (23):
facts/ — building_b_and_the_stated_measure.json; printed_tax_map_labels.json; pluto_rows_lots_70_and_1.json; zoning_nyzd_query_R6B.json; zoning_nyco_query_C2-2.json; settled_by_earlier_readings.json; block_7334_lot_outlines_epsg2263.json; streets_dcm_centerlines.json.
law/ — zr-23-322; zr-23-335; zr-23-342; zr-23-344; zr-23-362; zr-23-431; zr-23-432; zr-23-433; zr-23-436; zr-35-631; zr-35-633; zr-12-10-street-wide; zr-12-10-street-narrow; zr-12-10-lot-corner. Plus INDEX.json.
(Definitions of yard, rear yard, front/side yard, lot coverage, street wall, curb level, prevailing street wall frontage I take from settled_by_earlier_readings.json, cited as "settled".)

THE NINE BASES used below: law, deed, survey, printed_tax_map, approved_plan, filing_attribute, administrative_record, gis, derived. Each quantity names exactly one.

=== PART 1 of 5 — Q1: THE RULES THAT BEAR ON THE PLACEMENT ===

Facts used: Northern Boulevard mapped width = 100 ft; 215 Place mapped width = 60 ft [F, administrative_record — DCM City Map "Streetwidth", streets_dcm_centerlines.json]. Building = all-residential, 3 storeys, 30 ft high [F]. District R6B, overlay C2-2 [F, filing_attribute — pluto_rows + zoning_nyzd/nyco]. Lot is a corner lot with two front lot lines (Northern Boulevard, 215 Place), two side lot lines (the two interior edges), no rear lot line [S: step-p3-worked#real-lot-lot-lines].

Wide/narrow: "A 'wide street' is any #street# 75 feet or more in width" (zr-12-10-street-wide); "A 'narrow street' is any #street# less than 75 feet wide" (zr-12-10-street-narrow). So Northern Boulevard (100) = wide; 215 Place (60) = narrow [C].

(a) STREET WALL.
Overlay path: 35-633 says "The additional height and setback regulations set forth in Section 23-436 shall apply, except … references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631" (zr-35-633). 23-436(c): "On #corner lots#, … the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one of the #street# frontages … is a #wide street# and the other a #narrow street#, the #street wall# location rules shall be applied along the #wide street# frontage" (zr-23-436).
- WIDE street (Northern Boulevard): the location is MANDATORY here. 35-631(b): "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less" (zr-35-631). (The plain-R6B twin is 23-431(b)(1): ≥70% within 8 ft of a wide street.) "Whichever is less" = min(30 ft min base height, 30 ft building) = 30 ft, so the street wall need rise only to 30 ft [S: step-p6-worked#min-base-height-street-wall; C with zr-23-432 R6B row min base height = 30]. How much of the frontage: the law fixes 70% of the aggregate width of the street walls that exist within 8 ft; it does not itself mandate a fixed % of frontage be built [C].
- NARROW street (215 Place): location is NOT mandatory (23-436(c) applies it to only the one, wide, frontage), UNLESS a Commercial District is mapped along the ENTIRE 215 Place block frontage — 35-633(b): "where a #zoning lot# is bounded by only one #street line# … where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage" (zr-35-633). Whether that condition holds is NOT KNOWN [?; S: step-p6-worked#real-lot-street-wall]. The prevailing-street-wall-frontage line-up rule of 23-431(a)/35-631 "may be applied" (optional) and needs neighbour data the folder lacks [?].

(b) FRONT AND SIDE YARDS; open area along a side lot line.
- Front yard: "In the districts indicated, no #front yard# requirements shall apply" (zr-23-322) — the building may stand on the street line [S: step-p6-worked#made-up-front-yard].
- Side yard: 23-335(b): "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#" (zr-23-335). 23-335(a)'s 5-ft side yards are only for single-/two-family detached residences, which this is not [C; S: step-p6-worked#made-up-side-yard].

(c) REAR YARD (settled; where NOT KNOWN I state the placement's assumption).
No rear lot line exists [S]. 23-344(a): "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less" (zr-23-344). The Northern Blvd/215 Place interior angle computes at ≈89.7° from the GIS outline (≤135°) [C, gis — NOT a surveyed angle, so conditional]. Overall the rear-yard answer is NOT KNOWN [S: short-block-rear-yard#real-lot-z1-rear-yard]: it turns on (i) the governing measurement basis (street-line/tax-map vs centreline) and (ii) 23-344(c) — "the portion of a #side lot line# beyond 100 feet of the #street line# … shall be considered a #rear lot line#", then 23-344(c)(3) "no #rear yard# … where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#" vs (c)(1) a 23-342 rear yard where it coincides with a neighbour's rear lot line — and the adjoining zoning lot's lot-line kind is a missing fact [S: short-block-rear-yard#real-lot-beyond-100-sliver]. WHAT THE PLACEMENT ASSUMES: that no rear yard constrains it — consistent with 23-344(a) within 100 ft of the corner and the settled no-rear-lot-line finding; but the building's farthest corner is ~120.8 ft from the corner point (tax basis, below) and part of the footprint lies beyond 100 ft of the 215 Place street line, so this assumption rests on the unresolved 23-344(c)/basis question. If a rear yard were required there it is 20 ft at/below 75 ft (23-342(a)(2)(ii), lot width ≥40 ft) — not applied here [?].

(d) MAXIMUM LOT COVERAGE. 23-362(a): "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent" (zr-23-362). The corner-lot portion is defined (zr-12-10-lot-corner): "that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion … shall be subject to the regulations for a #through lot# or … #interior lot#." So for THIS corner lot the max is read by portion: 100% in the corner portion (within 100 ft of both street lines), 80% in any remaining interior portion (the strip beyond 100 ft of the 215 Place line) — no single whole-lot figure [S: step-p6-worked#real-lot-coverage-by-portion].

(e) SETBACK AT THIS HEIGHT. 23-432 (R6B row): minimum base height 30, maximum base height 45, maximum building height 55 ft (no footnote on the R6B row) [table, zr-23-432]. 23-432: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided…". 23-433: the 10-ft-wide/15-ft-narrow setback is required "At a height not lower than the minimum base height or higher than the maximum base height" (zr-23-433). The building is 30 ft, which does not exceed the 45-ft maximum base height, so the setback trigger height is not reached: NO setback is required at 30 ft [C].

=== PART 2 of 5 — Q2: THE PLATE; Q3: FOOTPRINT ON THE PRINTED-TAX-MAP BASIS ===

Q2. THE PLATE = zoning floor area per storey.
Facts: total zoning floor area = 20,150 sq ft; storeys = 3; "plate = zoning floor area per storey (20,150 / 3); no gross-up, exclusions or wall-thickness conversion worked" [F, building_b_and_the_stated_measure.json].
Division: 20,150 ÷ 3 = 6,716.6666… → 6,716.67 sq ft (rounded to the hundredth) [C].
Basis: DERIVED (computed from the stated 20,150 sq ft zoning floor area ÷ 3). The 20,150 is itself the recorded lot area 10,075 × 2.00 per settled [S], and is used here as given; it is zoning floor area, not a physical floor plate [F].

Q3. FOOTPRINT, PRINTED-TAX-MAP BASIS. Tax-map label lot 70 = "100.76 ft on Northern Boulevard, 100 ft deep" [F, printed_tax_map; matches PLUTO lotfront 100.76 / lotdepth 100, filing_attribute]. Placement: rectangle, full Northern Boulevard frontage as width, depth measured back from the Northern Boulevard street line = what the plate needs; one corner at the street-line intersection, one wall along 215 Place [F, placement].
- Plan WIDTH along Northern Boulevard = 100.76 ft [F, printed_tax_map].
- DEPTH the plate needs = plate ÷ width = 6,716.6667 ÷ 100.76 = 66.66005 → 66.66 ft [C, derived].
- Check: rounded depth × width = 66.66 × 100.76 = 6,716.6616 → 6,716.66 sq ft; the plate is 6,716.67 sq ft, so the rounded footprint is 0.01 sq ft LESS than the plate [C, derived].
- DISTANCE back wall → lot line opposite Northern Boulevard = tax-map depth − building depth = 100 − 66.66 = 33.34 ft [C, derived].
- DISTANCE to each other lot line: 215 Place front lot line = 0 ft (one wall runs on it for the 66.66 ft depth); the side lot line shared with lot 1 = 0 ft (the far width-wall runs on it for the 66.66 ft depth, because that side line is parallel to 215 Place and perpendicular to Northern Boulevard — confirmed from the GIS edge directions); back side lot line (opposite Northern Boulevard) = 33.34 ft [C, derived].
- LOT LINES THE BUILDING TOUCHES: the Northern Boulevard front lot line (full 100.76 ft width); the 215 Place front lot line (for 66.66 ft of its ~100 ft length); the lot-1 side lot line (for 66.66 ft of its length). It does NOT touch the back side lot line (33.34 ft away) [C].
- For the rear-yard note: the building's farthest corner from the corner point = √(100.76² + 66.66²) = 120.81 ft [C, derived].

=== PART 3 of 5 — Q4: PLACEMENT vs EACH Q1 RULE (printed-tax-map basis); Q5: GIS CONFLICT CHECK ===

Q4. Side-by-side (rule figure | placement figure; no compliance verdict):
(a) Street wall, WIDE (Northern Blvd): rule — ≥70% of aggregate street-wall width within 8 ft of the street line, rising to min(30 ft, building height)=30 ft [law, zr-35-631/23-431]. Placement — wall ON the street line (0 ft), full 100.76 ft frontage, 30 ft tall → 100% within 8 ft [derived/printed_tax_map]. Street wall, NARROW (215 Place): rule figure NOT KNOWN — not mandatory under 23-436(c) unless the 35-633(b) whole-frontage-commercial condition holds, which is NOT KNOWN [?]. Placement — a wall ON the 215 Place street line (0 ft) for the 66.66 ft depth [derived].
(b) Front yard: rule — none required (0) [law, 23-322]. Placement — 0 ft (on the street line) [derived]. Side yard: rule — none required for this building type; any open area along a side lot line ≥5 ft wide [law, 23-335(b)]. Placement — building ON the lot-1 side lot line (0 open area along the touched 66.66 ft); beyond the back wall the open strip along that side line is 33.34 ft long and far wider than 5 ft [derived].
(c) Rear yard: rule figure NOT KNOWN overall (23-344(a) no rear yard within 100 ft of the ~89.7° corner; 23-344(c) strip beyond 100 ft of the 215 Place line unresolved — missing adjoining-lot fact) [S/?]. Placement — back wall 66.66 ft from Northern Blvd; farthest building corner ~120.81 ft from the corner point; the placement assumes no rear yard constrains it [derived].
(d) Lot coverage: rule — corner-lot portion 100%, interior-lot portion 80% (23-362; portion split per zr-12-10-lot-corner). Placement — footprint 6,716.67 sq ft; share of the WHOLE lot = 6,716.67 ÷ 10,075 (recorded lot area, filing_attribute — PLUTO lotarea) = 66.67% [derived]; using the tax-map rectangle 100.76 × 100 = 10,076 sq ft (printed_tax_map) it is 66.66% [derived]. The footprint lies mostly in the corner portion (≤100 ft from both street lines, 100% max); a thin sliver beyond 100 ft of the 215 Place street line (the far ~0.76 ft of width on the tax basis) sits in the interior portion (80% max). SETTLED on the permitted max: read by portion, not a single whole-lot figure; the whole-lot coverage stays NOT KNOWN [S: step-p6-worked#real-lot-coverage-by-portion]. No compliance verdict given.
(e) Setback: rule — required only above the 45 ft maximum base height (then 10 ft wide / 15 ft narrow) [law, 23-432/23-433]. Placement — building 30 ft; the trigger height is not reached, so the rule states no setback figure for this building [derived].

Q5. CONFLICT CHECK — city GIS outline (EPSG:2263, US survey feet) beside the tax-map figure. GIS lot 70 is a near-rectangle; its Northern Boulevard frontage edge (corner → lot-1 side) = 103.879 ft; the two depth edges = 99.976/99.975 ft; measured area (shoelace) = 10,387.99 sq ft [all gis, block_7334_lot_outlines]. Reaches match settled (99.97 / 103.93 / 144.60) [S].
- Frontage/width on Northern Blvd: tax 100.76 ft | GIS 103.879 ft | difference +3.119 ft (GIS larger).
- Lot depth back from Northern Blvd: tax 100 ft | GIS 99.97 ft | difference −0.03 ft.
- Plan's depth (plate ÷ width): tax 66.66 ft | GIS = 6,716.6667 ÷ 103.879 = 64.658 → 64.66 ft | difference −2.00 ft (GIS shallower, because GIS width is larger).
- Back wall → opposite lot line: tax 33.34 ft | GIS = 99.97 − 64.66 = 35.31 ft | difference +1.97 ft.
- Distances to the touched lot lines (215 Place, lot-1 side): 0 ft on both bases | difference 0.
- Footprint share of the lot: tax recorded 66.67% (÷10,075) / tax rectangle 66.66% (÷10,076) | GIS 6,716.67 ÷ 10,387.99 = 64.66% | difference ≈ −2.0 percentage points.
- Apartment/other shares (Q6): UNCHANGED — they depend on the floor area and the stated 60%, not on the outline | difference 0.
I do NOT choose between the bases; the folder holds no survey/deed to resolve the ~3.1 ft frontage and ~313 sq ft area conflict.

=== PART 4 of 5 — Q6: AREA ALLOCATION; Q7: WHAT IS MISSING ===

Q6. ALLOCATION at the one stated share. "60% apartment area … an assumption, not a measurement; it applies to the proposed building's residential floor area … The rest is other building area: core, circulation, walls and services" [F]. The building is all-residential, so residential floor area = zoning floor area = 20,150 total; plate = 6,716.67/storey.
- Apartment area: per storey 0.60 × 6,716.6667 = 4,030.00 sq ft; total 0.60 × 20,150 = 12,090 sq ft [C, derived].
- Other building area: per storey 0.40 × 6,716.6667 = 2,686.67 sq ft; total 0.40 × 20,150 = 8,060 sq ft [C, derived].
- Sum to the plate: 4,030.00 + 2,686.67 = 6,716.67 sq ft = plate ✓. Sum to the total: 12,090 + 8,060 = 20,150 sq ft = total ✓ [C].
- Measure/basis: zoning floor area, DERIVED (floor area × the stated 60% assumption). What this does NOT establish: the number or size of dwelling units; the physical floor plate (no gross-up, exclusions or wall-thickness worked); any layout; that the building fits the lot; or any compliance. The 60% is an assumption at the low end of a 60–75% band, not a measurement [F].

Q7. WHAT IS MISSING.
Sections / defined terms the texts I used point to that the folder does NOT hold (pointing words → what stays NOT KNOWN/conditional):
- "located within an #outer court#" (23-431(b), 23-433(b), 35-631(b)) — the "outer court" definition is not in the folder; affects only the recess rules, which this flush-wall placement does not use → not load-bearing here [?].
- "#Mandatory Inclusionary Housing areas#" and "#UAP developments#" (23-432 footnotes) — not in the folder; the R6B row carries no footnote, so not load-bearing [?].
- "encroachments … permitted by the New York City Administrative Code" (23-431(d), 23-433) — the Administrative Code is not in the folder; not load-bearing for this placement [?].
Missing FACTS about the real lot that an answer turned on:
- No survey/deed/zoning-lot description → the tax-map vs GIS conflict (frontage 100.76 vs 103.879 ft; area 10,075/10,076 vs 10,387.99 sq ft) is unresolved; Q3/Q5 figures stay basis-split [?].
- The adjoining zoning lot's lot-line kind along the strip beyond 100 ft of the 215 Place street line (23-344(c)) → the rear-yard answer stays NOT KNOWN [?].
- Whether lots 1 and 70 are one zoning lot → Z1 is a condition, not a fact; a different zoning lot would move lot lines, lot area and the corner geometry [F/?].
- No base plane / curb level / ground elevations → the 30-ft height "as measured from #base plane#" (23-342) and the 75-ft rear-yard threshold cannot be tied to a datum from the folder [?].
- Whether a Commercial District is mapped along the entire 215 Place block frontage (35-633(b)) → the narrow-street street-wall mandate stays NOT KNOWN [?].
- Whether a prevailing street wall frontage exists (needs neighbour street-wall heights/depths) → which street-wall rule governs, 23-431(a) line-up vs (b) percentage, stays NOT KNOWN [?].
- The true Northern Blvd/215 Place intersection angle (used ~89.7° from GIS for the 135° tests) is not surveyed → the corner-lot/23-344(a) angle findings are conditional on the GIS geometry [?].
- The SW end of the block / the 2021 "ALLEY" feature kind → whether the Northern Blvd frontage is a "short dimension of a block" (23-344(b)) is unresolved [?].

=== PART 5 of 5 — Q8: TABLE OF EVERY QUANTITY + ONE-LINE SUMMARIES ===

name | value | unit | basis | computed from
Northern Blvd mapped width | 100 | ft | administrative_record | DCM City Map Streetwidth (streets file)
215 Place mapped width | 60 | ft | administrative_record | DCM City Map Streetwidth (streets file)
Wide-street threshold | 75 | ft | law | zr-12-10-street-wide (≥75 wide)
Narrow-street threshold | <75 | ft | law | zr-12-10-street-narrow
R6B min base height | 30 | ft | law | zr-23-432 R6B row
R6B max base height | 45 | ft | law | zr-23-432 R6B row
R6B max building height | 55 | ft | law | zr-23-432 R6B row
Building height | 30 | ft | filing_attribute | stated fact (3 storeys × 10 ft; from base plane not datum-tied)
Total zoning floor area | 20,150 | sq ft | derived | stated (= recorded lot area 10,075 × 2.00 per settled)
Plate (per storey) | 6,716.67 | sq ft | derived | 20,150 ÷ 3
Tax-map frontage (width) | 100.76 | ft | printed_tax_map | tax map label lot 70 (= PLUTO lotfront)
Tax-map lot depth | 100 | ft | printed_tax_map | tax map label lot 70 (= PLUTO lotdepth)
Recorded lot area | 10,075 | sq ft | filing_attribute | PLUTO lotarea
Tax rectangle area | 10,076 | sq ft | derived | 100.76 × 100
Plan depth (tax) | 66.66 | ft | derived | 6,716.6667 ÷ 100.76
Rounded footprint (tax) | 6,716.66 | sq ft | derived | 66.66 × 100.76 (0.01 under plate)
Back wall → opposite line (tax) | 33.34 | ft | derived | 100 − 66.66
Dist. to 215 Place / lot-1 side line | 0 | ft | derived | placement (walls on those lines)
Bldg far corner from corner point (tax) | 120.81 | ft | derived | √(100.76² + 66.66²)
GIS Northern Blvd frontage | 103.879 | ft | gis | lot-70 ring edge P1–P2
GIS depth edges | 99.976 / 99.975 | ft | gis | lot-70 ring edges
GIS measured lot area | 10,387.99 | sq ft | gis | shoelace of lot-70 ring
GIS reach from Northern Blvd | 99.97 | ft | gis | settled; perp. of P0 to P1–P2
GIS reach from 215 Place | 103.93 | ft | gis | settled; perp. of P0 to P2–P3
GIS reach from corner point | 144.60 | ft | gis | settled; diagonal P2→P0
GIS corner interior angle | 89.69 | degrees | gis | vectors P2→P1, P2→P3
Plan depth (GIS) | 64.66 | ft | derived | 6,716.6667 ÷ 103.879
Back wall → opposite line (GIS) | 35.31 | ft | derived | 99.97 − 64.66
Footprint share ÷ recorded area | 66.67 | % | derived | 6,716.67 ÷ 10,075
Footprint share ÷ tax rectangle | 66.66 | % | derived | 6,716.67 ÷ 10,076
Footprint share ÷ GIS area | 64.66 | % | derived | 6,716.67 ÷ 10,387.99
Corner-lot max lot coverage | 100 | % | law | zr-23-362(a)
Interior-lot max lot coverage | 80 | % | law | zr-23-362(a)
Apartment area / storey | 4,030.00 | sq ft | derived | 0.60 × 6,716.6667
Apartment area total | 12,090 | sq ft | derived | 0.60 × 20,150
Other building area / storey | 2,686.67 | sq ft | derived | 0.40 × 6,716.6667
Other building area total | 8,060 | sq ft | derived | 0.40 × 20,150

ONE-LINE SUMMARIES:
Q1 — R6B/C2-2: wide-street (Northern Blvd) street wall mandatory (≥70% within 8 ft, to 30 ft); narrow-street (215 Place) wall not mandatory unless a whole-frontage commercial condition holds (NOT KNOWN); no front yard; no side yard (open area along a side line ≥5 ft); rear yard NOT KNOWN; lot coverage 100% corner / 80% interior by portion; no setback at 30 ft.
Q2 — Plate = 20,150 ÷ 3 = 6,716.67 sq ft (derived).
Q3 — Tax basis: 100.76 ft wide × 66.66 ft deep (rounded footprint 6,716.66, 0.01 sq ft under the plate); 33.34 ft to the back lot line; touches the Northern Blvd, 215 Place and lot-1 lot lines; 0 ft to those.
Q4 — Placement sits on all three touched lines (0 ft), front/side yards 0 (none required), footprint 66.67% of the recorded lot (mostly corner portion, a sliver in the interior portion); no compliance verdict.
Q5 — GIS widens the frontage to 103.879 ft (+3.12), shallows the plan to 64.66 ft (−2.00), lengthens the back-wall gap to 35.31 ft (+1.97) and lowers the coverage share to 64.66% (−2.0 pts); shares unchanged; conflict left unresolved.
Q6 — At 60%: apartment 4,030.00/storey (12,090 total), other 2,686.67/storey (8,060 total); sums to the plate and total; establishes no units, layout, physical plate or compliance.
Q7 — Missing: "outer court" definition, MIH/UAP terms, Admin Code (not load-bearing); and facts — no survey/deed resolving the tax-vs-GIS conflict, the adjoining lot-line kind, the zoning-lot identity, the base plane/elevations, the 215 Place whole-frontage commercial condition, a prevailing street wall frontage, the surveyed corner angle, and the block's SW/ALLEY edge.
Q8 — Table above; every quantity carries one basis.

END-OF-REPORT
