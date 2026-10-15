# M5-T181 — producer report

**Task:** The Results window's first screen leads with the results (the floor-area allowance, then the
legal ceiling beside the apartment estimate); the assumed conditions sit below them (D-094 R151).
**Producer:** frontend-engineer (builder). **Claim head:** `658e51fbd4bb70ad5594061a08ac2f3102b1e293`
(`task/wave25-rear-yard-short-block`). Worktree: `/root/project/nyc-buildability/.claude/worktrees/wf_03dee06a-cdc-1`.

## What changed and why

The owner's outside reviewer (D-094 R151) read real pictures of the Results window and found "the
visible screen still gives substantial space to assumptions while results sit farther down." At the
claim head the Results window renders the identity, the status strip and the three answer cards in the
44fr left column with `ApartmentFigures` (the legal ceiling beside the apartment estimate) **after** all
three cards, so that block sat below the fold (preview notes: top 1296 px desktop / 1380 px phone),
while the 56fr right column showed the full "Assumed conditions" list from the top of the first screen.

This is a **placement/reading-order change only** — no number, figure, certainty label or fixed wording
changes; `ApartmentFigures.tsx`, `ScopeSummary.tsx`, `AnswerCard.tsx`, `apartment-figures.ts`,
`three-answers.ts` and `presentation-tokens.json` are untouched. The 29 stays Conditional, the 17-22
stays Provisional, the distinction line is unchanged, and all 13 assumed conditions stay open (R119 —
demoted, never capped).

`apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx`
- Added a full-width **lead band** `<div className="ta-lead" data-testid="three-answers-lead">` directly
  under the panel title. In report page-1 order it holds: the identity (`IdentityLine`), the one status
  strip (`ResultsStatusStrip`), the Floor-area allowance `AnswerCard` (with its `SupplementRow`
  remaining-area child), and — directly below it — the `ApartmentFigures` block. The allowance card and
  the apartment-figures JSX were **moved** here; their props and test ids are unchanged.
- The existing `.ta-layout` 44:56 grid stays **below** the band. Its left column (`three-answers-left`)
  now holds only `answer-permitted_envelope`, the building-option card, `FirstBuildingOptions` and
  `SharedConditions` ("What needs resolving"). Its right column (`three-answers-right`) still holds
  `ScopeSummary` (`three-answers-scope`), all 13 conditions open — now beneath the results band.
- Because `.ta-layout`, `three-answers-left` and `three-answers-right` keep their ids and the 44:56
  `grid-template-columns`, the forbidden `results-layout.flag-on.spec.ts` S1 (44:56 via
  `.ta-layout`/`three-answers-left`) and S12 (identity + allowance headline in the first screen, focus on
  the heading) keep passing unedited — the moved results sit higher, not lower.

`apps/web/src/components/architect/answers/three-answers.css`
- Added `.ta-lead { display: block; }` (no colour literal; its children carry their own spacing) and a
  `margin-top: var(--space-4)` on `.ta-layout` so the detail grid is separated from the band. The
  `@container (min-width:1000px)` grid rule is unchanged, so the 44:56 switch at 1000 px is unaffected;
  the lead shares the same size container (set on the window content), so it stacks in the same order on
  a narrow screen.

`apps/web/src/components/architect/answers/__tests__/three-answers-panel.test.tsx`
- Updated the one composition test (was "orders the left column…") to the new S4 composition: the lead
  band order identity → status strip → `answer-floor_area_allowance` → `apartment-figures`; the detail
  grid left column order `answer-permitted_envelope` → `answer-building_option` → `first-building-options`
  → `shared-conditions`; `three-answers-scope` in the right column; and `apartment-figures` precedes
  `three-answers-scope` in the DOM. Every other test is unedited.

`apps/web/e2e/results-first-screen.flag-on.spec.ts` (was a placeholder)
- New Playwright spec owned only by M5-T181, carrying S1, S2, S3 and S7. It defines its own
  `routeApi`/`openResults`/clipped-text/overlap helpers (the existing spec's are not exported and its file
  is forbidden) — acceptable e2e duplication of the M5-T149/M5-T171 pattern. It starts no server; it runs
  in CI (`chromium-flag-on`).

