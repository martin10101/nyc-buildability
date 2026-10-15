# Independent reading for M5-T185 (option 5 (ground-floor shops with residences above), reading A) (provenance)

M5-T185 PROVENANCE -26 (OPTION 5, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and, for sections that were not among the captures at the time it read, it cross-checked the official Zoning Resolution page (zoningresolution.planning.nyc.gov) live. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was NOT an offline reading and does not assert the reader was sealed off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte. (Several sections the reading marked uncaptured when it was made - for example 23-51, 23-12, 23-371, 32-421, 33-26, 33-301, 22-12/22-121/22-122, 32-121, 54-311 - were captured afterwards by task M3-T010 and are now present in docs/research/zr-snapshots/v1; the reference case records a value only where both readings of the option agree on the same value and the same basis.)

---

I have everything needed. Writing the sealed worked-example report.

---

# Option 5 — Ground-floor shops with residences above (C2-2 overlay in R6B)
215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070). Recorded lot area **10,075 sq ft** (city administrative record, PLUTO); the MapPLUTO outline (10,387.99 sq ft) is a different basis and is NOT mixed into any figure below. Corner lot: Northern Boulevard (wide, 100 ft), 215 Place (narrow, 60 ft).

**Unreviewed AI draft (ADR-007); not a professional or legal determination.** It decides no use permission, eligibility, or compliance any agency must grant. Every "applies" below is conditional on the two unresolved inputs flagged in the table (the zoning lot, NB-01; and the overlay's mapped coverage of the lot).

## Worked values

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| Retail/service use permitted at grade | Use Group VI permitted in C2 | — | law text | 32-161 (UG VI general use allowances); C2 column | applies | Per-use "S"/special-permit notations in the 32-161 table; use program is a scenario input, not decided |
| Floors shops may occupy | ≤ 2 stories; none above a story with dwelling units | stories | law text | 32-421 (official, Last Amended 6/6/2024, NOT captured) | applies | Shops may share a story with residences only if no access between them at a DU level; UG VIII amusement barred on a 2nd story with DUs only if C2-2 is a "select commercial overlay" — **not known** |
| Commercial FAR (overlay, keyed to R6B) | 2.00 | FAR | 33-121 table, "R5D R6B" row, Column A | 33-12 → 33-121 | applies | Column A governs a lot with commercial+residential (para (a)) |
| Residential FAR | 2.00 (std); 2.40 if qualifying | FAR | 23-22 table, R6B row | 35-31 → 23-22 | applies | 2.40 needs a qualifying-affordable/senior determination (not made) |
| Combined whole-lot cap (do they stack?) | **No** — total ≤ greatest single-use FAR = 2.00 | FAR | 35-31; 23-20 same words | 35-31 | applies | Both uses share one 2.00 cap; commercial FA reduces residential FA. 2.40 if residential qualifies |
| Maximum total floor area | **20,150** (std) | sq ft | 2.00 × 10,075 (recorded) | 35-31/23-22 | applies | 24,180 sq ft if qualifying (2.40). On lots 1+70 as one zoning lot it changes — NB-01 |
| Shared floor area | attributed pro rata on (total FA − shared) | sq ft | 35-31 / 33-12 | 35-31 | applies | Worked example below |
| Dwelling units | 20,150 ÷ 680, less commercial share | units | 23-52(b) factor 680 | 23-52 | applies | Baseline (all-residential) = 29; commercial reduces it (below). No factor only for qualifying senior (23-52(a)) |
| Min base / max base / max building height | 30 / 45 / 55 (std); 65 bldg if qualifying | ft | 23-432 R6B row | 35-01→35-63→35-632(a)→23-432 | applies | **Unchanged vs option 1** |
| Setback above max base height | 10 (wide) / 15 (narrow) | ft | 23-433 | 35-632(a)→23-433 | applies | Only for a street wall above 45 ft; a 3-storey/30 ft building triggers none. Unchanged vs option 1 |
| Street-wall location | ≥70% within 8 ft of street line | — | 35-631(b) | 35-63→35-631 | applies | **Changed by overlay** from R6B line-up rule 23-431(a). Final line turns on a "prevailing street wall frontage" (not known) |
| Lot coverage | corner 100% / interior-through 80% | % | 23-362 (residential portion, via 35-21/35-22) | 35-21/35-22→23-362 | not_known (whole-lot) | Overlay adds no coverage rule; same per-portion reason as option 1 (lot reaches ~103.9 ft from 215 Place, beyond the 100-ft corner reach) |
| Residential rear yard (mixed bldg) | 20 ft; none within 100 ft of corner | ft | 23-342 + 23-344(a); 35-53 sets the level | 35-53/23-342/23-344(a) | not_known (beyond 100 ft) | Far corner is 144.6 ft from the corner point, so part lies beyond 100 ft (L12) |
| Commercial rear yard | 20 ft; none within 100 ft of corner | ft | 33-26 (Last Amended 6/6/2024) waived by 33-301 (12/15/1961) — both official, NOT captured | 33-26/33-301 | not_known (beyond 100 ft) | Same corner geometry; 33-27/33-28/33-30 exceptions not checked |
| Overlay coverage of the lot | whole vs partial (split lot) | — | 76-131 default 150 ft | 76-131 | **not_known** | Actual mapped overlay line not read; nothing assumed |
| Zoning lot | lot 70 alone vs lots 1+70 | — | recorded instruments | NB-01 | **not_known** | A ZONE instrument is indexed against lots 1 and 70; every lot-area figure assumes lot 70 alone |

## Arithmetic (recorded-area basis)
- Total floor-area cap: 2.00 × 10,075 = **20,150 sq ft** (24,180 if qualifying at 2.40).
- All-residential units (option-1 baseline): 20,150 ÷ 680 = 29.63 → **29** (fraction < 0.75 dropped). Qualifying: 24,180 ÷ 680 = 35.56 → **35**.
- Mixed building: residential floor area = 20,150 − commercial floor area (then dwelling units = that ÷ 680). Each ≈ 680 sq ft given to shops costs ≈ 1 dwelling unit.
- Shared-area attribution (settled made-up worked example, lot 10,000, shop 4,200, residential 15,900, shared 400): base = 20,500 − 400 = 20,100; commercial 400×(4,200/20,100)=83.58; residential 400×(15,900/20,100)=316.42 → commercial 4,283.58, residential 16,216.42. Both under their 2.00 caps (20,000 each here).

## What option 5 adds or costs vs option 1 (standard residences)
- **Adds:** as-of-right ground-floor local retail/service (UG VI), ≤ 2 stories, below the residences (32-161, 32-421).
- **Costs:** it buys **no extra floor area**. Residential 2.00 and commercial 2.00 share a single 2.00/20,150 sq ft cap (35-31), so every square foot of shops comes out of the residential 20,150 and lowers the ≈29-unit ceiling proportionally.
- **Unchanged:** FAR cap, heights (30/45/55), setback depths, lot coverage, the all-residential rear yard logic.
- **Changed:** the street-wall rule (23-431(a) line-up → 35-631(b) 70%-within-8 ft) — but this already holds for any building on this overlay lot (overlay-reading settled case). New consideration: a **commercial** rear yard (33-26, with the 33-301 corner waiver) parallel to the residential 23-344(a) waiver — not conflated.

## What is not known (exact missing item → where found)
1. **Zoning lot (NB-01):** whether lot 70 is the zoning lot or lots 1+70 are one. If 1+70, lot area ≈ 20,000 sq ft and every area-based figure above roughly doubles. Source: recorded 2016/2022 CERT/ZONE/DECL instruments + a title/zoning-lot review. (The filed NB job 440608941 shows 39,934 proposed sq ft ≈ 2.0 × 20,000 — consistent with a combined lot, but not read.)
2. **Overlay mapped coverage:** whole-lot vs partial (split lot). Source: DCP Zoning Map sheet / ZoLa / NYCO GIS vs the 76-131 150-ft default; 76-00/76-01 scaled-measurement rules not read.
3. **"Select commercial overlay"** status of C2-2 (32-421 UG VIII bar). Source: 12-10 definition (not captured).
4. **Qualifying-housing** determination (chooses 2.00/20,150 vs 2.40/24,180 and the unit ceiling). A legal eligibility fact the program does not decide.
5. **Prevailing street wall frontage** on each frontage (fixes the exact 35-631 street-wall line). Source: an adjacency survey.
6. **Operative street-line positions** (the 8-ft measure and any setback run from them, not from DCM mapped widths). Source: survey or approved plan.

## Conflicts noted
- **Lot area:** 10,075 sq ft (recorded) vs 10,387.99 sq ft (MapPLUTO outline) — ~3.1% apart; all figures here use the recorded 10,075 and say so (NB-04).
- **Captured vs settled vs library:** 32-421, 33-26, 33-301 are **NOT captured** — I read them live (official URLs below, Last Amended 6/6/2024, 6/6/2024, 12/15/1961). The step-P5 settled case left the commercial FAR and the whole-building cap "not known" only because Article III Ch. 3 was absent from that sealed folder; the captured 33-121 (R6B = 2.00) now resolves both to **2.00**, consistent with the library and with 35-31. No contradiction found between captures, settled cases, and the library; the library's correction (shops = 32-161 UG VI, not 32-131 UG III) matches the captured snapshots.
- Official URLs read live: 32-421 https://zoningresolution.planning.nyc.gov/article-iii/chapter-2/32-421 ; 33-26 https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-26 ; 33-301 https://zoningresolution.planning.nyc.gov/article-iii/chapter-3/33-301

## Checked / could not check
Checked (captured snapshots, verbatim): 33-12, 33-121 (R6B row 2.00/2.00/2.00), 35-01, 35-31, 35-32 (table stops at R5 — does **not** reach R6B), 23-22 (R6B 2.00/2.40), 23-432 (30/45/55; 45/65 qualifying), 23-433, 23-362, 23-52 (680), 35-21/35-22, 35-53, 35-63/35-631/35-632, 34-11/34-111, 23-342/23-344, 32-161; evidence records NB-01/02/04/05/06; settled cases real-lot (L1 20,150, L2 24,180, L5 lot-coverage not known, L6 29, L7 35, L12 rear yard not known), overlay-reading (overlay changes only street-wall rule for a residential building), step-p5-worked (mixed combination = greatest single-use FAR; shared attribution). Could not check (no program runs, per seal; and not captured): the live mapped overlay line, the 12-10 "select commercial overlay" / "prevailing street wall frontage" terms, 33-27/33-28/33-30 rear-yard exceptions, the operative street line — all left not_known.

END-OF-REPORT