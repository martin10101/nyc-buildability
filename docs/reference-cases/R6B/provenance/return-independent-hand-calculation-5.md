# Independent reading of the commercial-overlay sealed folder (step P2), reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-07, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the pinned step-P2 law-text captures (the C2-2 commercial-overlay sections and the residential bulk sections they route to, without their notes), the benchmark lot's recorded official facts and outline, with no floor-area-ratio field and no program output - and had no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1; a value is recorded in the commercial-overlay reference-case row only where this reading and reading 2 (return-independent-hand-calculation-6.md) give the same value on the same basis.

---

PART 1 of 6

DRAFT READING — NOT legal advice and NOT a professional review. This is an AI independent reader's by-hand reading of captured NYC Zoning Resolution (ZR) text for one real lot — 215-16 Northern Boulevard, Queens, BBL 4073340070 — and the C2-2-overlay question. In production any rule citing these captures ships under a standing "not professionally reviewed" label with a direct source link (ADR-007). Nothing here is a zoning determination. Every capture is an extracted_draft (raw_html_verified=false), Last Amended 12/5/2024 for the Article II/III sections.

ONE HARD RULE — OBEYED. I read only files under .../scratchpad/sealed-p2 and wrote only under .../scratchpad/reader3 (one geometry script, geom.py). I opened NO official web page — the sealed folder held every text these questions needed; where it did not, I mark NOT KNOWN rather than guess or fetch. I opened nothing under /root/project.

FILES READ (all under sealed-p2): INDEX.json; facts/ lot_facts_pluto.json, lot_outline_epsg2263.json, streets_dcm_centerlines.json, zoning_nyco_query_C2-2.json, zoning_nyzd_query_R6B.json; law/ zr-34-11, zr-34-111, zr-11-25, zr-34-24, zr-35-53, zr-35-63, zr-35-631, zr-35-632, zr-35-633, zr-23-22, zr-23-362, zr-23-363, zr-23-52, zr-23-431, zr-23-432, zr-23-433, zr-23-342, zr-23-344, zr-12-10, zr-12-10-lot-corner, zr-12-10-lot-interior, zr-12-10-lot-through, zr-12-10-lot-area, zr-12-10-floor-area, zr-12-10-special-density-areas. My script: reader3/geom.py.

FACTS I RELY ON
[F] District/overlay: zonedist1=R6B, overlay1=C2-2, splitzone=false (lot_facts_pluto.json); corroborated by zoning_nyzd_query_R6B.json and zoning_nyco_query_C2-2.json.
[F] Borough QN / borocode 4, Block 7334, Lot 70 (lot_facts_pluto.json, lot_outline_epsg2263.json).
[F] Lot area — TWO recorded figures that DIFFER: PLUTO lotarea="10075" sq ft vs MapPLUTO Shape__Area=10387.988 sq ft.
[C] My shoelace of the recorded outline ring = 10387.988 sq ft — matches Shape__Area, not PLUTO 10075; difference ~313 sq ft (~3%). I treat lot area as UNRESOLVED and show any derived number both ways.
[F] PLUTO lotfront=100.76 ft, lotdepth=100.0 ft, lottype="3" (meaning NOT given in the facts — I do NOT use it).
[F] Adjoining street centerlines + mapped Streetwidth (free-text feet, streets_dcm_centerlines.json): Northern Boulevard "100"; 215 Place "60". (215 Street "60" and 45 Road "50" are present but, by the geometry below, do not adjoin this lot.)

LOT CLASSIFICATION (from recorded coordinates + quoted definitions; reader3/geom.py)
[C] The outline is a ~100 ft x ~104 ft parallelogram. North edge lies ~1.1 ft off the Northern Boulevard street line (centerline distance 51.06 ft minus the 50 ft half of the mapped 100 ft) -> the lot FRONTS Northern Boulevard there (edge ~103.9 ft). East edge lies essentially on the 215 Place street line (centerline distance 28.9 ft vs 30 ft half-width) -> the lot FRONTS 215 Place there (edge ~100.0 ft). The other two edges are 50-100 ft from any street line -> interior (side/rear) lot lines.
[C] The Northern Boulevard centerline and the 215 Place centerline share one exact vertex (1048907.267, 216487.365) — they intersect; the lot's NE corner adjoins that intersection; the lot's interior angle there is ~89.7 degrees.
[C] ZR 12-10 "corner lot" (zr-12-10-lot-corner): "a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle ... forms an angle of 135 degrees or less." 89.7 <= 135 -> CORNER LOT (Northern Boulevard x 215 Place). Not a through lot (frontages are perpendicular, not opposite/parallel — zr-12-10-lot-through).
[C] Street-width class (zr-12-10): "A 'wide street' is any street 75 feet or more in width.... A 'narrow street' is any street less than 75 feet wide." Northern Boulevard mapped 100 >= 75 -> WIDE; 215 Place mapped 60 < 75 -> NARROW. Basis = City-Map mapped width (the only width in the facts).
[?] Whether the zoning lot equals this single tax lot (no merger) is assumed from the one recorded BBL with splitzone=false, not independently shown.

