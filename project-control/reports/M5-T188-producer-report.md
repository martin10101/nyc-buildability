# M5-T188 (builder) producer report — constraint-overlay polish (DB-263) + S10 (DB-275)

Backend-engineer build at contract head `593f8c7ace9e807cd9ecd0790c87489e16827965`.
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-af47710c59cf2b3f5`.
No feasibility fact, rule, calculation or certainty-label changed. D-093 light: read (read-only)
`docs/research/evidence-records/NB-04-lot-dimensions-basis.json`, NB-06, and the settled readings
`docs/reference-cases/R6B/cases/{short-block-rear-yard,overlay-reading}.json`; none re-researched or
edited; every unresolved input stays unresolved. The change moves no number and names no new source.

## What changed (per advisory)

- **A1 (visual) — `constraint_overlay.py`.** The established LINE label's FIRST `_label_candidates`
  position is now a perpendicular offset OFF the line (a unit normal at the anchor), so the white-halo
  box sits beside the drawn line and a measurable part of the line stays visible. The full grid
  (including the on-line `(0,0)` origin and the rings) still follows as the fallback, so the
  fit/collision guarantee (`ConstraintOverlayError`, never shrink/drop) is unchanged. An area label
  passes no `perp` → byte-identical.
- **A2 (code) — `constraint_overlay.py` / `context_scene.py` / `site_context_plan.py`.** Deleted the
  fragile post-hoc SVG string rewrite `expand_frame_for_overlay` (regex on the first two height attrs
  + magic `_FURNITURE_TOP_PT=400.0`), its `__all__` entry, and the now-unused `import re`. Added a
  keyword-only `overlay_present: bool = False` to `compose_context`; in the close branch
  `height = furn_bottom + 8.0 if overlay_present else min(CLOSE_MAX_H_PT, furn_bottom + 8.0)`.
  `site_context_plan.py` close branch now passes `overlay_present=bool(constraint_lines)` and dropped
  the `expand_frame_for_overlay` import/call and the now-unused `from dataclasses import replace`.
  Other callers (`neighbourhood_map.py`, `block_map.py`, every non-close branch) omit the kwarg →
  default False → byte-identical (RISK 5 holds).
- **A3 (code) — `page_decision_summary.py`.** The page-1 rear-yard title strip fires only at a word
  boundary: the char after the title is `:` , whitespace, or end-of-string. The existing
  'Rear yard Rear yard …' outcome is preserved (char after 'Rear yard' is a space → boundary).
- **S10 (DB-275, scope correction 1) — `close_frame_dimensions.py`.** `draw_other_basis_dimensions`
  now excludes facts whose key starts `mapped_street_width:` from the other-basis LOT-dimension band.
  Those two gis street widths are already drawn on each frontage as '<n> ft mapped width'
  (`site_context_plan.py`), so the band no longer prints the duplicate chips '100 ft, map outline' /
  '60 ft, map outline'. A lot's OWN gis fact (a different key) still reads 'map outline'.
- **A4 (QA).** Real-geometry label-beside-line (S1) and legend-fit (S3) assertions added, no monkeypatch.

## RISK verifications

- RISK 4 (public symbol removal): `expand_frame_for_overlay` had exactly ONE consumer
  (`site_context_plan.py` import + call), verified in source; both removed. `grep -rn
  expand_frame_for_overlay services/api/app` → 0 hits. (`code_graph query --no-regen impact` returned
  `STALE (stale fingerprint): refusing to serve the cached graph` — advisory only; the one consumer was
  verified directly in source.)
- RISK 2 (latent plain-frame clip): untouched. Non-overlay close height stays 470.00 (S4).
- RISK 6 (modularity): `failures 0; warnings 33` (unchanged count). `site_context_plan.py` SHRANK;
  `context_scene.py` not flagged.

## One test per input state (tables)

**S1/A1 — overlay LINE label placement** (`test_constraint_overlay.py`, constructed inline line, not the shared fixture)
| input state | assertion |
|---|---|
| established line drawn | label anchor `screen_points[mid]` lies OUTSIDE the placed label box; ≥1 polyline vertex outside the box (line visible) |
| normal rect | label placed at ≥8.5 pt, no two boxes overlap (grid fallback intact) |
| rect with no room | `ConstraintOverlayError` raised (fail-rather-than-shrink intact) |

**S3/S4/A2 — close-frame height** (`test_site_context_close_frame.py`, recorded close frame + constructed inline line)
| input state | assertion |
|---|---|
| overlay present (overlay_present=True) | frame height > 470; 'No building placed' swatch y+height ≤ frame height (fits); swatch bottom > 470 (old clamp would clip); no `expand_frame_for_overlay` |
| no overlay (default False) | frame height == 470.00 (byte-identity on the plain frame); no `expand_frame_for_overlay` |

**S5/A2** (`test_constraint_overlay.py`): `expand_frame_for_overlay` absent from the module and `__all__`.

**S6/A3 — page-1 title strip** (`test_page_one_title_boundary.py`, constructed combined row)
| input state | assertion |
|---|---|
| title + space ('Rear yard Rear yard …') | stripped → 'Rear yard is conditional …' (S16 outcome preserved) |
| title + ':' | stripped → body after the colon |
| title == whole text | stripped to empty |
| title a bare PREFIX of a longer word ('Rear yardage …') | NOT stripped (left verbatim) |
| text not beginning with the title | untouched |

**S10 — other-basis band** (`test_constraint_overlay.py`, constructed facts)
| input state | assertion |
|---|---|
| street-width facts present (`mapped_street_width:*`, gis) + a lot fact | only the lot fact drawn; no '100 ft, map outline' / '60 ft, map outline' |
| street-width facts absent | lot facts unchanged (same keys, order, text) |
| a lot's own gis fact (different key) | drawn; basis_label == 'map outline' (filter keys on the KEY, not the gis basis) |

## Mutation proofs (each turned a test red, then restored)

| mutation | test run | result |
|---|---|---|
| S10 street-width filter removed (`lot_facts = list(facts)`) | `test_s10_street_width_facts_are_not_drawn…` | RED — drawn == 3 keys incl. the two `mapped_street_width:*` chips; restored |
| A1 perpendicular first candidate removed (`if perp: pass`) | `test_s1_the_line_label_sits_off_the_line…` | RED — `_point_in_box(box, 166.0, 286.0)` True (box covers the anchor); restored |
| A2 native-height rule removed (always `min(CLOSE_MAX_H_PT,…)`) | `test_s3_overlay_close_frame_grows…` (+ S4) | RED — overlay height 470.0 (not > 470); S4 stayed GREEN; restored |
| A3 boundary guard removed (plain startswith) | `test_s6_title_as_a_bare_prefix…` | RED — body mis-stripped to 'age rules …'; restored |
| A2 overlay_present gate dropped (always `furn_bottom+8`) | `test_s4_non_overlay_close_frame_stays_clamped_at_470` | RED — non-overlay height 474.0 != 470.0; restored |

## Checks (lanes venv; heavy runs one at a time under `flock /root/project/lanes-runtime/heavy-run.lock`)

| check | result | exit |
|---|---|---|
| `cd services/api && python -m ruff check .` | All checks passed | 0 |
| pytest `test_constraint_overlay.py test_site_context_close_frame.py test_page_one_title_boundary.py` | 50 passed | 0 |
| pytest consumer check `test_constraint_rows.py test_report_pages.py test_report_page_one.py` (read-only; not edited) | 89 passed | 0 |
| `grep -rn expand_frame_for_overlay services/api/app` | 0 hits | 1 (zero hits) |
| `python tools/code_graph/query.py --no-regen impact …/constraint_overlay.py` | STALE fingerprint (advisory; verified in source) | n/a |
| `python tools/modularity_check.py --check` | selected 812 files; failures 0; warnings 33 | 0 |
| pytest `tests/drawings/maps tests/drawings/report` (under lock) | 401 passed, 4 skipped | 0 |
| `python3 scripts/lanes/check_lane_paths.py --coverage` | LANE COVERAGE PASS: 10684 files | 0 |
| WHOLE api suite `pytest -q` (under lock) | 9965 passed, 8 skipped, 1 warning | 0 |

The 1 warning is the pre-existing `StarletteDeprecationWarning` (httpx), unrelated.

## Real print + page diff (no server, no ports)

TestClient POST `/api/v1/properties/4073340070/report?address=215-16 NORTHERN BOULEVARD, Queens`
with `benchmark_provider(with_zoning_lot=True, street_on=True)` + `recorded_pack_provider(
benchmark_215_16_northern_window)` (flags INTERNAL_RESULTS_ENABLED / LANE_A / LANE_E on) → HTTP 200,
`text/html`, 142067 bytes → `node apps/web/scripts/print-report-pdf.mjs` (Playwright Chromium) → 11-page PDF.

`diff_pages.py print-main-76745ade/report.pdf  …/M5-T188/print/report.pdf`:
- pages 1, 2, 3, 5, 6, 7, 8, 9, 10, 11: IDENTICAL text.
- **page 4: CHANGED — 2 lines removed: `60 ft, map outline` and `100 ft, map outline`** (the duplicate
  street-width chips, exactly DB-275 / S10). Nothing added. The lot's OWN other-basis figures stay: the
  band keeps `10,075 sq ft, city record` (recorded_lot_area) AND the lot's own gis fact
  `10,387.99 sq ft, map outline` (lot_outline_area, basis gis); only the two street-width chips go.
  (Round-2 G3 F2 correction: the earlier wording "the lot's own band carries no other gis lot fact …"
  was wrong — lot_outline_area is a gis lot fact and stays.)

This is the expected result: only page 4's two chips go (scope correction 1); pages 1 and 3 stay
byte-identical (S8 no-regression). The A1/A2 polish is NOT visible on the benchmark print because the
benchmark establishes NO constraint line (both lines not_known / not_established, RISK 1); the A1/A2
before/after is the constructed established-line case (S1/S3), the visual-G3 artifact.

## Scope / limitations / assumptions

- Only the 8 allowed files changed (5 production, 3 test). `close_frame_dimensions.py` is allowed per
  scope correction 1. No forbidden file touched; consumer tests (`test_constraint_rows.py`,
  `test_report_pages.py`, `test_report_page_one.py`) left read-only and green.
- The visual before/after SVGs for the G3 reviewer are produced from the constructed established-line
  close frame (recorded context + inline `rear_yard_100ft_line`): before (bb5c02b9 behaviour) the label
  box sits on the line and the overlay legend row is clipped at 470; after, the anchor is outside the box
  (S1) and the frame grows to 490 so the legend row (bottom ≈476) fits (S3).
- `code_graph query --no-regen` could not serve a graph (stale fingerprint); treated as advisory and the
  single `expand_frame_for_overlay` consumer verified directly in source.
- No push. One commit prepared with this report.

## Round 2 (G3 F1 required correction; F2/F3 advisories)

Round-2 build on the task branch `task/wave27-comparison-appendix`, reset to
`ac7b69e911aac1c25cd091c560c37e42f974c07a` (round 1 integrated there as `3c95cae9`).
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ac1b20a7c4a54baeb`. No feasibility
fact, rule, calculation or certainty label changed; D-093 light (NB-04, NB-06 read-only).

