# M5-T177 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `bff54dedd0710afdc4b3791251781f9690c9a8a7` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R043, R044, R076, R082, R091, R092.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None blocking. One optional advisory (already carried as backlog DB-260, non-blocking per G3/G4): in row real-lot-missing-facts, the "whether a Commercial District is mapped along the entire 215 Place block frontage (ZR 35-633(b))" missing fact is attributed to "reading 1 also records (reading 1)...", but I independently confirmed BOTH readings record it as NOT KNOWN (return-reading-P8-1.md lines 72/127; return-reading-P8-2.md lines 89/142). It should sit among the joint missing facts. This mis-buckets a shared qualitative not-known observation; it creates no false settled value, changes no recorded figure, and does not affect any of the six directive requirements or feed any later expected value. It may be folded into a later touch.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 03:26 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T177 (directive D-094, 6 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an automated, machine-reproduced review of a DRAFT reading of law written by AI helpers; it is NOT a human, professional, or legal/zoning review, and agreement between two AI readings is not proof. I produced none of the work or records and judged each row from primary evidence (the owner's words in the directive source files, then the task's files read through git plumbing at the frozen head), treating every report/map/gate/claim as an unverified claim.

(1) HEAD VERIFIED
 - I read the frozen head bff54dedd0710afdc4b3791251781f9690c9a8a7 on branch task/wave24-report-v3 in /root/project/w-wave20 (git cat-file -t = commit; subject = the M5-T177 review-record/evidence-map commit).
 - Live HEAD happened to equal the frozen head at review time, so the single allowed validator run (python3 tools/validate_directive_compliance.py --check, exit 0) reflects the frozen state.
 - Every row's evidence below was read with git show bff54dedd:<path> (never the moving working tree); the material commit is e3b0d8fa (a cherry-pick of producer 16e4fb76), and all 12 allowed-path files are blob-identical between e3b0d8fa, the gate-reviewed submit head 9bef0b72, and bff54dedd.

