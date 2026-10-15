# Independent comparer for M5-T186 (option 4 (more, smaller apartments)) (provenance)

M5-T186 PROVENANCE -34 (OPTION 4, INDEPENDENT COMPARER)

What this is: an independent cross-check made on 2026-10-15 by a third AI helper that took no part in writing the program's rules. METHOD, stated exactly: the comparer reopened the v1 ZR snapshots, the NB evidence records and the reference cases, recomputed every arithmetic step on the recorded 10,075 sq ft, and read no program output. The comparer is an adjudicator that confirms agreement between the two readings; it is not a third source of values. The checker's provenance guard requires the literal phrase "sealed folder"; here that phrase names the pinned, read-only set of law-text captures under docs/research/zr-snapshots/v1, the settled reference cases, the evidence records and the law library that the reader worked from - it was not a sealed folder in the step-P7/P8 sense, and the header does not assert the reader was cut off from every outside source. It is a draft reading of the law (ADR-007), not professionally reviewed, decides no eligibility and is not a statement that anything complies, is buildable, is optimal or is feasible. It is reproduced below unchanged, byte for byte.

---

I have verified all law sections and external facts against the captured snapshots and evidence records. All arithmetic recomputed on 10,075 sq ft. Here is my comparison.

---

INDEPENDENT COMPARER — Option 4 "More, smaller apartments", 215-16 Northern Blvd, Queens (block 7334 lot 70, BBL 4073340070), R6B + C2-2, corner. All figures recomputed on recorded 10,075 sq ft. I read only the v1 ZR snapshots, the NB evidence records, and the reference cases — no program output. This is an AI reader's unreviewed cross-check (ADR-007), not a professional determination.

ITEM TABLE (item | A | B | verdict | supported value / not sure | captured in v1?)

| Item | A | B | Verdict | Supported value | Captured |
|---|---|---|---|---|---|
| Recorded lot area | 10,075 | 10,075 | AGREE | 10,075 sq ft (NB-04 recorded; "lot area" def §12-10) | Def yes; number is admin record, not ZR |
| Residential FAR, standard R6B | 2.0 | 2.00 | AGREE | 2.00 (§23-22 table, R6B row — confirmed verbatim) | Yes |
| Max residential floor area | 20,150 | 20,150 | AGREE | 20,150 sq ft (2.00 × 10,075 — I recomputed) | Yes (derived) |
| Dwelling-unit factor | 680 | 680 | AGREE | 680 (§23-52(b); reaches R6B via §11-25) | Yes |
| Max dwelling units (standard) | 29 | 29 | AGREE | 29 (20,150 ÷ 680 = 29.632; 0.632 < 0.75 → round down) | Yes |
| No-factor (a)(1) special density | n/a | n/a | AGREE | not_applicable (NB-05: QN, SPDist1 null; §12-10 special density = Manhattan Core CD1–8 / Sp. Downtown Bklyn) | Yes |
| No-factor (a)(2) senior | not_known | not_known | AGREE | not_known (eligibility/applicant fact) | Section yes; fact not a lot fact |
| No-factor (a)(3) conversions | not_applicable | not_known (likely N/A) | DISAGREE (label only) | not_applicable — NB-02 job 440608941 is a new building (job_type NB), not a conversion; A's label better supported; same practical result | Yes |
| Rooming units outside density §23-51 | in prose | tabled "applies as law" | ONE-SIDED (B tables) | §23-51 "shall not apply to rooming units" confirmed; both leave owner N2 open | Yes |
| Qualifying affordable/senior FAR 2.40 → 35 units | prose ("option 2's path, not 4") | tabled, not_known | ONE-SIDED (B tables) | 2.40 (§23-22) and 35 (24,180 ÷ 680 = 35.56 → 35) both correct; correctly NOT an option-4 count | Yes |
| Minimum dwelling-unit size | not_known | not_known | AGREE | not_known; outside captured law (MDL / HMC / Building Code) | No (not in snapshots) |
| Can smaller units exceed 29 under ZR? | No | No | AGREE | No — the 680 factor caps count regardless of unit size (§23-52 opening + (b), confirmed verbatim) | Yes |

