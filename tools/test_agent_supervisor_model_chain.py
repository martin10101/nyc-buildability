#!/usr/bin/env python3
"""The orchestrator-role model chain, proven with REAL processes (D-007 am.12).

Every "Claude" here is a local Python script launched as a real OS process. There
is no provider, no token, and no network - but there IS a process, and that is
the whole point of this file.

D-007-R605 is the requirement these tests exist for. The V1.2.1 implementation
wrote a first-class `model_substitution` record while the runner kept launching
the exhausted pin: the audit trail asserted a model selection that never happened.
A test that only asserts a switch EVENT was written cannot tell those two apart,
so every test here asserts on what a real spawned process actually received:

* the fake CLI reads `--model` out of its OWN argv, refuses to come up at all when
  that id is marked exhausted (nonzero exit, quota message on stderr, no stream),
  and otherwise reports that exact id back on its stream-json stream;
* it appends `{pid, model, argv}` to a launch log, so the test reads the launched
  model out of a file written by ANOTHER process rather than out of in-process
  bookkeeping.

What that proves: a real OS process was launched, through the real `build_argv`
path, on the exact id the records name, after a simulated exhaustion of the pin.
What it does NOT prove: anything about Anthropic's live quota response. The fake
CLI's refusal is a stand-in for exhaustion; the exact bytes the installed CLI
emits when an account quota is exhausted have not been captured from a live
exhaustion (see `QUOTA_EXHAUSTION_SIGNAL_VERIFIED`), which is why the probe never
infers that reason and the classifier is injected here by the test.
"""
from __future__ import annotations

import contextlib
import json
import pathlib
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import config as cfg  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.claude_runner import ClaudeRunner, RunnerConfig  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewOutcome, map_decision_to_tier  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import CodexDecision, digest_of  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

PIN = "claude-fable-5"
FIRST_FALLBACK = "claude-opus-4-8"
SECOND_FALLBACK = "claude-opus-4-7"
UNLISTED = "claude-opus-5"

# --------------------------------------------------------------------------
# The fake CLI: it reports the --model id it was ACTUALLY launched with
# --------------------------------------------------------------------------

FAKE_CLAUDE_CHAIN = textwrap.dedent('''
    """FAKE claude that echoes the --model id it was really given.

    Env (the supervisor passes only an allowlisted, minimal environment, so the
    log falls back to a fixed name in the process's own cwd - which is the one
    thing the supervisor always sets):
      FAKE_LAUNCH_LOG      append one JSON line per launch: {pid, model, argv}
      FAKE_EXHAUSTED       comma-separated ids that refuse to come up
      FAKE_EXHAUST_AFTER   ids in FAKE_EXHAUSTED only refuse once the log
                           already has this many lines (0 = always refuse)
      FAKE_REPORT_MODEL    report THIS id instead of the one asked for
    """
    import json, os, sys

    argv = sys.argv[1:]
    model = ""
    if "--model" in argv:
        index = argv.index("--model") + 1
        if index < len(argv):
            model = argv[index]

    log_path = os.environ.get("FAKE_LAUNCH_LOG", "") or os.path.join(
        os.getcwd(), "fake_launches.jsonl")
    launches = 0
    if log_path and os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as handle:
            launches = sum(1 for line in handle if line.strip())

    exhausted = [m for m in os.environ.get("FAKE_EXHAUSTED", "").split(",") if m]
    after = int(os.environ.get("FAKE_EXHAUST_AFTER", "0") or 0)

    def record(started):
        if not log_path:
            return
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "model": model,
                                     "argv": argv, "started": started}) + "\\n")

    if model in exhausted and launches >= after:
        record(False)
        sys.stderr.write(
            "API Error: quota exhausted for model " + model + "; usage limit reached\\n")
        raise SystemExit(7)

    record(True)
    reported = os.environ.get("FAKE_REPORT_MODEL", "") or model

    def emit(obj):
        sys.stdout.write(json.dumps(obj) + "\\n")
        sys.stdout.flush()

    emit({"type": "system", "subtype": "init", "session_id": "sess-" + reported,
          "model": reported, "permissionMode": "manual"})
    emit({"type": "assistant", "uuid": "u-a-" + str(os.getpid()),
          "message": {"role": "assistant", "model": reported,
                      "usage": {"input_tokens": 10, "output_tokens": 5}}})
    CHECKPOINT = {
        "schema_version": "1.0.0", "run_id": "run-chain",
        "checkpoint_id": "cp-" + str(os.getpid()),
        "task_id": "M0-T036", "claude_session_id": "sess-" + reported,
        "status": "UNIT_COMPLETE", "summary": "unit on " + reported,
        "starting_sha": "a" * 40, "current_sha": "b" * 40,
        "branch": "task/M0-T036-supervisor-bridge", "worktree": "/fake",
        "proposed_next_action": "await review", "usage": "unknown",
        "context_pressure": "unknown"}
    emit({"type": "result", "subtype": "success", "uuid": "u-r-" + str(os.getpid()),
          "result": json.dumps(CHECKPOINT),
          "usage": {"input_tokens": 10, "output_tokens": 5}})
''')


