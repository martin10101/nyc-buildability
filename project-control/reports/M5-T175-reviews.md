# M5-T175 reviews (every return kept unchanged)

- G2 orchestrator self-check: round 1 integrated as f66e8212 (cherry-pick of 826bf88a), rework 1 as c11b4e03 (b8615008), rework 2 as 046c717d (03c989ba); every file inside the packet's allowed paths after the two scope corrections of 2026-10-14; LF sha256 equal to the builder's returns; the rework-2 blob ids equal those of the reviewed builder commit. The orchestrator printed the report from the branch at 11c932b5 through the preview (10 pages; the benchmark pages byte-identical to the print at 97b2a492).
- First reviews, pinned at 11c932b5: G1 data-contract-verifier PASS; G3 code-reviewer PASS with two advisories; G3 visual-quality-reviewer PASS WITH THREE REQUIRED CORRECTIONS on the close frame when a constraint line is drawn (legend clipped; legend named the reused 'Setback line'; the example's line drawn across the street); G4 qa-engineer PASS. The corrections were made in rework 2 under the second scope correction.
- Delta reviews by the SAME four reviewers on the rework-2 builder commit 03c989ba: all PASS; the three required corrections met. Their remaining advisories are backlog DB-263.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier) - part 1

<!-- saved unchanged by save_return.py from agent-abe53f96b638379ca.jsonl, entry 2026-10-14T17:29:46.697Z, sha256 aeb607163449fb7a1087d4bf126fd500d62db1ba5f22020fd98ea1134c539f1f -->
VERDICT: PASS

I am an AI agent (data-contract-verifier), not a human/professional reviewer. Independent, read-only G1 review of M5-T175 at pinned commit 11c932b5d (task/wave24-report-v3), verified in an archive copy under /tmp/claude-0/m5t175-g1. Confirmed `git diff --name-only c11b4e03d 11c932b5d` touches only control/living files, so material work (f66e82129, c11b4e03d) is frozen.

