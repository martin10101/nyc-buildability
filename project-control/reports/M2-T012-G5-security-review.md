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
