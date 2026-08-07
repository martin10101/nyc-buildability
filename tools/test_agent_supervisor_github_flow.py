#!/usr/bin/env python3
"""Executable proofs for the automatic ordinary GitHub flow (D-010 S5, S19.4).

SHADOW-ONLY. Every proof runs against fakes / fixture state: a `RecordingRunner`
stands in for git/gh and journals nothing to a real remote, and the crash proofs
use the same journal-close/reopen technique the phase-4 crash suite uses. No test
here contacts a real remote, and nothing lifts the R595 activation gate.

Directed capability under the supervisor freeze (0A.8 item 8; AD-006/AD-007/
AD-077). The ten-item D-010 Section 19.4 list is the acceptance backbone; the
`Section194RegisterTests` meta-test proves every list item maps to a named test.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import external_effects as ex  # noqa: E402
from tools.agent_supervisor import github_flow as gf  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.push_policy import PushPlan  # noqa: E402

REMOTE = "https://github.com/acme/buildability"
BRANCH = "task/M0-T044-github-flow"
HEAD = "a" * 40
REMOTE_HEAD = "b" * 40


def clean_push_plan(**overrides) -> PushPlan:
    """A PushPlan for an ordinary, clean, exact-task-branch push."""
    base = dict(
        remote_name="origin", remote_url=REMOTE, expected_remote_url=REMOTE,
        branch=BRANCH, authorized_branch=BRANCH, local_head=HEAD,
        expected_remote_head=REMOTE_HEAD, observed_remote_head=REMOTE_HEAD,
        changed_paths=("services/api/app.py", "tests/test_app.py"),
        force=False, mode="shadow", remote_state_known=True)
    base.update(overrides)
    return PushPlan(**base)


def green_merge_request(**overrides) -> gf.MergeRequest:
    """A MergeRequest whose ten S5.5 conditions all hold (ordinary product code)."""
    base = dict(
        task_id="M0-T044", task_authorized=True, dependency_valid=True,
        changed_paths=("services/api/app.py", "tests/test_app.py"),
        task_allowed_paths=("services/api/**", "tests/**"),
        required_checks={"unit": True, "lint": True, "ci": True},
        secret_scan_findings=(), completed_reviews={}, blocking_findings=(),
        is_production_deploy=False, will_record_main_sha=True,
        task_state_transactional=True,
        expected_remote_head=REMOTE_HEAD, observed_remote_head=REMOTE_HEAD,
        remote_state_known=True, mergeable=True)
    base.update(overrides)
    return gf.MergeRequest(**base)


class RecordingRunner:
    """A dry-run GitHub runner. Records calls; performs no real side effect.

    `fail_on` names a step whose call raises, simulating a crash mid-effect.
    """

    def __init__(self, *, fail_on: str = "", merged_sha: str = "c" * 40) -> None:
        self.fail_on = fail_on
        self.merged_sha = merged_sha
        self.pushes: list[str] = []
        self.prs: list[dict] = []
        self.merges: list[str] = []
        self.deletes: list[str] = []

    def push_task_branch(self, plan: PushPlan) -> str:
        if self.fail_on == "push":
            raise RuntimeError("simulated crash mid-push")
        self.pushes.append(plan.branch)
        return plan.local_head

    def create_pull_request(self, *, task_id: str, head: str, base: str,
                            title: str) -> str:
        if self.fail_on == "pr":
            raise RuntimeError("simulated crash mid-pr")
        ref = f"pr/{len(self.prs) + 1}"
        self.prs.append({"ref": ref, "head": head, "base": base})
        return ref

    def merge_pull_request(self, *, pr_ref: str, base_sha: str) -> str:
        if self.fail_on == "merge":
            raise RuntimeError("simulated crash mid-merge")
        self.merges.append(pr_ref)
        return self.merged_sha

    def delete_branch(self, branch: str) -> None:
        self.deletes.append(branch)


# ==========================================================================
# AS-1 - push authorization (D-010 S19.4: task push auto-passes; main/force deny)
# ==========================================================================


class PushAuthorizationTests(unittest.TestCase):
    def test_ordinary_task_branch_push_is_allowed(self) -> None:
        auth = gf.authorize_push(clean_push_plan())
        self.assertTrue(auth.allowed)
        self.assertEqual(auth.decision, gf.PUSH_ALLOW)
        self.assertEqual(auth.reason_code, "task_branch_push_permitted")

    def test_direct_main_push_is_hard_denied(self) -> None:
        auth = gf.authorize_push(clean_push_plan(branch="main", authorized_branch=""))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.decision, gf.PUSH_HARD_DENY)
        self.assertEqual(auth.reason_code, "push_to_main")

    def test_direct_master_push_is_hard_denied(self) -> None:
        auth = gf.authorize_push(clean_push_plan(branch="master", authorized_branch=""))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.reason_code, "push_to_main")

    def test_force_push_is_hard_denied(self) -> None:
        auth = gf.authorize_push(clean_push_plan(force=True))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.decision, gf.PUSH_HARD_DENY)
        self.assertEqual(auth.reason_code, "force_push")

    def test_a_push_to_the_wrong_task_branch_is_denied(self) -> None:
        auth = gf.authorize_push(clean_push_plan(branch="task/other"))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.reason_code, "unauthorized_branch")

    def test_a_remote_identity_mismatch_is_denied(self) -> None:
        auth = gf.authorize_push(clean_push_plan(remote_url="https://evil.example/x"))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.reason_code, "remote_identity_mismatch")

    def test_an_empty_authorized_branch_is_denied(self) -> None:
        """D-010 MINOR-2 defense-in-depth: an empty `authorized_branch` let
        push_policy fall through to ALLOW for any non-main branch. authorize_push
        now asserts a non-empty authorized branch."""
        auth = gf.authorize_push(
            clean_push_plan(branch="task/M0-T044-github-flow", authorized_branch=""))
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.decision, gf.PUSH_HARD_DENY)
        self.assertEqual(auth.reason_code, "no_authorized_branch")

    def test_main_and_force_stay_denied_even_with_an_empty_authorized_branch(self) -> None:
        # The new guard must not mask the pre-existing hard-denies: main/master/
        # force keep their own reason codes when authorized_branch is empty.
        self.assertEqual(
            gf.authorize_push(clean_push_plan(branch="main", authorized_branch="")).reason_code,
            "push_to_main")
        self.assertEqual(
            gf.authorize_push(clean_push_plan(force=True, authorized_branch="")).reason_code,
            "force_push")


# ==========================================================================
# AS-2 - PR creation + green-PR merge; refuse on each blocking condition
# ==========================================================================


class JournalTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.db = self.tmp / "journal.sqlite3"
        self.audit_path = self.tmp / "audit.jsonl"
        self.journal = DurableJournal(self.db).open()
        self.audit = AuditLog(self.audit_path, fsync=True)
        self.addCleanup(self._close)

    def _close(self) -> None:
        try:
            self.journal.close()
        except Exception:  # pragma: no cover
            pass

    def effects(self) -> ex.ExternalEffectJournal:
        # Shadow-scoped journal: it resolves the github_pr_merge spec from
        # SHADOW_EFFECT_SPECS without ever touching the production registry.
        return gf.shadow_effects_journal(self.journal, audit=self.audit)

    def flow(self, runner: RecordingRunner) -> gf.GitHubFlow:
        return gf.GitHubFlow(self.effects(), runner, task_id="M0-T044")

    def crash(self) -> None:
        """Kill the process as far as durable state is concerned."""
        self.journal.close()
        self.journal = DurableJournal(self.db).open()
        self.audit = AuditLog(self.audit_path, fsync=True)


class PullRequestCreationTests(JournalTestBase):
    def test_pr_creation_works_and_is_journaled(self) -> None:
        runner = RecordingRunner()
        result = self.flow(runner).create_pull_request(
            head=BRANCH, base="main", title="M0-T044")
        self.assertTrue(result.performed)
        self.assertEqual(result.reason_code, "pr_created")
        self.assertEqual(len(runner.prs), 1)
        stored = self.journal.get_effect(result.action_id)
        self.assertEqual(stored.status, "CONFIRMED")
        self.assertEqual(stored.resulting_state, "pr/1")


class MergeEligibilityTests(unittest.TestCase):
    def test_ordinary_green_pr_is_eligible(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request())
        self.assertTrue(evaluation.eligible, evaluation.refusal_codes())
        self.assertEqual(evaluation.refusals(), ())

    def test_all_ten_conditions_are_evaluated(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request())
        self.assertEqual(len(evaluation.conditions), 10)
        names = {c.name for c in evaluation.conditions}
        self.assertEqual(names, {
            "authorized_and_dependency_valid", "changed_paths_fit_task",
            "branch_current_enough", "required_checks_pass", "secret_scan_clean",
            "specialist_reviews_pass", "no_unresolved_blocking_finding",
            "not_production_deploy", "resulting_main_sha_recorded",
            "task_state_updated_transactionally"})

    def test_merge_refuses_on_a_failing_required_check(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(
            required_checks={"unit": True, "lint": False}))
        self.assertFalse(evaluation.eligible)
        self.assertIn("required_check_failing", evaluation.refusal_codes())

    def test_merge_refuses_when_no_required_check_ran(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(required_checks={}))
        self.assertFalse(evaluation.eligible)
        self.assertIn("no_required_checks", evaluation.refusal_codes())

    def test_merge_refuses_on_a_secret_finding(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(
            secret_scan_findings=("aws_key in services/api/app.py",)))
        self.assertFalse(evaluation.eligible)
        self.assertIn("secret_finding", evaluation.refusal_codes())

    def test_merge_refuses_on_an_unresolved_blocking_finding(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(
            blocking_findings=("unverified legal claim",)))
        self.assertFalse(evaluation.eligible)
        self.assertIn("unresolved_blocking_finding", evaluation.refusal_codes())

    def test_merge_refuses_on_a_stale_remote_sha(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(
            observed_remote_head="d" * 40))  # remote advanced under us
        self.assertFalse(evaluation.eligible)
        self.assertIn("stale_remote_sha", evaluation.refusal_codes())

    def test_merge_refuses_when_remote_state_is_unknown(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(remote_state_known=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("remote_state_unknown", evaluation.refusal_codes())

    def test_merge_refuses_when_not_authorized(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(task_authorized=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("not_authorized_or_dependency_invalid", evaluation.refusal_codes())

    def test_merge_refuses_when_dependency_invalid(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(dependency_valid=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("not_authorized_or_dependency_invalid", evaluation.refusal_codes())

    def test_merge_refuses_when_changed_paths_escape_the_task(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(
            changed_paths=("services/api/app.py", "apps/web/secret.ts")))
        self.assertFalse(evaluation.eligible)
        self.assertIn("changed_paths_outside_task", evaluation.refusal_codes())

    def test_merge_refuses_when_the_branch_does_not_merge_cleanly(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(mergeable=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("branch_not_mergeable", evaluation.refusal_codes())

    def test_merge_refuses_a_production_deployment(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(is_production_deploy=True))
        self.assertFalse(evaluation.eligible)
        self.assertIn("production_deploy", evaluation.refusal_codes())

    def test_merge_refuses_when_the_resulting_sha_would_not_be_recorded(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(will_record_main_sha=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("resulting_main_sha_not_recorded", evaluation.refusal_codes())

    def test_merge_refuses_when_the_state_update_is_not_transactional(self) -> None:
        evaluation = gf.evaluate_merge(green_merge_request(task_state_transactional=False))
        self.assertFalse(evaluation.eligible)
        self.assertIn("task_state_not_transactional", evaluation.refusal_codes())

    def test_each_condition_has_both_directions(self) -> None:
        # Every predicate passes on the green request and fails on a mutation.
        for cond in gf.MERGE_CONDITIONS:
            self.assertTrue(cond(green_merge_request()).ok, cond.__name__)


class GreenMergePathTests(JournalTestBase):
    def test_ordinary_green_pr_auto_merges_and_records_the_sha(self) -> None:
        runner = RecordingRunner(merged_sha="e" * 40)
        result = self.flow(runner).merge(
            green_merge_request(), pr_ref="pr/1", base_sha=REMOTE_HEAD)
        self.assertTrue(result.performed)
        self.assertEqual(result.reason_code, "merged")
        self.assertEqual(result.resulting_state, "e" * 40)
        self.assertEqual(runner.merges, ["pr/1"])
        stored = self.journal.get_effect(result.action_id)
        self.assertEqual(stored.status, "CONFIRMED")

    def test_an_ineligible_merge_leaves_no_external_effect(self) -> None:
        runner = RecordingRunner()
        result = self.flow(runner).merge(
            green_merge_request(secret_scan_findings=("leak",)),
            pr_ref="pr/1", base_sha=REMOTE_HEAD)
        self.assertFalse(result.performed)
        self.assertEqual(result.reason_code, "merge_ineligible")
        self.assertEqual(runner.merges, [])
        self.assertEqual(self.journal.pending_effects(), [])


# ==========================================================================
# AS-2 (reconcile branch) - stale remote SHA reconciliation, no blind retry
# ==========================================================================


class RemoteReconciliationTests(unittest.TestCase):
    def test_agreeing_heads_may_proceed(self) -> None:
        outcome = gf.reconcile_remote_sha(
            expected_head=REMOTE_HEAD, observed_head=REMOTE_HEAD, remote_state_known=True)
        self.assertTrue(outcome.may_proceed)
        self.assertEqual(outcome.reason_code, "remote_head_current")

    def test_unknown_remote_blocks(self) -> None:
        outcome = gf.reconcile_remote_sha(
            expected_head=REMOTE_HEAD, observed_head="", remote_state_known=False)
        self.assertFalse(outcome.may_proceed)
        self.assertEqual(outcome.reason_code, "remote_state_unknown")

    def test_divergence_without_a_refetch_blocks_and_is_not_retried(self) -> None:
        outcome = gf.reconcile_remote_sha(
            expected_head=REMOTE_HEAD, observed_head="d" * 40, remote_state_known=True)
        self.assertFalse(outcome.may_proceed)
        self.assertEqual(outcome.reason_code, "stale_remote_sha")

    def test_divergence_reconciles_after_a_successful_refetch(self) -> None:
        outcome = gf.reconcile_remote_sha(
            expected_head=REMOTE_HEAD, observed_head="d" * 40, remote_state_known=True,
            refetch=lambda: (True, "d" * 40))
        self.assertTrue(outcome.may_proceed)
        self.assertEqual(outcome.reason_code, "reconciled_after_refetch")
        self.assertEqual(outcome.verified_head, "d" * 40)

    def test_divergence_that_does_not_reconcile_stays_blocked(self) -> None:
        outcome = gf.reconcile_remote_sha(
            expected_head=REMOTE_HEAD, observed_head="d" * 40, remote_state_known=True,
            refetch=lambda: (False, "f" * 40))
        self.assertFalse(outcome.may_proceed)
        self.assertEqual(outcome.reason_code, "stale_after_refetch")


# ==========================================================================
# AS-3 - Tier B routing WITHOUT owner approval (D-010 S5.2)
# ==========================================================================


class ReviewRoutingTests(unittest.TestCase):
    def test_ordinary_paths_are_tier_a_with_no_review(self) -> None:
        routing = gf.route_for_review(("services/api/app.py", "docs/readme.md"))
        self.assertEqual(routing.tier, "A")
        self.assertEqual(routing.required_reviews, ())
        self.assertFalse(routing.owner_approval_required)

    def test_workflow_change_routes_to_security_and_control_plane(self) -> None:
        routing = gf.route_for_review((".github/workflows/ci.yml",))
        self.assertEqual(routing.tier, "B")
        self.assertIn("github_actions_and_ci", routing.change_classes)
        self.assertEqual(routing.review_set(), frozenset({"security", "control-plane"}))
        self.assertFalse(routing.owner_approval_required)

    def test_dependency_change_routes_to_dependency_security_and_ci(self) -> None:
        routing = gf.route_for_review(("package-lock.json", "package.json"))
        self.assertEqual(routing.tier, "B")
        self.assertIn("dependencies_and_lockfiles", routing.change_classes)
        self.assertEqual(routing.review_set(),
                         frozenset({"dependency-security", "ci"}))
        self.assertFalse(routing.owner_approval_required)

    def test_supervisor_code_routes_to_control_plane_security_crash_replay(self) -> None:
        routing = gf.route_for_review(("tools/agent_supervisor/github_flow.py",))
        self.assertEqual(routing.tier, "B")
        self.assertIn("supervisor_code", routing.change_classes)
        self.assertEqual(routing.review_set(),
                         frozenset({"control-plane", "security", "crash-replay"}))
        self.assertFalse(routing.owner_approval_required)

    def test_no_tier_b_routing_ever_requires_owner_approval(self) -> None:
        for paths in [(".github/workflows/ci.yml",), ("package-lock.json",),
                      ("tools/agent_supervisor/loop.py",)]:
            self.assertFalse(gf.route_for_review(paths).owner_approval_required)

    def test_merge_blocks_until_the_required_specialist_review_passes(self) -> None:
        req = green_merge_request(
            changed_paths=(".github/workflows/ci.yml",),
            task_allowed_paths=(".github/workflows/**",),
            completed_reviews={"security": True})  # control-plane still missing
        evaluation = gf.evaluate_merge(req)
        self.assertFalse(evaluation.eligible)
        self.assertIn("specialist_review_missing", evaluation.refusal_codes())

    def test_merge_proceeds_once_all_specialist_reviews_pass_no_owner(self) -> None:
        req = green_merge_request(
            changed_paths=(".github/workflows/ci.yml",),
            task_allowed_paths=(".github/workflows/**",),
            completed_reviews={"security": True, "control-plane": True})
        evaluation = gf.evaluate_merge(req)
        self.assertTrue(evaluation.eligible, evaluation.refusal_codes())


# ==========================================================================
# AS-4 - branch cleanup safety (D-010 S5.4)
# ==========================================================================


class BranchCleanupTests(unittest.TestCase):
    def test_a_proven_merged_task_branch_may_be_deleted(self) -> None:
        decision = gf.evaluate_branch_cleanup(branch=BRANCH, merged_into_main=True)
        self.assertTrue(decision.may_delete)
        self.assertEqual(decision.reason_code, "merged_task_branch")

    def test_an_unmerged_task_branch_is_retained(self) -> None:
        decision = gf.evaluate_branch_cleanup(branch=BRANCH, merged_into_main=False)
        self.assertFalse(decision.may_delete)
        self.assertEqual(decision.reason_code, "not_proven_merged")

    def test_the_default_branch_is_never_deleted(self) -> None:
        for name in ("main", "master", "origin/main"):
            decision = gf.evaluate_branch_cleanup(branch=name, merged_into_main=True)
            self.assertFalse(decision.may_delete)
            self.assertEqual(decision.reason_code, "protected_default_branch")

    def test_evidence_and_control_branches_are_retained(self) -> None:
        for name in ("evidence/M0-T036", "audit-anchor", "control/state",
                     "release/1.0", "backup/main"):
            decision = gf.evaluate_branch_cleanup(branch=name, merged_into_main=True)
            self.assertFalse(decision.may_delete)
            self.assertEqual(decision.reason_code, "unusual_or_evidence_branch")

    def test_an_unrecognized_branch_shape_is_retained(self) -> None:
        decision = gf.evaluate_branch_cleanup(branch="wip-experiment",
                                              merged_into_main=True)
        self.assertFalse(decision.may_delete)
        self.assertEqual(decision.reason_code, "unrecognized_branch_shape")

    def test_the_current_worktree_branch_is_retained(self) -> None:
        decision = gf.evaluate_branch_cleanup(
            branch=BRANCH, merged_into_main=True, is_current_worktree_branch=True)
        self.assertFalse(decision.may_delete)
        self.assertEqual(decision.reason_code, "current_worktree_branch")


class BranchCleanupOrchestrationTests(JournalTestBase):
    def test_flow_deletes_only_the_proven_merged_task_branch(self) -> None:
        runner = RecordingRunner()
        flow = self.flow(runner)
        merged = flow.cleanup_branch(branch=BRANCH, merged_into_main=True)
        unmerged = flow.cleanup_branch(branch="task/other", merged_into_main=False)
        evidence = flow.cleanup_branch(branch="evidence/x", merged_into_main=True)
        self.assertTrue(merged.performed)
        self.assertFalse(unmerged.performed)
        self.assertFalse(evidence.performed)
        self.assertEqual(runner.deletes, [BRANCH])


# ==========================================================================
# AS-5 - crash mid-push / mid-merge reconciled without blind retry
# ==========================================================================


class CrashReconciliationTests(JournalTestBase):
    def test_crash_mid_push_leaves_a_pending_effect_reconciled_not_retried(self) -> None:
        runner = RecordingRunner(fail_on="push")
        with self.assertRaises(RuntimeError):
            self.flow(runner).push(clean_push_plan())
        # The before-record is durable; the effect is PENDING after the crash.
        self.crash()
        pending = self.journal.pending_effects()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].effect_type, "git_push_task_branch")
        # A pending effect is never blindly retried.
        with self.assertRaises(ex.ExternalEffectError):
            self.effects().assert_safe_to_retry(pending[0].action_id)

    def test_crash_mid_merge_leaves_a_pending_effect(self) -> None:
        runner = RecordingRunner(fail_on="merge")
        with self.assertRaises(RuntimeError):
            self.flow(runner).merge(green_merge_request(), pr_ref="pr/1",
                                    base_sha=REMOTE_HEAD)
        self.crash()
        pending = self.journal.pending_effects()
        self.assertEqual([p.effect_type for p in pending], ["github_pr_merge"])
        with self.assertRaises(ex.ExternalEffectError):
            self.effects().assert_safe_to_retry(pending[0].action_id)

    def test_a_second_merge_attempt_on_a_pending_effect_does_not_re_fire(self) -> None:
        crashed = RecordingRunner(fail_on="merge")
        with self.assertRaises(RuntimeError):
            self.flow(crashed).merge(green_merge_request(), pr_ref="pr/1",
                                     base_sha=REMOTE_HEAD)
        self.crash()
        # A NEW runner that would succeed - proving we do NOT blindly re-fire.
        healthy = RecordingRunner()
        result = self.flow(healthy).merge(green_merge_request(), pr_ref="pr/1",
                                          base_sha=REMOTE_HEAD)
        self.assertFalse(result.performed)
        self.assertEqual(result.reason_code, "pending_effect_reconcile_first")
        self.assertEqual(healthy.merges, [], "the merge must not have been re-fired")

    def test_reconciling_a_proven_merge_confirms_it_without_duplication(self) -> None:
        crashed = RecordingRunner(fail_on="merge")
        action_id = self.flow(crashed).merge_action_id(pr_ref="pr/1", base_sha=REMOTE_HEAD)
        with self.assertRaises(RuntimeError):
            self.flow(crashed).merge(green_merge_request(), pr_ref="pr/1",
                                     base_sha=REMOTE_HEAD)
        self.crash()
        # Read-only evidence proves the merge landed on main.
        verdict = self.effects().reconcile(action_id,
                                           prober=lambda _r: (True, "z" * 40))
        self.assertEqual(verdict.status, ex.RECONCILED_OCCURRED)
        self.assertFalse(verdict.safe_to_retry)
        self.assertEqual(self.journal.get_effect(action_id).status, "CONFIRMED")
        # After reconciliation a further merge is idempotent, never a duplicate.
        healthy = RecordingRunner()
        result = self.flow(healthy).merge(green_merge_request(), pr_ref="pr/1",
                                          base_sha=REMOTE_HEAD)
        self.assertFalse(result.performed)
        self.assertEqual(result.reason_code, "already_merged")
        self.assertEqual(healthy.merges, [])

    def test_reconciling_a_merge_that_did_not_happen_is_safe_to_retry(self) -> None:
        crashed = RecordingRunner(fail_on="merge")
        action_id = self.flow(crashed).merge_action_id(pr_ref="pr/1", base_sha=REMOTE_HEAD)
        with self.assertRaises(RuntimeError):
            self.flow(crashed).merge(green_merge_request(), pr_ref="pr/1",
                                     base_sha=REMOTE_HEAD)
        self.crash()
        verdict = self.effects().reconcile(action_id,
                                           prober=lambda _r: (False, "main unchanged"))
        self.assertEqual(verdict.status, ex.RECONCILED_NOT_OCCURRED)
        self.assertTrue(verdict.safe_to_retry)

    def test_an_unprovable_merge_pauses_rather_than_retrying(self) -> None:
        crashed = RecordingRunner(fail_on="merge")
        action_id = self.flow(crashed).merge_action_id(pr_ref="pr/1", base_sha=REMOTE_HEAD)
        with self.assertRaises(RuntimeError):
            self.flow(crashed).merge(green_merge_request(), pr_ref="pr/1",
                                     base_sha=REMOTE_HEAD)
        self.crash()
        verdict = self.effects().reconcile(action_id,
                                           prober=lambda _r: (None, "unreachable"))
        self.assertTrue(verdict.requires_pause)
        self.assertFalse(verdict.safe_to_retry)
        self.assertEqual(self.journal.get_effect(action_id).status, "PENDING")

    def test_a_repeated_begin_after_a_crash_reuses_the_same_action_id(self) -> None:
        crashed = RecordingRunner(fail_on="merge")
        action_id = self.flow(crashed).merge_action_id(pr_ref="pr/1", base_sha=REMOTE_HEAD)
        with self.assertRaises(RuntimeError):
            self.flow(crashed).merge(green_merge_request(), pr_ref="pr/1",
                                     base_sha=REMOTE_HEAD)
        self.crash()
        # The reconcile-first guard keeps a re-attempt from minting a second row.
        self.flow(RecordingRunner()).merge(green_merge_request(), pr_ref="pr/1",
                                           base_sha=REMOTE_HEAD)
        self.assertEqual(len(self.journal.pending_effects()), 1)
        self.assertEqual(self.journal.pending_effects()[0].action_id, action_id)

    def test_a_confirmed_push_is_not_pushed_again(self) -> None:
        runner = RecordingRunner()
        first = self.flow(runner).push(clean_push_plan())
        self.assertTrue(first.performed)
        self.crash()
        again = self.flow(RecordingRunner()).push(clean_push_plan())
        self.assertFalse(again.performed)
        self.assertEqual(again.reason_code, "already_pushed")


# ==========================================================================
# Shadow-only posture - the merge is NOT wired into the live path
# ==========================================================================


class ShadowPostureTests(unittest.TestCase):
    def test_the_merge_effect_is_not_in_the_production_registry(self) -> None:
        # D-007 invariant 9 keeps MODELED_EFFECTS (the live-path authority) free
        # of any merge/deploy effect. The merge is only a shadow-scoped spec.
        self.assertNotIn("github_pr_merge", ex.MODELED_EFFECTS)
        self.assertIn("github_pr_merge", gf.SHADOW_EFFECT_SPECS)

    def test_a_plain_journal_cannot_journal_a_merge(self) -> None:
        # Without the shadow spec, a merge effect is refused as unmodeled - proof
        # the capability is not reachable from an ordinary live-path journal.
        with tempfile.TemporaryDirectory() as tmp:
            db = pathlib.Path(tmp) / "j.sqlite3"
            journal = DurableJournal(db).open()
            try:
                plain = ex.ExternalEffectJournal(journal)
                with self.assertRaises(ex.ExternalEffectError) as ctx:
                    plain.begin(effect_type="github_pr_merge", target="pr/1",
                                task_id="M0-T044", request_digest="d",
                                prior_state_reader=lambda: REMOTE_HEAD)
                self.assertEqual(ctx.exception.code, "unmodeled_effect")
            finally:
                journal.close()

    def test_the_shadow_merge_spec_is_not_destructive(self) -> None:
        self.assertFalse(gf.SHADOW_EFFECT_SPECS["github_pr_merge"].destructive)


# ==========================================================================
# C1 (G3 MINOR-1 / G5 SEC-2) - Tier routing CATCH-ALL: fail toward review
# ==========================================================================


class Section52CatchAllRoutingTests(unittest.TestCase):
    """Every detectable security-relevant change fails TOWARD review; only
    ordinary product code/docs/tests stays Tier A (D-010 SEC-2 / MINOR-1)."""

    def test_permission_and_hook_configuration_are_tier_d_owner_stop(self) -> None:
        for path in (".claude/settings.json", ".claude/rules/x.md",
                     ".claude/agents/y.md", ".pre-commit-config.yaml"):
            with self.subTest(path=path):
                routing = gf.route_for_review((path,))
                self.assertEqual(routing.tier, "D", path)
                self.assertTrue(routing.owner_stop, path)
                self.assertFalse(routing.owner_approval_required, path)

    def test_other_security_relevant_classes_fail_toward_review_not_tier_a(self) -> None:
        for path in (".env", "scripts/setup.sh", ".gitmodules", ".gitattributes",
                     "render.yaml"):
            with self.subTest(path=path):
                routing = gf.route_for_review((path,))
                self.assertEqual(routing.tier, "B", path)
                self.assertEqual(routing.review_set(),
                                 frozenset({"control-plane", "security"}), path)
                self.assertFalse(routing.owner_approval_required, path)

    def test_ordinary_product_code_is_still_tier_a(self) -> None:
        for path in ("services/api/app.py", "tests/test_app.py",
                     "docs/readme.md", "apps/web/page.tsx"):
            with self.subTest(path=path):
                self.assertEqual(gf.route_for_review((path,)).tier, "A", path)

    def test_no_security_relevant_class_ever_routes_tier_a(self) -> None:
        """Anti-drift: a representative path for EVERY SECURITY_RELEVANT_CLASSES
        entry must route away from Tier A (the catch-all is derived from that set
        so it cannot silently fall behind the policy table)."""
        from tools.agent_supervisor.policy import (
            FILE_CLASS_PATTERNS, SECURITY_RELEVANT_CLASSES)
        first_pattern = {name: patterns[0] for name, patterns in FILE_CLASS_PATTERNS}
        for klass in SECURITY_RELEVANT_CLASSES:
            path = first_pattern[klass].replace("**", "x").replace("*", "x").strip("/")
            with self.subTest(klass=klass, path=path):
                self.assertNotEqual(gf.route_for_review((path,)).tier, "A",
                                    f"{klass} ({path}) must never be Tier A")

    def test_a_permission_config_change_never_auto_merges(self) -> None:
        # Even with every named review passed, an owner-stop change is ineligible.
        req = green_merge_request(
            changed_paths=(".claude/settings.json",),
            task_allowed_paths=(".claude/**",),
            completed_reviews={"security": True, "control-plane": True})
        evaluation = gf.evaluate_merge(req)
        self.assertFalse(evaluation.eligible)
        self.assertIn("owner_stop_required", evaluation.refusal_codes())

    def test_a_deploy_definition_merges_only_after_the_catch_all_review(self) -> None:
        # Fail TOWARD review (not owner-stop): eligible once the catch-all
        # security + control-plane reviews pass.
        missing = gf.evaluate_merge(green_merge_request(
            changed_paths=("render.yaml",), task_allowed_paths=("render.yaml",),
            completed_reviews={"security": True}))  # control-plane missing
        self.assertFalse(missing.eligible)
        self.assertIn("specialist_review_missing", missing.refusal_codes())
        passed = gf.evaluate_merge(green_merge_request(
            changed_paths=("render.yaml",), task_allowed_paths=("render.yaml",),
            completed_reviews={"security": True, "control-plane": True}))
        self.assertTrue(passed.eligible, passed.refusal_codes())


# ==========================================================================
# C3 (G5 SEC-1) - the extra_specs override channel fails closed
# ==========================================================================


class ExtraSpecsGuardTests(unittest.TestCase):
    def _journal(self) -> DurableJournal:
        tmp = pathlib.Path(tempfile.mkdtemp())
        journal = DurableJournal(tmp / "j.sqlite3").open()
        self.addCleanup(journal.close)
        return journal

    def test_a_colliding_extra_spec_key_is_refused(self) -> None:
        colliding = {"git_push_task_branch": ex.EffectSpec(
            "git_push_task_branch", "shadow override", read_before_write=False,
            destructive=False, compensating_action="none")}
        with self.assertRaises(ex.ExternalEffectError) as ctx:
            ex.ExternalEffectJournal(self._journal(), extra_specs=colliding)
        self.assertEqual(ctx.exception.code, "extra_spec_collision")

    def test_a_destructive_extra_spec_is_refused(self) -> None:
        for spec in (
                ex.EffectSpec("delete_thing", "d", read_before_write=False,
                              destructive=True, compensating_action="none"),
                ex.EffectSpec("wipe_remote", "d", read_before_write=False,
                              destructive=False, compensating_action="none")):
            with self.subTest(effect=spec.effect_type):
                with self.assertRaises(ex.ExternalEffectError) as ctx:
                    ex.ExternalEffectJournal(
                        self._journal(), extra_specs={spec.effect_type: spec})
                self.assertEqual(ctx.exception.code, "destructive_extra_spec")

    def test_the_legitimate_shadow_merge_spec_is_still_admissible(self) -> None:
        j = gf.shadow_effects_journal(self._journal())
        self.assertIn("github_pr_merge", j.extra_specs)

    def test_every_live_journal_construction_site_uses_empty_extra_specs(self) -> None:
        """Source scan: the ONLY ExternalEffectJournal construction that passes
        extra_specs anywhere in the package is github_flow's shadow path."""
        import re

        import tools.agent_supervisor as pkg
        pkg_dir = pathlib.Path(pkg.__file__).resolve().parent
        offenders = []
        for path in pkg_dir.glob("*.py"):
            if path.name == "github_flow.py":
                continue
            text = path.read_text(encoding="utf-8")
            if re.search(r"ExternalEffectJournal\([^)]*extra_specs", text, re.DOTALL):
                offenders.append(path.name)
        self.assertEqual(offenders, [],
                         "only the github_flow shadow path may pass extra_specs")


