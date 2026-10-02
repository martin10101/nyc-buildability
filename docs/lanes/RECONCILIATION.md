# Reconciliation — current product plan vs. the repository

| | |
|---|---|
| **Date** | 2026-09-30 |
| **Base commit** | `2283c178` (code identical to `574432fd`; `2283c178` only changes `docs/SESSION_HANDOFF.md`). Spot checks were run in the `w0-docs` worktree at `8a813bdd`, which differs from `2283c178` only in `docs/`, `project-control/` and `scripts/lanes/README.md`, so every code line number is the same. |
| **Plan** | `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` (the single current plan; its task IDs, titles and "Done when" text are used unchanged). Benchmark: `docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`. |
| **Purpose** | Record, for every plan item, what the code does today, the evidence, and the gap against the plan's "Done when". This feeds the lane queues (A–E). It authorizes no change. |
| **Method** | Five read-only research passes, one per proposed lane: A engine/rules, B data and site facts, C contracts/study/integration, D architect web interface, E outputs/CI/validation. Where passes overlap, their findings are merged into one row. Then 48 of the most decisive references were spot-checked against the source (see "Spot-check log"). No code was run for this file; the one "run-verified" engine result is quoted from pass A. |
| **Evidence** | `file:line` in the repo, a named test file, or a CI workflow line. "none found" = no pass found any code. "unverified" = the passes could not determine it. Doc and ledger claims are not evidence. |
| **Path shorthand** | `api/` = `services/api/`; `web/` = `apps/web/`. Other paths are repo-root (`tools/`, `tests/fixtures/…`, `packages/`, `.github/`, `docs/`). |
| **Flag shorthand** | `IRE` `INTERNAL_RULE_EVAL_ENABLED` (`api/app/config.py:28`); `ISE` `INTERNAL_SCENARIO_ENABLED` (`config.py:34`); `LSP` `LIVE_SPATIAL_PROVIDER_ENABLED` (`api/app/spatial/live_provider.py:72`); `LWS` `LIVE_WIDE_STREET_PROVIDER_ENABLED` (`api/app/spatial/wide_street_live_provider.py:130`); `SDW` `SITE_DEFINITION_WRITE_ENABLED` (`api/app/api/v1/site_definition.py:117`). All default off; `render.yaml:109-135` sets none of them. |
| **Missing input** | The plan's execution reference `PARALLEL_BUILD_PLAN_LANES_2026-09-28.md` is not in the repo at `2283c178` (pass C). |

**Status legend**

| Status | Meaning |
|---|---|
| done | The plan's "Done when" is met at the base commit, with evidence. |
| partial | Code or tests toward the item exist, but the "Done when" is not met. |
| missing | Nothing toward the item exists, **or** the existing code contradicts the plan (marked "Contradicted" in the gap). |
| not-applicable | Owner or non-code item; the reason is given. |

Lane codes: **A** Engine · **B** Data & site facts · **C** Contracts/study/integration + hot files · **D** Architect web interface · **E** Outputs & parity · **Owner**. A lane in brackets supports the first one.

---

## Milestone 1 tasks

In the plan's table order. The plan has no M1-23. M1-06 is split into M1-06a (server, Lane C) and M1-06b (interface, Lane D), as the plan directs.

| ID | Task (short) | Status | Evidence | Gap vs "Done when" | Lane |
|---|---|---|---|---|---|
| M1-00 | Architect mockup review *(pending Q10)* | missing | No review record. Precursors only: CI dashboard screenshots (`.github/workflows/ci.yml:116-122`); owner AI images, "inspiration/reference ONLY" (`docs/design/ui-inspiration/README.md`); `docs/MVP_ARCHITECT_REVIEW_QA.md:58` "mockup file … still never received" (D) | No 2–3 architects have reviewed the §3 flow; no findings recorded | D (Owner Q10) |
| M1-00b | Competitor benchmark (owner, not code) | not-applicable | Owner purchases and the free Envelope check; no pass covered it. The only benchmark on file is the reviewed Envelope sample (competitor review doc) | Reason: owner action, not code. Features, formats and numbers still need recording (§9a, §11a) | Owner |
| M1-01 | Confirm sources on the working branch, incl. `AGENTS.md` | partial | The "§10 claims check" section of this file gives every §10 claim a `file:line` or a correction (merged from passes A–E). `AGENTS.md` and `.claude/rules/*.md` are present at the repo root (C) | Closes when an independent reviewer accepts that section (the producer never verifies its own work) | C |
| M1-02 | Runtime configuration record, read-only | missing | Only `GET /api/v1/health` → `{"status":"ok","version":"0.1.0"}` (`api/app/main.py:44,220-223`). No SHA, build-info or flag endpoint; no `RENDER_GIT_COMMIT`/`GIT_SHA` read anywhere. `render.yaml:109-135` declares no feature flag; web service block withheld (`render.yaml:156-168`) (C) | No record of deployed SHAs and flags. Needs an owner-read record or a read-only build-info route (SHA + boolean flags, no secrets) | C |
| M1-03 | Rule-coverage matrix (district × output × add-on) and street-width source | partial | FAR params for 45 district ids (ZR 23-21/23-22) in 5 files under `api/app/rules/rulesets/`; AS-2 "every snapshot district covered" `api/tests/rules/test_r1_r12_residential_far.py:257`; heights R1–R5 only; PLUTO inventory of 41 R labels `tests/fixtures/residential_validation/district_inventory.json`; only a static, district-agnostic matrix in code `api/app/scenario/constants.py:256-287` (A) | No matrix artifact. R10H (18 PLUTO parcels) is in no rule or snapshot. No cells for yards, coverage, dwelling units or add-ons. Street-width source encoded only in the wide-street stack (R6/R7-1/R7-2/R8) | A (+ reviewer) |
| M1-04 | Pilot A candidates | missing | none found. Pilot not chosen (Q1 open) (A §1e) | No ranked candidates with evidence | A (+B data; Owner confirms Q1) |
| M1-05 | Reviewer verification → golden record | missing | No golden record anywhere. All 18 rule files are `status: needs_review`, `qualified_human_approval: pending` (A) | No signed record, no recorded fixtures | Owner (reviewer Q12) + A fixtures |
| M1-06a | Remove example-site defaults — server side | partial | No example seed in server code (grep, C). Rule evaluation and scenario build inputs from the BBL profile only (`api/app/api/v1/rule_evaluation.py:240`; `scenario.py:160-215`). But `/proposal-checks` and `/max-envelope` accept caller-attested lot area, district and street class with free-form provenance (`proposal_checks_api.py:338-357`). Unknown street width silently takes the narrow row (`rule_evaluation.py:186-207`; `wide_street_live_provider.py:209-217`) (C) | No guard or test for "no example values in any real-property request". Unknown width should show "Unknown" or both results (§4) | C (+A/B street width) |
| M1-06b | Remove example-site defaults — interface | missing | `rectangleSampleDraft()` in `web/src/lib/architect/proposal-draft.ts:421-451`: R5 `:447`, 8,000 sq ft `:443`, "wide" `:448`, fake EPSG:2263 vertices `:429-434`. Seeded on every real property: `web/src/components/architect/ProposalEditor.tsx:73`. Locked by tests: `web/e2e/proposal-editor.spec.ts:149-151`, `entry.test.tsx:443-445`, `proposal-draft.test.ts:38` (C, D) | Example values sit in real-property state and reach `/proposal-checks` requests. No Example project exists | D (+C guard) |
| M1-07 | Input statuses: survey, city records, approximate, entered, assumed, unknown | partial | Per-fact provenance and `coverage_status` (`api/app/profile/builder.py:295-315,527,763-790`); unknowns listed as `missing_inputs` "never fabricated" (`builder.py:403-436`); dashboard shows a status and source per fact (`web/src/components/architect/workspace/DashboardPanels.tsx:48-71`) (B, D) | The six-status vocabulary exists nowhere (api, web, contracts: 0 hits, B). UI prints the raw coverage enum (`web/src/components/property/CoverageBadge.tsx:9-18`). No entered or assumed state; nothing editable | B (+C contract, D display) |
| M1-08 | Labeled input channel to the evaluator | missing | Rule evaluation is a `GET` with the BBL only (`rule_evaluation.py:240`). Evaluator inputs are only `{zoning_district, lot_area_sq_ft}` (`api/app/rules/integration.py:789`). Builder always emits `user_confirmations: []` (`builder.py:768`). Survey facts stop at an unwired gate (`api/app/documents/promotion.py:16-18`) (A, C) | No reviewed contract keeps entered, assumed and survey values distinct from facts; no path from them to the evaluator | C (+A intake, B sources) |
| M1-09 | Study contract | missing | None of the 11 schemas in `packages/contracts/schemas/v1` is a study. Only precursor: web-only `ParcelStudyDraft` v1 (`web/src/lib/architect/parcel-study.ts:6-34`), condo sets with ≥2 base lots only (C) | Needs a study schema (lots, site facts + sources, options as add-on selections + program/floor heights) with valid and invalid fixtures in `validate_contracts.py` | C |
| M1-10 | One study store for every surface | missing | Study state is component-local `useState` (`web/src/components/architect/ParcelStudyPanel.tsx:48`), created separately on the overview (`PropertyOverview.tsx:99`) and the dashboard (`DashboardTools.tsx:60`). Proposal state is local too (`ProposalEditor.tsx:73`) (C) | Surfaces cannot agree; no option model, so "editing one option leaves the others unchanged" is untestable | C (+D surfaces) |
| M1-11 | Revisions and dependency-based invalidation | partial | No study revision or dependency graph. Hooks only: rule-evaluation `input_fingerprint`, trace `rule_version`/`rule_release`, `profile_revision` (`packages/contracts/schemas/v1/property_profile.schema.json:23-30`). Only the late-response rule is implemented, with tests (§9 "Invalidation 4", done) (C) | 3 of the 4 §9 invalidation rules have no code or tests | C |
| M1-13 | Site setup: lot choice and pre-filled measurements with sources | partial | PLUTO lot area, frontage, depth, lot type, irregular code pre-filled (`builder.py:98-106`; units `api/app/connectors/pluto_soda.py:199-210`). Lot choice only for condo multi-lot sets (`api/app/api/v1/condo_records.py:588`; `ParcelStudyPanel.tsx:14-18,92-145`). Pre-filled facts are read-only (`DashboardPanels.tsx:135-147`) (B, D) | No per-street frontage, derived lot type, per-frontage street widths, "use all / pick" for non-condo lots, contiguity refusal, "lots you selected" label, or edit-with-source. Condo base lots get no measurements. No Pilot A fixture to prove "nothing typed" | B (+D UI, C study) |
| M1-12 | Connect the evaluator for Pilot A | partial | `evaluate_property` (`integration.py:614`), family `residential_far` only (`:75`), inputs `:789`; route `rule_evaluation.py:240`, gated `:259` → web `rule-evaluation.ts:310`. LSP off → every BBL fails safe (`live_provider.py:72-87`); LWS off → conservative row (`wide_street_live_provider.py:130,209-217`) (A, C) | No golden record (M1-05). FAR only. No labeled inputs (M1-08). Provider flags default off and not declared per environment | A (+C wiring/flags) |
| M1-14 | Generator for the three answers | partial | Allowance: FAR × lot area (`api/app/rules/evaluator.py:130-188`). Envelope/option: `derive_max_envelope` (`api/app/scenario/max_envelope.py:938`) is a rectangle prism; FAR and rear yard "non-commensurable" (`:206-265`); floors split at `MAX_FLOOR_TO_FLOOR_FT = 100.0` (`api/app/scenario/proposal.py:103`). Real registry → no candidate (`api/tests/scenario/test_max_envelope.py:628-642`). Route `max_envelope_api.py:269` not mounted (`api/app/main.py:126-218`) (A) | Only a FAR allowance. No permitted envelope beyond scalar R1–R5 heights; no building option, floor stack or shortfall explanation; nothing equals a golden record | A |
| M1-25 | Add-on switches, Best combination, completeness line | missing | 0 hits for add-on / best combination / toggle in `api/app/rules`, `scenario`, `spatial` (A) and in web (D). Only `conditional_alternative` exception text (`evaluator.py:320-323`; `r6_r12_residential_far.rule.json:54-62`) | All of it | A (+D UI) |
| M1-15 | Plan diagram per option (drawing kit) | partial | No plan drawing in web; maps are display-only (`web/src/components/architect/ParcelStudyMap.tsx:386-389`) (D). Server precursor only: a one-sheet PDF with lot/building rings and edge labels computed from the ring (`api/app/cad/pdf_sheet_writer.py:376-419`), fed caller rings (`export_service.py:161-180`) (E) | No kit, no per-option plan; no yards, hatching, street names/widths or coverage; no check that dimensions match the numbers; not on screen | E (+A geometry, D embed) |
| M1-16 | Section and 3D massing *(Q8 for interactive 3D)* | partial | No section drawing anywhere (E). `three`/`@react-three/fiber` declared (`web/package.json:18,23`), imported nowhere (D, E). Single-prism GLB (`export_service.py:417-521`); per-level plates (`api/app/scenario/massing_model.py:376,506`) used only by the unmounted `scene_api` (E) | No section, no vector axonometric; GLB ignores setbacks; no "one line names what is missing" | E (+A geometry, D embed) |
| M1-17 | Communication pass (§9, §5a) | missing | Precursors only: one "Active issues" strip (`web/src/components/architect/OverviewExceptionStrip.tsx:48-120`); dashboard sources behind buttons (D). Report identification line is "BBL … · Profile generated …" (`ReportView.tsx:77`) (C) | Contradicted: fails §5a (see "§5a rules" below; rules 2, 3, 5 and 6 are violated): no status strip, ~29 labels at once, caution labels beside numbers, raw codes, 9–12 px grey text. No UI review or §5a acceptance test | D |
| M1-24 | Floor-area availability reminder | missing | The exact §5a wording appears nowhere in `web/src` (grep, D; re-checked) | Not reachable from a strip; not in the report | D (+E report page) |
| M1-18 | Compare options side by side | missing | Only `ProposalVariations.tsx:97-129` (pass/fail of drawn drafts) and the parcel-study Compare ("Not calculated", `ParcelStudyPanel.tsx:138-142`). `ScenarioWorkspace.tsx:21`: "One preliminary scenario is supplied" (D) | No option side-by-side, no identical rows, no common-scale plans | D |
| M1-19 | Report and historical export | partial | Browser print of live screen state (`web/src/components/architect/ReportView.tsx:69`); "This brief is not saved automatically" (`:79`); props carry no option, study or revision (`:21-27`). Parity with the screen tested for the FAR panels (`web/src/components/architect/__tests__/report-view.test.tsx:51,96,214,253`). Parcel-study JSON is choices only (`ParcelStudyPanel.tsx:59-90`) (C, E) | Not bound to a revision; no "Option · revision · date" line; no saved or read-only history; no drawings | E (+C revision binding) |
| M1-22 | PDF, Excel and DXF export | partial | DXF: layers LOT / BUILDING_OUTLINE / MASSING_3D / ANNOTATION (`api/app/cad/dxf_writer.py:98-117`), `$INSUNITS` 21 US survey feet (`:85`), EPSG:2263 feet (1:1). PDF: one landscape sheet (`pdf_sheet_writer.py:1-10`). Route `api/app/api/v1/export_api.py` unmounted. Tests `test_dxf_writer.py`, `test_export_service.py` (E) | PDF has 1 of 7+ sheets. No Excel. DXF has no envelope layer and no "Approximate — city tax map" note, and refuses a lot-only export (`export_service.py:527,562-564`). AutoCAD open unverified | E |
| M1-26 | Validation suite (§9a) in CI | partial | `tools/residential_validation.py` + `tools/test_residential_validation.py` (26 tests), fixtures `tests/fixtures/residential_validation/v1/`; referenced by no workflow (grep of `.github/workflows/`: 0). FAR/height unit tests run in the `api` job (`.github/workflows/ci.yml:222-223`). DOB captures `api/tests/fixtures/dob_legacy/*` consumed by no code (A, E) | Not in CI. No City Planning examples, no DOB-filing comparison, no hand-checked lots, no difference log | E (suite) + A (engine cases) + C (CI step) |
| M1-27 | Drawing kit and design system (§5c) | missing | 0 SVG hits in `api/app`; no templates or style table. Only "snapshots" are byte-sha goldens of synthetic writer output (`api/tests/cad/test_dxf_writer.py:53`, `test_pdf_sheet_writer.py:42`, `test_glb_writer.py:67`). No PDF/SVG/Excel library in `api/requirements.in` or `requirements.txt` (E) | Everything: SVG site plan, section and massing from results; PDF templates; benchmark snapshots; the same SVGs on screen | E |
| M1-20 | Pilot A regression journey | partial | Recorded-fixture harness `web/e2e/harness/fixture_api.py:1-45` serves the real `app.main.app` (so export, scene and max-envelope are absent); CI `web-e2e` (`ci.yml:60-126`); the journey ends at "Print property brief" (`web/e2e/connected-dashboard.spec.ts:78-81`). BBL 4073340070 appears in no fixture (B, C, E) | No export step, no Pilot A fixture, no download assertion on PDF/XLSX/DXF | C (+E exports) |
| M1-21 | Observed architect session | missing | none found; no §5a rule-7 harness and no session (D) | Not held | D (Owner schedules) |

