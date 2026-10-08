# M5-T135 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `6645a320dbdcb6efa4c353dcdabc50dcdca4004b` (branch `task/wave8-captures-measurement-basis`, review copy `/root/project/rv-w6-b`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R513, R516, R519, R534, R539, R540, R541, R542, R543, R544, R545.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No blocking defect found. Three non-blocking NOTES for the acceptance sweep (already tracked): the legacy "25 percent allowance" shorthand in the intro/section 7 (align to 0.60–0.75); T1 asserts presence not absence of a validation-contradicting sentence (G4-F2); and the "not captured yet (Article III, Chapter 3)" phrase will go stale once M4-T036's captures are read into the reference cases.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 05:27 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T135 (directive D-090, eleven rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier). This is an automated, read-only review, not a human or professional/legal determination. I wrote nothing in any repo; I ran status-free inspection, the two focused tests, and the validator once.

(1) HEAD VERIFIED
 - `/root/project/rv-w6-b` is at `6645a320dbdcb6efa4c353dcdabc50dcdca4004b` (git rev-parse HEAD), the frozen head; working tree clean.
 - The task's one material commit is `c8988873`; `git show --name-status c8988873` touches exactly the 7 allowed files (record, example-c json+md, producer report, measurement_basis_check.py, measurement_basis_fit.py, test_measurement_basis_examples.py) — no program source, capture, reference case or other doc (S14 satisfied).

