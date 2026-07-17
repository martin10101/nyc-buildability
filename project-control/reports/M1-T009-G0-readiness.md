# G0 Readiness Record — M1-T009 (Pre-paid-traffic connector resilience)

- **Gate:** G0 definition-of-ready (administrative; recorded by the orchestrator)
- **Recorded:** 2026-07-17
- **Task:** M1-T009, implementation, producer backend-engineer, reviewers data-contract-verifier (G1) + qa-engineer (G3/G4)

## Readiness checklist

- **Objective unambiguous:** YES — connector-layer resilience before paid traffic: TTL response caching, exact Retry-After honoring, jittered bounded backoff, per-source circuit breaker, last-known-good serving with VISIBLE staleness (provenance/coverage — never silent), per-analysis request budgets with typed budget_exceeded failure.
- **Dependencies:** M2-T003 ACCEPTED (26th) — staleness labeling rides on the validated response contract; LKG payloads must still pass the backend validation now enforced at the boundary.
- **File scope exclusive:** `services/api/**` + own producer report. ORCHESTRATOR OVERLAP RESOLUTION: ci.yml allowance suspended for the parallel window (same as M2-T002's record) — new pytest suites are picked up by the existing `api` job automatically; report any genuinely needed CI change for the orchestrator to apply sequentially. NON-overlapping with M2-T002 (`apps/web/**`).
- **Contract-visibility constraint:** `packages/contracts/**` is FORBIDDEN — if a staleness field must be contract-visible, STOP and report it as a recommended follow-up (an additive M2-T003-pipeline change reviewed at G1); do not edit the contract in this task. Staleness can live in the existing provenance/coverage structures where the contract already allows it.
- **Inputs/outputs defined:** packet text; owner directive §2.5; M1-T002/M1-T005 SODA client + fixture transport seam; M1-T003/M1-T004 documented Socrata rate-limit/Retry-After semantics.
- **Acceptance scenarios:** S1–S8 (cache TTL, clock-controlled Retry-After, jittered backoff distribution, breaker state machine, LKG-with-visible-staleness, budget exhaustion, idempotency, full-suite regression; no live network in CI).
- **Determinism constraint:** injected clock, no sleeps in CI (packet risk 2).
- **Credentials:** none (fixture transport only). No blocker.
- **Gates assigned:** G0, G1 (data-contract-verifier — staleness/provenance semantics), G2, G3 + G4 (qa-engineer).
- **Execution location and disk:** source edits in isolated worktree `.claude/worktrees/M1-T009`; local pytest permitted (pure-Python, deps already installed); full validation in CI on the task PR.
- **Low-storage budget:** respected — KB-scale code/tests.
- **Cleanup/cloud routing:** task branch → PR → CI → merge; worktree removed after merge via deletion-approval flow.

Result: PASS — ready to claim and dispatch in parallel with M2-T002 (disjoint scopes after the ci.yml resolution above).
