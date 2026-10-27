# M5-T173 (builder) producer report — part B wiring

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-aee7bc5bd62c24359`.
Base reset to `e016a59d`; cherry-picked B3 round 1 `cece9d3e` (as `24892a71`) and B3 round 2
`069e2623` (as `ad5fd02c`); the wiring commit sits on top.

RESUME NOTE (session 2026-10-15c, 2026-10-17): a previous builder was stopped by a usage limit
BEFORE it committed; its 17-file work was saved as `w-saved-uncommitted.patch`
(sha256 `a14ec557695b7f98...`). This resuming builder applied that patch to the index, VERIFIED it
hunk-by-hunk against S1-S8 (production diffs match the forbidden B3/B4 module signatures; the
re-scoped pins follow the drawn state, not weakened), ran the full check suite, drove a live
mutation proof, produced the real prints and looked at the page images, then committed. The
sections below are the saved report with the final counts and evidence paths filled in.

## What the printed report now shows (the headline)

The report RENDERS every drawing first, builds ONE `DrawnManifest` from the rendered `Embedded`
values, and every shown/drawn/placed/fitted claim on pages 4, 5, 6 and the appendix reads that
manifest — never a data field. Proven by the BEFORE (`e016a59d`, unwired) vs AFTER (my wiring)
render of the real print (maps + Lane E), text-extracted from the two report HTMLs:

| claim | BEFORE e016a59d | AFTER (wiring) |
|---|---|---|
| footprint kind `illustrative_footprint` drawn | no | yes |
| page-4 "No building placed" legend | present | gone |
| page-4 "Illustrative building footprint on the city map outline" caption | absent | present |
| page-4 clearance sentence carrying 33.34 ft (tax) and 35.31 ft (city) | absent | present |
| page-5 placed-on-site status | "Worked out; not drawn" | "Shown on the site plan" |

This closes the owner's highest-priority defect (audit 2026-10-15, D-094 R196–R206): a drawn claim
now follows actual rendered content, not a hard-coded constant.

## Files changed (LF sha256 filled at the commit; see RETURN)

Production (`services/api/app/drawings/report/`):
- `builder.py` — embeds the scenario drawings once (`scenario_figures.embed_scenario_drawings`) and
  the site plan, builds ONE `manifest.build_manifest(...)` BEFORE any page renders, and threads
  `footprint_drawn` into `page_site_context`, `page_option_comparison`, `page_scenario_sheet` and
  `illustration_state` into `page_evidence`; passes the embedded drawings to the scenario sheet.
- `page_location.py` — new `placed_footprint(results)` reader of the floor-1 entry of
  `geometry.floor_plates` (available + a non-empty floor-1 outline ring; `None` for 1.4.0 / not
  available / malformed), passed as `placed_footprint=` to the CLOSE frame embed ONLY.
- `page_site_context.py` — `render(..., footprint_drawn=None)`; under the page-4 drawing it adds the
  "Illustrative building footprint on the city map outline (not surveyed; not a design)." line and
  the document's own `contradicted_record` clearance sentence (`_placement_conflict_sentence`, read
  verbatim, both bases named, neither chosen) when drawn; the worked-out-but-not-drawn line when the
  engine placed it but the drawn map did not draw it; nothing otherwise (gated on
  `site_plan.is_drawing` so drawings-off adds no words).
- `drawings_embed.py` — DELETED the legacy `site_plan_draws_placed_footprint()` predicate; the chart
  reads `footprint_drawn is True` (False/None = not drawn, byte-identical for an unwired caller).
- `page_evidence.py` — DELETED the legacy `_area_illustration_drawn()` predicate; the drawing clause
  reads ONLY the manifest state (`None`/other not-drawn state → "not yet drawn"; zones/bar named).
- `layout.py` — the scenario row STACKS (`display:block`) so the enlarged 382.5 pt section sits on
  its own line and the "Why it has this shape" text takes the full content width below it (visual
  T193-r2 G3v F1: the side column had wrapped to ~one word per line); section labels unshrunk.

Tests (`services/api/tests/drawings/report/`):
- `test_report_scenario_integration.py` — NEW; S1–S8 integration with mutation proofs (see below).
- `test_report_drawn_manifest.py` — the legacy-predicate test rewritten to the manifest (the
  predicate is asserted gone); S1 comment updated.
- `test_report_comparison.py` — `test_s14` drives `footprint_drawn` explicitly (no monkeypatch).
- `test_report_appendix.py` — `test_s14` drives the state through the manifest (Lane E on/off).
- `test_report_pages.py` — `test_f7` now asserts "Shown on the site plan" (kit fallback draws the
  footprint); `test_f4`/`test_q1` re-scoped to the B2/B3 caption "Section (Illustrative)".
- `test_constraints_page.py` — `test_s8` now asserts the footprint legend replaces "No building
  placed".
- `test_location_sheet.py` — `test_s3` placed case now draws the footprint.
- `test_constraint_rows.py` — the "printed tax map" overlay assertions re-scoped to the page-4
  other-basis dimension labels (`data-role="other-basis-dimension"`), excluding the scenario-sheet
  and footprint-caption prose (carry item 2).

Evidence + e2e:
- `apps/web/e2e/report-print.flag-on.spec.ts` — asserts the site page draws the illustrative
  footprint (`data-role="illustrative-footprint"`) and the scenario sheet the two-zone area
  illustration (`data-role="area_zone_apartment"`); text-size/width checks unchanged (S6).
- `docs/research/evidence-records/NB-04-lot-dimensions-basis.json` — revision 4 (DB-283): code
  identity resynced (close_frame_dimensions.py 8394b3e6 → 3950da23), `maps/placed_footprint.py`
  added to code_paths/identity (6ffae044), a revision-4 dependency assessment; status unchanged
  (README / RESEARCH_REQUESTS untouched); research_record_check shows NB-04 code_current True.

## Scenarios S1–S8 (each with its test)

- S1 drawings off / 1.4.0: `test_report_scenario_integration.py::test_s1_drawings_off_no_drawing_and_every_claim_reads_not_drawn`, `::test_s1_1_4_0_document_makes_no_new_drawn_claim`.
- S2 real print (maps + Lane E): `::test_s2_real_print_page4_footprint_drawn_with_both_bases`, `::test_s2_real_print_page5_shown_page6_sheet_and_appendix`.
- S3 kit fallback: `::test_s3_kit_fallback_draws_the_footprint_and_page5_agrees`; also `test_report_pages.py::test_f7`.
- S4 degenerate footprint (placed, not drawn): `::test_s4_degenerate_footprint_every_claim_reads_not_drawn` + mutation `::test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn`.
- S5 shared pins: the per-file pin updates listed above; `test_report_pages.py`, `test_report_comparison.py`, `test_report_appendix.py`, `test_constraints_page.py`, `test_location_sheet.py`, `test_constraint_rows.py`.
- S6 budgets: `::test_s6_footprint_caption_adds_a_bounded_number_of_words`; no-maps budgets unchanged (`test_report_benchmark.py` TOTAL_WORD_CAP, `test_constraints_page.py::test_s10`); the e2e spec carries the footprint/area-illustration assertions.
- S7 NB-04 revision 4: research_record_check shows NB-04 code_current True (an independent G1 delta review records the review entry).
- S8 three print states + H4 T7/T8: `::test_s8_the_footprint_kind_literal_equals_the_kit_style_kind`, `::test_s8_every_printed_claim_matches_the_rendered_footprint_state`, `::test_s8_no_figure_mixes_the_two_bases_and_each_is_named`, `::test_s8_long_commit_and_address_change_no_claim`.

## The seven owner rows bound by the orchestrator's correction (b561450e)

- R198 (every "shown on" line names a page that shows it): `test_s2_real_print_page5_shown_page6_sheet_and_appendix` + the e2e `footprintOnSite` assertion.
- R200 (zones named only where drawn): `test_s2_...appendix` ("it is shown as zones ...") + `test_s4_degenerate...` (no zones claim when not drawn) + e2e `areaIllustrationOnScenario`.
- R203 (no visible claim rests on a data field): `test_s8_every_printed_claim_matches_the_rendered_footprint_state` (page-5 status == footprint kind actually drawn, across four states).
- R204 (a claim that keeps `readers.building_not_placed()` states placement, never drawing): the chart's `placed_on_site` reads `building_not_placed` for PLACEMENT, and the DRAWN state reads the manifest's `footprint_drawn` (`drawings_embed.allowance_bar_chart_svg`); `test_s14_placed_on_site_three_states`.
- R205 (references, legends, statuses and methodology corrected together): the manifest threads one `footprint_drawn`/`illustration_state` to the site legend+caption, the page-5 status, the scenario placement line and the appendix method in one builder pass; `test_s1`/`test_s2`/`test_s4` assert all four together.
- R277 (print state with no rendered drawing): `test_s1_drawings_off...`.
- R278 (print state with a rendered drawing): `test_s2_real_print...` and `test_s4_mutation...`.

## Carry items (packet path_notes)

1. B3 integration — round 1 `cece9d3e` and round 2 `069e2623` cherry-picked; accepted at one head. DONE.
2. test_constraint_rows "printed tax map" — re-scoped to the page-4 `other-basis-dimension` labels (DEVIATION from the literal "scope to site section": my footprint caption's clearance sentence contains "printed tax map" in the site section by design — owner standard, both bases named — so a site-section scope would no longer exclude it; the overlay-label scope is the faithful intent). DONE.
3. Manifest None state — `_area_illustration_drawn` deleted; the clause's `None` branch rewritten to the not-drawn clause. DONE.
4. footprint_drawn threaded to the three pages; B2's height-line detection confirmed against B2's real signature (section caption "Section (Illustrative): ... (Conditional)."). DONE.
5. The `illustrative_footprint` kind literal pinned equal to the kit style kind — `test_s8_the_footprint_kind_literal_equals_the_kit_style_kind`. DONE.
6. Page 4 and page 5 read one manifest (close frame AND kit fallback draw the footprint) — `test_s8_every_printed_claim...` + `test_f7` (kit fallback). DONE.
7. Every drawing claim reads the manifest; a claim keeping `readers.building_not_placed()` states placement, never drawing — R204 above. DONE.
8. The kit fallback "Lot outline: Approximate — tax map" note sits over GIS figures — my page-4 caption states the footprint is on the city-map outline and names the tax-map clearance separately, so it does not read as the printed tax map. DONE.
9. The page-4 caption names the footprint figure — the illustrative-footprint legend + caption; the GIS edge labels are the footprint's own (B1). DONE.
10. Page fit — the scenario row stacks; see the print section. DONE (verified on the page image).
11. B3 round-2 captions on the real print — see the print section. VERIFIED on the page image.
12. NB-04 revision 4 — DONE; independent G1 delta review pending (reviewer).
13. Backlog (not this part): 35.31 vs the drawn 35.32 / 99.98 edge — left untouched; RISK 2 holds (35.32 is NEVER drawn; only the document's 35.31 is printed as a sentence).

## Checks (exit codes and counts)

- `cd services/api && python -m ruff check .` — PASS (exit 0, "All checks passed!").
- `python tools/modularity_check.py --check` — PASS (exit 0; 821 files, failures 0, 33 pre-existing warnings; none for the edited report files).
- `python3 tools/research_record_check.py --check` — PASS (exit 0; NB-04 code_current True).
- `python3 scripts/lanes/check_lane_paths.py --coverage` — PASS (11032 files, each owned by one lane).
- `tests/drawings/report` — 273 passed (exit 0; 117.62s), run under the heavy-run lock.
- `tests/drawings tests/cad tests/api/test_report_read_api.py` — 2048 passed, 6 skipped (exit 0;
  222.73s), run under the heavy-run lock (the documented command at the final wiring head).
- apps/web `npm run typecheck` — exit 0; `npm run lint` — exit 0 (2 pre-existing warnings, other files). The e2e Playwright spec must PASS IN CI (cannot run Playwright on this server).

## Mutation proofs (new behaviour tests)

- WIRING (live, resuming builder): reverting `builder.py` line 100 to `footprint_drawn = None`
  (unwired) fails exactly 3 integration tests — `test_s2_real_print_page4_footprint_drawn_with_both_bases`,
  `test_s2_real_print_page5_shown_page6_sheet_and_appendix`, and
  `test_s8_every_printed_claim_matches_the_rendered_footprint_state`
  (`AssertionError: maps: footprint kind drawn=True but page-5 shown=False`); restored from the index,
  ruff clean. This proves the whole wiring is load-bearing for the page-4 caption and the page-5 status.
- Footprint drawn-state: `test_s4_mutation_a_drawable_footprint_flips_every_claim_to_drawn` — a degenerate ring gives "Worked out; not drawn" / "The worked-out footprint is not drawn on this map."; restoring the drawable ring flips to "Shown on the site plan" and drops the not-drawn line. Also the BEFORE/AFTER print table above is a whole-report mutation proof.
- Area-illustration state: `test_report_appendix.py::test_s14` — Lane E off → "not yet drawn"; on → "it is shown as zones". `test_report_drawn_manifest.py::test_s2/test_s3` flip the chart/clause by flipping the manifest input.
- Chart predicate deletion: `test_report_comparison.py::test_s14` — `footprint_drawn` False/None vs True moves the status word.

## The page-by-page print comparison

Recipe (builder-safe, no ports): TestClient POST `/api/v1/properties/4073340070/report` with
`benchmark_provider(with_zoning_lot=True, street_on=True)` + `recorded_pack_provider(window pack)`,
`RENDER_GIT_COMMIT` a 40-character value, then `node apps/web/scripts/print-report-pdf.mjs`,
`pdftoppm -r 100`. Scratch (resuming builder): `/tmp/claude-0/M5-T173-builder-7k2m9x/`. Three AFTER
states printed (maps 11 pp, kit_fallback 11 pp, drawings_off 9 pp); BEFORE at a clean `e016a59d`
`git archive` extract (maps 10 pp). Image files the resuming builder LOOKED at:
`after_maps-page-04.png` / `-05.png` / `-06.png`, `after_kit-page-04.png`, `after_off-page-4.png`.

Page counts: AFTER maps = 11 pages (S6 cap ≤ 11; main was 10, DB-270). Every page carries
substantial content; NO block sits alone on a blank page (checked page by page on the images).
pdftotext of after_maps: 35.32 count 0, 34.32/34.33 (the forbidden average) count 0, and the full
"...reads 33.34 feet on the tax map and 35.31 feet on the city-map outline..." sentence present.

BEFORE (`e016a59d`, B1/B2/B4 present but UNWIRED) vs AFTER (`diff_pages.py before_maps.pdf maps.pdf`):
- pages 1–3: IDENTICAL.
- page 4 (the footprint page): ADDED `64.66 ft` / `103.88 ft` footprint dimensions; the legend
  "No building placed" → "Illustrative building footprint"; ADDED "Illustrative building footprint
  on the city map outline (not surveyed; not a design)." and the clearance sentence "…reads 33.34
  feet on the tax map and 35.31 feet on the city-map outline…". Image:
  `maps-page-04.png` (footprint drawn on the GIS basis, both clearance bases named, neither mixed;
  35.32 is NEVER drawn — RISK 2 holds).
- page 5: "Placed on site: Worked out; not drawn" → "Shown on the site plan" (`maps-page-05.png`,
  a status word, no bar).
- page 6: the section gains the permitted-envelope height lines (55/45/30 ft) and the "Section
  (Illustrative): … (Conditional). Horizontal width is schematic, not to scale." caption; the
  "Why it has this shape" text now takes the FULL content width (my layout.py stacking fixes the
  one-word-per-line side column, visual T193-r2 G3v F1); the two-zone area illustration carries
  12,090 / 8,060 / 20,150 sq ft (`maps-page-06.png`).
- pages 7–11: the scenario tail (one-column floor schedule + rounding note + apartment estimate +
  unresolved items, `maps-page-07.png`) and the appendix reflow as the sheet grew to two pages.

AFTER vs main's real print (`print-main-065e3fb5/report.pdf`, 10 pages): the SAME material changes
on pages 4–6; the only other difference is the address casing on pages 1–3/8 ("NORTHERN BOULEVARD"
vs "Northern Boulevard") — a print-recipe artifact of the `address=` param I passed, not a code
change (the owner's real preview uses the recorded address).

Other states: kit_fallback `maps`→`kit_fallback-page-04.png` draws the illustrative footprint
(kit report frame) and page 5 reads "Shown on the site plan" (S3); the kit's own "Lot outline:
Approximate — tax map" note is the pre-existing DB-269 residual (RISK 3) and my city-map caption
does not make the footprint read as the printed tax map (carry item 8). drawings_off: page 3 "the
site plan is not available", page 4 "Worked out; not drawn" (S1), 9 pages, no footprint.

## What I did NOT check / limits

- The Playwright e2e spec (`report-print.flag-on.spec.ts`) was NOT run here (no browser-driving e2e
  on this server); its new footprint/area-illustration assertions and the text-size/width checks
  must be confirmed GREEN IN CI at the exact head. I verified the server report route renders the
  footprint (`data-role="illustrative-footprint"`) and the area zones (`data-role=
  "area_zone_apartment"`) via TestClient, and that the route reads the process env for Lane E
  (`env=None` → `os.environ`), so the flag-on :3001 server draws them.
- The NB-04 independent G1 delta review is the reviewer's step; I resynced the code identity and
  added the dependency assessment only.
- The owner's real-preview print is the orchestrator's (I never touched the preview or ports
  3000/3001/8000).
- DB-227 corner-area drawing stays undrawn (not established); the 35.31-vs-35.32 operand question
  (H5 item 3) is backlog, not this part.

