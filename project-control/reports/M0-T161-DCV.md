# M0-T161 — directive-compliance verification (directive-compliance-verifier "dcv-m0t161", read-only)

> Transmission history: pinned at 6314a25c, delivered as six SendMessage parts (the up-front restamp predicate, then
> 1/5..5/5) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). The DCV sandbox refuses powershell.exe, so the dynamic AS-4 evidence is the orchestrator's harvest run (parser 0
> errors; run_ps_tests 8 files passed), corroborated by both reviewers. D-088-R003 is satisfied for this task's share (the
> procedure and its safeguards); its runtime closure and B-026 stay OPEN until the owner runs the helper.

---

M0-T161 DCV (D-088) — RESTAMP PRE-AUTHORIZATION (up front). Started at live HEAD 6314a25c.

BLOB-LEVEL PREDICATE. My PASS restamps to any target head WITHOUT re-review as long as ALL of these hold at the restamp target:
- HEAD:tools/controller_update/commission_lanes.ps1 == a39ba5bb (a39ba5bbad2b3f87ba24ac55b6c8bffbe488fa22)
- HEAD:tools/controller_update/ps_tests/test_commission_lanes.ps1 == f0d69ef1 (f0d69ef1e4bf9b17303dbf94c3f82ca220ea0a61)
- HEAD:project-control/reports/M0-T161-owner-guide.md == db29c32a (db29c32a7cb435c27d7ca50cbfbb5ad8cd8415cb)
- HEAD:project-control/reports/M0-T161-producer-report.md == f2fd87cd (f2fd87cda5a73042d48afb78d5621c3828692cb1)
- project_control._task_git_identity(dr, task) == reports/M0-T161.json content_manifest_sha256 == 82864416 (8286441633db9f2516b3ae3377e62af2e4264cc855a58d6d179f7f9f26e049b6), and the G2/G3/G5 gate records carry that same manifest.

If any of the four blobs or the identity manifest changes, the restamp is VOID and a re-review is required.

DISJOINT-PEER TOLERANCE (broad). None of the following void the restamp; I authorize the reviewed_sha to advance to the live HEAD across any of them:
- other tasks' files, gate records, material commits, and accepts landing between freeze and record;
- other directives' bind/append (requirements.json applicability edits) that do not touch M0-T161's four blobs or its identity;
- the orchestrator writing MY v2 verification rows for D-088/D-024/D-066 with digest resyncs and audit_log entries;
- docs/DISCOVERY_BACKLOG.md rows and contract-seam sweep lines;
- lifecycle-only packet/state changes for M0-T161 (status/progress/gate stamps) that leave the four blobs and 82864416 byte-stable.

Verified so far: the four blobs are byte-identical at reviewed_sha 158b5bca and at HEAD 6314a25c. 158b5bca is the material cherry-pick (25981c08 from wt-m0t161); 1f4933e8 is the submit+G2 ledger seam.

Full requirement rows, findings, and verdict follow in subsequent parts. Do not act on a verdict until the final line lands.

---

M0-T161 DCV (D-088) — FINAL REVIEW, PART 1/5: identity, gates, lifecycle, applicability.

LIVE HEAD at start: 6314a25c (as expected).

FROZEN IDENTITY — verified on primary evidence (reproduced myself):
- _task_git_identity(reg, task) at HEAD = 8286441633db9f2516b3ae3377e62af2e4264cc855a58d6d179f7f9f26e049b6.
- == reports/M0-T161.json content_manifest_sha256 (82864416). == G2, G3, G5 gate content_manifest_sha256 (all three carry 82864416).
- The four task blobs at HEAD: commission_lanes.ps1 a39ba5bb, test_commission_lanes.ps1 f0d69ef1, owner-guide.md db29c32a, producer-report.md f2fd87cd — byte-identical at reviewed_sha 158b5bca and at HEAD. git diff 158b5bca..HEAD on all four = empty (both reviewers independently confirmed the same).

MATERIAL vs SEAM: 158b5bca is the material cherry-pick (25981c08 from wt-m0t161; 4 task files). 1f4933e8 is the submit+G2 ledger seam (gates/state/task only, no material). Evidence-map labels material_commit 158b5bca for round 2 — correct (the cherry-pick, not the seam).

