# M5-T075 — Directive-compliance verification (directive-compliance-verifier, read-only)

> Transmission history: the fresh seq-128 DCV (t075-dcv2, dispatched at pinned head ed49b2d8) sent its whole report as ONE SendMessage at 2026-09-24T07:10:22.864Z addressed to 'team-lead' (summary: "M5-T075 DCV verdict PASS 1/1"). That address did not deliver to the orchestrator's inbox, so the orchestrator recovered the message VERBATIM from the verifier's own transcript (the SendMessage tool-use input) - byte-for-byte, no edits; single transmission, no truncation, ends with END-OF-REPORT. The verifier ran validate_directive_compliance.py --check ONCE (direct exit 0) and did NOT run tools/test_directive_compliance.py. One line (the test-file blob SHA in the restamp predicate) carries an appended `<!-- gitleaks:allow -->` marker: a 40-hex git blob id beside a path containing 'api' trips gitleaks' generic-api-key rule (false positive); the verifier's text is otherwise byte-exact.

---

M5-T075 — Directive-compliance verification (directive-compliance-verifier, read-only). PINNED HEAD ed49b2d8af5fb4783cc3e456e29f78152e921baf confirmed by `git rev-parse HEAD`. Verdict up front: PASS 1/1 — D-084-R001 SATISFIED on primary evidence I reproduced myself.

PART 1/4 — identity, applicability, registry integrity

- Applicability computed by me (not read from the packet): `directive_registry.load_registry().evaluate_task_refs(M5-T075)` → ok=true, applicable_ids=['D-084-R001'], cited_ids=['D-084-R001'], missing=[], invalid=[], unresolved=[]. Applicable == cited, one requirement. R001.applicability.task_ids literally = ['D-084-BOOTSTRAP','M5-T072','M5-T075','M5-T076'] (M5-T075 present).
- Registry digests recomputed LF-normalized: source-001.md = f95ee41169ff90ae7b96a112448c580048a2ebb0bad247e40322d559ca5e8084 == manifest.sources[0].content_digest; `sha256_text_artifact(requirements.json)` = d2baddf50bab601d750e8dc6cbdf9b6b4e91504e90199fb5a1e671b280e85752 == manifest.requirements_content_digest. Both MATCH.
- D-084 present in index.json status "active"; single source, manifest.amendments=[], zero amendment files on disk → every amendment is reflected (vacuously). Validator `python tools/validate_directive_compliance.py --check` run ONCE, DIRECT exit code = 0 (no pipe). CI control-plane run 35963219466 = SUCCESS at headSha ed49b2d8 (pinned).
- Frozen identity recomputed with the CLI's own fn: `project_control._task_git_identity(M5-T075)` @HEAD = 7ea9cb15241ad8baebf4e7ff6c9dc4d53431ec3d36d7c23f388d7eb263e11591, resolved ed49b2d8, error None. Byte-equal to reports/M5-T075.json content_manifest_sha256 AND to the content_manifest_sha256 in G0, G2, G3, G4 records. Submission identity intact at the pinned head; an accept here will not hit frozen-evidence mismatch.

PART 2/4 — D-084-R001 (obligation, binding) SATISFIED, clause by clause on primary evidence

