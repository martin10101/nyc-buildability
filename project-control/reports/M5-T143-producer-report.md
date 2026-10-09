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
| S1 | import the facade names from `three_way_document`; import the bridge and the route | every name resolves to the same object; the five public names are in `__all__` | whole folder imports resolve (464 passed); runtime identity check in this report |
| S2 | emit the committed journey/benchmark input and each made-up input in the test file | document deep-equals the committed journey fixture; no string moved | `tests/journey/test_215_16_northern_journey.py` (byte-exact) + the whole `tests/scenario/three_answers` folder |
| S3 | `python tools/modularity_check.py --check` | passes; emitter ~415, new module ~213, both < 600 | modularity check, exit 0 |
| S4 / DB-199 a | real benchmark document with a sentinel number injected into `geometry` (a block the named walk skips) | the named-block walk misses it; the whole-document scan catches it | `test_db199a_injected_number_caught_only_by_the_whole_document_scan` |
| S5 / DB-199 b | interior lot whose ways SHOW the standard limit, engine inner `unit_estimate` forced not-available | limit is a withheld value_state with its two exact texts; no number; both texts under the text guard | `test_db199b_shown_standard_limit_with_no_inner_block_is_withheld_with_no_number` |
| S6 / DB-199 c | interior lot whose ways SHOW the standard limit, with `rule_versions` present, then absent | present -> sources include `rule_table` + `zoning_resolution`; absent -> only `zoning_resolution` | `test_db199c_shown_standard_limit_carries_rule_table_source_with_the_list`; `test_db199c_missing_list_drops_rule_table_source_todays_behaviour_not_required` |

## Red proofs (before the fixes; outputs kept)

- (a) named walk is blind to an unvisited block. Script on the committed journey fixture:
  `real doc: sentinel in named-block walk : False`; `real doc: sentinel in whole-document scan :
  False`; `injected: sentinel MISSED by named walk : True`; `injected: sentinel CAUGHT by whole
  scan : True`. Exit 0.
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

- (a) `_all_numbers_anywhere` made to delegate to the named-block walk ->
  `test_db199a_...whole_document_scan` goes RED at `assert sentinel in _all_numbers_anywhere(
  injected)`. Reverted.
- (b) fallback reverted to append a value object -> `test_db199b_...withheld_with_no_number` goes
  RED (`way` is `conditional` not `withheld`; a number reappears). Reverted.
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
  tests/api/test_results_read_api.py`: 464 passed, 2 skipped, exit 0 (claim-head baseline 460
  passed, 2 skipped; +4 new tests).
- c. `python3 tools/modularity_check.py --check` (repo root): selected 735 files; failures 0; exit
  0. `three_way_document.py` 415 lines, `three_way_scope_lines.py` 213 lines (both < 600).
- d. `grep -c "result_way" .../three_way_scope_lines.py`: prints `0` (grep exit 1 is the normal
  "no matches" status for `-c`).
- e. the move proof (diff empty, exit 0); the red proofs (above); the mutation proofs (above).
- f. `git status --porcelain` shows only the four allowed paths; after the single commit
  `git diff --name-status 64ee307a..HEAD` lists exactly the four allowed paths and
  `git diff --stat 64ee307a..HEAD -- packages services/api/tests/drawings services/api/tests/cad
  services/api/tests/documents apps` is empty.