REQUIRED-CORRECTIONS LIFECYCLE — lawful:
- Round 1 material b27fc89b: G3 PASS (cr-m0t161 02:50) + G5 PASS (sec-m0t161 02:51), both PASS-with-required-corrections (advisory).
- progress --status rework (02:55) recorded the blocking corrections; producer reworked (25981c08) → cherry-picked to 158b5bca (23:28).
- Re-froze: G2 self-check at 158b5bca (03:36), submit at 158b5bca (03:36).
- Delta re-attestations at 0c76b136: G3-rework PASS (03:45), G5-rework PASS (03:46) — same reviewers, both carry manifest 82864416, both verdict lines "PASS". Transitions in_progress→awaiting_gate→rework→in_progress→awaiting_gate (no forbidden direct jumps). No material edit after the round-2 submit (blobs byte-stable to HEAD), so frozen submission identity is intact.

APPLICABILITY — applicable == cited (reproduced via registry):
- directive_registry.load_registry().evaluate_task_refs(M0-T161): ok=true, applicable_ids == cited_ids == [D-024-R287, D-066-R001, D-088-R003, D-088-R004, D-088-R007]; missing=[], invalid=[], unresolved=[].
- D-088 R001/R002/R005/R006 bind to D-088-BOOTSTRAP only, NOT M0-T161 — correctly excluded.

Requirement rows follow in parts 2-3.

---

M0-T161 DCV — PART 2/5: requirement rows (primary evidence I reproduced from source).

D-088-R003 (stand up lanes 4-5 as byte-identical certified instances) — SATISFIED (as to what the task delivers; runtime closure OPEN, see F5).
Primary evidence, commission_lanes.ps1:
- Own folders + mrl: Step-Propagate L513-521 creates C:\SupervisorController4/5 tools\agent_supervisor and mrl folders.
- Wrapper from lane 3, lane-specific values ONLY: New-LaneWrapperContent L615-640 derives from $Lane3Wrapper (C:\SupervisorController3\autostart-launch.ps1), replaces checkout key/path/log names/labels only; ACTIVE-TASK block blanked to NOT-YET-FED (Set-NotYetFedBlock L642-681).
- Checkout key from the controller's OWN function: Get-CheckoutKey L198-211 calls durable_state.checkout_key via python from wt-controller-src (never re-implemented).
- Proves all five identical + verify-controller from each: Assert-SameTree all five vs wt-controller-src L546-550; Step-VerifyController L553-568 loops all five lanes + wt-controller-src, STOP unless "controller verified, including the external config.toml binding".
- Never modifies config/model/manifest except 5.4: Invoke-UpdatePhase raw-hash snapshot L360-361 + STOP-on-change L373-380; manifest written only by Step-RecordManifest (5.4).
- G5 /MIR wipe safety: Get-TreeFileCount precondition L523-532 STOPs before any robocopy unless source holds exactly 204 files.
Tests: §4 wrapper-diff (region diff proves every out-of-block diff is lane-specific), §6 precondition, §10 immutability.
OPEN until owner runs -Phase update: actual C:\SupervisorController4/5 creation, the byte-identical tree lines and verify-controller PASS from each, and the unchanged config/manifest digests are produced only at owner run-time. Machine sweep confirms lanes 4/5 ABSENT today and B-026 open. This is by task design (producer changes nothing); the procedure + safeguards are correct and complete.

D-088-R004 (faithful fail-closed section-5 transcription; canary; lanes 2-5 after, ≥60s; fresh manifest + first-start-only repin; STOP halts) — SATISFIED.
- Faithful transcription verified against M0-T159-recertification.md §5.0-5.12: all pinned values match — candidate a3f24ff3 (L76), tree 82432361 (L77), subtree 9c0b14ea (L78), wrong-subtree 11d43515/cfc3d22c refusal (L79, L432-434), manifest STOP "147 55dc7135..." (L80,L478), chain STOP "2.1.281 946eb509..." (L86,L780), config raw 610ce9d5 (L81,L324), counts 204/147/146 (L88-90, asserted L440/L478/L495-502). Every §5 STOP present (STOP-table cross-checked).
- Canary: Get-LaneMode L696-711 forces lane 1 supervised; --max-cycles 1 (L789); canary WAIT_FOR_OWNER note L796-798.
- Approve: Invoke-ApprovePhase L806-845 (pending-approvals → verify digest is held → resume → re-start Repin=$false).
- ≥60s: Start-LaneSpacing between starts L1004-1007. Fresh manifest per start: mrl_launch_draft --force L759-772. Repin first-start-only: L790 (true in lane/lanes first start), false on approve re-start L842.
- STOP halts everything after: every STOP is throw → dispatcher catch → exit 1 (L1035-1038); "only after canary" enforced by owner-guide step 5 + orchestrator go-ahead. Tests §2a/2b/2c prove a STOP halts all subsequent steps and prevents the start.

