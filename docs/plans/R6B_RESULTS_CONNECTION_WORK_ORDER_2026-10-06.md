# Work order: the first R6B results connection

Written 2026-10-06 by the orchestrator while nothing can merge (blocker B-029, a security advisory).
Asked for by the owner (D-090 source-032: R221, R222 the four lists; R223 no building on unmerged
work; R224, R225 the scope; R226, R227 independent law-based examples; R228, R229 agreement and
unknowns).

**This is a work order, not a task and not a result.** Writing it changed no product file. Nothing
described here is built. Building starts only after the waiting changes are merged.

## 1. The piece

- **What:** row 1 of section 4.1 of the one-district-at-a-time plan (queue row C-08): the server
  computes the results document for one lot and the website shows it. A server switch, off by
  default, keeps it unreachable until it is turned on.
- **On what:** the benchmark lot, 215-16 Northern Boulevard, Queens (BBL 4073340070), on the recorded
  official data already in the repository. No live city call.
- **Finished means, for this piece only:** with the switches on in a test, a browser opens the lot,
  opens the results, and sees the same numbers the server computed, under the standing label; every
  test in section 7 passes; a different agent has reviewed each of the two parts at its exact commit.
- **Not this piece:** the one shared, saved result every output reads (plan row 2), the number checks
  (row 3), drawings from the result (row 4), a link to the law for every number (row 5), the PDF
  (rows 6 to 8), and the rest of the R6B rules (row 9). This piece does not finish R6B (R206).
- **Scope (R224, R225):** simplified zoning feasibility: how much can be developed, about how much
  fits, simple building shapes, later a clear PDF. No detailed apartment layouts, no permit-ready
  plans, no building-code design. Nothing below needs any of the three.

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
  (no route calls the engine; no page shows the panel; the pinned switch list; the journey test's
  typed-in values) and a script resolved every reference at the named commits.
- No test was run to write sections 3 to 7. The only runs are the engine probes in section 8.

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
| S10 | One test that runs the whole chain on recorded data: BBL, facts read, bridge, inputs, engine, site-plan drawing, AutoCAD file, saved fixture | `tests/journey/test_215_16_northern_journey.py:120`; fixture `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` | waiting, #440 | itself |
| S11 | The closed list of switches the server reports, pinned by a test | `app/api/v1/build_info.py:56`; `tests/api/test_build_info_api.py:33` | merged | that test |
| S12 | A test pattern for switch-gated read routes (off = a plain 404 identical to a path that does not exist; absent from the public route list) | `tests/api/test_read_router_mounts.py:137` | merged | itself |
| S13 | A guard that refuses example values in a real-property request | `app/api/v1/real_property_guard.py` | merged | its tests |
| W1 | The results panel. Display only: it takes one results document, fetches nothing, and **no page renders it** (only tests do). | `src/components/architect/answers/ThreeAnswersPanel.tsx:39` | merged | `src/components/architect/answers/__tests__/three-answers-panel.test.tsx` |
| W2 | Numbers from unreviewed rules are hidden unless the surface asks for them; the card then says "Not available" with the reason | `src/lib/architect/three-answers.ts:195` | merged | same |
| W3 | Each number prints the name of its law section as text (for example "ZR 23-22"). It is not a link. | `src/components/architect/answers/AnswerCard.tsx:66` | merged | same |
| W4 | Typed server clients to copy the pattern from (timeouts, typed outcomes for 404 / 422 / 503 / 500 / network) | `src/lib/study/study-setup-api.ts:269`; `src/lib/parity-api.ts:347` | merged | their tests |
| W5 | The dashboard's tool switch. Each newer tool sits behind its own server-read, off-by-default switch and shows a plain "not available" view when off. | `src/components/architect/workspace/DashboardTools.tsx:91`; labels `workspace/types.ts:5`; switch reader pattern `src/lib/architect/proposal-editor-flag.ts:19`; `src/app/property/page.tsx:50` | merged | workspace tests |
| W6 | Browser journeys that replace server routes with recorded answers | `e2e/harness/fixture_api.py`; pattern `e2e/parity.flag-on.spec.ts` | merged | the journeys |
| W7 | The standing label ("computed from official sources, not professionally reviewed") | `src/components/architect/StandingReviewLabel.tsx` | waiting, #433 | its tests |
| W8 | A website test that loads the saved journey fixture and renders it through the panel; every expected string is read from the document | `src/components/architect/answers/__tests__/journey-215-16-northern.test.tsx` | waiting, #440 | itself |

