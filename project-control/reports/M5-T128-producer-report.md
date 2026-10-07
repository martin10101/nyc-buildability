# M5-T128 producer report — results contract 1.3.0 (settled / conditional / withheld)

Producer: backend-engineer. Strictly additive; nothing emits 1.3.0 yet. Base: contract head
`d952c612a4ff147146c05c66105a9e021928cc71`.

## The shape chosen

Version `1.3.0` is appended to the closed `contract_version` enum. Two optional, additive carriers:

1. `value_states` — an OPTIONAL object on each AVAILABLE answer (`answer_available` and
   `building_option_answer_available`), keyed by the answer value's key (same namespace as
   `answer_value.key`). Each entry is `value_state`, a closed `oneOf` of three ways discriminated
   by `way`:
   - `settled` → `{ "way": "settled" }` (no condition, no number — the number stays in `values[]`).
   - `conditional` → `{ "way": "conditional", "conditions": [ ≥1 × value_condition ] }`; each
     `value_condition` = `{ kind, assumption, settled_by }`, `kind` ∈
     `user_statement | contradicted_record | unchecked_condition`.
   - `withheld` → `{ "way": "withheld", label, reason, gap_kind, resolved_by, zr_sections? }`,
     carries NO number; `gap_kind` ∈ `missing_information | work_owed`; `zr_sections` optional.
2. `answer_not_available` — a NEW def = the shared `not_available` (status, reason, reason_kind)
   PLUS optional `resolved_by` and `gap_kind`. The `answer` and `building_option_answer` `oneOf`
   now use it instead of the shared `not_available`; everything else (remaining_floor_area,
   shortfall, geometry layers, add-on gains…) keeps the UNCHANGED shared `not_available`.

Required-when: both carriers are optional. Reverse binding — a document carrying any non-null
`value_states` (even an empty map) or any non-null answer-level `resolved_by`/`gap_kind` MUST declare
`1.3.0`. Forward binding — a document that declares `1.3.0` MUST carry a `value_states` map on every
AVAILABLE answer (a not-available answer owes none); the schema cannot require that map to be
non-empty (round 4 — see below). The `scope` (1.1.0) and `notes` (1.2.0) version-binding
clauses were widened to admit `1.3.0` so a 1.3.0 document may still carry scope/notes (additive:
admits more, rejects nothing previously valid).

### What I rejected and why
- **`way` on each `answer_value` + a separate `withheld_values` array.** Cleanest for "no silence",
  but it cannot make S7's "one key both shown and withheld" rejectable: JSON Schema 2020-12 has no
  cross-container key-disjointness operator for dynamic keys. Rejected.
- **A single map that also carries the shown number.** Would duplicate the authoritative number in
  both `values[]` and the map — against the owner's one-number principle (work order §6/C-12).
  Rejected; the number stays only in `values[]`.
- **Chosen single-map (way only).** A JSON object keyed by value key. The schema refuses ONE
  value_state entry that mixes the fields of two ways (e.g. a settled entry carrying a reason, a
  withheld entry carrying a number). It does NOT refuse a key shown in `values[]` and withheld in
  the map (reviewer C6, reproduced in round 2), and it does NOT refuse a shown value with no map
  entry — settled by silence (reviewer C7b, reproduced). Neither rule is expressible in JSON Schema
  2020-12 in this shape or any other. FIVE of the six listed invalid cases are schema-rejectable;
  "a key both shown and withheld" is NOT. The round-1 report was wrong to claim "a key maps to
  exactly ONE way, so the same key is never both shown and withheld" and "all six invalid cases
  become schema-rejectable": object-key uniqueness holds only WITHIN the map and says nothing about
  the separate `values[]` array. Both uncovered rules are owed to the validator of the engine that
  first emits 1.3.0 (backlog row DB-171); the forward binding only guarantees the way-layer is
  present and that every entry it carries states a way (round 4: it cannot require the map be
  non-empty either — subset keywords only).

## Properties (a)–(h) and the test that proves each
- (a) every valid doc stays valid, every invalid stays invalid →
  `test_every_valid_results_fixture_still_validates`, `test_every_invalid_results_fixture_still_rejected`.
- (b) new fields optional; any binds 1.3.0 →
  `test_value_states_under_a_lower_version_is_rejected`, `test_not_available_resolution_fields_bind_1_3_0`.
