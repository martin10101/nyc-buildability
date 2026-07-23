# G1 (Source & Data-Contract) Gate Report — M4-T005 `rule_evaluation` v1.0.0

**Task:** M4-T005 — new canonical `rule_evaluation @ 1.0.0` contract for the deterministic rules-evaluator output.
**Reviewed SHA (frozen):** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (PR #84)
**Reviewer:** data-contract-verifier (read-only, ADR-005)
**Date:** 2026-07-22
**Verdict:** **PASS** — no required corrections.

## Setup / provenance of the reviewed tree
The mandated `git reset --hard <frozen>` is blocked by the read-only guard, so I reviewed the frozen content directly:
- The isolated worktree `.claude/worktrees/M4-T005-rule-eval` is at HEAD `f1e6772`, a descendant of the frozen SHA. `git merge-base --is-ancestor` confirms frozen is an ancestor of HEAD; `git diff --stat 84b50a7 f1e6772` shows the only delta is three project-control bookkeeping files (`M4-T005-producer-report.md`, `state.json`, `M4-T005.json`) — **zero** diff for every contract/schema/serializer/fixture path.
- `git diff --stat 84b50a7 -- packages/contracts services/api/app/rules services/api/app/_contract_schemas` is empty in the worktree, so the on-disk worktree content used to run the tests is byte-for-byte the frozen tree for all files under review.
- All file-content reads used explicit `git show 84b50a7:<path>`, independent of any working tree.

## Per-item findings

### Item 1 — Canonical reuse, no competing definitions — PASS
`rule_evaluation.schema.json`:
- `$defs/coverage_status_draft` = `allOf: [ {"$ref":"coverage_status.schema.json"}, {"enum":[5 values]} ]` — the vocabulary is **referenced**, never re-declared. Every coverage site (`coverage_status`, `family_coverage.coverage_status`, `evaluation_trace.coverage_status`) `$ref`s `#/$defs/coverage_status_draft`.
- `data_completeness` → `coverage_status.schema.json#/$defs/data_completeness`; `bbl` → `common.schema.json#/$defs/bbl`; `non_empty_string`/`digest_sha256` → `common`. No canonical enum/type is re-declared inline.
- Test `test_schema_refs_canonical_coverage_status_never_redefines_it` PASSED.

### Item 2 — `verified` excluded; disclaimer + review flag; spatial uncertainty preserved — PASS
- Canonical `coverage_status` enum = 6 values incl. `verified`; the draft subset enum = exactly those 6 minus `verified` (`conditional, professional_review_required, data_conflict, unsupported, not_applicable`). Empirically enforced: `validate_contracts.py` rejects `coverage_status_verified.json`. Tests `test_verified_is_not_an_allowed_coverage_status`, `test_valid_fixture_never_verified[*]` PASSED.
- Doc carries required `not_verified_disclaimer` (`common.non_empty_string`) and `professional_review_required` (boolean); grounded in `integration.NOT_VERIFIED_DISCLAIMER`.
- Spatial uncertainty preserved as structured ranges: `spatial_uncertainty.base_district_candidates[]` keeps `share_min/share_point/share_max`, `pair_class`, `minor_portion`, `review_reasons`, `crosscheck` — never collapsed. Test `test_as8_split_lot_preserves_share_ranges` and fixture PASSED.

### Item 3 — Input by reference, no embedded profile; deterministic fingerprint — PASS
- `evaluated_input` (`additionalProperties:false`, all four required) = `{bbl, profile_contract_version, input_fingerprint(digest_sha256), input_provenance}`. Root is `additionalProperties:false`.
- Invalid fixture `embedded_property_profile.json` is rejected: `$: additional properties not allowed: ['property_profile']`. Tests PASSED.
- Fingerprint determinism over the **evaluator input, not the whole profile**: `response.py::compute_input_fingerprint` digests only `{bbl, zoning_district, lot_area_sq_ft, lot_area_source, as_of_date, spatial_context}` via canonical JSON → `sha256:<64hex>`. Tests PASSED.

### Item 4 — Fidelity to `PropertyRuleEvaluation.export()` — PASS
- `as_dict()` emits exactly 20 keys; `serialize_rule_evaluation` moves `bbl`+`input_provenance` into `evaluated_input` and adds `contract_version`+`evaluated_input`, producing a root whose key set **equals the schema's 20-item `required`** list exactly.
- Types/units/provenance match: `lot_area_sq_ft` positive-or-null; the 6 `FAILSAFE_*` constants match the schema `fail_safe_reason` enum verbatim; `coverage_source`, `rule_lifecycle_statuses`/`rule_status` enums match. Fixtures grounded in real `evaluate_property(...).export()` output (no fabricated FAR numbers; ZR 23-21 draft rule, coverage tops at `conditional`).
- Real round-trips validate: AS-3/AS-5/AS-6/AS-7 tests PASSED (57/57 in the rule-eval contract+API suite).

### Item 5 — Versioning + drift guards — PASS (all commands run at frozen content)
- `contract_version` is a **closed** enum `["1.0.0"]`.
- `property_profile` stays **1.4.0 byte-identical** (last modified by M2-T012 `82b92e1`, untouched by any M4-T005 commit).
- Runtime bundle byte-identical to canonical (identical git blob hashes: `rule_evaluation` = `9e99b908` in both locations; same for common/coverage_status/source_fact).
- Three CI drift checks green: `generate_ts_types.py --check` exit 0; `sync_contract_schemas.py --check` exit 0; `validate_contracts.py` → `Checked 7 schema file(s); 0 failure(s)`. `pytest services/api/tests/contracts -q` → 28 passed; rule-eval contract+API suite → 57 passed.

### Deployability additions (sanity check) — PASS, no competing schema
- `services/api/app/rules/schemas/v1/{evaluation_trace,rule_definition}.schema.json` are **engine-internal** schemas (M4-T001/T003), not `packages/contracts` canonical contracts. The `rule_evaluation` contract deliberately narrows the internal export via `coverage_status_draft`. Canonical vocabulary lives only in `coverage_status.schema.json`.
- `app/_zr_snapshots/v1/zr-23-21.snapshot.json` is honest source-snapshot data (`raw_html_verified:false`, needs_review banner), not a contract definition.

## Non-blocking observations (not defects)
1. Phase-1 fixture `input_fingerprint` values are illustrative sha256 digests (documented as such); the deterministic computation is `response.py::compute_input_fingerprint`, separately proven deterministic.
2. The engine-internal `evaluation_trace.schema.json` inline-redefines the coverage enum, but it is an internal export schema outside `packages/contracts` and outside this contract's scope. No action required.

## Verdict: **PASS** — no required corrections.
