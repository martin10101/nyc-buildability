#!/usr/bin/env python3
"""Forced DISABLE_AUTOUPDATER=1 injection on every controller-launched CLAUDE child.

D-024 Amendment 13 (R278/R286), task M0-T117. The certified Claude CLI identity
must not drift mid-run (seq-30 reproduced installed 2.1.251 vs certified 2.1.248),
so every controller-launched claude child process carries DISABLE_AUTOUPDATER=1 in
its environment UNCONDITIONALLY - independent of the parent environment and of the
env allowlist. These tests are REMOVAL-SENSITIVE: deleting the forced injection
makes AS-1/AS-2/AS-3 fail (the env would then lack the key entirely).

Scope proof: the injection is CLAUDE-scoped. It lives in `process.claude_child_env`,
which the two claude Popen sites in `claude_runner` use; the shared `minimal_env`
that codex children (codex_channel) use is left untouched (AS-5).

No real provider is launched: `subprocess.Popen` is intercepted so the exact `env`
mapping the production call site constructs is captured, then the launch is aborted.
There are NO tokens and NO network here.
"""
from __future__ import annotations

import os
import pathlib
import sys
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import codex_channel  # noqa: E402
from tools.agent_supervisor import preflight  # noqa: E402
from tools.agent_supervisor import process as pc  # noqa: E402
from tools.agent_supervisor import turnover_adapters as ta  # noqa: E402
from tools.agent_supervisor import turnover_controller as tc  # noqa: E402


class _StopLaunch(Exception):
    """Raised by the fake Popen to abort the launch once the env is captured."""


