"""M0-T134 / D-024 Amendment 39 R501/R503 (C8): the untrusted WorkerResult contract
and the controller-authoritative ClaudeCheckpoint builder.

Positive path plus every fail-closed mutant the owner enumerated: unknown field, wrong
type, invalid enum, excess length, forged factual field, and proof that the controller
builds the checkpoint's factual fields from its OWN observed facts, never the worker's.
"""

import unittest

from tools.agent_supervisor.mrl_worker_result import (
    ContractError,
    ControllerObservedFacts,
    WorkerResult,
    build_claude_checkpoint,
    load_schema,
)


def _valid_raw(**over):
    raw = {"outcome": "COMPLETED", "summary": "did the unit",
           "requested_next_action": "please review"}
    raw.update(over)
    return raw


def _facts(**over):
    base = dict(run_id="run-1", checkpoint_id="ckpt-1", task_id="M0-T134",
                claude_session_id="sess-1", starting_sha="a" * 40, current_sha="b" * 40,
                branch="stabilization/D-024-mrl", worktree="/tmp/wt")
    base.update(over)
    return ControllerObservedFacts(**base)


class SchemaShapeTests(unittest.TestCase):
    def test_schema_declares_closed_object_and_exact_fields(self) -> None:
        schema = load_schema("worker_result.schema.json")
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["required"]), {"outcome", "summary", "requested_next_action"})
        self.assertEqual(set(schema["properties"]), {"outcome", "summary", "requested_next_action"})
        self.assertEqual(set(schema["properties"]["outcome"]["enum"]),
                         {"COMPLETED", "BLOCKED", "NEEDS_OWNER"})
        self.assertEqual(schema["properties"]["summary"]["maxLength"], 4096)
        self.assertEqual(schema["properties"]["requested_next_action"]["maxLength"], 1024)


class WorkerResultPositiveTests(unittest.TestCase):
    def test_valid_payload_parses(self) -> None:
        wr = WorkerResult.from_provider(_valid_raw())
        self.assertEqual((wr.outcome, wr.summary, wr.requested_next_action),
                         ("COMPLETED", "did the unit", "please review"))

    def test_empty_next_action_is_allowed(self) -> None:  # minLength 0
        wr = WorkerResult.from_provider(_valid_raw(requested_next_action=""))
        self.assertEqual(wr.requested_next_action, "")

    def test_boundary_lengths_allowed(self) -> None:
        WorkerResult.from_provider(_valid_raw(summary="x" * 4096,
                                              requested_next_action="y" * 1024))


class WorkerResultMutantTests(unittest.TestCase):
    def _rejects(self, raw):
        with self.assertRaises(ContractError):
            WorkerResult.from_provider(raw)

    def test_unknown_field_rejected(self) -> None:
        self._rejects(_valid_raw(note="extra"))

    def test_forged_factual_field_rejected(self) -> None:  # R503
        for forged in ("run_id", "current_sha", "branch", "origin", "model",
                       "gate_result", "evidence_digest", "task_id"):
            self._rejects(_valid_raw(**{forged: "x"}))

    def test_missing_field_rejected(self) -> None:
        raw = _valid_raw()
        del raw["summary"]
        self._rejects(raw)

    def test_wrong_type_rejected(self) -> None:
        self._rejects(_valid_raw(summary=123))
        self._rejects(_valid_raw(outcome=True))
        self._rejects(_valid_raw(requested_next_action=["x"]))

    def test_invalid_enum_rejected(self) -> None:
        self._rejects(_valid_raw(outcome="DONE"))
        self._rejects(_valid_raw(outcome="completed"))

    def test_excess_length_rejected(self) -> None:
        self._rejects(_valid_raw(summary="x" * 4097))
        self._rejects(_valid_raw(requested_next_action="y" * 1025))

    def test_empty_summary_rejected(self) -> None:  # minLength 1
        self._rejects(_valid_raw(summary=""))

    def test_non_object_rejected(self) -> None:
        self._rejects(["outcome"])
        self._rejects("COMPLETED")


class ControllerBuildTests(unittest.TestCase):
    def test_factual_fields_come_from_controller_not_worker(self) -> None:
        wr = WorkerResult.from_provider(_valid_raw(summary="worker text",
                                                   requested_next_action="worker action"))
        cp = build_claude_checkpoint(wr, _facts(run_id="R", current_sha="c" * 40))
        # factual fields are the controller's observed values
        self.assertEqual(cp.run_id, "R")
        self.assertEqual(cp.current_sha, "c" * 40)
        self.assertEqual(cp.starting_sha, "a" * 40)
        self.assertEqual(cp.branch, "stabilization/D-024-mrl")
        self.assertEqual(cp.task_id, "M0-T134")
        # only the two text fields come from the (untrusted) worker
        self.assertEqual(cp.summary, "worker text")
        self.assertEqual(cp.proposed_next_action, "worker action")

    def test_outcome_maps_to_status(self) -> None:
        cases = {"COMPLETED": "UNIT_COMPLETE", "BLOCKED": "BLOCKED", "NEEDS_OWNER": "BLOCKED"}
        for outcome, status in cases.items():
            wr = WorkerResult.from_provider(_valid_raw(outcome=outcome))
            self.assertEqual(build_claude_checkpoint(wr, _facts()).status, status)

    def test_empty_next_action_gets_placeholder(self) -> None:
        wr = WorkerResult.from_provider(_valid_raw(requested_next_action=""))
        self.assertTrue(build_claude_checkpoint(wr, _facts()).proposed_next_action)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
