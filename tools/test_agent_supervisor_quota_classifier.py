#!/usr/bin/env python3
"""AS-1: the account-quota exhaustion classifier (M0-T041).

Activation-checklist evidence: project-control/reports/
M0-T036-ACTIVATION-CHECKLIST.md ("Live-CLI account-quota exhaustion classifier
wired ... QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False today"); G3-A1 / G5-L-1 / G4-A1.

These tests prove the classifier machinery is REAL and corpus-gated while the
production stance stays fail-closed (AD-025: unknown is never treated as
zero/success). A proven (verified-live) fixture authorizes the reason; an unknown
shape, an absent signal, a malformed payload, and every production fixture (all
unverified) return "" -> the fail-closed PAUSE stays the default.
"""
from __future__ import annotations

import contextlib
import os
import pathlib
import stat
import sys
import tempfile
import unittest

from tools.agent_supervisor import claude_runner as cr
from tools.agent_supervisor.claude_runner import (
    QUOTA_EXHAUSTED_REASON,
    QUOTA_EXHAUSTION_FIXTURES,
    QUOTA_EXHAUSTION_SIGNAL_VERIFIED,
    QuotaSignalFixture,
    RunnerConfig,
    classify_quota_exhaustion,
    probe_model_launch,
)

# A verified-live test corpus. This is the ONLY thing a real live capture would
# add: one flag flipped to True plus the exact recorded bytes/version. It exists
# here so the "proven shape" path is exercised WITHOUT flipping the production
# corpus (which must stay fail-closed until a real exhaustion is captured).
_VERIFIED_CORPUS = (
    QuotaSignalFixture(
        name="test_only_verified_exhaustion",
        return_codes=frozenset({1}),
        stderr_regex=r"account quota exhausted",
        cli_version="test-fixture-1.0.0",
        verified_live=True,
        provenance="synthetic test fixture standing in for a live capture"),
)


class ClassifierUnitTests(unittest.TestCase):
    def test_proven_shape_returns_quota_exhausted(self) -> None:
        """A verified-live fixture whose shape matches authorizes the reason."""
        self.assertEqual(
            classify_quota_exhaustion(
                1, "error: account quota exhausted for this plan",
                corpus=_VERIFIED_CORPUS),
            QUOTA_EXHAUSTED_REASON)

    def test_unknown_shape_returns_unknown(self) -> None:
        """A shape no fixture recognizes is unknown -> "" (fail-closed)."""
        self.assertEqual(
            classify_quota_exhaustion(
                1, "TypeError: something unrelated blew up",
                corpus=_VERIFIED_CORPUS),
            "")

    def test_absent_signal_returns_unknown(self) -> None:
        """A clean/empty failure carries no signal -> "" (never fabricated)."""
        self.assertEqual(
            classify_quota_exhaustion(0, "", corpus=_VERIFIED_CORPUS), "")
        self.assertEqual(
            classify_quota_exhaustion(None, "", corpus=_VERIFIED_CORPUS), "")

    def test_malformed_payload_returns_unknown_never_raises(self) -> None:
        """A malformed payload degrades to "" and never raises (fail-open crash
        in a policy-adjacent decision would be worse than a denial)."""
        for rc, txt in ((1, None), ("weird", "account quota exhausted"),
                        (object(), b"account quota exhausted"), (1, 12345)):
            with self.subTest(rc=rc, txt=txt):
                self.assertEqual(
                    classify_quota_exhaustion(rc, txt, corpus=_VERIFIED_CORPUS), "")

    def test_verified_fixture_needs_the_code_too(self) -> None:
        """A verified fixture only fires when BOTH the code and stderr match."""
        # Right stderr, WRONG exit code -> no match.
        self.assertEqual(
            classify_quota_exhaustion(
                2, "account quota exhausted", corpus=_VERIFIED_CORPUS), "")


class FailClosedProductionTests(unittest.TestCase):
    """AD-025: the production corpus never authorizes a switch today."""

    def test_verified_flag_is_false_and_derived_from_corpus(self) -> None:
        self.assertFalse(QUOTA_EXHAUSTION_SIGNAL_VERIFIED)
        self.assertEqual(
            QUOTA_EXHAUSTION_SIGNAL_VERIFIED,
            any(f.verified_live for f in QUOTA_EXHAUSTION_FIXTURES))

    def test_every_production_fixture_is_unverified(self) -> None:
        self.assertTrue(QUOTA_EXHAUSTION_FIXTURES, "corpus must not be empty")
        for fixture in QUOTA_EXHAUSTION_FIXTURES:
            with self.subTest(fixture=fixture.name):
                self.assertFalse(fixture.verified_live)
                self.assertIn("UNCAPTURED", fixture.cli_version)

    def test_documented_candidate_match_still_returns_unknown(self) -> None:
        """A production shape that a documented CANDIDATE would recognize still
        returns "" because no fixture is verified-live (fail-closed)."""
        # "usage limit" matches the documented candidate's regex, but that
        # candidate is unverified, so the default production corpus yields "".
        self.assertEqual(
            classify_quota_exhaustion(1, "usage limit reached for your plan"), "")
        self.assertEqual(classify_quota_exhaustion(1, "429 rate limited"), "")


