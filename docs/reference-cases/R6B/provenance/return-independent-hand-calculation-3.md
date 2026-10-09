# Independent reading from the step-P1 sealed folder, reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-07, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the pinned step-P1 law-text captures (without their notes), the benchmark lot's recorded official facts and outline, with no floor-area-ratio field and no program output - and had no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1; a value is recorded in a step-P1 reference-case row only where this reading and reading 2 (return-independent-hand-calculation-4.md) give the same value on the same basis.

---

PART 1 of 6

DISCLAIMER. This is a DRAFT reading of zoning-law text by an AI. It is NOT legal advice and NOT a professional review. Every captured law file is itself an "extracted_draft" (none re-verified by a second reader). Nothing here is a verified zoning determination.

ONE-HARD-RULE COMPLIANCE. I worked only from the sealed folder `.../scratchpad/sealed-p1` and wrote only in `.../scratchpad/reader1`. I opened NO official web pages (none were needed; where a needed text was not in the folder I marked it NOT KNOWN rather than fetch). I did not open, list, or search anything under /root/project. I used only the `verbatim_excerpt` field as law text; I did not read or rely on any `provisions` summary block.

FILES I READ (all under sealed-p1):
- INDEX.json
- facts/lot_facts_pluto.json; facts/lot_outline_epsg2263.json; facts/streets_dcm_centerlines.json; facts/zoning_nyco_query_C2-2.json; facts/zoning_nyzd_query_R6B.json
- law/zr-12-10-lot-corner.json; zr-12-10-lot-interior.json; zr-12-10-lot-through.json; zr-12-10-lot-area.json; zr-12-10-special-density-areas.json
- law/zr-23-362.json; zr-23-363.json; zr-23-342.json; zr-23-344.json; zr-23-52.json; zr-11-25.json
Helper I wrote (arithmetic/geometry only): reader1/geom.py.

