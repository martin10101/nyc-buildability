---
name: m2-t003-g3-carryforward
description: M2-T003 property-API boundary + contract-1.2.0 hardening G3+G4 PASS @3a78fdd; packaging-rework closed M2-T004 D5; residual notes for M2-T002 client migration
metadata:
  type: project
---

M2-T003 (property API boundary + contract-version hardening; owner code-audit P0) — G3+G4 PASS @ 3a78fdd on branch task/M2-T003-property-api-contract (b4df7ae initial + 3a78fdd packaging rework). Resolves the [[m2-t004-g3-carryforward]] D5 deferral (builder declared stale 1.0.0 vs schema 1.2.0): builder now declares 1.2.0 with declared-vs-emitted-key-set validation (`app.profile.contract.VERSION_INTRODUCED`).

**What is settled (verified independently, not from producer report):**
- Backend validates every 200 payload against the SELECTED canonical schema before send (`validate_profile` wired in properties.py step 3). Invalid 200 structurally impossible — proven by S2 monkeypatch tests (drop required key / wrong type / broken provenance_ref -> typed 500 internal_contract_error).
- `SUPPORTED_CONTRACT_VERSIONS` read LIVE from the schema enum (no hard-coded stale version); = ('1.0.0','1.1.0','1.2.0'). Fails loud if schema shape changes.
- STATUS_STATE_MATRIX (properties.py) is the single source of truth; `test_s3_matrix_has_no_untested_pairs` asserts tested-set == full matrix (locks it both ways — no undocumented AND no unreachable pairs). 10 pairs, all driven.
- Unsupported version (1.3.0/9.9.9) -> bounded typed 500 unsupported_contract_version, never coerced, no traceback leaked.
- Backward compat: 1.0.0 (full_example.json) + 1.1.0 (full_example_v1_1.json) still validate. Additive-only; schema shape unchanged.
- Typegen: stdlib-only Python generator, byte-identical drift check (contracts-typegen), 100% key coverage, pins closed enum. Ran --check locally = OK.

**PACKAGING REWORK (the previously-failing web-e2e defect) — CLOSED:**
Schema load uses `importlib.resources` on bundled package data `app._contract_schemas.v1` (NOT `Path(__file__).parents[...]/packages`). Root cause was non-editable `pip install ./services/api`: `app/` in site-packages has no sibling `packages/`, so repo-relative walk raised FileNotFoundError at import. Fix verified: (1) importlib.resources loads all 4 bundled schemas; (2) pyproject `[tool.setuptools.package-data] "app._contract_schemas.v1"=["*.schema.json"]` + find_packages(include=['app*']) discovers the data subpackage (has __init__.py); (3) AST regression test forbids any `packages/contracts` runtime string or `Path(...).parents` schema walk; (4) bundled == canonical byte-identical (sha256 matched all 4) via sync_contract_schemas.py + contracts-schema-bundle CI drift guard; (5) jsonschema moved to RUNTIME deps (was dev-only — that was the second half of the web-e2e failure: validate at REQUEST time needs it in prod install).

**Verified locally (python 3.11.9, deps already present, no install):** full api suite 211 passed; M2-T003+touched tests 96 passed; typegen tests 6 passed; ruff clean; contracts validator 0 failures; both drift checks OK; wheel data-subpackage discovery confirmed.

**Why:** M2-T002 (web client migration) and M1-T009 depend on this. Future contract bumps must keep bundled schemas synced + typegen regenerated.

**How to apply — residuals / carry-forward for M2-T002 and later:**
1. Web client type still pins 1.0.0|1.1.0 — CORRECT scoping (apps/web is forbidden here; migration is M2-T002). Not a defect. M2-T002 must consume `packages/contracts/generated/property_profile.ts` (pins closed enum incl 1.2.0) and wire `fixtures/client_regression/http500_state_no_match.json` as the incoherent-(500,no_match) regression input.
2. Any future task that regenerates contract schemas/fixtures MUST also: re-run sync_contract_schemas.py (bundle), regenerate typegen, and include the shared-fixture web blast-radius (apps/web/src/test-support/fixtures.ts cross-imports contract fixtures — [[m2-t004-g3-carryforward]] lesson 6).
3. Scope note: `git diff main` shows project-control/gates,state.json,M0-T016.json,report deletions — these are merge-base drift (main advanced), NOT this task's commits. Confirm scope via `git diff <merge-base> HEAD` not `git diff main`. Merge-base here = 7087ee1.
4. Non-blocking: `_unsupported_contract_version_500` does a function-local `from app.profile.contract import SUPPORTED_CONTRACT_VERSIONS` — harmless (avoids a partial-import cycle concern) but a module-level import would be cleaner; drop at next properties.py edit.
5. R1 (re-review 2026-07-17): `_DEFAULT_ERROR_STATUS=503` fallback in properties.py would emit an UNDOCUMENTED (503, <new_state>) pair if the connector ever grows a fifth error_type (today closed set {rate_limited, source_unavailable, timeout, schema_drift}, all mapped). Any connector error-type addition must extend STATUS_STATE_MATRIX + its bidirectional test.
6. R2: typegen emits `{}[]` for `zoning.mapped_features` (schema items `{"type":"object"}`); TS `{}` is looser than "object". Generator has no oneOf/anyOf/allOf support — fine today (schemas don't use combinators); recheck if the contract grows them.
7. R3: declared-vs-emitted consistency covers ONLY the three top-level keys in `VERSION_INTRODUCED`; nested versioned keys (per-fact coverage_status, district-provenance maps, source_fact lineage keys, feasibility_relevant) are deliberately unchecked (documented in contract.py). Sufficient for the real builder; remember if a second producer appears.
8. R4: [[m2-t004-g3-carryforward]] D2 (unused `result` param, builder.py `_status_dimensions` ~line 419) STILL open after this task's version-constant-only builder edit; drop at next substantive builder edit.
9. Root property_profile schema is additive-OPEN (no root `additionalProperties: false`): a reviewer probe with an unknown extra top-level key PASSES backend validation — canonical M2-T004 schema design (enables additive evolution), not an M2-T003 defect; remember when evaluating "invalid 200 impossible" claims (impossible = schema-invalid, not unknown-key-free).
10. S4 fixture nuance: `client_regression/http500_state_no_match.json` is API-response-level (`http_status`/`response_headers`/`response_body`) — replayable via the web `jsonResponse()` fetch-stub (apps/web/src/test-support/fixtures.ts), NOT via the M2-T001 connector-seam harness (the real route structurally cannot emit the incoherent pair). M2-T002 must wire it at client-transport level; the fixture's `_consumed_by` says so.
