#!/usr/bin/env python3
"""Notifications, remote approvals, retention/restore, anchoring, preflight, CLI.

The remaining Phase 3 Section 15 items:

* **notifications / approvals** (S13.10) - a replayed approval, an expired nonce,
  a wrong digest, and `revoke-all`; notifications are view-only and refuse to
  carry secrets, raw commands, auth links, or private source excerpts; a failed
  notification leaves the item QUEUED
* **retention** (S13.11) - a COMPLETE restore drill, not merely backup creation;
  cleanup deletes only supervisor-owned artifacts of proven identity and age
* **anchoring** (S13.12 / D-007-R533 Option A) - mechanism present, no execution
  surface, publication gated on BOTH controller credentials and an explicit owner
  activation
* **preflight** - the control-response probe reports UNVERIFIED and makes no
  call unless explicitly asked to go live
* **CLI** - every S12.1 command is reachable, `start` never dispatches, and
  `limited-auto` refuses by name

No provider process, no network, no tokens.
"""
from __future__ import annotations

import datetime as _dt
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import anchor as anc  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import notifications as notif  # noqa: E402
from tools.agent_supervisor import preflight  # noqa: E402
from tools.agent_supervisor import remote_approvals as ra  # noqa: E402
from tools.agent_supervisor import retention as ret  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402

UTC = _dt.timezone.utc
NOW = _dt.datetime(2026, 8, 3, 12, 0, tzinfo=UTC)
OWNER = "owner@example"


class RuntimeBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runtime = pathlib.Path(self._tmp.name).resolve()
        self.db = self.runtime / "journal.sqlite3"
        self.journal = DurableJournal(self.db).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)


# --------------------------------------------------------------------------
# Notifications (S13.10)
# --------------------------------------------------------------------------


class NotificationTests(RuntimeBase):
    def build(self, **overrides) -> notif.Notification:
        data = {"run_id": "r", "task_id": "M0-T036", "checkpoint_id": "c-1",
                "reason": "a queued question is waiting", "risk_class": "ask",
                "summary": "one architecture question is queued",
                "where_to_review": "run pending-approvals in the controller terminal"}
        data.update(overrides)
        return notif.build_notification(**data)

    def test_a_view_only_notification_builds(self) -> None:
        notification = self.build()
        self.assertEqual(set(notification.to_dict()), set(notif.NOTIFICATION_FIELDS))

    def test_there_is_no_attachment_slot(self) -> None:
        self.assertNotIn("payload", notif.NOTIFICATION_FIELDS)
        self.assertNotIn("attachment", notif.NOTIFICATION_FIELDS)
        self.assertNotIn("transcript", notif.NOTIFICATION_FIELDS)

    def test_a_raw_command_is_refused(self) -> None:
        with self.assertRaises(notif.NotificationError) as raised:
            self.build(summary="run git push --force origin main to fix it")
        self.assertIn("raw_command", raised.exception.code)

    def test_an_auth_link_is_refused(self) -> None:
        with self.assertRaises(notif.NotificationError) as raised:
            self.build(summary="approve at https://example.com/auth?token=xyz")
        self.assertIn("auth_link", raised.exception.code)

    def test_a_source_excerpt_is_refused(self) -> None:
        with self.assertRaises(notif.NotificationError) as raised:
            self.build(summary="the code says:\n```python\nSECRET=1\n```")
        self.assertIn("source_excerpt", raised.exception.code)

    def test_a_private_user_path_is_refused(self) -> None:
        with self.assertRaises(notif.NotificationError) as raised:
            self.build(summary="see C:\\Users\\someone\\notes.txt")
        self.assertIn("private_path", raised.exception.code)

    def test_a_secret_is_redacted_before_the_leak_check(self) -> None:
        notification = self.build(
            summary="the packet mentioned a key value of sk-abcdefghijklmnopqrstuvwx")
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwx", notification.summary)
        self.assertGreater(notification.redaction_count, 0)

    def test_a_never_send_literal_is_removed(self) -> None:
        notification = self.build(summary="the value was hunter2 exactly",
                                  never_send=["hunter2"])
        self.assertNotIn("hunter2", notification.summary)

    def test_the_summary_is_bounded(self) -> None:
        notification = self.build(summary="x" * 5000)
        self.assertLessEqual(len(notification.summary), notif.MAX_SUMMARY_CHARS)

    def test_a_review_pointer_is_mandatory(self) -> None:
        with self.assertRaises(notif.NotificationError) as raised:
            self.build(where_to_review="   ")
        self.assertEqual(raised.exception.code, "missing_review_pointer")

    def test_an_unknown_risk_class_is_refused(self) -> None:
        with self.assertRaises(notif.NotificationError):
            self.build(risk_class="catastrophic")

    def test_a_successful_delivery_dequeues(self) -> None:
        queue = notif.NotificationQueue(self.journal, audit=self.audit)
        sink = notif.LocalFileSink(self.runtime / "notifications.log")
        result = queue.deliver(self.build(), sink)
        self.assertTrue(result.delivered)
        self.assertFalse(result.still_queued)
        self.assertEqual(queue.queued(), ())

    def test_a_failed_delivery_leaves_the_item_queued(self) -> None:
        class FailingSink(notif.NotificationSink):
            name = "failing"

            def deliver(self, notification):  # noqa: ANN001 - test double
                return False, "the surface was unreachable"

        queue = notif.NotificationQueue(self.journal, audit=self.audit)
        result = queue.deliver(self.build(), FailingSink())
        self.assertFalse(result.delivered)
        self.assertTrue(result.still_queued)
        self.assertEqual(len(queue.queued()), 1)

    def test_a_failed_notification_needing_owner_input_pauses_the_run(self) -> None:
        class FailingSink(notif.NotificationSink):
            name = "failing"

            def deliver(self, notification):  # noqa: ANN001 - test double
                return False, "unreachable"

        queue = notif.NotificationQueue(self.journal, audit=self.audit)
        result = queue.deliver(self.build(requires_owner_input=True), FailingSink(),
                               unit_can_proceed=False)
        self.assertTrue(result.run_must_pause)
        self.assertTrue(result.still_queued)

    def test_a_failed_notification_the_unit_can_survive_does_not_pause(self) -> None:
        class FailingSink(notif.NotificationSink):
            name = "failing"

            def deliver(self, notification):  # noqa: ANN001 - test double
                return False, "unreachable"

        queue = notif.NotificationQueue(self.journal, audit=self.audit)
        result = queue.deliver(self.build(requires_owner_input=True), FailingSink(),
                               unit_can_proceed=True)
        self.assertFalse(result.run_must_pause)
        self.assertTrue(result.still_queued)


