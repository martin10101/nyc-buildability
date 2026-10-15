# M5-T172 (part B) producer report — wire the illustrative placement and area allocation

Builder: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a76899b748e3ebd3a`.
Contract head: `4516dbd7affb684ac76a750047843d617cf42733` (task/wave28-placement-wiring after scope correction 1).
All expected values come ONLY from the settled reference case `docs/reference-cases/R6B/cases/placement-building-b.json`
(step P8) and the law; no value is taken from a program run. This is an AI builder's work, not a professional review.

## What was built (the keystone, per scenario)

The placement/area-allocation feature is OPT-IN (threaded only when the engine bridge supplies the four lot
measures, as the rear-yard and envelope analyses are). When absent the document is byte-identical.

- **Engine wiring (5 files).**
  - `three_way_document.py`: new `PlacementInputs` dataclass + optional `placement_inputs` kwarg on
    `emit_three_way_document`; thin `_apply_placement` (calls Part-A `build_placement`) and `_apply_area_allocation`
    (calls Part-A `build_area_allocation`); `_placement_applied` gates `_apply_first_option`. Logic stays in the
    Part-A modules and geometry.py (this file is a thin wiring layer).
  - `result_way_engine_bridge.py`: `_placement_inputs_for` assembles the four measures each on its own basis — the
    printed-tax-map pair from the recorded PLUTO lot facts (lotfront 100.76 / lotdepth 100), the city-map (GIS)
    frontage from the prepared outline's Northern Boulevard edge (103.8792), the GIS depth from the lot-reach measure
    (99.9747). NEVER the scope's `lot_front_ft` (a GIS figure mislabelled approximate_tax_map, DB-260). Threaded on the
    `run_engine_and_result_ways_from_evidence` (route/journey) path only, gated on the DCM street window.
  - `geometry.py`: `build_placed_floor_plates` / `place_building_on_geometry` draw the footprint in the corner on the
    placement frontage within the measured lot outline (3 plates) and return the floor-by-floor rows the drawings
    pair with (check C-4). The footprint is a corner parallelogram along the two confirmed street edges; its drawn
    area 6,716.57 reconciles with the plate 6,716.67 within the readers' half a square foot.
  - `first_option_results.py`: `placement_applied` drops the "Where the plan sits on the lot" not-checked line and the
    fit-note's placement clause once the building is placed (so page 5/6 agree with the placed footprint).
  - `results_way_rules.py`: the DB-248 way rule — the apartment figure must equal the stated share of the total within
    the display rounding (`allocation_share_mismatch`).
- **S1** the regenerated benchmark: `building_alternatives[0]` carries a placed placement (basis printed_tax_map,
  outline 100.76 × 66.66) and an area_allocation; `geometry.floor_plates` holds 3 drawn plates. Values match the
  reference case; cited from placement-building-b.json.
- **S2** real print (below): the building-not-placed sentence is gone, the massing plates draw, the area-illustration
  method appears; 1.4.0/absent-placement paths byte-identical (the whole feature is opt-in).
- **S3** C-4: 3 plate rows consistent with the 3-storey floor_by_floor; plates reconcile to 6,716.67 (±0.5).
- **S4** area_allocation emitted for every alternative; `fitted` true only when placement.status == placed; apartment+other=total.
- **S5** register renderer `--check` and `research_record_check --check` both PASS; calc-area-allocation and
  calc-first-placement entries exist with step P8 as the worked example and no human verdict.
- **S6** records revised: NB-01 rev 10, NB-06 rev 5 (three_way_document.py), NB-05 rev 8 (result_way_engine_bridge.py)
  — code-identity resync only, no reading changed; each dependency_assessment says so. NB-03 NOT revised (forbidden;
  rear_yard_checks.py untouched). NB-04 NOT revised (see limitations — its only staleness is close_frame_dimensions.py
  in the forbidden drawings/maps/, a pre-existing change not mine; the placement touches no NB-04 code path). No
  research_status changed, so README/RESEARCH_REQUESTS.md stay untouched (G-13 fires only on a status change).
- **S7** benchmark fan-out rebuilt (list below).
- **S8** label is exactly Illustrative; nothing reads complies/buildable/optimal/feasible; the not_checked list is
  complete and genuinely-unresolved facts stay unresolved (the GIS conflict stays not known).
- **S9** modularity_check `--check` PASS (failures 0). three_way_document.py is 790 SLOC (above the 750 justify warn,
  below the 1000 hard fail). Cohesion justification: the module's single responsibility is the additive
  engine-document→three-way-document transform; placement is the next additive emission block (after rear_yard and
  envelope). The geometry positioning and the Part-A arithmetic were kept out (in geometry.py / placement.py /
  area_allocation.py); the per-block emitters are thin. No new CI failure.
- **S10** DB-248 way rule + tests (equal / within-rounding / beyond-rounding / no-allocation) + mutation below.
- **S11** the bridge assembles the four measures each on its basis; input-state tests (all four / tax pair missing /
  GIS pair missing / neither) + the scope-frontage mutation, in `test_result_way_engine_bridge.py`.

## Input-state table (RULE 1 — no default stands for a fact)

| input state | placement result | basis "not known"? |
|---|---|---|
| all four measures given | placed; outline + GIS conflict shown | none |
| tax pair missing (frontage or depth None) | WITHHELD, no outline | not placed on the printed-tax-map basis |
| GIS pair missing (frontage/depth None) | placed on tax basis | GIS conflict basis not known (no GIS figures) |
| neither pair | WITHHELD | not placed on any basis |
| residential floor area None (area allocation) | no area_allocation emitted | — |
| residential floor area present | apartment = share×total; fitted follows placement | — |

Every optional fact is read by `is None`/equality, never truthiness. Tests: `test_s11_input_states_*`,
`test_db248_*`, and the Part-A module tests (M5-T182).

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider)

| check | exit | result |
|---|---|---|
| `ruff check .` (edited scenario/contracts files) | 0 | All checks passed |
| register renderer `--check` | 0 | register check PASSED (no issues) |
| `research_record_check.py --check` | 0 | PASS (NB-01/05/06 code_current True; NB-04 pre-existing stale, noted) |
| `modularity_check.py --check` | 0 | failures 0; three_way_document.py warn (justify) with recorded justification |
| `check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS (10812 files) |
| `validate_contracts.py` + `pytest .github/scripts/tests` | 0 | 23 schemas, 0 failures; 24 tests passed |
| focused api folders (first run) | — | tests/scenario/three_answers, contracts, journey, api, drawings, rules, cad — green after fixes |
| web vitest (the two benchmark pins) | 0 | 2 files, 28 tests passed |
| web `npm run lint` | 0 | 0 errors (2 pre-existing warnings, unrelated) |
| web `npm run typecheck` | 0 | tsc --noEmit clean |
| whole api `pytest -q` | see FINAL-SUITE below | — |

