# M5-T149 part A — producer report (the architect-facing answers slice)

Producer: frontend-engineer, an AI agent. Not a human or professional review. This is the builder's
own report; independent G2/G3/G4 review is the orchestrator's to arrange.

## Scope

Part A of M5-T149: the answers panel and its pieces — the identity line, the context strip, the
shared conditions (stated once), the three answers (label → value/unavailable with its gap kind →
one exception → Details), the on-demand ResultDetails, the detailed scope summary, and the
two-column desktop layout that composes the whole slice. Part B owns the building options and
Part C owns the Results window, the form and the browser tests.

## Files changed (all inside the packet's allowed_paths)

- `apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx` — composition: identity first,
  context strip, shared conditions, the three answers (left region); the detailed scope and Part B's
  `FirstBuildingOptions` (right region); the completeness line as a footer. New inline `IdentityLine`
  (lot, program, floor height — read from the document scope).
- `apps/web/src/components/architect/answers/AnswerCard.tsx` — the short face (label, headline value
  or "Not known"/"Not available" with its gap kind, the 'Conditional' marker, one exception) with the
  derivation (rows, conditions, withheld values, rule sections, measurement, supplements) folded into
  `ResultDetails`.
- `apps/web/src/components/architect/answers/ResultDetails.tsx` (was a placeholder) — the focus-managed
  Details disclosure: a button opens a region, focus moves in, Escape closes it and returns focus to
  the button; the content stays in the DOM (the `hidden` attribute) so assistive tech and in-page
  search still reach it.
- `apps/web/src/components/architect/answers/SharedConditions.tsx` (was a placeholder) — the shared
  conditions stated once via the M5-T148 notices adapter (`collectConditions` + `capNotices`), shown as
  "Condition 1 / Condition 2", at most three with the rest behind a count; never the adapter id "C1".
- `apps/web/src/components/architect/answers/three-answers.css` — rebuilt on the shared tokens with NO
  colour literal; the building-option styles (old lines 373–547) removed (Part B's building-options.css
  takes them); new identity / shared-conditions / details-button / details-region / two-column-grid
  styles; the `44fr / 56fr` desktop grid and the ≤700 px one-column padding via the window's container
  queries.
