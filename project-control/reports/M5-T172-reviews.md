# M5-T172 reviews (every return kept unchanged)

- Four producer rounds (backend-engineer, worktrees): round 1 stopped with nothing edited (the four lot measures reach the emitter only through the engine bridge; scope correction 1 at 4516dbd7 after a read-only depth check); round 1b builder commit b843f9b6 integrated as 11b2bb59 (the four placeholder pages of the contract, removed at dc8449d1, taken from the builder); round 2 builder commit e9b760dc integrated as e79ddbc6 (scope correction 2: the wiring moved into placement_wiring.py, three consumer tests, the massing snapshot); round 3 builder commit 5ef7d7eb integrated as 5994e220 (scope correction 3: the report claims only what it draws; one placed-and-drawn predicate). Each integration's files equal the builder commit's (git diff empty); nothing outside the allowed paths.
- G2 orchestrator self-check at 5994e220: the live route reproduces the committed placed benchmark (test_results_read_api street_on); the real-preview prints: print-e79ddbc6 (round 2) changed pages 3, 5, 6, 8, 9, 10 against print-23aeeff5 (10 pages both); print-5994e220 (round 3) changes only page 5's status ('Worked out; not drawn'), page 9's commit line and page 10's method sentence against print-e79ddbc6; the document fingerprint is stable between the two prints; whole api suite green at each round (builder: 10081, 10103 passed; G4: 10099 passed); CI run 38769376547 at e79ddbc6 21 of 21.
- Reviews at e79ddbc6: G1 data-contract-verifier PASS (values re-derived from placement-building-b.json; NB-01 r10, NB-05 r8, NB-06 r5 delta reviews PASS); G3 code-reviewer PASS with one finding taken as required (one 'placed' predicate, closed in round 3); G3 visual-quality-reviewer two REQUIRED findings (page 5's site-plan claim; the appendix's 'it is shown'), closed in round 3; G4 qa-engineer PASS (five mutations). Delta checks of round 3 at 5994e220 by four new reviewers of the same types follow each original return below.
- Carried to M5-T173 part B (backlog DB-283, DB-284): drawing the placed footprint on the site plan and the maps (then site_plan_draws_placed_footprint() and _area_illustration_drawn() switch on), the locator legend, NB-04's stale code identity; and the G1 observation that the drawn plates are on the city-map basis while placement.outline is the tax-map rectangle (each labelled; never mixed).

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

G1 DATA-CONTRACT VERIFIER report — M5-T172 part B (wave 28). Pinned SHA e79ddbc6c369a8a30c5d292245371a1e10eca4c5 on task/wave28-placement-wiring. I am an AI agent; this is an independent read-only review, not a human or professional verification.

VERDICT: PASS.

WHAT I CHECKED (all re-derived independently from docs/reference-cases/R6B/cases/placement-building-b.json and the quoted law, never from program output):

1. FOUR LOT MEASURES + BASES (benchmark placement.conditions + register calc-first-placement + engine bridge result_way_engine_bridge.py _placement_inputs_for):
 - Printed-tax-map frontage 100.76 ft / depth 100 ft — sourced from PLUTO lot_facts lotfront/lotdepth (basis printed_tax_map). The bridge explicitly does NOT use scope lot_front_ft (DB-260); _lot_tax_dimensions reads lotfront/lotdepth. Correct.
 - City-map (GIS) frontage 103.88 ft — from the prepared outline's Northern Boulevard frontage edge (I measured the drawn floor-plate polygon frontage edge = 103.8792 → 103.88). GIS depth 99.97 ft — from the lot-reach measure (99.9747 → 99.97). Correct bases, no mixing.

2. RE-DERIVED VALUES, all match the reference case and the benchmark:
 - Plate 20150/3 = 6,716.67; tax plan depth 6716.6667/100.76 = 66.66; footprint 66.66×100.76 = 6,716.66 (placement.outline rectangle 100.76×66.66; register footprint_sqft 6716.66). 
 - Tax back clearance 100−66.66 = 33.34; GIS back clearance 35.31 (I confirmed the rounding path: round plan depth to 64.66 and depth to 99.97 first, then subtract → 35.31; the unrounded path gives 35.32, so 35.31 is the reference-case value and the benchmark/register both carry 35.31 — RISK B5/DB-260 honoured). Frontage difference 103.88−100.76 = 3.12. All present verbatim in the benchmark placement.conditions and register actual (33.34/35.31/3.12/66.66/6716.66).
 - Plates: geometry.floor_plates = 3 drawn plate outlines, each gross_sf 6,716.6667, reconciling to the 3-storey floor_by_floor (3×6716.6667 = 20,150); floor_stack replaced the ruling-W5 not_available block.
 - Area split: share 0.6; apartment 20150×0.60 = 12,090.00; other 8,060.00; per-storey 4,030.00 / 2,686.67; apartment+other = total 20,150.00. Benchmark area_allocation = {share 0.6, apartment 12090.0, other 8060.0, total 20150.0, fitted true}.
 - Fitted only when placed: benchmark alt is placement.status "placed" with fitted true; the way rule enforces fitted true ⇒ placed.

3. RESULTS CONTRACT + NEW WAY RULE (results_way_rules.py): new rule allocation_share_mismatch checks apartment == round_half_up2(total×share) within 0.01+ε (DB-248), alongside the existing fitted-without-placement and apartment+other=total rules. Tests tests/contracts/test_results_way_rules.py cover all four input states (equal/within-rounding/beyond-rounding/no-allocation) plus a mutation separation (beyond-rounding case balances the total so ONLY the new rule fires), and version-gating below 1.5.0. Ran: 172 passed (way-rules + register-calculations) and 160 passed (test_results_contract_1_5_0, test_report_benchmark, test_215_16_northern_journey, test_three_answers_three_way_emit, test_result_way_engine_bridge) via the lanes venv under heavy-run.lock. Benchmark is contract_version 1.5.0 and validates; 1.4.0 byte-identical path tested.

