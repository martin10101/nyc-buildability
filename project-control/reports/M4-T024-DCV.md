# M4-T024 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `76f2b8ac7aa3890cbb420d5d3534d5b342e84252` (branch `task/M4-T024-r6b-reference-cases`, pull request 454, review copy `/root/project/rv-T024`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R226, R241, R259, R291 (4 rows).

## Verdict: PASS for all 4 rows. No required correction blocks acceptance.

The verifier writes "SATISFIED" for a row that is met; the registry's word for that state is PASS, and the verification rows use it.
- **R291 is met only for this task's share.** The row covers the whole of step 3 (check the R6B answers: resolve missing rules and conflicting inputs, and save independently calculated examples). This task saves the examples as files and shows each unsettled gap as "not known". It resolves no missing rule and no conflicting input; the verifier found that no record claims otherwise. The row itself stays open in the registry.
- It also checked the record of owner messages 99 and 100 that rides on this branch (source-047, rows R465 to R473): A1 to A5 all confirmed (each raw text against the saved transcript by digest; 32 quoted fragments, each an exact substring; forward and reverse trace; classifications; the manifest's digests and the audit log; no earlier row or source edited).
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head.
- What it could not check itself: the sealed folder given to the independent helper (outside the repository), so it could not prove from the folder that the helper had no access to the program; it relied on the helper's unchanged returns, the check that the support code imports nothing from the program, and the check that no case file holds a program result. The full api suite (the orchestrator's run at `79b46cf6`: 8075 passed, 8 skipped) and live CI. Read by the orchestrator on 2026-10-07 after the return: both CI runs on `76f2b8ac` completed with every job a success (push 37549098161, pull request 37549101748).

