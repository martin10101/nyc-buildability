# M5-T186 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `dce279695cb8cfb3723da87242ede8d952d9cfbd` (branch `task/wave27-comparison-appendix`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R007, R075, R084, R102.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T13:02:23Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T186 (directive D-094, 4 rows)
VERDICT: PASS

I am an AI agent. This is an independent, read-only machine verification of directive compliance, not a human or professional/legal review. I produced none of this work. Every row and figure in the case is an explicitly-labelled unreviewed AI draft reading of the law (ADR-007).

(1) HEAD VERIFIED
 - I read the frozen head dce279695cb8cfb3723da87242ede8d952d9cfbd on branch task/wave27-comparison-appendix (base main 76745ade).
 - All task content was read via git plumbing at that sha (git show dce27969:<path>); the on-disk requirements.json equals the frozen-head blob.
 - The branch head advanced to 155ea3cc during my review; the only change was docs/DISCOVERY_BACKLOG.md (a disjoint-peer backlog sweep) and no predicate file moved.
 - validate_directive_compliance.py --check returned exit 0 (quiet success); git log -1 was read to rule out a transient c14.

(2) ROWS (this task's share; numeric order)

ROW D-094-R007 — PASS
 - benchmark-options-4-11.json records option 4 (FAR 2.00, 20,150 sq ft, factor 680, 29 units) and option 11 (20,150/24,180 sq ft, 29/35 units, heights 30/45/55 and 30/45/65), the last two owed options.
 - The options-out-of-scope row states recording options 4 and 11 "does not narrow the eleven-option scope" and maps all eleven options to their cases; README row 42 says the set is complete across the reference cases.
 - This task's share (record the two owed options, remove no option or section) is delivered from primary evidence.
 - STAYS OPEN: the report's concise entry point, drawings and shown building-geometry/scenario results are owed by later report/engine tasks, not this one.

ROW D-094-R075 — PASS
 - The worked results the comparison needs for options 4 and 11 are recorded only where both sealed readings agree on value and basis and the option's comparer confirms (step_p11 per-option pair+comparer guard; 249 reference_cases tests pass).
 - I independently recomputed the arithmetic: 2.00x10,075=20,150; 20,150/680=29.63->29; 2.40x10,075=24,180; 24,180-20,150=4,030.
 - 31 of 45 rows carry recorded values with an administrative_record/derived basis; the 10,075 (administrative_record) and GIS 10,387.99 are never combined.
 - STAYS OPEN: the page-4 ordering (comparison before limitations) and showing these results on the page are a later report/engine task (evidence-map known_limits: "not evaluated until an engine task works them").

ROW D-094-R084 — PASS (prohibition honored)
 - The options-out-of-scope row lists all eleven options mapped to their cases (option 1 real-lot/step cases; 2/3/6/7 M5-T184; 5/8/9/10 M5-T185; 4/11 here); nothing is narrowed.
 - Owner questions N1 (split-lot/option 8) and N2 (shared housing) are kept kind=not_known with no number (opt11-split-lot-meaning, opt11-shared-housing); each does_not_establish says the case decides neither N1 nor N2.
 - Option 11's repeated figures cross-cite the prior cases and open no new pool: 20,150/29 cite option 1; 24,180/35 cite benchmark-options-2-3-6-7.json#opt2 (which records 24180 and 35 — reproduced).
 - STAYS OPEN: nothing of this prohibition for this task; showing all eleven options in the report export is later work.

ROW D-094-R102 — PASS (this task's share: a captured-section feed only)
 - All 49 citations are kind "captured"; I independently confirmed every content_digest equals its docs/research/zr-snapshots/v1 snapshot's content_digest_sha256, every official_url matches, every quote is found in verbatim_excerpt, and all 7 table assertions hold (R6B FAR 2.00/2.40; heights 30/45/55 and 30/45/65).
 - No uncaptured section (76-131, 23-154, 77-00, 35-34+, MDL/HMC/Building Code) appears as a formal citation; they are named only in not-known prose.
 - The task edits no law-library page (docs/zoning-law-library/ is a forbidden path and the 37403e84 diff touches none); the worked values and per-section capture state feed the option-4/option-11 library pages.
 - STAYS OPEN: the actual zoning-law-library build (sections reachable, cross-references followed, the handles/does-not list, the pitfall list, the handoff telling the next session) is held by the M3-Txxx library-lane tasks, not this one.

(3) BINDING B1-B5
 - B1 PASS: contract commit 835e3e24 appended "M5-T186" to applicability.task_ids of R007, R075, R084, R102 and changed no requirement text; requirements.json is byte-identical from 835e3e24 through the frozen head (no intervening commit, empty diff).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = 209ddf6b1a528283012f6fd60c9306305bd6c7d543f31d8c0f266cb59afe29e1 = manifest.requirements_content_digest_sha256, resynced in the same contract commit with an applicability_bound audit_log entry.
 - B3 PASS: verification.json holds one M5-T186 row with exactly [R007,R075,R084,R102], producer rules-engineer, verifier "", every requirement state pending, reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(packet) returns ok=True, applicable_ids == cited_ids == the four ids, missing/invalid/unresolved all empty.
 - B5 PASS: the derived applicable set equals the cited set, so no other active-directive requirement applies to this task uncited.
 - GATES: G0 PASS (orchestrator, sha 835e3e24); G2 PASS (orchestrator), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer), all reviewed_sha 4f3a294e. This task's allowed-path files are byte-identical from producer 37403e84 through the frozen head, so G2/G3/G4 are one content identity; reviewers examined 37403e84 and records pin 4f3a294e. CI run 38735954825 at 4f3a294e: completed, 21/21 jobs success. I reran focused checks at the frozen head: ruff clean, reference_cases pytest 249 passed, render --check PASS, modularity_check --check 0 failures (check.py 596, step_p11 373, cases.py 48, lib.py 457, render.py 369 — all < 600, split via a CASE_MODULES facade, principle 16). Task status awaiting_gate (not accepted); nothing merged to main; no prohibited action.

(4) CARRY-FORWARD CONDITION (stated up front so this PASS can be stamped at a later head without re-review)
 - Blob-level predicate: these frozen-head blobs stay identical — benchmark-options-4-11.json f53caac7, r6b_reference_cases_step_p11.py 851fed68, r6b_reference_cases_cases.py 06eaf61b, r6b_reference_cases_check.py 090c603d, requirements.json a913f9d9, and the remaining M5-T186 allowed-path files (provenance -32..-37, the .md page, README, lib.py, render.py, the moved p7/p8/p9/p10 test pins, test_r6b_reference_cases.py, test_step_p11.py, producer-report.md); AND the four rows' text and their M5-T186 applicability binding unchanged.
 - Broad disjoint-peer tolerance: later commits MAY touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records and a main-line merge that changes none of the predicate's files.
 - Already exercised: 155ea3cc touched only docs/DISCOVERY_BACKLOG.md and every predicate blob stayed byte-identical; the stamp may be recorded at 155ea3cc or any later head meeting the predicate.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Whether the v1 snapshots faithfully reproduce the live official Zoning Resolution text: those captures belong to M3-T010; I confirmed only that the case's cited digests equal each snapshot's own content_digest_sha256 and that each quote appears in verbatim_excerpt. I made no outside fetch (read-only, no ports/servers).
 - The legal correctness of the AI readings themselves (the 35-31 greatest-single-use mechanic, the NB-05 special-density and NB-06 mixed-building/street-wall draft readings): per the brief I checked settled figures against the sibling cases and the domain anchors but did not re-derive the law; all rows are labelled unreviewed AI drafts.
 - I did not run tools/test_directive_compliance.py or the full api suite (forbidden); I relied on validate_directive_compliance.py --check (exit 0), the focused reference_cases pytest, render --check, modularity_check --check, and CI run 38735954825.
 - The owner-facing report-presentation outcome of R007/R075 (page-1/page-4 redesign, drawings, displayed results) is later report/engine work; I verified only this task's recorded-values and capture-feed share, not any report page.
END-OF-REPORT
```
