# M5-T146 PART D (first half) producer report - the review register's checker: split + two DB-211 (a) guards

Producer: an AI agent (role rules-engineer), building in an isolated worktree. NOT a human or
professional review. Base: `f804ab50e6e555d1679805e7b7549f2a838bea6c`. Scope: the register's checker
only - its split into focused modules (behaviour unchanged) and the two DB-211 (a) guards with tests
plus the DB-211 (b) scenario fixes. NO data change: `register.json` and every rendered page under
`docs/zoning-rule-review/` stay byte-identical (verified empty diff). PART D2 (the register's data
update + render) and PART B (the server) are separate halves.

## What I built or changed, file by file

- **`services/api/app/rules/review_register/review_register_calculations.py`** (was 715 SLOC, now a
  139-SLOC COMPATIBILITY FACADE): re-exports every prior public name from three new focused modules,
  so `render_review_register.py`, `check_review_register.py` and the test file keep their old import
  path and names unchanged.
- **`services/api/app/rules/review_register/calc_vocab.py`** (NEW, 67 SLOC): the vocabularies and
  fixed field-key sets (pure data), plus two new step-state tuples `STEP_PRESENT_STATES` /
  `STEP_ABSENT_STATES` used by the verdict guard.
- **`services/api/app/rules/review_register/calc_render.py`** (NEW, 218 SLOC): the Markdown rendering
  of the calculation detail pages, table, coverage-gaps and history sections, and the page writer
  (moved verbatim; output is byte-identical).
