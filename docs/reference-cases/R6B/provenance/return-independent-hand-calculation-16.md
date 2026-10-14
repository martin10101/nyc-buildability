# Independent reading from the step-P7 sealed folder, reading 2 (provenance)

What this is: one of two independent readings made on 2026-10-11, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the 189 pinned law-text captures (without their notes), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, ten made-up boundary cases M1 to M10, and FOUR answers settled by earlier readings (copied word for word and given as settled, so completed readings are reused and not worked again) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2 of the step-P7 pair (a data-contract-verifier); a value is recorded in the short-block-rear-yard reference case only where this reading and reading 1 (return-independent-hand-calculation-15.md) give the same answer on the same basis.

---

PART 1 of 7

DRAFT AI READING — NOT LEGAL ADVICE, NOT A PROFESSIONAL REVIEW. This is one independent AI reader's hand reading of captured NYC Zoning Resolution text and stated facts. It is not a zoning determination and gives no verdict that any building or lot complies with the law. Every capture in the folder is an unverified "extracted_draft" (raw_html_verified=false); I treat verbatim_excerpt and table/tables fields as the text, and ignore others' summaries/extraction notes.

HARD-RULE COMPLIANCE. I worked ONLY inside /root/project/lanes-runtime/owner-docs/session-2026-10-11d/sealed-p7-v2. I opened no web page, ran no search, and opened nothing else under /root/project. I could NOT write to my scratch folder (reader-p7-2b): the Write tool is disabled and the session's read-only guard blocks shell file-writes, so no geom.py was saved; I did every calculation with read-only inline Python and show the method/numbers inline below.

FILES READ.
Law (23): zr-23-344, zr-23-34, zr-23-342, zr-23-343, zr-23-341; zr-12-10-short-dimension-of-a-block, -block, -street, -street-line, -lot-line-front, -lot-line-rear, -lot-line-side, -zoning-lot, -lot-corner, -lot-interior, -lot-through, -public-park, -yard, -yard-rear, -yard-front, -yard-side, -yard-equivalent-rear, -street-setback-line.
Facts (8) + INDEX: made_up_boundary_lots, settled_by_earlier_readings, pluto_rows_lots_70_and_1, printed_tax_map_labels, zoning_nyzd_query_R6B, zoning_nyco_query_C2-2, block_7334_lot_outlines_epsg2263, streets_dcm_centerlines, INDEX.json. (Folder built from repo head cb95092.) I did NOT open 34-231/232/233 or 35-53; for the overlay point I rely on the settled sheet (answer 4).

=== Q1. ZR 23-344(b), with definitions ===

[C] 23-344 chapeau (file zr-23-344.json): "In all districts, as indicated, the #rear yard# requirements set forth in Section 23-342 ... and the #rear yard equivalent# requirements of Section 23-343 ... shall be modified as set forth in this Section." District line: "R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12".

[C] (b) (zr-23-344.json): "(b) Along #short dimension of a block# In the districts indicated, whenever a #front lot line# of a #zoning lot# coincides with the #street line# of the #short dimension of a block#, no #rear yard# shall be required within 100 feet of such #street line#".

Definitions the folder holds:
[C] short dimension of a block (zr-12-10-short-dimension-of-a-block.json): "The "short dimension of a block" shall be a #block# frontage where the dimension between any two #streets# bounding the #block# measures less than 230 feet."
[C] block (zr-12-10-block.json): "A "block" is a tract of land bounded by: (a) #streets#; (b) #public parks#; (c) railroad rights-of-way, when located at or above ground level but not including sidings or spurs in the same ownership as the #zoning lot#; (d) airport boundaries; (e) pierhead lines (or shore lines where no pierhead lines have been established); or (f) corporate boundary lines of New York City."
[C] street (zr-12-10-street.json): "A "street" is: (a) a way established on the City Map; or (b) a way designed or intended for general public use, connecting two ways established on the City Map ... at least 50 feet in width ... covenanted ... ; or (c) ... approved by the City Planning Commission ...; or (d) any other public way that on December 15, 1961, was performing the functions usually associated with a way established on the City Map; or (e) a #covered pedestrian space# ...". Final paragraph: "... a #private road#, or a driveway that serves only to give vehicular access to an #accessory# parking or loading facility, or to allow vehicles to take on or discharge passengers ..., shall not be considered a #street#."
[C] street line (zr-12-10-street-line.json): "A "street line" is a #lot line# separating a #street# from other land. A #street setback line# supersedes the #street line# in the application of #yard#, height and setback, and #court# regulations."
[C] front lot line (zr-12-10-lot-line-front.json): "A "front lot line" is a #street line#."
[C] zoning lot (zr-12-10-zoning-lot.json): four forms — (a) a lot of record on 12/15/1961 or later amendment; (b) a single-ownership tract within one block on 12/15/1961; (c) a single-fee-ownership tract (lots contiguous ≥10 ft) at permit/CO filing; (d) a tract declared one zoning lot by recorded Declaration(s). "A #zoning lot# ... may or may not coincide with a lot as shown on the official tax map".
(Also used: rear lot line, side lot line, corner/interior/through lot, public park, yard definitions — quoted in Q2/Q4/Q5 where they bite.)

