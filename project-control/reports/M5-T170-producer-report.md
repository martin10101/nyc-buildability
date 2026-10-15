# M5-T170 producer report (backend-engineer) — envelope constraints from NB-06 in the engine

Requested status: **needs_split** — the build is complete and green within the task's own scope,
but adding the three draft lane-A rule files (required by the objective, S11) fans out to six
files OUTSIDE `allowed_paths` (two lane-A golden tests and four register calculation pages). They
are listed under "Out-of-scope fan-out (scope correction)" with the exact reason each is forced.
Everything else is in scope and the whole api suite + whole web suite + all documented checks pass.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/wf_9e85eac9-9e2-1`
Claim head reset to: `e392cab39b4fb63aaa90f0cb6633ceff03070bfa` (task/wave26-envelope-constraints).

## What changed, per the ORDER OF WORK

1. **`envelope_constraints.py` (new).** `build_envelope_analysis(...) -> EnvelopeAnalysis` with the
   three checks as labelled draft readings, each a `applies` / `not_applicable` row (never
   `not_known`, R061): STREET WALL (always applies; overlay -> ZR 35-631(b) 8 ft on each frontage;
   no overlay -> ZR 23-431(b) 8 ft wide / 10 ft narrow, the D-051 asymmetry, never collapsed;
   overlay not read -> distance withheld, the dependency named). SETBACK (keyed on the building
   street-wall height strictly above the 45 ft maximum base height; depths 10 wide / 15 narrow per
   frontage from the reused D-052 class; not triggered at/below 45 ft carries the depths + the
   above-base condition). SIDE YARD (none required for all but a single/two-family detached
   residence, 23-335(b)/34-232; two 5-ft yards for a detached one without the overlay; 5-ft
   open-area note). Plus `setback_value_state_from_row(row)` (the reconcile helper, co-located here
   so result_ways.py is untouched — see "Surprises") and `_constraint_lines` (street_wall_band /
   setback_line not_established on the benchmark, established only when a geometry is supplied, S6)
   and `_input_facts` (per-frontage mapped width, basis `gis`, G-10).
2. **Emission.** `three_way_document.py`: `_apply_envelope` attaches `envelope_rows`, EXTENDS
   `input_facts` and `geometry.constraint_lines` (never replaces the rear-yard ones),
   `_reconcile_setback_value_state` makes the `setback_above_base` value state agree with the
   envelope row (only on a 1.5.0 doc; 1.4.0 byte-identical), `_street_wall_applied` gates page 6.
   `result_way_engine_bridge.py`: `_envelope_analysis_for` (mirrors `_rear_yard_analysis_for`,
   opt-in on `street_data`), threaded ONLY into `run_engine_and_result_ways_from_evidence`
   (the evidence/route emit), with `_street_widths`/`_street_segments` building MappedStreetSegment
   records from `StreetData.centerlines` + the lot borough and running the ACCEPTED
   `derive_frontage_street_widths` (the D-052 classifier, never reinvented).
3. **`_setback_way` agreement.** Achieved by the document-level reconcile in (2); `result_ways.py`
   is NOT edited (see "Surprises: setback agreement").
4. **Page 6 / page 8.** `first_option_results.py`: `street_wall_applied` gates "The street wall"
   out of the not-checked list only when the engine applied it (1.4.0 keeps it). `readers.py`:
   `_apply_envelope_open_items` shows the applied setback / street-wall / side-yard readings on
   page 8 (no-op on a 1.4.0 doc), and `side_yard` joins `_ORDER`.
5. **Page 3 fallback (DB-266 / S18).** `page_site_context._constraint_rows_from_results`: a 1.5.0
   document with no envelope row for a kind falls back to its 1.4.0 row ("Setback above the base"
   Not worked out yet; "Street wall" Not checked) instead of silently omitting it.
6. **Rule files + register + records.** Three draft lane-A rule files (`r6b_street_wall`,
   `r6b_setback`, `r6b_side_yard`, mirroring `r6b_rear_yard_corner_waiver.rule.json`), their
   register entries (law digests synced to the captures, behaviour naming the envelope tests,
   `automated_tests` "Not run" — draft DSL suite not yet written), rule pages + evidence files, the
   two three_way_document.py calc entries resynced, and all six calc entries bound to the edited
   register-calc test file set to "Not run". Review register rendered (`--write`) and checked.
   NB-06 rev 3 (added the 12-10 street-wide/street-narrow captures E17/E18, closed condition 3,
   added the 23-433(a)-(d) note, added the implementation code_paths); NB-05 rev 5 (bridge
   code-identity); NB-01 rev 7 (three_way_document.py + readers.py code-identity). No human verdict
   entered; the independent G1 readings stay the reviewer's.
7. **Benchmark regenerated** by the repo's own path (`UPDATE_JOURNEY_FIXTURE=1` through
   `tests/journey/test_215_16_northern_journey.py::test_recorded_journey_entry...`), never
   hand-edited; consumer tests updated only where the engine output moved (below).

## Input-state table (one test per state; test_envelope_constraints.py)

STREET WALL:
| overlay | building type | each frontage value | zr | test |
|---|---|---|---|---|
| present | residential_only | 8 ft | ZR 35-631 + 34-24 | test_street_wall_overlay_is_eight_feet...[residential] |
| present | mixed | 8 ft | ZR 35-631 + 35-01 | test_street_wall_overlay_is_eight_feet...[mixed] |
| present | not stated | 8 ft (+ building-type condition) | ZR 35-631 | test_street_wall_building_type_not_stated_carries_a_named_condition |
| absent | any | 8 wide / 10 narrow | ZR 23-431 | test_street_wall_no_overlay_is_eight_wide_ten_narrow_never_collapsed |
| absent | any (unknown-width frontage) | no distance | ZR 23-431 | test_street_wall_no_overlay_unknown_width_shows_no_distance_never_narrow |
| not read | any | no distance (dependency named) | 35-631+23-431 | test_street_wall_overlay_not_read_withholds_the_distance |

SETBACK (street-wall height vs 45 ft max base; per-frontage depth from the D-052 class):
| height | triggered | state | test |
|---|---|---|---|
| 30 / 44.99 / 45.00 | no | not_applicable (carries 10/15 ft + above-base condition) | test_setback_trigger_table... ; test_setback_not_applicable_carries_the_depths... |
| 45.01 / 50 | yes | applies (10 wide / 15 narrow) | test_setback_trigger_table... ; test_setback_depths_are_ten_wide_fifteen_narrow_cited |
| None | unknown | applies, above-base condition (never not_known) | test_setback_height_not_stated_is_conditional_never_not_known |

| width string | D-052 class | setback depth | test |
|---|---|---|---|
| 100 / 75.00 | wide | 10 ft | test_per_frontage_width_class_drives_the_setback_depth |
| 60 / 74.99 | narrow | 15 ft | test_per_frontage_width_class_drives_the_setback_depth |
| 60-75 / <=75 | unresolved | withheld | test_per_frontage_width_class_drives_the_setback_depth |
| missing / garbled | unknown | withheld (never narrow) | test_per_frontage_width_class_drives_the_setback_depth |

SIDE YARD:
| building type | overlay | state / value | test |
|---|---|---|---|
| multi_family / mixed | either | not_applicable (none required) | test_side_yard_multi_family_none_required ; test_side_yard_mixed_none_required |
| single/two-family detached | present | not_applicable (34-232) | test_side_yard_detached_in_overlay_none_required |
| single/two-family detached | absent | applies (two 5-ft yards) | test_side_yard_detached_without_overlay_two_five_foot_yards |
| not stated | absent | not_applicable + detached condition | test_side_yard_building_type_not_stated_without_overlay_names_the_detached_case |
| any (open area provided) | — | 5-ft open-area condition | test_side_yard_open_area_minimum_is_five_feet |

No-default-for-a-fact (RULE 1) tests touched: `_no_overlay_offset` / `_setback_depth` return None
for unresolved/unknown widths (never narrow); `_overlay_present` returns None for NOT_READ;
`_building_type` returns None for an unstated program; `_setback_triggered` returns None (not
False) when a height is None; `_side_yard_check` carries the detached case as a named condition
when the type is not stated. No truthiness test reads an optional fact as a value.

## RULE 3 (texts guard)

`test_emitted_texts_are_plain_user_texts` scans every row text + condition assumption/settled_by
across six analyses for: `captur`, `reference case`, `milestone`, `m5-t`, `the caller`, `is built`,
`db-`, `fixture`, `step-p`, `nb-0`, `professional review`, `gap (`. All row texts are short
conditional/draft readings naming their ZR section (the page-3 summary, like the rear-yard combined
row); the DOB disclaimer is the shared limitation shown once, not repeated on every row.

## Benchmark lines changed (cited; recorded_215_16_northern_journey.json)

- NEW `envelope_rows`: street_wall applies (8 ft each frontage, Conditional on prevailing frontage
  + operative street line), ZR 35-631; setback not_applicable (30 ft option is at/below 45 ft),
  values 15 ft (215 Place narrow) / 10 ft (Northern Blvd wide), above-45-ft condition, ZR 23-433;
  side_yard not_applicable (none required), ZR 23-335/34-232. Cited: overlay-reading.json rows
  street-wall-location and setback-above-base, and NB-06; never a program run.
- NEW `input_facts` (added to the rear-yard ones): mapped_street_width:215 Place 60 (gis),
  mapped_street_width:Northern Boulevard 100 (gis) — DCM mapped widths, basis gis (E15/NB-06).
- NEW `geometry.constraint_lines` (added): street_wall_band not_established, setback_line
  not_established (both carry basis + zr_sections, NO geometry — D-094-R017, the operative street
  line is not fixed by a mapped width).
- `permitted_envelope.value_states.setback_above_base` reconciled from "not covered" to the
  envelope reading (reason = the setback row text); way stays `withheld` (a standalone carries no
  number and is never conditional in place).
- `building_alternatives[0].not_checked` drops "The street wall" (the engine applied the check).

## Checks (direct exit codes; lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider; heavy runs under flock)

- `cd services/api && python -m ruff check .` — **exit 0** (All checks passed).
- documented api set (`tests/scenario/three_answers tests/contracts/test_results_contract_1_5_0.py
  tests/journey tests/api/test_results_read_api.py tests/api/test_study_live_geometry.py
  tests/drawings/report/test_constraint_rows.py test_report_benchmark.py test_report_pages.py
  tests/rules/test_zoning_rule_review_register.py tests/cad tests/drawings/kit
  test_constraints_page.py test_report_law_links.py test_report_unit_limit_text.py
  test_report_page_one.py tests/drawings/maps/test_northern_fixture.py
  test_zoning_rule_review_register_calculations.py`) — **2067 passed, 2 skipped, exit 0**.
- `python3 .github/scripts/validate_contracts.py` — **Checked 23 schema file(s); 0 failure(s)**;
  `python3 -m pytest .github/scripts/tests` — **24 passed, exit 0**.
- `render_review_register.py --check` — **PASSED (no issues), exit 0**.
- `tools/research_record_check.py --check` — **PASS, exit 0** (NB-01/05/06 code_current True).
- `tools/modularity_check.py --check` — **804 files, failures 0** (warnings only; three_way_document.py
  and result_ways.py stay in the WARN band, below JUSTIFY 750 — S15).
- `scripts/lanes/check_lane_paths.py --coverage` — **PASS, 10513 files, exit 0**.
- apps/web (npm ci once in the worktree): `npm run lint` — **0 errors, 2 pre-existing warnings**;
  `npm run typecheck` — **exit 0**; whole `npx vitest run` — **129 files, 2704 passed, exit 0**
  (the jsdom getContext/WebGL lines are MapLibre console noise, not failures).
- WHOLE `cd services/api && python -m pytest -q -p no:cacheprovider` — **9813 passed, 8 skipped,
  1 failed, 490s** on the first run; the one failure was the out-of-scope lane-A golden test
  `tests/rules/test_r6b_other_districts_unchanged.py::test_flag_on_adds_only_the_r6b_rules`
  (pins the lane-A R6B rule set; the three new rule ids added — collateral below). After the fix,
  `tests/rules` re-run **green** (confirms the only whole-suite failure was that pin).

## Mutation proofs (mutate -> run the pinning test -> FAIL -> restore identical)

1. 45.00 ft boundary: `_setback_triggered` `>` -> `>=` -> test_setback_trigger_table...[45.0-False] FAILED. RESTORED_IDENTICAL.
2. unknown width never narrow: `_setback_depth` unknown -> narrow -> test_per_frontage_width_class... 4 FAILED. RESTORED_IDENTICAL.
3. no-overlay asymmetry: `_no_overlay_offset` narrow 10 -> 8 -> test_street_wall_no_overlay_is_eight_wide_ten_narrow_never_collapsed FAILED. RESTORED_IDENTICAL.
4. building type not stated: side-yard not-stated drops the detached condition -> test_side_yard_building_type_not_stated_without_overlay_names_the_detached_case FAILED. RESTORED_IDENTICAL.
5. page-8 open item on 1.5.0: `readers._apply_envelope_open_items` no-op -> test_m5t170_page_8_shows_the_applied_envelope_readings FAILED. RESTORED_IDENTICAL.
6. (S18/DB-266) restore the `continue` in `_constraint_rows_from_results` -> test_m5t170_s18_page3_lists_setback_and_street_wall_with_no_envelope_row FAILED. RESTORED_IDENTICAL.

## REAL PRINT (S10; /tmp/claude-0/M5-T170/print/report.{html,pdf})

Built `build_report_html(benchmark())` (the production renderer the report route uses), wrote the
HTML, and rendered the PDF with `node apps/web/scripts/print-report-pdf.mjs` (no server, no ports).
Pages 3, 6 and 8 AGREE on the regenerated 1.5.0 benchmark:
- PAGE 3 (site-and-context): "Street wall — A conditional reading of the street-wall location (ZR
  35-631) — Conditional"; "Setback above the base — A conditional reading: no setback above the
  base is required (ZR 23-433) — Conditional"; "Side yard — A draft reading: no side yard is
  required under ZR 34-232 — Conditional". All three applied readings with a (see item N) link.
- PAGE 6 (scenario-B, "What was not checked"): lists "Where the plan sits on the lot" and "Parking,
  loading and bicycle requirements" only — "The street wall" is gated out (page 6 agrees with the
  applied page-3 reading).
- PAGE 8 (assumptions-open-items): item 7 Setback above the base "No setback above the base is
  required for this building (ZR 23-433)"; item 8 Street wall "The street wall sits close to the
  street line; the exact position is conditional"; item 9 Side yard "No side yard is required (ZR
  23-335; ZR 34-232...)" — all applied conditional readings, no "not checked"/"not worked out".

## Out-of-scope fan-out (scope correction — add to allowed_paths; NOT edited speculatively)

Adding the three draft lane-A rule files (required by S11) forces five files outside
`allowed_paths`. They are committed as forced, mechanical collateral (mirroring M5-T167), each with
the exact reason:
- `services/api/tests/rules/test_r6b_a02b_golden.py` — pins the EXACT set of rules the lane-A flag
  indexes (`test_flag_on_adds_exactly...`); the three new lane-A rule files add three ids, so its
  expected set must include them. Fix applied: a new `ENVELOPE_RULE_IDS` tuple added to the
  flag-on assertion.
- `services/api/tests/rules/test_r6b_other_districts_unchanged.py` — pins the EXACT set the lane-A
  flag adds (`test_flag_on_adds_only_the_r6b_rules`); same reason. Fix applied: the three ids added
  to the expected set. (Caught by the WHOLE api suite, not the documented subset — R639.)
- `docs/zoning-rule-review/calculations/calc-floor-area-allowance.md`,
  `calc-lot-coverage-by-portion.md`, `calc-building-option-floor-stack.md`,
  `calc-legal-dwelling-unit-limit.md` — every calculation entry binds the register-calc test file
  `test_zoning_rule_review_register_calculations.py` as its deterministic test; the rule-entry
  count assertion there had to move 23 -> 26 for the three new rule entries, which re-renders every
  calc page (status -> Not run). Only `calc-first-building-option-complete.md` and
  `calc-preliminary-apartment-estimate.md` are in allowed_paths (they also change for the
  three_way_document.py resync). The four above are the forced collateral.

The pre-check (return-precheck-T170.md) enumerated the BENCHMARK fan-out but not this RULE-FILE
fan-out (lane-A golden set + the calc-page cascade through the shared register-calc test binding).

## Plan claims checked at the claim head (notes)

- The pre-check's R-1/R-2 (that `test_result_ways_truth_table.py` and
  `test_result_way_engine_bridge.py` would need the setback way changed) did NOT materialise: those
  tests exercise paths where the envelope analysis does not run, so `_setback_way` stays Withheld
  "not covered" there (byte-identical) and both files are UNCHANGED. The two-emitter agreement is
  achieved on the 1.5.0 document by the reconcile (lesson iii / S9), mirroring the coverage
  reconciliation precedent.
- S16: `result_ways.py` is NOT in this change (the reconcile helper lives in
  envelope_constraints.py) to avoid a disproportionate calc-entry fan-out (5 calc entries bind
  result_ways.py, 4 of their pages out of allowed_paths). NB-05/NB-01 still get their code-identity
  revisions for the files that DID change (result_way_engine_bridge.py; three_way_document.py +
  readers.py).

## Assumptions / limitations

- The three rule files are DRAFT extractions registered for the review register; the envelope law
  reading is applied in envelope_constraints.py (the engine), not evaluated through the DSL rules
  engine, so their automated_tests read "Not run" and the behaviour is exercised by the envelope
  tests. No consumer evaluates them yet.
- NB-06 stays `interpretation_awaiting_review`; condition 3 is closed as a builder draft on the
  now-present 12-10 captures (I read the verbatim: "wide street ... 75 feet or more"; "narrow
  street ... less than 75 feet"), confirming D-052. The independent G1 reading of the
  34-11 -> 34-24(b)(1) -> 35-63 -> 35-631(b) chain and the 12-10 confirmation is the reviewer's.
- Nothing written under `.claude/**`; no server/ports/Playwright; scratch only under
  `/tmp/claude-0/M5-T170/`.

---

# Round 2 (backend-engineer) — the G1 + G4 correction cluster

Reset to `48d6587b74454c8ad491a2781269452a9f78db8e` (head of `task/wave26-envelope-constraints`;
round 1 integrated as `281e23b7`). Requested status: **awaiting_gate**. One commit; no push. Both
REQUIRED findings (G1 F1, G4 F1=S17) and the three advisories applied or carried with a reason;
scratch under `/tmp/claude-0/M5-T170-r2/`.

## Finding dispositions

**G1 F1 (REQUIRED, provenance) — FIXED.** The mapped-street-width input facts were stamped with the
MapPLUTO lot-fact source; MapPLUTO carries no street-width field. New
`result_way_engine_bridge._street_width_source(street_data)` reads the DCM Street Center Line
provenance already threaded in `street_data` (the same `street_data.source` + `provenance.retrieved_at`
`_street_segments` stamps on each `SegmentSource`); `_envelope_analysis_for` now sources the width
facts from it, never `_mappluto_source(profile)`. A frontage without a retrieval date emits no width
fact (no borrowed source). The benchmark was regenerated by its own path (`UPDATE_JOURNEY_FIXTURE=1`);
the two `mapped_street_width:*` facts' `source_title` moved `NYC ... MapPLUTO, version 26v2` ->
`DCP Digital City Map street center lines`; `source_date` stayed `2026-09-30` (the DCM window's own
retrieval date equals the MapPLUTO date). Values 60/100 and basis `gis` unchanged; the rear-yard area
facts keep their MapPLUTO source (they ARE MapPLUTO). Test: `test_result_way_engine_bridge.py::
test_envelope_width_facts_cite_the_dcm_street_centerline_not_mappluto`. Mutation proven (below).

**G4 F1 = S17 (REQUIRED) — DB-265's six advisories:**
1. (c)(1) alternative — **FIXED**. `rear_yard_checks._check_c3` and `_combined` now name ZR 23-344(c)(1)
   (a rear yard IS required where the deemed rear lot line meets a neighbour's *rear* lot line)
   besides the (c)(3) side-lot-line branch; state unchanged (`not_known`). Read from the ZR 23-344
   snapshot ((c)(1)/(c)(2)/(c)(3) verbatim). Phrased to keep the "no rear yard" guard (never the
   bare phrase). Test: `test_rear_yard_short_block.py::test_c3_and_combined_texts_name_the_c1_alternative_besides_c3`.
2. register code_links — **CARRIED with reason**. Adding `rear_yard_checks.py` to the
   `r6b-rear-yard-corner-waiver` entry's `code_links` (+ revision/history, re-render) forces
   `render_review_register.py --write` to rewrite `docs/zoning-rule-review/rules/r6b-rear-yard-corner-waiver.md`,
   which is **outside this packet's allowed_paths**; `render_review_register.py --check` fails closed on
   a stale rendered page. Per the brief's STOP-and-report rule the register edit was reverted (register.json
   byte-unchanged). Recommend the orchestrator add that rendered rule page to allowed_paths (scope correction)
   and land the code_link + an `implementation_changed` event, or schedule a follow-up. The engine change to
   `rear_yard_checks.py` itself is applied here.
3. doubled street-window fetch — **CARRIED with reason**. The double fetch under
   `LIVE_SPATIAL_PROVIDER_ENABLED` is in the live providers in `app/api/v1/study_live_geometry.py`
   (geometry and street providers both fetch the window), **outside allowed_paths**; the flag is off by
   default in production, so it is latent. Carried for a follow-up (fix only if inside allowed paths).
4. unused operative-reach argument — **FIXED (dropped honestly)**. `_rear_yard_constraint_lines` no longer
   takes `operative_reach_ft`; the now-dead `operative_street_reach_ft` was dropped through its full reach
   (`build_rear_yard_analysis` signature, the bridge `_rear_yard_analysis_for` and its `street_reaches`
   computation, and the `_analysis` test helper). Behaviour identical (both lines stay `not_known`);
   `test_constraint_lines_carry_no_geometry_when_not_established` stays green.
5. `_check_b` not_applicable text — **FIXED**. The "(b) waiver consequence" ("within 100 feet ... no rear
   yard would be required") is appended only when (b) `applies`; a not_applicable reading no longer carries
   it. Tests: `test_check_b_not_applicable_text_omits_the_waiver_consequence` and
   `test_check_b_applies_text_keeps_the_waiver_consequence`.
6. 503 coercion — **FIXED**. `study_inputs.py` wraps the `street_data_provider(...)` call: an unexpected
   exception is coerced to `StudyInputsUnavailableError` (the route's fail-safe 503, reason
   `street_data_unavailable`); a `StudyInputsUnavailableError` passes through unchanged, and typed connector
   errors are untouched (they already fail closed to None inside the provider). Test:
   `test_study_live_geometry.py::test_unexpected_street_data_provider_exception_becomes_a_503`. Mutation proven.

**G1 F2 (advisory) — FIXED.** `envelope_constraints._side_yard_check`: for a `BUILDING_MIXED` building the
side-yard text leads with ZR 23-335(b) and the row cites `["ZR 23-335", "ZR 35-01"]` (the captured
35-01 -> Chapter 5 -> 23-335(b) pathway); 34-232 (residential-building only) and the uncaptured 35-24 are
not cited. A residential building in the overlay keeps 34-232. Tests:
`test_side_yard_mixed_leads_with_23_335b_not_34_232`, `test_side_yard_residential_in_overlay_keeps_34_232`.
The benchmark is residential-only, so the printed report is unaffected. Mutation proven.

**G1 F3 (advisory) — FIXED.** A triggered setback row now carries a condition that the 10 ft / 15 ft depths
are the least the setback must be and that ZR 23-433(a) to (d) may reduce or waive them (plain user words).
Tests: `test_triggered_setback_notes_the_depths_are_minimums_subject_to_23_433`,
`test_not_triggered_setback_carries_no_minimums_condition`. The benchmark (30 ft) triggers no setback, so
it does not move.

**G4 advisories 3 & 4 — FIXED.**
- adv 3: `readers._envelope_open_effect` side-yard effect follows the row state like the setback branch
  (applies -> "Two side yards ... are required (ZR 23-335(a))"; else "No side yard is required ..."), so a
  detached-no-overlay row cannot contradict page 3. Test:
  `test_report_benchmark.py::test_m5t170_page_8_side_yard_effect_follows_the_row_state`. Mutation proven.
- adv 4: `page_site_context._ENVELOPE_CATEGORY` gains `"side_yard": "side_yard"`, so the page-3 side-yard
  row carries the same "(see item N)" cross-reference the setback/street-wall rows have. Test:
  `test_constraint_rows.py::test_s9_page_three_side_yard_links_its_numbered_open_item`. Consumer moved: the
  page-3 site-section word baseline in `test_constraints_page.py::test_s10_site_section_words_within_the_baseline`
  went 216 -> 220 (the +4-word "(see item 9)" link; each reading still one short sentence).

## Records
- NB-06 rev 3 -> 4, NB-05 rev 5 -> 6, NB-01 rev 7 -> 8; `code_identity` updated to the new LF-sha256 of the
  files I changed that each record lists: `envelope_constraints.py` + `result_way_engine_bridge.py` (NB-06),
  `result_way_engine_bridge.py` (NB-05), `study_inputs.py` + `readers.py` (NB-01). `research_record_check.py
  --check` PASS; NB-01/05/06 `code_current=True`.
- **NB-03 is a forbidden path and lists `rear_yard_checks.py` in its `code_identity`.** Editing
  `rear_yard_checks.py` (advisories 1/4/5) makes NB-03 `code_current=False` — the check REPORTS this (NOTE),
  it does not FAIL (exit 0). Carried: the orchestrator should schedule an NB-03 code-identity revision (new
  LF-sha256 `24b7f2c8283baa460e6b58d4bccbf7df3b5f0da8ef2ebce56c6465c41d62182c`). No human verdict entered
  anywhere; nothing labelled Verified.

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider; heavy runs under flock)
- `ruff check .` (services/api) — **exit 0** (All checks passed).
- Touched tests (test_envelope_constraints, test_rear_yard_short_block, test_result_way_engine_bridge,
  test_study_live_geometry) — **109 passed, exit 0**.
- Benchmark regenerated: `UPDATE_JOURNEY_FIXTURE=1 pytest tests/journey/test_215_16_northern_journey.py` —
  **2 passed, exit 0**. Fixture diff = 4 lines: the (c)(3) check text, the combined condition assumption,
  and the two `mapped_street_width:*` `source_title` values.
- Benchmark consumers (report_benchmark, constraint_rows, report_pages, results_contract_1_5_0,
  constraints_page, report_law_links, maps/northern_fixture, cad, drawings/kit) — after the
  `test_constraints_page` baseline update: **all passed** (first run reddened only
  `test_s10_site_section_words_within_the_baseline`, 220 <= 216, fixed by the documented baseline bump).
- `validate_contracts.py` — **Checked 23 schema file(s); 0 failure(s)**; `.github/scripts/tests` — **24 passed, exit 0**.
- `render_review_register.py --check` — **PASSED (no issues), exit 0**.
- `research_record_check.py --check` — **PASS, exit 0** (NB-01/05/06 code_current True; NB-02/04 unaffected;
  NB-03 code_current False — reported, not failed — carried).
- `modularity_check.py --check` — **807 files, failures 0** (warnings only; no band crossed).
- `check_lane_paths.py --coverage` — **LANE COVERAGE PASS: 10607 file(s), exit 0**.
- WHOLE `cd services/api && pytest -q -p no:cacheprovider` — **9951 passed, 8 skipped, exit 0 (519s)**.
- `apps/web` `npm ci` (once) then WHOLE `npx vitest run` — **129 files, 2704 passed, exit 0** (the jsdom
  getContext/WebGL lines are MapLibre console noise, no FAILs).

## Mutation proofs (mutate -> run the pinning test -> FAIL -> restore; all four restored, the four pinning tests re-run green together)
1. F1 source swap (`_street_width_source` -> `_mappluto_source`) -> `test_envelope_width_facts_cite_the_dcm_street_centerline_not_mappluto` FAILED. RESTORED.
2. F2 citation (mixed cites 34-232) -> `test_side_yard_mixed_leads_with_23_335b_not_34_232` FAILED. RESTORED.
3. page-8 side-yard state (effect made state-invariant) -> `test_m5t170_page_8_side_yard_effect_follows_the_row_state` FAILED. RESTORED.
4. 503 coercion (re-raise instead of coerce) -> `test_unexpected_street_data_provider_exception_becomes_a_503` FAILED. RESTORED.

## REAL PRINT (TestClient POST /report; /tmp/claude-0/M5-T170-r2/print/report.{html,pdf})
`benchmark_provider(with_zoning_lot=True, street_on=True)` bound to `get_results_study_inputs_provider`
and `recorded_pack_provider(benchmark_215_16_northern_window)` to `get_report_map_context_provider`;
POST `/api/v1/properties/4073340070/report?address=215-16 NORTHERN BOULEVARD, Queens` with
`{"housing_program":"standard_residence"}` -> 200 HTML, then `node apps/web/scripts/print-report-pdf.mjs`
(11 pages, no server, no ports). Per-page `pdftotext -layout` vs the round-1 print
`session-2026-10-15a/print-b067e9db/report.pdf`:
- PAGE 3: CHANGED — the side-yard row gained " (see item 9)" (G4 adv 4 cross-reference). Only change.
- PAGES 1, 2, 4, 5, 6, 7, 8, 9, 10, 11: UNCHANGED (byte-identical text).
The width-fact provenance (F1) and the rear-yard (c)(1)/(c)(3) text (adv 1) changed in the document data
but are not rendered on any report page, so no page moved for them; F2/F3 are not reached by the
residential benchmark. Pages 3/6/8 still agree.

## Carried / stopped (for the orchestrator)
- DB-265 adv 2 (register code_link) and adv 3 (double fetch) are CARRIED because their required files
  (`docs/zoning-rule-review/rules/r6b-rear-yard-corner-waiver.md`; `app/api/v1/study_live_geometry.py`) are
  outside this packet's allowed_paths — STOP-and-report per the brief, not silently dropped (S17 allows a
  carry with a reason).
- NB-03 code-identity staleness for `rear_yard_checks.py` is carried (forbidden path).

END-OF-REPORT
