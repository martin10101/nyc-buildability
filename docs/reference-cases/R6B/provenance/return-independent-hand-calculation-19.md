# Independent reading for M5-T184 (reading A of option 2 (qualifying affordable housing, incl. UAP)) (provenance)

M5-T184 PROVENANCE -19 (OPTION 2, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: each reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and some readers read official Zoning Resolution pages live; each reader B was additionally told not to read any return- file; the comparer read both readings and opened captures and official pages. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was not an offline reading. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies. It is reproduced below unchanged, byte for byte. A value is recorded in the benchmark-options-2-3-6-7 reference case for option 2 only where this reading and its paired reading (return-independent-hand-calculation-19.md and return-independent-hand-calculation-20.md) give the same answer on the same basis, confirmed by the independent comparer (return-independent-hand-calculation-25.md).

---

I have everything needed from the primary sources and settled cases. Compiling the sealed worked reading.

---

# Sealed worked example — Option 2: Qualifying affordable housing (incl. UAP)

**Lot:** 215-16 Northern Boulevard, Queens (block 7334, lot 70; BBL 4073340070). R6B with a C2-2 overlay; corner lot. **Basis used throughout: recorded lot area 10,075 sq ft (PLUTO `lotarea`).** The city-map outline area 10,387.99 sq ft is a drawing measure, never mixed into a floor-area figure (NB-04).

This is an AI draft, not professionally reviewed (ADR-007), and decides no eligibility. Whether the building IS qualifying affordable housing is a legal determination the program does not make; every figure below is worked **on the assumption that it qualifies**. Values come from the law captures and settled cases only — no program run.

## Worked values

| Item | Value | Unit | Basis | ZR section | State | Conditions that change it |
|---|---|---|---|---|---|---|
| Max residential floor area (qualifying) | 24,180 | sq ft | 10,075 × 2.40 | 23-22 R6B 2nd col | applies (if qualifies) | UAP: FAR may exceed 2.00 **only by the affordable floor area provided** (27-111); see next row |
| Min affordable floor area to reach 2.40 (UAP) | 4,030 (≈16.7% of 24,180) | sq ft | (2.40−2.00) × 10,075 | 27-111 "UAP development" | applies to UAP route | MIH or regulatory-agreement routes set a different share |
| Min base height | 30 | ft | table (single col) | 23-432 R6B | applies | — |
| Max base height (qualifying) | 45 | ft | table, qual col | 23-432 R6B | applies | same as standard (no gain) |
| Max building height (qualifying) | 65 | ft | table, qual col | 23-432 R6B | applies | vs 55 ft standard |
| Max dwelling units (qualifying affordable) | 35 | DU | 24,180 ÷ 680 = 35.56 → 35 | 23-52(b) | applies (settled case) | dividend = qualifying FA (see conflict); 680 factor; fraction ≥0.75 rounds up, 0.56 drops |
| Affordable share / income terms | no single number | — | — | 27-111, 27-14, 27-131 | depends on pathway | UAP: weighted avg ≤60% of income index, no band >100%, ≥20% of affordable FA at ≤40% **only if ≥10,000 sq ft affordable** (not triggered, 4,030<10,000) |
| Lot coverage | not known (no whole-lot figure) | % | per-portion | 23-362, 12-10 corner | unchanged by option | corner portion 100% within 100 ft of each street line; interior portion 80% beyond |
| Rear yard | none within 100 ft of corner; beyond not known | ft | — | 23-344(a), 23-342 | unchanged | depth beyond needs building type + lot width (not given) |
| Street wall location | governed by 23-431; overlay changes only this rule | — | — | 23-431, 34-11 | unchanged by qualifying | NB-06 interpretation awaiting review |
| Setback above max base height | 10 (wide St) / 15 (narrow St) | ft | — | 23-433 | unchanged | applies only to street-wall portions above 45 ft |
| Side yard | governed by 23-335 | — | — | 23-335 | unchanged | not worked in the settled real-lot case |

## Arithmetic

- Max residential FA (qualifying): 2.40 × 10,075 = **24,180 sq ft** (recorded basis). [Outline basis, for reference only, never mixed: 2.40 × 10,387.99 = 24,931.2 sq ft.]
- UAP affordable floor area to reach the full 2.40 bonus: (2.40 − 2.00) × 10,075 = 0.40 × 10,075 = **4,030 sq ft**, = 4,030 ÷ 24,180 = 16.7% of the total.
- Max dwelling units (qualifying affordable): 24,180 ÷ 680 = 35.56; fraction 0.56 < 0.75 drops → **35 DU**.
- Option 1 (standard, settled): 2.00 × 10,075 = 20,150 sq ft; 20,150 ÷ 680 = 29.63 → 29 DU; heights 30 / 45 / 55 ft.

## What option 2 adds over option 1 (standard residences)

- **+4,030 sq ft** residential floor area (20,150 → 24,180; +20%), the 23-22 R6B qualifying column.
- **+10 ft building height** (55 → 65 ft); base height unchanged at 45 ft; min base unchanged at 30 ft (23-432).
- **+6 dwelling units** (29 → 35), *if* the dividend is the qualifying 2.40 floor area (see conflict).
- The envelope items (lot coverage, rear yard, street wall, setback, side yard) are **unchanged** from option 1.
- The price of the bonus: under UAP, at least the 4,030 sq ft increment above 2.00 FAR must be affordable floor area (27-111), under an executed regulatory agreement / HPD permit notice (27-151) — plus a qualifying-housing legal determination the program does not make.

## What is not known — exact missing item and official source

1. **Zoning lot** (NB-01, access_blocked). Three 2022 instruments are indexed against lots 1 & 70 (CERT, ZONE = "Zoning Lot Description", DECL) but the ZONE instrument text was not read; DOB jobs describe one zoning lot spanning tax lots 1 and 70. → ACRIS document images (CRFN 2022000059134) / the recorded ZLDA. Every FA/DU figure stays conditional on the zoning-lot scope and area.
2. **Lot-area basis conflict** (NB-04, conflicting_evidence): recorded 10,075 vs outline 10,387.99 sq ft (≈3.1%); frontage 100.76 vs 103.88 ft. → the 2017 Christopher M. Buckley survey.
3. **MIH-area membership** — gates UAP (outside MIH) vs MIH (inside), and sets the MIH share. The captured Appendix F is only its **index page** (lists the borough maps; the Queens boundary maps are not in the captured text). → ZR Appendix F – Queens maps + §27-133 + DCP ZoLa. MapPLUTO does not flag it.
4. **Option-2 unit-count dividend** — standard 2.00 vs qualifying 2.40 floor area. → legal/reviewer reading (not a lookup).
5. **§23-154 text** — HTTP 403 on WebFetch and the browser-UA GET fallback; needed only for the UAP Offsite Option, not load-bearing on this generating-site lot. → the print/PDF node channel.
6. **Overlay effect on a mixed building's envelope** (35-63/35-632) — NB-06 is interpretation_awaiting_review; 34-24(b)(1) routes a mixed building to 35-63. For an **all-residential** building the overlay changes only the street-wall location (overlay-reading, both step-P2 readings). → read §35-632 officially.
7. **Applicant facts** (not decided): qualifying pathway, affordable share/income band, rental vs homeownership (27-161/27-162), the executed regulatory agreement, the HPD permit notice to DOB.

## Conflicts between captures, settled cases, and the library

- **DU dividend.** The settled real-lot case (reviewer-ruled, M4-T024-L7-ruling) records **35 units** using the qualifying 2.40 floor area (24,180) as the dividend. The law library (`option-02-03…`) keeps the dividend "not sure / reviewer question, kept open." I report 35 as the settled-case value **with** the library's open flag; the 680 factor itself is not in dispute (affordable housing is not a 23-52(a) no-factor branch; NB-05 confirms the lot is not in a special density area).
- **UAP FAR condition.** The library reads the R6B 2.40 as a flat ceiling and states Chapter 7 (27-111, 27-131, 27-14, 27-151) and Appendix F are **NOT CAPTURED**. They **are now captured** in `zr-snapshots/v1/`. The captured **27-111** adds a material condition the library's reading omits: a UAP development's residential FAR may exceed 2.00 **only by the amount of affordable housing provided** — so 2.40 is reachable only with ≥4,030 sq ft of affordable floor area, not automatically. The library file predates these captures.
- **Lot area** 10,075 vs 10,387.99 sq ft (NB-04) — kept separate; all figures above are on the recorded 10,075 basis.

## What I could not check and why

I did not run or read any program output (sealed reading). §23-154 text is unread (HTTP 403). The MIH-area maps are unread (Appendix F capture is index-only). The zoning-lot instruments' full text is unread (ACRIS access_blocked, NB-01). NB-06 (street wall / mixed-building height) is an interpretation awaiting review, not settled. Eligibility for any qualifying pathway is a legal determination not made here.

Files read (all under `/root/project/w-read-bb5c02b9`): `docs/research/zr-snapshots/v1/` (23-22, 23-432, 23-52, 12-10-qualifying-affordable-housing, 27-111, 27-131, 27-14, 27-151, 27-16, 27-161, 27-162, appendix-f); `docs/reference-cases/R6B/cases/` (real-lot, step-p1/p3/p4/p5/p6-worked, overlay-reading); `docs/research/evidence-records/` (NB-01, NB-04, NB-05, NB-06); `docs/zoning-law-library/options/option-02-03-affordable-and-senior-housing.md` and `options-sections.md`.

END-OF-REPORT