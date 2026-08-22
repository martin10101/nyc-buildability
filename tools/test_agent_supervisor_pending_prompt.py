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
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    runtime_dir_for,
)
from tools.agent_supervisor.loop import (  # noqa: E402
    approve_pending_prompt,
    consume_pending_prompt,
    pending_prompt_key,
)
from tools.agent_supervisor.resume_scheduler import EMERGENCY_STOP_KEY  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402
from tools.test_agent_supervisor_loop import (  # noqa: E402
    HEAD_SHA,
    FakeRunner,
    FakeReviewer,
    LoopTestBase,
    checkpoint as make_checkpoint,
    decision as make_decision,
    outcome,
    run_result,
)


def covered_pending(**overrides: object) -> dict:
    """M0-T048: a well-formed parked forward record whose structured instruction
    reproduces both the operator-named approval digest and the deterministic body."""
    instruction = {
        "task_id": "M0-T036", "stage": "phase4",
        "allowed_paths": ["tools/agent_supervisor/**"],
        "requested_action": "ship it",
        "stop_conditions": ["no bypass flags"],
    }
    prompt = lp.build_forwarded_prompt(**instruction)
    record = {
        "cycle": 1, "digest": lp.approval_digest(**instruction),
        "approved_instruction": instruction, "prompt": prompt,
        "prompt_bytes_digest": lp.digest_of(prompt), "decision": "forward",
        "created_at_utc": "2026-08-05T00:00:00Z",
    }
    record.update(overrides)
    return record


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

    def test_successful_resume_marks_the_record_approved_not_consumed(self) -> None:
        """M0-T045: the contract changed. A successful resume no longer CONSUMES
        the record (which dropped the prompt bytes and stranded a cross-process
        forward); it marks it APPROVED, dropping only the re-approvable `digest`
        key so re-approval still fails closed while the held prompt survives."""
        pending = covered_pending()
        digest = pending["digest"]
        self._park(pending=pending)
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", digest)
        self.assertEqual(code, 0)
        self.assertEqual(self._state(), sm.FORWARD_PROMPT)
        record = self._pending()
        self.assertIsInstance(record, dict)
        self.assertTrue(record.get("approved"))
        self.assertFalse(record.get("digest"),
                         "the re-approvable digest must be dropped so it cannot be "
                         "re-approved")
        self.assertEqual(record.get("prompt"), pending["prompt"],
                         "the held prompt bytes must survive approval for a "
                         "cross-process forward")
        self.assertEqual(record.get("approved_digest"), digest,
                         "M0-T048: approved_digest binds to the operator-named digest")

    def test_a_second_resume_of_an_approved_record_fails_closed(self) -> None:
        """The re-approval guard is `not pending.get("digest")`; an approved record
        drops that key, so a second resume for the old digest refuses."""
        pending = covered_pending()
        digest = pending["digest"]
        self._park(pending=pending)
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", digest)
        self.assertEqual(code, 0)
        # State is now FORWARD_PROMPT, so a second resume is refused first by the
        # state guard; force it back to WAIT_FOR_OWNER to prove the DIGEST guard
        # (not merely the state guard) also fails closed on an approved record.
        runtime_dir = self._runtime_dir()
        journal = DurableJournal(runtime_dir / DB_FILENAME).open()
        try:
            journal.set_state("current_state", sm.WAIT_FOR_OWNER)
        finally:
            journal.close()
        code2, _out2, err2 = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", digest)
        self.assertEqual(code2, 1)
        self.assertIn("no pending-prompt record", err2)

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


class CliMismatchPreservesRecordTests(CliResumeConsumeTests):
    """AS-4 FAILURE-path lock (G4 QA review section 6): a mismatched digest must
    refuse WITHOUT consuming or mutating the pending record."""

    def test_a_mismatched_digest_refuses_and_preserves_the_record(self) -> None:
        digest = "a1b2c3d4e5f6"
        self._park(pending={"cycle": 1, "digest": digest, "decision": "forward",
                            "created_at_utc": "2026-08-05T00:00:00Z"})
        code, _out, err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", "deadbeefdead0")
        self.assertEqual(code, 1)
        self.assertIn("does not", err)
        # State unchanged and the record still carries its exact, unconsumed digest.
        self.assertEqual(self._state(), sm.WAIT_FOR_OWNER)
        record = self._pending()
        self.assertIsInstance(record, dict)
        self.assertFalse(record.get("consumed"),
                         "a mismatched digest must NOT consume the record")
        self.assertEqual(record.get("digest"), digest)


