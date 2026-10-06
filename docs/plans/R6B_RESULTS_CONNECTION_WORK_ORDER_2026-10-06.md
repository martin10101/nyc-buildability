# Work order: the first R6B results connection

Written 2026-10-06 by the orchestrator while nothing can merge (blocker B-029, a security advisory).
Asked for by the owner (D-090 source-032: R221 to R229). **Revised the same day after the owner's
check of the first version (D-090 source-033: R235 to R242).**

**This is a work order, not a task and not a result.** Writing it changed no product file. Nothing
described here is built. Building starts only after the waiting changes are merged.

## 0. What the revision changed, and why

The first version listed gaps in section 8 and then planned tests that required the answers those
gaps make uncertain. That would have put uncertain results on the new screen. Corrected here:

| What was wrong | Now |
|---|---|
| Test T3 required the route's answer to equal the saved journey result, which contains whole-lot corner coverage, a full-lot floor plate and a whole-lot rear-yard waiver. | No test accepts a value because it equals a saved result (section 8, rule 3). T3 compares the route with the engine on the same inputs. |
| Tests T4 and T5 and row L5 required 100 percent coverage for a whole corner lot. | 100 percent for a whole lot only when the lot's recorded shape supports it; otherwise "not known" (gap K1). |
| Test W-5 read numbers on the screen from that saved result. | The screen is checked against the law-based tables and against the list of results that must read "not known". |
| Open point D2 made the user answer every input or get no numbers. | An input may stay unanswered. Only the results that depend on it read "not known" (section 7). |
| The two lot-area figures were only to be printed side by side. | One rule for which figure a calculation uses (section 6). |
| Findings F1 to F6 were listed with "none is fixed here" and no rule for the screen. | Every known gap has one of two outcomes: corrected and tested, or "not known" (section 5). |

**The rule for the whole document (R237):** a result is shown as a number only if no known gap
affects it. A gap is either corrected with a test that proves the correction, or every result it
affects reads "not known". A number with a caveat beside it is not a third choice.

## 1. The piece

- **What:** row 1 of section 4.1 of the one-district-at-a-time plan (queue row C-08): the server
  computes the results document for one lot and the website shows it. A server switch, off by
  default, keeps it unreachable until it is turned on.
- **On what:** the benchmark lot, 215-16 Northern Boulevard, Queens (BBL 4073340070), on the recorded
  official data already in the repository. No live city call.
- **Finished means, for this piece only:** with the switches on in a test, a browser opens the lot,
  opens the results, and sees exactly what section 5 allows: a number where no known gap affects it,
  "not known" with the reason everywhere else; every test in section 8 passes; a different agent has
  reviewed each part at its exact commit.
- **Not this piece:** the one shared, saved result every output reads (plan row 2), the number checks
  (row 3), drawings from the result (row 4), a link to the law for every number (row 5), the PDF
  (rows 6 to 8), and the rest of the R6B rules (row 9). This piece does not finish R6B (R206).
- **Scope (R224, R225, R242):** simplified zoning feasibility: how much can be developed, about how
  much fits, simple building shapes, later a clear PDF. No detailed apartment layouts, no permit-ready
  plans, no building-code design. Where closing a gap would need detailed design, the result reads
  "not known" instead.

## 2. Where each statement can be checked

| Name used below | Commit | What it is |
|---|---|---|
| merged | `e97bf405453826bb7855a2129c8433e87bdb95e4` | the integration branch today |
| #432 | `14cd44f59ede7cce4587c89647156d57a9458bd5` | waiting: the rule change replacing the professional sign-off gate (ADR-007) |
| #433 | `af8d820cb6f09f53318393ec6310b7525063be38` | waiting: the standing label on the website |
| #439 | `280471836ce2e54ea37edb596138ad574829ae0a` | waiting: engine changes, first group |
| #440 | `b41dd369bdf5d461a46130a58a159f3fc793a70d` | waiting: results scope, corner-lot assumption, the recorded journey test |

- A `path:line` is the line at the commit named in its row. "Also changed" means a waiting change
  edits the same file, so the line moves when that change merges.
- How it was read: a read-only helper listed the code; the orchestrator re-checked the main claims
  and a script resolved every reference at the named commits.
- No test was run to write sections 3 to 8. The only runs are the engine probes in section 9.

## 3. What exists

Paths in the server rows start at `services/api/`; in the website rows at `apps/web/`.

