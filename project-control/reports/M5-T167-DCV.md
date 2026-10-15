# M5-T167 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `65d4ec9f1c20c55c0c0630db113959caa6d5338b` (branch `task/wave25-rear-yard-short-block`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R017, R026, R036, R037, R038, R039, R044, R061, R079, R136.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE row; all 10 PASS for this task's share and all five bindings hold. - Non-blocking observations (already reconciled by the reviewers/scope note 4, no action required for this verdict): NB-01 is at revision 6 (packet title anticipated rev 5) — expected branch movement after round 4 touched its code_paths; the objective's "net-shrink result_ways.py" wording actually describes result_way_bridge.py (525→444) and three_way_document.py (904→864), result_ways.py unchanged (scope note 4, G4 finding 2); six review advisories queued as DB-265 for M5-T170.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T03:11:50+00:00, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T167 (directive D-094, 10 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only
reproduction of primary evidence, NOT a human or professional review. I produced none of
the work or records; every matrix/map/gate/review below was treated as a claim to reproduce.

(1) HEAD VERIFIED
 - Frozen head read: 65d4ec9f1c20c55c0c0630db113959caa6d5338b on task/wave25-rear-yard-short-block in /root/project/w-wave20; working tree clean (git status --porcelain empty), so disk == frozen head.
 - 65d4ec9f adds only control-plane files over b5fd41a0 (gates G1-G5, evidence-map, reviews, report, state.json, task.json); no production file. b5fd41a0 is an ancestor of 65d4ec9f.
 - Production/report code is byte-identical between the review head d0611800, the owner-print commit 48b77e02 and 65d4ec9f (git diff --stat empty over services/api/app, packages/contracts/fixtures, apps/web/src), so the 48b77e02 print and the b5fd41a0 gates are faithful to the frozen head.
 - validate_directive_compliance.py --check exit 0 at the frozen head.

