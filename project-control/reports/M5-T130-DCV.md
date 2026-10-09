# M5-T130 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `db5020be03d8d28ea397a89342a4e2a5bdec5d81` (branch `task/wave5-facts-validators-captures`, pull request 464, review copy `/root/project/rv-w5-dcv-a`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review, and it gives no opinion on what the zoning law means. A second verifier checked the other two tasks of the wave (M5-T131, M4-T033).
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R239, R240, R255, R257, R267, R268 (7 rows).

## Verdict: PASS for this task's 7 rows, each for the task's share. No required correction blocks acceptance.

- **What "the task's share" means here.** Nothing calls the new modules and the emitted results document is unchanged. For every row the task does only the GATHERING of a lot's recorded facts and the handing of them to the decision module; showing a result to a user, on the website, the drawings or the PDF, is left to the pieces that wire it in and emit. All seven rows stay open in the registry.
- **How it checked.** It drove `gather_result_ways` itself from scripts outside the repository. Among what it drove: no city record at all (every column "not read", every result withheld); an uncertain frontage (the reach stays unknown, the coverage and the rear yard are withheld, never a zero); no recorded lot area (the floor area and the unit limit are withheld and the outline's area is not put in its place); the two area figures at 10,075 against 10,075.4, 10,075.6, 10,076 and 10,388 (agree only when the rounded outline equals the record; no tolerance invented; neither figure chosen); a user's statement about the special density area (a conditional result naming the statement; the statement in no fact record); the four conditions with no data source (always "not checked"; the entry function has no way to mark one checked).
- **Reading O14** (an empty column is "recorded as absent" only after a recorded fetch of the whole city record) was checked at its root in the connector's code, not taken on the builder's word.
- **How the wave was run:** five points W1 to W5 met (the concurrency record committed before any builder's commit; no two builders' commits share a file; at most three builders, one pull request, the branch from the merge of task M0-T183; the failed G4 review kept unchanged in the progress log and in the review record, with the re-review by the same reviewer and the three modules byte-unchanged between the two commits; nothing changed under `.claude/` or `CLAUDE.md`).
- **The two owner messages recorded on this branch (W5).** Commit `db5020be` records owner messages 110 and 111 (D-090 sources 054 and 055, rows R500 to R535). The verifier confirmed that all 36 rows are pending and bound to none of the wave's tasks, and judged that message 111's findings (two wrong explanations in the module merged by task M5-T129; a later inventory of every explanation text, this task's modules included) do not bear on this task's seven rows as it stands: no result's way changes, nothing emits and nothing calls these modules today.
- **Observations that block nothing:** the six points of backlog row DB-175 and the WATCH row DB-174, all carried to the piece that emits; the later texts-only correction task of row DB-176.
- **What it could not check, in its own words:** the full api suite (the orchestrator's run: 8384 passed, 8 skipped at `d1e6683c`); the registry validator (the second verifier ran it); Windows behaviour; the other two tasks' gate identities; the body of the ZR 23-362 capture.
- The tests it ran (the task's five test files): 62 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head; it states that commits to `project-control/`, to lines of the backlog and to the other tasks' files do not void it.
- Read by the orchestrator on 2026-10-07 at 19:44 UTC: the pull request's check list on `db5020be` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in two messages. The first, at 19:47 UTC, held part 1 of 3 only; the orchestrator asked for the rest at once; the second, at 19:48 UTC, held parts 2 and 3 and the closing line. Both are reproduced below unchanged, in order (copied by script from the session transcript `fe5b10e4-9775-4fc2-a29b-9b2be9865f3d.jsonl`, lines 531 and 592; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 3

HEADER
Role: INDEPENDENT directive-compliance verifier for task M5-T130 (directive D-090), wave 5. I produced none of this work. I am an AI agent; this is an AI agent's review, NOT a human or professional/legal review, and it gives no opinion on what the zoning law means. The measure is the owner's words in the D-090 sources, the work order, and the independently read reference rows.
Frozen head reviewed: db5020be03d8d28ea397a89342a4e2a5bdec5d81 (confirmed by `git -C /root/project/rv-w5-dcv-a rev-parse HEAD`), branch task/wave5-facts-validators-captures, PR 464, review copy /root/project/rv-w5-dcv-a (clean).
Scope confirmed: `directive_registry.load_registry(...).evaluate_task_refs(M5-T130)` returns applicable == cited == {R229,R239,R240,R255,R257,R267,R268}, missing/invalid/unresolved all empty.
Primary evidence read in full: the new modules result_way_facts.py (291 ln), result_way_bridge.py (375), result_way_bridge_overlay.py (102); their tests; the merged read-only modules result_way_inputs.py / result_ways.py / result_way_conditions.py; the connector app/connectors/pluto_soda.py and reader app/profile/site_facts.py; the packet M5-T130.json; the work order Part 0; the gate record M5-T130-G3G4.md; the concurrency record; the backlog. I drove the entry function myself (scratch scripts under /tmp, piped via stdin, no repo write).

ROW M5-T130 D-090-R229: PASS
 - result_way_facts.py `_read_column`/`_state_from_readings` (lines 133-181): a column with no PLUTO fetch, a failed fetch, no row, or an untrusted value is carried as Recorded.NOT_READ, never ABSENT. I drove profile=None -> every condition NOT_READ, every result Withheld (no guess, no default).
 - result_way_bridge.py `adapt_reach` (lines 195-206) passes an unknown measurement through unchanged: `ReachValue(line.reach.value)`/`ReachValue(measured.corner.reach.value)` with no coercion. I drove an uncertain First Avenue frontage: reach={First Avenue: None, Main Street: 100.0}, corner None, angle None; coverage and rear_yard Withheld (gap_kind missing_information); NO way carries a numeric 'value'. Never a zero.
 - result_way_bridge.py `large_lot_answer(None)` (267-284) returns met=None "...is not stated, because no lot area is recorded." I drove area=None: large_lot.met=None, max_residential_far Withheld, the outline area (10,387.99) NOT substituted (inputs.area.recorded_sq_ft stayed None).
 - Benchmark drive: no way carries a numeric value; every shown value is Conditional or Withheld.

ROW M5-T130 D-090-R239: PASS
 - Owner words traced to source-033-amendment.md#owner-message-77 ("Resolve how the two area figures are used before calculating from them."); registry R239 carries them verbatim; the "two figures = 10,075 record vs 10,388 outline" is marked ORCHESTRATOR'S READING, not owner wording.
 - The one rule is written down in result_way_bridge.py `compare_lot_area` (227-261) docstring + returned statement, and applied before any consumer: AGREE only when round(outline)==recorded, else DISAGREE, else could-not-compare. I drove 10075 vs 10075.4 -> agrees; 10075.6 -> disagrees; 10076 -> disagrees; 10075 vs 10388 -> disagrees. No invented tolerance (honest strict rule; DB-173 records the owed wider tolerance).
 - No calculation mixes the figures: the decision module reads only `area.recorded_sq_ft` (result_ways.py 146, 348); `outline_sq_ft` appears only in wording (result_way_conditions.area_condition). I drove the benchmark: DISAGREES, both figures shown in area_statement, recorded figure used, outline never substituted. The difference is shown.

ROW M5-T130 D-090-R240: PASS
 - Owner words traced to source-033-amendment.md#owner-message-77 ("Let missing inputs stay unanswered."); registry R240 verbatim.
 - result_way_bridge.py `read_site_inputs` (159-189) carries a missing key as None (never a default). I drove, one at a time: no-district -> every result Withheld; no-lot-type -> coverage+rear_yard Withheld while max_residential_far stays Conditional (others unchanged); no-area -> floor-area+unit Withheld, others unchanged; no-outline -> could-not-compare, coverage Withheld, floor area Conditional; no-profile -> every column NOT_READ -> every result Withheld. Each missing input leaves its dependents "not known" and the rest unchanged.

ROW M5-T130 D-090-R255: PASS
 - Owner words traced to source-035-amendment.md#owner-message-79 ("Facts and legal eligibility must come from evidence." / "A user assumption ... must not become a verified fact."); registry R255 verbatim.
 - result_way_bridge.py `_density` (290-301) turns `special_density_statement` into a DensityKnowledge enum passed to the decision module; it never reaches `gather_recorded_facts`. I drove statement=True: unit_limit_standard is Conditional naming KIND_USER_STATEMENT ("If the lot is not in a special density area, as the user states"); NO recorded fact statement mentions density/user/states (leak list empty); density input = user_statement_not_in_one.
 - result_way_facts.py reads only city data (docstring lines 32-34); the statement appears in no fact record. A statement that the lot IS in one has no decided path and is held back (not guessed).

(continued in PART 2)
```

```
PART 2 of 3

ROW M5-T130 D-090-R257: PASS
 - Owner words traced to source-035-amendment.md#owner-message-79 ("For conflicting areas, establish what each measures and which applies." / "Don't automatically choose one." / "If unresolved, show defensible conditional results or withhold the affected calculations."); registry R257 verbatim.
 - On DISAGREES, no single settled figure is shown: result_way_conditions.py `area_condition` (119-143) returns a Condition kind=contradicted_record ("...neither is chosen automatically"), so every area-dependent result is Conditional, never Settled. I drove the benchmark: max_residential_far/floor_area + unit_limit_standard all Conditional with the contradicted_record assumption naming both figures (10,075 vs 10,387.99); none settled.
 - On could-not-compare, kind=unchecked_condition (conditional); where no recorded area, the floor area and unit limit are Withheld (result_ways.py 146-156, 348-358) and the outline never stands in. I drove no-area -> max_residential_far Withheld. The two figures are never auto-picked; results are conditional or withheld.

ROW M5-T130 D-090-R267: PASS
 - Owner words traced to source-036-amendment.md#owner-message-80 ("'not checked' must not become 'confirmed' just because there's a disclaimer."); registry R267 verbatim.
 - result_way_bridge.py `gather_result_ways` (357-361) hardwires the four K20 conditions to Checked.NOT_CHECKED, always; the entry signature has NO parameter to mark any checked. I confirmed the signature: {evaluator_inputs, geometry, housing_kind, outline, profile, special_density_statement} - none of waterfront/airport_height/transit_easement/near_district_line. I drove the benchmark: all four states = not_checked.
 - No result an unchecked condition could change is shown settled: on the benchmark every shown floor-area/height value is Conditional and its assumption names all four not-checked conditions (result_way_conditions.k20_condition, 100-116); no numeric value in any way. A disclaimer never upgrades to confirmed.

ROW M5-T130 D-090-R268: PASS
 - Owner words traced to source-036-amendment.md#owner-message-80 ("For unchecked conditions, keep unaffected answers visible, label defensible assumptions as conditional, and withhold only the answers that cannot be supported."); registry R268 verbatim; "settles scope decision 3" is marked ORCHESTRATOR'S READING, not owner wording.
 - This task feeds the per-result deciders so the result is neither a blanket withhold nor a bare not-checked list. I drove the benchmark: unaffected answers visible (floor area, heights Conditional), the unchecked conditions shown as one named conditional assumption, and only the unsupported results withheld (coverage - reach beyond 100 ft; rear_yard; setback; building option; unit limits). I drove missing-input cases: dependents withheld, others unchanged.

W1: MET - the concurrency record project-control/reports/WAVE5-2026-10-07-concurrency-record.md was first committed at 83a592df (contract seam) and corrected at 6979d27d (scope seam), both before the first builder commit 1ed440c4 (2026-10-07 16:47:06 +0000).
W2: MET - no two builders' commits touch the same file. M5-T130 (1ed440c4, d1e6683c): services/api/app/scenario/three_answers/result_way_facts.py, result_way_bridge.py, result_way_bridge_overlay.py; tests/scenario/three_answers/test_result_way_*.py, test_result_ways.py; tests/spatial/test_lot_reach.py; its report. M5-T131 (edb2af6d/1f53e5fb/fdab9401/816c5227): app/contracts/results_way_rules.py, app/contracts/study_contracts.py, app/scenario/three_answers/contract.py; tests/contracts/test_contract_serializers.py, test_results_three_ways_slot.py, test_results_way_rules.py; its report. M4-T033 (99845581, 9ec94043): docs/research/zr-snapshots/v1/* and app/_zr_snapshots/v1/*; its report. Both M5-T130 and M5-T131 write inside scenario/three_answers/ but DIFFERENT files (result_way_* vs contract.py) and DIFFERENT guard tests - no overlap.
W3: MET - at most three builders; one pull request (#464); the branch's merge-base with the integration head is 596c034f itself, which is the merge of task M0-T183 (PR #463) on candidate/D-024-mrl-option-b. The branch starts from that merge.
W4: MET (for M5-T130; the other two tasks' internal gate identity is the peer verifier's) - the G4 FAIL at 1ed440c4 is kept unchanged in the task progress log (percent-70 entry) AND in the review record project-control/reports/M5-T130-G3G4.md (section "G4, first review ... FAIL - part 1/2/3"); the re-review is by the SAME qa-engineer (G4 PASS at d1e6683c), and the same data-contract-verifier confirmed the three modules byte-unchanged (G3). I verified independently: the three modules + two guard tests diff 1ed440c4..d1e6683c is EMPTY; d1e6683c itself touches only the report + test_result_way_bridge.py; the gates were recorded at the d1e6683c content identity and the allowed-path files are byte-identical from d1e6683c to the frozen head.
W5: MET - owner messages 110/111 ARE recorded on this branch: commit db5020be captures source-054-amendment.md and source-055-amendment.md with rows R500-R535 (I confirmed all 36 are status "pending" and bound only to D-090-BOOTSTRAP, none to M5-T130/M5-T131/M4-T033), so "no new owner message recorded unless the record says so" holds - the record says so. `git diff --stat 596c034f db5020be -- .claude CLAUDE.md` is EMPTY (nothing changed under .claude/ or CLAUDE.md). The concurrency record predates the messages and does not mention them, which is honest: they arrived in a later project-control-only commit; all five commits after d1e6683c (d9a003a1, cd392876, 42f3eee6, 910a39e5, db5020be) touch only project-control/ + docs/DISCOVERY_BACKLOG.md. Message 111's defect content (rows R521-R524, backlog DB-176) concerns the MERGED result_ways.py (task M5-T129) explanation texts and asks for a FUTURE texts-only inventory task that would also cover this task's fact-carrying modules; it changes no result's way, nothing emits and nothing calls these modules today, so it does NOT bear on the seven rows for THIS task as it stands.

(continued in PART 3)

PART 3 of 3

TESTS - exit code and counts
`python -m pytest -q -p no:cacheprovider tests/scenario/three_answers/test_result_way_facts.py tests/scenario/three_answers/test_result_way_bridge.py tests/scenario/three_answers/test_result_way_bridge_overlay.py tests/scenario/three_answers/test_result_ways.py tests/spatial/test_lot_reach.py` from services/api: 62 passed, 1 warning (StarletteDeprecation, unrelated); DIRECT exit code 0. The two files the brief names (test_result_way_facts.py, test_result_way_bridge.py) pass within this run; I added the task's other new/changed test files (test_result_way_bridge_overlay.py and the two guard tests). Supporting read-only checks I ran: ruff on the 8 task files exit 0 ("All checks passed!"); tools/modularity_check.py --check exit 0 (0 failures, 29 pre-existing warnings, none naming a task file). I did NOT run validate_directive_compliance.py, test_directive_compliance.py, or the full api suite (per brief).

CARRY-FORWARD CONDITION (blob-level predicate)
My seven PASS verdicts may be stamped at a later head WITHOUT re-reviewing me iff ALL hold:
 (1) every file under M5-T130.allowed_paths has the same git blob at the later head as at db5020be: the three modules (result_way_facts.py, result_way_bridge.py, result_way_bridge_overlay.py), the three new test files (test_result_way_facts.py, test_result_way_bridge.py, test_result_way_bridge_overlay.py), the two guard tests (tests/scenario/three_answers/test_result_ways.py, tests/spatial/test_lot_reach.py), and project-control/reports/M5-T130-producer-report.md;
 (2) the seven requirement rows (text, source_ref, classification, binding, applicability.task_ids) are unchanged, the D-090 manifest digests for them are unchanged, and the four source files they trace to (source-032/033/035/036-amendment.md) are unchanged;
 (3) every commit after db5020be touches only paths under project-control/ and/or lines of docs/DISCOVERY_BACKLOG.md.
I TOLERATE commits that touch none of (1)-(2) - including the other wave-5 tasks' files (M5-T131, M4-T033) and any disjoint peer material commit - without re-review, because nothing under services/api/app imports this task's modules (verified) and the emitted results document is unchanged, so no such commit can alter this task's behavior on the seven rows.

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none.

NON-BLOCKING OBSERVATIONS
 - Backlog DB-175 (a)-(f), all carried to the piece that emits 1.3.0, none a defect today: (a) the overlay standing-condition detector keys on the literal word "caveat" in a reference-row value (a differently-worded caveat could read as supported); (b) "recorded as absent" is recognised by exact-matching the shared reader's served-empty sentence (if it changes, the column falls to the safe NOT_READ); (c) compare_lot_area rounds half-to-even at exactly half a square foot (no recorded case there); (d) LARGE_LOT_THRESHOLD.captured_words drop the capture's #term# markup (the figure "30,000 square feet or more" and the content digest are the capture's); (e) on the benchmark the rear-yard withhold reason is the overlay-owed reading, shown before the reach-beyond-corner reason (both true); (f) the two held_back strings (odd lot type; "lot IS in a special density area") are not run through the S7 text guard and one says "this piece" - neither is shown anywhere today.
 - Backlog DB-174 (WATCH): the profile flags (map_based_rules.py/site_facts.py) read an empty city column as "none or unknown: check needed" while this task reads a served-empty-after-fetch column as "recorded as absent"; intentional and work-order-directed (gap K10), to reconcile the wording when both reach the same screen.
 - Owner message 111 row R524 / backlog DB-176: a future, separately-contracted, texts-only correction task will inventory every input-state explanation in the merged result_ways.py AND in this task's fact-carrying modules; it changes no result's way and does not affect the seven rows as they stand.
 - O14 verified at the root (not taken on the producer's word): pluto_soda.fetch_by_bbl builds the URL "?bbl=<bbl>" with NO $select projection (whole record requested) and records absent_columns = PLUTO_COLUMNS - record_keys; site_facts._view sets checked_source only when reproducibility.source_id == PLUTO_SOURCE_ID, so a served-empty column resolves to ABSENT only when a PLUTO fetch is recorded, else NOT_READ. The M5-T130 verification.json row is correctly PROVISIONAL (verifier "", all seven requirements "pending", empty evidence) - not pre-stamped.

WHAT I COULD NOT CHECK MYSELF
 - The full services/api suite and the directive validator (forbidden by the brief; the second verifier runs validate_directive_compliance.py once; the gate record's "8384 passed, 8 skipped at d1e6683c" is a CLAIM I did not reproduce).
 - Windows/CRLF behavior (not exercisable here).
 - The internal G2/G3/G4 content identity of the other two wave tasks (M5-T131, M4-T033) beyond the shared-branch facts above - the peer verifier's scope.
 - Substantive correctness of the ZR 23-362 capture's own body-to-content-digest (task M4-T033's concern); I confirmed only that LARGE_LOT_THRESHOLD carries a capture id and the verbatim "30,000 square feet or more" and that the decision module compares recorded_area >= 30000.0.

END-OF-REPORT
```
