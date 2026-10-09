#!/usr/bin/env python3
"""Independent Claude reviewer tests (owner directive D-091 T5).

Covers every M0-T168 acceptance scenario with NO live provider call - the Claude
executable is never launched; a fake ``runner`` callable returns a controlled
``ProcessResult``. The tests prove:

* primary: the read-only argv (``--permission-mode plan``, pinned allowlisted
  ``--model``, no write/edit/resume flag) and a verdict in the Codex reviewer's
  shape (``ReviewOutcome`` wrapping ``CodexDecision``);
* boundary: refusal when the reviewer identity equals the producer's, and when
  the packet is handed the Codex (or any peer) review;
* missing/ambiguous: a malformed or empty reviewer output is FAIL/UNVERIFIED
  (``decision is None``, ``ok`` False), never a proceed decision;
* failure: the switch defaults OFF and nothing in the loop references the module.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import claude_reviewer as cr  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewError, ReviewOutcome  # noqa: E402
from tools.agent_supervisor.models import CodexDecision  # noqa: E402
from tools.agent_supervisor.process import ProcessResult  # noqa: E402

HEAD = "a" * 40
OTHER_HEAD = "b" * 40
ORIGIN_MAIN = "c" * 40
MODEL = "claude-reviewer-model"
ALLOWED = (MODEL, "claude-combiner-model")


def make_packet(head: str = HEAD, **extra_sections) -> dict:
    """A minimal evidence-packet-shaped mapping with a recorded git head."""
    sections = {"git": {"head": {"value": head, "digest": "d"}}}
    sections.update(extra_sections)
    return {"packet_version": "1", "task_id": "M0-T168",
            "checkpoint_id": "cp-1", "sections": sections}


def decision_dict(decision: str = "CONTINUE", head: str = HEAD, **over) -> dict:
    base = {
        "schema_version": "1.0.0",
        "decision": decision,
        "reviewed_task_id": "M0-T168",
        "reviewed_checkpoint_id": "cp-1",
        "verified_repo_head": head,
        "verified_origin_main": ORIGIN_MAIN,
        "model_used": MODEL,
        "next_claude_prompt": "proceed with the next bounded unit",
    }
    base.update(over)
    return base


class FakeRunner:
    """Injected in place of process.run - records argv/stdin, returns canned output."""

    def __init__(self, *, stdout: str = "", returncode: int = 0, timed_out: bool = False):
        self.stdout = stdout
        self.returncode = returncode
        self.timed_out = timed_out
        self.calls: list[dict] = []

    def __call__(self, argv, *, cwd=None, env=None, timeout=None, input_text=None):
        self.calls.append({"argv": list(argv), "cwd": cwd, "env": env,
                           "timeout": timeout, "input_text": input_text})
        return ProcessResult(
            argv=tuple(argv), returncode=self.returncode, stdout=self.stdout,
            stderr="", duration_seconds=0.0, timed_out=self.timed_out)


def make_reviewer(runner: FakeRunner, *, reviewer_identity="claude-reviewer",
                  model=MODEL, allowed=ALLOWED) -> cr.ClaudeReviewer:
    return cr.ClaudeReviewer(
        "claude", model=model, allowed_models=allowed,
        reviewer_identity=reviewer_identity, repo="/repo", runner=runner)


# --------------------------------------------------------------------------
# Scenario 1 (primary): read-only argv, allowlisted model, Codex verdict shape
# --------------------------------------------------------------------------


class PrimaryReadOnlyArgvTests(unittest.TestCase):
    def test_build_argv_is_read_only_and_pinned(self):
        argv = cr.build_argv("claude", model=MODEL)
        self.assertEqual(argv[0], "claude")
        self.assertIn("-p", argv)
        self.assertIn("--permission-mode", argv)
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "plan")
        self.assertIn("--model", argv)
        self.assertEqual(argv[argv.index("--model") + 1], MODEL)
        lowered = {t.lower() for t in argv}
        for forbidden in cr.FORBIDDEN_REVIEWER_FLAGS:
            self.assertNotIn(forbidden, lowered)
        # No write-enabling mode value appears anywhere in the argv.
        for mode in cr.WRITE_ENABLING_PERMISSION_MODES:
            self.assertNotIn(mode, lowered)

    def test_build_argv_refuses_write_enabling_mode(self):
        for mode in ("acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk"):
            with self.assertRaises(ReviewError) as ctx:
                cr.build_argv("claude", model=MODEL, permission_mode=mode)
            self.assertEqual(ctx.exception.code, "reviewer_must_be_read_only")

    def test_build_argv_refuses_empty_model(self):
        with self.assertRaises(ReviewError) as ctx:
            cr.build_argv("claude", model="")
        self.assertEqual(ctx.exception.code, "no_model")

    def test_review_returns_codex_decision_shape(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        outcome = make_reviewer(runner).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker",
            expected_task_id="M0-T168", expected_checkpoint_id="cp-1")
        self.assertIsInstance(outcome, ReviewOutcome)
        self.assertIsInstance(outcome.decision, CodexDecision)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.decision.decision, "CONTINUE")
        self.assertEqual(outcome.model_used, MODEL)
        self.assertFalse(outcome.error_code)
        # The argv the reviewer actually launched is the read-only one.
        self.assertIn("--permission-mode", runner.calls[0]["argv"])
        self.assertIn("plan", runner.calls[0]["argv"])

    def test_model_must_be_allowlisted(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        reviewer = make_reviewer(runner, model="not-allowlisted")
        with self.assertRaises(ReviewError) as ctx:
            reviewer.review(make_packet(), frozen_head=HEAD,
                            producer_identity="claude-worker")
        self.assertEqual(ctx.exception.code, "model_not_allowlisted")
        self.assertEqual(runner.calls, [])  # refused before any process

    def test_envelope_wrapped_decision_is_extracted(self):
        # A claude --output-format json style envelope carrying the decision as a
        # string value is still recovered without hard-coding the envelope schema.
        envelope = {"type": "result", "subtype": "success",
                    "result": json.dumps(decision_dict())}
        runner = FakeRunner(stdout=json.dumps(envelope))
        outcome = make_reviewer(runner).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker")
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.decision.decision, "CONTINUE")

    def test_stdin_carries_packet_not_a_codex_review(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        make_reviewer(runner).review(make_packet(), frozen_head=HEAD,
                                     producer_identity="claude-worker")
        stdin = runner.calls[0]["input_text"]
        self.assertIn("INDEPENDENT CLAUDE REVIEW INSTRUCTIONS", stdin)
        self.assertIn(HEAD, stdin)
        self.assertNotIn("codex_review", stdin)


# --------------------------------------------------------------------------
# Scenario 2 (boundary): identity == producer, or handed the Codex review
# --------------------------------------------------------------------------


class IndependenceRefusalTests(unittest.TestCase):
    def test_refuses_when_reviewer_is_the_producer(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        reviewer = make_reviewer(runner, reviewer_identity="claude-worker-7")
        with self.assertRaises(ReviewError) as ctx:
            reviewer.review(make_packet(), frozen_head=HEAD,
                            producer_identity="claude-worker-7")
        self.assertEqual(ctx.exception.code, "reviewer_is_producer")
        self.assertEqual(runner.calls, [])

    def test_refuses_codex_review_under_marker_key(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        packet = make_packet(codex_review={"decision": "COMPLETE"})
        with self.assertRaises(ReviewError) as ctx:
            make_reviewer(runner).review(packet, frozen_head=HEAD,
                                         producer_identity="claude-worker")
        self.assertEqual(ctx.exception.code, "codex_review_leaked")
        self.assertEqual(runner.calls, [])

    def test_refuses_codex_decision_shaped_object_any_key(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        # A Codex decision smuggled under an innocuous section key.
        packet = make_packet(notes=decision_dict(decision="COMPLETE"))
        with self.assertRaises(ReviewError) as ctx:
            make_reviewer(runner).review(packet, frozen_head=HEAD,
                                         producer_identity="claude-worker")
        self.assertEqual(ctx.exception.code, "codex_review_leaked")

    def test_refuses_codex_decision_under_value_wrapper(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        packet = make_packet(peer={"value": decision_dict(decision="COMPLETE")})
        with self.assertRaises(ReviewError):
            make_reviewer(runner).review(packet, frozen_head=HEAD,
                                         producer_identity="claude-worker")

    def test_last_supervisor_decision_does_not_false_trip(self):
        # The one legitimate decision-shaped context section is allowed through.
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        packet = make_packet(last_supervisor_decision={"value": decision_dict()})
        outcome = make_reviewer(runner).review(packet, frozen_head=HEAD,
                                               producer_identity="claude-worker")
        self.assertTrue(outcome.ok)


# --------------------------------------------------------------------------
# Scenario 2 (boundary) continued: head must be frozen + packet-confirmed
# --------------------------------------------------------------------------


class FrozenHeadTests(unittest.TestCase):
    def test_refuses_non_sha_frozen_head(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        for bad in ("HEAD", "main", "abc123", "a" * 39, ""):
            with self.assertRaises(ReviewError) as ctx:
                make_reviewer(runner).review(make_packet(bad), frozen_head=bad,
                                             producer_identity="claude-worker")
            self.assertEqual(ctx.exception.code, "head_not_frozen")
        self.assertEqual(runner.calls, [])

    def test_refuses_packet_head_mismatch(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        with self.assertRaises(ReviewError) as ctx:
            make_reviewer(runner).review(make_packet(OTHER_HEAD), frozen_head=HEAD,
                                         producer_identity="claude-worker")
        self.assertEqual(ctx.exception.code, "head_not_frozen")

    def test_refuses_packet_without_recorded_head(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict()))
        packet = {"sections": {}}  # no git head
        with self.assertRaises(ReviewError) as ctx:
            make_reviewer(runner).review(packet, frozen_head=HEAD,
                                         producer_identity="claude-worker")
        self.assertEqual(ctx.exception.code, "head_not_frozen")

    def test_decision_reviewing_a_different_head_is_not_pass(self):
        runner = FakeRunner(stdout=json.dumps(decision_dict(head=OTHER_HEAD)))
        outcome = make_reviewer(runner).review(make_packet(), frozen_head=HEAD,
                                               producer_identity="claude-worker")
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.decision)
        self.assertEqual(outcome.error_code, "reviewed_head_mismatch")


# --------------------------------------------------------------------------
# Scenario 3 (missing/ambiguous): malformed/empty output is FAIL/UNVERIFIED
# --------------------------------------------------------------------------


class FailClosedParseTests(unittest.TestCase):
    def _assert_not_pass(self, outcome: ReviewOutcome, code: str):
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.decision)
        self.assertEqual(outcome.error_code, code)

    def test_empty_output_is_not_pass(self):
        outcome = make_reviewer(FakeRunner(stdout="")).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker")
        self._assert_not_pass(outcome, "empty_review_output")

    def test_non_json_output_is_not_pass(self):
        outcome = make_reviewer(FakeRunner(stdout="I could not complete the review")).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker")
        self._assert_not_pass(outcome, "empty_review_output")

    def test_object_missing_required_fields_is_not_pass(self):
        outcome = make_reviewer(FakeRunner(stdout=json.dumps({"decision": "COMPLETE"}))).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker")
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.decision)
        self.assertTrue(outcome.error_code)

    def test_bad_decision_value_is_not_pass(self):
        outcome = make_reviewer(FakeRunner(stdout=json.dumps(decision_dict(decision="PASS")))).review(
            make_packet(), frozen_head=HEAD, producer_identity="claude-worker")
        self.assertFalse(outcome.ok)
        self.assertIsNone(outcome.decision)
        self.assertEqual(outcome.error_code, "bad_decision")

    def test_timeout_is_not_pass(self):
        runner = FakeRunner(stdout="", returncode=-1, timed_out=True)
        outcome = make_reviewer(runner).review(make_packet(), frozen_head=HEAD,
                                               producer_identity="claude-worker")
        self._assert_not_pass(outcome, "review_timeout")

    def test_extract_decision_payload_empty(self):
        self.assertIsNone(cr.extract_decision_payload(""))
        self.assertIsNone(cr.extract_decision_payload("   \n  "))
        self.assertIsNone(cr.extract_decision_payload("no json here"))


# --------------------------------------------------------------------------
# Scenario 4 (failure): switch defaults OFF; nothing in the loop changes
# --------------------------------------------------------------------------


class SwitchDefaultsOffTests(unittest.TestCase):
    def test_config_default_is_off(self):
        self.assertFalse(cr.ClaudeReviewerConfig().enabled)

    def test_enabled_only_for_real_bool_true(self):
        self.assertFalse(cr.claude_reviewer_enabled({}))
        self.assertFalse(cr.claude_reviewer_enabled({"claude": {}}))
        self.assertFalse(cr.claude_reviewer_enabled({"claude": {"reviewer_enabled": False}}))
        # A truthy string must NOT turn it on (fail closed).
        self.assertFalse(cr.claude_reviewer_enabled({"claude": {"reviewer_enabled": "true"}}))
        self.assertFalse(cr.claude_reviewer_enabled({"claude": {"reviewer_enabled": 1}}))
        self.assertTrue(cr.claude_reviewer_enabled({"claude": {"reviewer_enabled": True}}))

    def test_from_mapping_strict_and_fail_closed(self):
        self.assertFalse(cr.ClaudeReviewerConfig.from_mapping({}).enabled)
        self.assertFalse(
            cr.ClaudeReviewerConfig.from_mapping({"reviewer_enabled": "true"}).enabled)
        self.assertTrue(
            cr.ClaudeReviewerConfig.from_mapping({"reviewer_enabled": True}).enabled)
        with self.assertRaises(ReviewError):
            cr.ClaudeReviewerConfig.from_mapping({"bogus": 1})

    def test_loop_does_not_reference_the_claude_reviewer(self):
        # "with it off nothing changes in the loop": the loop module does not
        # import or name this module at all, so the single-reviewer path is
        # untouched until a later task (T6) deliberately wires it in.
        loop_src = (REPO / "tools" / "agent_supervisor" / "loop.py").read_text(encoding="utf-8")
        self.assertNotIn("claude_reviewer", loop_src)


if __name__ == "__main__":
    unittest.main()
