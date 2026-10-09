# Independent reading from the step-P3 sealed folder, reading 2 (provenance)

What this is: one of two independent readings made on 2026-10-07, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, and three made-up lots - with no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2 of the step-P3 pair; a value is recorded in a step-P3 reference-case row only where this reading and reading 1 (return-independent-hand-calculation-7.md) give the same answer on the same basis.

---

PART 1 of 7

This is a DRAFT READING of law text by an AI. It is NOT legal advice and NOT a professional review. Nothing here is a verified zoning determination; every captured file is an "extracted_draft."

ONE HARD RULE: I obeyed it. I read ONLY the sealed folder `.../scratchpad/sealed-p3` and wrote only small arithmetic/geometry scripts in my own scratch folder `.../scratchpad/reader-p3-2`. I opened nothing under /root/project and no other /tmp folder. I have NO web access, so where a text the folder lacks is needed I say NOT KNOWN (I opened no official page).

FILES I READ
Facts (6): facts/lot_facts_pluto.json, facts/lot_outline_epsg2263.json, facts/made_up_lots.json, facts/streets_dcm_centerlines.json, facts/zoning_nyco_query_C2-2.json, facts/zoning_nyzd_query_R6B.json; plus INDEX.json.
Law (43): zr-12-10-lot-line-front, -lot-line-rear, -lot-line-side, -lot-width, -lot-depth, -street-line, -zoning-lot, -lot-corner, -lot-interior, -lot-through, -base-plane, -floor-area, -residence-or-residential, -special-density-areas, -manhattan-core, -special-downtown-brooklyn-district; zr-12-10 (wide/narrow street); zr-11-25; zr-23-342, -23-343, -23-344, -23-41, -23-411, -23-43, -23-432, -23-434, -23-435, -23-436, -23-362, -23-23, -23-231, -23-232, -23-233, -23-234; zr-34-11, -34-21, -34-111, -34-112, -34-113, -34-24; zr-35-63, -35-633. (The folder's other files I did not need and did not rely on.)
Marks on each line: [F]=fact from the folder, [C]=calculation/conclusion from quoted text, [?]=NOT KNOWN from the captured text.

KEY RECORDED FACTS I USE
[F] District R6B, overlay C2-2, splitzone false, borough QN, cd 411, lotarea 10075 sq ft, lotfront 100.76, lotdepth 100.0 (lot_facts_pluto.json). "lottype"=3 but its meaning is "NOT given here" [?].
[F] Lot outline, EPSG:2263 US survey feet, ring (lot_outline_epsg2263.json): P1(1048810.23,216310.44), P2(1048788.63,216408.05), P3(1048889.92,216431.10), P4(1048911.58,216333.50), P5(1048812.40,216310.93), closing to P1.
[F] Street mapped widths (streets_dcm_centerlines.json, "Streetwidth"=mapped City-Map width, free-text, feet): Northern Boulevard 100; 215 Place 60; 215 Street 60; 45 Road 50.
[C] Edge lengths/orientations (my geom.py): P1-P2 (west) 99.98 ft @102.5deg; P2-P3 (north) 103.88 ft @12.8deg; P3-P4 (east) 99.98 ft @-77.5deg; P4-P5 (south) 101.71 ft @-167.2deg; tiny P5-P1 2.22 ft. Shoelace area = 10,387.99 sq ft (= MapPLUTO Shape__Area) — this exceeds PLUTO lotarea 10,075 by 313 sq ft (~3%); I flag the two official area figures disagree.
[C] Which edge faces which street (perpendicular distance from each corner to each street centerline, vs half-width): P2 and P3 lie ~51 ft from the Northern Blvd centerline (half of 100 = 50) -> north edge P2-P3 is the Northern Blvd frontage/street line. P3 and P4 lie ~29 ft from the 215 Place centerline (half of 60 = 30) -> east edge P3-P4 is the 215 Place frontage/street line. West edge P1-P2 and south edge P4-P5 are not on any street (215 Street lies ~80-130 ft west; not adjacent).
So the real lot is a CORNER lot fronting Northern Boulevard (north) and 215 Place (east); the two street lines meet at vertex P3 = the corner point; interior angle at P3 = 89.69deg [C].

=====================================================================
Q1. LOT LINES, LOT WIDTH, LOT DEPTH

Definitions (quoted verbatim; file names given):
- "A 'front lot line' is a street line." (zr-12-10-lot-line-front)
- "A 'rear lot line' is any lot line of a zoning lot except a front lot line, which is parallel or within 45 degrees of being parallel to, and does not intersect, any street line bounding such zoning lot." (zr-12-10-lot-line-rear)
- "A 'side lot line' is any lot line which is not a front lot line or a rear lot line." (zr-12-10-lot-line-side)
- "'Lot width' is the mean horizontal distance between the side lot lines of a zoning lot." (zr-12-10-lot-width)
- "'Lot depth' is the mean horizontal distance between the front lot line and rear lot line of a zoning lot. In the case of a corner lot, the lot depth is the greater of the mean horizontal distances between the front lot lines and the respective side lot line opposite each." (zr-12-10-lot-depth)
- "A 'street line' is a lot line separating a street from other land. A street setback line supersedes the street line..." (zr-12-10-street-line)
- "A 'corner lot' is either a zoning lot bounded entirely by streets, or a zoning lot which adjoins the point of intersections of two or more streets and in which the interior angle formed by the extensions of the street lines ... forms an angle of 135 degrees or less. ... The portion of such zoning lot subject to the regulations for corner lots is that portion bounded by the intersecting street line and lines parallel to and 100 feet from each intersecting street line. Any remaining portion ... shall be subject to the regulations for a through lot or for an interior lot..." (zr-12-10-lot-corner)
- "An 'interior lot' is any zoning lot neither a corner lot nor a through lot." (zr-12-10-lot-interior)
- "A 'through lot' is any zoning lot, not a corner lot, which adjoins two street lines opposite to each other and parallel or within 45 degrees of being parallel to each other..." (zr-12-10-lot-through)

Q1a - the real lot's lot lines:
[C] It is a corner lot: it adjoins the intersection of two streets at P3 and the interior angle there is 89.69deg, i.e. "135 degrees or less" (zr-12-10-lot-corner).
[C] FRONT lot lines (each is a street line, zr-12-10-lot-line-front): north edge P2-P3 (Northern Boulevard) and east edge P3-P4 (215 Place).
[C] The west edge P1-P2 and the south edge P4-P5(-P1) are NOT front lot lines. Testing the rear-lot-line words: the west edge is ~parallel (0.03deg) to the 215 Place street line and does not intersect it, BUT it DOES intersect the Northern Blvd street line (they share P2); the south edge is ~parallel to the Northern Blvd street line and does not intersect it, BUT it DOES intersect the 215 Place street line (share P4). 
[?] The bare phrase "does not intersect ... ANY street line bounding such zoning lot" (zr-12-10-lot-line-rear) is ambiguous for a corner lot: read as "intersects NO street line," neither edge qualifies as a rear lot line (each touches one of the two); read as "parallel to and not intersecting SOME street line," both would qualify. Standing alone, the definition does not settle it. 
[C] However, the corner clause of zr-12-10-lot-depth ("the respective SIDE lot line opposite each [front lot line]") and zr-23-344(c) ("for interior or through lot portions of corner lots ... the portion of a SIDE lot line beyond 100 feet of the street line that it intersects shall be considered a rear lot line") both treat a corner lot's non-front edges as SIDE lot lines. Reading the definitions together, I classify: west edge P1-P2 and south edge P4-P5(-P1) = SIDE lot lines; the lot has NO rear lot line (subject to the 23-344 conversion in Q2). I flag the isolated-definition ambiguity above.

Q1b - real-lot width and depth:
[?] LOT WIDTH: method = "mean horizontal distance between the side lot lines." The two side lot lines here (west @102.5deg, south @12.8deg) are ~perpendicular, not opposing/parallel, so there is no single "mean horizontal distance between" them; the method presupposes two opposing side lines (as on an interior lot). For this two-frontage corner lot the words do not yield a lot width -> NOT KNOWN. (PLUTO "lotfront" 100.76 is a PLUTO frontage field, not the ZR "lot width.")
[C] LOT DEPTH (corner rule = greater of the two front-to-opposite-side mean distances; my geom2.py): Northern Blvd front (P2-P3) to opposite south side (P4-P5) = 99.98 ft; 215 Place front (P3-P4) to opposite west side (P1-P2) = 103.90 ft. Greater = 103.90 ft. So lot depth ~= 103.9 ft. (PLUTO "lotdepth"=100.0; the ZR corner method gives ~103.9 ft.) What it leaves undecided: it depends on first fixing "the respective side lot line opposite each" front (the Q1a classification).

Q1c - made-up interior lot 40 x 100 (40 ft on the street):
[C] Front lot line = the 40-ft street edge (a street line). Rear lot line = the opposite 40-ft edge (parallel to and not intersecting the street line). Side lot lines = the two 100-ft edges.
[C] Lot width = mean distance between the two side (100-ft) lines = 40 ft. Lot depth = mean distance between front and rear = 100 ft.

PART 2 of 7

Q2. REAR YARD
Controlling words:
- zr-23-342 (banner "R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12"): "In all districts, rear yards shall be provided on interior lots in accordance with this Section... (a) Standard lots ... (1) For detached and zero lot line buildings, for buildings or portions ... at or below 75 feet ... a rear yard with a depth of not less than 20 feet ... at every rear lot line ..., and for portions above 75 feet ... 30 feet ...; (2) For semi-detached and attached buildings: (i) for zoning lots with a lot width of less than 40 feet ... 30 feet ...; (ii) for zoning lots with a lot width of 40 feet or greater ... at or below 75 feet ... 20 feet ..., and ... above 75 feet ... 30 feet. (b) Shallow lots ... where an interior lot is less than 95 feet deep ... [and the shallow condition existed on 12/15/1961] ... reduced by six inches for each foot ... less than 95 feet ... in no event ... less than 10 feet."
- zr-23-343 (through lots): "(a) Exceptions ... (1) to any through lots that extend less than 110 feet in maximum depth from street to street; (2) to large sites; (3) ...; (4) ... occupying an entire block. (b)(1) For standard lots On any through lot that is 190 feet or more in maximum depth ... at or below 75 feet, a rear yard equivalent ... minimum depth of 40 feet ..., and above 75 feet ... 60 feet. (b)(2) For shallow lots ... where a through lot is less than 190 feet deep ... reduced by one foot [per foot] ... less than 190 feet ... in no event ... less than 20 feet. (c)(1) Standard location ... midway, or within 10 feet of being midway, between the two street lines ... (c)(2) Alternative location allowances [only] for zoning lots utilizing ... Section 23-434, the tower regulations of Section 23-435, or other ... provisions ... for R10 Districts without a letter suffix, or for shallow lots eligible for ... (b)(2) ..."
- zr-23-344: "(a) Within one hundred feet of corners ... no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less. ... (c) Beyond one hundred feet of a street line In all districts ... for interior or through lot portions of corner lots, and for zoning lots bounded by two or more streets that are neither corner lots nor through lots, the portion of a side lot line beyond 100 feet of the street line that it intersects shall be considered a rear lot line and the following rules shall apply ...: (1) ... a rear yard shall be provided in accordance with Section 23-342, where such rear lot line coincides with a rear lot line of an adjoining zoning lot. ... (3) In R6 through R12 Districts, no rear yard shall be required where such rear lot line coincides with a side lot line of an adjoining zoning lot."
[C] R6B is governed by the "R6" entries in 23-342/23-343/23-344 via zr-11-25 ("If a section lists an R4 District ... that section shall also apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with suffixes are listed"); none of these sections lists a separate R6B provision, so they reach R6B.

Q2a - real lot, part more than 100 ft from the corner point:
[C] Corner point = P3. Distance from P3 to each other corner (my geom2.py): P3->P1 = 144.60 ft, P3->P5 = 143.00 ft, P3->P2 = 103.88 ft, P3->P4 = 99.98 ft. FARTHEST corner = P1 at 144.60 ft. So part of the lot lies beyond 100 ft (radially) from the corner point.
[C] Within 100 ft of the corner point: zr-23-344(a) waives the rear yard — the two street lines intersect at 89.69deg, i.e. "135 degrees or less," and R6B is within R6-R12. So NO rear yard is required there.
[C] Beyond 100 ft: zr-23-344(a) does not waive it. zr-23-344(c) uses PERPENDICULAR distance from a street line (not radius). Testing each side lot line: the west side line P1-P2 reaches only 99.98 ft perpendicular from the Northern Blvd street line (P1 at 99.98) -> no portion "beyond 100 feet" -> no rear lot line from it. The south side line P4-P5(-P1) intersects the 215 Place street line at P4 and reaches 101.71 ft (P5) and 103.93 ft (P1) perpendicular from it -> its far ~1.7 ft near P5 (and on to P1) IS "beyond 100 feet" -> that portion "shall be considered a rear lot line."
[?] Whether a rear yard is actually required along that converted rear-lot-line portion depends on the adjoining zoning lot: zr-23-344(c)(1) requires a 23-342 rear yard where it coincides with a neighbour's REAR lot line; (c)(3) requires NONE (R6-R12) where it coincides with a neighbour's SIDE lot line. The neighbour's lot-line type is NOT in the folder.
If a rear yard is required, its depth comes from zr-23-342(a): 20 ft for parts at/below 75 ft, 30 ft above 75 ft (for detached/zero-lot-line, and for semi-detached/attached at lot width >= 40 ft). 
Facts/choices still needed (each named): [?] the adjoining lots' lot-line types along the south side line; [?] the building type (detached / zero lot line / semi-detached / attached); [?] the building height relative to 75 ft measured from base plane; [?] the lot width (undecided per Q1b — matters only for semi-detached/attached <40 ft); [?] whether the C2-2 overlay modifies the yard: zr-34-11/34-21 route residential yards through Section 34-23 "Modification of Yard Regulations," which is NOT in the folder. ([C] R6B-in-R6-R12 via 11-25 is settled, not missing.)

Q2b - made-up interior lot 40 x 100 (lot width 40 ft, depth 100 ft):
[C] zr-23-342(a): depth 100 ft >= 95, so the shallow-lot reduction (b) does not apply. Lot width = 40 ("40 feet or greater"), so:
- Detached or zero lot line building (a)(1): 20 ft at/below 75 ft; 30 ft above 75 ft.
- Semi-detached or attached building (a)(2)(ii) [width >= 40]: 20 ft at/below 75 ft; 30 ft above 75 ft.
- (The <40-ft branch (a)(2)(i) giving 30 ft does NOT apply because width = 40.)
So the rear yard is 20 ft (parts at/below 75 ft) / 30 ft (above 75 ft) in every building-type case for this width. Facts that decide: building type and building height vs 75 ft (base-plane-measured). Width 40 happens to make the type distinction immaterial here.

Q2c - made-up through lot 40 x 200 (street at each end):
[C] zr-23-343: it is a through lot. Depth 200 ft.
- Exceptions (a): 200 ft is NOT "less than 110 feet," so (a)(1) does not exempt it; (a)(2)/(3)/(4) [large sites / block-occupying] not shown to apply -> not exempt.
- Depth (b)(1) standard lots: 200 ft >= 190 ft, so a rear yard equivalent (open area) of minimum depth 40 ft is required for parts at/below 75 ft, and 60 ft above 75 ft (where permitted).
- (b)(2) shallow lots: applies only where "less than 190 feet"; 200 >= 190, so NO reduction.
- Location (c)(1): the rear yard equivalent must be "midway, or within 10 feet of being midway, between the two street lines." The (c)(2) alternative locations are available ONLY to lots using 23-434/23-435/R10-no-suffix/shallow-(b)(2); this plain R6B lot qualifies for none, so only the standard midway location applies.
[C] Threshold placement of 200 ft: ABOVE the 110-ft exemption floor (so not exempt) and AT/ABOVE the 190-ft standard-lot floor (so the full 40/60-ft requirement applies and no shallow reduction). Fact that decides the 40-vs-60 depth: building height vs 75 ft.

Q2d - made-up corner lot 150 (street A) x 100 (street B), part beyond 100 ft of corner point:
[C] Corner point = the A-B street-line intersection; streets meet at a right angle (90deg <= 135deg). Farthest corner = the diagonally opposite corner at sqrt(150^2+100^2) = 180.28 ft from the corner point, so part of the lot is beyond 100 ft (radially).
[C] Within 100 ft of the corner point: zr-23-344(a) waives the rear yard (90deg <= 135deg; R6B in R6-R12).
[C] Beyond 100 ft (zr-23-344(c), perpendicular test): put the corner point at (0,0), street A the bottom edge (y=0, length 150), street B the left edge (x=0, length 100). The side lot line opposite street A is the TOP edge (y=100), which intersects street B's line at (0,100); its portion beyond 100 ft from street B's line is x=100..150 (a 50-ft stretch) -> that stretch "shall be considered a rear lot line." The side lot line opposite street B is the RIGHT edge (x=150), which reaches only y=0..100 from street A's line -> not beyond 100 ft -> no rear lot line from it.
[?] Whether a rear yard is required along that converted top-edge rear-lot-line turns on the neighbour (23-344(c)(1) rear-coincidence -> 23-342 yard; (c)(3) side-coincidence in R6-R12 -> none); the neighbour's lot-line type is NOT in the folder. If required, depth = 20 ft (<=75 ft) / 30 ft (>75 ft) per zr-23-342. Needed: [?] neighbour lot-line type; [?] building type; [?] height vs 75 ft.

PART 3 of 7

Q3. ZR 23-436 AND ZR 35-633

Wide/narrow classification of the real lot's frontages (zr-12-10: "A 'wide street' is any street 75 feet or more in width.... A 'narrow street' is any street less than 75 feet wide."):
[C] Northern Boulevard mapped width 100 ft >= 75 -> WIDE street. 215 Place mapped width 60 ft < 75 -> NARROW street. (215 Street 60 and 45 Road 50 are also narrow but are not the lot's frontages.) The C5-3/C6-4/C6-6 "alternate width" and the Manhattan Broadway/Allen named-street clauses in zr-12-10 do NOT apply (wrong districts/borough: lot is C2-2 in Queens CD 11). Basis note: "Streetwidth" is the mapped City-Map width (free-text field); the ZR test is on street width.

Q3a - zr-23-436 paragraph by paragraph (banner "R6 R7 R8 R9 R10 R11 R12"; "In the districts indicated, the following additional regulations shall apply"):
(a) [quote] "Existing buildings may be vertically enlarged by up to one story or 15 feet without regard to the street wall location requirements of Section 23-431." -> applies to EXISTING buildings vertically enlarged.
(b) [quote] "On through lots which extend less than 190 feet in maximum depth from street to street, the street wall location requirements of Section 23-431 shall be mandatory along only one street frontage." -> applies to short through lots.
(c) [quote] "On corner lots, or portions thereof, the street wall location requirements of Section 23-431 shall be mandatory along only one street frontage. Where one of the street frontages ... is a wide street and the other a narrow street, the street wall location rules shall be applied along the wide street frontage;" -> applies to corner lots (and sets which frontage when wide+narrow).
(d) [quote] "The street wall location and minimum base height provisions of Sections 23-431 and 23-432, respectively, shall not apply along any street frontage of a zoning lot occupied by buildings whose street wall heights or widths will remain unaltered." -> applies to frontages with retained, unaltered street walls.
(e) [quote] "The minimum base height provisions of Section 23-432 shall not apply to buildings, or portions thereof, that are developed or enlarged and do not exceed such minimum base heights." -> applies to new/enlarged buildings that stay below the minimum base height.
(f) [quote] "For any zoning lot located in a Historic District designated by the Landmarks Preservation Commission, the street wall location and minimum or maximum base height regulations ... may be modified ..." (with (1)/(2) varying the base height to an adjacent building's street-wall height) -> applies only in an LPC Historic District.
(g) [quote] "Where a continuous sidewalk widening is provided on the zoning lot, along the entire block frontage of a street, the boundary of the sidewalk widening shall be considered to be the street line ..." -> applies where such a widening is built.

Q3b - which 23-436 paragraphs bind a NEW all-residential building on the real lot:
First, the routing (this matters): zr-34-11 ("C1 C2 C3 C4 C5 C6 ... the bulk regulations of Article II, Chapter 3, shall apply to all residential buildings ... except as modified by ... 34-21 through 34-24") + zr-34-111 (lists "C1-1 ... C2-2 ... C2-5"; "the bulk regulations for the Residence District within which such Commercial Districts are mapped apply") make the R6B Article-II-Chapter-3 rules (including 23-43/23-436) the base for a residential building in this C2-2 overlay; and zr-34-24(b) then says those residential height/setback rules are "modified ... [per] Section 35-63, inclusive," which carries in zr-35-633 (below). So 23-436 is reached, with 23-431 references superseded by 35-631.
Paragraph results for the new building:
(a) DOES NOT APPLY — "Existing buildings"; the building is new. [C]
(b) DOES NOT APPLY — "On through lots"; the real lot is a corner lot, not a through lot. [C]
(c) APPLIES — the lot is a corner lot with a wide frontage (Northern Blvd) and a narrow frontage (215 Place), so the street-wall location requirement is mandatory along only one frontage and, per the wide/narrow rule, along the WIDE Northern Boulevard frontage. [C] (In the overlay, "Section 23-431" is read as Section 35-631 per zr-35-633(a).)
(d) DOES NOT APPLY to a wholly new building — "occupied by buildings whose street wall heights or widths will remain unaltered"; nothing is retained in the stated scenario. [C] (Conditional: would apply only if an existing unaltered street wall were kept — a fact not in the folder.)
(e) CONDITIONAL — turns on design: it relieves the minimum base height (R6B minimum base height = 30 ft, zr-23-432 R6B row) only for a building/portion "that ... do[es] not exceed such minimum base heights." [?] depends on the chosen height.
(f) NOT KNOWN — needs the fact whether the lot is in an LPC-designated Historic District; not in the folder. [?]
(g) CONDITIONAL / does not apply unless such a continuous sidewalk widening is provided; not in the scenario. [?]

Q3c - zr-35-633 paragraph by paragraph (sits under zr-35-63, banner "C1 C2 C4 C5 C6", "In Commercial Districts mapped within, or with a residential equivalent of R6 through R12 Districts"):
Intro [quote] "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows:" -> for zoning lots to which the 35-63 commercial-district height/setback family applies. For the real lot's residential building this is reached via zr-34-24(b)(1) ("the modifications ... set forth in Section 35-63, inclusive, shall be applied"); C2-2 is a C2 district and R6B is within R6-R12 (via 11-25). [C] So 35-633 applies to the real lot and makes 23-436 apply with the two exceptions:
(a) [quote] "references to the street wall location provisions of Section 23-431 shall be superseded by those of Section 35-631" -> APPLIES to the real lot. [C]
(b) [quote] "for ... the street wall modifications on corner lots, where a zoning lot is bounded by only one street line along a street frontage where a Commercial District is mapped along the entire block frontage, the street wall shall be applied along such frontage." -> the lot is a corner lot, but this needs two facts not in the folder: [?] whether a Commercial District (overlay) is mapped along the ENTIRE block frontage of a given street, and which frontage is "bounded by only one street line." The C2-2 overlay query (zoning_nyco_query_C2-2.json) lists overlay polygons but does not establish block-frontage coverage. NOT KNOWN.
Caveat for all of Q3: these captures carry their own "must be confirmed by a qualified zoning professional" notes; the 34-11 -> 34-111 -> 34-24(b) -> 35-63/35-633 -> 23-436 chain is my reading of the quoted words, not a verified determination.

PART 4 of 7

Q4. ZR 34-21 (and 34-11, 34-112, 34-113, 34-111)

Q4a - what zr-34-21 says, and whether it itself changes FAR / lot coverage / yards / dwelling-unit rule for a residential building in a C2-2 district mapped within R6B:
[quote] (zr-34-21, banner "C1 C2 C3 C4 C5 C6") "In the districts indicated, the bulk regulations applicable to residential buildings as set forth in Section 34-11 (General Provisions) are modified by the provisions of Sections 34-22 (Modification of Floor Area Regulations), 34-23 (Modification of Yard Regulations) and 34-24 (Modification of Height and Setback Regulations). The purpose of these modifications is to make the regulations set forth in Article II, Chapter 3, applicable to Commercial Districts."
[C] By its own words, 34-21 changes NOTHING directly. It is a routing/pointer section: it says the residential-building bulk rules are modified by 34-22 (floor area), 34-23 (yards) and 34-24 (height/setback). It states no FAR number, no lot-coverage number, no yard dimension and no dwelling-unit rule itself. So 34-21 does not itself change FAR, lot coverage, yards, or the dwelling-unit rule; it names the three sub-sections that carry any modification.

Q4b - 34-11 names 34-22 and 34-23 (34-11 says "except as modified by ... Sections 34-21 through 34-24"; 34-21 names 34-22, 34-23, 34-24). Are 34-22 and 34-23 in the folder?
[?] NO. The folder holds zr-34-11, zr-34-21, zr-34-24, zr-34-111, zr-34-112, zr-34-113 — but NOT 34-22 and NOT 34-23. 
Pointing words (from zr-34-21): "34-22 (Modification of Floor Area Regulations)" and "34-23 (Modification of Yard Regulations)." 
[?] Without them: how the commercial-district rules MODIFY the residential floor-area (FAR) and the yard regulations stays NOT KNOWN. For the real lot this means the FAR actually allowed and any yard modification (including the rear-yard question in Q2) cannot be read off the folder. (34-24, height/setback, IS in the folder — see Q3.)

Q4c - does zr-34-112 (its table) apply to a C2-2 district mapped within R6B, or is that zr-34-111's case?
[C] It is zr-34-111's case, NOT 34-112's. Deciding words:
- zr-34-111 district line: "C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5" — includes C2-2 — and the title "...whose bulk is governed by surrounding Residence District," with body "In the districts indicated, the bulk regulations for the Residence District within which such Commercial Districts are mapped apply, except that: (a) ... [Greater Transit Zone, R1-R5] ...; (b) ... [R1 or R2] ..." 
- zr-34-112 district line: "C1-6 C1-7 C1-8 C1-9 C2-6 C2-7 C2-8 C3 C4 C5 C6" — does NOT include C2-2 — with body "the applicable bulk regulations are the bulk regulations for the residential equivalent of the Commercial District as set forth in the following table."
[C] C2-2 appears in 34-111's list and not in 34-112's. So for a C2-2 overlay mapped within R6B, the bulk regulations are "the bulk regulations for the Residence District within which such Commercial Districts are mapped" (i.e. R6B), per 34-111; the 34-112 residential-equivalent table does NOT apply, and neither exception (a) (R1-R5) nor (b) (R1/R2) applies because the surrounding district is R6B. (34-113 concerns existing bonused public amenities being eliminated/reduced and is not engaged by a plain new building.)

=====================================================================
Q5. SPECIAL DENSITY AREAS

Definitions:
- zr-12-10-special-density-areas: "'Special density areas' shall refer to special geographies where unique density regulations apply to residential developments or enlargements. Special density areas shall include: (a) the Manhattan Core; and (b) the Special Downtown Brooklyn District."
- zr-12-10-manhattan-core: "The 'Manhattan Core' is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8."
- zr-12-10-special-downtown-brooklyn-district: "The 'Special Downtown Brooklyn District' is a Special Purpose District designated by the letters 'DB' in which special regulations set forth in Article X, Chapter 1, apply."

Facts compared: [F] borough "QN" (Queens), borocode "4", cd "411" (lot_facts_pluto.json); [F] the served PLUTO row has NO spdist1 (listed under "fields_absent_from_the_served_row": "spdist1", "spdist2", "spdist3").

Manhattan Core:
[C] SETTLED: NO. The Manhattan Core is defined as "the area within Manhattan Community Districts 1-8." The lot is in Queens (borough QN, borocode 4), not Manhattan. A Queens lot cannot be within a Manhattan community district, so it is NOT in the Manhattan Core. (The boundary words are a community-district list; the fact compared is the borough = Queens.)

Special Downtown Brooklyn District:
[C] On the recorded facts the lot is outside it: it is in Queens, and the PLUTO row records NO special district (spdist1 absent) — so no "DB" designation is recorded for this lot.
[?] But the DEFINITION itself states no geographic boundary in words: it identifies the district by the zoning-map letters "DB" and points to "Article X, Chapter 1," which is NOT in the folder. So the text's own boundary cannot be checked from the folder; my "outside" conclusion rests on the recorded borough (Queens) and the absence of any spdist, not on a boundary quoted in the definition. What is NOT KNOWN from the text alone: where the "DB" boundary lies (it is on the zoning map / Article X, Chapter 1, not in the folder). For both areas, the density regulations themselves (the "unique density regulations") are not in the folder.

PART 5 of 7

Q6. HOW HEIGHT IS MEASURED

Q6a - from what level do the base heights and the building height of zr-23-432 measure:
[C] From the BASE PLANE. Quoted words:
- zr-23-43: "The height of all buildings or other structures shall be measured from the base plane. For the purposes of this Section, where base planes of different elevations apply to different portions of a building or other structure, each such portion ... may be considered to be a separate building."
- zr-23-432 sets "the minimum base height, maximum base height, and maximum building height" in its table; its paragraph ties base/setback to those base heights. Combined with 23-43, every one of those heights is measured from the base plane.
- zr-12-10-base-plane: "The 'base plane' is a plane from which the height of a building or other structure is measured as specified in certain Sections."
(For the R6B row of the zr-23-432 table: minimum base height 30, standard-residence maximum base height 45, standard-residence maximum building height 55 ft; a separate "qualifying affordable/senior housing" pair 45/65. Which column applies, and the wide/narrow-street footnotes 1/2, depend on #qualifying affordable/senior housing#, #UAP developments#, #Mandatory Inclusionary Housing areas# — terms NOT in the folder [?].)

Q6b - what the base-plane definition needs to know about a lot, and which facts are in the folder for the real lot:
The definition (zr-12-10-base-plane) needs:
1. [C derivable] Whether the building/segment is within or beyond 100 feet of a street line ("For buildings ... within 100 feet of a street line, the level of the base plane is any level between curb level and street wall line level. Beyond 100 feet of a street line, the level ... is the average elevation of the final grade ..."). This is a geometry fact derivable from the outline + street lines: the lot's far corner P1 is ~99.98 ft from the Northern Blvd street line and ~103.9 ft from the 215 Place street line, so parts of the lot are beyond 100 ft of the 215 Place street line. Partly in the folder (geometry) [C].
2. [?] curb level (an elevation) — NOT in the folder.
3. [?] street wall line level — NOT in the folder (depends on building + curb).
4. [?] whether street walls are at least 15 ft wide / the building segments — a building-design fact, NOT in the folder.
5. [?] the average elevation of the final grade adjoining the building "in the manner prescribed by the New York City Building Code for adjoining grade elevation" — NOT in the folder (no topography/grade data).
6. [?] for the optional sloping base plane: street wall line level, rear wall line level, and whether the site slopes >= 5% — NOT in the folder.
7. [C] whether corner-lot or through-lot regulations split the building into portions with separate base planes — the lot IS a corner lot (known), so separate base planes per portion may apply; but the elevations of those planes are unknown.
8. [?] the lot coverage of the proposed building (for the optional lot-coverage-weighted "adjusted base plane") — a design fact, NOT in the folder.
[?] Net: the base-plane ELEVATION cannot be determined from the folder. Only the geometric inputs (within/beyond 100 ft of a street line; corner-lot status) are available; every elevation, grade, curb-level and building-design input is missing.

=====================================================================
Q7. ELIGIBLE SITES

Q7a - which zoning lots may use zr-23-434, and is the term for them defined in the folder?
[quote] (zr-23-434) "R6 R7 R8 R9 R10 R11 R12 ... In the districts indicated, WITHOUT A LETTER SUFFIX, for zoning lots that meet the criteria of paragraph (a) of this Section, the height and setback modifications set forth in paragraph (b) may be applied. ... (a) Eligible sites The provisions of this Section shall apply to zoning lots that meet at least one of the following criteria: (1) zoning lots with a transportation-infrastructure-adjacent frontage; (2) zoning lots where one of the following irregularities exists ... (i) an interior lot ... depth less than 85 feet, or a through lot ... less than 170 feet; (ii) ... depth >= 115 feet (interior) / >= 230 feet (through); (iii) corner lots or other zoning lots with multiple front lot lines where the angle between two front lot lines is more than 15 degrees from being perpendicular; (iv) ... more than 15 degrees from being parallel; (v) ... slope of at least 15 percent ...; or (3) zoning lots that have a lot area of at least 20,000 square feet or occupy an entire block. ..."
[C] So 23-434 may be used by zoning lots in R6-R12 districts WITHOUT a letter suffix that meet at least one paragraph-(a) criterion (plus the combined-lot option where combined lot area exceeds 40,000 sq ft and at least one lot qualifies).
[C] The term for them ("eligible sites" / "eligible zoning lots") is DEFINED INLINE by the criteria in paragraph (a) of this same section (heading "(a) Eligible sites"); it is not a separate zr-12-10 defined term in the folder — only the enabling sub-terms it uses (e.g. #transportation-infrastructure-adjacent frontage#, #large sites#) are pointed to and are NOT in the folder [?].

Q7b - zr-23-362(b): to which lots does its different maximum lot coverage apply; does it apply to every lot of 30,000 sq ft or more?
[quote] (zr-23-362) "(b) For eligible sites In the districts indicated, for zoning lots with buildings UTILIZING the eligible site provisions of Section 23-434 ..., the maximum residential lot coverage of the entire site shall be: (1) 65 percent on zoning lots with a lot area of 30,000 square feet or more that are not large sites; and (2) 50 percent on large sites. ..."
[C] It applies only to zoning lots whose buildings are UTILIZING the 23-434 eligible-site provisions. [C] NO — it does not apply to every 30,000-sq-ft lot: a lot must both be >= 30,000 sq ft AND be utilizing 23-434 (and not be a "large site") to get 65%; a 30,000-sq-ft lot that does not use 23-434 keeps the standard 23-362(a) figures (80% interior/through, 100% corner). [?] "#large sites#" is undefined in the folder.

Q7c - does any of this apply to the real lot (lotarea 10,075 sq ft)?
[C] NO. 23-434 is limited "In the districts indicated, without a letter suffix" — R6B HAS a letter suffix (B), so 23-434 does not reach R6B. Independently, the real lot (10,075 sq ft) also fails criterion (a)(3) ("at least 20,000 square feet or occupy an entire block"). 
[C] 23-362(b) therefore does not apply either (it requires "buildings utilizing ... Section 23-434," which this R6B lot cannot). 
[C] zr-23-435 towers ("In R9 through R12 Districts ...") do not apply to R6B. 
So the real lot's lot coverage is governed by the STANDARD zr-23-362(a): "maximum residential lot coverage for interior lots or through lots shall be 80 percent and ... for corner lots shall be 100 percent" — it is a corner lot, so 100% (per the standard, not the eligible-site provision).

PART 6 of 7

Q8. THE WORD "RESIDENTIAL"

Q8a - "residence" and "residential":
[quote] (zr-12-10-residence-or-residential) "A 'residence' is one or more dwelling units or rooming units, including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas. A residence may, for example, consist of one-family or two-family houses, multiple dwellings, boarding or rooming houses, or apartment hotels. However, residences do not include: (a) such transient accommodations as transient hotels, motels or tourist cabins, or trailer camps; (b) non-profit hospital staff dwellings; or (c) student dormitories, fraternity or sorority student houses, monasteries or convents, long-term care facilities, or other living or sleeping accommodations in community facility buildings or portions of buildings used for community facility uses."
[quote] "'Residential' means pertaining to a residence."
[C] Spaces a residence INCLUDES, per the words: dwelling units or rooming units, AND common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas. (The defined sub-terms #dwelling unit# and #rooming unit# are NOT in the folder [?], so the precise content of those two is not fixed by the folder.)

Q8b - is "residential floor area" a defined term in the folder; and the base of each share in zr-23-23..23-234:
[?] "floor area" IS a defined term in the folder (zr-12-10-floor-area). "RESIDENTIAL floor area" is NOT a defined term in the folder (no such capture), yet it is used as a defined term "#residential floor area#" in zr-23-231.
Going section by section (NOT computing anything):
- zr-23-23 (umbrella): exempts "floor space allocated to building amenities, corridors, refuse storage or disposal, or access to elevated ground floor dwelling units ... from the definition of floor area pursuant to Section 12-10, provided that the provisions of this Section, inclusive, are met." It states NO share/percentage of a floor area itself; it routes to the sub-sections.
- zr-23-231 (amenities) states a SHARE: [quote] "Floor space ... allocated to residential amenities may be exempted from the definition of floor area, in an amount not to exceed FIVE PERCENT OF THE RESIDENTIAL FLOOR AREA OF THE BUILDING." Base named = "the residential floor area of the building." [?] The captured text does NOT settle what that base is: "#residential floor area#" is a defined term absent from the folder, so its exact scope/computation is NOT KNOWN.
- zr-23-232 (corridors) states a SHARE: [quote] "FIFTY PERCENT OF THE FLOOR SPACE OF A CORRIDOR may be exempted ..." (under criteria (a) termination / (b) length <= 100 ft). Base named = "the floor space of a corridor" (the corridor's own floor space). [C] The captured text DOES settle the base of the share (the corridor's floor space); which corridors qualify depends on (a)/(b).
- zr-23-233 (refuse): [quote] "an amount not to exceed a maximum of THREE SQUARE FEET PER DWELLING UNIT in the building." This is an absolute per-dwelling-unit cap, NOT a share of a floor area; so there is no "base of a share" — the measure is settled (3 sq ft x number of dwelling units; #dwelling unit# itself undefined in folder [?]).
- zr-23-234 (elevated ground floor units): [quote] "up to 100 square feet ... for each foot of difference between the floor level of such dwelling units and curb level ... no more than a maximum of 500 square feet ... for each building." Again absolute (per-foot, capped at 500 sq ft), NOT a share of a floor area; settled on its own terms (#curb level# undefined in folder [?]).
[C] So only 23-231 and 23-232 state allowances as a SHARE of a floor area; 23-231's base ("residential floor area of the building") is NOT settled by the folder, while 23-232's base ("floor space of a corridor") IS.

=====================================================================
Q9. WHAT IS MISSING (sections/defined terms pointed to but not in the folder; <=25-word pointer each; and which answers stay NOT KNOWN/conditional)

- Section 23-34 "inclusive" (zr-23-342/23-343: "except as otherwise provided pursuant to ... Section 23-34, inclusive"). -> Q2a/b/c/d conditional: other 23-34 rear-yard provisions unseen.
- Section 34-22 "Modification of Floor Area Regulations" (zr-34-21 names it). -> Q4b NOT KNOWN: FAR modification for the C2-2 lot.
- Section 34-23 "Modification of Yard Regulations" (zr-34-21/34-11 name it). -> Q4b and Q2a NOT KNOWN: whether/how the overlay modifies yards.
- Article X, Chapter 1 (zr-12-10-special-downtown-brooklyn-district: "special regulations set forth in Article X, Chapter 1, apply"). -> Q5: DB boundary/regulations unseen (facts still place the lot outside).
- #residential floor area# (used in zr-23-231 "five percent of the residential floor area of the building"). -> Q8b NOT KNOWN: the base of the 5% share.
- #dwelling unit# and #rooming unit# (zr-12-10-residence: "one or more dwelling units or rooming units"). -> Q8a/8b exact content not fixed.
- #large sites# (zr-23-343(a)(2) "to large sites"; zr-23-362(b)(2) "50 percent on large sites"). -> Q2c and Q7b conditional.
- #qualifying affordable housing#/#qualifying senior housing#/#UAP developments#/#Mandatory Inclusionary Housing areas# (zr-23-432 table columns & footnotes 1-3; zr-23-434 fn 1). -> Q6a: which 23-432 column/row-footnote governs the R6B building.
- #transportation-infrastructure-adjacent frontage# (zr-23-434(a)(1)). -> Q7a: one eligibility criterion unresolvable (moot for R6B anyway).
- #qualifying residential sites#/#Greater Transit Zone# (zr-34-111(a)). -> Q4c: the 34-111 exception (a) can't be fully tested (moot: surrounding district is R6B, not R1-R5).
- #residential equivalent# (zr-34-112 table; zr-35-63). -> Q4c/Q3: used but undefined (moot for C2-2 via 34-111).
- #short dimension of a block# (zr-23-344(b)). -> Q2a/d: the (b) short-block waiver can't be tested; block orientation not in folder.
- #curb level#, #street wall line level#, #rear wall line level#, final grade (NYC Building Code), #street wall#, #building segment#, #abutting buildings# (zr-12-10-base-plane). -> Q6b: base-plane elevation NOT KNOWN.
- #street setback line# (zr-12-10-street-line: it "supersedes the street line"). -> could shift front lot lines/yard measurement if one exists; none recorded (Q1/Q2).
- Section 23-431 (street wall location) IS in the folder (zr-23-431) though I did not need its text; Sections 35-631, 35-632, 35-64, 36-64, 35-71 ARE in the folder. The NEIGHBOUR lot-line facts (adjoining lots' rear/side lot lines) are not a ZR section but are the missing FACTS for Q2a/Q2d.

PART 7 of 7

Q10. ONE-LINE SUMMARY PER QUESTION

Q1a. Corner lot; two FRONT lot lines = Northern Blvd (P2-P3) and 215 Place (P3-P4); the other two edges are SIDE lot lines and there is NO rear lot line (the bare rear-lot-line "any street line" wording is ambiguous in isolation, but the lot-depth corner clause and 23-344(c) resolve it to side lot lines).

Q1b. Lot DEPTH ~= 103.9 ft (corner rule: greater of 99.98 ft and 103.90 ft); lot WIDTH = NOT KNOWN because the two side lot lines are ~perpendicular and the "mean horizontal distance between the side lot lines" method presupposes opposing side lines.

Q1c. Interior 40x100: lot width 40 ft, lot depth 100 ft.

Q2a. Within 100 ft of the corner point (P3) no rear yard is required (23-344(a); 89.69deg <= 135deg, R6B in R6-R12); beyond it (farthest corner P1 = 144.60 ft from P3), a rear yard is required only where 23-344(c) converts the south side line's far portion (beyond 100 ft of the 215 Place street line) into a rear lot line AND it meets a neighbour's REAR lot line (then 20/30 ft per 23-342) — NOT KNOWN because the neighbour's lot-line type, the building type/height, and the overlay yard rule (34-23) are missing.

Q2b. Interior 40x100: rear yard 20 ft at/below 75 ft and 30 ft above 75 ft (same for detached/zero-lot-line and for semi-detached/attached because lot width = 40 >= 40); decided by building type and height vs 75 ft; no shallow-lot reduction (depth 100 >= 95).

Q2c. Through 40x200: not exempt (200 > 110); 200 >= 190 so a rear yard equivalent of 40 ft (<=75 ft) / 60 ft (>75 ft) is required, located midway (±10 ft) between the two street lines; no shallow reduction and no alternative-location option for this plain lot.

Q2d. Corner 150x100: within 100 ft of the corner point no rear yard (23-344(a), 90deg); beyond (farthest corner 180.28 ft away), 23-344(c) makes the top edge from 100-150 ft (beyond 100 ft of street B's line) a rear lot line, and whether a yard is required there (20/30 ft) is NOT KNOWN without the neighbour's lot-line type and the building type/height.

Q3a. 23-436 lists seven additional R6-R12 height/setback provisions: (a) existing-building vertical enlargement, (b) short through lots, (c) corner lots (one frontage; wide beats narrow), (d) retained unaltered street walls, (e) buildings under minimum base height, (f) LPC Historic Districts, (g) continuous sidewalk widening.

Q3b. For the new residential building: (c) BINDS (corner lot; street wall along the WIDE Northern Blvd); (a), (b), (d) DO NOT apply; (e) and (g) are conditional on design; (f) is NOT KNOWN (Historic-District fact missing). Northern Blvd = wide (100 >= 75); 215 Place = narrow (60 < 75).

Q3c. 35-633 makes 23-436 apply (reached for this C2-2/R6B residential building via 34-11 -> 34-111 -> 34-24(b)(1) -> 35-63) with (a) 23-431 references read as 35-631 (APPLIES), and (b) a corner-lot one-frontage rule that is NOT KNOWN because entire-block-frontage commercial-overlay coverage is not in the folder.

Q4a. 34-21 changes nothing itself; it routes residential-building bulk to 34-22 (floor area), 34-23 (yards) and 34-24 (height/setback) "to make ... Article II, Chapter 3, applicable to Commercial Districts."

Q4b. 34-22 and 34-23 are NOT in the folder; so the floor-area (FAR) modification and the yard modification for the C2-2 lot stay NOT KNOWN.

Q4c. 34-112's table does NOT apply to C2-2 within R6B; that is 34-111's case (C2-2 is listed in 34-111: "the bulk regulations for the Residence District within which such Commercial Districts are mapped apply" = R6B); 34-112 lists only C1-6..C2-8/C3-C6.

Q5. Manhattan Core = NO, settled (lot is in Queens, not Manhattan CDs 1-8); Special Downtown Brooklyn District = outside on the recorded facts (Queens, no spdist), but the definition's boundary is the map letters "DB" / Article X Ch 1, which is NOT in the folder.

Q6a. The minimum base height, maximum base height and maximum building height of 23-432 are measured from the BASE PLANE (23-43: "The height of all buildings or other structures shall be measured from the base plane"; base plane = "a plane from which the height ... is measured").

Q6b. The base plane needs: within/beyond 100 ft of a street line (derivable from the folder), and curb level, street wall line level, final-grade elevation, street-wall width/segments, rear-wall-line level/slope, corner/through split, and lot coverage (building-design/elevation facts) — the elevation/design facts are NOT in the folder, so the base-plane elevation is NOT KNOWN.

Q7a. 23-434 may be used only by R6-R12 zoning lots WITHOUT a letter suffix that meet a paragraph-(a) "Eligible sites" criterion (defined inline in the section, not as a separate folder term).

Q7b. 23-362(b)'s lower lot coverage (65% / 50% large sites) applies ONLY to lots with buildings utilizing 23-434 — NOT to every 30,000-sq-ft lot.

Q7c. NO: R6B has a letter suffix, so 23-434 (and therefore 23-362(b)) does not reach it, and the lot (10,075 sq ft) also fails the 20,000-sq-ft threshold; the real lot keeps the standard 23-362(a) coverage (corner lot = 100%).

Q8a. A "residence" = one or more dwelling units or rooming units plus common spaces (hallways, lobbies, stairways, laundry, recreation, storage); "residential" = pertaining to a residence; transient, hospital-staff and community-facility/dormitory accommodations are excluded.

Q8b. "Residential floor area" is NOT a defined term in the folder; of the share provisions, 23-231's base ("five percent of the residential floor area of the building") is NOT settled by the folder, while 23-232's base ("fifty percent of the floor space of a corridor") IS; 23-233 (3 sq ft/dwelling unit) and 23-234 (100 sq ft/foot, max 500) are absolute, not shares.

Q9. Missing (each affects the answers noted in PART 6): 23-34 inclusive; 34-22; 34-23; Article X Ch 1; #residential floor area#; #dwelling unit#/#rooming unit#; #large sites#; #qualifying affordable/senior housing#/#UAP developments#/#Mandatory Inclusionary Housing areas#; #transportation-infrastructure-adjacent frontage#; #qualifying residential sites#/#Greater Transit Zone#; #residential equivalent#; #short dimension of a block#; base-plane sub-terms (#curb level#, #street wall line level#, #rear wall line level#, final grade, #street wall#, #building segment#, #abutting buildings#); #street setback line#; and the non-ZR missing FACTS: the adjoining lots' lot-line types and all site elevation/grade data.

Q10 overall caveat: every captured file is extraction_status "extracted_draft," several carry explicit "confirm with a qualified zoning professional" notes, and the §12-10 definition captures used the documented HTML fallback (print/PDF 504), so list-marker glyphs were not confirmed from the glyph-authoritative channel. This reading is an AI draft of the law text, not a professional review.

END-OF-REPORT
