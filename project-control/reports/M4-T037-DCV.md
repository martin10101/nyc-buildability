# M4-T037 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c94d8976ee55172eb1a23266a25eba17c82df9af` (branch `task/wave17-hand-worked-option`, review copy `/root/project/rv-w6-c`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R291, R519, R545, R650, R651, R664, R686, R687, R688, R689, R690, R699, R700.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. Two non-blocking notes already recorded by the G3/G4 reviewer stand: the floor-schedule-contents row has no dedicated content test (covered only by schema + both-readings validation), and reading 14's two real-lot portion areas sum to 10,387.98 vs its own stated 10,387.99 (its 0.01 rounding, faithfully transcribed under the not-known framing). Neither blocks any of the thirteen rows.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-09 07:07 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M4-T037 (directive D-090, thirteen rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is NOT a human or professional/legal review. I produced none of this work and none of its records; I worked read-only in the detached copy /root/project/rv-w6-c and treated every report, map and gate record as an unverified claim to reproduce.

(1) HEAD VERIFIED
 - git -C /root/project/rv-w6-c rev-parse HEAD = c94d8976ee55172eb1a23266a25eba17c82df9af (the frozen head); working tree clean.
 - validate_directive_compliance.py --check run once in the copy: exit 0 (direct exit code).

(2) ROWS

