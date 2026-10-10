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
