# M5-T191 reviews (every return kept unchanged)

- One producer round (backend-engineer, worktree): 2030acd6, integrated as the cherry-pick 9e5a2fe9 on task/wave29-scenario-drawings (8 files, all inside the allowed paths; blobs equal to the builder commit).
- G2 orchestrator self-check at 8e1d5912 (the integrated head with M5-T192 and M5-T194): the whole api suite passed on the increment (10179 passed, 8 skipped; api-suite-B124.log); ruff, research record check and lane coverage PASS.
- G1 data-contract-verifier PASS, G3 code-reviewer PASS, G3 visual-quality-reviewer PASS, G4 qa-engineer PASS, all at the builder commit 2030acd6 (same content). Advisories carried into the wiring part (M5-T173): page 4 and page 5 read one manifest; the caption names the building width; the kit fallback caption must not read as the printed tax map.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

VERDICT: PASS — G1 (data-contract-verifier) for M5-T191, builder commit 2030acd615c5ba0d2a1af7f00f7808b58383a0fa.

I am an AI agent; this is an independent, read-only review, not a human or professional sign-off. Scope held strictly to G1: the footprint ring and its two dimensions traced to the document's geometry and basis; no legal line; never mixed with the printed-tax-map basis. Verified against the builder's commit in the worktree, the extracted tree at /tmp/claude-0/g1-M5-T191/repo, the two builder SVGs in /tmp/claude-0/M5-T191/, and live runs with /root/project/lanes-runtime/venv.

=== VERIFIED (data contract holds) ===

1. Ring provenance = document geometry, GIS/city-map basis. FOOTPRINT_SOURCE = "/geometry/floor_plates/entries/0/outline/0" (placed_footprint.py:61); the ring is the engine's floor-1 plate, which geometry.py:51-86 derives from the drawn GIS frontage/side street lines (depth = plate/frontage), i.e. the city-map (GIS) outline — NOT the printed-tax-map rectangle. It is translated onto the map lot by overlay_offset = subject-outline min(x,y), a pure translation that preserves edge lengths (constraint_overlay.py:287-294; placed_footprint.py:221-222). test_s2_footprint_vertices asserts each map vertex = document vertex + offset within 0.01 ft. The renderer never reads placement.outline (the tax-map 100.76x66.66), so RISK 1 is honored.

2. Exactly two figure-only dimensions, each its own edge length. Width/back = longest edge farthest from the lot boundary; depth = shortest adjacent edge farthest from the boundary (placed_footprint.py:142-157; kit _footprint_edges). Label text = format_feet(edge_length) (placed_footprint.py:243; kit _footprint_dim). Both SVGs print 103.88 ft (width) and 64.66 ft (depth). These equal the INDEPENDENT reference case docs/reference-cases/R6B/cases/placement-building-b.json row gis-conflict-check (GIS Northern Boulevard frontage 103.88; GIS plan depth the plate needs 64.66) — the tests read the expected values from that row, never from a program run (test_placed_footprint.py:51-55; test_site_plan_footprint.py:46-50).

3. No basis-mixing with the printed-tax-map figures. The forbidden tax-map/clearance figures 33.34, 35.31, 35.32, 100.76, 66.66 are ABSENT from both SVGs (grep: 0 each). The close frame carries exactly one basis note: "All dimensions: city map outline, not surveyed." (dimension-basis role, once). The close frame's lot-edge and footprint dims are all GIS (lot 99.98/103.88/101.71; footprint 103.88/64.66) — one consistent basis.

4. C-4 traceability is real and non-vacuous (disconfirming check I ran). label_problems on the true close-frame SVG = [] . Substituting the GIS depth 64.66 with the tax-map 66.66 is caught: "'66.66 ft' does not print 64.658... (edge:/geometry/floor_plates/entries/0/outline/0#1)". So any tax-map figure on the footprint would fail C-4. The edge-source C-4 oracle (context_support.label_problems, :320-321, 357-361) resolves the document ring at the pointer and verifies the printed label equals that edge's length.

