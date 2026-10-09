# M5-T143 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `4626ebadac36b0396434dae0ac490f1b818199cd` (branch `task/wave15-emitter-split`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R570.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-09 03:23 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T143 (directive D-090, two rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier); this is an automated review, not a human or professional review. I produced none of this work or its records; every producer report, evidence map and gate report was treated as an unverified claim and reproduced from primary evidence in a read-only detached copy.

(1) HEAD VERIFIED
 - /root/project/rv-w6-a is at 4626ebadac36b0396434dae0ac490f1b818199cd (git rev-parse HEAD); it descends from 702a294a and carries material commits 4e7b9663, bb49fcba, 71334640.

(2) ROWS
ROW D-090-R229 — PASS
 - Row text: a value the program does not have is shown as not known, never a zero, default or guess.
 - test_db199b_shown_standard_limit_with_no_inner_block_is_withheld_with_no_number (test_three_answers_three_way_emit.py:1366) forces engine_doc["unit_estimate"]=not_available, then asserts way=="withheld", reason=="The legal dwelling-unit limit is not known: the figure it would be read from is not available for this lot.", resolved_by=="A recorded lot area, or a survey or deed dimensions.", the value object is None, and the would-have figure 16 is absent from _all_result_numbers — no number/zero/default appears. Focused run: 465 passed, 2 skipped, 1 xfailed, exit 0.
 - This is this task's whole share (the emitted document only); apps/web, drawings and PDF are untouched (git diff --stat ... -- apps empty), so the website/drawings/PDF part of R229 stays open (pending) in the registry for its own tasks.

ROW D-090-R570 — PASS
 - Row text: a withheld value stays withheld — no number, no older and no substitute value in its place.
 - test_db199a_every_block_of_the_emitted_document_is_classified (:1233) proves every top-level block and every in-answer key of six real documents is either walked by _all_result_numbers or named with a reason; test_db199a_completeness_guard_catches_a_new_numeric_block (:1266) proves a new numeric block (top-level and in-answer) fails the guard; the db199b test shows the withheld limit's would-have figure (16) is absent from the result numbers. All pass.
 - KNOWN DEFECT bearing on this share: for a corner lot in a recorded flood zone the withheld max_building_height (55) still sits at geometry.envelope.tiers[0].top_ft; the geometry guard reason (:1191-1198) names this truthfully and strict-xfail test_db199a_withheld_height_figure_leaks_into_geometry_known_defect (:1291) pins it. This task neither creates nor repairs it (no emitter behaviour changed), so the full R570 prohibition is NOT discharged here; the row stays open (pending) in the registry for the repair (backlog DB-209).

(3) BINDING B1–B5
 - B1: requirements.json diff 702a294a→head appends only M5-T143 to applicability.task_ids of R229 and R570, adds R641–R659 (source-065, all bound only to D-090-BOOTSTRAP, no wave task), and changes no existing row text or other field (reproduced in Python).
 - B2: sha256_text_artifact(requirements.json)=7c6e7aec… equals manifest.requirements_content_digest_sha256; audit_log has the 2026-10-09T01:25:49 "Bound task M5-T143 … R229, R570 … digest resynced … provisional verification row" entry and the source-065 amendment entry.
 - B3: verification.json has exactly one M5-T143 row; applicable_requirement_ids==[R229,R570]; both pending; verifier "".
 - B4: reg.evaluate_task_refs(M5-T143 packet) over the live registry → ok=true, applicable==cited==[R229,R570], missing/invalid/unresolved empty.
 - B5: only D-090 binds M5-T143 (grep of all directives); evaluate_task_refs returns no further applicable row, so nothing else applies uncited. Gates: G0 PASS(admin, dd430d4f); G2/G3/G4 PASS, all reviewed_sha 16156cf9 with one content_manifest_sha256 2b4739a2… (one identity); reviewers code-reviewer/qa-engineer ≠ producer backend-engineer. CI green on reviewed heads before the gates recorded 03:14Z (bb49fcba run 37874041571 completed 02:26Z; 71334640 run 37877222923 21/21 jobs success completed 03:08:58Z) — R639/R640 timing holds though not bound here. validate_directive_compliance.py --check exit 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head without re-review while: the frozen-head blob ids hold — three_way_document.py 0bad0df3, three_way_scope_lines.py 3f590234, test_three_answers_three_way_emit.py 48101caf, producer report 63e81df8; everything under packages, docs/reference-cases, .github, tools, apps/web, services/api/app (other than the two task app files), services/api/tests (other than the one task test file) and render.yaml unchanged; and R229/R570 text and their M5-T143 binding unchanged. Tolerated later commits: those touching only project-control/** and docs/DISCOVERY_BACKLOG.md, and a merge of the integration branch changing none of those files.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The frozen head 4626ebada is local/unpushed and has no CI run; I confirmed its three source/test blobs are byte-identical to the CI-green head 71334640 (only control-plane files differ), so CI green carries. I did not run the full api suite, the drawings/CAD/PDF snapshot suites or the web/e2e tests (forbidden / CI's job); I relied on gh showing 21/21 jobs success on 71334640 and success on bb49fcba. I did not run tools/test_directive_compliance.py (forbidden, hours).
END-OF-REPORT
```
