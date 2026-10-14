# Independent reading from the step-P7 sealed folder, reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-11, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the 189 pinned law-text captures (without their notes), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, ten made-up boundary cases M1 to M10, and FOUR answers settled by earlier readings (copied word for word and given as settled, so completed readings are reused and not worked again) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1 of the step-P7 pair (an official-source-researcher); a value is recorded in the short-block-rear-yard reference case only where this reading and reading 2 (return-independent-hand-calculation-16.md) give the same answer on the same basis.

---

PART 1 of 7

DRAFT AI READING — NOT LEGAL ADVICE, NOT A PROFESSIONAL REVIEW. This is one AI reader's hand-reading of captured New York City Zoning Resolution (ZR) text and stated facts. It is not a legal interpretation of record, not professional zoning/legal review, and gives NO verdict that any building or lot complies with the law.

THE ONE HARD RULE — OBEYED. I worked only inside the sealed folder /root/project/lanes-runtime/owner-docs/session-2026-10-11d/sealed-p7-v2 and wrote only in my scratch folder /root/project/lanes-runtime/owner-docs/session-2026-10-11d/reader-p7-1b. I opened no web page, ran no web search, opened nothing else under /root/project, wrote no agent memory, and did not look for any earlier reader's work.

FILES I READ (all inside the sealed folder):
law/: zr-23-34, zr-23-341, zr-23-342, zr-23-343, zr-23-344; zr-12-10-short-dimension-of-a-block, -block, -street, -street-line, -lot-line-front, -lot-line-rear, -lot-line-side, -zoning-lot, -lot-corner, -lot-through, -lot-interior, -public-park, -lot-depth, -yard, -yard-rear, -yard-equivalent-rear, -yard-side, -yard-front (.json each). I also listed the full law/ directory (189 files) and the facts/ directory.
facts/: made_up_boundary_lots.json, settled_by_earlier_readings.json, pluto_rows_lots_70_and_1.json, printed_tax_map_labels.json, zoning_nyzd_query_R6B.json, zoning_nyco_query_C2-2.json, block_7334_lot_outlines_epsg2263.json, streets_dcm_centerlines.json.
My scratch scripts (arithmetic/geometry only): geom.py, classify.py, blockdim.py, centresep.py, reach.py, attrs.py, farend.py, show.py.

Markers on lines below: [F] fact from the folder; [S] from settled_by_earlier_readings.json; [C] calculation/conclusion from quoted text; [?] NOT KNOWN from the captured text.

=================================================================
Q1. ZR 23-344(b) AND THE DEFINITIONS IT USES
=================================================================

23-344(b), quoted (file zr-23-344.json):
"(b) Along #short dimension of a block# — In the districts indicated, whenever a #front lot line# of a #zoning lot# coincides with the #street line# of the #short dimension of a block#, no #rear yard# shall be required within 100 feet of such #street line#"
The section header line is "R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12" and the chapeau says it modifies the #rear yard# requirements of 23-342 and the #rear yard equivalent# requirements of 23-343. [F]

Definitions it uses that the folder holds (quoting first words, since list labels in the capture may be markup positions, not printed labels):
- "short dimension of a block" (zr-12-10-short-dimension-of-a-block.json): "The 'short dimension of a block' shall be a #block# frontage where the dimension between any two #streets# bounding the #block# measures less than 230 feet." [F]
- "front lot line" (zr-12-10-lot-line-front.json): "A 'front lot line' is a #street line#." [F]
- "street line" (zr-12-10-street-line.json): "A 'street line' is a #lot line# separating a #street# from other land. A #street setback line# supersedes the #street line# in the application of #yard#, height and setback, and #court# regulations." [F]
- "zoning lot" (zr-12-10-zoning-lot.json): "A 'zoning lot' is either: (a) a lot of record existing on December 15, 1961...; (b) a tract of land... located within a single #block#, which, on December 15, 1961... was in single ownership; (c) a tract of land... consisting of two or more lots of record contiguous for a minimum of 10 linear feet... under single fee ownership...; or (d) a tract of land... declared to be a tract of land to be treated as one #zoning lot#... A #zoning lot#, therefore, may or may not coincide with a lot as shown on the official tax map..." [F]
- "rear yard" (zr-12-10-yard-rear.json): "A 'rear yard' is a #yard# extending for the full length of a #rear lot line#." [F]
- "yard" (zr-12-10-yard.json): "A 'yard' is that portion of a #zoning lot# extending open and unobstructed from the lowest level to the sky along the entire length of a #lot line#, and from the #lot line# for a depth or width set forth in the applicable district #yard# regulations..." [F]
- "block" (zr-12-10-block.json): see Q1c. [F]
- "street" (zr-12-10-street.json): a way established on the City Map; or a ≥50-ft public way connecting two City-Map ways and covenanted open; or other CPC-approved ≥50-ft public open area; or a pre-12/15/1961 public way; or a certified covered pedestrian space; with private roads/driveways excluded. [F]

