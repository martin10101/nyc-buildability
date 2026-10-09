"""M0-T134 / D-024 Amendment 39 R509/R500: the claude_runner.py -> checkpoint_extraction.py
behavior-neutral split.

Proves (1) the FACADE: RunnerError/CheckpointError/_event_text and the S8.3 checkpoint
find/validate/extract helpers remain importable from `claude_runner` and are the *same objects*
now defined in `checkpoint_extraction`, so cli.py's `except RunnerError` and every
`from .claude_runner import extract_checkpoint` consumer/test are unaffected; and (2) that the
relocated behavior is byte-for-byte the same (positive + the missing/conflicting/multiple/invalid
fail-closed mutants). The exhaustive extraction behavior is additionally covered by the pre-existing
runner/checkpoint suites, which stay green across the split.
"""

import unittest

from tools.agent_supervisor import checkpoint_extraction as ce
from tools.agent_supervisor import claude_runner as cr
from tools.agent_supervisor import cli


def _valid_checkpoint(checkpoint_id: str = "ckpt-1", summary: str = "did the unit") -> dict:
    return {
        "schema_version": "1.0.0",
        "run_id": "run-1",
        "checkpoint_id": checkpoint_id,
        "task_id": "M0-T134",
        "claude_session_id": "sess-1",
        "status": "UNIT_COMPLETE",
        "summary": summary,
        "starting_sha": "a" * 40,
        "current_sha": "b" * 40,
        "branch": "stabilization/D-024-mrl",
        "worktree": "/tmp/wt",
        "proposed_next_action": "independent review",
    }


class FacadeReExportTests(unittest.TestCase):
    """The split must be import-transparent for every consumer."""

    def test_names_reexported_are_identical_objects(self) -> None:
        for name in ("RunnerError", "CheckpointError", "_event_text",
                     "find_checkpoint_candidate", "validate_checkpoint",
                     "extract_checkpoint", "checkpoint_question_decided"):
            self.assertIs(getattr(cr, name), getattr(ce, name),
                          f"{name} must be the same object via the claude_runner facade")

    def test_errors_now_live_in_checkpoint_extraction(self) -> None:
        self.assertEqual(cr.RunnerError.__module__,
                         "tools.agent_supervisor.checkpoint_extraction")
        self.assertTrue(issubclass(ce.CheckpointError, ce.RunnerError))

    def test_cli_runner_error_is_the_same_object(self) -> None:
        # cli.py does `from .claude_runner import RunnerError`; its except-clause must
        # still catch what the checkpoint helpers raise.
        self.assertIs(cli.RunnerError, ce.RunnerError)
        try:
            raise ce.CheckpointError("missing_checkpoint", "x")
        except cli.RunnerError as exc:  # the exact clause cli.py relies on
            self.assertEqual(exc.code, "missing_checkpoint")


class RelocatedBehaviorTests(unittest.TestCase):
    """Positive path + the fail-closed mutants, run against the relocated functions."""

    def test_positive_find_validate_extract(self) -> None:
        events = [_valid_checkpoint()]
        candidate = ce.find_checkpoint_candidate(events)
        self.assertEqual(candidate["checkpoint_id"], "ckpt-1")
        checkpoint = ce.validate_checkpoint(candidate)
        self.assertEqual(checkpoint.status, "UNIT_COMPLETE")
        self.assertEqual(ce.extract_checkpoint(events).checkpoint_id, "ckpt-1")

    def test_fenced_json_candidate_is_found(self) -> None:
        import json
        text = "prose\n```json\n" + json.dumps(_valid_checkpoint()) + "\n```\n"
        events = [{"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}]
        self.assertEqual(ce.extract_checkpoint(events).checkpoint_id, "ckpt-1")

    def test_missing_checkpoint_fails_closed(self) -> None:
        with self.assertRaises(ce.CheckpointError) as ctx:
            ce.find_checkpoint_candidate([{"type": "result", "result": "no json"}])
        self.assertEqual(ctx.exception.code, "missing_checkpoint")

    def test_conflicting_duplicate_fails_closed(self) -> None:
        events = [_valid_checkpoint(summary="one"), _valid_checkpoint(summary="two")]
        with self.assertRaises(ce.CheckpointError) as ctx:
            ce.find_checkpoint_candidate(events)
        self.assertEqual(ctx.exception.code, "conflicting_duplicate_checkpoint")

    def test_multiple_distinct_fails_closed(self) -> None:
        events = [_valid_checkpoint("ckpt-1"), _valid_checkpoint("ckpt-2")]
        with self.assertRaises(ce.CheckpointError) as ctx:
            ce.find_checkpoint_candidate(events)
        self.assertEqual(ctx.exception.code, "multiple_distinct_checkpoints")

    def test_invalid_checkpoint_fails_closed(self) -> None:
        bad = {"checkpoint_id": "ckpt-1", "schema_version": "1.0.0", "status": "NOT_A_STATUS"}
        with self.assertRaises(ce.CheckpointError) as ctx:
            ce.validate_checkpoint(bad)
        self.assertEqual(ctx.exception.code, "invalid_checkpoint")

    def test_checkpoint_question_decided(self) -> None:
        self.assertTrue(ce.checkpoint_question_decided([_valid_checkpoint()]))
        self.assertFalse(ce.checkpoint_question_decided([{"type": "result", "result": "none"}]))
        # a present-but-invalid candidate still ANSWERS the question (True)
        self.assertTrue(ce.checkpoint_question_decided(
            [{"checkpoint_id": "c", "schema_version": "1.0.0", "status": "NOPE"}]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
