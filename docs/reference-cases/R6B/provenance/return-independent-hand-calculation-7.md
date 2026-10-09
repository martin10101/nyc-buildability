# Independent reading from the step-P3 sealed folder, reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-07, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the pinned law-text captures (without their notes), the benchmark lot's recorded official facts and outline, and three made-up lots - with no access to the program or this repository. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1 of the step-P3 pair; a value is recorded in a step-P3 reference-case row only where this reading and reading 2 (return-independent-hand-calculation-8.md) give the same answer on the same basis.

---

PART 1 of 7

THIS IS A DRAFT READING OF LAW TEXT BY AN AI. It is not legal advice and not a professional review. Every conclusion is a reading of captured source text; where the text does not settle a point I say NOT KNOWN.

ONE HARD RULE — OBEYED. I worked only from the sealed folder `.../scratchpad/sealed-p3` and my scratch folder `.../scratchpad/reader-p3-1`. I did not open, list or search anything under `/root/project`. I opened NO official web page: every text I quote is in the sealed folder, so the official site was not needed. I wrote only in my scratch folder (two arithmetic/geometry scripts: `geom.py`, `geom2.py`, plus a law-text extractor `dump_law.py`). I wrote no agent memory and invoked no repository skill.

FILES I READ
- facts: `lot_facts_pluto.json`, `lot_outline_epsg2263.json`, `made_up_lots.json`, `streets_dcm_centerlines.json`, `zoning_nyco_query_C2-2.json`, `zoning_nyzd_query_R6B.json`; and `INDEX.json`.
- law (verbatim_excerpt, and table for 23-432/34-112): `zr-12-10-lot-line-front`, `-lot-line-rear`, `-lot-line-side`, `-lot-width`, `-lot-depth`, `-street-line`, `-zoning-lot`, `-lot-corner`, `-lot-interior`, `-lot-through`, `zr-12-10` (wide/narrow), `zr-23-342`, `zr-23-343`, `zr-23-344`, `zr-23-41`, `zr-23-411`, `zr-12-10-lot-area`, `zr-23-436`, `zr-23-43`, `zr-35-63`, `zr-35-633`, `zr-35-631`, `zr-11-25`, `zr-34-11`, `zr-34-21`, `zr-34-24`, `zr-34-111`, `zr-34-112`, `zr-34-113`, `zr-12-10-special-density-areas`, `-manhattan-core`, `-special-downtown-brooklyn-district`, `zr-12-10-base-plane`, `zr-23-432`, `zr-23-434`, `zr-23-435`, `zr-23-362`, `zr-23-363`, `zr-12-10-residence-or-residential`, `zr-12-10-floor-area`, `zr-23-23`, `zr-23-231`, `zr-23-232`, `zr-23-233`, `zr-23-234`.

KEY FACTS USED (all [F] from the facts files)
- Real lot BBL 4073340070, 215-16 Northern Boulevard, borough QN (borocode 4), block 7334 lot 70, community district "411", zonedist1 R6B, overlay1 C2-2, splitzone false, lotarea 10075 sq ft, lotfront 100.76 ft, lotdepth 100.00 ft, lottype "3" (meaning not given). spdist1/2/3, zonedist2-4, overlay2, ltdheight ABSENT from the served row. (`lot_facts_pluto.json`)
- Outline (EPSG:2263 US survey feet, `lot_outline_epsg2263.json`): ring P0(1048810.23,216310.44) P1(1048788.63,216408.05) P2(1048889.92,216431.10) P3(1048911.58,216333.50) P4(1048812.40,216310.93) back to P0. P4 is 2.2 ft from P0 — I treat the lot as the quadrilateral P0-P1-P2-P3 and note P4 as a ~2 ft digitizing nub. Shape__Area 10387.99 sq ft.
- Streets (`streets_dcm_centerlines.json`): Northern Boulevard mapped Streetwidth "100"; 215 Place mapped Streetwidth "60". (Also 215 Street "60", 45 Road "50" nearby, not fronting the lot.)
- My measured edge lengths (ft): P0-P1 99.98, P1-P2 103.88, P2-P3 99.98, P3-P0 103.93. [C] The lot is a parallelogram.
- Which edge fronts which street, from perpendicular distances of edge midpoints to each centerline [C]: edge P1-P2 is ~51 ft from the Northern Boulevard centerline (half of the 100-ft mapped width = 50 ft, so essentially on the Northern street line) → fronts Northern Boulevard; edge P2-P3 is ~29 ft from the 215 Place centerline (half of 60 = 30 ft) → fronts 215 Place. Edges P0-P1 and P3-P0 are ~103-151 ft from any centerline → interior boundaries.
- Interior angle at corner P2 (between the Northern and 215 Place frontages) = 89.69° [C].

Q1 — LOT LINES, LOT WIDTH, LOT DEPTH

Definitions quoted (all `zr-12-10-...`):
- front: "A \"front lot line\" is a #street line#." (`-lot-line-front`)
- street line: "A \"street line\" is a #lot line# separating a #street# from other land." (`-street-line`)
- rear: "A \"rear lot line\" is any #lot line# of a #zoning lot# except a #front lot line#, which is parallel or within 45 degrees of being parallel to, and does not intersect, any #street line# bounding such #zoning lot#." (`-lot-line-rear`)
- side: "A \"side lot line\" is any #lot line# which is not a #front lot line# or a #rear lot line#." (`-lot-line-side`)
- lot width: "\"Lot width\" is the mean horizontal distance between the #side lot lines# of a #zoning lot#." (`-lot-width`)
- lot depth: "\"Lot depth\" is the mean horizontal distance between the #front lot line# and #rear lot line# of a #zoning lot#. In the case of a #corner lot#, the #lot depth# is the greater of the mean horizontal distances between the #front lot lines# and the respective #side lot line# opposite each." (`-lot-depth`)
- corner lot (`-lot-corner`): "A \"corner lot\" is either a #zoning lot# bounded entirely by #streets#, or a #zoning lot# which adjoins the point of intersections of two or more #streets# and in which the interior angle formed by the extensions of the #street lines# ... forms an angle of 135 degrees or less. ... The portion of such #zoning lot# subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion ... shall be subject to the regulations for a #through lot# or for an #interior lot# ...".
- interior (`-lot-interior`): "An \"interior lot\" is any #zoning lot# neither a #corner lot# nor a #through lot#."
- through (`-lot-through`): "A \"through lot\" is any #zoning lot#, not a #corner lot#, which adjoins two #street lines# opposite to each other and parallel or within 45 degrees of being parallel to each other. ...".

