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

## Rework 1 (reset to integrated head 1fbc856cb7b64ed15717e0e0b9023b17c1ed3cb5; scope now includes
`__tests__/results-panel.test.tsx`; scenarios S8, S9)

- **G1 (S8) — one wording for a scheduled building across the WHOLE screen.** The compact
  building-option card (`AnswerCard.tsx` `BuildingOptionCard`, scheduled branch) now renders the same
  adapter line as the building-options block: `scheduledFloorAreaLine(view.scheduledArea)` →
  "Scheduled floor area: 20,150 sq ft; site fit unverified". Removed the wave-20 pair
  (`SCHEDULED_AREA_LABEL` "Scheduled area" + `SITE_FIT_NOT_VERIFIED` "Site fit not verified", both now
  deleted from AnswerCard; the `answer-site-fit` element is gone). It renders nowhere for a scheduled
  building. Assertions changed:
  - `__tests__/results-panel.test.tsx` (W-2 loop, building_option branch): `toContain("Scheduled area")`
    + `toContain("Site fit not verified")` → `toContain("Scheduled floor area:")` +
    `toContain("site fit unverified")` + `not.toContain("Site fit not verified")`.
  - `answers/__tests__/three-answers-panel.test.tsx` S13: `answer-scheduled-area` now
    `.toBe(scheduledFloorAreaLine(quantityText(displayQuantity(...))))`; the `answer-site-fit`
    assertion → `queryByTestId("answer-site-fit")` is null + `not.toContain("Site fit not verified")`;
    the no-worked case `not.toContain("Scheduled area")` → `not.toContain("Scheduled floor area")`.
  - `answers/__tests__/journey-215-16-northern.test.tsx`: same two changes (one-line phrase;
    `answer-site-fit` null).
- **G2 (S9) — the street address reaches the report.** `report-api.ts`: new `sanitizeReportAddress`
  (trim → strip to `[A-Za-z0-9 \-.,'#/&]` → cap 120 → trim; empty → null) and `fetchReport` adds
  `?address=<encodeURIComponent(sanitized)>` when present, else no parameter (`FetchReportOptions.address`).
  `ReportPreview` takes an `address?` prop and passes it; `ResultsPanel` takes `address?` and passes it
  to `ReportPreview`; `DashboardTools` passes the property's street label `address?.label` to both the
  Results panel and the report tool. Tests: report-api S9 block (with address → encoded query; without
  → no param; over-long 200-char → decoded length 120; `sanitizeReportAddress` unit) and a ReportPreview
  test (address prop → request `?address=`).

### Rework 1 checks (apps/web, direct exit codes)

- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, untouched files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; 112 files, 2289 tests passed.
- `node --test scripts/tests/print-report-pdf.test.mjs` → EXIT 0; 4/4 (unchanged script).
- root `python3 tools/modularity_check.py --check` → EXIT 0 (no file of mine flagged).

## Rework 2 (reset to integrated head 475404f114333da71fc564b29faebcc781b9dc8b; the orchestrator ran
the browser suite — evidence `e2e-1-report-results.log`, `print-int2/`; scenarios S8, S9 + the report
drawings/title)

- **C1 — the results browser test follows the one-line wording.** `results.flag-on.spec.ts` lines
  116–117 still expected the old card pair; the compact card now reads the one-line phrase. Changed to
  `toContainText("Scheduled floor area: 20,150 sq ft; site fit unverified")` and asserted the old pair
  is absent (`not.toContainText("Scheduled area:")`, `not.toContainText("Site fit not verified")`).
- **C2 — the recorded address when no address was typed.** The real request (`report-request.txt`)
  carried no address because the workspace opened by lot number has no typed label. New
  `reportAddress(typedLabel, recordedAddress)` in `report-api.ts` (typed label wins, else the recorded
  address, each through `sanitizeReportAddress`, else null). `DashboardTools` builds the recorded
  address from the profile it already holds (`profile.identity.address.normalized_address` + borough)
  and passes `reportAddress(address?.label, recordedAddress)` to both the Results panel and the report
  tool. Unit tests (report-api.test.ts): typed label; recorded address only; neither.
- **C3 — the printed-report test requires the drawings and the address title.**
  `report-print.flag-on.spec.ts` now also asserts: the report `h1` title contains the routed profile
  fixture's recorded address (`normalized_address`); the report holds its drawings — total SVGs ≥ 3
  and a drawing on the decision-summary page, the site-and-context page and the scenario sheet (found
  by heading within each `.report-page`). A report printed without its drawings or address title now
  fails. Marked [DEPENDS ON M5-T151 / M5-T152].
- **Not fixed (out of scope, flagged).** The report-print run's other failure — "no visible text below
  its minimum print size" with ten `7.5pt` strings — is a REAL defect in the report's own CSS
  (`report.html` declares `font-size: 7.5pt` for conditions / not-checked / open-item text, below the
  8 pt minimum of page-types.md). My font check is correct and deliberately catches it; the fix is in
  the report generator (`services/api/app/drawings/report/`, M5-T151), not this task. I did NOT weaken
  the check.