---

## Milestone 2 tasks

In the plan's table order. The plan has no M2-04.

| ID | Task (short) | Status | Evidence | Gap vs "Done when" | Lane |
|---|---|---|---|---|---|
| M2-00 | Optional research: permit, ACRIS and DTM records | partial | DTM condo + units + ZTLDB research (`docs/research/condo-base-lot-resolution-sources.md:20,73-76,110-112,161`); DTM outlines recorded 2026-09-26 (`api/tests/fixtures/dtm_lot_outline/MANIFEST.json`) (B) | DOB permit and ACRIS records not pulled (`docs/research/live-case-regression-properties.md:102,117`) | B |
| M2-05 | Multi-lot site math | missing | No union/combined outline, frontage or lot-type derivation (grep, B). Multi-lot condo → substrate fail-safe `None` (`live_provider.py:355-368`); web map says "No union, area…" (`ParcelStudyMap.tsx:121,389`) (B) | Selecting 1, 2 or all lots updates nothing geometric; no combined-site fixtures | B |
| M2-06 | §8 warnings | missing | Data precursors: PLUTO `splitzone` (`builder.py:128`) and spatial `split_lot_confident` (`api/app/spatial/models.py:28`); missing street width → professional review (`wide_street_live_provider.py:43-57`) (B). UI: none of the §8 strings exist; split zone only as a raw fact (`web/src/lib/format.ts:88`) (D) | No not-on-one-block / not-touching check, no condo-board line, no unpermitted-work source (no DOB connector); the "larger" flag uses a forbidden source; nothing appears once beside the affected results | B (data) + D (placement) |
| M2-07 | Existing floor area input, with source | missing | Contradicted: `api/app/scenario/unused_floor_area.py:447-467` computes cap − PLUTO `bldgarea` (DOF-sourced); wired into every scenario (`scenario/builder.py:317`); tested as intended (`api/tests/scenario/test_unused_floor_area.py`); shown in web (`web/src/components/compare/UnusedFloorAreaSection.tsx:81-144`) (A, B, D) | Existing floor area **is** taken from DOF building area (behind ISE). No DOB filing/CO connector and no entered-assumption input | B (source + input) + A (remove subtraction) |
| M2-08 | Keep / partial rebuild / full rebuild (§5b) | missing | "54-41": 0 hits in app and tests; no existing-zoning-floor-area input in the engine (A). No 215-16 Northern fixture (B) | All three paths, the rebuild budget, both traps and the headline; the benchmark check cannot run | A |
| M2-01 | Wallabout options (floor area only) | missing | Condo multi-lot withholds allowances (`DashboardTools.tsx:70-73` "Site definition required"); study shows "Not calculated" (D). Wallabout has only DTM outlines and condo bodies; no PLUTO, ZTLDB or street data (B §2) | No options; no single height-gap line | D (+A/C) |
| M2-02 | Wallabout comparison and report | missing | none found. Prerequisites M2-01 and M1-18 are missing and M1-19 is partial (this file) | Report matching the screen | D (+E report) |
| M2-03 | Two-pilot regression | missing | none found. No Pilot A fixture; Wallabout fixtures limited to DTM outlines and condo bodies (B §2); M1-20 partial | Both pilots pass in CI | C |

---

## Rest of Phase 1 and Phase 2

The plan has no L-4.