PART 2 of 6 — Q1 WHICH BULK REGULATIONS APPLY

Q1a. Governing bulk; the 34-111 exceptions.
[C] zr-34-11 (C1 C2 C3 C4 C5 C6): "the #bulk# regulations of Article II, Chapter 3, shall apply to all #residential buildings# in accordance with the provisions of this Section, except as modified by the provisions of Sections 34-21 through 34-24, relating to exceptions to applicability of #Residence District# controls."
[C] zr-34-111 (list includes C2-2): "the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply, except that: (a) on #qualifying residential sites# within the #Greater Transit Zone#, where such districts are mapped within R1 through R5 Districts, the #bulk# regulations for R5 Districts without a letter suffix shall apply; and (b) on non-#qualifying residential sites#, where such districts are mapped within R1 or R2 Districts, the #bulk# regulations for R3-2 Districts shall apply." Plus: "Such district modifications shall apply for the purposes of applying the provisions of Article II, Chapter 3, and the remaining provisions of this Chapter, unless otherwise specified."
[C] Governing bulk = that of the surrounding Residence District = R6B.
The two listed exceptions are (a) and (b):
[C] (a) applies only "within R1 through R5 Districts." Fact: R6B [F] -> (a) does NOT apply.
[C] (b) applies only "within R1 or R2 Districts." Fact: R6B [F] -> (b) does NOT apply.
-> Neither applies; R6B bulk governs. OVERLAY EFFECT on which district's bulk applies: none (it confirms R6B). (The "Greater Transit Zone" / transitzone fact is moot because (a) is R1-R5 only.)

Q1b. What 34-11 and 34-111 route to; which are in the folder.
[C] 34-11 -> "Article II, Chapter 3" residence bulk, "as modified by ... Sections 34-21 through 34-24."
  In folder (Art II Ch 3, relevant): zr-23-22 (FAR), zr-23-362/363 (lot coverage), zr-23-52 (dwelling units), zr-23-342/344 (rear yard), zr-23-431/432/433 (street wall/height/setback). Of 34-21..34-24, ONLY zr-34-24 is in the folder.
[?] 34-21, 34-22, 34-23 are NOT in the folder — their content ("exceptions to applicability of Residence District controls") is NOT KNOWN; I cannot exclude that they touch FAR, coverage, or yards.
[C] 34-111 -> the R6B bulk of "Article II, Chapter 3, and the remaining provisions of this Chapter" (Article III, Chapter 4). Of Article III Ch 4, only 34-24 (plus the 34-11/34-111 I hold) is in the folder; other 34-1xx/34-2x sections are not.

PART 3 of 6 — Q2 FLOOR AREA, LOT COVERAGE, DWELLING UNITS

Q2a. Does any captured OVERLAY text state or change a FAR / lot coverage / DU rule?
[C] Reading each overlay text named in the prompt:
- zr-34-11: applies Art II Ch 3 bulk; no FAR/coverage/DU number.
- zr-34-111: applies the Residence District's bulk; exceptions (a)/(b) are R1-R5 / R1-R2 only and merely swap the governing district — no R6 FAR/coverage/DU number, no change for R6B.
- zr-34-24: "the height and setback regulations ... are modified as set forth in this Section" — height/setback ONLY.
- zr-35-53: a rear-yard modification for "a #residential# portion of a #mixed building#" — no FAR/coverage/DU.
- zr-35-63, zr-35-631, zr-35-632, zr-35-633: street-wall location and height/setback ONLY.
-> [C] NONE of the captured overlay texts states a FAR, a lot coverage, or a dwelling-unit rule, or changes the one the Residence District gives.
[?] Caveat: 34-11 points to 34-21..34-23 (not captured); whether those modify FAR/coverage/yards is NOT KNOWN.

