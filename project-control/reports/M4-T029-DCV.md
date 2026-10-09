# M4-T029 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `3c08c8dac8565c84966eebad2c42ef323efb3ab8` (branch `task/wave2-lot-reach-overlay-reading-further-captures`, pull request 460, review copy `/root/project/rv-w2-1007d`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
One verifier checked the two tasks M4-T028 and M4-T029 together. Its return is reproduced in full in both tasks' records (`M4-T028-DCV.md` and `M4-T029-DCV.md` hold the same text below the line); this file is the record for **M4-T029**.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R291 (1 row).

## Verdict: PASS for this task's row. No required correction blocks acceptance.

- **R291 is met only for this task's share.** The row covers the whole of step 3 (check the R6B answers: resolve missing rules and conflicting inputs, and save independently calculated examples). This task captures 27 law texts as source text; it resolves no rule and reads the text for no lot. The row stays open in the registry.
- **The failed first review.** The verifier confirmed that the review record keeps the FAIL (gates G3 and G4 at `eba169c5`, finding F1) unchanged, that the task's progress log records the FAIL, the rework and the re-review, and that the false statement (that ZR 12-10 does not define "residential") is gone from the builder's report at the frozen head. It read the official page itself: the definition exists, so the correction is right.
- **The conflict on the official site** (ZR 34-24(b)(3) points to "Section 35-71, inclusive" for sky exposure plane buildings; the page of ZR 35-71 is "Planting") is recorded and left undecided, in the builder's report and in row DB-169; the verifier reproduced it on the live site.
- It fetched four of the 27 captures' pages itself (ZR 35-71; the ZR 12-10 article "residence, or residential"; the table of ZR 34-112; the ZR 12-10 page's byte count) and found them equal to the captures. It did not fetch the other 23: the gate reviewer re-read every page, and the bundle test recomputes every digest.
- The registry validator, run by the verifier in the review copy: exit 0. The tests it ran (the reference cases and the capture bundle): 49 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head.
- Read by the orchestrator on 2026-10-07 at 08:16 UTC: the pull request's check list on `3c08c8da` showed 46 checks, all a completed success.

How the return arrived (2026-10-07, 08:16 UTC): as one message holding all three parts and the closing line. It is reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, line 2814; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 3

Header
- Role: INDEPENDENT directive-compliance verifier (DCV) for M4-T028 and M4-T029, directive D-090. I produced none of this work or its records; read-only.
- Frozen head: 3c08c8dac8565c84966eebad2c42ef323efb3ab8 (review copy /root/project/rv-w2-1007d, branch task/wave2-lot-reach-overlay-reading-further-captures, PR 460). Confirmed by git rev-parse HEAD; working tree clean.
- This is an AI agent's verification, NOT a human or professional/legal review (ADR-007).
- Task-ref check reproduced: directive_registry.evaluate_task_refs gives applicable==cited==rows for both tasks (M4-T028: R226,R241,R259,R291,R318; M4-T029: R291), ok=True, no missing/invalid.
- Source anchors reproduced verbatim: R226=source-032#msg-76, R241=source-033#msg-77, R259=source-035#msg-79, R291=source-039#msg-88, R318=source-040#msg-89; each requirement text matches the owner's quoted sentence.

ROW M4-T028 D-090-R226: PASS
 - docs/reference-cases/R6B/cases/overlay-reading.json holds 11 law-based rows, each citing its sections with snapshot_id + content_digest_sha256 + official_url (e.g. bulk-regulations cites 34-11 digest e54be53b.., 34-111 digest 5a71b0d9..); values trace to captured law text and the lot's PLUTO/DCM facts, never a program run.
 - The two readings are kept unchanged at docs/reference-cases/R6B/provenance/return-independent-hand-calculation-5.md and -6.md; I confirmed each states it worked only from a sealed folder with no program access, lists every file it read (all under sealed-p2), and marks NOT KNOWN rather than guess.
 - I diffed the saved readings against the returns the orchestrator received (owner-docs/.../return-reading-P2-1.txt and -2.txt): each received body is present byte-for-byte inside the saved file (received-body-in-saved=True); saved-file digests 3f7cd65e.. and 2c3d3c3d.. match the pins recorded in r6b_reference_cases_check.py OVERLAY_READINGS.
 - test_r6b_reference_cases.py asserts the case-file expected values, verifies both readings present unchanged (digest), and refuses a value where the readings differ; 49 tests pass. Limit: that the readers truly never saw program output is attested, not repository-provable (noted below).

