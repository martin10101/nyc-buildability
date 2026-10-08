# M5-T137 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `3e92599c0e2c476f73f876ae59d782ef84859675` (branch `task/wave10-conditions-from-evidence`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R139, R229, R240, R241, R255, R256, R570, R582, R584, R588.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 11:15 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T137 (directive D-090, ten rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier, read-only). This is not a human or professional review; it is an independent, reproduced-evidence check. I produced none of this work.

(1) HEAD VERIFIED
 - `git rev-parse HEAD` in `/root/project/rv-w6-a` = `3e92599c0e2c476f73f876ae59d782ef84859675` (detached), the frozen head; it branched from `42d85651` on `candidate/D-024-mrl-option-b`.
 - The ledger tells the history truly: `git log 42d85651..HEAD` shows contract (86f4ac73) → claim-seam 7b5938e4 (G0 PASS, progress 20) → builder 1aacada9 (progress 70) → correcting commit b6aab84a (progress 75) → reviews-kept fb54f797 (progress 90) → submit-seam f41ca2e2 (G2) → gate record 3e92599c (G3/G4). `scope_corrections` and the progress log show the orchestrator read 1aacada9 BEFORE any review, corrected its own reading O36 (a not-known scope line showed the stand-in value), the same builder made b6aab84a, both reviews ran at 3f540bb3 and passed first reading; no review failed.
 - The review record `project-control/reports/M5-T137-G3G4.md` keeps both returns verbatim (G3 data-contract-verifier PASS, G4 qa-engineer PASS), naming seven notes (G3 F1–F3, G4 F1–F4), including the one mutation nothing catches — G4 F1 / mutation (p): an interior/through lot treated as a corner inside the new entry — benign here (nothing mounted) and bound into the server-route packet.

(2) ROWS
ROW D-090-R139 — PASS
 - The journey and wiring tests now call `run_engine_and_result_ways_from_evidence` (new entry in `result_way_engine_bridge.py`); `git diff 7b5938e4 HEAD -- tests/journey/test_215_16_northern_journey.py` removes the five typed values (`overlay_present=True`, `special_district_present=False`, `within_100…=True`, `angle=90.0`, `special_density_area=False`) and the `build_three_answer_inputs` call.
 - The new entry gathers the decision facts first, then derives all five conditions from that same `gathered` object (lines 178–221); no condition is typed in anywhere on the journey path.
 - Stays open in the registry: the full bridge-scope obligation and D-090-BOOTSTRAP are broader than this one engine-condition piece.
ROW D-090-R229 — PASS
 - In the committed fixture the density line reads value `"Not known"`, unit null, basis `assumed`, statement naming what was taken and that the unit limit is withheld; the stand-in value is never shown as the row value (`three_way_document.py` `_WORDS_VALUE_BY_SOURCE`, lines 140–145, 248–253).
 - `tests/.../test_three_answers_three_way_emit.py::test_s137_not_known_lines_show_words_never_a_boolean_or_number` passed; G4 mutation (n) (a not-known line carrying a value) is caught by six tests.
 - Stays open: "shown on the website, the drawings and the PDF" across all outputs — the website reader and PDF are later pieces; this share is the emitted document and its two drawings only.
ROW D-090-R240 — PASS
 - `engine_conditions.within_100_and_angle` returns NOT_KNOWN when there is no corner measurement, and the invariant test `test_s137_invariant_over_the_benchmark_states` holds that with no geometry only the dependent results are withheld while the floor-area figures (20,150 / 24,180) stay shown.
 - `test_corner_without_a_measurement_is_not_known` passed in my run (352 passed, 2 skipped, exit 0).
 - Stays open: the general missing-input obligation across the product is broader than this piece.
ROW D-090-R241 — PASS
 - `test_wiring_emits_nothing.py` module docstring and `test_s12_entry_emits_the_committed_three_way_fixture` are explicitly labelled an "UNCHANGED/WIRING proof only … NOT that any value is correct — the correctness of each way comes from the reference cases" (lines 1–14, 102).
 - G4 check 2 reproduced that the expected measured figures load from `docs/reference-cases/R6B/cases/*.json` (144.60, 100.00, 180.28; FAR 20150/24180), not from program output.
 - Stays open: the row also covers several M4 tasks; this share is only this task's test list.
ROW D-090-R255 — PASS
 - `engine_conditions.special_density` maps the user's statement to `USER_STATEMENT`; the scope line (`three_way_document.py` lines 218–222) says "it is a statement, not a recorded fact", basis `entered`; no statement → NOT_KNOWN, never recorded as a fact.
 - `test_density_user_statement_not_in_one_is_no_as_a_statement` and `test_density_no_statement_uses_the_inside_one_stand_in` passed.
 - Stays open: the broad "facts and eligibility from evidence" obligation spans the whole product; this share is the density condition and its labelling.
ROW D-090-R256 — PASS
 - Every value the engine is given for a condition is printed in that condition's scope line: measured figures (144.60 ft, 89.7°), the recorded overlay code (C2-2), and for the one stand-in the statement names the value taken ("it is taken to be in one for the calculation") — nothing is applied unseen.
 - `test_s137_scope_lines_say_where_each_condition_comes_from` and `test_s137_scope_texts_are_plain_and_true` passed; the unit-limit label prints formula/factor/rounding (work-order H10).
 - Stays open: visible, editable starting values for design choices (floor height, apartment size) are other pieces; this share is the five engine conditions.
