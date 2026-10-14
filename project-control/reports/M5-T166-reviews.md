# M5-T166 reviews (every return kept unchanged)

Reviews of M5-T166 (one locator and the dimensioned close-up). First reviews at 7e09cc50 (G1, G3, G4: PASS with one required correction, the page-1 graphic) and a print at 5c96f92e (visual: PASS with required corrections); delta reviews at aecc4261 (rework 1: PASS, the correction resolved) and at 68d417fe (reworks 2 and 3, the owner's correction of 2026-10-12: PASS, no required finding); the visual review PASS at 68d417fe (advisories only, tracked as DB-246 and DB-249). After 68d417fe only the G1 reviewer's own entry in record NB-04 was re-issued (5e362d7f); no drawn output changed.

Every reviewer is an AI agent; none is a human or professional review.

## G1 data-contract-verifier (first review and delta reviews)

G1 DATA-CONTRACT REVIEW — M5-T166 (sources, data, bases). Reviewer: data-contract-verifier (AI agent). This is an automated review, NOT a human or professional review. Read-only; no files written, no ledger/git/gh writes. Pinned head 7e09cc5097ec12e2e11c96bb401dce66b5c53e92 (base d248293a0), read from /root/project/w-wave20 object store and an archived copy.

VERDICT: PASS WITH REQUIRED CORRECTIONS. My four-point data-contract share and the R008 condition all PASS. One REQUIRED finding on the "ONE SCOPE DECISION" (page-1 graphic) — it is an orchestrator/M5-T165 routing matter, not a data-contract defect and not a file the builder may edit.

WHAT I CHECKED AND VERIFIED

(1) Every drawn value traced to one basis, nothing invented (D-094 R044). I recomputed lot 70's outline edges from the raw MapPLUTO ring (EPSG:2263) in geometry-calculations.json (saved-copy sha256 31f1d4bf… matches NB-04 E4; raw ring in data/mappluto.json matches vertex-for-vertex, LotArea 10075 / Shape__Area 10387.99): edges = 99.976469 (shared w/ lot 1), 103.879213 (north), 99.976053 (opposite lot-1), 101.708961 (shared w/ lot 11), 2.224450 (sliver, shared w/ lot 61). Lots sharing an edge with 70 = 1, 11, 61 (confirmed independently from coordinates and from edge_sharing_lots()). I then loaded the production map_context (recorded_pack_provider) and dumped every drawn label's data-source: the 4 dimensions are each `edge:/map_context/subject_lot/outline/0#{0..3}` rounding to 99.98/103.88/99.98/101.71 ("… ft, map outline, not surveyed"); the sliver edge #4 (2.22 ft) is correctly left undimensioned (close_frame_dimensions.py MIN_LABELLED_EDGE_FT=6.0; test_s1 asserts len==4). Lot numbers "Lot 70/1/11/61" trace to subject_lot/bbl and tax_lots/entries/170,171,178/bbl (BBLs 4073340070/0001/0011/0061, all block 7334). No tax-map value (100.76 / 100.0 depth) is drawn as a dimension (the close frame draws the GIS 103.88 Northern-Blvd edge, never the 100.76 tax-map frontage); one basis only ({GIS_BASIS}); nothing merged. PASS.

(2) Street names + mapped widths. The drawn widths trace to `/map_context/streets/entries/{34,19}/mapped_width_ft` = Northern Boulevard 100, 215 Place 60. Source data: DCM_Street_Center_Line (dcm_street_centerline_lot_envelope_4073340070.json) gives Northern Boulevard Streetwidth='100', 215 Place Streetwidth='60', both Feat_Type='Mapped_St'. inputs.py:46 documents mapped_width_raw as "the DCM `Streetwidth` text … the mapped width". NB-06 independently records both as "DCM Street Center Line mapped width" (wide/narrow per D-052). I fetched the live official layer def (…/DCM_Street_Center_Line/FeatureServer/0?f=json): the layer represents "official street names and widths shown on the Official City Map of New York City." So these are DCM/City-Map mapped widths (usually incl. sidewalks), NOT LION paved widths. PASS.

(3) NB-04 revision 2. research_status unchanged = conflicting_evidence (rev1→rev2). close_frame_dimensions.py added to code_paths; its recorded identity f036a957ae5a2f1f99164e8d0872dd2bcc8369b6b27337c7935cf81c4b2c6f4d equals `git show 7e09cc50:…close_frame_dimensions.py | tr -d '\r' | sha256sum` exactly. Every drawn edge not previously recorded is now a gis quantity with its source: 99.97647 (E4 adjacent 70-1, drawn "99.98 ft…"), 99.97605 (E4 lot-70 edge, drawn "99.98 ft…"), 101.70896 (E4 adjacent 70-11, drawn "101.71 ft…"); the pre-existing 103.87921 north edge had its scope extended to note "drawn … 103.88 ft, map outline, not surveyed". The connector identities are byte-unchanged from the rev-1 review (I did not touch connectors). `tools/research_record_check.py --check` exits 0 (NB-04 conflicting_evidence, code_current=True). PASS.

(4) Basis labels vs contract. Contract Wording section: gis = "city map outline" (short form on drawings: "map outline"). The close frame draws "map outline, not surveyed" (short form, correct for a drawing); NB-04 scope notes mirror it; packet example matches. PASS.

R008 CONDITION (D-094 R017). The close frame draws NO rear-yard/setback/envelope area. Verified in code (draw_block_scene close path draws lots, buildings, street areas, dimensions, labels only) and by test_s4_no_yard_or_setback_area (kinds_drawn ∩ {yard,court,setback_zone,setback_line,envelope} == ∅). NB-03's unresolved ZR 23-344(b)/(c)(3) analysis (research_status interpretation_awaiting_review) feeds nothing drawn. PASS.

Reproduced at the pinned head: pytest test_site_context_close_frame.py + test_constraints_page.py + test_location_sheet.py = 41 passed. Heights table (_heights_table) reads label/display/status from the document (readers.present_values), not invented (S7). "Map geometry only" printed once (test_s6). "No building placed" is the close-frame legend entry; the not-placed sentence stays on the scenario sheet (test_s8). block_map.py and its tests (test_context_maps.py) are unchanged by the diff (restorable; S3).

FINDINGS

F1 — REQUIRED (scope decision; not a data-contract defect). The packet objective and plan (workorder-D094-v2.md:621) state "The page-1 graphic becomes the compact close frame (maps side only)." It is NOT met: page 1 still embeds the COMPACT SUMMARY frame — page_decision_summary.py:105-121 `_summary_block` ("page type 1's small site figure is the COMPACT summary frame … (ruling Y10)", caption "The lot among its neighbours (city map; not surveyed)."). page_decision_summary.py is an M5-T165 allowed_path (confirmed in project-control/tasks/M5-T165.json), is on M5-T166's Forbidden list ("every M5-T165 file"), and is absent from the diff — so the builder cannot and correctly did not change it. The governing contract (ARCHITECT_PRESENTATION_CONTRACT.md page-type table row 1) requires only "One site graphic" on page 1 — no close frame — so the current page-1 graphic is contract-compliant and data-clean (its summary frame draws with_edges=False/with_widths=False, i.e. no dimensions or widths). Also, no "compact close" frame variant exists in site_context_plan.py (frames: summary/wide/close/report/sheet); the "close" frame is sized to the full A4 width (≤515.95 pt), not the 88 mm column. Smallest compliant change if the owner/orchestrator wants it: inside page_decision_summary.py `_summary_block`, swap only the embedded SVG (the "maps side") to a compact close frame, leaving the figure wrapper (class summary-figure), the 88 mm column (layout.py:108 `.summary-figure { flex:0 0 88mm }`) and its caption unchanged — this is M5-T165 work plus a new compact-close frame in site_context_plan.py (M5-T166), and must be routed by the orchestrator exactly as the packet's own clause routes page-1/2/3 CSS to the M5-T165 builder. Recommended disposition: orchestrator reconciles the packet line with the contract (page 1 needs only "one site graphic") — either record that the objective is satisfied-by-contract/descoped, or raise a coordinated M5-T165 change. Nothing here blocks the G1 data-contract gate.

A1 — ADVISORY. The Northern-Blvd width label "100 ft mapped width" shares the numeral 100 with the tax-map lot depth (100 ft). It is NOT a tax-map value: it is sourced to streets/entries/34/mapped_width_ft (DCM Streetwidth=100, NB-06 basis gis). No action; noted so the coincidence is not misread.

A2 — ADVISORY. The close frame also labels a nearby "215 Street" with "60 ft mapped width" (streets/entries/7, DCM Streetwidth=60). Correctly sourced; present because it falls within CLOSE_STREET_REACH. Not a provenance issue.

A3 — ADVISORY. NB-04 review_state currently reads "stale" in the record check because agent_reviews still holds only the rev-1 review; appending the rev-2 entry below resolves it.

AGENT REVIEW ENTRY for NB-04 review.agent_reviews (append UNCHANGED; matches the existing entry shape):
{
 "reviewer": "data-contract-verifier",
 "date": "2026-10-11",
 "reviewed_revision": 2,
 "reviewed_code_identity": {
  "services/api/app/drawings/maps/close_frame_dimensions.py": "f036a957ae5a2f1f99164e8d0872dd2bcc8369b6b27337c7935cf81c4b2c6f4d"
 },
 "verdict": "agrees",
 "findings": [
  "G1 at 7e09cc50: the close frame draws only the gis (city map outline) basis. Lot 70's four edges >= 6 ft (99.98, 103.88, 99.98, 101.71 ft) recomputed from the MapPLUTO ring and each drawn label traced to edge:/map_context/subject_lot/outline/0#{0..3}; the 2.22 ft lot-61 sliver is left undimensioned. All four drawn edges are recorded as gis quantities with their E4 source; research_status stays conflicting_evidence. No tax-map value (100.76 / 100 ft depth) is drawn; nothing is merged across bases. close_frame_dimensions.py identity verified by `tr -d '\\r' | sha256sum`; the two connectors are byte-unchanged from the revision-1 review and were not edited."
 ],
 "report": "project-control/reports/M5-T166-G1.md"
}
(If the orchestrator saves the G1 report under a different filename, update the "report" value to match; the orchestrator sets the record's last_changed/digest resync in the same commit.)

WHAT I COULD NOT CHECK / LIMITS
- I did not re-fetch the live MapPLUTO/tax-map/PLUTO/DOB sources; I verified against the repo's saved evidence packs whose sha256 match NB-04 E3/E4/E5/E6 and the owner-research DCM pack, plus one live DCM layer-definition fetch. The orchestrator re-fetched the tax maps and MapPLUTO outline on 2026-10-10 (recorded identical). The DCM Streetwidth field has no field-level description in the service metadata; I relied on the layer-level statement ("widths shown on the Official City Map"), Feat_Type='Mapped_St', inputs.py:46 and NB-06.
- I did not run the full regression (CI's job); I ran the focused map/report tests, the record check, and block_map file presence. S9 byte-identical snapshots and S5/S10 budgets are G3/G4 scope; I did not re-run them.
- F1 is a contract/scope judgment delivered for the orchestrator; final ownership/descope is the orchestrator's call (producer ≠ verifier).

END-OF-REPORT

G1 DELTA REVIEW — M5-T166 rework 1 (data-contract-verifier; I am an AI agent, not a human/professional review). Read-only; scratch /tmp/claude-0/g1-t166-delta/. Reviewed aecc4261 vs my pin 7e09cc50.

DELTA VERDICT: PASS. F1 RESOLVED: YES.

1) Scope of change confirmed with git. Between 7e09cc50 and aecc4261, exactly 5 allowed-path files differ: site_context_plan.py, page_location.py, tests/.../test_location_sheet.py (all from rework ca74a6a6, the cherry-pick), NB-04.json (append from aecc4261), and the producer report. The net code+test diff over those three source files has patch-id 0242f0e0 — byte-identical to the rework commit alone (ca74a6a6^..ca74a6a6), proving NO contamination from the branch's disjoint commits (M5-T165 page-1 4617c720, docstring 20801603, other-task records). The two M5-T166 commits are the only changes to allowed-path files.

2) F1 judged resolved. A new `summary_close` frame (site_context_plan.py:+613) renders the CLOSE composition (close_frame_view: subject + edge-sharing lots 1/11/61 dominate) at the 88 mm page-1 size with with_edges=False, with_widths=False, label_focus=False — so NO dimension lines, NO street widths, NO neighbour labels; "never a bare number without its basis" is met by drawing no numbers (the dimensioned, basis-labelled version stays on the page-3 large close frame). page_location.py:134 swaps the page-1 graphic embed from "summary" to "summary_close" (maps side only). page_decision_summary.py (class summary-figure, caption "The lot among its neighbours (city map; not surveyed).") and layout.py (.summary-figure flex 0 0 88mm) are UNTOUCHED (absent from the diff) — wrapper, class, 88 mm column and caption unchanged, and the caption stays accurate. No data label < 8.5 pt (none drawn). draw_block_scene draws no yard/setback area, so R008/R017 preserved. Data-contract clean: the compact frame draws only outlines, street names (name_source) and the subject "Lot 70" (bbl_source) — no invented, tax-map, or mixed-basis value.

3) Commands (git archive aecc4261 copy, lanes venv):
- `ruff check .` → All checks passed! exit 0
- `pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py` → 222 passed, 4 skipped, exit 0
- `tools/research_record_check.py --check` → PASS, exit 0 (NB-04 conflicting_evidence, code_current=True).