Q1a — What exactly is measured for "short dimension of a block"?
[C] The text fixes only three things: (i) the thing measured is "the dimension between any two #streets# bounding the #block#"; (ii) the comparison value is "less than 230 feet"; (iii) the result ("short dimension of a block") is itself "a #block# frontage."
[?] Between WHAT the dimension is taken — street lines, street centrelines, or lot lines — is NOT STATED. The words are "between any two #streets#," and a "street" is a way/area, not a line; the definition does not say street line, centreline, or lot line, and does not say along which line to measure. Missing: an express measurement reference and method. (The best textual reading is that a #block# is "a tract of land bounded by #streets#," so the land's dimension runs between the bounding #street lines#; but the definition itself does not say "street line," so I keep the basis open.)
[C] "less than 230 feet" IS strict: the words are "less than," so exactly 230.00 does not qualify; only < 230 qualifies.
[?] "block frontage" is used but is NOT separately defined in the folder.

Q1b — What does "within 100 feet of such #street line#" mean for a point on the lot?
[C] 23-344(b) says only "no #rear yard# shall be required within 100 feet of such #street line#." The natural reading is a perpendicular distance from that street line into the zoning lot.
[?] The text does not state the measurement method expressly (perpendicular from the street line vs. some other path), and does not say whether exactly 100 feet is inside or outside the band ("within 100 feet" — inclusive or exclusive at the 100-ft line). Missing: the measurement method and the treatment of the exact-100-ft boundary. These matter in made-up cases M5/M6 below.

Q1c — Which features can bound a block? Park? Private way? (zr-12-10-block.json)
"A 'block' is a tract of land bounded by: (a) #streets#; (b) #public parks#; (c) railroad rights-of-way, when located at or above ground level but not including sidings or spurs in the same ownership as the #zoning lot#; (d) airport boundaries; (e) pierhead lines (or shore lines where no pierhead lines have been established); or (f) corporate boundary lines of New York City." [F]
[C] A public park CAN bound a block (item (b)). "Public park" (zr-12-10-public-park.json): "any publicly owned park, playground, beach, parkway or roadway within the jurisdiction and control of the Commissioner of Parks and Recreation, except for park strips or malls in a #street#..."
[C] A PRIVATE WAY is NOT in the list and so cannot bound a block as a private way. It could bound a block only if it independently qualifies as a "#street#" (e.g., a way established on the City Map, or a ≥50-ft public way meeting the street definition) — and the street definition expressly says "a #private road#, or a driveway that serves only to give vehicular access to an #accessory# parking or loading facility... shall not be considered a #street#." [C]

PART 2 of 7

=================================================================
Q2. ZR 23-344(c), ESPECIALLY (c)(3)
=================================================================
Quoted (zr-23-344.json):
"(c) Beyond one hundred feet of a #street line# — In all districts, as indicated, for #interior# or #through lot# portions of #corner lots#, and for #zoning lots# bounded by two or more #streets# that are neither #corner lots# nor #through lots#, the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply along such #rear lot line#:
(1) In all districts, a #rear yard# shall be provided in accordance with Section 23-342 (Rear yard requirements), where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#.
(2) In R1 through R5 Districts, a #rear yard# with a minimum depth of five feet shall be provided where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#.
(3) In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#." [F]

Definitions (c) relies on that the folder holds:
- "corner lot" (zr-12-10-lot-corner.json): "A 'corner lot' is either a #zoning lot# bounded entirely by #streets#, or a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle formed by the extensions of the #street lines#... forms an angle of 135 degrees or less... The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable." [F]
- "through lot" (zr-12-10-lot-through.json): "A 'through lot' is any #zoning lot#, not a #corner lot#, which adjoins two #street lines# opposite to each other and parallel or within 45 degrees of being parallel to each other..." [F]
- "interior lot" (zr-12-10-lot-interior.json): "An 'interior lot' is any #zoning lot# neither a #corner lot# nor a #through lot#." [F]
- "side lot line" (zr-12-10-lot-line-side.json): "A 'side lot line' is any #lot line# which is not a #front lot line# or a #rear lot line#." [F]
- "rear lot line" (zr-12-10-lot-line-rear.json): "A 'rear lot line' is any #lot line# of a #zoning lot# except a #front lot line#, which is parallel or within 45 degrees of being parallel to, and does not intersect, any #street line# bounding such #zoning lot#." [F]

Q2a — Which lots/portions does (c) speak to; what becomes a rear lot line; from which street line is 100 ft measured?
[C] (c) speaks to two kinds: (i) the "#interior# or #through lot# portions of #corner lots#" (i.e., the parts of a corner lot outside the within-100-ft-of-each-street-line corner portion), and (ii) "#zoning lots# bounded by two or more #streets# that are neither #corner lots# nor #through lots#."
[C] What becomes a rear lot line: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects." So only the far portion (beyond 100 ft) of a side lot line is reclassified, and only a side lot line that actually INTERSECTS a street line.
[C] From which street line the 100 ft is measured: from "the #street line# that it [that side lot line] intersects" — each reclassification is keyed to the specific street line the side lot line meets, not to any street line generally.

Q2b — What decides between (c)(1) and (c)(3)? Does the adjoining lot's district matter, or only its lot line's kind?
[C] The deciding factor is the KIND of the ADJOINING #zoning lot#'s lot line that the reclassified #rear lot line# coincides with:
 • coincides with a #rear lot line# of the adjoining #zoning lot# → (c)(1), a #rear yard# per 23-342 (all districts);
 • coincides with a #side lot line# of the adjoining #zoning lot# → (c)(2) in R1–R5 (5-ft minimum) or (c)(3) in R6–R12 (no #rear yard#).
[C] So the branch among (1)/(2)/(3) turns on (a) the adjoining lot's lot-line KIND, and (b) OUR OWN district (R1–R5 vs R6–R12). The text attaches NO condition to the ADJOINING lot's district; its district is not mentioned. Only its lot line's kind matters, plus the subject lot's own district.

=================================================================
Q3. HOW 23-342, 23-343, 23-344(a)/(b)/(c) FIT TOGETHER
=================================================================
[F] 23-342 ("In all districts, #rear yards# shall be provided on #interior lots# in accordance with this Section, except as otherwise provided pursuant to the provisions of Section 23-34, inclusive.") sets the base rear-yard rule for interior lots. 23-343 does the same for #rear yard equivalents# on #through lots#, with the same "except as otherwise provided... Section 23-34" carve-out. 23-344's chapeau: the 23-342 rear-yard and 23-343 rear-yard-equivalent requirements "shall be modified as set forth in this Section."
[C] So 23-344(a)–(d) are modifications of the 23-342/23-343 base requirements. (a) = no rear yard within 100 ft of a corner (two street lines at ≤135°); (b) = no rear yard within 100 ft of the short-dimension street line; (c) = beyond-100-ft reclassification for corner-lot interior/through portions and for multi-street non-corner/non-through lots; (d) = the multiple-rear-lot-line case.

Can more than one modification apply to one lot?
[C] Yes. The modifications are listed together and keyed to different geometry/zones; nothing makes them mutually exclusive. In particular (a) (within 100 ft of a corner) and (c) (beyond 100 ft of a street line) address complementary portions of the SAME corner lot, so both can bear on one corner lot.

Does (b) apply to a corner lot?
[C] The text of (b) is not limited to any lot type: "whenever a #front lot line# of a #zoning lot# coincides with the #street line# of the #short dimension of a block#." A corner lot has front lot lines (each front lot line is a street line). If one of them coincides with the short-dimension street line, (b) applies. Nothing in (b) excludes corner lots.

Where (b) applies, does (c) still matter beyond 100 ft?
[?] PARTLY NOT KNOWN. (b) exempts rear yards "within 100 feet of such [short-dimension] #street line#." (c) is keyed to a point/portion "beyond 100 feet of the #street line# that [a side lot line] intersects." A single area can be within 100 ft of ONE street line (so (b) exempts it) and at the same time beyond 100 ft of ANOTHER street line (so (c) may reach it). The captured text states NO priority or conflict rule between (b) and (c) for such an overlap. So where they overlap I preserve the conflict: under (b) no rear yard is required in that overlap, while (c) read alone might require one; the folder's text does not say which governs. Missing: an express ordering/override rule between 23-344(b) and (c).

PART 3 of 7

=================================================================
Q4. THE MADE-UP CASES M1–M10 (all plain R6B unless stated; "street" = mapped street of the stated width)
=================================================================
Framework used for every case: (b) applies only if the lot's front lot line is on a street line that is the short-dimension frontage's street line, i.e., the block frontage whose between-two-streets dimension is < 230 ft (strict). (c) speaks only to interior/through portions of corner lots and to multi-street non-corner/non-through zoning lots.

M1 — [F] Block rectangle; X,Y parallel, 229.99 ft apart measured between their FACING STREET LINES; P,Q cross at right angles, 600 ft apart; P frontage runs X→Y. Lot: interior, front lot line on P, 50 ft along P, 100 ft deep, touches neither X nor Y.
[C] The P frontage runs from X to Y; the dimension between the two streets (X,Y) bounding that frontage is 229.99 ft, measured between street lines. 229.99 < 230 (strict) → the P frontage IS a short dimension of the block. The lot's front lot line is on the P street line = the street line of the short dimension. → (b) APPLIES.
[C] Where no rear yard is required under (b): within 100 ft of the P street line. The lot is 100 ft deep from P, so the entire lot lies within 100 ft of the P street line → no rear yard required anywhere on this lot under (b).
[C] (c): the lot is a plain interior lot fronting a single street (touches neither X nor Y), so it is neither a corner-lot portion nor a multi-street lot → (c) does NOT speak to it.

M2 — [F] As M1 but X,Y 230.00 ft apart. Lot as M1.
[C] Dimension between X,Y = 230.00, which is NOT "less than 230 feet" (strict) → the P frontage is NOT a short dimension. → (b) does NOT apply. (No (b) exemption; any rear-yard duty on the interior lot's back rear lot line is governed by 23-342, not asked here.) (c) does not speak to it (single-street interior lot).

M3 — [F] As M1 but X,Y 230.01 ft apart.
[C] 230.01 > 230 → not a short dimension → (b) does NOT apply. (c) does not speak to it. (M1/M2/M3 together confirm the strict "< 230": 229.99 yes, 230.00 no, 230.01 no.)

M4 — [F] As M1 but the X–Y distance is 229.80 ft from the printed tax-map labels and 230.20 ft on a city GIS outline; no survey exists.
[?] Which measurement to use is NOT KNOWN. The short-dimension definition says only "the dimension... measures less than 230 feet"; it does NOT say which record governs (tax-map label vs GIS outline vs survey) or the method. On the tax-map figure 229.80 < 230 → (b) would apply; on the GIS figure 230.20 > 230 → (b) would not. The result therefore flips with the source. Missing: an authoritative/survey X–Y dimension and any rule in the captured text fixing the measurement source. So (b)'s applicability to M4 is NOT KNOWN (conditional: applies on 229.80, not on 230.20). (c) does not speak to it (single-street interior lot).

M5 — [F] Block: X,Y parallel 200 ft apart; P,Q 600 ft apart; P frontage runs X→Y. Lot: interior, front on P, 50 ft along P, 100.00 ft deep.
[C] Dimension between X,Y = 200 < 230 → P frontage is a short dimension → (b) APPLIES.
[C] Where no rear yard required: within 100 ft of the P street line. The lot is exactly 100.00 ft deep, so its back (rear) lot line sits exactly 100.00 ft from the P street line.
[?] Whether that rear lot line at EXACTLY 100.00 ft is "within 100 feet" is NOT KNOWN — see Q1b: the text does not say whether exactly 100 ft is inside the band. So: the part of the lot strictly inside 100 ft → no rear yard; at exactly 100 ft (the rear lot line) the exemption's reach is NOT KNOWN. (c) does not speak to it (single-street interior lot).

PART 4 of 7

M6 — [F] As M5 but the lot is 100.03 ft deep. (b) APPLIES (200 < 230). [C] The portion within 100 ft of the P street line → no rear yard. But the lot's rear lot line is at 100.03 ft, which is BEYOND 100 ft of the P street line, so (b)'s "no rear yard... within 100 feet" does NOT reach it. → a rear yard IS required at that rear lot line under 23-342 (the (b) exemption stops at 100 ft). This is the M5↔M6 contrast: at 100.00 ft the boundary is NOT KNOWN; at 100.03 ft the rear lot line is outside the band and the exemption does not cover it. (c) does not speak to it (single-street interior lot).

M7 — [F] Block as M5 (X,Y 200 apart; P,Q 600). Lot: a CORNER lot at P∩X, 100 ft along P and 150 ft along X; street lines meet at 90°; its other two lot lines adjoin interior lots.
Lot-line kinds as the definitions give them (corner at origin; P along one axis, X along the other; lot = the rectangle 100 ft deep from X and 150 ft deep from P):
[C] edge on P = #front lot line# (a street line). edge on X = #front lot line# (a street line). The edge perpendicular to P (100 ft from the X street line, opposite X) INTERSECTS the P street line at the P-end, so it is not a rear lot line → #side lot line#. The edge parallel to P at the back (150 ft from P) touches the X street line at its end, so it intersects a bounding street line → not a rear lot line → #side lot line#. Net: 2 front + 2 side + 0 rear. (Same shape family as the real corner lot.)
[C] (b): the P frontage (length = X→Y = 200) is a short dimension; the X frontage (length = P→Q = 600) is not. The lot's P front lot line coincides with the short-dimension (P) street line → (b) APPLIES → no rear yard within 100 ft of the P street line. The lot reaches 150 ft from the P street line, so the strip from 100 to 150 ft from P is beyond (b)'s band.
[C] (c): the lot is a corner lot; the portion beyond 100 ft of the P street line is its interior/through portion. The side lot line perpendicular to P intersects the P street line; its portion beyond 100 ft of P is reclassified as a #rear lot line#. Being R6B (an R6 district), (c)(3) gives "no #rear yard#" IF that reclassified rear lot line coincides with a #side lot line# of the adjoining #zoning lot#; (c)(1) requires a rear yard if it coincides with a #rear lot line# of the adjoining zoning lot.
[?] The fact says only that this edge "adjoins interior lots"; it does not state the adjoining interior lot's frontage street or its lot-line kind at the shared edge. If that neighbor fronts P (the natural row configuration), the shared edge is the neighbor's #side lot line# → (c)(3) → no rear yard. But the neighbor's frontage/lot-line kind is NOT STATED → the (c)(1)-vs-(c)(3) result on the beyond-100-ft strip is NOT KNOWN. Missing: the adjoining zoning lot's lot-line kind at the shared line.

M8 — [F] Block as M5. ONE zoning lot of two adjoining tax lots: tax lot A = corner at P∩X, 100 ft along P and 100 ft along X; tax lot B = interior, next to A along X, 50 ft along X and 100 ft deep; recorded as one zoning lot.
[C] Because A and B are ONE #zoning lot#, the A/B tax boundary is INTERNAL and is not a #lot line#; the whole is analysed as one lot. The combined lot is the same 100-ft-from-X by 150-ft-along-X corner shape as M7. Lot-line kinds: edge on P = #front lot line#; edge on X (A's + B's X frontages combined) = #front lot line#; edge perpendicular to P opposite X = #side lot line# (intersects the P street line); back edge parallel to P = #side lot line# (touches the X street line). 2 front + 2 side + 0 rear.
[C] (b): P frontage short (200 < 230); combined lot's P front lot line = short-dimension street line → (b) APPLIES → no rear yard within 100 ft of the P street line.
[C]/[?] (c): same reclassification as M7 for the beyond-100-ft portion of the P-intersecting side lot line; (c)(3) in R6 gives no rear yard if it coincides with a #side lot line# of the adjoining zoning lot. M8 states nothing about what adjoins the far (x>100) edge, so the adjoining lot's lot-line kind there is NOT KNOWN → the (c) result on that strip is NOT KNOWN. The teaching point M8 settles: the internal A/B line is NOT a lot line, so no rear yard arises from it.

PART 5 of 7

M9 — [F] Block bounded by streets X and Y (parallel, 220 ft apart), street P crossing them at one end, and a PUBLIC PARK closing the block at the other end (~600 ft from P). Lot: interior, front lot line on P, 50 ft along P, 100 ft deep.
[C] Does the park bound the block? YES. The block definition item (b) lists "#public parks#" as a feature that can bound a block, so a public park is a valid block boundary. (The fact states it is a public park; I take that as given.)
[C] Short dimension: the definition compares "the dimension between any two #streets# bounding the #block#." The streets bounding this block are X, Y and P (the park is not a street). The P frontage runs from X to Y; the dimension between those two streets is 220 ft < 230 → the P frontage IS a short dimension. The park at the far end does not disturb this, because the qualifying dimension is between two STREETS (X and Y).
[C] The lot's front lot line is on the P street line = the short-dimension street line → (b) APPLIES → no rear yard within 100 ft of the P street line; the lot is 100 ft deep, so (subject to the exact-100 boundary question of Q1b) the whole lot is within the band → no rear yard required anywhere under (b).
[C] (c): single-street interior lot → (c) does NOT speak to it.

M10 — [F] Four-sided block: streets X and Y are NOT parallel (210 ft apart where they meet P, 250 ft apart where they meet Q); P and Q are 500 ft apart. Lot: interior, front on P, 50 ft along P, 100 ft deep.
[?] How the dimension is to be measured is NOT KNOWN for non-parallel bounding streets. The short-dimension definition gives a single value "the dimension between any two #streets#" but states no method when the two streets converge, so the X–Y dimension is not single-valued (210 ft at the P end, 250 ft at the Q end). Reading "the dimension" as the length of the P frontage (X→Y at the P end) gives 210 < 230, which would make the P frontage a short dimension and (b) apply; the Q frontage at 250 > 230 would not. But the captured text does not fix which measure (frontage length vs perpendicular distance vs minimum/maximum/average) controls for non-parallel streets. So, conditionally: if the measure is the P-frontage span (210), (b) APPLIES and no rear yard is required within 100 ft of the P street line (whole 100-ft-deep lot); but the measurement method is NOT KNOWN, so the applicability of (b) is NOT KNOWN. Missing: a rule in the captured text for measuring "the dimension between" non-parallel streets. (c) does not speak to it (single-street interior lot).

Summary of (b) applicability across M1–M10: M1 yes (229.99<230); M2 no (230.00); M3 no (230.01); M4 NOT KNOWN (229.80 vs 230.20, source not fixed); M5 yes (200), exact-100 rear-line boundary NOT KNOWN; M6 yes (200) but rear lot line at 100.03 is beyond the band → rear yard required there; M7 yes via P, beyond-100 strip → (c), neighbour kind NOT KNOWN; M8 yes via P, internal A/B line is not a lot line, beyond-100 strip → (c), neighbour NOT KNOWN; M9 yes (220 between X,Y), park validly bounds the block; M10 NOT KNOWN (non-parallel streets, measurement method not fixed). (c) speaks only to M7 and M8 (corner lots); M1–M6, M9, M10 are single-street interior lots outside (c)'s scope.

PART 6 of 7

=================================================================
Q5. THE REAL LOT — 215-16 Northern Boulevard, Queens, tax lot 70 of block 7334 (BBL 4073340070), corner of Northern Boulevard and 215 Place, R6B with a C2-2 overlay. Z1 = lot 70 alone is the zoning lot; Z2 = lots 70 and 1 together are one zoning lot (which is true is NOT KNOWN).
=================================================================
All coordinates are EPSG:2263 (NAD83 / New York Long Island, US survey feet) per the facts files. My geometry scripts are in the scratch folder (geom.py, classify.py, blockdim.py, centresep.py, reach.py, attrs.py, farend.py).

Q5a — Bounding streets, widths, and block dimensions.
[F] Street centrelines (streets_dcm_centerlines.json), all Feat_Type "Mapped_St", Feat_status "City_St": Northern Boulevard mapped width 100 ft; 215 Place 60 ft; 215 Street 60 ft; nearby 45 Road 50 ft and 45 Drive 50 ft; 46 Avenue 80 ft.
[C] From the tax-lot outlines (block_7334_lot_outlines_epsg2263.json) and addresses, the block is clearly bounded on three sides: Northern Boulevard (100 ft) on the short NE end (lots 1 and 70, addresses "215-10 / 215-16 NORTHERN BOULEVARD"); 215 Street (60 ft) along the NW long side (lots addressed "45-xx 215 STREET"); 215 Place (60 ft) along the SE long side (lots addressed "45-xx 215 PLACE"). Each of these three centrelines runs ~28–30 ft outside the corresponding lot-outline edges, consistent with being the bounding streets.
[?] The SW short end (opposite Northern Boulevard) is NOT cleanly resolved by the folder: the nearest captured cross-streets are 45 Road (50 ft) and 45 Drive (50 ft) running roughly E–W near the block, and 46 Avenue (80 ft) lies ~126 ft beyond the farthest lots; and a 2021 tax-map ALLEY label sits inside the block. Which single feature bounds the SW end is NOT KNOWN from the folder.
Block dimensions (my projection of all lot vertices onto the Northern-Boulevard-frontage axis and its perpendicular, blockdim.py):
- SHORT direction (between 215 Street and 215 Place, i.e., the span of the Northern Boulevard frontage): [C] about 203 ft on the street-line / lot-outline basis (lot 1 corner to lot 70 corner, straight = 203.13 ft; sum of PLUTO/tax-map frontages 99.25 + 100.76 = 200.01 ft); [C] 260.02 ft between the 215 Street and 215 Place CENTRELINES (centresep.py). I state I measured the street-line/lot-outline value from the tax-lot outline corners (which the settled sheet confirms lie on the street lines) and the centreline value between the two mapped centrelines; the centreline exceeds the street-line value by the two centreline-to-lot offsets (27.87 + 29.02 ft).
- LONG direction (Northern Boulevard to the SW end): [C] about 545 ft on the lot-outline basis — far above 230 on any basis.
[C] Could the ALLEY bound the block? Only if it is a feature in the block definition — a #street#, #public park#, railroad right-of-way, airport boundary, pierhead/shore line, or NYC corporate line. [F] The tax-map labels file says "whether the ALLEY is a mapped street, a private way or something else is not stated." [C] A private way is not a block boundary and is excluded from "#street#." So the ALLEY could bound the block ONLY IF it qualifies as a #street# (or another listed feature); on the folder's facts that is NOT established → NOT KNOWN.

Q5b — Is the Northern Boulevard frontage a "short dimension of a block"? Is lot 70's front lot line on that street line? Is a rear yard required within 100 ft of the Northern Boulevard street line (Z1 and Z2)?
[C] Short-dimension test, by basis: street-line/lot-outline span ≈ 200–203 ft < 230 → the Northern Boulevard frontage IS a short dimension; tax-map labels 200.01 ft < 230 → IS a short dimension; centreline span 260.02 ft > 230 → is NOT a short dimension. So the determination is BASIS-DEPENDENT; the law does not fix the basis (Q1a). My best textual reading is the street-line basis (a block is "a tract of land bounded by #streets#," so its dimension runs between the bounding street lines), on which the Northern Boulevard frontage is the short dimension; but I keep the centreline result visible as an unresolved alternative.
[S] Lot 70 is a corner lot with two front lot lines — the Northern Boulevard edge and the 215 Place edge — two side lot lines, and NO rear lot line (settled: real-lot lot-lines). So lot 70's Northern Boulevard front lot line coincides with the Northern Boulevard street line.
[S] The whole lot is within 100 ft of the Northern Boulevard street line (max reach 99.97 ft); a strip ~3.93 ft wide (~390 sq ft) lies beyond 100 ft of the 215 Place street line; ~2,560 sq ft lies beyond 100 ft of the corner point (settled: real-lot reach). [C] I independently reproduced these from the outline (reach.py): max perpendicular reach from the Northern Boulevard edge 99.975 ft, from the 215 Place edge 103.932 ft, from the corner point 144.601 ft — matching the settled values.
Z1 (lot 70 alone):
[C] If the Northern Boulevard frontage is the short dimension (street-line/tax-map basis) → 23-344(b) applies: no rear yard required within 100 ft of the Northern Boulevard street line. Since the whole lot is within 100 ft of that street line, no rear yard is required anywhere on the lot under (b). (Independently, the lot has NO rear lot line [S], and 23-344(a) requires no rear yard within 100 ft of the corner — the Northern Boulevard/215 Place street lines meet at ~90° ≤ 135°, which I confirmed from the edge directions.)
[?] If the Northern Boulevard frontage is NOT the short dimension (centreline basis) → (b) does not apply; then no rear yard is required within 100 ft of the corner under (a), and because there is no rear lot line, a rear-yard duty can arise only through (c)'s reclassification on the beyond-100-ft sliver (see Q5c), which is NOT KNOWN.
Z2 (lots 70 + 1 together):
[C] Lot 1 also fronts Northern Boulevard and reaches ~99.98 ft deep from it (my classify.py: lot 1's 215-Street and shared edges are ~99.98 ft), so the combined lot is likewise entirely within ~100 ft of the Northern Boulevard street line, and the combined Northern Boulevard front lot line coincides with the short-dimension street line on the street-line/tax-map basis → (b) applies → no rear yard required anywhere on the combined lot on that basis. On the centreline basis (b) does not apply and the outcome tracks (a) + (c) as in Z1. [C] Under Z2 the lot 70/lot 1 shared edge becomes INTERNAL to the zoning lot and is not a lot line.

PART 7 of 7

Q5c — The part beyond 100 ft of a street line.
[S] Every point of the lot is within 100 ft of the Northern Boulevard street line (reach ≤ 99.97 ft), so NO point is beyond 100 ft of THAT street line. A ~3.93-ft sliver (~390 sq ft) is beyond 100 ft of the 215 PLACE street line.
[C] (c) applies to the interior portion of this corner lot — the part outside the within-100-ft-of-each-street-line corner portion. The back side lot line intersects the 215 Place street line (at the far-from-Northern-Blvd corner); its portion beyond 100 ft of the 215 Place street line (the ~3.93-ft sliver near the back corner) is, under (c), "considered a #rear lot line#." Being R6B (R6), (c)(3) gives "no #rear yard#" IF that reclassified rear lot line coincides with a #side lot line# of an adjoining #zoning lot#; (c)(1) requires a rear yard if it coincides with a #rear lot line# of an adjoining zoning lot.
[F] Geometrically (attrs.py) the lot(s) adjoining lot 70's back edge are tax lot 11 (address "45-12 215 PLACE", fronting 215 Place) along the main back segment and tax lot 61 ("45-11 215 STREET", fronting 215 Street) at the small back-corner segment where the sliver sits.
[?] But the adjoining #zoning lot#'s lot-line KIND cannot be fixed: the folder gives no zoning for any lot other than lot 70, no zoning-lot descriptions, and a tax lot is not necessarily a zoning lot. If tax lot 11 is a zoning lot fronting 215 Place, the shared edge is its side lot line → (c)(3) → no rear yard; but that treats the tax lot as a zoning lot and assumes its frontage — neither is established. So whether a rear yard is required on the sliver is NOT KNOWN.
[?] There is also the unresolved (b)-vs-(c) overlap (Q3): the sliver is within 100 ft of the Northern Boulevard street line (so (b) says no rear yard) yet beyond 100 ft of the 215 Place street line (so (c) reaches it). The captured text gives no priority rule → NOT KNOWN which governs. Under Z2 the same analysis holds; lot 1 may add a mirror sliver beyond 100 ft of the 215 Street street line, with the same NOT-KNOWN neighbour question.

Q5d — Real-lot result in one table.
Variant (Z1/Z2 × basis) | rear yard required? where? | deciding words | fact that would settle it
- Z1, street-line/tax-map basis: NO rear yard anywhere within 100 ft of the Northern Boulevard street line (= whole lot). | 23-344(b) "no #rear yard# shall be required within 100 feet of such #street line#"; settled reach (whole lot ≤ 99.97 ft). | the measurement basis for "short dimension" (whether the ~200–203 ft street-line span governs).
- Z1, centreline basis: within 100 ft of the corner, NO rear yard; on the ~3.93-ft sliver beyond 100 ft of the 215 Place street line, NOT KNOWN. | 23-344(a) "no #rear yard#... within 100 feet of the point of intersection"; 23-344(c)(3)/(c)(1). | the adjoining zoning lot's lot-line kind at the sliver; plus the (b)/(c) overlap rule.
- Z2, street-line/tax-map basis: NO rear yard anywhere within 100 ft of the Northern Boulevard street line (= whole combined lot). | 23-344(b), same words. | the measurement basis; and whether 70+1 are one zoning lot.
- Z2, centreline basis: within 100 ft of the corner(s), NO rear yard; slivers beyond 100 ft of the 215 Place / 215 Street street lines, NOT KNOWN. | 23-344(a), (c)(3)/(c)(1). | adjoining zoning lots' lot-line kinds; the (b)/(c) overlap rule; the zoning-lot question.

Q5e — What changes if the dimension is measured on a different basis. Basis-dependent answers:
[C] (1) The numeric short dimension itself: ~200.01 ft (tax-map) / ~203.13 ft (street-line, lot outline) / 260.02 ft (centreline). (2) Whether the Northern Boulevard frontage is a "short dimension of a block" (yes on street-line/tax-map, no on centreline). (3) Whether 23-344(b) applies to the real lot, under both Z1 and Z2. (4) Whether "no rear yard anywhere within 100 ft of the Northern Boulevard street line" rests on (b) (street-line/tax-map) or must instead rest on (a) + the absence of a rear lot line + (c) (centreline). (Separately, the Northern Boulevard frontage LENGTH differs by basis — GIS edge 103.88 ft vs PLUTO/tax-map 100.76 ft — but both keep the span < 230, so that difference does not flip the short-dimension conclusion on the street-line/tax-map basis.)

=================================================================
Q6. WHAT IS MISSING
=================================================================
Pointed-to texts the folder does NOT hold (pointing words ≤25 words), and the answer each leaves open:
[?] "#street setback line#" — street-line def: "A #street setback line# supersedes the #street line# in the application of #yard#... regulations." Not captured; if one exists on the City Map, yard measurement could shift. (Affects Q1/Q5b-c if any applies — none shown, but its existence is unverified.)
[?] "block frontage" / "frontage" — used in the short-dimension definition; no definition captured. Leaves Q1a/Q4/Q5b partly open on exactly what a "frontage" is.
[?] 23-342 shallow-lot and standard-lot specifics are captured, but 23-344(d) and (a) interactions beyond the quoted text are only as captured; no missing section blocks the asked (a)/(b)/(c) analysis.
Missing FACTS about the real lot that answers turned on:
[?] The authoritative measurement basis / a survey for the 215 Street–215 Place span (tax-map 200.01 vs street-line 203.13 vs centreline 260.02) — decides whether (b) applies.
[?] Whether lots 70 and 1 are one zoning lot (Z1 vs Z2) — no zoning-lot description, deed, or declaration in the folder.
[?] The zoning district and lot-line classification of EVERY other lot on the block (only lot 70's R6B/C2-2 is given) — decides (c)(1) vs (c)(3) on the beyond-100-ft sliver.
[?] The status of the ALLEY (mapped street / private way / other) and the identity of the SW-end bounding feature — decides the far-end block boundary.
[?] Whether exactly 100 ft counts as "within 100 feet," and the method of measuring "within 100 feet" and "the dimension between any two streets" — decides boundary cases (M5, M10, and the sliver).

=================================================================
Q7. ONE-LINE SUMMARY PER QUESTION
=================================================================
Q1: 23-344(b) gives no rear yard within 100 ft of the short-dimension street line; "< 230 ft" is strict, but the text does not fix whether the dimension or the 100 ft is measured between street lines, centrelines or lot lines (NOT KNOWN); public parks can bound a block, a mere private way cannot.
Q2: 23-344(c) reclassifies the beyond-100-ft portion of a side lot line (of a corner lot's interior/through portion, or a multi-street non-corner/non-through lot) into a rear lot line; (c)(1) vs (c)(3) turns on the ADJOINING lot's lot-line kind plus the subject lot's own district, not the adjoining lot's district.
Q3: 23-344(a)/(b)/(c) all modify the 23-342/23-343 base and more than one can apply to one lot; (b) is not limited to any lot type (so it can apply to a corner lot); where (b) and (c) overlap beyond/within 100 ft of different street lines the text sets no priority (NOT KNOWN).
Q4: (b) applies in M1 (229.99<230), M5, M9 (220 between the two streets), yes-but-rear-line-beyond-band in M6, via P in M7/M8 (with the beyond-100 strip governed by (c) and the neighbour's lot-line kind NOT KNOWN); (b) does not apply in M2 (230.00) or M3 (230.01); M4 and M10 are NOT KNOWN because the measurement source/method is not fixed; (c) speaks only to the corner lots M7 and M8, and M8 shows the internal A/B line is not a lot line.
Q5: On the street-line/tax-map basis the Northern Boulevard frontage (~200–203 ft < 230) is the short dimension and 23-344(b) requires no rear yard anywhere within 100 ft of the Northern Boulevard street line (the whole lot, Z1 and Z2); on the centreline basis (~260 ft) (b) does not apply and the result falls to (a) plus (c), with the ~3.93-ft sliver beyond 100 ft of the 215 Place street line NOT KNOWN because the adjoining zoning lot's lot-line kind is not in the folder; no compliance verdict is given.
Q6: The decisive gaps are the authoritative short-dimension measurement basis, whether lots 70+1 are one zoning lot, the other lots' zoning and lot-line kinds, the ALLEY/SW-end status, and the exact-100-ft and measurement-method questions.
Q7: This is a draft AI reading of captured ZR text and stated facts only, with every unresolved input kept NOT KNOWN and no compliance conclusion.

END-OF-REPORT