| # | What | Where | State | Covered by |
|---|---|---|---|---|
| S1 | The engine entry `generate_results`. It runs only when the switch `LANE_A_ENABLED` is on; otherwise every answer is "not available". It checks its own output against the results contract. | `app/scenario/three_answers/engine.py:181` (also changed) | merged | `tests/scenario/three_answers/test_three_answers_benchmark.py` |
| S2 | The engine's input object `ThreeAnswerInputs` | `app/scenario/three_answers/inputs.py:71` (also changed) | merged | same |
| S3 | "Remaining floor area" is always "Not confirmed", never a number | `app/scenario/three_answers/engine.py:21` (also changed) | merged | same |
| S4 | A read route for the lot's facts, `GET /api/v1/properties/{bbl}/study`, behind the off-by-default switch `INTERNAL_STUDY_READ_ENABLED`. It returns lots and sourced site facts, no zoning numbers. | route `app/api/v1/study_read.py:420`; switch `app/config.py:23`; mounted `app/main.py:235` | merged | `tests/api/test_study_read_api.py` |
| S5 | Reusable parts of that route: the data-source seam (recorded data in tests), the rate limit, the typed answers 404 / 422 / 429 / 503, the contract check before sending | `app/api/v1/study_read.py:173`, `:136`, `:217`, `:275`, `:296`, `:342`, `:385` | merged | same |
| S6 | The bridge from the facts read to a full study | `app/contracts/study_setup_bridge.py:81` | merged | `tests/contracts/test_study_setup_bridge.py` |
| S7 | The builders that turn a study into engine inputs. They refuse, by raising `EvaluatorInputsError`, when two sources of the same rank disagree, when an assumption sits beside a sourced value, and when a required value is not known. | `app/contracts/evaluator_inputs.py:297`, `:386`; refusals from `:174` (also changed) | merged | `tests/contracts/test_evaluator_inputs.py` |
| S8 | The list of every assumed input printed beside the numbers (12 rows), and the corner-lot front-line assumption | `app/contracts/engine_disclosures.py:273`, `:118`; `app/scenario/three_answers/scope.py:198` | waiting, #440 | the journey test, S10 |
| S9 | The results contract and its checker | `packages/contracts/schemas/v1/results.schema.json`; `app/contracts/study_contracts.py:196` | merged | contract tests |
| S10 | One test that runs the whole chain on recorded data: BBL, facts read, bridge, inputs, engine, site-plan drawing, AutoCAD file, saved result | `tests/journey/test_215_16_northern_journey.py:120`; saved result `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` | waiting, #440 | itself |
| S11 | The closed list of switches the server reports, pinned by a test | `app/api/v1/build_info.py:56`; `tests/api/test_build_info_api.py:33` | merged | that test |
| S12 | A test pattern for switch-gated read routes (off = a plain 404 identical to a path that does not exist; absent from the public route list) | `tests/api/test_read_router_mounts.py:137` | merged | itself |
| S13 | A guard that refuses example values in a real-property request | `app/api/v1/real_property_guard.py` | merged | its tests |
| S14 | **The rule files already handle an input that is not given.** Overlay and special district are optional inputs; lot type, within-100-ft, the angle and the density area are required ones; in each case a missing input gives no final value, never a default (the files call that state "professional review required" or "not available"). | `app/rules/rulesets/r6b_height.rule.json`, `r6b_lot_coverage.rule.json`, `r6b_rear_yard_corner_waiver.rule.json`, `r6b_dwelling_units.rule.json` (input lists) | merged | rule tests |
| S15 | **The rule files already record their own limits:** coverage is for "standard lots", may be changed by a section that is not captured (ZR 23-363), and applies to a lot "or the zoning-lot portion being evaluated"; the rear-yard waiver covers "only the area within 100 feet of the point of intersection"; with an overlay the commercial rules "are not captured"; the setback of ZR 23-433 is "not encoded". | `r6b_lot_coverage.rule.json:56` to `:58`, `:36`, `:37`; `r6b_rear_yard_corner_waiver.rule.json:64`; `r6b_height.rule.json:29`, `:66` | merged | rule tests |
| S16 | The city-record columns for special districts are already read from the official data set | `app/connectors/pluto_soda.py:163`; used today only as a flag, `app/profile/hidden_issue_flags/map_based_rules.py:23` | merged | their tests |
| S17 | A site fact can already be "unknown": no value, a label "Unknown", and a list of what it blocks | `packages/contracts/schemas/v1/site_fact.schema.json:5` | merged | contract tests |
| S18 | The engine draws the lot as a simple rectangle whose area is the recorded lot area, with proportions from the frontage and depth it was given. It is not the recorded outline. | `app/scenario/three_answers/geometry.py:29`, `:32`, `:34` | merged | drawing tests |
| S19 | The floor plate is the recorded lot area times the coverage ratio | `app/scenario/three_answers/building_option.py:310` | merged | benchmark test |
| S20 | The engine prints "No rear yard is required within 100 ft of the corner" for the lot when the rule applies, and says the setback lines are not available | `app/scenario/three_answers/geometry.py:108`, `:121` | merged | drawing tests |
| W1 | The results panel. Display only: it takes one results document, fetches nothing, and **no page renders it** (only tests do). | `src/components/architect/answers/ThreeAnswersPanel.tsx:39` | merged | `src/components/architect/answers/__tests__/three-answers-panel.test.tsx` |
| W2 | Numbers from unreviewed rules are hidden unless the surface asks for them; the card then says "Not available" with the reason | `src/lib/architect/three-answers.ts:195` | merged | same |
| W3 | Each number prints the name of its law section as text (for example "ZR 23-22"). It is not a link. | `src/components/architect/answers/AnswerCard.tsx:66` | merged | same |
| W4 | Typed server clients to copy the pattern from (timeouts, typed outcomes for 404 / 422 / 503 / 500 / network) | `src/lib/study/study-setup-api.ts:269`; `src/lib/parity-api.ts:347` | merged | their tests |
| W5 | The dashboard's tool switch. Each newer tool sits behind its own server-read, off-by-default switch and shows a plain "not available" view when off. | `src/components/architect/workspace/DashboardTools.tsx:91`; labels `workspace/types.ts:5`; switch reader pattern `src/lib/architect/proposal-editor-flag.ts:19`; `src/app/property/page.tsx:50` | merged | workspace tests |
| W6 | Browser journeys that replace server routes with recorded answers | `e2e/harness/fixture_api.py`; pattern `e2e/parity.flag-on.spec.ts` | merged | the journeys |
| W7 | The standing label ("computed from official sources, not professionally reviewed") | `src/components/architect/StandingReviewLabel.tsx` | waiting, #433 | its tests |
| W8 | A website test that loads the saved journey result and renders it through the panel; every expected string is read from the document | `src/components/architect/answers/__tests__/journey-215-16-northern.test.tsx` | waiting, #440 | itself |

