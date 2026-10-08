# M5-T136 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `99044e56aa6006443b04d97e542fc85eebc01026` (branch `task/wave9-emit-three-way-document`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R228, R229, R240, R255, R257, R258, R267, R268, R269, R543, R556, R567, R568, R569, R570, R583, R584, R588.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 08:43 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T136 (directive D-090, eighteen rows)
VERDICT: PASS

I am an AI agent (the independent, read-only directive-compliance verifier). This is NOT a human or professional review. I produced none of this work or its records; I decided each row from primary evidence (the committed fixture, the module/adapter source, the website reader, the focused tests I re-ran, the git objects, the registry), treating the producer report, the evidence map, the gate records and my brief as unverified claims. For each row I judge only THIS task's share; every row stays open in the registry for the later pieces (the route, the website display, the exports, the PDF, the estimator).

(1) HEAD VERIFIED
 - `git -C /root/project/rv-w6-a rev-parse HEAD` = 99044e56aa6006443b04d97e542fc85eebc01026, clean tree, branch task/wave9-emit-three-way-document; it branched from 1adaf7f4 (candidate/D-024-mrl-option-b).
 - The material commit 8ad287f5 is one builder commit of 22 files, all inside allowed_paths; from the claim-seam head 99647cb6 to the frozen head the only non-allowed-path changes are project-control/** and docs/DISCOVERY_BACKLOG.md (ledger/integration). Read-only production files (engine.py, dwelling_units.py, geometry.py, answers.py, building_option.py, the decision modules except the adapter, all schemas/copies/generated types) do not appear in the diff.
 - `python tools/validate_directive_compliance.py --check` exit 0 (direct). `pytest -q tests/scenario/three_answers tests/journey` = 326 passed, 2 skipped, exit 0 (three_answers 324 + journey). `tools/modularity_check.py --check` exit 0 (three_way_document.py 370 SLOC; warnings only on pre-existing tools/agent_supervisor files).

(2) ROWS
ROW D-090-R228 — PASS
 - The DXF and site-plan snapshots of the journey lot are regenerated from the one fixture and the massing snapshot is deleted (diff: `M` .../results_dxf/...dxf, `M` ...site_plan.svg, `D` ...massing.svg); a raw scan of the fixture finds "not required"/"not_required"/"No rear yard" = 0 occurrences, so the drawing note follows the withheld rear yard.
 - test_s4 asserts `yards["reason"] == rear["reason"]` and `"not_required" not in json.dumps(yards)`; the G3 reviewer check 9 confirmed the DXF holds no envelope/yard/plate layer and no other saved file changed.
 - This task's share is the emitted document plus its saved drawings agreeing with the one result; the website display and the PDF are later pieces and the row stays open for them.

ROW D-090-R229 — PASS
 - In the fixture every withheld result is a value_states entry with a reason and no number, and a result-number scan finds 29.0 (unit figure) and a coverage 100 absent; unit_estimate is not_available ("Not known…"), floor_stack/shortfall/best_combination not_available, floor_by_floor [].
 - test_s11 asserts `0.0 not in _all_result_numbers(no_profile.document)` and test_s20 asserts `_all_result_numbers(doc) == []` with the engine off; G3 check 8 confirmed no profile yields no zero.
 - Share covers the emitted document, drawings and reader; the PDF presentation of "not known" stays open.

ROW D-090-R240 — PASS
 - test_s11 (no site geometry) shows only reach-dependent coverage withheld while max_residential_floor_area stays conditional; with no profile every answer is not_available, never filled by a default.
 - The fixture's remaining_floor_area is `{status not_available, reason "Needs verified zoning-lot boundaries…", reason_kind missing_input}` — an unanswered input stays unanswered, not defaulted.
 - Share is the emission; the screen/PDF handling of unanswered inputs is later and the row stays open.

ROW D-090-R255 — PASS
 - test_s8 asserts: with the user density statement legal_unit_limit_standard is `conditional` with a `user_statement` condition and the text "as the user states"; without it `withheld`; a contradicting statement sets `held_back` and the limit stays withheld.
 - test_s19 shows the shown limit (16) only appears with the statement and "16 appears nowhere" without it; G3 check 7/8 reproduced this on its own interior-lot script.
 - Share is the document's conditional-vs-verified distinction; storing/showing user assumptions on screen stays for the display piece.

ROW D-090-R257 — PASS
 - The fixture's four floor-area value_states each carry a first condition of kind `contradicted_record` naming the recorded 10,075 sq ft vs the tax-map 10,387.99 sq ft, settled_by "A survey, or deed dimensions"; neither figure is chosen automatically.
 - test_s7 asserts "recorded lot area of 10,075 sq ft" is in the assumptions; G3 check 5 confirmed the conditions name the disagreeing areas.
 - Share is the document; which area applies is left unsettled and stays open.

ROW D-090-R258 — PASS
 - The fixture unit_estimate reason = "Not known. The Preliminary capacity estimate (a practical estimate of how many apartments might fit) is not built yet." — owed work said as owed work; raw scan "unsupported" = 0 occurrences.
 - reason_kind is `rule_not_implemented` (a calculation not built), kept distinct from a missing lot fact; test_s6 and the transform text guard forbid "unsupported".
 - Share is the reserved block's wording; building the estimator is later work (on record as owed) and the row stays open.

ROW D-090-R267 — PASS
 - Every shown benchmark value is `conditional` with an `unchecked_condition` (the K20 items); no value is settled when a condition is unchecked; raw scan "professional review" = 0.
 - test_s7/test_s9/test_s10 pin that a value is settled only when conditions are supplied checked-and-absent, else conditional; G4 mutation (h) catches writing settled where the module says conditional.
 - Share is the emitted document's conditional labelling; the screen/PDF disclaimer wording stays open.

ROW D-090-R268 — PASS
 - The fixture keeps floor-area (far 2.0/2.4, area 20150/24180) and six heights visible as conditional, and withholds coverage, rear_yard, setback_above_base, the building_option (answer not_available, values []) and all three unit limits.
 - test_s1/test_s3 assert this placement; G3 checks 3 and 5 confirmed the shown figures equal real-lot.json rows L1–L4 and each withheld result carries its reason.
 - Share is the one document; the row stays open for the display of these states.

ROW D-090-R269 — PASS
 - The six height values are conditional (`unchecked_condition`) and the phrase "the maximum for this property" = 0 occurrences in the fixture and in the transform's authored texts.
 - Shown heights 30/45/55 (standard) and 30/45/65 (qualifying) match real-lot.json; test_s7 asserts the no-"maximum" invariant; G3 check 5 confirmed.
 - Share is the emission; the confirmed-maximum claim depends on height rules not yet built and the row stays open.

ROW D-090-R543 — PASS
 - The fixture unit_estimate reason begins "Not known" and names the "Preliminary capacity estimate", the owner's two exact labels; test_s6 asserts `reason.startswith("Not known")` and "Preliminary capacity estimate" in the reason.
 - The "then label it Preliminary capacity estimate" half (once an option has floors and a shape) belongs to the estimator, which is not built here.
 - Share is the "Not known" reserved state; the estimate-with-floors label stays open for the estimator piece.

ROW D-090-R556 — PASS
 - apps/web/src/lib/architect/three-answers.ts answerView builds the headline from the withheld value_states entry when the headline key is withheld (kind "withheld", its reason), and falls back to values[0] ONLY when the key is in neither list (legacy 1.0.0 docs); a withheld non-headline key is listed as its reason, never a number.
 - three-answers.test.ts "S14 RED PROOF: a withheld HEADLINE key is shown as its reason, never the first value (R556)" and the panel/journey tests assert this over the globbed fixtures (results-fixtures.ts) and the journey fixture; G3 check 10 confirmed the reader never substitutes.
 - Share is the reader and the answer card; the full results display is a later piece and the row stays open.

ROW D-090-R567 — PASS
 - In the fixture rear_yard and setback_above_base are value_states of permitted_envelope ONLY; legal_unit_limit_standard/_qualifying_affordable/_qualifying_senior are value_states of floor_area_allowance ONLY; none of the five is in any values[] (all withheld on this lot).
 - test_s2 asserts exactly this placement and the owner's decision "as recommended"; G3 check 4 confirmed it independently.
 - This decision is fully realised in the document here; the same placement on screen/exports stays bound for later.

ROW D-090-R568 — PASS
 - The emitted unit_estimate carries no value, no formula, no factor (fixture shows only status/reason/reason_kind); test_s6 asserts the exact three-key shape and `"gap_kind" not in ue`.
 - test_s19 shows the standard legal limit, when shown, is a value of floor_area_allowance while unit_estimate stays reserved; test_s16 pins that nothing but the adapter reads the engine's inner block (which still holds 29).
 - Share is the reserved emitted block; the row stays open until the estimator fills it.

ROW D-090-R569 — PASS
 - In the document a legal limit is a floor-area value (key legal_unit_limit_standard, unit dwelling_units, its own label/sources) and the estimate block holds no count: the two never share a place or label; test_s19 + test_s6 pin both sides.
 - G3 check 7 confirmed the shown limit is one value labelled as the legal dwelling-unit limit with its formula while the estimate block holds no count.
 - Share is the document; the on-screen and in-export labelling is the display/PDF piece's and the row stays open.

ROW D-090-R570 — PASS
 - A whole-document result-number scan finds no withheld result's number (coverage 100, unit 29, floor plate 10075 absent as results; 10,075 appears only inside a conditional recorded-area assumption, an input fact); test_s5 asserts 10075.0/29.0/100.0 not in _all_result_numbers with per-block red proofs, and test_s15 shows the merged validator refuses a shown value marked withheld and a withheld entry carrying a number.
 - The saved drawings draw no withheld geometry and the reader shows a withheld value as its reason (row R556 tests); G4 checks 3–4 reproduced thirteen mutations, each re-insertion caught.
 - Share is the document, drawings and reader; carrying the ban into the screen and exports stays open.

ROW D-090-R583 — PASS
 - The emitting piece was built under the normal gates: G0 PASS (orchestrator), G2 PASS (self_check, orchestrator), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer); producer scenario-optimization-engineer differs from both reviewers and the reviewers differ from each other.
 - G2, G3 and G4 all carry one content identity `content_manifest_sha256 = 3ba6d1b2b9281480ec275947894c418eda5085e94488e9ccf1b363e8013ad6ca`; the reviews were performed at 4ab2238b (review record) and recorded at the live head 4cdb8d20, and the 22 material blobs are byte-identical from 8ad287f5 to the frozen head, so the record tells it truly (no review failed; one S4 scope correction before the reviews, both reviewers judged it).
 - The companion "connect the results display" piece authorised by the same row is separate and stays open.

ROW D-090-R584 — PASS
 - The diff touches nothing under services/api/app/api, app/main.py, app/config.py, render.yaml or .github; no production switch or route is added.
 - test_s16 asserts engine.py contains no "result_way", the engine's inner document still declares 1.2.0, and the sole generate_results caller under app is result_way_engine_bridge.py; G3 checks 1 and 12 confirmed.
 - The hold is an ongoing restriction honoured here; it stays bound for every later piece.

ROW D-090-R588 — PASS
 - Nothing is narrowed: every withheld result stays in the document as "not known" with its reason and resolver, all six addon_gains and both answers remain present, and the estimate block is kept for the estimate.
 - What stays owed is on record: docs/DISCOVERY_BACKLOG.md rows DB-196 (contract has no home for a formula field / conditional-block ways / estimate gap_kind, OPEN) and DB-198 (a withheld result names only its first standing reason, OPEN).
 - This is a standing scope obligation; the full report and all options stay owed across the later pieces and the row stays open.

(3) BINDING B1–B5
 - B1 — CONFIRMED. Between 1adaf7f4 and the frozen head the D-090 requirements.json appends exactly "M5-T136" to applicability.task_ids for all eighteen rows and changes no row text and no other field (verified field-by-field); the same diff appends new rows R591–R625 (contiguous, 35 rows) and none of them is bound to M5-T136; exactly eighteen rows carry M5-T136 at head.
 - B2 — CONFIRMED. directive_registry.sha256_text_artifact(requirements.json) = 02515371ff6197baaf62de915e590ba220989558888a01b51cfb0c6c8826b360 equals the manifest's requirements_content_digest_sha256; the manifest audit_log has the dated applicability_bound entry naming M5-T136, the eighteen rows, the digest resync and the provisional verification row, in one action.
 - B3 — CONFIRMED. verification.json has exactly one M5-T136 row (schema directive_verification/v2), applicable_requirement_ids == the eighteen, verifier "", reviewed_sha null, and each of the eighteen requirement rows state "pending" with empty evidence.
 - B4/B5 — CONFIRMED. reg.evaluate_task_refs(M5-T136 packet) over the live registry returns ok=True, applicable == cited == the eighteen, missing_ids [], invalid_refs [], unresolved []; across all active directives nothing else is applicable-and-uncited. Gate records G0/G2/G3/G4 are all PASS and G2/G3/G4 share the one content_manifest_sha256 above.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while a blob-level predicate holds: the task's 28 allowed-path files keep the exact blob ids they have at the frozen head (and the deleted massing.svg stays absent); engine.py, dwelling_units.py, geometry.py, answers.py, building_option.py and every other file under services/api/app/scenario/three_answers except the adapter and the new transform, everything under packages/contracts/schemas, services/api/app/_contract_schemas, packages/contracts/generated and docs/reference-cases stay byte-identical; and the text of the eighteen rows and their binding to M5-T136 stay unchanged.
 - Tolerated later commits: commits that touch only project-control/** and docs/DISCOVERY_BACKLOG.md; and a merge of the integration branch that changes none of the predicate's files. Any change to the transform, adapter, tests, fixture, snapshots, web reader/card/tests, the register, or any predicate file voids this verdict and requires re-review.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The web checks (npm lint/typecheck/unit tests/build and the 153 e2e/browser tests): my copy has no node install and the brief forbids the heavy runs, so I verified the reader source and the named website test assertions by reading them but could not reproduce the green run; I rely on the reviewers' and orchestrator's recorded output (web-checks-4ab2238b.out).
 - The full api suite (8562 passed / 8 skipped) and the cad/drawings suites (1359 passed / 6 skipped): forbidden/heavy; I ran only tests/scenario/three_answers + tests/journey (326 passed, 2 skipped). DXF/site-plan correctness rests on snapshot equality plus the producer's line-by-line review, not an independent oracle (G4 acknowledged this).
 - I confirmed the asserted expected numbers exist in the reference cases (real-lot, corner-reach, interior-lots) but did not re-derive the zoning math from first principles; the reference figures' correctness is an earlier-task concern.
 - I did not re-trigger CI on the pushed head, nor re-run the G4 thirteen mutations; I reproduced the per-block red-proof structure from the test source instead.
END-OF-REPORT
```
