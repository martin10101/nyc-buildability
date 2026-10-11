# M5-T164 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `2c180d0a4104a0ba75cf8bd05b62b7ec390a20a9` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R017, R026, R044, R058, R079, R082, R091, R092, R094, R096.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No REQUIRED/blocking finding at the frozen head. Non-blocking observations for later work (orchestrator/backlog, not corrections to this task): (a) R091 — the contract does not enforce apartment_area/total == share (only apartment+other=total); consider a future way-rule. (b) R096/R044 — the web reader guard does not enforce additionalProperties:false (server-side schema does; disclosed in the evidence-map known limits and G1-A3/G3-A3/G4-ADV-1). (c) no positive fixture yet for geometry.floor_plates.entries[].building (reverse binding is present and fires; G1-A1/G4-ADV-2; add when an engine emits tagged plates). (d) both Python validators word a 1.5.0 way breach with the fixed 1.3.0 prose (breach detail correct; strings live outside this task's files; G4-ADV-3). (e) PROVENANCE PROCESS FLAG (not a D-094 issue): commit 6dde13459's co-author trailer reads "Claude Opus 5.5"; per D-085 the builder subagent should be Opus 4.8 — the orchestrator/G1 note the transcript shows 4.8; I could not inspect the subagent transcript to confirm.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 22:43 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T164 (directive D-094, 10 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only evidence check, NOT a human or professional review. I produced none of the work and reproduced every item below from primary evidence (source files, schema, code, fixtures, a focused test run, git objects, CI). The producer's evidence map, reviews and report were treated as claims to reproduce.

(1) HEAD VERIFIED
 - Frozen head 2c180d0a4104a0ba75cf8bd05b62b7ec390a20a9 exists on task/wave24-report-v3 in /root/project/w-wave20 and is an ancestor of the live HEAD 6639a7b1 (peer wave tasks have since committed, as the brief anticipated); I read everything through git plumbing at 2c180d0a.
 - The SHA chain checks out: contract head fc96fd9c, claim head aac892fc, material head 6dde13459 (cherry-pick of builder 3c3f5a10), base main b4704161.
 - All 22 allowed-path files AND the test's import dependencies (study_contracts.py, three_answers/contract.py, preliminary_apartment_estimate.py, tools/research_record_check.py) are byte-identical (same git blob ids) across material 6dde13459, frozen 2c180d0a, and live 6639a7b1 — so a run at the live checkout reflects the frozen content exactly.
 - This is a contract-shapes-only task (results contract 1.5.0, additive/optional). Each row below is judged for THIS TASK'S SHARE: whether the contract shape correctly supports the owner's obligation without overstating resolution. Downstream engine/page/report work remains open per row.

(2) ROWS

ROW D-094-R017 — PASS
 - $defs.constraint_line is a oneOf by state: the "established" branch REQUIRES "geometry" (line or polygon); the "not_established"/"not_known" branch has no geometry property with additionalProperties:false — geometry only when established. Each item carries kind, state, basis (quantity_basis) and zr_sections.
 - Reproduced in the valid fixture synthetic_rear_yard_constraints_contract_1_5_0.json: rear_yard_100ft_line=established (carries geometry), corner_area=not_known (no geometry); envelope_row has an identical not_known-carries-no-values branch.
 - NB-06 (read) is interpretation_awaiting_review and NB-03 is awaiting review, so the unresolved basis is preserved by the not_known/not_established states; the contract never forces a drawn yard/setback.
 - Open: the drawing/report that actually renders only established geometry is M5-T166 and later page tasks.

ROW D-094-R026 — PASS
 - $defs.input_fact requires key, value, unit, basis, source_title, source_date; rear_yard_check and envelope_row applies/not_applicable branches carry inputs (name, value, unit, basis), conditions, text and zr_sections — the fields a worked calculation with real source identifiers and dates needs.
 - Reproduced: the valid fixture's input_facts carry distinct bases with title+date (lot_frontage/printed_tax_map "NYC DOF Digital Tax Map, 2021-07-29"; recorded_lot_area/administrative_record; outline_lot_area/gis "MapPLUTO 26v2").
 - The invalid fixture synthetic_input_fact_basis_unknown (basis "tax_map") is rejected by both Python validators (reproduced; test passed).
 - Open: the actual page-8 evidence rework (compact section references, worked calculations, renaming) is M0-T193 and later report tasks.

