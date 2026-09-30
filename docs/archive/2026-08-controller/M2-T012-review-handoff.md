# M2-T012 reviewer-report transport bundle

> **TEMPORARY TRANSPORT BUNDLE — NOT authoritative project state.** The authoritative
> record is the project-control ledger + git history + committed reports. These three
> reviewer reports are captured here only because their agent task-output transcripts were
> empty (0 bytes); at acceptance they should be persisted verbatim into
> project-control/reports/ (M2-T012-G1-data-contract-review.md / -G3-code-review.md /
> -G5-security-review.md) by the orchestrator. This file lives OUTSIDE every git repo/worktree
> and changes no repository, ledger, gate, checkpoint, branch, or GitHub state.

- Frozen reviewed SHA: `82b92e1be3866d42d9dd59189f3b31a10b7dd344`
- Branch / worktree: `task/M2-T012-profile` / `.claude/worktrees/M2-T012-profile`
- CI at this SHA: run 29855572873 = SUCCESS (all 10 jobs; web-e2e flake cleared on same-SHA rerun)
- All three gate verdicts: **PASS** (no blocking defects)

| Gate | Reviewer | task-output ID | Verdict | report-content SHA-256 |
|---|---|---|---|---|
| G1 | data-contract-verifier | af6b60ac23e18c390 | PASS | 113dee28f24bf87ab14fb87b839b4c9f14a0401cd177c894696a5efa7df813ac |
| G3 | code-reviewer | ab81212f31a16cad4 | PASS | 9f9a195f55b7a1438b29bfb657719c171c43501eeeeaa9a992c6eda6999628b6 |
| G5 | security-reviewer | a61b81b8113cbc67f | PASS | d22fcab352590d2c812f1a7c04a3758159dff713256245c894fe584bf07ebed4 |

The report-content SHA-256 above equals sha256sum of the exact verbatim bytes between the
BEGIN/END markers of each section below (transport HTML-entity decoding only; not summarized).

---

## Gate G1 — data-contract-verifier — VERDICT: PASS
- task-output ID: af6b60ac23e18c390
- report-content SHA-256: 113dee28f24bf87ab14fb87b839b4c9f14a0401cd177c894696a5efa7df813ac

<<<BEGIN VERBATIM G1 REPORT>>>
# Gate Report

- Gate ID: G1
- Task ID: M2-T012
- Reviewer: data-contract-verifier (independent; not the producer)
- Producer: orchestrator (lead-only, owner directive 2026-07-21)
- Result: **PASS**
- Clean environment/worktree used: Yes — worktree `.claude/worktrees/M2-T012-profile` at frozen SHA `82b92e1be3866d42d9dd59189f3b31a10b7dd344`; `git rev-parse HEAD` matches and `git status --porcelain` is empty (clean). Python 3.11.9, jsonschema 4.26.0.

## Acceptance criteria reviewed
PI-S1…PI-S8 from `project-control/tasks/M2-T012.json`, plus the six explicit G1 mandate items (derivation chain end-to-end; additive-only + back-compat; provenance & field mappings; uncertainty preservation; fourth geometric evidence stream; disclosure judgment). I did not rely on the producer's conclusions — I re-ran the check commands and the API suite, and I traced every field mapping to the real M2-T013 engine record shape.

## Steps independently executed
All run from the frozen worktree:

