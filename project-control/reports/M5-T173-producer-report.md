# M5-T173 (builder) producer report — part B wiring

Builder: backend-engineer (fresh, session 2026-10-27a, round r1d). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a24757af5c0154232`.

Base reset to `e016a59d`; cherry-picked B3 round 1 `cece9d3e` (as `3442f68a`) and B3 round 2
`069e2623` (as `728dbc52`); the base-with-B3 head is `728dbc52`.

RESUME NOTE: three earlier builders of this task were stopped by a usage limit before committing.
The second builder's 17-file work was saved as `saved-W-r1b-uncommitted.patch`
(sha256 `b4e34446eed16544f5f6836df7c25d584f4dff41395eb42915c1ecbb5ca6d553`). I verified the sha,
`git apply --check` passed, applied it to the index (one trailing-blank-line whitespace warning,
cosmetic), then VERIFIED it hunk-by-hunk against S1-S8 and the forbidden B3/B4 module signatures,
ran every packet check, drove my OWN live mutation proof, made my OWN before/after prints and
looked at the page images, then committed. Commit 1 (`c382e1eb`, parent `728dbc52`) captured the
verified-green patch to protect it; this commit (2) carries only this rewritten report (all code
and test changes are already in commit 1 — the saved patch covered every owed item; I verified
them and added no further code/test change). Every claim below is from my own evidence on this head.

## What the printed report now shows (the headline)

The report RENDERS every drawing first (`scenario_figures.embed_scenario_drawings` and the page-4
site plan), builds ONE `DrawnManifest` from the rendered `Embedded` values
(`manifest.build_manifest`), and threads `footprint_drawn` into `page_site_context`,
`page_option_comparison`, `page_scenario_sheet` and `illustration_state` into `page_evidence`
BEFORE any page renders. Every shown/drawn/placed/fitted claim reads that manifest — never a data
field. Proven on my own prints (TestClient, `RENDER_GIT_COMMIT` a 40-char value, `print-report-pdf.mjs`):

- Page 4 (site and context): the illustrative building footprint is DRAWN inside the subject lot
  (dimensions 103.88 ft and 64.66 ft); the legend reads "Illustrative building footprint" — the
  "No building placed" legend is GONE; the caption reads "Illustrative building footprint on the
  city map outline (not surveyed; not a design)." then the document's own sentence "…the clearance
  to the back lot line reads 33.34 feet on the tax map and 35.31 feet on the city-map outline, and
  the street frontage differs by about 3.12 feet." — both bases named, neither chosen, averaged or
  hidden. The measured 35.32 ft is NEVER drawn (RISK 2); the forbidden average 34.32/34.33 is absent.
- Page 5 (option comparison): "Placed on site — Shown on the site plan" (a status word, no bar),
  agreeing with page 4.
- Page 6 (scenario sheet): the floor-stack section with the permitted-envelope height lines
  (55/45/30 ft, 3 storeys) captioned "Section (Illustrative): … (Conditional). Horizontal width is
  schematic, not to scale."; the "Why it has this shape" text now takes the FULL content width and
  wraps readably (the one-word-per-line side column is fixed); the two-zone area illustration is
  DRAWN ("60% apartment area") with the caption "…apartment area 12,090 sq ft; other building area
  8,060 sq ft; of 20,150 sq ft residential floor area; footprint on the printed tax map".
- Page 7 (scenario tail): the floor schedule reconciles — 3 storeys × 6,716.67 = 20,150 sq ft
  running total — with the rounding note, the Provisional apartment estimate, and the unresolved
  list, kept together (no block alone on a blank page).

This closes the owner's highest-priority proof (D-094 R317; audit 2026-10-15c sections 3-4/10): the
building is visibly placed on page 4, the two-zone split is drawn on page 6, and the schedule matches.

## Files changed (commit 1 `c382e1eb`; LF sha256 in the RETURN)

Production (`services/api/app/drawings/report/`): `builder.py` (embed-once + one manifest + thread
the drawn state), `page_location.py` (new `placed_footprint` reader of the floor-1 plate, passed to
the CLOSE frame only), `page_site_context.py` (`footprint_drawn` caption: the illustrative line +
the document's `contradicted_record` sentence when drawn, the worked-out-not-drawn line when placed
but not drawn, nothing otherwise), `drawings_embed.py` (DELETED `site_plan_draws_placed_footprint`;
chart reads `footprint_drawn is True`), `page_evidence.py` (DELETED `_area_illustration_drawn`;
clause reads only the manifest state), `layout.py` (the scenario row STACKS so the enlarged 382.5 pt
section and the full-width "Why" text wrap readably; section labels unshrunk).

Tests (`services/api/tests/drawings/report/`): `test_report_scenario_integration.py` (NEW, S1-S8 +
mutations), and the shared pins re-scoped to the drawn state — `test_report_drawn_manifest.py`
(legacy predicate asserted gone), `test_report_comparison.py` / `test_report_appendix.py` (driven
through the manifest, no monkeypatch), `test_report_pages.py` (`test_f7` "Shown on the site plan";
`test_f4`/`test_q1` → "Section (Illustrative)"), `test_constraints_page.py` /
`test_location_sheet.py` (footprint legend replaces "No building placed"), `test_constraint_rows.py`
(the "printed tax map" assertions scoped to the page-4 `data-role="other-basis-dimension"` overlay
labels, which excludes the scenario sheet and footprint-caption prose — carry item 2).

Evidence + e2e: `apps/web/e2e/report-print.flag-on.spec.ts` (asserts the site page draws
`data-role="illustrative-footprint"` and the scenario sheet `data-role="area_zone_apartment"`);
`docs/research/evidence-records/NB-04-lot-dimensions-basis.json` (revision 4, DB-283: code identity
resynced for `close_frame_dimensions.py` 8394b3e6→3950da23, `maps/placed_footprint.py` added
6ffae044, a revision-4 dependency assessment; status unchanged, README/RESEARCH_REQUESTS untouched).

## Scenarios S1-S8 (each with its test)

- S1 drawings off / 1.4.0: `test_report_scenario_integration.py::test_s1_drawings_off_no_drawing_and_every_claim_reads_not_drawn`, `::test_s1_1_4_0_document_makes_no_new_drawn_claim`. Verified on the drawings-off print (no footprint, "Worked out; not drawn", "not yet drawn").
- S2 real print (maps + Lane E): `::test_s2_real_print_page4_footprint_drawn_with_both_bases`, `::test_s2_real_print_page5_shown_page6_sheet_and_appendix`. Verified on `after_maps-page-04/05/06.png`.
- S3 kit fallback: `::test_s3_kit_fallback_draws_the_footprint_and_page5_agrees`; `test_report_pages.py::test_f7`. Verified on `after_kit-page-04.png`.
- S4 degenerate footprint (placed, not drawn): `::test_s4_degenerate_footprint_every_claim_reads_not_drawn` + mutation `::test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn`.
- S5 shared pins: the per-file updates above; benchmark JSON and kit/maps/cad snapshots byte-unchanged (no snapshot in the diff; full tests/drawings tests/cad green).
- S6 budgets: `::test_s6_footprint_caption_adds_a_bounded_number_of_words`; the real print is 11 pages with no block alone on a blank page (checked on the page images); the e2e spec carries the footprint/area-illustration assertions (must pass IN CI — not run here).
- S7 NB-04 revision 4: `research_record_check --check` PASS, NB-04 `code_current True`; an independent G1 delta review is the reviewer's step.
- S8 three print states + H4 T7/T8: `::test_s8_the_footprint_kind_literal_equals_the_kit_style_kind`, `::test_s8_every_printed_claim_matches_the_rendered_footprint_state`, `::test_s8_no_figure_mixes_the_two_bases_and_each_is_named`, `::test_s8_long_commit_and_address_change_no_claim`.

## The seven bound owner rows

- R198 (every "shown on" line names a page that shows it): `test_s2_real_print_page5_shown_page6_sheet_and_appendix`; `after_maps-page-05.png`.
- R200 (zones named only where drawn): `test_s2_...appendix` + `test_s4_degenerate...` (no zones when not drawn); `after_maps-page-06.png`.
- R203 (no visible claim rests on a data field): `test_s8_every_printed_claim_matches_the_rendered_footprint_state` (page-5 status == footprint kind drawn, across four states).
- R204 (a claim keeping `readers.building_not_placed()` states placement, never drawing): `allowance_bar_chart_svg` reads `building_not_placed` for PLACEMENT and the manifest's `footprint_drawn` for DRAWING; `test_report_comparison.py::test_s14_placed_on_site_three_states`.
- R205 (references, legends, statuses, methodology corrected together): one `footprint_drawn`/`illustration_state` threaded in one builder pass to the site legend+caption, the page-5 status, the scenario placement line and the appendix method; `test_s1`/`test_s2`/`test_s4` assert them together.
- R277 (print state with no rendered drawing): `test_s1_drawings_off...`.
- R278 (print state with a rendered drawing): `test_s2_real_print...`, `test_s4_mutation...`.

## Carry items (packet path_notes + w-carry-items.md) — all covered by the saved patch, verified by me

1 B3 integration (cherry-picked, one head) — DONE. 2 constraint_rows re-scope to the overlay labels
(excludes scenario sheets) — DONE; the "no rounding note when the schedule reconciles" positive test
is B3's own `test_scenario_sheet.py::test_r2_no_rounding_note_when_the_schedule_reconciles_exactly`
(cherry-picked), not duplicated. 3 manifest None state (predicate deleted, not-drawn clause) — DONE.
4 `footprint_drawn` threaded to the three pages; B2 height lines confirmed on page 6 ("…(Conditional)")
— DONE. 5 kind literal pinned (`test_s8_the_footprint_kind_literal_equals_the_kit_style_kind`;
`manifest._FOOTPRINT_KIND == maps.placed_footprint.FOOTPRINT_KIND == kit style kind` = "illustrative_footprint")
— DONE. 6 page 4 and page 5 one manifest (close frame AND kit fallback draw it) — DONE
(`after_kit-page-04.png`). 7 every drawing claim reads the manifest; placement vs drawing split — DONE (R204).
8 kit "Approximate — tax map" note vs my city-map caption — DONE (verified on `after_kit-page-04.png`:
the footprint reads as on the city-map outline, the tax-map clearance stated separately). 9 caption
names the footprint figure — DONE (illustrative legend + GIS edge labels). 10 page fit (the stacked
row, full-width "Why" text) — DONE (verified on `after_maps-page-06.png`). 11 B3 round-2 captions on
the real print (schematic label, conditional caption, section labels) — VERIFIED on `after_maps-page-06.png`.
12 NB-04 revision 4 — DONE (record_check PASS). 13 backlog (35.31 vs 35.32 operands) — left untouched.

## Checks (lanes venv `/root/project/lanes-runtime/venv/bin/python`; exit codes and counts)

- `cd services/api && python -m ruff check .` — exit 0, "All checks passed!".
- `flock heavy-run.lock pytest -q tests/drawings tests/cad tests/api/test_report_read_api.py` — exit 0, **2048 passed, 6 skipped** (226.67 s).
- `pytest -q tests/drawings/report/test_report_scenario_integration.py` — exit 0, **12 passed** (28.19 s).
- `python tools/modularity_check.py --check` — exit 0 (pre-existing warnings only; none for the edited report files).
- `python3 tools/research_record_check.py --check` — exit 0, PASS; **NB-04 code_current True**.
- `python3 scripts/lanes/check_lane_paths.py --coverage` — exit 0, 11032 files each owned by one lane.
- apps/web e2e (`report-print.flag-on.spec.ts`) — NOT run here (no browser-driving e2e on this server); must be GREEN IN CI at the exact head. I confirmed via TestClient that the route renders `data-role="illustrative-footprint"` and `data-role="area_zone_apartment"`.

## Mutation proofs (my own, live)

- WIRING: reverting `builder.py:100` `footprint_drawn = drawn_manifest.site_plan_draws_footprint`
  to `footprint_drawn = None` (unwired) fails **7** integration tests —
  `test_s2_real_print_page4_footprint_drawn_with_both_bases`,
  `test_s2_real_print_page5_shown_page6_sheet_and_appendix`,
  `test_s3_kit_fallback_draws_the_footprint_and_page5_agrees`,
  `test_s4_degenerate_footprint_every_claim_reads_not_drawn`,
  `test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn`,
  `test_s8_every_printed_claim_matches_the_rendered_footprint_state`
  (`AssertionError: maps: footprint kind drawn=True but page-5 shown=False`),
  `test_s8_no_figure_mixes_the_two_bases_and_each_is_named`; restored with `git checkout`, status clean.
  (The earlier builder's report claimed 3; my live count is 7 — the wiring is more load-bearing than it stated.)
- Footprint drawn-state: `test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn` (degenerate
  ring → "Worked out; not drawn"; drawable ring → "Shown on the site plan"); `test_report_comparison.py::test_s14` (footprint_drawn False/None vs True moves the status word).
- Area-illustration state: `test_report_appendix.py::test_s14` (Lane E off → "not yet drawn"; on → "it is shown as zones").

## The page-by-page print comparison (my own prints)

Recipe (builder-safe, no ports): TestClient POST `/api/v1/properties/4073340070/report` with
`benchmark_provider(with_zoning_lot=True, street_on=True)` + `recorded_pack_provider(window pack)`,
`RENDER_GIT_COMMIT=a1b2c3d4e5f60718293a4b5c6d7e8f9012345678`, then
`node apps/web/scripts/print-report-pdf.mjs`, `pdftoppm -r 100`.
Scratch: `/tmp/claude-0/-root-project-nyc-buildability/5cb9f851-cfa4-4565-bdd0-8f30581ce977/scratchpad/M5-T173-prints/`.
BEFORE = base-with-B3 `728dbc52`, no patch (extracted via `git archive`, legacy predicate present);
AFTER = my commit. Page counts: BEFORE maps 9 pp; AFTER maps 11 pp, kit_fallback 11 pp, drawings_off 9 pp.
Images I looked at: `after_maps-page-04.png` (footprint drawn, both bases named, no "No building
placed"), `-05.png` ("Shown on the site plan", no bar), `-06.png` (height-line section + "(Conditional)"
+ schematic label; full-width "Why" text; two-zone split 12,090/8,060/20,150), `-07.png` (schedule
reconciles to 20,150, rounding note, estimate, unresolved list together), `after_kit-page-04.png`
(footprint drawn in the kit fallback; "Approximate — tax map" is the pre-existing DB-269 residual).
`pdftotext` of after maps: the literal forbidden averages 34.32/34.33 and the measured 35.32 are
absent (0); the full "…33.34 feet on the tax map and 35.31 feet on the city-map outline…" sentence
present. The BEFORE→AFTER diff is concentrated on pages 4-6 (the footprint, the page-5 status, the
section height lines/area split); the earlier pages reflow as the scenario sheet grew from one to two
pages. No page carries a block alone on a blank page (checked on the images).

## What I did NOT check / limits

- The Playwright e2e spec was NOT run here (no browser-driving e2e on this server); its new assertions
  and the text-size/width checks must be GREEN IN CI at the exact head.
- The NB-04 independent G1 delta review is the reviewer's step; I resynced the code identity and added
  the dependency assessment only.
- The owner's real-preview print is the orchestrator's (I never touched the preview or ports 3000/3001/8000).
  My print passes `address=` as a param, so pages 1-3/8 show "NORTHERN BOULEVARD" casing — a print-recipe
  artifact, not a code change (the real preview uses the recorded address).
- DB-227 corner-area drawing stays undrawn (not established); the 35.31-vs-35.32 operand question (H5
  item 3) is backlog, not this part.
