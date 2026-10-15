# M5-T167 producer report (backend-engineer) — round 2

Requested status: **needs_split** (a bounded scope correction is required to close the benchmark-regen
fan-out). The in-scope increment (steps 3-7 + the regeneration) is complete, self-consistent and green
within the task's `allowed_paths`; every documented check passes except the whole-suite runs, whose only
red is **5 out-of-scope / forbidden consumer tests** that assert the OLD "benchmark is 1.4.0, rear yard is
the open check" behaviour — exactly the behaviour R037/R079/R136/R039 require changing. Details and exact
fixes for those 5 files are in "Out-of-scope fan-out" below.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/wf_1fc04da7-475-1`
Branch head at start / commit parent: `61415679c26b8992e86c4fbfe4761c6804c81d47` (task/wave25-rear-yard-short-block).
Increment A (G-6 isolation + block-frontage measure, 474c8ee3) was already integrated on the branch.

## Starting point (the saved unfinished round-2 diff)

`git apply --3way .../unfinished-M5-T167-round2/tracked.diff` applied cleanly (11 files, all hunks).
I re-checked every line against the packet and the R6B reference case and KEPT the structure, with
these corrections (treat-as-unreviewed, THREE RULES):

- `rear_yard_checks.py` `_fmt` rounded `229.996` to `"230.00"` via `f"{v:.2f}"` — a direct S1 violation
  ("229.996 is never printed as '230.00'"). Added `_fmt_measure` (never rounds a separation UP across the
  two-decimal boundary) and used it for the short-dimension separation display. Angles/reaches keep `_fmt`
  (the benchmark's "89.7"/"144.6" are byte-unchanged; the benchmark (b) is not_known, carries no number).
- The (c)(3) not_known text said "…is not captured" and a combined condition said "Capturing and reading…"
  — internal vocabulary RULE 3 forbids. Reworded to "…are not recorded for this lot" and "Reading the
  adjoining zoning lots' recorded lot-line kinds". The benchmark fixture was regenerated for this text.
- The two synthetic fixtures' `building_alternatives[0].not_checked` still listed "The rear yard beyond the
  corner" (the pre-step-6 wording); re-derived to drop it so their shared 1.4.0 core equals the regenerated
  journey core (the only core drift). DB-262 input_facts (9,800→10,075; 10,120.5→10,387.99) were already
  fixed in the saved diff for synthetic_rear_yard; the 0→182.5 rear_yard_100ft_line is KEPT untouched.

Everything else in the saved diff was kept as-is.

## What changed, per step

- Step 3-4 (`rear_yard_checks.py`, new; `result_way_engine_bridge.py`, `three_way_document.py`): the
  ZR 23-344 (a)/(b)/(c)(3) checks combined into the additive contract-1.5.0 `rear_yard` block, `input_facts`
  and rear-yard constraint lines. `_apply_rear_yard` attaches them and sets `contract_version` to 1.5.0 only
  when an analysis is threaded; `rear_yard_analysis=None` keeps every other emit byte-identical (opt-in on a
  DCM street window via `run_engine_and_result_ways_from_evidence(..., street_data=...)`). `three_way_document.py`
  net-shrinks 679→637 SLOC across the whole task (increment A 679→612; this round +25), still below JUSTIFY;
  `result_ways.py` untouched at 622; `rear_yard_checks.py` 332, `block_frontage.py` 167. modularity_check --check exit 0 (S20).
- Step 5 (`readers.py`): `_apply_rear_yard_open_item` rewrites the appendix rear-yard open item from the
  document's own `rear_yard` block on a 1.5.0 document; a 1.4.0 document carries no block, so it is a no-op
  and stays byte-identical to M5-T165's open-check wording (R136/S23).
- Step 6 (`first_option_results.py`): removed the `_NOT_CHECKED_REAR_YARD` "The rear yard beyond the corner"
  item from `_not_checked` (it is now applied by the engine at the lot level, not a not-checked item).
- Step 7 (register/rule/records):
  - `register.json` — the two CALCULATION entries whose cited code module `three_way_document.py` changed
    (`calc-preliminary-apartment-estimate`, `calc-first-building-option-complete`) get the new module sha256
    `2caaebaa…`, recomputed `code_identity_sha256` (`1af34fa4…`, `4f05b238…`), `automated_tests.status` set to
    "Not run" (the sanctioned state after a code change; test_changed_code_module_demands_automated_tests_not_run),
    revision bumps (10→11, 11→12), and two `calculations_history` events (seq 50, 51, implementation_changed,
    no human verdict). This fixes the branch-red register check the round-2 brief flagged.
  - `register.json` r6b-rear-yard-corner-waiver RULE entry: title, applies_where and interpretation broadened
    to name (a)/(b)/(c)(3); the stale "withheld (not known) pending the overlay reading" text replaced with the
    conditional (a)/(b)/(c)(3) reading (S14). revision 2→3, one `history` event (seq 27, interpretation_changed).
    The DSL rule file r6b_rear_yard_corner_waiver.rule.json is UNCHANGED (its (a) reading and digest are byte-stable;
    (b)/(c)(3) live in rear_yard_checks.py) — so the golden tests test_r6b_a02b_golden etc stay green.
  - `REGISTER.md`/`HISTORY.md`/`calculations/*.md`/`rules/r6b-*.md` rendered by `render_review_register.py --write`
    (only those 5 files changed). `--check` exit 0.
  - Evidence file `docs/zoning-rule-review/evidence/r6b-rear-yard-short-block.txt` populated (the short-block law,
    the two independent readings, the real-lot outcome, a labelled unreviewed draft).
  - `NB-03` → revision 3: rear_yard_checks.py added to code_paths (current sha), gaps (b) and (f) marked RESOLVED
    2026-10-14, a dependency_assessment line; research_status stays `interpretation_awaiting_review` (the reading
    is still a conditional unreviewed draft — I did NOT promote it, D-093/ADR-007). README/RESEARCH_REQUESTS were
    NOT edited: NB-03's status VALUE is unchanged (the status column stays accurate). See "Assumptions".
  - `NB-01` → revision 5 (G-6 isolation): three_way_document.py/result_way_bridge.py/readers.py refreshed to
    current sha, the two new modules three_way_zoning_lot.py/result_way_zoning_lot.py added to code_paths, a
    dependency_assessment line recording the isolation decision.
  - `NB-05` → revision 4: code_identity refreshed (result_way_bridge.py + result_way_engine_bridge.py changed),
    a dependency_assessment line; the special-density decision and 680 arithmetic unchanged.
  - research_record_check.py --check exit 0 (NB-01/03/05 code_current True; stale review_state is non-failing).
- The regeneration: the benchmark journey (`recorded_215_16_northern_journey.json`) was regenerated by the
  repo's own path `UPDATE_JOURNEY_FIXTURE=1` through `tests/journey/test_215_16_northern_journey.py`
  (never hand-edited). It gains `rear_yard` + `input_facts` and flips to 1.5.0. The two synthetics were
  re-derived (DB-262 input_facts, the not_checked drift; 0→182.5 kept). The strip test
  (`test_results_contract_1_5_0.py`, in scope) was reworked (DECISION 3): strip the 1.5.0 blocks from BOTH
  the synthetic and the journey, compare the shared 1.4.0 cores, assert the journey declares 1.5.0.

The DXF (`recorded_215_16_northern_journey.dxf`) and site-plan SVG snapshots did NOT change (the rear_yard
block does not reach the DXF notes or the engine-sourced site-plan caption); tests/cad and tests/drawings/kit
pass unedited. DB-245 wording is OUT of scope (moved to M5-T180); no "tax map" wording was changed.

## THREE RULES evidence (the dedicated scenario test test_rear_yard_short_block.py)

RULE 2 — input-state tables (one test per state):

(b) short dimension of a block — classify_short_dimension(separation, basis, basis_fixed_by_law):
| separation | basis_fixed_by_law | outcome | test |
|---|---|---|---|
| 229.99 | True | applies | test_short_dimension_state_table |
| 230.00 | True | not_applicable | test_short_dimension_state_table / test_…threshold…strict |
| 230.01 | True | not_applicable | test_short_dimension_state_table |
| 229.996 | True | applies, printed "229.996" (never "230") | test_229_996_is_never_printed_as_230 |
| any (203.13/229.99/260) | False (real lot) | not_known | test_real_lot_short_dimension_is_not_known_whatever_the_measure |
| None | True/False | not_known | test_short_dimension_state_table |

(a) corner waiver — build_rear_yard_analysis → 23-344(a):
| reach | angle | outcome | test |
|---|---|---|---|
| None | 89.7 | not_known | test_corner_waiver_state_table |
| 144.6 | None | not_known | test_corner_waiver_state_table |
| 144.6 | 150.0 | not_applicable | test_corner_waiver_state_table |
| 144.6 | 135.0 | applies | test_corner_waiver_state_table |
| 144.6 | 89.7 | applies (covers only within 100 ft) | test_corner_waiver_state_table |
| 50.0 | 89.7 | applies (whole lot within 100 ft) | test_corner_waiver_state_table |

(c)(3) adjoining side lot line — build_rear_yard_analysis → 23-344(c)(3):
| district | outcome | test |
|---|---|---|
| None / "" | not_known (RULE 1: unknown/empty never read as "no") | test_c3_district_state_table |
| R6B / R12 / R7-1 | not_known (neighbours not recorded) | test_c3_district_state_table |
| R4B / R5 / R3-2 | not_applicable (outside R6-R12) | test_c3_district_state_table |

RULE 1 — no default stands for a fact; optional-fact truthiness tests touched/created: `_in_r6_r12`
(`if not district: return None` — empty/None → not known, proven by test_c3_district_state_table[None, ""]);
`_check_a` (`if angle_deg is None or reach_ft is None`); `build_rear_yard_analysis` emits a recorded/outline
area input_fact only when present and only with a non-empty source title AND date (proven by
test_no_provenance_means_no_input_fact_invented, test_a_missing_area_holds_its_fact_back). No truthiness test
reads an unknown yes/no/number as "no".

RULE 3 — texts guard (test_texts_are_plain_user_texts over 5 analyses): forbids `captur*`, `gap (`,
`reading 1/2`, `reference case`, `milestone`, `m5-t`, `the caller`, `is built`, `step-p`, `db-`, `schema`,
`fixture`; test_no_unconditional_no_rear_yard_anywhere requires every "no rear yard" be qualified by
"within 100 feet"; test_checks_name_b_and_c3_besides_the_corner_waiver (S11); the DOB disclaimer is on every
check. The guard found and I fixed the "captured"/"Capturing" jargon (see Starting point).

S24 — every input_fact equals the value the calculation uses on its basis, no second figure per basis; every
emitted constraint line within the lot (not_known → no geometry): test_input_facts_equal_the_calculation_values_one_per_basis,
test_constraint_lines_carry_no_geometry_when_not_established, and the red/green mover
test_recorded_area_fact_moves_when_the_input_moves.

## Benchmark lines changed (cited)

The regenerated benchmark changes only where the engine output moved, each from the R6B reference case / law:
- NEW `rear_yard` block: (a) applies — angle ~89.7°, reach ~144.60 ft (real-lot.json L9/L12; corner-reach case);
  (b) not_known — the measurement basis is unresolved law (short-block-rear-yard.md row b-measurement-basis);
  (c)(3) not_known — neighbours' lot-line kinds not recorded (NB-03 gap e); combined not_known / Conditional,
  never "no rear yard", ZR 23-344(b)/(c)(3) linked (S13; short-block-rear-yard.md real-lot-z1/z2).
- NEW `input_facts`: recorded_lot_area 10075 sq_ft (administrative_record; real-lot.json L1 = 20150/2.0),
  lot_outline_area 10387.99 sq_ft (gis; real-lot.json "Tax-map outline area", Shape__Area) — DB-262 corrected.
- NEW `geometry.constraint_lines`: rear_yard_100ft_line and corner_area both not_known (no geometry) — the
  whole lot is within ~99.97 ft of the Northern Blvd line, so a 100-ft line lies outside the lot (S24).
- `contract_version` 1.4.0 → 1.5.0 (reverse version binding).
- `building_alternatives[0].not_checked` loses "The rear yard beyond the corner" (step 6).

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider)

- `cd services/api && python -m ruff check .` — **exit 0** ("All checks passed!").
- tests/rules — **1158 passed, 1 failed** (the 1 is out-of-scope test_zoning_rule_review_register.py::test_s13,
  below). Tail: `/tmp/claude-0/M5-T167/round2-rules.log`.
- WHOLE `services/api` `python -m pytest -q -p no:cacheprovider` — **9762 passed, 8 skipped, 5 failed**
  (all 5 out-of-scope/forbidden consumers, below). Tail: `/tmp/claude-0/M5-T167/round2-api-pytest.log`.
- documented subset (tests/scenario/three_answers tests/spatial …) — 2316 passed / 2 skipped except the same
  out-of-scope reds; test_rear_yard_short_block.py 41 passed; test_results_contract_1_5_0.py 71 passed.
- `.github/scripts/validate_contracts.py` — **0 failures** (both synthetics + the regenerated journey OK).
- `pytest .github/scripts/tests` — **24 passed**.
- `render_review_register.py --check` — **PASSED (no issues)**.
- `tools/research_record_check.py --check` — **PASS** (exit 0).
- `tools/modularity_check.py --check` — **exit 0** (pre-existing WARN signals only; net-shrink on the two WARN files).
- `scripts/lanes/check_lane_paths.py --coverage` — **PASS** (10478 files, exit 0).
- apps/web (worktree `npm ci` ok): `npm run lint` — **0 errors** (2 pre-existing warnings); `npm run typecheck`
  — **pass**; `npx vitest run src/lib/architect src/lib/__tests__/results-contract-checks.test.ts` — **407 passed,
  1 failed** (the 1 is out-of-scope results-contract-checks.test.ts journey-1.4.0 assertion, below).

## Mutation proofs (mutate rear_yard_checks.py → run the pinning test → confirm FAIL → restore; restore verified identical)

- M1 (b) real-lot state: disable the `basis_fixed_by_law` early-return → test_real_lot_short_dimension_is_not_known… **1 failed**.
- M2 strict "< 230": change `<` to `<=` → test_short_dimension_threshold_is_the_captured_230_strict **1 failed**.
- M3 (c)(3) district: drop R2-R5 from the outside-range prefixes → test_c3_district_state_table **3 failed**.
- M4 input_fact == calc value: emit `0.0` instead of recorded_area → test_recorded_area_fact_moves… **1 failed**.
Baseline 41 passed; final `diff` of source vs backup: RESTORED_CLEAN.

## Out-of-scope fan-out — REQUIRED scope correction (5 consumer tests, none in allowed_paths)

All five assert the OLD "benchmark is a 1.4.0 doc, rear yard = the open check" behaviour and break only because
the benchmark regenerated to 1.5.0 with an applied rear_yard block — the core R037/R079/R136/R039 change. They
are NOT editable by this packet (one is in forbidden_paths; four are not listed in allowed_paths). Requesting a
scope correction to add them (to M5-T167 or a bounded follow-up) with these exact fixes:

1. `services/api/tests/scenario/three_answers/test_wiring_emits_nothing.py` (not listed) —
   `test_s12_entry_emits_the_committed_three_way_fixture`: make `_carriers` return its already-computed `streets`
   and thread `street_data=streets` in `_emit_from_evidence` (mirror the journey test), then flip the assertion
   `document["contract_version"] == "1.4.0"` → `"1.5.0"`.
2. `services/api/tests/rules/test_zoning_rule_review_register.py` (not listed) — `test_s13_…`: its sample history
   events are dated "2026-10-12"/"2026-10-20"; the real register history now ends at the r6b event dated
   2026-10-14, so "2026-10-12" is out of date order. Bump the first sample date to a date ≥ 2026-10-14 (e.g.
   "2026-10-15"); keep "2026-10-20".
3. `services/api/tests/drawings/report/test_constraint_rows.py` (**forbidden_paths**) —
   `test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged` (asserts `has_results_rows(benchmark()) is False`)
   and `test_s1_benchmark_page_one_rear_yard_uncertainty_is_unchanged` (asserts `rear_yard_combined(benchmark()) is None`).
   The benchmark now carries a rear_yard block, so both are now True / non-None. Update them to the applied
   Conditional result, or re-point them at a genuinely-1.4.0 document. (The synthetic-fixture assertions in this
   file — the 182.5 clip line etc — stay green and unedited, as the planner intended.)
4. `services/api/tests/drawings/report/test_report_benchmark.py` (not listed) —
   `test_benchmark_rear_yard_reads_as_the_open_check`: asserts `constraint_text.REAR_YARD_OPEN_CHECK in text`.
   Page 8 now shows the applied result (R136), so update to assert the applied Conditional wording and drop the
   open-check assertion.
5. `apps/web/src/lib/__tests__/results-contract-checks.test.ts` (not listed) — "accepts the committed journey
   document (regenerated contract-1.4.0…)": flip `expect(doc.contract_version).toBe("1.4.0")` → `"1.5.0"` and the
   test title. (It reads the journey AND the synthetics; the synthetic schema-only checks stay green.)

The planner's DECISION 2 under-enumerated these benchmark consumers (M5-T175/M5-T179 moved the benchmark open-check
assertions into test_report_benchmark.py / test_constraint_rows.py; test_wiring_emits_nothing.py and
results-contract-checks.test.ts hold their own journey pins). I did not touch any of them (scope discipline).

### Required collateral outside allowed_paths (committed, flagged)

The brief mandated fixing the branch-red register check, which requires updating the two CALCULATION entries that
fingerprint three_way_document.py. `render_review_register.py --write` therefore regenerates their rendered pages,
and `--check` fails (stale calculation page) unless they are in sync (verified: reverting them reddens --check):
- `docs/zoning-rule-review/calculations/calc-first-building-option-complete.md`
- `docs/zoning-rule-review/calculations/calc-preliminary-apartment-estimate.md`

These two files are NOT in allowed_paths (which lists REGISTER.md/HISTORY.md/rules/r6b-*.md/evidence/* but not the
per-entry calculation pages). I committed them because they are forced, mechanical collateral of the brief-mandated
register fix and --check cannot pass without them. Please add them to allowed_paths in the same scope correction.

## Assumptions / limitations

- NB-03 research_status stays `interpretation_awaiting_review` (not promoted): the reading has open conflicts and
  conditions and is an unreviewed draft (D-093/ADR-007). The packet called NB-03 "the only W25 research_status
  change" — I read this as NB-03 being the only record whose conclusion/gaps substantively advance this wave
  (gaps b/f resolved, rev 3), while NB-01/NB-05 are mechanical code-identity resyncs. Because the status VALUE is
  unchanged, README.md/RESEARCH_REQUESTS.md were not edited. Flagging for the reviewer.
- The r6b DSL rule FILE was NOT changed (only the register entry text), to protect the rule-evaluation goldens; the
  (b)/(c)(3) engine reading lives in rear_yard_checks.py. If the reviewer wants the rule file's own title/limitations
  broadened too, that is a follow-up (it forces a rule_file_sha256 resync + golden recompute).
- The two register calc entries read "Not run" (the honest producer state after a code change); the independent
  gate re-runs them.
- Nothing under `.claude/**` was written; no server/ports/Playwright. Scratch only under `/tmp/claude-0/M5-T167/`.

# M5-T167 producer report (backend-engineer) — round 3

Scope correction 2 (2026-10-14d) added the five benchmark-consumer tests the round-2 regeneration to
1.5.0 left red; round 3 edits ONLY those five test files (plus this report), so the branch goes green.
No production source changed. The round-2 commit 8fa1714c was cherry-picked onto the branch head
04d9975f (clean apply, disjoint-peer bases); round 3 is one commit on top of it. Each changed
assertion follows the R6B reference case, never a program run; the benchmark rear yard stays not
known / Conditional, ZR 23-344(b) linked, never an unconditional "no rear yard".

## Files changed and why the reference case supports each

1. `services/api/tests/scenario/three_answers/test_wiring_emits_nothing.py` (S12). `_carriers` now
   returns its already-computed `streets`, and `_emit_from_evidence` threads `street_data=streets`,
   mirroring the journey test (`test_215_16_northern_journey.py` line 263). With the DCM window
   threaded the wiring path emits the SAME 1.5.0 benchmark the journey test wrote, so the byte-exact
   fixture equality holds; the version assertion flips `1.4.0 -> 1.5.0`. This is a wiring/unchanged
   proof (equality with the committed fixture), never a correctness claim — the rear-yard content is
   pinned in the journey test from the reference case.
2. `services/api/tests/rules/test_zoning_rule_review_register.py` (S13). The sample history event's
   first date `2026-10-12 -> 2026-10-15` so it sorts at or after the real r6b event dated 2026-10-14
   the round-2 register change added (the checker enforces history date order). A TEST-DATA date, no
   behaviour change; the second sample date 2026-10-20 is kept.
3. `services/api/tests/drawings/report/test_constraint_rows.py` — ONLY the two `test_s1_benchmark_*`
   cases (the synthetic cases, the 182.5 line and S12 `..._1_4_0_report_with_maps_draws_no_overlay`,
   stay byte-identical). They pinned the 1.4.0 fall-back (`has_results_rows(benchmark()) is False`;
   `rear_yard_combined(benchmark()) is None`); the regenerated benchmark now carries the engine's
   1.5.0 rear_yard combined row, so each is rewritten to assert the applied result the reference case
   (short-block-rear-yard.md, real-lot-z1/z2) requires: the rear-yard row present, combined
   `state=not_known`/`way=conditional`, its conditions naming ZR 23-344(b) and (c)(3), labelled
   Conditional, ZR 23-344 linked and the open item linked, no number printed, never "no rear yard".
4. `services/api/tests/drawings/report/test_report_benchmark.py` — ONLY
   `test_benchmark_rear_yard_reads_as_the_open_check`, renamed
   `..._reads_as_the_applied_conditional_result` (every other case kept). Page 8's appendix rear-yard
   open item now reads the engine's applied ZR 23-344 result (R136), located by the reader's own item
   number (not program wording): labelled Conditional, naming ZR 23-344(b) and (c)(3), the conditions
   (the adjoining lots' lot lines) named, no open-check / "not yet checked" text, never "no rear
   yard"; ZR 23-344 is linked in the report where the reading is shown (pages 1/3 — the appendix item
   is a short plain-text summary by design, so the link is asserted on the whole HTML).
5. `apps/web/src/lib/__tests__/results-contract-checks.test.ts` — the journey contract-version pin
   `1.4.0 -> 1.5.0` (assertion + test title + the fixture docstring line); the synthetic 1.5.0 and
   schema-only checks are untouched.

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider; from services/api unless noted)

- `python -m ruff check .` — **exit 0** ("All checks passed!").
- `tests/rules` — **1159 passed, exit 0**. Tail: `/tmp/claude-0/M5-T167/round3-rules.log`.
- WHOLE `python -m pytest -q -p no:cacheprovider` (the integration gate) — **9767 passed, 8 skipped,
  exit 0** (round 2 was 9762 passed / 5 failed; the 5 are now green). Tail:
  `/tmp/claude-0/M5-T167/round3-api-pytest.log`.
- `.github/scripts/validate_contracts.py` — **Checked 23 schema file(s); 0 failure(s); exit 0**.
- `pytest .github/scripts/tests` — **24 passed, exit 0**.
- `render_review_register.py --check` — **PASSED (no issues), exit 0**.
- `tools/research_record_check.py --check` — **PASS, exit 0** (6 records; NB-01/03/05 code_current True).
- `tools/modularity_check.py --check` — **803 files, failures 0, warnings 33 (all pre-existing), exit 0**.
- `scripts/lanes/check_lane_paths.py --coverage` — **PASS, 10483 files, exit 0**.
- apps/web (worktree `npm ci` ok): `npm run lint` — **0 errors, 2 pre-existing warnings, exit 0**;
  `npm run typecheck` — **exit 0**; `npx vitest run src/lib` — **67 files / 1297 passed, exit 0** (a
  first run flaked on the unrelated dashboard "real ledger smoke" test under full-suite load; it
  passes isolated (21/21) and on a clean re-run — not in this task's scope). Log:
  `/tmp/claude-0/M5-T167/round3-web-vitest.log`.

## Mutation proofs (two; both on test_report_benchmark.py's rewritten page-8 case; restored verified)

- M1 (old open-check expectation reverted): flipping the appendix assertion back to
  `REAR_YARD_OPEN_CHECK in visible_text(appendix)` **FAILS** on the 1.5.0 benchmark (the open-check
  wording is gone from page 8) — proves the applied-result assertions are load-bearing. Restored
  (backup == file).
- M2 (reader says "no rear yard"): a scratch edit of `readers._rear_yard_open_effect` to emit
  "…no rear yard is required on this lot." makes the negative assertion
  `"no rear yard" not in low or "…within 100 feet" in low` **FAIL** — proves the no-unconditional-no-
  rear-yard guard is load-bearing. Restored (backup == file; readers.py byte-identical to the cherry-
  pick HEAD).

## Assumptions / limitations

- The page-8 appendix rear-yard open item carries no ZR 23-344 href itself (by design it is a short
  plain-text summary within the word cap); the per-stat link is emitted where the combined row renders
  (pages 1 and 3). The test therefore asserts the link on the whole report HTML and the "(b)/(c)(3)"
  wording and Conditional chip on the located page-8 row.
- No production source changed in round 3; modularity, register and record checks pass unchanged.
- Nothing under `.claude/**` was written; no server/ports/Playwright. Scratch only under `/tmp/claude-0/M5-T167/`.

END-OF-REPORT

---

# Round 4 (M5-T167, backend-engineer) — the live path and page 6 / page 8 agree (scope correction 3, R136)

Base: the branch head after scope correction 3, `199eb59075052a1d5c037a3c0d0771b2e60c5463`.

## The cause (verified against the owner's real print)

On the owner's live/preview print at `dde8a181` page 8 item 4 still said "Whether a rear yard is
required is not yet checked ... ZR 23-344(b) ... (c)(3) have not been applied to this lot." while
page 6's "What was not checked" had dropped "The rear yard beyond the corner" — the report
contradicted itself and the rear-yard result reached only the test fixture, not the deliverable. Two
root causes, closed together:

1. The live results route emitted a **1.4.0** document: `results_read.py` called
   `run_engine_and_result_ways_from_evidence(...)` with **no `street_data=`**, and `StudyInputs` had
   no field to carry a DCM window, so `_rear_yard_analysis_for` returned None and no 1.5.0 block was
   emitted (page 8 then keeps the "not yet checked" open check).
2. `first_option_results._not_checked` (round 3) dropped the page-6 corner-lot rear-yard line
   **unconditionally**, while `readers._apply_rear_yard_open_item` only rewrites page 8 when a 1.5.0
   `rear_yard` block exists — so on every 1.4.0 document page 6 and page 8 disagreed.

## Changes (per step)

1. **Page 6 and page 8 agree on every document.** `first_option_results.py`: restored
   `_NOT_CHECKED_REAR_YARD`; added `rear_yard_applied: bool = False` to `FirstOptionInputs`; gated
   `_not_checked` so the corner-lot line is kept when `not rear_yard_applied and lot_type ==
   "corner"` and dropped otherwise. `three_way_document.py`: `_apply_first_option` takes
   `rear_yard_applied`, and `emit_three_way_document` passes `rear_yard_applied=rear_yard_analysis is
   not None` (the analysis is already in hand before page 6 is built). three_way_document.py held at
   **637 source_lines** (net-zero: the added parameter/call lines offset by tightened docstrings;
   `modularity_check --check` exit 0).
2. **Street data on the live path.** `study_inputs.py`: added `street_data` to `StudyInputs`
   (default None = "none supplied"), a `StreetDataProvider` seam + `street_data` param on
   `assemble_study_inputs`/`pluto_study_inputs_provider`, and a `live_street_data_provider` factory
   (composes the accepted MapPLUTO lot fetch + `lot_outline_from_mappluto` + `street_data_for_lot`;
   local imports, mirroring `acris_zoning_lot_index_provider`), bound in `_live_study_inputs_provider`
   behind `LIVE_SPATIAL_PROVIDER_ENABLED` (default OFF, no switch changed). `results_read.py` threads
   `street_data=inputs.street_data`. `apps/web/e2e/harness/fixture_api.py` passes the recorded
   `streets` (built and formerly discarded) to `assemble_study_inputs`. With no/incomplete window the
   result stays not known with its condition named and both pages agree.
3. **Web journey pin.** `journey-215-16-northern.test.tsx`: `contract_version` pin `1.4.0 -> 1.5.0`
   (and the title), read against the regenerated 1.5.0 fixture; the envelope `rear_yard` value-state
   is still withheld, so no other assertion changed. (CI run 38659165455 at dde8a181 failed exactly
   here.)
4. **Tests that would have caught it** — one per input state (table below); the full-report red/green
   pair below.

## Input-state table (round 4)

| input | state | outcome | test that pins it |
|---|---|---|---|
| rear_yard_applied + lot_type | False + corner (1.4.0) | page 6 lists "The rear yard beyond the corner" FIRST; page 8 "not yet checked" | test_round4_corner_lot_without_rear_yard_applied_keeps_the_pre_check_line; test_round4_1_4_0_corner_report_page_6_and_page_8_agree |
| rear_yard_applied + lot_type | True + corner (1.5.0) | page 6 drops the line; page 8 reads the conditional result | test_round4_corner_lot_with_rear_yard_applied_drops_the_pre_check_line; test_round4_1_5_0_corner_report_page_6_drops_line_and_page_8_conditional; test_round4_benchmark_page_6_drops_the_rear_yard_pre_check_line |
| rear_yard_applied + lot_type | any + interior | line never listed (corner-only) | test_round4_interior_lot_never_lists_the_corner_rear_yard_line |
| results route | provider supplies street data (street_on=True) | 1.5.0 doc; rear_yard + input_facts byte-equal to the committed journey | test_m5t146_live_route_benchmark_matches_the_committed_first_option_blocks |
| results route | provider supplies none | 1.4.0 doc, no rear_yard; page 6 keeps the line (shared 1.4.0 core else equal) | test_m5t146_live_route_benchmark_matches_the_committed_first_option_blocks |
| live street-data provider | composes the recorded DCM window | yields the recorded StreetData | test_live_street_data_provider_composes_the_recorded_window |
| live street-data provider | typed connector failure | None (not known, nothing fabricated) | test_live_street_data_provider_failing_fetch_yields_none |
| study-inputs provider | a street_data provider is bound | StudyInputs.street_data carries the window; None when unbound | test_study_inputs_provider_carries_street_data_when_fetched |
| `_live_study_inputs_provider` | LIVE_SPATIAL_PROVIDER_ENABLED off / on | off -> street_data None (route 1.4.0); on -> bound (route 1.5.0) | test_live_default_flag_gates_the_geometry_binding |

Two consequence tests updated (the fix made them diverge by design, not a regression):
`test_harness_inputs_equal_the_test_trees_benchmark_provider` now compares against
`benchmark_provider(street_on=True)` (the harness carries the same recorded window — windows proven
equal); `test_w13_areas_disagree_benchmark_blocks_unchanged_through_the_threaded_emitter` compares
building B apart from `not_checked` (the 1.4.0 adapter emit keeps the line, the committed 1.5.0 drops
it; everything else byte-equal).

## Red/green proofs (gate reverted, then restored)

- **(a) 1.4.0 page-6 line kept.** Reverting `_not_checked` to the round-3 unconditional drop: both
  `test_round4_1_4_0_corner_report_page_6_and_page_8_agree` and
  `test_round4_corner_lot_without_rear_yard_applied_keeps_the_pre_check_line` **FAIL** (2 failed).
  Restored -> pass.
- **(b) 1.5.0 page-6 line dropped.** Reverting `_not_checked` to keep the line for every corner lot
  (ignoring `rear_yard_applied`): the FRESH 1.5.0 emit
  `test_round4_1_5_0_corner_report_page_6_drops_line_and_page_8_conditional` and
  `test_round4_corner_lot_with_rear_yard_applied_drops_the_pre_check_line` **FAIL** (2 failed).
  Restored -> pass. (`test_round4_benchmark_page_6_drops...` reads the static 1.5.0 fixture, a
  renderer/consistency guard, so it does not flip on a gate revert.)

## Checks (direct exit codes)

- `python -m ruff check .` (services/api): **exit 0**.
- `tests/rules`: **1159 passed**, exit 0.
- whole `python -m pytest -q -p no:cacheprovider` (services/api): **9776 passed, 8 skipped**, exit 0
  (`/tmp/claude-0/M5-T167/round4-api-pytest-2.log`).
- `.github/scripts/validate_contracts.py`: 23 schema files, **0 failures**, exit 0; `pytest
  .github/scripts/tests`: **24 passed**, exit 0.
- `render_review_register.py --check`: **PASSED**, exit 0 (re-rendered after the register resync).
- `tools/research_record_check.py --check`: **PASS**, NB-01 code_current=True, exit 0.
- `tools/modularity_check.py --check`: failures 0 (warnings only; three_way_document.py 637), exit 0.
- `scripts/lanes/check_lane_paths.py --coverage`: **PASS** (10483 files), exit 0.
- `apps/web`: `npm ci` exit 0; `npm run lint` exit 0 (2 pre-existing warnings, 0 errors); `npm run
  typecheck` exit 0; whole `npx vitest run`: **129 files, 2704 passed**, exit 0
  (`/tmp/claude-0/M5-T167/round4-web-vitest.log`).

## Records / register

- NB-01 -> **revision 6**: code_identity refreshed for `study_inputs.py`
  (`48eaf75f...`) and `three_way_document.py` (`9d4a1d19...`); a revision-6 note records the gate +
  the street-data carrier. No zoning-lot reading, warning or figure changed (access_blocked).
- register.json: `three_way_document.py` sha256 -> `9d4a1d19...` in both calc entries;
  code_identity_sha256 -> `1658abb8...` (apartment-estimate) and `8985d57f...`
  (first-building-option); two `implementation_changed` events (seq 52/53, revisions 12/13); the four
  rendered pages (REGISTER.md, HISTORY.md, calc-first-building-option-complete.md,
  calc-preliminary-apartment-estimate.md) re-rendered. The recorded automated-test runs read
  'Not run' at the new identity (CI re-runs them).

## What the owner's benchmark preview should now print (quoted from the regenerated 1.5.0 render)

- **Page 8, item 4 (Rear yard), label Conditional:** "A conditional reading of the short-block rule
  ZR 23-344(b) and the adjoining-side-line rule ZR 23-344(c)(3): the rear yard is not settled on this
  lot. A survey or deed that shows this lot's lot lines, and the adjoining lots' lot lines where they
  meet this lot." (No longer "Whether a rear yard is required is not yet checked ... have not been
  applied to this lot.")
- **Page 6, "What was not checked":** "Where the plan sits on the lot", "The street wall", "Parking,
  loading and bicycle requirements" — "The rear yard beyond the corner" is dropped (the rear yard is
  shown at the lot level). Page 6 and page 8 now agree.

## Assumptions / limitations

- `study_live_geometry.py` is not in this packet's allowed paths, so `live_street_data_provider`
  lives in `study_inputs.py` (the live-provider/Lane-C layer, matching `acris_zoning_lot_index_
  provider`). With `LIVE_SPATIAL_PROVIDER_ENABLED` ON the geometry provider and the street-data
  provider each fetch the lot + street window, so the window is fetched twice; a no-refetch design
  that surfaces the window `live_geometry_provider` already fetches would need `study_live_geometry.py`
  (out of scope). The flag is default-OFF, so production and the offline tests are unaffected
  (the harness/tests thread a recorded window directly).
- No production switch changed; `report_read.py` delegates to `post_results`, so the report route is
  fixed by the `results_read.py` change with no edit. The flag-on e2e specs read their expected
  values from the regenerated 1.5.0 fixture (building B not_checked[0], the envelope rear_yard
  withheld), so they stay green; CI runs Playwright.
- Nothing under `.claude/**`; no server/ports/Playwright. Scratch only under `/tmp/claude-0/M5-T167/`.

END-OF-REPORT
