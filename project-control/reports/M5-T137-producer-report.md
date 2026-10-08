# M5-T137 producer report — the engine's five conditions of a lot come from evidence

I am an AI agent (builder, role scenario-optimization-engineer). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a4b6661955116cc30`. Reset to the claim-seam
head `7b5938e4cba7c27c4d8c58db70d297816de00d2d` before work.

The older engine takes five facts of a lot as plain caller values. This piece makes those five come
from the SAME evidence the decision step gathers: one small derivation module, one new entry that
takes evidence instead of conditions, a stand-in for the engine only where a condition is not known
and only in the direction that withholds, no shown result resting on a stand-in, and the emitted
document's scope lines saying where each condition comes from. The committed journey result and its
two saved drawings are regenerated through the new entry. The engine, the decision modules, the
disclosure builder, every schema and the website source are NOT edited.

## Files changed (10; all inside the 19 allowed paths)

- `services/api/app/scenario/three_answers/engine_conditions.py` — NEW derivation (plain states in).
- `services/api/app/scenario/three_answers/result_way_engine_bridge.py` — new entry
  `run_engine_and_result_ways_from_evidence`; older `run_engine_and_result_ways` unchanged.
- `services/api/app/scenario/three_answers/three_way_document.py` — scope-line rewrite from sources.
- `services/api/tests/scenario/three_answers/test_engine_conditions.py` — NEW unit tests.
- `.../test_three_answers_three_way_emit.py` — red proof + the evidence-entry/invariant/text tests.
- `.../test_wiring_emits_nothing.py` — repointed to the new entry.
- `services/api/tests/journey/test_215_16_northern_journey.py` — repointed to the new entry.
- `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` — regenerated.
- `services/api/tests/cad/snapshots/results_dxf/recorded_215_16_northern_journey.dxf` — regenerated.
- `.../tests/drawings/kit/snapshots/recorded_215_16_northern_journey.site_plan.svg` — regenerated.

NO file was needed beyond the allowed paths. `test_result_ways.py` (the import guard) was NOT
changed: the new module takes plain states and never names the decision module, so the guard's
permitted list need not grow (`grep -c result_way engine_conditions.py` = 0; `grep -c lot_reach`
on both new files = 0). The three website test files were NOT changed (the web suite is green). The
review-register files were NOT changed (see "Questions of law / register").

## The shape of the new entry (five lines)

1. It takes what the server holds (evaluator-inputs doc, study, housing program, property profile,
   prepared outline, site geometry, the user's optional density statement, the result id and time).
2. It gathers the decision step's facts FIRST via `gather_result_ways` over that same evidence.
3. It derives the five conditions from those SAME facts with `engine_conditions.derive_conditions`
   (plain states in; the entry maps the decision step's `Recorded`/`LotType`/`DensityKnowledge` to
   the module's plain `Presence`/`is_corner`/`DensityStatement` — the module stays decoupled).
4. It builds the engine inputs with `build_three_answer_inputs` using the DERIVED values, runs the
   engine, decides the ways and emits the three-way document, passing the per-condition sources so
   the transform rewrites the five scope lines.
5. It touches no route, mount or switch; `build_three_answer_inputs`, `engine_disclosures.py` and
   every schema stay read-only. The older entry keeps its behaviour for a caller holding inputs.

## Table (a) — each condition: the engine results it moves, the evidence, the stand-in, the proof

| Condition (engine input) | Engine results it moves (file:line) | Direction | Decision-step evidence + states | Stand-in when not known | Proof the stand-in withholds (rule file) |
|---|---|---|---|---|---|
| overlay_present | `inputs.py` height_inputs:179, coverage_inputs:189, rear_yard_inputs:202 (adds a `documented_limitation` note only) | True adds a note; False adds none | recorded `commercial_overlay` (`result_way_facts.py` overlay1/overlay2) → PRESENT/ABSENT/NOT_READ | False (no note) | `r6b_height.rule.json` exc. `commercial_overlay_not_captured` (effect `documented_limitation`, condition overlay_present==true): False emits no note; the decision step's `overlay_block` withholds every residential result on a NOT_READ overlay |
| special_district_present | `inputs.py` :180,:189,:204,:214 → all four rules | True → `professional_review_required` → engine answer withholds | recorded `special_purpose_district` (`result_way_facts.py` spdist1/2/3) → PRESENT/ABSENT/NOT_READ | True | `r6b_height/_lot_coverage/_rear_yard_corner_waiver/_dwelling_units.rule.json` exc. `special_district_modification` effect `professional_review_required`; `rule_access.py:110` treats that as unusable → the answer withholds. The decision step `blanket_withhold` also withholds EVERY result on PRESENT/NOT_READ |
| within_100_ft_of_street_line_intersection | `inputs.py` rear_yard_inputs:196 (with the angle, the rear-yard waiver) | True (with angle ≤135) → waiver applies (rear_yard=0); False → not applicable, no figure | measured corner reach (`lot_reach` corner.reach, adapted in `result_way_bridge.py`) → a figure or unknown; not a corner → not applicable | False (not within 100 ft) | `r6b_rear_yard_corner_waiver.rule.json` applicability `equals within_100 == true`: False fails the predicate → not applicable → the waiver output `rear_yard_required_within_100_ft_of_corner` is never emitted |
| street_line_intersection_angle_degrees | `inputs.py` rear_yard_inputs:199 (with within_100) | ≤135 (with within_100) → waiver applies; >135 → not applicable | measured corner angle (`lot_reach` corner.angle) → a figure or unknown; not a corner → not applicable | 136.0 degrees (past the limit) | same rule applicability `compare angle le 135`: 136 fails it → not applicable; within_100=False already withholds, so this value never reaches a shown result |
| special_density_area | `inputs.py` dwelling_unit_inputs:213 | True → dwelling-unit rule not applicable → no unit figure | the user's statement (`result_way_bridge._density`) → USER_STATEMENT_NOT_IN_ONE / NOT_GIVEN; there is no recorded source today | True (inside one) | `r6b_dwelling_units.rule.json` applicability `not special_density_area==true`: True fails it → not applicable → no `max_dwelling_units`; the decision step also withholds the limit when the density is NOT_GIVEN |

## Table (b) — every input state of the new entry: state → outcome → test id

| Condition | State | Engine value / source | Test id |
|---|---|---|---|
| overlay | recorded present (C2-2) | True / recorded | `test_overlay_recorded_present_is_yes_with_the_code`; benchmark `test_s137_scope_lines...` |
| overlay | recorded absent | False / recorded | `test_overlay_recorded_absent_is_no` |
| overlay | not read | False (no note) / not known | `test_overlay_not_read_is_no_overlay_not_known`; `test_s137_invariant_special_district_not_read_withholds_everything` |
| special district | recorded present | True / recorded | `test_special_district_recorded_present_is_yes` |
| special district | recorded absent | False / recorded | `test_special_district_recorded_absent_is_no`; benchmark scope |
| special district | not read | True / not known → everything withheld | `test_special_district_not_read_uses_the_present_stand_in`; `test_s137_invariant_special_district_not_read_withholds_everything` |
| within100 / angle | corner, reach 144.60 & angle 89.7 measured | within=False, angle=89.7 / measured | `test_benchmark_corner_is_not_within_100_ft_measured`; benchmark scope |
| within100 / angle | corner C2, reach 100.00 (inclusive) | within=True / measured | `test_c2_corner_is_within_100_ft_measured` |
| within100 / angle | corner C3, reach 180.28 | within=False / measured | `test_c3_corner_is_not_within_100_ft_measured` |
| within100 / angle | not a corner (interior) | within=False, angle=136 / not applicable | `test_interior_lot_has_no_corner_conditions`; `test_s137_interior_lot_scope_says_not_applicable` |
| within100 / angle | corner, no measurement / no geometry | within=False, angle=136 / not known | `test_corner_without_a_measurement_is_not_known`; `test_s137_invariant_over_the_benchmark_states` (no-geometry) |
| within100 / angle | lot type not read, no measurement | not known | `test_unknown_lot_type_without_a_measurement_is_not_known` |
| density | user says not in one | False / the user's statement | `test_density_user_statement_not_in_one_is_no_as_a_statement`; `test_s137_invariant_over_the_benchmark_states` (with statement) |
| density | no statement | True (inside one) / not known | `test_density_no_statement_uses_the_inside_one_stand_in`; benchmark scope |

The five conditions assembled by scope key: `test_derive_conditions_keys_and_benchmark_values`. The
within-100 boundary is inclusive at 100 ft (the SAME comparison the decision step uses):
`test_the_within_100_boundary_is_inclusive_at_100_ft`. The angle stand-in is past the limit:
`test_angle_stand_in_is_past_the_waiver_limit`.

## The invariant (S11)

`_assert_no_shown_result_rests_on_a_stand_in` reads the emitted document: a condition is a stand-in
exactly when its scope-row basis is `assumed` (recorded→city_records, measured→approximate_tax_map,
the user's statement→entered). Wherever a condition is a stand-in, every result that depends on it
(special district / overlay → all residential; within_100 / angle → the rear yard; density → the
standard unit limit) must be withheld. Applied over: the benchmark (density not known), the benchmark
with the user's density statement, the benchmark with no site geometry (reach not known), the
special-district-not-read state, and the interior lot (not applicable). **No state broke the
invariant.**

## Reference-case source of every expected value

- Floor area 20,150 and 24,180 sq ft; heights 30/45/55/65 ft: `docs/reference-cases/R6B/cases/
  real-lot.json` rows L1, L2, L3, L4 (asserted in `test_s137_shown_values_and_withheld...`).
- Corner reach 144.60 ft and angle 89.7°, C2 100.00 ft, C3 180.28 ft: `corner-reach.json` rows
  `real-lot-reach`, `C2-reach`, `C3-reach`, loaded through the loader (asserted in
  `test_engine_conditions.py`), never the program's saved output.
- Interior lot (P5): `interior-lots.json` (the interior scope test uses the made-up lot).
- The measured reach/angle were produced offline by `lot_reach.measure_lot_reach` on the recorded
  benchmark pack (corner 215 Place / Northern Boulevard, reach 144.6, angle 89.7); these match the
  reference rows above.

## The red proof (S3)

`test_s137_red_committed_within_100_scope_line_agrees_with_the_measured_reach` read today's committed
journey result and FAILED before the production edit, because its scope line said the lot is
"assumed to lie within 100 feet" (value True, basis assumed) while the same document's coverage
reason says the lot "reaches 103.93 ft ... beyond the corner-lot portion". Captured output:
`AssertionError: {'basis':'assumed','key':'within_100_ft_of_street_line_intersection','value':True,
'statement':'The lot is assumed to lie within 100 feet of a street-line intersection.'} assert True
is False`. After the fix and the regeneration the within-100 line is the measured corner reach
(144.60 feet, more than 100 feet), basis approximate_tax_map, and the test passes.

## Every changed line of the regenerated files, with its reason

**Fixture `recorded_215_16_northern_journey.json`** (11 insertions, 21 deletions):
- `rule_versions`: dropped `r6b-rear-yard-corner-waiver` (within_100 now False → waiver not
  applicable) and `r6b-dwelling-units` (special density now the in-one stand-in → rule not
  applicable). These rules are only LISTED because of the old typed-in values; dropping them changes
  no shown number (the rear yard and the unit limit were and stay withheld).
- scope `overlay_present`: statement reworded ("in city data" → "in the city's records"); value/basis
  unchanged (recorded C2-2, city_records).
- scope `special_district_present`: basis assumed → city_records; statement "No special purpose
  district is assumed to apply; this run does not read the special-district layer." →
  "The city's records list no special purpose district for this lot." (removes the false claim that
  the run does not read a layer it reads).
- scope `special_density_area`: value false → true (the in-one stand-in); statement rewritten to say
  it is not known and the unit limit that depends on it is withheld.
- scope `within_100_ft_of_street_line_intersection`: value true → false; basis assumed →
  approximate_tax_map; statement rewritten to the measured corner reach (144.60 feet, more than 100).
- scope `street_line_intersection_angle_degrees`: value 90.0 → 89.7 (measured); basis assumed →
  approximate_tax_map; statement rewritten to the measured angle.

No shown value (floor area, the six heights, all conditional) and no withheld result changed.

**DXF snapshot** (5 changed scope-line rows) and **site-plan SVG snapshot** (20 lines = the five
rewritten scope statements wrapped across SVG text lines): the SAME five scope statements as the
fixture, rendered by the repository's own `render_results_dxf` / `render_site_plan` (regenerated with
`UPDATE_DXF_SNAPSHOTS=1` / `UPDATE_DRAWING_SNAPSHOTS=1`). The massing drawing stays absent (no
`.massing.svg` for this lot). No OTHER fixture or saved drawing changed.

## Every text the transform writes for the five scope lines (guard: `test_s137_scope_texts...`)

- overlay recorded present: "A commercial overlay (C2-2) is recorded for this lot in the city's records."
- overlay recorded absent: "The city's records list no commercial overlay for this lot."
- overlay not known: "Whether a commercial overlay applies to this lot is not known; every result that depends on it is withheld."
- special district recorded present: "A special purpose district is recorded for this lot in the city's records."
- special district recorded absent: "The city's records list no special purpose district for this lot."
- special district not known: "Whether a special purpose district applies to this lot is not known; a special purpose district is taken for the calculation, so every result that depends on it is withheld."
- within-100 measured within: "Measured from the tax-map outline, the lot's farthest point is {reach} from the corner where its two street lines meet, within 100 feet of it."
- within-100 measured beyond: "Measured from the tax-map outline, the lot's farthest point is {reach} from the corner where its two street lines meet, more than 100 feet from it."
- within-100 not applicable: "This lot is not a corner lot, so whether it lies within 100 feet of a street-line corner does not apply."
- within-100 not known: "Whether the lot lies within 100 feet of the corner where two street lines meet is not known; it is taken as not within 100 feet for the calculation, so the rear yard that depends on it is withheld."
- angle measured: "Measured from the tax-map outline, the lot's two street lines meet at about {angle}."
- angle not applicable: "This lot is not a corner lot, so the angle at which two street lines meet does not apply."
- angle not known: "The angle at which the lot's two street lines meet is not known; the rear yard that depends on it is withheld."
- density user's statement: "The lot is taken to be outside a special density area because that was stated for this run; it is a statement, not a recorded fact."
- density not known: "Whether the lot is in a special density area is not known; it is taken to be in one for the calculation, so the legal dwelling-unit limit that depends on it is withheld."

Each is plain and true: no gap/reading number, no task id, no "module"/"reference case"/"stand-in",
never "professional review", no machine code (snake_case). No scope line says the program does not
read something it reads; none contradicts a reason elsewhere in the document.

## Tests on optional values (no truthiness test on a value that may be unknown)

- `engine_conditions.within_100_and_angle`: `reach_ft is not None and angle_deg is not None` (an
  explicit None test, never a truthiness test — reach 0.0 would be a real measurement) and
  `is_corner is False` / `is_corner is None` (explicit identity, three states).
- `result_way_engine_bridge`: `reach.corner.reach.value if reach is not None else None` (explicit
  None), `_is_corner` on `LotType | None`, `_density_statement` on the explicit `DensityKnowledge`.
- `three_way_document._rewrite_scope_lines`: `condition_sources.get(key) is None` skip; `isinstance`
  guards on scope/assumptions/row; no truthiness on a value.

## Mutation proofs (step 8; run OUTSIDE the repository, all CAUGHT)

Copy of `engine_conditions.py` in the scratchpad, one flip each, the committed pinning assertion
re-run — a mutation is CAUGHT when the assertion raises. All nine CAUGHT:
`standin_special_district`, `standin_density`, `standin_overlay`, `standin_within_100`,
`standin_angle_limit`, `branch_within_100_inclusive`, `branch_overlay_present`,
`branch_special_district_present`, `branch_density_user_statement`.

## Questions of law / register

- A `not known` scope line carries the stand-in as its `value` and basis `assumed`, because the
  schema's `scope_assumption.basis` has no "not known" member and `value` cannot be null, and the
  schema is read-only here. The STATEMENT says it is not known. This is a reading for the reviewers;
  the contract question is held by backlog row DB-196 (NOT resolved here). Flagged, not decided.
- The benchmark rear yard is withheld on the recorded overlay (the decision step blocks on the
  overlay reading owed before the reach), not on the reach — unchanged from the last piece; DB-198
  (the rear-yard reason) stays owed. Not decided here.
- Review register `r6b-rear-yard-corner-waiver`: left UNCHANGED. Step 7 is conditional ("only if it
  describes how the waiver's two inputs are obtained"). The current entry does NOT describe how
  within_100 / the angle are obtained (it lists them as given rule inputs), and the rule file and
  the rule's evaluation are byte-identical, so the register entry stays valid. No human verdict was
  entered. (Check f not run: the register did not change.)

## What is NOT shown / activated

No route, no mount, no switch. `app/api/**`, `app/main.py`, `app/config.py`, `render.yaml`, `tools/`,
CI and dependency files untouched. No result appears on a screen from this piece: the website source
is unchanged and the new entry is called by no route. The engine files, the decision modules (except
the adapter `result_way_engine_bridge.py`), `engine_disclosures.py`, `evaluator_inputs.py`, every
schema and every rule file are byte-identical to the claim head (`git diff --name-only` vs the base
lists only the 10 files above).

## Correction (orchestrator, O36) — second commit on top of 11e738250

The orchestrator corrected reading O36: a scope line of a condition that is NOT KNOWN (or not
applicable) must SHOW the words, not the stand-in value the engine received. My first commit put the
stand-in into the scope row's `value` (as O36 then said), so the regenerated drawings printed
"Special density area **Yes** ...". A reader must not see a substitute (`Yes`) for something not
known.

- Change: in `three_way_document._rewrite_scope_lines`, a not-known line now sets `value` to the
  string `"Not known"` and `unit` to `null`; a not-applicable line sets `value` to `"Not applicable"`
  and `unit` to `null`. The `basis` stays `assumed`; the statement is unchanged. Recorded / measured
  / the user's-statement lines keep the real value and unit. **The value handed to the ENGINE does
  not change** (`engine_conditions` is untouched) - only what the emitted document shows.
- `unit`: the schema's `scope_assumption.unit` is `non_empty_string | null`, so I set it `null` for
  a words value (the stand-in - e.g. the angle's `136` with unit `degrees` - does not reach the
  document; without this the angle line would read "Not known degrees").
- Readers of `scope.assumptions`, READ ONLY, confirmed to handle a string value + null unit: the
  kit (`app/drawings/kit/scope.py` `_value_parts`) prints an unmapped string verbatim and omits a
  null unit (DXF via `results_dxf_notes.py`, SVG via `adapter.py`); `apps/web .../three-answers.ts`
  `scopeAssumptionValueText` returns the string unchanged (no unit); `ScopeSummary.tsx` shows
  `valueText`; `CalculationEvidence.tsx` / `ReportView.tsx` delegate to it; `tests/drawings/kit/
  test_scope.py` only closed-checks `housing_program`/`site_measurement_rank` values and an unknown
  KEY. None would fail or print wrong. I did not edit any of them. No STOP.
- The regenerated **density line now prints, exactly** (DXF, and the same words on the site-plan
  drawing): `Special density area Not known assumed Whether the lot is in a special density area is
  not known; it is taken to be in one for the calculation, so the legal dwelling-unit limit that
  depends on it is withheld.`
- The two **not-applicable** lines (an interior lot; not in the committed benchmark fixture, which
  is a corner lot) now read: value `Not applicable`, unit null, statements "This lot is not a corner
  lot, so whether it lies within 100 feet of a street-line corner does not apply." and "This lot is
  not a corner lot, so the angle at which two street lines meet does not apply." (previously they
  carried the made-up value `false` / `136 degrees`).
- Regenerated files, changed lines: the fixture's `special_density_area` row `value` `true` ->
  `"Not known"` (the only not-known condition on the benchmark; within-100 and the angle stay the
  measured `false` / `89.7`); the DXF prints `Not known` in place of `Yes`; the site-plan SVG prints
  `Not known` in place of `Yes`. No other line changed from the first commit.
- New test: `test_s137_not_known_lines_show_words_never_a_boolean_or_number` (plus value assertions
  in the benchmark, no-geometry, interior and special-district-not-read tests) FAILS if a not-known
  line's value is a boolean or a number. MUTATION PROOF (outside the repo,
  `scratchpad/mutation_not_known_value.py`): emptying the transform's words map makes the line show
  the stand-in `True` again - CAUGHT (the committed `value == "Not known"` assertion fails).

## Checks (direct exit codes) — first commit

| Check | Command | Result | Exit |
|---|---|---|---|
| a | `ruff check .` (services/api) | All checks passed | 0 |
| b | `pytest tests/scenario/three_answers` | 349 passed, 2 skipped (base 324+2) | 0 |
| c | `pytest tests/journey tests/contracts tests/spatial/test_lot_reach.py` | 573 passed (journey+contracts 559 at base, unchanged; + lot_reach) | 0 |
| d | `pytest tests/cad tests/drawings` | 1359 passed, 6 skipped (= base) | 0 |
| e | `tools/modularity_check.py --check` | exit 0 (no warning on the new/changed files) | 0 |
| e | `.github/scripts/validate_contracts.py` | Checked 23 schema file(s); 0 failure(s) | 0 |
| f | register render `--check` | NOT RUN (the register did not change) | n/a |
| g | `npm ci` (apps/web) | added 314 packages | 0 |
| g | `npm run lint` | 0 errors (2 pre-existing warnings, untouched files) | 0 |
| g | `npm run typecheck` | tsc --noEmit clean | 0 |
| g | `npm run test` | 2429 passed (= base; no web test changed) | 0 |
| g | `npm run build` | build succeeded | 0 |
| h | red proof (pre-fix) | FAILED (contradiction captured, above) | 1 |
| h | red proof (post-fix) + M5-T137 tests | 26 passed | 0 |
| h | mutation proofs (scratchpad) | 9/9 CAUGHT | 0 |
| i | `git diff --name-only <base>` | only the 10 allowed paths | — |

Exit codes were read from `$?` directly for ruff/the glob validator, and from `${PIPESTATUS[0]}`
(the test/npm command's own exit, before any display pipe) for the suites. The full api suite and the
browser tests (`test:e2e`) were NOT run (the orchestrator runs them at the final candidate).

## Checks (direct exit codes) — second commit (the O36 correction)

| Check | Result | Exit |
|---|---|---|
| a `ruff check .` (services/api) | All checks passed | 0 |
| b `pytest tests/scenario/three_answers` | 350 passed, 2 skipped (one new test) | 0 |
| c `pytest tests/journey tests/contracts tests/spatial/test_lot_reach.py` | 573 passed | 0 |
| d `pytest tests/cad tests/drawings` | 1359 passed, 6 skipped | 0 |
| e `tools/modularity_check.py --check` | exit 0 | 0 |
| e `.github/scripts/validate_contracts.py` | 23 schemas, 0 failures | 0 |
| g `npm run typecheck` | tsc --noEmit clean | 0 |
| g `npm run test` | 2429 passed (no web test changed) | 0 |
| g `npm run build` | build succeeded | 0 |
| mutation (scratchpad) | not-known-shows-words CAUGHT | 0 |

Exit codes read from `$?` for ruff/the validator and `${PIPESTATUS[0]}` / a `>log; echo $?` capture
for the suites. The full api suite and the browser tests were not run (the orchestrator runs them).

## Requested status

awaiting_gate. No blocker. Both commits are in the worktree; the orchestrator records the ledger.
