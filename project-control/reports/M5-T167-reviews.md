# M5-T167 reviews (every return kept unchanged)

- Four build rounds. Round 1 (a previous session; integrated 474c8ee3): the engine-side zoning-lot isolation behind facades and the block-frontage measure. Round 2 (builder 8fa1714c, integrated 59a1b9bb): the (b)/(c)(3) checks combined with (a), the 1.5.0 emission, the page-8 open item, the register events, NB-03 rev 3 / NB-01 / NB-05, the benchmark regenerated. Round 3 (ad9079f4, integrated 11cdb085): five benchmark-consumer tests outside the first packet (scope correction 2). Round 4 (ff65b622, integrated d0611800): the orchestrator printed the owner's report from the real preview at dde8a181 and found page 8 still printing the 1.4.0 item while page 6 had dropped its rear-yard line; an independent read-only diagnosis (three agents) traced it to the live results route never threading street data; round 4 carries street data on StudyInputs and threads it in the route (production switch unchanged, default off), and gates page 6's line on whether the engine applied the checks so pages 6 and 8 agree on every document (scope correction 3). Each round passed an independent read-only pre-integration check that re-ran the whole api suite (9767, then 9776 passed) and, in round 4, the whole web unit suite (2704 passed).
- G2 orchestrator self-check at d0611800: every file of the four material commits inside the packet's allowed paths (scope corrections 1-3); LF sha256 equal to each builder's return; lane coverage PASS; research_record_check PASS. The owner's report printed from the real preview at 48b77e02 (session-2026-10-14d/print-48b77e02/): page 8 item 4 'A conditional reading of the short-block rule ZR 23-344(b) and the adjoining-side-line rule ZR 23-344(c)(3): the rear yard is not settled on this lot', label Conditional, ZR 23-344 linked; page 6 no longer lists the rear yard as unchecked; the two pages agree. CI run 38670334315 at 48b77e02: 21 of 21 jobs success.
- G1 data-contract-verifier at d0611800: PASS, no required correction (law vs code for (a), (b), (c)(1), (c)(3); the benchmark against real-lot.json; NB-01/03/05 digests; the register; the owner's print); advisories: name the (c)(1) alternative in the text; add rear_yard_checks.py to the register entry's code links.
- G3 code-reviewer at d0611800: PASS, no required correction; advisories: S19's street-width clause (recorded by scope note 4), the objective's file-size wording (scope note 4), the doubled street-window fetch when the live flag is on, an unused argument.
- G4 qa-engineer at d0611800: PASS, no required correction (the whole api suite, the scenario table, the input-state sweep, the texts collection, own mutation probes); advisory: an unreachable not_applicable text.
- G5 security-reviewer at d0611800: PASS, no required correction; advisory: an unexpected street-data provider exception is not coerced to the route's 503 (flag off by default).
- Every advisory is backlog DB-265, queued for M5-T170.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

# M5-T167 G1 review — law and data (data-contract-verifier)

I am an AI agent (read-only). I reviewed ledger task M5-T167 at pinned commit d0611800 on task/wave25-rear-yard-short-block, from an archived copy, against the ZR 23-344 captures, the R6B reference case, the research records and the owner's real print. I did not produce this work. Agreement by an AI is not a professional or legal determination.

## Verdict: PASS (2 ADVISORY, no REQUIRED corrections)

## 1. Law vs code (ZR 23-344 a/b/c1/c3)
Snapshot zr-23-344.snapshot.json (digest 91f94915...) carries (a) within 100 ft of a 135-degree-or-less corner; (b) short dimension of a block, no rear yard within 100 ft of that street line; (c)(1) rear yard required where the deemed rear lot line coincides with a neighbour's rear lot line; (c)(3) in R6-R12 no rear yard where it coincides with a neighbour's side lot line. rear_yard_checks.py implements:
- (a) _check_a (L146-186): angle<=135 and within-100-ft reach — matches.
- (b) _check_b + classify_short_dimension (L108-231): strict `<230` (SHORT_DIMENSION_MAX_230=230.0), and for a REAL lot basis_fixed_by_law=False so (b) is not_known because the measurement basis is unresolved law — matches reference rows b-less-than-230 and b-measurement-basis (not because a value >=230).
- (c)(3) _check_c3 + _in_r6_r12 (L234-272): R6-R12 -> not_known (neighbour lot-line kind not captured); R1-R5 -> not_applicable — matches.
- _combined (L275-319): not_known, way=conditional, three conditions, ZR 23-344+12-10 linked, never unconditional "no rear yard"; names (b) and (c)(3) besides (a). R6B read as within "R6 through R12" with the professional-confirmation caveat (reference c-1-vs-c-3).
The zoning-lot condition attaches through combined condition 3 ("If the zoning lot is confirmed..."), satisfying the (b) requirement that it keys on the zoning lot's front lot line.

## 2. Benchmark lot (journey fixture)
recorded_215_16_northern_journey.json (contract_version 1.5.0): rear_yard (a) applies with 89.7 deg/144.6 ft (derived), (b) not_known, (c)(3) not_known, combined conditional with the basis/neighbour/zoning-lot conditions. No unconditional "no rear yard"; (a) is not the only exception. input_facts: recorded_lot_area 10075 administrative_record (used in the FAR calc, L1) and lot_outline_area 10387.99 gis (drawing measure, not used) — each one basis, no mixed figure (DB-262), matching real-lot.json facts and sources. constraint_lines rear_yard_100ft_line and corner_area both not_known, no geometry (S24). The block matches the code output byte-for-byte, confirming it is the regenerated emission, not a hand-edit.

## 3. Research records
NB-03 rev 3: research_status interpretation_awaiting_review; code_identity for rear_yard_checks.py = fd806941... — I recomputed the LF-normalized sha256 and it matches. NB-01 rev 6 (the brief anticipated rev 5; round 4 resynced it after the street-data threading touched study_inputs.py/readers.py/three_way_document.py in its code_paths — expected branch movement): all 13 code_identity digests recomputed and matched. NB-05 rev 4. `research_record_check --check` PASS (exit 0), code_current True for all. professional_review null in all three (no human verdict).

## 4. Review register
Entry r6b-rear-yard-corner-waiver: human_review verdict "Not reviewed", decision null; I scanned all 23 entries — no human verdict anywhere. A dated event seq 27 (2026-10-14, interpretation_changed, M5-T167) plainly describes the change: the reading broadened to (a)/(b)/(c)(3), the stale "withheld pending overlay" text replaced, combined row not_known/conditional, (b)/(c)(3) named and linked, no rule-file change. The cited code_links (rule.json + evaluator/registry) are unchanged, so the event is correctly interpretation_changed. `render_review_register --check` PASS (exit 0). See ADVISORY 2 (rear_yard_checks.py not in code_links).

## 5/6. Prints (branch head and owner's real print)
print-48b77e02 (round 4, head 48b77e02) report.html: page-8 open-item #4 "Rear yard" = Conditional label, text "A conditional reading of the short-block rule ZR 23-344(b) and the adjoining-side-line rule ZR 23-344(c)(3): the rear yard is not settled on this lot", conditions named (survey/deed, adjoining lot lines), law link to .../23-344; reason gives 144.60 ft and 89.7 degrees matching the fixture. "What was not checked" (Pending verification) lists plan placement / street wall / parking only — it does not re-raise rear yard, so pages 6 and 8 agree. Never an unconditional "no rear yard"; (a) is not the only exception. Street data parity: the journey test uses the recorded benchmark pack (services/api/tests/fixtures/benchmark_215_16_northern) and the recorded DCM window (DCM_ENVELOPE in tests/spatial/_northern_replay.py) through dcm_street_centerline_arcgis; the live route threads the lot's DCM street window on StudyInputs (study_inputs.py, round 4) via the same connector — the same recorded city-map source, and the live numbers equal the fixture.

## CI
d0611800 run 38670334315: all 21 jobs success (api ruff+pytest, web-e2e, contracts, modularity, control-plane, security gates). Delta d0611800..48b77e02 = only project-control/state.json + M5-T167.json (control records; no material M5-T167 file), so the reviewed identity is byte-stable. The 48b77e02 "CI" job was still in_progress at read time; confirm green before accept (do not rerun).

## Findings
1. ADVISORY — (c)(1) not named in the engine check/combined text (rear_yard_checks.py _check_c3 L247-272). Result is correctly not_known and page 8 conveys the fork; add the (c)(1) alternative wording for completeness.
2. ADVISORY — register entry code_links omit rear_yard_checks.py, the module implementing (b)/(c)(3); digest is carried by NB-03 and the checker passes, but add it to code_links.

No REQUIRED corrections: every owner prohibition holds — not-known/Conditional under both zoning-lot readings, (b) named and linked, the corner test never the only exception, no two bases mixed in one figure, no mapped width adopted as settled, no human verdict, draft reading labelled.

END-OF-REPORT

## G3 (code-reviewer)

M5-T167 INDEPENDENT GATE REPORT - G3 (code review, read-only)

I am an AI agent (code-reviewer). This is not a human or professional review. Pinned SHA d0611800 on task/wave25-rear-yard-short-block in /root/project/w-wave20; app files byte-identical to CI head 48b77e02 (control records only differ, per the brief). Net diff 1f98bcd6..d0611800.

VERDICT: PASS (with 4 ADVISORY notes; none block acceptance from the G3 code-review scope).

WHAT I CHECKED AND FOUND

1. THREE RULES (rear_yard_checks.py). RULE 1 - no default stands for a fact: every optional input is tested with `is None`/identity, never truthiness-as-no. _in_r6_r12 returns None for empty/None district (not \"outside\"), True for R6-R12 prefixes (checked before R1-R5), False only for R1-R5; _check_c3 uses `in_range is False` -> not_applicable, else not_known. _check_a requires BOTH angle and reach (`is None`), then numeric `> 135`. build_rear_yard_analysis emits an area fact only when the value is present AND source_title and source_date are both non-empty (no invented provenance). I found no truthiness test that reads an unknown yes/no/number as \"no\". RULE 2 - one test per input state: parametrized state tables SHORT_DIMENSION_TABLE, CORNER_WAIVER_TABLE, C3_DISTRICT_TABLE pin each state. RULE 3 - plain user texts: test_texts_are_plain_user_texts guards 5 analyses against captur*/gap/reading n/task-id/\"the caller\"/\"is built\"/db-/step-p/schema/fixture; the DOB disclaimer is on every check; test_no_unconditional_no_rear_yard_anywhere requires every \"no rear yard\" be qualified \"within 100 feet\"; (b)/(c)(3) are always named beside (a). Emitted texts carry no internal names.

2. Edge correctness. Strict `< 230`: 229.99 applies, 230.00 and 230.01 not (M2/M3). _fmt_measure re-renders at 6 decimals when a 2-decimal round would exceed the value, so 229.996 never prints \"230.00\". Corner waiver qualifies at exactly 135 (\"not more than 135\"). Real-lot (b) and (c)(3) are not_known whatever the measured separation (basis_fixed_by_law False on every real-lot path). The within/beyond-100-ft method and the exact-100-ft edge are handled by withholding: _rear_yard_constraint_lines emits rear_yard_100ft_line and corner_area as not_known with no geometry (S3/S24), so nothing is drawn or rounded on the unresolved edge.

3. Zoning-lot isolation (round 1, 474c8ee3). Facades confirmed: three_way_document.py imports _zoning_lot_scope_statement/_apply_zoning_lot_scope_row from .three_way_zoning_lot with a `# noqa: F401 facade` note and uses them at the call site; result_way_bridge.py imports and re-exports zoning_lot_citation from .result_way_zoning_lot (in __all__) and calls it. Line counts at d0611800 vs base: result_way_bridge.py 525->444, three_way_document.py 904->864 (both shrank); result_ways.py 711->711 (unchanged - see finding 2); new modules three_way_zoning_lot.py 105 and result_way_zoning_lot.py 102. python tools/modularity_check.py --check: 803 files, 0 failures, 33 pre-existing warnings, exit 0; the two review_signal WARN files are result_ways.py and three_way_document.py.

4. readers.py appendix open item. _apply_rear_yard_open_item calls constraint_text.rear_yard_combined(results) (a pre-existing, non-forbidden reader); on a 1.4.0 document this returns None -> no-op -> byte-identical to M5-T165's REAR_YARD_OPEN_CHECK wording. On 1.5.0 it rewrites the effect from the document's own combined `way` (Conditional label) and names ZR 23-344(b)/(c)(3), never \"not yet checked\". Proven by test_round4_1_4_0_corner_report_page_6_and_page_8_agree (asserts REAR_YARD_OPEN_CHECK on the 1.4.0 render).

5. block_frontage.py (S15). Pure geometry over an injected StreetData; it issues no request itself. Fail-closed: missing window/lot point/frontage centreline, or fewer than two bounding cross-streets on opposite sides, yields empty separations (not known), never a guess. Single basis (derived/centreline); street_mapped_width_ft returns None for ranges/Unknown (DB-260). No basis mixing.

6. Self-checks in my scratch copy (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider). `cd services/api && python -m ruff check .` -> All checks passed, exit 0. pytest tests/scenario/three_answers tests/drawings/report tests/contracts tests/journey -> 1418 passed, 2 skipped, exit 0.

7. Round 4 (d0611800). StudyInputs.street_data defaults None (additive, inert). live_street_data_provider is bound only behind LIVE_SPATIAL_PROVIDER_ENABLED (default off), proven by test_live_default_flag_gates_the_geometry_binding (flag off -> street_data None -> 1.4.0; flag on -> carried -> 1.5.0). results_read.py threads inputs.street_data into run_engine_and_result_ways_from_evidence; _rear_yard_analysis_for returns None when street_data is None (so the document stays 1.4.0 with no rear-yard check). first_option_results._not_checked gates the corner-lot rear-yard line on `not rear_yard_applied`, and emit_three_way_document drives both _apply_first_option(rear_yard_applied=...) and _apply_rear_yard from the SAME `rear_yard_analysis is not None`, so page 6 and page 8 cannot diverge. Regression coverage is strong and carries red/green notes: the 1.4.0 and 1.5.0 corner-report agreement tests, the benchmark page-6/page-8 tests, the live-route no-street vs street_on reproduction (reproduces the committed 1.5.0 rear_yard + input_facts byte-for-byte; stays 1.4.0 with the shared core when absent), and the fail-safe None test. These would catch a regression of the pages-6/8 contradiction (dde8a181). CI at head 48b77e02 (run 38670334315): all 21 jobs success.

FINDINGS

Finding 1 (ADVISORY) - input_facts emits only the two DB-262 area facts (recorded_lot_area administrative_record, lot_outline_area gis); S19's street-width facts (Northern Blvd/215 Street/215 Place administrative_record; SW end not known) are not emitted. S24 (one figure per basis, corrected areas) is met and tested. From code review this is not a defect; I route the REQUIRED/not completeness call on S19 and the \"nine bases\" clause to the data-contract-verifier and directive-compliance-verifier.

Finding 2 (ADVISORY) - the objective and S16/S20 say \"net-shrink result_ways.py\"; the moved cluster was actually in result_way_bridge.py, which shrank (525->444) along with three_way_document.py (904->864). result_ways.py is unchanged (not grown); modularity passes. Reconcile the acceptance-text file name; no code defect.

Finding 3 (ADVISORY) - with the live flag on, the geometry and street-data providers each fetch the DCM window (fetched twice). Flag off in production/benchmark, so it never ships; builder disclosed it. Efficiency only.

Finding 4 (ADVISORY) - _rear_yard_constraint_lines ignores its operative_reach_ft argument (lines are unconditionally not_known by design, S3). Drop the parameter or add a note; cosmetic.

WHAT I COULD NOT CHECK - the whole api suite (QA reviewer's run); the owner's PDF pixel comparison across the three prints and the website before/after screenshots; independent law/reference-case re-derivation of expected values and NB-01/NB-03/NB-05/register records (data-contract/directive/research reviewers own these); modularity exactly at d0611800 (ran at 48b77e02, byte-identical app files). The in-progress CI run is a disjoint M3-T009/M5-T181 control push.

END-OF-REPORT

## G4 (qa-engineer)

# M5-T167 G4 independent quality gate — rear yard on a short block (ZR 23-344(b)/(c)(3))

I am an AI agent performing an independent, read-only QA gate at the frozen reviewed commit `d0611800` (CI head `48b77e02` differs only in control records). This is not a human or professional review. I did not produce this task. All work ran in a `git archive` copy under `/tmp/claude-0/t167-review-g4/`; I wrote nothing in any repository and started no server.

## VERDICT: PASS (1 ADVISORY, not acceptance-blocking)

## 1. Required checks (archive copy, lanes venv) — all green
- ruff `services/api`: exit 0, "All checks passed!"
- pytest `tests/rules`: 1159 passed, exit 0
- WHOLE api pytest (`-p no:cacheprovider`): **9776 passed, 8 skipped, exit 0** (the single whole-suite run of this wave; `pgrep -af pytest` checked first, waited for the peer reviewer's run to finish)
- `validate_contracts.py`: 23 schemas, 0 failures, exit 0
- `research_record_check.py --check`: PASS, exit 0 (NB-03 `interpretation_awaiting_review`, every record `code_current=True`)
- `render_review_register.py --check`: PASSED, exit 0

## 6. CI at 48b77e02 (read-only, not rerun)
Run `38670334315`, `headSha 48b77e0257edc…`, workflow CI, conclusion **success**. All **21 jobs success, 0 non-success** — including `api (ruff + pytest)`, `web-e2e (vitest + Playwright vs recorded-official-fixture API)`, `web (lint+typecheck+build)`, `modularity`, `contracts`, `validation-suite`, `exact-production-install`.

## 2. Scenario table S1–S25 (no S22) — every scenario has a pinning test and reproduces
| S | Behaviour | Pinning test / evidence | Result |
|--|--|--|--|
|S1|strict <230; 229.996 never "230"|test_rear_yard_short_block::test_short_dimension_threshold_is_the_captured_230_strict, ::test_229_996_is_never_printed_as_230 (+ probe, mut1/4)|PASS|
|S2|bases straddle 230→not known, no mixing|::test_real_lot_short_dimension_is_not_known_whatever_the_measure, ::test_short_dimension_state_table|PASS|
|S3|within-100-ft method / exact-100-ft edge not known|::test_constraint_lines_carry_no_geometry_when_not_established; reach stays not_known; reference case b-within-100|PASS|
|S4|99.97 vs 100 conflict→Conditional|combined stays not_known/conditional; reference case|PASS|
|S5|lot on long side only→not applicable|test_block_frontage fail-closed + real-lot not_known|PASS|
|S6|corner lot→short street|test_block_frontage::test_nearest_cross_street_on_each_side|PASS|
|S7|two-lot zoning lot carries zoning-lot condition|journey byte-golden (mut2) + combined 3rd condition|PASS|
|S8|park/railroad/paper/ALLEY→not known|test_block_frontage::test_one_sided_window_is_not_known / ::test_parallel_streets_are_not_bounding|PASS|
|S9|irregular/non-parallel→not known|::test_parallel_streets_are_not_bounding + real-lot not_known|PASS|
|S10|district Conditional / outside not applicable|::test_c3_district_state_table (mut3)|PASS|
|S11|union (a)&(b) named; remainder (c)(3)|::test_checks_name_b_and_c3_besides_the_corner_waiver|PASS|
|S12|mixed-basis sums refused (DB-260)|test_block_frontage::test_street_mapped_width_single_number_only; single-basis separations dict|PASS|
|S13|benchmark Conditional only; 23-344(b) linked|::test_combined_row…, ::test_no_unconditional_no_rear_yard_anywhere, test_constraint_rows::test_s1_benchmark…, test_report_benchmark::test_benchmark_rear_yard_reads_as_the_applied_conditional_result|PASS|
|S14|register/record checks; title+interpretation broadened to (a)/(b)/(c)(3); NB-03 rev3|render_review_register --check, research_record_check --check, register.json diff verified ("No rule-file change" documented)|PASS|
|S15|window ≤1 request; failure→not known|test_block_frontage fail-closed; test_study_live_geometry::test_raising_fetch_yields_none_and_route_stays_200_with_unknown|PASS|
|S16|zoning-lot isolation behaviour-identical; NB-01; net-shrink|facades keep imports; NB-01 code_current=True; CI modularity green|PASS|
|S17|R6B reference-case tests green & unedited|docs/reference-cases + tests/rules/reference_cases forbidden/untouched (diff empty); tests/rules 1159 passed|PASS|
|S18|benchmark regen; e2e/DXF/SVG same commit, in CI|diff shows fixture_api.py, results specs, DXF/SVG; CI web-e2e green|PASS|
|S19|input_facts nine bases + source/date|::test_input_facts_equal_the_calculation_values_one_per_basis, ::test_no_provenance_means_no_input_fact_invented|PASS*|
|S20|modularity net-shrink; new modules behind facades|CI modularity job green (local run blocked — non-git copy)|PASS|
|S21|1.5.0 declared; strip compares shared 1.4.0 cores|test_results_contract_1_5_0::test_new_valid_fixture_is_journey_plus_only_the_new_blocks (ran green)|PASS|
|S23|appendix reads doc's own rear_yard; 1.4.0 byte-identical / 1.5.0 applied|test_report_benchmark::test_benchmark_rear_yard_reads_as_the_applied_conditional_result; readers no-op on 1.4.0; print verified|PASS|
|S24|each input_fact=calc value; within-lot lines; red/green revert|::test_input_facts_equal, ::test_recorded_area_fact_moves (red/green), ::test_constraint_lines_carry_no_geometry|PASS|
|S25|synthetics re-derived; 182.5 kept; overlay test unedited|synthetic fixture (1.5.0; input_facts 10075/10387.99; rear_yard_100ft_line established+geom); test_constraint_overlay.py forbidden/unedited; CI green|PASS|

*S19: only recorded_lot_area (administrative_record) and lot_outline_area (gis) are emitted; street-width facts are deliberately not emitted per DB-260 — consistent, not a defect.

## 3. Input-state sweep (probe_input_states.py)
Every state of the (b)/(c)(3) checks, the (a) waiver, and the block-frontage measure yields not_known / Conditional (condition named) or a correctly-stated applies/not_applicable — never a silent default. Highlights: real-lot (basis_fixed_by_law=False) always not_known regardless of separation; strict `<230` only on stated cases; unknown/other districts (C/M/empty)→not_known, R1–R5→not_applicable; missing reach/angle→not_known; block_frontage fail-closes on None street_data/lot_point, one-sided window, bad status, missing frontage; combined row always carries the basis, neighbours and **zoning-lot** conditions; input_facts invented only with real provenance.

## 4. Texts collection (probe_texts.py — 83 texts)
All plain user words; no internal tokens (gap/reading 1-2/capture/is built/step-p/db-/schema/fixture/milestone/reference case/tax map/not yet checked); no unconditional "no rear yard" (every occurrence qualified by "within 100 feet"); benchmark and appendix effect name ZR 23-344(b) and (c)(3). One latent wording issue → Finding 1.

## 5. Mutation probes (each red, then file restored to d0611800 byte-identity)
1. `<`→`<=`: test_short_dimension_state_table[230.0-True-not_applicable], test_short_dimension_threshold_is_the_captured_230_strict
2. drop zoning-lot condition: test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture (byte-exact journey golden, line 509)
3. c3 not_known→not_applicable: test_c3_district_state_table[None/''/R6B/R12/R7-1], test_not_known_checks_carry_no_number
4. break `_fmt_measure` round-up: test_229_996_is_never_printed_as_230

## 7. Round-4 live path + print
`test_study_live_geometry` pins: flag OFF (production default)→street_data None→document stays 1.4.0; flag ON→street_data present→1.5.0; raising fetch→None, route 200 with unknown (never invented). Page-6 gating pinned **both** directions (test_first_option_results.py:153 drops line when applied; :166 keeps it when not applied). The owner's real print `print-48b77e02/report.html`: `The rear yard beyond the corner`=0, `not yet checked`=0, `not been applied`=0; appendix open item #4 = conditional reading naming 23-344(b)/(c)(3) with the section linked — i.e. **page 6 has no rear-yard line and page 8 shows the conditional item, in agreement**. Contrasted with `print-dde8a181/` which still had `not yet checked`=1 and no applied reading — confirming round 4 resolved the contradiction. The engine's benchmark answer (not known / Conditional, basis unresolved law, no unconditional "no rear yard") matches the independent R6B reference case, not a program run.

## Findings
**1 (ADVISORY)** — `rear_yard_checks.py:225-231`: the `_check_b` not_applicable text appends "within 100 feet of that street line no rear yard would be required under ZR 23-344(b)" even when the frontage is NOT a short dimension of a block (contradictory). Qualified by "within 100 feet" so it is not an unconditional "no rear yard", and it is unreachable in production (basis_fixed_by_law=True is test-only; the production caller never passes it), so it does not block acceptance. Correction: emit that clause only on the applies state.

## Could not check
modularity_check local run (non-git copy) → relied on CI modularity green; Playwright not re-run (read-only) → relied on CI web-e2e + static artifacts; directive-requirement completeness is the directive-compliance-verifier's pass.

END-OF-REPORT

## G5 (security-reviewer)

G5 SECURITY REVIEW -- M5-T167 (rear yard on a short block), pinned commit d0611800 on task/wave25-rear-yard-short-block.

I am an AI agent (security-reviewer), read-only. This is not a human or professional security review.

VERDICT: PASS (no REQUIRED corrections; one ADVISORY/low note).

Scope: net change 1f98bcd6..d0611800 across services/api, packages/contracts, docs/research, docs/zoning-rule-review, apps/web/src/lib, apps/web/e2e/harness, the 215-16 journey test, and the producer report, focusing on the six security checks plus the round-4 live street-data provider. M5-T167's source/tests/harness/lib are byte-identical between d0611800 and the current branch head (empty diff), so this pinned review covers the live branch.

1. External requests (SSRF / timeouts / size / fail-closed / logging / rate). The block-frontage measure (spatial/site_geometry/block_frontage.py) is pure geometry over an already-fetched StreetData and performs NO I/O (no requests/urllib/socket imports; docstring: "performs no I/O itself"). The only new fetch is round-4 live_street_data_provider (api/v1/study_inputs.py:566-632), which introduces NO new connector: it composes the accepted MapPLUTO lot-geometry fetch and the accepted DCM street fetch (street_data_for_lot, D-090-R124). The host is the fixed NYC ArcGIS base inside those accepted connectors; only a normalize_bbl-validated BBL enters a query parameter -- no user-controlled host or path (no SSRF). The DCM connector sets urlopen(timeout=30.0), a 16 MB body cap, a field allowlist, and page/record/object-id caps; the MapPLUTO connector carries SourceTimeoutError, a retry budget, and feature caps. The provider fails closed: every typed error (MapPluto/DCM connector errors, UnusableLotOutlineError, BBLValidationError) -> None -> engine applies no rear-yard check and the document stays 1.4.0. Logging is minimal and redacted: only type(exc).__name__ and correlation_id (lines 623-629) -- no payload, no response body, no secret. PLUTO reuses the resilient fetcher (TTL cache/retries/breaker/LKG). Route-local rate limit (NB2) is unchanged.

2. New files / paths / deserialization. No new Python source under app (result_way_engine_bridge.py is a modularity split of result_way_bridge.py with a compatibility facade; the only git-added files are M3-T009's _zr_snapshots JSON, out of scope). readers.py reads the internally-produced results document via dict .get(); no pickle / yaml.load / eval / exec / subprocess / os.system anywhere in the diff. No untrusted-byte deserialization added (the DCM parse lives in the accepted connector, reused).

3. Report text / link emission. rear_yard_checks.py and drawings/report/readers.py emit fixed-string templates with numeric interpolation (_fmt / _fmt_measure) and the PLUTO district token; zr_sections are constant tokens ("ZR 23-344", "ZR 12-10"), not URLs. readers.py returns structured dicts, not raw HTML; the HTML/PDF rendering layer (unchanged, not in this diff) performs escaping. No new raw-markup path. The only URLs added in the range are M3-T009 law-snapshot provenance records (request_url / final_url / pdf banner), all on the official law domain zoningresolution.planning.nyc.gov / zr.planning.nyc.gov -- no off-domain link. _DOB is a fixed disclaimer string, not a link.

4. Secrets. Gitleaks-style scan of the added lines found no credentials/keys/passwords/tokens; the only matches were CSS type tokens, the out-of-scope M5-T181 packet objective text, and a _FORBIDDEN_TOKENS test that actively asserts internal tokens never leak into user text (a positive control). CI secret-scan green.

5. Dependencies. No requirements.txt / package.json / package-lock / poetry / pyproject / *.lock change. CI api-lock-verify (fresh hash-pinned uv lock), web-dependency-security, codex-cli-dependency-security, and exact-production-install (pip-audit) all green.

6. Production switch / env / deploy. No render.yaml, Dockerfile, .env, .github/workflows, supabase, config.py, or spatial/live_provider.py change. LIVE_SPATIAL_PROVIDER_ENABLED remains default OFF (live_provider.py unchanged; live_spatial_provider_enabled returns False unless an explicit true token). With the flag off, the live study read and the emitted document are byte-identical to the pre-wiring 1.4.0 slice. results_read.py threads inputs.street_data only; with None (production default) no rear-yard check is applied.

Browser-test harness (apps/web/e2e/harness/fixture_api.py:737-742): street_data=streets where streets = street_data_from_pages([recorded DCM page read by path], envelope) -- recorded data only, no live fetch.

ruff: `cd services/api && python -m ruff check .` on my extracted copy -> "All checks passed!"

CI: all 21 jobs SUCCESS at head 48b77e02 (run 38670334315) and at 18b9eac5 (run 38671073137), including secret-scan, pip-audit and dependency-security; only control-record runs (head 175ec83f) remain in progress (not rerun).

FINDINGS
1. ADVISORY (low) -- study_inputs.py:507-511. The street_data_provider call in pluto_study_inputs_provider is not wrapped to map an UNEXPECTED (non-typed) provider exception to the route's bounded 503, unlike _existing_evidence (259-290). The live provider catches its four documented typed errors and returns None, and the accepted connectors wrap transport/timeout failures in those typed errors, so in practice it fails closed; the production flag is OFF (dead code in production), and the geometry/outline seams use the identical accepted pattern. Correction (optional): document the fail-closed reliance on typed connector errors, or wrap the call to coerce any residual exception to StudyInputsUnavailableError, so an unforeseen connector exception cannot surface as a 500.

WHAT I CHECKED: the six security checks above; the live provider, block-frontage, engine threading, readers, first_option_results, and harness; ruff; a gitleaks-style diff scan; URL-host and escaping review; the dependency/config/deploy file inventory; CI job states.

WHAT I COULD NOT CHECK: I did not run the full api suite (role forbids; G4 is running it) -- I rely on CI green for suite evidence. I did not render the report HTML/PDF or run Playwright (read-only; owner's preview) -- I assessed emission at the data layer and rely on the unchanged rendering layer for escaping. The accepted MapPLUTO/DCM connectors are relied upon as previously accepted (I confirmed timeout=30s and bounded reads but did not re-review them in full, as they are outside this task's diff).

END-OF-REPORT