4. DELTA REVIEW OF REVISED RECORDS — all PASS:
 - NB-01 rev 10 (was 9): three_way_document.py hash 3376f7b8… — I recomputed LF-normalized and it matches. Dependency note true (three_way_document.py now emits placement/area_allocation/floor-by-floor; wiring moved to placement_wiring.py in round 2, resynced in same rev 10). Reading unchanged (zoning-lot-instruments; research_status stays access_blocked). Nothing labelled Verified (professional_review null).
 - NB-05 rev 8 (was 7): result_way_engine_bridge.py hash be72b9ce… — recomputed LF, matches. Dependency note true (bridge assembles the four lot measures). Special-density/680 reading unchanged; status answered_from_primary_source. Nothing Verified.
 - NB-06 rev 5 (was 4): both three_way_document.py (3376f7b8…) and result_way_engine_bridge.py (be72b9ce…) recomputed LF, match. Dependency note true; street-wall/setback/side-yard reading unchanged (placement checks cite the same ZR 23-335(b)); status interpretation_awaiting_review. Nothing Verified.
 - tools/research_record_check.py --check PASSES at the pinned head: NB-01/05/06 all code_current=True; "no record claims the Verified label without meeting every condition."

5. REGISTER CALCULATION ENTRIES + PINS: render_review_register.py --check PASSES (no issues) on the extracted pinned copy. Two new calculation entries (calc-first-placement, calc-area-allocation) carry step P8 / placement-building-b.json as the reference_case worked example, cited_rows from that case, human_review verdict "Not reviewed" / decision null (no human verdict, G-11). Entry actuals match my re-derivation (66.66/6716.66/33.34/35.31/3.12; 12090/8060/20150). I independently recomputed and matched every pinned module hash: three_way_document.py 3376f7b8…, placement_wiring.py 8a600b04…, geometry.py d85e1aed…, placement.py faf552ef…, area_allocation.py c644ec2f…, result_way_engine_bridge.py be72b9ce…. implementation_changed events seq 60-68 recorded for the four pre-existing calc entries + the two new entries' round-2 module move.

6. LABEL RULE (S8): placement.label and area_allocation.label are exactly "Illustrative"; the words complies/buildable/feasible appear only inside the negated disclaimer ("not a finding that the building complies, is buildable or is feasible"); "optimal" absent. placement.not_checked carries the full R093/NB-06 list; the alt-level not_checked correctly dropped "Where the plan sits on the lot" now that the building is placed; the whole-lot coverage, rear yard and zoning lot stay not-known/not-checked (genuinely unresolved, not "unfinished-feature").

OBSERVATIONS (not findings; no correction required):
 - O1 (ADVISORY, for geometry/visual reviewers): the drawn geometry.floor_plates polygon is on the GIS basis (edges 103.8792 × 64.6584, geometric area 6,716.57), while placement.outline is the tax-map rectangle (100.76 × 66.66 = 6,716.66); each plate's gross_sf label is the plate 6,716.6667. No single figure mixes two bases, and the ~0.1 sq ft plate-vs-GIS-geometry gap is within the reference case's ±0.5 sq ft reconciliation (plate and footprint are separate quantities, never forced into one), and the tax/GIS conflict is disclosed in placement.conditions. Consistent with the settled reading; flagged so the drawn-basis labelling is confirmed at G3.
 - O2: alt.footprint_area_sqft = 6716.6667 is the plate (floor area per storey), a pre-existing field unchanged by this task; the "footprint 6,716.66" my brief names is the geometric placement/register figure, which is correct.
 - O3: research_record_check reports NB-04 code_current=False. I confirmed this task did NOT touch NB-04 and did NOT change any NB-04-pinned module (mappluto_geometry_arcgis.py, mappluto_lot_outline.py, close_frame_dimensions.py — close_frame_dimensions.py is byte-identical at base 63ab5d19 and head, and already mismatched the NB-04 pin before this task). NB-04 staleness is pre-existing and out of this packet's scope (the packet correctly revised NB-04 only "if its measurement-basis reading is touched"; it was not). Worth a backlog note for a future NB-04 refresh, but not a defect of M5-T172.

WHAT I COULD NOT CHECK (out of G1 scope / other gates): the full api/web regression and lint (qa-engineer G4); the real PDF print and page diffs (visual-quality G3); professional/legal correctness of the law readings (ADR-007 — AI review only). The combined code_identity_sha256 values I did not recompute by hand, but render_review_register.py --check recomputes and validates them and PASSED.

END-OF-REPORT

## G1 (data-contract-verifier, round-3 delta check)

G1 DATA-CONTRACT VERIFIER — M5-T172 round 3 delta (reviewed SHA 5994e2201116b1c044e5b801022eed99946607a3 on task/wave28-placement-wiring). I am an independent, read-only AI agent; this is not a human or professional review. Verdict for my G1 share: PASS. No REQUIRED or ADVISORY findings.

WHAT I CHECKED (all against an archive copy of the pinned SHA; LF-normalized sha256 throughout)

1. NB-01 r10 / NB-06 r5 code identity. Of the round's five edited production files, each record cites only three_way_document.py. Both records resync it to cb9695bf9e83f6d4fc75f0fbaabdcfba4ab59f29281730cd73c7fe05788db751 — which equals my independent LF sha256 of the file at this SHA. The other four edited files (placement_wiring.py, geometry.py, drawings_embed.py, page_evidence.py) are not in either record's code_identity, so no resync is owed there (placement_wiring/geometry are tracked by the register; drawings_embed/page_evidence are pinned nowhere in the data-contract records). PASS.

2. Dependency notes / no reading / nothing Verified. The appended round-3 notes (one line each, same revision 10 / 5) are accurate: three_way_document.py now gates the page-5 line via _placement_drawn(doc.get("geometry"), placement_inputs) imported from placement_wiring; that predicate is placement-display logic (placed AND corner footprint drawable), touching no zoning-lot or street-wall/setback/side-yard reading. research_status unchanged (NB-01 access_blocked, NB-06 interpretation_awaiting_review); promotion.requested_label None in both. research_record_check reports NB-01 and NB-06 code_current=True. PASS.

