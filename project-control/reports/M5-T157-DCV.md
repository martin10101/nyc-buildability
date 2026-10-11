# M5-T157 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `2ca8069648691ec2965581e64b7168cdd28b73a7` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R229, R240, R241, R255, R392, R520, R569, R570, R584, R588, R689, R783, R050, R051, R061, R064, R033, R034, R035.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The only correction raised during review (G4 Finding 1, the sibling M5-T159 law-link test red against this task's fixture) was owned by M5-T159, fixed test-only at 0330d598, and re-verified PASS; it did not change any M5-T157 allowed_path file. The two G1 advisories (cite the Special-Downtown-Brooklyn snapshot as an NB-05 evidence item; record the DB probe against OQ-5) and the G3/G4 advisories are non-blocking record-provenance notes, deliberately not applied to avoid churn.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 06:25 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T157 (directives D-090, D-093 and D-094, 19 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier, read-only). This is a software/control-plane verification, not a human or professional legal review; the ZR captures ship as unreviewed drafts under ADR-007 and every unit figure here stays a Conditional ceiling, never a confirmed entitlement.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = 2ca8069648691ec2965581e64b7168cdd28b73a7 on branch task/wave23-density-zoning-lot; I read every artifact through `git show 2ca80696:<path>`.
 - Its parent is ced5bd73 (the submit/gate head); `git diff --name-only ced5bd73 2ca80696` changes only gates/reports/state/task files — NO allowed_path file differs, so the frozen head carries the reviewed content.

(2) ROWS

ROW D-090-R229 — PASS
 - decide_special_density (special_density_geography.py) returns NOT_KNOWN for an unread/untrusted column, a joint-interest-area or unrecognised cd, and a Manhattan-core cd contradicted by a non-Manhattan borough; NOT_IN needs BOTH Manhattan-Core-no AND every special-district column read with none "DB".
 - I ran tests/scenario/three_answers (111 passed incl. test_special_district_columns_not_read_is_not_known, test_nothing_read_is_not_known, test_contradiction_cd_105_borocode_3_is_not_known); "not read" never becomes "no".
 - Nothing stays open.

ROW D-090-R240 — PASS
 - A missing statement is NOT_GIVEN and is never filled; with no readable record the standard limit stays withheld (test_user_statement_never_overrides_the_record_s5 with special_density_statement=None still yields the record-driven conditional, not a default).
 - The invariant test parametrized over all DensityKnowledge proves a withheld state is shown as withheld, never defaulted.
 - Nothing stays open.

