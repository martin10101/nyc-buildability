# M5-T126 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `edcddf719dbedbae51162c490f42e57258bfdeb5` (branch `task/wave1-measurement-basis-p2-captures-reference-cases`, pull request 459, review copy `/root/project/rv-w1-1007`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R357, R358, R359, R387, R388, R389, R392, R396, R397, R407, R413, R428, R430, R431, R432, R433, R434, R435, R436, R437 (20 rows).

## Verdict: PASS for all 20 rows. No required correction blocks acceptance.

- **Four rows are met for this task's share only, and the verifier says what is left.** R359 and R389 ask that the owner be shown things: the record prepares the content; showing it to the owner happens after acceptance. R359's harness asks for the last part "as a worked table" of how the count moves: the record gives directions only and computes no count, so that table is still owed at the owner update. R387 and R428: the record sets out the basis and presents no count as accurate; whether the basis is resolved is the owner's to say. All four rows stay open in the registry.
- The tests of the task, run by the verifier: exit 0 (27 passed).
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head: the task's allowed paths, the eight law captures the record quotes, and the twenty rows, the manifest and sources 042, 043 and 044 unchanged.
- What it could not check itself: the HPD Design Guidelines at the official address (no network for it). The independent code reviewer did fetch that file on 2026-10-07 and found its digest equal to the recorded one and the quotation, edition and applicability as the record states (`project-control/reports/M5-T126-G3G4.md`). It did not run the registry validator (the second verifier ran it once at the same head: exit 0) or the full api suite (the orchestrator's run at `c2f72cdb`: 8108 passed, 8 skipped).
- Read by the orchestrator on 2026-10-07 at 06:17 UTC: the pull request's check list on `edcddf71` showed 46 checks, all a completed success.

How the return arrived (2026-10-07, 06:16 UTC): as one message holding all four parts and the closing line. It is reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, line 1644; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 4

ROLE: Independent directive-compliance verifier (G3/G4 read-only pass) for task M5-T126, directive D-090. I produced none of this work or its records. I am an AI agent; this is an automated verification, NOT a human or professional/legal review.
FROZEN HEAD: edcddf719dbedbae51162c490f42e57258bfdeb5 (confirmed via git rev-parse in the review copy /root/project/rv-w1-1007; working tree clean).
BINDING CONFIRMED: directive_registry.load_registry(...).evaluate_task_refs(M5-T126) returns ok=True, missing_ids=[], invalid_refs=[]; applicable_ids == cited_ids == the twenty rows (R357,R358,R359,R387,R388,R389,R392,R396,R397,R407,R413,R428,R430,R431,R432,R433,R434,R435,R436,R437).
HARNESS: `python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis` from services/api (PYTHONDONTWRITEBYTECODE=1, venv python) => 27 passed in 0.36s, DIRECT EXIT CODE 0.
VERDICT: PASS (all twenty rows satisfied for this task's share; no blocking correction).

CARRY-FORWARD CONDITION (stated up front). My twenty verdicts may be re-stamped at a later head WITHOUT re-review while ALL of these hold as a blob-level predicate:
(a) every file under this task's allowed_paths is byte-identical to the frozen head — docs/measurement-basis/** , services/api/tests/scenario/measurement_basis/** , project-control/reports/M5-T126-producer-report.md;
(b) the eight cited ZR captures under docs/research/zr-snapshots/v1/ (zr-12-10-floor-area, zr-12-10-qualifying-exterior-wall-thickness, zr-23-23, zr-23-231, zr-23-232, zr-23-233, zr-23-234, zr-23-52) are unchanged (same content_digest_sha256);
(c) the twenty requirement rows in D-090 requirements.json, the D-090 manifest, and sources 042/043/044 are unchanged.
I TOLERATE, with no re-review: later commits that touch only project-control/** (gate records, state, task files, reports, verification rows) and/or at most one line of docs/DISCOVERY_BACKLOG.md; the other two tasks' records on this branch (M4-T026 at services/api/app/_zr_snapshots/** and their docs/project-control files; M4-T027); and a merge of the integration branch that introduces no change to (a)-(c). Any change to (a), (b) or (c) voids the stamp and needs a fresh look.
Reviewed-identity note: G3/G4 were recorded at 81e3e508; `git diff --name-status 81e3e508..edcddf71` for this task's allowed paths is EMPTY (content identical), and edcddf71 adds only project-control gate/report/state/task files and one DISCOVERY_BACKLOG line — so the frozen head carries the reviewed content unchanged.

ROW M5-T126 D-090-R357: PASS
 - docs/measurement-basis/MEASUREMENT_BASIS.md §1c (lines 145-151) states the zoning and HPD bases "measure different things" and are "never mixed"; HCR's common-space percentage is named as a third basis and "is not used here".
 - Each schedule row (MEASUREMENT_BASIS.md §2 table, lines 163-183; each example page) names the component's treatment under BOTH systems separately, so no figure combines the two bases.
 - Double-deduction is prevented by construction: reconciliation lists each differing component once; test_mutation_proof_e_a_duplicated_bridge_step_fails and _a_component_deducted_under_both_systems_fails (test file lines 195-214) reproduce that a second deduction fails the check.

ROW M5-T126 D-090-R358: PASS
 - MEASUREMENT_BASIS.md orders definitions (§1 "The two areas, each defined by its source", line 26) BEFORE the ratio formula (§4, line 211). I confirmed the text position: "floor area" definition precedes "total HPD-measured dwelling-unit area".
 - Reproduced by test_record_defines_each_area_before_the_formula (test file lines 63-68): asserts text.find("floor area") < text.find("total hpd-measured dwelling-unit area") — passes.

ROW M5-T126 D-090-R359: PASS (task's share; owner-showing + numeric worked table are owed, see note)
 - MEASUREMENT_BASIS.md §8 "Open points for the owner" (lines 275-320) assembles the three return parts for the coming owner update: the proposed starting values as unapproved assumptions (points 1-3: ratio, 700 sq ft, editable inputs), the evidence/basis for each ("*Basis:*" on each point), and the uncertainty ("unvalidated", "not sure", "not known").
 - The fourth part (how the count moves) is present only as DIRECTION, not a numeric table: §8 closing paragraph (lines 322-327) states directions only and explicitly "no count is computed in this record".
 - LEFT / owed: R359's harness ("the owner update holds the four parts, the last as a worked table") is a post-acceptance owner update; the literal showing to the owner has not happened at this head (task status awaiting_gate), and a numeric worked table of count movement cannot exist until an estimator does. This task does its share (prepares the content); the owner update is named as the remaining step. Not a blocker for a RECORD task.

END OF PART 1 of 4

PART 2 of 4

ROW M5-T126 D-090-R387: PASS (task's share)
 - This task IS the reviewed measurement-basis record that resolves which area the estimate starts from, which area an apartment is measured as, and how they relate (MEASUREMENT_BASIS.md §1, §3, §4). No estimator is built: `git show --name-only 0a3ffed3 dbffb46b` (the two material commits) touch ONLY docs/measurement-basis/**, services/api/tests/scenario/measurement_basis/** and project-control/reports/M5-T126-producer-report.md — nothing under services/api/app/**.
 - Record header (lines 3-4, 18): "No estimator is built by this record and no program code is changed." Forbidden_paths in the packet bar services/api/app/**; the diff honours it.

ROW M5-T126 D-090-R388: PASS
 - MEASUREMENT_BASIS.md §3 line 205: "No generic gross-to-net loss percentage is applied to zoning floor area (R388, R397)." I searched the record and all three examples for any multiplication of zoning floor area by a generic figure (grep for gross-to-net / "% of zoning" / "times 0." / 25% / 75%): the ONLY hit is that negative statement; no such arithmetic exists.
 - The method is inclusion-based: measurement_basis_lib.residential_zoning_floor_area and total_hpd_dwelling_unit_area (lib lines 236-241) each SUM the components that count; neither multiplies by a loss factor.

ROW M5-T126 D-090-R389: PASS (task's share; literal owner-showing owed)
 - The written step-by-step conversion exists: MEASUREMENT_BASIS.md §2 (one schedule, each component's zoning vs HPD treatment with its governing provision) and §3 (two separate calculations then reconcile), each component carrying its law text (ZR 12-10 / 23-23x) or the HPD guideline quote.
 - A worked example accompanies it: example-a/-b/-c pages show the schedule, both totals computed separately, and a line-by-line reconciliation; test_both_areas_summed_separately_and_reconciled and test_the_bridge_accounts_for_every_square_foot_of_the_difference (test lines 147-170) reproduce that nothing is deducted twice.
 - Each space zoning already leaves out is named and NOT re-deducted (schedule rows for cellar, mechanical room; test_nothing_already_out_of_zoning_is_deducted_again, lines 120-128). LEFT: the act of showing the owner is the orchestrator's post-acceptance step.

ROW M5-T126 D-090-R392: PASS
 - MEASUREMENT_BASIS.md §5 (lines 225-234): the legal unit cap is a "separate figure", "not derived from the physical estimate (and the physical estimate is not derived from it) - R392, R404".
 - Rounding is applied ONLY to the legal cap: measurement_basis_lib.legal_unit_cap_units (lines 252-259) applies the ZR 23-52 three-quarters rule to max residential floor area / 680; the physical areas (residential_zoning_floor_area, total_hpd_dwelling_unit_area) stay exact decimals with no unit-rounding.
 - Each example shows a distinct units_cap (A=13, B=17, C=11) alongside its measured areas; test_legal_cap_is_separate_and_recomputes (lines 281-288) asserts the measured area differs from the max allowed.

ROW M5-T126 D-090-R396: PASS
 - MEASUREMENT_BASIS.md §4 line 215: "ratio = total HPD-measured dwelling-unit area / residential zoning floor area", with line 218 "nothing else enters the ratio (R396)". Matches the owner's exact words in source-043 (message 94).
 - Reproduced in data: every example's reconciliation.ratio has numerator == total HPD dwelling-unit area and denominator == residential zoning floor area; test_ratio_numerator_and_denominator_are_named (test lines 291-295) asserts this.

ROW M5-T126 D-090-R397: PASS
 - MEASUREMENT_BASIS.md §2 (lines 157-187) lists, per component, the spaces zoning already excludes (cellar, accessory mechanical room, qualifying parking/balconies) with treatment "excluded only if a stated condition is shown"; an unmet condition COUNTS the space (example A corridor, example B parking-room).
 - No allowance is taken for a space already out of zoning: test_nothing_already_out_of_zoning_is_deducted_again (lines 120-128) shows mechanical-room and cellar have bridge_contribution 0 and never appear in the reconciliation bridge; check.bridge_errors (check.py lines 348-351) refuses any bridge step for a component not in the residential zoning floor area.

ROW M5-T126 D-090-R407: PASS
 - MEASUREMENT_BASIS.md §6 (lines 238-244): a mixed-use estimate uses the residential portion's zoning floor area, "not the whole building's and not a shop floor's"; shared-space allocation and combined-FAR are named as checks/open points.
 - example-c-mixed-use shows the residential area used (6,920 sq ft) and where each component comes from; the three retail (non_residential) components count 0 toward the residential zoning floor area and 0 for HPD; test_mixed_use_uses_the_residential_portion_only (test lines 263-275) reproduces this and confirms residential lobby/circulation IS counted.

END OF PART 2 of 4

PART 3 of 4

ROW M5-T126 D-090-R413: PASS
 - MEASUREMENT_BASIS.md §1b (lines 120-135) quotes the HPD rule verbatim: "Structural members that are integral components of exterior walls or demising partitions, as well as all mechanical and plumbing chases, are excluded ... All other structural members - including freestanding columns and columns attached to interior partitions - are included", and concludes "The model must therefore not subtract all apartment walls (owner directive R413)." This matches the owner's own HPD description in source-043 message 94.
 - Reproduced in data: in every example the interior-partitions component has hpd.treatment == "count" while demising/exterior walls and chases are "exclude"; test_hpd_keeps_partitions_and_uses_mechanical_and_plumbing_chases (test lines 84-92) asserts partitions stay in.
 - I verified the HPD quote is internally pinned (lib HPD_SOURCE: official nyc.gov URL, pdf_sha256 309d1863..., pdf_page 28, date_read 2026-10-07) and that guideline citations in the examples are substrings of that embedded text (check._guideline_citation_errors). I could NOT re-fetch the live PDF (no network); see "could not check".

ROW M5-T126 D-090-R428: PASS (task's share)
 - No apartment count is presented anywhere in the record as an accurate feasibility result — the record computes no count (MEASUREMENT_BASIS.md §8 closing, line 327: "no count is computed in this record").
 - The four things the owner requires resolved are each named as OPEN for the owner: §8 lists the zoning-area conversion/ratio (points 1,7), mixed-use allocation (point 6), applicable exclusions (point 7), and physical layout / "not known without a layout" (point 4). §8 point 8 states the estimator is built only after points 1-7 settle (R387, R428).

ROW M5-T126 D-090-R430: PASS
 - MEASUREMENT_BASIS.md §3 (lines 191-203): from ONE schedule, residential zoning floor area and total HPD dwelling-unit area are each computed on their own (step 1 and step 2), then reconciled (step 3); "Neither is derived from the other."
 - Reproduced in code: measurement_basis_lib.residential_zoning_floor_area sums zoning_counted; total_hpd_dwelling_unit_area sums hpd_counted (lib lines 214-241) — two independent inclusion sums over the same component list. The bridge is a reconciliation check, not a derivation. test_both_areas_summed_separately_and_reconciled passes with the hand-verified oracle totals (test EXPECTED, lines 31-38).

ROW M5-T126 D-090-R431: PASS
 - MEASUREMENT_BASIS.md §3 line 193-195 records the withdrawal: "do not reach apartment area by subtracting walls and shafts from zoning floor area (that risks deducting, a second time, space zoning already excluded - R431)."
 - No record/formula/code derives apartment area by subtraction: HPD area is an independent inclusion sum (lib hpd_counted). check.bridge_errors (check.py lines 321-366) fails closed if any bridge step deducts a component already out of zoning; test_mutation_proof_e (test lines 195-206) reproduces that adding a cellar subtraction (a double deduction) is rejected with "not in the residential zoning floor area".

ROW M5-T126 D-090-R432: PASS
 - MEASUREMENT_BASIS.md §3 steps 1-2 and §4 follow the reviewer's table exactly: residential zoning floor area = measured physical residential space minus applicable zoning exclusions; total HPD dwelling-unit area = the same measured space minus everything excluded under HPD's rules; ratio = HPD / zoning.
 - §2 schedule header (lines 155-162) and the example schedules show each area "starts from the measured physical residential space and takes its own deductions". Reproduced by the lib functions and the reconciliation/ratio tests.

ROW M5-T126 D-090-R433: PASS
 - MEASUREMENT_BASIS.md §2 is one area-schedule table with one row per component (apartments, interior partitions, demising/exterior walls, qualifying wall thickness, chases, corridors, stairs, lifts, lobby, elevated-access, refuse, amenity/laundry, mechanical room, cellar, parking, balconies, energy) and a column for each system (zoning | HPD).
 - Each example's JSON has a components list with unique component_id and both a "zoning" and an "hpd" block per component; check.component_shape_errors enforces one row per component with both treatments; test_one_schedule_two_treatments (test lines 74-82) asserts no duplicate ids and valid treatments under both systems.

ROW M5-T126 D-090-R434: PASS
 - The precise HPD term "mechanical and plumbing chases" is used for the chase component throughout (MEASUREMENT_BASIS.md §1b line 133, §2 line 171; each example's "chases" component name and HPD reason). record_errors (check.py line 458) requires the exact phrase in the record.
 - Other shafts are named for what they are and treated by their own rule: elevators/lift shafts and stairs/stairwells are separate components under ZR 12-10 (schedule lines 172-174; example "Elevator shaft" rows). I grepped every "shaft" occurrence: all are either the ZR 12-10 zoning quote "elevator shafts or stairwells" or the lift/stair components — none puts "shafts" where HPD's rule says chases. The single §3 "walls and shafts" phrase (line 194) describes the WITHDRAWN subtraction method, quoting the owner's own prior wording.

END OF PART 3 of 4

PART 4 of 4

ROW M5-T126 D-090-R435: PASS
 - MEASUREMENT_BASIS.md §3 line 206-207: "The measured physical space comes from a proposed building layout, never from the maximum floor area the law allows (R435)."
 - Every example labels its made_up_note "The maximum floor area the law allows is used only as a limit to check the layout against, never as the measured space" (example pages line 7); areas are recomputed from stated dimensions, and each example's legal_unit_cap.max_residential_floor_area differs from its measured residential zoning floor area. Reproduced by test_areas_come_from_the_stated_dimensions (test lines 134-141) and test_legal_cap_is_separate_and_recomputes (asserts measured != max).

ROW M5-T126 D-090-R436: PASS
 - MEASUREMENT_BASIS.md §7 "What they do not show" (lines 266-271): the three ratios (0.7540, 0.6022, 0.6676) "differ ... precisely because each depends on its own made-up layout"; "Correct arithmetic is not support for an assumption"; "Example A's ratio happening to land near 75 percent proves nothing about any 75 percent ratio."
 - Each example page carries "This ratio belongs to THIS made-up example only. Two or three examples cannot establish a typical figure; no percentage is validated here." No percentage is presented as typical of R6B. test_examples_do_not_present_a_typical_percentage and test_the_worked_ratios_are_example_specific_and_differ (test lines 155-159, 249-257) reproduce the three distinct ratios and the disclaimer.

ROW M5-T126 D-090-R437: PASS
 - MEASUREMENT_BASIS.md §6 line 240-241 uses the exact owner-required input: "the estimate uses the residential portion's zoning floor area, including any counted residential circulation and support space". example-c uses the same wording.
 - The forbidden phrase is absent: grep across docs/measurement-basis for "area actually given to apartments" / "actually given" returns nothing; the input is consistently called "the residential portion's zoning floor area" (matches R437's harness).

TEST EXIT CODE: 0 (27 passed; `python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis` from services/api).

CARRY-FORWARD CONDITION: as stated in full in PART 1 — stamp holds while (a) all files under this task's allowed_paths, (b) the eight cited ZR captures, and (c) the twenty rows + D-090 manifest + sources 042/043/044 are byte-unchanged; tolerant of later project-control/** commits, one DISCOVERY_BACKLOG.md line, the other two tasks' records, and an integration-branch merge that leaves (a)-(c) untouched.

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none.

NON-BLOCKING OBSERVATIONS:
 - R359/R389 are "return" items whose literal delivery (showing the owner; R359's numeric worked table of count movement) is a post-acceptance orchestrator step and cannot exist until an estimator does. This task does its full share (the record content). When the orchestrator runs the owner update, R359's worked table should be produced then; verify at that point.
 - Example B's amenity 5% cap base is deliberately left as an open point (MEASUREMENT_BASIS.md §8 point 5); the data carries two candidate bases (5% of measured 11,291 and 5% of stated max 12,000) and the min_of includes the measured 480, so the cap does not bind — internally consistent and does not assert a settled base. Consistent with the round-2 F1 fix (commit dbffb46b).
 - Task status is awaiting_gate (progress 95), not accepted; PR 459 head is a task branch, not merged into main (a5c6c2f0). No open blocker references M5-T126. No prohibited action observed: nothing merged/accepted/deployed/installed/purchased/closed; no estimator or program code (services/api/app/**) changed by this task's commits (0a3ffed3, dbffb46b).
 - Support files all under the 600-line threshold (check 478, lib 259, render 259, test 328); S11 satisfied.

WHAT I COULD NOT CHECK MYSELF:
 - I could not re-fetch the live HPD Design Guidelines 2026 PDF (no network in this sandbox). I verified the HPD quote is internally pinned (URL, sha256 309d1863..., page 28, date 2026-10-07) and that it matches the owner's own quoted HPD wording in source-043 (which is the directive's primary evidence for R413/R434). The ultimate PDF-origin check is the law-capture task's concern and outside my twenty rows.
 - The ZR capture digests I verified by the stored content_digest_sha256 and by confirming each quoted fragment is a substring of the capture's verbatim_excerpt (the snapshots write defined terms as #term#, which check.py strips before matching); I did not re-derive each capture from the live planning.nyc.gov page (that was task M4-T025, already accepted, DB-167).
 - I did not run tools/validate_directive_compliance.py (the second verifier runs it once, per the prompt), nor the full api suite or test_directive_compliance.py.

END-OF-REPORT
```
