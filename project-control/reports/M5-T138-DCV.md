# M5-T138 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `f0b20febc004d4d5395350ad047210dae1b8e39e` (branch `task/wave11-results-route`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R167, R213, R228, R229, R240, R255, R256, R257, R258, R263, R267, R268, R269, R292, R570, R582, R584, R588.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 13:30 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T138 (directive D-090, eighteen rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an automated, independent machine review, NOT a human or professional/legal review. I produced none of the code and none of the records; I treated every producer report, evidence map, gate record and my brief as unverified claims and decided each item from primary evidence I reproduced myself.

(1) HEAD VERIFIED
 - `git -C /root/project/rv-w6-a rev-parse HEAD` = f0b20febc004d4d5395350ad047210dae1b8e39e, the frozen head; the task is awaiting_gate.
 - `git log 08b17a74..f0b20feb` shows the recorded arc: builder commit 9e0ba21b, seam a2e1faea (two scope corrections + backlog DB-203), correcting builder commit 6b60c9e2, seam f8c238f4 (reviews), post-review builder commit f0f67244, seam c3f58843 (deltas), f169eeca (six returns kept, evidence map, G2), 04e78331 (submit/G2), f0b20feb (G3/G4/G5). The ledger tells it truly.
 - Validator `python tools/validate_directive_compliance.py --check` DIRECT exit code 0. Focused tests 140 passed, exit 0: test_results_read_api 42, test_results_read_law_examples 13, test_study_live_outline_provider 3, test_build_info_api 70, test_result_ways 12.

(2) ROWS
ROW D-090-R167 — PASS
 - Concurrency record and task path_notes state "ONE PIECE, NO PARALLEL BUILDER"; the arc shows one backend-engineer building sequentially after M5-T137, not a swarm.
 - This piece is a single bounded route; the §B cap (3 writers + 4 reviewers) is unchanged.
 - Stays open: "build the whole program in full, one piece at a time" continues for every remaining R1–R12 piece; this row stays bound in the registry.
ROW D-090-R213 — PASS
 - This is the server half of "R6B results connected to the website," the first ordered step; it returns the one emitted results document for a lot (results_read.py:417).
 - M5-T136 (emit) and M5-T137 (evidence) are both accepted and in the base 08b17a74, so order is honoured.
 - Stays open: the website connection, then the report, then the PDF remain owed.
ROW D-090-R228 — PASS
 - The route returns emitted.document verbatim and adds/removes/changes no block; test_t3 proves the route body equals an independently built run_engine_and_result_ways_from_evidence document (blank-identity equality, "engine_result" absent).
 - It returns the single contract-1.3.0 document all downstream readers will share (one source of truth).
 - Stays open: the actual agreement of numbers across website, drawings and PDF cannot be shown until those consumers exist (Part B and later).
ROW D-090-R229 — PASS
 - No-zero scans assert `0.0 not in _result_numbers(doc)` on the recorded lot (test_t4:199), the interior lot and others; unknowns are withheld, never zeroed.
 - Missing evidence yields a withheld/named result or a typed 503, never a guessed number; test_t4_emitted confirms the inner 1.2.0 figures (29, 100) never leak.
 - Stays open: showing "not known" on the screen, drawings and PDF stays with later pieces.
ROW D-090-R240 — PASS
 - test_t7_fact_not_given_is_a_normal_200: a lot with no prepared outline returns 200, coverage and rear yard withheld and named, floor area still shown, no fact prefilled, no zero.
 - An absent floor_to_floor_ft is not silently filled: results_request.py:180 uses the stated default with a printed "stated default; editable" statement.
 - Stays open: the editable-input UI that lets the user leave inputs unanswered is Part B.
ROW D-090-R255 — PASS
 - results_request.py refuses any field beyond the three allowed with a typed 422; test_t10 drives 8 lot-fact fields (lot_area, lot_type, overlay, special_district, within_100_ft, geometry, provenance, bbl) and the provider is never reached.
 - The special_density_statement is carried as a statement to the entry only; test_t8 asserts it is never stored or returned as a fact and cannot override a recorded fact (unit limit stays withheld).
 - Stays open: evidence-sourcing of facts across the rest of the product stays bound to earlier/engine tasks.
