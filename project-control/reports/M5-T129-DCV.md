# M5-T129 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `1759c233e919a589c6b0a13d7ed5a3806bac548f` (branch `task/wave4-result-ways-readings-p4`, pull request 462, review copy `/root/project/rv-w4-1007a`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review, and it gives no opinion on what the zoning law means. A second verifier checked the other task of the wave (M4-T032).
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R237, R238, R240, R255, R257, R258, R267, R268, R269 (10 rows).

## Verdict: PASS for this task's 10 rows, each for the task's share. No required correction blocks acceptance.

- **What "the task's share" means here.** Nothing calls the module (the verifier searched `services/api/app` and `apps/web/src`). For every row the module does only the DECISION of how a result appears; showing it to a user, on the website, the drawings or the PDF, is left to the pieces that wire it in, and the verifier says so row by row. All ten rows stay open in the registry.
- **How it checked.** It drove `decide_result_ways` itself from a script outside the repository and validated 80 way objects against the contract. Among what it drove: a fact not given, one at a time (each withholds exactly its dependent results and leaves the rest unchanged; a large-lot answer not stated is not read as "no"); the benchmark lot's reach (the coverage is never shown at 103.93 ft); a user's statement (conditional, never settled); two area figures that disagree (conditional, both figures named, no choice); the four conditions not checked (no zoning result settled); no returned text calls a height the property's maximum.
- **The orchestrator's readings O1 to O13:** marked as the orchestrator's in the code, the report and the review record; none presented as the owner's rule or as settled law; none shows more than the owner's rows allow (it checked O1 and O4 itself against the work order). **The three scope-correction entries:** judged honest records of real points, each tightening the owner's rows on unknown and missing inputs, none a requirement reworded into a pass.
- **How the wave was run:** five points W1 to W5 met (the concurrency record committed before any builder's commit; no two builders' commits share a file, and the reach rows the module's tests read are byte-unchanged; one pull request from the merged base; both failed G4 reviews in the progress log and kept unchanged in the review record, with re-reviews by the same reviewers; no new owner message and no instruction file changed on the branch).
- **Three observations that block nothing.** (1) **One stale passage in the builder's report** (`project-control/reports/M5-T129-producer-report.md`, the list "Combinations left withheld under O10", item 2): it still says that a lot with no district is not specially withheld. That was true of the first version only; reading O11 changed it, the same report's Round 3 section and the review record say so, and the verifier drove the code (no district: every result withheld). The report is part of the reviewed content and was left as it is; this record is where the correction is stated. (2) The QA reviewer's note F10 is carried as backlog row DB-172, open, with row DB-171. (3) The condition kind chosen for an area that could not be compared is an imperfect but honest fit and never settles a result.
- **What it could not check, in its own words:** the full api suite (the orchestrator's run: 8267 passed at `71d52428`); the pull request's state on GitHub; whether the residential rules hold under the commercial overlay (out of this module's scope by design); the other task's rows.
- The test it ran (`tests/scenario/three_answers`): 130 passed, 2 skipped, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head; it states that commits to `project-control/`, to lines of the backlog and to the other task's files do not void it.
- Read by the orchestrator on 2026-10-07 at 14:31 UTC: the pull request's check list on `1759c233` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in one message holding all three parts and the closing line, at 14:33 UTC. It is reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, line 5336; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 3

Role: INDEPENDENT directive-compliance verifier (gate G3/G4 directive pass) for task M5-T129, directive D-090. I produced none of this work or its records. This is an AI agent's read-only review, NOT a human or professional/legal review; it gives no opinion on what the zoning law means — the measure is the owner's words and the work order.
Frozen head: `1759c233e919a589c6b0a13d7ed5a3806bac548f` (confirmed by `git -C /root/project/rv-w4-1007a rev-parse HEAD`), branch `task/wave4-result-ways-readings-p4`, PR 462.
Registry check: `directive_registry.load_registry(...).evaluate_task_refs(task)` returns ok=True, applicable_ids == cited_ids == the ten rows (R229, R237, R238, R240, R255, R257, R258, R267, R268, R269); missing_ids [], invalid_refs []. Confirmed myself.
Nothing calls the module: `grep -r result_way services/api/app apps/web/src` finds only the three module files themselves; `__init__.py` does not import them. So for every row below, the module does only the DECISION of how a result appears; EMITTING it to a user/screen/drawing/PDF is left to the later wiring piece (Part 0 B1/B2, Part A route, Part B website). I drove `decide_result_ways` myself from a stdin script outside the repo (imported from the review copy), and validated way objects against the bundled `results.schema.json` via a referencing Registry.

ROW M5-T129 D-090-R229: PASS
 - Drove the module: with district=None, area.recorded_sq_ft=None, reach=None, commercial_overlay=NOT_READ, or special_purpose_district=NOT_READ, the dependent results return `Withheld` ("not known") with reason+gap_kind+resolved_by — never a number, never `Settled`; the only `Settled` path requires every needed fact as evidence and K20 checked+absent (`result_ways.py` `_floor_area_way`/`_height_way`/`decide_result_ways`).
 - Validated 80 value_state objects (settled/conditional/withheld) against `packages/contracts/schemas/v1/results.schema.json#/$defs/value_state`: 0 errors, and withheld-with-a-number count = 0 (`Withheld.to_value_state` in `result_way_inputs.py` has no numeric field).
 - Task's share only: the module decides "not known"; SHOWING it on website/drawings/PDF (the three surfaces R229 names) is the uncalled wiring piece's job.

ROW M5-T129 D-090-R237: PASS
 - The producer report decision table (`project-control/reports/M5-T129-producer-report.md`, lines 390-413) has one line per gap K1-K20, each quoting the work-order sentence and its gap_kind; every gap resolves to either a shown value (settled/conditional when geometry/facts support) or `Withheld` ("not known"). This is the "table of every known gap with its choice" R237's harness requires.
 - No forbidden third state ("a number with a note"): a `Withheld` way carries no number; a `Conditional` carries a number-less way with named assumptions, not a settled number with a caveat (`result_way_inputs.py` dataclasses Settled/Conditional/Withheld). Source-035 records that the owner's six rules explicitly allow a clearly-labelled conditional, replacing the stricter "no third state" reading — the module matches that.
 - Harness I ran: `pytest -q -p no:cacheprovider tests/scenario/three_answers` from services/api → 130 passed, 2 skipped, exit 0; each gap's "not known"/shown choice is pinned by a test.

ROW M5-T129 D-090-R238: PASS
 - Drove the benchmark reach (street lines 99.97 & 103.93 ft, corner 144.60 ft): `max_lot_coverage` returns `Withheld`, reason "The lot reaches 103.93 ft from the 215 Place street line, beyond the corner-lot portion..." — whole-lot coverage is NEVER shown for this reach (`result_ways.py:_coverage_way` via `result_way_conditions.street_reaches_within`).
 - Drove a 40x100 lot fully within 100 ft with K20 checked+absent → coverage `Settled`; a 150 ft reach → `Withheld`. So coverage is shown only when the geometry (every street-line reach ≤ 100 ft) supports it; otherwise "not known".
 - The module computes no percentage (the 100% number stays in the engine); its share of R238 is the geometry gate on whether coverage may appear at all.

ROW M5-T129 D-090-R240: PASS
 - Drove each fact "not given" one at a time; each withholds exactly its dependent results and leaves the rest unchanged: lot_type=None → only coverage+rear_yard withheld (18/20 unchanged); area.recorded=None → floor-area(4)+unit_standard withheld (15/20 unchanged); reach=None → coverage+rear_yard; inclusionary=NOT_READ → floor area; flood=NOT_READ → heights; district=None → all (missing_information). (`result_ways.py`, `result_way_conditions.blanket_withhold`/`condition_withhold`/`no_lot_type`/`no_outline`.)
 - No input is filled by a default: drove `large_lot_threshold_met=None` in a coverage-showable lot → coverage `Withheld` (missing_information), NOT read as "no" (`result_ways.py:250-267`, reading O13).
 - landmark_or_historic NOT_READ and PRESENT → 0 results change (K19: landmark changes no zoning number) — correct, not an over-withhold.
 - Task's share: the module leaves dependent results "not known"; not forcing the user to answer and carrying unknown facts through are the route/website's job.

ROW M5-T129 D-090-R255: PASS
 - Drove special_density=USER_STATEMENT_NOT_IN_ONE → `unit_limit_standard` is `Conditional` with a `Condition(kind="user_statement", assumption="If the lot is not in a special density area, as the user states", settled_by="A sourced fact...")`; NEVER `Settled` (`result_ways.py:_unit_standard_way:360-369`).
 - Drove NOT_GIVEN → `Withheld`; EVIDENCE_IN_ONE → `Withheld`. So a user's assumption yields only a labelled conditional; without it the limit is withheld.
 - The statement is carried as a Condition, not a fact; keeping it out of the sourced-facts list and refusing a statement that contradicts a recorded fact live upstream (work order S7/H9) — correctly out of this uncalled module.

PART 2 of 3

ROW M5-T129 D-090-R257: PASS
 - Drove area agreement = DISAGREES → floor-area/unit `Conditional` with kind `contradicted_record`, assumption naming BOTH figures ("the recorded figure ... 10,075 sq ft ... and the tax-map outline area of 10,388 sq ft disagree; neither is chosen automatically") — no single settled figure, no automatic choice (`result_way_conditions.area_condition:133-143`).
 - Drove COULD_NOT_COMPARE → `Conditional` kind `unchecked_condition` ("it was not compared..."); agreement=None → `Conditional` unchecked_condition (explicit branch, no silent fall-through); AGREES → no area condition (K20 only); recorded=None → `Withheld`, outline never substitutes.
 - Task's share: the module never picks one figure; showing both figures/what each measures on screen and the tolerance (an input) are decided upstream.

ROW M5-T129 D-090-R258: PASS
 - The module keeps missing information and unfinished work apart with two gap_kind values; I collected both in use — not-read columns → `missing_information` (e.g. special_purpose NOT_READ, inclusionary NOT_READ), rule-not-built → `work_owed` (e.g. setback, building option, special-density evidence) (`result_way_inputs.REASON_KIND_BY_GAP`; every `Withheld.gap_kind`).
 - Checked reading O1 (the orchestrator's, not the owner's) against work-order §5's own kind definitions (lines 192-195): information→missing_information, owed/question→work_owed, evidence→missing_information when a column was not read / work_owed when a recorded condition can't be handled — faithful to the work order's K10/K18/K19 treatment; it does not reword R258, it implements the distinction.
 - The producer report (lines 448-463) lists every combination withheld as work owed (O10 open questions); no unfinished feature is counted as finished — withheld ways state what is owed.
 - Task's share: the section map and district checklist (also named in R258's evidence) are separate documents; the module's share is the per-result gap_kind only.

ROW M5-T129 D-090-R267: PASS
 - Drove K20 conditions NOT_CHECKED (all four) → every zoning result `Conditional` (heights and coverage both), NEVER `Settled`, naming the four conditions (`result_way_conditions.k20_condition`); the module returns a WAY, not a disclaimer, so a disclaimer cannot turn it settled.
 - Drove all four checked+absent → heights/coverage `Settled`; one PRESENT → `Withheld` (blanket). So "not checked" becomes neither "confirmed" nor settled.
 - Task's share: the screen must not add a disclaimer that masks the conditional — that is the website's job; the decision here is correct.

ROW M5-T129 D-090-R268: PASS
 - Drove K20 not-checked: results the conditions could change are `Conditional` and name the assumption (defensible), results that cannot be supported even on that assumption are `Withheld` (rear yard at 144.60 ft; coverage at 103.93 ft) (`result_ways.py:_rear_yard_way`/`_coverage_way`).
 - Drove all-absent → `Settled`, one-present → `Withheld` — matching "withhold only the answers that cannot be supported".
 - Task's share: "keep unaffected answers visible" is partly the module's (each result's way is decided independently and non-dependent results stay settled/conditional) and partly the wiring's (property facts are not this module's output).

ROW M5-T129 D-090-R269: PASS
 - Drove the heights: `Conditional` while K20 unchecked or flood not handled; `Settled` only when every applicable condition is checked+absent. Scanned every returned text across a wide input battery: 0 occurrences of "confirmed maximum", "maximum for this property", "the property's maximum", "professional review" (also 0 for "gap K"/"the caller"/"in this milestone"/"reference case").
 - Labels are the district's plain table-field names ("Maximum base height", `result_way_inputs.LABELS`), never "the property's maximum"; a base R6B height is shown as the district's limit, conditional until the other height rules are checked.
 - Task's share: labelling heights as the district's limit on screen is the website's job; the decision (conditional, not the property's settled max) is correct here.

Orchestrator's readings O1-O13: all marked as the orchestrator's readings in code comments, the producer report and the G3 review, and judged "fair/cautious" by G3 — I confirmed O1 and O4 myself against the work order; none is presented as the owner's rule or as settled law, and none shows more than the owner's rows allow. The three `scope_corrections` entries in `M5-T129.json` are honest records of real points, each TIGHTENING (not weakening) R229/R240: SC1 (third module for the 600-line threshold; O4 kind fix so a not-made comparison stays conditional-never-settled), SC2 (O11: district None → every result withheld as missing_information, per R240; O12: K14 label verbatim), SC3 (O13: large-lot "not stated" → coverage withheld, removing a default that stood for a fact). None is a requirement reworded into a pass.

PART 3 of 3

How the wave was run (W1-W5):
- W1 MET. `WAVE4-2026-10-07-concurrency-record.md` first appears in commit `7f5a97ba` (2026-10-07 11:39:49), before any builder commit (M4-T032 `48aa0de8` 12:16, M5-T129 `1d3d6964` 12:30). `git log 65338f6d..HEAD` confirms the order.
- W2 MET. M5-T129's six commits (1d3d6964, 6774d4b0, df7060ee, bcf44969, d96fb0b8, 71d52428) touch ONLY its allowed paths; M4-T032's commits (48aa0de8, 61c75613) touch no result_way file — no two builders' commits share a file. Read-while-written point held: `docs/reference-cases/R6B/cases/corner-reach.json` is byte-unchanged since `65338f6d` (empty `git diff --stat`), and M5-T129's tests read only its reach rows (confirmed in the G4 review's basis map). The module holds no overlay table (I scanned source: only legal numbers 100.0/135.0; no 34-/35- section).
- W3 MET. One PR (462); the branch starts from `65338f6d`, which is the tip of `origin/candidate/D-024-mrl-option-b` (merge of #461) — nothing built on unmerged work. The record names ≤3 builders/≤5 helpers, heavy runs one at a time.
- W4 MET for M5-T129. Both G4 FAILs (at 6774d4b0 and df7060ee) and the three G3 PASSes are recorded in `M5-T129.json` progress_log AND kept verbatim/unchanged in `M5-T129-G3G4.md`; re-reviews are by the SAME reviewers (data-contract-verifier G3, qa-engineer G4) at the corrected heads. Content identity: the three module files are byte-unchanged from round 6 `71d52428` through the frozen head; G2 (eaebe2c3), G3/G4 (reviewed_sha `82c1391215…`, identical content_manifest_sha256 `9fd68159…`) carry one allowed-path content identity. (M4-T032's W4 is the second verifier's; I did not independently verify it.)
- W5 MET. `git diff 65338f6d..HEAD -- project-control/directives` modifies only manifest.json (digest/audit), requirements.json (ONLY applicability task_id appends for M5-T129/M4-T032 + updated_at; no source text change) and verification.json (provisional rows). No new source file; no `.claude/**` or `CLAUDE.md` change; no `render.yaml`, dependency, or `.github/` change.

Harness: `python -m pytest -q -p no:cacheprovider tests/scenario/three_answers` from `services/api` → 130 passed, 2 skipped, DIRECT exit code 0. (The 2 skips are pre-existing NOT-BUILT guards, not this task's.) Per instruction I did NOT run `validate_directive_compliance.py`, `test_directive_compliance.py`, or the full api suite.

Prohibited-action evidence: task status `awaiting_gate` (progress 95) — NOT accepted; `verification.json` M5-T129 row is provisional (verifier "", status/result null) — no pre-filled/self-attested verdict; PR 462 open (not merged); no render.yaml/dependency/CI change (nothing deployed/installed); no new owner directive dispatched. Clean.

Carry-forward condition (blob-level predicate). My ten PASS verdicts may be stamped at a later head WITHOUT re-asking me iff at that head: (1) every file under M5-T129's allowed_paths — `services/api/app/scenario/three_answers/{result_ways.py,result_way_inputs.py,result_way_conditions.py}`, `services/api/tests/scenario/three_answers/{test_result_ways.py,test_result_ways_*.py}`, `project-control/reports/M5-T129-producer-report.md` — has the same blob sha as at `1759c233`; (2) `services/api/app/**` and `packages/contracts/**` are otherwise unchanged (nothing starts calling the module and the mirrored contract 1.3.0 is unchanged); (3) the ten D-090 rows in requirements.json, the D-090 manifest digests, and sources source-032/033/035/036 are byte-unchanged; (4) `docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md` and the reach rows of `docs/reference-cases/R6B/cases/corner-reach.json` are unchanged. I tolerate later commits that touch NONE of the above: i.e., commits confined to `project-control/**` (ledger/state/gates/reports/verification rows), to lines of `docs/DISCOVERY_BACKLOG.md`, and to M4-T032's own allowed paths (other `docs/reference-cases/R6B/**` and `services/api/tests/rules/reference_cases/**`) — none can change the module, its tests, the contract, or the rows. Any change to a blob in the set above voids the stamp.

Required corrections that BLOCK acceptance: none.

Non-blocking observations:
1. `M5-T129-producer-report.md` "Combinations left withheld under O10" item 2 (lines 456-459) still says a district-less lot "is not decided by the work order; the module does not specially withhold on it" — stale round-2 text, superseded by reading O11 and contradicted by the shipped code (I drove district=None → every result withheld, missing_information). The same report's Round 3 section (line 94) and the G3 second review both record O11 correctly. Report-narrative inconsistency only; code/tests/G3 are correct. Worth a one-line fix when convenient.
2. QA note F10 (the round-6 guard-test battery does not reach the K20-condition-present branch; those texts are clean today) is correctly NOT applied in this task and carried as `docs/DISCOVERY_BACKLOG.md` row DB-172(a), OPEN, bound into the next (wiring) engine task of Part 0. DB-171 is also OPEN (the 1.3.0 validator checks, bound into B2). Both confirmed OPEN and naming their binding task.
3. O4's kind choice (`unchecked_condition` for the could-not-compare area) is an imperfect-but-honest semantic fit (G3 note F2); it never settles the result. Acceptable.

What I could not check myself:
- The full api suite (ledger reports 8267 passed at 71d52428) — not run per instruction; I ran only the three_answers folder (exit 0) and reproduced S7 schema conformance + the row-driving scenarios.
- PR 462 merge state via `gh` (read-only) — I relied on the ledger (task awaiting_gate, not accepted).
- Whether the residential rules actually hold under the C2-2 overlay — a legal question, out of this module's scope by design (the caller states per-family support, reading O5).
- M4-T032's own rows/reviews (W4 for it) — the second verifier's task, not mine.

VERDICT: PASS — all ten rows (R229, R237, R238, R240, R255, R257, R258, R267, R268, R269) SATISFIED for this task's share, with the rest explicitly named as owed to the wiring piece; no VIOLATED or UNVERIFIABLE row; no blocking correction.

END-OF-REPORT
```
