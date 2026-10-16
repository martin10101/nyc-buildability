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
