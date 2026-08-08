#!/usr/bin/env python3
"""M0-T046 SCOPE 1 (D-010-R124) - park->approve operator-digest binding.

G5 M0-T045 LOW-1: `approve_pending_prompt` froze `approved_digest =
digest_of(parked prompt bytes)` by RE-HASHING whatever bytes were parked AT
APPROVAL time, without cross-checking them against a value anchored at park. An
attacker with journal write who tampered the `prompt` field between park and
approval got the tampered bytes forwarded under a self-consistent digest; the
only thing standing in the way was the journal-file ACL.

The fix parks a `prompt_bytes_digest` byte anchor at park (when the bytes are
authentic), re-verifies the parked bytes against it at approval BEFORE any state
change, refuses fail-closed (sealed refusal record, no approval) on a mismatch,
and binds `approved_digest` to the anchor rather than a fresh re-hash. The
resume-time check (`digest_of(prompt) == approved_digest`) then catches any
tamper AFTER approval.

These tests drive the REAL loop (to park), the REAL `resume-pending-prompt` CLI
(to approve), and the REAL loop again (to forward), tampering the durable journal
between the steps - exactly the threat. Deterministic, stdlib unittest, no
network, no credentials.

Scenario map:
  AS-1 <- test_tamper_between_park_and_approval_is_refused (attacker path a)
  AS-1 <- test_tamper_after_approval_is_caught_at_resume    (attacker path b)
  AS-1 <- test_happy_path_operator_digest_binds_and_forwards (path c)
  AS-1 <- test_missing_digest_arg_exits_nonzero / test_blank_digest_refused (CLI arg)
  AS-1 <- ApprovePendingPromptUnitTests (the binding function fails closed directly)
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
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    runtime_dir_for,
)
from tools.agent_supervisor.loop import (  # noqa: E402
    LoopError,
    approve_pending_prompt,
    pending_prompt_key,
)
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402
from tools.test_agent_supervisor_loop import (  # noqa: E402
    FakeRunner,
    FakeReviewer,
    decision as make_decision,
    outcome,
    run_result,
)


class _CrossProcessHarness(unittest.TestCase):
    """Park via a real supervised loop, approve via the real CLI, forward via a
    fresh loop that shares only the durable journal."""

    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        self.cli = cli
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.runtime = self.tmp / "runtime"
        self.run_id = "run-bind"
        self.runtime_dir = runtime_dir_for(self.repo, base=str(self.runtime))

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
            approval_gate=approval_gate)

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        argv = [*args, "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime)]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.cli.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def _park_real(self) -> dict:
        """Run one supervised cycle whose approval is DECLINED so the run parks the
        held prompt bytes + byte anchor at WAIT_FOR_OWNER, and return that record."""
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
        self.assertTrue(parked.get("prompt"), "held prompt bytes must be parked")
        self.assertTrue(parked.get("prompt_bytes_digest"),
                        "a park-time byte anchor must be recorded")
        self.assertEqual(lp.digest_of(parked["prompt"]),
                         parked["prompt_bytes_digest"],
                         "the anchor must be the digest of the authentic bytes")
        # M0-T048 (R136): the structured approved instruction is parked, and it
        # reproduces both the operator-named digest and the parked body (the forwarded
        # content is thus bound to operator-covered material, not journal bytes).
        instruction = parked.get("approved_instruction")
        self.assertIsInstance(instruction, dict,
                              "the structured approved instruction must be parked")
        self.assertEqual(lp.approval_digest(**instruction), parked["digest"],
                         "the parked instruction must reproduce the operator digest")
        self.assertEqual(lp.build_forwarded_prompt(**instruction), parked["prompt"],
                         "the parked body must be the deterministic reconstruction")
        self.assertNotIn("FORWARDED AT", parked["prompt"],
                         "the parked body is timestamp-free; the clock is added at "
                         "forward time only")
        return parked

    def _set_pending(self, record: dict) -> None:
        j = self._open()
        try:
            j.set_state(pending_prompt_key(self.run_id), record)
        finally:
            j.close()

    def _pending(self) -> dict | None:
        j = self._open()
        try:
            return j.get_state(pending_prompt_key(self.run_id))
        finally:
            j.close()

    def _state(self) -> str:
        j = self._open()
        try:
            return str(j.get_state("current_state"))
        finally:
            j.close()

    def _audit_events(self) -> list[dict]:
        path = self.runtime_dir / "audit.jsonl"
        return [json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]


class TamperBetweenParkAndApproval(_CrossProcessHarness):
    def test_tamper_between_park_and_approval_is_refused(self) -> None:
        """Attacker path (a): a journal-write tamper of the parked `prompt` field
        between park and approval is refused fail-closed - no transition, a sealed
        refusal audit record, and no approved record."""
        parked = self._park_real()
        approval_digest = parked["digest"]

        # ATTACK: rewrite ONLY the prompt bytes, leaving the anchor + approval
        # digest intact (exactly what the finding describes).
        tampered = dict(parked)
        tampered["prompt"] = parked["prompt"] + "\nSILENTLY INJECTED INSTRUCTION\n"
        self._set_pending(tampered)

        code, _out, err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", approval_digest)
        self.assertEqual(code, 1, "a tampered parked prompt must be refused")
        self.assertIn("byte anchor", err)

        # No state change: still parked at WAIT_FOR_OWNER, record NOT approved.
        self.assertEqual(self._state(), sm.WAIT_FOR_OWNER)
        record = self._pending()
        self.assertIsInstance(record, dict)
        self.assertFalse(record.get("approved"),
                         "a refused approval must not mark the record approved")

        # A SEALED (hash-chained) refusal record was written; the chain still verifies.
        events = self._audit_events()
        refusals = [e for e in events
                    if e["event_type"] == "operator_resume_pending_prompt_refused"]
        self.assertEqual(len(refusals), 1)
        self.assertEqual(refusals[0]["decision"], "refuse")
        audit = AuditLog(self.runtime_dir / "audit.jsonl", fsync=False)
        self.assertTrue(audit.verify_chain().ok,
                        "the sealed refusal keeps the audit chain valid")


class TamperAfterApproval(_CrossProcessHarness):
    def test_tamper_after_approval_is_caught_at_resume(self) -> None:
        """Attacker path (b): a tamper of the approved record's prompt AFTER a
        legitimate approval is caught by the resume-time digest check; the fresh
        loop refuses to forward and contacts no provider."""
        parked = self._park_real()
        approval_digest = parked["digest"]

        # Legitimate approval via the real CLI.
        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", approval_digest)
        self.assertEqual(code, 0)
        approved = self._pending()
        self.assertTrue(approved.get("approved"))
        self.assertEqual(approved.get("approved_digest"),
                         parked["digest"],
                         "M0-T048: approved_digest binds to the OPERATOR-NAMED "
                         "approval digest, not a journal-resident byte anchor")

        # ATTACK: now tamper the approved record's held prompt.
        tampered = dict(approved)
        tampered["prompt"] = approved["prompt"] + "\nPOST-APPROVAL INJECTION\n"
        self._set_pending(tampered)

        # A fresh loop resumes from FORWARD_PROMPT and must refuse: the held bytes
        # no longer hash to approved_digest.
        j3 = self._open()
        loop3 = self._build_loop(
            j3, runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            approval_gate=lambda _d, _p: True, max_cycles=1)
        with self.assertRaises(LoopError) as ctx:
            loop3.run("ignored - read from journal")
        self.assertEqual(ctx.exception.code, "forwarded_prompt_unavailable")
        self.assertEqual(loop3.provider_calls, 0, "no provider call on a refusal")
        j3.close()


class HappyPath(_CrossProcessHarness):
    def test_happy_path_operator_digest_binds_and_forwards(self) -> None:
        """Path (c): the operator names the recorded digest, the parked bytes match
        the anchor, and a fresh loop forwards the byte-identical prompt exactly
        once under the anchored approved_digest."""
        parked = self._park_real()
        approval_digest = parked["digest"]
        held_prompt = parked["prompt"]

        code, _out, _err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", approval_digest)
        self.assertEqual(code, 0)
        self.assertEqual(self._state(), sm.FORWARD_PROMPT)

        j3 = self._open()
        complete = outcome(make_decision(decision="COMPLETE", next_claude_prompt="",
                                         evidence_refs=[{"path": "report.md"}]))
        loop3 = self._build_loop(
            j3, runner=FakeRunner(run_result(), run_result()),
            reviewer=FakeReviewer(complete), approval_gate=lambda _d, _p: True,
            max_cycles=2)
        run = loop3.run("ignored - read from journal")
        j3.close()

        self.assertEqual(len(run.forwarded_message_ids), 1,
                         "the approved prompt forwards exactly once")
        # The record is consumed; a re-approval now fails closed.
        post = self._pending()
        self.assertTrue(post.get("consumed"))
        self.assertFalse(post.get("digest"))
        # M0-T048: the forwarded bytes are the deterministic reconstruction (bound to
        # the operator-covered instruction) plus the forward-time clock. Stripping the
        # non-authoritative FORWARDED AT stamp yields exactly the held/anchored body.
        message_id = run.forwarded_message_ids[0]
        rows = self._outbox_rows(message_id)
        self.assertEqual(len(rows), 1)
        forwarded = rows[0]["payload"]["prompt"]
        self.assertTrue(forwarded.startswith(held_prompt),
                        "the forwarded body is the anchored body plus the clock stamp")
        self.assertIn("FORWARDED AT: ", forwarded)
        body, _, _ = forwarded.partition("FORWARDED AT: ")
        self.assertEqual(body, held_prompt,
                         "everything before the clock stamp is the operator-covered "
                         "body, byte-identical to what was held and anchored")
        self.assertEqual(lp.digest_of(body), parked["prompt_bytes_digest"])

    def _outbox_rows(self, message_id: str) -> list[dict]:
        j = self._open()
        try:
            rows = j.conn.execute(
                "SELECT envelope FROM outbox WHERE message_id = ?",
                (message_id,)).fetchall()
        finally:
            j.close()
        return [json.loads(r["envelope"]) for r in rows]


class CliArgPath(_CrossProcessHarness):
    def test_blank_digest_refused(self) -> None:
        """A blank --approve-prompt-digest is refused with no state change even
        when a record is parked (a malformed operator digest never approves)."""
        self._park_real()
        code, _out, err = self.run_cli(
            "resume-pending-prompt", "--approve-prompt-digest", "   ")
        self.assertEqual(code, 1)
        self.assertIn("empty", err)
        self.assertEqual(self._state(), sm.WAIT_FOR_OWNER)

    def test_missing_digest_arg_exits_nonzero(self) -> None:
        """A MISSING --approve-prompt-digest is rejected by the parser (required),
        exiting non-zero without touching the journal."""
        with self.assertRaises(SystemExit) as ctx:
            self.run_cli("resume-pending-prompt")
        self.assertNotEqual(ctx.exception.code, 0)


def covered_pending(**overrides: object) -> dict:
    """A well-formed parked record whose structured instruction reproduces both the
    operator-named approval digest and the deterministic forwarded body. Callers pass
    overrides to introduce a specific tamper."""
    instruction = {
        "task_id": "M0-T036", "stage": "phase4",
        "allowed_paths": ["tools/agent_supervisor/**",
                          "tools/test_agent_supervisor_*.py"],
        "requested_action": "Do the next bounded unit.",
        "stop_conditions": ["no bypass flags"],
    }
    prompt = lp.build_forwarded_prompt(**instruction)
    record = {
        "cycle": 1, "digest": lp.approval_digest(**instruction),
        "approved_instruction": instruction, "prompt": prompt,
        "prompt_bytes_digest": lp.digest_of(prompt), "decision": "forward",
    }
    record.update(overrides)
    return record


class ApprovePendingPromptUnitTests(unittest.TestCase):
    """The binding function itself fails closed, independent of the CLI (M0-T048)."""

    def _journal(self) -> DurableJournal:
        tmp = pathlib.Path(tempfile.mkdtemp())
        return DurableJournal(tmp / "j.sqlite3").open()

    def test_missing_instruction_refuses(self) -> None:
        """An old-shape record with held bytes but NO structured instruction refuses
        fail-closed - it is never verified journal-resident-only (AS-6)."""
        journal = self._journal()
        try:
            pending = {"cycle": 1, "prompt": "held bytes",
                       "prompt_bytes_digest": lp.digest_of("held bytes"),
                       "decision": "forward"}
            with self.assertRaises(LoopError) as ctx:
                approve_pending_prompt(journal, "r", pending=pending,
                                       approval_binding="a" * 64)
            self.assertEqual(ctx.exception.code, "pending_prompt_uncovered")
            self.assertIsNone(journal.get_state(pending_prompt_key("r")),
                              "a refused approval writes nothing")
        finally:
            journal.close()

    def test_instruction_not_reproducing_operator_digest_refuses(self) -> None:
        """A record whose structured instruction does NOT reproduce the operator-named
        approval binding refuses - the content would be uncovered."""
        journal = self._journal()
        try:
            pending = covered_pending()
            with self.assertRaises(LoopError) as ctx:
                approve_pending_prompt(journal, "r", pending=pending,
                                       approval_binding="a" * 64)  # != digest
            self.assertEqual(ctx.exception.code, "pending_prompt_uncovered")
        finally:
            journal.close()

    def test_byte_tamper_against_covered_instruction_refuses(self) -> None:
        """The held bytes no longer match the reconstruction from the (intact)
        operator-covered instruction: refuse fail-closed."""
        journal = self._journal()
        try:
            pending = covered_pending(prompt="held bytes",
                                      prompt_bytes_digest=lp.digest_of("held bytes"))
            with self.assertRaises(LoopError) as ctx:
                approve_pending_prompt(journal, "r", pending=pending,
                                       approval_binding=pending["digest"])
            self.assertEqual(ctx.exception.code, "pending_prompt_tampered")
        finally:
            journal.close()

    def test_matching_instruction_binds_to_the_operator_digest(self) -> None:
        journal = self._journal()
        try:
            pending = covered_pending()
            approve_pending_prompt(journal, "r", pending=pending,
                                   approval_binding=pending["digest"])
            record = journal.get_state(pending_prompt_key("r"))
            self.assertTrue(record.get("approved"))
            self.assertEqual(record.get("approved_digest"), pending["digest"],
                             "M0-T048: bound to the OPERATOR-NAMED approval digest")
            self.assertEqual(record.get("prompt"), pending["prompt"])
            self.assertFalse(record.get("digest"),
                             "the re-approvable digest key is dropped")
        finally:
            journal.close()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
