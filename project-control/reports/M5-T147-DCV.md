# M5-T147 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c10ac73f095b503d99df5420e43ed51f0e59822f` (branch `task/wave19-first-option-wiring`, review copy `/root/project/rv-w6-b`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R256, R509, R526, R540, R541, R543, R544, R556, R570, R641, R688, R700.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE result. The two standing NOTEs (the typed "(on the HPD measurement basis)" label; the jsdom-structure-only narrow-table assertion) are non-blocking and already disclosed in the evidence map's known_limits.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-09 23:25 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T147 (directive D-090, 12 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is NOT a human or professional review. I produced none of the work or records; I reproduced every conclusion below from primary evidence (the code, the tests and what they assert, the committed document, the registry files and git objects) at the frozen head. I did not run tools/project_control.py write subcommands, git/gh writes, or CI; I started/stopped nothing on ports 3000/3001/8000.

(1) HEAD VERIFIED
 - Frozen head c10ac73f095b503d99df5420e43ed51f0e59822f is checked out and CLEAN in /root/project/w-wave19 on branch task/wave19-first-option-wiring (git rev-parse HEAD == the frozen sha; git status empty; git diff --name-only HEAD empty) — I read all frozen-head content from that clean worktree.
 - My own copy /root/project/rv-w6-b sits at 7cf94e09 (the walkthrough-FAIL round) and has no apps/web/node_modules, so I read the frozen head via the w-wave19 worktree and git plumbing rather than moving my copy.
 - The CI-green reviewed head f237d0d7 is a git ancestor of the frozen head; the only commits between them (…→566372cd→4a7e2089→c10ac73f) touch project-control/ files alone — no apps/web, packages/contracts, services/api, .github, tools or render.yaml path changed — so the material content under review is byte-identical at the frozen head.

(2) ROWS

ROW D-090-R256 — PASS
 - This task's share: every design value is SHOWN, with no hidden default. The floor-to-floor height is read from the document and shown on every storey of the floor schedule (FirstBuildingOptions.tsx FloorScheduleTable → row.floorToFloor, sourced from floor_schedule[].floor_to_floor_ft), and the share range and apartment size are shown under "Preliminary assumptions used (not editable here):" (first-building-options.ts CapacityView.shareLow/shareHigh/apartmentSize, read from the document, never typed).
 - The committed benchmark carries floor_to_floor_ft 10.0 on all three storeys and share 0.60–0.75 / size 700 — the panel formats, it does not invent (verified in recorded_215_16_northern_journey.json).
 - What this task CANNOT satisfy and stays open in the registry: changing these starting values ON this screen is explicitly not built here (ruling W7, recorded as work owed DB-213(a)); the "editable" clause of R256 remains open for a later screen task (row still applies to M5-T135/T145/T146 and the editor work).

ROW D-090-R509 — PASS
 - This task's share (display only): the screen shows the estimate worked from the proposed building's OWN residential zoning floor area, not from the maximum permitted. The capacity block prints "…from {floorArea} of residential floor area" where floorArea = capacity_estimate.floor_area_sqft (20,150 sq ft), and the maximum-permitted floor area stays a separate answer card, never the estimate's starting area.
 - I re-derived the shown quotients from the document's own fields: 20,150 × 0.60 / 700 = 17.271… → 17.27 and 20,150 × 0.75 / 700 = 21.589… → 21.59; both read from quotient_low/quotient_high (first-building-options.ts twoDp), not computed on screen.
 - Stays open: the formula/measurement-basis RECORD and the arithmetic itself are the share of M5-T133/M5-T145/M5-T146; R509 remains applicable to those tasks for the non-display obligations.