- **`services/api/app/rules/review_register/calc_checks.py`** (NEW, 561 SLOC): the per-entry
  validators, the code-identity fingerprint, the six-step comparison checks, `validate_calculations`
  (moved verbatim) PLUS the two new guards `step_verdict_errors` and `figure_rows_errors`, invoked
  from `calc_entry_errors` for every `calculation_comparison` entry. The guards therefore run in the
  normal check path: `render_review_register.py --check` -> `check_review_register.validate()` ->
  `calc.validate_calculations()` -> `calc_entry_errors()` -> the guards. (I placed the guard
  functions in the focused checks module for cohesion and the size rule; they are part of the
  register's checker that `check_review_register.validate()` runs.)
- **`services/api/tests/rules/test_zoning_rule_review_register_calculations.py`**: added the PART D
  tests (facade, both guards with render-again mutation proofs, the DB-211 (b) S7/S8 scenario fixes,
  the no-human-verdict guard-independence test).

### The two guards (as checker rules; both read `register.json` directly so a fresh render cannot hide a fault)

- `step_verdict_errors` (DB-211 a, guard 1): a step whose program side is `withheld`/`not_built` must
  read `side_missing` (nothing to compare); a step that reads `agree` needs a PRESENT actual state
  and a non-empty value on both sides. (`not_available` may still read `differ` - a difference of
  method, e.g. step 3 - matching the committed data.)
- `figure_rows_errors` (DB-211 a, guard 2): every law section the six steps rest on (each section in
  the entry's `law`) must have a LEGAL_REQUIREMENT row, and every preliminary-assumption figure the
  steps use (700, 0.60, 0.75) must have a DESIGN_ASSUMPTION row.

## Scenario -> input state -> expected -> test name

| Scenario | Input state | Expected | Test name |
|---|---|---|---|
| S15 split keeps behaviour | the checker split behind a facade (DB-211 c) | outputs byte-identical before/after; public names importable from the old path; modularity passes | `test_calculation_module_is_a_compatibility_facade` (+ split-only `--check`=0 and 86 existing tests pass) |
| S17 verdict follows actual side (committed) | the committed six-step entry | `step_verdict_errors == []` | `test_six_step_verdicts_follow_their_actual_side_on_the_committed_register` |
| S17 verdict guard, render-again | step 3 verdict differ->agree (G4 mutation f), pages re-rendered | stale-page check clean, guard still RED | `test_a_six_step_verdict_without_a_present_side_is_caught_after_render` |
| S17 side changes, verdict kept | step 1 actual.state settled->withheld, verdict stays agree | guard RED (withheld must be side_missing; agree needs a present side) | `test_a_step_whose_side_changes_without_its_verdict_is_caught` |
| S17 withheld cannot differ | step 5 (withheld) verdict -> differ | guard RED (must be side_missing) | `test_a_withheld_step_cannot_read_differ` |
| S18 every figure has its row (committed) | the committed six-step entry | `figure_rows_errors == []` | `test_every_six_step_figure_has_its_legal_or_design_row_on_the_committed_register` |
| S18 figure guard, render-again | drop the ZR 23-432 legal row (G4 mutation h2), pages re-rendered | stale-page check clean, guard still RED | `test_a_dropped_legal_row_is_caught_after_render` |
| S18 dropped design row | drop the apartment-size (700) design row | guard RED | `test_a_dropped_design_assumption_row_is_caught` |
| S19 / S7 special-density present | feed `special_density_area=True` to `r6b-dwelling-units` | engine returns `not_applicable`, no `max_dwelling_units` (the formula does not apply, ZR 23-52(a)(1)) | `test_special_density_present_makes_the_unit_limit_not_applicable` |
| S19 / S8 effective date derived | each calc entry vs its combined rules | `applicable_from == max(last_amended of the combined rules' law)` = 2024-12-05; `applicable_to` None while every combined rule is open | `test_effective_date_is_derived_from_the_combined_rules` |
| S20 no human verdict | set a human decision on a copy | both guards' output unchanged (they ignore the human-review block) | `test_the_guards_never_read_a_human_verdict` |

### Expected vs. what the code returned

- S15: expected byte-identical / facade exposes prior names -> got `--check`=0 and 86 tests pass with
  the unchanged test file; facade identity assertions pass. MATCH.
- S17 committed: expected `[]` -> got `[]`. MATCH.
- S17 mutation f (differ->agree, not_available): expected RED after render -> got RED ("step 3 reads
  'agree' but its program side is not_available (not a present state)"), stale-page check `[]`. MATCH.
- S17 side->withheld: expected RED -> got RED (side_missing required + agree needs present side). MATCH.
- S17 withheld->differ: expected RED -> got RED. MATCH.
- S18 committed: expected `[]` -> got `[]`. MATCH.
- S18 drop ZR 23-432 row: expected RED after render -> got RED ("no LEGAL_REQUIREMENT row ... for ZR
  23-432"), stale-page check `[]`. MATCH.
- S18 drop 700 design row: expected RED -> got RED. MATCH.
- S7: expected `not_applicable`, no number -> got `coverage_status='not_applicable'`, outputs `{}`
  (and False still computes 29). Basis: ZR 23-52(a)(1) as captured; `real-lot#L6` for the 29. MATCH.
- S8: expected `applicable_from == 2024-12-05` derived from the combined rules' `last_amended` (never
  a program run) -> got MATCH for all six calc entries.
- S20: expected both guards unaffected by a human decision -> got `([], []) == ([], [])`. MATCH.

## Mutation proofs (temporary copy OUTSIDE the repository: `/tmp/db211-proof-*`)

Each guard: mutate the register data, RENDER AGAIN into a temp docs folder (so pages match the
mutated data and the OLD stale-page/byte-identity check is fooled), then show the guard still RED.

- Guard 1: `steps[2].verdict` `differ` -> `agree` (state stays `not_available`). After re-render the
  stale-page check is CLEAN `[]`; `step_verdict_errors` is RED ("step 3 reads 'agree' but its program
  side is not_available ..."). This is exactly the G4 mutation f that a fresh render hid.
- Guard 2: remove the `legal_vs_design` row naming ZR 23-432 (8 rows -> 7). After re-render the
  stale-page check is CLEAN `[]`; `figure_rows_errors` is RED ("the six-step figure for ZR 23-432 has
  no LEGAL_REQUIREMENT row ..."). This is the G4 mutation h2 that a fresh render hid.
- Control: both guards are `[]` on the UNMUTATED committed comparison entry.

(The same two mutations are also committed as the render-again tests above, using `tmp_path` +
`monkeypatch` on `render.DOCS_DIR`.)

## Checks, each with its DIRECT exit code

- `ruff check app/rules/review_register tests/rules/test_zoning_rule_review_register_calculations.py`
  (my files, from `services/api`): **exit 0** ("All checks passed!").
- `ruff check .` (from `services/api`, whole package): **exit 1** - the ONLY error is a PRE-EXISTING
  E501 in `app/scenario/three_answers/first_option_results.py` (PART B's seeded placeholder, present
  at the base commit, unchanged by me and outside my scope).
- `pytest tests/rules/test_zoning_rule_review_register.py
  tests/rules/test_zoning_rule_review_register_calculations.py tests/rules/reference_cases`: **exit 1**
  - **191 passed, 5 failed**; all 5 failures (`test_committed_register_validates_clean` x2,
  `test_committed_calculations_validate_clean`, the two `test_s13_*`) have the IDENTICAL cause: the
  grown (in-scope) test file no longer matches `register.json`'s recorded
  `automated_tests.tested_test_file_sha256s`, so the register's freshness guard requires status
  `Not run`. This is NOT a split or guard defect; it is the register.json test-digest pin and only a
  register.json resync (PART D2, forbidden to me) clears it. Every new PART D test passes.
- SPLIT-ONLY proof (split code + the base, unchanged test file): `--check` **exit 0** ("register
  check PASSED"); the two register suites **86 passed, exit 0**. This proves the split is
  byte-identical.
- `render_review_register.py --check` (final commit state): **exit 1** - the same 6 digest-pin
  messages (one per calc entry). Cleared by the PART D2 digest resync.
- `tools/modularity_check.py --check`: **exit 0** - 0 failures. Line counts: BEFORE
  `review_register_calculations.py` = **715 SLOC** (over the 600 warn line, DB-211 c); AFTER the
  facade = **139**, `calc_vocab.py` = **67**, `calc_render.py` = **218**, `calc_checks.py` = **561**
  - each under the 600 warn line; `review_register_calculations.py` no longer appears in the warnings.
- `scripts/lanes/check_lane_paths.py --coverage`: **exit 0** ("LANE COVERAGE PASS: 9726 file(s)").
- `git diff --stat f804ab50 -- docs/zoning-rule-review
  services/api/app/rules/review_register/register.json`: **EMPTY** (byte-identical; no data or page
  change).

(Checks run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`,
`-p no:cacheprovider`. I did NOT run the full api suite - that is CI's.)

## What the NEXT parts must know

1. **PART D2 MUST resync the test-file digest in `register.json` FIRST.** The only reason `--check`
   and the 5 "validates clean"/s13 tests are red at this isolated commit is that
   `calculations[*].automated_tests.tested_test_file_sha256s` for
   `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` still records the BASE
   digest, while this half grows that file. D2 (which already updates `register.json`) must re-record
   that digest (one value across the six calc entries) and the `status`/`tested_commit`/`tested_on`
   at the integrated head after CI re-runs. After the resync the combined head is green. `register.json`
   is D2's file; my D1 brief forbids it, so I did NOT touch it.
2. **New public names** importable from `review_register_calculations` (facade): `step_verdict_errors`,
   `figure_rows_errors`. New modules beside it: `calc_vocab`, `calc_render`, `calc_checks`. All prior
   public names are re-exported unchanged.
3. **The guards now gate the six-step data.** When D2 updates the six-step entry's data, it must keep
   every step's verdict bound to its actual side and keep a LEGAL_REQUIREMENT row for each law section
   plus a DESIGN_ASSUMPTION row for each preliminary-assumption figure the steps use - otherwise the
   guards correctly fail.

## What I could not settle / open items

- **The test-digest contradiction (above).** The brief asks for (a) committed guard/scenario tests in
  the pinned test file, (b) `register.json` byte-identical, (c) `--check` exit 0 and every existing
  test unchanged. Because `register.json` pins that very test file's sha256, (a) and (b)+(c) cannot
  both hold at a single commit; the resolution (a test-digest resync) is a `register.json` change =
  PART D2. I delivered the complete, correct code + tests and kept `register.json` byte-identical, and
  flag this as the gating item.
- **Guard placement:** the guard functions live in the focused `calc_checks` module (cohesion + size
  rule), not literally inside `check_review_register.py`; they run via `check_review_register.validate()`.

END-OF-REPORT

## Second half (M5-T146 part D2 - the register's DATA follows the wired results)

Built on the integrated head `455caec46895298a772505cdf34325d7fd758d96` (holds part D first half as
`68ffb69bd`, the 1.4.0 contract, the server wiring, the regenerated benchmark document, and the web
first half). Producer: an AI agent (rules-engineer). I read every ACTUAL answer FROM the committed
regenerated document `recorded_215_16_northern_journey.json`, never from memory. No checker/renderer
code changed. `register.json` edited, Markdown re-rendered via `--write`, GUIDE followed.

### What I changed, file by file
- `services/api/app/rules/review_register/register.json` (source data): resynced code identity and
  automated-test evidence for all six calc entries (shared test file grew; `first_building_options.py`
  and `three_way_document.py` changed in part B); updated the ACTUAL sides to the regenerated
  document; bumped each entry's revision and appended six `calculations_history` events (seq 11-16);
  reworded/added coverage gaps. No human verdict entered; expected (case-row) sides unchanged.
- `docs/zoning-rule-review/` (renderer-written, via `--write` only): REGISTER.md, HISTORY.md and the
  six `calculations/*.md` re-rendered. The 23 rule pages under `rules/` are byte-identical (diff empty).
- `docs/zoning-rule-review/evidence/*.txt` (6 hand-written run logs): refreshed to the new run
  (commit `455caec4`, 53 passed) per GUIDE step 2, matching the resynced `automated_tests` fields.
- `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` (my first-half test
  file; NOT checker/renderer code): two assertion updates forced by the regenerated document -
  `test_document_actuals_match_the_recorded_fixture` (the stale `"not built yet"` assertion PART E's
  regeneration left behind; now checks the estimate is given in `building_alternatives`), and the
  guard-mutation test (its hardcoded old step-3 verdict; now mutates a withheld step, which is stable).

### Six-step verdicts, before -> after (read from the document)
- Step 1 Property inputs: agree -> agree (inputs settled, match).
- Step 2 Footprint / lot coverage by portion: side_missing -> side_missing (footprint figure now
  withheld because the recorded and tax-map outline lot areas disagree, a missing fact; law by portion).
- Step 3 Each floor's area and height: differ -> side_missing (building B now given and matches; building
  A not listed, it needs the withheld footprint, so that side is missing).
- Step 4 Total floor area: side_missing -> agree (building B total 20,150 sq ft now given, matches,
  conditional).
- Step 5 Applicable legal unit limit: side_missing -> side_missing (still withheld; engine computes 29).
- Step 6 Separate preliminary apartment estimate: side_missing -> agree (building B estimate 17.27 to
  21.59 now given, matches, conditional). All verdicts pass the DB-211 guards.

### Gaps changed
Reworded (no longer "connected to no reported result"): the building-option gap (building B reported,
building A needs the withheld footprint), the lot-coverage gap (figure withheld where the two areas
disagree), the preliminary-estimate gap (now reported for building B, DB-213 a). Added two: the older
single blocks now point to `building_alternatives`; the share/size are shown but not yet changeable
(DB-213 a). Kept (still true): three-answers engine, one floor height, legal unit limit withheld, the
three rule-field / integration / yard gaps, the M5-T144 fingerprint gap. 10 -> 12 gaps.

### Checks (direct exit codes)
- `ruff check .` (from services/api): 0 (All checks passed).
- `pytest register + calc + reference_cases + journey`: 0 - 198 passed (calc file alone: 53 passed).
- `render_review_register.py --check`: 0 (register check PASSED).
- `modularity_check.py --check`: 0.
- `check_lane_paths.py --coverage`: 0 (9736 files).
- `git diff --stat 455caec4 -- docs/zoning-rule-review/rules`: empty (23 rule pages unchanged).
- Mutation (temp copy outside the repo): changed step 2's verdict side_missing -> agree, re-rendered
  (stale-page check CLEAN `[]`), `step_verdict_errors` still RED ("step 2 program side is withheld, so
  its verdict must be 'side_missing'"). Guard holds.

### Scope notes / what I could not settle on my own
- The two calc-test-file assertion updates and the six evidence-log refreshes sit just outside the
  literal second-half file list (register.json + renderer docs + report), but are my own first-half
  test file / the register's own GUIDE-mandated run logs - not checker/renderer code and not another
  builder's files. Both were REQUIRED for a truthful, green suite: the test assertions were staled by
  PART E's document regeneration and by this half's own verdict moves. Flagged here for the reviewer.

END-OF-REPORT

## Third round (resync: the live-route fix and the areas-agree wiring)

Built on `0c048485f1f69fc554543050542897695968e0b3`. `three_way_document.py` changed again (PART B's
live-route fix, W13 a, and areas-agree wiring, W13 b), so the register check failed on two entries.
No checker/renderer code; no human decision; no test-file edit (the test file is unchanged and no
six-step verdict moves, so no assertion was legitimately moved). ACTUAL sides read from the program's
behaviour; the committed benchmark document did NOT change.

### Entries changed
- `calc-preliminary-apartment-estimate`: code module `three_way_document.py` resynced (new combined
  code identity `5b04627f...`), automated-test evidence resynced (commit `0c048485`, 53 passed); text
  now follows that building B's estimate is given on every path where the allowance is shown and
  building A's estimate where the two lot areas agree. Revision 3 -> 4, history appended.
- `calc-first-building-option-complete`: code module `three_way_document.py` resynced (new combined
  code identity `03b418ce...`), evidence resynced. The six-step actual sides come from the committed
  benchmark document, which did NOT change (the benchmark areas disagree), so NO step verdict moves -
  stated in the history line. Revision 3 -> 4.
- `calc-lot-coverage-by-portion` (text only; its code modules did not change): the text now follows
  the three cases - coverage by portion available with its figures where the two lot areas agree,
  withheld where they disagree (the benchmark), withheld with the outline-not-available reason where
  the outline is missing (W1/W13). Revision 3 -> 4 (interpretation_changed), history appended.
- `calc-building-option-floor-stack` (text only): the text now follows the live-route fix - building
  B listed on every path where the allowance is shown (it rests on the recorded lot area, not the
  outline), building A listed where the two lot areas agree. Revision 3 -> 4 (interpretation_changed).
- Coverage gaps 2, 4, 6 (building-option / lot-coverage / estimate) reworded to the realised
  areas-agree case; none dropped while true; 12 gaps kept.
- `calc-floor-area-allowance` and `calc-legal-dwelling-unit-limit`: unchanged (their code and the
  benchmark are unchanged).

### Checks (direct exit codes)
- `ruff check .` (from services/api): 0. `pytest register + calc + reference_cases + journey`: 0 -
  198 passed (calc file alone 53). `render_review_register.py --check`: 0. `modularity_check --check`:
  0. `check_lane_paths --coverage`: 0 (9738 files). `git diff --stat 0c048485 -- docs/zoning-rule-
  review/rules`: empty (23 rule pages unchanged).

### Scope note
Two evidence logs (`calc-preliminary-apartment-estimate.txt`, `calc-first-building-option-complete.txt`)
refreshed to commit `0c048485` per GUIDE step 2, matching the resynced `automated_tests` fields; the
other four entries' logs are unchanged (their code/tests and recorded run are still valid).

END-OF-REPORT