4) Carry: my earlier G1 PASS carries to aecc4261; the sole REQUIRED finding F1 is now resolved, so G1 at aecc4261 is PASS with no outstanding required corrections.

NEW / OBSERVATIONS (advisory). The NB-04 entry appended is my text verbatim (reviewed_revision 2, identity f036a957, verdict agrees), report path set to project-control/reports/M5-T166-reviews.md as stated. The record check still reports NB-04 review_state=stale (benign; exit 0): my rev-2 entry attests only close_frame_dimensions.py, while the record's code_identity also lists the two connectors (byte-unchanged, last attested in the rev-1 review). If the orchestrator wants review_state=current, add the two unchanged connector identities to the rev-2 entry; otherwise it is a known-benign structural state.

COULD NOT CHECK: full CI regression and S9 byte-identical snapshots (CI/G3-G4 scope); I ran the delta-requested focused checks only. No live source re-fetch (verified against sha256-pinned packs as before).

END-OF-REPORT

G1 DELTA REVIEW — M5-T166, ADDENDUM (re-issued NB-04 entry). I am an AI agent; not a human/professional review. Read-only.

My prior delta verdict stands: DELTA VERDICT PASS, F1 RESOLVED YES (ruff exit 0; pytest 222 passed/4 skipped exit 0; record check exit 0; scope-of-change proven to be the two M5-T166 commits only, patch-id 0242f0e0).

