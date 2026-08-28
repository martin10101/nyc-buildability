#!/usr/bin/env python3
"""Unit F: controller state machine, safe seams, exact-once succession, outage
handling — the D-024 section-16.3 matrix (M0-T092; scenario pack S1–S15 in
`project-control/reports/M0-T092-controller-succession.md` §1).

Stdlib `unittest` only (thin-client / CI safe). No network, no provider calls,
no credentials, no sleeps: every clock is an injected POSIX-seconds value and
every rng is an injected callable. Runtime state goes to temp directories only.

Matrix coverage (one test class per scenario, S-ids in class names):
  S1  section-3 state set mapped onto the extended machine (R029)
  S2  renewable epoch lease — renew or expire, never fork (R028)
  S3  idempotent journaled transitions / restart no-duplicate (R030)
  S4  stop-intent precedence survives restart (R026/R027)
  S5  three interruption classes handled separately (R031)
  S6  safe-seam detection + handoff validation (R066/R067, section 7)
  S7  exact-once lease race — exactly one winner (R028/R030)
  S8  crash-window reconciliation (R030/R031)
  S9  host-restart auto-resume / truthful activation blocker (R032)
  S10 Codex transport preflight fail-closed (R024/R025)
  S11 outage backoff vs blocked vs bounded idle (R033)
  S12 Bootstrap Gate 0 recovery for a new session (R125–R128)
  S13 one active backend + native-resume-is-not-a-seam (R160/R180)
  S14 no worker-visible token pressure (R045)
  S15 telemetry honesty — labelled usage, unknown never zero (R042)

Supervisor-freeze qualifying evidence: D-024-R102.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import bootstrap_gate  # noqa: E402
from tools.agent_supervisor import child_handoff  # noqa: E402
from tools.agent_supervisor import epoch_lease  # noqa: E402
from tools.agent_supervisor import outage_policy  # noqa: E402
from tools.agent_supervisor import recovery  # noqa: E402
from tools.agent_supervisor import rotation  # noqa: E402
from tools.agent_supervisor import runtime_backend  # noqa: E402
from tools.agent_supervisor import session_continuity  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor import stop_intent  # noqa: E402
from tools.agent_supervisor import turnover_seam  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.codex_reviewer import (  # noqa: E402
    ReviewError,
    validate_decision,
)
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.native_runtime import NativeCapabilities  # noqa: E402
from tools.agent_supervisor.protocol import CapabilityManifest  # noqa: E402
from tools.agent_supervisor.resume_scheduler import (  # noqa: E402
    LauncherSpec,
    build_autostart_plan,
    verify_installed_definition,
)
from tools.agent_supervisor.runtime_health import LANDING_DIRECTION_TEXT  # noqa: E402
from tools.agent_supervisor.subagent_contracts import (  # noqa: E402
    ContractError,
    assert_worker_text_clean,
)
from tools.agent_supervisor.telemetry_records import (  # noqa: E402
    Measurement,
    TelemetryRecordError,
)


class JournalCase(unittest.TestCase):
    """Shared temp-journal plumbing. Every test gets a fresh journal file."""

    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="unitf_"))
        self.db = self.tmp / "journal.sqlite3"
        self.journal = DurableJournal(self.db).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)

    def reopen(self) -> None:
        """Simulate a crash/restart: drop the process state, reread the disk."""
        self.journal.close()
        self.journal = DurableJournal(self.db).open()

    def machine(self, run_id: str = "run-1") -> sm.StateMachine:
        return sm.StateMachine(self.journal, self.audit, run_id)


# ---------------------------------------------------------------------------
# S1 — section-3 state set (R029)
# ---------------------------------------------------------------------------


class S1SectionThreeStateSet(JournalCase):
    """Every R029 distinction maps to a state or a documented durable
    composite; illegal transitions raise; the additions are well-formed."""

    #: R029 distinction -> the discriminator in the extended machine. A tuple
    #: entry names a STATE; a string names the durable composite that carries
    #: the distinction (proof detail: M0-T092 report §4).
    MAPPING = {
        "stopped/inactive": (sm.IDLE,),
        "starting-reconciling": (sm.RECOVER_BOOT,),
        "orienting": (sm.START_FRESH_SESSION,),
        "selecting/dispatching": (sm.POLICY_CHECK, sm.FORWARD_PROMPT),
        "producer running": (sm.CLAUDE_RUNNING,),
        "landing": (sm.ROTATION_PENDING, sm.PREPARE_ROTATION),
        "awaiting/reconciling child work": (sm.AWAIT_CHILDREN,),
        "reviewing": (sm.CODEX_REVIEW, sm.VALIDATE_DECISION),
        "correcting": "composite: POLICY_CHECK/FORWARD_PROMPT with the "
                      "journaled REVISE decision (codex_reviewer "
                      "REQUIRED_BY_DECISION['REVISE'])",
        "checkpointing": (sm.CHECKPOINT_RECEIVED, sm.COLLECT_EVIDENCE),
        "primary-session rotation": (sm.PREPARE_ROTATION, sm.VERIFY_HANDOFF,
                                     sm.START_FRESH_SESSION),
        "temporary lower-model bridge": "composite: CLAUDE_RUNNING with the "
                                        "durable orchestrator-role switch "
                                        "(loop.effective_model journal record)",
        "paused": (sm.PAUSED_RECOVERY,),
        "graceful stopping": (sm.GRACEFUL_STOPPING,),
        "emergency stopped": (sm.EMERGENCY_STOPPED,),
        "recovery/reconciliation": (sm.RECOVER_BOOT,
                                    sm.RECONCILE_EXTERNAL_EFFECT),
        "blocked": (sm.WAIT_FOR_OWNER, sm.HALTED),
        "idle because no eligible authorized task exists": (sm.NO_ELIGIBLE_WORK,),
    }

    def test_every_r029_distinction_is_mapped(self) -> None:
        self.assertEqual(len(self.MAPPING), 18)
        for distinction, target in self.MAPPING.items():
            with self.subTest(distinction=distinction):
                if isinstance(target, tuple):
                    for state in target:
                        self.assertIn(state, sm.STATES)
                else:
                    self.assertIn("composite:", target)

    def test_the_four_unit_f_states_exist_and_are_not_blocking_or_terminal(self) -> None:
        for state in (sm.GRACEFUL_STOPPING, sm.AWAIT_CHILDREN,
                      sm.CODEX_OUTAGE_BACKOFF, sm.NO_ELIGIBLE_WORK):
            self.assertIn(state, sm.STATES)
            self.assertNotIn(state, sm.BLOCKING_STATES)
            self.assertNotIn(state, sm.TERMINAL_STATES)
        # 27 at unit F; +2 unit-H1 Phase-E states (GUARDRAIL_BRIDGE,
        # REPRESENT_FABLE) — M0-T093, D-024-R070/R071/R103; covered in
        # tools/test_agent_supervisor_guardrail_bridge.py.
        self.assertEqual(len(sm.STATES), 29)

    def test_every_new_edge_is_walkable_and_documented(self) -> None:
        new_states = {sm.GRACEFUL_STOPPING, sm.AWAIT_CHILDREN,
                      sm.CODEX_OUTAGE_BACKOFF, sm.NO_ELIGIBLE_WORK}
        edges = [t for t in sm.TRANSITIONS
                 if t.state_from in new_states or t.state_to in new_states]
        self.assertGreaterEqual(len(edges), 16)
        for transition in edges:
            with self.subTest(edge=f"{transition.state_from}->{transition.state_to}"):
                self.assertTrue(transition.doc.strip())
                self.journal.set_state(sm.STATE_KEY, transition.state_from)
                self.journal.set_state(sm.LAST_TRIGGER_KEY, "")
                result = self.machine().transition(transition.state_to,
                                                   transition.trigger)
                self.assertTrue(result.applied)

    def test_every_new_state_has_an_exit_edge(self) -> None:
        for state in (sm.GRACEFUL_STOPPING, sm.AWAIT_CHILDREN,
                      sm.CODEX_OUTAGE_BACKOFF, sm.NO_ELIGIBLE_WORK):
            self.assertTrue(sm.legal_targets(state),
                            f"{state} would strand the journal with no exit")

    def test_illegal_transitions_into_the_new_states_raise(self) -> None:
        # IDLE may not jump straight into a landing, drain, backoff, or idle.
        for state in (sm.GRACEFUL_STOPPING, sm.AWAIT_CHILDREN,
                      sm.CODEX_OUTAGE_BACKOFF, sm.NO_ELIGIBLE_WORK):
            with self.subTest(state=state):
                with self.assertRaises(sm.IllegalTransitionError):
                    self.machine().transition(state, "owner_emergency_stop")


# ---------------------------------------------------------------------------
# S2 — renewable epoch lease (R028)
# ---------------------------------------------------------------------------


class S2RenewableEpochLease(JournalCase):
    def test_epochs_advance_as_a_renewable_bounded_sequence(self) -> None:
        lease = epoch_lease.acquire_first(
            self.journal, campaign_id="d024", owner_run_id="run-a",
            now=1000.0, ttl_seconds=100.0, audit=self.audit)
        self.assertEqual(lease.epoch, 1)
        renewed = epoch_lease.renew(self.journal, owner_run_id="run-a",
                                    now=1050.0)
        self.assertEqual(renewed.renew_by_epoch_seconds, 1150.0)
        # expiry, then succession -> epoch 2: a bounded sequence, not an
        # immortal process.
        successor = epoch_lease.succeed(
            self.journal, expected_epoch=1, new_owner_run_id="run-b",
            now=1200.0, ttl_seconds=100.0)
        self.assertEqual(successor.epoch, 2)
        self.assertEqual(successor.owner_run_id, "run-b")

    def test_one_active_lease_at_a_time_never_forks(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                      owner_run_id="run-b", now=1.0,
                                      ttl_seconds=100.0)
        self.assertEqual(ctx.exception.code, "lease_exists")

    def test_a_live_controller_is_never_taken_over(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.succeed(self.journal, expected_epoch=1,
                                new_owner_run_id="run-b", now=50.0,
                                ttl_seconds=100.0)
        self.assertEqual(ctx.exception.code, "predecessor_live")
        current = epoch_lease.current_lease(self.journal)
        self.assertEqual((current.epoch, current.owner_run_id), (1, "run-a"))

    def test_a_lease_renews_or_expires_never_revives(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.renew(self.journal, owner_run_id="run-a", now=50.0)
        self.assertEqual(ctx.exception.code, "lease_expired")

    def test_only_the_owner_renews_or_releases(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        for op in (lambda: epoch_lease.renew(self.journal,
                                             owner_run_id="run-x", now=1.0),
                   lambda: epoch_lease.release(self.journal,
                                               owner_run_id="run-x")):
            with self.assertRaises(epoch_lease.LeaseError) as ctx:
                op()
            self.assertEqual(ctx.exception.code, "not_owner")

    def test_unbounded_ttl_is_refused(self) -> None:
        with self.assertRaises(epoch_lease.LeaseError):
            epoch_lease.EpochLease(campaign_id="c", epoch=1,
                                   owner_run_id="r", ttl_seconds=0,
                                   renew_by_epoch_seconds=0.0,
                                   acquired_at_utc="")

    def test_expiry_boundary_is_strictly_after_the_deadline(self) -> None:
        # M0-T092 correction F3 (G4 LOW-1): pin the boundary semantic. The
        # renew-by instant itself is still owned (expired means now is
        # STRICTLY past renew_by); one tick later the lease is expired.
        lease = epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                          owner_run_id="run-a", now=100.0,
                                          ttl_seconds=50.0)
        self.assertFalse(lease.expired(now=150.0))
        self.assertTrue(lease.live(now=150.0))
        self.assertTrue(lease.expired(now=150.000001))
        renewed = epoch_lease.renew(self.journal, owner_run_id="run-a",
                                    now=150.0)
        self.assertEqual(renewed.renew_by_epoch_seconds, 200.0)

    def test_release_is_idempotent(self) -> None:
        # M0-T092 correction F3 (G4 LOW-2): releasing twice is a no-op.
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        first = epoch_lease.release(self.journal, owner_run_id="run-a")
        second = epoch_lease.release(self.journal, owner_run_id="run-a")
        self.assertTrue(first.released and second.released)
        self.assertEqual(first, second)

    def test_epoch_one_is_taken_at_most_once_even_after_release(self) -> None:
        # M0-T092 correction F4 (G4 ADVISORY-3): a released (or expired)
        # record still refuses acquire_first — later epochs go through
        # succeed() so the sequence stays gapless.
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                      owner_run_id="run-b", now=20.0,
                                      ttl_seconds=10.0)
        self.assertEqual(ctx.exception.code, "lease_exists")


# ---------------------------------------------------------------------------
# S3 — idempotent journaled transitions (R030)
# ---------------------------------------------------------------------------


class S3IdempotentJournaledTransitions(JournalCase):
    def test_a_replayed_transition_is_a_noop_not_a_repeat(self) -> None:
        machine = self.machine()
        machine.transition(sm.PREFLIGHT, "start_command")
        before = len(self.journal.transitions())
        result = machine.transition(sm.PREFLIGHT, "start_command")
        self.assertFalse(result.applied)
        self.assertEqual(result.reason, "idempotent_repeat")
        self.assertEqual(len(self.journal.transitions()), before)

    def test_a_restart_resumes_the_committed_state_exactly(self) -> None:
        self.machine().transition(sm.PREFLIGHT, "start_command")
        self.reopen()
        self.assertEqual(self.machine().current_state, sm.PREFLIGHT)

    def test_a_restart_never_creates_two_successors(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.succeed(self.journal, expected_epoch=1,
                            new_owner_run_id="run-b", now=100.0,
                            ttl_seconds=10.0)
        self.reopen()
        # The replayed succession attempt (same expected epoch) is refused.
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.succeed(self.journal, expected_epoch=1,
                                new_owner_run_id="run-b2", now=101.0,
                                ttl_seconds=10.0)
        self.assertEqual(ctx.exception.code, "succession_race_lost")
        self.assertEqual(epoch_lease.current_lease(self.journal).epoch, 2)

    def test_an_idempotency_key_is_never_reused(self) -> None:
        self.journal.record_before_effect(
            action_id="push-1", effect_type="git_push", target="origin",
            expected_prior_state="sha-a", request_digest="d1")
        from tools.agent_supervisor.durable_state import JournalError
        with self.assertRaises(JournalError):
            self.journal.record_before_effect(
                action_id="push-1", effect_type="git_push", target="origin",
                expected_prior_state="sha-a", request_digest="d1")


# ---------------------------------------------------------------------------
# S4 — stop-intent precedence survives restart (R026/R027)
# ---------------------------------------------------------------------------


class S4StopIntentPrecedence(JournalCase):
    def test_graceful_stop_survives_a_restart_and_wins_over_queued_work(self) -> None:
        stop_intent.set_graceful_stop(self.journal, reason="owner said land it",
                                      audit=self.audit)
        self.reopen()
        intents = stop_intent.StopIntents.read(self.journal)
        self.assertTrue(intents.graceful)
        self.assertEqual(intents.graceful_reason, "owner said land it")
        effective = stop_intent.effective_intent(intents)
        self.assertEqual(effective, stop_intent.INTENT_GRACEFUL)
        self.assertTrue(stop_intent.wins_over_queued_work(effective))
        self.assertFalse(stop_intent.may_dispatch_new_work(effective))

    def test_precedence_emergency_over_graceful_over_pause(self) -> None:
        recovery.set_manual_pause(self.journal, paused=True, reason="hold")
        self.assertEqual(
            stop_intent.effective_intent(stop_intent.StopIntents.read(self.journal)),
            stop_intent.INTENT_PAUSE)
        stop_intent.set_graceful_stop(self.journal, reason="land")
        self.assertEqual(
            stop_intent.effective_intent(stop_intent.StopIntents.read(self.journal)),
            stop_intent.INTENT_GRACEFUL)
        recovery.set_emergency_stop(self.journal, reason="stop now")
        self.assertEqual(
            stop_intent.effective_intent(stop_intent.StopIntents.read(self.journal)),
            stop_intent.INTENT_EMERGENCY)

    def test_only_graceful_lets_the_current_unit_finish(self) -> None:
        self.assertTrue(stop_intent.may_finish_current_unit(
            stop_intent.INTENT_GRACEFUL))
        self.assertFalse(stop_intent.may_finish_current_unit(
            stop_intent.INTENT_EMERGENCY))
        self.assertFalse(stop_intent.may_finish_current_unit(
            stop_intent.INTENT_PAUSE))

    def test_only_an_owner_command_clears_the_intent(self) -> None:
        stop_intent.set_graceful_stop(self.journal, reason="land")
        with self.assertRaises(stop_intent.StopIntentError):
            stop_intent.clear_graceful_stop(self.journal, owner_command=False)
        stop_intent.clear_graceful_stop(self.journal, owner_command=True)
        self.assertFalse(stop_intent.StopIntents.read(self.journal).graceful)

    def test_the_machine_lands_a_graceful_stop_from_checkpoint_and_recovery(self) -> None:
        machine = self.machine()
        self.journal.set_state(sm.STATE_KEY, sm.CHECKPOINT_RECEIVED)
        machine.transition(sm.GRACEFUL_STOPPING, "graceful_stop_intent_set")
        machine.transition(sm.IDLE, "graceful_stop_landed")
        self.journal.set_state(sm.STATE_KEY, sm.RECOVER_BOOT)
        self.journal.set_state(sm.LAST_TRIGGER_KEY, "")
        machine.transition(sm.GRACEFUL_STOPPING, "recovery_finds_graceful_stop")
        machine.transition(sm.EMERGENCY_STOPPED, "owner_emergency_stop")

    def test_an_unexplained_graceful_stop_is_refused(self) -> None:
        with self.assertRaises(stop_intent.StopIntentError):
            stop_intent.set_graceful_stop(self.journal, reason="   ")


# ---------------------------------------------------------------------------
# S5 — the three interruption classes are handled separately (R031)
# ---------------------------------------------------------------------------


class S5ThreeInterruptionClasses(JournalCase):
    def test_class_1_turnover_is_a_bounded_handoff_with_exact_once_successor(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")
        successor = epoch_lease.succeed(self.journal, expected_epoch=1,
                                        new_owner_run_id="run-b", now=10.0,
                                        ttl_seconds=100.0)
        self.assertEqual(successor.epoch, 2)
        log = self.journal.get_state(epoch_lease.SUCCESSION_LOG_KEY)
        self.assertEqual(log[-1]["predecessor_state"], "released")

    def test_class_2_crash_restart_resumes_the_same_epoch_no_duplicate(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        self.reopen()  # the watchdog restarted the controller process
        outcome = epoch_lease.reconcile_on_boot(self.journal, run_id="run-a",
                                                now=50.0)
        self.assertEqual(outcome.status, epoch_lease.OWN_LEASE_LIVE)
        self.assertTrue(outcome.resumes_same_epoch)
        self.assertEqual(outcome.lease.epoch, 1)

    def test_class_2_anothers_live_lease_permits_read_only_orientation_only(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        outcome = epoch_lease.reconcile_on_boot(self.journal, run_id="run-new",
                                                now=10.0)
        self.assertEqual(outcome.status, epoch_lease.OTHER_LEASE_LIVE)
        self.assertTrue(epoch_lease.may_orient_read_only(outcome))
        self.assertFalse(epoch_lease.may_dispatch_writes(
            outcome, external_effects_reconciled=True))

    def test_write_authority_needs_full_reconciliation(self) -> None:
        # M0-T092 correction F2/F3 (G3 LOW-2, G4 LOW-3): an owned live epoch
        # alone is not write authority — undrained children or unreconciled
        # external effects refuse, and the effects fact has NO default.
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        outcome = epoch_lease.reconcile_on_boot(self.journal, run_id="run-a",
                                                now=10.0)
        self.assertTrue(epoch_lease.may_dispatch_writes(
            outcome, external_effects_reconciled=True))
        self.assertFalse(epoch_lease.may_dispatch_writes(
            outcome, unreconciled_children=("child-1",),
            external_effects_reconciled=True))
        self.assertFalse(epoch_lease.may_dispatch_writes(
            outcome, external_effects_reconciled=False))
        with self.assertRaises(TypeError):
            epoch_lease.may_dispatch_writes(outcome)  # type: ignore[call-arg]

    def test_class_3_outage_is_explicit_backoff_or_blocked_never_a_successor(self) -> None:
        state = outage_policy.record_transient_failure(
            self.journal, cause="network", reason="connection reset",
            now=100.0,
            policy=outage_policy.BackoffPolicy(base_seconds=5, factor=2,
                                               cap_seconds=60, max_attempts=3),
            rng=lambda: 0.5)
        self.assertEqual(state.attempt, 1)
        self.assertIsNone(epoch_lease.current_lease(self.journal))

    def test_the_three_classes_use_distinct_durable_records(self) -> None:
        # Turnover -> the lease + succession log; crash -> the state machine
        # journal; outage -> the retry record. No class writes another's key.
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        outage_policy.record_transient_failure(
            self.journal, cause="timeout", reason="timed out", now=0.0,
            policy=outage_policy.BackoffPolicy(base_seconds=1, factor=2,
                                               cap_seconds=8, max_attempts=2),
            rng=lambda: 0.5)
        self.assertIsNotNone(self.journal.get_state(epoch_lease.LEASE_KEY))
        self.assertIsNotNone(self.journal.get_state(outage_policy.RETRY_KEY))
        self.assertNotEqual(epoch_lease.LEASE_KEY, outage_policy.RETRY_KEY)


# ---------------------------------------------------------------------------
# S6 — safe-seam detection and handoff validation (section 7, R066/R067)
# ---------------------------------------------------------------------------


class S6SafeSeamValidation(JournalCase):
    @staticmethod
    def quiet_state(**overrides) -> rotation.RotationSafetyState:
        return rotation.RotationSafetyState(**overrides)

    def test_a_quiet_unambiguous_moment_passes(self) -> None:
        turnover_seam.assert_safe_seam(self.quiet_state())

    def test_each_section_7_condition_refuses_the_seam(self) -> None:
        for field_name, value in (
            ("command_running", True),               # atomic batch incomplete
            ("tool_call_pending", True),
            ("approval_pending", True),              # unanswered permission
            ("unaccounted_background_actions", 2),   # effects not accounted
            ("unexplained_uncommitted_changes", True),
            ("merge_or_rebase_in_progress", True),
            ("conflict_present", True),
            ("sha_ambiguous", True),                 # lease/identity unknown
            ("worktree_ambiguous", True),
            ("task_stage_ambiguous", True),
            ("children_unreconciled", 1),            # children not reconciled
        ):
            with self.subTest(condition=field_name):
                with self.assertRaises(turnover_seam.SeamTurnoverError):
                    turnover_seam.assert_safe_seam(
                        self.quiet_state(**{field_name: value}))

    def test_undrained_children_flow_into_the_safety_state(self) -> None:
        state = turnover_seam.safety_state_from_run(
            head_sha="a" * 40, branch="b", worktree="w", task_stage="t",
            unreconciled_children=("child-1",))
        self.assertEqual(state.children_unreconciled, 1)
        with self.assertRaises(turnover_seam.SeamTurnoverError):
            turnover_seam.assert_safe_seam(state)

    def test_the_handoff_packet_is_smallest_complete_never_truncated(self) -> None:
        # R067: an incomplete handoff refuses; a bounded child summary refuses
        # a transcript-sized payload outright (no silent truncation).
        facts = turnover_seam.SeamFacts(
            task_id="M0-T092", stage="landing", branch="control/x",
            worktree="C:/wt", head_sha="a" * 40,
            exact_next_action="run the section-16.3 matrix",
            reason_code="context_threshold")
        handoff = turnover_seam.build_handoff(facts)
        self.assertIn("HEAD", handoff.authoritative_shas)
        for entry in turnover_seam.STRUCTURAL_FORBIDDEN_SCOPE:
            self.assertIn(entry, handoff.forbidden_scope)
        with self.assertRaises(turnover_seam.SeamTurnoverError):
            turnover_seam.build_handoff(
                turnover_seam.SeamFacts(
                    task_id="M0-T092", stage="landing", branch="control/x",
                    worktree="C:/wt", head_sha="a" * 40,
                    exact_next_action="", reason_code="context_threshold"))
        with self.assertRaises(child_handoff.HandoffError) as ctx:
            child_handoff.ChildHandoff(
                assignment_id="a1", parent_task_id="M0-T092",
                outcome="complete", bounded_summary="x" * 5000,
                completed="c", repository_state="clean",
                exact_next_action="none")
        self.assertEqual(ctx.exception.code, "transcript_not_summary")

    def test_a_refused_seam_names_every_reason(self) -> None:
        state = self.quiet_state(approval_pending=True, children_unreconciled=2)
        with self.assertRaises(turnover_seam.SeamTurnoverError) as ctx:
            turnover_seam.assert_safe_seam(state)
        reasons = ctx.exception.detail["reasons"]
        self.assertEqual(len(reasons), 2)


# ---------------------------------------------------------------------------
# S7 — exact-once rotation: the lease race has one winner (R028/R030)
# ---------------------------------------------------------------------------


class S7ExactOnceLeaseRace(JournalCase):
    def test_two_racing_successors_resolve_to_exactly_one_winner(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")
        # Both contenders READ the same predecessor state (epoch 1, released)
        # through their own connections, then race the succession.
        second = DurableJournal(self.db).open()
        self.addCleanup(second.close)
        winner = epoch_lease.succeed(self.journal, expected_epoch=1,
                                     new_owner_run_id="run-b", now=20.0,
                                     ttl_seconds=10.0)
        self.assertEqual(winner.owner_run_id, "run-b")
        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.succeed(second, expected_epoch=1,
                                new_owner_run_id="run-c", now=20.0,
                                ttl_seconds=10.0)
        self.assertEqual(ctx.exception.code, "succession_race_lost")
        # The durable store shows ONE successor; the loser dispatched nothing.
        final = epoch_lease.current_lease(self.journal)
        self.assertEqual((final.epoch, final.owner_run_id), (2, "run-b"))
        log = self.journal.get_state(epoch_lease.SUCCESSION_LOG_KEY)
        self.assertEqual(len(log), 1)

    def test_the_cas_primitive_is_single_winner_across_connections(self) -> None:
        second = DurableJournal(self.db).open()
        self.addCleanup(second.close)
        self.assertTrue(self.journal.compare_and_swap_state("k", None, "a"))
        self.assertFalse(second.compare_and_swap_state("k", None, "b"))
        self.assertTrue(second.compare_and_swap_state("k", "a", "c"))
        self.assertFalse(self.journal.compare_and_swap_state("k", "a", "d"))
        self.assertEqual(self.journal.get_state("k"), "c")

    def test_a_stored_null_is_not_absence(self) -> None:
        self.journal.set_state("cleared", None)
        self.assertFalse(self.journal.compare_and_swap_state("cleared", None, "x"))

    def test_a_lost_cas_is_a_typed_refusal_never_a_silent_win(self) -> None:
        # The interleaving the epoch check cannot catch: the other contender
        # commits BETWEEN this contender's read and its write. Modelled by a
        # journal whose CAS reports the loss; the loser must raise, not write.
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")

        class LosingJournal:
            def __init__(self, inner) -> None:
                self._inner = inner

            def get_state(self, key, default=None):
                return self._inner.get_state(key, default)

            def set_state(self, key, value):
                raise AssertionError("a losing successor must write nothing")

            def compare_and_swap_state(self, key, expected, value):
                return False  # the other contender committed first

        with self.assertRaises(epoch_lease.LeaseError) as ctx:
            epoch_lease.succeed(LosingJournal(self.journal), expected_epoch=1,
                                new_owner_run_id="run-l", now=20.0,
                                ttl_seconds=10.0)
        self.assertEqual(ctx.exception.code, "succession_race_lost")


# ---------------------------------------------------------------------------
# S8 — controller-crash windows reconcile without duplicates (R030/R031)
# ---------------------------------------------------------------------------


class S8CrashWindowReconciliation(JournalCase):
    def revalidation_all_pass(self) -> dict[str, bool]:
        return {step: True for step in recovery.REVALIDATION_STEPS}

    def test_crash_after_before_effect_classifies_ambiguous(self) -> None:
        self.journal.record_before_effect(
            action_id="pr-comment-1", effect_type="github_comment",
            target="PR#1", expected_prior_state="none", request_digest="d")
        self.reopen()
        outcome = recovery.recover_boot(
            journal=self.journal, lock=None,
            revalidation=self.revalidation_all_pass())
        self.assertEqual(outcome.classification, recovery.AMBIGUOUS_EFFECT)
        self.assertEqual(outcome.pending_effect_ids, ("pr-comment-1",))

    def test_crash_after_verified_after_effect_is_a_safe_checkpoint(self) -> None:
        self.journal.record_before_effect(
            action_id="pr-comment-2", effect_type="github_comment",
            target="PR#1", expected_prior_state="none", request_digest="d")
        self.journal.record_after_effect("pr-comment-2",
                                         resulting_state="comment exists")
        self.reopen()
        outcome = recovery.recover_boot(
            journal=self.journal, lock=None,
            revalidation=self.revalidation_all_pass())
        self.assertEqual(outcome.classification, recovery.SAFE_CHECKPOINT)
        # This build never auto-resumes: limited-auto is not owner-enabled.
        self.assertFalse(outcome.resume_permitted)

    def test_a_rolled_back_journal_is_rejected_not_guessed_at(self) -> None:
        self.machine().transition(sm.PREFLIGHT, "start_command")
        self.journal._meta_set("high_water_sequence", "99")
        report = self.journal.integrity_check()
        self.assertFalse(report.ok)
        self.assertEqual(report.code, "rolled_back")

    def test_crash_between_gate_arming_and_rotation_completion_fails_closed(self) -> None:
        # U12 ordering: the armed gate survives the crash; the successor's next
        # checkpoint must satisfy it before anything is forwarded.
        seam = turnover_seam.SeamTurnover(journal=self.journal, run_id="run-1")
        expectation = turnover_seam.SuccessorExpectation(
            task_id="M0-T092", branch="control/x", worktree="C:/wt",
            head_sha="a" * 40, model_id="m",
            continuity_mode=session_continuity.REORIENTATION)
        seam.arm_ready_gate(expectation, handoff_digest="h" * 64)
        self.reopen()
        seam_after = turnover_seam.SeamTurnover(journal=self.journal,
                                                run_id="run-1")

        class NotReady:
            status = "WORKING"
            claude_session_id = "s-1"

        with self.assertRaises(turnover_seam.SeamTurnoverError):
            seam_after.require_ready(NotReady())

    def test_crash_after_lease_commit_resumes_the_same_epoch(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=100.0)
        self.reopen()
        outcome = epoch_lease.reconcile_on_boot(self.journal, run_id="run-a",
                                                now=1.0)
        self.assertTrue(outcome.resumes_same_epoch)


# ---------------------------------------------------------------------------
# S9 — host-restart auto-resume, or a truthful activation blocker (R032)
# ---------------------------------------------------------------------------


class S9HostRestartAutoResume(JournalCase):
    def launcher(self) -> LauncherSpec:
        return LauncherSpec(
            path=str(self.tmp / "python.exe"),
            digest_sha256="c" * 64,
            launch_arguments=("-m", "tools.agent_supervisor", "resume"),
            working_directory=str(self.tmp))

    def test_the_plan_is_read_only_and_names_the_exact_action(self) -> None:
        plan = build_autostart_plan(launcher=self.launcher(), kind="boot")
        self.assertTrue(plan.create_argv)
        self.assertTrue(plan.task_xml)
        self.assertIn("resume", " ".join(plan.action_argv))

    def test_a_drifted_installed_definition_is_reported_not_accepted(self) -> None:
        plan = build_autostart_plan(launcher=self.launcher(), kind="boot")
        tampered = plan.task_xml.replace("resume", "exfiltrate")
        ok, reason = verify_installed_definition(plan, tampered)
        self.assertFalse(ok)
        self.assertTrue(reason)

    def test_forbidden_registration_reports_a_truthful_activation_blocker(self) -> None:
        limitations = runtime_backend.activation_limitations()
        self.assertTrue(limitations)
        joined = " ".join(limitations)
        self.assertIn("one-command start", joined)
        self.assertIn("activation blocker", joined)


# ---------------------------------------------------------------------------
# S10 — Codex transport preflight fails closed (R024/R025)
# ---------------------------------------------------------------------------


class S10CodexPreflightFailClosed(unittest.TestCase):
    def valid_decision(self) -> dict:
        return {
            "schema_version": "supervisor_codex_decision/v1",
            "decision": "CONTINUE",
            "reviewed_task_id": "M0-T092",
            "reviewed_checkpoint_id": "cp-1",
            "verified_repo_head": "a" * 40,
            "verified_origin_main": "b" * 40,
            "model_used": "gpt-5",
            "next_claude_prompt": "run the next bounded unit",
            "reason_codes": ["evidence_sufficient"],
        }

    def test_a_valid_identity_bound_decision_validates(self) -> None:
        decision = validate_decision(self.valid_decision(),
                                     expected_task_id="M0-T092",
                                     expected_checkpoint_id="cp-1")
        self.assertEqual(decision.decision, "CONTINUE")

    def test_missing_malformed_and_mismatched_decisions_dispatch_nothing(self) -> None:
        cases = {
            "not_an_object": "just a string",
            "unknown_field": {**self.valid_decision(), "surprise": 1},
            "missing_required": {k: v for k, v in self.valid_decision().items()
                                 if k != "next_claude_prompt"},
        }
        for name, payload in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(ReviewError):
                    validate_decision(payload, expected_task_id="M0-T092",
                                      expected_checkpoint_id="cp-1")

    def test_an_identity_mismatch_is_never_permission_to_dispatch(self) -> None:
        with self.assertRaises(ReviewError):
            validate_decision(self.valid_decision(),
                              expected_task_id="M9-T999",
                              expected_checkpoint_id="cp-1")
        with self.assertRaises(ReviewError):
            validate_decision(self.valid_decision(),
                              expected_task_id="M0-T092",
                              expected_checkpoint_id="cp-OTHER")

    def test_capability_drift_is_named_before_any_dispatch(self) -> None:
        accepted = CapabilityManifest(
            executables={"codex": {"version": "1.2.3", "json_events": True}})
        observed = CapabilityManifest(
            executables={"codex": {"version": "9.9.9", "json_events": True}})
        diffs = accepted.differences(observed)
        self.assertTrue(any("1.2.3" in d and "9.9.9" in d for d in diffs))
        self.assertEqual(accepted.differences(accepted), ())


# ---------------------------------------------------------------------------
# S11 — outage: backoff vs blocked vs bounded idle (R033)
# ---------------------------------------------------------------------------


class S11OutageBackoffVsBlocked(JournalCase):
    def policy(self) -> outage_policy.BackoffPolicy:
        return outage_policy.BackoffPolicy(base_seconds=10, factor=2,
                                           cap_seconds=60, max_attempts=3,
                                           jitter_fraction=0.2)

    def test_the_classification_is_closed_and_fails_closed(self) -> None:
        self.assertEqual(outage_policy.classify_reason_text(
            "HTTP 429: rate limit exceeded"), ("rate_limit", outage_policy.TRANSIENT))
        self.assertEqual(outage_policy.classify_reason_text(
            "401 Unauthorized: bad api key"), ("auth", outage_policy.BLOCKING))
        self.assertEqual(outage_policy.classify_reason_text(
            "something entirely novel"), ("unrecognized", outage_policy.BLOCKING))
        self.assertEqual(outage_policy.classify_cause("made_up_cause"),
                         outage_policy.BLOCKING)

    def test_mixed_reason_text_resolves_toward_blocking(self) -> None:
        # M0-T092 correction F1 (G3 LOW-1 / G5 LOW-1): a blocking token
        # anywhere in the reason outranks every transient token — auth,
        # billing, and revoked-access failures never enter the retry loop
        # merely because the message also mentions a transport symptom.
        for reason, cause in (
            ("Authentication error: connection refused by auth endpoint (401)",
             "auth"),
            ("authentication failed: connection reset", "auth"),
            ("billing problem, request timed out", "billing"),
            ("revoked access after timeout", "revoked_access"),
            ("unsupported version detected over a flaky network",
             "incompatibility"),
        ):
            with self.subTest(reason=reason):
                self.assertEqual(outage_policy.classify_reason_text(reason),
                                 (cause, outage_policy.BLOCKING))

    def test_backoff_grows_to_the_cap_with_bounded_jitter(self) -> None:
        policy = self.policy()
        mid = [policy.delay_for(a, rng=lambda: 0.5) for a in (1, 2, 3)]
        self.assertEqual(mid, [10.0, 20.0, 40.0])
        low = policy.delay_for(3, rng=lambda: 0.0)
        high = policy.delay_for(3, rng=lambda: 0.999999)
        self.assertGreaterEqual(low, 40.0 * 0.8)
        self.assertLess(high, 40.0 * 1.2000001)
        capped = outage_policy.BackoffPolicy(
            base_seconds=10, factor=2, cap_seconds=60, max_attempts=5,
            jitter_fraction=0.0)
        self.assertEqual(capped.delay_for(4, rng=lambda: 0.5), 60.0)
        self.assertEqual(capped.delay_for(5, rng=lambda: 0.5), 60.0)

    def test_attempts_are_bounded_never_unlimited(self) -> None:
        policy = self.policy()
        for _attempt in (1, 2, 3):
            outage_policy.record_transient_failure(
                self.journal, cause="network", reason="reset", now=0.0,
                policy=policy, rng=lambda: 0.5)
        with self.assertRaises(outage_policy.OutageError) as ctx:
            outage_policy.record_transient_failure(
                self.journal, cause="network", reason="reset", now=0.0,
                policy=policy, rng=lambda: 0.5)
        self.assertEqual(ctx.exception.code, "attempts_exhausted")

    def test_retry_state_is_durable_and_deadline_gated(self) -> None:
        state = outage_policy.record_transient_failure(
            self.journal, cause="timeout", reason="timed out", now=100.0,
            policy=self.policy(), rng=lambda: 0.5)
        self.reopen()
        stored = outage_policy.stored_retry_state(self.journal)
        self.assertEqual(stored.attempt, 1)
        self.assertFalse(outage_policy.retry_due(stored, now=100.0))
        self.assertTrue(outage_policy.retry_due(stored,
                                                now=state.next_retry_at_epoch))

    def test_blocking_causes_hold_for_the_owner_with_a_handoff(self) -> None:
        with self.assertRaises(outage_policy.OutageError):
            outage_policy.record_transient_failure(
                self.journal, cause="billing", reason="payment required",
                now=0.0, policy=self.policy(), rng=lambda: 0.5)
        record = outage_policy.record_blocked_with_handoff(
            self.journal, cause="billing", reason="payment required")
        self.assertIn("owner action", record["requires"])
        with self.assertRaises(outage_policy.OutageError):
            outage_policy.record_blocked_with_handoff(
                self.journal, cause="network", reason="reset")

    def test_no_eligible_work_enters_bounded_idle_never_a_busy_loop(self) -> None:
        state = outage_policy.begin_bounded_idle(
            self.journal, now=0.0, idle_seconds=600.0,
            reason="no eligible authorized task")
        self.assertFalse(outage_policy.idle_over(state, now=599.0))
        self.assertTrue(outage_policy.idle_over(state, now=600.0))
        with self.assertRaises(outage_policy.OutageError):
            outage_policy.begin_bounded_idle(
                self.journal, now=0.0,
                idle_seconds=outage_policy.MAX_IDLE_SECONDS + 1,
                reason="too long")

    def test_during_a_hold_nothing_new_dispatches(self) -> None:
        transient = outage_policy.permissions_during(outage_policy.TRANSIENT)
        self.assertTrue(transient.may_land_current_atomic_operation)
        self.assertFalse(transient.may_dispatch_new_producer_work)
        blocking = outage_policy.permissions_during(outage_policy.BLOCKING)
        self.assertFalse(blocking.may_land_current_atomic_operation)
        self.assertFalse(blocking.may_dispatch_new_producer_work)

    def test_the_machine_routes_outages_through_the_new_states(self) -> None:
        machine = self.machine()
        self.journal.set_state(sm.STATE_KEY, sm.CODEX_REVIEW)
        machine.transition(sm.CODEX_OUTAGE_BACKOFF, "codex_transient_failure")
        machine.transition(sm.CODEX_REVIEW, "outage_retry_due")
        machine.transition(sm.CODEX_OUTAGE_BACKOFF, "codex_transient_failure")
        machine.transition(sm.WAIT_FOR_OWNER, "outage_blocked_with_handoff")


# ---------------------------------------------------------------------------
# S12 — Bootstrap Gate 0 for a new session (R125–R128)
# ---------------------------------------------------------------------------


class S12Gate0Recovery(JournalCase):
    def passing_inputs(self) -> bootstrap_gate.Gate0Inputs:
        return bootstrap_gate.Gate0Inputs(
            primary_cwd=str(self.tmp), intended_root=str(self.tmp),
            mcp_enumeration_known=True)

    def test_a_correct_launch_root_and_clean_mcp_pass(self) -> None:
        verdict = bootstrap_gate.evaluate_gate0(self.passing_inputs())
        self.assertTrue(verdict.passed)
        self.assertTrue(bootstrap_gate.may_write(verdict))
        bootstrap_gate.assert_may_write(verdict)

    def test_added_dir_access_is_not_equivalent(self) -> None:
        inputs = bootstrap_gate.Gate0Inputs(
            primary_cwd=str(self.tmp), intended_root=str(self.tmp),
            mcp_enumeration_known=True, reached_via_added_dir=True)
        verdict = bootstrap_gate.evaluate_gate0(inputs)
        self.assertFalse(verdict.passed)

    def test_wrong_or_unknown_launch_root_fails(self) -> None:
        other = pathlib.Path(tempfile.mkdtemp(prefix="unitf_other_"))
        for inputs in (
            bootstrap_gate.Gate0Inputs(primary_cwd=str(other),
                                       intended_root=str(self.tmp),
                                       mcp_enumeration_known=True),
            bootstrap_gate.Gate0Inputs(primary_cwd="",
                                       intended_root=str(self.tmp),
                                       mcp_enumeration_known=True),
        ):
            with self.subTest(cwd=inputs.primary_cwd):
                self.assertFalse(bootstrap_gate.evaluate_gate0(inputs).passed)

    def test_unknown_or_unapproved_mcp_state_fails_closed(self) -> None:
        unknown = bootstrap_gate.Gate0Inputs(
            primary_cwd=str(self.tmp), intended_root=str(self.tmp),
            mcp_enumeration_known=False)
        self.assertFalse(bootstrap_gate.evaluate_gate0(unknown).passed)
        rogue = bootstrap_gate.Gate0Inputs(
            primary_cwd=str(self.tmp), intended_root=str(self.tmp),
            mcp_enumeration_known=True,
            attached_mcp_servers=("rogue-server",))
        self.assertFalse(bootstrap_gate.evaluate_gate0(rogue).passed)
        allowlisted = bootstrap_gate.Gate0Inputs(
            primary_cwd=str(self.tmp), intended_root=str(self.tmp),
            mcp_enumeration_known=True,
            attached_mcp_servers=("approved",),
            approved_mcp_allowlist=("approved",))
        self.assertTrue(bootstrap_gate.evaluate_gate0(allowlisted).passed)

    def test_failure_permits_read_only_diagnosis_only(self) -> None:
        verdict = bootstrap_gate.evaluate_gate0(bootstrap_gate.Gate0Inputs(
            primary_cwd="C:/elsewhere", intended_root=str(self.tmp),
            dirty_paths=("a.py",)))
        self.assertFalse(bootstrap_gate.may_write(verdict))
        with self.assertRaises(bootstrap_gate.Gate0Error):
            bootstrap_gate.assert_may_write(verdict)
        diagnosis = verdict.diagnosis
        self.assertEqual(diagnosis["actual_launch_directory"], "C:/elsewhere")
        self.assertEqual(diagnosis["intended_worktree_root"], str(self.tmp))
        self.assertEqual(diagnosis["dirty_uncommitted_paths"], ["a.py"])
        self.assertIn("read-only", diagnosis["posture_on_failure"])

    def test_adoption_of_uncommitted_work_requires_a_fresh_pass(self) -> None:
        failed = bootstrap_gate.evaluate_gate0(bootstrap_gate.Gate0Inputs(
            primary_cwd="C:/elsewhere", intended_root=str(self.tmp)))
        refused = bootstrap_gate.adoption_of_uncommitted(
            failed, dirty_paths=("a.py",))
        self.assertFalse(refused.permitted)
        passed = bootstrap_gate.evaluate_gate0(self.passing_inputs())
        allowed = bootstrap_gate.adoption_of_uncommitted(
            passed, dirty_paths=("a.py",))
        self.assertTrue(allowed.permitted)
        self.assertIn("never rewrite history", allowed.instruction)


# ---------------------------------------------------------------------------
# S13 — one active backend; native resume is never a seam (R160/R180)
# ---------------------------------------------------------------------------


class S13OneBackendNativeResumeNotASeam(unittest.TestCase):
    def caps(self, supported: bool) -> NativeCapabilities:
        from tools.agent_supervisor.native_runtime import (
            REQUIRED_BACKGROUND_FLAGS,
            REQUIRED_BACKGROUND_VERBS,
            STATUS_SUPPORTED,
        )
        status = STATUS_SUPPORTED if supported else "unknown"
        return NativeCapabilities(
            claude_version="2.1.247",
            flags={f: status for f in REQUIRED_BACKGROUND_FLAGS},
            verbs={v: status for v in REQUIRED_BACKGROUND_VERBS})

    def test_exactly_one_backend_is_ever_active(self) -> None:
        native = runtime_backend.select_runtime_backend(
            self.caps(True), prefer_native=True)
        controller = runtime_backend.select_runtime_backend(
            self.caps(True), prefer_native=False)
        degraded = runtime_backend.select_runtime_backend(
            self.caps(False), prefer_native=True)
        self.assertEqual(native.backend, runtime_backend.BACKEND_NATIVE)
        self.assertEqual(controller.backend, runtime_backend.BACKEND_CONTROLLER)
        self.assertEqual(degraded.backend, runtime_backend.BACKEND_CONTROLLER)
        self.assertEqual(
            {runtime_backend.BACKEND_NATIVE, runtime_backend.BACKEND_CONTROLLER},
            {native.backend, controller.backend})

    def test_native_resume_is_never_a_safe_seam_substitute(self) -> None:
        recorded = session_continuity.ProviderSession(
            session_id="prov-1", model_id="claude-fable-5")
        # A context-shedding rotation may NOT resume, even with the id recorded
        # and the capability verified: a large/confused conversation is not
        # resumed merely because it is technically resumable (R160).
        decision = session_continuity.decide_continuity(
            recorded=recorded, successor_model="claude-fable-5",
            rotation_reason="context_threshold",
            resume_capability_verified=True)
        self.assertEqual(decision.mode, session_continuity.REORIENTATION)
        self.assertIn(session_continuity.CONTEXT_SHEDDING_ROTATION,
                      decision.none_reasons)

    def test_an_unverified_resume_capability_reorients(self) -> None:
        recorded = session_continuity.ProviderSession(
            session_id="prov-1", model_id="claude-fable-5")
        decision = session_continuity.decide_continuity(
            recorded=recorded, successor_model="claude-fable-5",
            rotation_reason="", resume_capability_verified=False)
        self.assertEqual(decision.mode, session_continuity.REORIENTATION)
        self.assertIn(session_continuity.RESUME_CAPABILITY_UNVERIFIED,
                      decision.none_reasons)

    def test_a_verified_same_model_non_shedding_resume_is_a_resume(self) -> None:
        recorded = session_continuity.ProviderSession(
            session_id="prov-1", model_id="claude-fable-5")
        decision = session_continuity.decide_continuity(
            recorded=recorded, successor_model="claude-fable-5",
            rotation_reason="", resume_capability_verified=True)
        self.assertEqual(decision.mode, session_continuity.RESUME)
        self.assertEqual(decision.provider_session_id, "prov-1")


# ---------------------------------------------------------------------------
# S14 — no worker-visible token pressure (R045)
# ---------------------------------------------------------------------------


class S14NoWorkerTokenPressure(unittest.TestCase):
    def test_the_landing_instruction_is_clean(self) -> None:
        assert_worker_text_clean("landing_instruction", LANDING_DIRECTION_TEXT)

    def test_quota_language_fails_closed(self) -> None:
        for text in (
            "finish quickly, you have 20k tokens left",
            "context is at 85%, wrap up",
            "conserve tokens while you work",
        ):
            with self.subTest(text=text):
                with self.assertRaises(ContractError):
                    assert_worker_text_clean("assignment", text)


# ---------------------------------------------------------------------------
# S15 — telemetry honesty on succession records (R042)
# ---------------------------------------------------------------------------


class S15TelemetryHonesty(JournalCase):
    def test_missing_usage_is_unknown_never_zero(self) -> None:
        unknown = Measurement(value=None, label="unknown", category="occupancy")
        self.assertIsNone(unknown.value)
        with self.assertRaises(TelemetryRecordError):
            Measurement(value=None, label="provider-exact", category="occupancy")
        with self.assertRaises(TelemetryRecordError):
            Measurement(value=120000, label="unknown", category="occupancy")
        with self.assertRaises(TelemetryRecordError):
            Measurement(value=1, label="made-up-source", category="occupancy")

    def test_a_succession_records_its_usage_with_a_source_label(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")
        usage = Measurement(value=412_000, label="status-live",
                            category="occupancy",
                            detail="context at the succession decision")
        epoch_lease.succeed(self.journal, expected_epoch=1,
                            new_owner_run_id="run-b", now=20.0,
                            ttl_seconds=10.0, usage=usage)
        entry = self.journal.get_state(epoch_lease.SUCCESSION_LOG_KEY)[-1]
        self.assertEqual(entry["usage"]["label"], "status-live")
        self.assertEqual(entry["usage"]["value"], 412_000)

    def test_a_succession_with_no_usage_stores_no_invented_number(self) -> None:
        epoch_lease.acquire_first(self.journal, campaign_id="d024",
                                  owner_run_id="run-a", now=0.0,
                                  ttl_seconds=10.0)
        epoch_lease.release(self.journal, owner_run_id="run-a")
        epoch_lease.succeed(self.journal, expected_epoch=1,
                            new_owner_run_id="run-b", now=20.0,
                            ttl_seconds=10.0)
        entry = self.journal.get_state(epoch_lease.SUCCESSION_LOG_KEY)[-1]
        self.assertNotIn("usage", entry)


if __name__ == "__main__":
    unittest.main()
