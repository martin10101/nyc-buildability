# M0-T181 — directive-compliance verification (directive-compliance-verifier, independent, read-only)

Record header (orchestrator): verifier = directive-compliance-verifier subagent, dispatched 2026-10-03 pinned at 83a64029 and tracking the live branch head through b5cdbdeb and 58b88988 (gate-record head). Report received complete in one transmission with END-OF-REPORT; saved verbatim below. Its restamp predicate governs the accept seam that follows (verification row written at reviewed_sha 58b88988; accept recorded back-to-back; validator re-run on the accept state with a direct exit code before the seam commit).

---

DCV REPORT — ledger task M0-T181 (supervisor-bridge Windows CI repair), PR #372, directive D-090 R093/R094. Independent, read-only. Producer ≠ verifier preserved.

HEADS: contract db9c4351 (G0); claim-seam ec87eb6b; material head 1ba4380e; submit seam 83a64029; c14-fix seam b5cdbdeb; gate-record/restamp head 58b88988 = CURRENT PR head. Material identity (allowed_paths blobs) is BYTE-IDENTICAL across 1ba4380e → 83a64029 → b5cdbdeb → 58b88988 (I diffed each; all empty on the allowed_paths set). Worktree /root/project/w-M0-T181 verified clean at the live head each time.

OVERALL VERDICT: PASS.

== PER-REQUIREMENT VERDICTS ==

D-090-R093 (authorization: bounded repair in a SEPARATE PR; investigate timing vs real defect; fix the CAUSE; run alongside other work): PASS.
- Separate PR: `git diff --stat ec87eb6b..1ba4380e` touches ONLY the packet's allowed_paths — tools/agent_supervisor/{mrl_descendants.py,mrl_one_shot.py}, tools/test_agent_supervisor_{review_slots,mrl_one_shot}.py, project-control/reports/M0-T181-{convergence-record,producer-report}.md, and ci-evidence/. No lane PR, no .github/**, no services/apps/packages. Branch task/M0-T181-… is not a lane branch.
- Investigation is REAL, not fabricated. I authenticated the frozen CI evidence against GitHub myself: full-log sha256 via `gh api …/jobs/<job>/logs | sha256sum` AND headSha via `gh run view` for jobs 111231288935 (b341c4a2…/head 84ded09b), 111247110311 (2443eb67…/head 745e3318) and 111292325552 (bdb04229…/head 265635a8) — every sha256 and every headSha matches the recorded values EXACTLY. Decisive 4th-occurrence corroboration verified live: push run 37153603034 supervisor-bridge = SUCCESS while pull_request run 37153605150 (job 111292325552) FAILED on the SAME head 265635a8 — a load-only difference, ruling out a code-deterministic bug (= the TEST-TIMING classification of Failure A).
- Each failure classified with deciding evidence and fixed at the CAUSE (I read the diff, not the claim). Failure B = REAL supervisor defect in mrl_descendants.py (frozen proof: root 8028 absent, four live orphans 8040/8088/8136/8184 whose stale Win32 th32ParentProcessID = the reused root pid, 97 attempts over 5.05 s never clearing). Fix: descendants_of/prove_zero_descendants gain root_start + a creation-ordinal reader so a process created strictly BEFORE the root is pruned with its subtree; unknown creation time is KEPT (fail-closed); no root_start = byte-identical old walk; _ContainedSpawn captures root_start the instant after Popen while the child is alive. This is exactly S3's prescribed remedy and is sound (a true descendant is causally created after the root). Failure A = TEST-HARNESS TIMING (racer's independent 30 s go-deadline < parent's 60 s readiness window → early racer emits "0" without calling try_reserve → under-count); fix is in the TEST FILE ONLY (review_slots.py production unchanged): reason codes (admitted/refused:<code>/barrier_timeout), parent fails LOUDLY on any non-slot outcome, barrier budget derived (90 s = 60 parent + 30 lock-serialize).