Per the orchestrator's note (research_record_check derive: a review reads "current" only when reviewed_code_identity covers EVERY implementation.code_paths entry), I computed the LF-normalised sha256 (`git show aecc4261:<file> | tr -d '\r' | sha256sum`) of all three code_paths at aecc4261:
- services/api/app/connectors/mappluto_geometry_arcgis.py = 383d49c1b63771e843fa70457cda039398090ae803244d39575ae311b18fd9f4 (byte-unchanged from the rev-1 review that reviewed it)
- services/api/app/connectors/mappluto_lot_outline.py = df5ea5efeee71ce35910315fd07c595a3cd9d92f67367a78edcb489d64c1cad8 (byte-unchanged from the rev-1 review that reviewed it)
- services/api/app/drawings/maps/close_frame_dimensions.py = f036a957ae5a2f1f99164e8d0872dd2bcc8369b6b27337c7935cf81c4b2c6f4d
All three equal the record's implementation.code_identity block.

RE-ISSUED AGENT REVIEW ENTRY for NB-04 review.agent_reviews (append/replace UNCHANGED):
{
 "reviewer": "data-contract-verifier",
 "date": "2026-10-11",
 "reviewed_revision": 2,
 "reviewed_code_identity": {
  "services/api/app/connectors/mappluto_geometry_arcgis.py": "383d49c1b63771e843fa70457cda039398090ae803244d39575ae311b18fd9f4",
  "services/api/app/connectors/mappluto_lot_outline.py": "df5ea5efeee71ce35910315fd07c595a3cd9d92f67367a78edcb489d64c1cad8",
  "services/api/app/drawings/maps/close_frame_dimensions.py": "f036a957ae5a2f1f99164e8d0872dd2bcc8369b6b27337c7935cf81c4b2c6f4d"
 },
 "verdict": "agrees",
 "findings": [
  "G1 at 7e09cc50 (carried to aecc4261): the close frame draws only the gis (city map outline) basis. Lot 70's four edges >= 6 ft (99.98, 103.88, 99.98, 101.71 ft) recomputed from the MapPLUTO ring and each drawn label traced to edge:/map_context/subject_lot/outline/0#{0..3}; the 2.22 ft lot-61 sliver is left undimensioned. All four drawn edges are recorded as gis quantities with their E4 source; research_status stays conflicting_evidence. No tax-map value (100.76 / 100 ft depth) is drawn; nothing is merged across bases. close_frame_dimensions.py identity verified by `tr -d '\\r' | sha256sum`; the two connectors are byte-unchanged from the revision-1 review and were not edited by this task."
 ],
 "report": "project-control/reports/M5-T166-reviews.md"
}

With all three identities listed, NB-04 should read review_state=current (the only reason it showed stale was the single-file reviewed_code_identity). No other change to my delta findings.

COULD NOT CHECK: unchanged from the delta — full CI regression / S9 snapshots (CI/G3-G4 scope); no live source re-fetch (sha256-pinned packs).

END-OF-REPORT

G1 DELTA REVIEW 2 — M5-T166 (reworks 2 & 3, scope correction). I am an AI agent; not a human/professional review. Read-only; scratch /tmp/claude-0/g1-t166-delta2/. Reviewed 68d417fe vs my last PASS at aecc4261.

DELTA VERDICT: PASS. No REQUIRED finding. Verdict carries to 68d417fe.

1) Scope (git-confirmed). In aecc4261..68d417fe only 98c2ad16 (my re-issued NB-04 entry), cd6d7fc3 (rework 2) and 68d417fe (rework 3) touch M5-T166 allowed-path files; the scope-correction commits f96a087f/d91c95cd touch only control-plane (packet/G0). The contract file and NB-04 are touched by M5-T166 commits only — no M5-T165/M5-T176/owner-log contamination.

2) Reworks 2 & 3 under S1-S17.
- S1: labels are figure-only (`format_feet` → "99.98/103.88/99.98/101.71 ft", no basis words); the shared basis is stated once in a note under the drawing, role "dimension-basis" == ["All dimensions: city map outline, not surveyed."] at ≥8.5 pt; each DrawnDimension still records basis=GIS_BASIS; the mixed-basis tag path exists and is tested (no frame mixes today).
- S14: every data label sits on a white #FFFFFF background (one rect per label); no witness/dimension line crosses any label, its OWN lines included (cross_max_len=0.0, pad≤0.5); lot/street/width labels also avoid the dimension segments; forced cases fail closed (a line through a box is detected; every-lane-blocked raises DimensionPlacementError — never shrinks).
- S15: neighbour addresses dropped (lot_address==[]), lot numbers kept {70,1,11,61}; neighbour buildings wrapped in lighter groups (0<opacity<1), subject fill full-strength; same on the page-1 compact frame.
- S17: only the two contract sentences changed (Page-2 paragraph and the Wording gis clause), exactly as quoted; nothing else in the contract moved.
- R008: no yard/court/setback_zone/setback_line/envelope kind drawn.
- Data-contract: every drawn figure = edge length of the subject gis outline (source edge:/map_context/subject_lot/outline/0#{0..3}); label_problems(svg,DOC)==[]; no tax-map value (100.76/100) drawn; nothing merged across bases. The basis note is fixed contract wording, not invented data.

3) Commands (git archive 68d417fe, lanes venv):
- `ruff check .` → All checks passed! exit 0
- `pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py tests/scenario/three_answers/test_result_ways.py` → 247 passed, 4 skipped, exit 0
- `tools/research_record_check.py --check` → PASS exit 0 (NB-04 conflicting_evidence, code_current=True; review_state=stale only because the stored entry still carries the old close_frame_dimensions.py hash — the re-issued entry below fixes it).

