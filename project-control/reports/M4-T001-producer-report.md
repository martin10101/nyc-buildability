# M4-T001 — Producer report

Task: **M4-T001 Rules-engine foundation: versioned rule system + first rule family (R5 residential FAR).**
Producer: orchestrator (lead-only, owner directive 2026-07-21; no producer subagent dispatched).
Status: **implementation complete; self-checks green; ready to freeze a submit SHA and dispatch the
independent gates (G3 code-review, G4 integration/regression). G6 is a separate qualified-human event.**

## Submission summary

Built the **reusable** deterministic zoning-rules system (not a one-off R5 calculator): a versioned
JSON rule DSL, a deterministic evaluator with full calculation + citation traces, section-level ZR
source snapshots with provenance, a rule lifecycle whose `published`/`Verified` terminus requires a
recorded G6 qualified-human approval, and coverage honesty for unimplemented families. The first
implemented family is **R5 residential FAR** (`needs_review`, never auto-published/Verified). A
**structurally different** second family (a rear-yard minimum) is representable with **zero engine
changes**, proven by a fixture. M2-T013 geometric uncertainty is propagated, never collapsed.

## What was built

### Engine (`services/api/app/rules/`, all new)
`lifecycle.py`, `coverage.py`, `operations.py`, `snapshots.py`, `models.py`, `dsl.py`,
`evaluator.py`, `registry.py`, `__init__.py`, plus versioned contracts
`schemas/v1/rule_definition.schema.json` and `schemas/v1/evaluation_trace.schema.json`. Family logic
is **data, not code**: no engine file mentions any family or district name (test-enforced). No
`eval`/string-expression parser — computations are structured, inspectable steps.

### First rule family — R5 residential FAR (`rulesets/r5_residential_far.rule.json`)
`needs_review` draft citing NYC ZR **§23-21** (Last Amended 2024-12-05). Computes the
standard-zoning-lot maximum residential FAR (R5/R5A/R5B = 1.50; R5D = 2.00) and the resulting
maximum residential floor area; surfaces the qualifying-residential-site higher FAR as a conditional
alternative and the single-dwelling-unit 0.60 equivalent-FAR cap as a documented limitation
(neither collapsed nor silently applied). Declares a special-purpose-district modifier interaction
point.

### Section-level ZR snapshot (`docs/research/zr-snapshots/v1/zr-23-21.snapshot.json`)
Real capture from the official DCP portal (`.../article-ii/chapter-3/23-21`) with full provenance
(request URL, retrieved_at, section Last Amended, verbatim excerpt, sha256 content digest verified
on load). Per M1-T004 §5.5 the AI-summarized-markdown capture is **not** raw-HTML-verified:
`raw_html_verified: false`, `extraction_status: extracted_draft` — a drafted candidate pending
raw-HTML verification **and** G6 approval before any citing rule is published.

### Second-family representability proof (`services/api/tests/rules/fixtures/`)
A SYNTHETIC rear-yard rule (minimum linear dimension — structurally different from a ratio×area FAR)
+ its clearly-labeled synthetic snapshot, loaded and evaluated by the **same** engine with zero
engine changes.

### Architecture doc (`docs/RULES_ENGINE_ARCHITECTURE.md`)
DSL, lifecycle, versioning, citation model, coverage semantics, uncertainty propagation, snapshot
layout (M3-aligned), the G6 boundary, and the documented promotion path of the rule/trace schemas
into `packages/contracts` when a cross-tier consumer arrives.

## Acceptance scenarios RE-S1 … RE-S8 (evidence — `services/api/tests/rules/test_rules_engine.py`)

