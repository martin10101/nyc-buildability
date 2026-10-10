# M5-T151 producer report - the program's report generator

I am an AI agent (backend-engineer). Producer of ledger task M5-T151. One commit; no push.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a8199ae6bc0f48296`
Reset base / commit parent: `876d7a2e5fcaea6fb24b51bf0b30aa76f39b97ef`
(Wave-21 branch `task/wave21-report-redesign`; `git status --porcelain` empty after the one commit.)

## What was built

A server-side HTML report generator under `services/api/app/drawings/report/`, split into focused
modules, plus a flag-gated route and the presentation-contract record. Every figure is read from the
results document and only formatted (ruling X7); no number is typed in presentation code.

### Modules and line counts (SLOC via `wc -l`)

| Module | Lines | Responsibility |
|---|---|---|
| `__init__.py` | 23 | public entry re-export (`build_report_html`) |
| `builder.py` | 99 | assemble the six page types into one standalone HTML document |
| `formatting.py` | 78 | figure formatting from document leaves (X7) |
| `labels.py` | 122 | six labels + X4 mapping, X5 wording, forbidden words, standing label |
| `sources.py` | 84 | readable source/rule/law titles (X6, R925) |
| `options.py` | 118 | the eleven options in ONE place (X8) + shared limitations |
| `readers.py` | 316 | defensive read-only views of the results document |
| `drawings_embed.py` | 140 | the drawing interface (X9) + the allowance bar chart (own SVG) |
| `layout.py` | 85 | A4 print CSS from the shared tokens (margin boxes, counters, breaks) |
| `html.py` | 86 | stdlib-escaping HTML assembly, no template engine (X2) |
| `components.py` | 59 | shared presentation fragments |
| `page_decision_summary.py` | 129 | page type 1 |
| `page_site_context.py` | 97 | page type 2 |
| `page_option_comparison.py` | 104 | page type 3 |
| `page_scenario_sheet.py` | 129 | page type 4 (one sheet per worked building) |
| `page_assumptions.py` | 114 | page type 5 (+ nine-contents coverage inventory A-I) |
| `page_evidence.py` | 111 | page type 6 (inputs, allowance, provenance, status-label key) |

Tests: `services/api/tests/drawings/report/test_report_pages.py` (366), `services/api/tests/api/test_report_read_api.py` (124).

### The route

`POST /api/v1/properties/{bbl}/report` in `services/api/app/api/v1/report_read.py`, mounted in
`services/api/app/main.py` (same posture block as the results route). It REUSES the results route's
whole flow, not a copy: it delegates to `app.api.v1.results_read.post_results` (same flag
`INTERNAL_RESULTS_ENABLED`, same per-caller rate limit, same BBL/body validation, same injected
study-inputs provider, same engine chain and contract guard) and returns every non-200 verbatim, so
the gating and refusals are byte-identical to the results route's. On 200 it renders the emitted
results document into the full report and answers `text/html; charset=utf-8` (ruling X9 d).

### Identity and maps

- Identity (borough, block, lot, district, overlay, lot-selection) is read from the emitted results
  document (`scope.lot` + `scope.assumptions`). The STREET ADDRESS is NOT in the results document and
  is not reachable on this reuse path without a second call, so the running header uses the
  borough/block/lot display. `build_report_html(..., identity=...)` accepts an address when a caller
  has one (the pages test passes one); the route does not, so the benchmark report header shows
  "Queens block 7334, lot 70". This is the documented fallback the brief allows.
- Maps: the map connectors `build_map_context` needs (zoning features, building footprints) are not
  produced on the results-inputs path, so NO map document is built on the route; the report is
  produced without maps (never an error page). The site page prints one short line and the coverage
  inventory does not claim maps. `build_report_html` accepts a `map_context` so the with-maps branch
  is exercised in tests.

### Drawings interface (ruling X9) and the tests skipped until integration

The report calls the kit/maps at `frame="report"` through a defensive wrapper
(`drawings_embed`): it checks `inspect.signature` for the `frame` keyword and `getattr` for
`render_floor_stack`; when the keyword or the function is missing (pre-M5-T152) or the kit is
disabled, the page prints one short line. The allowance comparison chart is the report's OWN inline
SVG (a simple bar is presentation, not law); every printed number on it is a document figure.

Two tests are marked `skipif` until M5-T152 lands the `frame` keyword and `render_floor_stack`:
`test_site_plan_report_frame` and `test_floor_stack_report_frame`. The run reports them as `2 skipped`.
The orchestrator runs them after integration.

## Acceptance scenarios

S1-S12 are implemented as tests. S1-S11 in `tests/drawings/report/test_report_pages.py` (six page
types in order, each opening with its reader question; one scenario sheet for the benchmark and two
for the two-building synthetic document; CSS sheet/furniture; scheduled wording + no forbidden words;
no developer information on the benchmark and the partial-data document; eleven options + shared
limitations once; no min-base contradiction; maps-only-when-present; lot-area basis quoted; labels on
every committed fixture; number discipline; partial-data; escaping). S12 (the route) in
`tests/api/test_report_read_api.py`. S13 (the contract record) is below. Every expected figure is read
from the document, never retyped.

## S13 - presentation contract

Inserted a dated change entry ABOVE the adopted-brief marker in
`docs/design/ARCHITECT_PRESENTATION_CONTRACT.md`: heading
"Change 2026-10-10: report page types (D-090 source-081, rows R900 to R933)", the text of
`page-types.md` word for word, then one line naming the report's code paths. The brief below the
marker is byte-identical: `git diff --numstat` shows `29 0` (additions only, zero deletions) and the
sha256 of the marker-and-everything-below is unchanged (`225354013f46...`). The inserted page-types
text matches the source file verbatim (diff clean).

## Checks (DIRECT exit codes; `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`)

- `cd services/api && python -m ruff check .` -> `All checks passed!` - **RUFF_EXIT=0**
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/drawings/report tests/api/test_report_read_api.py tests/api/test_results_read_api.py` -> **149 passed, 2 skipped** - **PYTEST_EXIT=0**
- `python3 tools/modularity_check.py --check` -> **MODULARITY_EXIT=0** (no report module flagged; largest is `readers.py` at 316, well under the 600 warn)
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> `LANE COVERAGE PASS: 9859 file(s)` - **LANE_EXIT=0**