How the return arrived: in two parts. Part 1 arrived alone and the verifier stopped; the orchestrator asked the same verifier for the rest at once, and in the same message asked it to check one sentence of its part 1 against the work order (it had written that the program shows "not known" for row L7; the work order has two program columns). The verifier restated that sentence at the end of part 2 ("REPLACEMENT FOR R241 LINE 3": "Program today" reads "not available", "First screen" reads "not known (K13)"; the case's 35 matches neither). The two parts are joined below unchanged; the verification rows use the restated sentence in place of the original one.

---

```
PART 1 of 2

Role: INDEPENDENT directive-compliance verifier (gate reviewer) for task M4-T024, directive D-090. I produced none of this work or its records. I am an AI agent; this is an automated review, NOT a human or professional legal review. Read-only: I wrote no file, made no commit, ran no project_control/git/gh writes.
Frozen head: 76f2b8ac7aa3890cbb420d5d3534d5b342e84252 (confirmed via git rev-parse; review copy /root/project/rv-T024 clean, detached; PR 454 OPEN, not merged, not closed, headRefOid == frozen head).
Registry: directive_registry.evaluate_task_refs(task) -> ok=True, applicable == cited == [R226, R241, R259, R291], missing=[], invalid=[]. Confirmed.
OVERALL VERDICT: PASS.

ROW D-090-R226: PASS
 - Source traced: source-032-amendment.md message 76 item 5 "Include independently calculated, law-based test examples." is the exact owner text; row text and classification "harness" match.
 - Four case files (docs/reference-cases/R6B/cases/{real-lot,interior-lots,corner-reach,suffix}.json) each carry per-row facts+source, quoted law with section + snapshot id + content digest, why_applies, step arithmetic and expected value; I independently recomputed and the focused suite passed 31/31 (test_all_arithmetic_recomputes, test_each_row_is_followable).
 - Values trace to a blind hand-calculation, not the program: provenance/return-independent-hand-calculation-1.md and -2.md (present unchanged, each ends END-OF-REPORT) state the helper worked only from a sealed folder with no program access; I verified L1=20150 (2.00x10,075), L6=29 (20,150/680), L7=35 (24,180/680), interior P3=15, P5=16 all appear in those returns; each row's source_reference points at the return.
 - "Each example cites its section" verified at primary evidence: I reloaded 7 captured citations in real-lot.json and confirmed content_digest == live docs/research/zr-snapshots/v1/*.snapshot.json content_digest_sha256, request_url match, and quote is a substring of verbatim_excerpt (all True).
 - Engine-free: grep + the AST import-scan test (test_support_code_imports_no_engine) confirm the checker/renderer/loader/test import nothing from app.* .

ROW D-090-R241: PASS
 - Source traced: source-033-amendment.md message 77 "Matching an old saved result is not proof that it is correct." is the exact owner text; classification "evidence" matches.
 - No test accepts a value because it equals a saved program result: I read the whole test file; every numeric check recomputes from the row's own operands (decimal, r6b_reference_cases_lib.compute_step) or checks a law capture; there is no comparison to any saved program output anywhere.
 - No case file holds a program result: test_no_program_result_in_any_case passes on all four files, and the two mutation proofs (a program_today field / a "program today" sentence) fail as required; the work order's "Program today"/"First screen" columns are not copied in.
 - The L7 "not known"->35 change was made for a recorded, program-independent reason: project-control/reports/M4-T024-L7-ruling.md (independent code-reviewer, read-only) grounds 35 on the helper return line 46 ([C] 24,180/680=35.56->35); the program shows "not known" at L7, so the case does NOT match the program. Reason recorded in the case change log and scope_corrections[2]. real-lot.json L7 = value 35, arithmetic divide/dwelling_unit_three_quarters, eligibility caveat in does_not_establish.
 - README section "The rule for changing an expected value" states a program disagreement is never alone a reason and is "investigated on both sides" (test_readme_states_the_change_rule passes).

ROW D-090-R259: PASS
 - Source traced: source-035-amendment.md message 79 "Keep independently worked reference cases separate from program output." "AI can help prepare them, but agreement between AI answers alone isn't proof." exact owner text; classification "evidence" matches.
 - Cases live in their own files under docs/reference-cases/R6B/, apart from program output; test support under services/api/tests/rules/reference_cases/ is never read by the program at run time (no services/api/app/** changed; import-scan test).
 - Each case is followable and its page is byte-identical to its data: I ran r6b_reference_cases_render.py --check directly -> exit 0, "reference-case check PASSED".
 - "Agreement alone is not proof" is stated in README ("That agreement, between two AI answers, is not on its own proof of anything") and in every case what_it_is_worth ("prepared by an AI helper", "recomputed by a second AI", "not proof", "not professionally reviewed") - test_each_case_says_what_it_is_worth passes.
 - Change rule + a per-case change_log whose first entry is the dated creation, dates ordered (test_change_log_starts_with_creation_and_is_ordered passes).

ROW D-090-R291: PASS (for this task's bounded share; records do not overstate)
 - Source traced: source-039-amendment.md message 88 step 3 "Check the R6B answers." "Resolve missing rules and conflicting inputs, and save independently calculated examples to test against." exact owner text; classification "sequencing".
 - Share MET by this task (step R0): the independently calculated examples are saved as files to test against (four case JSONs + loader lib.load_row, tests S11 pass); each gap the reading could not settle is shown "not known" with a reason and no number (real-lot L5,L8,L12,L14,L15 and corner-reach cells; test_the_named_rows_are_not_known_with_a_reason_and_no_number passes).
 - Share NOT met and NOT claimed: resolving missing rules (capturing ZR 12-10 lot defs, 23-342, 23-363 -> step P1 / task M4-T025) and resolving conflicting inputs (the two area figures; shown/flagged on L1 does_not_establish, but "which applies" deferred). The not-captured sections are listed in README as waiting for step P1.
 - Records are honest: evidence-map R291 states verbatim "NOT done by this task, and not claimed: no missing rule is resolved, no conflicting input is resolved... This task covers only the saving of the examples as files." The task objective scopes it to step R0. No overstatement found.

(continued in PART 2)
```

```
PART 2 of 2

PART 2 - the record of owner messages 99 and 100 (source-047-amendment.md, rows R465-R473, captured in commit 12c1c5d2 on this branch).

A1 (raw text vs transcript; SHA-256 equality; quoted block == raw text): CONFIRMED.
 - Message 99: transcript f9ce0b61-...jsonl line 1737, type=attachment, uuid 8d27d1fb-13cf-42f2-93e5-a2afa362c122, field attachment.prompt = "/session-handoff " (trailing space). sha256 = a06af2e4eafbb032fc806c6321faa73b769390ac1f5a961bdde0f6bc552b70f3 == the digest in source-047. The source note documents the trailing space (not shown in the quote block, digest is of the raw text); uuid and timestamp match the source table.
 - Message 100: transcript 9c3a3cee-...jsonl line 13, type=user, uuid ebb6fa4a-f1aa-40b4-8e9c-1c4b7e0f210d, field message.content (a str). sha256 = cb54ecd86584397e2421901196c52af34ec0915da2b6afa24342cc7fef7454e0 == the digest in source-047. I reconstructed the "## Owner message 100" blockquote (stripping "> ") and it is byte-identical to the raw transcript text (== True).

A2 (every fragment quoted in R465-R473 is an exact substring of its own message): CONFIRMED.
 - All 9 rows R465-R473 appear in the Reading table. I extracted the 32 double-quoted fragments from the table and tested each against its own message's raw text (message 99 for R465, message 100 for R466-R473): 32 checked, 0 non-substring. Every quoted fragment is an exact substring.

A3 (forward + reverse trace): CONFIRMED.
 - Forward: message 99's whole text ("/session-handoff") -> R465. Message 100's four sections map completely - START/resume checks -> R466; goal -> R467; "Merging is open / three tasks contracted / DB-157 / CLAUDE.md question" facts -> R468; unvalidated assumptions -> R469; the five ordered NEXT ACTIONs -> R470; "asking again for the open decisions" -> R471; "number message 99 with the next record" -> R472; the STOPS block -> R473. No instruction is left unmapped.
 - Reverse: no row invents an owner obligation; each row's quoted spans are real substrings (A2). Interpretive additions are marked - R465 carries an explicit "ORCHESTRATOR'S READING:"; R467/R469 are framed "It restates R..."; the capture's notes ("What the start-up checks found", "Not new", "Already done when recorded", "Not claimed by this capture") are clearly the orchestrator's, not presented as owner words. This record lifts no restriction.

A4 (classification in the allowed vocabulary and fit): CONFIRMED.
 - R465 obligation, R466 harness, R467 decision, R468 external_fact, R469 hold, R470 sequencing, R471 return, R472 obligation, R473 hold. All nine are in the validator vocabulary (obligation|prohibition|hold|sequencing|dependency|decision|harness|evidence|external_fact|return|authorization) and each fits its content (e.g. the five ordered next actions = sequencing; the STOPS bundle = hold; the repo-state statements = external_fact; the owner-update item = return).

A5 (manifest consistency; no earlier row or source edited): CONFIRMED.
 - git diff d5fc21f0..76f2b8ac over the directive folder touches only manifest.json, requirements.json, source-047-amendment.md. The only removals are metadata: requirement_count 464, two updated_at values, the previous last-locked id D-090-R464, the two old requirements digests, and the old last source entry source-046 - i.e. NO existing row body (R001-R464) or earlier source file was edited.
 - Manifest resynced in the same commit: locked_ids extended through R465-R473; requirements_id_digest_sha256 and requirements_content_digest_sha256 updated; source entry source-047-amendment.md added with content_digest_sha256 c5ff75f8...; source list extended; an audit-log note appended ("Appended source-047... requirements R465..R473, all pending... no existing row edited").
 - I independently recomputed sha256(source-047-amendment.md) = c5ff75f8c888b184d5c2bca5116f0d20d2e0cec27ae03dc8fe25bfbeb8e5fa0b == the manifest's source digest (raw and LF-normalized identical).

VALIDATOR: python tools/validate_directive_compliance.py --check from the review copy -> DIRECT exit code 0 (quiet on success). Also run: tools/test_project_control.py -> exit 0 ("all 23 project-control test groups passed"); tools/test_directive_reminder.py -> exit 0 (12 tests OK); tools/modularity_check.py --check -> exit 0 (only pre-existing warnings on unrelated tools/agent_supervisor/* files, none on this task's files). Focused suite services/api/tests/rules/reference_cases -> 31 passed. Renderer r6b_reference_cases_render.py --check -> exit 0. I did NOT run tools/test_directive_compliance.py (CI's job) or the full api suite (orchestrator ran it alone at 79b46cf6: 8075 passed, 8 skipped).

CARRY-FORWARD CONDITION (blob-level predicate; my four-row verdicts and Part 2 CONFIRMEDs may be stamped at a later head without re-review iff, relative to 76f2b8ac, every one of these blobs is byte-unchanged):
 - the task's allowed paths: docs/reference-cases/R6B/**, services/api/tests/rules/reference_cases/**, project-control/reports/M4-T024-producer-report.md;
 - the cited law captures: every docs/research/zr-snapshots/v1/*.snapshot.json the cases cite (the citation check compares their content_digest_sha256 live);
 - services/api/app/** (cases stay engine-free; no production source touched), CLAUDE.md, .claude/rules/**;
 - the D-090 rows R226/R241/R259/R291 and R465-R473, the D-090 manifest.json, and source-032/-033/-035/-039/-047;
 - the work order docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md;
 - and any later commit changes only project-control/** bookkeeping (verification.json, state.json, M4-T024 status/accept seam, the gate records' acceptance), not the four reviewed gate JSONs' identity.
 Tolerance: a merge of the integration branch into this branch that touches NONE of the blobs above (e.g. only docs/SESSION_HANDOFF.md, docs/DISCOVERY_BACKLOG.md, docs/WORKING_KNOWLEDGE.md, other directives, or unrelated lanes/files), including an empty remerge-diff over the protected blobs, does not invalidate these verdicts.

BLOCKING CORRECTIONS: none. All four task rows SATISFIED; Part 2 A1-A5 all CONFIRMED; no VIOLATED or UNVERIFIABLE result.

NON-BLOCKING OBSERVATIONS:
 - R291 is a multi-step sequencing row spanning all of step 3; this task completes only step R0 (save the examples; show gaps as not-known). The remainder (missing-rule capture = M4-T025; conflicting-area resolution) is correctly deferred and explicitly disclaimed in the evidence map - no overstatement, but the row is not fully discharged by this task alone.
 - The G3/G4 reviewer notes were recorded as DB-162 (optional notes); I treated the reviewer report M4-T024-G3G4.md and the L7-ruling as claims and reproduced the evidence independently.
 - Producer-reported difference 2 (the "P2" interior probe dropped from table B) and the L7 difference are disclosed in the producer report and not silently resolved - consistent with S4.

WHAT I COULD NOT CHECK MYSELF:
 - The sealed packet given to the helper (/root/project/lanes-runtime/owner-docs/session-2026-10-06/sealed-packet/, outside the review copy) - I could not inspect it, so I cannot independently prove the helper had zero program access beyond what the provenance returns assert; I relied on the unchanged provenance returns plus the engine-free checker and the enforced "no program result in any case file".
 - The full services/api suite (8075 passed, 8 skipped) - run by the orchestrator at 79b46cf6, not re-run by me per instruction; I ran only the focused suite (31 passed).
 - Live CI on PR 454's head and the control-plane CI job - GitHub's job, outside my read-only reproduction; PR 454 confirmed OPEN / not merged / not closed at the frozen head.

REPLACEMENT FOR R241 LINE 3: The L7 "not known"->35 change was made for a recorded, program-independent reason: project-control/reports/M4-T024-L7-ruling.md grounds 35 on helper return line 46 ([C] 24,180/680=35.56->35); in work order table A line 450 the "Program today" column for L7 reads "not available" and the "First screen" column reads "not known (K13)", so the case's recorded independent value 35 matches NEITHER program column, confirming it was not fixed to agree with the program; the reason is recorded in the case change log and scope_corrections[2].

END-OF-REPORT
```
