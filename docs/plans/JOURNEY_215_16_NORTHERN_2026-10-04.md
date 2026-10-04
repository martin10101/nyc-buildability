# One working journey for 215-16 Northern Boulevard — plan (BBL 4073340070)

Owner directive **D-090-R109** (2026-10-04): prioritise one complete working journey —
real address → selected lots and sourced facts → study → calculation engine → actual
screen → available exports; reuse the existing work; identify the smallest remaining
tasks and dependencies, including the keep/remove choice and existing zoning floor area;
demonstrate what works and name every remaining assumption or missing connection.

This plan reuses the audited evidence in
`docs/walkthroughs/2026-10-04-215-16-northern-blvd.md` (the component-chain walkthrough)
and the lane queues/status under `docs/lanes/`. It changes no code and starts no task;
the orchestrator contracts the slices under the normal gates. Where the plan is silent on
a product or legal rule, this document says so and does not invent one.

A note on scope: today the pieces run **separately** over **test inputs**. No single
request carries a real address through to a drawn screen. This plan names the smallest
wiring that would join them, link by link.

---

## 1. The journey as seven links

For each link: what is proven today (file / test / PR), what is stubbed or missing, and
the smallest task that closes the gap with its dependencies. Queue ids are from
`docs/lanes/queues/{A..E}.md`; a "proposed" slice has no queue row yet.

**State by link (D-090-R133 — built / connected / tested / professionally verified).** The four
states are not collapsed. **built** = code exists; **connected** = wired into the 215-16 Northern
path on the **recorded-fixture** route (a "live?" note says whether it is bound live in production —
**today nothing is live**); **tested** = an automated test on the recorded data **plus** an
independent review PASS on the PR; **professionally verified** = a qualified human (G6) approved the
legal reading — **TRUE FOR NOTHING today** (every rule is `draft` / `needs_review`). The full
element-by-element table is in the walkthrough, section
"Status by state" (`docs/walkthroughs/2026-10-04-215-16-northern-blvd.md`); this is the per-link
summary.