ROW D-090-R526 — PASS
 - Each worked building shows a "Not checked for this option:" list read item-for-item from the document, and the benchmark list includes "Parking, loading and bicycle requirements" (not_checked in recorded_215_16_northern_journey.json; test S6 asserts the rendered items deep-equal alternative.not_checked).
 - Nothing is called feasible: the only "feasible/complies/legally correct" strings in non-test web source are a NEGATIVE statement ("It is not shown as feasible.") and code comments; tests S1/S6/journey/e2e all assert the section does NOT match /feasible|complies|legally correct|\bvalidated\b/.
 - Stays open: the later report SECTION carrying the parking/loading/bicycle COUNTS (R526's "can come later") is not part of this task and remains owed.

ROW D-090-R540 — PASS
 - This task's share: the residential-share range 0.60–0.75 is shown with its values (CapacityBlock → "Residential share: {shareLow} to {shareHigh}") under the heading "Preliminary assumptions used (not editable here):", and is never presented as realistic, expected or validated (no such wording anywhere in the section; the state is told in words).
 - The values are read from capacity_estimate.share_low/share_high (0.6/0.75), not typed; the contract check refuses a wrong-shape estimate.
 - Stays open: on-screen editability and the fuller "unvalidated sensitivity range" characterisation are governed by ruling W7 (shown as a preliminary assumption here) and stay open in the registry for M5-T135/T145/T146 and a later editor.

ROW D-090-R541 — PASS
 - The starting apartment size 700 sq ft is shown as a chosen starting value — "Apartment size: {apartmentSize} (on the HPD measurement basis)" — read from capacity_estimate.apartment_size_sqft (700.0), not described as a measured or typical average.
 - It is grouped under "Preliminary assumptions used (not editable here):", keeping it a preliminary assumption; the words "(on the HPD measurement basis)" are a static label typed in the panel (FirstBuildingOptions.tsx:202), flagged by G3 as provenance-consistent with the contract field description and not blocking.
 - Stays open: changing the size on this screen is work owed (ruling W7); the typed HPD-basis phrase is a standing low-risk NOTE (carry it as a document field later).

ROW D-090-R543 — PASS
 - The estimate's label is rendered byte-exact from the document: capacityView narrows on estimate.label === "Preliminary capacity estimate" and the panel prints view.label; the committed benchmark carries exactly that label. The "Not known" path renders estimate.label + reason for a not-yet-worked option.
 - The web contract check fails CLOSED on a non-owner label (results-contract-checks-1-4-0.test.ts "refuses a worked alternative whose estimate label is not an owner label", flips it to "Apartments" and expects rejection) — the check is non-vacuous (it also accepts two real 1.4.0 fixtures).
 - Stays open: nothing for this task's display share; the row also binds the document producers (M5-T135/T136/T145/T146) for emitting the labels.

ROW D-090-R544 — PASS
 - The estimate starts from the floor area the proposed building actually accommodates (20,150 sq ft shown), and the legal ceiling on the number of apartments is a SEPARATE figure: it is the withheld legal_unit_limit_standard value_state on the floor_area_allowance card, not restated in the building-options section (journey test S4; first-building-options.test.tsx S4 asserts queryByTestId("legal-unit-limit") is null in the section).
 - The maximum permitted floor area is likewise a separate answer, never the estimate's starting area.
 - Stays open: nothing for this task; R544 continues to bind the document/modules producers.

ROW D-090-R556 — PASS
 - The withheld-fallback bug is fixed in three-answers.ts (lines 360–385): when the designated headline key is withheld, the headline renders that entry's reason (kind "withheld"), explicitly "never values[0]"; the fall-through to values[0] fires only when the headline key is ENTIRELY ABSENT (e.g. a 1.0.0 document), which is not a withheld case — so no withheld result can surface an older or substitute value.
 - The web contract check refuses a withheld coverage that carries a footprint number (results-contract-checks-1-4-0.test.ts R556/R570 case sets footprint_sqft=8060 and expects "…coverage_by_portion.footprint_sqft…never carry a number"); the withheld coverage block and the withheld legal-limit row render no numeric field (CoverageView.withheld / journey S4 asserts the legal-limit reason does not match /\d/).
 - Stays open: nothing for this task's screen share; R556 also binds the server emitter (M5-T136/T140) in the registry.

ROW D-090-R570 — PASS
 - A withheld value stays withheld on the screen: test S5 proves the withheld coverage shows no footprint testid AND that building B's footprint (6,716.67 sq ft) never appears in the withheld coverage block's place; the benchmark coverage, the legal-unit limit and (at 16 ft) building B all render reason-only with no number.
 - The not-worked building blocks carry no footprint figure: journey S10 asserts building A's not-worked block textContent does not contain " sq ft", and the document's buildings_not_worked entry for A has no numeric field.
 - Stays open: nothing for this task's screen share; R570 additionally binds the document and export (M5-T144 etc.).

ROW D-090-R641 — PASS
 - The overall label "Preliminary zoning results" is read from the document status_strip (first item) and rendered by the untouched ResultsStatusStrip; it is NOT typed in any non-test web source (grep of apps/web/src excluding tests returns none).
 - Test S7 asserts the rendered status strip contains "Preliminary zoning results" AND that doc.status_strip carries it (so the pass is not vacuous); the committed document's status_strip[0].text is exactly that string.
 - Stays open: nothing for this task; R641 also binds M5-T144 (the document producer that emits the strip text).

ROW D-090-R688 — PASS
 - The preliminary apartment estimate is kept SEPARATE from the applicable legal dwelling-unit limit: the building-options section shows the estimate but does NOT restate the legal limit (first-building-options.test.tsx S4), while the legal limit is the withheld value_state on the floor_area_allowance card (journey S4), and the top-level unit_estimate is a pointer ("…given in building_alternatives") not a figure.
 - The two never contradict on screen because only one place shows each; the legal limit shows "Not known …" with no number.
 - Stays open: nothing for this task; R688 also binds the hand-worked comparison tasks (M4-T037/T038, M5-T145/T146).

ROW D-090-R700 — PASS
 - The apartment-size and efficiency (share) assumptions stay labelled as preliminary assumptions on screen: both sit under "Preliminary assumptions used (not editable here):" and nothing presents them as law, measured, typical or validated.
 - Values are read from the document (share_low/high, apartment_size_sqft), not typed.
 - Stays open: making these assumptions changeable on this screen is work owed (ruling W7); that clause of R700 remains open in the registry.

(3) BINDING B1–B5
 - B1 PASS: comparing requirements.json at the base 06759249 vs the frozen head for all 12 rows, each row's text, classification and source_ref are byte-identical and M5-T147 is NEWLY appended to applicability.task_ids (R256/R509/R526/R540/R541/R543/R544/R556/R570/R688/R700 also gained M5-T146; R641 gained only M5-T147); nothing was removed.
 - B2 PASS: tools.directive_registry.sha256_text_artifact(requirements.json) = 55780617ad8e6a50611bb908ccab0b3677981745e17d93c39a666cc324d487b0, exactly equal to the manifest's requirements_content_digest_sha256.
 - B3 PASS: verification.json holds exactly ONE M5-T147 row (schema directive_verification/v2, producer frontend-engineer, verifier ""), listing precisely the 12 ids, each with state "pending", empty evidence and null reviewed_sha.
 - B4 PASS: reg.evaluate_task_refs(packet) returns ok=true with applicable_ids == cited_ids == the 12 rows, missing_ids/invalid_refs/unresolved all empty; derive_applicable confirms applicable == cited.
 - B5 PASS: derive_applicable scans all active directives and yields exactly these 12 — nothing else applies to M5-T147 uncited. Gate records: G0 PASS (orchestrator, administrative, re-recorded at the corrected head c560b8c2), G2 PASS (orchestrator self_check), G3 PASS (code-reviewer), G4 PASS (qa-engineer); G2/G3/G4 share ONE content identity (content_manifest_sha256 0f1c094df0… at reviewed_sha 4a7e2089) and their reviewed_at (23:15 UTC) is after the recorded CI green on f237d0d7. tools/validate_directive_compliance.py --check returned exit 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the blob-level predicate holds: the HEAD blobs of apps/web, packages/contracts, services/api/app, .github, tools, render.yaml and the task's reports (project-control/reports/M5-T147-*) are byte-identical to the frozen head, AND the 12 rows' text and binding (B1–B5) are unchanged.
 - Tolerated later commits: those touching ONLY project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other tasks on this branch (M5-T146 etc.), and a merge of the main line that changes none of the predicate's files. I confirmed this predicate already holds between the CI-green head f237d0d7 and the frozen head (only project-control files differ).

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE result. The two standing NOTEs (the typed "(on the HPD measurement basis)" label; the jsdom-structure-only narrow-table assertion) are non-blocking and already disclosed in the evidence map's known_limits.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not execute the apps/web jsdom vitest suite or the Playwright e2e: my copy rv-w6-b has no apps/web/node_modules, so per the brief I rely on CI and say so. I confirmed by inspection that the test sources and fixtures assert from the document non-vacuously, and I rely on the recorded CI run 38001788978 on f237d0d7 (21/21 jobs success, incl. web, web-e2e, api, contracts, modularity; secret-scan 38001788968 and context-budget 38001789211 success) — a run I read in the records, did not re-run, and whose material content equals the frozen head.
 - Real browser rendering, screen-reader behaviour, and the 420 px "no sideways scroll" measurement are outside jsdom; the walkthrough reviewer judged them from screenshots I did not independently capture.
 - The upstream correctness of the document's figures (footprint 6,716.67, storeys, 20,150 total, the withheld reasons) is the share of M5-T145/M5-T146; I re-derived the estimate quotients by hand but did not re-verify those producers' calculations here.
 - CI itself I did not re-run (read-only; reruns forbidden by the brief).

END-OF-REPORT
```
