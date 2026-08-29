#!/usr/bin/env python3
"""M0-T070 (D-014): packet command authority wiring + revoke/status reconciliation.

Qualifying evidence (supervisor-freeze §2: a reproduced defect + inability to
complete an authorized product task): run_M0_T063_A1 (controller 0.4.0-phase4,
2026-08-18) failed closed because production `_run_loop` built its
`TaskAuthority` without `documented_test_commands` - the S4.1 documented-test
AUTO tier was unreachable, all three worker Bash requests classified
`ASK:undocumented_command`, and the run ended PAUSED_RECOVERY with no
checkpoint. After the owner's revoke-all, `status` still listed the three
revoked requests under `open_asks`, because nothing ever resolved a
`queued_asks` row.

This file proves the repair:

* AS-1  - ONE canonical, closed field (`documented_test_commands`), and the
          schema file + stdlib validator agree on the bounds and character
          profile so neither can drift permissive alone.
* AS-2/AS-7 - packet commands reach the authority THE REAL LOOP uses:
          `production_task_authority` carries them, and a source-level (AST)
          assertion pins `_run_loop` to that constructor, so the original
          defect (a bypassing `TaskAuthority.from_packet` call) cannot
          silently return.
* AS-3  - deterministic fail-closed validation: empty, wrong type, chaining,
          substitution, redirection, metacharacters, malformed - never AUTO,
          and a malformed field refuses the run.
* AS-4/AS-5/AS-10 - the exact M0-T063 fixture: every intended command is
          AUTO `documented_test_command`; every altered/injected variant
          stays ASK or HARD_DENY.
* AS-6  - the closed profile bounds the field; there is no general allowlist
          (asserted structurally: the validator caps entries and the AUTO
          path still requires an exact `_shape_matches` against the packet).
* AS-8/AS-9 - a pending ask is open; revoke-all revokes it durably;
          pending-approvals reports zero; `status` never presents a revoked
          request as actionable - including against a PRE-FIX journal (the
          live A1 shape) that must never be mutated - while the row and the
          audit chain survive as history.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import broker as bk  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
)
from tools.agent_supervisor.models import QueuedAsk, to_utc_iso  # noqa: E402

PACKAGE = REPO / "tools" / "agent_supervisor"
FIXTURE_PATH = PACKAGE / "fixtures" / "m0_t063_documented_test_command.json"
SCHEMA_PATH = PACKAGE / "schemas" / "task_packet_commands.schema.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def fixture_authority(**overrides: object) -> pol.TaskAuthority:
    run = dict(FIXTURE["run"])
    packet = dict(FIXTURE["packet"])
    params = dict(repo_root=run["repo_root"], worktree=run["worktree"],
                  branch=run["branch"], stage=run["stage"])
    params.update(overrides)
    return cli.production_task_authority(packet, **params)  # type: ignore[arg-type]


def classify(command: str, authority: pol.TaskAuthority) -> pol.PolicyDecision:
    action = pol.ProposedAction(kind="command", tool_name="Bash",
                                command_text=command)
    return pol.evaluate(action, authority=authority)


# --------------------------------------------------------------------------
# AS-1: one canonical, closed, schema-validated field
# --------------------------------------------------------------------------


class SchemaValidatorLockstepTests(unittest.TestCase):
    def test_the_schema_file_exists_and_names_the_canonical_key(self) -> None:
        self.assertIn(pol.DOCUMENTED_TEST_COMMANDS_KEY, SCHEMA["description"])
        self.assertEqual(SCHEMA["type"], "array")

    def test_schema_bounds_equal_validator_bounds(self) -> None:
        self.assertEqual(SCHEMA["maxItems"], pol.MAX_DOCUMENTED_TEST_COMMANDS)
        self.assertEqual(SCHEMA["items"]["maxLength"],
                         pol.MAX_DOCUMENTED_TEST_COMMAND_CHARS)
        self.assertEqual(SCHEMA["items"]["minLength"], 1)
        self.assertTrue(SCHEMA["uniqueItems"])

    def test_schema_pattern_equals_validator_profile(self) -> None:
        self.assertEqual(SCHEMA["items"]["pattern"],
                         pol._DOCUMENTED_COMMAND_PROFILE.pattern)

    def test_schema_regex_and_validator_agree_on_canonical_samples(self) -> None:
        pattern = re.compile(SCHEMA["items"]["pattern"])
        accepted = FIXTURE["packet"]["documented_test_commands"]
        rejected = ["", " padded", "a; b", "a && b", "a | b", "a > b", "a < b",
                    "a $(b)", "a `b`", 'a "b"', "a 'b'", "a \\ b", "a\nb",
                    "a\tb", "-flag first", "a # comment", "a ~ b", "a % b",
                    "a ^ b", "a ! b", "a { b }"]
        for sample in accepted:
            self.assertTrue(pattern.match(sample), sample)
            pol.validate_documented_test_commands(
                {pol.DOCUMENTED_TEST_COMMANDS_KEY: [sample]})
        for sample in rejected:
            self.assertFalse(pattern.match(sample), sample)
            with self.assertRaises(pol.PolicyError, msg=sample):
                pol.validate_documented_test_commands(
                    {pol.DOCUMENTED_TEST_COMMANDS_KEY: [sample]})


# --------------------------------------------------------------------------
# AS-3: deterministic, fail-closed validation
# --------------------------------------------------------------------------


class ValidatorFailClosedTests(unittest.TestCase):
    def check_raises(self, value: object) -> None:
        with self.assertRaises(pol.PolicyError):
            pol.validate_documented_test_commands(
                {pol.DOCUMENTED_TEST_COMMANDS_KEY: value})

    def test_an_absent_key_confers_no_authority_and_no_error(self) -> None:
        self.assertEqual(pol.validate_documented_test_commands({}), ())

    def test_an_empty_list_is_legal_and_confers_nothing(self) -> None:
        self.assertEqual(pol.validate_documented_test_commands(
            {pol.DOCUMENTED_TEST_COMMANDS_KEY: []}), ())

    def test_wrong_container_types_fail_closed(self) -> None:
        for value in (None, "python tools/test.py", 7, True,
                      {"cmd": "python tools/test.py"}, b"python"):
            self.check_raises(value)

    def test_wrong_entry_types_fail_closed(self) -> None:
        for entry in (None, 7, True, ["python"], {"c": 1}):
            self.check_raises([entry])

    def test_empty_and_padded_entries_fail_closed(self) -> None:
        for entry in ("", " ", "python tools/test.py ", " python tools/test.py",
                      "python\ttools/test.py"):
            self.check_raises([entry])

    def test_bounds_fail_closed(self) -> None:
        self.check_raises(["x" * (pol.MAX_DOCUMENTED_TEST_COMMAND_CHARS + 1)])
        self.check_raises(
            [f"python tools/t{i}.py"
             for i in range(pol.MAX_DOCUMENTED_TEST_COMMANDS + 1)])
        self.check_raises(["python tools/test.py", "python tools/test.py"])

    def test_shell_semantics_fail_closed(self) -> None:
        for entry in ("python a.py; python b.py", "python a.py && python b.py",
                      "python a.py | sh", "python a.py > out.txt",
                      "python a.py < in.txt", "python $(cat cmd)",
                      "python `cat cmd`", "python a.py & python b.py",
                      "eval python a.py", "python ${HOME}/a.py",
                      'python "a.py"', "python 'a.py'", "python a.py \\",
                      "-m pytest", "python a.py # test"):
            self.check_raises([entry])

    def test_a_valid_field_round_trips_in_order(self) -> None:
        cmds = FIXTURE["packet"]["documented_test_commands"]
        self.assertEqual(
            pol.validate_documented_test_commands(
                {pol.DOCUMENTED_TEST_COMMANDS_KEY: list(cmds)}),
            tuple(cmds))


# --------------------------------------------------------------------------
# AS-2 / AS-7: packet commands reach the authority the REAL loop uses
# --------------------------------------------------------------------------


class ProductionWiringTests(unittest.TestCase):
    def test_production_authority_carries_the_packet_commands(self) -> None:
        authority = fixture_authority()
        self.assertEqual(
            authority.documented_test_commands,
            tuple(FIXTURE["packet"]["documented_test_commands"]))

    def test_a_malformed_field_refuses_the_run_instead_of_dropping(self) -> None:
        packet = dict(FIXTURE["packet"])
        packet[pol.DOCUMENTED_TEST_COMMANDS_KEY] = ["python a.py; rm -rf ."]
        run = FIXTURE["run"]
        with self.assertRaises(pol.PolicyError):
            cli.production_task_authority(
                packet, repo_root=run["repo_root"], worktree=run["worktree"],
                branch=run["branch"], stage=run["stage"])

    @staticmethod
    def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        raise AssertionError(f"{name} not found in cli.py")

    def test_run_loop_builds_authority_only_through_the_production_path(
            self) -> None:
        """Source-level wiring pin (the loop.py owner-touch precedent).

        The original defect was a direct `TaskAuthority.from_packet(...)` call
        in `_run_loop` that omitted `documented_test_commands`. This assertion
        makes that exact regression a test failure: `_run_loop` must call
        `production_task_authority` and must not construct a TaskAuthority any
        other way.
        """
        tree = ast.parse((PACKAGE / "cli.py").read_text(encoding="utf-8"))
        run_loop = self._function(tree, "_run_loop")
        calls = [node for node in ast.walk(run_loop) if isinstance(node, ast.Call)]
        named = []
        for call in calls:
            func = call.func
            if isinstance(func, ast.Name):
                named.append(func.id)
            elif isinstance(func, ast.Attribute):
                named.append(func.attr)
        self.assertIn("production_task_authority", named)
        self.assertNotIn("from_packet", named)
        self.assertNotIn("TaskAuthority", named)

    def test_the_production_path_loads_commands_through_the_validator(
            self) -> None:
        tree = ast.parse((PACKAGE / "cli.py").read_text(encoding="utf-8"))
        producer = self._function(tree, "production_task_authority")
        for node in ast.walk(producer):
            if not isinstance(node, ast.keyword):
                continue
            if node.arg != "documented_test_commands":
                continue
            value = node.value
            self.assertIsInstance(value, ast.Call)
            func = value.func  # type: ignore[union-attr]
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            self.assertEqual(name, "validate_documented_test_commands")
            return
        raise AssertionError(
            "production_task_authority does not pass documented_test_commands")

    def test_the_intended_command_evaluates_auto_through_that_authority(
            self) -> None:
        authority = fixture_authority()
        decision = classify(FIXTURE["intended_auto"][0], authority)
        self.assertEqual(decision.tier, pol.AUTO)
        self.assertEqual(decision.reason_code, "documented_test_command")


# --------------------------------------------------------------------------
# AS-4 / AS-5 / AS-10: the exact M0-T063 fixture, intended vs adversarial
# --------------------------------------------------------------------------


class M0T063FixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authority = fixture_authority()

    def test_every_intended_command_is_auto_documented_test(self) -> None:
        for command in FIXTURE["intended_auto"]:
            decision = classify(command, self.authority)
            self.assertEqual(decision.tier, pol.AUTO, command)
            self.assertEqual(decision.reason_code, "documented_test_command",
                             command)
            self.assertTrue(decision.advisory_eligible, command)

    def test_every_altered_or_injected_variant_is_never_auto(self) -> None:
        for variant in FIXTURE["must_not_auto"]:
            decision = classify(variant["command"], self.authority)
            self.assertIn(decision.tier, (pol.ASK, pol.HARD_DENY),
                          f"{variant['command']} ({variant['why']}) -> "
                          f"{decision.tier}:{decision.reason_code}")

    def test_the_pre_fix_construction_reproduces_the_a1_failure(self) -> None:
        """BEFORE evidence, kept executable: the construction _run_loop used
        before this repair (no documented_test_commands) classifies the exact
        intended command ASK:undocumented_command - the recorded A1 outcome.
        """
        run = FIXTURE["run"]
        before = pol.TaskAuthority.from_packet(
            FIXTURE["packet"], repo_root=run["repo_root"],
            worktree=run["worktree"], branch=run["branch"], stage=run["stage"])
        self.assertEqual(before.documented_test_commands, ())
        decision = classify(FIXTURE["intended_auto"][0], before)
        self.assertEqual(decision.tier, pol.ASK)
        self.assertEqual(decision.reason_code, "undocumented_command")

    def test_a_command_outside_the_task_authority_is_not_auto(self) -> None:
        foreign = pol.TaskAuthority(
            task_id="M0-T999", stage="in_progress", repo_root="/repo",
            worktree="/repo/wt-other", branch="task/other",
            documented_test_commands=("python tools/test_other.py",))
        decision = classify(FIXTURE["intended_auto"][0], foreign)
        self.assertEqual(decision.tier, pol.ASK)
        self.assertEqual(decision.reason_code, "undocumented_command")


# --------------------------------------------------------------------------
# AS-6: the field cannot become a general allowlist
# --------------------------------------------------------------------------


class NoBroadGrantTests(unittest.TestCase):
    def test_the_entry_cap_forbids_allowlist_scale(self) -> None:
        self.assertLessEqual(pol.MAX_DOCUMENTED_TEST_COMMANDS, 16)

    def test_a_documented_command_still_authorizes_nothing_else(self) -> None:
        authority = fixture_authority()
        for command in ("git push origin main", "pip install anything",
                        "curl https://example.com", "del /s /q ."):
            decision = classify(command, authority)
            self.assertNotEqual(decision.tier, pol.AUTO, command)

    def test_no_wildcard_program_can_be_documented(self) -> None:
        for entry in ("* tools/test.py", "? tools/test.py", "*"):
            with self.assertRaises(pol.PolicyError):
                pol.validate_documented_test_commands(
                    {pol.DOCUMENTED_TEST_COMMANDS_KEY: [entry]})


# --------------------------------------------------------------------------
# AS-8 / AS-9: revoke-all / pending-approvals / status reconciliation
# --------------------------------------------------------------------------


class RevokeStatusLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._checkout_tmp = tempfile.TemporaryDirectory()
        self._base_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._checkout_tmp.cleanup)
        self.addCleanup(self._base_tmp.cleanup)
        self.checkout = pathlib.Path(self._checkout_tmp.name).resolve()
        self.base = pathlib.Path(self._base_tmp.name).resolve()
        from tools.agent_supervisor.durable_state import runtime_dir_for
        self.runtime = runtime_dir_for(self.checkout, base=self.base)
        self.runtime.mkdir(parents=True)
        self.journal = DurableJournal(self.runtime / DB_FILENAME).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / cli.AUDIT_FILENAME, fsync=False)
        self.authority = pol.TaskAuthority(
            task_id="M0-T063", stage="in_progress",
            repo_root=str(self.checkout), worktree=str(self.checkout),
            branch="task/M0-T063-context-index-a1", status="in_progress",
            active=True)
        self.broker = bk.ApprovalBroker(
            self.journal, self.audit, authority=self.authority, mode="shadow",
            run_id="run_M0_T063_A1")

    def defer_one(self, command: str) -> bk.ApprovalRequest:
        request = bk.build_request(
            tool_name="Bash", tool_input={"command": command},
            authority=self.authority, argv=(), target_paths=(),
            head_sha="a" * 40, origin_main_sha="b" * 40, session_id="sess-1")
        action = bk.action_from_tool_request("Bash", {"command": command})
        outcome = self.broker.evaluate_request(request, action)
        self.assertEqual(outcome.behavior, bk.DEFER_TO_OWNER)
        return request

    def status_payload(self) -> dict:
        args = argparse.Namespace(checkout=str(self.checkout),
                                  runtime_base=str(self.base), json=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.cmd_status(args)
        self.assertEqual(code, 0)
        return json.loads(out.getvalue())

    def pending_payload(self) -> dict:
        args = argparse.Namespace(checkout=str(self.checkout),
                                  runtime_base=str(self.base), json=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.cmd_pending_approvals(args)
        self.assertEqual(code, 0)
        return json.loads(out.getvalue())

    def test_pending_then_revoke_all_then_zero_and_no_open_ask(self) -> None:
        self.defer_one("python tools/test_repo_fingerprint.py")

        pending = self.pending_payload()
        self.assertEqual(pending["count"], 1)
        status = self.status_payload()
        self.assertEqual(len(status["open_asks"]), 1)
        self.assertEqual(status["resolved_asks"], [])

        revoked = self.broker.revoke_all(reason="operator revoke-all")
        self.assertEqual(revoked, 1)

        self.assertEqual(self.pending_payload()["count"], 0)
        status = self.status_payload()
        self.assertEqual(status["open_asks"], [])
        for entry in status["resolved_asks"]:
            self.assertFalse(entry.get("actionable", True))
        self.assertTrue(status["journal_ok"])
        self.assertTrue(status["audit_chain_ok"])
        self.assertEqual(self.journal.open_asks(), [])

    def test_the_revoked_ask_row_is_preserved_history_not_deleted(self) -> None:
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        self.broker.revoke_all(reason="operator revoke-all")
        rows = list(self.journal.conn.execute(
            "SELECT ask_id, answered_at_utc, answer, request_digest "
            "FROM queued_asks"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ask_id"], f"ask_{request.request_id}")
        self.assertNotEqual(rows[0]["answered_at_utc"], "")
        self.assertIn("revoked", rows[0]["answer"])
        self.assertEqual(rows[0]["request_digest"], request.digest())
        record = self.broker.record(request.request_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["status"], bk.STATUS_REVOKED)

    def test_a_pre_fix_journal_reports_revoked_history_without_mutation(
            self) -> None:
        """The live A1 journal shape: queued_asks rows still unanswered while
        every approval record is REVOKED (written before this repair). `status`
        must label them revoked history, list zero open asks, and must not
        write to the journal - the read path alone has to be truthful.
        """
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        # Reproduce the PRE-FIX revoke: flip the approval record only, leaving
        # the queued_asks row unanswered (exactly what revoke_all used to do).
        key = f"{bk.APPROVAL_PREFIX}{request.request_id}"
        record = self.journal.get_state(key)
        record["status"] = bk.STATUS_REVOKED
        record["revoked_reason"] = "operator revoke-all"
        self.journal.set_state(key, record)
        self.assertEqual(len(self.journal.open_asks()), 1)  # the defect shape

        status = self.status_payload()
        self.assertEqual(status["open_asks"], [])
        self.assertEqual(len(status["resolved_asks"]), 1)
        entry = status["resolved_asks"][0]
        self.assertFalse(entry["actionable"])
        self.assertEqual(entry["approval_status"], bk.STATUS_REVOKED)
        # Read-only: the row itself is still unanswered afterward.
        self.assertEqual(len(self.journal.open_asks()), 1)
        self.assertTrue(status["audit_chain_ok"])

    def test_a_loop_origin_ask_without_approval_record_stays_open(self) -> None:
        self.journal.queue_ask(QueuedAsk(
            ask_id="rotation_pause/run_M0_T063_A1/3", run_id="run_M0_T063_A1",
            task_id="M0-T063", question="rotation paused; how to proceed?",
            request_digest="d" * 64, created_at_utc=to_utc_iso(),
            classification="security"))
        self.broker.revoke_all(reason="operator revoke-all")
        status = self.status_payload()
        self.assertEqual(len(status["open_asks"]), 1)
        self.assertEqual(status["open_asks"][0]["ask_id"],
                         "rotation_pause/run_M0_T063_A1/3")

    def test_deny_resolves_the_queued_ask_row_not_just_the_approval_record(
            self) -> None:
        """M0-T113 live-restart defect (D-024-R274): `deny` answered the
        approval record but left the `ask_<request_id>` row unanswered, so the
        S11.5 `pending_requests` revalidation blocked every later restart. An
        owner deny must resolve its ask row exactly as revoke_all does."""
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        self.assertEqual(len(self.journal.open_asks()), 1)

        outcome = self.broker.deny_request(request.request_id, request.digest())
        self.assertEqual(outcome.reason_code, "owner_denied")

        self.assertEqual(self.journal.open_asks(), [])
        rows = list(self.journal.conn.execute(
            "SELECT ask_id, answered_at_utc, answer FROM queued_asks"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ask_id"], f"ask_{request.request_id}")
        self.assertNotEqual(rows[0]["answered_at_utc"], "")
        self.assertIn("denied", rows[0]["answer"])
        record = self.broker.record(request.request_id)
        self.assertEqual(record["status"], bk.STATUS_DENIED)

    def test_approve_once_resolves_the_queued_ask_row(self) -> None:
        """Same defect class on the approve path (D-024-R274): an owner-answered
        request must never linger as an open question blocking restart."""
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        outcome = self.broker.approve_once(request.request_id, request.digest())
        self.assertEqual(outcome.reason_code, "owner_approved_once")

        self.assertEqual(self.journal.open_asks(), [])
        rows = list(self.journal.conn.execute(
            "SELECT ask_id, answered_at_utc, answer FROM queued_asks"))
        self.assertEqual(len(rows), 1)
        self.assertNotEqual(rows[0]["answered_at_utc"], "")
        self.assertIn("approved", rows[0]["answer"])
        record = self.broker.record(request.request_id)
        self.assertEqual(record["status"], bk.STATUS_APPROVED)

    def test_a_digest_mismatch_deny_leaves_the_ask_row_open(self) -> None:
        """A refused answer is NOT an answer: only a successful deny/approve
        resolves the ask row; a digest mismatch leaves the question open."""
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        outcome = self.broker.deny_request(request.request_id, "0" * 64)
        self.assertEqual(outcome.reason_code, "digest_mismatch")
        self.assertEqual(len(self.journal.open_asks()), 1)

    def test_resolve_ask_is_idempotent_and_reports_misses(self) -> None:
        request = self.defer_one("python tools/test_repo_fingerprint.py")
        ask_id = f"ask_{request.request_id}"
        self.assertTrue(self.journal.resolve_ask(ask_id, "revoked: test"))
        self.assertFalse(self.journal.resolve_ask(ask_id, "revoked: again"))
        self.assertFalse(self.journal.resolve_ask("ask_missing", "revoked"))


if __name__ == "__main__":
    unittest.main()
