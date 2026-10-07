# M4-T032 producer report - the independent reading of ZR 34-22, 34-23 and the other newly captured text, written into the R6B reference cases

Producer: rules-engineer (builder), isolated worktree. Reset to the claim-seam head
`5f8b78ce452b4a214cceeb314372f6968373acf6` before starting. One commit; no ledger/push/accept.

This is an AI agent's build from two AI readings. Two readings that agree are not proof, and nothing
here is a professional or legal determination or a statement that any lot complies.

## Source for every new value

Only the two independent readings, each made by a different AI helper from a sealed folder (all 110
pinned law captures, the benchmark lot's recorded official facts and outline, two made-up lots), with
no program, repository or web:
- `return-reading-P4-1.txt` -> saved as `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-9.md` ("reading 9")
- `return-reading-P4-2.txt` -> saved as `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-10.md` ("reading 10")

Both saved byte-for-byte below a short header; the body below the `---` header equals the source txt
byte-for-byte (verified: 44,101 and 45,358 body bytes). Whole-file digests pinned in
`r6b_reference_cases_step_p4.py` (`STEP_P4_READINGS`), markers "ONE HARD RULE" (-9) and "one hard rule"
(-10):
- -9 sha256 `d49c8bf2344a285b034226bf167fe8d928f8d82d092b990d57e46d644aff579f`
- -10 sha256 `d46fd0e7b75b6751a1b63f1101d75ef7983c0a9ba159209ccecc5588463eb4d9`

## Files written

- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-9.md` (new, the saved reading 9)
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-10.md` (new, the saved reading 10)
- `docs/reference-cases/R6B/cases/step-p4-worked.json` (new case, 23 rows)
- `docs/reference-cases/R6B/step-p4-worked.md` (new, rendered from the data)
- `docs/reference-cases/R6B/cases/overlay-reading.json` (3 `superseded_by` markers + 1 change-log entry)
- `docs/reference-cases/R6B/overlay-reading.md` (re-rendered)
- `docs/reference-cases/R6B/README.md` (case table + provenance line + a step-P4 section)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_step_p4.py` (new focused module: digests, reading stems, must-stay-not-known rows)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_check.py` (wire step-P4 in: CASE_READINGS, label, READINGS_DIFFER, must-stay-not-known, provenance digest check)
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (CASE_IDS + REQUIRED_BASE_IDS for step-p4-worked)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases.py` (CASE_IDS tuple; overlay settled test split for the 3 superseded rows; NOT_KNOWN adds step-p4 rows)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases_round2.py` (SUPERSEDED adds the 3 overlay->step-p4 links)
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p4.py` (new focused test module, 7 tests + 2 mutation proofs)
- this report

Every changed path is inside `docs/reference-cases/R6B/**`,
`services/api/tests/rules/reference_cases/**` or the producer report. No rule file, engine, capture,
register, plan, measurement-basis record or other test changed.

## The 23 new rows (step-p4-worked.json)

A value or yes/no is recorded only where BOTH readings give it on the same basis; otherwise "not known"
with both named; where one reading holds a condition, it is said in the value naming that reading.

1. `zr-34-22-sections` (value) - what each of 34-221 to 34-224 does: 34-221 keeps the Article II Ch 3 FAR; 34-222 change-of-use only; 34-223/224 bonuses exclude C2-2; none changes the FAR for a new all-residential C2-2-in-R6B building. Both, Q1.
2. `zr-34-23-sections` (value) - 34-231 no front yard, 34-232 no side yard, 34-233 change-of-use; none speaks of the rear yard. Both, Q2.
3. `floor-area-ratio` (value) - same as plain R6B (2.00 standard); condition of the overlay reading (subject to ZR 34-21 to 34-23) resolved. Both, Q1/Q3. **Supersedes overlay#floor-area-ratio.**
4. `lot-coverage` (value) - same as plain R6B (ZR 23-362); no overlay text states a coverage rule. Both, Q3. **Supersedes overlay#lot-coverage.**
5. `rear-yard` (value) - same as plain R6B; 35-53 reaches only a mixed building; carries reading 9's completeness caveat (full ZR 34-23 sub-section list not confirmed) that reading 10 does not. Both, Q2/Q3. **Supersedes overlay#rear-yard.**
6. `overlay-text-on-lot-coverage` (value) - no: no captured Chapter-4 overlay text uses "lot coverage". Both, Q3.
7. `zr-35-sections` (value) - only 35-63 reaches (height/setback via 34-24(b)(1)); 35-62/641/642 no; 35-22 reaches the bulk in substance, its governing chapter not known; 35-643(a) not known (no transportation-adjacent frontage fact). Both, Q4.
8. `mixed-building-definition` (value). Both, Q4.
9. `lot-coverage-definition` (value) - counts the above-view footprint; the two exclusion sets. Both, Q5.
10. `yard-definitions` (value) - the five yard definitions. Both, Q5.
11. `rear-yard-obstructions` (value) - the 23-341 + 23-311 + 23-312 list, applied to nothing; 23-341(b)(3) barred in R6B. Both, Q5.
12. `street-wall-definitions` (value) - street wall, curb level, prevailing street wall frontage. Both, Q6.
13. `real-lot-prevailing-frontage` (**not known**) - needs neighbouring-building street-wall data, absent. Both, Q6.
14. `large-site` (value) - 1.5 acres = 65,340 sq ft; neither the real lot (~10,075/10,388) nor the made-up 100x100 (10,000) is one. Both, Q7. Arithmetic: 1.5 x 43,560 = 65,340.
15. `qualifying-residential-site` (value) - no: every branch needs an R1-R5 setting; R6B lot is not one. Both, Q7.
16. `zr-34-111-exceptions` (value) - no: neither (a) nor (b) reaches C2-2 in R6B; cross-references the step-P3 governs row for which-section-governs. Both, Q7.
17. `dwelling-unit-and-qualifying-housing-definitions` (value). Both, Q8.
18. `dwelling-unit-factors` (value) - 680 standard, 680 qualifying affordable, no factor qualifying senior, no factor in special density areas. Both, Q8.
19. `made-up-100x100-units` (value, conditional) - 29 units; condition both attach: the floor-area-ratio definition was not in the folder (strictly, not known). Arithmetic: 2.00 x 10,000 = 20,000; 20,000 / 680 = 29.41 -> 29. Both, Q8.
20. `zr-23-441-reach` (value) - no: R9D/R10X or R9/R10-no-suffix only; deciding fact = district (R6B); (c) park-clause moot. Both, Q9.
21. `zr-23-442-reach` (value) - no: Manhattan/Brooklyn CDs only; deciding fact = Queens CD 11. Both, Q9.
22. `zr-23-443-reach` (**not known**) - (a)/(b)/(d) not known (park, transportation frontage, adjacent R1-R5 boundary); (c) the two readings differ. Both named.
23. `sections-and-facts-not-had` (value) - the agreed "did not have" list, what stays not known, the one-reading-only differences, and each reading's separate not-read list.

## Point 4 - one current answer per question; candidates decided

- **overlay#floor-area-ratio** -> superseded_by `step-p4-worked#floor-area-ratio`. The overlay row held "same as plain R6B" subject to ZR 34-21 through 34-23; step P4 read 34-22 (and 34-21, 34-23) and both readings find no change, so the step-P4 row holds the current answer.
- **overlay#lot-coverage** -> superseded_by `step-p4-worked#lot-coverage`. Same reasoning; both readings find no overlay text speaks of lot coverage.
- **overlay#rear-yard** -> superseded_by `step-p4-worked#rear-yard`. Same reasoning; both readings find no 34-23 section modifies the rear yard (reading 9 with a completeness caveat).
- **overlay#not-captured** -> KEPT, not superseded. It is the true record of what the step-P2 readers did not have (ZR 34-21/34-22/34-23 among them). A dated change-log entry in overlay-reading.json records that those are now captured/read in step P4 and that the three result rows are superseded; the not-captured list itself still names what the step-P2 readers lacked and is unchanged.
- **real-lot unit rows (L6/L7 and the senior-housing row)** -> NOT superseded. Step P4 reads the ZR 23-52 factor and gives a worked count for the MADE-UP 100x100 lot only; neither reading computes the real lot's count (its area is recorded two ways and the FAR-definition gap applies). "A reading of the factor is not a reading of the real lot's count" - so the real-lot rows are left.

Each supersession carries a dated (2026-10-07) change-log entry in overlay-reading.json; the loader
refuses a superseded row by default and names the current step-P4 row (test proves it).

## Two things that did not move

- Whole-lot corner-coverage rows (real-lot L5; corner-reach real-lot-coverage; step-p1-worked corner-150x100-coverage and corner-200x120-coverage): UNCHANGED. Both readings again say coverage is 100 percent for the corner-lot portion only when comparing the overlay with plain R6B (lot-coverage row records "the overlay adds no coverage rule", not a whole-lot figure). The pinned_coverage guard still passes.
- Reach rows of corner-reach.json (real-lot-reach, C1-reach, C2-reach, C3-reach): UNCHANGED, not superseded, not reworded. tests/spatial/test_lot_reach.py passes unchanged.

A script comparison of every row's `expected` block and `superseded_by` in all seven pre-existing cases
(HEAD vs working tree) shows the ONLY changes are the three `superseded_by` additions above. No
expected kind or value changed anywhere.

## Where the two readings differ, or one holds a condition

- **ZR 23-443(c) (Limited Height Districts)**: reading 9 reads it NOT KNOWN (the PLUTO `ltdheight` field is absent from the served row); reading 10 reads it as NOT APPLYING on the recorded facts (no limited-height district recorded). -> row `zr-23-443-reach` stays NOT KNOWN, naming both; guarded by READINGS_DIFFER and MUST_STAY_NOT_KNOWN.
- **ZR 34-23 completeness (rear yard)**: reading 9 holds "no 34-23 rear-yard modifier" subject to the capture holding only the ZR 34-23 title line (full sub-section list not confirmed by the folder); reading 10 treats the captured 34-231/232/233 as the complete set and the result as settled. -> row `rear-yard` records the answer (same as plain R6B) AND states the condition in the value, naming reading 9.
- **ZR 35-22 governing chapter**: both reach the same effect (R6B bulk); both leave open whether ZR 35-22 (Chapter 5) or ZR 34-111 (Chapter 4) formally governs an all-residential building. -> stated in the `zr-35-sections` value as not known, both named.
- **made-up 100x100 units**: both reach 29 conditionally; both attach the floor-area-ratio-definition condition; reading 10 adds a "multiple dwelling residence" condition. -> `made-up-100x100-units` value states the shared condition and names reading 10's extra one.
- **"did not have" list differences**: reading 9 names the full-34-23-list caveat and the terms Limited Height District, aggregate width of street walls, block, short dimension of a block; reading 10 names multiple dwelling residence, height factor, open space and the Chapter-5 scope section. -> recorded in `sections-and-facts-not-had` as differences, NOT as the agreed list (the M4-T030 F1 lesson).

## What stays "not known"

- `real-lot-prevailing-frontage` (both: no neighbouring-building street-wall data).
- `zr-23-443-reach` (both for (a)/(b)/(d); readings differ on (c)).
- Carried forward, unchanged: the real lot's rear yard beyond the corner, lot width, base-plane elevation (step-P3 rows); whether the overlay's no-front-yard/no-side-yard changes plain R6B (no R6B front/side-yard requirement section - named in `sections-and-facts-not-had`).

## Checks (direct exit code captured with echo $? right after each)

- a. `python -m ruff check .` (services/api): `All checks passed!` - **exit 0**.
- b. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py` (lanes venv, PYTHONPATH=services/api, PYTHONDONTWRITEBYTECODE=1): **77 passed** - **exit 0**. (test_lot_reach.py unchanged and green.)
- c. renderer check mode `r6b_reference_cases_render.py --check`: `reference-case check PASSED (no issues)` - **exit 0** (8 pages byte-identical + full validate_all).
- d. `python3 tools/modularity_check.py --check` (repo root): `selected 717 files; failures 0; warnings 29` (all warnings pre-existing untouched files; no reference_cases file flagged; support files <=574 lines) - **exit 0**. `python3 scripts/lanes/check_lane_paths.py --coverage`: `LANE COVERAGE PASS: 9127 file(s)` - **exit 0**.
- e. two mutation proofs in a temporary copy of step-p4-worked.json OUTSIDE the repository (`scratchpad/step-p4-worked.copy.json`): (1) one quoted law phrase changed in the `zr-34-22-sections` 34-221 citation -> citation check FAILS naming `step-p4-worked/zr-34-22-sections: the quoted words for 34-221 are not found in the capture zr-34-221`; (2) `zr-23-443-reach` (the readings differ) given a value -> `readings_differ_errors` FAILS naming `step-p4-worked/zr-23-443-reach: the two readings differ here, so it must be 'not known', not 'value'`. **BOTH PASS, exit 0.**

The full services/api suite was NOT run (the orchestrator's single wave-final run).

## Doubts / limits

- "Had / did not have" is judged strictly from the two readings' own words (FILES I READ, Q10, and the separate not-read lists), as the M4-T030 reviewer did; I did not open the sealed folder.
- `zr-34-111-exceptions` overlaps in part with the step-P3 `zr-34-111-governs` row. I judged they answer different questions (which-section-governs vs do-the-exceptions-reach, the latter now read with the qualifying-residential-site definition), recorded them as distinct and cross-referenced in `does_not_establish`, and did NOT supersede the step-P3 row (its which-section answer is not re-established by both P4 readings). A reviewer may prefer a tighter framing.
- Geometry/area numbers (lot area, 1.5-acre threshold) are attributed to the readings and the recorded facts; I did not re-survey.

END-OF-REPORT
