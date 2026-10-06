# M4-T023 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `fd5d725213954e446cbff7a73c9105ff07c8d0a9` (branch `task/M4-T023-zoning-rule-review-register`, PR #452, review copy `/root/project/rv-T023`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R362 to R385, R393, R394, R423, R425, R426, R441, R442, R443 (32 rows).

## Verdict: PASS for all 32 rows. No required correction blocks acceptance.

The verifier writes "SATISFIED" for a row that is met; the registry's word for that state is PASS, and the verification rows use it.
It also checked the records of owner messages 93 to 97 that ride on this branch (source-042 to source-045, rows R344 to R457): A1 to A5 all PASS (each raw text against the saved transcript; 179 quoted fragments in 114 rows, each an exact substring; forward and reverse trace; classifications; the manifest's digests and the audit log).
Its carry-forward condition (item 4) is the rule for stamping these verdicts at a later head: (a) the 55 files under the task's allowed paths keep their blob ids (content identity `fc03d010`); (b) `CLAUDE.md`, the rule files, the law captures, the tests under `services/api/tests/rules/` and `.claude/rules/` are byte-identical; (c) the bytes of source-042 to source-045 and the text, classification, source reference and task binding of the 32 rows are unchanged; every later commit touches only `project-control/**` and `docs/**` outside `docs/zoning-rule-review/`, or is a merge of the integration branch that changes none of those files.
Its one non-blocking observation (the code reviewer's optional note as well): the first line of each run log under `docs/zoning-rule-review/evidence/` carries the internal task number; the rendered table and pages carry none. Left as it is; recorded for the owner.
What it could not check itself (item 6), and what the orchestrator read instead:
- Live GitHub state. Read by the orchestrator on 2026-10-06 after the return: pull request #452 is OPEN and the branch on GitHub is at `fd5d7252`, the verified head.
- The full api suite (the orchestrator's run at `9cb147a3` on this branch: 8044 passed, 8 skipped) and the registry validator (it reproduced the validator's per-directive checks itself; the control-plane CI job is the full run).
- Append-only history across commits cannot be proven by a build check; it is a standing duty of each change's reviewer, as `GUIDE.md` says.

Transmission: the verifier's return arrived in one message of three parts (PART 1 of 3 to PART 3 of 3), received 2026-10-06T19:58:16Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
PART 1 of 3

OVERALL VERDICT: PASS. All 32 bound requirement rows are SATISFIED on reproduced primary evidence, and intake checks A1-A5 all PASS. No VIOLATED/UNVERIFIABLE/BLOCKED row. I am the independent directive-compliance-verifier (not the producer rules-engineer, not the reviewer code-reviewer). I wrote nothing.

(1) HEAD VERIFIED: fd5d725213954e446cbff7a73c9105ff07c8d0a9 (git rev-parse HEAD in /root/project/rv-T023; working tree clean; its single parent is 1cdad2c0; `git branch -r --contains HEAD` = origin/task/M4-T023-zoning-rule-review-register).

ANCHORS reproduced before the rows:
- Content identity: the 55 allowed-path files at HEAD have blob ids byte-identical to allowed-path-blobs-fd5d7252.txt (55/55, zero mismatch, computed with git ls-tree -r HEAD). directive_registry.frozen_git_identity over the task allowed_paths at HEAD recomputes to fc03d010be3cac32f74bbd97f49833c1d912faebda1d66fe7620b285850c7dde, exactly the content_manifest_sha256 stamped in gates G2/G3/G4.
- Gate identity/independence: G2 (reviewer orchestrator, self_check, PASS, sha 83d64fc7), G3 and G4 (reviewer code-reviewer, independent_review, PASS, sha 1cdad2c0) all carry content_manifest fc03d010; producer rules-engineer != reviewer code-reviewer != me. The diff 1cdad2c0..fd5d7252 touches only project-control/** and docs/DISCOVERY_BACKLOG.md (no allowed_paths), so the gate-reviewed content equals the frozen-head content.
- Reproduced checks at HEAD (one at a time): `pytest tests/rules/test_zoning_rule_review_register.py` = 44 passed; `render_review_register.py --check` = "register check PASSED", exit 0; `tools/context_budget_check.py` = PASS, eager 9922/10000 tok.

(2) THE 32 ROWS

ROW D-090-R362: PASS
 - The register exists and reads without the code: docs/zoning-rule-review/REGISTER.md (23-row current table), 23 detail pages under docs/zoning-rule-review/rules/, HISTORY.md and GUIDE.md, all tracked at HEAD and rendered from services/api/app/rules/review_register/register.json.
 - REGISTER.md and every detail page show, per rule, the law, where it applies, the program's plain-English reading, a worked example and a human-verdict placeholder; `render_review_register.py --check` exits 0 and test_register_md_is_byte_identical passes, so the rendered record matches the data.

ROW D-090-R363: PASS
 - docs/zoning-rule-review/REGISTER.md is a standalone Markdown file holding one simple table of 23 rows (columns Rule | Law | Revision | Tests | Human verdict | Reviewer and date | Details).
 - test_register_md_is_byte_identical (44-test suite, all passed) asserts the committed table equals render.render_register_md(register.json).

ROW D-090-R364: PASS
 - Independently verified across all 23 entries in register.json: entry_id == rule_id (23/23), ids unique, and each rule_file_sha256 equals my own LF-normalized sha256 of the live services/api/app/rules/rulesets/*.rule.json (0 mismatch); rule_id and rule_version inside each live rule file match the entry.
 - 35 law references each carry content_digest_sha256 and snapshot_id byte-equal to the live docs/research/zr-snapshots/v1/*.snapshot.json; code_links/test_links reuse 55 existing files (all tracked at HEAD, confirmed via git ls-files), no record copied. Tests test_one_entry_per_rule_file_and_reverse, test_rule_version_and_sha256_match_live_files, test_law_digest_matches_live_capture pass.

ROW D-090-R365: PASS
 - Every entry's law[] carries section, official_url, last_amended and content_digest_sha256, plus applicable_from (verified present and non-empty for all 23); REGISTER.md column 2 renders "[section](official_url), applies from <date>" (e.g. row r1-r2-bare-pitched-height: "[23-421](...node/18075), applies from 2024-12-05").

ROW D-090-R366: PASS
 - All 23 entries have non-empty applies_where and a populated exceptions list; the detail page renders them under "Where it applies" and "Exceptions and limits" (e.g. r2x-r4-residential-far lists the qualifying-site and Special-Purpose-District exceptions).

ROW D-090-R367: PASS
 - All 23 entries have a non-empty interpretation field, rendered under "How the program reads it" (e.g. r2x-r4: "looks up the district's standard FAR (1.00 ...) and multiplies it by the lot area").

ROW D-090-R368: PASS
 - Each entry's example has inputs, expected{values,basis_kind,basis,prepared_by}, actual and agrees. test_example_actual_is_recomputed_through_the_engine evaluates every example's inputs through RuleRegistry.evaluate and asserts result.outputs == recorded actual.values and result.coverage_status == actual.coverage_status (not circular: actual is bound to the live engine).
 - Expected is independent: basis_kind distribution is law_text 18, reference_case 4, gap 1; test_agrees_equals_expected_vs_actual_or_null_for_gap asserts basis non-empty and prepared_by contains "not checked by a professional", and agrees == (expected.values == actual.values) or null for the gap (r6-r7-r8-wide-street-conditional-far).

ROW D-090-R369: PASS
 - All 23 entries carry non-empty code_links and test_links; I resolved every referenced code/test file (55 unique paths incl. evidence) against `git ls-files` at HEAD: 0 absent. test_linked_code_test_and_capture_files_exist passes; detail pages list them under "Code" and "Tests".

ROW D-090-R370: PASS
 - All 23 entries carry integer revision (all == 1) and a non-empty last_changed date, rendered in REGISTER.md column 3 ("1 (2026-10-06)"); check_review_register.history_errors requires current revision == latest history event (test_current_revision_must_match_latest_event).

ROW D-090-R371: PASS
 - register.json field_guide.verdict_values == exactly ["Not reviewed","Correct","Incorrect","Needs re-review"]; all 23 entries' human_review.verdict read "Not reviewed"; check_review_register.derive_human_review yields only those four values and human_review_errors refuses a stored verdict differing from the derived one.

ROW D-090-R372: PASS
 - All 23 human_review blocks contain reviewer_name, reviewer_role, review_date and comments, all empty; tests test_all_backfilled_entries_read_not_reviewed and test_not_reviewed_with_a_reviewer_name_is_rejected (a reviewer field set with decision null is refused) pass.

ROW D-090-R373: PASS
 - automated_tests is a block of its own; no "decision" key appears inside it and "automated_tests" is not inside human_review (verified for all 23; test_fields_are_fixed_and_structured). REGISTER.md shows "Tests" and "Human verdict" as separate columns; detail pages use separate "Automated test result" and "Human review" headings.

ROW D-090-R374: PASS
 - All 23 entries: human_review.decision is null and verdict "Not reviewed" (verified directly). check_review_register refuses a decision lacking a named reviewer/date/identity (test_decision_refused_without_a_named_reviewer_and_identity).
 - GUIDE.md ("How a human verdict is recorded") and REGISTER.md intro state a verdict comes only from a named human reviewer, never because tests passed or an agent agreed; CLAUDE.md principle 20 at HEAD ends "No session enters a human verdict." No production code outside the register package references human_review (grep over services/api/app = none).

ROW D-090-R375: PASS
 - A decision stores reviewed_revision, reviewed_conditions, reviewed_rule_file_sha256 and reviewed_law_digests; derive_human_review compares them to the entry's current revision/rule-digest/law-digests so a decision counts only for the version and conditions reviewed (tests test_s12a_rule_change_under_a_correct_decision_reads_needs_re_review and test_s12c_changed_law_capture_digest_flags_needs_re_review pass).

ROW D-090-R376: PASS
 - docs/zoning-rule-review/REGISTER.md is the short current table (one row per rule, linking each detail page); docs/zoning-rule-review/HISTORY.md is the append-only history (23 "created" events, contiguous seq 1-23). history_errors enforces contiguous seq, one created event per entry at revision 1, and current revision == latest event (tests test_history_rules_hold_for_committed_register, test_missing_created_event_is_caught, test_non_contiguous_seq_is_caught).

ROW D-090-R377: PASS
 - derive_human_review flips the shown verdict to "Needs re-review" when the rule digest, a law digest or the revision changes while keeping the stored original decision (tests test_s12a, test_s12b_touching_the_file_cannot_keep_an_old_correct, test_s12c); history records human_verdict_recorded then flagged_for_re_review (test_s12d). A changed rule whose entry is not updated is caught naming the rule (test_tampered_rule_sha_is_caught_and_names_the_rule asserts the message contains the rule id and "same change").

ROW D-090-R378: PASS
 - One entry per rule id/file and exactly one "created" event at revision 1 per entry (tests test_one_entry_per_rule_file_and_reverse, test_each_entry_has_a_created_event_at_revision_1); all 23 revisions == 1 and HISTORY.md has no duplicate event. GUIDE.md "Which changes move an entry's revision" states a register layout/wording change does not move a revision and forbids a second entry or a no-change event.

ROW D-090-R379: PASS
 - CLAUDE.md at HEAD, permanent principle 20 (one line): "Zoning-rule review register (D-090-R379): every session that adds or changes zoning-rule behavior must update the register (`docs/zoning-rule-review/`; how: its `GUIDE.md`) as part of the same change. No session enters a human verdict."
 - tools/context_budget_check.py = PASS, eager total 9922 of 10000 tokens, so the added instruction fits the cap.

PART 2 of 3

ROW D-090-R380: PASS
 - The register and its history live only under docs/zoning-rule-review/ and services/api/app/rules/review_register/; context_budget_check.py shows the eager auto-loaded set is CLAUDE.md + three .claude/rules/* files only (register files absent), so the detail is not auto-loaded; CLAUDE.md principle 20 points to the register (docs/zoning-rule-review/) rather than containing it.

ROW D-090-R381: PASS
 - 23 register entries for the 23 services/api/app/rules/rulesets/*.rule.json files (one-to-one, independently counted and matched; test_one_entry_per_rule_file_and_reverse asserts 23==23). Each entry is filled from checkable evidence: rule_file_sha256 (matches my LF recompute), law content_digest (matches live snapshot), an example recomputed through the engine, and automated_tests with a committed run log under docs/zoning-rule-review/evidence/<rule id>.txt (23 logs present).

ROW D-090-R382: PASS
 - All 23 entries carry a non-empty gaps[] list; the gap example (r6-r7-r8-wide-street-conditional-far) records basis_kind "gap" with empty expected.values and agrees null; committed_untested items read "no test found that exercises this" (test_committed_untested_items_say_no_test_was_found); r5b-height and r5d-height carry the gap line that the statement-to-district mapping is researcher-assigned/unconfirmed (first review note F2). No invented values (basis non-empty for non-gaps).

ROW D-090-R383: PASS
 - REGISTER.md intro and GUIDE.md state "This is a review record: nothing in the program waits for a verdict (ADR-007)"; no production code outside the register package references the verdict (grep services/api/app for review_register/human_review/applies_to_current = none). The check passes with no human decision at all (tests test_s13_updated_entry_without_a_decision_passes_the_check, test_s13_entry_whose_decision_no_longer_applies_passes_the_check); the task's required_gates are the ordinary G0/G2/G3/G4, none keyed to a register verdict.

ROW D-090-R384: PASS
 - entry_id is stable and equals rule_id (never changes); register.json carries schema "zoning_rule_review_register" and schema_version 1.0; field_guide fixes field names and closed value sets (verdict_values four, automated_test_status_values three, basis_kind three); test_fields_are_fixed_and_structured enforces ENTRY_KEYS/HR_KEYS/AT_KEYS/BEHAVIOUR_KEYS. GUIDE.md "Moving the register into a database later" maps entries to rows/columns.

ROW D-090-R385: PASS
 - `git diff --name-only 9c90ffbf HEAD` contains no supabase/**, no migration, no *.sql and no DB-connection code; the only services/api files changed are services/api/app/rules/review_register/{__init__,check_review_register,render_review_register}.py + register.json and the one test file. register.json is a flat JSON data file and GUIDE.md states "No database work is done now." (The lone project-control/blockers/B-030-...json in the diff is an unrelated sharp-advisory control record, not register DB code.)

ROW D-090-R393: PASS
 - Each entry has behaviour{tested, committed_untested, planned}; counts across 23 entries: 108 tested, 10 committed_untested in 7 entries, 45 planned. Every tested item names a test function and that function must be defined in one of the entry's linked test files (tests test_behaviour_is_structured_and_tested_items_name_a_test, test_tested_item_naming_a_function_not_in_a_linked_file_is_refused, test_every_committed_tested_citation_is_defined_in_a_linked_file); detail pages render the three lists under distinct headings.
 - "Planned, not built" holds missing behaviour only (first review note F3 applied); GUIDE.md documents the three-way split and the owner-update discipline (planned/committed/merged/tested).

ROW D-090-R394: PASS
 - The build check requires only that the record is current and never a human decision: tests test_s13_updated_entry_without_a_decision_passes_the_check and test_s13_entry_whose_decision_no_longer_applies_passes_the_check both pass (checker.validate returns [] while the verdict reads "Not reviewed"/"Needs re-review"); GUIDE.md states "The check enforces record-keeping only ... Development never waits for an examiner." No production code consumes the verdict.

ROW D-090-R423: PASS
 - REGISTER.md intro: "This register covers the 23 rule-definition files the program has today - one entry per rule. That is not complete coverage of the New York City Zoning Resolution"; GUIDE.md "What the register is, and is not" repeats it.

ROW D-090-R425: PASS
 - applies_to_current is derived by comparing the reviewed rule-file digest, law digests and revision with the current ones; the checker recomputes it and refuses a stored "Correct" when any reviewed identity differs, so touching/updating register.json cannot keep an old approval (test_s12b_touching_the_file_cannot_keep_an_old_correct asserts human_review_errors flags "Needs re-review"; test_s12a confirms a rule-digest change yields applies False/"Needs re-review" with the original decision retained).

ROW D-090-R426: PASS
 - human_review stores the original decision plus reviewer_name/role, review_date, comments, reviewed_revision, reviewed_conditions, reviewed_rule_file_sha256 and reviewed_law_digests unchanged; applies_to_current is a separate derived field; the detail page shows "Earlier decision ... it does not apply to the current version" when it lapses (test_s12d_history_records_the_decision_and_its_later_non_application).

ROW D-090-R441: PASS
 - automated_tests holds status (all 23 "Passed"), tested_commit (all 52e3d8a461cf08577273c82f802b85433f6f1ec3, 40 chars), tested_on, command, counts, evidence (a committed docs/zoning-rule-review/evidence/<rule id>.txt run log with command/date/commit/exit code/pytest summary, e.g. r6b-height.txt "32 passed", exit 0), tested_rule_file_sha256 and tested_test_file_sha256s. The checker demands "Not run" when a recorded rule- or test-file digest differs (tests test_changed_test_file_demands_status_not_run, test_changed_rule_file_demands_status_not_run, test_changed_second_linked_test_file_digest_demands_not_run). REGISTER.md "Tests" column shows status + short commit + log link, never a file count.

ROW D-090-R442: PASS
 - Both changes are built: the original decision is kept apart from the derived applies_to_current field (R425/R426 evidence) and the build check enforces record-keeping without requiring an examiner (R394 evidence); GUIDE.md affirms both.

ROW D-090-R443: PASS (with one caveat on live-GitHub, see item 6)
 - The register's branch task/M4-T023-zoning-rule-review-register containing HEAD is on the remote (`git branch -r --contains HEAD` = origin/...; `git remote -v` origin = https://github.com/martin10101/nyc-buildability). The review notes are committed in the repository at HEAD: project-control/reports/M4-T023-G3G4.md (first review, agent c55b7c47, five notes F1-F5), M4-T023-G3G4-rework.md and M4-T023-producer-report.md; the evidence map and reviewer records name where the work can be read.

(3) INTAKE CHECKS A1-A5

A1: PASS. For each of messages 93/94/95/96/97 I located the entry in the saved transcript by uuid and recomputed the raw-text SHA-256: msg93 (9b6b7b3f...jsonl line 825, uuid b2361151..., ts 2026-10-06T13:58:22.191Z) = d51fe2a0...1b6abe MATCH; msg94 (line 1264, 4f8ebf48..., 15:15:50.760Z) = 74413ccb...87174 MATCH; msg95 (line 1440, 2c6f52a5..., 15:34:59.023Z) = 49a1847e...1381c MATCH; msg96 (line 1629, 66f82e6a..., 15:51:42.854Z, the /session-handoff command tags) = 9c67e3be...9dc7de MATCH; msg97 (f9ce0b61...jsonl line 13, 86d7ead7..., 16:15:34.767Z) = 552d46f9...64a2a3 MATCH. All five line numbers, timestamps and stored-as kinds match the source tables.

A2: PASS. I parsed the leading quoted fragments from the registry `text` field of every row R344-R457 (114 rows, 179 fragments) and tested each as an exact substring (tabs preserved) of its own message content from the transcript: 0 non-substring, 0 rows with no parseable fragment. This mechanically covers every quoted fragment of the long messages 94 and 95 as required.

A3: PASS. Forward trace of messages 94 and 95: every numbered finding maps to rows - msg94 finding 1->R396/R397/R398/R399 (+Send-Claude R387/R388/R389), 2->R400/R401/R402/R403, 3->R404/R405/R406/R407/R408, 4->R409/R410/R411/R412, 5->R413/R414/R415, 6->R429/R416, 7->R417/R418/R419/R420, 8->R421, 9->R422/R423/R424/R425/R426, recommendation->R427/R428, plus R390/R391/R392/R393/R394/R395; msg95 1->R430/R431/R432/R433/R434/R435, 2->R436/R437, 3->R438/R439/R440/R446/R447, 4->R441/R442/R443, plus R444/R445. Reverse trace: the eight bound rows I verify restate the owner's words without widening/narrowing, and every interpretive extension is explicitly tagged "ORCHESTRATOR'S READING" (e.g. R364, R368, R379, R393, R443). No row asserts beyond the message.

A4: PASS. All 457 rows carry a classification in the registry vocabulary (0 outside {obligation,prohibition,hold,sequencing,dependency,decision,harness,evidence,external_fact,return,authorization}). The 32 bound rows' classes match their source Reading tables (R362/363 obligation, R364 prohibition, R365-372 obligation, R373 harness, R374 prohibition, R375 decision, R376/377 obligation, R378 prohibition, R379 obligation, R380 prohibition, R381/382 obligation, R383 decision, R384 obligation, R385 prohibition, R393 obligation, R394 prohibition, R423 obligation, R425/426 obligation, R441 obligation, R442 decision, R443 obligation); each is atomic (one obligation/prohibition each; the eight field rows R365-372 are one field apiece).

A5: PASS. manifest.json: locked_requirement_ids count 457 == the 457 requirement ids (equal set); requirements_id_digest_sha256 recomputes to c77b08a7...47b59 MATCH (sha256 of sorted newline-joined ids); requirements_content_digest_sha256 recomputes to 1ee779ef...b10aea MATCH (directive_registry.sha256_text_artifact of requirements.json); all 45 source content_digest_sha256 recompute clean, including source-043/044/045. audit_log (48 entries) contains the three capture entries (amended: source-043 @15:19:59, source-044 @15:36:47, source-045 @18:16:25) and an applicability_bound entry @15:39:55 binding M4-T023 to R393,R394,R423,R425,R426 (msg94) + R441,R442,R443 (msg95). verification.json (directive_verification/v2) has the M4-T023 row with applicable_requirement_ids = exactly the 32 ids, producer "rules-engineer", verifier "" (provisional/pending, all 32 states unset), reviewed_sha/reviewed_manifest_sha256 null. reg.evaluate_task_refs(M4-T023) returns ok=True with applicable (32) == cited (32), zero diff.

PART 3 of 3

(4) CARRY-FORWARD CONDITION
I accept your proposal with one tightening: my 32 row verdicts and A1-A5 stay valid at a later head iff (a) the task allowed_paths content identity still recomputes to fc03d010be3cac32f74bbd97f49833c1d912faebda1d66fe7620b285850c7dde (the 55 blobs in allowed-path-blobs-fd5d7252.txt unchanged); (b) CLAUDE.md, services/api/app/rules/rulesets/**, docs/research/zr-snapshots/**, services/api/tests/rules/** and .claude/rules/** are byte-identical to the frozen head; and (c) within project-control, the D-090 source-042/043/044/045 bytes and the 32 rows' text/classification/source_ref/applicability.task_ids in requirements.json are unchanged - so every later commit may touch only project-control/** (digest resyncs that preserve (c), filling the M4-T023 verification row, gate/report/state records) and docs/** outside docs/zoning-rule-review/, or be a merge of the integration branch that changes none of the files named in (a)-(c).

(5) REQUIRED CORRECTIONS
None that block acceptance. One non-blocking observation (already recorded by the code-reviewer, not a directive violation): the first line of each docs/zoning-rule-review/evidence/<rule id>.txt run log contains the internal task tag "(M4-T023)"; the rendered REGISTER.md/HISTORY.md/detail pages contain no internal ids, so the owner-facing register is clean. Does NOT block acceptance.

(6) WHAT I COULD NOT CHECK
 - Live GitHub state: I confirmed the branch/PR from the local clone's remote-tracking ref (origin/task/M4-T023-zoning-rule-review-register contains HEAD) and the origin URL (github.com/martin10101/nyc-buildability), but did not query GitHub over the network (not permitted), so I did not confirm PR #452 is open or that origin's tip equals HEAD right now. R443's "on GitHub" rests on the remote-tracking ref + committed review records.
 - Full api suite (reported 8044 passed/8 skipped at 9cb147a3) and tools/test_directive_compliance.py: not run per your limits; I reproduced the register suite (44 passed), render --check, and context_budget_check directly.
 - tools/validate_directive_compliance.py --check: not run (optional per your prompt; ~12 min). I instead reproduced its load-bearing per-directive checks directly - the c14 id/content digests, the 45 source digests, locked-id append-only, evaluate_task_refs, and the frozen content identity - all pass; the control-plane CI job remains the orchestrator's authoritative full run.
 - True cross-commit append-only history (S7/R376): the checker and I can see only the current register.json; append-only across git history is a disclosed standing reviewer duty (stated in GUIDE.md/HISTORY.md), not build-provable, and is a known honest limitation, not a defect.

END-OF-REPORT
```