@contextlib.contextmanager
def script_as_executable(script: pathlib.Path):
    """Run the fake script through the REAL argv builder.

    `build_argv` is patched at module level (the pattern the runner tests already
    use) so the fake is inserted as the interpreter's first argument. Everything
    downstream - the runner's launch AND the launch probe, which both call this
    one function - keeps building the real confirmed argv, including `--model`.
    """
    original = cr.build_argv

    def patched(config: RunnerConfig) -> list[str]:
        argv = original(config)
        return [argv[0], str(script), *argv[1:]]

    cr.build_argv = patched  # type: ignore[assignment]
    try:
        yield
    finally:
        cr.build_argv = original  # type: ignore[assignment]


def quota_classifier(returncode, stderr_text: str) -> str:
    """Recognize THIS fake's exhaustion signal.

    Injected by the test on purpose: the exact signal the installed CLI emits on
    a live account-quota exhaustion has not been captured, and the probe never
    guesses one (`QUOTA_EXHAUSTION_SIGNAL_VERIFIED` is False). What the product
    code owns is everything after the classification; what this function stands in
    for is one line of pattern matching against a signal nobody has recorded yet.
    """
    return cr.QUOTA_EXHAUSTED_REASON if "quota exhausted" in stderr_text.lower() else ""


# --------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------


def decision(**overrides) -> CodexDecision:
    data = dict(
        schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T036",
        reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="Do the next bounded unit.")
    data.update(overrides)
    return CodexDecision(**data)


class FakeReviewer:
    """Always CONTINUE, so the loop reaches its seams."""

    def __init__(self) -> None:
        self.packets: list[dict] = []

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        self.packets.append(dict(packet))
        actual = decision()
        return ReviewOutcome(decision=actual, model_used="fake-review-model",
                             selection_digest="sel", attempts=1,
                             decision_digest=digest_of(actual.to_dict()),
                             tier=map_decision_to_tier(actual))


class ChainTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.script = self.tmp / "fake_claude_chain.py"
        self.script.write_text(FAKE_CLAUDE_CHAIN, encoding="utf-8")
        self.launch_log = self.tmp / "launches.jsonl"
        self.journal = DurableJournal(self.tmp / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run-chain"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T036",
             "allowed_paths": ["tools/agent_supervisor/**"],
             "forbidden_paths": [".github/**"],
             "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T036-supervisor-bridge", stage="phase4")

    # -- what a real process actually received ------------------------------

    def launches(self) -> list[dict]:
        if not self.launch_log.exists():
            return []
        return [json.loads(line) for line in
                self.launch_log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def started_launches(self) -> list[dict]:
        return [entry for entry in self.launches() if entry.get("started")]

    def runner_config(self, model: str, *, exhausted: str = "",
                      exhaust_after: int = 0, report_model: str = "") -> RunnerConfig:
        env = {"FAKE_LAUNCH_LOG": str(self.launch_log),
               "FAKE_EXHAUSTED": exhausted,
               "FAKE_EXHAUST_AFTER": str(exhaust_after),
               "PYTHONIOENCODING": "utf-8"}
        if report_model:
            env["FAKE_REPORT_MODEL"] = report_model
        return RunnerConfig(executable=sys.executable, max_turns=2,
                            timeout_seconds=60.0, close_grace_seconds=10.0,
                            cwd=str(self.tmp), model=model, expected_model=model,
                            extra_env=env)

    def build_loop(self, config: RunnerConfig, *, session_role: str = "orchestrator",
                   mode: str = "supervised", max_cycles: int = 3,
                   chain=(PIN, FIRST_FALLBACK, SECOND_FALLBACK),
                   probe_timeout: float = 60.0) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode=mode, task_id="M0-T036", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=max_cycles, owner_touch_budget=4,
                                 session_role=session_role),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=ClaudeRunner(config, audit=self.audit, run_id=self.run_id),
            reviewer=FakeReviewer(), run_id=self.run_id,
            pinned_model=PIN,
            # A low threshold makes the FIRST unit cross it, so the loop reaches a
            # seam. That is the CONTEXT-ROTATION trigger (D-004-R743..R745), and it
            # is deliberately kept distinct from the quota trigger under test here
            # (D-007-R606): it only gets the run to a safe seam, and the assertions
            # below check the quota records, not the rotation ones.
            context_rotation_threshold=1,
            model_chain=chain,
            model_available=cr.make_launch_probe(
                config, timeout_seconds=probe_timeout,
                classify_unavailable=quota_classifier,
                audit=self.audit, run_id=self.run_id),
            approval_gate=lambda _digest, _prompt: True)

    def at_preflight(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")


# --------------------------------------------------------------------------
# THE hard requirement (D-007-R605)
# --------------------------------------------------------------------------


class RealProcessSwitchTests(ChainTestBase):
    def test_a_real_process_comes_up_on_opus_4_8_after_a_fable_5_exhaustion(self) -> None:
        """A REAL process is launched on claude-opus-4-8 after the pin is exhausted.

        The proof is not a record: it is a line the spawned process wrote itself,
        naming the `--model` value that reached its own argv, plus its own pid.
        """
        self.at_preflight()
        # The pin launches once (cycle 1) and is exhausted from then on: the seam's
        # launch probe of claude-fable-5 genuinely fails to come up.
        config = self.runner_config(PIN, exhausted=PIN, exhaust_after=1)
        loop = self.build_loop(config, max_cycles=2)
        with script_as_executable(self.script):
            run = loop.run("first unit")

        started = self.started_launches()
        models = [entry["model"] for entry in started]
        self.assertEqual(models[0], PIN, "cycle 1 really ran on the pin")
        self.assertIn(FIRST_FALLBACK, models[1:],
                      f"no real process came up on {FIRST_FALLBACK}; launches={self.launches()}")

        # The switched unit: a real OS process, its own pid, the exact id on argv.
        switched = [entry for entry in started if entry["model"] == FIRST_FALLBACK][-1]
        self.assertNotEqual(switched["pid"], None)
        argv = switched["argv"]
        self.assertIn("--model", argv)
        self.assertEqual(argv[argv.index("--model") + 1], FIRST_FALLBACK,
                         "the launched argv itself must carry the exact substitute id")
        self.assertNotIn(UNLISTED, argv)

        # The loop's own launch config agrees with what the process received, and
        # the run did NOT pause.
        self.assertEqual(loop.launched_model(), FIRST_FALLBACK)
        self.assertNotEqual(run.stopped, "rotation_paused_model_unavailable")
        self.assertNotEqual(run.stopped, lp.CHAIN_EXHAUSTED_STOP)

        # The record and the actuation now agree - the V1.2.1 divergence is closed.
        switch_records = [r for r in run.rotations if r.get("substitution")]
        self.assertEqual(len(switch_records), 1)
        record = switch_records[0]
        self.assertEqual(record["model"], FIRST_FALLBACK)
        self.assertEqual(record["launched_model"], FIRST_FALLBACK)
        self.assertEqual(record["exhausted_model"], PIN)
        self.assertEqual(record["chain"], [PIN, FIRST_FALLBACK, SECOND_FALLBACK])
        durable = self.journal.get_state(f"model_substitution/{self.run_id}")
        self.assertTrue(durable["active"])
        self.assertEqual(durable["substitute_model"], FIRST_FALLBACK)
        self.assertEqual(durable["launched_model"], FIRST_FALLBACK)

        # DISTINCT TRIGGER (D-007-R606): the quota switch keeps its own reason code
        # and its own event; the context rotation that got the run to the seam is
        # recorded separately and is not renamed or absorbed.
        self.assertEqual(durable["reason_code"], cr.QUOTA_EXHAUSTED_REASON)
        self.assertEqual(durable["rotation_reason"], "context_threshold")
        events = [r["event_type"] for r in self.audit.read_all()]
        self.assertIn("model_substitution", events)
        self.assertIn("model_launch_probe", events)

    def test_the_switch_is_a_launch_not_a_record_when_actuation_is_impossible(self) -> None:
        """A runner that cannot be rebound REFUSES; it never records a switch.

        The inverse of the defect: rather than writing a `model_substitution`
        record whose launch never changed, the loop raises and records nothing.
        """
        self.at_preflight()

        class UnrebindableRunner:
            def __init__(self) -> None:
                self.calls = 0

            def run_unit(self, _prompt, **_kwargs):
                self.calls += 1
                raise AssertionError("not reached in this test")

        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T036", stage="phase4",
                                 max_cycles=2, session_role="orchestrator"),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority, runner=UnrebindableRunner(),
            reviewer=FakeReviewer(), run_id=self.run_id, pinned_model=PIN,
            model_chain=(PIN, FIRST_FALLBACK),
            model_available=lambda model: (model == FIRST_FALLBACK,
                                           "" if model == FIRST_FALLBACK
                                           else cr.QUOTA_EXHAUSTED_REASON))
        rot.observe_mid_unit(self.journal, reason_code="model_downgrade", detail="d")
        self.journal.set_state(rot.ROTATION_REASON_KEY, "model_downgrade")
        with self.assertRaises(lp.LoopError) as raised:
            loop._rotate_at_seam(cycle=2)
        self.assertEqual(raised.exception.code, "model_actuation_unavailable")
        self.assertIsNone(self.journal.get_state(f"model_substitution/{self.run_id}"))
        self.assertNotIn("model_substitution",
                         [r["event_type"] for r in self.audit.read_all()])


