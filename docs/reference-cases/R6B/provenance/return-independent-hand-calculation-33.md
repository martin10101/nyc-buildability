# Independent reading for M5-T186 (option 4 (more, smaller apartments), reading B) (provenance)

M5-T186 PROVENANCE -33 (OPTION 4, READING B)

What this is: an independent worked reading made on 2026-10-15 by a second AI helper that took no part in writing the program's rules. METHOD, stated exactly: every section it relied on was among the captures, so no Zoning Resolution website fetch was required; it read no program output. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names the pinned, read-only set of law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library that the reader worked from - it was not a sealed folder in the step-P7/P8 sense, and the header does not assert the reader was cut off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte.

---

I have all sources needed (every section is captured; no ZR website fetch required). Composing the sealed worked-example return.

---

SEALED WORKED-EXAMPLE READER-B — Option 4 "More, smaller apartments" — 215-16 Northern Boulevard, Queens (block 7334, lot 70), R6B with C2-2 overlay.

This is an AI reader's unreviewed draft (ADR-007), not a professional zoning determination; it decides no eligibility or use permission an agency must grant. Every figure below assumes lot 70 alone is the zoning lot — unconfirmed (NB-01, access_blocked; likely one zoning lot of tax lots 1 + 70, not established). All figures use the recorded lot area 10,075 sq ft; the GIS-outline area 10,387.99 sq ft is a different basis and is never mixed in (NB-04).

HEADLINE: Under the Zoning Resolution, "smaller apartments" cannot raise the unit count above option 1 at the same floor area. §23-52 sets the maximum number of dwelling units by dividing floor area by a fixed dwelling-unit factor (680 for R6B); that factor is a density control tied to floor area, not to unit size. Making units smaller does not add units. The count only rises if §23-52(a) removes the factor (senior housing / special density area / certain conversions), if rooming units are used (§23-51 excludes them from density), or if more floor area is permitted (a higher FAR, e.g. qualifying affordable/senior at 2.40) — none of which is "more units at the same floor area."

WORKED VALUES

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Recorded lot area | 10,075 | sq ft | city record / PLUTO 26v2 | 12-10 lot area; NB-04 | applies | lot 70 alone = zoning lot (NB-01 unconfirmed) |
| Max residential FAR, standard residences | 2.00 | ratio | law (table) | 23-22 | applies | R6B row |
| Max residential floor area, standard | 20,150 | sq ft | derived 10,075 × 2.00 | 23-22 + 23-52 opening | applies | zoning-lot scope; FAR max, not necessarily buildable |
| Dwelling-unit factor, ordinary multiple dwelling | 680 | sq ft/unit | law | 23-52(b) | applies | reaches R6B via 11-25 |
| Max dwelling units at 20,150 sq ft | 29 | units | derived 20,150 ÷ 680 | 23-52(b) | applies | rounding rule below |
| No-factor: special density areas | — | — | law + recorded geography | 23-52(a)(1); 12-10 | not_applicable | NB-05: lot not in Manhattan Core / Sp. Downtown Bklyn |
| No-factor: qualifying senior housing | — | — | law | 23-52(a)(2); 12-10 | not_known | if AIRS or long-term care facility (DOH licensure, an applicant fact) |
| No-factor: certain conversions | — | — | law | 23-52(a)(3) | not_known | NB job 440608941 is a new building (NB-02) → likely N/A |
| Max FAR, qualifying affordable OR senior | 2.40 | ratio | law (table) | 23-22 | not_known | depends on program qualifying |
| Max DUs if qualifying affordable, factor still applies | 35 | units | derived 24,180 ÷ 680 | 23-22 + 23-52(b) | not_known | affordable is NOT in 23-52(a); more floor area, not smaller units |
| Rooming units excluded from density regs | — | — | law | 23-51 | applies (as law) | owner N2 (shared housing) open — not decided |
| Minimum dwelling-unit size | — | — | outside captured law | HMC / Multiple Dwelling Law / Building Code | not_known | names the bound on unit size; not a ZR/computed value |

ARITHMETIC
- Standard: 10,075 × 2.00 = 20,150 sq ft. 20,150 ÷ 680 = 29.632. §23-52(b): a fraction "equal to or greater than three-quarters" (0.75) counts as one unit; 0.632 < 0.75, so round down → 29 units.
- Qualifying affordable (illustrative upper floor area, factor retained): 10,075 × 2.40 = 24,180 sq ft; 24,180 ÷ 680 = 35.559; 0.559 < 0.75 → 35 units.
- Do-not-use cross-check of the basis conflict: GIS-outline 10,387.99 × 2.00 = 20,775.98; ÷ 680 = 30.55 → 30. This is why NB-04's rule (recorded area only) matters; mixing bases would add a phantom unit.

