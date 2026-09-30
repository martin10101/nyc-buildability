---
name: internal-surface-two-flag-gate
description: Internal enrichment surfaces (rule-evaluation, scenario) render only under TWO conditions — server-read env flag AND per-request ?opt-in; don't misread "flag on, nothing renders"
metadata:
  type: project
---

Internal property-screen enrichment surfaces (M4-T005 rule-evaluation panel, M5-T002 scenario panel) are gated by TWO independent conditions that BOTH must hold before anything renders or any fetch fires:

1. ENV flag, server-read only, NOT `NEXT_PUBLIC_`-prefixed (e.g. `INTERNAL_SCENARIO_UI`, `INTERNAL_RULE_EVAL_UI`) — the Server Component (`app/property/page.tsx`) reads it once per request and passes a plain boolean into the client tree, so it never leaks into the browser bundle. Absent/empty/unknown -> off (fail safe).
2. PER-REQUEST opt-in query param (e.g. `?scenario=on`, `?ruleeval=off` kill switch). Default off.

There is ALSO a separate BACKEND server flag (`INTERNAL_SCENARIO_ENABLED`) gating the API route itself; when the frontend surface is on but the backend flag is off, the route returns generic `404 {"detail":"Not Found"}` which the client maps to the benign `feature_unavailable` state.

**Why:** three distinct booleans (frontend env, per-request opt-in, backend env) means a reviewer can see "flag configured" yet correctly observe no render — that is intended, not a bug.

**How to apply:** For Playwright e2e journeys to render these surfaces you need BOTH `apps/web/playwright.config.ts` webServer `env: { INTERNAL_*_UI: "1" }` AND the test navigating with `?scenario=on`, PLUS the harness (`e2e/harness/fixture_api.py`) setting the backend `INTERNAL_*_ENABLED`. The flag-off spec proves no-render/no-fetch regardless of wiring. Don't flag "surface missing" without checking all three gates.

Related: [[playwright-artifact-evidence]].