4) NB-04 scope edits: the four gis quantities' `scope` strings now read "...drawn on the close frame as '103.88 ft' (the shared basis is stated once in a note under the drawing; owner K1, 2026-10-12)" etc. — accurate to the figure-only rendering; values (103.87921/99.97647/99.97605/101.70896) and bases (gis) UNCHANGED. close_frame_dimensions.py identity updated to 5dba6cf8 (matches my computed LF sha256).

RE-ISSUED AGENT REVIEW ENTRY (replace unchanged):
{
 "reviewer": "data-contract-verifier",
 "date": "2026-10-12",
 "reviewed_revision": 2,
 "reviewed_code_identity": {
  "services/api/app/connectors/mappluto_geometry_arcgis.py": "383d49c1b63771e843fa70457cda039398090ae803244d39575ae311b18fd9f4",
  "services/api/app/connectors/mappluto_lot_outline.py": "df5ea5efeee71ce35910315fd07c595a3cd9d92f67367a78edcb489d64c1cad8",
  "services/api/app/drawings/maps/close_frame_dimensions.py": "5dba6cf8e8307111b80fbd25bffe3c62964166572efd9a7e9347dbaeffb79dea"
 },
 "verdict": "agrees",
 "findings": [
  "G1 at 68d417fe (reworks 2-3): the close frame draws only the gis (city map outline) basis. Lot 70's four edges >= 6 ft recomputed from the MapPLUTO ring and drawn FIGURE-ONLY (99.98, 103.88, 99.98, 101.71 ft), each label traced to edge:/map_context/subject_lot/outline/0#{0..3}; the shared basis is stated once in a note under the drawing (\"All dimensions: city map outline, not surveyed.\") per owner K1 (2026-10-12); the 2.22 ft lot-61 sliver is undimensioned. The four scope strings were reworded to this rendering with values and bases unchanged; research_status stays conflicting_evidence. No tax-map value (100.76 / 100 ft) is drawn; nothing is merged across bases. close_frame_dimensions.py identity verified by `tr -d '\\r' | sha256sum`; the two connectors are byte-unchanged and were not edited by this task."
 ],
 "report": "project-control/reports/M5-T166-reviews.md"
}

COULD NOT CHECK: full CI regression / S9 snapshots / the by-eye print check of pages 1-4 (S16) and the 9-vs-10-page/layout.py page-break point are G3/visual/CI scope — not this gate. No live source re-fetch (sha256-pinned packs).

END-OF-REPORT

## G3 code-reviewer (first review and two delta reviews)

G3 CODE-REVIEW GATE REPORT — M5-T166 (reviewer: code-reviewer). I am an AI agent; this is not a human or professional review.

VERDICT: PASS with required corrections (one REQUIRED finding; all other code is sound). Recorded as PASS per repo semantics; the REQUIRED correction blocks acceptance.

Pinned head reviewed: 7e09cc5097ec12e2e11c96bb401dce66b5c53e92 (base d248293a0). The pinned commit is a SIBLING of the w-wave20 branch head (not an ancestor; the task files are absent at HEAD), so I worked from `git archive 7e09cc50` into my scratch tree and the shared object store. Lanes venv used for all runs.

WHAT I CHECKED (reproducible)
- Independent expected values (D-093, from sources not the brief): computed the lot-70 gis outline edge lengths from packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json (geometry.lot_outline, crs local_feet): edges = 2.22445, 101.70896, 99.97605, 103.87921, 99.97647 ft. These match NB-04 E4 (the saved MapPLUTO/geometry-calculations primary source) and NB-04 rev-2's added gis quantities exactly. The <6 ft (2.22) sliver is correctly left undimensioned; the four >=6 ft edges draw "101.71 / 99.98 / 99.98 / 103.88 ft, map outline, not surveyed". No tax-map value (100.76/100) is drawn.
- close_frame_dimensions.py (new, 106 SLOC): witness-line endpoints are the edge's own projected vertices (fr.px(a/b)); DrawnDimension.a_px/b_px are those exact points (S1 error 0). Fails closed: size<8.5 raises DimensionPlacementError; place()->None raises (no silent shrink/drop, S2). Basis is a parameterised constant ("map outline, not surveyed") — acceptable because the close frame only ever draws the gis outline; provenance source is edge:<outline.source>/0#i. Hash f036a957… matches NB-04 code_identity (LF-normalised) — verified.
- context_scene.py compose_context: new 'close' mode + CLOSE_* constants; the 'No building placed' legend row. SVG is sized from its viewBox (svg_document sets viewBox=width/height and width/height attrs; no CSS). test_close_frame_fits_the_a4_content_width: width<=515.95 pt.
- site_context_plan.py: site_context_view refactored into _view_toward_streets with SITE_* preserved; new close_frame_view (tighter CLOSE_PAD/REACH). The threaded min_pt/min_label_pt defaults (0.0) make width_size/asz/sizes behaviour-identical for summary/wide/report/sheet — so S9 holds (verified: test_snapshots.py 20 passed; producer changed no .svg).
- page_site_context.py: 3x2 heights table from the document (_height_pairs by _qualifying_affordable_or_senior suffix; missing counterpart -> "—"); height rows removed from constraint rows (no double-listing); _not_placed sentence removed from the site page, legend entry used instead; lot-only fallback in _site_outline UNCHANGED.
- page_location.py: page 2 = neighbourhood locator only; block still built (restorable) but not printed; one-outline/availability check and the "one line, never blank" fallback unchanged; report_plan now frame="close".
- map_caption.py: drops the "Map geometry only…" note so it prints once (S6).
- R008/R017 (checked): the close frame draws no yard/court/setback/envelope geometry — draw_block_scene emits only lots, buildings, subject, dimensions, labels, frame. test_s4_no_yard_or_setback_area_is_drawn asserts kinds_drawn ∩ {yard,court,setback_zone,setback_line,envelope} == ∅. CONDITION MET.
- Runs: tests/drawings/maps/test_site_context_close_frame.py + report/test_location_sheet.py + report/test_constraints_page.py + api/test_report_read_context.py = 46 passed (60.8s). test_snapshots.py = 20 passed. ruff app/drawings/maps+report = clean. research_record_check --check = exit 0 (NB-04 conflicting_evidence unchanged, code_current=True, review_state=stale awaiting G1 — expected). SLOC (tool's own method): close_frame_dimensions 106, context_scene 488, site_context_plan 542, map_caption 85, page_location 134, page_site_context 112 — all < WARN 600; neither maps file is in the modularity baseline, so --check would pass. The dimension logic was extracted into a new focused module rather than growing site_context_plan.py — good modularity (extraction-before-growth, stable interfaces, focused tests).

FINDINGS
1. [REQUIRED] Objective item "The page-1 graphic becomes the compact close frame (maps side only)" is NOT met. page_location.py:resolve still builds summary_plan = embed(render_site_context_plan, SITE_LAYERS, "summary"); builder.py feeds that to page 1 as site_context_plan. Page 1 therefore keeps the OLD wider "summary" site plan (SITE_PAD 80 ft, "lot among its neighbours"), not a compact instance of the new close-up composition. The objective (packet) and workorder-D094-v2.md line 618 both state this as a deliverable, and the common-part ruling instruction treats a miss as REQUIRED. The builder's rationale ("the compact of the two jobs" = summary; changing it alters M5-T165's page 1) is only partly correct: the GRAPHIC is produced in the builder's own editable page_location.py, and test_page1_carries_the_summary_frame_site_plan / its short caption are in the builder's editable test_location_sheet.py — so the change is within this task's scope. Smallest compliant change: in page_location.py make summary_plan render the COMPACT close frame (maps side only), keeping the page-1 wrapper, class="summary-figure", the 88 mm column (layout.report_css flex:0 0 88mm) and the short caption unchanged; update the two pins in test_location_sheet.py accordingly. REAL coordination risk to relay to the orchestrator: the compact close frame's svg text (dimension/street labels) can change page-1 visible-word counts / snapshot that M5-T165 (page_decision_summary.py, test_report_page_one.py, test_report_pages.py — all forbidden here) owns; confirm with M5-T165 before/at integration. This is a scope-completeness defect, not a code-quality defect.

