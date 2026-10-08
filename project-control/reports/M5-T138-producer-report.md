# M5-T138 producer report — the internal results route (R6B work order, Part A)

Producer: backend-engineer (an AI agent), in an isolated worktree reset to the claim-seam head
`2eb714abff96f08bf3a37b8a25352fc549958631`. One internal route
`POST /api/v1/properties/{bbl}/results` behind a new default-off switch `INTERNAL_RESULTS_ENABLED`,
calling ONLY the evidence entry `run_engine_and_result_ways_from_evidence` (ruling R1). The engine,
the decision modules, that entry, the three-way transform, every schema and fixture, and the
provider are not edited. `study_read.py` is edited only to import the extracted shared builder
(behaviour unchanged; a compatibility facade keeps its former private `_build_document` import).

## Files changed (all within the 16 allowed paths)

- `services/api/app/config.py` — new `INTERNAL_RESULTS_ENABLED_ENV_VAR` + `internal_results_enabled()`.
- `services/api/app/api/v1/build_info.py` — `INTERNAL_RESULTS_ENABLED` added to `FLAG_ENV_VARS`.
- `services/api/app/api/v1/study_setup_document.py` — the shared study-setup builder (extracted).
- `services/api/app/api/v1/study_read.py` — imports the shared builder; `_build_document` is a
  compatibility-facade alias (behaviour byte-identical; its tests stay green unedited).
- `services/api/app/api/v1/results_request.py` — the body reader/validator + the option builder.
- `services/api/app/api/v1/results_read.py` — the route (guards, typed matrix, chain).
- `services/api/app/main.py` — mounts the route in the study-read posture.
- `services/api/tests/api/test_results_read_api.py` — WIRING tests (T1-T3, T9-T11, S15, import pin).
- `services/api/tests/api/test_results_read_law_examples.py` — LAW tests (T4-T8, S13/S14, made-up lots).
- `services/api/tests/api/test_study_live_outline_provider.py` — DB-190 a direct test (S12).
- `services/api/tests/api/test_build_info_api.py` — `EXPECTED_FLAGS` + `_OWNER_READERS` pin.
- `docs/lanes/queues/C.md`, `docs/lanes/status/C.md`, `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md`
  — the stale golden-record / "flip the tests that assert it stays unmounted" lines (no behaviour).

`services/api/tests/api/test_read_router_mounts.py` (allowed) is LEFT UNCHANGED: its GET-parametrized
`ALL_ROUTES` pattern does not fit a POST route (a GET to a POST path is 405, not 404), so per ruling
R6 the same mount assertions (flag-off 404 byte-identical, OpenAPI absence in both states, flag-on
reachability) are made in `test_results_read_api.py` instead (T1).

## FILE BEYOND THE 16 ALLOWED (route to orchestrator — not edited here)

`services/api/tests/scenario/three_answers/test_result_ways.py`
(`test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module`) scans every
`services/api/app/**.py` for the literal `result_way` and permits a fixed list. The route MUST name
the evidence entry `run_engine_and_result_ways_from_evidence` (ruling R1), whose name contains the
substring `result_way`, so `results_read.py` is flagged as an offender (confirmed: it is the ONLY
offender; `results_request.py` has 0 occurrences). Required one-line fix, OUT OF SCOPE here: add
`"results_read.py"` to the permitted set (the route is the intended new consumer of the evidence
entry). This is the single failure in check (c).

## Table (a) — the option document and the minted identity (ruling R2)

Built by `results_request.build_option(req, option_id=…)` + the route's minting. None is a fact
about the lot.

