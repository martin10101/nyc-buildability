#!/usr/bin/env python3
"""M0-T054: deterministic tests for the Fable->Opus turnover DETECTION core.

Qualifying evidence (supervisor-freeze §2, AD-093): the reproduced provider
incident D-010 source-028 / R289 - Fable 5 hard-stopped at its weekly usage limit
with the exact message "You've reached your Fable 5 limit. Run /usage-credits to
continue or switch models with /model." and the built-in fallbackModel did NOT
auto-switch.

These tests pin the classifier CONTRACT: only a grounded, unambiguous Fable
usage-limit signal returns FABLE_EXHAUSTED; every unknown, insufficient,
contradictory, or merely limit-*looking* input fails closed to
AMBIGUOUS_FAIL_CLOSED and never guesses exhaustion. The module is pure detection:
these tests launch no process and make no live provider call.
"""
from __future__ import annotations

import unittest

from tools.agent_supervisor.model_turnover import (
    ExhaustionClassification,
    ExhaustionVerdict,
    TurnoverEvidence,
    classify_exhaustion,
)

#: The verbatim incident message (D-010 source-028 / R289).
_INCIDENT_MESSAGE = (
    "You've reached your Fable 5 limit. Run /usage-credits to continue or switch "
    "models with /model.")


class ConfirmedExhaustionTests(unittest.TestCase):
    """A grounded, unambiguous signal - and only that - returns FABLE_EXHAUSTED."""

    def _assert_exhausted(self, evidence: TurnoverEvidence) -> None:
        verdict = classify_exhaustion(evidence)
        self.assertIsInstance(verdict, ExhaustionVerdict)
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.FABLE_EXHAUSTED)
        self.assertTrue(verdict.should_turn_over)
        self.assertTrue(verdict.reason)

    def test_exact_incident_message_contraction(self) -> None:
        """The verbatim R289 message (ASCII "You've") -> FABLE_EXHAUSTED."""
        self._assert_exhausted(
            TurnoverEvidence(stderr=_INCIDENT_MESSAGE, exit_code=1))

    def test_expanded_apostrophe_variant(self) -> None:
        """The "You have reached your Fable 5 limit" variant -> FABLE_EXHAUSTED."""
        self._assert_exhausted(
            TurnoverEvidence(
                stderr="You have reached your Fable 5 limit. Run /usage-credits.",
                exit_code=1))

    def test_typographic_apostrophe_variant(self) -> None:
        """A curly U+2019 apostrophe is normalized before matching."""
        curly = "You" + chr(0x2019) + "ve reached your Fable 5 limit."
        self._assert_exhausted(TurnoverEvidence(stderr=curly, exit_code=1))

    def test_message_on_stdout_is_also_recognized(self) -> None:
        self._assert_exhausted(
            TurnoverEvidence(stdout=_INCIDENT_MESSAGE, exit_code=None))

    def test_structured_quota_result_with_model_field(self) -> None:
        """A typed quota code whose result names the Fable model -> FABLE_EXHAUSTED."""
        self._assert_exhausted(
            TurnoverEvidence(
                structured_result={"type": "usage_limit_reached",
                                   "model": "claude-fable-5"},
                exit_code=1))

    def test_structured_quota_result_attributed_via_model_id(self) -> None:
        """A typed quota code + evidence.model_id naming Fable -> FABLE_EXHAUSTED."""
        self._assert_exhausted(
            TurnoverEvidence(
                structured_result={"code": "quota_exhausted"},
                model_id="claude-fable-5",
                exit_code=None))

    def test_structured_nested_error_object(self) -> None:
        """A recognized code nested under `error` is still recognized."""
        self._assert_exhausted(
            TurnoverEvidence(
                structured_result={"error": {"type": "weekly_limit_reached"},
                                   "model": "claude-fable-5"},
                exit_code=1))


class NotExhaustedTests(unittest.TestCase):
    """Recognized non-exhaustion conditions -> NOT_EXHAUSTED (no turnover)."""

    def _assert_not_exhausted(self, evidence: TurnoverEvidence) -> None:
        verdict = classify_exhaustion(evidence)
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.NOT_EXHAUSTED)
        self.assertFalse(verdict.should_turn_over)
        self.assertTrue(verdict.reason)

    def test_normal_successful_completion(self) -> None:
        self._assert_not_exhausted(
            TurnoverEvidence(stdout="unit complete; checkpoint written",
                             exit_code=0))

    def test_ordinary_build_failure(self) -> None:
        """A plain compiler error with a non-zero exit -> NOT_EXHAUSTED."""
        self._assert_not_exhausted(
            TurnoverEvidence(
                stderr="error: expected ';' before '}' token\nmake: *** [build] Error 2",
                exit_code=2))

    def test_arbitrary_runtime_error(self) -> None:
        """An arbitrary traceback carries no exhaustion signal -> NOT_EXHAUSTED."""
        self._assert_not_exhausted(
            TurnoverEvidence(
                stderr="Traceback (most recent call last):\nValueError: boom",
                exit_code=1))

    def test_permission_denied(self) -> None:
        self._assert_not_exhausted(
            TurnoverEvidence(
                stderr="bash: /etc/secure: Permission denied", exit_code=126))