# ==========================================================================
# C4 (G5 SEC-3) - redaction discipline for findings and condition logging
# ==========================================================================


class SecretRedactionDisciplineTests(unittest.TestCase):
    def test_a_redacted_descriptor_finding_is_accepted(self) -> None:
        req = green_merge_request(
            secret_scan_findings=("aws_key in services/api/app.py",))
        self.assertEqual(req.secret_scan_findings,
                         ("aws_key in services/api/app.py",))

    def test_a_raw_secret_in_findings_is_refused(self) -> None:
        for raw in ("sk-ant-" + "A" * 40, "ghp_" + "B" * 36, "AKIA" + "C" * 16):
            with self.subTest(raw=raw[:8]):
                with self.assertRaises(gf.GitHubFlowError) as ctx:
                    green_merge_request(secret_scan_findings=(raw,))
                self.assertEqual(ctx.exception.code, "raw_secret_in_findings")

    def test_condition_logging_is_routed_through_redaction(self) -> None:
        secret = "sk-ant-" + "Z" * 40
        condition = gf.MergeCondition(
            "secret_scan_clean", False, "secret_finding",
            f"the scan reported {secret}")
        evaluation = gf.MergeEvaluation(
            eligible=False, conditions=(condition,), required_reviews=())
        logged = gf.redacted_condition_log(evaluation)
        self.assertEqual(len(logged), 1)
        self.assertNotIn(secret, logged[0]["detail"])
        self.assertIn("[REDACTED", logged[0]["detail"])
        self.assertEqual(logged[0]["reason_code"], "secret_finding")