def _capturing_popen(store: dict[str, object]):
    """A fake `subprocess.Popen` that records the `env` kwarg then aborts."""

    def fake_popen(argv, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        store["argv"] = argv
        store["env"] = kwargs.get("env")
        raise _StopLaunch()

    return fake_popen


def _base_config() -> "cr.RunnerConfig":
    # use_job_object=False keeps the container off the real Windows Job Object
    # path so the test never creates OS handles; it does not touch env building.
    return cr.RunnerConfig(executable="claude", use_job_object=False)


class ClaudeChildEnvInjectionTests(unittest.TestCase):
    """AS-1, AS-2: both claude launch sites inject DISABLE_AUTOUPDATER=1."""

    def setUp(self) -> None:
        # AS-1 precondition: the PARENT environment must lack the variable, so a
        # pass proves the injection - not mere inheritance. Restore afterwards.
        self._had = "DISABLE_AUTOUPDATER" in os.environ
        self._prev = os.environ.pop("DISABLE_AUTOUPDATER", None)

    def tearDown(self) -> None:
        if self._had:
            os.environ["DISABLE_AUTOUPDATER"] = self._prev  # type: ignore[assignment]
        else:
            os.environ.pop("DISABLE_AUTOUPDATER", None)

    def test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it(self) -> None:
        # The allowlist genuinely omits the variable, so the ONLY way it can reach
        # the child is the forced injection.
        self.assertNotIn("DISABLE_AUTOUPDATER", pc.DEFAULT_ENV_ALLOWLIST)
        self.assertNotIn("DISABLE_AUTOUPDATER", os.environ)

        store: dict[str, object] = {}
        with mock.patch("subprocess.Popen", _capturing_popen(store)):
            with self.assertRaises(_StopLaunch):
                cr.ClaudeRunner(_base_config()).run_unit("probe prompt")

        env = store["env"]
        assert isinstance(env, dict)
        self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")

    def test_as2_probe_launch_injects_identically(self) -> None:
        self.assertNotIn("DISABLE_AUTOUPDATER", os.environ)

        store: dict[str, object] = {}
        with mock.patch("subprocess.Popen", _capturing_popen(store)):
            with self.assertRaises(_StopLaunch):
                cr.probe_model_launch(_base_config(), "claude-test-model")

        env = store["env"]
        assert isinstance(env, dict)
        self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")


class ClaudeChildEnvSeamTests(unittest.TestCase):
    """AS-3, AS-6: the env-construction helper's exact behavior."""

    def test_as3_no_collateral_change_vs_minimal_env(self) -> None:
        extra = {"FAKE_MODE": "normal"}
        allow = pc.DEFAULT_ENV_ALLOWLIST
        expected = pc.minimal_env(extra, allow)
        expected["DISABLE_AUTOUPDATER"] = "1"
        # Byte-identical to minimal_env for identical inputs, except the one
        # forced pair. Dict equality is order-independent, so this is exact.
        self.assertEqual(pc.claude_child_env(extra, allow), expected)

    def test_as3_only_difference_is_the_single_forced_key(self) -> None:
        allow = pc.DEFAULT_ENV_ALLOWLIST
        base = pc.minimal_env(None, allow)
        built = pc.claude_child_env(None, allow)
        added = set(built) - set(base)
        removed = set(base) - set(built)
        changed = {k for k in base if k in built and base[k] != built[k]}
        self.assertEqual(added, {"DISABLE_AUTOUPDATER"})
        self.assertEqual(removed, set())
        self.assertEqual(changed, set())

    def test_as6_extra_env_conflict_is_overridden_forced_pair_wins(self) -> None:
        # Fail-closed choice: a config extra_env that tries to RE-ENABLE the
        # updater (or set any other value) cannot win. The forced "1" is applied
        # last, so it is unconditional.
        for hostile in ("0", "false", "", "off", "1"):
            env = pc.claude_child_env({"DISABLE_AUTOUPDATER": hostile})
            self.assertEqual(env["DISABLE_AUTOUPDATER"], "1",
                             f"extra_env value {hostile!r} must not survive")

    def test_as6_unrelated_extra_env_still_passes_through(self) -> None:
        env = pc.claude_child_env({"FAKE_MODE": "normal"})
        self.assertEqual(env["FAKE_MODE"], "normal")
        self.assertEqual(env["DISABLE_AUTOUPDATER"], "1")

    def test_g4f6_allowlist_reenable_vector_is_overridden(self) -> None:
        # G4 F6: even if the allowlist CONTAINS DISABLE_AUTOUPDATER and the parent
        # env carries a re-enabling "0", the inherited value cannot survive - the
        # forced pair is applied last. This closes the "widen the allowlist to let
        # the parent turn it back on" vector.
        prev = os.environ.get("DISABLE_AUTOUPDATER")
        os.environ["DISABLE_AUTOUPDATER"] = "0"
        try:
            allow = tuple(pc.DEFAULT_ENV_ALLOWLIST) + ("DISABLE_AUTOUPDATER",)
            # Prove the allowlist really would have admitted the parent's "0"...
            self.assertEqual(pc.minimal_env(None, allow)["DISABLE_AUTOUPDATER"], "0")
            # ...and that claude_child_env forces it back to "1" regardless.
            self.assertEqual(pc.claude_child_env(None, allow)["DISABLE_AUTOUPDATER"], "1")
        finally:
            if prev is None:
                os.environ.pop("DISABLE_AUTOUPDATER", None)
            else:
                os.environ["DISABLE_AUTOUPDATER"] = prev


class DoctorLiveProbeEnvTests(unittest.TestCase):
    """G3-2: the doctor --live control-response probe (preflight) injects the control.

    This probe launches the real claude executable INSIDE the certification window,
    so it must carry DISABLE_AUTOUPDATER=1 like every other supervisor-constructed
    claude launch. Same real-seam interception style as AS-1/AS-2.
    """

    def setUp(self) -> None:
        self._had = "DISABLE_AUTOUPDATER" in os.environ
        self._prev = os.environ.pop("DISABLE_AUTOUPDATER", None)

    def tearDown(self) -> None:
        if self._had:
            os.environ["DISABLE_AUTOUPDATER"] = self._prev  # type: ignore[assignment]
        else:
            os.environ.pop("DISABLE_AUTOUPDATER", None)

    def test_control_response_round_trip_injects_the_control(self) -> None:
        self.assertNotIn("DISABLE_AUTOUPDATER", os.environ)
        store: dict[str, object] = {}
        with mock.patch("subprocess.Popen", _capturing_popen(store)):
            with self.assertRaises(_StopLaunch):
                preflight.control_response_round_trip("claude", live=True)
        env = store["env"]
        assert isinstance(env, dict)
        self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")


class TurnoverSuccessorEnvTests(unittest.TestCase):
    """G3-3: the turnover successor launcher injects the control for BOTH layers.

    The successor launch (worker redispatch and orchestrator/handoff start) builds
    its env once in `_build_invocation`; that env must force DISABLE_AUTOUPDATER=1
    while preserving the existing effort/role pairs it already passes.
    """

    def setUp(self) -> None:
        self._had = "DISABLE_AUTOUPDATER" in os.environ
        self._prev = os.environ.pop("DISABLE_AUTOUPDATER", None)

    def tearDown(self) -> None:
        if self._had:
            os.environ["DISABLE_AUTOUPDATER"] = self._prev  # type: ignore[assignment]
        else:
            os.environ.pop("DISABLE_AUTOUPDATER", None)

    def _launcher(self) -> "ta.SupervisorLauncher":
        targets = ta.SuccessorLaunchTargets(
            checkout="C:/some/checkout",
            claude_executable="claude",
            orchestrator_argv_prefix=("python", "-m", "supervisor", "start"),
        )
        return ta.SupervisorLauncher(
            command_runner=lambda inv: ta.CommandRunResult(started=True, successor_id="s"),
            targets=targets,
        )

    def _request(self, layer: "tc.TurnoverLayer") -> "tc.LaunchRequest":
        return tc.LaunchRequest(
            layer=layer,
            task_id="M0-T117",
            event_id="evt-1",
            model_id="claude-opus-4-8",
            effort="xhigh",
            handoff_reference="handoff-1",
            safe_checkpoint_id="ckpt-1",
            failed_fable_execution_id="exec-1",
        )

    def test_worker_successor_env_injects_and_preserves_existing_pairs(self) -> None:
        self.assertNotIn("DISABLE_AUTOUPDATER", os.environ)
        inv = self._launcher()._build_invocation(self._request(tc.TurnoverLayer.WORKER))
        self.assertEqual(inv.env["DISABLE_AUTOUPDATER"], "1")
        # The pre-existing effort/role pairs are preserved (claude_child_env(extra)).
        self.assertEqual(inv.env["SUPERVISOR_SUCCESSOR_EFFORT"], "xhigh")
        self.assertEqual(inv.env["SUPERVISOR_SESSION_ROLE"], "worker")

    def test_orchestrator_successor_env_injects_the_control(self) -> None:
        self.assertNotIn("DISABLE_AUTOUPDATER", os.environ)
        inv = self._launcher()._build_invocation(self._request(tc.TurnoverLayer.ORCHESTRATOR))
        self.assertEqual(inv.env["DISABLE_AUTOUPDATER"], "1")
        self.assertEqual(inv.env["SUPERVISOR_SESSION_ROLE"], "orchestrator")


class CodexScopeTests(unittest.TestCase):
    """AS-5: codex child environments are NOT modified by this change."""

    def test_as5_shared_minimal_env_does_not_inject_the_control(self) -> None:
        os.environ.pop("DISABLE_AUTOUPDATER", None)
        self.assertNotIn("DISABLE_AUTOUPDATER", pc.minimal_env())

    def test_as5_codex_channel_still_uses_the_uninjected_builder(self) -> None:
        # codex_channel builds its child env with the shared minimal_env, NOT the
        # claude-scoped helper; proving it still binds the un-injected builder
        # keeps the scope boundary honest.
        self.assertIs(codex_channel.minimal_env, pc.minimal_env)
        self.assertIsNot(getattr(codex_channel, "claude_child_env", None),
                         pc.claude_child_env)


if __name__ == "__main__":
    unittest.main()