| field | value | source | why |
|---|---|---|---|
| option.option_id | minted `uuid4().hex` | minted | the study needs a `selected_option_id`; not a lot fact |
| option.name | `"Requested option"` (constant `OPTION_NAME`) | neutral constant | a display name; not a lot fact |
| option.addon_selection | `[]` | neutral | nothing selected (smallest valid array) |
| option.goal | `{"kind":"most_residential_floor_area","text":null}` | schema-default goal | the neutral default; not a lot fact |
| option.program | `["market_rate_residential"]` / `["affordable_residential"]` / `["senior_residential"]` mapped from the body's housing program | the user's housing choice in the option schema's own vocabulary | an option CHOICE (what to build), not a lot fact; NOT read by the engine (see "question of interpretation") |
| option.floor_to_floor_heights.ground_floor / typical_floor | `height_ft` = body `floor_to_floor_ft`, basis `entered`; or `10.0` with basis `stated_default` when absent | the user's / the engine's stated starting value | a design choice; a default is always stated in words, never silent |
| option.floor_to_floor_heights.per_floor_overrides | `[]` | neutral | none |
| option.assumptions | `[]` | neutral | not a lot fact |
| option.existing_building_plan | `"no_existing_building"` | neutral | not a lot fact |
| study_id | minted `uuid4().hex` | minted | study identity; not a lot fact |
| revision | `{"number":1,"created_at":<computed_at>,"parent":null}` | minted | a new study at revision 1; not a lot fact |
| results_id | minted `uuid4().hex` | minted | the result's id; not a lot fact |
| computed_at | `datetime.now(UTC)` RFC3339 `…Z` | minted at request time | the result's time; not a lot fact |

Difference from the tests' `_TEST_ONLY_OPTION`: option_id is minted (vs `"opt-test"`); name is
`"Requested option"` (vs the test-synthetic name); `program` is MAPPED from the body's housing
program (vs the fixed `["market_rate_residential"]`); `floor_to_floor_heights` ground+typical both
take the body's value (basis `entered`) or `10.0` (basis `stated_default`) (vs the test's fixed
ground 12 / typical 10). `goal`, `addon_selection`, `assumptions`, `existing_building_plan` match.
The engine reads the floor-to-floor height from `BuildingDefaults`, which the route builds from the
same body value and the engine PRINTS in the scope (owner R256; verified in T6).

## Table (b) — every answer of the route (rulings R3, R5); every chain exception and its answer