5. No legal line. draw_placed_footprint draws only the ring fill (kind illustrative_footprint) + two witness lines, one dimension line and one label per edge (placed_footprint.py:160-200, 236-247). It imports only overlay_offset from constraint_overlay; it draws no yard, setback, street-wall or clearance geometry. A clearance figure (33.34/35.31) is neither an edge length nor drawn.

6. Labels >= 8.5 pt. DIMENSION_MIN_PT = 8.5 (close_frame_dimensions.py:73); kit size = TYPOGRAPHY.dimension_pt + 0.5 = 8.5. SVGs show font-size 8.50 on the footprint dims; tests assert >= 8.5.

7. "No building placed" legend only when nothing is placed. not_placed_legend = (placed_footprint is None) (site_context_plan.py diff). A degenerate, non-None ring (engine placed it but the ring draws nothing) correctly drops the row — test_s4_a_degenerate_footprint_on_the_close_frame_shows_no_no_building_placed passes.

8. Kit report frame no longer calls the plate "Residential". Report-frame legend = {"Lot line","Illustrative building footprint"}; "Residential" absent. The sheet frame keeps the "Residential" use plate (test_s1 kit). Verified in SVG and tests.

9. Invalid ring / unplaceable label draws nothing, never partial (plan-then-commit): validated and tested (S4/S5). My own L-shaped (non-rectangular, untested input) ring control draws correctly with width=70.00 / depth=30.00 — each label equals its own edge length, confirming the two-edge contract holds beyond rectangles.

10. Opt-in: placed_footprint defaults None; S1/S6 maps byte-identity and the kit sheet byte-identity passed in my focused run.

11. The builder's two stated differences are SOUND.
  - Diff #1 (S2 raw-number check replaced by edge-sourced C-4): I confirmed the premise. On the plain close frame maps_support.numbers_not_in_input is already non-empty (flags 99.98, 101.71, 103.88 — these are computed edge LENGTHS, not raw input literals), so S2's literal "numbers_not_in_input passes" could never hold. The footprint adds NO new untraceable number (fp_missing - base_missing == []), and the authoritative C-4 oracle passes and is non-vacuous (item 4). Correct adaptation.
  - Diff #2 (provenance pointer /geometry/floor_plates/entries/0/outline/0): resolves for C-4 in both suites; in the live report part W must thread floor_plates into the doc (W's job, outside my scope).

Focused tests I ran (extracted scratch tree, venv): tests/drawings/maps/test_placed_footprint.py + tests/drawings/kit/test_site_plan_footprint.py => 25 passed in 8.16s.

=== FINDINGS ===

