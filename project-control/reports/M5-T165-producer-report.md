# M5-T165 producer report — report page 1 rebuilt to the design-contract change of 2026-10-11

Producer: backend-engineer. Worktree base: `d248293a0e8b77ea795cca73626443970e3a3506`
(`task/wave24-report-v3`). An earlier builder was stopped mid-task at a session handoff;
its unfinished 11-file patch (`M5-T165-builder-unfinished.patch`, base adc36fc7, no tests)
was applied first, read critically against the packet and contract, then carried to
completion. I own the result.

## 1. What changed and why

**Page 1 (decision summary), `page_decision_summary.py`** — rebuilt to the four kinds of
content plus named furniture (ARCHITECT_PRESENTATION_CONTRACT.md, "Change 2026-10-11",
"Page 1"): (1) results in large type, each with its assumption line (R055) and the allowance
phrase beside the headline (R029); (2) one site graphic in its unchanged wrapper; (3) the
legal ceiling beside the apartment estimate in one block with the token distinction line, the
estimate linking to its full calculation on the scenario sheet (R071/R078/R013); (4) at most
three uncertainties in the order zoning lot, lot-area basis, rear yard, each linked to
`#issue-<n>` (R050). The coverage inventory left the report (R012); a compact scope line on
page 1 points to the material-exclusions block at the head of the appendix. The property-
specific zoning-lot sentence names the register's INDEX ENTRY, never the instrument (R030);
the generic line shows only in the not-checked state.

**Print type scale, `layout.py`** — every print size now interpolated from the TYPE tokens
(no hard-coded pt); section-title 14 pt; headline 30 pt (28–32 band). Stale page-2 CSS comment
reworded to the one-locator composition. (I also wrapped three CSS rule lines that the earlier
patch left over 100 chars — ruff E501; behaviour-identical, only added newlines inside CSS rules.)

**Tokens** — `presentation-tokens.json` / `presentation_tokens.py` / `presentation-tokens.mjs`
gained a `wording` group (distinction line, the two zone labels, the area-illustration caption),
each byte-equal to the contract quote. The generator renders the long string as implicit-
concatenation chunks so every Python line stays ≤100 chars. The CSS block does not carry
`wording` (report/website copy, not CSS). `test_presentation_tokens.py` GROUPS gained `wording`
and a new assertion pins the three texts (S16).

**Refactors (G-6 isolation)** — the zoning-lot logic moved from `readers.py` to new
`zoning_lot_item.py` (marker, `zoning_lot_basis`, `zoning_lot_open_item`, the page-1 index-entry
sentence); the constraint effect texts moved to new `constraint_text.py`, which reads the open-
item category. Every moved text keeps its 1.4.0 output EXCEPT: `lot_area` now names the GIS
outline "city map outline" not "tax-map outline" (NB-04: the 10,387.99 sq ft outline area is
basis `gis`; contract G-10); `rear_yard` is the open check (NB-03; names ZR 23-344(b) and
(c)(3) as not yet checked, draws no conclusion, links 23-344). `readers.py` re-exports
`zoning_lot_basis` as a facade and stays ≤600 SLOC / ≤40 symbols (32 symbols).

**Scenario sheet, `page_scenario_sheet.py`** — the long apartment-estimate sentence prints ONCE
(the page-1 duplicate is gone; page 1 shows the range and links to `#estimate-<building>`, R013).

**`unit_limit_text.py`** — new `legal_ceiling()` reads the standard-residence ceiling from the
document: shown → value + its own label (Conditional for the benchmark 29, never Provisional or
settled); withheld → the document's own reason, no number.

**`open_items.py` NOT created** — the packet lists it as an *optional* path. The open-items
list stayed in `readers.py` because that keeps `readers.py` within its size/symbol ceiling; no
new module was needed. Flagged for the G1/G3 reviewers.

## 2. New page-1 visible text (benchmark, normalized)

> Decision summary · Queens block 7334, lot 70 · Zoning district R6B · Commercial overlay C2-2 ·
> the city's register lists a zoning lot description recorded 2022-02-08 against lots 1 and 70 ·
> Preliminary zoning results: a labelled, unreviewed draft. Each figure carries its source in the
> Zoning Resolution. Professional review is advisory. · What can I potentially build? ·
> [Answer | Result | Status] · Floor-area allowance | 20,150 sq ft (FAR 2.0) · 10,075 sq ft
> recorded lot area × FAR 2.0, tax lot 70 alone · 20,150 sq ft is a conditional tax-lot-only
> arithmetic allowance, not established remaining development rights. | Conditional · Permitted
> envelope | Base 30 ft to 45 ft; building up to 55 ft · R6B height limits | Conditional ·
> Scheduled building | Scheduled floor area: 20,150 sq ft; site fit unverified · 3 storeys; 30 ft
> | Conditional · The site plan is not available for this report. · Legal ceiling 29 Conditional ·
> Estimate 17-22 Provisional · The ceiling is a conditional zoning limit; the estimate is an
> unvalidated apartment-yield range; neither is a demonstrated layout. · What is still uncertain ·
> Zoning lot Conditional · Recorded lot area Conditional · Rear yard ZR 23-344 Unresolved · The
> material exclusions are listed at the head of the appendix.

