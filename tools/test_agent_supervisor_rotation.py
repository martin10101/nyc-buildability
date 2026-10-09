#!/usr/bin/env python3
"""Rotation tests (D-007 Section 15 "rotation" family).

Covers the directive's own list, in its order:

* thresholds with SMALL / MEDIUM / LARGE / UNKNOWN next units
* mandatory pre-dispatch rotation
* a threshold crossed MID-UNIT sets `rotation_pending` WITHOUT termination
* the in-flight unit reaches a complete checkpoint first
* a provider-enforced abort is recorded INCOMPLETE
* an emergency stop still terminates
* unknown usage
* compaction and checkpoint-count triggers
* unsafe mid-operation refusal
* an invalid handoff
* a Codex handoff rejection
* the new session's `READY` checkpoint
* no accidental old-session resume

plus the two structural rules: `advisory_model` is never accepted for handoff
verification (S3.3), and `/clear` is never automated (S11.3).

No provider process, no network, no tokens.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import ClaudeCheckpoint  # noqa: E402
from tools.agent_supervisor.state_machine import (  # noqa: E402
    CHECKPOINT_RECEIVED,
    CLAUDE_RUNNING,
    EMERGENCY_STOPPED,
    ROTATION_PENDING,
    StateMachine,
)

REVIEW_MODEL = "review-model-placeholder"
ADVISORY_MODEL = "advisory-model-placeholder"


def good_handoff(**overrides: object) -> rot.Handoff:
    data = {
        "task_and_stage": "M0-T036 / phase 3 implementation",
        "authoritative_shas": {"HEAD": "a" * 40, "origin/main": "b" * 40},
        "branch": "task/example",
        "worktree": "/w/example",
        "completed_work": "three modules implemented and unit-tested",
        "changed_files": ["tools/agent_supervisor/rotation.py"],
        "tests_and_ci": {"unit": "passing", "ci": "not run"},
        "pull_request_state": "no PR open",
        "reviews_and_findings": [],
        "open_blockers": [],
        "owner_gates": ["merge", "acceptance"],
        "forbidden_scope": [".github/**"],
        "exact_next_action": "implement recovery.py per S11.5",
        "evidence_digests": {"packet": "c" * 64},
    }
    data.update(overrides)
    return rot.Handoff.from_dict(data)


class JournalTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runtime = pathlib.Path(self._tmp.name).resolve()
        self.journal = DurableJournal(self.runtime / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / "audit.jsonl", fsync=False)


# --------------------------------------------------------------------------
# S11.1 - classification and the pre-dispatch decision
# --------------------------------------------------------------------------


class NextUnitClassificationTests(unittest.TestCase):
    def test_small_unit(self) -> None:
        result = rot.classify_next_unit(
            rot.NextUnitFeatures(file_count=1, total_target_bytes=2_000))
        self.assertEqual(result.job_size, rot.SMALL)

    def test_medium_unit(self) -> None:
        result = rot.classify_next_unit(
            rot.NextUnitFeatures(file_count=5, total_target_bytes=80_000))
        self.assertEqual(result.job_size, rot.MEDIUM)

    def test_large_unit(self) -> None:
        result = rot.classify_next_unit(
            rot.NextUnitFeatures(file_count=20, total_target_bytes=400_000))
        self.assertEqual(result.job_size, rot.LARGE)

    def test_unknown_when_no_objective_feature_is_available(self) -> None:
        result = rot.classify_next_unit(rot.NextUnitFeatures())
        self.assertEqual(result.job_size, rot.UNKNOWN)
        self.assertIn("no_objective_features", result.features_used)

    def test_full_repo_scan_is_unknown_not_small(self) -> None:
        result = rot.classify_next_unit(
            rot.NextUnitFeatures(file_count=1, total_target_bytes=10,
                                 requires_full_repo_scan=True))
        self.assertEqual(result.job_size, rot.UNKNOWN,
                         "an open-ended scan must never classify as SMALL")

    def test_classification_is_the_max_over_features(self) -> None:
        result = rot.classify_next_unit(
            rot.NextUnitFeatures(file_count=1, total_target_bytes=500_000))
        self.assertEqual(result.job_size, rot.LARGE)

    def test_negative_feature_is_refused(self) -> None:
        with self.assertRaises(rot.RotationError):
            rot.NextUnitFeatures(file_count=-1)

    def test_declared_size_must_be_a_known_class(self) -> None:
        with self.assertRaises(rot.RotationError):
            rot.NextUnitFeatures(declared_size="ENORMOUS")


class PreDispatchDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = rot.RotationThresholds()

    def decide(self, signals: rot.SessionSignals,
               features: rot.NextUnitFeatures) -> rot.RotationDecision:
        return rot.decide_pre_dispatch(signals, features, thresholds=self.thresholds,
                                       at_safe_checkpoint=True)

    def test_mandatory_threshold_rotates_before_any_unit(self) -> None:
        decision = self.decide(
            rot.SessionSignals(cumulative_usage=self.thresholds
                               .preflight_mandatory_rotation),
            rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.reason_code, "mandatory_threshold")
        self.assertEqual(decision.job_size, rot.SMALL,
                         "even a SMALL unit rotates at the mandatory bound")

    def test_large_bound_rotates_before_large_but_not_before_small(self) -> None:
        signals = rot.SessionSignals(
            cumulative_usage=self.thresholds.preflight_large_job_rotation)
        large = self.decide(signals, rot.NextUnitFeatures(file_count=20,
                                                          total_target_bytes=400_000))
        small = self.decide(signals, rot.NextUnitFeatures(file_count=1,
                                                          total_target_bytes=100))
        self.assertTrue(large.rotate)
        self.assertEqual(large.reason_code, "large_job_threshold")
        self.assertFalse(small.rotate)

    def test_large_bound_rotates_before_an_unknown_unit(self) -> None:
        decision = self.decide(
            rot.SessionSignals(
                cumulative_usage=self.thresholds.preflight_large_job_rotation),
            rot.NextUnitFeatures(requires_external_research=True))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.job_size, rot.UNKNOWN)

    def test_below_every_threshold_does_not_rotate(self) -> None:
        decision = self.decide(rot.SessionSignals(cumulative_usage=1000),
                               rot.NextUnitFeatures(file_count=2,
                                                     total_target_bytes=5_000))
        self.assertFalse(decision.rotate)
        self.assertEqual(decision.reason_code, "no_rotation_required")

    def test_unknown_usage_with_high_pressure_takes_the_conservative_action(self) -> None:
        decision = self.decide(
            rot.SessionSignals(usage_known=False, context_pressure_ratio=0.9),
            rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertTrue(decision.conservative_for_unknown)
        self.assertEqual(decision.reason_code, "unknown_usage_conservative")

    def test_unknown_usage_and_unknown_pressure_treats_the_unit_as_unknown(self) -> None:
        decision = self.decide(
            rot.SessionSignals(usage_known=False, context_pressure_known=False),
            rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.job_size, rot.UNKNOWN)
        self.assertTrue(decision.conservative_for_unknown)

    def test_unknown_usage_with_low_pressure_does_not_rotate_a_small_unit(self) -> None:
        decision = self.decide(
            rot.SessionSignals(usage_known=False, context_pressure_ratio=0.1),
            rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertFalse(decision.rotate)
        self.assertTrue(decision.conservative_for_unknown)

    def test_compaction_event_triggers_before_a_large_unit(self) -> None:
        decision = self.decide(rot.SessionSignals(cumulative_usage=10, compaction_events=1),
                               rot.NextUnitFeatures(file_count=30,
                                                     total_target_bytes=900_000))
        self.assertTrue(decision.rotate)
        self.assertIn("compaction_event", decision.triggered_signals)

    def test_checkpoint_count_triggers_regardless_of_unit_size(self) -> None:
        decision = self.decide(
            rot.SessionSignals(completed_checkpoints=self.thresholds
                               .max_checkpoints_per_session),
            rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.reason_code, "checkpoint_count")

    def test_repeated_adherence_loss_triggers(self) -> None:
        decision = self.decide(rot.SessionSignals(consecutive_adherence_failures=2),
                               rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.reason_code, "instruction_adherence_loss")

    def test_oversized_checkpoint_triggers(self) -> None:
        decision = self.decide(rot.SessionSignals(largest_checkpoint_bytes=999_999),
                               rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.reason_code, "oversized_checkpoint")

    def test_owner_request_always_rotates(self) -> None:
        decision = self.decide(rot.SessionSignals(owner_requested_rotation=True),
                               rot.NextUnitFeatures(file_count=1, total_target_bytes=100))
        self.assertTrue(decision.rotate)
        self.assertEqual(decision.reason_code, "owner_request")

    def test_decision_is_unreachable_outside_a_safe_checkpoint(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            rot.decide_pre_dispatch(rot.SessionSignals(), rot.NextUnitFeatures(file_count=1),
                                    at_safe_checkpoint=False)
        self.assertEqual(raised.exception.code, "not_at_safe_checkpoint")

    def test_thresholds_from_config_reject_an_unknown_key(self) -> None:
        class FakeConfig:
            raw = {"rotation": {"preflight_mystery": 1}}

        with self.assertRaises(rot.RotationError):
            rot.RotationThresholds.from_controller_config(FakeConfig())

    def test_thresholds_from_config_reject_an_inverted_pair(self) -> None:
        class FakeConfig:
            raw = {"rotation": {"preflight_large_job_rotation": 900,
                                "preflight_mandatory_rotation": 100}}

        with self.assertRaises(rot.RotationError) as raised:
            rot.RotationThresholds.from_controller_config(FakeConfig())
        self.assertEqual(raised.exception.code, "threshold_order")

    def test_context_rotation_threshold_defaults_to_400000(self) -> None:
        # D-004-R743: the context-token rotation threshold defaults to 400000.
        self.assertEqual(rot.RotationThresholds().context_rotation_threshold, 400_000)

    def test_context_rotation_threshold_is_configurable(self) -> None:
        # D-004-R744: it reads from [rotation] in the immutable controller config.
        class FakeConfig:
            raw = {"rotation": {"context_rotation_threshold": 123_456}}

        thresholds = rot.RotationThresholds.from_controller_config(FakeConfig())
        self.assertEqual(thresholds.context_rotation_threshold, 123_456)

    def test_context_rotation_threshold_rejects_a_non_positive_value(self) -> None:
        class FakeConfig:
            raw = {"rotation": {"context_rotation_threshold": 0}}

        with self.assertRaises(rot.RotationError):
            rot.RotationThresholds.from_controller_config(FakeConfig())


# --------------------------------------------------------------------------
# S11.2 - the finish-the-current-unit invariant
# --------------------------------------------------------------------------


class FinishCurrentUnitTests(JournalTestBase):
    def test_mid_unit_threshold_sets_pending_without_terminating(self) -> None:
        outcome = rot.observe_mid_unit(self.journal, reason_code="context_pressure",
                                       detail="0.82 of the reported window")
        self.assertTrue(outcome.rotation_pending)
        self.assertTrue(outcome.unit_continues)
        self.assertTrue(rot.rotation_pending(self.journal))
        self.assertFalse(hasattr(outcome, "terminate"),
                         "the mid-unit outcome type must not even be able to say "
                         "'terminate'")

    def test_rotation_pending_survives_a_process_restart(self) -> None:
        rot.observe_mid_unit(self.journal, reason_code="cumulative_usage")
        self.journal.close()
        reopened = DurableJournal(self.runtime / "journal.sqlite3").open()
        self.addCleanup(reopened.close)
        self.assertTrue(rot.rotation_pending(reopened))

    def test_pressure_reasons_may_never_interrupt(self) -> None:
        for reason in rot.PRESSURE_REASONS:
            with self.subTest(reason=reason):
                with self.assertRaises(rot.RotationError) as raised:
                    rot.may_interrupt_in_flight(reason)
                self.assertEqual(raised.exception.code, "pressure_may_not_interrupt")

    def test_the_five_permitted_interrupts(self) -> None:
        for reason in rot.INTERRUPT_PERMITTED_REASONS:
            with self.subTest(reason=reason):
                self.assertTrue(rot.may_interrupt_in_flight(reason))

    def test_an_unlisted_reason_does_not_permit_interruption(self) -> None:
        self.assertFalse(rot.may_interrupt_in_flight("the model asked nicely"))

    def test_interrupt_reasons_are_not_accepted_as_rotation_signals(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            rot.observe_mid_unit(self.journal, reason_code="owner_emergency_stop")
        self.assertEqual(raised.exception.code, "not_a_pressure_signal")

    def test_bounds_may_not_be_extended_in_flight(self) -> None:
        original = rot.UnitBounds(max_turns=8, wall_seconds=900.0, max_processes=8,
                                  max_output_bytes=1_000_000)
        with self.assertRaises(rot.RotationError) as raised:
            rot.assert_bounds_unchanged(original,
                                        rot.UnitBounds(12, 900.0, 8, 1_000_000))
        self.assertEqual(raised.exception.code, "bounds_extended_in_flight")

    def test_bounds_may_not_be_narrowed_in_flight_either(self) -> None:
        original = rot.UnitBounds(8, 900.0, 8, 1_000_000)
        with self.assertRaises(rot.RotationError) as raised:
            rot.assert_bounds_unchanged(original, rot.UnitBounds(4, 900.0, 8, 1_000_000))
        self.assertEqual(raised.exception.code, "bounds_changed_in_flight")

    def test_identical_bounds_are_accepted(self) -> None:
        bounds = rot.UnitBounds(8, 900.0, 8, 1_000_000)
        rot.assert_bounds_unchanged(bounds, bounds)

    def test_provider_abort_is_recorded_incomplete(self) -> None:
        record = rot.record_provider_abort(self.journal, unit_id="u-1",
                                           detail="provider closed the stream")
        self.assertEqual(record["outcome"], "INCOMPLETE")
        self.assertTrue(record["requires_recovery"])
        stored = self.journal.get_state(rot.PROVIDER_ABORT_KEY)
        self.assertEqual(stored["outcome"], "INCOMPLETE")


class MidUnitStateMachineTests(JournalTestBase):
    """The state machine's own view of S11.2: flag, finish, THEN rotate."""

    def setUp(self) -> None:
        super().setUp()
        self.machine = StateMachine(self.journal, self.audit, run_id="run-rotation")
        self.journal.set_state("current_state", CLAUDE_RUNNING)

    def test_threshold_crossed_mid_unit_goes_to_rotation_pending_not_stopped(self) -> None:
        result = self.machine.transition(ROTATION_PENDING, "rotation_threshold_crossed")
        self.assertTrue(result.applied)
        self.assertEqual(self.machine.current_state, ROTATION_PENDING)

    def test_the_in_flight_unit_still_reaches_a_terminal_checkpoint(self) -> None:
        self.machine.transition(ROTATION_PENDING, "rotation_threshold_crossed")
        self.machine.transition(CHECKPOINT_RECEIVED, "unit_reached_terminal_checkpoint")
        self.assertEqual(self.machine.current_state, CHECKPOINT_RECEIVED)

    def test_emergency_stop_still_terminates_a_pending_rotation(self) -> None:
        self.machine.transition(ROTATION_PENDING, "rotation_threshold_crossed")
        self.machine.transition(EMERGENCY_STOPPED, "owner_emergency_stop")
        self.assertEqual(self.machine.current_state, EMERGENCY_STOPPED)