ROW D-090-R256 — PASS
 - floor_to_floor_ft is a visible, editable starting value: present → basis "entered"; absent → stated default printed; test_s15 asserts the option's typical/ground height equals the body value or 10.0 and validates in a full study.
 - No hidden default: the only applied value is printed in the scope assumption (test_t6 shows the floor-to-floor statement changes when the input changes).
 - Stays open: the screen's editable control for this choice is Part B.
ROW D-090-R257 — PASS (narrow share)
 - The route does not auto-pick between conflicting area figures; it carries the engine's treatment, and test_t4 asserts floor area is shown "conditional" naming the recorded-area condition, not a single auto-chosen figure.
 - The decision/area-conflict logic itself is read-only here (evaluator_inputs.py, result_way_*.py byte-stable), so this task neither weakens nor resolves it.
 - Stays open: establishing which area measure applies, and the screen treatment, remain with the engine tasks and Part B.
ROW D-090-R258 — PASS
 - Owed work is kept distinct from missing data: backlog DB-203 records that a lot without geometry gets no result yet (owed engine change), and the business_reason keeps the full report/options owed.
 - Missing property data is answered as withheld/"not known"; it is never relabelled "unsupported=finished".
 - Stays open: the product-wide separation of missing-info vs unbuilt-feature continues across later pieces.
ROW D-090-R263 — PASS
 - No merge or security restriction is relaxed: INTERNAL_RESULTS_ENABLED defaults off, only an explicit true token enables (config.py `internal_results_enabled`; test_t1 non-true tokens stay 404), render.yaml and .github never name it, nothing under apps/ changed.
 - G5 security review confirms no new outbound call, secret or dependency and the same-or-stricter posture as the sibling route.
 - Stays open: nothing for this row's share; it stays a standing hold.
ROW D-090-R267 — PASS
 - test_t4 asserts the heights are the district limits shown "conditional", never "settled", and the blob contains neither "the maximum for this property" nor "professional review"; a disclaimer never turns not-checked into confirmed.
 - Unchecked K20 conditions keep the dependent results conditional or withheld, carried from the entry.
 - Stays open: the screen/PDF presentation of conditional labels is later work.
ROW D-090-R268 — PASS
 - test_t7: an answer the unknown reach cannot change (floor area 20150) stays visible while coverage and rear yard are withheld and named; test_t5 C2 shows a defensible conditional (coverage 100 percent, conditional) and C3 withholds.
 - Only unsupportable answers are withheld; the three-way document carries visible/conditional/withheld correctly.
 - Stays open: the screen rendering of this three-way treatment is Part B.
ROW D-090-R269 — PASS
 - test_t4 pins the R6B heights (30/45/55/65 ft) as the district's limits, "conditional", and asserts "the maximum for this property" never appears.
 - A base height is never shown as the confirmed property maximum.
 - Stays open: enforcing this across every other height rule and on the screen stays with the engine/display work.
ROW D-090-R292 — PASS (server share)
 - test_t6 proves one option is driven through the chain and a changed input updates exactly its dependents: a changed floor_to_floor changes the scope assumption only (law limits identical); lot area 5355 drives floor area 10710 and (with the statement) unit limit 16.
 - The option is built solely from the body (build_option) with neutral non-lot fields.
 - Stays open: "connected to the screen" is Part B; this task proves the input→result propagation at the document level only.
ROW D-090-R570 — PASS
 - Withheld stays withheld: test_s13-companion asserts `16.0 not in _result_numbers(doc)` when the unit limit is withheld; test_t4/_emitted assert 0.0 and 100.0 absent; the inner engine document is discarded (route returns only emitted.document).
 - No number, older value or substitute is put in a withheld slot anywhere in the returned document.
 - Stays open: the same discipline on screen and in exports stays with later pieces.
ROW D-090-R582 — PASS
 - Order honoured: M5-T136 (emit) and M5-T137 (evidence) are accepted and merged into the base; this "connect the results" server piece branched from that merged head, nothing built on unmerged work.
 - No handoff change was used to lighten any merge check.
 - Stays open: connecting the agreed results display comes next.
