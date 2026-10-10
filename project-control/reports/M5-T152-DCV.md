# M5-T152 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63` (branch `task/wave21-report-redesign`, review copy `read in place (/root/project/w-wave20)`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R795, R893, R896, R912, R913, R914, R915, R920, R921, R922, R923, R924, R927.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. No VIOLATED or UNVERIFIABLE row; every applicable requirement is SATISFIED for M5-T152's share from primary evidence.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 11:23 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T152 (directive D-090, 13 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only verification reproduced from primary evidence; it is not a human or professional review. I produced none of the work or records under review.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 1dd5fb51b8f894f1b009af294a10d5d4d3dbdb63 on branch task/wave21-report-redesign; base = d459358a4de6d4fa369e8ec039ba4cc7ac318e9b (confirmed). All source was read from this commit via `git show 1dd5fb51b8f8:<path>`.
 - Permitted focused tests from services/api with the lanes venv passed: test_geometry_streets.py + test_engine_wording_m5_t152.py + test_report_frame.py = 52 passed, exit 0.
 - `python tools/validate_directive_compliance.py --check` exit 0 (direct exit code).

(2) ROWS

ROW D-090-R795 — PASS
 - services/api/app/scenario/three_answers/geometry.py `_build_streets`/`build_geometry` draw from the measured tax-map outline (`_local_feet_ring(measured)`) and the engine's confirmed frontages; no conceptual geometry is substituted for calculated dimensions.
 - services/api/app/drawings/kit/section.py `draw_floor_stack` draws every band and number from `alternative["floor_schedule"]` only (test_report_frame.py::test_s3 asserts every drawn number is a schedule figure and bands==len(schedule)).
 - The printed drawings identify their basis as the row requires: site plan caption "Lot outline: Approximate — tax map" (print-final3/page-2.png) and floor-stack caption "Floor-stack section (Illustrative): drawn from the schedule only, with no placement on the lot." (page-4.png).
 - Stays open: R795 also governs other drawings/PDF surfaces across D-090; it remains pending in the registry for the rest of the directive.

ROW D-090-R893 — PASS
 - The report-frame site plan draws no notes column: tests/drawings/kit/test_report_frame.py::test_s2_site_plan_report_fits_a4_and_is_legible asserts `data-role=='note'` texts == [] over all fixtures (passed in my run).
 - print-final3/page-2.png shows the street names "Northern Boulevard" and "215 Place" and the edge dimensions (103.88 / 99.98 / 2.22 / 101.71 / 99.98 ft) inside the drawing, supporting notes moved out, at A4.
 - site_plan.py `draw_site_plan(..., frame='report')` composes the plan at ≤182x150 mm with every label ≥7 pt (the kit `labels_below`/size assertions in test_s2).
 - Stays open: M5-T151 assembles the full site page; R893 also binds M5-T151 and stays pending in the registry until the whole report page is verified.

ROW D-090-R896 — PASS
 - The drawn outline is the measured tax-map polygon, not a rectangle: the benchmark geometry.lot_outline is a 5-vertex ring whose shoelace area I computed = 10,387.99 sq ft, equal to the stated tax-map area; it is not reshaped to the recorded 10,075 sq ft.
 - The drawing and the measurement explanation agree: page-2.png labels the plan "Approximate — tax map" and the page text names the tax-map outline area as 10,387.99 sq ft, so the drawn area matches the explanation.
 - M5-T152 adds streets onto that outline (geometry.py) without changing it; the measured-outline drawing itself is M5-T150's share.
 - Stays open: R896 also binds M5-T150 and stays pending in the registry for its share.