1. SHA/tree binding: `git rev-parse HEAD` → `82b92e1…`; `git status --porcelain` → empty.
2. Diff surface: `git diff ac7cc3e…82b92e1 --name-status` → 25 files, all inside `allowed_paths`; 2 new backend files, 2 new test files.
3. Byte-identity of schema copies: SHA256(canonical) == SHA256(bundled) == `1aa83109…f88b3`; plus `python services/api/scripts/sync_contract_schemas.py --check` → "byte-identical" (EXIT 0).
4. `python packages/contracts/scripts/generate_ts_types.py --check` → "generated TypeScript types are up to date" + "client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum" (EXIT 0).
5. `python .github/scripts/validate_contracts.py` → "Checked 6 schema file(s); 0 failure(s)" (EXIT 0); cross-checked by BOTH the stdlib mini-validator and jsonschema 4.26.0.
6. Live backend derivation: imported `app.profile.contract` and `app.profile.builder` → `SUPPORTED_CONTRACT_VERSIONS = ('1.0.0','1.1.0','1.2.0','1.3.0','1.4.0')` (read live from the bundled enum, not hard-coded); `PROFILE_CONTRACT_VERSION = '1.4.0'`; `VERSION_INTRODUCED` registers all three keys at `1.4.0`.
7. Targeted tests: `pytest tests/profile/test_wave_integration.py tests/connectors/test_m2_t012_carried_defects.py tests/api/test_property_contract.py -q` → 57 passed.
8. Full regression: `pytest -q` (services/api) → **590 passed** in 13.87s.
9. Source-of-truth tracing: read the real engine record `app/spatial/models.py` (`LotIntersectionRecord.as_dict`), `app/spatial/crosscheck.py` (`geometric_ordered_districts` producer), and `app/profile/zoning_crosscheck.py` (the reader), to confirm key names match on real (non-fixture) data.

## Expected versus actual
- Schema enum gains "1.4.0", three OPTIONAL top-level keys added — expected/actual match (`packages/contracts/schemas/v1/property_profile.schema.json:27`, and the three key blocks at lines ~347–495).
- Only allowlisted keywords used; `required ⊆ properties` for every new object — actual: new objects use only `description/type/properties/required/items/$ref`; all in `KNOWN_KEYWORDS` (`validate_contracts.py:81`); `lot_geometry.required=[outcome,provenance_ref]`, `spatial_intersection.required=[bbl,lot_overall_class,professional_review_required,coverage_note,provenance_refs]`, `zoning_features.layers.items.required=[layer,provenance_ref]` — all have sibling properties. House-rule enforcement verified at `validate_contracts.py:195-200`. `spatial_intersection.provenance_refs` reuses the PRE-EXISTING `$defs/provenance_ref_list` (schema line 498), not a new def.
- Bundled schema byte-identical; TS + client version block regenerate cleanly — all three `--check` commands green.
- Backend derives 1.4.0 live; builder declares 1.4.0 — confirmed live (step 6).
- Additive-only + back-compat — the ONLY `-` lines in the schema diff are the top-level description and the `contract_version` enum line, both of which merely append 1.4.0 documentation/value; no existing property removed or retyped. 1.0.0–1.3.0 fixtures validate (validate_contracts output + `test_pi_s4_pre_1_4_0_fixtures_still_validate`). Rejected exemplar `contract_version_unknown.json` advanced 1.4.0→1.5.0 and is still correctly rejected against the enum now containing 1.4.0.
- Provenance integrity — `_source_fact` (`wave_integration.py:81-111`) emits all 12 source_fact-required fields; `dataset_version` fallback is honest: `source_data_last_edited` → content `digest` → explicit `"unknown-no-source-version"` sentinel (`wave_integration.py:65-78`), never a fabricated version; `confidence=1.0` is fixed for deterministic official retrieval and is NEVER mapped to a coverage label (coverage derived independently in `_lot_geometry_coverage`, `wave_integration.py:186-207`). `build_property_profile` appends wave provenance BEFORE `_assert_provenance_integrity`, which was extended to all three new ref sites (`builder.py:527-548`).
- Uncertainty preservation — `spatial_intersection` carries `lot_overall_class`, `pairs[].pair_class`, share RANGES (`share_min<share_point<share_max`), and the permanent `coverage_note`; the engine-internal `coverage_audits` is EXCLUDED, and the strip is COMPLETE because `coverage_audits` is a top-level-only key of `as_dict()` (`models.py:192`). No definitive single-district assignment field exists; the only "Verified" token is the disclaiming note (`test_pi_s2_…` asserts `blob.count("Verified")==1` and `"assigned_district" not in blob`).
- Fourth geometric stream — `geometric_zoning_observations` (`zoning_crosscheck.py:155-207`) emits a `zonedist1` value ONLY when `lot_overall_class == "single_district_confident"` and returns `[]` for every other class; a disagreeing value becomes a `resolution='unresolved'` conflict through the EXISTING conflict shape and gates `analysis_readiness=blocked_data_conflict` (proven end-to-end with real PLUTO/ZTLDB fixtures in `test_pi_s3_…`). Reader keys (`geometric_ordered_districts`, `label`, `share_point`) match the real engine (`models.py:153`, `crosscheck.py:48,69`) — the stream fires on real data, not just fixtures.

