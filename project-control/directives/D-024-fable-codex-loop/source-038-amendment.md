# D-024 Amendment 38 — external audit response: STOP the renewal/launch path; owner-decided target + PHASE 1 bounded launch-contract lab (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator, verbatim, BEFORE acting. Base identity at capture:
local control HEAD `e54e083d` (branch `control/D-024-fable-codex-loop`, unpushed; origin/control
`6f5d12a6`, origin/main `d8b3899f`). Amends: `source-001.md`. Requirement IDs: D-024-R472..D-024-R488.

Trigger: the owner supplied an external senior-engineering audit
(`NYC_CODEX_LOOP_SENIOR_ENGINEERING_AUDIT_20260901.md`, verdict NO-GO) and then issued this
directive. The orchestrator had committed the `claude_runner.py` modularity-exception renewal
(`b7b203d2`) + the recert/present-only deliverable (`e54e083d`) and was one step from gating/accepting
M0-T133. The orchestrator independently reproduced the audit's four P0 reproducible findings
(F-01 control 567-ahead of main; F-02 checkpoint validator accepts a malformed/empty payload; F-03
Codex COMPLETE accepts a non-SHA head / empty origin / empty evidence; F-04 modularity red 1432/1410
with reports having misstated exit 0) before stopping. This amendment records the owner's course
correction and authorizes PHASE 1 ONLY.

## Reconciliation
The owner STOPS the accept-renewal-launch path and STOPS any open-ended "stabilization tranche". The
finished target is reaffirmed as a genuinely end-to-end ordinary-work lifecycle (NOT a local-only
producer/reviewer loop). The `claude_runner.py` modularity exception must NOT be renewed; the eventual
correction must split the module. This message authorizes ONLY a bounded (<=8 engineering hours)
read-only launch-contract lab that adjudicates 14 launch-critical contracts and returns one
consolidated repair-estimate package with a single GO/NO-GO-shaped recommendation. It does NOT
authorize implementation of any fix. M0-T133 stays unaccepted; the loop stays PAUSED_RECOVERY.