2. [ADVISORY] The "No building placed" legend entry (_not_placed_legend_row) prints at TYPOGRAPHY.label_pt = 8.0 pt. The task tests treat it as kit furniture (>=7 pt) and exclude it from the >=8.5 pt data-label check, consistent with the existing legend/scale/north furniture. Contract section 6 ("drawing labels at least 8.5 pt") is enforced on the data labels (dimension/street/street_width/lot_number/lot_address, all verified >=8.5). Flagging for the later visual-quality-reviewer PDF pass to confirm the 8.0 pt legend reads acceptably at print size.

3. [ADVISORY] The plan text states site_context_plan.py "is at 509 SLOC"; actual is 542 SLOC. Still well under the 600 warn threshold and not baseline-tracked, so no modularity failure — noting only the plan-vs-actual drift.

WHAT I COULD NOT CHECK (and why)
- `tools/modularity_check.py --check` could not run live: the archived tree is not a git repo (git ls-files exit 128) and I am read-only (cannot git init). Verified instead via the tool's own SLOC method and thresholds + baseline/exceptions inspection; producer reports exit 0 from their worktree. Needs to pass in CI at the exact head.
- Printed-PDF visual judgement (label collisions, legibility, north/scale look) — that is the visual-quality-reviewer's separate G3 share on a rendered PDF; out of my code-only scope.
- Live primary sources (ArcGIS/MapPLUTO, DOF tax maps): no network and read-only. I verified the drawn edge lengths against NB-04 E4's saved geometry values via the benchmark fixture; I did not re-fetch the live endpoints or read the 2017 Buckley survey/2018 deed (NB-04 marks these not_found/access_blocked). DCM street widths (100/60 ft) come from the map document's own mapped_width_ft; traced via label_problems==[] only, not the DCM source itself.
- e2e/browser (report-print.flag-on.spec.ts) and any running server — not run (thin-client rule; ports 3000/3001/8000 untouched); CI is the authority.

UNRESOLVED INPUTS STAY UNRESOLVED: NB-01 access_blocked, NB-03 and NB-06 interpretation_awaiting_review, NB-04 conflicting_evidence (recorded area 10,075 vs gis 10,387.99; frontage 100.76 vs 103.88). The close frame draws only the gis outline with the "map outline, not surveyed" basis and no yard/setback/zoning-lot geometry depending on those analyses, so no unresolved input is turned into a settled drawn figure. The gis outline area/edges never enter a zoning calculation here.

END-OF-REPORT

M5-T166 DELTA REVIEW (G3 code). I am an AI agent; not a human/professional review.

DELTA VERDICT: PASS. F1 resolved: YES. My earlier PASS carries to aecc4261.

Item 1 (scope) — CONFIRMED. The only changes to M5-T166 allowed-path files between my pin 7e09cc50's content and aecc4261 are the two named commits:
- ca74a6a66 (rework 1): site_context_plan.py (+17), page_location.py, test_location_sheet.py, producer report — all allowed paths.
- aecc42610 ([ORCH-CORRECTED per G1]): NB-04 only.
The on-branch re-land 09ac564e7 is byte-identical to 7e09cc50 for every M5-T166 allowed-path file; `git diff 7e09cc50 09ac564e7` differs ONLY in disjoint ledger files (M5-T164/M3-T006 gates, state.json, D-094 verification). No disjoint commit (M5-T165 4617c720/20801603, M5-T176) touched an M5-T166 allowed path.

Item 2 (F1) — RESOLVED. New `summary_close` frame draws the close composition (close_frame_view, subject + edge-sharing neighbours dominate the tight view) fitted to the 88 mm SUMMARY_PLAN column, with_edges=False/with_widths=False, so NO dimension lines or labels are drawn there. page_location.resolve embeds it as summary_plan (page-1 graphic); report_plan stays the large page-3 "close" frame. Judged against the rules: the page-1 wrapper, class summary-figure, the 88 mm column and the caption "The lot among its neighbours (city map; not surveyed)." are unchanged (page_decision_summary.py/layout.py untouched); no bare number without basis (no numbers drawn on page 1); labels >=8.5 pt and fail-rather-than-shrink still enforced on the page-3 frame (close_frame_dimensions.py unchanged). Dropping the dimension label at the 88 mm size (too narrow for a legible >=8.5 pt basis label) is the correct "never shrink" choice. test_page1_carries_the_compact_close_frame_site_plan proves page1_svg == summary_close and != old summary, and absence of dimension roles; test_page1_compact_close_frame_states covers present/absent/outline-moved. R008 holds (with_edges=False, no yard/setback). site_context_plan.py 552 SLOC (<600 warn).

Item 3 (re-run, in a git-archive aecc4261 copy, lanes venv):
- `cd services/api && python -m ruff check .` -> "All checks passed!" EXIT 0.
- `python -m pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py` -> 222 passed, 4 skipped, EXIT 0.