| input state | status | typed body (state) | test id |
|---|---|---|---|
| switch off / non-true token | 404 | `{"detail":"Not Found"}` (no state, no correlation id) | T1 |
| more calls than the limit | 429 | `rate_limited` | T9 |
| malformed BBL (provider never called) | 422 | `validation_error` (BBL code) | T2 |
| body not an object | 422 | `validation_error` (`invalid_body`) | T10 (non-object) |
| a refused field (lot area / lot type / overlay / special district / corner / geometry / attested provenance / bbl) | 422 | `validation_error` (`field_not_accepted`, names the field) | T10 (8 cases) |
| missing housing program / program not in vocab | 422 | `validation_error` | T10 (bad) |
| bad floor-to-floor value (≤0 or non-number) | 422 | `validation_error` (`floor_to_floor_ft_invalid`) | T10 (bad) |
| bad density statement (not boolean) | 422 | `validation_error` (`special_density_statement_invalid`) | T10 (bad) |
| body too large / not valid JSON | 422 | `validation_error` (`body_too_large` / `invalid_json`) | (guarded; reasoned) |
| provider cannot produce inputs (`StudyInputsUnavailableError`) | 503 | `inputs_unavailable` | S14 |
| inputs without a property profile → the entry refuses (`EngineDisclosureError`: overlay flag can't be confirmed) | 503 | `lot_conditions_unconfirmed` (plain reason, never a document) | S14 |
| inputs with no lot-type geometry (`EvaluatorInputsError`: required engine input missing / ambiguous) | 503 | `lot_conditions_unconfirmed` | S14 (no-lot-type note) |
| inputs with no prepared outline (reach unknown, lot type known) | 200 | (reach-dependents withheld) | T7 |
| the bridged study fails its contract (`StudyContractError`) | 500 | `internal_contract_error` | (reasoned) |
| the emitted document fails its contract (`StudyContractError`) | 500 | `internal_contract_error` | (reasoned) |
| the bridge refuses (`StudySetupBridgeError`) / any other exception | 500 | `internal_error` | (reasoned) |
| success | 200 | the emitted 1.3.0 document (no `state`) | T3, T4, T5, T6, S13 |

Every pair is in `RESULTS_READ_STATUS_STATE_MATRIX`. The rate limit runs before any other work; the
BBL check before any body read or I/O; the body before the provider. Note (route vs the entry-level
S14 wording): through the route the single `StudyInputs.site_geometry` carries BOTH the lot-type
classification and the corner reach — "no outline" (reach unknown, lot type known) is the 200 case;
"no geometry at all" (no lot type) fails closed to the 503 `lot_conditions_unconfirmed` (it cannot
guess a lot type). This is a faithful consequence of one provider object, named for the reviewer.

## Table (c) — the law states (values FROM THE REFERENCE CASES, never the saved output)

| lot / state | expected | reference row | test id |
|---|---|---|---|
| recorded 215-16 Northern: floor area (standard) | 20,150 sq ft | real-lot L1 | T4 |
| recorded: floor area (qualifying) | 24,180 sq ft | real-lot L2 | T4 |
| recorded: heights (district limits, conditional) | min base 30 / max base 45 / max building 55 (+65 qual) ft | real-lot L3, L4 | T4 |
| recorded: coverage | not known → withheld | real-lot L5 | T4 |
| recorded: rear yard / building option / unit limit | withheld / not available | real-lot (H1/H2/H11) | T4 |
| made-up interior P5 (5,355 sq ft): floor area | 10,710 sq ft (conditional via the entry) | interior-lots P5-floor-area | T5, S9, S13, S6 |
| made-up interior P5: unit limit WITH the density statement | 16 (conditional) | interior-lots P5-units | S13, S19, T6 |
| made-up interior P5: two corner lines | "Not applicable" (not a corner lot) | — (ruling R4) | S13 |
| made-up corner C2 (60×80): coverage | 100 percent (conditional via the entry) | corner-reach C2-coverage | T5 |
| made-up corner C3 (150×100): coverage | not known → withheld | corner-reach C3-coverage | T5 |
| a changed floor-to-floor height | no law limit changes (floor area, heights, unit limit identical); only the floor-to-floor scope line changes | — | T6 |
| a fact not given (no outline → reach unknown) | 200; coverage + rear yard withheld; floor area shown; no zero | — (R229/R240) | T7 |
| a statement contradicting the record (density "in one") | 200; held back; unit limit stays withheld; never stored as a fact | — (R255) | T8 |

LAW = T4-T6; LAW+WIRING = T7/T8; WIRING = T3. Every figure is loaded from the reference-case JSON in
the test and asserted `== <literal>` so a drift in either side fails. No test accepts a value because
it equals a saved program output; T3 compares the route's document to a fresh entry call (not a file).

## Red proofs (before the route exists — run against an app with the route unmounted)

```
RED (reachability): status = 404 -> expected 200; FAILS
RED (route==entry): 'answers' in body = False -> the document comparison FAILS
RED (refused field): status = 404 -> expected 422; FAILS
```

## Mutation proofs (one per pinned branch; run in-process OUTSIDE the repo — no repo file mutated)

```
MUTATION 1 (interior-as-corner, ruling R4): within scope value = 'Not known' -> S13 assertion 'Not applicable' FAILS = True
MUTATION 2 (404 identity): X-Correlation-ID present = True -> T1 byte-identity FAILS = True
MUTATION 3 (refused field): status = 200 -> T10 '422' FAILS = True
```

Mutation 1 is the mandatory R4 proof: patching `_is_corner` so the entry treats the interior lot as
a corner lot turns its two corner scope lines from "Not applicable" into "Not known", so S13 fails.

## Tests on a value that MAY be absent (no truthiness test on any of them)

- `floor_to_floor_ft`: presence tested with `"floor_to_floor_ft" in body`; when present, refused
  unless it is a non-bool number `> 0`; absent → `None`. In the route, used with an explicit
  `req.floor_to_floor_ft is not None` (never a truthiness test; `0.0` could never reach it — it is
  refused — but the explicit-None guard is correct regardless).
- `special_density_statement`: presence tested with `"special_density_statement" in body`; when
  present, refused unless it `isinstance(…, bool)`; absent → `None`; passed as `bool | None` to the
  entry as-is (a present `False` is distinct from absent).

## Every text the route can return (plain and true; no internal path/law-capture claim; never "professional review")

- 404: `{"detail":"Not Found"}` — no state, no correlation id (byte-identical to an unknown path).
- 429: "per-caller rate limit exceeded; retry later".
- 422 messages (results_request): "the request body must be a JSON object"; "this field is not
  accepted; the request carries only the housing program, an optional floor-to-floor height and an
  optional statement about the special density area. Facts about the lot come from the city's
  records, not the request"; "a housing program is required"; "the housing program is not one the
  program offers"; "the floor-to-floor height must be a positive number of feet"; "the statement
  about the special density area must be true or false"; plus the BBL connector message, "the
  request body is larger than this route accepts", "the request body is not valid JSON".
- 503 inputs_unavailable: "the results are not available for this property right now; nothing was
  fabricated and this is safe to retry".
- 503 lot_conditions_unconfirmed: "the results are not available for this property right now: the
  city records needed to confirm the lot's conditions could not be read. Nothing was fabricated and
  this is safe to retry".
- 500 internal_error / internal_contract_error: generic "see server logs by correlation id" texts.

None names an internal module, a law section captured/built, an environment value, a stack trace, or
another lot's data; none says "professional review".

## The example-value guard here (T10 / ruling R3)

`real_property_guard.py` (the example-value guard) has NOTHING to check in this body: the body gate
refuses every lot-fact field (lot area, frontage, depth, lot type, district, overlay, special
district, corner condition, geometry, attested provenance, bbl) BEFORE any guard, so no example site
value, coordinate or attested fact can ever enter the request. T10 asserts the refusal of one case
each of those fields; that is what T10 can honestly assert here.

## Questions of law met (named, not decided by the builder)

1. The rear yard is WITHHELD on the recorded C2-2 overlay lot because the independent overlay reading
   does not yet support it (overlay-reading / step-p4-worked); this legal reading is owned by the
   read-only decision module, surfaced here, not decided by this route.
2. Interpretation point (not a law question): `option.program` maps the engine's `housing_program`
   vocabulary (`standard_residence` …) to the option schema's `program` vocabulary
   (`market_rate_residential` …) by a documented one-to-one correspondence. It is NOT read by the
   engine (the engine reads `housing_program` directly), so it changes no result; flagged for the
   data-contract reviewer in case a neutral fixed value is preferred.

## What is NOT shown (ruling / NOT-IN-THIS-TASK)

No website file (apps/web untouched — the client, the website switch, the panel and the browser
journeys are Part B, owed). No production switch turned on (`INTERNAL_RESULTS_ENABLED`, `LANE_A/B/C`,
`LIVE_SPATIAL_PROVIDER_ENABLED` all stay off; the engine's Lane A gate is separate and also off in
production, so the production route is a 404 and turns no zoning computation on). No `render.yaml`,
CI, or dependency change. No change to the engine, the decision modules, the three-way transform or
the results schema. The realistic apartment estimate, development options, building shapes, the
option comparison and the PDF stay owed.

## Checks (direct exit codes)

- (a) `python -m ruff check .` (services/api) — **exit 0**, "All checks passed!".
- (b) `pytest -q tests/api` — **exit 0**, **1112 passed** (claim-seam baseline 1067; +45 new).
- (c) `pytest -q tests/scenario/three_answers tests/journey tests/contracts` — **exit 1**,
  **908 passed, 2 skipped, 1 failed**. The ONE failure is the OUT-OF-SCOPE import guard
  `test_result_ways.py::test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module`
  (needs `results_read.py` added to its permitted set — see "FILE BEYOND THE 16 ALLOWED"). No other
  change; the figure is otherwise unchanged from the baseline.
- (d) `tools/modularity_check.py --check` — **exit 0** (only pre-existing `tools/agent_supervisor`
  warnings; no new file flagged). `.github/scripts/validate_contracts.py` — **exit 0**, 23 schemas,
  0 failures (no new schema). `scripts/lanes/check_lane_paths.py --coverage` — **exit 0**,
  9527 files, each owned by exactly one lane.
- (e) the red proofs and the mutation proofs above.
- (f) `git diff --name-status 2eb714ab… HEAD` lists only the 14 edited allowed paths (+ this report);
  no forbidden file touched.

END-OF-REPORT
