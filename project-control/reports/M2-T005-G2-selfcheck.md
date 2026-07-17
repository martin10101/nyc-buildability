# M2-T005 — G2 Producer Self-Check Evidence

- **Task:** M2-T005 — Confirm/Property a11y announcement + focus management (D1) + minors D2–D5 + N1 hygiene
- **Gate:** G2 (producer self-check; recorded by orchestrator per the hardened CLI convention `--reviewer orchestrator` = self_check role)
- **Producer:** frontend-engineer
- **Date:** 2026-07-17 (session 11)
- **Branch/commit under check:** `task/M2-T005-a11y-announcements` @ `689d118` (PR #33)

## Execution model disclosure

Per the low-storage policy, no npm/vitest/Playwright ran on the owner PC. The producer wrote code + tests (report: `project-control/reports/M2-T005-producer-report.md`); the orchestrator captured the executable half of G2 from GitHub Actions CI on PR #33 per the 2026-07-15 evidence-capture directive.

## CI evidence (PR #33, commit 689d118 — all jobs PASS on both push and pull_request events)

| Job | Result | Duration | Run/Job |
|---|---|---|---|
| web (lint + typecheck + build) | pass | 56s / 46s | actions/runs/29620815612/job/88015362030, runs/29620826778/job/88015392426 |
| web-e2e (vitest + Playwright vs recorded-official-fixture API) | pass | 2m57s / 2m34s | runs/29620815612/job/88015362041, runs/29620826778/job/88015392410 |
| api (ruff + pytest) | pass | — | both events |
| contracts / contracts-typegen / contracts-schema-bundle | pass | — | both events |
| control-plane (ADR-005 regression) | pass | — | both events |
| Scan repository for credentials | pass | — | both events |

Extracted from job 88015392410 log (verbatim key lines):

- vitest: `Test Files  13 passed (13)` / `Tests  156 passed (156)` — includes the new `announce.test.ts` (15 tests), `confirm-entry.test.tsx` (2 tests), extended `property-lookup.test.tsx` (30 tests), `confirm-screen.test.tsx` (11 tests), `api.test.ts` (31 tests, now NUL-free).
- Playwright: `Running 53 tests using 1 worker` → `53 passed (56.0s)` — 43 pre-existing journeys + 10 new (announcement arrivals ×4, focus assertions, keyboard-only lookup-to-confirm journey S6, D2/D3/D4 e2e checks).

## Scenario self-check mapping (producer report §3, cross-checked by orchestrator)

- S1 announcement exactly-once: 11-case parametrized component pack + 4 e2e arrival tests with live-region-count===1 — PASS in CI.
- S2 focus: document.activeElement asserted in component + e2e on both screens, keyboard retry with 800 ms delayed route, never-body checkpoints — PASS in CI.
- S3 minors: D2 computed-style e2e; D3 h1 component+e2e; D4 exactly-once component+e2e with Property regression; D5 token committed (pixel verification remains CF-2) — PASS in CI.
- S4 hygiene: byte scan captured in producer report — api.test.ts `raw control bytes present: NONE`, `escape sequence count: 1`; NOTE: PR #33's own diff shows the file as binary ONE last time because the old blob contains the NUL; text from this commit forward.
- S5 regression: zero existing assertions modified/deleted (all suite changes additive); full suites green above.
- S6 keyboard-only: new e2e journey, no mouse events — PASS in CI.

## Scope verification (orchestrator)

`git status`/diff of the task worktree: only `apps/web/**` + the producer report. The two M2-T006 A1 files (`apps/web/src/lib/contract.ts`, `apps/web/src/lib/__tests__/validate-profile.test.ts`) are NOT touched — the A1 overlap rule is satisfied on the M2-T005 side.

## Known limitations disclosed by the producer (for G3/G4 reviewers)

1. Real-screen-reader focus-echo vs polite-status interplay can only be judged in the CF-1 manual NVDA/VoiceOver session; DOM emits exactly one live announcement.
2. `client_timeout` announcement is unit-mapped but not screen-exercised.
3. Deterministic arrival focus moves focus even mid-typing (S2 determinism tradeoff, flagged).

## G2 verdict

Producer self-check evidence complete and green. G2 permits submission to independent review; it does not accept the task.
