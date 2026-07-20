# M2-T010 Producer Report — Contract-publication tooling: client supported-versions derivation, drift regression, contract.py docstring fix

- **Task ID:** M2-T010
- **Producer:** backend-engineer (isolated worktree `.claude/worktrees/agent-a4cc49236350a9208`)
- **Status requested:** `awaiting_gate`
- **Date:** 2026-07-20
- **Report path:** `project-control/reports/M2-T010-producer-report.md`

## 1. Summary

The web client's runtime `SUPPORTED_CONTRACT_VERSIONS` list is now a GENERATED, marker-delimited block inside `apps/web/src/lib/contract.ts`, derived by `packages/contracts/scripts/generate_ts_types.py` from the canonical schema's `profile_version.contract_version` enum (`packages/contracts/schemas/v1/property_profile.schema.json`). The existing `contracts-typegen` CI job (`generate_ts_types.py --check`) now byte-checks BOTH managed artifacts — `packages/contracts/generated/property_profile.ts` and the client block — so a schema-published version missing from the client list turns CI red. Negative drift regressions (schema-ahead fixture, client-ahead fixture, mangled markers) are executable tests. The backend derivation chain (owner amendment, CT-S7) is asserted with executed evidence, not rebuilt. The stale 1.2.0 module docstring in `services/api/app/profile/contract.py` is corrected (doc-only).

**No contract version was published. The schema enum still ends at 1.3.0. No semantic change to any contract field or validation behavior. No UI change. No workflow change.**

## 2. Design decision (disclosed per task risk "derivation mechanism choice")

**Chosen mechanism: build-time codegen of a marker-delimited block INSIDE `apps/web/src/lib/contract.ts`,** performed by the existing typegen script and checked by the existing `contracts-typegen` CI job. Alternatives rejected:

- *Runtime value import from `packages/contracts/generated/property_profile.ts`*: would break the deliberate M2-T002 discipline that only TYPE-ONLY imports cross the apps/web boundary ("erased at build time, so the Next.js bundle never compiles files outside apps/web"). A runtime import would make the Next build compile a file outside apps/web (`externalDir` risk).
- *New generated module `apps/web/src/lib/*.generated.ts`*: not in `allowed_paths` (only `contract.ts` and `validate-profile.ts` are allowed in `apps/web/src/lib/`).

The marker block preserves the byte-identity CI discipline: `--check` extracts the committed block and byte-compares it against a fresh derivation from the schema enum (universal-newline read on both sides, exactly like the property_profile.ts check, so it is EOL-safe on Windows/Linux). Write mode splices a fresh block between the markers and is idempotent. Missing/duplicated/out-of-order markers fail the check loudly (never pass silently).

The compile-time locks are unchanged and still active on top of the codegen: `as const satisfies readonly ContractVersion[]` plus the two-way `ContractEnumAssertions` exhaustiveness proof in `contract.ts`.

**No `.github/workflows/**` change was needed:** the existing `contracts-typegen` job already runs `generate_ts_types.py --check` and `pytest packages/contracts/scripts/tests`, both of which now cover the new derivation; the existing `web`/`web-e2e` jobs run the new vitest drift suite via `npm test`.

## 3. Files changed

| File | Change |
| --- | --- |
| `packages/contracts/scripts/generate_ts_types.py` | Added client-block derivation: `WEB_CONTRACT_PATH`, `CLIENT_BLOCK_BEGIN/END` markers, `contract_version_enum()`, `client_versions_block()`, `extract_client_block()`, `check_client_block()`, `write_client_block()`; `main()` now checks/writes both artifacts; docstring updated. Existing `generate()` output untouched (byte-identical). |
| `apps/web/src/lib/contract.ts` | `SUPPORTED_CONTRACT_VERSIONS` array replaced by the generated marker block (identical members/values); header comment item 2 updated to describe the derivation (removed the stale "closed manual set / coordinated change" narrative). No other export touched. |
| `packages/contracts/scripts/tests/test_generate_ts_types.py` | 8 new tests: schema-enum closure at 1.3.0; committed-block byte-identity; derivation determinism; schema-ahead drift turns `--check` red (isolated client-block red path + end-to-end); client-ahead drift red; mangled-marker red; write-mode publication flow on tmp copies (regenerates block, passes `--check`, idempotent). |
| `apps/web/src/lib/__tests__/contract-versions.test.ts` | NEW vitest suite: client list equals the canonical schema enum exactly (read via `node:fs` at test time only — nothing outside apps/web enters the bundle); exact current set 1.0.0–1.3.0 and no 1.4.0; negative schema-ahead fixture (`9.9.9`) detected by the same detector the positive lock uses; reverse-drift detection. |
| `services/api/app/profile/contract.py` | **Docstring-only** correction (module docstring "Design" bullet): no longer describes 1.2.0 as the current builder declaration; now states M2-T006 advanced `PROFILE_CONTRACT_VERSION` to 1.3.0 (`reproducibility.staleness`), notes the M2-T010/M2-T006-G3-LOW-D1 correction. Zero code change (ruff + full pytest green, see CT-S4). |
| `project-control/reports/M2-T010-producer-report.md` | This report. |