## Evidence paths
- `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T012-profile\packages\contracts\schemas\v1\property_profile.schema.json`
- `…\services\api\app\_contract_schemas\v1\property_profile.schema.json` (byte-identical bundle)
- `…\services\api\app\profile\wave_integration.py` (new; mapping + provenance)
- `…\services\api\app\profile\builder.py` (1.4.0 declaration; provenance-integrity extension; additive params)
- `…\services\api\app\profile\contract.py` (live enum derivation; VERSION_INTRODUCED)
- `…\services\api\app\profile\zoning_crosscheck.py` (fourth geometric stream)
- `…\services\api\app\spatial\models.py`, `…\app\spatial\crosscheck.py` (real engine record shape — source-of-truth cross-check)
- `…\services\api\tests\profile\test_wave_integration.py`, `…\tests\connectors\test_m2_t012_carried_defects.py`
- `…\packages\contracts\generated\property_profile.ts`, `…\apps\web\src\lib\contract.ts`, web version-assertion tests under `…\apps\web\src\lib\__tests__\`
- CI run 29855572873 (SUCCESS at frozen SHA) — verified consistent with my local reruns.

## Human-style walkthrough findings
N/A for G1 (data-contract). A PLUTO-only build declares 1.4.0 and emits no 1.4.0 key (byte-unchanged path), and a wave build carrying any of the three keys but misdeclaring 1.3.0 is correctly rejected with `reason='declared_version_below_emitted_keys'` — both confirmed by tests I re-ran.

## Regression/security/provenance findings
- Regression: full API suite 590 passed; contracts / typegen / schema-bundle checks green — no regression.
- Provenance: every emitted section fact carries a `provenance_ref`/`provenance_refs` resolving to a schema-valid `source_fact` record; even a `spatial_intersection` supplied alone yields a non-empty `provenance_refs=[wave:spatial-intersection]` (no dangling ref). Nothing is labeled `verified`; `coverage_status` values emitted (`conditional`/`unsupported`/`not_applicable`/`professional_review_required`/`data_conflict`) are all valid and deterministic.
- Security: no network, no new dependency, inputs consumed read-only/duck-typed; no secrets.

## Defects
None blocking. Three non-blocking observations:

- OBS-1 (cosmetic): the `spatial_intersection` section passes through the engine's internal `provenance` metadata dict in addition to the added `provenance_refs`. The open schema permits it and the profile validates; mildly redundant, deliberate open-passthrough design. No action required.
- OBS-2 (cosmetic): `_spatial_intersection_section` (`wave_integration.py:313-318`) `setdefault`s `professional_review_required` to `False` when a record omits it. The real engine always emits this field (required dataclass field, `models.py:177`) and the schema requires it, so this only affects hand-built test dicts; a `False` default is marginally less fail-safe than `True`, but it cannot occur on real data. No action required.
- OBS-3 (tracked follow-up — the producer's disclosed gap): `.github/scripts/validate_contracts.py`'s `profile_provenance_invariant` is NOT extended to the three new fixture ref sites.

## Required rework
None. (Verdict is a clean PASS, not "PASS with required corrections.")

Recommended (non-blocking) follow-up for the orchestrator to track, not a condition of this gate: when the first fixture exercising `zoning_features`/`lot_geometry`/`spatial_intersection` is added under `packages/contracts/fixtures/`, extend `.github/scripts/validate_contracts.py:profile_provenance_invariant` to those sites in the same change (a `.github/`-scoped task).

## Reviewer conclusion
**PASS.** This first post-tooling publication holds up to end-to-end scrutiny. The single canonical schema is the source; it propagates byte-identically to the runtime bundle and cleanly to the generated TS + client version block; and the backend derives `1.4.0` LIVE from the bundled enum (no hard-coded version). The change is strictly additive — all 1.0.0–1.3.0 fixtures still validate, no existing key was changed or retyped, and the rejected exemplar correctly moved to an unpublished 1.5.0. Provenance is intact at every new site (all `source_fact` records schema-valid, honest `dataset_version`, `confidence=1.0` never used as a coverage label). Owner hard rules are honored: M2-T013 uncertainty is preserved (classes + share ranges + coverage_note), the engine-internal `coverage_audits` is completely excluded (top-level-only key), no field asserts a definitive single-district assignment, and nothing is "Verified." The fourth geometric evidence stream emits a value only for `single_district_confident` and routes disagreement through the existing unresolved-conflict shape that gates `analysis_readiness` — and it uses key names that match the real engine, so it works on live data, not merely fixtures.

On the disclosure (mandate item 6): the un-extended CI `profile_provenance_invariant` is **acceptable for G1 and not a blocking gap**, because (a) zero fixtures currently exercise the three new keys, so nothing is unenforced in the committed corpus today; (b) the backend `_assert_provenance_integrity` — the live-data authority per PRD s9/s19 and the schema's own text — enforces all three sites and I verified it first-hand; (c) builder-output unit tests enforce it; and (d) `.github/` is outside this task's `allowed_paths`, so extending it here would be scope creep. It should be tracked as the recommended follow-up above.
<<<END VERBATIM G1 REPORT>>>

---

## Gate G3 — code-reviewer — VERDICT: PASS
- task-output ID: ab81212f31a16cad4
- report-content SHA-256: 9f9a195f55b7a1438b29bfb657719c171c43501eeeeaa9a992c6eda6999628b6

<<<BEGIN VERBATIM G3 REPORT>>>
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
<<<END VERBATIM G3 REPORT>>>

---

## Gate G5 — security-reviewer — VERDICT: PASS
- task-output ID: a61b81b8113cbc67f
- report-content SHA-256: d22fcab352590d2c812f1a7c04a3758159dff713256245c894fe584bf07ebed4

<<<BEGIN VERBATIM G5 REPORT>>>
# Gate Report

- Gate ID: G5 (security/privacy)
- Task ID: M2-T012
- Reviewer: security-reviewer (independent; not the producer)
- Producer: (per project-control/reports/M2-T012-producer-report.md)
- Result: PASS
- Clean environment/worktree used: Yes — worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T012-profile`; `git rev-parse HEAD` = `82b92e1be3866d42d9dd59189f3b31a10b7dd344` (matches frozen submit SHA), branch `task/M2-T012-profile`, `git status --porcelain` empty (clean). Review bound to `git diff ac7cc3e6..82b92e1b`.

