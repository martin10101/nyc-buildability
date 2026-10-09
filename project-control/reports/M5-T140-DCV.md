# M5-T140 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `19fbded5e53f2020755dc1d636069ceeef60971d` (branch `task/wave13-results-panel`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R228, R229, R240, R255, R256, R258, R267, R268, R269, R292, R548, R556, R569, R570, R582, R584, R588.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: None. No blocking defect reproduced. The open items (DB-199 d strip wording on the server, DB-203 lot-without-geometry, DB-204 b sign-in, DB-204 c height upper limit, and the advisory walkthrough findings DB-206: no screen-reader announcement of a new result/failure, layout crowding) are already on record and are not this task's to close.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 18:00 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T140 (directive D-090, seventeen rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an automated independent review, NOT a human or professional review. I produced none of the work or records; I reproduced each judgement from primary evidence (source rows, the code at the frozen head, test runs with a direct exit code, git objects, the registry helpers, and the orchestrator's own run files). Every statement that a row is met "on the website" is bounded: the panel is behind INTERNAL_RESULTS_UI_ENABLED, off by default, set only on the :3001 test server, and nothing is deployed — so nothing is visible to a user yet and each row stays open in the registry for the rest of the report, the drawings, the PDF, the other options, and production activation.

(1) HEAD VERIFIED
 - `git -C /root/project/rv-w6-a rev-parse HEAD` = 19fbded5e53f2020755dc1d636069ceeef60971d; working tree clean.
 - `git diff --stat fa93d096 HEAD -- services packages .github tools render.yaml apps/web/package.json apps/web/package-lock.json` is empty; no forbidden path (globals.css, ResultsStatusStrip.tsx, ScopeSummary.tsx, property/page.tsx, ArchitectEntry/ArchitectShell.tsx, config.py) moved.
 - `validate_directive_compliance.py --check` exit 0 (direct). Named vitest files (results-api, results-contract-checks, results-ui-flag, three-answers, results-panel, dashboard-results-flag, answers/__tests__): 10 files, 183 tests, exit 0. modularity_check --check exit 0 (three-answers.ts carries a symbol-count warning only, a signal).
 - History told truly: commit order 6d024fc8..HEAD matches the records; G4 FAIL at ec228eae and the walkthrough's first FAIL are both stated plainly (G3G4.md §"One review FAILED at first", HJ.md §"first verdict was FAIL"); all six returns are kept verbatim (four in G3G4.md, two in HJ.md); gates G3/G4 (reviewed_sha cfa6315f) were committed at 17:48, after the green second run (web-checks-b3e84b3d-run2.out: pictures exit 0, e2e 155 passed, api 8655 passed/8 skipped, ALL DONE 17:46); no gate was recorded at ec228eae where G4 had FAILed.

(2) ROWS
ROW D-090-R228 — PASS
 - W-2 in results-panel.test.tsx (green in my run) compares every settled value, conditional "If …" line and "Not known" against the committed journey document; nothing is retyped.
 - results-api.ts/results-contract-checks.ts render a 200 body only after the client's own shape check; new sources hold only client constants (HTTP codes, timeout 12000, version "1.3.0") — no server height, result or reason is hardcoded (confirmed by reading both modules).
 - Stays open: agreement of the drawings and the PDF with the same result is later-milestone work; this task covers only the website numbers.
ROW D-090-R229 — PASS
 - results-contract-checks.ts lines 164-169 refuse a document whose key is withheld in value_states and also a shown value; three-answers.ts shows a withheld value as its reason, never a number; AnswerCard WithheldLine prints "Not known — reason" with no digit; S4/S21 tests green.
 - buildRequest omits an unentered height and statement (parseHeight treats "0" as invalid, not sent; densityStatement only when === true) — no zero, default or guess is introduced.
 - Stays open: the same "unknown stays unknown" rule on drawings and PDF.
ROW D-090-R240 — PASS
 - ResultsForm starts the height field empty with its helper line and the density box unchecked; ResultsPanel makes no call on mount/open/change (submit only via the button/retry), so an input not given stays unanswered and nothing is forced.
 - A first press sends housing_program only (buildRequest; S7/S9 green); dependents the server withholds render "Not known" with their reason.
 - Stays open: the full set of inputs across the report; this task carries three.
