# Independent reading from the step-P8 sealed folder, reading 1 (provenance)

What this is: one of two independent readings made on 2026-10-14, each by a different AI helper that took no part in writing the program's rules. Each worked alone from a sealed folder - the 189 pinned law-text captures (without their notes), the block-7334 lot outlines, the DCM centrelines, the PLUTO rows of lots 70 and 1, the printed tax-map labels, the zoning of lot 70, the stated facts of Building B and the stated measure, and EIGHTEEN answers settled by earlier readings (copied word for word and given as settled, so completed readings are reused and not worked again; the earlier footprint answer real-building-b was left out on purpose) - with no access to the program, this repository or the web. It is a draft reading of the law, not professionally reviewed and not a statement that anything complies. It is reproduced below unchanged, byte for byte. It is reading 1 of the step-P8 pair (a geospatial-engineer); a value is recorded in the placement-building-b reference case only where this reading and reading 2 (return-independent-hand-calculation-18.md) give the same answer on the same basis.

---

DRAFT READING OF LAW TEXT BY AN AI — NOT legal advice, NOT a professional review, NOT a compliance verdict. Every figure is traced to the sealed law text and the stated facts only; no program was used.

ONE-HARD-RULE STATEMENT: I worked only inside the sealed folder .../session-2026-10-14a/sealed-p8 (read-only) and wrote only in my scratch folder .../reader-p8-1 (geom.py, calc.py). I opened no web page, ran no web search, and opened nothing else under /root/project.

FILES READ. facts/: building_b_and_the_stated_measure.json, printed_tax_map_labels.json, pluto_rows_lots_70_and_1.json, zoning_nyzd_query_R6B.json, zoning_nyco_query_C2-2.json, settled_by_earlier_readings.json, block_7334_lot_outlines_epsg2263.json, streets_dcm_centerlines.json. INDEX.json. law/: zr-23-431, zr-23-432, zr-23-433, zr-23-436, zr-23-322, zr-23-335, zr-23-342, zr-23-344, zr-23-362, zr-35-22, zr-35-631, zr-35-632, zr-35-633, zr-12-10-street-wide, zr-12-10-street-narrow, zr-12-10-lot-corner, zr-12-10-street-line, zr-12-10-lot-coverage. Legend: [F] fact, [S] settled sheet, [C] calc/conclusion from quoted text, [?] NOT KNOWN. Nine bases used: law, printed_tax_map, filing_attribute, gis, derived (others unused).

PART 1 of 8 — SETTING AND GEOMETRY FACTS
- [F] Subject: 215-16 Northern Boulevard, Queens, block 7334 lot 70 (BBL 4073340070); zoned R6B (zoning_nyzd_query_R6B.json) with a C2-2 overlay (zoning_nyco_query_C2-2.json); PLUTO splitzone=false (pluto_rows). Condition Z1: lot 70 alone is the zoning lot (stated; whether lots 1+70 are one zoning lot is NOT KNOWN — building_b facts).
- [S] Lot lines (settled real-lot-lot-lines): corner lot, TWO front lot lines (Northern Boulevard edge; 215 Place edge), TWO side lot lines (the two interior edges), NO rear lot line. Quotes §12-10.
- [F] Streets bounding the block (streets_dcm_centerlines.json): Northern Boulevard mapped width 100 ft; 215 Place 60 ft; 215 Street 60 ft. [C] §12-10 "street, wide": "A 'wide street' is any #street# 75 feet or more in width." (zr-12-10-street-wide) → Northern Boulevard = wide. §12-10 "street, narrow": "A 'narrow street' is any #street# less than 75 feet wide." (zr-12-10-street-narrow) → 215 Place = narrow. Basis of widths: gis/administrative (Digital City Map Streetwidth, a free-text mapped width).
- [C] Edge anchoring (my geom.py, from the GIS outline + the 100 ft NB and 60 ft 215 Place centrelines): lot-70 edge V1→V2 (len 103.88 ft) sits ~51 ft from the NB centreline = on the 100 ft NB street line → NB frontage. Edge V2→V3 (len 99.98 ft) sits ~29 ft from the 215 Place centreline = on the 60 ft 215 Place street line → 215 Place frontage. They meet at V2 = the corner of the two street lines. Edge V0→V1 (99.98 ft) is the side lot line shared with lot 1 (opposite 215 Place); edge V3→V4→V0 (103.93 ft) is the back side lot line (opposite NB). This matches [S] corner-reach (reach from NB 99.97 ft, from 215 Place 103.93 ft) and [S] measured area 10,387.99 sq ft.