# --------------------------------------------------------------------------
# Remote approvals (S13.10)
# --------------------------------------------------------------------------


class RemoteApprovalTests(RuntimeBase):
    def setUp(self) -> None:
        super().setUp()
        self.registry = ra.RemoteApprovalRegistry(self.journal, audit=self.audit,
                                                   owner_identity=OWNER)
        self.digest = "d" * 64

    def issue(self, **overrides) -> ra.ApprovalBinding:
        data = {"request_id": "req-1", "request_digest": self.digest,
                "task_id": "M0-T036", "branch": "task/x", "head_sha": "a" * 40,
                "question": "may the supervisor open a PR?", "now_utc": NOW}
        data.update(overrides)
        return self.registry.issue(**data)

    def answer(self, binding: ra.ApprovalBinding, **overrides) -> ra.RemoteAnswer:
        data = {"binding_id": binding.binding_id, "nonce": binding.nonce,
                "outcome": ra.APPROVE_ONCE, "owner_identity": OWNER,
                "request_digest": binding.request_digest,
                "displayed_binding_digest": binding.digest()}
        data.update(overrides)
        return ra.RemoteAnswer(**data)

    def test_a_binding_carries_every_required_element(self) -> None:
        binding = self.issue()
        for field in ("owner_identity", "request_digest", "nonce", "expires_at_utc",
                      "task_id", "branch", "head_sha"):
            self.assertTrue(getattr(binding, field), f"{field} is empty")

    def test_a_valid_answer_is_accepted_once(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding), now_utc=NOW)
        self.assertTrue(verdict.accepted)
        self.assertEqual(verdict.outcome, ra.APPROVE_ONCE)

    def test_a_replayed_approval_is_refused(self) -> None:
        binding = self.issue()
        self.registry.verify(self.answer(binding), now_utc=NOW)
        replay = self.registry.verify(self.answer(binding), now_utc=NOW)
        self.assertFalse(replay.accepted)
        self.assertEqual(replay.reason_code, "nonce_replayed")

    def test_an_expired_nonce_is_refused(self) -> None:
        binding = self.issue(expiry_seconds=60)
        verdict = self.registry.verify(self.answer(binding),
                                       now_utc=NOW + _dt.timedelta(hours=2))
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.reason_code, "expired_nonce")

    def test_an_expired_binding_is_also_consumed_so_it_cannot_be_retried(self) -> None:
        binding = self.issue(expiry_seconds=60)
        self.registry.verify(self.answer(binding), now_utc=NOW + _dt.timedelta(hours=2))
        second = self.registry.verify(self.answer(binding), now_utc=NOW)
        self.assertFalse(second.accepted)

    def test_a_wrong_request_digest_is_refused(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding, request_digest="e" * 64),
                                       now_utc=NOW)
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.reason_code, "wrong_digest")

    def test_a_wrong_displayed_binding_digest_is_refused(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(
            self.answer(binding, displayed_binding_digest="f" * 64), now_utc=NOW)
        self.assertEqual(verdict.reason_code, "wrong_digest")

    def test_a_wrong_owner_identity_is_refused(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding, owner_identity="someone-else"),
                                       now_utc=NOW)
        self.assertEqual(verdict.reason_code, "wrong_owner")

    def test_a_bare_yes_is_not_an_approval(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding, outcome="yes"), now_utc=NOW)
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.reason_code, "unbound_answer")

    def test_a_moved_head_invalidates_the_approval(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding), now_utc=NOW,
                                       current_head_sha="b" * 40)
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.reason_code, "repository_state_changed")

    def test_a_moved_branch_invalidates_the_approval(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding), now_utc=NOW,
                                       current_branch="main")
        self.assertEqual(verdict.reason_code, "repository_state_changed")

    def test_an_unknown_binding_is_refused(self) -> None:
        verdict = self.registry.verify(
            ra.RemoteAnswer(binding_id="nope", nonce="n", outcome=ra.APPROVE_ONCE,
                            owner_identity=OWNER, request_digest=self.digest),
            now_utc=NOW)
        self.assertEqual(verdict.reason_code, "unknown_binding")

    def test_a_deny_is_accepted_but_does_not_approve(self) -> None:
        binding = self.issue()
        verdict = self.registry.verify(self.answer(binding, outcome=ra.DENY), now_utc=NOW)
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.outcome, ra.DENY)
        self.assertEqual(verdict.reason_code, "answer_accepted")

    def test_an_approval_requires_an_owner_identity_to_issue(self) -> None:
        anonymous = ra.RemoteApprovalRegistry(self.journal, owner_identity="")
        with self.assertRaises(ra.RemoteApprovalError) as raised:
            anonymous.issue(request_id="r", request_digest=self.digest, task_id="t",
                            branch="b", head_sha="a" * 40, question="q")
        self.assertEqual(raised.exception.code, "no_owner_identity")

    def test_an_approval_must_expire(self) -> None:
        with self.assertRaises(ra.RemoteApprovalError):
            self.issue(expiry_seconds=0)

    def test_revoke_all_revokes_and_disables_limited_auto(self) -> None:
        self.issue(request_id="req-1")
        self.issue(request_id="req-2")
        record = self.registry.revoke_all(reason="operator revoke-all")
        self.assertEqual(record["revoked_bindings"], 2)
        self.assertFalse(record["limited_auto_enabled"])
        self.assertEqual(self.registry.open_bindings(), ())

    def test_a_revoked_nonce_cannot_be_used_afterwards(self) -> None:
        binding = self.issue()
        self.registry.revoke_all(reason="test")
        verdict = self.registry.verify(self.answer(binding), now_utc=NOW)
        self.assertFalse(verdict.accepted)
        self.assertEqual(verdict.reason_code, "nonce_replayed")

    def test_disable_limited_auto_asserts_the_flag_off(self) -> None:
        self.journal.set_state(ra.LIMITED_AUTO_KEY, True)
        ra.disable_limited_auto(self.journal, reason="test", audit=self.audit)
        self.assertFalse(self.journal.get_state(ra.LIMITED_AUTO_KEY))

    def test_two_bindings_never_share_a_nonce(self) -> None:
        self.assertNotEqual(self.issue(request_id="a").nonce,
                            self.issue(request_id="b").nonce)


