# Citywide all-at-once replan: every district, overlay and the report pipeline as parallel packets (D-090-R166)

Planner-writer document. It changes no code, contracts no task, and changes no master plan.
The orchestrator alone contracts the packets below under the normal gates and amends the master
plan on the owner's instruction (CLAUDE.md principle 9). No date is promised anywhere.

## 1. Purpose and the owner's decision

The owner decided (D-090 source-027, message 62, R166, 2026-10-04, verbatim):

> we are not narrow ing the target we going to work on it all at once

Target (owner wording, message 60): "every single type of property in NYC from r1 to r12 and
all type flood zoon speacl etc can print such a pdf". R166 reads this as: the target is every
property type in NYC worked in parallel, not a narrowed first district.

This supersedes two earlier sequencing instructions:

- **D-045-R008** said "one reviewed family at a time ... orchestrator wave order A1 to A2+B2 to A3
  to C to M to A4". The dependency order inside a family still holds (capture before draft, data
  before the rule that reads it); what changes is that families now run in parallel across lanes
  instead of one after another.
- The orchestrator's own "narrow the first target" suggestion (answered in chat before message 62)
  is withdrawn by R166.

The master plan is amended by the orchestrator on this instruction. The expansion pack (the 19-task
pack, the 9 contracts, GDS P1 to P8) is reference input only and changes no plan
(`.claude/rules/expansion-agent-dispatch-hold.md` section 2). Accepted work stands at the ledger's
count (325 accepted at capture).

Three other owner decisions from the same source shape this plan:

- **R163:** the orchestrator decides Lane A merges (per PR yes/no), on what is best for the program.
  The ADR-006 Tier D hard stops are untouched.
- **R164/R165:** no professional-review gate is asked of the owner. In its place: a one-time standing
  label on the website and on every exported report that the results need professional review; a
  paper trail that links every stat directly to the zoning-law text it comes from; and the program
  saying plainly when it is not sure. Rules still stay in the draft register, values stay labelled,
  and no compliance is declared.
- **R142:** the report pipeline must return a PDF of the kind in the competitor's 215-16 Northern
  sample, but accurate. No number from the sample is treated as truth
  (`docs/plans/ACCURATE_FEASIBILITY_REPORT_GAP_PLAN_2026-10-04.md`).

## 2. The full target as a checklist

Grouped. Residential coverage per district is read from
`services/api/app/rules/coverage/COVERAGE_MATRIX.md` and `coverage_matrix.json` (45 districts,
118 implemented_draft cells of 646, every cell at most implemented_draft and never reviewed).

### 2.1 Residential districts (45, every one listed; FAR and AO5 are drafted for all 45)

| Group | Districts (matrix order) | Columns drafted today | Still missing |
|---|---|---|---|
| R1 to R5 low-density | R1-2A, R1-1, R1-2, R2A, R2, R3A, R3X, R3-1, R3-2, R2X, R4A, R4B, R4, R4-1, R5A, R5B, R5, R5D | FAR, HGT, AO5 (R5 also SBK) | SBK (except R5), YRD, COV, UNI, AO1 to AO4, AO6 to AO11 |
| R6B contextual (most complete) | R6B | FAR, HGT, YRD, COV, UNI, AO2, AO5 (AO7 is needs_reviewer) | SBK, AO1, AO3, AO4, AO6, AO8 to AO11 |
| R6 to R8 wide-street FAR | R6, R7-1, R7-2, R8 | FAR, AO1, AO5 | HGT, SBK, YRD, COV, UNI, AO2 to AO4, AO6 to AO11 |
| R6 to R12 FAR-only | R6A, R6-1, R6-2, R6D, R7A, R7B, R7D, R7X, R7-3, R8A, R8B, R8X, R9, R9A, R9D, R9X, R9-1, R10, R10A, R10X, R11, R12 | FAR, AO5 | HGT, SBK, YRD, COV, UNI, AO1 to AO4, AO6 to AO11 |

AO12 (variances and rezonings) is not_applicable for all 45 by product decision (opportunity note
only). Height is drafted for 19 of 45 districts; setbacks, yards, coverage and units are drafted for
one or two districts only. The breadth work is: finish height and setback for every R6 to R12
district, and finish yards, coverage and units for every district.

