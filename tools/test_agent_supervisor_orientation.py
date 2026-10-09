#!/usr/bin/env python3
"""Removal-sensitive tests for the front-loaded orientation packet (property 1).

M0-T126 (D-024-R372; property 1 / R376, defect D3). R387 scenario 1
(fresh-session and rotated-session orientation). The live counted stop
dispatched a worker whose first prompt carried NO task/lineage/worktree/
progress/files/required-output orientation; these tests prove every required
element is present and that a fresh vs a rotated worker are oriented distinctly.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.agent_supervisor import orientation as orient  # noqa: E402
from tools.agent_supervisor.turn_budget import (  # noqa: E402
    TurnAllowances,
    size_turn_budget,
)
from tools.agent_supervisor.workload_classifier import (  # noqa: E402
    COHESIVE_SUBAGENT,
    OVERSIZED_SPLIT,
    WorkloadClassification,
)


def _budget(work_class: str = COHESIVE_SUBAGENT):
    return size_turn_budget(
        WorkloadClassification(work_class, "r", "reason"), TurnAllowances())


def _inputs(**over):
    base = dict(
        task_id="M0-T107", stage="claimed", run_id="run_abc123",
        worktree="C:/Users/x/wt-m0t107", branch="task/M0-T107",
        allowed_paths=("a.py", "b.py"),
        documented_commands=("pytest tools/test_x.py",))
    base.update(over)
    return orient.OrientationInputs(**base)


class RequiredElementsTests(unittest.TestCase):
    """Property 1: task, lineage, worktree, progress, files, required output."""

    def test_every_required_element_is_present(self) -> None:
        packet = orient.build_orientation_packet(_inputs(), _budget())
        for needle in (orient.ORIENTATION_SENTINEL, "TASK: M0-T107",
                       "AUTHORIZED STAGE: claimed", "WORKTREE:", "BRANCH:",
                       "RUN LINEAGE: run_abc123", "CURRENT PROGRESS:",
                       "RELEVANT FILES", "a.py", "b.py",
                       "DOCUMENTED COMMANDS", "pytest tools/test_x.py",
                       "CHECKPOINT CADENCE", "EXACT REQUIRED OUTPUT",
                       "claude_checkpoint.schema.json"):
            with self.subTest(needle=needle):
                self.assertIn(needle, packet)

    def test_cadence_names_early_incremental_and_reserved_final_turn(self) -> None:
        budget = _budget()
        packet = orient.build_orientation_packet(_inputs(), budget)
        self.assertIn(f"by turn {budget.early_checkpoint_by}", packet)
        self.assertIn("incremental checkpoint", packet)
        self.assertIn("FINAL turn is reserved", packet)
        self.assertIn(f"{budget.total_turns} turns total", packet)

    def test_missing_required_field_fails_closed(self) -> None:
        with self.assertRaises(orient.OrientationError):
            orient.OrientationInputs(
                task_id="", stage="claimed", run_id="r",
                worktree="w", branch="b")


class FreshVsRotatedTests(unittest.TestCase):
    def test_fresh_worker_states_fresh_lineage(self) -> None:
        packet = orient.build_orientation_packet(_inputs(rotated=False), _budget())
        self.assertIn("FRESH worker", packet)
        self.assertIn(orient.FRESH_PROGRESS, packet)

    def test_rotated_worker_names_predecessor_and_reason(self) -> None:
        packet = orient.build_orientation_packet(
            _inputs(rotated=True, rotation_reason="context_threshold",
                    predecessor_session="sid-999"), _budget())
        self.assertIn("ROTATED successor", packet)
        self.assertIn("sid-999", packet)
        self.assertIn("context_threshold", packet)

    def test_fresh_and_rotated_orientation_differ(self) -> None:
        fresh = orient.build_orientation_packet(_inputs(rotated=False), _budget())
        rotated = orient.build_orientation_packet(
            _inputs(rotated=True, rotation_reason="rotate_session",
                    predecessor_session="sid-1"), _budget())
        self.assertNotEqual(fresh, rotated)


class IdempotenceAndSafetyTests(unittest.TestCase):
    def test_with_orientation_is_idempotent(self) -> None:
        once = orient.with_orientation("do the work", _inputs(), _budget())
        twice = orient.with_orientation(once, _inputs(), _budget())
        self.assertEqual(once, twice)
        self.assertEqual(once.count(orient.ORIENTATION_SENTINEL), 1)

    def test_orientation_is_front_loaded(self) -> None:
        wrapped = orient.with_orientation("TASK BODY HERE", _inputs(), _budget())
        self.assertLess(
            wrapped.index(orient.ORIENTATION_SENTINEL),
            wrapped.index("TASK BODY HERE"),
            "the orientation block must precede the task body")

    def test_deterministic_no_clock(self) -> None:
        a = orient.build_orientation_packet(_inputs(), _budget())
        b = orient.build_orientation_packet(_inputs(), _budget())
        self.assertEqual(a, b)

    def test_non_dispatchable_unit_is_never_oriented(self) -> None:
        oversized = size_turn_budget(
            WorkloadClassification(OVERSIZED_SPLIT, "oversized", "spans seams"))
        with self.assertRaises(orient.OrientationError):
            orient.build_orientation_packet(_inputs(), oversized)


class RotatedReorientationTests(unittest.TestCase):
    """G3-1: oriented_reorientation_prompt front-loads the rotated packet onto a
    reorientation handoff, and fails safe when no dispatchable budget exists."""

    def _kwargs(self, **over):
        base = dict(
            task_id="M0-T107", stage="claimed", run_id="run_abc",
            worktree="C:/wt", branch="task/M0-T107",
            allowed_paths=("a.py", "b.py"), rotation_reason="context_threshold",
            predecessor_session="sid-9")
        base.update(over)
        return base

    def test_enriches_the_handoff_with_cadence_paths_and_required_output(self) -> None:
        budget = _budget()
        out = orient.oriented_reorientation_prompt(
            "HANDOFF BODY", budget, **self._kwargs())
        self.assertIn("HANDOFF BODY", out)
        self.assertIn(orient.ORIENTATION_SENTINEL, out)
        self.assertIn("ROTATED successor", out)
        self.assertIn("context_threshold", out)
        self.assertIn("CHECKPOINT CADENCE", out)
        self.assertIn(f"by turn {budget.early_checkpoint_by}", out)
        self.assertIn("a.py", out)
        self.assertIn("EXACT REQUIRED OUTPUT", out)
        # Front-loaded: the packet precedes the handoff body.
        self.assertLess(out.index(orient.ORIENTATION_SENTINEL),
                        out.index("HANDOFF BODY"))

    def test_no_budget_returns_the_handoff_unchanged(self) -> None:
        out = orient.oriented_reorientation_prompt(
            "HANDOFF BODY", None, **self._kwargs())
        self.assertEqual(out, "HANDOFF BODY")

    def test_oversized_budget_returns_the_handoff_unchanged(self) -> None:
        oversized = size_turn_budget(
            WorkloadClassification(OVERSIZED_SPLIT, "oversized", "spans seams"))
        out = orient.oriented_reorientation_prompt(
            "HANDOFF BODY", oversized, **self._kwargs())
        self.assertEqual(out, "HANDOFF BODY")


if __name__ == "__main__":
    unittest.main()
