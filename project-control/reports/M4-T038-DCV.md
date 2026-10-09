# M4-T038 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `5d7d3c7a79a19becd8e7ee0e4a69c9e43bee2f69` (branch `task/wave17-hand-worked-option`, review copy `/root/project/rv-w6-c`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R379, R686, R687, R688, R689, R690, R691, R692, R693, R694, R695, R696, R697, R698, R699, R700, R701, R702, R703, R704, R705, R706, R707.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one part, received whole; the return is kept unchanged below, received 2026-10-09 08:26 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M4-T038 (directive D-090, twenty-three rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only compliance verification, NOT a human or professional/legal review; the register's legal readings stay unreviewed drafts under ADR-007, and every calculation page reads "Not reviewed". I produced none of the work or records under review and reproduced each judgement from primary evidence in my detached copy /root/project/rv-w6-c.

(1) HEAD VERIFIED
 - git rev-parse HEAD in /root/project/rv-w6-c == 5d7d3c7a79a19becd8e7ee0e4a69c9e43bee2f69, the frozen head (detached, clean).
 - fedef10b (reviewed head) and 64689ac7 (gate-record head) are both ancestors of the frozen head; the diffs fedef10b..64689ac7 and 64689ac7..5d7d3c7a touch only project-control/** and docs/DISCOVERY_BACKLOG.md, so every material (allowed-path) blob is byte-stable from the reviewed head to the frozen head.
 - python tools/validate_directive_compliance.py --check exit 0; the register suites pass (86 passed = 44 existing + 42 new); render_review_register.py --check exit 0 ("register check PASSED").

(2) ROWS
ROW D-090-R379 — PASS
 - CLAUDE.md line 36 (principle 20, citing D-090-R379) carries the standing instruction: every session that adds or changes zoning-rule behaviour updates the register as part of the same change; the full diff 28026c5e..frozen head leaves CLAUDE.md unchanged (it is a forbidden path, pre-set by M4-T023).
 - This task did update the register inside its own commits by the existing process (register.json plus rendered docs/zoning-rule-review/ pages), satisfying the same-change duty.
 - No zoning-rule behaviour changed: the claim-seam..frozen-head diff touches no services/api/app/rules/rulesets/** and no services/api/app/scenario/** file.
 - Open for later: R379 is a permanent standing duty; no single task closes it — every future rule/calculation-changing session must keep honouring it.
ROW D-090-R686 — PASS
 - The source-068 requirements are carried into project-control/tasks/M4-T038.json as scope, acceptance scenarios S1-S14 and the 23 bound rows (rulings C1-C9), so the builder and both reviewers worked to them.
 - It is one ordinary ledger packet, not a separate project, consistent with R707.
 - The shared rows (R686-R690, R699, R700) also bind M4-T037, which carries the independent side of the comparison.
 - Open for later: R686 is the standing "include these requirements in the tasks they concern" obligation; later tasks touching these subjects must keep carrying the relevant rows.
ROW D-090-R687 — PASS
 - docs/zoning-rule-review/calculations/calc-first-building-option-complete.md sets the step-P6 independent example beside the program's actual output in six ordered steps (property inputs; footprint; each floor's area+height; total floor area; legal unit limit; preliminary estimate), each with a named case#row expected, the program's actual at a named revision/fixture, and a verdict.
 - The actual sides are the program's real output: I confirmed in recorded_215_16_northern_journey.json floor area 20150.0 conditional, max_lot_coverage and legal_unit_limit_standard withheld, building_option/floor_stack/unit_estimate not_available — matching the page.
 - The expected side cites step-p6/real-lot/step-p5 rows (all confirmed present) and is never taken from a program run; one step agrees (floor area), one differs by method (DB-210), four are side-missing.
 - Open for later: the footprint, floor stack, total, unit-limit display and estimate program sides stay withheld/not-built until those engine pieces are built and re-compared.
ROW D-090-R688 — PASS
 - calc-legal-dwelling-unit-limit and calc-preliminary-apartment-estimate are two separate calculation entries in register.json and are steps 5 and 6 of the six-step page, kept apart.
 - The estimate is marked a preliminary assumption (700 sq ft, 0.60-0.75), never a legal limit; test_size_or_share_marked_legal_is_refused enforces the separation.
 - Open for later: the estimate is not built in the program (not_available), so step 6 stays a side-missing comparison until built.
ROW D-090-R689 — PASS
 - Every expected side cites existing reference cases (real-lot, step-p5, step-p6, step-p3, step-p1); the claim-seam..frozen-head diff touches no docs/reference-cases file, so no new reading was made here.
 - step-p6-worked.json (the independent side, M4-T037) is reused and linked, not rewritten.
 - Open for later: continuing tasks must keep reusing the sealed-folder research rather than re-deriving it.
ROW D-090-R690 — PASS
 - The page's closing "Every disagreement and missing fact (and what would settle it)" names each with its kind: the method difference (a design assumption that differs, DB-210), the recorded-vs-outline ~313 sq ft and two-reading decimals (a missing fact about the property), coverage/generators/estimate and the unit-limit display (code not built), the rear yard (a missing fact).
 - Each kind agrees with the program's own gap_kind (work_owed / rule_not_implemented / missing_information), which I confirmed in the fixture; test_every_listed_withheld_gap_kind_agrees_with_the_program enforces it.
 - Open for later: the listed items stay owed (survey/deed, building the generators, the owner's DB-210 decision).
ROW D-090-R691 — PASS
 - register.json now holds a calculations collection fingerprinted by the LF-normalized sha256 of each scenario module; I recomputed result_ways.py (58788c78...) and three_way_document.py (7f0ecfed...) and the combined code_identity (7fc00851...) and all matched the record, so a module change would flip the entry stale.
 - GUIDE.md's "Calculation entries" section states a calculation change moves its entry and flips the test result to Not run, exactly like a changed rule file; test_code_module_drift_is_caught_and_names_the_module proves it.
 - Open for later: a standing keep-current duty; the first session that changes a fingerprinted module must revise the entry.
ROW D-090-R692 — PASS
 - Only register.json was authored; render_review_register.py --check returned exit 0, so every committed page equals the renderer's output of the source data.
 - The material commits modified register.json plus rendered docs/zoning-rule-review/ files only (no hand-edited page), confirmed by git show --name-status.
 - Open for later: standing duty to re-render via --write on every future change.
ROW D-090-R693 — PASS
 - For this task's share, the six entries name the rules combined (combines_rule_ids + law[]), the formula and rounding (dedicated fields), the exceptions, and the design assumptions (legal_vs_design), so the first-building-option path is traceable now.
 - What is not yet traceable is stated in the nine coverage gaps (the whole scenario engine, integration.py/wide-street, the yard/street-wall rules).
 - Open for later: full traceability of combining code outside this path stays a stated gap (gaps #1, #7, #8).
ROW D-090-R694 — PASS
 - Each calculation page carries a Law table (section, official link, last-amended, capture id, digest), a "Where it applies" and an "Exceptions and limits" section; legal rows quote the captured text verbatim (verified on calc-floor-area-allowance.md and calc-first-building-option-complete.md).
 - test_legal_rows_quote_a_verbatim_fragment_of_the_capture and test_every_calculation_entry_carries_an_effective_date enforce the source/version fields.
 - Open for later: the 23 rule pages lacking dedicated point-3 fields is a stated gap (#6), not an R694 defect on the calculation pages.
ROW D-090-R695 — PASS
 - Each page has "How the program reads it" (interpretation) and "What the program does today versus what is planned" (built / withheld / not built).
 - The floor-area page records tested behaviour; the withheld/not-built entries record their standing plainly; test_committed_calculations_validate_clean enforces the structure.
 - Open for later: the planned-but-not-built steps stay recorded until the program builds them.
ROW D-090-R696 — PASS
 - Each page has a dedicated "Inputs, units, measurement basis, formula and rounding" section; where there is no rounding rule the field reads "none - no rounding rule" (verified on calc-floor-area-allowance.md).
 - test_committed_calculations_validate_clean enforces the fields' presence.
 - Open for later: these dedicated fields exist only on calculation pages; adding them to the 23 rule pages is a stated gap (#6).
ROW D-090-R697 — PASS
 - Each page has a worked example with expected (independent), actual (program) and an Automated-test result bound to a tested commit (28026c5e) and code identity.
 - test_calc_floor_area_recomputed_matches_independent recomputes the actual through reg.evaluate and asserts it equals the recorded actual (20150, conditional); I re-ran the suites (86 passed).
 - Open for later: for withheld/not-built steps the actual stays "withheld / not built" at its revision until the program builds it.
ROW D-090-R698 — PASS
 - Each page has "Code and tests" (code modules + test file), a "Code identity" block with per-module sha256, and "Gaps and unresolved questions".
 - I reproduced a calculation's code identity independently; test_code_module_drift_is_caught_and_names_the_module proves the link is live.
 - Open for later: nothing specific; the links stay current under the keep-current duty.
ROW D-090-R699 — PASS
 - Every calculation page has a "Legal requirements and chosen design assumptions" table marking each figure LEGAL_REQUIREMENT (with quoted captured text) or DESIGN_ASSUMPTION.
 - test_every_figure_is_marked_legal_or_design and test_an_unmarked_figure_is_refused enforce completeness.
 - Open for later: enforced by the checker on every future edit.
ROW D-090-R700 — PASS
 - 700 sq ft and the 0.60-0.75 share carry the literal words "preliminary assumption" wherever they appear (9 occurrences on calc-preliminary-apartment-estimate.md, 7 on the complete page), both marked DESIGN_ASSUMPTION; none is presented as law or measured.
 - test_preliminary_assumption_words_are_required_on_size_and_share and test_size_or_share_marked_legal_is_refused enforce it.
 - Open for later: the labels stay required by the checker on any future edit.
ROW D-090-R701 — PASS
 - Six calculation entries that are not rule files are present (floor-area allowance, lot-coverage by portion, building-option floor stack, legal unit limit, preliminary estimate, and the six-step comparison), each combining several rules.
 - test_the_six_calculation_entries_are_present and test_a_calculation_id_colliding_with_a_rule_id_is_refused enforce the set and the id namespace.
 - Open for later: combining code still without an entry (the whole engine, integration.py, wide-street, named-street table, proposal checks) is listed in the coverage gaps, not yet entered.
ROW D-090-R702 — PASS
 - Each page's "Linked records (linked, not copied)" links the measurement-basis record, the reference cases and the rule-coverage matrix; the claim-seam..frozen-head diff touches none of those files, confirming linked-not-copied.
 - Open for later: standing duty to keep the links current.
ROW D-090-R703 — PASS
 - register.json carries a coverage_gaps list of nine plain sentences rendered into REGISTER.md; I read all nine — #9 states M5-T144 changed the engine but moved no register entry, #1 names the scenario engine, #6 names the 23 rule-page field gap with the six R6B-path entries, #7/#8 name integration.py/wide-street and the yard/street-wall rules.
 - test_coverage_gaps_are_data_and_hold_at_least_nine and test_too_few_coverage_gaps_is_caught enforce it; none of the nine read false.
 - Open for later: the list grows as coverage expands.
ROW D-090-R704 — PASS
 - All six calculation entries have human_review.decision = null and verdict "Not reviewed"; no human verdict was entered (both gate reviews are AI-agent reviews).
 - test_every_calculation_reads_not_reviewed and test_a_decision_without_a_named_reviewer_is_refused enforce it.
 - Open for later: a verdict can be set only by a named human reviewer's own decision in future.
ROW D-090-R705 — PASS
 - calculations_history holds six "created" events (one per new entry at revision 1) and the rule history is byte-identical claim-seam..frozen-head (26==26), so nothing earlier was overwritten or removed; the 23 rule entries are also byte-identical.
 - test_calculations_history_is_append_only_and_separate and GUIDE.md's standing append-only reviewer duty cover it.
 - Open for later: no prior calc decisions exist yet; the preserve-on-change duty applies once any decision is recorded.
ROW D-090-R706 — PASS
 - applies_to_current is a derived field (reviewed code identity + law digests + revision vs current), stored apart from the decision; the GUIDE and checker recompute it and refuse a stale "Correct".
 - test_a_decision_whose_code_identity_changes_reads_needs_re_review proves a decision flips to "Needs re-review" on a code change while the earlier decision is still shown.
 - Open for later: exercised in practice once a human decision exists.
ROW D-090-R707 — PASS
 - M4-T038 is one ordinary ledger task (task_type rule_engineering) with the ordinary gates G0/G2/G3/G4 and the normal reviewer roster; no separate project stands beside it.
 - The packet's business reason and ruling C9 confirm it is part of the building-option work (no G5, no route/dependency/ledger-tool change).
 - Open for later: the standing "part of existing work" obligation continues on later rule/calculation tasks.

(3) BINDING B1–B5
 - B1 PASS: requirements.json diff 65c60679..frozen head adds rows R685-R773 (89 new, numerically contiguous, none removed) and changes no existing row's text or classification (0 of 684 common rows changed). All 23 target rows bind M4-T038 at head (R379 pre-existing gained M4-T038; R686-R707 created with M4-T038; R686-R690/R699/R700 also carry M4-T037). M4-T037 was appended to its own pre-existing rows R291, R519, R545, R650, R651, R664.
 - B2 PASS: dr.sha256_text_artifact(requirements.json) = 8ca84d4a58f2... equals manifest requirements_content_digest_sha256; the id digest 480b148d0855... equals the manifest's; locked_requirement_ids == the 773 current ids; source-068 (65b65506...), source-042 (68d9379a...) and source-001 (a7f497c2...) digests all match the manifest; validator --check exit 0.
 - B3 PASS: verification.json (directive_verification/v2) has exactly one M4-T038 task row; applicable_requirement_ids == the 23; every requirement state is "pending" with requirement-level verifier null and task-level verifier "".
 - B4 PASS: reg.evaluate_task_refs(packet) → ok=True, applicable==cited==the 23, missing_ids=[], invalid_refs=[], reasons=[].
 - B5 PASS: evaluate_task_refs derives applicability across all active directives and returned missing_ids=[], so nothing else across the active directives applies to this task uncited. Gate records: G0 PASS (orchestrator, 3a6662fc), G2 PASS (orchestrator, 64689ac7), G3 PASS (data-contract-verifier, 64689ac7), G4 PASS (qa-engineer, 64689ac7) — G2/G3/G4 at one content identity (64689ac7), material files byte-identical to the reviewed head fedef10b; CI run 37902086129 on fedef10b is completed/success, 21/21 jobs, confirmed by a read-only gh query, so G3/G4 were recorded after CI on the reviewed head was green.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided every blob under services/api/app/rules/review_register, docs/zoning-rule-review, services/api/tests/rules and docs/reference-cases, and the task's project-control reports, keeps its blob id; docs/research, docs/measurement-basis, services/api/app/scenario, services/api/app/rules/rulesets, packages/contracts, apps/web/src, render.yaml, .github and tools are unchanged; and the twenty-three rows' text and binding (and the manifest digests) are unchanged.
 - Tolerated later commits: those touching only project-control/**, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md; and a merge of the integration branch that changes none of the predicate's files. Any change to a fingerprinted scenario module without a corresponding entry revision, or any hand-edit of a rendered page, voids this and requires re-verification.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full services/api pytest suite and tools/test_directive_compliance.py (forbidden by the brief; CI's job) — I relied on CI run 37902086129 (21/21 success at fedef10b), confirmed by a read-only gh query, plus my own 86-passed focused register suite, ruff-covered renderer check and validator exit 0.
 - tools/test_project_control.py and tools/test_directive_reminder.py were not run (outside the brief's enumerated allowed runs); this task changed no ledger-tool/governance code (C9: no G5), and the control-plane CI job passed at the reviewed head.
 - The professional/legal correctness of the register's law readings — I am an AI agent; this is not a human or professional review (ADR-007), and every page correctly reads "Not reviewed".
 - The true two-reader independence of the step-P6 sealed-folder process — that is M4-T037's scope (accepted separately); I verified only that the cited case#rows exist and that the expected side is never a program run.
 - History append-only before the claim seam — I verified the rule history byte-identical claim-seam..head and the GUIDE's standing reviewer duty, but the checker reads only the current file, so pre-seam append-only rests on that standing duty.
END-OF-REPORT
```