| ID | Work (short) | Status | Evidence | Gap | Lane |
|---|---|---|---|---|---|
| L-1 | Every R district: full catalog and rule coverage (waves) | partial | FAR for all ZR 23-21/23-22 rows; heights R1–R5 (12 files); setback R5 only (`r5_setback.rule.json`) (A) | No R6–R12 height/setback; no yard, coverage, dwelling-unit, QH/height-factor or add-on rule for any district; R10H absent; nothing reviewed | A |
| L-2 | Group B certifications, Group C neighbor estimate | missing | No certification, transfer or neighbor code (A) | All | A |
| L-3 | Group D1 switches, D2 opportunity notes | missing | No special permit, authorization or variance code (A) | All | A |
| L-5 | "Explain this", "Likely examiner questions" | missing | 0 hits for "examiner" / "explain this" in app code (E) | All | E |
| L-6 | Compare several properties *(pending Q10)* | missing | none found (no pass covered it) | All | D |
| L-7 | Keep the catalog current | partial | Mechanism only: temporal windows (`api/app/rules/models.py:90-100`); fail-closed snapshot digests (`models.py:188-212`); bundle sync guard (`api/tests/rules/test_zr_snapshot_bundle.py`); FH-2 conflict detection (`api/app/rules/registry.py:45-103`) (A) | No change-detection process; no catalog to keep current; stale docstring `test_r1_r12_residential_far.py:23-31` | A |
| L-8 | Commercial districts that allow housing | missing | Overlay family detected (`api/app/spatial/policy.py:64-68`); no C→R pairing table, no mixed-building rules (A) | All | A |
| L-9 | Manufacturing zones: residential pathways first | missing | No M-district or M1-D logic; "M1-2/R6A" → `not_applicable` (`integration.py:826-835`) (A) | No pathway check; no "New housing isn't allowed here" answer (correctly never emitted) | A |
| L-10 | Simple financials *(1b)* | missing | `financial_readiness: "not_computed"` (`api/app/profile/builder.py:494`); web `financials` tool is a `PlannedView` (`DashboardTools.tsx:76`) (E) | All | E |
| L-11 | Hidden-issues checks (§8a) | partial | PLUTO mapped features surfaced raw (`builder.py:127-130`); near-boundary class (`api/app/spatial/models.py:29`; 20 ft `policy.py:45`) (B) | No flag layer and no "Check needed" fallback for any §8a item; the nearest are the "Unknown — not supplied" rows for landmark, historic district and the flood flags (`web/src/components/architect/AdditionalZoningFlags.tsx:4-16`) (see "§8a hidden issues") | B (+A rule items) |
| P2-1 | Building-code feasibility (Phase 2) | missing | none found (Phase 2; E: test-fit layouts 0 hits) | Waits for Phase 1 coverage and owner go-ahead | A (Phase 2) |

---

## Benchmark checks (competitor review §D)

| ID | Check | Status | Evidence | Gap | Lane |
|---|---|---|---|---|---|
| C-1 | One source for heights | missing | Single-source design: envelope and checks both read family `residential_height_setback` (`max_envelope.py:236-244`; `api/app/rules/proposal_checks.py:226-233`); web does no height math (`web/src/lib/architect/development-limits.ts:1`). No ZR 23-43x rule or snapshot ("23-432": 0 hits, re-checked). R1–R4 heights live in families neither caller queries (A) | No R6B height lookup; the family-name split breaks "one lookup" | A |
| C-2 | Allowance vs. building | partial | 20,150 computable (R6B, 10,075 sf → 2.0 / 20150.0, run-verified by A). 24,180 never computed: a qualifying input still gives 20,150 plus exception id `qualifying_housing`. FAR non-commensurable in the envelope (`max_envelope.py:212-254`) (A) | No affordable allowance, no building, no shortfall reasoning | A |
| C-3 | Existing building | missing | `over_built` state and statement (`api/app/scenario/constants.py:115-120`; `unused_floor_area.py:462-467`) computed from PLUTO `bldgarea` vs. the draft cap (A, B) | Contradicted: the source is forbidden by §3 step 4 ("never subtracted") and §8 ("Recorded building area is never used"); wording differs from C-3; no existing zoning floor area shown; 54,488 sf in no fixture | A + B |
| C-4 | Drawings match numbers | partial | PDF edge labels computed from geometry, never fixed text (`pdf_sheet_writer.py:409-419`); max-envelope proves candidate containment in the lot (`max_envelope.py:19-22`) (E) | Export does not check footprint ≤ lot; no floors or per-floor areas drawn; no table to reconcile; geometry is caller-supplied | E |
| C-5 | Consistency sweep | missing | No cross-page or report value sweep (E) | All | E |
| C-6 | No duplicate options | missing | Ranking and comparison only break ties (`api/app/scenario/ranking.py:25-26,391`) (A) | No merge-or-explain | A |
| C-7 | Current sources | partial | Rule loader refuses a citation with a missing or mismatched snapshot (`api/app/rules/dsl.py:61-81`; `snapshots.py:157-184`); 14 snapshots; pre-2024 numbers (23-151/153/154/155, 23-662, 23-64) have 0 hits (A, E). PLUTO version read per record, not pinned (`pluto_soda.py:112,731-737`); fixtures mix 26v1 and 26v2 (B). Report shows dataset versions (`ReportSources.tsx:9,37`) (E) | No "current" check or "Out of date"; no report-level citation validator; "our app already uses 26v2" is not a code fact (B) | B (data) + A (rules) + E (report) |
| C-8 | Same rule everywhere (parking/transit) | missing | PLUTO `transitzone` raw fact only (`builder.py:129`); parking listed as a missing constraint (`scenario/constants.py:226,267`) (B) | No single transit/parking source feeding all options | B (+A) |
| C-9 | Zoning lot | partial | Scenario assumption "The selected tax lot is treated as the zoning lot." (`scenario/constants.py:134-143`); web map note (`ParcelStudyMap.tsx:389`) (B) | Plan label text absent; no recorded-zoning-lot-document flag (no ACRIS) | B (+D label) |
| C-10 | Lot-split ideas | missing | 0 hits for lot type / interior / through / subdivision in the engine (A) | All | A |
| C-11 | No template sentences | partial | Explanations are typed and depend on computed state (`EnvelopeGapReason`, `max_envelope.py:132-146`; shortfall only on a computed FAIL, `proposal_checks.py:682+`); `ENVELOPE_DISCLOSURE` is fixed boilerplate (`max_envelope.py:100-109`) (A) | No shortfall-explanation generator exists yet to test | A |
| C-12 | Units in one place | missing | No dwelling-unit rule, no 23-52 snapshot, no factor 680 in `api/app` (re-checked); DSL `round` is half-away-from-zero only (`api/app/rules/operations.py:100-107`) (A). Web `units` tool is a `PlannedView` (`DashboardTools.tsx:75`) (E) | All | A (+E report) |

### Benchmark readiness — 215-16 Northern Blvd (R6B / C2-2, corner)

Each expected value from competitor review §A. "Code today": present / partly present / absent. **No fixture of any kind exists for BBL 4073340070** (no PLUTO, MapPLUTO, DTM, ZTLDB, zoning, street, footprint, DOB or ACRIS capture; B §2), so none of these can run in CI yet.

| Expected (§A) | Value | Code today | Evidence |
|---|---|---|---|
| Lot area | 10,075 sq ft | partly present | PLUTO `lotarea` read with units (`pluto_soda.py:199-210`); the rule input uses the MapPLUTO polygon or spatial-pair area (`integration.py:351-370`), equal to 10,075 only if that area is exact (unverified) (A, B) |
| Lot dimensions | about 100.8 × 100 ft | partly present | PLUTO `lotfront`/`lotdepth` as single numbers (`builder.py:98-106`); no per-street frontage (B) |
| Lot type | corner (215 Pl & Northern Blvd) | absent | Raw PLUTO `lottype` code only (`builder.py:101`); no corner classifier (A, B) |
| Zoning | R6B with C2-2 overlay | partly present | PLUTO zoning and overlay facts (`builder.py:118-124`); overlay detected at the spatial layer (`policy.py:66`) but never a rule input (`integration.py:789`); a near-boundary overlay pair routes to professional review (`api/app/spatial/engine.py:222-236`) (A, B) |
| Max residential FAR (standard) | 2.00 → 20,150 sq ft | present | Draft, run-verified by A: `r6_r12_residential_far.rule.json:36` (R6B 2.0), steps `:46-47`; no R6B- or 10,075-specific test |
| Max residential FAR (affordable/senior) | 2.40 → 24,180 sq ft | absent | Stored parameter and exception text only (`r6_r12_residential_far.rule.json:37,57`); qualifying input still yields 20,150 (A) |
| No wide-street increase for R6B | none | present | R6B is only in the flat table; the wide-street rule covers R6, R7-1, R7-2, R8 only (`r6_r7_r8_wide_street_conditional_far.rule.json`) (A §2) |
| Heights (standard) | min base 30, max base 45, max 55 ft | absent | No ZR 23-43x rule or snapshot (A) |
| Heights (affordable/senior) | max base 45, max 65 ft | absent | Same (A) |
| Lot coverage | corner: up to 100% | absent | Family `lot_coverage` unsupported; no corner classification (A) |
| Rear yard | not required within 100 ft of the corner | absent | Family `rear_yard` unsupported; envelope treats rear yard as non-commensurable (`max_envelope.py:206-210`) (A) |
| Dwelling units (standard) | 20,150 ÷ 680 = 29.63 → 29 | absent | No DU rule; no threshold rounding (`operations.py:100-107`) (A) |
| Existing building | 5 stories, ~54,488 sq ft, 38 apts + 1 store | partly present | PLUTO building facts (`bldgarea`, `numfloors`, `unitsres`) as reference (`builder.py:109-115`; `DashboardPanels.tsx:42`); no existing *zoning* floor area (no DOB connector); no fixture (B) |
| Zoning-lot records | ZL description + certificate (2016, recorded 2022) | absent | No ACRIS source; PLUTO `appbbl`/`appdate` in inventory only (`pluto_soda.py:184`) (B) |
| To verify: parking / transit zone | — | partly present | Raw PLUTO `transitzone` fact only (`builder.py:129`); no rule consumes it (B) |
| To verify: ground-floor commercial required | — | absent | Overlay not a rule input (`integration.py:789`); no commercial trade-off (A) |
| To verify: unit cap with the affordable bonus | — | absent | No DU rule (A) |
| To verify: FRESH eligibility | — | absent | No FRESH data (B §8a) |

---

## §5b existing buildings — paths and traps

| Item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| Path 1 — keep and renovate (Article V) | missing | No non-compliance logic; `over_built` uses PLUTO `bldgarea`, not zoning floor area (`unused_floor_area.py:447-467`) (A) | All | A |
| Path 2 — partial rebuild (ZR 54-41) | missing | "54-41": 0 hits (A; re-checked) | Rebuild budget (floor area + outer-wall length); per-floor inputs; "Not available — needs existing floor-by-floor areas" | A (+B inputs) |
| Path 3 — full rebuild | partial | Equals today's rules: FAR allowance only (see M1-14) (A) | Envelope and building option; no side-by-side comparison | A |
| Trap — >75% floor area and >25% perimeter walls | missing | none found (A) | All | A |
| Trap — unsafe-condition cascade to 75% | missing | none found (A) | All | A |

The §5b headline ("Keeping the building preserves N sq ft…"), its flags (rent regulation, recorded zoning-lot documents, recorded-vs-zoning area gap) and the exceptions are also missing (A, M2-08).

---

## §8a hidden issues — one row per item

