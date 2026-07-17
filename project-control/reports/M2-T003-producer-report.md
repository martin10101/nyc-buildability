# M2-T003 Producer Report — Property API boundary + contract-version hardening

**Task ID:** M2-T003
**Producer:** backend-engineer
**Branch:** task/M2-T003-property-api-contract (worktree .claude/worktrees/M2-T003)
**Status requested:** `awaiting_gate` (all producer scenarios S1–S8, S10 pass locally; S9 is a data-contract-verifier diff)

## Summary

Implemented the backend/contracts half of the API boundary hardening against
the settled canonical contract 1.2.0: every 200 property-profile payload is now
validated against the selected canonical schema before send (an invalid 200 is
impossible); the builder's stale `1.0.0` declaration is resolved to the
canonical `1.2.0` with declared-vs-emitted consistency validation and full
1.0.0/1.1.0 backward compatibility; an unpublished contract version yields a
bounded typed error; the exact (HTTP status, state) pair matrix is codified and
test-enforced; a deterministic stdlib TypeScript type-generation pipeline plus
an additive CI drift check is added; and the HTTP-500 + state=no_match
client-regression fixture is recorded for M2-T002.

## Files changed (exact paths, all inside allowed scope)

Modified:
- `services/api/app/profile/builder.py` — `PROFILE_CONTRACT_VERSION` `1.0.0`→`1.2.0`; docstring updates. **Field MAPPING untouched** (S9): only the version-declaration constant and comments changed; no column mapping, bucketing, coverage, missing-input, conflict, digest, or status-dimension logic was altered.
- `services/api/app/api/v1/properties.py` — added `STATUS_STATE_MATRIX` (single source of truth), pre-send `validate_profile` call on the 200 path, two new typed responders (`_internal_contract_error_500`, `_unsupported_contract_version_500`), docstring + OpenAPI 500 doc updates.
- `services/api/tests/api/test_properties_v1.py` — updated the one M1-T005 assertion that expected `contract_version == "1.0.0"` to the resolved `1.2.0`.
- `services/api/tests/profile/test_data_semantics.py` — updated the M2-T004 S6 test (`test_s6_builder_...`) + its docstring to assert the resolved `1.2.0` declaration.
- `packages/contracts/README.md` — superseded the §167 deferral with the recorded contract_version DECISION (declaration=1.2.0, consistency rule, validation, bounded unsupported-version error, backward-compat, typegen, client-regression fixtures).
- `.github/workflows/ci.yml` — **ADDITIVE only**: new `contracts-typegen` job (byte-identical TS drift check + generator tests). No existing job was altered (diff is a pure insertion between `contracts` and `control-plane`).

Added:
- `services/api/app/profile/contract.py` — backend contract-metadata + validation module (single source of truth for the closed published enum read LIVE from the schema; `VERSION_INTRODUCED`; `select_schema_version`; `validate_profile`; `ContractValidationError`; `UnsupportedContractVersionError`).
- `services/api/tests/api/test_property_contract.py` — 29 tests covering S1, S2, S3, S6, S7, S8, and the S4 fixture check.
- `packages/contracts/scripts/generate_ts_types.py` — stdlib-only deterministic TS generator (`--check` drift mode + write mode).
- `packages/contracts/generated/property_profile.ts` — committed generated types (100% schema-key coverage).
- `packages/contracts/scripts/tests/test_generate_ts_types.py` — 6 typegen determinism + coverage tests.
- `packages/contracts/fixtures/client_regression/http500_state_no_match.json` — the S4 recorded client-regression fixture.

## Contracts / schema changed

**No JSON Schema shape changed.** `property_profile.schema.json` (1.2.0) is
settled and was NOT edited. The `contract_version` enum stays the closed
`["1.0.0","1.1.0","1.2.0"]`, read live by the backend. Only the builder's
DECLARED version and new backend validation/typegen were added.

## Acceptance scenarios created (S1–S10 mapping)

| Scenario | Where proven | Result |
| --- | --- | --- |
| S1 valid profile validates + declares 1.2.0 | `test_property_contract.py::test_s1_*` | PASS |
| S2 fault injection → typed 500, never invalid 200 | `test_property_contract.py::test_s2_*` (missing key, wrong type, dangling ref) | PASS |
| S3 pair-matrix enumeration; undocumented pair fails | `test_property_contract.py::test_s3_*` (7 parametrized paths + 3 500-state paths + matrix-completeness guard) | PASS |
| S4 500+no_match fixture recorded & replayable | `fixtures/client_regression/http500_state_no_match.json` + `test_s4_client_regression_fixture_*` | PASS (artifact; wired by M2-T002) |
| S5 typegen byte-identical + 100% key coverage | `scripts/tests/test_generate_ts_types.py` (6 tests) + CI `contracts-typegen` | PASS |
| S6 version consistency; no stale hard-coded version | `test_property_contract.py::test_s6_*` (schema/builder agree; declared<emitted rejected; source-grep guard) | PASS |
| S7 backward compat: valid 1.1.0 AND 1.0.0 still pass | `test_property_contract.py::test_s7_*` against committed full_example / full_example_v1_1 fixtures | PASS |
| S8 unsupported version → bounded typed error, never coerced | `test_property_contract.py::test_s8_*` (select, validate, route-level, non-coercion, malformed type) | PASS |
| S9 no field mapping/semantics changed | builder diff = version constant + comments only; for data-contract-verifier | (reviewer diff) |
| S10 full API pytest + web-e2e stay green | 207 API tests pass; web-e2e analysis below | PASS (API); web-e2e unaffected (analysis) |