- Tests: `__tests__/three-answers-panel.test.tsx`, `__tests__/result-details.test.tsx`,
  `__tests__/journey-215-16-northern.test.tsx` (rewritten: the journey leg now checks only that Part
  B's section is PRESENT, not its inside). `__tests__/scope-summary.test.tsx` needed no change and
  passes unchanged. `ResultsStatusStrip.tsx` and `ScopeSummary.tsx` needed no change.

## What it shows on the benchmark lot (recorded_215_16_northern_journey)

- Desktop (window content ≥ 1000 px): two columns. LEFT (44fr, ≥ 320 px): the lot
  "Queens block 7334, lot 70" with "Housing program: standard residence" and
  "Floor-to-floor height: 10 feet"; the one context strip ("Preliminary zoning results ·
  Approximate measurements · Lots you selected"); the two shared conditions once as
  "Condition 1 / Condition 2"; then the three stacked answers — Floor-area allowance
  "20,150 sq ft" marked Conditional (its legal dwelling-unit limit withheld, "Not known", inside its
  Details), Permitted envelope "55 ft" marked Conditional (coverage / rear yard / setback withheld
  with their gap kinds inside Details), Building option "Not available — the building options are shown
  below". RIGHT (56fr): the detailed scope (12 assumptions, open) and Part B's building-options section.
- At 390 px: one column, 16 px padding, same reading order — identity, strip, shared conditions, the
  three answers, then the detailed scope and the building options, then the completeness line. No
  material limitation is hidden; the withheld values remain in the (DOM-present) Details.

## Checks (in apps/web unless noted; direct exit codes)

- `npm run lint` → EXIT 0 (2 warnings, both pre-existing files I did not touch: lot-site-setup.test.tsx,
  study-vocabulary.test.ts).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; Test Files 110 passed (110), Tests 2247
  passed (2247). This includes Part C's frozen `results-panel.test.tsx`, the M5-T148 adapter suites, and
  my four test files.
- root `python3 tools/modularity_check.py --check` → EXIT 0 (warnings are pre-existing services/api &
  tools files; none of my files flagged).
- root `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0,
  "LANE COVERAGE PASS: 9810 file(s), each owned by exactly one lane."

## Mutation proofs (scratch copy OUTSIDE the repo; node_modules + packages symlinked; deleted after)

1. SharedConditions shows the adapter id instead of "Condition N" (`{`Condition ${index+1}`}` →
   `{condition.id}`). CAUGHT by three-answers-panel.test.tsx › "lists each distinct condition once as
   'Condition N', never an internal id such as 'C1'" (expected ['Condition 1','Condition 2'], got
   ['C1','C2']).
2. ResultDetails Escape no longer returns focus to the button (dropped `buttonRef.current?.focus()`).
   CAUGHT by result-details.test.tsx › "Escape closes the region and returns focus to the button"
   (activeElement stayed on the region div, not the button).

## Assumptions and limitations (please verify at the gate)

- The frozen Part C `results-panel.test.tsx` reads `cardEl.textContent` and
  `getAllByTestId("answer-withheld-value")` with no disclosure opened, so the Details content stays in
  the DOM via the `hidden` attribute rather than a conditional render. Consequence: a conditional
  value's full "If …" text sits once in the visible shared-conditions block and also, folded away, in
  that answer's Details — the repeated-clutter (note N3) is removed from the default view, not from the
  DOM.
- The desktop 44/56 split: at a 1440 px window the answers card computes to ≈ 41.8 % of the window
  (44 % of the content box after 24 px panel padding and the 24 px gap) — inside the 40–48 % target but
  sensitive to the window content width. The browser test (Part C, run by the orchestrator) is the
  authority; if it reads below 40 %, trimming the panel's horizontal padding raises it.
- The grid applies only when an ancestor is a size container; per the orchestrator this is Part C's
  window content. jsdom does no layout, so the grid widths are proven by Part C's browser test, not
  here; the jsdom test proves the two regions exist in reading order.
- The single building-option card still reads "the building options are shown below"
  (`BUILDING_OPTIONS_BELOW_REASON` in the forbidden three-answers.ts); at desktop the options sit in the
  right column (beside), below only when stacked. Text change is out of Part A's scope.
- DB-215(b) — tying the estimate's measurement-basis words to the contract — lives in Part B's
  `FirstBuildingOptions.tsx`, outside Part A's files.

No file outside Part A's scope was changed. No server was started; ports 3000/3001/8000 untouched.

## Correction after the reviews (ruling V11; rebuilt on the integrated head f81a1ec3)

The visual review FAILED on one blocking item and the walkthrough on two. Part A's share of V11:

- **(2) the building-option answer is the scheduled area.** When the document lists a building the
  card reads "Scheduled area: 20,150 sq ft" with "Site fit not verified" (the honesty line leads,
  R895), taken from the listed building through Part B's view model `first-building-options.ts`
  (`alternatives[0].totalFloorArea`); never "Not available", never "shown below". With no worked
  building it reads "Not known" with the document's reason and what would settle it. `BuildingOptionCard`
  in AnswerCard.tsx; the view is built in ThreeAnswersPanel from `firstBuildingOptionsView`.
- **(3) one wording per situation.** `GAP_KIND_LINES` (three-answers.ts) drops "Not built yet: … still
  owed"; `work_owed` now shows no second phrase and `missing_information` shows the short tag "Needs
  property information". A withheld value reads "Not known", the reason, then "What would settle it: …"
  (new `resolvedBy` on `WithheldValueView`).
- **(4) no developer words in the heading.** `DRAFT_PREVIEW_TAG` → "rules not professionally reviewed"
  (the "internal preview" dev framing is gone; the ADR-007 standing note stays).
- **(5) conditions by name.** Details no longer repeats the full "If …" text; it shows
  "Applies: Condition 1, Condition 2" (ConditionRefs), numbered to match the shared-conditions block
  through the notices adapter. The building-option card refers the same way.
- **(6) what needs resolving.** A new `openItemsView` (three-answers.ts) groups the document's own
  withheld reasons and resolvers; SharedConditions.tsx shows at most three, each naming what it affects
  and what would settle it (capped through the notices adapter).
- **(7) balance and reading order.** LEFT column: identity, context strip, conditions + open items, the
  three answers, then Part B's building options and comparison. RIGHT column: the scope detail and the
  assumed conditions, open by default. 44:56 grid, test id `three-answers-left` kept.

Not Part A: the form fold and focus-to-results (V11 (1), Part C); the server's "step-P6 method" wording
and the ".00" on whole square feet (V11 (4) server side); the stale-identity guard and the estimate's
measurement-basis test (V11 (10)/(11)); the comparison's frozen row labels (V11 (8)); the typed parking
line (V11 (9), ResultsPanel, Part C).

### Checks (final state; direct exit codes)

- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, untouched files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 1; Tests 2258 passed, **1 failed**. The one
  failure is Part C's `results-panel.test.tsx` › "renders the journey document through the three-answers
  cards" (line 98): it still asserts the full condition text inside the card and the building-option
  card reading "Not available" — both are exactly what V11 (5)/(2) remove. That file is Part C's and is
  being corrected in the same round; this out-of-scope test update is ROUTED TO THE ORCHESTRATOR (not
  edited here — V7). Every Part A test (the four answers tests and three-answers.test.ts) and every
  Part B test pass.
- root `python3 tools/modularity_check.py --check` → EXIT 0. root
  `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0 (9811 files).

### Mutation proofs (one per V11 item; scratch copy outside the repo, deleted after)

- (2) building-option card never scheduled → caught by three-answers-panel.test.tsx "at 10 ft reads
  'Scheduled area' …".
- (3) restore the "still owed" gap phrase → caught by three-answers.test.ts "V11 (3): … work owed gets
  no second phrase".
- (4) heading back to "internal preview …" → caught by three-answers.test.ts "(4) the draft heading
  note drops the dev framing".
- (5) refer to conditions by internal id "C1" → caught by three-answers-panel.test.tsx "refers to the
  shared conditions by name …".
- (6) openItemsView returns nothing → caught by three-answers.test.ts "(6) openItemsView collects …".
- (7) move the building options to the right column → caught by three-answers-panel.test.tsx
  "left = identity + answers + building options; right = the scope …".

## V12 — the left column in the contract's reading order (rebuilt on the integrated head 9ff46ee5)

The browser run showed V11 (7) pushed the answers out of the first screen (S12 failed at 1440 and
390 px), because the shared conditions and open items sat before the answers. Ruling V12 reorders the
left column; only ThreeAnswersPanel.tsx and three-answers.css changed (plus the panel test). The left
column is now: identity, context strip, the three answers, Part B's building options and comparison,
then "What needs resolving" and the shared conditions stated once (the answers still refer to them by
name). The right column is unchanged: the scope detail and the assumed conditions, open by default.
The 44:56 grid and the `three-answers-left` test id are kept; below 1000 px the same order in one
column. The integrated base already carried the orchestrator's rename of Part B's `gapKindLine` to
`propertyInfoTag` on the not-worked view, which the building-option card reads. The panel test's
layout case now asserts the DOM order identity → strip → the three answers → building options →
shared conditions (strengthened, not weakened).

Checks (final): `npm run lint` EXIT 0; `npm run typecheck` EXIT 0; `npx vitest run src/components/architect
src/lib` EXIT 0 — Test Files 110 passed, Tests 2263 passed (Part C's results-panel.test.tsx now passes
on the integrated base). Root `modularity_check --check` EXIT 0; `check_lane_paths --coverage` EXIT 0
(9811 files).

## Local-exception rule — a one-result condition stays with its result (rebuilt on 13c8bd16)

The browser run (results.flag-on.spec.ts) showed that after the special-density statement the
allowance card displayed "29 units" but no longer carried the condition it rests on, because every
condition had been moved to the shared list. The contract (§3) keeps a condition that changes a number
attached to that number, and only shared conditions are stated once and named (V11 (5)). Fixed in
AnswerCard.tsx, SharedConditions.tsx, three-answers.ts and their tests only (ResultDetails needed no
change).

- three-answers.ts: `conditionIndex` walks the document (notices-adapter order) and gives each distinct
  condition its position and fan-out (how many results reference it). `answerView` now splits each
  value's conditions into `localConditions` (fan-out 1, shown in full) and `sharedConditionNames`
  (fan-out ≥ 2, named "Condition N"). New `sharedConditionsView` returns the shared conditions only.
- AnswerCard.tsx: a value's local conditions render in full (one sentence each) with the value; shared
  ones render as "Applies: Condition N". The special-density statement's condition applies only to the
  standard legal-unit-limit, so "29 units" now carries its full condition in the allowance card.
- SharedConditions.tsx: lists only the shared (≥ 2) conditions, each by its own name; the one-result
  conditions are never here.

Checks (final): `npm run lint` EXIT 0; `npm run typecheck` EXIT 0; `npx vitest run src/components/architect
src/lib` EXIT 0 — 110 files, 2266 tests passed (Part C's results-panel.test.tsx passes: on the plain
journey every condition is shared, so named in the cards and stated once in the shared list). Root
`modularity_check --check` EXIT 0; `check_lane_paths --coverage` EXIT 0 (9811).
