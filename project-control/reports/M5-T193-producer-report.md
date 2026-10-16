# M5-T193 producer report — M5-T173 part B3 (page-6 scenario sheet)

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a55c8ecf1de23cf2c`.
Base head reset to at dispatch: `b9e9d563a8b9e869bcaf4af8862c9f3d411de645` (head of `task/wave29-scenario-drawings`).
Parallel part (with B1, B2, B4); integrated by the serial wiring part W.

## What changed

Two source files + one new test file (all inside the packet's allowed_paths):

1. `services/api/app/drawings/report/scenario_figures.py` (NEW) — the scenario-sheet drawings.
   - `embed_area_illustration(building, *, env) -> Embedded | None`: behind
     `kit.flag.drawing_kit_enabled`, calls
     `kit.area_allocation.draw_area_allocation(block, placement=building['placement'], caption=False)`.
     Returns `None` when the kit is off or the building carries no `area_allocation` block (so a
     1.4.0 sheet shows no illustration and no new claim); the drawing when drawn (SVG sized to points
     like `drawings_embed`); the kernel's own `Unavailable` reason verbatim when it refuses.
   - `embed_section(building, results, *, env) -> Embedded`: calls `kit.render_floor_stack` with
     `results=` ONLY when that keyword is in its signature (part B2), else `drawings_embed.embed_floor_stack`;
     any kit failure falls back to the plain call, so the two parts land in either order with no error (S7).
   - `embed_scenario_drawings(results, *, env)` / `scenario_drawings_for(building, results, *, env)`
     return a frozen `ScenarioDrawings(area_illustration, section, section_has_height_lines)` per worked
     building, for part W to embed once and pass through `drawings=`.
   - `_permitted_envelope_has_height` is a document read (status available + ≥1 finite non-negative
     standard-case height in feet from `answers.permitted_envelope.values`) used only to decide the
     section caption when B2 is present — no zoning law computed here.

2. `services/api/app/drawings/report/page_scenario_sheet.py` (EDIT) —
   `render(results, ident, *, env=None, drawings=None, footprint_drawn=None)`; `drawings=None` embeds
   itself via `scenario_figures`.
   - Area illustration placed under the section/text row with ONE figcaption: the caption token, then
     `apartment area {apartment_area_sqft} sq ft; other building area {other_area_sqft} sq ft; of
     {total_sqft} sq ft residential floor area; footprint on the {placement.basis in words}` — read
     from the document, existing formatting, no percentage, no second sentence. The footprint-basis
     clause is added only when `fitted` is True (the bar carries no footprint). Basis words:
     `printed_tax_map -> "printed tax map"`, `gis -> "city map outline"` (never a GIS outline mislabelled
     a tax map, G-10), else the readable token.
   - Section caption: height lines drawn →
     `"Section (Illustrative): storeys from the floor schedule; height limits from the permitted
     envelope (Conditional)."`; `footprint_drawn` True drops the `", with no placement on the lot"`
     clause; otherwise today's text byte-for-byte.
   - Placement line: `building_not_placed(results)` keeps `NOT_PLACED_LINE`; placed + floor plates
     available + `footprint_drawn` False → `"The footprint is worked out but is not drawn in this
     report."`; True or None → nothing.
   - Schedule: the `"Plan area"` column header is relabelled `"Zoning floor area per storey"`; the
     document conversion statement is printed once on the page (inside the illustration when drawn,
     else one footnote under the schedule); the note
     `"Storey areas are shown rounded; the running total adds the unrounded areas."` only when the
     shown per-storey figures do not add to the shown running total. The estimate block
     (page_scenario_sheet.py:117-126 equivalent) is unchanged.
   - Unresolved: `"Unresolved for this building"` (Pending verification chip) = `building.not_checked`
     plus `placement.not_checked`, de-duplicated case-insensitively in document order, then one line
     linking the appendix open items by number (`readers.open_items` anchors `#issue-<n>`; commas and
     the full stop sit inside each anchor so they do not read as separate budget words).

3. `services/api/tests/drawings/report/test_scenario_sheet.py` (NEW) — acceptance scenarios S1–S7
   (19 tests), numbers literal from `placement-building-b.json`, engine prose read at test time.

## Why (audit 2026-10-15c §3–4)

Page 6 showed a generic stack "with no placement on the lot"; 12,090/8,060 sq ft appeared nowhere;
one unchecked item of the placement's six; 3 × 6,716.67 against 20,150 with no reconciliation. This
part draws the two-zone allocation with the areas and basis, reconciles the schedule, shows all six
unresolved items, and makes every drawn/placed claim take an explicit flag.

## D-093 / research-and-verification

Values checked against `docs/reference-cases/R6B/cases/placement-building-b.json` rows `area-allocation`
(12,090.00 / 8,060.00 / 20,150.00 at the 60% share), `plate` (6,716.67 per storey), `footprint-tax-map`
(printed-tax-map basis), `physical-plate-not-checked`. No value comes from a program run; the kernel
validates and prints the block's own figures. No evidence record has `code_paths` under
`app/drawings/report/scenario_figures.py` or `page_scenario_sheet.py`, so no record was edited (NB-04's
`code_current=False` is the pre-existing DB-283 on `close_frame_dimensions.py`, part W's — not touched
here). `review_register/register.json` cites no `app/drawings` module. No rule behaviour changed, so no
zoning-rule-review entry.

## Checks (exit codes and counts)

- `cd services/api && python -m ruff check .` — **exit 0** (All checks passed), on scenario_figures.py,
  page_scenario_sheet.py, test_scenario_sheet.py.