CAN "SMALLER APARTMENTS" EXCEED OPTION 1 UNDER THE ZR? No. §23-52 opening: "the maximum number of #dwelling units# permitted shall be determined by dividing the maximum #residential# #floor area# permitted on the #zoning lot# by the applicable #dwelling unit# factor." The factor (680, §23-52(b)) is flat for all R6-R12 "other" multiple dwelling residences and is not reduced for small units. §23-52 has no per-district column and no small-unit exception; its only relief is the (a) no-factor branch. So at 20,150 sq ft the legal maximum is 29 units whether the units are large or small. Routes that genuinely raise the count are different options, not smaller units: (a)(2) qualifying senior housing removes the factor entirely (count then bounded by floor area, unit mix and other regs, not by 680); rooming/shared housing under §23-51 is outside the density regulations ("the provisions of this Section shall not apply to #rooming units#"; §54-311 attaches the factor only on conversion to dwelling units) — but owner question N2 (shared housing) is open and I do not decide it; and qualifying affordable/senior FAR 2.40 adds floor area (→ 35 for affordable), which is "more floor area," not "smaller units."

WHAT BOUNDS UNIT SIZE (outside this program's captured law): a minimum dwelling-unit floor area and minimum room dimensions live in the NYC Housing Maintenance Code and the NYS Multiple Dwelling Law, and light/air, egress, corridor and habitable-room standards in the NYC Building Code. These are named as outside the captured Zoning Resolution, not computed here. They set how small a unit may lawfully be; the ZR factor already caps how many units the floor area yields.

INPUTS A REALISTIC SMALL-UNIT ESTIMATE NEEDS (named, not computed; an estimate is not law): (1) the buildable residential floor area actually achievable after height (R6B 30/45/55), setback, yard and lot-coverage limits — may be below the 20,150 FAR maximum; (2) assumed average net unit area / unit mix (a visible, editable design assumption); (3) gross-to-net efficiency (circulation, stairs, elevators, mechanical, wall thickness); (4) the applicable §23-52 factor branch (680 vs no-factor) given program type; (5) whether rooming/shared units are used (changes density treatment per §23-51 — N2 open); (6) the outside-ZR minimum unit size (HMC/MDL/Building Code) as a floor on unit count. Note: for standard residences the estimate is capped above by 29 regardless of how small units are drawn.

COMPARISON WITH OPTION 1 (standard residences, settled: FAR 2.0 → 20,150 sq ft; heights 30/45/55; 29 units by the 680 factor). Option 4 adds nothing to the legal unit count for standard residences — it is the same 29 units, just a smaller-unit layout within them; what it "adds" is a design/marketing choice (more, smaller homes), what it "costs" is larger-unit flexibility, with no zoning gain. A real increase in units requires a different legal basis (senior no-factor housing, rooming/shared housing, or the 2.40 affordable/senior FAR → ~35 with the factor retained), which belong to options 2/3/9, not to "smaller apartments."

WHAT I COULD NOT CHECK / MISSING ITEMS
- Zoning-lot scope (NB-01, access_blocked): if tax lots 1 + 70 are one zoning lot, lot area and max floor area both rise and 29 changes. Missing item: the recorded ZONE/zoning-lot-description instrument text (read the deed/declaration, not the index entry). Keeps 29 conditional.
- Buildable (ZFA) vs FAR-maximum floor area: NB-02 shows filed proposed ZFA 39,934 sq ft and whether it includes the retained lot-1 building is unknown (searched_not_found) — I did not use it; 20,150 is the §23-22 FAR maximum for lot 70 alone, an upper bound, not an as-filed figure.
- Program type (standard / affordable / senior / conversion / shared): determines which §23-52 branch and which §23-22 FAR column apply; not an input I can decide.
- Owner questions N1 (option 8) and N2 (shared housing): open; not decided.

CONFLICTS between captures, settled cases and library: (1) lot-area basis conflict (NB-04): 10,075 recorded vs 10,387.99 GIS (3.11%); resolved by the project rule to use recorded area — I followed it. (2) No conflict between §23-52, §23-22, §12-10 and the library section 4/9; the library's own correction (rooming units are outside density per §23-51, §54-311) agrees with the captured §23-51 text. (3) §23-52's district list names R6 not R6B; reach to R6B is via §11-25 (a reading flagged for the reviewer in the snapshot), while §23-22 lists R6B expressly — consistent, but the §23-52→R6B link rests on §11-25, not an express naming.

END-OF-REPORT
