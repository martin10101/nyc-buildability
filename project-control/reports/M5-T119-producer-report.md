# M5-T119 — producer report (D-086 P3a, overview slice)

Producer: frontend-engineer (orchestrator-dispatched subagent). Worktree
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t119`, branch
`task/M5-T119-d086-p3a-overview`, claim seam `d895f3c8`. Thin client — every web
test result is **[PREDICTED]** (proves only in CI on the pushed head); the
self-checks I could run locally are **[OBSERVED]**.

## 0. What this slice actually changes (honest summary)

Four real visible changes on the loaded `/property` overview, plus meaning-
preserving re-cites of already-built behaviour (AS-3 FAR rows, Unknown, fail-safe
labels were built in M5-T037/T040/T058/T080 and are re-proved, not rebuilt):

1. **One "Active issues" strip** (new `OverviewExceptionStrip.tsx`) folds today's
   separate conflict / critical-missing / stale alerts into ONE `role=status`
   region, each row naming its critical field(s), the effect it blocks, and its
   preserved link. No strip when nothing is active.
2. **A two-column canvas** — site map/context (~55%, left) + limit matrix (~45%,
   right), stacking to one column ≤950px, no horizontal overflow at 360px.
3. **The readable per-cap coverage status beside the cap number** (A06), keeping
   "FAR only · Buildable envelope not assessed" and city-record vs draft FAR as
   distinct rows.
4. **The shell environment + professional-review disclosure at phone width on
   loaded surfaces** (closes DISC-P2-1 / DB-087 g — M5-T115 fixed only search).

Out of scope (P3b): the contextual inspector and the collapsed existing-building
group — untouched.

## 1. Files changed (all inside allowed_paths; no forbidden path)

- `apps/web/src/components/architect/OverviewExceptionStrip.tsx` — NEW component (the A04 strip).
- `apps/web/src/components/architect/PropertyOverview.tsx` — overview uses the strip; canvas reordered map-left.
- `apps/web/src/components/architect/DevelopmentLimits.tsx` — `DraftHeadline` cap status beside the value (A06).
- `apps/web/src/components/architect/ArchitectShell.tsx` — phone-only shell environment+review strip (loaded surfaces).
- `apps/web/src/app/property/architect.css` — overview-grid / exception-strip / cap-line / shell-environment selectors only.
- `apps/web/src/components/architect/__tests__/overview-exception-strip.test.tsx` — strip unit tests (replaced placeholder).
- `apps/web/src/components/architect/__tests__/development-limits.test.tsx` — A06/A09 unit tests + brief-unchanged.
- `apps/web/src/components/architect/__tests__/workspace.test.tsx` — shell env strip present/absent (jsdom DOM + gating).
- `apps/web/e2e/development-limits.spec.ts` — cap status beside the value.
- `apps/web/e2e/architect-workspace.spec.ts` — two-column canvas + strip fold.
- `apps/web/e2e/responsive-a11y.spec.ts` — loaded-overview no-overflow + phone-width shell env.
- `project-control/reports/M5-T119-producer-report.md` — this report.

## 2. Self-checks

- `python tools/modularity_check.py --check` → **[OBSERVED] EXIT 0**; `selected 504
  files; failures 0; warnings 27` — none of the 27 warnings touch my files.
- `git -C <worktree> diff --stat` → **[OBSERVED]** exactly the 11 code/test/css
  files above (+ this report). No `services/`, `packages/`, lockfile, `lib/`,
  `layout.tsx`, `globals.css`, `components/property|address`, `ReportView.tsx`,
  `ArchitectEntry.tsx`, `MaxEnvelopePanel.tsx`, `e2e/harness|helpers.ts`, `docs/`,
  `.github/`, `.claude/`.
- Web unit + Playwright: **[PREDICTED]** — routed to CI on the pushed head; not run
  locally (thin client; never npm/npx/node here).

## 3. Acceptance-scenario evidence

- **AS-1 (one strip) [PREDICTED PASS].** `OverviewExceptionStrip.tsx` renders ONE
  `role=status` `aria-label="Active issues"` region folding conflict + critical-
  missing + stale, each with fields + blocked effect + the exact preserved links
  ("Review conflicting source values →", "Review missing inputs →"); renders null
  when none active. Identity mismatch (A15) and incomplete assessment (A05) are NOT
  folded (see §6 D2). Tests: `overview-exception-strip.test.tsx` (none/conflict/
  missing/stale/fold/partial/identity-boundary/incomplete-boundary/integration);
  e2e `architect-workspace.spec.ts` "active issues fold into ONE exception strip".
- **AS-2 (canvas) [PREDICTED PASS].** `.architect-overview-grid` = `minmax(320px,
  1.25fr) minmax(0,1fr)` (map left ~55%, matrix ~45%), single column ≤950px. e2e:
  `architect-workspace.spec.ts` two-column boundingbox proof; `responsive-a11y.spec.ts`
  no-overflow at 360/768/1280 on the loaded overview.
- **AS-3 (FAR honesty) [PREDICTED PASS].** City-record FAR and evaluated (draft)
  FAR remain distinct rows (already built — `DevelopmentLimits.tsx:114-127`;
  re-proved). The cap row keeps "FAR only · Buildable envelope not assessed" AND
  the readable STATUS_LABELS gloss now sits BESIDE the number (`.architect-cap-line`);
  "Unknown" stays the word (`residentialReference`/lot-area — existing tests). No
  number computed in the UI. Tests: `development-limits.test.tsx` M5-T119 block;
  e2e `development-limits.spec.ts` "readable per-cap coverage status beside the cap".
- **AS-4 (phone disclosure) [PREDICTED PASS].** `ArchitectShell` renders a phone-
  only `.architect-shell-environment` (role=note) on loaded surfaces (active !==
  "search"): "Internal build" + the restriction paraphrase + "professional review
  required" line; `display:none` ≥701px (no desktop duplication). Meaning text
  asserted, never colour alone. Tests: `workspace.test.tsx` (present on loaded /
  absent on search / topbar intact); e2e `responsive-a11y.spec.ts` visible at 360
  on the loaded overview + hidden at 1280.
- **AS-5 (preservation) [PREDICTED PASS].** See the ledger proof table §4. The
  printed brief (`ReportView`) is untouched: `PropertyIssuesSummary` stays byte-
  identical (still imported/rendered by ReportView + the scenarios/facts/zoning
  views); `DraftHeadline` keeps every text node (cap value, "FAR only" note, exact
  enum gloss, source-wording disclosure) — the status only moves beside the value,
  proved by `development-limits.test.tsx` "the printed brief keeps the cap value,
  FAR-only note and readable status text". §29 stays verbatim in the global footer
  (`REQUIRED_DISCLAIMER`, `layout.tsx` — untouched). No permitted / approved /
  maximum-allowed wording introduced (grep-clean).
- **AS-6 (scope + CI) [OBSERVED scope / PREDICTED CI].** Exactly the allowed paths;
  zero new dependencies (no package.json/lockfile touched); no backend change.
  Modularity 0 failures. CI green predicted on the pushed harvest head.

## 4. Ledger proof table (touched A / LS-P rows — before → after → proving test)

| Row | Before | After | Protected meaning | Proving test | Print path |
|---|---|---|---|---|---|
| **A04** | Two separate `.architect-alert role=status` blocks (conflict, critical-missing) + a stale `<p>` on the overview (`PropertyIssuesSummary`). | ONE `role=status` `.architect-exception-strip` folding all three, each with fields + blocked effect + the same links (`OverviewExceptionStrip.tsx`). | Conflicts, critical missing (fields named) and staleness stay immediately visible; the two links + wording survive; one strip = one status region. | `overview-exception-strip.test.tsx` (all cases) | Unchanged — `PropertyIssuesSummary` still prints A04 in the brief (ReportView untouched). |
| **A06** | Readable cap status rendered AFTER the "FAR only" note. | Status BESIDE the cap value in `.architect-cap-line`; every text node preserved (`DraftHeadline`). | Cap is FAR-only, not a buildable envelope; exact coverage enum + cap_label + reasons survive. | `development-limits.test.tsx` M5-T119 "beside the cap value" + "professional_review_required" + "no scenario" + existing `:418` | Unchanged in meaning — same words print in the brief (brief-unchanged test). |
| **A09** | City-record FAR vs evaluated FAR as distinct rows (already built). | Unchanged; re-proved. | No reference-to-result promotion; both values kept. | `development-limits.test.tsx` M5-T119 "distinct rows" + existing "development-first entry points" | Unchanged. |
| **A05** | Incomplete-assessment = `IncompleteEvaluationNotice` (role=status), rendered by ArchitectEntry from the raw doc. | Unchanged; NOT folded into the strip. | "Rule details incomplete; numerical summaries unavailable; record preserved" survives at role=status. | `overview-exception-strip.test.tsx` incomplete boundary | Unchanged. |
| **A15** | Identity mismatch = `AnalysisIdentityNotice` (role=alert). | Unchanged; NOT folded (folding would downgrade role=alert). | "Results are withheld from this property" + two labelled IDs stay a role=alert. | `overview-exception-strip.test.tsx` identity boundary | Unchanged. |
| **A13** | Map/results split (matrix left, map right). | Split preserved; columns reordered map-left/matrix-right per §5.3. | Map/results split + collapsed existing-building survive; map-absence note kept. | e2e `architect-workspace.spec.ts` canvas + existing DB-005 map-card tests | Screen-only (A13); facts reach paper via PropertyFacts — unchanged. |
| **A01 / LS-P01** | Environment disclosure (`.architect-environment`, topbar) `display:none` ≤700px — hidden on loaded phone surfaces. | Phone-only `.architect-shell-environment` (role=note) restores internal-build / no-access-control / do-not-share / "not a legal determination" on loaded surfaces ≤700px. | The environment/reliance restriction survives on mobile (B-001 open). | `workspace.test.tsx` shell-env; e2e `responsive-a11y.spec.ts` 360 | Not a print obligation (topbar hidden in print; unchanged). |
| **A03** | "Preliminary analysis — professional review required" nav footnote `display:none` ≤700px. | Phone-only `.architect-shell-review` line restores it on loaded surfaces. | Non-final reliance framing survives on mobile. | same as A01 | Unchanged (footer §29 + calc-evidence carry it on paper). |
| **LS-P09 / LS-P12** | Missing-inputs / unsupported detail sections in the issues & facts views. | Unchanged in those views; the overview strip surfaces critical-missing + stale as a SUMMARY that links to the issues view. | Totals/critical never collapsed; "this retrieval" stale scope; detail sections intact. | strip tests + the preserved `propertyHref(bbl,"issues")` links | Unchanged. |

## 5. Exit-gate scenario map (UI_DEEP_DIVE §14 P3 row → test)

| Scenario | Where it shows / stays absent | Test |
|---|---|---|
| Compare city / reference / evaluated / existing FAR | Distinct FAR rows + existing-building disclosure | `development-limits.test.tsx` M5-T119 "distinct rows" + existing "development-first entry points" / "keeps every existing building fact behind one reversible disclosure" |
| Unsupported district | No district lookup; reference stays "Unknown"/value | existing `development-limits.test.tsx` "uses no district-specific lookup for %s" |
| Critical gaps | Strip "Critical inputs missing" row (fields + blocked effect + link); absent when none | `overview-exception-strip.test.tsx` missing + none |
| Mismatched identity | `AnalysisIdentityNotice` role=alert "Results are withheld"; NOT in the strip | `overview-exception-strip.test.tsx` identity boundary |
| Missing citation | Evaluated FAR withheld ("Not calculated") | existing `development-limits.test.tsx` "withholds an unreliable evaluated FAR: missing citation" |
| Stale source | Strip "Stale source" row (exact stale sentence + review clause); absent when fresh | `overview-exception-strip.test.tsx` stale + none |
| Split zones | ZoningContextPanel / district handling (out of scope, unchanged) | existing district tests (cited, not rebuilt) |
| Incomplete assessment | `IncompleteEvaluationNotice` role=status "Rule details incomplete"; NOT in the strip | `overview-exception-strip.test.tsx` incomplete boundary |

## 6. Changed user-visible strings (before → after → protected meaning)

1. Conflict row: "Unresolved data conflicts" + fields + "Review conflicting source
   values →" **kept verbatim**; ADDED "— official sources disagree on these; a
   reliable value is withheld until the conflict is reviewed." → names the blocked
   effect; nothing dropped. (Brief keeps the original via PropertyIssuesSummary.)
2. Critical-missing row: "Critical inputs missing" + fields + "Review missing
   inputs →" **kept**; ADDED "— a draft limit that depends on these cannot be
   relied on until they are supplied."
3. Stale row: "The property source is stale. Captured dates and retrieval status
   are available in Evidence." **kept verbatim**; ADDED "Review the retrieval dates
   before relying on these figures." + a "Stale source" category heading.
4. NEW strip label "Active issues" (region heading) — names the summary.
5. Cap status ("Conditional" / "Professional review required" / …): **no wording
   change** — the exact STATUS_LABELS gloss moves beside the cap number.
6. Phone shell strip (loaded surfaces): "Internal build" + "No sign-in or access
   control yet, the official data shown is unreviewed, and nothing here is a legal
   determination — do not share outside the engineering team." + "Preliminary
   analysis — professional review required before any reliance." — all **reused
   verbatim** from the accepted M5-T115 search strip (no new wording; the review
   line is byte-identical to `search-review`).

## 7. What an owner will SEE differently (plain words)

1. On the main analysis screen, one tidy "Active issues" box at the top lists only
   the real problems — data conflicts, missing critical inputs, stale data — each
   saying which field and what it holds back, with the same review links. It
   replaces the two or three separate warning boxes; if there are no problems, no
   box appears.
2. The screen now leads with a larger site map on the left and the limits on the
   right (a proper two-column layout), and it no longer runs off the side on a phone.
3. The floor-area cap shows its status word (like "Conditional") right next to the
   number, still labelled "FAR only — buildable envelope not assessed", with the
   city-record and draft FAR kept on separate lines.
4. On a phone, the loaded property screen now shows the internal-build warning and
   the "professional review required" line too — before, a phone user saw neither
   of those on a loaded screen.

Nothing new claims a permit, approval, or "maximum allowed building"; the §29
disclaimer and the printed brief are unchanged.

## 8. Deviations

- **D1 (canvas order).** Prior layout put the limit matrix left; I reordered to
  map-left (~55%) / matrix-right (~45%) to match the accepted P1 spec §5.3 and
  frame O-D. AS-2 does not mandate order; I followed the spec. See OQ-2.
- **D2 (strip scope — key decision).** The strip folds only the three profile-
  derived issues (conflict / critical-missing / stale). Identity mismatch (A15,
  role=alert) and incomplete assessment (A05, role=status) are NOT folded because
  (a) the task KEY RULE keeps identity withhold at role=alert — folding it into a
  role=status strip downgrades it — and (b) `LoadedWorkspace` (in the forbidden
  `ArchitectEntry`) nulls a mismatched or non-inspectable evaluation/scenario before
  `PropertyOverview` ever receives them, so the strip structurally cannot see them.
  Both are surfaced by their dedicated regions rendered directly ABOVE the strip and
  are proved preserved by boundary tests. The §5.3 "five categories" are therefore
  covered across the exception area = strip (3) + dedicated A15/A05 (2), with one
  live region per event (A04 / LS-P16). See OQ-1.
- **D3 (shell strip form).** The phone strip reuses the accepted M5-T115 paraphrase
  (role=note text) rather than a second `InternalBanner`, so no duplicate
  `internal-banner` region appears on a shell-wrapped route (e.g. survey review);
  the topbar `InternalBanner` stays the desktop carrier.

## 9. OPEN QUESTIONS (owner asleep — recommended answers)

- **OQ-1 (single home for all 5 categories).** Should a follow-up thread the RAW
  (pre-filter) returned evaluation/scenario into the strip so identity-mismatch and
  incomplete-assessment appear IN the strip too (one DOM element for all five
  §5.3 categories)? That needs an `ArchitectEntry` edit (out of P3a scope) plus a
  reviewed assistive-technology test to retire the dedicated A15 role=alert / A05
  role=status regions without a double live region. **Recommendation:** defer to
  P3b; keep the dedicated regions now (role=alert preserved).
- **OQ-2 (column order).** Map-left (~55%) per §5.3/O-D vs the prior analysis-first
  matrix-left. **Recommendation:** keep map-left (spec-faithful, "more visually
  explanatory"); flip via one CSS line + DOM-order swap if the owner prefers
  analysis-first.
- **OQ-3 (stale row link).** The stale row has no explicit link (matches today's
  PropertyIssuesSummary, which routes detail to Evidence via the "available in
  Evidence" prose — A04 progressive_destination). **Recommendation:** keep as-is; a
  later slice could add an explicit "Retrieval status in Evidence →" link.

## 10. DISCOVERIES (route to backlog; not fixed in-packet)

- **DISC-1.** A condo multi-lot profile carries an unresolved `condo_base_lot_
  resolution` conflict, so the strip (exactly as today's PropertyIssuesSummary)
  shows a generic "Unresolved data conflicts: condo_base_lot_resolution …" row IN
  ADDITION to the dedicated CondoRecordsChannelSection. Pre-existing behaviour;
  worth deciding whether the condo-resolution conflict should be excluded from the
  generic strip (it has its own records surface).
- **DISC-2 (resolved).** DISC-P2-1 / DB-087 g (loaded-surface phone-width
  environment + review gap, flagged by the M5-T115 HJ review) is CLOSED by this
  slice's `.architect-shell-environment` strip.
- **DISC-3.** `fieldLabel` returns "<field> (source column — label pending review)"
  for a field not in `FIELD_LABELS`; an unmapped critical-missing / conflict field
  shows that verbose fallback in the strip. Pre-existing `fieldLabel` behaviour;
  a friendlier fallback or a label-coverage check could be a small future task.

## 11. Requested status

**awaiting_gate.** Producer work complete inside scope; one commit to be made by
the orchestrator from this worktree; web results [PREDICTED] pending CI on the
pushed head. Gates G0/G2/G3/G4 with reviewers code-reviewer, qa-engineer,
human-journey-reviewer, directive-compliance-verifier.

END-OF-REPORT