## First screen, top to bottom (my reading of the CSS; CI + the orchestrator's pictures confirm the pixels)

The Results window is `min(1100, width) × min(690, height)`, centred (FloatingWorkspaceWindow). After
"Show results" the form folds to a one-line summary and focus moves to `.ta-panel-title`
(`preventScroll:false`), so the visible scroll region begins near the panel title.

**1440 × 900** (window ~1100 × 690, visible content region ~650 px): folded form summary + "Change
inputs"; panel title "Results — rules not professionally reviewed"; then the **lead band**: identity
(215-16 NORTHERN BOULEVARD, Queens; Queens block 7334, lot 70; standard residence; 10 feet); the one
status strip; the Floor-area allowance card ("20,150 sq ft Conditional"); then the apartment-figures
block ("Legal ceiling 29" Conditional beside "Estimate 17-22" Provisional, the distinction line, the
lot-area line, the zoning-lot concern). My CSS reading puts `apartment-figures-ceiling-value` ~490 px
below the panel title, inside the ~650 px visible region with margin. Below the band: the 44:56 grid —
left column (permitted envelope, building option, FirstBuildingOptions, "What needs resolving"), right
column (the Assumed conditions list), now beneath the results band rather than filling the first screen's
right half.

**390 × 844** (single column; window ~390 × 690): folded form summary + "Change inputs"; panel title;
identity (the long address wraps to two lines); the status strip on one line; the Floor-area allowance
card; then the apartment-figures block with the ceiling/estimate cells stacked and the distinction line
beneath. The allowance headline and the ceiling/estimate figures sit in/near the first screen above the
assumed conditions; the permitted envelope, building option, "What needs resolving" and the Assumed
conditions list follow. No sideways scroll; the long address wraps and no value ellipsizes.

## Scenario → test map

