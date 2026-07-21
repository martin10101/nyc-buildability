# Gate Report

- Gate ID: G3 (code review)
- Task ID: M2-T012 — Profile integration of wave connectors + spatial results (single contract 1.4.0 update)
- Reviewer: code-reviewer (independent; not the producer)
- Producer: orchestrator (lead-only, owner directive 2026-07-21)
- Result: **PASS**
- Clean environment/worktree used: Yes. `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T012-profile`; `git rev-parse HEAD` == `82b92e1be3866d42d9dd59189f3b31a10b7dd344` (branch `task/M2-T012-profile`); `git status --porcelain` empty. Diff reviewed = `ac7cc3e6…82b92e1b` (25 files, +2017/−179).

## Acceptance criteria reviewed
PI-S1 primary integration; PI-S2 uncertainty preservation; PI-S3 fourth-stream geometric conflict + readiness gating; PI-S4 back-compat + misdeclare-reject; PI-S5 M2-T010 derivation/drift; PI-S6 carried LOW-defect fixes (scope-limited); PI-S7 missing-data typed degradation; PI-S8 regression. Additive-only constraint, uncertainty-never-collapsed constraint, and connector-touch scope discipline were treated as the primary review axes.

## Steps independently executed
All run offline at the frozen SHA:
- `python -m pytest tests/profile/test_wave_integration.py tests/connectors/test_m2_t012_carried_defects.py -q` → **23 passed** (2.04s).
- `python -m pytest tests/profile tests/api/test_property_contract.py tests/api/test_properties_v1.py tests/api/test_contract_schema_packaging.py tests/connectors/test_zoning_features_arcgis.py tests/connectors/test_ztldb_soda.py tests/connectors/test_mappluto_geometry_arcgis.py -q` → **362 passed** (10.49s).
- `python -m pytest packages/contracts/scripts/tests -q` → **14 passed**.
- `python packages/contracts/scripts/generate_ts_types.py --check` → generated TS up to date + client version block matches schema enum.
- `python services/api/scripts/sync_contract_schemas.py --check` → runtime bundle byte-identical to canonical.
- `python .github/scripts/validate_contracts.py` → 6 schemas, **0 failures** (incl. the advanced rejected exemplar).
- `python -m ruff check` on all 9 changed backend/test modules → **All checks passed**.
- `sha256sum` on canonical vs bundled `property_profile.schema.json` → identical (`1aa83109…88b3`).

This independently reproduces the flagged risk "1.4.0 is the FIRST post-tooling contract publication — verify the derivation chain end-to-end": schema → byte-identical bundle → live `SUPPORTED_CONTRACT_VERSIONS` → generated TS → web client block, all green.

## Expected versus actual
- PLUTO-only build declares 1.4.0 and emits no 1.4.0 key — confirmed (test + code: `build_wave_sections` returns `({}, [])`, `profile.update({})`/`extend([])` no-ops).
- Wave payload misdeclaring 1.3.0 rejected with `reason="declared_version_below_emitted_keys"` — confirmed for all three keys (parametrized red path).
- Uncertainty preserved: `spatial_intersection` copies the engine record minus `coverage_audits`; share ranges/classes pass through verbatim; no `assigned_district`; the only "Verified" token is the disclaiming `coverage_note` — confirmed.
- Fourth stream: `geometric_zoning_observations` emits a `zonedist1` value ONLY for `single_district_confident`, else `[]`; disagreement becomes an `unresolved` conflict through the EXISTING shape and gates `analysis_readiness` to `blocked_data_conflict` — confirmed.
- Provenance refs resolve with no dangling; `provenance_refs` always ≥ `[wave:spatial-intersection]` (self-referencing), verified for the spatial-only path too.

## Evidence paths
- New module: `services/api/app/profile/wave_integration.py`
- Builder: `services/api/app/profile/builder.py` (params + version bump + `_assert_provenance_integrity` extension L512–L551; wave fold-in L732–L753)
- Contract: `services/api/app/profile/contract.py` (L104–L116 `VERSION_INTRODUCED`)
- Fourth stream: `services/api/app/profile/zoning_crosscheck.py` (L76, L155–L206; purely additive)
- Connector defect fixes: `connectors/zoning_features_arcgis.py` L530–L549; `connectors/mappluto_geometry_arcgis.py` L1380–L1397 (top-level SR), L1961/1976–1978/1998–2042/2085–2093 (opt-in TTL cache); `connectors/ztldb_soda.py` L700–L710
- Tests: `services/api/tests/profile/test_wave_integration.py`, `services/api/tests/connectors/test_m2_t012_carried_defects.py`
- Derived artifacts: `packages/contracts/schemas/v1/property_profile.schema.json`, `services/api/app/_contract_schemas/v1/property_profile.schema.json`, `packages/contracts/generated/property_profile.ts`, `apps/web/src/lib/contract.ts`, `packages/contracts/fixtures/invalid/property_profile/contract_version_unknown.json`