FINAL-SUITE: `cd services/api && pytest -q -p no:cacheprovider` → **3 failed, 10078 passed, 8 skipped** in 519.80s
(exit 0 under the flock wrapper). The 3 failures are EXACTLY the three out-of-scope report/drawing consumers listed
below (test_results_dxf, test_constraints_page, test_location_sheet) — all outside allowed_paths and not editable by
me; every in-scope test (the engine wiring, DB-248, S11, register, journey, benchmark fan-out, web) is green. A scope
correction is needed for those three (and the massing.svg snapshot) before the whole suite is green.

## Mutation proofs (then restored)

1. **placement written vs not** — removed `first["placement"] = placement` in `_apply_placement`; the journey test
   `test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture` FAILED (committed fixture carries the placement).
   Restored (ruff clean; register `--check` PASS confirms the byte-exact restore).
2. **fitted only when placed** — a doc with a withheld placement but `area_allocation.fitted=True` →
   `results_way_violations` returns `{'allocation_fitted_without_placement'}`; the placed benchmark has none. (data-level)
3. **DB-248 share rule** — disabled the `> _AREA_SHARE_TOLERANCE` comparison; `test_db248_share_beyond_rounding_is_flagged`
   FAILED (the beyond-rounding split passed without the rule). Restored (ruff clean; test passes again).
