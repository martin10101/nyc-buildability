# D-016 Stage 0 — complete read-only reconciliation matrix

Produced: 2026-08-18T09:05Z by orchestrator (session15-acc), before any repository mutation.
Every row was verified live this session; no fact is taken from conversational memory.

| # | Live fact | Expected fact | Verdict | Source of evidence |
|---|---|---|---|---|
| 1 | origin/main = f21eb1fbca3e16d1602a14775c99bb3cac75eb1e | f21eb1fbca3e16d1602a14775c99bb3cac75eb1e | PASS | `git fetch --all --prune && git rev-parse origin/main` |
| 2 | PR #223 state MERGED, mergeCommit f21eb1f, merged 2026-08-18T08:46:33Z | MERGED at f21eb1f | PASS | `gh pr view 223 --json state,mergeCommit,mergedAt` |
| 3 | origin/control/context-intelligence-init = de2f224a7db16405edfc0e2f2f0902f5164819a0 | de2f224a... | PASS | `git rev-parse` |
| 4 | session15-acc worktree: branch control/context-intelligence-init, HEAD de2f224, `git status --porcelain` empty | clean at de2f224 | PASS | `git status --porcelain` in session15-acc |
| 5 | origin/task/M0-T070-supervisor-authority-repair = 09e23162b364034f3e3a771291664cb40bfc5705 | 09e23162... | PASS | `git rev-parse` |
| 6 | wt-m0t070: branch task/M0-T070-supervisor-authority-repair, HEAD 09e2316, clean | clean at 09e2316 | PASS | `git status --porcelain` in wt-m0t070 |
| 7 | origin/task/M0-T063-context-index-a1 = de2f224; wt-m0t063 clean at de2f224 | de2f224, clean | PASS | `git rev-parse` + `git status --porcelain` in wt-m0t063 |
| 8 | PR #222 OPEN, base control/context-intelligence-init, head 09e2316, MERGEABLE (mergeStateStatus UNSTABLE), 0 reviews | OPEN on same base/head | PASS | `gh pr view 222 --json state,baseRefName,headRefName,mergeable,headRefOid,reviews` |
| 9 | PR #222 checks: 16 of 17 contexts SUCCESS; only `web-dependency-security` FAILURE | expected failure: nanoid fix exists only on main, not yet in this branch's base | PASS (expected, repaired by Stages 1-2) | `gh pr view 222 --json statusCheckRollup` |
| 10 | PR #222 changed files = D-014 records + M0-T070 gates/reports/packet + B-019 + state.json + index.json + tools/agent_supervisor/{broker,cli,durable_state,policy}.py + schema + fixture + test_agent_supervisor_command_authority.py; no apps/web files, no controller-runtime files | supervisor repair + control-plane records only | PASS | `gh pr view 222 --json files` |
| 11 | M0-T070 packet: status awaiting_gate, progress 95, directive_refs D-001:ALL + D-014:ALL | awaiting_gate at 95%, not accepted | PASS | `git show origin/task/M0-T070-...:project-control/tasks/M0-T070.json` |
| 12 | M0-T071 packet on main: accepted, 100 | accepted | PASS | `git show origin/main:project-control/tasks/M0-T071.json` |
| 13 | D-015 on main: manifest status active; verification.json rows verified by directive-compliance-verifier (e.g. R001 PASS: age gate rerun, nanoid@3.3.18 age 919738s > 604800s, no waiver artifact in diff 5c71fe0..a997f19) | D-015 independently verified, no waiver | PASS | `git show origin/main:project-control/directives/D-015-nanoid-security-repair/{manifest,verification}.json` + reports/M0-T071-DCV-final-verification.md |
| 14 | B-019 status "open" on PR #222 branch | open, awaiting Stage 2 resolution | PASS | `git show origin/task/M0-T070-...:project-control/blockers/B-019-...json` |
| 15 | accepted_tasks counts: control branch 85, origin/main 86, task branch 85 | 85 / 86 (main includes M0-T071) / 85 | PASS | state.json at each ref |
| 16 | directive registries: control D-001..D-013; main D-001..D-012+D-015; task branch D-001..D-014 | control lacks D-014/D-015; main lacks D-013/D-014; task branch lacks D-015 | PASS | directives/index.json at each ref |
| 17 | M0-T063 packet: status claimed, progress 10, no documented_test_commands field; M0-T064..M0-T069 packets present on control branch | A1 claimed, unimplemented, runway present | PASS | project-control/tasks/M0-T06[3-9].json on control branch |
| 18 | D-013: manifest active, 2 sources, 88 requirements, all 5 record files present | D-013 captured with 88 reqs | PASS | project-control/directives/D-013-context-intelligence-pipeline/ |
| 19 | M0-T070 report set (producer, return, evidence-map, G0/G3/G5 reviews, DCV, ci-reconciliation, before-after, incident) all in PR #222 diff; M0-T071 report set (producer, return, DCV-final-verification, dependency-evidence, evidence-map, G0/G4/G5) on main | final report sets exist | PASS | `gh pr view 222 --json files` + `git ls-tree origin/main project-control/reports/` |
| 20 | A1 durable supervisor state (LOCALAPPDATA/NYCBuildabilitySupervisor/1854a2a4.../supervisor_journal.sqlite3, key = sha256 of canonical wt-m0t063 path): current_state "PREFLIGHT", limited_auto_enabled false, revoke_all executed (3 asks REVOKED, reason "operator revoke-all"), launched_child_processes [], effects 0, transitions end PAUSED_RECOVERY -> PREFLIGHT | PREFLIGHT, A1 not implemented | PASS | sqlite read-only (`mode=ro`) on the journal |
| 21 | C:\SupervisorController contains repo-tree controller (INTEGRATION_MANIFEST.json present); C:\Program Files\SupervisorConfig\config.toml = immutable D-007 §3.1 config (shadow default, codex gpt-5.6-sol/terra, claude allowed_models ["claude-opus-4-8"]) | accepted PR #221 controller, untouched protected config | PASS (read-only; nothing changed) | directory listing + read-only cat |
| 22 | gh authenticated; remote refs fetched with --prune | working GitHub access | PASS | successful gh/git calls |

## Interpretation note (recorded, not a deviation)

Stage 1's required semantic outcome says directives/index.json "must contain every valid directive
D-001 through D-015 exactly once". D-014's registry entry exists only on the PR #222 branch
(neither Stage 1 merge parent carries it), so after Stage 1 the control-branch index holds
D-001..D-013 + D-015 exactly once; D-014 joins the control branch exactly once when PR #222 merges
(Stage 4), and the final integrated state contains D-001 through D-015 exactly once with no
duplicates. Importing D-014 directly at Stage 1 would bypass the PR #222 review flow and violate
stage ordering, so it is not done.

## Stage 0 verdict

All 22 rows PASS. No material identity or worktree condition differs from the owner's stated
starting state. Mutation stages are cleared to begin: D-016 capture commit first, then Stage 1.
