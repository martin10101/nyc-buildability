# M5-T159 (builder) producer report — report law links go to the exact ZR section

Task: D-094 P-1 / R027 — the report's evidence-page law links go to the exact
Zoning Resolution section URL from the repository's own captures, never the
homepage; a section with no capture prints as plain text.

Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a420ac72737ca9cc4`
Base: reset to `439e22b26e17283e49c9540715becba5ce86ae5b` (branch
`task/wave23-density-zoning-lot`), "Wave 23: G0 PASS for M5-T159 at its contract head".

## Files changed
- `services/api/app/drawings/report/law_links.py` — NEW module (117 lines; filled
  from the G0 placeholder). `section_url(cited)` resolves a cited section to the
  exact captured section URL or `None`; `official_zoning_text_url(value)` mirrors
  the website allowlist. The section index is built once through
  `app.rules.snapshots.SnapshotStore` and returned as a read-only `MappingProxyType`.
- `services/api/app/drawings/report/page_evidence.py` — removed the `_LAW_URL`
  homepage constant; `_law_links` now links to `law_links.section_url(section)` and
  prints plain text when there is none. Visible labels unchanged. (+8 / -3)
- `services/api/app/drawings/report/sources.py` — added `zr_section_page_number`
  (bare section page, sub-paragraph dropped) + `import re`; left `zr_section_number`
  (the visible-label helper, keeps the sub-paragraph) unchanged. (+19 / -1)
- `services/api/tests/drawings/report/test_report_law_links.py` — NEW tests
  (217 lines; S1–S6), built through the real builder on the benchmark fixture.
- `project-control/reports/M5-T159-producer-report.md` — this report.

`git diff --stat`: 4 code/test files, 361 insertions, 6 deletions.

## What each benchmark section now links to
The evidence page's `present_values` (non-withheld) rows are the only cited
sections rendered: floor_area_allowance cites `ZR 23-22` (4 rows),
permitted_envelope cites `ZR 23-432` (6 rows) → 10 law hrefs, matching the
planner's measured count.
- `23-22` (×4) → `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-22`
- `23-432` (×6) → `https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432`
Both equal the captures' own `source.request_url`. No href is the homepage.

## Design notes
- The section page for a sub-paragraph is the leading `<n>-<n>` of the citation;
  `23-52(b)` → page `23-52`, visible label keeps `23-52(b)`.
- Every candidate URL is validated by a faithful Python port of
  `apps/web/src/lib/architect/source-links.ts` (https, host
  `zoningresolution.planning.nyc.gov`, no query/credentials/port, path
  `/article-<roman>/chapter-<n>[/<section>]`, anchor only `#<n>-<n>`).
- Index-build guard: a capture is used for a section only when its `request_url`
  passes the allowlist AND its last path segment equals that section page. This
  drops captures whose `source.request_url` records a wrong host
  (`zr.planning.nyc.gov/entityprint/pdf/node/...` — e.g. zr-23-421-g,
  zr-23-421-r1-r2, zr-23-424-r1-r2, zr-11-25) or a chapter-only URL
  (zr-34-23-contents → `/article-iii/chapter-4`), fail-closed to plain text. The
  main section snapshot (shortest id) supplies the valid URL for those sections.

## Research & verification (D-093)
- Opened the capture files under `services/api/app/_zr_snapshots/v1/` (loaded by
  `rules/snapshots.py`) and confirmed the URL form each records in
  `source.request_url`: the article/chapter/section form
  `https://zoningresolution.planning.nyc.gov/article-<roman>/chapter-<n>/<section>`.
  Verified for 23-22, 23-52, 12-10, 23-344, 23-342, 23-362, 23-433, 23-432, 33-121.
- Confirmed across all 185 snapshots (128 distinct section numbers) that NO
  `source.request_url` records an anchor (`#`); therefore no anchor is ever added,
  satisfying "an anchor is added only where the capture records one". The anchor
  path is implemented and tested anyway (allowlist accepts `#<n>-<n>`).
- Did not fetch the live ZR site: the task says never guess a URL and use the
  repository captures as the authority; no URL is synthesized — every link is a
  capture's recorded `request_url`, allowlist-validated.
- Could not check: live reachability/currency of the recorded URLs (not required;
  no network used); the `docs/research/zr-snapshots/v1/` copy was taken as
  byte-identical per the in-sync note and the packaged copy is what the loader uses.

