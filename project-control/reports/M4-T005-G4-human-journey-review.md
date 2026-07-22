# G4 UI Human-Journey + Accessibility Gate Report — M4-T005

- **Task:** M4-T005 (draft rule-evaluation frontend surface), PR #84
- **Frozen SHA:** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (confirmed via `git reset --hard` + `git rev-parse HEAD`)
- **Reviewer:** human-journey-reviewer (read-only; no production edits, no control CLI, no git writes)
- **Environment:** thin client — npm/Playwright cannot run locally. Walkthrough is a rigorous static read of the frontend + e2e/component specs, relying on the CI `web-e2e` run at the frozen SHA (25/25 green, installed-wheel) as executed-journey evidence.
- **Verdict:** **PASS**

All six states are honest, programmatically distinct, keyboard-operable, and announced; Never-Verified discipline holds; the surface is optional enrichment that never blocks the profile; the defense-in-depth no-call guarantee is proven by a request-recording spec. No blocking defects. Two LOW, non-blocking observations for the record only.

## Per-state findings (file:line + proving test)
1. **Applicable draft** — `RuleEvaluationResult.tsx:267-284`, heading `:34` "Draft determination — requires professional review"; id `rule-eval-state-applicable_draft`. Proven by e2e AS-3 `rule-evaluation.spec.ts:25-59` (DRAFT banner, `conditional`, output `max_residential_far`=1.5, citation `23-21`, profile usable) + component tests.
2. **Not-applicable / unsupported** — `:285-286` reasons only, no outputs. Proven by classifier `rule-evaluation.test.ts:227-229` + component state test.
3. **Missing evidence** — `:287-297` fail-safe reason + reasons (the LIVE default endpoint path, no substrate wired). Proven by e2e AS-6 `:82-94` + classifier `:230-232`.
4. **Conflicting rules** — `:298-304, 235-257` competing rules with effective ranges; `DraftOutputs` structurally NOT rendered so no value can appear; classifier gives conflict highest priority. Proven by component test `rule-evaluation.test.tsx:73-80` (competing rules shown AND outputs null) + classifier priority test.
5. **Spatial uncertainty** — `:200-233` (`CandidateShare`) renders `min–max (point estimate …)`; never collapses a range to the point; no `DraftOutputs`. Proven by e2e AS-8 `:61-80` (0.55–0.65, 0.35–0.45 preserved) + component test.
6. **Network / server failure** — `RuleEvaluationFailure.tsx` renders non-200 as a separate section; recoverable faults carry Retry; `aborted` renders nothing. Proven by e2e recoverable journey `:96-122` (only rule-eval request fails; `confirm-link` stays visible; Retry reaches result) + component tests.

## Never-Verified framing — honest
- No Published/Verified/legally-final/guaranteed-buildable copy. Prominent DRAFT banner `RuleEvaluationResult.tsx:343-355` ("DRAFT — not a final legal determination… Do not rely on it…").
- Generated contract vocabulary excludes `verified`; a 200 with `coverage_status:"verified"` fails client validation and can never render (`rule-evaluation-contract.ts:63-71, 302`; test `:121-130`).
- The server disclaimer string (contains "Verified") is kept out of default innerText, surfaced only in a reachable labeled collapsed `<details>`; proven by `rule-evaluation.test.tsx:49-61`.
- Certainty never color-alone: `CoverageBadge.tsx:9-18` shows exact enum value + non-color symbol + SR gloss.

## Optional enrichment — never breaks the profile
Panel rendered LAST inside `ProfileView`, only when enabled (`PropertyLookup.tsx:160-164`); loads independently; failure renders a sibling section and never unmounts the profile. e2e `:113-121` asserts `confirm-link` visible during a rule-eval failure and Retry recovers.

## Accessibility — sound
- Keyboard-operable end to end (native `<details>`/`<button>`); e2e a11y journey is keyboard-only (`:124-158`).
- Live-region: panel owns a persistent `role="status" aria-live="polite"` with distinct `data-testid="rule-eval-announcer"`; message cleared while loading so repeats re-announce; no "verified/best" copy.
- Focus discipline: background arrival does NOT move focus (pendingFocus only on user Retry); profile keeps its focus target; e2e `:144-150` asserts focus remains on the profile heading.
- Provenance drill-down reachable + labeled: summary "Evaluated input and source provenance"; proven by e2e `:153-157` + component test.

## Defense-in-depth flag — zero calls when disabled
Server Component reads non-public `INTERNAL_RULE_EVAL_UI` at runtime + requires `?ruleeval=on`; when false the panel never mounts and `fetchRuleEvaluation` is never invoked. The no-call guarantee is proven by RECORDING browser request URLs: `rule-evaluation-flag-off.spec.ts:22-51` asserts `hits.toEqual([])` for both "no opt-in" and `?ruleeval=off`.

## Non-blocking observations (LOW — record only)
- **LOW-1 (clarity):** spatial-uncertainty shows the point estimate alongside the range; a skimming reader could anchor on the point value. Acceptable; range is primary and labeled.
- **LOW-2 (robustness):** `classifyRuleEvaluation` has no explicit branch for a top-level `coverage_status === "data_conflict"` unless `fail_safe`/`fail_safe_reason` is also set — would fall through to `applicable_draft`. In practice the backend pairs `data_conflict` with a fail-safe reason (CI green confirms), so theoretical. Future-hardening note only.

**Final verdict: PASS.** No required corrections. LOW-1/LOW-2 are optional future-hardening notes.
