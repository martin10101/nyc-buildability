# M5-T165 reviews (every return kept unchanged)

Reviews of M5-T165 (report page 1). First reviews at 4617c720 (G1, G3, G4) and a print at 5c96f92e (visual); delta reviews at 2767f6a1 (rework 1) and fd649b66 (rework 2, the material head: the task's files are unchanged since). G1 data-contract-verifier PASS (one follow-up outside the task's files, tracked as DB-245); G3 code-reviewer PASS (its one required finding resolved; advisories tracked as DB-256); the visual review FAIL at 5c96f92e, PASS at cd6d7fc3, PASS at 68d417fe; G4 qa-engineer PASS with required corrections at 4617c720, resolved, delta PASS at 2767f6a1 and fd649b66. No required finding is open.

Every reviewer is an AI agent; none is a human or professional review.

## G1 data-contract-verifier (first review and two delta reviews)

G1 REVIEW — M5-T165 (data-contract-verifier). I am an AI agent; this is a labelled automated review, not a human or professional/legal verification (ADR-007).

VERDICT: PASS (data-contract side), with one REQUIRED follow-up that is OUTSIDE this task's allowed paths (so not a within-task blocker) and one ADVISORY.

Frozen head verified: 4617c72067c1f6783debea92d02602238dfe8415 on task/wave24-report-v3. (Worktree HEAD had moved to the disjoint peer 8f713e6a6/M5-T176; I confirmed readers.py, zoning_lot_item.py, page_decision_summary.py, page_scenario_sheet.py are byte-identical at both, and read everything from 4617c720 via git plumbing / archive.)

WHAT I CHECKED AND REPRODUCED
Share 1 — page-1 zoning-lot sentence. Worked the expected sentence from NB-01 sources before reading code: ZONE 2022020201551002 = "ZONING LOT DESCRIPTION" (E3), recorded 2022-02-08 (E2 Master), indexed against lots 1 and 70 (E9 Legals); ZR 12-10 (E6) says an index entry does not establish the instrument. Expected: "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70". zoning_lot_item.py:114-150 parses this from the document's own condition (assumption built in app/scenario/.../result_way_conditions.py:240-275, "...recorded on February 8, 2022..."), converts to ISO, dedupes+sorts lots {1,70}. Output matches contract line 52 exactly and test_report_page_one.py S2 tests assert it. It names the INDEX ENTRY, never the instrument: page 1 excludes the CRFN (test asserts "2022000059134" not in text). Generic line "Based on the lots you selected — the app does not verify the zoning lot" (engine.py:54 LOT_SELECTION_STATEMENT, read from the document) shows only in the not-checked state and once (page_decision_summary.py:62-69; S2 generic test). FAITHFUL.

Share 2 — figures/bases, nothing recalculated. Floor-area assumption "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" is assembled in page_decision_summary.py:83-93 from document-read values (recorded_lot_area_text, far.display, scope lot); 20,150 is read (area["display"]), not recomputed. 10,075 = NB-01 administrative_record ("recorded lot area" per contract line 84). Ceiling: unit_limit_text.legal_ceiling reads legal_unit_limit_standard display "29" + its own state label; fixture state way="conditional" → "Legal ceiling 29 Conditional" — never Provisional, never settled (S4). Withheld path returns the document's own reason, no number (verified in code). The 29 derivation "20,150 ÷ 680 = 29.63" lives in the value label (evidence section, S8). No default stands for a fact (absent values show "Not available"/Pending verification markers only). The distinction token equals contract line 41 verbatim (presentation-tokens.json wording.ceiling_estimate_distinction). CORRECT.

