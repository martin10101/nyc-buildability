# G3 Human-Journey Walkthrough Report — M5-T002 (scenario endpoint + property-screen scenario surface)

> Saved VERBATIM by the orchestrator from the human-journey-reviewer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer.

**Reviewer:** human-journey-reviewer (code-walkthrough in lieu of live browser — thin-client policy; app cannot be launched locally)
**Branch / identity:** task/M5-T002-scenario-endpoint, HEAD 2fee786, content identity 31e652a
**Scope reviewed:** AS-7, AS-8, AS-9 especially; plus honesty/consistency/recovery/a11y across all no-scenario and failure states.
**Method:** traced the real analyst journey through source + fixtures + e2e specs; no code modified; no git/CLI/npm/node run.

## VERDICT: PASS

No blocking items. The journey is honest, consistent with the established property-screen and rule-evaluation patterns, and structurally prevents a "verified"/approved reading of a draft number. Four low-severity / informational findings are listed below; none block acceptance. Items that genuinely require the rendered browser are explicitly deferred to the CI web-e2e evidence.

---

## 1. Journey narrative — what the analyst literally sees, per state

### Entry: Property screen with the flag OFF (default posture, AS-7)
The analyst opens `/property`. `app/property/page.tsx` computes `scenarioEnabled = scenarioSurfaceEnabled({ scenario: params.scenario })`, which returns `false` unless BOTH the server-read env flag `INTERNAL_SCENARIO_UI` is a true token AND the request carries `?scenario=on`. With the default, `PropertyLookup` receives `scenarioEnabled={false}`, and `ProfileView` renders `{scenarioEnabled ? <ScenarioPanel/> : null}` → nothing. The panel is never mounted, so its `useEffect`→`fetchScenario` never fires. The `scenario-flag-off.spec.ts` records every request URL and asserts `hits === []` for both no-opt-in and explicit `?scenario=off`. The profile (identity card, coverage, facts, confirm link) is fully usable. **Honest: no scenario UI, no fetch.**

### Flag ON, happy path — preliminary draft cap (AS-8, fixture `preliminary_r5_cap.json`, BBL 1000010100)
After a successful profile, the panel mounts LAST (below every profile section and the "Review and confirm" next-step), loads independently, and does not move document focus (background load). The analyst reads, in order:

- Intro card `<h2>`: **"Draft scenario (internal)"** — "An experimental, unreviewed draft scenario for this property. It surfaces a draft zoning-floor-area cap where a draft rule applies, is never a final determination or a buildable envelope, and does not change the official facts above. This section loads on its own — if it fails, the property profile stays fully usable."
- Result `<h3>`: **"Preliminary draft scenario — requires professional review"**
- Prominent DRAFT banner (bold text + left rule, not color alone): **"DRAFT — not a final legal determination and not a buildable envelope. Produced by an unreviewed draft rule pending qualified-human legal approval. Do not rely on it for acquisition, design, filing, financing, or construction."**
- Coverage badge: exact enum **"conditional"** + non-color symbol ◐ + visually-hidden gloss "Official source fact, not yet professionally reviewed." (Never "verified".)
- Intro line: "A draft rule produced the zoning-floor-area cap below. It is unreviewed and NOT a final determination and NOT a buildable envelope — height, setbacks, yards, and other constraints are unknown (see the coverage map). A qualified New York professional must review it before any reliance."
- Cap callout: "Draft zoning-floor-area cap (surfaced verbatim from the rule trace):" then **15,000** sq ft (bold, 1.25rem), then the verbatim `cap_label`: "DRAFT maximum residential ZONING-FLOOR-AREA CAP under ZR 23-21. NOT gross, net, sellable, or feasible floor area; NOT a buildable envelope. Height, stories, setbacks, yards, lot coverage, open space, parking, and street-wall constraints are UNKNOWN (see coverage matrix). Draft rule (needs_review); requires professional review; NOT Verified."
- Known constraints (`<dl>`): Lot area 10,000 sq ft; Base zoning district R5.
- Reasons list; a collapsible **"Rule-coverage map (what this scenario does and does not cover)"** enumerating every family with `rule_status_today` and "(blocks a buildable envelope)" flags; a collapsible **"Cap rule and source provenance"** exposing rule id `r5-residential-far` (0.1.0-draft, needs_review), output `max_residential_floor_area_sq_ft`, and legal citation section **23-21** with quote, source id, retrieved host, retrieved-at; a collapsible **"Draft-scenario disclaimer (exact wording)"** with the verbatim `not_verified_disclaimer`; and **"Evaluated input"** (BBL by reference, contract versions, input fingerprint).