(The site graphic renders as a drawing when the site-context plan / LANE_E is available; on the
plain benchmark it falls back to the short line above.)

## 3. Per-section visible word counts (header/footer excluded), before vs after

| Section | Before (base d248293a) | After | Cap |
|---|---|---|---|
| decision-summary (page 1) | 330 | **190** | ≤200 (G0) |
| site-and-context | 202 | 202 | — |
| option-comparison | 319 | 319 | — |
| scenario-B | 199 | 199 | — |
| assumptions-open-items | 949 | 996 (exclusions block moved here) | — |
| calculations-evidence | 460 | 460 | — |
| **total (whole body)** | **2448** | **2355** | ≤2448 (G0 / before set) |

Repeat count (sentences ≥8 words printed ≥2×, period-delimited): before 2 distinct / 5 printings;
after 2 distinct / 5 printings. Against the contract's named before set (3 distinct / 7 printings,
PDF, main b4704161) the HTML stays below and does not rise. (The owner's relayed builder note
"3→2 distinct, 7→5" compares that contract before set to the HTML now.) No page-1 sentence of ≥8
words appears anywhere else in the report.

## 4. State table (state → outcome → test). Expected values from the packet/contract/records.

| Input state | Outcome on page 1 | Test |
|---|---|---|
| benchmark, ACRIS zoning-lot condition present | property-specific sentence "…recorded 2022-02-08 against lots 1 and 70"; no generic line | test_s2_zoning_lot_sentence_names_the_register_index_entry |
| document with NO register condition (`synthetic_scope_tax_lot_only_northern`) | generic "the app does not verify the zoning lot" once; no property-specific sentence | test_s2_generic_line_only_in_the_not_checked_state_and_once |
| standard ceiling shown (benchmark, 29) | "Legal ceiling 29" + Conditional; never Provisional/settled | test_s4_ceiling_and_estimate_sit_in_one_block_with_the_token_line |
| standard ceiling withheld (synthetic reader doc) | ceiling half shows the document's own reason; no number | test_s4_withheld_ceiling_shows_unit_limit_texts_reason |
| 1.4.0 rear-yard state | open check: names 23-344(b) and (c)(3), no conclusion, links 23-344 | test_s19_…, test_benchmark_rear_yard_reads_as_the_open_check |
| three uncertainties available | order zoning_lot, lot_area, rear_yard; ≤3 | test_s5_three_uncertainties_in_order_with_the_rear_yard_open_check |
| coverage inventory | absent from the report; scope line on page 1; exclusions head the appendix | test_s12_…, test_f10_r012_coverage_inventory_leaves_the_report |
| lot-area GIS outline | effect text says "city map outline", never "tax-map outline"; page 1 has no "tax map" | test_s18_lot_area_effect_names_the_city_map_outline_not_tax_map |
| moved effect texts | coverage/placement/setback/street_wall/parking + zoning-lot effect unchanged (1.4.0) | test_s13_moved_effect_texts_keep_their_1_4_0_output_except_the_rear_yard |
| long apartment-estimate sentence | printed once (scenario sheet), page 1 links to it | test_s17_…, test_report_pages.py::test_vc2 |

## 5. Commands (direct exit codes)

| Command | Exit | Result |
|---|---|---|
| `python -m ruff check .` (services/api) | 0 | All checks passed |
| `python -m pytest -q tests/drawings tests/cad tests/journey tests/api/test_report_read_api.py tests/api/test_report_read_context.py` | 0 | 1760 passed, 6 skipped |
| `node scripts/presentation-tokens.mjs --check` (apps/web) | 0 | CSS block and Python module match the source |
| `node --test scripts/tests/presentation-tokens.test.mjs` | 0 | 10 pass, 0 fail |
| `python3 tools/research_record_check.py --check` | 0 | PASS; NB-01 code_current=True, review_state=stale |
| `python3 tools/modularity_check.py --check` | 0 | no new offender (readers.py within ceilings) |

