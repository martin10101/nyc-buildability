# Independent reading for M5-T184 (reading B of option 3 (qualifying senior housing)) (provenance)

M5-T184 PROVENANCE -22 (OPTION 3, READING B)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: each reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and some readers read official Zoning Resolution pages live; each reader B was additionally told not to read any return- file; the comparer read both readings and opened captures and official pages. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was not an offline reading. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies. It is reproduced below unchanged, byte for byte. A value is recorded in the benchmark-options-2-3-6-7 reference case for option 3 only where this reading and its paired reading (return-independent-hand-calculation-21.md and return-independent-hand-calculation-22.md) give the same answer on the same basis, confirmed by the independent comparer (return-independent-hand-calculation-25.md).

---

I have read the law text, the five evidence records, the settled reference cases, the library files, and listed the snapshot set. Here is my sealed, independent reading.

---

**Reader B — worked example, Option 3 "Qualifying senior housing"**
215-16 Northern Boulevard, Queens (block 7334 lot 70), R6B + C2-2 overlay, corner lot. Unreviewed AI draft (ADR-007); decides no eligibility, use or legal step. Every figure is worked on the **recorded** lot area **10,075 sq ft** (PLUTO lotarea / city record), never the 10,387.99 sq ft city-map-outline area (NB-04). Assumptions stated per row.

**Worked values**

| Item | Value | Unit | Basis | ZR section | State | Key conditions |
|---|---|---|---|---|---|---|
| Max residential FAR | 2.40 | ratio | R6B 2nd column ("qualifying affordable/senior"); **no footnote** on R6B row | 23-22 | applies | senior-housing eligibility (legal determination, not made here) |
| Max residential floor area | 24,180 | sq ft | 2.40 × 10,075 sq ft recorded | 23-22 | applies | zoning lot unconfirmed (NB-01); recorded-area basis |
| Min base height | 30 | ft | R6B row (same as standard) | 23-432 | applies | measured from base plane |
| Max base height | 45 | ft | R6B qualifying col (= standard 45) | 23-432 | applies | base plane |
| Max building height | 65 | ft | R6B qualifying col (standard = 55) | 23-432 | applies | eligibility; base plane |
| Setback above 45 ft | 10 (wide) / 15 (narrow) | ft | from each street wall above max base height | 23-433 (via 23-432; overlay 35-632(a)) | applies only >45 ft | not triggered at/below 45 ft; runs from operative street line |
| Dwelling-unit factor | none | — | senior housing = no applicable factor | 23-52(a)(2) | applies | eligibility |
| Max dwelling units | not known | count | no factor → not set by the 23-52 division | 23-52(a)(2) | not_known | a different rule (not in captured text) would govern |
| Lot coverage | corner 100 / interior 80 (whole-lot not known) | % | unchanged from option 1 | 23-362 | applies (unchanged) | per-portion; corner rule only within 100 ft of each street line |
| Rear yard | none within 100 ft of corner; beyond not known | — | unchanged | 23-344(a); 23-342 | part not_known | building type + lot width needed |
| Side yard | not required (optional, ≥5 ft if provided) | — | unchanged | 23-335(b); overlay 34-232 | not_applicable (not required) | — |
| Street-wall location | ≥70% within 8 ft of each street line | — | unchanged by the housing program | 35-631(b) (overlay) | applies | prevailing-frontage test; street-line position |

**Arithmetic.** Floor area: 2.40 × 10,075 = **24,180 sq ft**. Heights read straight from the 23-432 R6B qualifying column: 30 / 45 / **65**. Dwelling units: 23-52 opening = max residential floor area ÷ factor, but 23-52(a)(2) gives qualifying senior housing **no** factor, so no number falls out (24,180 ÷ 680 = 35.56 would be the figure **only if** the 680 factor applied, which it does not for senior housing).

