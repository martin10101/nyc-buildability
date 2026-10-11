# M5-T176 reviews (every return kept unchanged)

Reviews: G3 data-contract-verifier PASS at d6d2f3b8 (with advisories A1/A2, fixed in rework 1) and delta PASS at ccb25c2a; G4 qa-engineer PASS at d6d2f3b8 and delta PASS at ccb25c2a. Each file below holds the reviewer's first return and its delta return, unchanged.

Every reviewer is an AI agent; none is a human or professional review.

## G3

G3 REVIEW — M5-T176 (data-contract-verifier), reference case `short-block-rear-yard` (35 rows)
Pinned head d6d2f3b8 on task/wave24-report-v3. I am an AI agent; this is not a human or professional review.

VERDICT: PASS (two ADVISORY notes; no required corrections)

INDEPENDENT READING (captures only, before reading the case/readings)
- "less than 230 feet" = strict (230.00 out) — fixed by text.
- Measurement basis of "the dimension between any two #streets#" — OPEN (text says neither street-line, centreline nor lot-line).
- "within 100 feet of such #street line#" method, and whether exactly 100 ft is inside — OPEN (contrast the explicit corner-lot definition).
- Block (12-10): public park CAN bound a block; a private way CANNOT unless it independently qualifies as a #street# (private road/accessory driveway expressly excluded) — fixed.
- (c)(1) vs (c)(3): decided by the KIND of the adjoining zoning lot's coinciding lot line plus the SUBJECT lot's own district; the adjoining lot's district is irrelevant — fixed.
My recomputation of the real block (EPSG:2263, my method stated): tax-map sum lots 1+70 = 100.76+99.25 = 200.01 ft; lot-outline NB frontage = 99.25+103.88 = 203.129 ft (far-corner straight = 203.129); centreline-to-centreline along Northern Blvd between the 215 St∩NB (1048653.70,216429.81) and 215 Pl∩NB (1048907.27,216487.37) intersections = 260.02 ft (−60 ft of half-widths ≈ 200.02 street-line). All bases <230 except centreline (>230). Every figure reproduced the case/readings exactly.