ROW D-090-R570 — PASS
 - The regenerated fixture carries NO number for any withheld result: `legal_unit_limit_standard/_affordable/_senior`, `max_lot_coverage`, `rear_yard`, `setback_above_base` are `way:"withheld"` entries (label/reason/gap_kind/resolved_by only), and `building_option` is whole-answer not_available; no `"value": 16` appears anywhere.
 - The O36 correction is in place: a not-known line shows the words "Not known", not the stand-in substitute; the invariant test confirms no shown result rests on a basis-`assumed` value; G4 mutations (a)–(e) each caught.
 - Stays open: "stays withheld on the screen and in an export" — the screen and exports are later pieces; this share is the emitted document and drawings.
ROW D-090-R582 — PASS
 - This is the piece before the server route (the connect-the-display chain), built on merged work: the claim base 42d85651 is the wave-9 merge; `docs/DISCOVERY_BACKLOG.md` DB-201 states the route waits for M5-T137.
 - What stays owed is on record: DB-200 (the contradiction this task removes) is QUEUED(task M5-T137) and DB-201 (the route) is OPEN.
 - Stays open: the wave-8-finished-and-merged-under-the-checks ordering is proven by the wave-8 merge record and contract dates, which are outside this task's diff; that part remains in the registry.
ROW D-090-R584 — PASS
 - `git diff 7b5938e4 HEAD --name-only` touches no file under `services/api/app/api/`, not `app/main.py`, `app/config.py`, `render.yaml`, nor `.github/`; the material commits change only the three modules, the fixture, two drawings, four tests and the report.
 - G3 check 1 independently confirmed app/api, main.py, config.py, render.yaml and the website source are byte-identical to the claim-seam head; no route, mount or switch.
 - Stays open: the restriction also binds the later display piece.
ROW D-090-R588 — PASS
 - No section or option is dropped; the diff adds derivation + scope honesty only. What stays owed is recorded: DB-196 (no "not known" basis in the contract), DB-198 (the benchmark rear yard still names one of its two reasons), DB-199 and DB-201 — none removes a part of the report.
 - The task packet and evidence map keep the full report in scope (the engine, schema, website untouched).
 - Stays open: the standing "keep the full report in scope" obligation binds every later packet/update.

(3) BINDING B1–B5
 - B1: `git diff 42d85651 HEAD -- …/requirements.json` appends `"M5-T137"` to exactly ten `applicability.task_ids` arrays (the only other +/- lines are trailing commas and the `updated_at` timestamp); no requirement `text` changed.
 - B2: `directive_registry.sha256_text_artifact(requirements.json)` = `a1ea42d0…ba01b` equals the manifest `requirements_content_digest_sha256`; the manifest audit_log has the 2026-10-08T09:24:50 `applicability_bound` entry naming M5-T137 and the ten rows, digest resynced same commit.
 - B3: `verification.json` has one M5-T137 row, `applicable_requirement_ids` exactly the ten in order, `verifier` "", `reviewed_sha` null, every requirement `pending` with empty evidence.
 - B4: `reg.evaluate_task_refs(M5-T137 packet)` over the real registry returns ok=True, applicable_ids == cited_ids == the ten, missing_ids=[], invalid_refs=[], reasons=[].
 - B5: `derive_applicable` spans all active directives and returned only the ten D-090 rows; nothing else applies to this task uncited. Gates: G0 PASS, G2/G3/G4 PASS, and G2/G3/G4 share one content identity `content_manifest_sha256 = 7f0ad3da…4b125`. `validate_directive_compliance.py --check` exit 0 (direct).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review provided: (a) the task's 19 allowed-path files keep the blob ids they have at 3e92599c (an absent file staying absent); (b) the engine files, the decision modules other than the adapter, `services/api/app/contracts/engine_disclosures.py` and `evaluator_inputs.py`, everything under `packages/contracts/schemas`, `services/api/app/_contract_schemas`, `packages/contracts/generated`, `services/api/app/rules/rulesets` and `docs/reference-cases` stay byte-identical to the claim-seam head 7b5938e4; (c) the text of the ten rows and their binding to M5-T137 are unchanged.
 - Tolerated later commits: commits touching only `project-control/**` and `docs/DISCOVERY_BACKLOG.md`, and a merge of the integration branch that changes none of the predicate files. Any change to a predicate blob voids this stamp and requires re-review.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The wave-8 merge-under-full-checks ordering (R582) is evidenced by the wave-8 merge record and contract dates, outside this task's diff; I verified only that this piece is built on the merged wave-9 base and is correctly sequenced before the route.
 - The full api suite, the website lint/typecheck/build and the 153 browser tests were run by the orchestrator (the brief forbids the full suite and the compliance harness here); I reproduced only `pytest tests/scenario/three_answers tests/journey` (352 passed, 2 skipped, exit 0) and `validate_directive_compliance.py --check` (exit 0).
 - The interior-lot-as-corner path through the new entry (G4 F1 / mutation p) is unpinned end-to-end; I confirmed it is named in the review record and bound into the server-route packet, but I did not exercise it, and it stays owed before the route lands.
END-OF-REPORT
```
