# M5-T149 - producers' report (assembled by the orchestrator from the part reports, each unchanged below)

Task: the architect-facing results slice (the presentation contract's step 3), corrected after its first visual review and walkthrough (rulings V10, V11, V12). Built on one branch with tasks M5-T148, M5-T149 and M5-T150 (wave 20), reviewed at one head and merged as one pull request. Every builder was an AI agent in its own worktree; the orchestrator integrated each commit, read it, and sent back what was wrong (the packet's rulings V1 to V12 and its `scope_corrections` say what and why).

## Builders' run times (from the task notifications)

```
Wave 20 builders (run times from the task notifications' duration_ms; every builder an AI agent in its own worktree):
M5-T148 part A tokens (frontend-engineer): 18.0 min (1,077,741 ms) -> 11d69391 (integrated b6c92236)
M5-T148 part B adapters (frontend-engineer): 19.3 min (1,157,511 ms) -> 36887c5c (integrated a2cffc97); made no report file, its return kept as the part report
M5-T150 outline (geospatial-engineer): 46.0 min (2,761,819 ms) -> 7fd1982c (integrated d183c487); made no report file; its memory-note commit not integrated
M5-T149 part B (frontend-engineer): 28.0 min (1,678,703 ms) -> fbbeb252 (integrated 4f9ea1b1)
M5-T149 part C (frontend-engineer): 26.8 min (1,610,119 ms) -> 99a93361 (integrated 63e0daca); made no report file
M5-T149 part A (frontend-engineer): 46.7 min (2,799,505 ms) -> 9fb1aca4 (integrated 923f3905 without two agent-memory files)
M5-T149 part C, layout-test measures V10: 4.2 min (249,486 ms) -> 4312f1ca (integrated b4126d55)
CORRECTION ROUND (ruling V11):
M5-T150 server wording (rules-engineer): 13.7 min (822,396 ms) -> 0476d78c (integrated bcc5a2ac)
M5-T149 part B: 17.8 min (1,070,780 ms) -> 894f1f53 (integrated 873c87dc)
M5-T149 part A: 25.6 min (1,538,519 ms) -> fb14daba (integrated 553c09fe)
M5-T149 part C: 26.6 min (1,595,811 ms) -> 385295de (integrated c8551767)
orchestrator: gapKindLine -> propertyInfoTag (dec878c2)
M5-T149 part C assertion: 1.9 min (116,037 ms) -> adf3e551 (integrated d22ddd78)
M5-T149 part A V12 order: 5.4 min (322,303 ms) -> ece3f9ce (integrated da1fea97)
M5-T149 part C one-line inputs: 4.5 min (271,182 ms) -> 6ff29e62 (integrated 13c8bd16)
after one diagnostic run (deficit convergence):
M5-T149 part C phone height: 6.4 min (383,714 ms) -> 650596b1 (integrated ad786e43)
M5-T149 part A one-result conditions: 12.8 min (769,296 ms) -> e731cc7a (integrated d745b635)
```


---

## Part A report (unchanged)

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


---

## Part B report (unchanged)

# M5-T149 part B — producer's report (the architect-facing results slice, step 3's building-option part)

Producer: frontend-engineer, an AI agent. This is not a human or professional review. I wrote files
and made one commit in my own worktree; I did not review, accept, push, or touch the ledger.

Contract head reset to `91ec048f4dbe06198446f20c587795ca9fca5a3f` (branch
`task/wave20-presentation-slice`), `git status --porcelain` empty before work. `npx npm@11.18.0 ci`
in `apps/web` exit 0.

## What this part makes true

- **The building option first (S6, row R895).** Each worked building now shows, in this order: its
  document label; then `Building option: Site fit not verified` (the shared constant
  `SITE_FIT_NOT_VERIFIED` imported from the M5-T148 adapter `presented-results.ts`, so the words are
  not retyped); then `Scheduled area: 20,150 sq ft` read from the document; then storeys and height;
  then the caveats (fit note, conditions, floor schedule, what was not checked, the estimate). The
  word "achieved" appears nowhere, and the old "0 sq ft unused" / "total floor area" summary is gone
  — never "no allowance left unused" (row R895). At 16 ft, with no worked building, no scheduled area
  shows and each building's reason comes from the document (the existing not-worked blocks).