## Acceptance criteria reviewed
The five security/privacy mandate items for this contract/data-integration diff: (1) no secrets in new code/provenance; (2) connector defect fixes do not weaken security posture; (3) SOCRATA_APP_TOKEN test hermeticity without leak; (4) no injection / untrusted-input reaching logs or payloads unsanitized; (5) no new external calls, no new dependencies, no PII beyond public BBL. Plus the standing G5 posture checks: cross-tenant isolation, service-role secrecy, private storage, SSRF/injection, upload controls, prompt-injection, least privilege, log redaction.

## Steps independently executed
1. `git rev-parse HEAD`, `git status --porcelain`, `git rev-parse --abbrev-ref HEAD` — SHA/branch/clean-tree binding confirmed.
2. `git diff --stat ac7cc3e6..82b92e1b` and `git log --oneline` — 25 files, single commit, no dependency/lockfile files touched.
3. Full read of the new module `services/api/app/profile/wave_integration.py` (407 lines).
4. `git diff` of the three connectors (`zoning_features_arcgis.py`, `mappluto_geometry_arcgis.py`, `ztldb_soda.py`) plus surrounding-context reads of `build_query_url` and `MapPlutoLayerMetadata`.
5. `git diff` of `builder.py`, `contract.py`, the token test fixture, and full read of `zoning_crosscheck.py`.
6. Targeted greps over the diff: dependency/lockfile changes; network/logging/env/secret patterns in added app source; hard-coded secret literals across the whole diff; network egress in tests; token/auth/env usage in the ArcGIS connectors; logging in the two new profile modules.
7. Full read of the schema additions (`packages/contracts/schemas/v1/property_profile.schema.json`).