Q1a — classification of the real lot's lines:
- The lot adjoins the Northern Boulevard / 215 Place intersection and the interior angle is 89.69° ≤ 135°, so it is a CORNER LOT. [C]
- FRONT lot lines: edge P1-P2 (on Northern Boulevard street line) and edge P2-P3 (on 215 Place street line) — each is a #street line#, so each is a front lot line. [C]
- The two interior edges: P0-P1 runs from inner corner P0 to P1, and P1 is a corner of the Northern frontage, so P0-P1 touches (meets) the Northern street line at P1. P3-P0 runs from P3 (a corner of the 215 Place frontage) to P0, so it touches the 215 Place street line at P3. By the rear-lot-line words, a rear lot line must "not intersect ... any #street line# bounding such #zoning lot#." Each interior edge meets a street line at its outer endpoint, so neither qualifies as a rear lot line; being neither front nor rear, each is a SIDE lot line. [C] Therefore the lot has NO rear lot line — two front lot lines and two side lot lines. This reading is corroborated by `zr-23-344`(c), which separately "consider[s]" part of a #side lot line# to be a #rear lot line# on corner lots (it would be unnecessary if a corner lot's non-front lines were already rear lot lines).
- The one word the captured text does not define is "intersect": if meeting only at a shared endpoint were NOT counted as intersecting, an argument could be made that an interior edge is a rear lot line. The folder's definitions do not resolve that; I flag it [?], but the natural reading (endpoint contact = intersect) gives "no rear lot line; both interior edges are side lot lines." Quoted open words: "...and does not intersect, any #street line# bounding such #zoning lot#."

Q1b — lot width and lot depth of the real lot:
- LOT DEPTH, corner-lot method = greater of the two mean horizontal distances between each front lot line and its opposite side lot line. Front P1-P2 (Northern) is parallel to side P3-P0: mean perpendicular distance = 99.98 ft. Front P2-P3 (215 Place) is parallel to side P0-P1: mean perpendicular distance = 103.90 ft. Greater = 103.9 ft. LOT DEPTH ≈ 103.9 ft. [C]
- LOT WIDTH = mean horizontal distance between the side lot lines. The two side lot lines (P0-P1 and P3-P0) meet at P0 at ~89.7° and are not parallel/opposite. "Mean horizontal distance between" two adjacent, non-parallel lines is not defined by the words. So the method does NOT yield a lot width for this corner lot. NOT KNOWN; what is missing is any rule in the captured `-lot-width` definition for a lot whose two side lot lines are not opposite one another (the corner-lot case that `-lot-depth` handles but `-lot-width` does not). [?]
- What the method leaves undecided for a two-frontage lot: lot width (above); and `-lot-depth` returns a single number only by picking the greater of two directions — it does not tell you a depth per frontage.

Q1c — made-up interior lot 40 ft x 100 ft (40 ft on the street) (`made_up_lots.json`):
- One street, on the 40-ft side. Front lot line = that 40-ft #street line#. [C] The opposite 40-ft edge is parallel to it and touches no street line, so it is the REAR lot line. [C] The two 100-ft edges are neither front nor rear → SIDE lot lines. [C]
- LOT WIDTH = mean horizontal distance between the two side lot lines (the 100-ft edges) = 40 ft. [C]
- LOT DEPTH = mean horizontal distance between front and rear lot line = 100 ft. [C]

PART 2 of 7

Q2 — REAR YARD

Controlling words:
- `zr-23-342` (R1-R12): "rear yards shall be provided on #interior lots# ...". (a) Standard lots: (1) #detached#/#zero lot line buildings# — ≤75 ft (from #base plane#): 20 ft at every #rear lot line#; above 75 ft where permitted: 30 ft. (2) #semi-detached#/#attached#: (i) #lot width# <40 ft → 30 ft; (ii) #lot width# ≥40 ft → ≤75 ft 20 ft, above 75 ft 30 ft. (b) Shallow lots: modifiable where an #interior lot# is "less than 95 feet deep," the condition existed 12/15/1961 and is unchanged; reduce 6 inches per foot under 95, never below 10 ft.
- `zr-23-343` (through lots): (a) Exceptions — none apply to a through lot under 110 ft; also none to #large sites#, to a zoning lot whose through-lot portion is contiguous to two corner-lot portions and occupies the entire block frontage, or to a lot occupying an entire block. (b)(1) standard: a through lot "190 feet or more in maximum depth" → ≤75 ft, equivalent open area min depth 40 ft; above 75 ft 60 ft. (b)(2) shallow (<190 ft). (c)(1) location: "midway, or within 10 feet of being midway, between the two #street lines#"; (c)(2) alternative locations ONLY for lots using 23-434 eligible-site provisions, 23-435 towers, provisions superseding R10-without-suffix, or shallow lots under (b)(2).
- `zr-23-344`: (a) "no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less." (c) "Beyond one hundred feet of a #street line# — In all districts ... for #interior# or #through lot# portions of #corner lots#, ... the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects shall be considered a #rear lot line# and the following rules shall apply ...: (1) a #rear yard# ... per 23-342 where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#. (2) In R1 through R5 ... 5 feet where ... coincides with a #side lot line# of an adjoining #zoning lot#. (3) In R6 through R12 ... no #rear yard# ... where ... coincides with a #side lot line# of an adjoining #zoning lot#." (d) analogous rules for zoning lots with multiple rear lot lines.
- R6B is within "R6 through R12": `zr-11-25` — "All regulations applicable to a district designation shall be applicable to such district designation appended with a suffix, except as otherwise set forth ...". No separate R6B rear-yard provision is listed in 23-342/344, so the R6 ... R12 rules reach R6B. [C]

