# M4-T005 Phase 3 — Frontend rule-evaluation surface (producer report)

Producer evidence only. CI is the validator (thin client: npm/node/tsc/vitest/playwright
never run locally — `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`). The `web`
(lint+typecheck+build) and `web-e2e` (vitest+Playwright) jobs validate everything after the
orchestrator pushes. Worktree synced to `86f4b9f` (`git reset --hard 86f4b9f`; `git log --oneline -3`
showed `86f4b9f M4-T005 Phase 2` on top). No other git command run; `tools/project_control.py` not run.

## What was built

An additive, flag-gated draft rule-evaluation surface on the EXISTING internal Property screen. It
surfaces the Phase-2 endpoint's result with six explicit UI states, full accessibility, provenance
drill-down, and a defense-in-depth no-fetch guarantee. The existing property-profile fetch/state
behavior is untouched (extended, never altered).

## How the generated contract types are consumed

Identical mechanism to the accepted property-profile path: a **type-only relative import** erased at
build time (no copy script, no path alias). `src/lib/contract.ts` imports
`../../../../packages/contracts/generated/property_profile`; the new
`src/lib/rule-evaluation-contract.ts` imports `../../../../packages/contracts/generated/rule_evaluation`
the same way and re-exports the generated types. No sync/copy under `apps/web` was needed, so no
out-of-scope file was touched for typegen. Runtime enum arrays are two-way `MutuallyEqual`-locked to
the generated unions (same pattern as `contract.ts`), so drift fails `tsc`.

## Flag mechanism (defense in depth; two factors)

- **Env gate (primary):** `INTERNAL_RULE_EVAL_UI` — deliberately NOT `NEXT_PUBLIC_`, so Next never
  inlines it into the browser bundle and it is read at RUNTIME by the Server Component
  (`app/property/page.tsx`), which passes a plain boolean into the client tree. Absent/empty/unknown →
  OFF (fail safe), mirroring the server's `internal_rule_eval_enabled()` token rule.
- **Per-request opt-in (second factor):** the surface renders only when the request also carries
  `?ruleeval=on`. Absent or `?ruleeval=off` → OFF. This keeps the experimental surface silent unless
  deliberately requested, and — crucially — lets the shared single-server e2e harness enable the
  surface for the rule-eval journeys WITHOUT rendering it (or issuing its fetch) on any other journey,
  so **every existing spec is provably unaffected** (they never opt in). In production, where the env
  gate is closed, the opt-in has no effect at all.

When the resulting boolean is false the client never renders the panel and never issues the fetch.
`PropertyLookup` gained one optional prop (`ruleEvalEnabled`, default false); the panel is rendered
last inside `ProfileView` so it never alters the existing layout or the Property→Confirm focus/tab flow.

## The six UI states and reused components

Classification (`classifyRuleEvaluation`) reads ONLY backend discriminators (`rule_conflict.conflict`,
`coverage_status`, `fail_safe`, `fail_safe_reason`, `professional_review_required`) — no legal/numeric
computation in React. States 1–5 are derived from the 200 document; State 6 is a non-200 outcome.

1. **Applicable draft** — `coverage_status=conditional`, outputs shown, DRAFT-framed. `RuleEvaluationResult`.
2. **Not applicable / unsupported** — `coverage_status` `unsupported`/`not_applicable`. `RuleEvaluationResult`.
3. **Missing evidence** — `fail_safe` with `spatial_intersection_absent`/`spatial_context_incomplete`
   (the LIVE default endpoint path). `RuleEvaluationResult`.
4. **Conflicting rules** — typed `rule_conflict.conflict=true`, competing rules listed visibly, no value. `RuleEvaluationResult`.
5. **Spatial uncertainty** — split-lot `geometry_uncertain`/`data_conflict`; share ranges shown as
   `min–max (point …)`, NEVER collapsed. `RuleEvaluationResult`.
6. **Network / server failure** — recoverable non-200 outcome; the property profile stays fully usable;
   Retry re-issues only the draft request. `RuleEvaluationFailure`.

