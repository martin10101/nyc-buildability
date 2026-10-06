# Independent hand-calculation, follow-up (provenance)

What this is: the follow-up return from the same AI helper, under the same hard rule (sealed folder, no program access), made on 2026-10-06. It covers the reach of a corner lot (table C) and the suffix question (table D). It is a draft reading of the law, not professionally reviewed. It is reproduced below unchanged; it is the origin of the expected values in the corner-reach and suffix cases.

---

FOLLOW-UP — same rules (sealed packet + official ZR only; nothing under /root/project opened; draft reading, NOT legal advice; NOT KNOWN where text is silent).
Method: street lines = the two lot edges I identified (P1-P2 = Northern Blvd, P2-P3 = 215 Place). Perp distance = |(B-A)x(P-A)|/|B-A| to each edge-line. Strip-beyond area = polygon clipped at the 100-ft offset line (Sutherland-Hodgman); circle-beyond area = 1200x1200 grid point-in-polygon. Coords from facts/lot_outline_epsg2263.json (EPSG:2263 ft).

== Q1 (real lot) ==
(a) Greatest perpendicular distance of any lot point from each street line (max occurs at a vertex):
 - Northern Blvd street line: 99.97 ft, at vertex P0 (P3 and P4 also 99.97).
 - 215 Place street line: 103.93 ft, at vertex P0.
(b) Whole lot within 100.00 ft of each street line?
 - Northern Blvd: YES (max 99.97 ft, nothing beyond).
 - 215 Place: NO. A sliver beyond 100 ft: width 3.93 ft (= 103.93 - 100.00), area approx 390 sf (near the P0-P1 west edge).
(c) Greatest distance of any lot point from corner point P2 = 144.60 ft, at P0. NOT the whole lot within 100 ft of P2. Approx lot area beyond 100 ft of P2 = approx 2,560 sf (grid integration; the south-west wedge near P0/P4).

== Q2 (rectangular 90-deg corner lots, R6B, no overlay) ==
Perp-from-A-line max = the B-frontage dimension; perp-from-B-line max = the A-frontage dimension; farthest-corner = diagonal.

C1 - 40 on A x 100 on B (4,000 sf): perp from A line max 100.00 ft; perp from B line max 40.00 ft -> WHOLE lot within 100 ft of EACH street line (A exactly 100.00). Diagonal 107.70 ft -> NOT whole lot within 100 ft of the corner point.
 (i) Coverage: 23-362(a) "the maximum residential lot coverage for corner lots shall be 100 percent." Whole lot is within 100 ft of each street line, so it is entirely the corner-lot portion (ZR 12-10 "lot, corner": the corner-lot regulation covers "that portion bounded by the intersecting street line and lines parallel to and 100 feet from each intersecting street line") -> 100% for the whole lot.
 (ii) Rear yard: 23-344(a) "no rear yard shall be required within 100 feet of the point of intersection of two street lines intersecting at an angle of 135 degrees or less" (90 <= 135) -> none required within 100 ft of the corner. The small part beyond 100 ft of the corner is NOT covered by (a); whether a rear yard is required there = NOT KNOWN - missing ZR 23-342 (baseline rear-yard requirement) and the 12-10 "rear lot line"/"side lot line" definitions.

C2 - 60 x 80 (4,800 sf): perp from A line max 80.00; perp from B line max 60.00 -> WHOLE lot within 100 ft of EACH street line. Diagonal 100.00 ft -> WHOLE lot within 100.00 ft of the corner point (exactly on the boundary).
 (i) Coverage: 100% whole lot (23-362(a) corner lots 100 percent; whole lot inside the 12-10 corner-lot portion).
 (ii) Rear yard: whole lot within 100 ft of the corner -> 23-344(a) waives it over the entire lot -> NO rear yard required anywhere. Fully settled by the packet.

C3 - 150 on A x 100 on B (15,000 sf): perp from A line max 100.00 (within); perp from B line max 150.00 -> NOT within 100 ft of street line B (strip beyond: width 50 ft, area 50x100 = 5,000 sf). Diagonal 180.28 ft -> NOT whole lot within 100 ft of the corner point.
 (i) Coverage: near portion within 100 ft of each street line -> corner-lot 100% (23-362(a)); the 50-ft strip beyond 100 ft of street line B is outside the 12-10 corner-lot portion -> interior-lot 80% (23-362(a) "interior lots ... 80 percent"). So no single whole-lot figure: ~100% on 10,000 sf + 80% on 5,000 sf. From the PACKET's 23-362 alone (which does not portion the lot) the far-strip rule is NOT KNOWN; the portioning relies on ZR 12-10 "lot, corner" (not in packet; web-read).
 (ii) Rear yard: 23-344(c) - for corner lots "the portion of a side lot line beyond 100 feet of the street line that it intersects shall be considered a rear lot line"; then (c)(1) a rear yard per 23-342 if it coincides with an adjoining rear lot line, or (c)(3) "In R6 through R12 Districts, no rear yard shall be required where such rear lot line coincides with a side lot line of an adjoining zoning lot." So a rear yard MAY be required along the 50-ft rear-lot-line portion -> NOT KNOWN without neighbor lot-line coincidence and ZR 23-342 (depth). Within 100 ft of the corner, 23-344(a) waives it.

== Q3 (suffix: do R6-listed sections reach R6B?) ==
Basis = ZR 11-25 (packet law/zr-11-25.json), verbatim: "All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth in express provisions of this Resolution. If a section lists an R4 District, therefore, the provisions of that section shall also apply to R4-1, R4A and R4B Districts, unless separate provisions for the districts with suffixes are listed within such section. Wherever a section lists only a district with a suffix, the provisions applicable to such district are different from the provisions of that district without a suffix."
Yes, 11-25 carries the exception "except as otherwise set forth in express provisions" / "unless separate provisions for the districts with suffixes are listed." None of the three captures names R6B or any suffixed R6x row, so the general R6 rule reaches R6B.
 - 23-362: APPLIES TO R6B - via 11-25; header "R6 R7 R8 R9 R10 R11 R12", no R6B-specific provision in the capture.
 - 23-52: APPLIES TO R6B - via 11-25; header "R1 ... R12", no R6B-specific provision in the capture.
 - 23-344: APPLIES TO R6B - via 11-25; header "R1 ... R12" and its (c)/(d) distinguish only "R1 through R5" vs "R6 through R12" (R6B sits in the R6-R12 group); no R6B-specific exception in the capture.
(Contrast: 23-22 and 23-432 DO list a separate R6B row, so those used R6B directly - not asked here.)

== Web pages read ==
No new fetches this round. I rely on one page read earlier (today, 2026-10-06): https://zr.planning.nyc.gov/article-i/chapter-2/12-10 - gave the ZR 12-10 "lot, corner" definition, including the "portion ... parallel to and 100 feet from each intersecting street line" clause used for the coverage portioning (this clause is NOT in the packet's 12-10 capture, which holds only wide/narrow street).

END-OF-REPORT