(2) ROWS (this task's SHARE; numeric order)

ROW D-094-R017 — PASS
 - Source anchor reproduced: source-001.md line 96/222 "Show applicable yard/setback areas only when their geometry and basis are established."
 - The regenerated real benchmark (recorded_215_16_northern_journey.json @65d4ec9f) carries NO rear_yard_100ft_line or corner_area geometry — no yard/setback area is drawn for the lot.
 - test_rear_yard_short_block.py::test_constraint_lines_carry_no_geometry_when_not_established asserts a not_known line carries "geometry" not in line (within-lot invariant).
 - Stays open: the synthetic fixture's over-extended 182.5 rear_yard_100ft_line is deliberately KEPT for M5-T175's clip test; its within-lot correction is routed to DB-263, not this task.

ROW D-094-R026 — PASS (partial row; this task's share met)
 - Source anchor reproduced: source-001.md line 101/231 (evidence page: compact section refs, actual source identifiers and dates, input basis, calculation, result).
 - This task's share = the rear-yard evidence: the rear_yard block names ZR 23-344 (a)/(b)/(c)(3) + ZR 12-10, and input_facts carry recorded_lot_area (administrative_record) and lot_outline_area (gis), each with source_title "NYC DCP MapPLUTO, version 26v2" and source_date 2026-09-30.
 - test_input_facts_equal_the_calculation_values_one_per_basis asserts each fact has source_title and source_date and a distinct basis; the result carries its conditions.
 - Stays open: the whole evidence-page worked-calculation redesign / rename is M0-T193 and M5-T164's share (also bound), not this task.

ROW D-094-R036 — PASS
 - Source anchor reproduced: source-001.md line 127/241 ("Evaluate these pathways against the actual zoning-lot and boundary evidence." "Update the diagram and conclusion together.").
 - Benchmark rear_yard checks evaluate (b) → not_known (short-dimension measurement basis is unresolved law, zoning lot unconfirmed) and (c)(3) → not_known (adjoining lot-line kinds not recorded); both cite ZR 23-344 + ZR 12-10.
 - Conclusion and drawing change together: page 8 now reads the conditional result while no rear-yard line is drawn (no geometry emitted); NB-03 is at revision 3, conclusion.research_status interpretation_awaiting_review.
 - Nothing stays open for this task's engine/record share; the on-site diagram beyond the no-draw state belongs to the overlay/scenario tasks.

ROW D-094-R037 — PASS
 - Source anchor reproduced: source-001.md line 127/242 (no unconditional zero rear yard from GIS; corner-radius not the only exception).
 - Benchmark combined row: state not_known, way "conditional", named conditions, ZR 23-344 linked — no unconditional "no rear yard".
 - test_no_unconditional_no_rear_yard_anywhere asserts every "no rear yard" is qualified by "within 100 feet"; test_corner_waiver_reach_describes_coverage_but_is_not_the_only_exception and test_checks_name_b_and_c3_besides_the_corner_waiver confirm (a) sits beside (b)/(c)(3).
 - Nothing stays open.

ROW D-094-R038 — PASS
 - Source anchor reproduced: source-001.md line 129/243 ("Fix the data path, not just the wording.").
 - Root cause recorded (return-diag-T167-synth.md + scope correction 3): the live results route never threaded street data, so the renderer read a 1.4.0 revision; page 8 kept "not yet checked" while page 6 dropped its line (reproduced on the dde8a181 print).
 - Round 4 fixes the data path: results_read.py threads street_data=inputs.street_data into the engine entry; first_option_results._not_checked gates page 6 on rear_yard_applied; test_study_live_geometry.py pins the corrected live path.
 - Stays open: with LIVE_SPATIAL_PROVIDER_ENABLED off (production default) the document stays 1.4.0 and BOTH pages say "not yet checked" consistently; full live-provider production wiring is a later item.

ROW D-094-R039 — PASS (this task's share met)
 - Source anchor reproduced: source-001.md line 134/244 (reconcile the three evidence issues; record each; regenerate from the corrected result source).
 - Rear-yard evidence issue recorded as awaiting specifically identified documents (a survey/deed showing this lot's and the adjoining lots' lot lines) in the rear_yard combined conditions and NB-03.
 - Report regenerated from the corrected source, not hand-edited: test_215_16_northern_journey.py states the fixture is "the byte-exact serialization of the engine output" (UPDATE_JOURNEY_FIXTURE=1) and asserts contract_version 1.5.0 with the three check states.
 - Stays open: the other two evidence issues (zoning lot, special density) are handled by their own tasks; M5-T167 only touches NB-01/NB-05 for code identity.

ROW D-094-R044 — PASS
 - Source anchor reproduced: source-001.md line 137/249 ("Do not invent geometry to fill a layout.").
 - block_frontage.py is pure geometry over an injected window and fails closed: one-sided window, missing frontage centreline, no window, no lot point → not known / empty (test_block_frontage.py tests), inventing nothing; ranges never collapsed (DB-260).
 - A not_known check carries no number (test_not_known_checks_carry_no_number; benchmark (b)/(c)(3) have no "inputs"); the real lot emits no rear-yard line geometry.
 - Nothing stays open for this task.

ROW D-094-R061 — PASS
 - Source anchor reproduced: source-001.md line 178/266 (facts not marked unknown solely because a feature is unfinished; unresolved site facts stay unresolved).
 - (b)/(c)(3) are not_known for named legal/site reasons (measurement basis = unresolved LAW; adjoining lot-line kinds and the zoning lot = unresolved SITE facts), not software incompleteness; (a) applies with its measured reach/angle.
 - test_c3_district_state_table: empty/missing district → not_known (never read as "no"); test_no_provenance_means_no_input_fact_invented. research_record_check.py --check PASS (exit 0), NB-03 interpretation_awaiting_review.
 - Nothing stays open.

ROW D-094-R079 — PASS
 - Source anchor reproduced: source-002-amendment.md line 41/69 (explicit applicability check of ZR 23-344(b) beside the 100-ft test; exemption not presented as established).
 - The engine adds an explicit (b) check: strict "< 230 feet" (229.99 applies / 230.00 / 230.01 not_applicable; test_short_dimension_state_table), measured from the short street, keyed to the zoning lot's front lot line; the real lot is not_known on every basis.
 - Exemption never presented as established: combined not_known/Conditional; NB-03 rev 3 (interpretation_awaiting_review, two independent readings); render_review_register.py --check PASS and the r6b register entry broadened to (a)/(b)/short dimension.
 - Nothing stays open for this task's engine/record/report share.

ROW D-094-R136 — PASS
 - Source anchor reproduced: source-019-amendment.md line (owner) "Page 8 still says the additional rear-yard rules have not been applied."
 - Old main (30762409) print page 8 item 4 = "Whether a rear yard is required is not yet checked ... have not been applied ... Unresolved"; frozen-head print (48b77e02, identical rendering code) = "A conditional reading of the short-block rule ZR 23-344(b) and the adjoining-side-line rule ZR 23-344(c)(3) ... Conditional" — the engine's own result, no unconditional "no rear yard".
 - Page 6 of the same print now shows the rear yard as Conditional (not "unchecked"); the two pages agree, driven from one rear_yard_analysis-is-not-None gate.
 - Stays open: this is satisfied on the owner's PREVIEW deliverable (recorded street window); in production with the provider flag off the report stays a consistent 1.4.0 "not yet checked" until live wiring is enabled.

(3) BINDING B1–B5
 - B1 PASS: each of the 10 rows has "M5-T167" in applicability.task_ids at the frozen head and absent at base main 30762409; all 10 row texts are byte-identical between base and head (no row text changed by this task). Contract commit d006e2b2 / audit_log entry 2026-10-14T19:36:21 records the applicability_bound.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = 86a96a7575a950f6c41a22100b7f15d13a0173a39ca45c8e40c4834cba05662d, equal to manifest requirements_content_digest_sha256.
 - B3 PASS: verification.json has exactly one M5-T167 row, applicable_requirement_ids = the 10 ids, every requirement state "pending", verifier "" (producer backend-engineer).
 - B4 PASS: reg.evaluate_task_refs(packet) → ok True, applicable_ids == cited_ids (the 10), missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: same evaluate_task_refs shows no other active-directive requirement applies to this task uncited (missing_ids empty across the registry).
 - Gates PASS at one content identity: G0 PASS (0ca549ab) and G1 (data-contract-verifier), G2 (orchestrator), G3 (code-reviewer), G4 (qa-engineer), G5 (security-reviewer) all PASS with reviewed_sha b5fd41a0; reviews record shows no REQUIRED corrections (all advisories = backlog DB-265); CI run 38672990884 at b5fd41a0 completed success, 21/21 jobs.
 - Prohibited actions: none. M5-T167 is in active_tasks, NOT in accepted_tasks (407 accepted); frozen head is NOT an ancestor of origin/main (main still 30762409); no PR exists for the branch; verification.json M5-T167 row is pending/unverified. Nothing merged, accepted, deployed, installed, purchased or closed.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while this blob-level predicate holds: every file in the M5-T167 packet allowed_paths keeps its current blob id at the stamping head, AND the 10 rows' text plus their M5-T167 applicability.task_ids binding are unchanged (requirements_content_digest unchanged).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports, other tasks' directive bindings, new rows appended to D-094, and ledger state — plus this task's own acceptance records (its verification.json rows, gate records, accept state), and a merge of the main line that changes none of the predicate's files. Any of these alone does not void the stamp.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE row; all 10 PASS for this task's share and all five bindings hold.
 - Non-blocking observations (already reconciled by the reviewers/scope note 4, no action required for this verdict): NB-01 is at revision 6 (packet title anticipated rev 5) — expected branch movement after round 4 touched its code_paths; the objective's "net-shrink result_ways.py" wording actually describes result_way_bridge.py (525→444) and three_way_document.py (904→864), result_ways.py unchanged (scope note 4, G4 finding 2); six review advisories queued as DB-265 for M5-T170.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-run the whole services/api pytest suite or the web/e2e browser suites (forbidden by brief and ports 3000/3001/8000 off-limits); I relied on CI run 38672990884 (21/21 success at b5fd41a0) plus the validator and the focused source/test reads.
 - I did not regenerate the PDF myself (no server/port); I read the committed print HTML at 48b77e02 and proved its rendering code is byte-identical to the frozen head instead.
 - The legal correctness of the ZR 23-344(b)/(c)(3) interpretation is not something I verify — it ships as a labelled unreviewed draft (ADR-007), read independently by two AI helpers in the R6B reference case, no human verdict; I verified the engine matches those settled readings, not the underlying law.
 - I did not recompute all 13 NB-01 code_identity digests; I confirmed research_record_check.py --check exit 0, NB-03 rev 3 / interpretation_awaiting_review, and the register checker PASS, and relied on the data-contract-verifier's recompute for the NB-01 digit-level match.
END-OF-REPORT
````
