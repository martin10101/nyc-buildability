# M5-T172 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `5a826f597398c661d6e2238436f4d721bababa58` (branch `task/wave28-placement-wiring`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R044, R058, R082, R091, R092.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The verdict is PASS for all five rows' shares. Non-blocking observations for the orchestrator: (a) the frozen-head CI run 38781282159 was still in_progress at review time — it runs on a project-control-only delta, but read it green before accept (D-090 R639); (b) research_record_check reports NB-04 code_current=False — pre-existing DB-283 (NB-04 stale vs close_frame_dimensions.py, not edited here), reported-not-failed, correctly left unrevised; (c) the G3 gate JSON names only code-reviewer — the visual-quality-reviewer's G3 PASS (round-2 FAIL closed, round-3 PASS) is captured in M5-T172-reviews.md and I confirmed both visual findings closed on the real print, but there is no separate G3-visual gate record; (d) G1 observation O1 (drawn plates on the GIS basis vs placement.outline on the tax-map basis, each labelled, never mixed, within the 0.5 sq ft reconciliation) is a legitimate carry-forward note, not a defect.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T18:05:42Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T172 (directive D-094, 5 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an independent reproduction of primary evidence, NOT a human or professional/legal review (ADR-007). I produced none of the work or records I checked.

(1) HEAD VERIFIED
 - Frozen head 5a826f597398c661d6e2238436f4d721bababa58 read via git plumbing in /root/project/w-wave20 on branch task/wave28-placement-wiring; `git rev-parse HEAD` returned exactly that sha and the worktree is clean (`git status --porcelain` empty).
 - Material rounds 11b2bb59, e79ddbc6, 5994e220 and the G0 re-record commit 53d98589 (scope correction 3) are all ancestors of the frozen head (confirmed with `git merge-base --is-ancestor`).
 - The frozen head differs from the round-3 head 5994e220 only in project-control files (`git diff --name-only 5994e220 5a826f59` lists only gates/reports/state/tasks); all production, benchmark, record and snapshot blobs are byte-identical, so the gates/CI/print taken at 5994e220 cover the frozen production content.

(2) ROWS

ROW D-094-R044 — PASS
 - Source matches: source-001.md lines 137/249 "Do not invent geometry to fill a layout."; the requirements.json row text is the owner's words, unweakened.
 - No geometry is invented: result_way_engine_bridge.py assembles the four lot measures each from its own source (_lot_tax_dimensions reads PLUTO lotfront/lotdepth as printed_tax_map and explicitly NOT scope lot_front_ft per DB-260; _frontage_edge_length_ft from the prepared outline; _street_reach_ft from the lot-reach), and every helper returns None when its source is unread — never a default (I read lines 401-480).
 - The drawn plates are real computed polygons: I reshoelaced the benchmark geometry.floor_plates (3 entries, GIS vertices) = 6716.569 sq ft each, reconciling to the plate gross_sf 6716.6667 within 0.098 sq ft (< 0.5 tol); place_building_on_geometry returns None (keeps honest not_available) when no corner footprint can be formed.
 - Nothing stays open for this task's share; the drawn footprint on the site plan (M5-T173 part B) must itself honour R044 when it is drawn.

ROW D-094-R058 — PASS
 - Source matches: source-001.md line 175 "...same result revision and scenario. Distinguish allowance, scheduled area, demonstrated site fit, preliminary apartment estimate, and legal unit limit." — row text verbatim.
 - One document: the placement, area_allocation and floor_plates all come from the one regenerated benchmark recorded_215_16_northern_journey.json (contract_version 1.5.0), which the live route reproduces (test_results_read_api street_on asserts doc == committed); the frozen benchmark blob is byte-identical to the round-3 head.
 - Categories stay distinct in the real print (print-5994e220/report.html): "Floor-area allowance ... 20,150 sq ft" vs "Building B scheduled 20,150 sq ft" vs "Placed on site: Worked out; not drawn" vs "site fit unverified" vs "legal dwelling-unit limit ... conditional ceiling" vs the preliminary apartment estimate — allowance, scheduled area, demonstrated site fit, estimate and legal unit limit are each separately labelled.
 - Nothing material stays open for this task; later pages that add diagrams (M5-T173) must preserve the same-revision/same-scenario discipline.