Q2a — real lot, the part more than 100 ft from the corner point:
- The corner point is the Northern/215 Place street-line intersection, essentially vertex P2. The farthest vertex P0 is 144.6 ft from P2 [C], so part of the lot lies beyond a 100-ft radius of the corner point. Under `zr-23-344`(a), "no #rear yard# shall be required within 100 feet of the point of intersection" — so within the 100-ft radius of P2 no rear yard is required; that radius covers most of the lot.
- Whether any rear yard is required OUTSIDE that radius turns on `zr-23-344`(c), which uses a different measure — "the portion of a #side lot line# beyond 100 feet of the #street line# that it intersects." I measured perpendicular distances [C]: side line P0-P1 intersects the NORTHERN street line (at P1) and runs perpendicular to it, reaching only 99.98 ft, so it has NO portion beyond 100 ft of that street line. Side line P3-P0 intersects the 215 PLACE street line (at P3) and runs perpendicular to it, reaching 103.9 ft, so the segment from 100 ft to ~103.9 ft (a ~3.9-ft stub near P0) is "beyond 100 feet of the #street line# that it intersects" and is "considered a #rear lot line#."
- Along that ~3.9-ft deemed rear lot line, because R6B is an R6-R12 district, `zr-23-344`(c)(3): "no #rear yard# shall be required where such #rear lot line# coincides with a #side lot line# of an adjoining #zoning lot#," BUT (c)(1): a #rear yard# per 23-342 is required "where such #rear lot line# coincides with a #rear lot line# of an adjoining #zoning lot#."
- So: NOT KNOWN whether a rear yard is required on that stub. [?] Facts/choices still needed, each named:
  1. The lot-line classification of the ADJOINING zoning lot along the P3-P0 boundary — whether that boundary coincides with the neighbour's rear lot line (→ 23-342 rear yard) or side lot line (→ none in R6-R12). The folder has no neighbour geometry. [?]
  2. If 23-342 applies: the building type — #detached#/#zero lot line# vs #semi-detached#/#attached# — and the #lot width# (itself undecided here, Q1b), which select 20 vs 30 vs (width<40) 30 ft. [?]
  3. The building height relative to 75 ft (above/below), for 20 vs 30 ft. [?]
  4. Whether the C2-2 overlay modifies the yard: `zr-34-11`/`zr-34-21` route yard modifications to Section 34-23 (Modification of Yard Regulations), which is NOT in the folder → the overlay's effect on the rear yard is NOT KNOWN. [?]