### 2.2 Commercial districts (Article III)

C1 through C8, with the commercial overlays. The ZR structure is captured
(`docs/research/zoning-resolution-2026-07-16.md`: Article III is Commercial District Regulations).
The overlays appear in PLUTO as `overlay1`/`overlay2`
(`services/api/app/profile/hidden_issue_flags/map_based_rules.py`). The enumerated C-district and
overlay list, and the C-to-R equivalence tables (33-121 overlay FAR, 34-111 governing rule, 34-112
equivalents), must be captured from Article III before any rule is drafted. No commercial rule
exists today.

### 2.3 Manufacturing districts (Article IV)

M1, M2, M3, and the residential and mixed-use pathways (MX special mixed-use districts, M1-xD,
loft conversions). Article IV is captured as a structure only
(`docs/research/zoning-resolution-2026-07-16.md`). The governing sections must be captured before
drafting. No manufacturing rule exists today.

### 2.4 Special purpose districts (Articles VIII to XIV)

The ZR names "Articles VIII through XIV set forth the purpose and regulations for each Special
Purpose District", and "Appendix B, Index of Special Purpose Districts"
(`docs/research/zoning-resolution-2026-07-16.md`, captured contents menu). The individual district
list is NOT in the repo. List to be captured from the ZR table of contents and Appendix B before any
special-purpose rule is drafted. Nothing is typed from memory.

### 2.5 Flood zones (Appendix G flood-resilience; FEMA/PFIRM flags)

The data side is partly built: PLUTO `firm07_flag`/`pfirm15_flag` are read with provenance
(`map_based_rules.py`; the module deliberately makes "no flood-zone letter and no Appendix G claim").
Still to capture and build: the flood-zone letter and base flood elevation from a sourced FEMA/PFIRM
dataset, and the ZR flood-resilience height and bulk provisions. The captured ZR contents menu lists
Appendix G as Radioactive Materials and the flood-resilience provisions under the Article VI special
regulations; the exact location and text of the flood-resilience rules must be captured from the ZR
before drafting, not asserted here.

### 2.6 Other overlays

- **Landmarks and historic districts:** PLUTO `landmark`/`histdist` are read as flags (`map_based_rules.py`).
  A landmark designation is an LPC determination, not ZR math, so it stays a flag plus a surface warning,
  not a computed rule.
- **Inclusionary housing (MIH):** PLUTO `mih_opt1` to `mih_opt4` are read as flags. The MIH areas list
  is ZR Appendix F (captured as a structure). The MIH bonus and requirement rules, and the Appendix F
  area list, must be captured before drafting.
- **Waterfront and coastal:** Article VI chapter 2. To be captured before drafting.
- **Transit zones:** the transit/parking read exists (`services/api/app/profile/transit_parking.py`).
  Transit-zone parking exemptions are rules, folded into the parking packet.
- **Parking:** requirements and exemptions, including the transit-zone and City of Yes parking reform.
  To be captured before drafting.

### 2.7 Bonus programs

Affordable and senior (City of Yes Universal Affordability Preference, Affordable Independent
Residences for Seniors), community facility floor area, ground-floor commercial. These are add-on
columns AO5, AO6, AO8 in the coverage matrix with no published rule. Each program's ZR text must be
captured before the add-on is computed as a number rather than a screened-but-not-computed flag.

### 2.8 The report pipeline

Results route, report-model builder, PDF, maps, and the label plus per-stat law links. Gap plan
`docs/plans/ACCURATE_FEASIBILITY_REPORT_GAP_PLAN_2026-10-04.md` records: no report_model builder
exists, no `/reports` route is mounted, no multi-page report PDF, no Excel writer. The contract shape
`packages/contracts/schemas/v1/report_model.schema.json` exists; nothing produces one. Maps renderers
exist (`services/api/app/drawings/maps/`) but are not connected to a results document.

### 2.9 The scenario engine (M5)