PART 2 of 8 — Q1 RULES BEARING ON THE PLACEMENT (new all-residential building, 30 ft high, this corner lot, R6B + C2-2). Overlay routing: §35-22 — in C2-2 "the #bulk# regulations for the #Residence Districts# within which such #Commercial Districts# are mapped apply to #residential# portions of #buildings#" (→ R6B governs); §35-632(a) applies the §23-432 table for the applicable Residence District; §35-633 applies §23-436 with §23-431 superseded by §35-631. [S] (min-base-height-overlay) confirms the building is permitted in C2-2/R6B and the 30/45/55 figures carry over.

(a) STREET WALL. §23-436(c): "On #corner lots#… the #street wall# location requirements of Section 23-431 shall be mandatory along only one #street# frontage. Where one of the #street# frontages… is a #wide street# and the other a #narrow street#, the #street wall# location rules shall be applied along the #wide street# frontage" (zr-23-436). So mandatory on the WIDE street = Northern Boulevard; NOT mandatory on the narrow 215 Place. In the overlay §35-631(b) governs the percentage test: "At least 70 percent of the #aggregate width of street walls# shall be located within eight feet of the #street line# and shall extend to at least the minimum base height specified in Sections 23-432, or the height of the #building#, whichever is less." [S] (real-lot-street-wall) confirms mandatory-on-wide via §23-436(c)/§35-633(a)/§35-631(b), 70% within 8 ft. Narrow-street caveat: §35-633(b) — where a zoning lot "is bounded by only one #street line#… where a #Commercial District# is mapped along the entire #block# frontage, the #street wall# shall be applied along such frontage"; whether a Commercial District is mapped along the ENTIRE 215 Place block frontage is [?] NOT KNOWN (zoning only queried for lot 70). Occupancy required: on the wide street ≥70% of aggregate street-wall width within 8 ft of the NB street line (§35-631(b)); extend to min base height 30 ft or building height 30 ft, whichever less (both 30). Line-up alternative (§23-431(a), the named R6B rule) turns on a #prevailing street wall frontage# the readers could not confirm — [S] left horizontal placement unsettled; the stated placement (wall on the line) satisfies the within-8-ft test either way.

