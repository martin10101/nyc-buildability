# Independent reading for M5-T186 (option 11 (all programs combined), reading A) (provenance)

M5-T186 PROVENANCE -35 (OPTION 11, READING A)

What this is: an independent worked reading made on 2026-10-15 by an AI helper that took no part in writing the program's rules. METHOD, stated exactly: the reader cross-checked every figure against the v1 snapshots, the settled step-P4/P5 and benchmark cases and the evidence records; no program run was read. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names the pinned, read-only set of law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library that the reader worked from - it was not a sealed folder in the step-P7/P8 sense, and the header does not assert the reader was cut off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte.

---

I have everything I need. All figures cross-checked against the snapshots (23-22, 23-432, 33-121, 24-11, 35-31, 35-632, 23-52), the settled step-P4/P5 readings, the benchmark options case, and evidence records NB-01/04/05/06. Here is my sealed reading.

---

**Sealed worked-example reader-A — Option 11 "All programs combined" — 215-16 Northern Boulevard (block 7334, lot 70), R6B + C2-2 overlay, corner lot.**

Unreviewed AI draft (ADR-007); not a professional or legal determination; decides no eligibility or use permission an agency must grant. Every figure worked on the **recorded** lot area **10,075 sq ft** (administrative_record, NB-04); the GIS outline 10,387.99 sq ft is display-only and never mixed in. This is a **tax-lot-70-only** reading; the zoning lot is unconfirmed (NB-01). No program run was read.

**Core law (settled, two readers agree, `step-p5#mixed-use-floor-area-combination`, `#shared-floor-area-rule`).** Under ZR 35-31 (and 23-20 in the same words, both captured; library last-amended 12/5/2024): each use keeps its own maximum FAR (residential → Art. II Ch. 3; commercial/CF → Art. III Ch. 3), and **the total of all FARs may not exceed the greatest FAR permitted for any single use on the zoning lot**, except where explicitly stated otherwise. Uses **share one envelope; they do not stack.** Shared floor area is attributed to each use pro-rata on a base of total floor area **less** the shared portion.

**Worked values**

| Item | Value | Unit | Basis | ZR § | State | Conditions |
|---|---|---|---|---|---|---|
| Single-use FAR: standard res | 2.00 | FAR | 23-22 R6B | applies | — |
| Single-use FAR: qualifying affordable/senior res | 2.40 | FAR | 23-22 R6B 2nd col | applies | legal eligibility determination (not made here) |
| Single-use FAR: commercial (C2-2) | 2.00 | FAR | 33-121 col A, R5D/R6B | applies | overlay must cover footprint (76-131 extent not read); UG VI use (32-161) |
| Single-use FAR: community facility | 2.00 | FAR | 24-11 R6B / 33-121 col B | applies | — |
| **Combination ceiling, no qualifying housing** | **2.00** | FAR | 35-31/23-20 | applies | greatest single use = 2.00 (all three = 2.00) |
| **Combination ceiling, with qualifying affordable OR senior** | **2.40** | FAR | 35-31; 23-22 2nd col | applies | qualifying residential raises the single shared ceiling |
| Max total FA, ceiling 2.00 | 20,150 | sq ft | 10,075 × 2.00 | 35-31 | applies | = option 1 total |
| **Max total FA, ceiling 2.40** | **24,180** | sq ft | 10,075 × 2.40 | 35-31 | applies | qualifying housing present |
| Split by use | not fixed | — | 35-31 | applies | design choice; each use ≤ own max, sum ≤ ceiling; shared FA pro-rata on (total − shared) |
| Max residential FA (qualifying) | ≤ 24,180 | sq ft | 23-22/35-31 | applies | less any commercial/CF FA taken from the same cap |
| Commercial / CF FA in the mix | ≤ 20,150 each | sq ft | 33-121/24-11 | conditional | but sum with residential ≤ ceiling; adds no total FA |
| Combined-building height, standard res | 30 / 45 / 55 | ft | 35-632(a)→23-432 R6B | applies | min base / max base / max bldg; 35-632(b) excluded (R6B has suffix) |
| Combined-building height, qualifying res | 30 / 45 / 65 | ft | 35-632(a)→23-432 R6B 2nd col | applies | residential qualifies |
| Setback above max base | 10 (wide) / 15 (narrow) | ft | 35-632(a)→23-433 | applies | portions above the 45-ft base; Northern Blvd wide, 215 Pl narrow (NB-06) |
| Street-wall location (overlay/mixed) | 70% within 8 ft (wide) / within 10 ft (narrow) | — | 35-631 | applies | overlay rule replaces the 23-431 line-up rule |
| DU, all-residential qualifying affordable | 35 | units | 24,180 / 680 | 23-52(b) | applies | mixing in commercial/CF lowers it |
| DU, standard residential alone | 29 | units | 20,150 / 680 | 23-52(b) | applies | = option 1 |
| DU, qualifying senior | not_known | — | 23-52(a)(2) | not_known | no DU factor; occupancy set outside ZR |
| Zoning lot | unconfirmed | — | 12-10 / NB-01 | not_known | lots 1+70 may be one ~20,000 sq ft zoning lot |

