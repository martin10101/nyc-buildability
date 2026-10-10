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