ROW D-094-R082 — PASS (this task's data share)
 - Source matches: source-002-amendment.md line 48 "Finish one meaningful scenario: a dimensioned footprint on the site, a section, and a reconciled floor schedule. Clearly identify every constraint still untested." — row text verbatim.
 - The first building option is now placed on the lot (placement.status "placed", basis printed_tax_map, outline 100.76 x 66.66) with its reconciled floor schedule: floor_schedule is 3 storeys at 6716.6667 summing to 20,150 and 3 floor plates at the same plate — C-4 holds (3 x 6716.6667 = 20,150); the QA mutation dropping a floor-by-floor row raised plates_rows_mismatch, proving the reconciliation is pinned.
 - Untested constraints are named: placement.not_checked lists the physical floor plate, walls/rooms/core/stairs/elevators, parking/loading/bicycle, whole-lot coverage, street wall/setback, and the survey/zoning-lot; the alt fit_note states it checks coverage only.
 - OPEN for later work: the DIMENSIONED footprint drawn on the site plan and the section drawing are M5-T173 part B (the evidence map and packet path_notes assign them there; page-4 site plan still legends "No building placed"); this task delivers the scenario's computed placement + reconciled schedule + untested-constraint naming only.

ROW D-094-R091 — PASS (this task's data share)
 - Source matches: source-003-amendment.md line 26 "Use one explicitly stated percentage from the existing 60–75% assumption. Keep the drawing and calculations consistent, and show the assumed percentage beside it." — row text verbatim.
 - One stated percentage: benchmark area_allocation.share = 0.6 (apartment 12,090.0, other 8,060.0, total 20,150.0); calc-area-allocation.md states "the 0.60 apartment-area share is a preliminary assumption chosen by the owner (the low end of a 0.60-0.75 range), not law" — one explicit percentage from the existing 60-75% assumption.
 - Drawing and calculation agree by construction: apartment = share x total (12090 = 20150 x 0.60 exactly, 12090/20150 = 0.6), and results_way_rules.py enforces allocation_share_mismatch (apartment must equal round2(total x share) within rounding, DB-248); the QA/G3 beyond-rounding mutation proved only this rule fires.
 - OPEN for later work: the DRAWN two-zone illustration (where the drawing's proportions are visibly shown and the percentage sits beside the figure) is M5-T173 part B; the appendix method here is honestly future-tensed ("not yet drawn in this report; when drawn it will be shown as zones...").

ROW D-094-R092 — PASS (this task's data share)
 - Source matches: source-003-amendment.md line 27 "Check that the estimate and drawing use compatible area measurements. Do not automatically treat zoning floor area as the physical floorplate area." — row text verbatim.
 - Compatible measures: both placement.measure and area_allocation.measure are "residential_floor_area"; each carries conversion_statement "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked"; the printed appendix repeats "The plate measure is stated as: plate = zoning floor area per storey; no gross-up...".
 - Zoning floor area is NOT presented as the physical plate: placement.not_checked explicitly lists "the physical floor plate (gross-up, exclusions, wall thickness)"; calc-area-allocation.md states the residential floor area is the zoning floor area and "no physical floor plate ... is worked."
 - Nothing material stays open for this task; a future drawn plate (M5-T173) must keep the measures compatible and labelled.

(3) BINDING B1–B5
 - B1 PASS: at the frozen head all five rows carry M5-T172 in applicability.task_ids (R044, R058, R082, R091, R092), and each row's text equals the owner's verbatim source quote (no row text changed by this task; the binding appended task_ids only).
 - B2 PASS: `python3 tools/validate_directive_compliance.py --check` run once in w-wave20 at the frozen head exited 0 (quiet on success), confirming the requirements digest / manifest consistency and c14; I re-read `git log -1` (head stable) — not a transient mismatch.
 - B3 PASS: verification.json has exactly one M5-T172 task_verifications row (index 36) with applicable_requirement_ids = the five ids, every requirement state "pending", verifier "" (empty), reviewed_sha null — the correct pre-DCV state.
 - B4 PASS: reg.load().evaluate_task_refs(M5-T172 packet) returns ok=True, applicable_ids == cited_ids == the five ids, missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS: the derived applicable set equals exactly the five cited ids with missing_ids empty, so no other active-directive requirement is applicable-but-uncited for this task. Gates: G0 PASS (orchestrator, 53d98589 = scope-correction-3 head), G1 PASS (data-contract-verifier), G2 PASS (orchestrator), G3 PASS (code-reviewer), G4 PASS (qa-engineer) — G1-G4 all recorded at one content identity 5994e220; manifest.affected_tasks contains M5-T172. CI run 38779490023 at 5994e220 = 21/21 jobs success (I read the job conclusions directly).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: (blob predicate) the packet's allowed-path files keep their blob ids at the stamping head, and the five rows' text and their M5-T172 applicability binding are unchanged; AND (broad disjoint-peer tolerance) later commits may touch any other file — other wave-28 tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, new rows appended to D-094, ledger state — plus this task's own acceptance records (verification.json M5-T172 row, gate/report/state writes) and a merge of main that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None. The verdict is PASS for all five rows' shares. Non-blocking observations for the orchestrator: (a) the frozen-head CI run 38781282159 was still in_progress at review time — it runs on a project-control-only delta, but read it green before accept (D-090 R639); (b) research_record_check reports NB-04 code_current=False — pre-existing DB-283 (NB-04 stale vs close_frame_dimensions.py, not edited here), reported-not-failed, correctly left unrevised; (c) the G3 gate JSON names only code-reviewer — the visual-quality-reviewer's G3 PASS (round-2 FAIL closed, round-3 PASS) is captured in M5-T172-reviews.md and I confirmed both visual findings closed on the real print, but there is no separate G3-visual gate record; (d) G1 observation O1 (drawn plates on the GIS basis vs placement.outline on the tax-map basis, each labelled, never mixed, within the 0.5 sq ft reconciliation) is a legitimate carry-forward note, not a defect.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full services/api pytest and web vitest regressions (forbidden: test_directive_compliance.py and the full api suite) — I relied on CI run 38779490023 (21/21 success) at the production content identity, not a self-run suite.
 - The rendered PDF pixel layout / A4 bounds — I read the orchestrator-captured print-5994e220 HTML/text (byte-identical production), not a self-generated print; I started no server and touched no ports.
 - Professional/legal correctness of the zoning readings (ADR-007 — AI review only).
 - The Part-A modules placement.py and area_allocation.py internals (forbidden, consumed read-only) — I verified their OUTPUTS equal the settled reading placement-building-b.json (plate 6716.67; footprint 6716.66; 33.34/35.31/3.12; 12090/8060 at share 0.60), not their source.
 - modularity_check.py --check I did not re-run — reviewers report three_way_document.py at 704 SLOC under the 750 justify line (S9/S12); not a D-094 row obligation.
END-OF-REPORT
```
