# M2-T001 — G0 definition-of-ready (orchestrator)

- **Task:** Priority 4 — first browser Property screen (real BBL lookup against accepted property-profile API v1.1)
- **Date:** 2026-07-16
- **Reviewer:** orchestrator (G0 is the orchestrator's readiness gate)
- **Origin:** Owner directive 2026-07-16 item 2 (proceed immediately after contract v1.1 acceptance; every listed screen requirement is embedded in the packet outputs/scenarios). Session-handoff queue item 2.

## Checklist

| G0 item | Status |
| --- | --- |
| Objective unambiguous | YES — packet objective + 8 owner requirements mapped into outputs and S1–S8 |
| Dependencies accepted | YES — M1-T005 (API, accepted CP-0009) and M1-T006 (contract v1.1, accepted CP-0011); no other blocker gates this slice. Address lookup explicitly OUT (B-004) with honest-copy requirement instead |
| File scope exclusive | YES — `apps/web/**` + additive ci.yml web job; no other active tasks; `services/**`, `packages/contracts/**`, `render.yaml` forbidden |
| Inputs/outputs defined | YES — packet lists the contract, API behavior, tolerance rules (M1-T005 G3 §5), M1-T006 D5, design system, scaffold, CI |
| Acceptance scenarios | YES — S1–S8 including the UI human-journey pack items (primary, boundary, malformed, no-match, dependency failure, partial data, honesty checks, regression/accessibility) |
| Source documentation | YES — all inputs exist in-repo; no external research required |
| Credentials | NONE required — no secrets, no deploys, no live-credentialed sources. Optional live SODA smoke is tokenless and non-gating |
| Gates assigned | G0 (this), G2 producer self-check, G3 human-journey-reviewer (real browser evidence via CI Playwright traces/screenshots), G4 CI integration, G5 security-reviewer (bundle secrets, honesty markers, no exposure) |
| Execution location / disk | **Critical constraint honored:** owner PC at ~1.67 GB free (below the 4 GB floor) → NO local installs of any kind; source edits only. All npm ci/build/lint/typecheck/unit/Playwright runs in the additive GitHub Actions web job. CI artifacts (traces/screenshots) kept at short retention |
| Cleanup | Nothing heavy lands locally; worktree removed after acceptance; CI artifacts auto-expire |

## Confirmations

- **No production deployment** — `render.yaml` is a forbidden path; the web job builds and tests only; screen is INTERNAL/DEV with a visible banner and the PRD §29 disclaimer.
- **No credentials introduced or required.**
- **No mocked successful property results in the app** — the only fixture usage is the CI test harness running the REAL FastAPI service over committed official-response fixtures through the existing transport seam (same pattern the accepted API tests use), clearly labeled.

## Result

**G0 PASS** — claiming for frontend-engineer with worktree `.claude/worktrees/M2-T001`, branch `task/M2-T001-property-screen`.
