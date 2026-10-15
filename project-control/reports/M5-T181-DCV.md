# M5-T181 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `18b9eac5775ea6d09d93cd637e06944ed0322bbb` (branch `task/wave25-rear-yard-short-block`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R051, R057, R071, R073, R081, R083, R151.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. All three independent reviews returned PASS with no required correction. The one stale packet text (S4's stated order) was already reconciled by the orchestrator scope note (ead79566; G0 re-recorded 0678aff9) and is advisory only.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T02:37:32+00:00, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T181 (directive D-094, 7 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated reproduction of
primary evidence, not a human or professional review. I produced none of this work.

(1) HEAD VERIFIED
 - Frozen head 18b9eac5775ea6d09d93cd637e06944ed0322bbb read via git plumbing in /root/project/w-wave20; HEAD == frozen head; working tree clean.
 - The 5 allowed-path files are byte-identical at material 965de3d5, CI head 48b77e02, measured-preview head f78d302f and the frozen head (git diff = 0 on each).
 - The diff 48b77e02 -> 18b9eac5 touches only control-plane records (M5-T181/M3-T009 gates, reports, tasks, state.json); no code, so CI run 38670334315 at 48b77e02 is valid for the frozen head's code.

(2) ROWS

ROW D-094-R051 — PASS (this task's share)
 - Source quote verified verbatim in source-001.md:148 ("Put the result first, the material qualification next, and the derivation in linked detail..."); row text byte-identical at main 30762409 and the frozen head.
 - ThreeAnswersPanel.tsx leads with a full-width .ta-lead band: identity, then the floor-area allowance beside the legal-ceiling/estimate block (chips, distinction line, lot-area basis, zoning-lot concern); the derivation and the assumed conditions follow in the detail grid below.
 - positions.txt (f78d302f, code-identical to the frozen head) confirms the results band leads and the assumed conditions drop below the fold at 1440/1920 (356 -> 977).
 - STAYS OPEN: the "PDF contains or precisely references the same essential evidence" half of R051 is the report/PDF tasks' share, not this website task's.

ROW D-094-R057 — PASS (this task's share)
 - Source quote verified verbatim in source-001.md:174 ("Check the website at representative desktop and mobile sizes...").
 - The new spec results-first-screen.flag-on.spec.ts measures six widths (1920/1440/1024/768 + 390/320); CI run 38670334315 web-e2e passed both its tests (lines :173 and :237), and six-width before/after pictures exist.
 - The figures/labels shown are the unchanged ApartmentFigures block (forbidden file byte-identical claim-head to material), so no label or caveat drifted.
 - STAYS OPEN: the full website<->PDF figure/label/source-reference parity cross-check is not re-derived by this placement task; it belongs to the parity tasks (M5-T171/M5-T174).

ROW D-094-R071 — PASS
 - Source quote verified verbatim in source-002-amendment.md:23 ("This does not establish that 29 units can actually be built.").
 - Placement-only: ApartmentFigures.tsx, apartment-figures.ts, three-answers.ts and presentation-tokens.json are byte-identical between claim head 658e51fb and material 965de3d5 (git diff = 0), so the "29 Conditional" label and the distinction line are unchanged.
 - Grep of the two changed source files finds no "buildable", "achievable" or "can be built"; the unchanged ApartmentFigures comment states "the 29 is never shown as settled".
 - STAYS OPEN: nothing stays open — the prohibition is not regressed.

ROW D-094-R073 — PASS (this task's share)
 - Source quote verified verbatim in source-002-amendment.md:32 ("Page 1 Results compete with warnings, assumptions, and a software feature inventory." / "The architect still has to assemble the answer.").
 - On the website the results no longer compete with assumptions: before (main 30762409) the assumed-conditions list sat at top 356 (top of the first screen) at 1440/1920; after (f78d302f) it moved to 977 (below the 795 fold) while the ceiling rose from 1382 to 539 (into the first screen).
 - The cited authority, contract principle 1 (ARCHITECT_PRESENTATION_CONTRACT.md:32 "Architect-facing results come first; the material qualification next..."), is honoured.
 - STAYS OPEN: the report page-1 share of R073 is other tasks' (M5-T165); this task's website share is met.

ROW D-094-R081 — PASS (this task's share)
 - Source quote verified verbatim in source-002-amendment.md:47 ("Rebuild the first page: prominent results, their assumptions beside them, one useful site graphic, and the few uncertainties that materially change the answer.").
 - The website first screen now leads with the prominent floor-area allowance beside the ceiling/estimate with assumptions demoted below (positions.txt), matching the "prominent results, their assumptions beside them" clause.
 - STAYS OPEN: only the allowance leads among the three answers; the height/scheduled-building answers, the "one useful site graphic" (a report feature, not in the Results window) and a summarised "few uncertainties" remain for the later website parity task M5-T174 (recorded DB-264).

ROW D-094-R083 — PASS
 - Source quote verified verbatim in source-002-amendment.md:49 ("Require visual proof: before-and-after screenshots of every changed PDF page and corresponding website view, checked against the existing design requirements.").
 - six-before-30762409/ and six-after-f78d302f/ each hold six PNGs plus positions.txt; I confirmed the before/after images differ at every width (distinct sha256), directly answering the owner's identical-image concern from source-021.
 - The visual-quality-reviewer and human-journey-reviewer both checked the before/after at six widths against the presentation contract and returned PASS (M5-T181-reviews.md).
 - STAYS OPEN: nothing stays open for this task's changed website view.

ROW D-094-R151 — PASS (this task's share)
 - Source quote verified verbatim in source-021-amendment.md:26/39 ("The visible screen still gives substantial space to assumptions while results sit farther down."); the row is bound to only D-094-BOOTSTRAP and M5-T181.
 - At 768/1024/1440/1920 the allowance, legal ceiling (29, Conditional) and estimate (17-22, Provisional) with the distinction line lie wholly inside the Results window (measured f78d302f: ceiling 531-550, estimate 565-584, visible to 795; assumptions start at 977+); CI run 38670334315 passed the new spec's desktop S1/S2 test (:173).
 - On phones (390/320) the allowance leads the first screen and the ceiling is one short scroll below (tops 848/963, under 1.25x844); the new spec asserts this at CI line :237.
 - STAYS OPEN: the ceiling/estimate reaching the first screen on phones needs a results-scoped window height, carried to M5-T174 / DB-264; the directive is honestly not called complete by this task alone.

(3) BINDING B1–B5
 - B1 PASS — all 7 rows carry M5-T181 in applicability.task_ids at the frozen head; the six pre-existing rows (R051/R057/R071/R073/R081/R083) have text byte-identical to main 30762409 with M5-T181 newly appended (no text change); R151 is the new source-021 capture and matches its source verbatim.
 - B2 PASS — python3 tools/validate_directive_compliance.py --check exits 0 (quiet on success), so sha256_text_artifact(requirements.json) equals the manifest digest and the registry is internally consistent.
 - B3 PASS — verification.json holds exactly one M5-T181 row listing the 7 ids, every requirement state "pending", verifier "" (awaiting this verdict).
 - B4 PASS — the packet directive_refs cite exactly the 7 ids; the applicable set for M5-T181 is exactly those 7, so applicable == cited.
 - B5 PASS — a scan of every active directive's requirements.json finds M5-T181 applicable to only these 7 rows; nothing else applies uncited.
 - GATES PASS — G0, G2, G3, G4 all record result PASS; G2/G3/G4 share content_manifest_sha256 2c659509... at reviewed_sha 48b77e02 (one content identity); G0 at scope-correction head ead79566 carries the same manifest. (G3 reviewer = visual-quality-reviewer, with the human-journey walkthrough folded into the G3 report; G4 = qa-engineer; G2 = orchestrator self-check.)

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided (blob predicate) the five allowed-path files — ThreeAnswersPanel.tsx, three-answers.css, __tests__/three-answers-panel.test.tsx, e2e/results-first-screen.flag-on.spec.ts, reports/M5-T181-producer-report.md — keep their frozen-head blob ids, AND the 7 rows' text plus their M5-T181 binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' source under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive-bindings, new rows appended to D-094, ledger state — plus this task's own acceptance records and a main-line merge that changes none of the predicate files.

(5) REQUIRED CORRECTIONS
 - None. All three independent reviews returned PASS with no required correction. The one stale packet text (S4's stated order) was already reconciled by the orchestrator scope note (ead79566; G0 re-recorded 0678aff9) and is advisory only.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I ran no browser/Playwright and started no server (read-only; ports 3000/3001/8000 forbidden); the six-width pass/fail rests on CI run 38670334315 (web-e2e SUCCESS, both first-screen tests :173/:237 green, vitest 2704 passed), which I read in the job log but did not execute.
 - I did not run the full api suite or tools/test_directive_compliance.py (forbidden, hours-long); registry integrity rests on validate_directive_compliance.py --check (exit 0) and the green control-plane CI job.
 - The real-person 10-second reader check (contract R062) is not performed; it needs a human.
 - The website<->PDF essential-evidence parity (the cross-output half of R051/R057) is not re-derived against a freshly rendered PDF here; it is other tasks' share.

END-OF-REPORT
````
