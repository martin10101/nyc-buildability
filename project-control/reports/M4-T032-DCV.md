# M4-T032 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `1759c233e919a589c6b0a13d7ed5a3806bac548f` (branch `task/wave4-result-ways-readings-p4`, pull request 462, review copy `/root/project/rv-w4-1007c`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review. A second verifier checked the other task of the wave (M5-T129).
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R226, R241, R259, R291, R318 (5 rows).

## Verdict: PASS for this task's 5 rows, each for the task's share. No required correction blocks acceptance.

- **What the rows are met for, and what is left.** R226 and R318: the 23 new rows are worked from captured law text and the lot's recorded facts by two readers; the verifier recomputed two content digests against the live captures and confirmed that the saved readings equal the returns the orchestrator received, byte for byte below their headers. R241: no existing expected value or kind changed; the three overlay rows gained only `superseded_by`, and the loader hands out one current answer per question; the one later change to a new row (the review note) has a dated reason. R259: the cases are files of their own, apart from program output, and say that two AI answers agreeing is not proof. R291: this task's share of step 3 only (examples saved and tested); it resolves no missing rule and shows no result. All five rows stay open in the registry.
- **Left to later work, in the verifier's words:** the definition of "floor area ratio" and the R6 front- and side-yard requirement sections (the readers did not have them: the unit count of the made-up lot stays conditional); whether the lot has a prevailing street wall frontage; whether ZR 23-443 reaches it; the whole-lot corner coverage, per portion; connecting any of this to a result of the program.
- **Checked against both readings by the verifier itself:** ten rows, among them the four the orchestrator named. Each records a value only where both readings agree on the same basis; a condition one reading attaches is in the row's value and names that reading.
- **The corner-coverage point holds:** no row records a whole-lot coverage for the benchmark lot; row L5 of the real lot is "not known" and unchanged since the wave's base, as is the corner-reach case that the other task's tests read.
- **Two observations that block nothing:** the rear-yard row states one reading's caveat about ZR 34-23 and does not repeat the caveat both readings raise for the part of the lot beyond 100 ft of the corner (that part is "not known" in the rows that hold it); the README's description of the earlier overlay case and that case's change log still use the words "not captured" (earlier tasks; the test that guards the wording passes).
- **What it could not prove, in its own words:** that the two readers had no access to the program during their runs (it rests on their statements; the orchestrator's audit of the readers' tool logs is recorded in the session notes, outside the repository); the full prose of the 13 rows it did not trace one by one (the structural guards pass for all 23).
- The directive validator, run by the verifier in the review copy: exit 0. The tests it ran (the reference cases and the lot-reach test): 77 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head; it states that commits to the other task's files, to `project-control/` and to lines of the backlog do not void it.

How the return arrived (2026-10-07): in one message holding both parts and the closing line, at 14:31 UTC. It is reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, line 5309; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 2

Role: independent directive-compliance verifier (DCV) for task M4-T032, directive D-090. Frozen head confirmed: git -C /root/project/rv-w4-1007c rev-parse HEAD = 1759c233e919a589c6b0a13d7ed5a3806bac548f (branch task/wave4-result-ways-readings-p4, PR 462). I produced none of this work. I am an AI agent; this is an automated reading and reproduction of evidence, NOT a human or professional/legal review. Applicability confirmed: directive_registry.evaluate_task_refs(M4-T032) returns ok=true, applicable == cited == {R226,R241,R259,R291,R318}, no missing/invalid. verification.json for M4-T032 is still pending (verifier "", all five rows pending) — not yet stamped.

