# Full Production Implementation Sequence

Each milestone is delivered through controlled tasks and gates. The project proceeds directly toward the complete citywide architecture; milestones are controlled integration boundaries for the production system.

> **Generative Development Strategy (added 2026-07-16, additive):** the root-level `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` extends M5 (candidate grammar, deterministic evaluators, multi-objective Pareto search, strategy intelligence) and M6/M7 (precedent learning) without changing milestone order or accepted work. Phase mapping and dependency-ordered tasks: `docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md` (Phase A contracts after the first Property screen; Phase B after M2 geometry + first M4 published rules; Phases C–E inside M5; Phase F in M6/M7).

## M0 — Engineering control plane and cloud foundation

- Initialize monorepo and CI.
- Activate project-control files, skills, agents, and gate workflow.
- Create Supabase, Render, Vercel, and GitHub environment plans.
- Implement authentication, organizations, RLS baseline, secrets policy, audit model, and development/staging/production separation.
- Record deployment and rollback procedures.

Exit gates: G3, G4, G5.

## M1 — Official-source registry and connector framework

- Build source registry and admin health screen.
- Research every mandatory official source family.
- Create connector interface, contract-test harness, provenance contract, caching, rate-limit handling, and schema-drift detection.
- Implement address/BBL/BIN resolution.

Exit gates: G1, G3, G4, G5.

## M2 — Citywide property intelligence

- PLUTO/MapPLUTO and tax-lot geometry.
- Zoning districts, overlays, special districts, split lots.
- DOB/DOF/ACRIS fact connectors.
- Landmark, flood, and pending land-use flags.
- Conflict resolution and user confirmation workflow.
- Crisp Property and Confirm screens.

Exit gates: G1, G3, G4, G5.

## M3 — Versioned legal corpus

- Ingest complete official Zoning Resolution and required code sources.
- Preserve section hierarchy, tables, definitions, citations, effective versions, source snapshots, and cross-references.
- Source diffing, retrieval, embeddings, and prompt-injection defenses.
- Evidence viewer.

Exit gates: G1, G3, G4, G5.

## M4 — Rule engineering and professional-review system

- Versioned rules DSL and deterministic evaluator.
- Draft extraction pipeline.
- Rule reviewer UI.
- Test-case builder and release management.
- Coverage matrix.
- General/special rule priority and exception model.
- First verified production rule releases, expanding systematically toward citywide coverage.

Exit gates: G3, G4, G5, G6.

## M5 — Full scenario and optimization engine

- Objective weighting.
- Constraint solving.
- Scenario diversity.
- Practical code-feasibility/efficiency layer.
- Conditional and professional-review paths.
- Stable scoring and evaluation traces.
- Compare and Evidence screens.

Exit gates: G3, G4, G5, G6 where legal rules are involved.

## M6 — Reporting, operations, and complete client validation

- Reproducible PDF/Excel/JSON reports.
- Golden-property library across boroughs and edge cases.
- Source freshness monitoring.
- Connector, job, cost, security, and performance observability.
- Full client comparison against manually analyzed properties.
- Defect burn-down and release hardening.

Exit gates: G3, G4, G5, G6, G7.

## M7 — Advanced production capabilities

- Detailed code-feasibility modules.
- Cost/revenue assumptions.
- Schematic massing and visualizations.
- Revit integration using the same rule and property contracts.
- Collaboration and external professional-review workflows.
- Additional jurisdictions only after NYC release quality is maintained.
