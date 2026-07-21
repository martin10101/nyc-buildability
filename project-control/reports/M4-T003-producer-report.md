# M4-T003 — Producer report

Task: **M4-T003 Rules-engine correctness hardening (fail-closed input & predicate validation, temporal
versioning, compliance determinations).**
Producer: orchestrator (lead-only, rules-engineer role; no producer subagent dispatched).
Status requested: **`awaiting_gate`** — implementation complete; self-checks green; ready to freeze a
submit SHA and dispatch independent gates G3 (code), G4 (integration/regression), G5 (security). Not
accepted; no merge; no rule published/Verified.

## Why this task
The owner launch-readiness review (2026-07-21) returned a **no-go for public launch** and directed
correcting the M4-T001 rules engine and independently re-reviewing it **before any G6** and **before
the M4-T002 integration is merged**. Every actioned finding was first **verified against the code**
(not taken on faith). The owner selected the **broader corrective wave** (the confirmed defects PLUS
effective-date temporal versioning and a compliance pass/fail capability).

## Findings addressed (each verified in code, then fixed)

| # | Owner finding (verified) | Fix |
|---|---|---|
| 1 | Negative / non-finite numeric inputs produced bad values (`lot_area=-5000` → `floor_area=-7500`); a non-numeric input crashed | **Fail-closed input validation** in the evaluator: every supplied input is checked for type / declared enum / numeric finiteness / declared numeric domain BEFORE computation; a required-or-supplied invalid value yields a typed `professional_review_required` with NO computed value and NO crash |
| 2 | Predicate references were not validated (a misspelled `applicability` / exception-condition input silently became `not_applicable`) | **DSL-load validation** walks the applicability + every exception-condition predicate tree; an undeclared predicate input now fails the rule load (`DSLError`) |
| 3 | Evaluation traces carried no rule test/release status | **`rule_release`** section on every trace: lifecycle status + deterministic-tests + independent-review + G6 state + `verified_eligible` (false for a draft) |
| 4 | The effective-date test was one static date, not a before/after transition | **Effective-date temporal versioning**: rules carry `effective_from`/`effective_to`; `evaluate(..., as_of_date=...)` gates a version to its half-open window (out-of-window → visible not-effective `not_applicable`); `registry.effective_rules(family, as_of)` selects the version in effect; proven by a synthetic 2-version before/after fixture |
| 5 | "Applies and fails" only tested a spatial conflict, not a proposal failing a constraint | **Compliance determination**: a rule may compare a proposal input against a computed output and emit a genuine pass/fail (`applies+passes` / `applies+fails`) in the trace WITHOUT changing coverage; proven by a synthetic compliance fixture |

## What changed (all within `services/api/app/rules/**` + `services/api/tests/rules/**`)
- **Engine-owned schemas extended additively** (`schemas/v1/rule_definition.schema.json`,
  `schemas/v1/evaluation_trace.schema.json`): input domain (`minimum`/`maximum`/`exclusive_minimum`/
  `exclusive_maximum`), `effective_from`/`effective_to`, `release`, `determination`; trace
  `input_validation`/`rule_release`/`effective_window`/`determination`. The canonical
  `packages/contracts/**` are **untouched** (these schemas are engine-owned).
- **`evaluator.py`** — fail-closed `_validate_inputs`; temporal gating; determination evaluation;
  release status; non-finite floats are represented as strings so a fail-closed trace stays strict
  JSON. Single shared trace builder threads the new sections through every return path.
- **`dsl.py`** — parses the new fields; validates predicate + determination references fail-closed;
  enforces ordered effective windows.
- **`models.py`** — `InputSpec` domain fields; `RuleDefinition` temporal/release/determination fields
  + `is_in_effect(as_of)` + `output_names()`; `EvaluationTrace` new sections + `as_dict`.
- **`registry.py`** — `as_of_date` passthrough; `effective_rules(family, as_of)` temporal selection.
- **R5 rule** — a **semantic correction**: the applicability set (`R5/R5A/R5B/R5D`) was in
  `zoning_district`'s `enum`, which fail-closed validation would (wrongly) treat as an invalid input
  for `R7`. `enum` now means the input DOMAIN; district SCOPE stays in applicability, so a non-R5
  district remains a visible `not_applicable` (preserving M4-T001 + M4-T002 RI-S6). Added
  `exclusive_minimum: 0` on `lot_area_sq_ft`, `effective_from: 2024-12-05` (the section's Last
  Amended date), and a `release` block.
- **Synthetic fixtures** (`tests/rules/fixtures/m4t003/**`, clearly labeled, out of production
  rulesets): two temporal versions + one compliance rule + one synthetic snapshot (digest-verified).

## Acceptance scenarios RH-S1 … RH-S8 (evidence — `tests/rules/test_rules_engine_hardening.py`)

