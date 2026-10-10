# M5-T153 — producer report (the website follows the report's priorities and wording)

Producer: frontend-engineer, an AI agent. Not a human or professional review. I wrote files and made
ONE commit in my own worktree; I did not review, accept, push, or touch the ledger.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ab510aa37441da6b0`
Contract head reset to `876d7a2e5fcaea6fb24b51bf0b30aa76f39b97ef`; `git status --porcelain` empty before work.
No server started; ports 3000/3001/8000 untouched. Playwright/Next not started (the node print test
launches headless Chromium itself, no port).

## What each scenario makes true

- **S1 (scheduled wording).** New `scheduledFloorAreaLine(areaText)` + `SITE_FIT_UNVERIFIED` in
  `lib/architect/presented-results.ts` build the report's exact phrase. Building B's authoritative
  block (`FirstBuildingOptions.tsx` `AlternativeBlock`) now reads ONE line
  `Scheduled floor area: 20,150 sq ft; site fit unverified` (figure from the document via the metric
  adapter). The rendered panel holds none of `achieved / no allowance left unused / optimal /
  compliant / feasible / preferred / recommended` (the two building-option leads were reworded off
  "None is preferred" → "None is ranked ahead of the others").
  - **The building-option CARD (`AnswerCard.tsx`) was deliberately LEFT at its wave-20 compact wording**
    ("Scheduled area" + "Site fit not verified"). Reason: `src/components/architect/__tests__/results-panel.test.tsx`
    (OUTSIDE my allowed paths) asserts that card's wording; changing it would require an out-of-scope
    file to change (ruling X10 STOP). S1's "building B reads … as one line" is satisfied by building B's
    authoritative block. AnswerCard's only net change is a comment. If reviewers want the card to also
    use the exact one-line phrase, that needs `__tests__/results-panel.test.tsx` added to scope — routed
    to the orchestrator; I did NOT touch it.
  - The internal key `achieved_zoning_floor_area` in `three-answers.ts` STAYS a key (it only selects a
    headline value from an available building_option answer). It is never shown on the live
    building-alternatives path. NOTE/finding (out of scope): the legacy `synthetic_all_answers_available`
    fixture carries an engine label text "Achieved zoning floor area" that the old single-answer shape
    renders — that is document/engine wording (`services/**`, `packages/**`), not presentation; flagged
    for M5-T152/engine.
- **S2 (result/state/limitation, no repeated state columns, shared once).** Kept the wave-20 comparison
  (`BuildingOptionsComparison`) — per-building columns, one "Not known" wording for a not-worked
  building, no repeated "not computed" column — and `SharedConditions` (shared limitations stated once,
  named "Condition N"). No change needed beyond the reworded lead.
- **S3 (expandable detail).** `AlternativeBlock` now keeps the answer + its limitation (scheduled line,
  storeys·height, fit note) in the first view and moves the conditions, floor schedule, what-was-not-
  checked and the capacity estimate into a `ResultDetails` disclosure with the accessible name
  "<building> — conditions and floor schedule"; keyboard reaches and opens it; detail stays in the DOM
  (`hidden`) so AT/search reach it. (The three answer cards already used this disclosure pattern.)
- **S4 (report action).** New `lib/report-api.ts` `fetchReport(bbl, body, options)` POSTs the SAME body
  the results form sends to `POST /api/v1/properties/{bbl}/report`, classifying the answer into ONE
  plain state: success(html) / not_available / refused(server message) / error / aborted — no status
  code, route or field name reaches the user. New `components/architect/report/ReportPreview.tsx`:
  - in the Results window (`ResultsPanel.tsx`) it is driven by the current form inputs (`request` prop);
  - in the workspace report tool it is self-contained (`withInputs`, renders the results form) —
    `DashboardTools.tsx` `case "report"` renders it ONLY when `resultsUiEnabled`, else `ReportView`
    unchanged;
  - states: loading; a failed fetch / refusal in plain words; and after any input change the shown
    report is marked OUT OF DATE and the "Print or save as PDF" button is DISABLED until "Update
    report" reloads it;
  - the report shows in an `<iframe>` with `sandbox="allow-same-origin allow-modals"`.
- **S5 (print script).** `scripts/print-report-pdf.mjs` prints a URL or local HTML file with the
  installed Playwright Chromium: `preferCSSPageSize:true, printBackground:true, outline:true,
  tagged:true` (the installed playwright-core 1.61.1 PDFOptions type declares `outline` and `tagged`,
  checked in `node_modules/playwright-core/types/types.d.ts`; no package added). Missing argument /
  missing input file fail with a clear message and exit 1. Node test prints a tiny `@page A4` document
  and reads the PDF's MediaBox to confirm A4.
- **S6 (printed-report browser test).** `e2e/report-print.flag-on.spec.ts` (written, NOT run — the
  orchestrator runs it): opens results, opens the report from the Results window, checks the frame runs
  no script, then renders the report HTML standalone in print media and asserts the six page-type
  titles in order (loose match), no visible text < 7 pt in drawings / < 8 pt elsewhere, no element
  wider than the A4 content box, none of the forbidden words, and `page.pdf({preferCSSPageSize:true})`
  pages all A4 (MediaBox). Steps that need M5-T151's real report output are marked [DEPENDS ON M5-T151].
- **S7 (results specs).** `results.flag-on.spec.ts`: added the exact one-line scheduled assertion for
  building B and a disclosure-open step before the floor-schedule assertions (the schedule is now
  behind a disclosure); the card assertions ("Scheduled area"/"Site fit not verified") were NOT touched
  because the card wording was kept. No assertion weakened or dropped. `results-layout.flag-on.spec.ts`:
  reviewed, NO change — it checks layout/focus/clipped-text, not the block wording; the disclosure only
  shortens the (hidden-content) left column, which does not affect its width-based or first-screen
  checks (a `[role=region][aria-label]` schedule box inside a `hidden` disclosure has zero dimensions,
  so the clipped-text scan skips it).

## Iframe sandbox tokens and why

`sandbox="allow-same-origin allow-modals"` — only what printing from the parent needs.
- `allow-same-origin`: the parent reads `iframe.contentWindow` to print the report; a sandboxed frame
  without it is an opaque origin the parent cannot drive. With NO `allow-scripts` the frame still
  executes nothing.
- `allow-modals`: `window.print()` opens the browser print dialog, which the sandbox treats as a modal;
  without this token the print call is silently blocked.
- Omitted `allow-scripts` (the report is standalone static HTML, ruling X9 d — nothing can execute),
  `allow-forms`, `allow-popups`, `allow-top-navigation`, `allow-downloads` (the report does none of
  these).

## Checks (in apps/web unless noted; DIRECT exit codes)

- `npm run lint` → EXIT 0 (2 pre-existing warnings in untouched files: lot-site-setup.test.tsx,
  study-vocabulary.test.ts; 0 from my files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; Test Files 112 passed (112), Tests 2284
  passed (2284). (One earlier run showed a flaky 5 s timeout in the out-of-scope `window.print` test
  `__tests__/workspace.test.tsx`; it passed in isolation and on the clean re-run — load-sensitive, not
  caused by this change.)
- `node --test scripts/tests/print-report-pdf.test.mjs` → EXIT 0; tests 4, pass 4 (launched the
  installed headless Chromium; parsed the PDF MediaBox = A4).
- root `python3 tools/modularity_check.py --check` → EXIT 0 (all warnings pre-existing services/api &
  tools files; none of my files flagged).

## Mutation proofs (scratch copy OUTSIDE the repo; node_modules + packages symlinked; deleted after;
the repo worktree never mutated — verified byte-for-byte afterwards)

1. "achieved" put back into the scheduled line (`scheduledFloorAreaLine(view.totalFloorArea)` →
   ``Achieved floor area: ${view.totalFloorArea}; site fit unverified``). CAUGHT by TWO tests:
   `first-building-options.test.tsx › "S1/S6: building B reads the report's one-line scheduled phrase …"`
   (expected 'Achieved floor area: …' to be 'Scheduled floor area: …') AND
   `three-answers-panel.test.tsx › "S1 … > recorded_215_16_northern_journey: … holds none of the
   forbidden words …"` (not to contain 'achieved').
2. The out-of-date report left printable after an input change (`canPrint = hasReport && !outOfDate` →
   `canPrint = hasReport`). CAUGHT by `report-preview.test.tsx › "marks the report out of date after
   the inputs change and DISABLES printing until reloaded"` (`expect(report-print).toBeDisabled()`).

## Files changed (18)

`e2e/report-print.flag-on.spec.ts`, `e2e/results.flag-on.spec.ts`, `scripts/print-report-pdf.mjs`,
`scripts/tests/print-report-pdf.test.mjs`, `src/components/architect/ResultsPanel.tsx`,
`src/components/architect/answers/AnswerCard.tsx` (comment only),
`src/components/architect/answers/BuildingOptionsComparison.tsx`,
`src/components/architect/answers/FirstBuildingOptions.tsx`,
`src/components/architect/answers/__tests__/building-options-comparison.test.tsx`,
`src/components/architect/answers/__tests__/first-building-options.test.tsx`,
`src/components/architect/answers/__tests__/three-answers-panel.test.tsx`,
`src/components/architect/report/ReportPreview.tsx`,
`src/components/architect/report/__tests__/report-preview.test.tsx`,
`src/components/architect/report/report-preview.css`,
`src/components/architect/workspace/DashboardTools.tsx`, `src/lib/__tests__/report-api.test.ts`,
`src/lib/architect/presented-results.ts`, `src/lib/report-api.ts` — plus this report.

## STOP / routing

No STOP: no file OUTSIDE allowed_paths needed to change, because I kept the building-option CARD's
wave-20 wording. The ONE item an orchestrator may optionally expand: to make the compact card ALSO read
the exact one-line phrase, add `apps/web/src/components/architect/__tests__/results-panel.test.tsx` to
scope and change its two building_option assertions (lines ~90–91). I did not touch it.

REQUESTED STATUS: awaiting_gate (G2 self-check / G3 / G4; the two e2e specs and the full PDF render are
the orchestrator's to run per ruling X10).
END-OF-REPORT