`services/api/app/scenario/` has builder, comparison and max_envelope. The compare backend (C-09) and
the compare surfaces (D-10) wire it over rule-backed programs. Scenario comparison is only as broad as
the published families feeding it.

### 2.10 Massing and floor plans (D-087)

Released under D-087 (3D building-and-lot massing, CAD export, PDF blueprints). Primitives exist
(`scenario/massing_mesh.py`, `cad/glb_writer.py`) and a basic floor-by-floor table exists
(`scenario/three_answers/building_option.py`). Still to build: detailed apartment layouts, building
core and deduction calculations, unit schedules, and synthesized floor-plan drawings, each marked
diagrammatic and not for construction.

### 2.11 Live data connections

Geoclient address resolution is built (`services/api/app/connectors/geoclient_address.py`); the
`GEOCLIENT_SUBSCRIPTION_KEY` is set in Render per R161, so the recording can run. Street and geometry
live binding is merged behind the default-off `LIVE_SPATIAL_PROVIDER_ENABLED`. Flipping a flag live in
production is an owner switch.

### 2.12 Financial analysis (HELD, no plan)

Financial feasibility (pro forma, net rentable, 485-x and other tax-abatement tables) stays HELD under
the expansion hold (`.claude/rules/expansion-agent-dispatch-hold.md` section 2). D-087 released 3D, CAD
and PDF blueprints but not financial analysis. This plan names it and plans nothing for it.

## 3. Packetization

Each packet is one independent unit the orchestrator contracts as a ledger task `M<x>-T<n>` citing
`D-090:D-090-R166`. Packets use the existing lane-queue id where one exists, else `NEW-<lane>-<n>`.
Every rule-family packet starts with ZR text capture (snapshot into `docs/research/zr-snapshots/v1/`
plus `sync_zr_snapshots`) before any rule is drafted. New rule files auto-load by glob
(`services/api/app/rules/registry.py:152` globs `*.rule.json`; the module notes adding a rule is
"purely a matter of dropping a new *.rule.json in the rulesets directory, no" registry edit), so
distinct rule filenames and distinct snapshot sections give zero file overlap between parallel packets.
The generated `coverage_matrix.json` and `COVERAGE_MATRIX.md`, the FastAPI wiring (`main.py`,
`config.py`, `api/**`), the contracts (`packages/contracts/**`) and the CI config are hot files edited
only by a Lane C integration packet or by the orchestrator between waves, never by a family packet.

Column key: id, lane, inputs (ZR sections or data to capture first), outputs, size, depends on, owned
directories (no two packets in a wave share a file).

### 3.1 Lane A, rules (engine)