### Where each engine input comes from today

| Input | Source today | Which rules use it |
|---|---|---|
| zoning district, lot area, lot type | sourced facts (city records; lot type from the approximate tax-map outline) | all |
| lot front, lot depth | sourced where present; on a corner lot the front is the address street, shown as an assumption (#440) | the simple rectangle only (S18) |
| commercial overlay present | sent by the caller, and refused if it contradicts the recorded overlay fact | height, coverage, rear yard (a note only; S15) |
| housing program, floor-to-floor height | the user's own choices for an option; they are not facts about the lot | floor area, units; the building option |
| special district present | **no source.** Typed into the journey test as "no". | height, coverage, rear yard, units. The floor-area rule does not look at it. |
| special density area | **no source.** Typed in as "no". | units |
| within 100 ft of a street-line intersection | **no source.** Typed in as "yes", for the whole lot. | rear yard |
| angle of the street lines | **no source.** Typed in as 90. | rear yard |

The engine's input object requires a yes/no or a number for the last four, the overlay and the
program (`inputs.py:89` to `:94`, merged). **The rules can receive "not given" (S14); the engine's
input object cannot pass it on.**

## 4. What is missing

1. **The route.** No server route calls the engine. A search of `services/api/app` finds
   `generate_results` only inside the engine's own folder, and `app/api/v1/` has no results file.
2. **The request.** Nothing defines what the caller sends and what the server must read itself and
   never accept from a caller (lot area, frontage, depth, lot type, district, overlay, special
   district, the reach of the lot from the corner).
3. **"Not given" cannot reach the rules.** The engine's input object requires a value for six inputs
   (section 3). Four of them have no source at all and are typed into the test.
4. **One value inside an answer cannot be "not known".** In the results contract a value must be a
   number (`results.schema.json:640`, merged); only a whole answer can be "not available"
   (`:508`). Coverage sits inside the envelope answer next to the heights, so today it cannot read
   "not known" while the heights are shown.
5. **No check of the lot's shape against the corner rules.** Nothing computes how far the lot reaches
   from each street line or from the corner point. The engine takes one yes/no for the whole lot.
6. **No rule for the two lot-area figures.** The numbers use the recorded lot area; the frontage comes
   from the tax-map outline; the engine's rectangle mixes a frontage from one with a depth from the
   other (S18).
7. **Law text not captured** that the gaps of section 5 depend on: the ZR 12-10 definitions of
   corner, interior and through lot, lot area and special density area; ZR 23-342 (rear yards);
   ZR 23-363 (special coverage rules for some interior and through lots); the Article III sections
   that govern a residential building in a commercial overlay (the rule files name ZR 34-111,
   35-632(a), 34-24(b)(1), 35-631(b) and 35-53).
8. **Typed answers for refusals.** Nothing turns the builders' refusals (`EvaluatorInputsError`,
   `EngineDisclosureError`) into a typed server answer the website can show.
9. **Result identity.** The result id and the time are typed into the test. A route has to set them.
10. **The website.** No results client. No page or dashboard tool shows the panel. No state for
    loading, error or a "not known" value inside an answer. Numbers from unreviewed rules stay hidden
    unless the surface asks for them (W2).
11. **A browser journey** for the results, and a recorded answer for the route in the journey harness.
12. **Two things the queue row assumes that do not exist.** `docs/lanes/queues/C.md:16` says "flip the
    tests that assert it stays unmounted": no such test exists. It also names an owner block on a
    "golden record"; see section 7.

## 5. Every known gap, and what the screen shows

"Corrected" means: changed, with a test whose expected value comes from the law (section 9), before
the result is shown. "Not known" means: the result reads "not known" with the reason until a later
piece corrects it. The remaining-floor-area line keeps its settled wording, "Not confirmed".

