_Verbatim independent security-reviewer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G5 SECURITY & PRIVACY GATE REPORT — M5-T001 (scenario foundation)

**Reviewed SHA:** `e994147` (branch `task/M5-T001-scenario-foundation`, PR #86), base `main` @ `0a61b7d`
**Reviewer role:** Independent G5 (security & privacy), read-only
**Verdict:** **PASS**

## Scope & method
Read frozen source via `git show e994147:<path>`; ran the permitted test suite. Direct inline adversarial probes (`python -c`, heredoc) were blocked by the read-only guard, so hostile-input verification rests on reading the guards + the parametrized acceptance suite, which covers the same cases.

## Commands & outputs
- `git diff --name-only e994147 0a61b7d` → only `packages/contracts/**`, `services/api/**`, `project-control/**`. Filtering out those three prefixes returned **NO OTHER PATHS TOUCHED**. Canonical shared contracts (`common.schema.json`, `coverage_status.schema.json`, `property_profile.schema.json`, `rule_evaluation.schema.json`) and `sync_contract_schemas.py` are untouched.
- `diff <(git show e994147:packages/contracts/schemas/v1/scenario.schema.json) <(git show …:services/api/app/_contract_schemas/v1/scenario.schema.json)` → **IDENTICAL** (runtime bundle byte-identical to canonical; also enforced by `test_runtime_bundle_copy_is_byte_identical_to_canonical`).
- `python -m pytest tests/scenario -q` (from `services/api`) → **54 passed in 0.41s**.
- Canonical `coverage_status.schema.json` enum contains `verified`; scenario `coverage_status_draft` allOf subset enum excludes it → narrowing is meaningful and `verified` is structurally unrepresentable.
- Import audit of `services/api/app/scenario/*.py`: only `math`, `typing`, `json`, `functools.lru_cache`, `importlib.resources`, `enum`. No network / `os` / `subprocess` / `socket` / `eval` / `exec` / `open()` on user paths / `getenv` / `environ`. Codegen `generate_ts_types.py` has no dangerous sinks (build-time only, not runtime).

## Focus-area findings

**1. Draft-not-Verified integrity — PASS.** `verified` is structurally impossible, not conventional:
- Schema narrows `coverage_status` via `allOf` [canonical `$ref` + subset enum {conditional, professional_review_required, data_conflict, unsupported, not_applicable}] — `verified` excluded (`scenario.schema.json` `$defs/coverage_status_draft`).
- `ScenarioKind` enum (`models.py`) is only {preliminary, no_scenario, unsupported}; no up-label path. Preliminary caps `coverage_status="conditional"`.
- Builder hardcodes `needs_review=True` and the `NOT_VERIFIED_DISCLAIMER` constant on every outcome (`builder.py:316-318`).
- Belt-and-suspenders `assert_scenario_not_verified` recurses the whole document and rejects any `verified` under a `coverage_status` key anywhere (`contract.py`).
- Invalid fixture `coverage_status_verified.json` proves rejection (`test_invalid_verified_fixture_fails_on_coverage_enum`; `test_verified_is_not_an_allowed_coverage_status` also tampers a valid fixture → rejected). Exhaustive `test_as9` validates all 7 outcome kinds carry no `verified`.

**2. Fail-closed / no crash — PASS.** `_finite_float` rejects bool, non-numeric, NaN, ±inf, and huge-int→inf overflow; `_positive_finite_float` guards lot_area/cap (`builder.py:58-80`). Any malformed field → `no_scenario` + `professional_review_required`, no cap (precedence malformed > conflict > review > unsupported > preliminary). Wrong top-level types coerced via `_as_dict`. Empty/degenerate inputs fail closed (`test_as12_degenerate_empty_inputs`). Strict-JSON guard `json.dumps(document, allow_nan=False)` in `validate_scenario_document` rejects any residual NaN/Infinity. Integrity recompute is verification-only and fails closed on disagreement — neither the canonical value nor the recompute is surfaced (`test_as7`). Parametrized `test_as6` covers nan/inf/huge-int/wrong-type/negative/zero for both lot_area and cap. No unbounded loops: input traversal uses fixed `.get()` keys, not recursion over attacker depth.

**3. No injection / leak — PASS.** No dynamic execution or string interpolation into any dangerous sink. Provenance/citation strings (`snapshot_id`, `quote`, `zoning_district`, etc.) are copied verbatim as JSON data values, never into shell/SQL/HTML/format-code. f-strings in `reasons` interpolate only field-name lists and `fail_safe_reason` into human-readable JSON string fields. Error messages (`ScenarioContractError`) contain only a schema path + the jsonschema message — no secrets, filesystem paths, or tracebacks.

**4. Least privilege / read-only — PASS.** Inputs consumed read-only; `test_as12_builder_never_mutates_its_inputs` confirms no mutation (builder uses `.get()`, never assigns into inputs). `importlib.resources` reads only the fixed bundled schema names in `_REGISTRY_SCHEMA_FILES` (no path traversal, no user-controlled paths). No network, DB, env, or filesystem writes. No new external calls.

**5. No trust in browser-supplied data — PASS.** `evaluated_input` identifies inputs BY REFERENCE only (bbl + contract versions + fingerprint); root `additionalProperties:false`. Invalid fixture `embedded_property_profile.json` proves an embedded profile is rejected (`test_invalid_embedded_profile_fixture_fails_on_additional_property` asserts `property_profile` + `additional`). Engine operates on server-rebuilt canonical `property_profile`/`rule_evaluation` documents.

## Non-blocking observations (LOW, defense-in-depth for the future endpoint task)
- **L1 — `build_scenario` does not self-validate.** Strict-JSON / never-verified enforcement lives in `validate_scenario_document`, which the builder does not call before returning. A NaN buried in a verbatim-copied provenance sub-object (a field the builder does not numeric-guard) would only be caught at validation. Mitigated: inputs are canonical strict-JSON rule_evaluation documents and the documented contract requires callers to validate. Recommend the future endpoint always call `validate_scenario_document` before emit. Worst case today is a typed `ScenarioContractError`, never a wrong/Verified result.
- **L2 — recursion over verbatim-copied provenance.** `assert_scenario_not_verified` / `json.dumps` recurse over the assembled doc; the builder embeds attacker-adjacent nested sub-objects (`citation.provenance`, `rule_conflict.competing_rules`, `spatial_uncertainty.*`) by reference. Adversarial deep nesting there could raise `RecursionError` inside validation. Mitigated: inputs are upstream-schema-validated canonical rule_evaluation (bounded depth). Note for the endpoint boundary; not a defect in this slice.

Neither observation permits a Verified label or a silent wrong number; the worst outcome is a typed exception. Both are appropriate to address at the M5 endpoint task, not blocking for this service-layer draft engine.

**VERDICT: PASS** — no critical/high/medium security or privacy defects. Draft-not-Verified integrity is structurally guaranteed, hostile inputs fail closed to typed outcomes with no crash/leak, the engine is read-only with no network/fs/db/env reach, and canonical/forbidden contracts are untouched. Two LOW defense-in-depth notes are recorded for the future endpoint boundary.