- (c) in 1.3.0 the way-layer is mandatory on every available answer (present) and every
  entry it carries states a way → `test_value_state_that_states_no_way_is_rejected`,
  `test_available_answer_without_a_way_layer_is_rejected_at_1_3_0`. PARTIAL (subset keywords only):
  the schema does NOT refuse a shown value in `values[]` with no way entry, nor an EMPTY `value_states`
  map (round 4 — same gap; an available answer always has a shown value) — both are settled by
  silence; pinned as known limits (`test_KNOWN_LIMIT_a_shown_value_with_no_way_entry_is_not_refused_by_the_schema`,
  `test_KNOWN_LIMIT_an_empty_way_map_is_not_refused_by_the_schema`, both xfail strict) and owed to
  the engine validator (DB-171). An ABSENT map on an available answer IS still refused (that test).
- (d) shown value keeps its value object/number; conditional ≥1 condition; settled none →
  `test_conditional_value_names_its_assumptions`, `test_conditional_without_a_condition_is_rejected`,
  `test_conditional_with_an_empty_condition_list_is_rejected`, `test_settled_value_with_a_condition_is_rejected`.
- (e) withheld carries no number; beside shown values with key/label/reason/kind/resolve/law →
  `test_withheld_value_sits_beside_shown_values`, `test_withheld_value_may_carry_its_law_section_or_omit_it`,
  `test_withheld_value_carrying_a_number_is_rejected`; one entry mixing two ways is refused →
  `test_one_entry_mixing_two_ways_is_rejected`. PARTIAL: "the same key never both shown and
  withheld" is NOT enforced — a key shown in `values[]` and withheld in the map validates; pinned
  as a known limit (`test_KNOWN_LIMIT_a_key_both_shown_and_withheld_is_not_refused_by_the_schema`,
  xfail strict) and owed to the engine validator (DB-171).
- (f) whole-answer not_available may say resolve/kind without changing required fields →
  `test_whole_answer_not_available_carries_resolution_fields_at_1_3_0`, `test_not_available_resolution_fields_bind_1_3_0`,
  `test_not_available_answer_still_requires_a_reason`.
- (g) remaining-floor-area unchanged (shared not_available) →
  `test_remaining_floor_area_not_available_gained_no_1_3_0_fields`.
- (h) shown value's number stays `number` in the generated types →
  `test_shown_value_number_stays_a_number_in_generated_types`, `test_runtime_copy_accepts_a_1_3_0_document`.

## Worked example — permitted_envelope (height shown, coverage withheld), 1.3.0
```
"permitted_envelope": {
  "status": "available",
  "values": [ { "key": "max_building_height", "value": 55, "unit": "feet", ... } ],
  "value_states": {
    "max_building_height": { "way": "conditional", "conditions": [
      { "kind": "unchecked_condition",
        "assumption": "If none of the unchecked conditions (waterfront, airport height, transit easement, near a district line) applies",
        "settled_by": "Capturing the governing law text and confirming each is absent" } ] },
    "min_base_height": { "way": "settled" },
    "max_lot_coverage": { "way": "withheld", "label": "Maximum lot coverage",
      "reason": "The lot reaches 103.93 ft from the 215 Place street line, beyond the 100 ft corner-coverage area; the ZR 12-10 corner definition is not captured.",
      "gap_kind": "missing_information",
      "resolved_by": "Capturing the ZR 12-10 corner definition and reading the outline.",
      "zr_sections": ["ZR 23-362"] }
  }
}
```
A height that is SHOWN keeps its number in `values[]` and a `settled`/`conditional` entry in
`value_states`; a coverage that is WITHHELD has no entry in `values[]` and only a `withheld`
entry (no number).

## What a later engine / screen must do
- Engine: when it emits `1.3.0`, write one `value_states` entry per value key of every available
  answer (settled/conditional for each shown `values[]` key; a withheld entry — no number — for
  each gap), and may add `resolved_by`/`gap_kind` to a withheld whole answer. Keep shown numbers in
  `values[]` only.
- Screen: read a value's way from `value_states[key]` (number from `values[]`); show conditional
  results apart, labelled with their condition; show a withheld value with its reason/resolve/kind;
  never render a number for a withheld value.
- F4 (reviewer note): an answer whose EVERY value is withheld cannot stay "available" — the
  available shape still requires `values` to hold at least one item. Such an answer is the
  whole-answer not-available case (answer_not_available, which may carry resolved_by/gap_kind), not
  an available answer with an all-withheld value_states map.
- F5 (reviewer note): the top-level `unit_estimate` (and the other top-level blocks) have no
  value_states; the three-ways layer lives only inside the three answers. A later engine that needs
  a unit estimate to read "not known" uses that block's own not_available shape, not value_states.
- F6 (reviewer note): a reader must never treat an absent value as zero. A withheld value carries no
  number at all (no `value` key); the screen shows "not known", never 0, and the engine emits no
  zero stand-in for a gap.