F1 (ADVISORY — pre-existing residual, out of this task's scope; for part W + visual-quality-reviewer). kit_report_footprint.svg caption "Lot outline: Approximate — tax map" sits over GIS-basis figures (lot 103.88/99.98/101.71/2.22; footprint 103.88/64.66). This is the known DB-269 / packet RISK 3 residual (schema const; the adapter and schema are forbidden paths for this task). This task adds only GIS footprint dims that are consistent with the already-present GIS lot dims, so it introduces NO new figure-level basis-mixing — but a reader of the kit fallback still sees city-map (GIS) numbers under a "tax map" caption. Correction belongs to the caption/clearance wiring in part W (my brief lists that as the UNKNOWN W owns), not here. No G1 figure is mixed.

F2 (ADVISORY — visual-quality-reviewer's call). close_frame_footprint.svg legend carries both "Building footprint" (existing buildings, city records layer, pre-existing) and the new "Illustrative building footprint". The "Illustrative" qualifier distinguishes them, but the pair is close in wording. Pre-existing layer naming, not a data-contract defect.

No REQUIRED findings.

=== NOT CHECKED (declared) ===
- Full byte-identity of the kit sheet/summary snapshots and tests/cad DXF (builder reports tests/drawings + tests/cad = 1958 passed; this is the qa-engineer/G4 lane + CI). I ran only the two focused files plus the maps S1/S6 inside them (passed); I did NOT re-run the full heavy suite.
- ruff and modularity_check and the SLOC claims (placed_footprint.py 216<300; site_context_plan.py +9) — code-reviewer lane; not independently recomputed.
- Part W's threading of the plate into the live report and its statement of the 33.34 / 35.31 ft clearances — explicitly W's job and out of scope per my brief.
- Rasterized visual quality (hatch/legibility) — visual-quality-reviewer's lane; I inspected SVG text/structure and the forbidden/expected figures, not a rendered raster.

G1 data-contract verdict: PASS. The footprint ring and its two dimensions trace to the document's floor_plates geometry on the city-map/GIS basis, are figure-only edge lengths matching the independent reference case, carry one city-map basis note, draw no legal line, and are never mixed with the printed-tax-map basis.

END-OF-REPORT

## G3 (code-reviewer)

VERDICT: PASS (G3 code review of M5-T191, commit 2030acd615c5ba0d2a1af7f00f7808b58383a0fa). I am an AI agent; this is not a human or professional review. No REQUIRED defects found. Three ADVISORY notes below.

## Scope checked
One commit, renderer level only (part W wires the live report). Reviewed at the frozen SHA by reading `git show 2030acd6:<path>` in the worktree (HEAD confirmed == 2030acd6, tree clean) and by running tests from an ISOLATED extraction of that commit (see process note). Packet `project-control/tasks/M5-T191.json`, builder return, and producer report `project-control/reports/M5-T191-producer-report.md` all read.

## What I verified (reproducible)

1. Focused tests PASS. From a clean `git archive 2030acd6` extraction, `services/api` cwd, lanes venv, `flock heavy-run.lock pytest -q tests/drawings/maps/test_placed_footprint.py tests/drawings/kit/test_site_plan_footprint.py` -> 25 passed (reproduced twice).

2. Byte-identity regression PASS. `flock heavy-run.lock pytest -q tests/drawings tests/cad` on the clean tree -> 1958 passed, 6 skipped, exit 0 (202.75s) — matches the producer's claim exactly. This confirms S1/S6: maps non-close frames, kit sheet/summary, snapshots and DXF are byte-identical; close-frame and report-frame suites green; style table green.

3. Figures trace to source, not a program run. Ring `geometry.floor_plates.entries[0].outline[0]` of `recorded_215_16_northern_journey.json` is a parallelogram with edge lengths [103.88, 64.66, 103.88, 64.66] ft. These equal `placement-building-b.json` row `gis-conflict-check` (GIS frontage 103.88, GIS plan depth 64.66). The two drawn dims are exactly {103.88 ft, 64.66 ft}. The results pointer `FOOTPRINT_SOURCE=/geometry/floor_plates/entries/0/outline/0` resolves in the real fixture (not a guessed schema).

4. No basis mixing / no tax-map or clearance figures. Direct grep of the builder's benchmark SVG `/tmp/claude-0/M5-T191/close_frame_footprint.svg`: legend "Illustrative building footprint" present; "No building placed" absent (count 0); single basis note "All dimensions: city map outline, not surveyed."; the two footprint dims carried as `data-source="edge:/geometry/floor_plates/entries/0/outline/0#1|#2"`; and zero occurrences of 33.34 / 35.31 / 35.32 / 100.76 / 66.66. RISK 1 honoured: the GIS floor_plates ring (103.88x64.66) is drawn, never `placement.outline` (tax-map 100.76x66.66). Translation is by the existing `overlay_offset` import (constraint_overlay.py not edited), confirmed within 0.01 ft per vertex; never a yard/setback/legal line.

5. Provenance check is sound and stronger. The reported S2 difference (raw `numbers_not_in_input` replaced by the edge-sourced C-4 `label_problems`) is correct: I reproduced that the plain no-footprint close frame already fails the raw check (5 edge-length numbers incl. 99.98/103.88/101.71/BBL), so the literal S2 wording cannot hold on the close frame. `context_support.label_problems` resolves each `edge:<pointer>#<i>` source to the true ring edge length and asserts the label prints it — a per-label provenance check stronger than the global raw scan; it returns [] for the footprint (tests S2/S3). The footprint-dim provenance pointer (the second reported difference) is sound: the label value is the edge length and the source names the ring in the results doc; part W resolves it in the integrated C-4 (W's job).

6. Fail-closed behaviour holds. S4 (7 degenerate states) and S5 (unplaceable label) draw nothing, no exception, never partial; the close frame still drops "No building placed" when a footprint is PASSED but degenerate (engine placed it). Mutation proofs A-D in the report are consistent with the code. Disconfirming inputs the builder did NOT test — a valid triangle (n=3), a clockwise ring, an un-closed ring, and a 1000-vertex ring — all draw correctly with no crash or partial output (checked directly via draw_placed_footprint).

7. Kit report frame no longer "Residential": draws kind `illustrative_footprint` not `plate.use`; test_s3 asserts no "Residential" legend and test_s1 asserts the report frame has `illustrative_footprint` and no `residential` kind while the sheet frame keeps the use plate. The latent `use_kind` hardcode fix (now `for kind in tmp.kinds`) is proven by mutation C.

8. Scope / modularity. All 8 changed files are inside allowed_paths; no forbidden path touched; the 4 kit pins (test_report_frame*.py, test_style_table.py) unchanged. `tools/modularity_check.py --check` -> exit 0 (warnings only). SLOC verified: placed_footprint.py 216 (<300); site_context_plan.py 620 (+9, within the packet +15 cap); kit/site_plan.py 473 (<600 warn). styles.py addition is additive with a unique hatch signature (45,4.0,crossed — no other AREA style matches) and a unique CAD layer A-BLDG-ILLUS; the kind literal `illustrative_footprint` (RISK 2 / B4 manifest contract) is preserved; the held kit caption (RISK 3) is untouched.

## Findings (all ADVISORY, none blocking)

1. ADVISORY — duplicated footprint geometry/dimension logic across stacks. `maps/placed_footprint.py` (`_dimension_edges`, `_draw_edge_dimension`) and `kit/site_plan.py` (`_footprint_edges`, `_footprint_dim`, `_place_footprint_label`, `_halo`) implement the same edge-selection and interior-side dimensioning twice. Justified here (different helper stacks: maps uses context_scene.place + shapely containment; kit uses text_box/_reserve_seg, no containment), so not a defect, but a future shared helper would cut the duplication. No correction required for this task.

2. ADVISORY/observation — kit report-frame footprint is unconditional. `kit/site_plan.py` draws the illustrative footprint on the report frame whenever a floor-1 plate exists, while the live-report page-5 status ("Shown on the site plan" vs "Worked out; not drawn") is gated separately by `drawings_embed.site_plan_draws_placed_footprint()` (part W, forbidden here). This matches the pre-existing page-4-draws / page-5-says-not-drawn state the task is built to fix (business_reason, DB-284/DB-227) and is explicitly W's job (UNKNOWN #4). Flag for part W: ensure page-4 (BOTH the maps close-frame opt-in path and the kit fallback) and the page-5 status agree once wired, so the owner's every-visible-claim standard holds end to end. Not a B1 defect.

3. ADVISORY — `site_context_plan.py` sits above the modularity warn threshold (620 code-lines). The +9 is inside the packet's +15 allowance and the warn pre-exists; no action owed in this task, but the module boundary should be weighed before the next growth.

## What I did NOT check (out of my gate)
- Visual rasterisation/legibility of the SVGs (hatch reads as illustrative, label readability/placement, city-map basis note legibility) — that is the visual-quality-reviewer's gate; the two SVGs exist at `/tmp/claude-0/M5-T191/close_frame_footprint.svg` and `kit_report_footprint.svg`.
- The formal per-requirement D-094 pass (R017/R043/R044/R053/R082/R197/R225/R226/R235) — that is the directive-compliance-verifier's gate; at code level the ones I can map (illustrative-not-use-colour; >= 8.5 pt labels) are satisfied.
- Part W's live-report wiring and the 33.34 / 35.31 ft clearance caption — explicitly W's job (UNKNOWN #4).

## Process note for the orchestrator
My first extraction path `/tmp/claude-0/code-reviewer/repo` was CLOBBERED mid-review by a parallel agent sharing the same role-named scratch path (a foreign `pytest tests/api/test_study_*` for M5-T203 was running from it; the two new test files were overwritten with 35-byte stubs). That produced a spurious "1933 passed" (= 1958 - 25 collected-away new tests). I re-extracted to an isolated session scratchpad dir and reproduced 25 passed and 1958 passed / 6 skipped cleanly. All numbers above are from the clean isolated tree. Heads-up: parallel reviewers using `/tmp/claude-0/<role>/repo` collide — distinct per-session paths are advisable.

END-OF-REPORT

## G3 (visual-quality-reviewer)

VERDICT: PASS (G3 visual review of M5-T191, builder commit 2030acd615c5ba0d2a1af7f00f7808b58383a0fa). I am an AI agent; this is a visual/interaction review, not a human or professional sign-off.

WHAT I DID
Rasterised the builder's two SVGs myself with the main checkout's Playwright chromium (1228) at 1x, 2x and cropped 4x/3x, and looked at them at full size:
- /tmp/claude-0/M5-T191/close_frame_footprint.svg  -> /tmp/claude-0/visual-quality-reviewer/close_{1x,2x}.png, close_fp_zoom.png
- /tmp/claude-0/M5-T191/kit_report_footprint.svg   -> /tmp/claude-0/visual-quality-reviewer/kit_{1x,2x}.png, kit_fp_zoom.png
Read the packet (project-control/tasks/M5-T191.json), the renderer source at 2030acd6, the reference case docs/reference-cases/R6B/cases/placement-building-b.json, and ran a validator probe. Rasteriser script: /tmp/claude-0/visual-quality-reviewer/raster.mjs.

VERIFIED FACTS (the footprint reads as an illustration, dimensions are correct and well placed, nothing reads as a legal line)
1. Close frame: the footprint is a quiet slate wash (#E8EEF2) with a crossed-diagonal hatch and a dashed #5B7083 outline — clearly distinct from the orange subject lot and the grey neighbour footprints. Legend carries "Illustrative building footprint"; the basis note "All dimensions: city map outline, not surveyed." prints exactly once (grep count 1). No "No building placed" row (building is placed) — grep count 0 both SVGs.
2. Exactly two footprint dimensions per frame, both figure-only edge lengths at font-size 8.50 pt, both on the lot-interior side with no overlap with the lot-edge dimensions (which are drawn outside the lot): 103.88 ft (back/width edge, data-source edge:/geometry/floor_plates/entries/0/outline/0#2) and 64.66 ft (depth edge, #1). Both readable in the raster.
3. Those two figures match the INDEPENDENTLY-worked reference case placement-building-b.json row gis-conflict-check (GIS frontage 103.88, GIS plan depth 64.66) on one consistent city-map/GIS basis — not a program run.
4. No forbidden figure in either SVG (grep): 33.34, 35.31, 35.32, 100.76, 66.66 all absent — no tax-map figure, no clearance, no mixed basis on the drawing.
5. Kit report frame: the floor-1 plate is drawn as kind illustrative_footprint, NOT the use colour — "Residential" absent (grep count 0). Legend = "Lot line" + "Illustrative building footprint". Same two labels 103.88/64.66 ft at 8.5 pt. Held caption "Lot outline: Approximate — tax map" kept (RISK 3 / DB-269, a forbidden-path schema const, out of scope here).
6. Nothing looks like a yard/setback/zoning line anywhere; the only dashed-grey line is the neighbour "Existing building (city records)" legend entry.

CODE-LEVEL CONFIRMATIONS (support the visual findings)
7. Provenance: services/api/app/drawings/maps/placed_footprint.py draws only the passed floor-1 ring translated by overlay_offset(subject_outline) (pure translation, import-only), never a yard/setback/legal line; labels sourced edge:/geometry/floor_plates/.../#i. Exactly two edges dimensioned (for i in (back, depth)); labels are edge lengths via format_feet(_edge_len(...)), not raw doc numbers.
8. Withhold-whole is genuine plan-then-commit in BOTH paths (maps draw_placed_footprint and kit _report_footprint): all drawing goes into a temp Sheet and is merged only after both labels place; any invalid branch or unplaceable label returns None -> nothing drawn, never partial.
9. DIMENSION_MIN_PT = 8.5 enforced (close_frame_dimensions raises below it; kit uses dimension_pt + 0.5 = 8.5).
10. Frame gating: placed_footprint drawn on the close frame only; report footprint on the report frame only; all defaults None so every other frame is byte-identical (S1/S6). not_placed_legend = (placed_footprint is None) — correctly drops "No building placed" whenever a footprint is passed, even if a degenerate ring draws nothing (S4).
11. Style addition is additive: one new ShapeStyle("illustrative_footprint", ... "A-BLDG-ILLUS") with a unique kind, CAD layer and AREA signature; test_style_table.py checks invariants (unique kind/layer/AREA signature/CVD distinctness), so the addition does not break it — consistent with the builder's "passes unchanged" claim.
12. Disconfirming probe (validator, no heavy lock): non-finite, >1e9 magnitude, point-not-a-pair, <3, >1000, zero-area-collinear and duplicate-vertex rings are all REJECTED; only a valid ring is ACCEPTED (/tmp/claude-0/visual-quality-reviewer/probe.py). Confirms the "invalid ring draws nothing" gate.

Builder's two reported differences — both SOUND: (a) replacing S2's raw numbers_not_in_input check with the edge-sourced context_support.label_problems==[] plus fp_missing ⊆ base_missing is correct because the footprint figures are edge lengths, not raw document numbers; (b) the footprint-dim provenance pointer /geometry/floor_plates/entries/0/outline/0 is a results-doc source that part W resolves in the integrated C-4.

ADVISORY findings (none blocking; no REQUIRED defects)
A1 (ADVISORY, close_frame_footprint.svg lines 198 & 232): two identical "103.88 ft" labels appear — the lot north-edge dimension and the footprint back-edge width — about 53 px apart. Geometrically honest (the footprint spans the full Northern Boulevard frontage) and disambiguated by position (one above the lot, one inside the blue footprint), but a first-time reader could momentarily wonder why the figure repeats. No change required at this level; worth part W making the caption state the footprint figure as the building width.
A2 (ADVISORY, close_frame_footprint.svg lines 230-232): the footprint width label floats ~24 px inside its own dimension line (collision-avoidance pushed it toward the centroid). Unambiguous and non-overlapping; purely a cosmetic gap.
A3 (ADVISORY, kit site_plan.py _footprint_dim, size = dimension_pt + 0.5): the kit footprint labels render at 8.5 pt while the lot-edge dimensions render at 8.0 pt, so the illustrative (secondary) figures are marginally larger than the primary lot dimensions. This follows the D-094 R053 >=8.5 pt floor, so it is compliant; noting only as a visual-consistency observation.
A4 (ADVISORY): the footprint's north edge is drawn coincident with, and on top of, the lot's Northern Boulevard line; the orange lot line still reads. Honest (0-ft front setback matches the reference case "touches the Northern Boulevard front lot line"). Not a defect.

WHAT I DID NOT CHECK (kept separate)
- I did NOT reproduce the full tests/drawings + tests/cad run (builder: 1958 passed, byte-identical snapshots) or the focused 25-pass run. My focused pytest was queued behind 13 other helpers' heavy runs on the shared flock /root/project/lanes-runtime/heavy-run.lock and never started; I stopped it so it would not run unattended after hand-back. That is the qa-engineer's gate and CI's job at the frozen head. Request: orchestrator/CI confirm the 1958-passed and 25-passed evidence at 2030acd6 before accept. The diff structure supports the byte-identical claim (report=False path unchanged; _report_footprint only called when report; style additive).
- Part W's wiring of the plate into the live report and the 33.34 / 35.31 ft clearance caption (brief point 4 — W's job).
- Independent correctness of overlay_offset itself (M5-T175; import-only / forbidden path here).

Net: for the visual gate, the two renderers produce clear, honestly-labelled illustrative footprints with readable, correctly-placed, correctly-sourced dimensions on a single consistent basis, no legal-line appearance, no forbidden figures, no "Residential", no "No building placed". PASS for G3.
END-OF-REPORT

## G4 (qa-engineer)

VERDICT: PASS

G4 (qa-engineer) review of ledger task M5-T191 (M5-T173 part B1 — page-4 illustrative footprint renderers), builder commit 2030acd615c5ba0d2a1af7f00f7808b58383a0fa, parent/base b9e9d563. I am an AI agent; this is not a human or professional review. Read-only; all runs on a scratch extract under /tmp/claude-0/qa-M5-T191/, never on any repository worktree.

=== WHAT I DID (reproducible) ===
Extracted the commit tree with `git archive 2030acd6 | tar -x` to /tmp/claude-0/qa-M5-T191/repo. Ran the lanes venv (/root/project/lanes-runtime/venv/bin/python, pytest 9.0.3, shapely 2.0.7) from .../repo/services/api with -p no:cacheprovider.

1. Focused: `pytest tests/drawings/maps/test_placed_footprint.py tests/drawings/kit/test_site_plan_footprint.py` -> 25 passed.
2. Regression under the lock: `flock .../heavy-run.lock pytest tests/drawings tests/cad` -> 1958 passed, 6 skipped in 201.9s. Exactly matches the builder's claim.
3. ruff check . -> All checks passed. modularity_check.py --check (throwaway git init in scratch) -> exit 0, failures 0, warnings 33. Matches claim.
4. SLOC via the repo's own counter (modularity_check.source_lines): placed_footprint.py 216 (<300); site_context_plan.py base 611 -> 620 (+9, <=+15); kit/site_plan.py 473. S7 satisfied.
5. Scope: exactly the 8 packet files changed vs base; all in allowed_paths, none in forbidden_paths; close_frame_dimensions.py and constraint_overlay.py (forbidden) only imported, not edited; kit pins test_report_frame*.py / test_style_table.py NOT in the diff (pass unchanged inside the regression run).

=== MUTATIONS REPRODUCED (3 of 4; required >=2) ===
Each applied on the scratch copy, named test rerun, then restored (diff -q clean confirmed):
- B (containment tol): _INSIDE_TOL_FT 0.05 -> 1e9 => test_s4[...vertex_0_06_ft_outside] RED (an outside vertex gets drawn); other 6 degenerate cases still correctly None. Confirms the 0.05 containment check is load-bearing.
- C (kit area kind): kit/site_plan.py:395 "illustrative_footprint" -> plate.use => test_s3, test_s1_sheet, test_s5(kit) RED; the plate reverts to residential yellow #F0E442. Confirms the report frame genuinely draws illustrative_footprint, not the use colour.
- D (withhold): removed `return None` on an unplaceable label => test_s5 RED (the partial fill is merged into the sheet before the crash). Confirms the draw-whole-or-nothing guard is load-bearing.
(A was not rerun; 3/4 already exceed the bar.)

=== DISCONFIRMING / NEW INPUT STATES (none the builder tested) ===
Via draw_placed_footprint on a synthetic 100x100 lot, asserting "drawn whole OR nothing at all" each time — the invariant held in every case, no exception, no partial state:
- vertex EXACTLY on the lot edge (dist 0.0): drawn (covers=True).
- vertex EXACTLY 0.05 ft outside (the stated tolerance boundary): drawn (matches the `<=` in the objective; builder only tested 0.04 and 0.06).
- footprint == the whole lot; footprint flush against the frontage; very narrow (6 ft) sliver lot; sub-foot (1x1) footprint: all drawn, no crash.
- triangle (min 3 verts, unclosed); unclosed rectangle; tuple pairs instead of lists; clockwise winding (negative signed area): all drawn correctly.
- 0.35 ft diagonally outside a corner: not drawn; 0.03 ft diagonal at a corner (within 0.05 straight-line): drawn — tolerance correctly measured as point-to-polygon distance.
- empty list / None / string input: not drawn, no exception, no partial state.

=== VISIBLE OUTPUT (independently rendered + rasterised) ===
Re-rendered the close frame from my scratch copy (render_site_context_plan, frame=close, placed_footprint=benchmark ring): BYTE-IDENTICAL (sha256 437ce3b0...) to the builder's close_frame_footprint.svg — determinism confirmed. Rasterised both SVGs with the review-sandbox Playwright chromium and viewed them full size:
- Close frame: illustrative footprint drawn as a quiet blue crossed-hatch over the lot with a distinct "Illustrative building footprint" legend entry; the two dims "103.88 ft" (back edge) and "64.66 ft" (depth) on the lot-interior side, clear of the lot-edge dims; "All dimensions: city map outline, not surveyed." note printed once; NO "No building placed" row; NO "Residential". No tax-map/clearance figures (33.34/35.31/35.32/100.76/66.66) anywhere in the SVG (grep + per-text check). Nothing reads as a hard/legal line.
- Kit report frame: footprint in illustrative_footprint (blue crossed hatch), legend "Illustrative building footprint" (no "Residential"); same two dims interior-side; the held "Lot outline: Approximate — tax map" caption present (RISK 3 honoured).
The reported planner-vs-packet differences both check out: S2 correctly substitutes the edge-sourced C-4 label_problems==[] + fp_missing⊆base_missing for the raw numbers_not_in_input check (the baseline close-frame edge dims are edge LENGTHS, not raw doc numbers); the footprint dim provenance pointer /geometry/floor_plates/entries/0/outline/0 resolves under the injected _fp_doc and is part W's to thread into the live C-4.

=== FINDINGS ===
No REQUIRED findings.

ADVISORY 1 (test gap) — placed_footprint.py:65 `_MAX_VERTICES = 1000` and test_placed_footprint.py:170 `"over_1000_vertices": [[0.0,0.0]]*1002`. Mutating _MAX_VERTICES to 100000 reddens NO S4 case: the 1002-point ring is all-identical points, so it is rejected by the zero-area / _signed_area check, not by the >1000 upper bound. The upper-bound branch therefore has no distinct regression test. Correction: make the over_1000 case a ring of >1000 DISTINCT vertices with non-zero area (e.g. points sampled around a circle) so it pins the count bound alone. Production code is correct with the bound in place; this is coverage only.

ADVISORY 2 (visual, defer to visual-quality-reviewer) — on both frames the footprint back-edge dimension "103.88 ft" is numerically identical to the lot-frontage dimension "103.88 ft" (the building spans the full GIS frontage), so two identical "103.88 ft" labels appear on one drawing. Both are correct and separately traceable (lot edge vs floor_plates edge); flagging only as a possible reader-clarity point for the visual gate.

ADVISORY 3 (defer to part W / UNKNOWN) — the kit report frame draws the GIS-basis plate (103.88 x 64.66) on a lot whose held caption says "Approximate — tax map". This task does NOT introduce a basis mix: it only changes the plate's render kind and adds the plate's own edge-length labels; the plate-on-lot geometry is unchanged from the pre-existing fallback. Whether the integrated report's caption adequately distinguishes the GIS footprint from the tax-map lot outline is part W's job (how W threads the plate and states clearances is explicitly out of scope for this gate).

=== NOT CHECKED / UNKNOWN ===
- I did not run the full services/api pytest, research_record_check.py, or check_lane_paths.py — those are CI's / the orchestrator's authoritative job at the accepted head; I ran only the focused + tests/drawings + tests/cad surface per the brief.
- Per-directive-requirement authoritative verdict (D-094 R017/R043/R044/R053/R082/R197/R225/R226/R235) is the directive-compliance-verifier's pass; my scenario-level evidence reproduces the key ones (R043/R044 illustrative footprint kind + legend + drop "No building placed"/"Residential"; R053 labels >=8.5 pt; no basis mixing / no tax-map figures).
- How part W wires the plate into the live report and states the 33.34 / 35.31 ft clearances — out of scope (part W), confirmed not drawn here.

Scratch evidence (reproducible, /tmp only): /tmp/claude-0/qa-M5-T191/repo (extract), probe.py, probe2.py, render_close.py, my_close.svg (sha 437ce3b0...), my_close.png, kit_report.png.

END-OF-REPORT
