# M5-T146 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c10ac73f095b503d99df5420e43ed51f0e59822f` (branch `task/wave19-first-option-wiring`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R147, R192, R239, R255, R256, R257, R267, R322, R374, R379, R509, R526, R540, R541, R543, R544, R556, R570, R650, R688, R700, R707, R773.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. (Observation, not a defect: the SVG/DXF snapshots are NOT byte-identical to the base — each changed by 22 lines — because the W14(c) correction replaced the false "below the minimum base height / rear yard" note with the true "no placement is worked" note and updated the coverage note; the lot_outline geometry is byte-identical and no new footprint/floor-plate geometry was drawn. This text-only change is correct and was reviewed at the delta head; any residual "snapshots byte-identical/unchanged" phrasing in the first-round/part-E summaries is imprecise but not a compliance failure.)
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-09 23:29 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T146 (directive D-090, 23 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only machine verification, NOT a human or professional/legal review. I produced none of the work or records. I verified each item from primary evidence (the committed benchmark document, the contract schema, the tests and what they assert, the register pages/JSON, the git objects and the control-plane records), treating every report/map/gate record and my brief as unverified claims.

(1) HEAD VERIFIED
 - Frozen head is c10ac73f095b503d99df5420e43ed51f0e59822f on branch task/wave19-first-option-wiring. My copy /root/project/rv-w6-a is pinned at 7cf94e09 and the read-only guard blocks checkout, so (per my brief) I read the frozen head through /root/project/w-wave19, which `git status --porcelain` shows CLEAN and `git rev-parse HEAD` shows AT c10ac73f — its working tree equals the frozen head.
 - Code identity reviewed-head → frozen-head: `git diff --name-status f237d0d7..c10ac73f` shows ONLY project-control/ files (gates, reports, evidence maps, state.json, the two task JSONs). No packages/contracts, services/api, docs/zoning-rule-review, apps/web, render.yaml, .github or tools file changed, so the CI green and the G2/G3/G4 records pinned at f237d0d7/4a7e2089 carry to the frozen head.
 - The directive validator `python tools/validate_directive_compliance.py --check` ran once against the frozen head with a DIRECT exit code = 0.

(2) ROWS

ROW D-090-R147 — PASS
 - This task's share: the benchmark figures follow the law and the recorded area. In packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json the floor-area allowance is 20,150 = FAR 2.0 × the recorded lot area 10,075 (not the 10,387.99 outline), and building B's bound is 8,060 = 0.80 × 10,075 (fit_note), both re-derived by me.
 - coverage is read by portion (ZR 23-362 / ZR 12-10) and withheld with no square-foot figure; the estimate uses the building's own floor area; the units follow one formula — none of the competitor's E1-E20 patterns is reproduced here.
 - The competitor error-guard assessment doc (docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md) is NOT in the base→frozen name-only diff, so the error-guard table is unchanged by this task.
 - Stays open for later work: the full E1-E20 guard assessment is carried by D-090-BOOTSTRAP and M5-T145, not by this wiring task.

ROW D-090-R192 — PASS
 - No footprint and no floor plate is drawn for the benchmark lot: in the regenerated document geometry.floor_plates and geometry.envelope are not_available, and the SVG snapshot's only drawn geometry is the unchanged lot_outline path (M135.24 370.18 L380.76 370.18 L380.76 133.82 L135.24 133.82 Z, data-source="/geometry/lot_outline") — the base→frozen SVG/DXF diff adds NO new footprint/floor-plate geometry.
 - The drawings follow the document: the only snapshot change is annotation text — the floor_plates note now reads "No floor plate is drawn: no placement on the lot is worked for any building…" pointing to building_alternatives and buildings_not_worked, and the coverage note now gives the areas-disagree reason; the false "below the minimum base height" text is gone from both the SVG and DXF.
 - test_w14c_floor_plates_reason_is_the_true_placement_reason_on_the_benchmark asserts this reason and the absence of "minimum base height"/"rear yard"; it is in the suite I ran (260 passed).
 - Stays open for later work: drawing a worked placement/footprint/floor plate waits for the placement task; the lot_outline is the one parcel-geometry conclusion drawn here.

ROW D-090-R239 — PASS
 - The two area figures (recorded 10,075 vs tax-map outline 10,387.99) and how each is used were decided before calculation (work order docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md §6, ruling W1): the outline area is a drawing measure, never used in a zoning calculation; only the recorded area feeds the allowance and the bound.
 - In the committed document coverage_by_portion.status = "withheld", gap_kind "missing_information", reason names the disagreement, resolved_by a survey/deed; no footprint_sqft is present.
 - test_w13_areas_disagree_benchmark_blocks_unchanged_through_the_threaded_emitter asserts coverage_by_portion is byte-equal to the committed document with no footprint_sqft; it passed in my run.
 - Stays open for later work: the owner's A1 question (show the footprint conditional on the outline instead) is recorded open; the rule holds until answered.

ROW D-090-R255 — PASS
 - Facts/eligibility come from evidence; the only user assumption used (the entered floor-to-floor height) feeds only a result labelled conditional. Building B's way is "conditional" with a contradicted_record condition ("If the recorded lot area of 10,075 sq ft is confirmed…") — never a stored verified fact.
 - test_m5t146_live_route_entered_floor_to_floor_works_building_b_at_that_height (tests/api/test_results_read_api.py) posts floor_to_floor_ft=14 and asserts every schedule row is 14 ft (never silently 10) and building B is listed as conditional; it passed.
 - Stays open for later work: the broad "all facts from evidence" obligation spans many M5 tasks; this task satisfies it for the first-building wiring.

ROW D-090-R256 — PASS
 - No hidden defaults: the document shows the design choice values with a statement — scope.assumptions carries floor_to_floor_ft=10 ("A 10-foot floor-to-floor height is used as the default"), and the estimate shows share_low/high and apartment_size_sqft.
 - The live-route test proves the shown height is used when entered (14 → 14-ft storeys), i.e. the applied value is the shown value.
 - Stays open for later work: letting the user CHANGE floor height / share / size on the screen is work owed (ruling W7, backlog DB-213 a), recorded in the estimate register page.

ROW D-090-R257 — PASS
 - Where the two areas disagree no settled footprint is shown: coverage_by_portion is withheld with reason, gap_kind (missing_information) and resolved_by; neither area is chosen automatically.
 - Building A is listed in buildings_not_worked with the SAME reason/kind/resolver as the withheld coverage (recorded_215_16…json buildings_not_worked[0]).
 - test_w14_s27_building_b_listed_building_a_not_worked_at_10_and_14_ft asserts building A appears only in buildings_not_worked with gap_kind missing_information; it passed.
 - Stays open for later work: the conditional-on-outline alternative (A1) is the owner's open decision.

ROW D-090-R267 — PASS
 - "Not checked" never becomes "confirmed": building B is "conditional" (never settled), carries not_checked = [rear yard beyond the corner, where the plan sits on the lot, the street wall, parking/loading/bicycle], and the fit_note says it "checks the plan against coverage only".
 - test_w14_no_not_worked_reason_claims_feasible_or_preferred asserts none of {"feasible","complies","preferred","optimal"} appears in either list at 10/14/16/25 ft; it passed. The schema building_alternative $def also states nothing is called feasible/complies/confirmed/validated.
 - Stays open for later work: none specific to this row; the no-confirmation rule continues for later options.

ROW D-090-R322 — PASS
 - Missing facts stay unknown / conditional and unfinished features stay work owed: building A is buildings_not_worked gap_kind "missing_information" (areas disagree); building B at 16 ft and 25 ft is "work_owed" (plan above the bound / base above the maximum).
 - test_w14_s25_sixteen_ft_no_building_worked_both_reasons_given and test_w14_s26_twenty_five_ft_building_b_base_passes_maximum assert these gap kinds and reasons; both passed.
 - Stays open for later work: single-floor-height / above-base-storey handling is recorded as work owed (known_limits); it is reported not-worked, not hidden.

ROW D-090-R374 — PASS
 - No human verdict is entered: I walked services/api/app/rules/review_register/register.json and found 29 human_review nodes, ZERO with a non-null decision.
 - The rendered estimate page (docs/zoning-rule-review/calculations/calc-preliminary-apartment-estimate.md) states "Current verdict: Not reviewed" and "A verdict is a named human reviewer's own answer; agent reviews are never recorded here."
 - Stays open for later work: human review of the rules remains advisory/ADR-007; this task entered none, as required.

ROW D-090-R379 — PASS
 - The standing instruction is in the main instruction file at the frozen head: CLAUDE.md line 20 "Zoning-rule review register (D-090-R379): every session that adds or changes zoning-rule behavior must update the register … as part of the same change. No session enters a human verdict."
 - The register was updated inside this task's own commits (a7764239, b219f8fd, 4fe56698, 5dba465c) and `render_review_register.py --check` returns exit 0 at the frozen head ("register check PASSED").
 - Stays open for later work: the instruction row itself is standing and unchanged by this task (correctly); each future rule/calculation change must keep updating the register.

ROW D-090-R509 — PASS
 - The estimate starts from the proposed building's own residential floor area, not the legal maximum: capacity_estimate.floor_area_sqft = 20,150 (building B's own total_floor_area_sqft), quotient_low 17.27 = 20,150×0.60/700 and quotient_high 21.59 = 20,150×0.75/700 (re-derived).
 - The maximum permitted floor area is kept separate in floor_area_allowance; the legal_unit_limit_standard is a separate withheld result.
 - Stays open for later work: using a detailed-layout measured area directly applies only once layouts exist (not in this slice).

