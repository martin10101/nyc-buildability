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