ROW M4-T028 D-090-R241: PASS
 - git show 4b04689f -- cases/real-lot.json: the only edits are an extension of one "does not establish" sentence and a change_log entry that reads "No expected value changed"; no row value changed, L5 stays not known for its per-portion reason.
 - git show 4b04689f/d23f6faf -- cases/interior-lots.json: interior-coverage expected value is unchanged ("80 percent", confirmed by loading the row at HEAD); the DB-168 edits replace a too-broad prose sentence (a recorded "corrected reading") and add two ZR 23-362(b) citations — a prose/citation fix, not a value taken from or changed to match a saved result.
 - The overlay case asserts no whole-lot coverage percentage and no dwelling-unit count (rows lot-coverage, dwelling-units) and the README/check prove no case file carries a program result, so no expected value rests on a saved program result.

ROW M4-T028 D-090-R259: PASS
 - Each reference case is its own pair of files under docs/reference-cases/R6B/cases/<id>.json + <id>.md (overlay-reading added; real-lot, interior-lots, corner-reach, suffix, step-p1-worked present), with facts, quoted law, arithmetic and expected value, apart from program output.
 - README.md and overlay-reading.json what_it_is_worth / checked_by both state in terms that two AI answers agreeing is not, alone, proof; the case records prepared_by (reading 1) and checked_by (reading 2) as two independent AIs.
 - r6b_reference_cases_check.py enforces FORBIDDEN_VALUE_PHRASES / no-program-result and the loader imports no rule or scenario engine; the README records the rule that an expected value changes only with a recorded reason (corrected evidence / corrected reading / law change), and the change_logs carry such reasons. 49 tests pass.

END OF PART 1

PART 2 of 3

ROW M4-T028 D-090-R291: PASS
 - M4-T028's share of step 3 (save independently calculated examples to test against) is met: overlay-reading.json + overlay-reading.md are saved as files, and test_r6b_reference_cases.py reads their expected values; overlay-reading.md is a GENERATED FILE rendered from the json (header says so).
 - It resolves no missing rule and no conflicting input beyond what the captures allow, and shows that honestly: row section-35-633 is kind=not_known because Section 23-436 is uncaptured and the two readings differ on the 35-633(b) corner clause; rows floor-area-ratio, lot-coverage and rear-yard record the comparison "subject to" the uncaptured ZR 34-21 through 34-23 (reading 1 raised that residual, reading 2 read the route as settled), so no affected row reads as more settled than the more-cautious reading makes it.
 - No result is shown: M4-T028-producer-report.md line 6 "Nothing in this work comes from a program run"; I found no row recording a value the two readings do not both give on the same basis (the DU count and whole-lot coverage are explicitly not asserted). Resolving the remaining gaps (23-436, 34-21..23, etc.) is owed to a later reference-case task (DB-170 item a), not claimed here.