| Scenario | Tests |
|---|---|
| RH-S1 negative numeric fails closed | `test_rh_s1_negative_lot_area_fails_closed_no_value` (PRR, outputs `{}`, `input_validation.valid=false`, `missing_critical`) |
| RH-S2 non-finite fails closed + strict-JSON trace | `test_rh_s2_non_finite_lot_area_fails_closed` (NaN/inf/-inf; `json.dumps(..., allow_nan=False)` succeeds) |
| RH-S3 wrong type / bad enum fail closed; non-R5 stays not_applicable | `test_rh_s3_wrong_type_fails_closed_no_crash`, `_invalid_enum_fails_closed`, `_non_r5_district_is_still_not_applicable_not_invalid` |
| RH-S4 predicate/determination refs validated at load | `test_rh_s4_misspelled_applicability_input_rejected_at_load`, `_misspelled_exception_condition_input_rejected_at_load`, `_determination_undeclared_output_rejected_at_load` |
| RH-S5 release status in trace | `test_rh_s5_release_status_in_trace_draft_not_verified_eligible` |
| RH-S6 effective-date before/after transition | `test_rh_s6_effective_date_selects_version` (2023→v1 FAR 1.0; 2024-01-01 boundary + 2024→v2 FAR 2.0; out-of-window → not-effective), `_no_as_of_means_no_temporal_gating` |
| RH-S7 genuine applies+passes / applies+fails | `test_rh_s7_compliance_pass_and_fail` (pass + fail, coverage stays conditional), `_no_determination_when_rule_has_none` |
| RH-S8 regression / determinism / never-verified | `test_rh_s8_valid_r5_still_computes`, `_hardened_trace_validates_against_schema`, `_determinism_same_inputs_identical_trace`, `_nothing_verified`, `_finite_helpers_are_strict` |

## Self-check evidence (local worktree; Python 3.11.9, shapely 2.0.7, pytest 8.4.2, jsonschema)
- `python -m pytest tests/rules/test_rules_engine_hardening.py -v` → **20 passed** (RH-S1..RH-S8).
- `python -m pytest tests/rules/test_rules_engine.py -q` → **36 passed** (the accepted M4-T001 pack,
  unchanged; **no regression**).
- `python -m pytest -q` (full `services/api`) → **646 passed** (626 M4-T001 baseline + 20 new).
- `python -m ruff check app tests` → **All checks passed**.

Expected vs actual: `lot_area=-5000` → PRR, no value (was `-7500`); `NaN`/`inf` → PRR, strict-JSON
trace (was `inf` output); misspelled predicate input → load error (was silent `not_applicable`);
as_of 2023 → FAR 1.0, as_of 2024 → FAR 2.0; proposal 12 000 ≤ 15 000 → pass, 20 000 → fail. All match.

## Scope decisions & disclosures
- **`enum` = input domain, not rule scope.** The R5 `zoning_district` enum was the applicability set;
  leaving it would make fail-closed validation reject a non-R5 district as invalid. Corrected so
  district scope stays in applicability (R7 → visible `not_applicable`, unchanged behavior).
- **`as_of_date` is always caller-supplied** — the engine never reads the wall clock, so evaluations
  stay deterministic and reproducible.
- **A compliance `fail` does NOT change coverage** — a draft rule stays `conditional`; the pass/fail
  determination is orthogonal to the coverage/confidence label.
- **Temporal + compliance demonstrated on synthetic fixtures** (labeled, out of production rulesets);
  the R5 production rule gains only `effective_from` (its Last Amended date) — a real prior R5 version
  needs official legal-source research (a documented follow-up), which this task does not fabricate.

## Known limitations
- Effective-date selection is by rule-`family` window; a production temporal series (e.g. successive
  R5 amendments) needs the corresponding official prior-version captures (source research), out of
  this engine-hardening slice.
- `release.independent_review` / `qualified_human_approval` are author-declared pointers; the
  authoritative record remains the project-control ledger + a recorded `G6Approval`.

## Security / provenance impact
Strictly strengthens fail-closed posture: invalid/hostile inputs (negative, NaN, inf, wrong type, bad
enum) now yield a typed professional-review outcome with no value and no crash; misspelled predicate
inputs fail at load. No auth/storage/secret/network/dependency change. Provenance stays fail-closed
(`RuleResult.export()`); nothing is published or Verified (`verified_eligible=false` for every draft).

## New risks or dependencies
None. No new package. Additive engine-owned schema changes only; canonical contracts untouched.

## Recommended next tasks
1. Owner-authorized merge of M4-T003, then **rebase M4-T002 onto the corrected engine** and integrate
   (M4-T002 stays held at CI-green `f25dbff` with 3 gate PASS).
2. Official prior-version R5 capture to make R5 temporal selection real (source research).
3. The broader launch-readiness items (auth/RLS, rate limiting/request budgets, persistence, the
   PLUTO↔ZTLDB↔zoning↔geometry↔spatial↔rules composition layer, a persisted immutable G6 publication
   workflow) remain tracked for the pilot phase — not part of this engine-hardening slice.

## Gate status
Required gates **G0 (PASS, recorded) / G2 (self-check green above) / G3 (code) / G4 (integration) /
G5 (security)**. Submitting to the independent gates at the frozen submit SHA. Not accepted; no merge;
no rule published/Verified.

## Exact report path
`project-control/reports/M4-T003-producer-report.md`
