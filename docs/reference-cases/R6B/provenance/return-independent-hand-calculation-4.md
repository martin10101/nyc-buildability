# Independent reading from the step-P1 sealed folder, reading 2 (provenance)

What this is: the second of two independent readings made on 2026-10-07, by a different AI helper from the one that made reading 1, under the same hard rule - working alone from the sealed folder (the pinned step-P1 law-text captures without their notes, the benchmark lot's recorded official facts and outline, no floor-area-ratio field, no program output) with no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2; a value is recorded in a step-P1 reference-case row only where this reading and reading 1 (return-independent-hand-calculation-3.md) give the same value on the same basis.

---

PART 1 of 4

WHAT THIS IS. This is a draft reading of captured law text by an AI. It is NOT legal advice and NOT a professional/qualified zoning review. Where the captured text does not settle a point I say NOT KNOWN and name what is missing; I do not fill gaps with guesses, typical values or rules of thumb.

ONE HARD RULE — OBEYED. I worked only from the sealed folder .../scratchpad/sealed-p1 (read-only) and wrote only under .../scratchpad/reader2. I did not open, list or search anything under /root/project.

FILES I READ (all under sealed-p1):
- law/INDEX.json; law/zr-12-10-lot-corner.json; law/zr-12-10-lot-interior.json; law/zr-12-10-lot-through.json; law/zr-12-10-lot-area.json; law/zr-23-362.json; law/zr-23-363.json; law/zr-11-25.json; law/zr-23-342.json; law/zr-23-344.json; law/zr-12-10-special-density-areas.json; law/zr-23-52.json
- facts/lot_facts_pluto.json; facts/lot_outline_epsg2263.json; facts/streets_dcm_centerlines.json; facts/zoning_nyzd_query_R6B.json; facts/zoning_nyco_query_C2-2.json
OFFICIAL PAGES I OPENED: none. Every text I needed was in the sealed folder, so I did not fetch from zoningresolution.planning.nyc.gov.
Per the captures' own notes, every law file is an extracted_draft (raw_html_verified=false) and the §12-10 term files used the documented HTML fallback (the whole-page print/PDF returned HTTP 504). I treated only the `verbatim_excerpt` as law text; I did not rely on any `provisions` summary block.

UNITS / CRS. Lot outline and street centerlines are EPSG:2263 (NAD83 / NY Long Island), US survey feet; areas in square feet. [F] (lot_outline_epsg2263.json, streets_dcm_centerlines.json)

A DISCREPANCY TO CARRY THROUGHOUT. [F] The MapPLUTO outline (lot_outline_epsg2263.json, Shape__Area) gives 10,387.99 sq ft; my shoelace of its 5 vertices reproduces 10,387.988 sq ft exactly [C]. [F] The PLUTO tabular row (lot_facts_pluto.json) gives lotarea = 10,075 sq ft, lotfront = 100.76 ft, lotdepth = 100.00 ft. The two official area figures differ by ~313 sq ft (~3%). ZR 12-10 "lot area" = "the area of a #zoning lot#" (zr-12-10-lot-area) [F], but a tax lot need not equal a zoning lot and the two sources disagree; the captures do not resolve which equals the zoning-lot area. I use the OUTLINE geometry for all measurements below (angles, which edges are streets, portion areas) and report the tabular figures only as cross-references. [?] which figure is the operative "lot area" is NOT settled by the captures.

Also: [F] PLUTO lottype = "3", but the facts file states its meaning is NOT given; so I do NOT use lottype to decide lot type. [?] meaning of lottype code "3" NOT KNOWN from captures.

=====================================================================
Q1. LOT TYPE AND THE CORNER PORTION
=====================================================================

Outline vertices (ring, ft) — I label them P0..P4 (P5 closes to P0):
P0 (1048810.232, 216310.440); P1 (1048788.628, 216408.054); P2 (1048889.918, 216431.104); P3 (1048911.575, 216333.501); P4 (1048812.401, 216310.934). [F]

Edge lengths [C]: P0->P1 = 99.98 ft; P1->P2 = 103.88 ft; P2->P3 = 99.98 ft; P3->P4 = 101.71 ft; P4->P0 = 2.22 ft. (P3-P4-P0 is one nearly-straight "bottom" line ≈ 103.93 ft; P4 is a 2.2-ft kink.)

Q1a — which lot lines are street lines, the angle, and the lot type.

Streets recorded (streets_dcm_centerlines.json) [F]: Northern Boulevard (Streetwidth "100", Mjr_st), 215 Place (OBJECTID 11453, width "60"), 215 Street (width "60"), 45 Road (width "50"). Streetwidth is the mapped City-Map width in feet (free-text field).

Matching edges to streets by perpendicular offset from each centerline (half-width = street width / 2) [C]:
- Northern Blvd centerline is 51.08 ft from P1 and 51.03 ft from P2; half-width = 50 ft. So the lot's TOP edge P1->P2 lies on the Northern Boulevard street line (within ~1 ft of the mapped line). [C]
- 215 Place centerline is 29.02 ft from P2 and 28.81 ft from P3; half-width = 30 ft. So the lot's RIGHT edge P2->P3 lies on the 215 Place street line (within ~1 ft). [C]
- 215 Street centerline runs ~80-150 ft WEST of the lot; 45 Road runs ~130-240 ft SOUTH. Neither adjoins the lot. [C] So the LEFT edge (P0->P1) and the BOTTOM edge (P3->P4->P0) are NOT street lines; they are interior/side lot lines. [C]
- Corroboration: the Northern Blvd and 215 Place centerlines share the exact vertex (1048907.267, 216487.365) — i.e. the two streets intersect there — and the lot corner P2 is 58.88 ft from that intersection. [C] So the lot "adjoins the point of intersection of two #streets#."

[F] There is a ~1 ft slack between each lot frontage edge and its mapped centerline-derived street line (two independently digitized datasets). It does not change which edges are streets, but the exact street-line position (hence the exact corner-portion boundary) carries ~1 ft uncertainty. [?]

Angle of the two street lines at the corner. ZR 12-10 "lot, corner" (zr-12-10-lot-corner): a corner lot is one "bounded entirely by #streets#, OR ... which adjoins the point of intersections of two or more #streets# and in which the interior angle formed by the extensions of the #street lines# ... forms an angle of 135 degrees or less." [F-law] The lot is not bounded entirely by streets (two of four sides). Interior angle at P2 between the Northern Blvd line (P2->P1) and the 215 Place line (P2->P3) = 89.69° [C]; the two centerlines meet at 89.6° [C]. 89.69° ≤ 135°.

ANSWER Q1a: Two lot lines are street lines — the top edge P1->P2 (Northern Boulevard) and the right edge P2->P3 (215 Place). They form an interior angle of ~89.7° (≤135°). The lot is a CORNER LOT under ZR 12-10 "lot, corner." [C] (It is not an "interior lot" — zr-12-10-lot-interior: "any #zoning lot# neither a #corner lot# nor a #through lot#" — nor a "through lot" — zr-12-10-lot-through requires adjoining "two #street lines# opposite to each other and parallel or within 45 degrees of being parallel"; here the two streets meet at ~90°, not opposite/parallel.)

Q1b — the corner portion, its area, the remaining portion.

Law (zr-12-10-lot-corner) [F-law]: "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."

So the corner portion = the part of the lot within 100 ft (perpendicular) of BOTH street lines. I measured from the two street LINES, which for this lot are its own frontage edges (top = Northern Blvd line, right = 215 Place line) [method].
- Perp distance from the Northern Blvd street line to the far (bottom) edge: P0 = 99.975 ft, P3 = 99.975 ft (max 99.98). The whole lot is within 100 ft of Northern Blvd, so the line "100 ft parallel to Northern Blvd" does NOT cut the lot. [C]
- Perp distance from the 215 Place street line to the far (left) edge: P1 = 103.878 ft, P0 = 103.932 ft. So the strip between 100 ft and ~104 ft from 215 Place (near the left edge) lies OUTSIDE the corner portion. [C]

Clipping the outline at the line 100 ft parallel to the 215 Place street line (Sutherland-Hodgman) [C]:
- CORNER PORTION area = 9,997.60 sq ft (within 100 ft of 215 Place and within 100 ft of Northern Blvd). [C]
- REMAINING PORTION area = 390.39 sq ft (the strip near the left edge, beyond 100 ft from the 215 Place street line). Sum = 10,387.99 sq ft. [C]

Remaining-portion lot type: it adjoins only ONE street (Northern Blvd, along part of the top edge); its other sides are interior lot lines. A "through lot" needs two opposite streets (zr-12-10-lot-through) — not met — so the remaining portion is subject to INTERIOR-LOT regulations. [C]

HOW MEASURED: corner portion measured as {perp dist ≤ 100 ft from the Northern Blvd street line (top edge P1-P2)} ∩ {perp dist ≤ 100 ft from the 215 Place street line (right edge P2-P3)}, clipped to the outline. Remaining portion = outline minus that.

CAVEATS for Q1b: areas scale with the outline (10,387.99 sq ft); on the PLUTO tabular lotarea (10,075) they would be ~3% smaller [?]. The ~1 ft street-line slack shifts the 100-ft cut by ~1 ft, so the 390-sq-ft remnant is sensitive (a ~1 ft shift changes it by ~100 sq ft). [?] The 100-ft-from-Northern-Blvd line sits 0.025 ft outside the lot; a razor-thin sliver beyond 100 ft from Northern Blvd is within measurement noise and I treat it as none. [?]

PART 2 of 4

Q1c — three made-up right-angle corner lots (two adjacent sides are the street lines "along street A" and "along street B"; the other two sides are lot lines). Right angle = 90° ≤ 135°, so each is a CORNER LOT. Corner portion = within 100 ft of both street lines (the 100×100 square at the corner, per zr-12-10-lot-corner). [C]

C1 = 100 (A) × 100 (B). Depth from A = 100, depth from B = 100. Corner portion = 100×100 = 10,000 sq ft = the WHOLE lot. Remaining portion = 0. One lot type: CORNER. [C]

C2 = 150 (along A) × 100 (along B). Rectangle 150×100 = 15,000 sq ft. Depth perpendicular from street A = side along B = 100 ft; depth from street B = side along A = 150 ft.
- Corner portion = min(100,150) along-A × min(100,100) depth-from-A = 100 × 100 = 10,000 sq ft. [C]
- Remaining portion = 15,000 − 10,000 = 5,000 sq ft (the strip 100-150 ft from street B). [C] It adjoins only street A → INTERIOR-LOT regs. [C]

C3 = 200 (along A) × 120 (along B). Rectangle 200×120 = 24,000 sq ft. Depth from A = 120; depth from B = 200.
- Corner portion = min(100,200) × min(100,120) = 100 × 100 = 10,000 sq ft. [C]
- Remaining portion = 24,000 − 10,000 = 14,000 sq ft (L-shaped). [C] Adjoins at most one street in any part (the inner elbow adjoins none) → INTERIOR-LOT regs. [C]

=====================================================================
Q2. MAXIMUM LOT COVERAGE — District R6B
=====================================================================
R6B reach: zr-23-362 lists "R6 R7 R8 R9 R10 R11 R12". ZR 11-25 (zr-11-25) [F-law]: "All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth in express provisions..." 23-362/23-363/23-342/23-344 list R6 with no separate R6B provision, so by 11-25 they reach R6B. [C] (The capture notes flag this reach to R6B and every overlay/special-district interaction as an advisory professional-review item under ADR-007; the lot also carries a C2-2 overlay (lot_facts_pluto overlay1), whose provisions are NOT captured — they bear on commercial use, not the residential coverage/yard figures below. [?])

Key law (zr-23-362 verbatim): "(a) For standard lots ... the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." [F-law]
(zr-23-363 verbatim) "(b) Within 100 feet of corners ... for #interior# or #through lots#, or portions thereof, within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less, the maximum #lot coverage# shall be 100 percent." [F-law]

A GEOMETRY FACT I use repeatedly: 23-363(b) measures RADIALLY ("within 100 feet of the point of intersection"), whereas the 12-10 corner PORTION is a perpendicular/parallel box ("lines parallel to and 100 feet from each ... #street line#"). For a point Q, perpendicular distance to a street line ≤ straight-line distance to the corner (the corner is on that line). So any remaining portion (by definition beyond 100 ft perpendicular of a street line) is also beyond 100 ft RADIALLY from the corner point. Hence 23-363(b)'s radial-100 zone lies entirely inside the 12-10 corner portion, and never reaches a remaining portion except as a boundary touch. [C]

Q2a — REAL LOT. The lot is a corner lot (Q1). Per 12-10 the corner portion gets corner-lot regs, the remaining portion interior-lot regs.
- CORNER PORTION (9,997.60 sq ft): corner lot → 23-362(a) → 100% max residential lot coverage. [C]
- REMAINING PORTION (390.39 sq ft, interior-lot regs): 23-362(a) → 80%. Does 23-363(b) raise it? I computed the minimum radial distance from the corner point P2 to the remaining-portion polygon = 100.00 ft — it only TOUCHES the 100-ft radial circle at a single boundary point; it has NO area within 100 ft of P2. [C] So 23-363(b) does not apply (a boundary touch, not material overlap). Remaining portion stays 80%. [C]
WHOLE-LOT FIGURE? No — the lot has a remaining portion at a different maximum, so I give it PER PORTION: corner portion 100%, remaining portion 80%. [C]
(The percentages are the law; the areas they apply to carry the lotarea discrepancy and ~1 ft slack from Q1b. [?])

Q2b — C1/C2/C3 in R6B.
C1: whole lot is the corner portion → corner lot → 23-362(a) → 100% for the WHOLE lot (one provision covers it). [C]
C2: corner portion 10,000 sq ft → 100% (corner lot). Remaining 5,000 sq ft → interior → 80%. 23-363(b) check: the remaining rectangle's nearest point to the corner is (100 ft along street A) at exactly 100 ft radial — boundary touch only, no area within 100 ft — so no 100% uplift. PER PORTION: 100% / 80%. [C]
C3: corner portion 10,000 sq ft → 100%. Remaining 14,000 sq ft → interior → 80%. 23-363(b) check: every point of the L-shaped remnant has x>100 or y>100, so radial distance >100 ft (touching only at (100,0) and (0,100)); no uplift. PER PORTION: 100% / 80%. [C]

Q2c — made-up INTERIOR lot 40×100 and THROUGH lot 40×200, R6B. (I read "40×100" as 40 ft wide, 100 ft deep, and "40×200" as 40 ft wide, 200 ft deep, by analogy with the through-lot depth. [assumption])
23-362(a) gives 80% to interior AND through lots. [F-law]
23-363 opening: the 23-362 maximum "may be INCREASED in accordance with the provisions of this Section." So 23-363 can only raise 80%, never lower it, and only if a listed condition is met:
- 23-363(a) Shallow zoning lots: available only for lots "eligible for the #rear yard# modifications for shallow #interior lots# set forth in Section 23-342 ... or the #rear yard equivalent# modifications for shallow #through lots# set forth in Section 23-343." Those shallow modifications require depth less than 95 ft (interior) / 190 ft (through). [F-law] The 40×100 interior lot is 100 ft deep (≥95) and the 40×200 through lot is 200 ft deep (≥190) — NOT shallow by those thresholds — so 23-363(a) gives no increase from the given dimensions. [C] (23-342(b) additionally requires the shallow condition to have existed on 12/15/1961, unchanged — a FACT not given, [?] — but moot here since neither is shallow. Also 23-343 is NOT captured. [?])
- 23-363(b) Within 100 ft of corners: would give 100% to an interior/through portion within 100 ft of a qualifying (≤135°) street intersection — but whether either lot is within 100 ft of such an intersection is a LOCATION fact not given. [?] NOT KNOWN.
- 23-363(c) Along the short dimension of the block: gives 100% within 100 ft of the street line where "a #front lot line# ... coincides with the #street line# of the #short dimension of a block#" — whether the lot's front is on the block's short dimension is a BLOCK-geometry fact not given. [?] NOT KNOWN.
ANSWER Q2c: On the dimensions alone, 23-363 does NOT change the 80% that 23-362 gives (the shallow test (a) fails for both). 23-363 could raise either to 100% under (b) or (c), but only with facts the captures do not supply — the lot's proximity to a qualifying street intersection, and the block's short vs long dimension (and, for (a), the 1961 shallow history). Those stay NOT KNOWN. [C/?]

PART 3 of 4

=====================================================================
Q3. REAR YARD — R6B
=====================================================================
Law (zr-23-342 verbatim): "In all districts, #rear yards# shall be provided on #interior lots# in accordance with this Section ... (a) Standard lots ... (1) For #detached# and #zero lot line buildings#, for #buildings# ... at or below ... 75 feet ... a #rear yard# with a depth of not less than 20 feet shall be provided at every #rear lot line# ... and for portions above 75 feet ... 30 feet ...; and (2) For #semi-detached# and #attached# #buildings#: (i) for #zoning lots# with a #lot width# of less than 40 feet, ... not less than 30 feet ...; and (ii) for #zoning lots# with a #lot width# of 40 feet or greater, ... not less than 20 feet ... [≤75 ft] ... 30 feet [above]." "(b) Shallow lots ... where an #interior lot# is less than 95 feet deep at any point, and the shallow lot condition was in existence on December 15, 1961 ... reduced by six inches for each foot ... less than 95 feet ... in no event ... less than 10 feet." [F-law]
Law (zr-23-344 verbatim): "(a) Within one hundred feet of corners ... no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less. ... (c) Beyond one hundred feet of a #street line# ... for #interior# or #through lot# portions of #corner lots#, and for #zoning lots# bounded by two or more #streets# that are neither #corner lots# nor #through lots#, the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply ...: (1) ... a #rear yard# shall be provided in accordance with Section 23-342 ... where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#. ... (3) In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#." [F-law]

A GAP that touches all of Q3: ZR definitions of #front lot line#, #rear lot line#, #side lot line# and #lot width# are NOT in the captures. So the exact identification of which edge is the "rear lot line" rests on terms I cannot quote. [?]

Q3a — REAL LOT (corner lot; two street lines at 89.69° ≤ 135°).
- 23-344(a) WAIVER: because the Northern Blvd × 215 Place street lines intersect at 89.69° (≤135°), NO rear yard is required within 100 ft (radial) of the corner point P2. [C] Measured radially from P2. Radial distances: P3 = 99.98 ft, P1 = 103.88 ft, P0 = 144.60 ft, P4 = 143.00 ft [C] — so the bulk of the lot (and all of the 9,997.6-sq-ft corner portion) lies within the 100-ft radius and needs no rear yard; the far left/bottom reaches of the lot lie beyond it.
- BEYOND 100 ft — 23-344(c): the lot is a corner lot, so its interior-lot portion is governed by (c). "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line#." The left side lot line (P0-P1) is ≤99.98 ft (perpendicular) from the Northern Blvd street line it meets at P1 — entirely within 100 ft — so no part of it converts. The bottom side lot line (P3-P0) is up to 103.93 ft from the 215 Place street line it meets at P3 — so its far segment (beyond the 100-ft line, near P0/P4) is treated as a #rear lot line#. [C] Along that converted rear lot line, in R6 (R6B) districts: 23-344(c)(3) = NO rear yard if it coincides with the adjoining lot's #side lot line#; 23-344(c)(1) = a rear yard (per 23-342) if it coincides with the adjoining lot's #rear lot line#. Which one holds depends on the NEIGHBOR's configuration — a fact not given. [?] NOT KNOWN.
- DEPTH where a rear yard is required (23-342(a)): depends on building type (detached/zero-lot-line vs semi-detached/attached) and #lot width# — design facts not given. [?] 23-342(b) shallow reduction does not apply: the lot is ~100 ft deep (≥95 ft), and the 12/15/1961 condition is unknown anyway. [C/?]
SUMMARY Q3a: No rear yard within 100 ft (radial) of the corner point P2 (23-344(a)) — covering the corner portion and most of the lot. Along the far segment of the bottom lot line (beyond 100 ft of the 215 Place street line), 23-344(c) governs; whether a rear yard is required there, and its depth, is NOT KNOWN (neighbor configuration, building type, lot width, and the uncaptured lot-line definitions).

Q3b — C2, C3 (remnant lots) and the 40×100 interior lot.
C2 and C3 (corner lots, 90° ≤ 135°): 23-344(a) → NO rear yard within 100 ft radial of the corner point. [C] Beyond that, 23-344(c) converts the portion of a side lot line beyond 100 ft of the street line it intersects into a rear lot line (e.g. for C2, the part of the far "top" side lot line beyond 100 ft from street B; for C3, the far reaches of both non-street sides). Along each, R6 rule (c)(3)/(c)(1) makes a required rear yard depend on the adjoining lot's side-vs-rear line, and any required depth depends on building type and lot width. [?] All of those are facts not given, and the lot-line definitions are uncaptured → the rear-yard outcome beyond the 100-ft radius is NOT KNOWN. [C/?]
40×100 INTERIOR lot (R6B): 23-342 requires a rear yard at every #rear lot line#. [F-law] Taking 40 ft as #lot width# and 100 ft as depth [assumption]: for width = 40 ("40 feet or greater"), both 23-342(a)(1) (detached/zero-lot-line) and (a)(2)(ii) (semi-detached/attached, width ≥40) give the SAME standard — not less than 20 ft at/below 75 ft height, 30 ft above 75 ft (where permitted); only (a)(2)(i) (width <40) would give 30 ft, and width 40 is not <40. [C] So the standard rear yard = 20 ft (≤75 ft) / 30 ft (above). 23-342(b) shallow does NOT apply (depth 100 ≥95; and the 1961 history is unknown anyway). [C/?] A 23-344(a) corner waiver would apply only if this interior lot is within 100 ft of a qualifying street intersection — a location fact not given. [?] NOT KNOWN. The precise rear lot line rests on the uncaptured definition. [?]

PART 4 of 4

Q3c — THROUGH lot 40×200, R6B.
23-342 provides rear yards "on #interior lots#" (opening sentence and (b) both say interior lots). [F-law] A through lot is not an interior lot, so the captured 23-342 does NOT impose its rear yard on a clean 40×200 through lot. The through-lot requirement is the #rear yard equivalent# in Section 23-343 — which is NOT in the captures. [?] 23-344 modifies both 23-342 and 23-343, but 23-344(a) (corner waiver) needs two street lines intersecting at ≤135°; a pure through lot adjoins two OPPOSITE/parallel streets (zr-12-10-lot-through), so (a) does not apply. [C] 23-344(b) (short dimension of block) and (c)/(d) could bear on it given more facts (block short dimension, multiple rear lot lines), which are not given. [?] The 12-10 through-lot definition sends any portion "not or could not be bounded by two such opposite #street lines# and two straight lines ..." to interior-lot regs; a clean rectangle fully bounded by the two opposite streets has no such leftover portion, so 23-342 reaches none of it. [C]
ANSWER Q3c: The CAPTURED text (23-342, 23-344) does not state the through lot's rear-yard requirement. The operative rule is the rear-yard EQUIVALENT of Section 23-343, which is NOT captured. [?] NOT KNOWN from the captures; what is missing is Section 23-343 (and the front/rear/side lot-line definitions). 23-344(a)'s corner waiver does not apply to a pure through lot.

=====================================================================
Q4. SPECIAL DENSITY AREAS
=====================================================================
Q4a — what the definition lists. zr-12-10-special-density-areas (verbatim): "'Special density areas' shall refer to special geographies where unique density regulations apply to #residential# #developments# or #enlargements#. #Special density areas# shall include: (a) the #Manhattan Core#; and (b) the #Special Downtown Brooklyn District#." [F-law] (The term is used in zr-23-52(a)(1): #developments#/#enlargements# of #residences# in #special density areas# have "no applicable #dwelling unit# factor." [F-law])

Q4b — the real lot.
[F] The lot is in Queens: lot_facts_pluto borough "QN", borocode "4", BBL 4073340070, block 7334, cd 411, zipcode 11361; BBL first digit 4 = Queens (also BoroCode 4 in the outline attributes). [F]
[F] The served PLUTO row lists spdist1/spdist2/spdist3 among "fields_absent_from_the_served_row" — no special district is carried in the served fields. (But PLUTO's "spdist" is a special-PURPOSE-district field, not necessarily the ZR "special density areas" term — the two are not shown to be the same. [?])
What CAN be said: the definition's list is closed to exactly two areas, named for Manhattan and for Downtown Brooklyn. The lot is in Queens, a different borough from both names. So on the borough fact it is implausible-to-not within either listed area. [C]
What CANNOT be said / NOT KNOWN: the captures do NOT include the boundary definitions of "#Manhattan Core#" or "#Special Downtown Brooklyn District#" (both are defined terms with their own geographies, not captured). So a rigorous confirmation that this Queens lot is outside both requires those definitions. [?] The fact relied on is Borough = Queens (borocode 4). To settle it definitively, the captured ZR definitions/boundaries of the Manhattan Core and the Special Downtown Brooklyn District are needed.

=====================================================================
Q5. WHAT THE NEW CAPTURES CHANGE vs the earlier reading
=====================================================================
Earlier reader (no corner definition, no 23-342, no 23-363): lot type = corner; coverage and rear yard "not known."

NOW SETTLED by the captures:
1. Lot type = CORNER LOT — grounded in zr-12-10-lot-corner + geometry (two street lines, 89.69° ≤ 135°), not merely asserted. [C]
2. Corner portion vs remaining portion (zr-12-10-lot-corner): corner portion ≈ 9,997.6 sq ft; remaining ≈ 390.4 sq ft, which takes INTERIOR-lot regs. [C]
3. Coverage (zr-23-362 + 11-25): corner portion = 100%; remaining portion = 80% (23-363(b) does NOT raise it — the remnant only touches the 100-ft radial circle at one boundary point). Per portion, not one whole-lot figure. [C]
4. Rear yard — the CORNER WAIVER is settled: zr-23-344(a) requires NO rear yard within 100 ft (radial) of the corner point, because the angle is ≤135°. [C]

STILL NOT KNOWN (what the captures do NOT settle):
a. The rear-yard outcome along the lot's far bottom segment beyond 100 ft of the 215 Place street line — zr-23-344(c) makes it depend on the adjoining lot's rear-vs-side line (R6 rule); neighbor facts not given. [?]
b. Any required rear-yard DEPTH (zr-23-342(a)) — depends on building type and #lot width# (design facts). [?]
c. Definitions of #front/rear/side lot line# and #lot width# are NOT captured — the rear-lot-line identification is not fully grounded. [?]
d. Through-lot rear yard — Section 23-343 (#rear yard equivalent#) is NOT captured. [?]
e. For the hypothetical interior/through lots, 23-363(b)/(c) and 23-344(a)/(b) turn on location and block-dimension facts not given; 23-363(a)/23-342(b) shallow also need the 12/15/1961 history. [?]
f. Special density area membership — boundary definitions of the Manhattan Core and the Special Downtown Brooklyn District are NOT captured (borough = Queens makes membership implausible, but confirmation is unavailable). [?]
g. "Lot area" is ambiguous between the MapPLUTO outline (10,387.99 sq ft) and PLUTO tabular lotarea (10,075 sq ft) — a ~313-sq-ft (~3%) official-source discrepancy the captures do not resolve; it scales every portion-area figure above. PLUTO lottype "3" meaning is also NOT KNOWN. [?]
h. 11-25 reach to R6B and every overlay (C2-2)/special-district interaction are flagged by the captures' own notes as advisory professional-review items (ADR-007); I applied them as the plain reading of the captured text, not as a verified determination. [?]

Scratch artifacts (my own folder only): .../scratchpad/reader2/geom.py, clip.py, radial.py.

END-OF-REPORT