3. NB-05 untouched and still current. Not in the e79ddbc6..5994e220 delta; none of its 8 code_identity paths is among the round's edits; all 8 hashes MATCH the files at this SHA; research_record_check code_current=True. PASS.

4. Register — five calculation entries. calc-lot-coverage-by-portion (rev 11→12), calc-preliminary-apartment-estimate (15→16), calc-first-building-option-complete (16→17), calc-first-placement (2→3), calc-area-allocation (2→3). Each carries matching implementation_changed history events (seq 69–73, 2026-10-15). These are exactly the entries pinning a round-edited module; no other entry pins one. I independently recomputed, per entry: every pinned module hash == the real file (geometry.py 19e727ad…, three_way_document.py cb9695bf…, placement_wiring.py ab9b2a52…) and code_identity_sha256 == sha256 over the sorted path:sha256 lines — all OK. `render_review_register.py --check` = "register check PASSED (no issues)", exit 0; it delegates to validate_calculations → code_module_errors + calc_rendered_errors, so the PASS also confirms the five calc-*.md pages and REGISTER.md/HISTORY.md are in sync. PASS.

5. research_record_check --check. Exit 0, "PASS: every record is structurally valid and no record claims the Verified label without meeting every condition." PASS.

6. Benchmark results JSON unchanged since e79ddbc6 (confirmed ancestor). packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json is blob b4c3e7944b482a488798dd27c7eaf282af670ddc at BOTH heads (byte-identical). The DXF snapshot and both kit SVG snapshots (massing, site_plan) are also blob-identical. The e79ddbc6..5994e220 delta contains no fixture/results JSON. PASS.