| # | Known gap | Where it is recorded | Outcome for this piece | On the benchmark lot |
|---|---|---|---|---|
| K1 | The corner rule (100 percent coverage) covers the part of a corner lot within 100 ft of each street line, not always the whole lot. The engine applies it to the whole lot. | finding F1; S15; the definition (ZR 12-10) is not captured | **Not known**, unless the recorded outline shows the whole lot within 100 ft of each street line and the definition is captured (step P1). | not known: the lot reaches 103.93 ft from the 215 Place street line (a strip about 3.93 ft wide, about 390 sq ft) |
| K2 | The 80 percent for interior and through lots may be changed by ZR 23-363, which is not captured. | S15 | **Not known** until 23-363 is captured and read (step P1). | does not apply (corner lot) |
| K3 | A different maximum applies to lots of 30,000 sq ft or more. | S15 ("standard lots") | **Not known** for lots of 30,000 sq ft or more. | does not apply (10,075 sq ft) |
| K4 | The rear-yard waiver covers only the area within 100 ft of the corner point. The engine takes one yes/no for the whole lot. The ordinary rear yard (ZR 23-342) is not captured. | finding F2; S15; S20 | "No rear yard required" for the whole lot only when the whole lot is within 100 ft of the corner point. Otherwise the rear yard is **not known**, and so is everything that needs a footprint: floor plates, building option, floor stack, floor table. | not known: the far corner is 144.60 ft from the corner point; about 2,560 sq ft of the lot lies beyond 100 ft |
| K5 | Two lot-area figures are in use (10,075 and 10,388 sq ft on this lot). | finding F3; S18 | **Corrected**: the rule of section 6, with tests. | the numbers use 10,075; both figures and the 3.1 percent difference are printed |
| K6 | The building option is lower than the minimum base height, and no independent example exists for a building option. | finding F4 | **Not known**: no building option is shown in this piece. | not known |
| K7 | A reason shown to the user says the site "needs professional review". | finding F5 | **Corrected**: every reason says what is not known and why; a test rejects that phrase. | corrected |
| K8 | The setback above the base (ZR 23-433) is captured and not built. | S15; S20 | The setback reads "not covered". The envelope drawing and any floor above the base height are **not known**. The height limits themselves are table values and are not affected. | not covered / not known |
| K9 | The rules for a commercial overlay are not captured. With an overlay the engine gives the residential number with a note; the floor-area and unit rules do not look at the overlay at all. | finding F6; S15 | On a lot with a recorded overlay **every residential result is not known** until the governing sections are captured and read independently (step P2). | this lot has a recorded C2-2 overlay: **no number is shown for it until step P2 is done**, and then only if that reading supports it |
| K10 | Special district: no source; the floor-area rule ignores it. | section 3; S14 | **Corrected**: read from the city-record columns (S16) as a sourced fact. None recorded: stated as "city records list no special purpose district". One recorded: every result is "not known" (not covered). Not read: unanswered, so every result is "not known". | city records list none (the recorded row has no such column) |
| K11 | Special density area: no source; its definition (ZR 12-10) is not captured. In such an area the unit formula does not apply. | section 3; S14 | Unanswered unless the user states it. Unanswered: the unit count is **not known**. Stated: the count is shown and marked as resting on the user's entry. | not known until the user states it |
| K12 | "Within 100 ft" and the angle: no source; typed in. | section 3 | **Corrected**: computed from the recorded outline and street lines (K1 and K4 use the same measurements). Never typed by a user or a test. No outline: unanswered. | measured: angle 89.7 degrees; reaches as in K1 and K4 |
| K13 | Unit count for qualifying housing. | row L7, L8; S15 | **Not known** (affordable); for senior housing "not set by this formula". | not known |
| K14 | The unit formula does not cover conversions or mixed buildings. | S15 | The count is labelled "new all-residential building". Other cases: **not known**. | labelled |
| K15 | Three sections list "R6" and not "R6B" (coverage, units, rear yard). The rule files apply them through the suffix section, ZR 11-25, and mark that as needing confirmation. | S15 (`r6b_lot_coverage.rule.json:56`) | **Tested**: the independent reading reached the same conclusion from the captured text of 11-25 for all three (section 9, table D). The result cites both sections. | tested |
| K16 | The definitions of zoning lot and floor area are not captured. | finding F6 | The result is already labelled "Tax-lot-only estimate" and never claims the zoning lot. What counts toward floor area is "not covered"; no gross or net area is shown. | labelled / not covered |
| K17 | How height is measured on the lot is not captured. | finding F6 | The height limits are shown as the table's limits. Anything that turns height into floors is **not known** (K6, K8). | limits shown; floors not known |

**What the first screen can show for the benchmark lot.** Until step P2 is done: nothing but the
sourced facts and "not known". After it, and only if its independent reading supports the residential
rules under the overlay: the two floor-area figures and the height limits. The unit count appears
only when the user states the density-area answer. Coverage, rear yard, setback, building option,
floors and the envelope drawing read "not known" or "not covered". That is less than the saved
journey result shows today, on purpose.

## 6. The rule for the two area figures (K5, R239)

1. **One figure for every calculation.** Any calculation that needs the lot's area uses the lot-area
   fact with the best measurement rank: a survey, then an entered value, then city records. On this
   lot that is 10,075 sq ft (city records).
2. **The outline is for shape only.** The area of the tax-map outline is never used in a calculation.
   The outline answers shape questions: the lot type, which sides face a street, the frontage
   lengths, and the two reach measurements of K1 and K4. Everything read from it is marked
   approximate.
3. **No mixing.** A figure is never built from a dimension of one source and a dimension of the
   other. The engine's rectangle (S18) takes both proportions from the outline, is scaled to the
   governing area, is labelled "simplified shape", and is never used to answer a shape question.
4. **The difference is always printed.** The result carries both figures, their difference and which
   one the numbers use, on the website and on every drawing. Above a tolerance it is shown as a
   notice beside the numbers; below it, it stays in the details. The tolerance is set when the part
   is contracted, from the recorded lots, and is written into the result; it hides nothing.
5. **No stand-in.** If no ranked lot-area fact exists, every number that needs the area reads "not
   known". The outline's area is not used in its place.

## 7. Settled points and open points

**Settled by the owner's decisions. No question for the owner.**

