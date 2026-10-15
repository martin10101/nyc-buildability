# Independent reading for M5-T184 (reading B of options 6 (residences with a community facility) and 7 (a community facility alone)) (provenance)

M5-T184 PROVENANCE -24 (OPTIONS 6-7, READING B)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: each reader had READ access to a detached, read-only checkout of this repository at commit bb5c02b9 (the law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library), was told not to read any program output (no test run, no API call, no report print and no benchmark fixture value), and some readers read official Zoning Resolution pages live; each reader B was additionally told not to read any return- file; the comparer read both readings and opened captures and official pages. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names that pinned, read-only set of captures and settled cases in the detached checkout at bb5c02b9 - it was NOT a sealed folder in the step-P7/P8 sense, and because some official pages were read live this was not an offline reading. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies. It is reproduced below unchanged, byte for byte. A value is recorded in the benchmark-options-2-3-6-7 reference case for options 6 and 7 only where this reading and its paired reading (return-independent-hand-calculation-23.md and return-independent-hand-calculation-24.md) give the same answer on the same basis, confirmed by the independent comparer (return-independent-hand-calculation-25.md).

---

I have independently worked the example from the law text and settled facts, verifying the uncaptured table values against the official ZR site. Here is my sealed reading.

---

# Reader B — worked example, options 6 & 7 (community facility), R6B + C2-2, 215-16 Northern Boulevard

**Unreviewed AI draft (ADR-007). Decides no eligibility, use permission or legal step. Every figure is worked by hand from the law text and the settled facts; no program output was read.**

**Basis used throughout:** recorded lot area **10,075 sq ft** (administrative record, tax lot 70 alone; NB-04). The GIS outline 10,387.99 sq ft is a different basis and is never mixed in. **Governing unknown (NB-01): the zoning lot is unconfirmed** — tax lots 1+70 may form one zoning lot (~20,000 sq ft). FAR, lot coverage, the combination ceiling and the unit count are all *per zoning lot*, so every derived figure below scales if the zoning lot is larger than lot 70.

## Worked values

| Item | Value | Unit | Basis | ZR section | State | Conditions |
|---|---|---|---|---|---|---|
| CF max FAR (opt 7, and CF part of opt 6) | 2.00 | FAR | R6B contextual CF table | 24-11; overlay 33-121 Col B = 2.00 | applies | per zoning lot |
| CF max floor area (opt 7) | 20,150 | sq ft | 2.00 × 10,075 (derived) | 24-11 | applies | zoning-lot scope unconfirmed |
| Combined max FAR (opt 6) | 2.00 | FAR | greatest single use = max(2.0 resid, 2.0 CF) | **24-161** (35-31 same words via overlay) | applies | no overlay/CF bonus in R6B |
| Combined max floor area (opt 6) | 20,150 | sq ft | derived | 24-161 | applies | split resid/CF is a design input |
| Residential FAR (opt 6) | 2.00 | FAR | underlying R6B | 23-22 via 34-111 | applies | — |
| CF lot coverage, corner | 80 | % | corner column | 24-11 | applies | corner lot (confirmed) |
| CF max footprint, corner | 8,060 | sq ft | 0.80 × 10,075 | 24-11 | applies | per level |
| Mixed-use lot coverage (opt 6) | 100 | % | higher of resid 100 / CF 80 on shared levels | **24-163** + 23-362 | applies | levels containing both uses |
| Dwelling units (opt 7) | 0 | units | no residences | — | applies | CF-only |
| Dwelling units (opt 6) | ≤29 | units | (resid FA)/680; 20,150/680 = 29.6→29 if CF=0 | 23-52(b) | applies | falls as CF floor area rises; not in special density area (NB-05) |
| Min base / max base / max bldg height | 30 / 45 / 55 | ft | R6B row | **24-04(b)(1) → 23-432** | applies | same chain as residences |
| Street wall location | at prevailing wall (else 70% within 8 ft wide / 10 ft narrow) | — | R6B | 23-431 | applies | 24-04 exempts UG III(B) houses of worship from 23-431(b) |
| Setback above base | 10 (wide) / 15 (narrow) | ft | — | 23-433 | applies | Northern Blvd wide, 215 Pl narrow (NB-06) |
| Front yard | none | — | R6 not listed | 24-34 | applies | — |
| Side yard | none required; ≥8 ft if provided | ft | R6-R12 | 24-35(b) | applies | vs 5 ft for residences (23-335) |
| Rear yard | 30 | ft | every rear lot line | 24-36 | applies | subject to 24-391 |
| Rear-yard corner waiver | none within 100 ft of ≤135° corner | — | corner | 24-391 | applies | corner lot |
| CF use permission | Use Group III | — | use groups | 22-13; overlay 32-131 | applies | which specific uses = **not_known** |
| 24-162 Column A/B CF reduction | — | — | R6B listed as exception | 24-162 | **not_applicable** | R6B excluded |
| 35-33 mixed-building CF tightening | — | — | suffixed district | 35-33 | **not_applicable** | applies only to R6 *without* a suffix |

