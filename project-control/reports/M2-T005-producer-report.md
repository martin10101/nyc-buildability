# M2-T005 Producer Report — Confirm/Property a11y announcement + focus (D1) and minors D2–D5 + N1

- **Task:** M2-T005
- **Producer:** frontend-engineer
- **Worktree/branch:** `.claude/worktrees/M2-T005`, `task/M2-T005-a11y-announcements` (based on main `3992caf`; worktree HEAD at claim `2a996a3`)
- **Requested status:** `awaiting_gate` (G2 self-check evidence below is complete for everything executable on the owner PC; vitest/Playwright/lint/typecheck/build execution is CI-only by policy — the orchestrator must run CI on this branch and attach the run as the executable half of G2 before dispatching G3)
- **Date:** 2026-07-17

## 1. Objective delivered

Bounded correction of the M2-T002 visual-quality defect list — no redesign, no contract change, no coverage-label change. Every change is either a listed defect fix or a test proving one.

- **D1 (Major):** every outcome arrival (success + all failure states) on BOTH screens is announced to assistive technology exactly once through a persistent live region, and focus is managed deterministically (outcome heading after arrival; loading card after retry; never `body`).
- **D2:** `.secondary-button:disabled` styled token-based (inset surface, tertiary text, quiet border, `not-allowed` cursor).
- **D3:** the `confirm-bad-param` state now renders an `h1`.
- **D4:** landmark/flood/historic flags render exactly once on Confirm — kept in the dedicated flags section (which also carries the honest unknown states); filtered out of the shared zoning mapped-features table there, with a visible note saying where they live. Property screen table unchanged.
- **D5:** focus-ring token alpha raised 0.35 → 0.9 (`rgba(31,79,130,0.9)`; blended on white ≈ rgb(53,97,143), ≈6.5:1 — clears the 3:1 focus-appearance guideline at code level; rendered-pixel verification remains carry-forward CF-2).
- **N1:** the raw NUL byte in `api.test.ts` replaced with the six-character source escape (backslash-u-0000, six source characters); the file now contains zero raw control bytes.

## 2. D1 design (the load-bearing decisions)

1. **Persistent announcer, not `role="alert"` on the cards.** New `OutcomeAnnouncer` — a visually-hidden, always-mounted `div role="status" aria-live="polite" aria-atomic="true"` rendered once per screen. Because it never unmounts, its text updates are reliably announced; the old defect (loading live-region unmounting and swallowing the outcome) is structurally impossible.
2. **Exactly-once:** the announcer is the ONLY live region carrying outcome text. Failure cards deliberately carry no `role="alert"`/`aria-live` (asserted in tests), so mounting them cannot double-announce. The message is cleared to `""` while a lookup is in flight, so a retry that fails the SAME way genuinely changes the region text and re-announces (live regions only announce on change).
3. **Deterministic focus:** every failure title is now a shared `FailureTitle` (`h2.failure-title` + `tabIndex={-1}` + `data-outcome-heading`); the success identity `h2` on both screens carries the same attributes. On arrival (state change `result`/`outcome`, which changes ONLY on arrival), the screen focuses `[data-outcome-heading]` inside the outcome container. On retry, the unmounting Retry button no longer drops focus to `body`: a `retryFocus` flag makes the loading card (`tabIndex={-1}`, `data-focus-target`) take focus, then arrival moves focus to the new outcome heading. Initial (non-retry) lookups never pass the flag, so loading never steals focus from the form; a client-invalid submit changes no result and moves no focus (D5 behavior preserved and now asserted).
4. **Visible programmatic focus:** browsers do not reliably apply `:focus-visible` to script-moved focus, so `[data-outcome-heading]:focus, [data-focus-target]:focus` get the focus-ring token explicitly.
5. **Announcement copy** (`src/lib/announce.ts`) mirrors the visible card titles, prefixed "Lookup complete/rejected/failed:"; `aborted` → `""` (a superseded request must announce nothing). Unit-locked per outcome kind including all four upstream states, with an explicit honesty test (no "best"/"verified").

