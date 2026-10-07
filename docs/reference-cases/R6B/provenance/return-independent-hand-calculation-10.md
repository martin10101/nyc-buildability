# Independent reading from the step-P4 sealed folder, reading 2 (provenance)

What this is: one of two independent readings made on 2026-10-07, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - all 110 pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, and two made-up lots - with no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 2 of the step-P4 pair; a value is recorded in a step-P4 reference-case row only where this reading and reading 1 (return-independent-hand-calculation-9.md) give the same answer on the same basis.

---

PART 1 of 7

This is a DRAFT reading of captured law text by an AI. It is NOT legal advice and NOT a professional review. It returns no verdict and verifies nothing in any repository.

I obeyed the one hard rule: I worked ONLY from the sealed folder `.../scratchpad/sealed-p4` and wrote only in my own scratch folder. I did NOT open, list or search anything under `/root/project`. I opened NO web page and ran no web search (the official-site fallback does not apply to this task; where a text is missing I say NOT KNOWN and name it). I used only each law file's `verbatim_excerpt` and the `table`/`tables` fields; I did not rely on any summary/"provisions" block. In the quotes below, `#...#` marks a defined term exactly as captured.

FILES I READ
Facts (5): lot_facts_pluto.json; lot_outline_epsg2263.json; made_up_lots.json; streets_dcm_centerlines.json; zoning_nyco_query_C2-2.json; zoning_nyzd_query_R6B.json. (I also read INDEX.json.)
Law – definitions (12-10): wide/narrow street (zr-12-10.json); residence-or-residential; dwelling-unit; rooming-unit; qualifying-affordable-housing; qualifying-senior-housing; qualifying-residential-site; residential-equivalent; large-site; mixed-building; lot-coverage; yard; yard-rear; yard-equivalent-rear; yard-front; yard-side; street-wall; prevailing-street-wall-frontage; curb-level; lot-corner; lot-interior; lot-through; lot-line-front; lot-line-rear; lot-line-side; lot-width; lot-depth; zoning-lot; street-line; floor-area; lot-area; special-density-areas.
Law – sections: zr-23-22; 23-311; 23-312; 23-341; 23-342; 23-343; 23-344; 23-362; 23-43; 23-431; 23-432; 23-44; 23-441; 23-442; 23-443; 23-52; 34-11; 34-111; 34-21; 34-22; 34-221; 34-222; 34-223; 34-224; 34-23; 34-231; 34-232; 34-233; 34-24; 35-22; 35-53; 35-62; 35-63; 35-631; 35-64; 35-641; 35-642; 35-643.
(Files present but NOT read are listed in Q10.)

KEY FACTS USED
[F] Real lot 215-16 Northern Boulevard, BBL 4073340070: zonedist1 "R6B", overlay1 "C2-2", splitzone false, lotarea "10075" (sq ft), lotfront "100.76" ft, lotdepth "100.0" ft, lottype "3", cd "411" (lot_facts_pluto.json). [?] The meaning of lottype "3" is not given in the folder.
[F] Outline Shape__Area 10387.99 sq ft; EPSG:2263 US survey feet (lot_outline_epsg2263.json).
[F] Streets at the lot: Northern Boulevard Streetwidth "100", Route_Type "Mjr_st"; 215 Place "60"; 215 Street "60"; 45 Road "50" (streets_dcm_centerlines.json).
[C] Northern Boulevard width 100 ft is a #wide street# ("A 'wide street' is any street 75 feet or more in width", zr-12-10.json); 215 Place at 60 ft is a #narrow street# ("any street less than 75 feet wide").

=== Q1. ZR 34-22 AND ITS SECTIONS ===

