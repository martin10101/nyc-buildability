# G3 Code Review — M0-T044 "Automatic safe GitHub flow (0A.8 item 8; AD-077; Section 19.4 proofs)"

**Reviewer:** code-reviewer (independent, read-only)
**Task:** M0-T044 | **Branch/worktree:** `task/M0-T044-github-flow` @ `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
**Reviewed content SHA:** `af46b3e` (verified: `git diff af46b3e HEAD -- <code files>` is empty; later commits `0b40889`, `7437747` touch only `project-control/**`; working tree clean for all three reviewed files)
**Base:** `origin/main` `341fa4d`
**Posture verified:** SHADOW-ONLY; R595 activation gate not lifted; no live path imports `github_flow`.

## Verdict: **PASS** (with MINOR + ADVISORY findings; none blocking)

All five acceptance scenarios and all seven bound directive requirements are satisfied with reproducible evidence. The shadow posture is genuine and load-bearing. No BLOCKING or MAJOR defect found.

## Reproduction (run by me, not trusting the producer)

```
$ python -m pytest -q tools/test_agent_supervisor_github_flow.py
57 passed in 0.88s

$ python -m pytest -q tools/test_agent_supervisor_*.py
1271 passed, 2 skipped in 78.76s
```
Both match the producer's report exactly. Determinism confirmed: tests use temp-dir `DurableJournal`/`AuditLog` + a `RecordingRunner` fake; no network, no real git remote, no wall-clock read in any decision path.

**Scope compliance:** `af46b3e` touched only `tools/agent_supervisor/github_flow.py` (NEW), `tools/test_agent_supervisor_github_flow.py` (NEW), `tools/agent_supervisor/external_effects.py` (MODIFIED), `project-control/reports/M0-T044-producer-report.md`. All within `allowed_paths`; no `forbidden_paths` (`.github/`, `.claude/`, `apps/`, `services/`, `directives/`, manifests/lockfiles) touched. PASS.

## Critical-dimension findings

**1. S5.5 ten-condition completeness — PASS.** I re-derived the ten conditions from source-001.md §5.5 (lines 684–695). `MERGE_CONDITIONS` (github_flow.py:475–486) implements all ten in the directive's exact order, each as an independent predicate returning a `MergeCondition` with a machine-readable `reason_code`, and `evaluate_merge` ANDs all ten. Each is tested in both directions (`MergeEligibilityTests` + `test_each_condition_has_both_directions` + `test_all_ten_conditions_are_evaluated` which pins the name set). None is stubbed or merged away. Two conditions (`resulting_main_sha_recorded`, `task_state_updated_transactionally`, github_flow.py:455–470) are caller-supplied intent booleans rather than derived facts — acceptable at eligibility time, and the SHA recording is genuinely backed by behavior (`GitHubFlow.merge` calls `effects.confirm(resulting_state=resulting_sha)`, github_flow.py:748; `test_ordinary_green_pr_auto_merges_and_records_the_sha` asserts it). See ADVISORY-A.

**2. Hard-deny integrity (R007) — PASS.** `authorize_push` (github_flow.py:221–237) delegates deny logic to `push_policy.evaluate_push` and surfaces only HARD_DENY checks. Verified the preserved hard-denies: force push, `main`/`master`, `*/main` suffix (case-insensitive via `.lower()`), empty branch, unauthorized branch, remote-identity mismatch, suspected secret leakage. Cleanup regex `_TASK_BRANCH_RE` independently rejects refspec-shaped names (`main:main`, `+refs/...` → classified "unknown" → RETAIN). Fail-closed on unknown branch class in cleanup. See MINOR-2 for one defense-in-depth gap.

**3. Shadow posture — PASS (load-bearing claim verified).** `github_pr_merge` is NOT in `external_effects.MODELED_EFFECTS` (only the 5 pre-existing effects remain). D-007 invariant-9 test (`test_invariant_9_no_modeled_effect_performs_a_gated_action`, invariants.py:326: asserts no `"merge"`/`"deploy"` substring and non-destructive across `MODELED_EFFECTS`) still passes inside the green 1271-suite. A plain live journal refuses the merge as `unmodeled_effect` (`test_a_plain_journal_cannot_journal_a_merge`, reproduced). The `extra_specs` mechanism is only reachable via `shadow_effects_journal`, whose sole caller is the test harness (`JournalTestBase.effects`, test:167) — grep confirms no live module (`loop`, controller, bridge) imports `github_flow`/`GitHubFlow`/`shadow_effects_journal`. **external_effects.py diff is strictly additive and default-behavior-preserving:** the only changes are the `extra_specs` kwarg (defaults to `None`→`{}`), `_spec_for` (checks empty `extra_specs` then falls back to `spec_for`), and two call sites switching `spec_for`→`self._spec_for`. With no `extra_specs`, `_spec_for(x) == spec_for(x)` identically. Confirmed by the unchanged 1214→1271 (1214 baseline + 57 new) with zero pre-existing test status changes.

**4. Crash reconciliation (AS-5) — PASS.** `GitHubFlow` journals PENDING via `effects.begin` before the runner call; a crash leaves PENDING. `_guard` (github_flow.py:644–662) returns `pending`→refuse-and-reconcile, `confirmed`→idempotent no-repeat, `proceed` only on no-record. The idempotency key (`stable_action_id` over content digest) is deterministic across the crash, so `test_a_second_merge_attempt_on_a_pending_effect_does_not_re_fire` proves a healthy runner does NOT re-fire (`healthy.merges == []`). `reconcile` decides purely from journal record + injected read-only prober (occurred/not-occurred/None→pause), never wall-clock, never blind retry. All eight `CrashReconciliationTests` reproduced.

**5. Tier B routing (AS-3) — PASS for declared scope; see MINOR-1.** `SPECIALIST_REVIEW_TABLE` (github_flow.py:89–101) transcribes all 11 §5.2 rows correctly against source lines 631–643 (verified each mapping). `owner_approval_required` is a hard-coded `False` on `ReviewRouting` with no code path setting it True. Workflow/dependency/supervisor-code route to correct specialist sets and never to owner.

**6. Branch cleanup (AS-4) — PASS.** `evaluate_branch_cleanup` (github_flow.py:549–585) deletes only when `_classify_branch=="task"` AND caller proves `merged_into_main` AND not current-worktree branch. Protected default (`main`/`master`/`*/main`), retained markers (evidence/audit/anchor/control/release/backup/archive/hotfix/prod/production), unknown shapes, unmerged, and current-worktree all RETAIN. Deny-by-default on ambiguity confirmed (`"unrecognized_branch_shape"`). All `BranchCleanupTests` reproduced.

**7. Test quality — PASS.** 57 real tests, no vacuity: predicates asserted in both directions with distinct `reason_code`s; `Section194RegisterTests` maps all ten §19.4 items (source lines 1886–1895) to named tests and asserts `len==10`. The meta-test is a substring-existence guard (mildly weak) but each mapped test is a genuine assertion, so removal/rename breaks it. Good fixture isolation (`TemporaryDirectory` + `addCleanup`).

**8. Code quality — PASS.** Style consistent with the supervisor tree (row-citing docstrings, frozen dataclasses, `digest_of`/`stable_action_id` reuse, no deny-logic duplication — `authorize_push` is a thin classifier over `push_policy`). **The task-prompt's Pyright "unused names" claim does NOT reproduce:** `stable_action_id` is used at github_flow.py:672/698/756, `EFFECT_CONFIRMED` at :658, `EFFECT_PENDING` at :660, `digest_of` at :612, `ReconciliationResult` at :775. No dead imports.

## Findings

| ID | Severity | File:line | Finding |
|---|---|---|---|
| MINOR-1 | MINOR | github_flow.py:106–110, 128–144 | **Tier B change-class detection covers only 3 of 11 §5.2 classes.** `_FILE_CLASS_TO_CHANGE_CLASS` maps only `workflow`, `lockfile`, `dependency_manifest`; supervisor-code is caught by controller-path match. The 8 semantic §5.2 classes (auth/session code, additive DB migration, contract/schema addition, official-source connector, legal-corpus ingestion, draft-rule, scenario-calc, survey/PDF parser) — plus `deploy_definition` — are not derivable from `policy.file_class` and route as **Tier A (auto-permit), i.e. fail-open, not fail-toward-review**. Scenario: a PR editing `services/api/auth/session.py` (or `render.yaml`), with other conditions green, is `evaluate_merge`-eligible with `specialist_reviews_pass` vacuously satisfied. **Non-blocking:** AS-3/§19.4-item-8 explicitly scope to workflow/dependency (met and tested); shadow-only with no live consumer; the full table is present as forward data. **However this asymmetry is undisclosed in the producer's residuals** — the docstrings present `route_for_review` as routing "the S5.2 table" while only 3 classes reach it. Recommend: (a) disclose the detection scope in the report, and (b) before any live wiring, make undetected-but-sensitive classes fail toward review. |
| MINOR-2 | MINOR | github_flow.py:221–237 (via push_policy.py:154–170) | **`authorize_push` inherits push_policy's empty-`authorized_branch` fall-through.** When `plan.authorized_branch == ""`, push_policy's branch check reaches the `else → AUTO` arm for any non-`main`/non-empty branch name, so `authorize_push` ALLOWs it. `main`/`master`/`*/main` and force remain HARD_DENY regardless, so the core R007 protection holds; the residual is a refspec like `"main:main"` only if the grant's `authorized_branch` itself equals it. Pre-existing push_policy behavior, not introduced here. Recommend `authorize_push` assert a non-empty `authorized_branch` as defense-in-depth. |
| ADVISORY-A | ADVISORY | github_flow.py:455–470 | §5.5 conditions 9/10 (`resulting_main_sha_recorded`, `task_state_transactional`) are caller-supplied intent booleans at eligibility time. Acceptable (condition 9 is genuinely backed by `merge()` journaling the resulting SHA), but they are promises, not derived facts; a live caller must set them honestly. |
| ADVISORY-B | ADVISORY | authorize_push docstring | `authorize_push` intentionally collapses all non-HARD_DENY push checks (sensitive-path/workflow/deploy/remote-head-divergence ASKs) to ALLOW for a task-branch push. Defensible (task-branch, not `main`; gating deferred to merge/review), but worth noting the merge-time routing gap in MINOR-1 is where those ASK classes would need to be re-caught. |

## Per-requirement verdicts

| Req | Verdict | Evidence |
|---|---|---|
| D-010-R006 (no owner approval, routine flow) | **PASS** | `ReviewRouting.owner_approval_required` hard-`False`, no predicate consults owner approval; `test_no_tier_b_routing_ever_requires_owner_approval`, `test_merge_proceeds_once_all_specialist_reviews_pass_no_owner`. |
| D-010-R007 (PRs + protected main) | **PASS** | main/master/`*/main`/force HARD_DENY (`PushAuthorizationTests`); PR is first-class via `github_pr_create`; merge only via PR record. See MINOR-2 (defense-in-depth). |
| D-010-R010 (continue on noncritical block) | **PASS** | Refusals are structured `FlowResult(performed=False, reason_code=…)` data, not exceptions; `test_an_ineligible_merge_leaves_no_external_effect` (no journal residue). Continue-loop lives in the loop layer (honestly disclosed as out-of-scope). |
| D-010-R077 (prove the flow) | **PASS** | Ten §19.4 items → named tests + register meta-test; ten §5.5 predicates both directions; crash reconciliation idempotent/no-blind-retry; 57 + 1271/2 reproduced. |
| D-010-R093 (nothing speculative) | **PASS** | Surface = exactly §19.4/§5.5/§5.2; `github_pr_merge` kept out of live `MODELED_EFFECTS` (invariant 9 intact); live journal refuses merge as `unmodeled_effect`; no live wiring. |
| D-010-R116 (session-2 re-dispatch) | **PASS** | Acknowledge-only; no new obligations; holds/shadow/R595 untouched. |
| D-010-R117 (session-3 re-dispatch) | **PASS** | Acknowledge-only; no new obligations; dormant batches and holds untouched. |

## Per-AS verdicts

| AS | Verdict | Evidence |
|---|---|---|
| AS-1 (task push allow; main/force hard-deny) | **PASS** | `PushAuthorizationTests` (6): task-branch allow; main, master, force, wrong-branch, remote-identity all deny. |
| AS-2 (PR + green merge; refuse per condition) | **PASS** | `PullRequestCreationTests`, `GreenMergePathTests`, `MergeEligibilityTests` (16), `RemoteReconciliationTests` — refuses on failing check / no check / secret / blocking finding / stale SHA / unknown remote / not-mergeable / production deploy / paths-escape / unauthorized. |
| AS-3 (workflow/dependency → specialist review, no owner) | **PASS** (declared scope) | `ReviewRoutingTests` (7). See MINOR-1 re: the 8 undetected semantic classes. |
| AS-4 (delete only proven-merged task branches) | **PASS** | `BranchCleanupTests` (6) + `BranchCleanupOrchestrationTests`. |
| AS-5 (crash reconciled, no blind retry) | **PASS** | `CrashReconciliationTests` (8) + `ShadowPostureTests` (3). |

## Summary

The delivered shadow proof is sound, deterministic, and honestly scoped. The shadow posture (merge effect deliberately excluded from the live registry; additive, behavior-preserving `external_effects` change; no live importer) is the load-bearing safety claim and it holds. The two MINOR findings are forward-looking completeness/defense-in-depth items that do not compromise the scoped acceptance criteria and require no rework to accept this task; MINOR-1 warrants a one-line disclosure in the record and a note for whoever eventually wires `route_for_review` into a live path (fail-toward-review for undetected sensitive classes).

**Recommended gate result: PASS.**

## Orchestrator note (disclosure per MINOR-1 recommendation)

MINOR-1 (Tier B detection scope: 3 of 11 classes derivable; remainder fail-open pending a semantic
classifier) and MINOR-2 (empty-`authorized_branch` fall-through) are hereby disclosed in the task
record and REGISTERED on `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` as pre-activation
MUST-RESOLVE items for the GitHub flow. Shadow-only posture makes both non-blocking for this
acceptance; neither may survive into live wiring.
