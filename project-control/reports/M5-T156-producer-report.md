M5-T156 PRODUCER REPORT — "The report shows where the lot is". I am an AI agent (backend-engineer producer).

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-a73319db7ea2b332b
COMMIT: dcc23402c172243f3b274f6fc8d61e45998a4162  PARENT: 17ebd08a933e9affc23bcfd197a4c7dd2f44ddaf (the contract head). `git status --porcelain` empty.
NOTE on the report file: per the active harness instruction ("Do NOT Write report/summary/findings/analysis .md files; return findings directly as your final message"), I did NOT create project-control/reports/M5-T156-producer-report.md. This return is the producer report — save it verbatim to that path if the ledger needs it.

FILES CHANGED (15; all within allowed paths):
- services/api/app/drawings/report/page_location.py (NEW): the one-outline check (Y5, cyclic+reversal vertex match, 0.01 ft) and the "Where is the lot?" sheet (neighbourhood + block, or one short line; no photo, Y9).
- builder.py: resolves surroundings; picks the map-based site plan vs the lot-only plan; sets maps_present; feeds page 1 the site context plan.
- page_site_context.py: page type 2 opens with the location sheet, then "What constrains the design?" with the site plan among its surroundings and the Y8 not-placed line (old Context-maps section removed).
- page_decision_summary.py: page 1's figure becomes the site context plan report frame when available (Y10).
- page_scenario_sheet.py: adds the Y8 not-placed line.
- drawings_embed.py: embed_map composes the caption from the maps' note labels + each layer's provenance last-edited date (Y7).
- readers.py: results_lot_outline + not_placed_reason (reads /geometry/floor_plates/reason, drops any internal-field sentence, X6).
- layout.py: page break between the two sheets; location-figure spacing.
- api/v1/report_read.py: route asks get_report_map_context_provider for the same BBL; a provider error never fails the report (S7).
- apps/web/e2e/harness/fixture_api.py: report route bound to recorded_pack_provider(benchmark_215_16_northern_window).
- apps/web/e2e/report-print.flag-on.spec.ts: adds location-sheet assertions (title order, >=2 location SVGs, a dated caption, no image, no photo words); no existing assertion weakened.
- docs/design/ARCHITECT_PRESENTATION_CONTRACT.md: dated change entry 2026-10-10, D-090 R936–R940, plus page-type rows 1/2 amended.
- tests: new test_location_sheet.py (S1–S6, S8, S9 + mutation-catch tests), filled test_report_read_context.py (S7), Q3 in test_report_pages.py rewritten to the new flow.

SHEET ORDER (benchmark, 6 page types / 13 printed A4 pages): 1 Decision summary — "What can I potentially build?" (answers table; the site context plan flows to its 2nd printed page with the estimate/open items/coverage). 2 Site and context — opens with "Where is the lot?" (Neighbourhood map, then Block close-up, each captioned with sources+dates), then "What constrains the design?" (site plan among its surroundings, the not-placed line, constraints). 3 Option comparison. 4 Scenario sheet (not-placed line + floor stack). 5 Assumptions and open items. 6 Calculations and evidence. The location sheet lives inside page type 2; the page-type count stays six.