4. **plate count vs floor_by_floor (C-4)** — dropped storey-3's floor_by_floor row from the benchmark (3 plates, 2 rows);
   `load_drawing_input` raised `DrawingInputError('plates_rows_mismatch')` for floor 3 residential. (data-level)
5. **S11 scope frontage** — `compute_placement_geometry` with the scope frontage 103.88 (instead of PLUTO 100.76):
   frontage_conflict collapses 3.12 → 0.0 and the footprint changes, so the reference-case figures no longer hold
   (committed `test_s11_mutation_feeding_the_scope_frontage_collapses_the_conflict`).

## Benchmark fan-out from my own regeneration (`UPDATE_JOURNEY_FIXTURE=1` / `UPDATE_DXF_SNAPSHOTS=1` / `UPDATE_DRAWING_SNAPSHOTS=1`)

In scope (updated, all green):
- `recorded_215_16_northern_journey.json` (regenerated from the corrected engine), its `.dxf` and `.site_plan.svg` snapshots.
- `test_three_answers_three_way_emit.py` (w13: exclude placement-driven fields), `test_results_read_api.py`
  (no-street comparison), `test_results_contract_1_5_0.py` (`_strip_1_5_0_blocks` normalizes floor_by_floor /
  floor_plates / "Where the plan sits" / fit-note; `_total_mismatch_doc` moves `other` to isolate the total rule),
  `test_report_pages.py` (f7 "Shown on the site plan"; a3 dedupe on an unplaced copy), `test_report_appendix.py`
  (area-illustration method now present on the benchmark), `test_zoning_rule_review_register_calculations.py` (eight
  calc entries), `test_result_way_engine_bridge.py` (S11), `test_results_way_rules.py` (DB-248).
- test_lot_reach's text-scan import guard went red because my bridge docstring contained the literal `lot_reach`;
  fixed in-scope by rewording the bridge docstring (now "the spatial lot-reach measure").

OUT OF SCOPE — require a scope correction (add to allowed_paths), NOT edited by me:
- `services/api/tests/cad/test_results_dxf.py::test_no_note_when_everything_drawn_is_surveyed[recorded_215_16_northern_journey]`
  — the drawn floor plates on the un-surveyed benchmark now add an honest "Measurement status not stated ... (floor
  plates)" note; the test asserts no note. FIX: drop the benchmark from this parametrization (or assert the note).
- `services/api/tests/drawings/report/test_constraints_page.py::test_s8_no_building_placed_legend_on_site_sentence_on_scenario`
  and `test_location_sheet.py::test_s3_not_placed_sentence_scenario_only_legend_on_site` — the not-placed sentence /
  legend no longer appears on the placed benchmark. FIX: assert the placed state (or use an unplaced doc).
- `services/api/tests/drawings/kit/snapshots/recorded_215_16_northern_journey.massing.svg` — a NEW snapshot the massing
  now draws (the benchmark previously had no plates). Regenerate with `UPDATE_DRAWING_SNAPSHOTS=1 pytest tests/drawings/kit`
  and add to allowed_paths. (It exists untracked in my worktree; NOT committed, being outside allowed_paths.)

## Real print (TestClient POST /report, benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(window); no server)

`node apps/web/scripts/print-report-pdf.mjs` → `/tmp/claude-0/M5-T172/print/report.pdf`. Page count stays 10.
Compared every page with main's print (`print-main-86a450d4/report.pdf`) via `diff_pages.py`. Whole-document net content
delta (header + fingerprint ignored):
- REMOVED: "No building is placed on this plan yet…" (the not-placed sentence); page-5 chart "Not demonstrated"; the
  "Where the plan sits on the lot" open item (page 6/8); the dedupe pointer "A check of the same kind…" (only parking
  carries the honest sentence now).
