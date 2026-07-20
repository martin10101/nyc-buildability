<!-- Preserved VERBATIM by the orchestrator from the code-reviewer G3+G4 gate return, 2026-07-20 (transport entity-decoding only). Reviewer read-only per ADR-005; gate recorded by the orchestrator. -->

# M2-T010 — G3 (independent walkthrough) + G4 (integration/regression) Gate Report

## VERDICT: PASS (zero defects)

Task M2-T010 (contract-publication tooling) merged to main at **555d68a** (PR #51). Reviewed independently from acceptance scenarios CT-S1..CT-S7; producer claims reproduced from a clean read of the merged tree. READ-ONLY per ADR-005 — orchestrator records the gate.

---

## Commands run (exact) + result tails

| Command (cwd) | Result |
|---|---|
| `python -m pytest scripts/tests -q` (packages/contracts) | **14 passed** in 0.36s |
| `python scripts/generate_ts_types.py --check` (packages/contracts) | `OK: generated TypeScript types...` + `OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.` — **rc=0** |
| `ruff check app/profile/contract.py` (services/api) | `All checks passed!` — **rc=0** |
| `python -m pytest tests/api -q` (services/api) | **79 passed** in 2.68s |
| `python -m pytest -q` (services/api, full) | **538 passed** in 5.50s |
| `python scripts/sync_contract_schemas.py --check` (services/api) | `OK: runtime-bundled contract schemas are byte-identical...` — **rc=0** |
| backend enum derivation (import) | `('1.0.0','1.1.0','1.2.0','1.3.0')` |
| schema on disk `profile_version.contract_version.enum` | `['1.0.0','1.1.0','1.2.0','1.3.0']` |
| marker count in contract.ts | exactly 1 BEGIN / 1 END |
| write mode re-run then `git diff --stat` | empty (idempotent; only autocrlf LF/CRLF warning) |

## Focus findings

1. **Codegen approach (generate_ts_types.py)** — CORRECT. Marker block extracted/checked/spliced deterministically from the schema enum in schema order. Single BEGIN/END pair enforced (`extract_client_block` fails on 0/2 markers or out-of-order → red). Write mode idempotent, no double-generation. `contract_version_enum()` raises (never guesses) if the schema stops exposing the enum. `generate()` output byte-identical (property_profile.ts unchanged). No semantic schema change.

2. **No publication >1.3.0** — CONFIRMED. Schema enum ends at 1.3.0 on disk; merge diff touches NO schema JSON or generated artifact; `test_schema_enum_is_closed_at_1_3_0` pins it; generated union carries no "1.4.0". CT-S5 satisfied.

3. **contract.py docstring (CT-S4)** — CONFIRMED doc-only. Diff (6dfac68→555d68a) is confined to the module-docstring "Design" bullet: now states M2-T006 advanced `PROFILE_CONTRACT_VERSION` to 1.3.0 and 1.0.0–1.2.0 remain valid. Zero code change; ruff + 538 pytest green. Matches actual builder behavior. Closes M2-T006 LOW-D1.

4. **Orchestrator vitest fixup (6e9d8b1) — reviewed hardest: CORRECT & MEANINGFUL, NOT weakened.**
   - The original `fileURLToPath(import.meta.url)` genuinely threw `ERR_INVALID_URL_SCHEME` under jsdom (non-`file:` `import.meta.url`). The fix `path.resolve(process.cwd(), "../../packages/contracts/schemas/v1/property_profile.schema.json")` is correct: CI runs vitest with `working-directory: apps/web` (ci.yml line 77) and `vitest.config.ts` sets no custom `root`, so `process.cwd()`=`apps/web`; the relative path resolves to the real canonical schema (verified on disk).
   - The suite still reads the **on-disk canonical schema** at test time and asserts `[...SUPPORTED_CONTRACT_VERSIONS].toEqual(canonicalSchemaEnum())` — a genuine client==schema-enum positive lock (not a hardcoded copy). Drift is caught two ways: schema-ahead `9.9.9` via the same `omittedVersions` detector the positive lock uses, plus reverse-drift. Negative regression intact.
   - Robust failure mode: a wrong cwd makes `readFileSync` **throw** (loud red), never a false green.

5. **Publication-friction risk (report §10)** — ACCEPTABLE / INTENDED, not a hazard. 1.4.0 will require updating two hardcoded pins (`test_schema_enum_is_closed_at_1_3_0` + the vitest "exactly 1.0.0–1.3.0" case) plus pre-existing pins. This is precisely the "no silent publication" property M2-T012 must exercise. Producer disclosed it accurately.

## Acceptance scenarios
CT-S1 PASS · CT-S2 PASS · CT-S3 PASS (backend-provable portion; web vitest/Playwright CI-deferred per low-storage policy — established division of labor, not a BLOCKED condition) · CT-S4 PASS · CT-S5 PASS · CT-S6 PASS (local proxies all green; push-event CI for orchestrator to capture) · CT-S7 PASS (both backend chain halves exercised).

## Observations (non-blocking, no severity)
- **OBS-1 (OBSERVATION):** Web vitest + Playwright not executed locally (no `apps/web/node_modules`; local npm prohibited). CI `web`/`web-e2e` are authoritative; orchestrator should confirm those jobs green on the PR before final acceptance sign-off (this is normal for this repo, not a defect).
- **OBS-2 (LOW, pre-existing, carried):** `validate-profile.test.ts` still hardcodes a separate 1.0.0–1.3.0 list; producer recommends folding it into the schema-derived helper on next touch. Owner's consolidation instruction correctly declined to spawn a microtask. Recheck at next apps/web/src/lib test touch.

## Scope / provenance
Merge diff = exactly 6 files, all within `allowed_paths`; no forbidden path touched (no UI, no workflow, no `services/api/**` beyond the one docstring, no `project-control/**` beyond own report). Provenance strengthened: published-version list now has a single provable canonical source (schema enum) on BOTH client and backend, each byte-identity-checked with negative drift tests. No security/auth/storage/secret impact.

Relevant files:
- `packages/contracts/scripts/generate_ts_types.py`
- `apps/web/src/lib/contract.ts` (block lines 86–99)
- `apps/web/src/lib/__tests__/contract-versions.test.ts` (orchestrator-fixed)
- `packages/contracts/scripts/tests/test_generate_ts_types.py`
- `services/api/app/profile/contract.py`

Recommend orchestrator record **G3 PASS** and **G4 PASS**. OBS-1/OBS-2 are non-blocking. (CI web/web-e2e confirmed green on PR #51 by the orchestrator before merge.)