SCENARIOS (G1 coverage)
- S1 (contract side) PASS. My own scan of all 12 valid results fixtures: every 1.4.0/earlier fixture AND the benchmark recorded_215_16_northern_journey.json give `has_results_rows=False`, `rear_yard_combined=None`, `envelope_rows=[]`, no constraint_lines -> page-3 falls back to the 1.4.0 output; the overlay draws nothing. Only synthetic_rear_yard_constraints_contract_1_5_0.json exercises the new path (has_rows=True, combined=Y, env=3, clines=Y). synthetic_placed_building_contract_1_5_0.json is 1.5.0 but carries none of the additive blocks and correctly falls back. The reader keys on block PRESENCE, not contract_version — correct for optional/additive blocks.
- S2 (contract side) PASS. rear_yard.combined way="conditional", zr_sections ["ZR 23-344","ZR 12-10"], no number field; labels.label_for_way maps conditional->"Conditional". Text is a *conditional* no-rear-yard reading, not unconditional.
- S3 PASS. The 23-344(c)(3) check is state=not_known with no inputs (schema's not_known branch forbids inputs); corner_area is not_known with no geometry; the overlay draws neither and no number is carried.
- S4 PASS. My computation: for the fixture only rear_yard_100ft_line (established) is drawn; corner_area (not_known) is skipped. Feeding a not_known AND a not_established line each WITH geometry present: drawn=0, zero SVG parts — the state guard (constraint_overlay.py:161), not missing geometry, rejects them (R017/R044); legend lists only drawn kinds.
- S5 PASS. My computation on the synthetic example: DrawnConstraint.source_points == document vertices exactly (max deviation 0.0 ft, well within 0.01 ft); screen points equal a PURE translation fr.px(vertex + overlay_offset) (deviation 0.0) — no reprojection. The three input_facts render as "100.5 ft, printed tax map" / "9,800 sq ft, city record" / "10,120.5 sq ft, map outline": each its own basis, units named, nothing averaged/merged, gis reads "map outline" never "tax map".
- S7 (contract side) PASS. envelope_rows() reads the top-level 1.5.0 `envelope_rows` array (3 rows: setback/street_wall/side_yard) through the same reader, so M5-T170's later emission needs no further report change.
- S10 PASS. NB-04 is revision 3, last_changed 2026-10-14, research_status still "conflicting_evidence" (conflicts non-empty). The recorded code_identity for close_frame_dimensions.py = 8394b3e605728f14afc1544f8a6d5dec659a9fde0cd4e9c358822e83814529e8 EQUALS my LF sha256 of the file at the pin (computed the way tools/research_record_check.py does: CRLF/CR->LF). `python3 tools/research_record_check.py --check` => PASS, EXIT 0 (NB-04 code_current=True).

FINDINGS

1. ADVISORY (constraint_text.py / scenario engine). The brief asked me to compare the reader against both the schema AND "the engine code that emits these blocks." The scenario engine (services/api/app/scenario/three_answers/*) does NOT yet emit the top-level 1.5.0 blocks (`rear_yard`{checks,combined}, `envelope_rows`, `geometry.constraint_lines`, `input_facts`); they exist only in M5-T164's committed schema + synthetic fixtures. This is by design (M5-T175 is a reader; M5-T170 will emit envelope rows later per S7). Consequence: the reader can only be proven against the schema + committed fixtures today, not against a live engine emission. I validated both 1.5.0 fixtures against packages/contracts/schemas/v1/results.schema.json with jsonschema: both VALID. No correction required; stating the provenance limit explicitly so a later reviewer re-checks the reader once M5-T170 wires real emission.

2. REQUIRED-level check, PASSED (field/enum conformance). Every field the reader expects exists in the schema; none is invented, and no emitted field is ignored in a way that would drop a number:
   - rear_yard_combined -> state{applies,not_applicable,not_known}, way{settled,conditional,withheld}, conditions, text, zr_sections (schema $defs/rear_yard_combined). Match.
   - rear_yard_checks -> provision{23-344(a),(b),(c)(3)}, state, inputs, conditions, text, zr_sections (schema rear_yard_check oneOf). Match; not_known branch carries no inputs/number.
   - envelope_rows/envelope_row -> kind{setback,street_wall,side_yard}, state, values, text, zr_sections. Match.
   - constraint_line (overlay) -> kind{rear_yard_100ft_line,corner_area,street_wall_band,setback_line}, state(established=>geometry; not_established/not_known=>none), basis, zr_sections. Match.
   - input_fact (close frame reads key,value,unit,basis). The quantity_basis enum (law, deed, survey, printed_tax_map, approved_plan, filing_attribute, administrative_record, gis, derived) EQUALS OTHER_BASIS_WORDS keys exactly — all nine covered, none invented, none missing. (Schema also requires source_title/source_date; the drawing label needs neither — not a defect.)
   - way vocabulary is the real vocabulary only: label_for_way handles settled/conditional/withheld and defaults unexpected tokens to "Pending verification"; no invented value. No forbidden result words (optimal/compliant/feasible/preferred/recommended/...) introduced.

3. REQUIRED-level check, PASSED (no contradiction with reference cases / records — item 6). Benchmark (1.4.0) falls back to the REAR_YARD_OPEN_CHECK wording ("not yet checked: ZR 23-344(b) and 23-344(c)(3) have not been applied... draws NO conclusion"); the synthetic 1.5.0 combined is state=applies/way=conditional with named conditions and text "a conditional no-rear-yard reading under ZR 23-344(b), with (c)(3) as an alternative... not a DOB determination." Neither is an UNCONDITIONAL "no rear yard," matching docs/reference-cases/R6B/cases/short-block-rear-yard.json and real-lot.json (which forbid an unconditional no-rear-yard and keep the rear yard conditional/not-known). Lot-dimension bases stay apart (NB-04 double_count_risk honored). No contradiction found.

TESTS RUN (lanes venv, from services/api, -p no:cacheprovider): the two task-owned files tests/drawings/report/test_constraint_rows.py and tests/drawings/maps/test_constraint_overlay.py => 21 passed. tools/research_record_check.py --check => PASS exit 0.

WHAT I CHECKED: the 1.5.0 schema $defs vs constraint_text.py / constraint_overlay.py / close_frame_dimensions.py; jsonschema validation of both committed 1.5.0 fixtures; my own established-only + endpoint-on-vertex (0.01 ft) + fall-back computations on the synthetic example and all fixtures; NB-04 revision/status/code-identity; the four R6B reference cases; the way->label mapping and forbidden-word list.

WHAT I COULD NOT CHECK: (a) live-engine emission of the 1.5.0 blocks (not implemented yet — Finding 1); (b) byte-identical HTML/SVG fall-back (S1 code side) and the full drawings suite — left to the code-reviewer (G3) and qa-engineer (G4) per the brief; I verified only the contract-level fall-back predicate. (c) CI run state — qa-engineer's item 6; I did not query gh.

No REQUIRED defects. PASS.

END-OF-REPORT

## G1 (data-contract-verifier) - part 2

<!-- saved unchanged by save_return.py from agent-abe53f96b638379ca.jsonl, entry 2026-10-14T18:26:36.592Z, sha256 e433f1cb20d3f157ce73c01ba02705d47a22ab12401c00358e5cc2b05a09fb21 -->
VERDICT: PASS

AI agent (data-contract-verifier), read-only. Delta review of M5-T175 rework-2 at pin 03c989bad (archive copy /tmp/claude-0/m5t175-g1-delta). My first-review PASS at 11c932b5d stands; this addendum covers only what rework-2 changed, per the delta brief's G1 checks.

SCOPE CONFIRMATION
`git diff --stat d1a42a8d7 03c989bad` changed styles.py, constraint_overlay.py, site_context_plan.py, drawings_embed.py, page_decision_summary.py, page_site_context.py + 3 test files + the producer report. The reader constraint_text.py and close_frame_dimensions.py are UNCHANGED, so every field/enum/fallback/input-facts conclusion from my first review holds byte-identically. NB-04 json is unchanged.

G1 CHECKS

1. S5 reworded — clip on the lot outline (PASS). My own computation at the rework-2 pin on the committed example (synthetic_rear_yard_constraints_contract_1_5_0.json), rear_yard_100ft_line geometry [[0,100],[182.5,100]], clipped to the lot outline:
   - source_points = [(10.484,100),(105.875,100)]; max x = 105.87, inside the lot (lot max x 122.95) and far short of the document's 182.5 — the line is drawn only within the lot and does not cross the street (S14).
   - Both clipped ends lie ON the lot boundary at distance 0.0 ft (<=0.01); every drawn point is on/inside the lot. 
   - Interior-vertex preservation (my own 3-point line [[-50,50],[60,50],[300,50]], middle vertex strictly inside): clipped source_points = [(10.538,50),(60.0,50),(116.970,50)] — the interior vertex (60,50) is preserved EXACTLY; the ends rest on the outline. Repeated with a non-zero offset (1000,2000) and the lot outline shifted into the mapped frame as the live path does (clip happens in the mapped frame): results-local source_points are byte-identical to the offset-0 case, proving source_points = clipped_mapped - offset returns the document's own vertices (pure translation, no reprojection).
   - A line wholly outside the lot draws nothing: drawn=[], sheet.parts=[], sheet.kinds=[] — no geometry, no legend row.
   So nothing is invented or moved beyond the clip; the clip is shapely's deterministic intersection; where the clip yields several pieces, every piece is drawn and the longest carries the single label (a display choice, not a data change). Areas (polygons) are drawn as given/unclipped; the committed example's only established item is the line, so this is not exercised there — consistent with the contract.

2. New style kinds one-to-one with the schema constraint kinds (PASS). Schema `constraint_line.kind` enum = {corner_area, rear_yard_100ft_line, setback_line, street_wall_band}. `_CONSTRAINT_STYLE` maps each kind to a style of the SAME name; the three new style-table rows (rear_yard_100ft_line, corner_area, street_wall_band) plus the existing setback_line give every kind its own entry, and each style label equals the drawing-label name in CONSTRAINT_LABELS (e.g. style_for("rear_yard_100ft_line").label == "Rear-yard 100 ft line"). One-to-one, full cover, nothing reused — the legend names the drawn kind and never lists "Setback line" when none is drawn (S13 data-contract side). The _AREA_FALLBACK/_LINE_FALLBACK only catch a kind outside the closed enum, which a schema-valid document never carries.

3. Failure note claims nothing (S15, PASS). The note text is "A zoning line could not be drawn on this map; page 3 lists it." It asserts no legal fact, no value, no compliance, no existence/absence of the constraint — only that a line could not be drawn, and points to page 3. It is honest and claims nothing substantive. (The retry robustness in embed_map is G3-code's remit; the note wording is within my lane and is clean.)

4. Earlier PASS items still hold (PASS). Reader field/enum conformance, the conditional (not unconditional) rear-yard reading, the input_facts own-basis labels ("100.5 ft, printed tax map" / "9,800 sq ft, city record" / "10,120.5 sq ft, map outline"; gis reads "map outline", never "tax map"), schema-validity of both 1.5.0 fixtures, and the byte-identical 1.4.0/benchmark fall-back are all carried on unchanged source. S16's data-contract point (a not_known 23-344(c)(3) check prints no number, carries no inputs) matches the schema's not_known branch and is now asserted directly by a test.

5. NB-04 / S10 (PASS, unchanged). At the rework-2 pin research_record_check.py --check = PASS, exit 0; NB-04 status conflicting_evidence, code_current=True (close_frame_dimensions.py unchanged, identity still 8394b3e6...), review_state=stale (expected pre-review).

TESTS RUN (lanes venv, from services/api, -p no:cacheprovider): tests/drawings/report/test_constraint_rows.py + tests/drawings/maps/test_constraint_overlay.py + tests/drawings/kit/test_style_table.py => 51 passed. tools/research_record_check.py --check => exit 0.

WHAT I CHECKED: the rework-2 diff; my own clip/translation/interior-vertex/wholly-outside computations at the pin; the style-kind-to-schema one-to-one mapping; the failure-note wording; NB-04 immutability + record check; schema validity carried from the first review.

WHAT I COULD NOT CHECK (out of G1 lane / deferred): the post-hoc SVG growth (expand_frame_for_overlay) correctness and the retry robustness in embed_map — G3 code; the printed legend-fit and page-1 title-strip rendering — G3 visual; byte-identity of HTML/SVG and the heavy drawings suite — G3 code / G4 qa; CI — none exists for the unpushed commit (G4/orchestrator).

No REQUIRED defects. PASS.

END-OF-REPORT

## G3 (code-reviewer) - part 1

<!-- saved unchanged by save_return.py from agent-a63f5d854f5051f11.jsonl, entry 2026-10-14T17:33:00.384Z, sha256 3193089ddf3a984b33d53910b7bc36230cdb307258140ee435e9c79e4e33a9b0 -->
VERDICT: PASS (two ADVISORY findings; no REQUIRED corrections)

G3 code-reviewer of M5-T175, at pinned commit 11c932b5d. I am an AI agent; this is not a human or professional review. Read-only: I wrote nothing in any repo folder, changed no git state, ran no project_control.py, touched no server/ports. Scratch under /tmp/claude-0/m5t175-g3code|-base|-pin. Material changes isolated to services/api/app/drawings/** + the two test files + NB-04 (material commits f66e82129, c11b4e03d; the rest of 654ea3fad..pin is other tasks' control/web/zr/reference-case commits, confirmed not in the drawings render path).

FINDINGS

1. ADVISORY — overlay failure silently removes the WHOLE site-context map.
services/api/app/drawings/report/drawings_embed.py (embed_map, the `except Exception` at ~line 181-183) catches every error from the map fn and returns Embedded(short_line="This map is not shown here."). constraint_overlay.draw_constraint_overlay raises ConstraintOverlayError BY DESIGN when a label cannot be placed at >=8.5pt (presentation contract section 6, honored). That deliberate "fail rather than shrink" propagates up draw_site_constraints -> draw_block_scene -> draw_site_context_plan -> render_site_context_plan -> embed_map, where it becomes a silent loss of the ENTIRE site plan (base map + dimensions), with no signal that a constraint existed. Evidence (reproduced): I stubbed render_site_context_plan to raise and called embed_map with overlay args -> short_line="This map is not shown here.", is_drawing=False. For 1.4.0 docs the overlay is never invoked, so S1 is unaffected; the risk is latent for real 1.5.0 engine output (M5-T170) on a dense lot. Fail-safe (never a wrong drawing), but opaque. Correction: on a label-placement failure degrade to the base map without the overlay (and/or a short "a constraint could not be labelled" note) rather than dropping the whole map; or the orchestrator/design owner explicitly accepts this surface.

2. ADVISORY — malformed established-line geometry funnels into the same whole-map loss.
constraint_overlay.py (_is_polygon / _translate) assume numeric coordinate pairs; an established line whose geometry is a scalar/non-numeric would raise ValueError/TypeError, caught by the same embed_map blanket except. page_location._overlay_data guards presence/type of the list but not element shape. Schema-validated fixtures render fine, so low severity. Correction: validate element shape or wrap the per-item draw in try/continue so one bad line does not drop the map; or state the reliance on upstream schema validation.

(No REQUIRED findings. The hard-coded page-3 state dict was moved to constraint_text.PAGE3_FALLBACK_STATE/PAGE3_DEFAULT_STATE with one home, pinned by a test — brief check 4 satisfied. All changed function signatures add trailing kwargs defaulting to None; the one cross-scope consumer, maps/block_map.py calling draw_block_scene, is unaffected — confirmed by byte-identical block-map render. page_location._overlay_data reads geometry.constraint_lines/input_facts defensively (isinstance + non-empty) — check 3 satisfied. The overlay uses fr.px, the same projection as the lot outline, and only runs after outlines_match guarantees vertex-for-vertex correspondence, so the pure-translation offset is sound and rotation is handled.)

SCENARIOS (code side)
- S1 (exact fall-back): PASS. Independently rendered build_report_html for all 12 valid results fixtures at claim head 654ea3fad vs pin: every fixture WITHOUT 1.5.0 constraint blocks (10 incl. the benchmark and the 1.5.0-versioned placed_building, which carries no rear_yard/envelope) is byte-identical; only synthetic_rear_yard_constraints_contract_1_5_0.json changes (7964f53c->e000c59a), as intended. The FULL report WITH the benchmark map context is byte-identical base->pin (sha 4a6ccc2e, len 44347), exercising the map-embed/overlay-forwarding path with None args.
- S8 (no new fixture): PASS. `git diff --name-status 654ea3fad 11c932b5d -- packages/contracts/fixtures` is empty; test_s12 builds its not_established line in memory by appending to doc["geometry"].
- S9 (issue anchors resolve): PASS. readers.open_items numbers items 1..n; page_assumptions.py:64 emits id="issue-{number}"; page_site_context._issue_link and page_decision_summary._uncertainty_line emit href="#issue-{number}" from the same numbering (item_number = {cat:number from open_items}; decision_open_items returns the same dicts). test_s9 renders build_report_html and asserts no dangling href.
- S11 (thin hook + modularity): PASS. `modularity_check --check` exit 0 (site_context_plan.py warns only, consistent with DB-250). The site_context_plan.py change is signature threading + one guarded ~12-line call block; the overlay body (236 lines) lives in constraint_overlay.py with cohesive responsibilities.
- S12 (live path): PASS. test_s12 passes and asserts the displaced behaviour (established line drawn, not_established-WITH-geometry rejected by the R017 state guard not by missing geometry, "printed tax map"/"city record" basis labels present, 1.4.0 draws no overlay). Corroborated by my byte-identical full-report render.

WHAT I CHECKED
- ruff check services/api: All checks passed (exit 0), in the pin archive copy.
- The task's own test files ONLY (not the heavy drawings suite — that is the qa-engineer): tests/drawings/report/test_constraint_rows.py + tests/drawings/maps/test_constraint_overlay.py (the close-frame other-basis dimension tests live inside the latter): 21 passed.
- Two reverts via module-level patching in the pin copy: (A) forcing page_site_context's fall-back for the 1.5.0 doc (has_results_rows->False) makes test_s2 fail with AssertionError; unpatched test_s2 passes. (B) reverting the established-only guard (ESTABLISHED="not_established") makes test_s4_a_not_established_line_draws_nothing fail. Tests genuinely catch regressions.
- Read every changed production file diff (constraint_text.py, page_site_context.py, close_frame_dimensions.py, constraint_overlay.py, site_context_plan.py, maps/__init__.py, drawings_embed.py, page_location.py, page_decision_summary.py) and the two test files in full; verified place/format_number imports, label constants (Provisional/Conditional/Pending verification/Unresolved are valid design-contract labels), backward-compatible signatures, and consumers outside allowed paths.

WHAT I COULD NOT CHECK (out of my role / limits)
- The printed-page visual quality (label >=8.5pt at print size, hatching, collisions, white backgrounds, no-line-over-text, page-1 legibility, forbidden words) — visual-quality-reviewer (S2/S5/S6/S12 visual).
- The 1.5.0 schema field/enum/state-way vocabulary conformance of the reader (constraint_text, _envelope_label state handling) against results.schema.json and the emitting engine — data-contract-verifier (G1). _envelope_label defaults any non-not_known, non-conditioned state to Provisional; G1 should confirm the engine's real state vocabulary so an unexpected state is not mislabelled.
- NB-04 revision-3 code identity / research_record_check — G1/G4.
- CI run state at the pin and the full heavy suite (tests/drawings, tests/cad, api) — qa-engineer (G4); I did not rerun CI.
- modularity_check and ruff were run against the worktree/scratch copy at the pin; the authoritative green must be CI at the accepted head.

END-OF-REPORT

## G3 (code-reviewer) - part 2

<!-- saved unchanged by save_return.py from agent-a63f5d854f5051f11.jsonl, entry 2026-10-14T18:30:22.025Z, sha256 bf2a7415fd6cb6356622bf5b20f64aa604a291125430e6e5e89317665de4e30b -->
VERDICT: PASS (two low ADVISORY findings; no REQUIRED corrections). My two first-review advisories are resolved.

G3 code-reviewer delta of M5-T175 at rework-2 pin 03c989bad7004d36b5ae199a8c087c5dd20c5484. I am an AI agent; not a human/professional review. Read-only: wrote nothing in any repo folder, no git state change, no project_control.py, no servers/ports. Scratch under /tmp/claude-0/m5t175-g3code-delta (03c989bad) and -base (654ea3fad). Diff d1a42a8d7..03c989bad is 7 production/test files + the report; all in allowed paths (styles.py and test_style_table.py added this round).

WHAT I VERIFIED (each reproduced in my own copy)

S1 byte-identity re-proved (my own script): rendered build_report_html for all 12 valid results fixtures at 654ea3fad vs 03c989bad. Every non-1.5.0 fixture (10, incl. the benchmark and the 1.5.0-versioned placed_building) is byte-identical; only synthetic_rear_yard_constraints_contract_1_5_0.json changes (now 2f77427f, differs from the first-review pin because of the page-1 strip). Full benchmark report WITH the map context is byte-identical base==rework2 (sha 4a6ccc2e, len 44347) — the new embed_map retry and the expand_frame guard do not disturb the 1.4.0 path.

A. Style table (styles.py): three additive ShapeStyle entries (rear_yard_100ft_line LINE, corner_area/street_wall_band AREA with unique hatches), correct 11-field arity; no existing drawing draws these kinds, so legends (built from drawn kinds) are unchanged — confirmed by the byte-identity above. test_s13 passes and asserts the legend names the drawn rear-yard line and never a reused "Setback line".

B. expand_frame_for_overlay (post-hoc SVG growth): reproduced directly — a fitting SVG is returned byte-identical; an overflowing-furniture SVG grows the viewBox height and both height attributes (count=2) to contain the legend, never shrinks, and moves no element coordinate. It is invoked ONLY when constraint_lines are present (site_context_plan.py `if constraint_lines:`), so every 1.4.0 frame is untouched. It only edits numeric height/viewBox, so it cannot misplace drawing content.

C. Shapely clip (_clip_line_to_polygon): reproduced all degenerate cases on a unit-square lot — line crossing out → clipped to the outline (x=100); wholly outside → [] (draws nothing); collinear with an edge → kept on the boundary; single-vertex touch → [] (dropped, nothing drawable); out-in-out-in → two pieces (MultiLineString handled); interior vertex → preserved exactly. Clipped ends rest on the boundary; the longest piece carries the single label. Areas are intentionally not clipped (per the rework scope). Both S14 tests pass; I mutated the clip to a no-op and both S14 tests fail (one ConstraintOverlayError, one AssertionError), then restored.

D. embed_map retry (addresses my first-review advisories 1 and 2): reproduced three cases — overlay-only failure (base map succeeds without overlay) → map KEPT (is_drawing=True) + note "A zoning line could not be drawn on this map; page 3 lists it."; genuine failure (both attempts raise) → one line "This map is not shown here."; no-overlay failure → unchanged. The retry fires only when overlay args were present and the first call raised, and only produces the note when the base map renders without the overlay — so there is no new silent whole-map loss and non-overlay failures keep today's behaviour. page_site_context._site_outline renders site_plan.notes via short_line; Embedded already has a notes field (default ()), neighbourhood/block embeds never receive overlay args, so they never carry the note.

E. page-1 strip: for the combined text "Rear yard: a conditional no-rear-yard reading…", `text.startswith(row["title"])` strips "Rear yard" then `.lstrip(": ")` → "a conditional…", removing the "Rear yard Rear yard:" stutter; page 3 keeps the full text (separate columns). Only a leading own title is removed.

ruff: All checks passed. Task tests: 51 passed (test_constraint_rows.py + test_constraint_overlay.py + test_style_table.py), incl. S13–S16 and the direct not_known (c)(3) case. modularity --check: exit 0; site_context_plan.py (745 raw lines) is only a WARN — it is not in modularity_baseline.json and is far under JUSTIFY (750 code) / HARD (1000), so no FAIL; this is the pre-existing DB-250 WATCH, not a new regression. (I confirmed baseline non-membership via the tool's own load_baseline.)

FINDINGS (both ADVISORY, low severity — not blocking)

1. ADVISORY — expand_frame_for_overlay is a string-regex SVG rewrite. constraint_overlay.py expand_frame_for_overlay: it depends on the `<svg>` height attribute and the background rect height being the first two `height="{H}"` occurrences (replace count=2) and on a hard-coded _FURNITURE_TOP_PT=400.0 to tell furniture from drawing content. It is robust for the current close-frame SVG and only ever GROWS (worst case: a little extra bottom whitespace, never a clip or misplacement), so correctness is safe. If the close-frame SVG structure changes (another early element carrying the same height string, or a drawing viewport taller than 400 pt), the growth could be wrong. Correction: derive the furniture top from the composition rather than a constant, or target the specific `<svg>`/background elements by a data attribute instead of positional count. Flagging so the design owner and a future SVG change are aware.

2. ADVISORY — page-1 strip uses startswith without a word boundary. page_decision_summary.py _uncertainty_line: `if text.startswith(row["title"])` would also strip a title that is a prefix of a longer first word (e.g. a hypothetical "Rear yardage…"). Harmless for the engine's actual text (title + ": "). Correction: strip only when the title is followed by ":" or whitespace.

WHAT I COULD NOT CHECK
- The live overlay through a REAL map context in my standalone script: the recorded-pack provider hit a subject_lot FileNotFoundError in my extract (a harness/path limitation, not a product defect), so I relied on the passing test harness (test_s12*, test_offset_places_results_geometry_on_the_map_lot) which draws the clipped established line, the other-basis dimensions, and asserts no overlay on the 1.4.0 benchmark.
- The printed-page look of the grown frame, the legend, the clipped line and the failure note — visual-quality-reviewer.
- The 1.5.0 schema/enum conformance and the clipped-vertex provenance (S5 reworded) — data-contract-verifier.
- The heavy drawings/cad/api suite and CI — qa-engineer; and no CI run exists for this unpushed commit (leave to the orchestrator).

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 1

<!-- saved unchanged by save_return.py from agent-a5538f69efe737474.jsonl, entry 2026-10-14T17:34:32.255Z, sha256 1792d097698e38bf81b0b9247cb82dbf01e72218192c3aa59b288a78db19072e -->
VERDICT: PASS with required corrections

I am an AI agent (visual-quality-reviewer), not a human or professional reviewer. Independent G3 visual review of M5-T175 at pin 11c932b5d. I printed the synthetic 1.5.0 report myself (I did not trust the orchestrator's prints or the producer report). READ-ONLY: no repo write, no server, no git/project_control change.

## What I did
- BEFORE vs AFTER benchmark byte-compare: HTML and all 10 page PNGs are byte-IDENTICAL (report.pdf differs only in embedded metadata). Confirms the exact 1.4.0 fall-back: the benchmark's live document carries no 1.5.0 blocks, so no benchmark page changed (intended).
- Built the S12 doc the way tests/drawings/report/test_constraint_rows.py does (synthetic_rear_yard_constraints_contract_1_5_0.json + benchmark window pack, build_report_html(map_context, env=LANE_E)) via my own scratch script, printed it with apps/web/scripts/print-report-pdf.mjs (node_modules symlinked; binds no port), rendered pages at 140-200 dpi. Overlay present in S12, absent in benchmark.

## Findings

1. REQUIRED — Legend clipped on the site close-up (page 4). The overlay adds a "Setback line" legend entry, growing the legend from 3 rows (5 items) to 4 rows (6 items); the last row "No building placed" is clipped by the SVG bottom edge and overlaps the "Sources:" caption (pdftotext reads "No b ilding placed"). In the benchmark (no overlay) the identical legend fits with "No building placed" fully visible. This regresses for ANY 1.5.0 doc that draws a constraint line. Evidence: /tmp/claude-0/m5t175-g3visual/crop-p4-legend-04.png vs crop-bench-legend-04.png. Fix: enlarge the drawing/legend vertical allowance (or wrap the legend) so the full legend fits above the sources caption when the overlay adds an entry.

2. REQUIRED — Legend names the drawn line "Setback line" though the only established line drawn is the rear-yard 100 ft line (page 4). The packet and design contract require "the legend lists only what is drawn"; the legend lists "Setback line" (not drawn) and never names the rear-yard line that IS drawn. constraint_overlay.py deliberately reuses the setback_line style/legend name (comment lines 22-25, CONSTRAINT_LABELS/_LINE_STYLE), putting the real name only on the inline drawing label. A reader scanning the legend sees a setback line that isn't there. Evidence: crop-p4-legend-04.png + crop-p4-overlay-04.png. Fix: name the reused legend entry generically ("Constraint line") or after the drawn kind, so it does not assert a feature that is not present.

3. REQUIRED — Drawn rear-yard line overshoots the lot and fails S5's endpoints-on-vertices (page 4). Fixture rear_yard_100ft_line endpoints are [0,100] and [182.5,100]; the lot_outline vertices are (21.6,0),(23.8,0.5),(122.9,23.1),(101.3,120.7),(0,97.6). Neither endpoint lies on a vertex (nearest, (0,97.61), is 2.4 ft off; x=182.5 is ~77 ft past the lot's right edge, which is ~106 ft at y=100). The line is drawn crossing 215 Place into a neighbouring lot/building — it reads as a rear yard spanning the street. S5 ("endpoints lie on the document's vertices within 0.01 ft") is NOT met for the committed 1.5.0 example. Evidence: crop-p4-overlay-04.png + fixture geometry. Root cause (fixture coordinates vs code that draws geometry as-given) is for G1/G4 to settle; visual fix: emit the line on lot vertices per S5, or have the overlay trim constraint lines to the drawn lot extent so the picture does not cross the street. (White label boxes DO correctly mask the line where it would cross text — no line over a label — that part is fine.)

4. ADVISORY — Page-1 rear-yard uncertainty stutter. The bullet reads "Rear yard Rear yard: a conditional no-rear-yard reading…": the link label "Rear yard" is immediately followed by combined text that itself begins "Rear yard:". On page 1 (inline) it reads as a doubled label (page 3's table avoids it because title and text are separate columns). Evidence: s12-01.png. Fix: on page 1 strip the leading "Rear yard: " from the combined text (or drop the separate link label).

5. ADVISORY — Cross-page lot-dimension inconsistency. Page-4 close-frame (input_facts) shows "9,800 sq ft, city record" and "10,120.5 sq ft, map outline"; page-3 lot-area basis states "recorded lot area of 10,075 sq ft" and "tax-map outline area of 10,387.99 sq ft" — same bases, different figures on adjacent pages, uncross-referenced (page 1 uses 10,075 in the FAR arithmetic). Stems from the synthetic fixture's input_facts differing from its lot_area; a real doc should match. UX-05 cross-output-identity risk. Evidence: s12-03.png vs s12-04.png. Fix: guarantee input_facts lot-area values equal the lot_area used in the calculation (or make the committed fixture self-consistent) so the report never ships two figures for one basis.

6. OBSERVATION (owned by M5-T167, not this task) — Page 1/3 present the rear yard as a Conditional "no-rear-yard reading"; appendix issue-4 still reads "Whether a rear yard is required is not yet checked" (1.4.0 open-check wording). S2's scope correction moves this appendix reconciliation to M5-T167, so it is expected now, but it is a reader-facing gap until M5-T167 lands. Not a defect of M5-T175.

## Positives confirmed
- Exact fall-back: benchmark HTML + 10 PNGs byte-identical; overlay/other-basis absent on 1.4.0.
- S2: page-1 uncertainty and page-3 row show the combined row's OWN text, labelled Conditional, ZR 23-344 linked, no number printed (not the 1.4.0 Unresolved open-check).
- Page-3 rows each show their own state/way/text; Side yard not_known shows text, no number, "Pending verification"; Street wall "Provisional"; coverage 1.4.0 row preserved.
- S5: other-basis dims each labelled with basis ("city record" / "map outline" / "printed tax map") on white backgrounds, nothing merged/averaged.
- S6: overlay label = 8.5 pt exactly (meets floor; design prefers 9.5), no collision; thumbnail draws geometry only (no label), close frame labelled; SVGs embed 1:1 (width/height pt == viewBox).
- Forbidden result words: only "Verified" in the page-6 status-key definition (not applied to a result) — acceptable.
- All internal #issue-n links resolve; the 1.5.0 combined sentence prints exactly twice (p1, p3), not in the appendix. Page-2 locator unaffected.

## Scenario lines (my coverage)
- S2 (visual): PASS — Conditional reading, ZR 23-344 linked, no number on p1 and p3 (ADVISORY #4 stutter on p1).
- S5 (visual): FAIL on endpoints-on-vertices for the committed example (REQUIRED #3); other-basis-dimension labelling PASS.
- S6: PASS at the 8.5 pt floor, no collision; could NOT visually verify a hatched AREA overlay (see below).
- S12 (visual): PASS on established-only drawing and byte-identical 1.4.0 fall-back; close-up carries REQUIRED #1/#2/#3.

## What I could not check
- A hatched AREA overlay (S6 "distinguishable by hatching"): the S12 fixture's only established line is a LINE; its area kind (corner_area) is not_known, so no established hatched area was drawn — relies on unit tests (G3 code / G4).
- Benchmark property has no live constraint lines (confirmed via byte-identity); 1.5.0 behaviour only via the synthetic example I built.
- CI state (G4's role); geometry/data root cause of #3 (G1/G4).

## Scratch artifacts (pictures I made)
/tmp/claude-0/m5t175-g3visual/s12-report.pdf and s12-01.png … s12-10.png (140 dpi); crop-p4-legend-04.png, crop-p4-overlay-04.png, crop-p4-otherbasis-04.png, crop-bench-legend-04.png (200 dpi); s12-report.html, bench-report.html; build_s12.py.

END-OF-REPORT

## G3 (visual-quality-reviewer) - part 2

<!-- saved unchanged by save_return.py from agent-a5538f69efe737474.jsonl, entry 2026-10-14T18:27:49.427Z, sha256 991b7861bfb8fb02b25763217fab2e34ca7cc7365b5eafcc8c7a988944b5b04d -->
VERDICT: PASS

Delta G3 visual review of M5-T175 rework 2 at pin 03c989bad. I am an AI agent (visual-quality-reviewer), not a human/professional reviewer. READ-ONLY: no repo write, no server, no ports, no git/project_control change. I rebuilt the S12 document at the new pin with my own build_s12 script (synthetic_rear_yard 1.5.0 + benchmark window pack, build_report_html(map_context, env=LANE_E)), printed it with apps/web/scripts/print-report-pdf.mjs (binds no port), and rendered pages 1, 3 and the close frame.

## My three required corrections — all resolved
1. REQUIRED #1 (legend clipped) — RESOLVED. The close frame now grows to fit the overlay legend; all legend rows are fully visible with clear space above the "Sources:" caption. "No building placed" is no longer clipped/overlapping. Matches S13. Evidence: /tmp/claude-0/m5t175-g3visual-delta/crop-legend-04.png (vs review-1 crop-p4-legend showing the clip).

2. REQUIRED #2 (legend named the drawn line "Setback line") — RESOLVED. The legend now names "Rear-yard 100 ft line" with its own green dashed swatch; "Setback line" no longer appears anywhere (0 occurrences in the HTML; the drawn kind is named in both legend and drawing label). Matches S13. Evidence: crop-legend-04.png, crop-lot-04.png.

3. REQUIRED #3 (line crossed the street) — RESOLVED. The rear-yard line is clipped to the lot outline (shapely); the overlay path is now a short green (#009E73) dashed segment inside the lot, and NO line crosses 215 Place on either the close frame or the page-1 thumbnail (the previous orange line into the neighbour is gone). Matches S14/reworded S5. Evidence: s12-04.png, crop-lot-04.png, crop-line-04.png; the page-1 thumbnail in s12-01.png.

## My page-1 advisory — resolved
4. ADVISORY #4 (page-1 "Rear yard Rear yard:" stutter) — RESOLVED. The bullet now reads "Rear yard a conditional no-rear-yard reading under ZR 23-344(b)…" — the leading title is stripped; "Rear yard Rear yard" no longer appears; still labelled Conditional, ZR 23-344/12-10 linked, no number. Matches S16. Evidence: s12-01.png.

## New finding (minor)
5. ADVISORY — The clipped green rear-yard line, now short and coincident with its own label anchor, is largely occluded by its white label background box, so the drawn line itself is barely visible on the close frame (the label "Rear-yard 100 ft line, established, ZR 23-344" and the legend swatch still convey it). Evidence: crop-line-04.png. Optional polish: offset the label a few points off the line so a segment of the green dashes stays visible, confirming to the reader a line is actually drawn. Not blocking — the constraint is clearly communicated by the label + legend.

## Carryover from review 1 (NOT in rework-2 scope; still advisory/observation)
6. ADVISORY — Cross-page lot-dimension inconsistency persists: page-4 close-frame input_facts show "9,800 sq ft, city record" / "10,120.5 sq ft, map outline" while page-3 lot-area basis states "recorded lot area 10,075 sq ft" / "tax-map outline 10,387.99 sq ft" — same bases, different figures on adjacent pages. This stems from the synthetic fixture's input_facts differing from its lot_area; it is not a defect introduced by this task and was not in rework-2 scope. Recommend the engine guarantee input_facts lot-area values equal the lot_area used in calculations (or make the committed fixture self-consistent). Evidence: s12-03.png vs s12-04.png.
7. OBSERVATION — Front pages present the rear yard as a Conditional reading while appendix issue-4 still reads "not yet checked" (1.4.0 open-check wording). Per S2's scope split this reconciliation is owned by M5-T167; expected in this task's state.

## Other confirmations
- Benchmark unchanged: my bench-report.html is byte-identical between the review-1 pin (11c932b5d) and the rework-2 pin (03c989bad) (md5 187d57b2…), confirming rework 2 does not touch the no-constraint-line fall-back; combined with review 1's BEFORE==AFTER benchmark page byte-identity, the benchmark pages remain unchanged.
- Overlay structure intact: 2 overlay roles (page-1 thumbnail geometry-only + close frame), 1 label at 8.5 pt, no collision; SVGs embed 1:1.
- Forbidden result words: none (only "Verified" ×1 in the page-6 status-key definition, not applied to a result).
- Combined rear-yard sentence prints exactly twice (p1, p3), not in the appendix; all internal #issue-n links resolve.

## What I could not check
- The S15 overlay-failure note: the S12 overlay draws successfully, so the note is absent here; I did not construct a failing overlay to render it (optional per the brief; covered by G3 code / G4).
- Geometry/data correctness of the clip to 0.01 ft and the new style-kind-to-schema mapping (G1/G4's determination); I verified the visual result only.
- CI: no CI run exists for the builder's commit yet (not pushed) — leaving CI to the orchestrator.

## New scratch pictures
/tmp/claude-0/m5t175-g3visual-delta/s12-report.pdf and s12-01.png … s12-10.png (140 dpi); crop-lot-04.png, crop-line-04.png, crop-topstrip-04.png (close-frame zooms); crop-legend-04.png (legend band, 200 dpi); s12-report.html, bench-report.html, build_s12_delta.py.

END-OF-REPORT

## G4 (qa-engineer) - part 1

<!-- saved unchanged by save_return.py from agent-ac0fada2386e93265.jsonl, entry 2026-10-14T17:31:35.256Z, sha256 3af4ab6adac0f52c91f419137357f47f22867467f295063c7e16bc7099cbec2c -->
VERDICT: PASS

I am an AI agent (qa-engineer), the independent G4 reviewer of M5-T175. READ-ONLY: I wrote nothing in any repo, ran no project_control.py beyond none needed, started no server, touched no ports, and did every mutation only in my scratch copy under /tmp/claude-0/m5t175-g4/. Pin 11c932b5d on task/wave24-report-v3; claim head 654ea3fad. Material commits f66e82129 + c11b4e03d; `git diff --name-only c11b4e03d 11c932b5d` = control/living files only (confirmed). The zr-snapshots and reference_cases step_p8 changes in 654..pin are NOT in either material commit — they are base, not this task.

COMMANDS (archive copy of the pin; lanes venv py3.12.3; PYTHONDONTWRITEBYTECODE=1; -p no:cacheprovider; from services/api unless noted):
- `python -m ruff check .` -> exit 0, "All checks passed!"
- Heavy run `pytest -q tests/drawings tests/cad tests/api/test_report_read_api.py tests/api/test_report_read_context.py` -> exit 0, 1819 passed, 6 skipped, 1 warning in 182.72s (I am the only reviewer who ran this; matches the rework-1 claim).
- Task files alone (test_constraint_rows.py + test_constraint_overlay.py) -> exit 0, 21 passed (12 report + 9 overlay).
- `tools/research_record_check.py --check` -> exit 0, PASS; NB-04 status=conflicting_evidence code_current=True review_state=stale.
- `tools/modularity_check.py --check` (git-init'd scratch copy so `git ls-files` resolves) -> exit 0, selected 799 files, failures 0, warnings 33; site_context_plan.py carries the expected review_signal warning only, no failure.
- `scripts/lanes/check_lane_paths.py --coverage` -> exit 0, "LANE COVERAGE PASS: 10364 file(s)".

SCENARIO TABLE (file::test; asserts the 'then'?):
- S1  test_constraint_rows::test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged + test_s1_a_..._falls_back + test_s12_1_4_0_report_with_maps_draws_no_overlay + test_s1_benchmark_page_one_...unchanged; plus my byte-identity script. YES (pins exact 4 fall-back rows + page-1 + overlay-absent; full fixture-wide identity proven by my script).
- S2  test_s2_conditional_rear_yard_shows_combined_text_labelled_conditional (page-3) + test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard (page-1). YES (combined text, "23-344(b)", Conditional chip, ZR 23-344 href, no ft/sq-ft number).
- S3  test_s3_not_known_envelope_row_shows_text_no_number (side_yard not_known: no "values", own text, no number, Pending verification) + test_s4_only_established_lines_are_drawn (corner_area not_known line draws nothing). YES, with one note (see Finding 1).
- S4  test_s4_only_established_lines_are_drawn + test_s4_a_not_established_line_draws_nothing (drawn==[], sheet.parts==[], kinds==[]). YES.
- S5  test_s5_drawn_endpoints_lie_on_the_document_vertices (<=0.01 ft vs document vertices AND vs fr.px(vertex+offset)) + test_s5_each_input_fact_names_its_own_basis_nothing_merged (exactly one basis word/label; gis="map outline" not "tax map") + test_s5_other_basis_dimensions_draw_beside_the_outline. YES.
- S6  test_s6_labels_are_at_least_8_5_pt_with_no_collisions (font-size>=8.5, box overlap check) + test_s6_an_established_area_is_distinguishable_by_its_hatch + test_s6_a_label_that_cannot_be_placed_fails_rather_than_shrinks. YES at the SVG/geometry level (true print legibility is the visual reviewer's call).
- S7  test_s7_envelope_rows_render_through_the_same_reader (setback+street_wall text present; Conditional/Provisional chips). YES.
- S8  no pytest; `git diff --name-status 654..pin -- packages/contracts/fixtures` = EMPTY -> no new results fixture. YES.
- S9  test_s9_every_issue_href_resolves_to_an_anchor (every href="#X" has id="X"; issue_links non-empty) + test_s9_page_three_rear_yard_links_its_numbered_open_item. YES.
- S10 no pytest; research_record_check exit 0; NB-04 rev 3 records close_frame_dimensions.py LF-sha256 8394b3e6...29e8 which EQUALS the file at the pin (I recomputed `git show 11c932b5d:...|tr -d '\r'|sha256sum`), research_status unchanged. YES.
- S11 no pytest; modularity_check exit 0; site_context_plan.py within material-growth limit (warning, not failure); overlay body in constraint_overlay.py (236 lines). YES.
- S12 test_s12_live_report_draws_only_established_lines_and_other_basis_dimensions (data-role="constraint-overlay", data-kind="rear_yard_100ft_line", label once; setback_line/corner_area absent; "printed tax map"+"city record" present) + test_s12_1_4_0_report_with_maps_draws_no_overlay + test_s12_page_one_... + test_offset_places_results_geometry_on_the_map_lot. YES.

MY OWN MUTATIONS (scratch copy; applied, named test FAILED, restored to byte-identical backup — sha256 match confirmed on all 4 files):
1. constraint_overlay.py: defeated the `state != ESTABLISHED` guard -> test_s4_a_not_established_line_draws_nothing FAILED (exit 1). (S4)
2. close_frame_dimensions.py other_basis_label: appended " / city record" to every label -> test_s5_each_input_fact_names_its_own_basis_nothing_merged FAILED (names 2 bases). (S5)
3. page_site_context.py: broke the `#issue-{number}` anchor target -> both test_s9_* FAILED (dangling link). (S9)
4. page_decision_summary.py: forced `combined = None` -> test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard FAILED (page-1 reverted to "Rear yard ZR 23-344 Unresolved"). (S12)
All four scenarios therefore have a test that fails when the behaviour is reverted.

S1 BYTE-IDENTITY (my own script, not the producer's): rendered report HTML for all 12 valid results fixtures, the benchmark-with-maps, and 5 site_context_plan SVGs (close/summary_close/report/summary/wide) at the claim head 654ea3fad and at the pin, LF-normalized sha256. `diff` = EXACTLY ONE line differs: report::synthetic_rear_yard_constraints_contract_1_5_0.json. All 11 other reports (incl. placed_building 1.5.0, which correctly falls back), the benchmark-with-maps, and all 5 SVGs are byte-identical. S1 holds and the change is isolated to the one fixture carrying the 1.5.0 blocks (intended).

CI AT THE PIN: run 38605637322 (headSha 11c932b5d) = completed/success; all 21 jobs success, incl. api (ruff+pytest), web (lint+typecheck+build), web-e2e (vitest+Playwright), modularity, contracts, control-plane. secret-scan and context-budget at the pin also success. A later commit f2c8d4516 (after the pin) has CI in_progress — out of scope; I did not rerun anything.

FINDINGS:
1. ADVISORY — S3 coverage is by proxy, not literal. The scenario names "23-344(c)(3) / corner_area" as the not_known instance. test_s3 asserts the not_known rule on the side_yard ENVELOPE row (no values, no number), and corner_area's draws-nothing is asserted in test_s4/test_s12 — both valid not_known instances — but there is no direct assertion that a not_known rear_yard CHECK (23-344(c)(3)) row prints no number. The behaviour is reader-shared with the asserted rows, so risk is low. Correction (optional): add one assertion over rear_yard.checks for the 23-344(c)(3) not_known entry.
2. ADVISORY — S6 is proven at the SVG/geometry level only (font-size>=8.5, box-overlap, hatch style, fail-rather-than-shrink). True print legibility/collision at page size is the visual-quality-reviewer's render check, which I did not perform.

WHAT I COULD NOT CHECK: live preview/browser rendering and on-page visual quality at print size (no server, thin client — the visual-quality-reviewer's and H2's domain); the AFTER print PDF (I verified behaviour via tests and my own renders, not the PDF); primary legal sources / professional-legal correctness (I am an AI agent; out of scope — ADR-007 label applies). The reference_cases/zr-snapshot base changes present in 654..pin are not this task's material and I did not audit them beyond confirming the heavy suite passes with them.

Net: every acceptance scenario has a test (or tooling check for S8/S10/S11) that asserts its 'then'; 4 independent mutations prove the behaviour is real; the 1.4.0 fall-back is byte-identical fixture-wide by my own script; NB-04 rev-3 code identity matches the pinned file; all local checks and the pinned CI run are green. No REQUIRED defect found.

END-OF-REPORT

## G4 (qa-engineer) - part 2

<!-- saved unchanged by save_return.py from agent-ac0fada2386e93265.jsonl, entry 2026-10-14T18:27:42.743Z, sha256 2f977b6434e1f1621a92c349366ba1169ced27d3bcbd9a507db77c53a5f7e962 -->
VERDICT: PASS

I am an AI agent (qa-engineer), delta G4 reviewer of M5-T175 rework 2 at pin 03c989bad (parent d1a42a8d7; claim head 654ea3fad). READ-ONLY: no repo write, no git/ledger/gh-write, no server, no ports, no Playwright. All mutations were in a separate scratch archive copy; the heavy suite ran against its own copy so mutations never touched it. `pgrep -af pytest` showed no other heavy run before I started.

COMMANDS (lanes venv py3.12.3; PYTHONDONTWRITEBYTECODE=1; -p no:cacheprovider; from services/api unless noted; direct exit codes):
- `ruff check .` -> 0, "All checks passed!"
- Heavy run `pytest tests/drawings tests/cad tests/api/test_report_read_api.py tests/api/test_report_read_context.py` -> 0: 1828 passed, 6 skipped in 186.83s (I am the only reviewer who ran it; matches the builder's claim; +9 over the first pin's 1819).
- Three task files (test_constraint_rows + test_constraint_overlay + test_style_table) -> 0: 51 passed.
- `tools/research_record_check.py --check` -> 0 PASS (NB-04 unchanged this round, code_current=True).
- `tools/modularity_check.py --check` (git-init'd scratch) -> 0: failures 0, warnings 33 (site_context_plan.py review_signal only).
- `scripts/lanes/check_lane_paths.py --coverage` -> 0: LANE COVERAGE PASS.

SCENARIO TABLE (file::test; asserts the 'then'?):
- S5 (reworded) test_s5_drawn_endpoints_lie_on_the_document_vertices + test_s14_established_line_is_drawn_only_inside_the_lot (clipped ends on lot boundary <=0.01 ft; shapely distance check) + test_s14_a_line_wholly_outside_the_lot_draws_nothing + test_s5_each_input_fact_names_its_own_basis + test_s5_other_basis_dimensions_draw_beside_the_outline. YES.
- S13 test_constraint_kinds_have_their_own_legend_entries (4 distinct names; rear_yard_100ft_line label, geometry LINE/AREA mapping) + test_s13_legend_names_the_drawn_rear_yard_line_never_setback (">Rear-yard 100 ft line</text>" present, ">Setback line</text>" absent) + test_s13_overlay_legend_fits_and_the_plain_frame_is_unchanged (over_h>plain_h, "No building placed" y+2 <= height, plain_h==470.0). YES (fit proven as "within grown viewBox height"; see Finding 1).
- S14 test_s14_established_line_is_drawn_only_inside_the_lot (max x<130, every point on/inside lot, bare line reaches >=182) + test_s14_a_line_wholly_outside_the_lot_draws_nothing (drawn==[], parts/kinds empty). YES.
- S15 test_s15_overlay_failure_keeps_the_map_with_a_note (both failure kinds via monkeypatch: is_drawing True + exact note) + test_s15_report_keeps_the_site_map_when_overlay_geometry_is_malformed (end-to-end: note present, base map drawn, overlay absent). YES.
- S16 test_s16_page_one_rear_yard_uncertainty_does_not_repeat_its_title ("Rear yard Rear yard" absent; body present) + test_s16_not_known_rear_yard_check_prints_no_number (c3 23-344(c)(3) state not_known, no inputs, has text, no ft/sq-ft). YES.
- S1-S12 still pass: all green in the 1828-pass heavy run; S12 live test updated to count "Rear-yard 100 ft line" twice (drawing label + its own legend entry) and assert ">Setback line</text>" absent; S1 fall-back re-proven below.

MY OWN MUTATIONS on NEW behaviour (separate scratch copy; named test FAILED; restored, sha256 match confirmed):
1. Defeated the line clip (`pieces` always the full mapped line) -> test_s14_established_line_is_drawn_only_inside_the_lot FAILED (line reached x182.5 across the lot). (S5/S14)
2. Defeated the embed_map retry (overlay failure returns _MAP_UNAVAILABLE) -> both test_s15_* FAILED (map dropped, note absent). (S15)
3. Reverted the rear-yard line to reuse the "setback_line" style -> test_s13_legend_names_...never_setback and test_s12_live_report FAILED (legend showed "Setback line"). (S13)

S1 BYTE-IDENTITY (my own s1_render.py; claim head 654ea3fad vs delta pin 03c989bad; LF-normalized sha256 of 12 fixture reports + benchmark-with-maps + 5 site_context_plan SVGs): `diff` = EXACTLY ONE line differs — report::synthetic_rear_yard_constraints_contract_1_5_0.json (intended). All 11 other reports (incl. placed_building 1.5.0), the benchmark-with-maps, and all 5 plain SVGs are byte-identical, confirming a frame without the overlay is unchanged (S13's byte-identity clause and S1).

CI NOTE: no CI run exists for the builder's commit 03c989bad — it is not pushed (gh run list shows runs only for the branch head's other shas, never 03c989ba). CI is left to the orchestrator to capture after integration.

FINDINGS:
1. ADVISORY — S13's "fits above the sources caption" is proven as "fits within the grown viewBox height" (`No building placed` row y+2 <= over_h) plus plain_h==470.0, not by asserting the row sits above the specific "Sources:" caption text position. The grow-only `expand_frame_for_overlay` logic (needed<=height -> byte-identical) and the visual reviewer's print crops cover the remaining gap; low risk. Optional: assert the legend's bottom row y < the sources-caption y.
2. ADVISORY — S15 end-to-end test forces the overlay failure via a malformed geometry; the "a label that cannot be placed" kind and the genuine-map-failure-still-unavailable path are covered only at embed_map via monkeypatch, not end-to-end. The inner try/except handles the genuine-failure path and mutation 2 proves the note is real; acceptable.

WHAT I COULD NOT CHECK: live preview/browser rendering and true print layout/legibility at page size (thin client; the visual-quality-reviewer's and H2's domain — I did not render the PDF this round); shapely clip behaviour for areas (areas are drawn unclipped by design — correct per the brief; only the example's line is established); professional/legal correctness (out of scope — ADR-007 label applies); the synthetic fixture's own recorded inconsistencies (line past its outline; input_facts != lot_area) are backlogged to M5-T167 per the scope correction and are not this task's defects.

Net: the three visual-required corrections (S13 legend naming, S13 fit, S14/S5 clip) and the two advisory-driven additions (S15 retry note, S16 title-strip + direct (c)(3) test) are implemented and each has a test that fails when reverted; the 1.4.0 fall-back is byte-identical fixture-wide by my own script; all local checks are green and the heavy suite is 1828 passed. No REQUIRED defect found.

END-OF-REPORT