## Generated types diff (packages/contracts/generated/results.ts)
Added: `ValueStates = null | { [key: string]: ValueState }`; `ValueState` (settled | conditional
with `ValueCondition[]` | withheld with label/reason/gap_kind/resolved_by/zr_sections?);
`ValueCondition`; `GapKind = "missing_information" | "work_owed"`; `AnswerNotAvailable` (NotAvailable
+ optional resolved_by/gap_kind). Changed: `Answer = AnswerAvailable | AnswerNotAvailable`;
`BuildingOptionAnswer = … | AnswerNotAvailable`; `AnswerAvailable`/`BuildingOptionAnswerAvailable`
gain `value_states?`; `Results.contract_version` adds `"1.3.0"`. **`AnswerValue` is UNCHANGED —
`value: number` stays a number**; no `way` marker was added to the shown value object.

## Checks (direct exit codes)
Round 1 (schema + tests at 7abdba88): a ruff → 0; b `pytest tests/contracts` → 0 (474 passed);
c readers → 0 (1424 passed, 8 skipped); d sync/generate `--check` → 0 (byte-identical, all .ts in
step); e modularity → 0, lane-paths → 0 (9013 files), generator harness → 0 (74 passed); f forbidden
paths diff empty; g new field names unused outside the bundled copy. CORRECTION (round 4): round 1
also claimed "no separate schema validator exists beyond tests/contracts and the generator harness" —
WRONG. The repository also runs `.github/scripts/validate_contracts.py` (CI "contracts") and
`.github/scripts/tests` (CI "validation-suite"), a stricter keyword-subset validator that round 1
did not run and that later failed on `minProperties`/`propertyNames` — see the Round 4 section.

Round 2 (test + report only; schema/copy/types unchanged):
- a. `python -m ruff check .` (services/api) → exit 0 ("All checks passed!").
- b. `pytest -q -p no:cacheprovider tests/contracts/test_results_three_ways_slot.py -rx`
  → exit 0 (44 passed, 2 xfailed — the two DB-171 KNOWN_LIMIT tests, strict).
- c. `pytest -q -p no:cacheprovider tests/contracts` → exit 0 (474 passed, 2 xfailed, 1 warning).
- d. `git diff --stat 7abdba88 HEAD -- packages/contracts/schemas/v1/results.schema.json
  services/api/app/_contract_schemas/v1/results.schema.json packages/contracts/generated/results.ts`
  → empty (the schema, its runtime copy and the generated types are byte-identical to round 1).

## Files changed round 2 (2, all allowed)
- services/api/tests/contracts/test_results_three_ways_slot.py (rename + 2 strict-xfail KNOWN_LIMIT tests)
- project-control/reports/M5-T128-producer-report.md (F1 corrections, F4–F6 notes)

## Stops / doubts
- No stop: strict additivity held throughout; no fixture added/changed/removed; the schema, its copy
  and the generated types stay byte-identical to round 1.
- Correction (round 2, review F1): the round-1 report was WRONG to claim the chosen shape makes
  "a key both shown and withheld" schema-rejectable and "all six invalid cases" rejectable. The
  truth: FIVE of the six listed invalid cases are schema-rejectable; two rules — a key shown in
  `values[]` and withheld in the map, and a shown value with no way entry — are NOT expressible in
  JSON Schema 2020-12 and are owed to the validator of the engine that first emits 1.3.0 (DB-171).
  Reproduced both (reviewer C6 and C7b) in round 2; both are now pinned as strict-xfail tests.
- Disclosure (round 2, now resolved in round 3): the schema's `value_states` description carried the
  same optimistic phrasing ("a single key maps to exactly ONE way, so the same key is never both
  shown and withheld"); the round-2 constraint froze the schema, so it was left unchanged then.
  Round 3 corrects it (below): that false sentence and two other overstatements in the descriptions
  are gone; the schema now says what it enforces and what it cannot.

## Round 3 — the schema's descriptions say what it enforces and what it cannot
Description text only (no keyword, structure, enum or required-list change); the runtime copy was
re-synced and the types regenerated by their scripts. Three overstatements corrected:

1. `$defs/value_states`. OLD: "Because this is a JSON object keyed by value key, a single key maps
   to exactly ONE way, so the same key is never both shown and withheld in one answer." NEW: "One
   entry states exactly one way: an entry that mixes the fields of two ways matches no branch and is
   refused. This schema does NOT compare the keys of the 'values' list with the keys of this map, so
   it does not refuse (i) a shown value that has no entry here, nor (ii) a key that is shown in
   'values' and marked withheld here. Both are rules of the contract all the same: the emitter must
   give one entry for every shown value and must never mark a shown key withheld, and the validator
   of the engine that emits this version must refuse a document that breaks either." Also OLD "a
   withheld value has NO entry in 'values'" → NEW "a withheld value must have no entry in 'values'"
   (a rule, not a schema guarantee); and the closing OLD "...on every available answer (the forward
   version-binding allOf above) so none is settled by silence." → NEW ends "...on every available
   answer (the forward version-binding allOf above)." (the silence rule is stated once, as a duty).
