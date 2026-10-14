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