`packages/contracts/generated/property_profile.ts`: **regenerated-identical** — write mode rewrote it byte-identically (`git diff` empty; the transient `M` status was git `core.autocrlf=true` EOL normalization only, restored via `git checkout --`; `--check` rc=0 proves identity). `apps/web/src/lib/validate-profile.ts`: untouched (already consumes `SUPPORTED_CONTRACT_VERSIONS` from contract.ts). Schema files: untouched. Workflows: untouched. `services/api/tests/**`: untouched (existing tests already prove the backend chain; nothing was genuinely required — narrowed-scope discipline respected).

## 4. Contracts/schema changed

**None.** Schema enum unchanged (ends at 1.3.0, proven by `test_schema_enum_is_closed_at_1_3_0` and CT-S5 below). Generated artifact regenerated-identical only. No new contract version, no semantic change, no validation-behavior change.

## 5. Acceptance scenarios CT-S1..CT-S7 — commands, expected vs actual

Environment: producer worktree on Windows (bash), Python 3.11.9, pytest 8.4.2, ruff 0.9.9, jsonschema 4.26.0, fastapi 0.128.0. Node v22.18.0 present but `apps/web/node_modules` absent (thin-client policy — no local npm install ever); web-suite execution is CI-deferred, see Limitations.

### CT-S1 — derivation (single source of truth; current output exactly 1.0.0/1.1.0/1.2.0/1.3.0; byte-identity preserved)

```
$ python packages/contracts/scripts/generate_ts_types.py --check
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
check rc=0

$ python packages/contracts/scripts/generate_ts_types.py
wrote ...\packages\contracts\generated\property_profile.ts
unchanged ...\apps\web\src\lib\contract.ts
write rc=0
```

Expected: `--check` rc 0 on both artifacts; write mode idempotent on contract.ts; property_profile.ts regenerated byte-identically. Actual: as above (`git diff` on property_profile.ts empty — only autocrlf EOL noise, restored). Pytest proof of block identity and determinism:

```
test_committed_client_block_is_byte_identical_to_fresh_derivation PASSED
test_client_block_derivation_is_deterministic PASSED
test_committed_output_is_byte_identical_to_fresh_generation PASSED
test_check_mode_passes_against_committed_file PASSED
```

Current derived output (block in `apps/web/src/lib/contract.ts` lines 86–99): exactly `"1.0.0","1.1.0","1.2.0","1.3.0"`. **PASS.**

### CT-S2 — drift regression (negative): schema-published version missing from client list fails loudly

```
$ python -m pytest packages/contracts/scripts/tests -v   (tail)
test_drift_schema_published_version_missing_from_client_turns_check_red PASSED
test_drift_end_to_end_check_fails_when_schema_moves_ahead PASSED
test_client_block_check_red_when_client_ahead_of_schema PASSED
test_client_block_check_red_when_markers_are_mangled PASSED
test_write_mode_updates_stale_client_block_from_schema PASSED
============================= 14 passed in 0.40s ==============================
```

Mechanics of the primary red-path test: the four canonical schemas are copied to tmp, `"1.4.0"` is appended to the `contract_version` enum (simulated publication), `SCHEMA_DIR` is pointed at the fixture, and the property_profile.ts half of `--check` is satisfied against a fresh tmp generation so the failure is attributable to the CLIENT block alone. `main(--check)` returns **rc 1** and stderr contains "SUPPORTED_CONTRACT_VERSIONS block" + "out of date" — the exact CI-red path of the `contracts-typegen` job. The end-to-end companion proves the same publication also reddens the committed-artifact half (drift cannot pass either half). Reverse drift (client ahead of schema) and mangled markers also fail. The web-side negative fixture (schema-ahead `9.9.9`) is in `contract-versions.test.ts` (runs in CI web jobs). **PASS.**

### CT-S3 — compatibility: 1.0.0–1.3.0 payloads validate; no behavior change