Share 3 — NB-01 revision 4. research_status unchanged = access_blocked (confirmed; diff touches only revision 3→4, code_paths +zoning_lot_item.py, code_identity readers.py 4a515b68→91f607aa and +zoning_lot_item.py, and two dependency_assessment lines). I independently recomputed LF-normalised sha256 of ALL 11 code_paths at 4617c720; every one equals NB-01 rev-4 code_identity (readers.py=91f607aa…, zoning_lot_item.py=f3595523…, incl. M5-T162's readers.py change now reflected). research_record_check.py --check → exit 0, NB-01 code_current=True, review_state=stale (correct for a producer; G1 makes it current). CORRECT.

G-6 ISOLATION DECISION: readers.py STAYS in NB-01 code_paths (I agree with the builder). Reason: detection + page-1 sentence + item builder moved to zoning_lot_item.py (rightly added), but readers.py still carries NB-01 behaviour realizing report.zoning_lot_warning — it re-exports zoning_lot_basis as a facade (readers.py:14,41) AND owns the ordering/surfacing: _ORDER leads with "zoning_lot" (:269), decision_open_items wires zoning_lot_item.zoning_lot_open_item in and surfaces it FIRST among the three page-1 uncertainties (:326-329,:363-372). Neither module alone covers the surfaced behaviour; both belong in code_paths.

Share 4 / COMMON-POINT 1 (S18). S18 as written ("no text calls a GIS value or outline 'tax map'/'tax-map outline'" across the whole report) is NOT met. The task's own surface IS clean: constraint_text.py:27-28 lot_area effect now "city map outline"; page 1 (benchmark) has no "tax map". But the GIS-outline value is still called "tax-map outline"/"approximate tax map" in the recorded document itself, emitted by the scenario engine — app/scenario/three_answers/first_option_results.py:79,83,93,96 and result_way_bridge.py:345-372 ("The recorded lot area … and the tax-map outline area … disagree") — baked into packages/contracts/fixtures/.../recorded_215_16_northern_journey.json (0 "city map outline", multiple "tax-map outline") and rendered on site-and-context / option-comparison / open-items / evidence pages. These contradict contract line 84 (gis → "city map outline"; a city map outline is never called "tax map"). ALL of this is OUTSIDE this task's allowed paths (forbidden: services/api/app/scenario/, packages/, page_site_context.py, page_option_comparison.py, page_evidence.py). REQUIRED follow-up (new backlog/task for the scenario-engine GIS wording); it cannot be fixed here. NB: genuine printed-tax-map labels (NB-04 E1/E2, basis printed_tax_map) are correctly "printed tax map" and are not in scope of this violation.

COMMON-POINT 2 (labels). Correct per contract lines 49/52/102 and the six owner labels. Ceiling 29 = Conditional (document state), never Provisional/settled. Estimate labelled Provisional is permitted (the contract bars Provisional only on the ceiling). Estimate is framed as "an unvalidated apartment-yield range … neither is a demonstrated layout", not a count of apartments to build; S4 bars buildable/achievable/can be built.

COMMON-POINT 3 (S17). Matches. page_scenario_sheet.py gives the full estimate sentence id="estimate-<building>"; page 1 shows only the range "Estimate 17-22" linking to it (_estimate_cell). test_report_pages.py::test_vc2 changed from count==2 to count==1 with the correct rationale — consistent with R013/S17 (the long sentence now prints once).

R008 CONDITION: MET. constraint_text.REAR_YARD_OPEN_CHECK names ZR 23-344(b) (short-block) and 23-344(c)(3) (adjoining side line) as "not yet checked", draws NO conclusion; REAR_YARD_LAW_SECTION links ZR 23-344; page_decision_summary.py:254-263 adds the link, no corner-only framing. Matches NB-03 (interpretation_awaiting_review; (b) and (c)(3)). "not known beyond the corner area" (S19) appears in the rendered report NOWHERE — it survives only in a constraint_text docstring, negative-assertion tests, and historical reference-case docs; the fixture does not carry it.

WHAT I COULD NOT CHECK: I did not re-fetch live ACRIS/ZR (not required; NB-01/03/04/05 captures are current 2026-10-11, sha-pinned; E2 Master and E9 Legals saved copies match). I did not render the full report HTML myself (read-only guard blocks shell file-writes incl. scratch), so S18/S19 whole-report rendering is verified by source + fixture inspection + the producer's benchmark-scoped tests, not by my own build. PDF page counts/point sizes are H2/visual-reviewer scope. Modularity/size (S10) is G3's remit; I ran tools/modularity_check.py --check → exit 0 (no new offender; readers.py within ceilings; warnings are on pre-existing scenario/tooling modules).

FINDINGS
1. ADVISORY (data): page_decision_summary.py:181 fallback caption "Site plan: the lot's approximate tax-map outline (city records)." is an in-allowed-path GIS-"tax-map" phrase; pre-existing and unchanged by this task, and NOT emitted on the benchmark (embed_summary_site_plan falls back to a short line). Reachable on documents with an embedded summary site plan. Recommend sweeping it in the same follow-up as point 2.
2. REQUIRED (follow-up, OUTSIDE allowed paths): open a backlog/task to rename the GIS-outline value from "tax-map outline"/"approximate tax map" to "city map outline" in app/scenario/three_answers/first_option_results.py and result_way_bridge.py (and refresh the benchmark fixture), so whole-report S18 and contract line 84 are met. Not a within-task blocker — the task cannot touch these paths.

AGENT REVIEW ENTRY (append unchanged to NB-01 review.agent_reviews):
{
 "reviewer": "data-contract-verifier",
 "date": "2026-10-11",
 "reviewed_revision": 4,
 "reviewed_code_identity": {
  "services/api/app/profile/hidden_issue_flags/zoning_lot_history.py": "d3f19fc93ec278ab4adf64652878b103535a8b1703e022ff4ed4aa48d852633e",
  "services/api/app/profile/existing_floor_area/scope.py": "46f5a589f1d1bd73425ebfda265cbb9afd1693cedc56afece0e4bfa2a05ca8d6",
  "services/api/app/connectors/acris_index_soda.py": "f5e2805e6d19865ef692bf8f8df518d685b2e205a76c0e1e2c6890340cde206e",
  "services/api/app/profile/zoning_lot_index.py": "2969be42e41bf969cc4e360f6007579dfbece8af00710f04755a41513098b48a",
  "services/api/app/api/v1/study_inputs.py": "ebc38eeab6b1892d24040ef6e6d39d890bb5db9fb46cd373803a1c59ba5ef733",
  "services/api/app/scenario/three_answers/result_way_conditions.py": "379192f698abff042bbe3ff5731ad9638675f875f148bce121c0214120587e40",
  "services/api/app/scenario/three_answers/result_way_bridge.py": "485dff13c10228665df4febe12a09a9412b3bd6820ae4926a46d66b06f0fb06f",
  "services/api/app/scenario/three_answers/result_ways.py": "ac0747a37bb4c462483041cd8f4b0fffce6ff450af492ff61aee5ca76e7b2af3",
  "services/api/app/scenario/three_answers/three_way_document.py": "b813ba029bb19ebed9d416991eb8c9b8c022767a910f9d94ee753fd995d1bd70",
  "services/api/app/drawings/report/readers.py": "91f607aaca9d99bab66be4b0112ff94d90a945622785df95416846f7bfb783a1",
  "services/api/app/drawings/report/zoning_lot_item.py": "f3595523d30105fcb6a261859bedfb56ff8a61923851da54faefc52ef1dbab59"
 },
 "verdict": "agrees",
 "findings": [
  "G1 at 4617c720: all 11 code_paths' LF sha256 recomputed and equal rev-4 code_identity (readers.py 91f607aa reflects M5-T162 and this task; zoning_lot_item.py f3595523 added); research_status unchanged (access_blocked); research_record_check.py --check exit 0, code_current True, review_state stale (producer).",
  "Page-1 property-specific sentence reproduced from NB-01 E2/E3/E9 and ZR 12-10 (E6): 'the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70' — names the index ENTRY not the instrument (CRFN excluded from page 1); generic line only in the not-checked state and once. Figures read, not recalculated; 10,075 recorded (administrative_record) × FAR 2.0; ceiling 29 Conditional, never Provisional/settled; rear yard the R008 open check (23-344(b)/(c)(3), no conclusion, links 23-344); 'not known beyond the corner area' absent from the rendered report.",
  "G-6 decision: readers.py STAYS in code_paths — it keeps the zoning_lot_basis facade and the open-items ordering/wiring (_ORDER leads 'zoning_lot'; decision_open_items surfaces it first) that realize report.zoning_lot_warning; detection and the page-1 sentence correctly moved to zoning_lot_item.py (added).",
  "S18 residual (outside allowed paths): the GIS outline is still called 'tax-map outline' by the scenario engine (first_option_results.py, result_way_bridge.py) and the recorded fixture, contradicting contract line 84; the task's own lot_area effect text and page 1 are clean. A backlog follow-up is owed; this task cannot touch app/scenario/ or packages/."
 ],
 "report": "project-control/reports/M5-T165-G1.md"
}

Files (absolute): /root/project/w-wave20 @ 4617c720 — services/api/app/drawings/report/{zoning_lot_item.py,constraint_text.py,unit_limit_text.py,page_decision_summary.py,readers.py,page_scenario_sheet.py}; services/api/app/scenario/three_answers/{result_way_conditions.py,first_option_results.py,result_way_bridge.py}; packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json; docs/research/evidence-records/{NB-01,NB-03,NB-04}-*.json; docs/design/{ARCHITECT_PRESENTATION_CONTRACT.md,presentation-tokens.json}; services/api/tests/drawings/report/{test_report_page_one.py,test_report_pages.py}.

END-OF-REPORT

G1 DELTA REVIEW — M5-T165 at 2767f6a1 (data-contract-verifier). I am an AI agent; this is a labelled automated review, not a human/professional/legal verification (ADR-007).

DELTA VERDICT: PASS. My earlier verdict carries to 2767f6a1 and every REQUIRED correction of mine is resolved.

1. SCOPE CONFIRMED. Over 4617c720..2767f6a1, `git log -- <the 24 allowed paths>` shows only two commits changed allowed-path files: 20801603 (zoning_lot_item.py docstring + NB-01) and 2767f6a1 (layout.py, page_decision_summary.py, test_report_page_one.py, producer report). 485b8ecb (scope correction) touched no allowed-path file — only the packet and G0. No other task's commit (M5-T176/T164/T166, backlog sweeps) touched an allowed-path file.

2. JUDGEMENT under G1 rules + visual findings 1-3 + narrowed S18:
- 20801603: zoning_lot_item.py docstring reworded only (drops the literal text 'result_way' per the test_result_ways text scan); the marker value `_ZONING_LOT_CONDITION_MARKER = "register of recorded documents"` and all logic are unchanged — behaviour-identical. NB-01 code_identity for zoning_lot_item.py updated f3595523→88e1916a (matches my LF-recompute).
- 2767f6a1 key-figure split (page_decision_summary.py): each headline KEY FIGURE is a single value read from the document's own value fields — allowance_key=area["display"], envelope_key="Up to "+max_building["display"], scheduled_key=scheduled_display. No figure recomputed; no sentence cut by a pattern (the envelope uses distinct min_base/max_base/max_building fields; the scheduled detail keeps the whole fixed "…site fit unverified" wording). The assumption line "10,075 sq ft recorded lot area × FAR 2.0, tax lot 70 alone" is unchanged and still document-read (NB-01 administrative_record 10,075; contract line 84). No font below its token: new `.answer-detail` = _BODY_PT; layout.py's remaining literal pt values are borders/weights/spacing, not type sizes — S3 (every font-size a TYPE token) passes. Page 1 still holds all items and the S7 caps hold (full tests/drawings/report suite green, incl. the two new rework tests and S1-S19).
- Visual findings 1-3 are design/PDF-fit calls (visual G3's return), not mine; from the data side the values and bases are intact.

RESOLUTION OF MY EARLIER FINDINGS:
- ADVISORY #1 (the page-1 fallback caption "…approximate tax-map outline (city records)" at page_decision_summary.py:181) is FIXED → "Site plan: the lot's city map outline (not surveyed)." No GIS value is called "tax map" anywhere on page 1 (the only "tax" strings left are legitimate "tax-lot"/"tax lot" scope words).
- REQUIRED #2 (the scenario-engine GIS wording) is RESOLVED as tracked owed work: the orchestrator narrowed S18 by a dated scope_corrections entry to this task's own texts + the whole of page 1, and queued the remaining "tax-map outline"/"Approximate tax map" texts — in forbidden paths (first_option_results.py, result_way_bridge.py, the fixture, page_site_context.py, options.py) AND the shared basis-rank display name readers.py _BASIS_NAMES['approximate_tax_map'] (shared with the web, so a PDF-only rename would split PDF/website, R041/R057) — to ONE GIS-wording sweep, DB-245 queued to M5-T167. That display name does not appear on page 1, so the narrowed S18 (page 1 clean) holds.

G-6 DECISION UNCHANGED: readers.py STAYS in NB-01 code_paths (facade re-export of zoning_lot_basis + the _ORDER/decision_open_items wiring that surfaces report.zoning_lot_warning first); detection + page-1 sentence remain in zoning_lot_item.py. No new reason to change it.

3. COMMANDS (git archive 2767f6a1 copy, lanes venv):
- `cd services/api && python -m ruff check .` → "All checks passed!" RUFF_EXIT=0
- `python -m pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` → "161 passed, 1 warning" PYTEST_EXIT=0
Also: all 11 NB-01 code_paths' LF sha256 at 2767f6a1 equal NB-01 rev-4 code_identity; research_status unchanged (access_blocked); revision 4.

NEW: nothing adverse. The docstring/caption/scope narrowing are honest and improve provenance.

4. RE-ISSUED NB-01 AGENT REVIEW ENTRY (revision 4, at 2767f6a1; append unchanged):
{
 "reviewer": "data-contract-verifier",
 "date": "2026-10-11",
 "reviewed_revision": 4,
 "reviewed_code_identity": {
  "services/api/app/profile/hidden_issue_flags/zoning_lot_history.py": "d3f19fc93ec278ab4adf64652878b103535a8b1703e022ff4ed4aa48d852633e",
  "services/api/app/profile/existing_floor_area/scope.py": "46f5a589f1d1bd73425ebfda265cbb9afd1693cedc56afece0e4bfa2a05ca8d6",
  "services/api/app/connectors/acris_index_soda.py": "f5e2805e6d19865ef692bf8f8df518d685b2e205a76c0e1e2c6890340cde206e",
  "services/api/app/profile/zoning_lot_index.py": "2969be42e41bf969cc4e360f6007579dfbece8af00710f04755a41513098b48a",
  "services/api/app/api/v1/study_inputs.py": "ebc38eeab6b1892d24040ef6e6d39d890bb5db9fb46cd373803a1c59ba5ef733",
  "services/api/app/scenario/three_answers/result_way_conditions.py": "379192f698abff042bbe3ff5731ad9638675f875f148bce121c0214120587e40",
  "services/api/app/scenario/three_answers/result_way_bridge.py": "485dff13c10228665df4febe12a09a9412b3bd6820ae4926a46d66b06f0fb06f",
  "services/api/app/scenario/three_answers/result_ways.py": "ac0747a37bb4c462483041cd8f4b0fffce6ff450af492ff61aee5ca76e7b2af3",
  "services/api/app/scenario/three_answers/three_way_document.py": "b813ba029bb19ebed9d416991eb8c9b8c022767a910f9d94ee753fd995d1bd70",
  "services/api/app/drawings/report/readers.py": "91f607aaca9d99bab66be4b0112ff94d90a945622785df95416846f7bfb783a1",
  "services/api/app/drawings/report/zoning_lot_item.py": "88e1916a672564b52917aec595950cf44e1cf4d126b19b26b4f23b729ce45b52"
 },
 "verdict": "agrees",
 "findings": [
  "G1 delta at 2767f6a1: all 11 code_paths' LF sha256 recomputed and equal rev-4 code_identity (zoning_lot_item.py 88e1916a after the docstring-only ORCH correction 20801603; readers.py 91f607aa unchanged); research_status unchanged access_blocked.",
  "Page-1 zoning-lot sentence, figures, bases, ceiling 29 Conditional and the rear-yard open check (23-344(b)/(c)(3), no conclusion) are unchanged from 4617c720 and remain faithful to NB-01/NB-03/NB-04 and the contract. The rework split only moved the non-key result text to the body token; every key figure is still read from the document's own value field, none recomputed.",
  "G-6 decision unchanged: readers.py stays in code_paths (facade + open-items ordering realizing report.zoning_lot_warning); zoning_lot_item.py carries detection and the page-1 sentence.",
  "S18 (narrowed by orchestrator scope correction 485b8ecb to this task's texts + the whole of page 1): met — the page-1 fallback caption now says 'city map outline (not surveyed)'; the remaining 'tax-map outline'/'Approximate tax map' texts live outside this task's paths or in the shared basis-rank display name and are owed by the GIS-wording sweep DB-245 (M5-T167)."
 ],
 "report": "project-control/reports/M5-T165-reviews.md"
}

END-OF-REPORT

G1 DELTA REVIEW 2 — M5-T165 at fd649b66 (data-contract-verifier). I am an AI agent; this is a labelled automated review, not a human/professional/legal verification (ADR-007).

DELTA VERDICT: PASS. My PASS carries to fd649b66.

1. SCOPE CONFIRMED. Over 2767f6a1..fd649b66, `git log -- <the 24 allowed paths>` returns exactly two commits: fd649b66 (rework 2: layout.py, page_decision_summary.py, test_report_page_one.py, producer report) and c2413c5d (NB-01 review-block append only — 26 insertions adding my prior G1 entry verbatim; it does NOT touch NB-01's implementation.code_identity). I recomputed all 11 NB-01 code_paths' LF sha256 at fd649b66: every one equals the recorded code_identity (readers.py 91f607aa, zoning_lot_item.py 88e1916a, the other nine unchanged); revision 4; research_status access_blocked. No code identity changed, so no new NB-01 entry is needed.

2. JUDGEMENT (S1-S19, S18 as narrowed):
- Every key figure is read from the document's own value fields, nothing recomputed: allowance = area["display"] ("20,150 sq ft", unit kept), envelope = "Up to "+max_building["display"] ("Up to 55 ft"), scheduled = worked[0]["storey_count"] ("3 storeys", with height then area_disp as ordered fallbacks). The scheduled floor-area number is preserved VERBATIM inside the fixed X5 detail "Scheduled floor area: 20,150 sq ft; site fit unverified" (labels.scheduled_floor_area_line) — no recompute, no data dropped; the change only stops the same 30 pt number printing as two headlines.
- No font below its token: layout.py adds only table-layout:fixed, a 24 mm first-column width, gap 6→4 mm and margins — no new font sizes; all font-size values stay TYPE tokens (S3 green).
- S14: the page-1 figure wrapper is untouched — `.summary-figure flex 0 0 88mm` unchanged, the caption branch unchanged; the two-column change is in the answers table only.
- Status label still shown per answer: label_chip(label) now sits in the Answer-name `<th>` (answer-name div + chip); the header drops the "Status" column but every row still renders its label.
- Every page-1 item present and the S7 caps hold: full tests/drawings/report suite green, including S1/S4/S5/S7/S12/S18-narrowed and the new test_rework2_* (number-keeps-its-unit; no duplicate headline figure).

3. COMMANDS (git archive fd649b66 copy, lanes venv, services/api cwd):
- `python -m ruff check .` → "All checks passed!" RUFF_EXIT=0
- `python -m pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` → "163 passed, 1 warning" PYTEST_EXIT=0 (two more than delta-1's 161 = the two rework2 tests).

NEW: nothing adverse. The rework-2 scheduled key-figure change is a presentation choice that removes a duplicate headline; the data (floor area, storeys, height) is document-read and the floor-area figure is retained verbatim in the detail. All earlier findings stay resolved (ADVISORY-1 caption fixed; REQUIRED-2 engine wording tracked as DB-245/M5-T167 under the narrowed S18).

END-OF-REPORT

## G3 code-reviewer (first review and two delta reviews)

GATE REPORT — M5-T165 G3 (code-reviewer share: correctness & maintainability of the report changes)

AI-agent notice: I am an AI agent. This is an automated, read-only code review at the frozen head, NOT a human or professional review. Verified at PINNED HEAD 4617c72067c1f6783debea92d02602238dfe8415 on task/wave24-report-v3 (parent/base 6639a7b1). Reviewed files are byte-identical pinned→worktree HEAD except one docstring line-wrap in zoning_lot_item.py (immaterial).

VERDICT: PASS (code & maintainability). No blocking code defect. One out-of-scope residual the orchestrator must track (F1); advisories below.

=== WHAT I INDEPENDENTLY VERIFIED (reproduced, not trusted) ===
- S13 (moved texts keep 1.4.0 output except rear yard): I built build_report_html for ALL 12 valid results fixtures at 6639a7b1 vs 4617c720 and diffed per section. The ONLY non-page-1 text changes are: (a) rear_yard effect "...not known beyond the corner area." → the open check "Whether a rear yard is required is not yet checked: the short-block rule ZR 23-344(b) and the adjoining-side-line rule ZR 23-344(c)(3) have not been applied to this lot." (b) lot_area effect "tax-map outline" → "city map outline". (c) the material-exclusions scope-note moved into the appendix head. (d) id attributes added (#issue-<n>, #estimate-<building>) — no text change. ALL other effect texts (coverage/placement/setback/street_wall/parking, zoning-lot effect, legal_unit_limit) byte-unchanged. Site-and-context section unchanged for every fixture. S13 holds.
- S10: readers.py = 573 lines / 490 SLOC (≤600) and exactly 40 top-level symbols (≤40). Every base __all__ name preserved; adds apartment_estimate_range; zoning_lot_basis re-exported as facade. Marker "register of recorded documents" matches scenario result_way_conditions.ZONING_LOT_INDEX_MARKER. modularity_check --check: 796 files, 0 failures (readers/layout/new modules not flagged).
- S3: every font-size in layout.py is interpolated from a TYPE token (headline-value print_pt=30 ∈ 28–32; property-title 22; section-title 14; body 10.5; compact 9.5; source-note 8.5). Docstring states fonts never shrunk to fit. Remaining literal pt are border/line-weights and letter-spacing (contract §6), not type sizes.
- S16: the 4 wording-group values (ceiling_estimate_distinction, area_zone_apartment, area_zone_other, area_illustration_caption) are byte-equal to the contract quotes and appear verbatim in the contract; caption dash is U+2014; Python module == JSON; no " or \ in any value. `node scripts/presentation-tokens.mjs --check` OK; node test 10/10 pass.
- S6: 0 unresolved in-page href anchors across all 12 fixtures; benchmark page 1 links #estimate-B + three #issue-<n>, all resolve to appendix ids.
- S14: page-1 summary-figure wrapper preserved (class summary-figure, flex 0 0 88mm, caption "The lot among its neighbours (city map; not surveyed)."). e2e runs in CI.
- Plain user text: benchmark page-1 visible text carries no keys/task-ids/internal names; matches the contract page-1 spec (identity, R030 index-entry sentence "…recorded 2022-02-08 against lots 1 and 70", standing label, answers+assumption lines, R029 allowance phrase, ceiling 29 Conditional beside Estimate 17-22 Provisional + distinction line, three uncertainties zoning-lot/lot-area/rear-yard, scope line).
- S19 + forbidden words: "corner area"/"not known beyond"/"buildable"/"achievable"/"can be built"/optimal/compliant/feasible/preferred/recommended/achieved appear in NO fixture report.
- "No default stands for a fact": material facts gated by `is not None` (allowance area, envelope max_building, ceiling value, estimate range, legal_ceiling all-None when absent → "not available"); unit_limit_text avoids truthiness on optional blocks.
- 141 report+token pytest pass against the pinned tree; ruff clean on touched api files; research_record_check PASS (NB-01 code_current=True).
- D-093: opened NB-01 rev4 (access_blocked, zoning lot UNCONFIRMED, isolation + code-paths recorded), NB-03 (interpretation_awaiting_review, names 23-344(b)+(c)(3)), NB-04 (10,387.99 outline basis=gis → "city map outline"; 10,075 recorded area basis=administrative_record). The task's texts are faithful to these records; every unresolved input stays unresolved.

=== THE THREE POINTS ===
1) S18 NOT met as written (whole report). "tax-map outline" and "Approximate tax map" still describe the GIS outline (10,387.99 sq ft, basis gis per NB-04) on site-and-context, option-comparison and the appendix for every fixture carrying the 1.4.0 lot-area condition. These strings originate in app/scenario/** and the packages/ fixtures and render via page_site_context.py / page_option_comparison.py / page_assumptions.py pass-through — ALL forbidden/outside this task's editable scope. WITHIN scope the lot_area effect text and page 1 ARE fixed to "city map outline" (page 1: zero tax-map hits across all 12 fixtures). Conclusion: the shortfall is OUTSIDE this task's allowed paths. REQUIRED (orchestrator): track a follow-up for the scenario-engine wording and/or re-scope S18; do not fail M5-T165 for it. (The evidence-page basis label "Approximate tax map" comes from readers._BASIS_NAMES["approximate_tax_map"] in-scope, but it labels a declared tax-map basis key, not a GIS value, so it is not an S18 violation.)
2) Estimate "Provisional" / ceiling "Conditional" is contract-correct: the ceiling is never Provisional (it is Conditional, read from the value state), and the estimate "17-22" is a range with the distinction line ("unvalidated apartment-yield range; neither is a demonstrated layout"), not a count of apartments to build. Provisional is one of the owner's six labels and matches the scenario sheet. PASS.
3) S17: the long apartment-estimate sentence prints exactly once in the benchmark report (count=1); page 1 shows the range and links to #estimate-B; the test change 2→1 matches S17. PASS.

=== FINDINGS ===
F1 REQUIRED (orchestrator tracking; out-of-scope fix) — S18 whole-report residual, as in point 1. file:page_site_context.py / page_option_comparison.py / app/scenario/** / packages fixtures. Evidence: cross-commit tax-map search (0 hits in decision-summary; hits only on forbidden/pass-through pages).
F2 ADVISORY — page_decision_summary.py:181 fallback caption still reads "Site plan: the lot's approximate tax-map outline (city records)." It is in-scope and authored by this task but UNREACHABLE by all 12 valid fixtures (0 decision-summary tax-map hits), so emitted page 1 is clean. Recommend changing to "city map outline" to prevent a latent S18 violation if a drawable summary plan without surroundings ever occurs.
F3 ADVISORY — page_assumptions._material_exclusions builds the "Not yet" list without map_context (docstring-acknowledged), so "Context maps" would be listed as excluded even when page 2 shows maps. No fixture exercises maps-present; latent only.
F4 ADVISORY — estimate label is the constant labels.PROVISIONAL (page_decision_summary.py:228), not read from document state; contract-compliant and consistent with the scenario sheet, noted for completeness.
F5 ADVISORY — minor truthiness on optional display adornments: `if min_base and max_base` (:120) and `if worked[0].get("storey_count") and …` (:136) gate only basis adornment lines, not the shown facts; a 0-storey count would drop its basis line. Non-material.
F6 ADVISORY — readers.py is at exactly the 40-symbol S10 ceiling; any further addition must extract to another module.
F7 ADVISORY — layout.py docstring overstates "every pt is interpolated"; literal pt remain for borders/line-weights/letter-spacing. Every font-size does use a TYPE token, so S3 is met.

=== WHAT I COULD NOT CHECK (and why) ===
- PDF rendering, printed point sizes, page counts (contract H2, by eye) — the visual-quality-reviewer share on the printed PDF; outside the code review; I started no server and touched no ports 3000/3001/8000.
- report-print e2e / browser — runs in CI; not run here.
- Full services/api pytest + dependency-security at the exact head — CI's job (R639); I ran the drawings/report + token subset (141 passed) and the node token tests.
- NB-01 review_state=stale → current re-stamp — G1's job (producer ≠ reviewer).
- Live ACRIS/ZR network sources — I relied on the evidence records' saved copies/excerpts and did not re-fetch.

END-OF-REPORT

DELTA REVIEW — M5-T165 G3 (code-reviewer share), 4617c720 → 2767f6a1f

AI-agent notice: I am an AI agent; this is an automated, read-only code review, not a human or professional review. I am the G3 CODE reviewer, so I skip delta step 4 (G1-only NB-01 entry) — that belongs to the data-contract/G1 reviewer.

DELTA VERDICT: PASS. My earlier PASS carries to 2767f6a1, and my one REQUIRED finding is resolved.

1) Commit range (git): over M5-T165's allowed-path files, `git log 4617c720..2767f6a1` shows exactly two commits — 2767f6a1f (rework 1) and 20801603f (ORCH-CORRECTED zoning_lot_item.py docstring). 485b8ecb touched only the packet + G0 (not allowed-path source), matching the delta. No disjoint task touched an allowed-path file. Confirmed.

2) Judgement (code/maintainability, S1–S19 with S18 narrowed):
- layout.py: docstring corrected ("every FONT SIZE from a TYPE token; remaining literal pt are borders/line-weights/letter-spacing, not type sizes") — resolves my earlier advisory F7. New `.answer-detail` uses `_BODY_PT` (a token); `.answer-figure` stays `_HEADLINE_PT` with line-height 1.1. Margins/paddings tightened (mm/pt structural). NO font below its token; no font-size hard-coded; nothing shrunk to fit — the key figure stays at headline, the rest at body, exactly as the delta directs.
- page_decision_summary.py: `_answer_cell` now splits key figure vs detail. Each KEY FIGURE is read from a document value field — allowance=`area["display"]`, envelope=`max_building["display"]` ("Up to 55 ft"), scheduled=`scheduled_display`; the FAR, base range and the whole X5 "Scheduled floor area… site fit unverified" sentence move to the body detail. No figure recomputed, no sentence cut by a pattern. Fallback caption changed to "Site plan: the lot's city map outline (not surveyed)." — resolves my advisory F2 (no more in-scope "tax-map outline").
- zoning_lot_item.py: docstring-only reword so no app file outside the permitted list carries the text "result_way"; behaviour identical.
- Page 1 still holds every item (benchmark rebuilt at 2767f6a1): identity + R030 index-entry sentence, standing label, question, three answers (key/detail/basis/label), site line, ceiling 29 Conditional beside Estimate 17-22 Provisional + distinction line, three uncertainties (zoning-lot/recorded-lot-area/rear-yard ZR 23-344 Unresolved), scope line. All in-page anchors resolve (0 unresolved). Minor, non-blocking: the scheduled figure prints twice within its own cell (key + inside the kept-whole X5 sentence); within caps.
- S7 caps hold at 2767f6a1 across all 12 fixtures: page-1 worst = 192 words (≤200), total worst = 2318 (≤2448). No "tax map"/"tax-map" anywhere on page 1 (all fixtures) → S18-as-narrowed met (page 1 + the texts this task writes are clean; the GIS-wording sweep is correctly deferred to DB-245/M5-T167).
- D-093: changes are presentation only; no feasibility fact, rule, figure, or label changed; zoning lot stays Conditional/unconfirmed, recorded lot area Conditional, rear yard an Unresolved open check — every unresolved input stays unresolved. The caption wording "city map outline" aligns with NB-04 (the 10,387.99 outline is basis gis). NB-03 still backs the rear-yard open check (23-344(b)/(c)(3), no conclusion).

3) Commands (archive of 2767f6a1, lanes venv), exit codes:
- `git log 4617c720..2767f6a1 -- <allowed paths>` → the two commits above (exit 0).
- `python -m ruff check .` (services/api) → exit 0, "All checks passed!".
- `python -m pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` → exit 0, 161 passed, 1 warning.

4) (G1 only — not performed; I am the code reviewer.)

5) Earlier verdict carries to 2767f6a1. REQUIRED finding F1 (S18 whole-report residual) is RESOLVED: the scope correction (485b8ecb) narrows S18 to the texts this task writes and the whole of page 1 — both verified clean — and routes the scenario-engine GIS wording to backlog DB-245 (M5-T167). Advisories F2 and F7 resolved; F3 (map_context-less exclusions list), F4 (estimate label constant), F5 (minor truthiness adornments), F6 (readers at the 40-symbol ceiling) remain as non-blocking advisories.

What I could not check (unchanged from my earlier report): PDF rendering / printed point sizes / page-fit (visual-quality-reviewer on the printed PDF — the visual G3 FAIL these commits answer is that reviewer's re-check, not mine); report-print e2e/servers (CI; no ports touched); full api suite + dependency-security at head (CI); the NB-01 G1 re-stamp; live ACRIS/ZR network (I used the saved evidence records).

END-OF-REPORT

DELTA REVIEW 2 — M5-T165 G3 (code-reviewer share), 2767f6a1 → fd649b66f

AI-agent notice: I am an AI agent; this is an automated, read-only code review, not a human or professional review.

DELTA 2 VERDICT: PASS. My PASS carries to fd649b66.

1) Commit range (git): over M5-T165's allowed-path files, `git log 2767f6a1..fd649b66` shows exactly two commits — fd649b66f (rework 2: code + test_rework2_*) and c2413c5d6 (NB-01 review-block append). The NB-01 diff is +26/-0: a pure append of the G1 data-contract-verifier AGENT REVIEW ENTRY for revision 4; the record's `code_identity` block is untouched (no code identity changed). Confirmed.

2) Judgement (S1–S19, S18 narrowed):
- Answers table is now two columns: the status chip sits in the first column beside the answer NAME, Result column widened (table-layout:fixed, 24mm first col, .summary gap 6→4mm). Structural mm only; no font-size changed, so no font drops below its token. The Status label is still shown for every answer (benchmark page 1 carries 8 label-chips: 3 answers + ceiling + estimate + 3 uncertainties).
- Scheduled-building key figure is now the storey count "3 storeys" (document `storey_count`; height as fallback, area as last resort); the fixed X5 sentence "Scheduled floor area: 20,150 sq ft; site fit unverified" is kept verbatim as the detail. Every key figure is read from a document value field (allowance 20,150 sq ft, envelope "Up to 55 ft", scheduled "3 storeys"); nothing recomputed, no sentence cut by a pattern. The floor-area number now appears as a headline key only once (allowance row) — resolves the visual advisory.
- S14: `_summary_block` wrapper, `.summary-figure` 88 mm column and the caption are untouched by rework 2.
- Every page-1 item present (verified on the benchmark); anchors all resolve (0 unresolved); no "tax map"/"tax-map" on page 1 for any fixture (S18-as-narrowed holds).
- S7 caps hold at fd649b66 across all 12 fixtures: page-1 worst 188 (≤200), total worst 2314 (≤2448).
- D-093: presentation-only; no fact, rule, figure or label changed; unresolved inputs stay unresolved.

3) Commands (archive fd649b66, lanes venv), exit codes:
- `python -m ruff check .` (services/api) → exit 0, "All checks passed!".
- `python -m pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` → exit 0, 163 passed.

4) PASS carries to fd649b66. Nothing new/defective; the within-cell figure duplication I noted in delta 1 is resolved.

Could not check (unchanged): PDF/printed-size visual (visual-quality-reviewer), report-print e2e/servers (CI), full api suite + security at head (CI), live ACRIS/ZR (used saved records).

END-OF-REPORT

## G3 visual-quality-reviewer (three rounds; the returns cover M5-T165 and M5-T166)

VISUAL GATE REVIEW — M5-T165 & M5-T166 (wave 24, G3 visual share), frozen head 5c96f92e on task/wave24-report-v3.

I am an AI agent (visual-quality-reviewer). This is not a human or professional review. Read-only; I reviewed the orchestrator's AFTER trial PDF/HTML (re-rendered at 150–400 dpi in scratch), the BEFORE set, the contract at 5c96f92e, both packets, and evidence records NB-01/03/04/06. I did not run the server (no ports). I did not re-derive rule values (FAR 2.0, ceiling 29, estimate 17-22, heights 55/65) — those come from the frozen document + published rules and are out of visual scope.

=== M5-T165 (page 1 / decision summary) — VERDICT: FAIL ===

1. REQUIRED — Headline 28–32 pt scale is applied to WHOLE SENTENCES, not the key figure (p1–p2). `.answer-figure`=30 pt renders "Base 30 ft to 45 ft; building up to 55 ft" and "Scheduled floor area: 20,150 sq ft; site fit unverified" each as a 5-line word-by-word tower in the ~450 px Result column. Breaks the print scale ("headline value 28–32 pt", R047/R048) and the page-type-1 "results in large type, each with its assumption line". Smallest fix: put only the key figure at 30 pt (e.g. "20,150 sq ft", "30–55 ft") and the rest of the sentence at body 10.5 / assumption 9.5 pt — no font below its token.

2. REQUIRED — Status column clipped/occluded by the site graphic (p1). The first "Conditional" badge renders "Conditi" and is cut off where the map overlaps the Answer/Result/Status table. The BEFORE layout had the figure fully clear of the table. Smallest fix: constrain the answers-table width (or the figure's left offset) so Status clears the figure.

3. REQUIRED — Decision summary spills onto a 2nd page as a LAYOUT DEFECT, not the allowed scale-add (p1–p2). BEFORE fit all four kinds of content + figure on one page; the spill here is caused by #1's towers. Fixing #1 collapses them; any small residual spill would then be the legitimate scale-add. Same fix as #1.

4. REQUIRED (report-level; root cause OUTSIDE both tasks' editable scope) — A gis outline value is printed as "tax-map outline". The lot-area basis (p4) and Limitation 1 (appendix) say "the tax-map outline area of 10,387.99 sq ft". NB-04 records 10,387.99 as basis `gis`. Contract wording rule: "a city map outline is never called 'tax map' or 'tax-map outline'" (and M5-T165 S18). The close-frame drawing and constraint_text.py correctly call the SAME outline "map outline"/"city map outline", so the report is internally inconsistent and conflates two bases NB-04 says to keep distinct. Editable source strings are in services/api/app/scenario/three_answers/result_way_conditions.py:187 and report/options.py:45 (both FORBIDDEN to both tasks); page_decision_summary.py:180 holds a non-rendered fallback with the same wording (in-scope). M5-T165's own test_report_pages.py test_s7 asserts "tax-map outline" IS present — it encodes the wrong expectation, so the green suite hides the S18 violation. Smallest fix: a follow-up task on the scenario layer to rename the gis area to "city map outline area" and align test_s7.

PASS on substance (M5-T165): distinction line matches R078 verbatim; ceiling 29 (Conditional) beside estimate 17-22 (Provisional), flex side-by-side; estimate links to #estimate-B (defined); three uncertainties (zoning lot, recorded lot area, rear yard) one line each, all #issue anchors resolve; rear-yard open check names ZR 23-344(b) and (c)(3), draws no conclusion; "not known beyond the corner area" gone; allowance phrase, scope line present; coverage inventory removed; zoning-lot sentence names the register index entry (2022-02-08, lots 1 & 70); text SHRANK 2769→2559 words; repeats fell 3→1; all 13 law links to zoningresolution.planning.nyc.gov; type tokens 22/30/14/10.5/9.5/8.5 pt within scale.

OBSERVATION (not a task defect): the street address "215-16 Northern Boulevard" is absent from the AFTER (title + header show BBL only). Cause is the TRIAL INPUT — fixture recorded_215_16_northern_journey.json has no `address` field; the title code (`address or display`, unchanged) shows the address when present, as the owner's-preview BEFORE set did. Orchestrator should confirm the real preview still shows the address on page 1.

=== M5-T166 (pages 2–3 / physical p3 locator, p4 constraints) — VERDICT: PASS with required corrections ===

5. REQUIRED (minor) — Right-edge dimension label collides with a boundary line (p4). The vertical "99.98 ft, map outline, not surveyed" (215-Place edge) is crossed near its top (word "surveyed") by a neighbouring-lot boundary line. Breaks section 6 label placement and S2 ("no collisions; fail rather than shrink"). The left-edge twin is clean. Smallest fix: widen the right dimension lane / nudge the label clear of the neighbour line, or move "not surveyed" to the legend (keep "99.98 ft, map outline").

6. ADVISORY — Legend and scale-bar text below the 8.5 pt drawing-label floor. Legend entries (incl. "No building placed") at 8.0 pt; scale-bar numerals at 7.5 pt. The 2026-10-11 scale sets drawing labels ≥8.5 pt. "No building placed" READS ACCEPTABLY at 8.0 pt, but for strict conformance raise legend + scale-bar text to 8.5 pt. Load-bearing dimension/street labels are already at 8.5 pt.

PASS on substance (M5-T166): neighbourhood locator is clean (streets, north arrow, scale bar, legend Subject lot/Street, sources caption). Close frame: subject lot + edge-sharing lots (1, 11, 61) dominate; four dimension lines anchored to edges, each naming gis basis ("103.88 / 99.98 / 99.98 / 101.71 ft, map outline, not surveyed"), all roundings match NB-04, no tax-map value drawn; street names + mapped widths (Northern Blvd 100 ft, 215 St 60 ft, 215 Place 60 ft) distinct from the lot edges; north arrow + scale bar; "No building placed" legend entry present while the not-placed sentence stays once on the scenario sheet; "Map geometry only…" once; compact 3×2 standard/qualifying-housing heights table; at most 3 map figures, each a distinct job; outline not stretched. Yards/setbacks correctly NOT drawn (1.4.0 unresolved state, R017).

What the page-1 graphic rework must satisfy: dimension labels ≥8.5 pt; no label/line collisions; each dimension names its gis basis ("map outline, not surveyed"); no tax-map value; the Status column must clear the new graphic (ties to #2); must not reintroduce "tax-map outline" for the gis outline.

=== WHOLE REPORT ===
Page count 9 → 11. +1 page is the decision-summary layout spill (#1/#3, a defect); the remainder is within the contract's allowed scale-add. Text did not grow (shrank 7.6%). Repeats fell 3→1 (residual: "A check not yet made against an independently worked example." ×3 — ADVISORY, improving toward zero).
Changed pages, before→after (one line each):
- p1 decision summary: readable result values on one page → two-page spill with 30 pt sentence towers + clipped Status badge.
- p2 (new continuation): ceiling/estimate pair + three linked uncertainties + scope line — new content model, correct.
- p3 locator: ~same neighbourhood locator (was before-p2).
- p4 constraints: lot-only/among-neighbours plan → large dimensioned close frame (edge dimensions + 3×2 heights + "No building placed" legend).

Could not check: live server/website/interactive, keyboard/reduced-motion/tablet (PDF trial; M5-T166 made no CSS change, website unchanged); rule-derived numeric values; deep NB-05 re-derivation (read for bases only).

END-OF-REPORT

VISUAL DELTA — M5-T165 page 1, re-judged at cd6d7fc3 (rework 1 integrated 2767f6a1). I am an AI agent; not a human/professional review. Read-only; I re-rendered page 1 at 200 dpi and page 4 at 150 dpi in /tmp/claude-0/visual-t165-delta/ and read the new HTML/CSS. Per instruction I did NOT judge the close frame (PDF page 3).

VERDICT M5-T165: PASS (prior FAIL findings 1-3 all resolved; two ADVISORY polish items remain; the extra page is M5-T166's, not page 1's).

Resolved:
- Finding 1 (30 pt on whole sentences) RESOLVED. `.answer-figure` (30 pt) now holds key figures only: "20,150 sq ft", "Up to 55 ft", "20,150 sq ft". The descriptive text ("FAR 2.0", the assumption lines, "Scheduled floor area: 20,150 sq ft; site fit unverified", "3 storeys; 30 ft") is body/compact size. No sentence towers.
- Finding 2 (Status column clipped) RESOLVED. All three "Conditional" badges render fully; the site graphic no longer overlaps the Answer/Result/Status table.
- Finding 3 (decision summary spilled to a 2nd page) RESOLVED. The full decision summary — three results, site graphic, ceiling 29 / estimate 17-22 with the distinction line, the three uncertainties, scope line — now fits on page 1 (218 words). Ceiling/estimate and uncertainty links intact. Type tokens 22/30/14/10.5/9.5/8.5 pt, none below 8.5 pt.

New page-1 items:
1. ADVISORY — p1, Result column. The 30 pt key figures wrap to two lines in the narrow column: "20,150" / "sq ft" and "Up to" / "55 ft". It is a key figure (not a sentence), so it conforms to the headline-value rule and stays legible, but the unit breaking away from the number is slightly awkward. Smallest fix (page_decision_summary.py / report CSS in layout.py): widen the Result column (trim the Answer/Status widths) or keep number+unit together (nowrap) so the figure sits on one line — no font shrink.
2. ADVISORY — p1, "Scheduled building" cell. "20,150 sq ft" prints twice in the same cell: once as the 30 pt key figure and again inside the kept fixed sentence "Scheduled floor area: 20,150 sq ft; site fit unverified". Combined with the identical "20,150 sq ft" floor-area-allowance figure above, page 1 shows the same number as a giant 30 pt value twice, which dents the five-second hierarchy. Smallest fix (page_decision_summary.py): for the scheduled-building row use a non-duplicative key figure (e.g. "3 storeys" / "30 ft") or render the fixed sentence as the value without a separate 30 pt number; keep the fixed sentence verbatim.

Constraints-page ruling (PDF page 4, 70 words):
LAYOUT DEFECT, not the contract's allowed scale-add. Page 4 carries only the 4-row "Zoning constraints for this lot" table (Rear yard / Setback above the base / Maximum lot coverage / Street wall) on an otherwise blank page; it was orphaned off page 3 (close frame + lot-area basis + heights table). A 4-row table alone on a blank page is avoidable pagination waste, not genuine content needing a page. This is the source of the page-count growth: page type 2 (site and context) now spans PDF p2 (locator) + p3 (close frame) + p4 (orphan table) = 3 pages vs the before set's 2. It is in M5-T166's files (page_site_context.py table placement; the close-frame drawing height in site_context_plan.py / close_frame_dimensions.py) — fix it by shrinking the p3 drawing enough that the constraints table flows onto p3, or restructuring the section so the table is not orphaned. It naturally belongs with M5-T166's in-flight rework 3. Page 1 (M5-T165) does not cause it and no longer spills.

Whole report: 10 pages (before 9). The +1 is the orphaned constraints page above (M5-T166), not page 1. Decision summary is back to one page.

END-OF-REPORT

VISUAL DELTA 2 — pages 1-4 at 68d417fe (M5-T165 rework 2 fd649b66, M5-T166 rework 3 68d417fe). I am an AI agent; not a human/professional review. Read-only; re-rendered pages 1-4 at 150-300 dpi in /tmp/claude-0/visual-delta2/ and read the HTML/SVG.

=== M5-T165 (page 1) — VERDICT: PASS ===
Both advisories resolved, nothing new.
- A1 (key figures wrapping) RESOLVED: the 30 pt figures are now one line each — "20,150 sq ft", "Up to 55 ft", "3 storeys".
- A2 (duplicate scheduled figure) RESOLVED: the scheduled-building key figure is now "3 storeys"; "20,150 sq ft" appears once as a giant figure (floor-area allowance) and once in the body sentence "Scheduled floor area: 20,150 sq ft; site fit unverified". No duplicate headline number.
- Extra wins: the street address is restored ("215-16 NORTHERN BOULEVARD, Queens" in title + header); the status chips moved under each Answer label, so the Status column is gone and nothing is clipped; the whole decision summary fits one page. Ceiling 29 / Estimate 17-22 + distinction line + three linked uncertainties + scope line all present. Five-second hierarchy is strong.

=== M5-T166 (pages 2-4) — VERDICT: PASS (advisories only) ===
Owner complaint FIXED. On the page-4 close frame: labels are figure-only ("103.88 ft", "99.98 ft" ×2, "101.71 ft") on white boxes beside their lines; the basis is stated ONCE under the drawing ("All dimensions: city map outline, not surveyed.", K1); neighbours are lighter; neighbour addresses removed; no word touches a line or fill; dimension, street-name, mapped-width and basis-note labels are 8.5-9.0 pt. Legend, north arrow, scale bar, sources caption present; locator (p2) clean.

1. ADVISORY — p4 right side: "215 PLACE" and its "60 ft mapped width" sit apart and offset, while the top (Northern Blvd) and left (215 Street) group name-over-width tidily. Legible, no collision. Smallest fix: align the right street-name + width as one stacked group (site_context_plan.py / close_frame_dimensions.py label placement).
2. ADVISORY — p4 bottom: "101.71 ft" and "Lot 11" are stacked close together (each on its own white box, legible). Smallest fix: nudge "Lot 11" down or "101.71 ft" up a few pt.
3. ADVISORY — p4: legend text "No building placed" at 8.0 pt and scale-bar numerals at 7.5 pt sit below the 8.5 pt label floor (they read acceptably). Raise to 8.5 pt for strict conformance.

Page flow (the explicit question): p2 locator, p3 lot-area basis + the 3×2 heights table + the 4-row constraints table (~half the page), p4 the full-size close frame (~60% of the page). This is ACCEPTABLE FOR NOW, not a defect — there is no orphan or near-blank page (the earlier 70-word orphan is gone; the tables now sit together on p3), and a full-size dimensioned site drawing reasonably occupies its own page. ADVISORY: co-fitting the tables with the drawing to drop one page would tighten it, but the builder is correct that this needs page-break CSS in layout.py, an M5-T165 file — so route it through the orchestrator (M5-T166 is forbidden to edit layout.py), not as an M5-T166 self-fix.

Notes (not new findings): the p3 lot-area-basis line still reads "the tax-map outline area of 10,387.99 sq ft" for a value NB-04 records as gis — unchanged, already tracked under the DB-245 GIS-wording sweep per the earlier scope correction; not re-raised. Whole report: 10 pages (before 9); the +1 is the full-size site drawing page, reasonable. Page 1 no longer spills; no orphan pages remain.

END-OF-REPORT

## G4 qa-engineer (first review and two delta reviews)

# M5-T165 — G4 QA gate report (qa-engineer, independent, read-only)

I am an AI agent. This is an automated review, not a human or professional/legal review.

**VERDICT: PASS with required corrections** (one narrow REQUIRED finding on S18; one ADVISORY).

Reviewed at the pinned head `4617c72067c1f6783debea92d02602238dfe8415` (task/wave24-report-v3), in a `git archive` copy under my scratch. Expected page-1 texts were worked from the contract + benchmark fixture + NB-01/03/04/05 BEFORE reading the change.

## Commands (direct exit codes, lanes venv, my pinned-head copy)
| Command | Exit | Result |
|---|---|---|
| `ruff check .` (services/api) | 0 | All checks passed |
| `pytest -q tests/drawings tests/cad tests/journey tests/api/test_report_read_api.py tests/api/test_report_read_context.py` | 0 | 1782 passed, 6 skipped |
| `pytest test_report_page_one.py test_report_benchmark.py -v` | 0 | 22 passed (every S# test green) |
| `tools/modularity_check.py --check` | 0 | no new offender; readers.py not flagged |
| `tools/research_record_check.py --check` | 0 | NB-01 code_current=True, review_state=stale |
| web `presentation-tokens.mjs --check` | 0 | CSS+Python mirror the JSON source |
| web `node --test presentation-tokens.test.mjs` | 0 | 10 pass, 0 fail |

## Scenario results (independently reproduced)
- **S1** PASS – my probe: page 1 = four kinds (results+assumption lines, one site graphic, ceiling|estimate block, ≤3 uncertainties) + furniture only.
- **S2** PASS – `page_one_zoning_lot_sentence` parses the condition to exactly "the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70" (index entry, not the CRFN instrument); generic line only in not-checked state, once.
- **S3** PASS – layout.py reads every `pt` from TYPE tokens; headline `.answer-figure` = 30 pt (28–32).
- **S4** PASS – one block; WORDING["ceiling_estimate_distinction"] **byte-equals** the contract quote; no "buildable/achievable/can be built" on page 1; ceiling = "Legal ceiling 29 Conditional" (never Provisional); withheld-ceiling path shows unit_limit_text reason.
- **S5** PASS – exactly three: Zoning lot, Recorded lot area, Rear yard, in order; rear yard from constraint_text open check.
- **S6** PASS – page-1 anchors #issue-1/2/4 and #estimate-B all resolve to ids present.
- **S7** PASS – my own count (header/footer excluded): page 1 = 190 (≤200); total = 2327 (≤2448); no page-1 8+-word sentence found elsewhere; repeat count 1 distinct / 3 printings (≤ before-set 3/7, falls).
- **S8** PASS – "20,150 ÷ 680 = 29.63 → 29" all present in evidence; zoning-lot flag is item 1; test_report_law_links.py unedited and green.
- **S9** PASS – eleven-option test `test_s5_eleven_options_shared_limitations_once` (line 175) untouched by the diff; green.
- **S10** PASS – readers.py 32 top-level symbols, ~475 SLOC (≤600/≤40); `zoning_lot_basis` re-exported as facade; modularity --check exit 0.
- **S11** PASS; **S12** PASS – scope line on page 1, exclusions head appendix, no feature inventory, six page types.
- **S13** PASS – moved effect texts unchanged except rear yard; test_location_sheet.py unedited and green.
- **S14** PARTIAL / could-not-check – wrapper class `summary-figure` and caption "The lot among its neighbours (city map; not surveyed)." present in code; the report-print flag-on e2e is **browser/CI-only** (I ran no e2e, no servers, ports untouched).
- **S15** PASS – NB-01 rev 4 code_current=True exit 0; code_identity includes readers.py `91f607aa…` (M5-T162) + zoning_lot_item.py `f3595523…`; isolation decision recorded in dependency_assessment.
- **S16** PASS – wording group holds the 3 texts, each equal to the contract quote (distinction line; "Apartment area"; "Other building area: core, circulation, walls and services"; caption with em dash); screen tokens mirror JSON.
- **S17** PASS – long apartment-estimate sentence prints exactly ONCE; test_vc2 changed 2→1 is a true regression guard (I measured count=1 on the benchmark).
- **S18** NOT met as written (see Finding 1).
- **S19** PASS – "not known beyond the corner area" absent report-wide; rear-yard open check names ZR 23-344(b) and (c)(3), draws no conclusion, links ZR 23-344.

## My own mutation proofs (scratch copy; restored, re-verified green)
1. One char of the distinction token (`demonstrated`→`Demonstrated`) → FAILED test_s4, test_module_mirrors_the_json_source, test_wording_group_holds_the_three_contract_texts (3). Restored → green.
2. Re-added a "What this report covers" coverage inventory to page 1 → FAILED test_s7_page_one_section_is_within_the_word_cap and test_s12 (2). Restored → green.

## R008 condition — MET
Page 1 presents the rear yard only as the open check: uncertainty row "Rear yard · ZR 23-344 · Unresolved"; the open-check text names 23-344(b)+(c)(3) as not yet checked, draws no conclusion, links 23-344; never worded as if the corner test were the only exception (corner wording gone).

## Points to rule on
**1 (S18 / "tax-map outline").** S18 **as written (whole report) is NOT met.** Page 1 as rendered on the benchmark is clean, and the task's explicit objective — the `lot_area` effect text in constraint_text.py now says "city map outline" — is done. My probe finds 11 "tax-map"/"tax map" strings across site-and-context, option-comparison and the appendix. Classifying each by the packet's paths:
- OUTSIDE allowed paths (cannot be fixed here; producer right to flag): site drawing caption/annotations (page_site_context.py, maps/ — FORBIDDEN), the option-comparison limitation line (options.py:45 — FORBIDDEN), and the document's own condition words "...tax-map outline area of 10,387.99 sq ft..." (fixture packages/ + app/scenario/ — FORBIDDEN).
- **INSIDE allowed paths (producer's "entirely outside allowed paths" claim is INCOMPLETE):** (a) `page_decision_summary.py:180` — the page-1 fallback site-plan caption "Site plan: the lot's approximate **tax-map outline** (city records)." (ALLOWED; page 1; reachable when a summary drawing renders, e.g. geometry present without full surroundings; not exercised by the benchmark, so untested); (b) `readers.py:505` — `_BASIS_NAMES["approximate_tax_map"]="Approximate tax map"`, emitted on the benchmark evidence page as "Lot frontage 103.88 ft · Approximate tax map" (103.88 ft is a **gis** value per NB-04). Both predate this task (unchanged in the diff) but sit in allowed files, and both violate the contract's absolute wording rule ("a city map outline is never called 'tax map' or 'tax-map outline'"). **Finding 1 (REQUIRED, narrow):** correct these two allowed-path wordings to the contract's plain words, OR the orchestrator records a backlog item and formally narrows S18 for this task (and books the forbidden-path scenario-engine/site-page wording as the owed follow-up the producer recommends).

**2 ("Estimate 17-22 Provisional").** Contract-compliant → no finding. The ceiling is labelled **Conditional**, never Provisional/settled (unit_limit_text reads the value's own `way`). Provisional is a valid one-of-six label and is applied to the *estimate*, which the contract does not bar from Provisional — it only bars presenting the estimate as a count of apartments to build. "Estimate 17-22" links to the scenario-sheet calculation and the distinction line calls it "an unvalidated apartment-yield range; neither is a demonstrated layout", so it is not presented as apartments-to-build.

**3 (estimate sentence once / test 2→1).** Matches S17. The long sentence prints once (scenario sheet); page 1 shows the range and links to #estimate-B. The test_vc2 change from 2→1 reflects the real de-duplication, not a weakening.

## Findings
- **F1 — REQUIRED (narrow).** `page_decision_summary.py:180` and `readers.py:505` still call a GIS/map value an "approximate tax-map outline" / "Approximate tax map" (one on page 1, one on the benchmark evidence page); both are in allowed paths and violate the contract wording rule, so S18 is not met as written. Pre-existing; fix in-scope or book+narrow as above.
- **F2 — ADVISORY.** The dominant whole-report "tax-map outline" text is produced by forbidden files (scenario engine, fixtures, site/option pages); a scenario-engine + site-page wording follow-up is owed (as the producer notes).

## What I could not check
- S14 report-print e2e (browser/CI only; no servers run).
- PDF page counts / printed point sizes (H2, by eye — not this gate).
- Live ACRIS/ZR sources: not re-opened; the evidence records are current (checked 2026-10-11) and NB-01 code_current verified structurally. Every unresolved input stays unresolved (zoning lot Conditional, lot area Conditional, rear yard Unresolved open check).

END-OF-REPORT

# M5-T165 — G4 QA DELTA review (qa-engineer, independent, read-only)

I am an AI agent; this is an automated review, not a human/professional review. Reviewed the change from my earlier head `4617c720` to `2767f6a1` on task/wave24-report-v3 (git archive copy, lanes venv). Step 4 (NB-01 entry) is G1-only — not mine.

## DELTA VERDICT: PASS

## 1. Attribution confirmed (git)
Between 4617c720 and 2767f6a1, M5-T165's allowed-path **source** files changed in exactly two commits:
- `20801603` — zoning_lot_item.py (docstring only; marker constant and functions unchanged, behaviour-identical) + NB-01 code-identity bump.
- `2767f6a1` — layout.py, page_decision_summary.py, test_report_page_one.py, producer-report.md.
`485b8ecb` touched only the packet + G0 (control, not producer source). `page_location.py`/`test_location_sheet.py` changed in `ca74a6a6` = **M5-T166** (disjoint; test_location_sheet.py is in M5-T165's forbidden set, correctly untouched by this task). No other commit touched M5-T165's allowed-path source.

## 2. Judgement under my gate rules
- **Visual F1 (headline on whole sentences):** fixed. `_answer_cell` now splits key figure / detail. Each `answer-figure` is a short value read from a single document value field — `max_residential_floor_area["display"]`, `"Up to "+max_building["display"]`, `area_disp+" sq ft"` — **never recomputed, never a regex-cut sentence**. Guarded by new `test_rework1_headline_holds_only_a_key_figure_not_a_sentence`.
- **Visual F2 (Status column clipped):** fixed. 88 mm figure column + 8 mm gap < 182 mm printable; answers column `min-width:0`. Guarded by new `test_rework1_answers_table_and_figure_fit_printable_width`.
- **No font below its token:** confirmed — new `.answer-detail` = body token (10.5 pt); every font-size still from a TYPE token (test_s3 green); layout spacing reductions are mm margins/line-weights, not type.
- **Page 1 holds every item (my probe):** four kinds + furniture all present; S1/S4/S5/S6/S11/S12 unchanged.
- **S7 caps hold (my own count):** page 1 = 192 ≤ 200; total = 2329 ≤ 2448; repeats 1 distinct/3 printings ≤ before-set; no page-1 8+-word sentence elsewhere.
- **S18 as narrowed:** page 1 and every text this task writes carry **no** "tax map"/"tax-map"; the lot_area effect text says "city map outline"; the page-1 fallback caption is now "Site plan: the lot's city map outline (not surveyed)." The scope correction (485b8ecb) is well-formed; the residual engine/site/option/evidence wordings are tracked in **DB-245 QUEUED(M5-T167)** with a sound PDF↔website↔DXF parity rationale (R041/R057).
- NB-01 code_current=True at 2767f6a1; zoning_lot_item.py LF sha256 = `88e1916a…` matches the record.

## 3. Commands (direct exit codes, git archive 2767f6a1, lanes venv)
| Command | Exit | Result |
|---|---|---|
| `ruff check .` (services/api) | 0 | All checks passed |
| `pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` | 0 | 161 passed |
| (aux) `research_record_check.py --check` | 0 | NB-01 code_current=True |

The CI text-scan guard that triggered 20801603 (`test_result_ways.py::test_only_task_m5_t130_bridge_and_facts_modules_import_the_decision_module`) now passes.

## 5. Carry / required corrections
My earlier verdict carries to 2767f6a1 as a clean **PASS**. My one REQUIRED correction (F1) is resolved: (a) the page-1 fallback caption is fixed in-scope; (b) the shared engine basis-rank display name ("Approximate tax map") is formally narrowed out of S18 and deferred to DB-245/M5-T167 (correct — renaming it in the PDF alone would split the PDF from the website). My F2 advisory is folded into the same DB-245 sweep.

## Could not check
Visual finding 3 (page-1 one-page fit) and printed PDF pagination are visual/H2 matters (no browser/PDF render here) — the visual G3 reviewer's return is authoritative on fit. All unresolved inputs remain unresolved (zoning lot / lot area Conditional; rear yard Unresolved open check).

END-OF-REPORT

# M5-T165 — G4 QA DELTA review 2 (qa-engineer, independent, read-only)

I am an AI agent; automated review, not a human/professional one. Reviewed 2767f6a1 → `fd649b66` on task/wave24-report-v3 (git archive copy, lanes venv).

## DELTA VERDICT: PASS

## 1. Attribution (git) — confirmed
Between 2767f6a1 and fd649b66 the only M5-T165 allowed-path changes are:
- `fd649b66` (rework 2): layout.py, page_decision_summary.py, test_report_page_one.py, producer report.
- `c2413c5d`: NB-01 — a review-block APPEND only (a G1 data-contract-verifier rev-4 entry); the record's own `implementation.code_identity` is unchanged (the hashes in the diff are inside the appended `reviewed_code_identity`). No code identity changed.
`test_site_context_close_frame.py` (the other changed file) = `cd6d7fc3`, M5-T166 (disjoint; not an M5-T165 path).

## 2. Judgement (my gate)
- **Key figures from document value fields, nothing recomputed:** "20,150 sq ft" (max_residential_floor_area display), "Up to 55 ft" (max_building_height display), "3 storeys" (storey_count). The scheduled row's key figure is now its own storey count (height fallback), not a second copy of the allowance; the fixed "Scheduled floor area: 20,150 sq ft; site fit unverified" is kept verbatim as the detail. All three key figures are DISTINCT and each keeps its number with its unit — both visual advisories resolved.
- **No font below its token:** rework-2 diff changes only table geometry (two columns, fixed 24 mm name column, gap 6→4 mm); no font-size touched; test_s3 green.
- **S14:** `.summary-figure` wrapper + 88 mm column unchanged; the "neighbours" caption lines were not touched by rework 2.
- **Status label per answer:** shown — each answer name carries its Conditional chip (status moved beside the name in the 2-column table).
- **Every page-1 item present; S7 caps hold (my count):** page 1 = 188 ≤ 200; total = 2325 ≤ 2448; repeats 1 distinct/3 printings; no "tax map" and no forbidden word on page 1.

## 3. Commands (direct exit codes, git archive fd649b66, lanes venv)
| Command | Exit | Result |
|---|---|---|
| `ruff check .` (services/api) | 0 | All checks passed |
| `pytest -q tests/drawings/report tests/drawings/test_presentation_tokens.py tests/scenario/three_answers/test_result_ways.py tests/api/test_report_read_context.py` | 0 | 163 passed (incl. 2 new test_rework2_*) |

## 4. Carry
My PASS carries to fd649b66. Nothing new; all unresolved inputs stay unresolved (zoning lot / lot area Conditional; rear yard Unresolved open check). PDF one-page fit is the visual gate's call (no render here).

END-OF-REPORT