class EmptyShapeFixtureTests(unittest.TestCase):
    """AS-1 (G4 QA review section 6): an empty-shape VERIFIED fixture must be a
    catch-NOTHING, not a catch-all. This locks the final guard line of
    `matches()` (`return bool(self.return_codes) or self.stderr_regex is not
    None`); dropping it goes fail-OPEN - an empty shape would then match every
    input and fabricate a quota signal - and this test fails.
    """

    def _empty_verified(self) -> QuotaSignalFixture:
        # verified_live=True but NEITHER a return-code set NOR a stderr pattern.
        return QuotaSignalFixture(
            name="empty_shape_verified", verified_live=True,
            cli_version="test-empty-1.0.0",
            provenance="a verified fixture that constrains neither code nor stderr")

    def test_an_empty_shape_fixture_matches_nothing(self) -> None:
        fixture = self._empty_verified()
        self.assertEqual(fixture.return_codes, frozenset())
        self.assertIsNone(fixture.stderr_regex)
        for rc, txt in ((1, "account quota exhausted"), (0, ""),
                        (None, "anything at all"), (7, "usage limit reached")):
            with self.subTest(rc=rc, txt=txt):
                self.assertFalse(fixture.matches(rc, txt),
                                 "an empty shape must never match")

    def test_an_empty_verified_fixture_authorizes_no_classification(self) -> None:
        # Even though it is verified_live, an empty shape authorizes nothing:
        # the classifier returns "" for every input.
        corpus = (self._empty_verified(),)
        for rc, txt in ((1, "account quota exhausted"), (1, "TypeError: boom"),
                        (0, ""), (None, "usage limit reached")):
            with self.subTest(rc=rc, txt=txt):
                self.assertEqual(
                    classify_quota_exhaustion(rc, txt, corpus=corpus), "")


class SeamWiringTests(unittest.TestCase):
    """The classifier flows through probe_model_launch into the reason_code."""

    @contextlib.contextmanager
    def _fake_executable(self, script: pathlib.Path):
        original = cr.build_argv

        def patched(config: RunnerConfig) -> list[str]:
            argv = original(config)
            return [argv[0], str(script), *argv[1:]]

        cr.build_argv = patched  # type: ignore[assignment]
        try:
            yield
        finally:
            cr.build_argv = original  # type: ignore[assignment]

    def test_probe_uses_classifier_for_reason_code(self) -> None:
        """A process that exits with a quota signal and never reports a model id
        gets reason_code=quota_exhausted from the verified-corpus classifier."""
        tmp = pathlib.Path(tempfile.mkdtemp())
        script = tmp / "fake_quota.py"
        # Writes the quota signal to stderr, reports NO model id, exits 1.
        script.write_text(
            "import sys\n"
            "sys.stderr.write('error: account quota exhausted for this plan\\n')\n"
            "sys.stderr.flush()\n"
            "sys.exit(1)\n",
            encoding="utf-8")
        os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
        config = RunnerConfig(executable=sys.executable, model="claude-fable-5",
                              expected_model="claude-fable-5", cwd=str(tmp),
                              max_turns=1, timeout_seconds=30.0)

        def classifier(rc, txt):
            return classify_quota_exhaustion(rc, txt, corpus=_VERIFIED_CORPUS)

        with self._fake_executable(script):
            result = probe_model_launch(config, "claude-fable-5",
                                        timeout_seconds=30.0,
                                        classify_unavailable=classifier)
        self.assertFalse(result.available)
        self.assertEqual(result.reason_code, QUOTA_EXHAUSTED_REASON)

    def test_probe_stays_unknown_without_a_verified_signal(self) -> None:
        """The SAME failing process, run through the real production classifier,
        does NOT yield quota_exhausted (fail-closed): the reason falls back to the
        probe's own observation, never the unverified quota reason."""
        tmp = pathlib.Path(tempfile.mkdtemp())
        script = tmp / "fake_quota.py"
        script.write_text(
            "import sys\n"
            "sys.stderr.write('error: account quota exhausted for this plan\\n')\n"
            "sys.exit(1)\n",
            encoding="utf-8")
        os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
        config = RunnerConfig(executable=sys.executable, model="claude-fable-5",
                              expected_model="claude-fable-5", cwd=str(tmp),
                              max_turns=1, timeout_seconds=30.0)
        with self._fake_executable(script):
            result = probe_model_launch(config, "claude-fable-5",
                                        timeout_seconds=30.0,
                                        classify_unavailable=classify_quota_exhaustion)
        self.assertFalse(result.available)
        self.assertNotEqual(result.reason_code, QUOTA_EXHAUSTED_REASON)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
