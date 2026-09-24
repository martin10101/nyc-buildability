# M0-T159 — directive-compliance verification (directive-compliance-verifier "dcv-m0t159", read-only)

> Transmission history: pinned at 464dda21 (HEAD advanced through five disjoint orchestrator commits to cd58a348;
> identity 3ccb0c5e reproduced at each), delivered as four SendMessage parts (1/4..4/4) ending with END-OF-REPORT;
> no truncation. Part 1 carries the identity-level restamp predicate and explicitly tolerates the later,
> separately reviewed re-pin of tools/controller_update/source_binding.json to a3f24ff3 after acceptance. Joined
> verbatim by the orchestrator (transport wrapper tags removed only). Validator EXIT 0 (one run). B-026 stays OPEN
> until the owner types the commissioning commands (recertification section 5).

---

M0-T159 DCV report (directive-compliance-verifier). Part 1/4 — VERDICT + restamp predicate (up front).

VERDICT: PASS 3/3. Applicable requirements D-024-R287, D-066-R001, D-087-R001 all SATISFIED at the frozen identity; gates independent + PASS; no prohibited action.

RESTAMP PRE-AUTHORIZATION (blob-level). Reviewed identity = content_manifest_sha256 3ccb0c5e6ca10b82b9edf8dec9b70cc9a1c9aabb944f615e781e594abe19d4aa, which I reproduced with project_control._task_git_identity over M0-T159's 12 allowed_paths (9 tools/ raw-blob + 3 project-control/reports material). Byte-identical at submit cdd62c5c, gate-record head fa7e5fae, and every live HEAD I observed. Verification stays valid while those 12 blobs remain byte-identical (identity==3ccb0c5e) at accept-time HEAD.