ROW D-090-R255 — PASS
 - ResultsForm density helper reads "This is your statement about the lot, not a recorded fact … any result it produces is shown as conditional on your statement"; it is never pre-filled and sent only when made.
 - The flag-on spec (read statically; proven green by the orchestrator's 155-e2e run) asserts the statement yields the standard unit limit (reference L6 = 29) as a conditional result naming the statement, never settled.
 - Stays open: facts/eligibility on every other surface and input; verified only for this one assumption here.
ROW D-090-R256 — PASS
 - Housing program is a visible editable choice starting at standard_residence; the height is a visible editable field empty at start; the website holds no starting number (three-answers/ResultsForm read; G3 check 8).
 - When the field is empty the server's starting height is shown and called the default (flag-on spec asserts "10-foot … used as the default"); 14 entered returns "A 14-foot … was entered"; a large height is now accepted (G4 re-review mutation (q) caught) — no value is applied unshown.
 - Stays open: other design choices (e.g. average apartment size) and their surfaces.
ROW D-090-R258 — PASS
 - three-answers.ts GAP_KIND_LINES holds the two plain sentences in one place; gapKindLine returns null for absent/null/unknown (`!= null`, never truthiness); AnswerCard prints the gap-kind span after the reason; S5 tests green.
 - A withheld value or whole not-available answer tells missing information apart from work still owed; the S14 guard and R10 wording keep "unsupported"/machine words off the screen.
 - Stays open: feature-vs-missing tracking across the whole report (backlog).
ROW D-090-R267 — PASS (this task's share)
 - No line the website writes calls a value confirmed/the property's maximum/feasible: the flag-on spec asserts innerText never contains "maximum for this property"; the S14 panel guard enforces it.
 - The strip's first item "Zoning maximum" is the server's words shown verbatim (ruling R5); its rewording is owed on the server (DB-199 d) before the switch is turned on anywhere and is stated plainly in the records and the walkthrough's advisory F3 — it is not this task's.
 - Stays open: the DB-199 d server wording and every rule whose "not checked → confirmed" risk lives off this screen.
ROW D-090-R268 — PASS
 - The reader carries the document's three-way layer faithfully: conditional values keep their "If …" lines (conditionLine), withheld values show reasons, unaffected answers stay visible; the flag-on spec shows heights conditional naming the unchecked conditions, coverage/rear-yard "Not known", building option "Not available".
 - Which answer is settled/conditional/withheld is the server's determination (M5-T136/T137); this task displays it.
 - Stays open: the server-side classification and the other options.
ROW D-090-R269 — PASS (this task's share)
 - The R6B heights appear as the district's limits, conditional, naming the unchecked conditions, and nowhere are called the property's maximum by a website-written line (flag-on spec; S14).
 - Same caveat as R267: the server's "Zoning maximum" strip text is shown as the document has it; its rewording is DB-199 d, on the server, on record.
 - Stays open: DB-199 d and the full set of height rules checked before any "maximum" claim.
ROW D-090-R292 — PASS (this task's share)
 - The flag-on spec observes a REAL cross-origin POST to :8000 returning 200 and proves a changed input changes its dependent result: 14 ft → the entered-height line; the statement → the unit limit appears conditional; each program → its program line.
 - LIMIT confirmed by G4's note (F1/F2): "only the unit limit changes" exclusivity and "every affected result" completeness are engine properties, not asserted on the screen; this task changes no server file.
 - Stays open: the exclusivity/completeness proof and step 4 for every other option.
ROW D-090-R548 — PASS
 - ResultsPanel renders PARKING_LINE ("Parking, loading and bicycle requirements are not yet checked for this option. It is not shown as feasible.") inside results-document whenever a success document shows; S13 green; the S14 guard confirms no value is called feasible.
 - Capturing the actual parking/loading/bicycle provisions is owed research (DB-180), not this display line.
 - Stays open: the provisions and the counts section.
ROW D-090-R556 — PASS
 - three-answers.ts headline branch (lines 316-326) shows a withheld headline's reason, never values[0]; three-answers.test.ts red/green proof green; mutation (k) reddens it.
 - results-contract-checks.ts additionally refuses any document that carries a number for a withheld key (S21 green), so a server error cannot surface an older/substitute value.
 - Stays open: the same guarantee on drawings/PDF/exports.
ROW D-090-R569 — PASS (this task's share)
 - The estimated apartment count (unit_estimate) is not in the reader's Pick, so it is never shown; the legal dwelling-unit limit appears under its own legal label in the floor-area answer (three-answers.ts; S13; walkthrough journey 5).
 - On this screen only the legal limit is present, under its own name, so the two cannot be confused.
 - Stays open: exports (PDF) and the case once the apartment estimate exists.
ROW D-090-R570 — PASS
 - A value the document withholds stays withheld on the screen — no number, older or substitute value (same reader guard as R556 plus the S21 refusal); S4/S21 green.
 - Evidence reproduced in results-contract-checks.ts and three-answers.ts at the frozen head.
 - Stays open: the "everywhere it is carried" guarantee in exports.
ROW D-090-R582 — PASS (this task's share)
 - This display connects after the emitting pieces: the packet's dependencies are M5-T136/T137/T138/T139 and the diff changes no services/api or packages file (confirmed empty).
 - The branch base is candidate/D-024-mrl-option-b at 6d024fc8; this task emits nothing on the server.
 - Stays open: that wave 8 and the emitting tasks were actually merged under the checks is verified by their own gates, outside this task's diff.
ROW D-090-R584 — PASS
 - results-ui-flag.ts: INTERNAL_RESULTS_UI_ENABLED is off unless an explicit true token is set; distinct from the server's INTERNAL_RESULTS_ENABLED; never NEXT_PUBLIC_.
 - playwright.config.ts sets INTERNAL_RESULTS_UI_ENABLED="1" only on the :3001 server (line 120); config.py (server flag) is unchanged and default-off; render.yaml/.github not in the diff; the flag-off spec proves no opener and zero requests on :3000.
 - Stays open: production activation stays held until sign-in (DB-204 b) and the owed server items; nothing here turns a production switch on.
ROW D-090-R588 — PASS (this task's share)
 - The packet is scoped as Part B (one screen, one option) and explicitly records what stays owed (DB-199 d, DB-203, DB-204 b/c, DB-206); it does not drop any section or declare the report finished.
 - The task title, objective and evidence map keep the full report and all options in view.
 - Stays open: the master plan/backlog carry the remaining sections and options; this task does not narrow the goal, but the program-level scope is tracked elsewhere.

(3) BINDING B1–B5
 - B1 PASS: across the whole 625-row registry, 6d024fc8→HEAD appends exactly "M5-T140" to the 17 named rows and to no other row; no row text or classification changed (only the metadata updated_at moved).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = 94a44e7f405d91e8a1cf6d99f481a491729cb4f605b270577491a582f7923f2a equals the manifest's requirements_content_digest_sha256; the audit_log carries the applicability_bound entry naming M5-T140 → the 17 rows, "digest resynced in the same commit; a provisional verification row (pending, verifier unset) added; no requirement text edited".
 - B3 PASS: verification.json has one M5-T140 row; applicable_requirement_ids are exactly the 17; producer frontend-engineer; verifier ""; every requirement state "pending", evidence []; reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(M5-T140) over the real registry returns ok:true, applicable_ids == cited_ids == the 17, missing/invalid/unresolved all empty; derive_applicable over all active directives yields exactly the 17 and nothing more.
 - B5 PASS: no other active directive (D-001..D-092) has a requirement applying to M5-T140 by task_id/type/milestone that is uncited. Gates: G0 PASS (048cf67e), G2 PASS (92a2d7c0), G3 PASS (cfa6315f), G4 PASS (cfa6315f); G2/G3/G4 all carry one content identity content_manifest_sha256 = e9a7ed51fb19c7180079572870af977a23d35408340f46d438c7853a672971d2, and apps/web is byte-stable b3e84b3d→HEAD (I could not recompute that exact hash from the working tree because the tool uses a different path-set/normalization; the three gates carry the identical value and the source is unchanged to HEAD).

(4) CARRY-FORWARD CONDITION
This PASS may be stamped at a later head WITHOUT re-review while ALL of the following hold: (a) the task's 26 allowed-path files keep the exact blob ids they have at 19fbded5e; (b) everything under services/api/app, services/api/tests, packages, docs/reference-cases, .github, tools, render.yaml, and apps/web/package.json, apps/web/package-lock.json, apps/web/src/app/globals.css, apps/web/src/components/architect/answers/ResultsStatusStrip.tsx and ScopeSummary.tsx is unchanged; (c) the text of the 17 rows and their binding to M5-T140 are unchanged (manifest digest 94a44e7f…, verification row intact). Tolerated later commits: commits touching only project-control/** and docs/DISCOVERY_BACKLOG.md; and a merge of candidate/D-024-mrl-option-b that changes none of the predicate's files. Any change to a predicate file, to the server results contract, or to a row's text voids this and needs re-review.

(5) REQUIRED CORRECTIONS
None. No blocking defect reproduced. The open items (DB-199 d strip wording on the server, DB-203 lot-without-geometry, DB-204 b sign-in, DB-204 c height upper limit, and the advisory walkthrough findings DB-206: no screen-reader announcement of a new result/failure, layout crowding) are already on record and are not this task's to close.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The browser suite's actual PASS: I was forbidden to run the e2e/build/api suites and could not drive a browser. I read results.flag-on.spec.ts and results.spec.ts statically and verified they assert the right behavior, and I read the orchestrator's run files (web-checks-ec228eae.out and web-checks-b3e84b3d-run2.out: 155 e2e passed, api 8655 passed/8 skipped, ports 0, ALL DONE) — but I did not re-execute them.
 - The server-side facts the journey relies on: _HOUSING_PROGRAM_DISPLAY label equality and the "only the unit limit changes" exclusivity are server/engine properties outside this task's diff; I confirmed the spec asserts the form label equals the returned line but did not run the engine.
 - The exact content_manifest_sha256 recomputation (see B5) and the merge-under-checks of M5-T136/T137/T138/T139 and wave 8 (R582), which are evidenced by those tasks' own gates, not by this task's files.
 - I ran the named unit test files (183 passed, exit 0) but not the full web unit suite (2491/116) or the full api suite (8655) — those remain the orchestrator's/CI's runs, which I read from the frozen run files rather than reproduced.
END-OF-REPORT
```