**Disclosed residual (CF-1):** the packet requires BOTH a live-region announcement AND a focus move. A real screen reader will speak the focused heading (focus echo) in addition to the single polite live-region message. At the DOM/ARIA level exactly one announcement is emitted per event (asserted); whether the focus echo + status combination is perceived as a double announcement can only be judged in the CF-1 manual NVDA/VoiceOver session, which no trace can substitute. If that session judges it a defect, the documented fallback is suppressing the announcer message when the focus move succeeds (one-line change in each screen's `announcement` derivation). I chose polite (`role="status"`) over assertive `role="alert"` to keep the combination as quiet as possible.

## 3. Files changed (complete list, all under `apps/web/**` + this report)

New:
- `apps/web/src/lib/announce.ts` — outcome → announcement mapping (presentation-only copy).
- `apps/web/src/components/property/OutcomeAnnouncer.tsx` — persistent live region.
- `apps/web/src/lib/__tests__/announce.test.ts` — 15 unit tests (every kind, all 4 upstream states distinct, aborted empty, honesty).
- `apps/web/src/components/confirm/__tests__/confirm-entry.test.tsx` — D3 component tests (h1 in both bad-param variants; no fetch).
- `apps/web/e2e/a11y-announcements.spec.ts` — 10 new Playwright journeys (S1/S2/S3/S6).

Modified:
- `apps/web/src/components/property/FailureState.tsx` — `FailureTitle` helper; all 9 state components' h2 titles now render through it (DOM change: `tabindex="-1"` + `data-outcome-heading` attributes on the same `h2.failure-title`).
- `apps/web/src/components/property/LoadingStages.tsx` — `tabIndex={-1}`, `data-focus-target`, optional `focusOnMount` prop (focus itself on mount when a retry initiated the loading). `aria-live="polite"` kept as-is.
- `apps/web/src/components/property/PropertyLookup.tsx` — announcer render + message derivation; arrival-focus effect keyed on `result`; `retryFocus` flag; identity `h2` focus target; outcome render wrapped in a `div ref` (structural only, no CSS effect).
- `apps/web/src/components/confirm/ConfirmScreen.tsx` — same announcer/focus/retry pattern; identity `h2` focus target; D4 `ZoningSection` props (`excludeFeatures`/`featuresHeading`/`featureNote`); D3 bad-param `h2` → `h1` (same `.failure-title` class).
- `apps/web/src/components/property/ZoningSection.tsx` — optional `excludeFeatures`/`featuresHeading`/`featureNote` props (defaults preserve the accepted Property rendering exactly); `data-testid="zoning-section"` added; honest empty-text variant when all features are excluded flags.
- `apps/web/src/app/globals.css` — D5 token alpha; D2 `.secondary-button:disabled`; programmatic-focus ring rule.
- `apps/web/src/lib/__tests__/api.test.ts` — N1 byte-level fix only (raw NUL byte replaced by the backslash-u-0000 source escape); no assertion changed.
- `apps/web/src/components/property/__tests__/property-lookup.test.tsx` — additive: parametrized S1/S2 pack (11 failure cases covering all rendered outcome kinds incl. all 4 upstream states), success announcement/focus, retry clear/re-announce/focus, invalid-submit no-focus-steal, D4 Property regression. Import line gained `waitFor`.
- `apps/web/src/components/confirm/__tests__/confirm-screen.test.tsx` — additive: failure/success/validation-failure announcement + focus, retry focus journey, D4 exactly-once pack. Import line gained `fireEvent`, `waitFor`.

**No existing test assertion was modified, weakened, or deleted — every suite change is additive.** No file outside `apps/web/**` and this report was touched (`git status` clean otherwise).

## 4. Contracts/schema changed

None. `packages/contracts/**`, `services/**` untouched. The frontend still consumes only documented contract keys; announcements are derived from already-classified typed outcomes and contain no data values beyond the echoed BBL.

## 5. Acceptance scenarios → evidence mapping

| Scenario | Where proven |
|---|---|
| **S1** exactly-once announcement, every failure state + success, both screens; loading handoff cannot swallow | Component: `property-lookup.test.tsx` it.each over 11 cases (all rendered kinds + all 4 upstream states) + success case — each asserts announcer text, exactly one live region containing the message, failure card has no `role=alert`/`aria-live`; `confirm-screen.test.tsx` no_match/validation_failure/success equivalents (mechanism shared, wiring proven); `announce.test.ts` locks the full mapping. E2e: `a11y-announcements.spec.ts` tests 1, 2, 4, 5 (real harness) with `liveRegionCount(...) === 1`. Structural swallow-proofing: announcer never unmounts (code + persistent testid across states). |
| **S2** focus on outcome heading after arrival and after keyboard retry; never body | Component: `document.activeElement` asserted per case (arrival → `[data-outcome-heading]`; retry → `loading-stages` then heading; invalid submit → unchanged). E2e: `activeElementInfo` assertions in tests 1–7, including keyboard-only retries on both screens with the route delayed 800 ms so the loading-phase focus is observable; `isBody === false` asserted at every checkpoint. |
| **S3** D2/D3/D4/D5 | D2: e2e computed-style assertions (`not-allowed`, `rgb(244,244,241)` bg, `rgb(111,111,105)` fg) + existing `toBeDisabled`. D3: `confirm-entry.test.tsx` (level-1 heading, both variants, zero fetch) + e2e h1 assertions (`h1` count = 1 on the bad-param page). D4: component + e2e exactly-once packs (each flag label count 1; values only in `confirm-flags`; zoning table keeps non-flag features and states where flags live; Property regression asserts the unfiltered table). D5: token change committed; `keyboard.spec.ts` still asserts a visible focus ring; pixel contrast stays CF-2. |
| **S4** hygiene | `python` byte scan: `raw control bytes present: NONE`, `escape sequence count: 1` (exact outputs in section 6). The laundering test still constructs the identical runtime string (no_<NUL>match), so the RAW-comparison assertion is unchanged. Note: `git diff` against main still SHOWS "binary" for this one commit because the OLD committed blob contains the NUL; the new blob is pure text, so the file diffs as text from this commit forward (that is exactly the N1 ask). |
| **S5** regression | No existing assertion touched (additive-only diffs on both test files; e2e additions are a new spec file; the 11 pre-existing spec files are byte-identical — `git status` shows no modification). DOM changes to accepted surfaces are limited to: attribute additions (`tabindex`, `data-outcome-heading`, `data-focus-target`, `data-testid="zoning-section"`), one wrapper `div`, the hidden announcer, D3's `h2`→`h1`, and the D4 Confirm-only table filter + note — each traced to a listed defect above. Copy changes: D4 note/heading on Confirm only + new SR-only announcement strings; no coverage-label or enum wording touched. Full suites run in CI (see section 6). |
| **S6** keyboard-only journey | E2e test 7: Tab→input, type, Enter, arrival-focus assertion, Tab→confirm link, Enter, Confirm arrival focus + announcement, Tab→way-back link, Enter, back at the form — zero mouse events. |

## 6. Commands run and results (exact)

Executed locally (read-only or byte-level, no npm/node):

1. N1 replacement (Python, byte-level; done this way deliberately so no tool JSON layer could re-decode the escape into a literal byte):
   - Pre-check asserted exactly one NUL; replaced `no_<NUL>match` with `no_` + `\` + `u0000match`; post-check asserted zero NULs.
   - Output: `b'      stub(jsonResponse({ state: "no_\\u0000match" }, 404)),'` / `control bytes remaining: 0`
2. Verification scan:
   - `python` full-file control-byte scan → `raw control bytes present: NONE`, `escape sequence count: 1`
3. `git status --short` (scope check) → only the files listed in section 3, all under `apps/web/**`.
4. `git diff --numstat` → recorded in-session; `api.test.ts` shows `- -` (binary OLD side; see S4 note).
5. Wiring greps (`OutcomeAnnouncer|data-outcome-heading|data-focus-target|LoadingStages`, `Mapped features`, `aria-live|role=`) → all consumers/attributes present exactly where section 3 says; no unexpected live regions besides the pre-existing `bbl-error` inline region, `LoadingStages`, and `CompletenessBanner` (all carrying different text than the outcome announcements, so the exactly-once filters hold).

**NOT executed locally (honest disclosure, low-storage policy — no node_modules/Playwright browsers on this machine ever):** `npm run lint`, `npm run typecheck`, `npm run build`, `npm test` (vitest), `npm run test:e2e` (Playwright). These run in GitHub Actions (`web (lint + typecheck + build)` and `web-e2e (vitest + Playwright vs recorded-official-fixture API)` jobs). I am NOT claiming they pass; the orchestrator must trigger CI on this branch and capture the run URL/result as G2 executable evidence. Everything in section 5 that says "asserted" describes committed test code whose pass/fail comes from that CI run.

## 7. Expected vs actual

- Expected CI totals: Playwright 43 existing + 10 new = **53 journeys**; vitest existing suites + ~37 new tests (15 announce, 15 property-lookup, 5 confirm-screen, 2 confirm-entry). Actual: pending CI (see above).
- Expected: `git show` of this branch's commit diffs `api.test.ts` as binary ONE last time (old blob), then text forever after. Local byte evidence already actual (section 6).

## 8. Assumptions and defaults

1. D4 placement: the visual review offered either location; I kept flags in the dedicated flags section (it carries the honest unknown/never-assumed-absent states and matches PRODUCT_FLOW step 2's required flag card) and filtered the zoning table on Confirm only. A visible note explains the placement — nothing silently hidden.
2. Polite (`role="status"`) rather than assertive announcements — least double-speak risk; failure text is also fully readable at the focused heading.
3. Announcement wording is new SR-facing copy mirroring existing card titles (no legal semantics, honesty-tested). If reviewers want different wording, it is one table in `announce.ts` + matching test strings.
4. `focusOnMount` loading-focus applies ONLY to retry-initiated lookups; form submits keep native focus (submit button/input), which is not `body`.
5. D5 alpha 0.9 (not 1.0) keeps a trace of the design's softness while clearing 3:1 with wide margin; trivially adjustable if the visual reviewer prefers solid.

## 9. Known limitations

1. **Real screen-reader behavior is unverified** (CF-1 stands): the focus-echo + polite-status interplay in section 2 needs the manual NVDA/VoiceOver session; DOM-level exactly-once is the strongest claim automatable here.
2. `client_timeout` is announcement-mapped and unit-tested, but not exercised at screen level in these tests (would need fake timers against the 12 s budget); the screen mechanism is outcome-kind-agnostic. Existing M2-T001 e2e still covers the state's rendering.
3. The Confirm screen's screen-level announcement tests cover representative states (no_match, validation_failure, source_unavailable retry, success), not all ten — the parametrized all-states pack runs on the Property screen and both screens share the identical `OutcomeAnnouncer`/`FailureTitle`/effect wiring.
4. Deterministic arrival focus means: if a user is mid-typing a NEW query when a slow outcome arrives, focus moves to the outcome heading (packet S2 requires deterministic focus on arrival; noting the tradeoff explicitly for the G3 reviewer).
5. D5/CF-2 and CF-3/CF-4/CF-5 pixel questions remain carry-forwards; the new spec's `trace: "on"` artifacts add focused-element screenshots that should answer CF-2.
6. jsdom focus assertions are a simulation; the same assertions run in real Chromium in the new e2e spec, which is the authoritative half.

## 10. Security / provenance impact

None negative. No new inputs, storage, or network paths; announcements are derived exclusively from already-classified typed outcomes (no raw server text — bounded upstream as before); the announcer renders plain text through React (no `dangerouslySetInnerHTML` anywhere, unchanged); no legal logic entered the frontend; coverage labels and provenance rendering untouched; nothing persistent written to the user device.

## 11. New risks / dependencies

1. If CI reveals a timing flake in the two keyboard-retry journeys (800 ms route delay window), the fix is raising the delay — noting proactively.
2. The `FLAG_FEATURE_FIELDS` filter list lives beside `FLAG_FEATURES` in `ConfirmScreen.tsx`; if a future task adds a flag row it must extend ONE array (they are derived from the same constant, so they cannot drift).

## 12. Recommended next tasks

1. Orchestrator: trigger CI on `task/M2-T005-a11y-announcements`, capture the run as G2 evidence, then dispatch G3 (human-journey-reviewer) and G4 visual re-review (visual-quality-reviewer) per the packet.
2. First browser-accessible session: execute CF-1 (manual SR pass over both screens' arrivals/retries — decides the focus-echo question in section 2) and CF-2 (focus-ring pixels, now with the 0.9-alpha token).
3. Carry-forward unchanged from M2-T002: production CORS/proxy decision (D8) before any deployment; `status_dimensions` display follow-up.

## 13. Report path

`project-control/reports/M2-T005-producer-report.md` (this file, inside the M2-T005 worktree).
