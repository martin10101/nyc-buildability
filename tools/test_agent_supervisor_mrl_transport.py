"""M0-T134 / D-024 Amendment 39 R509 (C7): the single-process one-shot transport.

Injectable spawn (no live launch). Proves the transport PERMITS one fresh claude -p,
one prompt, stdin closed immediately, one wall-clock budget and one --max-turns; and
REFUSES/makes-impossible a second message, queued input, resume/continue, background,
model fallback, and provider-directed continuation.
"""

import json
import unittest

from tools.agent_supervisor.mrl_transport import (
    FORBIDDEN_FLAGS,
    OneShotResult,
    build_one_shot_plan,
    run_one_shot,
)
from tools.agent_supervisor.mrl_worker_result import ContractError, WorkerResult


def _plan(**over):
    kw = dict(executable="/usr/bin/claude", prompt="do the unit", model="claude-opus-4-8",
              max_turns=1, wall_clock_seconds=900.0)
    kw.update(over)
    return build_one_shot_plan(kw.pop("executable"), kw.pop("prompt"), **kw)


class BuildPlanTests(unittest.TestCase):
    def test_positive_shape(self) -> None:
        plan = _plan()
        self.assertIn("--max-turns", plan.argv)
        self.assertIn("1", plan.argv)
        self.assertIn("--model", plan.argv)
        self.assertEqual(plan.prompt, "do the unit")
        self.assertEqual(plan.wall_clock_seconds, 900.0)
        # no forbidden flag anywhere in the assembled argv
        self.assertFalse(set(plan.argv) & FORBIDDEN_FLAGS)

    def test_forbidden_flags_refused(self) -> None:
        for flag in ("--resume", "--continue", "-c", "--last", "--fork-session", "--background"):
            with self.assertRaises(ContractError):
                _plan(extra_flags=[flag])

    def test_no_fallback_model(self) -> None:
        with self.assertRaises(ContractError):
            _plan(model="")
        with self.assertRaises(ContractError):
            _plan(model=["primary", "fallback"])  # a list is not one model

    def test_budgets_required(self) -> None:
        with self.assertRaises(ContractError):
            _plan(max_turns=0)
        with self.assertRaises(ContractError):
            _plan(max_turns=True)  # bool is not a turn count
        with self.assertRaises(ContractError):
            _plan(wall_clock_seconds=0)

    def test_empty_prompt_refused(self) -> None:
        with self.assertRaises(ContractError):
            _plan(prompt="   ")


class RunOneShotTests(unittest.TestCase):
    def test_single_spawn_one_prompt_stdin_closed(self) -> None:
        seen = {}

        def spawn(argv, *, stdin_text, timeout):
            seen["argv"] = argv
            seen["stdin_text"] = stdin_text
            seen["timeout"] = timeout
            return 0, json.dumps({"outcome": "COMPLETED", "summary": "ok",
                                  "requested_next_action": "review"}), ""

        result = run_one_shot(_plan(), spawn=spawn)
        self.assertIsInstance(result, OneShotResult)
        self.assertEqual(result.spawns, 1)                     # exactly one process
        self.assertEqual(seen["stdin_text"], "do the unit")    # exactly one prompt
        self.assertEqual(seen["timeout"], 900.0)               # one wall-clock budget

    def test_one_schema_bound_result(self) -> None:
        payload = {"outcome": "COMPLETED", "summary": "ok", "requested_next_action": ""}

        def spawn(argv, *, stdin_text, timeout):
            return 0, json.dumps(payload), ""

        result = run_one_shot(_plan(), spawn=spawn)
        wr = WorkerResult.from_provider(json.loads(result.stdout))  # one schema-bound result
        self.assertEqual(wr.outcome, "COMPLETED")

    def test_provider_continuation_does_not_cause_second_spawn(self) -> None:
        calls = {"n": 0}

        def spawn(argv, *, stdin_text, timeout):
            calls["n"] += 1
            # stdout "asks" for another turn; the transport must ignore it and not re-spawn
            return 0, "please give me another turn to continue", ""

        run_one_shot(_plan(), spawn=spawn)
        self.assertEqual(calls["n"], 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
