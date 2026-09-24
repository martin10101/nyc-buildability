# M5-T085 producer report - D-087 BLUEPRINT-1 (zero-dependency vector PDF site-plan sheet writer)

Producer: backend-engineer. Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t085`
(branch `task/M5-T085-pdf-sheet-writer`, claim-seam HEAD `f9bfd54d`). Scope: exactly the
three allowed_paths, nothing else touched. All evidence `[OBSERVED]` on this sandbox unless
marked otherwise.

## IMPLEMENTATION

- `services/api/app/cad/pdf_sheet_writer.py` (400 lines) - a pure, deterministic PDF 1.4
  writer over the stdlib only (`math`, `dataclasses`). Public surface: `SitePlanInput`
  (frozen dataclass; `generated_at`/`generator_version` are INPUTS, never a clock),
  `SitePlanRefusal` (typed fail-closed value), `render_site_plan_pdf` (`:136`),
  `choose_scale` (`:122`), `SCALE_CANDIDATES_FT_PER_IN` (`:65`).
- Drawing (device space, translation-only CTM): sheet + title-block borders via `re`
  (`_draw_rect :318`), lot/building rings via `m`/`l`/`h`/`S` (`_draw_ring :250`), per-edge
  dimension labels (`_label_edges :259`), grid-north arrow (`_draw_north_arrow :272`), scale
  bar (`_draw_scale_bar :283`), title block (`_draw_title_block :298`). Only reader-subset
  operators are emitted (straight lines, rectangles, horizontal text; no curves/images/
  rotated transforms), so the bytes round-trip through the in-repo strict reader.
- Object/xref/trailer assembly per ISO 32000-1 §7.5.4-§7.5.5 [recalled - verify]: 5 objects
  (catalog/pages/page/contents-stream/font), classic `xref` with 20-byte entries and exact
  10-digit offsets, `trailer`/`startxref`/`%%EOF` (`_assemble_pdf :361`). Content stream is
  uncompressed (no `/Filter`) with a direct integer `/Length`.
- Measurement honesty: dimension values are `math.sqrt(dx*dx+dy*dy)` over the EPSG:2263
  inputs only, rounded to 2 dp (`_label_edges :259`). Title block prints
  `Units: US survey feet   CRS: EPSG:2263`, `Scale: 1 in = N ft   Orientation: EPSG:2263
  grid north` (`:306-307`) - the arrow is labeled `GRID N (EPSG:2263)` (`:280`), never "true
  north".
- ONE escaper (`_escape_pdf_text :329`): ASCII-sanitise (non 0x20-0x7E -> `?`) then
  backslash-escape `(` `)` `\`; it is the sole path text takes into the stream. ONE number
  formatter (`_num :349`): `round(v,3)` then trim, `-0` collapsed - only IEEE-deterministic
  ops feed it, so bytes are stable across platforms.

## Per-AS evidence

- **AS-1 structure + determinism.** `test_valid_pdf_structure_markers` (header/xref/trailer/
  startxref/%%EOF/Root, test:105); `test_deterministic_bytes_no_clock` (render twice equal,
  test:115); `test_golden_sha256` = `c38360f9b803299c75dd837ec65de3e3a4dc046a11aa2bcb386fe74aa5312db2`
  (test:119); `test_xref_offsets_point_at_object_headers` independently parses the classic
  xref and asserts each in-use offset lands on `N 0 obj` (test:123).
- **AS-2 round-trip.** `test_roundtrip_reader_accepts_and_counts` (test:144) feeds the bytes
  to the in-repo `read_pdf_container` + `interpret_content`: PdfDocument, 1 page, EXACT
  counts segments=17 (`4 lot + 4 building + _SCALE_BAR_SEGMENTS(6) + _NORTH_ARROW_SEGMENTS(3)`),
  rects=2 (`_SHEET_RECTS`), text_runs=19.
- **AS-3 measurement.** `test_dimension_strings_from_2263_feet` (30x100 lot + 20x60 footprint
  yield `30.00/100.00/20.00/60.00`, test:169); `test_choose_scale_fits_sheet`
  (`choose_scale(30,100)==20.0`, test:178); `test_units_crs_scale_and_grid_north_printed`
  (`US survey feet`, `EPSG:2263`, `Scale: 1 in = 20 ft`, `grid north` all present, test:184).
- **AS-4 fail-closed + escaping.** `test_invalid_rings_are_typed_refusals` (invalid_ring /
  non_finite_coordinate x2 / oversize_input, test:207); `test_too_many_vertices_refused`
  (test:213); `test_geometry_larger_than_any_scale_refused` (test:220);
  `test_special_characters_round_trip_through_escaper` (address `12 MAIN ST \ (REAR)` survives
  intact, test:227); `test_escaper_bypass_mutant_reddens_roundtrip` (in-process mutant proves
  the container still parses but the content is refused when the escaper is bypassed,
  test:236); `test_xref_offset_corruption_is_detected` (test:261).
- **AS-5 honesty + scope.** `test_proposed_and_professional_review_stamps_always_present`
  (both stamps present even with no building, test:278); `test_never_claims_true_north`
  (test:287). Zero new dependencies (stdlib only); ruff + modularity clean; exactly the three
  allowed_paths changed.

## Self-check commands (verbatim; cwd noted)

- cwd `services/api`: `python -m ruff check .`
  -> `All checks passed!`
- cwd `services/api`: `python -m ruff check app/cad/pdf_sheet_writer.py tests/cad/test_pdf_sheet_writer.py`
  -> `All checks passed!`
- cwd `services/api`: `python -m pytest tests/cad/test_pdf_sheet_writer.py -q`
  -> `19 passed in 0.11s`
- cwd worktree root: `python tools/modularity_check.py --check`
  -> `EXIT=0`; `selected 483 files; failures 0; warnings 22` (all 22 warnings are pre-existing
  files; `grep -c pdf_sheet_writer` of the output = 0 - my module is not flagged).

## Mutation record (red/green; production temporarily mutated, then restored byte-identically)

Runner temporarily edited `app/cad/pdf_sheet_writer.py`, ran ONE named test, restored the
original, verified `RESTORED identical: True`:

- Baseline: `test_special_characters_round_trip_through_escaper` = PASS `1 passed in 0.30s`;
  `test_roundtrip_reader_accepts_and_counts` = PASS `1 passed in 0.21s`.
- Mutation 1 - escaper bypassed (drop the `( ) \` escape branch): escaper test = **FAIL**
  `1 failed in 0.46s` (unescaped literal string is unbalanced -> reader content parse
  refuses). Reverted.
- Mutation 2 - xref offset off-by-one (`offsets.append(len(out) + 1)`): roundtrip test =
  **FAIL** `1 failed in 0.34s` (reader's xref/object identity check refuses the lying offset).
  Reverted. `RESTORED identical: True`.

The suite also carries these as PERMANENT in-process guards (test:236, test:261) so the
regression backstop survives beyond this manual run.

## Environment / verification-context notes

- Sandbox is Python **3.11.9**; the repo/CI target is **3.12** (ruff `target-version=py312`).
  Importing `app.documents.extraction` normally fails here on an unrelated 3.12-only PEP 695
  line (`app/documents/units.py:276`) - the repo's own reader tests (`tests/documents/
  test_pdf_container.py`) also fail to COLLECT under 3.11 for the same reason. My test's
  `_reader()` helper (test:38) tries the plain package import first (used in CI 3.12) and, on
  `SyntaxError`, sideloads the SELF-CONTAINED reader subgraph (lexer/objects/xref/container/
  content) directly from the same source files (test `_sideload` :54). This exercises the
  identical reader code; it does not touch or modify the extraction package. `[OBSERVED]` on
  3.11 via the fallback; `[PREDICTED green]` on CI 3.12 via the plain import path.
- Golden sha256 was computed on 3.11/Windows. Only `+ - * /` and `math.sqrt` (IEEE
  correctly-rounded) feed `_num`, and every emitted number is `round(.,3)`-then-formatted via
  CPython's platform-independent dtoa, so the golden is expected byte-identical on CI 3.12/
  Linux. If CI ever disagrees, that is a real determinism defect to fix, not a flake.

## DISCOVERIES (D-069 - route to the orchestrator; not fixed in-packet)

- D1: The strict reader ignores `/Resources`/`/Font` and does not validate the `Tf` font name
  against the resource dictionary - a `Tf` with ANY name satisfies "font set before text".
  The writer still emits a real `/Font /Helvetica` resource for genuine PDF viewers. No action
  needed; noted so a future wiring packet does not assume the reader enforces font resources.
- D2: The reader's `interpret_content` does not advance the text position per glyph (no font
  metrics), so overlapping dimension labels are possible on very short edges at coarse scales.
  Purely cosmetic for this module; a later layout pass (leader lines / collision avoidance)
  would be its own product task if legibility matters.
- D3: `choose_scale` uses a fixed standard-scale ladder and a fixed Letter-landscape sheet.
  Sheet size / orientation / paper series (ARCH, ANSI) selection is a future enhancement, not
  in this packet's scope.

## Deviations

- None from the packet. Inputs are a frozen dataclass (not pydantic) to keep the writer pure,
  dependency-light, and obviously deterministic - consistent with the reader modules' plain
  dataclasses and within "stdlib only".

END-OF-REPORT
