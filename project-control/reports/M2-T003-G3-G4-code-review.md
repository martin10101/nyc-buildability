<!-- Verbatim reviewer return (agent-return channel; agentId afe9921d082b8eabc, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdicts: G3 PASS, G4 PASS (zero blocking defects; LOW residuals R1-R4 + observations O-1/O-2 carried forward). -->

# GATE REPORT — M2-T003 — G3 (independent walkthrough) + G4 (integration & regression)

- **Task:** M2-T003 — Property API boundary + contract-1.2.0 hardening (owner code-audit P0)
- **Reviewer:** code-reviewer (independent; did not produce this work; READ-ONLY per ADR-005)
- **Review target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003`, branch `task/M2-T003-property-api-contract`, HEAD = `3a78fdd` (packaging rework) on top of `b4df7ae` (initial implementation); merge-base diff (`git diff main...HEAD`) used for all scope checks
- **Date:** 2026-07-17
- **Method:** Reviewed from the acceptance criteria in `project-control/tasks/M2-T003.json` and `packages/contracts/README.md` §167, not the producer report. Independently executed the offline suites and drift checks locally; ran reviewer-authored adversarial probes not present in the producer's tests. G1 official-source-mapping (S9) is NOT re-litigated per instruction.

## 1. Independent reproduction (commands actually run by this reviewer)

| Command | Result |
|---|---|
| `python -m pytest services/api/tests -q` (from `services/api`) | **211 passed in 2.25s** — matches the CI `api` job count |
| `python -m pytest packages/contracts/scripts/tests -q` | **6 passed** |
| `python packages/contracts/scripts/generate_ts_types.py --check` | **OK: generated TypeScript types are up to date** (rc=0) |
| `python services/api/scripts/sync_contract_schemas.py --check` | **OK: runtime-bundled contract schemas are byte-identical to the canonical source** (rc=0) |
| Reviewer adversarial probes P1–P5 (in-process, see §4) | Behaved as designed (one schema-design observation, §5 O-1) |

All KB-scale; no artifacts written to the owner PC; only `--check` (read-only) modes used. CI status (16/16 green on PR #16 including `web-e2e`, `contracts`, `contracts-typegen`, `contracts-schema-bundle`) is orchestrator-asserted; local reproduction above independently confirms the `api`, typegen, and both drift-check results.

## 2. G3 findings — scenario walkthrough

| Scenario | Verdict | Evidence |
|---|---|---|
| **S1** valid profile validates, declares 1.2.0 | **PASS** | `test_s1_valid_profile_declares_resolved_version_and_validates` drives the real route over the F01 recorded-official fixture: 200, `X-Correlation-ID`, `contract_version == "1.2.0"`, and re-runs `validate_profile` on the served body. `test_s1_validate_profile_accepts_the_real_builder_output` covers the builder directly. All recorded-official fixtures still serve (211-test suite includes the accepted M1-T005/M2-T004 suites). Normal case exercised. |
| **S2** malformed profile → typed 500, never invalid 200 | **PASS** | Three monkeypatched fault injections (drop required key, wrong type, broken `provenance_ref`) each yield `(500, internal_contract_error)` with correlation id and typed `detail.reason`. Structural impossibility confirmed by code inspection: `properties.py:378–391` — `validate_profile(profile)` is on the ONLY 200-emission path, before `_json(200, ...)`; the whole block sits inside the generic-500 guard, so any escape path still cannot produce an invalid 200. Failure case exercised. |
| **S3** pair matrix single source of truth | **PASS** | `STATUS_STATE_MATRIX` (frozenset, `properties.py:96–109`) documents 10 pairs. `test_s3_every_pair_is_documented` parametrizes 7 drive paths; three dedicated tests drive the 500-state paths. Critically, `test_s3_matrix_has_no_untested_pairs` asserts tested-set == matrix **bidirectionally** — no undocumented emission AND no documented-but-unreachable pair. Residual R1 noted (§5). Boundary case (422 with connector-must-not-be-called assertion) exercised. |
| **S5** typegen determinism + coverage | **PASS** | Generator (`generate_ts_types.py`) is stdlib-only, no network; determinism comes from JSON insertion-order iteration, a fixed `NAMED_DEFS` literal, LF + single trailing newline. Handles cross-file `$ref`s, named aliases, string AND numeric enums (`BoroughCode = 1\|2\|3\|4\|5`), `type` lists (`string \| null`), `additionalProperties` maps (index signatures), array-of-union parenthesization, and models untyped nodes as `unknown` (forces narrowing — correct). Coverage test walks the full 4-file `$ref` graph and asserts every schema key appears as a TS member; enum-pinning test forbids unpublished versions. Byte-identity verified locally. Residual R2 (fidelity nit) in §5. |
| **S6** contract_version consistency, no stale hard-code | **PASS** | Builder declares `1.2.0` (`builder.py`); `SUPPORTED_CONTRACT_VERSIONS` is read **live** from the schema enum at import with fail-fast `RuntimeError` guards (`contract.py:134–156`) — no hard-coded version set anywhere in the backend. `VERSION_INTRODUCED` declared-vs-emitted check rejects exactly the deferred stale-declaration bug (`reason=declared_version_below_emitted_keys`, tested for both 1.0.0 and 1.1.0 declarations carrying `status_dimensions`). Source-level guard test forbids `PROFILE_CONTRACT_VERSION = "1.0.0"` reappearing. README §167 deferral is superseded with the decision recorded; fixtures agree (1.2.0 fixture `status_dimensions_lineage_m2_t004.json` present; historical 1.0.0/1.1.0 fixtures documented as schema fixtures, not live output). Soundness caveat R3 in §5. |
| **S7** backward compat 1.0.0 + 1.1.0 | **PASS** | `full_example.json` (1.0.0) and `full_example_v1_1.json` (1.1.0) pass the same backend `validate_profile` the route runs; declared-at-or-below-own-version key carriage explicitly tested; reviewer probe P4 confirms declare-high/emit-low is accepted per the documented decision. The canonical schema directory is byte-untouched vs main (empty diff) — additive-only guarantee holds by construction. |
| **S8** unsupported version → bounded typed error | **PASS** | `select_schema_version` raises typed error carrying the declared version; route maps to `(500, unsupported_contract_version)` with correlation id, declared version, and the closed supported set echoed; no traceback in body (asserted). Non-coercion proven by mutation-check test. Reviewer probe P5: `"01.2.0"` rejected as unsupported, not normalized. Malformed-type (int) and missing/None cases yield distinct typed reasons (probes P2/P3). Missing/ambiguous + failure cases exercised. |
| **S4** 500+no_match transport fixture | **PASS** (with clarification) | `fixtures/client_regression/http500_state_no_match.json` is recorded with exemplary provenance annotations (`_synthetic: true`, derivation, `_consumed_by`). **Format finding:** it is an API-response-level fixture (`http_status`/`response_headers`/`response_body`), which by design CANNOT replay through the M2-T001 harness's connector-seam transport (`fixture_api.py::fixture_response` consumes upstream SODA-level `{http_status, response_body_raw}`, and the harness runs the real route — which structurally cannot emit the incoherent pair; that is the whole point). It IS directly replayable through the web client-transport stub the same e2e ecosystem uses: `apps/web/src/test-support/fixtures.ts::jsonResponse(body, status, correlationId)` maps 1:1 onto the fixture's keys. The fixture self-documents this consumption path. Placed outside `valid/`/`invalid/` so `validate_contracts.py` ignores it; `(500,"no_match") ∉ STATUS_STATE_MATRIX` asserted in test. Judged conformant to the packet's intent ("the frontend regression input for M2-T002"); M2-T002 must wire it at the client fetch-stub level — carry-forward recorded. |
| **S10** regression | **PASS** | Full api suite 211 passed locally; pre-existing test updates (`test_properties_v1.py`, `test_data_semantics.py`) inspected line-by-line — they correctly flip the two deferral-era assertions (`1.0.0` → `1.2.0`) with documentation; no assertion was weakened or deleted. |

**G3 case-type coverage:** normal (S1 200), boundary (S6 declared-1.1.0-with-1.2.0-key; 422 no-connector-call), missing/ambiguous (S2 missing required key; None/absent `profile_version`), failure (S8 unpublished version; generic 500; 502/503/504 upstream) — all exercised.

## 3. Packaging rework disposition (explicit)

**CLOSED — verified, cannot silently recur.** The prior web-e2e failure (FileNotFoundError under non-editable install + jsonschema dev-only at request time) is fixed and triple-guarded:

1. **Runtime load path:** `contract.py::_load_bundled_schema` uses `importlib.resources.files("app._contract_schemas.v1")` — no `Path(__file__).parents[...]` walk, no `packages/` runtime reference. Verified by reading the module.
2. **Package data ships:** `pyproject.toml` adds `[tool.setuptools.package-data] "app._contract_schemas.v1" = ["*.schema.json"]`; both `__init__.py` files present so `include = ["app*"]` discovers the subpackage. The failing CI path is genuinely exercised: web-e2e job runs `pip install ./services/api` (ci.yml line 72, non-editable) and was green at 3a78fdd.
3. **jsonschema promoted to runtime:** verified in the `pyproject.toml` diff — moved from `[dev]` into `[project].dependencies` (`jsonschema>=4.21,<5`) with the rationale documented in-file.
4. **Byte-identity of the bundle:** `sync_contract_schemas.py --check` passed locally; additive `contracts-schema-bundle` CI job runs the identical command. Canonical authority (`packages/contracts/schemas/v1`) is not forked — the bundle is a regenerated build artifact, documented as such.
5. **Regression guard:** `test_contract_schema_packaging.py` loads all four schemas the installed-package way, asserts `SUPPORTED_CONTRACT_VERSIONS` populated at import, and adds a thorough AST-based static guard (forbids any non-docstring `packages/contracts` runtime string and any `.parents` attribute access in `contract.py`).

Rework commit `3a78fdd` diffstat is cleanly scoped to exactly this fix (bundle + sync script + packaging test + contract.py sourcing + pyproject + additive CI job + producer-report update).

## 4. G4 findings — integration & regression

| Check | Verdict | Evidence |
|---|---|---|
| CI green | **PASS** | 16/16 asserted on PR #16; api (211), typegen (6), and both drift checks independently reproduced locally by this reviewer (§1). |
| Contract compatibility (additive-only) | **PASS** | `git diff main...HEAD -- packages/contracts/schemas apps/web` is **empty** — the 1.2.0 schema shape is byte-unchanged vs main; all changes are new files, README prose, and version-constant/test updates. 1.0.0/1.1.0 consumers proven unaffected (S7). |
| No duplicate/contradictory implementations | **PASS** | Bundled schemas are drift-guarded synced artifacts with the authority model documented in three places (contract.py docstring, sync script, CI job comment). The handwritten `apps/web/src/lib` type persists intentionally until M2-T002 (packet input line, README, fixture `_consumed_by` all agree) — noted, not a defect here. |
| Scope discipline | **PASS** | Merge-base diffstat contains only `services/api/**`, `packages/contracts/**`, `.github/workflows/ci.yml`, and `project-control/reports/M2-T003-producer-report.md` — exactly the allowed paths. `apps/web` untouched. |
| ci.yml strictly additive | **PASS** | Diff inserts two new jobs (`contracts-typegen`, `contracts-schema-bundle`) between existing jobs; zero modified lines in existing jobs. Action pins (`checkout@34e11487… v4.3.1`, `setup-python@a26af69b… v5.6.0`) are byte-identical to every pre-existing job's pins. |
| Low-storage policy | **PASS** | All additions are KB-scale text (largest: 321-line bundled schema copy). Generators/checks are stdlib-only, no network, no Node toolchain; heavy execution routed to CI. This review itself wrote nothing outside agent memory. |
| jsonschema promotion (producer-flagged) | **VERIFIED** | In `[project].dependencies` in the pyproject diff (§3.3). |
| Web client pins 1.0.0\|1.1.0 | **Noted, not a defect** | apps/web is a forbidden path here; M2-T002 widens via the generated types. Carry-forward recorded. |

## 5. Defects and residuals

**Blocking defects: NONE.**

Non-blocking residuals (recorded for carry-forward; none warrants FAIL):

| ID | Severity | Finding |
|---|---|---|
| R1 | LOW | `_DEFAULT_ERROR_STATUS = 503` fallback (`properties.py:81, 335`) would emit an undocumented `(503, <new_state>)` pair if the connector ever adds a fifth `error_type`. Today the connector's set is closed ({`rate_limited`, `source_unavailable`, `timeout`, `schema_drift`} — verified in `pluto_soda.py`) and fully mapped, so the pair-matrix guarantee holds; but no test ties the connector's error-type set to `_ERROR_STATUS`/matrix membership. Any future connector error-type addition must extend the matrix and its bidirectional test. |
| R2 | LOW | Typegen emits `{}[]` for `zoning.mapped_features` (schema items `{"type":"object"}`); TS `{}` accepts any non-nullish value, looser than "object" (`Record<string, unknown>` would be faithful). Generator also has no oneOf/anyOf/allOf support — unused by current schemas, and the 100%-key-coverage test would surface silent omissions, but recheck if the contract grows combinators. |
| R3 | LOW | `VERSION_INTRODUCED` covers only the three top-level optional keys; nested versioned additions (per-fact `coverage_status`, district-provenance maps, `source_fact` lineage keys, `feasibility_relevant`) are deliberately outside the declared-vs-emitted check. Documented in `contract.py:91–96` and sufficient for the single real builder; revisit if a second profile producer appears. |
| R4 | NIT | M2-T004 carry-forward D2 (unused `result` param in `_status_dimensions`, `builder.py:419`) remains open — this task's builder edit was version-constant-only, so minimal-diff discipline plausibly excuses it; drop at the next substantive builder edit. |
| O-1 | OBSERVATION | Reviewer probe: an unknown extra top-level key passes backend validation because the canonical root schema is additive-open (no root `additionalProperties: false`) — settled M2-T004/G1 schema design enabling additive evolution, not an M2-T003 defect. "Invalid 200 impossible" means schema-invalid, not unknown-key-free. |
| O-2 | OBSERVATION | S4 fixture consumption level clarified (§2/S4): client fetch-stub, not connector seam. M2-T002 must wire it accordingly; the fixture's `_consumed_by` already instructs this. |

## 6. Verdict rationale

Every acceptance scenario in my charge (S1–S8, S10) is implemented, tested, and independently reproduced or code-verified; the §167 deferral is resolved exactly as contracted (decision recorded, implemented consistently, stale declaration made structurally impossible); the packaging rework is closed with three independent guards; the integration surface is additive, in-scope, and regression-clean. All residuals are LOW/nit and carried forward with named enforcement points.

Key file paths:
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\services\api\app\profile\contract.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\services\api\app\api\v1\properties.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\services\api\tests\api\test_property_contract.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\services\api\tests\api\test_contract_schema_packaging.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\services\api\scripts\sync_contract_schemas.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\packages\contracts\scripts\generate_ts_types.py`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\packages\contracts\fixtures\client_regression\http500_state_no_match.json`
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T003\packages\contracts\README.md`

G3: PASS
G4: PASS