ROW D-090-R526 — PASS
 - No option is presented as feasible while parking/loading/bicycle applicability is unresolved: building B's not_checked list includes "Parking, loading and bicycle requirements", and nothing in the document is called feasible.
 - test_w14_no_not_worked_reason_claims_feasible_or_preferred asserts the banned words are absent at all tested heights; it passed.
 - Stays open for later work: the report section with the actual parking/loading/bicycle counts "can come later" (owner) and is not built here.

ROW D-090-R540 — PASS
 - The efficiency share travels with the estimate as a 0.60–0.75 range: capacity_estimate.share_low = 0.6, share_high = 0.75 in the committed document; the register estimate page labels "the 0.60-0.75 efficiency share … a preliminary assumption chosen by the owner, not law."
 - Stays open for later work: showing it editable on the screen is work owed (ruling W7 / DB-213 a), stated in the estimate page.

ROW D-090-R541 — PASS
 - The apartment size travels as a chosen starting value on the HPD basis: capacity_estimate.apartment_size_sqft = 700.0; the register estimate page says "the 700 sq ft apartment size … a preliminary assumption chosen by the owner" and "measured as HPD measures an apartment" (measurement-basis record linked).
 - Stays open for later work: on-screen editing of the size is work owed (ruling W7 / DB-213 a).

