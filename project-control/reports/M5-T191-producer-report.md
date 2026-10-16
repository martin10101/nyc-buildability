# M5-T191 (M5-T173 part B1) producer report — page-4 footprint renderers

Builder: backend-engineer. Base head: `b9e9d563a8b9e869bcaf4af8862c9f3d411de645`
(head of `task/wave29-scenario-drawings` at dispatch). Renderer level only; part W
(serial) threads the data and wires it into the live report.

## What changed

Opt-in illustrative building footprint on page 4, drawn from the engine's floor-1 plate
only; every other frame byte-identical (default `None`).

1. **NEW `services/api/app/drawings/maps/placed_footprint.py` (216 SLOC, < 300; S7).**
   `draw_placed_footprint(sheet, footprint, subject_outline, fr, rect, ...)` translates the
   results-local floor-1 plate ring onto the map lot by `constraint_overlay.overlay_offset`
   (import only — the pure translation that places the min-anchored results outline on the
   map subject outline). It validates the ring (finite; |value| ≤ 1e9; 3–1000 vertices;
   each vertex a pair; non-zero area; every translated vertex inside or ≤ 0.05 ft outside
   the subject outline) and draws it in the new kind `illustrative_footprint`
   (legend "Illustrative building footprint"). It dimensions two edges — the back edge
   (width) and one depth edge, chosen as the longest/shortest edge farthest from the lot
   boundary so both dimension lines fall on the lot-interior side and never meet the
   lot-edge dimensions — each a FIGURE-ONLY label of the edge's own length at ≥ 8.5 pt on a
   white background, reusing `close_frame_dimensions.DIMENSION_MIN_PT`, `context_scene.place`
   / `readable_angle` and `kit.labels.format_feet`. Plan-then-commit via a temp `Sheet`
   seeded with the live label boxes: an invalid ring or an unplaceable label draws NOTHING
   (returns `None`, no exception, never shrunk or partial; S4/S5). The two shared the
   city-map (gis) basis the close frame already states once in its note, so no basis words
   sit on the figures and no clearance or tax-map figure is drawn (NB-04; C-4).

2. **`maps/site_context_plan.py` (611 → 620 SLOC, +9 ≤ +15; S7).** `draw_site_context_plan`
   gained `placed_footprint=None`; the **close** frame alone draws it (after
   `draw_block_scene`, so it sits over the subject fill). `not_placed_legend` now drops to
   True only when `placed_footprint is None` — a passed-but-degenerate ring still removes the
   "No building placed" row (the engine placed the building; S4); a drawn footprint sets
   `overlay_present` so its legend entry gets the frame's full height like a constraint
   overlay's.

3. **`maps/__init__.py`.** `render_site_context_plan(..., placed_footprint=None)` forwards it.

4. **`kit/styles.py`.** One new `ShapeStyle("illustrative_footprint", "Illustrative building
   footprint", AREA, "#E8EEF2", "#5B7083", 0.8, (3.0, 2.0), Hatch(45, 4.0, True, "#5B7083",
   0.4), "A-BLDG-ILLUS", True, 8)` — a quiet neutral wash, dashed outline, unique crossed
   diagonal hatch (signature (45, 4.0, True), not used by any other AREA kind), unique CAD
   layer. Additive: no existing drawing draws this kind, so every existing SVG is
   byte-identical.

5. **`kit/site_plan.py` (352 → 473 SLOC; modularity PASS, below the 600 warn).** The report
   frame draws the floor-1 plate in kind `illustrative_footprint` (not the `Residential` use
   kind) with the same two dimensions; the sheet/summary frames keep the use-coloured plate
   byte-identical. The illustrative footprint is drawn LAST (after the lot/street/dimension
   labels) so its labels yield to them; the fill is spliced to the bottom so the lot lines
   read over it, the dimensions on top; plan-then-commit withholds the whole footprint if a
   label cannot be placed (S5). One latent fix: the registered legend kind now follows the
   drawn area kind (`for kind in tmp.kinds`) instead of a hardcoded literal — proven by
   mutation C below.

No file outside the allowed paths was edited. `test_report_frame.py`,
`test_report_frame_rework1.py`, `test_report_frame_rework3.py`, `test_style_table.py` (the
kit pins this part owns if they move) did NOT move — they pass unchanged.

## Acceptance scenarios

New tests: `services/api/tests/drawings/maps/test_placed_footprint.py` (S1, S2, S4, S5, S6,
S9) and `services/api/tests/drawings/kit/test_site_plan_footprint.py` (S3, S1-kit, S5-kit).
S2/S3 read the expected GIS figures from `docs/reference-cases/R6B/cases/placement-building-b.json`
row `gis-conflict-check` (frontage 103.88 ft, GIS plan depth 64.66 ft) — never a program run.

- **S1** — `placed_footprint=None` byte-identical to the base close frame; "No building
  placed" kept; sheet frame keeps the use plate (the close-frame/snapshot suites are unchanged).
- **S2** — close frame with the benchmark ring: footprint inside the subject lot, each drawn
  vertex = document vertex + `overlay_offset` within 0.01 ft (max err 0.0); legend
  "Illustrative building footprint", no "No building placed"; the two labels are exactly
  "103.88 ft" and "64.66 ft" (reference case); the single note "All dimensions: city map
  outline, not surveyed." printed once; `context_support.label_problems == []` (C-4, footprint
  dims included); no 33.34 / 35.31 / 35.32 / 100.76 / 66.66 in the SVG; labels ≥ 8.5 pt, no
  overlaps.