(2) ROWS (this task's share = the independent worked example written into docs/reference-cases/R6B/cases/placement-building-b.json, 11 rows; the report page, website drawing, section, engine are later tasks)

ROW D-094-R043 — PASS
 - Source verbatim confirmed: source-001.md line 137 "5. Finish one meaningful spatial example... footprint placed on the site, relevant constraints, section/massing, and a reconciled schedule. Preserve an explicit incomplete state..."; row text in requirements.json (line 1359) matches and carries M5-T177.
 - This task's share is met: placement-building-b.json places Building B's footprint on lot 70 (rows footprint-tax-map 6,716.66 sq ft and placement-tax-map), on the printed-tax-map basis under Z1, with the constraints both readings reach (lot-coverage-max 100%/80% by portion).
 - The explicit-incomplete state is preserved: rows physical-plate-not-checked, lot-coverage-whole-lot, and rear-yard are kind=not_known with a stated kind of gap (verified by step_p8.must_stay_not_known_errors and its passing mutation test).
 - OPEN for later work: the section/massing and the reconciled floor schedule are M5-T172 (engine) and M5-T173 (drawing); they are not in this task.

ROW D-094-R044 — PASS
 - Source verbatim confirmed: source-001.md line 137 "Do not invent geometry to fill a layout."; row (requirements.json line 1392) matches and carries M5-T177.
 - No geometry is invented: every figure cites the two sealed readings and a measurement basis; no value comes from a program run (check.program_result_errors == [] reproduced; reference-case suite 144 passed, render --check byte-identical).
 - Where the readings differ, the row is NOT SETTLED and bases are never merged: gis-conflict-check stays not_known (tax 100.76/66.66/33.34 vs GIS 103.88/64.66/35.31 kept side by side), and the whole-lot coverage share is kept per basis (66.66% tax / 64.66% GIS).
 - The work order's draft "33.32 (map outline)" back clearance is given by neither reading and was correctly NOT recorded (the case records 35.31 from both readings); logged as backlog DB-260. Nothing stays open for this task's share.

ROW D-094-R076 — PASS
 - Source verbatim confirmed: source-002-amendment.md line 35 "Page 5 Three large stacked rectangles... provide no building footprint, placement, circulation, or apartment arrangement."; row (requirements.json line 2431) matches and carries M5-T177.
 - This task's share supplies the missing footprint and placement as a worked example: 100.76 ft on Northern Boulevard x 66.66 ft deep = 6,716.66 sq ft, touching the Northern Boulevard, 215 Place and lot-1 lines at 0 ft and clearing the back line by 33.34 ft, each on the printed-tax-map basis under Z1.
 - Both figures appear in both readings (return-reading-P8-1/2.md: 100.76, 66.66, 33.34 present; placement touches at 0 ft), satisfying the "value only where both agree on the same basis" rule.
 - OPEN for later work: drawing the diagram on page 5 and showing where circulation/apartments would go (labelled by status) is M0-T193 / M5-T173; no detailed apartment layout is produced (owner goal honoured).

ROW D-094-R082 — PASS
 - Source verbatim confirmed: source-002-amendment.md line 48 "Finish one meaningful scenario: a dimensioned footprint on the site, a section, and a reconciled floor schedule. Clearly identify every constraint still untested."; row (requirements.json line 2638) matches and carries M5-T177.
 - This task's share provides the dimensioned footprint for the one scenario (footprint-tax-map, placement-tax-map with explicit dimensions and basis) and names every untested constraint: the not_known rows each state their kind of gap (missing fact about the property, or unresolved law), plus rows both-readers-did-not-have and real-lot-missing-facts.
 - placement_basis_errors reproduced empty: no placement/coverage row omits its basis or the Z1 condition (S6 mutation test passes).
 - OPEN for later work: the section and the reconciled floor schedule are M5-T173; they are not in this task.

ROW D-094-R091 — PASS
 - Source verbatim confirmed: source-003-amendment.md line 26 "Use one explicitly stated percentage from the existing 60-75% assumption. Keep the drawing and calculations consistent, and show the assumed percentage beside it."; row (requirements.json line 2937) matches and carries M5-T177.
 - This task's share uses exactly one stated percentage, 60% (the low end of 60-75%): area-allocation records apartment 12,090.00 sq ft / other 8,060.00 sq ft of 20,150, and 4,030.00 / 2,686.67 per storey; apartment + other = total and per-storey sum = the plate 6,716.67.
 - Every arithmetic step recomputes exactly (lib.recompute_row_errors == []; the +1 mutation on the apartment figure is caught by test_a_changed_allocation_apartment_figure_is_caught); both readings give 12,090/8,060/4,030/2,686.67.
 - OPEN for later work: making the drawn apartment-share proportions equal the stated percentage and showing it beside the drawing is the later drawing task (M5-T164 / M0-T193); only the calculation side is in this task.

ROW D-094-R092 — PASS
 - Source verbatim confirmed: source-003-amendment.md line 27 "Check that the estimate and drawing use compatible area measurements. Do not automatically treat zoning floor area as the physical floorplate area."; row (requirements.json line 2973) matches and carries M5-T177.
 - Compatible measures: the allocation is worked on the proposed building's residential floor area (the estimate's measure); zoning floor area is NOT treated as the physical plate — the plate row carries the label "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" (step_p8.plate_label_errors == []; the dropped-label mutation is refused).
 - The footprint figure (6,716.66) and the plate (6,716.67) are separate quantities, each pinned to its own exact recompute (0.01 apart, within +/-0.5), never forced into one; physical-plate-not-checked stays not_known.
 - Every quantity names exactly one of the nine bases (step_p8.quantity_basis_errors == []; QUANTITY_BASES == tools/research_record_check.py set; missing/invalid-basis mutations refused). Nothing stays open for this task's share.