**Arithmetic.** 10,075 × 2.40 = 24,180 sq ft; 10,075 × 2.00 = 20,150 sq ft; qualifying-housing bonus = 24,180 − 20,150 = **+4,030 sq ft**. Units: 24,180 / 680 = 35.56 → **35** (fraction < 0.75 dropped); 20,150 / 680 = 29.63 → **29**. These match the settled benchmark options (`benchmark-options-2-3-6-7.json`: opt2 24,180/35; opt6 "rises to 2.40 only if the residential use qualifies").

**Which programs may combine.** Residences + qualifying affordable (2) OR senior (3): raise the one shared ceiling to 2.40 (35-31; 23-22 2nd col; height 23-432 2nd col). Affordable vs senior are **alternatives** (same 2.40 column); whether one development may hold both is **not sure** (no ZR text read) and gives no stacking benefit either way. Residences + ground-floor shops (5): **may** (mixed building; 32-161 UG VI; 33-121 commercial 2.00 under the 35-31 cap) — conditional on the mapped overlay reaching the footprint. Residences + community facility (6): **may** (24-11 CF 2.00; 24-162 and 35-33 both exclude R6B, so no tightening; 24-163 higher residential coverage on a mixed level). Two buildings on one zoning lot (8, reading A.2): **may** — 35-01 extends the Chapter-5 cap across a zoning lot with residential + commercial/CF in multiple buildings; a district-boundary split (77-00) is not captured / not sure. Shared housing (9): **not sure** (use/density identified — 22-12/23-51/54-311 — but the City-of-Yes occupancy framework is pending 2027). Parking waiver (10): **may** combine with any (orthogonal to FAR; Outer Transit Zone is a recorded value).

**Decisive finding.** Because the standard-residential, commercial and CF single-use FARs are all 2.00, adding shops or a community facility **adds no total floor area** — they consume the same 35-31 envelope. The only program that raises the ceiling on this lot is qualifying affordable/senior housing (2.00 → 2.40). So the maximum total floor area for "all programs combined" is **24,180 sq ft** (greatest single-use 2.40), whether or not shops/CF are mixed in; mixing them in trades residential floor area (and units) for non-residential use under one cap.

**Vs option 1** (standard residences: 2.00 → 20,150 sq ft; 30/45/55; 29 units). The combination **adds** +4,030 sq ft of floor area (+20%), +10 ft of max building height (55 → 65), and, for affordable, +6 units (29 → 35) — all contingent on a qualifying-housing legal determination. For senior, the 680 factor is removed (unit count then not set by 23-52). It **costs**: the affordability/senior regulatory agreement and eligibility (not decided here); and shops/CF, if included, **cost** residential floor area and units rather than adding any. Base heights, setback, side yard and the corner rear-yard waiver (within 100 ft, 23-344(a)/24-391) are unchanged.

**What is not known (exact item → where).** (1) **Zoning lot** — ZONE/CERT/DECL instruments (CRFN 2022000059133 / 59134 / 121661) indexed against lots 1 **and** 70 suggest a single ~20,000 sq ft zoning lot; access_blocked (NB-01). If so, the 35-31/35-01 cap and lot 1's existing building apply across both lots, and every figure above (lot 70 alone) is not the zoning-lot figure → read the instruments on ACRIS. (2) **Overlay extent** on the lot (76-131 default 150 ft vs 100-ft depth) → DCP zoning map / survey; governs whether commercial FAR is reachable. (3) **Eligibility** for affordable/senior/UAP → legal determination the program does not make. (4) **Full 35-31 carve-out sweep** — only 35-32 (R1-R5 only) and 35-33 (R6 un-suffixed only) checked, both inapplicable to R6B → read 35-31 and neighbours in full. (5) **23-154 UAP** text → access-blocked (HTTP 403); Art. II Ch. 7 (27-111 etc.) captured. (6) **Shared housing** occupancy framework (pending 2027) and **split-lot meaning** → owner questions **N1/N2, not decided here**. (7) Lot coverage, rear-yard depth beyond 100 ft, affordable share %, MIH-area membership → not settled (benchmark cases).

**Conflicts.** Recorded area 10,075 vs GIS 10,387.99 sq ft (NB-04, ~3.11%) — never mixed; worked on recorded. No conflict found between the captures, the settled step-P4/P5 and benchmark cases, and the law library (option-11-combinations.md): all agree the ceiling is the greatest single-use FAR = 2.40 with qualifying housing, 2.00 otherwise. The library additionally notes current *program behavior* reduces option 11 to the single best qualifying-housing column (read-only context; not read as program output, and a product question for the owner, not a legal limit).

END-OF-REPORT
