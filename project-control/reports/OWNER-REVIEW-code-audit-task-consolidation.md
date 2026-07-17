# OWNER REVIEW — Code-audit follow-up task consolidation

**Prepared by:** orchestrator, 2026-07-17, immediately after M0-T010/M0-T013 acceptance (per the directive's timing condition)
**Status:** AWAITING OWNER REVIEW — all six packets are `backlog`; **no producer has been dispatched and nothing has been implemented.**
**Directive honored:** "Do not create a large collection of overlapping tasks. Consolidate these into the smallest dependency-ordered set and return the task packets for owner review before implementation."

## 1. The consolidated set (6 packets, zero overlap)

Every bullet of the directive maps to exactly one task. The 5 audit workstreams plus the already-queued Confirm screen collapse into 6 packets because the directive's frontend-boundary bullets and the Confirm screen touch the same files — splitting them would create the overlapping-task collection the directive prohibits.

| # | Task | Covers | Producer | Depends on | Gates |
|---|------|--------|----------|-----------|-------|
| 1 | **M0-T014** Project-control CLI hardening | P0 project-control (all 7 bullets) | backend-engineer | — | G0,G2,G3,G4 |
| 2 | **M2-T003** Property API boundary + contract-version hardening | P0 API boundary, backend/contracts half: backend response validation; exact status/state pairs at the API; TS type **generation pipeline**; contract_version 1.1.0 resolution; the 500+no_match fixture | backend-engineer | — | G0,G1,G2,G3,G4 |
| 3 | **M2-T002** Confirm screen with hardened API client | P0 API boundary, frontend half: exact pair enforcement + `unexpected_response`; the HTTP-500+state=no_match regression; runtime validation of 200 profiles before render; bounded input/error reflection; cancellation/timeout — PLUS the queued Confirm screen itself and M2-T001 carry-forwards D1–D5 | frontend-engineer | M2-T003 | G0,G2,G3,G4,G5 |
| 4 | **M2-T004** Data-semantics separation + snapshot lineage | P1 (all 4 bullets) | backend-engineer | M2-T003 | G0,G1,G2,G3,G4 |
| 5 | **M0-T015** Deployment reconciliation preflight | Deployment blocker (all 5 bullets); resolves M2-T001 G3 D8 (CORS/proxy); **no provisioning** — B-002 stays owner-gated | cloud-architect | — | G0,G2,G3,G5 |
| 6 | **M1-T009** Pre-paid-traffic resilience | Resilience (all 6 items: caching, Retry-After, jitter, breaker, LKG+staleness, budgets) | backend-engineer | M2-T003 | G0,G1,G2,G3,G4 |

**Dependency-ordered waves** (tasks inside a wave are parallel-safe — disjoint file scopes):

- **Wave 1 (can start on your approval):** M0-T014 (tools/), M2-T003 (services/api + packages/contracts), M0-T015 (render.yaml + deploy config)
- **Wave 2 (after M2-T003):** M2-T002 (apps/web — the client-facing critical path), M2-T004 (services/api + contracts), M1-T009 (services/api connector layer — sequenced after M2-T004 if file overlap emerges at G0)

## 2. Directive-bullet → task traceability (verbatim bullets)

### 2.1 P0 project-control hardening → M0-T014
- progress status must use an explicit transition enum and may never set accepted
- accept must require awaiting_gate, all required gates PASS, all dependencies accepted and zero open task/blocker records
- gate reviewer must be listed in reviewer_agents and differ from producer_agent
- task IDs and report paths must be validated and contained under approved directories
- writes must be atomic and concurrency-safe
- document honestly that a caller-provided --agent string is not cryptographic identity
- add negative tests for every prohibited transition and spoofing attempt

*Note recorded in the packet:* G2 evidence gates are recorded by the orchestrator after evidence validation (precedent M2-T001-G2, M0-T013-G2). The hardening documents this as the single sanctioned exception to "reviewer listed in reviewer_agents" rather than silently breaking the established G2 mechanism. If you want G2 recorded differently, say so at review.

### 2.2 P0 Property API boundary hardening before Confirm → M2-T003 (backend/contracts) + M2-T002 (frontend client)
- enforce exact HTTP-status/state pairs → **M2-T003** (API cannot emit undocumented pairs) + **M2-T002** (client rejects them)
- mismatched pairs must produce unexpected_response → **M2-T002**
- regression: HTTP 500 + state=no_match must never become no_match → fixture **M2-T003**, client regression **M2-T002**
- full runtime validation of a 200 profile before rendering → **M2-T002** (against generated types)
- generate TypeScript types from the canonical contract, no competing handwritten representation → **M2-T003** (pipeline), **M2-T002** (migration/removal)
- enforce backend response validation → **M2-T003**
- resolve contract_version 1.1.0 declaration → **M2-T003**
- bounded input/error reflection and browser request cancellation/timeout → **M2-T002**

Sequencing honored: the Confirm screen cannot start before the boundary hardening (hard dependency M2-T002 → M2-T003).

### 2.3 P1 data semantics before persistence/professional reports → M2-T004
All four bullets (dimension separation; no 108-column completeness; fact_key vs observation_id; digest + snapshot lineage). Sequenced before any persistence/professional-report task; does not block M2-T002.

### 2.4 Deployment blocker → M0-T015
All five bullets (requirements.txt, /api/v1/health, NEXT_PUBLIC_API_BASE_URL or proxy, phantom worker/cron entrypoints, auth/CORS/security-header completion). The packet forbids provisioning; B-002 remains owner-gated. Also closes M2-T001 G3 D8 (CORS/proxy decision).

### 2.5 Pre-paid-traffic resilience → M1-T009
Caching, Retry-After, jitter, circuit breaker, last-known-good with visible staleness, request budgets — one connector-layer task with deterministic clock-injected tests.

## 3. What was deliberately NOT created
- No separate "unexpected_response task", "typegen task", "regression-test task", "CORS task" etc. — each would overlap an existing packet's file scope.
- No reopening of accepted tasks (M2-T001 stays accepted; its D1–D5 carry-forwards ride in M2-T002 as contracted inputs).
- No master-plan/milestone changes; no expansion-pack planning (counter-notice §2 owner-review hold untouched).

## 4. What happens on your approval
Reply with approval (or edits) and I will move Wave 1 to `ready`, dispatch producers under the normal G0→G5 gate chain, and run everything through the protected-main PR workflow (task branch → PR → checks green → merge). Until then, nothing runs.
