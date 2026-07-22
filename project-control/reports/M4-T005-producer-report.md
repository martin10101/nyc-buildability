# M4-T005 — Producer self-check report (consolidated)

**Frozen implementation SHA:** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (PR #84, base `9e8c22c`).
**CI at frozen SHA:** MERGEABLE / CLEAN, **25/25 checks SUCCESS** (incl. `web-e2e` in the installed wheel, `contracts`, `contracts-typegen`, `contracts-schema-bundle`, `api`, `exact-production-install`).
**Producers:** backend-engineer (contract, API, deployability), frontend-engineer (property screen). Independent of all assigned reviewers.
**Holds:** nothing Published/Verified/accepted; results always draft (`assert_not_verified` end-to-end); endpoint disabled-by-default in production; `property_profile` 1.4.0 and existing `/properties/{bbl}` unchanged; M4-T001 unaccepted; PR #64, CP-0032, expansion holds untouched.

## What shipped (by phase)
- **Phase 1 — `rule_evaluation` v1.0.0 contract** (`43b7ac5`): `packages/contracts/schemas/v1/rule_evaluation.schema.json`; `coverage_status` referenced from the canonical schema via `allOf`+subset (excludes `verified`, never redefined); input identified by reference (`bbl` + `profile_contract_version` + sha256 `input_fingerprint` + `input_provenance`), root `additionalProperties:false` rejects an embedded profile; typegen (`generated/rule_evaluation.ts`) + runtime bundle + validate_contracts wired; canonical valid/invalid fixtures + contract tests. `property_profile` 1.4.0 byte-identical.
- **Phase 2 — internal flag-gated endpoint + FH-4** (`86f4b9f`): `GET /api/v1/properties/{bbl}/rule-evaluation`; server-side rebuild via trusted `build_property_profile` (never a browser-supplied profile); serializer maps to the contract by reference (no embed) with `assert_not_verified` + strict bundled-schema validation before send; safe typed errors (no traceback/secret/path); FH-4 routes `as_of_date` through `_valid_iso_date` at `detect_rule_conflicts` (additive, fail-closed). Feature flag `INTERNAL_RULE_EVAL_ENABLED` fail-safe (absent/unknown → generic 404, `include_in_schema=False`).
- **Phase 3 — property-screen draft surface** (`4209cf6`): additive; two-factor fail-safe frontend flag (server-only `INTERNAL_RULE_EVAL_UI` + `?ruleeval=on`) gates BOTH render and fetch; hardened typed client (exact status/state matrix, runtime-validates 200 vs generated types, bounded reflected text, abort/timeout); six UI states + keyboard/live-region a11y + provenance drill-down; result never shown as Published/Verified/legally-final/guaranteed; existing property behavior untouched.
- **Phase 2b — installed-wheel deployability fix** (`b14097f`, `aa2cfa8`, `fcffce9`, `84b50a7`): the rule engine read four runtime data-resource classes from disk that were absent from the installed wheel (`pip install --no-deps .`), 500-ing the endpoint in web-e2e and the real Render deploy — a latent M4-T001 gap the endpoint is the first to exercise. Fixed by shipping all four as package-data: ZR snapshots bundled under `app/_zr_snapshots/v1/` (byte-identical, `sync_zr_snapshots.py --check` + guard test) with `snapshots.py` resolving via `importlib.resources`+docs fallback; `app/rules/rulesets/*.rule.json` and `app/rules/schemas/v1/*.schema.json` via `app.rules` package-data globs (dirs untouched). Regression guard `test_installed_deployability.py` pins all three package-data declarations. Owner-authorized scope expansion (2026-07-22, Option A).

## Acceptance-scenario evidence (14 scenarios)
- AS-1/AS-2 (contract): schema validates real `export()` payloads; `$ref` reuse; `property_profile` byte-identical — **contracts/contracts-typegen/contracts-schema-bundle green**.
- AS-3/AS-5/AS-6/AS-7/AS-8 (API results): applicable-draft, unsupported/not-applicable, missing-evidence fail-safe, typed conflict, spatial-uncertainty ranges — proven in `services/api/tests/api/test_rule_evaluation_api.py` and end-to-end in `apps/web/e2e/rule-evaluation.spec.ts` (real route→builder→evaluator→serializer→validate). **api + web-e2e green.**
- AS-4 (security prod-disable): flag OFF/unknown → generic 404, `include_in_schema=False`; `assert_not_verified` boundary — API tests + `rule-evaluation-flag-off.spec.ts` (surface absent AND zero `/rule-evaluation` calls).
- AS-9 (FH-4): impossible date fails closed identically on both paths — `test_rules_fh4_temporal_parity.py`.
- AS-10 (safe errors): typed errors, no internal-trace/secret/path, strict JSON — API tests.
- AS-11/AS-12 (UI failure recovery + a11y): recoverable failure leaves profile usable; keyboard/announcements/focus/provenance — component + e2e specs.
- AS-13 (honesty): no Published/Verified/guaranteed wording; not_verified disclaimer end-to-end; existing `honesty.spec.ts` still passes.
- AS-14 (regression): full `api` suite (**857 tests**) + `web`/`web-e2e` green; existing `/properties/{bbl}` matrix unchanged.

## Independent orchestrator validation (local, pre-freeze)
Contract + API re-run in the task worktree at each phase: typegen/bundle/validate_contracts green; 857 pytest pass; ruff clean; security-critical files (`config.py`, `rule_evaluation.py`, `response.py`, `snapshots.py`) audited; `properties.py`/`integration.py`/`evaluator.py`/`property_profile` byte-identical. Frontend validated by CI (`web`, `web-e2e`) — no local npm (thin-client).

## Transparency: temporary debug commits (all reverted before freeze)
Diagnosing the installed-wheel failures required capturing the server traceback (the endpoint deliberately logs type-only). Commits `3f66ae7`/`d9c601e` switched the `stage=evaluate` log to `logger.exception`; both were reverted (`face5a8`, `84b50a7`). The frozen SHA `84b50a7` contains the safe type-only logging — verified: no `TEMP-DEBUG`/`logger.exception` remains in `rule_evaluation.py`.

## Requested status
`awaiting_gate`. Not self-accepting. Risk-required gates at `84b50a7`: **G1** data-contract, **G3** code, **G4** integration + UI/a11y (human-journey), **G5** security.