**Definitions the program requires (12-10).** "Qualifying senior housing" = (a) *affordable independent residence for seniors*, or (b) *long-term care facility*. AIRS: a building/portion with residences where ≥90% of the allocated dwelling units are each occupied by at least one person 62+, and (except a super's unit) all such units are restricted by an *affordable housing regulatory agreement* for households at/below 60% of the *income index* and used for Class A occupancy (NYS Multiple Dwelling Law); ≥4% of total floor area must go to accessory social/welfare facilities ("super's unit", "regulatory agreement", "income index" are defined in §27-111). LTCF: a community-facility use with NYS DOH licensure — nursing homes/assisted living, or continuing-care retirement communities meeting a life-care-contract test and a unit-count test; for bulk it uses the residential bulk of qualifying senior housing and is treated as residential. These are eligibility conditions / legal determinations — **not** decided here.

**Envelope items that do NOT change** vs option 1 (standard): minimum base height (30 ft), maximum base height (45 ft), lot coverage (23-362), rear yard (23-344/23-342), side yards, street-wall location, and the 10/15 ft setback depth. **Only three figures move** for senior vs standard: FAR 2.00→2.40, max building height 55→65 ft, and the DU factor 680→none.

**Comparison with option 1** (standard: FAR 2.0 → 20,150 sq ft; 30/45/55; 29 units @ 680): Option 3 adds +4,030 sq ft of floor area (+20%) and +10 ft of building height; its base height and base/envelope controls are identical; and it is **not** unit-capped by 23-52. Note: the 23-22 footnote-2 and 23-432 footnote-3 senior-specific "within 100 ft of a wide street" uplifts apply to R8–R12 rows only — **not** R6B (R6B carries no footnote), so Northern Boulevard being a wide street does not raise R6B figures.

**What is not known (missing item → where to find it).**
1. **Zoning lot** (NB-01): lot 70 may form one zoning lot with lot 1; every floor-area figure is conditional. Missing: the contents of CERT 2022020201551001, ZONE 2022020201551002, DECL 2022031600431001 → ACRIS document images / owner records request + title review.
2. **Senior-housing eligibility** (the whole option gate): executed regulatory agreement, 62+/60%-income/Class A (AIRS) or NYS DOH licensure (LTCF). Missing: applicant/agency facts → HPD and NYS DOH; not a zoning lookup.
3. **Senior DU count**: 23-52 sets none. Missing: whether any other provision caps units for no-factor housing → a density/unit-rule capture.
4. **Lot-area conflict** (NB-04): recorded 10,075 vs GIS 10,388 sq ft. Missing: Christopher M. Buckley survey (2017-02-21) or deed 2018013000919001 → owner/DOF.
5. **Height measurement datum**: 30/45/65 are measured from the base plane; definition captured (zr-12-10-base-plane) but not read here.

**Conflicts (captures vs settled cases vs library).**
- The library `option-02-03-affordable-and-senior-housing.md` marks **"affordable independent residences for seniors"** and **"long-term care facility"** as **NOT CAPTURED**; both are now captured (M3-T008, 2026-10-14). The library is **out of date**.
- It also marks §§27-111, 27-131, 27-133, 27-14, 27-151 (and 27-161/27-162) NOT CAPTURED; the snapshot set now contains all of them. **Out of date.**
- Term-name drift: library uses the plural "residences"; the official §12-10 article title and the capture are the **singular** "affordable independent residence for seniors" (renamed in M3-T008 rework).
- No value conflict: reference case `real-lot.md` rows L2/L4 (24,180 sq ft; 45/65 ft) and L8 (senior units "not known") agree with my reading; `overlay-reading.md` confirms the C2-2 overlay changes only the street-wall rule and leaves FAR, coverage, units, heights, setback and all-residential rear yard as plain R6B.

**Sections a capture task should add.**
- **ZR 23-63** (Required Recreation Space in Multi-family Buildings) — cited inside the AIRS definition (indoor recreation counts toward the 4% accessory allocation); **not captured** (listing has 23-62, not 23-63).
- A section (if any) governing the **maximum number of dwelling units for no-factor housing** — 23-52(a) removes the factor but states no cap; confirm whether any density rule binds senior units.
- External non-ZR references the definitions lean on (note, not ZR capture): NYS Multiple Dwelling Law "Class A", NYS Public Health Law (nursing home / assisted living), NYC Housing Maintenance Code "rooming units", NYS DOH licensure — these are eligibility inputs, not zoning calculations.
- Library refresh so §27-111 and both senior sub-terms show as captured.

Files read (read-only, /root/project/w-read-bb5c02b9): docs/research/zr-snapshots/v1/{zr-23-22, zr-23-432, zr-23-52, zr-12-10-qualifying-senior-housing, zr-12-10-affordable-independent-residence-for-seniors, zr-12-10-long-term-care-facility, zr-12-10-special-density-areas}.snapshot.json; docs/research/evidence-records/{NB-01,NB-02,NB-04,NB-05,NB-06}.json; docs/reference-cases/R6B/{real-lot.md, overlay-reading.md}; docs/zoning-law-library/options/option-02-03-affordable-and-senior-housing.md; services/api/app/drawings/report/options.py. I read no return-* file and no program output. I did not need the live ZR site (every load-bearing section is captured).

END-OF-REPORT