# M5-T145 PART E producer report - the review register follows the four new calculation modules

Written by the PART E builder (an AI agent, role rules-engineer). This is a draft reading, not
professionally reviewed (ADR-007). I changed only the register's SOURCE DATA and rendered its pages
by its own process (`render_review_register.py --write`); I wrote no renderer or checker code, moved
no verdict, and touched no human-review field. Base/contract head
`2e6dde3ee15a1d3ff742701c5637bc2f3e1ff0ae`.

## The four new modules (M5-T145 parts A-D, already on the branch)

- A `services/api/app/spatial/corner_reach_area.py` - measures the corner-lot / interior-lot area split.
- B `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` - applies the 100%/80% ratios.
- C `services/api/app/scenario/three_answers/first_building_options.py` - the two step-P6 buildings.
- D `services/api/app/scenario/three_answers/preliminary_apartment_estimate.py` - the estimate arithmetic.

Each exists as a pure module, is imported by nothing, and is connected to no reported result. The
committed results document (`recorded_215_16_northern_journey.json`) is UNCHANGED, so the program's
actual answer on every step is unchanged (withheld / not built). The journey test confirms this.

## Entry by entry (six calculation entries; S31 names four)

CHANGED (on the new-module path; revision 1 -> 2, one history event each, the new module(s) added to
`code_modules` so their identity is fingerprinted, automated_tests re-recorded at the new code
identity):

- `calc-lot-coverage-by-portion` (+A, +B; code identity d13b7093...). interpretation / exceptions /
  behaviour.planned / coverage_gap reworded: the by-portion split is now built as two pure modules
  but connected to no reported result; the engine still withholds `max_lot_coverage`.
- `calc-building-option-floor-stack` (+C; b76885b3...). Reworded: the two step-P6 buildings are built
  as a pure module, connected to no reported result; the engine's own generator is not built; the
  one-floor-to-floor-height limit (R542) stated.
- `calc-preliminary-apartment-estimate` (+D; fad72467...). Reworded: the estimate is built as a pure
  module, connected to no reported result; the document still reports it not built.
- `calc-first-building-option-complete` (+A,+B,+C,+D; dc2b0950...). interpretation / exceptions /
  behaviour / gaps and the "code not built" closing row reworded to say the component modules now
  exist but are wired to nothing; every one of the six step verdicts is UNCHANGED; the closing kind
  stays "code not built" (it must match the program's own gap_kind, which did not change); DB-210
  still named.

NOT CHANGED substantively (off the new-module path - no new module implements them, no narrative or
revision change): `calc-floor-area-allowance`, `calc-legal-dwelling-unit-limit`. Their recorded
test-file digest was resynced only because the ONE shared linked test file had an assertion moved
(see below); no revision moved and no history line was added for them.

## Coverage gaps before -> after (register-wide list)

9 gaps -> 10 gaps; none dropped. Reworded the three on-path gaps (building-option, lot-coverage,
preliminary-estimate) from "not built" to "built as a pure module but connected to no reported
result". Added one NEW gap the new modules open: part C works one floor-to-floor height for every
storey (R542 10 ft), so a 15 ft shop ground floor is not worked. The three-answers-engine gap
(index 0) and the M5-T144 gap (both required by the checker) are unchanged.

## History lines appended (calculations_history, seq 7-10, all 2026-10-09, implementation_changed)

7 calc-lot-coverage-by-portion rev 2; 8 calc-building-option-floor-stack rev 2; 9
calc-preliminary-apartment-estimate rev 2; 10 calc-first-building-option-complete rev 2. No earlier
line (seq 1-6) changed.

## Test-file assertion changed (one; S32)

`test_calculations_history_is_append_only_and_separate` pinned the history length to the number of
calculations (`== list(range(1, len(CALCS) + 1))`). Appending revision-2 history events legitimately
grows the history past one-per-entry, so I changed that single assertion to the real invariant: the
seq is contiguous from 1 to `len(calculations_history)`. No other assertion changed; the renderer and
checker are untouched. Because all six calc entries link this one file, editing it forced a
test-file-digest resync on all six `automated_tests` blocks (new digest
eb029a9a...); the four changed entries absorb it in their revision bump, the two off-path entries get
the digest-only resync. Without the resync the checker would demand their status read "Not run".

## S33 mutation (temporary copy OUTSIDE the repository)

Copied the worktree (minus .git) to the scratchpad; baseline `--check` PASSED. Appended one comment
line to `first_building_options.py` in the copy; `--check` FAILED with 2 issues, each naming the
changed module: "calc-building-option-floor-stack: code module .../first_building_options.py content
changed (sha256 8a9a8d02... != recorded 26a92c40...); the register must be updated in the same change
(new revision, history event)" and the same for calc-first-building-option-complete. The committed
register `--check` passes (exit 0). The drift is caught and names the module, as S31/S33 require.

## Checks (each with its direct exit code)

All via `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`.

- (services/api) `python -m ruff check .` -> All checks passed! RUFF_EXIT=0
- (services/api) `pytest ... test_zoning_rule_review_register.py test_zoning_rule_review_register_calculations.py tests/rules/reference_cases tests/journey` -> 187 passed, 1 warning EXIT=0
- (worktree root) `render_review_register.py --check` -> register check PASSED (no issues) CHECK_EXIT=0
- (worktree root) `tools/modularity_check.py --check` -> failures 0 (pre-existing warnings only, none my files) MOD_EXIT=0
- (worktree root) `scripts/lanes/check_lane_paths.py --coverage` -> LANE COVERAGE PASS, 9699 files LANE_EXIT=0
- (worktree root) `git diff --stat 2e6dde3e -- docs/zoning-rule-review/rules` -> empty (the 23 rule pages byte-identical) EXIT=0
- S33 temp-copy `--check`: baseline PASS (exit 0); after one-byte mutation FAIL naming the module (exit 1).

The full api suite was NOT run locally (CI runs it).

## Scope / what I could not settle

Files changed: register.json; the 2 rendered index pages (REGISTER.md, HISTORY.md); the 6
calculations/*.md pages and 6 evidence/*.txt logs (produced/updated by the register's process); the
one test assertion. No module, no renderer/checker code, no rule entry or page, no results fixture,
no reference case touched; every entry still reads "Not reviewed". Nothing blocking.
