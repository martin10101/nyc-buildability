# M5-T145 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `75dba198e5466a7365191ed7e273d80f83ed8ab9` (branch `task/wave18-first-option-modules`, review copy `/root/project/rv-w6-c`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R147, R192, R239, R255, R256, R322, R379, R509, R519, R540, R541, R543, R545, R650, R688, R691, R692, R700, R703, R704, R705, R707, R773.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one part, received whole; the return is kept unchanged below, received 2026-10-09 10:06 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T145 (directive D-090, twenty-three rows)
VERDICT: PASS

I am an AI agent (the independent, read-only directive-compliance-verifier). This is an automated independent verification, NOT a human or professional (architect / zoning) review (ADR-007). I produced none of the work or records; I re-derived every item below from primary evidence in my detached copy /root/project/rv-w6-c.

(1) HEAD VERIFIED
 - git rev-parse HEAD in /root/project/rv-w6-c == 75dba198e5466a7365191ed7e273d80f83ed8ab9 (the frozen head); the commit is "M5-T145: submitted at da8e2c14; gates G2/G3/G4 PASS at one content identity".
 - Material content (services/api, docs/zoning-rule-review, docs/reference-cases, packages, apps/web) is byte-identical from the reviewed head 9d9764f3 to the submit head da8e2c14 to the frozen head 75dba198; the only changes beyond the reviewed head are project-control/** and docs/DISCOVERY_BACKLOG.md.

(2) ROWS

ROW D-090-R147 — PASS
 - Only mistake E10 ("Footprint never larger than the lot", source-025-amendment.md line 65) is in this task's reach; the row names E1–E20 and the rest are other tasks'.
 - Part A guarantees corner + interior == the outline's own area (interior = full - corner, corner_reach_area.py:175-188; a corner exceeding the outline raises ValueError); test_resolve_rest_clamps_rounding_noise_but_raises_a_real_negative, test_s1, test_s4 assert the sum equals the outline area.
 - Part B caps footprint = corner*ratio + interior*ratio with both ratios bounded to [0,1] (lot_coverage_by_portion.py:85-89,115-117); test_c16c_footprint_never_exceeds_sum_of_areas asserts it over the scenario inputs and test_c16b rejects a ratio above 1.
 - Open: the guard on a REPORTED footprint against the lot and mistakes E1-E9,E11-E20 are owed by the wiring step and other tasks; R147 stays open in the registry for them.

ROW D-090-R192 — PASS
 - Part A measures the parcel's own prepared tax-map outline in EPSG:2263 feet (measure_corner_reach_area uses outline.vertices from prepare_outline; _outline_source reads geometry.provenance lot_outline), not a rectangle or typical lot.
 - test_s4_benchmark_lot_within_tolerance_of_both_readings feeds the real replayed MapPLUTO outline (_northern_replay) and lands within 1.0 sq ft of both independent step-P6 readings; test_s3 confirms distance is perpendicular to the actual outline.
 - Open: no parcel conclusion is reported or drawn yet (nothing wired); R192 stays open for the wiring step that reports/draws parcel-specific conclusions.

ROW D-090-R239 — PASS
 - The modules keep the recorded lot area and the measured outline apart and decide nothing: part A reads only the measured outline, part B takes the two measured portion areas, part C takes footprint and floor-area allowance as two separate plain inputs.
 - Which lot area a building rests on is NOT decided here (evidence-map known_limits; backlog DB-210 point a).
 - Open: R239 is also bound to M5-T130 (the resolve task) and the wiring step; how the two area figures are used is decided there, and the row stays open for it.

ROW D-090-R255 — PASS
 - A missing input or unmeasurable lot stays unknown/not_known with a plain reason, never a zero or default: part A unknown_value (corner_reach_area.py:265-269; tests S5/S6), parts B/C/D not_known with named missing_inputs (tests S13/S20/S21/S26).
 - A genuinely measured zero (whole lot within the distance) is a KNOWN value distinct from unknown (test_s2 asserts LABEL_TAX_MAP, value 0.0).
 - Open: labelling a user assumption as a conditional scenario on screen is the wiring/screen work; R255 (also bound to M5-T128/129/130/134/136/137/138/140) stays open there.

ROW D-090-R256 — PASS
 - Design choices are explicit visible inputs with no hidden default: part C floor_to_floor_ft is a required parameter (building_a/building_b signatures, no default); part D share_low/share_high/apartment_size are parameters whose values are returned in the result and named in its texts (preliminary_apartment_estimate.py:92-96,133-135,146).
 - test_s28 confirms the share and size appear in the returned formula and reason texts.
 - Open: showing and editing these starting values on the screen is the wiring/screen work; R256 (also M5-T137-T140) stays open there.

ROW D-090-R322 — PASS
 - Missing facts stay unknown and unbuilt work is called code not built: the R255 tests, plus part C's own-limit states return gap_kind "code not built" (test_s29, test_s30); part E records the modules are connected to no reported result.
 - This restates R255 rule 4 and is followed as written.
 - Open: naming the kind of gap for a missing input and for wired results is owed by the wiring step; R322 stays open for the full report.

ROW D-090-R379 — PASS
 - The standing rule is followed: the register is updated inside this task's own commits (register.json + rendered docs in commit 87d69ec2, PART E) as part of the same change that adds the calculation code.
 - The CLAUDE.md standing instruction (item 20, citing D-090-R379) already exists from the earlier task; this task demonstrates compliance with it.
 - Open: R379 is a standing instruction for every future session; it stays open as a permanent rule.

ROW D-090-R509 — PASS
 - Part D's dividend is the proposed building's residential floor area (floor_area_sq_ft, the first required parameter; preliminary_apartment_estimate.py:92-96,101,144-145), never the maximum; the legal maximum is kept separate (dwelling_units.py not imported). Owner source: source-055-amendment.md lines 49-56.
 - Tests S22/S25 feed each building's own floor area; part C returns a building's total apart from the allowance and the unused remainder (test_s17).
 - Open: feeding part D from the shown building's floor area is the wiring step's; R509 (also M5-T133) stays open there.

ROW D-090-R519 — PASS
 - Part C states its assumptions in every available text (same-plan stack and floor-to-floor height as design assumptions, "not rules of law"; first_building_options.py:230-239,322-331) and returns no storey above the maximum base height (test_s30: code-not-built, height None, no storey row).
 - The one-floor-to-floor-height limit (a 15 ft shop ground floor not worked, R542) is stated in the module docstring and a new register coverage gap.
 - Open: storeys above the base with their setbacks are not worked (code not built); R519 (also M5-T133/T135, M4-T037) stays open for the shape engine.

ROW D-090-R540 — PASS
 - The share range 0.60 to 0.75 is the module default and is called a preliminary assumption, an unvalidated sensitivity range the user can change (preliminary_apartment_estimate.py:94-95,80-89); owner's exact wording source-057-amendment.md line 21.
 - test_s28 asserts "sensitivity range" and "the user can change"; test_c15d rejects a share outside 0-1 and a low share above the high.
 - Open: showing/editing the range on screen is the wiring/screen work; R540 (also M5-T135) stays open there.

ROW D-090-R541 — PASS
 - 700 sq ft is the module default apartment size, called a preliminary assumption, a chosen starting size on the HPD measurement basis the user can change (preliminary_apartment_estimate.py:96,80-89); owner's exact wording source-057-amendment.md line 22.
 - test_s28 asserts "hpd measurement basis" and "the user can change"; test_s27 rejects a zero apartment size.
 - Open: showing/editing the size on screen is the wiring/screen work; R541 (also M5-T135) stays open there.

ROW D-090-R543 — PASS
 - Part D's label is exactly the owner's words: "Preliminary capacity estimate" when available, "Not known" when not (preliminary_apartment_estimate.py:31-32,137,162); owner's exact wording source-057-amendment.md line 24.
 - test_s28 asserts label == "Preliminary capacity estimate" and that "preliminary assumption" is NOT in the label; test_s26 asserts label == "Not known"; the first commit's wrong label was sent back before any review (ruling C15).
 - Open: the label on the screen is the wiring/screen work; R543 (also M5-T135/T136) stays open there.

ROW D-090-R545 — PASS
 - No returned text says the owner's choice validates a value: parts C and D call the values design/preliminary assumptions, not law, measured or validated (first_building_options.py reasons; preliminary_apartment_estimate.py note). Owner source: source-057-amendment.md line 25.
 - test_s28 forbids the words validated/measured/typical and the term "approval"; the register entries carry no human verdict (see R704).
 - Open: R545 (also M5-T135, M4-T037) is a standing prohibition across every screen and record; it stays open.

ROW D-090-R650 — PASS
 - A module names the kind of gap only for its OWN limit: part C returns gap_kind "code not built" for its method limits (test_s29, test_s30).
 - For a missing input the modules name the input and no kind (missing_inputs, gap_kind None; test_s13, test_c12, test_s26); part A gives each unknown outcome a distinct STATE_* code and no kind (test_cause_tells_not_confirmed_from_not_straight, test_more_than_two_confirmed_frontages_split_unknown).
 - Open BY DESIGN (rulings C12/C18): naming which of the three kinds (missing property fact / unresolved law / code not built) a missing input or a measurement state is belongs to the wiring step where the result is decided; R650 (also M4-T037) stays open for that.

ROW D-090-R688 — PASS
 - Part D is apart from the legal unit limit: it imports nothing from the dwelling-unit code (imports only dataclasses/decimal/math) and no text calls its result a legal limit, a ceiling or a count.
 - test_s28 forbids "legal limit", "ceiling", "dwelling-unit limit" and count-style wording.
 - Open: the side-by-side comparison of the estimate with the legal unit limit in the full first-option report is other work; R688 (also M4-T037/T038) stays open there.

ROW D-090-R691 — PASS
 - Part E moved the four on-path calculation entries to revision 2; each now says a module exists and is connected to no reported result, listing the new module(s) in code_modules (register.json: calc-lot-coverage-by-portion, calc-building-option-floor-stack, calc-preliminary-apartment-estimate, calc-first-building-option-complete).
 - The recorded module shas (corner_reach_area bf6435ae, lot_coverage_by_portion 8b603fbe, first_building_options 26a92c40, preliminary_apartment_estimate a0ea51bd) match G3's carry-forward digests; render --check exits 0 and test_code_module_drift_is_caught_and_names_the_module passed.
 - Open: R691 (also M4-T038) is a standing rule for every future rule/calculation change; it stays open.

ROW D-090-R692 — PASS
 - Part E changed only the source data register.json (and one calc-test assertion); I reproduced render_review_register.py --check exit 0; the pages and evidence logs are the renderer's output.
 - No renderer/checker .py changed (git diff of services/api/app/rules/review_register/*.py empty); test_each_calculation_page_is_byte_identical and test_no_orphan_calculation_page passed.
 - Open: R692 (also M4-T038) is a standing process rule; it stays open.

ROW D-090-R700 — PASS
 - Every part D text that names the apartment size or the share carries "preliminary assumption" (_assumption_note, preliminary_apartment_estimate.py:80-89, appended to both formula and reason).
 - test_s28 asserts "preliminary assumption" in formula and reason; the register's calc test test_preliminary_assumption_words_are_required_on_size_and_share passed.
 - Open: R700 (also M4-T037/T038) is a standing labelling rule; it stays open.

ROW D-090-R703 — PASS
 - Every remaining coverage gap is stated plainly: three reworded truthfully (floor-stack, lot-coverage-by-portion, preliminary-estimate now say the module exists but is connected to no reported result), one added (one floor-to-floor height, so a 15 ft shop ground floor is not worked), none dropped.
 - I verified the gap count 9 -> 10 and that every base gap survives (reworded or verbatim) in the head register.json; test_coverage_gaps_are_data_and_hold_at_least_nine passed.
 - Open: R703 (also M4-T038) is a standing rule; it stays open.

ROW D-090-R704 — PASS
 - No human decision is entered: every one of the six calculation entries has human_review.decision null and verdict "Not reviewed" (register.json); both gate reviewers are AI agents.
 - test_every_calculation_reads_not_reviewed passed; the G3/G4 review record states no human verdict.
 - Open: a human verdict can be entered only later by a named human reviewer's actual decision; R704 (also M4-T038) stays open as a standing rule.

ROW D-090-R705 — PASS
 - Previous decisions are preserved: the calculations_history is append-only (the 6 base entries are a byte-prefix of the 10 head entries) and the 23 rule entries and rule history are byte-identical (register.json entries and history unchanged).
 - test_calculations_history_is_append_only_and_separate and test_the_23_rule_entries_are_untouched passed.
 - Open: R705 (also M4-T038) is a standing rule; it stays open.

ROW D-090-R707 — PASS
 - The register update is PART E of this same task, under the same gates (G0/G2/G3/G4) and reviewers; a scope correction before any review put it into the task rather than a separate project (packet scope_corrections; scenarios S31-S33).
 - No separate register project stands beside the building-option work.
 - Open: R707 (also M4-T038) is a standing rule that each rule/calculation task updates the register within its own scope; it stays open.

ROW D-090-R773 — PASS
 - This is ONE task of five parts on separate files: parts A, C and B+D built by three rules-engineer builders side by side (concurrency record WAVE18-2026-10-09; run times 18.9/16.5/17.5 min, one correction each, part E 29.5 min afterwards), within the owner's recorded limits (<=3 builders, no shared file). Owner's exact wording source-075-amendment.md line 16.
 - The parts share no file and none imports another (forbidden-path diff empty; no engine file touched); part E ran only after parts A-D were integrated (a dependency kept in order and recorded).
 - Open: R773 is a standing way of working for future tasks; it stays open.

(3) BINDING B1–B5
 - B1 PASS: diffing requirements.json between b4095ebb and the frozen head, all 23 rows gain "M5-T145" in applicability.task_ids — the 16 build rows at the contract and the 7 register rows (R379,R691,R692,R703,R704,R705,R707) at the scope correction; none carried it at the base; no row's text changed.
 - B2 PASS: tools/directive_registry.sha256_text_artifact(requirements.json) == 36333b955c78ad987716e273a1e803db54d392c9b3e6f4eb480369217ec44f7e == manifest.requirements_content_digest_sha256.
 - B3 PASS: verification.json has exactly one M5-T145 row with 23 applicable_requirement_ids and 23 requirement sub-rows, each state "pending", evidence [], reviewed_sha null; the task-row verifier is "" (empty).
 - B4 PASS: evaluate_task_refs on the packet returns ok True, applicable == cited == the 23 ids, missing/invalid/unresolved all empty.
 - B5 PASS: derive_applicable across all active directives yields exactly those 23 (all D-090); no other active directive's requirement names M5-T145 uncited. The task is rule_engineering and touches no tools/dependency path, so no governance/security directive attaches.
 - GATES: G0 PASS (4 PASS records in history, re-recorded across the packet corrections, history kept); G2 PASS (orchestrator self-check), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer); G2/G3/G4 all at reviewed_sha da8e2c14 (one content identity). The two reviews were pinned at 9d9764f3; CI on 9d9764f3 was green before G3/G4 were recorded — I confirmed via gh that CI (37912550886), secret-scan (37912550888) and context-budget (37912550818) all conclude "success" on headSha 9d9764f3, and the material content at that head is byte-identical to the frozen head.
 - SUPPORTING RUNS I reproduced: validate_directive_compliance.py --check exit 0; focused pytest (the four module tests + the two register test files) 130 passed, exit 0; render_review_register.py --check exit 0; modularity_check.py --check exit 0 (the four new modules are not among the pre-existing warnings; G3/G4 recorded them at 348/149/345/166 SLOC, under the 600 WARN threshold). No forbidden engine file, renderer/checker .py, reference-case, contract, web file, or dependency/lockfile/render.yaml/.github file changed; the 23 rule pages under docs/zoning-rule-review/rules are unchanged. The task is awaiting_gate (not accepted/done); nothing was merged, accepted, dispatched, deployed, installed, purchased or closed.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review iff ALL of: every blob under services/api/app, services/api/tests, docs/zoning-rule-review, docs/reference-cases and this task's project-control/reports keeps its blob id; docs/research, docs/measurement-basis, packages/contracts, apps/web/src, render.yaml, .github and tools are unchanged; and the twenty-three rows' text and binding (B1-B5 above) are unchanged.
 - Equivalently at blob level: corner_reach_area.py bf6435ae, lot_coverage_by_portion.py 8b603fbe, first_building_options.py 26a92c40, preliminary_apartment_estimate.py a0ea51bd and their four test files stay byte-unchanged; register.json code_identity for the four changed entries stays as recorded; render --check stays exit 0; no new app module imports the four modules; CI stays green on that head.
 - Tolerated later commits: those touching only project-control/**, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md; and a merge of the integration branch that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full services/api pytest suite and tools/test_directive_compliance.py were out of scope by instruction (CI's job / hours-long); I relied on the CI "success" conclusions on the exact reviewed head 9d9764f3 plus the focused suite (130 passed) and validate_directive_compliance.py --check exit 0.
 - The absolute geometric correctness of part A's clip against surveyed ground truth: I confirmed it matches BOTH independent step-P6 hand readings within 1.0 sq ft and that corner + interior equals the outline area; the G3 reviewer independently recomputed it with a separate shapely method. No real-world survey was available.
 - The live official ZR 12-10 / ZR 23-362 pages: I confirmed the module's ratios (100%/80%) and 100-ft corner distance against the digest-pinned captures cited in the packet; G3 recorded that a live fetch of the ZR 12-10 page mis-extracted, so authority rests on the pinned snapshot (noted, not blocking).
 - I did not enumerate all 21 CI jobs individually; I confirmed the CI, secret-scan and context-budget workflow conclusions are each "success" on the exact reviewed head.

END-OF-REPORT
```
