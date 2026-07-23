_Verbatim independent data-contract-verifier return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G1 Gate Report — M5-T001 (Scenario Foundation contract)

**Gate:** G1 (source & data-contract verification)
**Task:** M5-T001 — Deterministic coverage-aware scenario foundation
**Reviewed SHA:** `e994147` (`e9941471a7d930a499df047537581a648347f498`) on `task/M5-T001-scenario-foundation` (PR #86)
**Base:** `main` @ `0a61b7d`
**Reviewer role:** independent, read-only (ADR-005). No writes, no `project_control.py`, no git/gh writes.
**Verdict: PASS** (with 2 non-blocking hardening notes)

## SHA / worktree equivalence
- `git rev-parse HEAD` → `e9941471a7d930a499df047537581a648347f498` (exact match to frozen SHA).
- `git diff e994147 --stat` → empty. Worktree is byte-identical to the reviewed SHA.

## Scope-1 — narrowing pattern & canonical contracts untouched — PASS
- `git diff 0a61b7d e994147 -- packages/contracts/schemas/v1/coverage_status.schema.json packages/contracts/schemas/v1/property_profile.schema.json packages/contracts/schemas/v1/rule_evaluation.schema.json` → **EMPTY**. All three canonical contracts are byte-unchanged.
- `scenario.schema.json` `$defs/coverage_status_draft` uses the identical `allOf` + subset-enum pattern as `rule_evaluation.schema.json`: `{ "$ref": "coverage_status.schema.json" }` intersected with `enum: [conditional, professional_review_required, data_conflict, unsupported, not_applicable]`.
- Canonical `coverage_status.schema.json` enum = those 5 **plus** `verified`. The subset removes **exactly** `verified`; `coverage_status.schema.json` remains the single source of the vocabulary (never redefined inline). `verified` is structurally impossible on a scenario. Confirmed at runtime: the invalid fixture with `coverage_status: verified` is rejected (below), and generated TS models it as an intersection type excluding `verified` (`DraftCoverageStatus = CoverageStatus & ("conditional" | ... )`).

## Scope-2 — units, labels, provenance-required, vocabularies — PASS
- Draft cap field `draft_zoning_floor_area_cap_sq_ft`: `anyOf` `{number, exclusiveMinimum: 0}` or `null`. Unit encoded in the field name; `constraints[].unit` carries `"square_feet"` on the value-bearing rows. Strictly positive when present; null on every non-preliminary/fail-closed outcome (fixtures confirm).
- `cap_label` is mandatory (required), present only on preliminary, and its text explicitly states DRAFT residential zoning-floor-area cap under ZR 23-21 and **NOT** gross/net/sellable/feasible/envelope. Contract description reinforces this repeatedly.
- Provenance required on outputs: `cap_provenance` is a required top-level field and is non-null whenever a cap is surfaced (rule_id/version/status + `output_name` = `max_residential_floor_area_sq_ft` + `citations` each carrying source-snapshot `provenance`). `citation` requires `snapshot_id/section/quote/provenance`.
- Constraint-completeness vocabulary `known/draft/missing/conflicting/unsupported/professional_review_required` present verbatim in `constraint.state` enum — faithful to proposal §4.
- PRD §12 data-completeness `complete/missing_noncritical/missing_critical` referenced via `coverage_status.schema.json#/$defs/data_completeness` at both scenario level and per-constraint (never redefined).
- Coverage matrix (§7) and integrity-check (verification-only, fail-closed) modeled as typed `$defs`; fixtures carry all 11 matrix rows including the two `out_of_scope` gross-to-net/tower rows.

## Scope-3 — bundle byte-identity, typegen, validation — PASS (commands + outputs)
- `git diff --no-index packages/contracts/schemas/v1/scenario.schema.json services/api/app/_contract_schemas/v1/scenario.schema.json` → empty, EXIT 0. **Runtime bundle byte-identical to canonical source.**
- `python .github/scripts/validate_contracts.py` → EXIT 0. "Checked 8 schema file(s); 0 failure(s)." All 8 schemas OK; every scenario fixture validated/rejected as intended.
- `python packages/contracts/scripts/generate_ts_types.py --check` → EXIT 0. "generated scenario TypeScript types are up to date"; rule_evaluation + property_profile generation still up to date (no collateral drift).
- `python services/api/scripts/sync_contract_schemas.py --check` → EXIT 0. "runtime-bundled contract schemas are byte-identical to the canonical source."
- `python -m pytest services/api/tests/scenario/test_scenario_contract.py packages/contracts/scripts/tests/test_generate_scenario_ts.py -q` → **28 passed**.

## Scope-4 — fixtures validate/reject for stated defects — PASS
Per-fixture summary (kind / coverage / cap):
- valid `preliminary_r5_cap` — preliminary / conditional / 15000 (label present)
- valid `no_scenario_conflict` — no_scenario / data_conflict / null (label null)
- valid `no_scenario_professional_review` — no_scenario / professional_review_required / null
- valid `unsupported_family` — unsupported / unsupported / null
- invalid `coverage_status_verified` — rejected: `$.coverage_status: value 'verified' is not one of the allowed enum values [...]`. This fixture is byte-identical to the valid preliminary fixture except line 4 (`verified` vs `conditional`) and the added `_expected_failure` annotation — it fails **only** for its stated defect.
- invalid `embedded_property_profile` — rejected: `$: additional properties not allowed: ['property_profile']`. `additionalProperties:false` correctly rejects the embedded profile (identity is by-reference only via `evaluated_input`).
- invalid `missing_scenario_kind` — rejected: `$: missing required property 'scenario_kind'`.
- The `_expected_failure` optional key is whitelisted under `additionalProperties:false` (same convention as rule_evaluation), so invalid fixtures fail only for their intended defect and valid fixtures (which omit it) stay clean.

## Scope-5 — provenance discipline — PASS
The single surfaced material value (`draft_zoning_floor_area_cap_sq_ft`) traces verbatim to `cap_provenance` (rule_id/version/status + ZR 23-21 citation with full source-snapshot provenance: request_url, content_digest, extraction_status, last_amended). `lot_area` traces to profile field + `provenance_refs` + resolved dataset record. Identity is carried by reference (`bbl` + profile/rule_evaluation contract versions + `input_fingerprint`), never by embedding the profile — consistent with permanent principle 2 and PRD §9/§19.

## Non-blocking notes (hardening; not required for PASS)
1. **`constraint.provenance` permissiveness.** The schema types `provenance` as `["object","null"]` with prose "null when the constraint is a recorded gap with no source." In `preliminary_r5_cap.json` the `zoning_district` constraint has `state: "known"` but `provenance: null`. It is not a gap, so `null` is looser than the prose. The district remains traceable by reference through the consumed rule_evaluation's `input_provenance.zoning_district`, so this is not a provenance failure — but a future revision could either require `provenance` non-null when `state ∈ {known, draft}` or carry the district's `provenance_refs` as `lot_area` does.
2. **`constraint.provenance` / `citation.provenance` are open objects** (`type: object`, no inner shape). Acceptable for a foundation contract that propagates provenance verbatim from heterogeneous sources; a later version could narrow to the source_fact resolved shape once stable.

## Confirmation statement
Canonical contracts (`coverage_status`, `property_profile`, `rule_evaluation`) are byte-unchanged vs base. The new `scenario.schema.json` narrows `coverage_status` to exclude exactly `verified` via the same `allOf`+subset pattern rule_evaluation uses; a scenario can never be `verified` (enforced by schema, generated TS type, and a rejecting fixture). Runtime bundle and generated TS are in sync; all validation/typegen/sync/test checks pass.

**Verdict: PASS.** No blocking corrections. The two notes above are non-blocking hardening suggestions and do not gate acceptance.