| id | inputs to capture | outputs | size | depends on | owned files |
|---|---|---|---|---|---|
| A-03 | none (set-aside) | legacy building-area subtraction behind a default-off flag; default answer "Not confirmed" | S | none | rules/integration.py flag + its test |
| A-05 | none | no duplicate options, no template sentences | S | A-04 | three_answers emit path + its test |
| A-06 | bonus-model inputs | add-on model: automatic on, optional off, gains, Best combination | L | A-04 | scenario add-on model + its test |
| A-07 | none | existing buildings 5b keep/partial/full rebuild (ZR 54-41) | M | A-04, B-05 | rulesets r_5b_* + test_5b |
| A-10 | 23-22 (captured) | wide-street apportionment per rule text | M | B-04 | rules/wide_street_wiring.py + test |
| NEW-A-01 | R1 to R5 yard, coverage, open-space, unit sections | yards/coverage/units rules R1 to R5 | L | A-01 | rulesets r1_r5_yard_cov_unit_* + test |
| NEW-A-02 | 23-432, 23-433 (captured) | height and setback for every R6 to R12 district | L | A-01 | rulesets r6_r12_height_setback_* + test |
| NEW-A-03 | 23-73x sky-exposure sections | optional sky-exposure plane, un-suffixed R6 to R10 | M | NEW-A-02 | rulesets r6_r10_sky_* + test |
| NEW-A-04 | Quality Housing sections | Quality Housing vs height-factor choice (AO7) | M | NEW-A-02 | rulesets qh_choice_* + test |
| NEW-A-05 | obstruction and averaging sections | AO2 corner coverage, AO3 split-district averaging, AO4 exclusions and obstructions | L | B-03, B-04 | rulesets geom_addon_* + test |
| NEW-A-06 | UAP, AIRS, community facility, ground-floor sections | bonus programs AO5 computed, AO6, AO8 | L | A-06 | rulesets bonus_* + test |
| A-12 | none | Groups B certifications, C neighbor estimate, D1 approval switches, D2 notes | L | A-06 | rulesets group_bcd_* + test |
| A-13 | none | lot-split ideas, each resulting lot its own type | M | A-04, B-03 | scenario lot_split + test |
| NEW-A-07 | Article III: C1 to C8 FAR/bulk, 33-121, 34-111, 34-112 | commercial district rule families | L | A-01 | rulesets c1_c8_* + test |
| NEW-A-08 | Article IV: M1 to M3 residential/mixed pathways | manufacturing rule families | L | A-01 | rulesets m1_m3_* + test |
| NEW-A-09 | Appendix B index + Articles VIII to XIV | special purpose district rule families (decomposed per district once the list is captured) | L | capture | rulesets spd_* + test |
| NEW-A-10 | ZR flood-resilience provisions | flood-resilience height and bulk rules | M | NEW-B-01 | rulesets flood_resilience_* + test |
| NEW-A-11 | Appendix F MIH areas + MIH sections | inclusionary housing bonus and requirement rules | M | B-09 | rulesets mih_* + test |
| NEW-A-12 | Article VI waterfront chapter 2 | waterfront and coastal rules | M | capture | rulesets waterfront_* + test |
| NEW-A-13 | parking sections (incl. City of Yes reform) | parking requirements and exemptions, transit-zone | M | B-10 | rulesets parking_* + test |

### 3.2 Lane B, data and site facts

| id | inputs to capture | outputs | size | depends on | owned files |
|---|---|---|---|---|---|
| B-04 | DCM mapped width | street width per frontage into the study read; unknown reads both results | M | B-03 | spatial street-width surface + test |
| B-05 | DOB filing / certificate rows | existing zoning floor area wired, honest unknown otherwise | M | B-01 | profile/existing_floor_area + test |
| B-09 | 8a group sources | hidden-issue flags group by group with "Check needed" fallback | L | B-01 | profile/hidden_issue_flags + test |
| B-10 | transit/parking source | one transit/parking-zone source applied to every option | S | B-01 | profile/transit_parking + test |
| B-11 | parity datasets | unused floor area, neighbors, 485-x zones, comparable sales, sourced | L | B-05 | profile/parity + test |
| NEW-B-01 | FEMA/PFIRM dataset | flood-zone letter and base flood elevation, flag connected to the study read | M | B-01 | connectors/flood_* + fixtures |
| NEW-B-02 | Geoclient address fixture for the benchmark (key set on Render, R161) | recorded fixture, connector exercised on the recorded path | S | none | connectors fixtures + test |

### 3.3 Lane C, contracts, study and integration

| id | inputs | outputs | size | depends on | owned files |
|---|---|---|---|---|---|
| C-03 | contracts | wire study, site_fact, results, report_model, export_record into typegen and the bundle | M | contracts | packages/contracts + typegen |
| C-04 | none | reject example values in real-property requests | M | none | api request validators + test |
| C-05 | none | one study store for every surface | L | C-03 | web lib/study + test |
| C-06 | none | revisions and dependency-based invalidation | L | C-05 | web study store + test |
| C-07 | none | labeled input channel: entered, assumed, survey distinct from facts | M | C-03, B-02, A-01 | api input channel + test |
| C-08 | none | mount the results route behind flags for the pilot | L | A-04, C-07 | api/v1 results route + test |
| C-09 | none | compare backend: identical rows for two options | M | C-05, A-04 | api compare + test |
| C-10 | none | run the orphaned suites in CI, add the validation-suite job | S | none | CI config |
| C-11 | none | recorded-fixture CI journey address to export | M | C-08, E-03, E-04 | e2e harness + test |
| NEW-C-01 | report_model contract | mount POST and GET /reports behind flags | M | NEW-E-01, C-08 | api/v1 reports route + test |
| NEW-C-02 | per-wave | regenerate coverage_matrix.json and COVERAGE_MATRIX.md, register new rules, run full rules suite (integration serialization point) | S | each wave's A packets | rules/coverage + matrix (integrator only) |

