# M5-T144 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `5e7be6c312756d07ece87c86343b9ff79fb3fa22` (branch `task/wave16-server-corrections`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R258, R267, R570, R641, R642, R646, R647, R648, R649, R661.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED, BLOCKED or UNVERIFIABLE row; no required correction.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-09 05:19 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T144 (directive D-090, ten rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier); this is an independent, automated, read-only review, NOT a human or professional/legal review. I reproduced each requirement from primary evidence (code, the named reference-case rows, the committed document, the focused tests run myself, the registry objects and git), treating the producer report, evidence map and gate returns as claims.

(1) HEAD VERIFIED
 - `git -C /root/project/rv-w6-a rev-parse HEAD` = 5e7be6c312756d07ece87c86343b9ff79fb3fa22 (the frozen head); working tree clean; I worked only in this copy.
 - Focused suite (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider, from services/api, NO update var) over the six named folders: 1474 passed, 2 skipped, exit 0 (no xfailed/xpassed). `tools/validate_directive_compliance.py --check` exit 0.

(2) ROWS
ROW D-090-R258 — PASS
 - result_ways.py new `not within_point and within_angle` branch sets gap_kind=MISSING_INFORMATION; the committed fixture (recorded_215_16_northern_journey.json) shows value_states.rear_yard.gap_kind "missing_information" and geometry.yards.reason_kind "missing_input".
 - test_result_ways_truth_table.py pins position-16 rear yard as missing_information with required substrings; S4/S6/S16 keep the other branches work_owed, so unbuilt work stays labelled work_owed, not missing-info.
 - Stays open: the rule code that would compute the rear yard from those facts is still owed work, recorded in the backlog (ruling C3), not relabelled finished and not in this task.
ROW D-090-R267 — PASS
 - build_status_strip (explanations.py) emits {"text":"Preliminary zoning results"} as item 0 (was "Zoning maximum"); committed document status_strip[0] = {"text":"Preliminary zoning results"}; every value-state keeps its own way.
 - All residual "Zoning maximum" strings are out of scope: the different dashboard string "Zoning maximum not available", two schema DESCRIPTION examples, a compare_rows.py comment, and hand-authored synthetic/invalid contract fixtures — none is the results strip shown to a user for this document.
 - Stays open: the out-of-scope schema-description/synthetic-fixture lag still carries the old word (a harmless doc lag for a trivial follow-up); not bound to this task.
ROW D-090-R570 — PASS
 - three_way_document.py _apply_geometry now clears geometry.envelope when max_building_height OR coverage is withheld (_combined_not_available); the former strict-xfail test (test_db199a_..._known_defect) passes as an ordinary test asserting no withheld height figure (e.g. 55) remains anywhere in geometry; S11–S14 pin the envelope behaviour.
 - test_db199a_every_block_of_the_emitted_document_is_classified classifies every block of several real emitted documents and the guard catches any new numeric block; geometry.py (read-only) confirms the envelope was the only reachable leak surface today.
 - Stays open: floor_plates (building option) and setback are always not_available this milestone, so their coverage-footprint leak is not reachable yet; the same follow-logic must cover floor_plates once the building option is built — R570 stays a standing invariant open in the registry.
ROW D-090-R641 — PASS
 - explanations.py item 0 == {"text":"Preliminary zoning results"}; test_status_strip_first_item_is_preliminary_zoning_results asserts it in code and in the generated document; the committed document carries it (byte-compared by test_215_16_northern_journey.py line 330).
 - I confirmed status_strip[0] in the committed fixture reads exactly the owner's words.
 - Stays open: nothing for this task.
ROW D-090-R642 — PASS
 - Comparing every value_states.way in the committed document at 7f0e131f vs the frozen head: NONE of the 16 ways changed; only rear-yard reason/gap_kind/resolver/zr_sections and status_strip[0] changed.
 - test_result_ways_truth_table.py pins the way and kind of every result in every state.
 - Stays open: nothing for this task.
ROW D-090-R646 — PASS
 - I read docs/reference-cases/R6B/cases/step-p5-worked.json row zr-34-23-page: its expected value states the three subsections are the complete set, none speaks of the rear yard, "resolving the completeness caveat reading 9 raised in step P4" — the owner's statement is true by the row's own words; the G0 report quotes it truly.
 - The code acts on it: OVERLAY_SUPPORT_ROWS REAR_YARD is now supported=True resting on step-p5-worked/zr-34-23-page; test_result_way_bridge_overlay asserts this; S2 is the proved consequence (within-waiver now shown).
 - Stays open: nothing for this task (external-fact row verified by reading and recorded).
ROW D-090-R647 — PASS
 - I read row benchmark-rear-yard-23-342-23-344: it states the beyond-100-ft result "turns on the adjoining zoning lot's lot-line type ... which the readers did not have" and "The readers differ on the geometry" — the owner's statement is true; the G0 report quotes it truly.
 - The corrected reason's clauses ("depends on this lot's exact lot lines and on which lot lines of the adjoining lots meet them ... the program does not have those facts") are sourced to this row; no section number in prose, no "two readings disagree", no "professional review" (ruling C2 holds).
 - Stays open: nothing for this task; the pure-corner-square note (F1) is non-blocking.