IMAGES LOOKED AT (headless chromium print-to-pdf from file://, no server; scratch): 
- page-01.png: decision summary — property, three answers (Conditional), clean; site figure pushed to page 2.
- page-02.png: site context plan (subject Lot 70 among neighbours + street areas), caption naming all three sources with "last edited" dates, estimate, open items, "In this report: … Context maps".
- page-03.png: "Where is the lot?" Neighbourhood map, north-up, subject marked, scale bar, caption with DCM source + date.
- page-04.png: Block close-up with lots/buildings/streets and a sources+dates caption (dense labels — M5-T155 rework territory, not judged here).
- page-05.png: "What constrains the design?" — lot-area basis, site plan among surroundings, the line "No building is placed on this plan yet: …", constraints table.
- page-07.png: option comparison unchanged (eleven options, bar chart).
- page-08.png: scenario Building B — carries the not-placed line and the Illustrative floor stack.
Composition reads correctly; the location sheet gives the "where is he" reference the owner asked for.

CHECKS (via /root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1):
- services/api `python -m ruff check .` → exit 0 (All checks passed).
- services/api `python -m pytest -q -p no:cacheprovider tests/drawings tests/api tests/contracts tests/journey` → 2798 passed, 6 skipped, exit 0 (174 s).
- root `python3 tools/modularity_check.py --check` → exit 0 (784 files, 0 failures; none of my files flagged; page_location.py 149 lines).
- root `python3 scripts/lanes/check_lane_paths.py --coverage` → exit 0 (LANE COVERAGE PASS, 9948 files).

MUTATIONS (scratch copy outside the repo, reverted/removed after):
1. Outline-check tolerance 0.01 → 1.0 ft: CAUGHT by tests/drawings/report/test_location_sheet.py::test_s2_moved_outline_drops_the_surroundings AND ::test_s2_tolerance_is_one_hundredth_of_a_foot (both FAIL; a 0.5-ft interior-vertex move wrongly matches).
2. A caption's source date removed (_layer_edit_date → None): CAUGHT by tests/drawings/report/test_location_sheet.py::test_s1_captions_name_sources_and_their_dates (FAIL: no caption carries "last edited").
Both pass on the unmutated sources.

STOP/BLOCKERS: none — no file outside allowed paths needed to change. No server started; ports 3000/3001/8000 untouched; nothing labelled Verified.

OBSERVATIONS for review (not defects I can fix in scope):
- The not-placed line reads "No building is placed on this plan yet: No floor plate is drawn: no placement on the lot is worked for any building." — faithful to Y8's template + the document's own first sentence (the second sentence, which names internal fields, is dropped per X6). Slightly doubled phrasing.
- Visible "BBL 4073340070" labels and a "NYC Open Data 5zhs-2jue" dataset id appear inside the M5-T155 drawings / M5-T154 attribution (report_context.py, both forbidden paths). Surfaced faithfully; the brief's note says judge page composition, not the drawings' insides, and M5-T155 is being reworked.
- Page type 1 is sparse on its first printed page because the report-frame site context plan (≈180×145 mm, the only frame M5-T155 exposes) breaks to the next page; faithful to Y10 ("page 1's figure becomes the report frame of the site context plan").

Requested status: awaiting_gate.
END-OF-REPORT


---

REWORK 1 RETURN (saved unchanged by the orchestrator):

M5-T156 REWORK 1 complete. I am an AI agent (backend-engineer producer).

COMMIT: 54a6a5cbf7abb57554f34dfc3deb7089fdeb952c  PARENT: c1d05fc0b792fa458df257ae1b150b502bcb33d5. git status clean. (No report file written, per harness instruction.)

PRINTED PAGES — now 7 A4 (was 13), none nearly empty, no lone line/row (rendered file:// via headless Chromium and looked at every page):
1 Decision summary — property, three answers, the COMPACT summary-frame site plan beside the answers, apartment estimate, open items, coverage (all on one page).
2 Where is the lot? — ONE page: the Neighbourhood and Block close-up summary thumbnails side by side, each titled and captioned (room left for a third figure).
3 What constrains the design? — lot-area basis, the full-size site plan among its surroundings (printed once), the fixed not-placed sentence, the whole constraints table.
4 Option comparison — shared limitations, allowance bar chart, eleven options, worked/not-worked.
5 Scenario sheet (Building B) — scheduled line, not-placed sentence, floor stack, why, floor schedule, what-not-checked, and the apartment estimate kept with them (no lone line).
6 Assumptions and open items — eleven assumptions, open-items table.
7 Calculations and evidence — inputs, allowance, envelope, provenance, Drawing notes (plain "Sources: … (edited …)" lines, no dataset id / "via NYC Open Data" / terms-of-use), status-label key.

Captions: one short "Sources: NYC City Planning, MapPLUTO (edited 9 Sep 2026); NYC building footprints (edited 27 Sep 2026); NYC Digital City Map street centre lines (edited 1 Dec 2025)." plus the drawing's own notes — each date once, no doubling, no dataset id. Not-placed line is the fixed sentence, never spliced.

CHECKS (lanes venv, direct exit codes):
- services/api `ruff check .` → exit 0.
- services/api `pytest -q tests/drawings tests/api tests/contracts tests/journey` → 2813 passed, 6 skipped, exit 0.
- `tools/modularity_check.py --check` → 0 failures, exit 0.
- `scripts/lanes/check_lane_paths.py --coverage` → PASS, exit 0.

Files changed (all in allowed paths): report/{builder,drawings_embed,layout,page_decision_summary,page_evidence,page_location,page_scenario_sheet,page_site_context,readers,sources}.py + new report/map_caption.py; tests/api/test_report_read_context.py; tests/drawings/report/test_location_sheet.py; report-print.flag-on.spec.ts; ARCHITECT_PRESENTATION_CONTRACT.md. (fixture_api.py and report_read.py from my first commit were already correct in the base head.)
END-OF-REPORT


---

REWORK 2 RETURN (saved unchanged by the orchestrator):

M5-T156 REWORK 2 complete. I am an AI agent (backend-engineer).

COMMIT: 1de64504e8902b55339d371f7b64dbbc9deaa3df  PARENT: fd63367ffd67d62c4b245551d96a1950d789c56e. Clean tree. No report file written.

PAGE COUNT: 8 A4 pages (rendered file:// via headless Chromium; pdftotext -bbox confirms max glyph x=555.7pt, content edge ~555.6, zero glyphs beyond the page — no caption runs off, FIX 1).
PAGE 1 (decision summary): property, the three answers, and the compact site plan beside them with a SHORT caption that wraps inside its bounded 88mm column; apartment estimate, open items, coverage — all on one page.
PAGE 2 ("Where is the lot?"): the full-width neighbourhood map on top (its own title, legend, north arrow, scale bar), then the compact block close-up in the left half with both captions (sources + notes) in the right half. Fits and fills one page; no empty frame; the full-size site plan stays only on "What constrains the design?" (FIX 2).

Note: the true unscaled layout is 8 pages (the earlier 7 was Chromium shrinking the doc to absorb the off-page caption — the very FIX-1 defect). Page 8 is a 4-row status-key continuation with a repeating header (allowed).

CHECKS (lanes venv, direct exit codes): ruff check . exit 0; pytest -q tests/drawings tests/api tests/contracts tests/journey 2814 passed/6 skipped exit 0; tools/modularity_check.py --check exit 0; scripts/lanes/check_lane_paths.py --coverage PASS exit 0.

Files (all allowed): layout.py, page_location.py, page_decision_summary.py, test_location_sheet.py, report-print.flag-on.spec.ts, ARCHITECT_PRESENTATION_CONTRACT.md.
END-OF-REPORT


---

REWORK 3 RETURN (saved unchanged by the orchestrator):

M5-T156 REWORK 3 complete. I am an AI agent (backend-engineer).

COMMIT: f9e14fb10c29d88e31d274348954e180a83986ae  PARENT: 174d6a9c58cdda1a8ba76886a9b4e9c9e2edd852. Clean tree. No report file written.

FIX: the html table builder marks any table of 8 rows or fewer "no-split"; the print CSS gives .no-split break-inside: avoid, and its heading stays with it (h3 break-after: avoid). Short tables now move whole.

PAGE COUNT: 8 (rendered file:// headless Chromium). LAST PAGE (8): the complete 6-row status-label key with its "Status-label key" heading, moved whole — no 2/4 fragment. Page 7 ends cleanly after the drawing notes.

CHECKS (lanes venv, direct exit codes): ruff check . exit 0; pytest -q tests/drawings tests/api tests/contracts tests/journey 2816 passed/6 skipped exit 0; modularity_check.py --check exit 0; check_lane_paths.py --coverage PASS exit 0.

Files (allowed): html.py, layout.py, test_report_pages.py.
END-OF-REPORT


---

CORRECTIONS RETURN, after the review wave (saved unchanged by the orchestrator):

M5-T156 CORRECTIONS complete. I am an AI agent (backend-engineer).

COMMIT: 1355a82fb06d80a5f10ec14e6d8c4371af164fb7  PARENT: 4d9aef34d4a54a14c534fefff9eeb16e866c1340. Clean tree. No report file written.

PAGE COUNT: 7 (was 8). One line per page:
1 Decision summary - answers + compact site plan + estimate + open items + coverage.
2 Where is the lot? - the neighbourhood map and the block close-up as two CO-EQUAL full-width wide maps stacked, each titled and captioned (T156-C2).
3 What constrains the design? - lot-area basis + full-size site plan + not-placed line + constraints table.
4 Option comparison - shared limitations, bar chart, 11-option table, worked/not-worked.
5 Scenario sheet - scheduled line, not-placed line, floor-stack, schedule, not-checked, estimate.
6 Assumptions and open items - 11 assumptions + open-items table.
7 Calculations and evidence - inputs, allowance, envelope, provenance + drawing notes in TWO COLUMNS, and the full status-label key all on this page (T156-C1: no orphaned near-empty page 8).

C3: builder.py now requires report_plan.is_drawing, so a missing tax_lots/building_footprints layer falls back to today's lot-only plan + its tax-map limitation line (never the drawing's reason).

MUTATION: revert the C3 fix (drop .is_drawing) -> test_c4_constraints_falls_back_to_lot_only_when_a_layer_is_unavailable FAILS (both tax_lots and building_footprints); passes with the fix.

Note: page 2's maps underscale in my chrome CLI (pt rendered as px); they render full-size in the orchestrator's Playwright print (~92% fill, fits one page).

CHECKS (lanes venv, direct exit codes): ruff check . exit 0; pytest -q tests/drawings tests/api tests/contracts tests/journey 2848 passed/6 skipped exit 0; modularity_check.py --check exit 0; check_lane_paths.py --coverage PASS exit 0.
END-OF-REPORT
