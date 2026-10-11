# M5-T156 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `7adc476edb171f16386981708c06c0c7dddf995d` (branch `task/wave22-site-context`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R551, R843, R893, R923, R936, R937, R938, R939, R940.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. (Prohibited-action check clean: M5-T156 is in state.json active_tasks, not accepted_tasks; the branch is not merged into main; the wave diff changes no services/api/requirements*, pyproject.toml, package.json, package-lock.json or .github/ file — the only "requirements.json" in the diff is the directive registry file.)
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-11 00:41 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T156 (directive D-090, 9 rows)
VERDICT: PASS

I am an AI agent (the independent directive-compliance-verifier). I produced none of this work or its records. This is an automated verification, not a human or professional review.

(1) HEAD VERIFIED
 - I read the frozen head 7adc476edb171f16386981708c06c0c7dddf995d on branch task/wave22-site-context in /root/project/w-wave20; `git rev-parse HEAD` returns it and the worktree is clean for services/api, apps/web and docs/design (git status --porcelain empty on those paths).
 - Base is main 9ab3a47e6a55; the frozen head is NOT an ancestor of main (branch not merged). Only project-control/ files differ between the reviewed/printed head 6c8c9f7d, the submit head 2341590e and 7adc476, so the reviews, CI and the printed report print-w22g all represent the frozen head's product content.

