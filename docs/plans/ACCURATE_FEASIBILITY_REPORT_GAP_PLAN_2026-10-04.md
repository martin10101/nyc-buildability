# Accurate feasibility-report gap plan: what we still need to add (D-090 source-024, R142-R144)

Owner question (2026-10-04): the owner handed us a competitor's 88-page "Envelope" Zoning
Analysis and Massing Study for 215-16 Northern Boulevard as the KIND of report an architect
should be able to get back from our web app, and said the sample contains multiple errors.
The question this plan answers: what do we still need to add so our app returns a PDF of that
kind, but accurately?

Source text read page by page from the sample:
`/root/.claude/projects/-root-project-nyc-buildability/4d3637bc-346a-4b44-a0e7-b9688bc4f91a/tool-results/bfxv3rbfq.txt`
(88 pages). The sample is a shape-and-scope reference only. No number in it is treated as
truth here. Where a sample figure differs from our captured Zoning Resolution reading, this
plan says "differs; qualified review decides" and never says which is right.

This document changes no code, contracts no task, and changes no plan. The orchestrator
contracts the slices under the normal gates (CLAUDE.md principle 9).

---

## 1. Purpose and the accuracy rule

"Accurately" has a precise meaning for us, and it is the whole difference between our report and
the sample:

1. Every value is computed by deterministic code from captured official sources, and every fact,
   formula and figure carries provenance (CLAUDE.md principles 1-2; PRD section 9; the report is
   bound to one results document by id and canonical digest in
   `packages/contracts/schemas/v1/report_model.schema.json`).
2. Every legal reading is marked draft until a qualified reviewer approves it at G6. Today every
   rule in `services/api/app/rules/rulesets/*.rule.json` is `needs_review` and the coverage matrix
   (`services/api/app/rules/coverage/COVERAGE_MATRIX.md`) carries at most `implemented_draft`.
3. The report never says "complies", "approved" or "guaranteed". It shows the required disclaimer
   (PRD section 29) and leaves the legal conclusion to a licensed professional.
4. The sample is a form reference. Its imagery, its comparable-sale price-per-SF, its "max units"
   and its tax-abatement table are treated as scope we must reproduce only where we can source the
   number, never as answers we copy.

Four-state honesty (owner directive D-090-R133) runs through the whole plan and is never collapsed:
**built** = code exists; **connected** = wired into the 215-16 Northern path on the recorded-fixture
route (nothing is live today, all `LANE_*` / `INTERNAL_*` / `LIVE_*` flags are off); **tested** = an
automated test on recorded data plus an independent review PASS; **professionally verified** = a
qualified human approved the legal reading at G6, which is TRUE FOR NOTHING today.

---

## 2. Section-by-section gap table over the sample's contents

One row per section of the sample report. Columns b/c/t/v are the four states (built, connected on
the recorded-fixture path, tested, G6-verified). Y = yes, N = no, P = partial. "Repo evidence" is a
file path or PR; "Owner lane / gate / order" names the lane, the owner decision or hold, and where it
sits in the build order from section 4.

Every "we do not have X" claim below was checked with `git grep`; the exact searches and their
results are listed after the table (DB-122).