## Commands run + results (expected vs actual)

All run in `.claude/worktrees/M2-T003` (Python 3.11.9 local; CI uses 3.12).

- `cd services/api && python -m pytest -q`
  - Baseline before changes: **178 passed**. After: **207 passed** (+29 new). Expected all pass → actual all pass.
- `python -m pytest packages/contracts/scripts/tests -q` → **6 passed** (typegen determinism + 100% coverage + --check).
- `python packages/contracts/scripts/generate_ts_types.py --check` → `OK: generated TypeScript types are up to date.` (byte-identical).
- `python .github/scripts/validate_contracts.py` → `Checked 6 schema file(s); 0 failure(s).` (unchanged; new client_regression dir correctly ignored).
- `python -m pytest .github/scripts/tests -q` → **24 passed** (historical `builder_output_m1_t005.json` 1.0.0 assertion preserved; NOT touched — forbidden path).
- `cd services/api && python -m ruff check .` → `All checks passed!`

Note on local vs CI: local Python is 3.11.9; the package `requires-python >=3.12`
but the code uses only 3.11-compatible constructs (`from datetime import UTC`),
so it imports and tests cleanly locally. The full suite also runs on CI's 3.12
(`api` job = ruff + pytest; new `contracts-typegen` job runs the generator
--check + tests).

## contract_version decision and where recorded

**Decision:** the builder declares the canonical **1.2.0** (it emits keys
through 1.2.0). Declared version and emitted key set ARE validated against each
other (declaring a version below the min-version of any emitted optional key is
rejected as `internal_contract_error`). The version validated against is
SELECTED from the payload's declared version against the closed enum, which is
read LIVE from the schema — no stale version is hard-coded in the backend. An
unpublished declared version is a bounded typed `unsupported_contract_version`
500. **Recorded in** `packages/contracts/README.md` under
"`contract_version` semantics — RESOLVED by M2-T003 (supersedes the deferral)",
replacing the §167 deferral text.

## How backward compatibility (1.0.0 / 1.1.0) is proven

- `test_s7_valid_1_0_0_instance_still_validates` — `full_example.json` (1.0.0, no additive keys) passes `validate_profile`.
- `test_s7_valid_1_1_0_instance_still_validates` — `full_example_v1_1.json` (1.1.0, `data_completeness` + `reproducibility`, no `status_dimensions`) passes `validate_profile`.
- `test_s7_a_declared_11_instance_may_carry_11_keys` — the declared-vs-emitted check allows a version to carry keys at OR below its own version.
- Rationale: every 1.1.0/1.2.0 key is OPTIONAL, so no 1.0.0/1.1.0 instance's required-key set or types changed. The consistency check only forbids declaring a version *below* a key it emits, never forbids a lower-version instance that omits later keys.

## Typegen tool/approach and the CI drift check

- **Tool:** `packages/contracts/scripts/generate_ts_types.py` — a stdlib-only Python generator. Chosen over a Node tool (json-schema-to-typescript, quicktype) to honor the thin-client low-storage policy: no `node_modules`, no browser/toolchain install, no network. It resolves cross-file `$ref`s into common/source_fact/coverage_status, honors enums/unions/nullable/required/additionalProperties, preserves schema key order (deterministic), and emits LF-only with a single trailing newline.
- **Output:** `packages/contracts/generated/property_profile.ts` (committed). Named aliases for reused `$defs` (Bbl, BoroughCode, CoverageStatus, SourceFact, FactValue, …) plus the `PropertyProfile` interface. The `contract_version` union is pinned to `"1.0.0" | "1.1.0" | "1.2.0"`.
- **CI drift check:** new additive job `contracts-typegen` runs `generate_ts_types.py --check` (fails byte-for-byte on divergence) and `pytest packages/contracts/scripts/tests` (determinism + 100%-key-coverage). Regenerate command for developers: `python packages/contracts/scripts/generate_ts_types.py`.

## Assumptions / defaults