| Link | built | connected (recorded-fixture; live?) | tested | G6 | walkthrough rows |
|---|---|---|---|---|---|
| 1 Real address → BBL | Yes — Geoclient connector + mounted route | **No on this path** (synthetic seam used); never live | connector/route unit tests; no 215-16 fixture | n/a | 1–3 |
| 2 Lots selected | Yes — B-07 (#281); B-03 geometry bridge (#390) | B-07 **connected (fixture)**; B-03 geometry → study read **fixture path only (#390)**, live binding **not connected**; not live | #281, #390 (review PASS) | n/a (zoning lot not verified) | 5, 6 |
| 3 Sourced facts | Yes — PLUTO read; B-05 (#397); street seam `street_data_for_lot` (#403) | PLUTO facts **connected (fixture)**; B-05 → study read **fixture only (#397)**; street seam **built+tested, not attached (#403)** — **street width still not surfaced** | reviews PASS on #329/#397/#403 | none | 4, 7, 8, 9, 10 |
| 4 Study | Yes — study read + study_setup→study bridge (#400); C-07 inert slot (#391) | bridge **closes the shape + lot_type gap (#400)** but the Northern **corner read fails closed** (two frontages); slot inert; not live | #400, #391 (review PASS) | n/a | 11, 12 |
| 5 Calculation engine | Yes — A-04 `generate_results` (#353); A-05 #369 / A-06 #377 **open** | **library-only, no route**; hard-coded `_benchmark_inputs`; not live | #353 (review PASS) | **No** — rules `draft` / `needs_review` | 13, 14 |
| 6 Actual screen | panel exists (#264); results `scope` emission in **#405 open** | **no mounted results route (C-08)**; scope not yet emitted by the engine (#405 open); not live | #264 (review PASS) | **No** | 15, 16 |
| 7 Available exports | Yes — SVG/DXF (#263/#268); maps renderers (#286). **PDF/Excel not built** | SVG/DXF **connected (fixture)**, AutoCAD-open NOT tested; maps **not connected** (no `map_context`); not live | #263/#268/#286 (review PASS) | n/a | 17, 18, 19 |

### Link 1 — Real address → BBL

- **Proven:** a real Geoclient v2 `/address` connector exists
  (`services/api/app/connectors/geoclient_address.py`, M2-T021) and the
  `GET /api/v1/address-resolution` route is mounted (`services/api/app/main.py:163`)
  behind the EXISTING default-off `INTERNAL_RULE_EVAL_ENABLED` flag and returns 200;
  `lot-geometry` is mounted (`main.py:173`).
- **Missing / stubbed (SYNTHETIC in this walkthrough):** the walkthrough drove the route
  through a synthetic test seam (`apps/web/e2e/harness/fixture_api.py:372`
  `harness_address_resolver`, map at `:362`, injected via
  `dependency_overrides[get_address_resolver]` at `:564`): "Northern Boulevard" returns the
  default BBL `1008350041`, **not** the benchmark `4073340070`. The real Geoclient connector
  and route (above) already exist; the walkthrough used the test seam, so the real connector
  was not exercised and the address flow and the benchmark study flow are separate in this
  test setup. The on-card lot outline seam has no feature for the benchmark BBL
  (`lot_geometry.json` → `no_outline`, `fixture_api.py:313`).
- **Smallest task (PROPOSED "B-addr", Lane B/C wiring):** record an official Geoclient
  `/address` fixture for the benchmark address and exercise the **existing** connector +
  mounted route on the recorded path (enabling the flag), so the address step resolves the
  benchmark BBL instead of the synthetic default. **Depends on:** no owner wording decision —
  the geocoder (Geoclient v2) and the route already exist; a live call would additionally need
  the `GEOCLIENT_SUBSCRIPTION_KEY` secret, but the recorded-fixture path does not. Until the
  fixture + wiring land, the walkthrough's address step stays synthetic.

### Link 2 — Lots selected

- **Proven:** lot choice (use all / pick) and the multi-lot math are built — B-07 merged
  (`services/api/app/spatial/multi_lot_site/`, #281) and the D-04 "Lot & site setup" UI
  merged (#310, #322). `study_setup.json` shows one lot, `lot_selection.mode "all"`,
  `combination.status "single_lot"`, and the owner-pinned statement "Based on the lots you
  selected — the app does not verify the zoning lot" (`three_answers/engine.py:48`).
  Single-lot geometry (B-03, lot type / frontage / depth from the outline) merged (#259).
- **Missing / stubbed (INCOMPLETE):** B-03's geometry is **not threaded into the
  study-read document** — the study read is the single-lot *setup* half only, and
  frontage/street-width were explicitly deferred (C request D-1 slice 1). So the read shows
  `lot_type: null` (unknown) even though B-03 can compute "corner" from the outline.
  On-card parcel outline rendering is the D-040-scoped lot-outline increment (MapPLUTO),
  not wired for this BBL.
- **Smallest task (B-03 wiring, PROPOSED Lane C slice):** thread B-03 single-lot geometry
  (lot type, frontage, depth from the outline) into the study-read document.
  **Depends on:** B-03 (done). This is the gap the task packet calls "B-03 lot type from
  geometry".

### Link 3 — Sourced facts

- **Proven (REAL-RECORDED):** lot area 10,075 sq ft, depth 100 ft, zoning R6B, overlay
  C2-2, transit zone "Outer Transit Zone" — all PLUTO 26v2, `version_check current`
  (`study_setup.json`, `transit_parking.json`). B-02 ranks/labels, B-06 version check
  (wired #335), the W2 hidden-issue flags (24 flags, `hidden_issue_flags.json`, route
  mounted #329) and the W3 transit/parking read (mounted #329) are all built.
- **Missing / stubbed (INCOMPLETE):** `existing_zoning_floor_area` reads **unknown**
  (B-05 is built, #274, but no DOB job rows were wired into the study provider);
  `lot_type` reads **unknown** (link 2); **no frontage / street-width fact** in the study
  read (B-04 built, not surfaced — a real gap for a corner lot); 22 of 24 flags are
  `check_needed` (no connected source).
- **Smallest task (B-05 wiring + street-width wiring, PROPOSED Lane C slices):** (a) wire the
  B-05 DOB-filing / certificate rows into the study provider so the existing-floor-area fact
  carries a sourced value (or stays honestly unknown with the rows attached); (b) surface
  street width per frontage into the study read by **connecting the existing envelope fetch to
  the geometry wrapper (reuse — no new connector)**: the EPSG:2263 intersects-envelope
  predicate already exists (`dcm_street_centerline_arcgis.py`) and the benchmark pack already
  carries the recorded envelope query (`dcm_street_centerline_lot_envelope_4073340070.json`).
  **Part (a) is now merged** (#397: B-05 evidence threaded into the study read — honest unknown with
  the DOB figure set aside). **The fetch→wrapper wiring is also now built** (#403:
  `app/spatial/site_geometry/live_streets.py` `street_data_for_lot`, reuse — no new connector). What
  remains is attaching that seam into the study read's live provider
  (`_live_study_inputs_provider` binds no live geometry provider) and **threading street width per
  frontage into the study read** (it is still not surfaced). **Depends on:** B-05 (done, wired #397),
  the street-centerline envelope fetch/parser/wrapper and the `street_data_for_lot` seam (all done,
  #403), link 2 for the frontage geometry.

### Link 4 — Study

- **Proven:** the read-only `GET /api/v1/properties/{bbl}/study` route is mounted behind
  the default-off `INTERNAL_STUDY_READ_ENABLED` flag (D-1 slice 1/2, #316/#317/#318/#320);
  it returns a `study_setup` document (property / lots / lot_selection / site facts). The
  C-05 in-memory study store and the C-06 slice-1 §9 invalidation rules are built (#351).
- **Missing / stubbed (INCOMPLETE):** the study-read document is a `study_setup`, **not** a
  persisted `study` with `options` / `revision` / `study_id`, so the C-07 adapter fails
  closed on it (`build_evaluator_inputs` raises `StudyContractError: Additional properties
  are not allowed ('bbl', 'document_kind')`, and it also requires a known `lot_type`). No
  durable study store persists options/revisions — C-06 slice 2 (saved revisions) is
  blocked on durable storage B-001 / Q7.
- **Smallest task (C-07 adapter, queue row):** close the adapter gap so the study-read
  document bridges to the engine — either the read emits a persistable `study` shape, or
  C-07 accepts the `study_setup` read shape — and it needs a known `lot_type` (link 2).
  **Depends on:** link 2 (lot_type), C-03/C-07 (done).

### Link 5 — Calculation engine

- **Proven (REAL, deterministic):** the three-answer generator
  (`app.scenario.three_answers.generate_results`, A-04 slice 1, #353) recomputes, from the
  draft R6B rule tables, allowance 20,150 / 24,180 sq ft, envelope 30 / 45 / 55 ft,
  a 2-floor FAR-limited building option, and 29 units with the formula
  "20,150 ÷ 680 = 29.63" (`results_lane_a_on.json`). Flag-off yields a valid
  `not_available` document.
- **Missing / stubbed (HARD-CODED inputs; draft rules):** the engine was run on the
  benchmark test's `_benchmark_inputs`, which **hard-codes** the non-site inputs
  (`housing_program`, `overlay_present`, `special_district_present`, within-100-ft,
  angle 90°, `special_density_area`, floor-to-floor 10 ft) and reads `lot_type="corner"`,
  `lot_front_ft=100.8`, `lot_depth_ft=100` from the contract **fixture**, not the live
  study read. All six rules are `0.1.0-draft` / `needs_review`; the document is
  `draft: true` (G6 pending). `ThreeAnswerInputs` (`three_answers/inputs.py`) has **no**
  existing-floor-area or keep/remove field (see §2).
- **Smallest task:** feed the engine from the C-07 adapter (link 4) instead of
  `_benchmark_inputs`; that removes the hard-coded site inputs once the live read carries a
  known lot type and (where supplied) frontage. The non-site flags (overlay present,
  within-100-ft, angle) still need a sourced origin — the plan is silent on where several
  of these come from for a live lot, so they stay named assumptions until a source is
  decided. **Depends on:** link 4 (C-07), golden record M1-05 for final acceptance.

### Link 6 — Actual screen

- **Proven:** `architect/answers/ThreeAnswersPanel.tsx` renders the three answer cards from
  one `results` document (vitest-pinned against the benchmark doc,
  `three-answers-panel.test.tsx`); D-05 merged (#264). By default it **hides draft
  numbers** (`showDraftValues` defaults false → "Not available — the rules for this answer
  are not reviewed yet"). `DevelopmentLimits.tsx` renders "Remaining development capacity:
  Not confirmed" (e2e-pinned, `development-limits.spec.ts`). The D-03 single-page dashboard
  and its §5a passes are merged.
- **Missing / stubbed (INCOMPLETE):** **no mounted route serves the Northern three-answer
  document to a browser** — `three_answers` is library-only (its docstring: "The engine is
  library-only; Lane C mounts any route later."). The only CI screenshot
  (`ci-development-limits-not-confirmed.png`, run 37165881685) is pilot BBL **1000010010**,
  not the Northern lot. D-02 (single-page dashboard as default entry) is blocked on Q4.
- **Smallest task (C-08, queue row):** mount a results route behind flags (flip the tests
  that assert it stays unmounted), send the lot BBL and lines; then point the D-05 panel at
  the live route. **Depends on:** A-04 (done), C-07 (link 4); **owner-blocked** on golden
  record M1-05 (Q1 pilot + Q12 reviewer).

### Link 7 — Available exports

- **Proven (REAL):** the SVG site plan and massing (`app.drawings.kit`, E-01, #263) and
  the results DXF (`app.cad.results_dxf`, E-03, #268 — 4 layers, 9 notes, structurally valid
  per an independent group-code reader, carries the not-a-survey note) are generated and
  cross-checked vertex-for-vertex against the results geometry (`results.dxf`, `dxf_meta.json`);
  the tests prove the file's structure, not that AutoCAD opens it
  (`services/api/tests/cad/test_results_dxf.py` docstring). All behind `LANE_E_ENABLED` (off).
- **Missing / stubbed (INCOMPLETE):** the location/zoning map **renderers exist** (E-07,
  #286 — `app.drawings.maps.render_location_map` / `render_zoning_map`, `load_map_context`);
  they are simply **not connected** to the results/study document for this lot — the
  three-answer results carry no `map_context` block, so `load_map_context` raises
  `MapInputError`. Separately, the report PDF (E-02 converter trial — WeasyPrint vs headless
  Chromium), the E-04 ReportModel report and the E-05 Excel mirror are not built.
- **Smallest task (E-02, queue row):** run the PDF converter trial on the benchmark lots
  and choose a converter. **Depends on:** the dependency-security gate (7-day age, zero
  advisories, G5) and a Render runtime check — an **owner item** (the WeasyPrint/Chromium
  runtime). E-04 depends on E-02 and C-06; E-05 depends on E-04.

---

## 2. The keep/remove choice and existing zoning floor area (one thread)

This choice is captured in the web but **cannot change the answer** today, because the
engine has no field for it. The pieces and their exact order:

1. **Web capture — DONE** (D-06 slice 2, #360; slice 2b #364).
   `apps/web/src/components/architect/ExistingBuildingStep.tsx` records keep / remove /
   no-building and, under "keep", the existing zoning floor area with an explicit source
   (architect entry or stated assumption — never a city source). Nothing pre-selected.
2. **Site fact — DONE as code, NOT wired** (B-05, #274).
   `resolve_existing_zoning_floor_area` takes a certificate / DOB filing / stated
   assumption, never DOF/PLUTO building area. In the study read the fact is **unknown** (no
   DOB rows were wired into the study provider), so there is nothing to subtract — see
   link 3.
3. **Engine field — MISSING** (`three_answers/inputs.py`). `ThreeAnswerInputs` has no
   existing-floor-area, keep/remove, or demolition field (verified in the walkthrough:
   the matching-field search returns empty). So `generate_results` returns the **identical**
   result for "keep" and "remove", and `remaining_floor_area` is **always** `not_available`
   ("Needs verified zoning-lot boundaries and existing zoning floor area.").
4. **Contract slot — MERGED as an inert slot**
   (`packages/contracts/schemas/v1/evaluator_inputs.schema.json`, evaluator_inputs 1.1.0, #391,
   journey wave 1 item 4). The additive existing-floor-area + keep/remove slot was added as a
   `contract_version` bump owned by Lane C; it is inert (flag-off) until the A-07 rule consumes
   it. Before #391 the governing inputs were lot area, frontage, depth, lot type, zoning
   district only.
5. **A-07 rule step (ZR 54-41 existing buildings §5b):**
   - **step 1** — pinned ZR snapshots (54-41, 54-40, 11-23; source text only, no rule, no
     interpretation) in **PR #382, OPEN**, Lane A, merge needs the owner's yes.
   - **step 2** — the draft rule: keep / partial rebuild / full rebuild, rebuild budget,
     both path-2 traps, exceptions only when they apply, headline sentence (A-07 queue row,
     M2-08).
   - **step 3** — the engine consumes it so "keep" keeps more floor area than "full
     rebuild" on this benchmark (M2-08 done-when).

**Exact order (as executed and merged — the additive/inert wiring did NOT wait for PR #382;
#382's merge gates only the A-07 rule step):** the independent, flag-off wiring landed first and
in any order — (a) the evaluator_inputs existing-FA + keep/remove governing slot (Lane C,
additive, flag-off) **merged as #391**; (b) the B-03 site geometry → study read (lot type,
frontage, depth) **merged as #390**, the B-05 existing-floor-area → study-provider wiring (link 3)
**merged as #397**, and the C-07 study-read → engine bridge (link 5) **merged as #400** (the
corner-lot two-frontage input still fails closed); (c) the matching inert
field on `ThreeAnswerInputs` (Lane A, inert until the rule — but its merge still needs the owner's
yes per PR, Lane A). Then, **gated on PR #382's merge
(owner's yes)**: (d) the A-07 draft rule → (e) the engine consumes keep/remove so the answer
differs and remaining capacity can compute → (f) surface it in the D-11 keep/partial/full-rebuild
comparison UI. Remaining capacity still stays "Not confirmed" until **both** a verified zoning lot
(a professional step — the app does not verify it) **and** a sourced existing zoning floor area are
present (owner D-090-R038), and until the rules pass G6.

---

## 3. Dependency table

"Authorized under the lane plan already?" = has a queue row that the owner's GO (D-090-R007)
covers. "Owner decision needed" names the specific gate.

| Task | Depends on | Lane | Owner decision needed? | Authorized under lane plan? |
|---|---|---|---|---|
| B-03 geometry → study read (lot type, frontage, depth) | B-03 (done) | C | No | Partly — D-1 named it a later slice; no discrete row |
| Street width → study read (connect existing envelope fetch → `street_data_from_pages` wrapper; reuse) | envelope fetch/parser/wrapper (all done), B-03 wiring | C | No | Partly — D-1 later slice |
| B-05 existing-FA → study provider | B-05 (done) | C | No | Partly — implied by the study read; no discrete row |
| evaluator_inputs existing-FA + keep/remove slot | C-07 (done) | C | No (DB-113 assumption-override is tangential) | Yes — C-07 follow-up |
| `ThreeAnswerInputs` existing-FA + keep/remove field | A-04 (done) | A | **Yes — owner's yes to merge (Lane A)** | Yes — under A-07 |
| C-07 adapter bridges the live read | B-03 wiring, C-07 (done) | C | No | Yes — queue C-07 (gap named) |
| Real address → BBL (proposed B-addr) | Geoclient connector M2-T021 + route M2-T022 (both done) | B/C | No — geocoder (Geoclient v2) + route already exist; needs a recorded fixture + flag, not an owner choice | No — no queue row |
| A-07 existing buildings §5b rule | A-04 (done), B-05 (done), PR #382 | A | **Yes — owner's yes to merge PR #382; G6/Q12 for the rule** | Yes — queue A-07 |
| C-08 mount results route | A-04 (done), C-07 | C | **Yes — golden record M1-05 (Q1 pilot + Q12 reviewer)** | Yes — queue C-08 (blocked) |
| C-11 recorded-fixture CI journey | C-08, E-03 (done), E-04 | C | Inherits C-08 (M1-05) and E-04 (E-02) | Yes — queue C-11 |
| C-06 slice 2 saved revisions | C-05 (done) | C | **Yes — durable storage B-001 token / Q7** | Yes — queue C-06 (blocked) |
| D-02 default single-page entry | — | D | **Yes — Q4 (which screen is default)** | Yes — queue D-02 (blocked) |
| D-11 keep/rebuild comparison UI | A-07 | D | Inherits A-07 (owner/G6) | Yes — queue D-11 |
| E-02 PDF converter trial | — | E | **Yes — WeasyPrint vs Chromium Render runtime; E-02 converter choice** | Yes — queue E-02 |
| E-04 report from ReportModel | C-06, E-01 (done), E-02 | E | Inherits C-06 (B-001) and E-02 | Yes — queue E-04 |
| Golden record M1-05 | — | A / owner | **Yes — Q1 pilot lot + Q12 reviewer** | Owner input, not a code task |
| G6 qualified legal review of the rules | A-02 / A-04 rules | reviewer | **Yes — qualified reviewer (no rule publishes without it; CLAUDE.md p12)** | Owner/reviewer gate |
| A-05 (no duplicate options) | A-04 (done) | A | **Yes — owner's yes to merge #369 (reviewed PASS)** | Yes — queue A-05 |

---

## 4. What works now, and every remaining assumption or missing connection

From the walkthrough honesty table. Each line carries its label and the task that removes
it. "What works now" first, then the assumptions / missing connections.

**Works now (proven):**
- Lots / study setup — **REAL-RECORDED** (PLUTO 26v2 replayed through the real connector).
- Lot area / depth / zoning / overlay / transit zone — **REAL-RECORDED**, `current`.
- Three-answer computation — **REAL (deterministic)** over its inputs (20,150 / 24,180 /
  30-45-55 / 29 units).
- SVG site plan, SVG massing, DXF — **REAL**, cross-checked vertex-for-vertex.

**Remaining assumptions / missing connections:**
| Item | Label | Task that removes it |
|---|---|---|
| Address resolution → the benchmark BBL | SYNTHETIC (walkthrough seam) | proposed B-addr: record a Geoclient fixture + exercise the existing connector/route (no owner geocoder choice) |
| On-card lot outline for this BBL | INCOMPLETE | D-040 lot-outline increment (MapPLUTO) |
| `lot_type` (PLUTO code 3 unverified; not a zoning-lot type) | INCOMPLETE / NEEDS PROFESSIONAL VERIFICATION | B-03 geometry → study read (link 2) |
| `existing_zoning_floor_area` (unknown; no DOB rows wired) | INCOMPLETE | B-05 → study provider (link 3) |
| Frontage / street width (absent from the study read) | INCOMPLETE | connect the existing envelope fetch to the `street_data_from_pages` wrapper (reuse) → study read (link 3) |
| 22 of 24 hidden-issue flags `check_needed` | INCOMPLETE | B-09 connectors (owner-queued) / reviewer / survey |
| Zoning-lot statement ("app does not verify the zoning lot") | NEEDS PROFESSIONAL VERIFICATION | ACRIS zoning-lot docs read + confirmed (not planned) |
| Keep/remove in the engine | INCOMPLETE | §2 thread (A-07 + inputs.py + contract slot) |
| Three-answer non-site inputs (overlay/angle/within-100-ft/floor-to-floor) | HARD-CODED | C-07 live feed (link 5); several lack a sourced origin — plan silent |
| `lot_type` / frontage used by the engine (fixture-sourced) | HARD-CODED | C-07 live feed (link 4/5) |
| Rule status (all 6 `needs_review`, `draft:true`) | NEEDS PROFESSIONAL VERIFICATION | G6 qualified legal review |
| Screen render for this lot (no mounted route) | INCOMPLETE | C-08 (M1-05 / Q1 / Q12) |
| Maps (E-07) renderers exist (#286) but not connected to the results/study | INCOMPLETE | connect the renderers: feed a `map_context` from the results/study (Lane E) |
| Report PDF / Excel (E-02/E-04/E-05) | INCOMPLETE | E-02 trial (owner runtime) → E-04 → E-05 |
| Durable storage / auth / production | INCOMPLETE | B-001 Supabase token (owner); C-08 mount |

---

## 5. Recommended order for the next two waves

Every item is one small PR, green on its own. **Owner-blocked items are listed but NOT to
be started** (D-090-R007 GO covers the queue rows but the named gates still hold).

**Wave 1 — unblocked wiring (no owner product/gate decision; join the links that already have the
code — but any Lane A merge still needs the owner's yes per PR, e.g. item 5):**
1. [C] B-03 geometry → study read (lot type, frontage, depth from the outline) — closes the
   `lot_type: unknown` gap (link 2).
2. [C] street width per frontage → study read by connecting the existing envelope fetch to the
   `street_data_from_pages` wrapper (reuse — no new connector), after #1 (link 3).
3. [C] B-05 existing-floor-area (DOB rows) → study provider so the fact carries a value or
   stays honestly unknown with the rows attached (link 3 / §2 step 2).
4. [C] evaluator_inputs contract: add the existing-FA + keep/remove governing slot
   (additive, `contract_version` bump, flag-off) — §2 step 4.
5. [A] `ThreeAnswerInputs` (`inputs.py`): add the existing-FA + keep/remove field, inert
   until the A-07 rule — §2 step 4. **Lane A: the merge needs the owner's yes per PR.**
6. [C] C-07 adapter: bridge the live study read to the engine once #1 provides a known lot
   type (link 4). This replaces the hard-coded `_benchmark_inputs` site inputs.

**Wave 2 — rule + mount + exports (several owner-gated; do not start the gated ones):**
7. [A] A-07 existing-buildings §5b draft rule — **needs PR #382 merged (owner's yes) and
   G6/Q12**; do not start the rule before the snapshots merge.
8. [C] **C-08 mount results route — OWNER-BLOCKED on golden record M1-05 (Q1 / Q12). Do not
   start.** This is the one link that puts the Northern numbers on a real screen.
9. [E] E-02 PDF converter trial — the trial may run, but the converter admission needs the
   dependency-security gate and a **Render runtime decision (owner)**; do not pick/admit a
   converter without it.
10. [A] A-05 merge (#369, reviewed PASS) — **owner's yes to merge.**
11. [D] D-11 keep/partial/full-rebuild comparison UI — after A-07 (owner/G6).
12. [C] C-11 recorded-fixture CI journey (address → lots → results → export) — after C-08
    and E-04; this is the test that would prove the whole journey end to end.

**Do not start (owner / human gates):** C-08 and the golden record (M1-05 / Q1 / Q12);
A-07 rule and PR #382 merge (owner's yes + G6); A-05 merge (#369); C-06 slice 2 and E-04
(durable storage B-001 token / Q7); D-02 (Q4); E-02 converter choice (Render runtime);
and the qualified legal review of every draft rule.

The honest shortest path to the journey the owner asked for runs through Wave-1 steps 1-6
(which are unblocked and join address-less lot/fact/study/engine), then is **gated at the
screen** by the golden record M1-05 (C-08) and at the rules by G6 — neither of which an
agent can clear.