ROW D-090-R543 — PASS
 - The schema admits exactly the two owner labels: packages/contracts/schemas/v1/results.schema.json capacity_estimate is a oneOf of const "Preliminary capacity estimate" (building has floors and a shape) and const "Not known". Building B's estimate label in the document is exactly "Preliminary capacity estimate".
 - I validated the invalid fixture building_alternative_estimate_label_wrong.json against the schema with a local registry — it is REJECTED; the three valid 1.4.0 fixtures validate.
 - Stays open for later work: none — the two labels are enforced by the contract.

ROW D-090-R544 — PASS
 - The estimate uses the building's accommodated floor area (20,150), and the legal ceiling is a separate figure: legal_unit_limit_standard.way = "withheld" with no number (the 29-unit figure is computed but not shown).
 - The register estimate page states the estimate "is kept apart from the legal dwelling-unit limit."
 - Stays open for later work: showing the legal unit limit as a settled or conditional figure is withheld work owed (special-density evidence), separate from the estimate.

ROW D-090-R556 — PASS
 - A withheld result shows no older or substitute value: coverage_by_portion is withheld with no footprint_sqft; the older max_lot_coverage value state and geometry.envelope carry the same reason/kind/resolver (reconciled, ruling W11 a); building_option/unit_estimate/floor_stack are not_available and point to the lists, claiming nothing else.
 - I validated coverage_by_portion_withheld_with_number.json against the schema — it is REJECTED (a withheld result may carry no number).
 - Stays open for later work: the website reader's first-value fallback fix is M5-T147's share; the document/server side here emits withheld correctly.