| Group | Item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|---|
| Existing building | Larger than today's rules | missing | Flag computed from PLUTO `bldgarea` (`unused_floor_area.py:450`; `constants.py:115-120`) (B) | Contradicted: source forbidden (§3 step 4, §8); needs existing zoning floor area (M2-07) | A + B |
| Existing building | Non-conforming use | missing | none found (B) | Flag and data | B |
| Existing building | Legal use and occupancy on the CO | missing | Research fixtures only (`api/tests/fixtures/dob_legacy/`), no app importer (B) | DOB CO connector and flag | B |
| Existing building | Rent-regulated apartments | missing | No DHCR/HPD source (B) | All | B |
| Existing building | Harassment certification | missing | none found (B) | All | B |
| Zoning-lot history | Recorded zoning-lot descriptions or mergers | missing | No ACRIS; PLUTO `appbbl`/`appdate` in inventory only (`pluto_soda.py:184`) (B) | Flag only (P-2) | B |
| Zoning-lot history | Floor area already transferred | missing | none found (B) | All | B |
| Zoning-lot history | (D) and restrictive declarations | missing | none found (B) | All | B |
| Zoning-lot history | E-designations | partial | Raw PLUTO `edesignum`, `edesigdate` (`builder.py:128`) (B) | No flag, no "Check needed", no primary source | B |
| Map-based | Special districts and overlays | partial | Raw PLUTO special-district/overlay facts; ZTLDB and layers (`api/app/connectors/zoning_features_arcgis.py:186-240`) only on the rule-eval path (LSP + IRE) (B); special district → professional review only (A) | No flag; wave-4 rules missing | B (+A) |
| Map-based | Inclusionary-housing areas | partial | PLUTO `mih_opt1-4` in inventory (`pluto_soda.py:188-189`), not bucketed; no IH-area layer (B) | Flag and layer | B |
| Map-based | Lots split by a district line | partial | Typed class `split_lot_confident` (`api/app/spatial/models.py:28`) + PLUTO `splitzone`; LSP + IRE only (B); UI raw fact only (`format.ts:88`) (D) | Flag beside results; "Check needed" | B (+D) |
| Map-based | Within about 20 ft of a district line | partial | Typed class (`models.py:29`; 20 ft `policy.py:45`) (B) | Flag; "Check needed" | B |
| Map-based | Flood zones and flood-resilience height rules | partial | Raw PLUTO `firm07_flag`, `pfirm15_flag` (`builder.py:129`); no FEMA layer, no resilience-height data (B) | Flag, FEMA source, rules | B |
| Map-based | Waterfront and coastal-zone rules | missing | none found (B) | All | B |
| Map-based | Transit easements near stations | missing | none found (B) | All | B |
| Map-based | Airport height limits | missing | none found (B) | All | B |
| Map-based | Landmarks and historic districts | partial | Raw PLUTO `landmark`, `histdist` (`builder.py:128`); no LPC layer (B); recorded values in `ZoningContextPanel.tsx` (D) | Flag; LPC source | B |
| Site shape and street | Mapped-but-unbuilt streets / widening lines | partial | DCM `Feat_Type` used for width only (`api/app/connectors/dcm_street_centerline_arcgis.py:141`) (B) | Flag | B |
| Site shape and street | Shallow or irregular lots (yard relief) | partial | Raw PLUTO `irrlotcode`, `lotdepth` (`builder.py:101`) (B) | Flag; yard-relief rules | B (+A) |
| Site shape and street | Through lots | partial | Raw PLUTO `lottype` code only (B) | Derived lot type (M2-05) | B |
| Site shape and street | Line-up rules (R6B, R7B, R8B) | partial | Building-footprints connector (`api/app/connectors/building_footprints_arcgis.py`), used only by the scene assembler (B) | Flag and rule | B (+A) |
| Site shape and street | Sloping sites | missing | Only footprint `GROUND_ELEVATION`, with datum caveats (`building_footprints_arcgis.py:20-25`) (B) | Source and flag | B |
| Site shape and street | Neighbors' lot-line windows | missing | none found (B) | All | B |
| Opportunities | Floor-area exemptions (corridors, amenities, refuse rooms) | missing | Group A exclusions/obstructions missing (A) | All | A |
| Opportunities | Affordable and senior housing bonuses | partial | Qualifying FAR stored, never computed (`r6_r12_residential_far.rule.json:37`) (A); PLUTO `affresfar`, `mih_opt*` data (B) | Computed alternative and eligibility inputs | A |
| Opportunities | Height increases for eligible sites | partial | Qualifying heights R1–R5 only (`r5_qrs_height`, `r1_r2_qrs_height`; ZR 23-424) (A) | R6+ heights | A |
| Opportunities | Underbuilt neighbors and assemblage | missing | PLUTO connector is per-BBL only (`pluto_soda.py:600`); no neighbor query (B) | All | B (+A) |
| Opportunities | Lot splits evaluated correctly | missing | 0 hits for lot type / subdivision (A, C-10) | All | A |
| Opportunities | Conversion rules for older non-residential buildings | partial | Raw `yearbuilt`, `bldgclass`, `landuse` only (B) | No conversion rules, no flag | A (+B) |
| Opportunities | FRESH and similar programs | missing | none found (B) | All | B |
| Approvals and process (Phase 2) | Special permits and variances (notes only) | missing | No special permit or variance code (A, L-3) | Opportunity notes (Phase 2 per §8a) | A |
| Approvals and process (Phase 2) | Environmental review for discretionary actions | missing | none found (B marks it n/a as a rules item, not data) | Phase 2 | A |
| Approvals and process (Phase 2) | Demolition prerequisites | missing | none found (B) | Phase 2 | B |

---

## §11b parity rows

| Feature | Plan phase | Status | Evidence | Gap | Lane |
|---|---|---|---|---|---|
| Scenario comparison, floor-by-floor area table, unit estimate with formula | 1 (M1) | missing | No option compare (M1-18); no floor table; "Units" is a `PlannedView` (`DashboardTools.tsx:75`) and "Unit estimate · Not calculated" (`DashboardPanels.tsx:212`) (D); no DU rule (A) | All three | D (+A units, E report) |
| Existing building: keep, partial or full rebuild (§5b) | 1 (M2) | missing | See "§5b existing buildings" (A) | All | A |
| Unused floor area on the lot ("air rights") | 1 | missing | Contradicted: the existing section is cap − PLUTO `bldgarea` (`unused_floor_area.py:447-467`), ISE-gated, tax lot assumed to be the zoning lot (`constants.py:134-143`) (B, D) | Needs existing zoning floor area (M2-07); current section to be set aside (Set-aside list, item 6) | A + B |
| Data flags: flood, E-designation, landmark, transit/parking | 1 | partial | Raw PLUTO columns (`builder.py:127-130`) (B). An "Additional flags" card shows "Unknown — not supplied" for landmark, historic district and the 2007/2015 FIRM flood flags, plus "Pending land-use actions: Unknown — source not connected" (`web/src/components/architect/AdditionalZoningFlags.tsx:4-16`), on the zoning view (`ProfileViews.tsx:30`) and in the report (`ReportView.tsx:116`) (D) | No E-designation or transit/parking flag; no "Check needed" beside the affected results; FEMA/LPC/DCP sources | B (+D) |
| Other programs as options (senior, CF, shared housing, commercial overlay, lot split) | 1 (L-1 to L-3) | missing | Senior/affordable: stored qualifying FAR only; CF, commercial trade-off and lot split missing (A); shared housing: none found | All as options | A (+D switches) |
| Neighbors' unused floor area (Group C) | 1 (after M1) | missing | No neighbor query (`pluto_soda.py:600` is per-BBL) (B); Group C missing (A) | All | B + A |
| Tax-program eligibility (485-x) | 1b | missing | 0 hits for "485" (B, E) | All | E |
| Comparable sales | 1b | missing | 0 hits (B, E) | All | E |
| Financials (L-10) | 1b | missing | `builder.py:494`; `DashboardTools.tsx:76` (E) | All | E |
| Building-code checks; test-fit layouts | 2 | missing | 0 hits (E) | Phase 2 | E |

---

## Other plan sections

### §4 measurements

| Item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| Rank 1 — Survey (entered) | missing | Survey pipeline is standalone (`api/app/documents/promotion.py:16-18`); no importer feeds lot facts (B) | Entry channel and label | B + C |
| Rank 2 — City records (PLUTO, DOF) | partial | PLUTO area, frontage, depth, lot type with units (`pluto_soda.py:199-210`) and provenance; tests `api/tests/connectors/test_pluto_soda.py` (B) | "City records" label; per-street frontage; DOF dimensions not fetched | B |
| Rank 3 — Approximate, tax map | missing | DTM outlines are display-only: "No area, dimension, or measurement is derived" (`api/app/connectors/dtm_lot_outline.py:37-41`); MapPLUTO 2263 area (`mappluto_geometry_arcgis.py:597`) reaches no route (`properties.py:393`, `rule_evaluation.py:363`) (B) | Nothing measured from any outline; label absent | B |
| Unknown — enter | partial | `missing_inputs` "never fabricated" (`builder.py:403-436`); `blocked_missing_critical` (`builder.py:206,470-476`) (B) | Label and entry path | B (+D) |
| Multi-lot combined outline, shared lines removed | missing | none found (B, M2-05) | All | B |
| Frontage only along outside streets | missing | Street lines are caller-attested inputs only (`api/app/scenario/derivation.py:234-261`) (B) | Street-facing edge classification | B |
| Lot type from the combined outline | missing | Raw PLUTO `lottype` code only (`builder.py:101`) (B) | All | B |
| Combined area = sum, checked against outline | missing | No area-vs-outline check (only a Shape__Area divergence note, `mappluto_geometry_arcgis.py:264-267`) (B) | All | B |
| Condo base lots use rank 3 | missing | PLUTO has no base-lot record (`pluto_soda.py:575-585`); DTM outlines display-only (B) | Base lots get no measurement | B |
| Street-width source | partial | DCM `Streetwidth` + `Feat_Type` (`dcm_street_centerline_arcgis.py:141-159,846`) → D-052 policy → 100-ft buffer → live provider (LWS + IRE) (B) | Used only for the wide-street FAR row; no per-frontage width fact; wide segments → professional review (`wide_street_live_provider.py:43-57`) | B (+A) |
| "Needs street width" — wide and narrow side by side | missing | 0 hits (B); unknown width silently takes the narrow row (C, M1-06a) | All | A + B |
| Weakest-input label carries through | missing | No status vocabulary to carry (B) | All | C (+A/B) |
| Coordinates internal only, in feet | partial | 2263 measurement discipline (`mappluto_geometry_arcgis.py:471,597`) (B) | 4326 rings shipped to web (`api/app/api/v1/lot_geometry.py:1-30`); architect-drawn vertices (`outline_bridge.py`, unmounted); DTM outlines have no 2263 path | B (+D set-aside) |