- **One option comparison (S7, row R894).** New `BuildingOptionsComparison.tsx` + the view
  `buildingOptionsComparisonView` in `first-building-options.ts`. Every building of the method
  (worked and not worked) is one column, ordered by building id (A then B). Two presentations of the
  same buildings, both in the DOM: per-building summaries (CSS flex: side by side above 700 px,
  stacked at 700 px and below), and one aligned table in a labelled, keyboard-reachable scroll region
  (`role="region"`, `aria-label`, `tabIndex=0`, `overflow-x`) with the SAME five rows, order and
  units for every building — Storeys, Height, Scheduled area, Plan per storey, Estimate. A building
  that was not worked reads the one wording `Not known` in every cell — never 0, never an empty cell —
  and its reason once in its summary. None is preferred (question A2 open). The comparison is built
  only when at least one building is worked AND at least two buildings exist; a single building, or a
  set of only not-worked buildings, shows none.
- **Floor schedule and estimate stay with their building** (unchanged structure from M5-T147); the
  estimate is `17.27 to 21.59` tagged as a preliminary capacity estimate.
- **Styles moved.** The building-option styles (three-answers.css lines 373–547) are now in the new
  `building-options.css`, imported by `FirstBuildingOptions.tsx`, with the class names kept and every
  value changed to the shared `pt` tokens (`apps/web/src/app/globals.css` /
  `docs/design/presentation-tokens.json`). A test asserts the file has no colour literal. Spacing and
  radii use `pt` tokens; type sizes use the `pt` type tokens where a role matches (section-title,
  body); the 24 px estimate range has no exact token and keeps a rem value (documented in the CSS).
- **Props unchanged.** `FirstBuildingOptions({ view })` and `firstBuildingOptionsView(results,
  showDraftValues)` keep their signatures, so Part A's `ThreeAnswersPanel` needs no change.

## On the benchmark lot, in words

- **Desktop (≈1440 px):** the building-options section leads with building B — "Building option:
  Site fit not verified", "Scheduled area: 20,150 sq ft", "3 storeys · 30 ft" — then its fit note,
  the "Conditional" marker with its two conditions, the six-column floor schedule, what was not
  checked, and "Preliminary capacity estimate 17.27 to 21.59 apartments". Below it, building A reads
  "Not known — …the areas disagree…". Then one comparison: building A and building B side by side, A's
  column all "Not known", B's column with its five measures; then coverage by portion, withheld with
  no figure.
- **390 px:** one column; the comparison's per-building summaries stack (A above B); the comparison
  table and the floor-schedule table each sit in their own labelled scroll box, so the page never
  scrolls sideways and every column stays reachable by keyboard.

## Checks (in apps/web unless noted; direct exit codes)

- `npm run typecheck` → EXIT 0.
- `npm run lint` → EXIT 0 (2 warnings, both in pre-existing files I did not touch:
  lot-site-setup.test.tsx, study-vocabulary.test.ts; 0 from my files).
- `npx vitest run src/components/architect src/lib` → EXIT 0; Test Files 110 passed (110), Tests
  2249 passed (2249). (Baseline at the contract head before my work: 110 files / 2242 tests.)
- root `python3 tools/modularity_check.py --check` → EXIT 0 (selected 756 files; failures 0; 30
  advisory warnings, all pre-existing services/api & tools files plus the pre-existing three-answers.ts
  symbol-ceiling note; none of my files flagged).
