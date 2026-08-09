---
name: rule-eval-two-factor-flag
description: How the M4-T005 draft rule-evaluation surface is flag-gated (env + per-request opt-in) and why the shared e2e server needs it
metadata:
  type: project
---

The internal draft rule-evaluation UI surface (Property screen) is gated by TWO independent factors, both required: the non-public runtime env var `INTERNAL_RULE_EVAL_UI` (read server-side only, never `NEXT_PUBLIC_`, never inlined into the browser bundle) AND a per-request `?ruleeval=on` opt-in. Absent/empty/unknown/`off` → OFF (fail safe). When OFF the panel never renders and the browser issues zero `/rule-evaluation` requests.

**Why:** The Playwright e2e suite runs ONE shared `next start` server with the env flag on. A single-env boolean would render the panel (and fire its background fetch) on EVERY journey, polluting existing API-call-counting specs (e.g. `expect(apiCalls).toBe(0)`). The `?ruleeval=on` opt-in makes non-interference structural, not timing-dependent, so every pre-existing spec is provably unaffected. In production the env gate stays closed, so the opt-in has no effect.

**How to apply:** When reviewing this or similar flag-gated additive surfaces, a "flag off → zero network calls" claim must be proven by a spec that records browser request URLs (see `e2e/rule-evaluation-flag-off.spec.ts`), not merely by "panel absent". To manually see the surface: visit `/property?ruleeval=on` with the env flag set. The e2e harness sets the SERVER flag `INTERNAL_RULE_EVAL_ENABLED` in `e2e/harness/fixture_api.py` and the FRONTEND flag in `playwright.config.ts` webServer env.
