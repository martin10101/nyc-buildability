# Independent reading for M5-T184 (reading A of option 3 (qualifying senior housing)) (provenance)

M5-T184 PROVENANCE -21 (OPTION 3, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: each reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and some readers read official Zoning Resolution pages live; each reader B was additionally told not to read any return- file; the comparer read both readings and opened captures and official pages. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was not an offline reading. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies. It is reproduced below unchanged, byte for byte. A value is recorded in the benchmark-options-2-3-6-7 reference case for option 3 only where this reading and its paired reading (return-independent-hand-calculation-21.md and return-independent-hand-calculation-22.md) give the same answer on the same basis, confirmed by the independent comparer (return-independent-hand-calculation-25.md).

---

I now have everything needed from the law text, the settled cases, and the evidence records. All values below are worked independently from the captured ZR text and the recorded lot facts — no program output was read.

---

**SEALED WORKED EXAMPLE — Option 3, "Qualifying senior housing"**
215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070); R6B with a C2-2 overlay; corner lot.

Unreviewed AI draft (ADR-007); not a professional determination and not an eligibility determination. Whether the building IS qualifying senior housing is a legal determination the program does not make; every figure below is worked **on the assumption that it qualifies**. Every lot-area figure uses the **recorded** area 10,075 sq ft (city record, NB-04); the 10,387.99 sq ft city-map-outline area is a drawing measure and never enters a zoning calculation — the two bases are never mixed.

**Worked values (recorded-area basis, zoning-lot and qualification conditional)**

| Item | Value | Unit | Basis | ZR section | State | Key conditions |
|---|---|---|---|---|---|---|
| Max residential FAR (qualifying) | 2.40 | ratio | law | 23-22 R6B 2nd col | applies | flat for R6B (no footnote → no wide-street test) |
| Max residential floor area | 24,180 | sq ft | derived | 23-22 (× lot area) | applies | zoning lot (NB-01), recorded-area basis (NB-04), qualifies |
| Minimum base height | 30 | ft | law | 23-432 R6B | applies | same as standard |
| Max base height (qualifying) | 45 | ft | law | 23-432 R6B qual. col | applies | identical to standard 45 |
| Max building height (qualifying) | 65 | ft | law | 23-432 R6B qual. col | applies | +10 ft over standard 55 |
| Dwelling-unit factor | none | — | law | 23-52(a)(2) | applies | qualifies; 23-52 sets no numeric unit limit |
| AIRS accessory social/welfare space | ≥4% of total floor area | — | law | 12-10 AIRS def. | applies (AIRS path) | counts within the residential floor area |
| Side yards | none required | — | law | 23-335(b); 34-232 (overlay) | applies | ≥5 ft if any open side strip provided |
| Setback above max base height | 10 (wide) / 15 (narrow) | ft | law | 23-433 | applies only >45 ft | Northern Blvd wide, 215 Pl narrow; 23-433(c) exceptions |
| Street-wall location | ≥70% within 8 ft of each street line | ft | law | 35-631(b) via overlay / 23-431 | conditional | prevailing-frontage + operative street line (NB-06) |
| Lot coverage / rear yard / street-wall / side yard | unchanged from option 1 | — | law | 23-362/363; 23-344(a); 35-631(b)/23-431; 23-335 | — | corner waiver within 100 ft; beyond not known |

**Arithmetic (independent, from the law text)**
- Max residential floor area = 2.40 × 10,075 = **24,180 sq ft** (23-22 R6B qualifying column; the R6B qualifying cell carries no footnote, so it does not depend on wide-street proximity — unlike the R6 3.90 row).
- Heights: read directly from the 23-432 R6B row — single minimum base height 30 ft (spans the row); qualifying column max base 45 ft, max building 65 ft. No R6B footnote, so street width does not change them.
- Dwelling units: 23-52(a)(2) places **qualifying senior housing** in the no-factor list, so the 680 divisor does **not** apply; 23-52 produces **no numeric dwelling-unit limit**. The unit count is then governed by the physical floor area and dwelling-unit standards, not by 23-52. (Both independent settled readings in `step-p4-worked.json#…-dwelling-unit-factor` and the library confirm "no applicable factor" for senior.)