Reused existing components/patterns: `CoverageBadge` (exact enum value + non-color symbol + SR gloss —
never color-alone), `OutcomeAnnouncer` (given an additive optional `testId` so a second live region can
coexist), the native `<details>` provenance-disclosure pattern (mirroring `ProvenanceDisclosure`, which
is `SourceFact`-typed so it cannot be reused verbatim for the rule-eval citation shape), the
`card`/`failure-state`/`failure-title`/`failure-meta`/`loading-stages`/`missing-list` styles, and the
`LoadingStages` staged-loading pattern.

## Never-Verified discipline

No visible string presents the result as Published, Verified, legally final, or guaranteed buildable.
The prominent framing is a bold, border-emphasized (shape, not color) "DRAFT — not a final legal
determination" banner plus the coverage badge. The exact server `not_verified_disclaimer` (which
contains the word "Verified") is surfaced in a REACHABLE, labeled collapsed `<details>` — mirroring the
accepted property-profile coverage-policy pattern, which keeps that word out of default `body.innerText`
so the honesty invariant holds even where the surface renders.

## Accessibility

Keyboard-operable end to end (native `<details>`, standard buttons). Status changes announced through
the panel's OWN persistent `role="status"` live region (`rule-eval-announcer`, distinct testId).
Deliberate focus discipline: on the BACKGROUND initial load the panel does NOT move document focus (so
it never competes with the property-profile focus flow the a11y specs assert); focus moves to the
panel heading ONLY after a user-initiated Retry. Provenance drill-down is reachable and labeled.

## Files created / modified (all within allowed scope)

Created:
- `apps/web/src/lib/rule-evaluation-contract.ts` — generated-type re-export + runtime 200-body validator (rejects `verified`).
- `apps/web/src/lib/rule-evaluation.ts` — flag helpers, (status,state) matrix, `fetchRuleEvaluation`, classifier, announcements.
- `apps/web/src/components/rule-evaluation/RuleEvaluationPanel.tsx` — client orchestrator (idle→loading→outcome, seq+AbortController, retry, announce, focus).
- `apps/web/src/components/rule-evaluation/RuleEvaluationResult.tsx` — the five document-derived states + provenance + disclaimer.
- `apps/web/src/components/rule-evaluation/RuleEvaluationFailure.tsx` — the sixth state + feature-unavailable + result envelopes.
- `apps/web/src/components/rule-evaluation/__tests__/rule-evaluation.test.tsx` — component tests.
- `apps/web/src/lib/__tests__/rule-evaluation.test.ts` — client/flag/classifier tests.
- `apps/web/src/test-support/rule-evaluation-fixtures.ts` — loads committed contract fixtures + a derived conflict doc.
- `apps/web/e2e/rule-evaluation.spec.ts` — human journeys.
- `apps/web/e2e/rule-evaluation-flag-off.spec.ts` — no-call spec.

Modified (additive):
- `apps/web/src/app/property/page.tsx` — async Server Component reads the flag + `?ruleeval` and passes a boolean prop.
- `apps/web/src/components/property/PropertyLookup.tsx` — optional `ruleEvalEnabled` prop; renders the panel LAST (existing fetch/state untouched).
- `apps/web/src/components/property/OutcomeAnnouncer.tsx` — optional `testId` prop (default "outcome-announcer"; existing usages unchanged).
- `apps/web/src/lib/api.ts` — NOT modified in the end (reused `apiBaseUrl` export as-is; no behavior change).
- `apps/web/e2e/harness/fixture_api.py` — enables the SERVER flag for the test process and overrides the substrate provider with the faithful M2-T013 shapes from the accepted phase-2 pack.
- `apps/web/playwright.config.ts` — sets `INTERNAL_RULE_EVAL_UI=1` on the `next start` webServer (see deviation note).

`src/lib/contract-matrix.ts` was NOT modified — the rule-eval matrix differs (it adds the `(404, null)`
feature-unavailable pair), so a self-contained matrix lives in `rule-evaluation.ts` rather than
overloading the property matrix.

## Test inventory (what each proves)

