# M5-T166 producer report — one locator and a dimensioned constraints close frame

Producer: geospatial-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a9abc376695a5d1e2`.
Base: `d248293a0e8b77ea795cca73626443970e3a3506` (branch head of `task/wave24-report-v3`;
moved on from the claim head `adc36fc7` with commits that touch none of this task's files).

This task was continued from an earlier builder that was stopped at a session handoff. Its
unfinished work (`M5-T166-builder-unfinished.patch`, base `adc36fc7`, 10 files) was applied
cleanly at `d248293a`, reviewed against the packet and contract, and completed here. Its last
note (NB-04 revision 2 not yet written, so the research-record check would fail once
`close_frame_dimensions.py` was added to `code_paths`) was the main open item; it is resolved.

## What changed and why

- **Page 2 = the neighbourhood locator only** (`page_location.py`). The block close-up is still
  built in `resolve()` (restorable) but no longer printed; `block_map.py` and its tests are
  untouched (D-094 R014/R074).
- **Page 3 = a large dimensioned constraints close frame** (`site_context_plan.py` `frame="close"`;
  `context_scene.py` `compose_context` close mode + `CLOSE_PLAN`/furniture constants;
  `close_frame_dimensions.py`, the new module that holds the dimension-line logic so
  `site_context_plan.py` does not grow past its responsibility). The subject lot and its
  edge-sharing neighbours (lots 1, 11, 61) dominate; every edge ≥ 6 ft carries a dimension line
  anchored to the edge's own projected vertices; north arrow, scale bar, street names with mapped
  widths, and a "No building placed" legend entry. No rear-yard or setback AREA is drawn (R008/
  R017): `test_s4_no_yard_or_setback_area_is_drawn` proves no law geometry is emitted.
- **Page-1 graphic**: kept as the compact summary-frame `site_context_plan` (the "compact" of the
  two site-plan jobs; the "large" is the page-3 close frame). This is pinned by the unchanged,
  passing `test_page1_carries_the_summary_frame_site_plan` and by `test_s12` (wrapper/caption
  unchanged); changing the summary composition would alter page 1, which a parallel task owns.
- **Heights**: the shown height values become a compact 3×2 standard / qualifying-housing table
  (`page_site_context.py` `_heights_table`); they are removed from the constraint rows so no value
  is listed twice. "Maximum lot coverage" stays once in the constraints table; no bare "Not shown".
- **"No building placed"**: a close-frame legend entry on the site page; the full not-placed
  sentence stays on the scenario sheet only (`test_report_read_context.py`, `test_s3`, `test_s8`).
- **"Map geometry only…"** honesty line dropped from every map caption (`map_caption.py`) so it
  prints once in the report (on the evidence page); `test_s6` asserts count == 1.
- **e2e** (`report-print.flag-on.spec.ts`, location block only, per the packet): updated to expect
  one locator figure/SVG on the location sheet (was two). Not run here; CI runs it.
- **Two ruff E501 fixes** in `site_context_plan.py` (lines carried in from the patch, 101>100):
  behaviour-identical (one extracted local, one wrapped call).

No CSS change was needed: every SVG is sized from its viewBox
(`test_close_frame_fits_the_a4_content_width`: width 512.0 ≤ 515.95 pt).

## Dimensions drawn (close frame)

The outline the close frame draws is the MapPLUTO (gis) lot-70 outline — the only basis the 1.4.0
document carries. Values traced to NB-04 E4's saved primary source
(`docs/research/owner-research/2026-10-10-215-16-northern-evidence/geometry-calculations.json`,
lot-70 `edge_lengths_ft` and `adjacent_shared_lengths_ft`), not this brief's summary.

| edge | length (ft, US survey) | label drawn | basis | identity |
|---|---|---|---|---|
| 0 | 99.97647 | `99.98 ft, map outline, not surveyed` | gis | boundary shared with lot 1 |
| 1 | 103.87921 | `103.88 ft, map outline, not surveyed` | gis | north edge (already in NB-04 rev 1) |
| 2 | 99.97605 | `99.98 ft, map outline, not surveyed` | gis | edge opposite the lot-1 boundary (not shared) |
| 3 | 101.70896 | `101.71 ft, map outline, not surveyed` | gis | boundary shared with lot 11 |
| 4 | 2.22445 | (undimensioned) | gis | sliver shared with lot 61; < 6 ft, left undimensioned |

Endpoints lie on the edge's own projected vertices within 0.01 ft (S1). One basis only; nothing
merged across bases; no tax-map value (100.76 / 100) is drawn (none is in the 1.4.0 document).
Street names/widths (Northern Boulevard 100 ft, 215 Place 60 ft) are the map document's own
`mapped_width_ft`; `label_problems` == [] confirms every drawn value traces to the document.

## State table (one test per input state)

| state | outcome | test |
|---|---|---|
| map document present | close frame + large site plan drawn; site section has an svg | `test_s4_close_frame_contents`, `test_s7_context_maps_svg_only_with_a_map_document` |
| map document absent | no "Context maps" text, no svg in the site section | `test_s7_context_maps_svg_only_with_a_map_document` (without branch) |
| one-outline check passes | surroundings shown (locator + close frame) | `test_s4_close_frame_contents`, `test_s1_location_sheet_opens_page_type_two` |
| one-outline check fails / missing layer | Unavailable (drawing) / lot-only fallback (report), never blank | `test_s4_a_missing_layer_gives_unavailable`, `test_s1_tolerance…` |
| edge too short to label (2.22 ft) | left undimensioned, never a bare number | `test_an_edge_too_short_to_label_is_left_undimensioned` |
| label below 8.5 pt / cramped frame | `DimensionPlacementError` (fail, never shrink / drop) | `test_s2_a_sub_minimum_size_fails…`, `test_s2_a_cramped_frame_fails…` |
| no building placed | legend on site page; sentence on scenario sheet only | `test_s8…`, `test_s3_not_placed_sentence_scenario_only_legend_on_site` |

## Commands (direct exit codes)

- `python -m ruff check .` (services/api, lanes venv ruff 0.13.0) → **exit 0** (clean; two E501 fixed).
- `python -m pytest -q tests/drawings tests/cad tests/api/test_report_read_context.py` →
  **exit 0**, **1739 passed, 6 skipped** (153–160 s).
- `python3 tools/research_record_check.py --check` → **exit 0**; NB-04 `status=conflicting_evidence`
  (unchanged), `code_current=True`, `review_state=stale` (revision 2 awaits the G1 review; reported,
  not failed).
- `python tools/modularity_check.py --check` → **exit 0** (site_context_plan.py 643 raw lines, SLOC
  under the 600 warn threshold; new logic is in close_frame_dimensions.py, 130 lines).

(The default `python` has no ruff/pytest installed; the project lanes venv
`/root/project/lanes-runtime/venv` was used. The e2e browser tests were NOT run and no server was
started — ports 3000/3001/8000 untouched; CI runs the e2e.)

## Mutation proof (each reverted; suite re-run green afterwards)

1. **Endpoint off its vertex by 0.1 ft** (`close_frame_dimensions.py`: `fr.px((a[0]+0.1, a[1]))`) →
   `test_s1_dimension_endpoints_lie_on_their_edge_vertices` **FAILED**:
   `AssertionError: edge 0 start off its vertex; assert 0.1125 <= 0.01`.
2. **Basis words dropped** (`text = f"{format_feet(length)}"`) →
   `test_s1_each_label_names_its_basis_in_plain_words` **FAILED**:
   `AssertionError: assert 'map outline' in '99.98 ft'`.
3. **Block close-up printed again** (re-added `_wide_figure("Block close-up", …)` in
   `page_location.render`) → 3 FAILED:
   `test_s5_at_most_three_map_figures_each_a_distinct_job` (assert 2 == 1 figures / block_map 0),
   `test_s1_location_sheet_opens_page_type_two`, `test_location_page_is_the_locator_only`.

All three mutations were reverted; no `MUTATION` marker remains; `close_frame_dimensions.py`
re-hashes to the identity recorded in NB-04.

## NB-04 revision 2 note

Revision 1 → 2 (`last_changed` 2026-10-11). Added `close_frame_dimensions.py` to
`implementation.code_paths` with its LF sha256
`f036a957ae5a2f1f99164e8d0872dd2bcc8369b6b27337c7935cf81c4b2c6f4d` in `code_identity`
(the two MapPLUTO connector paths and their hashes are unchanged and still match). Added three gis
quantities for the drawn close-frame edges not previously recorded (99.97647, 99.97605, 101.70896
ft), each traced to E4 and scoped "tax lot outline". `conclusion.research_status`,
`meaning_and_applicability`, the conflicts and conditions are unchanged — no result is promoted and
no verification status changes. README and RESEARCH_REQUESTS untouched. The revision-1 agent review
stays recorded; the record now reads `review_state=stale`, honestly reflecting that revision 2
awaits the G1 (data-contract-verifier) review.

## Changed snapshots

**None.** No `.svg` snapshot file was changed; the summary/wide/report/sheet frames use the
drawing's default parameters, so their output is byte-identical (`test_snapshots.py` passed). The
close frame is a new, un-snapshotted drawing.

## What I could not check

- **ruff could not be run under the default interpreter** (no module); I used the project lanes
  venv's ruff 0.13.0. Same binary CI uses; still, CI must confirm on the exact head.
- **e2e / browser (Playwright) and the running server** were not exercised (thin-client rule); the
  e2e location-block edit is verified only by reading. CI is the authority.
- **The gis street widths** (100 ft / 60 ft "mapped width") come from the map document's street
  layer, assembled by an earlier task; I confirmed traceability via `label_problems`, not the DCM
  source itself.
- **The unresolved inputs stay unresolved**: the rear-yard (NB-03) and street-wall/setback/side-yard
  (NB-06) analyses are `interpretation_awaiting_review` and NB-01 is `access_blocked`; the close
  frame draws no yard, setback or zoning-lot geometry depending on them (R008/R017), so no
  unresolved input is turned into a drawn figure.
- Nothing here is a professional verification.

## Rework 1 (G3/G4 F1: the page-1 graphic is the compact close frame)

Base reset to `8f713e6a6312a1cdcb6ae5eb941c2bd4e3a887db` (my cherry-pick `09ac564e` + M5-T165
integrated as `4617c720` + other wave-24 records). All three reviews (G3 code, G4 QA, G1 data)
PASSed with the same REQUIRED F1; the orchestrator kept the objective and ordered this change.

**What changed.** Page 1's site graphic is now the COMPACT CLOSE frame, not the old summary frame.
A new frame `summary_close` in `site_context_plan.py` draws the same close COMPOSITION as the
page-3 frame (`close_frame_view` — the subject and its edge-sharing neighbours dominate the tight
view) but at the 88 mm page-1 column (`SUMMARY_PLAN` sizing, `mode="summary"` furniture).
`page_location.py` now embeds `frame="summary_close"` for `summary_plan` (the swap is maps side
only; `builder.py` and `page_decision_summary.py` wrap the SVG they are given, unchanged). The 88 mm
column is too narrow for a legible basis label at >= 8.5 pt, so the compact frame draws NO dimension
line and NO dimension label at all (the large page-3 close frame carries them) — never a bare
number. Street widths and neighbour labels are dropped too, keeping the word budget.
`close_frame_dimensions.py` is unchanged, so NB-04 revision 2's code identity is untouched (I did
not edit NB-04; its review block is the orchestrator's to append).

**Files changed:** `site_context_plan.py` (new `summary_close` branch + docstrings),
`page_location.py` (embed `summary_close` + docstrings), `test_location_sheet.py`
(`test_page1_carries_the_summary_frame_site_plan` → `test_page1_carries_the_compact_close_frame_site_plan`,
pinning the compact close frame via `embed_map` identity and forbidding any dimension label; new
`test_page1_compact_close_frame_states` for the three input states).

**NOT edited (routed to the orchestrator):** `page_decision_summary.py` (an M5-T165 file) still
carries the wording "the existing compact summary frame" (docstring) and a comment naming the
"summary frame" for the page-1 graphic; these now misname the frame but are outside this task's
allowed paths — the orchestrator should route the wording fix to the M5-T165 builder.

**Page-1 word counts (visible_text, decision-summary section):**

| measurement | before (summary frame) | after (compact close frame) | cap |
|---|---|---|---|
| standing test `build_report_html(benchmark())` (no map_context) | 190 | 190 | 200 (M5-T165) |
| real report `build_report_html(benchmark(), map_context=…)` | 208 | 208 | — (not a standing test) |

The standing CI cap is measured WITHOUT a map document, so the page-1 map graphic does not appear
there (page 1 falls back to the kit site plan): the swap leaves it at 190, well under 200. With a
map document the page-1 section is 208 both before and after — the compact close frame carries the
SAME labels as the summary frame did (street names, `Lot 70`, north arrow, scale bar), so the swap
is word-neutral; the 208 is the pre-existing results-text size (M5-T165's page 1), not caused by the
graphic, and no standing test caps the with-maps page-1 section. I did not take page 1 over any cap.

**State table (page-1 frame):**

| state | outcome | test |
|---|---|---|
| map document present + one-outline check passes | page 1 = compact close frame (`summary_close`) | `test_page1_carries_the_compact_close_frame_site_plan`, `test_page1_compact_close_frame_states` (a) |
| no map document | surroundings unavailable; `summary_plan is None`; page 1 falls back | `test_page1_compact_close_frame_states` (b) |
| one-outline check fails (outline moved 0.5 ft) | surroundings dropped; `summary_plan is None` | `test_page1_compact_close_frame_states` (c) |
| compact frame, dimensions | none drawn (no line, no label) — never a bare number | the two assertions in `test_page1_carries_…` |

**Checks (direct exit codes; lanes venv):**
- `ruff check .` (services/api) → exit 0.
- `pytest -q tests/drawings tests/cad tests/journey tests/api/test_report_read_api.py tests/api/test_report_read_context.py` → exit 0, **1783 passed, 6 skipped** (includes M5-T165's now-filled page-1 tests).
- `tools/research_record_check.py --check` → exit 0 (NB-04 conflicting_evidence unchanged, code_current=True, review_state=stale pending the orchestrator's rev-2 review entry).
- `tools/modularity_check.py --check` → exit 0 (failures 0; site_context_plan.py still under the warn threshold).
- e2e/browser not run; no server; ports 3000/3001/8000 untouched.

**Mutation proof (each reverted; page-1 tests green afterwards):**
1. Put the summary frame back on page 1 (`page_location.py` embed `"summary"`) → both page-1 pins
   FAILED (`page1_svg == embed(summary_close)` false; it equals `embed(summary)`).
2. Enable edges on the `summary_close` branch (`with_edges=True`) → the compact frame drew four
   bare-number labels ("99.98 ft" … at 8.00 pt, no basis) and
   `test_page1_carries_the_compact_close_frame_site_plan` FAILED on `'data-role="dimension"' not in
   page1_svg`. (The literal "drop the basis words" mutation is N/A: the compact frame carries no
   basis label by design; this mutation proves the stronger "never a bare number" invariant.)

No snapshot `.svg` file changed in this rework.