Q1a — what must be measured for "short dimension of a block":
[C] The measured quantity is "the dimension between any two #streets# bounding the #block#", and it must be "less than 230 feet".
[?] BETWEEN WHAT: NOT KNOWN from the text. It says "between any two #streets#". A #street# is a "way" (an area), not a line; the definition does NOT say to measure between street lines, between centrelines, or along lot lines. The most defensible reading is street-line to street-line (a block is the "tract of land bounded by #streets#", and the #street line# is "a #lot line# separating a #street# from other land", so the land-between-streets is bounded by the two street lines) — but the text does not state this, so centreline-to-centreline cannot be excluded on the text alone. Missing: the measurement baseline.
[?] ALONG WHAT LINE / direction (perpendicular? along the frontage?): NOT KNOWN; the text does not say.
[C] STRICT? Yes. "less than 230 feet" is strict: 230.00 ft is not less than 230 ft. (Confirmed by the made-up pair M2=230.00 and M3=230.01, both not short; M1=229.99 short.)

Q1b — "within 100 feet of such street line":
[C] (b) says "no #rear yard# shall be required within 100 feet of such #street line#." Read literally, "within 100 feet of [a line]" is the set of points whose distance to that street line is 100 ft or less (distance to a line being perpendicular). 
[?] The text does not expressly define the method, and in particular does not resolve the boundary (is a point at exactly 100.00 ft "within"?). NOT KNOWN at the exact boundary. (Contrast the corner-lot definition, which is explicit: "lines parallel to and 100 feet from each intersecting #street line#".) Missing: inclusive/exclusive treatment of the 100-ft line; whether a #street setback line# displaces the baseline here (zr-12-10-street-setback-line.json: a setback line "supersedes the #street line# in the application of #yard# ... regulations", but exists only in Staten Island or Queens Community District 10, and the folder does not state the lot's community district).

