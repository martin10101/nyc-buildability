<!-- Verbatim reviewer return (agent-return channel; agentId a81379575b266e456, data-contract-verifier, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: PASS (no blocking or non-blocking corrections). -->

# G1 Gate Report — M2-T003 (Property API boundary + contract-1.2.0 hardening)

**Reviewer:** data-contract-verifier (independent, read-only per ADR-005)
**Target:** worktree `.claude/worktrees/M2-T003`, branch `task/M2-T003-property-api-contract`, HEAD incl. packaging rework `3a78fdd`
**Gate lens:** This is contract/API hardening, NOT a new government connector. G1 scope focused on official-source-fidelity (S9), contract-version canonical correctness, bundle provenance integrity, backward compatibility, and unsupported-version bounding — not general code quality (G3).
**Date:** 2026-07-17

## Method
Read the M2-T003 packet (S1–S10) and `packages/contracts/README.md` §78/§167. Diffed `builder.py`, the two touched test files, and the canonical schemas against `main` (read-only `git diff`/`git hash-object`). Read `services/api/app/profile/contract.py`, `properties.py`, the packaging test, and `sync_contract_schemas.py`. Independently ran the drift-check command and the api test subset in the sandbox.

## Verification table

| Scenario / Concern | Method | Result |
| --- | --- | --- |
| **S9 — no official-source field mapping/semantics/units changed (core G1 concern)** | `git diff main -- services/api/app/profile/builder.py` | **PASS.** Only change is `PROFILE_CONTRACT_VERSION` `"1.0.0"`→`"1.2.0"` plus its comment and one docstring paragraph (22 lines, 2 hunks). `FEASIBILITY_COLUMNS`, PLUTO column buckets, all field mapping/normalization, and the M2-T004 digest/lineage logic never appear in the diff — untouched. |
| **1.2.0 canonical, read live (not hard-coded)** | Read `contract.py` `_supported_versions()`; `git diff main` on canonical schema; source-grep test | **PASS.** Backend reads the closed enum LIVE from `property_profile.schema.json` via `_supported_versions()`; `SUPPORTED_CONTRACT_VERSIONS=("1.0.0","1.1.0","1.2.0")`. Canonical schema has NO diff vs main (enum landed in dependency M2-T004; this task correctly consumes it). Builder now declares 1.2.0; `test_s6_no_stale_version_hard_coded_in_builder_source` asserts `PROFILE_CONTRACT_VERSION = "1.0.0"` absent. README §167 deferral resolved and documented in §167 replacement text. |
| **Bundle byte-identity (provenance integrity)** | `git hash-object` canonical vs bundled (4 schemas); `sync_contract_schemas.py --check` | **PASS.** All 4 blob SHAs identical (property_profile `499a3871…`, source_fact `8df7be0a…`, common `d94159d5…`, coverage_status `6aefb396…`). Drift check exits 0 ("byte-identical"). Authority model correct: `packages/contracts/schemas/v1/*` is single source; bundled copies are artifacts regenerated (never hand-edited), loaded via `importlib.resources` to survive non-editable install. `contracts-schema-bundle` CI job + static-guard test (`test_contract_module_has_no_packages_relative_runtime_path`) prevent silent divergence. |
| **Provenance/version persistence unaffected (M2-T004)** | Read builder diff; ran `test_data_semantics.py` | **PASS.** contract_version persisted in `profile_version` as before; digest/lineage/reproducibility fields unchanged. 22/22 data-semantics tests green. |
| **S7 — backward compatibility (1.0.0 + 1.1.0 still validate)** | Read + ran `test_property_contract.py` S7 cases; verified fixtures | **PASS.** `full_example.json` (1.0.0, no additive keys) and `full_example_v1_1.json` (1.1.0, data_completeness+reproducibility) both present and validate unchanged. Additive-optional guarantee proven. |
| **S8 — unsupported version bounded typed error** | Read + ran S8 cases | **PASS.** 1.3.0/9.9.9 → `UnsupportedContractVersionError` → bounded `500 unsupported_contract_version` with declared + supported set, correlation id, no traceback; profile object not mutated (never coerced to a neighbor). |
| **S6 — declared-vs-emitted consistency** | Read `_assert_declared_matches_emitted`; ran S6 cases | **PASS.** `VERSION_INTRODUCED` map drives the check; declaring 1.0.0/1.1.0 while emitting `status_dimensions` (1.2.0 key) rejected as `declared_version_below_emitted_keys`. Kills the exact stale-declaration bug M2-T004 deferred. |
| **S3 — status/state pair matrix** | Read `STATUS_STATE_MATRIX` + parametrized tests | **PASS.** Single-source frozenset; `test_s3_matrix_has_no_untested_pairs` proves every documented pair is exercised and no undocumented pair can ship. |
| **S2 — invalid 200 impossible** | Read fault-injection tests; ran suite | **PASS.** Malformed builder output (missing key / wrong type / broken provenance_ref) → typed `500 internal_contract_error`, never 200. |
| **Test execution** | `pytest test_property_contract.py test_contract_schema_packaging.py test_properties_v1.py` | **PASS. 74 passed.** Data-semantics: 22 passed. |

## Defects
None. Both touched test files (`test_data_semantics.py`, `test_properties_v1.py`) diff as pure version-declaration updates (1.0.0→1.2.0) with no mapping change.

## Observations (non-blocking, informational)
- **O1:** The `internal_contract_error`/`unsupported_contract_version` responses correctly echo only the builder's own declared version and a fixed `reason` classifier — no untrusted upstream content, consistent with the M1-T002 G5 payload-only-logging discipline. (G5 territory; noted for completeness.)
- **O2:** `builder_output_m1_t005.json` intentionally remains a 1.0.0-declaring SCHEMA fixture (validated version-agnostically), documented in README §215; not live builder output. Verified this is deliberate, not a stale-declaration leak.

## Verdict
S9 (the core G1 concern) is clean: no official PLUTO/Geoclient field mapping, unit, normalization, or provenance/digest semantics changed — only the contract-version declaration. 1.2.0 is canonical and read live from the schema; bundled schemas are provably byte-identical to the single canonical source; backward compatibility and unsupported-version bounding are proven by passing tests. No blocking or non-blocking corrections required.

PASS
