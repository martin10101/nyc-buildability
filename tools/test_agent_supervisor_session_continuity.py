#!/usr/bin/env python3
"""Session-continuity ceiling-telemetry tests (M0-T123, D-024-R332/R333).

Focused coverage of the `ProviderSession` context-token telemetry added so a
later START can evaluate the 400k rotation ceiling before provider contact, plus
regression guards that the continuity DECISION (`decide_continuity`) is unchanged
by the additive fields. The broader continuity behaviour is exercised by
`tools/test_agent_supervisor_turnover_integration.py`.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import session_continuity as sc  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402


class ProviderSessionTelemetry(unittest.TestCase):
    def test_tokens_round_trip_when_usage_known(self) -> None:
        rec = sc.ProviderSession(session_id="s", model_id="claude-fable-5",
                                 context_tokens=604_772, usage_known=True)
        back = sc.ProviderSession.from_dict(rec.to_dict())
        self.assertEqual(back.context_tokens, 604_772)
        self.assertTrue(back.usage_known)
        self.assertEqual(back.model_id, "claude-fable-5")

    def test_legacy_record_without_tokens_reads_unknown_not_zero(self) -> None:
        # The preserved provider_session_continuity had NO context_tokens key.
        back = sc.ProviderSession.from_dict(
            {"session_id": "798d2f00", "run_id": "run_x", "cycle": 1})
        self.assertIsNone(back.context_tokens)
        self.assertFalse(back.usage_known)

    def test_malformed_token_value_reads_unknown(self) -> None:
        back = sc.ProviderSession.from_dict(
            {"session_id": "s", "context_tokens": "lots"})
        self.assertIsNone(back.context_tokens)

    def test_record_never_stores_unknown_usage_as_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            j = DurableJournal(pathlib.Path(d) / "j.sqlite3").open()
            try:
                sc.record_provider_session(j, session_id="s", context_tokens=500,
                                           usage_known=False)
                got = sc.recorded_provider_session(j)
                self.assertIsNone(got.context_tokens)
                self.assertFalse(got.usage_known)
            finally:
                j.close()

    def test_record_persists_known_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            j = DurableJournal(pathlib.Path(d) / "j.sqlite3").open()
            try:
                sc.record_provider_session(j, session_id="s", run_id="r",
                                           context_tokens=640_224, usage_known=True)
                got = sc.recorded_provider_session(j, run_id="r")
                self.assertEqual(got.context_tokens, 640_224)
                self.assertTrue(got.usage_known)
            finally:
                j.close()


class ContinuityDecisionUnchanged(unittest.TestCase):
    """Regression: the additive telemetry fields do not change the resume/reorient
    decision, which still turns on identity, model, capability, and shed reason."""

    def _sess(self, **kw) -> sc.ProviderSession:
        base = dict(session_id="prov-1", model_id="claude-fable-5")
        base.update(kw)
        return sc.ProviderSession(**base)

    def test_resume_when_all_conditions_met(self) -> None:
        d = sc.decide_continuity(
            recorded=self._sess(context_tokens=100, usage_known=True),
            successor_model="claude-fable-5", rotation_reason="model_downgrade",
            resume_capability_verified=True)
        self.assertTrue(d.resumed)
        self.assertEqual(d.provider_session_id, "prov-1")

    def test_context_shedding_reason_still_reorients(self) -> None:
        d = sc.decide_continuity(
            recorded=self._sess(context_tokens=100, usage_known=True),
            successor_model="claude-fable-5", rotation_reason="context_threshold",
            resume_capability_verified=True)
        self.assertFalse(d.resumed)
        self.assertIn(sc.CONTEXT_SHEDDING_ROTATION, d.none_reasons)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