(apps/web `node_modules` is absent; the token generator and its node test are standalone and
run without it. e2e / server never started; ports 3000/3001/8000 untouched.)

## 6. Mutation proof (each reverted; green restored)

1. **Rear-yard text** reverted to "The rear yard is not known beyond the corner area." →
   `test_s19_…` and `test_benchmark_rear_yard_reads_as_the_open_check` FAILED on
   `assert "rear yard is not known beyond the corner area" not in text`. Restored → 2 passed.
2. **Distinction-line token** one char changed (`limit`→`Limit`) in `presentation_tokens.py` →
   `test_s4_…`, `test_module_mirrors_the_json_source`, `test_wording_group_…` FAILED
   (module ≠ contract quote and module ≠ JSON). Restored → 3 passed.
3. **Coverage inventory re-added to page 1** → `test_s7_page_one_section_is_within_the_word_cap`
   (page 1 over 200 words), `test_s12_…` and `test_f10_r012_…` FAILED
   (`"What this report covers"` back in the report). Restored → green.

## 7. NB-01 revision note

Revision 3 → 4, status unchanged (`access_blocked`). Added `zoning_lot_item.py` to `code_paths`
and `code_identity` (`f3595523…`); updated `readers.py` code identity to `91f607aa…` (reflects
M5-T162's change and this task's). `code_current` is now True; `review_state` is `stale` pending
the G1 re-stamp (a producer cannot self-review). Recorded in `dependency_assessment`: the G-6
isolation (logic moved to `zoning_lot_item.py`; `readers.py` keeps the facade + open-items
wiring; marker held in step with `result_way_conditions.py` by a test) and my **code-path
proposal** — readers.py should STAY in code_paths (facade + open-items wiring still carry NB-01
behaviour); the G1 reviewer decides.

## 8. What I could not check / limitations

- **S18 residual (flagged).** Within this task's allowed paths the lot-area effect text now says
  "city map outline". But the scenario engine still emits "tax-map outline" / "approximate tax
  map" for GIS-basis values (NB-04), and those sentences render on the site-and-context,
  option-comparison, appendix open-items and evidence sections via the document's own words. All
  of those producers (`app/scenario/**`, `page_site_context.py`, `page_option_comparison.py`,
  `page_evidence.py`, the fixtures) are FORBIDDEN here, so the whole-report "tax-map outline"
  wording is NOT fully removed by this task. My S18 test is scoped to what this task controls
  (the effect text + page 1). Recommend a follow-up/backlog item for the scenario-engine wording
  (owed to the site task / a scenario-engine task). `test_report_pages.py::test_s7_lot_area_…`
  still asserts the document's "tax-map outline" on the site page and is left unedited (out of
  scope).
- **review_state = stale** on NB-01 is expected and correct for a producer; G1 makes it current.
- Research: I opened the primary records NB-01 (ACRIS index evidence, ZR 12-10), NB-03 (rear-yard
  23-344(b)/(c)(3), status interpretation_awaiting_review), NB-04 (lot dimensions; the 10,387.99
  outline is basis gis, conflicting_evidence) and read NB-05. I did NOT re-open the live ACRIS /
  ZR sources (no network use required; the records are current, checked 2026-10-11). Every
  unresolved input stays unresolved: the zoning lot is Conditional, the lot area Conditional, the
  rear yard an Unresolved open check.
- PDF page counts / printed point sizes are checked by eye in H2 (not by this builder); the
  larger type scale may add a page (fonts were not shrunk).

## Rework 1 (visual G3 of 2026-10-11; base 7ab4bda5)

Addressed the visual G3 FAIL on page 1 (plus the G3/G4 in-scope advisories). Only
`page_decision_summary.py`, `layout.py` and `test_report_page_one.py` changed. I printed the
benchmark report in-process (`make_after_report.py` with the map-context pack, so M5-T166's close
frame renders), converted to PDF (`print-report-pdf.mjs`) and rendered the pages (`pdftoppm`) to
check by eye; no server, no ports.

