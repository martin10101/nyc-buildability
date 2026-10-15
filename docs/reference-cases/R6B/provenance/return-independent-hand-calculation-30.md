# Independent reading for M5-T185 (options 9-10 (shared housing; parking and the transit zone), reading A) (provenance)

M5-T185 PROVENANCE -30 (OPTIONS 9-10, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

I have everything needed. Compiling the sealed worked-example return.

---

SEALED WORKED-EXAMPLE READER — OPTIONS 9 & 10 (shared housing; shared housing with the parking waiver)
215-16 Northern Boulevard, Queens (BBL 4073340070; block 7334, lot 70), R6B with a C2-2 overlay, corner lot.

This is an unreviewed AI draft (ADR-007), not a professional or legal determination. It decides no eligibility, grants no use permission, and authorizes no legal step. "Shared housing" is not a Zoning Resolution term; the ZR regulates it as rooming units. All figures work on the recorded lot area 10,075 sq ft (administrative record); the GIS outline 10,387.99 sq ft is display-only and never enters a zoning figure. The zoning lot is unconfirmed (the 2022 ZONE/CERT/DECL index lot 70 with lot 1 — NB-01), so every lot-area figure below is conditional on lot 70 alone being the zoning lot.

WORKED VALUES

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Lot area (zoning basis) | 10,075 | sq ft | administrative record (PLUTO/DOF) | 12-10 "lot area" | applies | zoning lot unconfirmed (may include lot 1, NB-01); GIS 10,387.99 display-only (NB-04) |
| Residential FAR (R6B std res.) | 2.0 | ratio | law (table) | 23-22 | applies | same for options 1/9/10 (rooming units are a residential use) |
| Max residential floor area | 20,150 | sq ft | derived (2.0 × 10,075) | 23-22; 12-10 FAR | applies | the only ZR quantity that caps a rooming-unit building |
| Use permission (rooming units in R6B) | permitted as-of-right (Use Group II) | — | unreviewed reading | 22-12/22-121; 22-122 (bar does NOT list R6B) | applies (draft; sections NOT captured) | C2-2 overlay adds only commercial UGs (32-121 permits residences) |
| Dwelling-unit factor for rooming units | none (680 does NOT apply) | — | unreviewed reading | 23-51 (excludes rooming units from 23-50); 23-52; 54-311 | applies (draft) | 23-51 verified on official site 12/5/2024 but NOT in repo captures; conflicts with library first pass + owner sample |
| ZR cap on rooming-unit count | none in ZR | units | law | 23-51/23-52 | not_applicable | bounded only by FAR (counted once, 23-51) and non-ZR room minima |
| Rooming-unit size minimum | not set by ZR | sq ft | law (hand-off) | 12-10 "rooming unit" → MDL "living room" | not_applicable (within ZR) | MDL §4 / HMC / Building Code govern; pending bills propose 100 (1 occ.)/150 (2) |
| Transit-zone membership | Outer Transit Zone | — | recorded value (ZoLa "Transit Zones Parking Geographies"; dataset 6ztr-wgff 2025-12-16) | 12-10 "Transit Zone, Outer" | recorded (not a legal determination); NOT Inner | Appendix I maps are images, not captured as text; text controls over ZoLa on conflict |
| Parking — rooming units (opt. 9 & 10) | 0 | spaces | law | 25-20 → 25-221 (Outer; created after 3/22/2016) | applies | automatic elimination, NOT a special permit |
| Parking — any standard dwelling units | 25% per std DU; waived if ≤15 (Column C) or lot width ≤25 ft (fn 3) | spaces | law (captured table) | 25-222 (R6/R7-1/R7-2 row: A 25, B 0, C 15) | applies to any DU portion | R6B reads the unsuffixed "R6" row (suffix.json; parking-specific clause not read) |
| Bicycle parking | 1 per 2 DU-equiv.; 3 rooming units = 1 DU; waived ≤10 DU | spaces | law | 25-80/25-811 | applies (per building) | per building/segment, not per zoning lot |
| Loading berths | none for residences | berths | law | 36-62 | not_applicable (residential) | C2-2 commercial uses would schedule separately |
| Heights (context, unchanged by 9/10) | base 30 min / 45 max; building 55 max | ft | law | 23-432/23-433 (R6B) | applies | interpretation_awaiting_review (NB-06) |

ARITHMETIC
- Max residential floor area: 2.0 × 10,075 = 20,150 sq ft (FAR definition, 12-10; lot area 10,075, NB-05/NB-04).
- Option 1 dwelling-unit count (dwelling-unit scenario only): 20,150 / 680 = 29.63 → fraction 0.63 < 0.75 → 29 units (23-52(b); NB-05). Boundary: 20,230/680 = 29.75 → 30; 20,400/680 = 30.0.
- Options 9/10, rooming-unit scenario: the 680 factor does not apply (23-51), so there is NO ZR unit ceiling; the floor-area cap stays 20,150 sq ft. Room count is set outside the ZR by MDL/HMC minimum room area.
- Option 10 parking for rooming units: 0 spaces (25-221). For any standard DU, required = DU × 25%, with no spaces required if the result ≤ 15 (Column C) or if the zoning lot existed 12/5/2024 with lot width ≤ 25 ft (fn 3). The lot's recorded frontages are 100.76 ft / 100 ft, so fn 3 does not reach it. No count is computed here.

WHAT OPTIONS 9/10 ADD OR COST vs OPTION 1 (standard residences: FAR 2.0 → 20,150 sq ft; 29 units; 30/45/55 ft)
- Same floor-area ceiling (20,150 sq ft) and same height envelope — rooming units are a residential use at the same R6B FAR and bulk.
- Adds: removal of the 680 dwelling-unit cap (potentially many more, smaller rooming units within the same 20,150 sq ft), and zero required parking in the Outer Transit Zone (25-221) versus option 1's dwelling-unit parking (25-222: 25% with the 15-space/lot-width waivers).
- Costs/limits: the per-room floor-area minimum is set by non-ZR law (MDL/HMC), and the modern shared-housing operating framework is NOT yet enacted (state S10497/A11136 in committee; city Intro 1475-2025; targeted 2027-01-01), so as of today a new shared-housing suite is not shown as lawfully occupiable as-of-right.
- Option 10 vs option 9: for a pure rooming-unit building they reach the SAME parking answer (0, by 25-221, not a discretionary waiver). Option 10's distinct meaning (shown with the parking requirement eliminated, vs a different housing programme) is a product question, not a law question (owner question N2, below).

WHAT IS NOT KNOWN (exact missing item → where it could be found)
1. Whether the proposal's units are rooming units or dwelling units — an applicant/program fact, not inferable; it gates both density (23-51 vs 23-52 680 factor) and parking (25-221 zero vs 25-222 25%). Keep unresolved.
2. The zoning lot — unconfirmed (NB-01, access_blocked): read CERT 2022020201551001, ZONE 2022020201551002, DECL 2022031600431001 (owner saves them from ACRIS, or a title/zoning-lot review).
3. Rooming-unit room-area minimum — outside the ZR: MDL §4 / HMC §27-2004 (HMC fetch was HTTP 403) / Building Code; and the pending 2027 bills.
4. Transit-zone membership from law alone — unsettled by captured text (Appendix I is image maps; ZoLa boundary; 66-11); the Outer value is a recorded dataset/ZoLa value only.
5. Suffix: that R6B is covered by the unsuffixed "R6" parking row — a parking-specific applicability clause was not read.

CONFLICTS (captures vs settled cases vs library)
- Density: the library's option-09 FIRST pass applied the 23-52 680 factor to rooming units via the 12-10 "dwelling unit" bridge clause; the corrected reading (DB-251) and my independent fetch of 23-51 ("the provisions of this Section shall not apply to rooming units", Last Amended 12/5/2024) say the density regulations do NOT apply to rooming units. Caveat: the literal referent of "this Section" is 23-51; two interpretive readings both reach "no DU factor for rooming units," reinforced by 54-311. This is an unreviewed draft, and 23-51 is NOT captured in the repo.
- Owner's sample (scenarios 7/8) counts SRO rooms as dwelling units for density and shows required/waived parking; the law as read excludes rooming units from density (23-51) and requires no parking for them in the Outer zone regardless of count (25-221). The sample's "trim rooms to hit a waiver" premise is the dwelling-unit path (25-222 Column C), not the rooming-unit rule. Carried to owner questions.
- Library wording (DB-258): option-10 says "Appendix I text controls on a conflict"; the captured 12-10 "Outer Transit Zone" says the textual description of the boundary controls over ZoLa. Option-09 dates Intro 1475-2025 to 2025-11-25 (Council record unconfirmed; its proposed, not-law status is right).

SECTIONS A CAPTURE TASK SHOULD ADD (source text only; DB-253)
- 23-51 (density applicability / rooming-unit carve-out) — load-bearing, verified live but NOT captured.
- 22-12 / 22-121 / 22-122 (Use Group II permission and the single-/two-family bar) and 32-121 (residences in C1/C2).
- 54-311 (rooming-unit conversion → dwelling-unit factor).
- 25-30 and following (community-facility parking in the residence district).
- 12-10 "Transit Zone, Inner"; 25-24/25-241 (general-rule completeness).
- Appendix I: note it cannot be captured as text (image maps), so the transit zone stays a recorded value.
(Captured and confirmed this pass: 25-20, 25-211, 25-221, 25-222 incl. the R6 Column A/B/C table, 12-10 rooming-unit, dwelling-unit, Transit Zone Outer/Greater, 23-22, 23-52.)

OWNER QUESTION (do not decide): N2 / DB-255 — how options 9 and 10 are shown while the shared-housing operating framework is unenacted, and whether option 10 differs from option 9 only by showing the parking requirement eliminated or by a different housing programme. Worked, not decided, here.

END-OF-REPORT