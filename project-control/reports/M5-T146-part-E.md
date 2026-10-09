# M5-T146 PART E producer report - the committed document regenerated once

Producer: rules-engineer (an AI agent). Base: `f804ab50e6e555d1679805e7b7549f2a838bea6c`. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-ad1180e48b762c831`.

PART E regenerated the committed benchmark results document ONCE, with the journey test's own
update switch, and made the journey, read-route, drawings and CAD tests that read it pass. The
server content tests were updated for the additive 1.4.0 blocks. Done AFTER PART B and its tests
passed.

## What I changed, file by file
- `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` - regenerated
  ONCE by `UPDATE_JOURNEY_FIXTURE=1 pytest tests/journey/test_215_16_northern_journey.py`, never by
  hand.
- `services/api/tests/journey/test_215_16_northern_journey.py` - the version assertion is now 1.4.0;
  added assertions that building_option points to the list, building_alternatives = [building B]
  (conditional, with its floor schedule and preliminary capacity estimate), and coverage_by_portion
  is withheld carrying NO number (S21/S8/S9/S10/S7/S24).
- `services/api/tests/api/test_results_read_api.py` - `test_t3` now asserts 1.4.0 and that the route
  serves `building_alternatives` (= [B], estimate label 'Preliminary capacity estimate') and a
  withheld `coverage_by_portion` (S23). The reference-document equality still holds (same entry).
- The two snapshots `recorded_215_16_northern_journey.site_plan.svg` and
  `...results_dxf/recorded_215_16_northern_journey.dxf` were NOT changed: their tests show they do
  NOT follow (S22). The geometry block is unchanged (no footprint, no floor plates; the
  `max_lot_coverage` value and geometry.envelope reason are byte-identical), so both snapshots are
  byte-identical and their tests pass.

## The regenerated document's diff, key by key (91 insertions, 6 deletions)
- `contract_version`: "1.3.0" -> "1.4.0" (carrying a 1.4.0 block binds the version).
- `answers.building_option`: reason changed to "The single building option is not shown; the worked
  first-building alternatives are listed in building_alternatives (none is preferred or a default)";
  the now-stale `gap_kind` / `resolved_by` keys dropped. Status stays `not_available` (S8).
- NEW top-level `coverage_by_portion`: withheld, gap_kind `missing_information`, the law by portion,
  NO number (S7).
- NEW top-level `building_alternatives`: [building B] - 3 storeys of 6,716.666..., 20,150 total,
  30 ft, way conditional (contradicted_record + unchecked), its preliminary capacity estimate
  17.27-21.59, and a label stating the plan fits at the lowest ratio (8,060 >= plan) (S9/S11).
- EVERYTHING else byte-identical: floor_area_allowance, permitted_envelope (incl. `max_lot_coverage`
  withheld), unit_estimate (reserved), geometry (all layers), scope, rule_versions. (S21/S24)

## Scenarios
| Scenario | Expected | Test |
|---|---|---|
| S21 | regenerated document declares 1.4.0; building B + estimate; footprint, building A and the legal limit withheld/absent; journey passes | `test_215_16_northern_journey.py::test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture` |
| S22 | site_plan.svg and .dxf byte-identical (geometry unchanged); their tests pass | `tests/drawings` + `tests/cad` for `recorded_215_16` (byte-identical; unchanged) |
| S23 | the read route serves building_alternatives + the estimate; test passes | `tests/api/test_results_read_api.py::test_t3_route_document_equals_the_entry_document` |
| S24 | drawings and document agree on what is withheld; nothing drawn carries a withheld figure | journey asserts coverage_by_portion carries no number; the geometry omits exactly the footprint/plates that are withheld |

## Checks, one at a time, with direct exit codes
- regenerate: `UPDATE_JOURNEY_FIXTURE=1 pytest -q tests/journey/test_215_16_northern_journey.py` ->
  2 passed (exit 0); then WITHOUT the switch -> 2 passed (exit 0), so the committed fixture matches.
- `pytest -q tests/journey tests/api/test_results_read_api.py tests/documents/test_pdf_content.py`
  -> 167 passed (exit 0)
- `pytest -q tests/drawings tests/cad -k "not synthetic"` -> only the two PRE-EXISTING Part A
  failures remain (`test_street_names_...`, `test_snapshots_are_ascii_...`), both present at the
  base; `recorded_215_16` passes in all drawings/CAD tests (its snapshots are byte-identical).
- `python .github/scripts/validate_contracts.py` -> the regenerated document validates as a 1.4.0
  `results` fixture; 0 failures (exit 0).

## STOP / doubt
- S22's "byte-identical snapshots" holds for `recorded_215_16` (my only fixture change) because the
  geometry block and the `max_lot_coverage` reason are unchanged - the 1.4.0 blocks are additive and
  the drawings/CAD renderers do not read them.
- The ~44 CAD/drawings failures on Part A's synthetic fixtures are PRE-EXISTING (base RED) and NOT
  caused by PART E; the full detail and the four out-of-scope seam files are in `M5-T146-part-B.md`.

## Correction before review (ruling W11; second orchestrator round)

The benchmark document was regenerated ONCE more (the journey test's `UPDATE_JOURNEY_FIXTURE=1`
switch) after the W11 corrections. The recorded_215_16 DXF snapshot was regenerated once
(`UPDATE_DXF_SNAPSHOTS=1`); its SVG is byte-identical. The W11 logic and the mutation proofs are in
`M5-T146-part-B.md`.

### Every key that changed in the regenerated document, and why
- `answers.permitted_envelope.value_states.max_lot_coverage`: reason/gap_kind/resolved_by rewritten
  to AGREE with `coverage_by_portion` (W11 a) - was "beyond the corner-lot portion ... computing per
  portion" / `work_owed`; now the block's "the two lot areas disagree ... law by portion" /
  `missing_information` / "A survey or deed ...". No figure either way.
- `geometry.envelope.reason` + `reason_kind`: reconciled to that same coverage reason /
  `missing_input` (W11 a) - the envelope layer draws the footprint, so its reason must agree. No new
  geometry; still nothing drawn.
- `unit_estimate.reason`: was "Not known ... not built yet"; now "Not shown here. Each worked
  building's preliminary capacity estimate is given in building_alternatives." (W11 b). Status and
  reason_kind unchanged.
- `floor_stack.reason`: was "... worked out from the building option ... neither is known"; now
  "Not shown here. Each worked building's floor schedule is given in building_alternatives." (W11 b).
- `building_alternatives[0].label`: shortened to "Building B: the fewest storeys reaching the
  minimum base height" (W11 c).
- `building_alternatives[0].fit_note`: NEW key - the sentence that the plan fits at the lowest ratio
  (8,060 >= plan), moved out of the label (W11 c).
- Everything else byte-identical: floor_area_allowance, the other envelope value states, scope,
  rule_versions, geometry's other layers, the rest of building B, coverage_by_portion, building_option.

### The regenerated DXF snapshot (recorded_215_16)
One text changed: `geometry.envelope`'s reason, reconciled to the coverage block (W11 a). No new
entity, layer, footprint or floor plate; it still draws the lot outline only. The SVG snapshot is
byte-identical (the coverage reason is not rendered in the SVG). S22/S24 hold: the drawing omits
exactly the footprint/plates the document withholds.

### The synthetic fixtures' snapshots (W10 #5/#6)
They have `not_available` geometry: `Unavailable` from every renderer, so there is no snapshot to
generate and nothing to draw. They are excluded from the drawing/CAD parametrisations by the
`fixture_paths()` drawable-only filter (see `M5-T146-part-B.md`); tests/drawings and tests/cad are
green (1359 passed).

END-OF-REPORT