- ADDED: page-5 chart "Shown on the site plan"; the page-10 appendix "Area-illustration method" block (the 0.60 share
  split, Illustrative, the plate measure statement); open-item cross-references renumbered on page 3.
- The massing (page 6) now draws the 3 plates; the document fingerprint changed (content changed). No page silently
  lost content (verified by a whole-document sorted text comparison). NOTE: the per-page header reads "Queens block
  7334, lot 70" vs main's "215-16 NORTHERN BOULEVARD…" — a print-HARNESS artifact (TestClient identity vs the
  preview-based main print), not a content change; the orchestrator's own preview print carries the address.

## What I could not check / limitations

- The 4 out-of-scope consumers above need a scope correction before the whole api suite is fully green; I did not edit
  them (outside allowed_paths).
- NB-04 is left at rev 3: its only stale code pin is `close_frame_dimensions.py` under the forbidden `drawings/maps/`,
  a change not mine; the placement touches no NB-04 code path, so I did not revise it (brief: NB-04 "only if you touch
  its measurement-basis reading"). `research_record_check --check` PASSES (it notes NB-04's staleness, does not fail).
- The record reviews are left `stale` (review_state) for the independent G1 delta review; I authored the code-identity
  resync + dependency assessment only (producer ≠ verifier).
- The register calc entries' automated_tests read "Not run" (the code identity changed this task; CI re-runs the
  deterministic register tests) — consistent with calc-preliminary-apartment-estimate.
</content>

## Round 2 (S12 + S13) — on top of the round-1b builder commit `b843f9b6`

One bounded follow-up round. No round-1b result changed; the emitted document is byte-identical.

### What changed and why