ROW D-090-R648 — PASS
 - result_ways.py returns the corrected reason/kind/resolver; the fixture carries the exact text at value_states.rear_yard and geometry.yards. test_s1 and test_s3 assert the whole reason == _BEYOND_REASON and resolver == _BEYOND_RESOLVER via one shared constant, matching the fixture; the website panel test shows "Missing information about this property." for the rear yard (S17).
 - One text for one situation (ruling C1): S3 (no-overlay R6B) asserts the same text as S1 (C2-2).
 - Stays open: nothing for this task.
ROW D-090-R649 — PASS
 - The fixture value_states.rear_yard has way=withheld and NO `value` key; geometry.yards is not_available with no entries/figure; the journey test asserts no withheld result carries a number anywhere; G4 mutation m12 (figure 20 on the rear yard) fails the byte-compare and DB-199 guards.
 - I confirmed there is no rear-yard figure in value states, geometry.yards or elsewhere in the document.
 - Stays open: nothing for this task.
ROW D-090-R661 — PASS
 - three_way_document.py clears geometry.envelope on a withheld height; the former strict-xfail test carries no @pytest.mark.xfail and passes as an ordinary test (focused run: 0 xfailed/xpassed); S11 proves the flood-zone corner lot clears the envelope and leaks no height figure; S12–S14 pin the reason and precedence.
 - The repair covers the envelope/height leak (the only reachable leak today) before drawings/CAD/PDF read the geometry block.
 - Stays open: the floor_plates coverage-footprint leak is latent (building option always withheld now, so unreachable); the broader "geometry follows every withheld result" invariant continues for future layers.

(3) BINDING B1–B5
 - B1 PASS: requirements.json 7f0e131f→frozen appends M5-T144 to exactly the ten rows' applicability.task_ids (no removals), changes no existing row's text, and appends new rows R669–R684 (none bound to this task). Base 668 rows → head 684 (16 new); R641–R668 already present at base (merged from the prior branch).
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = b66c96714566136e204f830384dd03e0f1273f035278e6d84f8de0da3721fdef = manifest.requirements_content_digest_sha256; audit_log holds an "applicability_bound" entry for M5-T144 binding the ten rows with the digest resynced in the same commit.
 - B3 PASS: verification.json has one M5-T144 row; applicable_requirement_ids are exactly the ten; producer rules-engineer; verifier ""; each of the ten state=pending, evidence [], reviewed_sha null.
 - B4 PASS: evaluate_task_refs over the real registry → ok:True, applicable_ids == cited_ids == the ten, missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: derive_applicable returns only the ten D-090 rows (empty second element) — no other active directive applies to M5-T144 and goes uncited. Gate records: G0 PASS (6fd1c6d4, orchestrator), G2 PASS (b6de4c0c, orchestrator self-check), G3 PASS (b6de4c0c, data-contract-verifier), G4 PASS (b6de4c0c, qa-engineer) — G2/G3/G4 share one content identity. CI on the reviewed head 582dcccb (run 37884285350 + secret-scan 37884285480 + context-budget 37884285511) all success, created 04:31Z, read green 04:39Z BEFORE the reviews (04:48Z/05:00Z) and the gate commit (b6de4c0c, 05:06Z); the allowed-path material files are byte-identical 582dcccb→frozen. This satisfies the intent of R639/R640 (CI green on the reviewed head before the gates), though those rows are not bound to this task.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while a blob-level predicate holds: the task's 19 allowed-path files keep their frozen-head blob ids; the read-only inputs are unchanged (geometry.py, result_way_conditions.py, result_way_inputs.py, engine.py, three_way_scope_lines.py and the other named three_answers files, everything under docs/reference-cases, docs/research, packages/contracts/schemas and /generated, .github, tools, apps/web/src/lib, apps/web/e2e, services/api/app/api, /contracts, /_contract_schemas, render.yaml); and the ten rows' text plus their M5-T144 binding are unchanged. I verified that between the reviewed head 582dcccb and the frozen head only docs/SESSION_HANDOFF.md and project-control/** changed — no allowed-path material file moved.
 - Tolerated later commits: those touching only project-control/**, docs/DISCOVERY_BACKLOG.md and docs/SESSION_HANDOFF.md (the handoff file rides on this branch, one commit, that file only); and a merge of the integration branch that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED, BLOCKED or UNVERIFIABLE row; no required correction.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The full services/api pytest suite, the web lint/typecheck/build, and the browser/Playwright e2e tests are CI's and are forbidden to me here; I relied on the orchestrator-recorded CI run 37884285350 at headSha 582dcccb (21/21 jobs success, incl. web-e2e, api, web, contracts, modularity, dependency-security) read via `gh run list`, plus secret-scan and context-budget success — I did not re-execute them.
 - I did not run npm/vitest; the 199-passed web count and the scratch-copy website mutation are the orchestrator's/G4's reproduced claims, though I read the committed three-answers-panel.test.tsx diff and confirmed it tightens (not weakens) the rear-yard assertions.
 - I ran the focused server suite, the validator, the modularity check (exit 0; no warning on this task's modified files), geometry.py, the reference-case rows, the registry objects and the git history myself; those are first-hand.
END-OF-REPORT
```
