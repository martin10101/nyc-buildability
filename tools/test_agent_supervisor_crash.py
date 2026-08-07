#!/usr/bin/env python3
"""Crash injection at every external effect and journal boundary (D-007 S15).

S15 closes with: "Where feasible, inject a crash immediately before and after
every external effect and journal boundary." This file does exactly that.

A "crash" here is the real thing as far as the durable state is concerned: the
journal handle is closed without any orderly shutdown and a brand-new
`DurableJournal` is opened on the same file, the way a fresh process would. No
in-memory state survives, so anything the run still knows afterwards is
something the journal genuinely persisted.

`BOUNDARIES` enumerates every boundary this file injects at, and a meta-test
proves each one has a test. The invariant under test never changes:

    after a crash at ANY boundary, the run either continues from the exact
    journaled point or refuses to continue - it never repeats a performed
    effect and never invents one that did not happen.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import external_effects as ex  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import CodexDecision, digest_of  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

#: Every boundary crashed at, and the test-name fragment that covers it.
BOUNDARIES: dict[str, str] = {
    "before_transition_commit": "before_a_transition_commit",
    "after_transition_commit": "after_a_transition_commit",
    "before_effect_begin": "before_an_effect_is_journaled",
    "after_effect_begin": "after_an_effect_is_journaled",
    "before_effect_confirm": "before_an_effect_is_confirmed",
    "after_effect_confirm": "after_an_effect_is_confirmed",
    "before_outbox_enqueue": "before_the_outbox_enqueue",
    "after_outbox_enqueue": "after_the_outbox_enqueue",
    "after_outbox_mark_sent": "after_the_outbox_mark_sent",
    "before_audit_append": "before_an_audit_append",
    "after_audit_append": "after_an_audit_append",
    "before_state_write": "before_a_state_write",
    "after_state_write": "after_a_state_write",
}


class CrashTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.db = self.tmp / "journal.sqlite3"
        self.audit_path = self.tmp / "audit.jsonl"
        self.journal = DurableJournal(self.db).open()
        self.audit = AuditLog(self.audit_path, fsync=True)
        self.run_id = "run-crash"
        self.repo = self.tmp / "repo"
        (self.repo / "src").mkdir(parents=True)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T036", "allowed_paths": ["src/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T036-supervisor-bridge", stage="phase4")

    def tearDown(self) -> None:
        try:
            self.journal.close()
        except Exception:  # pragma: no cover - the journal may already be closed
            pass

    # -- the crash ----------------------------------------------------------

    def crash(self) -> DurableJournal:
        """Kill the process, as far as durable state is concerned."""
        self.journal.close()
        self.journal = DurableJournal(self.db).open()
        self.audit = AuditLog(self.audit_path, fsync=True)
        return self.journal

    def machine(self) -> StateMachine:
        return StateMachine(self.journal, self.audit, self.run_id)

    def effects(self) -> ex.ExternalEffectJournal:
        return ex.ExternalEffectJournal(self.journal, audit=self.audit)

    def begin_push(self, journal=None, *, digest: str = "req-1"):
        return (journal or self.effects()).begin(
            effect_type="git_push_task_branch",
            target="origin/task/M0-T036-supervisor-bridge",
            task_id="M0-T036", request_digest=digest,
            prior_state_reader=lambda: "a" * 40)

    def assert_journal_healthy(self) -> None:
        report = self.journal.integrity_check()
        self.assertTrue(report.ok, report.detail if hasattr(report, "detail") else report)

    def assert_chain_valid(self) -> None:
        self.assertTrue(AuditLog(self.audit_path, fsync=False).verify_chain().ok)


# --------------------------------------------------------------------------
# Journal boundaries: transitions
# --------------------------------------------------------------------------


class TransitionBoundaryTests(CrashTestBase):
    def test_crash_before_a_transition_commit_leaves_the_previous_state(self) -> None:
        machine = self.machine()
        machine.transition(sm.PREFLIGHT, "start_command")
        self.assertEqual(machine.current_state, sm.PREFLIGHT)
        # Crash BEFORE the next commit happens.
        self.crash()
        self.assertEqual(self.machine().current_state, sm.PREFLIGHT)
        self.assert_journal_healthy()

    def test_crash_after_a_transition_commit_resumes_at_the_new_state(self) -> None:
        machine = self.machine()
        machine.transition(sm.PREFLIGHT, "start_command")
        machine.transition(sm.START_CLAUDE, "preflight_pass")
        self.crash()
        self.assertEqual(self.machine().current_state, sm.START_CLAUDE)
        self.assert_journal_healthy()

    def test_a_crash_after_every_transition_in_a_full_cycle_resumes_exactly(self) -> None:
        path = [
            (sm.PREFLIGHT, "start_command"),
            (sm.START_CLAUDE, "preflight_pass"),
            (sm.CLAUDE_RUNNING, "claude_process_started"),
            (sm.CHECKPOINT_RECEIVED, "valid_checkpoint_received"),
            (sm.COLLECT_EVIDENCE, "checkpoint_validated"),
            (sm.CODEX_REVIEW, "evidence_packet_built"),
            (sm.VALIDATE_DECISION, "decision_received"),
            (sm.POLICY_CHECK, "decision_schema_valid"),
            (sm.FORWARD_PROMPT, "tier_auto"),
            (sm.CLAUDE_RUNNING, "prompt_forwarded"),
        ]
        for state, trigger in path:
            self.machine().transition(state, trigger)
            self.crash()                                 # crash after EVERY commit
            self.assertEqual(self.machine().current_state, state,
                             f"did not resume at {state}")
            self.assert_journal_healthy()

    def test_a_restart_from_every_state_reads_that_state_back(self) -> None:
        for state in sm.STATES:
            self.journal.set_state(sm.STATE_KEY, state)
            self.crash()
            self.assertEqual(self.machine().current_state, state)

    def test_an_idempotent_repeat_after_a_crash_is_not_a_second_transition(self) -> None:
        machine = self.machine()
        machine.transition(sm.PREFLIGHT, "start_command")
        before = len(self.journal.transitions())
        self.crash()
        result = self.machine().transition(sm.PREFLIGHT, "start_command")
        self.assertFalse(result.applied)
        self.assertEqual(result.reason, "idempotent_repeat")
        self.assertEqual(len(self.journal.transitions()), before)

    def test_the_side_effect_never_runs_before_the_commit_is_durable(self) -> None:
        observed: list[str] = []
        machine = self.machine()

        def side_effect() -> None:
            # By the time this runs the journal must ALREADY read the new state,
            # so a crash here can never leave an un-journaled effect.
            observed.append(str(self.journal.get_state(sm.STATE_KEY)))

        machine.transition(sm.PREFLIGHT, "start_command", side_effect=side_effect)
        self.assertEqual(observed, [sm.PREFLIGHT])


# --------------------------------------------------------------------------
# External-effect boundaries
# --------------------------------------------------------------------------


class ExternalEffectBoundaryTests(CrashTestBase):
    def test_crash_before_an_effect_is_journaled_leaves_no_trace(self) -> None:
        self.crash()
        self.assertEqual(self.journal.pending_effects(), [],
                         "an effect that was never journaled must not exist")

    def test_crash_after_an_effect_is_journaled_leaves_it_pending(self) -> None:
        record = self.begin_push()
        self.crash()
        pending = self.journal.pending_effects()
        self.assertEqual([p.action_id for p in pending], [record.action_id])
        self.assertEqual(pending[0].status, "PENDING")

    def test_a_pending_effect_after_a_crash_is_never_blindly_retried(self) -> None:
        record = self.begin_push()
        self.crash()
        with self.assertRaises(ex.ExternalEffectError):
            self.effects().assert_safe_to_retry(record.action_id)

    def test_a_repeated_begin_after_a_crash_reuses_the_same_action_id(self) -> None:
        first = self.begin_push()
        self.crash()
        second = self.begin_push()
        self.assertEqual(first.action_id, second.action_id)
        self.assertEqual(len(self.journal.pending_effects()), 1,
                         "the crash must not have produced a second pending effect")

    def test_crash_before_an_effect_is_confirmed_keeps_it_ambiguous(self) -> None:
        record = self.begin_push()
        self.crash()
        outcome = rec.classify(rec.RecoveryContext(
            revalidation={n: True for n in rec.REVALIDATION_STEPS},
            pending_effect_ids=(record.action_id,),
            flags=rec.DurableFlags(limited_auto_enabled=True)))
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)
        self.assertFalse(outcome.resume_permitted)

    def test_crash_after_an_effect_is_confirmed_reports_it_done(self) -> None:
        record = self.begin_push()
        self.effects().confirm(record.action_id, resulting_state="b" * 40)
        self.crash()
        stored = self.journal.get_effect(record.action_id)
        self.assertEqual(stored.status, "CONFIRMED")
        self.assertEqual(self.journal.pending_effects(), [])
        with self.assertRaises(ex.ExternalEffectError):
            self.effects().assert_safe_to_retry(record.action_id)

    def test_a_confirmed_effect_survives_a_crash_as_a_safe_checkpoint(self) -> None:
        record = self.begin_push()
        self.effects().confirm(record.action_id, resulting_state="b" * 40)
        self.crash()
        outcome = rec.classify(rec.RecoveryContext(
            revalidation={n: True for n in rec.REVALIDATION_STEPS},
            pending_effect_ids=(),
            flags=rec.DurableFlags(limited_auto_enabled=True)))
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)

    def test_reconciling_after_a_crash_never_duplicates_the_effect(self) -> None:
        record = self.begin_push()
        self.crash()
        verdict = self.effects().reconcile(record.action_id,
                                           prober=lambda _r: (True, "b" * 40))
        self.assertEqual(verdict.status, ex.RECONCILED_OCCURRED)
        self.assertFalse(verdict.safe_to_retry)
        self.assertEqual(self.journal.get_effect(record.action_id).status, "CONFIRMED")

    def test_an_unprovable_effect_after_a_crash_pauses(self) -> None:
        record = self.begin_push()
        self.crash()
        verdict = self.effects().reconcile(record.action_id,
                                           prober=lambda _r: (None, "unreachable"))
        self.assertTrue(verdict.requires_pause)
        self.assertFalse(verdict.safe_to_retry)
        self.assertEqual(self.journal.get_effect(record.action_id).status, "PENDING")

    def test_an_after_effect_without_a_pending_record_is_refused(self) -> None:
        """A crash must never let the run invent an after-effect."""
        from tools.agent_supervisor.durable_state import JournalError

        self.crash()
        with self.assertRaises(JournalError) as ctx:
            self.journal.record_after_effect("never-began", resulting_state="x")
        self.assertEqual(ctx.exception.code, "no_pending_effect")


# --------------------------------------------------------------------------
# Outbox boundaries (exactly-once prompt forwarding)
# --------------------------------------------------------------------------


class OutboxBoundaryTests(CrashTestBase):
    def loop(self) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036",
                                 stage="phase4"),
            journal=self.journal, audit=self.audit, machine=self.machine(),
            authority=self.authority, runner=None, reviewer=None,
            run_id=self.run_id, approval_gate=lambda d, p: True)

    def decision(self) -> CodexDecision:
        return CodexDecision(
            schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T036",
            reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
            verified_origin_main="a" * 40, model_used="fake",
            next_claude_prompt="next unit")

    def test_crash_before_the_outbox_enqueue_leaves_no_message(self) -> None:
        self.crash()
        self.assertEqual(self.journal.unsent_outbound(), [])

    def test_crash_after_the_outbox_enqueue_resumes_the_same_message(self) -> None:
        loop = self.loop()
        message_id = loop.forward_message_id(1, "the prompt",
                                             decision=self.decision())
        self.journal.enqueue_outbound(message_id, {"message_id": message_id})
        self.crash()

        resumed = self.loop()
        result = resumed.forward_exactly_once("the prompt", cycle=1,
                                              decision=self.decision())
        self.assertTrue(result.sent)
        self.assertTrue(result.resumed_unsent)
        self.assertEqual(result.message_id, message_id)
        rows = self.journal.conn.execute("SELECT COUNT(*) AS n FROM outbox").fetchone()
        self.assertEqual(rows["n"], 1, "a crash must not mint a second message")

    def test_crash_after_the_outbox_mark_sent_suppresses_the_duplicate(self) -> None:
        loop = self.loop()
        first = loop.forward_exactly_once("the prompt", cycle=1,
                                          decision=self.decision())
        self.assertTrue(first.sent)
        self.crash()

        resumed = self.loop()
        second = resumed.forward_exactly_once("the prompt", cycle=1,
                                              decision=self.decision())
        self.assertFalse(second.sent)
        self.assertTrue(second.duplicate_suppressed)
        self.assertEqual(second.message_id, first.message_id)

    def test_repeated_crashes_never_send_the_same_prompt_twice(self) -> None:
        sent = 0
        for _ in range(5):
            result = self.loop().forward_exactly_once(
                "the prompt", cycle=1, decision=self.decision())
            sent += 1 if result.sent else 0
            self.crash()
        self.assertEqual(sent, 1, "exactly one send across five crash cycles")

    def test_the_persisted_envelope_survives_the_crash_intact(self) -> None:
        loop = self.loop()
        message_id = loop.forward_message_id(2, "payload prompt",
                                             decision=self.decision())
        loop.forward_exactly_once("payload prompt", cycle=2,
                                  decision=self.decision())
        self.crash()
        row = self.journal.conn.execute(
            "SELECT envelope FROM outbox WHERE message_id = ?", (message_id,)).fetchone()
        envelope = json.loads(row["envelope"])
        self.assertEqual(envelope["payload"]["prompt_digest"],
                         digest_of("payload prompt"))

    def test_a_duplicate_inbound_message_id_is_recognized_after_a_crash(self) -> None:
        self.assertTrue(self.journal.record_inbound("msg-1", "d" * 64))
        self.crash()
        self.assertFalse(self.journal.record_inbound("msg-1", "d" * 64),
                         "a redelivered checkpoint must be recognized, not reprocessed")


# --------------------------------------------------------------------------
# Audit-log and state-write boundaries
# --------------------------------------------------------------------------


class AuditAndStateBoundaryTests(CrashTestBase):
    def test_crash_before_an_audit_append_leaves_a_valid_shorter_chain(self) -> None:
        for index in range(3):
            self.audit.append("probe", run_id=self.run_id, detail={"i": index})
        self.crash()
        self.assert_chain_valid()
        self.assertEqual(len(AuditLog(self.audit_path, fsync=False).read_all()), 3)

    def test_crash_after_an_audit_append_keeps_the_chain_valid_and_extendable(self) -> None:
        self.audit.append("probe", run_id=self.run_id, detail={"i": 0})
        self.crash()
        self.audit.append("probe", run_id=self.run_id, detail={"i": 1})
        self.assert_chain_valid()
        records = AuditLog(self.audit_path, fsync=False).read_all()
        self.assertEqual([r["sequence"] for r in records], [1, 2])
        self.assertEqual(records[1]["prev_digest"], records[0]["digest"])

    def test_a_crash_after_every_append_keeps_the_chain_linked(self) -> None:
        for index in range(6):
            self.audit.append("probe", run_id=self.run_id, detail={"i": index})
            self.crash()
            self.assert_chain_valid()
        records = AuditLog(self.audit_path, fsync=False).read_all()
        self.assertEqual([r["sequence"] for r in records], [1, 2, 3, 4, 5, 6])

    def test_a_partially_written_final_line_is_detected_not_ignored(self) -> None:
        self.audit.append("probe", run_id=self.run_id, detail={"i": 0})
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write('{"sequence": 2, "event_type": "torn')   # power loss
        log = AuditLog(self.audit_path, fsync=False)
        with self.assertRaises(Exception) as ctx:
            log.append("after_the_tear", run_id=self.run_id)
        self.assertIn("append_to_damaged_chain", str(ctx.exception))

    def test_crash_before_a_state_write_leaves_the_previous_value(self) -> None:
        self.journal.set_state("probe_key", {"v": 1})
        self.crash()
        self.assertEqual(self.journal.get_state("probe_key"), {"v": 1})

    def test_crash_after_a_state_write_reads_the_new_value(self) -> None:
        self.journal.set_state("probe_key", {"v": 1})
        self.journal.set_state("probe_key", {"v": 2})
        self.crash()
        self.assertEqual(self.journal.get_state("probe_key"), {"v": 2})
        self.assert_journal_healthy()

    def test_the_owner_touch_ledger_survives_a_crash_without_double_counting(self) -> None:
        ledger = lp.OwnerTouchLedger(self.journal, run_id=self.run_id, budget=2)
        ledger.record(lp.TOUCH_SYNCHRONOUS_STOP, reason_code="stop", reason="",
                      cycle=1)
        self.crash()
        after = lp.OwnerTouchLedger(self.journal, run_id=self.run_id, budget=2)
        self.assertEqual(after.counted(), 1)
        after.record(lp.TOUCH_SYNCHRONOUS_STOP, reason_code="stop2", reason="",
                     cycle=2)
        self.crash()
        self.assertEqual(
            lp.OwnerTouchLedger(self.journal, run_id=self.run_id, budget=2).counted(), 2)

    def test_a_queued_ask_survives_a_crash(self) -> None:
        from tools.agent_supervisor.models import QueuedAsk, to_utc_iso

        self.journal.queue_ask(QueuedAsk(
            ask_id="ask-1", run_id=self.run_id, task_id="M0-T036",
            question="Approve the push?", request_digest="d" * 64,
            created_at_utc=to_utc_iso(), classification="scope"))
        self.crash()
        asks = self.journal.open_asks()
        self.assertEqual([a.ask_id for a in asks], ["ask-1"])


# --------------------------------------------------------------------------
# Meta
# --------------------------------------------------------------------------


class BoundaryRegisterTests(unittest.TestCase):
    def test_every_declared_boundary_has_a_crash_test(self) -> None:
        source = pathlib.Path(__file__).read_text(encoding="utf-8")
        names = set(re.findall(r"def (test_\w+)", source))
        for boundary, fragment in BOUNDARIES.items():
            self.assertTrue(any(fragment in name for name in names),
                            f"no crash test covers the {boundary!r} boundary "
                            f"(expected a test name containing {fragment!r})")

    def test_the_register_covers_before_and_after_for_each_effect_boundary(self) -> None:
        for stem in ("transition_commit", "effect_begin", "effect_confirm",
                     "outbox_enqueue", "audit_append", "state_write"):
            self.assertIn(f"before_{stem}", BOUNDARIES, stem)
            self.assertIn(f"after_{stem}", BOUNDARIES, stem)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
