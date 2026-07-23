# M0-T022 — Producer Report (Owner Mission-Control Dashboard, V1)

**Task:** Read-only owner observability dashboard over project-control.
**Branch:** `task/M0-T022-owner-dashboard` (worktree `.claude/worktrees/M0-T022-dashboard`).
**Frozen impl SHA:** `6c501aaf1b898a11ebf1843090c6b04dca54ebb7`
**CI:** run 29976490909 — **all 11 jobs success** (https://github.com/martin10101/nyc-buildability/actions/runs/29976490909)
**Status:** producer self-check complete; submitting to independent gates. **Not accepted.**

## What was built

A strictly read-only `/dashboard` route in `apps/web` that observes the existing control plane
without weakening, duplicating, or mutating it. One new canonical metadata file
(`project-control/product-map.json`) maps engineering tasks to owner-facing product systems and
carries the explicit weights. Two deterministic, auditable progress numbers (Engineering
completion, Launch readiness) are computed from ledger + weights, each with a reproducible
"How is this calculated?" breakdown. Supplemental live GitHub status (public repo, no token) is
kept strictly separate from canonical project state. See `docs/DASHBOARD.md`.

## Architecture (read-only observer)

- **Pure engine** `apps/web/src/lib/dashboard/{types,parse,membership,model,progress,health,currentWork,activity,launch,github,assemble}.ts` — no React/Next/fs/network; independently unit-tested.
- **IO edges** `loader.server.ts` (fs read), `githubClient.ts` (cached public GitHub), `server.ts` (composition).
- **UI** `apps/web/src/components/dashboard/*` + `apps/web/src/app/dashboard/{page,dashboard.css}` — light theme (existing tokens), zero new npm deps, internal-flag gated, INTERNAL banner.
- **Metadata + gate** `project-control/product-map.json` + `product-map.schema.json` + `tools/validate_product_map.py` + `tools/test_product_map.py` + additive `product-map` CI job.

## Owner-directive compliance (2026-07-23)

1. Whole-% only in the headline; exact value + breakdown in detail. ✓ (`ui.tsx` PercentStat)
2. Reproducible from repo state; "How is this calculated?" breakdown per number. ✓ (`progress.ts`, PercentStat)
3. Health computed separately from completion. ✓ (`health.ts`; test: accepted-but-RED system)
4. Unknown/corrupt/contradictory → UNKNOWN/DEGRADED, never coerced to 0/complete/healthy. ✓ (`parse.ts`, `progress.ts`, `assemble.ts`; tests)
5. Current work from lifecycle state, not commits; all active + deterministic primary. ✓ (`currentWork.ts`)
6. "What changed" = control-plane events; raw commits excluded. ✓ (`activity.ts`)
7. "Biggest things preventing beta" derived from launch-critical deps + unmet gates, not an AI list. ✓ (`launch.ts`)
8. Historical honesty: canonical current status; roster/status contradiction flagged. ✓ (`model.ts`; test)
9. GitHub never corrupts canonical state (files authoritative; GitHub supplemental). ✓ (`github.ts`/`githubClient.ts` isolated; test: failed CI leaves numbers unchanged)
10. Framework-independent, independently testable engine. ✓ (pure core; `__tests__/engine.test.ts`)

## Acceptance-scenario evidence

| AS | Evidence |
|---|---|
| AS-1 product-map contract | `tools/test_product_map.py` (13 tests) + `product-map` CI job green |
| AS-2 deterministic parse | `engine.test.ts` real-ledger smoke + parse tests |
| AS-3 owner status mapping | `parse.ts` DEFAULT_OWNER_STATUS + unknown→UNKNOWN; `engine.test.ts` |
| AS-4 gate + acceptance-eligibility | `model.ts`; `engine.test.ts` (M0-T002 eligible, M1-T002 not; producer-gate ignored) |
| AS-5 engineering completion | `engine.test.ts` hand-computed 72.5→73% |
| AS-6 launch readiness (G6 cap) | `engine.test.ts` hand-computed 32.5→33%, diverges from engineering |
| AS-7 dependency + current work | `currentWork.ts`; `engine.test.ts` |
| AS-8 blocker detection | `engine.test.ts` (only open B-900; resolved excluded) |
| AS-9 biggest-things | `engine.test.ts` (deterministic kinds + ranks) |
| AS-10 activity feed | `engine.test.ts` (today = accepted/started/gate_pass; pr_merged present) |
| AS-11 GitHub parse + stale | `engine.test.ts` (parse; stale fallback retains last-known) |
| AS-12 fail-safe unknown | `engine.test.ts` (empty raw → unknown, null %, no throw) |
| AS-13 read-only + internal + security | `config.ts` flag (fail-safe off) + `dashboardEnabled` test; page 404 when off; JSX auto-escape; no secrets; **G5** |
| AS-14 human-journey + a11y + mobile + honesty | `e2e/dashboard.spec.ts` (tabs, map, drawer, keyboard, honesty) + **G4 human-journey** |
| AS-15 regression + zero new deps | full CI (web, web-e2e, api, contracts, control-plane, product-map) green; package.json/lock unchanged |
| AS-16 calc transparency + precision | PercentStat breakdown; whole-% headline; **G3/G4** |
| AS-17 health≠completion; GitHub isolation | `health.ts`; `engine.test.ts` (failed CI leaves %s unchanged) |
| AS-18 UNKNOWN + historical honesty | `engine.test.ts` (unknown status → partial/null; roster contradiction flagged) |

## CI evidence (frozen SHA)

Recorded/verified at the frozen head — jobs: `web` (lint+typecheck+build), `web-e2e`
(vitest + Playwright incl. `dashboard.spec.ts`), `api`, `contracts`, `contracts-typegen`,
`contracts-schema-bundle`, `control-plane`, `product-map`, `secret-scan`, `context-budget`.
_(Exact run id/conclusions appended when the frozen SHA's run is green.)_

## Files created / modified

Created: `project-control/product-map.json`, `product-map.schema.json`,
`tools/validate_product_map.py`, `tools/test_product_map.py`,
`apps/web/src/lib/dashboard/*` (15), `apps/web/src/components/dashboard/*` (8),
`apps/web/src/app/dashboard/{page.tsx,dashboard.css}`,
`apps/web/src/test-support/dashboard/fixtures.ts`, `apps/web/e2e/dashboard.spec.ts`,
`docs/DASHBOARD.md`, plus this report + G0/G2 reports.
Modified (additive): `.github/workflows/ci.yml` (new `product-map` job),
`apps/web/playwright.config.ts` (e2e flag; scope amendment recorded in packet).
Unchanged: all existing product screens/contracts, `services/api/**`, `packages/contracts/**`,
`apps/web/package.json`/lockfile (no new dependency), `project-control/master_plan.json`,
`tools/project_control.py`.

## Current limitations (V1, intentional)

No historical progress deltas (no snapshot store), no auth (internal flag only), no live AI
summaries (static owner metadata), no Render provisioning (local-first + Render-ready), no writes.

## Honesty / holds

Read-only observer; nothing Published/Verified; M4 rules shown as draft/needs-review; no
control-plane mutation; no merge to protected main outside the PR+CI+gate flow; expansion/GDS
holds untouched.
