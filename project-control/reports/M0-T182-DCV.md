# M0-T182 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `65053cddb07c613ec2f2ab8fdd1857857ddee17d` (branch `task/M0-T182-source-map-js-one-time-age-exception`, review copy
`/root/project/rv-446`). Directive D-092. The verifier was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R004, R006, R007, R008, R012, R013, R014, R015.

## Verdict: PASS. No required correction.

The verifier writes "SATISFIED" for a row that is met; the registry's word for that state is PASS, and the verification rows use it.
Its carry-forward condition (section 7 of the return) is the rule for stamping these verdicts at a later head: the nine named blobs
byte-identical and every later commit confined to `project-control/**`.
One observation of the verifier, answered: the blocker file B-029 is not on this branch; it is on the handoff branch (pull request
#444) and is updated there after the merge.

The verifier's return follows unchanged (received 2026-10-06T06:33:26.880Z; copied from the session transcript by script, line 887).

---

DCV REPORT — directive D-092, task M0-T182, PR #446 (independent, read-only)

(1) HEAD VERIFIED
`git -C /root/project/rv-446 rev-parse HEAD` = 65053cddb07c613ec2f2ab8fdd1857857ddee17d; working tree clean.

(2) A1–A8
A1 PASS. Extracted raw texts from the transcript: msg83 sha=c4eff5da…, reply sha=8ccd0f39…, msg84 sha=3c9bde9b… — all three equal the stated digests. msg83 raw begins with two "\n"; block == raw[2:]; reply/msg84 blocks == raw. source-001.md sha256 = 3371a159… == manifest sources[0].
A2 PASS. Every quoted fragment in R001–R016, plus the R012 reply quote ("For the exception I would need your explicit approval…"), is an exact substring of its attributed text.
A3 PASS. Forward: every sentence of msgs 83/84 maps to a row (R001–R013). Reverse: no row widens/narrows; interpretation is labelled "ORCHESTRATOR'S READING" (R009/R010/R012).
A4 PASS (key judgement). Msg83 held restrictions "until I explicitly approve a specific proposal"; the reply described exactly ONE proposal and asked for "explicit approval of that exact change: this one version, that fingerprint, that expiry, the policy edits and the clean-up." Msg84 "Go ahead update it only this 1 time" is that explicit, one-time approval. R012 reads "it" as the vulnerable package and binds the approval to the reply's proposal — a fair, not inflated, reading. The built change matches item-for-item: exact pin 1.2.2; an age-checker rule bound to name+version+integrity+publication-instant; the .npmrc name exclusion; S1–S8 tests; policy edits; and M0-T183 as a separate backlog clean-up. Nothing exceeds the reply: binding the publication instant makes the exception NARROWER, and the clean-up is only created, not performed.
A5 PASS. Rows atomic; classifications all within vocab (authorization/obligation/return/prohibition/hold/sequencing).
A6 PASS. requirement_count=16, locked=16. Recomputed id digest 4944084b… and content digest 777d9897… both MATCH manifest; source digest 3371a159… MATCH. index.json has the D-092 entry (affected_tasks M0-T182+M0-T183, right manifest path). affected_tasks and scope.task_ids = [M0-T182, M0-T183]. verification.json has provisional rows: M0-T182 (the eight ids), M0-T183 (R016). amendments [].
A7 PASS. Live registry.npmjs.org source-map-js 1.2.2: integrity sha512-KGj/8Y43…P3Vw== and time 2026-09-30T14:08:09.382Z — exactly match source-001.md, the lock, OWNER_AGE_EXCEPTIONS, and the policy table. Age at approval 487485 s = floor(msg84 05:32:54.564Z − publish) (checks). Expiry 2026-10-07T14:08:09.382Z = publish + 604800 s.
A8 validate_directive_compliance.py --check: DIRECT exit 0. test_project_control.py: 23 groups passed, exit 0. test_directive_reminder.py: 12 tests OK, exit 0. (Did not run test_directive_compliance.py.) Also: node --test 50/50; modularity_check --check exit 0 (gate not flagged).

(3) EIGHT TASK ROWS — evaluate_task_refs(M0-T182) ok=True, applicable==cited==R004,R006,R007,R008,R012,R013,R014,R015.
| ID | Verdict | Primary evidence (reproduced) |
|---|---|---|
| R004 | SATISFIED | No .github change in e97bf405..65053cdd; exception branch sits AFTER host/integrity/timestamp checks (dependency_age_gate.mjs 240–299); workflow run 37421376443: npm audit "found 0 vulnerabilities"/"total==0 across all severities", age gate RESULT PASS, npm-CLI advisory PASS; independent G3/G4 (code-reviewer) + G5 (security-reviewer) PASS; node --test 50/50. |
| R006 | SATISFIED | git diff touches no workflow file; no existing check removed/reordered (added Kind, frozen list, matchOwnerAgeException, one branch, reporting); MIN_AGE_SECONDS=604_800 unchanged; PR rollup 47/48 success, 0 fail. |
| R007 | SATISFIED | decide() computes ageSeconds from registry time + injected now (mjs 280–290); matchOwnerAgeException only COMPARES registry instant to recorded, never substitutes (mjs 116–127, 294–305); test S6 (wrong/missing/malformed/future → too_new/missing_timestamp). |
| R008 | SATISFIED | No audit step/threshold/suppression changed; cleared by moving to fixed 1.2.2 (GHSA-68fv-2mgg-jv7q range >=1.0.0,<1.2.2); workflow run audit total==0; age-only branch unreachable before integrity. |
| R012 | SATISFIED | Msg84 verbatim approval; built as ledger M0-T182 under G0/G2/G3/G4/G5; change == reply's proposal; lock diff only node_modules/source-map-js 1.2.1→1.2.2 (integrity = recorded). |
| R013 | SATISFIED | OWNER_AGE_EXCEPTIONS = one frozen entry (mjs 98–106); S8 deep-equals one entry, asserts list+entry frozen and push/mutate throw; policy "no agent may add an exception; each needs its own owner approval+directive+G5"; S3/S4 other version/name → too_new. |
| R014 | SATISFIED | Material diff = package.json pin, .npmrc exclusion, gate rule, S1–S8 tests, policy, producer report only; lock by workflow commit 246bcebf (github-actions[bot]), not hand-edited; no forbidden path. |
| R015 | SATISFIED | OK returns at age>=604800 BEFORE the branch; matcher requires 0<=age<604800; S2: 604799→OWNER_AGE_EXCEPTION, 604800→OK; S8 matcher null at 604800; expiry = publish+604800 = 2026-10-07T14:08:09.382Z. |

(4) OTHER ROWS (one line each)
R001 SATISFIED — reply "I changed nothing"; first D-092 commit a51132bd post-dates msg84.
R002 SATISFIED — reply "A mature update cannot remove the package" answers it.
R003 SATISFIED — reply "A narrow exception is workable" assesses the 1.2.2-only change.
R005 SATISFIED — reply states expiry + how the change passes review/CI.
R009 SATISFIED (git) — a51132bd parent=e97bf405, dated 05:44 (> msg84 05:32), touches only project-control; no apps/web change before producer commit 8fe57ca0. (Transcript-window tool-scan repeatedly blocked by the read-only guard; git is authoritative.)
R010 SATISFIED — manifest/scope lift only the approved exception; "NO other restriction lifted."
R011 SATISFIED — reply gives recommendation (wait), risks, approval needed, time comparison.
R016 SATISFIED as planned, NOT done — M0-T183 exists (backlog, 0%, cites R016, allowed_paths=.npmrc+gate+test+policy); .npmrc and gate comments name M0-T183; not claimed/accepted.

(5) PART C — nothing refusable.
- Nothing merged: PR #446 OPEN, head 65053cdd; 47/48 checks SUCCESS, 1 web-e2e IN_PROGRESS, 0 FAILED.
- No advisory waived, no check weakened, no workflow file changed (verified in diff).
- Exactly one frozen exception entry; no standing permission (policy requires per-entry owner approval).
- No gate recorded by its own producer: G0/G2 orchestrator, G3/G4 code-reviewer, G5 security-reviewer; producer=frontend-engineer. Gate reviewed_sha=153424da (G2–G5), content_manifest 416ce200 identical; material byte-stable 653b254d→65053cdd.
- PR body: no sentence false at this head (states nothing merged, B-029 open, clean-up not done, DCV result not stated, checks pinned at 653b254d with later commits project-control-only).
- Observation (not a correction): no B-029 blocker JSON exists (blockers stop at B-028); "B-029" is a reference label meaning the advisory merge-hold, still in effect since nothing is merged — the PR sentence is substantively true. Before accept, confirm no other OPEN blocker's affects/detail names M0-T182/M0-T183 (standard accept-time scan).

(6) REQUIRED CORRECTIONS: none.

(7) CARRY-FORWARD CONDITION
These verdicts may be stamped at a later head iff the seven material blobs (80a8e0c3 package.json, 5b6bc11e package-lock.json, 939062d6 .npmrc, c6c0268d gate, 42110cc9 gate test, b848d8a3 policy, 08d77e3d producer report) and D-092 source-001.md (8a4822d7) and requirements.json (dcbd5380) are byte-identical at that head, and every commit after 65053cdd changes only project-control/**. A later unrelated commit IS tolerated only if it is confined to project-control/** and alters none of those nine blobs; any change to a material/directive blob, or any change outside project-control/**, voids the carry and requires re-review. Because G4 is live-check-pinned, the merge step must additionally re-confirm the full check rollup COMPLETED/SUCCESS on the final head (one web-e2e check is currently IN_PROGRESS, not failed).

(8) DCV: PASS
END-OF-REPORT
