"""M0-T134 / D-024 Amendment 39 R505 (C11): read-only remote-freshness observation.

Injectable git runner (no network, no live GitHub call). Positive plus fail-closed
mutants: empty url/ref (Option-B neutral - base ref is never defaulted to origin/main),
and ls-remote output that does not yield a 40-hex sha.
"""

import datetime
import unittest

from tools.agent_supervisor.mrl_remote import (
    RemoteObservation,
    normalize_remote_url,
    observe_remote,
)
from tools.agent_supervisor.mrl_worker_result import ContractError

_FIXED = datetime.datetime(2026, 9, 1, 17, 0, tzinfo=datetime.timezone.utc)


def _run_returning(text):
    return lambda argv: text


class NormalizeTests(unittest.TestCase):
    def test_strips_dot_git_and_trailing_slash(self) -> None:
        self.assertEqual(normalize_remote_url("https://x/y.git"), "https://x/y")
        self.assertEqual(normalize_remote_url("https://x/y/"), "https://x/y")


class ObserveRemoteTests(unittest.TestCase):
    def test_positive_records_fresh_sha_and_timestamp(self) -> None:
        sha = "c" * 40
        obs = observe_remote(
            "https://github.com/o/r.git", "refs/heads/integration",
            run=_run_returning(f"{sha}\trefs/heads/integration\n"),
            now=lambda: _FIXED)
        self.assertIsInstance(obs, RemoteObservation)
        self.assertEqual(obs.base_sha, sha)
        self.assertEqual(obs.base_ref, "refs/heads/integration")  # Option-B neutral
        self.assertEqual(obs.normalized_remote_url, "https://github.com/o/r")
        self.assertEqual(obs.observed_at_utc, _FIXED.isoformat())

    def test_empty_remote_url_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            observe_remote("", "refs/heads/integration", run=_run_returning("x"))

    def test_empty_base_ref_fails_closed(self) -> None:  # Option-B: never a default main
        with self.assertRaises(ContractError):
            observe_remote("https://x/y", "", run=_run_returning("x"))

    def test_no_sha_in_output_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            observe_remote("https://x/y", "refs/heads/integration", run=_run_returning(""))

    def test_non_hex_sha_fails_closed(self) -> None:
        with self.assertRaises(ContractError):
            observe_remote("https://x/y", "refs/heads/integration",
                           run=_run_returning("not-a-sha\trefs/heads/integration\n"))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