- root `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0, "LANE COVERAGE PASS: 9810
  file(s), each owned by exactly one lane."

Browser/layout tests NOT run (ruling V6; the orchestrator runs them). No server started; ports
3000/3001/8000 untouched.

## Mutation proofs (scratch copy of the worktree outside the repo, node_modules symlinked; deleted
afterwards; the repo worktree never touched)

1. `Scheduled area:` → `Achieved area:` in `FirstBuildingOptions.tsx` (reintroduces the forbidden
   "achieved", row R895). CAUGHT by `first-building-options.test.tsx › S6: the building option is
   SCHEDULED, site fit not verified — never 'achieved', never 'unused'`
   (`expected 'Achieved area: 20,150 sq ft' to be 'Scheduled area: 20,150 sq ft'`).
2. The not-worked cell fallback `COMPARISON_NOT_KNOWN` → `"0"` for the Storeys row in
   `BuildingOptionsComparison.tsx` (a not-worked building would read 0). CAUGHT by
   `building-options-comparison.test.tsx › S7: a building not worked reads 'Not known' with its
   reason, never 0, never an empty cell` (`expected '0' to be 'Not known'`).

## Files changed (8)

- `apps/web/src/lib/architect/first-building-options.ts` — storeyText; comparison types + view
  (`buildingOptionsComparisonView`); `comparison` field on the view; totalFloorArea reused for the
  scheduled line.
- `apps/web/src/components/architect/answers/FirstBuildingOptions.tsx` — scheduled-area / site-fit
  presentation, "unused" removed, imports building-options.css + SITE_FIT_NOT_VERIFIED, renders the
  comparison.
- `apps/web/src/components/architect/answers/BuildingOptionsComparison.tsx` (new; placeholder
  replaced).
- `apps/web/src/components/architect/answers/building-options.css` (new; placeholder replaced).
- `apps/web/src/test-support/results-two-buildings.ts` (new; synthetic two-worked-building document
  composed from the committed 1.4.0 fixtures, labelled synthetic, test-only).
- `apps/web/src/components/architect/answers/__tests__/first-building-options.test.tsx` — rewritten
  to render FirstBuildingOptions directly (decoupled from part A).
- `apps/web/src/components/architect/answers/__tests__/building-options-comparison.test.tsx` (new
  tests; placeholder replaced) — S7 + the no-colour-literal CSS check.
- `apps/web/src/lib/architect/__tests__/first-building-options.test.ts` — comparison view-model tests
  appended.

Not changed: `building-option-notes.test.tsx` (in my file list but tests part A's answer-card note on
a 1.2.0 fixture with no building blocks, so my change does not affect it) left unchanged.

## Coordination note (not a blocker; packet risk 1)

The building-option styles now live in `building-options.css` (mine). Part A is to remove lines
373–547 from `three-answers.css`. Until that lands they are defined in both files; CSS duplication is
harmless and both carry the same class names, so after integration the styles live only in
building-options.css. Shared classes used by FirstBuildingOptions but defined OUTSIDE 373–547
(`.ta-withheld-reason` base, `.ta-gap-kind`, `.ta-conditional*`, `.ta-row`) stay in three-answers.css
(part A); they apply because ThreeAnswersPanel imports three-answers.css.

No STOP. No file outside my scope changed.

---

## Correction after the reviews (ruling V11 items (3), (5), (8), (11))

Reset to the integrated head `f81a1ec3312353b36593c2927761e616c9a8564f`; `git status --porcelain`
empty before work. The visual-quality and walkthrough reviews FAILED; this round applies my four V11
items. Items (1),(2),(4),(6),(7),(9),(10) belong to the other builders/server.

- **(3) One wording in the not-worked blocks.** A not-worked building now reads: label, "Not known —
  {document reason}", then "What would let it be worked: {document resolver}". The generic gap-kind
  line is gone; a missing property fact carries only the short tag "Needs property information"
  (gap_kind `missing_information`); a building the method cannot yet work (gap_kind `work_owed`)
  carries no tag and no second phrase ("Not built yet"/"still owed"). The view field
  `gapKindLine` became `propertyInfoTag`. The comparison keeps its single "Not known" (unchanged).
  The coverage block, a different result, keeps its own gap line (out of this item's scope).
- **(5) Conditions by name under the building option.** The full "If …" text is no longer repeated
  under a worked building; it now shows the "Conditional" marker + "Applies: Condition 1, Condition
  2". The names and order come from the M5-T148 notices adapter (`collectConditions`) — the SAME
  first-appearance order and "Condition N" numbering Part A's shared-conditions card uses. The full
  text is stated once in that card.
- **(8) Comparison row labels stay in view.** The comparison table's first column (metric row
  headers + the corner cell) is a sticky column (`position: sticky; left: 0`) with its background
  from `--pt-color-surface`, so row context survives horizontal scroll. Class `bo-compare-rowhead`.
- **(11) Measurement-basis words tied to the contract.** The words beside the apartment size are the
  exported constant `APARTMENT_SIZE_BASIS_NOTE = "on the HPD measurement basis"`; a test reads
  `packages/contracts/schemas/v1/results.schema.json` (read only) and asserts every
  `apartment_size_sqft` description contains those words, so the UI phrase is the contract's wording.

### Checks (direct exit codes)

- `npm run typecheck` → EXIT 0.
- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, not my files).
- `npx vitest run src/components/architect src/lib` → EXIT 0; Test Files 110 passed (110), Tests
  2260 passed (2260).
- `python3 tools/modularity_check.py --check` → EXIT 0 (failures 0; no file of mine flagged).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0 (9811 files).

Browser/layout tests NOT run (ruling V6). No server; ports 3000/3001/8000 untouched.

### Mutation proofs (scratch worktree copy outside the repo, node_modules symlinked; deleted after)

- (3) `propertyInfoTag` always set (work-owed would wrongly show the tag) → CAUGHT by
  `first-building-options.test.tsx › S6: with no building worked (16 ft)…` (`expected <p
  class="ta-property-info-tag"> to be null`).
- (5) the condition name map returns the full text instead of "Condition N" → CAUGHT by
  `first-building-options.test.ts › maps building B's floor schedule, totals and estimate…`
  (`expected 'If the recorded lot area…' to match /^Condition \d+$/`).