(b) FRONT/SIDE YARDS. §23-322: "In the districts indicated, no #front yard# requirements shall apply." (zr-23-322) → no front yard on either street line. §23-335(b): "for #zoning lots# containing all other types of #residences#, no #side yards# shall be required. However, if any open area extending along a #side lot line# is provided at any level, it shall have a minimum width of five feet, measured perpendicular to the #side lot line#." (zr-23-335; (a)'s 5-ft side yards are only for single-/two-family detached, which this is not). So: no side yard required; any open area along a side lot line must be ≥5 ft wide.

(c) REAR YARD (use settled). [S] real-lot-z1-rear-yard = NOT KNOWN: on the tax-map/street-line basis §23-344(b) ("whenever a #front lot line#… coincides with the #street line# of the #short dimension of a block#, no #rear yard# shall be required within 100 feet of such #street line#") waives the rear yard within 100 ft of the NB street line (NB is read as the block's short dimension); on the centreline basis the result rests on §23-344(a) ("no #rear yard# shall be required within 100 feet of the point of intersection of two #street lines# intersecting at an angle of 135 degrees or less"), the settled no-rear-lot-line finding, and §23-344(c) for the beyond-100-ft strip. Unresolved because (i) the governing measurement basis is unresolved and (ii) §23-344(c)/(c)(3) turns on the adjoining zoning lot's lot-line kind, which is [?] NOT KNOWN. PLACEMENT ASSUMES: the building is only ~66.66 ft deep from NB (Part 4), so it lies wholly within 100 ft of the NB street line and of the corner; the placement assumes no rear yard constrains this footprint under §23-344(a)/(b). CAVEAT the placement cannot clear: the building spans the full NB frontage, so it sits ON the side lot line opposite 215 Place; the portion of that side lot line beyond 100 ft of the 215 Place street line is deemed a #rear lot line# (§23-344(c)); §23-344(c)(3) requires no rear yard there IF it coincides with an adjoining #side lot line#, but §23-344(c)(1) requires a §23-342 rear yard IF it coincides with an adjoining #rear lot line# — adjoining kind NOT KNOWN, so whether the building touching that deemed-rear-lot-line is permitted stays NOT KNOWN.

(d) MAX LOT COVERAGE. §23-362(a): "the maximum #residential# #lot coverage# for #interior lots# or #through lots# shall be 80 percent and the maximum #residential# #lot coverage# for #corner lots# shall be 100 percent." (zr-23-362). Which part of a corner lot: §12-10 "lot, corner" — "The portion… subject to the regulations for #corner lots# is that portion bounded by the intersecting #street line# and lines parallel to and 100 feet from each intersecting #street line#. Any remaining portion… shall be subject to the regulations for a #through lot# or for an #interior lot#." So the corner-lot portion (within 100 ft of BOTH street lines) → 100%; any remaining portion → 80%.

(e) SETBACK AT 30 FT. §23-432 R6B row (zr-23-432 table): minimum base height 30 ft, standard maximum base height 45 ft, standard maximum building height 55 ft. §23-432: "For portions of a #building# #street wall# that exceed the maximum base height, a setback shall be provided… in accordance with Section 23-433." §23-433: 10 ft setback from a wide-street street wall, 15 ft from a narrow-street street wall, only at/above the base-height band. [C] The building is 30 ft < 45 ft max base height, so NO portion exceeds the maximum base height → NO setback is required. §23-436(e) also exempts a building not exceeding the minimum base height from the minimum-base-height provision (30 ≤ 30).

PART 3 of 8 — Q2 THE PLATE
- [F] Building B: all-residential, 3 storeys, 30 ft high, 20,150 sq ft zoning floor area total; "plate = zoning floor area per storey (20,150/3)"; no gross-up/exclusions/wall-thickness; physical floor plate not checked (building_b facts).
- [C] plate = 20,150 ÷ 3 = 6,716.6667 → rounded to the hundredth = 6,716.67 sq ft per storey.
- Measure: zoning floor area. Basis: derived (20,150 ÷ 3 storeys). The 20,150 is itself [S] (real-lot-recorded-vs-measured-area) derived as 2.00 FAR (law, R6B) × 10,075 recorded lot area (filing_attribute, PLUTO lotarea); it is a stated design input, not from any approved plan (none exists).

PART 4 of 8 — Q3 FOOTPRINT ON THE PRINTED-TAX-MAP BASIS
- [F] Printed tax-map labels (printed_tax_map_labels.json): lot 70 = "100.76 ft on Northern Boulevard, 100 ft deep" (both maps, 2017 and 2021). PLUTO agrees: lotfront 100.76, lotdepth 100 (pluto_rows). Basis: printed_tax_map.
- Plan width along Northern Boulevard = 100.76 ft (full NB frontage). Basis printed_tax_map.
- Depth the plate needs = plate ÷ width = 6,716.6667 ÷ 100.76 = 66.660050 → 66.66 ft. Basis derived.
- [C] Rounded depth × width = 66.66 × 100.76 = 6,716.66 sq ft (6,716.6616), which is 0.01 sq ft LESS than the plate 6,716.67 (exact shortfall 0.0051 sq ft). Basis derived.
- Distance from the building's back wall to the lot line opposite Northern Boulevard = tax-map depth − building depth = 100 − 66.66 = 33.34 ft. Basis derived (printed_tax_map depth − derived depth).
- Distances to the other lot lines (basis derived from printed_tax_map): to the Northern Boulevard front lot line = 0 (wall on it, full 100.76 ft); to the 215 Place front lot line = 0 (one wall on it, for the 66.66 ft depth); to the side lot line opposite 215 Place (shared with lot 1) = 0 (the building spans the full 100.76 ft NB frontage, so its far wall lies on that side lot line, for the 66.66 ft depth).
- Lot lines the building TOUCHES: Northern Boulevard front lot line (full), 215 Place front lot line (for 66.66 ft), and the lot-1 side lot line (for 66.66 ft) — three of the four. It does NOT touch the back side lot line opposite Northern Boulevard (clear by 33.34 ft). The open remainder is a back strip 100.76 ft × 33.34 ft.

PART 5 of 8 — Q4 PLACEMENT vs EACH Q1 RULE (printed-tax-map basis; rule figure | placement figure)
(a) Street wall, wide (Northern Boulevard): rule ≥70% of aggregate street-wall width within 8 ft of the street line (§35-631(b), law) | placement 100% of the 100.76 ft wall at 0 ft from the street line (derived from printed_tax_map). Extend-to height: rule min base 30 ft or building height, whichever less = 30 ft (law) | building 30 ft [F]. Street wall, narrow (215 Place): rule not mandatory for this corner lot unless §35-633(b) condition holds = [?] NOT KNOWN its own figure | placement wall at 0 ft along 66.66 ft (derived).
(b) Front yard: rule 0 required (§23-322, law) | placement 0 (derived). Side yard: rule 0 required, any open area along a side lot line ≥5 ft wide (§23-335(b), law) | placement leaves a back open strip 33.34 ft wide along the side lot line opposite NB and 33.34 ft along the rear part of the lot-1 side line — both ≥5 ft (derived).
(c) Rear yard: rule figure = [?] NOT KNOWN (§23-344, [S]; 20 ft if a §23-342 rear yard were ever required) | placement back clearance 33.34 ft (derived), building confined to within 66.66 ft of NB; conflict at the deemed-rear-lot-line (Part 2c) stays NOT KNOWN.
(d) Lot coverage: rule 100% for the corner-lot portion, 80% for interior/through portion (§23-362(a), law). Footprint share of the lot = footprint ÷ lot area. Lot area used = printed-tax-map rectangle 100.76 × 100 = 10,076 sq ft (basis printed_tax_map/derived; the PLUTO recorded lotarea is 10,075, filing_attribute — a conflicting input). Footprint 6,716.66 ÷ 10,076 = 66.66%. By portion: the footprint's corner part = 100 × 66.66 = 6,666.00 sq ft against a 100%-allowed corner portion of 100 × 100 = 10,000 sq ft; its interior part = 0.76 × 66.66 = 50.66 sq ft against an 80%-allowed interior strip of 0.80 × (0.76 × 100) = 60.80 sq ft — within both per-portion maxima (all derived). [S] (real-lot-coverage-by-portion) note: the whole-lot lot-coverage figure stays NOT KNOWN as a single number (read by portion; the two earlier readers' GIS-outline measurements differ).
(e) Setback: rule required only above the 45 ft max base height (§23-432/§23-433, law) | building 30 ft [F] → none. No conflict.

PART 6 of 8 — Q5 CONFLICT CHECK ON THE CITY GIS OUTLINE (gis figure | tax-map figure | difference). GIS lot area = 10,387.99 sq ft (shoelace, gis; [S] agrees).
- Frontage along Northern Boulevard: 103.88 ft | 100.76 ft | +3.12 ft (GIS longer). Basis gis vs printed_tax_map.
- Depth available back from Northern Boulevard (perpendicular reach): 99.97 ft | 100 ft | -0.03 ft. (Note the ZR §12-10 corner-lot "lot depth" on GIS is ~103.9 ft, [S], vs the tax-map "100 ft deep.")
- Plan's depth the plate needs (= plate ÷ frontage): 6,716.6667 ÷ 103.88 = 64.66 ft | 66.66 ft | -2.00 ft. Basis derived.
- Distance back wall to the lot line opposite NB: 99.97 − 64.66 = 35.31 ft | 33.34 ft | +1.97 ft. Basis derived.
- Distances to NB line, 215 Place line, lot-1 side line: 0 | 0 | 0 on both bases (touches). Basis derived.
- Footprint share of lot area: 6,716.66 ÷ 10,387.99 = 64.66% | 66.66% | -2.00 percentage points. Basis derived.
I do not choose between the bases; both are shown. (The GIS outline is a near-parallelogram, not a true rectangle, so its "frontage/depth" are the NB-edge length and the mean perpendicular reach; a rectangular building cannot sit perfectly inside it — a further reason the two bases should not be mixed.)

PART 7 of 8 — Q6 AREA ALLOCATION AT THE 60% SHARE
- [F] Share = 60% apartment area (low end of a 60-75% assumption; an assumption, not a measurement), applied to the proposed building's residential floor area; the rest is other building area (core, circulation, walls, services). All-residential → residential floor area = the 20,150 sq ft zoning floor area.
- [C] Apartment area: total 0.60 × 20,150 = 12,090.00 sq ft; per storey 12,090 ÷ 3 = 4,030.00 sq ft. Other building area: total 0.40 × 20,150 = 8,060.00 sq ft; per storey 8,060 ÷ 3 = 2,686.67 sq ft (2,686.6667).
- Sums (checks): per storey 4,030.00 + 2,686.67 = 6,716.67 = the plate; totals 12,090.00 + 8,060.00 = 20,150.00 = the total. Measure: zoning floor area. Basis: derived (stated ZFA × stated 60%).
- What this does NOT establish: not a dwelling-unit count, not net/rentable/usable area, not a physical floor plate, not any layout; the 60% is a stated assumption, not a measurement; it establishes no compliance and no feasibility.

PART 8 of 8 — Q7 WHAT IS MISSING, and Q8 TABLES

Q7 — Pointed-to texts the folder does NOT hold (pointing words ≤25 words), and what stays NOT KNOWN/conditional:
- §12-10 "short dimension of a block" (pointed by §23-344(b) "coincides with the #street line# of the #short dimension of a block#") — the §23-344(b) rear-yard waiver on the tax-map basis is conditional. (The term's own file exists in INDEX but was not needed/opened for a quote; the block's SW end is [S] unresolved regardless.)
- §23-343 "Rear yard equivalent requirements" (pointed by §23-344 "the #rear yard equivalent# requirements of Section 23-343… shall be modified") — not independently read; rear-yard analysis stays conditional.
- §23-341 "Permitted obstructions in required rear yards" (pointed by the §12-10 lot-coverage definition "obstructions permitted pursuant to Section 23-341… shall not be included in #lot coverage#") — not read; obstruction/lot-coverage edge cases NOT settled.
- §12-10 "prevailing street wall frontage" / "aggregate width of street walls" (pointed by §23-431 and §35-631 "where… do not have a #prevailing street wall frontage#"; "70 percent of the #aggregate width of street walls#") — not read here; the horizontal street-wall placement and the exact occupancy test stay NOT KNOWN ([S] agrees).
- §23-434 "Height and setback modifications for eligible sites" (pointed by §23-362(b) and §35-632(b)) — not read; the eligible-site 65%/50% coverage path is not evaluated (not invoked by this placement).
Missing FACTS about the real lot that answers turned on:
- No survey, deed, or zoning-lot description for lot 70 or any neighbour → the adjoining lot-line kind for §23-344(c) is NOT KNOWN (rear-yard caveat, Part 2c); the zoning-lot identity (Z1) is a condition, not a fact.
- The printed-tax-map rectangle (100.76 × 100 = 10,076), the PLUTO recorded lotarea (10,075), and the GIS-measured outline (10,387.99) conflict by ~313 sq ft; which is correct is NOT KNOWN — a surveyed outline would settle it.
- Whether a Commercial District is mapped along the entire 215 Place block frontage (§35-633(b)) is NOT KNOWN → the narrow-street street-wall mandate is conditional.
- No ground elevations / base plane / curb level in the folder → nothing turned on them here (building below base height), but any height-measured-from-base-plane check is unverifiable.

Q8 — TABLE OF EVERY QUANTITY (name | value | unit | basis | computed from):
1 Northern Boulevard mapped width | 100 | ft | gis | DCM Streetwidth
2 215 Place mapped width | 60 | ft | gis | DCM Streetwidth
3 NB classification | wide | - | law | §12-10 (≥75 ft)
4 215 Place classification | narrow | - | law | §12-10 (<75 ft)
5 ZFA total (Building B) | 20,150.00 | sq ft | derived | 2.00 FAR(law)×10,075 recorded lot area(filing_attribute) [stated design input]
6 Plate per storey | 6,716.67 | sq ft | derived | 20,150÷3
7 Tax-map NB frontage | 100.76 | ft | printed_tax_map | tax-map label / PLUTO lotfront
8 Tax-map depth | 100 | ft | printed_tax_map | tax-map label / PLUTO lotdepth
9 Tax-map lot area | 10,076 | sq ft | derived | 100.76×100 (printed_tax_map)
10 PLUTO recorded lot area | 10,075 | sq ft | filing_attribute | PLUTO lotarea
11 Plan depth (tax map) | 66.66 | ft | derived | 6,716.6667÷100.76
12 Rounded depth×width (tax map) | 6,716.66 | sq ft | derived | 66.66×100.76
13 Plate−(depth×width) | 0.01 (0.0051) | sq ft | derived | 6,716.6667−6,716.6616
14 Back-wall clearance (tax map) | 33.34 | ft | derived | 100−66.66
15 Footprint (tax map) | 6,716.66 | sq ft | derived | 100.76×66.66
16 Footprint share (tax map) | 66.66 | % | derived | 6,716.66÷10,076
17 Corner-lot portion (tax map) | 10,000.00 | sq ft | derived | 100×100 (within 100 ft of both lines)
18 Interior strip (tax map) | 76.00 | sq ft | derived | 0.76×100
19 Corner max coverage | 100 | % | law | §23-362(a)
20 Interior/through max coverage | 80 | % | law | §23-362(a)
21 GIS lot area | 10,387.99 | sq ft | gis | shoelace of outline
22 GIS NB frontage | 103.88 | ft | gis | edge V1–V2
23 GIS 215 Place frontage | 99.98 | ft | gis | edge V2–V3
24 GIS depth from NB (perp reach) | 99.97 | ft | gis | perpendicular to NB edge ([S] 99.97)
25 GIS reach from 215 Place | 103.93 | ft | gis | [S] / perpendicular to 215 Place edge
26 Plan depth (GIS) | 64.66 | ft | derived | 6,716.6667÷103.88
27 Back-wall clearance (GIS) | 35.31 | ft | derived | 99.97−64.66
28 Footprint share (GIS) | 64.66 | % | derived | 6,716.66÷10,387.99
29 R6B min base height | 30 | ft | law | §23-432 table
30 R6B max base height | 45 | ft | law | §23-432 table
31 R6B max building height | 55 | ft | law | §23-432 table
32 Building height | 30 | ft | derived | stated 3 storeys×10 ft [F]
33 Setback required at 30 ft | none | - | law | §23-432/§23-433 (30<45)
34 Wide-street street-wall test | ≥70% within 8 ft | %/ft | law | §35-631(b)
35 Front yard required | 0 | ft | law | §23-322
36 Side yard required | 0 | ft | law | §23-335(b)
37 Min open-area width along side lot line | 5 | ft | law | §23-335(b)
38 §23-344(a) corner waiver radius / angle | 100 / 135 | ft / deg | law | §23-344(a)
39 Apartment area total (60%) | 12,090.00 | sq ft | derived | 0.60×20,150
40 Other building area total | 8,060.00 | sq ft | derived | 0.40×20,150
41 Apartment area per storey | 4,030.00 | sq ft | derived | 12,090÷3
42 Other area per storey | 2,686.67 | sq ft | derived | 8,060÷3
43 Z1 rear-yard requirement | NOT KNOWN | - | - | [S] real-lot-z1-rear-yard

ONE-LINE SUMMARIES:
Q1: On this R6B/C2-2 corner lot a 30-ft all-residential building has the street wall mandatory only on the wide Northern Boulevard frontage (≥70% within 8 ft, §35-631(b)/§23-436(c)), no front yard (§23-322), no side yard but any side-lot-line open area ≥5 ft (§23-335(b)), rear yard NOT KNOWN under Z1 (§23-344), lot coverage 100% on the corner-lot portion / 80% on any remainder (§23-362(a)), and NO setback (30 ft < 45 ft max base height).
Q2: Plate = 20,150 ÷ 3 = 6,716.67 sq ft/storey (zoning floor area, basis derived).
Q3: On the tax-map lot (100.76 × 100), the 100.76-ft-wide plan needs 66.66 ft of depth (66.66×100.76 = 6,716.66, ~0.01 sq ft under the plate), leaving 33.34 ft to the lot line opposite Northern Boulevard; it touches the Northern Boulevard, 215 Place, and lot-1 side lot lines (0 ft) and clears only the back side lot line.
Q4: The placement meets each knowable Q1 figure (wall on the line = 100% ≥ the 70%; yards 0 where 0 is allowed; 66.66% footprint under the 100% corner / 80% interior maxima; no setback), while the rear-yard figure and the deemed-rear-lot-line touch stay NOT KNOWN.
Q5: Switching to the GIS outline changes frontage 100.76→103.88 ft (+3.12), depth available 100→99.97 ft (−0.03), plan depth 66.66→64.66 ft (−2.00), back clearance 33.34→35.31 ft (+1.97) and footprint share 66.66%→64.66% (−2.00 pts); the three touching distances stay 0 — bases not mixed, no choice made.
Q6: At 60%, apartment area = 12,090.00 sq ft total / 4,030.00 per storey and other area = 8,060.00 / 2,686.67, summing to the 6,716.67 plate and the 20,150 total; it establishes no units, no layouts, no compliance.
Q7: Missing texts (short-dimension-of-a-block, §23-343, §23-341, prevailing-street-wall-frontage/aggregate-width, §23-434) and missing facts (survey/deed/zoning-lot description, the 10,075/10,076/10,387.99 area conflict, the 215 Place commercial-frontage question, elevations) leave the rear yard, the street-wall horizontal placement, and the "which lot area" choice NOT KNOWN or conditional.
Q8: Table above lists all 43 quantities with one basis each.

END-OF-REPORT
