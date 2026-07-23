_Verbatim independent qa-engineer return (transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# G4 GATE REPORT — M5-T001 (Integration & Regression)

**Reviewed SHA:** `e994147` on branch `task/M5-T001-scenario-foundation` (PR #86)
**Base:** `main` @ `0a61b7d`
**Reviewer:** qa-engineer (independent, read-only)
**Gate:** G4 — integration & regression
**Verdict: PASS**

## Method / equivalence note
`git reset --hard` is a reviewer-blocked git write, so per the packet's fallback I materialized the frozen tree via pure blob extraction (`git show e994147:<path> > <path>`) into the assigned worktree (which sat at base `0a61b7d`) and confirmed **byte-identity**: all 27 changed files verified `MATCH=27 MISMATCH=0` against `git show e994147:<path>`. All commands below ran against that byte-identical materialization.

## 1. Independently executed commands + actual outputs

From `services/api` (Python 3.11.9, ruff 0.9.9, pytest 8.4.2, jsonschema 4.26.0):

| Command | Result |
|---|---|
| `python -m ruff check .` | `All checks passed!` (exit 0) |
| `python -m pytest tests/scenario -q` | **54 passed** in 0.63s |
| `python -m pytest -q` (FULL API / AS-12) | **881 passed** in 9.42s, 0 failed |

From repo root:

| Command | Result |
|---|---|
| `python .github/scripts/validate_contracts.py` | `Checked 8 schema file(s); 0 failure(s).` (exit 0) — scenario valid/invalid fixtures validate/reject correctly |
| `python packages/contracts/scripts/generate_ts_types.py --check` | `OK` for property_profile, rule_evaluation, **and scenario** TS types + client version block (exit 0) |
| `python services/api/scripts/sync_contract_schemas.py --check` | `OK: runtime-bundled contract schemas are byte-identical to the canonical source.` (exit 0) |
| `python -m pytest packages/contracts/scripts/tests -q` | **24 passed** in 0.34s |

All green / byte-identical.

## 2. AS-1..AS-12 → proving test mapping (all genuine)

| AS | Proving test (file:location) | Assessment |
|---|---|---|
| AS-1 surfaced==trace (not recomputed) | `tests/scenario/test_scenario_foundation.py::test_as1_confident_r5_cap_surfaces_canonical_trace_value` + `::test_as1_value_comes_from_trace_not_recompute_even_without_far` | **Strong.** Second test deletes `max_residential_far` so `far*lot_area` recompute is impossible, yet the cap is still surfaced from the trace — proves the value is READ, never derived. |
| AS-2 unsupported stub | `::test_as2_unsupported_family_is_visible_stub_no_cap` (parametrized unsupported + not_applicable) | Strong: visible stub, no cap, reason present. |
| AS-3 missing constraint | `::test_as3_missing_required_input_names_the_gap_and_infers_nothing` | Strong: no_scenario, gap named, every envelope family still MISSING/null. |
| AS-4 spatial uncertainty | `::test_as4_spatial_uncertainty_blocks_and_preserves_ranges` | Adequate: split_lot; share ranges preserved (`share_min != share_max`), not collapsed. (Non-blocking: only split_lot fixture; sliver/invalid-geometry share the same code path but aren't separately fixtured.) |
| AS-5 rule conflict | `::test_as5_rule_conflict_blocks_and_surfaces_competing_rules` | Strong: no_scenario, data_conflict, both competing rule_ids surfaced. |
| AS-6 malformed/non-finite | `::test_as6_malformed_inputs_fail_closed_no_crash` (8 params: NaN/±inf/huge-int/wrong-type/non-positive/zero) | Strong: fail-closed, strict-JSON (`json.dumps(allow_nan=False)`), all surfaced numbers finite, schema-valid. |
| AS-7 integrity fails closed, canonical never replaced | `::test_as7_integrity_disagreement_fails_closed_and_surfaces_no_number` | **Strong.** Recompute 30000 ≠ canonical 15000 → data_conflict, `integrity_check.performed=True/agreed=False`, cap null, and asserts **neither** 15000 nor 30000 appears anywhere in output. |
| AS-8 determinism / byte-identical | `::test_as8_identical_input_yields_byte_identical_output` (4 kinds) | Strong: `json.dumps(first)==json.dumps(second)` (order-preserving). Satisfies item 4. |
| AS-9 never verified | `::test_as9_no_scenario_is_ever_verified` (7 factories) + contract-layer `test_scenario_contract.py::test_verified_is_not_an_allowed_coverage_status` + schema `coverage_status_draft` allOf-subset | Strong. Disclaimer text containing the word "Verified" is not a `coverage_status` value, so no false path. |
| AS-10 provenance & completeness | `::test_as10_provenance_and_completeness_preserved` | Strong: cap rule_id/version/status/citations verbatim; lot-area profile_field + resolved source_id/dataset_version. |
| AS-11 explicit-assumption-only variation | `::test_as11_variation_only_via_explicit_assumption_no_hidden_factor` | **Strong.** Baseline cap == variant cap == raw trace cap with a 0.8 utilization_factor assumption present; documents identical except the `assumptions` array — proves no hidden utilization/efficiency/optimization factor. |
| AS-12 regression | `::test_as12_builder_never_mutates_its_inputs` + `::test_as12_degenerate_empty_inputs_fail_closed_not_crash` + full suite (881 passed) + git-diff scope | Strong. |

## 3. Regression isolation (`git diff --name-only e994147 0a61b7d`)
Zero modification to forbidden paths — grep for `services/api/app/{profile,spatial,rules,api}/`, `apps/web/`, and canonical contracts (`property_profile`/`rule_evaluation`/`coverage_status.schema.json`) returned **NONE — clean isolation**. Every services/api change is an **add (A)**; no existing test file was modified (so the 827 pre-existing API tests are structurally unchanged and all pass within the 881). The only non-additive change is `packages/contracts/scripts/generate_ts_types.py` — a purely additive third TS-generation artifact (new `SCENARIO_*` maps/functions, independent codepath) that leaves property_profile.ts and rule_evaluation.ts byte-identical (confirmed by `--check`). This is within the packet's `allowed_paths` ("its generated typegen/runtime-bundle/fixtures"). `state.json` is a ledger touch (orchestrator scope).

## 4. Determinism
Proven by AS-8 (`test_as8_...`) asserting byte-identical serialized output for identical input across 4 scenario kinds; builder emits constraints/matrix/reasons in fixed order and normalizes assumptions by sorted key.

## Blocking gaps
**None.**

## Non-blocking suggestions (for future hardening, do not block acceptance)
- AS-4: add a sliver / invalid-geometry / `inconsistent_confident_geometry` fixture variant (currently only `split_lot`; the other fail-safe reasons share the code path but aren't separately fixtured).
- AS-5/6: the `bbl_mismatch` conflict trigger and a wrong-type cap value (only `lot_area` wrong-type is fixtured) are exercised by code but not independently asserted.

## Note to orchestrator
This G4 verdict certifies integration/regression at SHA `e994147` only. Per the packet, **final acceptance remains gated on genuine G6 legal approval of M4-T001** and the other required gates (G1 contract, G3 code, G5 security); this G4 does not speak to those.

**Requested status:** gate PASS — return to orchestrator to record via `project_control.py gate`.