ROW D-090-R570 — PASS
 - Withheld values stay withheld everywhere this task carries them: the document (coverage, building A) carries no number; buildings_not_worked and coverage_by_portion-withheld carry NO number field (schema $defs have additionalProperties:false); the SVG/DXF note layers carry text reasons only, no footprint figure.
 - I validated buildings_not_worked_entry_with_number.json and coverage_by_portion_withheld_with_number.json against the schema — both REJECTED; the valid benchmark validates.
 - Stays open for later work: the on-screen (apps/web) withheld rendering is M5-T147's share.

ROW D-090-R650 — PASS
 - Each remaining blocker names its kind: coverage_by_portion and building A are "missing_information" (a missing property fact — areas disagree); building B at 16/25 ft is "work_owed" (code not built yet for one floor height / above-base storeys); the legal unit limit is "work_owed".
 - test_w14_s25/s26/s27 (emit and live-route) assert these gap_kind values; they passed. The kinds are true to the decided state.
 - Stays open for later work: kinds for building states not yet decided (e.g. the agree-case on a real lot) are carried by M5-T145/BOOTSTRAP.

ROW D-090-R688 — PASS
 - The first-building comparison runs through the complete calculation and keeps the preliminary estimate SEPARATE from the applicable legal unit limit: building B's footprint/floor schedule/total/estimate trace to docs/reference-cases step-p6-worked#real-building-b/#real-estimate-b, while legal_unit_limit_standard is a separate withheld result.
 - test_w13_areas_agree_through_emitter_shows_footprint_and_building_a checks the made-up agree-lot against #made-up-building-a through the emitter; it passed.
 - Stays open for later work: a live-route agree-case comparison awaits a recorded lot whose areas agree (disclosed in known_limits).

ROW D-090-R700 — PASS
 - The apartment-size and efficiency assumptions stay labelled preliminary: the document carries share 0.60–0.75 and size 700 inside capacity_estimate, and the register estimate page labels both "a preliminary assumption chosen by the owner, not law."
 - Nothing presents them as law, measured, typical or validated (register page and schema estimate $def wording "an unvalidated share range … a chosen starting apartment size").
 - Stays open for later work: making them editable on screen is work owed (W7).

ROW D-090-R707 — PASS
 - The register updates arrived inside this task's own commits (a7764239, b219f8fd, 4fe56698, 5dba465c) and were reviewed with the task (G3 check 6), not in a separate project.
 - `render_review_register.py --check` exits 0 at the frozen head and HISTORY.md shows 0 removed lines base→frozen (append-only).
 - Stays open for later work: none — the register continues to be updated within each future rule/calculation task's scope.

ROW D-090-R773 — PASS
 - The task was cut into parts on separate files built side by side: project-control/reports/WAVE19-2026-10-09-concurrency-record.md records part A alone, then the parallel window {part B services/api/app/scenario/three_answers, part D1 services/api/app/rules/review_register, part C apps/web of M5-T147} on disjoint folders, then D2/E alone.
 - The record states the owner's limits are kept (≤3 builders / ≤4 reviewers, no shared file, heavy runs and merges one at a time) and that run times are recorded afterward; the packet path_notes carry the same disjoint-folder proof.
 - Stays open for later work: the row seeks a standing way of working for future tasks; this task demonstrates and records it.