Q1c — what can bound a block; park or private way?
[C] Bounding features: the six listed in the block definition — streets; public parks; at/above-ground railroad rights-of-way (excluding sidings/spurs in the zoning lot's ownership); airport boundaries; pierhead/shore lines; NYC corporate boundary lines.
[C] Public park: YES — expressly item (b). "public park" (zr-12-10-public-park.json) = "any publicly owned park, playground, beach, parkway or roadway within the jurisdiction and control of the Commissioner of Parks and Recreation, except for park strips or malls in a #street# ...".
[C] Private way: NO, unless it independently qualifies as a #street#. The street definition expressly says "a #private road#, or a driveway that serves only to give vehicular access ... shall not be considered a #street#", and a private way is not a park/railroad/airport/pierhead/City-boundary. So a mere private way does not bound a block.

PART 2 of 7

=== Q2. ZR 23-344(c), especially (c)(3) ===

[C] (c) (zr-23-344.json): "(c) Beyond one hundred feet of a #street line# In all districts, as indicated, for #interior# or #through lot# portions of #corner lots#, and for #zoning lots# bounded by two or more #streets# that are neither #corner lots# nor #through lots#, the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply along such #rear lot line#:
(1) In all districts, a #rear yard# shall be provided in accordance with Section 23-342 ..., where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#.
(2) In R1 through R5 Districts, a #rear yard# with a minimum depth of five feet shall be provided where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#.
(3) In R6 through R12 Districts, no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#."

Q2a — which lots/portions; what becomes a rear lot line; from which street line is 100 ft measured:
[C] (c) speaks to two situations: (i) the "#interior# or #through lot# portions of #corner lots#" (i.e., the part of a corner lot left over after the corner portion — see the corner-lot definition in Part 4), and (ii) "#zoning lots# bounded by two or more #streets# that are neither #corner lots# nor #through lots#".
[C] What becomes a rear lot line: "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line#." So a side lot line that physically meets (intersects) a street line is reclassified, for the part lying more than 100 ft from that street line.
[C] From which street line: "the #street line# that it [the side lot line] intersects" — the specific street line that particular side lot line touches, not necessarily the frontage street.

Q2b — what decides between (c)(1) and (c)(3); does the adjoining lot's district matter?
[C] The deciding fact is the KIND of the adjoining zoning lot's coinciding lot line: if the constructive rear lot line "coincides with a #rear lot line# of an adjoining #zoning lot#" → (c)(1), rear yard per 23-342; if it "coincides with a #side lot line# of an adjoining #zoning lot#" → (c)(2)/(c)(3) by the SUBJECT lot's district.
[C] The adjoining lot's DISTRICT is not mentioned anywhere in (c); it does not matter. The district that matters is the subject zoning lot's own district, which selects the subparagraph: (c)(1) all districts (adjoining rear lot line), (c)(2) R1–R5 (adjoining side lot line → 5 ft), (c)(3) R6–R12 (adjoining side lot line → none). So: only the adjoining lot's lot-line KIND, plus the subject lot's district.

=== Q3. How 23-342, 23-343, 23-344(a),(b),(c) fit together ===

[C] 23-342 (zr-23-342.json): "In all districts, #rear yards# shall be provided on #interior lots# in accordance with this Section, except as otherwise provided pursuant to the provisions of Section 23-34, inclusive." Standard depth 20 ft (≤75 ft height) / 30 ft (above 75 ft), with lot-width and shallow-lot variants.
[C] 23-343 (zr-23-343.json): rear yard EQUIVALENTS on #through lots#, "except as otherwise provided pursuant to ... Section 23-34, inclusive"; exceptions include through lots <110 ft deep, large sites, entire-block lots.
[C] 23-344 chapeau: these 23-342/23-343 requirements "shall be modified as set forth in this Section." So 23-344 is a set of modifications to the base requirements. 23-342/343 fix when and how big a rear yard (or equivalent) is; 23-344(a)–(d) carve out where none (or a reduced one) is required.

Can more than one 23-344 modification apply to the same lot?
[C] The text lists (a) within 100 ft of a corner; (b) along a short dimension; (c) beyond 100 ft of a street line; (d) multiple rear lot lines — each introduced by "In the districts indicated"/"In all districts, as indicated." Nothing in the captured text makes them mutually exclusive or sets a priority. [?] So the text neither forbids nor sequences overlap: more than one can speak to one lot (e.g., a corner lot can meet both (a) and (c)); how they combine where they overlap is NOT stated.

Does (b) apply to a corner lot?
[C] (b) applies "whenever a #front lot line# of a #zoning lot# coincides with the #street line# of the #short dimension of a block#." A #corner lot# has #front lot lines# (each street line is a front lot line). Nothing in (b) excludes corner lots. [C] So (b) can apply to a corner lot whose front lot line sits on a short-dimension street line. [?] The text gives no corner-lot carve-out.

Where (b) applies, does (c) still matter beyond 100 ft?
[C] (b) removes the rear-yard requirement "within 100 feet of such [short-dimension] #street line#." (c) operates on side-lot-line portions "beyond 100 feet of the #street line# that it intersects" — possibly a DIFFERENT street line. For a point beyond 100 ft of the short-dimension street line, (b) does not reach it, and (c) may convert a side lot line there into a rear lot line. [?] The text does not say (b) switches off (c) or vice-versa, so each can govern its own zone; their interaction where both touch the same ground is NOT resolved by the text.

PART 3 of 7

Common law for Q4 (all made-up blocks are plain R6B; "Street" = a mapped street of the stated width — note zr-12-10-made_up header [F]). R6B is an R6 district; the 23-344 header lists "R6" and (c)(3) says "R6 through R12 Districts". [?] The captured text does not separately enumerate letter-suffix districts (R6A/R6B); I read R6B as within "R6 through R12", a point a professional must confirm.

Definitions used in Q4:
[C] corner lot (zr-12-10-lot-corner.json): "A "corner lot" is either a #zoning lot# bounded entirely by #streets#, or a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle ... forms an angle of 135 degrees or less. ... The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion ... shall be subject to the regulations for a #through lot# or for an #interior lot#, whichever is applicable."
[C] interior lot (zr-12-10-lot-interior.json): "neither a #corner lot# nor a #through lot#."
[C] through lot (zr-12-10-lot-through.json): "not a #corner lot#, which adjoins two #street lines# opposite to each other and parallel or within 45 degrees of being parallel".
[C] rear lot line (zr-12-10-lot-line-rear.json): "any #lot line# ... except a #front lot line#, which is parallel or within 45 degrees of being parallel to, and does not intersect, any #street line# bounding such #zoning lot#."
[C] side lot line (zr-12-10-lot-line-side.json): "any #lot line# which is not a #front lot line# or a #rear lot line#."
[C] rear yard (zr-12-10-yard-rear.json): "a #yard# extending for the full length of a #rear lot line#." (So no rear lot line ⇒ no rear yard.)

=== Q4. Made-up cases M1–M10 ===

M1 [F]: block X‖Y 229.99 ft apart (between facing street lines), P⊥Q 600 ft; P frontage runs X→Y; lot = interior, front on P, 50 ft on P, 100 ft deep, touches neither X nor Y.
- (b): [C] For the P block frontage, the two bounding cross-streets are X and Y; their stated separation (street-line basis) = 229.99 ft < 230 ⇒ the P frontage IS a "short dimension of a block" on the basis the fact supplies. The lot's front lot line on P coincides with that short-dimension street line ⇒ (b) APPLIES. [?] The definition itself does not fix the basis; on a centreline basis (widths of X,Y not given) the result could differ — NOT KNOWN if that basis were intended.
- Where no rear yard under (b): [C] within 100 ft of the P street line; the lot is 100 ft deep, so this is the whole lot.
- (c): [C] Does NOT speak to M1 — the lot is an interior lot fronting one street (P); it is not a corner-lot portion and not "bounded by two or more #streets#".

M2 [F]: as M1 but X–Y = 230.00 ft.
- (b): [C] 230.00 is NOT < 230 ⇒ the P frontage is NOT a short dimension ⇒ (b) does NOT apply. Base 23-342 governs the interior lot's rear lot line (rear yard required, standard depth). (c) does not speak to it.

M3 [F]: as M1 but X–Y = 230.01 ft.
- (b): [C] 230.01 not < 230 ⇒ not short ⇒ (b) does NOT apply (same as M2). (c) does not speak to it.

M4 [F]: X–Y = 229.80 ft from printed tax-map labels, 230.20 ft on city GIS outline; no survey.
- Which measurement does the text tell you to use? [?] NOT KNOWN. The short-dimension definition states only "measures less than 230 feet"; it names no source, instrument, or basis (survey vs tax map vs GIS). Missing: the authoritative measurement source/basis.
- Consequence: [?] Whether (b) applies is NOT KNOWN / conditional — short on the tax-map figure (229.80 < 230), not short on the GIS figure (230.20 ≥ 230). (c) does not speak to this interior one-street lot.

M5 [F]: block X‖Y 200 ft, P⊥Q 600 ft; lot interior, front on P, 50 on P, 100.00 ft deep.
- (b): [C] X–Y = 200 < 230 ⇒ P frontage short ⇒ (b) APPLIES. No rear yard within 100 ft of the P street line. The rear lot line sits at exactly 100.00 ft. [?] Whether a point at exactly 100.00 ft is "within 100 feet" is NOT resolved by the text (Q1b). If inclusive, the whole lot (incl. the rear lot line) is covered ⇒ no rear yard anywhere; if exclusive, the rear lot line at 100.00 is at the edge of the waiver. No part of the lot lies beyond 100 ft.
- (c): [C] Does not speak to M5 (interior, one street).

PART 4 of 7

M6 [F]: as M5 but 100.03 ft deep.
- (b): [C] Block still short (200 < 230) ⇒ (b) applies to the first 100 ft. But the rear lot line is at 100.03 ft — beyond 100 ft of the P street line. (b) waives the rear yard only "within 100 feet of such #street line#." Because the rear lot line lies beyond 100 ft, (b) does NOT waive it there, so a #rear yard# is required along that rear lot line under 23-342. [C] Net: no rear yard is required in the 0–100 ft band (waived by (b)), but the rear-yard requirement survives because the rear lot line is at 100.03 ft (> 100). [?] The text does not address how a required rear yard whose depth would reach back inside the 100-ft band interacts with (b); I read (b) as a location waiver keyed to the street line, so the requirement attaches at the beyond-100 rear lot line. (c) does not speak to M6 (interior, one street). This M5/M6 pair shows the result turns on the strict 100-ft line.

M7 [F]: block as M5; lot = corner lot at P×X, 100 ft on P, 150 ft on X, street lines meet at 90°; the other two lot lines adjoin interior lots.
- Each lot line's kind [C] (coordinates: P along y=0, X along x=0, lot x∈[0,100], y∈[0,150]):
  • P edge (y=0): #front lot line# (= P street line).
  • X edge (x=0): #front lot line# (= X street line).
  • Edge opposite P (y=150): parallel to P, but it meets the X street line at (0,150) ⇒ it "intersects" a bounding street line ⇒ NOT a rear lot line ⇒ #side lot line#.
  • Edge opposite X (x=100): parallel to X, meets the P street line at (100,0) ⇒ intersects ⇒ #side lot line#.
  ⇒ Two front lot lines, two side lot lines, NO rear lot line.
- (b): [C] P frontage is short (X–Y=200<230); the P front lot line coincides with the short-dimension street line ⇒ (b) APPLIES: no rear yard within 100 ft of the P street line (the band y≤100). The X frontage is NOT short (P–Q=600) so (b) does not apply via X.
- (c): [C] The corner portion = within 100 ft of each intersecting street line; the remaining portion (y∈(100,150]) is an interior/through portion, so (c) speaks to the lot. The side lot line x=100 intersects the P street line; its portion beyond 100 ft of P (y∈(100,150]) is "considered a #rear lot line#." [?] Whether a rear yard is then required there is (c)(1) vs (c)(3): NOT KNOWN — the facts say it "adjoins interior lots" but do not state the KIND (rear vs side) of the adjoining zoning lot's coinciding lot line. (The edge y=150 is within 100 ft of X everywhere, so it yields no (c) rear lot line.)

M8 [F]: block as M5; ONE zoning lot of two tax lots — tax lot A corner at P×X (100 on P, 100 on X), tax lot B interior next to A on X (50 on X, 100 deep); recorded as one zoning lot.
- [C] Combined geometry = x∈[0,100], y∈[0,150] (same as M7). The internal A/B boundary (y=100) is NOT a lot line of the zoning lot. Lot-line kinds are identical to M7: P edge front; X edge front; y=150 edge side (meets X street line at (0,150)); x=100 edge side (meets P street line at (100,0)). ⇒ Two front, two side, NO rear lot line. (This illustrates the zoning-lot definition's "may or may not coincide with a lot as shown on the official tax map": merging the tax lots erases the internal line.)
- (b): [C] P frontage short (200<230) ⇒ (b) APPLIES: no rear yard within 100 ft of the P street line.
- (c): [C] Speaks to the interior/through portion (y∈(100,150]); the x=100 side lot line's beyond-100-of-P part becomes a constructive rear lot line. [?] (c)(1) vs (c)(3) NOT KNOWN — the kind of the adjoining zoning lot's coinciding lot line east of x=100 is not stated.

M9 [F]: block bounded by streets X and Y (parallel, 220 ft apart), street P crossing at one end, and a PUBLIC PARK closing the block ~600 ft from P; lot interior, front on P, 50 on P, 100 deep.
- Does the park bound the block? [C] YES — the block definition lists "(b) #public parks#" as a bounding feature. So the block is bounded by X, Y, P (streets) and the public park.
- (b): [C] For the P frontage, the two bounding cross-streets are X and Y, 220 ft apart < 230 ⇒ P frontage short ⇒ (b) APPLIES: no rear yard within 100 ft of P (the whole 100-ft-deep lot). The park bounds the far end and does not enter the X–Y dimension that governs the P frontage. (Same [?] basis caveat as M1: the definition does not fix street-line vs centreline.)
- (c): [C] Does not speak to this interior one-street lot.

M10 [F]: four-sided block; X and Y NOT parallel (210 ft apart where they meet P, 250 ft where they meet Q); P–Q 500 ft; lot interior, front on P, 50 on P, 100 deep.
- How is the dimension to be measured? [?] NOT KNOWN. The short-dimension definition speaks of "the dimension between any two #streets#" but gives no rule for NON-parallel bounding streets: it does not say to measure at the P end (210), at the Q end (250), the average (230), or perpendicular. Missing: the measurement location/convention for non-parallel streets.
- Consequence: [?] Whether the P frontage is short, hence whether (b) applies, is NOT KNOWN / conditional — 210 ft (at the P frontage) < 230 ⇒ short; 250 ft (at Q) ≥ 230 ⇒ not short; 230 ft (average) is not < 230 ⇒ not short. The most natural reading (the P block frontage's own length = distance between X and Y at the P street line = 210 ft) gives short, but the text does not compel it.
- (c): [C] Does not speak to this interior one-street lot.

PART 5 of 7

=== Q5. THE REAL LOT (215-16 Northern Blvd, block 7334 lot 70; BBL 4073340070; R6B + C2-2 overlay as recorded [F] zoning_nyzd/zoning_nyco) ===

Geometry method (read-only; EPSG:2263 US survey feet [F] outlines units). I projected every lot-outline and centreline vertex onto a frame aligned to the Northern Boulevard frontage: origin at lot-1 NW corner G=(1048691.85,216386.03); u-axis along Northern Blvd (bearing 12.82°, east +); v-axis perpendicular, into the block (south +). Lot 70's own front-edge bearings gave the 12.82°. Key projected points [C]:
• Lot 1 (west, 215-10 Northern Blvd): G(u0,v0), B(u99.25,v0), A(u98.66,v99.97), F(u-0.59,v99.97). Spans u[-0.6,99.25], v[0,99.97].
• Lot 70 (east, 215-16 Northern Blvd): B(u99.25,v0), C(u203.13,v0), D(u202.59,v99.98), A(u98.66,v99.97). Spans u[98.66,203.13], v[0,99.98].
• Whole block (41 lots): u[-3.0,203.1] (span 206.1), v[0,545.4].
• Side-street centrelines within the block: 215 Street (west) mean u≈-30.8; 215 Place (east) mean u≈+230.1 [F] centrelines.

Q5a — bounding streets, widths, block dimensions, ALLEY:
[C]/[F] Streets bounding block 7334 (name | mapped Streetwidth, from streets_dcm_centerlines.json):
• Northern Boulevard — 100 ft (north; lots 1 and 70 front it).
• 215 Place — 60 ft (east side).
• 215 Street — 60 ft (west side).
• South end — [?] NOT KNOWN. No street centreline in the capture bounds the block's south edge within the block's frontage (within u -50..240, the only centreline near v≈545 is 215 Street continuing down the west side at u≈-32). The southernmost lot is 33 (45-54 215 Place) at v≈545. Missing: the identity of any street (or other feature) closing the block on the south.

Block dimension between OPPOSITE bounding streets, and on which basis [C]:
• Between the two SIDE streets (215 Street ↔ 215 Place), i.e., the length that governs the Northern Blvd frontage:
  – centreline-to-centreline ≈ 230.1 − (−30.8) = 261.0 ft (I averaged each side street's centreline u within the block).
  – tax-lot-outline edge-to-edge (west lot edge u≈−3 to east lot edge u≈+203) ≈ 206.1 ft. Along the Northern Blvd frontage specifically (G→C) ≈ 203.1 ft.
  – true STREET-LINE to STREET-LINE ≈ NOT KNOWN [?]: the centrelines file states "a street line lies half the mapped width from the centreline only where the street is mapped symmetrically, which this file does not state." If symmetric (−30.8+30 to +230.1−30) ≈ 199–201 ft, but symmetry is not given.
• Between Northern Blvd and the south street: lot-outline v-span ≈ 545 ft; centreline-to-centreline larger. On every basis this is ≫ 230 ft (not short).

From printed tax-map labels [F] printed_tax_map_labels.json: labels give LOT sizes, not a block width — lot 70 "100.76 ft on Northern Boulevard, 100 ft deep"; lot 1 "99.25 ft by 100 ft". Summing the two Northern Blvd frontages (if lots 1 and 70 together span the whole block frontage, which the outlines confirm: G at u≈0 near 215 Street, C at u≈203 near 215 Place) gives ≈ 99.25 + 100.76 = 200.0 ft between the side streets on the tax-map basis.

So the side-street separation is ≈ 200 ft (tax-map), ≈ 203–206 ft (GIS outline), ≈ 261 ft (centreline), and NOT KNOWN on a true street-line basis.

ALLEY [F]: labelled only on the 2021 tax map, "an ALLEY label across the southern part of the northern lots"; "whether the ALLEY is a mapped street, a private way or something else is not stated." [C]/[?] It could bound the block only if it is a #street# (or a park/railroad/airport/pierhead/City line); a private way is expressly not a #street#. Its status is NOT KNOWN, and as described it runs across the interior (south of the northern lots), not on the block perimeter, so on the folder's facts it does not bound the block along Northern Blvd. If it were a mapped #street#, it could split the block (changing the block's depth/identity) but would NOT change the ~200–261 ft side-street separation that governs the Northern Blvd frontage.

Q5b — is the Northern Blvd block frontage a "short dimension"? Is lot 70's front lot line on that street line? Rear yard within 100 ft?
[C]/[?] Short dimension? The governing figure is the side-street separation: ≈ 200 ft (tax-map) and ≈ 203–206 ft (GIS) are < 230 ⇒ SHORT; ≈ 261 ft (centreline) is ≥ 230 ⇒ NOT short. Because the definition does not fix the basis (Q1a), this is BASIS-DEPENDENT / NOT KNOWN. Most-defensible reading (block = land between the two street lines) ⇒ short; literal "between streets" leaves centreline open.
[S] Lot 70's front lot line on Northern Blvd: YES — settled: step-p3-worked#real-lot-lot-lines gives lot 70 as a corner lot with two front lot lines (the Northern Boulevard edge and the 215 Place edge), two side lot lines, and NO rear lot line.
[S] Reach: settled corner-reach#real-lot-reach — the whole lot is within 100 ft of the Northern Boulevard street line (max reach 99.97 ft); a strip ~3.93 ft wide (~390 sq ft) lies beyond 100 ft of the 215 Place street line; ~2,560 sq ft lies beyond 100 ft of the corner. So 100% of the lot is within 100 ft of the Northern Blvd street line.

PART 6 of 7

Q5b, continued — rear yard within 100 ft of the Northern Blvd street line:
Z1 (lot 70 alone) [S]+[C]: lot 70 has NO rear lot line, and a #rear yard# exists only along a #rear lot line# (zr-12-10-yard-rear.json) ⇒ under the base definitions no rear yard is required anywhere. The whole lot being within 100 ft of Northern Blvd, if (b) applies (short-dimension basis) it independently waives any rear yard within 100 ft of the Northern Blvd street line; and 23-344(a) independently waives rear yard within 100 ft of the corner (two street lines meeting at 90° ≤135°). ⇒ Within 100 ft of the Northern Blvd street line, NO rear yard is required, with ONE unresolved exception described in Q5c (the ~3.93 ft strip, where 23-344(c) can create a constructive rear lot line).
Z2 (lots 70+1 one zoning lot) [C]: the merged lot spans u[-0.6,203.1], v[0,99.98]; it fronts Northern Blvd (N), 215 Street (W) and 215 Place (E) — three streets — and adjoins two street intersections at ~90°, so it is a #corner lot#. Its south edge (v≈99.97) runs from the 215 Street street line (at F) to the 215 Place street line (at D); being parallel to Northern Blvd but intersecting both side-street street lines, it is a #side lot line#, not a rear lot line ⇒ Z2 also has NO base rear lot line (3 front + 1 south side). The merged lot's depth from Northern Blvd is ≤ ~100 ft ⇒ the whole merged lot is within ~100 ft of Northern Blvd. Same result: within 100 ft of the Northern Blvd street line, NO rear yard is required, subject to the same (c) exception (now along the south side lot line where it lies beyond 100 ft of a side street). [C] C2-2 overlay: per settled step-p4-worked#rear-yard, for an all-residential building the overlay does not change the rear yard — it follows R6B (23-342/343/344) [S] (settled flags one caveat: the ZR 34-23 capture holds only its title, so an unseen 34-23 sub-section modifying the rear yard cannot be fully ruled out — a residual [?]).

Q5c — beyond 100 ft of a street line, what does (c) say, which adjoining lot line, rear yard?
[C] Which part is beyond 100 ft: from the 215 Place street line (east, u≈203), points with u < 103 are beyond 100 ft — the west ~3.93 ft strip of lot 70 (settled reach 103.93 ft / ~390 sq ft). From the Northern Blvd street line nothing is beyond 100 ft (max 99.97). Under Z2 additionally, the middle of the merged lot (u between ~100 and ~103) is beyond 100 ft of BOTH side streets.
[C] (c) applies: lot 70 (and merged Z2) is a #corner lot# with an "#interior# or #through lot# portion" (the remaining portion beyond 100 ft of a street line). The side lot line D–A intersects the 215 Place street line (at D, u≈203); its portion beyond 100 ft of that street line (near A, u≈98.7–103) "shall be considered a #rear lot line#."
[F]/[C] Which adjoining lot: from the outlines, lot 70's south edge D–A adjoins lot 11 (45-12 215 Place) near D and lot 61 (45-11 215 Street) near A; the beyond-100-of-215-Place strip (near A) coincides with lot 61's boundary.
[?] Rear yard required there? NOT KNOWN. (c)(3) [R6–R12] gives "no #rear yard#" if the constructive rear lot line coincides with a #side lot line# of the adjoining zoning lot; (c)(1) requires a rear yard (per 23-342) if it coincides with a #rear lot line# of the adjoining zoning lot. The folder holds no zoning-lot membership, no zoning, and no lot-line classification for lots 61/11, so whether their coinciding line is a side or rear lot line is unknowable from it. Also NOT KNOWN: whether R6B counts within "R6 through R12" for (c)(3) (suffix point). Note the strip is within 100 ft of Northern Blvd, so IF (b) applies (short-dimension basis) it waives any rear yard there; IF (b) does not apply (centreline basis), only (c) governs and the result is NOT KNOWN.

Q5d — real-lot result table (variant | rear yard required? where? | deciding words | fact that would settle it):

| Variant | Rear yard required? where? | Deciding words | What would settle it |
|---|---|---|---|
| Z1, street-line/tax-map basis (≈200–206 ft < 230 ⇒ short) | NO within 100 ft of Northern Blvd (whole lot); the ~3.93 ft strip is also within 100 ft of NB, so covered by (b) | 23-344(b): "no #rear yard# shall be required within 100 feet of such #street line#" (+ no rear lot line, settled) | Which measurement basis the ZR's "dimension between any two #streets#" intends |
| Z1, centreline basis (≈261 ft ≥ 230 ⇒ not short) | NO within 100 ft of NB via "no rear lot line" (settled) + 23-344(a) corner waiver; EXCEPT the ~3.93 ft strip = NOT KNOWN | 23-344(c)(1) vs (c)(3); 12-10 rear-yard (no rear lot line) | Kind (side vs rear) of lot 61's coinciding lot line; whether R6B is within "R6–R12" |
| Z2, street-line/tax-map basis (short) | NO within 100 ft of NB (whole merged lot); A–B edge is internal | 23-344(b) same words (+ no rear lot line) | Same basis question; AND whether lots 70+1 are one zoning lot |
| Z2, centreline basis (not short) | NO via "no rear lot line"; EXCEPT the south side lot line where beyond 100 ft of a side street = NOT KNOWN | 23-344(c)(1) vs (c)(3) | Adjoining zoning lots' lot-line kinds along the south edge; Z1/Z2 status |

Q5e — what changes on a different basis; every basis-dependent answer:
[C]/[?] The measurement basis for the side-street separation changes: (1) whether the Northern Blvd frontage is a "short dimension of a block" (short on tax-map ≈200 and GIS ≈203–206; not short on centreline ≈261; NOT KNOWN on a true street-line basis); and therefore (2) whether 23-344(b) applies to lot 70 / the merged lot; and therefore (3) whether the ~3.93 ft (c) strip's rear-yard question is disposed of by (b) (waived) or left to (c)(1)/(c)(3) (NOT KNOWN). NOT basis-dependent: the block's Northern-Blvd-to-south depth (~545 ft, ≫230 on any basis); the settled lot-line kinds; the settled reach (whole lot within 100 ft of Northern Blvd).

PART 7 of 7

=== Q6. WHAT IS MISSING ===

Sections / defined terms the texts I used point to but the folder does not hold (pointing words ≤25 words; the answer each leaves open):
• General "#lot line#" definition — the rear/side/front-lot-line and yard definitions all build on "#lot line#", but no standalone 12-10 "lot line" capture exists. [?] Leaves the base lot-line test slightly under-sourced; I used the front/rear/side captures directly.
• 23-38 / 23-72 and special-district rear-yard rules — the 23-344 source note points to "every interaction with Sections 23-342, 23-343, 23-38, 23-72, any commercial overlay or special district". Not in folder. [?] Could add further modifications; left unverified.
• ZR 34-23 full text — settled sheet flags its capture holds only the title line. [?] An unseen 34-23 sub-section modifying the rear yard cannot be ruled out (settled answer 4 caveat); the C2-2 overlay rear-yard conclusion stays conditional.
• #street setback line# mapping for this lot — definition limits them to Staten Island or Queens CD 10; the lot's community district is not stated. [?] If one existed it would "supersede the #street line#" for yards; left as a residual, likely inapplicable.
• 23-342 cross-refs (#base plane#, #lot width#, detached/attached #building# types) — present as defined terms but not needed because lot 70 has no rear lot line.

Missing FACTS about the real lot that an answer turned on:
• The authoritative measurement basis for the side-street separation (tax-map ≈200 / GIS ≈203–206 / centreline ≈261; true street lines unknown because symmetric mapping "is not stated") — turns the short-dimension / 23-344(b) answer.
• Whether lots 70 and 1 are one zoning lot (Z1 vs Z2) — no zoning-lot description, deed, or Declaration in the folder.
• The zoning-lot membership, zoning, and lot-line classification (side vs rear) of lots 61 and 11 (and any lot south of the merged lot) — turns 23-344(c)(1) vs (c)(3) for the beyond-100-ft strip.
• The identity of the street (or feature) bounding the block on the south — no centreline in the capture.
• The ALLEY's status (mapped street / private way / other) and exact location — "not stated on the labels read."
• Whether "R6 through R12 Districts" includes the R6B suffix for (c)(3) — captured text does not enumerate suffixes.

=== Q7. ONE-LINE SUMMARY PER QUESTION ===
Q1: 23-344(b) waives the rear yard within 100 ft of a front-lot-line/street-line that sits on a block's "short dimension" (side-street separation < 230 ft, strict); the definition does not fix whether that separation is measured between street lines or centrelines (NOT KNOWN); a public park can bound a block, a private way cannot unless it is itself a #street#.
Q2: 23-344(c) turns the beyond-100-ft part of a corner/multi-street lot's side lot line (measured from the street line it intersects) into a constructive rear lot line, and (c)(1) vs (c)(3) depends only on whether the adjoining zoning lot's coinciding line is a rear or side lot line — the adjoining lot's district is irrelevant; R6–R12 (c)(3) = none.
Q3: (a)–(d) are separate, non-exclusive modifications of 23-342/343; (b) is not barred on corner lots; where a point lies beyond 100 ft of (b)'s street line, (c) can still create a rear lot line — the text does not sequence overlaps (NOT KNOWN).
Q4: M1 short/(b) applies; M2 & M3 not short (strict <230); M4 NOT KNOWN (no stated basis); M5 short/(b), rear lot line at exactly 100 ft (boundary NOT KNOWN); M6 short but rear lot line at 100.03 ft ⇒ not waived, rear yard required; M7 & M8 two front + two side + no rear lot line, (b) applies, (c) strip NOT KNOWN; M9 park bounds the block and (b) applies (220<230); M10 NOT KNOWN (no measurement convention for non-parallel streets); (c) touches only M7/M8.
Q5: Block 7334 is bounded by Northern Blvd (100 ft), 215 Place (60 ft), 215 Street (60 ft) and an unidentified south edge; the Northern Blvd frontage is a "short dimension" on the tax-map/GIS basis (~200–206 ft) but not on the centreline basis (~261 ft) = BASIS-DEPENDENT/NOT KNOWN; lot 70's front lot line is on the Northern Blvd street line (settled); the whole lot is within 100 ft of that street line and has no rear lot line, so no rear yard is required within 100 ft under Z1 and Z2, except the ~3.93 ft strip beyond 100 ft of the 215 Place street line where 23-344(c)(1)/(c)(3) leaves the result NOT KNOWN (adjoining lot-line kind unknown); the ALLEY is not shown to bound the block.
Q6: Missing texts (general #lot line#, 23-38/23-72, full 34-23, setback-line mapping) and missing facts (measurement basis, Z1/Z2 status, neighbours' zoning-lot/line kinds, the south street, the ALLEY's status, R6B-in-"R6–R12") hold several answers at NOT KNOWN/conditional.
Q7: This is the per-question summary.

END-OF-REPORT