---

M0-T161 DCV — PART 3/5: requirement rows (continued).

D-088-R007 (owner guide: simple English, exact '!' lines in order, correct canary steps) — SATISFIED.
Primary evidence, project-control/reports/M0-T161-owner-guide.md:
- Plain English, five steps, each an exact '!' one-liner in order: Step 1 -Phase check (L21); Step 2 -Phase update (L34); Step 3 -Phase lane -Lane 1 -Worktree <folder> -PacketId <task-name> (L48); Step 4 -Phase approve (without digest, L65) then again with -PromptDigest <digest> (L81); Step 5 -Phase lanes -PlanFile <plan-file> (L99), gated on "wait for the assistant to say go ahead" (L9, L93).
- "What good looks like" per step (CHECK PASSED / UPDATE PASSED / started DETACHED / approved + canary re-started / LANES STARTED); STOP handling ("stop and tell the assistant"); "why fewer than five loops run" section (L120-126).
- Canary steps correct and match the script: the first approve STOPs on purpose showing the digest, then re-run with it; guide quotes the STOP line byte-exact to commission_lanes.ps1 L823 ("STOP [approve]: pass -PromptDigest <the digest printed above> to approve the held prompt"). The round-1 G3 F2 step-4 misdirection is fixed (step 3 note now says it does NOT print the code). G3 reviewer independently confirmed the byte-exact quote and end-to-end correctness.

D-024-R287 (admission → recertification → install/manifest before any repin; no silent version acceptance) — SATISFIED.
Primary evidence, commission_lanes.ps1:
- Admission gate: Invoke-CheckPhase L293-298 STOPs unless source_binding pins the recertified candidate a3f24ff3 (Get-BoundCommit L171-182).
- Install + record-manifest + verify BEFORE any repin: update phase runs Step-Install (5.3) → Step-RecordManifest (5.4) → Step-VerifyManifest (5.5) with full identity asserts; repin (--repin-cli-identity) is added only at a lane's first start (L790), which runs in the separate lane/lanes phase AFTER update.
- No silent version acceptance: the launch-manifest chain STOP L780-783 requires exactly "2.1.281 946eb509..." before any start; version 2.1.281 is a pinned constant ($ClaudeVersion L87, $ChainCheckStop L86).

D-066-R001 (code-graph navigation block present in the packet) — SATISFIED.
Primary evidence:
- The packet carries the navigation block: tasks/M0-T161.json inputs[7] "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at this contract seam, 832 files / 17984 nodes / 7700 edges)" — states no python module imports tools/controller_update, names the read-only existing scripts/tests, and instructs query.py --no-regen before sweeps; the checkout key must come from durable_state.checkout_key at run time.
- The helper honors it (graph advisory, verified in source): Get-CheckoutKey L198-211 and Get-RuntimeDirFor L184-196 call durable_state through python from wt-controller-src rather than re-implementing.

---

M0-T161 DCV — PART 4/5: findings and prohibited-action sweep.