Client (`src/lib/__tests__/rule-evaluation.test.ts`):
- env-token table + absence → flag on/off; surface gate OFF by default, OFF with env-only, ON only with env AND opt-in (the no-fetch guarantee at the gate).
- documented (status,state) pairs incl. BOTH 404 meanings; `(500,no_match)`/`(200,no_match)` rejected structurally.
- every envelope → outcome: valid 200→evaluation; verified-200→validation_failure; generic 404→feature_unavailable; 404 no_match; 422 validation_error; 503/504/502 upstream; 500 internal_error; 500 internal_contract_error→server_contract_error; undocumented 500+no_match→unexpected_response; browser failure→network_error; pre-aborted→aborted.
- classifier → correct presentation for all five documents (conflict highest priority).
- runtime validation accepts all five committed shapes; announcements never say verified/best and are empty for aborted.

Component (`src/components/rule-evaluation/__tests__/rule-evaluation.test.tsx`):
- each of the five document-derived states renders its own heading + DRAFT banner.
- never a `.status-verified` badge; the exact "Verified" disclaimer lives in the reachable `<details>`.
- split-lot share ranges preserved (`0.55–0.65`, `0.35–0.45`), never collapsed.
- rule conflict surfaced visibly with competing rules and NO outputs.
- provenance drill-down (`<details>`) reachable with input fingerprint + citation `23-21`.
- draft outputs shown for the applicable draft.
- sixth state: recoverable network failure with a working Retry; benign feature-unavailable with no Retry.
- panel loads independently and announces through its own live region; recovers when Retry succeeds.
- **PropertyLookup gating:** disabled → no panel AND no `/rule-evaluation` request; enabled → panel mounts AND the `/…/rule-evaluation` request fires.

e2e (`e2e/rule-evaluation.spec.ts`, real API + real evaluator via the substrate seam):
- AS-3 applicable-draft journey: DRAFT framing, `conditional`, output `1.5`, provenance citation `23-21`, profile stays usable.
- AS-8 split-lot spatial-uncertainty journey (F05 `1000010010`): share ranges preserved.
- AS-6 default no-substrate journey: professional-review fail-safe, no fabricated value.
- recoverable failure: only the rule-eval request fails; profile stays usable; Retry reaches the result.
- a11y: two distinct live regions; the background load never steals focus from the profile heading; provenance disclosure is keyboard-reachable.

e2e (`e2e/rule-evaluation-flag-off.spec.ts`):
- no opt-in → surface absent AND zero `/rule-evaluation` requests recorded by the browser.
- `?ruleeval=off` kill switch → same.

Existing property-profile specs are unchanged and unaffected (they never opt in, so the panel never
renders on their journeys; the `OutcomeAnnouncer` testId default is preserved).

## Deviations / decisions the orchestrator must weigh

1. **`playwright.config.ts` edit (outside the enumerated allowed-paths list).** Enabling the FRONTEND
   flag for the e2e `next start` server has no other home (the server env cannot be set from
   `e2e/**`, and `.github/**`/`package.json` are forbidden). The change is a single test-only
   `env: { INTERNAL_RULE_EVAL_UI: "1" }` on the existing webServer — squarely "wiring the harness" as
   the packet instructs. If the gate deems this out of scope, the alternative is a blocker: the e2e
   rule-eval specs cannot run without it. The SERVER flag is set inside `e2e/harness/fixture_api.py`
   (in scope).
2. **Two-factor flag (env + `?ruleeval=on`) instead of a single env boolean.** Chosen because the
   shared single Playwright server would otherwise render the panel on EVERY journey, and the panel's
   background fetch would pollute existing API-call-counting specs (e.g. `client-hardening`
   `expect(apiCalls).toBe(0)`), violating "existing specs must pass unchanged." The opt-in makes
   non-interference structural rather than timing-dependent, and is strictly MORE conservative than a
   single boolean. Human-walkthrough note: visit `/property?ruleeval=on` to see the surface.
3. **Substrate fidelity.** The e2e harness substrate dicts are copied verbatim from the accepted
   phase-2 acceptance pack (`services/api/tests/api/test_rule_evaluation_api.py` `_pair`/`_substrate`),
   which prove those exact shapes drive the real builder+evaluator to applicable-draft / split-lot
   results. No rule-evaluation body is hand-written; the whole route/builder/evaluator/serializer/
   strict-validate path is exercised.
4. **CI is the validator.** npm/node/tsc/vitest/playwright were not run locally (thin-client policy).
   TypeScript was written to mirror the existing hardened patterns exactly; the `web` and `web-e2e`
   jobs must confirm.

No blockers. Requested status: awaiting_gate.
