#!/usr/bin/env python3
"""Removal-sensitive tests for D9 next-task machinery and R388 advancement.

M0-T126 (D-024-R372; M0-T125 defect D9). R387 scenarios 8 (exactly-once task
advancement) and 10 (next-task selection + dispatch), and R388 (several
consecutive simulated bounded advancements with no human intervention, no
duplicate or lost work, no false acceptance). Exercises the REAL durable
journal's single-winner compare_and_swap primitive in a temp runtime dir, so
the exactly-once guarantee is proven against the real store, including across a
simulated crash/restart at the advancement boundary.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.agent_supervisor import next_task as nt  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.state_machine import COMPLETE, IDLE, PREFLIGHT  # noqa: E402


class _JournalCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._handles: list[DurableJournal] = []
        # Close every open journal handle BEFORE the temp dir is removed, so
        # Windows can delete the sqlite file (an open handle blocks deletion).
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._close_all)
        self.db = pathlib.Path(self._tmp.name) / "j.sqlite3"
        self.journal = self._track(DurableJournal(self.db).open())

    def _track(self, journal: DurableJournal) -> DurableJournal:
        self._handles.append(journal)
        return journal

    def _close_all(self) -> None:
        for journal in self._handles:
            try:
                journal.close()
            except Exception:
                pass

    def reopen(self) -> DurableJournal:
        """Simulate a crash/restart: a fresh journal handle on the same file.

        The prior handle is closed first, mirroring a process exit before the
        restart re-opens the same durable file.
        """
        self._close_all()
        self._handles.clear()
        return self._track(DurableJournal(self.db).open())


class CloseRunTests(_JournalCase):
    def test_complete_plans_run_closed_to_idle(self) -> None:
        plan = nt.plan_close_run(COMPLETE)
        self.assertTrue(plan.should_close)
        self.assertEqual(plan.trigger, nt.RUN_CLOSED_TRIGGER)
        self.assertEqual(plan.to_state, IDLE)

    def test_non_complete_state_is_not_closed(self) -> None:
        for state in (IDLE, PREFLIGHT, "CLAUDE_RUNNING"):
            with self.subTest(state=state):
                self.assertFalse(nt.plan_close_run(state).should_close)

    def test_close_after_complete_is_idempotent_alias(self) -> None:
        self.assertTrue(nt.close_after_complete(COMPLETE).should_close)
        self.assertFalse(nt.close_after_complete(IDLE).should_close)


class ExactlyOnceAdvancementTests(_JournalCase):
    def _advance(self, journal, task="M0-T107", cid="ckpt-1"):
        return nt.record_advancement(
            journal, task_id=task, run_id="run_x", checkpoint_id=cid,
            from_state=COMPLETE, evidence_refs=("report.md",))

    def test_first_advancement_is_newly_recorded(self) -> None:
        rec = self._advance(self.journal)
        self.assertTrue(rec.newly_recorded)
        self.assertTrue(nt.is_advanced(self.journal, "M0-T107"))

    def test_duplicate_advancement_in_same_process_is_noop(self) -> None:
        first = self._advance(self.journal)
        second = self._advance(self.journal)
        self.assertTrue(first.newly_recorded)
        self.assertFalse(second.newly_recorded)
        self.assertEqual(second.checkpoint_id, first.checkpoint_id)

    def test_advancement_survives_a_crash_restart_without_doubling(self) -> None:
        # Advance, then re-open the journal (a crash/restart) and re-attempt: the
        # exactly-once record persists, so the restart does NOT double-advance.
        first = self._advance(self.journal)
        self.assertTrue(first.newly_recorded)
        restarted = self.reopen()
        again = self._advance(restarted)
        self.assertFalse(again.newly_recorded)
        self.assertEqual(again.run_id, "run_x")

    def test_contradictory_later_output_never_re_advances(self) -> None:
        # A different checkpoint claiming the same task advanced loses the CAS and
        # is surfaced as the STORED fact, never a second advancement (no false
        # acceptance of injected/duplicate provider output).
        first = self._advance(self.journal, cid="ckpt-real")
        rogue = self._advance(self.journal, cid="ckpt-injected")
        self.assertFalse(rogue.newly_recorded)
        self.assertEqual(rogue.checkpoint_id, first.checkpoint_id)
        self.assertEqual(rogue.checkpoint_id, "ckpt-real")

    def test_advancement_requires_a_checkpoint_id(self) -> None:
        with self.assertRaises(nt.NextTaskError):
            nt.record_advancement(
                self.journal, task_id="T", run_id="r", checkpoint_id="",
                from_state=COMPLETE)


class SelectionTests(_JournalCase):
    def _packets(self):
        return [nt.TaskPacketRef("A", "a.json"),
                nt.TaskPacketRef("B", "b.json"),
                nt.TaskPacketRef("C", "c.json")]

    def test_selects_first_unadvanced(self) -> None:
        sel = nt.select_next_packet(self.journal, self._packets())
        self.assertIsNotNone(sel.selected)
        self.assertEqual(sel.selected.task_id, "A")

    def test_skips_advanced_and_picks_next(self) -> None:
        nt.record_advancement(self.journal, task_id="A", run_id="r",
                              checkpoint_id="c", from_state=COMPLETE)
        sel = nt.select_next_packet(self.journal, self._packets())
        self.assertEqual(sel.selected.task_id, "B")
        self.assertIn("A", sel.skipped_advanced)

    def test_exhausted_list_returns_no_eligible_work(self) -> None:
        for tid in ("A", "B", "C"):
            nt.record_advancement(self.journal, task_id=tid, run_id="r",
                                  checkpoint_id="c", from_state=COMPLETE)
        sel = nt.select_next_packet(self.journal, self._packets())
        self.assertIsNone(sel.selected)
        self.assertIn("NO_ELIGIBLE_WORK", sel.reason)

    def test_empty_list_is_no_eligible_work(self) -> None:
        self.assertIsNone(nt.select_next_packet(self.journal, []).selected)

    def test_duplicate_packet_id_is_refused(self) -> None:
        with self.assertRaises(nt.NextTaskError):
            nt.select_next_packet(
                self.journal,
                [nt.TaskPacketRef("A", "a.json"), nt.TaskPacketRef("A", "a2.json")])


class ConsecutiveAdvancementTests(_JournalCase):
    """R388: several consecutive simulated bounded advancements, no human touch."""

    def _packets(self):
        return [nt.TaskPacketRef(f"M0-T{n}", f"{n}.json") for n in (200, 201, 202)]

    def test_three_consecutive_advancements_exactly_once_each(self) -> None:
        packets = self._packets()
        advanced_order = []
        selected = packets[0]
        cycles = 0
        while selected is not None and cycles < 10:
            cycles += 1
            result = nt.advance_and_select(
                self.journal, completed_task_id=selected.task_id,
                run_id=f"run_{selected.task_id}", checkpoint_id=f"ckpt_{selected.task_id}",
                from_state=COMPLETE, ordered_packets=packets)
            self.assertTrue(result.advancement.newly_recorded,
                            f"{selected.task_id} should advance exactly once")
            advanced_order.append(selected.task_id)
            selected = result.next_selection.selected
        self.assertEqual(advanced_order, ["M0-T200", "M0-T201", "M0-T202"])
        # No duplicate, no lost: each advanced once, and the run is now exhausted.
        for tid in ("M0-T200", "M0-T201", "M0-T202"):
            self.assertTrue(nt.is_advanced(self.journal, tid))

    def test_crash_AFTER_campaign_advancement_is_exactly_once(self) -> None:
        # G4 correction 3 (interruption AFTER campaign advancement): advance A,
        # then CRASH before selection/dispatch. On restart, re-running
        # advance_and_select for A must NOT re-advance A and must select B.
        packets = self._packets()
        first = nt.advance_and_select(
            self.journal, completed_task_id="M0-T200", run_id="r",
            checkpoint_id="c", from_state=COMPLETE, ordered_packets=packets)
        self.assertTrue(first.advancement.newly_recorded)
        restarted = self.reopen()
        replay = nt.advance_and_select(
            restarted, completed_task_id="M0-T200", run_id="r",
            checkpoint_id="c", from_state=COMPLETE, ordered_packets=packets)
        self.assertFalse(replay.advancement.newly_recorded,
                         "the crash-replay must not double-advance A")
        self.assertEqual(replay.next_selection.selected.task_id, "M0-T201")

    def test_crash_BEFORE_campaign_advancement_loses_no_work(self) -> None:
        # G4 correction 3 (interruption BEFORE campaign advancement): the
        # supervisor crashes before record_advancement runs. On restart the
        # advancement runs (newly_recorded True) - the work is NOT lost, and it is
        # still recorded exactly once thereafter.
        self.assertFalse(nt.is_advanced(self.journal, "M0-T200"))
        restarted = self.reopen()  # crash before any advancement
        result = nt.advance_and_select(
            restarted, completed_task_id="M0-T200", run_id="r",
            checkpoint_id="c", from_state=COMPLETE, ordered_packets=self._packets())
        self.assertTrue(result.advancement.newly_recorded)
        self.assertEqual(result.next_selection.selected.task_id, "M0-T201")

    def test_crash_BEFORE_verdict_persistence_re_obtains_no_double_advance(self) -> None:
        # G4 correction 3 (interruption BEFORE verdict persistence): the reviewed
        # checkpoint id (the verdict binding) is not yet persisted in an
        # advancement record. On restart, advancing with the re-obtained verdict
        # records it once.
        restarted = self.reopen()
        rec = nt.record_advancement(
            restarted, task_id="M0-T200", run_id="r", checkpoint_id="verdict-ckpt",
            from_state=COMPLETE)
        self.assertTrue(rec.newly_recorded)
        self.assertEqual(rec.checkpoint_id, "verdict-ckpt")

    def test_crash_AFTER_verdict_persistence_never_re_advances(self) -> None:
        # G4 correction 3 (interruption AFTER verdict persistence): the advancement
        # record (carrying the reviewed checkpoint id) is durable. A restart that
        # re-attempts returns the STORED verdict binding, never a second advance -
        # even if a later re-decision carries a different (stale) checkpoint id.
        nt.record_advancement(self.journal, task_id="M0-T200", run_id="r",
                              checkpoint_id="verdict-ckpt", from_state=COMPLETE)
        restarted = self.reopen()
        replay = nt.record_advancement(
            restarted, task_id="M0-T200", run_id="r",
            checkpoint_id="stale-different-ckpt", from_state=COMPLETE)
        self.assertFalse(replay.newly_recorded)
        self.assertEqual(replay.checkpoint_id, "verdict-ckpt")


if __name__ == "__main__":
    unittest.main()
