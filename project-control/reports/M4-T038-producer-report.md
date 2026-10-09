# M4-T038 producer report - calculation entries in the zoning-rule review register

Producer: rules-engineer (an AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-aae9c4b7d4c93111d`. Claim-base head (parent
of the producer commit): `28026c5efbf1ad879b7cb4fbe3f8b36bbd1d153f`. No push, no ledger, no rule,
calculation, result, fixture or human-verdict change. Not legal advice (ADR-007).

## What was built

The register gained a sibling `calculations` collection (schema_version 1.0 -> 1.1, additive; the 23
rule `entries` and the rule `history` are byte-identical to the claim head - verified). The
calculation renderer and checker live in one new focused module
`services/api/app/rules/review_register/review_register_calculations.py`, wired into
`render_review_register.py` and `check_review_register.py` by minimal delegation (old import paths
kept). The calculation detail pages render to the new `docs/zoning-rule-review/calculations/` folder;
`REGISTER.md` gained a Calculations table and a Coverage-gaps section; `HISTORY.md` gained a
Calculations-history section; `GUIDE.md` gained a hand-written "Calculation entries" section.

Each calculation entry has no rule file, so it is fingerprinted by the LF-sha256 of its scenario-
engine code module(s) and a combined `code_identity_sha256`; a module drift fails the check and flips
the test result to `Not run`, exactly as a changed rule file is caught for a rule entry. The expected
side is always an independent reference case (`case#row`); the actual side is the program's own
answer, read from the committed results document or recomputed through the engine's functions for a
figure the engine computes and the document withholds. Expected is never taken from a program run.

## Entries added (6)

| id | kind | combines | code modules (fingerprinted) | example state | agrees |
|---|---|---|---|---|---|
| calc-floor-area-allowance | calculation | r6-r12-residential-far | answers.py, result_ways.py | available_conditional | true |
| calc-lot-coverage-by-portion | calculation | r6b-lot-coverage | result_ways.py, geometry.py | withheld | null |
| calc-building-option-floor-stack | calculation | r6-r12-residential-far, r6b-height | building_option.py, result_ways.py | not_available | null |
| calc-legal-dwelling-unit-limit | calculation | r6b-dwelling-units | dwelling_units.py, result_ways.py | withheld | null |
| calc-preliminary-apartment-estimate | calculation | r6-r12-residential-far | three_way_document.py | not_built | null |
| calc-first-building-option-complete | calculation_comparison | r6-r12-residential-far, r6b-lot-coverage, r6b-height, r6b-dwelling-units | result_ways.py, three_way_document.py | (six steps) | n/a |

Plus `calculations_history` (6 `created` events, seq 1-6, revision 1, 2026-10-09) and a top-level
`coverage_gaps` list of 9 gaps.

## States and tests (state / independent expected / a test that pins it)

| Calculation | Program state | Independent expected (case#row) | Test |
|---|---|---|---|
| floor-area-allowance | available-conditional 20,150 sq ft | real-lot#L1 = 20,150; step-p5#floor-area-ratio-made-up-100x100 | test_calc_floor_area_recomputed_matches_independent |
| lot-coverage-by-portion | withheld (no single whole-lot figure) | step-p6#real-lot-coverage-by-portion (not known; two readings) | test_document_actuals_match_the_recorded_fixture |
| building-option-floor-stack | not_available (coverage withheld) | step-p6#real-building-a/b, made-up-building-a/b | test_engine_sample_stack_differs_from_independent_two_buildings |
| legal-dwelling-unit-limit | withheld (engine computes 29) | real-lot#L6 = 29; step-p6#real-unit-limit | test_calc_unit_limit_engine_computes_29_document_withholds |
| preliminary-apartment-estimate | not_built | step-p6#real-estimate-a/b | test_document_actuals_match_the_recorded_fixture |
| six-step page | mixed (see below) | step-p6 rows | test_six_step_page_has_six_steps_and_closing_names_db210 |

## The six-step page (expected / actual / verdict)

1. Property inputs - expected: R6B; overlay C2-2; corner; recorded 10,075 vs outline 10,387.99;
   10-ft floor-to-floor (real-lot#L9/L10, step-p6#real-lot-recorded-vs-measured-area). actual:
   same, shown as a condition. **agree.**
2. Footprint / lot coverage by portion - expected: no single figure, corner ~9,997.5 at 100% +
   strip ~390 at 80% = ~10,310 (step-p6#real-lot-coverage-by-portion). actual: withheld. **a side
   is missing.**
3. Each floor's area and height - expected: real A 1 storey ~10,310 at 10 ft; real B 3 storeys of
   6,716.67 at 30 ft (step-p6#real-building-a/b). actual: not_available; the engine's method differs
   from the two buildings. **differ.**
4. Total floor area - expected: real B 20,150 (step-p6#real-building-b). actual: not_available. **a
   side is missing.**
5. Applicable legal unit limit - expected: 29 (real-lot#L6, step-p6#real-unit-limit). actual:
   withheld (engine computes 29, document withholds pending special-density evidence). **a side is
   missing.**
6. Separate preliminary apartment estimate - expected: 20,150 x 0.60/700 = 17.27, x 0.75/700 = 21.59
   (step-p6#real-estimate-b; preliminary). actual: not_built. **a side is missing.**

## Every disagreement and missing fact (from the six-step closing)

Disagreements: (a) design assumption that differs - the engine stacks one uniform widest plate to a
partial top floor (made-up lot: 3 floors 8,000/8,000/4,000 = 20,000 at 30 ft) while the independent
example offers two buildings; backlog **DB-210**, the owner's pending choice of which building the
first option shows; settled by the generator's design and the owner's choice. (b) missing fact about
the property - recorded lot area 10,075 vs outline 10,387.99 (~313 sq ft); floor area rests on the
recorded area, footprint on the outline, so the widest same-plan building is one storey (DB-210 a);
settled by a survey/deed. (c) missing fact - the two readings differ in the footprint decimals; both
held; settled by a surveyed outline. Missing facts: code not built (coverage by portion, the
building-option generator and floor schedule, the estimate - program gap_kind work_owed /
rule_not_implemented); code not built (the legal dwelling-unit limit - the program's gap_kind is
work_owed and its reason is the display "has not been worked out and checked against an independently
worked example"; the law is read and the cases read the lot outside both special density areas, so
the kind is code not built, not unresolved law; the engine computes 29 internally); missing property
facts (rear yard beyond the corner, adjoining lot-line types, neighbouring street walls, ground
elevations - step-p6#real-lot-missing-facts; program gap_kind missing_information).

## Coverage gaps stated (9; R703)

The scenario three-answers engine still has no single entry of its own; the building-option/floor-
stack calculation; lot coverage by portion; the withheld legal-unit-limit decision; the unbuilt
preliminary estimate; the 23 rule entries have no dedicated units/measurement/formula/rounding
fields; integration.py and wide-street determination; front/side yard and street-wall rules; and
**task M5-T144 changed the scenario engine but moved no register entry** (the new entries now
fingerprint result_ways.py, geometry.py and three_way_document.py, so a later change is caught).

## Inventory: confirmed vs different

Confirmed against the code myself: the building option is withheld unconditionally
(`result_ways._building_option_withheld` returns True); max_lot_coverage, legal_unit_limit_standard
and building_option are withheld/not_available in the committed results document; the engine computes
floor area 20,150 (r6-r12-residential-far rule) and the dwelling-unit count 29 (r6b-dwelling-units
rule, 20,150/680 = 29.63 -> 29); the apartment estimate is not built (three_way_document);
`compute_building_option(20000, 8000, 55, 10)` returns 3 floors (8,000/8,000/4,000) = 20,000 at 30
ft. Different from the inventory: (1) the inventory (written at 65c60679) treated the step-P6 case as
"being written"; ruling C3 confirms it is integrated at the claim base, so I bound every expected
side to it - no entry waits on a gap. (2) A few inventory line numbers have drifted slightly from the
current head (the functions are the same); I fingerprinted whole modules, not lines.

## Correction (second commit): each gap's kind agrees with the program's own kind and the cases

The orchestrator read the six-step page and asked that the kind of every gap naming a withheld result
match the program's own `gap_kind` for that result and the reference cases. I added a structured
`program_results` field to each closing row and verified it against the committed results document.
The one changed kind:

| Page (closing row) | Old kind | New kind | Rests on |
|---|---|---|---|
| calc-first-building-option-complete / legal dwelling-unit limit | unresolved law | code not built | fixture `legal_unit_limit_standard.gap_kind` = `work_owed` + its reason ("has not been worked out and checked against an independently worked example"); the law is read and step-p3#manhattan-core ("not in the Manhattan Core"), step-p3#special-downtown-brooklyn-district ("outside ... on the recorded facts") and step-p1#special-density-areas-list read the lot outside both special density areas, so the gap is the unbuilt connected-evidence/checked display, not the law |

Every other listed kind already matched the program and is unchanged: the coverage/generator/estimate
cluster = code not built (max_lot_coverage and building_option `gap_kind` work_owed; floor_stack and
unit_estimate `reason_kind` rule_not_implemented); the rear yard = a missing fact about the property
(rear_yard `gap_kind` missing_information). I also aligned the `calc-legal-dwelling-unit-limit`
component page's prose (exceptions, gaps, coverage_gap, engine note) and linked the two step-p3 /
step-p1 special-density cases. New test `test_every_listed_withheld_gap_kind_agrees_with_the_program`
enforces this for every listed gap naming a withheld result; mutation proof
`test_a_mismatched_gap_kind_is_caught` (a deep copy, not the committed file) mislabels the legal unit
limit "unresolved law" and the enforcement catches it.

The engine-method recompute (point 3): the floors 8,000 / 8,000 / 4,000 at 30 ft are recomputed
through the engine by `test_engine_sample_stack_differs_from_independent_two_buildings`, which calls
`app.scenario.three_answers.building_option.compute_building_option(allowance_sf=20000.0,
plate_sf=8000.0, max_building_height_ft=55.0, floor_to_floor_ft=10.0)` and asserts
`floor_rows == [8000.0, 8000.0, 4000.0]`, `building_height_ft == 30.0`, `floors_built == 3`.

## Checks (each with its direct exit code; lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider)

1. `cd services/api && ruff check .` -> **0** (All checks passed).
2. `cd services/api && pytest tests/rules/test_zoning_rule_review_register.py
   tests/rules/test_zoning_rule_review_register_calculations.py` -> **0** (86 passed: 44 existing +
   42 new).
3. `render_review_register.py --check` -> **0** (register check PASSED).
4. `tools/modularity_check.py --check` -> **0** (0 failures; the new module warns at 715 SLOC, above
   the 600 warning threshold and below the 750 justification threshold - see note).
5. `scripts/lanes/check_lane_paths.py --coverage` -> **0** (LANE COVERAGE PASS).
6. (brief's extra) `cd services/api && pytest tests/rules/reference_cases tests/journey` -> **0** (101
   passed). The journey test proves the committed results document byte-equal to the program output,
   so the document-read actual side equals the program (ruling C2).

The 42 new tests include the required mutation proofs, each on an in-memory/temp copy (never a
committed file): a changed code module is caught; a cited row that does not exist is refused; a
superseded cited row is refused; a 'not known' reading cannot be a forced single figure; the words
'preliminary assumption' removed is refused; a figure left unmarked is refused; a decision typed into
a human-review block without a named reviewer/identity is refused; and a gap kind that disagrees with
the program's own kind is caught.

## Modularity note (cohesion justification)

`review_register_calculations.py` is 715 SLOC, above the 600 warning threshold (a warn, not a CI
failure; under the 750 justification and 1000 hard thresholds). The allowed paths permit exactly one
new module, and the packet mandates one focused module for the calculation collection, so the file is
not split. It has a single responsibility - the review register's calculation collection - and is
internally two cohesive halves (the checker helpers and the Markdown renderer for that one
collection), mirroring the existing check/render split that the one-module constraint collapses here.

## Scope, limitations, assumptions

- Only the 11 allowed paths changed; `git status` confirms no forbidden path was touched; no rule,
  scenario/calculation code, result, fixture or human-verdict field changed. The existing register
  test `test_zoning_rule_review_register.py` did NOT need changing (ruling C8): the calculation
  history lives in a separate `calculations_history` list, so the rule-entry history and its tests
  stay byte-identical; the checker's top-level key set and `validate` were extended in the allowed
  `check_review_register.py`.
- `tested_commit` on each calculation entry is the claim-base code head (the scenario modules are
  unchanged by this task); the staleness check binds to file digests, not the commit.
- The engine's sample floor stack is demonstrated on the made-up interior lot stated in the entry
  (the benchmark program side is withheld because coverage is withheld); the method difference is
  recorded as a design assumption that differs and names DB-210, resolving nothing (rulings C2/C4).
- The full services/api pytest suite and the dependency/security checks run in CI on the pushed head
  (not run locally per the thin-client policy).