### Rework 2 checks (apps/web, direct exit codes)

- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, untouched files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; 112 files, 2290 tests passed.
- `node --test scripts/tests/print-report-pdf.test.mjs` → EXIT 0; 4/4.
- root `python3 tools/modularity_check.py --check` → EXIT 0.

## Rework 3 (reset to integrated head 8b82814f3cb1462941c427dffb373546f4f1f239; evidence
`print-int3/desktop-results.png`; scenario E1 — the screen's identity matches the report's title)

- **E1 — the Results window shows the same property identity as the report.** The report now titles
  the property with its address ("215-16 NORTHERN BOULEVARD, Queens") while the screen's identity
  heading read "Queens block 7334, lot 70". `ThreeAnswersPanel` takes a new optional `address` prop
  (the SAME address the report receives — the typed label, else the recorded address, resolved
  upstream by `reportAddress` and passed `DashboardTools → ResultsPanel → ThreeAnswersPanel`). Its
  `IdentityLine` now leads with the address as the heading (testid `three-answers-identity-address`)
  and keeps the borough/block/lot beneath it (testid `three-answers-identity-lot`, new quiet class
  `.ta-identity-sublot` in three-answers.css, colour from a token). With no address it keeps today's
  lot heading. Files: ThreeAnswersPanel.tsx, three-answers.css, ResultsPanel.tsx (passes `address`).
- **Tests.** three-answers-panel.test.tsx: with an address → the address is the heading and the lot
  line sits beneath; with no address → no address element and today's lot heading. The existing
  identity assertions (rendered without an address) still read `three-answers-identity-lot` =
  `scope.lot.display`, unchanged.
- **Browser-spec assertions expecting the old heading:** none. The only identity assertion in my
  browser specs is `results-layout.flag-on.spec.ts:206` (`three-answers-identity` is in the viewport),
  which is text-agnostic and needs no change.

### Rework 3 checks (apps/web, direct exit codes)

- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, untouched files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; 112 files, 2292 tests passed.

## Rework 4 (reset to 334b07d17ebe8cd45ebe84a32fc32b1f377341fe; full browser suite 167 passed / 1 failed)

- **report-print.flag-on.spec.ts "page-type titles are in order"** failed (log `e2e-4-full.log:224`)
  because the report's decision summary now carries a coverage block naming "H. Option comparisons",
  so the loose `/option comparison/i` first-matched on page 1. Fix: match each page type by its OWN
  `type-name` label line, anchored and multiline — `/^decision summary$/im`, `/^site and context$/im`,
  `/^option comparison$/im`, `/^scenario sheet\b/im`, `/^assumptions and open items$/im`,
  `/^calculations and evidence$/im` (label text confirmed in `print-int4/report.html`). Every other
  assertion unchanged. Checks: `npm run lint` → EXIT 0; `npm run typecheck` → EXIT 0.

## Corrections after review (reset to 7f972796604ee8cc2207983413cd94f56acab0d5; all reviewers PASS;
`return-review-w21-walk.txt` corrections 1–3 + CI run 38044133021)

- **CI-1 (required).** CI's web-dependency-security job runs `node --test scripts/tests/*.test.mjs`
  WITHOUT browsers, so the Chromium-launching `scripts/tests/print-report-pdf.test.mjs` failed there.
  Deleted that file (scripts/tests is now browser-free: `node --test scripts/tests/*.test.mjs` → EXIT
  0, 50 tests) and moved the check into `report-print.flag-on.spec.ts` as a second test that drives
  `scripts/print-report-pdf.mjs` through a child process (the real CLI) — keeping every former node
  assertion: a valid run writes A4 pages (every MediaBox A4), a missing output argument and no
  arguments each fail with a clear message, and a non-existent input fails. The orchestrator runs it.
- **W1.** `BuildingOptionsComparison.tsx` per-building worked summary now reads the one-line phrase
  `scheduledFloorAreaLine(column.scheduledArea)` ("Scheduled floor area: N sq ft; site fit unverified")
  instead of a separate "Site fit not verified" note beside a duplicate "Scheduled area" row — one
  wording per situation. The aligned table keeps its "Scheduled area" metric row. Test asserts the
  worked summaries read the phrase and never "Site fit not verified".
- **W2.** `ResultDetails.tsx` opener now carries `aria-label="Details — <name>"` (visible label stays
  "Details"/"Hide details"), so several disclosures on one screen no longer all read "Details" to a
  screen reader. Test renders two and asserts the accessible names differ.
- **W3.** Updated the stale doc comments in `FirstBuildingOptions.tsx` (module header) and
  `AnswerCard.tsx` (BuildingOptionCard header) to the one-line phrase; comment-only, nothing rendered.

### Corrections checks (apps/web, direct exit codes)

- `npm run lint` → EXIT 0 (same 2 pre-existing warnings, untouched files).
- `npm run typecheck` → EXIT 0.
- `npx vitest run src/components/architect src/lib` → EXIT 0; 112 files, 2293 tests passed.
- `node --test scripts/tests/*.test.mjs` → EXIT 0; 50 tests, 0 fail, NO browser used.

END-OF-REPORT