- **S12 — the placement wiring moved to a new focused module.** Round 1b left `three_way_document.py`
  at 790 SLOC, above the 750 justification line S9 forbids crossing. `PlacementInputs`,
  `_placement_applied`, `_apply_placement`, `_placed_floor_to_floor` and `_apply_area_allocation`
  moved VERBATIM into the new thin module
  `services/api/app/scenario/three_answers/placement_wiring.py` (116 SLOC). `three_way_document.py`
  imports the four names, keeps `PlacementInputs` importable at its old path (re-exported; the bridge's
  `from .three_way_document import PlacementInputs` still resolves — verified `PlacementInputs is` the
  bridge's object), and now sits at **704 SLOC** — at/under 750 with **no justify warning**
  (`modularity_check --check` reports only the lesser warn-band "consider the module boundary" signal,
  not "above the justification threshold"). No import cycle: `placement.py`/`area_allocation.py`/
  `geometry.py` import nothing back, and the contract-version string is passed in
  (`contract_version=CONTRACT_VERSION_REAR_YARD`) so `placement_wiring.py` never imports
  `three_way_document.py`. The new module contains no `result_way` text (test_result_ways.py scan clean).
- **Byte-identity proof.** Regenerated the benchmark JSON (`UPDATE_JOURNEY_FIXTURE=1`, 2 passed), the
  DXF snapshot (`UPDATE_DXF_SNAPSHOTS=1`, 25 passed) and the kit snapshots (`UPDATE_DRAWING_SNAPSHOTS=1`,
  481 passed) from the moved code: `git status` shows ZERO diff on
  `recorded_215_16_northern_journey.json`, `recorded_215_16_northern_journey.dxf` and
  `recorded_215_16_northern_journey.site_plan.svg`. The only new file is the massing snapshot (below).
- **S12 — register.** Four calculation entries that pin `three_way_document.py` were resynced to its new
  LF sha256 `3376f7b8…`, each with an `implementation_changed` event (`calculations_history` seq 65–68):
  `calc-first-placement` (rev 1→2) and `calc-area-allocation` (rev 1→2) ALSO now cite
  `placement_wiring.py` with its pinned hash `8a600b04…` (recomputed combined `code_identity_sha256`);
  `calc-preliminary-apartment-estimate` (rev 14→15) and `calc-first-building-option-complete` (rev
  15→16) resync `three_way_document.py` only. `calc-lot-coverage-by-portion` pins `geometry.py` (not
  changed in round 2) and is untouched. Markdown pages re-rendered by
  `render_review_register.py --write` (36 files rendered; only the 2 placement pages, the 2 resync
  pages, `REGISTER.md` and `HISTORY.md` changed); `--check` PASSED. automated_tests stay "Not run" for
  every resynced entry (stale code identity; CI re-runs the deterministic register tests).
- **S12 — evidence records.** `NB-01` (revision 10, unchanged) and `NB-06` (revision 5, unchanged) carry
  `three_way_document.py`'s new hash `3376f7b8…` in the SAME revision; a `dependency_assessment` line in
  each records that the wiring moved out to `placement_wiring.py` with no behaviour change (NB-01: the
  moved wiring is placement, not zoning-lot, logic — the ACRIS zoning-lot scope row is byte-identical;
  NB-06: the street-wall/setback/side-yard readings are untouched). No reading changed. The records'
  `review_state` stays `stale` for the independent G1 delta review (producer ≠ verifier).
  `research_record_check --check` PASSES.
- **S13 — the three placed-benchmark consumer tests (now in allowed paths).**
  - `test_results_dxf.py::test_no_note_when_everything_drawn_is_surveyed` — the placed benchmark draws
    floor plates read from the not_available `building_option` answer, so even when every available answer
    is surveyed the plates carry one honest note `"Measurement status not stated in the results, not known
    to be a survey (floor plates)"` sourced `/answers/building_option/status`. The test now ASSERTS that
    note for the benchmark (not hidden) and keeps "no note" for every other fixture.
  - `test_constraints_page.py::test_s8` — the not-placed sentence is GONE from the scenario sheet once
    placed (`NOT_PLACED_LINE not in scenario`); the site close-frame context MAP keeps its `No building
    placed` legend (that forbidden `drawings/maps` drawing draws no building massing — unchanged). Added
    explicit not-placed coverage: a floor_plates-withheld copy still carries the sentence on the scenario
    sheet only.
  - `test_location_sheet.py::test_s3` — `building_not_placed(benchmark)` is now `False`, sentence gone
    from the scenario sheet, legend still on site; a not-placed copy still shows the sentence on the
    scenario sheet only and never splices the document's reason text.
  - **Massing snapshot** `recorded_215_16_northern_journey.massing.svg` committed from
    `UPDATE_DRAWING_SNAPSHOTS=1`; it draws **three** plates (`data-plate …/entries/0,1,2`; Floor 1/2/3),
    checked, not guessed.
- **Pre-existing E501 fixed (in-scope file).** The full `ruff check .` (the api CI first step) surfaced
  three `E501` lines round 1b left in `test_result_way_engine_bridge.py` (an allowed-paths file; lines
  491, 560–561). Fixed behaviour-identically (one word dropped from a comment; one call wrapped) so the
  required `ruff check .` and CI pass. No logic changed.

### Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider; heavy runs under `flock`)

| check | exit | result |
|---|---|---|
| `cd services/api && python -m ruff check .` | 0 | All checks passed |
| `python tools/modularity_check.py --check` | 0 | failures 0; three_way_document.py 704 SLOC (warn band, NO justify warning); placement_wiring.py 116 SLOC |
| register renderer `--check` | 0 | register check PASSED (no issues) |
| `python3 tools/research_record_check.py --check` | 0 | PASS; NB-01/NB-06 code_current True |
| `python3 scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS: 10812 files |
| the three S13 tests (`-k` the three) | 0 | 14 passed |
| WHOLE api `pytest -q` (one run, under flock) | 0 | **10081 passed, 8 skipped, 0 failed** in 517.55s |

The round-1b 3 failures are now green; the whole api suite is fully green (zero failures).

## Round 3 (S14 + S15) — on top of the scope-correction-3 head `8585b6aa`

One small, bounded correction round closing the two G3 visual findings (F1, F2) and the G3 code
review's finding 1 (taken as required, S15). No value, reading or label changed; the benchmark
corner-lot results JSON, the DXF and the kit SVG snapshots are byte-identical (regenerated, zero git
diff). Only the report's page-5 status line and the appendix method change on the print.

### What changed and why

- **S14 (F1) — page 5 no longer claims a placement the site plan contradicts.** The page-5 chart
  status (`drawings_embed.allowance_bar_chart_svg`, `services/api/app/drawings/report/drawings_embed.py`)
  now has three honest states: `Not demonstrated` (nothing placed), `Worked out; not drawn` (placed
  but the site plan does not draw the footprint — this head) and `Shown on the site plan` (only once
  the footprint is actually drawn). The drawn condition is the single named predicate
  `site_plan_draws_placed_footprint()` (returns `False`, documented: the page-4 maps context close
  frame — `drawings.maps.site_context_plan` — still passes `not_placed_legend=True` and draws no
  footprint; M5-T173 part B flips this one predicate, reading the scene's drawn state, never a guess).
  Because the site plan does not draw the footprint on this head, the benchmark page-5 cell reads
  `Worked out; not drawn`.
- **S14 (F2) — the appendix method no longer asserts an absent drawing.** `_area_illustration_method`
  (`services/api/app/drawings/report/page_evidence.py`) keeps the method block (its facts — the share,
  the measure, the G-14 conversion statement — are honest on their own; CHOICE: keep, not omit, so the
  method stays documented and the appendix stays short, one reworded clause), but the drawing clause is
  made honest: unless `_area_illustration_drawn(results)` is true (returns `False`; M5-T173 part B draws
  the two-zone illustration) it reads `it is not yet drawn in this report; when drawn it will be shown
  as {zones inside the placed building footprint | a proportional bar …}` — never the present-tense
  `it is shown`, which sent a reader hunting for a figure that is not in the report.
- **S15 — one predicate decides 'placed'.** The page-5 `Where the plan sits on the lot` not-checked
  line (and the fit-note tail), the area-allocation `fitted` flag and the scenario sheet's not-placed
  sentence now all follow ONE placed-AND-drawn fact — never the four lot measures alone.
  - `geometry.footprint_drawable(geometry, frontage_street_name)` (new, `geometry.py`) is the corner
    test `place_building_on_geometry` applies (reuses `_frontage_lines`/`_footprint_outline`): true
    only when the frontage street and an adjacent street share a corner.
  - `placement_wiring._placement_drawn(geometry, placement_inputs)` (new) = the four measures present
    AND `footprint_drawable` — it predicts exactly whether the plates will be drawn.
  - `three_way_document.emit_three_way_document` now passes `placement_applied=_placement_drawn(...)`
    to `_apply_first_option` (was `_placement_applied` = four measures alone); `_placement_applied` is
    no longer imported there.
  - `_apply_area_allocation` reads the actual drawn outcome from the document
    (`_floor_plates_drawn`: `geometry.floor_plates.status == "available"`, the same fact
    `readers.building_not_placed` reads) and passes `placement_status` as placed only when the plates
    were drawn, so `fitted` is False on a placement whose footprint could not be drawn.
  - Result (verified by emit probe and the S15 test): a single-frontage lot (four measures present, no
    corner) keeps the line, has `fitted` False and keeps the not-placed sentence; the corner benchmark
    is unchanged (line dropped, `fitted` True) — byte-identical.
- **Register + evidence records resynced (code-identity only, no reading/value changed).** The five
  calculation entries pinning an edited module were resynced to its new LF sha256 with an
  `implementation_changed` event each (`calculations_history` seq 69–73): `calc-lot-coverage-by-portion`
  (rev 11→12, geometry.py), `calc-preliminary-apartment-estimate` (15→16, three_way_document.py),
  `calc-first-building-option-complete` (16→17, three_way_document.py), `calc-first-placement` (2→3,
  three_way_document.py + placement_wiring.py + geometry.py), `calc-area-allocation` (2→3,
  three_way_document.py + placement_wiring.py); Markdown re-rendered by `render_review_register.py
  --write`. NB-01 (revision 10, unchanged) and NB-06 (revision 5, unchanged) carry three_way_document.py's
  new hash `cb9695bf…` with a dependency-assessment line recording the S15 predicate change; no reading,
  value or status changed, so the README status cell and RESEARCH_REQUESTS.md index are untouched
  (G-13 fires only on a status change). The records' `review_state` stays `stale` for the independent G1
  delta review (producer ≠ verifier). NB-05 pins only result_way_engine_bridge.py (not edited) and is
  untouched.

### Real print comparison (TestClient POST /report, benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(window); no server, no ports)

`node apps/web/scripts/print-report-pdf.mjs` → `/tmp/claude-0/M5-T172-r3/report.pdf`; 10 pages, same as
before. Compared every page with `print-e79ddbc6/report.pdf` via `diff_pages.py`. The two MATERIAL
content changes, exactly as the brief allows:
- **page 5:** `Placed on site  Shown on the site plan` → `Placed on site  Worked out; not drawn` (F1).
- **page 10 (appendix):** `… it is shown as zones inside the placed building footprint. …` → `… it is
  not yet drawn in this report; when drawn it will be shown as zones inside the placed building
  footprint. …` (F2).

Every other per-page line in the diff is a print-HARNESS artifact (NOT a code change), identical on all
10 pages and already documented in the round-1 report: the per-page header reads `Queens block 7334,
lot 70` (TestClient identity) vs e79ddbc6's `215-16 NORTHERN BOULEVARD, Queens · block 7334, lot 70`
(the orchestrator's preview print resolves the address), and page 9's run-identity block reads `Code
commit: unknown` (no git commit env in the TestClient harness) vs e79ddbc6's pinned hash. No page lost
or gained content; page count stays 10.

### Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider; heavy runs under `flock`)

| check | exit | result |
|---|---|---|
| `cd services/api && python -m ruff check .` (lanes venv) | 0 | All checks passed |
| `python tools/modularity_check.py --check` | 0 | failures 0; three_way_document.py in the warn band, NO justify warning (under 750 SLOC) |
| register renderer `--check` | 0 | register check PASSED (no issues) |
| `python3 tools/research_record_check.py --check` | 0 | PASS; NB-01/NB-05/NB-06 code_current True |
| `python3 scripts/lanes/check_lane_paths.py --coverage` | 0 | LANE COVERAGE PASS: 10843 files |
| journey fixture regen (`UPDATE_JOURNEY_FIXTURE=1`, 2 passed) | 0 | benchmark JSON + DXF + SVG snapshots byte-identical (zero git diff) |
| touched test files (comparison/appendix/pages/geometry_streets/emit) | 0 | 141 passed |
| WHOLE api `pytest -q` (one run, under flock) | 0 | **10103 passed, 8 skipped, 0 failed** in 512.09s |

### Mutation proofs (then restored)

1. **drawn predicate forced true (S14).** `site_plan_draws_placed_footprint()` → `return True`:
   `test_s14_benchmark_placed_on_site_reads_worked_out_not_drawn` FAILED (page 5 said `Shown on the
   site plan` again; `assert "Worked out; not drawn" in comparison` failed). Restored (drawings_embed.py
   back to its edited state, LF sha256 `f3456225…`).
2. **old measures-only predicate restored (S15).** emit line back to
   `placement_applied=_placement_applied(placement_inputs)`:
   `test_s15_one_predicate_decides_placed_corner_vs_single_frontage` FAILED
   (`assert 'Where the plan sits on the lot' in [...]` — the line was dropped on the single-frontage
   lot). Restored (three_way_document.py sha back to `cb9695bf…`, matching the register/records).
