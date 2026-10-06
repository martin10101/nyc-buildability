# Work order: the first milestone of the R6B feasibility report - results on the screen

Written 2026-10-06 by the orchestrator while nothing can merge (blocker B-029, a security advisory).
Asked for by the owner (D-090 source-032: R221 to R229). Corrected after the owner's check (source-033:
R235 to R242). Revised on the owner's decisions of the same day (source-035: R248 to R265), with the three
corrections its second audit required. **Corrected again after the owner's check of that revision
(source-036: R266 to R273): "not checked" is never "confirmed".**

**This is a work order, not a task and not a result.** Writing it changed no product file. Nothing
described here is built. Building starts only after the waiting changes are merged.

**The goal is the full feasibility report** of the kind of the owner's sample, with reliable numbers
(R248). This work order covers its first milestone only. A milestone is not completion (R251), and a
screen of zoning limits is not the product (R249). The whole report, section by section against the
sample, is in `docs/plans/FEASIBILITY_REPORT_SECTION_MAP_2026-10-06.md`.

## 0. What each revision changed

| Revision | What was wrong | Now |
|---|---|---|
| second (owner's check) | Tests T3, T4, T5 and W-5 required the saved journey result or 100 percent coverage for a whole corner lot. Gaps were listed with no rule for the screen. | No test accepts a value because it equals a saved result. Whole-lot coverage only when the lot's shape supports it. Every known gap has an outcome (section 5). |
| third, audit correction 1 | The unit count would have been shown as a number once the user said the lot is not in a special density area, a fact the program cannot check. | A user's statement can only produce a result labelled as conditional on that statement. It is never a settled number and never stored as a fact (rule 1 below; gap K11). |
| third, audit correction 2 | No test checked that the unit count for qualifying housing reads "not known". | Test H2 now does. |
| third, audit correction 3 | The text said no input is filled by a default, while the engine carries a 10 ft floor-to-floor default. | Design choices may start from a value the user can see and change. Nothing is used that is not shown (rule 2 below; test H10). |
| third, owner's decisions | "A number or not known, nothing else"; the recorded lot area used with a notice; nothing prefilled; "unsupported" counted as an outcome. | The six rules below. |
| fourth (owner's check of the third) | The R6B height limits were to be shown as settled for the property, and for conditions the program has no data for the recommendation was a visible "not checked" list. Together that would have shown a district height as the property's confirmed maximum beside a disclaimer. | "Not checked" is never "confirmed" (R267). An answer an unchecked condition cannot change stays visible; one that holds only if the condition does not apply is conditional and names it; one that cannot be supported is withheld (R268, gap K20). The R6B height is the district's limit, not the property's confirmed maximum (R269). Tests H1, H3, H4, T4 and W-5 changed; test H11 added. |
| this one, its audit's corrections | Four sentences still let a real-lot result read as settled without the unchecked conditions: corner coverage (K1), the rear-yard waiver (K4), the area rule (section 6, rule 3) and test H6. | Each now says the result is conditional on the unchecked K20 conditions on a real lot, and settled only in a test that supplies them as checked and absent. |

**The owner's six rules (R255 to R260). They govern every section of this document.**

1. **Facts and legal eligibility come from evidence.** What a user assumes can support only a result
   clearly labelled as conditional on that assumption. It never becomes a verified fact.
2. **Design choices may have visible, editable starting values.** Floor-to-floor height and average
   apartment size are examples. No hidden defaults: nothing is used in a calculation that the result
   does not print.
3. **Conflicting areas.** Establish what each figure measures and which applies. Do not choose one
   automatically. If it is not settled, show defensible conditional results or withhold the affected
   calculations.
4. **Missing information and unfinished features are different.** A promised feature that is not
   built is owed work. Calling it "unsupported" does not finish it.
5. **Reference cases are kept apart from program output.** An AI can help prepare them. Agreement
   between AI answers alone is not proof.
6. **Options are compared on stated criteria.** None is called "best" without saying why.

**How a result may appear.** Three ways, and no other:

| Way | When | How it looks |
|---|---|---|
| settled | every fact behind it comes from evidence, a reference case supports the reading of the law, and every condition that could change it has been checked | the number, its law section, its sources |
| conditional | it rests on an explicit, defensible assumption that is not evidence (a user's statement about the lot; a recorded figure that another figure contradicts; a condition that was not checked and is assumed not to apply) | "If <the assumption>: <the number>", set apart from the settled results, naming the assumption and what would settle it |
| withheld | a known gap affects it and no defensible condition covers the gap | "not known", the reason, what would resolve it, and whether it is missing information or unfinished work |

The remaining-floor-area line keeps its settled wording, "Not confirmed". Every result also carries
the existing label "Tax-lot-only estimate": the program does not verify the zoning lot.

**"Not checked" is never "confirmed" (R267).** A disclaimer, a label or a list of unchecked items
does not turn a result into a settled one. A limit read from the district's table is the district's
limit. It is the property's maximum only when every other rule that could change it has been
checked (R269).

## 1. The milestone

- **What:** row 1 of section 4.1 of the one-district-at-a-time plan (queue row C-08): the server
  computes the results document for one lot and the website shows it. A server switch, off by
  default, keeps it unreachable until it is turned on.
- **On what:** the benchmark lot, 215-16 Northern Boulevard, Queens (BBL 4073340070), on the recorded
  official data already in the repository. No live city call.
- **Reached when:** with the switches on in a test, a browser opens the lot, opens the results, and
  sees exactly what section 5 allows, each result settled, conditional or withheld; every test in
  section 8 passes; a different agent has reviewed each part at its exact commit.
- **What it is not.** It is not the report. Development options beyond the first, estimated floors,
  building shapes, the realistic apartment estimate, option comparisons and the PDF are later
  milestones (the section map, section 3). Everything this milestone withholds stays owed. R6B is not
  finished by it (R206); this milestone is a finished piece, not completion of the whole report
  (R251). Completion of any piece, district or the program is reported only when its agreed
  requirements and tests pass (R278).
- **Scope (R254, R224, R225, R242):** no detailed apartment layouts, no permit-ready plans, no
  building-code design. Where closing a gap would need detailed design, the result is withheld.

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
- This revision was checked against the owner's six rules of section 0 before it was sent for audit.

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
| housing program, floor-to-floor height | design choices. The program is the user's choice of option. The height has a starting value of 10 ft in the engine (`inputs.py:22`, merged), described there as stated and editable. | floor area, units; the building option |
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
13. **The realistic apartment-count estimate does not exist.** The engine computes the legal unit
    limit only. No average apartment size and no shared-space allowance exist in it. It is a later
    milestone (the section map, content G) and is named here so that the legal limit of this
    milestone is never mistaken for it (R253).
14. **Reference cases are not files of their own.** The independent examples of section 9 sit in
    this document. Rule 5 requires them apart from program output, each one followable with the law
    text and a calculator.

## 5. Every known gap, its kind, and how the result appears

Kinds: **owed** = unfinished work the program still has to do (rule 4); **question** = the law text
has to be captured and read before the program may rely on it (owed research); **evidence** = closed
in this plan by reading a recorded fact; **information** = something only this property's evidence
can settle. "Withheld" always means "not known" with the reason and what would resolve it.

| # | Known gap | Kind | How the result appears in this milestone | On the benchmark lot |
|---|---|---|---|---|
| K1 | The corner rule (100 percent coverage) covers the part of a corner lot within 100 ft of each street line, not always the whole lot. The engine applies it to the whole lot. The definition (ZR 12-10) is not captured. | owed; question | 100 percent only when the recorded outline shows the whole lot within 100 ft of each street line and the definition is captured (step P1); on a real lot it is then conditional on the unchecked K20 conditions, like every zoning result, and settled only in a test that supplies them as checked and absent. Otherwise withheld. | withheld: the lot reaches 103.93 ft from the 215 Place street line (a strip about 3.93 ft wide, about 390 sq ft) |
| K2 | The 80 percent for interior and through lots may be changed by ZR 23-363, which is not captured. | question | Withheld until 23-363 is captured and read (step P1). | does not apply (corner lot) |
| K3 | A different maximum applies to lots of 30,000 sq ft or more. | owed | Withheld for lots of 30,000 sq ft or more. | does not apply (10,075 sq ft) |
| K4 | The rear-yard waiver covers only the area within 100 ft of the corner point. The engine takes one yes/no for the whole lot. The ordinary rear yard (ZR 23-342) is not captured. | owed; question | "No rear yard required" for the whole lot only when the whole lot is within 100 ft of the corner point; on a real lot it is then conditional on the unchecked K20 conditions, like every zoning result. Otherwise the rear yard is withheld, and so is everything that needs a footprint: floor plates, building option, floor stack, floor table. | withheld: the far corner is 144.60 ft from the corner point; about 2,560 sq ft of the lot lies beyond 100 ft |
| K5 | Two lot-area figures disagree (10,075 and 10,388 sq ft on this lot). | information | The rule of section 6. Where the figures disagree beyond the stated tolerance, every result that needs the area is conditional, never settled. | conditional: "If the recorded lot area of 10,075 sq ft is confirmed" |
| K6 | The building option is lower than the minimum base height, and no reference case exists for a building option. | owed | Withheld: no building option is shown in this milestone. | withheld |
| K7 | A reason shown to the user says the site "needs professional review". | closed here | Every reason says what is not known, why, and what would resolve it; a test rejects that phrase. | corrected |
| K8 | The setback above the base (ZR 23-433) is captured and not built. | owed | The setback is withheld as "not covered". The envelope drawing and any floor above the base height are withheld. The height limits themselves are table values and are not affected. | withheld |
| K9 | The rules for a commercial overlay are not captured. With an overlay the engine gives the residential number with a note; the floor-area and unit rules do not look at the overlay at all. | question | On a lot with a recorded overlay every residential result is withheld until the governing sections are captured and read independently (step P2). A legal reading is never the subject of a conditional result. | this lot has a recorded C2-2 overlay: **nothing is shown for it until step P2 is done**, and then only what that reading supports |
| K10 | Special district: no source; the floor-area rule ignores it. | evidence | Read from the city-record columns (S16) as a sourced fact. None recorded: stated as "city records list no special purpose district". One recorded: every result is withheld (owed). Not read: every result is withheld; a column that was not read is never taken as "none". | city records list none |
| K11 | Special density area: whether a lot is in one is a fact about the lot. No source exists and the definition (ZR 12-10) is not captured. In such an area the unit formula does not apply. | owed; question | Without evidence the legal unit limit is withheld. If the user states that the lot is not in such an area, the limit may be shown only as a conditional result naming that statement; it is never settled and the statement is never stored as a fact. | withheld; or conditional on the user's statement |
| K12 | "Within 100 ft" and the angle: no source; typed in. | evidence | Computed from the recorded outline and street lines (K1 and K4 use the same measurements). Never typed by a user or a test. No outline: withheld. | measured: angle 89.7 degrees; reaches as in K1 and K4 |
| K13 | The legal unit limit for qualifying housing. | question | Withheld for qualifying affordable housing; for qualifying senior housing "not set by this formula". Test H2 checks both. | withheld |
| K14 | The unit formula does not cover conversions or mixed buildings. | owed | The limit is labelled "new all-residential building". Other cases are withheld. | labelled |
| K15 | Three sections list "R6" and not "R6B" (coverage, units, rear yard). The rule files apply them through the suffix section, ZR 11-25. | closed here | The reference case (section 9, table D) reads the captured text of 11-25 the same way for all three. The result cites both sections. | supported |
| K16 | The definitions of zoning lot and floor area are not captured. | owed | The result is labelled "Tax-lot-only estimate" and never claims the zoning lot. What counts toward floor area is withheld as "not covered"; no gross or net area is shown in this milestone. | labelled; withheld |
| K17 | How height is measured on the lot is not captured. | question | The height limits are shown as the table's limits. Anything that turns height into floors is withheld (K6, K8). | limits shown; floors withheld |
| K18 | A lot split by a district line: a recorded yes/no exists and is not used by the engine. No averaging rule exists. | evidence; owed | Recorded "not split": stated as a fact. Recorded "split": every result is withheld. Not read: every result is withheld. | city records: not split |
| K19 | Other recorded conditions the engine does not use: an inclusionary-housing area, a flood zone, a landmark or historic district. | evidence; owed | Each is read as a fact. Where one is recorded, the results it can change are withheld (floor area for inclusionary housing; heights for flood). A landmark or historic district changes no zoning number; it is shown as a fact beside the results. | read as facts |
| K20 | Conditions with no data source today: waterfront rules, airport height limits, transit easements, a lot close to a district line. Their law text is not captured, so which results each can change is not established. | owed | Decided by the owner (R268). The property facts cannot be changed by them and stay visible. Every zoning result for the lot is treated as one they could change: it is conditional, "If none of these applies to this lot (not checked): ...", and names them. It is never shown as settled and never called the property's maximum. A result that cannot be supported even on that assumption is withheld. Finding a data source for each is owed work; when a condition is checked and absent, its part of the condition is removed. | height limits and floor-area figures: conditional, naming the four conditions |

**What the first screen can show for the benchmark lot.** Until step P2 is done: the sourced facts,
and "not known" with reasons. After it, and only if the reading of step P2 supports the residential
rules under the overlay: the height limits as the district's limits, conditional on the conditions
that were not checked (K20) and never as the property's confirmed maximum; and the floor-area figures
as conditional results ("If the recorded lot area of 10,075 sq ft is confirmed", and on K20).
The legal unit limit appears only as a conditional result, when the user states the density-area
answer. Coverage, rear yard, setback, building option, floors and the envelope drawing are withheld.
That is less than the saved journey result shows today, on purpose, and all of it is owed.

## 6. The rule for conflicting area figures (K5, R257)

1. **What each figure measures.** The recorded lot area is the area the city's property record gives
   for the tax lot. The outline's area is computed from the approximate digital tax-map boundary.
   Neither is a survey, and neither proves the zoning lot.
2. **Which applies.** A floor-area calculation needs the area of the zoning lot. The evidence, best
   first: a survey; an area the user enters from a survey or deed, with that document named; the
   city record. The outline's area is a drawing measure. It is never used in a zoning calculation
   and is never offered as an alternative answer.
3. **No automatic choice.** When the recorded area and the outline's area agree within the stated
   tolerance, the recorded area is used and results that need it stop being conditional on the area; they stay
   conditional on the unchecked K20 conditions, like every zoning result. When they disagree
   beyond it, nothing picks one: every result that needs the area is conditional, "If the recorded
   lot area of N sq ft is confirmed", and says what each figure measures, their difference, and that
   a survey or deed dimensions would settle it. The two figures are not offered as a low and a high.
4. **The tolerance is stated, per check.** It is written into the result and set when the part is
   contracted, from the recorded lots. It hides nothing: both figures are always in the details.
5. **No mixing.** A figure is never built from a dimension of one source and a dimension of the
   other. The engine's rectangle (S18) is labelled "simplified shape" and is never used to answer a
   shape question; shape questions use the recorded outline, marked approximate.
6. **No stand-in.** With no recorded or better lot area, every result that needs the area is
   withheld. The outline's area is not used in its place.

## 7. Settled points and open points

**Settled by the owner's decisions. No question for the owner.**

- No professional sign-off gate (R164, R165; ADR-007, waiting as #432). The "golden record" block on
  this piece in the older documents is replaced by: one standing label, the law section for each
  number, and "not known" when the program is not sure. Nothing is called verified or compliant.
- The order: results, then report, then PDF (R213). One piece at a time (R250).
- **Facts and eligibility (rule 1).** No fact about the lot is filled by a default or a guess, on the
  server or on the website, and the user is never made to answer. A request with unanswered facts
  is a normal request: the results that depend on them are withheld and name them; the others are
  unchanged. What the user states about the lot is used only for conditional results.
- **Design choices (rule 2).** The floor-to-floor height keeps a starting value. It is shown, it is
  editable, and it is printed with every result that uses it. The engine's present 10 ft value
  (`inputs.py:22`, merged) is such a starting value only once the screen shows it; Part 0 makes sure
  no result uses it unseen. The starting values themselves are the owner's to approve (the section
  map, choice 4). The housing program is the user's choice of option, not a default.
- **A saved result proves nothing (R241).** See section 8, rule 3.

**Open. The orchestrator decides at contract time; the recommendation is given.**

| # | Question | Recommendation | Other choice |
|---|---|---|---|
| D1 | Which switch | a new off-by-default `INTERNAL_RESULTS_ENABLED`. Needs S11's list and its pinned test updated. | reuse existing switches |
| D3 | Shape of the request | `POST /api/v1/properties/{bbl}/results` with a small checked body (the user's option, the design choices, and anything the user chose to state), like the existing `POST /api/v1/max-envelope` | `GET` with the values in the address |
| D4 | Where the website shows it | a new dashboard tool behind its own off-by-default website switch (pattern W5) | a separate page |
| D5 | How one value says "settled", "conditional" or "withheld" in the contract (missing item 4) | a new contract version in which a value carries one of the three ways of section 0 | separate answers for each |

**Open, the owner's:** the scope choices of the section map (section 4 there). The owner has
settled how unchecked conditions are treated (R268; gap K20). None of the open choices is needed to
start step R0, P1 or P2. Turning any switch on in production stays the owner's and is not asked now.

## 8. Files that would change, and how success will be tested

Steps in order, one at a time. Each: one writer, then a different agent's review at the exact
commit, then merge. Paths were checked at the named commits; names of new files are proposals.

**Three rules for every test below.**

1. Each test is marked. **[LAW]**: the expected value is taken from a reference case (step R0), which
   was worked out from the law text without reading the program's answer. **[WIRING]**: it proves the
   parts are connected and the data is carried unchanged. **[UNCHANGED]**: it compares with a saved
   earlier result and proves only that nothing moved.
2. A result is settled because of a reference case and evidence, or it is not settled. Every result
   that section 5 withholds has a test that it reads "not known"; every conditional result has a test
   that it is labelled and names its assumption.
3. **Matching a saved result is never proof.** No [UNCHANGED] or [WIRING] test is counted as evidence
   that a value is right, and a saved result is never the reason a value appears on the screen. When
   the engine changes, the saved result is regenerated and its differences are reviewed line by line
   against section 5.

### Step R0: the reference cases as files of their own (rule 5)

- **Files:** new, under `docs/reference-cases/R6B/`: one file per case of section 9 (the real lot;
  the made-up interior lots; the corner-lot shapes; the suffix question). Each holds the facts and
  where they come from, the law text relied on with its capture, why that rule applies, the
  arithmetic, the expected values, who prepared it and how it was checked, and a change log.
- **Rules:** nothing in these files is copied from a program run. An expected value changes only
  with a recorded reason: corrected evidence, a corrected reading, or a change in the law. A
  disagreement between a case and the program is investigated on both sides.
- **What a case is worth.** These cases were prepared by an AI helper and checked by a second AI.
  That agreement alone is not proof (rule 5). Each case is written so a person can follow it with
  the law text and a calculator, and says what it does not establish.
- **Tests:** a check that every [LAW] test names a case file and uses its values.

### Step P1 and step P2: capture the missing law text, then read it independently

- **Files:** new capture files under `docs/research/zr-snapshots/v1/` and their synced copy, made
  with the existing capture tool. Source text only; no rule and no reading inside the capture.
  P1: ZR 12-10 (lot definitions, lot area, special density area), 23-342, 23-363.
  P2: the Article III sections named in missing item 7.
- **Then, before any rule or gate changes:** new reference cases are worked from the new text, as in
  step R0. Their answers set the expected values for the steps below.
- **Tests:** the existing capture checks (the text matches its recorded digest). No number is shown
  because of a capture alone.

### Part 0: make the result honest (server engine and contract)

| | Path | Note |
|---|---|---|
| edit | `services/api/app/scenario/three_answers/inputs.py`, `engine.py`, `answers.py`, `building_option.py`, `geometry.py`, `rule_access.py` | facts may be "not given"; the three ways of section 0; the outcomes of section 5; the area rule; reasons without the phrase of K7; no value used unseen |
| edit | `services/api/app/scenario/three_answers/scope.py`, `explanations.py`; `services/api/app/contracts/engine_disclosures.py` | exist only in the waiting changes (#439, #440) |
| edit | `services/api/app/contracts/evaluator_inputs.py`; `services/api/app/api/v1/study_inputs.py` | carry the recorded conditions (K10, K18, K19) and the reach measurements as sourced facts; carry "unknown" facts through; keep a user's statement apart from the facts |
| new | `services/api/app/spatial/lot_reach.py` and its test | from the recorded outline and street lines: the angle of the street lines, the farthest reach from each street line and from the corner point |
| edit | `packages/contracts/schemas/v1/results.schema.json`, its fixtures, `packages/contracts/generated`, `services/api/app/_contract_schemas`, `apps/web/src/lib/contract.ts` | shared files; a value is settled, conditional or withheld (D5) |
| edit | `apps/web/src/lib/architect/three-answers.ts`, `src/components/architect/answers/AnswerCard.tsx` and their tests | show a conditional result apart and labelled; show a withheld value with its reason |
| new | `services/api/tests/scenario/three_answers/test_three_answers_law_examples.py`, `test_three_answers_not_known.py`, `test_three_answers_area_rule.py`, `test_three_answers_conditional.py` | tests H1 to H10 |
| edit | tests that pin today's numbers: `tests/scenario/three_answers/test_three_answers_benchmark.py`; `tests/journey/test_215_16_northern_journey.py` and its saved result; the saved drawings under `tests/cad/snapshots/results_dxf/` and the drawing tests that read results fixtures; the website tests W1 and W8 | found in full with the code-graph impact query when the part is contracted; each change is reviewed against section 5 |

| # | Kind | Test |
|---|---|---|
| H1 | LAW | The benchmark lot through the engine on recorded facts, **only if step P2's reading supports it** (otherwise each reads "not known" and the test asserts that): the height limits (L3, L4) appear as the district's limits, conditional on the unchecked conditions of K20 and naming them, and never as settled or as the property's maximum; the floor-area figures (L1, L2) appear only as conditional results that name the recorded-area condition and the K20 conditions. |
| H2 | LAW | The benchmark lot: coverage is withheld and its reason carries the measured reach (103.93 ft from the 215 Place street line); the rear yard is withheld beyond the corner area (144.60 ft); building option, floor plates, floor stack and floor table are withheld; the setback reads "not covered"; **the legal unit limits for qualifying affordable and qualifying senior housing read "not known"** (K13). Never a zero. |
| H3 | LAW | Three made-up corner lots with outlines (table C), each supplied with the K20 conditions as checked and absent: 40 x 100 ft gives coverage 100 percent and rear yard withheld; 60 x 80 ft gives coverage 100 percent and no rear yard required anywhere; 150 x 100 ft gives coverage withheld and rear yard withheld. With the K20 conditions not checked, the same values are conditional. |
| H4 | LAW | The made-up interior lots of table B, each with one lot-area figure: floor area as in the table, settled when the K20 conditions are supplied as checked and absent, conditional when they are not checked; the legal unit limit withheld with no density-area evidence, and conditional, with the table's value, when the user states it; coverage withheld until step P1's reading of 23-363 is in, then the value that reading supports. |
| H5 | LAW and WIRING | Facts not given, one at a time: the special-district column not read; no outline; no lot area; the split-lot record not read. Each time the results that depend on it are withheld and name it, and every other result is unchanged. A recorded special district, or a recorded split lot, withholds every result. |
| H6 | LAW and WIRING | The area rule: with figures that agree within the tolerance, one governing figure and results that are settled only when the K20 conditions are also supplied as checked and absent (as in H4), and conditional otherwise; with figures that disagree, conditional results only, both figures and what each measures in the result, and no automatic choice; with no recorded area, withheld; no calculation reads the outline's area; no figure mixes the two sources. |
| H7 | WIRING | No reason text contains "professional review"; every withheld result has a reason, a kind, and what would resolve it. |
| H8 | UNCHANGED | The regenerated saved journey result equals the engine's output. It proves nothing about correctness (rule 3). |
| H9 | LAW and WIRING | A user's statement about the lot (the density-area answer) produces only a conditional result that names the statement; the statement is absent from the sourced facts and from the saved facts; without it the result is withheld again; a statement that contradicts a recorded fact is refused as a conflict. |
| H11 | LAW and WIRING | Not checked is not confirmed (R267 to R269). With the K20 conditions not checked: no zoning result is settled; each is conditional and names the conditions; the height limits are labelled the district's limits and nowhere "the maximum for this property"; the facts stay visible. With one of them recorded as present: the results it can change are withheld. With all of them supplied as checked and absent: the height limits become settled. A disclaimer or label alone never changes a result's way of appearing. |
| H10 | WIRING | No hidden default: every value used in a calculation is printed in the result with its kind (fact, design choice, user's statement); changing the floor-to-floor starting value changes what depends on it and nothing else; a search of the engine finds no constant used in a result that the result does not print. |

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
| T4 | LAW | The recorded lot through the route: the same expectations as H1, H2 and H11, conditional and withheld alike; no height limit is returned as settled. |
| T5 | LAW | The made-up lots of tables B and C through the same chain: the same expectations as H3 and H4. |
| T6 | LAW | A changed input changes every result that depends on it and nothing else: the lot area 5,355 sq ft gives the floor area of row P5 and, with the user's density statement, its conditional unit limit; a changed floor-to-floor height changes no law limit. |
| T7 | LAW and WIRING | A request with facts not given is answered normally (a 200): the dependent results are withheld and name the fact; the others are shown. No zero appears anywhere. |
| T8 | WIRING | Conflicting evidence stays visible: a caller who states something that contradicts a recorded fact does not override it; the answer names both, and the results that depend on it are withheld. |
| T9 | WIRING | Too many calls: a typed 429 before any other work. |
| T10 | WIRING | Example values in a real-property request are refused (S13). |
| T11 | WIRING | Nothing changes in production: the new switch defaults to off, and the change does not touch `render.yaml`. |

### Part B: the website

| | Path | Note |
|---|---|---|
| new | `apps/web/src/lib/results-api.ts` and its test | typed client, same outcome kinds as W4 |
| new | `apps/web/src/lib/architect/results-flag.ts` and its test | the website switch, read on the server, default off |
| new | `apps/web/src/components/architect/ResultsPanel.tsx` and its test | shows the design choices with their starting values, lets the user change them or state something about the lot, fetches, shows loading / withheld / error, then renders the existing panel W1 |
| new | `apps/web/e2e/results.flag-on.spec.ts`, `apps/web/e2e/results.spec.ts` | the journey with the switch on, and the plain "not available" view with it off |
| edit | `apps/web/e2e/harness/fixture_api.py` | a recorded answer for the route, taken from the regenerated saved result of Part 0 |
| edit | `apps/web/src/components/architect/workspace/DashboardTools.tsx`, `workspace/types.ts`, and the entry files that pass switches down (`workspace/DashboardEntry.tsx`, `ArchitectEntry.tsx`, `src/app/property/page.tsx`) | the new tool |

| # | Kind | Test |
|---|---|---|
| W-1 | WIRING | The client maps each server answer to its outcome. |
| W-2 | WIRING | **Numbers agree:** every settled value, every conditional result with its condition, and every "not known" on the cards equals the document the server returned (walk every value; nothing is retyped in the component). |
| W-3 | WIRING | States: loading; switch off (the plain "not available" view, and no call is made); a fact not given (its results are withheld, the rest are shown, no fact is prefilled); each design choice visible with its starting value and editable; server error. |
| W-4 | WIRING | The standing label is on the screen once. |
| W-5 | LAW | The browser journey on recorded data: open the lot, open the results. The height limits appear as the district's limits with the values of table A, conditional, naming the conditions that were not checked, and nowhere called the maximum for the property. The floor-area figures appear as conditional results naming the recorded-area condition. Coverage, rear yard and building option read "not known". Stating the density-area answer makes the unit limit of row L6 appear as a conditional result naming that statement, never as a settled number. Expected values come from the reference cases, not from the recorded answer. |
| W-6 | WIRING | Keyboard and screen-reader checks, as the existing suite does for each tool. |

**Not touched by any step:** the rule tables' values, `render.yaml`, any production setting, the CI
configuration, the dependency files.

### Runs and agreement

- Before each step's pull request: the full server suite alone; then the website's lint, type check,
  unit tests, build and browser journeys, one at a time (R211). A run with one failing test is not
  green (R212).
- **Numbers, drawings and PDF agree (R228).** Every output reads the one results document. This
  milestone checks the website against it (W-2). The drawings read the same document; where a result
  is withheld the drawing leaves it out and says so. The PDF does not exist; its milestone must add
  the same check. The area figures are shown everywhere by the rule of section 6.

## 9. Independent reference cases

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
Tables C and D come from a follow-up to the same helper under the same rules.

**What they are worth (rule 5).** The helper is an AI, and so is the auditor that recomputed them.
Their agreement alone is not proof. Each row gives the law text and the arithmetic so that a person
can follow it with the source and a calculator. This is a draft reading, not professionally
reviewed, and not a statement that anything complies. Most sections were read from the same captures
the rules were written from, so an error in a capture would be shared; the live-page check covers
four sections. The corner-lot definition used in tables A and C was read on the official site and is
not yet captured (step P1). It is one lot. Step R0 moves these tables into files of their own.

### Table A: the real lot (R6B; a C2-2 overlay is recorded; lot area 10,075 sq ft from city records)

"First screen" is what section 5 allows once steps P1 and P2 are done. Every zoning entry in that
column waits for K9 (if the reading of step P2 does not support it, it reads "not known") and is
conditional on the unchecked conditions of K20.

| # | Quantity | Law relied on | Independent value | Program today | First screen |
|---|---|---|---|---|---|
| L1 | Maximum residential floor area, standard | ZR 23-22, R6B row: 2.00; 2.00 x 10,075 | 20,150 sq ft | 20,150 | conditional: "If the recorded lot area of 10,075 sq ft is confirmed" (K5) |
| L2 | The same, qualifying affordable or senior housing | ZR 23-22, R6B row: 2.40; 2.40 x 10,075 | 24,180 sq ft | 24,180 | conditional on the same (K5), as a labelled alternative |
| L3 | Heights, standard | ZR 23-432, R6B row | base 30 to 45 ft; building 55 ft | 30 / 45 / 55 | conditional: the district's limits; the property's maximum only if no other height rule applies (K20, not checked). Never shown as the confirmed maximum. |
| L4 | Heights, qualifying housing | ZR 23-432, R6B row | base 30 to 45 ft; building 65 ft | 30 / 45 / 65 | conditional in the same way, as a labelled alternative |
| L5 | Maximum lot coverage | ZR 23-362(a): corner 100 percent, interior and through 80 percent; the corner part is the part within 100 ft of each street line (official page) | 100 percent on the corner part; the strip beyond is not a corner lot; no single figure for the whole lot | 100 for the whole lot | **not known** (K1) |
| L6 | Maximum dwelling units, standard | ZR 23-52(b): factor 680; a fraction of three-quarters or more counts as one; 20,150 / 680 = 29.63 | 29 | 29 | withheld with no density-area evidence (K11); when the user states it, conditional on that statement and on the recorded area (K5), never settled |
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
| P1 | 5,000 sq ft | 10,000 | 14.706 | 14 | 10,000 / 14 | floor area conditional on K20, settled only in a test that supplies those conditions as checked; unit limit withheld, or conditional on the user's density statement |
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
area, heights, the legal unit limit, and the coverage percentage of the corner rule. **That does not
make every number fit to show.** The program also gives a number in three cases where the independent
reading says the text does not settle it for the whole lot: coverage (K1), the rear yard (K4) and the
full-lot floor plate (K4, K6). The floor-area figures rest on a lot area that another figure
contradicts (K5). And every number on this lot waits for the overlay reading (K9).

## 10. What must be on the screen (R229, R240, R255, R258)

| Case | The screen shows |
|---|---|
| a fact was not read, or the user left it unanswered | the results that depend on it read "not known", name it and say what would resolve it; the rest are shown; no fact is prefilled; never 0 |
| the user states something about the lot | results that depend on it appear only as conditional, "If <the statement>", apart from the settled results; the statement is not listed among the facts |
| two area figures disagree | conditional results on the recorded figure; both figures, what each measures, and what would settle it |
| a design choice | its starting value, visible and editable, printed with every result that uses it |
| a condition the program did not check | the results it could change are conditional and name it; none is called confirmed or the maximum for the property; the facts stay visible |
| a result section 5 withholds | "not known" or "not covered", the reason, and whether it is missing information or work still owed |
| remaining floor area | "Not confirmed" (the settled wording) |
| the user contradicts a recorded fact | both; no result computed from the statement |
| the server cannot reach its data | "could not be loaded"; nothing made up |

## 11. Order and what must be true first

1. On 2026-10-07 at 14:09 UTC or later: the dependency fix, by the normal reviewed path, started by
   hand. It is not done and not verified today.
2. The waiting changes, one at a time, each on a fresh green run after the fix.
3. Step R0 (the reference cases as files), then step P1, then step P2.
4. Part 0, then Part A, then Part B. Each is contracted as a ledger task (citing R166, R167, R213,
   R221 to R229, R235 to R242, R248 to R265 and R266 to R273), written by one producer on a branch from the
   then-current integration branch, reviewed by a different agent at the exact commit, and merged
   before the next starts. That is milestone 1.
5. Then the later milestones of the section map, each with a work order of its own, in an order the
   orchestrator proposes and the owner can change: the gaps that withhold floors and shapes (K1, K4,
   K6, K8); the development options; the realistic apartment-count estimate; the option comparison;
   the report builder; the PDF. The program is not reported complete before all of them are.
6. No production switch changes. No timer of any kind. No merge on a red or stale check (R263).

## 12. Lines in existing documents that are out of date

| Where (merged) | What it says | What is true |
|---|---|---|
| `docs/lanes/queues/C.md:16` | "flip the tests that assert it stays unmounted" | no such test exists |
| `docs/lanes/queues/C.md:16`; `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` (links 5, 6) | this piece is blocked on the owner's "golden record" and reviewer | replaced by R164, R165 and ADR-007 (waiting as #432) |
| `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md:121` (link 4) | the adapter still fails closed on the facts read | the bridge S6 is merged |
| `docs/plans/district-checklists/R6B.md` (waiting as #441), "R6B is complete when" | a row may be "deliberately recorded as unsupported" and count | a promised feature that is not built is owed work (R258); the sentence is corrected after that change merges |
| the results contract field `best_combination` and the add-on wording "Best combination" (waiting as #439) | an option is called best | allowed only with the criterion and the reason stated (R260); settled when the options milestone is built |

## 13. What this document does not establish

- It builds nothing and proves nothing works in a browser. The website was not run.
- The combined tree used for the made-up-lot runs is local and was never pushed.
- Whether the residential rules hold under the commercial overlay is not known. Step P2 decides it;
  this document does not.
- The files listed for Part 0 are the ones known today. The full list of tests that pin today's
  numbers is found when the part is contracted.
- The open scope choices of the section map are the owner's and are not decided here. No section of
  the sample and no option is dropped by this document (R272).
- This milestone is not the report. R6B is not finished, the dependency fix is not in, and the
  program is not complete.