(2) ROWS (this task's share; every row stays open in the registry for the rest of its scope)

ROW D-090-R551 — PASS
 - The real website output /root/project/lanes-runtime/owner-docs/session-2026-10-10a/print-w22g/report.html contains zero `<img>` and zero SVG `<image>` elements (grep count 0 each): no Street View or any raster photograph is embedded in the saved report.
 - The only "Aerial"/"photograph" text is the scope line "Not yet: … Aerial and street photographs" (page-1.png and report.html); no Esri or other raster imagery is used anywhere in this report.
 - services/api/tests/drawings/report/test_location_sheet.py::test_s4_no_photo_no_empty_frame_no_photo_wording passed in my frozen-head run (91 passed) and asserts no photo/street-view/aerial wording and no `<img>` in the location sheet.
 - Stays open: the "Esri imagery only within its agreement, with attribution" and "read both sets of terms before building" clauses apply when imagery is actually added; none is added here, so that part of R551 stays open in the registry.

ROW D-090-R843 — PASS
 - Page 3 "What constrains the design?" (print-w22g/page-3.png) draws the subject lot outline (coral "Lot 70") among adjoining lots (Lot 1/11/61), named streets as areas with mapped widths (NORTHERN BOULEVARD "100 ft mapped width", 215 STREET/215 PLACE/216 STREET "60 ft mapped width"), a grid-north arrow, a scale bar (0/100/200 ft), edge-length dimensions (103.88/99.98/99.98/101.71 ft) and a legend of only the drawn kinds.
 - The caption states the measurement basis and limitation: "Sources: NYC City Planning, MapPLUTO (edited 9 Sep 2026); … Map geometry only; tax boundaries do not establish the legal zoning lot; nothing is surveyed."
 - The lot-only fallback with its limitation line is exercised by test_s6_without_map_data_one_line_never_blank and test_c4_constraints_falls_back_to_lot_only_when_a_layer_is_unavailable (both passed): missing context is stated, never a false complete map.
 - Stays open: drawn yards/setbacks are not on the plan (ruling Y6 — the engine computes no building position/yards/setbacks yet); they appear only textually in the constraints table, so that drawn element of R843 stays open across M5-T154/M5-T155/M5-T156.

ROW D-090-R893 — PASS
 - On page 3 the supporting notes sit in the figure caption (not a notes column) and the street names plus surrounding context are drawn inside the figure (streets, neighbours, existing buildings), matching the orchestrator's reading that the drawing kit now draws them.
 - No raw terms appear: a tag-stripped scan of print-w22g/report.html found no dataset id (5zhs), "via NYC Open Data", FeatureServer, OwnerName, OBJECTID, Street_NM, Streetwidth, ZONEDIST, EPSG, http, or any snake_case token in visible text.
 - The report prints at its stated size: pdfinfo reports 9 pages at 594.96 x 841.92 pts (A4), and my own run of print-w22e/overflow.cjs on report.html returned W=688, docW=688, n=0 — nothing wider than the printable width, so text is not shrunk.
 - Stays open: R893 is also bound to M5-T151/M5-T152; any further page-overload concerns on those report sections stay with them — M5-T156's site-plan share is satisfied.

ROW D-090-R923 — PASS
 - The report now prints context maps (neighbourhood map + block close-up on page-2.png, site-context plan on page-1.png and page-3.png), so the scope-inventory claim is backed by real supported maps.
 - "Context maps" shows under "In this report" (page-1.png) only because maps are printed; test_s5_context_maps_moves_only_when_printed (passed) asserts it returns to "Not yet" when no maps are present, so the claim is never false.
 - This satisfies the owner's "include useful supported maps or correct that claim": useful supported context maps are now included and the claim is accurate.
 - Stays open: a zoning-district context map specifically is not printed (only location/context maps), so any zoning-map element of R923 stays open under its broader M5-T151/M5-T152 binding.

ROW D-090-R936 — PASS
 - The site drawing is titled and shows the lot among its surroundings: page-3.png, the page-1.png compact figure and the page-2.png block close-up all draw named streets as streets (mapped widths 100/60 ft), the corner (Northern Blvd & 215 Place), neighbouring lots and existing building footprints — not an isolated outline.
 - test_page1_carries_the_summary_frame_site_plan and test_s1_location_sheet_opens_page_type_two passed, confirming the compact and full site-context plans sit on the right sheets.
 - I inspected the printed pages myself; the lot reads as a corner lot among its neighbours, answering the owner's "a rectangle on an angle / no reference where he is."
 - Stays open: R936 is also bound to M5-T154 (map data) and M5-T155 (the drawings themselves); M5-T156's share is the report wiring/placement, which is satisfied.

ROW D-090-R937 — PASS
 - Page 2 "Where is the lot?" (page-2.png) opens page type 2 with a neighbourhood map (north-up street network, subject lot marked, scale 0/500/1,000 ft) and a block close-up, each captioned.
 - The captions name sources and dates in plain words — "NYC City Planning, MapPLUTO (edited 9 Sep 2026); NYC building footprints (edited 27 Sep 2026); NYC Digital City Map street centre lines (edited 1 Dec 2025)"; test_s1_captions_name_sources_and_their_dates (passed) pins those three dates.
 - test_s1_location_sheet_opens_page_type_two (passed) asserts "Where is the lot?" precedes "What constrains the design?" and that the location sheet holds two figures/SVGs.
 - Stays open: the maps and their data come from M5-T155/M5-T154; M5-T156's share (the location sheet on page type 2 with captions) is satisfied. A city-overview-scale map is optional — the row's "city OR neighbourhood scale" is met by the neighbourhood map.

ROW D-090-R938 — PASS
 - The report now has a property-location page ("Where is the lot?") plus coloured, labelled drawings at stated scales (scale bars on pages 1/2/3), which I inspected directly against the competitor sample's property-location page; it reads as a bespoke location feature, not a default template.
 - The independent visual-quality-reviewer recorded PASS at 6c8c9f7d after its corrections T155-C1/T156-C1/T156-C2 (project-control/reports/M5-T156-reviews.md); I confirmed those fixes on the printed pages (subject lot coral-filled above the existing-building dashed outline; two co-equal wide maps on page 2; 9 pages with no near-empty page).
 - Stays open: the "building's shape shown on its lot" element is NOT delivered — the building is not placed yet (honestly shown by the not-placed line), and the final "looks like my competitors" sign-off is a subjective judgement from an AI visual review only (the ten-second test with a real architect was NOT run), so that part of R938 stays open.

ROW D-090-R939 — PASS
 - The engine does not place the building yet, so the report prints the fixed line "No building is placed on this plan yet: the program does not yet work out where a building sits on the lot." on the site plan (page-3.png) and the scenario sheet (page-5.png), and labels the floor stack "Floor-stack section (Illustrative): drawn from the schedule only, with no placement on the lot."
 - No proposed building footprint is drawn on the subject lot; test_s3_not_yet_placed_on_site_plan_and_scenario_sheet (passed) asserts the fixed sentence on both sheets and that the document's raw reason text is never spliced in.
 - Stays open: the primary obligation — a building footprint placed on the site plan — waits for the engine (backlog DB-227); the required fallback (say plainly it is not placed) is met, so M5-T156's share is satisfied.

ROW D-090-R940 — PASS
 - The location page carries no street photo and nothing implying one: zero raster images in report.html, no empty figure frame (test_s4 asserts location `<figure>` count == `<svg>` count), and street-photo wording appears nowhere except the scope "Not yet" list.
 - The figure grid is laid out to take a third figure later without a redesign (two co-equal wide maps stacked; test_location_page_layout_two_co_equal_wide_maps passed; the presentation-contract entry states "The stack can take a third figure later without a redesign").
 - Stays open: opening a paid Google account and checking Google's terms before any street-photo work are future owner/actions, not this task, so that part of the decision stays open in the registry.

(3) BINDING B1–B5
 - B1 PASS. Base (main 9ab3a47e) requirements.json = 933 rows; frozen head = 940. R934–R940 are new and match the captured sources (source-082 rows R934–R939, source-083 row R940) in quoted fragment, classification and source_ref; NO pre-existing row's `text` changed (row-by-row compare). The only task_ids appends are R551 (+M5-T156), R843 (+M5-T154/M5-T155/M5-T156), R893 (+M5-T156), R923 (+M5-T156); no other field on any row changed. manifest.audit_log records the two amendments (R934–R939 pending at 18:36:53Z; R940 pending at 18:42:30Z) and the M5-T156 applicability bind at 18:56:14Z with the content-digest resync in the same commit — no post-capture text edits.
 - B2 PASS. tools.directive_registry.sha256_text_artifact(requirements.json) = 99bcd267cee2fb1bf8414f79d12daf0d961f3fc8c4053511abc6cb9bbb5da235 == manifest.requirements_content_digest_sha256. source-082 digest 7604c8f4d5f618318ad5cb9c7640d18e4f6a4f3004109c4b5550d39abd817dda and source-083 digest 2a6675af06e9bc9ee455b9d5c454237b1603faa17790085e80a0f6f82fd4badd equal the manifest's recorded content_digest_sha256. `python tools/validate_directive_compliance.py --check` exited 0.
 - B3 PASS. verification.json holds exactly one M5-T156 row; applicable_requirement_ids == the 9 cited ids; every requirement state "pending"; verifier "" (empty); reviewed_sha null.
 - B4 PASS. registry.evaluate_task_refs(M5-T156 packet) returned ok=true, applicable_ids == cited_ids (the 9), missing_ids=[], invalid_refs=[].
 - B5 PASS. registry.derive_applicable over all active directives yields exactly the 9 D-090 ids for this task and nothing uncited; no other active directive binds a requirement to M5-T156.
 - Gates: G0/G2/G3/G4 all recorded PASS (G2 orchestrator self-check, G3 code-reviewer, G4 qa-engineer); G2/G3/G4 at one content identity reviewed_sha 2341590e4d49…, G0 at the contracting head 86df73c15…; the packet's required_gates are exactly G0,G2,G3,G4 (no G5 for this task). CI runs 38097919683 (pull_request) and 38097916934 (push) both conclusion "success" at headSha 6c8c9f7d (21 jobs, all success: api, web-e2e, control-plane, modularity, web, dependency-security, secret-scan, context-budget). Product blobs are byte-identical from 6c8c9f7d through 2341590e to 7adc476 (diff touched only project-control/), so gate records and CI represent the frozen head.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided: (a) the blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules and the task's reports are unchanged from 7adc476; (b) the 9 rows' text and their M5-T156 binding are unchanged and verification.json still carries the pending M5-T156 row; and (c) the only intervening commits touch project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of M5-T154/M5-T155 on this branch, and/or a main-line merge that changes none of the predicate's files. I confirmed the predicate currently holds from 6c8c9f7d to 7adc476 (the intervening commits 2341590e and 7adc476 touched only project-control/).

(5) REQUIRED CORRECTIONS
 - None. (Prohibited-action check clean: M5-T156 is in state.json active_tasks, not accepted_tasks; the branch is not merged into main; the wave diff changes no services/api/requirements*, pyproject.toml, package.json, package-lock.json or .github/ file — the only "requirements.json" in the diff is the directive registry file.)

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The ten-second test with a real architect and a real screen-reader pass (need a person) — not run; the "looks like my competitors" sign-off (R938) rests on an AI visual review only.
 - The faithfulness of the recorded window pack to live NYC data (MapPLUTO/building footprints/DCM) — I used the recorded fixture via the real connectors; its byte-integrity is M5-T154's share (the QA reviewer verified the three recording digests against the MANIFEST by hand, now guarded by added tests).
 - CI did not literally run at 7adc476 or 2341590e; I relied on CI "success" at 6c8c9f7d plus the proof that product blobs are byte-identical through the frozen head. A fresh full CI pass at the exact merged head (R639) is the orchestrator's integration step.
 - Whether Google's terms permit printing its street photos (R940 future check) — not applicable to this task; no such work was done.

END-OF-REPORT
````