### 3.4 Lane D, architect interface

| id | inputs | outputs | size | depends on | owned files |
|---|---|---|---|---|---|
| D-03 | none | one status strip, details on tap, notices behind the strip | L | none | web components status strip + e2e |
| D-05 | none | three-answers panel against results fixtures | M | contracts | web answers panel + e2e |
| D-07 | none | add-on switches with gains, Best combination picker | M | A-06 | web add-on switches + e2e |
| D-08 | none | plan, section and floor-stack views of the server SVGs | M | E-01, E-01b | web drawing views + e2e |
| D-09 | none | floor-area availability reminder from the status strip | S | D-03 | web reminder + e2e |
| D-10 | none | compare options side by side, plans at a common scale | M | C-09, D-08 | web compare + e2e |
| D-11 | none | keep / partial rebuild / full rebuild comparison with headline | M | A-07 | web rebuild compare + e2e |
| D-12 | none | 8 warnings and 8a flags once, beside the affected results | M | B-09 | web warnings + e2e |
| D-15 | none | parity panels | M | B-11 | web parity panels + e2e |
| NEW-D-01 | R164/R165 wording | one-time standing review label, per-stat zoning-law link, "not sure" rendering on cards, drawings and the screen | M | C-08 | web label + per-stat link + e2e |

### 3.5 Lane E, outputs and parity

| id | inputs | outputs | size | depends on | owned files |
|---|---|---|---|---|---|
| E-01 | contracts | drawing kit v0: SVG site plan and axonometric massing, style table | L | contracts | drawings/kit + snapshots |
| E-01b | none | section SVG in the drawing kit | M | E-01 | drawings/kit section + snapshots |
| E-02 | converter trial | WeasyPrint vs headless Chromium through the dependency gate | M | none | documents trial + G5 report |
| E-03 | none | DXF from results geometry, lot and envelope on separate layers | M | E-01, A-04 | cad/results_dxf + test |
| E-04 | none | report from the ReportModel, bound to option and revision | L | C-06, E-01, E-02, NEW-E-01 | documents report render + test |
| E-05 | none | Excel mirroring the screen with values, units, sources, ZR sections | M | E-04 | documents excel + test |
| E-06 | none | consistency sweep over every report value, page snapshots in CI | M | E-04 | documents sweep + snapshots |
| E-07 | imagery licence | location and zoning maps from city open data, licensed imagery only | M | E-01 | drawings/maps connect + snapshots |
| E-08 | none | "Explain this" and "Likely examiner questions", AI never changes numbers | M | E-04 | documents explain + test |
| E-09 | none | 485-x eligibility note, comparable sales, simple non-financial parity outputs | L | B-11 | documents parity outputs + test |
| NEW-E-01 | report_model contract | report_model builder: assemble one report_model from results plus study, with the standing label and per-stat law links | M | C-08 | documents report_model builder + test |
| NEW-E-03 | scenario geometry | detailed floor plans, building core, unit schedules, massing scene (D-087) | L | E-01, A-06 | drawings/kit + scenario massing |

Packet count by lane and size:

| Lane | S | M | L | total |
|---|---:|---:|---:|---:|
| A | 2 | 9 | 9 | 20 |
| B | 2 | 3 | 2 | 7 |
| C | 2 | 6 | 3 | 11 |
| D | 1 | 8 | 1 | 10 |
| E | 0 | 8 | 4 | 12 |
| total | 7 | 34 | 19 | 60 |

## 4. Parallel waves at 16 agents (8 writers + 8 reviewers)

