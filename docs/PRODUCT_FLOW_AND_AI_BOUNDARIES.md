> **Partly set aside — the [2026-09-28 plan](PRODUCT_PLAN_CURRENT_2026-09-28.md) wins on conflict.** Set aside: the four-step flow "Step 1 Property … Step 4 Evidence" (plan §3: one dashboard page), "Practical usable range" (Phase 2), "Verified, conditional, review-required … labels" (plan §5, §5a.3) and "Next.js on Vercel" (ADR-004). The AI-boundary and state-machine rules still apply.

# Product Flow and AI Boundaries

## Design objective

Make the user experience exceptionally simple while keeping the legal/data architecture rigorous.

## Main analyst interface

### Step 1 — Property

- Address or BBL
- Development type
- Objective selection
- Analyze button

### Step 2 — Confirm

Present a compact property card with:

- Canonical address
- BBL/BIN
- Lot area and geometry summary
- Existing building facts
- Zoning districts, overlays, and special districts
- Landmark/flood/pending-action flags
- Data conflicts
- Only questions the government data cannot reliably answer

### Step 3 — Compare

Show:

- Maximum preliminary development potential
- Practical usable range
- Ranked scenario cards
- Objective and score breakdown
- Verified, conditional, review-required, conflict, and unsupported labels
- Main opportunity and main risk

### Step 4 — Evidence

For every material value show:

- Source fact
- Rule
- Formula
- Units
- Effective/source version
- Assumptions
- Evaluation trace
- Reviewer/coverage status

## UI rules

- Progressive disclosure: normal users do not see ingestion internals.
- One clear next action per screen.
- Plain language first; exact legal language available in evidence view.
- Never encode legal certainty only by color.
- Never display “best” without the optimized objective.
- Never silently use a default that materially changes a scenario.
- Conflicts and unsupported checks remain visible in results and reports.

## Standing label and per-stat law link (ADR-007)

Professional review is advisory, not a gate (owner D-090-R164, 2026-10-04). Every website surface and
every exported report carries one standing, always-visible label: the results are computed from
official public sources, have not been professionally reviewed, and must be verified by a licensed New
York professional before reliance. Every printed stat links directly to the zoning-law text it rests on
(the captured, pinned source snapshot plus the official page). When an input is missing or a rule family
is not covered, the program says "not known" or "not covered" with the reason, never a guess. The ban on
compliance declarations ("complies", "approved", "guaranteed") still holds.

## Backend state machine

The workflow state is deterministic and persisted. Each transition has preconditions and produces an event. Failed steps are resumable.

The AI is invoked only after the backend has assembled bounded input and an exact output schema. AI output is validated and stored as a draft or explanation, never as an unverified legal result.

## Canonical contracts

Maintain versioned contracts for:

- Property profile
- Source fact
- Rule definition
- Rule evaluation trace
- Scenario
- Coverage status
- Analysis state transition
- Report evidence item

Frontend, API, workers, and reports consume the same contracts.

## Complexity containment

Use one modular monorepo and one deployable FastAPI service plus scalable worker processes. Do not create microservices without a demonstrated isolation, scale, or security need.

Recommended deployment:

- Next.js on Vercel
- FastAPI Web Service on Render
- Render background workers, cron jobs, and one-off jobs
- Supabase Postgres/PostGIS/Auth/Storage/pgvector
- GitHub CI

Internal modules remain separated by contracts so they can be extracted later if operational evidence justifies it.