CHECKS PERFORMED (all PASS unless noted)
1. Provenance — provenance/return-independent-hand-calculation-15.md and -16.md are the two input returns byte-for-byte below a short header (diff of body vs /session-2026-10-11e/return-reading-P7-1.md/-2.md = empty). Their sha256 (ba7efca9…, 1c806925…) match the digests pinned in STEP_P7_READINGS (r6b_reference_cases_step_p7.py).
2. Rule of agreement — 24 value rows + 11 not_known rows. I checked all 35 against both full readings. Every value row is jointly held on the same basis; every not_known row is a genuine gap (both not-known, or the readings differ, or basis unfixed) and all 11 are locked by MUST_STAY_NOT_KNOWN (b-measurement-basis, b-within-100-feet, b-exact-100-ft, fit-b-c-overlap, M4, M10, real-lot-short-dimension, real-lot-alley, real-lot-z1/z2-rear-yard, real-lot-beyond-100-sliver). Critically, row real-lot-short-dimension keeps the two divergent centreline figures as SEPARATE `derived` quantities (260.02 reading 1 / 261.0 reading 2) and records NO single centreline figure — no smoothing. No not_known row conceals an actual agreement.
3. Law quotes — all 103 citations across the rows are exact substrings of their repo snapshot `verbatim_excerpt`, with matching `snapshot_id` and `content_digest_sha256` (programmatic check over 16 distinct snapshots, 0 failures). The sealed captures agree with the repo snapshots.
4. Real lot — no row records an unconditional "no rear yard"; all 9 real-lot rows cite ZR 23-344 and name conditions (zoning lot Z1/Z2, measurement basis, the street line/point, neighbour lot-line kind), enforced by real_lot_rear_yard_errors. "complies" appears only in disclaimers (4×, all negations). No "feasible"/"legally correct"/"legally compliant". No program output (program_result_errors guard + FORBIDDEN_KEY_SUBSTRINGS, empty for this case).
5. Bases — every structured quantity carries exactly one of the nine QUANTITY_BASES ({law,deed,survey,printed_tax_map,approved_plan,filing_attribute,administrative_record,gis,derived}); found administrative_record×3 (mapped widths), printed_tax_map×2, gis×5, derived×2. No figure mixes bases; the enum has no "centreline" bucket, so centreline separations are correctly `derived`.
6. M5-T167 map — row m5-t167-scenario-map covers S1–S12 (verified against workorder-D094-v2.md lines 791–802), each to rows or the named reading gap; "within 100 feet" (b-within-100-feet) and "less than 230 feet" (b-less-than-230) are their own rows. S4's ~101.06 ft figure is correctly flagged as an earlier-reading (non-step-P7) value, leaving the within/beyond-100-ft edge not settled.
7. Older rows untouched — no other case JSON changed (diff ced8c5098..d6d2f3b8). Wiring edits (check/lib/render/test, CASE_IDS, REQUIRED_BASE_IDS, OPTIONAL_ROW_KEYS+="quantities") are purely additive registration of the P7 case. The producer report lists the older rows holding the same question (step-p3-worked#real-lot-rear-yard-beyond-corner, step-p5-worked#benchmark-rear-yard-23-342-23-344, step-p6-worked#real-lot-rear-yard-variants — all verified to exist and remain not-settled) and proposes no edit. README update is additive.
8. Authoritative harness — ran tests/rules/reference_cases/test_r6b_reference_cases_step_p7.py + test_r6b_reference_cases.py in w-wave20 (lanes venv): 68 passed. The pinned head d6d2f3b8 is an ancestor of the worktree's current HEAD 7ab4bda5 and the reference-case/checker/research_record_check paths are byte-identical between them with a clean working tree, so the run reflects the frozen content identity.

ADVISORY FINDINGS (not required; the case faithfully applies the rule of agreement)
- A1 (rows c-1-vs-c-3, m5-t167-scenario-map, README, producer report): the district-suffix rule is glossed as "(such as ZR 11-25)". Neither reading names ZR 11-25 (it comes from M5-T167 S10's own framing); and zr-11-25.json was physically present in the sealed folder but unopened, so "a district-suffix rule … that the readers did not have" is slightly loose. Hedged with "such as" and the reading-2-only caveat is correctly recorded (not treated as settled), so this is not a rule-of-agreement violation.
- A2 (row real-lot-bounding-streets, a value row): the detail "the nearest captured cross-streets (45 Road 50 ft, 45 Drive 50 ft) … 46 Avenue (80 ft) … about 126 ft beyond" is stated by reading 1 only (reading 2 did not identify these). It sits inside the acknowledged "SW short end is NOT resolved" portion; the recorded VALUE (the three bounding streets + widths) is jointly held and the closing clause scopes the agreement correctly, and it asserts no settled conclusion and does not conflict with reading 2.

WHAT I COULD NOT CHECK
- I did not re-fetch the ZR live from zoningresolution.planning.nyc.gov; I verified quotes against the repo snapshots and the sealed captures (which agree). NB-03/NB-04 freshness notes record an orchestrator re-fetch of 23-344/12-10 on 2026-10-10 unchanged. A live-source G1 check is out of scope for this sealed-folder reading.
- The tax-map PDF images, the 2017 Buckley survey, and any deed/ZD1 are not in the repo (sealed facts give only labels/derived geometry); these remain missing facts and are correctly kept unresolved in every dependent row.
- Full CI at the accept head is the orchestrator's/CI's job; I ran only the focused reference-case suite.

Every unresolved input (measurement basis, within/exact-100-ft, (b)/(c) overlap, non-parallel-block method, Z1/Z2, neighbour lot-line kinds, ALLEY/SW-end feature, R6B-suffix) is kept unresolved throughout.

END-OF-REPORT

M5-T176 G3 DELTA REVIEW (rework 1 at ccb25c2a). I am an AI agent; not a human/professional review.

DELTA VERDICT: PASS — my earlier PASS carries to ccb25c2a.

1. SCOPE (git). Between d6d2f3b8 and ccb25c2a the ONLY commit touching M5-T176 allowed paths is ccb25c2a ("rework 1: the R6B-suffix condition and the cross-street detail worded exactly as the readings give them (G3 A1, A2)"). Files: case JSON, rendered page, README, producer report (+Rework 1 section). Across ALL 35 rows no expected.kind, value structure, quantities, citations or facts_used changed; only four rows' prose changed: c-1-vs-c-3, real-lot-bounding-streets, m5-t167-scenario-map, both-readers-did-not-have. The 11 not_known rows are untouched; every unresolved input stays unresolved. The branch also carries disjoint other-task commits; none touch M5-T176 paths.

2. WORDING vs the readings (provenance 15/16).
- A1 fixed: the suffix condition now reads reading 2's own words — "the captured 23-344 text does not separately enumerate the letter-suffix districts (R6A/R6B); reading 2 reads R6B within 'R6 through R12' … a point a professional must confirm" (reading 2 line 76 verbatim sense), "reading 1 … without raising the suffix point" (reading 1 M7). ZR 11-25 is now stated as "was in the sealed folder and is not read by reading 1 or by reading 2" (the case's "not read by reading N" vocabulary; zr-11-25.json is indeed in the folder, unread by both) and, in the scenario-map row, attributed to "M5-T167 S10's own framing" — no longer implied to be the readers'.
- A2 fixed: the cross-street detail (45 Road 50 ft, 45 Drive 50 ft, 46 Avenue 80 ft ~126 ft beyond) is now explicitly "reading 1 adds (reading 1 only)" (reading 1 Q5a words); the jointly-held part is scoped "(both readings)". Reading 2 does not name these — attribution now correct.

3. CHECKS (git archive unnecessary: worktree HEAD == ccb25c2a, clean for these paths; run in place). From services/api, lanes venv:
- `python -m ruff check .` → "All checks passed!", exit 0.
- `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py` → 137 passed, exit 0 (the producer's prior single failure, the brittle CASE_IDS tuple, is resolved).
- `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` → "reference-case check PASSED", exit 0.

COULD NOT CHECK (unchanged from the G3 report): no live ZR re-fetch (verified against pinned snapshots/sealed captures, which agree); no tax-map image/survey (kept unresolved); full CI at the accept head is the orchestrator's/CI's job. NB-03/NB-04 read only and untouched by this rework.

Nothing new adverse. END-OF-REPORT

## G4

# M5-T176 G4 QA gate report — short-block-rear-yard (ZR 23-344(b)/(c)(3))

I am an AI agent (role: qa-engineer), an independent read-only reviewer. This is not a human or professional legal review. I reviewed at the pinned head `d6d2f3b80d8f6ead56c6d505befdc9f04ccf57f2` on `task/wave24-report-v3`, from a clean `git archive` copy under my scratch folder. I did not edit, commit, push, or run `project_control.py` (beyond none needed).

## VERDICT: PASS

No REQUIRED findings. One ADVISORY observation (F1). All 8 acceptance scenarios and all 7 common-brief check points reproduced clean.

## Required checks (direct exit codes, lanes venv, from the archive)
- `cd services/api && python -m ruff check .` -> `All checks passed!`, exit 0.
- `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py` -> **137 passed**, exit 0. (The producer's report said "1 failed, 136 passed"; that single failure was the `test_r6b_reference_cases.py` CASE_IDS tuple, fixed by the ORCH-CORRECTED commit `d6d2f3b8`. At the pinned head it is green.)
- `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` -> `reference-case check PASSED (no issues)`, exit 0.

## S1-S8 scenario table
| S | how I tested | result | exit |
|---|---|---|---|
| S1 provenance present/unchanged, digest pinned | `sha256sum` of prov 15/16 == pins in step_p7.py; byte-diff of each prov body (from `PART 1 of`) vs the original returns = identical (0 lines); `step_p7_reading_errors()` | PASS | 0 |
| S2 every row names both readings + quotes captured words | `both_readings_errors`/`citation_errors` over 35 rows (via full suite); source_reference names both stems on every row | PASS | 0 |
| S3 S1-S12 mapped; "within 100 ft"/"less than 230 ft" own rows | read `m5-t167-scenario-map` (S1..S12 each present) + `b-within-100-feet`(not_known), `b-less-than-230`(value) | PASS | 0 |
| S4 program_result_errors empty | `program_result_errors` == [] | PASS | 0 |
| S5 suite green + README lists case | 137 passed; `readme_errors` clean; CASE_IDS tuple updated | PASS | 0 |
| S6 NOT SETTLED rows stay not_known w/ kind-of-gap | 11 not_known rows all carry "kind of gap"; my probe 2 refuses a value | PASS | 0 |
| S7 every quantity one of nine bases, no mixing | module bases == `tools/research_record_check.QUANTITY_BASES`; probes 3a/3b refuse missing/second basis | PASS | 0 |
| S8 no unconditional "no rear yard"; real-lot quotes 23-344 | `real_lot_rear_yard_errors` == []; probe 4 refuses unconditional | PASS | 0 |

## My own mutation probes (independent, in-memory deepcopy / monkeypatched dir)
All behaved as required:
1. Changed a quoted law phrase in `c-from-which-street-line` -> `citation_errors` fails and names the row. PASS
2. Gave a value to NOT-SETTLED `b-measurement-basis` -> `must_stay_not_known_errors` fails and names the row. PASS
3a. Removed a quantity's basis (`real-lot-bounding-streets`) -> `quantity_basis_errors` fails ("no measurement basis"). PASS
3b. Added a second basis key to a `real-lot-reach` quantity -> `quantity_basis_errors` fails ("keys differ"). PASS
4. Unconditional "no rear yard" in `real-lot-z2-rear-yard` -> `real_lot_rear_yard_errors` fails and names the row. PASS
5. Flipped one byte below the header of provenance 15 -> digest pin fails ("digest changed"). PASS
Control: clean case `validate_case` == []. PASS

## Rule of agreement — independent read of both returns (P7-1, P7-2) vs the 35 rows
I read both returns in full (the sealed-folder readings reproduced byte-for-byte in provenance 15/16) and the ZR captures, not the brief's summary.
- Value rows rest on genuine agreement on the same basis: b-what-measured, b-less-than-230 (strict <230, both via M1/M2/M3), b-block-boundary (park yes / private way no), c-which-lots, c-becomes-rear-lot-line, c-from-which-street-line, fit-sections, fit-multiple-apply, fit-b-on-corner-lot, M1/M2/M3/M5/M6/M7/M8/M9, real-lot-bounding-streets, real-lot-front-lot-line [S], real-lot-reach [S], real-lot-missing-facts, both-readers-did-not-have, m5-t167-scenario-map. No value row is supported by only one reading.
- No value row smooths two differing figures: `real-lot-short-dimension` keeps BOTH centreline figures separate (reading 1 = 260.02 ft, reading 2 = 261.0 ft) and stays not_known; quantities carry distinct bases (printed_tax_map, gis, derived, derived) with no mixing.
- `c-1-vs-c-3` correctly records the AGREED branching rule as the value and keeps the R6B-within-"R6 through R12" point as a NAMED condition (reading 2 flags it via a suffix rule it lacked; reading 1 did not raise it) — it does not resolve the disputed sub-point. S10 maps to that gap.
- All 11 not_known rows are genuine: both readings read the gap as unknown (unresolved law and/or a missing property fact), not a concealed agreement. `b-within-100-feet`/`b-measurement-basis`: both call the natural reading perpendicular/street-line but both state the text does not fix it -> correctly NOT SETTLED. Real-lot rear-yard rows stay conditional/basis-dependent.
- `both-readers-did-not-have` correctly separates items BOTH name from items EACH names, and treats the #street setback line# as "read by reading 2, not read by reading 1" (never "not captured").

## Provenance, citations, scope
- Provenance 15/16 raw sha256 == the pins in `r6b_reference_cases_step_p7.py`; bodies byte-identical to the two original returns below a short header; both end END-OF-REPORT.
- All 16 captured snapshot files cited exist; every cited `content_digest` matches the live capture's `content_digest_sha256`; `citation_errors` clean over all rows. I independently confirmed the 23-344(a) quote (only paraphrased in the readings) is a true substring of the `zr-23-344` capture.
- No forbidden wording: "complies/feasible/legally correct/optimal/preferred" appear only inside the explicit disclaimer and the "never the only exception" self-statement; program_result_errors empty.
- Support files all < 600 lines (step_p7 178, check 580, lib 364, render 369; test 258) and import nothing from `app` (the sole "app" hit is a docstring line).
- Byte-stability: M5-T176's material footprint is exactly its 12 allowed-path files (producer `0b88d3068` = 11 files; ORCH `d6d2f3b8` = `test_r6b_reference_cases.py` only). No existing case data file or provenance 1-14 was touched by any T176 commit. The scope-correction (`89c631240`) and G0 re-record (`ced8c5098`) touched only project-control files. The broader `8f713e6a..d6d2f3b8` diff (NB-01, NB-04, verification.json, M5-T164/T166, drawings) is from disjoint PEER commits, not T176; **NB-03/NB-04 were untouched by T176 and remain read-only.** `test_prior_cases_rows_are_byte_stable` passes.
- The ORCH-CORRECTED tuple diff is exactly "append `short-block-rear-yard` to CASE_IDS (line 45)" — matching the `scope_corrections` entry word for word (no row binding, scenario, or other path change).
- Point 7: producer report lists the older rows holding the same question (step-p3/p5/p6-worked#…, real-lot#L12, corner-reach#real-lot-rear-yard), proposes no edit; all remain not-settled, so no contradiction.

## Findings
1. ADVISORY — The "both readings"/NOT-SETTLED guards rely on producer-authored hardcoded row-id lists (`MUST_STAY_NOT_KNOWN`, `STEP_P7_READING_STEMS`), consistent with the step-P3..P6 design. The guards would not by themselves catch a NEW mis-settled row the author omitted from the list; the real guarantee is the independent reading comparison, which I performed and found every current row correctly classified. No action required; noted for suite-design transparency.

## What I could not check
- The sealed folder's third-party captures/geometry inputs on the private build server were not independently re-measured; I verified the readings' internal consistency, their byte-for-byte preservation, and that every cited ZR quote is an exact substring of the pinned repo capture with a matching digest. Reach/geometry figures carry [S] "settled by earlier readings" and are reused, not re-derived here.
- Per the skill, the directive requirement-by-requirement pass (D-094 R036/R037/R044/R079) is the independent `directive-compliance-verifier`'s recorded role; within my G4 scope the substance I can see is satisfied (R036 independent applicability check present; R037 no established exemption — probe 4 + conditional real-lot rows confirm).

END-OF-REPORT

# M5-T176 G4 DELTA review — rework 1 (ccb25c2a)

I am an AI agent (qa-engineer), independent read-only reviewer. Not a human or professional legal review.

## DELTA VERDICT: PASS — my earlier PASS carries to `ccb25c2aa884594a913b5c67d4709c2021db964e`.

### Commands (git archive ccb25c2a, lanes venv)
- `cd services/api && python -m ruff check .` -> `All checks passed!`, exit 0.
- `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py` -> **137 passed**, exit 0.
- `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` -> `PASSED (no issues)`, exit 0.

### 1. Scope of change (git-confirmed)
Between d6d2f3b8 and ccb25c2a, `ccb25c2a` is the ONLY commit touching M5-T176 allowed paths (`git log … -- docs/reference-cases/R6B/ services/api/…reference_cases/ …producer-report.md` returns just it). It changes README, the case JSON, the rendered page and the producer report. The case-JSON diff is exactly 4 rows — c-1-vs-c-3, real-lot-bounding-streets, both-readers-did-not-have, m5-t167-scenario-map — and only their `value`/`source_reference` text (12/12 lines). No `kind`, value-type, quantity, citation, or other row changed. The 137-test suite (incl. byte-stability of prior cases, clean-validate, forbidden-wording) stays green, so the rest of the case is untouched and still valid.

### 2. New wording vs the readings' own words
- **A1** fixed correctly. New text: reading 2 holds the R6B point "because the captured 23-344 text does not separately enumerate the letter-suffix districts (R6A/R6B); … reads R6B as within 'R6 through R12' … a point a professional must confirm." This matches reading 2 Part 3/Q6 verbatim in substance; reading 2 never cited ZR 11-25 (`grep "11-25"` = 0). The old "(such as ZR 11-25) that the readers did not have" is gone, replaced by the accurate fact "ZR 11-25 … was in the sealed folder and is not read by reading 1 or by reading 2" — verified: `zr-11-25.json` IS in the sealed folder law/, and neither reading references it (0/0). Correct "not read by reading N" vocabulary.
- **A2** fixed correctly. The 45 Road / 45 Drive / 46 Avenue cross-street detail is now marked "(reading 1 only)" with source_reference attributing it to reading 15 Q5a only — accurate (reading 2 Q5a names none of these). The ALLEY-inside-block is marked "(both readings)" — accurate (both name it).

### Checked / could not check
Checked: git scope, the two readings' words, sealed-folder contents, NB-03/NB-04 untouched (read only), the three commands. Could not re-measure the sealed folder's third-party geometry; unresolved inputs stay unresolved and are unchanged by this wording-only rework.

END-OF-REPORT