ROW M4-T032 D-090-R226: PASS
 - docs/reference-cases/R6B/cases/step-p4-worked.json row made-up-100x100-units carries the by-hand arithmetic (operands: FAR 2.00, lot area 10000 -> 20000; 20000 / factor 680 -> 29, fraction <0.75 dropped); both return-reading-P4-1.txt Q8(c) and return-reading-P4-2.txt Q8c give 29 on the same basis, so the worked example is law-based and independently calculated.
 - each row cites its section with snapshot_id + content_digest; I recomputed zr-34-221 (32320c4a30...) and zr-23-52 (f48f1ddc18...) against docs/research/zr-snapshots/v1/*.snapshot.json content_digest_sha256 — both match and the quoted text is inside the snapshot verbatim_excerpt.
 - the two readings' preambles (P4-1.txt line 5; P4-2.txt lines 3-5) state they worked only from the sealed folder with no access to the program or repository, so the examples were worked without reading the program's answer; I rely on those statements as the readers' claim (I did not observe the sealing).
 - services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p4.py::test_step_p4_settled_and_not_known_rows asserts the 29/floor-area-ratio values; suite passes.
 - Left to later work: the floor-area-ratio definition is still "did not have", so the unit count is a conditional value, not a settled number.

ROW M4-T032 D-090-R241: PASS
 - git diff 65338f6d..48aa0de8 -- cases/overlay-reading.json shows the floor-area-ratio, lot-coverage and rear-yard rows gained ONLY a superseded_by field (-> step-p4-worked#...); their expected.value/kind are byte-unchanged, so each stays the true record of what the step-P2 readers settled.
 - test_r6b_reference_cases_step_p4.py::test_step_p4_supersedes_the_three_overlay_rows... loads each superseded overlay row and raises lib.RowSuperseded naming step-p4-worked#<rid>, with the step-P4 target's superseded_by == [] — one current answer per question; suite passes.
 - the only existing-row change (sections-and-facts-not-had value, commit 61c75613) moved "Chapter-5 scope section" into the both-readings list to match BOTH readings, with a dated change_log entry — a corrected reading, not a match to a saved program result.
 - case-level what_it_is_worth and checked_by both state "agreement between two AI answers alone is not proof"; support code imports nothing from the rule/scenario engine (test_support_code_imports_no_engine passes), so no test accepts a value because it equals a saved program result.

ROW M4-T032 D-090-R259: PASS
 - cases live in their own files under docs/reference-cases/R6B/cases/ with facts, quoted law + capture id + content_digest and arithmetic; grep of services/api/tests/rules/reference_cases/*.py shows only stdlib + sibling-module imports, no rule/scenario engine or app.* import — engine-free, kept apart from program output.
 - step-p4-worked.json what_it_is_worth: "their agreement alone is not proof"; what_it_does_not_establish: "asserts no whole-lot coverage percentage ... real-lot.json row L5 and the corner-coverage rows stay not known"; test_no_program_result_in_any_case + its two mutation guards pass.
 - an expected value changes only with a recorded reason: change_log holds the dated F1 entry and the supersession entry.
 - test_step_p4_case_rows_name_both_readings asserts every row's source_reference names both readings; suite passes.

ROW M4-T032 D-090-R291: PASS
 - the examples are saved as files (cases/step-p4-worked.json + step-p4-worked.md + the two provenance readings) and tested (test_r6b_reference_cases_step_p4.py), not produced from a program run — this task's share of step 3.
 - where both readings agree the row resolves the step-P2 overlay condition (floor-area-ratio / lot-coverage / rear-yard now read); where they do not jointly settle, the row stays not_known with the reason — real-lot-prevailing-frontage and zr-23-443-reach are kind not_known (confirmed by lib.load_row and must_stay_not_known_errors).
 - no program result is shown: no FAR-to-floor-area number is asserted as settled (count held conditional), and no whole-lot coverage for the benchmark lot — real-lot.json L5 is kind not_known with its per-portion reason and its blob (d716f77d...) is unchanged since 65338f6d.
 - Left to later work (not "all addressed"): the floor-area-ratio definition and the R6/R6B front- and side-yard requirement sections are still "did not have" (unit count stays conditional; front/side-yard-vs-plain-R6B stays not known); prevailing-street-wall-frontage and ZR 23-443(a)/(b)/(d) reach stay not known; the whole-lot corner-coverage per-portion reading is not done; connecting any of this to a program result is later work.

ROW M4-T032 D-090-R318: PASS
 - each step-p4 row is worked from source text: it quotes captured ZR text with snapshot_id/content_digest, which I re-verified against the live snapshots (zr-34-221, zr-23-52 match).
 - worked by agents that did not see program output: the two readings state sealed-folder isolation and are saved unchanged as provenance — sha256 of provenance/return-independent-hand-calculation-9.md = d49c8bf2... and -10.md = d46fd0e7... both match the pinned digests, and the provenance bodies equal the received readings byte-for-byte (43934 / 45044 chars).
 - kept as files under docs/reference-cases/R6B/; the digest-pin test test_the_two_step_p4_readings_are_present_unchanged and its mutation test test_a_changed_step_p4_reading_is_caught pass.

END OF PART 1 — PART 2 follows with harness exits, carry-forward, corrections, observations, limits.

PART 2 of 2

HARNESS (ran once each, from the review copy /root/project/rv-w4-1007c):
 - python tools/validate_directive_compliance.py --check -> DIRECT exit code 0 (ran once; no stdout emitted, exit status captured directly).
 - cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py (venv /root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1, PYTHONPATH=services/api) -> 77 passed in 1.73s, exit code 0.
 - I did NOT run tools/test_directive_compliance.py or the full api suite (per instruction; those are CI's job).

ADDITIONAL REPRODUCED CHECKS (supporting the five rows):
 - F1 correction (gate claim in M4-T032-G3G4.md) reproduced from primary evidence: git diff 48aa0de8..61c75613 -- docs/reference-cases shows exactly the sections-and-facts-not-had row value (Chapter-5 scope moved into the both-readings list), one change_log entry, the README and page echoing it, and the producer report — no other case row changed. Verified against both readings: P4-1 Q4 ("the Chapter-5 scope/heading is not in the folder") and P4-2 Q10/Q4 both name it, so moving it to the agreed list is correct. The reading-9-only and reading-10-only pointer lists in that row match the two readings.
 - Whole-lot corner coverage: both readings state only the 23-362 rule (interior 80% / corner 100%) when comparing overlay vs plain R6B and neither works the corner-lot portion rule for the benchmark lot. Confirmed no step-p4 row records a whole-lot coverage for that lot (lot-coverage and overlay-text-on-lot-coverage rows record "same as plain R6B" / "lot coverage comes only from 23-362", no number). real-lot.json L5 is kind not_known, value null, per-portion reason.
 - corner-reach.json byte-unchanged since 65338f6d: blob 5b00fb8ce770... identical at both heads. real-lot.json likewise identical (d716f77d...).
 - Supersession is semantically sound: overlay-reading floor-area-ratio/lot-coverage/rear-yard ask "does the overlay change it" for the same benchmark lot/building; step-p4 rows answer "with ZR 34-22/34-23 read, is it the same as plain R6B" — same question, same lot and building, and the loader hands out only the step-p4 answer.
 - Rows checked against BOTH readings myself: floor-area-ratio, rear-yard, made-up-100x100-units, zr-23-441-reach, sections-and-facts-not-had (the four mandated + floor-area-ratio), plus lot-coverage, overlay-text-on-lot-coverage, dwelling-unit-factors, qualifying-residential-site and the readings-differ row zr-23-443-reach. Each records a value only where both readings agree on the same basis; conditions one reading attaches (reading 9's title-only completeness caveat on rear-yard; reading 10's "multiple dwelling residence" second condition on the unit count) are stated in the row value and attributed to the single reading.

CARRY-FORWARD CONDITION (blob-level predicate): my five PASS verdicts may be stamped at a later head without re-review while ALL of the following blobs are byte-identical to the frozen head 1759c233: (1) every file under docs/reference-cases/R6B/** — in particular cases/step-p4-worked.json, cases/overlay-reading.json, cases/real-lot.json, cases/corner-reach.json, provenance/return-independent-hand-calculation-9.md and -10.md, README.md, step-p4-worked.md, overlay-reading.md; (2) every file under services/api/tests/rules/reference_cases/**; (3) the D-090 requirements.json rows R226/R241/R259/R291/R318 and manifest.json; (4) the zr-snapshots/v1 capture files the step-p4 rows cite (content_digest_sha256 unchanged). I tolerate any later commit that touches NONE of the above — e.g. commits confined to project-control/** (gates, state.json, verification.json, reports) and to lines of docs/DISCOVERY_BACKLOG.md, and disjoint peer commits from the other task on this branch (M5-T129, services/api engine module and its own tests/decision files). A disjoint peer commit that modifies no file in (1)-(4) does not disturb these verdicts. If any blob in (1)-(4) changes, re-review that row.

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none.

NON-BLOCKING OBSERVATIONS:
 - rear-yard row: its value states reading 9's title-only completeness caveat but does not restate the beyond-100-ft / adjoining-lot caveat that BOTH readings also raise (P4-1 Q2 caveat (ii); P4-2 Q2b). It does not overstate (the agreed "same as plain R6B, no rear yard within 100 ft of the corner" is given by both; the beyond-100-ft not-known is carried in real-lot.json L5 and corner-reach.json). Informational only.
 - README line 33 (overlay-reading description) and overlay-reading.md change-log lines retain the phrase "not captured"/"uncaptured"; these are pre-existing (tasks M4-T028 / M4-T030), the README explainer (lines 58-59) defines the meaning, and the S6 test enforcing the "did not have" wording on the relevant rows passes. Not a defect introduced by M4-T032; the step-P4 README additions and rows use "did not have"/"not known".

WHAT I COULD NOT CHECK MYSELF:
 - Whether the two AI readers were truly isolated from the program output and repository when they worked — this rests on their own preamble statements. The repository supports it only indirectly (sealed-folder provenance saved unchanged, engine-free support code, no engine imports). I did not observe the sealing or the readers' runtime.
 - Full semantic fidelity of the step-p4 rows I did not individually trace to both readings (roughly 13 of 23). The structural guards (both_readings naming, readings_differ, must_stay_not_known, citation-digest, no-program-result, page-byte-identity) pass for all rows, but those check structure/citation/kind, not every row's full prose match; the ~10 rows I did trace are faithful.
 - The full services/api suite and CI at the pushed head (the orchestrator/CI's job); I ran only the two named suites plus the validator once.

VERDICT: PASS for all five requirement IDs (D-090-R226, R241, R259, R291, R318) at frozen head 1759c233, for this task's share, with the carry-forward predicate above and no blocking corrections. R291 is this task's share of step 3 only (examples saved and tested; it resolves no missing rule and shows no program result) — the items listed as "left to later work" remain owed.

END-OF-REPORT
```