ROW M4-T028 D-090-R318: PASS
 - Same primary artifacts as R226: the overlay-reading case is worked from the captured source text by two readers who state they could not see the program's output, and is kept as files; this is the "independently worked, source-backed examples to check interpretation" rule (R318 restates rule 5 of R255-R260).
 - The caveat handling (reading 1's ZR 34-21..23 residual carried into exactly floor-area-ratio, lot-coverage and rear-yard, with a zr-34-11 citation quoting "except as modified by ... Sections 34-21 through 34-24") keeps the source-backed reading intact without strengthening or weakening either reading; verified in the row expected/does_not_establish text and in the report's round-2 note.

ROW M4-T029 D-090-R291: PASS
 - The 27 captures (26 in eba169c5, 1 in 2e60a66e) are source-text-only: each snapshot carries verbatim_excerpt, extraction_status=extracted_draft, and a note that "nothing here is a rule, an interpretation of the text for any lot, or a number derived." I independently fetched the official site and confirmed four: zr-35-71 raw_html_sha256 396bc0f3.. and 84740 bytes match exactly (page titled "Planting"); zr-12-10-residence-or-residential content_digest fffb54b1.. recomputes and its text ("A \"residence\" is one or more #dwelling units#...", "\"Residential\" means pertaining to a #residence#") is present on the live §12-10 page (1,316,758 bytes = the pin); zr-34-112 table section_title and cells (C4-6, R10, "Applicable residential equivalent") match the live page (97,134 bytes).
 - No record over-claims step 3: no rule resolved, no text read for a lot, no result shown. DB-170 states "NOT YET READ for any lot: all 27 new texts"; the capture notes and producer report keep to source text only.
 - The 34-24(b)(3) -> "Section 35-71, inclusive" (sky exposure plane) vs ZR 35-71 "Planting" conflict is recorded and left undecided: producer report section 4 ("recorded, not resolved"; nothing substituted) and DISCOVERY_BACKLOG DB-169 (status OPEN). I reproduced the conflict on the live site (35-71 body is the Section 23-613 planting text). The capture file correctly holds only the page's source text and does not embed the conflict reading.
 - The failed first review is honest: M4-T029-G3G4.md keeps the FAIL (G3/G4 FAIL at eba169c5, F1) unchanged; M4-T029.json progress_log records the FAIL, the rework and the re-review PASS; and the false "ZR 12-10 does not define residential" statement is gone from the producer report at the frozen head (§7 now reads "CAPTURED (round-2 correction)" with an honest account of the round-1 miss). I verified on the live §12-10 page that the definition does exist, so the correction is accurate.

END OF PART 2

PART 3 of 3

Harness (direct exit codes)
- python tools/validate_directive_compliance.py --check (run once from the review copy): DIRECT exit code 0.
- python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/rules/test_zr_snapshot_bundle.py (from services/api): 49 passed, exit code 0.
- I did NOT run tools/test_directive_compliance.py or the full api suite (per instructions; those are CI's job).

Carry-forward condition (stated up front)
- These six verdicts may be stamped at a later head WITHOUT re-asking me iff, as a blob-level predicate: (1) every file under the two tasks' allowed paths is byte-identical to the frozen head — docs/reference-cases/R6B/**, services/api/tests/rules/reference_cases/**, project-control/reports/M4-T028-producer-report.md; docs/research/zr-snapshots/v1/**, services/api/app/_zr_snapshots/v1/**, services/api/tests/rules/test_zr_snapshot_bundle.py, project-control/reports/M4-T029-producer-report.md; (2) the six requirement rows, the D-090 manifest, and the source files they trace to (source-032/-033/-035/-039/-040-amendment.md) are unchanged; and (3) every later commit touches ONLY paths under project-control/ and/or lines of docs/DISCOVERY_BACKLOG.md.
- I tolerate, with no effect on these verdicts, commits that touch none of the files in (1)/(2) — e.g. the M5-T127 files on this branch or any disjoint peer. I already reproduced that 66803c5a..3c08c8da (reviewed sha -> frozen head) changed only project-control/ files and docs/DISCOVERY_BACKLOG.md, so the tasks' allowed-path blobs at the frozen head equal the reviewed content (gate records G3/G4 PASS, reviewed_sha 66803c5a, reviewers code-reviewer for M4-T028 and data-contract-verifier for M4-T029 — matching the packets).

Required corrections that BLOCK acceptance: none.

Non-blocking observations
- README "not captured"/"uncaptured" wording is reconciled with the repo only via the README's definition ("the readers did not have"), because M4-T029 captures on the same branch some texts the readers earlier named as missing; DB-170 records this and owes uniform "the readers did not have" wording inside the case files to the next reading task. Not a defect at this head.
- zr-35-71's last_amended is the Unix-epoch date 12/31/1969 (the portal shows no real amendment date and no machine-readable <time> stamp); correctly recorded verbatim and flagged in the capture notes and DB-169.

What I could not check myself
- The negative that the two step-P2 readers never saw the program's output and that the sealed folder held no program result: the sealed scratchpad is ephemeral and outside the repository. I verified the saved readings match the orchestrator-received returns verbatim, cite only sealed-folder files, and keep strict NOT-KNOWN discipline, which corroborates but does not prove the negative.
- I independently re-fetched and verified 4 of the 27 M4-T029 captures (zr-35-71, zr-12-10-residence-or-residential, zr-34-112 table, and the §12-10 page byte count) against the live official site; I did not re-fetch the other 23 (the gate reviewer did; the bundle test and in-file digest recomputation cover them deterministically).
- tools/test_directive_compliance.py and the full api suite were not run by me (excluded by instruction).

Overall verdict: PASS for all six rows (five M4-T028, one M4-T029). No VIOLATED, BLOCKED or UNVERIFIABLE row; no blocking correction.

END-OF-REPORT
```