# --------------------------------------------------------------------------
# The mirrored half: returning to the pin (D-007-R605, return leg)
# --------------------------------------------------------------------------


class RealProcessReturnTests(ChainTestBase):
    def test_the_return_to_the_pin_launches_a_real_process_on_the_pin(self) -> None:
        """Once the pin launches again, the next REAL process runs on the pin."""
        self.at_preflight()
        # The pin is exhausted for launches 2..3 only (cycle 1, then the seam probe)
        # and launchable again afterwards, so the run switches away and comes back.
        config = self.runner_config(PIN, exhausted=PIN, exhaust_after=1)
        loop = self.build_loop(config, max_cycles=3)

        calls = {"n": 0}
        real_probe = cr.make_launch_probe(config, timeout_seconds=60.0,
                                          classify_unavailable=quota_classifier,
                                          audit=self.audit, run_id=self.run_id)

        def probe(model: str):
            # Every answer still comes from a REAL launch attempt; the only thing
            # scripted is WHEN the pin recovers, which no fake can decide for us.
            calls["n"] += 1
            if model == PIN and calls["n"] > 2:
                # Re-run the pin against a config where it is no longer exhausted.
                return real_probe_recovered(model)
            return real_probe(model)

        recovered_config = self.runner_config(PIN)
        real_probe_recovered = cr.make_launch_probe(
            recovered_config, timeout_seconds=60.0,
            classify_unavailable=quota_classifier, audit=self.audit, run_id=self.run_id)
        loop._model_available_probe = probe

        with script_as_executable(self.script):
            loop.run("first unit")

        models = [entry["model"] for entry in self.started_launches()]
        self.assertIn(FIRST_FALLBACK, models)
        self.assertEqual(loop.launched_model(), PIN,
                         "after the return, the launch config is the pin again")
        # A real process came up on the pin AFTER one came up on the substitute.
        self.assertGreater(len(models) - 1 - models[::-1].index(PIN),
                           models.index(FIRST_FALLBACK),
                           f"expected a pin launch after the substitute; got {models}")
        ended = self.journal.get_state(f"model_substitution/{self.run_id}")
        self.assertFalse(ended["active"])
        events = [r["event_type"] for r in self.audit.read_all()]
        self.assertIn("model_substitution_ended", events)


# --------------------------------------------------------------------------
# Chain exhaustion, unlisted ids, and the roles that never switch
# --------------------------------------------------------------------------


