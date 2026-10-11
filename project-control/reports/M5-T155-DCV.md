# M5-T155 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `7adc476edb171f16386981708c06c0c7dddf995d` (branch `task/wave22-site-context`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R843, R936, R937, R938.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. All corrections raised by the independent reviewers (code M5-T154-C1; QA C1–C4; visual T155-C1, T156-C1, T156-C2; the modularity split into context_scene.py) were applied before the corrected head 6c8c9f7d and re-passed by every reviewer; I reproduced the end state and found no open defect in this task's share.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-11 00:41 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T155 (directive D-090, 4 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. I produced none of this work and none of its records. This is not a human or professional review. I judged each row from primary evidence (the code at the frozen head, the tests and what they assert and a rerun of them, the printed report pages I looked at myself, the ledger gate records, the registry objects, the git objects, and the CI run conclusions read via gh). The producer report, evidence map and review record were treated as claims to reproduce, not as proof.

(1) HEAD VERIFIED
 - I read the frozen head 7adc476edb171f16386981708c06c0c7dddf995d directly: `git -C /root/project/w-wave20 rev-parse HEAD` returns it, on branch task/wave22-site-context, base main 9ab3a47e6a55fc75e13140e910f0839541754874; the working tree is clean (git status --porcelain empty).
 - Its product files (services/api/app, services/api/tests, packages/contracts, docs, apps/web, render.yaml, .github, tools, CLAUDE.md, .claude/rules) are byte-identical to the corrected/reviewed head 6c8c9f7d and to the submit head 2341590e: `git diff --stat` across those paths for 6c8c9f7d..2341590e and 2341590e..7adc476 is empty, so the reviews, CI and gate records carry to this head.

(2) ROWS

