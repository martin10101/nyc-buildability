#!/usr/bin/env python3
"""`loop_turnover.actuate_resume` telemetry-threading tests (M0-T123, D-024-R332).

When a rotation RESUMES a recorded session, the actuation must carry that
session's ceiling telemetry onto the launch config so the runner's pre-`Popen`
launch seam can evaluate the 400k ceiling before the `--resume` reaches the
provider. The broader turnover behaviour is exercised by
`tools/test_agent_supervisor_turnover_integration.py`.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import loop_turnover as lt  # noqa: E402
from tools.agent_supervisor import session_continuity as sc  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402


class _RecordingRunner:
    """Records the kwargs its `with_resume` was called with."""

    def __init__(self, accepts_kwargs: bool = True) -> None:
        self.config = cr.RunnerConfig(executable="fake")
        self.calls: list[dict] = []
        self._accepts = accepts_kwargs

    def with_resume(self, provider_session_id, **kwargs):
        if not self._accepts and kwargs:
            raise TypeError("with_resume() got unexpected kwargs")
        self.calls.append({"id": provider_session_id, **kwargs})
        clone = _RecordingRunner(self._accepts)
        clone.calls = self.calls
        clone.config = dataclasses.replace(
            self.config, resume_session_id=provider_session_id,
            resume_context_tokens=kwargs.get("context_tokens"),
            resume_usage_known=bool(kwargs.get("usage_known", False)))
        return clone


class _Loop:
    def __init__(self, journal, runner, run_id="r") -> None:
        self.journal = journal
        self.runner = runner
        self.run_id = run_id


class ActuateResumeTelemetry(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.journal = DurableJournal(
            pathlib.Path(self._tmp.name) / "j.sqlite3").open()
        self.addCleanup(self.journal.close)

    def test_recorded_below_ceiling_tokens_are_threaded_to_the_resume(self) -> None:
        sc.record_provider_session(self.journal, session_id="prov-1", run_id="r",
                                   context_tokens=120_000, usage_known=True)
        runner = _RecordingRunner()
        loop = _Loop(self.journal, runner)
        lt.actuate_resume(loop, "prov-1")
        self.assertEqual(loop.runner.config.resume_context_tokens, 120_000)
        self.assertTrue(loop.runner.config.resume_usage_known)
        self.assertEqual(runner.calls[-1]["context_tokens"], 120_000)

    def test_unknown_telemetry_is_threaded_as_unknown(self) -> None:
        # A legacy recorded session with no token field threads unknown telemetry,
        # which the runner-level seam then fails closed on.
        self.journal.set_state(sc.PROVIDER_SESSION_KEY,
                               {"session_id": "prov-legacy", "run_id": "r", "cycle": 1})
        runner = _RecordingRunner()
        loop = _Loop(self.journal, runner)
        lt.actuate_resume(loop, "prov-legacy")
        self.assertIsNone(loop.runner.config.resume_context_tokens)
        self.assertFalse(loop.runner.config.resume_usage_known)

    def test_legacy_runner_without_kwargs_still_rebinds(self) -> None:
        # A runner whose with_resume predates the telemetry kwargs is not broken:
        # actuate_resume falls back to the positional rebind.
        sc.record_provider_session(self.journal, session_id="prov-1", run_id="r",
                                   context_tokens=100, usage_known=True)
        runner = _RecordingRunner(accepts_kwargs=False)
        loop = _Loop(self.journal, runner)
        lt.actuate_resume(loop, "prov-1")
        self.assertEqual(loop.runner.config.resume_session_id, "prov-1")

    def test_a_runner_that_cannot_rebind_is_a_refusal(self) -> None:
        from tools.agent_supervisor.errors import LoopError

        class _NoRebind:
            config = cr.RunnerConfig(executable="fake")
        loop = _Loop(self.journal, _NoRebind())
        with self.assertRaises(LoopError) as cm:
            lt.actuate_resume(loop, "prov-1")
        self.assertEqual(cm.exception.code, "resume_actuation_unavailable")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