**What changed and why**
1. **Key figure only at the headline size (REQUIRED #1).** `_answer_cell` now takes a short
   `key_figure` (headline 30 pt) plus a body-size `detail`, and `_answers_table` reads the key
   figure from the document's own value fields: Floor-area allowance = `max_residential_floor_area`
   display ("20,150 sq ft"), detail "FAR 2.0"; Permitted envelope = "Up to " + `max_building_height`
   display ("Up to 55 ft"), detail "Base 30 ft to 45 ft"; Scheduled building = `scheduled_display`
   + " sq ft" ("20,150 sq ft"), detail the whole fixed X5 wording "Scheduled floor area: N sq ft;
   site fit unverified". No figure is recomputed and no sentence is cut up by a pattern. New
   `.answer-detail` CSS at the body token. The 30 pt sentence-towers are gone.
2. **Status column clear of the figure (REQUIRED #2).** With short key figures the Result column no
   longer blows out the table width, so the answers table and the 88 mm figure sit side by side
   within the printable width and every "Conditional" badge prints in full. `.summary-answers`
   (flex 1 1 auto; min-width 0) and `.summary-figure` (flex 0 0 88mm) are unchanged (S14 /
   test_correction2). A CSS-level test guards the fit.
3. **Decision summary fits page 1 (REQUIRED #3).** Headline `line-height: 1.1`, tighter block
   margins (standing label, ceiling-estimate, uncertainties, scope line, h1), tighter answers-table
   row padding and uncertainty-list margins, and `break-inside: avoid` on the uncertainties so the
   list never splits. All four kinds of content and all named furniture (including the scope line)
   now print on page 1; the page count fell from 11 to 10 (the spill page is gone). No font was
   shrunk below its token.
4. **Fallback caption + docstrings (CORRECTIONS #4/#5).** The page-1 fallback site-plan caption is
   now "Site plan: the lot's city map outline (not surveyed)." (a GIS outline is never "tax map").
   The module docstring/comment say "compact close frame" (M5-T166 rework 1). The layout.py
   docstring now says every FONT SIZE is read from a TYPE token (borders, line weights and letter
   spacing stay literal). Left alone per the rework: readers.py `_BASIS_NAMES['approximate_tax_map']`,
   test_s7's site-page "tax-map outline" assertion, and all engine text (the DB-245 GIS sweep under
   the narrowed S18).

**Page-1 / page-2 description (my own print, 10 pages total).** Page 1 holds, top to bottom: the
identity (Decision summary; Queens block 7334, lot 70; Zoning district R6B · Commercial overlay
C2-2; the register index-entry sentence "…recorded 2022-02-08 against lots 1 and 70"); the standing
label; "What can I potentially build?"; the three-row answers table with each key figure at 30 pt
(20,150 sq ft; Up to 55 ft; 20,150 sq ft), its body detail, its assumption line, the allowance
phrase, and the Status badge "Conditional" fully visible; the compact close frame (Lot 70 among its
neighbours, north arrow, scale bar, "The lot among its neighbours (city map; not surveyed).");
"Legal ceiling 29" (Conditional) beside "Estimate 17-22" (Provisional, links to #estimate-B) with
the distinction line; "What is still uncertain" with Zoning lot (Conditional), Recorded lot area
(Conditional), Rear yard · ZR 23-344 (Unresolved); and the scope line. Page 2 begins the next page
type, "Site and context" — nothing from the decision summary spills.

**New tests.** `test_rework1_headline_holds_only_a_key_figure_not_a_sentence` (every `.answer-figure`
is ≤4 words with no clause separator; the fixed scheduled wording is a body detail) and
`test_rework1_answers_table_and_figure_fit_printable_width` (figure flex basis + gap < 182 mm
printable; answers can shrink). S1 (page-1 items) and S7 (page 1 ≤200 words, total ≤2448) still hold.

**Word counts (no-map benchmark, as tests measure).** Page 1 = 192 words (≤200); total = 2318 words
(≤2448). (The site-and-context section's count moved with M5-T166's rework at this head, not mine.)

**Checks (direct exit codes, lanes venv).** `ruff check .` = 0 (All passed). `pytest -q tests/drawings
tests/cad tests/journey tests/api tests/scenario/three_answers/test_result_ways.py` = 0 (3015 passed,
6 skipped). `node presentation-tokens.mjs --check` = 0; `node --test presentation-tokens.test.mjs` = 0
(10/10). `research_record_check.py --check` = 0 (NB-01 code_current=True; unchanged this rework).
`modularity_check.py --check` = 0.

**Mutation proofs (restored byte-identical, re-verified green).** (A) envelope key figure set back to
the whole sentence "Base 30 ft to 45 ft; building up to 55 ft" →
`test_rework1_headline_holds_only_a_key_figure_not_a_sentence` FAILED (11 words ≤ 4). (B)
`.summary-figure` widened to `flex: 0 0 200mm` → `test_rework1_answers_table_and_figure_fit_printable_width`
FAILED (200 + 6 ≥ 182). Both restored → green.

**What I could not check.** The live website/preview and real browser (no server/ports); printed
point sizes are by eye. NB-01 unchanged this rework (no code path touched); review_state stays stale
pending G1. Every unresolved input stays unresolved (zoning lot Conditional, lot area Conditional,
rear yard an Unresolved open check).