### §5 calculation behavior, add-ons and "Also shown"

| Item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| Calculation behavior: answer shown only when rules reviewed, eligibility resolved, geometry supported; otherwise "Not available" + reason | partial | Typed coverage (`api/app/rules/coverage.py`); family `unsupported` (`registry.py:199-212`); draft never "verified" (`integration.py:235`) (A); web withholding (`development-limits.ts:115-153,198-209`) (D) | No rule is reviewed; supported numbers still carry caution labels (§5a rule 3); no per-district completeness | A (+D) |
| Automatic add-ons always included | partial | Wide-street row only (`api/app/rules/wide_street_wiring.py:461-474`; fold `integration.py:847-871`), behind LWS (A) | Whole-lot grant on any-portion intersect needs a reviewer decision; corner coverage missing | A |
| Optional add-ons as switches, off by default, showing their gain | missing | none found (A, D) | All | A + D |
| Best combination with a stated goal | missing | none found (A, D) | All | A + D |
| Agreement/approval add-ons labeled "With approvals — not guaranteed" | missing | Groups C and D1 missing (A) | All | A |
| Variances and rezonings as an opportunity note | missing | Group D2 missing (A) | All | A |
| Also shown: completeness line | missing | Nearest: "Envelope assessment incomplete…" (`AssessmentCoverage.tsx:20`) (D) | All | D (after A catalog) |
| Also shown: the building (floors, height, footprint) | missing | `MaxEnvelopePanel.tsx:227-248` shows only an "Adopt" button; route unmounted (D) | All | D (after A) |
| Also shown: floor-by-floor area table | missing | none found (D) | All | D/E |
| Also shown: floor stack with editable floor-to-floor | missing | Only the proposal-editor levels table (`ProposalEditor.tsx:345-397`) (D) | Legal stack, stated defaults | D (after A) |

### §5a rules 1–7 ("Label on the box")

| Rule | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| 1. One status strip (≤3 items, tap for details) | missing | No strip; "Active issues" lists issues, not status (`OverviewExceptionStrip.tsx:69`) (D) | All | D |
| 2. Standing notices behind the strip, once | missing | Violated: footer disclaimer on every page (`web/src/app/layout.tsx:35-48`), "Internal" and review lines (`DashboardEntry.tsx:118,122`), "not an approval" (`DashboardPanels.tsx:180`); `web/e2e/honesty.spec.ts:11-23` requires the banner (D) | Floor-area reminder and "zoning lot not verified" absent | D |
| 3. Beside a number, only one real exception | missing | Violated: cap + "Conditional" chip (`DevelopmentLimits.tsx:43-44`, locked by `web/e2e/development-limits.spec.ts:74-83`); unused FA + "(DRAFT …)" (`UnusedFloorAreaSection.tsx:69-77`) (D) | All | D |
| 4. Rule sections, sources, IDs in details | partial | Dashboard sources behind buttons; violations on main views: rule id/version (`MaxEnvelopePanel.tsx:132-146`), "PLUTO reference · {dataset_version}" (`DevelopmentLimits.tsx:124`) (D) | Remove the main-view violations | D |
| 5. Readable; no small grey print; no internal codes | missing | Violated: 9–12 px muted text (`web/src/app/property/architect.css:1,22,35,37`; `workspace.css:79,84`); raw enum (`CoverageBadge.tsx:12-14`); "Lot type code" (`format.ts:85`); raw objective key (`ScenarioWorkspace.tsx:22`) (D) | All | D |
| 6. At most three notices at once, else "Notes (N)" | missing | Violated: ~29 labels on the dashboard for a clean single lot (`DashboardPanels.tsx:131-213`); ~20 on the overview (D) | All | D |
| 7. Acceptance test with the architect | missing | No harness and no session (D) | All (M1-00, M1-21) | D |

### §5c points 1–6 (drawings and report)

| Point | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| 1. One geometry source | partial | Massing truth object (`massing_model.py:376`, per-level plates `:451-460`, `build_from_generated_option` `:506`); `export_service.py:72-75` does not import it (E) | Results do not carry lot outline, yards, setbacks per level, envelope and plates as one contract | A (+E) |
| 2. Server SVG kit (site plan, section, 3D massing, maps) | missing | 0 server SVG; maps are client MapLibre only (E) | All four drawings | E |
| 3. Three outputs, one source | missing | Screen shows no server drawing; PDF, DXF and GLB re-derive from caller rings in separate writers (E) | All | E (+D) |
| 4. PDF composition (HTML → PDF on the server) | missing | Hand-built PDF 1.4 in Helvetica (`pdf_sheet_writer.py:528-545`); web uses browser print (`ReportView.tsx:69`); headless Chromium only in CI Playwright, not in the API runtime (`render.yaml:73-101`) (E) | Converter trial; templates with headers, footers, page numbers, cover | E (+C lock/deploy) |
| 5. Design system and drawing style table | missing | Fixed ACI colors per DXF layer (`dxf_writer.py:112-117`); hard-coded GLB color (`export_service.py:466`); 0 hits for hatch/palette (E) | All | E |
| 6. Quality checks (figures from results, PDF page snapshots) | missing | Byte-hash goldens on one synthetic lot only; no benchmark PDFs, no page compare, no drawing-vs-table check (E) | All | E |

### §6 catalog groups

| Group / item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| Group A — as-of-right | partial | Only the wide-street FAR row and qualifying-housing text exist (A) | 6 of 8 starting items; no add-on data model | A |
| A: Wide-street portion | partial | R6 2.2→3.0, R7-1/R7-2 3.44→4.0, R8 6.02→7.2 (`r6_r7_r8_wide_street_conditional_far.rule.json`); any-portion intersect (`wide_street_wiring.py:461-474`); apportionment "future" (`api/app/connectors/wide_street_buffer_engine.py:49-53`); tests `api/tests/rules/test_rules_integration.py:793-969` (A) | Higher FAR given to the whole lot; floor area not recomputed; reviewer decision; LWS off | A |
| A: Corner-lot coverage | missing | `lot_coverage` unsupported; only a test fixture (`api/tests/rules/fixtures/proposal_checks/rulesets/pc-lot-coverage-demo.rule.json`) (A) | All | A (+B lot type) |
| A: Split-district averaging | missing | Split lots fail safe (`integration.py:744-760`) (A) | All | A |
| A: Floor-area exclusions and permitted obstructions | missing | none found (A) | All | A |
| A: Qualifying affordable or senior housing | partial | Qualifying FAR stored (`r6_r12_residential_far.rule.json:37`), exception text only, never computed (A) | Computed alternative, eligibility inputs, R6+ heights | A |
| A: Community facility floor area | missing | none found (A) | All | A |
| A: Choice of bulk rules (QH vs height factor) | missing | none found (A) | All | A |
| A: Ground-floor commercial trade-off | missing | Worse than absent: R1–R5 height rules escalate any overlay to professional review (`api/app/rules/rulesets/r5_height.rule.json:53`) (A) | Conflicts with §12a (overlay lots use R rules; commercial is a switch) | A |
| Group B — certification | missing | none found (A) | All | A |
| Group C — neighbor | missing | none found (A) | All | A |
| Group D1 — approval with a text maximum | missing | none found (A) | All | A |
| Group D2 — variances and rezonings (note only) | missing | none found (A) | All | A |

### §9 foundations

| Foundation | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| No example data in real work | missing | Violated: `ProposalEditor.tsx:73` → `proposal-draft.ts:421-451` (C, D) | Remove the seed; explicit Example project; guard test | D + C |
| Unknowns stay unknown | partial | `missing_inputs` shown (`web/src/lib/missing-inputs.ts:1-30`); "Not calculated" (`ParcelStudyPanel.tsx:139-141`); rule-eval fails safe with reasons (`integration.py:665-690`) (C) | Unknown street width silently narrow; `wide_street` block absent on the default path (`rule_evaluation.py:161-207`) | A/B (+C) |
| Explicit assumptions | partial | Scenario `assumptions` (`ScenarioAssumptions.tsx`); parcel study "your study assumption" (`ParcelStudyPanel.tsx:116`) (C) | No assumption channel into calculations (M1-08) | C |
| One shared study per property (site shared, options independent, selected option drives report) | missing | No study/option model; report takes no option (`ReportView.tsx:21-27`) (C) | All three sub-rules | C |
| Invalidation 1 — site change marks every option stale | missing | Nearest: parcel-study reset on scope change (`ParcelStudyPanel.tsx:42-44`) (C) | All | C |
| Invalidation 2 — option change affects only that option | missing | No options; proposal variations are local (`ProposalEditor.tsx:80-81`) (C) | All | C/D |
| Invalidation 3 — new rule version marks results | missing | Traces carry `rule_version`/`rule_release`; nothing consumes them (C) | All | C/A |
| Invalidation 4 — late responses never overwrite newer | done | Sequence refs + AbortController (`web/src/lib/architect/use-analysis.ts:17-37`, `use-property.ts:12-26`, `use-parcel-study-records.ts:55-121`, `ProposalEditor.tsx:86-111`); tests `use-parcel-study-records.test.tsx:75,94,111`, `autocomplete.test.tsx:33,200,219` (C, D) | `useAnalysis`/`useProperty` have no dedicated late-response unit test | C |
| Export records inputs, sources, rule versions, results | missing | Export provenance is format/source/time/version/floors only (`export_service.py:592-601`); parcel-study JSON is choices only (`ParcelStudyPanel.tsx:72`) (C, E) | Export record | E (+C store) |
| Reopening an export is read-only history | missing | Import restores an editable draft (`parcel-study.ts:212`; `ParcelStudyPanel.tsx:85`) (C, E) | Read-only history view | E (+D) |
| "Start a new study from this" copies inputs, re-fetches, lists differences | partial | Parcel-study import copies inputs only, checks scope (`parcel-study.ts:163-201`); tests `parcel-study.test.ts:124-177` (C, E) | Multi-lot choices only; no re-fetch; no difference list | C/E |
| Nothing imported becomes a current fact or result | done | Exact-keys allowlist, forged-field refusal, scope match (`parcel-study.ts:65-68,163-201`); tests `parcel-study.test.ts:166,172`, `parcel-study-panel.test.tsx:87` (C) | Holds for the only import today (parcel study); must extend to the future study/export format | C |
| Communication: one identification line ("Option B · revision 7 · date") | partial | "BBL … · Profile generated …" (`ReportView.tsx:77`); "Profile revision …" (`ReportSources.tsx:9`) (C) | Option and revision | E/C |
| Role of AI ("Explain this", examiner questions; never changes numbers) | missing | "Explain this"/examiner: 0 hits (E, L-5). "AI never changes the numbers": unverified (no pass checked it) | All | E |