2. Forward version-binding clause. OLD first sentence: "A document that declares 1.3.0 must state
   the way of every value of every AVAILABLE answer, so none is settled by silence: ...". NEW: "This
   clause enforces that a document declaring 1.3.0 carries a non-empty value_states map on every
   AVAILABLE answer (status 'available'), and - through value_state - that every entry present
   declares a way... This clause does NOT enforce that there is an entry for every value shown in an
   answer's 'values' array: JSON Schema 2020-12 cannot compare the keys of the two. Giving one entry
   for every shown value, so none is settled by silence, is the contract's rule all the same - the
   emitter's duty, refused by the validator of the engine that emits this version, not by this
   schema."
3. `properties/contract_version` (1.3.0 passage). OLD: "a document declaring 1.3.0 must state the
   way of every available answer (the forward-binding allOf below) so none is settled by silence".
   NEW: "a document declaring 1.3.0 carries a non-empty way-layer on every available answer (the
   forward-binding allOf below), each entry present stating one way; stating the way of every shown
   value, so none is settled by silence, is the emitter's rule, refused by the validator of the
   engine that emits this version, not by this schema".

Other overstatement found (review step 4): the `value_state` SETTLED and CONDITIONAL branch
descriptions said "The number ... are/stays in the answer's 'values' array" as if guaranteed. Both
now read "lives in the matching entry of the answer's 'values' array (the emitter's rule; this
schema does not cross-check the two)." No other schema-guarantee overstatement was found in the
descriptions added by this task (value_state top, the WITHHELD branch's "carries NO number", the
reverse-binding clause, `value_condition`, `gap_kind` and `answer_not_available` all state only what
closed branches / minItems / optional+binding keywords actually enforce). The pre-existing
scope (1.1.0) and notes (1.2.0) binding-clause descriptions were not authored by this task and only
had their version enums widened; their prose was left unchanged.

Per the instruction, no backlog row, task or reviewer is named inside the corrected sentences (they
say "the emitter" and "the validator of the engine that emits this version"); the version-provenance
citations already in the file ("contract 1.3.0, M5-T128, ...", matching 1.1.0/1.2.0) were left as-is.

### Round 3 proofs (description-only) and checks
- Proof 1 (schema): raw JSON differs vs b98c37f2 (False); after deleting every `description` key
  recursively from both, the two are EQUAL (True) → no keyword/structure/enum/required change.
- Proof 2 (runtime copy): same result — raw differs (False), equal after stripping descriptions (True).
- Proof 3 (generated types): `results.ts` is byte-identical old vs new (True) — the study-contract
  generator emits no per-field doc comments — and identical after removing comment lines (True).
- Checks (direct exit codes, round 3): `ruff check .` → 0; `pytest tests/contracts -rx` → 0 (474
  passed, 2 xfailed — the DB-171 KNOWN_LIMIT tests); `sync_contract_schemas.py --check` → 0;
  `generate_ts_types.py --check` → 0; `pytest packages/contracts/scripts/tests` → 0 (74 passed).
- Files changed round 3: packages/contracts/schemas/v1/results.schema.json;
  services/api/app/_contract_schemas/v1/results.schema.json; project-control/reports/M5-T128-producer-report.md.
  (packages/contracts/generated/results.ts unchanged — descriptions do not flow into it; the test
  file unchanged — no test pins a description.)

## Round 4 — value_states uses only keywords the repository's contract validator accepts
WHAT CI CAUGHT. After re-review the branch was pushed and two checks failed — CI job "contracts"
(`.github/scripts/validate_contracts.py`) and CI job "validation-suite" (`.github/scripts/tests`,
the test `test_full_validator_run_exits_zero`). Cause: that validator accepts only a fixed
`KNOWN_KEYWORDS` subset of JSON Schema and fails closed on anything else; `$defs/value_states` used
`minProperties` and `propertyNames`, both outside the subset. Reproduced before fixing: the validator
printed two FAIL lines for `#/$defs/value_states/anyOf/1` and exited 1; the validation-suite gave 1
failed, 23 passed.

