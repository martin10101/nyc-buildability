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
  present and non-empty and that every entry it carries states a way.

## Properties (a)–(h) and the test that proves each
- (a) every valid doc stays valid, every invalid stays invalid →
  `test_every_valid_results_fixture_still_validates`, `test_every_invalid_results_fixture_still_rejected`.
- (b) new fields optional; any binds 1.3.0 →
  `test_value_states_under_a_lower_version_is_rejected`, `test_not_available_resolution_fields_bind_1_3_0`.
- (c) in 1.3.0 the way-layer is mandatory on every available answer (present, non-empty) and every
  entry it carries states a way → `test_value_state_that_states_no_way_is_rejected`,
  `test_available_answer_without_a_way_layer_is_rejected_at_1_3_0`. PARTIAL: the schema does NOT
  refuse a shown value in `values[]` with no way entry (settled by silence) — JSON Schema 2020-12
  cannot quantify it; pinned as a known limit (`test_KNOWN_LIMIT_a_shown_value_with_no_way_entry_is_not_refused_by_the_schema`,
  xfail strict) and owed to the engine validator (DB-171).
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
paths diff empty; g new field names unused outside the bundled copy.

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
- Disclosure: the schema's `value_states` description also carries the same optimistic phrasing
  ("a single key maps to exactly ONE way, so the same key is never both shown and withheld"). Per
  the round-2 constraint (change only the test and the report; schema/copy/types byte-identical) I
  left it unchanged; it overstates the guarantee the same way and is covered by DB-171.
