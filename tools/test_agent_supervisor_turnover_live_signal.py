#!/usr/bin/env python3
"""M0-T054 increment 5: the REAL Fable exhaustion signal fires end to end.

Qualifying evidence (supervisor-freeze §2, AD-093): a *live proof*, not a
hypothetical. The orchestrator ran the real worker
``claude.exe --model claude-fable-5 -p ... --output-format stream-json`` while
Fable 5 was genuinely exhausted and captured its output under
``project-control/reports/M0-T054-live-proof/``. That proof exposed a REAL gap in
increment 4's integration seam: on a genuine weekly-limit hard-stop the exact
message

    You've reached your Fable 5 limit. Run /usage-credits to continue or switch
    models with /model.

surfaces as STRUCTURED stream-json events - a ``rate_limit_event`` with
``rateLimitType == "seven_day_overage_included"`` / ``status == "rejected"``, an
``assistant`` message flagged ``is_api_error_message``, and a terminal ``result``
with ``is_error`` / ``terminal_reason == "api_error"`` carrying the phrase - and
NOT on the worker's stderr (empty) or in ``checkpoint_error`` (a generic
no-checkpoint string). Increment 4 built the classifier's evidence only from
``checkpoint_error`` + ``stderr_tail``, so ``classify_exhaustion`` saw no phrase
and returned NOT_EXHAUSTED: the turnover NEVER fired on real exhaustion.

These tests use the REAL captured stream-json as the oracle. They parse it with the
runner's own ``ClaudeStreamParser``, reproduce the exact ``RunResult`` field values
``run_unit`` would set for that output (including the generic ``checkpoint_error``
that ``extract_checkpoint`` actually raises and the EMPTY ``stderr_tail``), and
prove that ``WorkerTurnoverIntegration.evaluate`` now yields a confirmed
FABLE_EXHAUSTED turnover end to end - while a transient per-minute 429 (no
seven_day/weekly marker, no phrase) stays fail-closed and a normal success never
triggers. No live provider call, no subprocess, no network.
"""
from __future__ import annotations

import pathlib
import sys
import unittest
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor.claude_runner import (  # noqa: E402
    ClaudeStreamParser,
    CheckpointError,
    RunResult,
    detect_exhaustion_evidence,
    extract_checkpoint,
)
from tools.agent_supervisor.model_turnover import (  # noqa: E402
    ExhaustionClassification,
    TurnoverEvidence,
    classify_exhaustion,
)
from tools.agent_supervisor.turnover_controller import (  # noqa: E402
    ALLOWED_SUCCESSOR_EFFORT,
    ApprovedSuccessor,
    TurnoverLayer,
)
from tools.agent_supervisor.worker_turnover import (  # noqa: E402
    REASON_TURNOVER_LAUNCHED,
    REASON_TURNOVER_RECORDED,
    WorkerTurnoverIntegration,
)

# The gate-independent controller fakes are reused verbatim from the increment-4
# integration test so this proof drives the SAME real controller/launcher stack.
from tools.test_agent_supervisor_turnover_integration import (  # noqa: E402
    build_controller,
    _authorized,
)

#: The exact captured live proof (D-010 source-028 / R289).
LIVE_PROOF = (REPO / "project-control" / "reports" / "M0-T054-live-proof"
              / "real-fable-exhaustion-streamjson.txt")

FABLE_PHRASE = "You've reached your Fable 5 limit"


def _config() -> Any:
    from tools.agent_supervisor import loop as lp
    return lp.LoopConfig(mode="supervised", task_id="M0-T054", stage="phase4",
                         max_cycles=4)


def _parse_events(text: str) -> list[dict[str, Any]]:
    """Feed the captured stream-json through the runner's own parser."""
    parser = ClaudeStreamParser()
    events: list[dict[str, Any]] = []
    for chunk in text.splitlines(keepends=True):
        events.extend(parser.feed(chunk))
    events.extend(parser.close())
    return events