## Expected versus actual
- Expected: provenance records carry only non-sensitive descriptors. Actual: `_source_fact` (wave_integration.py:81-111) emits `provenance_id, source_id, original_field_name, original_value, normalized_value, retrieved_at, dataset_version, effective_date, bbl, confidence=1.0, user_confirmed_or_overridden="none", conflict_status="none"` — layer names, content digests, record counts, CRS, timestamps, library versions, and public BBL only. Match.
- Expected: `build_query_url` change tightens the allowlist. Actual: the new `if order_by_field not in out_fields:` gate (zoning_features_arcgis.py:~535-547) raises `DisallowedRequestError` *after* the pre-existing non-allowlisted-field rejection, and sanitizes via `_safe_field_name`; the `where`-clause allowlist (`_require_known_where`) and single-quote escaping (`build_attribute_where`) are untouched. Match (tightening).
- Expected: metadata cache adds no security surface. Actual: opt-in, default `None`/OFF (mappluto_geometry_arcgis.py:~1971, guard at `_acquire_metadata` `ttl is None or ttl <= 0`); caches a single global `MapPlutoLayerMetadata` (fields at :1247-1264 are correlation id, public keyless layer URL, timestamps, schema field names, CRS ids, counts, digest, drift strings — no auth/PII/tenant data); `threading.Lock` guarded; service documented keyless ("no token exists"). Match.
- Expected: token test fix improves hermeticity, no leak. Actual: `_hermetic_app_token` autouse fixture (`monkeypatch.delenv(APP_TOKEN_ENV_VAR, raising=False)`) clears ambient env; connector emits token only as `X-App-Token` header ("never logged", ztldb_soda.py:532-534) and logs only `bool(app_token)` as `token_configured` (:1176); no hard-coded token value. Match.

## Evidence paths
- `services/api/app/profile/wave_integration.py`
- `services/api/app/profile/zoning_crosscheck.py`
- `services/api/app/profile/builder.py`
- `services/api/app/profile/contract.py`
- `services/api/app/connectors/zoning_features_arcgis.py`
- `services/api/app/connectors/mappluto_geometry_arcgis.py`
- `services/api/app/connectors/ztldb_soda.py`
- `services/api/tests/connectors/test_ztldb_soda.py`
- `packages/contracts/schemas/v1/property_profile.schema.json`
- CI evidence (orchestrator-captured): run 29855572873 at 82b92e1 = SUCCESS (exact-production-install: pip-audit ZERO advisories on both locks + release-age gate + validate_profile smoke; separate secret-scan workflow = success).

## Human-style walkthrough findings
Not applicable — no UI surface in this diff (contract/data-integration only; no new endpoints, no auth/RLS/storage changes). Behavior-level review performed by tracing the wave-section builder path and the connector-fix code paths.

