# M4-T035 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `109d48c05749210a4b39b31ed57a614ee5270aac` (branch `task/wave7-wiring-reading-seal`, review copy `/root/project/rv-w6-b`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R291, R513, R516, R526, R548.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08T03:08:36Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M4-T035 (directive D-090, five rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier), read-only; this is an automated agent review, not a human or professional/legal review.

(1) HEAD VERIFIED
 - `git rev-parse HEAD` in /root/project/rv-w6-b = 109d48c05749210a4b39b31ed57a614ee5270aac, the frozen head; working tree clean.
 - HEAD commit is "M4-T035: gates G3 and G4 PASS recorded at 0784ce7f"; the one material commit is e6e9ac79 (parent = claim head b416cf0d); task status is awaiting_gate (95%), no PR, integration branch at 85500b94.
 - Focused harness at this head: `pytest tests/rules/reference_cases` = 72 passed, exit 0; `validate_directive_compliance.py --check` = exit 0 (silent success). I did not run test_directive_compliance.py (forbidden) or the full api suite.

(2) ROWS
ROW D-090-R291 — PASS
 - Independently worked examples are saved as files a test reads: docs/reference-cases/R6B/cases/step-p5-worked.json (28 rows) plus provenance/return-independent-hand-calculation-11.md and -12.md; the two saved readings are byte-identical to the orchestrator-received returns return-reading-P5-1/2.txt except a 6-line header (diff shows only "0a1,6").
 - The both-must-agree rule is enforced by tests I reproduced: test_the_two_step_p5_readings_are_present_unchanged (digest-pins the readings), test_a_step_p5_value_where_the_readings_differ_is_refused and test_a_step_p5_unsettled_row_given_a_value_is_refused (72 passed).
 - Conflicting/missing items are named, not chosen: rows made-up-mixed-commercial-far, made-up-mixed-whole-building-max, zr-23-24-reach and benchmark-rear-yard-23-342-23-344 are not_known, and sections-and-facts-not-had lists what both readers lacked.
 - Open for later: the wider "check the R6B answers / resolve missing rules" step and the still-missing texts (Article III Ch 3, 25-222, Use-Group tables, LL154) remain work owed.

ROW D-090-R513 — PASS
 - The shared-floor-area provision is read from the captured text of ZR 35-31 (content_digest 65e29c68…, digest match + quote present in verbatim_excerpt) and ZR 23-20 (0685a2e4…, match), stating the base as "total floor area of the zoning lot LESS any shared floor area" — row shared-floor-area-rule.
 - It is worked on one mixed building (row made-up-mixed-shared-attribution): base 20,500−400=20,100; 400 split 83.58 commercial / 316.42 residential; both readings reach these exact figures on the same basis (reading 11 L44-49; reading 12 L40-46).
 - It frames allocation as a required calculation and uses not_known where exclusive-use areas/commercial FAR are missing, consistent with "result stays unknown/conditional".
 - Open for later: wiring the allocation into the live estimate as a non-switchable step and the measurement-basis follow-up (DB-184) are not done here.

ROW D-090-R516 — PASS
 - The specific eligibility of both energy definitions is stated from the captures: fully-electrified-building-definition (a building EXISTING on December 6, 2023 + LL154; digest 2ea4afe2… match) and ultra-low-energy-building-definition (LL154, net-zero ≤3 stories or ≥15% better, registered-design-professional verification, inspection/commissioning/airtightness plans, final-CO report; digest 8a1d6418… match, quote present).
 - A user's statement supports only a conditional result: proposed-building-energy-eligibility records fully-electrified = NO for a new building, ultra-low-energy = provisional at plan approval; both readings agree (reading 11 L130-131; reading 12 L151-152).
 - Open for later: the row's exterior/qualifying-WALL exclusion is explicitly NOT read in this task, and the measurement-basis record stays owed (stated in the case and evidence map).

