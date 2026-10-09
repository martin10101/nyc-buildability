# D-023 capture readiness — bounded-autonomy campaign bootstrap

Recorded by the orchestrator at live-reconciled origin/main
`d8b3899f61efa6620e18a26541ced96020f5bef9` (tree `c50919b628a7618527768593ed37cc992b95b3e1`),
2026-08-21, on control branch `control/D-023-autonomy-campaign` (worktree `ctl23`, clean before
this capture).

## Live reconciliation before first mutation (D-023-R007, R009, R035)

Verified live on the Windows controller host before any write; **zero drift** from the campaign
packet's frozen identities:

- `git fetch --prune` → origin/main `d8b3899f`, 0/0 ahead-behind vs the reviewed identity.
- PR #241 OPEN, head `4174a3b2a547ae7d5df5d35cefb63767cbf84721`, title carries the live
  "DO NOT MERGE until owner authorizes" banner; auto-merge disabled. Its checkout `wt-m0t064`
  contains uncommitted user agent-memory edits — untouched (R031).
- PR #64 OPEN, head `39080822`, mergeable CONFLICTING — unrelated, untouched.
- Ledger: 121 packets = 100 accepted / 9 awaiting_gate / 10 backlog / 2 blocked (exact match);
  no nonterminal task owned `tools/agent_supervisor/**` before this capture.
- Directive registry: main ends at D-020; D-021/D-022 exist only on the held #241 branch →
  **D-023 collision-free**; ledger max M0 task M0-T077 → **M0-T078..M0-T085 collision-free**.
- Ruleset `protect-main` (active): PR required, merge-commit only, no force-push/deletion,
  review-thread resolution, 8 required checks (credentials scan; api; contracts ×3;
  control-plane; web; web-e2e).
- Validators at frozen identity, all PASS live: `validate_directive_compliance.py --check`,
  `validate_mcp_policy.py`, `context_budget_check.py`.
- Controller surface reachable: `C:\SupervisorController` tree + runtime journals under
  `%LOCALAPPDATA%\NYCBuildabilitySupervisor`; CLIs: claude 2.1.220, codex 0.146.0, gh 2.83.2,
  git 2.47.1.windows.2, Python 3.11.9, PowerShell 5.1 (no pwsh). Protected-config hashes/ACLs
  deliberately NOT touched (owner checkpoint only).

## Capture provenance (D-023-R001, R009)

- Delivery vehicle: `NYC_BUILDABILITY_AUTONOMY_CAMPAIGN_PACKET_2026-08-21.md`
  (full-packet SHA-256 `ebf21d44ffeca1ef39132e2903c9538c8f1f74a13f5b51a9182fe6648107b210`).
- `source-001.md` = packet Appendix A extracted **byte-for-byte** after the
  "## Appendix A" heading: 4,228 bytes, SHA-256
  `d07148c798e1cf9c65e0cf6faa277d7d1d71c8a26e967698768bffe662390b62`.
- The handoff the directive attaches, `NYC_BUILDABILITY_AUTONOMY_HANDOFF_2026-08-21.md`,
  read completely and verified against its recorded identity: SHA-256
  `08aee279e495237033c56671b3f00a443acfebffc18be8af637ea7e87bed9752`, 50,147 bytes, 867 lines
  — exact match.
- `source-002-amendment.md` = owner mid-session correction received during capture, before
  activation, captured verbatim as transmitted (81 bytes, SHA-256
  `5c0278d1c20bf9c2e2610f09291763d35e2fe9b4d964a4364f20a2dc7ead1f55`): no hardcoded maximum
  run-length limit; run duration owner-controlled, unlimited allowed. Interpretation recorded in
  `manifest.json → audit_log[1]` and flagged for owner confirmation at the final checkpoint.

## Decomposition and adversarial trace check

38 atomic requirements (D-023-R001..R038; R037 from amendment source-002, R038 the
p4-item5 named-repository prohibition). Before activation, four independent checkers
(forward trace, reverse trace, category completeness, schema/precedent conformance) reviewed
the decomposition against the verbatim source; their 2 must-fix + 3 important findings were
corrected before this commit:

1. must-fix: invented provenance in R001 (handoff digest attributed to owner text) → digest
   moved to the orchestrator-recorded evidence field; owner wording restored.
2. must-fix: invented implementation specifics in R015 (file paths, router design) → moved to
   the orchestrator-designed acceptance-harness field; owner wording restored.
3. important: R006 mis-anchor (named repositories are p4-item5, not p2) → R006 restored to the
   literal p2 clause; new R038 carries the p4-item5 sentence at the correct anchor.
4. important: R011 evidence cross-reference (R028 → R033) corrected.
5. important: applicability binding made uniform — all always-on prohibitions/scope rows
   (R001-R006, R010) now bind BOOTSTRAP + all eight campaign tasks, matching R023/R025-R031.
   Minor glosses (R002, R004, R014, R032, R033, R036) trimmed to source wording.

Residual noted deviations (deliberate): four bootstrap-only rows (R007, R008, R009, R035) have
empty `maps_to.tasks` because they are orchestrator session acts completed at capture, not task
deliverables; `dependencies` arrays are empty per D-020 precedent — sequencing lives in the
requirement text and the task-chain `depends_on` graph.

## Coordinated task campaign (D-023-R002)

Eight in-regime packets created via `tools/project_control.py new-task --directive-refs
D-023:ALL`, dependency-ordered, all gates explicit, reviewers rostered
(producer ≠ reviewer ≠ verifier):

| Task | Deliverable | Depends on |
|---|---|---|
| M0-T078 | Engineering-reliability standard + skill router | — |
| M0-T079 | Bounded mode: owner-controlled budgets (no hardcoded run limit), breakers, recovery probes, typed refusals | — |
| M0-T080 | Session/model turnover + owner-approved model routing | M0-T079 |
| M0-T081 | Production GitHub continuation, exact-head binding | M0-T079 |
| M0-T082 | Semantic fail-closed routing + hold dominance + policy reconciliation | M0-T081 |
| M0-T083 | Platform truthfulness (Windows preserved, Linux fail-closed) | M0-T079 |
| M0-T084 | Remote Control monitoring/steering boundary + runbook | M0-T080 |
| M0-T085 | Integration proof, frozen content manifest, consolidated review, owner-checkpoint bundle | T078, T080–T084 |

## Validation at capture

- `python tools/validate_directive_compliance.py --check` → **PASS (exit 0)** with D-023 active,
  38 locked requirement IDs, digests recorded in `manifest.json`.
- `python tools/validate_mcp_policy.py` → PASS. `python tools/context_budget_check.py` → PASS.
- No code, policy, GitHub, task-state (beyond the new packets), or protected configuration was
  changed by this capture (D-023-R009). PR #241 untouched and held (R032).
