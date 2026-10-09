# M5-T144 producer report

Producer: rules-engineer (an AI agent). Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a07d362aca5edba80`, reset to the claim head `fcd22b9d763b6942f9167f3dc563ca44d8058e43`. Three server corrections before the first building shape: (1) the withheld rear yard of an R6B corner lot beyond the waiver area says what is really missing (kind: missing information; the C2-2 overlay no longer blocks it; it stays withheld with no figure); (2) the status line's first item reads `Preliminary zoning results`; (3) the geometry block follows every withheld result it draws. One regeneration of the committed journey fixture and its two snapshots; nothing hand-edited.

## The ruled texts as built (exact)

- **Beyond-the-waiver reason** (`_rear_yard_outside_waiver`, branch `not within_point and within_angle`; for the recorded lot, reach 144.60 ft, angle 89.7 deg):
  `The corner rear-yard waiver does not cover the whole lot: the far corner is 144.60 ft from the point where the two street lines meet, beyond the rear-yard waiver area (the waiver covers the area within 100 ft of that point); the two street lines meet at 89.7 degrees, within the waiver's limit of 135 degrees. For the part beyond the waiver area, whether a rear yard is required depends on this lot's exact lot lines and on which lot lines of the adjoining lots meet them. The program does not have those facts, so the rear yard is not known.`
- **Kind of gap:** `missing_information` (geometry.yards.reason_kind `missing_input`).
- **Resolver:** `A survey or deed that shows this lot's lot lines, and the adjoining lots' lot lines where they meet this lot.`
- The first (measured) clause is byte-identical to the claim-head "beyond" clause; the two other branches (angle over the limit; both fail) keep their text, kind (work_owed) and resolver character for character (pinned by S16, RY8, RY9, test_s2, test_s4).
- **Status strip first item:** `{"text": "Preliminary zoning results"}`; chip and `{"text": "Lots you selected"}` unchanged.

### Case rows each new sentence rests on
- "whether a rear yard is required depends on ... which lot lines of the adjoining lots meet them" / "not known": `step-p5-worked` row `benchmark-rear-yard-23-342-23-344` (expected `not_known`; "turns on the adjoining zoning lot's lot-line type ... which the readers did not have"; "would be settled by the adjoining zoning lots' lot-line types") and `step-p3-worked` row `real-lot-rear-yard-beyond-corner` (`not_known`; "needs the adjoining zoning lot's lot-line type"); snapshot `zr-23-344` paragraphs (c)(1)/(c)(3).
- "this lot's exact lot lines": the two readings differ on the far-edge reach (`benchmark-rear-yard-23-342-23-344` facts/reason); a survey/deed settles the lot's own lot lines.
- the overlay no longer blocks the rear yard: `step-p5-worked` row `zr-34-23-page` (ZR 34-23 page read as the complete three-subsection list, "None of the three speaks of the rear yard", "resolving the completeness caveat reading 9 raised in step P4") with `step-p4-worked` row `rear-yard` ("same as plain R6B").
- No section number appears in the new sentences; the words "professional review"/"qualified" are absent. No word of the ruled texts claims more than those rows — no STOP.

## Table 1 - scenarios S1..S17

| S | input (state) | expected | test (file::name) |
|---|---|---|---|
| S1 | C2-2 overlay in R6B, corner, reach 144.60 (>100), angle 89.7 (<135), real table wired | rear yard withheld; exact corrected reason; kind missing_information; exact resolver; no figure; no "overlay" in reason | test_result_ways_facts_area_overlay::test_s1_c2_2_r6b_corner_beyond_100_angle_within_corrected_reason |
| S2 | same overlay/district, corner reach 100 (<=100), angle 90 (<135), K20 checked | rear yard SHOWN (settled); not withheld | ...::test_s2_c2_2_r6b_corner_within_100_angle_within_rear_yard_shown |
| S3 | no overlay, R6B corner, reach 144.60, angle 89.7 | SAME reason/kind/resolver as S1 (C1) | ...::test_s3_no_overlay_r6b_corner_beyond_100_same_corrected_text; also truth_table::test_s3_corner_distance_fails_angle_holds_names_the_distance_not_the_angle |
| S4 | other overlay code (C1-1) in R6B, corner | overlay_support_for None; generic overlay-withheld text naming (C1-1); work_owed | ...::test_s4_other_overlay_code_in_r6b_unchanged_generic_withheld |
| S5 | C2-2 but district not R6B (R5) | overlay_support_for None; lot blanket-withheld (district out of scope); not the corner text | ...::test_s5_c2_2_other_district_table_is_none_and_lot_is_blanket_withheld; bridge_overlay::test_the_statement_is_built_only_for_a_c2_2_overlay_within_r6b |
| S6 | C2-2 in R6B, corner, angle 140 (>135), reach 90 (<=100) | keeps "angle over the limit" waiver text; work_owed; not the corrected text | ...::test_s6_c2_2_r6b_corner_angle_over_135_keeps_waiver_text; truth_table RY8 |
| S7 | C2-2 in R6B, corner present, reach not measured | keeps rear_yard_unmeasured text; missing_information; not the corner text | ...::test_s7_c2_2_r6b_corner_unmeasured_keeps_unmeasured_text; truth_table RY4 |
| S8 | emit recorded state | value_states.rear_yard.reason == geometry.yards.reason; gap_kind missing_information / reason_kind missing_input; no figure | emit::test_s4_rear_yard_withheld_not_not_required; journey honesty assertions |
| S9 | build_status_strip(any rank) | first item == {"text":"Preliminary zoning results"}; chip + "Lots you selected" unchanged | c6_c11::test_status_strip_first_item_is_preliminary_zoning_results |
| S10 | regenerated fixture | status_strip[0] = Preliminary zoning results; only the rear yard's value_states changed (R642) | journey test assertions; wiring test byte-compare |
| S11 | made-up flood-zone corner (heights withheld, coverage shown) through the real engine | geometry.envelope not_available; no withheld height figure (55) anywhere; xfail mark removed, now passes | emit::test_db199a_withheld_height_figure_leaks_into_geometry_known_defect; emit::test_s11_flood_zone_corner_height_withheld_envelope_cleared |
| S12 | both max building height and coverage withheld, engine envelope available | envelope not_available; reason = height reason then coverage reason (fixed order); reason_kind rule_not_implemented (any work_owed) else missing_input | emit::test_s12_envelope_both_height_and_coverage_withheld_combined_reason; test_s12b_...missing_input |
| S13 | height shown, coverage withheld | envelope not_available with coverage reason ALONE (today's behaviour) | emit::test_s13_envelope_height_shown_coverage_withheld_unchanged |
| S14 | height shown, coverage shown | envelope AVAILABLE (tier top_ft) unchanged | emit::test_s14_envelope_height_and_coverage_shown_available |
| S15 | regenerated fixture (no flood zone) | envelope still not_available via coverage; piece 3 changed nothing on this lot | journey test assertion (envelope reason "beyond the corner-lot portion") |
| S16 | R6B corner, angle >135, within and beyond, with/without overlay | the two unchanged branches read identically with and without the overlay; work_owed; unchanged resolver | facts_area_overlay::test_s16_angle_over_and_both_branches_identical_with_and_without_overlay |
| S17 | regenerated document rendered by the website card test | rear yard shows "Missing information about this property."; coverage + setback show the not-built line; no figure | apps/web three-answers-panel.test.tsx S5 (both variants) |

## Table 2 - ruling C5: each geometry layer (from geometry.py), what it draws, states tried, can a withheld figure remain?

| layer (geometry.py line) | zoning results it draws | decision-module states tried | withheld figure can remain? |
|---|---|---|---|
| lot_outline / streets (51, 133) | none (lot rectangle; empty streets) | all | No - draws no zoning-result figure |
| yards (100-118) | rear yard | rear yard withheld (overlay/corner/no-outline/blanket) | No - a withheld rear yard already clears it (`_withheld_not_available`) |
| setback_lines_per_level (120-123) | setback | always not_available from the engine (setback always withheld this milestone) | No - no figure drawn |
| envelope (62-77) | maximum building height (top_ft) AND lot coverage (footprint) | height withheld + coverage shown (flood corner, S11); both withheld (S12/S12b); height shown + coverage withheld (S13); both shown (S14) | WAS the only leak (height withheld while coverage shown kept top_ft=55); NOW cleared when EITHER is withheld - fixed |
| floor_plates (80-97) | building option (and coverage footprint) | building option always withheld this milestone -> always not_available | No - no reachable leak today |

Only `envelope` could leak (max building height withheld while coverage shown); it is the branch repaired. No other layer can leak in any state the decision module produces.

## Regenerated committed document - changed lines, by piece

`packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` (git diff --stat: 1 file, 8 insertions, 8 deletions):
- `value_states.rear_yard.reason` (piece 1): overlay reading-owed text -> the corrected "corner rear-yard waiver does not cover the whole lot: ..." text.
- `value_states.rear_yard.gap_kind` (piece 1): `work_owed` -> `missing_information`.
- `value_states.rear_yard.resolved_by` (piece 1): overlay reading -> survey/deed resolver.
- `value_states.rear_yard.zr_sections` (piece 1): `["ZR 34-23","ZR 23-344"]` -> `["ZR 23-344","ZR 23-342"]` (the rear-yard `_rear_yard_way` zr, reached once the overlay no longer blocks).
- `status_strip[0].text` (piece 2): `Zoning maximum` -> `Preliminary zoning results`.
- `geometry.yards.reason` (piece 1): follows the rear yard -> the corrected text.
- `geometry.yards.reason_kind` (piece 1): `rule_not_implemented` -> `missing_input`.
- `geometry.envelope` UNCHANGED (coverage reason) - confirms piece 3 does not touch this lot (S15).

Snapshots: site-plan SVG - only the `/geometry/yards/reason` note text changed (SVG canvas height grew 1018->1118 to fit the longer note; the two following notes shifted down accordingly; no new/removed shape). DXF - only the A-ANNO-NOTE rear-yard text line changed. No file outside the allowed paths was regenerated (ruling C6).

## Existing tests that MOVED and why (ruling STEP 1 d / C7)

- `test_result_ways_truth_table.py`: row `RY7_distance_fails` kind `work_owed`->`missing_information` + strengthened substrings; `test_s3_corner_distance_fails_angle_holds` asserts the new reason/kind/resolver; `test_rear_yard_reach_just_over_the_limit_prints_visibly_beyond` kind updated; `_EXPECTED_WAY_SIGNATURE` position 16 (rear yard) `Wo`->`Wm` for the 28 states that reach the beyond branch (proven: ONLY position 16 changed, no other position moved).
- `test_result_way_bridge_overlay.py`: rear yard now SUPPORTED, resting on `step-p5-worked/zr-34-23-page`; tests rewritten to check it rests on the caveat-resolving row and all six families are supported.
- `test_result_way_engine_bridge.py`: `test_s8` rewritten - the overlay no longer blocks the rear yard; under a C2-2 overlay with no geometry it is withheld as missing information, no "overlay" in the reason.
- `test_three_answers_three_way_emit.py`: xfail mark removed on `test_db199a_...` (now ordinary, passes); benchmark S4 + S21 rear-yard reason assertions updated (corner text, no "overlay"); added S11/S12/S12b/S13/S14 envelope tests.
- `test_three_answers_c6_c11.py`: added S9 strip test.
- `test_215_16_northern_journey.py`: added pins for the new rear-yard reason/kind, geometry.yards following it, status_strip[0], and envelope unchanged (S15).
- `apps/web/.../three-answers-panel.test.tsx`: both S5 variants now expect "Missing information about this property." for the rear yard and the work-owed line for coverage/setback (the only change that follows from the regenerated document; weakened nothing). `journey-215-16-northern.test.tsx` needed no change (its only rear-yard assertion is way==withheld).
- Unchanged and still green (no assertion moved): `test_result_ways_corner_interior.py` (H3 C1/C3 assert withheld + the measured reach, both still true), `test_result_ways_benchmark.py` (explicit-support dicts), emit S10.

## Ruling C3 limit (one sentence)

Even given this lot's exact lot lines and the adjoining lots' lot-line types, the program has no code yet that takes those facts and works out the rear yard beyond the waiver area, so closing the missing-information gap is necessary but not sufficient - the rule itself is still owed work (to be recorded in the backlog by the orchestrator).

## What is NOT changed

No rear-yard figure anywhere (value_states or geometry.yards or any export). No overlay code other than C2-2 and no district other than R6B (both keep the generic/blanket text). No other status-strip item or label. `geometry.py`, `result_way_conditions.py`, `result_way_inputs.py`, the engine and every schema read-only. No schema const/enum/version change. No switch turned on. No route-notice or frontage-line wording (C9). No apps/web source file. The schema description example and a `compare_rows.py` comment still say "Zoning maximum" (illustrative, out of this task's paths - C4).

## Red proofs (before the fixes)

- Committed document at the claim head: rear-yard reason = "This lot has a recorded commercial overlay (C2-2); an independent reading of the commercial-overlay rear-yard rule for an all-residential building is owed before this result may be shown."; gap_kind `work_owed`; status_strip[0].text = "Zoning maximum"; geometry.yards carried the same overlay reason with reason_kind `rule_not_implemented`.
- Geometry defect: `pytest --runxfail ...::test_db199a_withheld_height_figure_leaks_into_geometry_known_defect` FAILED with `AssertionError: withheld height figures still in geometry: [55.0]` (the withheld max building height 55 remained in geometry.envelope.tiers[0].top_ft).

## Mutation proofs (one per pinned branch; each applied in place, run, reverted exactly)

| mutation | test that went RED |
|---|---|
| ruled reason's last sentence -> old "...is not settled." | truth_table::test_s3_corner_distance_fails_angle_holds; facts_area_overlay::test_s1_... (both failed) |
| beyond-branch kind -> `WORK_OWED` | truth_table::test_s3_... + 28 rows of ::test_the_way_and_kind_of_every_result_in_every_state_is_pinned (29 failed) |
| overlay rear-yard row -> `supported=False` | bridge_overlay::test_every_family_including_the_rear_yard_is_supported; ::test_the_built_statement_matches_the_table; engine_bridge::test_s8_... (3 failed) |
| strip[0] label -> "Zoning maximum" | c6_c11::test_status_strip_first_item_is_preliminary_zoning_results |
| envelope NOT cleared on withheld height (coverage only) | emit::test_db199a_...; emit::test_s11_flood_zone_corner_height_withheld_envelope_cleared (2 failed) |
| combined-reason order swapped (coverage, height) | emit::test_s12_envelope_both_height_and_coverage_withheld_combined_reason |

## Checks (direct exit codes)

- (a) `python -m ruff check .` (services/api): exit 0 ("All checks passed!").
- (b) `pytest -q ... tests/scenario/three_answers tests/journey tests/api/test_results_read_api.py tests/drawings/kit tests/cad tests/documents/test_pdf_content.py` (no update var): exit 0; **1474 passed, 2 skipped** (claim head: 1459 passed, 2 skipped, 1 xfailed - the xfail now passes plus the new scenarios).
- (c) `npx vitest run` the six website test files (apps/web): exit 0; **8 files, 199 passed** (unchanged count).
- (d) `python3 tools/modularity_check.py --check` (repo root): exit 0; failures 0, warnings 30 (unchanged). Line counts: `result_ways.py` 635 -> 662; `three_way_document.py` 415 -> 444 (neither is in the warnings list).
- (e) `grep -c "Zoning maximum" services/api/app/scenario/three_answers/explanations.py` = **0** (exit 1 = no match, intended). Old words still stand only in: `packages/contracts/schemas/v1/results.schema.json` and `services/api/app/_contract_schemas/v1/results.schema.json` (schema DESCRIPTION example - C4, out of paths) and `services/api/app/contracts/compare_rows.py` (a code comment - out of paths); plus hand-authored fixtures and the apps/web dashboard string "Zoning maximum not available" (a different screen, C4). All left intentionally.
- (f) red + mutation proofs + regeneration diff: above.
- (g) `git status --porcelain` and `git diff --name-status <base> HEAD`: only the allowed paths (15 files + this report). No forbidden path, no file outside allowed paths.

## For the reviewer
- Verify the ruled texts char-for-char against the named case rows (claims no more than them; no section number; never "professional review"/"qualified").
- Confirm the fixture diff is exactly the three expected places and the snapshots only the rear-yard note (geometry.envelope on the recorded lot unchanged - S15).
- Confirm the signature change is ONLY position 16 `Wo`->`Wm` (rear yard) across the 28 states.
- The full server suite and the browser tests are CI's on the exact pushed head.