ROW D-090-R526 — PASS
 - Applicability of parking, loading and bicycle requirements is read for each kind of building BEFORE any result depends on it: parking-loading-bicycle-sections (14 sections quoted) plus seven option rows; I confirmed two kinds against both readings — standard residences parking REQUIRED (25-221, amount not known) and rooming units parking NOT REQUIRED (25-221 after 2016-03-22; digest 21327ea6… match).
 - Nothing is presented as feasible: parking-loading-bicycle-line-per-option states a line may say "required/not yet checked" and MAY NOT give a count, declare feasibility, or turn law into preference; the task shows nothing to a user (reading-only, forbidden_paths bar engine/result/display).
 - Open for later: the option-comparison/website line and the report section with counts (DB-180) and the missing texts (25-222, Use-Group tables) are later pieces.

ROW D-090-R548 — PASS
 - This is R526 in the owner's own words and is served by the same rows; applicability is read per building kind and parking-loading-bicycle-line-per-option explicitly forbids calling any option feasible on these readings.
 - No option is presented as feasible and no count is stated anywhere in the case (every row carries "It says nothing complies"); this task changes no result and no display.
 - Open for later: the display line on every option and the counts belong to later pieces (DB-180).

(3) BINDING B1–B5
B1 — PASS: diff 85500b94→109d48c0 of D-090 requirements.json appends exactly "M4-T035" to applicability.task_ids of R291, R513, R516, R526, R548, with text_same=True and no other field change for each; the other 8 changed rows belong to peer task M5-T134.
B2 — PASS: directive_registry.sha256_text_artifact(requirements.json)=63cba9e9…eccacf equals the manifest requirements_content_digest_sha256; the manifest audit_log has the 2026-10-08T01:34:59 "applicability_bound" entry for M4-T035 to the five rows with digest resync.
B3 — PASS: verification.json has exactly one M4-T035 row; applicable_requirement_ids = the five; each requirement state "pending" with empty evidence; verifier "" and reviewed_sha null.
B4 — PASS: reg.evaluate_task_refs(M4-T035 packet) = ok:true, applicable_ids == cited_ids == the five, missing_ids/invalid_refs/unresolved all empty.
B5 — PASS: reg.derive_applicable(packet) across ALL active directives returns exactly {R291,R513,R516,R526,R548} with no unresolved reasons — nothing else applies uncited. Scope correction: the single scope_corrections entry is one forced line in test_r6b_reference_cases.py (frozen CASE_IDS tuple gains "step-p5-worked"); the diff confirms it changes no allowed path, gate, reviewer, scenario or row (the step-p4 edit only adds superseded_by+changelog, no value/kind change).

(4) CARRY-FORWARD CONDITION
This PASS may be stamped at a later head WITHOUT re-review while all of: every file under docs/reference-cases/R6B/ and services/api/tests/rules/reference_cases/ and project-control/reports/M4-T035-producer-report.md keeps the exact git blob id it has at 109d48c0 (byte-identical); the capture folder docs/research/zr-snapshots/v1/, the rule files services/api/app/**, the review register docs/zoning-rule-review/** and docs/measurement-basis/** are unchanged; and the text of the five rows and their applicability binding to M4-T035 are unchanged. Tolerated later commits: commits touching only project-control/** and docs/DISCOVERY_BACKLOG.md; the peer task's commits under tools/; and a merge of the integration branch that changes none of the predicate's files. Any change to a predicate blob voids the stamp and requires re-review.

(5) REQUIRED CORRECTIONS
None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Capture-equals-official-source: I am offline/read-only and cannot re-fetch the ZR pages; I matched each sampled quote to its pinned capture's verbatim_excerpt and content_digest_sha256, but capture↔official equivalence rests on the M4-T033/M4-T034 capture reviews (the G4 data-contract-verifier re-fetched 9 of 13 quotes and likewise could not open the four large ZR 12-10 energy/FAR quotes).
 - Reader independence: the sealed-folder isolation and tool-log audit are orchestrator attestations; I verified only that the two saved returns are the received returns verbatim, not that the readers had no repo/web access.
 - I did not re-derive the benchmark rear-yard geometry (144.60 ft, 89.7°) from the raw outline; I confirmed both readings record it and that the row withholds the beyond-100-ft part as not_known.
 - I ran the named reference_cases suite (72 passed) and the validator (exit 0) only; the full api pytest "once at the wave's final candidate" is the orchestrator's run, not reproduced here.
END-OF-REPORT
```