(3) BINDING B1-B5
 - B1 PASS: all six rows carry M5-T177 in applicability.task_ids; it was already present at the claim head e27bc2a0 (added in the contract commit, not this task's material commit, which does not touch requirements.json); each row's text is byte-identical between e27bc2a0 and bff54dedd.
 - B2 PASS: tools.directive_registry.sha256_text_artifact(requirements.json) = a6810f2256c7af074f99810dc2191c48332275437da3b8d644954632c646b579, equal to manifest.requirements_content_digest_sha256.
 - B3 PASS: verification.json has exactly one M5-T177 block with applicable_requirement_ids = the six ids, verifier "", and each requirement state "pending" (evidence []).
 - B4 PASS: reg.evaluate_task_refs(M5-T177 packet) returns ok=true, applicable_ids == cited_ids == the six, missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: because evaluate_task_refs derives applicability across the whole loaded registry and applicable == cited with no missing, nothing else across the active directives applies to this task uncited.
 - GATES PASS: G0 PASS (orchestrator, f34aec55), G2 PASS (orchestrator), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer) — G2/G3/G4 all recorded at sha 9bef0b72, an ancestor of the frozen head, and all 11 task files are blob-identical at 9bef0b72 and bff54dedd, so the gates reviewed one content identity equal to the frozen head. CI run 38504217080 at 9bef0b72 = 21/21 jobs success; the frozen head bff54dedd also has three completed-success runs.

(4) CARRY-FORWARD CONDITION
 - Blob-level predicate: this verdict may be stamped at any later head where the M5-T177 allowed-path files keep their frozen-head blob ids — placement-building-b.json c0d13cc9, placement-building-b.md 6afc8f11, R6B/README.md db154e26, provenance/return-independent-hand-calculation-17.md e6f0308e and -18.md 42d4934c, r6b_reference_cases_lib.py d1db1624, r6b_reference_cases_check.py c3fd9f92, r6b_reference_cases_step_p8.py 19dc8284, test_r6b_reference_cases_step_p8.py a814879d, test_r6b_reference_cases.py e049844d, test_r6b_reference_cases_step_p7.py 37b68b72 — AND the six rows' text plus their M5-T177 applicability binding stay unchanged, AND manifest.requirements_content_digest_sha256 stays a6810f22.
 - Broad disjoint-peer tolerance: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports, other tasks' directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records (its gate records, M5-T177-reviews.md, evidence-map, verification.json row) and a merge of the main line (e.g. b4704161) that changes none of the predicate files; none voids this verdict.

(5) REQUIRED CORRECTIONS
 - None blocking. One optional advisory (already carried as backlog DB-260, non-blocking per G3/G4): in row real-lot-missing-facts, the "whether a Commercial District is mapped along the entire 215 Place block frontage (ZR 35-633(b))" missing fact is attributed to "reading 1 also records (reading 1)...", but I independently confirmed BOTH readings record it as NOT KNOWN (return-reading-P8-1.md lines 72/127; return-reading-P8-2.md lines 89/142). It should sit among the joint missing facts. This mis-buckets a shared qualitative not-known observation; it creates no false settled value, changes no recorded figure, and does not affect any of the six directive requirements or feed any later expected value. It may be folded into a later touch.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-derive NYC zoning law from scratch or audit the sealed folder's captures against the City's official source; I confirmed the readers worked from the sealed folder (headers, file counts named), that the two provenance files are byte-for-byte the raw returns (diff exit 0) with digests equal to the step_p8 pins (7d6b923..., 0e166f9...), and that all recorded values appear in both readings on the same basis — but two agreeing AI readings are not proof (ADR-007).
 - Per the brief I did not run tools/test_directive_compliance.py or the full services/api suite; I relied on the one allowed validator run (exit 0), the focused reference-case suite (144 passed), render --check (byte-identical), tools/modularity_check.py --check (exit 0, no reference_cases file flagged), and the gh-read CI evidence (21/21 success at 9bef0b72) for the full-suite claim.
 - I did not verify the later tasks (M5-T172 engine, M5-T173 drawing/section/schedule, M0-T193/M5-T164 page-5 diagram and drawn apartment share) that hold the remaining share of R043/R076/R082/R091 — those are out of this task's scope and remain owed.

END-OF-REPORT
```