The cap value is displayed via `formatValue`, which uses `toLocaleString("en-US", { maximumFractionDigits: 20 })` — it only groups digits and truncates no precision, so the surfaced number is the canonical trace value verbatim (15000.0 → "15,000"). No recomputation or relabel anywhere in the component.

### Flag ON, professional-review no-scenario (AS-9, fixture `no_scenario_professional_review.json`, BBL 1000010101)
`classifyScenario` → `professional_review` (scenario_kind=no_scenario, coverage=professional_review_required, professional_review_required=true). Heading **"Professional review required — spatial uncertainty"**; intro "The platform could not confidently establish the spatial inputs a draft scenario needs, so it produced no value and made no guess. The gap is shown, not hidden." **No cap callout is rendered** (`presentation !== "preliminary_cap"`), so no fabricated number; `scenario.spec.ts` asserts `scenario-cap` count 0. Coverage badge "professional_review_required" (!).

### Unsupported (`unsupported_family.json`) and conflict (`no_scenario_conflict.json`)
- unsupported → heading **"No applicable draft rule for this property"**, "The platform has no draft rule that applies to this property, so no draft scenario is produced. This is shown explicitly rather than left silent." Badge "unsupported" (∅).
- data_conflict → heading **"Conflicting draft rules or data — professional review required"**, "More than one draft rule or a data conflict is present. Which rule governs is a legal determination, so the platform produced no scenario value and picked no winner." Badge "data_conflict" (≠).

### Failure / recovery states (AS-9)
- `feature_unavailable` (backend flag off → generic 404, no state, no correlation id) → **"Draft scenario is not available here" / "…not enabled in this environment. The property profile above is complete and unaffected…"** No retry button (correct — retry is pointless), never blocks the profile.
- `network_error` / `client_timeout` / `upstream_failure` (rate_limited/source_unavailable/timeout/schema_drift) / `internal_error` / `server_contract_error` / `validation_failure` / `unexpected_response` → each has a specific plain-language heading + body, a **"Retry draft scenario"** button that re-issues only the scenario fetch, and (where present) a bounded correlation id. Every copy string reassures "the property profile above is unaffected." `no_match` (404) and `validation_error` (422) show a message (+ code / correlation id) and no retry — correct, since re-requesting the same BBL re-yields the same result.

### Accessibility as coded
A single persistent `role="status" aria-live="polite" aria-atomic` region (`scenario-announcer`) emits exactly one arrival announcement (e.g. "Draft scenario loaded: a preliminary draft zoning-floor-area cap that requires professional review; not a buildable envelope."). Announcement clears while loading so a repeated identical outcome re-announces. Background load does NOT steal focus; focus moves to the scenario heading only after a user-initiated Retry (`pendingFocus` ref + `data-scenario-heading`). Coverage status is always enum value + symbol + SR gloss, never color alone. Heading hierarchy is h2 (intro) → h3 (result/failure/loading). This mirrors the accepted M4-T005 rule-evaluation surface guarantee-for-guarantee.

---

## 2. Honesty guarantees confirmed (positive findings)

- **"Verified" is structurally impossible to reach the screen.** `scenario-contract.ts` `SCENARIO_COVERAGE_STATUSES` excludes `verified` and is pinned to the generated `DraftCoverageStatus` union by a two-way `MutuallyEqual` compile-time proof (tsc fails on drift). `validateScenarioDocument` runs `checkEnum` on `coverage_status` before render, so a 200 body carrying `verified` becomes a `validation_failure` and nothing is drawn. Backend independently validates before emit (`validate_scenario_document`) and never labels verified.
- **Cap is never recomputed/relabeled.** Frontend displays `draft_zoning_floor_area_cap_sq_ft` and `cap_label` verbatim; `formatValue` preserves precision. Backend consumes `build_scenario` READ-ONLY and surfaces the canonical rule_evaluation trace value.
- **No no-scenario state dead-ends or hides a reason.** Every family renders a plain-language heading + intro + the backend-produced `reasons`, plus the coverage matrix showing what is MISSING. `feature_unavailable` is benign and non-blocking. Recoverable faults carry Retry.
- **No injection surface reaches the human path.** The route takes only the `bbl` path param; the client sends only the encoded bbl (`fetchScenario`), no body, no query-supplied facts.

---

