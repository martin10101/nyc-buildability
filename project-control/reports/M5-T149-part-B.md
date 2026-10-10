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