### F1 (REQUIRED) — the native-height predicate

Round 1 passed `overlay_present=bool(constraint_lines)` to the close `compose_context`. That is true for
ANY 1.5.0 document that merely CARRIES a `constraint_lines` block, even when every item is
not_established/not_known and nothing is drawn — exactly the benchmark (four items, all
not_known/not_established, no geometry). It dropped the `CLOSE_MAX_H_PT` clamp for the benchmark, growing
the page-4 close frame **470 → 474 pt**. Reproduced on the real benchmark inputs before fixing.

**Predicate chosen: the presence of an actually-drawn constraint kind** (the brief's second option).
`constraint_overlay.py` now exposes `CONSTRAINT_STYLE_KINDS` (the four constraint styles + the two
generic fallbacks `yard` / `setback_line`) and a helper `overlay_was_drawn(sheet)` that returns
`any(kind in CONSTRAINT_STYLE_KINDS for kind in sheet.kinds)`. A constraint style kind is registered on
the sheet ONLY when `draw_constraint_overlay` draws an established item (a not_established/not_known item
draws nothing; a line clipped wholly outside the lot draws nothing) — and none of those kinds is a
base-scene style (the scene draws subject_lot / neighbour_lot / street_area / building_footprint /
existing_building), so the predicate exactly answers "was an established constraint actually drawn?".
`site_context_plan.py` close branch now passes `overlay_present=overlay_was_drawn(sheet)`.
Why this over a boolean threaded from the drawing step: `draw_block_scene` returns only the `Sheet` and
is shared by six frames; threading a new return through all of them would be a far larger change than a
one-line read of the sheet the composer already consumes. Reads the actual draw outcome (clip included),
not the input list.

Result on the benchmark: close-frame height back to **470** (viewBox `0 0 512.00 470.00`), the only page-4
change being the two chips removed — the packet's stated intent and S8's premise restored.

**Tests (one per input state, `test_site_context_close_frame.py`):**
| input state | height | test |
|---|---|---|
| no constraint_lines | 470 | `test_s4_non_overlay_close_frame_stays_clamped_at_470` (existing) |
| a list, all not_established/not_known, no geometry (benchmark case) | 470 | `test_s4_a_not_established_constraint_list_stays_clamped_at_470` (NEW) |
| an established line drawn | > 470 (grows) | `test_s3_overlay_close_frame_grows_so_the_legend_row_is_not_clipped` (existing) |

Plus a direct unit test of the helper, `test_overlay_was_drawn_tracks_the_actual_draw_not_the_list`
(`test_constraint_overlay.py`): empty sheet → False; a not_established/not_known list drawn → sheet.kinds
empty → False; an established line drawn → a constraint kind on the sheet → True.

**Mutation:** reverting the predicate to `overlay_present=bool(constraint_lines)` turned
`test_s4_a_not_established_constraint_list_stays_clamped_at_470` RED (`474.0 == 470.0` assertion failed)
while `test_s3` (established, grows) and `test_s4` (no overlay, 470) stayed GREEN (`1 failed, 2 passed`);
restored.

### F2 (advisory, applied)

Corrected the round-1 real-print wording above: the lot's own gis fact
`lot_outline_area` ("10,387.99 sq ft, map outline") stays in the other-basis band alongside
`recorded_lot_area` ("10,075 sq ft, city record"); only the two street-width chips go. Verified in the
rendered HTML (counts: `10,075 sq ft, city record` ×1, `10,387.99 sq ft, map outline` ×1,
`100 ft, map outline` ×0, `60 ft, map outline` ×0).

### F3 (advisory)

**Kept the key-prefix exclusion** (`close_frame_dimensions.py`, skip keys starting
`mapped_street_width:`). An allow-list by kind would be LARGER and no clearer: it would need to enumerate
every lot-dimension fact key (which can grow), whereas the exclude-list is a single well-commented line
that matches the only producer family needing exclusion. The QA mutation (G4 MINE-A) already proved the
filter keys on the KEY, not the gis basis (a lot gis fact is kept). No change.

### Round-2 print + page diff (no server, no ports)

Same TestClient path as round 1 (`benchmark_provider(with_zoning_lot=True, street_on=True)` +
`recorded_pack_provider(benchmark_215_16_northern_window)`, flags INTERNAL_RESULTS_ENABLED / LANE_A /
LANE_E on) → HTTP 200, `text/html`, 142067 bytes → `node apps/web/scripts/print-report-pdf.mjs` (the
installed Playwright 1.61.1 Chromium; starts no server, binds no port) → 11-page PDF.
`diff_pages.py print-main-76745ade/report.pdf  …/M5-T188-r2/print/report.pdf`: pages
1,2,3,5,6,7,8,9,10,11 IDENTICAL; **page 4 CHANGED — 0 added, 2 removed: `60 ft, map outline` and
`100 ft, map outline`**. Page-4 close-frame SVG before/after: main `76745ade` `viewBox="0 0 512.00
470.00"` → after-fix `viewBox="0 0 512.00 470.00"` — **470 kept** (the 474 round-1 regression is gone),
only the two chips removed.

### Round-2 checks (lanes venv; heavy runs under `flock /root/project/lanes-runtime/heavy-run.lock`)

| check | result | exit |
|---|---|---|
| `cd services/api && python -m ruff check .` | All checks passed | 0 |
| pytest the three task test files | 52 passed (was 50; +2 round-2 tests) | 0 |
| pytest `tests/drawings/maps tests/drawings/report` (under lock) | 403 passed, 4 skipped | 0 |
| `python tools/modularity_check.py --check` | selected 812 files; failures 0; warnings 33 | 0 |
| `python3 scripts/lanes/check_lane_paths.py --coverage` | LANE COVERAGE PASS: 10715 files | 0 |
| WHOLE api suite `pytest -q` (under lock) | see the final return line | — |

Files changed in round 2 (all in allowed_paths): `constraint_overlay.py`, `site_context_plan.py`,
`tests/drawings/maps/test_site_context_close_frame.py`, `tests/drawings/maps/test_constraint_overlay.py`,
and this report. `context_scene.py` / `close_frame_dimensions.py` / `page_decision_summary.py` were NOT
re-touched in round 2 (their round-1 changes stand).

END-OF-REPORT