- No professional sign-off gate (R164, R165; ADR-007, waiting as #432). The "golden record" block on
  this piece in the older documents is replaced by: one standing label, the law section for each
  number, and "not known" when the program is not sure. Nothing is called verified or compliant.
- The order: results, then report, then PDF (R213). The scope (R210, R224, R225, R242).
- **Missing inputs stay unanswered (R240).** No input is filled by a default or a guess, on the
  server or on the website, and the user is never made to answer. A request with unanswered inputs is
  a normal request. Each result that depends on an unanswered input reads "not known" and names the
  input; the other results are unchanged. A user's own choices for an option (the program, the
  floor-to-floor height) are choices, not facts about the lot; an option exists only when the user
  makes one.
- **A saved result proves nothing (R241).** See section 8, rule 3.

**Open. The orchestrator decides at contract time; the recommendation is given.**

| # | Question | Recommendation | Other choice |
|---|---|---|---|
| D1 | Which switch | a new off-by-default `INTERNAL_RESULTS_ENABLED`. Needs S11's list and its pinned test updated. | reuse existing switches |
| D3 | Shape of the request | `POST /api/v1/properties/{bbl}/results` with a small checked body (the user's option and anything the user chose to state), like the existing `POST /api/v1/max-envelope` | `GET` with the values in the address |
| D4 | Where the website shows it | a new dashboard tool behind its own off-by-default website switch (pattern W5) | a separate page |
| D5 | How one value says "not known" in the contract (missing item 4) | a new contract version in which a value is either a number or "not known" with a reason | move coverage into an answer of its own |

**Needs the owner, unchanged, not asked now:** turning any switch on in production.

## 8. Files that would change, and how success will be tested

Steps in order, one at a time. Each: one writer, then a different agent's review at the exact
commit, then merge. Paths were checked at the named commits; names of new files are proposals.

**Three rules for every test below.**

1. Each test is marked. **[LAW]**: the expected value is typed from section 9, with its section, and
   was worked out without reading the program's answer. **[WIRING]**: it proves the parts are
   connected and the data is carried unchanged. **[UNCHANGED]**: it compares with a saved earlier
   result and proves only that nothing moved.
2. A value is shown because of a [LAW] test or it is not shown. Every result that section 5 marks
   "not known" has a test that it reads "not known".
3. **Matching a saved result is never proof.** No [UNCHANGED] or [WIRING] test is counted as evidence
   that a value is right, and a saved result is never the reason a value appears on the screen. When
   the engine changes, the saved result is regenerated and its differences are reviewed line by line
   against section 5.

### Step P1 and step P2: capture the missing law text, then read it independently

- **Files:** new capture files under `docs/research/zr-snapshots/v1/` and their synced copy, made
  with the existing capture tool. Source text only; no rule and no reading inside the capture.
  P1: ZR 12-10 (lot definitions, lot area, special density area), 23-342, 23-363.
  P2: the Article III sections named in missing item 7.
- **Then, before any rule or gate changes:** a helper that has not seen the program works examples
  from the new text, as in section 9. Its answers set the expected values for the steps below.
- **Tests:** the existing capture checks (the text matches its recorded digest). No number is shown
  because of a capture alone.

### Part 0: make the result honest (server engine and contract)

| | Path | Note |
|---|---|---|
| edit | `services/api/app/scenario/three_answers/inputs.py`, `engine.py`, `answers.py`, `building_option.py`, `geometry.py`, `rule_access.py` | inputs may be "not given"; the outcomes of section 5; the area rule; reasons without the phrase of K7 |
| edit | `services/api/app/scenario/three_answers/scope.py`, `explanations.py`; `services/api/app/contracts/engine_disclosures.py` | exist only in the waiting changes (#439, #440) |
| edit | `services/api/app/contracts/evaluator_inputs.py`; `services/api/app/api/v1/study_inputs.py` | carry the special-district fact and the reach measurements as sourced facts; carry "unknown" facts through |
| new | `services/api/app/spatial/lot_reach.py` and its test | from the recorded outline and street lines: the angle of the street lines, the farthest reach from each street line and from the corner point |
| edit | `packages/contracts/schemas/v1/results.schema.json`, its fixtures, `packages/contracts/generated`, `services/api/app/_contract_schemas`, `apps/web/src/lib/contract.ts` | shared files; a value may be "not known" (D5) |
| edit | `apps/web/src/lib/architect/three-answers.ts`, `src/components/architect/answers/AnswerCard.tsx` and their tests | show a "not known" value inside an answer |
| new | `services/api/tests/scenario/three_answers/test_three_answers_law_examples.py`, `test_three_answers_not_known.py`, `test_three_answers_area_rule.py` | tests H1 to H8 |
| edit | tests that pin today's numbers: `tests/scenario/three_answers/test_three_answers_benchmark.py`; `tests/journey/test_215_16_northern_journey.py` and its saved result; the saved drawings under `tests/cad/snapshots/results_dxf/` and the drawing tests that read results fixtures; the website tests W1 and W8 | found in full with the code-graph impact query when the part is contracted; each change is reviewed against section 5 |

| # | Kind | Test |
|---|---|---|
| H1 | LAW | The benchmark lot through the engine on recorded facts: the floor-area figures (L1, L2) and the height limits (L3, L4) equal section 9, **only if step P2's reading supports them**; if it does not, each reads "not known" and the test asserts that instead. |
| H2 | LAW | The benchmark lot: coverage reads "not known" and its reason carries the measured reach (103.93 ft from the 215 Place street line); the rear yard reads "not known" beyond the corner area (144.60 ft); building option, floor plates, floor stack and floor table read "not known"; the setback reads "not covered". Never a zero. |
| H3 | LAW | Three made-up corner lots with outlines (table C): 40 x 100 ft gives coverage 100 percent and rear yard "not known"; 60 x 80 ft gives coverage 100 percent and no rear yard required anywhere; 150 x 100 ft gives coverage "not known" and rear yard "not known". |
| H4 | LAW | The made-up interior lots of table B: floor area as in the table; unit count as in the table when the density-area answer is stated, "not known" when it is not; coverage "not known" until step P1's reading of 23-363 is in, then the value that reading supports. |
| H5 | LAW and WIRING | Unanswered inputs, one at a time: the special-district fact not read; the density area not stated; no outline; no lot area. Each time the results that depend on it read "not known" and name it, and every other result is unchanged. A recorded special district makes every result "not known". |
| H6 | LAW and WIRING | The area rule: every number that uses an area traces to the one governing lot-area fact; no calculation reads the outline's area; both figures and the difference are in the result; with no lot-area fact the numbers read "not known". |
| H7 | WIRING | No reason text contains "professional review"; every "not known" has a reason and a kind. |
| H8 | UNCHANGED | The regenerated saved journey result equals the engine's output. It proves nothing about correctness (rule 3). |

### Part A: the server route

| | Path | Note |
|---|---|---|
| new | `services/api/app/api/v1/results_read.py` | the route: switch check, rate limit, BBL check, then the existing chain S4 to S1, contract check, answer |
| new | `services/api/app/api/v1/results_request.py` | reads and checks the caller's body. Kept apart so the route file stays small. |
| new | `packages/contracts/schemas/v1/results_request.schema.json` and one valid and one invalid fixture | shared file area; only if D3 is a body |
| new | `services/api/tests/api/test_results_read_api.py`, `test_results_read_law_examples.py` | tests T1 to T11 |
| edit | `services/api/app/main.py`, `services/api/app/config.py`, `services/api/app/api/v1/build_info.py` | mount; the new switch, default off; the reported list (S11). Shared files. |
| edit | `services/api/tests/api/test_build_info_api.py` | its pinned list changes (`:33`) |
| edit | `docs/lanes/queues/C.md`, `docs/lanes/status/C.md`, `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` | the stale lines in section 12 |

| # | Kind | Test |
|---|---|---|
| T1 | WIRING | Switch unset, or set to anything but a true word: a plain 404, byte-identical to a path that does not exist, and the route is absent from the public route list. |
| T2 | WIRING | A malformed BBL: a typed 422, and the data source is never called. |
| T3 | WIRING | The route returns what the engine returns for the same inputs: the test calls both and compares, apart from the id and time fields. It does not compare with a saved file. |
| T4 | LAW | The recorded lot through the route: the same expectations as H1 and H2, numbers and "not known" alike. |
| T5 | LAW | The made-up lots of tables B and C through the same chain: the same expectations as H3 and H4. |
| T6 | LAW | A changed input changes every number that depends on it and nothing else: the lot area 5,355 sq ft gives the floor area and unit count of row P5; a changed floor-to-floor height changes no law limit. |
| T7 | LAW and WIRING | A request with unanswered inputs is answered normally (a 200): the dependent results read "not known" and name the input; the others are shown. A lot whose area is not known gets "not known" for every number that needs it. No zero appears anywhere. |
| T8 | WIRING | Conflicting evidence stays visible: a caller who states something that contradicts a recorded fact does not override it; the answer names both, and the results that depend on it read "not known". |
| T9 | WIRING | Too many calls: a typed 429 before any other work. |
| T10 | WIRING | Example values in a real-property request are refused (S13). |
| T11 | WIRING | Nothing changes in production: the new switch defaults to off, and the change does not touch `render.yaml`. |

### Part B: the website

| | Path | Note |
|---|---|---|
| new | `apps/web/src/lib/results-api.ts` and its test | typed client, same outcome kinds as W4 |
| new | `apps/web/src/lib/architect/results-flag.ts` and its test | the website switch, read on the server, default off |
| new | `apps/web/src/components/architect/ResultsPanel.tsx` and its test | lets the user state inputs or leave them, fetches, shows loading / "not known" / error, then renders the existing panel W1 |
| new | `apps/web/e2e/results.flag-on.spec.ts`, `apps/web/e2e/results.spec.ts` | the journey with the switch on, and the plain "not available" view with it off |
| edit | `apps/web/e2e/harness/fixture_api.py` | a recorded answer for the route, taken from the regenerated saved result of Part 0 |
| edit | `apps/web/src/components/architect/workspace/DashboardTools.tsx`, `workspace/types.ts`, and the entry files that pass switches down (`workspace/DashboardEntry.tsx`, `ArchitectEntry.tsx`, `src/app/property/page.tsx`) | the new tool |

| # | Kind | Test |
|---|---|---|
| W-1 | WIRING | The client maps each server answer to its outcome. |
| W-2 | WIRING | **Numbers agree:** every value on the cards, and every "not known", equals the document the server returned (walk every value; nothing is retyped in the component). |
| W-3 | WIRING | States: loading; switch off (the plain "not available" view, and no call is made); an input left unanswered (its results read "not known", the rest are shown, nothing is prefilled); server error. |
| W-4 | WIRING | The standing label is on the screen once. |
| W-5 | LAW | The browser journey on recorded data: open the lot, open the results. The numbers on the screen are the ones section 5 allows and equal table A; coverage, rear yard and building option read "not known"; stating the density-area answer makes the unit count of row L6 appear, marked as resting on the user's entry. Expected values are typed from section 9, not read from the recorded answer. |
| W-6 | WIRING | Keyboard and screen-reader checks, as the existing suite does for each tool. |

**Not touched by any step:** the rule tables' values, `render.yaml`, any production setting, the CI
configuration, the dependency files.

### Runs and agreement

- Before each step's pull request: the full server suite alone; then the website's lint, type check,
  unit tests, build and browser journeys, one at a time (R211). A run with one failing test is not
  green (R212).
- **Numbers, drawings and PDF agree (R228).** Every output reads the one results document. This piece
  checks the website against it (W-2). The drawings read the same document; where a result is "not
  known" the drawing leaves it out and says so. The PDF does not exist; its piece must add the same
  check. The two area figures are printed everywhere by the rule of section 6.

## 9. Independent, law-based examples

**How they were made.** A helper that had no part in writing the rules was given a sealed folder: the
20 pinned law-text captures (without the notes that describe how the program encoded them) and the
recorded official facts for the lot (without any floor-area-ratio field). It was told not to open the
repository. Its own tool log (read by the orchestrator: 31 calls in the first round, 3 in the
follow-up) shows no file read outside the sealed folder and six page reads, all on the official
Zoning Resolution site. It worked the numbers by hand and read the live official pages for the rows
it relied on (2026-10-06): ZR 23-22, 23-432, 23-362 and 23-52 matched the captures; ZR 12-10 (lot
definitions) and 23-342 are not captured and were read there only. The orchestrator re-read 23-22
("R6B 2.00 2.40") and 23-52 ("680"; "Fractions equal to or greater than three-quarters") on the
official site the same day. **Only afterwards** were the results set beside the program's answers.
Tables C and D come from a follow-up to the same helper, asked after the owner's check, under the
same rules.

**Limits.** This is a draft reading, not professionally reviewed, and not a statement that anything
complies. Most sections were read from the same captures the rules were written from, so an error in
a capture would be shared; the live-page check covers four sections. The corner-lot definition used
in tables A and C was read on the official site and is not yet captured (step P1). It is one lot.

### Table A: the real lot (R6B; a C2-2 overlay is recorded; lot area 10,075 sq ft from city records)

"First screen" is what section 5 allows once steps P1 and P2 are done. Every "number" in that column
also depends on K9: if the reading of step P2 does not support it, it reads "not known".

| # | Quantity | Law relied on | Independent value | Program today | First screen |
|---|---|---|---|---|---|
| L1 | Maximum residential floor area, standard | ZR 23-22, R6B row: 2.00; 2.00 x 10,075 | 20,150 sq ft | 20,150 | number |
| L2 | The same, qualifying affordable or senior housing | ZR 23-22, R6B row: 2.40; 2.40 x 10,075 | 24,180 sq ft | 24,180 | number, as a labelled alternative |
| L3 | Heights, standard | ZR 23-432, R6B row | base 30 to 45 ft; building 55 ft | 30 / 45 / 55 | numbers |
| L4 | Heights, qualifying housing | ZR 23-432, R6B row | base 30 to 45 ft; building 65 ft | 30 / 45 / 65 | numbers, as a labelled alternative |
| L5 | Maximum lot coverage | ZR 23-362(a): corner 100 percent, interior and through 80 percent; the corner part is the part within 100 ft of each street line (official page) | 100 percent on the corner part; the strip beyond is not a corner lot; no single figure for the whole lot | 100 for the whole lot | **not known** (K1) |
| L6 | Maximum dwelling units, standard | ZR 23-52(b): factor 680; a fraction of three-quarters or more counts as one; 20,150 / 680 = 29.63 | 29 | 29 | not known until the user states the density-area answer (K11); then 29 |
| L7 | Dwelling units, qualifying affordable | same; 24,180 / 680 = 35.56 | 35 | "not available" | not known (K13) |
| L8 | Dwelling units, qualifying senior | ZR 23-52(a)(2): no factor applies | not set by this formula | "not available" | not known (K13) |
| L9 | Lot type | two street frontages meeting at 89.7 degrees | corner | corner | fact, marked approximate |
| L10 | Frontages | recorded outline | Northern Boulevard 103.9 ft; 215 Place 100.0 ft | front 103.88 | facts, marked approximate |
| L11 | Street widths | ZR 12-10: 75 ft or more is wide; recorded mapped widths 100 and 60 | Northern wide, 215 Place narrow; no effect on R6B floor area or height | no street-width case | facts |
| L12 | Rear yard | ZR 23-344(a): none required within 100 ft of the point where two street lines meet at 135 degrees or less | waived within 100 ft of the corner point only; the rest is not settled by the captured text | "not required", for the whole lot | **not known** (K4) |
| L13 | Setback above the base | ZR 23-433: 10 ft on a wide street, 15 ft on a narrow street | 10 ft on Northern Boulevard; 15 ft on 215 Place | not modelled | not covered (K8) |
| L14 | Ordinary rear-yard depth | ZR 23-342, not captured | NOT KNOWN from the captured text | not computed | not known (K4) |
| L15 | Building option, floor plates, floors | no independent example | none | 2 floors, 20 ft, plates of 10,075 sq ft | **not known** (K4, K6, K8) |

### Table B: made-up interior lots (R6B, no overlay, standard residences)

| # | Lot | Floor area (2.00 x area) | Area / 680 | Units, independent | Program today (floor area / units) | First screen |
|---|---|---|---|---|---|---|
| P1 | 5,000 sq ft | 10,000 | 14.706 | 14 | 10,000 / 14 | floor area; units when the density-area answer is stated |
| P3 | 5,350 sq ft | 10,700 | 15.735 | 15 | 10,700 / 15 | same |
| P4 | 5,360 sq ft | 10,720 | 15.765 | 16 | 10,720 / 16 | same |
| P5 | 5,355 sq ft | 10,710 | 15.750 exactly | 16 ("equal to") | 10,710 / 16 | same |

The independent reading gives 80 percent coverage for an interior lot from ZR 23-362(a), and the
program gives 80. It stays "not known" on the first screen because of K2.

### Table C: the reach of a corner lot (follow-up; the test values for K1, K4 and K12)

| Lot | Farthest reach from each street line | Farthest point from the corner | Whole lot within 100 ft of each street line? | Of the corner point? | Coverage for the whole lot | Rear yard |
|---|---|---|---|---|---|---|
| The real lot | 99.97 ft (Northern Boulevard); 103.93 ft (215 Place) | 144.60 ft | no: a strip 3.93 ft wide, about 390 sq ft | no: about 2,560 sq ft beyond | not known | not known beyond the corner area |
| C1: 40 ft x 100 ft, 4,000 sq ft | 100.00; 40.00 | 107.70 ft | yes | no | 100 percent | not known beyond the corner area |
| C2: 60 ft x 80 ft, 4,800 sq ft | 80.00; 60.00 | 100.00 ft | yes | yes (exactly on the limit) | 100 percent | none required anywhere |
| C3: 150 ft x 100 ft, 15,000 sq ft | 100.00; 150.00 | 180.28 ft | no: a strip 50 ft wide, 5,000 sq ft | no | not known (no single figure) | not known |

The first version's row "P2, corner, 4,000 sq ft, 100 percent" gave no shape. It is replaced by C1.

### Table D: do the sections that list "R6" apply to R6B? (follow-up; gap K15)

ZR 11-25, captured: "All regulations applicable to a district designation shall be applicable to such
district designation appended with a suffix, except as otherwise set forth in express provisions of
this Resolution." None of the three captures names R6B or a separate rule for a suffixed R6 district.

| Section | Independent conclusion |
|---|---|
| ZR 23-362 (coverage) | applies to R6B, through 11-25 |
| ZR 23-52 (units) | applies to R6B, through 11-25 |
| ZR 23-344 (rear yard) | applies to R6B, through 11-25 |

ZR 23-22 and 23-432 list R6B in a row of its own and need no such step.

### What the comparison shows

Wherever the program gives a number for these lots, the number equals the independent value: floor
area, heights, the unit count, and the coverage percentage of the corner rule. **That does not make
every number fit to show.** The program also gives a number in three cases where the independent
reading says the text does not settle it for the whole lot: coverage (K1), the rear yard (K4) and the
full-lot floor plate (K4, K6). And every number on this lot waits for the overlay reading (K9).

### Findings from the independent reading

F1 to F6 of the first version are now gaps K1, K4, K5, K6, K7 and K9 / K16 / K17 in section 5, each
with its outcome.

## 10. Unknown stays unknown (R229, R240): what must be on the screen

| Case | The screen shows |
|---|---|
| the user left an input unanswered | the results that depend on it read "not known" and name it; the rest are shown; nothing is prefilled |
| a fact was not read (no special-district record, no outline, no lot area) | the same: dependent results "not known" with the reason; never 0 |
| a result that section 5 marks "not known" or "not covered" | those words, with the reason |
| remaining floor area | "Not confirmed" (the settled wording) |
| two sources disagree, or the user contradicts a recorded fact | both values; no number computed from either |
| the server cannot reach its data | "could not be loaded"; nothing made up |

## 11. Order and what must be true first

1. On 2026-10-07 at 14:09 UTC or later: the dependency fix, by the normal reviewed path, started by
   hand. It is not done and not verified today.
2. The waiting changes, one at a time, each on a fresh green run after the fix.
3. Step P1, then step P2: captures, then the independent readings.
4. Part 0, then Part A, then Part B. Each is contracted as a ledger task (citing R166, R167, R213,
   R221 to R229 and R235 to R242), written by one producer on a branch from the then-current
   integration branch, reviewed by a different agent at the exact commit, and merged before the next
   starts.
5. No production switch changes. No timer of any kind.

## 12. Lines in existing documents that are out of date

| Where (merged) | What it says | What is true |
|---|---|---|
| `docs/lanes/queues/C.md:16` | "flip the tests that assert it stays unmounted" | no such test exists |
| `docs/lanes/queues/C.md:16`; `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` (links 5, 6) | this piece is blocked on the owner's "golden record" and reviewer | replaced by R164, R165 and ADR-007 (waiting as #432) |
| `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md:121` (link 4) | the adapter still fails closed on the facts read | the bridge S6 is merged |

## 13. What this document does not establish

- It builds nothing and proves nothing works in a browser. The website was not run.
- The combined tree used for the made-up-lot runs is local and was never pushed.
- Whether the residential rules hold under the commercial overlay is not known. Step P2 decides it;
  this document does not.
- The files listed for Part 0 are the ones known today. The full list of tests that pin today's
  numbers is found when the part is contracted.
- R6B is not finished, the dependency fix is not in, and the program is not complete.