class LoopFailurePreservesRecordTests(LoopTestBase):
    """AS-4 FAILURE-path lock (G4 QA review section 6): a declined approval and an
    unsent forward each leave the pending_prompt record intact (digest survives,
    never consumed), so the record can only be consumed by a genuine approve+send."""

    def _supervised_loop(self, *, approval, forward_patch=None) -> lp.SupervisedLoop:
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
            run_id=self.run_id, approval_gate=approval)
        if forward_patch is not None:
            loop.forward_exactly_once = forward_patch  # type: ignore[assignment]
        return loop

    def test_a_declined_approval_does_not_consume_the_record(self) -> None:
        loop = self._supervised_loop(approval=lambda _digest, _prompt: False)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertFalse(result.forwarded)
        self.assertEqual(result.stopped, "operator_declined")
        record = self.journal.get_state(pending_prompt_key(self.run_id))
        self.assertIsInstance(record, dict)
        self.assertFalse(record.get("consumed"),
                         "a declined approval must NOT consume the record")
        self.assertTrue(record.get("digest"),
                        "the held digest must survive a decline (nothing dropped)")

    def test_an_unsent_forward_does_not_consume_the_record(self) -> None:
        # Approval passes, but the forward is not sent (e.g. duplicate-suppressed).
        # Consume is gated on `forward.sent`, so the record must survive intact.
        loop = self._supervised_loop(
            approval=lambda _digest, _prompt: True,
            forward_patch=lambda *a, **k: lp.ForwardResult("m", sent=False))
        result = loop.run_cycle("first unit", cycle=1)
        self.assertFalse(result.forwarded)
        record = self.journal.get_state(pending_prompt_key(self.run_id))
        self.assertIsInstance(record, dict)
        self.assertFalse(record.get("consumed"),
                         "an unsent forward must NOT consume the record")
        self.assertTrue(record.get("digest"))


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