class AmbiguousFailClosedTests(unittest.TestCase):
    """Unknown, insufficient, contradictory, or limit-looking -> AMBIGUOUS."""

    def _assert_ambiguous(self, evidence: object) -> ExhaustionVerdict:
        verdict = classify_exhaustion(evidence)
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED)
        self.assertFalse(verdict.should_turn_over)
        self.assertTrue(verdict.reason)
        return verdict

    def test_bare_limit_word_is_ambiguous_never_exhausted(self) -> None:
        """A bare "limit" mention MUST be AMBIGUOUS, never FABLE_EXHAUSTED."""
        verdict = self._assert_ambiguous(
            TurnoverEvidence(stderr="some limit was hit while processing",
                             exit_code=1))
        self.assertNotEqual(verdict.classification,
                            ExhaustionClassification.FABLE_EXHAUSTED)

    def test_quota_word_without_confirmed_phrase_is_ambiguous(self) -> None:
        self._assert_ambiguous(
            TurnoverEvidence(stderr="quota warning issued", exit_code=1))

    def test_network_timeout_ambiguity(self) -> None:
        self._assert_ambiguous(
            TurnoverEvidence(
                stderr="curl: (28) Connection timed out after 30000 ms",
                exit_code=7))

    def test_contradictory_exhaustion_text_with_success_exit(self) -> None:
        """Exhaustion text + exit 0 is contradictory -> AMBIGUOUS, never exhausted."""
        verdict = self._assert_ambiguous(
            TurnoverEvidence(stderr=_INCIDENT_MESSAGE, exit_code=0))
        self.assertNotEqual(verdict.classification,
                            ExhaustionClassification.FABLE_EXHAUSTED)

    def test_structured_quota_code_with_success_exit_is_contradictory(self) -> None:
        self._assert_ambiguous(
            TurnoverEvidence(
                structured_result={"type": "usage_limit_reached",
                                   "model": "claude-fable-5"},
                exit_code=0))

    def test_quota_code_not_attributable_to_fable(self) -> None:
        """A recognized quota code with no Fable attribution -> AMBIGUOUS."""
        self._assert_ambiguous(
            TurnoverEvidence(
                structured_result={"code": "quota_exhausted"}, exit_code=1))

    def test_quota_code_for_a_different_model(self) -> None:
        self._assert_ambiguous(
            TurnoverEvidence(
                structured_result={"code": "quota_exhausted",
                                   "model": "claude-opus-4-8"},
                exit_code=1))

    def test_unknown_empty_evidence(self) -> None:
        self._assert_ambiguous(TurnoverEvidence())

    def test_no_signal_and_unknown_exit(self) -> None:
        self._assert_ambiguous(
            TurnoverEvidence(stdout="...working...", exit_code=None))


class RobustnessTests(unittest.TestCase):
    """The classifier is total: it never raises and never guesses exhaustion."""

    def test_none_evidence_is_ambiguous_never_raises(self) -> None:
        verdict = classify_exhaustion(None)
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED)

    def test_malformed_field_types_never_raise(self) -> None:
        """Non-str text, weird exit codes, and non-mapping results degrade safely."""
        cases = (
            TurnoverEvidence(stderr=12345, exit_code="weird"),  # type: ignore[arg-type]
            TurnoverEvidence(stdout=object(), exit_code=True),  # type: ignore[arg-type]
            TurnoverEvidence(structured_result=["not", "a", "mapping"]),  # type: ignore[arg-type]
            TurnoverEvidence(structured_result="usage_limit_reached"),  # type: ignore[arg-type]
        )
        for evidence in cases:
            with self.subTest(evidence=evidence):
                verdict = classify_exhaustion(evidence)
                self.assertIsInstance(verdict, ExhaustionVerdict)
                self.assertNotEqual(verdict.classification,
                                    ExhaustionClassification.FABLE_EXHAUSTED)

    def test_boolean_exit_code_is_treated_as_unknown(self) -> None:
        """A bool exit (an int subclass) is never read as success/failure."""
        # Confirmed phrase + bool exit -> not the success-contradiction path;
        # a bool is unknown, so a genuine signal still classifies as exhausted.
        verdict = classify_exhaustion(
            TurnoverEvidence(stderr=_INCIDENT_MESSAGE, exit_code=True))  # type: ignore[arg-type]
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.FABLE_EXHAUSTED)


class ContractTests(unittest.TestCase):
    """The typed result surface the callers depend on."""

    def test_enum_has_the_three_required_members(self) -> None:
        names = {member.name for member in ExhaustionClassification}
        self.assertLessEqual(
            {"FABLE_EXHAUSTED", "NOT_EXHAUSTED", "AMBIGUOUS_FAIL_CLOSED"}, names)

    def test_should_turn_over_only_true_for_exhaustion(self) -> None:
        self.assertTrue(
            ExhaustionVerdict(ExhaustionClassification.FABLE_EXHAUSTED, "x")
            .should_turn_over)
        self.assertFalse(
            ExhaustionVerdict(ExhaustionClassification.NOT_EXHAUSTED, "x")
            .should_turn_over)
        self.assertFalse(
            ExhaustionVerdict(ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED, "x")
            .should_turn_over)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