**Definitions — what qualifying senior housing requires (capture state)**
"Qualifying senior housing" (zr-12-10-qualifying-senior-housing, captured) = (a) an **affordable independent residence for seniors** (AIRS) or (b) a **long-term care facility** (LTCF).
- **AIRS** (zr-12-10-affordable-independent-residence-for-seniors, captured 2026-10-14): ≥90% of the AIRS dwelling units each occupied by ≥1 person aged 62+; except a super's unit, all AIRS units restricted under an **affordable housing regulatory agreement** for households ≤60% of the **income index**, class A occupancy (NYS MDL); ≥4% of total floor area for accessory social/welfare facilities; the C/O must state AIRS use. "Super's unit", "affordable housing regulatory agreement" and "income index" are defined in §27-111 — **NOT CAPTURED**.
- **LTCF** (zr-12-10-long-term-care-facility, captured 2026-10-14): a community-facility use with NYS Department of Health certificate of authority/licensure — nursing homes/assisted living, or continuing-care retirement communities meeting a life-care-contract condition and having fewer independent-living units than assisted-living + nursing-home beds. For bulk, an LTCF uses the residential bulk of qualifying senior housing, and "dwelling unit" then includes HMC "rooming units".

**What the option adds versus option 1 (standard residences)**
| | Option 1 (standard) | Option 3 (senior) | Added |
|---|---|---|---|
| FAR / max residential FA | 2.00 / 20,150 sq ft | 2.40 / 24,180 sq ft | +0.40 FAR, **+4,030 sq ft (+20%)** |
| Heights (min base / max base / max bldg) | 30 / 45 / 55 ft | 30 / 45 / 65 ft | **max building +10 ft** only; base heights unchanged |
| 23-52 unit limit | 29 units (20,150 ÷ 680 = 29.63, fraction <0.75 dropped) | **no 23-52 limit** (no factor) | the 680-per-unit cap is removed |

The option adds floor area, 10 ft of building height (above the 45-ft base), and removes the 23-52 unit cap, in exchange for the senior-housing program conditions above. The envelope rules themselves (street-wall location, side yards, lot coverage, rear yard, the 23-433 setback rule, the 30-ft minimum base and 45-ft maximum base) are the same as option 1; the setback is merely now reachable because the building may exceed 45 ft.

**What is not known (exact missing item → official source)**
1. **That the building qualifies** (assumed here): AIRS needs an executed affordable housing regulatory agreement and HPD permit notice (HPD); an LTCF needs NYS DOH licensure. Not decided by the program.
2. **The zoning lot** (NB-01, access_blocked): the 2022 CERT 2022020201551001, ZONE 2022020201551002 and DECL 2022031600431001 are indexed against lots 1 and 70 but their contents are unread. → ACRIS recorded-document images / a title and zoning-lot review. If the zoning lot is lots 1+70 (~20,000 sq ft), every FAR/floor-area figure roughly doubles.
3. **Lot-area basis conflict** (NB-04, conflicting_evidence): recorded 10,075 vs GIS 10,387.99 sq ft (≈3.1%). → the Christopher M. Buckley survey of 2017-02-21 (named in DOF transaction 76338) or the 2018 deed 2018013000919001 Schedule A.
4. **§27-111 sub-terms** (super's unit, regulatory agreement, income index) — NOT CAPTURED. → ZR §27-111 (official portal).
5. Street-wall position / prevailing-frontage / operative street line (NB-06) — conditional, same as option 1.

**Conflicts between captures, settled cases and the library**
- The library file `option-02-03-affordable-and-senior-housing.md` lists the two senior sub-terms and Appendix F as **NOT CAPTURED**; both senior sub-terms (M3-T008, 2026-10-14) and Appendix F are now captured in the snapshot folder. The library is **stale on this point**; Article II Chapter 7 (27-111/27-131/27-133/27-14/27-151) remains genuinely not captured. §23-154 stays access-blocked (HTTP 403) but is not load-bearing for senior housing (it is the UAP Offsite Option).
- The captured snapshot_id uses the official **singular** term "affordable independent residence for seniors"; the library text uses the plural — cosmetic, not substantive.
- `real-lot.json` row L7 shows "35 units" = 24,180 ÷ 680 for **qualifying affordable** housing (option 2, where the 680 factor still applies to the higher FAR). This is **not** the senior count: for senior housing (option 3) 23-52 imposes no factor and no cap. The 35 figure must not be carried into option 3.

**What I checked / could not check**
Checked against primary captured text: 23-22 R6B rows (standard 2.00, qualifying 2.40, no R6B footnote); 23-432 R6B row (30/45/55 standard, 45/65 qualifying, no footnote); 23-52(a)(2) no-factor for senior and (b) 680/0.75 rule; the two senior sub-term definitions; the settled readings (real-lot, step-p4) and the evidence records NB-01/02/04/05/06. Could not check: the zoning-lot instruments' contents (access_blocked), the 2017 survey/deed (not published), the §27-111 sub-terms (not captured), and §23-154 (HTTP 403). Every unresolved input stays unresolved in the figures above.

END-OF-REPORT