class CrossProcessResumeTests(unittest.TestCase):
    """M0-T045 T1: the integration lock across the process boundary. Park via a
    real supervised loop run, approve via a SEPARATE `resume-pending-prompt` CLI
    call, then forward via a FRESH loop.run() that shares only the durable
    journal - exactly the sequence the live R595 rehearsal broke on. With a
    rotation armed, the resume must also actuate the seam (archive -> mint ->
    relaunch), which is the point of the rehearsal.
    """

    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        self.cli = cli
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.runtime = self.tmp / "runtime"
        self.run_id = "run-xproc"
        self.runtime_dir = runtime_dir_for(self.repo, base=str(self.runtime))

    # -- infrastructure shared with the real loop + real CLI --------------------

    def _open(self) -> DurableJournal:
        return DurableJournal(self.runtime_dir / DB_FILENAME).open()

    def _authority(self) -> pol.TaskAuthority:
        return pol.TaskAuthority.from_packet(
            {"task_id": "M0-T036",
             "allowed_paths": ["tools/agent_supervisor/**",
                               "tools/test_agent_supervisor_*.py"],
             "forbidden_paths": [".github/**", ".claude/**"],
             "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T036-supervisor-bridge", stage="phase4",
            documented_test_commands=("python tools/test_agent_supervisor_loop.py",))

    def _build_loop(self, journal: DurableJournal, *, runner, reviewer,
                    approval_gate, max_cycles: int) -> lp.SupervisedLoop:
        audit = AuditLog(self.runtime_dir / "audit.jsonl", fsync=False)
        machine = StateMachine(journal, audit, self.run_id)
        authority = self._authority()
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036", stage="phase4",
                                 allowed_paths=authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=max_cycles, owner_touch_budget=4),
            journal=journal, audit=audit, machine=machine, authority=authority,
            runner=runner, reviewer=reviewer, run_id=self.run_id,
            # M0-T080: a rotation now builds the FULL S11.3 handoff, which must
            # name the authoritative HEAD. A seam that cannot name one refuses on
            # `sha_ambiguous` rather than rotating into an unknown state, so the
            # fixture states the HEAD a real run always knows.
            head_sha="b" * 40,
            approval_gate=approval_gate)

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        argv = [*args, "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime)]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.cli.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def _outbox_rows(self, message_id: str) -> list[dict]:
        journal = self._open()
        try:
            rows = journal.conn.execute(
                "SELECT envelope FROM outbox WHERE message_id = ?",
                (message_id,)).fetchall()
        finally:
            journal.close()
        return [json.loads(r["envelope"]) for r in rows]

    # -- the test ---------------------------------------------------------------

    def test_park_then_cli_approve_then_fresh_start_forwards_once_and_rotates(
            self) -> None:
        # PROCESS 1: a supervised run reaches the WAIT with no approval and PARKS
        # the held prompt (approval declined => operator_declined, journal at
        # WAIT_FOR_OWNER with the new-shape record that carries the prompt bytes).
        j1 = self._open()
        loop1 = self._build_loop(
            j1, runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            approval_gate=lambda _d, _p: False, max_cycles=1)
        loop1.machine.transition(sm.PREFLIGHT, "start_command")
        result1 = loop1.run_cycle("first unit", cycle=1)
        self.assertEqual(result1.stopped, "operator_declined")
        parked = j1.get_state(pending_prompt_key(self.run_id))
        j1.close()
        self.assertIsInstance(parked, dict)
        held_prompt = parked["prompt"]
        binding_digest = parked["digest"]
        self.assertTrue(held_prompt, "the held prompt bytes must be parked durably")

        # PROCESS 2: a SEPARATE resume-pending-prompt CLI call approves it. The
        # journal advances to FORWARD_PROMPT and the record retains the prompt.
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", binding_digest)
        self.assertEqual(code, 0)
        approved = self._open()
        try:
            self.assertEqual(str(approved.get_state("current_state")),
                             sm.FORWARD_PROMPT)
            approved_record = approved.get_state(pending_prompt_key(self.run_id))
        finally:
            approved.close()
        self.assertTrue(approved_record.get("approved"))
        self.assertEqual(approved_record.get("prompt"), held_prompt)

        # PROCESS 3: a fresh `start`/loop that shares only the durable journal.
        # Arm a rotation so the resume MUST actuate the seam. Cycle 2 completes so
        # the run ends cleanly without re-parking.
        j3 = self._open()
        j3.set_state(rot.ROTATION_PENDING_KEY, True)
        complete = outcome(make_decision(decision="COMPLETE", next_claude_prompt="",
                                         evidence_refs=[{"path": "report.md"}]))
        # M0-T080: the session that comes up after the seam rotation is a
        # RE-ORIENTED successor, so its first answer is the S11.3 READY checkpoint
        # reporting the task/branch/worktree/HEAD it was commanded onto - which
        # the READY gate and the post-launch identity check now verify.
        successor = run_result(
            session_id="sess-successor",
            checkpoint=make_checkpoint(
                status="READY", checkpoint_id="cp-successor",
                claude_session_id="sess-successor",
                starting_sha=HEAD_SHA, current_sha=HEAD_SHA,
                worktree=str(self.repo),
                summary="re-oriented from the verified handoff; nothing changed",
                proposed_next_action="await the forwarded unit"))
        # The seam fires BEFORE this process runs any unit, so the very first
        # unit loop3 dispatches is the re-oriented successor's.
        loop3 = self._build_loop(
            j3, runner=FakeRunner(successor),
            reviewer=FakeReviewer(complete), approval_gate=lambda _d, _p: True,
            max_cycles=2)
        run = loop3.run("ignored - the approved prompt is read from the journal")
        final_state = str(j3.get_state("current_state"))
        post = j3.get_state(pending_prompt_key(self.run_id))
        j3.close()

        # Exactly one forward, byte-identical to what was held (digest verified by
        # the loop before it forwarded).
        self.assertEqual(len(run.forwarded_message_ids), 1,
                         "the approved prompt is forwarded exactly once")
        message_id = run.forwarded_message_ids[0]
        rows = self._outbox_rows(message_id)
        self.assertEqual(len(rows), 1, "exactly one outbox row for the forward")
        # M0-T048: forwarded == the operator-covered body (== held) + forward-time clock.
        forwarded = rows[0]["payload"]["prompt"]
        body, _, _ = forwarded.partition("FORWARDED AT: ")
        self.assertEqual(body, held_prompt,
                         "the operator-covered body forwarded is identical to what was "
                         "held; only the non-authoritative clock stamp is appended")
        self.assertEqual(approved_record["approved_digest"], binding_digest,
                         "approved_digest is the operator-named approval digest")
        # The seam actuated: a rotation was recorded (archive -> mint -> relaunch).
        self.assertTrue(run.rotations, "an armed rotation must actuate at the seam")
        # The record is consumed, so a re-approval fails closed.
        self.assertTrue(post.get("consumed"))
        self.assertFalse(post.get("digest"))
        self.assertFalse(post.get("approved_digest"))
        self.assertIn(final_state, (sm.COMPLETE, sm.CLAUDE_RUNNING))

        # And a second resume-pending-prompt CLI call now refuses (nothing parked).
        code2, _out2, err2 = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", binding_digest)
        self.assertEqual(code2, 1)


class LoopResumeFailClosedTests(LoopTestBase):
    """M0-T045 T2: every degenerate FORWARD_PROMPT entry refuses with a structured
    forwarded_prompt_unavailable, contacts no provider, and leaves the journal
    unchanged. Exercised through the real loop.run() entry."""

    def _at_forward_prompt(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")
        self.machine.transition(sm.WAIT_FOR_OWNER, "preflight_requires_owner")
        self.machine.transition(sm.FORWARD_PROMPT, "owner_approved_pending_prompt")

    def _loop(self, *, runner=None) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=runner or FakeRunner(run_result()),
            reviewer=FakeReviewer(outcome()), run_id=self.run_id,
            approval_gate=lambda _d, _p: True)

    def _assert_refused(self, loop: lp.SupervisedLoop, *, runner) -> None:
        state_before = self.machine.current_state
        with self.assertRaises(lp.LoopError) as ctx:
            loop.run("ignored")
        self.assertEqual(ctx.exception.code, "forwarded_prompt_unavailable")
        self.assertEqual(loop.provider_calls, 0, "no provider call on a refusal")
        self.assertEqual(runner.prompts, [], "the worker was never contacted")
        self.assertEqual(self.machine.current_state, state_before,
                         "a refused resume never advances the journal")

    def test_old_shape_record_without_prompt_bytes_refuses(self) -> None:
        self._at_forward_prompt()
        # A pre-fix approved record: no held prompt bytes were ever parked.
        self.journal.set_state(pending_prompt_key(self.run_id),
                               {"approved": True, "cycle": 1, "decision": "CONTINUE",
                                "prior_digest": "b" * 64})
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)

    def test_digest_mismatch_refuses(self) -> None:
        self._at_forward_prompt()
        prompt = "REQUESTED ACTION:\ndo it\n"
        self.journal.set_state(
            pending_prompt_key(self.run_id),
            {"approved": True, "cycle": 1, "prompt": prompt,
             "approved_digest": "deadbeef" * 8,  # NOT digest_of(prompt)
             "decision": "CONTINUE", "prior_digest": "b" * 64})
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)

    def test_missing_record_refuses(self) -> None:
        self._at_forward_prompt()
        # No pending_prompt record at all.
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)

    def test_consumed_record_refuses(self) -> None:
        self._at_forward_prompt()
        self.journal.set_state(pending_prompt_key(self.run_id),
                               {"consumed": True, "prior_digest": "b" * 64})
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)

    def test_journal_not_actually_approved_refuses(self) -> None:
        # State is FORWARD_PROMPT but the last trigger is NOT the owner approval.
        self.journal.set_state("current_state", sm.FORWARD_PROMPT)
        self.journal.set_state("last_trigger", "prompt_forwarded")
        prompt = "REQUESTED ACTION:\ndo it\n"
        self.journal.set_state(
            pending_prompt_key(self.run_id),
            {"approved": True, "cycle": 1, "prompt": prompt,
             "approved_digest": lp.digest_of(prompt), "decision": "CONTINUE",
             "prior_digest": "b" * 64})
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)

    def test_emergency_stop_refuses(self) -> None:
        self._at_forward_prompt()
        prompt = "REQUESTED ACTION:\ndo it\n"
        self.journal.set_state(
            pending_prompt_key(self.run_id),
            {"approved": True, "cycle": 1, "prompt": prompt,
             "approved_digest": lp.digest_of(prompt), "decision": "CONTINUE",
             "prior_digest": "b" * 64})
        self.journal.set_state(EMERGENCY_STOP_KEY, True)
        runner = FakeRunner(run_result())
        self._assert_refused(self._loop(runner=runner), runner=runner)