### §12a waves and safeguards

| Item | Status | Evidence | Gap | Lane |
|---|---|---|---|---|
| Wave 1 — pilot district family | partial | Pilot not chosen (Q1). For R6B: standard FAR only (A) | Heights, coverage, yards, DU, affordable alternative | A |
| Wave 2 — R6–R10 | partial | FAR only (flat and wide-street conditional) (A) | Heights/setbacks, QH/HF, affordable computed, R10H | A |
| Wave 3 — R1–R5 | partial | FAR; heights for all R1–R5 variants (needs_review); R5 setback (A) | Yards, coverage, R1–R4 setback, ADU/TOD, building-type inputs | A |
| Wave 4 — special districts and overlays | missing | Only a `special_district_present` exception → professional review; "special-district-far-modifier (not yet implemented)" (`r6_r12_residential_far.rule.json:69`) (A) | All | A |
| Wave 5 — commercial districts | missing | none found (A) | All | A |
| Manufacturing pathways | missing | none found (A, L-9) | M1-D, special mixed-use, "not allowed" answer | A |
| Honesty rule (district complete only when all outputs reviewed) | partial | Typed coverage; family `unsupported`; draft never verified (`integration.py:235`; `api/app/rules/lifecycle.py:95`) (A) | No per-district completeness to drive "district incomplete" | A |
| Safeguard 1 — exact zone identification | partial | ZTLDB crosscheck + geometric engine; split/uncertain/conflict fail safe (`integration.py:726-760`); unknown district → `not_applicable` (`:826-835`) (A) | Overlay detected (`policy.py:64-68`) but never passed to rule inputs (`integration.py:789`) | B (detect) / A (consume) |
| Safeguard 2 — all-residential headline | partial | Only residential FAR is computed, so it holds trivially (A) | No commercial switch to keep separate | A |
| Safeguard 3 — visible rule basis | partial | Every trace carries citations and snapshot provenance (`evaluator.py:332-345`); export fails closed (`models.py:203`) (A) | No "C district — residential rules of paired R" basis | A |
| Safeguard 4 — differences captured | missing | none found (A) | All | A |
| Safeguard 5 — reviewed before live | partial | G6 lifecycle (`lifecycle.py:72-107`); loader forbids `published` (A) | No rule reviewed; no hand-calculated C examples | A + reviewer |
| Safeguard 6 — R answers locked | missing | FAR values pinned to snapshots, not per-lot golden results (A) | R golden suite | A |

---

## §10 claims check (plan task M1-01)

Each §10 bullet, confirmed or corrected from source.

**Independent M1-01 review — 2026-10-02, worktree head `c81ba14d`.** Every file:line below was
re-checked against source at this head (the section was first written before several Lane PRs
merged). 30 claims verified as cited; 5 carried file:line references that had drifted and are
refreshed in place, each tagged `[M1-01 review …]` in its Evidence cell — the claim text and the
`confirmed`/`corrected` verdicts are unchanged (so the §10 counts, 30 confirmed / 5 corrected, still
hold; "refreshed ref" ≠ "corrected verdict", and only the Draft-rule-evaluation row is in both sets):

- Floating tools: `DashboardEntry.tsx:90-92` → `:100-102` (the cited lines were the analysis-notice block).
- Proposal-editor example site: `proposal-draft.ts:421-451` → `:444-469` (`rectangleSampleDraft`).
- Two property screens: `DashboardTools.tsx:59-61` → `:64-66` (the `study` case).
- Draft rule evaluation: `config.py:38-57` → `:45-58,61-66`; `rule_evaluation.py:259` → `:268`.
- Scenario endpoint: `config.py:60-66` → `:69-75` (that range is now `internal_rule_eval_enabled`).

The `config.py` / `rule_evaluation.py` drift is the M0-T164 (D-090) lane-flag block inserted at
`config.py:38-43` (≈6–9 lines). Observed but NOT changed (outside §10 per the M1-01 scope): the same
stale `proposal-draft.ts:421-451` and `config.py:34,60-66` appear in the Set-aside list (items 2, 3).

| §10 bucket | Claim | Verdict | Evidence | Correction / note |
|---|---|---|---|---|
| Header | "The branch was at `574432f` on 2026-09-27" | confirmed | `2283c178` = `574432fd` + `docs/SESSION_HANDOFF.md` only (git; B, D) | — |
| Working | Address search and confirmation | confirmed | DCP GeoSearch autocomplete (`web/src/lib/address-search.ts:4-8`); resolve route `api/app/api/v1/address_resolution.py:407` (IRE `:420`) → Geoclient (`api/app/connectors/geoclient_address.py:135`); confirm card (`AddressConfirmCard.tsx`) (B, D) | Resolve route off unless IRE set and `GEOCLIENT_SUBSCRIPTION_KEY` present |
| Working | PLUTO property facts | confirmed | `GET /api/v1/properties/{bbl}` (`api/app/api/v1/properties.py:306,393`, ungated) → `pluto_soda.fetch_by_bbl` (`pluto_soda.py:600`) (B) | — |
| Working | Condo billing-to-base lot resolution | confirmed | `api/app/connectors/dtm_condo_soda.py:108-109,376,592`; `condo_base_lot.py:148`; route `condo_records.py:588` (IRE `:601`) (B) | Multi-lot → records only, no calculation |
| Working | Per-lot DOF tax-map outlines | confirmed | `lot_geometry.py:202-255` `source=tax-map` → `dtm_lot_outline.build_lot_outline` (`:274`) (B) | Display only; no measurement derived |
| Working | Parcel picker (each lot or all) | corrected | `ParcelMapViewPicker.tsx:10-30` ("never changes the study's parcel membership"), used at `ParcelStudyMap.tsx:363` (D) | A map camera/focus picker for condo multi-lot outlines only; not the §3 step-2 lot choice; condo base lots have no per-lot size (B) |
| Working | Together/Separately/Compare study state and JSON export/restore | confirmed | `parcel-study.ts:9,112-121,142-223`; `ParcelStudyPanel.tsx:14-18,59-90` (C, D) | Condo sets with ≥2 base lots only (`ParcelStudyPanel.tsx:29`); default is "compare", not "use all"; component-local on two screens |
| Working | Floating tools | confirmed | `FloatingWorkspaceWindow.tsx:69-231`; rendered at `DashboardEntry.tsx:100-102` (import `:28`); test `floating-workspace-window.test.tsx:68-235` (D) — [M1-01 review @ c81ba14d: ref refreshed, was `DashboardEntry.tsx:90-92`] | — |
| Working | Honest withholding of unsupported results | confirmed | `development-limits.ts:115-153,198-209`; `DashboardEntry.tsx:44-46`; `web/e2e/development-limits.spec.ts:86-132` (D) | Supported numbers still carry caution labels (§5a rule 3) |
| Working | Stale-response handling | confirmed | See §9 Invalidation 4 (C, D) | — |
| Working | Server gate and kill switch | confirmed | `web/src/lib/rule-evaluation.ts:92-138`; `web/src/app/property/workspace/page.tsx:14`; `api/app/config.py:28-57`; `web/e2e/rule-evaluation-flag-off.spec.ts:22,38` (C, D) | One flag (IRE) gates 13 handlers; no per-feature kill |
| Working | Recorded-official-data test harness | confirmed | `web/e2e/harness/fixture_api.py:1-40,80-137,319-331` (B) | Covers neither benchmark lot, except DTM outlines for Wallabout |
| Disconnected | Study choices never reach calculations or the report | confirmed | `ParcelStudyPanel.tsx:22-23,139-141`; `use-analysis.ts:6-37` keys on BBL only; `ReportView.tsx:21-27` (C, D) | — |
| Disconnected | Proposal editor starts from an example site | confirmed | `ProposalEditor.tsx:73,87` (`example` prop → seed) → `proposal-draft.ts:444-469` (`rectangleSampleDraft`) (C, D) — [M1-01 review @ c81ba14d: ref refreshed, was `proposal-draft.ts:421-451`] | — |
| Disconnected | Envelope request sent without lot or street lines | confirmed | `web/src/lib/architect/max-envelope-api.ts:555-580` (`lot_line_segments: []`, `street_lines: []` at `:570-571`) (C, D) | Worse: request also omits `lot.bbl`, so server lot-line derivation (`max_envelope_api.py:162-182`) never fires; route is unmounted (`api/tests/api/test_max_envelope_api.py:158`); e2e passes only via a browser mock (`proposal-editor.spec.ts:555`) |
| Disconnected | Site-definition records not connected to combined calculations | confirmed | `api/app/site_definition/records.py:11-19` ("NO calculation path reads a confirmation"); only consumer `condo_records.py:100-103,669-674` (B, C) | — |
| Disconnected | Two property screens host the study | confirmed | `PropertyOverview.tsx:99` (`/property?…&view=overview`); `DashboardTools.tsx:64-66` (`study` case; `/property/workspace?…&tool=study`) (C, D) — [M1-01 review @ c81ba14d: ref refreshed, was `DashboardTools.tsx:59-61`] | Plus aliases `/property/confirm` and `/property/compare` (`confirm/page.tsx:24`, `compare/page.tsx:24`); Q4 open |
| Disabled | Draft rule evaluation behind an internal flag (draft R7 FAR with wide-street branches; R5 path) | corrected | IRE (`config.py:28`, default off `:45-58,61-66`, checked `rule_evaluation.py:268`); also needs LSP (`live_provider.py:72-79`) and LWS (`wide_street_live_provider.py:130,209`) (A) — [M1-01 review @ c81ba14d: refs refreshed after the M0-T164 lane-flag insertion, were default off `:38-57` and check `:259`] | Draft FAR covers **all** R1–R12 ZR 23-21/23-22 rows, not only R7/R5; R7 wide-street only for R7-1/R7-2; `render.yaml` sets none of the three flags |
| Disabled | Scenario endpoint, default-off | confirmed | `config.py:34,69-75`; `scenario.py:174`; `scenario_analysis.py:652,692,732,770` (C) — [M1-01 review @ c81ba14d: `config.py` accessor ref refreshed after the M0-T164 lane-flag insertion, was `:60-66` (now `internal_rule_eval_enabled`)] | Web accepts scenario `1.0.0` only (`scenario-contract.ts:739`) while the schema publishes 1.1.0 (drift) |
| Disabled | Site-definition lifecycle needs authentication and storage | confirmed | In-memory store (`api/app/site_definition/store.py:1-17`); SDW mount (`main.py:217-218`) (C) | — |
| Disabled | 3D/expanded UI under an owner hold | corrected | `.claude/rules/expansion-agent-dispatch-hold.md` §2.3 (D-087, 2026-09-24) released 3D massing, DXF and PDF; `three`/`@react-three/fiber` unused (`web/package.json:18,23`); scene route unmounted (D) | What keeps 3D off is missing code and unmounted routes, not a hold; Q8 (section view) still open |
| Missing | R7 height, setback, yard and coverage rules | confirmed | No height/setback rule for any R6–R12 district; `rear_yard` and `lot_coverage` unsupported; only synthetic fixtures (`api/tests/rules/fixtures/…/pc-*.rule.json`) (A) | Broader than stated: no yard or coverage rule for **any** district |
| Missing | Add-on catalog and toggles | confirmed | See M1-25 (A, D) | — |
| Missing | Maximum-building generator | corrected | Exists: `max_envelope.py:938` and `massing_model.build_from_generated_option` (`:506`) (A) | Unreachable (route not mounted), ineffective (no coverage rule → no candidate, `test_max_envelope.py:628-642`), incomplete (prism, FAR ignored, ≤100 ft floors) |
| Missing | Lot-choice step with the measurement source order | confirmed | See M1-13 and §4 (B, D) | — |
| Missing | DXF export | corrected | A DXF writer exists (`api/app/cad/dxf_writer.py`, via `export_service.py`) behind the unmounted `POST /api/v1/export` (`export_api.py`; absence asserted by `test_glb_writer.py:593-594`) (E) | Not reachable; writes caller rings, not results; no envelope layer |
| Missing | Study revisions and invalidation | confirmed | See M1-11 (C) | Only the late-response rule exists |
| Missing | Report bound to a revision | confirmed | `ReportView.tsx:21-27,69,79` (C, E) | — |
| Missing | Authentication | confirmed | `main.py:6-11` ("authentication is NOT enabled… B-001"); no auth dependency anywhere (C) | — |
| Missing | Durable storage | confirmed | `supabase/migrations` holds only `.gitkeep`; in-memory stores (`site_definition/store.py:9-17`; `documents/storage.py:9-15`) (C) | — |
| Set-aside candidates | Coordinate/vertex proposal drawing in real-property workflows | confirmed | Reachable on both screens (Set-aside list, item 1) (D) | — |
| Set-aside candidates | Example-site defaults | confirmed | Set-aside list, item 2 (D) | — |
| Set-aside candidates | Scenario endpoint (Q5) | confirmed | Set-aside list, item 3 (A, C) | — |
| Set-aside candidates | One of the two property screens (Q4) | confirmed | Set-aside list, item 4 (D) | — |
| Set-aside candidates | Zoning-lot evidence features beyond §8 | confirmed | Set-aside list, item 5 (D) | — |