| Scenario | Evidence |
|---|---|
| RE-S1 DSL round-trip + full trace | `test_re_s1_dsl_round_trip_and_full_trace`, `test_re_s1_rule_file_validates_against_schema` — parses, schema-validates, deterministic trace (inputs, steps, citation, versions) |
| RE-S2 lifecycle (never auto-Verified) | `test_re_s2_draft_rule_never_verified`, `_dsl_rejects_published_status`, `_publish_requires_g6_approval`, `_verified_only_for_published_with_matching_approval` |
| RE-S3 applicability + special-district point | `test_re_s3_applicability` (positive/negative/boundary), `_special_district_interaction_point_present` |
| RE-S4 missing evidence + uncertainty | `test_re_s4_missing_required_input_yields_typed_missing_no_value`, `_uncertainty_propagates_never_collapses` (all 6 M2-T013 classes) |
| RE-S5 second-family, zero engine changes | `test_re_s5_second_family_evaluates_with_same_engine`, `_zero_engine_changes_families_are_pure_data`, `_second_family_uses_only_generic_ops` |
| RE-S6 provenance | `test_re_s6_every_citation_resolves_to_snapshot_provenance`, `_export_without_provenance_is_impossible`, `_snapshot_digest_tamper_evidence` |
| RE-S7 coverage honesty | `test_re_s7_unimplemented_family_is_visible_unsupported` |
| RE-S8 regression/determinism | `test_re_s8_determinism_same_inputs_identical_trace`; full API suite green (below) |

Plus the ACCEPTANCE_SCENARIO_STANDARD legal cases: applies+passes, applies+fails (data_conflict),
threshold boundary (4,000 sq ft), exception applies/does-not, citation + rule-version +
effective-date assertions, general-modified-by-special stub; and DSL integrity guards (forward-step
ref rejected, unresolvable citation rejected) + engine↔canonical coverage-vocabulary drift check.

## Self-check evidence (local worktree; Python 3.11.9, jsonschema 4.26.0)

- `python -m pytest tests/rules/ -q` → **36 passed**
- `python -m pytest -q` (full services/api) → **626 passed** (590 prior baseline + 36 new; no regression)
- `python -m ruff check .` (services/api) → **All checks passed**
- `python .github/scripts/validate_contracts.py` → unaffected (no `packages/contracts` schema changes; engine schemas are engine-owned and validated via jsonschema at load + the acceptance pack)

The web jobs (Node) are not runnable on the thin client and are unaffected — this task touches no
`apps/web/**` and no shared canonical contract; they run on CI.

## Scope decisions & disclosures

- **Engine-owned rule/trace schemas (not `packages/contracts`).** Deliberate altitude choice: no
  cross-tier consumer exists yet (`apps/web/**` is a forbidden path). Documented promotion path to
  `packages/contracts` via M2-T010 tooling when the reviewer UI/report layer arrives. Not a forked
  competing schema (no prior rule/trace schema exists).
- **`zr-23-21` is a summarizer-mediated draft**, `raw_html_verified: false`. Raw-HTML byte
  verification is a needs_review/G6 item, honestly flagged in the snapshot and the R5 rule.
- **Second family is a synthetic test fixture**, clearly labeled, kept out of the production
  rulesets and out of `docs/research/zr-snapshots` (which hold only real captures).
- **No `published`/`Verified` rule authored.** The engine cannot reach `verified` without a G6
  approval record; the DSL loader rejects an authored `published` status.

## Files changed (all within `allowed_paths`)

New: `services/api/app/rules/**` (9 modules + 2 schemas), `services/api/app/rules/rulesets/r5_residential_far.rule.json`,
`services/api/tests/rules/test_rules_engine.py`, `services/api/tests/rules/fixtures/**` (synthetic rule + snapshot),
`docs/research/zr-snapshots/v1/zr-23-21.snapshot.json`, `docs/RULES_ENGINE_ARCHITECTURE.md`,
`project-control/reports/M4-T001-producer-report.md`. Started earlier: G0 readiness + claim + B-010
blocker (`5de0971`).

## Blockers

- **B-010 (open, bounded):** the client R5 benchmark sheet is not in the repo; blocks ONLY the
  client-benchmark validation acceptance item. All engine/architecture/snapshot/fixture work
  proceeds without it.
- **G6 (standing human dependency):** any `published`/`Verified` labeling of the R5 rule requires
  the qualified zoning professional; the engine (G3/G4) is acceptable independently.

## Gate status

Required gates G0 (PASS, recorded) / G2 (self-check) / G3 (code) / G4 (integration) / G6 (human).
Submitting to the independent gates **G3 code-reviewer** and **G4 qa-engineer** at the frozen submit
SHA. Not accepted; no merge; no rule published/Verified.