- (I note the lot's shallow-lot test under 23-342(b)/23-344 would need the 12/15/1961 depth history, also absent.)

Q2b — made-up interior lot 40 ft x 100 ft, under `zr-23-342`:
- Interior lot; #lot width# = 40 ft; depth 100 ft (≥95 ft, so NOT a shallow lot under (b) — no reduction). [C]
- Depth of the required rear yard by the cases the text distinguishes:
  - #detached#/#zero lot line buildings# (a)(1): 20 ft at/below 75 ft; 30 ft above 75 ft (where permitted). [C]
  - #semi-detached#/#attached# (a)(2): lot width is 40 ft = "40 feet or greater," so (a)(2)(ii) applies: 20 ft at/below 75 ft; 30 ft above 75 ft. The <40-ft branch (a)(2)(i) (30 ft regardless of height) does NOT apply because 40 is not "less than 40 feet." [C]
- Facts that decide: the building type (detached/zero-lot-line vs semi-detached/attached) and the building height relative to 75 ft measured from #base plane#. For this width, every applicable case gives 20 ft at/below 75 ft and 30 ft above 75 ft. [C]

Q2c — made-up through lot 40 ft x 200 ft, under `zr-23-343`:
- Through lot, 200 ft between the two streets. [F]
- Exceptions (a): the lot is ≥110 ft, so (a)(1) does not exempt it. (a)(2) #large sites# — "large site" is not defined in the folder, so I cannot confirm the lot is or isn't a large site [?] (8,000 sq ft is small, but the term is undefined here). (a)(3)/(a)(4) need block-frontage facts not in the folder [?]. Taking the plain small-lot case, no exception removes the requirement.
- Depth (b): 200 ft ≥ 190 ft → "standard lot" rule (NOT shallow, so no reduction). Required #rear yard equivalent# open area: min depth 40 ft at/below 75 ft; 60 ft above 75 ft (where permitted). [C]
- Thresholds the 200-ft depth crosses: ≥110 ft (so not exempt under (a)(1)); ≥190 ft (so the full 40/60 ft applies and it is not a shallow lot). [C]
- Location (c)(1): the equivalent must be "midway, or within 10 feet of being midway, between the two #street lines#" — i.e., centred ~100 ft from each street line (90-110 ft band). [C] The alternative locations in (c)(2) are NOT available: the deciding words restrict them to lots "utilizing the height and setback provisions for eligible sites in Section 23-434, the tower regulations of Section 23-435, or other height and setback provisions ... that modify or supersede the underlying provisions for R10 Districts without a letter suffix, or for shallow lots eligible for ... paragraph (b)(2)" — a plain R6B through lot is none of these. [C]
- Still needed: building height vs 75 ft (40 vs 60 ft); whether it is a #large site# (undefined in folder); block-frontage facts for (a)(3)/(a)(4). [?]

Q2d — made-up corner lot 150 ft (street A) x 100 ft (street B), the part beyond 100 ft of the corner point:
- Corner lot; streets meet at a right angle at one corner O. Front lot lines: the 150-ft edge on street A and the 100-ft edge on street B. The other two edges are side lot lines (same reasoning as Q1a). [C]
- Perpendicular depth from street A = 100 ft (the whole lot is within 100 ft of street A). Perpendicular depth from street B = 150 ft. [C]
- `zr-23-344`(a): within a 100-ft radius of corner O, no rear yard. (c): the side lot line opposite street A (the 150-ft edge at the far side) intersects the street B line at its near end; its portion "beyond 100 feet of the #street line# that it intersects" (street B) is the 50-ft segment from 100 ft to 150 ft — that segment "shall be considered a #rear lot line#." The other side lot line (the 100-ft edge opposite street B) intersects street A and never exceeds 100 ft from it, so it yields no deemed rear lot line. [C]
- Along that 50-ft deemed rear lot line, R6-R12 rule (c)(3): no rear yard where it coincides with the neighbour's #side lot line#; (c)(1): a 23-342 rear yard where it coincides with the neighbour's #rear lot line#. So NOT KNOWN whether a rear yard is required. [?] Facts needed: the adjoining lot's lot-line type along that 50-ft segment; and, if 23-342 applies, the building type, lot width and height vs 75 ft. (These made-up lots are plain R6B with no overlay, so no 34-23 overlay issue.) [?]

PART 3 of 7

Q3 — ZR 23-436 AND ZR 35-633

First, the two streets by the captured definition (`zr-12-10`): "A 'wide street' is any street 75 feet or more in width. ... A 'narrow street' is any street less than 75 feet wide." Northern Boulevard mapped width 100 ≥ 75 → WIDE street [C]; 215 Place mapped width 60 < 75 → NARROW street [C].

Q3a — `zr-23-436` paragraph by paragraph (header districts "R6 R7 R8 R9 R10 R11 R12"; reaches R6B via `zr-11-25`):
- (a) "Existing buildings may be vertically #enlarged# by up to one story or 15 feet without regard to the #street wall# location requirements of Section 23-431." Applies to EXISTING buildings being vertically enlarged.
- (b) "On #through lots# which extend less than 190 feet in maximum depth ... the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage." Applies to through lots under 190 ft deep.
- (c) "On #corner lots#, or portions thereof, the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one of the #street# frontages ... is a #wide street# and the other a #narrow street#, the #street wall# location rules shall be applied along the #wide street# frontage." Applies to corner lots.
- (d) "The #street wall# location and minimum base height provisions of Sections 23-431 and 23-432 ... shall not apply along any street frontage of a #zoning lot# occupied by buildings whose #street wall# heights or widths will remain unaltered." Applies to lots keeping existing street walls unaltered.
- (e) "The minimum base height provisions of Section 23-432 shall not apply to #buildings#, or portions thereof, that are #developed# or #enlarged# and do not exceed such minimum base heights." Applies to buildings/portions below the minimum base height.
- (f) "For any zoning lot located in a Historic District designated by the Landmarks Preservation Commission, the #street wall# location and minimum or maximum base height regulations ... may be modified ..." (two sub-rules tied to adjacent buildings). Applies to lots in an LPC Historic District.
- (g) "Where a continuous sidewalk widening is provided on the #zoning lot#, along the entire #block# frontage ... the boundary of the sidewalk widening shall be considered to be the #street line# for ... Section 23-431; but such widening may be included in the setback reductions permitted pursuant to paragraph (a) of Section 23-433." Applies to lots providing a continuous sidewalk widening along the whole block frontage.

Q3b — which paragraphs bind a NEW all-residential building on the real lot (R6B + C2-2 overlay):
- Routing: the lot is a C2-2 Commercial District mapped within R6B (R6-R12 equivalency). `zr-34-11` makes Article II Ch 3 bulk apply to residential buildings "except as modified by ... 34-21 through 34-24." `zr-34-24`(b)(1): in Commercial Districts with R6-R12 equivalency "the modifications to #residential# height and setback regulations set forth in Section 35-63, inclusive, shall be applied." `zr-35-633` then states "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows: (a) references to ... Section 23-431 shall be superseded by those of Section 35-631 ...". So 23-436 DOES bind this building, via 35-633, with 23-431 street-wall references read as 35-631. [C]
- Paragraph results for a new all-residential building on this corner lot:
  - (a) — DOES NOT APPLY. Deciding words: "Existing buildings may be vertically #enlarged#"; the subject is a new building, not an enlargement. [C]
  - (b) — DOES NOT APPLY. The lot is a corner lot, not a "#through lot#." [C]
  - (c) — APPLIES. "On #corner lots# ... the #street wall# location requirements ... shall be mandatory along only one #street# frontage ... applied along the #wide street# frontage." Northern Boulevard is the wide street (100 ft) and 215 Place the narrow street (60 ft), so the street-wall location rule (as 35-631, per 35-633(a)) is mandatory along Northern Boulevard. [C]
  - (d) — DOES NOT APPLY on the stated facts (a new building leaves no existing street walls "unaltered"). Conditional only if an existing building is kept, which the facts do not state. [C]/[?]
  - (e) — CONDITIONAL / NOT KNOWN. Applies only to a building or portion that "do[es] not exceed" the minimum base height (R6B minimum base height = 30 ft, `zr-23-432`). Depends on the chosen building height. [?]
  - (f) — NOT KNOWN. Depends on whether the lot is in an LPC-designated Historic District; the folder records no Historic District (no such field; spdist fields absent). [?]
  - (g) — CONDITIONAL / NOT KNOWN. Applies only if a continuous sidewalk widening along the entire block frontage is provided — a design choice not in the facts. [?]

Q3c — `zr-35-633` paragraph by paragraph, and application to the real lot:
- Chapeau: "The additional height and setback regulations set forth in Section 23-436 shall apply, except as follows." Applies to zoning lots in the `zr-35-63` scope — "Commercial Districts mapped within, or with a #residential equivalent# of R6 through R12 Districts" (header C1 C2 C4 C5 C6). The C2-2 overlay within R6B is such a district (reached via 34-24(b)(1)), so the chapeau APPLIES to the real lot's all-residential building. [C]
- (a) "references to the #street wall# location provisions of Section 23-431 shall be superseded by those of Section 35-631." Applies wherever 23-436 cites 23-431 — which includes 23-436(c) (the corner-lot rule that binds here). So on the real lot the street-wall location along Northern Boulevard is governed by 35-631, not 23-431. APPLIES. [C]
- (b) "for the purposes of applying the #street wall# modifications on #corner lots#, where a #zoning lot# is bounded by only one #street line# along a #street# frontage where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage." Applies to corner lots meeting that condition. The real lot IS a corner lot, but whether it "is bounded by only one #street line# along a ... frontage where a #Commercial District# is mapped along the entire #block# frontage" is NOT KNOWN — the folder does not record whether the C2-2 overlay covers the entire block frontage, nor the single-street-line condition. [?]
- Missing fact for (b): the extent of the C2-2 overlay along each block frontage (entire frontage or not). The overlay query (`zoning_nyco_query_C2-2.json`) gives only feature areas, not block-frontage coverage for this lot. [?]

PART 4 of 7

Q4 — ZR 34-21 (with 34-11, 34-112, 34-113)

Q4a — what `zr-34-21` says, and whether it changes FAR, lot coverage, yards, or the dwelling-unit rule for a residential building in a C2-2 district mapped within R6B:
- `zr-34-21` (C1 C2 C3 C4 C5 C6): "the #bulk# regulations applicable to #residential buildings# as set forth in Section 34-11 ... are modified by the provisions of Sections 34-22 (Modification of Floor Area Regulations), 34-23 (Modification of Yard Regulations) and 34-24 (Modification of Height and Setback Regulations). The purpose of these modifications is to make the regulations set forth in Article II, Chapter 3, applicable to #Commercial Districts#."
- By its own words, 34-21 changes NOTHING directly — it is a routing/general provision. It names the three sections that carry the modifications. Consequences for the four items asked: [C]
  - Floor area ratio / floor area: modified, if at all, by 34-22 — NOT in the folder → NOT KNOWN. [?]
  - Lot coverage: 34-21 names only floor area, yards and height/setback; lot coverage is not one of the three named modification topics, so 34-21 does not itself modify it. Any lot-coverage modification would sit in 34-22 (floor area), which is absent → NOT KNOWN. [?]
  - Yards: modified, if at all, by 34-23 — NOT in the folder → NOT KNOWN. [?]
  - Dwelling-unit rule: NOT named by 34-21 (the three sections are floor area, yards, height/setback), so 34-21 does not change the dwelling-unit rule. [C]
- (For completeness: height/setback IS routed, by 34-24, to Section 35-63 inclusive, which IS in the folder — but Q4a asks only about FAR, lot coverage, yards and the DU rule.) Context: `zr-34-11` — "the #bulk# regulations of Article II, Chapter 3, shall apply to all #residential buildings# ... except as modified by ... Sections 34-21 through 34-24"; and `zr-34-111` (which lists C2-2) — "the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply" (i.e., R6B). [C]

Q4b — 34-11 names Sections 34-22 and 34-23; are they in the folder?
- NO. The folder holds `zr-34-11`, `zr-34-111`, `zr-34-112`, `zr-34-113`, `zr-34-21`, `zr-34-24` — but NOT 34-22 or 34-23. [F]
- Pointing words (`zr-34-21`): "Section 34-22 (Modification of Floor Area Regulations) ... 34-23 (Modification of Yard Regulations)." So 34-22 concerns modification of floor-area regulations; 34-23 concerns modification of yard regulations. [C]
- What stays NOT KNOWN without them: how floor-area (and any lot-coverage) regulations and the yard regulations (including the rear yard of Q2a) are modified for a residential building in the C2-2 overlay. This makes the Q2a rear-yard answer conditional and any FAR/floor-area conclusion unknown. [?]

Q4c — does `zr-34-112` (its table) apply to a C2-2 district mapped within R6B, or is that `zr-34-111`?
- It is `zr-34-111`, NOT 34-112. Deciding words: `zr-34-112` header district list is "C1-6 C1-7 C1-8 C1-9 C2-6 C2-7 C2-8 C3 C4 C5 C6" — C2-2 is not in it. `zr-34-111` header is "C1-1 C1-2 C1-3 C1-4 C1-5 C2-1 C2-2 C2-3 C2-4 C2-5" — C2-2 IS listed, and 34-111 says "the #bulk# regulations for the #Residence District# within which such #Commercial Districts# are mapped apply" (here, R6B). [C] So 34-112's residential-equivalent table does not govern C2-2-within-R6B; the surrounding R6B does. (34-111's own exceptions (a)/(b) apply only within R1-R5, not R6B, so they do not bite here.)

