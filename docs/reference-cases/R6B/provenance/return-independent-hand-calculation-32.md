# Independent reading for M5-T186 (option 4 (more, smaller apartments), reading A) (provenance)

M5-T186 PROVENANCE -32 (OPTION 4, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader read only the law snapshots, the NB evidence records, the settled R6B cases and the law library, and read no program output, fixtures, API, report or owner-docs. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names the pinned, read-only set of law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library that the reader worked from - it was not a sealed folder in the step-P7/P8 sense, and the header does not assert the reader was cut off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte.

---

# Sealed worked-example return — Option 4 "More, smaller apartments" (reader-A)

I am an AI agent. This is an unreviewed draft (ADR-007), not a professional zoning determination; it decides no eligibility or use permission an agency must grant. I read only the law snapshots, the NB evidence records, the settled R6B cases, and the library — no program output, fixtures, API, report, or owner-docs. Lot: 215-16 Northern Blvd, Queens, block 7334 lot 70, BBL 4073340070, R6B + C2-2 overlay, corner. All figures on the **recorded** area 10,075 sq ft (administrative record); the GIS outline 10,387.99 sq ft is a different basis and is never mixed in.

## Worked values

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Recorded lot area | 10,075 | sq ft | administrative record (PLUTO 26v2 / DOF) | — (not ZR) | applies | conflicts with GIS 10,387.99 (+3.11%); use recorded |
| Base residential FAR | 2.0 | ratio | settled (option 1) | 23-22 | applies | standard multiple dwelling |
| Max residential floor area (dividend) | 20,150 | sq ft | derived 2.0 × 10,075 | 23-22 + 23-52 opening | applies | zoning lot = lot 70 alone (NB-01 unconfirmed) |
| Dwelling-unit factor | 680 | sq ft/unit | law | 23-52(b) | applies | removed only under 23-52(a) |
| No-factor: special density area | — | — | law | 23-52(a)(1) + 12-10 | not_applicable | Queens: not Manhattan Core (CD 1–8), SPDist1 null → not Downtown Brooklyn |
| No-factor: qualifying senior housing | — | — | law | 23-52(a)(2) | not_known | applicant/program fact, not a lot fact; eligibility is a legal determination not made here |
| No-factor: conversions | — | — | law | 23-52(a)(3) | not_applicable | new development, not a conversion |
| **Max dwelling units (standard)** | **29** | units | derived | 23-52(b) | applies | 20,150 / 680; rounding below |
| "Smaller apartments" exceeding 29 under the ZR | No | — | law | 23-52(b) | not_applicable (blocked) | factor caps the count regardless of unit size |
| Minimum dwelling-unit size (lower bound on "smaller") | — | sq ft | outside captured law | not ZR | not_known | MDL / NYC HMC / NYC Building Code — not captured here |

## Arithmetic

- **Count:** 20,150 / 680 = 29.6324. The fraction 0.63 is below 0.75, so it drops → **29 units** (23-52(b): "Fractions equal to or greater than three-quarters … shall be considered to be one dwelling unit"). This equals option 1 exactly.
- **Rounding boundaries:** 20,230 / 680 = 29.75 → 30; 20,400 / 680 = 30.00 → 30; 20,229 / 680 = 29.7485 → 29.
- **Basis warning (do not mix):** if the GIS outline were used, 10,387.99 × 2.0 = 20,775.98 / 680 = 30.55 → 30. The basis choice alone moves the count 29↔30. Work on the recorded area → 29.
- **Senior branch (23-52(a)(2)):** no factor → 23-52 sets **no** unit cap; the count is bounded only by the physical envelope and by minimum-unit-size law outside the ZR. Not computed.

## Can "smaller apartments" exceed the option-1 count?

**No — not under the Zoning Resolution, for an ordinary multiple dwelling.** 23-52 caps the maximum number of dwelling units at *floor area ÷ 680*. Making apartments physically smaller does not raise that ceiling; it only lowers the average size below the 680-sq-ft-per-unit implied by the factor. So option 4 yields the **same 29 units** as option 1 on this lot. The only ZR routes past 29 are the 23-52(a) no-factor branches — and here (a)(1) special density area is **not_applicable** (Queens, NB-05) and (a)(3) conversions is **not_applicable** (new build); only (a)(2) **qualifying senior housing** removes the factor, but that is option 3 and turns on an eligibility determination this program does not make. Separately, **more floor area** (not smaller units) could raise the count — option 2's UAP/affordable 2.40 FAR gives 10,075 × 2.40 = 24,180 / 680 = 35.56 → 35 units (settled in the benchmark). That is option 2's path, not option 4's.

**What bounds unit size — outside this program's captured law** (name only, not computed): NYS Multiple Dwelling Law (minimum living-room/dwelling-unit dimensions, light/air); NYC Housing Maintenance Code (Admin Code Title 27, ch. 2); NYC Building Code / Construction Codes (minimum habitable-room area and ceiling height, egress). None is captured in `zr-snapshots/v1`; each is a statutory/code floor on how small a lawful unit can be, not a ZR value.

**What option 4 adds / costs vs option 1:** it adds **no legal units** (29 = 29). It is a design/estimate layer — a smaller target average unit size under the same 23-52 ceiling. Its "cost" is that the "more apartments" idea is legally blocked by the 680 factor unless the program changes (senior → no factor) or floor area rises (affordable FAR). A realistic small-unit *estimate* is an estimate, not law (library: `preliminary_apartment_estimate.py`; option 4 "cannot be shown before that estimate is built").

## Inputs a realistic small-unit estimate needs (named, not computed)

1. Max residential floor area permitted on the zoning lot (the dividend) — depends on FAR, lot-area basis, overlay, and zoning-lot scope.
2. The 23-52 legal cap (29) — the ceiling the estimate must not exceed.
3. Factor applicability (680 vs none for senior housing).
4. Net-to-gross efficiency: corridor, stair, elevator, lobby, mechanical and wall deductions (ZR floor area is gross).
5. Target unit mix / average unit size (a design assumption).
6. Minimum dwelling-unit size from MDL / HMC / Building Code (external bound).
7. Envelope constraints that shape the floor plate: heights 30/45/55 (settled), setback, lot coverage (23-362), rear yard.
8. C2-2 ground-floor commercial reservation — retail at grade reduces residential floor area and ground-floor units.

## Not known, with the exact missing item and where to find it

- **Zoning-lot scope (load-bearing).** NB-01 is `access_blocked`; a ZONE description (CRFN 2022000059134) and DECL are indexed against **lots 1 and 70**, so the zoning lot is likely lots 1+70, not established. The whole 20,150/29 result assumes **lot 70 alone**. Missing item: the recorded Zoning Lot Description text. Where: ACRIS, that CRFN. If lots 1+70 are one zoning lot, dividend and count change entirely.
- **Lot-area basis conflict:** recorded 10,075 vs GIS 10,387.99 (3.11%). Where to settle: the named 2017 Buckley survey (DOF txn 76338, 2017-03-22).
- **R6B reach of 23-52:** the section lists R1–R12, not R6B; it reaches R6B via 11-25 suffix inheritance ("except as otherwise set forth") — a reading (open Q12), not an express naming.
- **Minimum unit size:** outside captured law (MDL/HMC/Building Code); not in the snapshots.
- **23-52 closing paragraph** (mixed factor applicability; shared floor area attributed proportionately) is not encoded — matters only for a mixed senior/market building.

## Conflicts between captures, settled cases and library

- **Captures vs captures:** recorded vs GIS lot area → 29 vs 30 if the basis is mixed (flagged; use recorded).
- **Capture vs settled/library:** none on the 680 reading — NB-05, the benchmark ("bounded at 29"), and the library agree. Library correctly notes the no-factor branch does not help this lot and that 23-51 excludes **rooming units** from density regs (relevant to options 9/N2 "shared housing" — an open owner question I do not decide; N1 option-8 meaning likewise untouched).
- **Checked but could not verify:** anything a program computes (no program output read). I verified the law text, the NB records' primary sources, the 680 arithmetic and its boundaries by hand.

END-OF-REPORT