New/notes: NB-04 change is a pure additive G1 agent-review entry (data-contract-verifier "agrees", reviewed_revision 2); research_record_check --check EXIT 0, status still conflicting_evidence. NB-04 review_state still reads "stale" (a G1/acceptance-stamp matter, not a G3 code defect). Unresolved inputs (NB-01 access_blocked; NB-03/NB-06 awaiting review) stay unresolved; page 1 draws no geometry depending on them. Could not check live: modularity_check --check (archive has no git index — verified via SLOC), printed-PDF visual (visual-quality-reviewer's later pass), CI at the exact head.

END-OF-REPORT

M5-T166 DELTA REVIEW 2 (G3 code). I am an AI agent; not a human/professional review.

DELTA VERDICT: PASS. My verdict carries to 68d417fe. No REQUIRED finding. (Item 4 is G1-ONLY — the NB-04 re-issued review entry and the four scope-string edits are the data-contract-verifier's call, outside my G3 gate; not done here.)

Item 1 (scope) — CONFIRMED. Between aecc4261 and 68d417fe the ONLY commits touching M5-T166 allowed-path files are 98c2ad16 (NB-04 G1 entry replacement), cd6d7fc3 (rework 2) and 68d417fe (rework 3). f96a087f and d91c95cd touch only control-plane files (directive records, G0, packet json, state) — no allowed-path producer file. The contract file ARCHITECT_PRESENTATION_CONTRACT.md is touched by 68d417fe only; no disjoint/cross-task commit (M5-T165/M5-T176/master-plan) touched any M5-T166 allowed path. aecc4261 is a linear ancestor of 68d417fe.

Item 2 (rework 2+3, S1-S17) — judged at 68d417fe:
- S1: labels are figure-only — DrawnDimension.text == "<fig> ft" (test_s1_each_label_shows_only_the_figure); the shared basis is stated once under the drawing as role="dimension-basis" == ["All dimensions: city map outline, not surveyed."] at >=8.5 pt (GIS_BASIS_NOTE); basis still recorded on each dimension; the mixed-basis path (edge_bases naming >1 basis -> per-label short tag) is exercised, and a single basis stays figure-only. Nothing merged; no tax-map value.
- S14: two-pass placement draws all witness/dimension lines first, then places each label avoiding lot boundaries + street lines + ALL dimension/witness lines (own included) with cross_max_len=0.0 and a white background (halo rect appended to parts BEFORE the text -> correct z-order, verified in sheet.py). Forced-failure tests are non-vacuous: test_s2_a_forced_collision_fails_closed and test_s14_a_label_with_no_clear_place_fails_rather_than_shrinking raise DimensionPlacementError; test_s2_a_line_through_a_label_box_is_detected proves the no-crossing check catches a line through (True) and clears one beside (False). One white background per label (count ==).
- S15: neighbour addresses dropped (with_address=not close_style; lot_address role == []), lot numbers kept {70,1,11,61}; neighbour buildings wrapped in opacity 0.45 group (kind still registered -> legend entry kept), subject fill NOT inside any lighter group; applies to the page-1 summary_close frame too.
- S17: EXACTLY the two intended passages changed — the Page-2 close-up sentence and the Wording-paragraph gis entry (basis once under the drawing, figure-only labels, short tag only when bases mix, citing owner K1 2026-10-12); nothing else in the contract changed.
- R008: close frame draws no yard/court/setback/envelope geometry (test_s4_no_yard_or_setback_area_is_drawn); the lighter-neighbour change affects building fills only. Every drawn value traces to the document; the basis note is a fixed honesty string (no fabricated number). Non-close frames are behaviour-identical (halo/opacity/with_address/light_neighbours/close_style all default off) — no committed snapshot .svg changed (S9 holds).

Item 3 (git archive 68d417fe, lanes venv):
- `python -m ruff check .` -> "All checks passed!" EXIT 0.
- `python -m pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py tests/scenario/three_answers/test_result_ways.py` -> 247 passed, 4 skipped, EXIT 0.

ADVISORY (non-blocking): (a) site_context_plan.py is now 597 SLOC — 3 under the 600 warn threshold; a candidate for extraction before any further growth (close_frame_dimensions.py 158, context_scene.py 523, page_site_context.py 109 — all comfortably under). (b) The single-basis note is placed at a fixed y in the reserved band (not run through the collision-checked place()), so S14's no-crossing/white-background guarantees do not cover the note itself — it relies on the reserved band; the visual reviewer's S16 print check is the backstop. (c) page_site_context.render reorders the section (tables before the frame) to avoid an orphaned table; this is in-scope (report/layout.py untouched, S12), but M5-T165's test_report_pages.py (S7/S10 word budget, forbidden here) must read green at the accept head in CI. Unresolved inputs stay unresolved (NB-01 access_blocked; NB-03/NB-06 awaiting review); no drawn figure depends on them.

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

G4 QA GATE REPORT — M5-T166 "One locator and a dimensioned constraints close frame"

I am an AI agent (qa-engineer). This is an independent, read-only review, NOT a human or professional/legal review. I did not produce this task. Frozen reviewed head: 7e09cc5097ec12e2e11c96bb401dce66b5c53e92 (base d248293a0). I worked in a `git archive 7e09cc50` copy under /tmp/claude-0/t166-g4/tree with the lanes venv; forbidden files confirmed untouched (`git diff --name-only d248293a0 7e09cc50` names none of layout.py/builder.py/readers.py/page_decision_summary.py/test_report_pages/benchmark/page_one/constraint_text/zoning_lot_item).

VERDICT: PASS with required corrections (one REQUIRED finding, F1 — the page-1 scope clause).

COMMANDS I RAN (direct exit codes, in the archive copy / lanes venv):
- `python -m ruff check .` (services/api) -> All checks passed, exit 0.
- `python -m pytest -q tests/drawings tests/cad tests/api/test_report_read_context.py` -> 1739 passed, 6 skipped, exit 0 (161.6 s). All S1-S13 tests individually PASSED.
- `python tools/research_record_check.py --check` -> exit 0; NB-04 status=conflicting_evidence (unchanged), code_current=True, review_state=stale (rev 2 awaits G1; reported, not failed).
- `python tools/modularity_check.py --check` (real repo /root/project/w-wave20, read-only; task files byte-identical at 7e09cc50 vs HEAD per `git diff --stat`) -> exit 0; none of this task's files in the warn list.
- My own probes (/tmp/claude-0/t166-g4/probe.py, probe2.py) -> exit 0.

INDEPENDENT VALUE DERIVATION (from the primary source, not the brief): geometry-calculations.json edge_lengths_ft["70"] = [99.97647, 103.87921, 99.97605, 101.70896, 2.22445]; adjacent_shared_lengths["70"] = {1:99.976, 11:101.709, 61:2.224}. So lot 70 shares edges with 1, 11, 61 (matches), has 5 edges, 4 are >=6 ft. My PROBE A confirmed the close frame draws exactly those 4, each endpoint on the projected ring vertex (<=0.01 ft), each length == the primary-source value, each label naming its basis ("99.98 / 103.88 / 99.98 / 101.71 ft, map outline, not surveyed"); the 2.224 ft sliver (edge 4) is undimensioned. No tax-map value (100.76/100) is drawn.

SCENARIO TABLE (scenario | how tested | result | exit):
- S1 endpoints/basis/no-merge/no-tax-map | test_s1_* (4) + my PROBE A (ties to primary source) + PROBE B negative controls | PASS | 0
- S2 >=8.5pt, no collision, fail-not-shrink | test_s2_* (3): sub-minimum & cramped frame both raise DimensionPlacementError | PASS | 0
- S3 page 2 = locator only, block_map green | test_s3 / test_location_page_is_the_locator_only + full suite (block_map untouched) + PROBE D (block_map count 0) | PASS | 0
- S4 frame contents; one-outline & lot-only fallback unchanged | test_s4_close_frame_contents / _no_yard_or_setback_area / _a_missing_layer_gives_unavailable | PASS | 0
- S5 <=3 map figures, each distinct | test_s5 + PROBE D: {site_context_plan:2, neighbourhood_map:1}=3, block_map:0 | PASS | 0
- S6 "Map geometry only" once | test_s6 + PROBE D: count==1 in full report | PASS | 0
- S7 3x2 heights table from doc; coverage once; svg only with map doc | test_s7_* (4) + PROBE D/E | PASS | 0
- S8 legend on site, sentence on scenario sheet | test_s8 / test_s3 / test_report_read_context.py:66 + PROBE D | PASS | 0
- S9 unchanged frames byte-identical; close frame deterministic | test_snapshots.py (no snapshot changed) + test_s9_close_frame_is_deterministic | PASS | 0
- S10 site-and-context visible words <= 199 baseline | test_s10 + PROBE F measured 163 (<=199); G0 report confirms 199 is the recorded 2f546ec5 baseline | PASS | 0
- S11 modularity passes / file modular | modularity_check exit 0; site_context_plan.py 542 SLOC (<600 WARN), new close_frame_dimensions.py 106 SLOC; growth 509->542 non-material (limit 559) | PASS | 0
- S12 section ids, page-1 wrapper, layout.py untouched | test_s12 + diff shows layout.py/wrapper files not in diff | PASS | 0
- S13 NB-04 rev2 code_paths + drawn edges as gis quantities; status unchanged | verified LF-sha256 of close_frame_dimensions.py == f036a957... recorded; all 4 drawn edges recorded (north 103.87921 from rev 1; +99.97647/99.97605/101.70896); sliver correctly omitted; research_status conflicting_evidence unchanged; record check exit 0 | PASS | 0

R008 CONDITION (no rear-yard/setback AREA whose basis depends on the unresolved ZR 23-344(b)/(c)(3) analysis): CONFIRMED. PROBE2 shows the close frame's kinds_drawn = {building_footprint, existing_building, neighbour_lot, street_area, subject_lot}; no yard/court/setback/envelope/sky kind; no suspicious svg token; the "No building placed" legend swatch is an empty dashed rect (no proposed building drawn). NB-03/NB-06 stay interpretation_awaiting_review, NB-01 access_blocked — no unresolved input becomes a drawn figure.

MY MUTATION PROOF (PROBE G, reverted): weakening the asserted label input from "99.98 ft, map outline, not surveyed" to "99.98 ft" flips the S1 basis assertion (`'map outline' in text`) from True to False; the real value passes. Also independently: a 0.1-unit endpoint shift gives dist 0.1000 > 0.01 tolerance (S1 vertex check would catch an off-vertex endpoint).

E2E (apps/web/e2e/report-print.flag-on.spec.ts, location block): read-only check. The spec now expects locationSvgs==1, wideFigureCount==1, everyWideHasSvg==true, captionWithDate==true, images==0. PROBE2 against the actual rendered report HTML: location block has 1 `.location-wide-figure`, 1 `<svg`, 1 `.figure-note`, 0 raster `<img`, no "photo" wording, "Block close-up" absent. The spec's expectations match what the pages print. I did NOT run the browser test (thin-client/read-only/ports forbidden); CI runs it.

FINDINGS:
F1 (REQUIRED — scope decision). Objective clause "The page-1 graphic becomes the compact close frame (maps side only)" is NOT met. page_location.py:138 still embeds `frame="summary"` for page 1; test_location_sheet.py:81-91 pins the summary frame. Reading the objective against the plan text (workorder lines 616-618 pair "a large close frame" for page 3 with "the compact close frame" for page 1 — parallel construction => both are CLOSE frames at different sizes) and the contract, the summary frame is not a compact close frame. The builder's three justifications do not hold: (1) the page-1 drawing is fed from page_location.py (T166-ALLOWED), not the forbidden page_decision_summary.py, so a "maps side only" swap needs no forbidden file; (2) there is no page-1 snapshot pin — test_report_page_one.py and test_report_benchmark.py are empty placeholders, and the only forbidden M5-T165 page-1 test (test_summary_frame_site_plan_in_decision_summary) asserts merely `class="summary-figure"`, which a drawing swap preserves; (3) test_page1_carries_the_summary_frame_site_plan lives in T166's OWN allowed test_location_sheet.py and test_s12 checks only the wrapper/caption — both self-imposed, not external constraints. Smallest compliant change: in page_location.py change the page-1 embed to a compact close frame (a compact-sized `close` variant), keeping the page-1 wrapper, class summary-figure, the 88 mm column and its short caption "The lot among its neighbours (city map; not surveyed)." unchanged; update test_page1_carries_the_summary_frame_site_plan to assert the compact close frame. CONTRACT NUANCE for the orchestrator: ARCHITECT_PRESENTATION_CONTRACT "Page 1" requires only "One site graphic" (not a close frame), so page 1 is CONTRACT-compliant as built. The orchestrator therefore has a legitimate choice — implement the maps-side swap, OR formally amend/relax this packet objective to accept the summary frame (a scope decision; relaxing a stated objective should not be done silently by the builder, and narrowing owner scope is the orchestrator's/owner's call, not mine).

A1 (ADVISORY). The workorder prose "site_context_plan.py is at 509 SLOC" was the pre-change base (confirmed 509 at d248293a); post-change it is 542 SLOC — growth of 33, non-material, under WARN 600. Not a defect; the packet's actual S11 is only "modularity check passes."

WHAT I COULD NOT CHECK: the Playwright/browser e2e and any running server (thin-client; ports forbidden) — verified by reading only; CI is authoritative. The street mapped widths (Northern Blvd 100 ft, 215 Place 60 ft) I confirmed trace to the map document via label_problems==[] but did not re-derive from the DCM source itself (same limitation the producer states). I could not run `modularity_check.py --check` inside the archive copy (needs a git repo; the worktree guard refused `git init`), so I ran it read-only on the real repo where the task files are byte-identical, plus measured every changed file's SLOC directly. No value in NB-04 rev 2 promotes a result or changes a verification status; the unresolved inputs stay unresolved.

END-OF-REPORT

M5-T166 DELTA REVIEW (G4 QA, rework 1). I am an AI agent; read-only; not a human or professional review. Verified at head aecc4261 in a `git archive` copy (lanes venv).

DELTA VERDICT: PASS. F1 resolved: YES.

1. GIT SCOPE CONFIRMATION. `git diff --stat 7e09cc50 aecc4261` on the task's allowed-path files = exactly 5 files: site_context_plan.py, page_location.py, test_location_sheet.py, NB-04, producer-report.md. The branch re-landed the original build as 09ac564e7, which is BYTE-IDENTICAL to my pin 7e09cc50 for every allowed-path file (`git diff --stat 7e09cc50 09ac564e7 -- services/api/app/drawings services/api/tests NB-04 e2e` = empty). So the only content changes versus my pin are ca74a6a6 (rework 1) and aecc4261 (the G1 [ORCH-CORRECTED] entry). The NB-04 change is solely an appended data-contract-verifier review entry (reviewed_revision 2, verdict "agrees", report path M5-T166-reviews.md) — no quantity, status, condition or code-identity change.

2. F1 JUDGEMENT. The rework adds a `summary_close` frame: the close composition (close_frame_view — subject lot 70 and its edge-sharing neighbours 1/11/61 dominate the tight view) at the 88 mm page-1 column, with_edges=False/with_widths=False, so no dimension lines or labels (the 88 mm column cannot carry a basis label at >=8.5 pt, so none is drawn — never shrunk, never a bare number). page_location.py embeds it as the page-1 graphic. My own probe (independent of the builder's test): page1 svg == summary_close, != old summary frame (F1), != the large page-3 close frame; page 1 has NO dimension-line and NO dimension label (the only " ft" text is the scale-bar "100 ft", role="scale"); class="summary-figure", the 88 mm column and the short caption "The lot among its neighbours (city map; not surveyed)." are unchanged; no "Sources:" long caption on page 1; the large dimensioned close frame is still printed once on the constraints sheet. page_decision_summary.py and layout.py were not touched (maps-side-only change). F1 is met under the same rules I applied before.

3. COMMANDS (archive aecc4261, lanes venv):
- `python -m ruff check .` (services/api) -> All checks passed, exit 0.
- `python -m pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py` -> 222 passed, 4 skipped, exit 0.
- `python tools/research_record_check.py --check` -> PASS, exit 0; NB-04 status=conflicting_evidence unchanged (no result promoted; unresolved inputs — NB-01 access_blocked, NB-03/NB-06 awaiting_review — stay unresolved).

4. My earlier PASS carries to aecc4261 and the single REQUIRED correction (F1) is resolved. Nothing new of concern. The page-1 scale-bar on an 88 mm thumbnail is a visual-quality (G3) matter, not a G4 correctness defect.

END-OF-REPORT

M5-T166 DELTA REVIEW 2 (G4 QA, reworks 2+3). I am an AI agent; read-only; not a human or professional review. Verified at head 68d417fe in a `git archive` copy (lanes venv). Item 4 (re-issue the NB-04 review entry) is marked G1 ONLY — not my gate — so I did not perform it; I did judge the four NB-04 scope edits for correctness (below).

DELTA VERDICT: PASS. No REQUIRED finding. My earlier PASS (and F1 resolution) carries to 68d417fe.

1. GIT SCOPE. Among M5-T166's allowed-path content files, `git log aecc4261..68d417fe --` on those paths lists ONLY 98c2ad16 (G1 re-issue), cd6d7fc3 (rework 2), 68d417fe (rework 3). f96a087f/d91c95cd are control-plane (packet/G0/state), not content. No foreign task's commit touched a T166 allowed path. The contract file changed EXACTLY the two sentences of S17 (Page-2 "site and context" + the Wording gis-basis line), both describing figure-only labels with the basis stated once; nothing else in the contract changed.

2. SCENARIOS (reproduced; my own probe, not the builder's assertions):
- S1 figure-only + basis once: the 4 dimension labels read "99.98/103.88/99.98/101.71 ft" (figure only, no "map outline"); each ties to the primary-source edge_lengths_ft["70"]; basis still recorded GIS_BASIS; the single note "All dimensions: city map outline, not surveyed." appears exactly once at >=8.5 pt. No tax-map value (100.76/100) drawn; nothing merged.
- S14 collisions: 14 white label-background rects; 0 of the 4 dimension labels is crossed by any drawn line with its OWN witness/dimension lines included (box_crosses_lines, pad 0.3, max_len 0.0). Tests add forced-failure cases: a forced DimensionPlacementError, and positive/negative controls for box_crosses_lines (line through box -> True; beside -> False) over all 12 witness+dimension segments vs every label. Covers "every label vs every drawn segment and fill, own included."
- S15: 0 lot_address labels on the close frame; a `lighter-neighbour-building` opacity group is emitted (neighbours drawn lighter).
- S17: only the two contract sentences changed (confirmed by diff).
- R008: close frame kinds_drawn = {building_footprint, existing_building, neighbour_lot, street_area, subject_lot}; no yard/court/setback/envelope geometry. Unresolved NB-03/NB-06/NB-01 stay unresolved; no unresolved input becomes a drawn figure.
- Nothing invented: every drawn value traces to the document; the basis note is a fixed honesty string (no number).

NB-04 scope edits (correctness only): the four `scope` strings reworded to the figure-only rendering; the VALUES (103.88/99.98/99.98/101.71) and the BASIS ("gis") are unchanged; research_status stays conflicting_evidence; no result promoted. implementation.code_identity for close_frame_dimensions.py = 5dba6cf8... matches the file I hashed (LF).

3. COMMANDS (archive 68d417fe, lanes venv):
- `python -m ruff check .` (services/api) -> All checks passed, exit 0.
- `python -m pytest -q tests/drawings/maps tests/drawings/report/test_location_sheet.py tests/drawings/report/test_constraints_page.py tests/api/test_report_read_context.py tests/scenario/three_answers/test_result_ways.py` -> 247 passed, 4 skipped, exit 0.
- `python tools/research_record_check.py --check` -> PASS, exit 0; NB-04 status unchanged.

WHAT I COULD NOT CHECK: the actual PDF pagination / S16 by-eye print check of pages 1-4 (no servers/PDF render; ports forbidden) — I confirmed the code reorder (lot-area basis + both tables together, the large frame on the next page) so no 4-row table is orphaned, but the printed layout is the orchestrator's/G3-visual check (after-68d417fe/). ADVISORY (dependency, not my gate): NB-04 reads review_state=stale because the G1 review entry's reviewed_code_identity still carries the rework-1 hash f036a957 for close_frame_dimensions.py (now 5dba6cf8); the G1 delta (item 4) must re-issue it. The record check still PASSES and no drawn output is affected.

END-OF-REPORT