WHAT I COULD NOT CHECK
- Full services/api pytest (CI's job; heavy) — not run; I verified the data contract deterministically instead.
- render --write byte-diff of the markdown (read-only guard blocks file writes); covered instead by render --check's S8/calc_rendered_errors delegation, which passed.

OUT-OF-SCOPE NOTE (not a round-3 finding): research_record_check flags NB-04 code_current=False ("reported, not failed"); this is pre-existing backlog DB-283 (NB-04 stale vs close_frame_dimensions.py), untouched by this round.

END-OF-REPORT

## G3 (code-reviewer)

G3 CODE-REVIEW GATE REPORT — M5-T172 (part B, wave 28). I am an AI agent (code-reviewer), read-only; this is not a human or professional review.

PINNED/VERIFIED HEAD: e79ddbc6c369a8a30c5d292245371a1e10eca4c5 on task/wave28-placement-wiring in /root/project/w-wave20 (git rev-parse HEAD matched the pin at review start).

VERDICT: PASS (one ADVISORY finding, no REQUIRED corrections in my scope).

=== WHAT I CHECKED AND REPRODUCED ===

1. BRIDGE — four measures, each on its own source (result_way_engine_bridge.py). CORRECT.
   - tax frontage/depth from property_profile.lot_facts.lotfront/lotdepth (printed_tax_map); never the scope lot_front_ft (DB-260). gis frontage from _frontage_edge_length_ft summing the prepared outline's frontage edges; gis depth from _street_reach_ft (lot-reach). Each returns None when its source is unread — never a default.
   - Values match the settled reading docs/reference-cases/R6B/cases/placement-building-b.json: tax 100.76 x 100, gis 103.88 / 99.97 → footprint 6716.66, tax back-clearance 33.34, gis back-clearance 35.31 (not 33.32, DB-260), frontage diff 3.12.
   - S11 tests reproduced GREEN (134 passed, incl. four input-states: all four→placed+conflict; tax pair missing→withheld; gis pair missing→placed, no conflict; neither→withheld; and the mutation feeding scope frontage collapses the conflict to 0).

2. placement_wiring.py + three_way_document.py — byte-identical-when-absent + facade. CORRECT.
   - When placement_inputs is None: _placement_applied→False (defaults preserve _apply_first_option output) and the emit block (three_way_document.py:865) is skipped. geometry.py diff is purely additive, so the default not_available floor_plates path is unchanged. Emit/first_option tests GREEN.
   - Facade confirmed at runtime: PlacementInputs is the same object via three_way_document and via result_way_engine_bridge (old import path preserved); emit_three_way_document placement_inputs default = None.

3. geometry.py plates. CORRECT. Benchmark geometry.floor_plates: status available, 3 entries (1 per storey), use residential, gross_sf 6716.67; drawn ring area 6716.569 reconciles to the plate within the readers' 0.5 sq ft (Δ≈0.098, check C-4). floor_by_floor 3 storeys, height 10.0. Depth = plate/frontage so area reconciles regardless of frontage basis. Returns None (keeps honest not_available) when the footprint cannot be positioned.

4. DB-248 way rule (results_way_rules.py). CORRECT. New allocation_share_mismatch rule: apartment must equal round2(total*share) within 0.01+1e-9. Five tests (equal, within-rounding, beyond-rounding flagged, no-allocation, version-gated<1.5.0) reproduced GREEN; the beyond-rounding test proves the share rule (not the total rule) catches it. Version-gated so 1.3.0/1.4.0 docs unaffected.

5. Consumer-test edits (S13) — each only follows the placed state. OK. test_results_dxf.py asserts the one honest "measurement status not stated (floor plates)" note for the placed benchmark; test_constraints_page.py and test_location_sheet.py drop the not-placed sentence for the placed benchmark while keeping explicit not-placed coverage via a mutated floor_plates=not_available copy. All reproduced GREEN.

6. ruff — `ruff check .` over services/api: All checks passed (lanes venv).

7. modularity — tools/modularity_check.py --check: failures 0. three_way_document.py = 704 SLOC (tool source_lines), under the 750 JUSTIFY line (warn-band review signal only, no justify warning). placement_wiring.py 116, geometry.py 322.

8. No 'result_way' text in the new module — placement_wiring.py contains none; test_result_ways guard GREEN (it is not in the permitted list and correctly must stay clean).

9. Evidence-record code-identity resync verified: NB-01 rev 9→10, NB-05 rev 7→8, NB-06 rev 4→5. Recorded LF sha256 for three_way_document.py (3376f7b8…) and result_way_engine_bridge.py (be72b9ce…) match my independent `git show e79ddbc6:<path> | tr -d '\r' | sha256sum`. Dependency assessments state no reading/value/status changed.

Tests reproduced (lanes venv, under flock): test_result_ways + test_results_way_rules = 131 passed; test_result_way_engine_bridge + test_three_answers_three_way_emit + test_geometry_lot_outline + test_geometry_streets + test_first_option_results + test_result_ways_input_states = 134 passed.

=== FINDINGS ===

FINDING 1 — ADVISORY. The two "building placed" signals use different predicates and can disagree.
  Files: three_way_document.py:852 (placement_applied=_placement_applied(placement_inputs), evaluated and passed to _apply_first_option BEFORE the plates are drawn) vs the plate draw at placement_wiring.py:98/106 (via geometry.place_building_on_geometry). first_option_results.py:546-547 drops the "Where the plan sits on the lot" page-5 not-checked line whenever _placement_applied is True; the scenario-sheet not-placed SENTENCE instead keys on geometry.floor_plates actually being present (readers.building_not_placed).
  _placement_applied (placement_wiring.py:55) returns True whenever all four lot measures are present, independent of whether the footprint could be drawn. geometry._frontage_lines/_footprint_outline return None for a single-frontage (non-corner) lot (no second street to form the corner), so no plates are drawn.
  Evidence (unit-level reproduction): with all four measures present, _placement_applied → True (page-5 line dropped), yet place_building_on_geometry on a one-street available geometry returns None and leaves floor_plates unset (so the not-placed sentence stays). On such a document page 5 would say the placement is worked while the scenario sheet still says "No building is placed on this plan yet" — a self-contradiction.
  Not exercised by the benchmark (a corner lot with two streets), so S2 and every pinned test pass; but the live route threads placement_inputs whenever street_data + a confirmed frontage exist (results_read.py:400, _placement_inputs_for returns non-None for any confirmed frontage), so a single-frontage lot is a reachable live case.
  Suggested correction (for the orchestrator to weigh, likely M5-T173 territory): gate the page-5 line drop (and the area-allocation fitted flag) on the ACTUAL placed-and-drawn outcome rather than on measure presence — e.g. compute placement_applied after _apply_placement from geometry.floor_plates/placement.status — or restrict placement activation to the corner-lot case this task targets and document the single-frontage limitation. Confirm whether the live route can yet reach a single-frontage placement before shipping broadly.

=== WHAT I COULD NOT CHECK ===
- The full api pytest and web vitest regressions (a sibling G4 reviewer was running the whole api suite under the shared heavy-run lock during my review); I ran scoped suites only. CI-green at the accept head remains the orchestrator's gate.
- The rendered PDF/visual agreement of pages 3/5/6/appendix (visual-quality-reviewer's scope).
- Part-A build_placement/compute_placement_geometry/build_area_allocation internals are forbidden-to-edit and consumed read-only; I verified their outputs match the reference case via the S11 tests, not their source.
- Directive-requirement-to-evidence mapping and register/calc-doc completeness (directive-compliance-verifier / data-contract-verifier scope).

END-OF-REPORT

## G3 (code-reviewer, round-3 delta check)

G3 CODE-REVIEW GATE REPORT (delta) — M5-T172 part B, round 3 (wave 28). I am an AI agent (code-reviewer), independent and read-only; this is not a human or professional review.

PINNED/VERIFIED HEAD: 5994e2201116b1c044e5b801022eed99946607a3 on task/wave28-placement-wiring in /root/project/w-wave20. `git rev-parse HEAD` matched the pin before every command and again after my last test run (worktree did not move). Delta scope = the single cherry-pick commit 5994e220 (21 files; equals the builder's 5ef7d7eb), vs the round-2 head e79ddbc6.

VERDICT: PASS (one ADVISORY; no REQUIRED corrections in my share).

WHAT I CHECKED AND REPRODUCED (each CHECK from the brief):
1. ONE placed-AND-drawn predicate drives the three signals — CONFIRMED. three_way_document.py:856 now passes placement_applied=_placement_drawn(doc.get("geometry"), placement_inputs) (was _placement_applied). placement_wiring._placement_drawn = _placement_applied AND geometry.footprint_drawable(geometry, frontage). _apply_area_allocation gates `fitted` on _floor_plates_drawn(doc) (geometry.floor_plates.status=="available"); the scenario-sheet sentence reads readers.building_not_placed (same floor_plates). I verified footprint_drawable reuses _footprint_outline (the exact ring builder place_building_on_geometry uses) and its None-ness is independent of plate size (depth=plate/frontage is computed AFTER all None returns), so footprint_drawable (plate=1.0) == corner-drawable == floor_plates-availability for any building with storeys/area. I confirmed the emit ordering forces two expressions: _apply_first_option (page-5 line) runs at :852 BEFORE _apply_placement draws plates at :870, so page-5 must re-derive drawability while fitted/sentence (after :870) read the actual outcome — sound.
2. Named drawn predicates clear for M5-T173 part B — CONFIRMED. drawings_embed.site_plan_draws_placed_footprint() → False and page_evidence._area_illustration_drawn(results) → False, both named/documented as the single switch M5-T173 flips; the S14 tests simulate the flip and prove the text follows.
3. Corner benchmark byte-identical — CONFIRMED. recorded_215_16_northern_journey.json, the results DXF, site_plan.svg and massing.svg are sha256-identical between e79ddbc6 and 5994e220 and are absent from the round-3 diff; the byte-identical engine document means not_checked, placement and area_allocation.fitted are unchanged on the benchmark.
4. Single-frontage test is real — CONFIRMED and load-bearing. test_s15_one_predicate_decides_placed_corner_vs_single_frontage asserts, on the SAME four measures: corner → floor_plates available, line dropped, fitted True, building_not_placed False; single-frontage → placement.status=="placed" yet floor_plates NOT available, line KEPT, fitted False, building_not_placed True, fit_note names where the building sits. I independently reproduced the divergence (_placement_applied=True vs _placement_drawn=False on the single-frontage lot), proving reverting the predicate flips the assertion (builder mutation #2 is genuine). test_s15_footprint_drawable_needs_a_corner covers four geometry states.
5. ruff — All checks passed (services/api, five changed app files, lanes venv).
6. modularity — `modularity_check.py --check`: failures 0, warnings 33; three_way_document.py is in the warn band only (not above the justify/750 line) — S9/S12 satisfied.
7. No 'result_way' text in the new code — CONFIRMED (grep of added app lines in placement_wiring/geometry/drawings_embed/page_evidence: none).
Tests reproduced GREEN under flock: the two S15 tests + test_report_appendix.py + test_report_comparison.py = 26 passed. S14 tests assert the real new strings ("Worked out; not drawn"; "not yet drawn in this report; when drawn it will be shown…") and the drawn-state simulation ("it is shown…").

FINDINGS:
1. ADVISORY — placement_wiring.py:76 (_placement_drawn) vs :90 (_floor_plates_drawn). The page-5 line keys on a re-derived prediction (_placement_drawn) while fitted/sentence key on the actual drawn outcome (floor_plates). They agree on every tested and realistic case (any worked option has storeys+area), but can theoretically diverge for a degenerate first alternative with four lot measures + a corner yet no storeys/floor-area/floor-schedule (footprint_drawable ignores storeys>0; floor_plates needs it) — page-5 would drop the line while fitted/sentence stay not-placed. Not reachable for a real first option and out of S15 scope; no correction required. Concrete option for M5-T173: once _apply_placement runs, re-read _floor_plates_drawn(doc) for the page-5 line too, so all three read one source literally.

WHAT I COULD NOT CHECK: the full api pytest / web vitest regression (CI's gate at the accept head; builder reports whole api pytest 10103 passed, 8 skipped locally — unverified by me); the rendered-PDF visual agreement of pages 5/10 (the G3v delta reviewer's scope); directive-requirement/register/calc completeness (directive-compliance-verifier / data-contract-verifier scope); Part-A build_placement/area_allocation internals (forbidden, consumed read-only — verified via S15 outputs, not source).

END-OF-REPORT

## G3 (visual-quality-reviewer, round-2 review)

G3 VISUAL REVIEW — M5-T172 part B (wave 28 placement wiring). I am an AI agent; this is an independent, read-only visual review, not a human or professional review. Verdict below.

VERDICT: FAIL (equivalently "PASS with required corrections" — the increment's structure is sound, but two reader-facing contradictions in the printed report must be corrected before acceptance).

PROVENANCE CHECKED (trustworthy): after print = print-e79ddbc6/report.pdf, built+printed at e79ddbc6c369a8a30c5d292245371a1e10eca4c5 (matches the pinned SHA; page-9 "Run identity → Code commit" prints that exact hash). Before = print-23aeeff5/report.pdf. Both 10 pages. I rendered changed pages with pdftoppm and diffed text with pdftotext; I did NOT start any server or run Playwright.

WHAT PASSES:
- Page 3 open-item cross-references renumbered correctly: Rear yard→item 4, Setback→item 6, Street wall→item 7, Side yard→item 8, Max lot coverage→item 3; each resolves to the matching Open-items row on pages 7-8 (items now run 1-9; the old "Where the building sits on the lot" item 5 was removed). Internally consistent; renders cleanly, no cut text.
- Page 5 site-fit column reads "Shown on the site plan" (was "Not demonstrated"); page 6 removed the "No building is placed on this plan yet" note; page 6 floor-stack massing plates render cleanly with no overlap.
- Labels honest: Illustrative 3, Conditional 20, Provisional 3, Pending verification 10, Unresolved 3; "Verified" appears once only, in the page-10 key row marked "Not used in this report." No result is labeled Verified.
- Forbidden words scan (complies/compliant/buildable/optimal/feasible/preferred/recommended): NONE found anywhere in the after print.
- No overlap, cut text, or unreadable size on any changed page.
- (Not in T172 scope, noted no-regression:) the page-6 apartment estimate now spells out the 0.60-0.75 factor, resolving my wave-21 should-fix #1.

REQUIRED FINDINGS (one shared root cause: placement/area-split asserted in prose but drawn nowhere in the PDF):

1. REQUIRED — Page 5 claims a placement the site plan contradicts. Page 5 (Option comparison) now reads "Placed on site — Shown on the site plan", and the Building B row carries it. But the only site plan in the report, page 4 "Site plan: the lot among its neighbours", is byte-for-byte identical to the before print (sha256 of the rendered page 4 is identical in both prints), still carries the legend entry "No building placed", and draws NO gray "Building footprint" polygon on Lot 70 (Lot 70 shows only the orange subject-lot hatch plus a small dashed "existing building" outline). Page 6, the other candidate, is captioned "Floor-stack section (Illustrative): drawn from the schedule only, with no placement on the lot" — a section, explicitly not a placement. So a reader told "Shown on the site plan" finds a site plan whose own legend says "No building placed." Evidence: after print p5 "Placed on site  Shown on the site plan"; p4 legend "No building placed"; sha256(bef p4)==sha256(aft p4). Correction: either regenerate the site plan to actually render the placed Building B footprint and drop the "No building placed" legend entry, or revert the page-5 cell to a non-asserting wording (e.g. keep "Not demonstrated"/"Placement computed, not drawn") until the footprint is drawn.

2. REQUIRED — Page 10 "Area-illustration method" asserts a drawing that is absent. The block states: "it is shown as zones inside the placed building footprint." No two-zone (apartment/other) area illustration appears anywhere in the report, and no placed footprint is drawn (p4 shows "No building placed"; p6 section is "with no placement on the lot" and shows undivided storey plates). Present-tense "it is shown" sends a reader hunting for a figure that does not exist — it misleads. This is exactly the condition my brief asked about: the method block is printed although the illustration is not yet on the scenario sheet, and yes, it misleads a reader. Correction: reword to make clear the method is defined but the illustration is not drawn in this report (e.g. "would be shown as zones…" / "the illustration is not yet drawn in this report"), or add the illustration; do not claim "it is shown."

WHAT I COULD NOT CHECK:
- The website results surface (2D/3D). The placement and area split may be rendered there, but my brief scope is the PDF prints and I must not start the preview; the two findings concern the PDF, where the drawings are genuinely absent regardless of the website.
- Numerical correctness of the engine's placement geometry and area split (plate = 6,716.67 sq ft/storey ×3 = 20,150; it reconciles arithmetically, but the placement polygon/share is the G4 / directive-compliance verifier's job, not this visual pass).
- Exact font-pixel sizes / A4 bound compliance — relied on the report-print e2e (not re-run); all visible text rendered at a readable size.

Scratch (my renders/crops, outside the repo): /tmp/claude-0/review-t172-g3v/ (aft-p4hi-04.png and bef-p4hi-04.png are the identical site plans; aft-p4-lot70-04.png is the Lot-70 crop showing no footprint; aft-p10-10.png shows the method block). Source prints: /root/project/lanes-runtime/owner-docs/session-2026-10-15b/print-e79ddbc6/report.pdf and print-23aeeff5/report.pdf; text diff print-e79ddbc6/diff-vs-23aeeff5.txt.

END-OF-REPORT

## G3 (visual-quality-reviewer, round-3 delta check)

G3 VISUAL REVIEW — M5-T172 part B, ROUND 3 DELTA (scope correction 3, S14/S15). I am an AI agent; this is an independent, read-only visual review, not a human or professional review.

VERDICT: PASS (my two round-2 visual findings are closed; nothing else on the 10 pages moved; the new wording reads plainly).

PROVENANCE (independently cross-checked, not taken from the producer's print alone): after print print-5994e220/report.pdf. Its own page-9 "Code commit" field prints 5994e2201116b1c044e5b801022eed99946607a3 = the pinned SHA. I also read the SOURCE at the pin and confirmed it emits exactly the printed strings: drawings_embed.py returns "Worked out; not drawn"; page_evidence.py returns the "not yet drawn … when drawn it will be shown" clause. Rendered pages with pdftoppm, diffed text/images; started no server, ran no Playwright.

F1 (round-2 visual finding 1 — page 5 claimed a placement the site plan contradicts): CLOSED.
- Page 5 "Placed on site" now reads "Worked out; not drawn" (was "Shown on the site plan"). drawings_embed.py:site_plan_draws_placed_footprint() returns a literal False, so the status can read "Shown on the site plan" only once the footprint is actually drawn (M5-T173 part B) — not reachable on this head.
- Page 4 (the only site plan) is image-identical to before and still legends "No building placed". So page 5 now AGREES with page 4 (previously contradicted it). The contradiction is removed in substance, not papered over.

F2 (round-2 visual finding 2 — appendix "it is shown" asserts an absent drawing): CLOSED.
- Page 10 "Area-illustration method" now reads "…it is not yet drawn in this report; when drawn it will be shown as zones inside the placed building footprint." Present-tense "it is shown as zones" is gone everywhere (scan NEITHER PRESENT). page_evidence.py:_area_illustration_drawn() returns a literal False, so "it is shown" is unreachable on this head; the method facts are kept and honest.

NOTHING ELSE MOVED (10 pages):
- Pages 1–4, 6, 7, 8 byte-identical images (sha256). Desktop + phone capture PNGs byte-identical.
- Page 5 image/text change = only the status line.
- Page 9 change = only the run-identity "Code commit" hash e79ddbc6→5994e220 (provenance; everything else on page 9 text-identical).
- Page 10 change = only the method sentence.
- Label counts unchanged vs my round-2 pass: Verified 1 (key row, "Not used in this report"), Provisional 3, Illustrative 3, Conditional 20, Pending verification 10, Unresolved 3. Forbidden-words scan (complies/compliant/buildable/optimal/feasible/preferred/recommended/guaranteed): NONE. No result labeled Verified.

PLAIN-READING (architect): both phrasings are plain, honest and correctly tensed. "Worked out; not drawn" says the placement was computed but not rendered; "not yet drawn in this report; when drawn it will be shown…" documents the method without sending a reader hunting for a missing figure. No cut text, no overlap, readable sizes on pages 5/9/10.

FINDINGS: none REQUIRED, none ADVISORY for my gate's share of round 3.

WHAT I CHECKED: the before/after real prints and page images; page-4/5 consistency; the appendix method sentence; label counts and forbidden words on the whole after print; the two predicates at the pinned SHA (both literal False).
WHAT I COULD NOT CHECK (out of my scope): the website 2D/3D results surface (I must not start the preview); numeric correctness of the placement geometry / area split (G4 / data-contract scope); the single-frontage one-predicate code logic S15/_placement_drawn beyond its page-5 print consistency (G3 code / directive-compliance-verifier scope — the visual side is consistent here); exact A4 bound / font-pixel sizes (relied on the report-print e2e, not re-run — all visible text rendered readably with no clipping).

Scratch (outside the repo): /tmp/claude-0/review-t172-g3v-d/ (aft-p5hi-05.png, aft-p10hi-10.png renders; after.txt full text). Source prints: /root/project/lanes-runtime/owner-docs/session-2026-10-15b/print-5994e220/ (after) and print-e79ddbc6/ (before); diff print-5994e220/diff-vs-e79ddbc6.txt.

END-OF-REPORT

## G4 (qa-engineer)

M5-T172 (part B) — G4 QA ENGINEER gate report. I am an AI agent; this is an independent, read-only evidence gate, not a human or professional review. Pinned head e79ddbc6c369a8a30c5d292245371a1e10eca4c5 (task/wave28-placement-wiring); verified in a scratch archive copy with the lanes venv. w-wave20 had already moved off the pin (to 2727a27a) so every file/run was taken from the pinned archive.

VERDICT: PASS. No REQUIRED findings. Two ADVISORY observations and one cosmetic note below.

== CHECKS RUN (all under flock heavy-run.lock) ==
1. WHOLE api pytest -q (one run): 10099 passed, 8 skipped, 0 failed, exit 0, 526.52s. (Producer reported 10081 at its own worktree; the 18 extra are sibling tests present at the integrated pinned head — all pass, 0 failures either way.)
2. Two web benchmark pins after `npm ci` (npm@11.18.0, exit 0) in my copy: `npx vitest run results-contract-checks.test.ts journey-215-16-northern.test.tsx` → 2 files, 28 passed, exit 0.
3. test_results_read_api.py: 114 passed. test_m5t146 asserts, with street_on=True, `doc["building_alternatives"] == committed["building_alternatives"]` — the LIVE route reproduces the committed benchmark placement+area_allocation (CHECK confirmed). Its no-street branch asserts contract 1.4.0 with `placement`/`area_allocation` ABSENT and the not-placed lines kept — 1.4.0 renders unchanged (opt-in design confirmed: placement threaded only when the DCM window is supplied).
4. Five mutations, each turned a test RED then restored (cp from a pristine backup):
   (1) comment out `first["placement"]=placement` (placement_wiring.py) → test_m5t146_live_route FAILED.
   (2) disable the fitted-without-placement rule (results_way_rules.py:145) → 4 fitted tests FAILED (test_s7_fitted_true…, test_S12_fitted_without_placement_is_refused_by_both[x2], test_pure_rule_flags_fitted_without_placement).
   (3) `and False` on the DB-248 share check (results_way_rules.py:178) → test_db248_share_beyond_rounding_is_flagged FAILED; the other 4 DB-248 states still passed (proves S10 mutation: beyond-rounding passes when the rule is gone).
   (4) drop the Floor-3 floor_by_floor row from the benchmark → adapter.load_drawing_input raised DrawingInputError "plates_rows_mismatch: floor 3 residential: floor plates 6716.67 sf vs floor-by-floor None sf" (C-4). Baseline loads clean.
   (5) feed the GIS frontage (103.88) as the tax frontage in _placement_inputs_for → test_s11_bridge_assembles_the_four_measures_each_on_its_basis FAILED (asserts tax 100.76 / frontage_conflict 3.12); other S11 tests passed.

== INDEPENDENT VERIFICATION (against the settled reading placement-building-b.json + law, never a program run) ==
- Scope: all 35 changed files are inside allowed_paths; none in forbidden_paths; readers.py is NOT edited (the not-placed sentence must clear without it — it does).
- Benchmark building_alternatives[0]: placement.status "placed", basis printed_tax_map, label "Illustrative", outline 100.76×66.66; checks give tax back-clearance 33.34 and GIS 35.31; contradicted_record names frontage conflict 3.12 — all equal to the reference case. area_allocation share 0.6, apartment 12090.0, other 8060.0, total 20150.0, fitted true. Every figure matches the reference-case rows (plate 6716.67; footprint 6716.66; 12090/8060 at the owner-stated 0.60 share).
- geometry.floor_plates: 3 entries, gross_sf 6716.67 each; I recomputed the drawn polygon area = 6716.57, reconciling to the plate within 0.10 sqft (tol 0.5). floor_by_floor has 3 storeys at 6716.67 — C-4 holds (S3).
- Code identity: I recomputed LF-sha256 of three_way_document.py (3376f7b8…), result_way_engine_bridge.py (be72b9ce…), placement_wiring.py (8a600b04…), geometry.py (d85e1aed…) — all match the hashes recorded in NB-01 rev 10, NB-05 rev 8, NB-06 rev 5 and register.json. NB records say "code-identity resync only; no reading changed" — consistent with the diffs (no reading/figure/status altered). placement.py withholds on any missing measure (verified in source), backing S11's input-state claim.
- Authoritative checks (my copy): render_review_register.py --check PASS; research_record_check.py --check PASS; modularity_check.py --check 0 failures (three_way_document.py 704 SLOC = warn band, NO justify warning; placement_wiring.py 116) — S9/S12 hold.
- Register: calc-first-placement (rev 2) and calc-area-allocation (rev 2) cite step P8 / placement-building-b.json with expected==actual and "Not reviewed" (no human verdict, G-11); HISTORY events 60–68 are append-only; REGISTER rows are "Not reviewed"; nothing is labelled Verified (S5).
- Labels (S8): "Illustrative" throughout; "complies/buildable/feasible/preferred" appear only inside negations; "optimal" absent.
- Real print (orchestrator-captured print-e79ddbc6 vs 23aeeff5): 10 pages both; pages 1/2/4/7 byte-identical text; the not-placed sentence is gone on page 6; "Placed on site: Shown on the site plan" on page 5; a new page-10 "Area-illustration method" block (share 0.6, Illustrative, no reviewed rule). Pages 8/9/10 reflow from the removed open item — content preserved, not lost (I cross-checked the moved tables).

== ADVISORY (not blocking) ==
A1 (test_location_sheet.py / test_constraints_page.py; services/api/app/drawings/maps, forbidden): the site locator/close-frame context map keeps the "No building placed" legend even though the scenario sheet now shows a placed building. Honest (that map draws no massing) and disclosed by the producer, but a reader could find the placed-sheet-vs-"No building placed"-legend pairing confusing. Correction: align the locator legend with the placed state in the later drawn-page task (M5-T173); no change owed here.
A2 (NB-04, not edited by this task): research_record_check reports code_current=False for NB-04 — pre-existing, driven by its pinned close_frame_dimensions.py (under forbidden drawings/maps) changed by an earlier task. NB-04 pins no file this task edits, so leaving it unrevised is correct; the check NOTEs, does not fail. No action in scope; flag for a future maps task.
A3 (cosmetic, REGISTER.md): the two new calc rows show "Not run ()" with an empty run-id (freshly created, not yet run through the register-calculation test); other rows carry a run-id. register --check passes; fills on next run. Not a defect.

== WHAT I COULD NOT CHECK ==
- Visual rendering quality of the changed pages (visual-quality-reviewer's G3 pass) — I checked the committed text diff only.
- DXF opening in AutoCAD (no CAD app available); I confirmed the committed DXF snapshot carries the honest "(floor plates)" measurement note and the full cad suite passed.
- I did not generate my own real print (no server/ports per the read-only rule); I relied on the orchestrator-captured print-e79ddbc6 PDFs and cross-checked them against the benchmark JSON.
- modularity_check ran in a re-init'd scratch git snapshot (the real worktree had moved off the pin); results are valid because the files are byte-identical to the pinned content.
- The formal per-requirement D-094 (R044/R058/R082/R091/R092) pass is the directive-compliance-verifier's; from the QA side the data-share obligations (placement + area_allocation emitted with the Illustrative label, provenance to the reference case, no compliance/verified claims) are satisfied.

END-OF-REPORT

## G4 (qa-engineer, round-3 delta check)

G4 QA-ENGINEER GATE REPORT — M5-T172 part B, ROUND 3 (delta). I am an AI agent; this is an independent, read-only gate, not a human/professional review.

PINNED HEAD: 5994e2201116b1c044e5b801022eed99946607a3 (cherry-pick of builder 5ef7d7eb, 21 files). Ran in an archive copy under /tmp/claude-0/review-t172-g4-d/ (outside every repo); lanes venv; PYTHONPATH=<archive>/services/api so the copy's app wins over the site-packages install; every multi-file run under flock heavy-run.lock.

VERDICT: PASS.

=== TEST FOLDERS (my core CHECK; all exit 0) ===
1. tests/drawings/report — 227 passed, 84.65s, exit 0.
2. tests/scenario/three_answers — 629 passed, 2 skipped, 53.07s, exit 0.
3. tests/rules/test_zoning_rule_review_register.py + test_zoning_rule_review_register_calculations.py — 97 passed, 2.50s, exit 0.

=== THE TWO MUTATIONS (repeated independently, then restored) ===
M1 — forced drawings_embed.site_plan_draws_placed_footprint() → True: test_s14_benchmark_placed_on_site_reads_worked_out_not_drawn FAILED (page 5 reverted to "Shown on the site plan"); test_f7_columns_chart_and_units ALSO FAILED on the same assertion (builder named only the first — extra coverage). exit 1.
M2 — restored emit to the old measures-only predicate (placement_applied=_placement_applied(...) instead of _placement_drawn(...)): test_s15_one_predicate_decides_placed_corner_vs_single_frontage FAILED — the single-frontage lot's "Where the plan sits on the lot" not-checked line was dropped (AssertionError showed it absent from not_checked). exit 1.
RESTORE — both files restored byte-for-byte from the pinned archive (no MUTATION markers remain; emit line back to _placement_drawn). Re-ran the six round-3 tests (both mutation targets + test_s14_area_illustration_method_three_states + test_s14_placed_on_site_three_states + test_s15_footprint_drawable_needs_a_corner + test_f7): 6 passed, exit 0. Clean.

=== ROUND-2 FINDINGS CLOSED (independently re-derived from the real-preview PDF, not the diff file) ===
Visual F1 — pdftotext -layout page 5 of print-5994e220/report.pdf: "Placed on site  Worked out; not drawn"; "Shown on the site plan" absent. CLOSED.
Visual F2 — page 10: "...it is not yet drawn in this report; when drawn it will be shown as zones inside the placed building footprint." No present-tense "it is shown". CLOSED.
Code finding 1 (ADVISORY, single-frontage self-contradiction) — S15 now routes the page-5 line, the area-allocation fitted flag and the scenario-sheet not-placed sentence through one placed-AND-drawn predicate; the S15 test asserts all three agree on both the corner (placed) and single-frontage (not placed) cases, and my M2 proved the test genuinely pins it. RESOLVED.
Page 9 built at 5994e220 (commit line matches pin); all other pages byte-identical text — the benchmark did not move (report-folder DXF/SVG snapshot tests green corroborate byte-identity).

=== REGISTER / EVIDENCE RESYNC ===
Actual LF sha256 of three_way_document.py at head = cb9695bf9e83f6d4fc75f0fbaabdcfba4ab59f29281730cd73c7fe05788db751; both NB-01 and NB-06 evidence records carry exactly that hash. The register calc test (calc.validate_calculations, which lf_sha256-reads each module off disk) is green, proving the five resynced calc entries' recorded module hashes match the real round-3 code.

=== FINDINGS ===
None REQUIRED.
F1 (ADVISORY) — the page-5 predicate uses geometry.footprint_drawable(plate=1.0) while the fitted flag/sentence read the real-plate floor_plates; their agreement rests on the "footprint depth scales to frontage, independent of plate size" property. Confirmed empirically by the S15 test on the benchmark plate and a single-frontage copy, not proven for all geometries. No action needed for this task.

=== WHAT I COULD NOT CHECK ===
- The whole api pytest at head (heavy; out of my delta scope). Builder reported 10103 passed / 8 skipped / 512s; CI-green at the accept head remains the orchestrator's gate.
- Web vitest and the live preview surface (read-only; ports off-limits).
- Part-A internals (forbidden-to-edit; consumed read-only via the passing S15 reconciliation).

END-OF-REPORT
