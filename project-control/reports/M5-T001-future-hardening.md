# M5-T001 — future-hardening notes (non-blocking)

Raised by the independent G1/G3/G4/G5 reviewers at frozen `e994147`. **None blocks acceptance** — all
gates PASS. Recorded for a future task, not as required corrections. They join the M5 backlog and are
mostly targeted at the **future M5 rule-evaluation→scenario endpoint** boundary.

## Security (G5, LOW — for the future endpoint task)
- **FH-M5T001-S1 (`build_scenario` does not self-validate):** strict-JSON / never-Verified enforcement
  lives in `validate_scenario_document`, which the builder does not call before returning. A NaN buried
  in a verbatim-copied provenance sub-object (not numeric-guarded by the builder) would only be caught at
  validation. Recommend the future endpoint always call `validate_scenario_document` before emit. Worst
  case today is a typed `ScenarioContractError`, never a wrong/Verified result.
- **FH-M5T001-S2 (recursion over verbatim-copied provenance):** `assert_scenario_not_verified` /
  `json.dumps` recurse over the assembled doc, which embeds attacker-adjacent nested sub-objects
  (`citation.provenance`, `rule_conflict.competing_rules`, `spatial_uncertainty.*`) by reference.
  Adversarial deep nesting could raise `RecursionError` inside validation. Inputs are upstream
  schema-validated canonical rule_evaluation (bounded depth) today; add a depth bound at the endpoint.

## Test coverage (G4, non-blocking)
- **FH-M5T001-Q1:** add a sliver / invalid-geometry / `inconsistent_confident_geometry` AS-4 fixture
  variant (currently only `split_lot`; the other fail-safe reasons share the code path but aren't
  separately fixtured).
- **FH-M5T001-Q2:** independently assert the `bbl_mismatch` conflict trigger and a wrong-type **cap**
  value (only wrong-type `lot_area` is currently fixtured); both are exercised by code today.

## Contract (G1, non-blocking hardening)
- **FH-M5T001-C1:** `constraint.provenance` is `["object","null"]`; a `known`/`draft` constraint could
  carry `null` (looser than the prose "null only for a recorded gap"). A future revision could require
  `provenance` non-null when `state ∈ {known, draft}` or carry `provenance_refs` for the district as
  `lot_area` does. (District remains traceable by reference via consumed `input_provenance`.)
- **FH-M5T001-C2:** `constraint.provenance` / `citation.provenance` are open objects; a later version
  could narrow to the resolved `source_fact` shape once stable.

## Code (G3, non-blocking observations — no action required)
- **FH-M5T001-K1:** `_positive_finite_float` coerces the trace cap to `float` (value-identical;
  `15000` → `15000.0`). "Verbatim" holds in value.
- **FH-M5T001-K2:** integrity recompute uses top-level `rule_evaluation.lot_area_sq_ft` rather than the
  trace's `evaluated_inputs.lot_area_sq_ft` — strictly more conservative (a mismatch also fails closed).
- **FH-M5T001-K3:** the BBL cross-check (profile vs rule_evaluation `data_conflict`) is an extra
  fail-closed guard beyond §5 — conservative, kept.
- **FH-M5T001-K4:** `_no_scenario_missing` can carry `coverage_status="conditional"` on a `no_scenario`
  outcome (coverage carried through while the scenario-layer input is absent) — honest, no schema
  violation.

These are non-blocking and do not affect M5-T001 acceptance eligibility. Final acceptance of M5-T001
remains gated on genuine G6 legal approval of the M4 dependency chain (M4-T001) — not weakened.