def _run_result_like_runner(events: list[dict[str, Any]], *,
                            returncode: int = 1) -> RunResult:
    """Build the RunResult ``run_unit`` would produce for these events.

    Mirrors the post-loop assembly in ``run_unit``: ``extract_checkpoint`` is run to
    obtain the exact (generic) ``checkpoint_error``, ``stderr_tail`` is EMPTY (the
    exhaustion rides stdout, never stderr), and ``result_text`` /
    ``rate_limit_rejection`` come from ``detect_exhaustion_evidence`` over the SAME
    event list.
    """
    checkpoint_error = ""
    try:
        extract_checkpoint(events)
    except CheckpointError as exc:
        checkpoint_error = f"{exc.code}: {exc.message}"
    result_text, rate_limit_rejection = detect_exhaustion_evidence(events)
    return RunResult(
        argv=("claude", "--model", "claude-fable-5"),
        returncode=returncode,
        duration_seconds=1.0,
        session_id="cbdd293d-8062-46d4-95c5-09255a285c45",
        events=len(events),
        checkpoint=None,
        checkpoint_error=checkpoint_error,
        stderr_tail="",
        raw_events=tuple(events),
        result_text=result_text,
        rate_limit_rejection=rate_limit_rejection,
    )



# --------------------------------------------------------------------------
# M0-T080 (D-023-R013): the successor is no longer a module constant in the
# production code. `ALLOWED_SUCCESSOR_MODEL_ID = "claude-opus-4-8"` is GONE,
# because a model id living in the source is a selection the owner never
# approved and no launch probe ever proved. `TurnoverController` now takes an
# injected resolver that names the next OWNER-APPROVED, live-probed model, so
# these tests state the approved chain THEMSELVES and assert the launch used
# that id - a strictly stronger claim than "it equals the constant the code
# also reads", which could not fail even if the id were wrong.
# --------------------------------------------------------------------------

#: The owner-approved chain these tests pretend the protected config declares.
APPROVED_CHAIN: tuple[str, ...] = ("claude-fable-5", "claude-opus-4-8")
#: The entry after the exhausted Fable model - what the resolver must pick.
APPROVED_SUCCESSOR = "claude-opus-4-8"


def _approved_successor(_context: object) -> ApprovedSuccessor:
    """A `SuccessorResolver` standing in for the approved + live-probed selection."""
    return ApprovedSuccessor(
        model_id=APPROVED_SUCCESSOR, effort=ALLOWED_SUCCESSOR_EFFORT,
        probed_at_utc="2026-08-21T00:00:00+00:00",
        config_identity="test-config-identity", cli_version="test-cli-version")

class LiveProofDistillationTests(unittest.TestCase):
    """The runner-side gatherer distills exactly what the classifier needs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = LIVE_PROOF.read_text(encoding="utf-8")
        cls.events = _parse_events(cls.text)

    def test_fixture_present_and_parses(self) -> None:
        self.assertTrue(LIVE_PROOF.exists(), f"missing live proof: {LIVE_PROOF}")
        self.assertGreaterEqual(len(self.events), 5)

    def test_the_gap_stderr_and_checkpoint_error_lack_the_phrase(self) -> None:
        # The precise reason increment 4 was blind: the phrase is NOT on stderr and
        # NOT in the checkpoint error - only in the stream events.
        rr = _run_result_like_runner(self.events)
        self.assertEqual(rr.stderr_tail, "")
        self.assertNotIn(FABLE_PHRASE, rr.checkpoint_error)
        self.assertIn("missing_checkpoint", rr.checkpoint_error)

    def test_distills_phrase_and_weekly_rejection(self) -> None:
        result_text, rejection = detect_exhaustion_evidence(self.events)
        self.assertIn(FABLE_PHRASE, result_text)
        self.assertIsNotNone(rejection)
        assert rejection is not None
        self.assertEqual(rejection.get("status"), "rejected")
        self.assertIn("seven_day", str(rejection.get("rateLimitType", "")))
        # The running model was attached for attribution.
        self.assertIn("fable", str(rejection.get("model_id", "")).lower())

    def test_classifier_confirms_on_distilled_evidence(self) -> None:
        result_text, rejection = detect_exhaustion_evidence(self.events)
        verdict = classify_exhaustion(TurnoverEvidence(
            stdout=result_text, exit_code=1,
            structured_result=rejection, model_id="claude-fable-5"))
        self.assertEqual(verdict.classification,
                         ExhaustionClassification.FABLE_EXHAUSTED)


class LiveProofSeamTests(unittest.TestCase):
    """End to end through the integration seam on the REAL captured signal."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.events = _parse_events(LIVE_PROOF.read_text(encoding="utf-8"))

    def test_real_exhaustion_triggers_and_actuates(self) -> None:
        controller, launcher, audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = _run_result_like_runner(self.events)
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=_config(),
            run_id="run-live", cycle=1, safe_checkpoint_id="cp-safe")

        self.assertTrue(decision.triggered)
        self.assertTrue(decision.actuated)
        self.assertEqual(decision.reason_code, REASON_TURNOVER_LAUNCHED)
        self.assertEqual(len(launcher.calls), 1)
        self.assertEqual(launcher.calls[0].layer, TurnoverLayer.WORKER)
        self.assertEqual(launcher.calls[0].model_id, APPROVED_SUCCESSOR)
        self.assertEqual(len(audit.launched_records()), 1)

    def test_real_exhaustion_triggers_recorded_when_unauthorized(self) -> None:
        # Default (fail-closed) authorization: still TRIGGERED on the real signal,
        # recorded and surfaced, but not auto-run (supervised gating preserved).
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller)  # default gate
        rr = _run_result_like_runner(self.events)
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=_config(),
            run_id="run-live", cycle=1)

        self.assertTrue(decision.triggered)
        self.assertFalse(decision.actuated)
        self.assertEqual(decision.reason_code, REASON_TURNOVER_RECORDED)
        self.assertEqual(len(launcher.calls), 0)

    def test_pre_fix_shape_would_not_trigger(self) -> None:
        # Proves the gap was real AND that the new fields are what flip it: the SAME
        # failed unit, but with result_text/rate_limit_rejection absent (increment
        # 4's shape - only checkpoint_error + empty stderr), does NOT trigger.
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = _run_result_like_runner(self.events)
        pre_fix = RunResult(
            argv=rr.argv, returncode=rr.returncode, duration_seconds=1.0,
            session_id=rr.session_id, checkpoint=None,
            checkpoint_error=rr.checkpoint_error, stderr_tail="",
            result_text="", rate_limit_rejection=None)
        decision = integration.evaluate(
            pre_fix, current_model="claude-fable-5", config=_config(),
            run_id="run-live", cycle=1)

        self.assertFalse(decision.triggered)
        self.assertEqual(len(launcher.calls), 0)


