#!/usr/bin/env python3
"""Approval-broker tests (D-007 Section 15 "approval broker" family).

Covers, in order of the directive's own list:

* the exact safe request is approved ONCE
* a changed digest invalidates the approval
* an unknown request queues rather than allows
* an unhandled non-interactive request DENIES rather than hangs
* a background-agent request without broker access denies
* a deferred request resumes only the exact session and call
* "always allow" is never selected and no settings file is ever written
* broad executable rules are rejected
* recursive/wildcard and substitution-concealed deletion are denied
* canonical-path/symlink/junction/space escapes are denied
* a task-allowed edit in the isolated worktree is approved and the SAME edit
  outside `allowed_paths` is denied
* a push to the exact task branch follows mode and grants
* `main` and force pushes are denied

plus the S8.4 Codex-advisory rules and the S13.5 recompute-before-execute
invalidation.

No provider process, no network, no tokens.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import broker as bk  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.test_agent_supervisor_policy import load_owner_grants  # noqa: E402


class BrokerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._repo_tmp = tempfile.TemporaryDirectory()
        self._runtime_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._repo_tmp.cleanup)
        self.addCleanup(self._runtime_tmp.cleanup)
        self.root = pathlib.Path(self._repo_tmp.name).resolve()
        self.runtime = pathlib.Path(self._runtime_tmp.name).resolve()
        (self.root / "tools" / "agent_supervisor").mkdir(parents=True)
        (self.root / "services").mkdir()

        self.journal = DurableJournal(self.runtime / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)
        self.authority = pol.TaskAuthority(
            task_id="M0-T036", stage="phase-2", repo_root=str(self.root),
            worktree=str(self.root), branch="task/M0-T036-supervisor-bridge",
            allowed_paths=("tools/agent_supervisor/**",
                           "tools/test_agent_supervisor_*.py"),
            forbidden_paths=(".github/**", "services/**"),
            documented_test_commands=("python tools/test_agent_supervisor_phase1.py",),
            grants=load_owner_grants(),
            runtime_dir=str(self.runtime),
            status="in_progress", active=True)
        self.broker = self.make_broker()

    def make_broker(self, **kwargs: object) -> bk.ApprovalBroker:
        params = dict(authority=self.authority, mode="shadow", run_id="run-1")
        params.update(kwargs)
        return bk.ApprovalBroker(self.journal, self.audit, **params)  # type: ignore[arg-type]

    def tool_request(self, tool_name: str, tool_input: dict,
                     **kwargs: object) -> tuple[bk.ApprovalRequest, pol.ProposedAction]:
        action = bk.action_from_tool_request(tool_name, tool_input,
                                             stated_reason=str(kwargs.pop("reason", "")))
        request = bk.build_request(
            tool_name=tool_name, tool_input=tool_input, authority=self.authority,
            argv=action.argv, target_paths=action.target_paths,
            head_sha="a" * 40, origin_main_sha="b" * 40, session_id="sess-1",
            **kwargs)  # type: ignore[arg-type]
        return request, action


# --------------------------------------------------------------------------
# Approve once
# --------------------------------------------------------------------------


class ApproveOnceTests(BrokerTestBase):
    def test_an_exact_safe_request_is_approved_once(self) -> None:
        request, action = self.tool_request("Bash", {"command": "git status"})
        outcome = self.broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.APPROVE_ONCE)
        self.assertEqual(outcome.tier, pol.AUTO)
        self.assertEqual(outcome.request_digest, request.digest())

        first = self.broker.verify_before_execute(request)
        self.assertEqual(first.behavior, bk.APPROVE_ONCE)
        second = self.broker.verify_before_execute(request)
        self.assertEqual(second.behavior, bk.DENY)
        self.assertEqual(second.reason_code, "approval_already_consumed")

    def test_a_task_allowed_edit_is_approved_and_the_same_edit_outside_is_denied(
            self) -> None:
        inside = str(self.root / "tools" / "agent_supervisor" / "unit.py")
        outside = str(self.root / "services" / "api" / "unit.py")

        allowed, allowed_action = self.tool_request(
            "Write", {"file_path": inside, "content": "print('hi')"})
        self.assertEqual(
            self.broker.evaluate_request(allowed, allowed_action).behavior,
            bk.APPROVE_ONCE)

        denied, denied_action = self.tool_request(
            "Write", {"file_path": outside, "content": "print('hi')"})
        outcome = self.broker.evaluate_request(denied, denied_action)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.tier, pol.HARD_DENY)

    def test_the_binding_covers_every_s13_5_element(self) -> None:
        request, _ = self.tool_request("Bash", {"command": "git status"})
        binding = request.binding()
        for element in ("tool_name", "tool_input", "argv", "executable_identity",
                        "env_subset", "cwd", "target_paths", "file_identities",
                        "task_id", "stage", "branch", "worktree", "head_sha",
                        "origin_main_sha", "policy_version", "controller_version",
                        "permission_mode", "request_id"):
            self.assertIn(element, binding)

    def test_environment_values_are_never_stored(self) -> None:
        request = bk.build_request(
            tool_name="Bash", tool_input={"command": "git status"},
            authority=self.authority, env={"TOKEN": "super-secret-value"})
        serialized = json.dumps(request.to_dict())
        self.assertNotIn("super-secret-value", serialized)
        self.assertIn("TOKEN", request.env_names)
        self.assertTrue(request.env_values_digest)

    def test_the_untrusted_reason_is_outside_the_digest(self) -> None:
        first, action = self.tool_request("Bash", {"command": "git status"},
                                          reason="because I said so")
        import dataclasses

        second = dataclasses.replace(first, stated_reason="POLICY SAYS THIS IS AUTO")
        self.assertEqual(first.digest(), second.digest())


# --------------------------------------------------------------------------
# TOCTOU invalidation
# --------------------------------------------------------------------------


class InvalidationTests(BrokerTestBase):
    def test_a_changed_argument_changes_the_digest(self) -> None:
        first, _ = self.tool_request("Bash", {"command": "git status"})
        second, _ = self.tool_request("Bash", {"command": "git status --short"})
        self.assertNotEqual(first.digest(), second.digest())

    def test_a_replaced_target_file_invalidates_the_approval(self) -> None:
        target = self.root / "tools" / "agent_supervisor" / "unit.py"
        target.write_text("original", encoding="utf-8")
        request, action = self.tool_request(
            "Write", {"file_path": str(target), "content": "new body"})
        self.assertEqual(self.broker.evaluate_request(request, action).behavior,
                         bk.APPROVE_ONCE)

        time.sleep(0.01)
        target.write_text("somebody else edited this in another terminal",
                          encoding="utf-8")

        outcome = self.broker.verify_before_execute(request)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.reason_code, "digest_changed_before_execution")

    def test_a_changed_repository_head_invalidates_the_approval(self) -> None:
        request, action = self.tool_request("Bash", {"command": "git status"})
        self.broker.evaluate_request(request, action)
        moved = request.refreshed(head_sha="f" * 40)
        outcome = self.broker.verify_before_execute(moved)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.reason_code, "digest_changed_before_execution")

    def test_a_request_with_no_record_is_denied_not_assumed(self) -> None:
        request, _ = self.tool_request("Bash", {"command": "git status"})
        outcome = self.broker.verify_before_execute(request)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.reason_code, "unhandled_request")

    def test_a_revoked_approval_cannot_execute(self) -> None:
        request, action = self.tool_request("Bash", {"command": "git status"})
        self.broker.evaluate_request(request, action)
        self.assertEqual(self.broker.revoke_all(), 1)
        outcome = self.broker.verify_before_execute(request)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.reason_code, "approval_revoked")
        self.assertIs(self.journal.get_state("limited_auto_enabled"), False)


# --------------------------------------------------------------------------
# Queue, defer, never hang
# --------------------------------------------------------------------------


class QueueAndDenyTests(BrokerTestBase):
    def test_an_unknown_request_queues_rather_than_allows(self) -> None:
        request, action = self.tool_request("SomeBrandNewTool", {"whatever": 1})
        outcome = self.broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DEFER_TO_OWNER)
        self.assertNotEqual(outcome.behavior, bk.APPROVE_ONCE)
        self.assertTrue(outcome.ask_id)
        self.assertEqual(len(self.broker.pending()), 1)

    def test_an_unhandled_request_denies_rather_than_hanging(self) -> None:
        request, _ = self.tool_request("Bash", {"command": "git status"})
        outcome = self.broker.handle_unhandled(request)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertEqual(outcome.reason_code, "unhandled_request")

    def test_a_background_agent_request_is_never_approved(self) -> None:
        request, action = self.tool_request("Task", {"prompt": "do something"})
        outcome = self.broker.evaluate_request(request, action)
        self.assertNotEqual(outcome.behavior, bk.APPROVE_ONCE)

    def test_a_deferred_request_preserves_the_exact_call_and_session(self) -> None:
        request, action = self.tool_request("SomeBrandNewTool", {"payload": "x"})
        outcome = self.broker.evaluate_request(request, action)
        record = self.broker.record(request.request_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["session_id"], "sess-1")
        self.assertEqual(record["request"]["tool_input"], {"payload": "x"})
        self.assertEqual(record["request_digest"], outcome.request_digest)
        self.assertEqual([a.ask_id for a in self.journal.open_asks()], [outcome.ask_id])

    def test_the_owner_answer_must_quote_the_exact_digest(self) -> None:
        request, action = self.tool_request("SomeBrandNewTool", {"payload": "x"})
        outcome = self.broker.evaluate_request(request, action)

        wrong = self.broker.approve_once(request.request_id, "0" * 64)
        self.assertEqual(wrong.behavior, bk.DENY)
        self.assertEqual(wrong.reason_code, "digest_mismatch")

        truncated = self.broker.approve_once(request.request_id,
                                             outcome.request_digest[:16])
        self.assertEqual(truncated.behavior, bk.DENY)

        right = self.broker.approve_once(request.request_id, outcome.request_digest)
        self.assertEqual(right.behavior, bk.APPROVE_ONCE)
        self.assertEqual(self.broker.verify_before_execute(request).behavior,
                         bk.APPROVE_ONCE)

    def test_the_owner_can_deny_by_digest(self) -> None:
        request, action = self.tool_request("SomeBrandNewTool", {"payload": "x"})
        outcome = self.broker.evaluate_request(request, action)
        denied = self.broker.deny_request(request.request_id, outcome.request_digest,
                                          reason="not now")
        self.assertEqual(denied.behavior, bk.DENY)
        self.assertEqual(self.broker.pending(), [])

    def test_answering_an_unknown_request_raises(self) -> None:
        with self.assertRaises(bk.BrokerError):
            self.broker.approve_once("req_does_not_exist", "0" * 64)


# --------------------------------------------------------------------------
# Never "always allow"; never write settings
# --------------------------------------------------------------------------


class NeverAlwaysAllowTests(BrokerTestBase):
    SUGGESTIONS = [
        {"type": "setMode", "mode": "acceptEdits", "destination": "session"},
        {"type": "addRules", "rules": [{"toolName": "Write", "behavior": "allow"}]},
    ]

    def test_permission_suggestions_are_recorded_as_refused(self) -> None:
        request, action = self.tool_request(
            "Write",
            {"file_path": str(self.root / "tools" / "agent_supervisor" / "x.py"),
             "content": "y"},
            permission_suggestions=self.SUGGESTIONS)
        outcome = self.broker.evaluate_request(request, action)
        self.assertIn("setMode:acceptEdits", outcome.rejected_suggestions)
        self.assertIn("addRules", outcome.rejected_suggestions)

    def test_no_settings_file_is_ever_written(self) -> None:
        request, action = self.tool_request(
            "Write",
            {"file_path": str(self.root / "tools" / "agent_supervisor" / "x.py"),
             "content": "y"},
            permission_suggestions=self.SUGGESTIONS)
        self.broker.evaluate_request(request, action)
        for base in (self.root, self.runtime):
            for path in base.rglob("*"):
                self.assertNotIn("settings", path.name.lower(), f"{path} was written")

    def test_the_broker_has_no_settings_write_path_at_all(self) -> None:
        # Structural, not textual: the module must contain no filesystem WRITE
        # call of any kind. (The docstring names `acceptEdits` on purpose - that
        # is documentation of what is refused, not a code path.)
        source = (REPO / "tools" / "agent_supervisor" / "broker.py").read_text(
            encoding="utf-8")
        for forbidden in ("write_text(", "write_bytes(", "open(", "os.replace(",
                          "shutil.", "mkdir(", "settings.json"):
            self.assertNotIn(forbidden, source)

    def test_every_forbidden_suggestion_type_is_named(self) -> None:
        for suggestion_type in bk.FORBIDDEN_SUGGESTION_TYPES:
            self.assertIsInstance(suggestion_type, str)
        self.assertIn("setMode", bk.FORBIDDEN_SUGGESTION_TYPES)
        self.assertIn("alwaysAllow", bk.FORBIDDEN_SUGGESTION_TYPES)


# --------------------------------------------------------------------------
# Denials that must survive a hostile request
# --------------------------------------------------------------------------


class DenialTests(BrokerTestBase):
    def test_recursive_and_concealed_deletion_are_denied(self) -> None:
        for command in ("rm -rf /", "rm -rf $(cat target.txt)", "del /s *.*",
                        "git clean -fdx"):
            with self.subTest(command=command):
                request, action = self.tool_request("Bash", {"command": command})
                outcome = self.broker.evaluate_request(request, action)
                self.assertEqual(outcome.behavior, bk.DENY)
                self.assertEqual(outcome.tier, pol.HARD_DENY)

    def test_path_escapes_are_denied(self) -> None:
        for target in ("../../escape.txt", "%APPDATA%\\x.txt", "$HOME/x.txt"):
            with self.subTest(target=target):
                request, action = self.tool_request(
                    "Write", {"file_path": target, "content": "x"})
                outcome = self.broker.evaluate_request(request, action)
                self.assertNotEqual(outcome.behavior, bk.APPROVE_ONCE)

    def test_a_path_with_spaces_is_ordinary_and_approved(self) -> None:
        target = self.root / "tools" / "agent_supervisor" / "a file with spaces.py"
        request, action = self.tool_request(
            "Write", {"file_path": str(target), "content": "x"})
        self.assertEqual(self.broker.evaluate_request(request, action).behavior,
                         bk.APPROVE_ONCE)

    def test_main_and_force_pushes_are_denied(self) -> None:
        for command in ("git push origin main", "git push --force origin task/x",
                        "git push -f origin task/M0-T036-supervisor-bridge"):
            with self.subTest(command=command):
                request, action = self.tool_request("Bash", {"command": command})
                outcome = self.broker.evaluate_request(request, action)
                self.assertEqual(outcome.behavior, bk.DENY)
                self.assertEqual(outcome.tier, pol.HARD_DENY)

    def test_a_push_to_the_exact_task_branch_follows_mode_and_grants(self) -> None:
        action = pol.ProposedAction(kind="push",
                                    branch="task/M0-T036-supervisor-bridge")
        request = bk.build_request(tool_name="ControllerPush", tool_input={},
                                   authority=self.authority)

        shadow = self.broker.evaluate_request(request, action, review_passed=True)
        self.assertEqual(shadow.behavior, bk.DEFER_TO_OWNER)

        limited = self.make_broker(mode="limited-auto")
        granted = limited.evaluate_request(request, action, review_passed=True)
        self.assertEqual(granted.behavior, bk.APPROVE_ONCE)
        self.assertEqual(granted.matched_grant, "M0-T036-grant-b-push")

    def test_a_bypass_flag_request_halts(self) -> None:
        request, action = self.tool_request(
            "Bash", {"command": f"claude {pol.BYPASS_FLAG_MARKERS[0]} -p go"})
        outcome = self.broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DENY)
        self.assertTrue(outcome.synchronous_stop)
        self.assertEqual(outcome.outcome, pol.DENY_AND_HALT)

    def test_repeated_hard_denies_feed_the_circuit_breaker(self) -> None:
        from tools.agent_supervisor.circuit_breakers import CircuitBreakers
        from tools.agent_supervisor.config import Limits

        breakers = CircuitBreakers(Limits())
        broker = self.make_broker(breakers=breakers)
        for index in range(Limits().max_consecutive_hard_denies):
            request, action = self.tool_request(
                "Bash", {"command": f"git push origin main # {index}"})
            broker.evaluate_request(request, action)
        self.assertTrue(any(v.tripped for v in breakers.tripped()))


# --------------------------------------------------------------------------
# Codex advisory (S8.4 step 3)
# --------------------------------------------------------------------------


class AdvisoryTests(BrokerTestBase):
    def setUp(self) -> None:
        super().setUp()
        self.calls: list[tuple[str, str]] = []

    def advisory(self, recommendation: str, category: str | None = None):
        def callback(request: bk.ApprovalRequest, marked: str
                     ) -> bk.AdvisoryRecommendation:
            self.calls.append((request.tool_name, marked))
            return bk.AdvisoryRecommendation(
                recommendation=recommendation, category=category or marked,
                model_used="fake-advisory-model", reason="advisory reason")
        return callback

    def test_an_advisory_may_approve_inside_its_marked_category(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.APPROVE_ONCE))
        request, action = self.tool_request("Bash", {"command": "ls -la"})
        outcome = broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.APPROVE_ONCE)
        self.assertEqual(outcome.advisory_used, "fake-advisory-model")
        self.assertEqual(self.calls, [("Bash", "documented_test_command")])

    def test_an_advisory_approval_outside_its_category_is_void(self) -> None:
        broker = self.make_broker(
            advisory=self.advisory(bk.APPROVE_ONCE, category="anything_i_like"))
        request, action = self.tool_request("Bash", {"command": "ls -la"})
        outcome = broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DEFER_TO_OWNER)

    def test_an_advisory_may_deny(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.DENY))
        request, action = self.tool_request("Bash", {"command": "ls -la"})
        self.assertEqual(broker.evaluate_request(request, action).behavior, bk.DENY)

    def test_an_advisory_may_route_to_ask(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.ROUTE_TO_ASK))
        request, action = self.tool_request("Bash", {"command": "ls -la"})
        self.assertEqual(broker.evaluate_request(request, action).behavior,
                         bk.DEFER_TO_OWNER)

    def test_security_sensitive_requests_are_never_advisory_eligible(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.APPROVE_ONCE))
        authority = pol.TaskAuthority(
            task_id="M0-T036", stage="s", repo_root=str(self.root),
            worktree=str(self.root), branch="task/x", allowed_paths=("**",))
        broker.authority = authority
        request, action = self.tool_request(
            "Write", {"file_path": str(self.root / "package-lock.json"),
                      "content": "{}"})
        outcome = broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DEFER_TO_OWNER)
        self.assertEqual(self.calls, [])

    def test_external_writes_are_never_advisory_eligible(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.APPROVE_ONCE))
        action = pol.ProposedAction(kind="external_write", effect_type="send_email")
        request = bk.build_request(tool_name="ExternalWrite", tool_input={},
                                   authority=self.authority)
        outcome = broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DEFER_TO_OWNER)
        self.assertEqual(self.calls, [])

    def test_a_hard_deny_never_reaches_the_advisory(self) -> None:
        broker = self.make_broker(advisory=self.advisory(bk.APPROVE_ONCE))
        request, action = self.tool_request("Bash", {"command": "git push origin main"})
        self.assertEqual(broker.evaluate_request(request, action).behavior, bk.DENY)
        self.assertEqual(self.calls, [])

    def test_an_advisory_failure_falls_through_to_ask(self) -> None:
        def explode(request: bk.ApprovalRequest, category: str
                    ) -> bk.AdvisoryRecommendation:
            raise RuntimeError("codex unavailable")

        broker = self.make_broker(advisory=explode)
        request, action = self.tool_request("Bash", {"command": "ls -la"})
        self.assertEqual(broker.evaluate_request(request, action).behavior,
                         bk.DEFER_TO_OWNER)


# --------------------------------------------------------------------------
# Audit trail
# --------------------------------------------------------------------------


class BrokerAuditTests(BrokerTestBase):
    def test_every_outcome_is_audited_and_the_chain_stays_valid(self) -> None:
        cases = [
            ("Bash", {"command": "git status"}),
            ("Bash", {"command": "git push origin main"}),
            ("SomeBrandNewTool", {"x": 1}),
        ]
        for tool, payload in cases:
            request, action = self.tool_request(tool, payload)
            self.broker.evaluate_request(request, action)
        verification = self.audit.verify_chain()
        self.assertTrue(verification.ok, verification.message)
        self.assertGreaterEqual(verification.records_checked, 3)

    def test_the_audit_records_no_raw_secret(self) -> None:
        request = bk.build_request(
            tool_name="Bash", tool_input={"command": "echo sk-ant-SEEDEDFAKEKEY123456"},
            authority=self.authority)
        action = bk.action_from_tool_request(
            "Bash", {"command": "echo sk-ant-SEEDEDFAKEKEY123456"})
        self.broker.evaluate_request(request, action)
        text = (self.runtime / "audit.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("sk-ant-SEEDEDFAKEKEY123456", text)


# --------------------------------------------------------------------------
# Tool translation
# --------------------------------------------------------------------------


class ToolTranslationTests(BrokerTestBase):
    def test_known_tools_map_to_their_kinds(self) -> None:
        cases = {
            "Read": "read", "Write": "file_write", "Edit": "file_write",
            "Bash": "command", "Task": "subagent", "WebFetch": "network",
        }
        for tool, kind in cases.items():
            with self.subTest(tool=tool):
                action = bk.action_from_tool_request(tool, {})
                self.assertEqual(action.kind, kind)

    def test_an_unknown_tool_maps_to_unknown(self) -> None:
        self.assertEqual(bk.action_from_tool_request("Whatever", {}).kind, "unknown")

    def test_change_size_is_measured_from_the_input(self) -> None:
        action = bk.action_from_tool_request(
            "Write", {"file_path": "a.py", "content": "x" * 100})
        self.assertEqual(action.change_bytes, 100)
        multi = bk.action_from_tool_request(
            "MultiEdit", {"file_path": "a.py",
                          "edits": [{"new_string": "y" * 10}, {"new_string": "z" * 5}]})
        self.assertEqual(multi.change_bytes, 15)

    def test_the_command_string_is_carried_but_never_reassembled(self) -> None:
        action = bk.action_from_tool_request("Bash", {"command": "git status | tee x"})
        self.assertEqual(action.command_text, "git status | tee x")
        self.assertEqual(action.argv, ())
        shape = action.command_shape()
        self.assertTrue(shape.has_metacharacter)


# --------------------------------------------------------------------------
# The operator surface (S12.1)
# --------------------------------------------------------------------------


class OperatorCommandTests(unittest.TestCase):
    """`pending-approvals`, `approve-once`, `deny`, `revoke-all`, `verify-controller`."""

    def setUp(self) -> None:
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for

        self._repo_tmp = tempfile.TemporaryDirectory()
        self._base_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._repo_tmp.cleanup)
        self.addCleanup(self._base_tmp.cleanup)
        self.checkout = pathlib.Path(self._repo_tmp.name).resolve()
        (self.checkout / "tools" / "agent_supervisor").mkdir(parents=True)
        self.base = self._base_tmp.name
        self.runtime = runtime_dir_for(self.checkout, base=self.base)
        self.runtime.mkdir(parents=True, exist_ok=True)

        journal = DurableJournal(self.runtime / DB_FILENAME).open()
        audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)
        authority = pol.TaskAuthority(
            task_id="M0-T036", stage="phase-2", repo_root=str(self.checkout),
            worktree=str(self.checkout), branch="task/M0-T036-supervisor-bridge",
            allowed_paths=("tools/agent_supervisor/**",), status="in_progress")
        broker = bk.ApprovalBroker(journal, audit, authority=authority, mode="shadow")
        request, action = (
            bk.build_request(tool_name="MysteryTool", tool_input={"x": 1},
                             authority=authority, session_id="sess-cli"),
            bk.action_from_tool_request("MysteryTool", {"x": 1}))
        self.outcome = broker.evaluate_request(request, action)
        self.request_id = request.request_id
        journal.close()

    def run_cli(self, *args: str) -> tuple[int, dict]:
        import contextlib
        import io

        from tools.agent_supervisor import cli

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main([*args, "--checkout", str(self.checkout),
                             "--runtime-base", self.base, "--json"])
        text = buffer.getvalue()
        return code, (json.loads(text) if text.strip() else {})

    def test_pending_approvals_shows_the_exact_digest(self) -> None:
        code, payload = self.run_cli("pending-approvals")
        self.assertEqual(code, 0)
        self.assertEqual(payload["count"], 1)
        item = payload["pending"][0]
        self.assertEqual(item["request_id"], self.request_id)
        self.assertEqual(item["digest"], self.outcome.request_digest)
        self.assertEqual(item["session_id"], "sess-cli")

    def test_approve_once_requires_the_exact_digest(self) -> None:
        code, payload = self.run_cli("approve-once", self.request_id, "0" * 64)
        self.assertEqual(payload["behavior"], "DENY")
        self.assertEqual(payload["reason_code"], "digest_mismatch")

        code, payload = self.run_cli("approve-once", self.request_id,
                                     self.outcome.request_digest)
        self.assertEqual(code, 0)
        self.assertEqual(payload["behavior"], "APPROVE_ONCE")

    def test_deny_records_the_owner_answer(self) -> None:
        code, payload = self.run_cli("deny", self.request_id,
                                     self.outcome.request_digest)
        self.assertEqual(code, 0)
        self.assertEqual(payload["behavior"], "DENY")
        _, listing = self.run_cli("pending-approvals")
        self.assertEqual(listing["count"], 0)

    def test_revoke_all_clears_the_queue_and_reasserts_limited_auto_off(self) -> None:
        code, payload = self.run_cli("revoke-all")
        self.assertEqual(code, 0)
        self.assertEqual(payload["revoked"], 1)
        self.assertFalse(payload["limited_auto_enabled"])
        _, listing = self.run_cli("pending-approvals")
        self.assertEqual(listing["count"], 0)

    def test_an_unknown_request_id_fails_cleanly(self) -> None:
        code, _ = self.run_cli("approve-once", "req_nope", "0" * 64)
        self.assertEqual(code, 1)

    def test_verify_controller_reports_the_live_package(self) -> None:
        # M0-T072 (D-017-R043): a bare verify-controller verifies NOTHING and
        # therefore fails closed - the former self-generated `ok: true` was the
        # defect this repair closes.
        code, payload = self.run_cli("verify-controller")
        self.assertEqual(code, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["reason_code"], "missing_manifest")
        self.assertIn("nothing was verified", payload["detail"])

    def test_verify_controller_halts_on_a_tampered_manifest(self) -> None:
        from tools.agent_supervisor import cli
        from tools.agent_supervisor.manifest import generate_manifest, write_manifest

        manifest = generate_manifest(cli.PACKAGE_ROOT)
        first = sorted(manifest["files"])[0]
        manifest["files"][first] = "0" * 64
        manifest_path = pathlib.Path(self._base_tmp.name) / "manifest.json"
        write_manifest(manifest, manifest_path)

        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = cli.main(["verify-controller", "--checkout", str(self.checkout),
                             "--runtime-base", self.base, "--json",
                             "--manifest", str(manifest_path)])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(buffer.getvalue())["ok"])

    def test_limited_auto_still_refuses_by_name(self) -> None:
        from tools.agent_supervisor import cli

        with self.assertRaises(NotImplementedError) as ctx:
            cli.main(["start", "--checkout", str(self.checkout),
                      "--runtime-base", self.base, "--mode", "limited-auto"])
        self.assertIn("limited-auto is disabled", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