class LoopResumeForwardExactlyOnceTests(LoopTestBase):
    """M0-T045 T4: a crash between the approved send and its consume must not
    double-forward. A second FORWARD_PROMPT entry re-uses the same message id and
    the outbox suppresses the duplicate: exactly one send survives."""

    def _approved_at_forward_prompt(self, binding: str) -> tuple[str, str]:
        base = covered_pending()
        record = {"approved": True, "cycle": 1, "prompt": base["prompt"],
                  "approved_instruction": base["approved_instruction"],
                  "prompt_bytes_digest": base["prompt_bytes_digest"],
                  # M0-T048: approved_digest is the operator-named approval digest.
                  "approved_digest": base["digest"], "decision": "CONTINUE",
                  "reviewed_checkpoint_id": "cp-1", "prior_digest": binding}
        self.journal.set_state("current_state", sm.FORWARD_PROMPT)
        self.journal.set_state("last_trigger", "owner_approved_pending_prompt")
        self.journal.set_state(pending_prompt_key(self.run_id), record)
        # M0-T048 REWORK (D-010 R145..R150): a GENUINE cross-process approval always
        # seals an operator-approval audit event naming the operator digest; the resume
        # now cross-checks approved_digest against it, so a faithful stage must include
        # it (this mirrors what `resume-pending-prompt` writes on a real approval).
        self.audit.append(lp.OPERATOR_APPROVAL_EVENT, run_id=self.run_id,
                          input_digest=base["digest"], decision="approve",
                          state_from=sm.WAIT_FOR_OWNER, state_to=sm.FORWARD_PROMPT,
                          detail={"operator_initiated": True, "cycle": 1})
        return f"{self.run_id}/fwd/1/{binding[:16]}", base["prompt"]

    def _loop(self, *, runner) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=1, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority, runner=runner,
            reviewer=FakeReviewer(outcome()), run_id=self.run_id,
            approval_gate=lambda _d, _p: True)

    def test_a_second_resume_does_not_double_forward(self) -> None:
        binding = "c" * 64
        message_id, prompt = self._approved_at_forward_prompt(binding)

        # CRASH SIMULATION: the send happened durably, but the process died before
        # the CLAUDE_RUNNING transition and the consume (state still FORWARD_PROMPT,
        # record still approved). Perform just the forward, nothing after.
        crashed = self._loop(runner=FakeRunner(run_result()))
        first = crashed._resume_forward(
            prompt, cycle=1, approval_binding=binding, decision_str="CONTINUE",
            reviewed_checkpoint_id="cp-1")
        self.assertTrue(first.sent)

        # A fresh loop resumes from the same FORWARD_PROMPT. The outbox row is
        # already sent, so forward_exactly_once suppresses the duplicate: no
        # second send, and the journal still advances to CLAUDE_RUNNING once.
        runner2 = FakeRunner(run_result())
        loop2 = self._loop(runner=runner2)
        loop2.run("ignored")

        rows = self.journal.conn.execute(
            "SELECT COUNT(*) AS n FROM outbox WHERE message_id = ?",
            (message_id,)).fetchone()
        self.assertEqual(rows["n"], 1, "exactly one outbox row: no double-send")
        self.assertEqual(self.machine.current_state, sm.CLAUDE_RUNNING)
        record = self.journal.get_state(pending_prompt_key(self.run_id))
        self.assertTrue(record.get("consumed"),
                        "the second resume consumes the record after the forward")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
