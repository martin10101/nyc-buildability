# M5-T134 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `3c0a1b648c130b3856f40a30cede225c167183df` (branch `task/wave7-wiring-reading-seal`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R240, R255, R257, R267, R268, R531.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08T02:51:34Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T134 (directive D-090, seven rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an automated verification, not a human or professional review. I produced none of the work and none of the records; every statement below I reproduced from the code, the registry, git objects, the focused tests, and my own offline drive of the adapter.

(1) HEAD VERIFIED
 - `git rev-parse HEAD` in /root/project/rv-w6-a = 3c0a1b648c130b3856f40a30cede225c167183df; working tree clean.
 - The reviewed material commit 25d95eb0 reaches the frozen head through only three ledger commits (9680977f, 2ae09d12, 3c0a1b64) that touch project-control/** alone; the 12 allowed-path blob ids at the frozen head equal those G4 recorded at 25d95eb0.

(2) ROWS
ROW D-090-R229 — PASS (this task's seam share)
 - A value the wiring lacks reaches the decision module as missing, never a zero/default: the adapter run_engine_and_result_ways forwards inputs.property_profile/prepared_outline/site_geometry verbatim, None included, with zero branching (result_way_engine_bridge.py:86-95).
 - My drive: profile=None -> every recorded column NOT_READ and all ways Withheld; outline=None -> reach street_lines empty, every way's to_value_state() carries no "value" (never a zero) — reproduced, matching tests test_s6/test_s2/test_s1.
 - STAYS OPEN: the "shown as not known on the website, drawings and PDF" half — this task emits nothing to a user; the row stays bound to M5-T127/128/129/130/131 for that.
ROW D-090-R240 — PASS (this task's seam share)
 - An input not given stays unanswered and only its dependents are held back: my drive with area=None gave large_lot.met=None and "not stated"; geometry=None gave reach=None with coverage/rear_yard Withheld (tests test_s5/test_s3).
 - No default fills a missing input: the added production lines contain no `or {}`/`or []`/`.get(`/`if not` on a fact (G4 CHECK 6, which I re-read in the diff; only `is None`/`is not None` guards present).
 - STAYS OPEN: the user-facing "results show not known / user not forced to answer" behaviour belongs to the emitting piece, not this wiring.
ROW D-090-R255 — PASS (this task's seam share)
 - A user's special-density statement is handed as a statement and enters no fact record: my drive with special_density_statement=True made legal_unit_limit_standard Conditional carrying a KIND_USER_STATEMENT condition, and no gathered fact mentions "density"; with None it was Withheld (test_s9).
 - The statement is a bare adapter argument, never written onto the profile or any Recorded fact (result_way_engine_bridge.py:93).
 - STAYS OPEN: the user-facing conditional labelling on the website is future emitting work.
ROW D-090-R257 — PASS (this task's seam share)
 - The two real area figures are compared and neither is chosen: my drive gave recorded 10,075 sq ft vs outline ~10,388 sq ft, agreement DISAGREES, floor-area ways Conditional (test_s1/test_s4).
 - With no recorded area the outline never substitutes: large_lot.met=None, large_lot statement "not stated", area_statement "never used in its place" (test_s5); outline absent -> AreaAgreement.COULD_NOT_COMPARE (test_s2).
 - STAYS OPEN: presenting the defensible-conditional / withheld area results to a user is not in this task.
ROW D-090-R267 — PASS (this task's seam share)
 - The adapter adds no judgement that could turn unchecked into confirmed: it is a pure pass-through (zero branching) and on the benchmark lot the ways equal the decision module's own benchmark set — coverage/rear-yard/setback/building-option/three unit limits Withheld, floor-area/heights Conditional (my drive, test_s1).
 - A missing profile yields all-Withheld, never a confirmed answer carrying a disclaimer (my drive, test_s6).
 - STAYS OPEN: "a disclaimer does not make it confirmed" as a user-visible presentation rule lives in the emitting piece.
ROW D-090-R268 — PASS (this task's seam share)
 - The three-way split survives the wiring unchanged: under a recorded C2-2 overlay the FLOOR_AREA family (OVERLAY_SUPPORT_ROWS supported=True) stays Conditional (far not withheld), while REAR_YARD (supported=False, zr_sections present) is Withheld as gap_kind "work_owed" (my drive, test_s7/test_s8).
 - An answer the condition cannot change stays visible and only unsupportable answers are withheld — reproduced, tied to the merged reference rows via result_way_bridge_overlay, not to new logic here.
 - STAYS OPEN: the user-facing rendering of visible/conditional/withheld answers is not emitted by this task.
ROW D-090-R531 — PASS
 - This task IS the allowed integration/wiring and exposes nothing: `git grep result_way` over services/api/app/api and apps/web/src returns nothing; run_engine_and_result_ways has no caller under services/api/app (only its own definition); no production switch is flipped (the diff only reads LIVE_SPATIAL_PROVIDER_ENABLED, default OFF).
 - The three prerequisite repairs are accepted in the ledger before this task was contracted (created 2026-10-08T01:34): M5-T133 (measurement-basis/worked example), M5-T132 (the two explanations), M4-T034 (law-text captures) all status=accepted, merged at the integration base 85500b94 (PR #466).
 - STAYS OPEN: the sequencing bar on approving/contracting the apartment estimator and on exposing results to a user governs future waves; this task neither approves that estimator nor emits results.

(3) BINDING B1–B5
 - B1 PASS: diff of D-090 requirements.json 85500b94 -> frozen head appends only "M5-T134" to applicability.task_ids of exactly the seven rows (and updates updated_at); no row `text` changed. Exactly seven rows carry M5-T134 at the frozen head, equal to the cited set.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json)=63cba9e9…cacf equals manifest.requirements_content_digest_sha256; manifest audit_log has the dated "applicability_bound" entry binding M5-T134 to R229/R240/R255/R257/R267/R268/R531.
 - B3 PASS: verification.json holds one M5-T134 row; applicable_requirement_ids == the seven; verifier=""; reviewed_sha/manifest null; all seven per-requirement states "pending" with empty evidence (correct pre-verdict state).
 - B4 PASS: reg.evaluate_task_refs(M5-T134 packet) over the real registry -> ok=True, applicable_ids==cited_ids==the seven, missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS: same call shows no uncited applicable requirement from any active directive (missing_ids empty; registry-level errors empty); `validate_directive_compliance.py --check` exits 0 (direct).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while ALL of: the twelve allowed-path files keep their frozen-head blob ids (study_inputs.py 5d81c672, study_live_geometry.py 74bd5c08, evaluator_inputs.py d77a1581, inputs.py 1fe8f5e2, result_way_engine_bridge.py f19212d4, test_study_geometry.py 381007b2, test_study_inputs_live.py 73602594, test_evaluator_inputs.py 5d69ec4e, test_result_way_engine_bridge.py b5aadf58, test_result_ways.py ad9bd424, test_wiring_emits_nothing.py 1c703813, report 6b6117e2); the committed fixture recorded_215_16_northern_journey.json, engine.py and the six decision-module files stay byte-identical (confirmed unchanged 85500b94->head); and the seven rows' text and their M5-T134 binding are unchanged.
 - Tolerated later commits: commits touching only project-control/** and docs/**; the two peer tasks' files (docs/reference-cases/R6B/**, services/api/tests/rules/reference_cases/**, tools/** for M4-T035 and M0-T188); and a merge of candidate/D-024-mrl-option-b that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The builder's out-of-repo mutation copies MP1–MP7 I did not re-execute (read-only, no write access); I reproduced the behaviours they pin by my own offline drive and by the committed red/mutation-covered tests.
 - The full api pytest suite and live CI at the frozen head I did not run (CI's job; running tools/test_directive_compliance.py is forbidden); I ran the three named focused suites (27 passed, exit 0), validate_directive_compliance.py --check (exit 0), and modularity_check.py --check (exit 0, no changed file flagged).
 - Windows/CRLF checkout behaviour and any live network/production path I could not exercise; no server route exists yet, so there is no end-to-end user path to drive.
END-OF-REPORT
```