FACTS USED (real lot 215-16 Northern Boulevard, BBL 4073340070):
[F] PLUTO (lot_facts_pluto.json): borough QN, borocode 4, block 7334, lot 70; zonedist1 "R6B"; overlay1 "C2-2"; splitzone false; lotarea "10075" (sq ft per the file's unit note); lotfront "100.76" ft; lotdepth "100.00" ft; lottype "3"; transitzone "Outer Transit Zone". Fields spdist1/spdist2/spdist3, zonedist2-4, overlay2 are listed ABSENT from the served row.
[?] PLUTO lottype "3" — the file states its meaning is NOT given; so the lot type code is unusable here. I derive lot type from geometry + ZR text instead.
[F] MapPLUTO outline (lot_outline_epsg2263.json): EPSG:2263, US survey feet; Shape__Area 10387.99 sq ft; one ring, vertices:
 P0(1048810.23,216310.44) P1(1048788.63,216408.05) P2(1048889.92,216431.10) P3(1048911.58,216333.50) P4(1048812.40,216310.93) → back to P0.
[F] Street centerlines (streets_dcm_centerlines.json), mapped Streetwidth (feet, free-text field): Northern Boulevard 100; 215 Place 60; 215 Street 60; 45 Road 50. Geometry in same coordinate system as the lot.
[F] Zoning queries: R6B zone-district features and C2-2 overlay features both present (attributes only).

GEOMETRY METHOD (reader1/geom.py; EPSG:2263 US survey feet):
[C] Edge lengths: P0-P1 = 99.98 ft; P1-P2 = 103.88 ft; P2-P3 = 99.98 ft; P3-P4 = 101.71 ft + P4-P0 = 2.22 ft (P4 lies almost on the P3→P0 line; interior angle at P4 = 179.995°, so the lot is effectively a quadrilateral P1-P2-P3-P0 with P3→P0 = 103.93 ft).
[C] Lot area by shoelace of P0..P4 = 10387.99 sq ft (matches Shape__Area). [?] This differs from PLUTO lotarea 10075 sq ft by ~313 sq ft (~3%); the captures do not reconcile the two. I use the outline-geometry area for portion measurements and flag the discrepancy.
[C] Interior angle at P2 = 89.69°; at the other corners ~90°.
Street-line identification (perpendicular distance of each lot vertex to each street centerline; half-width assumed = Streetwidth/2, i.e. centerline bisects the mapped bed — an assumption I flag):
[C] Northern Boulevard (half-width 50): P1=51.1, P2=51.0 ft from centerline; P0/P3≈151 ft. Edge directions parallel (lot P1→P2 unit (0.975,0.222) vs centerline (0.975,0.221)).
[C] 215 Place (half-width 30): P2=29.0, P3=28.8 ft; P0/P1≈133 ft. Directions parallel.
[C] 215 Street and 45 Road: every lot vertex ≥108 ft away → not adjacent.
Conclusion of identification: the NORTH edge P1-P2 is the Northern Boulevard street line and the EAST edge P2-P3 is the 215 Place street line (each lies ~1 ft from the mapped half-width line — within cross-dataset tolerance — and runs parallel to it). The WEST edge P0-P1 and SOUTH edge P3-P0 are NOT street lines (nearest mapped street >100 ft away) → they are interior (non-street) lot lines. The two street lines meet at vertex P2.

PART 1 END.

PART 2 of 6

Q1. LOT TYPE AND THE CORNER PORTION

Q1a — street lines, angle, lot type (real lot).
Law relied on (law/zr-12-10-lot-corner.json): "A 'corner lot' is either a #zoning lot# bounded entirely by #streets#, or a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle formed by the extensions of the #street lines# in the directions which they take at their intersections with #lot lines# other than #street lines#, forms an angle of 135 degrees or less."
[C] Street lines: exactly two — the north edge P1-P2 (Northern Boulevard) and the east edge P2-P3 (215 Place). The west edge P0-P1 and south edge P3-P0 are interior lot lines. (Basis: Part-1 perpendicular-distance/parallelism test.)
[C] Angle the street lines form: interior angle at their intersection P2 = 89.69° (≈ a right angle). Both street lines are straight, so "the directions which they take at their intersections with lot lines other than street lines" equal the edge directions.
[C] Lot type = CORNER LOT. The lot is NOT "bounded entirely by streets" (only 2 of 4 edges are streets), but it DOES adjoin the intersection of two streets (at P2) and the interior angle (89.69°) is ≤135° → the second branch of the definition is met.
[?] The PLUTO lottype code "3" is not usable (meaning not in captures); the corner classification above rests on geometry + the ZR definition, not on that code.

Q1b — corner portion and remaining portion (real lot).
Law (zr-12-10-lot-corner.json): "The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion of a #corner lot# shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."
How I measured: I treated the lot's two street-fronting edges as the two intersecting street lines (the lot frontage line IS the street line), then clipped the lot polygon to the region within 100 ft (perpendicular) of edge P1-P2 AND within 100 ft of edge P2-P3, using the outline coordinates. This is exactly "bounded by the intersecting street line and lines parallel to and 100 feet from each."
[C] Max perpendicular depth of the lot from the Northern Boulevard street line = 99.98 ft (just under 100) → the WHOLE lot is within 100 ft of Northern Boulevard (margin only ~0.03 ft).
[C] Max perpendicular depth from the 215 Place street line = 103.93 ft (over 100) → a thin far strip is beyond 100 ft of 215 Place.
[C] Corner portion (within 100 ft of BOTH street lines) ≈ 9,998 sq ft (96.2% of the 10,388 sq ft outline). This is essentially the whole lot except a ~3.9-ft-wide strip at the western (P0-P1) end.
[C] Remaining portion ≈ 390 sq ft (3.8%): the ~3.9 ft × ~100 ft western strip that is MORE than 100 ft from the 215 Place street line (but still within 100 ft of Northern Boulevard).
[C] The corner portion is subject to corner-lot regulations. The remaining ~390 sq ft portion adjoins only ONE street line (a short run of the Northern Boulevard frontage) and does not adjoin two opposite parallel street lines, so it is NOT a through lot → it is subject to INTERIOR-LOT regulations (per the definition's "whichever is applicable", read with zr-12-10-lot-through.json / zr-12-10-lot-interior.json).
[?] Sensitivity: the ~390 sq ft rests on the ~1-ft lot-edge-vs-mapped-street tolerance and the half-width/centering assumption; a ±1 ft shift of the 215 Place street line moves the remaining area by ~±100 sq ft. Its EXISTENCE (lot deeper than 100 ft from 215 Place) is robust; the exact figure is approximate. Also, because the Northern Boulevard depth (99.98) is a hair under 100, a marginally greater true depth could create a second tiny sliver on that side — not present on these coordinates.

PART 2 END.

PART 3 of 6

Q1c — three made-up right-angle rectangular corner lots (both stated sides are street lines, meeting at 90°). Applying the same rule (corner portion = bounded by the two street lines and the lines parallel to and 100 ft from each; at a right angle those parallel lines are 100 ft in from each street):
[C] C1 = 100 × 100. Both offset lines (100 ft from each street) coincide with the lot's far edges → corner portion = the ENTIRE lot = 10,000 sq ft. Remaining portion = 0. One lot type (corner) covers the whole lot.
[C] C2 = 150 (street A) × 100 (street B). Corner portion = 100 (along A) × 100 (along B) = 10,000 sq ft. Remaining portion = the strip from 100 to 150 ft along street A = 50 × 100 = 5,000 sq ft. That strip adjoins only street A (one street), not two opposite streets → subject to INTERIOR-LOT regulations.
[C] C3 = 200 (street A) × 120 (street B). Corner portion = 100 × 100 = 10,000 sq ft. Remaining portion = 200×120 − 10,000 = 24,000 − 10,000 = 14,000 sq ft (an L-shape: the x>100 strip plus the y>100 strip). It adjoins street A and street B but NOT two OPPOSITE parallel streets → subject to INTERIOR-LOT regulations.
[F]/[C] note: "150 ft (along street A) by 100 ft (along street B)" etc. are the given dimensions; the corner portion is 10,000 sq ft in every case because both streets meet at a right angle and each 100-ft offset is independent of total lot size (as long as the lot reaches ≥100 ft in each direction).

Q2. MAXIMUM LOT COVERAGE (district R6B)

Bridge to R6B. Law (law/zr-11-25.json): "All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth in express provisions ... If a section lists an R4 District, therefore, the provisions of that section shall also apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with suffixes are listed within such section."
[C] zr-23-362 lists "R6 R7 R8 R9 R10 R11 R12" and contains no separate R6B provision, so by §11-25 its R6 rule applies to R6B. (The capture's own note flags that this reach to R6B must be professionally confirmed; per ADR-007 this is an unreviewed, labelled draft reading.)

Q2a — real lot.
Law (law/zr-23-362.json, paragraph (a) "For standard lots"): "In the districts indicated, the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent."
[C] Corner portion (~9,998 sq ft): subject to corner-lot regulations → maximum residential lot coverage = 100%.
[C] Remaining portion (~390 sq ft, interior-lot regulations): maximum residential lot coverage = 80%.
[C] NO single whole-lot figure: because the lot has a remaining portion governed by a different provision (80%) than the corner portion (100%), one provision does not cover the whole lot. So the answer is per portion (100% on ~96% of the lot; 80% on the ~390 sq ft strip).
[?] zr-23-362(b) "For eligible sites" (buildings using §23-434) gives 65%/50% caps — but that depends on a building using the §23-434 eligible-site provisions, a fact not given, and §23-434 is not captured → NOT KNOWN; absent those facts, paragraph (a) governs.
[?] zr-23-363(b) could lift an interior portion to 100% "within 100 feet of the point of intersection" — but the remaining strip lies ~100 ft or more from the corner point P2 (its nearest point sits on the 100-ft line; the strip runs out to ~145 ft from P2), so §23-363(b) does not clearly reach it, and §23-363 only increases coverage. Remaining stays 80% on the given facts.
[?] Overlay C2-2 (PLUTO overlay1): the commercial-overlay rules are not captured; any overlay effect on residential lot coverage is NOT KNOWN.

PART 3 END.

PART 4 of 6

Q2b — made-up corner lots (R6B; §23-362(a) via §11-25).
[C] C1 (100×100): whole lot is the corner portion → maximum residential lot coverage 100% for the WHOLE lot (one provision covers it).
[C] C2 (150×100): corner portion (10,000 sq ft) → 100%; remaining portion (5,000 sq ft, interior-lot regs) → 80%. Per portion.
[C] C3 (200×120): corner portion (10,000 sq ft) → 100%; remaining portion (14,000 sq ft, interior-lot regs) → 80%. Per portion.
[?] Same caveats as Q2a: §23-362(b) eligible-site caps and §23-363 increases are NOT KNOWN without building/shallow/block facts; for the remaining portions, §23-363(b) could raise 80%→100% only for the part within 100 ft of the corner point — fact-specific, not given.

Q2c — 40×100 interior lot and 40×200 through lot in R6B: does zr-23-363 change what zr-23-362 gives?
Law (law/zr-23-363.json), opening: "In the districts indicated, the maximum #lot coverage# set forth in Section 23-361 ... or 23-362 ..., as applicable, may be increased in accordance with the provisions of this Section." It then gives three triggers:
(a) "Shallow #zoning lots#" — for lots eligible for the shallow-lot rear-yard modifications of §23-342 (interior) or the shallow through-lot rear-yard-equivalent modifications of §23-343, coverage "may be increased by one percent for every five feet the depth ... is less than 95 feet for #interior lots# or 190 feet for #through lots#"; and "In no event shall the maximum #lot coverage# of an #interior lot# or #through lot# exceed 90 percent."
(b) "Within 100 feet of corners" — "for #interior# or #through lots#, or portions thereof, within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less, the maximum #lot coverage# shall be 100 percent."
(c) "Along the short dimension of the block" — where a front lot line "coincides with the #street line# of the #short dimension of a block#", 100 percent "within 100 feet of such #street line#."
[C] What §23-363 requires before ANY provision applies: the district must be among R1–R12 (R6B qualifies via §11-25), AND one of the three specific triggers (a)/(b)/(c) must be met. §23-363 can only INCREASE §23-362's coverage, never decrease it.
Interior lot 40×100:
[C] §23-362 base = 80% (interior lot).
[?] (a) Shallow: needs the lot's DEPTH <95 ft AND eligibility for the §23-342 shallow-lot modification (which requires the shallow condition to have existed on 12/15/1961, unchanged). "40 by 100" does not say which dimension is the depth (front-lot-line orientation unknown); the 1961 history is unknown. NOT KNOWN.
[?] (b) Within 100 ft of a corner: needs the lot/portion to be within 100 ft of an intersection of two street lines at ≤135°. An interior lot adjoins only one street; no corner facts are given. NOT KNOWN.
[?] (c) Short dimension of block: needs the front lot line to coincide with the short-dimension street line of the block; no block dimensions given. NOT KNOWN.
[C] So on "40×100 interior, R6B" alone, §23-363 does NOT change the 80% — but whether it WOULD (up to 90% via (a) or 100% via (b)/(c)) is NOT KNOWN pending: which dimension is the depth/front lot line, the 1961 shallow-condition history, proximity to a two-street intersection, and the block's short-dimension frontage.
Through lot 40×200:
[C] §23-362 base = 80% (through lot).
[?] (a) Shallow through: needs depth <190 ft and §23-343 eligibility; "40 by 200" leaves the between-streets depth ambiguous, and §23-343 is not captured. NOT KNOWN. (b)/(c): same unknowns as above. So §23-363 does not change 80% on the bare facts; whether it would is NOT KNOWN.

PART 4 END.

PART 5 of 6

Q3. REAR YARD (law/zr-23-342.json, zr-23-344.json; both list R1–R12, reaching R6B via §11-25).

Base rule. zr-23-342 opening: "In all districts, #rear yards# shall be provided on #interior lots# in accordance with this Section., except as otherwise provided pursuant to the provisions of Section 23-34, inclusive." Depths (paragraph (a) "Standard lots"): (1) detached / zero-lot-line buildings — rear yard ≥20 ft at/below 75 ft height, 30 ft above 75 ft; (2) semi-detached / attached — (i) lot width <40 ft: ≥30 ft; (ii) lot width ≥40 ft: ≥20 ft (≤75 ft), 30 ft above. Paragraph (b) "Shallow lots": modifications where an interior lot is <95 ft deep and the shallow condition existed on 12/15/1961 unchanged (reduce 6 in per foot <95 ft, floor 10 ft).
Corner modification. zr-23-344(a) "Within one hundred feet of corners": "In the districts indicated, no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less."
zr-23-344(c) "Beyond one hundred feet of a #street line#": "for #interior# or #through lot# portions of #corner lots# ... the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line#", then (1) a §23-342 rear yard where it coincides with a rear lot line of an adjoining lot; (3) "In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#."

Q3a — real lot (R6B corner lot).
[C] §23-342 requires a rear yard only "on interior lots." The real lot is a corner lot; the base rear-yard rule therefore reaches only the portion subject to interior-lot regulations (the ~390 sq ft remaining strip), NOT the corner portion.
[C] §23-344(a) corner waiver APPLIES: the two street lines meet at P2 at 89.69° (≤135°), so NO rear yard is required within 100 ft of point P2. Measured radially 100 ft from the intersection point P2 (the Northern Boulevard ∩ 215 Place corner). This covers the near-corner area.
[C] The ~390 sq ft remaining strip sits ~104–145 ft from P2 → BEYOND the §23-344(a) 100-ft corner waiver → a rear yard can be required there under §23-342, as modified by §23-344(c).
[C] §23-344(c): the part of the SOUTH side lot line beyond 100 ft from the 215 Place street line (the ~3.9 ft nearest P0) is treated as a rear lot line. (The west side lot line is only ~99.98 ft long, so essentially none of it is beyond 100 ft from Northern Boulevard.)
[?] Rear-yard DEPTH is NOT KNOWN: it depends on building type (detached/zero-lot-line vs semi-detached/attached) and lot width — none given (would be 20 ft or 30 ft under (a)(1)/(a)(2)).
[?] Whether a yard is actually required along that reclassified rear lot line is NOT KNOWN: §23-344(c)(3) says NONE in R6–R12 where it coincides with an adjoining lot's SIDE line, but (c)(1) requires a §23-342 yard where it coincides with an adjoining lot's REAR line — the adjoining-lot configuration is not given.

Q3b — C2, C3, and the 40×100 interior lot (R6B).
[C] C2 and C3 are right-angle corner lots (90° ≤135°) → §23-344(a): no rear yard within 100 ft of the corner point. Their remaining portions (C2 5,000 sq ft; C3 14,000 sq ft) are interior-regulated, so §23-342 can require a rear yard there, and §23-344(c) reclassifies the beyond-100-ft side-lot-line portions as rear lot lines.
[?] For C2/C3 the rear-yard DEPTH (20 vs 30 ft) is NOT KNOWN (building type/lot width not given), and whether a yard is required along each reclassified rear lot line is NOT KNOWN (adjoining-lot coincidence, §23-344(c)(1) vs (3)).
40×100 interior lot:
[C] It is an interior lot → §23-342 requires a rear yard at every rear lot line. §23-344(a) corner waiver does NOT apply (an interior lot has no two intersecting street lines on it, absent corner facts).
[?] Depth NOT KNOWN: 20 ft or 30 ft depending on building type and lot width (which of 40/100 is the frontage/width is not stated; width exactly 40 would be "40 ft or greater" → 20 ft for semi-detached/attached, but detached vs attached is not given).
[?] Shallow reduction (23-342(b)) only if the interior lot is <95 ft deep AND the 1961 condition holds — depth orientation and 1961 history NOT KNOWN.

Q3c — through lot 40×200 (R6B).
[C] zr-23-342 provides rear yards "on interior lots"; it does NOT state a rear-yard requirement for a THROUGH lot. For through lots it (and zr-23-344) refer to the "#rear yard equivalent# requirements of Section 23-343."
[?] §23-343 is NOT in the sealed captures → the rear-yard-equivalent requirement for a clean 40×200 through lot is NOT KNOWN from the provided text. (A 40×200 lot bounded by its two opposite street lines is all "through-lot" with no interior portion under zr-12-10-lot-through, so §23-342 does not supply the answer; the missing item is §23-343.)

PART 5 END.

PART 6 of 6

Q4. SPECIAL DENSITY AREAS

Q4a — what the definition lists. Law (law/zr-12-10-special-density-areas.json): "'Special density areas' shall refer to special geographies where unique density regulations apply to #residential# #developments# or #enlargements#. #Special density areas# shall include: (a) the #Manhattan Core#; and (b) the #Special Downtown Brooklyn District#."
[F] The definition lists exactly two: (a) the Manhattan Core; (b) the Special Downtown Brooklyn District.
(The term is used in law/zr-23-52.json: paragraph (a) removes the dwelling-unit factor for "#developments# or #enlargements# of #residences# in #special density areas#" and for certain conversions there.)

Q4b — can the real lot be placed, from the facts alone?
[F] Fact relied on: PLUTO records borough "QN" (Queens), borocode 4, BBL 4073340070; and spdist1/spdist2/spdist3 are listed ABSENT from the served row (no special district recorded for the lot).
[C] What CAN be said: the lot is in Queens; the two listed special density areas are named for Manhattan ("Manhattan Core") and Brooklyn ("Special Downtown Brooklyn District"); neither names Queens; and the PLUTO row carries no special-district value.
[?] What CANNOT be settled from the captures: the captured text does not define the geographic BOUNDARIES of "Manhattan Core" or "Special Downtown Brooklyn District" (both are #defined terms# not captured), and it uses "shall include", which may be non-exhaustive. So a definitive "the lot is not in any special density area" cannot be fully closed from the captured text alone — though the Queens location makes it the strong reading.
[?] To settle it: capture the ZR definitions/geographic limits of "Manhattan Core" and "Special Downtown Brooklyn District", and confirm whether the "shall include" list is exhaustive.

Q5. WHAT THE NEW CAPTURES CHANGE vs the earlier reading (earlier reader, without these captures, had: lot type corner; coverage and rear yard "not known" because the corner definition, §23-342 and §23-363 were missing).

Now SETTLED by the captured text:
[C] Lot type CORNER is now text-grounded (zr-12-10-lot-corner, second branch; angle 89.69° ≤135°).
[C] The lot divides into a corner portion (~9,998 sq ft) under corner-lot regulations and a remaining portion (~390 sq ft) under interior-lot regulations — now definable because the corner definition is captured.
[C] Maximum residential lot coverage (R6B via §11-25, §23-362(a)): 100% on the corner portion, 80% on the interior/remaining portion — settled, PER PORTION (no single whole-lot figure).
[C] Rear-yard corner waiver: §23-344(a) removes any rear-yard requirement within 100 ft of the corner point (angle ≤135° satisfied) — now settled.
[C] §23-363 structure is now known (coverage may only be INCREASED, and only under the shallow / within-100-ft-of-corner / short-dimension-of-block triggers).
[C] The "special density areas" definition is now captured (lists Manhattan Core and Special Downtown Brooklyn District).

Still NOT KNOWN even with these captures:
[?] Rear-yard DEPTH on the interior/remaining portion — needs building type (detached/zero-lot-line vs semi-detached/attached) and lot width (20 vs 30 ft).
[?] Whether a rear yard is required along the §23-344(c) reclassified (beyond-100-ft) rear lot line — needs adjoining-lot configuration ((c)(1) vs (c)(3)).
[?] Through-lot rear yard — §23-343 "rear yard equivalent requirements" is not captured.
[?] §23-363 application — needs shallow-lot depth + 1961 history, proximity to a two-street intersection, or the block's short-dimension frontage.
[?] §23-362(b) eligible-site coverage (65%/50%) — needs §23-434 building facts; §23-434 not captured.
[?] C2-2 commercial-overlay effect on residential coverage/rear yard — overlay rules not captured.
[?] Lot-area discrepancy — PLUTO lotarea 10,075 sq ft vs outline 10,388 sq ft is unreconciled in the captures (I used 10,388 for portions).
[?] Whether the lot is in a "special density area" — boundary definitions of the two listed areas are not captured (Queens location strongly implies NO, but the text does not close it).
[?] PLUTO lottype code "3" meaning — not in the captures.

Measurement caveats carried throughout: street-line identification used an assumed centerline-bisects-bed half-width; the lot's frontage edges sit ~1 ft from the mapped street lines (cross-dataset tolerance), giving the ~390 sq ft remaining portion a ~±100 sq ft uncertainty; the Northern Boulevard depth (99.98 ft) is a hair under 100 ft, so the "entire lot within 100 ft of Northern Boulevard" finding has near-zero margin.

END-OF-REPORT
