# M5-T150 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c` (branch `task/wave20-presentation-slice`, review copy `/root/project/rv-w6-c`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R192, R239, R257, R570, R804, R841, R846, R878, R886, R888, R890, R896, R899.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 04:50 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T150 (directive D-090, 13 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only, reproduced-evidence review; it is NOT a human or professional review. I produced none of the work or records and treated every report, map, gate record and the brief as an unverified claim. Scope: this task's SHARE of each row; each row stays open in the registry for the other tasks still bound to it.

(1) HEAD VERIFIED
 - I read the frozen head db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c on task/wave20-presentation-slice in /root/project/w-wave20 (git rev-parse HEAD confirms; working tree clean); base main 0bb6acb293278d125e31c76da18e4ffe6e4b9ac1 is the merge-base.
 - The read-only guard blocked git checkout and shell redirects, so I read the head through git plumbing (git show db7824e70e0c:<path>, git archive|tar) and ran the authorized tests against the w-wave20 working tree, which is already at the frozen head.
 - Commits d745b635..db7824e70e0c change ONLY project-control/ files (git diff --name-only shows no non-control path), so the material code at the reviewed head d745b635 is byte-identical to the frozen head; the gate content identity (content_manifest_sha256 13d6af21..., reviewed_sha 5bf6f72949cfc591da5b6cedf54c2a976961e601) is that same code.

(2) ROWS

ROW D-090-R192 — PASS
 - geometry.build_geometry (services/api/app/scenario/three_answers/geometry.py) draws the lot outline from inputs.lot_outline (the measured tax-map polygon), never the recorded-area rectangle; the committed benchmark fixture's geometry.lot_outline is a 5-distinct-vertex polygon whose shoelace area I computed as 10,387.99 sq ft, not the old 102.30x98.48 rectangle (=10,075.0) it replaced.
 - I ran tests/scenario/three_answers/test_geometry_lot_outline.py (lanes venv, frozen head): test_s1_benchmark_lot_outline_is_the_measured_polygon asserts area==measured within 0.5, area != recorded by >1.0, and >=5 distinct vertices — passed (118 passed, exit 0 with test_results_read_api.py).
 - Open: R192 is broader than this task (any parcel-specific conclusion — yards, coverage, footprint, what-fits) and stays bound to M5-T145/M5-T146; this task corrects only the drawn site-plan outline.

ROW D-090-R239 — PASS
 - The two figures are the recorded lot area (10,075) and the outline area (10,387.99); the drawing uses the outline's area while the recorded area still feeds the floor-area path — I verified the benchmark fixture changed ONLY under /geometry (key-level flatten: 0 non-geometry leaf changes; all other geometry sub-keys byte-identical), so no figure was mixed into another.
 - test_s1 asserts the drawn area is >1.0 sq ft away from the recorded 10,075, proving the recorded area was not used to size the drawing; _lot_dimensions (a recorded-area rectangle) exists only as an internal option-comparison extent, never shown.
 - Open: the full written decision of how each area figure is used across all calculations stays with M5-T130/M5-T145/M5-T146.

ROW D-090-R257 — PASS
 - Neither area is stretched to the other: R846's _local_feet_ring only translates (area-preserving), and the no-outline path withholds rather than substituting — the live route (test_m5t146_live_route_lists_building_b_without_the_tax_map_outline, which I ran green) returns coverage_by_portion status "withheld", gap_kind "missing_information", reason "...outline is not available", with no footprint_sqft number.
 - The drawing shows the measured outline where present and the affected coverage is withheld where the two areas disagree; the recorded area is never placed into the withheld coverage result.
 - Open: full conflicting-area establishment across M5-T129/T130/T134/T136/T138/T146 remains.

ROW D-090-R570 — PASS
 - With no measured outline the whole geometry block is withheld: test_s2_no_outline_draws_nothing_and_says_why and the live-route test both assert geometry.status=="not_available", reason contains "outline is not available", reason_kind=="missing_input", and "lot_outline" not in geometry — I reproduced both (green).
 - No number, older value or substitute appears in place of the withheld geometry/coverage (no footprint_sqft; the recorded 10,075 rectangle is never rendered); the transform _apply_geometry (three_way_document.py, lot_outline_available is False branch) replaces the block with LOT_OUTLINE_NOT_AVAILABLE_REASON and returns.
 - Open: R570 applies program-wide (also M5-T136..M5-T149); this task covers only the geometry/outline slice.