ROW D-090-R241 — PASS
 - tests/api/test_results_read_law_examples.py header states every expected value comes from reference cases under docs/reference-cases/R6B/cases (real-lot#L6 = 29), driven THROUGH the route, "never from the program's saved output"; the suite passed in my run.
 - calc-legal-dwelling-unit-limit.md line 63 cites real-lot#L6 = 29 as the independent basis; a saved result is not used to justify a shown value.
 - Nothing stays open.

ROW D-090-R255 — PASS
 - test_user_statement_never_overrides_the_record_s5 (read + passed): the record decides; a statement that disagrees withholds with gap_kind "missing_information" naming both sides; the statement is never stored as a recorded fact (asserts no "density"/"states" fact).
 - The conditional 29 carries no KIND_USER_STATEMENT condition; the assumption text is the zoning-lot record condition, not the user's claim.
 - Nothing stays open.

ROW D-090-R392 — PASS
 - Journey fixture: legal_unit_limit_standard value 29.0 way=conditional while unit_estimate.status = not_available — the legal cap is a distinct figure from the apartment estimate.
 - ZR 23-52(b) .75 rounding is applied only to the legal limit (20,150/680=29.63→29, which I reproduced); the estimate path is untouched/withheld.
 - Nothing stays open.

ROW D-090-R520 — PASS
 - The standard-residences ceiling shows as a Conditional ceiling value 29.0 (fixture legal_unit_limit_standard way=conditional), checked against the R6B reference case real-lot#L6=29 before being repeated; the realistic estimate (not_available) does not replace it.
 - result_ways._unit_qualifying_affordable_way and _unit_qualifying_senior_way currently withhold the 35-unit affordable and the senior cases as honestly-labelled work owed ("does not work out … yet, so it is not known"; senior "no factor … pending check"), consistent with R229/R240 — neither is dropped or replaced.
 - Open for later work: the qualifying-affordable (35) and qualifying-senior option ceilings are not yet computed/shown; this task's share delivers the standard 29 conditional ceiling.

ROW D-090-R569 — PASS
 - Legal limit and apartment estimate are distinct outputs with their own key/label/place in the fixture; SVG note and DXF line 364 describe only the legal limit as "a conditional ceiling on the zoning lot," with no apartment-count number shown under it.
 - G3 independently found no wording merging the two; unit_estimate is not_available so no cross-labelling occurs.
 - Nothing stays open for this share (when both appear they stay distinguished per the structure).

ROW D-090-R570 — PASS
 - Withheld rows carry no number anywhere: fixture shows building_option/floor_stack/unit_estimate/coverage_by_portion status not_available with no value; the invariant/truth-table tests cover every withheld state; SVG/DXF carry no substitute number for them.
 - A disagreeing statement withholds the standard limit (Withheld, missing_information) and no older/substitute 29 reappears (test_user_statement_never_overrides_the_record_s5).
 - Nothing stays open.

ROW D-090-R584 — PASS
 - No flag/switch changed: r6b_dwelling_units.rule.json code_identity (404179f2) is byte-identical across NB-05 revision 1 and 2; it is not in files_changed and lives under forbidden rulesets/.
 - files_changed contains no config.py, render.yaml, package.json or .github/ change; the evidence map's "what_did_not_change" (no setting/flag/report-page code) matches the diff.
 - Nothing stays open.

ROW D-090-R588 — PASS
 - The change only ADDS a shown conditional figure (legal_unit_limit_standard) and removes no report page or development option; the apartment estimate and other option outputs remain (status not_available = work owed, not removed).
 - Diff scope is confined to the special-density decision, tests, fixture, snapshots, register and NB-05; no narrowing of the full-report goal.
 - Nothing stays open.

ROW D-090-R689 — PASS
 - NB-05 revision 2 reuses revision 1's evidence E1–E4 and worked example (from M0-T190) and maps the regression cases to named tests; it does not re-run completed research.
 - The G1 revision-2 review (in NB-05 review.agent_reviews and the review record) identifies the remaining gap (OQ-5 Appendix A token) as an open item.
 - Nothing stays open.

ROW D-090-R783 — PASS
 - The shown unit limit carries exactly one status: way="conditional" → the Conditional label; calc doc states "conditional ceiling - never settled"; nothing labels the 29 Verified.
 - "verified" appears in the fixture only inside withhold reasons ("Needs verified zoning-lot boundaries"), never as a label on an output; withheld rows carry their withheld status.
 - Nothing stays open.

ROW D-093-R050 — PASS
 - The G1 data-contract-verifier return (frozen in the review record and in NB-05 agent_reviews rev 2, verdict "agrees") opened the ZR 12-10 and 23-52 captures and the F08 PLUTO dictionary, worked 20,150/680 and the boundaries BEFORE reading code, and ran a live Socrata/ArcGIS probe — independent of the builder's explanation.
 - I independently reproduced the same: opened the three ZR 12-10 snapshots + ZR 23-52 and re-derived the arithmetic, corroborating the review.
 - Nothing stays open.

ROW D-093-R051 — PASS
 - Boundaries are tested, not formula-copied: 0.75 rounding both sides (29.75→30, 29.747→29, 15.75→16 — all reproduced by me), all record×statement combinations, and the engine/shown invariant; mutation proofs recorded by builder and G4.
 - The made-up lots are explicitly "never a real lot" (law-examples header) and the 29/16 figures stay Conditional, never relabelled as a verified real-site result.
 - Nothing stays open.

ROW D-093-R061 — PASS
 - Northern Boulevard Q5 answered yes: the special-density geography is resolved from the record (Queens cd 411, spdist null → not in one, confirmed live for BBL 4073340070) while the unit count stays Conditional on the zoning lot and lot area (NB-05 conditions; always-present zoning-lot condition in the fixture).
 - result_ways emits the standard limit as conditional with that zoning-lot condition first.
 - Open for later work: the property-specific zoning-lot confirmation (which tax lots make up the zoning lot, NB-01) is added by DB-232 (M5-T158) in the same wave; only the generic always-present condition is present now.

ROW D-093-R064 — PASS
 - The review records show reviews ran in read-only sessions: G4 in a /tmp detached worktree created and removed, mutations restored; G1/G3 via git plumbing; "No ports touched."
 - No owner session was cleared; ports 3000/3001/8000 were not stopped.
 - Open caveat: this rests on the reviewers' attestations in the record (I cannot observe the sessions directly) — see section (6).

ROW D-094-R033 — PASS
 - I opened the primary captures: zr-12-10-special-density-areas verbatim = "(a) the Manhattan Core; and (b) the Special Downtown Brooklyn District"; zr-12-10-manhattan-core = "Manhattan Community Districts 1,2,3,4,5,6,7 and 8"; zr-12-10-special-downtown-brooklyn-district = designated "DB".
 - The three LawCapture digests pinned in special_density_geography.py (e8029ab3…, 2c04132a…, ae66c93e…) EQUAL sha256 of each snapshot's verbatim excerpt (I recomputed all three).
 - Nothing stays open (the exact PLUTO token enumeration is a separate corroboration, OQ-5, not this external fact).

ROW D-094-R034 — PASS
 - decide_special_density resolves the source fact from the record (PLUTO cd/borocode/spdist columns) rather than a user declaration; the Queens benchmark reads NOT IN (cd 411, spdist null), confirmed live against official PLUTO.
 - A record that cannot be read is withheld as "not known" distinct from a legal unknown, and the implementation limitation (Appendix A token not captured, OQ-5) is recorded separately in NB-05 searches[]/conditions, not promoted.
 - Open: only the recorded OQ-5 implementation limit, appropriately carried as a condition.

ROW D-094-R035 — PASS
 - The 29 is way="conditional" with an always-present unchecked zoning-lot condition ("the city's special-density record is kept per tax lot, while the dwelling-unit limit is set on the zoning lot (ZR 23-52)"); "entitlement" appears in zero emitted texts, fixture, SVG, DXF or calc doc; calc doc says "never settled."
 - Resolving geography does not establish the limit: zoning-lot basis/area/use/exemptions remain conditions.
 - Open for later work: DB-232 (M5-T158) adds the property-specific zoning-lot condition; the 29 stays Conditional until those inputs are confirmed.

(3) BINDING B1–B5
 - B1 PASS: contract commit 9fa99590 appended "M5-T157" to all 12 D-090 rows and all 4 D-093 rows (`git show 9fa99590 -- …requirements.json | grep -c '^+.*M5-T157'` = 12 and 4); 687c8719 appended it to all 3 D-094 rows; `git log -S` shows 9fa99590 is the only commit touching the D-090 binding. No row text changed: I diffed the 19 rows' `text` between their binding/capture commit (9fa99590 for D-090/D-093, 5ae716eb for D-094) and the frozen head — all identical.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) equals each manifest's requirements_content_digest_sha256 (160eac6f…, 2a6e30d6…, 3c446844…); `validate_directive_compliance.py --check` exit 0.
 - B3 PASS: each verification.json has exactly one M5-T157 row with applicable_requirement_ids = the cited ids (12/4/3), producer backend-engineer, verifier "", every requirement state "pending", reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs(packet) → ok=true, applicable_ids == cited_ids (all 19), missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: because applicable == cited with no missing, nothing else across the active directives applies to M5-T157 uncited. Gates: G0 PASS (orchestrator, ea335844), G1 PASS (data-contract-verifier), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) — G1–G4 all recorded at ced5bd73 (one content identity); G4 reached PASS after its required correction (the T159 sibling test) cleared, delta PASS at 0330d598; carried forward because no allowed_path file changed ced5bd73→2ca80696.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided the blob-level predicate holds: every file in M5-T157's allowed_paths (the 42 paths in the packet, incl. the 41 material files + NB-05) has the same git blob id at the stamping head as at 2ca80696, AND in the three requirements.json the 19 bound rows' `text` and their `applicability.task_ids` still contain M5-T157 unchanged, AND each verification.json still carries the M5-T157 row with these ids.
 - BROAD DISJOINT-PEER TOLERANCE: later commits MAY touch any other file — other tasks' sources under services/, apps/, packages/, docs/ (including other evidence records), their packets, gates, reports and directive bindings, and ledger state — plus this task's own acceptance records (its gates/reports/verification.json/state.json) and a main-line merge that changes none of the predicate's files. None of these voids the verdict.