---

## Set-aside list

Method for every item: **set aside by flag, never delete.** Keep the code and its unit tests; the e2e harness turns a flag on where a spec still exercises the feature.

| # | Item | Exact location | How it is reached today | Set-aside method (flag-based) | Gate |
|---|---|---|---|---|---|
| 1 | Coordinate/vertex drawing in real-property workflows (§7) | Web: `ProposalEditor.tsx` (vertex table `:302-343`, walls `:399-450`), `ProposalOutlineDraw.tsx`, `ProposalOutlineMap.tsx`, `ProposalVariations.tsx`, `ProposalCheckReport.tsx`, `web/src/lib/architect/proposal-draft.ts`, `web/src/lib/proposal-checks-api.ts`, `web/src/lib/outline-bridge-api.ts`. Server: `POST /api/v1/proposal-checks` (`proposal_checks_api.py:455`, mounted `main.py:202`), `POST /api/v1/proposal-validation` (`proposal_validation.py:225`, mounted), `POST /api/v1/outline-bridge` (`outline_bridge.py:625`, unmounted); engine `api/app/scenario/{proposal,proposal_input_gate,derivation}.py`, `api/app/rules/proposal_checks.py` (A, B, C, D) | Nav "Proposal editor" (`ArchitectShell.tsx:7`) → `/property?ruleeval=on&bbl=X&view=proposal` (`ArchitectEntry.tsx:182-183`); dashboard "Draw a proposal", "Envelope", "Buildable envelope" (`DashboardPanels.tsx:156,202,211`) → `DashboardTools.tsx:70-73`; deep link `/property/workspace?…&tool=proposal` or `tool=envelope`. Only gate: IRE | New server-read, default-off `INTERNAL_PROPOSAL_EDITOR_ENABLED` (D) read in the property route pages; when off, drop "proposal" from `PRIMARY`, hide the three buttons, render `PlannedView` or a numbers-only envelope card. Server: leave outline-bridge unmounted; consider gating proposal-checks/-validation on the same flag (C) | No Q gate; plan §7/§10. Note: D-076 (hold notice §2.2) earlier released the proposal-editor slice; the 2026-09-28 plan now excludes coordinate drawing from real-property workflows |
| 2 | Example-site defaults (§9) | `web/src/lib/architect/proposal-draft.ts:421-451` (`rectangleSampleDraft`); seed `ProposalEditor.tsx:73`; unlabeled defaults `ProposalEditor.tsx:341` (vertex 0,0) and `:394` (10 ft floor-to-floor) (D). Server accepts caller-attested values without a guard (`proposal_checks_api.py:338-357`) (C) | Every real-property editor mount | Real-property mounts start from `emptyDraft()` (`proposal-draft.ts:342`); `rectangleSampleDraft` reachable only through an explicit Example project behind a flag; request guard on the server (M1-06a); update the locking tests (`proposal-editor.spec.ts:94-102,149-151`, `entry.test.tsx:443-445`, `proposal-editor.test.tsx:82,204`) | None (M1-06) |
| 3 | Scenario endpoint | `GET /api/v1/properties/{bbl}/scenario` (`api/app/api/v1/scenario.py:160`, gate `:174`); `POST …/scenario/{sensitivity,ranking,comparison,threshold}` (`scenario_analysis.py:642,682,722,760`; no web caller); engine `api/app/scenario/{builder,derive,ranking,sensitivity,comparison,breakeven}.py` (gross-to-net factors are Phase-2-like, A). Web: `scenario-api.ts:228`, `ScenarioWorkspace.tsx`, legacy `CompareScreen`; `ReportView` takes a `scenario` prop (C) | Only when ISE is set (default off, `config.py:34,60-66`; `render.yaml` sets none); the CI harness sets it (`fixture_api.py:402,414`) | Keep ISE off in every deployment (already the default); add a web flag hiding the Scenarios tool/view; keep the rule-evaluation FAR path for the dashboard and report | Q5 |
| 4 | The duplicate property screen | Multi-page shell `ArchitectEntry.tsx` + `ArchitectShell.tsx`, served by `/property?ruleeval=on[&view=*]` (`web/src/app/property/page.tsx:41`), `/property/confirm` (`confirm/page.tsx:24`), `/property/compare` (`compare/page.tsx:24`). Legacy flag-off screens: `PropertyLookup.tsx`, `ConfirmScreen.tsx`, `CompareScreen.tsx` (D) | Default entry: home "Open workspace →" → `/property` (`web/src/app/page.tsx:5`). The §3 dashboard `/property/workspace` is reached only via the nav link (`ArchitectShell.tsx:54`) or a direct URL | After Q4: default-off `INTERNAL_MULTIPAGE_WORKSPACE_ENABLED` with a server-side redirect to `dashboardHref(bbl)` mapping view→tool (`DashboardEntry.tsx:69-71`); keep shared view components; legacy screens stay as the flag-off fallback or go behind `INTERNAL_LEGACY_SCREENS_ENABLED` (D) | Q4 |
| 5 | Zoning-lot evidence features beyond §8 | Site-definition confirmation display (`web/src/lib/condo-records.ts:127-236`; `ParcelStudyPanel.tsx:152`); `CondoRecordsSection.tsx` (D). Server routes `site_definition.py:489,541,579,635`, mounted only with SDW (`main.py:217-218`), read by `condo_records.py:669-674` (C) | Records tool, overview and report (D) | Move behind details or the "Notes (N)" item; keep only the §8 condo line on the main view; keep SDW off (already the default) | None in §13 (plan §10); lifecycle also waits on Q7 |
| 6 | Unused floor area from DOF/PLUTO building area | `api/app/scenario/unused_floor_area.py:447-467`, wired `scenario/builder.py:317`; web `UnusedFloorAreaSection.tsx` at `ScenarioWorkspace.tsx:30,35` and `ScenarioResult.tsx:267`; `CalculationEvidence.tsx:144-150` (A, B, D) | Scenarios tool/view and legacy compare when ISE is on | Flag-hide the web section (D); behind a server flag, emit "Not available — needs existing zoning floor area" instead of the subtraction until M2-07 supplies a zoning value; keep code and tests | Q5 (inside the scenario document); replaced by M2-07 |
| 7 | AutoCAD/PDF drawing import (§7: no AutoCAD import) | `api/app/drawings/**` (DXF reader/import, PDF-sheet reader, alignment); `api/app/api/v1/dxf_import_api.py` (E) | Not reachable: unmounted, and needs `DXF_IMPORT_ENABLED` + IRE (`dxf_import_api.py:110,180-194`) | Keep unmounted and `DXF_IMPORT_ENABLED` off; record it as set aside | None (plan §7) |
| 8 | Answer-first envelope panel and "Adopt" | `MaxEnvelopePanel.tsx`; `max-envelope-api.ts:555-580` → unmounted `/max-envelope` (D) | Inside the proposal tool/view | Set aside with item 1; re-home as the permitted-envelope answer card once A/C mount a route with lot and street lines | None |
| 9 | Planned-tool placeholders (clutter) | `ArchitectShell.tsx:8,63-68` ("Planned" ×3); `DashboardTools.tsx:75-76`; `PlannedView` (`ProfileViews.tsx:75-84`) (D) | Nav and dashboard buttons ("Units", "Financials") | Hide by flag until built | None |

---

## Counts

| Section | Rows | done | partial | missing | not-applicable |
|---|---|---|---|---|---|
| Milestone 1 tasks (incl. M1-06a/b) | 29 | 0 | 14 | 14 | 1 |
| Milestone 2 tasks | 8 | 0 | 1 | 7 | 0 |
| Rest of Phase 1 and Phase 2 (L-1…L-11, P2-1) | 11 | 0 | 3 | 8 | 0 |
| Benchmark checks C-1…C-12 | 12 | 0 | 5 | 7 | 0 |
| §5b paths and traps | 5 | 0 | 1 | 4 | 0 |
| §8a hidden issues | 34 | 0 | 14 | 20 | 0 |
| §11b parity rows | 10 | 0 | 1 | 9 | 0 |
| §4 measurements | 13 | 0 | 4 | 9 | 0 |
| §5 calculation behavior, add-ons, "Also shown" | 10 | 0 | 2 | 8 | 0 |
| §5a rules 1–7 | 7 | 0 | 1 | 6 | 0 |
| §5c points 1–6 | 6 | 0 | 1 | 5 | 0 |
| §6 catalog groups | 13 | 0 | 3 | 10 | 0 |
| §9 foundations | 14 | 2 | 4 | 8 | 0 |
| §12a waves and safeguards | 13 | 0 | 8 | 5 | 0 |
| **Total** | **185** | **2** | **62** | **120** | **1** |