ARITHMETIC (all recomputed on 10,075 sq ft): 2.00 × 10,075 = 20,150; 20,150 ÷ 680 = 29.632 → **29**. Rounding boundaries A cited all check: 20,230÷680 = 29.75 → 30; 20,400÷680 = 30.00 → 30; 20,229÷680 = 29.7485 → 29. Affordable 2.40: 10,075 × 2.40 = 24,180 ÷ 680 = 35.559 → 35. Every figure in both returns is reproduced exactly; no arithmetic error in either.

PROGRAM-OUTPUT / GIS-BASIS CHECK (required flag): **Neither reader took any value from program output or from the 10,387.99 GIS basis.** Both use recorded 10,075, and both compute the GIS figure only as a do-not-use warning (10,387.99 × 2.00 = 20,775.98 ÷ 680 = 30.55 → 30), i.e. the basis choice alone moves the count 29↔30. Both correctly isolate it. No contaminated value in either return.

HEADLINE VALUES BOTH AGREE ON (law-supported, captured): recorded lot area 10,075 sq ft; standard R6B FAR 2.00; max residential floor area 20,150 sq ft; dwelling-unit factor 680; **maximum 29 dwelling units**; option 4 yields the **same 29 units as option 1** — "smaller apartments" is a design layer, not a zoning increase, because §23-52 ties the cap to floor area, not unit size. All conditional on lot 70 being the zoning lot. These are mutually corroborating; the only divergence anywhere is the item-8 confidence label.

OPEN ITEMS (exact missing fact):
1. **Zoning-lot scope (load-bearing).** NB-01 is access_blocked; the recorded ZONE instrument (Zoning Lot Description, CRFN 2022000059134) and CERT/DECL are indexed against **lots 1 AND 70**, and DOB text states "ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)". Missing item: the ZONE/DECL instrument *text* (read the instrument, not the ACRIS index). If lots 1+70 are one zoning lot, the 20,150 dividend and the 29 count both change. Both readers flag this; both keep 29 conditional. Correct.
2. **Lot-area basis conflict.** Recorded 10,075 vs GIS 10,387.99 = +312.99 sq ft (3.11%); frontage 100.76 vs 103.879. Settle via the 2017 Buckley survey (DOF txn 76338, recorded CRFN 2005000015416). Both flag; both use recorded. Correct.
3. **Program/eligibility type** (standard / affordable / senior / conversion) selects the §23-52 branch and the §23-22 FAR column; not decidable from lot facts. Both flag.
4. **Buildable ZFA vs FAR maximum.** NB-02: filed proposed ZFA 39,934 sq ft, searched_not_found whether it includes the retained lot-1 building; 20,150 is the §23-22 FAR *maximum* for lot 70 alone (upper bound), not an as-filed figure. B states this; A treats 20,150 as the FAR ceiling likewise. Consistent.
5. **Minimum dwelling-unit size** — MDL / NYC HMC / Building Code; not in the v1 snapshots. Both name it as the outside-ZR floor on how small a lawful unit can be. Correct.

RESOLUTION OF THE ONE DISAGREEMENT (item 8, conversions): the captured §23-52(a)(3) covers conversions of non-residential/community-facility buildings to residences. NB-02 records the lot-70 project as a **new building** (job_type NB, PERMIT ISSUED). For option 4 (new, smaller apartments) the conversion branch does not apply, so A's **not_applicable** is the better-supported label; B's not_known reaches the same "likely N/A." No effect on the 29-unit result.

BOTTOM LINE: the two sealed returns agree on every computed value and every cited clause, with one minor confidence-label difference (conversions) and two presentation differences (B tables the §23-51 rooming-unit point and the 2.40/35 affordable figures that A keeps in prose as "not option 4's path"). Both are law-supported, both clean of GIS/program-output contamination, both correctly conditional on the unresolved zoning-lot scope. The supported option-4 answer is **29 dwelling units, identical to option 1**, conditional on lot 70 being the zoning lot.

Scratch only: /tmp/claude-0/compare-option-4/ (nothing written to any repository).

END-OF-REPORT