# ==========================================================================
# C5 (G5 INFO-1) - audit every FlowResult, including refusals
# ==========================================================================


class AuditFlowResultTests(unittest.TestCase):
    def test_a_performed_result_produces_a_performed_record(self) -> None:
        result = gf.FlowResult(True, "eff_1", "c" * 40, "merged",
                               "ordinary green PR merged")
        record = gf.audit_flow_result(result, task_id="M0-T044", operation="merge")
        self.assertTrue(record["performed"])
        self.assertEqual(record["outcome"], "performed")
        self.assertEqual(record["reason_code"], "merged")
        self.assertEqual(record["action_id"], "eff_1")

    def test_a_refused_result_is_still_audited(self) -> None:
        result = gf.FlowResult(False, "", "", "merge_ineligible",
                               "automatic merge refused: secret_finding")
        record = gf.audit_flow_result(result, task_id="M0-T044", operation="merge")
        self.assertFalse(record["performed"])
        self.assertEqual(record["outcome"], "refused")
        self.assertEqual(record["reason_code"], "merge_ineligible")

    def test_the_helper_emits_to_an_audit_log_when_supplied(self) -> None:
        class RecordingAudit:
            def __init__(self) -> None:
                self.events: list = []

            def append(self, event, *, run_id="", detail=None) -> None:
                self.events.append((event, run_id, detail))

        audit = RecordingAudit()
        gf.audit_flow_result(
            gf.FlowResult(False, "", "", "unauthorized_branch", "denied"),
            task_id="M0-T044", operation="push", audit=audit, run_id="run-x")
        self.assertEqual(len(audit.events), 1)
        self.assertEqual(audit.events[0][0], "github_flow_result")
        self.assertEqual(audit.events[0][1], "run-x")

    def test_the_audit_detail_is_routed_through_redaction(self) -> None:
        secret = "ghp_" + "D" * 36
        record = gf.audit_flow_result(
            gf.FlowResult(False, "", "", "secret_finding",
                          f"the scan reported {secret}"),
            task_id="M0-T044", operation="merge")
        self.assertNotIn(secret, record["detail"])
        self.assertIn("[REDACTED", record["detail"])


