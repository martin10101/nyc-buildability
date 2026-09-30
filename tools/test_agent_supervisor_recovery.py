#!/usr/bin/env python3
"""Recovery and locking tests (D-007 Section 15 "recovery and scheduling" + S7 lock).

Covers the recovery half of that family:

* a crash BEFORE and AFTER every journal boundary and every modeled side effect
* SAFE_CHECKPOINT / AMBIGUOUS_EFFECT / UNSAFE_OR_DRIFTED classification
* a verified safe checkpoint does NOT auto-resume unless limited-auto was already
  owner-enabled - and this build never enables it
* ambiguous-effect reconciliation proves via read-only evidence and NEVER
  duplicates a performed effect; unprovable means PAUSED_RECOVERY
* durable emergency-stop and manual-pause flags beat autostart
* recovery restores a usage-limit deadline and contacts nobody
* startup recovery with the exact checkout identity
* stale vs. live lock; a live lock is never stolen; pid reuse is detected
* interrupted-turn resumption only behind a recorded capability probe

Real child processes are this interpreter running a trivial fake script; no
provider is ever involved.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import locking  # noqa: E402
from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DurableJournal,
    checkout_key,
    runtime_dir_for,
)
from tools.agent_supervisor.external_effects import (  # noqa: E402
    RECONCILED_NOT_OCCURRED,
    RECONCILED_OCCURRED,
    RECONCILIATION_IMPOSSIBLE,
    ExternalEffectJournal,
)
from tools.agent_supervisor.resume_scheduler import (  # noqa: E402
    EMERGENCY_STOP_KEY,
    MANUAL_PAUSE_KEY,
    RESUME_NOT_BEFORE_KEY,
)
from tools.agent_supervisor.state_machine import (  # noqa: E402
    PAUSED_RECOVERY,
    PREFLIGHT,
    RECONCILE_EXTERNAL_EFFECT,
    USAGE_LIMIT_WAIT,
)

CONTROLLER = "0.3.0-test"


def all_pass() -> dict:
    return {step: True for step in rec.REVALIDATION_STEPS}


class RecoveryBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runtime = pathlib.Path(self._tmp.name).resolve()
        self.db = self.runtime / "journal.sqlite3"
        self.journal = DurableJournal(self.db).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------


class ClassificationTests(unittest.TestCase):
    def test_a_clean_recovery_is_a_safe_checkpoint(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass()))
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)
        self.assertEqual(outcome.next_state, PREFLIGHT)

    def test_a_safe_checkpoint_does_not_auto_resume_without_prior_limited_auto(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass()))
        self.assertFalse(outcome.resume_permitted)
        self.assertEqual(outcome.reason_code, "safe_no_auto_resume")
        self.assertIn("never enables or broadens limited-auto", outcome.reason)

    def test_a_safe_checkpoint_auto_resumes_only_with_prior_limited_auto(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(
            revalidation=all_pass(),
            flags=rec.DurableFlags(limited_auto_enabled=True)))
        self.assertTrue(outcome.resume_permitted)
        self.assertEqual(outcome.reason_code, "safe_auto_resume")

    def test_a_pending_effect_is_ambiguous(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass(),
                                                   pending_effect_ids=("act-1",)))
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)
        self.assertEqual(outcome.next_state, RECONCILE_EXTERNAL_EFFECT)
        self.assertFalse(outcome.resume_permitted)

    def test_every_failed_revalidation_step_is_drift(self) -> None:
        for step in rec.REVALIDATION_STEPS:
            with self.subTest(step=step):
                results = all_pass()
                results[step] = False
                outcome = rec.classify(rec.RecoveryContext(revalidation=results))
                self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)
                self.assertIn(step, outcome.failed_steps)
                self.assertEqual(outcome.next_state, PAUSED_RECOVERY)

    def test_a_missing_revalidation_step_is_a_failed_step(self) -> None:
        results = all_pass()
        del results["auth"]
        outcome = rec.classify(rec.RecoveryContext(revalidation=results))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)
        self.assertIn("auth", outcome.missing_steps)

    def test_an_unknown_revalidation_step_is_refused(self) -> None:
        results = all_pass()
        results["vibes"] = True
        with self.assertRaises(rec.RecoveryError):
            rec.classify(rec.RecoveryContext(revalidation=results))

    def test_a_competing_writer_is_drift(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(
            revalidation=all_pass(), competing_writer_detected=True,
            competing_writer_detail="a second terminal modified the worktree"))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)

    def test_a_lost_lock_is_drift(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(
            revalidation=all_pass(), lock_acquired=False,
            lock_detail="another instance holds this checkout"))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)

    def test_a_surviving_child_is_drift(self) -> None:
        child = rec.ChildAccount(pid=4242, role="worker", recorded_start_token="",
                                 surviving=True, determined=True, detail="running")
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass(),
                                                   children=(child,)))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)
        self.assertIn(4242, outcome.unaccounted_children)

    def test_an_undeterminable_child_is_drift_not_assumed_gone(self) -> None:
        child = rec.ChildAccount(pid=4242, role="worker", recorded_start_token="",
                                 surviving=False, determined=False,
                                 detail="OpenProcess failed")
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass(),
                                                   children=(child,)))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)

    def test_drift_dominates_an_ambiguous_effect(self) -> None:
        results = all_pass()
        results["auth"] = False
        outcome = rec.classify(rec.RecoveryContext(revalidation=results,
                                                   pending_effect_ids=("act-1",)))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED,
                         "an unsafe finding is never downgraded to merely ambiguous")


class DurableFlagTests(RecoveryBase):
    def test_emergency_stop_beats_autostart(self) -> None:
        self.journal.set_state(EMERGENCY_STOP_KEY, True)
        permitted, why = rec.autostart_permitted(rec.DurableFlags.read(self.journal))
        self.assertFalse(permitted)
        self.assertIn("emergency stop", why)

    def test_manual_pause_beats_autostart(self) -> None:
        self.journal.set_state(MANUAL_PAUSE_KEY, True)
        permitted, _ = rec.autostart_permitted(rec.DurableFlags.read(self.journal))
        self.assertFalse(permitted)

    def test_an_owner_gate_beats_autostart(self) -> None:
        self.journal.set_state(rec.OWNER_GATE_KEY, True)
        permitted, _ = rec.autostart_permitted(rec.DurableFlags.read(self.journal))
        self.assertFalse(permitted)

    def test_a_pending_deadline_beats_autostart(self) -> None:
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "2026-08-03T18:00:00.000Z")
        permitted, _ = rec.autostart_permitted(rec.DurableFlags.read(self.journal))
        self.assertFalse(permitted)

    def test_a_safe_checkpoint_under_a_stop_flag_still_pauses(self) -> None:
        outcome = rec.classify(rec.RecoveryContext(
            revalidation=all_pass(),
            flags=rec.DurableFlags(emergency_stop=True, limited_auto_enabled=True)))
        self.assertEqual(outcome.next_state, PAUSED_RECOVERY)
        self.assertEqual(outcome.reason_code, "safe_but_forbidden")

    def test_an_emergency_stop_is_cleared_only_by_an_owner_command(self) -> None:
        rec.set_emergency_stop(self.journal, reason="test", audit=self.audit)
        with self.assertRaises(rec.RecoveryError) as raised:
            rec.clear_emergency_stop(self.journal, owner_command=False)
        self.assertEqual(raised.exception.code, "stop_requires_owner")
        rec.clear_emergency_stop(self.journal, owner_command=True, audit=self.audit)
        self.assertFalse(rec.DurableFlags.read(self.journal).emergency_stop)

    def test_pause_and_resume_round_trip(self) -> None:
        rec.set_manual_pause(self.journal, paused=True, reason="test", audit=self.audit)
        self.assertTrue(rec.DurableFlags.read(self.journal).manual_pause)
        rec.set_manual_pause(self.journal, paused=False, reason="test", audit=self.audit)
        self.assertFalse(rec.DurableFlags.read(self.journal).manual_pause)


# --------------------------------------------------------------------------
# Crash at every journal boundary
# --------------------------------------------------------------------------


class CrashBoundaryTests(RecoveryBase):
    """Simulate a crash before/after each journal write and each modeled effect."""

    def reopen(self) -> DurableJournal:
        self.journal.close()
        journal = DurableJournal(self.db).open()
        self.addCleanup(journal.close)
        self.journal = journal
        return journal

    def test_crash_before_the_before_effect_record_leaves_nothing_pending(self) -> None:
        journal = self.reopen()
        self.assertEqual(journal.pending_effects(), [])
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass()))
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)

    def test_crash_after_the_before_effect_record_is_ambiguous(self) -> None:
        effects = ExternalEffectJournal(self.journal, audit=self.audit, run_id="r")
        effects.begin(effect_type="github_pr_create", target="pr#1", task_id="T",
                      request_digest="d" * 64,
                      prior_state_reader=lambda: "no pr open for this branch")
        journal = self.reopen()
        pending = [e.action_id for e in journal.pending_effects()]
        self.assertEqual(len(pending), 1)
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass(),
                                                   pending_effect_ids=tuple(pending)))
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)

    def test_crash_after_the_after_effect_record_is_safe(self) -> None:
        effects = ExternalEffectJournal(self.journal, audit=self.audit, run_id="r")
        record = effects.begin(effect_type="github_pr_create", target="pr#1", task_id="T",
                               request_digest="d" * 64,
                               prior_state_reader=lambda: "no pr open for this branch")
        effects.confirm(record.action_id, resulting_state="pr 42 created")
        journal = self.reopen()
        self.assertEqual(journal.pending_effects(), [])
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass()))
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)

    def test_the_state_survives_a_restart_exactly(self) -> None:
        self.journal.record_transition(state_from="IDLE", state_to="PREFLIGHT",
                                       trigger="start_command", run_id="r",
                                       state_updates={"current_state": "PREFLIGHT"})
        journal = self.reopen()
        self.assertEqual(journal.get_state("current_state"), "PREFLIGHT")
        self.assertEqual(journal.last_transition().state_to, "PREFLIGHT")

    # -- M0-T126 (defect D6): unit-dispatch crash-injection replays ---------
    # Three R387 scenario-9 interruption rows. Each leaves an UNRECONCILED
    # dispatch intent at recovery, so the crash-mid-unit is classified
    # AMBIGUOUS_EFFECT (reconcile before re-dispatch), never SAFE (re-dispatch).

    def _classify_after_crash(self):
        journal = self.reopen()
        return rec.recover_boot(journal=journal, lock=None,
                                revalidation=all_pass(), audit=self.audit)

    def test_d6_crash_immediately_after_popen_is_ambiguous(self) -> None:
        rec.record_dispatch_intent(self.journal, run_id="r", cycle=1)
        outcome = self._classify_after_crash()
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)
        self.assertEqual(outcome.reason_code, "unit_dispatch_unreconciled")

    def test_d6_crash_after_partial_stream_is_ambiguous(self) -> None:
        # Partial stream, no checkpoint extracted: the durable signal is the
        # still-pending dispatch intent, which drives AMBIGUOUS.
        rec.record_dispatch_intent(self.journal, run_id="r", cycle=1)
        outcome = self._classify_after_crash()
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)
        self.assertEqual(outcome.reason_code, "unit_dispatch_unreconciled")

    def test_d6_crash_checkpoint_in_stream_before_extract_is_ambiguous(self) -> None:
        # The checkpoint reached the stream but the supervisor crashed before
        # extracting/journaling the outcome: the intent is still pending.
        rec.record_dispatch_intent(self.journal, run_id="r", cycle=2)
        outcome = self._classify_after_crash()
        self.assertEqual(outcome.classification, rec.AMBIGUOUS_EFFECT)
        self.assertEqual(outcome.reason_code, "unit_dispatch_unreconciled")

    def test_d6_reconciled_dispatch_is_not_ambiguous(self) -> None:
        # Removal sensitivity: a unit whose outcome WAS reconciled must classify
        # SAFE, so the AMBIGUOUS branch fires only on an unreconciled crash.
        rec.record_dispatch_intent(self.journal, run_id="r", cycle=1)
        rec.reconcile_dispatch_intent(self.journal)
        outcome = self._classify_after_crash()
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)

    def test_d16_determined_dead_child_is_archived_with_provenance(self) -> None:
        rec.record_launched_child(self.journal, pid=999999, role="worker",
                                  start_token="tok")
        archived = rec.sweep_dead_child_records(self.journal, audit=self.audit)
        self.assertEqual(len(archived), 1)
        self.assertIn("archived_at_utc", archived[0])
        self.assertEqual(self.journal.get_state(rec.CHILD_PROCESSES_KEY, []), [])
        stored = self.journal.get_state(rec.ARCHIVED_DEAD_CHILDREN_KEY, [])
        self.assertEqual(len(stored), 1)


# --------------------------------------------------------------------------
# Reconciliation
# --------------------------------------------------------------------------


class ReconciliationTests(RecoveryBase):
    def setUp(self) -> None:
        super().setUp()
        self.effects = ExternalEffectJournal(self.journal, audit=self.audit, run_id="r")
        self.record = self.effects.begin(
            effect_type="github_pr_create", target="pr#1", task_id="T",
            request_digest="d" * 64,
            prior_state_reader=lambda: "no pr open for this branch")

    def test_read_only_evidence_proving_it_happened_never_reruns(self) -> None:
        reruns: list[str] = []

        def prober(record):  # noqa: ANN001 - test double
            return True, "pr 42 exists"

        verdict = rec.reconcile_effect(self.effects, self.record.action_id, prober=prober)
        self.assertTrue(verdict.resolved)
        self.assertEqual(verdict.status, RECONCILED_OCCURRED)
        self.assertEqual(verdict.next_state, PREFLIGHT)
        self.assertEqual(reruns, [], "a proven effect is never re-performed")

    def test_read_only_evidence_proving_it_did_not_happen_allows_a_retry(self) -> None:
        verdict = rec.reconcile_effect(self.effects, self.record.action_id,
                                       prober=lambda record: (False, "no such pr"))
        self.assertTrue(verdict.resolved)
        self.assertEqual(verdict.status, RECONCILED_NOT_OCCURRED)

    def test_an_unprovable_effect_pauses(self) -> None:
        verdict = rec.reconcile_effect(self.effects, self.record.action_id,
                                       prober=lambda record: (None, "network unreachable"))
        self.assertFalse(verdict.resolved)
        self.assertEqual(verdict.status, RECONCILIATION_IMPOSSIBLE)
        self.assertEqual(verdict.next_state, PAUSED_RECOVERY)
        self.assertEqual(verdict.trigger, "effect_unprovable")

    def test_a_confirmed_effect_is_never_safe_to_retry(self) -> None:
        self.effects.confirm(self.record.action_id, resulting_state="pr 42")
        with self.assertRaises(Exception):
            self.effects.assert_safe_to_retry(self.record.action_id)

    def test_codex_recovery_discards_partial_output(self) -> None:
        plan = rec.codex_recovery_plan()
        self.assertTrue(plan["discard_partial_output"])
        self.assertFalse(plan["resume_partial_review"])


# --------------------------------------------------------------------------
# Interrupted-turn resumption gate
# --------------------------------------------------------------------------


class ResumptionGateTests(RecoveryBase):
    def test_without_a_probe_a_digest_bound_continuation_is_used(self) -> None:
        plan = rec.interrupted_turn_resumption(
            self.journal, session_id="s-1", last_safe_checkpoint_digest="d" * 64)
        self.assertEqual(plan.mode, "digest_bound_continuation")
        self.assertEqual(plan.continuation_digest, "d" * 64)

    def test_a_partial_probe_record_does_not_open_the_gate(self) -> None:
        self.journal.set_state(rec.RESUME_CAPABILITY_KEY,
                               {"proves_no_duplicate_pending_action": True})
        plan = rec.interrupted_turn_resumption(self.journal, session_id="s-1",
                                               last_safe_checkpoint_digest="d")
        self.assertEqual(plan.mode, "digest_bound_continuation")

    def test_a_complete_probe_record_opens_the_gate(self) -> None:
        self.journal.set_state(rec.RESUME_CAPABILITY_KEY, {
            "probe_id": "interrupted-turn-1",
            "proves_no_duplicate_pending_action": True,
            "tested_against_installed_cli": True})
        plan = rec.interrupted_turn_resumption(self.journal, session_id="s-1",
                                               last_safe_checkpoint_digest="d")
        self.assertEqual(plan.mode, "interrupted_turn")
        self.assertEqual(plan.session_id, "s-1")


# --------------------------------------------------------------------------
# The RECOVER_BOOT driver
# --------------------------------------------------------------------------


class RecoverBootTests(RecoveryBase):
    def lock(self) -> locking.SingleInstanceLock:
        return locking.SingleInstanceLock(self.runtime, checkout_key="k" * 64,
                                          controller_version=CONTROLLER)

    def test_a_clean_boot_classifies_safe_and_records_the_outcome(self) -> None:
        outcome = rec.recover_boot(journal=self.journal, lock=self.lock(),
                                   revalidation=all_pass(), audit=self.audit)
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)
        self.assertEqual(rec.last_outcome(self.journal)["classification"],
                         rec.SAFE_CHECKPOINT)

    def test_recovery_writes_exactly_one_audit_event(self) -> None:
        before = self.audit.head_sequence
        rec.recover_boot(journal=self.journal, lock=self.lock(),
                         revalidation=all_pass(), audit=self.audit)
        self.assertEqual(self.audit.head_sequence, before + 1)

    def test_a_restored_deadline_overrides_a_safe_resume(self) -> None:
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "2026-08-03T18:00:00.000Z")
        outcome = rec.recover_boot(journal=self.journal, lock=self.lock(),
                                   revalidation=all_pass(), audit=self.audit)
        self.assertEqual(outcome.next_state, USAGE_LIMIT_WAIT)
        self.assertEqual(outcome.trigger, "recovery_restores_deadline")
        self.assertFalse(outcome.resume_permitted)

    def test_a_held_lock_makes_recovery_unsafe(self) -> None:
        holder = self.lock()
        holder.acquire()
        self.addCleanup(holder.release)
        contender = locking.SingleInstanceLock(self.runtime, checkout_key="k" * 64,
                                                controller_version=CONTROLLER,
                                                pid=os.getpid() + 100000)
        outcome = rec.recover_boot(journal=self.journal, lock=contender,
                                   revalidation=all_pass(), audit=self.audit)
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)

    def test_recovery_contacts_no_provider(self) -> None:
        """Structural: the module imports no subprocess and no network module."""
        source = (REPO / "tools" / "agent_supervisor" / "recovery.py").read_text(
            encoding="utf-8")
        for forbidden in ("import subprocess", "import socket", "import urllib",
                          "import http"):
            self.assertNotIn(forbidden, source)


class ChildAccountingTests(RecoveryBase):
    def test_a_dead_child_is_accounted_for(self) -> None:
        script = self.runtime / "fake_child.py"
        script.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        process = subprocess.run([sys.executable, str(script)], capture_output=True,
                                 shell=False)
        self.assertEqual(process.returncode, 0)
        rec.record_launched_child(self.journal, pid=999999, role="worker")
        accounts = rec.account_for_children(self.journal)
        self.assertEqual(len(accounts), 1)
        self.assertFalse(accounts[0].surviving)

    def test_a_live_child_is_detected_as_surviving(self) -> None:
        script = self.runtime / "sleeper.py"
        script.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        process = subprocess.Popen([sys.executable, str(script)], shell=False,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def stop() -> None:
            process.kill()
            process.wait(timeout=10)

        self.addCleanup(stop)
        rec.record_launched_child(self.journal, pid=process.pid, role="worker",
                                  start_token=locking.process_start_token(process.pid))
        accounts = rec.account_for_children(self.journal)
        self.assertTrue(accounts[0].surviving)
        outcome = rec.classify(rec.RecoveryContext(revalidation=all_pass(),
                                                   children=accounts))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)

    def test_a_reused_pid_is_not_treated_as_the_original_child(self) -> None:
        rec.record_launched_child(self.journal, pid=os.getpid(), role="worker",
                                  start_token="deadbeefdeadbeef")
        accounts = rec.account_for_children(self.journal)
        self.assertFalse(accounts[0].surviving,
                         "a live pid with a different creation token is a REUSED pid")

    def test_clearing_the_record_empties_it(self) -> None:
        rec.record_launched_child(self.journal, pid=1, role="worker")
        rec.clear_child_record(self.journal, pid=1, start_token="")
        self.assertEqual(rec.account_for_children(self.journal), ())

    def _recorded_pids(self) -> list[int]:
        recorded = self.journal.get_state(rec.CHILD_PROCESSES_KEY, []) or []
        return [int(e.get("pid", 0) or 0) for e in recorded]

    def test_p2_sc1_settling_one_child_leaves_a_second_recorded_child(self) -> None:
        """P2-SC1: clearing one child does NOT wipe a second recorded child.

        The pre-M0-T059 whole-key wipe would fail OPEN here: one worker's clean
        exit would erase a live successor's record (D-010-R347).
        """
        rec.record_launched_child(self.journal, pid=101, role="worker",
                                  start_token="tokA")
        rec.record_launched_child(self.journal, pid=202, role="worker",
                                  start_token="tokB")

        rec.clear_child_record(self.journal, pid=101, start_token="tokA")

        self.assertEqual(self._recorded_pids(), [202],
                         "only the settled child is cleared; the other survives")

    def test_p2_sc2_settling_an_unrecorded_pid_is_a_no_op(self) -> None:
        """P2-SC2: clearing a pid that was never recorded touches nothing."""
        rec.record_launched_child(self.journal, pid=303, role="worker",
                                  start_token="tokC")

        rec.clear_child_record(self.journal, pid=999, start_token="tokX")

        self.assertEqual(self._recorded_pids(), [303],
                         "an unrecorded pid leaves every recorded child intact")

    def test_p2_sc3_a_reused_pid_with_a_different_start_token_is_not_cleared(self) -> None:
        """P2-SC3: start_token disambiguates a reused pid.

        A record for pid P under token B must NOT be cleared by a settle that
        recorded pid P under token A - they are different processes.
        """
        rec.record_launched_child(self.journal, pid=404, role="worker",
                                  start_token="tokB")

        rec.clear_child_record(self.journal, pid=404, start_token="tokA")

        self.assertEqual(self._recorded_pids(), [404],
                         "a differing start_token means a reused pid, left untouched")


# --------------------------------------------------------------------------
# Single-instance locking (S7)
# --------------------------------------------------------------------------


class LockingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runtime = pathlib.Path(self._tmp.name).resolve()

    def lock(self, pid: int | None = None) -> locking.SingleInstanceLock:
        return locking.SingleInstanceLock(self.runtime, checkout_key="k" * 64,
                                          controller_version=CONTROLLER, pid=pid)

    def test_acquire_and_release(self) -> None:
        lock = self.lock()
        record = lock.acquire()
        self.assertEqual(record.pid, os.getpid())
        self.assertTrue((self.runtime / locking.LOCK_FILENAME).exists())
        self.assertTrue(lock.release())
        self.assertFalse((self.runtime / locking.LOCK_FILENAME).exists())

    def test_a_live_lock_is_never_stolen(self) -> None:
        holder = self.lock()
        holder.acquire()
        self.addCleanup(holder.release)
        contender = self.lock(pid=os.getpid() + 100000)
        with self.assertRaises(locking.LockError) as raised:
            contender.acquire()
        self.assertEqual(raised.exception.code, "lock_held")

    def test_a_stale_lock_is_taken_over(self) -> None:
        stale = locking.LockRecord(pid=999999, start_token="", checkout_key="k" * 64,
                                   controller_version=CONTROLLER,
                                   acquired_at_utc="2026-01-01T00:00:00.000Z",
                                   lock_id="old")
        (self.runtime / locking.LOCK_FILENAME).write_text(
            json.dumps(stale.to_dict()), encoding="utf-8")
        lock = self.lock()
        record = lock.acquire()
        self.addCleanup(lock.release)
        self.assertEqual(record.pid, os.getpid())
        self.assertIsNotNone(lock.took_over_stale)
        self.assertEqual(lock.took_over_stale.code, "owner_gone")

    def test_pid_reuse_is_detected_as_stale(self) -> None:
        record = locking.LockRecord(pid=os.getpid(), start_token="0" * 16,
                                    checkout_key="k", controller_version=CONTROLLER,
                                    acquired_at_utc="", lock_id="x")
        verdict = locking.assess(record)
        self.assertTrue(verdict.stale)
        self.assertEqual(verdict.code, "pid_reused")

    def test_a_live_owner_is_reported_live(self) -> None:
        token = locking.process_start_token(os.getpid())
        record = locking.LockRecord(pid=os.getpid(), start_token=token, checkout_key="k",
                                    controller_version=CONTROLLER, acquired_at_utc="",
                                    lock_id="x")
        self.assertFalse(locking.assess(record).stale)

    def test_liveness_probing_never_signals_the_process(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" / "locking.py").read_text(
            encoding="utf-8")
        self.assertNotIn("os.kill(pid, 0)\n", source.split("if os.name")[0],
                         "os.kill must never be the Windows probe: CPython implements it "
                         "with TerminateProcess")
        probe = locking.probe_process(os.getpid())
        self.assertTrue(probe.determined and probe.alive)
        self.assertTrue(time.monotonic() > 0)  # the process is obviously still alive

    def test_an_unknown_pid_is_a_determined_negative(self) -> None:
        probe = locking.probe_process(999999)
        self.assertTrue(probe.determined)
        self.assertFalse(probe.alive)

    def test_an_invalid_pid_is_refused(self) -> None:
        self.assertFalse(locking.probe_process(0).alive)
        self.assertFalse(locking.probe_process(-5).alive)

    def test_release_never_removes_another_holder_lock(self) -> None:
        holder = self.lock()
        holder.acquire()
        self.addCleanup(holder.release)
        other = self.lock(pid=os.getpid() + 100000)
        self.assertFalse(other.release())
        self.assertTrue((self.runtime / locking.LOCK_FILENAME).exists())

    def test_a_malformed_lock_file_is_refused_not_overwritten(self) -> None:
        (self.runtime / locking.LOCK_FILENAME).write_text("not json", encoding="utf-8")
        with self.assertRaises(locking.LockError) as raised:
            self.lock().acquire()
        self.assertEqual(raised.exception.code, "malformed_lock")

    def test_reacquiring_our_own_lock_is_idempotent(self) -> None:
        lock = self.lock()
        first = lock.acquire()
        second = lock.acquire()
        self.addCleanup(lock.release)
        self.assertEqual(first.lock_id, second.lock_id)

    def test_the_lock_is_keyed_to_the_checkout_runtime_directory(self) -> None:
        """Two checkouts get different runtime dirs, so they never contend."""
        base = self.runtime / "base"
        one = self.runtime / "checkout-one"
        two = self.runtime / "checkout-two"
        one.mkdir()
        two.mkdir()
        self.assertNotEqual(runtime_dir_for(one, base=base), runtime_dir_for(two, base=base))
        self.assertNotEqual(checkout_key(one), checkout_key(two))

    def test_the_context_manager_releases(self) -> None:
        with self.lock() as lock:
            self.assertTrue((self.runtime / locking.LOCK_FILENAME).exists())
            self.assertIsNotNone(lock.record)
        self.assertFalse((self.runtime / locking.LOCK_FILENAME).exists())

    def test_held_by_other_reports_a_live_foreign_holder(self) -> None:
        holder = self.lock()
        holder.acquire()
        self.addCleanup(holder.release)
        contender = self.lock(pid=os.getpid() + 100000)
        self.assertIsNotNone(contender.held_by_other())

    def test_the_lock_file_records_no_secret_or_user_path(self) -> None:
        lock = self.lock()
        lock.acquire()
        self.addCleanup(lock.release)
        content = (self.runtime / locking.LOCK_FILENAME).read_text(encoding="utf-8")
        data = json.loads(content)
        self.assertEqual(set(data), {"pid", "start_token", "checkout_key",
                                     "controller_version", "acquired_at_utc", "lock_id"})


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