WHY IT WAS MISSED. The round-1 report said "No separate fixture/schema validator exists beyond
tests/contracts and the generator harness" — that was WRONG. The repository has a second, stricter
contract validator under `.github/**` (the "contracts" and "validation-suite" CI jobs) that none of
the producer, reviewer or orchestrator ran. The validator is CI tooling and is forbidden to this
task; by the orchestrator's decision it is NOT changed — the schema is expressed with subset
keywords only.

NON-DESCRIPTION SCHEMA CHANGE (the whole of it): in `$defs/value_states`, the object branch lost two
lines — `"minProperties": 1,` and `"propertyNames": { "pattern": "^[a-z][a-z0-9_]*$" }`. The
remaining `"additionalProperties": { "$ref": "#/$defs/value_state" }` line changed only by dropping
its now-trailing comma (it is the last key). No keyword, enum, type or required list changed anywhere
else. Searched the whole schema for every out-of-subset keyword (`minProperties maxProperties
propertyNames patternProperties not if then else uniqueItems dependentRequired dependentSchemas
contains minContains maxContains prefixItems unevaluatedProperties/Items multipleOf $dynamic* $anchor
$vocabulary contentEncoding contentMediaType`): only `minProperties` and `propertyNames` were
present, both in value_states; none remain.

WHAT THE SCHEMA NO LONGER REFUSES, and how each is said and pinned:
1. An EMPTY `value_states` map on an available answer (no `minProperties`). Because an available
   answer always has at least one shown value, an empty map is the same gap as "a shown value with no
   way entry" — already owed to the engine validator (DB-171). Said in the `value_states`, forward-
   binding and `contract_version` descriptions; pinned by new strict-xfail
   `test_KNOWN_LIMIT_an_empty_way_map_is_not_refused_by_the_schema`.
2. The FORM of the map's keys (no `propertyNames`). The keys must equal the answer's value keys,
   whose form is checked on the value object (`answer_value.key`'s pattern). Said in the
   `value_states` description. Neither rule could be re-expressed with subset keywords without
   changing the shape, so no workaround was invented.

ABSENT MAP STILL REFUSED: yes — the forward-binding clause still lists `value_states` in `required`
for an available answer, so an absent map on an available 1.3.0 answer is still rejected
(`test_available_answer_without_a_way_layer_is_rejected_at_1_3_0`, a plain passing test).

GUARD ADDED: `test_repository_contract_validator_accepts_results_schema` loads
`.github/scripts/validate_contracts.py` by path and runs its `structural_check` over
`results.schema.json`, asserting no keyword error — so this failure class cannot return unseen from
the api suite. It is sound (the .github tests themselves import that module in-process; loading by
path does not run `main()`); it skips only if the repo tree is absent from the checkout.

"non-empty" wording corrected in the schema (forward-binding clause, `value_states`, the 1.3.0
passage of `contract_version`) and in this report (the shape summary, property (c)); the round-3
historical quotes above are left as the record of what round 3 said. The round-1 "no separate
validator" sentence is corrected here.

### Round 4 checks (direct exit codes)
- a. `python .github/scripts/validate_contracts.py` → exit 0 (last line "Checked 23 schema file(s);
  0 failure(s)."; `OK results.schema.json`); `pytest .github/scripts/tests` → exit 0 (24 passed,
  was 23 passed + 1 failed).
- b. `ruff check .` (services/api) → 0; `pytest tests/contracts -rx` → 0 (475 passed, 3 xfailed — the
  three DB-171 KNOWN_LIMIT tests); readers (`tests/scenario/three_answers tests/journey tests/cad
  tests/drawings`) → 0 (1424 passed, 8 skipped).
- c. `sync_contract_schemas.py --check` → 0; `generate_ts_types.py --check` → 0;
  `pytest packages/contracts/scripts/tests` → 0 (74 passed).
- d. the two fixture-verdict tests `test_every_valid_results_fixture_still_validates` and
  `test_every_invalid_results_fixture_still_rejected` both pass (inside the 475) — every valid
  results fixture still validates and every invalid one is still refused.
- e. `git diff --stat 906bd518 HEAD`: results.schema.json; its runtime copy; the test file; this
  report (generated results.ts does NOT move — `minProperties`/`propertyNames` never affected the
  emitted TS). Non-description schema lines changed: the two removals above only.
- Files changed round 4: packages/contracts/schemas/v1/results.schema.json;
  services/api/app/_contract_schemas/v1/results.schema.json;
  services/api/tests/contracts/test_results_three_ways_slot.py;
  project-control/reports/M5-T128-producer-report.md.