D-090-R094 (prohibition: preserve safety/concurrency assertions; no skipped tests, weakened checks, or retries for green): PASS.
- I enumerated every assertion in both test files at ec87eb6b vs 1ba4380e. Every OLD assertion is present in NEW (line-shifted only); none removed or weakened. Race invariants byte-identical: assertEqual(winners,2), assertLessEqual(len(ReviewSlots(self.dir).active()),2), per-lane assertEqual(winners,1). The existing descendants mutation asserts (descendants_of 10/1/0/777, orphan walk) are byte-identical. The reaped-child assertion `proof.proven is True and proof.remaining == ()` is UNCHANGED (only setup now captures root_start as production does).
- Added-line scan over the whole diff for skip|xfail|rerun|--reruns|flaky|pytest.mark|retry|sleep-and-retry = NONE. No .github/** and no pytest config (pytest.ini/pyproject/conftest/tox/setup.cfg) in the diff.
- The ONE timeout change (barrier 30→90 s) meets the S4 exception: convergence record §2 shows the old 30 s IS the cause (shorter than the 60 s parent window) and DERIVES 90 s from a stated budget (60 parent readiness + 30 lock-serialization). lock_timeout_s, the winner hold, and the descendants settle window are unchanged.
- New tests are strengthening only (loud self.fail branch; guarded-vs-unguarded mutation proof on the exact frozen shape; fail-closed unknown-creation-time).

== PACKET-INTEGRITY FINDINGS ==
F1 Binding OK. From the worktree, reg.evaluate_task_refs(M0-T181) = ok True, applicable==cited==[D-090-R093,D-090-R094], missing=[], invalid=[]. Applicability bound in contract db9c4351: M0-T181 appended to both rows' applicability.task_ids, requirements_content_digest resynced (509e16fb…→80d2651f…), and an audit_log action "applicability_bound" added in the SAME commit; no requirement text edited. Requirement texts match owner message 39 verbatim (source-014#owner-message-39-verbatim).
F2 Gates OK and substantive. G0 (db9c4351, orchestrator, administrative, PASS); G2 (1ba4380e, orchestrator, self_check, PASS); G3+G4 (b5cdbdeb, code-reviewer, independent_review, PASS, report M0-T181-G3G4.md); G5 (b5cdbdeb, security-reviewer, independent_review, PASS, report M0-T181-G5.md). All content_manifest_sha256 = 5a35443f… (material). Both review reports are real independent reproductions (code-reviewer ran 164 passed = 83+81; security-reviewer did a line-level fail-closed analysis of the pruning rule) — they corroborate my findings.
F3 Evidence map OK. Shape = requirements:{id:[prose]}. material_commits name the producer cherry-pick commits 0ad93762 (Failure B) + 4d94d75b (Failure A) + 1ba4380e (material head); contract_head db9c4351, claim_seam_head ec87eb6b correct. The Windows run id was recorded as an [ORCH-CORRECTED 2026-10-03] prose line in the evidence map (not in the convergence record, to avoid moving material identity).
F4 Frozen evidence OK. The three contract evidence files have 0 commits since db9c4351 (unchanged); the fourth (job-111292325552…) was added in the single-file commit ce66ac48. All four authenticated against GitHub (F-R093).
F5 S1–S8 all satisfied. S1 four-job frozen table; S2 Failure-A trace+classification; S3 Failure-B trace+classification+fix+new test; S4 timeout derivation; S5 assertions preserved (producer report lists before/after); S6 Windows CONFIRMED — supervisor-bridge (windows-latest) job = SUCCESS at material head 83a64029 (run 37154896211, job success; the run-level "failure" was the c14 control-plane job, since fixed) and SUCCESS again at the current head's CI (runs 37155544286/37155541432); S7 recert recorded (both production modules changed → M0-T179 voided, D-091 path, a cost not a bar); S8 ends VERIFIED_CLOSED. Honest residual disclosed: mrl_one_shot_review.py:291 (outside allowed_paths) still calls prove_zero_descendants without root_start = old fail-closed walk (safe over-count) — a recorded one-line follow-up, not fixed here.
F6 Lifecycle/prohibited-action OK. tasks/M0-T181.json status = awaiting_gate (progress 85→95 in the restamp); in state.json active_tasks, NOT in accepted_tasks/blocked_tasks/failed_gates. PR #372 OPEN, MERGEABLE — nothing merged/accepted/deployed/installed/purchased/closed.
F7 No open blocker references M0-T181 (grep clean; accept-flow blocker scan will not trip).
F8 Holds OK. No loop activation/commissioning (D-090-R084 stays deferred); diff touches no Tier D item.
F9 c14 history. Validator at 83a64029 was EXIT 1 with the single error "c14 [D-090] in-regime affected task M0-T181 has no task_verification row" — the exact row my verdict populates. The coordinator's seam b5cdbdeb adds the provisional task_verifications row (applicable R093/R094, producer backend-engineer, verifier "", reviewed_sha null, both pending — the M0-T180/bbb77dec shape), touching only verification.json; allowed_paths blobs unchanged. Validator then EXIT 0 at b5cdbdeb and at the current head 58b88988.
F10 Restamp 58b88988 OK. Changes vs b5cdbdeb are confined to gates/M0-T181-{G3,G4,G5}.json, reports/M0-T181-{G3G4,G5}.md, evidence-map.json (the [ORCH-CORRECTED] Windows line), tasks/M0-T181.json lifecycle, state.json. Material allowed_paths blobs byte-identical to 1ba4380e. Modularity: mrl_descendants.py grew ~90 lines but is NOT flagged (check 0 failures; warnings only on unrelated files).

== COMMANDS RUN (direct exit codes) ==
- git -C /root/project/w-M0-T181 status → clean (EXIT 0); HEAD tracked live (83a64029 → b5cdbdeb → 58b88988).
- git diff --stat ec87eb6b..1ba4380e → 7 files, allowed_paths only (EXIT 0).
- evaluate_task_refs(M0-T181) → ok True (EXIT 0).
- validate_directive_compliance.py --check @83a64029 → c14 error, DIRECT EXIT 1.
- validate_directive_compliance.py --check @b5cdbdeb → DIRECT EXIT 0.
- validate_directive_compliance.py --check @58b88988 (current head) → DIRECT EXIT 0.
- pytest -q test_agent_supervisor_review_slots.py + mrl_one_shot.py -p no:cacheprovider → 83 passed, 2 subtests, EXIT 0 (reproduces producer's 83/8.19s).
- pytest -q test_agent_supervisor_mrl_one_shot_review.py (consumer) → 81 passed, EXIT 0.
- supervisor_command_doc_check.py → 11 checked, 0 failures, EXIT 0.
- modularity_check.py --check → 0 failures (29 warnings, none on changed files), EXIT 0.
- test_project_control.py → all 23 groups passed, EXIT 0.
- test_directive_reminder.py → 12 tests OK, EXIT 0.
- gh api jobs/{111231288935,111247110311,111292325552}/logs | sha256sum → all 3 match recorded; gh run view headSha for each → all match; push run 37153603034 supervisor-bridge = success.
- gh run view 37154896211 → supervisor-bridge job = success at head 83a64029.

== CI CONTROL-PLANE JOB STATE AT HEAD ==
`gh pr view 372 --json statusCheckRollup` at head 58b88988 (merge ref 58b88988): control-plane (workflow regression test, ADR-005) = COMPLETED/SUCCESS (both event contexts); supervisor-bridge (pytest tools/test_agent_supervisor_*.py, windows-latest) = COMPLETED/SUCCESS (both contexts); ANY FAILURES = NONE. A few unrelated jobs may still be IN_PROGRESS at the moment of reading but none failed; the two load-bearing jobs (control-plane + windows supervisor-bridge) are green.

== RESTAMP PRE-AUTHORIZATION (state up front) ==
My PASS verdict carries, WITHOUT re-review, to any later head whose tree is BYTE-IDENTICAL to 58b88988 for every allowed_paths file (tools/agent_supervisor/{mrl_descendants.py,mrl_one_shot.py}, tools/test_agent_supervisor_{review_slots,mrl_one_shot}.py, project-control/reports/M0-T181-{producer-report,convergence-record}.md, project-control/reports/M0-T181-ci-evidence/**), AND whose only other changes are confined to:
  • project-control/gates/M0-T181-*.json;
  • project-control/reports/M0-T181-{G3G4,G5,DCV}.md;
  • project-control/reports/M0-T181-evidence-map.json (orchestrator [ORCH-CORRECTED]-tagged edits only);
  • project-control/reports/M0-T181-convergence-record.md ONLY if the sole change is an appended line naming a windows-latest run id (no other byte moves — note it is in the material set, so any other edit voids carry);
  • project-control/directives/D-090-*/verification.json (recording my DCV verdict and the task_verification row/state transitions) and, if that write triggers it, a verification-digest resync in project-control/directives/D-090-*/manifest.json;
  • project-control/tasks/M0-T181.json lifecycle fields (status/progress/updated_at/gate pointers) and project-control/state.json.