(2) ROWS
ROW D-090-R513 — PASS (this task's share)
 - Record section 6 (lines 344-362) states shared floor area as "a required calculation, not a switch and not an optional allowance (R513)", quotes ZR 23-20 verbatim with digest 0685a2e4…, says it "does not necessarily increase the residential figure", and leaves a missing-area result "not known"/conditional.
 - I read each capture file: digests cited for zr-23-20, zr-35-30/31/32/33, zr-12-10-mixed-building all equal the file's content_digest_sha256, and each quoted sentence (markup stripped) is a verbatim substring of its verbatim_excerpt; test_every_new_law_quote_stands_in_its_capture passes.
 - The row still binds M5-T133, M4-T034, M4-T035 (the capture/read work); it stays pending in the registry for the whole directive, this task satisfying only the record's statement of the rule.
ROW D-090-R516 — PASS (this task's share)
 - Section 1d (lines 176-224) states eligibility from captures: fully-electrified = a building existing 12/6/2023 (so a new building cannot be one, digest 2ea4afe2…), ultra-low-energy provisional at plan approval and confirmed post-construction (8a1d6418…), wall exclusion = thickness added to an existing building not new ordinary walls (119324c8…), energy exclusion 15 of zr-12-10-floor-area (e14ecafc…) — all digests verified equal to the capture files.
 - It says a user statement "supports only a conditional result; it never establishes eligibility", there is no general "confirm it applies" switch, no example takes the energy exclusion, and Local Law 154 / the energy code are named not-captured (DB-188 item 7).
 - The row also binds M5-T133/M4-T034/M4-T035 for the capture work and stays pending registry-wide.
ROW D-090-R519 — PASS (this task's share)
 - Section 8c (lines 550-580) states floors above R6B's 45-ft maximum base height are set back and smaller, cites the ZR 23-432 table and ZR 23-433 setback, and labels a floors×floorplate count an assumption; the diff shows 8c body unchanged by this task.
 - What this task added is section 8a item 3 (line 491-492): the owner's 10/15-ft floor heights are "subject to the actual building envelope" and "not a licence to count equal floors above the maximum base height (R519, section 8c)"; examples B and C assumption-notes call equal floors an assumption.
 - The part this task cannot satisfy — the program computing the actual setback — is still open (8c says "The program does not work out the setback yet"); that is engine work beyond this document task and the row stays pending for it.
ROW D-090-R534 — PASS (this task's share)
 - M5-T135 is a contracted ledger packet (producer scenario-optimization-engineer); gate records G3 (data-contract-verifier) and G4 (qa-engineer) are PASS at one content identity (content_manifest_sha256 b25ce330…), both agents different from the producer; producer ≠ verifier holds.
 - Example C's two now-false statements were corrected: a correct JSON diff of example-c vs claim head shows exactly two changed string fields (what_it_does_not_show[1], shared_floor_area.conditional_note) plus an added dated change_log[2]; all 141 numeric values identical (ratio 0.6828, 98.32/21.68 unchanged).
 - Section 8 keeps the owner's choices (8a) apart from the questions of law (8b), its intro stating law is "never put to the owner as a preference"; R534's other sub-corrections are shared with prior tasks and stay pending registry-wide.
ROW D-090-R539 — PASS (this task's share)
 - Section 8a (lines 469-474) records the choices as DECIDED BY THE OWNER on 2026-10-07 and quotes "approved as preliminary, editable assumptions."; I confirmed this fragment is a byte-exact substring of source-057-amendment.md and of the record (whitespace-normalised for wrapping).
 - The intro and section 7 call the starting values "preliminary, editable assumptions"; test_section_8a_records_the_owners_decisions requires the needle and the R539 id and passes.
 - The row also binds D-090-BOOTSTRAP and stays pending registry-wide pending this verification being recorded.
ROW D-090-R540 — PASS (this task's share)
 - Section 8a item 1 (lines 476-480) quotes "Use 0.60–0.75 as an unvalidated sensitivity range." with the U+2013 en-dash preserved (byte-exact vs source-057) and carries it as unvalidated, editable, "never a validated or expected range".
 - T1 requires "0.60 to 0.75" and "unvalidated sensitivity range"; the record states them and no sentence calls the range realistic/expected/validated (grep of every "validate" occurrence — all are denials).
 - Non-blocking NOTE (reviewers' G3-F1): the intro and section 7 keep a legacy "25 percent allowance" shorthand not in the owner's words; it is labelled an unvalidated assumption, does not inflate the approval, and is a pre-existing phrase this task did not introduce — it does not defeat this row's share, which is stated correctly in 8a.
ROW D-090-R541 — PASS (this task's share)
 - Section 8a item 2 (lines 482-486) quotes "Use 700 sq ft as the chosen starting apartment size, on the HPD measurement basis." (byte-exact vs source-057), editable and "not a measured or typical average".
 - T1 requires "700 sq ft" and "hpd measurement basis"; the G4 mutation 700→750 fails the test, which I reproduced as passing at the head.
 - The row also binds BOOTSTRAP and stays pending registry-wide.
ROW D-090-R542 — PASS (this task's share)
 - Section 8a item 3 (lines 488-492) quotes "Use 10 ft residential floors and 15 ft shop ground floors as starting assumptions." (byte-exact), editable and subject to the building envelope.
 - T1 requires both floor heights and the R542 id; the test passes at the head.
 - The row ties forward to R519/8c (covered above) and stays pending registry-wide.
ROW D-090-R543 — PASS (this task's share)
 - Section 8a item 4 (lines 494-499) quotes the owner's sentence with both curly-quoted labels "Not known" and "Preliminary capacity estimate." (U+201C/U+201D preserved, byte-exact vs source-057).
 - T1 requires both labels as the owner words them; the G4 mutation to "capacity figure" fails it.
 - No screen is built by this document task, so the display behaviour the row also describes stays open for the estimator/UI work; the row stays pending registry-wide.
ROW D-090-R544 — PASS (this task's share)
 - Sections 4 (lines 293-299), 5 (lines 326-331) and 8a (lines 506-511) quote "Use the residential floor area the proposed building actually accommodates." and "Keep the legal ceiling separate." (both byte-exact vs source-057); the formula is unchanged (no numeric edit in the record diff).
 - test_legal_cap_is_separate_and_recomputes and test_mixed_use_uses_the_residential_portion_only pass; T1 requires the R544 id.
 - The row also binds BOOTSTRAP and stays pending registry-wide.
ROW D-090-R545 — PASS (this task's share)
 - The record states in the intro (line 22-23), section 7 (line 452) and 8a (lines 472-474) that the owner's approval "validates neither the assumptions nor the worked examples" and quotes "This approval does not validate the assumptions or the worked examples." (byte-exact).
 - I grepped every "validate" occurrence in the record and in all three example JSONs: each is a denial; no sentence says or implies the approval validates a value or example.
 - LIMIT (reviewers' G4-F2, which I confirm): T1 asserts the no-validation sentence is present, not that a contradicting sentence is absent; the delivered record holds no contradicting sentence, so this is a non-blocking robustness gap, not a violation — a backlog item.

RULING ON THE ARTICLE III CHAPTER 3 FACT: M4-T036's commit 9663a523 only ADDS new snapshots (zr-33-10/11/12/121…, Article III Ch 3, plus others) and modifies none of the captures this record cites; all 14 cited captures are blob-identical at claim head 599f9b0c and the frozen head. M5-T135 was correctly scoped to quote only claim-head captures, and no Article III Ch 3 text is read into any reference case yet. This does NOT affect any of the eleven rows (none requires the commercial FAR to be captured/read). The record's "not captured yet (Article III, Chapter 3)" becomes a documentation-freshness item once those captures are read — explicitly out of this task's scope (packet NOT-IN-THIS-TASK clause; evidence-map known_limit) and owed at the acceptance sweep. Non-blocking.

(3) BINDING B1–B5
 - B1 PASS: comparing requirements.json at 39e7f2d2 vs the frozen head for all eleven rows — text identical, rest-of-row identical, and M5-T135 appended as the last task_id for every one (verified programmatically); no row text changed.
 - B2 PASS: tools.directive_registry.sha256_text_artifact(requirements.json) = 1f621ca2d076461fb5a9aef10cf63b052996b9bae71e15dd10e2faa149868bc1, equal to the manifest's requirements_content_digest_sha256; the manifest audit_log carries the 2026-10-08 "applicability_bound" entry binding M5-T135 to the eleven rows with "requirements content digest resynced in the same commit".
 - B3 PASS: verification.json has one M5-T135 row, applicable_requirement_ids exactly the eleven, every per-requirement state "pending", verifier "".
 - B4 PASS: reg.evaluate_task_refs(M5-T135 packet) over the real registry returns ok=True, applicable==cited==the eleven, missing/invalid/unresolved all empty.
 - B5 PASS: reg.derive_applicable(packet) across all active directives returns exactly the eleven D-090 rows and nothing else; gate records G0 PASS, G2 PASS, G3 PASS, G4 PASS, with G2/G3/G4 all carrying one content identity (content_manifest_sha256 b25ce330…).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while ALL of the following hold: the 13 packet allowed-path files keep their frozen-head blob ids — MEASUREMENT_BASIS.md 1ef33e07, example-a json a4eb5b69 / md e87087b6, example-b json f92b7734 / md 33975647, example-c json e1ca5a1d / md d8c16fe1, measurement_basis_check.py 24b91e87, measurement_basis_fit.py f4641ae3, measurement_basis_lib.py d0536b27, measurement_basis_render.py f6d91afc, test_measurement_basis_examples.py 75d83c30, project-control/reports/M5-T135-producer-report.md 1c974e1a; everything under docs/reference-cases, services/api/app/rules and services/api/app/scenario unchanged; the 14 captures the record cites unchanged; and the eleven rows' text and their M5-T135 binding unchanged.
 - Tolerated later commits: commits touching only project-control/** and docs/DISCOVERY_BACKLOG.md; commits of M4-T036 that ADD or correct its own new capture files under docs/research/zr-snapshots/v1 and services/api/app/_zr_snapshots/v1 without changing any cited capture; and a merge of the integration branch that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None. No blocking defect found. Three non-blocking NOTES for the acceptance sweep (already tracked): the legacy "25 percent allowance" shorthand in the intro/section 7 (align to 0.60–0.75); T1 asserts presence not absence of a validation-contradicting sentence (G4-F2); and the "not captured yet (Article III, Chapter 3)" phrase will go stale once M4-T036's captures are read into the reference cases.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The owner's raw session transcript is not in the repo; I verified owner fragments against source-057-amendment.md (whose own header asserts a scripted, non-retyped capture with a raw-text SHA-256), not against the original transcript.
 - I did not re-fetch the live NYC zoning site; I verified each quote against the committed capture's verbatim_excerpt and its content_digest_sha256 only (the G3 reviewer reports an external site spot-check, which I treat as a claim).
 - Per my instructions I did NOT run tools/test_directive_compliance.py (hours-long) nor rerun CI; the authoritative evidence I reproduced is validate_directive_compliance.py --check (exit 0), the measurement_basis pytest (41 passed, exit 0) and the renderer --check ("measurement-basis check PASSED", exit 0). The full control-plane test suite and CI remain the orchestrator's/CI's responsibility.
END-OF-REPORT
```