## Regression/security/provenance findings
- No secrets in code or provenance: CONFIRMED. `wave_integration.py` imports only `from typing import Any` (no network, no env, no logging); no token/secret/credential literal or reference anywhere in the added app source (single grep match was the doc-comment phrase "SODA-style release token" describing dataset versioning, not a credential). Diff-wide hard-coded-secret scan returned zero matches. `dataset_version` derives only from `source_data_last_edited` or content digest or a documented sentinel `"unknown-no-source-version"`.
- Connector fixes: all three are tightenings or robustness-only. `build_query_url` adds a required object-id-field check (does not loosen URL/where allowlisting; no injection introduced). `fetch_layer_metadata` adds a top-level `spatialReference` validation gate (raises `WrongCRSError`; `repr()`-sanitized detail). `check_columns_for_drift` guards against a `None` dict key causing `TypeError` in `sorted()` (no security surface).
- Injection / untrusted input: `GEOMETRIC_SOURCE_ID = "nyc-geometric-intersection"` is a static label (zoning_crosscheck.py:76). Neither new profile module (`wave_integration.py`, `zoning_crosscheck.py`) contains any `logging`/`print` — no log-leak path; official-derived values reaching `reproducibility.connector_notes` are `repr`-formatted (`!r`). No shell/SQL/eval/URL sink is introduced; the connectors' existing `repr`/`_safe_field_name` sanitization is not undone. Payload values are JSON-serialized (no payload-layer injection).
- Cross-tenant isolation: the only new shared state is the global metadata cache holding public citywide layer schema (identical for all tenants, no per-tenant/PII data), keyed by nothing (single entry) with a time-based TTL — no cross-tenant or stale-auth risk. No RLS/auth changes.
- Service-role secrecy / private storage / upload controls: no such code paths added or altered; ArcGIS services keyless, Socrata token redacted.
- SSRF: no user-controlled URL construction added; URLs built from allowlisted layer specs + connector-built bounded where clauses.
- Prompt-injection: no AI/LLM invocation in the diff (module docstring: "no AI, no legal interpretation"); deterministic mapping only.
- Least privilege: metadata cache is opt-in default-off; new builder params (`lot_geometry`, `zoning_features`, `spatial_intersection`) default `None` (backward compatible; PLUTO-only build byte-unchanged).
- Provenance integrity: `builder._assert_provenance_integrity` extended to the three 1.4.0 sites; every emitted `provenance_ref`/`provenance_refs` resolves to an emitted `source_fact` (fail-loud `RuntimeError` on dangling).
- Dependencies / egress: no dependency or lockfile file in the diff; no network imports in added source or tests. Consistent with the CI pip-audit/age-gate evidence.

## Defects
None (no critical/high/medium/low security defect).

## Required rework
None required.

Informational (non-blocking, defense-in-depth for a future task — not a defect in this diff): `_spatial_intersection_section` (wave_integration.py:296-298) forwards the engine record by exclusion (`record_dict.items()` minus `coverage_audits`) rather than by explicit allow-list, and the schema sections are "DELIBERATELY OPEN" by design. This is safe here because the server is the sole emitter of deterministic non-sensitive spatial facts and the sources are keyless. Recommendation: when the M2-T013 engine is wired to real input (out of this task's file scope), confirm the engine record's complete key set carries no internal-only/sensitive field, to keep the pass-through free of surprise fields. No evidence any such field exists today.

## Reviewer conclusion
The diff is a deterministic contract/data-integration change that adds no secrets, no dependencies, no network egress, no logging of sensitive values, and no new injection/SSRF/upload/prompt-injection surface. The three connector changes strictly tighten validation or add robustness; the opt-in metadata cache holds only public layer schema with no cross-tenant or stale-auth exposure; the token test fix improves hermeticity with correct redaction and no hard-coded secret. Provenance records and the new response sections carry only non-sensitive, provenance-stamped, official-derived data plus the public BBL. Static security properties independently verified from the frozen diff; dynamic scans (pip-audit dual-lock, release-age gate, secret-scan, validate_profile smoke) confirmed via orchestrator-captured CI run 29855572873 at the frozen SHA (SUCCESS).

**VERDICT: PASS** for G5 (security/privacy) at SHA `82b92e1be3866d42d9dd59189f3b31a10b7dd344`.
<<<END VERBATIM G5 REPORT>>>
