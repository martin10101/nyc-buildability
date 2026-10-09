# M5-T133 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c8b9032419b0e91c35767033860e913826a5571a` (branch `task/wave6-corrections-after-reviewer-check`, pull request 466, review copy `/root/project/rv-w6-c`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review, and it gives no opinion on what the zoning law means. A second verifier checked the other two tasks of the wave (M5-T132, M4-T034).
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R435, R436, R509, R510, R511, R512, R513, R514, R515, R516, R519, R532, R534 (13 rows).

## Verdict: PASS for this task's 13 rows, each for the task's share. No required correction blocks acceptance.

- **What "the task's share" means here.** The task corrects a written record and its three made-up worked examples; it builds no estimator and approves no starting value. Rows R513 and R516 are met as far as the texts captured before the task reach: the mixed-building section and the two energy definitions were captured by task M4-T034 of the same wave and are written in the record as "not captured yet"; the verifier judged that an honest statement of this task's share, with the reading left to later work (backlog row DB-184). Row R534's last step, putting the corrected record to the owner again, is the orchestrator's. All thirteen rows stay open in the registry.
- **How it checked.** It added up one floor of Example B and one of Example C itself from the stated dimensions (2,640 against 40 x 66; 2,552 against 44 x 58; every difference zero) and checked every component's own arithmetic with exact fractions; it broke a dimension, removed an outline and built a floor like the old Example C (1,743 against 1,260, 483 too much): the check failed each time. It compared the record's quotes of ZR 23-20, 23-231, 23-432, 23-433 and the exterior-wall definition with the captures and their digests; opened the R6B row of the captured height table; searched the record for a sentence that starts the estimate from the allowed floor area, calls 0.60 to 0.75 realistic or validated, or offers a switch or a "confirm it applies" choice (only negations); and confirmed the two lists of section 8 (no question of law in the owner's list; no choice written as decided).
- **The failed review.** The first G3 review failed on one figure left over from the old layout of Example B; the verifier found the failure in the progress log ahead of the rework and kept unchanged in the review record, and the finding closed only by the reviewer's own second pass.
- **Observations that block nothing:** the record's quotes leave out the captures' term marks (the words are verbatim); one quote of the energy sentence stops before the sentence's end without an ellipsis; the gates were recorded at the submit head and the reviews made earlier, with one content identity; the fit check run on the raw old files fails for all three (they have no floors at all in the new form), while the builder's and the reviewer's red proofs restate the old floors first; the two limits of the checks carried as backlog row DB-182.
- **What it could not check, in its own words:** the owner update; the external HPD guideline document; the full api suite (the orchestrator's run: 8519 passed, 8 skipped at `fedd6ca1`).
- The registry validator, run by the verifier in the review copy: exit 0. The tests it ran (`tests/scenario/measurement_basis`): 38 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head: the task's files, the captures the record quotes, the thirteen rows, the D-090 manifest, the two sources and the task's gate and review records unchanged; it states that commits to other tasks' files, new capture files, other `project-control/` files and added lines of the backlog do not void it.
- Read by the orchestrator on 2026-10-07 at 22:26 UTC: the pull request's check list on `c8b90324` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in one message holding all three parts and the closing line, at 22:29 UTC. It is reproduced below unchanged (copied by script from the session transcript `fe5b10e4-9775-4fc2-a29b-9b2be9865f3d.jsonl`, line 1966; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 3
Role: INDEPENDENT directive-compliance verifier (DCV) for task M5-T133, directive D-090. I produced none of this work or its records. I am an AI agent; this is an AI review, NOT a human or professional/legal review (ADR-007). Read-only: I ran no project_control write, no git/gh write, wrote no file.
Frozen head: c8b9032419b0e91c35767033860e913826a5571a (git -C /root/project/rv-w6-c rev-parse HEAD confirmed; working tree clean). Applicability check: directive_registry.evaluate_task_refs(M5-T133) returns ok=True, applicable_ids == cited_ids == the exact thirteen rows (R435,R436,R509-R516,R519,R532,R534); missing/invalid/unresolved empty.

OVERALL VERDICT: PASS (all thirteen rows SATISFIED for this task's share; 0 VIOLATED, 0 UNVERIFIABLE).

CARRY-FORWARD CONDITION (stated up front, blob-level predicate). My verdicts may be stamped at a later head WITHOUT re-asking me provided, by git blob identity, ALL hold:
(a) every file under the task's allowed_paths is byte-identical to the frozen head blobs: docs/measurement-basis/MEASUREMENT_BASIS.md (5b82cdca), example-a json/md (a4eb5b69 / e87087b6), example-b json/md (f92b7734 / 33975647), example-c json/md (636c3525 / 4a1785a4), producer-report.md (be49b644), and the five test files measurement_basis_check.py (c13a0bac), _fit.py (4bcbd7ca), _lib.py (d0536b27), _render.py (f6d91afc), test_measurement_basis_examples.py (ba962087);
(b) the captures the record quotes are byte-unchanged under docs/research/zr-snapshots/v1/: zr-12-10-floor-area, zr-12-10-qualifying-exterior-wall-thickness, zr-12-10-mixed-building, zr-23-20, zr-23-23, zr-23-231, zr-23-232, zr-23-233, zr-23-234, zr-23-432, zr-23-433, zr-23-52;
(c) the thirteen rows' text/required_harness/required_evidence, the D-090 manifest, and the sources they trace to (source-044-amendment.md, source-055-amendment.md) are byte-unchanged;
(d) the M5-T133 gate records G0/G2/G3/G4 and project-control/reports/M5-T133-G3G4.md are byte-unchanged.
I TOLERATE, with no effect on these verdicts, any later commit that touches none of (a)-(d): the other wave tasks' files (M5-T132, M4-T034), NEW capture files added under docs/research/zr-snapshots/v1/ or services/api/app/_zr_snapshots/v1/ (the record cites none of them), commits touching only other project-control/ files, and individual added lines of docs/DISCOVERY_BACKLOG.md.

HARNESS RESULTS (reproduced in the review copy):
- python tools/validate_directive_compliance.py --check: DIRECT exit code 0 (no output on success; run unpiped from /root/project/rv-w6-c).
- cd services/api && python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis: exit 0, 38 passed in 0.42s.
- I did NOT run tools/test_directive_compliance.py or the full api suite (forbidden by brief; that is CI's job).

ROW M5-T133 D-090-R435: PASS
 - MEASUREMENT_BASIS.md section 3 line 258: "The measured physical space comes from a proposed building layout, never from the maximum floor area the law allows (R435)."
 - Section 4 lines 271-278: estimate starts from the proposed building's residential zoning floor area, "never from the 'allowed' or maximum permitted floor area"; "The maximum permitted floor area is a separate figure, a limit to check the proposal against."
 - Each example measures a stated layout (components with dimensioned area_parts), and section 5 keeps the legal cap as a distinct number; no schedule starts from max FAR. Source words verified at source-044-amendment.md line 39.

ROW M5-T133 D-090-R436: PASS
 - Section 4 line 288: "The ratios computed in the examples below belong to those examples only (R436)."
 - Section 7 lines 390-394: the three ratios differ (0.7540, 0.6483, 0.6828) "precisely because each depends on its own made-up layout"; "Correct arithmetic is not support for an assumption"; no percentage presented as typical of R6B.
 - Section 3 line 252-254 states the reconciliation "so nothing is deducted twice"; source words verified at source-044-amendment.md lines 41-43.

ROW M5-T133 D-090-R509: PASS
 - Section 4 lines 264-278 states the formula in words exactly as the owner required: estimated apartments = (proposed building's residential zoning floor area x assumed apartment-area ratio) / assumed HPD-measured apartment size; "No count is computed in this record."
 - grep of the whole record for "allowed/permitted floor area" returns only negations (lines 273-274, 296: "no sentence starts the estimate from the allowed or permitted floor area"); the owner's flagged "opening formula still says allowed floor area" is resolved.
 - Line 276-278 preserves "Where a detailed layout already measures the apartments ... used directly." Source verified source-055-amendment.md lines 49-56.

ROW M5-T133 D-090-R510: PASS
 - I independently added up Example C upper floor (typical-res) from example-c-mixed-use.json dimensions: apartment-interior 1720 + interior-partitions 60 + demising 96 + exterior-walls 200 + corridor 220 + stair 180 + elevator 56 + chases 20 = 2552; stated outline 44x58 = 2552; difference 0.
 - I independently added up Example B typical floor from example-b json: 1680+80+120+208+280+192+56+24 = 2640; outline 40x66 = 2640; difference 0. Example A typical 2000 = 40x50 outline.
 - Every component reconciles internally (sum of area_parts == measured_area; sum(floor_area x floor count) == measured_area) for all three examples, checked with exact Fraction arithmetic. Example C now supplies a complete ground floor (44x70=3080, sum 3080) that the claim-head file lacked.

ROW M5-T133 D-090-R511: PASS
 - Calling fit.fit_errors in-memory on the repaired examples returns [] for all three (they genuinely fit).
 - The check bites: I broke one dimension (B apartment rooms depth 42->43) -> 1 error (per-floor footprints 7420 vs schedule 7580); I removed C typical-res outline -> error "the floor has no stated outside outline"; I built a synthetic old-C floor (rooms 1120 fill inside outline 1120, ring 140, extras to 1743 vs outline 1260) -> both the overflow "difference 483" and the rooms-fill message fired, reproducing the owner's exact figures.
 - RED PROOF: running the committed fit check against the claim-head examples (git show d8ad46a8:...) fails for all three (structural: no floors/floor_areas keys in the pre-repair files); the producer's report reproduces the owner's exact overflow (C 1743 vs 1260 = 483; B no outline; A passes) by restating the old floors with old dimensions. The preserved tests include test_fit_check_bites_no_outline / _dimension_changed_by_a_foot / _rooms_fill_inside_outline / _on_a_real_example_mutation / _when_a_floor_outline_is_removed; all 38 pass.

PART 2 of 3

ROW M5-T133 D-090-R512: PASS
 - MEASUREMENT_BASIS.md line 290-296: "The worked examples establish no realistic range"; if adopted 0.60-0.75 is "a chosen sensitivity range, labelled unvalidated"; line 295-296: "No sentence in this record calls 0.60 to 0.75 realistic, expected or validated."
 - Section 8a item 1 (lines 412-416): ratio carried as "sensitivity range labelled unvalidated - never a validated or expected range"; reviewer recommendation noted but "NOT decided until the owner says so."
 - Withdrawn ratios named: section 7 line 380 and both change_logs name "earlier Example B ratio 0.6022" and "earlier Example C ratio 0.6676" as WITHDRAWN with the reason. grep for realistic/expected/validated shows only negations.

ROW M5-T133 D-090-R513: PASS (this task's share; the ZR 35-31 mixed-building combination is explicitly left to later work)
 - Section 6 lines 322-326 quotes ZR 23-20: the words match the capture zr-23-20 verbatim_excerpt exactly ("Where #floor area# in a #building# is shared by multiple #uses#, ... less any shared #floor area#"), the only difference being the ZR #defined-term# delimiters (markup, not words) stripped; cited digest 0685a2e4... equals the capture's content_digest_sha256.
 - No on/off choice: lines 319, 335-336 state it is "a required calculation, not a switch and not an optional allowance" and "never offered as a choice or a 'confirm it applies' switch"; grep for switch/optional/confirm/"off unless" in the record yields only negations.
 - Example C carries the attribution: example-c json shared_floor_area present=true, one shared component (shared-utility 120 sq ft); I recomputed 10428/12728=0.8193 share, 120x0.8193=98.32 to residential, 21.68 to commercial, labelled conditional ("not captured yet"); ratio uses residential-exclusive 10428 only.
 - The mixed-building section (ZR 35-31) is "not captured yet" (section 6 lines 339-347; section 8b item 2); its reading is later work carried by backlog DB-184. Honest for this task's share.

ROW M5-T133 D-090-R514: PASS
 - Section 1d lines 155-168 quotes the amenity rule; the words match capture zr-23-231 verbatim_excerpt exactly (#markup stripped): base named "the residential floor area of the building"; "amenity space shall not include floor space for circulation ... corridors or vertical circulation spaces"; "accessible to the residents of the building"; cited digest 81eb95e8... equals the capture's content_digest_sha256.
 - Line 166-167: "never an automatic 5 percent added to apartment space."
 - The old open point 5 no longer asks the base: section 8b item 1 states the base is settled by ZR 23-231 and only the ORDER remains a question of law (not a preference). Source verified source-055-amendment.md lines 68-69.

ROW M5-T133 D-090-R515: PASS
 - Section 8 is split into 8a "Choices for the owner" (design assumptions/display only: ratio, 700 sq ft size, floor heights, what-stays-not-known/naming, what the user sees) and 8b "Questions of law (settled by capturing and reading the text, never by preference)".
 - No question of law in 8a and no choice presented as decided: each 8a item carries "NOT decided until the owner says so"; 8b items (amenity order, mixed-building combination, energy/wall eligibility) are all legal questions, none put as a preference. The G3 reviewer independently confirmed the two lists are clean.
 - Source verified source-055-amendment.md line 69 ("resolved through research, rather than handed to you as a preference").

ROW M5-T133 D-090-R516: PASS (this task's share; reading the energy definitions is explicitly later work)
 - Section 1d lines 174-186 quotes the exterior-wall exclusion from capture zr-12-10-qualifying-exterior-wall-thickness (digest 119324c8..., matches); states it applies to wall thickness "added to a building existing on December 6, 2023" (over-cladding/re-cladding), "not a licence to subtract the ordinary exterior walls of a new building"; every example counts full exterior wall thickness.
 - Lines 188-202: the energy exclusion's two terms "fully electrified building" and "ultra low energy building" are "not captured yet (M4-T034 captures them)"; eligibility "withheld and no example takes it"; "A user's statement ... supports only a conditional result; it never establishes eligibility"; "no general 'confirm it applies' switch."
 - I confirmed the record cites neither zr-12-10-fully-electrified-building nor zr-12-10-ultra-low-energy-building (both files now present on the branch via M4-T034 but written as "not captured yet"; follow-up carried by DB-184). Honest for this task's share.

ROW M5-T133 D-090-R519: PASS
 - Section 8c lines 480-502 states floors above the maximum base height are set back and smaller; "A count of floors times one floorplate is therefore an assumption, and is labelled as one."
 - I opened the capture zr-23-432 structured table R6B row and verified: min base 30 ft, standard max base 45 ft, standard max building 55 ft, qualifying max base 45 ft, qualifying max building 65 ft - exactly as the record states (digest 9fab7be8... matches); the setback-trigger quote matches the capture verbatim_excerpt.
 - The setback depths quoted from zr-23-433 (digest 4fecf4d2... matches): "depth of at least 10 feet ... wide street ... at least 15 feet ... narrow street"; line 500 states "The program does not work out the setback yet" - the later-work part is honestly flagged.

PART 3 of 3

ROW M5-T133 D-090-R532: PASS
 - Two independent reviews recorded, both by agents other than the builder (producer = scenario-optimization-engineer): gate G3 reviewer = data-contract-verifier, G4 = qa-engineer (gates/M5-T133-G3.json, G4.json, result PASS at reviewed_sha 2670f454, manifest 94433ad7...).
 - The FAILED first review is recorded before the rework: task progress_log entry at 2026-10-07T21:26:04 (65->70%) records "GATE G3 ... at f2b446ec: FAIL on ONE finding F1 ... THE FAILED REVIEW IS RECORDED HERE BEFORE THE REWORK", ahead of the round-3 rework entry at 21:33:52; and it is preserved unchanged in reports/M5-T133-G3G4.md (line 5 "G3 FAILED at f2b446ec ... PASSED at 7c67cbea", lines 177-233 the full FAIL record).
 - No "addressed/closed on the builder's word": the progress log says finding F1 is "closed" only after the data-contract-verifier's independent second PASS at 7c67cbea; the G3G4 report ties the close to the one-line data diff verified by the reviewer.

ROW M5-T133 D-090-R534: PASS (the "put to the owner again" step is later work, not part of this task)
 - The record and examples are corrected by a contracted task of their own (packet project-control/tasks/M5-T133.json, directive_refs D-090 with these 13 rows) covering the formula (C1/R509), examples+test (R510/R511), range (R512), allocation (R513), amenity (R514), eligibility (R516), unequal floors (R519), and section 8 rewritten into owner-choices + questions-of-law (R515).
 - Independently reviewed before re-presentation: G3 (data-contract recompute of every floor/ratio and every quote-vs-capture) and G4 (fit test, 14 mutations, red proof) both PASS at 7c67cbea; I reproduced the fit, the arithmetic and the citation/digest checks myself.
 - The owner update ("put to the owner again") is NEXT ACTION item 3 of source-055 and is a later orchestrator step, not inside this task's allowed paths; correctly left to later work.

VALIDATOR EXIT CODE: 0 (python tools/validate_directive_compliance.py --check, direct/unpiped, from /root/project/rv-w6-c).
TESTS EXIT CODE: 0 (python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis from services/api; 38 passed).

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none. Scope confirmed clean: the union of this task's three material commits (38efb977, cacac6aa, 55cf2ac4) touches only files under the allowed paths (docs/measurement-basis/**, services/api/tests/scenario/measurement_basis/**, project-control/reports/M5-T133-producer-report.md); no services/api/app change, no estimator, no approved starting value, no new capture. The stale "15 units = 45 sq ft" figure is corrected to "13 units = 39 sq ft" in both example-b json (line 916) and its rendered .md (line 41); no residual.

NON-BLOCKING OBSERVATIONS:
1. The record quotes ZR provisions with the capture's #defined-term# delimiters removed. The words are verbatim against each capture's verbatim_excerpt; the # are ZR markup, not words, and the record discloses capture-markup as a known artifact (DB-167 note). Faithful.
2. The energy-exclusion quote (lines 52 and 190) truncates the capture sentence at "five percent of the floor area", dropping the capture's continuation "located within such building, and exclusive of any floor space otherwise excluded from floor area" without an ellipsis. Quoted words are verbatim; meaning for the point made (eligibility, not amount) is unaffected.
3. Gates G3/G4 were recorded at the task's own candidate head 2670f454 (reviews made at 7c67cbea), not at the frozen head c8b90324; identity carried by content_manifest_sha256 94433ad7 and the G3G4 report's identity note (allowed-path blobs equal at gate head; intervening commits touch only other tasks' files, project-control/ and DISCOVERY_BACKLOG.md). Consistent with the carry-forward predicate.
4. Red-proof nuance: the producer's "Example A passes" narrative is from a restatement of the claim-head examples (floor scaffolding added with old dimensions); the current check run against the RAW claim-head JSON fails structurally on all three (no floors key). This is historical narrative, not a defect - the check demonstrably bites (I proved it four ways) and the owner's cited C defect is reproduced exactly.
5. Known fit-check limits carried as WATCH in DB-182 (a vertical component is not checked to run through every floor it serves; the cap-figure test matches the sentence by exact wording) - not defects today.

WHAT I COULD NOT CHECK MYSELF:
- The owner-facing update / "put to the owner again" (a later orchestrator step outside this task's allowed paths); R512/R515 harness also reference docs/SESSION_HANDOFF.md and the session transcript, which are outside this task's scope - I verified only the record and examples (this task's deliverables).
- The external HPD Design Guidelines PDF content (sha256-pinned in the record, section 1b); I verified the in-repo ZR captures, not the external PDF.
- The full services/api suite (forbidden by brief; CI/orchestrator runs it); I ran only tests/scenario/measurement_basis (38 passed).

END-OF-REPORT
```
