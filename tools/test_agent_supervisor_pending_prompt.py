#!/usr/bin/env python3
"""AS-4: resume-pending-prompt consumes/clears the pending_prompt record (M0-T041).

Evidence: G5 V1.2.3 LOW finding (project-control/reports/
M0-T036-V1.2.3-G5-security-delta-review.md): "neither it nor the loop
consumes/clears the record after use", so in an active supervised multi-cycle run
a later WAIT for a DIFFERENT ask could still carry a prior cycle's pending_prompt
and an operator supplying that (genuine) digest would re-fire
owner_approved_pending_prompt. These tests prove the record is consumed on a
successful resume/forward, so a stale record can never be re-approved.
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    runtime_dir_for,
)
from tools.agent_supervisor.loop import consume_pending_prompt, pending_prompt_key  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402
from tools.test_agent_supervisor_loop import (  # noqa: E402
    FakeRunner,
    FakeReviewer,
    LoopTestBase,
    outcome,
    run_result,
)


class ConsumeHelperTests(unittest.TestCase):
    def test_consume_writes_a_marker_with_no_truthy_digest(self) -> None:
        tmp = pathlib.Path(tempfile.mkdtemp())
        journal = DurableJournal(tmp / "j.sqlite3").open()
        try:
            journal.set_state(pending_prompt_key("r1"),
                              {"cycle": 1, "digest": "deadbeef"})
            consume_pending_prompt(journal, "r1", prior_digest="deadbeef")
            record = journal.get_state(pending_prompt_key("r1"))
        finally:
            journal.close()
        self.assertIsInstance(record, dict)
        self.assertTrue(record.get("consumed"))
        self.assertFalse(record.get("digest"),
                         "a consumed record must not carry a re-approvable digest")
        self.assertEqual(record.get("prior_digest"), "deadbeef")


class CliResumeConsumeTests(unittest.TestCase):
    """The CLI resume-pending-prompt command through cli.main."""

    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        self.cli = cli
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.runtime = self.tmp / "runtime"
        self.run_id = "run-pp"

    def _runtime_dir(self) -> pathlib.Path:
        return runtime_dir_for(self.repo, base=str(self.runtime))

    def _park(self, *, pending: dict | None) -> None:
        runtime_dir = self._runtime_dir()
        journal = DurableJournal(runtime_dir / DB_FILENAME).open()
        try:
            machine = StateMachine(
                journal, AuditLog(runtime_dir / "audit.jsonl", fsync=False),
                self.run_id)
            machine.transition(sm.PREFLIGHT, "start_command")
            machine.transition(sm.WAIT_FOR_OWNER, "preflight_requires_owner")
            if pending is not None:
                journal.set_state(pending_prompt_key(self.run_id), pending)
        finally:
            journal.close()

    def _state(self) -> str:
        journal = DurableJournal(self._runtime_dir() / DB_FILENAME).open()
        try:
            return str(journal.get_state("current_state"))
        finally:
            journal.close()

    def _pending(self) -> dict | None:
        journal = DurableJournal(self._runtime_dir() / DB_FILENAME).open()
        try:
            return journal.get_state(pending_prompt_key(self.run_id))
        finally:
            journal.close()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        argv = [*args, "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime)]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.cli.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_successful_resume_consumes_the_record(self) -> None:
        digest = "a1b2c3d4e5f6"
        self._park(pending={"cycle": 1, "digest": digest, "decision": "forward",
                            "created_at_utc": "2026-08-05T00:00:00Z"})
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", digest)
        self.assertEqual(code, 0)
        self.assertEqual(self._state(), sm.FORWARD_PROMPT)
        record = self._pending()
        self.assertIsInstance(record, dict)
        self.assertTrue(record.get("consumed"))
        self.assertFalse(record.get("digest"),
                         "the record must be consumed so it cannot be re-approved")

    def test_a_consumed_record_cannot_be_re_approved(self) -> None:
        """The regression: a journal parked at WAIT_FOR_OWNER whose pending record
        was already consumed refuses a resume for the old digest, fail-closed."""
        digest = "a1b2c3d4e5f6"
        # Simulate a later WAIT whose only pending record is a CONSUMED marker
        # from a prior cycle (exactly what consume_pending_prompt leaves behind).
        self._park(pending={"consumed": True,
                            "consumed_at_utc": "2026-08-05T00:00:00Z",
                            "prior_digest": digest})
        code, _out, err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", digest)
        self.assertEqual(code, 1)
        self.assertIn("no pending-prompt record", err)
        self.assertEqual(self._state(), sm.WAIT_FOR_OWNER,
                         "a refused resume never mutates state")


class LoopInProcessConsumeTests(LoopTestBase):
    def test_supervised_forward_consumes_the_pending_prompt(self) -> None:
        """The in-loop supervised path also consumes the record after it forwards
        the approved prompt (the finding named 'neither it nor the loop')."""
        self.at_preflight()
        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036",
                                 stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=1, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id,
            approval_gate=lambda _digest, _prompt: True)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertTrue(result.forwarded)
        record = self.journal.get_state(pending_prompt_key(self.run_id))
        self.assertIsInstance(record, dict)
        self.assertTrue(record.get("consumed"))
        self.assertFalse(record.get("digest"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