(5) REQUIRED CORRECTIONS
 - None. The only correction raised during review (G4 Finding 1, the sibling M5-T159 law-link test red against this task's fixture) was owned by M5-T159, fixed test-only at 0330d598, and re-verified PASS; it did not change any M5-T157 allowed_path file. The two G1 advisories (cite the Special-Downtown-Brooklyn snapshot as an NB-05 evidence item; record the DB probe against OQ-5) and the G3/G4 advisories are non-blocking record-provenance notes, deliberately not applied to avoid churn.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The reviews' session-isolation attestations (D-093-R064): I confirmed the review records state /tmp detached worktrees and "no ports touched," but I cannot directly observe that the owner's live session/ports were untouched — I relied on the frozen review returns.
 - Live PLUTO/ArcGIS reachability and the exact Appendix A token (OQ-5): no authoritative enumerated list is captured in the repo; I verified ZR 12-10 says the district is designated "DB" and trusted the G1 live Socrata probe (spdist1='DB' for Downtown Brooklyn CD 302) — appropriately kept open in NB-05.
 - Full api and web suites: forbidden by my brief; I ran only the focused special-density suites (111 passed), the register check (PASS) and research_record_check (PASS, NB-05 review_state=current) — the full suites are CI's job at the accepted head.
 - apps/web TS/vitest behaviour: not run here; the five changed web test files are in allowed_paths and were reported green by G4 (71 passed) and the producer.
 - I did not run tools/test_directive_compliance.py (brief-forbidden; the registry is large).
END-OF-REPORT
```
