<!-- Preserved VERBATIM by the orchestrator from the data-contract-verifier G1 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# G1 GATE REPORT — M2-T010 (data-contract gate)

**Task:** Contract-publication tooling — derive client supported-versions from canonical schema, drift regression, contract.py docstring fix
**Reviewer:** data-contract-verifier (independent; did not implement)
**Merged commit under review:** 555d68a
**Environment:** Windows, Python 3.11.9, pytest 8.4.2, read-only, `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider`

## VERDICT: **PASS**

Both the client and backend supported-version declarations provably derive from the single canonical schema enum (`property_profile.schema.json` → `profile_version.contract_version.enum` = `["1.0.0","1.1.0","1.2.0","1.3.0"]`). No contract version after 1.3.0 was published anywhere. Drift protection is real and correctly isolated. All executed suites green.

## Scenario results (CT-S1..CT-S7)

**CT-S1 — Single-source derivation + byte-identity — PASS**
- `generate_ts_types.py --check` → rc 0, prints both `OK: generated TypeScript types are up to date.` and `OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.`
- Client block is a generated marker block (`contract.ts:86-99`) spliced by `generate_ts_types.py` `client_versions_block()` reading `contract_version_enum()` from the canonical schema (script lines 270-310). Not a second hand-maintained copy. `WEB_CONTRACT_PATH` is `__file__`-relative (`parents[3]`), cwd-robust.
- Current derived value is exactly `"1.0.0","1.1.0","1.2.0","1.3.0"`. `git diff` on `property_profile.ts` and `contract.ts` empty — byte-identical, no drift.

**CT-S2 — Drift detection (negative) — PASS**
- `pytest packages/contracts/scripts/tests -q` → **14 passed**.
- Verified the red-path test is genuine (test file lines 216-240): it appends `1.4.0` to a tmp schema enum, satisfies the property_profile.ts half against a fresh tmp generation, and asserts the **client-block** half returns rc 1 with `"SUPPORTED_CONTRACT_VERSIONS block"` + `"out of date"` — failure correctly attributed to the client block alone. Companion `test_drift_end_to_end...` proves drift reddens BOTH halves; reverse-drift and mangled-marker tests also present and passing. This is the exact CI-red path of the `contracts-typegen` job (ci.yml:153).

**CT-S3 — Compatibility (1.0.0–1.3.0) — PASS**
- `pytest tests/api -q` → **79 passed**; `pytest tests/api/test_property_contract.py -k "version or contract"` → **34 passed**. Client runtime values unchanged (same four, same order); only comments/markers changed around the array — no behavior change possible in `validate-profile.ts` (untouched).

**CT-S4 — Docstring correction — PASS**
- `contract.py:18-23` now states "Task M2-T006 advanced it to `1.3.0`" and "Docstring corrected by task M2-T010 (M2-T006 G3 LOW D1: this text previously still described 1.2.0 as current)." Stale 1.2.0 description gone. api pytest green (above).

**CT-S5 — No publication proof — PASS**
- `grep -rn "1.4.0"` across the 4 managed runtime artifacts (schema, generated TS, contract.ts, backend contract.py, excluding tests) → **NONE**. Generated union: `contract_version: "1.0.0" | "1.1.0" | "1.2.0" | "1.3.0"` (property_profile.ts:52). Schema enum closed at 1.3.0 (schema line 27). `test_schema_enum_is_closed_at_1_3_0` passes.

**CT-S7 — Backend derivation chain — PASS**
- `sync_contract_schemas.py --check` → rc 0 (`runtime-bundled contract schemas are byte-identical to the canonical source`).
- `from app.profile.contract import SUPPORTED_CONTRACT_VERSIONS` → `('1.0.0','1.1.0','1.2.0','1.3.0')`. Read at **import** via `_supported_versions()` from the bundled schema enum (contract.py:142-164) — not hardcoded (grep of `__all__`/module shows no literal list).
- `pytest tests/api/test_contract_schema_packaging.py` → **4 passed**.
- Rejection semantics: `select_schema_version('1.4.0')` raises `UnsupportedContractVersionError` (declared_version preserved, **not coerced** to 1.3.0); all published versions pass through unchanged.

## Orchestrator integration fix (scrutinized)
The vitest test (`contract-versions.test.ts`) resolves the schema via `path.resolve(process.cwd(), "../../packages/contracts/schemas/v1/property_profile.schema.json")`. This is **correct**: the CI `web`/`web-e2e` jobs run `npm run test` with `working-directory: apps/web` (ci.yml:76-78), so `process.cwd()` = `apps/web` and `../../` reaches repo root. The prior `fileURLToPath(import.meta.url)` form throws under jsdom (import.meta.url is not a `file:` URL). The test genuinely asserts client-list == schema-enum (members AND order, lines 56-58) and exercises a schema-ahead `9.9.9` fixture through the same `omittedVersions` detector the positive lock uses (lines 77-88) — not a tautology.

## Defects / observations
1. **OBSERVATION (LOW, not blocking):** The web suite (vitest `contract-versions.test.ts`, tsc, Playwright) was **not executed locally** — `apps/web/node_modules` is absent per the thin-client low-storage policy; local npm install is prohibited. The Python-side drift protection (typegen `--check` + `pytest scripts/tests`) is fully executed and independently proves the client block matches the enum, so the client-side runtime assertion is corroborated by the byte-identity mechanism even without vitest. CI `web`/`web-e2e` jobs are the authoritative execution evidence — orchestrator should confirm those jobs green on the PR. This is the established, disclosed division of labor, not a defect in the work.

## Explicit confirmations
- **No contract version >1.3.0 was published** — schema enum closed at 1.3.0; zero `1.4.0` in any managed runtime artifact; generated union and backend tuple both end at 1.3.0.
- **Both declarations derive from the single canonical source** — client via `generate_ts_types.py` marker block (byte-checked by `contracts-typegen`); backend via `_supported_versions()` import-time read of the byte-identical bundled schema (checked by `sync_contract_schemas.py --check` / `contracts-schema-bundle`). Neither is a hand-maintained list.

**Files relevant to this gate:**
- `packages/contracts/scripts/generate_ts_types.py`
- `apps/web/src/lib/contract.ts` (block lines 86-99)
- `apps/web/src/lib/__tests__/contract-versions.test.ts`
- `packages/contracts/scripts/tests/test_generate_ts_types.py`
- `services/api/app/profile/contract.py`
- `packages/contracts/schemas/v1/property_profile.schema.json` (enum line 27)

Reviewer updated its own agent memory only (`reference_contract-derivation-drift-verification.md` + MEMORY.md index). No ledger/git writes performed per ADR-005.
