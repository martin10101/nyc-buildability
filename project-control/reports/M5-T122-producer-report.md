# M5-T122 — producer report (D-086 P3b: condo records surface + M5-T119 strip riders)

Producer: frontend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t122`, branch
`task/M5-T122-d086-p3b-condo-records`. Contract/claim seam `55276f2d`.

Evidence-status legend: [OBSERVED] ran here; [BLOCKED] could not run; [PREDICTED] web
test proven only in CI on the pushed head (thin client — no local npm/npx/node).

---

## 1. What shipped (three objectives)

1. **Condo records visual/state pass (AS-1, spec §5.4 C01–C11).** Added the §5.4
   presentation the mockup under-rendered, preserving every existing state: a
   "Reference only" tag on the multi-lot group (C02), a "City record" claim tag on
   the single/allow substitution (C01), a "Human record" claim tag on the confirmed
   site-definition (C04), a plain "Zoning missing for N lots" summary count (C08),
   and a "Parcels differ" label plus a recorded-vs-current comparison `<details>`
   (C06). No records read as allowances; every prior meaning and role is intact.
2. **Modularity move (AS-2).** The condo surface (`CondoRecordsChannelSection`,
   `CondoSiteDefinitionRecord`, `deriveCondoSurface`, `deriveCondoDisplay`,
   `condoWithholdsAllowances`, the parse helpers/constants/types) moved out of
   `PropertyOverview.tsx` into the new `CondoRecordsSection.tsx`. `PropertyOverview.tsx`
   is now a compatibility **facade** re-exporting every public name. No importer edited
   (`ReportView.tsx`, `ArchitectEntry.tsx`, the tests all resolve unchanged).
3. **M5-T119 strip riders (AS-3) on `OverviewExceptionStrip.tsx`.** A2 real `<h2>` +
   `aria-labelledby` (name announced once, heading-navigable); A4 stale row now links
   to the Evidence retrieval status; A5 the `condo_base_lot_resolution` conflict keeps
   its heading, field and link but gets a TRUE clause instead of "official sources
   disagree"; A7 the identity-withhold alert made visually distinct from the strip
   (CSS only, role/text unchanged); G3 advisory the overview-grid comment corrected.

## 2. Move map (AS-2)

Moved `PropertyOverview.tsx → CondoRecordsSection.tsx` (verbatim logic, provenance
comments preserved): constants `CONDO_RESOLUTION_FIELD`, `CONDO_RESOLUTION_NOTE_PREFIX`,
`CONDO_RESOLUTION_NOTE_RE`, `CONDO_ALLOWANCE_OK_OUTCOME`; type `CondoResolutionNote` +
`condoResolutionNotes`; type `CondoDisplayState` + `deriveCondoDisplay` +
`condoWithholdsAllowances`; type `CondoSurfaceDecision` + `deriveCondoSurface`; the
internal `CondoSiteDefinitionRecord`; `CondoRecordsChannelSection`.

Facade re-exports from `PropertyOverview.tsx` (public API byte-identical): values
`CondoRecordsChannelSection`, `deriveCondoSurface`, `deriveCondoDisplay`,
`condoWithholdsAllowances`; types `CondoDisplayState`, `CondoSurfaceDecision`. Unchanged
in place: `PropertyOverview`, `PropertyIssuesSummary`, and the `DraftHeadline` re-export
from `./DevelopmentLimits`. Consumers verified unchanged: `ReportView.tsx`
(`CondoRecordsChannelSection` + `deriveCondoSurface`), `condo-resolution-display.test.tsx`
(`CondoRecordsChannelSection`, `PropertyOverview`, `deriveCondoSurface`),
`report-view.test.tsx` (imports nothing from PropertyOverview — renders `ReportView`).
The new `condo-records-section.test.tsx` asserts the facade exports are the SAME
references (`facade.X === CondoRecordsSection.X`).

## 3. Ledger proof (D-086-R003) — every touched C/A row: before → after, protected meaning, proving test, print path

| Row | Before → After | Protected meaning | Proving test | Print path |
|---|---|---|---|---|
| A04 (strip) | `<p>` title + `aria-label` (doubled name); one lumped conflict row; stale no link → `<h2>`+`aria-labelledby` (name once); condo conflict own true-clause row; stale Evidence link | One `role=status` region naming active issues; each clause true; links/wording preserved | overview-exception-strip.test.tsx (A2/A4/A5) + e2e | Not printed (overview screen); PropertyIssuesSummary prints the brief unchanged |
| A15 (identity withhold) | `.architect-alert` amber, same as strip → `.architect-alert[data-identity-state]` rose (spec §3 conflict) | Severe wrong-property withhold stays `role=alert`, text unchanged, now visually distinct | condo-resolution-display.test.tsx identity suite (role/text unchanged) | AnalysisIdentityNotice prints in brief; color-only, role/text/layout unchanged, report-view.test.tsx green |
| C01 (single substitution) | h2 only → h2 + sibling "City record" tag | Paired identity joined by "City record" claim class; records not allowances | condo-records-section.test.tsx (tag + locked h2 name) | Prints in brief (report-view.test.tsx substitution) |
| C02 (multi-lot group) | h2 only → h2 + sibling "Reference only" tag | City records are references, not allowances; channel-disagreement clause unchanged | condo-records-section.test.tsx (tag + locked h2 name); report-view.test.tsx (h2 name) | Prints in brief |
| C03 (identity rows) | unchanged (moved verbatim) | Entered/billing/base distinct; equal-ID collapse; unknowns as words | condo-resolution-display.test.tsx DB-036(b)/(f)-1 | Prints |
| C04 (human confirmation) | added "Human record" claim tag | A recorded human act, not a system choice or calculation | condo-records-section.test.tsx (present + absent) | Prints |
| C05 (self-attested refusal) | unchanged | Unverified identity never unlocks calculation; refusal not buried | condo-resolution-display.test.tsx refusal suite | Prints |
| C06 (parcel discrepancy) | plain `<p>` → "Parcels differ" label + comparison `<details>` | Discrepancy surfaced for review; never silently revokes the record | condo-records-section.test.tsx + condo-resolution-display.test.tsx discrepancy | Prints (details opened on beforeprint) |
| C07 (not confirmed vs no active) | unchanged | "never recorded" ≠ "no longer active"; honest unconfirmed footing | condo-resolution-display.test.tsx unconfirmed suite | Prints |
| C08 (unknown zoning) | per-lot unknown only → + "Zoning missing for N lots" count | Unknown zoning ≠ no zoning; partial gap never erases recorded districts; ZTLDB gap named | condo-records-section.test.tsx (mixed/all/absent) | Prints |
| C09 (provenance footer) | unchanged | Exact source/dataset/version/retrieved with explicit unknowns | condo-resolution-display.test.tsx (g); report-view.test.tsx (exact retrieved/version) | Prints (exact values) |
| C10 (channel disagreement) | unchanged | `role=status`, not alert; no second region; limits govern | condo-resolution-display.test.tsx conflict test | Prints |
| C11 (honest absence) | unchanged | No fabricated records; outage never withholds on its own | condo-resolution-display.test.tsx absence/outage tests | Nothing (by design) |
| LS-P16 (one announcer) | unchanged | Exactly one `role=status` strip; identity stays `role=alert`; no new live region added | strip "one status region" test | Not printed |

## 4. Exit-gate scenario map (spec §14 P3 / packet AS)

| Scenario | Covered by | Status |
|---|---|---|
| Mixed-known condo zoning (some recorded, some unknown) | condo-records-section.test.tsx (Zoning missing for 1 lot) + condo-resolution-display.test.tsx (e) mixed | [PREDICTED] new + existing |
| Self-attested confirmation | condo-resolution-display.test.tsx "self-attested refusal" (existing, cited — not rebuilt) | [PREDICTED] |
| Revoked/superseded ("No active confirmation" vs "Not confirmed") | condo-resolution-display.test.tsx unconfirmed history (existing, cited) | [PREDICTED] |
| Discrepant parcels ("Parcels differ") | condo-records-section.test.tsx (label + disclosure) + condo-resolution-display.test.tsx discrepancy | [PREDICTED] new + existing |
| Unavailable / route_absent (no records, no withhold) | condo-resolution-display.test.tsx outage/absence + deriveCondoSurface tests (existing, cited) | [PREDICTED] |
| Strip riders (heading once, stale link, condo clause) | overview-exception-strip.test.tsx (A2/A4/A5) + architect-workspace/responsive-a11y e2e | [PREDICTED] new |

## 5. Before → after, every changed/added user-visible string

1. Strip title: visual `<p>` "Active issues" (+ `aria-label`) → `<h2>` "Active issues" (same text; region named via `aria-labelledby`, announced once). Protects: the strip's single-status-region meaning; adds heading navigability.
2. Condo conflict clause (strip): "{fields} — official sources disagree on these; a reliable value is withheld until the conflict is reviewed." → (condo row only) "{fields} — the condo's base lot is not resolved to a single lot; see "City records for this condo" below for the recorded base lots." Protects: accurate framing of a records case; generic conflicts keep the old clause verbatim.
3. Stale strip row: added link "Retrieval status in Evidence →" (sentence unchanged). Protects: the actionable path the other rows already offer.
4. Multi-lot records group: added "Reference only" tag. Protects: records are references, not allowances.
5. Single substitution: added "City record" tag. Protects: the C01 claim-class join.
6. Site-definition confirmed: added "Human record" tag. Protects: a recorded human act, not a calculation.
7. Multi-lot records: added "Zoning missing for N lots." Protects: the C08 gap is legible; "not recorded (unknown)" per lot unchanged.
8. Discrepancy: added "Parcels differ." + a "Compare recorded and current base lots" disclosure listing recorded/current BBLs. Protects: C06 surfaced-for-review, never a silent revocation.

No wording adopted from the meaning-change register; no permitted/approved/maximum-allowed wording (grep-clean); §29 disclaimer untouched (not in scope); no number computed in the UI; visual states never remap backend statuses.

## 6. What an owner will SEE differently (plain words)

- The "Active issues" box at the top of the overview is now a real heading you can jump to, and a screen reader says its name once, not twice.
- A stale-source warning now has a clickable "Retrieval status in Evidence" link, like the conflict and missing warnings.
- For a condo split across several lots, the top warning now says plainly that the condo's base lot isn't settled and points to the "City records for this condo" section, instead of the misleading "official sources disagree".
- The most serious "wrong property" warning now looks visibly different (a red-tinted box) from the amber issues box.
- The condo records section carries small "Reference only" / "City record" / "Human record" labels, a plain "Zoning missing for N lots" count, and a "Parcels differ" note with a click-to-compare list — all making clearer that these are city records, not calculated allowances.

## 7. Self-checks

- [OBSERVED] cwd repo root `python tools/modularity_check.py --check` → exit 0. 507 files selected, 0 failures, 27 warnings — all on pre-existing files in services/api and tools; none in this task's scope (PropertyOverview shrank 401→~120 lines; CondoRecordsSection ~318 lines).
- [OBSERVED] `git -C C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t122 diff --stat` → exactly the 8 allowed source/css/test/e2e paths; `git status --porcelain | grep -v '^ M'` → no untracked files. `condo-resolution-display.test.tsx` and every forbidden path (ReportView.tsx, ArchitectEntry.tsx, report-view.test.tsx, lib/**, layout.tsx, globals.css, harness/, helpers.ts, docs/, .github/, .claude/) untouched.
- [OBSERVED] banned-wording grep (`permitted|approved|maximum allowed`) over the changed components + css → no matches (exit 1).
- [PREDICTED] web unit (vitest) + e2e (Playwright) green in CI on the pushed head — thin client, cannot run npm/npx/node locally. New/updated tests: condo-records-section.test.tsx (facade identity + C01/C02/C04/C06/C08 present+absent), overview-exception-strip.test.tsx (A2 heading, A4 stale link, A5 condo clause, absent-heading), architect-workspace.spec.ts (+heading assertion, +riders test), responsive-a11y.spec.ts (+360px riders test). Existing suites relied on unchanged: condo-resolution-display.test.tsx and report-view.test.tsx (both pass via the facade; the locked h2 names "City records for this condo" / "Recorded base lot for this condo" are unchanged — the new tags are h2 siblings).

## 8. Deviations

- D1 (A5 heading): "keeps its heading" read literally — the condo conflict row keeps the "Unresolved data conflicts" heading text, its field label and its review link; only the clause changed to a true one. Cosmetic edge: a profile carrying BOTH a real source conflict AND a condo conflict shows two rows headed "Unresolved data conflicts" with different clauses (each true). See OQ-1.
- D2 (locked h2 vs spec heading): report-view.test.tsx (forbidden) pins the exact h2 name "City records for this condo"; spec C02/copy #6 wants "City records — Reference only". Kept the h2 name exact and added "Reference only" as a visible sibling tag — both the locked test and the spec's reference-only visual intent are satisfied.
- D3 (test placement): condo-resolution-display.test.tsx left UNCHANGED — the move is transparent through the facade, so its ~40 assertions pass unedited (that is the AS-2 evidence). New-element coverage lives in the new condo-records-section.test.tsx.
- D4 (identity-alert print): the A7 distinct treatment is color-only and reaches the brief (AnalysisIdentityNotice prints there); role/text/layout unchanged, report-view.test.tsx green; browsers typically drop print background color. More prominent, never weaker.

## 9. OPEN QUESTIONS (owner asleep — recommended answers)

- OQ-1: A5 condo-row heading wording. I kept "Unresolved data conflicts" per the literal "keeps its heading". If a reviewer prefers an accurate heading ("Condo base lot not resolved"), it is a one-line change with the true clause already in place. **Recommendation:** keep the literal heading to honor the rider verbatim.
- OQ-2: "City records — Reference only" as the h2 vs a sibling tag. I used a sibling tag because report-view.test.tsx locks the h2 name. **Recommendation:** keep the sibling tag; changing the h2 requires editing a forbidden locked test.
- OQ-3: the C06 comparison `<details>` opens for print (ReportView opens non-raw details on beforeprint), so recorded/current parcels print in the brief. **Recommendation:** acceptable per C06 (prints in brief); a future slice could mark it raw-tier if print bloat matters.

## 10. DISCOVERIES (D-069 — routed, not fixed in-packet)

- C07 "revoked/superseded history in a native disclosure" (ledger C07 P0-proposed) is NOT fully implementable today: `SiteDefinitionView` exposes only `confirmationCount`, not the individual revoked/superseded records, so a meaningful history list cannot be rendered without a contract/parse addition in `lib/condo-records.ts` (READ-ONLY here). The two distinct texts (never-recorded vs revoked-or-superseded) already satisfy the protected meaning and are tested. Route to backlog.
- DB-091 (a)–(e) riders all landed (heading, stale link, condo clause, identity-alert distinctness) and the M5-T119 G3 grid-comment advisory is fixed.

END-OF-REPORT
