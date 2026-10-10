# M5-T153 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63` (branch `task/wave21-report-redesign`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R894, R895, R903, R917, R918, R922, R924, R927, R928, R929.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The reviewers' advisory items were all applied before the frozen head and re-attested: CI-1 (print-script test moved out of scripts/tests so the browser-free security job stays clean), W1 (BuildingOptionsComparison one phrasing), W2 (distinguishing Details accessible names), W3 (stale comments), and M5-T151's C1/C2 (outside this task). No open blocker references M5-T153.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 11:24 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T153 (directive D-090, 10 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is NOT a human or professional review. I produced none of this work or its records; every report, map and gate record was treated as an unverified claim and re-derived from primary evidence (source files, git objects, the registry, deterministic tests, CI, and the real printed artifacts). Frozen checkout /root/project/w-wave20 was never modified.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63 on branch task/wave21-report-redesign; `git status` clean. This is the frozen head in the brief.
 - Chain confirmed: capture 9c564ad8 (source-081, rows R900-R933) -> contract 87e13f6e -> claim-seam 876d7a2e -> builds/reworks -> corrected head f28d065f (reviews' delta attestations) -> submit head 88afbb47 (review records/evidence maps/progress 90) -> frozen head 1dd5fb51 (records the gate JSONs). Base main-line d459358a.
 - `git diff --name-only f28d065f..1dd5fb51` and `88afbb47..1dd5fb51` both touch ONLY project-control/; the material tree (apps/web, services, tools, .github …) at the frozen head is byte-identical to the CI'd/reviewed identity.

(2) ROWS (numeric order; PASS = this task's share satisfied from primary evidence at the frozen head)

ROW D-090-R894 — PASS
 - Obligation (concise option comparison; "the same applies to the website's comparison"). The website comparison is this task's share; the eleven-option concise-column table in the PDF is M5-T151's share.
 - apps/web/src/components/architect/answers/BuildingOptionsComparison.tsx shows the method's worked buildings side by side with ONE fixed set of metric rows (METRIC_ROWS lines 29-43) and a single not-known wording for a not-worked building (COMPARISON_NOT_KNOWN — reason, lines 123-125); no repeated state column. The one wording comes from the shared adapter scheduledFloorAreaLine (presented-results.ts:44-46).
 - Test building-options-comparison.test.tsx:96-97 asserts "Scheduled floor area:" + "site fit unverified"; I reran the suite at the frozen head (vitest: 9 files / 167 tests passed).
 - Stays open in the registry for the report's eleven-option table under BOOTSTRAP / M5-T149 / M5-T151.

ROW D-090-R895 — PASS
 - Prohibition (never "achieved"; scheduled wording with the site-fit caveat before any caveat; PDF and website). Registry text matches its source-080 reading anchor (line 59, classification "prohibition"). Website is this task's share.
 - AnswerCard.tsx:222-224, FirstBuildingOptions.tsx:110-112 and BuildingOptionsComparison.tsx:137-139 all render scheduledFloorAreaLine(...) = "Scheduled floor area: N sq ft; site fit unverified"; the figure is read from the document (presented-results.ts:6, ruling X7).
 - three-answers-panel.test.tsx:525-549 scans the whole rendered panel against a 7-word FORBIDDEN list (incl. "achieved", "no allowance left unused") and asserts none present plus "site fit unverified" present; passed. The producer mutation (achieved→back) is caught here.
 - The PDF side (I confirmed print-final3/report.txt shows the phrase 4x and 0 forbidden words) stays open under BOOTSTRAP / M5-T148 / M5-T149 / M5-T151.

ROW D-090-R903 — PASS
 - Obligation (make the correction in the report generator AND the website components). New row (source-081 line 91, "obligation"). The website components are this task's share; the server generator is M5-T151's.
 - apps/web/src/lib/report-api.ts fetchReport (lines 112-122) POSTs to /api/v1/properties/{bbl}/report with the SAME body the results form sends plus the optional ?address=; ReportPreview.tsx shows the returned report for printing; DashboardTools.tsx:111-113 wires it into the workspace report tool only when results are on, else ReportView unchanged.
 - The orchestrator's real render print-final3/report-request.txt shows the website POSTed to …/4073340070/report?address=215-16%20NORTHERN%20BOULEVARD%2C%20Queens, status 200, body {"housing_program":"standard_residence"}.
 - The server report generator share stays open under BOOTSTRAP / M5-T151.

ROW D-090-R917 — PASS
 - Obligation (rework pages 4-5; each option's available result, current state and material limitation; drop the repeated "not computed/…/outputs owed" columns). New row (source-081 line 105, "obligation"). The pages 4-5 PDF rework is M5-T151's; the website comparison following the same rules is this task's share.
 - BuildingOptionsComparison.tsx shows each worked building's result (scheduled line + storeys/height/plan/estimate) and a not-worked building's state/limitation as ONE not-known line; the five metric rows are identical across buildings — no repeated state column. Tested (building-options-comparison.test.tsx, in the 167 passed).
 - print-final3/report.txt confirms the report's 11-option table uses a 5-column layout with the limitation shown by number (M5-T151's share); the row stays open under BOOTSTRAP / M5-T149 / M5-T151.

ROW D-090-R918 — PASS
 - Obligation (explain shared limitations once). New row (source-081 line 106, "obligation"). Website share here; report share is M5-T151's.
 - SharedConditions.tsx (lines 20-50) lists only conditions shared by two or more results, each named "Condition N" and stated once; options refer to them by name via AppliesConditions (FirstBuildingOptions.tsx:283-296) and ConditionRefs (AnswerCard.tsx:279-286), never repeating the full "If …" text.
 - three-answers-panel.test.tsx:288 asserts a referring option's text does not contain "If " (the full condition text is not repeated per option); passed.
 - The report's "shared limitations once" (print-final3 page 3) stays open under BOOTSTRAP / M5-T151.

ROW D-090-R922 — PASS
 - Prohibition (scheduled wording while placement/geometry incomplete; "achieved"/"no allowance left unused" not used; PDF and website). New row (source-081 line 110, "prohibition"). Website share here.
 - The shared one-line phrase renders at every website site (AnswerCard.tsx:222-224, FirstBuildingOptions.tsx:110-112, BuildingOptionsComparison.tsx:137-139); scope-correction 1 tied R922 to the compact card — results-panel.test.tsx:92-93 asserts the card reads "Scheduled floor area:" + "site fit unverified" and three-answers-panel.test.tsx:334 asserts the old "Site fit not verified" pair is gone; passed.
 - I also confirmed the rendered PDF (print-final3/report.txt): the phrase appears 4x and each of the 7 forbidden words appears 0 times. The PDF/drawing wording stays open under BOOTSTRAP / M5-T151 / M5-T152.

ROW D-090-R924 — PASS
 - Prohibition (no HTTP checks / implementation notes / internal identifiers / owner-question references / backlog language in the main report). New row (source-081 line 112, "prohibition"). The website's report surface + results surface are this task's share.
 - report-api.ts maps every HTTP outcome to one plain state (lines 59-64, 151-181) with no status code/route/field name reaching the screen; ReportPreview.tsx:44-49 uses plain developer-free lines ("Preparing the report…", "The report could not be loaded. Trying again is safe.", out-of-date line).
 - three-answers-panel.test.tsx scans the rendered results against RAW_CODES (17 snake_case tokens incl. not_available, square_feet, buildings_not_worked; lines 40-60) and BANNED_WORDS ("still owed","Not built yet","Not worked","internal preview", line 61) and asserts none present; passed.
 - I corroborated the main report itself: print-final3/report.html shows no HTTP status codes and "Verified" only in the page-6 label key marked "Not used in this report." The main-report cleanliness stays open under BOOTSTRAP / M5-T151 / M5-T152.

ROW D-090-R927 — PASS
 - Prohibition (change reusable templates and presentation logic, not hand-polish a separate sample). New row (source-081 line 115, "prohibition"). Website share here; report templates are M5-T151's.
 - The website wording is produced by ONE shared adapter (scheduledFloorAreaLine, presented-results.ts:44-46) consumed by all four render sites, and by reusable components (ReportPreview, ResultDetails, BuildingOptionsComparison, SharedConditions, AnswerCard, FirstBuildingOptions). No standalone static sample file exists.
 - `git diff --name-only base..88afbb47 -- apps/web` is 24 files, all reusable source/tests within M5-T153's allowed_paths; no forbidden path (ReportView.tsx, package.json, package-lock.json, e2e/harness/**, .github/**, services/**, packages/**) was touched by this task (apps/web/e2e/harness/fixture_api.py was changed by M5-T151 commits 7bf9df32/8b82814f, not by M5-T153).
 - The report-template side stays open under BOOTSTRAP / M5-T151 / M5-T152.

ROW D-090-R928 — PASS
 - Obligation (same information priorities and result wording on the website, with expandable supporting detail). New row (source-081 line 116, "obligation"). This is this task's PRIMARY row — only M5-T153 and D-090-BOOTSTRAP are applicable; nothing is deferred to another task.
 - Same priorities/wording: the shared scheduled phrase and forbidden-word/developer-text discipline above, plus the report-matching identity heading ("215-16 NORTHERN BOULEVARD, Queens" leads the Results window — ThreeAnswersPanel; desktop-results.png).
 - Expandable detail: ResultDetails.tsx is a real <button> with aria-expanded/aria-controls and a distinguishing accessible name `${open?"Hide details":"Details"} — ${name}` (lines 39-53), opening a role=group region (aria-label "Details — <name>") that holds conditions/schedule/not-checked/estimate and stays in the DOM when hidden; focus moves in on open and returns to the button on Escape. result-details and three-answers-panel tests passed in my rerun.
 - Fully satisfied by this task; nothing of this row stays open for other tasks.

ROW D-090-R929 — PASS
 - Obligation (generate the full current-scope PDF; render and inspect every page at its intended print size). New row (source-081 line 117, "obligation"). The print script + browser test + report action are this task's share; server generation is M5-T151's.
 - apps/web/scripts/print-report-pdf.mjs prints with the installed Playwright Chromium (no new package), preferCSSPageSize/printBackground/outline/tagged (lines 52-58), honouring the report's @page A4; a missing arg or missing input fails with a clear message + exit 1 (resolveInput lines 26-36; printToPdf lines 44-46).
 - The orchestrator's full render print-final3/report.pdf = 6 pages, each 594.96x841.92 pt = A4 (pdfinfo). The browser test apps/web/e2e/report-print.flag-on.spec.ts (A4 MediaBox, legibility, drawings, forbidden words) ran green in CI web-e2e (run 38047040636) at the material identity of the frozen head.
 - "Inspect every page at print size" includes a human visual pass (reviewers did it; I corroborated from the page images). The server-generation share and the human-with-a-person inspection stay open under BOOTSTRAP / M5-T151.

(3) BINDING B1-B5
 - B1 PASS. `git diff base..1dd5fb51 -- requirements.json` appends exactly 10 "M5-T153" lines, one into each bound row's applicability.task_ids (grep count = 10). Across base(899)->head(933) NO existing row's text changed (0) and NO classification changed (0); the 34 new rows are exactly R900-R933; no row removed. R903/R917/R918/R922/R924/R927/R928/R929 equal their source-081 reading anchors (lines 91/105/106/110/112/115/116/117, classifications match); R894/R895 equal their source-080 reading anchors (lines 58/59). R894/R895 also received M5-T151 in this wave — expected (both tasks apply). No post-capture body edit beyond the applicability append and recorded digest resyncs.
 - B2 PASS. directive_registry.sha256_text_artifact(requirements.json) = 030652450f861cc0b4785cb8b44f6867c6e734cbbf453b58c9211727dbacdaa8 = manifest.requirements_content_digest_sha256 (byte-match). `python tools/validate_directive_compliance.py --check` at the frozen head: exit 0 (direct exit code; run once).
 - B3 PASS. verification.json has exactly ONE M5-T153 row; applicable_requirement_ids = the 10 bound ids; producer="frontend-engineer"; verifier="" (empty); all 10 requirements state="pending", evidence=[], reviewed_sha=null. (This row is the provisional slot my verdict fills.)
 - B4 PASS. reg.evaluate_task_refs(M5-T153 packet) -> ok=True; applicable_ids == cited_ids == the 10 ids; missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS. Scanning all 89 active directives, exactly 10 rows are applicable to M5-T153 — all in D-090, all cited; no uncited applicable row anywhere. Gate records: G0 PASS (orchestrator, administrative, reviewed dd1e9c44), G2 PASS (orchestrator, self-check), G3 PASS (code-reviewer), G4 PASS (visual-quality-reviewer). G2/G3/G4 all at content_manifest 43bdbfb6 and reviewed_sha 88afbb47 — ONE content identity — recorded 2026-10-10 11:11 UTC, after CI run 38047040636 at the corrected head f28d065f completed (status completed, conclusion success, 21/21 jobs success incl. web-e2e, api, web-dependency-security, control-plane, modularity, contracts). Note (not a defect): the G4 JSON names visual-quality-reviewer; the packet's second G4 reviewer, human-journey-reviewer, also returned an independent PASS in the same review record (M5-T153-G3G4.md return 3 and delta return 6), so both independent G4 reviews are on file.

(4) CARRY-FORWARD CONDITION
 - My PASS may be stamped at a later head WITHOUT re-review provided: the blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules, and the task's reports (project-control/reports/M5-T153-*) are unchanged from frozen head 1dd5fb51; AND the 10 rows' text and the binding (B1-B5) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other wave-21 tasks (M5-T151, M5-T152), and a main-line merge that changes none of the predicate's files. I verified f28d065f..1dd5fb51 and 88afbb47..1dd5fb51 touch ONLY project-control/, so the material at the frozen head equals the reviewed/CI'd identity.

(5) REQUIRED CORRECTIONS
 - None. The reviewers' advisory items were all applied before the frozen head and re-attested: CI-1 (print-script test moved out of scripts/tests so the browser-free security job stays clean), W1 (BuildingOptionsComparison one phrasing), W2 (distinguishing Details accessible names), W3 (stale comments), and M5-T151's C1/C2 (outside this task). No open blocker references M5-T153.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not execute Playwright (read-only; started no server; ports 3000/3001/8000 untouched). I verified browser behaviour from CI web-e2e success (run 38047040636 at f28d065f, material byte-identical to the frozen head), the orchestrator's captured print-final3/ artifacts (report.pdf 6xA4 by pdfinfo; report-request.txt status 200 with the address), and the spec source — I did not re-run report-print.flag-on.spec.ts / results specs myself.
 - The real-person ~10-second readability test and a real screen-reader pass are human-only and were not run by anyone (recorded NOT RUN by the reviewers); I am an AI agent and cannot substitute for them.
 - I did not run the full services/api pytest suite or tools/test_directive_compliance.py (forbidden / hours-long); I relied on the CI "api" job success and validate_directive_compliance.py --check exit 0.
 - Per-page legibility/overlap/visual-answers judgement I corroborated from the page images but did not perform as a human.
 - I reproduced the web unit layer directly: vitest at the frozen head over src/components/architect/report, src/lib/__tests__/report-api.test.ts and src/components/architect/answers = 9 files / 167 tests passed.

END-OF-REPORT
```