FINDINGS (all non-blocking):
- F1 (INFO): I could NOT reproduce the AS-4 dynamic run — this DCV sandbox blocks ALL powershell.exe (writes and even parse-only ParseFile). I rely on the orchestrator-captured harvest evidence (evidence-map [ORCH-HARVEST rework] at 158b5bca: "parse ok: 0 errors in both files"; run_ps_tests exit 0, "8 test file(s) passed") per the evidence-capture division of labor, corroborated by both reviewers (each reported parser-clean + run_ps_tests green and, crucially, verified the new assertion strings against the REAL update_controller_from_candidate.ps1 output L697-700/790-791 to prove no false-STOP). I verified the test CONTENT directly by reading test_commission_lanes.ps1 (11 sections: parse, 5.4/5.11/5.1 STOP-halt, no-write, wrapper region-diff, plan validator, /MIR precondition, wrong-subtree, canary-mode, approve, immutability, linked-worktree/glob/packet-id). Every machine write is stubbed and dispatch is skipped via -LoadOnly.
- F2 (MINOR, doc-only): producer-report section-2 line numbers reflect round-1 material and drifted after round-2 growth (e.g. cites Invoke-CheckPhase L265-321; actual L289-349; Start-LaneFirstLaunch L657-719; actual L731-800). The R2.2 anchors are current. Logic/functions all present and correct as I verified. No requirement impact.
- F3 (MINOR fidelity): two recert expected-OUTPUT items aren't separately asserted — 5.2 "controller 200 file(s)" (helper gates on BACKUP VERIFIED + proves lanes 2/3 byte-identical) and the 5.6 post-robocopy __pycache__/.pytest_cache removal loop (helper uses robocopy /XD exclusion + tree-compare that excludes those dirs). Neither is a §5 STOP; both are covered/justified. Note only.
- F4 (justified deviations, disclosed): (a) lanes 4-5 stand-up extends recert 5.6's 2-3 mirror per D-088-R003; (b) free-disk STOP in check per D-088-R006 (1.0 GiB floor); (c) detached Start-Process starts vs recert foreground start, per packet DESIGN so lanes survive the session. Nothing in §5 dropped/reordered.
- F5 (R003 runtime OPEN): full R003 closure (lanes 4/5 actually stood up, verify-controller PASS from each, unchanged digests) awaits owner -Phase update. By design.

PROHIBITED-ACTION SWEEP (read-only; all clean):
- Not accepted: task status awaiting_gate (tasks/M0-T161.json); no accept.
- No verification row: 0 mentions of M0-T161 in D-088/D-024/D-066 verification.json.
- Not on main: material 158b5bca only on candidate/D-024-mrl-option-b; NOT ancestor of origin/main or local main.
- PR #241: state OPEN, mergedAt null, headRefName task/M5-T002-scenario-endpoint, updatedAt 2026-08-20 — untouched.
- B-026: OPEN (owner has not run commissioning).
- Controller untouched: C:\SupervisorController/2/3 exist with mtime Sep 23 17:11 (predates this task, created 2026-09-25); SupervisorController4 and 5 ABSENT (stand-up not run). SupervisorBackup unchanged (Sep 6). Consistent with "producer changed nothing on the machine."
- No open blocker references M0-T161 (word-bounded scan of affects+detail).

---

M0-T161 DCV — PART 5/5: restamp predicate and verdict.

RESTAMP PREDICATE (restated; full disjoint-peer tolerance in my first message). PASS restamps to any target head WITHOUT re-review while ALL hold at that head:
- blob commission_lanes.ps1 == a39ba5bb; test_commission_lanes.ps1 == f0d69ef1; M0-T161-owner-guide.md == db29c32a; M0-T161-producer-report.md == f2fd87cd;
- _task_git_identity == report content_manifest_sha256 == 82864416, and the G2/G3/G5 records carry 82864416.
Any change to a blob or the identity VOIDS the restamp. Tolerated (do not void): other tasks' files/gates/material/accepts; other directives' binds; the orchestrator writing my v2 rows with digest resyncs + audit entries; DISCOVERY_BACKLOG rows and sweep lines; lifecycle-only packet/state changes that leave the four blobs and 82864416 byte-stable.

REQUIREMENT SUMMARY (5 applicable, all judged on primary source evidence I reproduced):
- D-088-R003 SATISFIED (procedure + safeguards; runtime closure OPEN pending owner -Phase update, F5)
- D-088-R004 SATISFIED
- D-088-R007 SATISFIED
- D-024-R287 SATISFIED
- D-066-R001 SATISFIED
No VIOLATED, no UNVERIFIABLE. F1-F5 are non-blocking. Frozen identity, lifecycle, applicability, and the prohibited-action sweep are all clean. Note for acceptance: R003's directive-level runtime goal (lanes 4/5 actually stood up) and B-026 close ONLY when the owner runs the helper — this task correctly delivers the reviewed helper, not the commissioning itself.

M0-T161 DCV VERDICT: PASS 5/5
END-OF-REPORT
