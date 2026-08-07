# M0-T044 Producer Report — Automatic safe GitHub flow (shadow-only)

Task: M0-T044 "Automatic safe GitHub flow (0A.8 item 8; AD-077; Section 19.4 proofs)"
Branch/worktree: `task/M0-T044-github-flow` @ `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
Posture: SHADOW-ONLY. Every proof runs against fakes/fixture state. No real push/PR/merge.
Nothing is wired into a live path; the R595 activation gate is not lifted.
Requested status: awaiting_gate.

## Files written / changed

- `tools/agent_supervisor/github_flow.py` (NEW) — decision + orchestration for the ordinary
  GitHub flow: push authorization, Tier B review routing, ten S5.5 merge predicates,
  stale-remote-SHA reconciliation, branch-cleanup safety, and the injected-runner/journal
  orchestration (`GitHubFlow`) with idempotency + no-blind-retry guard.
- `tools/test_agent_supervisor_github_flow.py` (NEW, 57 tests) — the S19.4 proofs, AS-1..AS-5,
  the shadow-posture proofs, and the ten-item S19.4 register meta-test. Picked up automatically
  by the CI supervisor-bridge glob `tools/test_agent_supervisor_*.py`.
- `tools/agent_supervisor/external_effects.py` (MODIFIED, additive) — `ExternalEffectJournal`
  gains an optional `extra_specs` constructor arg + `_spec_for()`. This lets a SHADOW-scoped
  journal resolve `github_pr_merge` WITHOUT adding it to the production `MODELED_EFFECTS`
  registry. `begin()` and `assert_not_destructive()` now resolve via `_spec_for()`. Default
  behavior (no `extra_specs`) is byte-for-byte unchanged, so the production live-path registry
  stays free of any merge effect (D-007 invariant 9 preserved).

## Design decisions

- **github_flow.py vs push_policy.py.** Push HARD-DENY logic (force/main/remote-identity/secret)
  stays authoritative in `push_policy.evaluate_push`. `github_flow.authorize_push` is a thin
  Tier A/D classifier over it: ALLOW when no S13.6 check HARD-DENIES, else surface the deny
  reason verbatim. No deny logic is duplicated. New logic (routing, the ten merge predicates,
  remote reconciliation, branch cleanup, orchestration) lives in `github_flow.py`.
- **Shadow-scoped merge effect (the key SHADOW-ONLY decision).** `github_pr_merge` is
  DELIBERATELY not added to `external_effects.MODELED_EFFECTS`. That registry is the live-path
  authority and D-007 invariant 9 (`test_invariant_9_no_modeled_effect_performs_a_gated_action`)
  keeps it free of any merge/deploy effect. The merge is journaled/reconciled through an
  `ExternalEffectJournal` built with `extra_specs=SHADOW_EFFECT_SPECS`, reusing all of the S13.7
  idempotency/before-after/reconcile machinery without wiring a new automatic effect into the
  live path. A plain live-path journal still refuses a merge as `unmodeled_effect` (proven).
- **Dry-run boundary.** All real side effects cross the injected `GitHubRunner` Protocol. Tests
  pass `RecordingRunner`, which records calls and can `fail_on` a step to simulate a crash.
- **Journal schema reuse.** No schema change. `git_push_task_branch` and `github_pr_create` are
  the pre-existing production modeled effects; only `github_pr_merge` is shadow-scoped.
- **Determinism / no wall-clock.** Every predicate takes explicit inputs; no `time`/`datetime`
  read in decision logic. Timestamps live only in the journal persistence layer.
- **Idempotency + no blind retry.** `GitHubFlow._guard(action_id)` classifies an effect key
  before re-firing: no record -> proceed; CONFIRMED -> return recorded result, do NOT repeat;
  PENDING (crash survivor) -> refuse and require reconciliation. Reconciliation uses
  `ExternalEffectJournal.reconcile` (occurred=confirm/no-dup; not-occurred=FAILED+safe-to-retry;
  None=pause).

## Per-requirement evidence

- **R006 (no owner approval for routine flow).** `ReviewRouting.owner_approval_required` is
  always False; no merge predicate consults an owner approval. Tests:
  `test_no_tier_b_routing_ever_requires_owner_approval`,
  `test_merge_proceeds_once_all_specialist_reviews_pass_no_owner`.
- **R007 (keep PRs + protected-main workflow).** PRs are first-class (`create_pull_request`,
  `github_pr_create` effect); direct main push and force push HARD-DENY via `authorize_push`.
  Tests: `PushAuthorizationTests`, `PullRequestCreationTests`.
- **R010 (continue another accepted dependency when a noncritical item blocks).** Structurally
  honored: refusals are machine-readable structured reasons (never a world-stop); an ineligible
  merge leaves no external effect (`test_an_ineligible_merge_leaves_no_external_effect`), so the
  controller records and continues. (Queue/continue orchestration itself lives in the loop layer;
  this task supplies the deterministic refusal signal it consumes.)
- **R077 (prove automatic safe GitHub flow).** The whole file + S19.4 register.
- **R093 (nothing speculative — exactly this list).** Scope is exactly the S19.4 ten items and
  the S5.5 conditions; no extra capability added. `test_the_register_lists_all_ten_items`.
- **R116 / R117 (re-dispatch rows, acknowledge only).** Acknowledged; no action required.

## Section 19.4 ten-item -> test map

1. ordinary task branch push auto-passes -> `test_ordinary_task_branch_push_is_allowed`
   (+ orchestration `test_a_confirmed_push_is_not_pushed_again`)
2. main push hard-denies -> `test_direct_main_push_is_hard_denied`
   (+ `test_direct_master_push_is_hard_denied`)
3. force push hard-denies -> `test_force_push_is_hard_denied`
4. PR creation works -> `test_pr_creation_works_and_is_journaled`
5. ordinary green PR auto-merges -> `test_ordinary_green_pr_auto_merges_and_records_the_sha`
   (+ eligibility `test_ordinary_green_pr_is_eligible`)
6. secret finding blocks -> `test_merge_refuses_on_a_secret_finding`
7. stale remote SHA blocks or reconciles -> `test_merge_refuses_on_a_stale_remote_sha`
   (blocks) + `test_divergence_reconciles_after_a_successful_refetch` (reconciles) +
   `test_merge_refuses_when_remote_state_is_unknown`
8. workflow/dependency require specialist review but not owner approval ->
   `test_workflow_change_routes_to_security_and_control_plane`,
   `test_dependency_change_routes_to_dependency_security_and_ci`,
   `test_no_tier_b_routing_ever_requires_owner_approval`,
   `test_merge_blocks_until_the_required_specialist_review_passes`
9. branch cleanup is safe -> `test_flow_deletes_only_the_proven_merged_task_branch`
   (+ `BranchCleanupTests` for every retain/delete direction)
10. crash during push/merge reconciled without blind retry ->
    `test_crash_mid_push_leaves_a_pending_effect_reconciled_not_retried`,
    `test_crash_mid_merge_leaves_a_pending_effect`,
    `test_a_second_merge_attempt_on_a_pending_effect_does_not_re_fire`,
    `test_reconciling_a_proven_merge_confirms_it_without_duplication`,
    `test_reconciling_a_merge_that_did_not_happen_is_safe_to_retry`,
    `test_an_unprovable_merge_pauses_rather_than_retrying`

Meta-guard: `Section194RegisterTests.test_every_section_19_4_item_has_a_named_test` proves the
mapping stays honest, and `test_the_register_lists_all_ten_items` proves all ten are present.

## AS-1..AS-5 -> test map

- AS-1 (task push allow; main/force hard-deny) -> `PushAuthorizationTests` (6 tests).
- AS-2 (PR + green merge; refuse on failing check / secret / blocking finding / stale SHA, one
  each) -> `PullRequestCreationTests`, `GreenMergePathTests`, `MergeEligibilityTests` (16 tests,
  including each of the ten S5.5 predicates in both directions), `RemoteReconciliationTests`.
- AS-3 (workflow/dependency route to specialist review WITHOUT owner approval) ->
  `ReviewRoutingTests` (7 tests).
- AS-4 (delete only proven-merged task branches; retain unusual/evidence/unmerged/current) ->
  `BranchCleanupTests` (6 tests) + `BranchCleanupOrchestrationTests`.
- AS-5 (crash mid-push/mid-merge reconciled without blind retry; idempotent, no duplicate,
  completed-or-rolled-back per journal) -> `CrashReconciliationTests` (8 tests).
- Shadow posture (merge not in live registry) -> `ShadowPostureTests` (3 tests).

## Commands + real counts

Baseline (origin/main state, before this task's files):
```
$ python -m pytest -q tools/test_agent_supervisor_*.py
1214 passed, 2 skipped in 75.08s
```

New file, pytest runner:
```
$ python -m pytest -q tools/test_agent_supervisor_github_flow.py
57 passed in 0.81s
```

New file, unittest runner (both runners required):
```
$ python -m unittest tools.test_agent_supervisor_github_flow
Ran 57 tests in 0.612s
OK
```

Full supervisor suite, after (regression check):
```
$ python -m pytest -q tools/test_agent_supervisor_*.py
1271 passed, 2 skipped in 75.20s
```

Arithmetic: 1214 (baseline) + 57 (new) = 1271. Zero pre-existing tests changed status; the one
transient failure during development (invariant 9, from a first-cut registry addition) was
resolved by the shadow-scoped `extra_specs` design and the full suite is green.

## Residuals / honest limitations

- The merge/push orchestration proves the DECISION + JOURNALING + RECONCILIATION contract in
  shadow. It does not execute git/gh; a future live implementation of `GitHubRunner` remains
  gated on the ADR-005 amendment / R595 activation and is out of this task's scope.
- The "retry-with-same-key re-execution" after a proven NOT-occurred effect is proven at the
  reconciliation-verdict level (`safe_to_retry == True`); the durable journal's current schema
  transitions PENDING->CONFIRMED/FAILED only, so actually re-minting a fresh attempt with the
  same key is a journal capability not exercised here (and not required by S19.4).
- `cond_branch_current` folds stale-remote-SHA currency and clean-mergeability into the single
  S5.5 "branch is current enough to merge safely" condition; the reconcile path is additionally
  exercised directly via `reconcile_remote_sha` (`RemoteReconciliationTests`).
- "Changed paths fit the task" reuses `policy.path_matches` against the task's allowed-path
  globs; it does not re-derive allowed paths from the packet (the caller supplies them, matching
  how `TaskAuthority` is built elsewhere).