ROW D-090-R804 — PASS
 - The diff touches only geometry threading, the regenerated benchmark + its SVG/DXF snapshots, the review-register resync and the V11(4) reason wording; no rule file, schema, or production switch changed (git diff base..head shows no services/api/app/rules/rulesets, no packages/contracts/schemas, no render.yaml production toggle), so scope, calculation authority, security and production holds are preserved.
 - python tools/validate_directive_compliance.py --check returned exit 0 (quiet-on-success, per the script's own line-22 contract); deterministic code still calculates (the engine/decision modules are read-only in this diff).
 - Open: R804 is program-wide and also bound to M0-T189/M5-T148/M5-T149.

ROW D-090-R841 — PASS
 - The lot outline is the document's real measured polygon drawn through the existing server drawing kit (forbidden styles.py untouched; the SVG snapshot carries 5 dimension texts each data-source="edge:/geometry/lot_outline/0#N"); no stand-in rectangle reaches any shown output.
 - I independently traced the shown path: the API route services/api/app/api/v1/results_read.py calls run_engine_and_result_ways_from_evidence (line 385), and test_t3_route_files_name_neither_older_entry_nor_the_inputs_builder asserts "run_engine_and_result_ways(" not in the route source — so the only path that could keep the rectangle is test-only; the live-route no-outline test proves the route withholds the whole block instead.
 - The DXF snapshot carries the measured polygon vertices (6 matches on 101.28981/122.9469/120.6634/97.6142) and zero occurrences of the old rectangle coordinates (102.303030/98.481931); screen/PDF/DXF follow the same canonical geometry. Open: the contract's PDF/drawing surfaces (steps 4/5) carry R841 further.

ROW D-090-R846 — PASS
 - The block is labelled crs "local_feet", units "feet" — never EPSG:2263; _local_feet_ring subtracts min x/min y (area-preserving translation), and test_s1_lot_outline_is_translated_to_local_feet asserts min x==0, min y==0, max<1000 ft (not State-Plane ~1.05e6), which I reproduced green.
 - The outline is never stretched to the recorded area: the drawn area is 10,387.99 (the measured area), not 10,075; test_s1 asserts area==measured within 0.5 and area != recorded.
 - Open: the transform is stated via the crs="local_feet" + measurement "Approximate — tax map" fields (the producer could not add a free-text transform sentence because the schema fields are const/additionalProperties:false); the drawing never mislabels, so nothing is owed, but a richer transform note is a later-surface item.

ROW D-090-R878 — PASS (geometry/metric share; legibility portion stays open)
 - UX-10 geometry/metric match is met: test_s5_drawn_outline_area_equals_the_recorded_measurement compares the shoelace of the drawn ring to the Shapely area of the recorded fixture within 0.5 sq ft (green), and I independently recomputed the five edge lengths of the drawn polygon as 2.22, 101.71, 99.98, 103.88, 99.98 ft — exactly the SVG's five dimension labels.
 - The old rectangle dimensions (102.30/98.48 ft) are absent from the SVG; the three "99.98 ft" strings are two dimension labels plus one scope note (215 Place frontage), not a false dimension.
 - Open (I did not verify): "labels remain legible at final output size" + collision checks + visual inspection — the genuine 2.22 ft sliver label legibility is explicitly a G4 visual-quality/human-walkthrough item (DB-216), and street names/context are not drawn yet; this row continues on the drawings/PDF surfaces.

ROW D-090-R886 — PASS
 - The expected area is independently established, not a program echo: test_s5 reads the measured polygon from the recorded replay fixture (_measured_outline().polygon.area via lot_outline_from_mappluto(replay_lot_geometry()) + prepare_outline) and compares it to an in-test shoelace, never a retyped literal (_RECORDED_LOT_AREA=10075.0 is used only to prove the drawing is NOT the recorded value).
 - Only the one benchmark fixture whose geometry actually changed and its two snapshots were regenerated (git diff shows no other valid results fixture's geometry moved), so baselines were not updated wholesale.
 - Open: visual review of the regenerated SVG/DXF snapshot images is a G4/walkthrough item; the numeric correctness value is verified here.

ROW D-090-R888 — PASS
 - Producer/reviewer separation holds: producer geospatial-engineer (+ rules-engineer for the V11(4) wording); independent reviewers were a data-contract-verifier (G3) and a qa-engineer (G4), the same two across two rounds, and the visual-quality review + walkthrough FAILED in round 1 and forced corrections (a producer checklist did not pass itself).
 - verification.json carries exactly one M5-T150 row with the 13 ids, producer "geospatial-engineer", verifier "" (empty) — this DCV pass is the independent verification; the gate records G3/G4 name the independent reviewer types, not the producer.
 - Open: none specific to this task.

ROW D-090-R890 — PASS
 - The producer report and evidence map claim only what changed and list honest known-limits (street names not drawn, 2.22 ft label may read cramped, register tested_commit informational); nothing is called perfect/complete/fully-verified/production-ready.
 - The review-register resync entered implementation_changed events "behaviour unchanged" by "M5-T150 (geospatial-engineer, an AI agent)" and human_review.reviewer_name stayed "" — no session entered a human verdict (CLAUDE.md item 20).
 - Open: none specific to this task.

ROW D-090-R896 — PASS
 - The owner's finding 4 is corrected: before, geometry.py drew a rectangle sized to the recorded area (10,075) while the site plan labelled it the tax-map outline (10,387.99); the frozen benchmark fixture's lot_outline is now the 5-vertex measured polygon of area 10,387.99 with the measurement label "Approximate — tax map" unchanged, so the drawing and the measurement explanation now agree.
 - Where no outline exists, nothing is drawn and the page says why: the live-route no-outline test asserts geometry.status=="not_available" with the reason, through the real API route (reproduced green).
 - Open: nothing for the correction itself; drawing completeness (street names/context) is R893/R899 territory for later surfaces.

ROW D-090-R899 — PASS (this task's share: the mismatched drawing information + the server's reasons)
 - The mismatched drawing information is corrected now (per R896); the V11(4) wording share is met: _B_BOUND_RESOLVED in first_option_results.py now reads "the program's method for a first building does not yet cover." (no "step-P6"; the remaining "step-P6" strings are docstrings/comments at lines 26/123/319, never emitted), and the new _sqft formatter prints whole numbers without ".00" and keeps fractions (6,716.67 sq ft).
 - test_v11_4_live_route_plain_words_and_whole_square_feet_without_decimals walks EVERY string of the returned document at 10/14/16/25 ft asserting no "step-p6" and no /\d\.00 sq ft/ — I reproduced it green.
 - Open: the crowded-presentation and inconsistent-wording shares belong to M5-T148/M5-T149 (website); street names/context stay honestly not-drawn (backlog R893).

(3) BINDING B1–B5
 - B1 — PASS. git diff base..head of requirements.json changes only applicability.task_ids plus requirement_count (891->899) and updated_at; a programmatic row-by-row compare found ZERO text/classification/source_ref/binding changes. M5-T150 was appended to 11 pre-existing rows (R192, R239, R257, R570, R804, R841, R846, R878, R886, R888, R890); R896 and R899 are two of eight brand-new source-080 rows (R892-R899) created with M5-T150 bound from creation — both correct and text-stable.
 - B2 — PASS. I recomputed the digests from the frozen requirements.json: content digest (LF-normalized sha256_text_artifact) = 59a3752d3d2c60ed2f4d858295f914b12d14cdf97faa3811e8f157f63d2e5304 and id digest (sha256 of sorted ids) = f31113ebdb803a0187e5092ed61d63be4ad3d089062ff1452d94c446a7405dcd; both equal the manifest's requirements_content_digest_sha256 and requirements_id_digest_sha256 (899 unique ids).
 - B3 — PASS. verification.json (schema directive_verification/v2) has exactly one M5-T150 row; applicable_requirement_ids == the cited 13; producer "geospatial-engineer"; verifier ""; every one of the 13 requirement states "pending" with reviewed_sha null.
 - B4 — PASS. Exactly 13 rows carry M5-T150 in applicability.task_ids and they equal the cited set; no D-090 row matches M5-T150 via task_types ("backend") or milestones ("M5"), so applicable == cited.
 - B5 — PASS. Only the D-090 requirements.json and manifest reference M5-T150 across the directives tree (git grep); no other active directive binds this task uncited. Gate records: G0 PASS (orchestrator, re-recorded at the corrected head eac6d07d), G2 PASS (orchestrator self_check), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer); G2/G3/G4 share one content identity (content_manifest_sha256 13d6af21..., reviewed_sha 5bf6f729) and were reviewed_at 2026-10-10 04:37:34/37/39 UTC, after CI run 38023638114 completed success at 04:26:15. I confirmed via gh that run 38023638114 on d745b635 has 21/21 jobs success (plus secret-scan 38023638134 and context-budget 38023638117 success), and all three workflows were success on the first-round head b4126d55 too.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: (a) the blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, apps/web/src, render.yaml, .github, tools and this task's project-control reports are unchanged from the frozen head; and (b) the 13 rows' text and their M5-T150 binding (B1/B2/B4) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of M5-T148/M5-T149 on this branch, and a main-line merge that changes none of the predicate's files. I verified the frozen head itself already satisfies the code-identity half of this predicate relative to the reviewed head d745b635 (only project-control changed between them).

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Visual legibility of the 2.22 ft sliver dimension label at final output size, label-collision checks, and the screenshot/visual appearance of the regenerated SVG/DXF (R878/R886 visual portion) — I confirmed the labels exist and match the polygon edges, but legibility at print scale is a human/visual-review item explicitly carried forward (DB-216).
 - The Playwright browser suite (claimed 167/167 at d745b635) and the full api/web suites — the brief forbids running the full suites and tools/test_directive_compliance.py and bars touching ports 3000/3001/8000; I relied on the recorded CI (run 38023638114, 21/21 success, which I read via gh) at the reviewed head and on the verified code-identity stability to the frozen head.
 - The mutation-catch runs the producer/reviewers recorded (rectangle restored, translation dropped, step-P6/".00" restored) were verified by me through assertion-coupling inspection and by running the tests green, not by re-materializing each mutant (the read-only guard blocks in-repo writes); the tests are structured to fail on those exact mutations.

END-OF-REPORT
```
