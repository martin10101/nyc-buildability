# M5-T157 producer report (backend-engineer builder; both returns kept unchanged)

Integrated by cherry-pick into task/wave23-density-zoning-lot as 9e19afac and 754def4e (every file LF-equal to the builder's final commit 6cbbf715). NB-05 revision 2 was written by the orchestrator from section 7b (a6aff342). The builder's section-8 blocker was resolved by scope correction 2 and its second return.

## Return 1

<!-- saved unchanged by save_return.py from agent-afe9ecd06b2ea38b6.jsonl, entry 2026-10-11T05:29:01.004Z, sha256 3675b7c8554f04b5a460a10789645f4f7a2945d46359fb3f2d3afc1647c26417 -->
# M5-T157 (builder) producer report — DB-231 special density area from the record

**Worktree:** /root/project/nyc-buildability/.claude/worktrees/agent-afe9ecd06b2ea38b6
**Branch:** worktree-agent-afe9ecd06b2ea38b6 (reset to contract head f369b7e8 at start)
**Commit:** b9b5547e6 "M5-T157 (builder): special density area read from the city's record (DB-231)" — 39 files, +1348 / -376.

**Requested status: BLOCKED** on ONE out-of-scope test file that is now red because of this (correct) behaviour change and that R8 forbids me to edit. All in-scope work is complete, committed, and green. Exact remedy below (§8). Everything else is done; the block is mechanical.

---

## 1. Starting point: the previous builder's patch
Applied `T157-builder-unfinished-0423.patch` (git apply --check clean, 39 files). I read every hunk, opened the primary sources, and re-derived every expected value from the law myself. I found the patch correct and kept all of it; I made **no** correction to any hunk. I then independently re-verified: regenerated all snapshots with the UPDATE_* switches (byte-identical to the patch — numstat matched exactly: journey json 47/11, dxf 1/1, svg 18/18), re-ran all checks, and proved the tests by mutation.

## 2. Primary sources opened (not the brief's summary)
- `docs/research/zr-snapshots/v1/zr-12-10-special-density-areas.snapshot.json` — two special density areas: (a) Manhattan Core; (b) Special Downtown Brooklyn District. content_digest `e8029ab3…f401b6`.
- `…/zr-12-10-manhattan-core.snapshot.json` — "Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8." digest `2c04132a…c59c56`. (No per-term last-amended stamp; noted in the snapshot.)
- `…/zr-12-10-special-downtown-brooklyn-district.snapshot.json` — "…designated by the letters 'DB'…". digest `ae66c93e…d7dd2d`. **This is where "DB" comes from.**
- `…/zr-23-52.snapshot.json` — factor **680**; "Fractions equal to or greater than three-quarters … considered to be one dwelling unit"; (a)(1) no factor in special density areas. digest `f48f1ddc…b908ac`.
- `services/api/tests/fixtures/pluto/F08_api_views_columns_snapshot.json` (dataset 64uk-42ks): `cd` = three digits, first = borough code, last two = CD/JIA number; JIAs incl. 164 Central Park; Marble Hill cd 207/208 (Bronx-serviced), borocode 1 (legally Manhattan); `spdist1/2/3` = text, ">=10% of tax lot" rule, blank = not in a special district, co-equal districts joined by "/", "See Appendix A for valid values".

All three ZR digests in `special_density_geography.py` match the snapshots above (also enforced by `test_each_law_capture_digest_matches_the_committed_snapshot`, passing).

## 3. R1–R7 and D-094 R033/R034/R035 → code & tests

**R1 / D-094 R033** (ZR 12-10 names Manhattan Core + Special Downtown Brooklyn): pure fold `services/api/app/scenario/three_answers/special_density_geography.py::decide_special_density`. IN = cd 101–108 OR a "DB" special-district token (spdist split on "/"); NOT IN = Manhattan-Core-no AND every spdist column read with none "DB"; NOT KNOWN otherwise (column not read/untrusted; Manhattan with unusable cd; cd 164/JIA/unrecognised; cd 101–108 contradicted by a non-Manhattan borocode). "Not read" never "no"; either IN signal alone suffices. Tests `tests/scenario/three_answers/test_special_density_geography.py`: `test_cd_101…_is_in`, `test_cd_108…_is_in`, `test_cd_109/112…_is_not_in`, `test_marble_hill_cd_207_is_not_in`, `test_queens_benchmark_cd_411_is_not_in`, `test_special_district_db_token_is_in`, `test_split_special_district_value_xx_slash_db_is_in`, `test_special_district_db_token_overrides_an_unknown_community_district`, `test_brooklyn_without_db_is_not_in`, `test_special_district_columns_not_read_is_not_known`, `test_community_district_served_empty_is_not_known`, `test_cd_164_joint_interest_area_is_not_known`, `test_contradiction_cd_105_borocode_3_is_not_known`, `test_unrecognised_cd_value_is_not_known`, `test_nothing_read_is_not_known`, `test_each_law_capture_digest_matches_the_committed_snapshot`. Fact-gathering: `result_way_facts.gather_special_density_record` (reads cd/borocode/spdist1-3, four column states, splits on "/"), tests `test_result_way_facts.py`.

**R2 / D-094 R034** (record wins; one decision drives engine + way; invariant): combination table `result_way_bridge._density` (9 record×statement combos → EVIDENCE_IN/NOT_IN_ONE, USER_STATEMENT_NOT_IN_ONE, RECORD_AND_STATEMENT_DISAGREE, NOT_GIVEN). The ONE `DensityKnowledge` drives (a) the shown way in `result_ways._unit_standard_way` and (b) the engine condition via `result_way_engine_bridge._DECISION_BY_KNOWLEDGE` → `engine_conditions.special_density`. Invariant test `test_result_ways_input_states.py::test_m5t157_engine_not_in_one_iff_the_unit_limit_is_shown` (parametrized over all `DensityKnowledge`). Combination/record-wins tests: `test_result_way_bridge.py::test_user_statement_never_overrides_the_record_s5`; `test_engine_conditions.py::test_density_*`; `test_result_ways_input_states.py::test_density_record_and_statement_disagree_withholds_missing_information`. D-094 R034 implementation-limit-vs-legal-unknown separation is honoured: NOT KNOWN from "columns not read / can't be read" is withheld as the limit-is-not-yet-usable case, distinct from a legal unknown.

**R3 / D-094 R035** (conditional ceiling with always-present zoning-lot condition; never settled; kept apart from the apartment estimate): `result_ways._zoning_lot_condition` (KIND_UNCHECKED_CONDITION, never removed) + `_unit_standard_way` EVIDENCE_NOT_IN_ONE → `Conditional`. Apartment estimate stays separate (law-examples asserts `doc["unit_estimate"]["status"]=="not_available"`). The 29-unit figure is a Conditional ceiling tied to the zoning-lot condition — never a confirmed entitlement (R035). Tests `test_result_ways_input_states.py::test_density_evidence_not_in_one_is_a_conditional_ceiling_with_the_zoning_lot_condition`, `test_result_ways_truth_table.py`.

**R4** (law-derived values): benchmark 20,150/680=29.63→29; interior made-up lot 10,710/680=15.75→**16** (exactly the 0.75 round-up boundary — the "gives 30" direction); 20,150 drop direction = 29. Rule rounding (factor 680, 0.75) tested by `tests/rules/test_round_threshold_op.py` + `test_r6b_coverage_yard_units.py` (r6b_dwelling_units rule, forbidden to edit). Scenario expected values in `test_results_read_law_examples.py` are asserted against reference-case rows (`real-lot#L6`=29, `interior-lots#P5-units`=16), not a program run.

**R5** (regenerate + explain changed expectations): see §5.

**R6** (review register): `render_review_register.py --check` PASS. Five calc entries sharing result_ways.py each got a new combined code_identity, revision bump, last_changed 2026-10-11, and an `implementation_changed` HISTORY event (events 39–43). calc-legal-dwelling-unit-limit (rev 4) and calc-first-building-option-complete (rev 10) rewritten (conditional-ceiling behaviour, the DB token, the 10% caveat, the per-tax-lot-vs-zoning-lot standing condition). Evidence `.txt` run logs refreshed. No rule file under rulesets/ touched.

**R7** (NB-05): not edited (left for you). Notes in §7.

## 4. Files changed (39, all within allowed_paths — verified programmatically)
New-behaviour production (8): special_density_geography.py (+239), result_way_facts.py (+108), result_way_bridge.py, result_ways.py, engine_conditions.py, result_way_engine_bridge.py, result_way_inputs.py, three_way_scope_lines.py. `results_request.py` NOT changed — it already accepts `special_density_statement` from M5-T137. NB-05.json NOT changed (R7).
Tests (16 in-scope): test_special_density_geography.py, test_result_way_facts.py, test_result_way_bridge.py, test_result_ways_input_states.py, test_result_ways_truth_table.py, test_three_answers_three_way_emit.py, test_engine_conditions.py, test_results_read_law_examples.py, test_215_16_northern_journey.py, test_zoning_rule_review_register_calculations.py, + 5 web tests (journey-215-16-northern, results-contract-checks, presented-notices, presented-results, three-answers).
Fixtures/snapshots: recorded_215_16_northern_journey.json, .site_plan.svg, .dxf.
Register/docs: register.json, REGISTER.md, HISTORY.md, 5 calc .md, 5 evidence .txt.

## 5. Changed expectations (file · old → new · why)
- `recorded_215_16_northern_journey.json` · legal_unit_limit_standard way=withheld (no density evidence) → way=conditional, value **29.0**, zoning-lot condition · benchmark record (Queens cd 411, no DB) now resolves NOT IN, so the limit shows (20,150/680=29.63→29).
- same file · scope/assumptions/3 (special_density_area): "Not known…withheld" → "outside both special density areas…conditional ceiling on the zoning lot" · engine now given "not in one" from the record.
- `recorded_215_16_northern_journey.site_plan.svg` · the special-density scope note text rewritten + follow-on notes shifted +10px (more lines) · same scope-line change, re-laid-out.
- `recorded_215_16_northern_journey.dxf` · one note line "Special density area Not known assumed …withheld" → "Special density area No city_records …conditional ceiling on the zoning lot" · same.
- `test_results_read_law_examples.py` · benchmark unit limit withheld → conditional 29 (T4); interior-lot withheld → conditional 16 (T5/S13); T8 statement-in-one now DISAGREES with the record → withheld missing_information "does not override"; S13-without-statement withheld → conditional 16 (the "S4 withheld inversion") · record now decides.
- `test_215_16_northern_journey.py` · unit-limit assertions withheld → conditional 29 · same.
- `test_result_way_bridge.py` / `..._input_states.py` / `..._truth_table.py` / `test_three_answers_three_way_emit.py` / `test_engine_conditions.py` · added the new DensityKnowledge/DensityDecision states, the invariant, the record-wins/disagreement cases; local `_WITHHELD_ON_BENCHMARK` drops legal_unit_limit_standard · new behaviour.
- `register.json` + 5 calc .md + 5 evidence .txt + HISTORY.md + REGISTER.md · revisions, code identities, history events, rewritten dwelling-unit/first-option entries · R6.
- 5 web tests · journey-fixture consumers updated to assert conditional 29 and the inverted S4 · R5.

## 6. Self-checks (lanes venv: ruff 0.13.0, pytest 9.0.3, py 3.12.3)
- `ruff check .` (services/api): **All checks passed!** exit 0.
- `pytest -q tests/scenario tests/api tests/journey tests/rules tests/drawings tests/cad`: **2 failed, 5383 passed, 8 skipped** (257s). The 2 failures are the out-of-scope file in §8; every in-scope test passes.
- `render_review_register.py --check`: **register check PASSED (no issues)**.
- `research_record_check.py --check`: **PASS**; NB-05 `code_current=False review_state=stale` — expected after this change (reported, not failed), exactly as the brief predicted.
- `modularity_check.py --check`: exit 0, failures 0, 32 warnings (all pre-existing; new module not flagged; result_ways.py is a pre-existing warn, not a failure).
- Web (apps/web, after `npm ci`): `npm run lint` 0 errors (2 pre-existing warnings in untouched files); `npm run typecheck` exit 0; `npx vitest run` full suite **128 files / 2641 tests passed** (I ran the whole suite, not just the 5 changed files, to catch any other journey-fixture consumer — none red). No browser e2e run (CI's job); ports 3000/3001/8000 never touched.

## 7. Mutation proofs (break → failing test → restore via git checkout; tree clean after each)
1. **Fold IN condition** — `MANHATTAN_CORE_COMMUNITY_DISTRICTS = range(101,109)` → `range(101,108)` (drops cd 108). `test_cd_108_manhattan_core_is_in` FAILED: `_area(cd=108,borocode=1)` returned NOT_IN instead of IN. Restored.
2. **Record-wins** — in `_density`, NOT_IN + says-in-one returned `EVIDENCE_IN_ONE` (statement overrides) instead of `RECORD_AND_STATEMENT_DISAGREE`. `test_user_statement_never_overrides_the_record_s5` FAILED: disagreeing gap_kind `missing_information` → `work_owed`. Restored.
3. **Invariant** — `engine_conditions.special_density(RECORDED_NOT_IN_ONE)` returned `Derived(True…)` instead of `False`. `test_m5t157_engine_not_in_one_iff_the_unit_limit_is_shown[EVIDENCE_NOT_IN_ONE]` FAILED: engine_value True while way 'conditional' (shown). Restored.

## 7b. NB-05 notes (R7 — for you to revise the record)
- **New code paths:** `services/api/app/scenario/three_answers/special_density_geography.py` (the fold, the ZR 12-10 captures/digests); `result_way_facts.gather_special_density_record`; `result_way_bridge._density`; `result_ways._unit_standard_way`/`_zoning_lot_condition`; `result_way_engine_bridge._DECISION_BY_KNOWLEDGE`/`_density_decision`; `engine_conditions.special_density` + `DensityDecision`; `three_way_scope_lines._scope_statement` (special_density branch).
- **Regression cases → tests:** (1) Queens lot, no special district, NOT IN → `test_queens_benchmark_cd_411_is_not_in`, `test_result_way_bridge.py::test_benchmark_lot_s1`. (2) Manhattan CD 1–8 IN / CD 9–12 NOT IN → `test_cd_101…_is_in`, `test_cd_108…_is_in`, `test_cd_109/112…_is_not_in`. (3) Special Downtown Brooklyn (DB) IN → `test_special_district_db_token_is_in`, `test_split_special_district_value_xx_slash_db_is_in`. (4) special district not read → not known, withheld → `test_special_district_columns_not_read_is_not_known`. (5) rounding .75↑ / <.75↓ → interior-lot 16 (`test_t5_made_up_interior_lot_p5`), benchmark 29 (`test_t4_recorded_lot_three_ways`), rule tests `test_round_threshold_op.py`. (6) senior housing no factor → `result_ways._unit_qualifying_senior_way` + its truth-table coverage.
- **What the record should now say:** revise to **revision 2**; the geography is now **read from the city's record** (not only the hand-worked example); `implementation.code_paths` += the modules above; `implementation.code_identity` re-fingerprinted (engine_conditions.py changed; r6b_dwelling_units.rule.json unchanged); add conditions: (i) PLUTO lists a special district only at ≥10% of the tax lot, so a DB sliver can read as none; (ii) the record is per **tax lot** while ZR 23-52 sets the limit on the **zoning lot** (the always-present condition); add the **open item** that the exact PLUTO token spelling of "DB" is not confirmed from captured evidence (Appendix A not captured, OQ-5) — the match rests on the ZR 12-10 map designation + the dictionary token semantics (G1 to probe). A fresh independent review (G1/G3/G4) should cover revision 2.

## 8. OUT-OF-SCOPE BLOCKER (R8 — not edited; your decision needed)
`services/api/tests/scenario/three_answers/test_result_way_engine_bridge.py` is a direct consumer of the changed behaviour (it exercises the benchmark through `run_engine_and_result_ways`) but is **NOT in M5-T157 allowed_paths**. Two of its tests now assert the OLD (withheld) behaviour and fail; they are the only red in the whole suite:
- `test_s1_benchmark_carriers_reach_gather_through_adapter` — its local `_WITHHELD_ON_BENCHMARK` (lines 160–165) still lists `legal_unit_limit_standard`, now Conditional.
- `test_s9_user_density_statement` — premise invalid: the benchmark record now resolves "not in one", so with/without an agreeing statement both give the record's zoning-lot Conditional (not KIND_USER_STATEMENT); the user-statement path must be exercised with a record-NOT-KNOWN profile (e.g. a bare profile).

**Exact remedy (mirror the already-updated in-scope `test_result_way_bridge.py`):**
- Edit the local `_WITHHELD_ON_BENCHMARK` to drop `"legal_unit_limit_standard"` (keep the two qualifying unit limits), and after the `_WITHHELD_ON_BENCHMARK` loop in test_s1 add: `unit=_way(ways,"legal_unit_limit_standard"); assert isinstance(unit, Conditional); assert any("zoning lot" in c.assumption for c in unit.conditions)` (mirrors test_result_way_bridge.py lines 198–202; confirm `Conditional`/`KIND_UNCHECKED_CONDITION` imports).
- Rewrite test_s9 to mirror `test_result_way_bridge.py::test_user_statement_never_overrides_the_record_s5` (record decides: with_agreeing+without → Conditional zoning-lot, never user_statement kind; disagreeing → Withheld missing_information), OR exercise USER_STATEMENT_NOT_IN_ONE with a record-NOT-KNOWN profile.

Please either **add this file to the task scope** (so a builder applies the above) or apply the two edits directly. No other consumer is red (full py + full web suites confirmed).

## 9. What I could not verify / limitations
- **Exact PLUTO "DB" token spelling**: not confirmable from captured evidence — PLUTO Appendix A (valid special-district values) is not in the repo (OQ-5). The module matches the ZR 12-10 map-designation letters "DB" plus the dictionary's "/"-split token semantics; documented in the module docstring and flagged for the G1 probe. Same for the module's per-borough CD-number ceiling (18) — administrative geography, flagged for G1, never used as a zoning rule.
- **No legal/professional verification**: per ADR-007 this ships as an unreviewed draft with its law link; every ZR citation remains not-professionally-reviewed. The 29/16 figures are Conditional ceilings, never confirmed entitlements (R035).
- Snapshot regeneration proved byte-identical to the patch; I did not change any patch hunk.
- Lands with DB-232 in one wave (per packet) — not to be merged alone.

END-OF-REPORT


## Return 2 (scope correction 2)

<!-- saved unchanged by save_return.py from agent-afe9ecd06b2ea38b6.jsonl, entry 2026-10-11T05:36:03.238Z, sha256 6b4f38f3e2df4df54ddc374b06ab1ee143c6dd969134aab455f153d542cad6e0 -->
# M5-T157 (builder) — scope-correction-2 remedy applied (test_result_way_engine_bridge.py)

**Commit:** `6cbbf7153f6551cf536e22f3db32fc68c2207d1a` on top of b9b5547e6 (worktree /root/project/nyc-buildability/.claude/worktrees/agent-afe9ecd06b2ea38b6; working tree clean).

**Diff stat:** `1 file changed, 39 insertions(+), 8 deletions(-)` — `services/api/tests/scenario/three_answers/test_result_way_engine_bridge.py` only.

## What changed (real behaviour, values from the law/record)
- `_WITHHELD_ON_BENCHMARK` drops `legal_unit_limit_standard` (benchmark record = Queens cd 411 → outside both special density areas → the limit is a conditional ceiling, not withheld).
- `test_s1_benchmark_carriers_reach_gather_through_adapter`: after the withheld-loop it now asserts the unit limit is `Conditional`, carries the always-present `"zoning lot"` condition, and is never `KIND_USER_STATEMENT` (the record decides).
- `test_s9_user_density_statement` rewritten:
  - Record-decides case on the benchmark (kept): with an agreeing statement (True) or no statement → `Conditional` zoning-lot ceiling, never the user_statement kind; a disagreeing statement (False) → `Withheld` (a statement never overrides the record).
  - User-statement path exercised with a record-NOT-KNOWN `_bare_profile()` (every column served empty, so the community district cannot be read): statement True → `Conditional` with `KIND_USER_STATEMENT`; no statement → `Withheld`; the statement never enters a gathered fact record.

## Self-checks (lanes venv)
- `cd services/api && ruff check .`: **All checks passed!** (exit 0). [Note: fixed two E501 line-length flags in my new comment/docstring before this.]
- `cd services/api && pytest -q -p no:cacheprovider tests/scenario/three_answers tests/api tests/journey`: **1717 passed, 2 skipped** (113.57s, exit 0). cd back done.

## Mutation proof (assertion target)
- Reverted the s1 edit's target: put `"legal_unit_limit_standard"` back into `_WITHHELD_ON_BENCHMARK`.
- `pytest …::test_s1_benchmark_carriers_reach_gather_through_adapter` → **FAILED** at line 210: `assert isinstance(_way(ways, key), Withheld)` raised because the way is `Conditional(... kind='unchecked_condition', "If this tax lot is the whole zoning lot…" …, way='conditional')`.
- Restored (removed the key again); test_s1 **passes** (1 passed); no MUTATION marker left; only the one file modified.

Record NB-05 (D-093) unchanged in this commit (orchestrator revises it per my earlier §7b notes); ports 3000/3001/8000 untouched.

END-OF-REPORT
