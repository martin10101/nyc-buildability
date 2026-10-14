# M5-T166 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c3b3c9abb7bbd691a799c5e43f6e7e8ac1a9676d` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R014, R015, R016, R044, R052, R053, R074, R077, R115, R116.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 02:39 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T166 (directive D-094, 10 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is not a human or professional/legal review. Read-only: I wrote no file, made no commit, ran no project_control write, started no server, and touched no ports 3000/3001/8000. I ran tools/validate_directive_compliance.py --check once (exit 0) and four focused pytest files (60 passed). All task evidence was read through git plumbing at the frozen head; I treated every report/map/gate record as a claim to reproduce. No D-090 row is bound to this task; all 10 rows are D-094.

(1) HEAD VERIFIED
 - git -C /root/project/w-wave20 cat-file confirms c3b3c9abb7bbd691a799c5e43f6e7e8ac1a9676d exists on task/wave24-report-v3 (base main b4704161); the working tree has moved to e27bc2a0 (other wave tasks commit there), so I read every row's evidence via `git show c3b3c9ab:<path>`, never the working tree.
 - The frozen head is an ancestor of the live head; this task's material files are byte-identical 5e362d7f -> 7c831652 -> c3b3c9ab (only control-plane files were added at c3b3c9ab), so the submission identity and the G1-G4 records carry.