ROW D-090-R584 — PASS
 - All production switches stay off: INTERNAL_RESULTS_ENABLED defaults off (test_t11: build-info reports it False; render.yaml does not contain it), LANE_A/B/C and LIVE_SPATIAL stay off; no hidden feature is turned on.
 - G5 states plainly that if the switch were turned on as the code stands an unauthenticated caller could POST any BBL (no sign-in; blocker B-001), so the switch must stay off until auth lands — recorded as an owner fact, not code owed here.
 - Stays open: the row stays a standing activation hold.
ROW D-090-R588 — PASS
 - Nothing is dropped: the business_reason explicitly keeps the full report and every development option owed; this piece is the server route only.
 - The realistic estimate, options, shapes, comparison and PDF are named as later milestones and remain in scope.
 - Stays open: the full report and all promised options stay bound in the registry.

(3) BINDING B1–B5
 - B1 PASS: `git diff 08b17a74..f0b20feb` on requirements.json adds "M5-T138" to exactly 18 applicability.task_ids and changes no row text (the only other lines are the metadata updated_at and trailing-comma reformatting of each prior last element).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = c7d29e266ba81bfcf42ff5feb6dfd9497a7662335a32968d59b05f9cc764ded9 equals manifest.requirements_content_digest_sha256; the manifest audit_log has the 2026-10-08T11:40:32 applicability_bound entry naming the eighteen ids, digest resynced same commit, provisional verification row added.
 - B3 PASS: verification.json has one M5-T138 row (schema v2), applicable_requirement_ids exactly the eighteen, each requirement state "pending", verifier "" and reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(M5-T138) over the real registry = ok True, applicable == cited == the eighteen, missing/invalid/unresolved all empty.
 - B5 PASS: reg.derive_applicable across ALL active directives returns exactly the eighteen D-090 rows with zero unresolved; nothing else applies uncited. Gates G0, G2, G3, G4, G5 are all PASS; G2/G3/G4/G5 share one content_manifest_sha256 ae7ecbc76a2db0d51528f29eb2723df97deb3b384e973c3d239c4d7c5f078ca1 (G0 differs, the claim-seam contract head, as expected); reviewers are independent (G3 data-contract-verifier, G4 qa-engineer, G5 security-reviewer, G2 producer self-check by orchestrator; producer = backend-engineer ≠ any reviewer).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while all of the following hold: the task's 17 allowed-path files keep the blob ids they have at f0b20feb (results_read.py, results_request.py, study_setup_document.py, study_read.py, config.py, build_info.py, main.py; tests test_results_read_api.py, test_results_read_law_examples.py, test_study_live_outline_provider.py, test_build_info_api.py, test_read_router_mounts.py, test_result_ways.py; docs lanes/queues/C.md, lanes/status/C.md, plans/JOURNEY_215_16_NORTHERN_2026-10-04.md; and the producer report); everything under services/api/app/scenario, services/api/app/contracts, services/api/app/rules, packages/contracts, apps/web and docs/reference-cases, plus render.yaml, stays byte-identical; and the eighteen row texts and their binding to M5-T138 are unchanged.
 - Tolerated later commits: any that touch only project-control/** and docs/DISCOVERY_BACKLOG.md; and a merge of the integration branch that changes none of the files named in the predicate. I verified every file changed from the last material commit f0f67244 to the frozen head is under project-control/, and the forbidden/unchanged paths are byte-stable from the claim-seam.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The out-of-repo RED/mutation proofs (ruling R4 "treat the interior lot as a corner lot", and other per-branch mutations) are recorded in the producer report and run in a copy; I reproduced the GREEN assertions the mutations would break (e.g. S13 "Not applicable" corner lines; test_t9's in-file loosen-mutation ran), but I did not re-run the out-of-repo mutations myself.
 - The full api suite (recorded 8647 passed 8 skipped) and the website checks (lint/typecheck/2429 unit/build/153 browser) were forbidden to me and there is no website file in this task; I relied on the ledger's recorded orchestrator runs as claims.
 - No pull request exists yet (branch task/wave11-results-route); I verified the validator locally (exit 0) but did not run the CI control-plane job at a pushed head.
 - I did not re-derive the zoning reference numbers (20150, 24180, 10710, 16, etc.) from first law principles; I confirmed the tests load them from docs/reference-cases/R6B/cases/*.json and assert against them, and that correctness of the engine math is the domain of M5-T136/M5-T137, not this route.
END-OF-REPORT
```