# --------------------------------------------------------------------------
# Retention and the restore drill (S13.11)
# --------------------------------------------------------------------------


class RetentionTests(RuntimeBase):
    def setUp(self) -> None:
        super().setUp()
        self.store = ret.RetentionStore(self.runtime, journal=self.journal,
                                        audit=self.audit)

    def sample(self, name: str = "sample.txt", content: bytes = b"payload") -> pathlib.Path:
        path = self.runtime / name
        path.write_bytes(content)
        return path

    def test_a_pre_operation_manifest_records_hashes(self) -> None:
        path = self.sample()
        manifest = ret.PreOperationManifest.capture([path], operation="risky",
                                                    task_id="T", worktree_clean=True)
        self.assertEqual(len(manifest.entries), 1)
        self.assertEqual(len(manifest.entries[0]["sha256"]), 64)

    def test_a_dirty_unexplained_worktree_blocks_the_operation(self) -> None:
        manifest = ret.PreOperationManifest.capture([], operation="risky", task_id="T",
                                                    worktree_clean=False)
        with self.assertRaises(ret.RetentionError) as raised:
            ret.assert_precondition(manifest)
        self.assertEqual(raised.exception.code, "dirty_unexplained_worktree")

    def test_explicitly_recorded_task_changes_satisfy_the_precondition(self) -> None:
        manifest = ret.PreOperationManifest.capture(
            [], operation="risky", task_id="T", worktree_clean=False,
            recorded_task_owned_changes=("tools/agent_supervisor/rotation.py",))
        ret.assert_precondition(manifest)

    def test_a_missing_file_is_recorded_not_invented(self) -> None:
        manifest = ret.PreOperationManifest.capture(
            [self.runtime / "absent.txt"], operation="x", task_id="T", worktree_clean=True)
        self.assertFalse(manifest.entries[0]["exists"])
        self.assertEqual(manifest.entries[0]["sha256"], "")

    def test_quarantine_verifies_the_copy(self) -> None:
        item = self.store.quarantine(self.sample(), operation="test")
        self.assertTrue(pathlib.Path(item.quarantine_path).is_file())
        self.assertEqual(ret.file_sha256(item.quarantine_path), item.sha256)

    def test_quarantine_never_moves_the_source(self) -> None:
        path = self.sample()
        self.store.quarantine(path, operation="test")
        self.assertTrue(path.exists(), "quarantine copies, it never moves")

    def test_deleting_a_source_before_verification_is_refused(self) -> None:
        item = self.store.quarantine(self.sample(), operation="test")
        pathlib.Path(item.quarantine_path).unlink()
        verdict = self.store.restore(item)
        self.assertFalse(verdict.verified)
        with self.assertRaises(ret.RetentionError) as raised:
            self.store.safe_to_delete_source(verdict)
        self.assertEqual(raised.exception.code, "recovery_not_verified")

    def test_a_complete_restore_drill_passes(self) -> None:
        result = ret.run_restore_drill(self.store, journal_db_path=self.db,
                                       sample_path=self.sample("drill.txt", b"important"))
        self.assertTrue(result.passed, result.detail)
        self.assertIn("destroyed the source to make the drill real", result.steps)
        self.assertTrue(any("integrity check" in step for step in result.steps))

    def test_cleanup_refuses_a_path_outside_the_runtime_directory(self) -> None:
        outside = pathlib.Path(tempfile.gettempdir()) / "not_ours.txt"
        with self.assertRaises(ret.RetentionError) as raised:
            self.store.register(outside, artifact_class=ret.QUARANTINE)
        self.assertEqual(raised.exception.code, "outside_runtime_dir")

    def test_cleanup_refuses_an_artifact_outside_its_class_directory(self) -> None:
        stray = self.runtime / "stray.txt"
        stray.write_bytes(b"x")
        self.store.register(stray, artifact_class=ret.CHECKPOINTS)
        plan = self.store.plan_cleanup(now_utc=NOW)
        self.assertTrue(any("class membership is not proven" in item["reason"]
                            for item in plan["refused"]))
        self.assertEqual(plan["delete"], [])

    def test_an_over_age_artifact_is_proposed_for_deletion(self) -> None:
        path = self.store.class_dir(ret.EVENT_STREAMS) / "old.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        entry = self.store.register(path, artifact_class=ret.EVENT_STREAMS)
        entry["created_at_utc"] = "2020-01-01T00:00:00.000Z"
        self.store._write_inventory([entry])  # noqa: SLF001 - fixture setup
        plan = self.store.plan_cleanup(now_utc=NOW)
        self.assertEqual(len(plan["delete"]), 1)
        self.assertTrue(any("age" in reason for reason in plan["delete"][0]["reasons"]))

    def test_a_fresh_artifact_is_kept(self) -> None:
        path = self.store.class_dir(ret.EVENT_STREAMS) / "new.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        self.store.register(path, artifact_class=ret.EVENT_STREAMS)
        plan = self.store.plan_cleanup(now_utc=NOW)
        self.assertEqual(plan["delete"], [])
        self.assertIn(str(path.resolve()), plan["keep"])

    def test_an_unreadable_creation_time_refuses_deletion(self) -> None:
        path = self.store.class_dir(ret.EVENT_STREAMS) / "odd.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
        entry = self.store.register(path, artifact_class=ret.EVENT_STREAMS)
        entry["created_at_utc"] = "not-a-time"
        self.store._write_inventory([entry])  # noqa: SLF001 - fixture setup
        plan = self.store.plan_cleanup(now_utc=NOW)
        self.assertEqual(plan["delete"], [])
        self.assertTrue(any("age is not proven" in item["reason"]
                            for item in plan["refused"]))

    def test_execute_cleanup_only_consumes_a_plan(self) -> None:
        with self.assertRaises(ret.RetentionError) as raised:
            self.store.execute_cleanup({"nothing": True})
        self.assertEqual(raised.exception.code, "not_a_plan")

    def test_execute_cleanup_reproves_identity(self) -> None:
        outside = pathlib.Path(tempfile.gettempdir()) / "planted.txt"
        outside.write_bytes(b"x")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        forged = {"delete": [{"path": str(outside), "artifact_class": ret.QUARANTINE}]}
        record = self.store.execute_cleanup(forged)
        self.assertEqual(record["deleted"], [])
        self.assertTrue(outside.exists(), "a forged plan entry must not delete anything")

    def test_every_artifact_class_has_limits(self) -> None:
        policy = ret.RetentionPolicy()
        for artifact_class in ret.ARTIFACT_CLASSES:
            limits = policy.for_class(artifact_class)
            self.assertGreater(limits.max_items, 0)
            self.assertGreater(limits.max_age_days, 0)

    def test_an_unknown_artifact_class_is_refused(self) -> None:
        with self.assertRaises(ret.RetentionError):
            ret.RetentionPolicy().for_class("mystery")