- **S3** — kit report frame: plate in `illustrative_footprint`, no "Residential" legend; the
  same two labels; one caption; within 182×150 mm; no overlap; `numbers_not_in_input == []`,
  `label_problems == []`; footprint labels ≥ 8.5 pt.
- **S4** — one test per degenerate state (non-finite, |value| > 1e9, a point not a pair,
  over 1000 vertices, under 3 points, zero area, a vertex 0.06 ft outside): draws nothing,
  no exception, no `illustrative_footprint` kind; a vertex 0.04 ft outside IS drawn (the
  0.05 ft tolerance boundary); on the close frame a degenerate ring still shows no "No
  building placed" row.
- **S5** — an unplaceable label (every lane blocked) withholds the whole footprint (maps and
  kit); the clear-sheet control draws it.
- **S6** — `placed_footprint` passed to summary / summary_close / wide / report / sheet is
  byte-identical to the same frame without it (pages 1 and 2 unchanged).
- **S7** — ruff + modularity pass; placed_footprint.py 216 SLOC (< 300); site_context_plan.py
  +9 SLOC (≤ +15).

### Mutation proofs (reverted, shown red, restored)

- **A** close branch `footprint = None` → `test_s2_footprint_drawn...` RED (no
  `illustrative_footprint`). Restored.
- **B** containment tolerance `≤ 0.05` → `≤ 1e9` → `test_s4[...vertex_0_06_ft_outside]` RED
  (an outside vertex drawn). Restored.
- **C** kit area kind `illustrative_footprint` → `plate.use` → `test_s3...` and `test_s1_sheet...`
  RED (kind `residential`, not `illustrative_footprint`). Restored. (This exposed and fixed the
  hardcoded `use_kind` that had masked the mutation.)
- **D** maps withhold `return None` → keep going → `test_s5...` RED (partial footprint drawn).
  Restored.

## Checks (lanes venv, from services/api, `-p no:cacheprovider`; direct exit codes)

- `python -m ruff check .` → `All checks passed!` (exit 0).
- `python tools/modularity_check.py --check` (repo root) → exit 0; `failures 0; warnings 33`
  (all pre-existing; site_context_plan.py above the warn threshold, no new failure).
- `python3 tools/research_record_check.py --check` → PASS. No evidence record's `code_paths`
  include any file this task edits (NB-04 pins `close_frame_dimensions.py`, import-only here,
  and is pre-existingly `code_current=False` per DB-283 — part W's revision); nothing to write
  here (D-093: STOP-if-needed not triggered).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → `LANE COVERAGE PASS` (10920 files).
- `flock .../heavy-run.lock python -m pytest -q tests/drawings/maps/test_placed_footprint.py
  tests/drawings/kit/test_site_plan_footprint.py` → **25 passed**.
- `flock .../heavy-run.lock python -m pytest -q tests/drawings tests/cad` → **1958 passed,
  6 skipped** (regression: sheet/maps/DXF snapshots byte-identical, close-frame and
  report-frame suites green, style table green).

## Pictures for the visual review

Standalone SVGs written to `/tmp/claude-0/M5-T191/`: `close_frame_footprint.svg` (maps close
frame with the benchmark footprint) and `kit_report_footprint.svg` (kit report-frame fallback).
This sandbox has no SVG→PNG rasteriser (no rsvg-convert / inkscape / chromium / cairosvg; web
deps not installed), so PNGs were not produced; the SVGs are directly viewable and the full
report print is part W's / the reviewer's harness.

## Assumptions, limitations, reported differences

- **Planner vs packet (reported per the brief):** S2's literal "maps_support.numbers_not_in_input
  passes" cannot hold on the close frame — the baseline (no-footprint) close frame already fails
  that RAW-number check because its subject-edge dimensions are edge LENGTHS, not raw document
  numbers (validated instead by the edge-sourced `context_support.label_problems`, which the
  footprint passes, == []). The test therefore (a) asserts full C-4 via `label_problems`, and
  (b) proves the footprint adds NO new untraceable number vs the baseline
  (`fp_missing ⊆ base_missing`). This satisfies S2's intent; recorded here as a difference.
- **Provenance source for the footprint dims:** `FOOTPRINT_SOURCE =
  "/geometry/floor_plates/entries/0/outline/0"` (the results pointer part W threads). The maps
  SVG thus carries a source into the RESULTS document for the footprint dims; part W resolves it
  against the results document in the integrated report's C-4.
- **S4 for the kit report frame:** the kit draws from the adapter-validated plate, so degenerate
  RINGS cannot reach it (the adapter fails closed earlier); the kit's degenerate behaviour is the
  unplaceable-label withhold (S5-kit). The ring-validation states are tested on the maps renderer.
- Input contract for part W: `placed_footprint` is the floor-1 plate EXTERIOR RING (a sequence of
  `[x, y]` pairs in results-local feet); a wrong shape fails validation and draws nothing.
- RISK 1/2/3 honoured: the GIS floor_plates outline (103.88 × 64.66) is drawn, never
  `placement.outline` (tax-map 100.76 × 66.66); the kind literal `illustrative_footprint` is
  unchanged (B4 manifest contract); the kit fallback's held caption is untouched.

END-OF-REPORT
