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

---

# Rework 1 — the overlay and other-basis dimensions wired into the live report; page 1 reads the 1.5.0 row

Producer: backend-engineer (an AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a7fdf6d94b592c2ef`.
Reset to the scope-correction head `79e2bfb9c644713b095c963643f9a0306b3fd732` (it
carries the first round as commit `f66e8212`) before work. This round closes the first
round's two disclosed limitations (A and B); the first round's reader, page-3 rows,
overlay and other-basis dimensions are unchanged.

## What changed and why

**A. Wiring (the live report now draws what the unit tests prove; S12).** The first
round built the overlay and the other-basis close-frame dimensions and hooked them into
`site_context_plan.draw_site_context_plan`, but the report never passed the document's
`geometry.constraint_lines` / `input_facts` down to it, so the live render drew nothing.
Three files thread the data through, with the fewest lines and no change to
`site_context_plan.py` (it is above its size warning, DB-250):

1. `maps/__init__.py` — `render_site_context_plan` gains `constraint_lines=None,
   input_facts=None` and forwards them to `draw_site_context_plan` (every other caller is
   byte-identical).
2. `report/drawings_embed.py` — `embed_map` gains the same two kwargs and forwards them to
   the map function ONLY when they are not None, so the neighbourhood/block maps (which do
   not accept them) and every overlay-free render are byte-identical.
3. `report/page_location.py` — `resolve` reads `geometry.constraint_lines` and
   `input_facts` defensively (`_overlay_data`) and passes them to the two site-context
   embeds (the page-1 `summary_close` thumbnail and the page-3 `close` frame); the
   neighbourhood/block locators get nothing. A 1.4.0 document yields `(None, None)`.

**B. Page 1 reads the 1.5.0 combined rear-yard row (S2).** `page_decision_summary.py`'s
rear-yard uncertainty line now reads `constraint_text.rear_yard_combined(results)` — the
SAME wording source the page-3 row uses. For a document carrying the 1.5.0 combined row it
shows the row's OWN text, its ZR sections linked (`_rear_yard_section_links` via
`law_links`, 23-344/12-10), and the label from its way (Conditional); no measurement
number. For a 1.4.0 (and earlier) document `rear_yard_combined` is None, so the line keeps
the open-check reference byte-identical (title + ZR 23-344 link + Unresolved). The appendix
open item (`readers.py`) is NOT this task's — it moved to M5-T167 (scope correction).

**C. Tests (in the task's own test files).** `tests/drawings/report/test_constraint_rows.py`
gains the live-path S12 coverage, the benchmark's recorded map context helper, and a 1.4.0
page-1 guard (four tests). No new results fixture; the S12 document is the committed 1.5.0
example rendered WITH the benchmark's recorded window pack (same lot, bbl 4073340070, so
the one-outline check passes).

## Live-path test table — every state has its own outcome and its own test

| Through the live path (`build_report_html` + map embed) | Outcome | Test |
|---|---|---|
| 1.5.0 established `rear_yard_100ft_line` | drawn on the site frames; the large close frame labels it once | `test_s12_live_report_draws_only_established_lines_and_other_basis_dimensions` |
| 1.5.0 `not_established` line WITH geometry | draws nothing (R017 is the guard, not missing geometry) | same test (`data-kind="setback_line"` absent) |
| 1.5.0 `not_known` `corner_area` (no geometry) | draws nothing | same test (`data-kind="corner_area"` absent) |
| 1.5.0 `input_facts` other bases | printed-tax-map + recorded-area dimensions drawn, each basis named | same test (`"printed tax map"`, `"city record"`) |
| 1.4.0 document WITH map context | no overlay, no other-basis dimension (byte-identical) | `test_s12_1_4_0_report_with_maps_draws_no_overlay` |
| 1.5.0 conditional combined rear yard, page 1 | combined text, ZR 23-344 linked, Conditional, no number | `test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard` |
| 1.4.0 document, page 1 | open-check reference unchanged (title + ZR 23-344 + Unresolved) | `test_s1_benchmark_page_one_rear_yard_uncertainty_is_unchanged` |

## Byte-identity proof for the 1.4.0 output (S1, re-run vs the claim head)

Script `/tmp/claude-0/M5-T175-rw1/render_report.py` rendered, in a detached worktree at the
claim head `654ea3fade56e075f7bb447eb2f87d0b88fb38a4` and in this worktree, the report HTML
for every valid results fixture (12), the benchmark report WITH its recorded map context
(1), and the five `site_context_plan` map SVGs (close, summary_close, report, summary,
wide). sha256 (LF-normalized) compared:

- 18 render outputs total; **17 byte-identical** to the claim head.
- The ONLY difference is `report::synthetic_rear_yard_constraints_contract_1_5_0.json`
  (`4a6ccc2e…` → `ea6cce1e…`) — the one fixture carrying the 1.5.0 blocks, whose page-3 rows
  (first round) AND page-1 uncertainty (this round) now read the engine's own rows (intended).
- Byte-identical: all 11 other fixtures' report HTML, the benchmark report-with-maps, and
  ALL five site_context_plan map SVGs — the wiring draws nothing without the 1.5.0 data.

The within-test S1 guards (`test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged`,
`test_s1_benchmark_page_one_rear_yard_uncertainty_is_unchanged`) pin the benchmark's page-3
rows and page-1 rear-yard uncertainty to the exact 1.4.0 output.

## Commands, exit codes and counts (rework 1)

- `cd services/api && python -m ruff check .` → **exit 0** ("All checks passed!").
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/drawings tests/cad
  tests/api/test_report_read_api.py tests/api/test_report_read_context.py` → **exit 0**:
  **1819 passed, 6 skipped** in 148.04s (1815 + the 4 new live-path/page-1 tests; every
  forbidden/benchmark test green, unedited).
- New/changed test file alone: `pytest … test_constraint_rows.py test_constraint_overlay.py`
  → **exit 0**: 21 passed (12 report rows incl. the 4 new + 9 overlay).
- `python3 tools/research_record_check.py --check` → **exit 0**: NB-04
  `status=conflicting_evidence code_current=True review_state=stale`; "PASS". No code path
  NB-04 lists changed this round (close_frame_dimensions.py is untouched), so NB-04 is
  unchanged (revision 3 still records the current code identity).
- `python3 tools/modularity_check.py --check` → **exit 0**: failures 0 (warnings only).
  `site_context_plan.py` is untouched (609 SLOC, unchanged); the wiring additions to
  `__init__.py` / `drawings_embed.py` / `page_location.py` / `page_decision_summary.py`
  cross no threshold.
- `python3 scripts/lanes/check_lane_paths.py --coverage` → **exit 0**:
  "LANE COVERAGE PASS: 10392 file(s), each owned by exactly one lane."

Browser/e2e tests were NOT run and no server was started (ports 3000/3001/8000 untouched).

## Mutation outputs (applied, failing test kept, reverted, re-run green)

1. **Dropped the wiring** (`resolve` passes `constraint_lines=None, input_facts=None`):
   `test_s12_live_report_draws_only_established_lines_and_other_basis_dimensions` **FAILED**
   (`'data-role="constraint-overlay"'` absent from the live report). Reverted.
2. **Gave page 1 the 1.4.0 open-check text for a 1.5.0 conditional row** (forced
   `combined = None` in `_uncertainty_line`): `test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard`
   **FAILED** (combined text absent; the line reverted to "Rear yard · ZR 23-344 ·
   Unresolved"). Reverted.
3. **Drew a not_established line through the live path** (removed the `state == established`
   guard in `draw_constraint_overlay`): the same S12 live test **FAILED**
   (`data-kind="setback_line"` appeared in the report). Reverted.

After reverting all three, ruff and both task test files are green again (21 passed).

## What I could not check (rework 1)

- The LIVE preview/browser rendering of the wired overlay (no server, thin-client). The
  live render is proven by `build_report_html` with the benchmark's recorded map context
  (an in-memory pack), not by a running preview; the on-page visual quality of the overlay
  labels/legend at print size is a visual-quality-reviewer / H2 render check.
- Primary sources: no file NB-04 lists changed this round, so I relied on NB-04's existing
  revision 3 (first round) and re-fetched no live source. No professional/legal review.

---

# Rework 2 — the four review corrections on the close frame when a constraint line is drawn

Producer: backend-engineer (an AI agent). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-a6db22b7a45b80bde`. Reset to the second
scope-correction head `d1a42a8d7` (it carries rounds `f66e8212` and `c11b4e03`) before work. This
round makes the corrections the four reviews required (session 2026-10-14c): G3 visual's three
REQUIRED corrections, the G3-code advisories 1/2 and the G4 advisory 1. The earlier rounds' reader,
page-3 rows, overlay and other-basis dimensions are unchanged; every EXISTING output stays
byte-identical (proven below). Only the 1.5.0 example's close frame changes.

## Corrections and why

- **A. S13 legend names what is drawn (visual G3 finding 2).** The overlay reused the dashed
  `setback_line` style, so the legend listed "Setback line" though no setback line was drawn and
  never named the rear-yard line that IS drawn. Added three dedicated style-table entries
  (`kit/styles.py`, additive): `rear_yard_100ft_line` (a LINE, green dash, "Rear-yard 100 ft line"),
  `corner_area` and `street_wall_band` (two AREA kinds, each a unique black-and-white hatch);
  `setback_line` already had one. `constraint_overlay._CONSTRAINT_STYLE` now draws each kind in its
  OWN style, so the legend (generated from the drawn kinds) names the rear-yard line and never lists
  "Setback line". Additive only: no existing drawing draws these kinds, so every existing output is
  byte-identical (the style-table tests on line looks, colour separation and CAD layers still pass).
- **B. S13 legend fits (visual G3 finding 1).** The extra legend entry pushed the "No building
  placed" row past the fixed 470 pt close-frame height, clipping it over the sources caption. The
  frame-height logic lives in `context_scene.compose_context`, which is NOT in this task's allowed
  paths, so I did not edit it. Instead `constraint_overlay.expand_frame_for_overlay(svg)` (called
  from `site_context_plan`'s close branch only when `constraint_lines` are passed) grows the SVG
  height and viewBox to contain the furniture content with an 8 pt margin. It ONLY GROWS the frame
  (never shrinks it), so a frame whose legend already fits — every frame without the overlay — is
  returned byte-identical. Measured: the plain benchmark close frame stays 470.00 pt; the overlay
  frame grows to 484.50 pt and the "No building placed" row (baseline 474.50) is fully inside it.
- **C. S5/S14 line inside the lot (visual G3 finding 3).** The committed example's rear-yard line
  runs x 0 -> 182.5 while the lot ends near x 123, so it was drawn ~60 ft past the lot, across 215
  Place. `draw_constraint_overlay` now takes a `clip_polygon` (the subject lot outline, map frame)
  and clips each line segment to it with shapely (`_clip_line_to_polygon`): a line running past the
  lot is drawn only inside it (clipped ends on the outline within 0.01 ft), a line wholly outside
  draws nothing, and an interior vertex inside the lot is preserved (no point moved or invented).
  The label and legend follow the drawn part. Areas are drawn as given (the brief clips lines).
- **D. S15 failure keeps the map (code-review advisories 1/2).** A label that cannot be placed at
  8.5 pt raises by design, and a malformed established geometry raises too; both were caught by
  `embed_map`'s blanket except and dropped the WHOLE site map. `embed_map` now RETRIES the map
  without the overlay when an overlay was requested; on success it keeps the map and carries one
  short note "A zoning line could not be drawn on this map; page 3 lists it." (rendered by
  `page_site_context._site_outline`). If it fails without the overlay too, it is a genuine map
  failure — today's one short line. Any other map failure is unchanged (S1 unaffected).
- **E. S16 page 1 title + (c)(3) test (QA advisory 1 / visual finding 4).** On page 1 the title is
  the link label, so a combined text beginning with the title read "Rear yard Rear yard:".
  `page_decision_summary._uncertainty_line` now strips the leading title from the combined text on
  page 1 (page 3 keeps the full text — separate columns, no stutter). Added a direct test that the
  not_known 23-344(c)(3) check row carries no inputs and prints no ft/sq-ft number, only its text.

## Scenario-test table (each asserts the displaced value)

| Scenario | Test (file::name) | Asserts |
|---|---|---|
| S13 names | test_constraint_overlay::test_s13_legend_names_the_drawn_rear_yard_line_never_setback; test_style_table::test_constraint_kinds_have_their_own_legend_entries | legend has "Rear-yard 100 ft line", never ">Setback line</text>" |
| S13 fit | test_constraint_rows::test_s13_overlay_legend_fits_and_the_plain_frame_is_unchanged | overlay frame height > plain; "No building placed" within height; plain == 470.0 |
| S14 clip | test_constraint_overlay::test_s14_established_line_is_drawn_only_inside_the_lot | drawn max x < 130 (never 182.5); each point on/inside lot <=0.01 ft; bare (no clip) reaches 182.5 |
| S14 outside | test_constraint_overlay::test_s14_a_line_wholly_outside_the_lot_draws_nothing | drawn == [], sheet empty |
| S15 both kinds | test_constraint_rows::test_s15_overlay_failure_keeps_the_map_with_a_note (ConstraintOverlayError + ValueError) | em.is_drawing True, the note present |
| S15 end-to-end | test_constraint_rows::test_s15_report_keeps_the_site_map_when_overlay_geometry_is_malformed | report keeps site_context_plan + note; no overlay |
| S16 stutter | test_constraint_rows::test_s16_page_one_rear_yard_uncertainty_does_not_repeat_its_title | "Rear yard Rear yard" absent; body present |
| S16 (c)(3) | test_constraint_rows::test_s16_not_known_rear_yard_check_prints_no_number | not_known, no inputs, no number |

Updated existing tests (behaviour changed by A/E): test_constraint_overlay::test_offset_places_...
and test_constraint_rows::test_s12_live_... (the rear-yard name now appears twice: drawing label +
legend entry); test_s12_page_one_... (page-1 body shows without the leading title).

## Byte-identity (S1) vs the claim head 654ea3fad

Script `/tmp/claude-0/M5-T175-rw2/byteid.py` rendered, in a detached checkout at `654ea3fad` and in
this worktree, the report HTML for every valid results fixture (12), the benchmark report WITH its
recorded map context (1), and the five `site_context_plan` map SVGs (close, summary_close, report,
summary, wide). LF-normalized sha256 compared: **18 outputs, 17 byte-identical, 1 differs** — only
`report::synthetic_rear_yard_constraints_contract_1_5_0.json` (`7964f53c...` -> `2f77427f...`), the
one fixture carrying the 1.5.0 blocks (intended: its overlay/page-1 reading). The DXF snapshots under
`tests/cad` stay byte-identical (the heavy run's `tests/cad` passes unedited; the style-table
additions touch only drawn kinds, and no existing drawing draws the new kinds).

## Commands, exit codes and counts (rework 2; lanes venv py3.12.3, PYTHONDONTWRITEBYTECODE=1, -p no:cacheprovider)

- `cd services/api && python -m ruff check .` -> **exit 0** ("All checks passed!").
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/drawings tests/cad tests/api/test_report_read_api.py tests/api/test_report_read_context.py` -> **exit 0**: **1828 passed, 6 skipped** in 185.87s (rework 1's 1819 + 9 new; every forbidden/benchmark/snapshot/DXF test green, unedited).
- Task files alone (test_constraint_rows + test_constraint_overlay + test_style_table) -> **exit 0**: 51 passed.
- `python3 tools/research_record_check.py --check` -> **exit 0**: NB-04 `status=conflicting_evidence code_current=True review_state=stale` (NB-04's code paths — close_frame_dimensions.py, the two connectors — are UNCHANGED this round, so NB-04 is not edited; revision 3 still records the current code identity).
- `python3 tools/modularity_check.py --check` -> **exit 0**: selected 799 files, **failures 0**, warnings 33. `site_context_plan.py` carries its expected review_signal warning only (the close branch gained one guarded `expand_frame_for_overlay` call; the overlay/clip/expander bodies live in `constraint_overlay.py`). No new file is above the hard threshold.
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> **exit 0**: "LANE COVERAGE PASS: 10402 file(s)".

Browser/e2e tests were NOT run and no server was started (ports 3000/3001/8000 untouched).

## Mutation outputs (applied, named test FAILED, reverted, re-run green)

1. **Remove the clip** (`pieces = [list(mapped)]` always): `test_s14_established_line_is_drawn_only_inside_the_lot` **FAILED** (drawn reaches x 182.5) and `test_s14_a_line_wholly_outside_the_lot_draws_nothing` **FAILED** (the off-lot line now draws -> ConstraintOverlayError). Reverted.
2. **Restore the reused 'Setback line' kind** (`_CONSTRAINT_STYLE["rear_yard_100ft_line"] = "setback_line"`): `test_s13_legend_names_the_drawn_rear_yard_line_never_setback` **FAILED** (legend shows "Setback line") and `test_s12_live_...` **FAILED** (name count 1, not 2). Reverted.
3. **Let the overlay failure propagate** (`embed_map` returns the short line on the first exception, no retry): both `test_s15_*` **FAILED** (the map is dropped, the note absent). Reverted.

After reverting all three, ruff and the task test files are green again (51 passed).

## What I saw on the printed page

I rendered the S12 document to A4 PDF myself (`node scripts/print-report-pdf.mjs` from a scratch
`apps/web` with `node_modules` symlinked from `/root/project/w-wave20/apps/web`; it binds no port):
`/tmp/claude-0/M5-T175-rw2/s12-report.pdf`, close-frame page rendered to
`/tmp/claude-0/M5-T175-rw2/p4-04.png`. The close-frame page (page 4 of 10) shows: the legend names
"Rear-yard 100 ft line" with a green dashed swatch (NOT "Setback line"); every legend row, including
"No building placed" (bottom-left, dashed swatch), sits fully ABOVE the "Sources:" caption with
nothing clipped or overlapping; the rear-yard line and its label "Rear-yard 100 ft line,
established, ZR 23-344" stay WITHIN the orange subject lot (Lot 70) and do not cross 215 Place; the
other-basis dimensions ("9,800 sq ft, city record", "10,120.5 sq ft, map outline", "100.5 ft,
printed tax map") each name their own basis on white backgrounds; the single basis note "All
dimensions: city map outline, not surveyed." sits under the frame.

## What I could not check

- Live preview/browser rendering (no server, thin-client); the overlay is proven by unit tests, the
  byte-identity script, and my own one-off PDF render, not by a running preview. The visual-quality
  re-review owns the on-page print judgement.
- S15's label-placement failure through the FULL live report path (the real viewport is large, so a
  label always places): I proved that kind at `embed_map` with a monkeypatched render fn that raises
  ConstraintOverlayError, and the malformed-geometry kind end-to-end through `build_report_html`.
- Areas (corner_area / street_wall_band) are not clipped to the lot (the brief clips lines; the
  committed example's only established item is the rear-yard LINE, corner_area is not_known).
- Primary sources: no NB-04-listed file changed, so I re-fetched no live source. No professional/legal review.