Q5 — SPECIAL DENSITY AREAS

Definitions quoted:
- `zr-12-10-special-density-areas`: "\"Special density areas\" ... shall include: (a) the #Manhattan Core#; and (b) the #Special Downtown Brooklyn District#."
- `zr-12-10-manhattan-core`: "The \"Manhattan Core\" is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8."
- `zr-12-10-special-downtown-brooklyn-district`: "The \"Special Downtown Brooklyn District\" is a Special Purpose District designated by the letters \"DB\" in which special regulations set forth in Article X, Chapter 1, apply."

Facts compared: borough = Queens (borocode 4, "QN"); community district "411" (Queens CD 11); spdist1/spdist2/spdist3 ABSENT from the served PLUTO row. [F]

- Manhattan Core: SETTLED — NO. The Manhattan Core is "within Manhattan Community Districts 1 ... 8"; the lot is in Queens, not Manhattan, so it cannot be within a Manhattan community district. Fact compared: borough = Queens. [C]
- Special Downtown Brooklyn District: SETTLED — NO. It is a "Special Purpose District designated by the letters 'DB'" (a Brooklyn, Downtown-Brooklyn district). The lot is in Queens, and the PLUTO row carries no special-district designation (spdist fields absent), so no "DB" district is assigned. [C] Caveat: the definition points the precise boundaries/regulations to "Article X, Chapter 1," which is NOT in the folder, so the exact district map is NOT KNOWN from the folder [?]; but that map is not needed to exclude a Queens lot with no special-district designation.

