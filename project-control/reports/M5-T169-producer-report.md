# M5-T169 producer report — option comparison, evidence appendix, run identity (P-3b/c)

Producer: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ad2eafad411f91f7d`.
Contract base (reset head): `fdfd2749261366dfb219710c69e0dc25235f69ab` (claim head on `task/wave27-comparison-appendix`;
main `76745ade` after the wave-26 merge + the wave-27 contracts). Render-only change; no engine/schema/fixture change.

## What changed, per scenario

- **S1 (page 3, table first; R075/R059/R084).** `page_option_comparison.render` now emits the 11-row table BEFORE the
  chart; the `_shared_limitations` block of `<p><strong>Limitation N.</strong>` paragraphs is removed; the "Limitation"
  column is dropped. Options 1-3 carry figures; options 4-11 read "Not evaluated in this report"
  (`options._NOT_PRODUCED`, was "Not produced yet") in the owner-approved order. Verified: no `<p><strong>Limitation`
  remains in the section; `count("Not evaluated in this report") == 8`.
- **S2 (chart; R018/R020).** `drawings_embed.allowance_bar_chart_svg(..., placed_on_site=bool)` distinguishes three
  things on one zero-based scale: the floor-area allowance bar, each worked building's "<Building> scheduled" bar, and a
  "Placed on site" STATUS row ("Not demonstrated" when nothing is placed; "Shown on the site plan" when placed) rendered
  with NO rectangle — an unknown is never a zero-height bar. The page passes `placed_on_site = not building_not_placed`.
- **S3 (five-field issue records; R025/R054).** The appendix open items are issue / consequence / next action /
  responsible role / evidence reference (`open_items.appendix_issue_records`). Missing site documents carry
  "Owner or surveyor"; program work carries "This program". The honest "A check not yet made against an independently
  worked example." next action is de-duplicated to at most ONCE. `id="issue-N"` anchors are byte-stable (page-1/page-3
  "see item N" links still resolve; `test_constraint_rows.py::test_s9_every_issue_href_resolves_to_an_anchor` green).
- **S4 (input_facts bases; G-10).** New `readers.input_facts` (defensive 1.5.0 reader; empty on a 1.4.0 doc) +
  `open_items.input_fact_rows`/`basis_label` with the nine closed bases' plain words. Read from the 4-entry block, NOT
  hard-coded. The work order's "103.88 = city map outline (GIS)" example is FALSE and was NOT asserted (103.88 is the
  approximate tax-map frontage in scope.assumptions; the gis basis is the 10,387.99 lot_outline_area) — conflict
  preserved, not reconciled (D-093).
- **S5 (worked arithmetic; R023/R026).** `open_items.worked_arithmetic` renders, read from the document:
  `10,075 sq ft (recorded lot area, city record) × 2.0 (FAR, zoning law) = 20,150 sq ft` and
  `20,150 ÷ 680 = 29.63 → 29` (the dwelling-unit equation read from the legal_unit_limit_standard label; the factor
  parenthetical is NOT repeated — it stays in the figures table, R077). No single figure mixes two bases: the floor-area
  line uses the recorded lot area (administrative_record), never the gis outline 10,387.99.
- **S6 (register linkage + review state; R027).** `open_items.register_rule_rows` reads
  `rules/review_register/register.json` (read-only, G-11) and maps each `rule_versions` entry to its short readable rule
  title + register verdict ("review: Not reviewed"). Statutory links still resolve to the exact captured section
  (M5-T159 untouched; `test_report_law_links.py` green).
- **S7 (run identity; R028/R038/R058).** New `run_identity.py`: `document_fingerprint` (sha256 over the document's
  values EXCLUDING `results_id`/`computed_at`, 12 hex) stable across runs and changing with any value; `deployed_commit`
  reads `RENDER_GIT_COMMIT`/`GIT_COMMIT_SHA` ("unknown" when unset) WITHOUT importing the API router module. The route
  (`report_read.py`) carries the commit via `identity={"commit": deployed_commit()}`. The appendix shows fingerprint,
  commit, revision, computed date. The status-label key is the only place "Verified" appears.
- **S8 (area-illustration method; R095/R092).** `page_evidence._area_illustration_method` renders once FROM an
  `area_allocation` block when present (M5-T164 synthetic fixtures): the stated share, the measure (residential floor
  area), the G-14 conversion statement, the bar-or-zones rule ("zones inside the placed footprint" / "proportional
  bar"), and the Illustrative label. Absent on the benchmark (no block until M5-T172).
- **S9 (merged appendix; R028/R077).** `page_assumptions` + `page_evidence` merged via `builder.py` into ONE section
  `id="appendix"`, type-name "Appendix", question "What remains unresolved, and how was this derived?". Section count
  6 → 5 (section-id/question/count lists in `test_report_pages.py` reworked, not deleted). Material-exclusions scope
  note heads the appendix.
- **S10 (word budget; R072/G-9).** Total HTML visible words = **2217 ≤ TOTAL_WORD_CAP 2448** (set at main b4704161 in
  `test_report_benchmark.py`). Repeated explanations removed (the scope-assumption input rows that duplicated the shared
  assumptions were dropped from the inputs table, R077; the zoning-lot/rear-yard/lot-area open-item detail rows that
  repeat page-1/page-3/assumptions were dropped, keeping only the unique material coverage + legal-limit reasons).
- **S11 (R032).** 39,934 is absent from the benchmark; the report emits no auto-subtracted remaining-capacity figure.
  NB-02 read, not revised.
- **S12 (R059/R084).** All eleven options stay in scope; the unavailable ones read "Not evaluated in this report".
- **S13 (real print).** Produced via the live route (see below).
- **S14/S17 (NB-01; DB-274).** `readers.py` edited (the new `input_facts` reader, no-op on a 1.4.0 document) → NB-01
  written to **revision 9** with the recomputed LF sha256 `12b2c0c3…537c53d` and a new dependency_assessment entry; the
  stale "(revision 7)" parenthesis of the revision-8 (M5-T170) entry is clarified (the M5-T170 work landed across
  revisions 7-8). `research_record_check.py --check` PASS. The G1 agent delta review is the reviewer's to record.
  NB-05's half of DB-274 is NOT in this task (NB-05 does not list readers.py in code_paths) — routed to the records task.
- **S15 (1.4.0 / modularity).** New 1.5.0-only blocks render only from 1.5.0 fields: on
  `synthetic_building_alternatives_contract_1_4_0` `readers.input_facts == []`, the area-illustration method and the
  input_facts table are absent, and no floor-area worked line appears. Appendix open-item + input_facts logic lives in
  the new `open_items.py` so `readers.py` crosses no modularity threshold; the `formatting.whole_percent_shares`
  largest-remainder helper carries a line-scoped boundary justification (re-rounds document shares; computes no zoning
  quantity). `modularity_check --check` PASS, no new failure (none of my files flagged).
- **S16 (DB-270 page count).** Real print returns to **10 pages** (main 2bcdb05a = 10; M5-T170 made it 11). See below.

## Input-state table (every basis read from the benchmark input_facts, never hard-coded)

| input_fact key | value | basis (enum) | plain-word basis shown | source shown |
|---|---|---|---|---|
| recorded_lot_area | 10,075 sq ft | administrative_record | city record | NYC Department of City Planning MapPLUTO, version 26v2 (as of 2026-09-30) |
| lot_outline_area | 10,387.99 sq ft | gis | city map (GIS measurement) | NYC Department of City Planning MapPLUTO, version 26v2 (as of 2026-09-30) |
| mapped_street_width:215 Place | 60 ft | gis | city map (GIS measurement) | DCP Digital City Map street center lines (as of 2026-09-30) |
| mapped_street_width:Northern Boulevard | 100 ft | gis | city map (GIS measurement) | DCP Digital City Map street center lines (as of 2026-09-30) |

Both gis facts share the plain word; the SOURCE TITLE distinguishes outline from street-width. A street-width row is
never labelled "city map outline"; no gis row carries any "tax" reference (G-10). The scope-assumption `lot_front_ft`
(103.88, basis `approximate_tax_map` → "Approximate tax map") stays an assumption, correctly NOT called "recorded" and
NOT a gis basis.

## Texts guard (owner-visible report text)

No internal names (record ids, gap numbers, "reference case", "milestone", "the caller") in any new sentence; no claim
that law text is "captured"/"built"; no default stands for a fact (the input_facts reader and area-illustration render
only when the 1.5.0 field is present; no truthiness test on an optional fact). Verified by the standing guards
`test_report_pages.py::test_s4_no_developer_information_*` (snake_case / developer-word / bare None scan), which pass on
the benchmark and the partial document. Returned texts are plain user texts.

## Checks (lanes venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider; heavy runs one at a time under flock)

| check | command | result |
|---|---|---|
| ruff (api CI first step) | `cd services/api && python -m ruff check .` | **exit 0** — All checks passed! |
| report suite | `pytest -q tests/drawings/report tests/api/test_report_read_api.py` | **exit 0** — 224 passed |
| three-answers emit (shared slice) | `pytest -q tests/scenario/three_answers/test_three_answers_three_way_emit.py` | **exit 0** — 60 passed |
| whole api suite | `cd services/api && python -m pytest -q -p no:cacheprovider` | **exit 0** — 9982 passed, 8 skipped (475.62s) |
| modularity | `python tools/modularity_check.py --check` | **exit 0** — no new failure; none of my files flagged |
| research record | `python3 tools/research_record_check.py --check` | **exit 0** — PASS; NB-01 code_current=True, status access_blocked |
| lane paths | `python3 scripts/lanes/check_lane_paths.py --coverage` | **exit 0** — 10676 files, each one lane |
| web lint | `cd apps/web && npm run lint` | **exit 0** — 0 errors, 2 pre-existing warnings (files I did not touch) |
| web typecheck | `cd apps/web && npm run typecheck` | **exit 0** — tsc --noEmit clean |

Web install: reused the primary checkout's `apps/web/node_modules` via a temporary symlink (same committed lockfile; no
package.json change), ran lint + typecheck, then removed the symlink (nothing untracked left). Playwright was NOT run
(CI runs it). The e2e spec `report-print.flag-on.spec.ts` PAGE_TYPE_TITLES went 6 → 5 (merged "Appendix").

## Mutation proofs (monkeypatched; real behaviour holds, mutation flips the assertion; nothing left on disk)

1. **Table-first order:** real table-before-chart=True; a chart-before-table render makes the S1 order check flip. ✓
2. **Merged-appendix section count:** real `report-page` count = 5; emitting the appendix twice yields 6, so the ==5
   check flips. ✓
3. **Run-identity fingerprint input:** real fingerprint stable across runs (excluding results_id/computed_at) AND
   changes with any value; a fingerprint that INCLUDES results_id is no longer stable across runs — flips. ✓
4. **One basis label (G-10):** real gis label "city map (GIS measurement)" (no "tax"); a mutated "tax map outline" label
   violates G-10 — flips. ✓

## Real print and page-by-page comparison (S13/S16/H2)

Rendered through the live route from `services/api`: TestClient POST `/api/v1/properties/4073340070/report` with
`benchmark_provider(with_zoning_lot=True, street_on=True)` + `recorded_pack_provider(benchmark_215_16_northern_window)`
(flags INTERNAL_RESULTS_ENABLED / LANE_A_ENABLED / LANE_E_ENABLED; `?address=215-16 Northern Boulevard, Queens` to match
main's running header), then `apps/web/scripts/print-report-pdf.mjs`. No server, no ports.

- Report-page sections: 5. Printed PDF pages: **10** (main 76745ade print = 11). `diff_pages.py` (before=main, after=mine):
  `pages: before 11, after 10`.
- pages 1-4, 6: text byte-identical except the running-header address CASE ("215-16 NORTHERN BOULEVARD" in main's
  recorded print vs "215-16 Northern Boulevard" from my harness input) — furniture only, not a code change.
- page 5 (option comparison): CHANGED — the 11-row table leads, the "Shared limitations / Limitation 1..5" paragraphs
  are gone, options 4-11 read "Not evaluated in this report", the chart carries the "Placed on site: Not demonstrated"
  row.
- pages 7-10 (merged appendix): CHANGED — "Appendix" heading, the five-field issue records, the input_facts table with
  bases + sources, the worked arithmetic, one combined figures-and-law table, rules/review + run identity, the
  status-label key printed once.
- page 11: REMOVED (the 11th page of main's print is gone).
- Open items: now span 2 physical pages (pages 7-8) — down from main's 3 pages; the appendix as a whole dropped from 5
  physical pages to 4 and the report from 11 to 10. See limitation below on DB-270's "single page" sub-clause.

## What I could not check / limitations / assumptions

- **DB-270 "open items no longer spill onto a second page":** the primary, test-pinnable requirement (≤10 printed pages)
  is MET (10). The open items still span 2 physical pages because the design-contract order puts the 13 shared
  assumptions before them on the first appendix page; forcing the table onto one page either reorders against the
  contract or cuts owner assumption content, and a `break-before: page` experiment REGRESSED the count to 11. I left the
  open items at 2 pages (an improvement from main's 3) and reduced their cell padding. Flagging for the reviewer/owner.
- **H2 PDF word total (≤2,993 hard / ≤2,713 target):** HTML visible words = 2217; I did not compute the PDF-extracted
  word total (that is an H2 reviewer check). The HTML cap and the 10-page count are both well within budget.
- **Run-identity commit on the benchmark reads "unknown"** (RENDER_GIT_COMMIT/GIT_COMMIT_SHA unset in the harness);
  tests tolerate "unknown" and inject a sha via `identity={"commit": …}`. The Render var name is still TO CONFIRM
  (build_info.py), unchanged by this task.
- **NB-01 review_state is "stale"** after the revision-9 bump (the latest recorded agent review is revision 4); this is
  expected and does not fail `research_record_check --check` (NB-01 requests no label). The G1 delta review is the
  reviewer's to record.
- Playwright e2e and full web suites + the dependency-security checks must pass IN CI on the exact head; I did not run
  Playwright (CI owns it). No forbidden file changed; no engine/schema/fixture change.