- `flock /root/project/lanes-runtime/heavy-run.lock python -m pytest -q tests/drawings/report tests/drawings/kit`
  — **1 failed, 730 passed** in 120 s. The one failure is the shared-pin collision below
  (`test_constraint_rows.py::test_s12_1_4_0_report_with_maps_draws_no_overlay`); every other report/kit
  test, including the benchmark pins `test_report_benchmark.py` and `test_report_pages.py`, is green.
- `pytest -q tests/drawings/report/test_scenario_sheet.py` — **19 passed**.
- `python tools/modularity_check.py --check` — **exit 0**; scenario_figures.py (176 lines) and
  page_scenario_sheet.py (337 lines) raise no warning.
- `python3 tools/research_record_check.py --check` — **exit 0** PASS (NB-04 `code_current=False` is the
  pre-existing DB-283, reported not failed, part W's).
- `python3 scripts/lanes/check_lane_paths.py --coverage` — **exit 0** (10920 files, each one lane).

## Budgets (benchmark)

- Plain render (LANE_E off): page 6 (scenario-B) = **258 visible words** (cap 260); whole report =
  **2,339 words** (cap 2,448; was 2,231). Repeat count of 8+-word sentences = **0**.
- LANE_E on (no map): whole report = 2,458 words. No test covers this render (H5 PART 1 item 12 recorded
  ~2,468 for the maps+kit render); the plain report the cap governs is 2,339.
- Exactly one percentage on the sheet ("60% apartment area", the kernel's). The conversion statement
  appears once on page 6 in both drawing states; it also appears once in the appendix (different
  sentence — `"The plate measure is stated as: …"`), so the report repeat count stays 0.
- `"Floor-stack section (Illustrative)"` count in the LANE_E-on report = 1 (keeps
  `test_report_pages.py:265/311` green while `footprint_drawn` is None).

## Mutation proof (each new behaviour test; revert → fails → restore)

Driver backed up each file, applied the mutation, ran the one test, restored the original (0 `# MUT`
leftovers afterwards). All FAIL as expected:

- S2 illustration present (embed_area_illustration → None) — rc=1, 1 failed.
- S2 caption figures (_area_caption → token only) — rc=1, 1 failed.
- S4 footprint_drawn False → worked-out line (guard disabled) — rc=1, 1 failed.
- S4 footprint_drawn True → drop clause (guard disabled) — rc=1, 1 failed.
- S5 rounding note (_needs_rounding_note → False) — rc=1, 1 failed.
- S5 conversion footnote when not drawn (footnote branch disabled) — rc=1, 1 failed.
- S6 six-items dedup (drop placement.not_checked) — rc=1, 1 failed.
- S6 linked line (_appendix_link_line → None) — rc=1, 1 failed.
- S7 section caption height lines (height-line branch disabled) — rc=1, 1 failed.

## Render for the visual review (no ports)

`build_report_html(benchmark(), env={"LANE_E_ENABLED":"1"})` written to scratch
(`benchmark-report-lane-e.html`, `page6-scenario-B.html`). Full PDF print + page-count (DB-270, RISK 2)
is part W's per the H5 split (W S2/S6 does the real print). Page 6 confirmed to carry: the two-zone
illustration (`data-role="area_zone_apartment"`/`area_zone_other`, not the bar), one `60% apartment
area`, the caption with 12,090 / 8,060 / 20,150 sq ft and `footprint on the printed tax map`, the bare
`Residential floor area` measure (no `Measure:`), the relabelled schedule column, the rounding note, the
six-item unresolved list (parking once) and the appendix link line.

## STOPPED / shared-pin collision for the orchestrator (part W must re-pin)

`services/api/tests/drawings/report/test_constraint_rows.py::test_s12_1_4_0_report_with_maps_draws_no_overlay`
(line 264) asserts `"printed tax map" not in html` on the whole benchmark report rendered WITH maps +
LANE_E. The packet-required page-6 caption now legitimately prints `footprint on the printed tax map`,
so this whole-HTML assertion fails. `test_constraint_rows.py` is a **forbidden file for B3** and is in
part W's allowed_paths (W "updates the shared pins that follow the drawn state"). I did NOT edit it.

- The assertion's INTENT is the page-4 map overlay (cf. line 254, which asserts `"printed tax map" IN
  html` for the `rear_yard_1_5_0` doc whose `input_facts` draw the overlay's other-basis frontage). It
  is not about page 6.
- Suggested one-line re-pin (W): scope line 264 to the site-and-context section, e.g.
  `site = html[html.index('id="site-and-context"'):html.index('id="option-comparison"')]` then
  `assert "printed tax map" not in site` (the page-4 overlay is absent for the benchmark), leaving the
  page-6 caption free. This is the H5 "shared pins that follow the drawn state" re-pin and belongs to W.

No other forbidden pin broke (benchmark pins green). No source file outside allowed_paths was changed.

## Limitations / assumptions

- The B2 height-lines branch is exercised only via a stub at this head (B2 absent); the caption switches
  to the height-line wording when `render_floor_stack` carries `results=` AND the document has a finite
  standard-case permitted-envelope height AND the section drew. If B2 drops all lines while the envelope
  is "available", the caption could over-claim; W should confirm against B2's actual availability logic
  at integration.
- The appendix link line links ALL numbered open items (the faithful reading of "the appendix open
  items by number"); a narrower per-building subset would need a shared classifier the readers module
  does not expose publicly.
- `footprint_drawn` defaults to None, so at this head the section caption keeps "…with no placement on
  the lot" (the audit-noted wording) until W passes `footprint_drawn=True` — the staged delivery the H5
  split intends.
