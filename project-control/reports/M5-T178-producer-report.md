# M5-T178 architect-entered facts feed the results — producer report

Task: M5-T178 (backend). Directive D-094-R103 (architect-entered facts feed the results, each
result resting on the architect's value, never mistaken for a city record) and D-094-R285
(missing stays missing; conditional stays conditional). Producer: backend-engineer.
Contract head reset to: `3627b572`. Worktree isolated (not the primary checkout).

## What an architect's survey value now changes

An architect can send a SURVEY measurement of a lot value (area, frontage or depth) through a
new, optional, provenance-tagged `entered_facts` request field on
`POST /api/v1/properties/{bbl}/results`. Each entry becomes a `survey_entered` site fact merged
BESIDE the city fact in the study (never overwriting it), so the already-accepted labelled-input
channel (`app.contracts.evaluator_inputs.build_evaluator_inputs`) chooses the survey value as the
governing engine input and keeps the city record visible in that record's `displaced`. Every
dependent answer recomputes from the architect's value. With no entered facts the document is
byte-identical to the city-record baseline (verified). No contract schema change, no engine edit:
the `survey_entered` rank, `displaced` and the weakest-input label already exist and are accepted.

Every check passed (exit 0; counts below).

## Files changed

- NEW `services/api/app/api/v1/entered_facts.py` — the channel's one responsibility:
  `parse_entered_facts` (body-gate validation → typed `EnteredFactsError`) and
  `merge_entered_facts` (mints contract-valid `survey_entered` site facts beside the matching
  city fact; never mutates the input study).
- `services/api/app/api/v1/results_request.py` — added `entered_facts` to `ALLOWED_BODY_FIELDS`,
  carried the parsed `tuple[EnteredFact, ...]` on `ResultsRequest`, re-raised `EnteredFactsError`
  as `ResultsRequestError` for the 422 gate, and updated the refusal message + module docstring so
  a RAW lot fact stays refused while the provenance-tagged channel is named as accepted.
- `services/api/app/api/v1/results_read.py` — call `merge_entered_facts(study, req.entered_facts,
  retrieved_at=computed_at)` after `study_from_study_setup` and before `build_evaluator_inputs`;
  map `EnteredFactsError` (unplaceable survey value) to the existing `lot_conditions_unconfirmed`
  503 (fail safe, nothing fabricated).
- `services/api/tests/api/test_entered_facts.py` — the S1–S8 acceptance pack (31 tests).
- `services/api/tests/api/test_results_read_api.py` — T10 docstring updated (the "only three
  allowed fields" wording now names the fourth accepted channel; its enumerated raw-field
  refusals are unchanged and still pass).

## Key design decisions (verified against source, not the spec)

1. The survey fact copies the `street` and `lot_bbl` of the EXISTING city fact so the two land in
   the same `(engine_key, street, lot_bbl)` group in `_grouped_known_facts`; the governing
   precedence (`_GOVERNING_PRIORITY`: survey_entered=0 < city_records=2) then selects the survey
   value and displaces the city fact. Confirmed by probing the live benchmark study
   (`lot_area` one group street=None/bbl=4073340070; `lot_frontage` TWO groups — a corner lot's
   215 Place + Northern Boulevard; `lot_depth` one group).
2. Fail closed, never guess (D-094-R285, CLAUDE.md principles 3/4): when an entered input has no
   single recorded group to sit beside (none at all, or several on different streets/tax lots),
   `merge_entered_facts` raises. On the benchmark, a survey `lot_frontage` therefore returns a
   bounded 503 (two frontages — which one the survey replaces is not settled), demonstrated by
   `test_s4_unplaceable_survey_value_fails_closed_to_503`. A survey `lot_area`/`lot_depth` (one
   group each) governs on the live route.
3. Basis enum closed to `survey` only (RISK 2): a survey value is already labelled
   "Survey measurements" with no engine edit or new owner wording. The plain-entered basis + DB-114
   chip, the per-ANSWER label, existing floor area, zoning-lot grouping and the web wiring are the
   named follow-ons — deliberately not built.
4. Minted survey source: `kind: survey`, non-null `document_ref` (site_fact.schema requires a
   string document_ref for a survey source — checked) AND a non-null `statement` (the spec's
   wording). No echo of a free-text caller value in any error message (a duplicate names only the
   closed-enum input key).

## Checks (direct exit codes; lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider; api from services/api)

- `python -m ruff check .` (from services/api) → **exit 0** ("All checks passed!").
- `flock heavy-run.lock pytest -q tests/api/test_results_read_api.py tests/api/test_entered_facts.py
  tests/contracts/test_evaluator_inputs.py tests/scenario/three_answers/test_three_answers_c6_c11.py
  tests/journey/test_215_16_northern_journey.py` → **exit 0, 188 passed** (consumer sweep green:
  T10, the evaluator channel, the chip test and the journey test all unchanged).
- `python tools/modularity_check.py --check` → **exit 0** (823 files; failures 0; the 35 warnings
  are pre-existing and name none of this task's files; entered_facts.py is well under WARN 600).
- `python tools/research_record_check.py --check` → **exit 0** ("PASS: every record is structurally
  valid…"; no evidence record touched).
- `python scripts/lanes/check_lane_paths.py --coverage` → **exit 0** ("LANE COVERAGE PASS: 11065
  file(s), each owned by exactly one lane.").
- `flock heavy-run.lock pytest -q` (WHOLE api suite, from services/api) → **exit 0,
  10213 passed, 8 skipped** in 565.45s. This task changes the live results route; the full suite is
  green at this head.

## Mutation proofs (each new behaviour test reverts to red; source restored after each)

- Merge → no-op (`merged = copy.deepcopy(study)` → `return study`): **5 red** —
  `test_s2_*governs_and_recomputes`, `test_s2_*governing_record_city_in_displaced`,
  `test_s3_*governs_and_displaces`, `test_s7_*validate`, `test_s8_all_survey_*`.
- `len(groups) != 1` → `len(groups) < 1`: **1 red** —
  `test_s4_unplaceable_survey_value_fails_closed_to_503` (corner lot no longer fails closed).
- Refusal message reverted to drop every `entered_facts` mention: **1 red** —
  `test_s5_refusal_message_distinguishes_the_entered_facts_channel`.
- Value guard `… or value <= 0` dropped: **3 red** — the two `entered_fact_value_invalid`
  parametrisations (value 0, value -5) and `test_s6_present_value_is_never_confused_with_an_absent_channel`.
- `if raw is None:` disabled: **1 red** — `test_s1_absent_channel_is_byte_identical_*[extra1]`
  (`entered_facts: null` no longer treated as an absent channel).

## Scenario → evidence

- S1 byte-identity → `test_s1_*` (absent / null / empty all blank-identity-equal to the baseline;
  baseline floor area = 2.00 × 10,075; chip "Approximate measurements").
- S2 survey lot area governs → route `test_s2_*governs_and_recomputes` (floor area = 2.00 × 10,388
  = 20,776, not 20,150) + evaluator `test_s2_*governing_record_city_in_displaced` (lot_area record
  survey_entered 10,388, PLUTO 10,075 in `displaced`).
- S3 survey frontage governs/displaces → `test_s3_*` on a single-frontage study.
- S4 duplicate → 422 at gate; unplaceable → 503; no-recorded-value → fail closed.
- S5 bare lot fact still refused (T10 preserved) + message names the channel.
- S6 value/basis/input/shape validation (incl. raw-JSON NaN/Infinity → 422 not 500; present 0 ≠
  absent channel).
- S7 merged study + evaluator inputs validate against their contracts.
- S8 all-survey → "Survey measurements"; one survey beside a city input keeps
  "Approximate measurements" while the survey still governs its input.

## Report print

Not applicable: this task changes the results input channel, not any report PAGE. The no-channel
document is byte-identical (S1); the web wiring that would send entered_facts from the preview is
named follow-on D (not built), so the live report/preview is unchanged. No drawings, PDF, evidence
record, review register or zoning-rule-review file touched (confirmed by research_record_check and
the forbidden-paths list).

## Figures

From `docs/reference-cases/R6B/cases/real-lot.json` (never a program run): PLUTO lot area
10,075 sq ft; PLUTO lot front 100.76 ft; MapPLUTO outline ~10,388 sq ft. Tests use these, not
emitted values.

## What I did not check

- No browser / web / e2e run (no apps/web change; the web wiring is follow-on D). The brief's
  web-check path does not apply.
- No report-print render (no report-page change, per above).
- Behaviour is read from source at the reset head and proven by the executed tests above; an engine
  output is not independent legal verification (ADR-007 label stands).

## Round 2 (review findings closed; commit on top of round-1 `c62839d5`)

The four reviews (data-contract, code, test, security) all PASSED round 1. Round 2 closes the
REQUIRED data-contract finding 1 and the advisories the reviewers converged on. No contract
schema, engine, scenario, web, evidence-record or zoning-rule-review file touched (same scope).

### What an architect now sees for a refused entry (the owner's truthfulness standard)

- **Corner-lot frontage (the REQUIRED fix, item a).** A survey `lot_frontage` on a lot with two
  recorded frontages on different streets used to become the **503 `lot_conditions_unconfirmed`**
  whose message said the city record or lot outline "could not be read" — FALSE (the same lot
  answers 200 for a survey `lot_area`). It is now a typed **422** (`validation_error`, code
  `entered_fact_needs_street`) whose message states the true cause and the remedy. Live on the
  benchmark: *"the survey lot frontage cannot be applied on its own: the city record has 2 recorded
  lot frontages for this lot, on 215 Place and Northern Boulevard. Enter the survey value with the
  street it was measured on, on the lot's site-facts screen."* The street names come from the city
  record, never caller text. The 503 is no longer reachable for an entered-fact cause.
- **No recorded value (item a).** A survey value for an input the lot has no recorded value for is
  now **422** `entered_fact_no_recorded_value`: *"the survey lot depth cannot be applied yet: the
  city record has no recorded lot depth for this lot for the survey to replace, and entering a
  measure the city record is missing is not available yet."* No "could not be read".

### Items b–d

- **b (provenance).** The minted survey fact now copies `contract_version` from the matched city
  fact it sits beside (`_survey_fact(..., contract_version=city_fact["contract_version"])`), so a
  survey beside the live 1.1.0 `lot_area`/`lot_depth` city facts is itself 1.1.0, not a hardcoded
  1.0.0. The merged study stays schema-valid (verified by `validate_study_document`).
- **c (defense in depth).** `results_read.py` calls `validate_study_document(study)` after the merge
  (only when the channel added a fact) and before `build_evaluator_inputs`. NOTE (honest): this is
  **redundant today** — `build_evaluator_inputs` validates the study as its own first step
  (`app/contracts/evaluator_inputs.py:360`), so a minting regression was already a clean
  `internal_contract_error`, not a generic 500. The explicit call makes the route's "merged study
  is contract-valid before use" guarantee LOCAL and independent of `build_evaluator_inputs`
  internals. Because the guarantee is held jointly, there is **no mutation that isolates this one
  line** (removing it leaves the guard test green via `build_evaluator_inputs`); the guard test
  discriminates on the injected malformation (bad minted fact → 500 `internal_contract_error`; the
  normal S2 path → 200).
- **d (defense in depth).** `merge_entered_facts` now uses `_INPUT_TO_SITE_KEY.get(...)` with a
  typed `entered_fact_input_invalid` refusal for an input outside the closed enum (never a
  `KeyError` → generic 500), guarding a future direct `EnteredFact` caller. `parse_entered_facts`
  now bounds the list length to the closed input count (`entered_facts_too_many`) before any
  per-item work.

### Follow-ons recorded (item e; NOT built)

- A survey entry can only **displace a known** city value today; it cannot **FILL** a missing or
  unknown city value (the no-recorded-value 422 above is the chosen, visible limit). Filling a
  missing/unknown measure needs the standalone/street-qualified entry path — named follow-on
  (part of the website entry wiring, follow-on D / survey reader E).
- The **tax-map drawing measure 10,387.99 sq ft** (MapPLUTO `Shape__Area`, labelled in
  `real-lot.json` L1 as a drawing measure "never used in a floor-area calculation") must **never**
  be piped into the survey channel as a survey value. The tests use 10,388 only as a synthetic
  "architect's entered value" to exercise the plumbing; the live route sends no `entered_facts`
  yet. The website wiring (follow-on D) must take a real survey measurement, not the tax-map
  drawing figure.

### Round-2 checks (direct exit codes; lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider; api from services/api)

- `python -m ruff check .` (from services/api) → **exit 0** ("All checks passed!").
- `pytest -q tests/api/test_entered_facts.py` → **exit 0, 36 passed** (was 31; +5 round-2 tests;
  2 S4 tests repurposed 503→422).
- `flock heavy-run.lock pytest -q tests/api/test_results_read_api.py tests/api/test_entered_facts.py
  tests/contracts/test_evaluator_inputs.py tests/scenario/three_answers/test_three_answers_c6_c11.py
  tests/journey/test_215_16_northern_journey.py` → **exit 0, 193 passed** (was 188; consumer sweep
  green).
- `python tools/modularity_check.py --check` → **exit 0** (824 files; failures 0; none of this
  task's files flagged; entered_facts.py 354 / results_read.py 467 SLOC, under WARN 600).
- `python3 tools/research_record_check.py --check` → **exit 0** ("PASS"). The NB-04
  `code_current=False` note is pre-existing and unrelated: this task touches none of NB-04/NB-05's
  pinned `code_paths` (density/result-way files).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → **exit 0** ("LANE COVERAGE PASS").
- `flock heavy-run.lock pytest -q` (WHOLE api suite, from services/api) → **exit 0,
  10218 passed, 8 skipped** in 548.91s (round 1 was 10213 passed; +5 round-2 tests). The live
  results route changed; the full suite is green at this head.

### Round-2 mutation proofs (each new behaviour test reverts to red; source restored after each)

- Item a route 422 → `_lot_conditions_unconfirmed_503`: **1 red** —
  `test_s4_unplaceable_corner_frontage_is_a_truthful_422` (503 != 422).
- Item a merge street naming (`streets = []`): **2 red** —
  `test_s4_multi_frontage_message_names_the_streets_from_the_record` and
  `test_s4_unplaceable_corner_frontage_is_a_truthful_422` (street names dropped from the message).
- Item a no-value code → old `entered_fact_not_placeable`: **1 red** —
  `test_s4_entered_fact_for_an_input_with_no_recorded_value_is_a_truthful_refusal`.
- Item b `contract_version` → hardcoded `"1.0.0"`: **1 red** —
  `test_minted_survey_fact_copies_the_city_facts_contract_version` (expects 1.1.0).
- Item d length bound disabled (`if False and …`): **1 red** —
  `test_entered_facts_list_is_bounded_to_the_closed_inputs` (4-item list then hits the duplicate
  check: `entered_fact_duplicate_input` != `entered_facts_too_many`).
- Item d unknown input (`.get` → `[...]`): **1 red** —
  `test_merge_refuses_an_unknown_input_with_a_typed_error` (a `KeyError` is raised, which
  `pytest.raises(EnteredFactsError)` does not catch).
- Item c: no isolating mutation (redundant with `build_evaluator_inputs` validation, per item c
  note above); the guard test `test_merged_study_is_contract_guarded_before_use` discriminates on
  the injected malformation.