## 3. Numbered findings

1. **[Low / gap]** The `"missing"` presentation template (`ScenarioPresentation` fallback; heading "No draft scenario — a required input is missing") has **no canonical fixture** under `packages/contracts/fixtures/valid/scenario/` and is only reachable as `classifyScenario`'s final fallthrough (`lib/scenario.ts:433-434`; headings/intros at `ScenarioResult.tsx:33,50`). AS-3 lists "missing critical constraint" as a no-scenario family, but I cannot confirm from fixtures that the backend actually emits a document classifying to `missing` rather than folding into `unsupported`/`professional_review`. **Recommend** the orchestrator confirm from the API acceptance pack that a "missing critical constraint" case produces a document that classifies to `missing` (or that the family is deliberately represented by `unsupported`). Non-blocking.

2. **[Low / visual hierarchy]** `ScenarioResult.tsx:71-73` renders `cap_label` — which carries the strongest "NOT a buildable envelope / NOT Verified" qualifiers — in muted `failure-meta` styling directly beneath the large bold cap value. Honesty is preserved because the DRAFT banner and intro already carry the plain-language caveat prominently, and this mirrors accepted patterns, but the strongest caveat sitting in the smallest type under the biggest number is a minor hierarchy smell. Non-blocking.

3. **[Info / consistency]** The exact `not_verified_disclaimer` string sits inside a collapsed `<details>` "Draft-scenario disclaimer (exact wording)" (`ScenarioResult.tsx:141-148`). AS-8 requires it "surfaced"; it is one keystroke away and the plain-language equivalent is prominent — identical to the ACCEPTED rule-evaluation surface (`RuleEvaluationResult.tsx:62-72`). Recorded as intended, not a defect.

4. **[Info / a11y]** Three polite `role="status"` regions can now coexist on one screen (property `outcome-announcer`, optional `rule-eval-announcer`, `scenario-announcer`). This matches the accepted M4-T005 pattern; polite queueing avoids collision. Actual SR timing deferred to live/CI.

---

## 4. Could NOT be judged without the live browser — deferred to CI web-e2e evidence

- Rendered focus behavior: background scenario load never steals focus from the profile heading; Retry moves focus to the scenario heading. (Coded correctly; asserted by `scenario.spec.ts` a11y test — defer to the CI trace.)
- Actual no-render / zero-fetch with flag off and with `?scenario=off` kill switch. (Asserted by `scenario-flag-off.spec.ts` recording request URLs — defer.)
- Cap rendered verbatim "15,000", coverage text "conditional", provenance drill-down showing "23-21". (`scenario.spec.ts` AS-8 — defer to CI screenshots/trace.)
- Professional-review path shows no fabricated value (`scenario-cap` count 0), and recoverable network failure → benign failure state → Retry restores the result, profile stays usable. (`scenario.spec.ts` AS-9 — defer.)
- Design-system contrast tokens / actual visual contrast and responsive layout. (Uses `status-badge`, `card`, `provenance-details` tokens — defer to visual evidence.)
- Real screen-reader announcement wording/timing across the three live regions.

Per `docs/PROJECT_CONTROL_PROTOCOL.md` / ADR-005, these are not BLOCKED items — they are standard live-browser evidence the CI Playwright suite (`scenario.spec.ts`, `scenario-flag-off.spec.ts`) produces; the orchestrator should confirm those specs are green in the M5-T002 CI run before recording the gate.

---

**Reviewer files consulted (absolute):**
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t064\apps\web\src\app\property\page.tsx`, `...\components\property\PropertyLookup.tsx`, `...\components\property\CoverageBadge.tsx`, `...\components\property\OutcomeAnnouncer.tsx`, `...\components\scenario\ScenarioPanel.tsx`, `ScenarioResult.tsx`, `ScenarioFailure.tsx`, `...\src\lib\scenario.ts`, `scenario-contract.ts`, `coverage.ts`, `format.ts`, `...\components\rule-evaluation\RuleEvaluationPanel.tsx`, `RuleEvaluationResult.tsx`, `...\e2e\scenario.spec.ts`, `scenario-flag-off.spec.ts`, `...\playwright.config.ts`, `...\services\api\app\api\v1\scenario.py`, `...\app\config.py`, `...\packages\contracts\fixtures\valid\scenario\{preliminary_r5_cap,no_scenario_professional_review,unsupported_family,no_scenario_conflict}.json`.

**Verdict: PASS** (4 low/informational findings above; none blocking).