### Where each engine input comes from today

| Input | Source today |
|---|---|
| zoning district, lot area, lot type | sourced facts (city records; lot type from the approximate tax-map outline) |
| lot front, lot depth, lot outline | sourced where present; on a corner lot the front is the address street, shown as an assumption (#440) |
| commercial overlay present | sent by the caller, and refused if it contradicts the recorded overlay fact |
| housing program | the caller's choice; "standard residence" is shown as a default |
| floor-to-floor height | a stated default of 10 ft that the user may change |
| special district present | **no source.** Typed into the journey test as "no". Printed as "assumed; this run does not read the special-district layer" (`engine_disclosures.py:327`, #440). |
| special density area | **no source.** Typed in as "no". Printed as assumed. |
| within 100 ft of a street-line intersection | **no source.** Typed in as "yes". Printed as assumed. |
| angle of the street lines | **no source.** Typed in as 90. Printed as assumed. |
| result id, time computed | typed into the test |

The four "no source" inputs, the overlay and the program are required yes/no or number fields
(`inputs.py:89` to `:94`, merged). **The engine cannot be told "not known" for any of them.**

## 4. What is missing

1. **The route.** No server route calls the engine. A search of `services/api/app` finds
   `generate_results` only inside the engine's own folder, and `app/api/v1/` has no results file.
2. **The request.** Nothing defines what the caller sends (the option and the stated assumptions) and
   what the server must read itself and never accept from a caller (lot area, frontage, depth, lot
   type, district, overlay).
3. **Four inputs with no source, and no way to say "not known".** See the table above. For a real lot
   somebody has to state them, or the answers that depend on them have to say "not known". The engine
   supports neither a source nor "not known" today.
4. **Typed answers for refusals.** Nothing turns the builders' refusals (`EvaluatorInputsError`,
   `EngineDisclosureError`) into a typed server answer the website can show.
5. **Result identity.** The result id and the time are typed into the test. A route has to set them.
6. **The website.** No results client. No page or dashboard tool shows the panel. No loading, error,
   "input needed" or "not known" state for a results fetch. Numbers from unreviewed rules stay hidden
   unless the surface asks for them (W2), so today the panel would show "Not available" on every card.
7. **A browser journey** for the results, and a recorded answer for the route in the journey harness.
8. **Two things the queue row assumes that do not exist.** `docs/lanes/queues/C.md:16` says "flip the
   tests that assert it stays unmounted": no such test exists (S12 pins three other routes only).
   It also names an owner block on a "golden record"; see section 5.

## 5. Settled points and open points

**Settled by the owner's decisions. No question for the owner.**

- No professional sign-off gate (R164, R165; ADR-007, waiting as #432). The "golden record" block on
  this piece in the older documents (`docs/lanes/queues/C.md:16`,
  `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md`) is replaced by: one standing label, the law
  section for each number, and "not known" when the program is not sure. Nothing is called verified
  or compliant. This piece therefore waits for #432 and #433 to merge.
- The order: results, then report, then PDF (R213).
- The scope (R210, R224, R225).

**Open. The orchestrator decides at contract time; the recommendation is given.**

| # | Question | Recommendation | Other choice |
|---|---|---|---|
| D1 | Which switch | a new off-by-default `INTERNAL_RESULTS_ENABLED`, beside the existing engine switch. Needs S11's list and its pinned test updated. | reuse existing switches: no list change, but results and other internal tools could not be turned on separately |
| D2 | The four inputs with no source | **The server never fills them in.** The caller states each one; each is printed on the result as an entered assumption. If one is missing the server answers "input needed" and names it; it returns no numbers. | a silent default on the server or the website: rejected, it is a guess |
| D3 | Shape of the request | `POST /api/v1/properties/{bbl}/results` with a small checked body (the option and the stated assumptions), like the existing `POST /api/v1/max-envelope` | `GET` with the values in the address |
| D4 | Where the website shows it | a new dashboard tool beside the existing ones, behind its own off-by-default website switch (pattern W5) | a separate page |

D2 leaves one honest gap: a user who does not know an answer cannot say so, because the engine has no
"not known" input. Closing it is a small engine change of its own, to be listed as the next piece.
It is not hidden inside this one.

**Needs the owner, unchanged, not asked now:** turning any switch on in production.

## 6. Files that would change

Two parts, one after the other. Each: one writer, then a different agent's review at the exact
commit, then merge.

### Part A: the server route

| | Path | Note |
|---|---|---|
| new | `services/api/app/api/v1/results_read.py` | the route: switch check, rate limit, BBL check, then the existing chain S4 to S1, contract check, answer |
| new | `services/api/app/api/v1/results_request.py` | reads and checks the caller's body; builds the "input needed" and conflict answers. Kept apart so the route file stays small. |
| new | `packages/contracts/schemas/v1/results_request.schema.json` and one valid and one invalid fixture | shared file area; only if D3 is a body |
| new | `services/api/tests/api/test_results_read_api.py` | tests T1 to T3, T7 to T11 |
| new | `services/api/tests/api/test_results_read_law_examples.py` | tests T4 to T6, expected values from section 8 |
| edit | `services/api/app/main.py` | mount the route (shared file) |
| edit | `services/api/app/config.py` | the new switch, default off (shared file) |
| edit | `services/api/app/api/v1/build_info.py` | add the switch to the reported list (S11) |
| edit | `services/api/tests/api/test_build_info_api.py` | its pinned list changes (`:33`) |
| edit | `docs/lanes/queues/C.md`, `docs/lanes/status/C.md`, `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` | the stale lines in section 11 |

### Part B: the website

| | Path | Note |
|---|---|---|
| new | `apps/web/src/lib/results-api.ts` and its test | typed client, same outcome kinds as W4 plus "input needed" |
| new | `apps/web/src/lib/architect/results-flag.ts` and its test | the website switch, read on the server, default off |
| new | `apps/web/src/components/architect/ResultsPanel.tsx` and its test | asks for the stated inputs, fetches, shows loading / input needed / not known / error, then renders the existing panel W1 with numbers shown |
| new | `apps/web/e2e/results.flag-on.spec.ts`, `apps/web/e2e/results.spec.ts` | the journey with the switch on, and the plain "not available" view with it off |
| edit | `apps/web/e2e/harness/fixture_api.py` | a recorded answer for the route |
| edit | `apps/web/src/components/architect/workspace/DashboardTools.tsx`, `workspace/types.ts`, and the entry files that pass switches down (`workspace/DashboardEntry.tsx`, `ArchitectEntry.tsx`, `src/app/property/page.tsx`) | the new tool |

**Not touched by either part:** the rule files, the engine, the results contract, `render.yaml`, any
production setting, the CI configuration, the dependency files.

## 7. How success will be tested

Each test is marked. **[LAW]**: the expected value is typed from the hand calculation in section 8,
with its section, and is not read from a program run or a saved fixture. **[WIRING]**: it proves the
parts are connected and the data is carried unchanged. A [WIRING] test repeats the program's own
answer and proves nothing about whether the law was read correctly.

### Part A

| # | Kind | Test |
|---|---|---|
| T1 | WIRING | Switch unset, or set to anything but a true word: a plain 404, byte-identical to a path that does not exist, and the route is absent from the public route list. |
| T2 | WIRING | A malformed BBL: a typed 422, and the data source is never called. |
| T3 | WIRING | The recorded lot with the switches on: a 200 whose body passes the results contract and equals the saved journey fixture except for the id and time fields. |
| T4 | LAW | The same answer, checked value by value against table A of section 8 (L1 to L6, L9, L10). |
| T5 | LAW | The five made-up lots of table B through the same chain: floor area, coverage and unit count equal the table, including the rounding edge (15.735 gives 15; 15.75 and 15.765 give 16). |
| T6 | LAW | A changed input changes every number that depends on it: the same lot with area 5,355 sq ft and lot type "interior" gives table B row P5 in full; a changed floor-to-floor height changes the floor stack and leaves the law limits alone. |
| T7 | LAW and WIRING | Missing information never becomes a number: a caller who omits one of the four stated inputs gets "input needed" naming it and no numbers; a lot whose area is not known gets a typed "not available" answer; the qualifying-housing unit count stays "not available" with its reason; "remaining floor area" stays "Not confirmed". No zero appears in any of them. |
| T8 | WIRING | Conflicting evidence stays visible: a caller who states "no overlay" for a lot whose record carries one gets a typed conflict answer naming both; no numbers. |
| T9 | WIRING | Too many calls: a typed 429 before any other work. |
| T10 | WIRING | Example values in a real-property request are refused (S13). |
| T11 | WIRING | Nothing changes in production: the new switch defaults to off, and the change does not touch `render.yaml`. |

### Part B

| # | Kind | Test |
|---|---|---|
| W-1 | WIRING | The client maps each server answer to its outcome, including "input needed". |
| W-2 | WIRING | **Numbers agree:** every value on the cards equals the value in the document the server returned (walk every value; no number is retyped in the component). W8 already does this for the saved fixture; this test does it for the fetched document. |
| W-3 | WIRING | States: loading; switch off (the plain "not available" view, and no call is made); input needed; a card whose answer is not available shows the reason, never a zero; server error. |
| W-4 | WIRING | The standing label is on the screen once. |
| W-5 | LAW and WIRING | The browser journey on recorded data: open the lot, open the results, read the values of table A; change one stated input and see the dependent numbers change. The recorded answer in the harness is the saved journey fixture, so it can only contain what the real server can produce. |
| W-6 | WIRING | Keyboard and screen-reader checks, as the existing suite does for each tool. |

### Runs and agreement

- Before each part's pull request: the full server suite alone; then the website's lint, type check,
  unit tests, build and browser journeys, one at a time (R211). A run with one failing test is not
  green (R212).
- **Numbers, drawings and PDF agree (R228).** Today the journey test S10 draws the site plan and the
  AutoCAD file from the same document and compares their labels. This piece adds the website (W-2).
  The PDF does not exist; its piece must add the same check: every number in the PDF is read from the
  same result, at the same revision, as the website and the drawings. Finding F3 below is a
  disagreement this check must show, not hide.

## 8. Independent, law-based examples

**How they were made.** A helper that had no part in writing the rules was given a sealed folder: the
20 pinned law-text captures (without the notes that describe how the program encoded them) and the
recorded official facts for the lot (without any floor-area-ratio field). It was told not to open the
repository and reported that it did not. It worked the numbers by hand and also read the live official
pages for the rows it relied on (2026-10-06): ZR 23-22, 23-432, 23-362 and 23-52 matched the captures.
The orchestrator re-read 23-22 ("R6B 2.00 2.40") and 23-52 ("680"; "Fractions equal to or greater
than three-quarters") on the official site the same day. **Only afterwards** were the results set
beside the program's answers: the saved journey fixture at #440 for the lot, and the engine run on
the made-up lots on the local combined tree.

**Limits.** This is a draft reading, not professionally reviewed, and not a statement that anything
complies. Most sections were read from the same captures the rules were written from, so an error in
a capture would be shared; the live-page check covers four sections. It is one lot.

### Table A: the real lot (R6B; a C2-2 overlay is recorded; lot area 10,075 sq ft from city records)

| # | Quantity | Law relied on | Hand calculation | Independent value | Program today | Result |
|---|---|---|---|---|---|---|
| L1 | Maximum residential floor area, standard | ZR 23-22, R6B row: 2.00 | 2.00 x 10,075 | 20,150 sq ft | 20,150 | agrees |
| L2 | The same, qualifying affordable or senior housing | ZR 23-22, R6B row: 2.40 | 2.40 x 10,075 | 24,180 sq ft | 24,180 | agrees |
| L3 | Heights, standard | ZR 23-432, R6B row | read from the table | base 30 to 45 ft; building 55 ft | 30 / 45 / 55 | agrees |
| L4 | Heights, qualifying housing | ZR 23-432, R6B row | read from the table | base 30 to 45 ft; building 65 ft | 30 / 45 / 65 | agrees |
| L5 | Maximum lot coverage, corner lot | ZR 23-362(a): corner 100 percent, interior and through 80 percent | lot type from L9 | 100 percent | 100 | agrees; see F1 |
| L6 | Maximum dwelling units, standard | ZR 23-52(b): factor 680; a fraction of three-quarters or more counts as one | 20,150 / 680 = 29.63 | 29 | 29 | agrees |
| L7 | Dwelling units, qualifying affordable | same | 24,180 / 680 = 35.56 | 35 | "not available" | the program gives no number; a gap, not an error |
| L8 | Dwelling units, qualifying senior | ZR 23-52(a)(2): no factor applies | none | not set by this formula | "not available" | consistent |
| L9 | Lot type | geometry: two street frontages meeting at 89.7 degrees; the definition of a corner lot was read on the official page, it is not captured | measured from the recorded outline and street lines | corner | corner | agrees |
| L10 | Frontages | recorded outline | edge lengths | Northern Boulevard 103.9 ft; 215 Place 100.0 ft | front 103.88 | agrees |
| L11 | Street widths | ZR 12-10: 75 ft or more is wide | recorded mapped widths 100 and 60 | Northern wide, 215 Place narrow; no effect on R6B floor area or height (the R6B rows carry no footnote) | no street-width case | agrees |
| L12 | Rear yard near the corner | ZR 23-344(a): none required within 100 ft of the point where two street lines meet at 135 degrees or less | distance of the lot's far corners from that point: 143.0 and 144.6 ft | the waiver covers the part within 100 ft, not the whole lot | one yes/no for the whole lot, assumed "yes" | see F2 |
| L13 | Setback above the base | ZR 23-433: 10 ft on a wide street, 15 ft on a narrow street | read from the text | 10 ft on Northern Boulevard; 15 ft on 215 Place | not modelled | must print "not covered" |
| L14 | Ordinary rear-yard depth | ZR 23-342, not captured | none | NOT KNOWN from the captured text | not computed | must print "not known" |

### Table B: made-up lots that test the reading (R6B, no overlay, standard residences)

| # | Lot | Floor area (2.00 x area) | Coverage | Area / 680 | Units, independent | Program today | Result |
|---|---|---|---|---|---|---|---|
| P1 | interior, 5,000 sq ft | 10,000 | 80 percent | 14.706 | 14 | 10,000 / 80 / 14 | agrees |
| P2 | corner, 4,000 sq ft | 8,000 | 100 percent | 11.765 | 12 (rounds up) | 8,000 / 100 / 12 | agrees |
| P3 | interior, 5,350 sq ft | 10,700 | 80 percent | 15.735 | 15 | 10,700 / 80 / 15 | agrees |
| P4 | interior, 5,360 sq ft | 10,720 | 80 percent | 15.765 | 16 | 10,720 / 80 / 16 | agrees |
| P5 | interior, 5,355 sq ft | 10,710 | 80 percent | 15.750 exactly | 16 ("equal to") | 10,710 / 80 / 16 | agrees |

**Wherever the program gives a number, it equals the independent value.** That covers the floor
area, the heights, the coverage percentage and the unit count for this lot and five made-up lots. It
does not cover what the program does not compute.

### Findings from the independent reading (none is fixed here)

| # | Finding | What it needs |
|---|---|---|
| F1 | The official definition of a corner lot limits the corner rule to the part of the lot within 100 ft of each street line. The program applies 100 percent coverage to the whole lot. On this lot the difference is a strip about 4 ft wide; on a larger corner lot it is not small. | capture the ZR 12-10 lot definitions; then a labelled draft reading and a law-based test |
| F2 | The rear-yard waiver covers only the part of the lot within 100 ft of the corner point. The program takes one yes/no for the whole lot. The far part of this lot may need a rear yard, and the ordinary depth is not captured, so the building option's full-lot floor plate may be too large. | capture ZR 23-342; until then the result says "not known" for the part beyond 100 ft |
| F3 | Two lot areas are in use: 10,075 sq ft (city records, used for the numbers) and 10,388 sq ft (the tax-map outline, used for the frontage and the drawing). They differ by 3.1 percent. | the agreement check prints both and their difference; neither is silently preferred |
| F4 | The building option is 20 ft tall and the minimum base height is 30 ft. The result carries a note about it; there is no independent example for the building option yet. | a law-based example for the building option |
| F5 | The reason shown when the qualifying-housing unit count is not available says the site "needs professional review". | reword to "not known" with the cause (R164) |
| F6 | Not captured, so the program cannot be checked against them: the ZR 12-10 definitions of lot area, zoning lot, floor area and lot coverage; the commercial overlay rules; how height is measured in R6B. | listed as "not known" on the R6B checklist until captured |

## 9. Unknown stays unknown (R229): what must be on the screen

| Case | The screen shows |
|---|---|
| a stated input is missing | "input needed", naming the input; no numbers |
| the lot area or lot type is not known | "not available", with the reason; never 0 |
| an answer whose rule does not cover the case (L7, L13, L14) | "not available" or "not covered", with the reason |
| remaining floor area | "Not confirmed" (the settled wording) |
| two sources disagree | both values, and no number computed from either |
| the server cannot reach its data | "could not be loaded"; nothing made up |

## 10. Order and what must be true first

1. On 2026-10-07 at 14:09 UTC or later: the dependency fix, by the normal reviewed path, started by
   hand. It is not done and not verified today.
2. The waiting changes, one at a time, each on a fresh green run after the fix.
3. Part A is contracted as a ledger task (citing R166, R167, R213 and R221 to R229), written by one
   producer on a branch from the then-current integration branch, reviewed by a different agent at
   the exact commit, merged.
4. Part B, the same way.
5. No production switch changes. No timer of any kind.

## 11. Lines in existing documents that are out of date

| Where (merged) | What it says | What is true |
|---|---|---|
| `docs/lanes/queues/C.md:16` | "flip the tests that assert it stays unmounted" | no such test exists |
| `docs/lanes/queues/C.md:16`; `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md` (links 5, 6) | this piece is blocked on the owner's "golden record" and reviewer | replaced by R164, R165 and ADR-007 (waiting as #432) |
| `docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md:121` (link 4) | the adapter still fails closed on the facts read | the bridge S6 is merged |

## 12. What this document does not establish

- It builds nothing and proves nothing works in a browser. The website was not run.
- The combined tree used for the made-up-lot runs is local and was never pushed.
- The inventory was not reviewed by a second agent before this document was written; its review
  record is on the pull request that carries it.
- R6B is not finished, the dependency fix is not in, and the program is not complete.