ROW D-090-R291 — PASS
 - Row text (requirements.json): "independently calculated examples are saved as files to test against"; classification sequencing, status pending, applicability includes M4-T037.
 - The task saves one independently-worked example as files: docs/reference-cases/R6B/cases/step-p6-worked.json (30 rows) + provenance/return-independent-hand-calculation-13.md and -14.md + the step-P6 test module; nothing comes from a program run (the case summary/what_it_does_not_establish say agreement is not proof and no value is from a program; grep of services/api/tests/rules/reference_cases/*.py found NO engine/app import).
 - This task's share = adding step P6 as one more saved example; R291 is applicable to many M4 tasks (M4-T024..M4-T037) and stays pending in the registry for the rest.

ROW D-090-R519 — PASS
 - Row text: an illustration states its assumption and no estimate treats floors as equal floorplates above the maximum base height / no storey above the base counted.
 - In step-p6-worked.json every worked building stays at/below the 45 ft maximum base height (made-up A 20 ft, real A 10 ft, both B's 30 ft = the minimum base height), the summary and each building row say "no storey above the base is counted and no setback is worked", and tests test_every_storey_table_sums_to_its_total_and_total_plus_unused_is_the_maximum / test_plan_area_times_storeys_equals_building_a_floor_area recompute the stacks (99 passed).
 - Share: applied to the step-P6 example only; row also binds M5-T133/M5-T135 and stays pending.

ROW D-090-R545 — PASS
 - Row text (prohibition): nothing says the owner's approval validates the starting values or worked examples; they stay unvalidated assumptions.
 - The case what_it_does_not_establish and every estimate/building mark say the 10 ft, 0.60–0.75 and 700 sq ft are "not validated, not measured and not law"; mutation test_an_estimate_row_calling_its_figures_validated_is_refused enforces this (passes).
 - Share: enforced within this case; row also binds M5-T135 and stays pending.

ROW D-090-R650 — PASS
 - Row text: each remaining blocker says which of three kinds it is (missing property fact / unresolved law / code not built).
 - The three not_known rows (made-up-street-wall, real-lot-coverage-by-portion, real-lot-rear-yard-variants) each carry "KIND OF GAP:" naming a missing property fact or a measurement (test_step_p6_not_known_rows_with_a_kind_of_gap asserts it); the G0 report's five remaining pieces each state a KIND; closing rows real-lot-missing-facts and six-steps-closing tag every gap by kind.
 - Share: satisfied for this task's blockers; R650 is bootstrap-wide and stays pending.

ROW D-090-R651 — PASS
 - Row text (sequencing): before any new reading is commissioned the record identifies which are really necessary.
 - project-control/reports/M4-T037-G0.md quotes in full the list "Which new readings the first building shape really needs", states it was written 2026-10-09 04:42 UTC and the two readers were started 05:16 UTC (04:42 < 05:16); project-control/reports/WAVE17-2026-10-09-concurrency-record.md records the same readers, their 05:16 UTC start, read-only, and that they wrote no repository file.
 - The quoted list is internally complete and consistent; the wall-clock times are orchestrator-asserted from the session transcript (not in the repo), noted in (6). Row stays pending.

ROW D-090-R664 — PASS
 - Row text: the smallest remaining work for the milestone is identified from the helper's findings.
 - project-control/reports/M4-T037-G0.md "THE SMALLEST REMAINING WORK" lists five pieces in order, each with its KIND and what it DEPENDS ON, and names the one point of the helper's study it corrected (that one new reading is necessary).
 - Share: identification done; row stays pending for the downstream pieces (generator, coverage-by-portion, estimator, screen).

ROW D-090-R686 — PASS
 - Row text: the requirements of the owner's message are put into the tasks they concern (as scope, scenarios and bound rows).
 - The packet project-control/tasks/M4-T037.json carries the objective paragraphs "THE SIX STEPS OF THE COMPLETE CALCULATION" and "LEGAL REQUIREMENT OR DESIGN ASSUMPTION", scenarios S13 and S14, and binds seven owner-message rows (R686-R690, R699, R700); source-068-amendment.md "Reading" maps each quoted sentence to its row.
 - Share: this task carries its share of source-068; R686 also binds M4-T038 (register side) and stays pending.

ROW D-090-R687 — PASS
 - Row text: for the first building option an independently worked example is compared with the program's actual output through six steps (property inputs; footprint; each floor's area and height; total floor area; legal unit limit; separate preliminary estimate).
 - THIS TASK MAKES ONLY THE INDEPENDENT SIDE: for each lot and each building step-p6-worked.json carries all six steps as rows AND as numbers (numbers_block: footprint_sides/area; per-storey floor_to_floor/top_ft/plan_area/floor_area; total and unused; the legal unit-limit rows; the estimate rows), and row six-steps-closing asserts "All six steps are present as rows for each lot and each building"; tests test_building_blocks_recompute_clean / test_estimate_four_figures_follow_from_the_floor_area / test_real_building_a_holds_both_readers_footprints recompute them (pass).
 - The record states the program's side and the comparison itself are task M4-T038's (task objective; evidence-map known_limits; case what_it_does_not_establish); that comparison stays OPEN in the registry (R687 also binds M4-T038).

ROW D-090-R688 — PASS
 - Row text: the preliminary apartment estimate is separate from the applicable legal unit limit.
 - The legal ceiling is in its own rows (made-up-unit-limit, real-unit-limit) citing ZR 23-52 (digest f48f1ddc…), while the estimate is in separate rows (made-up/real-estimate-a/b) sourced to the owner's starting assumptions via Q6a; different rows, different sources; tests test_made_up_unit_ceiling_is_the_current_conditional_29_superseding_step_p4 and test_real_unit_ceiling_is_pinned_to_the_live_value_of_real_lot_L6 pass.
 - Share: separation held on the independent side; the comparison-level use of this separation stays open for M4-T038; row pending.

ROW D-090-R689 — PASS
 - Row text: completed research is reused.
 - Both provenance headers and README.md (lines ~197) state the readers were "given 34 earlier answers as settled" copied word for word so completed readings are not re-worked; the G0 report's reuse paragraph and the sealed folder's settled_by_earlier_readings.json are cited.
 - Share: reuse demonstrated for this reading; R689 also binds M4-T038 and stays pending.

ROW D-090-R690 — PASS
 - Row text: every remaining disagreement and every missing fact is identified, each with its kind and what would settle it.
 - Rows six-steps-closing (steps where readings differ, with kind), real-lot-missing-facts (three property facts, each with source), both-readers-did-not-have (five texts both readings name) and settled-answer-contradicted (none) cover this; mutation test_a_step_p6_value_where_the_readings_differ_is_refused enforces that a differing figure is not collapsed to one value (pass). The real-lot footprint keeps both readers' figures (10309.91 vs 10309.88).
 - Share: the independent side's disagreements/gaps are listed; the register's gap statement stays open for M4-T038; row pending.

ROW D-090-R699 — PASS
 - Row text: legal requirements are clearly told apart from chosen design assumptions.
 - Every figure in each building and estimate numbers_block carries mark=legal_requirement or design_assumption with a basis (maximum floor area and footprint-bound = legal_requirement; floor-to-floor, same-plan stack, derived counts, share, apartment size = design_assumption); mutations test_a_building_figure_marked_as_neither_is_refused and test_an_assumption_marked_as_a_legal_requirement_is_refused pass.
 - Share: marking done on the independent side; R699 also binds M4-T038 and stays pending.

ROW D-090-R700 — PASS
 - Row text (prohibition): the apartment-size and efficiency assumptions stay labelled as preliminary assumptions.
 - "preliminary assumption" appears 26 times; every row referencing 700 sq ft or 0.60–0.75 (the four estimate rows) carries the words, and the facts/summary do too; mutation test_an_estimate_row_whose_share_lacks_preliminary_assumption_is_refused passes.
 - Share: the words are present wherever the two figures appear in this case; R700 also binds M4-T038 (register pages) and stays pending.

(3) BINDING B1–B5
 - B1 PASS. Diff of D-090 requirements.json 65c60679..c94d8976: six pre-existing rows (R291,R519,R545,R650,R651,R664) each gained exactly M4-T037; 86 NEW rows R685–R770 added (the seven of these that are in the thirteen — R686..R700 — are created already carrying M4-T037 and M4-T038); M4-T038 appended across 23 rows (incl. existing R379); zero existing rows removed; zero existing row text/classification changed. Exactly 13 rows carry M4-T037 and they are precisely the cited thirteen.
 - B2 PASS. directive_registry.sha256_text_artifact(requirements.json) = 39093a36a93e71c56decd7d190d0c7faf1307cbde326e3c85f8782352ca453e0 == manifest.requirements_content_digest_sha256.
 - B3 PASS. verification.json has exactly one M4-T037 row; applicable_requirement_ids = the thirteen; producer rules-engineer; verifier ""; every requirement state=pending with empty evidence.
 - B4 PASS. reg.evaluate_task_refs(M4-T037.json): ok=True, missing_ids=[], invalid_refs=[], applicable==cited==the thirteen.
 - B5 PASS. Scanning every active directive's requirements by task_id/task_type(research)/milestone(M4)/path: the only requirements applicable to M4-T037 are the thirteen cited D-090 rows; nothing else applies uncited.
 - Gates: G0 PASS (orchestrator, administrative, reviewed_sha 0929af2a claim seam); G2 PASS (orchestrator self-check), G3 PASS and G4 PASS (data-contract-verifier) all at reviewed_sha 4edf2dac with one content identity content_manifest_sha256=56da988414… The review (M4-T037-G3G4.md) was performed at head 22262650, on which CI run 37894474011 was recorded green and read 06:44 UTC before the review (received 06:53 UTC); the task's allowed_paths files are byte-identical across 22262650 → 4edf2dac → the frozen head (git diff empty), and 22262650 is an ancestor of 4edf2dac, so the review validly carries to the gate head. corner-reach.json is byte-identical to the base (reach rows unmoved); real-lot#L15 superseded_by [step-p6#real-building-a, real-building-b] (kept kind/value), step-p4#made-up-100x100-units superseded_by [step-p6#made-up-unit-limit], real-lot#L5 and corner-reach#real-lot-coverage left not_known, real-lot#L6 unchanged.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the blob-level predicate holds: every file under docs/reference-cases/R6B and services/api/tests/rules/reference_cases and project-control/reports/M4-T037-producer-report.md keeps its blob id; provenance digests stay b1cf6454…(13) and e30eb39e…(14) and the reach-rows digest e708d886…; docs/research, services/api/app/scenario, services/api/app/rules/rulesets, packages/contracts, .github and tools are unchanged; and the thirteen rows' text and binding (B1–B5 above) are unchanged. All of this is true at the frozen head now.
 - Tolerated later commits: those touching only project-control/**, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, and the M4-T038 files on this branch (services/api/app/rules/review_register/**, docs/zoning-rule-review/**, services/api/tests/rules/test_zoning_rule_review_register_calculations.py); and a merge of the integration branch that changes none of the predicate's files. The branch's existing extra commits already fall only within these tolerated paths (no protected dir changed).

(5) REQUIRED CORRECTIONS
 - None. Two non-blocking notes already recorded by the G3/G4 reviewer stand: the floor-schedule-contents row has no dedicated content test (covered only by schema + both-readings validation), and reading 14's two real-lot portion areas sum to 10,387.98 vs its own stated 10,387.99 (its 0.01 rounding, faithfully transcribed under the not-known framing). Neither blocks any of the thirteen rows.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - CI result: I did not and may not re-run CI; I reproduced git ancestry and byte-identity of the task files and read the gate/review records, but the green status of CI run 37894474011 on head 22262650 rests on the recorded run, not a re-execution.
 - Wall-clock times (list written 04:42 UTC; readers started 05:16 UTC; returns 05:29/05:30; review 06:53 UTC) come from the session transcript, which is outside the repo; I confirmed the records are internally consistent, not the live timestamps.
 - Reader independence and the readers' tool-log audit (no repo/web/other-reader access) are orchestrator-attested in the concurrency record and self-attested in the two provenance files; I verified the two readings differ and match their pinned digests, but cannot re-audit the readers' transcripts.
 - Harness scope: per the brief I ran validate_directive_compliance.py --check (exit 0) and, from services/api, pytest tests/rules/reference_cases (99 passed); tools/test_directive_compliance.py and the full api suite were forbidden and are CI's responsibility.
END-OF-REPORT
```