# --------------------------------------------------------------------------
# Option A anchoring (S13.12, D-007-R533)
# --------------------------------------------------------------------------


class AnchorTests(RuntimeBase):
    def anchor(self) -> anc.AnchorRecord:
        self.audit.append("probe_event", run_id="r")
        return anc.build_anchor(audit_log=self.audit, checkout_key="k" * 64, run_id="r",
                                task_id="M0-T036", checkpoint_id="c-1")

    def test_the_module_has_no_execution_surface(self) -> None:
        anc.assert_no_execution()
        source = (REPO / "tools" / "agent_supervisor" / "anchor.py").read_text(
            encoding="utf-8")
        # Look for EXECUTION SYNTAX, not for bare mentions: the names themselves
        # legitimately appear once, in EXECUTION_SURFACE_NAMES, which is the deny
        # list the assertion above is built from (the AS-7 constants exception).
        for forbidden in ("import subprocess", "import os\n", "subprocess.run(",
                          ".Popen(", "os.system(", "os.popen("):
            self.assertNotIn(forbidden, source)
        self.assertEqual(source.count("Popen"), 1,
                         "'Popen' may appear only in the deny-list constant")

    def test_an_anchor_captures_the_chain_head(self) -> None:
        anchor = self.anchor()
        self.assertEqual(anchor.chain_head_digest, self.audit.head_digest)
        self.assertEqual(anchor.sequence, self.audit.head_sequence)

    def test_the_anchor_content_is_deterministic(self) -> None:
        anchor = self.anchor()
        self.assertEqual(anchor.content_bytes(), anchor.content_bytes())
        self.assertTrue(anchor.content_bytes().endswith(b"\n"))

    def test_the_publish_plan_targets_the_dedicated_branch(self) -> None:
        plan = anc.build_publish_plan(self.anchor())
        self.assertEqual(plan.branch, anc.ANCHOR_BRANCH)
        self.assertTrue(any("push" in argv for argv in plan.argv))

    def test_main_is_never_an_anchor_target(self) -> None:
        for branch in ("main", "master", "HEAD"):
            with self.subTest(branch=branch):
                with self.assertRaises(anc.AnchorError) as raised:
                    anc.build_publish_plan(self.anchor(), branch=branch)
                self.assertEqual(raised.exception.code, "forbidden_anchor_branch")

    def test_an_unsafe_remote_is_refused(self) -> None:
        with self.assertRaises(anc.AnchorError):
            anc.build_publish_plan(self.anchor(), remote="origin; rm -rf /")

    def test_anchoring_is_not_active_without_credentials(self) -> None:
        self.journal.set_state(anc.ACTIVATION_KEY,
                               {"owner_activated": True, "directive_reference": "D-007-R533"})
        status = anc.activation_status(self.journal, credentials_present=False)
        self.assertFalse(status.active)
        self.assertIn("credentials", status.reason)

    def test_anchoring_is_not_active_without_owner_activation(self) -> None:
        status = anc.activation_status(self.journal, credentials_present=True)
        self.assertFalse(status.active)
        self.assertIn("explicit activation", status.reason)

    def test_both_conditions_activate(self) -> None:
        self.journal.set_state(anc.ACTIVATION_KEY,
                               {"owner_activated": True, "directive_reference": "D-007-R533"})
        status = anc.activation_status(self.journal, credentials_present=True)
        self.assertTrue(status.active)
        anc.assert_activated(status)

    def test_assert_activated_refuses_when_inactive(self) -> None:
        with self.assertRaises(anc.AnchorError) as raised:
            anc.assert_activated(anc.activation_status(self.journal))
        self.assertEqual(raised.exception.code, "anchoring_not_activated")

    def test_the_checkpoint_entry_point_records_but_never_publishes(self) -> None:
        record = anc.anchor_at_checkpoint(
            journal=self.journal, audit_log=self.audit, checkout_key="k" * 64,
            run_id="r", task_id="t", checkpoint_id="c")
        self.assertFalse(record["published"])
        self.assertFalse(record["activation"]["active"])
        self.assertIsNotNone(anc.last_anchor(self.journal))

    def test_an_anchor_detects_a_truncated_chain(self) -> None:
        anchor = self.anchor()
        stored = anchor.to_dict()

        class ShorterLog:
            head_sequence = anchor.sequence - 1
            head_digest = "0" * 64

        ok, detail = anc.verify_anchor_against_chain(stored, ShorterLog())
        self.assertFalse(ok)
        self.assertIn("truncated or rolled back", detail)

    def test_an_anchor_detects_a_rewritten_head(self) -> None:
        anchor = self.anchor()
        stored = anchor.to_dict()

        class RewrittenLog:
            head_sequence = anchor.sequence
            head_digest = "9" * 64

        ok, detail = anc.verify_anchor_against_chain(stored, RewrittenLog())
        self.assertFalse(ok)
        self.assertIn("rewritten", detail)

    def test_a_growing_chain_stays_consistent_with_an_old_anchor(self) -> None:
        anchor = self.anchor()
        self.audit.append("later_event", run_id="r")
        ok, _ = anc.verify_anchor_against_chain(anchor.to_dict(), self.audit)
        self.assertTrue(ok)

    def test_a_broken_chain_is_never_anchored(self) -> None:
        (self.runtime / "audit.jsonl").write_text("{not json\n", encoding="utf-8")
        broken = AuditLog(self.runtime / "audit.jsonl", fsync=False)
        with self.assertRaises(anc.AnchorError) as raised:
            anc.build_anchor(audit_log=broken, checkout_key="k", run_id="r", task_id="t",
                             checkpoint_id="c")
        self.assertEqual(raised.exception.code, "chain_not_verifiable")

    def test_the_history_note_states_what_is_proven_today(self) -> None:
        note = anc.anchor_history_note([{"a": 1}])
        self.assertIn("0 published", note)
        self.assertIn("ON THIS MACHINE", note)


# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------


class PreflightTests(RuntimeBase):
    def test_the_default_probe_makes_no_call(self) -> None:
        result = preflight.control_response_round_trip("any-executable", live=False)
        self.assertEqual(result.status, preflight.UNVERIFIED)
        self.assertFalse(result.ran_live)
        self.assertIn("no live call was made", result.detail)

    def test_the_probe_argv_is_built_by_the_shipped_adapter(self) -> None:
        argv = preflight._probe_argv("claude", str(self.runtime))  # noqa: SLF001
        for flag in ("--permission-mode", "manual", "--permission-prompt-tool", "stdio",
                     "--max-turns", "1"):
            self.assertIn(flag, argv)

    def test_a_live_probe_with_no_executable_fails_rather_than_guessing(self) -> None:
        result = preflight.control_response_round_trip("", live=True)
        self.assertEqual(result.status, preflight.FAILED)
        self.assertFalse(result.ran_live)

    def test_probe_records_persist(self) -> None:
        result = preflight.control_response_round_trip("x", live=False)
        preflight.record_probe(self.journal, result, executable_identity="sha256:abc")
        stored = preflight.probe_record(self.journal, "control_response_round_trip")
        self.assertEqual(stored["status"], preflight.UNVERIFIED)
        self.assertEqual(stored["executable_identity"], "sha256:abc")

    def test_resolution_never_searches_the_path(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" / "preflight.py").read_text(
            encoding="utf-8")
        self.assertNotIn("shutil.which", source,
                         "S13.4 forbids following a discovered executable path")
        self.assertEqual(preflight.resolve_canonical_claude(["/definitely/not/here"]), "")