Q2b. Is the maximum residential FAR the R6B one of zr-23-22?
[C] Route: C2-2 in R6B -> 34-11 (apply Art II Ch 3 bulk) -> 34-111 (bulk of the surrounding R6B; neither exception applies) -> zr-23-22: "the maximum #residential# #floor area ratio# shall be as set forth in the following table." R6B row = 2.00 (standard residences), 2.40 (qualifying affordable/senior housing). The subject is a new all-residential building with NO recorded affordable/senior-housing status [F none] -> the STANDARD 2.00 row is the one indicated; 2.40 would need a qualifying-housing fact not in the record.
[C] R6B carries NO footnote in zr-23-22, so the "within 100 feet of a #wide street#" footnote creates no different R6B FAR — being on Northern Boulevard (wide) does not raise it.
-> YES: maximum residential FAR = R6B 2.00 (standard) via the quoted route. OVERLAY EFFECT: none (same 2.00).
[C] If a floor area is wanted (shown BOTH ways because the two recorded lot areas DIFFER): 2.00 x 10075 = 20,150 sq ft; 2.00 x 10387.988 = 20,775.98 sq ft. I do not choose between them (lot area unresolved: PLUTO 10075 vs MapPLUTO 10387.988).
[?] Same 34-21..34-23 gap as Q2a.

Lot coverage (zr-23-362 / zr-23-363):
[C] zr-23-362(a) (R6-R12; R6B via zr-11-25): "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." Corner lot -> 100% for the corner-lot portion.
[C] zr-23-363(b): interior/through portions "within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less ... shall be 100 percent." The corner is ~90 (<=135) and the lot is ~100 ft each way, so effectively 100% across it; any portion >100 ft from the intersecting street lines reverts to 80% unless 23-363 raises it.
-> [C] Max residential lot coverage = 100% (corner lot). OVERLAY EFFECT: none.

Dwelling units (zr-23-52):
[C] zr-23-52 (R1-R12): "the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor"; (b) "For all other ... #multiple dwelling residences#, the applicable #dwelling unit# factor shall be 680. Fractions equal to or greater than three-quarters ... shall be considered to be one #dwelling unit#." The (a) no-factor cases: developments/enlargements in #special density areas#, #qualifying senior housing#, or certain #conversions#.
[C] zr-12-10-special-density-areas: "#Special density areas# shall include: (a) the #Manhattan Core#; and (b) the #Special Downtown Brooklyn District#." The lot is in Queens [F] -> not a special density area; it is a NEW building (not a conversion); no senior-housing fact recorded -> the (a) no-factor cases do not apply -> factor 680 applies.
-> [C] Max DU = (max residential floor area) / 680, a fraction >= 0.75 counting as one. Both ways: 20,150 / 680 = 29.6 -> 29 DU; 20,775.98 / 680 = 30.6 -> 30 DU (DIFFERS with the unresolved lot area). OVERLAY EFFECT: none.
[?] "#multiple dwelling residences#" is not defined in the folder; the DU rule presupposes a multiple dwelling (3+ units), which I assume for the subject building.

PART 4 of 6 — Q3 HEIGHT AND SETBACK

Q3a. Route from 34-24 for C2-2 within R6B.
[C] zr-34-24 (C1-C6): "the height and setback regulations set forth in Article II, Chapter 3 ... are modified as set forth in this Section." Then "(b) In Commercial Districts with R6 through R12 equivalency ... In #Commercial Districts# mapped within, or with a #residential equivalent# of R6 through R12 Districts: (1) the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied; (2) the special height and setback provisions for certain areas set forth in Section 36-64 shall be applied; and (3) where the optional #bulk# regulations for #sky exposure plane buildings# are utilized, the provisions set forth in Section 35-71, inclusive, shall be applied." R6B is within "R6 through R12" (zr-11-25) -> paragraph (b) applies; (a) [R1-R5] does not.
[C] zr-35-63: "the #street wall# location of a #building# shall be as set forth in Section 35-631, and the height and setback provisions shall be as set forth in Section 35-632. Additional height and setback provisions are set forth in Section 35-633 and Section 35-64, inclusive." -> street wall -> 35-631; height/setback -> 35-632; additional -> 35-633 (and 35-64, not in folder).
[?] 34-24(b)(2)->36-64 and (b)(3)->35-71 are NOT in the folder (36-64 = special height/setback for certain areas; 35-71 = optional sky-exposure-plane envelope). Whether 36-64 adds anything here is NOT KNOWN; 35-71 matters only if that optional envelope is chosen.

