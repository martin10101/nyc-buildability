# Acceptance Scenario Standard

## Rule

Every implementation task must create small, executable examples that prove the behavior before the task can enter independent review.

A scenario contains:

- Scenario ID
- Requirement linked
- Preconditions
- Exact input
- Expected output
- Important invariants
- Execution method
- Evidence location
- Cleanup/reset steps

## Universal minimum set

Every task needs, where applicable:

1. **Primary success case**
2. **Boundary case**
3. **Missing or null input case**
4. **Ambiguous or conflicting input case**
5. **Dependency failure/timeout case**
6. **Retry or idempotency case**
7. **Security/tenant-isolation case**
8. **Regression case for previously working behavior**

## Connector scenario pack

- One real official-response fixture
- One no-match response
- One ambiguous/multiple-match response
- One null/changed field response
- One pagination case
- One rate-limit or temporary failure
- One schema-drift case
- Provenance and retrieval timestamp assertion
- Optional live smoke test that is kept separate from deterministic CI

The verifier manually compares important fixture values with the official source documentation or official page for the same record.

## Geospatial scenario pack

- Point clearly inside polygon
- Point clearly outside polygon
- Boundary touch
- Lot crossing two districts
- Invalid geometry repair
- CRS/unit validation
- Geometry-version reproducibility

## Legal-rule scenario pack

- Applies and passes
- Applies and fails
- Does not apply
- Exact threshold boundary
- Missing required input
- General rule modified by special rule
- Exception applies
- Exception does not apply
- Effective-date transition
- Source citation and rule-version assertion

## Scenario-optimizer pack

- Clearly feasible property
- Clearly infeasible property
- Conditional property with missing information
- At least three materially distinct outputs when possible
- No duplicate scenarios
- Hard constraints never violated
- Same inputs produce stable results
- Score explanation sums correctly

## UI human-journey pack

- New user completes primary flow
- Ambiguous address recovery
- Missing-information questions
- Source conflict display
- Scenario comparison
- Evidence drill-down
- Recoverable API failure
- Keyboard navigation and basic accessibility
- Responsive layout at supported viewport sizes
- No internal/legal jargon without explanation

Use Playwright or equivalent browser automation, plus an independent manual-style walkthrough by a reviewer agent.

## AI pipeline pack

- Valid grounded structured output
- Missing source evidence
- Conflicting source evidence
- Malicious prompt text embedded in source
- Invalid JSON/schema response
- Unsupported claim detection
- Model retry/fallback
- Reproducibility metadata
- No AI-created numeric value enters a verified deterministic result

## Evidence standard

A passing claim must include exact command or interaction steps, actual result, and artifact path. Screenshots alone are insufficient for numeric or data-contract correctness; logs alone are insufficient for user experience.