## Arithmetic
- CF floor area (opt 7) = 2.00 × 10,075 = **20,150 sq ft**; max footprint = 0.80 × 10,075 = **8,060 sq ft** per level.
- Combined ceiling (opt 6) = greatest single-use FAR = max(2.00, 2.00) = **2.00** → 20,150 sq ft total. If CF takes C sq ft, residential ≤ 20,150 − C; units = ⌊(20,150 − C)/680⌋ (fractions ≥ ¾ round up). CF = 0 → 29.6 → **29**. There is no combining bonus here because both uses cap at 2.0.
- If the zoning lot is lots 1+70 (~20,000 sq ft), every FAR figure roughly doubles (e.g. CF floor area ≈ 40,000 sq ft) — kept unresolved.

## Comparison with option 1 (resid FAR 2.0 → 20,150 sq ft; 30/45/55; 29 units)
- **Total floor area: identical** (20,150 sq ft) — both uses cap at 2.0; different section (24-11/24-161 vs 23-22).
- **Height/setback envelope: identical** — 24-04(b)(1) routes the R6B CF building into the same 23-43 chain (30/45/55).
- **Lot coverage differs:** CF-alone (opt 7) 80% corner (24-11) vs residential **100%** corner (23-362); mixed (opt 6) returns to 100% on shared levels via 24-163.
- **Side open area:** CF ≥8 ft (24-35) vs residential ≥5 ft (23-335).
- **Dwelling units:** opt 7 = 0; opt 6 reduced by the CF floor area.
- **Use & rear-yard citation:** UG III (22-13/32-131) vs UG II; corner rear-yard waiver cited 24-391 (Ch 4) vs 23-344(a) (resid) — same effect. 24-33 additionally permits a 1-story (≤23 ft) CF accessory building in the rear yard *within* 100 ft of the wide street (Northern Blvd); not beyond it.

## What is not known (with the exact missing item and where to find it)
1. **Zoning-lot scope** (NB-01) — whether lot 70 stands alone or with lot 1. Missing: confirmation of the recorded ZLDA. Where: ACRIS CRFN 2022000059133 / …59134 / …121661; DOF zoning-lot records.
2. **Which UG III uses are as-of-right vs size-limited (22-132) vs special permit (22-134)** in R6B / the C2-2 overlay. Where: 22-131…22-135 (not individually captured), 32-131.
3. **Whether the CF has sleeping accommodations** (triggers 24-04(c)(3) allowances) and **whether it is a UG III(B) house of worship** (triggers the 23-431(b) street-wall exemption). These are scenario/use-program inputs, not lot facts.
4. **Opt 6 CF/residential split** — a design assumption that sets the unit count; left editable, not fixed.
5. **24-11 and 33-121 numeric table values** were read from the official site this session, not from a captured snapshot (see conflicts).

## Conflicts (captures vs settled cases vs library)
- **The library is stale on capture state.** `docs/zoning-law-library/options/option-06-07-community-facility.md` states "No zr-24-* snapshot exists, so every Article II Chapter 4 section is NOT CAPTURED." That is no longer true: `zr-24-04/-11/-111/-161/-162/-163/-33/-34/-35/-36/-391/-52/-522/-56` all exist in `docs/research/zr-snapshots/v1/` (captured under M3-T009 / DB-253). The library predates that capture.
- **Section text captured, table body not.** `zr-24-11` and `zr-33-121` have `table: null` — the FAR / lot-coverage numbers live only on the official page. I re-verified them directly (24-11 R6B = 2.00 / 80 / 60; 33-121 R5D-R6B Columns A/B/C all 2.00; both Last Amended 12/5/2024, HTTP 200).
- **R6B exclusions now confirmed from captured snapshots** (not just the library's WebFetch): `zr-24-162` lists R6B among the excepted districts; `zr-35-33` reads "without a letter suffix." Library and captures agree.
- **Area conflict** (NB-04): recorded 10,075 vs GIS 10,387.99 sq ft (~3.11%); I used recorded throughout.
- Settled cases (step-p5) and 24-161 agree on the greatest-single-use ceiling; no conflict.

## Sections a capture task should add
1. **Table bodies** for `zr-24-11` (R6-R12 contextual + non-contextual FAR / lot coverage) and `zr-33-121` (Columns A/B/C) — section text is captured but the numeric tables are null; these carry the load-bearing FARs.
2. **22-131…22-135** Use Group III use tables (CF use-permission precision).
3. Confirm the **23-432 structured R6B row** (30/45/55) is present in the snapshot table body.
4. Update the law-library option file to record that Article II Chapter 4 is now captured and that **24-161 directly supplies the R6B combination ceiling** (resolving its open question 1 for a residence-district reading; the overlay 35-31 gives the same number).

END-OF-REPORT