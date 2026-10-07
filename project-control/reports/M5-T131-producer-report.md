# M5-T131 producer report — the results validators refuse the 1.3.0 documents the schema cannot

Task: the two results validators refuse the contract-1.3.0 documents the JSON Schema cannot
refuse, from ONE shared rule; nothing emits 1.3.0. Producer: backend-engineer, isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a0c0845438acca5b3`.

Backlog row DB-171; directive D-090 R229 (unknown stays unknown) and R267 ("not checked" must not
become "confirmed").

## The shared rule (app/contracts/results_way_rules.py::results_way_violations)

A pure function, no I/O, no serializer import. For a document that declares contract version
`1.3.0`, in every AVAILABLE answer (floor_area_allowance, permitted_envelope, building_option):

1. every shown value (a key of the answer's `values[]`) has exactly one `value_states` entry and it
   is `settled` or `conditional` (`value_states` is a map, so a key has at most one entry; "exactly
   one" means the entry is present and its way is settled or conditional);
2. every `settled` / `conditional` entry belongs to a shown value;
3. a `withheld` entry belongs to no shown value (a withheld value carries no number and is absent
   from `values[]`).

Below contract 1.3.0 the function returns `[]` — the rule does nothing, so every 1.0.0 / 1.1.0 /
1.2.0 document (and every existing fixture) is unaffected. The function RETURNS the list of breaches;
each validator raises its OWN error type, so the two cannot drift and there is no copy of the rule.

## Each refused case with its message

Both validators raise with the prefix
`results document declares contract 1.3.0 but breaks the value-state way rule: <detail>`, joining all
breach details with `; `. `study_contracts.validate_results_document` raises `StudyContractError`
(`contract="results"`, `location="answers/<answer>/value_states/<key>"`);
`three_answers.contract.validate_results_document` raises `ResultsContractError` (same `location`).

- Shown value with no way entry (empty map is the extreme case) — detail:
  `answer 'floor_area_allowance': shown value 'max_residential_floor_area' has no way entry in
  value_states (every shown value must be settled or conditional, so none is settled by silence)`.
- A key both shown and withheld — detail:
  `answer 'floor_area_allowance': value 'max_residential_far' is shown in values[] but its way entry
  is 'withheld' (a shown value is settled or conditional; a withheld value carries no number and is
  not shown)`.
- A settled/conditional way entry for no shown value — detail:
  `answer 'floor_area_allowance': way entry 'phantom_key' is 'settled' but no shown value has that
  key (a settled or conditional entry must belong to a shown value)`.

## What the schema already refuses, and how S4 is tested (DB-171 F4)

An available answer whose every value is withheld would have an EMPTY `values[]` list. The SCHEMA
refuses that directly: `$defs/answer_available/values` and `$defs/building_option_answer_available/
values` both carry `minItems: 1`. So the "all-withheld available answer" case (S4) never reaches the
shared rule. `test_results_way_rules.py` tests this two ways:
`test_S4_all_withheld_available_answer_is_a_schema_breach_not_a_way_breach` asserts
`results_way_violations(doc) == []` (no breach from the rule), and
`test_S4_all_withheld_available_answer_is_refused_by_both` asserts BOTH validators raise (the schema's
`minItems: 1` refusal). The answer must instead be a whole-answer `not_available`.

## Callers of both validators (production)

- `study_contracts.validate_results_document`: `app/drawings/kit/adapter.py` (line 125),
  `app/contracts/compare_rows.py` (line 344); re-exported in `study_contracts.__all__`.
- `three_answers.contract.validate_results_document`: `app/scenario/three_answers/engine.py`
  (lines 233 and 291); re-exported via `app/scenario/three_answers/__init__.py`.

All callers consume pre-1.3.0 documents today (nothing emits 1.3.0), so the rule is a no-op for them.

## F5 and F6 (DB-171, carried from the M5-T128 review, unchanged by this task)

- F5 — the top-level `unit_estimate` has no way-layer (`value_states` attaches only to the three
  answers). The validators do nothing special with the unit estimate for 1.3.0; it keeps the shared
  available / not_available shape. A conditional or withheld legal unit limit (gap K11/K13) must be
  carried as a value INSIDE an answer, or the contract needs a later (schema) extension. That decision
  belongs to the piece that emits 1.3.0, not to this task.
- F6 — a reader rule, not a validator rule. A withheld value is absent from `values[]`, so a key that
  was always present can now be missing. A later reader (web, drawings, PDF, DXF) must read the way
  from `value_states[key]` and must NOT treat an absent value as zero. Forward guidance; nothing emits
  1.3.0 now.
- a key repeated in an answer's values list is refused neither by the schema nor by this rule
  (reviewer's note F1); owed to the piece that emits.

## The module does not reach the provenance serializer

`results_way_rules.py` imports only the standard library (`collections.abc`, `dataclasses`,
`typing`); it has no import or reference to any allowlist serializer symbol or `app.contracts.serializers`.
It is therefore a proven non-serializer submodule, so `results_way_rules` is added to the set in
`test_contract_serializers.py::test_study_contracts_is_the_proven_non_serializer_submodule` (the only
change to that file). The three serializer guard tests pass, and the two importer/reference guards
still resolve to exactly the profile write boundary (`services/api/app/profile/builder.py`).

## Round-2 change to the three tests (scope expanded by the orchestrator)

`services/api/tests/contracts/test_results_three_ways_slot.py` pinned the schema's limits with three
`xfail(strict=True)` tests that pass their document through the study validator. Adding the shared
rule to that validator (round 1) made them XPASS(strict) = fail, exactly as DB-171 and that file's
own comment foretold ("strict xfail fails when that lands … forcing whoever closes it to remove the
mark"). Round 2 turns them into refusal assertions — the `@pytest.mark.xfail` mark removed from each,
renamed, and the comments rewritten (the SCHEMA alone still accepts each document; the shared rule of
`app/contracts/results_way_rules.py` refuses it). Old name → new name:

- `test_KNOWN_LIMIT_a_shown_value_with_no_way_entry_is_not_refused_by_the_schema`
  → `test_a_shown_value_with_no_way_entry_is_refused_by_the_validator`
- `test_KNOWN_LIMIT_a_key_both_shown_and_withheld_is_not_refused_by_the_schema`
  → `test_a_key_both_shown_and_withheld_is_refused_by_the_validator`
- `test_KNOWN_LIMIT_an_empty_way_map_is_not_refused_by_the_schema`
  → `test_an_empty_way_map_on_an_available_answer_is_refused_by_the_validator`

The section comment above the three tests was rewritten accordingly, and the now-false clause in the
"Property e" section comment ("pinned as known limits in the xfail tests below") corrected. Nothing
else in that file was changed (`_base_1_3_0` and the other tests are byte-identical). A new test in
`test_results_way_rules.py`, `test_bare_schema_accepts_the_three_documents_the_rule_refuses`, pins that
the bare bundled schema (via `validate_study_contract_document("results", doc)`, which runs the schema
but NOT the way-rule) still ACCEPTS all three documents while `results_way_violations` reports a breach.

A round-2 grep for `KNOWN_LIMIT` / "known limit" across `services/api/tests`, `packages/contracts`,
`docs/DISCOVERY_BACKLOG.md` and `.github` found one surviving pointer: a NOTE inside
`test_one_entry_mixing_two_ways_is_rejected` that read "the schema does NOT refuse that (see the
KNOWN_LIMIT xfail tests below)". Its factual claim (the SCHEMA does not refuse that case) was true,
but the pointer was stale (those tests had been renamed and are no longer expected failures). Round 2
left it untouched because it is inside another test, outside this task's allowed edit of this file,
and reported it; round 3 reworded that one comment at the orchestrator's instruction to point to the
tests below as what they now are (the validator's shared rule refusing what the schema alone accepts),
keeping the schema claim. No `KNOWN_LIMIT` or expected-failure (`xfail`) marker now remains under
`services/api/tests`. DB-171 and the schema's own descriptions speak of the SCHEMA and remain true
(the orchestrator's to update DB-171).

## Checks (direct exit codes; venv python, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider, from services/api)

- a. `python -m ruff check .` → exit 0 ("All checks passed!").
- b. `python -m pytest -q -p no:cacheprovider tests/contracts -rx` → exit 0: 556 passed, 0 xfailed
  (previously 552 passed + 3 xfailed; the three former xfails now pass as refusal assertions, plus the
  new bare-schema test). No expected failure remains in the folder.
- c. `python -m pytest -q -p no:cacheprovider tests/scenario tests/journey tests/cad tests/drawings`
  → exit 0: 2415 passed, 8 skipped.
- d. `python .github/scripts/validate_contracts.py` → exit 0 (23 schemas, 0 failures);
  `python -m pytest -q -p no:cacheprovider .github/scripts/tests` → exit 0 (24 passed);
  `python3 tools/modularity_check.py --check` → exit 0 (722 files, 0 failures; results_way_rules.py
  not flagged).
- e. mutation proofs (in-place, reverted by re-edit): removing the shared-rule call from the study
  validator fails 5 study_contracts refusal tests (engine still passes); making the rule apply below
  1.3.0 — done by removing the version gate in the rule's source (`results_way_rules.py`), not by
  patching the two validators' call sites — fails 25 tests (valid fixtures + prior-version + pure
  below-1.3.0) run as `pytest tests/contracts/test_results_way_rules.py`. Both reverted; the new test
  file is 77 passed afterward.
- f. `git status --porcelain` empty after the round-2 commit; `git diff --stat <contract-head> HEAD --
  packages services/api/app/_contract_schemas` empty (no schema, generated-type or fixture change).

## Scope

Allowed paths only: `services/api/app/contracts/results_way_rules.py` (new),
`services/api/app/scenario/three_answers/contract.py`, `services/api/app/contracts/study_contracts.py`,
`services/api/tests/contracts/test_results_way_rules.py`,
`services/api/tests/contracts/test_contract_serializers.py` (one test function),
`services/api/tests/contracts/test_results_three_ways_slot.py` (the three tests, round 2), and this
report. The schema, its runtime copy, the generated types and every fixture are byte-unchanged.
Nothing emits contract 1.3.0 after this task.

round 3: one stale comment in test_one_entry_mixing_two_ways_is_rejected reworded at the orchestrator's instruction
