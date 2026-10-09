# M5-T132 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `c8b9032419b0e91c35767033860e913826a5571a` (branch `task/wave6-corrections-after-reviewer-check`, pull request 466, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review, and it gives no opinion on what the zoning law means.
One verifier checked the two tasks M5-T132 and M4-T034 together. Its return is reproduced in full in both tasks' records (`M5-T132-DCV.md` and `M4-T034-DCV.md` hold the same text below the line); this file is the record for **M5-T132**. Another verifier checked the third task of the wave (M5-T133).
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R258, R521, R522, R523, R524, R532 (6 rows).

## Verdict: PASS for this task's 6 rows. No required correction blocks acceptance.

- **How it checked.** It drove the decision module itself, at this head and at the claim head. Evidence that a lot is outside a special density area: the reason now names the evidence and the "resolved by" text names the owed work; the old module answered "there is no evidence" and asked for the fact (the fault reproduced). The three corner states (the angle only, the distance only, both): each names the condition that really fails and says which one holds; the old module blamed the distance when the angle failed (reproduced). The lot-coverage reason for the benchmark reach of 103.93 ft no longer says that the whole lot is within 100 feet. Its own battery of 85 input states, compared with the claim head: no result changed the way it appears and no kind changed. It picked ten states the packet does not name and found each in the builder's table with a true reason and a test.
- **Row R523** (before the module reaches users): nothing under the server's routes or the website names the module, so the order holds today; wiring the module into the engine, a route, a screen or an export is left to later pieces, and the row stays open for keeping that order.
- **The failed reviews (row R532).** Both first reviews failed and are in the progress log ahead of the rework and unchanged in the review record; the findings closed on the reviewers' own second reviews, never on the builder's report.
- **How the wave was run:** five points W1 to W5 met (the concurrency record committed before any builder's commit; the three tasks' files disjoint; three builders, one branch from the merge of wave 5; every failed review recorded and re-reviewed by the same reviewer, one content identity per task, the changed files bound by literal paths; the correction of the orchestrator's own reading in row R517 judged an honest record with the owner's words and the source file unchanged; owner message 112 recorded and bound to no task; nothing changed under `.claude/` or `CLAUDE.md`).
- **One slip in the verifier's own text, noted here so that no reader is misled:** it calls `d8ad46a8` "M5-T133's first commit" that "bundled the orchestrator-only claim-seam control files". `d8ad46a8` is the orchestrator's claim-seam commit (the head all three builders started from) and holds no builder's work; the builder's first commit for M5-T133 on the branch is `38efb977`. Its conclusion (no file touched by two builders) is unaffected.
- **Observations that block nothing:** the two notes of the second gate reviews (a failing value closer to its limit than about five ten-millionths would print as the limit, backlog row DB-183; two rows' tests would pass on the text for "both not measured", carried in the backlog).
- **What it could not check, in its own words:** the full api suite (the orchestrator's run: 8519 passed, 8 skipped at `fedd6ca1`); the registry validator (the other verifier ran it: exit 0); the pull request's state on GitHub.
- The tests it ran (`tests/scenario/three_answers` and the capture bundle test): 296 passed, 2 skipped, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head: the task's files, the rows, the D-090 manifest and the sources unchanged; later commits only under `project-control/` and lines of the backlog.
- Read by the orchestrator on 2026-10-07 at 22:26 UTC: the pull request's check list on `c8b90324` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in two messages. The first, at 22:31 UTC, held part 1 of 3 only; the orchestrator asked for the rest at once; the second held parts 2 and 3 and the closing line. Both are reproduced below unchanged, in order (copied by script from the session transcript `fe5b10e4-9775-4fc2-a29b-9b2be9865f3d.jsonl`, lines 1993 and 2012; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 3

Role: INDEPENDENT directive-compliance verifier (final review, read-only) for tasks M5-T132 and M4-T034, directive D-090. I produced none of this work or its records. Frozen head: c8b9032419b0e91c35767033860e913826a5571a (confirmed by git -C /root/project/rv-w6-a rev-parse HEAD; branch task/wave6-corrections-after-reviewer-check; working tree clean). I am an AI agent; this is an agent review, not a human or professional review, and gives no opinion on what the zoning law means. Applicability confirmed: directive_registry.evaluate_task_refs returns applicable==cited for both tasks, exactly the eleven rows under review (M5-T132: R258,R521,R522,R523,R524,R532; M4-T034: R291,R513,R516,R517,R526), ok=true, no missing/invalid.

ROW M5-T132 D-090-R258: PASS
 - I drove the module myself (scratch via stdin, no files written): every withheld/conditional state carries a kind that keeps "missing information" apart from "work owed" - e.g. B4 special-purpose-district NOT_READ -> missing_information ("a column that was not read is never taken as 'none'"); the density rule, senior housing, per-portion coverage -> work_owed with resolved_by naming the owed work, never settled/finished.
 - services/api/app/scenario/three_answers/result_ways.py and report section 3 ("Kinds changed: NONE") show no owed feature is labelled finished; a promised-but-unbuilt rule stays work_owed (e.g. _unit_qualifying_senior_way lines 502-520: "not known: it is not set by this formula", kind work_owed).
 - My 85-state before/after battery (current vs claim head d8ad46a8) found 0 gap_kind changes, confirming the kind of each state is deliberate and unchanged.

ROW M5-T132 D-090-R521: PASS
 - I drove decide_result_ways on special_density=EVIDENCE_NOT_IN_ONE: unit_limit_standard reason = "Evidence records this lot outside a special density area; how the legal dwelling-unit limit is shown on that evidence has not been worked out ..." and resolved_by = "Working out how the legal dwelling-unit limit is shown for a lot recorded outside a special density area ..." - it does NOT say "no evidence" and does NOT ask for a density-area fact the state already holds (result_ways.py lines 437-457).
 - I loaded the claim-head module (git show d8ad46a8) and drove the same state: old reason = "There is no evidence of whether this lot is in a special density area ...", old resolved_by = "A sourced fact saying whether the lot is in a special density area." - reproducing exactly the fault O19/the harness name, so the fix is real and the pinning test fails on the old code.
 - The distinct NOT_GIVEN state still correctly says "There is no evidence ..." - the two states are separated, not merged.

ROW M5-T132 D-090-R522: PASS
 - I drove the three corner states myself. Angle-only (reach 90 ft, angle 140 deg): reason = "... the two street lines meet at 140 degrees, more than the rear-yard waiver's limit of 135 degrees; the far corner is 90 ft ..., within 100 ft of it." - names the angle as failing, says the distance holds, never "beyond" (result_ways.py _rear_yard_outside_waiver lines 319-371, else-branch line 357).
 - Distance-only (corner 144.6 ft, angle 90 deg): reason names "the far corner is 144.60 ft ..., beyond the rear-yard waiver area ...; the two street lines meet at 90 degrees, within the waiver's limit of 135 degrees." - distance fails, angle holds.
 - Both (144.6 ft, 140 deg): names both conditions.
 - I drove the claim-head module on the angle-only state: old reason = "The far corner is 90 ft from the corner point, beyond the rear-yard waiver area (the whole lot is within 100 feet ...)" - reproducing the fault (blames distance when the angle fails); the fix is genuine.

ROW M5-T132 D-090-R523: PASS
 - Texts-only confirmed: my 85-input-state battery comparing (key, way-type, gap_kind) of every result between the claim head d8ad46a8 (loaded via git show into a synthetic package) and HEAD returned 0 mismatches - no result changed the way it appears, no kind changed.
 - No consumer shows the module's texts yet: grep across services/api/app/api and apps/web/src finds no reference; no file in services/api/app outside the three_answers package imports decide_result_ways or gather_result_ways. So "before the module reaches users" holds trivially today.
 - Still left to later pieces: wiring decide_result_ways/gather_result_ways into the engine, any route, screen or PDF export (explicitly NOT IN THIS TASK); the truth-table test pins US5, RY8, RY9 (and every withheld state) as still withheld.

ROW M5-T132 D-090-R524: PASS
 - The report (project-control/reports/M5-T132-producer-report.md section 2) tables every input state (blanket, overlay, floor-area, heights, coverage, rear yard, setback, unit limits, building option, whole-answer, gather texts) with way, kind, checks a/b/c, verdict and a test id.
 - I picked ten states the packet does not name (B4 spd-not-read, B7 K20-present, OB1 overlay-not-read, OB3 overlay-family-missing, FA3 inclusionary-not-read, FA7 area-could-not-compare, H2 flood-not-read, C4b street-reach-unknown, C6 large-lot-not-stated, US3 evidence-in-one, plus UA1) and drove each: every reason names the condition that really fails and no resolved_by asks for a held fact; each matches its table row.
 - Same fault left anywhere: I re-drove the coverage "reaches beyond" state and the benchmark lot (103.93 ft) - both now read "beyond the corner-lot portion (the part within 100 ft of each intersecting street line)" with no false "whole lot is within 100 feet" clause (the G3 F1 fix), so that same-class fault is gone.
 - services/api/tests/scenario/three_answers/test_result_ways_truth_table.py: a 55-row parametrized _TABLE with per-row must_contain/must_not_contain token assertions, plus a 55-key _EXPECTED_WAY_SIGNATURE test pinning the way+kind of ALL results per state - one test per state, and the two reviewer cases became regression tests (test_s1_..., test_s2_...).

ROW M5-T132 D-090-R532: PASS
 - Independent gate records at a named commit: project-control/gates/M5-T132-G3.json (reviewer data-contract-verifier) and M5-T132-G4.json (reviewer qa-engineer), both result PASS, reviewed_sha 2670f454, content_manifest_sha256 47faffdf..., report_file M5-T132-G3G4.md; G2 recorded by reviewer "orchestrator" (not the producer).
 - Both first reviews FAILED and are recorded before the rework: the task progress_log 70% entries record "GATE G4 ... at f2b446ec: FAIL" and "GATE G3 ... at f2b446ec: FAIL on ONE finding, F1", each ending "THE FAILED REVIEW IS RECORDED HERE BEFORE THE REWORK"; the 95% entry records both second reviews PASS at fedd6ca1.
 - project-control/reports/M5-T132-G3G4.md holds every reviewer return verbatim (both FAIL reports at f2b446ec and both PASS reports at fedd6ca1, each ending END-OF-REPORT), with an identity note that the blobs under allowed paths are unchanged between fedd6ca1 and the gate head 2670f454. Findings close on the independent second review, never on the builder's report; no record says a finding is "addressed/closed" from the builder's own report.

END PART 1 - continued in PART 2.
```

```
PART 2 of 3

ROW M4-T034 D-090-R291: PASS (this task's share)
 - M4-T034's share of step 3 is the law-text captures the R6B/mixed-building check rests on; all 23 new captures carry extraction_status=extracted_draft (source text only) - verified by reading every one; none states a rule, a reading, or a reference-case result.
 - The report (project-control/reports/M4-T034-producer-report.md) draws no conclusion: "No reading of any text for any lot; no verdict on the reviewer's statements." - so the task resolves no rule and claims no independently-calculated example (those belong to other M4 tasks); it does not over-claim its share.
 - git show --name-status of the material commits 3736a22d (46 A + report M) and b35cacfb (report M only) shows only added captures/synced copies and the report - no reference-case or rule file touched.

ROW M4-T034 D-090-R513: PASS (this task's share)
 - I fetched https://zoningresolution.planning.nyc.gov/article-iii/chapter-5/35-31 myself: live sha256 = 8842ac0b0e262c6c72c258bb8ce1a45f5e31e1e031ab961b2108c96b15033b0b, byte-identical to zr-35-31.snapshot.json source.raw_html_sha256 and response_bytes 86986.
 - On that live page I extracted the shared-floor-area text verbatim: "... shared by multiple uses, the floor area for such shared portion shall be attributed to each use proportionately, based on the percentage each use occupies of the total floor area of the zoning lot less any shared floor area." - equal to the capture's verbatim_excerpt; the allocation provision the reviewer names is captured from the official source.
 - The task's share is capture-only: the report states no on/off switch and draws no reading; the "record states the rule" half is M5-T133's share, correctly not claimed here.

ROW M4-T034 D-090-R516: PASS (this task's share)
 - I fetched the ZR 12-10 page myself: live sha256 = 3c7197026d616c459fd38b3cc76ccc607b7891f600e5a1ec00053ceb8574b5bc, byte-identical to the source.raw_html_sha256 pinned in zr-12-10-fully-electrified-building and zr-12-10-ultra-low-energy-building.
 - On that live page I confirmed the eligibility conditions: "existing on December 6, 2023" (present), "Local Law 154 of 2021" (present, both definitions), "ultra-low-energy building" and "net-zero energy" (present) - matching the captures' verbatim_excerpt ("a building existing on December 6, 2023 which complies with Local Law 154 of 2021 ..." and the ultra-low-energy performance/verification text). The terms building and story the definitions rest on are also captured (zr-12-10-building, zr-12-10-story).
 - Capture-only: each is extracted_draft; the report quotes the conditions and offers no "confirm it applies" switch and no reading; the ultra-low-energy label caveat (PDF channel 504/403) is disclosed, text kept verbatim.

ROW M4-T034 D-090-R517: PASS
 - The report section (5) lists each reviewer statement of law with the section the site shows and the capture id holding it, and states "No verdict is drawn on whether any statement is correct." - no verdict given.
 - I independently fetched five official pages and all live sha256 match the captures exactly: 35-31 (8842ac0b...), 25-811 (60f4d916...), 23-24 (4bb1fda5...), 25-211 (aadce9a6...), 12-10 (3c719702...); the texts those statements rest on are present on the live pages.
 - Differences between the site and the reviewer's lead are reported plainly: the "small-lot/small-number waiver" expectation is not in the residential sections (named in 25-30 non-residential, listed not captured); the 25-231 page omits "after" (disclosed as Doubt 6, kept verbatim). The orchestrator's own earlier R517 misreading (23-22 vs 23-52) is corrected in the row with the dwelling-unit statement mapped to 23-22 (FAR by housing kind) and 23-52 (dwelling-unit factor), matching the captures.
 - No existing capture modified: git diff --diff-filter=M over docs/research and services/api/app/_zr_snapshots across both commits is empty; b35cacfb changed only the report.

ROW M4-T034 D-090-R526: PASS (this task's share)
 - The task captures the sections that say WHETHER parking/loading/bicycle requirements apply (group 4, 14 captures <= 20): 25-02, 25-20, 25-211/221/231, 25-80, 25-81/811, 36-21, 36-31, 36-62, 36-70/71/711 - I verified the applicability wording in zr-25-211/221/231 (e.g. 25-231 reduction via 73-433 or 74-52; 25-211 via 73-432 or 75-31; 25-211 "created after December 5, 2024 ... 25-212").
 - Capture-only: the report presents no option as feasible and draws no reading; the "every display carries a line / no option called feasible" binding is the display task's, correctly not claimed here. The report's F1 (25-211 overstatement) and F2 (73-432 wrongly tied to 25-231) were corrected in round 2 to the captured words - I confirmed both against the captures.

W1: MET - the concurrency record project-control/reports/WAVE6-2026-10-07-concurrency-record.md was added at 4ce89144 ("Wave 6 contracted"), which is absent at f111b927 and is an ancestor of the first builder commit c675c469 (git merge-base --is-ancestor passes); it states it was written before any builder was started.

W2: MET - the material files of the three tasks are disjoint. Per task (builder commits): M5-T132 only services/api/app/scenario/three_answers/ + its tests + its report; M5-T133 only docs/measurement-basis/ + services/api/tests/scenario/measurement_basis/ + its report; M4-T034 only the two capture folders + its report. Pairwise intersections of material files = empty (132&133, 132&034, 133&034 all []). The two tasks under services/api/tests/scenario/ write in different folders (three_answers vs measurement_basis). (Observation: M5-T133's first commit d8ad46a8 also carried the orchestrator-only claim-seam control files - project-control gates/state/tasks - which is control-plane bundling, not a builder material-file collision.)

W3: MET - f111b927 is the wave-5 merge (Merge pull request #464, parents 3f08c6c6 and a869abb6) and sits on candidate/D-024-mrl-option-b (local and remotes/origin). Three builders (scenario-optimization-engineer x2, legal-corpus-engineer) per the concurrency record and packets; one branch task/wave6-corrections-after-reviewer-check (PR 466 per the brief; I did not query gh).

W4: MET - every failed review is in its progress log and kept unchanged in its review record, with the re-review by the SAME reviewer (M5-T132: data-contract-verifier G3 and qa-engineer G4; M4-T034: one data-contract-verifier for G3+G4). G2/G3/G4 of each task carry one content identity (M5-T132 content_manifest_sha256 47faffdf...; M4-T034 6bdccc05...). Each literal changed path is bound at HEAD: git ls-tree -r c8b9032 returns a blob for result_ways.py, result_way_conditions.py, result_way_bridge.py, test_result_ways.py, test_result_way_bridge.py, test_result_ways_truth_table.py (M5-T132) and the 23+23 capture paths (M4-T034); the truth-table test file was added to allowed_paths by the one scope-correction entry (honest: a literal name for a file matching the already-allowed pattern test_result_ways_*.py, per DB-181), not a requirement reworded into a pass.

W5: MET - git diff --stat f111b927..c8b9032 -- project-control/directives touches only manifest.json, requirements.json, verification.json and the new source-056-amendment.md; no source-001..055 file changed. The R517 correction (contract commit 4ce89144, requirements+manifest+verification only) corrects the ORCHESTRATOR'S OWN reading with a digest resync and an audit_log entry dated 2026-10-07T20:17:45 ("Row D-090-R517: the orchestrator's reading corrected ..."), and the owner/reviewer words are unchanged - source-055 is byte-identical f111b927..HEAD and its "Seen so far" misreading sentence is still present verbatim. The only owner message recorded is source-056 (message 112, "a quick update", rows R536/R537 pending, bound only to D-090-BOOTSTRAP i.e. no wave task), disclosed by commit cc27ec75 and an audit entry. No change under .claude/ or CLAUDE.md (diff empty).

END PART 2 - continued in PART 3.

PART 3 of 3

Harness: cd services/api && python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/rules/test_zr_snapshot_bundle.py -> 296 passed, 2 skipped, 1 warning; DIRECT exit code 0. Supporting read-only checks I ran: sync_zr_snapshots.py --check -> "byte-identical (156 file(s))", exit 0; docs-vs-synced byte comparison of the 23 new captures -> 0 mismatches; tools/modularity_check.py --check -> exit 0 (warnings only, none for the three_answers result_way modules). Per the brief I did NOT run validate_directive_compliance.py, test_directive_compliance.py, or the full api suite.

Carry-forward condition (blob-level predicate; my eleven verdicts may be stamped at a later head without re-review iff ALL hold):
 - M5-T132: every file under its allowed_paths is byte-identical to its blob at c8b9032419b0e91c35767033860e913826a5571a - specifically services/api/app/scenario/three_answers/result_ways.py, result_way_conditions.py, result_way_inputs.py, result_way_facts.py, result_way_bridge.py, result_way_bridge_overlay.py, and the tests test_result_ways.py, test_result_ways_truth_table.py, test_result_ways_lib.py, test_result_way_bridge.py and the other test_result_ways_*/test_result_way_* files named, plus project-control/reports/M5-T132-producer-report.md.
 - M4-T034: every file under its allowed_paths byte-identical at that head - the 23 captures under docs/research/zr-snapshots/v1/ and their 23 synced copies under services/api/app/_zr_snapshots/v1/, services/api/tests/rules/test_zr_snapshot_bundle.py, and project-control/reports/M4-T034-producer-report.md.
 - AND the eleven requirement rows' text (R258,R521,R522,R523,R524,R532,R291,R513,R516,R517,R526), the D-090 manifest.json, and the sources they trace to (source-035, source-039, source-055) are unchanged at the later head.
 - AND every commit between c8b9032 and the stamp head touches only files under project-control/ and/or lines of docs/DISCOVERY_BACKLOG.md.
 - I tolerate commits that touch none of the above - including the third wave task M5-T133's files (docs/measurement-basis/**, services/api/tests/scenario/measurement_basis/**) and any disjoint peer commit - because they cannot change this task's allowed-path blobs, the eleven rows, the manifest, or the traced sources, and my drive/battery showed the result-way modules depend on none of them.

Required corrections that BLOCK acceptance: none. All eleven rows PASS on primary evidence I reproduced.

Non-blocking observations:
 - M5-T132 G3 note F4 (carried in DB-183): a failing reach/angle closer to its limit than ~5e-7 would still print at the limit - below any measurement the program makes.
 - M5-T132 G4 note F9 (backlog): the "only reach missing" and "only angle missing" rows' reason-token tests would also pass on the "both missing" text; a second resolved_by assertion catches a wrong branch. Acceptable.
 - M4-T034: zr-12-10-ultra-low-energy-building list labels are HTML-markup positions, not confirmed printed glyphs (the 12-10 PDF channel returned 504/403); item text is verbatim - disclosed. zr-36-21 PDF text-check is partial for a few styled table cells that ARE present in the sha256-pinned HTML - disclosed. zr-25-231 keeps a source-page anomaly (a missing "after") verbatim - disclosed.
 - M5-T133's first integration commit d8ad46a8 bundled the orchestrator-only claim-seam control files with that task's material; no builder material-file overlap results.

What I could not check myself:
 - The full services/api suite result claimed in the records (8519 passed, 8 skipped at fedd6ca1) - the brief forbids running it; it remains the producer/orchestrator's claim, not reproduced by me (CI/the orchestrator's single run is its proof).
 - The directive-compliance validator (validate_directive_compliance.py --check) - the second verifier runs it once, per the brief.
 - PR 466 state and prohibited-action evidence (nothing merged/accepted/deployed) via gh - I am read-only and did not query GitHub; the primary evidence I did see is that both task packets show status "awaiting_gate" (not accepted) at this head, consistent with nothing yet accepted.
 - Task M5-T133 (another verifier owns it).

Overall verdict for the two tasks I reviewed: PASS - all eleven rows SATISFIED on reproduced primary evidence; W1-W5 all MET; harness exit 0.

END-OF-REPORT
```
