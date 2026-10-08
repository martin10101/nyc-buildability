# M5-T139 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `4f7e818de07ba0caada7f5652a95ebc98da6bbdb` (branch `task/wave12-user-choices-said-truly`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R256, R582, R584, R588.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 14:53 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T139 (directive D-090, four rows)
VERDICT: PASS
(1) HEAD VERIFIED
 - I am an AI agent (independent, read-only directive-compliance verifier); this is an automated review, NOT a human or professional review. I produced none of this work or its records and treated every report, evidence map and gate record as an unverified claim.
 - `git rev-parse HEAD` in /root/project/rv-w6-a == 4f7e818de07ba0caada7f5652a95ebc98da6bbdb (the frozen head). Branch task/wave12-user-choices-said-truly; no PR; task status awaiting_gate (not accepted/merged). Nothing merged, accepted, dispatched or deployed for this task.
 - Commit order 10607b0e..HEAD matches the record: 9bf39565 contract, 5ed7b4c8 claim+G0, b8bcbb74 builder material (7 files), 82c32742 integration, 091860aa reviews-kept+evidence-map, 3e595a6b submit+G2, 4f7e818 G3/G4. Both reviews were made at 82c32742, both PASS on first reading, no correction asked, no review failed; both returns are kept verbatim and the six notes (G3 F1–F3, G4 F1–F3) are named in M5-T139-G3G4.md. The six material blob ids the reviewers pinned at 82c32742 are byte-identical at the frozen head, so the reviews carry.
 - `validate_directive_compliance.py --check` DIRECT exit 0. Focused suites tests/api/test_results_read_law_examples.py + test_results_read_api.py + tests/scenario/three_answers: 413 passed, 2 skipped, exit 0. modularity_check --check exit 0, three_way_document.py 599 lines (no warning for it). Whole-tree diff 5ed7b4c8..HEAD = only the 6 app/test files + project-control ledger; packages, apps/web, tests/cad, tests/drawings diff EMPTY; engine_disclosures.py, evaluator_inputs.py, results_request.py, engine_conditions.py untouched.
(2) ROWS
ROW D-090-R256 — PASS
 - Entered height is said to be entered: test_t139_s1 drives the real POST route with floor_to_floor_ft 14 and asserts the floor_to_floor_ft scope row has value 14, unit feet, basis "entered", statement "A 14-foot floor-to-floor height was entered for this run.", and "default" absent — reproduced green.
 - Starting value still called the default: test_t139_s2 (no height) keeps value 10.0, basis "default", engine sentence "A 10-foot floor-to-floor height is used as the default." unchanged; test_t139_s3 for all three programs gives basis "entered", "<Display> was selected for this run as the housing program.", never "the default housing program", value == program.
 - No value applied unseen: the transform's user-choice branch sets only basis+statement (reads row["value"] for the sentence only); S5 test deep-copies the whole document and asserts _blanked(d1)==_blanked(d0) with value/unit unchanged — nothing else moves.
 - Stays open: R256 covers the visible/editable starting values and every design choice program-wide; only this task's two scope lines are closed here; the row stays applicable to BOOTSTRAP/M5-T137/M5-T138 for the rest.
ROW D-090-R582 — PASS
 - This task is a small correction inside the already-merged "emit results document" piece (wave 11 merged as 10607b0e per the backlog sweep); it adds no website file and builds only on merged work, so no merge is lightened and nothing is built on unmerged work.
 - The agreed results display (website panel) is recorded as the NEXT piece, not built here (DISCOVERY_BACKLOG sweep 2026-10-08 wave 12; evidence map R582).
 - Stays open: the whole ordering obligation (finish/merge wave 8, then emit, then connect the display) keeps binding later tasks; this task only shows its one fix respected the order.
ROW D-090-R584 — PASS
 - Whole-tree diff 5ed7b4c8..HEAD shows app/main.py, app/config.py, render.yaml and .github byte-identical (empty diff): no mount, switch default or deployment setting moved.
 - The route stays behind INTERNAL_RESULTS_ENABLED (off by default; config.py unchanged); the material commit adds no switch and turns none on (route tests must call _enable to exercise it).
 - Stays open: the activation hold (all production switches off, no hidden feature on) keeps binding M5-T136/137/138 and future work; this task only shows it changed no activation surface.
ROW D-090-R588 — PASS
 - The change edits only two scope lines and drops nothing from the report; the backlog sweep records what stays owed (DB-204 points b–f OPEN; website panel next; three_way_document.py must split before growing), so scope is not narrowed.
 - No step or update narrows the goal to the results screen or to one option (task packet objective and evidence map keep the full report and all options in scope).
 - Stays open: keeping the full report and every promised option in scope is a standing program-wide obligation; this task only demonstrates it dropped no scope.
(3) BINDING B1–B5
 - B1 PASS: requirements.json diff 10607b0e..HEAD = only updated_at + four appends of "M5-T139" after "M5-T138" in applicability.task_ids of R256, R582, R584, R588; no row text/statement changed; requirement_count 625 unchanged.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) == manifest.requirements_content_digest_sha256 (bde8cfa5…); audit_log has the 2026-10-08T13:54:18 "applicability_bound" entry (bound M5-T139 to the four, digest resynced same commit, provisional verification row added, no requirement text edited).
 - B3 PASS: verification.json has exactly one M5-T139 row; applicable_requirement_ids == the four; each requirement state "pending"; verifier "".
 - B4 PASS: evaluate_task_refs on the M5-T139 packet over the real registry returns ok=true, applicable==cited==the four, missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: missing_ids empty across the full loaded registry => nothing else applies uncited. Gates G0 PASS (orchestrator 9bf39565), G2 PASS (orchestrator self-check), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer); G2/G3/G4 share one content identity content_manifest_sha256 93bb7074c894….
(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head without re-review while, blob-level: results_read.py e012a3a7, result_way_engine_bridge.py cb5a8570, three_way_document.py bc6b3459, test_results_read_api.py 4822ca17, test_results_read_law_examples.py bd9dc884, test_three_answers_three_way_emit.py 1b4cf5ff keep those blob ids; everything under services/api/app/contracts, services/api/app/rules, packages/contracts, apps/web, services/api/tests/cad, services/api/tests/drawings and docs/reference-cases is unchanged; and the text of the four rows and their binding to M5-T139 is unchanged.
 - Tolerated later commits: commits that touch only project-control/** and docs/DISCOVERY_BACKLOG.md; and a merge of the integration branch that changes none of the predicate's files. The producer report (937e664a) may change freely. If any of the six blobs changes, re-verify.
(5) REQUIRED CORRECTIONS
 - None.
(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full api suite (forbidden here); I relied on the record of 8655 passed / 8 skipped at 82c32742 and did not reproduce it.
 - CI on a pushed head (no PR exists yet) and any live/production behavior of the route (off by default; I exercised it only offline through the FastAPI test client).
 - The builder's mutation proofs: I did not rerun them; G4 reports 11 mutations all caught in an external copy, and the S1 red proof, which I did not independently re-derive beyond confirming the pre-change source lacks the user-choice branch.
 - The full tools/test_directive_compliance.py suite (forbidden, hours); I ran validate_directive_compliance.py --check once (exit 0) as the authoritative harness evidence.
END-OF-REPORT
```