(a) Contracted — contract seam ed764d40 (packet + R001 bind + digest resync + G0 report + seeded placeholder; evaluate_task_refs ok). gates/M5-T075-G0.json PASS, orchestrator, administrative.
(b) Claimed — claim seam a0b41ed0 (`git show --stat`: G0 record + task file + state.json; progress 20; FULL worktree path).
(c) In-regime — tasks/M5-T075.json: directive_regime_version "1.0", directive_regime_entered_at 2026-09-23T05:12:03Z, directive_refs [{D-084,[D-084-R001]}]. task_type "frontend".
(d) Pushed — material 7d225e2f is ancestor of HEAD (= origin/candidate/D-024-mrl-option-b head ed49b2d8); contract+claim seams likewise ancestors.
(e) Worktree at/past the claim seam — `git worktree list`: C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t075 at 42a0157e on branch task/M5-T075-bridge-client-fault-tests; `git merge-base --is-ancestor a0b41ed0 42a0157e` = true. Packet.worktree carries that exact full path.
(f) Launcher pointed / fresh run-id / launch / close — lane-1 journal outside the repo at %LOCALAPPDATA%\NYCBuildabilitySupervisor\<CheckoutKey>\supervisor_journal.sqlite3 opened mode=ro&immutable=1. CheckoutKey from C:\SupervisorController\autostart-launch.ps1 = 9aca7075…f713b6a (lane-1; that launcher now points to run-71/M5-T076 with a comment recording run-70 = M5-T075 harvested 7d225e2f, COMPLETE). transitions seq 1723–1737 ALL run_id persistent-local-70-m5t075: 1723 PREFLIGHT→START_CLAUDE (preflight_pass, 2026-09-23T05:13:41.711Z), 1724 →CLAUDE_RUNNING, cycle 1 REVISE (gpt-6-astra), cycle 2 →1737 POLICY_CHECK→COMPLETE trigger decision_complete 05:38:20.072Z, evidence_refs naming apps/web/src/lib/__tests__/outline-bridge-api.test.ts. `group by run_id` shows this run exactly once, between run-69-m5t072 (1705–1722) and run-71-m5t076 (1738–1742) — never reused → lane-1's SECOND feed after T072. Launch log autostart-20260923-011336.out.txt: "DISPATCHED in limited-auto mode. cycles=2 final_state=COMPLETE stopped=stage_complete", elapsed 1478.5s, owner touches 0 of 2.
(g) Stale asks denied in both stores first — journal queued_asks: 0 asks for run-70 and 0 unanswered asks globally at verification time; run-70 raised none, consistent with stale asks cleared before the fresh launch.
- Allowed-path discipline (audit.jsonl, same dir): 14 approval_auto events for run-70, decision APPROVE_ONCE, policy_rule S4.1/in_scope_edit, all task_id M5-T075 / branch task/M5-T075-bridge-client-fault-tests; every target_path is one of exactly the two packet allowed_paths under wt-m5t075 (the test file + M5-T075-producer-report.md); zero denied/blocked writes.

PART 3/4 — work content + gates reproduced independently

- Material 7d225e2f `--numstat` = 143/0 on the test file (additions-only, zero deletions); producer report the only other file. Test blob ed57959e4c9fb8e5d56d086f8d2a6f5d215cbf53 byte-identical at 7d225e2f, at CI head 490c3413, and at HEAD. Production client blob b1b36871…3ef943 identical at 7d225e2f^ and HEAD → zero production edits (AS-4), honoring the read-only note for the frozen T071 consumer.
- I read the additions (test file 263–403): five specs — network TypeError→network_error (+recoverable, .toBe literal); timeout AbortError→client_timeout carrying timeoutMs=10; pre-flight caller abort→aborted with fetchCalls===0; mid-flight caller abort→aborted (distinct branch); over-budget Content-Length→unexpected_response(httpStatus 200, receivedState null, correlationId "cid"). Each asserts REFUSAL_OR_BRIDGED_KINDS.has(kind)===false (AS-2). Announcement literals byte-match the client arms.
- CI: web material rode run 35829303244 = SUCCESS at 490c3413 (whole CI workflow success; blob identity above ties that green to exactly this content).
- Gates: G0 PASS (orchestrator/administrative), G2 PASS (orchestrator/self_check = producer self-check), G3 PASS (code-reviewer/independent_review), G4 PASS (backend-engineer/independent_review). Producer = qa-engineer; both independent reviewers differ from the producer and from each other and both are in reviewer_agents (backend-engineer added by the roster amendment specifically because producer=qa-engineer). All four gate records carry the same content_manifest_sha256 7ea9cb15. Packet required_gates [G0,G2,G3,G4] exactly match config.json required_gates_by_task_type["frontend"] — no gate-set gap.

PART 4/4 — prohibited-action sweep, findings, restamp predicate, verdict