Benchmark report written to `/tmp/agent-a8199ae6bc0f48296-report.html` (21,744 bytes) and inspected:
all six page types present, the eleven options present and in the owner-approved order, no forbidden
result word, "Verified" appears exactly once (the label-key definition row).

## Two mutation proofs (out-of-repo copy at scratch; not committed)

- "achieved" put back into the scheduled line -> CAUGHT by
  `test_s3_scheduled_wording_and_no_forbidden_words` (the forbidden-word scan finds `achieved`).
- One shared limitation printed twice -> CAUGHT by
  `test_s5_eleven_options_shared_limitations_once` (the once-only count becomes 2).

## Assumptions and limitations

- The street address is not in the results document and is not fetched on the reuse path; the header
  uses borough/block/lot (documented fallback the brief allows).
- Per-section deep law links / review-register links are not reachable from the results document on
  this path; the evidence page renders readable ZR section references linked to the official Zoning
  Resolution site. No URL is invented.
- Options 2 and 3 (qualifying affordable/senior) show the qualifying floor-area allowance from the
  document (a real conditional figure) as their available result; options 4-11 show "Not produced
  yet". Two shared limitations (lot-area basis for options 1-3; "not produced yet" for options 4-11)
  are authored presentation sentences (no figures) and each appears once.
- Drawings (site plan, floor stack, maps) are short lines in this build because the `frame` keyword
  and `render_floor_stack` arrive with M5-T152; the interface calls are written and the two
  integration tests are skipped with a reason until then.

No STOP condition was hit: every file changed is inside the task's allowed paths.

## Rework 1 (orchestrator printed every page; twelve findings)

Integrated head base. What changed, by finding:
- F1 running header/footer written LITERALLY into the `@page` margin boxes (`string-set`/`string()` removed; Chromium ignores them).
- F2 the route accepts an optional `address` query parameter (<=120 chars, address charset, else ignored); shown as the title with borough/block/lot beneath.
- F3 the decision summary and the site page each fit one sheet; the empty context-maps section/sheet removed (the coverage inventory reports maps).
- F4 stale "shown when the drawing is available" captions removed; one caption per drawing.
- F5 the lot-area basis reads with the result it conditions ("The floor-area allowance holds if …"), the document's own words.
- F6 one row per constraint; the two coverage rows merged (by-portion rule + withheld, one Unresolved label); states named, never bare "Not shown".
- F7 the comparison chart reader fixed; doubled unit removed; columns Option / Floor-area allowance / Scheduled building / Status / Limitation; numbered shared limitations from the document's reasons (developer wording replaced).
- F8 open items carry a short structural effect with the full reason beneath in smaller type.
- F9 the label-basis assumption moved to the evidence provenance.
- F10 the coverage inventory uses three states and adds the six further sections plus context maps.
- F11 the evidence page: inputs table, envelope law sections, no-wrap figures, R783 label definitions; dropped "read from the result".
- F12 content kept within compact budgets; the orchestrator confirms page fit on print.
Checks (rework 1): ruff 0; pytest 149 passed / 2 skipped; modularity 0; lane 0. Mutations: "achieved" -> S3; shared limitation twice -> S5.

## Rework 2 (printed from the real route on the preview; browser test; ten findings)