1. **S4 fixture kind:** "HTTP 500 + state=no_match" is not producible by the real app (an upstream 5xx retries to `source_unavailable`/503; `no_match` only ever emits at 404). I therefore recorded it as a deliberately-labeled SYNTHETIC/adversarial API-response fixture (`_synthetic: true`, full `_provenance` note) in `packages/contracts/fixtures/client_regression/` — a client-defense regression input, not a claim the API emits this pair. M2-T002 wires it (apps/web is my forbidden path).
2. **`builder_output_m1_t005.json` left at 1.0.0:** it is a historical M1-T005 SCHEMA fixture (validated against the version-agnostic schema, not through the backend consistency check) and its 1.0.0 assertion lives in `.github/scripts/tests/` (a forbidden path). Leaving it untouched both respects scope and demonstrates that an optional-key-bearing 1.0.0 instance stays schema-valid. Live builder output now declares 1.2.0.
3. **Declared-vs-emitted signal:** top-level optional-key presence (`data_completeness`/`reproducibility`=1.1.0; `status_dimensions`=1.2.0) is the robust consistency signal; per-fact `coverage_status` and the zoning provenance maps (also 1.1.0) live inside required containers, so top-level presence suffices.
4. **`unknown` for untyped JSON nodes:** schema nodes with no `type`/`properties` (e.g. `fact_value.value`, `original_value`) generate TS `unknown` (forces a narrowing check at use sites) rather than `any`.

## Known limitations

1. **Web client type is still narrow (`"1.0.0" | "1.1.0"`) at `apps/web/src/lib/property-profile.ts:70`.** This is the handwritten competing representation the generated types replace. It is compile-time only (TS is erased at runtime), so the web-e2e Playwright job — which flows live 1.2.0 responses through the client at runtime with no runtime version check — stays green. Widening/removing it is M2-T002's client migration (apps/web is forbidden here). **Coordination note for M2-T002:** import `packages/contracts/generated/property_profile.ts` and drop the handwritten type; the generated union already includes 1.2.0.
2. **The generator is bespoke** (not a widely-adopted tool). It covers exactly the constructs these four schemas use; a future schema using unsupported keywords (e.g. `allOf`, `oneOf`, tuple `items`) would need generator extension. Guarded by the 100%-key-coverage test which would fail if a new key were not emitted.
3. **Local Python is 3.11**, one minor below the declared `>=3.12`; verified import/run-clean locally, and CI runs 3.12.

## Security / provenance impact

- **Provenance preserved:** no field mapping, digest, lineage, or provenance-ref logic changed. `_assert_provenance_integrity` still runs; the new `validate_profile` is an ADDITIONAL pre-send gate, strictly tightening the contract.
- **No secret/internal leakage:** the two new typed 500 responders log only fixed classifiers (`reason` ∈ {schema_validation_failed, missing_profile_version, malformed_contract_version, declared_version_below_emitted_keys}) and echo only the builder's own declared version (not untrusted upstream content). No stack traces, tokens, or builder internals in any response body (asserted by `test_s8_route_..._Traceback not in text`).
- **Bounded errors:** unpublished versions and contract failures are typed, correlation-id'd, and bounded — never a raw 500 stack, never silent coercion.
- The endpoint remains INTERNAL/DEV-ONLY (no auth yet, M0-T007/T008 blocked on Supabase token) — unchanged by this task and already documented in the route module.

## New risks / dependencies

- **M2-T002 dependency:** must consume the generated types and the S4 client-regression fixture, and widen/remove the handwritten `property-profile.ts` type. Documented above.
- **CI job count +1** (`contracts-typegen`); stdlib generator + one `pip install pytest` in that job only.
- No new runtime dependency in the API: `jsonschema` was already a test/validation dependency; `validate_profile` uses it. If a production deployment excluded `jsonschema` from runtime deps, the pre-send validation would fail to import — **recommend confirming `jsonschema` is a runtime (not dev-only) dependency for the API service** before this endpoint is served in production (flagged for the orchestrator; currently `jsonschema` is under `[dev]` extras in `services/api/pyproject.toml`). See recommended next tasks.

## Recommended next tasks

1. **M2-T002 (already planned):** client migration to `packages/contracts/generated/property_profile.ts`; wire the S4 client-regression fixture; remove the handwritten `apps/web/src/lib/property-profile.ts` union.
2. **Small follow-up (backend):** move `jsonschema` from `[dev]` to runtime dependencies in `services/api/pyproject.toml` so pre-send `validate_profile` is available in the deployed API (out of this task's test-focused scope; needs a deliberate dependency decision). Flagged as a risk above.
3. **G1 re-verification (S9):** data-contract-verifier diffs `builder.py` to confirm no official-source field mapping/semantics changed.

## Exact report path

`project-control/reports/M2-T003-producer-report.md` (this file, inside the worktree).