ROW D-094-R044 — PASS
 - The contract forbids invented geometry in three places: a withheld building_placement has no outline property (additionalProperties:false); a not_known rear_yard_check has no inputs property (no number); area_allocation has additionalProperties:false with no zone-geometry/unit-count/core keys.
 - Reproduced: invalid fixtures synthetic_withheld_placement_with_outline, synthetic_withheld_check_with_number and synthetic_allocation_zone_geometry (extra "zones" key) are each rejected by validate_contracts and both Python validators; the focused test (71 passed) proves each becomes valid only when the single defect is removed.
 - Open: this row is shared with M5-T166 (the drawing task); the contract-level prohibition is in force now.

ROW D-094-R058 — PASS (this task's share)
 - The contract keeps the five categories as distinct, separately labelled blocks: allowance (floor_area_allowance answer), scheduled (building_alternatives), illustrative site-fit (building_placement with const label "Illustrative"), preliminary apartment estimate (area_allocation with const label "Illustrative"), and the legal unit limit as its own answer.
 - A way rule keeps "demonstrated site fit" distinct from the estimate: area_allocation.fitted may be true only when placement.status=="placed", and apartment+other must equal total (results_way_rules._building_alternative_violations; mirrored in the web checks). Reproduced via S12 tests and the pure-rule assertions (test passed).
 - Open: the harness itself — verifying that each result and diagram comes from the SAME result revision/scenario across the full report, and that an architect can tell the five apart — is report/export work (the row is also bound to M5-T162); this contract task only makes the categories distinguishable.

ROW D-094-R079 — PASS (this task's share)
 - $defs.rear_yard.checks items use provision enum exactly ["23-344(a)","23-344(b)","23-344(c)(3)"]; an applies/not_applicable check may carry inputs, a not_known check carries none and no number; combined.way ∈ {settled, conditional, withheld}. This gives an explicit, per-provision applicability slot for 23-344(b) beside the corner test, and lets it stay unresolved.
 - Reproduced: the valid fixture carries all three provisions — 23-344(a)=not_applicable, 23-344(b)=applies, 23-344(c)(3)=not_known — with combined way=conditional.
 - I read NB-03 (revision 2): research_status=interpretation_awaiting_review, a CONDITIONAL no-rear-yard reading under 23-344(b) with 23-344(c)(3) pending; the contract's enum and not_known/conditional states match the record and do NOT present the exemption as established.
 - Open: the actual applicability reading, the engine that emits it, the page-6/item-4 rewrite and NB-03's independent human-free review are M5-T163/M5-T165/M5-T176 and later; the contract performs no legal determination itself.

ROW D-094-R082 — PASS (this task's share)
 - $defs.building_placement carries status, const label "Illustrative", outline only in the "placed" branch, method, basis, measure, conversion_statement, conditions, checks and not_checked (the slot that names every untested constraint); $defs.envelope_row carries setback/street_wall/side_yard rows. These are the contract pieces of one worked scenario.
 - Reproduced: synthetic_placed_building_contract_1_5_0.json has a placed placement with an outline; the rear-yard fixture carries envelope_rows (setback applies, street_wall applies, side_yard not_known). Test passed; validate_contracts exit 0.
 - Open: ACTUALLY finishing one meaningful scenario — a dimensioned footprint fitted to the site, a section, and a reconciled floor schedule — is engine/drawing/page work in later waves; this task supplies only the shape to carry it (incl. not_checked for untested constraints).

ROW D-094-R091 — PASS (this task's share)
 - $defs.area_allocation has a single "share" number with minimum 0.6 and maximum 0.75, plus apartment_area_sqft, other_area_sqft and total_sqft; a way rule enforces apartment+other=total within display rounding.
 - Reproduced: invalid synthetic_allocation_share_out_of_range (0.90) is rejected; boundary behaviour confirmed (G4 probes 0.5999/0.7501 REJECT, 0.60/0.75 ACCEPT); the placed fixture uses share=0.70 with apartment 13300 + other 5700 = total 19000 (0.70 exactly). Test passed.
 - Open: rendering the percentage beside the drawing is later page work. OBSERVATION (not a required correction): the contract enforces apartment+other=total but does NOT enforce apartment_area/total == share, so share-vs-split consistency is left to the emitter; a future way-rule could tie them. The row's shape (ONE bounded share + the three areas + the sum rule) is satisfied.

ROW D-094-R092 — PASS (this task's share)
 - $defs.area_measure is const "residential_floor_area" (the preliminary estimate's own measure) and $defs.plate_conversion_statement is const "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked"; both are required on area_allocation and placement, so zoning floor area is never taken as the physical plate without an explicit conversion.
 - Reproduced: invalid synthetic_allocation_without_measure is rejected; the const measure/conversion are enforced byte-exact. Test passed.
 - I read NB-04: research_status=conflicting_evidence, with lot-70 area recorded as 10075 (administrative_record) vs 10387.99 (gis outline); the contract's input_fact.basis closed enum preserves which basis each figure is, matching the record's "never equate recorded with GIS outline".
 - Open: integrating the estimate and the drawing on compatible measures in the actual pages is later work; the contract forces the measure + conversion statement.

ROW D-094-R094 — PASS (this task's share)
 - $defs.area_allocation has a "fitted" boolean; the way rule in results_way_rules.py (and the web checkAreaAllocation) refuses fitted=true unless the same building's placement.status=="placed" — zones go inside a footprint only after one is fitted.
 - Reproduced: S12 fitted-without-placed is accepted by the bare schema (cross-key, non-expressible) but flagged by results_way_violations as allocation_fitted_without_placement and rejected by BOTH Python validators; version-gated (a 1.2.0 copy yields no violation). G4's mutation proof M2 (removing 1.5.0 from the way-layer set) flips it. Test passed.
 - Open: the "proportional bar beside the diagram until fitted" rendering is page work; the contract carries the fitted flag to drive it.

ROW D-094-R096 — PASS (this task's share)
 - Both version sets gain 1.5.0: services/api results_way_rules.CONTRACT_VERSIONS_WITH_WAY_LAYER = {1.3.0,1.4.0,1.5.0} and web SUPPORTED_RESULTS_CONTRACT_VERSIONS = ["1.3.0","1.4.0","1.5.0"]; the web checkPlacement/checkAreaAllocation mirror the server's placement and area-allocation rules (label, share range, measure, conversion, fitted-requires-placed, apartment+other=total).
 - Reproduced: grep of both files confirms 1.5.0; the web test and S11/S12 web probes pass; focused test passed; both schema copies are byte-identical (CI contracts-schema-bundle green) and results.ts is regenerated (CI contracts-typegen green).
 - Open: the actual website/PDF RENDERING of the illustration is later page/export work. OBSERVATION (disclosed, not a required correction): the web reader guard does not enforce additionalProperties:false, so an extra key (e.g. "zones") passes the client but is rejected server-side; the illustration RULES themselves are mirrored on both outputs.

(3) BINDING B1–B5
 - B1 PASS: contract commit fc96fd9c appended "M5-T164" to exactly these 10 rows' applicability.task_ids (10 "+M5-T164" additions, no "+\"text\"" line; the "-D-094-BOOTSTRAP" lines are JSON comma reflow). No row text changed; the material commit 6dde13459 touches no directive/requirements file (22 files, all allowed-path). Row text is byte-identical frozen vs live for all 10 rows.
 - B2 PASS: tools/validate_directive_compliance.py --check exits 0 (VALID) at the live head — the c14 digest resync (requirements_id/content_digest in each manifest) holds for every directive; CI's control-plane job is green at the frozen head.
 - B3 PASS: D-094 verification.json has exactly one M5-T164 row (schema directive_verification/v2) with the 10 ids, producer=backend-engineer, verifier="" (empty), reviewed_sha=null, all 10 requirements state=pending — at both the frozen head and the live head.
 - B4 PASS: the packet cites exactly the 10 ids; a scan of ALL directives shows the set of rows listing M5-T164 in applicability.task_ids equals the cited set (applicable == cited; neither excess nor shortfall).
 - B5 PASS: no other row across the active directives names M5-T164 uncited (applicable − cited is empty). Gate records: G0 PASS (orchestrator) at contract head fc96fd9c; G1 PASS (data-contract-verifier), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer, fresh reviewer) all at submit head 13146a67 with ONE shared content_manifest_sha256 e2eed13f… (reviews pinned at material head 6dde1345; the task files are byte-identical across those heads). CI "CI" run 38180383941 at the frozen head 2c180d0a = 21/21 jobs success (api, contracts, contracts-typegen byte-identical, contracts-schema-bundle, control-plane, web, web-e2e, modularity, validation-suite, …).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while BOTH hold:
 - Blob-level predicate: the 22 allowed-path files of M5-T164 keep the git blob ids they have at 6dde13459/2c180d0a (verified identical through live 6639a7b1); AND the 10 rows' text and their "M5-T164" applicability binding are unchanged; AND the M5-T164 verification.json row stays producer=backend-engineer / verifier="" / all requirements pending until this verdict is recorded.
 - Broad disjoint-peer tolerance: later commits may touch ANY other file — other tasks' source under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports, the directive bindings/verification rows of OTHER tasks, and ledger state.json — plus this task's own acceptance records and a merge of main that changes none of the predicate's files. Such commits do not void this verdict.

(5) REQUIRED CORRECTIONS
 - None. No REQUIRED/blocking finding at the frozen head. Non-blocking observations for later work (orchestrator/backlog, not corrections to this task): (a) R091 — the contract does not enforce apartment_area/total == share (only apartment+other=total); consider a future way-rule. (b) R096/R044 — the web reader guard does not enforce additionalProperties:false (server-side schema does; disclosed in the evidence-map known limits and G1-A3/G3-A3/G4-ADV-1). (c) no positive fixture yet for geometry.floor_plates.entries[].building (reverse binding is present and fires; G1-A1/G4-ADV-2; add when an engine emits tagged plates). (d) both Python validators word a 1.5.0 way breach with the fixed 1.3.0 prose (breach detail correct; strings live outside this task's files; G4-ADV-3). (e) PROVENANCE PROCESS FLAG (not a D-094 issue): commit 6dde13459's co-author trailer reads "Claude Opus 5.5"; per D-085 the builder subagent should be Opus 4.8 — the orchestrator/G1 note the transcript shows 4.8; I could not inspect the subagent transcript to confirm.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Web vitest/TypeScript: I did not run npm/vitest (avoided heavy install and ports 3000/3001/8000 per the brief); I verified the web checks by reading the diff (they mirror the schema + Python way rules) and confirmed the CI web + web-e2e jobs are green at the frozen head; G4 ran its own web probes.
 - SVG/DXF snapshots were not regenerated from the renderer; their consuming suites (tests/drawings/kit, tests/cad) are green in the frozen-head CI, so the committed snapshots are self-consistent with the pinned renderer.
 - modularity_check.py --check: not run by me (needs git ls-files); the CI modularity job is green at the frozen head and G3 reported exit 0.
 - The full services/api pytest (2548) is forbidden to me; the CI "api" job is green at the frozen head (D-090-R639 is the accept-time read).
 - The LEGAL reading of ZR 23-344(b)/(c)(3), 23-431/23-433 and the NB-03/NB-04/NB-06 interpretations: these records are interpretation_awaiting_review / conflicting_evidence and are not settled; verifying the law itself is out of scope for a contract-shapes task and beyond an AI agent (no professional review).
 - Byte-exactness of the conversion_statement/measure const against the docs/design-contract R092 wording: docs/ is a forbidden/unchanged path for this task; I confirmed the const is enforced and a document missing it is rejected, but did not diff it against the design contract prose.

END-OF-REPORT
```
