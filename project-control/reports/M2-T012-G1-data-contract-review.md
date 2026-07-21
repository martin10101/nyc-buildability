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
