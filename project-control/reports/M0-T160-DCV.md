# M0-T160 — directive-compliance verification (directive-compliance-verifier "dcv-m0t160", read-only)

> Transmission history: pinned at cf0da358 (HEAD advanced through disjoint orchestrator commits; the four reviewed blobs
> and identity f63172da byte-stable), delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT; no
> truncation. Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance. Joined verbatim by the
> orchestrator (transport wrapper tags removed only). F1: the one validator run straddled concurrent registry commits (a
> transient c14 race); committed digests hand-verified VALID and CI control-plane green at 851c4e63. F2-F3 are info.

---

M0-T160 DCV VERDICT: PASS 3/3 applicable requirements SATISFIED — part 1/5, restamp pre-authorization up front.

Frozen ref recorded at start: HEAD cf0da358 (advanced to e9a268a5 during review via concurrent orchestrator commits; cf0da358 remains an ancestor). reviewed_sha 83fdb5bd; content_manifest f63172da.

RESTAMP PRE-AUTHORIZATION (blob-level predicate) — I pre-authorize restamping my PASS to the live HEAD at accept time provided ALL hold:
- tools/controller_update/source_binding.json blob == 4f6fdfdbcb597bd20b307efa09557d2cc14922e2
- docs/CONTROLLER_UPDATE_RUNBOOK.md blob == 4ee5a21bb05a262672ac1fd7e3ca2fa3ed0bb14f
- tools/controller_update/ps_tests/test_runbook_parse.ps1 blob == 2288cb62b4c552b7d3695428cd68b9f71ff23542
- project-control/reports/M0-T160-producer-report.md blob == 94f62afcacdefbfb13bd9d930ed77ddd48e84bb8
- _task_git_identity(M0-T160) == f63172da573da8f55479ce78d9a77b48b760f56b3a07a6243c5a4e62418f24dc (I reproduced this at 83fdb5bd)
- M0-T160 gate records G0/G2/G3/G5 and material packet fields unchanged.

DISJOINT-PEER TOLERANCE (broad) — the HEAD advance may include, without voiding my PASS: other tasks' files/gates/material; other directives' registry binds (requirements.json/manifest.json/verification.json + digest resyncs + audit entries), INCLUDING transient in-flight c14 states that settle; the orchestrator adding MY verification rows to D-024/D-087/D-066 verification.json with matching digest resyncs + audit entries; DISCOVERY_BACKLOG rows + sweep lines; and lifecycle-only M0-T160 packet changes (awaiting_gate→accepted, progress_percent/updated_at/progress_log append, state.json accepted/active updates). Any change to the 4 reviewed blobs, the M0-T160 material fields, or its gate records voids the predicate → re-review required.

---

M0-T160 DCV part 2/5 — D-024-R287 evidence (SATISFIED).