The owner offered 16 agents (8 writers + 8 reviewers). The standing cap in
`.claude/ORCHESTRATION_POLICY.md` section B is "Normal maximum: three concurrent writing producers;
four concurrent independent reviewers/verifiers. Add agents beyond this only for genuinely independent,
read-only work." Running 8 concurrent writers exceeds that cap, so the agent width (16 or more) is an
owner decision listed in section 6. The policy also requires (section C) that concurrent writers never
overlap on production code, schema, workflow, lockfile, ledger or task-packet paths. Every wave below
is built so no two writers share a file; the hot files (coverage matrix, contracts, CI, `main.py`) are
touched only by Lane C or by the orchestrator between waves.

Merge and CI constraints that do not change under "all at once": one integration branch
(`candidate/D-024-mrl-option-b`); CI runs about 10 to 15 minutes per run; merges happen one PR at a
time (rebase, full CI including the lane path check and web-e2e, merge); merge fails closed on any
non-success; review per change by a different agent; and the merge order C, B, A, D, E when several are
ready (`docs/lanes/PARALLEL_BUILD_PLAN.md` section 2).

Between every wave the orchestrator runs the integration step NEW-C-02: regenerate the coverage matrix,
register the new rule files, and run the full rules suite, so the next wave starts from a clean head.

### Wave 1 (foundations plus the first capture-first families)

Eight writers, each owning a disjoint file set. Reviewers pair one per writer.

| writer packet | lane | why it does not overlap |
|---|---|---|
| NEW-A-02 | A | writes r6_r12_height_setback rule files and its own test; reads captured 23-432/23-433 |
| NEW-A-01 | A | writes r1_r5 yard/coverage/unit rule files and its own test; captures distinct R1 to R5 sections |
| B-04 | B | spatial street-width surface, no rules files |
| B-05 | B | profile/existing_floor_area, no rules files |
| C-03 | C | contracts and typegen only |
| C-04 | C | api request validators only |
| E-01 | E | drawings/kit only |
| D-03 | D | web status strip component only |

Between-wave merge: C-03, C-04 first (Lane C), then B-04, B-05, then A packets, then D-03, E-01, then
NEW-C-02 regenerates the matrix.

### Wave 2 (height and setback breadth plus the study wiring)

| writer packet | lane | why it does not overlap |
|---|---|---|
| NEW-A-03 | A | sky-exposure rule files, distinct from height/setback files |
| NEW-A-04 | A | Quality Housing choice rule files |
| NEW-A-07 | A | commercial C1 to C8 rule files (Article III capture first) |
| B-09 | B | profile/hidden_issue_flags only |
| NEW-B-01 | B | connectors/flood only |
| C-05 | C | web study store |
| E-01b | E | section SVG in the drawing kit (after E-01) |
| D-05 | D | three-answers panel |

### Wave 3 (more families, add-on model and the results route)

| writer packet | lane | why it does not overlap |
|---|---|---|
| NEW-A-05 | A | geometry add-on rule files |
| NEW-A-06 | A | bonus-program rule files |
| NEW-A-08 | A | manufacturing M1 to M3 rule files (Article IV capture first) |
| A-06 | A | scenario add-on model (distinct from rulesets) |
| C-07 | C | api labeled input channel |
| C-08 | C | api results route |
| E-03 | E | cad results DXF |
| D-07 | D | web add-on switches |

Waves 4 and beyond continue the same shape across the remaining packets (special purpose A-09,
flood-resilience A-10, inclusionary A-11, waterfront A-12, parking A-13, groups A-12, lot-split A-13,
report builder NEW-E-01, reports route NEW-C-01, report render E-04, Excel E-05, maps E-07, the
standing label NEW-D-01, the parity and compare surfaces, and the massing detail NEW-E-03), always
eight disjoint writers with the hot files held to Lane C and the between-wave integration step.

## 5. Quality rules that do not change under "all at once"

- Review per change by a different agent; producer is never the verifier (CLAUDE.md principle 7).
- Green CI before any merge; merge fails closed on any non-success; one PR at a time.
- No compliance declaration anywhere; rules stay in the draft register at implemented_draft, never
  higher without the record R164/R165 replaces G6 with (CLAUDE.md principle 12 as amended by R164).
- The standing review label shown once on the website and on every export (R165).
- A direct zoning-law link for every stat, and "not sure" said plainly when the program is not sure
  (R164/R165).