ROW D-090-R912 — PASS
 - Real dimensions and street relationships are drawn from the spatial engine: test_geometry_streets.py::test_s1 generates the document through the real evidence entry and confirms geometry.streets carries the engine's two confirmed frontages ("215 Place" 99.98 ft, "Northern Boulevard" 103.88 ft), each point on an outline edge within 0.01 ft.
 - A real schedule diagram is produced: section.py `draw_floor_stack` and page-4.png show three storey bands with floor-to-floor/top heights read from the floor schedule.
 - Map support is added: drawings/maps/__init__.py gains `frame='report'` on render_location_map/render_zoning_map so real context maps can be drawn when map data is present.
 - Stays open: "the report uses real maps … wherever supported" is a whole-PDF/visual obligation; maps are not yet fetched (see R923), and R912 stays pending in the registry for the full-scope visual verification.

ROW D-090-R913 — PASS
 - Missing geometry is never invented: geometry.py `_build_streets` returns [] on the direct-engine path, on unconfirmed frontages, and when prepared/measured/site-geometry is absent (test_s1 mutation proof + test_s7 asserts streets absent and nothing invented when geometry is not_available).
 - No prose block replaces a drawing: in the partial-data case the report emits a short limitation line and no SVG (QA reviewer's Check 3; the drawing kit returns Unavailable rather than prose), and the measured outline is drawn where available (page-2.png).
 - The floor stack returns Unavailable with no schedule (test_s3_floor_stack_unavailable_without_a_schedule), not an invented shape.
 - Stays open: R913 also binds M5-T151 and stays pending for the whole-PDF review.

ROW D-090-R914 — PASS
 - Report frames are sized for A4, not an oversized sheet: test_report_frame.py asserts width ≤515.9 pt (182 mm) and height ≤425.2 pt (150 mm) for the site plan, massing and floor stack over all fixtures.
 - No text prints below the minimum: test_s2/test_s3 assert `labels_below(svg, 7.0) == []`, with a mutation proof (a label shrunk to 6.5 pt is caught); print-final3/page-2.png and page-4.png are legible at A4 (no ~5 pt notes).
 - render_floor_stack/draw_site_plan(frame='report') produce report compositions (section.py REPORT_MAX_W_PT/REPORT_MAX_H_PT = 515.9/425.2) rather than a 13×20.5-inch sheet shrunk to fit.
 - Stays open: R914 also binds M5-T151 (overall page sizing) and stays pending in the registry for the full set of page types.

ROW D-090-R915 — PASS
 - The site page shows a site composition in place of a notes column: page-2.png draws the lot, its two named frontages (Northern Boulevard, 215 Place), edge dimensions and a "Lot line" legend, with the notes column removed.
 - The composition is backed by tests: test_s2 asserts no note-role text, no overlapping labels, and that every drawn number comes from the results (numbers_not_in_input == []).
 - Street names/frontages are drawn only where the engine has confirmed frontages (geometry.py status==FRONTAGE_CONFIRMED guard), matching the row's orchestrator reading that otherwise the page states what is missing.
 - Stays open: R915 (M5-T152-only in the registry) stays pending until the directive is closed; the full-page assembly around this drawing is M5-T151's.

ROW D-090-R920 — PASS
 - The two lot areas are explained with their bases: page-2.png text reads "The floor-area allowance holds if the recorded lot area of 10,075 sq ft is confirmed (the recorded figure and the tax-map outline area of 10,387.99 sq ft disagree; neither is chosen automatically)."
 - The drawing matches the area it is said to show: the drawn outline's shoelace area (my computation) = 10,387.99 sq ft = the tax-map figure the caption names; geometry is not reshaped to a preferred figure.
 - M5-T152's share is drawing the measured outline and carrying its edge dimensions (99.98/103.88/2.22/101.71 ft) from the outline, never typed (test_s2 numbers_not_in_input == []); the explanatory sentence is M5-T151's page text.
 - Stays open: R920 also binds M5-T151/M5-T150 and stays pending in the registry for their shares.

ROW D-090-R921 — PASS
 - The engine's stale "building options are not known for this lot" sentences are removed: three_way_document.py reworded SHORTFALL/BEST_COMBINATION/ADDON_GAIN/FLOOR_STACK reasons to "it needs a building fitted to the site, and none is fitted yet"; the benchmark fixture contains "not known for this lot" 0 times (my grep) and page-3 limitations 2 and 5 read the new wording.
 - Statements agree across the data: the benchmark's single building_alternatives[0].below_min_base == False, consistent with Building B reaching the minimum base height (page-4 floor stack shows the "Minimum base height 30 ft" line reached); no page carries a "below minimum base height" note.
 - test_engine_wording_m5_t152.py asserts none of the four follows-withheld reasons says "building option(s) … not known" (mutation-proofed).
 - Stays open: the report-page min-base-note logic/reconciliation is M5-T151's share; R921 also binds M5-T151 and stays pending in the registry for it.

ROW D-090-R922 — PASS
 - The engine's user-facing "achieved" label is gone: building_option.py label "Achieved zoning floor area (building option)" → "Scheduled …" and result_way_inputs.py LABELS["achieved_zoning_floor_area"] "Building option: achieved …" → "… scheduled …"; the benchmark and printed report contain no user-facing "achieved" (my grep count 0; remaining "achieved" tokens are internal variable/key names, not displayed text).
 - The schedule is worded as the owner specified: page-3 and page-4 show "Scheduled floor area: 20,150 sq ft; site fit unverified" (Conditional) for Building B/Option 1.
 - "no allowance left unused" is not used in engine output (benchmark count 0); it appears only in app/drawings/report/labels.py as the forbidden-word detection list (M5-T151 file), not as emitted text.
 - Stays open: R922 also applies to the website (M5-T153) and to M5-T151; the engine label is M5-T152's share, while the website string enforcement stays pending in the registry under M5-T153.

ROW D-090-R923 — PASS
 - The scope inventory does not falsely claim maps: print-final3/report.txt "What this report covers" lists "Context maps" under "Not yet", correcting the earlier claim.
 - M5-T152 adds the capability to draw supported maps in the report: drawings/maps/__init__.py adds `frame='report'` to render_location_map/render_zoning_map (keeping attribution/notes reachable as labels), per the evidence map and the maps report-frame test (S4, reproduced by the data/QA reviewers).
 - The report does not yet fetch map data, so it correctly states the limitation rather than inventing maps.
 - Stays open: including the actual location/zoning maps once map data is fetched is future report work; R923 also binds M5-T151 and stays pending in the registry.

ROW D-090-R924 — PASS
 - No field/code word appears in the report-frame drawing text: test_report_frame.py::test_s6_no_field_or_code_word_in_the_report_drawings scans the site-plan and massing SVGs for snake_case over all fixtures and asserts none (passed in my run).
 - The printed drawings (page-2.png, page-4.png) carry no HTTP checks, internal ids, or backlog words; snake_case appears in report.html only as data-role/data-source provenance attributes, not as visible glyph text (data-contract-verifier corroboration).
 - M5-T152's share is the drawing text; it touches no app/ or report-prose surface (forbidden_paths include apps/** and drawings/report/**).
 - Stays open: the whole-report developer-info scan (page prose) is M5-T151/M5-T153's share; R924 also binds them and stays pending in the registry.

ROW D-090-R927 — PASS
 - The change is made in reusable modules, not a hand-polished sample: the M5-T152 diff touches services/api/app/drawings/kit/* (section.py, site_plan.py, massing.py, furniture.py, __init__.py), drawings/maps/* and scenario/three_answers/* (geometry, building_option, result_way_inputs, three_way_document), plus tests/fixtures/register — no standalone hand-drawn page.
 - The report reuses these primitives: the printed site plan and floor stack are produced by the kit renderers invoked by the report generator, not by bespoke sample artwork.
 - No file under a hand-sample location was added; the benchmark fixture change is data regenerated from the engine, not a hand-edited drawing.
 - Stays open: R927 also binds M5-T151/M5-T153; it stays pending in the registry for their presentation-logic changes.

(3) BINDING B1–B5
 - B1: requirements.json base(d459358a)→head(1dd5fb51): R795/R893/R896 pre-exist with byte-identical text and M5-T152 newly appended to applicability.task_ids (R893 also +M5-T151); R912–R927 are absent at base, present at the capture commit 9c564ad8, and byte-identical capture→head. All 34 new rows R900–R933 are byte-identical capture→head (no post-capture text edits). Each of the 13 head row texts equals its source-081 Reading-table fragment and classification (R912/R915/R920/R921/R923 obligation; R913/R922/R924/R927 prohibition; R795 source-078, R893/R896 source-080). PASS.
 - B2: directive_registry.sha256_text_artifact(requirements.json) = 030652450f861cc0b4785cb8b44f6867c6e734cbbf453b58c9211727dbacdaa8 == manifest.json requirements_content_digest_sha256. PASS.
 - B3: verification.json has exactly one M5-T152 task_verifications row listing the 13 ids, each state "pending", evidence [], producer "geospatial-engineer", verifier "" (empty), reviewed_sha null. PASS.
 - B4: reg.evaluate_task_refs(M5-T152) → ok True; applicable_ids == cited_ids == the 13 rows; missing_ids [], invalid_refs [], unresolved []. PASS.
 - B5: reg.derive_applicable(M5-T152) across all 90 active directives returns exactly the 13 D-090 rows and an empty unresolved list; nothing else applies uncited; manifest.affected_tasks includes M5-T152 and audit_log records the 2026-10-10T07:36:31 binding. PASS.
 - Gates: G0 PASS (orchestrator, sha 87e13f6e contract head); G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) all recorded at one head 88afbb47; the data-contract-verifier PASS is recorded in M5-T152-G3G4.md (Return 3 of 5). Reviews were done at 7f972796 (first) and f28d065f (corrected) with delta attestations that CARRY. CI run 38047040636 at f28d065f = success, 21 of 21 jobs (api, web-e2e, web-dependency-security now green after CI-1, modularity, control-plane, contracts all success). The diff f28d065f→88afbb47→1dd5fb51 touches only project-control/ files, so the material content CI verified is byte-identical at the frozen head. PASS.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head without re-review while this blob-level predicate holds: the git blob ids of services/api/app, services/api/tests, packages/contracts, docs/zoning-rule-review, docs/reference-cases, docs/design, apps/web/src, apps/web/e2e, apps/web/scripts, render.yaml, .github, tools, CLAUDE.md, .claude/rules and this task's project-control/reports files are unchanged from 1dd5fb51, and the 13 rows' text and binding (B1–B5) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of the other wave-21 tasks (M5-T151, M5-T153) on this branch, and a merge of the main line that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None. No VIOLATED or UNVERIFIABLE row; every applicable requirement is SATISFIED for M5-T152's share from primary evidence.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not render the full-scope PDF myself (read-only; no server; ports 3000/3001/8000 forbidden). I inspected the orchestrator-captured real-route artifacts in /root/project/lanes-runtime/owner-docs/session-2026-10-10a/print-final3/ (report.html, report.txt, report.pdf, page-1..6.png, report-request.txt returning 200), which reflect the frozen head's material content (unchanged f28d065f→1dd5fb51).
 - The human-performed passes the directive names (a ten-second real-architect read and a real screen-reader pass) need a person and were not done; they are not part of this task's automated share.
 - I ran only the three permitted focused test files; I did not run tests/drawings/maps/test_report_frame.py (S4) or the full api suite — I verified the maps report-frame via the drawings/maps/__init__.py diff and relied on the data-contract-verifier and qa-engineer S4 reproductions recorded in M5-T152-G3G4.md.
 - The website application of R922/R924 (apps/**) is M5-T153's scope (forbidden to M5-T152); I verified only the engine data feeding it.
 - Noted, not a row violation: the default-frame site-plan snapshots were regenerated under the orchestrator's rework-1 directive K2 (label-collision recompose), so the default frame is no longer byte-identical to the pre-wave baseline — this deviates from the literal X9(a) wording but was an authorized, recorded rework that changed no legal dimension value and bears on none of the 13 directive rows.

END-OF-REPORT
```