D-024-R287 (obligation; source-013-amendment.md#standing-admission-discipline): "Future Claude Code upgrades are deliberate admission events: update, recapture fixtures, recertify, and only then repin." Applicability task_ids include M0-T160.

VERDICT: SATISFIED. Primary evidence I reproduced myself:
- ORDER correct: M0-T159 (2.1.281 admission + recertification) is ACCEPTED — tasks/M0-T159.json status=accepted/100%; accept-seam commit 9c44b68d "…M0-T159 ACCEPTED (273rd-275th)". M0-T160 (the repin) is awaiting_gate, i.e. after recert acceptance. Update→recertify→then repin.
- Binding pins the git-plumbing values of the FROZEN candidate a3f24ff3 (source_binding.json:6-9), each reproduced by me:
  commit_sha a3f24ff3825c126c038f59b1ea6d2352f29d724a == `git rev-parse a3f24ff3^{commit}`;
  commit_tree_sha 82432361540c3c2a11c55ffa3d6d485426cd45f7 == a3f24ff3^{tree};
  subtree_tree_sha 9c0b14eaa56ce32d241c77f789266035b584380c == a3f24ff3:tools/agent_supervisor (204 files).
- NOT the integrated ledger tree: cfc3d22c:tools/agent_supervisor = 11d43515… (≠ 9c0b14ea). Recert §5.0 (M0-T159-recertification.md:82-89) warns cfc3d22c carries UNCERTIFIED M0-T149/T152 supervisor code; the binding correctly names the isolated recertified subtree 9c0b14ea. This is the supply-chain guard, and it holds.
- 12/12 required_modules exist at a3f24ff3 (git cat-file -e each — reproduced). git diff --stat a5886dab a3f24ff3 = 12 files, ALL M0-T159 paths (reports/fixtures/tests + one benign event_drift.py fixture-pointer re-point).
- Nothing installed: the 4 material commits touch only the 4 allowed paths; commissioning (recert §5) is owner-typed + deferred; B-026 status=open. Authority sentence (source_binding.json:3) records recert "3662 passed / 2 skipped / 0 failed", which matches recert §2 line 25.

---

M0-T160 DCV part 3/5 — D-087-R001, D-066-R001, applicability, gates, frozen identity.

Applicability (reproduced): directive_registry.evaluate_task_refs(M0-T160) → ok=True; applicable_ids == cited_ids == [D-024-R287, D-066-R001, D-087-R001]; missing/invalid = none.

D-087-R001 (obligation; capacity unit, never skip a state/gate) — SATISFIED:
- M0-T160 is a contracted/claimed/gated packet citing D-087-R001 (tasks/M0-T160.json directive_refs).
- NEEDS_SPLIT handled by a RECORDED re-scope, not a skip: gates/M0-T160-G0.json result=PASS reviewed_sha=edafaad2 with 1 prior history PASS (original claim seam); progress_log records claim→NEEDS_SPLIT→re-scope(edafaad2)→rework/harvest→submit. Root cause DB-063 (DISCOVERY_BACKLOG.md:192, OPEN). Round-1 evidence preserved on branch task/M0-T160-round1 (exists).

D-066-R001 (obligation; navigation block + query.py --no-regen; advisory) — SATISFIED:
- tasks/M0-T160.json inputs carry "CODE-GRAPH NAVIGATION BLOCK (D-066-R001)": names the binding's readers (update_controller_from_candidate.ps1 Read-SourceBinding; test_runbook_parse.ps1 + test_source_binding.ps1), instructs `python tools/code_graph/query.py --no-regen impact <path>` before sweeps, and states "graph ADVISORY — verify … in actual source."

Gates — all required PASS; reviewers independent:
- G0 PASS (orchestrator/administrative, re-recorded edafaad2); G2 PASS (orchestrator/self_check); G3 PASS (code-reviewer/independent_review); G5 PASS (security-reviewer/independent_review). Producer=backend-engineer; neither reviewer is the producer; both reviewers are in reviewer_agents.
- All four gate stamps carry content_manifest_sha256 = f63172da.

Frozen identity (reproduced): frozen_git_identity at reviewed_sha 83fdb5bd = f63172da573da8f55479ce78d9a77b48b760f56b3a07a6243c5a4e62418f24dc == reports/M0-T160.json content_manifest_sha256 == G2/G3/G5 stamps. Material blobs at 83fdb5bd: 4f6fdfdb / 4ee5a21b / 2288cb62 / 94f62afc — match G2/G3/G5 and are byte-stable at the current HEAD.

---

M0-T160 DCV part 4/5 — lockstep, scope, prohibited-action sweep, harness.

Lockstep (reproduced by reading all three files): binding commit_sha (source_binding.json:6) == test $pinnedSha (test_runbook_parse.ps1:27) == runbook section-4 SHA (CONTROLLER_UPDATE_RUNBOOK.md:84) == a3f24ff3825c126c038f59b1ea6d2352f29d724a. Old full SHA 3f4cee86…dbc3 = 0 occurrences in all three (short "3f4cee86 (M0-T143)" survives only as supersession provenance). AS-3 dynamic run is [ORCH-HARVEST] (run_ps_tests.ps1 EXIT 0, 7/7 PASS at 777e6b81; RED at pre-rescope a612652b) — I verified the static 3-way lockstep, the RED→GREEN assertion logic (test lines 87-88), and blob identities; the PS run itself is orchestrator-captured (evidence-capture division), taken as stored evidence, not self-run.

Scope: material commits 8df2bec5 + 83fdb5bd touch EXACTLY the 4 allowed paths; no forbidden path. AS-2/AS-4 hold.

Prohibited-action sweep — all clear:
- Not accepted: tasks/M0-T160.json status=awaiting_gate; absent from state.json accepted_tasks (279 accepted).
- No verification row: 0 "M0-T160" in D-024/D-066/D-087 verification.json (all files present, task_verifications lists checked).
- Not on main: 8df2bec5, 83fdb5bd, cf0da358 are NOT ancestors of origin/main.
- PR #241 untouched: state OPEN, head task/M5-T002-scenario-endpoint, mergedAt null, updatedAt 2026-08-20.
- B-026 status=open; affects=[D-084 lanes, D-087-R001 loop-lane share]; "M0-T160" not present anywhere in the blocker JSON → will not block acceptance; stays open (correct — commissioning deferred).

Harness:
- test_project_control.py PASS (all 23 groups, exit 0); test_directive_reminder.py PASS (12/12, exit 0).
- CI control-plane job (runs validate_directive_compliance.py --check, ci.yml:442) = SUCCESS at head 851c4e63 (all 18 CI jobs green); cf0da358 + 83fdb5bd are ancestors of 851c4e63 with identical D-066/D-087 registry blobs.
- I did NOT run tools/test_directive_compliance.py (prohibited).

---

M0-T160 DCV part 5/5 — findings and final verdict.

F1 (INFO; investigated + resolved; NOT a defect): my single `validate_directive_compliance.py --check` run (ran once, ~25 min) returned exit 1 with 3 c14 "requirements.json content digest mismatch" errors — D-066, D-083, D-087 (D-024 was NOT flagged). This is the transient "requirements-lands-before-manifest" race from concurrent orchestrator registry writes in the shared checkout. Per your run-too-long fallback I hand-verified the committed digests: using directive_registry.normalize_text_artifact_bytes + sha256 (line-ending-normalized, so CRLF is irrelevant), declared == actual (c14 VALID) for all three at the cf0da358 blob, at the CI-green head 851c4e63 blob, AND on the now-settled disk (e.g. D-083 declared==actual==2ff20c34; the validator had transiently seen manifest 2de94081 vs a newer in-flight requirements 2ff20c34). CI's control-plane job runs the same validator and is GREEN on identical D-066/D-087 blobs. Conclusion: no committed c14 defect at the frozen head; does not affect M0-T160.

F2 (INFO; non-blocking; pre-existing, out of scope): G5 ADVISORY-1 — runbook stale lines 19 (pre-B-025 config SHA) and 122-124 (M0-T142 freeze-record pointer). Confirmed OUTSIDE the DB-063 re-scope (only section-4 lines 83-88 changed) and fail SAFE (mismatch → owner STOP, never a wrong install). Recommend a follow-up doc-consistency task.

F3 (INFO): DB-063 discoveries (test should read the SHA from the binding; wire the controller_update ps_tests into CI) routed to backlog; endorsed by G3/G5. Out of scope.

No BLOCKING findings. Every applicable requirement is SATISFIED on primary evidence I reproduced myself; the producer and G2/G3/G5 matrices were treated as claims and independently confirmed.

Requirement summary:
- D-024-R287: SATISFIED
- D-087-R001: SATISFIED
- D-066-R001: SATISFIED

M0-T160 DCV VERDICT: PASS 3/3 | no FAIL, no UNVERIFIABLE

END-OF-REPORT
