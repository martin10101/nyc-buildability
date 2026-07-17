# M2-T001 — G2 producer self-check evidence (orchestrator-captured CI evidence)

- **Task:** M2-T001 Priority 4 Property screen
- **Date:** 2026-07-17 (UTC)
- **Branch:** `task/M2-T001-property-screen` at `dd34c7b`
- **Recorded by:** orchestrator (ADR-005 evidence capture — the producer cannot execute anything locally: owner PC at ~1.67 GB free, below the 4 GB floor, so the packet routed ALL execution to GitHub Actions)

## Commit chain on the branch

1. `1dd3224` producer: screen + libs + 11 components + 6 unit-test files + 7 Playwright specs + fixture-API harness + additive web/web-e2e CI jobs (46 files, +4072)
2. `89f4609` bot: `package-lock.json` regenerated on the CI runner via the "Generate web lockfile" workflow (run 29545548345, success)
3. `acc73ec` orchestrator: empty commit — GitHub does not fire `on: push` for GITHUB_TOKEN bot commits (anti-recursion), so CI had to be re-triggered
4. `dd34c7b` orchestrator mechanical lint fix: removed one unused `waitFor` import (the SOLE failure of run 29545748874 — both web jobs failed on that single eslint error; all four pre-existing jobs were green)

## Authoritative CI evidence (run on `dd34c7b`)

**Run:** https://github.com/martin10101/nyc-buildability/actions/runs/29548158336 — `completed / success`

| Job | Result |
| --- | --- |
| web (lint + typecheck + build) | success |
| web-e2e (vitest + Playwright vs recorded-official-fixture API) | success — 14 browser journeys |
| api (ruff + pytest) | success (142 tests, regression intact) |
| contracts (JSON Schema validation) | success |
| control-plane (workflow regression, ADR-005) | success |

secret-scan on `dd34c7b`: https://github.com/martin10101/nyc-buildability/actions/runs/29548158304 — success.

Playwright traces/screenshots uploaded as the `playwright-evidence` artifact on the run (7-day retention) — the G3 reviewer's browser-interaction evidence.

## Scenario mapping (producer's S1–S8 → executed tests, all green in web-e2e/web)

- S1 primary → e2e/primary-journey.spec.ts
- S2 boundary/D5 both join paths → e2e/no-match.spec.ts + e2e/partial-and-conflict.spec.ts + provenance unit tests
- S3 malformed-before-network (request-counter proof) + server 422 → e2e/validation.spec.ts
- S4 no-match billing-lot explanation → e2e/no-match.spec.ts
- S5 typed 502/503/504, 500+correlation id, connection-refused retry → e2e/failures.spec.ts
- S6 partial data + missing-inputs nothing-dropped invariant → e2e/partial-and-conflict.spec.ts + missing-inputs unit tests
- S7 honesty (banner, disclaimer, disabled address, no invented wording, no mocked success) → e2e/honesty.spec.ts
- S8 keyboard-only + focus visibility + existing jobs green + no local artifacts → e2e/keyboard.spec.ts + this run

## Producer disclosures carried to G3/G5

- CORS: API has no CORS policy; the e2e harness adds test-origin-only middleware; production proxy/CORS decision is an open orchestrator follow-up.
- Live API emits contract 1.0.0, so the D5 fallback provenance join is the production path; the district-map path is unit-tested on a documented derived v1.1 fixture.
- Producer report: `project-control/reports/M2-T001-producer-report.md` (on the branch).

## Result

**G2 PASS** — every acceptance scenario has an executed, green, reproducible CI check; evidence is remote and durable (run links + artifact).