- (8) `position: sticky` → `position: static` in building-options.css → CAUGHT by
  `building-options-comparison.test.tsx › keeps the row labels in view when the table scrolls
  sideways (ruling V11 (8): a sticky column)`.
- (11) `APARTMENT_SIZE_BASIS_NOTE` → "on the DOB measurement basis" (not in the schema) → CAUGHT by
  `first-building-options.test.ts › the shown measurement-basis words appear in the results schema's
  apartment-size description`.

### Files changed (7 code/test + this report)

`FirstBuildingOptions.tsx`, `BuildingOptionsComparison.tsx`, `building-options.css`,
`first-building-options.ts`, and the tests `first-building-options.test.tsx`,
`building-options-comparison.test.tsx`, `lib/architect/__tests__/first-building-options.test.ts`.
Not changed this round: `building-option-notes.test.tsx` and `results-two-buildings.ts` (in my file
list, no change needed). No STOP. No file outside my scope changed.


---

## Part C report (unchanged)

# M5-T149 part C - producer's report

The builder (frontend-engineer, an AI agent) made no report file in its commit; its return is kept here unchanged, saved by the orchestrator from the session transcript (`return-builder-w20-T149C.txt`).

```
I am an AI agent (frontend-engineer producer). M5-T149 PART C — the Results window as a wide two-column tool, every data state, labelled inputs with a reset, and the browser layout tests — is built, all local checks pass, one commit made. No STOP; no file outside my scope changed. Not a human/professional review.

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-af6b6833ff63e3790
COMMIT: 99a933610166009b87ed33633469a4e52df8f895  PARENT: 57a217a102799384d69ca168664a54d73da1b32d (contract head). `git status --porcelain` empty.

FILES CHANGED (8; 340+/32-):
- src/components/architect/workspace/DashboardEntry.tsx — added "results" to the wide-window list (the ONLY change).
- src/components/architect/workspace/floating-workspace-window.css — every colour + the panel radius moved onto --pt-* tokens (no colour literal); overlay shadow tint via color-mix on the ink token; added one scoped rule `…__content:has(> .results-panel){padding:0}` so the Results window hands its padding to results-panel.css.
- src/components/architect/results-panel.css — rewritten on tokens; `@container` layout: 24px panel padding base, 32px at ≥1000px, 16px one column at ≤700px; 44px controls; no colour literal.
- src/components/architect/ResultsForm.tsx — added a "Reset inputs" secondary button + onReset prop + a wrapping actions row; height input keeps its label-with-unit "(feet)" and >0 bound.
- src/components/architect/ResultsPanel.tsx — wired the reset handler (restores starting inputs, clears the field error, asks the server nothing).
- __tests__/results-panel.test.tsx — kept all existing tests; added a reset test and a "no colour literal" test for results-panel.css.
- workspace/__tests__/floating-workspace-window.test.tsx — kept all; added a wide-is-wider test and a "no colour literal" test for the frame CSS.
- e2e/results-layout.flag-on.spec.ts — new (was a placeholder): six widths (320/390/768/1024/1440/1920) with no sideways page scroll and no clipped text outside labelled scroll regions; at 1440 the answers column 40–48% of the window width and ≥320px; at 1280 a text-spacing override and a 200%-zoom reflow (640px) with no sideways scroll; keyboard focus-into-tool + Escape-return + a tolerant per-result Details check.

WHAT IT SHOWS ON THE BENCHMARK LOT (in words):
- Desktop (1440; the wide window opens ~1100px): the form — housing program, floor-to-floor height in feet, the optional density statement, and Show results / Reset inputs — runs full-width across the top with 32px panel padding and 44px controls; the returned document sits below with the identity/status strip across the top, the three answers in the left column near 44% and the details/comparison on the right. Colours are from the tokens; the focus ring is visible.
- 390px: the window fills the viewport (~374px) with 16px padding; everything is one column — form, then identity, then each answer stacked; no sideways scroll; labels and values wrap and never ellipsize; any wide table sits in its own labelled scroll region.

CHECKS (in apps/web unless noted; direct exit codes):
- npm run lint → EXIT 0 (2 warnings, both pre-existing untouched files: lot-site-setup.test.tsx, study-vocabulary.test.ts; 0 from my files).
- npm run typecheck → EXIT 0 (tsconfig include is **/*.ts, so e2e/results-layout.flag-on.spec.ts is covered and clean).
- npx vitest run src/components/architect src/lib → EXIT 0; Test Files 110 passed (110), Tests 2246 passed (2246).
- root python3 tools/modularity_check.py --check → EXIT 0 (warnings all pre-existing tools/ files; none mine).
- root python3 scripts/lanes/check_lane_paths.py --coverage → EXIT 0, "LANE COVERAGE PASS: 9811 file(s)".

MUTATION PROOFS (file backed up to the scratchpad OUTSIDE the repo, mutated, single test run, restored; cmp confirms each file byte-identical after restore; repo untouched):
1. Reintroduced a colour literal (`#123456`) in results-panel.css → vitest EXIT 1, CAUGHT by results-panel.test.tsx › "results-panel.css carries no colour literal (every colour comes from a presentation token)".
2. Made the Reset button a no-op in ResultsForm.tsx → vitest EXIT 1, CAUGHT by results-panel.test.tsx › "Reset restores the starting inputs and clears a field error, asking the server nothing".

