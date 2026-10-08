# M5-T139 producer report

A choice the user made is said to be the user's choice: through the route, the housing-program and
floor-to-floor scope lines of the results document say the choice was ENTERED/SELECTED when the user
made it, and "the default" only when the engine's starting value was used. No value, no way, no other
line and no saved file changes. `engine_disclosures.py` is not edited. Producer: backend-engineer
(an AI agent), isolated worktree, reset to the claim-seam head before work.

## 1. Table of states (built before any edit; each verified in source)

| State | Outcome (the two lines: value / basis / sentence) | Test id |
|---|---|---|
| Route, height **entered** 14, standard | floor_to_floor: value 14 / basis `entered` / "A 14-foot floor-to-floor height was entered for this run." (no "default") | `test_t139_s1_entered_floor_to_floor_height_is_said_to_be_entered` (RED→GREEN) |
| Route, **no** height, standard | floor_to_floor: value 10.0 / basis `default` / engine's own "A 10-foot floor-to-floor height is used as the default." (unchanged) | `test_t139_s2_starting_floor_to_floor_height_is_still_called_the_default` |
| Route, housing `standard_residence` | housing_program: value `standard_residence` / basis `entered` / "Standard residence was selected for this run as the housing program." | `test_t139_s3_housing_program_is_the_users_selection[standard_residence-Standard residence]` |
| Route, housing `qualifying_affordable_housing` | basis `entered` / "Qualifying affordable housing was selected for this run as the housing program." | `test_t139_s3_...[qualifying_affordable_housing-...]` |
| Route, housing `qualifying_senior_housing` | basis `entered` / "Qualifying senior housing was selected for this run as the housing program." | `test_t139_s3_...[qualifying_senior_housing-...]` |
| Evidence entry **without** the new param, and the **older** entry (`run_engine_and_result_ways`) | both lines as the engine made them: basis `default`, the engine's "the default" sentences | `test_t139_entry_without_user_choices_leaves_the_two_lines_as_the_engine_made_them` |
| Transform: only the **named** choice rewritten; value untouched | naming floor_to_floor rewrites only it (value 10.0 kept); naming housing_program rewrites only it (value kept) | `test_t139_transform_rewrites_only_the_named_design_choice` |
| Entry **with vs without** choices, same lot/values | only basis + statement of the two rows differ; every value, unit, other scope line and other block identical | `test_t139_only_the_two_choice_lines_differ_with_user_choices` |
| Route doc **==** entry doc (user_choices mirrored in the reference) | the route's document equals the entry's for the same evidence, incl. the two rewritten rows | `test_t3_route_document_equals_the_entry_document` (reference reproduction updated) |
| Two new sentences are plain and true | both rendered sentences carry no internal name, no id, never "professional review", never "the default" | `test_every_text_the_transform_writes_is_plain_and_true` (extended) |

## 2. The parameter (smallest shape) and its three-line justification

Shape (one line): `run_engine_and_result_ways_from_evidence(..., *, user_choices: frozenset[str] | None = None)` — an immutable set of the scope-row keys the caller chose, a subset of `USER_CHOICE_KEYS = {"housing_program", "floor_to_floor_ft"}`.

1. It is NOT a fact about a lot: it records what the caller's own request carried (which design
   choices the user made), so no default stands for a fact (L1/R256).
2. Smallest shape: an immutable set of at most the two known scope keys; `None`/empty = no choice
   named, so the entry behaves exactly as today (default `None`) and the committed journey result is
   byte-identical.
3. It maps directly onto the scope rows the transform rewrites (a membership test keyed by the row's
   own `key`), needing no new enum or vocabulary; the route and the test reference the exported key
   constants, so there are no magic strings.

## 3. The two sentences the transform writes (plain, true, no internal name, never "the default")

- floor-to-floor: `USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT` = "A {height}-foot floor-to-floor height was entered for this run." (e.g. "A 14-foot floor-to-floor height was entered for this run.")
- housing program: `USER_SELECTED_HOUSING_PROGRAM_STATEMENT` = "{program} was selected for this run as the housing program." (e.g. "Standard residence was selected for this run as the housing program.")

The basis of a rewritten row becomes `entered` (a value the schema's `scope_assumption.basis` enum
allows); the row's `value` and `unit` are never touched.

## 4. Red proof (captured on today's code, before any production edit)

`tests/api/test_results_read_law_examples.py::test_t139_s1_entered_floor_to_floor_height_is_said_to_be_entered`,
driving the route with `{"housing_program":"standard_residence","floor_to_floor_ft":14}`:

```
>       assert row["basis"] == "entered"
E       AssertionError: assert 'default' == 'entered'
1 failed
```

On today's code the floor_to_floor line reads "A 14-foot floor-to-floor height is used as the
default." (basis `default`). After the production edit the same test is GREEN (the line reads
"A 14-foot floor-to-floor height was entered for this run.", basis `entered`).

## 5. Mutation proofs (each in a copy OUTSIDE the repository; pristine copy: 4 target tests passed)