- DB-122 existence checks: every "we do not have X" claim is backed by a recorded `git grep`.
- No number from the competitor sample is treated as truth (R142; gap plan section 1).

## 6. Owner decisions still needed (outside the orchestrator's authority)

- **Agent width:** 16 agents (8 writers + 8 reviewers) exceeds the standing cap of 3 writers / 4
  reviewers (`.claude/ORCHESTRATION_POLICY.md` section B). Running at 16 or more needs the owner's word.
- **Production switches:** flipping any `LANE_*`, `LIVE_*` or `INTERNAL_*` flag live in production.
- **PDF converter choice:** WeasyPrint vs headless Chromium and the Render runtime decision (E-02),
  with the dependency-security age and provenance gate (G5) for the new package.
- **Durable storage:** Supabase token (B-001), gating saved revisions and the report PDF.
- **Imagery licence:** needed before any raster, aerial or street-view base map.
- **Financial-analysis hold:** still suspended under the expansion hold; release is an owner directive.

Professional review is not on this list (R164 removed it as an owner gate).

## 7. What this plan does not do

- It promises no date; gates and holds, not a calendar, decide when each packet runs.
- It contracts no task and changes no master plan; the orchestrator does both on the owner's
  instruction (CLAUDE.md principle 9).
- It invents no rule, no legal reading, no effective date and no source meaning; every rule-family
  packet captures the ZR text first (CLAUDE.md principle 3).
- It copies no number from the competitor sample as truth.

## Appendix: self-checks (DB-122)

Table column counts were checked by reading each table; every table in sections 3 and 4 has a fixed
column count per its header.

`grep -c` for the em dash character in this file returns 0 (checked before commit).

Repo paths cited, each verified present with `git ls-files`:

- `services/api/app/rules/coverage/COVERAGE_MATRIX.md`, `coverage_matrix.json` (present)
- `services/api/app/rules/rulesets/` (23 tracked `*.rule.json`)
- `services/api/app/rules/registry.py` (present; line 152 globs `*.rule.json`)
- `docs/research/zr-snapshots/v1/` (20 tracked snapshots)
- `docs/plans/ACCURATE_FEASIBILITY_REPORT_GAP_PLAN_2026-10-04.md`,
  `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` (present)
- `docs/lanes/PARALLEL_BUILD_PLAN.md`, `docs/lanes/queues/{A,B,C,D,E}.md` (present)
- `docs/IMPLEMENTATION_SEQUENCE.md`, `docs/research/zoning-resolution-2026-07-16.md` (present)
- `.claude/ORCHESTRATION_POLICY.md`, `.claude/rules/expansion-agent-dispatch-hold.md` (present)
- `packages/contracts/schemas/v1/report_model.schema.json`, `results.schema.json`,
  `map_context.schema.json` (present)
- `services/api/app/connectors/geoclient_address.py` (present)
- `services/api/app/profile/hidden_issue_flags/map_based_rules.py` (present)
- `services/api/app/scenario/`, `scenario/three_answers/`, `drawings/`, `cad/`, `documents/` (present,
  tracked files: 32 / 10 / 40 / 8 / 30)

Queue ids cited, each verified present in `docs/lanes/queues/*.md`:

- Lane A: A-01, A-03, A-04, A-05, A-06, A-07, A-10, A-12, A-13 (A queue holds A-01 to A-14)
- Lane B: B-01, B-02, B-03, B-04, B-05, B-09, B-10, B-11 (B queue holds B-01 to B-11)
- Lane C: C-03, C-04, C-05, C-06, C-07, C-08, C-09, C-10, C-11 (C queue holds C-01 to C-14)
- Lane D: D-03, D-05, D-07, D-08, D-09, D-10, D-11, D-12, D-15 (D queue holds D-01 to D-15)
- Lane E: E-01, E-01b, E-02, E-03, E-04, E-05, E-06, E-07, E-08, E-09 (E queue holds E-01, E-01b, E-02 to E-09)

`NEW-<lane>-<n>` ids are new by design (no queue row yet) so the orchestrator can contract them.
