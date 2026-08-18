# M0-T070 / D-014 final directive-compliance verification (fresh, independent)

Verifier: directive-compliance-verifier (fresh run, producer=orchestrator != verifier)
Frozen reviewed head: 46f746928dda26b1a3527e1cfec901e642115578 (branch task/M0-T070-supervisor-authority-repair, worktree clean)
Material identity: 296b8fa6b7ff5e44cee9eacf0e2bb1b7bbfdd3fa170c0e77cae71140372f965c (all 7 implementation files blob-identical to gate-reviewed 6aae5857; G2/G3/G5 apply unchanged; no gate invalidation)
Recorded: 2026-08-18T10:17:41+00:00 by orchestrator from the verifier's returned matrix (verbatim states/evidence).

Scope: the COMPLETE D-014 requirement set (52 rows) = 30 M0-T070-applicable rows
(restamped in verification.json at this head), the D-014-BOOTSTRAP sentinel rows, and
the 13 reconciliation-amendment rows (source-002-amendment.md, amendment_sequence 2).
Sentinel-only rows are verified here at directive level (D-015 precedent: sentinel rows
are never inside a ledger task's accept() set).

| Requirement | State | Primary evidence |
|---|---|---|
| D-014-R001 | PASS | incident-evidence.md + ci-reconciliation.md: read-only recon of branch/HEAD 46f7469, wt-m0t063 clean de2f224, origin/main, PR#222, ledger, M0-T063..T069 reserved |
| D-014-R002 | PASS | incident-evidence.md root-cause section inspects cli.py/policy.py/broker.py/durable_state.py/replay.py with line citations |
| D-014-R003 | PASS | incident-evidence.md Defect A: pre-fix from_packet kwarg default () policy.py:883-915; _run_loop pre-fix cli.py:2487-2489 omitted arg; CONFIRMED |
| D-014-R004 | PASS | incident-evidence.md Defect B: revoke_all pre-fix broker.py:665-689 approval-only; queued_asks never UPDATEd; cmd_status open_asks unconditional; CONFIRMED |
| D-014-R005 | PASS | incident-evidence.md: 'M0-T063.json additionally carried no command-authority field at all' |
| D-014-R006 | PASS | return-report item1: M0-T070 chosen; M0-T063..T069 allocated by D-013, no reuse |
| D-014-R007 | PASS | gh pr view 222 base=control/context-intelligence-init; stacked at de2f224; return-report item2; no unrelated changes in PR own files |
| D-014-R008 | PASS | both defects source-CONFIRMED before fix (incident-evidence.md); stop-rule not triggered; no speculative fix implemented |
| D-014-R009 | PASS | project-control/tasks/M0-T070.json is the single corrective task; branch task/M0-T070-supervisor-authority-repair; worktree wt-m0t070 (git worktree list) |
| D-014-R010 | PASS | M0-T070-incident-evidence.md + bounded packet M0-T070.json committed (in PR#222 file list) |
| D-014-R011 | PASS | source-001.md captured once (git blob sha256 7628740 == manifest); manifest owner_approval 'capture-once authorized by the same message'; no duplicate capture |
| D-014-R012 | PASS | PR#222 own files all within wt-m0t070 allowed_paths + control plane; no apps/; diff confined to task scope |
| D-014-R013 | PASS | gates G0/G2/G3/G5 recorded (in diff); suites reproduced: cmd-auth 29/29, dc 120, pc 23 groups, reminder 12 |
| D-014-R014 | PASS | PR#222 OPEN head 46f7469, branch pushed; first-parent chain 6aae585->bcc0962->04cae38->09e2316->46f7469 |
| D-014-R015 | PASS | PR#222 mergeCommit null / mergedAt null (OPEN); M0-T070 status awaiting_gate not accepted; controller SHADOW-ONLY per return-report; no runtime activation |
| D-014-R016 | PASS | wt-m0t063 clean de2f224 (no restart); no A1 impl files or protected config in diff; policy strengthened; PR#222 unmerged |
| D-014-R017 | PASS | schemas/task_packet_commands.schema.json closed profile (maxItems16, restrictive pattern) + policy.validate_documented_test_commands; SchemaValidatorLockstepTests 4 pass |
| D-014-R018 | PASS | cli.production_task_authority (cli.py:2513) loads validator, used by _run_loop (cli.py:2544); ProductionWiringTests pass |
| D-014-R019 | PASS | validate_documented_test_commands (policy.py:881) raises PolicyError on empty/wrong-type/bounds/shell-meta/multi-segment; ValidatorFailClosedTests 8 pass |
| D-014-R020 | PASS | M0T063FixtureTests.test_every_intended_command_is_auto_documented_test passes |
| D-014-R021 | PASS | M0T063FixtureTests: altered/injected variants never AUTO + test_a_command_outside_the_task_authority_is_not_auto pass |
| D-014-R022 | PASS | MAX_DOCUMENTED_TEST_COMMANDS=16 cap; no allowlist/bypass in diff; NoBroadGrantTests 3 pass (entry cap + no-other-authority + no-wildcard-program) |
| D-014-R023 | PASS | ProductionWiringTests.test_run_loop_builds_authority_only_through_the_production_path (AST pin) + loads-through-validator pass |
| D-014-R024 | PASS | broker.revoke_all->journal.resolve_ask UPDATE queued_asks never DELETE (durable_state.py:619-638); cmd_status read-time reconcile read-only (cli.py:1346-1370) |
| D-014-R025 | PASS | RevokeStatusLifecycleTests 5 pass: pending open->revoke->pending-approvals 0->status truthful->revoked history preserved + audit/journal integrity |
| D-014-R026 | PASS | fixtures/m0_t063_documented_test_command.json (4 intended + 13 adversarial); M0T063FixtureTests pass |
| D-014-R027 | PASS | CI supervisor-bridge SUCCESS (pytest tools/test_agent_supervisor_*.py) on 46f7469; local cmd-auth 29/29; pc 23 groups + dc 120 + reminder 12 reproduced |
| D-014-R028 | PASS | M0-T070-before-after-evidence.md + M0T063FixtureTests.test_the_pre_fix_construction_reproduces_the_a1_failure; no A1 re-run |
| D-014-R029 | PASS | config.toml appears only in verbatim directive text; absent from diff de2f224..46f7469 |
| D-014-R030 | PASS | model_selection.toml absent from diff de2f224..46f7469; only in directive text |
| D-014-R031 | PASS | A1 SQLite DB in %LOCALAPPDATA%, not in repo/diff; incident-evidence.md documents mode=ro&immutable=1 read-only access |
| D-014-R032 | PASS | wt-m0t063 clean at de2f224 (git worktree list); A1 branch task/M0-T063-context-index-a1 head unchanged = de2f224 |
| D-014-R033 | PASS | fail-closed validator ADDED (strengthens); no tier weakened; adversarial variants remain ASK/HARD_DENY; NoBroadGrantTests pass |
| D-014-R034 | PASS | C:/SupervisorController absent from repo/diff; PR#222 unmerged; nothing activated/replaced |
| D-014-R035 | PASS | reflog shows only 3 no-op 'reset: moving to HEAD' at de2f224 (git stash push/pop internals; HEAD never moved; no force/clean/rewrite). Disclosed for owner literal-reading adjudication |
| D-014-R036 | PASS | diff de2f224..46f7469 contains no Units A1-F impl files (repo_fingerprint/index in forbidden_paths, absent) |
| D-014-R037 | PASS | return-report item8: rollback scoped to branch+worktree removal only; A1 + runtime evidence intact |
| D-014-R038 | PASS | project-control/reports/M0-T070-return-report.md committed at 04cae38 with all 9 required items (task id, branch, files, root cause, before/after, SHA+PR, gates, risks, merge/controller cmds) |
| D-014-R039 | PASS | wt-m0t063 clean de2f224; no supervisor start/resume against A1 this session |
| D-014-R040 | PASS | M0-T070-ci-reconciliation.md cites run 32108527309 jobs 95622882065/95622881295; 32 rollup checks reproduced green on 46f7469 via gh |
| D-014-R041 | PASS | manifest audit_log records CRLF->LF digest restamp (never silent); requirements_content_digest 96828f9; validate --check exit 0 |
| D-014-R042 | PASS | reproduced: validate_directive_compliance.py --check exit 0; test_directive_compliance 120 OK; test_project_control 23 groups OK; cmd-auth 29 pass |
| D-014-R043 | PASS | ci-reconciliation Item3: material identity 296b8fa6 at 6aae5857 == reconciled head; 7 impl files blob-identical to 6aae5857 (git rev-parse) |
| D-014-R044 | PASS | gh api check-runs on 46f7469: 30 runs all 'success', none incomplete; statusCheckRollup 32 all SUCCESS |
| D-014-R045 | PASS | gh pr view 222 files: only M0-T070/supervisor/D-014-capture/control-plane files; no apps/ or unrelated paths |
| D-014-R046 | PASS | PR#222 OPEN/unmerged (mergeCommit null); head 46f7469 is a base-sync merge into the PR branch (not landing the PR); nothing activated |
| D-014-R047 | PASS | PR#222 own files exclude apps/web/package.json & package-lock.json; no waiver/allowlist artifact; nanoid fixed via separate PR#223 |
| D-014-R048 | PASS | B-019 reproduced_facts + ci-reconciliation: nanoid identical integrity hash at PR head/base de2f224/origin-main; inherited unchanged (read-only git show) |
| D-014-R049 | PASS | project-control/blockers/B-019-nanoid-transitive-advisory-web-dependency-gate.json exists, records nanoid advisory as separate external blocker needing own task |
| D-014-R050 | PASS | B-019 resolution_path recommends branch-from-origin/main not-stacked; separate task M0-T071 created under D-015 (new owner auth), not under D-014 |
| D-014-R051 | PASS | M0-T070-ci-reconciliation.md is durable reconciliation record; all M0-T070-owned failures corrected (digest fixed, nanoid external) => PR_222_CI_RECONCILED state |
| D-014-R052 | PASS | wt-m0t063 at de2f224 unchanged; A1 not restarted |

## Cross-cutting verifications

- Material identity: All 7 impl files (cli.py 9d021fa, policy.py 25cf16e, broker.py e05ad18, durable_state.py 613e679, schema 6edec28, fixture 58f187e, test 39ff0d4) blob-identical HEAD vs 6aae5857 via git rev-parse
- B-019: status 'resolved' in this head; resolution evidence verified (nanoid 3.3.18 at HEAD (integrity sha512-DTg4...); PR#223 MERGED f21eb1f into main; web-dependency-security SUCCESS on 46f7469; no waiver)
- CI: all 32 PR #222 check contexts pass on 46f7469 (gh statusCheckRollup + check-runs)

## Disclosures / notes (verifier verbatim)

- R035 (prohibition-7 literal reading, DISCLOSED, non-blocking): one git stash push/pop for a read-only lint comparison left 3 no-op 'reset: moving to HEAD' reflog entries in wt-m0t070; HEAD never moved off de2f224, nothing cleaned/rewritten/force-pushed. Producer did not directly invoke git reset/clean/force-push. Flagged for owner literal-reading adjudication; verified non-destructive from reflog, so marked PASS.
- Note (not a defect): full-range diff de2f224..46f7469 shows apps/web/package*.json + D-015/D-016/M0-T071 files, but these are base inheritance from the synchronized base 351ced6 / merged PR#223 (f21eb1f), NOT M0-T070 task edits (PR#222 own file list excludes them).

## Verdict

PASS - all 52 D-014 requirements verified from primary evidence at the frozen head;
zero FAIL / BLOCKED / UNVERIFIABLE / improper NOT_APPLICABLE; one fully-disclosed,
non-blocking conduct caveat on R035 left for owner literal-reading adjudication.