PART 5 of 7

Q6 — HOW HEIGHT IS MEASURED

Q6a — from what level the base heights and building height of `zr-23-432` measure:
- `zr-23-43`: "The height of all #buildings or other structures# shall be measured from the #base plane#." [quote]
- `zr-23-432`: "the minimum base height, maximum base height, and maximum #building# height shall be as set forth in the following table." The table's figures are heights, and by 23-43 they are measured from the #base plane#. [C] (The R6B row gives, for standard residences, minimum base height 30 ft, maximum base height 45 ft, maximum building height 55 ft; the footnotes key the applicable row to being within/ beyond 100 ft of a #wide street# — the lot fronts Northern Boulevard, a wide street.) So: both the base heights and the building height measure from the base plane. [C]

Q6b — what the base-plane definition needs to know about a lot, and which facts are in the folder:
`zr-12-10-base-plane` makes the base plane depend on: [C, from the quoted definition]
1. Whether the building/segment is within 100 ft of a #street line# or beyond it (position). [in folder as geometry — derivable: the lot's frontages and the ~50 ft / ~30 ft street-line offsets place the lot within and, near edge P0-P1, just beyond 100 ft of a street line] — DERIVABLE [F/C]
2. #Curb level# (an elevation). — NOT in the folder [?]
3. #Street wall line level# (the within-100-ft base plane is "any level between #curb level# and #street wall line level#"). — NOT in the folder (and depends on the building) [?]
4. Beyond 100 ft: "the average elevation of the final grade adjoining the #building#" (grade elevations). — NOT in the folder [?]
5. Whether the average final grade adjoining the street wall is "more than two feet below #curb level#" (grade vs curb). — NOT in the folder [?]
6. The optional sloping base plane: whether the site "slope[s] from the #street wall line level# to the #rear wall line level# by at least five percent," and the #rear wall line level#. — NOT in the folder [?]
7. Street-wall width ("#street walls# at least 15 feet in width") / whether the building has a street wall. — a building-design fact, not in the folder [?]
8. Corner-lot / through-lot regulations subjecting portions to different base planes; and, for the weighted-average option (c), the #lot coverage# percentages of each portion. — the lot IS a corner lot (in folder) [F]; lot-coverage percentages depend on the building [?]
- Summary: the planimetric facts (within/beyond 100 ft of a street line; corner-lot status) are in or derivable from the folder; every ELEVATION input (curb level, street-wall-line level, final grade, rear-wall-line level, slope) is NOT in the folder, and street-wall width / lot coverage are building-design choices. Therefore the base-plane ELEVATION for the real lot cannot be determined from the folder — NOT KNOWN, missing: curb level and the adjoining final-grade elevations (and `curb level`, `street wall line level`, `rear wall line level` are not defined in the folder either). [?]

Q7 — ELIGIBLE SITES

