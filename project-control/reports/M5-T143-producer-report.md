# M5-T143 producer report

Producer: backend-engineer (an AI agent). Worktree reset to the claim head
`64ee307a534979d31ef111cd617d9ff383a5192c`. No ledger, no push, no review. Python
`/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest with
`-p no:cacheprovider`, run from `services/api`.

## What moved where (names and line counts)

The self-contained scope-line block of `three_way_document.py` moved CHARACTER FOR CHARACTER into
a new leaf module `services/api/app/scenario/three_answers/three_way_scope_lines.py`. The block is
claim-head lines 131-313 (183 lines). Names moved: `_SCOPE_BASIS_BY_SOURCE`, `_NOT_KNOWN_VALUE`,
`_NOT_APPLICABLE_VALUE`, `_WORDS_VALUE_BY_SOURCE`, `HOUSING_PROGRAM_KEY`, `FLOOR_TO_FLOOR_KEY`,
`USER_CHOICE_KEYS`, `_HOUSING_PROGRAM_DISPLAY`, `USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT`,
`USER_SELECTED_HOUSING_PROGRAM_STATEMENT`, `_fmt_feet`, `_fmt_degrees`, `_scope_statement`,
`_user_choice_statement`, `_rewrite_scope_lines`. The new module imports from `.engine_conditions`
only (`Derived`, `Source`) and contains no occurrence of the substring `result_way` (ruling B3).

`three_way_document.py` keeps every name anything names there (ruling B2) via a compatibility
facade `from .three_way_scope_lines import (FLOOR_TO_FLOOR_KEY, HOUSING_PROGRAM_KEY,
USER_CHOICE_KEYS, USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT, USER_SELECTED_HOUSING_PROGRAM_STATEMENT,
_HOUSING_PROGRAM_DISPLAY, _rewrite_scope_lines)`; the five public names stay in `__all__`. Its
`.engine_conditions` import narrowed to `Derived` (only the moved code used `Source`). The two
DB-199 (b) fallback texts were hoisted BYTE-IDENTICAL to module constants
`STANDARD_UNIT_LIMIT_NOT_AVAILABLE_REASON` and `STANDARD_UNIT_LIMIT_NOT_AVAILABLE_RESOLVED_BY`,
referenced by the fallback and brought under the existing text guard through the test imports; the
emitted strings are unchanged (ruling B5 b, verified: the constants equal the literals).

`test_three_answers_three_way_emit.py`: `_scope_statement` / `_user_choice_statement` now import
from `three_way_scope_lines` (the facade list, packet + B2, does not keep them at the old path);
the two hoisted constants import from `three_way_document`; the three gap tests were added.

Line counts: `three_way_document.py` 599 -> 415; `three_way_scope_lines.py` 1 (placeholder) -> 213;
both under the 600 warning (neither appears in the modularity warning list).

## Proof of the move (ruling B1)

Claim-head lines 131-313 extracted to `block_131_313.txt` (183 lines, 8979 bytes). The new module's
body after its docstring and imports (from the first `_SCOPE_BASIS_BY_SOURCE = {` to EOF) was
extracted and compared: byte-for-byte equal (8979 == 8979), `diff` empty, exit 0. The import prefix
ends with `from .engine_conditions import Derived, Source\n\n`. Facade identity verified at runtime:
every facade name `is` the same object as in the new module; the bridge (`result_way_engine_bridge`)
and the route (`results_read`) re-exports resolve to the same objects; `_HOUSING_PROGRAM_DISPLAY`
is importable from the old path. No emitted or shown string changed anywhere.

## Table of states -> input -> expected -> test

| id | input (state) | expected | test(s) |
|----|---------------|----------|---------|
| S1 | import the facade names from `three_way_document`; import the bridge and the route | every name resolves to the same object; the five public names are in `__all__` | whole folder imports resolve (465 passed); runtime identity check in this report |
| S2 | emit the committed journey/benchmark input and each made-up input in the test file | document deep-equals the committed journey fixture; no string moved | `tests/journey/test_215_16_northern_journey.py` (byte-exact) + the whole `tests/scenario/three_answers` folder |
| S3 | `python tools/modularity_check.py --check` | passes; emitter ~415, new module ~213, both < 600 | modularity check, exit 0 |
| S4 / DB-199 a (corrected) | the REAL emitted documents (benchmark, evidence benchmark, made-up interior/corner, lane-off, no-profile); and copies with a NEW numeric block at the top level and inside an answer | every top-level block and every key inside each answer is classified as a result-number block (walked) or a no-result-number block (named, with a reason); a new unclassified block is caught | `test_db199a_every_block_of_the_emitted_document_is_classified`; `test_db199a_completeness_guard_catches_a_new_numeric_block` |
| S5 / DB-199 b | interior lot whose ways SHOW the standard limit, engine inner `unit_estimate` forced not-available | limit is a withheld value_state with its two exact texts, `gap_kind == missing_information`, no value object, and the figure it would have (16) is not a result number; both texts under the text guard | `test_db199b_shown_standard_limit_with_no_inner_block_is_withheld_with_no_number` |
| S6 / DB-199 c | interior lot whose ways SHOW the standard limit, with `rule_versions` present, then absent | present -> sources include `rule_table` + `zoning_resolution`; absent -> only `zoning_resolution` | `test_db199c_shown_standard_limit_carries_rule_table_source_with_the_list`; `test_db199c_missing_list_drops_rule_table_source_todays_behaviour_not_required` |

## Red proofs (before the fixes; outputs kept)

- (a) see the Correction section below (the first-version red proof was superseded).
- (b) fallback branch untested. A temporary `raise AssertionError(...)` placed in the fallback
  else-branch, then `tests/scenario/three_answers` run: `353 passed, 2 skipped` (GREEN, exit 0) -
  no existing test reaches the branch. The raise was removed.
- (c) the brief's literal red proof (force `_rule_version` to return None) actually FAILS an
  EXISTING test: `test_s19_standard_unit_limit_shown_with_its_formula` (`assert "rule_table" in
  kinds`), because S19 already pins the PRESENT-list branch. The genuine untested gap is the
  MISSING/empty-list branch: a temporary `else: raise` in the `version is None` branch, then
  `tests/scenario/three_answers` run: `353 passed, 2 skipped` (GREEN, exit 0) - no existing test
  enters that branch. The raise was removed. (This discrepancy with the brief's wording is
  disclosed; it does not block the task - the new test closes the real gap.)

## Mutation proofs (one per pinned branch; in place, reverted exactly)

- (a) see the Correction section below (the first-version mutation was superseded).
- (b) `_rule_version`-independent fallback mutations - see the Correction section below (gap b was
  strengthened with two more assertions and two more mutation proofs).
- (c) `_rule_version` forced to return None ->
  `test_db199c_...carries_rule_table_source_with_the_list` goes RED at `assert "rule_table" in
  kinds`, while `test_db199c_missing_list_...` stays GREEN. Reverted.

## What is NOT changed

No emitted or shown string anywhere (byte-identity: the move diff is empty, the journey byte-exact
test passes, the two fallback texts were hoisted byte-identical). No change to the decision module,
the engine, `engine_disclosures.py`, the route `results_read.py`, any schema, any fixture, any
drawings/CAD/PDF code, or `apps/web`. The import-guard test in `test_result_ways.py` is unedited
(the new module holds no `result_way`). `contract_version` and the document structure are unchanged.

## Open question of gap (c)

Whether a shown standard unit limit whose engine document lacks the rule-versions list should be
WITHHELD, rather than shown today with only the zoning-resolution source, stays an open question
recorded in backlog DB-199 (c); no behaviour of the emitter changes in this task.

## Checks (direct exit codes)

- a. `python -m ruff check .` (from `services/api`): "All checks passed!", exit 0.
- b. `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/journey
  tests/api/test_results_read_api.py`: 465 passed, 2 skipped, exit 0 after the correction (claim-head
  baseline 460 passed, 2 skipped; +5 new tests). The first commit 7d8b0845 had 464 (+4); the
  correction replaced the one gap (a) test with two, so +1.
- c. `python3 tools/modularity_check.py --check` (repo root): selected 735 files; failures 0; exit
  0. `three_way_document.py` 415 lines, `three_way_scope_lines.py` 213 lines (both < 600).
- d. `grep -c "result_way" .../three_way_scope_lines.py`: prints `0` (grep exit 1 is the normal
  "no matches" status for `-c`).
- e. the move proof (diff empty, exit 0); the red proofs (above); the mutation proofs (above).
- f. `git status --porcelain` shows only the four allowed paths; after the single commit
  `git diff --name-status 64ee307a..HEAD` lists exactly the four allowed paths and
  `git diff --stat 64ee307a..HEAD -- packages services/api/tests/drawings services/api/tests/cad
  services/api/tests/documents apps` is empty.

## Correction (2026-10-09; second commit on top of 7d8b0845; test file + report only)

The orchestrator corrected ruling B5 (a): the first gap (a) test guarded nothing (it only showed a
second helper `_all_numbers_anywhere` could see an injected number; no guard of the REAL document
used it), and a plain whole-document walk is wrong (the document rightly carries coordinates,
measurements, inputs and counts outside the result blocks - four existing tests fail if
`_all_result_numbers` walks the whole document). This commit REPLACES the first gap (a) test and the
`_all_numbers_anywhere` helper with a COMPLETENESS guard, and strengthens gap (b). No production file
changes (the two app files are byte-identical to 7d8b0845); the emitter's behaviour and every
emitted/shown text are unchanged.

Gap (a), the completeness guard. `_all_result_numbers` is kept exactly as it is. Two literal sets in
the test file, derived by READING `_all_result_numbers` (not guessed):
- RESULT-NUMBER blocks (walked; every number in them is a result): top level
  `{addon_gains, best_combination, floor_by_floor, floor_stack, shortfall, unit_estimate}`; inside
  each answer ONLY `{values}`.
- NO-RESULT-NUMBER blocks (named, each with a one-line reason): top level `answers` (entered in
  part), `contract_version`/`results_id`/`study_id`/`option_id`/`street_width_case` (identifiers),
  `revision`/`notices_count` (metadata counts), `computed_at` (timestamp), `draft`/`out_of_date`
  (flags), `out_of_date_reason`/`completeness_line`/`status_strip`/`lot_selection_statement`/
  `with_approvals_label` (prose), `depends_on_fact_ids`/`rule_versions` (identifiers),
  `existing_building` (an input fact), `remaining_floor_area` (a not_available block), `scope`
  (condition values / measurements / the floor-to-floor input), `geometry` (polygon coordinates and
  the dimensions that RENDER shown results); inside each answer `{status, measurement, value_states,
  reason, reason_kind, resolved_by, gap_kind}`. One test asserts every block of the real documents
  (benchmark, evidence benchmark, made-up interior/corner, lane-off, no-profile) is in exactly one
  set; another asserts a NEW numeric block (top level and inside an answer) is caught.
- Classification I had to reason about: `geometry` carries the building height (e.g. 55.0), which IS
  a shown result. It is classified NO-RESULT-NUMBER because geometry only RENDERS results that are
  already shown in an answer's `values[]` (walked), and a withheld result's geometry layer follows
  it to `not_available` (reading O29/O31) - so geometry never hides a withheld result's number. No
  non-walked block carries a result figure that is not also a shown value; nothing to STOP on.

Gap (a) red proof (before the guard): a copy of the committed journey document with a NEW top-level
numeric block leaves `_all_result_numbers` unchanged and the injected 100.0 unseen
(`_all_result_numbers unchanged by the new block: True`; `injected 100.0 NOT seen: True`) - the only
existing numeric guard is blind to it. Exit 0.

Gap (a) mutation proofs (each reverted exactly): (m1) remove `unit_estimate` from the walked set ->
`test_db199a_every_block_...` RED on the real document; (m2) remove `remaining_floor_area` from the
no-result-number set -> same; (m3) make `_unclassified_blocks` skip the inside-an-answer keys ->
`test_db199a_completeness_guard_catches_a_new_numeric_block` RED (the inside-an-answer case goes
unseen).

Gap (b), strengthened. Two assertions added: `state["gap_kind"] == "missing_information"` (nothing
pinned the kind before); and that the figure the limit WOULD have for this lot (read from the
unforced emit: 16) is NOT in `_all_result_numbers` of the forced document (whose result numbers are
2, 2.4, 30, 45, 55, 65, 10710, 12852 - 16 is not among them, so the assertion bites). Mutation
proofs (each reverted exactly): (m-b1) fallback `gap_kind` changed to `work_owed` ->
`test_db199b_...` RED at the `gap_kind` assertion; (m-b2) fallback made to append a value object with
the figure -> `test_db199b_...` RED (first at `way == withheld`; under the mutation the figure 16
also appears in `_all_result_numbers`, confirmed separately, so the figure assertion is
load-bearing).

Correction checks (direct exit codes): ruff `check .` from `services/api` exit 0 ("All checks
passed!"); `pytest tests/scenario/three_answers tests/journey tests/api/test_results_read_api.py`
465 passed, 2 skipped, exit 0; `git diff --stat HEAD -- services/api/app` empty before the commit (no
production change); `git status --porcelain` clean after the commit.