Q1a — section by section, with the district line quoted:
[C] 34-11 (zr-34-11) applies to "C1 C2 C3 C4 C5 C6": "the #bulk# regulations of Article II, Chapter 3, shall apply to all #residential buildings# ... except as modified by the provisions of Sections 34-21 through 34-24." Makes the R6-R12 bulk rules apply to residential buildings in C districts.
[C] 34-21 (zr-34-21), "C1 C2 C3 C4 C5 C6": the 34-11 bulk rules "are modified by ... Sections 34-22 ..., 34-23 ... and 34-24 .... The purpose ... is to make the regulations ... applicable to #Commercial Districts#."
[C] 34-22 (zr-34-22), "C1 C2 C3 C4 C5 C6": "the #floor area# and #open space# regulations as set forth in Section 23-20 ... and made applicable ... in Section 34-11 ... are modified as set forth in this Section." (Header for 34-221..224.)
[C] 34-221 (zr-34-221), "C1 C2 C3 C4 C5 C6": "the maximum #floor area ratio# on a #zoning lot# shall be the applicable maximum #floor area ratio# permitted pursuant to ... Article II, Chapter 3, except as provided for in ... Section 34-223 ... [and] Section 34-224 .... However, for #Commercial Districts# with a #residential equivalent# of an R10 or R11 District with a letter suffix, no #floor area# bonuses ... shall be permitted."
[C] 34-222 (zr-34-222), "C1 C2 C3 C4 C5 C6": a non-residential use in "a #building# ... in existence on December 15, 1961, may be changed to a #residential use# and the regulations pertaining to maximum #floor area ratio# shall not apply to such change of #use#."
[C] 34-223 (zr-34-223) applies only to "C4-6 C4-7 C4-11 C4-12 C5 C6-4 C6-5 C6-6 C6-7 C6-8 C6-9 C6-11 C6-12": a public-plaza floor-area bonus (6 sq ft per sq ft of #public plaza#, over the 23-22 amount).
[C] 34-224 (zr-34-224) applies only to "C4-6 C4-7 C4-11 C4-12 C5-1 C5-2 C5-4 C6-4 C6-5 C6-8 C6-11 C6-12": an arcade floor-area bonus (3 sq ft per sq ft of #arcade#).
[C] 23-22 (zr-23-22), "R6 Through R12": the maximum residential FAR table; the R6B row = standard residences "2.00", qualifying affordable/senior "2.40" (no footnote on the R6B row).

Q1b — for a residential building in C2-2 within R6B, does each change the max residential FAR / buildable floor area?
[C] 34-11 — APPLIES ("C1 C2 ...", "all #residential buildings#"); it imports the R6-R12 FAR, it does not itself change the number.
[C] 34-21 — APPLIES ("C1 C2 ..."); introductory, changes no number itself.
[C] 34-22 — APPLIES ("C1 C2 ..."); header, the operative rule is 34-221.
[C] 34-221 — APPLIES ("C1 C2 ..."); it fixes the max FAR at the Article II Ch 3 value (R6B standard = 2.00 per 23-22) and allows only the 34-223/34-224 bonuses. The R10/R11-letter-suffix sentence is irrelevant to R6B. So NO CHANGE vs plain R6B.
[C] 34-222 — DOES NOT APPLY: deciding words "a #building# ... in existence on December 15, 1961, may be changed". The subject is a NEW building, not a change of use.
[C] 34-223 — DOES NOT APPLY: C2-2 is not in its district line ("C4-6 ... C6-12").
[C] 34-224 — DOES NOT APPLY: C2-2 is not in its district line.
[C] Net: the C2-2 overlay (Chapter 4 floor-area sections) leaves the maximum residential FAR and the buildable floor area the SAME as plain R6B — 2.00 FAR, with no plaza/arcade bonus available to a C2 district.

PART 2 of 7

=== Q2. ZR 34-23 AND ITS SECTIONS; yards on the real corner lot ===

Q2a — section by section:
[C] 34-23 (zr-34-23) — capture holds ONLY the heading "34-23 Modification of Yard and Open Area Regulations"; no district line and no operative text. It is a header for 34-231/232/233.
[C] 34-231 (zr-34-231), "C1 C2 C3 C4 C5 C6": "no #front yard# shall be required for any #residential building#."
[C] 34-232 (zr-34-232), "C1 C2 C3 C4 C5 C6": "no #side yard# shall be required for any #residential building#. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet ... The allowances for permitted obstructions ... set forth in Sections 23-311 and 23-312 shall be permitted in such open areas."
[C] 34-233 (zr-34-233), "C1 C2 C3 C4 C5 C6": a non-residential use in "a #building# ... in existence on December 15, 1961, may be changed to a #residential use# and the regulations pertaining to minimum required #open space ratio# shall not apply to such change".
[C] There is NO 34-23x rear-yard section in the folder (only front yard, side yard, change-of-use). So Chapter 4 does not modify the rear yard.

Supporting facts on the real lot being a corner lot:
[C] From the outline (lot_outline_epsg2263.json), the five vertices form an ~100 x ~104 ft quadrilateral (edge B–C ≈ 103.9 ft, C–D ≈ 100.0 ft; interior angle at C ≈ 90°; area ≈ 10,388 sq ft).
[C] Edge B–C lies ≈ 51.1 ft from the Northern Boulevard centerline (half of its 100 ft width = 50 ft) → on the Northern Boulevard street line. Edge C–D lies ≈ 28.9 ft from the 215 Place centerline (half of its 60 ft width = 30 ft) → on the 215 Place street line. 215 Street is ≈ 179 ft away (not adjacent).
[C] So the lot fronts TWO intersecting streets (Northern Boulevard and 215 Place) meeting at vertex C at ≈ 90°. Against zr-12-10-lot-corner: a "#corner lot#" is "a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle ... forms an angle of 135 degrees or less." 90° ≤ 135° → consistent with a corner lot. [F] PLUTO lottype "3" is recorded but [?] its meaning is not in the folder.
[C] zr-12-10-yard-front: "In the case of a #corner lot#, any #yard# extending along the full length of a #street line# shall be considered a #front yard#." zr-12-10-yard-side: "In the case of a #corner lot#, any #yard# which is not a #front yard# shall be considered a #side yard#." So on this lot both street frontages are front-yard positions; non-street yards are side yards.

Q2b — does any 34-23 section change the rear / side / front yard the R6B rules require or don't?
[C] FRONT yard — 34-231 APPLIES ("C1 C2 ..."): no front yard required for the residential building, along either street. [?] NOT KNOWN whether this CHANGES R6B, because the folder holds no R6/R6B front-yard requirement section (e.g. a 23-32); the captured R6-R12 yard rules (23-34 group) address only rear yards. Net effect: no front yard required.
[C] SIDE yard — 34-232 APPLIES: no side yard required; any open area along a #side lot line# provided at any level must be ≥ 5 ft wide, with 23-311/23-312 obstructions allowed there. [?] NOT KNOWN whether this changes R6B, for the same reason (no R6/R6B side-yard requirement section in the folder). Net effect: no side yard required.
[C] CHANGE OF USE — 34-233 DOES NOT APPLY: the subject is a new building, not a pre-1961 non-residential building being changed.
[C] REAR yard — no 34-23 section modifies it; therefore the overlay does NOT change the rear yard. The rear yard is governed by the underlying R6B rules (23-342/23-343/23-344). For this corner lot: 23-344(a) "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." The Northern Boulevard/215 Place lines meet at ≈ 90° ≤ 135°, and the lot extends only ≈ 100 ft from that corner, so within 100 ft of the corner no rear yard is required. 23-344(c)/(d) govern any portion beyond 100 ft of a street line (in R6-R12, "no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#", but a rear yard is required where it coincides with an adjoining #rear lot line#). [?] NOT KNOWN whether any part of the lot lies beyond 100 ft of a street line and how the adjoining zoning lots' lot lines run — the folder has no adjoining-lot data and no metes-and-bounds lot-line labels, so the exact beyond-100-ft treatment cannot be settled.

PART 3 of 7

=== Q3. THE OVERLAY, AFTER Q1 AND Q2 ===

[C] FLOOR AREA RATIO — SAME as plain R6B. 34-221 fixes the max FAR at "the applicable maximum #floor area ratio# permitted pursuant to ... Article II, Chapter 3" (zr-34-221), i.e. the 23-22 R6B value 2.00; the only exceptions (34-223 public plaza, 34-224 arcade) do not list C2-2, so no bonus is available. The earlier readers' "subject to these sections" is borne out: the sections confirm 2.00 and add nothing for C2.
[C] LOT COVERAGE — SAME as plain R6B. No captured overlay section changes it; it is governed by the underlying R6B rule 23-362(a): "the maximum #residential# #lot coverage# for #interior lots# ... shall be 80 percent and ... for #corner lots# shall be 100 percent." For this corner lot the corner-lot portion is allowed 100%.
[C] REAR YARD — SAME as plain R6B: the Chapter 4 overlay sections do not touch the rear yard (Q2), so the R6B rear-yard rules apply unchanged; for this corner lot, 23-344(a) waives the rear yard within 100 ft of the ≈ 90° corner. [?] The exact treatment of any beyond-100-ft portion stays NOT KNOWN (adjoining-lot / lot-line facts missing).
[C] DOES ANY CAPTURED OVERLAY TEXT SPEAK OF LOT COVERAGE? No. The Chapter 4 modification sections speak of "#floor area#" and "#open space#" (34-22), "maximum #floor area ratio#" (34-221/222), "#front yard#" (34-231), "#side yard#" (34-232) and "#open space ratio#" (34-233); none uses the term "#lot coverage#". (35-53, read for Q2/Q3, addresses a mixed building's rear yard, not lot coverage.) So "lot coverage" for this lot comes only from the underlying R6B section 23-362.

=== Q4. ZR 35-22, 35-62, 35-63, 35-64, 35-641..643; all-residential building in C2-2/R6B ===

[C] Definition quoted (zr-12-10-mixed-building): "A '#mixed building#' is a #building# in a #Commercial District# used partly for #residential use# and partly for #community facility# or #commercial use#." → An ALL-residential building is NOT a mixed building (it is not partly community-facility/commercial). Any rule keyed to "#mixed buildings#" does not reach it by its words.

To which buildings does each apply, and does it reach an all-residential building in C2-2/R6B?
[C] 35-22 (zr-35-22), "C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5": "the #bulk# regulations for the #Residence Districts# within which such #Commercial Districts# are mapped apply to #residential# portions of #buildings#", with the same (a)/(b) R1-R5 carve-outs as 34-111. C2-2 is in the list and the R6B surrounding district governs. For an all-residential building the "#residential# portion" is the whole building, so 35-22 reaches it IN SUBSTANCE (surrounding-R6B bulk). [?] Whether 35-22 (Article III Ch 5) is the governing section for an all-residential building, or whether 34-111 (Ch 4) governs and 35-22 governs only mixed/CF buildings, is NOT KNOWN — the Chapter 5 scope/applicability provision (e.g. a 35-00/35-20/35-21) is not in the folder. The outcome is identical either way (R6B bulk).
[C] 35-62 (zr-35-62) — DOES NOT APPLY: deciding words "In #Commercial Districts# mapped within, or with a #residential equivalent# of an R1 through R5 District". C2-2 here has an R6B (R6) equivalent, not R1-R5.
[C] 35-63 (zr-35-63), "C1 C2 C4 C5 C6", "mapped within, or with a #residential equivalent# of R6 through R12 Districts" — APPLIES. C2-2/R6B has R6-R12 equivalency; and 34-24(b)(1) (zr-34-24) directs that in such districts "the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied." So 35-63 (and 35-631 street wall within it) governs the all-residential building's height/setback.
[C] 35-64 (zr-35-64) — heading only in the capture ("Special Provisions for Certain Areas"); no operative text. Its subsections:
[C] 35-641 (zr-35-641), "C1 C2 C4 C5 C6" — DOES NOT APPLY to C2-2/R6B: it modifies the tower rules only "(a) ... an R9D or R10X District" and "(b) In C1 or C2 Districts mapped within R9 or R10 Districts without a letter suffix, or in C1-8, C1-9, C2-7 or C2-8 Districts ... for #mixed buildings#". R6B is none of these, and (b) is for mixed buildings.
[C] 35-642 (zr-35-642) — DOES NOT APPLY: every branch names a specific out-of-borough geography — Manhattan CD6 (a), Brooklyn CDs 8/9 and 3/5/16 (b), Bronx CD1 (c). The real lot is in Queens CD "411" (Community District 11, Queens).
[C] 35-643 (zr-35-643) — (a) applies to "#zoning lots# or portions thereof within 100 feet of a #street line# along a #transportation-infrastructure-adjacent frontage#". [?] NOT KNOWN whether the lot has such frontage: the defined term "#transportation-infrastructure-adjacent frontage#" is not in the folder and no fact states the lot adjoins transportation infrastructure. On the recorded facts there is no indication it does, so most likely it does not apply, but the fact is missing → NOT KNOWN.
[C] Summary: of the named sections, 35-63 (height/setback, via 34-24) applies to the all-residential building, and 35-22 reaches its bulk in substance (governing-chapter detail NOT KNOWN); 35-62, 35-641, 35-642 do not apply; 35-643(a) is NOT KNOWN for want of a frontage fact. None of the mixed-building-specific rules reach an all-residential building.

PART 4 of 7

=== Q5. LOT COVERAGE AND THE YARDS, AS DEFINED ===

Q5a — lot coverage (zr-12-10-lot-coverage), quoted:
"'#Lot coverage#' is that portion of a #zoning lot# which, when viewed directly from above, would be covered by a #building# or any part of a #building#. However, for purposes of computing a #height factor#, any portion of such #building# covered by a roof which qualifies as #open space#, or any terrace, balcony, breeze way, or porch or portion thereof not included in the #floor area# of a #building#, shall not be included in #lot coverage#. ... When a #height factor# is not computed for a #residential building# or #residential# portion of a #building#, obstructions permitted pursuant to Section 23-341 ... shall not be included in #lot coverage#, except that the portion of any balcony which does not project from the face of the #building# shall be counted as #lot coverage#."
[C] COUNTS: the above-view footprint of a building or any part of a building.
[C] LEAVES OUT: when computing a #height factor# — building area under a roof that qualifies as #open space#, and terraces/balconies/breezeways/porches not counted in #floor area#; and when no #height factor# is computed for a residential building — the 23-341 permitted obstructions (except a balcony not projecting from the building face, which counts). [?] "#height factor#" and "#open space#" are used but their definitions are not in the folder.
[C] The definition's worked example (a 20,000 sq ft lot split 100x100 corner / 100x100 interior; interior 70% = 7,000 sq ft, corner 100% = 10,000 sq ft) is illustrative text, not the R6B maxima; the R6B maxima are in 23-362 (80% interior / 100% corner).

Q5b — yard definitions (verbatim):
[C] Yard (zr-12-10-yard): "A '#yard#' is that portion of a #zoning lot# extending open and unobstructed from the lowest level to the sky along the entire length of a #lot line#, and from the #lot line# for a depth or width set forth in the applicable district #yard# regulations. Where a #street setback line# is shown on the City Map the #yard# extends along the entire length of the #street setback line# ...".
[C] Rear yard (zr-12-10-yard-rear): "A '#rear yard#' is a #yard# extending for the full length of a #rear lot line#."
[C] Rear yard equivalent (zr-12-10-yard-equivalent-rear): "A '#rear yard equivalent#' is an open area which may be required on a #through lot# as an alternative to a required #rear yard#."
[C] Front yard (zr-12-10-yard-front): "A '#front yard#' is a #yard# extending along the full length of a #front lot line#. In the case of a #corner lot#, any #yard# extending along the full length of a #street line# shall be considered a #front yard#."
[C] Side yard (zr-12-10-yard-side): "A '#side yard#' is a #yard# extending along a #side lot line# from the required #front yard# (or from the #front lot line# if no #front yard# is required) to the required #rear yard# (or to the #rear lot line#, if no #rear yard# is required). In the case of a #corner lot#, any #yard# which is not a #front yard# shall be considered a #side yard#."

Q5c — what may stand in a required rear yard or rear yard equivalent of a residential building in R6B (LIST ONLY, each with quoted item and any size limit). 23-341(a) and (b) each say "the obstructions set forth in Sections 23-311 and 23-312, as well as the following" are permitted, so the list is 23-311 + 23-312 + 23-341's own list.

From 23-341 (zr-23-341) own list:
- (a)(1) "Breezeways" — no size limit stated.
- (a)(2) "Fire escapes" — none stated.
- (a)(3) "Greenhouses, non-commercial, #accessory#" — "limited to one #story# or 15 feet in height ... whichever is less, and limited to an area not exceeding 25 percent of a required #rear yard#".
- (a)(4) "Recreational or drying yard equipment" — none stated.
- (a)(5) "Sheds, tool rooms or other similar #accessory# #buildings or other structures# for domestic or agricultural storage" — "height not exceeding 10 feet above the level of the #rear yard# or #rear yard equivalent#".
- (a)(6) "Solar energy systems, #accessory# or as part of an #energy infrastructure equipment#" — on roof of a permitted-obstruction building "up to four feet in height" (18 inches on a #detached# accessory building or roof slope > 20°); on solar canopies over unenclosed accessory parking "height shall not exceed 15 feet above ... adjoining grade".
- (a)(7) "Water-conserving devices ... in #buildings# existing prior to May 20, 1966" — "located not less than eight feet from any #lot line#".
- (b)(1) "Balconies, unenclosed, subject to the provisions of Section 23-62" — [?] 23-62 not in folder.
- (b)(2) "Parking spaces, off-street, #accessory#, for automobiles or bicycles": (i) accessory to a single-/two-family residence — building "not exceed 10 feet in height ... and ... #detached#"; (ii) accessory to any other building containing residences — within the rear yard "not exceed 15 feet above #base plane#" (plus decks/parapets etc. ≤ 18 in); (iii) enclosed accessory bicycle parking — area not exceeding that excludable under 25-85.
- (b)(3) "any portion of a #building# used for #residential uses# other than #dwelling units# in #buildings# containing #qualifying senior housing#" — requires "(i) such #zoning lot# is located in an R6 through R12 Districts OTHER THAN R6B, R7B or R8B". NOTE: by its own words this item is NOT available in R6B.
- (b)(4) "for #single-# or #two- family residences#, any portion of a #building# used for #residential uses#" — heights 1 story/15 ft or 2 stories/25 ft as specified; "size ... not exceeding one-third of the #rear yard# or #rear yard equivalent#"; if free-standing "not ... closer than five feet to a #rear lot line# or #side lot line#".
- Closing clause: "no portion of a #rear yard equivalent# which is also a required #front yard# or required #side yard# may contain any obstructions not permitted in such #front yard# or #side yard#."

PART 5 of 7

Q5c continued — from 23-311 (zr-23-311), permitted in any required yard/rear yard equivalent:
- (a) "#Accessory# mechanical equipment, limited in depth to 18 inches from an exterior wall".
- (b) "Arbors or trellises".
- (c) "Awnings and other sun control devices" — above the first story: "maximum projection ... of 2 feet, 6 inches" and solid surfaces "no more than 30 percent of the area of the #building# wall".
- (d) "Bicycle or micromobility parking, including necessary ancillary structures".
- (e) "Canopies".
- (f) "Chimneys, projecting not more than three feet into, and not exceeding two percent of the area of, the required #yard# or #rear yard equivalent#".
- (g) "Eaves, gutters, downspouts ... not more than 16 inches or 20 percent of the width ... whichever is the lesser".
- (h) "Electric vehicle charging equipment".
- (i) "Flagpoles".
- (j) "#Qualifying exterior wall thickness#".
- (k) "Ramps or lifts for people with physical disabilities".
- (l) "Solar energy systems" — on walls existing 4/30/2012 "projecting no more than 10 inches and occupying no more than 20 percent of the surface area"; or above other obstructions "limited to 18 inches".
- (m) "Terraces or porches, open".
- (n) "Window sills, or similar projections ... not more than four inches".

From 23-312 (zr-23-312), also permitted in any yard/rear yard equivalent:
- (a) "Balconies, unenclosed ... Such balconies are not permitted in #side yards# or within five feet of the #side lot line# or #rear lot line# in a #rear yard# or #rear yard equivalent#".
- (b) "Fences, not exceeding four feet in height ... in any #front yard#" (corner lots up to six feet in part of one front yard).
- (c) "Fire escapes, projecting into a #front yard#, only ... for the #conversion# of a #building# in existence before December 15, 1961".
- (d) "Overhanging portions of a #single-# or #two-family residence# ... project not more than three feet into the #front yard#" (lowest level ≥ 7 ft above front yard; supports ≤ 15% of area underneath).
- (e) "Parking spaces for automobiles, off-street, open, #accessory#, within a #side# or #rear yard#".
- (f) "Parking spaces, off-street, open, within a #front yard# ... #accessory# to a #building# containing #residences#" (with the R4B/R5B/R5D and qualifying-residential-site front-yard prohibitions, etc.).
- (g) "#Energy infrastructure equipment# and #accessory# mechanical equipment" — size ≤ 25% of a required yard/rear yard equivalent (front yards also ≤ 25 sq ft); height "in R6 through R12 Districts, a height of 15 feet above the adjoining grade".
- (h) "Steps ... access only the lowest #story# or #cellar# of a #building# fronting on a #street#".
- (i) "Swimming pools, #accessory#, above-grade ... not exceeding eight feet above the level of the #rear yard# or #rear yard equivalent#" (not in any front yard).
- (j) "Walls, not exceeding eight feet in height ... and not exceeding four feet in height in any #front yard#" (corner lots up to six feet in part).
[C] I applied nothing; this is the list only. The one item explicitly barred in R6B is 23-341(b)(3).

=== Q6. THE STREET WALL ===

Q6a — definitions (verbatim):
[C] Street wall (zr-12-10-street-wall): "A '#street wall#' is a wall or portion of a wall of a #building# facing a #street#."
[C] Prevailing street wall frontage (zr-12-10-prevailing-street-wall-frontage): "A '#prevailing street wall frontage#' shall refer to #block# frontages where, within 150 feet of the #street wall# of a subject #building#, at least half of the #aggregate width of street walls# on the same side of the #block# are within two feet of the average distance of such #street walls# from the #street line#. The total #aggregate width of street walls# shall not be less than 100 feet. The 150-foot selection may be measured in either direction from the subject property, or ... from both directions ...". It then gives the averaging method: each ≥5 ft #street wall# segment's distance from the street line times its width, summed, divided by total aggregate width = average distance; the frontage qualifies if the percentage of segments within two feet of that average exceeds 50 percent.
[C] Curb level (zr-12-10-curb-level): "'#Curb level#' is the mean level of the curb adjoining a #zoning lot#. On #corner lots#, #curb level# is the average of the mean levels of the adjoining curbs on intersecting #streets#, except that, for the purpose of regulating ... #yards# ... on #corner lots#, the #curb level# is the highest of the mean levels ...". (Plus the through-lot and base-plane variants quoted in the capture.)

Q6b — 35-631 and 23-431 both use "#prevailing street wall frontage#". What must be known to say whether the real lot has one, and which facts are in the folder?
[C] From the definition, to decide a prevailing street wall frontage you must know, for each block frontage (here Northern Boulevard and 215 Place), within 150 ft of the subject building's street wall and on the same side of the block: (i) the location of the #street line#; (ii) each existing neighbouring building's #street wall# segments of ≥ 5 ft width; (iii) each such segment's perpendicular distance from the street line; (iv) each segment's width; (v) the #aggregate width of street walls# (which must total ≥ 100 ft); and (vi) whether > 50% of that aggregate width lies within 2 ft of the width-weighted average distance.
[C] In the folder: the #street line# positions can be derived from the centerlines and mapped widths (streets_dcm_centerlines.json), and the subject lot's own frontages (≈ 103.9 ft on Northern Boulevard, ≈ 100 ft on 215 Place) from the outline.
[?] NOT KNOWN / NOT IN THE FOLDER: every fact about the NEIGHBOURING buildings — their street-wall segment positions, setbacks from the street line, widths, heights and the aggregate width on each block side. The folder has no data on neighbouring buildings. Therefore whether the real lot has a #prevailing street wall frontage# on either street is NOT KNOWN. Consequently the 23-431(a) R6B line-up rule (which needs "existing adjacent #building#" positions within 15 ft of the street line, within 25 ft of the subject, height > 35 ft) and the "where ... do not have a #prevailing street wall frontage#" fallback to 23-431(b) cannot be resolved from the folder.

PART 6 of 7

=== Q7. LARGE SITES AND QUALIFYING RESIDENTIAL SITES ===

Q7a — large site (zr-12-10-large-site), quoted: "A '#large site#' is either a single #zoning lot# with a #lot area# of at least 1.5 acres, or two or more #zoning lots# under single fee ownership or alternate ownership arrangements that are contiguous or would be contiguous but for their separation by a #street# with a #lot area# of at least 1.5 acres."
[C] 1.5 acres = 1.5 × 43,560 sq ft = 65,340 sq ft (standard acre = 43,560 sq ft).
[C] Real lot: recorded lotarea 10,075 sq ft (lot_facts_pluto.json) and outline area 10,388 sq ft (lot_outline_epsg2263.json) — both far below 65,340 sq ft. As a single zoning lot it is NOT a #large site#. The multi-lot branch needs ownership/contiguity facts not in the folder (the folder shows one BBL) → not met on the recorded facts.
[C] Made-up interior 100 ft × 100 ft lot = 10,000 sq ft (made_up_lots.json) < 65,340 sq ft → NOT a #large site#.

Q7b — qualifying residential site (zr-12-10-qualifying-residential-site), as it bears on an R6B lot. The paragraphs (first words quoted, since the labels may be markup positions):
[C] Item beginning "(a) in an R1 through R5 District, that:" — applies only in R1 through R5 Districts.
[C] Item beginning "(b) in a C1, C2 or C4 District mapped within, or with a #residential equivalent# of, an R1 through R5 District" — applies to C1/C2/C4 districts whose equivalent is R1-R5.
[C] Item beginning "(c) in an M1 District paired with an R1 through R5 District" — M1 context.
[C] None of (a), (b), (c) describes an R6 context. R6B is an R6 (R6-R12) district, and the real lot's C2-2 is "mapped within" R6B (an R6 district), not R1-R5. So BY ITS WORDS the #qualifying residential site# definition does not reach a plain R6B lot or a C2-2-in-R6B lot; such a lot is NOT a qualifying residential site.
[C] Deciding fact: the lot's district / residential equivalent is R6B — recorded in the folder (zonedist1 "R6B", overlay1 "C2-2"; zoning_nyzd_query_R6B.json, zoning_nyco_query_C2-2.json). That fact IS in the folder and settles it: R6B falls outside every paragraph's R1-R5/M1 scope. (The further criteria inside (a)/(b) — lot area ≥ 5,000 sq ft, #Greater Transit Zone#, #wide street#/short-dimension frontage, community-facility floor space, etc. — never need to be reached; and "#Greater Transit Zone#"/"#Outer Transit Zone#" are not defined in the folder, though PLUTO transitzone "Outer Transit Zone" is recorded.)

Q7c — 34-111 (zr-34-111) exceptions (a) and (b): do they reach a C2-2 in R6B?
[C] 34-111 applies to "C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5" and states the general rule "the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that:"
[C] Exception (a): "on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter suffix shall apply" — DOES NOT REACH C2-2/R6B: deciding words "where such districts are mapped within R1 through R5 Districts" (and the lot is not a qualifying residential site, per Q7b).
[C] Exception (b): "on non-#qualifying residential sites#, where such districts are mapped within R1 or R2 Districts, the #bulk# regulations for R3-2 Districts shall apply" — DOES NOT REACH C2-2/R6B: deciding words "where such districts are mapped within R1 or R2 Districts".
[C] So for C2-2 mapped within R6B, neither exception operates; the general 34-111 rule applies and the surrounding R6B bulk governs.

=== Q8. DWELLING UNITS AND QUALIFYING HOUSING ===

Q8a — definitions (verbatim):
[C] Dwelling unit (zr-12-10-dwelling-unit): "A '#dwelling unit#' contains at least one #room# in a #residential building#, #residential# portion of a #building#, or #non-profit hospital staff dwelling#, and is arranged, designed, used or intended for use by one or more persons living together and maintaining a common household, and which #dwelling unit# includes lawful cooking space and lawful sanitary facilities reserved for the occupants thereof. Where a particular regulation ... applies to #dwelling units# in a #building# ... for #residences# other than #single-# or #two-family residences#, such provisions shall also apply to #rooming units#, unless specifically stated."
[C] Qualifying affordable housing (zr-12-10-qualifying-affordable-housing): "shall include any of the following: (a) #MIH developments# in #Mandatory Inclusionary Housing areas#; (b) #UAP developments#; or (c) #buildings# subject to an #affordable housing regulatory agreement#. ...".
[C] Qualifying senior housing (zr-12-10-qualifying-senior-housing): "shall include the following types of facilities: (a) #affordable independent residences for seniors#; or (b) #long-term care facilities#."

Q8b — 23-52 (zr-23-52) max number of dwelling units in R6B:
[C] General rule (R1-R12): "for #buildings# containing #multiple dwelling residences#, the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor."
[C] (i) Standard residences: fall under "(b) For all other types of #multiple dwelling residences#, the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters resulting from this calculation shall be considered to be one #dwelling unit#." → factor 680.
[C] (ii) Qualifying affordable housing: 23-52 sets NO separate factor for it; it is not in the "no factor" list (a) and not otherwise excepted, so it falls under (b) factor 680 (same divisor). (No separate affordable-housing factor is given in this section.)
[C] (iii) Qualifying senior housing: "(a) ... there shall be no applicable #dwelling unit# factor: ... (2) #qualifying senior housing#". → NO dwelling-unit factor (the DU count is not limited by this factor; the section sends the limit elsewhere by removing the factor).

Q8c — made-up interior 100 ft × 100 ft lot (10,000 sq ft), standard residences, R6B, NOT in a special density area:
[C] Step 1 — FAR: 23-22 table, R6B standard residences = 2.00 (zr-23-22).
[?] Step 2 — convert FAR to a floor-area figure in square feet: this needs the definition of "#floor area ratio#" (that an FAR of 2.00 means floor area = 2.00 × lot area). That definition is NOT in the folder (there is a #floor area# definition, zr-12-10-floor-area, but no #floor-area-ratio# capture). So the square-foot maximum is NOT settled by the captured text.
[C] Conditional on the ordinary meaning (floor area = FAR × #lot area#, #lot area# = "the area of a #zoning lot#", zr-12-10-lot-area): max residential floor area = 2.00 × 10,000 = 20,000 sq ft.
[C] Step 3 — factor: 680 (23-52(b); the lot is not in #special density areas# (premise; defined in zr-12-10-special-density-areas as the #Manhattan Core# and #Special Downtown Brooklyn District#), not qualifying senior housing, not a conversion).
[C] Step 4 — divide: 20,000 ÷ 680 = 29.41 (29 whole units, fraction 0.41).
[C] Step 5 — rounding rule (quoted): "Fractions equal to or greater than three-quarters ... shall be considered to be one #dwelling unit#." 0.41 < 0.75, so no extra unit → 29 dwelling units.
[C] ANSWER: 29 dwelling units — CONDITIONAL on (i) the uncaptured #floor area ratio# meaning used in Step 2, and (ii) the building being one "containing #multiple dwelling residences#" (the term #multiple dwelling residence# is not in the folder). If the Step-2 definition is required strictly from the folder, the square-foot floor area and the final count are NOT KNOWN.

PART 7 of 7

=== Q9. ZR 23-44 AND ITS SECTIONS ===

Q9a — section by section:
[C] 23-43 (zr-23-43), "R6 R7 R8 R9 R10 R11 R12": routes height/setback to 23-431 (street wall), 23-432 (height/setback), 23-433 (standard setback); modifications via 23-434 (eligible sites) or 23-435 (towers); "Additional height and setback provisions are set forth in Section 23-436 and Section 23-44, inclusive."
[C] 23-44 (zr-23-44) — heading only in the capture ("Special Provisions for Certain Areas"); header for 23-441/442/443.
[C] 23-441 (zr-23-441) "Special tower provisions": modifies the 23-435 tower rules — "(a) In R9D and R10X Districts ..."; "(b) In R9 or R10 districts without a letter suffix ..." (tower-on-a-base where > 25% of floor area is residential and the lot fronts a wide street within 125 ft/100 ft); "(c) No towers shall be permitted on any #building# located wholly or partly in a #Residence District#, that is within 100 feet of a #public park# with an area of one acre or more ...". Includes the lot-coverage/floor-area-distribution table.
[C] 23-442 (zr-23-442) "Special provisions for certain community districts": "(a) Borough of Manhattan — (1) Community District 9 ... R8 ... north of West 125th Street"; "(2) Community District 6 ... R10 ... east of First Avenue and north of East 51st Street"; "(b) Borough of Brooklyn — (1) ... Community Districts 8 and 9 ... Eastern Parkway"; "(2) ... Community District 9 ... block bounded by Montgomery Street, Washington Avenue, Sullivan Place, and Franklin Avenue". All named geographies with named districts (R8/R10/MIH).
[C] 23-443 (zr-23-443) "Special provisions in other geographies": "(a) ... #zoning lots# adjoining #public parks#" (where 23-381 is used, the park counts as a #wide street#); "(b) ... #transportation-infrastructure-adjacent frontage#" (street-wall/min-base-height relief; +10 ft R1-R6, +20 ft R7-R12 for multiple dwelling residences); "(c) #Limited Height Districts#" (underlying rules apply, no 23-434 eligible-site height, and an LH height cap table LH-1 50 ft / LH-1A 60 ft / LH-2 70 ft / LH-3 100 ft); "(d) ... along certain district boundaries" — where an R6-R12 lot line coincides with an R1-R5 district boundary, a transition-area height cap table applies (keyed to adjacency, qualifying vs non-qualifying site, and lot width; e.g. R1/R2/R3 non-qualifying 45 ft, with "*" = 65 ft max within the transition area for R7-R10).

Q9b — can any reach a NEW building on an R6B lot? Deciding fact and folder status:
[C] 23-441 — DOES NOT APPLY to R6B: deciding words name "R9D and R10X" (a) and "R9 or R10 districts without a letter suffix" (b). R6B is not among them. (Towers under 23-435 are not available in R6B on this text.) (c)'s park prohibition only bites if a tower is permitted at all. → does not apply. [The adjoining-park fact is not in the folder, but it is moot since no tower provision reaches R6B.]
[C] 23-442 — DOES NOT APPLY: every branch names Manhattan CD9/CD6 or Brooklyn CD8/9 — out-of-borough, named districts (R8/R10). The real lot is Queens CD 11 in R6B.
[C] 23-443(a) — public park adjacency using 23-381: [?] NOT KNOWN — whether the lot adjoins a #public park# and uses 23-381 is not stated in the folder (no park fact; 23-381 not captured).
[C] 23-443(b) — transportation-infrastructure-adjacent frontage: [?] NOT KNOWN — the term is undefined in the folder and no fact says the lot has such frontage (same gap as 35-643(a)).
[C] 23-443(c) — Limited Height Districts: DOES NOT APPLY unless the lot is in an LH district. [F] lot_facts_pluto lists "ltdheight" among "fields_absent_from_the_served_row", i.e. no limited-height district is recorded for the lot → on the recorded facts it is not in an LH district.
[C] 23-443(d) — district-boundary transition: applies where "a #lot line# of a #zoning lot# located in an R6 through R12 District coincides with the district boundary of an R1 through R5 District." R6B is an R6-R12 district, so this COULD reach the lot. [?] NOT KNOWN whether any lot line of the real lot coincides with an R1-R5 district boundary: the folder's zoning query (zoning_nyzd_query_R6B.json) returns only R6B polygon attributes (areas/lengths, no geometry) and gives no adjacent-district boundary; splitzone is false but adjacency to an R1-R5 district next door is not shown. → the deciding fact (an adjacent R1-R5 boundary coinciding with a lot line) is missing.

=== Q10. WHAT IS MISSING ===
Pointed-to but NOT in the folder (pointer words ≤25, and which answer stays open):
[?] "#floor area ratio#" definition — 23-52 divides "maximum #residential# #floor area#" and 23-22 gives the ratio; converting ratio→sq ft needs this. Keeps Q8c square-foot floor area and 29-DU count CONDITIONAL.
[?] R6/R6B front-yard and side-yard REQUIREMENT sections (e.g. a 23-32/23-33) — captured R6-R12 yard rules cover only rear yards. Keeps Q2b "does the overlay CHANGE the front/side yard" NOT KNOWN.
[?] "#multiple dwelling residence#" definition — 23-52 "for #buildings# containing #multiple dwelling residences#". Makes Q8 depend on an unverified classification.
[?] "#transportation-infrastructure-adjacent frontage#" definition — 35-643(a)/23-443(b). Keeps Q4 35-643 and Q9 23-443(b) NOT KNOWN.
[?] "#Greater Transit Zone#"/"#Outer Transit Zone#" definitions — qualifying-residential-site (a)(1)(ii)/(2). Not needed for the conclusion (R6B fails the district test first) but noted.
[?] "#height factor#" and "#open space#" definitions — used in the lot-coverage definition exclusions (Q5a). The exclusions cannot be fully worked without them.
[?] Section 23-381 — 23-443(a) "where a #building# ... utilizes the provisions of Section 23-381". Keeps Q9 23-443(a) NOT KNOWN.
[?] Section 23-62 — 23-341(b)(1)/23-312(a) balconies "subject to ... Section 23-62". Leaves balcony limits incompletely stated in Q5c.
[?] Chapter 5 scope/applicability section (e.g. 35-00/35-20/35-21) — needed to say whether 35-22 governs an all-residential building vs 34-111. Keeps Q4 35-22 governing-section NOT KNOWN (substance unaffected).
[?] Adjacent-district boundaries / neighbouring-building data / metes-and-bounds lot-line labels for the real lot — needed for Q6b (prevailing street wall frontage), Q9 23-443(d), and the beyond-100-ft rear-yard treatment in Q2b/Q3. Not in the folder.

Texts that ARE in the folder but I chose NOT to read (separate list): zr-11-23; zr-11-25; zr-12-10-base-plane; zr-12-10-manhattan-core; zr-12-10-qualifying-exterior-wall-thickness; zr-12-10-special-downtown-brooklyn-district; zr-23-21; zr-23-23; zr-23-231; zr-23-232; zr-23-233; zr-23-234; zr-23-363; zr-23-41; zr-23-411; zr-23-412; zr-23-413; zr-23-42; zr-23-421 (+ -421-g, -421-r1-r2, -421-r3-r4); zr-23-422 (+ -422-r3-r4); zr-23-423; zr-23-424 (+ -424-r1-r2); zr-23-433; zr-23-434; zr-23-435; zr-23-436; zr-34-112; zr-34-113; zr-35-632; zr-35-633; zr-35-71; zr-36-64; zr-54-40; zr-54-41. (I read zr-23-44 and the 23-34 group headings but not the 23-34 parent body beyond its title.)

=== Q11. ONE-LINE SUMMARY PER QUESTION ===
Q1: The C2-2 Chapter-4 floor-area sections leave R6B's max residential FAR (2.00) and buildable floor area unchanged — 34-221 pegs FAR to Article II Ch 3, and the only bonuses (34-223/224) do not list C2; 34-222 is change-of-use only.
Q2: 34-23's sections remove any required front yard (34-231) and side yard (34-232) and do not touch the rear yard; whether they "change" R6B's front/side yard is NOT KNOWN (no R6B front/side-yard requirement in folder); the rear yard stays on R6B rules, waived within 100 ft of the ~90° corner (23-344(a)).
Q3: FAR, lot coverage and rear yard are each the SAME as plain R6B (FAR 2.00 via 34-221; lot coverage via 23-362 corner 100%/interior 80%; rear yard via 23-342/344); NO captured overlay text speaks of "lot coverage".
Q4: Only 35-63 (height/setback, via 34-24(b)(1)) applies to the all-residential building, and 35-22 reaches its bulk in substance (governing-chapter NOT KNOWN); 35-62/35-641/35-642 do not apply and 35-643(a) is NOT KNOWN; a #mixed building# (partly commercial/CF) is not an all-residential building.
Q5: Lot coverage = above-view building footprint (with #height-factor#/23-341-obstruction exclusions); yard/rear-yard/RYE/front-yard/side-yard quoted; and the rear-yard obstruction list = 23-311 + 23-312 + 23-341 as listed (R6B bars 23-341(b)(3)).
Q6: Definitions quoted; whether the real lot has a #prevailing street wall frontage# is NOT KNOWN because all neighbouring-building street-wall facts are absent from the folder (only the subject lot's frontages and the street lines are derivable).
Q7: The real lot (~10,075/10,388 sq ft) and the 100x100 lot (10,000 sq ft) are NOT #large sites# (< 65,340 sq ft); a C2-2-in-R6B / R6B lot is NOT a #qualifying residential site# (definition reaches only R1-R5/M1 contexts); 34-111 exceptions (a)/(b) do not reach C2-2/R6B (they require mapping within R1-R5 / R1-R2).
Q8: Definitions quoted; R6B factors = 680 standard (23-52(b)), 680 for qualifying affordable (no separate factor given), NO factor for qualifying senior (23-52(a)(2)); the 100x100 R6B standard-residence count = 29 dwelling units, CONDITIONAL on the uncaptured #floor area ratio# meaning (20,000 ÷ 680 = 29.41, fraction < 0.75).
Q9: None of 23-441 (R9D/R10X, R9/R10-no-suffix) or 23-442 (Manhattan CD9/CD6, Brooklyn CD8/9) reaches a Queens R6B lot; 23-443(c) LH district does not apply (no ltdheight recorded); 23-443(a)/(b)/(d) are NOT KNOWN for want of park / transportation-frontage / adjacent-R1-R5-boundary facts.

END-OF-REPORT