Q7a — which zoning lots may use `zr-23-434`, and is the term defined or only pointed to?
- Deciding words: "In the districts indicated, without a letter suffix, for #zoning lots# that meet the criteria of paragraph (a) ...". So: R6-R12 districts WITHOUT a letter suffix, for zoning lots meeting at least one criterion in (a). [C] (It may also combine lots whose combined #lot area# exceeds 40,000 sq ft where at least one meets (a).)
- The criteria ("eligible sites") are set out IN 23-434(a) itself — e.g., a #transportation-infrastructure-adjacent frontage#; interior depth <85 or ≥115 ft, through depth <170 or ≥230 ft; corner lots / multiple front lot lines >15° from perpendicular; through lots / multiple front lot lines >15° from parallel; slope ≥15%; or lot area ≥20,000 sq ft or an entire block. There is NO separate 12-10 defined term "eligible site" in the folder — the content is only in 23-434(a). [C] Several terms the criteria invoke are not in the folder: #transportation-infrastructure-adjacent frontage#, #large sites# (used in (b) of 23-362). [?]

Q7b — `zr-23-362`(b): to which zoning lots does its different maximum lot coverage apply? every lot ≥30,000 sq ft?
- Deciding words: "for #zoning lots# with #buildings# utilizing the eligible site provisions of Section 23-434." So (b) applies ONLY to lots whose buildings use the 23-434 eligible-site provisions: then "(1) 65 percent on #zoning lots# with a #lot area# of 30,000 square feet or more that are not #large sites#; and (2) 50 percent on #large sites#." [C]
- It does NOT apply to every lot of 30,000 sq ft or more — only to those that are actually using 23-434. A 30,000-sq-ft lot NOT using 23-434 falls under 23-362(a) (80% interior/through, 100% corner), not (b). [C]

Q7c — does any of this apply to the real lot (recorded lot area 10,075 sq ft)?
- NO. [C] Two independent reasons:
  1. 23-434 is limited to districts "without a letter suffix"; R6B HAS the suffix "B," so 23-434 does not apply to R6B. [C] Quoted words: "In the districts indicated, without a letter suffix."
  2. 23-362(b) applies only to lots "utilizing the eligible site provisions of Section 23-434"; since 23-434 is unavailable in R6B, (b) cannot apply. Also the recorded lot area (10,075 sq ft) and the outline area (~10,388 sq ft) are both far below both the 20,000-sq-ft 23-434(a)(3) threshold and the 30,000-sq-ft 23-362(b)(1) threshold. [C]
- (Note the lot-area discrepancy: `zr-12-10-lot-area` defines "lot area" as "the area of a #zoning lot#"; the recorded tabular lotarea is 10,075 sq ft while the outline/Shape__Area is ~10,388 sq ft. Both are well under the thresholds, so the conclusion is unaffected. [F/C]) So neither 23-434 nor 23-362(b) applies to the real lot; the applicable maximum residential lot coverage is 23-362(a) — 100% for this corner lot — subject to any overlay modification via the absent 34-22. [C]/[?]

PART 6 of 7

Q8 — THE WORD "RESIDENTIAL"

Q8a — definitions (`zr-12-10-residence-or-residential`):
- "A \"residence\" is one or more #dwelling units# or #rooming units#, including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas. A #residence# may, for example, consist of one-family or two-family houses, multiple dwellings, boarding or rooming houses, or #apartment hotels#. However, #residences# do not include: (a) such transient accommodations as #transient hotels#, #motels# or #tourist cabins#, or #trailer camps#; (b) #non-profit hospital staff dwellings#; or (c) student dormitories, fraternity or sorority student houses, monasteries or convents, #long-term care facilities#, or other living or sleeping accommodations in #community facility buildings# or portions of #buildings# used for #community facility uses#."
- "\"Residential\" means pertaining to a #residence#."
- Spaces a residence INCLUDES, by the words: dwelling units or rooming units, "including common spaces such as hallways, lobbies, stairways, laundry facilities, recreation areas or storage areas." [C]

Q8b — is "residential floor area" a defined term in the folder, and the base of each share in 23-23 to 23-234 (no computation):
- "residential floor area" is NOT a defined term in the folder. The folder holds `zr-12-10-floor-area` (defining "#floor area#") but no capture defining "residential floor area." [F]
- `zr-23-23` (parent): states that floor space "allocated to #building# amenities, corridors, refuse storage or disposal, or access to elevated ground floor #dwelling units# may be exempted from the definition of #floor area# ... provided that the provisions of this Section, inclusive, are met." It gives no share itself — it routes to 23-231 to 23-234. [C]
- `zr-23-231` (amenities): base named — "in an amount not to exceed five percent of the #residential floor area# of the #building#." The base is "the #residential floor area# of the #building#." Because "residential floor area" is NOT defined in the folder, the captured text does NOT settle what that base is. [?]
- `zr-23-232` (corridors): base named — "Fifty percent of the floor space of a corridor may be exempted." The base is that corridor's own floor space; this IS settled by the words (no reference to a building-wide floor-area figure). [C]
- `zr-23-233` (refuse): base named — "in an amount not to exceed a maximum of three square feet per #dwelling unit# in the #building#." The base is a per-#dwelling unit# amount (3 sq ft × number of dwelling units); settled as a rule (the DU count is a building fact). [C]
- `zr-23-234` (elevated ground-floor units): base named — "up to 100 square feet of such entryways ... for each foot of difference between the floor level of such #dwelling units# and #curb level#," capped at "a maximum of 500 square feet ... for each #building#." The base is per foot of elevation difference, capped per building; settled as a rule (the elevation difference is a design fact). [C]
- So only 23-231 keys its share to "#residential floor area#," whose meaning the folder does not settle; the other three state bases in their own words. (No figures computed, per instruction.) [C]/[?]

Q9 — WHAT IS MISSING (sections/terms pointed to but not in the folder; pointing words ≤25 words; and which answers stay NOT KNOWN/conditional)

- Section 34-22 "Modification of Floor Area Regulations" (pointed to by 34-21). → Q4a (FAR/floor area), Q4b, Q7c lot-coverage-overlay stay NOT KNOWN/conditional. [?]
- Section 34-23 "Modification of Yard Regulations" (34-21). → Q2a and any overlay yard conclusion stay conditional. [?]
- Section 34-24 names Sections 35-62/35-63 inclusive, 36-64, 35-71 — 35-63/35-631/35-633 ARE in the folder; 35-632 (max height and setback), 36-64, 35-71 and 35-62 are NOT read/quoted here → the actual height/setback NUMBERS and sky-exposure-plane option stay NOT KNOWN for Q3/Q6. [?]
- Section 23-44 "Special Provisions for Certain Areas" (pointed to by 23-43, 23-41, 23-436 "Section 23-44, inclusive"). → could further modify Q3/Q6 height/setback. [?]
- Section 23-341 "Permitted obstructions in required yards or rear yard equivalents" (23-343(c)); and 23-311/23-312 (23-343(c)(2)). → what may obstruct the Q2c rear-yard equivalent stays NOT KNOWN. [?]
- "#large sites#" (23-343(a)(2), 23-362(b), 23-434) — not defined in folder. → Q2c exception and Q7b/Q7c large-site cases stay NOT KNOWN. [?]
- "#transportation-infrastructure-adjacent frontage#" (23-434(a)(1)) — not in folder. → Q7a criterion detail unknown (does not change Q7c, barred by suffix). [?]
- "#residential equivalent#" (34-112, 35-63); "#qualifying residential sites#", "#Greater Transit Zone#" (34-111); "#UAP developments#", "#qualifying senior housing#", "#qualifying affordable housing#", "#Mandatory Inclusionary Housing areas#" (23-432/23-434 footnotes) — not defined in folder. → affect only the alternative (affordable/senior) height rows, not the standard-residence reading. [?]
- "#short dimension of a block#" (23-344(b), 23-363(c)) — not defined in folder. → the "short dimension" rear-yard/lot-coverage exceptions cannot be tested for the real or made-up lots. [?]
- "#curb level#", "#street wall line level#", "#rear wall line level#" (base-plane definition) — not defined/measured in folder. → Q6b base-plane elevation stays NOT KNOWN. [?]
- "Article X, Chapter 1" (Special Downtown Brooklyn District) — not in folder. → Q5 exact SDBD boundary unknown (does not change the Queens exclusion). [?]
- Section 35-632 street-wall/height detail and 35-64 (pointed to by 35-63) — 35-64 present but not read; 35-632 not read. → Q3 street-wall numeric rules stay NOT KNOWN. [?]
- Neighbour (adjoining zoning lot) lot-line classifications — not a section, but an absent FACT the law needs (23-344(c)/(d)). → Q2a and Q2d rear-yard existence stay NOT KNOWN. [?]

PART 7 of 7

Q10 — ONE-LINE SUMMARY PER QUESTION

Q1. The real lot is a corner lot with two FRONT lot lines (Northern Boulevard edge P1-P2; 215 Place edge P2-P3) and two SIDE lot lines (the interior edges), and NO rear lot line; lot depth ≈ 103.9 ft; lot WIDTH is NOT KNOWN because the two side lot lines are adjacent and non-parallel, which `-lot-width` does not resolve (interior 40x100: front/rear = 40-ft street edges, sides = 100-ft edges, width 40 ft, depth 100 ft).

Q2. (a) NOT KNOWN whether a rear yard is required beyond the 100-ft corner — in R6B it hinges on whether the deemed rear lot line (a ~3.9-ft stub of side line P3-P0 beyond 100 ft of the 215 Place street line) coincides with the neighbour's rear vs side lot line, plus building type/height and the absent 34-23; (b) interior 40x100 is 20 ft at/below 75 ft and 30 ft above 75 ft for both detached/zero-lot-line and semi/attached (width 40 ≥ 40), not shallow; (c) through 40x200 needs a 40-ft (≤75 ft) / 60-ft (>75 ft) rear-yard equivalent midway (±10 ft) between the streets — 200 ft is ≥110 (not exempt) and ≥190 (standard, not shallow), and the alternative locations are unavailable to a plain R6B lot; (d) corner 150x100: within 100 ft of the corner no rear yard, and on the 50-ft deemed rear lot line (far edge, 100-150 ft from street B) a rear yard is required only if it meets the neighbour's rear lot line — otherwise NOT KNOWN.

Q3. 23-436 binds via 34-24(b)(1)→35-63→35-633: on the real corner lot only paragraph (c) clearly binds (street-wall mandatory along the WIDE Northern Boulevard, read as 35-631 per 35-633(a)); (a),(b),(d) do not apply; (e),(f),(g) are NOT KNOWN/conditional; and 35-633(b) is NOT KNOWN because the overlay's block-frontage extent is not in the folder.

Q4. 34-21 itself changes nothing — it routes bulk modifications to 34-22 (floor area), 34-23 (yards), 34-24 (height/setback) and does NOT name the dwelling-unit rule, so FAR/lot-coverage and yards stay NOT KNOWN (34-22/34-23 absent); 34-112's table does NOT reach C2-2 (that is 34-111, which sends bulk to the surrounding R6B).

Q5. SETTLED: the real lot is NOT in the Manhattan Core (it is in Queens, not Manhattan CDs 1-8) and NOT in the Special Downtown Brooklyn District (Queens, with no "DB"/special-district designation); the SDBD's exact map (Article X Ch 1) is not in the folder but is not needed to exclude a Queens lot.

Q6. 23-432's base heights and building height are measured from the #base plane# (23-43); the base plane needs curb level, street-wall-line level, final-grade elevations, rear-wall-line level, slope, street-wall width and lot coverage — only the planimetric/position facts are in the folder, so the base-plane ELEVATION is NOT KNOWN (missing curb level and adjoining final grades).

Q7. 23-434 is limited to R6-R12 WITHOUT a letter suffix and to lots meeting its own (a) criteria ("eligible site" is defined in 23-434(a), not a separate 12-10 term); 23-362(b)'s lot-coverage applies ONLY to lots using 23-434, not to every 30,000-sq-ft lot; NONE of it applies to the real lot (R6B is suffixed, and its lot area ~10,075-10,388 sq ft is far below the thresholds).

Q8. "Residence" = one or more dwelling/rooming units including common spaces (hallways, lobbies, stairways, laundry, recreation, storage), excluding transient/hospital-staff/dormitory-type accommodations; "residential" means pertaining to a residence; "residential floor area" is NOT defined in the folder, so 23-231's "five percent of the #residential floor area#" base is NOT settled, while 23-232 (corridor's own floor space), 23-233 (per dwelling unit) and 23-234 (per foot of elevation, capped per building) state their bases in their own words.

Q9. Missing from the folder and leaving answers NOT KNOWN/conditional: Sections 34-22, 34-23, 23-44, 23-341/23-311/23-312, 35-632; the defined terms "large sites", "transportation-infrastructure-adjacent frontage", "residential equivalent", "short dimension of a block", "curb level", "street wall line level", "rear wall line level", "residential floor area"; Article X Ch 1; and the absent FACTS of adjoining-lot lot-line types and the C2-2 overlay's block-frontage extent.

Q10. (this summary).

END-OF-REPORT