ROW D-090-R843 — PASS (for this task's share)
 - The site-context plan draws every mapping element the row names: the selected lot outline, the adjoining context (neighbouring tax lots, existing building footprints, streets), street names with mapped widths, a grid-north arrow, a real scale bar at a standard architectural scale, the lot's edge-length dimensions and a legend of only what is drawn; I confirmed this in services/api/app/drawings/maps/site_context_plan.py and context_scene.py and in printed page 3 of print-w22g (Lot 70 with 103.88/99.98/99.98/101.71 ft, NORTHERN BOULEVARD "100 ft mapped width", 216 STREET "60 ft mapped width", north arrow, scale bar, legend).
 - Source, date and measurement basis are returned in the caption and are source-traced: test_s5_caption_names_each_source_and_its_date and test_s5_the_street_area_and_survey_notes_are_present PASS in my rerun (MapPLUTO 2026-09-09, Digital City Map 2025-12-01, Building footprints 2026-09-27, "Approximate — tax map"); a missing layer returns Unavailable, never a partial picture (test_s6_* PASS), satisfying "state the limitation instead of an isolated polygon."
 - The one element the row names that this task does NOT draw is yards/setbacks: ruling Y6/Y8 forbids drawing any law (the engine does not yet compute them), confirmed by test_s7_no_law_is_drawn (kinds_drawn ⊆ {street_area, subject_lot, neighbour_lot, building_footprint, existing_building}).
 - OPEN FOR THE REST: the yards/setbacks depiction and the whole-report placement of the plan stay open under R843 for M5-T156 and later envelope work (the row remains pending and bound to M5-T154/M5-T156/BOOTSTRAP in the registry).

ROW D-090-R936 — PASS (for this task's share)
 - The drawing names what it is and shows the lot among its surroundings, not an isolated rectangle: render_site_context_plan titles itself "Site plan: the lot among its neighbours", draws the streets as named street areas with mapped widths, the street corner, the neighbouring lots and the existing buildings, rotated to the Northern Boulevard frontage; test_s2_streets_are_named_with_their_mapped_widths, test_s2_only_the_subject_and_its_edge_sharing_neighbours_are_labelled and test_s2_rotated_to_the_frontage_with_grid_north_noted PASS in my rerun.
 - I looked at the printed pages myself: page 3 reads as an architect's site plan (coral Lot 70 as a corner lot at Northern Blvd & 215 Place among Lots 1/11/61, grey existing buildings, named streets with widths), and page 1 carries the compact summary frame of the same plan.
 - The subject lot reads first (coral fill drawn above the grey neighbour buildings; the subject's own existing building is a dashed outline), proven by test_t155_c1_subject_fill_reads_above_the_existing_building, answering the "grey rectangle" complaint.
 - OPEN FOR THE REST: R936 is also bound to M5-T154 (the live map data) and M5-T156 (placing the drawing in the report at a glance); the row stays pending for those shares.

ROW D-090-R937 — PASS (for this task's share)
 - The task produces the two "where is the lot" drawings the row requires: render_neighbourhood_map (street network north-up with the lot marked) and render_block_map (the block close-up), each returning a sources-and-dates caption; test_s3_neighbourhood_shows_the_street_network_with_the_lot_marked, test_s3_block_marks_only_the_subject_and_names_the_streets and test_s4_caption_is_returned_with_dates PASS in my rerun.
 - I looked at printed page 2 ("Where is the lot?"): the neighbourhood map (north-up grid, "Subject lot" marker, scale 0/500/1,000 ft, Digital City Map source + 1 Dec 2025 date) and the block close-up (Lot 70 coral among neighbours, MapPLUTO/footprints/DCM sources with edit dates) are both present.
 - The row says "city OR neighbourhood scale"; the neighbourhood map satisfies the neighbourhood-scale option, so the absence of a city-scale overview (tracked as backlog DB-228) does not fail the row.
 - OPEN FOR THE REST: R937 is bound to M5-T154 and M5-T156; the page-level assembly and the optional city-scale overview stay open there (the row remains pending).

ROW D-090-R938 — PASS (for this task's share)
 - This task delivers coloured, clearly labelled drawings at stated standard scales to the competitor-sample standard: the drawings carry a legend, named streets, a scale bar and north arrow, every label is at least 7 pt with no overlaps (test_s4_fits_and_every_label_is_at_least_7pt_with_no_overlaps and test_s4_report_frame_fits_and_every_label_is_at_least_7pt PASS in my rerun), and the look sits within the presentation contract (no URL/field/code word: test_s5_no_url_field_name_or_code_word and forbidden_tokens == [] PASS; no stock/photo imagery — Y9).
 - The independent visual-quality-reviewer compared the printed report with the competitor sample's location page and returned PASS at the corrected head 6c8c9f7d, finding the owner's "doesn't look like my competitors" complaint "substantially answered"; I corroborated by looking at pages 1–3 myself (coloured, labelled, stated-scale drawings, property-location page present).
 - "The building's shape shown on its lot" is only partially in this task's scope: existing building footprints are drawn (dashed on the subject), while the proposed building's placement is deferred by ruling Y8/R939 to M5-T156, which prints the plain "No building is placed on this plan yet" line (seen on page 3).
 - OPEN FOR THE REST: R938 is bound to M5-T156; the full property-location page assembly and the eventual proposed-building placement stay open there (the row remains pending).

(3) BINDING B1–B5
 - B1: the D-090 requirements.json diff from base appends M5-T155 to the applicability.task_ids of R843 (base [BOOTSTRAP] -> [BOOTSTRAP, M5-T154, M5-T155, M5-T156]), R936, R937 ([BOOTSTRAP, M5-T154, M5-T155, M5-T156]) and R938 ([BOOTSTRAP, M5-T155, M5-T156]); no existing row's text changed base->head (changed-text set empty) and no row was removed. Rows R934–R940 are the seven new rows of this wave and their text equals the captured sources' reading (source-082 maps R934–R939, source-083 maps R940; I read both amendments and the row texts match verbatim quotes and the orchestrator's reading). The audit_log records the two "amended" entries and the per-task "applicability_bound" entry for M5-T155 (R843, R936, R937, R938) with a digest resync in the same commit and no text edit.
 - B2: directive_registry.sha256_text_artifact(requirements.json) = 99bcd267cee2fb1bf8414f79d12daf0d961f3fc8c4053511abc6cb9bbb5da235, equal to manifest.requirements_content_digest_sha256; the id digest ca491ca2… also matches requirements_id_digest_sha256. The source digests on disk match the manifest (source-082 7604c8f4…, source-083 2a6675af…). `tools/validate_directive_compliance.py --check` exits 0 at this head.
 - B3: verification.json holds exactly one M5-T155 task_verifications row, applicable_requirement_ids = [R843, R936, R937, R938], producer "geospatial-engineer", verifier "" (empty), schema directive_verification/v2, and each of the four requirement rows is state "pending" with empty evidence and null reviewed_sha — i.e. awaiting this verdict.
 - B4: reg.evaluate_task_refs(M5-T155) returns ok=True with applicable_ids == cited_ids == [R843, R936, R937, R938], missing_ids [], invalid_refs [], unresolved []; reg.derive_applicable(task) returns exactly {R843, R936, R937, R938} with no issues.
 - B5: across all 90 active directives the registry loads (D-001..D-092), derive_applicable for this task yields only the four cited D-090 rows — nothing else applies to M5-T155 uncited. Gate records: G0 PASS (orchestrator, administrative, at contract head 60635e40 then re-recorded after scope correction 1), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) — the three required product gates G2/G3/G4 all at one content identity (reviewed_sha 2341590e, content_manifest_sha256 2b562d8f…). CI at the corrected head 6c8c9f7d is success on both the pull-request run 38097919683 (21 jobs, all success) and the push run 38097916934 (21 jobs, all success); the product files at 6c8c9f7d are byte-identical to the gate head 2341590e and to the frozen head. I reran the task's focused suite at the frozen head (services/api: pytest -q tests/drawings/maps) = 175 passed, 4 skipped (the 4 skips are in the pre-existing location/zoning test_maps.py, unrelated to this task); tools/modularity_check.py --check exits 0 and flags none of this task's maps modules (site_context_plan.py 595 phys, context_scene.py 531, street_areas 307, block_map 89, neighbourhood_map 66, adapter 334, model 224). The task's commits touched only files inside allowed_paths plus project-control control-plane records; no forbidden-path file, no requirements/pyproject/package/lockfile, no new package. Prohibited actions: nothing merged/accepted/closed — PR #486 is OPEN (mergedAt null), the frozen head is not on main (main still 9ab3a47e), the task status is awaiting_gate, and nothing was deployed/installed/purchased.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: (a) the blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules and the M5-T155 reports (G0, evidence-map, reviews, producer-report) are unchanged; and (b) the four rows' text and their M5-T155 binding in requirements.json / verification.json are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other tasks on this branch (M5-T154, M5-T156), and a merge of the main line that changes none of the predicate files above. Any change to a predicate blob, or to a row's text/binding, voids this carry-forward and requires re-review.

(5) REQUIRED CORRECTIONS
 - None. All corrections raised by the independent reviewers (code M5-T154-C1; QA C1–C4; visual T155-C1, T156-C1, T156-C2; the modularity split into context_scene.py) were applied before the corrected head 6c8c9f7d and re-passed by every reviewer; I reproduced the end state and found no open defect in this task's share.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The ten-second test with a real architect and a real screen-reader pass — needs a person; not run by me or by any reviewer (all reviewers are AI).
 - The live-provider path (LIVE_SPATIAL_PROVIDER_ENABLED on, real ArcGIS calls) — off by default and outside this task; the drawings were verified on the recorded pack via the real provider, not against live services.
 - The full api suite and the whole Playwright e2e suite — forbidden by my brief (and tools/test_directive_compliance.py); I relied on the recorded CI conclusions at 6c8c9f7d, which I read via gh but did not re-execute. I counted 21+21=42 CI jobs all success rather than literally enumerating "46 checks"; the discrepancy is in how check-runs/contexts are tallied, and I found zero non-success among all jobs on both runs.
 - "Reaching the competitor visual standard" (R938) is partly a visual judgement; I looked at the printed pages myself and relied on the independent visual-quality-reviewer's PASS, but I did not render my own high-DPI crop comparison against the competitor sample pages.
END-OF-REPORT
````