- Client runtime values are IDENTICAL (same four versions, same order); only comments/markers changed around the array, so no behavior change is possible in `validate-profile.ts` (untouched) or any consumer.
- Backend full suite (includes the 1.0.0–1.3.0 payload fixtures and `test_accepts_every_published_contract_version`-style checks in `tests/api/test_property_contract.py`):

```
services/api$ python -m pytest -q
522 passed in 5.37s
```

- Web vitest (`validate-profile.test.ts` "accepts every published contract_version" 1.0.0–1.3.0) and Playwright e2e: **not runnable locally** (no `node_modules`; local npm install prohibited by the low-storage policy). CI `web` (lint+typecheck+build) and `web-e2e` (vitest+Playwright) jobs provide this evidence on push — orchestrator to capture (this is the established division of labor). **PASS locally-provable portion; web-suite execution CI-deferred, disclosed.**

### CT-S4 — docstring correction; api pytest green

```
services/api$ python -m pytest tests/api -q
79 passed in 2.92s
services/api$ ruff check app/profile/contract.py
All checks passed!
```

`services/api/app/profile/contract.py` module docstring now states the builder declares 1.3.0 (M2-T006, `reproducibility.staleness`) and that 1.0.0/1.1.0/1.2.0 instances remain valid. Diff is confined to the docstring bullet (doc-only; ruff+pytest green). **PASS.**

### CT-S5 — no-publication proof

```
$ git status --porcelain
 M apps/web/src/lib/contract.ts
 M packages/contracts/scripts/generate_ts_types.py
 M packages/contracts/scripts/tests/test_generate_ts_types.py
 M services/api/app/profile/contract.py
?? apps/web/src/lib/__tests__/contract-versions.test.ts
```

Schema files untouched. `test_schema_enum_is_closed_at_1_3_0` asserts the enum is exactly `["1.0.0","1.1.0","1.2.0","1.3.0"]`; `test_generated_types_pin_the_closed_contract_version_enum` (pre-existing) asserts no `"1.4.0"` leaks into the generated union; the new vitest suite asserts the client list contains no `"1.4.0"`. `packages/contracts/generated/property_profile.ts` regenerated-identical (empty `git diff`). Contract-schema validator:

```
$ python .github/scripts/validate_contracts.py   (tail)
Checked 6 schema file(s); 0 failure(s).
```

**PASS.**

### CT-S6 — full repository CI green on both events

Local proxies all green: full api pytest (522), typegen pytest (14), `generate_ts_types.py --check`, `sync_contract_schemas.py --check`, `validate_contracts.py`, ruff. The `web`, `web-e2e`, `contracts-typegen`, `contracts-schema-bundle`, `contracts`, `api`, `control-plane` jobs run on push/PR after the orchestrator integrates this worktree; producer cannot push (ADR-005). **CI execution deferred to orchestrator — evidence to be captured on the PR.**

### CT-S7 — backend derivation proof (owner amendment 2026-07-20)

Both halves of the backend chain exercised and green, proving BOTH declarations follow the single canonical source:

```
$ python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.
sync-check rc=0

services/api$ python -c "from app.profile.contract import ..."
backend SUPPORTED_CONTRACT_VERSIONS = ('1.0.0', '1.1.0', '1.2.0', '1.3.0')
derived at import from bundled schema package: app._contract_schemas.v1
re-derivation identical: True

services/api$ python -m pytest tests/api/test_contract_schema_packaging.py -q
4 passed in 0.02s
```

Chain: canonical `packages/contracts/schemas/v1/*.schema.json` → (byte-identity, `sync_contract_schemas.py --check` + `contracts-schema-bundle` CI job) → bundled `app/_contract_schemas/v1/*` → (import-time enum read, `_supported_versions()`) → backend `SUPPORTED_CONTRACT_VERSIONS`. The pre-existing tests `test_supported_versions_populated_without_packages_relative_access` and `test_module_helper_loads_bundled_schema` pin the tuple and the enum read path; nothing was rebuilt. Client chain (new): same canonical schema → (`generate_ts_types.py` codegen + `contracts-typegen --check` byte-identity) → `contract.ts` generated block → `validate-profile.ts`. **PASS.**

## 6. Commands run (complete list)

