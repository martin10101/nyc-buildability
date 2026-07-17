# M2-T001 — G4 integration and regression evidence (orchestrator-captured)

- **Task:** M2-T001 Priority 4 Property screen
- **Date:** 2026-07-17 (UTC)
- **Merge commit:** `e074a2e` (no-ff merge of `task/M2-T001-property-screen` @ `dd34c7b`); ledger commit `9353466` (CI ran at this head)
- **Recorded by:** orchestrator (evidence-capture per ADR-005)

## CI evidence on main

| Workflow | Run | Commit | Result |
| --- | --- | --- | --- |
| CI (now 6 jobs: api, contracts, control-plane, web, web-e2e + matrix internals) | [29551111567](https://github.com/martin10101/nyc-buildability/actions/runs/29551111567) | `9353466` | completed / **success** |
| secret-scan | [29551111573](https://github.com/martin10101/nyc-buildability/actions/runs/29551111573) | `9353466` | completed / **success** |

Command: `gh run list --commit 9353466e513fdd777d933f242be89911f530d6d5 --json name,status,conclusion` → both `completed/success`.

## G4 checklist

- Full build/lint/type-check/test suite: CI `web` job (eslint, tsc, next build), `web-e2e` (vitest unit + 22 Playwright journeys against the real FastAPI harness over committed official fixtures), `api` (ruff + 142 pytest), `contracts` (schema+fixture validation incl. the v1.1 referential-integrity invariants), `control-plane` — all green on the integrated main tree.
- Contract compatibility: the screen consumes only v1.1-documented keys (G3-verified); contracts job green post-merge.
- No duplicate/contradictory implementations: the API remained untouched (`git diff` on `services/**` vs pre-merge base empty except the one-line test-registry pairing already merged with M1-T006).
- Regression: all pre-existing jobs green; the branch-side runs (29548158336) plus this main run bracket the merge.
- Migrations: none in scope (no DB work).
- Low-storage/cleanup: nothing installed locally at any point (all execution in CI); local by-products limited to git objects; the orchestrator's temp Playwright artifact download (`%TEMP%\m2t001-playwright`, ~16 MB with extraction) deleted at acceptance.
- Performance: within budget — web-e2e job completes in single-digit minutes on the free runner; artifact retention 7 days.

## Result

**G4 PASS.** M2-T001 meets all required gates (G0, G2, G3, G5, G4) — eligible for acceptance.

## Tracked follow-ups fed into the backlog (non-blocking for this task)

- G3 D1–D5 (field labels, responsive journeys, coverage legend, missing-inputs density, post-success invalid-submit UX) → Confirm-screen task inputs.
- G5 C1–C3 (CORS/proxy decision, auth + rate limiting, security headers + https API base) → BLOCKING conditions on any future deploy task (recorded alongside B-001/B-002).
- G5 F2/F3 + G3 D6 (generate-lockfile workflow disposition, ci.yml comment accuracy, journey-count bookkeeping) → hygiene batch.
- G3 D8/G5 C1 duplicate tracking resolved in favor of G5 C1 wording.