Prohibited-action evidence, each checked by me: NOT accepted — state.json accepted_tasks (256 entries) has no M5-T075 (last three: M5-T071, M5-T072, M5-T076). D-084 verification.json task_verifications has rows for M5-T072 and M5-T076 ONLY — no M5-T075 row; mine would be first. `git merge-base --is-ancestor 7d225e2f origin/main` = false → nothing merged. PR #241 still OPEN, title unchanged ("DO NOT MERGE until owner authorizes"), headRef task/M5-T002-scenario-endpoint, updatedAt 2026-08-20; no PR references M5-T075 → nothing dispatched/closed. No blocker file mentions M5-T075 (`grep -rl` over blockers/*.json empty; open blockers B-001/B-010/B-011 unrelated). Diff touches no dependency/lockfile/deploy/config path → nothing installed/deployed/purchased. I wrote no repository/ledger file.

Findings:
- F1 (INFO, affirming; non-blocking) — R001's out-of-repo lane-1 evidence (journal transitions, launch log, audit.jsonl) exists and corroborates the fresh run end-to-end through a clean COMPLETE/decision_complete close; paths/sequences/timestamps in Part 2(f)/(g).
- F2 (LOW, advisory; non-blocking) — producer report line anchors are stale after the re-feed revision: the branch table (:33-39) cites the timeout/pre-flight/mid-flight/over-budget specs at 329/341/358/370 and "lines 263–385", but the committed specs are at 319/335/351/368/384 and the block runs 263–403. All SOURCE-side anchors (:359-361,:380,:381,:382-387,:399-401,:549-556) are correct. Already surfaced as G3 F1 and marked "dispositioned at accept". CAUTION for the orchestrator: the producer report is inside allowed_paths / the frozen manifest 7ea9cb15, so an [ORCH-CORRECTED] edit to fix anchors would change the frozen identity and force a re-freeze + gate re-attestation; since non-blocking and source-side anchors are correct, disposition-by-note at accept (not edit) is the clean path.

No VIOLATED or UNVERIFIABLE results.

RESTAMP PRE-AUTHORIZATION. My PASS carries forward to any later head H' with no re-review iff BOTH hold at H': (1) every blob below is byte-identical, AND (2) `_task_git_identity(M5-T075)` still stamps 7ea9cb15241ad8baebf4e7ff6c9dc4d53431ec3d36d7c23f388d7eb263e11591 (this is also reviewed_manifest_sha256 for the v2 row).
- apps/web/src/lib/__tests__/outline-bridge-api.test.ts = ed57959e4c9fb8e5d56d086f8d2a6f5d215cbf53 <!-- gitleaks:allow -->
- project-control/reports/M5-T075-producer-report.md = 1dd8c49f9306938f449b1e22d8d80215ca353c6d
- project-control/tasks/M5-T075.json = e3bd1abed203aa94371913faaf26b36c9b05da88
- project-control/reports/M5-T075-evidence-map.json = d8c33b80077910c0507cfc4f379db59055cc4d1a
- project-control/reports/M5-T075.json = 2144a2fc09a995d1bf6383ce31d3f702e4c01e4a
- gates M5-T075-G0/G2/G3/G4.json = ddb6928540efbaf7e3f99a7a84df66e81140cf64 / 2d04fb5abe94334fa73a3eaabaf8b279e620be5c / 38551f4d380b6c33083974e25b4e235555571fb1 / 99bd88da5b8ef38e0c1ad27f5de9abaa8a27763e
- D-084 requirements.json = e79cea214058287ec3f02c018d5113c8a92e012d ; manifest.json = 98ca27a4355b086fcb20c6ba4d278d9235484c15

Disjoint-peer tolerance, stated explicitly and broadly: any number of peer commits may land between this head and the restamp target without voiding the PASS — other tasks' project-control files (reports/gates/evidence maps/ledger), other tasks' material under apps/** or services/**, other directives' capture files, handoff docs, accept seams for other tasks. I do NOT require the product directories empty, and I do NOT require D-084's verification.json unchanged (the orchestrator appending my M5-T075 row there is expected and does not void the predicate). Only a change to one of the blobs listed above, or a different identity stamp, voids it and needs a delta re-attestation from me.

DCV VERDICT: PASS 1/1

END-OF-REPORT
