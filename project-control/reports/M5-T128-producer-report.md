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
`value_states` or any non-null answer-level `resolved_by`/`gap_kind` MUST declare `1.3.0`. Forward
binding — a document that declares `1.3.0` MUST carry a non-empty `value_states` on every AVAILABLE
answer (a not-available answer owes none). The `scope` (1.1.0) and `notes` (1.2.0) version-binding
clauses were widened to admit `1.3.0` so a 1.3.0 document may still carry scope/notes (additive:
admits more, rejects nothing previously valid).

### What I rejected and why
- **`way` on each `answer_value` + a separate `withheld_values` array.** Cleanest for "no silence",
  but it cannot make S7's "one key both shown and withheld" rejectable: JSON Schema 2020-12 has no
  cross-container key-disjointness operator for dynamic keys. Rejected.
- **A single map that also carries the shown number.** Would duplicate the authoritative number in
  both `values[]` and the map — against the owner's one-number principle (work order §6/C-12).
  Rejected; the number stays only in `values[]`.
- **Chosen single-map (way only).** A JSON object keyed by value key → a key maps to exactly ONE
  way, so "both shown and withheld" is a single entry mixing two ways' fields, rejected by the
  closed `oneOf`/`additionalProperties`. All six required invalid cases become schema-rejectable.
  Residual (disclosed): the schema cannot force every `values[]` key to have a matching map entry;
  the forward binding guarantees the way-layer is present and non-empty and every entry it carries
  states a way, and the engine owes one entry per value key.

## Properties (a)–(h) and the test that proves each
- (a) every valid doc stays valid, every invalid stays invalid →
  `test_every_valid_results_fixture_still_validates`, `test_every_invalid_results_fixture_still_rejected`.
- (b) new fields optional; any binds 1.3.0 →
  `test_value_states_under_a_lower_version_is_rejected`, `test_not_available_resolution_fields_bind_1_3_0`.
- (c) in 1.3.0 every available answer states its way; none by silence →
  `test_value_state_that_states_no_way_is_rejected`, `test_available_answer_without_a_way_layer_is_rejected_at_1_3_0`.
- (d) shown value keeps its value object/number; conditional ≥1 condition; settled none →
  `test_conditional_value_names_its_assumptions`, `test_conditional_without_a_condition_is_rejected`,
  `test_conditional_with_an_empty_condition_list_is_rejected`, `test_settled_value_with_a_condition_is_rejected`.
- (e) withheld carries no number; beside shown values with key/label/reason/kind/resolve/law; never
  both → `test_withheld_value_sits_beside_shown_values`, `test_withheld_value_may_carry_its_law_section_or_omit_it`,
  `test_withheld_value_carrying_a_number_is_rejected`, `test_one_key_both_shown_and_withheld_is_rejected`.
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

## Generated types diff (packages/contracts/generated/results.ts)
Added: `ValueStates = null | { [key: string]: ValueState }`; `ValueState` (settled | conditional
with `ValueCondition[]` | withheld with label/reason/gap_kind/resolved_by/zr_sections?);
`ValueCondition`; `GapKind = "missing_information" | "work_owed"`; `AnswerNotAvailable` (NotAvailable
+ optional resolved_by/gap_kind). Changed: `Answer = AnswerAvailable | AnswerNotAvailable`;
`BuildingOptionAnswer = … | AnswerNotAvailable`; `AnswerAvailable`/`BuildingOptionAnswerAvailable`
gain `value_states?`; `Results.contract_version` adds `"1.3.0"`. **`AnswerValue` is UNCHANGED —
`value: number` stays a number**; no `way` marker was added to the shown value object.

## Checks (direct exit codes)
- a. `python -m ruff check .` (services/api) → exit 0 ("All checks passed!").
- b. `pytest -q -p no:cacheprovider tests/contracts` → exit 0 (474 passed, 1 warning).
- c. `pytest -q -p no:cacheprovider tests/scenario/three_answers tests/journey tests/cad tests/drawings`
  → exit 0 (1424 passed, 8 skipped).
- d. `sync_contract_schemas.py --check` → exit 0 (byte-identical); `generate_ts_types.py --check`
  → exit 0 (every generated .ts up to date, client block matches).
- e. `tools/modularity_check.py --check` → exit 0 (716 files, failures 0, 29 pre-existing warnings,
  none on changed files); `scripts/lanes/check_lane_paths.py --coverage` → exit 0 (9013 files,
  each owned by one lane); `pytest packages/contracts/scripts/tests` (the TS-generator harness) →
  exit 0 (74 passed). No separate fixture/schema validator exists beyond tests/contracts and the
  generator harness.
- f. `git diff --stat <base> -- packages/contracts/fixtures apps services/api/app/scenario
  services/api/app/cad services/api/app/drawings` → empty (exit 0).
- g. grep of `services/api/app` (.py, excluding `_contract_schemas`) and `apps/web/src` for every
  new field name → no matches; the names appear only in the bundled schema copy.

## Files changed (4, all allowed)
- packages/contracts/schemas/v1/results.schema.json
- services/api/app/_contract_schemas/v1/results.schema.json (script-synced)
- packages/contracts/generated/results.ts (script-generated)
- services/api/tests/contracts/test_results_three_ways_slot.py

## Stops / doubts
- No stop: strict additivity held throughout; no fixture added/changed/removed.
- One disclosed limitation (above): JSON Schema 2020-12 cannot quantify that every `values[]` key
  has a matching `value_states` entry — guaranteed at the engine. All six required invalid cases
  are schema-rejectable in the chosen shape.