| # | Branch mutated | Test run | Result |
|---|---|---|---|
| M1 | transform rewrites a line when the user did NOT choose (dropped the `key in choices` guard) | `test_t139_entry_without_user_choices_...` | FAIL — `AssertionError: assert 'entered' == 'default'` |
| M2 | route does NOT pass the height's choice (removed the `is not None` add) | `test_t139_s1_...` | FAIL — `AssertionError: assert 'default' == 'entered'` |
| M3 | route passes the height choice when the body carried none (added it unconditionally) | `test_t139_s2_...` | FAIL — `AssertionError: assert 'entered' == 'default'` |
| M4 | the value of a line is changed (set `row["value"]` in the user-choice branch) | `test_t139_transform_rewrites_only_the_named_design_choice` | FAIL — `AssertionError: assert 'MUTATION-M4' == 10.0` |

All four mutations were killed; each file was restored from the worktree original between mutations.

## 6. Tests on an optional value (all presence tested with `is not None`; no truthiness test)

- Route `results_read.py`: `req.floor_to_floor_ft is not None` (for `building_defaults` and for adding `FLOOR_TO_FLOOR_KEY` to `user_choices`).
- Reference reproduction `test_results_read_api.py::_reference_document`: `req.floor_to_floor_ft is not None`.
- Transform `three_way_document.py`: `condition_sources if condition_sources is not None else {}`, `user_choices if user_choices is not None else frozenset()`, and the emit guard `if condition_sources is not None or user_choices is not None:`.

No optional value is tested for truthiness; a present `0`/`False`/empty is never confused with absent.

## 7. What is NOT changed

- `engine_disclosures.py`, `evaluator_inputs.py`, `results_request.py`, `engine_conditions.py`, the
  engine, the decision modules, every schema, every fixture and saved drawing, every website file,
  `app/main.py`, `app/config.py`: byte-identical to the claim-seam head (not in the diff).
- No value, no way entry, no other scope line; no saved file; the committed journey result
  (`recorded_215_16_northern_journey.json`) is byte-identical (verified: empty `git diff --stat`).
- No switch/flag turned on; the older entry `run_engine_and_result_ways` is untouched.
- `three_way_document.py` stays under the 600-line warning threshold (599 lines; SLOC check: 0 failures, not flagged).

## 8. Checks (each with its DIRECT exit code)

- a. `ruff check .` (from services/api): exit **0** — "All checks passed!"
- b. `pytest -q -p no:cacheprovider tests/api`: exit **0** — 1131 passed (baseline 1126 + 5 new route tests: S1, S2, S3×3).
- c. `pytest -q -p no:cacheprovider tests/scenario/three_answers tests/journey tests/contracts`: exit **0** — 912 passed, 2 skipped (baseline 909 + 3 new emit tests).
- d. `pytest -q -p no:cacheprovider tests/cad tests/drawings`: exit **0** — 1359 passed, 6 skipped (no saved drawing changed).
- e. `python3 tools/modularity_check.py --check` (repo root): exit **0** — selected 729 files; failures 0; `three_way_document.py` = **599 lines**, not flagged.
- f. red proof: exit **1** (RED on today's code, as above); mutation proofs M1/M2/M3/M4: each exit **1** (all killed); pristine copy pre-check: exit 0 (4 passed).
- g. `git status --porcelain` / `git diff --name-status <claim head> HEAD`: only the 7 allowed paths (6 code/test files + this report).

## 9. Files changed (7 allowed paths, nothing beyond)

1. `services/api/app/scenario/three_answers/result_way_engine_bridge.py` — the evidence entry takes `user_choices` and passes it to the transform; re-exports the two key constants.
2. `services/api/app/scenario/three_answers/three_way_document.py` — `emit_three_way_document`/`_rewrite_scope_lines` take `user_choices`; new `_user_choice_statement`, the two sentence constants, the key constants and the display map.
3. `services/api/app/api/v1/results_read.py` — the route builds `user_choices` (housing program always; floor-to-floor only when the body carried one) and passes it.
4. `services/api/tests/api/test_results_read_api.py` — `_reference_document` mirrors the route's `user_choices` so the route==entry comparison holds.
5. `services/api/tests/api/test_results_read_law_examples.py` — S1 (red proof→green), S2, S3 (×3 programs).
6. `services/api/tests/scenario/three_answers/test_three_answers_three_way_emit.py` — S4, the per-row transform test, S5; the text guard extended to the two new sentences; `_evidence` forwards `user_choices`.
7. `project-control/reports/M5-T139-producer-report.md` — this report.

## Notes / assumptions / limitations

- Deviation from the brief's suggested function list: I added a dedicated `_user_choice_statement`
  helper rather than overloading `_scope_statement(key, derived)`, because the two design-choice rows
  have no `Derived`; forcing them through `_scope_statement` would contort its signature. The brief's
  RULES-THAT-DO-NOT-BEND do not name functions, only behavior; all behavior rules are met.
- The housing-program display map is defined locally in the presentation transform (closed 3-value
  study-schema vocabulary) because `engine_disclosures.py` is read-only and exposes no public display
  accessor; an unknown key falls back to itself. No new cross-module import was added.
- No file beyond the 7 allowed paths was needed or touched. No blockers; no points stopped on.
- The full api suite was NOT run (per the brief); the orchestrator runs it at the final candidate.

END-OF-REPORT