| Sample section | b | c | t | v | Repo evidence (path / PR) | What is missing | Lane / gate / order |
|---|---|---|---|---|---|---|---|
| Cover + executive summary (max ZFA, unit range, FAR, height, site-at-a-glance) | Y | P | Y | N | Three-answer engine `services/api/app/scenario/three_answers/engine.py` (#353); results `scope` block in `results.schema.json` 1.1.0, emitter in #405 (open); cards `apps/web/src/components/architect/answers/ThreeAnswersPanel.tsx` (#264); `DevelopmentLimits.tsx` "Not confirmed" | No rendered cover SHEET; `report_model.schema.json` defines `cover` but no builder produces a report_model | Lane C/E; gate: #405 owner yes, then report builder; order 4-11 |
| Property location maps + imagery (NYC overview, neighborhood, close-up, street view) | P | N | Y | N | Vector location + zoning SVG renderers `services/api/app/drawings/maps/` (E-07, #286); `map_context` contract 1.0.0 (#413), builder (#415), Northern fixture + SVG snapshots (#419) | No raster/aerial/street-view imagery at all; maps not connected to any results document; map licence undecided | Lane E; gate: imagery licence (owner), connect map_context to results; order 14 |
| Site summary from PLUTO (address, BBL, lot area, frontage, depth, land use, overlay, existing FAR, block character) | Y | Y | Y | N | PLUTO connector `services/api/app/connectors/pluto_soda.py`; study read `GET /properties/{bbl}/study` (#316/#317); facts B-02/B-03; existing-floor-area module `services/api/app/profile/existing_floor_area/` (B-05, #397, honest unknown); corner lot type from geometry (#390, in review #417) | Existing zoning floor area reads unknown (no DOB rows wired); block-character narrative and "largest property on block" only partly covered by parity (`services/api/app/profile/parity/`) | Lane C; gate: none for the facts; order 1-3 |
| Applicable development characteristics (zoning district, street class, program, lot type, parking, overlay, flood zone) | Y | P | Y | N | Hidden-issue flags `services/api/app/profile/hidden_issue_flags/` (24 flags, #329; 22 of 24 `check_needed`); flood via `hidden_issue_flags/map_based_rules.py` (B-09, #315); street-width stack `dcm_street_width_classifier.py` + D-052 policy; overlay C2-2 from PLUTO | Street width per frontage not yet surfaced in the study read; most hidden-issue flags have no connected source | Lane C; gate: none; order 3 |
| Zoning overview + parameter table with ZR references (FAR, height, DU factor, ZFA, base-height rules) | Y | P | Y | N | R6B draft rules `r6b_qualifying_housing_far.rule.json`, `r6b_height.rule.json`, `r6b_dwelling_units.rule.json`, `r6b_lot_coverage.rule.json`, `r6b_rear_yard_corner_waiver.rule.json`, `r6_r12_residential_far.rule.json`; engine recomputes allowance/envelope/units | No rendered parameter-table sheet (`report_model.schema.json` `calculation_rows` defined, no builder); every rule `needs_review` (no G6) | Lane A/E; gate: G6 legal review; order 10-11 |
| Calculation detail with plan view (footprint, yards, coverage, unit count) | Y | P | Y | N | `three_answers/geometry.py`, `three_answers/dwelling_units.py`; SVG site plan `services/api/app/drawings/kit/` (E-01, #263); results DXF `services/api/app/cad/results_dxf.py` (#268, structure tested, not AutoCAD-open-tested) | Live site inputs still fed from hard-coded `_benchmark_inputs`; plan-view not yet bound to the live study read | Lane C; gate: C-07 adapter; order 5 |
| Programs screened / applicable (48 evaluated, 7 applicable; UAP, AIRS, CF, SRO, overlay) | P | N | N | N | Coverage matrix add-on columns AO5 (affordable/senior City of Yes), AO6 (community facility), AO8 (ground-floor commercial) in `COVERAGE_MATRIX.md`; add-on model A-06 catalogue-as-data (#377, open) | No published bonus-program rule exists (grep below); program screening not rule-backed | Lane A; gate: M4 D-045 A3 wave + G6; stage 2 |
| Scenario pages: floor schedules, building core, floor plans, financial inputs | P | N | N | N | Scenario engine `services/api/app/scenario/builder.py`, `comparison.py`, `max_envelope.py`; massing `services/api/app/scenario/massing_mesh.py`, `cad/glb_writer.py` (D-087 released) | No floor-schedule / core / unit-schedule / floor-plan producer; no financial-inputs module (grep below); financial analysis is HELD under expansion hold | Lane A/E; gate: M5 scenario engine; financial HELD (expansion §2); stage 2 |
| Scenario comparison (cards + numeric table across programs) | P | N | N | N | `services/api/app/scenario/comparison.py`; `compare_rows.schema.json`; Lane C C-09 compare backend in progress | Comparison needs rule-backed programs; no mounted comparison over the Northern document | Lane A/C; gate: M4 D-045 programs + G6; stage 2 |
| Tax abatement eligibility (485-x, 421-a, J-51) | N | N | N | N | Explicitly out of scope: `services/api/app/api/v1/parity_read.py` ("computes no 485-x"); `profile/parity/__init__.py` ("485-x source pointers still to come under B-11") | No 485-x / tax-incentive logic at all (grep below) | Lane B; gate: product + owner scope decision; stage 2 or later |
| Comparable sales nearby (ACRIS + PLUTO, ranked, $/SF) | Y | P | Y | N | `services/api/app/profile/parity/comparable_sales.py`; DOF sales connector `connectors/dof_sales_soda.py`; route `api/v1/parity_read.py` (B-11, #312/#352) | Uses DOF sales, not ACRIS; computes no average or price-per-SF by product choice; selection filter is an open owner question | Lane B; gate: product decision on the filter; stage 2 |
| Colophon / disclaimers / data versions / reproducibility id | P | P | Y | N | Provenance via `source_fact.schema.json`, `legal_source_manifest.schema.json`; version check `services/api/app/profile/data_versions.py`; required disclaimer PRD section 29; reproducibility via `results_ref` digest in `report_model.schema.json` | No rendered colophon sheet (report_model builder absent) | Lane E; gate: report builder; order 11 |

### DB-122 existence checks (what we do not have, and what was searched)

- Report PDF rendered from the report model: `git grep -il "weasyprint\|headless chromium\|render_report_pdf\|report_to_pdf" -- services` returned nothing. We have a single-sheet site-plan PDF writer (`services/api/app/cad/pdf_sheet_writer.py`, M5-T085, D-087) and a PDF blueprint reader (`services/api/app/drawings/sheet_reader.py`), but no multi-page report PDF.
- Excel export: `git grep -in "openpyxl\|write_excel\|to_excel\|\.xlsx" -- services/api/app` returned nothing. `report_model.schema.json` names Excel as a render target, but no Excel writer exists.
- Report model builder: `git grep -il "build_report_model\|ReportModel" -- services/api/app` returned only schema copies and `contracts/study_contracts.py`. The report model is a contract shape only; nothing produces one.
- Financial analysis: `git grep -il "pro.forma\|proforma\|net rentable\|financial.analysis\|underwriting" -- services/api/app` returned nothing.
- Tax abatement / 485-x: `git grep -in "485-x\|485x\|421-a\|j-51" -- services` returned only disclaimers in `parity_read.py` and `parity/__init__.py` stating it is out of scope, plus one incidental PLUTO/DOB fixture string. No abatement logic.
- Imagery / raster base map: `git grep -il "esri world imagery\|street.view\|raster.base\|basemap\|aerial" -- services` returned only map-module files whose comments say a raster/aerial base map is deferred until an imagery licence is confirmed. No imagery is fetched.
- Published bonus-program rule: the coverage matrix (`COVERAGE_MATRIX.md`) states "Nothing here is reviewed. Every cited rule is status needs_review". No rule file is published.
- Mounted report route: `git grep -in "/reports" -- services/api/app/main.py services/api/app/api` returned only a comment. No `POST /reports` or `GET /reports/{id}` route is mounted.

---

## 3. The accuracy gaps specifically

Where the sample's method would be wrong for us, and how our pipeline prevents the same mistake.

1. **Unsourced numbers.** The sample prints figures (for example lot frontage 100.8 ft, existing FAR
   5.41) with no per-value provenance a reader can trace. Our every fact carries a source, rank and
   label (`source_fact.schema.json`, study read facts), and the report is bound to one results
   document by canonical digest (`report_model.schema.json` `results_ref`), so a value cannot appear
   without a traceable origin (PRD section 9 and the "impossible to export a material calculation
   without a provenance record" rule). Where our captured reading differs from the sample (for
   example the sample's own page 9 shows "Lot Coverage 100%" while noting "corner lot: 80%"), we do
   not pick a side: the figure stays draft and qualified review decides.

2. **Imagery licence.** The sample uses ESRI World Imagery and Google Street View. We render only
   vector city data (`services/api/app/drawings/maps/`) and have deliberately not fetched any raster
   or street imagery until an imagery licence is confirmed from the publisher's own terms page
   (`docs/samples/maps/README.md`). Our report either carries a licensed base map or carries none,
   never an unlicensed screenshot.

3. **Bonus programs without captured rules.** The sample lists UAP, AIRS senior housing, shared
   housing/SRO and a +0.40 FAR bonus as if settled. We will not emit a bonus FAR until the program
   rule is captured, drafted and G6-approved. Today those are add-on columns in the coverage matrix
   (AO5, AO6, AO8) with no published rule, so our report shows them as screened-but-not-computed
   rather than as a number.

4. **"Max units" without the dwelling-unit rule.** The sample asserts a unit count (for example 29,
   and an SRO scenario of 62) on its own. Our unit count is computed by a named draft rule
   (`r6b_dwelling_units.rule.json`) with the explicit formula "20,150 / 680 = 29.63" and the rounding
   rule, and it stays draft until G6. We never show a unit count that is not the output of a cited
   rule.

5. **Heights not tied to captured ZR text.** The sample gives base and max heights (30 / 50 / 60 ft,
   and elsewhere "base height 30-45 ft, max 55 ft", which is internally inconsistent on its own pages
   7 and 10) without binding each to a Zoning Resolution node. Our heights come from
   `r6b_height.rule.json` with ZR references and from the minimum-base-height finding in #388, each
   carrying the captured text; mismatches surface as a draft note (results 1.2.0 `notes[]`, #412),
   not a silent number.

In short: every mechanism that would let an inaccurate number reach the sample's pages is exactly the
mechanism our provenance, draft-until-G6, and deterministic-engine rules remove.

### The sample disagrees with itself (why copying it would be wrong)

These are concrete places where the sample's own pages conflict. They are listed only to show why a
value must be computed and cited rather than copied, not to say which side is right (qualified review
decides every one):

- **Lot coverage.** Page 9 reads "Lot Coverage 100% (10,075 SF max footprint)" and, in the same row,
  "ZR 23-153 (corner lot: 80%)". A single report cannot hold both as the governing figure. Our
  coverage comes from `r6b_lot_coverage.rule.json` with the corner condition explicit, draft until G6.
- **Base and max height.** Pages 7 and 9 give base 30 ft, max base 50 ft, max building 60 ft, while
  page 10 (programs) says "base height 30-45 ft, max 55 ft". Our heights come from
  `r6b_height.rule.json` plus the #388 minimum-base-height finding, each tied to the captured ZR node.
- **Bonus FAR.** Several scenario pages describe "FAR 2.40 (+0.40 bonus)" in prose but then state
  "Base FAR 2.00 + Bonus realized 0.30 = 2.30 FAR". We emit a bonus FAR only from a captured,
  G6-approved program rule, so the headline and the arithmetic cannot drift apart.
- **FAR table source.** Page 9 cites residential FAR to "ZR 23-151/153/154/155"; our captured R6B
  FAR reading is `r6b_qualifying_housing_far.rule.json` / `r6_r12_residential_far.rule.json`, and any
  difference from the sample's citation is a draft note, not a silent correction.

---

## 4. Ordered build plan to the first accurate PDF (one lot, one program: R6B residential, Quality Housing)

Each step names its lane, its dependency, the owner decision if any, and the gate. Owner-gated steps
are listed but not to be started until the owner clears them. Nothing here promises a date.

1. **[C] Thread lot geometry into the study read** (lot type, frontage, depth from the outline).
   Dependency: B-03 (done, #390). Status: in review in #417 (corner read). Gate: independent review +
   Option-B merge.
2. **[C] Corner-lot front lot line as a disclosed assumption** (address-street frontage governs
   `lot_front_ft`, fail closed without an address match; the legal call stays for qualified review).
   Dependency: step 1. Status: #417 (R138), stacked on #405. Gate: review; legal reading stays draft.
3. **[C] Street width per frontage into the study read** by connecting the existing envelope fetch to
   the `street_data_for_lot` wrapper (reuse, no new connector). Dependency: #403 seam, #408 binding
   (behind `LIVE_SPATIAL_PROVIDER_ENABLED`, off). Gate: review.
4. **[A] Merge the results-scope emitter** so the headline card and drawings carry the
   "Tax-lot-only estimate" label and the lot identity (#405, reviewed PASS). Owner decision: the Lane
   A yes to merge. Gate: owner yes per PR.
5. **[C] C-07 adapter bridges the live study read to the engine**, replacing the hard-coded
   `_benchmark_inputs` site inputs. Dependency: steps 1-3. Gate: review. Note: several non-site inputs
   (overlay present, within-100-ft, angle) still lack a sourced origin and stay named assumptions.
6. **[A] Add the 1.2.0 notes emitter** (minimum-base-height finding) on #388 so the computed note
   reaches the results document. Status: prepared, reviewed PASS, HELD by the owner (R125/R136). Gate:
   owner yes after the hold lifts.
7. **[C] One continuous recorded-data journey test** (BBL entry, study, bridge, engine, results, site
   plan, DXF, cards) proving the chain end to end on recorded data (#421, R137, stacked on #417).
   Dependency: steps 1-6. Gate: review.
8. **[owner] Golden record M1-05** (Q1 pilot lot + Q12 reviewer). This is owner input, not a code
   task, and it gates the on-screen result.
9. **[C] Mount the results route (C-08)** so the Northern numbers reach a browser. Dependency: step 5
   and step 8. Gate: owner-blocked on M1-05.
10. **[reviewer/owner] G6 qualified legal review** of the R6B draft rules (FAR, height, DU, coverage,
    rear-yard corner waiver). No rule becomes a value an architect can rely on without it (CLAUDE.md
    principle 12). Gate: qualified reviewer approval; the full M3 legal corpus is still owed before
    publication.
11. **[E] Build the report_model builder** that assembles ONE `report_model` (1.0.0) from the results
    document plus the study at the same revision: cover, dimensioned site plan (reuse E-01), the
    calculation table with ZR sections, the floor-by-floor table, the assumptions page, the standing
    notices shown once, and the colophon with data versions and the reproducibility id. Dependency:
    step 9 and the report_model contract (present). Gate: review.
12. **[E] E-02 PDF converter trial** on the benchmark lot and the owner's Render-runtime decision
    (WeasyPrint vs headless Chromium). Owner decision: E-02 converter choice. Gate: the dependency
    -security age/advisory gate (G5 provenance review for a new package, CLAUDE.md principle 15).
13. **[E] E-04 render the report PDF** from the report_model. Dependency: step 12 and durable storage
    B-001. Gate: review; owner decision B-001.
14. **[E] Connect the maps** (feed a `map_context` from the results/study into the location and zoning
    SVG renderers) so the report carries the two vector maps. Dependency: step 11; the imagery licence
    decision governs any raster base map. Gate: review.

The honest shortest path to the FIRST accurate PDF runs steps 1-7 (unblocked wiring and the journey
test), is then gated at the screen by the golden record M1-05 (steps 8-9), at the rules by G6 (step
10), and at the export by the PDF converter and durable storage (steps 11-13). An agent can clear 1-7
and 11 and 14; it cannot clear 8, 10, 12 or 13.

### Critical path at a glance

- Facts and study read: steps 1 -> 2 -> 3 (Lane C, unblocked today).
- Scope and engine feed: step 4 (owner yes on #405) -> step 5 (C-07 adapter) -> step 7 (journey test).
- Screen: step 8 (owner golden record M1-05) -> step 9 (mount results route C-08).
- Legal: step 10 (G6) is parallel to the wiring but blocks any reliance on a rule value.
- Export: step 11 (report builder) -> step 12 (owner converter choice) -> step 13 (PDF, needs B-001)
  -> step 14 (maps into the report).

The two hard human gates on this path are the golden record (step 8) and G6 (step 10). Neither can be
cleared by an agent, and both sit before the report can be called accurate rather than draft.

### Second stage: breadth, drawings, financial, imagery

- **Multiple programs and scenarios.** M4 D-045 campaign waves: A3 contextual / Quality Housing plus
  bonus programs (including City of Yes UAP), then C-district overlays and parking, then the M-district
  families (campaign order A1 -> A2+B2 -> A3 -> C -> M -> A4 per the M4 summary in
  `python tools/project_control.py status`). Each program is one reviewed family at a time, draft until
  G6. The M5 scenario engine (`services/api/app/scenario/`) then compares them the way the sample's
  scenario pages and comparison table do, but only over rule-backed programs.
- **Floor plans and massing.** Released under D-087 (3D building-and-lot massing, CAD export, PDF
  blueprints). The massing primitives exist (`scenario/massing_mesh.py`, `cad/glb_writer.py`). Still to
  build: the floor-schedule, building-core and unit-schedule producers, and the synthesized floor-plan
  drawings the sample shows, each marked diagrammatic and not for construction.
- **Financial analysis.** The sample's financial-analysis inputs and 485-x table are financial
  feasibility. That family is still HELD under the expansion §2 hold
  (`.claude/rules/expansion-agent-dispatch-hold.md`); D-087 released 3D / CAD / PDF blueprints but not
  financial analysis. This plan names it and plans nothing for it.
- **Imagery.** Any raster/aerial/street-view base map waits on a confirmed imagery licence. Until then
  the report carries vector city maps only.

---

## 5. Owner decisions needed (one list, with the ledger / handoff IDs)

- **M1-05 (Q1 pilot lot, Q12 reviewer)** - the golden record that gates the mounted results screen (C-08).
- **E-02** - PDF converter choice (WeasyPrint vs headless Chromium) and the Render runtime decision.
- **B-001** - durable storage (Supabase) token, gating saved revisions (C-06 slice 2) and the report PDF (E-04).
- **Q4** - which screen is the default entry (D-02).
- **Q7** - durable storage scope for saved revisions (tied to B-001).
- **Q8** - whether the section drawing (E-01b) falls under the expansion hold.
- **Geoclient key configuration** - `GEOCLIENT_SUBSCRIPTION_KEY` is not configured on this server; configure it securely where the one-off recording runs, never in chat (R140).
- **Lane A merges (per PR)** - #369 (A-05), #377 (A-06), #382 (A-07 step 1 snapshots), #405 (scope emitter). Each needs the owner's explicit yes.
- **#388 hold** - the R6B minimum-base-height finding and the 1.2.0 notes emitter are HELD (R125/R136).
- **CI change** - the proposed CI policy change is HELD (R125/R136); no workflow change exists yet.
- **Imagery licence** - needed before any raster/aerial/street-view base map.
- **Financial-analysis hold** - still suspended under the expansion §2 hold; release is an owner directive.
- **G6 qualified legal review** - no rule publishes without a qualified reviewer's approval (CLAUDE.md principle 12).

---

## 6. What this plan does NOT do

- It promises no dates. The gates and holds, not a calendar, decide when each step can run.
- It changes no master plan and contracts no task. The owner-review hold on expansion planning stands
  (`.claude/rules/expansion-agent-dispatch-hold.md` §2); the orchestrator alone contracts the slices
  and changes the plan (CLAUDE.md principle 9).
- It invents no rule, no legal reading, no effective date and no source meaning (CLAUDE.md principle 3).
- It copies no number from the sample as truth. The sample is a shape-and-scope reference; every figure
  our report shows is computed by our engine from captured sources and stays draft until G6.