class ChainExhaustionTests(ChainTestBase):
    def test_no_chain_entry_launches_so_the_run_stops_and_notifies(self) -> None:
        """D-004-R755: nothing launches -> STOP + notify, never a silent continue."""
        self.at_preflight()
        exhausted = ",".join([PIN, FIRST_FALLBACK, SECOND_FALLBACK])
        config = self.runner_config(PIN, exhausted=exhausted, exhaust_after=1)
        loop = self.build_loop(config, max_cycles=3)
        with script_as_executable(self.script):
            run = loop.run("first unit")

        self.assertEqual(run.stopped, lp.CHAIN_EXHAUSTED_STOP)
        self.assertEqual(self.machine.current_state, sm.PAUSED_RECOVERY)
        # NO unit was launched after the exhaustion: exactly one process started,
        # the cycle-1 unit on the pin. Every later launch was a probe that refused.
        started = self.started_launches()
        self.assertEqual([entry["model"] for entry in started], [PIN])
        # Every chain entry was really attempted, in order, by an actual launch.
        attempted = [entry["model"] for entry in self.launches() if not entry["started"]]
        self.assertEqual(attempted[0], PIN, "the pin was probed first")
        self.assertIn(FIRST_FALLBACK, attempted)
        self.assertIn(SECOND_FALLBACK, attempted)
        # No switch was recorded and no substitute became effective.
        self.assertEqual([r for r in run.rotations if r.get("substitution")], [])
        self.assertIsNone(self.journal.get_state(f"model_substitution/{self.run_id}"))
        self.assertEqual(loop.launched_model(), PIN, "nothing was switched to")
        # The owner is notified through the existing surfaces, and the handoff was
        # refreshed under the stop's own reason code.
        self.assertTrue(self.journal.open_asks())
        events = [r for r in self.audit.read_all()
                  if r["event_type"] == lp.CHAIN_EXHAUSTED_STOP]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["detail"]["chain"],
                         [PIN, FIRST_FALLBACK, SECOND_FALLBACK])
        handoff = self.journal.get_state(f"session_handoff/{self.run_id}")
        self.assertEqual(handoff["reason_code"], lp.CHAIN_EXHAUSTED_STOP)

    def test_a_process_that_reports_another_id_does_not_make_that_model_available(self) -> None:
        """D-004-R754: the id asked for is the id that must answer.

        A launch that quietly resolves to Opus 5 is NOT an available claude-opus-4-8,
        and Opus 5 never becomes selectable by being reported.
        """
        config = self.runner_config(FIRST_FALLBACK, report_model=UNLISTED)
        with script_as_executable(self.script):
            result = cr.probe_model_launch(config, FIRST_FALLBACK, timeout_seconds=60.0)
        self.assertFalse(result.available)
        self.assertEqual(result.reason_code, cr.PROBE_MODEL_ID_MISMATCH)
        self.assertIn(UNLISTED, result.observed_models)
        # ...and the process that answered really was launched with the asked-for id.
        argv = self.launches()[-1]["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], FIRST_FALLBACK)

    def test_an_unlisted_id_is_never_selectable_even_if_it_launches(self) -> None:
        """Opus 5 launches perfectly well and is still never chosen: it is not in
        the chain, so it is never probed and never actuated."""
        self.at_preflight()
        config = self.runner_config(PIN, exhausted=f"{PIN},{FIRST_FALLBACK},{SECOND_FALLBACK}",
                                    exhaust_after=1)
        loop = self.build_loop(config, max_cycles=3)
        with script_as_executable(self.script):
            run = loop.run("first unit")
        self.assertEqual(run.stopped, lp.CHAIN_EXHAUSTED_STOP)
        probed = {entry["model"] for entry in self.launches()}
        self.assertNotIn(UNLISTED, probed,
                         "an id outside the chain must never even be attempted")
        # And the loop refuses to actuate one if asked directly.
        with self.assertRaises(lp.LoopError) as raised:
            loop._actuate_model(UNLISTED)
        self.assertEqual(raised.exception.code, "model_not_in_chain")

    def test_a_non_orchestrator_role_pauses_and_launches_nothing_new(self) -> None:
        """D-004-R756/R757: only the orchestrator role walks the chain."""
        self.at_preflight()
        config = self.runner_config(PIN, exhausted=PIN, exhaust_after=1)
        loop = self.build_loop(config, session_role="", max_cycles=3)
        with script_as_executable(self.script):
            run = loop.run("first unit")
        self.assertEqual(run.stopped, "rotation_paused_model_unavailable")
        self.assertEqual([entry["model"] for entry in self.started_launches()], [PIN])
        self.assertIsNone(self.journal.get_state(f"model_substitution/{self.run_id}"))
        # No fallback was even attempted: the worker default never walks the chain.
        attempted = {entry["model"] for entry in self.launches()}
        self.assertNotIn(FIRST_FALLBACK, attempted)
        self.assertNotIn(SECOND_FALLBACK, attempted)

    def test_shadow_observes_and_never_switches(self) -> None:
        self.at_preflight()
        config = self.runner_config(PIN)
        loop = self.build_loop(config, mode="shadow", max_cycles=3)
        with script_as_executable(self.script):
            run = loop.run("only observation")
        self.assertFalse(rot.rotation_pending(self.journal))
        self.assertEqual(run.rotations, ())
        self.assertIsNone(self.journal.get_state(f"model_substitution/{self.run_id}"))
        self.assertEqual([entry["model"] for entry in self.started_launches()], [PIN])


# --------------------------------------------------------------------------
# Crash resume: the REBUILT runner launches on the effective model
# --------------------------------------------------------------------------

CONFIG_TOML = f"""
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["{PIN}", "{FIRST_FALLBACK}", "{SECOND_FALLBACK}"]

[controller]
default_mode = "shadow"

[model_chain]
orchestrator_preference = ["{PIN}", "{FIRST_FALLBACK}", "{SECOND_FALLBACK}"]

[limits]
max_review_packet_bytes = 262144
"""

SELECTION_TOML = f"""
[codex]
review_model = "codex-primary"
advisory_model = "codex-primary"
fallback_models = []

[claude]
model = "{PIN}"
fallback_models = []
"""


class CrashResumeTests(ChainTestBase):
    """cli.py rebuilt the runner on the PIN unconditionally, so a resumed run
    relaunched on the exhausted model while its records said otherwise."""

    def setUp(self) -> None:
        super().setUp()
        # `start` builds the runner itself and passes only a minimal allowlisted
        # environment, so the fake falls back to its cwd - the worktree the
        # supervisor sets. Nothing about the launch is arranged by the test.
        self.launch_log = self.repo / "fake_launches.jsonl"
        self.runtime = self.tmp / "runtime"
        self.config_path = self.tmp / "config.toml"
        self.config_path.write_text(CONFIG_TOML, encoding="utf-8")
        self.selection_path = self.tmp / "model_selection.toml"
        self.selection_path.write_text(SELECTION_TOML, encoding="utf-8")
        self.packet = self.tmp / "M0-T036.json"
        self.packet.write_text(json.dumps({
            "task_id": "M0-T036",
            "allowed_paths": ["tools/agent_supervisor/**"],
            "forbidden_paths": [".github/**"],
            "status": "in_progress",
            "stop_conditions": ["no bypass flags"],
        }), encoding="utf-8")

    def _seed_active_switch(self, run_id: str) -> None:
        """The durable record a crashed, already-switched run leaves behind."""
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for

        runtime_dir = runtime_dir_for(self.repo, base=str(self.runtime))
        journal = DurableJournal(runtime_dir / DB_FILENAME).open()
        try:
            journal.set_state(f"model_substitution/{run_id}", {
                "active": True, "pinned_model": PIN,
                "substitute_model": FIRST_FALLBACK, "effective_model": FIRST_FALLBACK,
                "reason_code": cr.QUOTA_EXHAUSTED_REASON, "cycle": 2,
                "chain": [PIN, FIRST_FALLBACK, SECOND_FALLBACK]})
        finally:
            journal.close()

    def test_effective_model_is_read_from_the_durable_record(self) -> None:
        self.assertEqual(lp.effective_model(self.journal, self.run_id, PIN), PIN)
        self.journal.set_state(f"model_substitution/{self.run_id}",
                               {"active": True, "substitute_model": FIRST_FALLBACK})
        self.assertEqual(lp.effective_model(self.journal, self.run_id, PIN),
                         FIRST_FALLBACK)
        self.journal.set_state(f"model_substitution/{self.run_id}",
                               {"active": False, "substitute_model": FIRST_FALLBACK})
        self.assertEqual(lp.effective_model(self.journal, self.run_id, PIN), PIN)

    def test_a_resumed_run_launches_a_real_process_on_the_effective_model(self) -> None:
        """`start` on a journal carrying an active switch must NOT relaunch on the
        exhausted pin: a real process comes up on the effective model."""
        import contextlib as _contextlib
        import io

        run_id = "run-resume"
        self._seed_active_switch(run_id)
        argv = ["start", "--mode", "supervised",
                "--claude-executable", sys.executable,
                "--codex-executable", sys.executable,
                "--task-packet", str(self.packet),
                "--config", str(self.config_path),
                "--model-selection", str(self.selection_path),
                "--session-role", "orchestrator",
                "--run-id", run_id, "--max-cycles", "1",
                "--unit-timeout", "60",
                "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime), "--json"]
        stdout = io.StringIO()
        with script_as_executable(self.script):
            with _contextlib.redirect_stdout(stdout):
                cli.main(list(argv))

        started = self.started_launches()
        self.assertTrue(started, "the resumed run launched no process at all")
        self.assertEqual(started[0]["model"], FIRST_FALLBACK,
                         "the rebuilt runner must launch on the EFFECTIVE model, not the pin")
        launched_argv = started[0]["argv"]
        self.assertEqual(launched_argv[launched_argv.index("--model") + 1], FIRST_FALLBACK)

    def test_the_runner_start_builds_is_configured_on_the_effective_model(self) -> None:
        """The rebuilt launch config itself, captured where `start` builds it.

        The end-to-end test above proves the resumed PROCESS is right; this one
        pins the specific line G4 named - cli.py rebuilt `RunnerConfig` on the pin
        unconditionally - so the fix cannot regress behind the loop's own rebind.
        """
        import contextlib as _contextlib
        import io

        run_id = "run-capture"
        self._seed_active_switch(run_id)
        captured: list[RunnerConfig] = []
        original = cli.ClaudeRunner

        class CapturingRunner(original):  # type: ignore[misc, valid-type]
            def __init__(self, config, **kwargs):
                captured.append(config)
                super().__init__(config, **kwargs)

        cli.ClaudeRunner = CapturingRunner  # type: ignore[assignment]
        self.addCleanup(setattr, cli, "ClaudeRunner", original)
        argv = ["start", "--mode", "supervised",
                "--claude-executable", sys.executable,
                "--codex-executable", sys.executable,
                "--task-packet", str(self.packet),
                "--config", str(self.config_path),
                "--model-selection", str(self.selection_path),
                "--session-role", "orchestrator",
                "--run-id", run_id, "--max-cycles", "1",
                "--unit-timeout", "60",
                "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime), "--json"]
        with script_as_executable(self.script):
            with _contextlib.redirect_stdout(io.StringIO()):
                cli.main(list(argv))
        self.assertTrue(captured, "start never built a runner")
        self.assertEqual(captured[0].model, FIRST_FALLBACK)
        self.assertEqual(captured[0].expected_model, FIRST_FALLBACK,
                         "a pinned expected_model would flag every event as a downgrade")

    def test_a_clean_journal_still_launches_on_the_pin(self) -> None:
        """The mirror: with no active switch the resumed run is on the pin."""
        import contextlib as _contextlib
        import io

        argv = ["start", "--mode", "supervised",
                "--claude-executable", sys.executable,
                "--codex-executable", sys.executable,
                "--task-packet", str(self.packet),
                "--config", str(self.config_path),
                "--model-selection", str(self.selection_path),
                "--run-id", "run-clean", "--max-cycles", "1",
                "--unit-timeout", "60",
                "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime), "--json"]
        stdout = io.StringIO()
        with script_as_executable(self.script):
            with _contextlib.redirect_stdout(stdout):
                cli.main(list(argv))
        started = self.started_launches()
        self.assertTrue(started)
        self.assertEqual(started[0]["model"], PIN)


# --------------------------------------------------------------------------
# The chain is configuration, not judgement (D-004-R751/R758)
# --------------------------------------------------------------------------


class ModelChainConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()

    def _write(self, body: str) -> pathlib.Path:
        path = self.tmp / "config.toml"
        path.write_text(body, encoding="utf-8")
        return path

    def test_the_default_chain_is_the_owners_order(self) -> None:
        self.assertEqual(cfg.DEFAULT_ORCHESTRATOR_MODEL_CHAIN,
                         (PIN, FIRST_FALLBACK, SECOND_FALLBACK))
        self.assertNotIn(UNLISTED, cfg.DEFAULT_ORCHESTRATOR_MODEL_CHAIN)

    def test_an_absent_section_falls_back_to_that_exact_order(self) -> None:
        config = cfg.load_controller_config(self._write(
            '[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'))
        self.assertEqual(config.model_chain.entries,
                         (PIN, FIRST_FALLBACK, SECOND_FALLBACK))

    def test_the_owner_may_reorder_the_chain_in_the_immutable_config(self) -> None:
        config = cfg.load_controller_config(self._write(
            '[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'
            f'[model_chain]\norchestrator_preference = ["{FIRST_FALLBACK}", "{PIN}"]\n'))
        self.assertEqual(config.model_chain.entries, (FIRST_FALLBACK, PIN))

    def test_an_empty_or_malformed_chain_is_refused(self) -> None:
        for body, code in (
            ('[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'
             '[model_chain]\norchestrator_preference = []\n', "empty_model_chain"),
            ('[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'
             '[model_chain]\nmodels = ["a"]\n', "unknown_model_chain_key"),
            ('[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'
             '[model_chain]\norchestrator_preference = ["a", "a"]\n', "duplicate_model"),
            ('[codex]\nallowed_models = []\n[claude]\nallowed_models = []\n'
             '[model_chain]\norchestrator_preference = [" a "]\n', "bad_model_name"),
        ):
            with self.subTest(code=code):
                with self.assertRaises(cfg.ConfigError) as raised:
                    cfg.load_controller_config(self._write(body))
                self.assertEqual(raised.exception.code, code)

    def test_the_walk_never_leaves_the_chain(self) -> None:
        chain = cfg.ModelChain(entries=(PIN, FIRST_FALLBACK, SECOND_FALLBACK))
        self.assertEqual(chain.candidates_after(PIN), (FIRST_FALLBACK, SECOND_FALLBACK))
        self.assertEqual(chain.candidates_after(FIRST_FALLBACK), (SECOND_FALLBACK,))
        self.assertEqual(chain.candidates_after(SECOND_FALLBACK), ())
        self.assertNotIn(UNLISTED, chain)
        # An unlisted current model starts the walk at the head, still inside the
        # chain, and never re-offers the id that just failed.
        self.assertEqual(chain.candidates_after("claude-unlisted-pin"),
                         (PIN, FIRST_FALLBACK, SECOND_FALLBACK))

    def test_the_ids_are_exact_strings_with_no_aliasing(self) -> None:
        chain = cfg.ModelChain()
        for near_miss in ("claude-opus-48", "Claude-Opus-4-8", "opus-4-8",
                          "claude-opus-4-8 ", UNLISTED):
            with self.subTest(near_miss=near_miss):
                self.assertNotIn(near_miss, chain)
        self.assertIn(FIRST_FALLBACK, chain)


# --------------------------------------------------------------------------
# The runner rebind itself
# --------------------------------------------------------------------------


class RunnerRebindTests(unittest.TestCase):
    def test_with_model_moves_both_model_and_expected_model(self) -> None:
        runner = ClaudeRunner(RunnerConfig(executable="claude", model=PIN,
                                           expected_model=PIN))
        switched = runner.with_model(FIRST_FALLBACK)
        self.assertEqual(switched.config.model, FIRST_FALLBACK)
        self.assertEqual(switched.config.expected_model, FIRST_FALLBACK,
                         "a stale expected_model would flag every event as a downgrade")
        argv = cr.build_argv(switched.config)
        self.assertEqual(argv[argv.index("--model") + 1], FIRST_FALLBACK)
        # The original runner is untouched: a copy, never a mutation.
        self.assertEqual(runner.config.model, PIN)

    def test_a_rebind_never_repairs_the_id(self) -> None:
        runner = ClaudeRunner(RunnerConfig(executable="claude", model=PIN))
        for bad in ("", "  ", " claude-opus-4-8", "claude-opus-4-8\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(cr.RunnerError) as raised:
                    runner.with_model(bad)
                self.assertEqual(raised.exception.code, "bad_model_rebind")


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