I explicitly tolerate as disjoint peers (predicate NOT voided):
- other tasks' files/gates/reports/material commits (the M5 + D-087 lanes landing now);
- other directives' registry binds and their verification.json rows/digest resyncs/audit entries;
- the orchestrator adding M0-T159's OWN verification rows to D-024/D-066/D-087 verification.json with matching digest resyncs + audit_log entries in the same commit;
- lifecycle-only edits to tasks/M0-T159.json (status/progress/timestamps/progress_log) leaving the material fields and all 12 blobs unchanged;
- the later separately-reviewed re-pin of tools/controller_update/source_binding.json to a3f24ff3 AFTER acceptance (not in this task's identity).
VOIDS the predicate: any commit mutating one of the 12 allowed_path blobs (identity != 3ccb0c5e).

HEAD MOVED repeatedly during my read-only run (start pin 464dda21 → f00a4745 → 24455e45 → validator straddle 5cb3ca94→cd58a348). All disjoint orchestrator peers; identity 3ccb0c5e reproduced across them — the pre-authorized disjoint-peer condition, empirically met. Harness: validate_directive_compliance.py --check EXIT=0 at the reviewed head (one run, direct exit code).

---

M0-T159 DCV Part 2/4 — requirement rows (primary evidence, reproduced myself).

D-024-R287 [obligation] — SATISFIED. Source: source-013-amendment.md#standing-admission-discipline ¶5 ("Treat future Claude Code upgrades as deliberate admission events: update intentionally, recapture fixtures, recertify, and only then repin. Do not silently accept version drift."); requirement text is a faithful ¶5→R287 decomposition (not weakened/invented). Deliverable verified in-tree at HEAD via git ls-tree: four 2.1.281 fixtures (capability_probe_live_2026-09-24_m0t159_2_1_281, hook_event_catalog_2_1_281, native_runtime_detection_2026-09-24_m0t159, shell_routing_2026-09-24_m0t159_2_1_281); event_drift.py re-pointed 2_1_252→2_1_281 (line 37/47), older catalogs kept as history. Recert recorded (M0-T159-recertification.md): a5886dab OWN baseline 3659 + 3 CLI-drift teeth, 2 skipped, 3664 collected → after re-point 3662 passed / 0 failed / 2 skipped / 3664 collected, no test removed; 147-file manifest 55dc71350b to a TEMP path, config.toml bound, verify-controller PASS, non-live doctor 41/41.
Division of labour: tools/controller_update/source_binding.json STILL pins commit a5886dab / tree 65036d3f / subtree 850841ab (cat-verified); a3f24ff3 is NOT an ancestor of HEAD and no M0-T159 commit touches source_binding.json — the repin correctly deferred, not claimed. Commissioning (install / verify / doctor --live / lane restarts / --repin-cli-identity) presented in recert §5 as OWNER-TYPED, "presented, never run" (recert line 8-9; producer report line 81-83 "NOT run"); the producer's own record-manifest/doctor wrote only under %TEMP%\m0t159\ (recert line 391). See F2 re suite-count evidence source.

D-066-R001 [obligation] — SATISFIED. tasks/M0-T159.json inputs[4] carries the CODE-GRAPH NAVIGATION BLOCK: names the fixture-pack consumers (capability_probe / event_drift / native_runtime / recovery_probes / start_gate + the 4 test packs), instructs the producer to run query.py --no-regen impact before sweeps, and states graph-advisory / verify-every-conclusion-in-source. Present in packet.

---

M0-T159 DCV Part 3/4 — D-087-R001, frozen identity, gates, prohibited-action sweep.

D-087-R001 [obligation] — SATISFIED (this task's share). M0-T159 is the B-026 remedy re-enabling the three codex lanes on CLI 2.1.281 (B-026.affects names "D-087-R001 (loop-lane share of today's capacity ramp)"). Ran as a fully gated ledger packet — G0 PASS at contract seam 125efaa1, claimed with FULL worktree path wt-m0t159 on certified a5886dab, G2/G3/G4 PASS, lifecycle backlog→in_progress→awaiting_gate with a proper rework loop; no state/gate skipped. Orchestrator-dispatched backend-engineer subagent; allowed_paths scoped to tools/agent_supervisor + its reports (disjoint from the M5 lanes — G4 confirms full-repo diff cfc3d22c→HEAD touches only unrelated M5 tasks). B-026 stays OPEN pending owner-typed commissioning — verified (B-026.status=open); remedy delivered as a repository deliverable, commissioning deferred. (F4: R002 no-interference is not bound to M0-T159, so correctly not cited.)

FROZEN IDENTITY — INTACT. reports/M0-T159.json content_manifest 3ccb0c5e == G2 == G3 == G4 stamps (all 3ccb0c5e); G0 stamp 4294de1f = contract-seam identity (by design). _task_git_identity reproduced = 3ccb0c5e at HEAD, err=None. G3/G4 re-recorded at disjoint head fa7e5fae carrying the SAME manifest (identity-carry reviews).

GATES — independent + PASS. G0 orchestrator(administrative); G2 orchestrator(self_check, producer self-check); G3 code-reviewer(independent, M0-T159-G3-corrections.md, history→G3.md); G4 qa-engineer(independent, M0-T159-G4-carry.md, history→G4.md). Producer backend-engineer ∉ reviewers. required_gates G0/G2/G3/G4 all PASS.

PROHIBITED-ACTION SWEEP — clean. Not accepted (awaiting_gate, 95%). No verification row (grep NONE across the 3 directives' verification.json). Not on main (cdd62c5c on candidate/D-024-mrl-option-b only; not ancestor of origin/main or local main). PR #241 untouched (OPEN, head task/M5-T002-scenario-endpoint, updated 2026-08-20 — unrelated). No blocker names M0-T159 (grep empty; B-026 names M0-T132 precedent, affects D-087-R001/D-084). No worker-pin/allowlist edit — M0-T159 commits (cfc3d22c material + cdd62c5c reports-only, 2 files) touch only allowed_paths; config.toml/allowlist only READ + described in report prose.

---

M0-T159 DCV Part 4/4 — findings + verdict.

FINDINGS (all informational; none blocking):
- F1 HEAD advanced 5× during my read-only verification (464dda21→f00a4745→24455e45→5cb3ca94→cd58a348), concurrent orchestrator lanes. Identity 3ccb0c5e reproduced across them; pre-authorized disjoint-peer tolerance empirically satisfied.
- F2 Recert suite counts (3662/3664) are producer+G4 evidence, not DCV-reproduced — the ~3664-test controller suite is live-adjacent and out of DCV scope (safety rules preclude touching the controller surfaces). G4 qa-engineer independently re-ran the 4 fixture-consuming packs = 150 passed / 0 skipped and confirmed tools/ byte-identical cfc3d22c→HEAD. I verified deliverable presence, frozen identity, pin deferral, and the owner-typed framing directly from source/git.
- F3 No fresh control-plane CI run at the M0-T159 head on the candidate branch (latest control-plane CI green dates 2026-09-14/15). Harness evidence is the single local validator --check EXIT=0 at the reviewed head (start 5cb3ca94 → end cd58a348; direct exit code, no straddle defect), as pre-authorized.
- F4 D-087-R002 (no-interference) correctly not cited (not applicable to M0-T159); disjointness still evidenced by the tools/agent_supervisor-scoped allowed_paths.

BOTTOM LINE. The R287 admission + recertification is complete AS A REPOSITORY DELIVERABLE on the certified a5886dab base: fixtures recaptured at 2.1.281, drift tooth re-pointed + removal-sensitive, whole-suite recert reconciled to baseline (no test removed), temp-manifest bound + verify-controller PASS, with the source_binding re-pin and all live commissioning correctly deferred as owner-typed. B-026 remains open until that commissioning. Applicability == cited exactly (evaluate_task_refs ok=True, missing/invalid=none). Frozen identity intact; gates independent + PASS; no prohibited action.

M0-T159 DCV VERDICT: PASS 3/3

END-OF-REPORT
