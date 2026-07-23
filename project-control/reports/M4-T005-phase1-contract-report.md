# M4-T005 Phase 1 (contract layer) — producer report

Task: create the versioned `rule_evaluation @ 1.0.0` JSON-Schema contract for the
rules-evaluator output, wire it through typegen + runtime-bundle + validation
tooling (all three CI drift checks green), and add canonical fixtures +
contract tests. No API endpoint, no frontend (later phases). Producer evidence
only — not a self-acceptance.

Worktree: `.claude/worktrees/agent-a1a84d39a56c9c2ae` (branch
`worktree-agent-a1a84d39a56c9c2ae`), at HEAD `9e8c22ca`. Python 3.11.9 local;
no npm used (thin-client policy).

## Files created / modified (all within allowed scope)

Created:
- `packages/contracts/schemas/v1/rule_evaluation.schema.json` — the new canonical contract (draft 2020-12).
- `packages/contracts/generated/rule_evaluation.ts` — generated TS types (stdlib generator).
- `packages/contracts/fixtures/valid/rule_evaluation/` — 4 valid fixtures (supported draft, unsupported→not_applicable, professional-review fail-safe, split-lot spatial uncertainty).
- `packages/contracts/fixtures/invalid/rule_evaluation/` — 3 invalid fixtures (forbidden `verified`, missing required field, embedded full profile).
- `packages/contracts/scripts/tests/test_generate_rule_evaluation_ts.py` — typegen determinism + property_profile-unchanged drift test.
- `services/api/app/_contract_schemas/v1/rule_evaluation.schema.json` — byte-identical runtime bundle copy.
- `services/api/tests/contracts/__init__.py`, `services/api/tests/contracts/test_rule_evaluation_contract.py` — contract-layer acceptance pack (28 tests).

Modified (allowed):
- `packages/contracts/scripts/generate_ts_types.py` — added a SECOND, independent generation target for `rule_evaluation.ts` (new constants, `RULE_EVAL_NAMED_DEFS`, `load_rule_eval_schemas` / `generate_rule_evaluation` / `check_rule_evaluation` / `write_rule_evaluation`, and `main()` wiring). `type_expr`/`object_expr`/`emit_named_defs` gained an optional `named_defs` param (defaults to `NAMED_DEFS`) plus a pure-combiner (`anyOf`→union / `allOf`→intersection) branch that only fires for nodes with no `type`/`properties`/`$ref`/`enum` — property_profile has none such, so its output is unaffected.

Working-tree note (NOT a content change):
- `packages/contracts/generated/property_profile.ts` shows ` M` in `git status`
  but `git diff HEAD` is EMPTY and the worktree blob sha equals the HEAD blob
  (`3cffb8f0…`). The write-mode generator re-touches the file; with
  `core.autocrlf=true` the pre-existing working copy was CRLF (sha `5f3645…`)
  while the committed blob is LF (`3cffb8…`). My run rewrote it as LF, which
  MATCHES the committed blob exactly — so property_profile.ts is byte-identical
  to what is committed (AS-2), and a subsequent `git add`/commit stages no
  change for it.

Forbidden paths — confirmed untouched (`git diff HEAD` empty for each):
`property_profile.schema.json`, `coverage_status/common/source_fact*.schema.json`,
`generated/property_profile.ts` (content), `services/api/scripts/sync_contract_schemas.py`,
`.github/scripts/validate_contracts.py`, `services/api/app/rules/integration.py`,
`apps/web/src/lib/contract.ts`.

## Design of the input-identity block (no profile embed)

The contract document is the serialization the Phase-2 endpoint will emit; it is
the evaluator's `PropertyRuleEvaluation.export()` (as_dict) shape with the flat
`bbl` + `input_provenance` REGROUPED into a single `evaluated_input` identity
object plus two genuinely new identity fields, and a top-level `contract_version`.
`evaluated_input` (additionalProperties:false, all required) =
`{ bbl, profile_contract_version, input_fingerprint, input_provenance }`:

- `bbl` — `anyOf[$ref common.bbl, null]` (the evaluated property; null when the profile had no identity.bbl).
- `profile_contract_version` — `$ref common.non_empty_string` (e.g. `"1.4.0"`). Deliberately an OPEN string, NOT a closed enum, so it is not coupled to property_profile.schema.json's own evolving published-version list (that closed enum stays the single authority there).
- `input_fingerprint` — `$ref common.digest_sha256` (`sha256:<64hex>`). A deterministic fingerprint of the canonical evaluator inputs, so a consumer can confirm a result came from a specific input snapshot WITHOUT storing the profile. The field + hex-digest shape are defined now; the exact canonicalization/computation is Phase 2. (Fixture values are real sha256 digests over a small canonical identity blob, clearly documented as illustrative.)
- `input_provenance` — `{ zoning_district: string[], lot_area_sq_ft: string[] }`, each a list of provenance_ref ids that resolve into the evaluated profile's `provenance` array — the SAME provenance-ref-by-string pattern property_profile already uses (a `source_fact` record per id).

No full property profile is ever embedded. `additionalProperties:false` at the
document root actively rejects an embedded `property_profile`/`identity`/… key
(exercised by the `embedded_property_profile.json` invalid fixture). A later
aggregate-analysis contract can embed or reference this self-contained,
`$id`-versioned document without breaking it.

## Canonical coverage vocabulary — referenced, never redefined, never `verified`

`$defs/coverage_status_draft = allOf[ {$ref coverage_status.schema.json},
{enum: 5 values without "verified"} ]`. This keeps coverage_status.schema.json
the single source of the vocabulary while NARROWING it to exclude `verified`
(a draft-rule result may never be Verified before published-rule + G6). `not`
is not in validate_contracts.py's keyword allowlist, so the subset is expressed
as an allOf of the canonical `$ref` plus a subset `enum`, not a competing
6-value redefinition. Every coverage_status site (top-level, `family_coverage`,
each `evaluation_trace`) `$ref`s `#/$defs/coverage_status_draft`. Shared shapes
(`data_completeness`, `bbl`, `non_empty_string`, `digest_sha256`) are `$ref`'d
from the canonical files. The `evaluation_trace` `$def` mirrors the authoritative
rule-engine-internal `services/api/app/rules/schemas/v1/evaluation_trace.schema.json`
export shape (citations-with-provenance, computation steps, outputs,
determination, uncertainty), with coverage narrowed to the never-Verified set.

Fixtures are grounded in REAL evaluator output: I ran `app.rules.integration.
evaluate_property(...).export()` on four minimal profiles (confident R5;
confident R7→not_applicable; no spatial→fail-safe PRR; split-lot→PRR) and
transformed each into the contract document. No legal FAR numbers were
fabricated — values are the R5 draft rule's own computed/needs_review output
(coverage tops out at `conditional`, never `verified`).

## The three drift checks (exact commands + output)

1) `python packages/contracts/scripts/generate_ts_types.py --check`
```
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
OK: generated rule_evaluation TypeScript types are up to date.
exit=0
```

2) `python services/api/scripts/sync_contract_schemas.py --check`
```
OK: runtime-bundled contract schemas are byte-identical to the canonical source.
exit=0
```

3) `python .github/scripts/validate_contracts.py`
```
OK   packages\contracts\schemas\v1\rule_evaluation.schema.json (Rule Evaluation Result)
OK   ...\valid\rule_evaluation\professional_review_fail_safe.json (valid fixture passes rule_evaluation)
OK   ...\valid\rule_evaluation\split_lot_spatial_uncertainty.json (valid fixture passes rule_evaluation)
OK   ...\valid\rule_evaluation\supported_family_draft.json (valid fixture passes rule_evaluation)
OK   ...\valid\rule_evaluation\unsupported_not_applicable.json (valid fixture passes rule_evaluation)
OK   ...\invalid\rule_evaluation\coverage_status_verified.json (invalid fixture correctly rejected: $.coverage_status: value 'verified' is not one of the allowed enum values [...])
OK   ...\invalid\rule_evaluation\embedded_property_profile.json (invalid fixture correctly rejected: $: additional properties not allowed: ['property_profile'])
OK   ...\invalid\rule_evaluation\missing_coverage_status.json (invalid fixture correctly rejected: $: missing required property 'coverage_status')
Checked 7 schema file(s); 0 failure(s).
exit=0
```
`validate_contracts.py` AUTO-DISCOVERS schemas (`SCHEMA_ROOT.rglob`) and fixtures
(fixture dir name → `schemas/v1/<stem>.schema.json`), so NO edit to it was
needed — the new schema + fixtures were picked up automatically and the
stdlib mini-validator and the jsonschema engine agreed (no disagreement, exit 0).