```
python packages/contracts/scripts/generate_ts_types.py --check      # rc 0 (both artifacts OK)
python packages/contracts/scripts/generate_ts_types.py              # write; contract.ts "unchanged" (idempotent)
git checkout -- packages/contracts/generated/property_profile.ts    # restore autocrlf EOL-only rewrite
python -m pytest packages/contracts/scripts/tests -q                # 14 passed
python -m pytest packages/contracts/scripts/tests -v                # names in CT-S2 evidence
services/api: python -m pytest tests/api -q                         # 79 passed
services/api: python -m pytest -q                                   # 522 passed (full suite incl. connectors/resilience, read-only)
services/api: ruff check app/profile/contract.py                    # All checks passed
python services/api/scripts/sync_contract_schemas.py --check        # OK, rc 0
services/api: python -c "<import contract module, print tuple>"     # ('1.0.0','1.1.0','1.2.0','1.3.0')
services/api: python -m pytest tests/api/test_contract_schema_packaging.py -q   # 4 passed
python .github/scripts/validate_contracts.py                        # 6 schemas, 0 failures
git status --porcelain                                              # exact intended file set
```

## 7. Assumptions and defaults

- "Byte-identity CI discipline preserved" is satisfied by extending the SAME `--check` entry point the `contracts-typegen` job already runs; no workflow edit is required or made.
- Marker-block codegen inside `contract.ts` is within "apps/web/src/lib/contract.ts ... (derivation consumption only)" — the file consumes the derivation by carrying the generated block; no new apps/web file outside `__tests__/` was created.
- Enum order in the schema is authoritative and stable (ascending semver today); the block reproduces schema order verbatim.
- Running (not editing) `services/api/tests/{connectors,resilience}` for regression evidence does not violate the M2-T011 disjointness rule (read-only execution, zero edits there).

## 8. Known limitations

1. **Web suites not executed locally** (vitest, tsc typecheck, eslint, Playwright): `apps/web/node_modules` is absent and local npm installs are prohibited (docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md). The new test file and contract.ts edits are static-verified (import depth `../../../../../packages/...` = 5 levels from `__tests__` to repo root; vitest include pattern matches; `node:fs` is available to vitest in the jsdom environment since tests execute in Node). CI `web` + `web-e2e` jobs are the authoritative green evidence — orchestrator to capture on push.
2. The client block's byte-identity check normalizes EOL via Python universal-newline reads (same as the pre-existing property_profile.ts check); on `core.autocrlf=true` Windows checkouts, write mode may rewrite files LF (content-identical; git normalizes). CI runs on LF checkouts where comparison is exactly byte-for-byte.
3. Documented maintenance considerations carried WITHOUT new microtasks (owner instruction, task input 5): (a) M2-T006 TypedDict suggestion for builder internals; (b) stronger staleness conditional encoding (`if/then` remains outside the `validate_contracts.py` allowlist). Recorded here only.

## 9. Security / provenance impact

None adverse. Tooling and documentation only: no endpoint, auth, storage, secret, upload, or logging change. Provenance is strengthened: the published-version list now has a single provable source (the canonical schema enum) on BOTH the client and backend, each protected by a byte-identity CI check and negative drift tests — a silently omitted published version can no longer reach either runtime.

## 10. New risks or dependencies

- Anyone hand-editing the generated block in `contract.ts` will be caught by `contracts-typegen` (`--check` rc 1) and by the vitest equality lock — intended friction; the fix is always "edit schema, run generator".
- Publication of 1.4.0 (M2-T012) now requires: schema enum edit → `generate_ts_types.py` (client block + TS union) → `sync_contract_schemas.py` (backend bundle) → update the two intentionally hardcoded pins in tests (`test_schema_enum_is_closed_at_1_3_0`, vitest "exactly 1.0.0–1.3.0" case) which exist precisely to make publication a reviewed act, plus the pre-existing pinned expectations (e.g. `test_contract_schema_packaging.py`, `validate-profile.test.ts`). This is the intended "no silent publication" property, not drift.

## 11. Recommended next tasks

- M2-T012 (contract 1.4.0 publication) is now unblocked once this task is accepted: the client list follows the schema by regeneration.
- Optional hygiene (no new microtask created, per owner consolidation instruction): fold the two pre-existing hardcoded version lists in `validate-profile.test.ts` ("accepts every published contract_version") into the schema-derived helper introduced by `contract-versions.test.ts` when that file is next touched.

## 12. Evidence locations

- This report: `project-control/reports/M2-T010-producer-report.md`
- Drift tests: `packages/contracts/scripts/tests/test_generate_ts_types.py` (8 new), `apps/web/src/lib/__tests__/contract-versions.test.ts` (new)
- Mechanism: `packages/contracts/scripts/generate_ts_types.py`; generated block: `apps/web/src/lib/contract.ts` lines 86–99
- Docstring fix: `services/api/app/profile/contract.py` module docstring
- All command outputs: section 5/6 above (exact tails as executed in this worktree)