## Human-style walkthrough findings
Not a UI task (rendering is a forbidden path, deferred to a separate frontend task). Contract/back-end walkthrough exercised via the runnable checks above.

## Regression/security/provenance findings
- **Scope discipline holds.** Connector *code* touches are limited to exactly the four enumerated carried defects (out_fields object-id footgun, top-level metadata `spatialReference`, opt-in `metadata_cache_ttl_seconds`, `check_columns_for_drift` string-`fieldName` filter). No `services/api/app/resilience/**` change; no `apps/web/src/components/**`; no `project-control/**` beyond the producer report; no `.claude/**`; no contract version beyond 1.4.0. The remaining PI-S6 items (drift-signal assertions, count==cap page test, test rename/dead-code removal, SOCRATA token hermeticity) are test-only.
- **Connector fixes correct + non-regressive.** Top-level SR guarded by `is not None` (asserts only when present, mirrors extent check); out_fields check lives only in the explicit-list branch (default `'*'` unaffected) and runs after the unknown-field check; `check_columns_for_drift` now filters to `isinstance(fieldName, str)` so `sorted()` can never mix `None`+`str`; TTL cache is default-OFF (`None`) and fetched inside the existing `try/except` so a metadata failure routes through the same breaker/LKG — the OFF path is byte-unchanged (proven by `test_..._off_by_default_refetches_metadata`, 4 upstream calls). `now=time.monotonic` (float) makes the TTL arithmetic correct.
- **Provenance integrity.** New `source_fact` records satisfy every required field; object-valued `original_value`/`normalized_value` are explicitly "Any JSON type"; `effective_date: null`, `confidence: 1.0`, and both platform enums (`"none"`) are valid; `confidence` is never mapped to a coverage label; `coverage_status` only ever emits members of the 6-value enum and never `verified`. IDs are collision-free (`wave:` prefix, per-layer dedup). Inputs consumed read-only; no connector/shapely import coupling in `wave_integration.py`.
- **Tests** are deterministic and offline (fixture/`FakeTransport` seams, fixed clock, seeded `Random`), well-labeled per scenario/defect, and actually exercise the load-bearing claims (esp. PI-S2 non-collapse, PI-S3 uncertain-no-emit across all five classes, PI-S4 misdeclare-reject, PI-S5 per-key red path).

## Defects
None (no blocking or non-blocking defects).

## Required rework
None required for this gate. Three non-blocking observations recorded for the orchestrator/backlog (no action required to pass G3):
1. `wave_integration._spatial_intersection_section` backfills `bbl`/`lot_overall_class`/`professional_review_required` via `setdefault` but not the required `coverage_note`. This is acceptable and arguably preferable — fabricating the honest disclaimer would be inventing a value; a record lacking it is caught by `validate_profile` before send (typed 500, never an invalid 200), and the real M2-T013 engine always emits it. Note only.
2. Wave `source_fact` records omit the OPTIONAL M2-T004 lineage keys (`fact_key`, `observation_id`, `value_digest`, `response_digest`) that PLUTO facts carry. Schema-valid (all optional); a possible future provenance-completeness enhancement.
3. Two follow-ups the producer already disclosed as out of file scope: extending `.github/scripts/validate_contracts.py` referential-integrity to the three new fixture sites (a `.github/`-scoped task), and live multi-connector endpoint orchestration (needs credentials). Backend `_assert_provenance_integrity` + unit tests cover the new sites in the interim.

## Reviewer conclusion
**PASS.** The change is a correct, additive-only, uncertainty-preserving contract 1.4.0 integration. The three new sections carry full, resolvable provenance; the fourth geometric evidence stream flows through the existing conflict shape and readiness machinery without a new mechanism; the M2-T010 derivation chain is byte-consistent end-to-end; back-compat and fail-closed behavior are preserved; and the carried connector fixes are correct, individually disclosed, and strictly limited to the enumerated defects. Independent reruns (23 new + 362 impacted + 14 typegen tests, ruff, typegen/bundle/contract-validation `--check`) are all green at the frozen SHA. No corrections are blocking.
