<!-- Verbatim reviewer return (agent-return channel; agentId a50d1a711bed411c9, visual-quality-reviewer, 2026-07-17; FIRST real dispatch of this reviewer — agent-memory containment confirmed in-report). Saved by the orchestrator per the report-preservation rule. Contributes visual evidence to G3/G4 per .claude/rules/3d-ui-expansion.md item 11. Verdict: VISUAL-QUALITY PASS; Major a11y finding D1 tracked by the orchestrator as defect task M2-T005 (announcement/focus management) rather than blocking this task (no committed acceptance scenario breached; app remains INTERNAL/DEV behind B-001 no-deploy). -->

# Visual Quality Review — M2-T002 Confirm screen (G3/G4 visual evidence)

**Reviewer:** visual-quality-reviewer (independent; did not produce this work)
**Target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T002`, branch `task/M2-T002-confirm-screen`, HEAD `6d9fbd4`
**Method and honest limitation:** No browser can run on the owner PC. This is a code-level visual/interaction review of JSX structure, `apps/web/src/app/globals.css` tokens, a11y attributes, and responsive CSS, cross-checked against the committed Playwright assertions (43 journeys, CI green on PR #21 per dispatch). I cannot see pixels; every pixel-dependent claim below is confined to what code plus committed e2e assertions prove, and open pixel questions are named as carry-forwards against the standing CI playwright-evidence traces.

---

## 1. Design-system conformance — PASS

- The Confirm screen (`src/components/confirm/ConfirmScreen.tsx`, `src/app/property/confirm/page.tsx`) extends, not forks, the accepted M2-T001 vocabulary: it imports and reuses `CoverageBadge`, `CoverageLegend`, `ConflictsSection`, `ZoningSection`, `ProvenanceDisclosure`, `LoadingStages`, `OutcomeFailureStates`, `InternalBanner`, and the shared `.card` / `.section-title` / `.section-note` / `.primary-button` / `.status-badge` classes. New CSS (`confirm-grid`, `confirm-row`, `confirm-persistence`, `legend-list`, `table-scroll`) is built entirely from the existing token variables (`--space-*`, `--radius-*`, `--border-quiet`, single accent `--accent`). No second accent color, no component-template default look — this is a hand-rolled token system, not a default dashboard.
- Minor token drift (pre-existing pattern, not new): inline style objects (`h3` sizes in `ZoningSection.tsx` lines 39/114, `h1` fontSize in `ConfirmScreen.tsx` line 396, footer styles in `layout.tsx`) bypass the type-scale tokens. Informational only.

## 2. Visual hierarchy — PASS

- Normal path has exactly one `h1` ("Step 2 — Confirm the property"), sections as `h2` cards, sub-heads `h3`; the compact card uses semantic `dl`/`dt`/`dd` (`.confirm-row` two-column grid, stacking under 768px), values emphasized via `.fact-value` (bold, tabular-nums) with quiet `.fact-units`.
- One clear next action: single `.primary-button` per state ("Back to property lookup" in the Next step card; the confirm affordance is a disabled `.secondary-button` honestly labeled "not yet available"). The five-second read in code terms is: step framing, identity card, facts, questions, one primary action — coherent.
- **Defect D4 (Minor, clutter):** landmark/flood values render twice on the Confirm screen — once in `ZoningSection`'s "Mapped features and flags" table (which renders all `mapped_features`) and again in the dedicated "Landmark, flood, and pending flags" `dl` (`FLAG_FEATURES` covers `landmark`, `histdist`, `firm07_flag`, `pfirm15_flag`, all of which are mapped features). Redundant duplication on one screen; consider filtering the flag fields out of the Zoning table on Confirm or vice versa.

## 3. Legal-certainty-not-by-color — PASS

- Every status is text-first: `CoverageBadge` renders the verbatim PRD §12 enum value + non-color symbol (aria-hidden) + visually-hidden gloss; `CoverageLegend` (D3 resolution) states glosses visibly with no hover, only for statuses actually present, with the remaining vocabulary in a `details` disclosure deliberately not rendered as badges (S7 honesty — verified by the honesty journey counting `.status-verified` nodes).
- Code-level contrast estimates of the token pairs all clear WCAG AA for their sizes: badge fg/bg pairs approximately 6.4:1 (`conditional`), 6.5:1 (`data_conflict`), high for `review`/`verified`; `--text-tertiary` #6f6f69 on white approximately 5.0:1; accent #1f4f82 on white approximately 8.4:1. Red is confined to the conflict hue (muted #8a3b1f), consistent with the "avoid excessive red" rule. Exact rendered contrast is a carry-forward (CF-2).

## 4. Accessibility — PASS with one Major defect

Proven good: keyboard-only toggle and retry journeys committed in `e2e/responsive-a11y.spec.ts` (Tab-to-target via `tabUntil`, Enter and Space activation, `aria-expanded` asserted both ways; retry re-issue asserted by request count). `MissingInputsSection` toggle carries `aria-expanded`; disclosures are native `details`/`summary` (keyboard-free-of-JS); form input has `label for` + `aria-describedby="bbl-hint bbl-error"`; inline form error region has `aria-live="polite"`; global `:focus-visible` ring; `prefers-reduced-motion` kill-switch present (no animations exist anyway); icons/symbols are `aria-hidden` with text equivalents; footer disclaimer has `role="contentinfo"`.

- **Defect D1 (Major, a11y — recommended blocking correction, orchestrator's call):** outcome arrival is not announced and focus is not managed. `LoadingStages` has `aria-live="polite"` but unmounts when the outcome arrives; the replacing failure cards (`FailureState.tsx` — all ten states) have no `role="alert"`/`aria-live` and no focus move, so a screen-reader user hears "Looking up BBL…" and then silence for every failure state on both screens. After keyboard retry, the failure card unmounts (loading replaces it) and focus drops to `body`, forcing a full re-Tab. On the Property screen only the success path partially announces (via `CompletenessBanner role="status"`); the Confirm screen announces nothing. Partially inherited from accepted M2-T001, but M2-T002 added five new failure states and a whole new screen sharing the gap, and the packet's own review scope names this check. No committed acceptance scenario is breached (S6 covers keyboard operability only), so I classify it as a required-correction/tracked-defect recommendation rather than a gate FAIL.
- **Defect D2 (Minor):** `.secondary-button` has no `:disabled` style (only `.text-input:disabled` is styled); the disabled "Confirm facts (not yet available)" button keeps `cursor: pointer` and full-contrast styling — its disabled state is carried only by the label text. Also, disabled buttons are unfocusable, so keyboard users can only discover the affordance through the adjacent persistence note (acceptable, but style the disabled state).
- **Defect D3 (Minor):** the bad-parameter branch of `ConfirmEntry` (`confirm-bad-param`) renders with no `h1` on the page (only the `h2` failure title) — heading hierarchy starts at level 2 in that state.
- **Defect D5 (Minor, needs browser):** the focus ring is `0 0 0 3px rgba(31,79,130,0.35)` — a 35%-alpha accent blends to roughly #a8bdd4 on white, likely under the 3:1 focus-appearance contrast guideline. Operability is proven; visibility is not.

## 5. Responsive robustness — PASS

- The committed e2e asserts `scrollWidth <= clientWidth + 1` for both screens at 360/768/1280 plus legend visibility at each width — real overflow assertions, not screenshots.
- The layout approach is robust beyond the three tested widths: the shell is fluid `max-width: 68rem`; `.confirm-row` is a `14rem 1fr` grid collapsing to `1fr` below 768px (no awkward intermediate breakpoint — behavior between 481–767 and 768–1280 is continuous); wide tables scroll inside `.table-scroll` rather than the page; `overflow-wrap: anywhere` on `dd`, failure meta, and provenance bodies handles long correlation ids/URLs (bounded-reflection helpers cap length upstream); zoning chips wrap and go full-width on phones; the provenance `dl` stacks below 480px. `white-space: nowrap` badges live inside scrollable tables or wrapping flex rows, so they cannot force page overflow. One browser check flagged: focus ring / opened `details` inside a horizontally scrolled `.table-scroll` at 360px (CF-3).

## 6. Consistency — PASS

- `InternalBanner` is now a shared component rendered on both screens with identical copy/styling; the PRD §29 disclaimer renders from the shared layout footer on every page, and the S1 journey asserts both are present on the Confirm route.
- Error states: the Confirm screen reuses the exact `OutcomeFailureStates` switch from M2-T001 with a "Back to property lookup" recovery link appended — same `.failure-state` visual grammar, same correlation-id meta, no raw backend dumps (all reflected text is bounded upstream). The bad-param card also uses `.card failure-state`.
- Spacing/typography rhythm follows the same token scale on both screens. One informational inconsistency: `CoverageLegend` sits before `ConflictsSection` on the Property screen but after it on Confirm — deliberate-looking (legend adjacent to the flag badges it explains) but worth a note.

## 7. Regression of modified M2-T001 components — PASS

- `git diff main...HEAD` on `CoverageBadge`, `ProfessionalReviewPanel`, `ProvenanceDisclosure`, `coverage.ts` shows type-import migration only (`property-profile` → generated `contract`), zero rendered-output change. `FactsTable`/`ZoningSection` changes are the `.table-scroll` wrapper (additive, D2 fix) and the runtime-narrowing helper in `UnsupportedSection` (same rendered result). `MissingInputsSection` adds the D4 shared-reason note and per-field-exception filtering; `ConflictsSection` adds the derivation gloss — both additive.
- All 8 pre-existing e2e spec files (`primary-journey`, `failures`, `honesty`, `keyboard`, `no-match`, `partial-and-conflict`, `validation`, plus helpers/harness) are untouched by the diff and green in CI, so the M2-T001 visual contract they describe still holds.

---

## Defect summary

| ID | Severity | Blocking? | Description |
|----|----------|-----------|-------------|
| D1 | Major | Recommended blocking correction (no scenario breach) | Failure/outcome states have no `role="alert"`/`aria-live`; live loading region unmounts before outcome; focus dropped after retry/state change (both screens; `FailureState.tsx`, `ConfirmScreen.tsx`, `PropertyLookup.tsx`) |
| D2 | Minor | No | No `.secondary-button:disabled` styling; disabled confirm affordance visually identical to actionable buttons (`globals.css` line 182 ff., `ConfirmScreen.tsx` line 337) |
| D3 | Minor | No | `confirm-bad-param` state renders without an `h1` (`ConfirmScreen.tsx` line 437) |
| D4 | Minor | No | Landmark/flood values duplicated on Confirm (Zoning mapped-features table + Flags section) |
| D5 | Minor | No (needs browser) | Focus ring at 35% alpha likely below 3:1 focus-appearance contrast (`globals.css` line 52) |
| D6 | Info | No | Legend-placement order differs between screens; scattered inline styles bypass tokens (pre-existing pattern) |

## Carry-forwards for the first browser-accessible session

- **CF-1 (D1):** Screen-reader announcement of failure/success arrival — not answerable from any trace; needs manual NVDA/VoiceOver. Traces cannot substitute.
- **CF-2 (D5 + contrast):** Focus-ring visibility and rendered contrast — playwright-evidence traces for the `responsive-a11y.spec.ts` keyboard-toggle and keyboard-retry journeys contain focused-element screenshots that would answer this.
- **CF-3:** Focus ring/`details` behavior inside `.table-scroll` at 360px — the `phone-360` Property/Confirm traces from `responsive-a11y.spec.ts`.
- **CF-4 (D4):** Perceived duplication weight of flags on the Confirm card — the `confirm-journey.spec.ts` S1 trace screenshots.
- **CF-5:** Overall spacing rhythm / "premium, not municipal" gestalt — any full-page trace screenshot; code strongly indicates conformance but gestalt is inherently pixel-level.

## Agent-memory statement (M0-T013 G3 carry-forward 4)

I wrote exactly two files, both under my own agent-memory directory and nowhere else: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\agent-memory\visual-quality-reviewer\project_review-environment-and-baselines.md` and `...\visual-quality-reviewer\MEMORY.md`. No implementation file, ledger file, report file, or git/gh write command was touched; all repository access was read-only (Read/Grep/Glob and read-only `git diff`/`git log`/`ls`).

## Verdict

The Confirm screen genuinely extends the accepted design system, satisfies the packet's S1/S6/S7 visual requirements with committed executable evidence, resolves D1–D5 from M2-T001 as specified, and introduces no visual regression. Defect D1 (no announcement/focus management on state changes) is a real accessibility gap I recommend the orchestrator record as a blocking correction or tracked defect before client-facing exposure; it does not breach any committed acceptance scenario of this task.

VISUAL-QUALITY: PASS