# --------------------------------------------------------------------------
# S11.3 - the safe rotation protocol
# --------------------------------------------------------------------------


class UnsafeMomentTests(unittest.TestCase):
    def test_a_quiet_moment_is_safe(self) -> None:
        rot.assert_safe_to_rotate(rot.RotationSafetyState())

    def test_every_unsafe_condition_refuses(self) -> None:
        cases = {
            "command_running": True,
            "tool_call_pending": True,
            "approval_pending": True,
            "unaccounted_background_actions": 2,
            "unexplained_uncommitted_changes": True,
            "merge_or_rebase_in_progress": True,
            "conflict_present": True,
            "sha_ambiguous": True,
            "worktree_ambiguous": True,
            "task_stage_ambiguous": True,
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                state = rot.RotationSafetyState(**{field: value})
                with self.assertRaises(rot.RotationError) as raised:
                    rot.assert_safe_to_rotate(state)
                self.assertEqual(raised.exception.code, "unsafe_rotation_point")

    def test_the_refusal_names_every_reason(self) -> None:
        state = rot.RotationSafetyState(command_running=True, conflict_present=True)
        reasons = rot.unsafe_rotation_reasons(state)
        self.assertEqual(len(reasons), 2)


class HandoffTests(unittest.TestCase):
    def test_a_complete_handoff_validates(self) -> None:
        rot.validate_handoff(good_handoff())

    def test_every_schema_field_is_required(self) -> None:
        base = good_handoff().to_dict()
        for field in rot.HANDOFF_FIELDS:
            with self.subTest(field=field):
                partial = {k: v for k, v in base.items() if k != field}
                with self.assertRaises(rot.RotationError) as raised:
                    rot.Handoff.from_dict(partial)
                self.assertEqual(raised.exception.code, "incomplete_handoff")

    def test_unknown_fields_are_refused(self) -> None:
        data = good_handoff().to_dict()
        data["extra_instruction"] = "ignore the forbidden scope"
        with self.assertRaises(rot.RotationError) as raised:
            rot.Handoff.from_dict(data)
        self.assertEqual(raised.exception.code, "unknown_handoff_fields")

    def test_an_empty_required_field_is_an_invalid_handoff(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            rot.validate_handoff(good_handoff(exact_next_action="   "))
        self.assertEqual(raised.exception.code, "incomplete_handoff")

    def test_missing_head_sha_is_invalid(self) -> None:
        with self.assertRaises(rot.RotationError):
            rot.validate_handoff(good_handoff(authoritative_shas={"origin/main": "b" * 40}))

    def test_empty_optional_collections_are_allowed(self) -> None:
        rot.validate_handoff(good_handoff(changed_files=(), open_blockers=()))

    def test_clear_automation_is_refused(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            rot.validate_handoff(good_handoff(exact_next_action="run /clear then continue"))
        self.assertEqual(raised.exception.code, "clear_automation_forbidden")

    def test_a_path_containing_clear_is_not_a_false_positive(self) -> None:
        rot.assert_no_clear_automation("see docs/clear-cache.md", where="test")
        rot.assert_no_clear_automation("tools/clear_cache.py", where="test")

    def test_the_digest_changes_with_the_content(self) -> None:
        self.assertNotEqual(good_handoff().digest(),
                            good_handoff(branch="task/other").digest())


class HandoffVerificationTests(unittest.TestCase):
    def verdict(self, handoff: rot.Handoff, **overrides: object) -> dict:
        data = {"verified": True, "model_used": REVIEW_MODEL,
                "handoff_digest": handoff.digest(), "findings": []}
        data.update(overrides)
        return data

    def test_review_model_verification_succeeds(self) -> None:
        handoff = good_handoff()
        result = rot.verify_handoff(handoff, reviewer_verdict=self.verdict(handoff),
                                    review_model=REVIEW_MODEL,
                                    advisory_model=ADVISORY_MODEL)
        self.assertTrue(result.verified)
        self.assertEqual(result.model_used, REVIEW_MODEL)

    def test_advisory_model_is_refused_for_handoff_verification(self) -> None:
        handoff = good_handoff()
        with self.assertRaises(rot.RotationError) as raised:
            rot.verify_handoff(handoff,
                               reviewer_verdict=self.verdict(handoff,
                                                             model_used=ADVISORY_MODEL),
                               review_model=REVIEW_MODEL, advisory_model=ADVISORY_MODEL)
        self.assertEqual(raised.exception.code, "advisory_model_forbidden")

    def test_the_advisory_role_is_refused_outright(self) -> None:
        handoff = good_handoff()
        with self.assertRaises(rot.RotationError) as raised:
            rot.verify_handoff(handoff, reviewer_verdict=self.verdict(handoff),
                               review_model=REVIEW_MODEL, role="advisory")
        self.assertEqual(raised.exception.code, "advisory_model_forbidden")

    def test_an_unexpected_verifier_model_is_refused(self) -> None:
        handoff = good_handoff()
        with self.assertRaises(rot.RotationError) as raised:
            rot.verify_handoff(handoff,
                               reviewer_verdict=self.verdict(handoff,
                                                             model_used="something-else"),
                               review_model=REVIEW_MODEL)
        self.assertEqual(raised.exception.code, "unexpected_verifier_model")

    def test_a_codex_rejection_is_not_verified(self) -> None:
        handoff = good_handoff()
        result = rot.verify_handoff(
            handoff,
            reviewer_verdict=self.verdict(handoff, verified=False,
                                          findings=["the SHA does not match the remote"]),
            review_model=REVIEW_MODEL)
        self.assertFalse(result.verified)
        self.assertEqual(result.reason_code, "handoff_rejected")

    def test_findings_block_verification_even_when_verified_is_true(self) -> None:
        handoff = good_handoff()
        result = rot.verify_handoff(
            handoff, reviewer_verdict=self.verdict(handoff, findings=["stale packet"]),
            review_model=REVIEW_MODEL)
        self.assertFalse(result.verified)

    def test_verifying_a_different_handoff_is_a_digest_mismatch(self) -> None:
        handoff = good_handoff()
        other = good_handoff(branch="task/other")
        result = rot.verify_handoff(
            handoff, reviewer_verdict=self.verdict(handoff,
                                                   handoff_digest=other.digest()),
            review_model=REVIEW_MODEL)
        self.assertFalse(result.verified)
        self.assertEqual(result.reason_code, "digest_mismatch")

    def test_an_invalid_handoff_never_reaches_verification(self) -> None:
        with self.assertRaises(rot.RotationError):
            rot.verify_handoff(good_handoff(completed_work=""),
                               reviewer_verdict={"verified": True,
                                                 "model_used": REVIEW_MODEL},
                               review_model=REVIEW_MODEL)


class RotationLedgerTests(JournalTestBase):
    def setUp(self) -> None:
        super().setUp()
        self.ledger = rot.RotationLedger(self.journal, audit=self.audit)
        self.handoff = good_handoff()
        self.verification = rot.HandoffVerification(
            True, REVIEW_MODEL, "primary", "handoff_verified", "ok",
            self.handoff.digest())

    def test_only_a_verified_handoff_is_stored(self) -> None:
        rejected = rot.HandoffVerification(False, REVIEW_MODEL, "primary",
                                           "handoff_rejected", "no")
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.store_verified_handoff(self.handoff, rejected)
        self.assertEqual(raised.exception.code, "unverified_handoff")

    def test_storing_records_the_digest_and_the_model(self) -> None:
        record = self.ledger.store_verified_handoff(self.handoff, self.verification)
        self.assertEqual(record["handoff_digest"], self.handoff.digest())
        self.assertEqual(record["verified_by_model"], REVIEW_MODEL)
        self.assertEqual(self.ledger.stored_handoff()["handoff_digest"],
                         self.handoff.digest())

    def test_a_rotation_record_key_is_always_new_and_never_looks_like_a_session(self) -> None:
        # M0-T080: this used to be `new_session_id`, which minted `sup-<uuid4>` and
        # was stored where the NEW SESSION's identity belonged - an id no provider
        # had ever issued. It is now named for what it is (supervisor-internal
        # bookkeeping) and carries a prefix that can never be mistaken for a
        # provider session id, and `ClaudeRunner.with_resume` refuses one outright.
        first = rot.new_rotation_record_key()
        self.assertNotEqual(first, rot.new_rotation_record_key(first))
        self.assertTrue(first.startswith("sup-rot-"))
        self.assertFalse(hasattr(rot, "new_session_id"),
                         "the old name must be gone, not aliased: an alias would let a "
                         "caller keep minting a fake session identity")

    def test_there_is_exactly_one_ready_gate_and_it_is_the_live_one(self) -> None:
        # M0-T080 correction U4. `RotationLedger.assert_ready_checkpoint` used to
        # live here with three tests of its own, but it had ZERO production
        # callers, its docstring falsely claimed `turnover_seam.SeamTurnover` as
        # one, and it DISAGREED with the live gate: it demanded
        # `claude_session_id == expected_session_id`, unsatisfiable on a
        # reorientation because the successor's provider id does not exist until
        # the successor reports it. Two gates that disagree are worse than one.
        # The dead duplicate is gone; the live gate is covered by
        # `test_agent_supervisor_turnover_live_seam.py::SeamTurnoverTests`.
        self.assertFalse(hasattr(self.ledger, "assert_ready_checkpoint"),
                         "the dead duplicate READY gate must not come back as a decoy")
        from tools.agent_supervisor import turnover_seam as ts
        self.assertTrue(callable(getattr(ts.SeamTurnover, "require_ready", None)),
                        "the live READY gate is SeamTurnover.require_ready")

    def test_an_archived_session_is_never_resumed(self) -> None:
        self.ledger.archive_session("old-1", reason="rotation")
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.assert_not_archived("old-1")
        self.assertEqual(raised.exception.code, "archived_session_resume")
        self.ledger.assert_not_archived("new-1")

    def test_completing_a_rotation_archives_and_clears_pending(self) -> None:
        rot.observe_mid_unit(self.journal, reason_code="context_pressure")
        self.assertTrue(rot.rotation_pending(self.journal))
        record = self.ledger.complete_rotation(
            previous_provider_session_id="old-1",
            rotation_record_key="sup-rot-abc",
            handoff_digest=self.handoff.digest(),
            continuity_mode="reorientation",
            provider_session_none_reason="cross_model")
        self.assertFalse(rot.rotation_pending(self.journal))
        self.assertIn("old-1", self.ledger.archived_sessions())
        self.assertEqual(record["tier"], "NOTIFY")
        # M0-T080: BOTH identities are on the record, and the internal key is
        # never archived as though it were a session.
        self.assertEqual(record["previous_provider_session_id"], "old-1")
        self.assertEqual(record["rotation_record_key"], "sup-rot-abc")
        self.assertEqual(record["provider_session_id"], "")
        self.assertEqual(record["provider_session_none_reason"], "cross_model")
        self.assertNotIn("sup-rot-abc", self.ledger.archived_sessions())

    def test_a_resume_names_the_session_and_does_not_archive_it(self) -> None:
        # A rotation recorded as a RESUME continues the same provider session, so
        # archiving it would make the very resume being recorded illegal (S15).
        record = self.ledger.complete_rotation(
            previous_provider_session_id="prov-1",
            rotation_record_key="sup-rot-xyz",
            handoff_digest=self.handoff.digest(),
            continuity_mode="resume",
            provider_session_id="prov-1")
        self.assertEqual(record["continuity_mode"], "resume")
        self.assertEqual(record["provider_session_id"], "prov-1")
        self.assertNotIn("prov-1", self.ledger.archived_sessions())
        self.ledger.assert_not_archived("prov-1")

    def test_a_resume_with_no_provider_session_id_is_refused(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.complete_rotation(
                previous_provider_session_id="prov-1",
                rotation_record_key="sup-rot-xyz", handoff_digest="d",
                continuity_mode="resume")
        self.assertEqual(raised.exception.code, "resume_without_provider_session")

    def test_a_reorientation_must_say_why_resume_was_impossible(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.complete_rotation(
                previous_provider_session_id="prov-1",
                rotation_record_key="sup-rot-xyz", handoff_digest="d",
                continuity_mode="reorientation")
        self.assertEqual(raised.exception.code, "reorientation_without_reason")

    def test_resuming_an_archived_session_is_refused_at_completion(self) -> None:
        self.ledger.archive_session("prov-1", reason="an earlier rotation")
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.complete_rotation(
                previous_provider_session_id="prov-1",
                rotation_record_key="sup-rot-xyz", handoff_digest="d",
                continuity_mode="resume", provider_session_id="prov-1")
        self.assertEqual(raised.exception.code, "archived_session_resume")

    def test_the_internal_key_may_never_equal_the_provider_session_id(self) -> None:
        # M0-T080 replacement for the old "a rotation that reuses the session id is
        # refused": the two values are different KINDS of identity now, so holding
        # the same value is a conflation, not merely a non-rotation.
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.complete_rotation(
                previous_provider_session_id="s-1", rotation_record_key="s-1",
                handoff_digest="d", continuity_mode="reorientation",
                provider_session_none_reason="cross_model")
        self.assertEqual(raised.exception.code, "identity_conflated")

    def test_an_unknown_continuity_mode_is_refused(self) -> None:
        with self.assertRaises(rot.RotationError) as raised:
            self.ledger.complete_rotation(
                previous_provider_session_id="s-1", rotation_record_key="sup-rot-1",
                handoff_digest="d", continuity_mode="probably-resumed")
        self.assertEqual(raised.exception.code, "unknown_continuity_mode")

    def test_export_payload_requires_a_ready_first_response(self) -> None:
        payload = rot.export_handoff_payload(self.handoff, self.verification,
                                             rotation_record_key="sup-rot-1",
                                             evidence=("packet-1",))
        self.assertEqual(payload["rotation_record_key"], "sup-rot-1")
        # M0-T080: the payload must NOT claim a new session id. The successor's
        # provider session identity does not exist until the provider issues it.
        self.assertNotIn("new_session_id", payload)
        self.assertIn("READY", payload["required_first_response"])
        self.assertEqual(payload["handoff_digest"], self.handoff.digest())

    def test_export_refuses_clear_automation(self) -> None:
        handoff = good_handoff(exact_next_action="continue")
        payload = rot.export_handoff_payload(handoff, self.verification,
                                             rotation_record_key="sup-rot-1")
        self.assertNotIn("/clear", str(payload))


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
