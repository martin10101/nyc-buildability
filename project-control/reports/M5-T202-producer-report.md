# M5-T202 producer report (builder, frontend-engineer)

Task: Fitted two-zone illustration on the website (M5-T174 part B2a). Replace the
`fitted_deferred` stub with a web-native port of the PDF kernel's split geometry so the
website draws the two zones inside the placed footprint exactly as
`services/api/app/drawings/kit/area_allocation.py` (M5-T183) does. The component stays
mounted nowhere.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-aae110aa0f61f31b7`
Reset base (brief head): `60d0a096c1b009f29356f4faae5597a8a8f28114`.

## What changed and why

- `apps/web/src/lib/architect/area-allocation.ts` — ported the kernel's `_poly_area`,
  `_clip_x` and `_division_x` (100-step bisection) as `polyArea`, `clipX`, `divisionX`;
  ported `_placed_ring` (de-dup the closing vertex; caps: 1000-vertex ceiling,
  `|coord| <= 1e9` and finite, non-zero shoelace area) with its four refusal reasons
  byte-equal to the kernel. Removed the `fitted_deferred` view; a sound fitted block with a
  drawable placed outline now returns a new `fitted_zones` view carrying `apartmentFraction`
  (the apartment zone's share of the FOOTPRINT area), `divisionX`, the division segment
  y-extent, the de-duplicated `ring`, the two zone polygons and the ring bounds. No zoning
  maths and no block figure is recomputed — only the block's OWN placed footprint is split.
- `apps/web/src/components/architect/answers/AreaAllocation.tsx` — replaced the deferred
  placeholder with an SVG drawing (kernel `_draw_zones` in the browser): the two zone
  polygons share one neutral fill (`var(--pt-color-selected)`) and are told apart only by a
  hatch `<pattern>` (rotate -45 / -135, 5-unit spacing, 0.5 weight), over them the single
  footprint edge and the one proportional division line. Points are placed with the kernel's
  transform (scale the longer side to 196 units; flip y). Pattern ids are per-instance
  (`useId`) so several mounted illustrations never collide. The bar branch is unchanged; the
  legend, caption and expandable methodology are shared by both branches (`IllustrationFooter`).
- `apps/web/src/test-support/report-parity-area-zones.json` — golden written BY the kit code
  (`UPDATE_GOLDEN=1`), never hand-typed: benchmark share 0.6, de-duplicated ring
  `[[0,0],[100.76,0],[100.76,66.66],[0,66.66]]`, footprint_area 6716.6616, division_x 60.456,
  apartment_fraction 0.6.
- `services/api/tests/drawings/kit/test_web_parity_area_zones.py` — (1) regenerates the golden
  from the kernel and asserts the committed golden equals it; (2) pins the four outline refusal
  reasons AND the not-placed reason READ from the kernel to appear verbatim in the web selector
  (cross-surface byte-equality); (3) a benchmark-shape assertion (100.76 x 66.66, cut at
  0.6*width, 60% area).
- The two web test files — the selector input-state table + S1 golden parity + S2 one-test-
  per-degenerate-outline; the component S1 (zones drawn, one division, fraction/x = golden),
  S3 (bar unchanged), S4 (wording byte-equal to presentation-tokens.json; measure words),
  S5 (one fill + two hatch angles; no `<text>`, one division, no forbidden mark), fail-closed.

`area-allocation-tokens.ts` was NOT changed (see S4 below).

## Scenario coverage

- S1 (benchmark 0.6; 100.76 x 66.66): one division; apartment/footprint 0.6 within 1e-6;
  division x and fraction equal the kernel's golden. Covered in the lib test (`areaAllocationView`
  on the recorded fixture vs the golden) and the component test (`data-apartment-fraction`,
  `data-division-x` vs the golden).
- S2 (no / un-drawable outline): one test per state — not placed, withheld, < 3 vertices,
  > 1000 vertices, a non-point vertex, NaN/Inf/-Inf/1e308 coord, zero-area collinear ring,
  zero-width spike — each returns the kernel's byte-equal reason and nothing is drawn.
- S3 (fitted false): the bar branch and its DOM/test ids are unchanged; `area-allocation-zones`
  is absent for a bar.
- S4 (labels, caption, percentage, measure): zone labels and caption are byte-equal to the
  JSON `wording` tokens. MEASURE WORDS: kept the kernel's bare "Residential floor area"
  (`kit/area_allocation.py:49`). See the gap note below.
- S5 (hatch not colour; only the division inside; no plan detail): the two zones carry the
  same `fill` and differ only by `patternTransform`; the SVG contains no `<text>`; exactly one
  `area_division` and one `area_footprint`; no room/wall/unit/stair/elevator/"units"/"apartments".
- S6 (sq ft split): the kernel's drawing shows only the percentage (60%) and the labels, NOT
  the sq ft split (12,090 / 8,060). The website matches: it shows the percentage and labels,
  not the sq ft numbers. Neither surface shows the sq ft split. Gap note below.
- S7: `git status` shows only the six allowed files; `grep` finds no import or `<AreaAllocation`
  outside its own file and tests — still mounted nowhere.

## Gaps reported (unknowns per the brief)

- M5-T173 part B is NOT contracted at this head (`project-control/tasks/M5-T173.json` does not
  exist). Per the brief's unknown clause and the packet `path_notes`, I kept the kernel's bare
  "Residential floor area" for the measure words and did not change the on-screen presentation.
  The methodology disclosure still reads "Measure: Residential floor area" (M5-T187 presentation);
  H8 item 3 flagged the "Measure: " prefix as a surface difference from the PDF's bare label.
  The exact presentation of the measure next to the illustration is owned by the accepted
  M5-T173 scenario sheet; when it is accepted, a later part should align the prefix/placement.
- The sq ft split is shown on NEITHER surface (the kernel draws only the percentage). This is
  consistent; if the accepted M5-T173 sheet later prints the sq ft split, the website must add
  the same numbers from the block (never recomputed) at that time.

## Checks (direct exit codes; lanes venv; api from services/api)

- `ruff check .` (services/api) -> exit 0, "All checks passed!" (api CI first step).
- `pytest -q tests/drawings/kit/test_web_parity_area_zones.py` -> exit 0, 3 passed.
- `npm run lint` (apps/web) -> exit 0, 0 errors (2 warnings in pre-existing files I don't own).
- `npm run typecheck` (apps/web) -> exit 0.
- `npx vitest run` on both touched web test files (under the heavy-run lock) -> exit 0,
  Test Files 2 passed, Tests 35 passed.
- `tools/modularity_check.py --check` -> exit 0 (warnings only, all pre-existing files).
- `tools/research_record_check.py --check` -> exit 0, PASS. No evidence record's `code_paths`
  includes a file I edited (NB-01/NB-06 mention "area-allocation" only in historical prose about
  the backend `three_way_document.py`, which I did not touch; both code_current=True).
- `scripts/lanes/check_lane_paths.py --coverage` -> exit 0, PASS (10949 files, each one lane).

## Mutation proof (each new behaviour test; reverted after)

- Golden<->kernel (api): changed the golden `division_x` 60.456 -> 61.456 ->
  `test_web_parity_area_zones_golden_matches_kernel` FAILED (1 failed, 1 passed); restored ->
  2 passed.
- Geometry port (lib S1): changed `divisionX` target `share*total` -> `(1-share)*total` ->
  only the two S1 geometry tests FAILED (2 failed | 22 passed), S2 reasons still passed;
  restored.
- Cross-surface reason byte-equality (api): changed the web `AREA_REASON_OUTLINE_NO_AREA` string
  -> `test_outline_refusal_reasons_are_byte_equal_to_the_web_selector` FAILED on the missing
  no_area reason; restored.

## Not checked / out of scope

- No server, no e2e, no width capture, no report print (this part changes no report page; the
  component is mounted nowhere, so there is no page to print). Recipe V / the six-width capture
  belong to the later mount parts (B2d) and the orchestrator.
- CI at the merge head (full web + api suites, security gates) is the orchestrator's to read
  green per R639.
- What M5-T173's accepted sheet will finally print for the measure words and the sq ft split.
