# M5-T115 producer report — D-086 P2 (address + confirmation slice)

Producer: frontend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t115`
(branch `task/M5-T115-d086-p2-address-confirm`). Parent / claim seam:
`01856916eba27de2cbdebbf0c305693063281976`. Directive regime: D-086 (R001–R004),
D-083-R001, D-066-R001, D-087-R001/R002.

## 0. What P2 is, and the posture I took

P2 applies the accepted P1 visual/state design (`docs/design/ui-cleanup/P1-VISUAL-STATE-SPEC.md`
§5.1/§5.2) to the LIVE `/property?ruleeval=on` search → confirm flow. On inspection the
**behavioural** P2 requirements were already implemented and heavily tested on this surface
(no-auto-pick, keyboard+touch suggestions, manual fallback preserving the typed text, a distinct
recovery per typed error category spoken once, entered-vs-matched-vs-PLUTO identity distinctness,
equal-ID collapse, the stable-action-area CLS behaviour, and the full set of concise map states).
The owner's D-086 ask is "more visually explanatory" WITHOUT losing meaning (D-086-R003). I therefore
made **additive, meaning-preserving** changes that (a) close the one concrete assessment gap for this
surface — the environment badge + professional-review line hidden at ≤700px (DB-083 f / HJ ADV-4) —
(b) make the confirm-card identity comparison explicit with a label, (c) frame the BBL path as an
alternative and give the four `lib/bbl.ts` errors a distinct, non-generic presentation, and (d) apply
P1 token/spacing polish through search/confirm/autocomplete/map CSS. **No existing user-visible string,
testid, role, DOM order, or backend contract was changed or removed.** Every changed string is NEW and
listed in §4. Meaning-change items (P1 §10 MR-1..MR-8) stay NOT adopted.

## 1. Files changed (all inside allowed_paths; 7 files)

- `apps/web/src/components/architect/ArchitectEntry.tsx` — **PropertySearch block only** (§ scope
  rule): added the always-visible environment badge + review line, the BBL-alternative framing note,
  and distinct BBL-error styling/`aria-invalid`/testid. Every other part of the file is byte-unchanged.
- `apps/web/src/components/address/AddressConfirmCard.tsx` — added the static "City-matched address"
  label above the matched line (identity comparison, AS-2). Nothing else changed.
- `apps/web/src/app/property/architect.css` — appended a P2 block of **new** search/confirm-scoped
  selectors + polish that layers over existing search/autocomplete/map rules. No shared selector
  (`.architect-disclosure`, `.architect-eyebrow`, shell rules) was edited.
- `apps/web/src/components/architect/__tests__/entry.test.tsx` — new describe "D-086 P2 search surface".
- `apps/web/src/components/address/__tests__/address-confirm.test.tsx` — two new AS-2 label tests.
- `apps/web/e2e/confirm-journey.spec.ts` — new live AddressConfirmCard AS-2 journey.
- `apps/web/e2e/responsive-a11y.spec.ts` — new phone/tablet/desktop env-badge visibility test.

Untouched (verified present + correct, cited as evidence, NOT edited): `AddressResolutionScreen.tsx`,
`AddressAutocomplete.tsx`, `SuggestionChooser.tsx`, `AddressForm.tsx`, `AddressOutcomeCards.tsx`,
`LotOutlineMap.tsx` and their existing suites — they already carry the P2 behaviour.

## 2. Per-AS evidence

- **AS-1 (one search/recovery area).** Suggestions with keyboard + touch and no auto-pick:
  `AddressAutocomplete.tsx:170-206` (arrow/Enter, `role=listbox/option`, `onClick`), no default
  selection in `SuggestionChooser.tsx:29,59-71`; tests `autocomplete.test.tsx` "resolves only an
  explicit keyboard pick", "Enter with no highlighted suggestion triggers the explicit /search",
  `address-resolution.test.tsx` S3. BBL alternative is a native `<details>` framed as an alternative
  (`ArchitectEntry.tsx` PropertySearch); manual fallback keeps the typed text
  (`AddressResolutionScreen.tsx:225-229`, test S8). Distinct recovery per typed error, announced once
  (`AddressAutocomplete.tsx:39-60`, `address/AddressOutcomeCards.tsx:211-285`; tests
  `autocomplete.test.tsx` "reads each failure reason with its own copy", `address-resolution.test.tsx`
  S5/S7). Four distinct BBL errors verbatim from `lib/bbl.ts`: NEW `entry.test.tsx` four-error test.
- **AS-2 (identity comparison).** Entered vs matched vs PLUTO kept distinct: entered
  (`AddressConfirmCard.tsx:204-234`), matched with NEW explicit label (`:188-201`), PLUTO record
  (`:420-430`). Equal-ID collapse: `:160-162` + test `address-confirm.test.tsx` S10 AS-2. NEW tests:
  `address-confirm.test.tsx` "matched line carries an explicit 'City-matched address' label" +
  absent-when-no-normalized-street; e2e `confirm-journey.spec.ts` AS-2.
- **AS-3 (stable action area).** Record-address renders OUTSIDE the interactive block, after both
  actions and before the Meta footer (`AddressConfirmCard.tsx:420-431`); the NEW static label renders
  on first paint so it never shifts the CTA. Proof: `address-confirm.test.tsx` S11 rider a (structural,
  `childIds` invariant) + `responsive-a11y.spec.ts` DB-035 pixel CLS at 360/768/1280 (exact-equality).
  City warnings verbatim above Continue: `AddressConfirmCard.tsx:236-257`, test S1.
- **AS-4 (map states).** `LotOutlineMap.tsx` already renders rendered / unavailable / no-WebGL /
  render-error / no_outline / multiple_features / invalid_geometry / route_absent as distinct truthful
  states, keeps the "±20 ft / Approximate" accuracy + DCP attribution + ZoLa escape hatch without the
  map, and a basemap-layer error (`:477-483` per-layer `contextLayers`) never tears down a rendered
  parcel. Tests `lot-outline-map.test.tsx`, e2e `lot-outline.spec.ts`. P2 touched only map CSS polish.
- **AS-5 (preservation).** §29 stays verbatim in the global footer via `REQUIRED_DISCLAIMER`
  (`lib/disclaimer.ts`), never retyped — the NEW env note is the distinct internal-build disclosure and
  is asserted to NOT contain the §29 sentence (`entry.test.tsx`). No-guess matching, raw-warning
  placement, optional record-address behaviour unchanged. Environment badge + review line now visible at
  phone width (NEW). No permitted/approved/maximum-allowed wording introduced. Ledger proof in §3.
- **AS-6 (scope + CI).** `git diff --stat` = exactly 7 allowed paths (§6). Zero new dependencies
  (no `package.json`/lockfile touched). No backend/services change. PropertySearch-only edit in
  ArchitectEntry.tsx. Web unit + e2e results are [PREDICTED] (thin client — proven only in CI after the
  orchestrator pushes).

## 3. Ledger proof table (rows whose rendering I touched)

| Row | Before | After | Protected meaning | Test that proves it |
|---|---|---|---|---|
| SH-02 / A01 / A03 / LS-P01 (DB-083 f) | Environment disclosure + review line only in the shell (`.architect-environment` details + `.architect-nav-footnote`), both `display:none` ≤700px. | Search-scoped `search-environment` (`role=note`) badge + `search-review` line, visible at every width; no breakpoint hides them. | Internal-build / no-access-control / do-not-share / "not a legal determination" (A01/LS-P01) and "professional review required" (A03) survive at phone width. | `entry.test.tsx` env-badge test; `responsive-a11y.spec.ts` NEW phone/tablet/desktop test. |
| AD01–AD28 | BBL details unframed; error a bare `<p>`. | BBL details framed as an alternative (not a separate step); the four distinct `lib/bbl.ts` messages styled, still verbatim; `aria-invalid` while errored. | No-auto-pick, distinct per-error recovery, manual fallback keeps typed text, four distinct BBL errors — none dropped or merged. | `entry.test.tsx` four-error test; existing `autocomplete.test.tsx`, `address-resolution.test.tsx` S5/S7/S8. |
| AC01–AC11 | Matched address a large unlabeled line. | Static "City-matched address" label above it; entered / matched / PLUTO stay distinct; equal-ID collapse and warnings-above-Continue unchanged. | Identity comparison distinct; carried identity is the BBL; §5.2 collapse rule; no meaning change. | `address-confirm.test.tsx` S8 (new label tests), S1, S10 AS-2; `confirm-journey.spec.ts` AS-2. |
| M01–M13 / ZC-04 | Map states already distinct/truthful. | Unchanged behaviour; map CSS polish only. | Rendered/unavailable/no-WebGL/multi/invalid/basemap-only-vs-parcel distinct; accuracy+attribution+ZoLa survive without the map. | `lot-outline-map.test.tsx`; `lot-outline.spec.ts`. |
| SH-01 (§29) | Verbatim in global footer via REQUIRED_DISCLAIMER. | Untouched; NEW env note is a DIFFERENT disclosure and never retypes §29. | §29 prominence/verbatim intact; no tooltip/collapsed-only substitute. | `entry.test.tsx` asserts the env note does NOT contain the §29 sentence. |

No AD/AC/M/SH row lost a disclosure, honest gap, provenance note, or professional-review meaning; the
P1 meaning-change register (MR-1..MR-8) stays open and NOT adopted.

## 4. Before → after: every changed user-visible string (all NEW; none removed/reworded)

1. (added) Env badge: **"Internal build"** + note **"No sign-in or access control yet, the official
   data shown is unreviewed, and nothing here is a legal determination — do not share outside the
   engineering team."** — protects the internal-build/no-access-control/do-not-share/not-a-legal-
   determination meaning (A01/LS-P01) at every width.
2. (added) Review line: **"Preliminary analysis — professional review required before any reliance."**
   — protects the professional-review requirement (A03) at every width.
3. (added) BBL framing: **"Already have the 10-digit borough–block–lot? Open it directly — this is an
   alternative to the address search above, not a separate step."** — makes the BBL path an explicit
   alternative in the ONE search/recovery area (AS-1); no meaning change.
4. (added) Confirm label: **"City-matched address"** — names the matched identity so it is visibly
   distinct from the entered and PLUTO identities (AS-2); no meaning change.

The four `lib/bbl.ts` error messages render verbatim (unchanged): empty / non_numeric / wrong_length /
invalid_borough. No existing copy on any surface was edited.

## 5. Exit-gate scenario map (assessment §14 P2 row → test)

| Scenario | Test |
|---|---|
| Keyboard + touch | `autocomplete.test.tsx` keyboard-pick; `address-confirm.test.tsx` S9 (click pick = touch); `a11y-announcements.spec.ts` S6 keyboard journey |
| No auto-pick | `autocomplete.test.tsx` "never auto-accepts the first candidate" + "Enter with no highlighted suggestion"; `address-resolution.test.tsx` S3 (no default, disabled Use) |
| Manual fallback keeps typed text | `address-resolution.test.tsx` S8; `autocomplete.test.tsx` "routes a source failure to the prefilled manual fallback" |
| All error/retry categories | `address-resolution.test.tsx` S4/S5; `autocomplete.test.tsx` "reads each failure reason with its own copy" |
| Delayed PLUTO without CTA shift | `address-confirm.test.tsx` S11 rider a; `responsive-a11y.spec.ts` DB-035 pixel CLS (360/768/1280) |
| Invalid/missing BBL | `entry.test.tsx` NEW four-error test; `confirm-journey.spec.ts` legacy bad-param |
| No WebGL | `lot-outline-map.test.tsx` webgl-unavailable; `lot-outline.spec.ts` single_lot map-or-fallback |
| Multiple / invalid parcel | `lot-outline-map.test.tsx` multiple_features/invalid_geometry; `lot-outline.spec.ts` multiple_features |
| Absent source | `lot-outline-map.test.tsx` route_absent; `lot-outline.spec.ts` upstream failure |
| Identity comparison + env badge (NEW P2) | `address-confirm.test.tsx` new label tests + `confirm-journey.spec.ts` AS-2; `entry.test.tsx` + `responsive-a11y.spec.ts` env-badge |

## 6. Self-checks

- `python tools/modularity_check.py --check` (cwd `wt-m5t115` repo root): **[OBSERVED]** exit 0;
  selected 502 files, failures 0. All 27 warnings are pre-existing files I did not touch (none of my
  7 files appears).
- `git diff --stat` (cwd `wt-m5t115`): **[OBSERVED]** exactly the 7 allowed paths, +253/−4. No
  forbidden path, no `package.json`/lockfile, no `services/`/`packages/`, no shell/global CSS.
- Web unit + e2e suites: **[PREDICTED]** — thin client, never run locally. They prove only in CI on
  the pushed harvest head. New assertions were written against the real fixture harness
  (`e2e/harness/fixture_api.py`): the AS-2 e2e uses the existing `OUTLINE AVENUE` → `1008350041`
  resolver mapping; I deliberately did NOT add an e2e "warnings above Continue" test because the
  synthetic resolver only emits `status="resolved"` (grc `00`), so a `resolved_with_warnings` request
  is not elicitable — that scenario stays proven by the unit test `address-confirm.test.tsx` S1.

## 7. Deviations

- The `confirm-journey.spec.ts` file's existing tests exercise the LEGACY `/property/confirm`
  ConfirmScreen (testid `confirm-card`), which is in `components/property/` (forbidden). I left those
  byte-unchanged and ADDED only architect `address-confirm-card` tests.
- I applied the P1 visual polish conservatively (CSS + two small static DOM additions) rather than a
  full structural re-layout of the confirm card, because the CLS/identity/warning behaviour is locked
  by exact-equality and byte-identical-copy tests and cannot be verified locally (thin client). The
  visible-explanatory wins delivered are the ones the assessment names for this surface.

## 8. OPEN QUESTIONS (overnight — recommended answers, orchestrator/owner to decide)

- **OQ-1 (search-surface horizontal overflow at 360px).** I did not add an `expectNoHorizontalOverflow`
  assertion for the architect search surface because I cannot run it and it could surface a PRE-EXISTING
  overflow unrelated to P2. *Recommend:* the G4 reviewer confirms in CI that `/property?ruleeval=on`
  has no horizontal overflow at 360px; if it does, file a DISCOVERY (it predates P2).
- **OQ-2 (two `role=note` at ≥768px).** At desktop the shell InternalBanner (`role=note`, inside a
  collapsed details) and my always-visible `search-environment` (`role=note`) both exist. Neither is a
  landmark, so this is allowed and honest (mine is the always-visible echo; the shell's is the
  expandable full text). *Recommend:* keep as-is; a future P-slice may fold the shell disclosure into a
  single always-visible element once the shell is in scope.
- **OQ-3 (env-note vs InternalBanner wording).** My concise env note paraphrases the InternalBanner
  meaning rather than importing that component (to avoid a duplicated `data-testid="internal-banner"`
  and a second identical block). *Recommend:* accept the paraphrase; if the reviewer prefers the exact
  InternalBanner text, it can be swapped in a follow-up without meaning loss.

## 9. DISCOVERIES (route to docs/DISCOVERY_BACKLOG.md at the seam — not fixed in-packet)

- **DISC-P2-1.** The shell's own environment badge and nav footnote are still hidden ≤700px
  (`architect.css:138`, `.architect-environment` / `.architect-nav-footnote`) on EVERY architect
  surface. P2 closed the gap only for the SEARCH surface (scope). P3+ should close it for the loaded
  workspace surfaces too, or the shell rule should be revisited when the shell is in scope.
- **DISC-P2-2.** The synthetic e2e resolver (`e2e/harness/fixture_api.py`) has no
  `resolved_with_warnings` / ambiguous / not_found / typed-error street mappings — only `resolved`.
  Full browser coverage of the address error/warning matrix on the architect arc is therefore
  unit-only today; a harness street→outcome table would let the e2e prove those journeys end-to-end.

END-OF-REPORT