Base `475404f114333da71fc564b29faebcc781b9dc8b`. What changed, by finding:
- A1 the e2e harness (`apps/web/e2e/harness/fixture_api.py`) turns on `LANE_E_ENABLED` for its process only, so the drawing kit renders on the real route; proven by a route test.
- A2 no non-drawing CSS rule sets a font below 8 pt (the open-item detail row raised 7.5 pt -> 8 pt); a CSS test enforces it.
- A3 an open item's detail line is omitted when it only repeats the item's name (the not-checked items).
- A4 the compact `frame="summary"` site plan now draws on the decision summary (M5-T152 added it); the fallback line goes when the drawing is present.
- A5 the zoning identity line is "Zoning district R6B · Commercial overlay C2-2" from the scope assumptions' structured values, never a joined fragment.
- A6 the bar-chart value labels have room; Building B uses the full scheduled line; "Building A – not worked" uses an en dash with the X4 label from its gap kind (Unresolved); the Limitation column shows only the number; the allowance keeps the area on one line with the FAR on a second.
- A7 the evidence inputs use the document's own labels ("Lot frontage", "Lot within 100 ft of the street-line intersection"); the law-link section number never breaks.
- A8 context maps read "Not yet in this report", note "Map data is not yet fetched for the report."
- A9 an unavailable drawing's line names it ("The site plan is not available for this report.").
- A10 this report's Rework 1 and Rework 2 sections.
Checks (rework 2): ruff 0; pytest 170 passed / 0 skipped; modularity 0; lane 0. Benchmark report (LANE_E on) at /tmp/agent-a8199ae6bc0f48296-report.html. No STOP: every changed file is inside the task's allowed paths.

## Rework 3 (whole browser suite; every drawing printed at 0.75 size)

Base `8b82814f3cb1462941c427dffb373546f4f1f239`. Cause confirmed: the kit's SVGs carry UNITLESS `width`/`height` (points), which a browser reads as CSS px (1px = 0.75pt), so drawings printed at 0.75 of size and their labels fell to 5.6-6.8 pt.
- D1 every embedded drawing (kit drawings and the report's own bar chart) is stamped `width="<w>pt" height="<h>pt"` from its viewBox (`drawings_embed.size_svg_to_points`), so it prints at its designed size; the stylesheet sets no size on an svg and never shrinks one. Benchmark viewBoxes (512x422, 238x224, 360x376 pt; bar chart 500 wide) all fit the 182 mm content box.
- D2 a test checks every embedded SVG's displayed pt size equals its viewBox and every SVG text font size (viewBox units) is >= 7, and the CSS sizes no svg.
- D3 page budget: with true sizes the benchmark site page holds the lot-area basis, the 512x422 pt plan and the constraints table within one A4 sheet (~250 mm < 269 mm content height); the figure stays whole (break-inside: avoid) and the constraints table flows after it, so if content grows the table continues to a second sheet with no near-empty sheet.
- D5 the running header joins with " · " and does not repeat the borough ("215-16 Northern Boulevard, Queens · block 7334, lot 70").
- D6 every mention of a scheduled building uses the one phrase "Scheduled floor area: N sq ft; site fit unverified" (the worked-and-not-worked list included); a test enforces it.
- D7 the site plan has its own block with space above (figure margin-top), so the top street name no longer touches a line above.
- D8 the tax-map-outline caption is stated once, below the drawing: the report's redundant line above is removed; the single caption is the kit's own "Lot outline: Approximate - tax map" inside the SVG. NOTE: making that caption text the report's own would require editing the kit SVG (`services/api/app/drawings/kit/**`, M5-T152's scope); flagged for the orchestrator.
Checks (rework 3): ruff 0; pytest 173 passed / 0 skipped; modularity 0; lane 0. Benchmark report (LANE_E on) at /tmp/agent-a8199ae6bc0f48296-report.html.

## Rework 4 (7-page print: near-empty page 6; floor stack captioned twice)

Base `a719082efe312d2b13c2859840a7f99f12ab6565`.
- D9 the coverage of the promised sections moved OFF the assumptions page (where it held a near-empty sheet) ONTO the decision summary as a compact block "What this report covers", grouped by state in a few lines: In this report (sections); Partly (each with its short note, e.g. "Development options (1 of 11 options worked)"); Not yet (sections, the owner-held "Financial analysis inputs (held)"). Same content and states; a new module `coverage.py` holds the data and grouping; the assumptions page no longer carries the table. The F10 test now checks the compact block on the decision summary and its absence from the assumptions page.
- D10 the floor-stack section keeps ONE caption - the report's own "Floor-stack section (Illustrative): drawn from the schedule only, with no placement on the lot." (with the Illustrative label). The drawing's own in-SVG caption is dropped by M5-T152 in the report frame; no report change was needed to keep one caption, and the single-caption test (test_f4) still holds.
- D11 this section.
Checks (rework 4): ruff 0; pytest 173 passed / 0 skipped; modularity 0; lane 0. Benchmark report (LANE_E on) at /tmp/agent-a8199ae6bc0f48296-report.html; the report is 6 page types for the benchmark.