(2) ROWS (D-094, numeric order; THIS TASK'S SHARE)

ROW D-094-R014 — PASS
 - Page 2 renders the neighbourhood locator only and page 3/4 the dimensioned close-up; I ran test_location_sheet.py::test_location_page_is_the_locator_only and test_constraints_page.py::test_s5_at_most_three_map_figures_each_a_distinct_job (60 passed, exit 0).
 - No generated photograph: test_s4_no_photo_no_empty_frame_no_photo_wording asserts no "<img" and no "photo"/"street view"/"aerial" wording; page-02.png and hi-04.png show only drawings.
 - This task's share (the two maps of pages 2-3) is met; the "one locator + one close-up" rule lives in the design contract (M0-T193, accepted) and licensed site imagery stays unavailable, so nothing else is owed here now.

ROW D-094-R015 — PASS
 - close_frame_dimensions.py anchors each dimension to the edge's own projected vertices; test_s1_dimension_endpoints_lie_on_their_edge_vertices (<=0.01 ft) passed in my run.
 - In hi-04.png the subject Lot 70 and its edge-sharing lots 1/11/61 dominate, with 103.88/99.98/99.98/101.71 ft drawn on the four edges.
 - test_s4_close_frame_contents (lot numbers {70,1,11,61}, label_problems==[]) passed; applicability is M5-T166+BOOTSTRAP only, so nothing stays open.

ROW D-094-R016 — PASS
 - page-03.png shows a compact 3-row x 2-program heights table (Min base 30/30, Max base 45/45, Max building 55/65 ft), replacing the six repeated rows the owner flagged.
 - test_s7_heights_table_is_three_by_two_from_the_document and test_s7_coverage_once_and_no_bare_not_shown passed; the long per-row label is gone and "Maximum lot coverage" appears once.
 - Applicability is M5-T166+BOOTSTRAP only; nothing stays open.

ROW D-094-R044 — PASS
 - Every drawn figure traces to the gis outline source edge:{outline.source}/0#{i}; test_s1_no_tax_map_value_is_drawn passed and the 2.22 ft sliver is left undimensioned.
 - No yard/court/setback/envelope geometry is drawn: test_s4_no_yard_or_setback_area_is_drawn passed; the basis note is a fixed honesty string, not fabricated data.
 - The drawn edge lengths equal NB-04 E4's recorded gis values (103.87921/99.97647/99.97605/101.70896 ft); this task's share is met, and R044 also binds M5-T164/M5-T176 for their own drawings.

ROW D-094-R052 — PASS
 - test_s5_at_most_three_map_figures_each_a_distinct_job passed: locator 1, site_context_plan 2 (page-1 compact + page-3 large), block_map 0 — each a distinct job.
 - hi-04.png is a useful dimensioned site drawing, not a diagram that merely repeats "three floors".
 - This task's share (distinct map jobs + a useful site drawing) is met; replacing the three-box scenario diagram stays open for the scenario-sheet task (M5-T173, not yet contracted).

ROW D-094-R053 — PASS
 - hi-04.png shows source-based geometry: anchored dimension lines, street names with mapped widths (NORTHERN BOULEVARD 100 ft, 215 PLACE/215 STREET 60 ft), a north arrow ("Grid north") and a scale bar (0-50-100 ft).
 - test_s2_every_measured_label_is_at_least_8_5pt_no_collisions passed: the load-bearing data labels (dimension/street/width/lot) are >=8.5 pt and the build fails rather than shrinks.
 - Open residual: the legend "No building placed" at 8.0 pt and scale-bar numerals at 7.5 pt sit below the 8.5 pt floor (read acceptably; tracked DB-246, a kit-typography task), and "mark illustrative geometry distinctly" is not exercised because no illustrative placement is drawn here (that belongs to the engine/scenario task).

ROW D-094-R074 — PASS
 - Page 2 is the locator only and pages 3/4 carry the dimensioned close-up; test_location_page_is_the_locator_only ("Block close-up" absent, one figure) and test_s5 (<=3 distinct maps) passed.
 - Dimensions are attached to the lot boundaries: test_s1_dimension_endpoints_lie_on_their_edge_vertices passed and I saw the four edge dimensions in hi-04.png.
 - This task's share (pages 2-3) is met; before/after screenshots of every changed page across the whole report belong to the final export task (M0-T195, not yet contracted).

ROW D-094-R077 — PASS
 - Within scope two repeated explanations were reduced to once: map_caption.py drops "Map geometry only..." so it prints once (test_s6_map_geometry_only_appears_once) and the full "No building placed" sentence moves off the site page to the scenario sheet (test_s8...), both passed.
 - The site-section visible-word count stays within its baseline (test_s10 <=199).
 - This task edits pages 2-3 only; removing repeated explanations on pages 6-9 and building one organised evidence appendix stay open for the appendix/option-comparison tasks (M0-T194/M5-T169, not yet contracted).

ROW D-094-R115 — PASS
 - In hi-04.png (byte-identical to the owner's draft-2 PDF, sha256 dcc59288) the close-up reads cleanly: figure-only labels, the basis stated once under the drawing ("All dimensions: city map outline, not surveyed."), no repeated basis phrase, no word crossed or touched by any line.
 - close_frame_dimensions.py places every label with cross_max_len=0.0 and a white halo; test_s2_no_line_crosses_any_label_own_dimension_line_included, test_s14_every_label_sits_on_a_white_background, and the forced fail-not-shrink tests passed in my run.
 - The visual-quality-reviewer's by-eye print check at 68d417fe PASSed (advisories only); applicability is M5-T166+BOOTSTRAP only.
 - Open: polish advisories only (215 PLACE name/width offset; "101.71 ft" near "Lot 11"; the single-basis note placed outside the collision-checked placer) — all legible, no collision, tracked DB-249.

ROW D-094-R116 — PASS
 - git show 68d417fe -- ARCHITECT_PRESENTATION_CONTRACT.md is exactly two hunks (the Page-2 close-up sentence and the Wording gis clause): basis once under the drawing, figure-only labels, short tag only when bases mix, dated 2026-10-12 citing question K1; nothing else in the contract changed.
 - hi-04.png drops neighbour addresses (lot numbers {70,1,11,61} kept) and draws neighbours lighter than the coral subject; test_s15_no_neighbour_addresses_but_lot_numbers_stay, test_s15_neighbour_buildings_are_drawn_lighter_than_the_subject and test_s14_s15_apply_to_the_page_one_compact_close_frame passed.
 - The second draft PDF the owner received 2026-10-12 is byte-identical to the render I inspected (sha256 dcc59288); the by-eye check passed.
 - Open: co-fitting the close-up with its tables on one page (the report is 10 pages) needs report/layout.py, an M5-T165 file forbidden to this task — legitimately routed out (producer STOP item 6), tracked DB-249; the K1 drawn requirements are all met.

(3) BINDING B1-B5
 - B1 PASS: the 8 non-K1 rows (R014/R015/R016/R044/R052/R053/R074/R077) gained "M5-T166" in applicability.task_ids in the contract commit 574b886e (absent at 574b886e^, present at 574b886e); R115 and R116 gained it in the scope-correction commit f96a087f; each row's text and classification are byte-identical 574b886e^ -> c3b3c9ab (R115/R116 are new rows, unchanged by this task).
 - B2 PASS: I recomputed the LF-normalised sha256 of requirements.json at c3b3c9ab = bdcfaac5f6e14f1c... == manifest requirements_content_digest_sha256, and the id digest = c9eb6c1538fb59f3... == manifest requirements_id_digest_sha256; validate_directive_compliance.py --check exits 0.
 - B3 PASS: D-094 verification.json (schema directive_verification/v2) has exactly one M5-T166 row, producer "geospatial-engineer", verifier "" (empty), reviewed_sha null, listing all 10 ids each state "pending".
 - B4 PASS: the D-094 rows whose applicability.task_ids contain M5-T166 are exactly the 10 cited in the packet's directive_refs (applicable == cited; no cited-nonapplicable, no uncited-applicable; no milestone/type/path rule pulls in extras).
 - B5 PASS: across all 93 directive registries at c3b3c9ab only D-094 binds M5-T166 (10 rows). Gates: G0 PASS (reviewed_sha f96a087f, re-recorded at the scope-correction head); G1 data-contract-verifier, G2 orchestrator (self-check), G3 code-reviewer, G4 qa-engineer all PASS at reviewed_sha 7c831652 with one content identity (content_manifest_sha256 678d9912...); material files are byte-identical 7c831652 -> c3b3c9ab (only control-plane files added); CI workflow run 38498777681 at c3b3c9ab is success across all 21 jobs (incl. api ruff+pytest, web-e2e, web, control-plane, modularity, contracts).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review iff the blob-level predicate holds: the packet's allowed-path material files keep their frozen-head blob ids — close_frame_dimensions.py 25d078f8, context_scene.py d0237a98, site_context_plan.py 2116ab34, page_location.py bc4af2b9, page_site_context.py 531a2a1e, map_caption.py d6d6deb2, ARCHITECT_PRESENTATION_CONTRACT.md d3e85388, NB-04 3f27c997, test_site_context_close_frame.py 0a635ce1, test_constraints_page.py c73601d0, test_location_sheet.py 7d972812, test_report_read_context.py 9e0f6cf6, report-print.flag-on.spec.ts c312b448 — AND the 10 rows' text and their M5-T166 binding in requirements.json are unchanged (content digest bdcfaac5..., id digest c9eb6c15... still match D-094's manifest).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any OTHER file — other tasks' source under services/, apps/, packages/, docs/, .claude/; their packets, gates, reports, directive bindings; ledger state — plus this task's own acceptance records (its task json, gate records, the M5-T166 verification.json stamp, the evidence map), and a merge of the main line that changes none of the predicate's files. If any listed blob id or the row text/binding changes, a fresh review is required.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-fetch live MapPLUTO/DCM/tax-map sources; I verified the drawn edge lengths and the 100 ft / 60 ft mapped street widths against NB-04's sha256-pinned evidence packs and the gis outline source (as the producer and G1/G3/G4 did), not the live endpoints.
 - I did not run the full api suite or the Playwright report-print e2e myself (forbidden / thin-client; ports untouched); I ran only four focused test files (60 passed, exit 0) and relied on CI run 38498777681 at c3b3c9ab (all 21 jobs success) for the full suite, the forbidden-to-me test_report_pages.py S7/S10 word budgets, and the e2e.
 - I inspected the close-up from the build-server renders hi-04.png/page-02.png/page-03.png and confirmed byte-identity with the owner's draft-2 PDF (sha256 dcc59288); I did not open the PDF in a viewer or click live PDF hyperlink destinations.
 - The R6B reference cases in docs/reference-cases/R6B/cases/ settle the rear-yard/short-block reading (NB-03), which this task deliberately does not draw (no yard/setback geometry), so no row here turns on a figure they settle; I did not re-derive those.
 - I am an AI agent; this is not a human or professional/legal review, and nothing here certifies the report's feasibility conclusions.
END-OF-REPORT
```
