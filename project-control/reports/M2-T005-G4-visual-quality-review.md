# M2-T005 — G4 Independent Visual-Quality Review

> Orchestrator preservation note: reviewer return saved VERBATIM from the agent-return channel (transport entity-decoding only, per the report-preservation rule in .claude/rules/project-control.md). Reviewer: visual-quality-reviewer. Received 2026-07-17, session 11.

**Reviewer:** visual-quality-reviewer (independent; did not produce this work; author of the original M2-T002 defect table D1–D5 being corrected here)
**Target:** branch `task/M2-T005-a11y-announcements` @ `39c39a5` (implementation commit `689d118`; G2-evidence-only delta `689d118..39c39a5` verified to touch only `project-control/reports/M2-T005-G2-selfcheck.md`), worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T005`
**Method and honest limitation:** No browser/npm exists on this machine (documented CI-only model). This is a code/token/test-level review of the full `git diff fb67d5a..39c39a5 -- apps/web` (14 files, +1157/−47), cross-checked against my own M2-T002 defect wording read verbatim, the task packet S1–S6, the design-system tokens, one locally executed byte-scan (N1), and the orchestrator-captured CI evidence in the committed G2 self-check (PR #33, both push and pull_request events green: vitest `Test Files 13 passed (13)` / `Tests 156 passed (156)`; Playwright `53 passed` = 43 pre-existing + 10 new). I did not rely on producer screenshots (none were offered). Pixel-dependent claims remain explicitly deferred to CF-2 below.

**Scope check:** `git diff --name-only fb67d5a..39c39a5` shows only `apps/web/**` plus the two permitted report files. The two M2-T006 A1 overlap files (`contract.ts`, `validate-profile.test.ts`) are untouched. In scope.

---

## Per-defect resolution assessment

### D1 (Major) — announcement + focus management on both screens: RESOLVED, and the design is better than my original suggestion

My original recommendation named `role="alert"`/`aria-live` on the failure cards as the missing piece. The producer instead built a **persistent announcer** (`OutcomeAnnouncer.tsx`: always-mounted visually-hidden `div role="status" aria-live="polite" aria-atomic="true"`), with the failure cards deliberately carrying **no** live semantics (asserted negatively in every one of the 11 parametrized component cases: `expect(card).not.toHaveAttribute("role","alert")` / `not.toHaveAttribute("aria-live")`). **I endorse this deviation explicitly.** The defect I found was structural — a live region that unmounted before the outcome. `role="alert"` on a *mounting* card is exactly the pattern that is unreliable across AT and is the classic double-announce source; a never-unmounting region whose text changes is structurally immune to the original failure, and pairing it with a focus move makes assertive interruption the wrong politeness level anyway. Choosing `role="status"` (polite) over `alert` for failure severity is correct here: every failure arrives ≤12 s after a user-initiated action, focus simultaneously lands on the failure heading (focus echo reads the title), and nothing is time-critical or destructive. Assertive would have collided with the focus echo.

Verified mechanics, at file level:

- **Exactly-once (S1):** announcer is the only live region carrying outcome text; DOM-level exactly-once asserted by `liveRegionsContaining(...)===1` in component tests and `liveRegionCount(...)===1` in e2e across `[aria-live]`, `[role=alert]`, `[role=status]`. Coverage is genuinely complete: all 11 rendered failure kinds incl. all four upstream states on Property (parametrized), representative states + success on Confirm (identical shared wiring), full mapping locked in `announce.test.ts` (15 tests, distinctness across upstream states, `aborted → ""`, honesty test excluding "best"/"verified" — consistent with PRD §6/§12).
- **Repeat-outcome re-announcement:** message derived `loading ? "" : announcementForOutcome(...)` on both screens — cleared during flight so a retry failing the same way produces a genuine text change. Correct use of live-region change semantics; asserted in both retry tests (`textContent === ""` during loading).
- **Focus (S2):** shared `FailureTitle` (`h2.failure-title tabIndex={-1} data-outcome-heading`) across all nine failure components; success identity `h2` on both screens carries the same attributes; arrival effect keyed on `result`/`[loading, outcome]`, which change **only** on arrival — so a client-invalid submit cannot steal focus (regression-asserted: `document.activeElement` unchanged and announcement unchanged after invalid submit). Retry: `retryFocus` flag → `LoadingStages focusOnMount` takes focus when the Retry button unmounts; never `body` (asserted at every checkpoint in e2e tests 3 and 6, with an 800 ms delayed route making the loading phase observable in real Chromium).
- **Focus-steal mid-typing (disclosed tradeoff):** if the user is mid-typing a *new* query when a slow outcome arrives, arrival focus wins. This is what packet S2 demands ("focus lands on the outcome container/heading" deterministically), the window only exists during a lookup the user initiated, and the producer disclosed it rather than hiding it. Acceptable; folded into CF-1 for real-user judgment.
- **Programmatic-focus ring via `:focus`:** correct call. Browsers do not reliably apply `:focus-visible` to script-moved focus; `[data-outcome-heading]:focus, [data-focus-target]:focus` with the ring token guarantees sighted keyboard users see where focus landed. Side effect (observation O1, cosmetic, non-blocking): a mouse click on an outcome heading now also paints the ring, since `:focus` doesn't distinguish modality. This is the known cost of the only reliable technique; I would not trade it back.
- **Residual, honestly disclosed:** the perceived combination of polite status + focus echo — and, my addition, the pre-existing `CompletenessBanner role="status"` mounting on Property success with different text — can only be judged with real NVDA/VoiceOver. DOM-level exactly-once is the strongest automatable claim and it is proven. Stays CF-1 with a documented one-line fallback.

**D1 verdict: resolved at the standard I set, with a defensible upgrade over my literal recommendation.**

### D2 — `.secondary-button:disabled`: RESOLVED

`globals.css:209–214`: `background: var(--surface-inset); color: var(--text-tertiary); border-color: var(--border-quiet); cursor: not-allowed` — fully token-based, deliberately mirrors the pre-existing `.text-input:disabled` grammar (consistency, not invention). E2e asserts computed styles (`not-allowed`, `rgb(244,244,241)`, `rgb(111,111,105)`) plus `toBeDisabled()`. Disabled contrast has no WCAG requirement and #6f6f69 on #f4f4f1 (~4.6:1) remains readable. Resolved.

### D3 — h1 in `confirm-bad-param`: RESOLVED

`ConfirmScreen.tsx` bad-param card now renders `<h1 className="failure-title">No property selected</h1>`; the "Step 2" h1 never mounts in that state, so the page has exactly one h1 (e2e asserts `h1` count === 1; component tests cover both bad-param variants and assert zero fetch). `.failure-title` sets explicit `font-size: 1.05rem; font-weight: 600; margin` (globals.css:404–408), so the h1→h2 element swap has zero visual delta against the accepted card. Observation O2 (cosmetic, non-blocking, pre-dating this task's scope): that page's title now renders at 1.05rem while other pages' h1s are inline-styled 1.4rem — a rhythm nit belonging to the pre-existing D6/inline-style informational item, not to D3, which only required correct hierarchy.

### D4 — flags exactly once on Confirm: RESOLVED, first-listed option, no information loss

The producer took my first-listed option (filter the flag fields out of the Zoning table on Confirm). Verified:

- `FLAG_FEATURE_FIELDS` is derived from `FLAG_FEATURES` (`ConfirmScreen.tsx:75`) — single source, cannot drift, matches `mappedFeatureView().feature` source-column keys (`contract.ts:241–253`).
- `ZoningSection` gains `excludeFeatures`/`featuresHeading`/`featureNote` props with **defaults preserving the accepted Property rendering exactly**; a Property-side regression test plus an e2e check assert the unfiltered table still shows all four flags.
- No information loss: `FlagRow` (ConfirmScreen.tsx:120–160) retains value, `CoverageBadge`, and `ProvenanceDisclosure` per flag, plus the honest unknown states ("unknown, never assumed absent") the table never had.
- Nothing silently hidden: a visible `featureNote` on the Confirm table states where the flags live ("each official value is shown once"), and the all-excluded edge renders an honest variant note instead of the misleading "No mapped features…". The filter keeps `feature === null` entries in the table — correctly conservative (never hide what you can't identify).
- Exactly-once asserted both component-level (`getAllByText(label).toHaveLength(1)` for all four labels) and e2e (values present in `confirm-flags`, absent from `zoning-section`).

Hierarchy stays coherent: the Confirm card order (identity → facts → zoning → flags) is unchanged; the table just stops repeating four rows. Resolved cleanly.

### D5 — focus-ring token: RESOLVED at code level; pixels stay CF-2

Token changed `rgba(31,79,130,0.35)` → `rgba(31,79,130,0.9)` (globals.css:55). My independent arithmetic: 0.9-alpha blend on white = rgb(53, 97, 143); relative luminance ≈ 0.113; contrast **≈ 6.4:1 against white** (producer's ≈6.5:1 claim is honest within rounding), ≈ 5.9:1 against `--surface-inset` #f4f4f1 and similar against `--surface-page` #fafaf8 — every surface the ring appears over is light, so 3:1 focus-appearance clears with >90% margin everywhere it can render. Keeping 0.9 rather than 1.0 preserves the design's softness without contrast risk — accepted. **What CF-2 still needs in a browser:** the rendered ring as actually composited (box-shadow spread, radius clipping, ring vs. the accent-colored primary button's own edge, and the ring inside `.table-scroll` at 360px = CF-3) — the new spec runs with `trace: "on"`, so the CI Playwright traces for the two keyboard-retry journeys and `tabUntil` steps contain focused-element screenshots that should close CF-2 without owner hardware.

### N1 — api.test.ts hygiene: RESOLVED, verified by my own execution

I ran an independent byte scan on the checked-out file: **0 raw control bytes, exactly one `\u0000` six-character escape**. The `Bin 10948 -> 10953` line in the diffstat is the correct, expected artifact of the *old* blob containing the NUL — git flags a diff binary if either side is; from this commit forward the file diffs as text, which is precisely the N1 ask. The laundering test constructs the identical runtime string, so no assertion weakened.

---

## Token / design-system findings

- All new CSS is token-based: focus-ring token reused for the programmatic rule, D2 uses `--surface-inset`/`--text-tertiary`/`--border-quiet`, the D4 note uses `.section-note`. **Zero new hardcoded colors** in the diff (the two rgb literals live in a test asserting token values, which is correct practice).
- `.visually-hidden` (globals.css:610–620) is the correct clip-pattern (absolute/1px/clip/overflow-hidden) — pre-existing, reused, **not** `display:none`, so AT reads the announcer. Responsive behavior cannot be affected by a 1px absolutely-positioned element; the only other structural change is a style-free wrapper `div` around the outcome region.
- No default-template regression: every change extends the accepted hand-rolled vocabulary (`FailureTitle` reuses `.failure-title`, announcer invisible, D4 uses existing table/note grammar). Copy changes are confined to SR-only strings mirroring visible titles plus the D4 note — no coverage-enum wording, no "best"/"verified" (unit-locked).
- Regression surface: all 11 pre-existing e2e spec files byte-identical; both modified vitest files are additive-only (import-line widening plus appended describes); CI green on the full 156/53 totals.

## Carry-forward status (from my M2-T002 report)

| CF | Status after M2-T005 |
|----|----|
| CF-1 (real-SR announcement) | **Open, sharpened.** The question changed from "is anything announced?" (now structurally yes) to "is the polite-status + focus-echo (+ Property-success CompletenessBanner mount) combination perceived as clean single announcement?" Manual NVDA/VoiceOver, first browser session. Documented one-line fallback exists. |
| CF-2 (focus-ring pixels/contrast) | **Materially narrowed.** Token now arithmetically ≈6.4:1; only rendered-composite confirmation remains, and the new `trace: "on"` artifacts likely close it from CI traces alone. |
| CF-3 (ring/`details` in `.table-scroll` @360px) | Open, unchanged; same trace source. |
| CF-4 (flag duplication weight) | **Closed by D4** — duplication no longer exists; nothing left to eyeball. |
| CF-5 (premium gestalt) | Open, unchanged; nothing in this diff plausibly degrades it. |

## Defect table (this review)

| ID | Severity | Blocking? | Description |
|----|----------|-----------|-------------|
| — | — | — | **No new Major or Minor defects.** All five original defects (D1–D5) and N1 verified resolved as recorded. |
| O1 | Observation | No | Mouse click on an outcome heading paints the focus ring (`:focus` modality tradeoff, `globals.css:80–85`) — cosmetic, inherent to the only reliable programmatic-focus technique; assess alongside CF-2 traces. |
| O2 | Observation | No | Bad-param page title renders at 1.05rem (`.failure-title`) vs 1.4rem inline-styled h1 elsewhere — belongs to the pre-existing D6 inline-style informational item, not new to this diff. |
| O3 | Observation | No | On Property success, the pre-existing `CompletenessBanner role="status"` mounts alongside the announcer update (different text; DOM exactly-once for the outcome message holds) — folded into CF-1's manual-session checklist. |

## Verdict

Every defect I raised in M2-T002 is genuinely resolved at the standard I set: D1's fix is structurally sounder than my literal recommendation and I endorse the `role="status"`-not-`alert` decision; D2/D3/D4/D5 match their recorded resolutions with token discipline, no information loss, and no visual regression; N1 is byte-verified by my own execution. The diff is tightly bounded to the defect list, all suite changes are additive, and CI evidence (156/156 vitest, 53/53 Playwright on PR #33) covers the executable half. Remaining pixel/SR questions are honestly named carry-forwards (CF-1, CF-2 narrowed, CF-3, CF-5), none of which a non-browser session can close and none of which blocks this correction task.

**VISUAL-QUALITY G4: PASS** (no blocking corrections; CF-1/CF-2/CF-3/CF-5 remain tracked for the first browser-accessible session).
