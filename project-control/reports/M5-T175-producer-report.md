# M5-T175 producer report — the report reads the results contract 1.5.0 rows, input facts and constraint lines

Producer: backend-engineer (an AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-ae497a8c1e361f036`.
Contract/claim head reset to `654ea3fade56e075f7bb447eb2f87d0b88fb38a4` before work.

## What changed and why

The engine already emits the results contract 1.5.0 rear-yard checks, envelope rows,
input facts and `geometry.constraint_lines`; the report did not read them. This task
makes the report read the engine's OWN readings (fix the data path, D-094 R038),
with an EXACT fall-back to the 1.4.0 output.

1. **`report/constraint_text.py`** gains readers of the 1.5.0 blocks —
   `rear_yard_combined`, `rear_yard_checks`, `envelope_rows`, `envelope_row`,
   `has_results_rows` — plus the page-3 fall-back State strings
   (`PAGE3_FALLBACK_STATE`, `PAGE3_DEFAULT_STATE`), moved here from the hard-coded
   dict in `page_site_context.py` so the fall-back wording has one home. `effect_for`
   is UNCHANGED for the no-document call (it still returns `REAR_YARD_OPEN_CHECK` for
   `rear_yard`, pinned by `test_report_page_one.py:263` and `test_report_benchmark.py`).

2. **`report/page_site_context.py`** page-3 "What constrains the design?" rows now
   read `constraint_text`: when the document carries a 1.5.0 `rear_yard`/`envelope_rows`
   block, each row shows the engine's OWN state/way/text, its ZR sections linked
   (`law_links`), its numbered open item linked as `#issue-<n>`, and its label from the
   row's way/state. The rear yard shows the combined row (Conditional), never an
   unconditional zero. A 1.4.0 (and earlier) document takes the UNCHANGED fall-back
   branch (the hard-coded dict is gone — its strings are `constraint_text`'s
   `PAGE3_FALLBACK_STATE`; the plain `(see item N)` text is kept so the benchmark is
   byte-identical).

3. **`maps/close_frame_dimensions.py`** gains `draw_other_basis_dimensions` /
   `other_basis_label` / `OTHER_BASIS_WORDS` / `DrawnFact`: the `input_facts`'
   other-basis lot dimensions (printed_tax_map frontage, administrative_record recorded
   area, gis outline area) drawn BESIDE the map-outline dimensions, each label naming its
   OWN basis (plain-word labels of the design contract). Two bases are never merged into
   one figure (NB-04 `double_count_risk`); a GIS value reads "map outline", never "tax
   map". `draw_edge_dimensions` is untouched.

4. **`maps/constraint_overlay.py`** (new) draws `geometry.constraint_lines` on the site
   frame ONLY where a line's state is `established` (R017): a `not_established` or
   `not_known` item carries no geometry and draws NOTHING, so the legend lists only what
   is drawn (R044). Lines are drawn as a distinctive dashed stroke, areas as a hatched
   fill (S6); each is labelled with its name, state and ZR section at ≥ 8.5 pt and a
   label that cannot be placed without a collision FAILS rather than shrinks. The
   constraint geometry is in the RESULTS local-feet frame; the pure-translation
   `overlay_offset` (the subject outline's minimum, from the one-outline match) places it
   on the map lot — never a reprojection; the drawn endpoints lie on the document's own
   vertices (S5). `draw_site_constraints` is the thin entry the site-plan hook calls.

5. **`maps/site_context_plan.py`** gains ONLY the thin hook: `draw_site_context_plan` /
   `draw_block_scene` accept optional `constraint_lines` / `input_facts` (default None, so
   every existing caller is byte-identical) and, on the large close frame, call
   `draw_site_constraints`. The compact page-1 thumbnail draws the constraint geometry
   only (named by the legend, no label) — it already drops its dimension labels (too
   narrow for 8.5 pt). The overlay body lives in `constraint_overlay.py`.

6. **`NB-04`** → revision 3: `last_changed` 2026-10-14 and the new code identity of
   `close_frame_dimensions.py`
   (`8394b3e605728f14afc1544f8a6d5dec659a9fde0cd4e9c358822e83814529e8`, LF-normalized).
   `research_status` stays `conflicting_evidence` (unchanged; only M5-T167 changes a
   research_status in W25, G-13). The G1 reviewer appends the revision-3 agent review
   (`review_state` is `stale` until then; the record-check still exits 0).

## Scope limits actually hit (disclosure)

- **The overlay (4) and the other-basis dimensions (3) are built, hooked and tested, but
  NOT wired into the LIVE report render.** Threading `results.geometry.constraint_lines`
  and `results.input_facts` into the close frame needs `report/drawings_embed.py`
  (`embed_map`), `report/page_location.py` (`resolve`) and `maps/__init__.py`
  (`render_site_context_plan`) — none in this task's allowed paths. Per the brief
  ("if any file outside your allowed paths must change, STOP and report it"), I did not
  edit them. The capability + hook + tests are complete; a follow-on task threads the
  data through those three files. This is also why S1 holds trivially: the live report
  never receives the new data, so every 1.4.0 output is unchanged. (There is also no
  committed `map_context` pack for the synthetic 1.5.0 fixture, and the only fixture with
  a pack — recorded_215_16 — is 1.4.0 with no constraint_lines, so no committed render
  path would draw the overlay even if wired.)

- **S2's "page-1 uncertainty … labelled Conditional" is NOT achieved on page 1.** The
  page-1 uncertainty line and the appendix open-item list are built by
  `page_decision_summary.py` / `page_assumptions.py` / `readers.py` — all forbidden —
  from the permitted_envelope withheld `rear_yard` value, and `test_report_page_one.py`
  (not in my allowed paths) pins `effect_for("rear_yard") == REAR_YARD_OPEN_CHECK`. So
  page 1 keeps the safe open-check reference `Rear yard · ZR 23-344 · Unresolved` (it
  names the law and never says "no rear yard"), while the PAGE-3 row carries the full
  combined Conditional reading. Making page 1 read the 1.5.0 combined row/label would
  require editing those forbidden files. The design contract's safety rule ("never an
  unconditional 'no rear yard'; never worded as if the corner test were the only
  exception") is met on both surfaces. The return-prep's claim that `(see item N)`
  "renders nowhere today" is incorrect — the benchmark renders it in all four page-3
  rows — so converting it to a link universally WOULD break S1; the fall-back keeps the
  plain text and the `#issue-<n>` link is emitted on the 1.5.0 reading path.

## Byte-identity proof for the 1.4.0 output (S1)

Script `/tmp/claude-0/M5-T175/render_report.py` rendered, in a claim-head worktree and in
this worktree, the report HTML for every valid results fixture (12), the benchmark report
WITH its recorded map context (1), and the five `site_context_plan` map SVGs (close,
summary_close, report, summary, wide). sha256 (LF-normalized) compared:

- 18 render outputs total; **17 byte-identical** before/after.
- The ONLY difference is `report::synthetic_rear_yard_constraints_contract_1_5_0.json`
  (`4a6ccc2e…` → `c6e0829b…`) — the one fixture carrying the 1.5.0 rear_yard/envelope/
  input_facts/constraint_lines, whose page-3 now reads the engine's rows (intended).
- Byte-identical: all 11 other fixtures' report HTML, the benchmark report-with-maps, and
  ALL five site_context_plan map SVGs — the maps hook draws nothing without the data.

The within-test S1 guard `test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged` pins the
benchmark's four page-3 rows to the exact 1.4.0 strings (mutation 1 reddens it).

## State table — every input state has its own outcome and its own test

| State | Outcome | Test |
|---|---|---|
| 1.4.0 (and earlier) document | page-3 rows unchanged (fall-back); report byte-identical | `test_constraint_rows.py::test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged`; byte-identity script |
| 1.5.0 document with NO rear_yard/envelope | falls back to 1.4.0 path | `test_s1_a_1_5_0_document_with_no_rear_yard_or_envelope_falls_back` |
| 1.5.0 conditional rear yard | combined row's own text, Conditional, ZR 23-344 linked, no number | `test_s2_conditional_rear_yard_shows_combined_text_labelled_conditional` |
| 1.5.0 not_known row (side yard) | shows its reason/text, no number | `test_s3_not_known_envelope_row_shows_text_no_number` |
| 1.5.0 envelope rows present | setback/street-wall render through the same reader | `test_s7_envelope_rows_render_through_the_same_reader` |
| constraint line `established` | drawn (hatched/dashed), labelled, endpoints on vertices | overlay `test_s4_only_established_lines_are_drawn`, `test_s5_drawn_endpoints_lie_on_the_document_vertices` |
| constraint line `not_established`/`not_known` | draws nothing; legend omits it | `test_s4_a_not_established_line_draws_nothing`, `test_s4_only_established_lines_are_drawn` |
| input_facts (other bases) present | each basis labelled beside the outline, nothing merged | `test_s5_each_input_fact_names_its_own_basis_nothing_merged`, `test_s5_other_basis_dimensions_draw_beside_the_outline` |
| no 1.5.0 blocks / no overlay data | overlay/other-basis draw nothing; byte-identical | `test_offset_places_results_geometry_on_the_map_lot` (no-args branch); byte-identity script |
| every internal #issue href | resolves to a page_assumptions id="issue-<n>" | `test_s9_every_issue_href_resolves_to_an_anchor`, `test_s9_page_three_rear_yard_links_its_numbered_open_item` |

The printed texts are plain architect texts; none says a value was "captured" or "verified".

## Exact page-3 row and page-1 uncertainty for the 1.5.0 conditional example

Page-3 "What constrains the design?" rear-yard row (`synthetic_rear_yard_constraints_contract_1_5_0.json`):

- Constraint cell: `Rear yard`
- State cell (visible): `Rear yard: a conditional no-rear-yard reading under ZR 23-344(b),
  with (c)(3) as an alternative along the neighbours' side lot lines. A labelled draft
  reading, not a DOB determination.` followed by linked `ZR 23-344` (→
  `…/article-ii/chapter-3/23-344`) and `ZR 12-10`, then `(see item 4)` linking `#issue-4`.
- Status cell: `Conditional`. No rear-yard measurement number is printed.

Page-1 uncertainty line (unchanged, from the forbidden page_decision_summary.py): visible
`Rear yard  ZR 23-344  Unresolved` (title + law link + the open-check label) — see the
disclosure above.

## Commands, exit codes and counts

- `cd services/api && python -m ruff check .` → **exit 0** ("All checks passed!").
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/drawings tests/cad tests/api/test_report_read_api.py tests/api/test_report_read_context.py` → **exit 0**: **1815 passed, 6 skipped** in 168.51s (every forbidden/benchmark test green, unedited).
- New tests alone: `pytest … tests/drawings/report/test_constraint_rows.py tests/drawings/maps/test_constraint_overlay.py` → **exit 0**: 17 passed (8 page-3 + 9 overlay).
- `python3 tools/research_record_check.py --check` → **exit 0** (direct `$?`): NB-04 `status=conflicting_evidence code_current=True review_state=stale`; "PASS".
- `python3 tools/modularity_check.py --check` → **exit 0**: `selected 796 files; failures 0; warnings 33`. site_context_plan.py 597→609 SLOC (crossing the 600 WARN, within the 656 material-growth limit → one `review_signal` warning; the overlay body lives in constraint_overlay.py, so the hook growth is +12 SLOC).
- `python3 scripts/lanes/check_lane_paths.py --coverage` → **exit 0**: "LANE COVERAGE PASS: 10362 file(s), each owned by exactly one lane."

Browser/e2e tests were NOT run and no server was started (ports 3000/3001/8000 untouched).

## Mutation outputs (applied, failing line kept, reverted, re-run green)

1. Fall-back rear-yard text `"Not known"` → `"Not known MUT"`:
   `test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged` **FAILED**
   (`'Not known MUT (see item 4)' != 'Not known (see item 4)'`). Reverted.
2. Removed the `state != established` guard so a not_established line (with geometry) is
   drawn: `test_s4_a_not_established_line_draws_nothing` **FAILED**
   (drawn contained the setback_line). Reverted.
3. Merged a second basis into one label (`word` → `"<word> / city record"`):
   `test_s5_each_input_fact_names_its_own_basis_nothing_merged` **FAILED**
   (`'100.5 ft, printed tax map / city record' names ['printed tax map', 'city record']`).
   Reverted.
4. Broke the issue target (`#issue-{n}` → `#issue-{n}99`): both `test_s9_*` **FAILED**
   (`href="#issue-4"` absent / dangling link `#issue-499`). Reverted.

After reverting all four, ruff and both new test files are green again.

## NB-04 revision note

NB-04 → revision 3 (2026-10-14). Only `implementation.code_identity` for
`close_frame_dimensions.py` was updated to the new LF-normalized sha256
`8394b3e605728f14afc1544f8a6d5dec659a9fde0cd4e9c358822e83814529e8` (that file gained the
other-basis-dimension function; the two MapPLUTO connectors are byte-unchanged).
`research_status` stays `conflicting_evidence`; no evidence or reading was changed.
`constraint_overlay.py` is registered in no evidence record (orchestrator decision in the
packet path_notes: it renders document values only) — the G1 reviewer may decide otherwise.

## What I could not check

- The LIVE report/preview rendering of the overlay (no server, thin-client; and the data
  is not wired into the render path — see the scope-limits disclosure). The overlay and
  other-basis geometry are proven by direct unit tests against an in-memory map context
  and a constructed ViewFrame, not by a full report render.
- The visual quality of the overlay labels/legend at print size (a visual-quality-reviewer
  / H2 render check, outside a producer unit test). The legend currently names the reused
  style kinds (Yard / Setback line / Setback zone) because styles.py holds no dedicated
  constraint styles and is out of scope; the drawing LABEL carries the exact constraint
  name, state and law.
- Primary sources: I re-read NB-04's cited evidence (tax maps, PLUTO, MapPLUTO, DOF
  transaction 76338, ZR 12-10) and NB-03/NB-06 as read-only; I did not re-fetch any live
  source (freshness is NB-04's own `checked_on` 2026-10-10). No professional/legal review.
