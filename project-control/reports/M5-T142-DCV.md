# M5-T142 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `33beb8cc42640cfbbc138e82b4b8f4e91ea1a206` (branch `task/wave14-results-layout`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R258, R267, R268, R269, R570.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The three walkthrough advisories (F1 marker quieter than the number; F2 the withheld gap line inherits bold 600 while "Not known" is 400; F3 no "all-must-hold" lead-in) and the two uncaught-mutation notes (empty <ul> for settled; fixture conditions not asserted item-by-item) are non-blocking and do not affect row compliance.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-09 00:56 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T142 (directive D-090, six rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier). This is NOT a human or professional review. I produced none of this work; I verified read-only from primary evidence and treated every producer report, evidence map and gate report as an unverified claim.

(1) HEAD VERIFIED
 - `git rev-parse HEAD` in /root/project/rv-w6-a = 33beb8cc42640cfbbc138e82b4b8f4e91ea1a206 (the frozen head), detached, unpushed (no origin branch contains it).
 - Between material commit 69b126f6 and the frozen head only files under project-control/ changed (git diff --name-only shows nothing outside project-control/); the material commit touches exactly the 8 allowed-path files.

(2) ROWS
ROW D-090-R229 — PASS
 - Withheld values structurally carry no number: WithheldValueView has only key/label/reason/gapKindLine (three-answers.ts:205-206); the card renders "Not known — <reason>" (AnswerCard.tsx:136-148).
 - Test S5 (three-answers-panel.test.tsx) asserts each withheld envelope row's full textContent is exactly `${label}Not known — ${reason}${gapLine}` — no figure, no zero/default/guess; I ran it green.
 - Open for the rest: R229 also covers drawings and the PDF, which this website task does not touch; the row stays open in the registry for those.
ROW D-090-R258 — PASS
 - The kind-of-gap line is set apart from the reason: WithheldLine renders it as its own sibling span (the joining `{" "}` removed, AnswerCard.tsx:142-146); three-answers.ts GAP_KIND_LINES (76-77) maps missing_information vs work_owed to distinct plain-words lines.
 - Test S5 asserts `gap.previousSibling === reason` and the gap text "Not built yet: this part of the program is still owed." as its own element; I ran it green.
 - Open for the rest: the work-order/section-map/district-checklist evidence the row names is not this task; the row stays open for that.
ROW D-090-R267 — PASS
 - Every conditional value and headline renders the plain-text marker "Conditional" adjacent to the figure (ConditionBlock, AnswerCard.tsx:154-170; CONDITIONAL_MARKER const:24); a settled value renders the figure alone (empty list → null).
 - Tests S2/S3/S4 assert the marker is present and S4 that headline-number and marker both render (count 1 each) so the number never shows alone; G4 mutation (c) "drop marker on conditional headline" turns S4 red. I ran S1-S12 green (140 tests in the 3 touched files).
 - Open for the rest: the engine classification (which results are conditional) is not this task; this task is the display, which honours the state. The row stays open for the engine gap-table tests.