Q3b. Base heights / building height under 35-632; does (b) or (c) apply?
[C] zr-35-632(a): "The minimum base height, maximum base height and maximum #building# height shall be as set forth in the table in Section 23-432 for the applicable #Residence District#." District = R6B.
[C] zr-23-432 R6B row (quoted values): minimum base height 30 ft; standard residences max base height 45 ft, max building height 55 ft; qualifying affordable/senior housing max base 45 ft, max building 65 ft. R6B has NO footnote (no wide-street split).
-> For a standard all-residential building: MIN BASE 30 ft, MAX BASE 45 ft, MAX BUILDING 55 ft. (Qualifying-housing 45/65 only with a qualifying-housing fact, which is not recorded.)
[C] Case (ii) plain R6B: height/setback come from 23-43 -> the SAME zr-23-432 R6B row -> SAME 30/45/55. OVERLAY EFFECT: none on base or building heights.
[C] (b) vs (c): zr-35-632(b) applies only "within, or with a #residential equivalent# of R6 through R12 without a letter suffix" — R6B HAS the letter suffix "B" -> (b) does NOT apply (so 23-434's criteria need not be reached). zr-35-632(c) (towers) applies only "R9 through R12" -> does NOT apply to R6B. -> Neither (b) nor (c) applies; paragraph (a) governs. This is SETTLED by the text (not NOT KNOWN).

Q3c. Setback above the base, each street.
[C] zr-35-632(a): "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided ... in accordance with Section 23-433."
[C] zr-23-433: "At a height not lower than the minimum base height or higher than the maximum base height specified for the applicable district, a setback with a depth of at least 10 feet shall be provided from any #street wall# fronting on a #wide street#, and a setback with a depth of at least 15 feet shall be provided from any #street wall# fronting on a #narrow street#." Modifications (a)-(d) may reduce/adjust it (e.g., (a) reduce 1 ft per 1 ft the wall is beyond the street line, floor 7 ft; (c) optional where a wall is beyond 50 ft of a street line or at a shallow angle; (d) dormers).
-> [C] Northern Boulevard (WIDE) frontage: setback at least 10 ft above the base height. 215 Place (NARROW) frontage: setback at least 15 ft above the base height. Each occurs at a height between min base 30 ft and max base 45 ft.
[C] OVERLAY EFFECT: none on setback DEPTHS — 35-632(a) routes to the same 23-433 that plain R6B reaches via 23-43. Same 10 ft / 15 ft.

Q3d. 35-633.
[C] zr-35-633: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows: (a) for the purposes of applying such provisions, references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631; and (b) for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage."
[C] So 35-633 (i) imports "additional height and setback regulations" from Section 23-436, (ii) for THOSE swaps 23-431 street-wall references to 35-631, and (iii) adds a corner-lot street-wall rule.
[?] Section 23-436 is NOT in the folder -> what those "additional height and setback" provisions are, and whether they bind this building, is NOT KNOWN. The 35-633(b) corner-lot rule turns on whether a Commercial District is mapped "along the entire #block# frontage," a fact not in the record -> NOT KNOWN. Applies to buildings in this C2-2/R6-R12 family, but the substance depends on the missing 23-436.

PART 5 of 6 — Q4 STREET WALL LOCATION; Q5 REAR YARD

Q4a. Which paragraph of 35-631 applies to C2-2 within R6B, outside the Manhattan Core.
[C] zr-35-631(a) ("Line-up rules") applies "For #Commercial Districts# mapped within, or with a #residential equivalent# of, R8 through R12 Districts, when located within the #Manhattan Core#." District is R6B (an R6, not R8-R12) -> (a) cannot apply, regardless of the Manhattan Core.
[C] zr-35-631(b) ("Percentage-based rules"): "For all #buildings# that are not subject to the provisions of paragraph (a) of this Section the following shall apply: At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less. Up to 30 percent ... may be recessed beyond eight feet of the #street line#, provided that any such recesses deeper than 10 feet along a #wide street# or 15 feet along a #narrow street# are located within an #outer court#."
[C] zr-35-631(c) (large lots) applies only to lots >= 40,000 sq ft or a full block; this lot is ~10,075-10,388 sq ft -> (c) does not apply. (d) articulation allowances apply in all districts.
-> [C] Paragraph (b) governs: >=70% of the aggregate street-wall width within 8 ft of each street line, rising to at least the 30 ft minimum base height (R6B) or the building height, whichever is less.

Q4b. Inside or outside the Manhattan Core from the facts?
[F] The lot is in Queens (borough QN, borocode 4). [?] The DEFINITION/extent of the "#Manhattan Core#" is not in the folder; zr-12-10-special-density-areas names the Manhattan Core as a Manhattan geography, so a Queens lot is outside it, but I cannot verify the Core's boundary from captured text. It does not matter here: 35-631(a) is also limited to R8-R12, so (a) is excluded for R6B on that ground alone, and (b) governs either way.

Q4c. Plain R6B (case ii) street-wall rule (zr-23-431); is the overlay different?
[C] zr-23-431 (R6-R12) paragraph (a) names R6B: "In R6B, R7B, and R8B Districts, the #street wall# of a #building# shall be located no closer to the #street line# than the closest #street wall#, or portion thereof, nor further from the #street line# than the furthest #street wall#, or portion thereof, of an existing adjacent #building# on the same or an adjoining #zoning lot# located on the same #street# frontage. Eligible adjacent #buildings# shall be located within 15 feet of the #street line#, within 25 feet of the subject #building#, and have a height that exceeds 35 feet...." Fallback: "where ... the #street wall# surrounding the subject #building# do not have a #prevailing street wall frontage#, the applicable #street wall# regulations of paragraph (b) may be applied." (23-431(b) splits 8 ft wide / 10 ft narrow.)
-> [C] Plain R6B uses a LINE-UP rule keyed to existing adjacent buildings (23-431(a)).
[C] The overlay does NOT use 23-431: 35-63 sends street-wall to 35-631, and 35-633(a) expressly supersedes 23-431 references with 35-631. 35-631 has NO R6B line-up rule; for this lot it gives percentage rule (b) — 70% within a flat 8 ft of the street line.
-> [C] YES, the overlay CHANGES the street-wall location rule (23-431(a) line-up -> 35-631(b) percentage, flat 8 ft).
[?] Whether a "#prevailing street wall frontage#" exists (which could switch the applicable paragraph in either regime) is undefined in the folder and unestablished by the facts.

Q5a. To which buildings does 35-53 apply; does it reach an all-residential building?
[C] zr-35-53: "for a #residential# portion of a #mixed building#, the required #residential# #rear yard# shall be provided at the floor level of the lowest #story# used for #dwelling units# or #rooming units#, where any window of such #dwelling units# or #rooming units# faces onto such #rear yard#...." The operative subject is "a #residential# portion of a #mixed building#."
-> [C] On its words, 35-53 addresses the residential portion of a MIXED building (one that also has a non-residential portion). The subject is an ALL-RESIDENTIAL building, so 35-53 does not set its rear yard; the rear-yard requirement comes from Article II Ch 3 (23-342 / 23-344).
[?] "#mixed building#" is not defined in the folder; I rely on the provision's own words. Whether an all-residential building could ever be a "mixed building" is NOT KNOWN from captured text, but nothing in 35-53 purports to govern an all-residential building.

Q5b. Does any captured overlay text change the plain-R6B rear-yard reading (no rear yard within 100 ft of the corner; beyond that not known)?
[C] zr-23-344(a) (R1-R12): "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." The lot is a corner lot (Northern Blvd x 215 Place, ~90 <= 135) -> no rear yard within 100 ft of that intersection.
[C] Beyond 100 ft, zr-23-344(c)/(d) make the result depend on whether the far lot line "coincides with" an adjoining zoning lot's REAR lot line (rear yard required per 23-342) or SIDE lot line (in R6-R12, "no #rear yard# shall be required") — a neighbor-lot fact not in the record -> NOT KNOWN. (zr-23-342 base rear yards, e.g. 20/30 ft, apply to interior-lot portions.)
[C] The only captured OVERLAY rear-yard text is 35-53, which (Q5a) reaches only mixed buildings.
-> [C] The overlay does NOT change the rear-yard reading for an all-residential building; it stays the Article II reading (no rear yard within 100 ft of the corner; beyond 100 ft NOT KNOWN).
[?] Same bounded 34-21..34-23 gap (not in folder) as Q2.

PART 6 of 6 — Q6 WHAT IS MISSING; Q7 SUMMARY

Q6. Sections/terms the captured OVERLAY texts point to that the folder does NOT hold (pointing words <=25 each), and which answers stay NOT KNOWN/conditional:
1. [?] Sections 34-21, 34-22, 34-23 — zr-34-11: "except as modified by ... Sections 34-21 through 34-24, relating to exceptions to applicability of Residence District controls." -> keeps Q2a/Q2b (FAR), lot coverage, and Q5b (rear yard) bounded-conditional (cannot exclude an overlay-chapter modification).
2. [?] Section 36-64 — zr-34-24(b)(2): "the special height and setback provisions for certain areas set forth in Section 36-64 shall be applied." -> keeps Q3a/Q3b/Q3c height-setback conditional (unknown extra-area rules).
3. [?] Sections 35-71 and 35-64 — zr-34-24(b)(3)/zr-35-63: optional sky-exposure-plane option / "Additional height and setback provisions ... Section 35-64, inclusive." -> Q3 conditional only if the optional envelope is used.
4. [?] Section 23-436 — zr-35-633: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows." -> Q3d NOT KNOWN (substance of the additional provisions).
5. [?] Section 23-434 — zr-35-632(b): "for #zoning lots# meeting the criteria of paragraph (a) of Section 23-434, the maximum #building# heights may be increased." -> does not change R6B (para (b) excluded by the letter suffix), but the cross-reference itself is absent.
6. [?] Section 23-435 — zr-35-632(c): towers "permitted pursuant to the provisions of Section 23-435." -> not applicable (R9-R12 only); absent.
7. [?] Defined term "#Manhattan Core#" — zr-35-631(a): "when located within the #Manhattan Core#." -> Q4b not fully verifiable from text (does not change the Q4a outcome).
8. [?] Defined term "#prevailing street wall frontage#" — zr-35-631(a)/(b) and zr-23-431: "a #block# with a #prevailing street wall frontage#." -> leaves open which street-wall paragraph could apply in each regime (Q4a/Q4c).
9. [?] Defined term "#mixed building#" — zr-35-53: "a #residential# portion of a #mixed building#." -> underpins Q5a (reliance on the provision's own words).
10. [?] Section 23-41 (Permitted Obstructions) — zr-35-53: "pursuant to Section 23-41 (Permitted Obstructions), inclusive." -> affects only obstruction detail of a mixed-building rear yard, not this all-residential building.
(Behind Art II Ch 3, not in the overlay-text set but noted: 23-34 / 23-343 rear-yard cross-refs sit behind 23-342/23-344 and are part of the "beyond 100 ft NOT KNOWN.")

Q7. ONE-LINE SUMMARY for the lot as recorded (C2-2 within R6B):
- Floor area ratio: SAME as plain R6B (route 34-11 -> 34-111 -> 23-22 R6B = 2.00 standard); overlay adds no FAR.
- Lot coverage: SAME as plain R6B (100% corner lot, 23-362(a); 23-363(b) within 100 ft of corner); overlay adds none.
- Dwelling units: SAME as plain R6B (max residential floor area / 680, 23-52(b)); overlay adds none. [conditional on the unresolved lot area: ~29 vs ~30 units]
- Base heights and building height: SAME as plain R6B (35-632(a) -> 23-432 R6B row = the plain-R6B row): min base 30 ft, max base 45 ft, max building 55 ft (standard).
- Setback: SAME as plain R6B (35-632(a) -> 23-433 = plain-R6B 23-43 -> 23-433): 10 ft above the base on the wide street (Northern Blvd), 15 ft on the narrow street (215 Place).
- Street wall location: CHANGED BY THE OVERLAY — from the R6B line-up rule of 23-431(a) to the percentage rule of 35-631(b) (>=70% within 8 ft of the street line) (35-63; 35-633(a) supersedes 23-431).
- Rear yard: SAME as plain R6B for an all-residential building — no rear yard within 100 ft of the Northern Blvd x 215 Place corner (23-344(a)); beyond 100 ft NOT KNOWN (23-344(c), neighbor-lot fact missing). The overlay's rear-yard text (35-53) reaches only mixed buildings.

Overall: on these recorded facts the C2-2 overlay changes ONLY the street-wall location rule; FAR, lot coverage, dwelling units, base/building heights, setback depths, and the all-residential rear-yard reading are the same as plain R6B. Everything above is a draft reading of captured, not-yet-second-verified law text; items marked [?] are genuinely NOT KNOWN from the sealed folder.

END-OF-REPORT