## Test suites (exact commands + output)

- `python -m pytest packages/contracts/scripts/tests -q` → `19 passed` (14 pre-existing typegen tests still green — the property_profile drift-test monkeypatch scenarios pass — plus 5 new rule_evaluation typegen tests).
- `python -m pytest services/api/tests/contracts -q` → `28 passed` (valid fixtures validate; invalid fixtures rejected for their stated defect; schema `$ref`s canonical coverage_status and excludes `verified`; input-by-reference / no-embed; runtime bundle byte-identity; property_profile still 1.4.0 and its fixtures still validate).
- `python -m pytest services/api/tests/rules -q` → `152 passed` (rules-engine regression — the new schema/bundle changed nothing there).

## Acceptance scenarios

- AS-1 PASS — the schema validates realistic exported `evaluate_property` payloads (4 valid fixtures derived from real evaluator output); coverage/provenance resolve via `$ref`; no canonical enum redefined; `rule_evaluation.ts` byte-identical under `--check`; the runtime bundle copy is byte-identical (guarded by the contract test, see blocker below).
- AS-2 PASS — `property_profile.schema.json` + `generated/property_profile.ts` byte-identical to HEAD (`git diff HEAD` empty; blob sha `3cffb8f0…` matches); the closed enum stays `1.4.0`; all existing property_profile fixtures still validate; `validate_contracts` passes.

## Blocker / decision for the orchestrator (runtime-bundle drift guard)

`services/api/scripts/sync_contract_schemas.py` guards the runtime bundle via a
HARDCODED `SCHEMA_FILES` tuple of exactly the four profile schemas, and that
file is a FORBIDDEN edit target for this task. Wiring `rule_evaluation.schema.json`
into that script's guarded set would require editing it. Per the task
instruction I did NOT edit it and instead:

1. Produced the runtime bundle copy `services/api/app/_contract_schemas/v1/rule_evaluation.schema.json` byte-for-byte from the canonical source (same sha256 `b5dc55f7…`); `sync_contract_schemas.py --check` still passes (it simply does not inspect the new file).
2. Added a CI-enforced byte-identity guard for it in the contract test suite (`test_runtime_bundle_copy_is_byte_identical_to_canonical`), so drift IS caught in CI even though the standalone sync script does not cover it.

Decision needed: fold `rule_evaluation.schema.json` into
`sync_contract_schemas.py`'s `SCHEMA_FILES` (a one-line addition) via a
follow-up task scoped to `services/api/scripts/` — recommended to do when Phase 2
builds the runtime loader that actually reads this bundle. Until then the
byte-identity is guarded by the contract test above. Nothing loads
`rule_evaluation` at runtime in Phase 1, so there is no current runtime gap.

## Assumptions / limitations

- The contract document = the evaluator `export()` fields with identity regrouped into `evaluated_input` + a new `contract_version` and `input_fingerprint`. Phase 2 owns the serializer (as_dict→contract mapping) and the deterministic fingerprint canonicalization; this phase defines the shapes only.
- `_expected_failure` is an OPTIONAL documented fixture-annotation property so invalid fixtures fail ONLY for their stated defect under `additionalProperties:false`; the evaluator never emits it and valid fixtures omit it.
- Typegen renders open objects / `type:["object","null"] determination` / `crosscheck` as `unknown` (consistent with the existing repo precedent that the generator does not emit conditional/open-object types; runtime validation is the guard).

Requested status: awaiting_gate (with the runtime-bundle drift-guard decision above flagged for the orchestrator).