# --------------------------------------------------------------------------
# CLI surface (S12.1)
# --------------------------------------------------------------------------


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = pathlib.Path(self._tmp.name).resolve()
        self.checkout = self.base / "checkout"
        self.checkout.mkdir()
        self.runtime_base = self.base / "runtime"

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        common = ["--checkout", str(self.checkout),
                  "--runtime-base", str(self.runtime_base)]
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = cli.main([*argv, *common])
        except SystemExit as exc:  # pragma: no cover - argparse failures
            code = int(exc.code or 0)
        return code, out.getvalue(), err.getvalue()

    def test_every_s12_1_command_is_registered(self) -> None:
        parser = cli.build_parser()
        registered = set()
        for action in parser._subparsers._group_actions:  # noqa: SLF001
            registered |= set(action.choices)
        expected = {
            "doctor", "replay", "start", "status", "pause", "resume", "stop",
            "emergency-stop", "verify-controller", "recovery-status", "schedule-status",
            "cancel-scheduled-resume", "autostart-plan", "install-autostart",
            "uninstall-autostart", "pending-approvals", "approve-once", "deny",
            "revoke-all", "set-codex-model", "set-claude-model", "export-handoff",
        }
        self.assertEqual(expected - registered, set())

    def test_only_replay_remains_deferred(self) -> None:
        self.assertEqual(set(cli.DEFERRED_COMMANDS), {"replay"})

    def test_limited_auto_refuses_by_name(self) -> None:
        with self.assertRaises(NotImplementedError) as raised:
            self.run_cli("start", "--mode", "limited-auto")
        self.assertIn("limited-auto is disabled", str(raised.exception))
        self.assertIn("explicit owner activation", str(raised.exception))

    def test_start_never_dispatches(self) -> None:
        code, out, _ = self.run_cli("start", "--mode", "shadow", "--json")
        payload = json.loads(out)
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["provider_calls_made"], 0)
        self.assertFalse(payload["limited_auto_enabled"])
        self.assertEqual(code, 0)

    def test_start_releases_the_lock_it_took(self) -> None:
        self.run_cli("start", "--mode", "shadow", "--json")
        code, _, _ = self.run_cli("start", "--mode", "supervised", "--json")
        self.assertEqual(code, 0, "a second start must not find a leaked lock")

    def test_pause_then_recovery_status_reports_the_flag(self) -> None:
        self.run_cli("pause")
        code, out, _ = self.run_cli("recovery-status", "--json")
        payload = json.loads(out)
        self.assertTrue(payload["flags"]["manual_pause"])
        self.assertFalse(payload["autostart_permitted"])
        self.assertEqual(code, 0)

    def test_resume_refuses_while_an_emergency_stop_stands(self) -> None:
        self.run_cli("emergency-stop")
        code, _, err = self.run_cli("resume")
        self.assertEqual(code, 1)
        self.assertIn("emergency stop", err)

    def test_stop_clear_is_an_explicit_owner_command(self) -> None:
        self.run_cli("emergency-stop")
        code, _, _ = self.run_cli("stop", "--clear")
        self.assertEqual(code, 0)
        code, _, _ = self.run_cli("resume")
        self.assertEqual(code, 0)

    def test_emergency_stop_reports_what_it_did(self) -> None:
        code, out, _ = self.run_cli("emergency-stop", "--json")
        payload = json.loads(out)
        self.assertTrue(payload["emergency_stop"])
        self.assertIn("children", payload)
        self.assertEqual(code, 0)

    def test_schedule_status_with_no_wait(self) -> None:
        code, out, _ = self.run_cli("schedule-status", "--json")
        payload = json.loads(out)
        self.assertIsNone(payload["limit_record"])
        self.assertEqual(code, 0)

    def test_cancel_scheduled_resume_with_nothing_scheduled_reports_failure(self) -> None:
        code, _, _ = self.run_cli("cancel-scheduled-resume")
        self.assertEqual(code, 1, "cancelling nothing must not report success")

    def test_autostart_plan_is_read_only(self) -> None:
        code, out, _ = self.run_cli("autostart-plan", "--kind", "boot", "--json")
        payload = json.loads(out)
        self.assertTrue(payload["read_only"])
        self.assertIn("nothing was created", payload["note"])
        self.assertEqual(code, 0)

    def test_install_autostart_without_the_digest_changes_nothing(self) -> None:
        code, _, err = self.run_cli("install-autostart", "--kind", "boot")
        self.assertEqual(code, 1)
        self.assertIn("NOTHING WAS CHANGED", err)

    def test_export_handoff_without_a_verified_handoff_refuses(self) -> None:
        code, _, err = self.run_cli("export-handoff")
        self.assertEqual(code, 1)
        self.assertIn("no verified handoff is stored", err)

    def test_set_codex_model_requires_both_configuration_files(self) -> None:
        code, _, err = self.run_cli("set-codex-model", "some-model")
        self.assertEqual(code, 1)
        self.assertIn("--config", err)

    def test_doctor_passes_and_never_runs_a_live_probe_by_default(self) -> None:
        code, out, _ = self.run_cli("doctor", "--json")
        payload = json.loads(out)
        self.assertTrue(payload["ok"], [c for c in payload["checks"] if not c["ok"]])
        live = [c for c in payload["checks"]
                if c["check"] == "control_response_live_probe"][0]
        self.assertIn("no live call was made", live["detail"])
        self.assertEqual(code, 0)

    def test_doctor_reports_a_recorded_live_probe_without_calling_again(self) -> None:
        """A VERIFIED probe recorded per checkout is reported on later runs.

        Verification is host- and binary-specific, so it lives in the journal
        rather than in a module constant. This exercises that branch with a
        seeded record and makes NO live call.
        """
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for

        self.run_cli("doctor", "--json")  # create the runtime dir and journal
        runtime = runtime_dir_for(self.checkout, base=self.runtime_base)
        verified = preflight.ProbeResult(
            "control_response_round_trip", preflight.VERIFIED,
            "seeded for this test", ran_live=True)
        with DurableJournal(runtime / DB_FILENAME) as journal:
            preflight.record_probe(journal, verified,
                                   executable_identity="sha256_head:abcdef0123456789")
        _, out, _ = self.run_cli("doctor", "--json")
        live = [c for c in json.loads(out)["checks"]
                if c["check"] == "control_response_live_probe"][0]
        self.assertTrue(live["ok"])
        self.assertIn("VERIFIED by a recorded live probe", live["detail"])
        self.assertIn("sha256_head:abcdef0123456789", live["detail"])

    def test_doctor_reports_unverified_without_a_recorded_probe(self) -> None:
        _, out, _ = self.run_cli("doctor", "--json")
        live = [c for c in json.loads(out)["checks"]
                if c["check"] == "control_response_live_probe"][0]
        self.assertIn("no live call was made", live["detail"])

    def test_doctor_reports_the_phase_3_checks(self) -> None:
        _, out, _ = self.run_cli("doctor", "--json")
        names = {c["check"] for c in json.loads(out)["checks"]}
        for expected in ("rotation_invariants", "reset_parser", "fixed_scheduler_action",
                         "recovery_classification", "single_instance_lock",
                         "model_change_ipc", "retention_policy",
                         "audit_anchor_option_a", "notification_hygiene"):
            self.assertIn(expected, names)

    def test_replay_still_refuses(self) -> None:
        with self.assertRaises(NotImplementedError) as raised:
            self.run_cli("replay")
        self.assertIn("Phase 4", str(raised.exception))


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