| Scenario | Where verified |
|---|---|
| S1 (identity, allowance headline, ceiling & estimate in the first screen at 768/1024/1440/1920; no overflow; no clipped text; cells don't overlap) | `results-first-screen.flag-on.spec.ts` S1 loop — **CI** |
| S2 (1440×900: results above assumptions, both DOM and vertically) | `results-first-screen.flag-on.spec.ts` S2 — **CI**; DOM order also in the vitest S4 test |
| S3 (390×844 & 320×844: allowance headline in the first screen; results precede assumptions; ceiling top < 1.25× viewport; no sideways scroll; no clipped text/ellipsize) | `results-first-screen.flag-on.spec.ts` S3 loop — **CI** |
| S4 (composition/order in ThreeAnswersPanel) | `three-answers-panel.test.tsx` "S4: the results lead in a full-width band…" — **vitest (local, PASS)** |
| S5 (no forbidden word; 29 Conditional; 17-22 Provisional; distinction line unchanged; tokens unmodified) | `three-answers-panel.test.tsx` existing X5/S5/token tests + forbidden-word grep — **vitest (local, PASS)** |
| S6 (forbidden suites unedited stay green; all 13 conditions; results-layout S1/S12) | forbidden suites unchanged — **CI** |
| S7 (320/390/768/1024/1440/1920: no sideways scroll; no clipped text) | `results-first-screen.flag-on.spec.ts` S7 loop — **CI** |
| S8 (lint/typecheck/touched vitest pass; Playwright from CI) | commands below — **local PASS** |

## Commands (direct exit codes)

| Command (cwd `apps/web` unless noted) | Result | Exit |
|---|---|---|
| `npx --yes npm@11.18.0 ci --no-audit --no-fund` | added 314 packages | 0 |
| `npm run lint` (`eslint .`) | 0 errors, 2 warnings (pre-existing, in untouched files `lot-site-setup.test.tsx`, `study-vocabulary.test.ts`) | 0 |
| `npm run typecheck` (`tsc --noEmit`) | clean | 0 |
| typecheck-covers-e2e probe (appended a deliberate type error to the new spec; `tsc -p .` reported exactly 1 error in `results-first-screen`; reverted) | confirmed the new e2e spec type-checks | — |
| `npx vitest run src/components/architect/answers src/lib/architect` | **Test Files 32 passed (32); Tests 591 passed (591)** | 0 |

## Mutation proof (S4 is a real guard)

Backed up the good `ThreeAnswersPanel.tsx`, mutated, ran the focused S4 test, restored (sha back to
`44f6b7e3…`), reran the full touched vitest green (591 passed).

1. **ApartmentFigures moved back into the left column after the answer cards** → S4 FAILS:
   `TestingLibraryElementError: Unable to find an element by: [data-testid="apartment-figures"]` at
   `within(lead).getByTestId("apartment-figures")`. Exit 1.
2. **ScopeSummary moved into the lead before the allowance (removed from the right column)** → S4 FAILS:
   `TestingLibraryElementError: Unable to find an element by: [data-testid="three-answers-scope"]` at
   `within(right).getByTestId("three-answers-scope")`. Exit 1.
3. **Lead given the test id `three-answers-left`** → S4 FAILS:
   `TestingLibraryElementError: Unable to find an element by: [data-testid="three-answers-lead"]` (the
   `three-answers-lead` lookup no longer resolves; `three-answers-left` is also now ambiguous with two
   matches). Exit 1.

After restore: `npx vitest run src/components/architect/answers src/lib/architect` → 591 passed, exit 0.

## LF-normalized sha256 of each changed file

```
44f6b7e3f5c999b738325688ef878448324f6b2ab9b634d3c5f4359dcd1d921e  apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx
b83d0e85c11afe9ad725cad73ad7fce74638700f8a4ccd18276e76c94259a4ec  apps/web/src/components/architect/answers/three-answers.css
3088f105bbec037ec9702afd3f2c2579534cac2cc0265a2be7c6269ba1854dd1  apps/web/src/components/architect/answers/__tests__/three-answers-panel.test.tsx
277b56e124c7c03ebd7693ec2d7471950b7fa919a232a4dc48961793061e9cde  apps/web/e2e/results-first-screen.flag-on.spec.ts
```

## Research & verification (D-093)

This change moves where existing results appear; it changes no feasibility fact, figure, rule
applicability, calculation input, result or certainty label. The read-only evidence records
`docs/research/evidence-records/NB-01-zoning-lot-instruments.json` and `NB-04-lot-dimensions-basis.json`
are untouched; the zoning-lot concern and the lot-area line keep their conditions attached (rendered by
the unchanged `ApartmentFigures`). Settled legal readings in `docs/reference-cases/R6B/cases/` were not
re-researched. Nothing I changed alters a figure, a label or a condition, so no evidence record or
zoning-rule-review entry is owed by this task.

## What I could NOT check (for the orchestrator / reviewers)

- **The Playwright specs** (`results-first-screen.flag-on.spec.ts`, and the forbidden
  `results-layout.flag-on.spec.ts` S1/S12, `results.flag-on.spec.ts`) run in **CI** only — I started no
  server and touched no port (3000/3001/8000). S1/S3's `toBeInViewport` and the exact measured top of
  `apartment-figures-ceiling-value` at 320/390 (and that ceiling+estimate land in the first screen at
  every desktop width inside the ~690 px window) must be read from the CI run and stated in the record.
  My CSS reading says the lead fits with margin; **if a desktop width cannot fit, raise the
  results-scoped-window-height open question — do not change the shared FloatingWorkspaceWindow.**
- **The before/after pictures** are the orchestrator's (ruling V6). The after captures must be genuinely
  distinct from the before (R150 defect: identical before/after) and taken from the real built head.
- **Open questions** carried forward (plan `return-plan-T181-spec.json`): demote-but-open vs cap (keep
  all 13 open, R119 — recommended); whether the assumptions must be entirely below the fold on desktop
  (would break the shared `results-layout.flag-on.spec.ts` S1 which overlaps M5-T167 — deferred); confirm
  M5-T167's producer edits none of the four forbidden e2e/harness files so the two tasks share no file.

## Surprises

- Mutation 3 fails at the `three-answers-lead` lookup (not at an ambiguity error), because that lookup
  runs before the `three-answers-left` one in the S4 test — either way the test guards the lead's id.
- The typecheck (`tsc --noEmit`) does cover `apps/web/e2e/**` (tsconfig `include` is `**/*.ts`), confirmed
  by the deliberate-error probe — the new spec is type-checked by the same `npm run typecheck`.

---

# M5-T181 — producer report, ROUND 2

**Producer:** frontend-engineer (builder, round 2). **Head reset to:** `1bec706590cc0837d285cb355882d3750040de9e`
(contains round 1, the lead band above the unchanged 44:56 grid). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/wf_8c6fd1b2-887-1`.

Round 1 put the results in a full-width lead band but left the legal ceiling and the apartment estimate
BELOW the window's visible fold: the orchestrator's real-preview measurements at `1bec7065`
(`six-after-1bec7065/positions.txt`) show the ceiling value at top 824 px (1440, below the ~795 px fold),
816 px (1024), 844 px (768), 1040 px (390) and 1213 px (320, above 1.25×844 = 1055). The allowance card
was tall and the identity + status strip filled the top. A second defect: round 1's spec made ~13 results
requests (one per test), which exhausted the shared rate limit and failed the unedited
`results.flag-on.spec.ts:68` ("Too many requests"; CI run 38651131040).

## What changed and why (three levers, placement/spacing/type-token only)

No figure, label, certainty word or fixed wording changed; `ApartmentFigures.tsx`, `AnswerCard.tsx`,
`ScopeSummary.tsx`, `apartment-figures.ts`, `three-answers.ts`, `presentation-tokens.json` and the shared
`FloatingWorkspaceWindow` are untouched. The 29 stays Conditional, 17-22 Provisional, all 13 assumed
conditions open (R119). `.ta-layout`/`three-answers-left`/`three-answers-right` ids and the 44:56 columns
are unchanged, so the forbidden `results-layout.flag-on.spec.ts` S1 (44:56) and S12 (identity + allowance
headline in the first screen) keep passing UNEDITED (both pull the allowance headline UP, never down).

1. **The allowance card and the apartment-figures block sit SIDE BY SIDE** in the lead where the Results
   window is wide enough. New wrapper `<div className="ta-lead-figures">` holds the two; CSS
   `@container (min-width: 640px)` makes it a two-column `minmax(0,1fr) minmax(0,1fr)` grid (`align-items:
   start`, `gap: --pt-space-24`), measured on the SAME size container as the detail grid. Side by side the
   ceiling/estimate align with the allowance card's top instead of sitting below its full height, so they
   reach the first screen at every desktop width. The breakpoint is 640 px (not the grid's 1000 px) ON
   PURPOSE: the hard target is the ceiling/estimate visible at 768 and 1024 (container ≈ 701 and ≈ 968 px),
   which a 1000 px switch would leave stacked and below the fold. This is a deliberate, documented
   deviation from the advisory "switch at the same 1000 px" risk note — the target wins; the detail grid
   below still switches at its own 1000 px, independently. `minmax(0,1fr)` lets either card shrink, so no
   label clips and the page never scrolls sideways; the af-pair cells wrap to stacked when the column is
   narrow. `.ta-lead-figures > .af-figures { margin-top: 0 }` inside the 640 px query removes the block's
   stacked top margin so it aligns with the allowance top (it keeps the margin when the two stack).

2. **The one status strip now follows the results** (identity → results → strip), as the round-2 brief
   permits ("the status strip directly after the ceiling-and-estimate block instead of above the
   allowance … still one strip, at most three items"). On a phone (stacked) this removes the tall strip
   (~90 px at 390, ~138 px at 320) from between the identity and the allowance, pulling the allowance and
   the ceiling up into the first screen; on desktop it adds margin. This is a deliberate deviation from
   the packet objective's "identity, the one status strip, the allowance …" order; it is the brief's
   sanctioned lever and the page-1 reading (result first, context after) is preserved.

3. **The property heading steps down one type size on a phone-width container** (`@container (max-width:
   480px)`): `.ta-identity-lot` goes from `--pt-type-property-title-size` (28 px) to
   `--pt-type-section-title-size` (18 px) — a TYPE TOKEN only, no number literal. The long address
   "215-16 NORTHERN BOULEVARD, Queens" then wraps to fewer lines (4 lines → ~2 at 320 px; ~2 → ~1 at
   390 px), saving ~80 px at 320 and ~40 px at 390. The borough/block/lot sub-line and the facts are
   unchanged. (Desktop containers are ≥ 700 px, so the heading is unaffected there.)

## Rate-limit fix (second defect) — the new spec makes 2 results requests

`apps/web/e2e/results-first-screen.flag-on.spec.ts` now has exactly TWO tests, each calling `openResults`
once and then RESIZING the viewport across the widths (the floating window re-fits on `resize`), so the
whole file issues **2** results (POST) requests total — one for the desktop sweep (768/1024/1440/1920), one
for the phone sweep (390/320) — never one per width. Only `openResults` issues the rate-limited POST
(`route.continue()` on `…/results`; the GET profile is fulfilled from the fixture). 2 ≤ 3 as required. The
sweep runs LARGEST → SMALLEST because `FloatingWorkspaceWindow.fitFrame` only shrinks a frame to fit and
does not re-grow it once shrunk; descending the widths lands the correct `min(1100, viewport)` window at
every step.

## Stronger assertions (not just toBeInViewport)

For each value the new spec asserts its bounding-box BOTTOM is at or above the dialog's visible bottom —
`(await boxBottom(value)) <= scrollViewportBottom(dialog)`, where `scrollViewportBottom` is the
`.workspace-window__content` box's `y + height` (the window's clipped region) — with 40 px of spare at
1440/1920. At the phones the allowance headline must be wholly inside that visible bottom and the ceiling
top under 1.25 × 844 = 1055 px. S2 (results precede the assumed conditions, in the DOM and vertically) and
S7 (no sideways scroll, no clipped text at every width) are kept, folded into the two sweeps. `expect.poll`
is used for the dialog-relative numeric checks so each re-measures after the viewport re-fit settles.

## Expected positions (top px from the browser window top; my CSS/arithmetic reading — CI and the
orchestrator's re-measurement confirm or refute). Deltas applied to the round-1 `positions.txt` values.

Desktop fold ≈ 795 px (height 900); phone fold ≈ 836 px (height 844). Levers: strip-below −H_strip
(≈66 px desktop 1-line / ≈90 px @390 / ≈138 px @320); 2-up puts the ceiling at the results-row top + ~43 px
(af pad-top 16 + af-title 18.9 + its 8 px margin); heading-shrink −~40 @390 / −~80 @320.

| width×h | item | round-1 top | round-2 expected top | arithmetic | target |
|---|---|---|---|---|---|
| 1440/1920×900 | allowance headline | 623 | ~557 | 623 − 66 (strip) | in screen |
| 1440/1920×900 | ceiling value | 824 | ~529 | row-top ~486 + 43 (2-up) | ≤755 (40 spare); bottom ~553 ✓ |
| 1440/1920×900 | estimate value | 824 | ~529 | same row as ceiling | ≤755; bottom ~553 ✓ |
| 1440/1920×900 | distinction line | — | ~561 | af-pair bottom ~553 + 8 | ≤795; bottom ~585 ✓ |
| 1024×900 | allowance headline | 615 | ~549 | 615 − 66 | in screen |
| 1024×900 | ceiling/estimate | 816 | ~521 | row-top ~478 + 43 (2-up, side by side) | ≤795; bottom ~545 ✓ |
| 768×900 | allowance headline | 643 | ~577 | 643 − 66 | in screen |
| 768×900 | ceiling value | 844 | ~549 | row-top ~506 + 43 (2-up, cells wrap) | ≤795; bottom ~573 ✓ |
| 768×900 | estimate value | 844 | ~581 | ceiling bottom ~573 + 8 (wrapped) | ≤795; bottom ~605 ✓ |
| 390×844 | allowance headline | 797 | ~667 | 797 − 90 (strip) − 40 (heading) | <836; bottom ~711 ✓ |
| 390×844 | ceiling value | 1040 | ~910 | 1040 − 90 − 40 | <1055 ✓ (145 margin) |
| 320×844 | allowance headline | 946 | ~728 | 946 − 138 − 80 | <836; bottom ~772 ✓ |
| 320×844 | ceiling value | 1213 | ~995 | 1213 − 138 − 80 | <1055 ✓ (60 margin) |

Identity top is unchanged by the strip move (the strip was after the identity): ~356 (1440/1920), ~348
(768/1024), and at the phones the heading-shrink lowers the identity's own height, moving everything below
it up by the deltas above.

## Checks (direct exit codes, cwd `apps/web`)

| Command | Result | Exit |
|---|---|---|
| `npx --yes npm@11.18.0 ci --no-audit --no-fund` | added 314 packages | 0 |
| `npm run lint` | 0 errors, 2 pre-existing warnings (untouched `lot-site-setup.test.tsx`, `study-vocabulary.test.ts`) | 0 |
| `npm run typecheck` (`tsc --noEmit`, covers `apps/web/e2e/**`) | clean | 0 |
| `npx vitest run src/components/architect/answers src/lib/architect` | **Test Files 32 passed (32); Tests 591 passed (591)** | 0 |

## Mutation proofs

**Vitest S4 is a real guard of the new lead order** (backed up the good file, mutated, ran focused S4,
restored byte-clean, re-ran 591 green):
1. **Status strip moved BACK above the allowance (round-1 order)** → S4 FAILS:
   `AssertionError: lead item 3 must follow 2` (the strip must be LAST now). Exit 1.
2. **ApartmentFigures moved out of the lead into the left column** → S4 FAILS:
   `TestingLibraryElementError: Unable to find an element by: [data-testid="apartment-figures"]` in the
   lead. Exit 1.

**The new e2e spec's stronger assertions are real** (proof by reading the round-1 `positions.txt`; the
spec runs in CI). On round 1's LAYOUT the new dialog-bottom assertion FAILS where round 1's
`toBeInViewport` PASSED:
3. At **1440×900**, round-1 ceiling/estimate top 824 → box bottom ~848; the window's visible bottom
   ~793. New assertion `848 ≤ 793` is FALSE (fails); round-1 `toBeInViewport` (824 < 900) was TRUE. The new
   assertion catches the below-fold figure.
4. At **768×900**, round-1 ceiling top 844 → box bottom ~868 > ~793. New assertion FALSE (fails); round-1
   `toBeInViewport` (844 < 900) was TRUE. Caught.
   (The phone S3 top-under-1055 assertion already existed in round 1 and failed at 320 — 1213 > 1055 — and
   is retained; round 2 moves the ceiling to ~995 to pass it.)

## What I could NOT check (CI's / the orchestrator's)

- **The Playwright spec** runs in CI only (I started no server, touched no port 3000/3001/8000). The exact
  positions above are my CSS/arithmetic reading; the CI run at the round-2 head and the orchestrator's
  re-measurement confirm or refute them. If any desktop width still cannot fit, the shared window height
  is NOT to be changed here — raise the results-scoped-window-height open question.
- The resize-across-widths pattern relies on `FloatingWorkspaceWindow` re-fitting on `resize` (confirmed by
  reading its `resize` effect) and on the shrink-only `fitFrame` behaviour (hence the largest→smallest
  sweep). If CI shows a width measuring at the wrong window size, the sweep order is the first thing to check.

## Research & verification (D-093)

Unchanged from round 1: this is a placement/spacing/type-size change only. No feasibility fact, figure,
rule applicability, calculation input, result or certainty label changes; the read-only evidence records
`NB-01-zoning-lot-instruments.json` and `NB-04-lot-dimensions-basis.json` are untouched and the zoning-lot
concern and lot-area line keep their conditions attached (rendered by the unchanged `ApartmentFigures`).
Settled legal readings in `docs/reference-cases/R6B/cases/` were not re-researched. No evidence record or
zoning-rule-review entry is owed by this task.