ASSUMPTIONS / LIMITATIONS (please verify at the gate / reconcile across parts):
- Boundary: the inner two-column grid itself (minmax(320px,44fr) 56fr, answers left | details+comparison right) is composed by part A's three-answers.css and part B's building-options.css in the rebuilt ThreeAnswersPanel, NOT in results-panel.css. ThreeAnswersPanel is a single child of .results-panel and holds the identity, answers, details and comparison, so part C cannot lay those out from its own files without colliding; part C owns the wide window, the container-query outer flow (form+identity across the top, document below), the padding tiers, the content-padding handoff, the frame tokens, the form, and the browser tests. If part A does not build the 44fr column, the 1440 answers-column assertion in results-layout will fail — this is the #1 integration point.
- I did NOT start any server/Playwright (ruling V6). The two e2e specs are the orchestrator's to run; I verified them only by reasoning and the real-route fixture pattern, NOT by execution — treat them as unverified-by-me. results-layout measures the answers column through the stable answer-floor_area_allowance card id, uses three-answers-panel, and a tolerant /details/i locator for part A's per-result Details control.
- The frame close-button red hover was removed (no danger token exists, and "Close window — keeps your work" is non-destructive; its accessible name states the effect). Frame SPACING was left stable to avoid regressing the other tool windows; only colours and the panel radius moved to tokens there. This touches every window frame's colours — a visual-quality reviewer should confirm no regression on map/report/evidence windows.
- results.flag-on.spec.ts was reviewed and left UNCHANGED: the wide window and two-column layout change no testid or content, so every existing assertion still holds and none was layout-driven.
- Per the no-report-file override and the M5-T148 precedent I did NOT create project-control/reports/M5-T149-part-C.md; the commit contains only the 8 code/test files (matching its message). Please save THIS return verbatim as that report at the submit seam.

NO SERVER STARTED; ports 3000/3001/8000 untouched.

