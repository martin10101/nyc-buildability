# M4-T002 — G0 Definition-of-Ready reconciliation

- Gate ID: G0 (administrative readiness, orchestrator)
- Task ID: M4-T002 — Rules-engine integration with property-profile / spatial-analysis results
- Recorded by: orchestrator
- Result: PASS (ready to start; lead-only per owner directive 2026-07-21)

## Why this task now
Owner directive 2026-07-21: advance product engineering without waiting for B-010 or G6. The M4-T001
rules-engine foundation is merged to main (PR #76 @ `de88ba2`); the next unblocked product step is
connecting the engine to the property-analysis flow. This is the smallest properly controlled task for
that step (no new endpoint/UI/contract in this slice). CP-0032 not touched.

## Readiness checks (2026-07-21, base main `f2939d6`)
- **Dependency M4-T001 (engine):** on main, status `awaiting_gate` (G0/G2/G3/G4 PASS; awaiting G6). Its
  code (`services/api/app/rules/**`) is available and consumable now. M4-T001 is NOT accepted (G6
  outstanding); M4-T002's own final acceptance will therefore be coupled to M4-T001's G6 — acceptable
  and safe: the integration ships only `needs_review`/non-Verified draft results.
- **Dependency M2-T012 (profile contract 1.4.0):** accepted ✓ — `zoning_features` / `lot_geometry` /
  `spatial_intersection` keys are the read-only inputs.
- **Dependency M2-T013 (spatial uncertainty):** accepted ✓ — `LotIntersectionRecord` shape is the
  uncertainty substrate to preserve.
- **Contracts + coverage vocabulary:** available; the engine already asserts vocabulary equality with
  the canonical `coverage_status` contract.
- **No blocker required for the engineering slice.** G6 (human) and B-010 (client benchmark) remain
  outstanding but block only publication/verification + final acceptance, not this integration.

## Scope binding
Producer: lead-only (no producer subagent dispatched). Reviewers (independent, after a frozen SHA +
CI): code-reviewer (G3), qa-engineer (G4), security-reviewer (G5). Required gates G0/G2/G3/G4/G5. File
scope per packet `allowed_paths` (services/api/app/rules/**, services/api/tests/rules/**, own producer
report); consume profile/spatial contracts READ-ONLY (imports only); forbidden: modifying
profile/spatial/contract code, new endpoints/UI, publishing/Verifying, collapsing uncertainty,
project-control beyond own report, .claude/**.

## Verdict
**G0 PASS** — ready. Implement lead-only: a service-layer integration mapping a property profile +
M2-T013 spatial facts into evaluator inputs + `spatial_context`, preserving uncertainty, failing safe
on missing/uncertain spatial context, returning deterministic traces + honest draft status, and
preventing any downstream read of a draft as Verified. Then freeze a SHA, run CI, and dispatch G3/G4/G5
once. Return the frozen-SHA evidence packet before merge.