## Self-checks (all from the lanes venv on PATH)
- `cd services/api && python -m ruff check .` → `All checks passed!` (exit 0)
- `cd services/api && python -m pytest -q -p no:cacheprovider tests/drawings tests/rules`
  → `2143 passed, 6 skipped, 1 warning` (exit 0)
- New file alone: `pytest tests/drawings/report/test_report_law_links.py` → `21 passed` (exit 0)
- `python3 tools/modularity_check.py --check` → exit 0 (only pre-existing warnings;
  no new file flagged)
- `python3 scripts/lanes/check_lane_paths.py --coverage` →
  `LANE COVERAGE PASS: 10074 file(s)` (exit 0)

## Mutation proof
Reintroduced the homepage bug for one section: in `page_evidence._law_links`,
forced `url = "https://zoningresolution.planning.nyc.gov/"` whenever the section
number contained `23-22`. Running S1/S4/S6:
- `test_s1_every_href_is_the_exact_section_and_never_the_homepage` FAILED
  (`assert _HOMEPAGE not in hrefs`),
- `test_s6_only_link_targets_change_labels_and_text_stay` FAILED (same),
- `test_s4_every_rendered_href_passes_the_allowlist` FAILED
  (`official_zoning_text_url('…/') == None`).
Reverted the mutation; `grep MUTATION` finds nothing; the 21 tests pass again.

## Not touched / out of scope
- `readers.py` and `tests/drawings/report/test_report_pages.py` — untouched
  (another builder owns them). No existing test pins the homepage URL, so no STOP.
- `test_f11_evidence_inputs_label_key_and_nowrap` still green: the
  `<span class="nowrap">23-432</span>` label is preserved; only the href changed.

## Nothing needed outside scope.

## Addendum — test made fixture-derived after M5-T157 integration (G3 rework)

At integrated head `2bbfed94`, M5-T157 changed the shared benchmark fixture
(outside this task's scope): a new shown value in `floor_area_allowance` ("Legal
dwelling-unit limit ... 20,150 ÷ 680 = 29.63") cites `ZR 23-52`, `ZR 23-52(b)` and
`ZR 11-25`. The evidence page now renders 12 law hrefs (23-22 ×4, 23-52 ×2, 23-432
×6); `11-25` is captured only on the wrong host (`zr.planning.nyc.gov/entityprint/
pdf/node/18433`), so it correctly prints as plain text with no link. **Production
code is unchanged and correct.** Only `test_report_law_links.py` was too rigid: S1
and S6 hard-coded `len(hrefs)==10` and the `{23-22, 23-432}` set.

Fix (test file only): S1 and S6 now derive expectations from the fixture + capture
files and never depend on how many values the fixture shows (M5-T158 part B will
change it again). For every section the page renders: a section whose capture
records an official section-page `request_url` gets exactly one link equal to that
URL (last path segment == section); a section with no such capture prints as plain
text (no `</span></a>`); no href is the homepage; `Counter(hrefs)` equals the
derived expected links. A new explicit test `test_s1_known_sections_link_or_print_
plain_from_captures` asserts 23-22, 23-52 (incl. from `23-52(b)`) and 23-432 link
to their section pages and 11-25 is plain text — each URL read from the capture
files, none typed. The oracle `_capture_section_url(page)` scans the capture dir
and selects the capture's own `request_url` on the official host ending at that
section; it uses local parsers, not `law_links`/`sources`.

Self-checks at `2bbfed94` (lanes venv):
- `python -m ruff check .` → `All checks passed!` (exit 0)
- `pytest -q tests/drawings/report tests/rules` → `1204 passed` (exit 0)
- new file alone → `22 passed` (exit 0)

Mutation proof (repeat): forced `url = ".../"` (homepage) for the `23-22` section in
`page_evidence._law_links`; `test_s1_every_rendered_section_links_to_its_capture_
or_prints_plain`, `test_s1_known_sections_link_or_print_plain_from_captures`,
`test_s4_every_rendered_href_passes_the_allowlist` and
`test_s6_only_link_targets_change_labels_and_text_stay` all FAILED (4 failed, 18
passed); reverted; `grep MUTATION` finds nothing; 22 pass again. Only
`test_report_law_links.py` is modified in this rework.