REQUESTED STATUS: awaiting_gate (ready for G2 self-check / G3 / G4; the two e2e specs run by the orchestrator per ruling V6).
END-OF-REPORT

```

## Correction after the first browser run (2026-10-10; ruling V10)

The orchestrator ran the layout spec at the integrated head and got seven failures in
`apps/web/e2e/results-layout.flag-on.spec.ts` — all from the test's own measures, not the layout.
Only that file changed (plus this section). Both fixes follow ruling V10.

- (b) Clipped-text check: it was flagging three elements that are visually hidden by design for
  screen readers at every width — the window move hint "Drag the title to move this window…", the
  resize hint "Drag this corner…" (both `.workspace-window__sr-only`, a 1×1 box clipped with
  `clip: rect(0 0 0 0)`), and the "Development results are ready." live-region announcement
  (OutcomeAnnouncer, visually hidden). `clippedTextOutsideScrollRegions` now skips an element whose
  rendered box is at most 1×1 px or that is clipped to nothing (clip rect(0,0,0,0) / a clip-path),
  and still reports any element with a real box whose visible text is cut off. The three hints are
  named in a jsdom-free proof comment in the helper (this is a Chromium/Playwright check).
- (a) 1440 px answers-column share: it divided the answers card width by the whole dialog width and
  got 0.379 — but the window also holds the form and the panel padding, which the contract's "near a
  44:56 split" does not count. The test now measures the answers column `three-answers-left` against
  the two-column GRID `.ta-layout` (both columns and the 24 px gap) in ThreeAnswersPanel's markup
  (read, not changed), keeping 40–48 % and at least 320 px.

Checks (apps/web, direct exit codes): `npm run lint` EXIT 0 (same two pre-existing warnings, none
mine); `npm run typecheck` EXIT 0. Playwright NOT run (ruling V6; ports untouched) — the orchestrator
runs the spec. Commit parent is the integrated head `02af2245e19fafb87f306597ae919dbeb0a858a2`.

## Correction after the reviews (2026-10-10; ruling V11 items (1), (9), (10); scenarios S12, S15)

The visual-quality review failed on one blocking item and the walkthrough on two. Part C's share of
V11, rebased onto the integrated head `553c09fee` (parts A and B present):

- (1) FIRST SCREEN: once a result is shown, `ResultsForm` folds to a one-line summary of the inputs
  used — the program; the floor-to-floor height, or "Starting height" when left empty; and the
  density statement only when made — with a "Change inputs" button that reopens the form with the
  inputs kept. Focus moves to the results heading (`.ta-panel-title`, focus only; announcements
  unchanged). Before the first result the form shows as today. Reopening moves focus into the form.
- (9) The typed parking line (and its `PARKING_LINE` export) is removed from `ResultsPanel`; the
  concern now reaches the reader from the listed building's own `not_checked` list in the document
  ("Parking, loading and bicycle requirements"). The S13 vitest test points at the document's list.
- (10) ANOTHER LOT: the panel uses the identity adapter (`result-identity.ts`, read only). A success
  document whose scope names a different lot than the requested BBL is NOT shown; the panel shows
  "These results are for another property" with an "Ask again for this property" button. New test
  added (S15). An unidentified document (no scope) is shown as-is, never guessed to be another lot.
- LAYOUT S12 (`results-layout.flag-on.spec.ts`): at 1440x900 and 390x844, after Show results the
  identity line and the floor-area allowance's headline value are in the viewport and focus is on the
  results heading. The 1440 grid-share, six-width, 200%-zoom and keyboard measures are kept.

Cross-part e2e alignment (my file `results.flag-on.spec.ts`, run only at the integrated head):
Change-inputs clicks inserted before each post-fold form interaction (V11 (1)); the building-option
card assertions aligned to V11 (2) — "Scheduled area"/"Site fit not verified" when a building is
listed (default run), "Not known" when none is listed (16 ft). W-2 in `results-panel.test.tsx`
updated to the V11 truth (conditions referred to by name "Condition N"; the full assumption text once
in the panel; the scheduled-area card), per the orchestrator's note.

Checks (direct exit codes): `npm run lint` EXIT 0 (same two pre-existing warnings, none mine);
`npx vitest run src/components/architect src/lib` EXIT 0, Test Files 110 passed (110), Tests 2263
passed (2263) — with parts A and B present; root `python3 tools/modularity_check.py --check` EXIT 0;
`python3 scripts/lanes/check_lane_paths.py --coverage` EXIT 0 (9811 files). Playwright NOT run
(ruling V6); the orchestrator runs the two e2e specs.

`npm run typecheck` EXIT 2 — ONE remaining error, NOT in a Part C file and outside my scope:
`apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx(158,35): Property 'gapKindLine' does
not exist on type 'BuildingNotWorkedView'`. Part A's `ThreeAnswersPanel` reads `notWorked.gapKindLine`
but Part B's `BuildingNotWorkedView` (first-building-options.ts) carries `propertyInfoTag`, not
`gapKindLine` — a Part A/B integration mismatch present in `553c09fee` independent of my commit (my
files do not touch those). My own typecheck error (ResultsPanel passing the panel's narrowed
`ThreeAnswersResults` to the identity adapter) is fixed by widening to `Results` for the adapter call.
BLOCKER for the wave's typecheck: Part A must change `notWorked.gapKindLine` to `notWorked.propertyInfoTag`.

Mutations (scratch backup outside the repo, one test run each, restored byte-identical):
- (1) `formFolded = false` → CAUGHT by "V11(1)/S12: once results show, the form folds…" (vitest EXIT 1).
- (9) a typed parking `<p data-testid="results-parking">` re-added → CAUGHT by
  "S13/V11(9): no typed parking line…" (vitest EXIT 1).
- (10) `forAnotherLot = false` → CAUGHT by "V11(10)/S15: a results document for another lot is not
  shown…" (vitest EXIT 1).

Follow-up after the whole browser suite (ruling V11 (5)): `results.flag-on.spec.ts` line 94 moved to
the new truth — the allowance card now asserts "Condition 1" (referred to by name) and the
`shared-conditions` block asserts the condition's full text "recorded lot area of 10,075 sq ft"
(stated once). Every other assertion kept. Base `9ff46ee5`. `npm run lint` EXIT 0; `npm run typecheck`
EXIT 0 (the earlier cross-part ThreeAnswersPanel `gapKindLine` error is resolved at this head).

Follow-up after the whole browser suite at `da1fea97` (part A's V12 reorder): two of my assertions
still failed. (1) The folded inputs summary was a tall card (heading + line + button ≈ 180 px) that
pushed the floor-area headline below the window edge at 1440 and 390 (S12). It is now ONE compact
line — "Inputs used: Standard residence · Starting height" with "Change inputs" on the same line
(wrapping only on a narrow window), no card, minimal vertical padding; its accessible name and the
focus move to the results heading are kept. (2) `results.flag-on.spec.ts` envelope assertion moved to
ruling V11 (5): the card asserts "Condition 2" (by name) and the `shared-conditions` block asserts
the full text "none of these conditions, which were not checked" (stated once). `npm run lint` EXIT 0;
`npm run typecheck` EXIT 0; `npx vitest run src/components/architect src/lib` EXIT 0 (110 files, 2263
tests). The S12 test itself is unchanged; its 1440/390 failure cause — my tall folded card — is
fixed by the compact line above (Part A's V12 reorder having landed at this head).

Follow-up (S12 at 390 x 844; diagnostic head `13c8bd16`): S12 passed at 1440 but still failed at 390
— the JS-centred window was 690 px (top 77) on an 844 px screen and the summary wrapped to ~119 px,
so the first answer's headline sat below the window's bottom edge. (a) In floating-workspace-window.css
a `@media (max-width: 700px)` rule overrides the JS inline frame so a non-maximized window fills the
screen height (top 8, height `calc(100dvh - 16px)`, `!important` to beat the inline style); desktop is
untouched, other windows only gain full height on phones. A jsdom test asserts that CSS rule exists.
(b) At narrow container widths the inputs summary hides its "Inputs used:" label from view (kept for
screen readers via the region's accessible name) and compacts the "Change inputs" button, so the
summary is about one line and the button stays beside the text where it fits. Together the first
answer's headline lands inside the 844 px screen. `npm run lint` EXIT 0; `npm run typecheck` EXIT 0;
`npx vitest run src/components/architect src/lib` EXIT 0 (110 files, 2264 tests). Playwright not run
(V6); the orchestrator runs the browser suite.