Not in the totals: the 215-16 Northern readiness table (18 values: 2 present, 5 partly present, 11 absent) and the §10 claims check (35 claims: 30 confirmed, 5 corrected). The two "done" rows are both in §9 (late responses never overwrite newer; nothing imported becomes a current fact).

After the independent G1 review the legend was applied the same way everywhere: M1-11, M1-15, M1-16, M1-19, M1-20, C-2 and §11b "Data flags" moved to partial (code toward them exists); M1-17, C-3 and §8a "Larger than today's rules" moved to missing (their only code contradicts the plan, marked "Contradicted").

---

## Summary for the owner

**How much of Milestone 1 exists.** None of the 29 Milestone 1 items meets its "Done when" yet; 14 are partly there and 14 are missing. The groundwork is real and reusable:
- address search and PLUTO facts;
- condo base-lot resolution and the DOF tax-map outlines;
- draft FAR tables for every district in ZR 23-21/23-22 (45 district IDs; R10H, mapped on 18 lots, has none), and draft height tables for R1–R5;
- the single-page dashboard with floating tools;
- honest withholding of unsupported results, and late-response guards;
- the recorded-data test harness and a 20-job CI;
- basic DXF, PDF and 3D writers, which are built but not switched on.

What the architect actually came for is almost entirely missing: the permitted envelope, the building option, add-ons, drawings, the full report and Excel. Roughly, the plumbing is a third of the way there and the answers are near zero.

**Biggest gaps**
1. **No height, setback, yard, coverage or unit rules for R6 and up.** On the benchmark lot (R6B) the app can only give 20,150 sq ft. The 24,180 sq ft affordable-housing figure is never calculated.
2. **No shared study, results or report formats, and no shared store.** The architect's lot and option choices never reach a calculation.
3. **No drawing kit.** The PDF is one sheet, there is no Excel, and exports don't read the engine's results.
4. **No recorded data for the benchmark lot** (215-16 Northern Blvd), so checks C-1 to C-12 cannot run yet.
5. **No measurement labels.** None of the plan's six measurement-status labels (survey, city records, approximate, entered, assumed, unknown) exists yet. Facts already carry their source and a coverage status, unknown inputs are listed rather than guessed, and some flags read "Unknown — not supplied". There is no frontage per street, no lot-type or combined-outline math, and no street width per frontage.
6. **The screens break the "label on the box" rules.** About 29 labels show at once, numbers carry caution labels, the grey text is small, and internal codes appear.

**Where live code contradicts the plan.** These are set aside first, behind switches, and nothing is deleted:
- every real property's proposal editor starts from an example site (R5, 8,000 sq ft, wide street), and tests lock that in;
- coordinate drawing is reachable from the main buttons;
- "unused floor area" subtracts the city-recorded building area;
- the plan's single-page dashboard is not the default screen.

**Top risks**
1. **Reviewer time sets the pace.** No rule is reviewed, and the golden record needs the reviewer and the pilot lot (Q1, Q12).
2. **Some rule questions need a legal ruling.** For example, the code applies the wide-street FAR to the whole lot if any part is within 100 ft. Only the reviewer can settle that.
3. **PDF and Excel need new libraries.** Each must pass the repo's 7-day, zero-advisory rules and a security review. The PDF library may also need system packages the current Render setup lacks.
4. **The screens call routes that are switched off, and tests insist they stay off.** Switching them on needs coordinated changes, which are Lane C's job.
5. **There is no sign-in and no durable storage** (blocker B-001, Q7). Saved revisions and read-only historical exports wait on these.

---

## Spot-check log

All checks were made in the `w0-docs` worktree at `8a813bdd` (code identical to `2283c178`). 48 references checked; 46 matched as cited, 1 was wrong and is corrected above, 1 was imprecise and is refined above. No reference was marked "unverified".

| # | Reference (as cited by the pass) | Pass | Result |
|---|---|---|---|
| 1 | `api/app/rules/integration.py:75` — `TARGET_FAMILY = "residential_far"` | A | matches |
| 2 | `integration.py:789` — inputs are only `zoning_district`, `lot_area_sq_ft` | A, C | matches |
| 3 | `integration.py:351-370` — lot area prefers the MapPLUTO geometry area | A | matches (`_lot_area` at `:351`) |
| 4 | `api/app/scenario/max_envelope.py:938` — `derive_max_envelope` | A | matches |
| 5 | `api/app/scenario/proposal.py:103` — `MAX_FLOOR_TO_FLOOR_FT = 100.0` | A | matches |
| 6 | `api/app/main.py:126-218` — no max-envelope, export, scene or outline-bridge router | A, C, D, E | matches (11 `include_router` calls, none of those) |
| 7 | `api/app/main.py:44,220-223` — health returns only status and version | C | matches |
| 8 | `api/app/scenario/unused_floor_area.py:447-467` — `value = cap - existing_area`, `OVER_BUILT` | A, B | matches (`:450`) |
| 9 | `api/app/scenario/builder.py:317` — unused-floor-area section wired into the scenario | A, B | matches |
| 10 | `r6_r12_residential_far.rule.json:36-37` — R6B 2.0 standard, 2.4 qualifying | A | matches |
| 11 | Flag names at `config.py:28,34`, `live_provider.py:72`, `wide_street_live_provider.py:130` | A, B, C | matches |
| 12 | `api/app/api/v1/rule_evaluation.py:240,259` — BBL-only GET route and IRE gate | A, C | matches |
| 13 | `render.yaml:109-135` — no feature flag declared | A, C | matches (only ENVIRONMENT, Supabase, Geoclient, Anthropic, Sentry, CORS keys) |
| 14 | `web/src/lib/architect/proposal-draft.ts:421-451` — R5 `:447`, 8000 `:443`, wide `:448`, vertices `:429-434` | C, D | matches (C's `:421-449` also valid; the function ends at `:450`) |
| 15 | `web/src/components/architect/ProposalEditor.tsx:73` — seeds `rectangleSampleDraft()` | C, D | matches |
| 16 | `web/e2e/proposal-editor.spec.ts:149-151` — asserts 8000 / R5 / wide in the POST | D | matches |
| 17 | `web/src/lib/architect/max-envelope-api.ts:555-580` — empty lot and street lines at `:570-571`, no `lot.bbl` | C, D | matches |
| 18 | `api/app/api/v1/max_envelope_api.py:269` — `POST /max-envelope` | A | matches |
| 19 | `api/tests/api/test_max_envelope_api.py:158` — test asserting the route is unmounted | C | matches |
| 20 | `api/tests/scenario/test_max_envelope.py:628-642` — real registry gives `candidate is None` | A | matches |
| 21 | `web/src/components/architect/ReportView.tsx:21-27,69,77` — props, `window.print()`, identification line | C, E | matches |
| 22 | "This brief is not saved automatically" — C cited `ReportView.tsx:77-82`, E cited `:79` | C, E | sentence is at `:79`; used `:79` |
| 23 | `ParcelStudyPanel.tsx:22-23,29,48,139-141` | C, D | matches |
| 24 | `web/src/lib/architect/parcel-study.ts:112-121` — default arrangement `"compare"` | C | matches |
| 25 | `DashboardTools.tsx:69-76` — report tool, condo withhold, Units/Financials `PlannedView` | D, E | matches |
| 26 | `DashboardPanels.tsx:41-42,156,202,211` — lot/building fields; Envelope, Draw a proposal, Buildable envelope | B, D | matches |
| 27 | `ArchitectShell.tsx:7` — `PRIMARY` includes "proposal" | D | matches |
| 28 | `ArchitectEntry.tsx:44-50,182-183`; `web/src/app/property/page.tsx:41` | D | matches |
| 29 | `web/src/app/page.tsx:5` — home links to `/property` | D | matches |
| 30 | `web/src/lib/format.ts:85` — "Lot type code" | D | matches |
| 31 | `web/package.json:18,23` — `@react-three/fiber`, `three` | D, E | matches |
| 32 | `web/src/lib/scenario-contract.ts:739` — accepts `"1.0.0"` only | C | matches |
| 33 | `api/app/cad/dxf_writer.py:98-117` — four layers | E | matches |
| 34 | `dxf_writer.py:172-174` — annotation labels, "GENERATED BUILDING OPTION" | E | matches |
| 35 | `dxf_writer.py:84` — `$INSUNITS` 21 | E | **wrong line**: the constant `INSUNITS_US_SURVEY_FEET = 21` is at `:85`; corrected to `:85` in M1-22 |
| 36 | `api/app/cad/export_service.py:527,562` — lot-only export refused (`missing_building_geometry`) | E | **refined**: `:527` defines `_REQUIRES_BUILDING`, `:562` tests it, the refusal code is at `:564`; cited as `:527,562-564` |
| 37 | `export_service.py:72-75` — does not import `massing_model` | E | matches |
| 38 | `api/app/profile/builder.py:98-115,126-131,768` — lot/building columns, mapped features, `user_confirmations: []` | B, C | matches |
| 39 | `api/app/rules/wide_street_wiring.py:461-474` — any-portion intersect selects the wide row | A | matches |
| 40 | `api/app/rules/operations.py:100-107` — `round` is half-away-from-zero only | A | matches |
| 41 | `api/app/rules/evaluator.py:320-323` — `conditional_alternative` effect | A | matches |
| 42 | `api/app/rules/rulesets/r5_height.rule.json:53` — `commercial_overlay_modification` → professional review | A | matches |
| 43 | `api/app/scenario/massing_model.py:376,506` — `build_massing_model`, `build_from_generated_option` | A, E | matches |
| 44 | `api/app/scenario/constants.py:134-143,256-287` — tax lot = zoning lot; static coverage matrix | A, B | matches |
| 45 | `api/app/connectors/dtm_lot_outline.py:37-41`; `api/app/site_definition/records.py:11-19`; `api/app/documents/promotion.py:16-18` | B, C | matches |
| 46 | `api/tests/cad/test_glb_writer.py:593-594` — asserts `main.py` has no `export_api` | E | matches |
| 47 | `.github/workflows/ci.yml:222-223` pytest step; `residential_validation` in `.github/workflows/`: 0 hits | A, E | matches |
| 48 | Greps in `api/app`: "54-41", "23-432", `\b680\b` → 0 hits; "Make sure this floor area" in `web/src` → 0 hits; `AGENTS.md` present; `2283c178` = `574432fd` + `docs/SESSION_HANDOFF.md` | A, C, D | matches |