class FailClosedTransientTests(unittest.TestCase):
    """A transient per-minute 429 must stay fail-closed - never a turnover."""

    def _transient_result(self) -> RunResult:
        # A transient throttle: a rejected rate-limit event WITHOUT any seven_day /
        # weekly marker, and result text WITHOUT the exact phrase.
        return RunResult(
            argv=("claude", "--model", "claude-fable-5"), returncode=1,
            duration_seconds=1.0, session_id="sess-transient", checkpoint=None,
            checkpoint_error="missing_checkpoint: the run produced no structured "
                             "checkpoint",
            stderr_tail="",
            result_text="API Error: 429 rate limit exceeded, please retry shortly.",
            rate_limit_rejection={"status": "rejected",
                                  "rateLimitType": "requests_per_minute",
                                  "model_id": "claude-fable-5"})

    def test_transient_429_not_triggered(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        decision = integration.evaluate(
            self._transient_result(), current_model="claude-fable-5",
            config=_config(), run_id="run-x", cycle=1)

        self.assertFalse(decision.triggered)
        self.assertEqual(decision.verdict.classification,
                         ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED)
        self.assertEqual(len(launcher.calls), 0)

    def test_weekly_structured_signal_alone_triggers(self) -> None:
        # The structured weekly-rejection path is independently sufficient: even with
        # NO phrase text, a seven_day rejected rate-limit attributed to Fable is a
        # grounded exhaustion.
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        rr = RunResult(
            argv=("claude",), returncode=1, duration_seconds=1.0,
            session_id="sess-weekly", checkpoint=None,
            checkpoint_error="missing_checkpoint: no structured checkpoint",
            stderr_tail="", result_text="",
            rate_limit_rejection={"status": "rejected",
                                  "rateLimitType": "seven_day_overage_included",
                                  "model_id": "claude-fable-5"})
        decision = integration.evaluate(
            rr, current_model="claude-fable-5", config=_config(),
            run_id="run-w", cycle=1)

        self.assertTrue(decision.triggered)
        self.assertEqual(decision.verdict.classification,
                         ExhaustionClassification.FABLE_EXHAUSTED)

    def test_normal_success_not_triggered(self) -> None:
        controller, launcher, _audit = build_controller()
        integration = WorkerTurnoverIntegration(controller=controller,
                                                authorize=_authorized)
        ok = RunResult(argv=("claude",), returncode=0, duration_seconds=0.1,
                       session_id="sess-ok", result_text="", rate_limit_rejection=None)
        decision = integration.evaluate(
            ok, current_model="claude-fable-5", config=_config(),
            run_id="run-ok", cycle=1)

        self.assertFalse(decision.triggered)
        self.assertEqual(len(launcher.calls), 0)


if __name__ == "__main__":
    unittest.main()