## Forward trace (owner text -> requirement id)
- Decision 1 (end-to-end ordinary-work lifecycle target; not local-only) -> R472
- Decision 2 (PR #241 + every pre-existing PR untouched unless separately authorized) -> R473
- Decision 3 (do not renew the claude_runner.py modularity exception; preserve the local renewal commit as evidence; eventual correction must split responsibilities + remove reliance on the renewal) -> R474 (no-renew prohibition) + R475 (preserve-commit + split obligation)
- Decision 4 (no Agent SDK / third-party framework / downloaded agent code / global Claude config change / protection weakening / direct-main write / silent model substitution / unauthorized GitHub mutation) -> R476
- Decision 5 (authorizes PHASE 1 ONLY; does not authorize implementation) -> R477
- PHASE 0 FREEZE (record HEAD/branch/tree/status/unpushed/ahead-behind; explain 567 vs 565 + identify the two local commits) -> R478
- PHASE 0 (preserve all work; no reset/revert/amend/push/accept/recertify/mutate campaign/runtime/journal) -> R479
- PHASE 0 (M0-T133 remains unaccepted; loop remains PAUSED_RECOVERY) -> R480
- PHASE 1 (timebox <=8 engineering hours; collection-style, do not stop after first failure; do not fix defects) -> R481
- PHASE 1 (adjudicate the 14 enumerated launch-critical contracts only; no general inventory / unrelated P2 cleanup) -> R482
- PHASE 1 (provider canaries only: new $env:TEMP scratch repo, non-mutating, <=8 provider calls, owner-approved exact model only, no updater/background/fallback/substitution/owner-gated op; BLOCKED_OWNER_GATE if more specific auth required, never bypass, never call it a pass) -> R483
- DELIVERABLE (one consolidated package: LAUNCH_CONTRACT_MATRIX.md + LAUNCH_CONTRACT_RESULTS.json + STABILIZATION_REPAIR_PLAN.md; per-row fields enumerated) -> R484
- DELIVERABLE (separate launch-blocking P0/P1 vs post-launch P2/P3 vs unrelated backlog; do not expand P2/P3 into the stabilization package) -> R485
- KILL CRITERIA (7 conditions -> return NOT_VIABLE_WITHIN_CURRENT_BOUND and stop before implementation) -> R486
- RECOMMENDATION (exactly one: PROCEED_WITH_ONE_BOUNDED_REPAIR_PACKAGE with scope+estimate, OR NOT_VIABLE_WITHIN_CURRENT_BOUND with smallest architecture decision) -> R487
- (do not implement; do not ask piecemeal questions; return complete matrix + recommendation in one response) -> R488

Anchors: #target-lifecycle (R472), #pr-untouched (R473), #no-renew (R474), #preserve-and-split (R475),
#prohibitions (R476), #phase1-only (R477), #freeze (R478), #preserve-no-mutation (R479), #holds (R480),
#timebox-collection (R481), #fourteen-contracts (R482), #canary-bounds (R483), #deliverable (R484),
#severity-separation (R485), #kill-criteria (R486), #recommendation (R487), #one-response (R488).

---VERBATIM-BEGIN---
Your immediate stop was correct. Do not accept M0-T133, do not launch, and do not begin an open-ended "stabilization tranche."

The owner decisions are:

1. The finished target remains a genuinely end-to-end ordinary-work lifecycle: isolated task branch, implementation, commit, push, correlated PR, required CI/review, permitted ordinary green merge, and ledger continuation. Do not redefine success as a local-only producer/reviewer loop.
2. PR #241 and every pre-existing PR remain untouched unless separately authorized.
3. Do not renew the "claude_runner.py" modularity exception. Preserve the existing local commit as evidence, but the eventual correction must split responsibilities and remove reliance on the renewal.
4. No Agent SDK, third-party agent framework, downloaded agent code, global Claude configuration change, protection weakening, direct-main write, silent model substitution, or unauthorized GitHub mutation.
5. This message authorizes PHASE 1 ONLY: a bounded launch-contract lab and final repair estimate. It does not authorize implementation.

PHASE 0 — FREEZE

- Record the exact local HEAD, branch, tree, status, unpushed commits, and ahead/behind state.
- The external check currently sees remote "control/D-024-fable-codex-loop" at "6f5d12a6203c2c89390a982657fa8d66a91a0c3d" and "origin/main" at "d8b3899f61efa6620e18a26541ced96020f5bef9", 565 commits apart. Explain the local 567-ahead result and identify the two local commits.
- Preserve all work. Do not reset, revert, amend, push, accept, recertify, or mutate the campaign/runtime/journal.
- M0-T133 must remain unaccepted and the loop must remain "PAUSED_RECOVERY".

PHASE 1 — BOUNDED CONTRACT LAB

Timebox this entire phase to no more than eight engineering hours. Run all independent checks and return once with the complete result. Do not stop after the first failure, and do not fix defects during this phase.

Do not repeat general repository inventory or investigate unrelated P2 cleanup. Adjudicate these launch-critical contracts only:

1. Canonical controller source, approved SHA, installation source, and stale-"main" risk.
2. Generated PowerShell command semantics, path existence, task/worktree/branch/SHA binding, and raw "$LASTEXITCODE" capture.
3. Full executable hashes, versions, updater freeze, and drift between preflight and dispatch.
4. Effective Claude/Codex settings, hooks, MCP, plugins, rules, tools, effort, and redacted environment inventory.
5. Exact selected-model identity and Claude/Codex/GitHub authentication inside the production child environment.
6. Real "--permission-prompt-tool stdio" allow/deny/unsupported/EOF/timeout behavior on the installed Claude CLI.
7. Two-message "stream-json" behavior and controller-owned total turn/call/time enforcement independent of "--max-turns".
8. Complete Claude checkpoint schema enforcement and exact run/task/session/checkpoint/Git correlation.
9. Complete Codex decision schema enforcement and exact HEAD/origin/evidence-digest binding.
10. Queue file, task packet, canonical worktree, branch, starting HEAD, current status, and successor transition binding.
11. Fresh remote observation versus stale tracking refs.
12. Raw gate-result integrity, including failure through output filters or PowerShell display pipelines.
13. Process-tree containment, result/EOF ordering, timeout classification, recovery reachability, and zero descendants.
14. Real GitHub lifecycle topology: whether a worker branch can safely target the intended integration branch without dragging hundreds of control commits; identify exactly what production push/PR/check/merge/acceptance execution is absent.

The owner authorizes only non-mutating provider canaries in a newly created "$env:TEMP" scratch Git repository, with:

- no repository, controller, journal, queue, campaign, PR, or remote mutation;
- no updater;
- no background agents;
- no fallback or model substitution;
- at most eight provider calls;
- only an already owner-approved exact model;
- no purchase, production action, or owner-gated operation.

If an existing directive requires a more specific authorization, mark that row "BLOCKED_OWNER_GATE"; do not bypass it and do not call it a pass.

DELIVERABLE

Return exactly one consolidated package:

- "LAUNCH_CONTRACT_MATRIX.md"
- "LAUNCH_CONTRACT_RESULTS.json"
- "STABILIZATION_REPAIR_PLAN.md"

For every matrix row include:

- PASS, FAIL, BLOCKED, or NOT_RUN;
- observed fact;
- expected invariant;
- exact command or probe;
- raw exit code;
- evidence artifact and digest;
- whether proof is static, fixture, simulated, or real-CLI;
- exact defect if failed;
- exact production files/functions affected;
- positive test and mutant test required;
- dependency on another row;
- estimated engineering hours.

Separate findings into:

- launch-blocking P0/P1;
- post-launch hardening P2/P3;
- unrelated backlog.

Do not expand P2/P3 work into the stabilization package.

KILL CRITERIA

Return "NOT_VIABLE_WITHIN_CURRENT_BOUND" and stop before implementation if any of these is true:

- the launch-critical repair estimate exceeds five working days;
- safe GitHub topology requires an undefined large control-branch merge;
- the permission bridge cannot be reproduced reliably;
- structured checkpoint output cannot coexist with required stream/resume behavior;
- exact child authentication or effective configuration cannot be deterministically bound;
- more than twelve independent launch-critical defects remain after deduplication;
- a necessary fix requires Agent SDK, a new framework, protection weakening, or another owner-prohibited architecture change.

End with one recommendation:

- "PROCEED_WITH_ONE_BOUNDED_REPAIR_PACKAGE", including exact scope and total estimate; or
- "NOT_VIABLE_WITHIN_CURRENT_BOUND", including the smallest architecture decision required.

Do not implement anything and do not ask piecemeal questions. Return the complete matrix and recommendation in one response.
---VERBATIM-END---