ROW D-090-R268 — PASS
 - Settled shows the figure alone (S1), conditional shows the assumption verbatim as conditional (S2/S3/S12 assert each `<li>` equals the document's assumption, "If " applied per entry), withheld shows "Not known" (S5).
 - Test S6 asserts the three states are told apart on textContent/testids alone in one card; I ran it green. Distinction is by words, never by colour.
 - Open for the rest: deciding which answers stay visible/conditional/withheld is engine work, not this display task; the row stays open for that.
ROW D-090-R269 — PASS (narrow display share)
 - The marker mechanism guarantees ANY conditional value — a height included — renders "Conditional" beside the figure and never reads as the settled maximum (S4 proves a conditional headline carries the marker; CSS weight 400, never colour-only).
 - I did NOT reproduce a height/R6B-specific unit test (the tests exercise floor_area_allowance); the walkthrough's picture claim that the recorded lot's heights render "Conditional" is a claim I did not reproduce in a browser.
 - Open for the rest: the R6B height-rule engine classification is not this task; the row stays open for the height-row tests named in its harness.
ROW D-090-R570 — PASS
 - A withheld value cannot render a number, an older value or a substitute: WithheldValueView has no numeric field and the card prints only reason + gap line (AnswerCard.tsx:126-148).
 - Test S5 asserts the withheld row text holds no figure; G4 check 6 confirms no existing no-number assertion was weakened (journey-215-16-northern.test.tsx unchanged and passing). I ran the folder green (485 tests, exit 0).
 - Open for the rest: R570 also binds the emitted document and exports; those are not this task and stay open.

(3) BINDING B1–B5
 - B1 PASS: requirements.json diff 1cd18f68→frozen head = six "M5-T142" appends to applicability.task_ids plus an updated_at bump; no row text changed (grep of the diff).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = 9ce7a7dc…b7f2d equals manifest.requirements_content_digest_sha256; audit_log carries the "applicability_bound" entry (M5-T142 → the six, digest resynced, provisional verification row, no text edited).
 - B3 PASS: verification.json has one M5-T142 row, applicable_requirement_ids exactly the six, each state "pending", verifier "".
 - B4 PASS: evaluate_task_refs over the real registry → ok=True, applicable==cited==the six, missing/invalid/unresolved all empty.
 - B5 PASS: the derived applicable set across all active directives is exactly the six (no other directive requirement applies uncited). Gates G0/G2/G3/G4 all PASS; G2/G3/G4 share content_manifest 107948b8… and reviewed_sha 7acd27be (one content identity); G3/G4 recorded 00:48:44Z, after CI run 37865020367 went green on 69b126f6 at 00:36:08Z (21/21 jobs incl. web-e2e) — R639/R640 observed (not bound here). validate_directive_compliance.py --check exit 0.

(4) CARRY-FORWARD CONDITION
 - Stamp this PASS at any later head where the 8 allowed-path files keep their frozen-head blob ids: three-answers.ts a8184958, three-answers.test.ts 4d0ea68c, AnswerCard.tsx 5a1de1fd, three-answers.css 232894ed, three-answers-panel.test.tsx 04a30a81, ResultsPanel.tsx 9cdfc256, results-panel.test.tsx 305c00f3, M5-T142-producer-report.md a6eab72e; AND packages/contracts/generated/results.ts (01c3aee0), the journey fixture (894fc473), OutcomeAnnouncer.tsx (9b1ccb46) and everything under packages, docs/reference-cases, .github, tools, services/api/app, services/api/tests, apps/web/e2e, plus render.yaml, playwright.config.ts, package.json, package-lock.json, globals.css, ResultsForm.tsx, ResultsStatusStrip.tsx, ScopeSummary.tsx, ThreeAnswersPanel.tsx unchanged; AND the six rows' text and their binding to this task unchanged.
 - Tolerated later commits: those touching only project-control/** and docs/DISCOVERY_BACKLOG.md, and a merge of the integration branch that changes none of the predicate files.

(5) REQUIRED CORRECTIONS
 - None. The three walkthrough advisories (F1 marker quieter than the number; F2 the withheld gap line inherits bold 600 while "Not known" is 400; F3 no "all-must-hold" lead-in) and the two uncaught-mutation notes (empty <ul> for settled; fixture conditions not asserted item-by-item) are non-blocking and do not affect row compliance.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Real browser / screen-reader rendering, visual weight, contrast and colour, and narrow-window layout (no narrow picture exists); I verified structure via jsdom tests and code only.
 - The Playwright/web-e2e suite and the full api suite (forbidden / CI-only): I read CI run 37865020367 via gh (all 21 jobs success on 69b126f6) but did not execute them.
 - A height/R6B-specific conditional test for R269 and the screens-wave14 pictures: I relied on the general marker mechanism and the walkthrough's description, not on reproduction.
END-OF-REPORT
```
