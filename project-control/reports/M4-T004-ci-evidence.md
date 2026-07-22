# M4-T004 — CI evidence at frozen SHA 3e45524 (orchestrator-captured)

**Commit:** `3e45524f57459c90c38f28a7a5291034c9240ce6` (branch `task/M4-T004-safeguards`).
**Result:** all **12/12** required checks GREEN (latest run per check).

| Conclusion | Check |
|---|---|
| success | Scan repository for credentials |
| success | api (ruff + pytest) — full 742-test suite incl. 48 new FH safeguards |
| success | api-lock-verify |
| success | api-tooling-lock-verify (seeded verifier from M0-T021) |
| success | context-budget |
| success | contracts (JSON Schema validation) |
| success | contracts-schema-bundle (byte-identical) |
| success | contracts-typegen (byte-identical) |
| success | control-plane (ADR-005) |
| success | exact-production-install |
| success | web (lint + typecheck + build) |
| success | web-e2e (vitest + Playwright) |

**web-e2e note:** the first run of `web-e2e` failed on a single flaky frontend accessibility
focus-timing assertion — `apps/web/e2e/a11y-announcements.spec.ts:169` ("S2: KEYBOARD retry on Confirm —
focus moves to the loading card, then the outcome heading, never body"; `during.isBody` expected false,
got true; 52 passed / 1 failed). M4-T004 changed **only** `services/api/app/rules/**` + tests (no
`apps/web`, no contract), so the failure is unrelated to the frozen code. The failed job was re-run at
the same frozen SHA and passed. No frozen code changed.