(3) BINDING B1–B5
 - B1 PASS — comparing requirements.json at base 067592499 vs frozen c10ac73f: all 23 rows gained "M5-T146" in applicability.task_ids (rows shared with the sibling screen task also gained "M5-T147"); ZERO rows had any text or classification change.
 - B2 PASS — directive_registry.sha256_text_artifact(requirements.json) = 55780617ad8e6a50611bb908ccab0b3677981745e17d93c39a666cc324d487b0, equal to the manifest's requirements_content_digest_sha256.
 - B3 PASS — verification.json has exactly ONE M5-T146 row with applicable_requirement_ids = the 23 cited; each requirement entry is {"state":"pending","evidence":[],"reviewed_sha":null}; the row verifier is "" and every per-requirement verifier is null.
 - B4 PASS — reg.evaluate_task_refs(packet) returns ok=True with applicable_ids == cited_ids (23 each), missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS — scanning every directive's requirements.json, exactly 23 rows apply to M5-T146 and they equal the cited set (no apply-but-uncited, none cited-but-not-applying). GATES: G0 PASS (readiness, re-recorded at each scope correction); G2 (reviewer orchestrator, role self_check) / G3 (data-contract-verifier) / G4 (qa-engineer) all result PASS, all at ONE content_manifest_sha256 = aed9a53238588bf2396ec355b2d1b153a586c9d297d54e5b107383fad2b91b77, reviewed_sha 4a7e2089 (code-identical to the CI head f237d0d7), recorded 23:15 UTC after CI run 38001788978 completed success at 23:02. validate_directive_compliance.py --check exit 0.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while the blob ids are unchanged for services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, apps/web/src, apps/web/e2e, render.yaml, .github, tools, docs/research, docs/measurement-basis and this task's project-control/reports, AND the 23 rows' text and their binding (applicability append, digest, verification row) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other tasks on this branch (e.g. M5-T147, M0-T189), and a main-line merge that changes none of the predicate files. I confirmed f237d0d7→c10ac73f already satisfies this (project-control-only), so the frozen head is within the condition relative to the reviewed/CI head.

(5) REQUIRED CORRECTIONS
 - None. (Observation, not a defect: the SVG/DXF snapshots are NOT byte-identical to the base — each changed by 22 lines — because the W14(c) correction replaced the false "below the minimum base height / rear yard" note with the true "no placement is worked" note and updated the coverage note; the lot_outline geometry is byte-identical and no new footprint/floor-plate geometry was drawn. This text-only change is correct and was reviewed at the delta head; any residual "snapshots byte-identical/unchanged" phrasing in the first-round/part-E summaries is imprecise but not a compliance failure.)

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - CI run status: I did not re-query gh or re-run any CI job (forbidden / read-only). I relied on the recorded CI run 38001788978 (21/21 success) at f237d0d7 and independently proved the frozen head's code is identical to that head (diff is project-control-only), plus my own focused reruns.
 - Reruns I DID perform at the frozen head (via /root/project/w-wave19 with the lanes venv): the four focused suites (tests/scenario/three_answers/test_three_answers_three_way_emit.py, tests/api/test_results_read_api.py, tests/rules/test_zoning_rule_review_register.py, test_zoning_rule_review_register_calculations.py) = 260 passed; render_review_register.py --check = exit 0; the directive validator --check = exit 0; and in-memory jsonschema validation of the 3 valid + 6 invalid fixtures.
 - I did NOT run the full services/api pytest suite, tests/drawings, tests/cad, or tools/test_directive_compliance.py (forbidden by my brief); the drawings/cad suites and the browser e2e (apps/web/e2e, ports held) were covered by CI and by the G4/walkthrough reviewers, not re-executed by me — I inspected the SVG/DXF snapshot diffs directly instead.
 - The sibling screen task M5-T147 (apps/web) is NOT within my task's verification; for rows shared with it (R256, R540, R541, R556, R570, R543, R544, R526, R688, R700, R509) I verified only this task's document/server/register share and stated the screen side as M5-T147's share.

This is an AI-agent verification, not a human or professional/legal review.
END-OF-REPORT
```