Disjoint peer commits (lane PRs merging into the base candidate/D-024-mrl-option-b, or that base merged into this branch) are TOLERATED when the merge introduces no change to any allowed_paths blob — prove with `git show --remerge-diff --format= <merge> -- <allowed_paths>` == empty and an unchanged patch-id of the net allowed_paths diff. Re-run validate_directive_compliance.py --check with a DIRECT exit code at the final accept head (must be EXIT 0) before accept.

== ONE-PARAGRAPH VERDICT ==
PASS. M0-T181 is a genuine, cause-level repair of the recurring windows-latest supervisor-bridge failures, delivered in a separate PR confined to the packet's allowed_paths. The investigation is authenticated — three frozen job logs' full-log sha256 and headSha match GitHub exactly, and the decisive same-head push-pass/pull_request-fail pair is real. Failure A (test-timing barrier/parent-window decoupling) is fixed in the harness with reason codes, a loud fault, and a budget-derived barrier; Failure B (a real Win32 stale-parent + pid-reuse false "descendants remaining") is fixed at the cause in mrl_descendants.py with a sound, fail-closed creation-ordinal exclusion and a new mutation-proof test on the exact frozen shape. No assertion was removed or weakened, no test skipped, no retry added, no CI/pytest config touched; the single timeout change is traced and derived. S1–S8 are satisfied (S6's Windows run is now CONFIRMED SUCCESS, not merely pending; S7 recertification consequence recorded), G0/G2/G3/G4/G5 are PASS, the validator is EXIT 0 at the current head after the provisional-verification-row seam, and the task remains awaiting_gate with nothing prohibited performed. I found no VIOLATED or UNVERIFIABLE requirement. The orchestrator may record my DCV verdict in verification.json and accept at a head satisfying the restamp predicate above.

END-OF-REPORT
