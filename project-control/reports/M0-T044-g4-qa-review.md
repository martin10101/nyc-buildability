# G4 QA Gate Report — M0-T044 "Automatic safe GitHub flow (0A.8 item 8; AD-077; Section 19.4 proofs)"

**Reviewer:** qa-engineer (independent; read-only)
**Verdict:** **PASS**
**Reviewed content:** producer commit `af46b3e` — verified byte-identical to branch HEAD `7437747` for all three implementation files (`git diff --name-only af46b3e HEAD -- github_flow.py test_...github_flow.py external_effects.py` returned empty; commits on top are control-plane only). Base `origin/main` `341fa4d`.
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch` branch `task/M0-T044-github-flow`
**Scope note:** This is an independent QA gate over AS-1..AS-5 and the ten D-010 §19.4 items. Per-directive-requirement (D-010-R006/R007/R010/R077/R093/R116/R117) verification is the directive-compliance-verifier's pass; not re-adjudicated here.

## 1. Executed-command log (real excerpts)

**New file, both runners, twice each — no flakes:**
```
python tools/test_agent_supervisor_github_flow.py   -> Ran 57 tests ... OK   (run 1: 1.199s; run 2: 0.916s)
python -m pytest -q tools/test_agent_supervisor_github_flow.py -> 57 passed (run 3: 1.12s; run 4: 0.98s)
```
Zero skips in the new file (57 passed / 0 skipped both runners).

**Full supervisor suite:**
```
python -m pytest -q tools/test_agent_supervisor_*.py  ->  1271 passed, 2 skipped in 76.47s
python -m pytest --collect-only -q ... github_flow.py  ->  57 tests collected
python -m pytest --collect-only -q ... _*.py           ->  1273 tests collected  (= 1271 passed + 2 skipped)
```
Baseline arithmetic verified: 1273 total − 57 new = **1216 = 1214 passed + 2 skipped** at baseline. New file contributes exactly 57 passing, 0 skipped ⇒ **+57, zero regressions** (producer claim confirmed). The 2 skips are pre-existing (not in the new file).

**D-007 invariant-9 (shadow posture) with new code present:**
```
python -m pytest -q tools/test_agent_supervisor_invariants.py -k invariant_9  ->  2 passed, 43 deselected
```
`test_invariant_9_no_modeled_effect_performs_a_gated_action` iterates `ex.MODELED_EFFECTS` and asserts no name contains "merge"/"deploy" — passes because `github_pr_merge` lives only in `github_flow.SHADOW_EFFECT_SPECS`, never in the production registry.

**Regressions:**
```
python tools/test_project_control.py       -> all 22 project-control test groups passed (exit 0)
python tools/test_directive_compliance.py  -> Ran 102 tests ... OK (53.7s)
python -m pytest -q tools/test_agent_supervisor_crash.py -> 32 passed  (exercises default ExternalEffectJournal)
```

## 2. Per-AS results (independently reproduced)

| AS | Covering tests (executed) | Independent probe | Result |
|---|---|---|---|
| AS-1 push allow/deny | `test_ordinary_task_branch_push_is_allowed`, `test_direct_main_push_is_hard_denied`, `test_direct_master_push_is_hard_denied`, `test_force_push_is_hard_denied`, `test_a_push_to_the_wrong_task_branch_is_denied`, `test_a_remote_identity_mismatch_is_denied` | Probe 1 (14 ref shapes) | **PASS** |
| AS-2 PR + green merge + 4 refusals | `test_pr_creation_works_and_is_journaled`, `test_ordinary_green_pr_auto_merges_and_records_the_sha`, `test_merge_refuses_on_a_failing_required_check`, `test_merge_refuses_on_a_secret_finding`, `test_merge_refuses_on_an_unresolved_blocking_finding`, `test_merge_refuses_on_a_stale_remote_sha`, `test_an_ineligible_merge_leaves_no_external_effect` | Probe 2 (10 single-condition refusals) | **PASS** |
| AS-3 Tier B without owner approval | `test_workflow_change_routes_...`, `test_dependency_change_routes_...`, `test_supervisor_code_routes_...`, `test_no_tier_b_routing_ever_requires_owner_approval`, `test_merge_blocks_until_the_required_specialist_review_passes`, `test_merge_proceeds_once_all_specialist_reviews_pass_no_owner` | Probe 3 | **PASS** (see OBS-2) |
| AS-4 cleanup only proven-merged | `test_a_proven_merged_task_branch_may_be_deleted`, `test_an_unmerged_task_branch_is_retained`, `test_the_default_branch_is_never_deleted`, `test_evidence_and_control_branches_are_retained`, `test_an_unrecognized_branch_shape_is_retained`, `test_the_current_worktree_branch_is_retained`, `test_flow_deletes_only_the_proven_merged_task_branch` | Probe 4 (18 branch shapes) | **PASS** |
| AS-5 crash reconciliation, no blind retry | `test_crash_mid_push_...`, `test_crash_mid_merge_leaves_a_pending_effect`, `test_a_second_merge_attempt_on_a_pending_effect_does_not_re_fire`, `test_reconciling_a_proven_merge_confirms_it_without_duplication`, `test_reconciling_a_merge_that_did_not_happen_is_safe_to_retry`, `test_an_unprovable_merge_pauses_rather_than_retrying`, `test_a_repeated_begin_after_a_crash_reuses_the_same_action_id`, `test_a_confirmed_push_is_not_pushed_again` | Probe 5 (double-replay) | **PASS** |

## 3. Per-§19.4-item results (all ten proven)

| # | §19.4 item | Named test | Result |
|---|---|---|---|
| 1 | ordinary task branch push auto-passes | `test_ordinary_task_branch_push_is_allowed` | PASS |
| 2 | main push hard-denies | `test_direct_main_push_is_hard_denied` | PASS |
| 3 | force push hard-denies | `test_force_push_is_hard_denied` | PASS |
| 4 | PR creation works | `test_pr_creation_works_and_is_journaled` | PASS |
| 5 | ordinary green PR auto-merges | `test_ordinary_green_pr_auto_merges_and_records_the_sha` | PASS |
| 6 | secret finding blocks | `test_merge_refuses_on_a_secret_finding` | PASS |
| 7 | stale remote SHA blocks **or** reconciles | block: `test_merge_refuses_on_a_stale_remote_sha`; reconcile: `test_divergence_reconciles_after_a_successful_refetch` | PASS (both directions) |
| 8 | workflow/dependency → specialist review, not owner | `test_no_tier_b_routing_ever_requires_owner_approval` (+ routing tests) | PASS |
| 9 | branch cleanup is safe | `test_flow_deletes_only_the_proven_merged_task_branch` (+ `BranchCleanupTests`) | PASS |
| 10 | crash during push/merge reconciled w/o blind retry | `test_crash_mid_merge_leaves_a_pending_effect` (+ `CrashReconciliationTests`) | PASS |

**Register meta-test break-glass — verified NOT a tautology.** `Section194RegisterTests.test_every_section_19_4_item_has_a_named_test` scans the file for `def test_\w+` and requires each of the 10 register fragments to match a real test def. I replicated its logic against mutated source: unmodified ⇒ `missing items: []`; after renaming `test_merge_refuses_on_a_secret_finding` ⇒ `missing items: ['secret_finding_blocks']`; after renaming `test_crash_mid_merge_leaves_a_pending_effect` ⇒ `missing items: ['crash_during_push_or_merge_reconciled']`. It genuinely fails if an item loses its test. `test_the_register_lists_all_ten_items` pins the count at 10.

**S5.5 ten merge conditions** each individually tested (`MergeEligibilityTests`, 16 tests) and `test_each_condition_has_both_directions` proves every predicate passes green and fails on mutation.

## 4. Adversarial probe results

**Probe 1 — push authorization (14 ref shapes).** `main`/`Main`/`MAIN`/`master`/`origin/main`/`refs/heads/main` all → `HARD_DENY push_to_main` (case-insensitive, suffix-aware); force → `force_push`; force+main → `force_push` (ordered first); empty/whitespace → `no_branch`; wrong branch → `unauthorized_branch`. `main2` is correctly **NOT** treated as main (allowed only as the authorized branch; else `unauthorized_branch`) — no false positive. See OBS-1 for the one soft spot.

**Probe 2 — ten single-condition merge refusals, each a distinct machine-readable code:** `not_authorized_or_dependency_invalid`, `changed_paths_outside_task`, `branch_not_mergeable`, `required_check_failing`, `secret_finding`, `specialist_review_missing`, `unresolved_blocking_finding`, `production_deploy`, `resulting_main_sha_not_recorded`, `task_state_not_transactional` (10 distinct). The branch-currency condition additionally distinguishes `stale_remote_sha` vs `remote_state_unknown` vs `branch_not_mergeable` by cause. No condition silently passes.

**Probe 3 — Tier B / unknown class.** workflow/lockfile/manifest/supervisor route to Tier B with correct review tuples, `owner_approval_required=False` in every case. **No reachable Tier B with empty required reviews** (checked all cases). No path ever sets owner approval. Ordinary/unknown/junk/empty paths → Tier A. See OBS-2 for the semantic-class coverage limitation.

**Probe 4 — cleanup.** Only `task/M0-T044-github-flow` when `merged_into_main=True` → `DELETE merged_task_branch`. Everything ambiguous is RETAINED: unmerged task branch, `main/master/origin/main/HEAD` (protected), `backup/main`/`evidence/x`/`release/1.0`/`hotfix/urgent` (unusual/evidence), `wip-experiment`/`TASK/upper`/`task/`/`task/../etc`/empty/whitespace/`task/x:main` (unrecognized), and the current worktree branch. Path-traversal and colon-refspec names are retained, never deleted.

**Probe 5 — crash double-replay no-op.** Crash mid-merge ⇒ 1 PENDING `github_pr_merge`. Replay #1 with a *healthy* runner ⇒ `performed=False`, `pending_effect_reconcile_first`, `runner.merges=[]`, still 1 row (same `action_id`). Replay #2 ⇒ identical no-op, still 1 row. After `reconcile→RECONCILED_OCCURRED` (status CONFIRMED), a further attempt ⇒ `already_merged`, `merges=[]`. No duplicate external effect is ever produced; a healthy runner does **not** re-fire a pending/confirmed merge.

**Probe 6 — shadow posture.** Default `ExternalEffectJournal(journal)` has `extra_specs={}` (constructor default unchanged). A plain live journal refuses `begin(effect_type="github_pr_merge", ...)` with `code=unmodeled_effect`, while still accepting the modeled `git_push_task_branch` — proving the capability is unreachable from an ordinary live-path journal and default behavior is intact. `github_pr_merge`: not in `MODELED_EFFECTS`, present in `SHADOW_EFFECT_SPECS`.

**Probe 7 — determinism.** `grep` of `github_flow.py` finds no `datetime`/`time`/`.now(`/`utcnow`/`random`/`monotonic`/`perf_counter`/`to_utc_iso`. `evaluate_merge`, `route_for_review`, `evaluate_branch_cleanup` return objects equal across repeated calls. Timestamps live only in the journal's audit layer, never inside a decision predicate.

## 5. Observations (non-blocking; recommended follow-ups — do NOT reopen this accepted scope)

**OBS-1 — Refspec parsing at the push boundary (Low; latent robustness).** `authorize_push` treats `PushPlan.branch` as a plain ref name. When `authorized_branch` is **empty**, a colon-refspec (`task/x:main`) or leading-`+` refspec (`+task:main`) is returned as `ALLOW task_branch_push_permitted` — the `:main` destination and `+` force token are not parsed. In all real usage `authorized_branch` is the exact task branch, so these are caught as `unauthorized_branch`; the ALLOW only occurs on caller misuse (empty `authorized_branch`). This is checks-only/shadow-only and execution is R595-gated. Recommendation for the future execution layer: validate `branch` as a bare ref (reject `:` and a leading `+`) and require a non-empty `authorized_branch`. Fails no AS/§19.4 item. (Same underlying gap as G3 MINOR-2 — pinned on the activation checklist.)

**OBS-2 — Merge-time specialist-review routing covers 3 of 11 S5.2 classes (Low–Medium; scope/activation).** `route_for_review` (hence merge-time `cond_specialist_reviews_pass`) mechanically detects only `github_actions_and_ci` (workflow), `dependencies_and_lockfiles` (lockfile/manifest), and `supervisor_code` (controller-path match). `policy.file_class` returns `"ordinary"` for auth/session code, DB migrations, schema additions, source connectors, legal-corpus, rule/scenario/survey code, and `"deploy_definition"` for `render.yaml` — none of which map to a Tier B class here, so they classify **Tier A (no required review)**. `SPECIALIST_REVIEW_TABLE` lists all 11 for completeness, but detection is wired for only 3+supervisor. **This is within this task's named scope** — AS-3 and the §19.4 item are specifically "workflow/dependency" and supervisor_code is an implemented bonus — so it does **not** fail the gate. It is, however, a material pre-activation limitation: were the automatic merge live, an auth/migration/schema/connector/legal/rule/scenario/survey/deploy change could auto-merge without its S5.2-mandated review. The module docstring's "intentionally absent" framing mentions only `deploy_definition` and understates that 8 enumerated S5.2 classes lack a detection path. Mitigations today: shadow-only, R595 not lifted; deploy partially covered by `cond_not_production_deploy` when the evidence collector sets `is_production_deploy`. Recommendation: a follow-up task to add semantic change-class detection for the remaining S5.2 classes, and to gate live activation on `route_for_review` no longer being the sole merge-time review authority for them. (Same finding as G3 MINOR-1 — pinned on the activation checklist.)

## 6. Verdict

**PASS.** All required runs are green and reproduced independently (57/57 new file ×2 runners ×2, full suite 1271 passed / 2 skipped, +57 with zero regressions, invariant-9 intact, project-control 22/22, directive-compliance 102/102, crash 32/32). Every AS-1..AS-5 and every one of the ten §19.4 items maps to a real executed proof, not a brush; the register meta-test is a genuine break-glass. The ten S5.5 single-condition refusals are each distinct and machine-readable; cleanup retains everything ambiguous; the crash double-replay is a strict no-op with no duplicate effect; the shadow posture holds (`github_pr_merge` absent from `MODELED_EFFECTS`, plain live journal refuses it, default constructor unchanged); decisions are deterministic and wall-clock-free. OBS-1 and OBS-2 are non-blocking and recorded as follow-ups; neither contradicts a named acceptance criterion for this shadow-only, R595-gated task.
