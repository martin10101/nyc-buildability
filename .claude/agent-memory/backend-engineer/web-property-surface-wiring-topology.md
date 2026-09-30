---
name: web-property-surface-wiring-topology
description: Where an optional property-screen panel (rule-eval / scenario) is actually wired, and which files a frontend-surface task must include in allowed_paths
metadata:
  type: project
---

An optional draft surface on the Property screen (rule-evaluation, scenario, …) is NOT rendered by
`apps/web/src/app/property/page.tsx`. The page is a Server Component that only computes the feature flag
and passes a boolean prop. The actual panel render happens inside the client component
`apps/web/src/components/property/PropertyLookup.tsx` (its `ProfileView` renders
`{ruleEvalEnabled ? <RuleEvaluationPanel .../> : null}` after a successful profile lookup, using
`profile.identity.bbl`).

**Why:** the BBL only exists in `PropertyLookup`'s internal post-lookup client state, so any panel needing
the looked-up BBL must be rendered from there. `page.tsx` can't pass a new prop to `PropertyLookup` without
`PropertyLookup` declaring it (else `tsc` fails on the unknown prop).

**How to apply:** a task that adds a flag-gated property-screen panel MUST have BOTH
`apps/web/src/app/property/page.tsx` AND `apps/web/src/components/property/PropertyLookup.tsx` in its
allowed_paths, plus (for e2e render) `apps/web/playwright.config.ts` (the web-server frontend flag lives in
`webServer.env`, e.g. `INTERNAL_RULE_EVAL_UI: "1"`; a runtime non-public var is picked up by `next start`
without a rebuild — `NEXT_PUBLIC_*` would require it at `next build` time instead). The e2e API harness
(`apps/web/e2e/harness/fixture_api.py`) sets the SERVER endpoint flag and can be extended additively; a new
route that reuses the existing `get_pluto_fetcher` / `get_spatial_substrate_provider` seams needs no other
harness change. If those files are missing from allowed_paths (M5-T002 packet listed only `app/property/**`),
the surface can be fully built+unit-tested but the property-screen render + e2e cannot be wired in scope —
request an allowed_paths amendment (M0-T077 precedent) rather than editing outside scope.

Related: [[socrata-pluto-gotchas]], [[agent-supervisor-rotation-and-model-machinery]].