# ==========================================================================
# Meta - the ten-item Section 19.4 register
# ==========================================================================


class Section194RegisterTests(unittest.TestCase):
    #: Each S19.4 GitHub-automation proof -> a test-name fragment that covers it.
    SECTION_19_4: dict[str, str] = {
        "ordinary_task_branch_push_auto_passes": "ordinary_task_branch_push_is_allowed",
        "main_push_hard_denies": "direct_main_push_is_hard_denied",
        "force_push_hard_denies": "force_push_is_hard_denied",
        "pr_creation_works": "pr_creation_works_and_is_journaled",
        "ordinary_green_pr_auto_merges": "ordinary_green_pr_auto_merges",
        "secret_finding_blocks": "merge_refuses_on_a_secret_finding",
        "stale_remote_sha_blocks_or_reconciles":
            "merge_refuses_on_a_stale_remote_sha",
        "workflow_dependency_specialist_review_not_owner":
            "no_tier_b_routing_ever_requires_owner_approval",
        "branch_cleanup_is_safe": "flow_deletes_only_the_proven_merged_task_branch",
        "crash_during_push_or_merge_reconciled":
            "crash_mid_merge_leaves_a_pending_effect",
    }

    def test_every_section_19_4_item_has_a_named_test(self) -> None:
        import re

        source = pathlib.Path(__file__).read_text(encoding="utf-8")
        names = set(re.findall(r"def (test_\w+)", source))
        for item, fragment in self.SECTION_19_4.items():
            self.assertTrue(any(fragment in name for name in names),
                            f"no test covers S19.4 item {item!r} "
                            f"(expected a test name containing {fragment!r})")

    def test_the_register_lists_all_ten_items(self) -> None:
        self.assertEqual(len(self.SECTION_19_4), 10)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
