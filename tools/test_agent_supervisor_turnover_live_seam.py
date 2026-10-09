#!/usr/bin/env python3
"""M0-T080: real session continuity, the full turnover seam, approved-model routing.

Three reproduced defects are pinned here (supervisor-freeze §2/§3, AD-093):

* **The invented session identity.** `rotation.new_session_id` minted
  `sup-<uuid4>` and the loop stored it where the NEW SESSION's identity belonged.
  `RunnerConfig.resume_session_id` existed and `build_argv` knew how to emit
  `--resume`, but no production code ever assigned it, so a "completed rotation"
  launched a fresh, UNRESUMED session while recording rotation success.
* **The bypassed turnover protocol.** All three loop seams wrote a smaller,
  non-S11.3 snapshot and called `RotationLedger.complete_rotation` directly, so
  `assert_safe_to_rotate`, `verify_handoff`, `store_verified_handoff`, and
  `assert_ready_checkpoint` had NO production caller at all.
* **The code-default model chain.** `config.DEFAULT_ORCHESTRATOR_MODEL_CHAIN`,
  `turnover_controller.ALLOWED_SUCCESSOR_MODEL_ID`, and two `cli.py` defaults
  named model ids in SOURCE, which D-023-R013 prohibits.

EVIDENCE LABEL (D-023-R021). Everything below is UNIT / FAKE-RUNNER proof. No
live Claude or Codex provider is contacted anywhere in this file. The exact-id
LIVE LAUNCH PROBE seam is exercised by injected fakes only; running a real probe
against a real provider CLI is an owner-checkpoint act on the controller, and no
claim is made here about any provider's live behaviour. The three tests that
spawn a process spawn a LOCAL PYTHON SCRIPT, which is a real OS process and not a
provider.
"""
from __future__ import annotations

import contextlib
import dataclasses
import json
import os
import pathlib
import sys
import tempfile
import textwrap
import unittest
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import approved_models as am  # noqa: E402
from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import config as cfg  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import loop_turnover as lt  # noqa: E402
from tools.agent_supervisor import model_change_ipc as ipc  # noqa: E402
from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor import session_continuity as sc  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor import turnover_seam as ts  # noqa: E402
from tools.agent_supervisor.claude_runner import ClaudeRunner, RunnerConfig  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.turnover_controller import (  # noqa: E402
    ALLOWED_SUCCESSOR_EFFORT,
    ApprovedSuccessor,
    LaunchResult,
    TurnoverContext,
    TurnoverController,
    TurnoverLayer,
    TurnoverStatus,
)
from tools.test_agent_supervisor_loop import (  # noqa: E402
    HEAD_SHA,
    FakeRunner,
    LoopTestBase,
    checkpoint as make_checkpoint,
    run_result,
)

PIN = "claude-pinned"
APPROVED_A = "model-approved-a"
APPROVED_B = "model-approved-b"
UNAPPROVED = "model-never-approved"


# --------------------------------------------------------------------------
# Shared fakes. Nothing here contacts a provider.
# --------------------------------------------------------------------------


class FakeApprovedConfig:
    """The approved-model surface of an immutable controller config."""

    def __init__(self, entries: tuple[str, ...] = (APPROVED_A, APPROVED_B),
                 identity: str = "config-identity-1") -> None:
        self._entries = tuple(entries)
        self._identity = identity

    @property
    def approved_models(self) -> am.ApprovedModels:
        return am.ApprovedModels(entries=self._entries, source="fake-config.toml")

    def allowlist(self, provider: str) -> tuple[str, ...]:
        return (APPROVED_A, APPROVED_B, UNAPPROVED) if provider == "claude" else ("codex-x",)

    def digest(self) -> str:
        return self._identity


def probe_all_ok(_model: str) -> am.ProbeOutcome:
    return am.ProbeOutcome(ok=True, cli_version="cli-v1")


def probe_none_ok(model: str) -> am.ProbeOutcome:
    return am.ProbeOutcome(ok=False, cli_version="cli-v1", reason_code="quota_exhausted",
                           detail=f"{model} did not come up")


def probe_only(*available: str):
    def _probe(model: str) -> am.ProbeOutcome:
        if model in available:
            return am.ProbeOutcome(ok=True, cli_version="cli-v1")
        return am.ProbeOutcome(ok=False, cli_version="cli-v1",
                               reason_code="quota_exhausted", detail="not available")
    return _probe


class MemoryJournal:
    """A dict-backed journal exposing only what these tests exercise."""

    def __init__(self) -> None:
        self.state: dict[str, Any] = {}
        self.asks: list[Any] = []

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value

    def pending_effects(self):
        return []

    def open_asks(self):
        return list(self.asks)

    def all_state(self):
        return dict(self.state)


def good_facts(**overrides) -> ts.SeamFacts:
    data: dict[str, Any] = dict(
        task_id="M0-T080", stage="build", branch="task/M0-T080",
        worktree="/repo/wt", head_sha="a" * 40,
        exact_next_action="dispatch the next bounded unit under the same authority",
        reason_code="context_threshold", forbidden_scope=(".github/**",),
        last_checkpoint_id="cp-7")
    data.update(overrides)
    return ts.SeamFacts(**data)


def resume_decision(session_id: str = "prov-1") -> sc.ContinuityDecision:
    return sc.ContinuityDecision(mode=sc.RESUME, provider_session_id=session_id,
                                 successor_model=PIN, session_model=PIN,
                                 reason="test resume")


def reorientation_decision() -> sc.ContinuityDecision:
    return sc.ContinuityDecision(mode=sc.REORIENTATION, none_reason=sc.CROSS_MODEL,
                                 none_reasons=(sc.CROSS_MODEL,),
                                 successor_model=APPROVED_B, session_model=PIN,
                                 reason="test reorientation")


# --------------------------------------------------------------------------
# AS-1 / AS-2: the PROVIDER session identity, off the real stream
# --------------------------------------------------------------------------

FAKE_CLAUDE_SESSION = textwrap.dedent('''
    """FAKE claude that emits a configurable session-id shape. No provider."""
    import json, os, sys

    def emit(obj):
        sys.stdout.write(json.dumps(obj) + "\\n")
        sys.stdout.flush()

    shape = os.environ.get("FAKE_SESSION_SHAPE", "init")
    first = os.environ.get("FAKE_SESSION_ID", "prov-session-1")
    second = os.environ.get("FAKE_SESSION_ID_2", "prov-session-2")

    if shape in ("init", "conflict"):
        emit({"type": "system", "subtype": "init", "session_id": first,
              "model": "m", "permissionMode": "manual"})
    CHECKPOINT = {
        "schema_version": "1.0.0", "run_id": "run-seam", "checkpoint_id": "cp-1",
        "task_id": "M0-T080", "claude_session_id": first, "status": "UNIT_COMPLETE",
        "summary": "unit done", "starting_sha": "a" * 40, "current_sha": "b" * 40,
        "branch": "task/M0-T080", "worktree": "/repo/wt",
        "proposed_next_action": "await review", "usage": "unknown",
        "context_pressure": "unknown"}
    reported = second if shape == "conflict" else first
    # `result_only` is the RESUMED-session shape: the CLI stamps the id on the
    # ordinary events instead of opening with a system/init event.
    emit({"type": "result", "subtype": "success", "uuid": "u-1",
          "session_id": reported, "result": json.dumps(CHECKPOINT),
          "usage": {"input_tokens": 1, "output_tokens": 1}})
''')


@contextlib.contextmanager
def script_as_executable(script: pathlib.Path):
    """Insert the fake script as the interpreter's first argument (the pattern
    `test_agent_supervisor_model_chain.py` already uses), so the REAL argv builder
    and the REAL runner are exercised."""
    original = cr.build_argv

    def patched(config: RunnerConfig) -> list[str]:
        argv = original(config)
        return [argv[0], str(script), *argv[1:]]

    cr.build_argv = patched  # type: ignore[assignment]
    try:
        yield
    finally:
        cr.build_argv = original  # type: ignore[assignment]


class ProviderSessionParsingTests(unittest.TestCase):
    """AS-1: the id `--resume` needs comes off the provider's own stream."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.script = self.tmp / "fake_claude_session.py"
        self.script.write_text(FAKE_CLAUDE_SESSION, encoding="utf-8")

    def _run(self, shape: str) -> cr.RunResult:
        config = RunnerConfig(
            executable=sys.executable, max_turns=1, timeout_seconds=60.0,
            close_grace_seconds=10.0, cwd=str(self.tmp), model="m", expected_model="m",
            extra_env={"FAKE_SESSION_SHAPE": shape, "PYTHONIOENCODING": "utf-8"})
        with script_as_executable(self.script):
            return ClaudeRunner(config, run_id="run-seam").run_unit("do the unit")

    def test_the_session_id_is_read_from_the_init_event(self) -> None:
        result = self._run("init")
        self.assertEqual(result.session_id, "prov-session-1")
        self.assertEqual(result.session_id_conflict, "")

    def test_a_stream_with_no_init_event_still_yields_the_session_id(self) -> None:
        # THE DEFECT: the runner read `session_id` only from `system`/`init`, so a
        # stream that opened without one - notably a RESUMED session, where the CLI
        # stamps the id on the ordinary events - produced an EMPTY id and made the
        # session unresumable from then on.
        result = self._run("result_only")
        self.assertEqual(result.session_id, "prov-session-1")

    def test_two_different_ids_are_an_ambiguity_not_a_last_one_wins(self) -> None:
        result = self._run("conflict")
        self.assertEqual(result.session_id, "prov-session-1", "FIRST wins, never last")
        self.assertIn("ambiguous", result.session_id_conflict)


class ResumeActuationTests(unittest.TestCase):
    """AS-2: a resume that does not reach the launch is not a resume."""

    def test_with_resume_puts_the_provider_id_into_the_real_argv(self) -> None:
        runner = ClaudeRunner(RunnerConfig(
            executable="claude", model="m", expected_model="m",
            resume_capability_verified=True))
        resumed = runner.with_resume("prov-session-1")
        self.assertEqual(resumed.config.resume_session_id, "prov-session-1")
        argv = cr.build_argv(resumed.config)
        self.assertEqual(argv[argv.index("--resume") + 1], "prov-session-1")
        # A copy, never a mutation: the outgoing runner keeps its own config.
        self.assertEqual(runner.config.resume_session_id, "")

    def test_an_unverified_resume_capability_still_refuses_to_emit_the_flag(self) -> None:
        runner = ClaudeRunner(RunnerConfig(executable="claude", model="m"))
        with self.assertRaises(cr.RunnerError) as raised:
            cr.build_argv(runner.with_resume("prov-session-1").config)
        self.assertEqual(raised.exception.code, "resume_capability_unverified")

    def test_a_supervisor_internal_rotation_key_can_never_be_resumed(self) -> None:
        runner = ClaudeRunner(RunnerConfig(executable="claude", model="m",
                                           resume_capability_verified=True))
        with self.assertRaises(cr.RunnerError) as raised:
            runner.with_resume(rot.new_rotation_record_key())
        self.assertEqual(raised.exception.code, "internal_key_as_session_id")

    def test_a_resume_id_is_never_repaired(self) -> None:
        runner = ClaudeRunner(RunnerConfig(executable="claude", model="m",
                                           resume_capability_verified=True))
        for bad in ("", "  ", " prov-1", "prov-1\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(cr.RunnerError) as raised:
                    runner.with_resume(bad)
                self.assertEqual(raised.exception.code, "bad_resume_rebind")


# --------------------------------------------------------------------------
# AS-3: resume, or an EXPLICIT reorientation - never a silent middle
# --------------------------------------------------------------------------


class ContinuityDecisionTests(unittest.TestCase):
    def _recorded(self, **overrides) -> sc.ProviderSession:
        data: dict[str, Any] = dict(session_id="prov-1", model_id=PIN,
                                    run_id="run-1", cycle=1,
                                    recorded_at_utc="2026-08-21T00:00:00+00:00",
                                    recorded_at_epoch=1000.0)
        data.update(overrides)
        return sc.ProviderSession(**data)

    def test_a_real_resume_when_everything_lines_up(self) -> None:
        decision = sc.decide_continuity(
            recorded=self._recorded(), successor_model=PIN,
            rotation_reason="session_relaunch", resume_capability_verified=True)
        self.assertTrue(decision.resumed)
        self.assertEqual(decision.provider_session_id, "prov-1")
        self.assertEqual(decision.none_reason, "")
        self.assertEqual(decision.to_dict()["continuity_mode"], "resume")

    def test_no_recorded_session_is_a_named_reorientation(self) -> None:
        decision = sc.decide_continuity(
            recorded=None, successor_model=PIN, rotation_reason="session_relaunch",
            resume_capability_verified=True)
        self.assertFalse(decision.resumed)
        self.assertEqual(decision.none_reason, sc.NO_RECORDED_SESSION)
        self.assertEqual(decision.provider_session_id, "")

    def test_a_cross_model_rotation_can_never_resume(self) -> None:
        decision = sc.decide_continuity(
            recorded=self._recorded(), successor_model=APPROVED_B,
            rotation_reason="session_relaunch", resume_capability_verified=True)
        self.assertIn(sc.CROSS_MODEL, decision.none_reasons)

    def test_a_context_shedding_rotation_can_never_resume(self) -> None:
        # Resuming the same session would carry the very context the rotation
        # exists to drop straight back into the successor (S11.3).
        for reason in sorted(sc.CONTEXT_SHEDDING_REASONS):
            with self.subTest(reason=reason):
                decision = sc.decide_continuity(
                    recorded=self._recorded(), successor_model=PIN,
                    rotation_reason=reason, resume_capability_verified=True)
                self.assertIn(sc.CONTEXT_SHEDDING_ROTATION, decision.none_reasons)

    def test_an_unknown_recorded_model_can_never_resume(self) -> None:
        # M0-T080 correction U2 (G3 I-3). CROSS_MODEL used to require BOTH ids to
        # be non-empty, so a recorded session whose model was unknown ("") plus a
        # KNOWN different successor produced a clean `resume` with no reasons at
        # all - maximum ignorance read as "no objection". CLAUDE.md principle 3:
        # unknown is an impossibility, not a pass.
        decision = sc.decide_continuity(
            recorded=self._recorded(model_id=""), successor_model=APPROVED_B,
            rotation_reason="session_relaunch", resume_capability_verified=True)
        self.assertFalse(decision.resumed)
        self.assertIn(sc.CROSS_MODEL, decision.none_reasons)

    def test_an_unknown_successor_model_can_never_resume(self) -> None:
        # The mirror case: the session's model is known but the successor's is not.
        decision = sc.decide_continuity(
            recorded=self._recorded(model_id=PIN), successor_model="",
            rotation_reason="session_relaunch", resume_capability_verified=True)
        self.assertFalse(decision.resumed)
        self.assertIn(sc.CROSS_MODEL, decision.none_reasons)

    def test_both_models_unknown_can_never_resume(self) -> None:
        decision = sc.decide_continuity(
            recorded=self._recorded(model_id=""), successor_model="",
            rotation_reason="session_relaunch", resume_capability_verified=True)
        self.assertFalse(decision.resumed)
        self.assertIn(sc.CROSS_MODEL, decision.none_reasons)

    def test_a_made_up_primary_none_reason_is_refused(self) -> None:
        # M0-T080 correction U14 (G3 M-2): only the tuple was validated, so the
        # PRIMARY reason - the one every record and message quotes - could be
        # anything at all.
        with self.assertRaises(sc.ContinuityError) as raised:
            sc.ContinuityDecision(mode=sc.REORIENTATION, none_reason="looked_fine")
        self.assertEqual(raised.exception.code, "unknown_none_reason")

    def test_a_session_recorded_by_another_run_is_not_this_runs_session(self) -> None:
        # M0-T080 correction U14 (G4 F6): the record is keyed per CHECKOUT, so
        # run B could read run A's leftover session - and then archive it, or
        # offer it to a --resume.
        journal = MemoryJournal()
        sc.record_provider_session(journal, session_id="prov-1", model_id=PIN,
                                   run_id="run-A")
        self.assertIsNone(sc.recorded_provider_session(journal, run_id="run-B"))
        self.assertEqual(
            sc.recorded_provider_session(journal, run_id="run-A").session_id, "prov-1")
        # Unscoped reads still see it: the standalone watchdog runs after the
        # orchestrator process is gone and legitimately wants the last session.
        self.assertEqual(sc.recorded_provider_session(journal).session_id, "prov-1")

    def test_an_unprobed_resume_capability_can_never_resume(self) -> None:
        decision = sc.decide_continuity(
            recorded=self._recorded(), successor_model=PIN,
            rotation_reason="session_relaunch", resume_capability_verified=False)
        self.assertIn(sc.RESUME_CAPABILITY_UNVERIFIED, decision.none_reasons)

    def test_an_age_bound_is_applied_only_when_a_caller_supplies_one(self) -> None:
        # Nothing on this build knows the provider's real session lifetime, and
        # CLAUDE.md principle 3 forbids guessing it, so there is no default bound.
        recorded = self._recorded()
        unbounded = sc.decide_continuity(
            recorded=recorded, successor_model=PIN, rotation_reason="session_relaunch",
            resume_capability_verified=True, now_epoch=10_000_000.0)
        self.assertTrue(unbounded.resumed)
        bounded = sc.decide_continuity(
            recorded=recorded, successor_model=PIN, rotation_reason="session_relaunch",
            resume_capability_verified=True, max_age_seconds=60.0,
            now_epoch=10_000_000.0)
        self.assertIn(sc.PROVIDER_SESSION_EXPIRED, bounded.none_reasons)

    def test_every_impossibility_is_reported_not_just_the_first(self) -> None:
        decision = sc.decide_continuity(
            recorded=self._recorded(), successor_model=APPROVED_B,
            rotation_reason="context_threshold", resume_capability_verified=False)
        self.assertEqual(set(decision.none_reasons),
                         {sc.CROSS_MODEL, sc.CONTEXT_SHEDDING_ROTATION,
                          sc.RESUME_CAPABILITY_UNVERIFIED})

    def test_a_resume_without_an_id_and_a_blank_reorientation_are_unconstructible(self) -> None:
        with self.assertRaises(sc.ContinuityError) as raised:
            sc.ContinuityDecision(mode=sc.RESUME)
        self.assertEqual(raised.exception.code, "resume_without_session_id")
        with self.assertRaises(sc.ContinuityError) as raised:
            sc.ContinuityDecision(mode=sc.REORIENTATION)
        self.assertEqual(raised.exception.code, "reorientation_without_reason")
        with self.assertRaises(sc.ContinuityError) as raised:
            sc.ContinuityDecision(mode="probably_resumed")
        self.assertEqual(raised.exception.code, "unknown_continuity_mode")

    def test_an_empty_session_id_never_overwrites_a_recorded_one(self) -> None:
        journal = MemoryJournal()
        sc.record_provider_session(journal, session_id="prov-1", model_id=PIN)
        self.assertIsNone(sc.record_provider_session(journal, session_id=""))
        self.assertEqual(sc.recorded_provider_session(journal).session_id, "prov-1")


# --------------------------------------------------------------------------
# AS-4: the FULL S11.3 turnover the loop seams used to skip
# --------------------------------------------------------------------------


class _Facts:
    """The four attributes seam_safety_state reads from SeamFacts."""

    def __init__(self) -> None:
        self.head_sha = "a" * 40
        self.branch = "task/M0-T107-plugin-portability"
        self.worktree = "/repo/wt"
        self.stage = "build"


class _Ask:
    def __init__(self, ask_id: str) -> None:
        self.ask_id = ask_id


class SeamSafetyFeedReconciliationTests(unittest.TestCase):
    """M0-T115 correction round (G3 BLOCKER-1; D-024-R274): the rotation
    seam's approval_pending feed is the FOURTH open_asks() consumer and must
    apply the broker reconciliation - the M0-T113 live-restart defect class
    would otherwise refuse the first rotation seam of any pre-fix journal."""

    def setUp(self) -> None:
        self.journal = MemoryJournal()
        self.facts = _Facts()

    def _broker_ask(self, request_id: str, status: str | None) -> None:
        self.journal.asks.append(_Ask(f"ask_{request_id}"))
        if status is not None:
            self.journal.state[f"approval/{request_id}"] = {
                "request_id": request_id, "status": status}

    def test_a_pre_fix_denied_journal_does_not_refuse_the_rotation_seam(
            self) -> None:
        self._broker_ask("9f45b2ca", "DENIED")
        safety = lt.seam_safety_state(self.journal, self.facts)
        self.assertFalse(safety.approval_pending)

    def test_a_pre_fix_approved_journal_does_not_refuse_the_rotation_seam(
            self) -> None:
        self._broker_ask("c73f9247", "APPROVED_ONCE")
        safety = lt.seam_safety_state(self.journal, self.facts)
        self.assertFalse(safety.approval_pending)

    def test_a_pending_request_still_refuses_the_seam(self) -> None:
        self._broker_ask("7e4b33d8", "PENDING_OWNER")
        safety = lt.seam_safety_state(self.journal, self.facts)
        self.assertTrue(safety.approval_pending)

    def test_a_broker_ask_with_no_record_still_refuses_the_seam(self) -> None:
        self._broker_ask("deadbeef", None)
        safety = lt.seam_safety_state(self.journal, self.facts)
        self.assertTrue(safety.approval_pending)

    def test_a_non_broker_ask_still_refuses_the_seam(self) -> None:
        self.journal.asks.append(_Ask("rotation_pause/run-1/3"))
        safety = lt.seam_safety_state(self.journal, self.facts)
        self.assertTrue(safety.approval_pending)


class SeamTurnoverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.journal = MemoryJournal()
        self.seam = ts.SeamTurnover(journal=self.journal, run_id="run-1")

    def _safe(self) -> rot.RotationSafetyState:
        return ts.safety_state_from_run(head_sha="a" * 40, branch="task/M0-T080",
                                        worktree="/repo/wt", task_stage="build")

    def test_an_unsafe_moment_refuses_before_anything_durable_is_written(self) -> None:
        unsafe = ts.safety_state_from_run(
            open_asks=[object()], head_sha="a" * 40, branch="b",
            worktree="/w", task_stage="build")
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.execute(facts=good_facts(), safety_state=unsafe,
                              continuity=reorientation_decision(),
                              previous_provider_session_id="prov-1",
                              successor_model=APPROVED_B)
        self.assertEqual(raised.exception.code, "unsafe_seam")
        self.assertIsNone(self.seam.ledger.stored_handoff())
        self.assertEqual(self.seam.ledger.archived_sessions(), ())

    def test_an_unaccounted_effect_or_an_unknown_sha_is_an_unsafe_moment(self) -> None:
        for label, state in (
            ("pending effect", ts.safety_state_from_run(
                pending_effects=[object()], head_sha="a" * 40, branch="b",
                worktree="/w", task_stage="build")),
            ("unknown sha", ts.safety_state_from_run(
                head_sha="", branch="b", worktree="/w", task_stage="build")),
            ("unknown worktree", ts.safety_state_from_run(
                head_sha="a" * 40, branch="b", worktree="", task_stage="build")),
        ):
            with self.subTest(label=label):
                with self.assertRaises(ts.SeamTurnoverError):
                    ts.assert_safe_seam(state)

    def test_the_full_handoff_is_built_verified_and_stored(self) -> None:
        result = self.seam.execute(
            facts=good_facts(), safety_state=self._safe(),
            continuity=reorientation_decision(),
            previous_provider_session_id="prov-1", successor_model=APPROVED_B)
        stored = self.seam.ledger.stored_handoff()
        self.assertIsNotNone(stored)
        self.assertEqual(stored["handoff_digest"], result.handoff_digest)
        # Verified DETERMINISTICALLY, and the record says so - it never names a
        # model that did not review anything.
        self.assertEqual(result.verification.model_used, ts.DETERMINISTIC_VERIFIER)
        self.assertTrue(result.verification.verified)
        # All fourteen S11.3 fields are present and the handoff validates.
        handoff = rot.Handoff.from_dict(stored["handoff"])
        rot.validate_handoff(handoff)
        for entry in ts.STRUCTURAL_FORBIDDEN_SCOPE:
            self.assertIn(entry, handoff.forbidden_scope)

    def test_the_deterministic_verifier_actually_detects_a_wrong_handoff(self) -> None:
        # A rubber stamp would pass this; the re-derivation must not.
        facts = good_facts()
        handoff = ts.build_handoff(facts)
        tampered = ts.build_handoff(good_facts(branch="task/somewhere-else"))
        verdict = ts.deterministic_verdict(tampered, facts)
        self.assertFalse(verdict["verified"])
        self.assertTrue(verdict["findings"])
        self.assertIn("branch", verdict["findings"][0])
        # And the good one passes, so the check is not simply always-fail.
        self.assertTrue(ts.deterministic_verdict(handoff, facts)["verified"])

    def test_an_independent_fact_source_can_actually_refuse_the_rotation(self) -> None:
        # M0-T080 correction U3 (a-arm). Without an independent source the
        # deterministic verdict compares the handoff to the same `facts` it was
        # built from and cannot diverge. With one wired, the WORLD is
        # authoritative and a divergence refuses.
        seam = ts.SeamTurnover(
            journal=MemoryJournal(), run_id="run-1",
            fact_source=lambda: {"branch": "task/somewhere-else",
                                 "head_sha": "a" * 40})
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            seam.execute(facts=good_facts(), safety_state=self._safe(),
                         continuity=reorientation_decision(),
                         previous_provider_session_id="prov-1",
                         successor_model=APPROVED_B)
        self.assertEqual(raised.exception.code, "handoff_unverified")
        self.assertTrue(any("branch" in f for f in raised.exception.detail["findings"]))
        self.assertIsNone(seam.ledger.stored_handoff())

    def test_an_agreeing_independent_source_is_recorded_as_the_stronger_check(self) -> None:
        facts = good_facts()
        seam = ts.SeamTurnover(
            journal=MemoryJournal(), run_id="run-1",
            fact_source=lambda: {"task_and_stage": f"{facts.task_id} @ {facts.stage}",
                                 "branch": facts.branch, "worktree": facts.worktree,
                                 "exact_next_action": facts.exact_next_action,
                                 "head_sha": facts.head_sha})
        result = seam.execute(facts=facts, safety_state=self._safe(),
                              continuity=reorientation_decision(),
                              previous_provider_session_id="prov-1",
                              successor_model=APPROVED_B)
        self.assertEqual(result.verification.model_used,
                         ts.DETERMINISTIC_INDEPENDENT_VERIFIER)
        self.assertNotEqual(ts.DETERMINISTIC_INDEPENDENT_VERIFIER,
                            ts.DETERMINISTIC_VERIFIER,
                            "the two checks must be labelled differently")

    def test_a_fact_source_that_raises_refuses_instead_of_downgrading(self) -> None:
        def exploding():
            raise RuntimeError("git is unavailable")

        seam = ts.SeamTurnover(journal=MemoryJournal(), run_id="run-1",
                               fact_source=exploding)
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            seam.execute(facts=good_facts(), safety_state=self._safe(),
                         continuity=reorientation_decision(),
                         previous_provider_session_id="prov-1",
                         successor_model=APPROVED_B)
        self.assertEqual(raised.exception.code, "handoff_fact_source_failed")

    def test_the_verdict_states_its_own_scope_rather_than_implying_more(self) -> None:
        # M0-T080 correction U3 (b-arm): the record must not let a reader infer
        # 14-field independent re-derivation from a 6-field consistency check.
        verdict = ts.deterministic_verdict(ts.build_handoff(good_facts()), good_facts())
        self.assertEqual(verdict["model_used"], ts.DETERMINISTIC_VERIFIER)
        self.assertIn("consistency", verdict["model_used"])
        scope = verdict["scope"]
        self.assertIn("in-memory", scope["value_source"])
        self.assertEqual(len(scope["not_re_derived"]), 8)
        self.assertIn("completed_work", scope["not_re_derived"])
        self.assertIn("14", scope["completeness"])

    def test_an_unverified_handoff_is_never_carried_into_a_successor(self) -> None:
        seam = ts.SeamTurnover(journal=MemoryJournal(), run_id="run-1",
                               verifier=lambda h: {"model_used": "reviewer-x",
                                                   "handoff_digest": h.digest(),
                                                   "verified": False,
                                                   "findings": ["the SHA does not match"]},
                               review_model="reviewer-x")
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            seam.execute(facts=good_facts(), safety_state=self._safe(),
                         continuity=reorientation_decision(),
                         previous_provider_session_id="prov-1",
                         successor_model=APPROVED_B)
        self.assertEqual(raised.exception.code, "handoff_unverified")
        self.assertIsNone(seam.ledger.stored_handoff())

    def test_a_reorientation_carries_both_identities_and_archives_the_old_session(self) -> None:
        result = self.seam.execute(
            facts=good_facts(), safety_state=self._safe(),
            continuity=reorientation_decision(),
            previous_provider_session_id="prov-1", successor_model=APPROVED_B)
        record = self.journal.get_state("last_rotation")
        self.assertTrue(record["rotation_record_key"].startswith("sup-rot-"))
        self.assertEqual(record["previous_provider_session_id"], "prov-1")
        self.assertEqual(record["continuity_mode"], "reorientation")
        self.assertEqual(record["provider_session_id"], "")
        self.assertEqual(record["provider_session_none_reason"], sc.CROSS_MODEL)
        self.assertNotEqual(record["rotation_record_key"],
                            record["previous_provider_session_id"])
        self.assertIn("prov-1", self.seam.ledger.archived_sessions())
        # The FULL handoff is delivered as the successor's first prompt.
        self.assertIn(sc.REORIENTATION_HEADER, result.reorientation_prompt)
        self.assertIn("READY", result.reorientation_prompt)
        self.assertIn(good_facts().exact_next_action, result.reorientation_prompt)
        self.assertNotIn("/clear", result.reorientation_prompt)

    def test_a_resume_names_the_session_archives_nothing_and_sends_no_prompt(self) -> None:
        result = self.seam.execute(
            facts=good_facts(reason_code="session_relaunch"), safety_state=self._safe(),
            continuity=resume_decision(), previous_provider_session_id="prov-1",
            successor_model=PIN)
        record = self.journal.get_state("last_rotation")
        self.assertEqual(record["continuity_mode"], "resume")
        self.assertEqual(record["provider_session_id"], "prov-1")
        self.assertEqual(self.seam.ledger.archived_sessions(), (),
                         "archiving the session being resumed would make the resume "
                         "illegal (S15)")
        self.assertEqual(result.reorientation_prompt, "",
                         "a resumed successor already has the context")

    def test_a_crash_between_the_two_durable_writes_fails_closed(self) -> None:
        # M0-T080 correction U12 (G4 F7 / G5 N2) - the one fail-OPEN window.
        # `arm_ready_gate` and `complete_rotation` are two separate durable
        # writes. In the OLD order (complete, then arm) a crash between them left
        # a COMPLETED rotation with NO armed gate, so the restarted run bypassed
        # both the READY gate and the identity check. Reversed, the same crash
        # leaves an ARMED GATE and no completed rotation: the rotation is still
        # pending and the next checkpoint must satisfy the gate.
        journal = MemoryJournal()
        seam = ts.SeamTurnover(journal=journal, run_id="run-1")
        rot.observe_mid_unit(journal, reason_code="context_threshold")

        crashed: list[str] = []
        original = seam.ledger.complete_rotation

        def crash_after_arming(**kwargs):
            crashed.append("complete_rotation was reached")
            raise RuntimeError("power loss between the two durable writes")

        seam.ledger.complete_rotation = crash_after_arming  # type: ignore[assignment]
        with self.assertRaises(RuntimeError):
            seam.execute(facts=good_facts(), safety_state=self._safe(),
                         continuity=reorientation_decision(),
                         previous_provider_session_id="prov-1",
                         successor_model=APPROVED_B)
        self.assertEqual(crashed, ["complete_rotation was reached"],
                         "the gate must be armed BEFORE the rotation is completed")

        # What the restarted run finds: an ARMED gate, no completed rotation, and
        # the rotation still pending. Nothing is forwarded until READY.
        seam.ledger.complete_rotation = original  # type: ignore[assignment]
        self.assertIsNotNone(seam.armed_gate())
        self.assertIsNone(journal.get_state("last_rotation"))
        self.assertTrue(rot.rotation_pending(journal))
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            seam.require_ready(make_checkpoint(status="UNIT_COMPLETE",
                                               claude_session_id="prov-1"))
        self.assertEqual(raised.exception.code, "rotation_ready_required")

    def test_an_archived_session_can_never_be_resumed_by_a_later_rotation(self) -> None:
        self.seam.ledger.archive_session("prov-1", reason="an earlier rotation")
        with self.assertRaises(rot.RotationError) as raised:
            self.seam.execute(facts=good_facts(reason_code="session_relaunch"),
                              safety_state=self._safe(), continuity=resume_decision(),
                              previous_provider_session_id="prov-1",
                              successor_model=PIN)
        self.assertEqual(raised.exception.code, "archived_session_resume")

    def test_the_ready_gate_blocks_until_a_ready_checkpoint_arrives(self) -> None:
        self.seam.execute(facts=good_facts(), safety_state=self._safe(),
                          continuity=reorientation_decision(),
                          previous_provider_session_id="prov-1",
                          successor_model=APPROVED_B)
        working = make_checkpoint(status="UNIT_COMPLETE", claude_session_id="prov-2")
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.require_ready(working)
        self.assertEqual(raised.exception.code, "rotation_ready_required")
        # The gate stays armed until it is actually satisfied.
        self.assertIsNotNone(self.seam.armed_gate())
        ready = make_checkpoint(status="READY", claude_session_id="prov-2")
        self.seam.require_ready(ready)
        self.assertIsNone(self.seam.armed_gate())

    def test_a_ready_from_the_archived_session_never_satisfies_the_gate(self) -> None:
        self.seam.execute(facts=good_facts(), safety_state=self._safe(),
                          continuity=reorientation_decision(),
                          previous_provider_session_id="prov-1",
                          successor_model=APPROVED_B)
        impostor = make_checkpoint(status="READY", claude_session_id="prov-1")
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.require_ready(impostor)
        self.assertEqual(raised.exception.code, "ready_from_archived_session")

    def test_a_resume_that_landed_in_a_different_session_is_not_a_resume(self) -> None:
        self.seam.execute(facts=good_facts(reason_code="session_relaunch"),
                          safety_state=self._safe(), continuity=resume_decision(),
                          previous_provider_session_id="prov-1", successor_model=PIN)
        elsewhere = make_checkpoint(status="READY", claude_session_id="prov-9")
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.require_ready(elsewhere)
        self.assertEqual(raised.exception.code, "resumed_wrong_session")

    def test_a_ready_naming_no_session_can_never_clear_the_gate(self) -> None:
        # M0-T080 correction U1 (G5 must-fix). `ClaudeCheckpoint.validate` checks
        # only `status` and `usage`, so this checkpoint is WELL-FORMED and still
        # names no session. The gate used to guard its archived-session and
        # resumed-session comparisons with `if session and …`, so a blank
        # `claude_session_id` skipped both and CLEARED the gate - which is exactly
        # how the just-archived session, or a session doing the wrong work, passed
        # by saying nothing.
        self.seam.execute(facts=good_facts(), safety_state=self._safe(),
                          continuity=reorientation_decision(),
                          previous_provider_session_id="prov-1",
                          successor_model=APPROVED_B)
        anonymous = make_checkpoint(status="READY", claude_session_id="")
        anonymous.validate()  # a well-formed checkpoint, not a malformed one
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.require_ready(anonymous)
        self.assertEqual(raised.exception.code, "ready_without_session_id")
        self.assertIsNotNone(self.seam.armed_gate(), "the gate must stay armed")

    def test_a_blank_session_cannot_smuggle_the_archived_one_past_the_gate(self) -> None:
        # The same defect from the attacker's side: the archived session reports
        # READY with its id omitted. Before U1 that satisfied the gate.
        self.seam.execute(facts=good_facts(), safety_state=self._safe(),
                          continuity=reorientation_decision(),
                          previous_provider_session_id="prov-1",
                          successor_model=APPROVED_B)
        self.assertIn("prov-1", self.seam.ledger.archived_sessions())
        with self.assertRaises(ts.SeamTurnoverError):
            self.seam.require_ready(make_checkpoint(status="READY",
                                                    claude_session_id=""))

    def test_a_blank_resume_session_cannot_satisfy_the_resume_gate(self) -> None:
        self.seam.execute(facts=good_facts(reason_code="session_relaunch"),
                          safety_state=self._safe(), continuity=resume_decision(),
                          previous_provider_session_id="prov-1", successor_model=PIN)
        with self.assertRaises(ts.SeamTurnoverError) as raised:
            self.seam.require_ready(make_checkpoint(status="READY",
                                                    claude_session_id=""))
        self.assertEqual(raised.exception.code, "ready_without_session_id")

    def test_no_armed_gate_means_an_ordinary_cycle_is_untouched(self) -> None:
        self.seam.require_ready(make_checkpoint(status="UNIT_COMPLETE"))

    def test_post_launch_verification_names_every_mismatch(self) -> None:
        result = self.seam.execute(
            facts=good_facts(), safety_state=self._safe(),
            continuity=reorientation_decision(),
            previous_provider_session_id="prov-1", successor_model=APPROVED_B)
        ok, reason, _ = self.seam.verify_post_launch(
            checkpoint=make_checkpoint(task_id="M0-T080", branch="task/M0-T080",
                                       worktree="/repo/wt", starting_sha="a" * 40),
            run_result=run_result(observed_models=(APPROVED_B,)),
            expectation=result.expectation)
        self.assertTrue(ok, reason)
        bad, reason, detail = self.seam.verify_post_launch(
            checkpoint=make_checkpoint(task_id="M0-T999", branch="task/other",
                                       worktree="/elsewhere", starting_sha="f" * 40),
            run_result=run_result(observed_models=(UNAPPROVED,)),
            expectation=result.expectation)
        self.assertFalse(bad)
        for field in ("task_id", "branch", "worktree", "starting_sha", "model"):
            self.assertTrue(any(field in m for m in detail["mismatches"]),
                            f"{field} mismatch not reported: {detail['mismatches']}")

    def test_an_omitted_identity_field_is_a_mismatch_not_a_pass(self) -> None:
        # M0-T080 correction U1 (G5 must-fix). Every axis used to be guarded
        # `if expected and observed …`, so a successor could satisfy ALL FOUR
        # identity checks by reporting BLANKS - and `ClaudeCheckpoint.validate`
        # permits that, since it checks only status and usage. The suite was
        # structurally blind to this: it only ever tested populated-but-wrong.
        result = self.seam.execute(
            facts=good_facts(), safety_state=self._safe(),
            continuity=reorientation_decision(),
            previous_provider_session_id="prov-1", successor_model=APPROVED_B)
        blank = make_checkpoint(task_id="", branch="", worktree="", starting_sha="")
        blank.validate()  # well-formed, and says nothing about who it is
        ok, reason, detail = self.seam.verify_post_launch(
            checkpoint=blank, run_result=run_result(observed_models=(APPROVED_B,)),
            expectation=result.expectation)
        self.assertFalse(ok, "a successor that names nothing must not pass")
        for field in ("task_id", "branch", "worktree", "starting_sha"):
            self.assertTrue(
                any(field in m and "NOTHING" in m for m in detail["mismatches"]),
                f"{field} omission not reported as a mismatch: {detail['mismatches']}")

    def test_each_identity_axis_fails_closed_on_its_own_omission(self) -> None:
        # One blank field is enough; they need not accumulate.
        result = self.seam.execute(
            facts=good_facts(), safety_state=self._safe(),
            continuity=reorientation_decision(),
            previous_provider_session_id="prov-1", successor_model=APPROVED_B)
        good = dict(task_id="M0-T080", branch="task/M0-T080", worktree="/repo/wt",
                    starting_sha="a" * 40)
        for blanked in good:
            with self.subTest(field=blanked):
                fields = {**good, blanked: ""}
                ok, _reason, detail = self.seam.verify_post_launch(
                    checkpoint=make_checkpoint(**fields),
                    run_result=run_result(observed_models=(APPROVED_B,)),
                    expectation=result.expectation)
                self.assertFalse(ok)
                self.assertEqual(len(detail["mismatches"]), 1, detail["mismatches"])
                self.assertIn("NOTHING", detail["mismatches"][0])

    def test_an_axis_the_supervisor_never_commanded_is_not_invented(self) -> None:
        # Fail-closed is not fail-noisy: where the supervisor wrote down NO
        # expectation there is nothing to mismatch against, so a blank is fine.
        expectation = ts.SuccessorExpectation(
            task_id="M0-T080", branch="", worktree="", head_sha="",
            model_id="", continuity_mode=sc.REORIENTATION)
        ok, _reason, detail = self.seam.verify_post_launch(
            checkpoint=make_checkpoint(task_id="M0-T080", branch="", worktree="",
                                       starting_sha=""),
            run_result=run_result(), expectation=expectation)
        self.assertTrue(ok, detail)


# --------------------------------------------------------------------------
# AS-5: owner-approved, live-probed model routing (D-023-R013)
# --------------------------------------------------------------------------


class ApprovedModelRoutingTests(unittest.TestCase):
    def _router(self, *, entries=(APPROVED_A, APPROVED_B), probe=probe_all_ok,
                identity="config-identity-1", cli="cli-v1") -> am.ModelRouter:
        self.journal = getattr(self, "journal", None) or MemoryJournal()
        return am.ModelRouter(
            approved=am.ApprovedModels(entries=entries, source="fake-config.toml"),
            ledger=am.ProbeLedger(self.journal, config_identity=identity,
                                  cli_version=cli),
            probe=probe)

    def test_an_empty_approved_list_stops_safely_with_a_typed_refusal(self) -> None:
        router = self._router(entries=())
        for act in (lambda: router.select(APPROVED_A),
                    lambda: router.next_after(PIN)):
            with self.assertRaises(am.ModelRoutingError) as raised:
                act()
            self.assertEqual(raised.exception.code, am.APPROVED_MODELS_EMPTY)
            self.assertEqual(raised.exception.refusal.outcome, "halted")
            self.assertEqual(raised.exception.refusal.exit_code, 10)
            self.assertIn("populate", raised.exception.message)

    def test_an_unlisted_id_is_never_selectable_however_available(self) -> None:
        router = self._router(probe=probe_all_ok)
        with self.assertRaises(am.ModelRoutingError) as raised:
            router.select(UNAPPROVED)
        self.assertEqual(raised.exception.code, am.MODEL_NOT_APPROVED)
        self.assertEqual(raised.exception.refusal.outcome, "unsafe")

    def test_membership_is_exact_with_no_aliasing_or_trimming(self) -> None:
        approved = am.ApprovedModels(entries=(APPROVED_A,))
        for near_miss in (APPROVED_A.upper(), f" {APPROVED_A}", f"{APPROVED_A} ",
                          APPROVED_A.replace("-", "")):
            with self.subTest(near_miss=near_miss):
                self.assertNotIn(near_miss, approved)
        self.assertIn(APPROVED_A, approved)

    def test_a_listed_model_with_no_probe_seam_is_not_selectable(self) -> None:
        router = self._router(probe=None)
        with self.assertRaises(am.ModelRoutingError) as raised:
            router.select(APPROVED_A)
        self.assertEqual(raised.exception.code, am.PROBE_SEAM_MISSING)

    def test_a_failed_probe_is_recorded_and_the_model_is_not_selectable(self) -> None:
        router = self._router(probe=probe_none_ok)
        with self.assertRaises(am.ModelRoutingError) as raised:
            router.select(APPROVED_A)
        self.assertEqual(raised.exception.code, am.MODEL_PROBE_FAILED)
        recorded = router.ledger.recorded(APPROVED_A)
        self.assertFalse(recorded.ok)
        self.assertEqual(recorded.reason_code, "quota_exhausted")

    def test_a_probe_that_raises_proves_nothing_and_fails_closed(self) -> None:
        def exploding(_model: str):
            raise RuntimeError("the probe blew up")

        router = self._router(probe=exploding)
        with self.assertRaises(am.ModelRoutingError) as raised:
            router.select(APPROVED_A)
        self.assertEqual(raised.exception.code, am.MODEL_PROBE_FAILED)
        self.assertEqual(router.ledger.recorded(APPROVED_A).reason_code, "probe_error")

    def test_an_unparseable_probe_result_is_never_read_as_availability(self) -> None:
        # M0-T080 correction U5 (G5 I1). This used to coerce with
        # `ok=bool(outcome)`, so ANY truthy value the router could not parse was
        # recorded as a SUCCESSFUL launch probe and made the model selectable.
        # Latent while no probe seam is wired; live the moment the owner wires one.
        for junk in (True, "available", {"ok": True}, 1, ["yes"]):
            with self.subTest(returned=type(junk).__name__):
                self.journal = MemoryJournal()
                router = self._router(probe=lambda _m, value=junk: value)
                with self.assertRaises(am.ModelRoutingError) as raised:
                    router.select(APPROVED_A)
                self.assertEqual(raised.exception.code, am.MODEL_PROBE_FAILED)
                record = router.ledger.recorded(APPROVED_A)
                self.assertFalse(record.ok, "an unparseable result is not availability")
                self.assertEqual(record.reason_code, "probe_shape")

    def test_an_exhaustion_message_never_claims_a_probe_that_did_not_happen(self) -> None:
        # M0-T080 correction U7 (G4 F1): measured-claims discipline on a refusal
        # message. The sentence used to assert "Every candidate was tried by an
        # actual launch probe" even when NOTHING was probed.
        unprobed = am.ModelRouter(
            approved=am.ApprovedModels(entries=(APPROVED_A, APPROVED_B)),
            ledger=am.ProbeLedger(MemoryJournal(), config_identity="c", cli_version="v"),
            probe=None)
        with self.assertRaises(am.ModelRoutingError) as raised:
            unprobed.next_after(APPROVED_A)
        self.assertIn("NOTHING was probed", raised.exception.message)
        self.assertNotIn("were tried by an actual launch probe and none came up",
                         raised.exception.message)
        # And when they really were probed, it says so.
        self.journal = MemoryJournal()
        probed = self._router(probe=probe_none_ok)
        with self.assertRaises(am.ModelRoutingError) as raised:
            probed.next_after(APPROVED_A)
        self.assertIn("were tried by an actual launch probe", raised.exception.message)
        self.assertNotIn("NOTHING was probed", raised.exception.message)

    def test_a_successful_probe_is_recorded_with_identity_and_time(self) -> None:
        router = self._router()
        selected = router.select(APPROVED_A)
        self.assertEqual(selected.model_id, APPROVED_A)
        record = selected.probe
        self.assertTrue(record.ok)
        self.assertEqual(record.cli_version, "cli-v1")
        self.assertEqual(record.config_identity, "config-identity-1")
        self.assertTrue(record.probed_at_utc)

    def test_a_probe_from_another_config_or_cli_makes_the_model_unselectable(self) -> None:
        journal = MemoryJournal()
        am.ProbeLedger(journal, config_identity="config-identity-1",
                       cli_version="cli-v1").record(
            APPROVED_A, am.ProbeOutcome(ok=True, cli_version="cli-v1"))
        for identity, cli, label in (("config-identity-2", "cli-v1", "config changed"),
                                     ("config-identity-1", "cli-v2", "CLI changed")):
            with self.subTest(label=label):
                ledger = am.ProbeLedger(journal, config_identity=identity,
                                        cli_version=cli)
                self.assertIsNone(ledger.successful(APPROVED_A))
                router = am.ModelRouter(
                    approved=am.ApprovedModels(entries=(APPROVED_A,)),
                    ledger=ledger, probe=None)
                with self.assertRaises(am.ModelRoutingError) as raised:
                    router.select(APPROVED_A)
                self.assertEqual(raised.exception.code, am.PROBE_SEAM_MISSING)

    def test_start_and_the_watchdog_share_one_probe_identity(self) -> None:
        """M0-T080 correction U8 (G4 F2) - a latent R595 activation-blocker.

        `start` keyed its ProbeLedger on the real
        `runner.executable_identity()["digest"]`; the watchdog keyed on
        `cli_version=""` because it had no `--claude-executable` and never passed
        one. Once the owner wires a real probe, a probe recorded by `start` could
        NEVER satisfy the watchdog's identity match, so the orchestrator turnover
        would answer `no_approved_successor` forever. Fail-closed today, which is
        why it was invisible - and why it had to be fixed before activation.
        """
        from tools.agent_supervisor import cli

        journal = MemoryJournal()
        config = FakeApprovedConfig()
        start_identity = cli._claude_cli_identity(sys.executable)
        self.assertTrue(start_identity, "a named executable must yield an identity")

        # A probe recorded the way `start` records one.
        am.ProbeLedger(journal, config_identity=config.digest(),
                       cli_version=start_identity).record(
            APPROVED_B, am.ProbeOutcome(ok=True, cli_version=start_identity))

        # The watchdog, given the SAME executable, finds it and can select.
        from tools.agent_supervisor import turnover_wiring as tw
        shared = tw.approved_model_router(journal, config=config, probe=None,
                                          cli_version=start_identity)
        self.assertEqual(shared.next_after(APPROVED_A).model_id, APPROVED_B)

        # The pre-correction behaviour - an empty cli_version - cannot use it.
        blind = tw.approved_model_router(journal, config=config, probe=None,
                                         cli_version="")
        with self.assertRaises(am.ModelRoutingError) as raised:
            blind.next_after(APPROVED_A)
        self.assertEqual(raised.exception.code, am.APPROVED_CHAIN_EXHAUSTED)

        # And the flag that carries the identity really exists on the subcommand.
        parser = cli.build_parser()
        args = parser.parse_args(
            ["orchestrator-watchdog", "--exhaustion-signal", "x",
             "--claude-executable", sys.executable])
        self.assertEqual(args.claude_executable, sys.executable)

    def test_an_unreadable_probe_record_reads_as_no_probe(self) -> None:
        journal = MemoryJournal()
        journal.set_state(am.PROBE_LEDGER_KEY, {APPROVED_A: "not a record"})
        ledger = am.ProbeLedger(journal, config_identity="config-identity-1",
                                cli_version="cli-v1")
        self.assertIsNone(ledger.successful(APPROVED_A))

    def test_the_walk_takes_the_next_approved_entry_that_actually_comes_up(self) -> None:
        router = self._router(probe=probe_only(APPROVED_B))
        selected = router.next_after(APPROVED_A)
        self.assertEqual(selected.model_id, APPROVED_B)
        self.assertEqual([a["model"] for a in selected.attempts], [APPROVED_B])

    def test_exhausting_the_approved_chain_is_a_typed_safe_stop(self) -> None:
        router = self._router(probe=probe_none_ok)
        with self.assertRaises(am.ModelRoutingError) as raised:
            router.next_after(APPROVED_A)
        self.assertEqual(raised.exception.code, am.APPROVED_CHAIN_EXHAUSTED)
        self.assertEqual(raised.exception.refusal.outcome, "halted")
        self.assertEqual([a["model"] for a in raised.exception.detail["attempts"]],
                         [APPROVED_B])
        self.assertIn("safe stop", raised.exception.message)

    def test_the_walk_never_leaves_the_approved_list(self) -> None:
        approved = am.ApprovedModels(entries=(APPROVED_A, APPROVED_B))
        self.assertEqual(approved.candidates_after(APPROVED_A), (APPROVED_B,))
        self.assertEqual(approved.candidates_after(APPROVED_B), ())
        # An unlisted current model starts at the head, still inside the list.
        self.assertEqual(approved.candidates_after(UNAPPROVED),
                         (APPROVED_A, APPROVED_B))


class ApprovedSuccessorControllerTests(unittest.TestCase):
    """The turnover successor comes from the approved chain, not a constant."""

    class _Lock:
        def __init__(self) -> None:
            self.acquired = 0

        def acquire(self) -> bool:
            self.acquired += 1
            return True

        def release(self) -> None:
            pass

    class _Audit:
        def __init__(self) -> None:
            self.records: list[dict] = []
            self.actioned: set[str] = set()

        def already_actioned(self, event_id: str) -> bool:
            return event_id in self.actioned

        def append(self, record) -> str:
            self.records.append(dict(record))
            return f"audit-{len(self.records)}"

        def mark_actioned(self, event_id: str) -> None:
            self.actioned.add(event_id)

    class _Identity:
        def now_iso(self) -> str:
            return "2026-08-21T00:00:00+00:00"

        def new_audit_id(self) -> str:
            return "audit-id"

    class _Launcher:
        def __init__(self) -> None:
            self.requests: list[Any] = []

        def launch(self, request) -> LaunchResult:
            self.requests.append(request)
            return LaunchResult(available=True, successor_id="succ-1",
                                model_id=request.model_id)

    def _controller(self, resolver, launcher=None):
        launcher = launcher or self._Launcher()
        audit = self._Audit()
        controller = TurnoverController(
            launcher=launcher, lock=self._Lock(), audit=audit,
            identity=self._Identity(), survivor_detected=lambda _c: False,
            successor=resolver)
        return controller, launcher, audit

    def _context(self, **overrides) -> TurnoverContext:
        data: dict[str, Any] = dict(
            task_id="M0-T080", event_id="evt-1", failed_fable_execution_id="exec-1",
            safe_checkpoint_id="cp-7", handoff_reference="handoff://ref",
            layer=TurnoverLayer.WORKER, current_model=APPROVED_A)
        data.update(overrides)
        return TurnoverContext(**data)

    def _verdict(self):
        class _V:
            should_turn_over = True
            reason = "confirmed exhaustion"
        return _V()

    def _resolver(self, entries=(APPROVED_A, APPROVED_B), probe=probe_all_ok):
        journal = MemoryJournal()
        router = am.ModelRouter(
            approved=am.ApprovedModels(entries=entries, source="fake-config.toml"),
            ledger=am.ProbeLedger(journal, config_identity="config-identity-1",
                                  cli_version="cli-v1"),
            probe=probe)

        def _resolve(context: TurnoverContext) -> ApprovedSuccessor:
            selected = router.next_after(context.current_model)
            return ApprovedSuccessor(model_id=selected.model_id,
                                     effort=ALLOWED_SUCCESSOR_EFFORT,
                                     probed_at_utc=selected.probe.probed_at_utc,
                                     config_identity=selected.probe.config_identity,
                                     cli_version=selected.probe.cli_version)
        return _resolve

    def test_the_successor_is_the_next_approved_entry(self) -> None:
        controller, launcher, audit = self._controller(self._resolver())
        result = controller.execute(self._verdict(), self._context())
        self.assertIs(result.status, TurnoverStatus.LAUNCHED_SUCCESSOR)
        self.assertEqual(result.model_id, APPROVED_B)
        self.assertEqual(launcher.requests[0].model_id, APPROVED_B)
        launched = [r for r in audit.records if r.get("successor_id") == "succ-1"]
        # The audit row shows WHY the id was permitted, not just which id it was.
        self.assertEqual(launched[0]["successor_model_id"], APPROVED_B)
        self.assertEqual(launched[0]["successor_config_identity"], "config-identity-1")
        self.assertTrue(launched[0]["successor_probed_at_utc"])

    def test_an_empty_approved_list_is_a_safe_stop_that_launches_nothing(self) -> None:
        controller, launcher, audit = self._controller(self._resolver(entries=()))
        result = controller.execute(self._verdict(), self._context())
        self.assertIs(result.status, TurnoverStatus.NO_APPROVED_SUCCESSOR)
        self.assertEqual(launcher.requests, [])
        self.assertFalse(audit.actioned, "a safe stop never consumes the dedup key")

    def test_a_no_approved_successor_safe_stop_leaves_a_durable_audit_row(self) -> None:
        # M0-T080 correction U6 (G5 I2). This branch used to append NOTHING. The
        # watchdog runs standalone under the OS scheduler, where the returned JSON
        # is nobody's audit trail, and every OTHER watchdog refusal is hash-chain
        # audited - so the one refusal meaning "the owner has approved nothing"
        # was the one that vanished.
        controller, launcher, audit = self._controller(self._resolver(entries=()))
        result = controller.execute(self._verdict(), self._context())
        self.assertIs(result.status, TurnoverStatus.NO_APPROVED_SUCCESSOR)
        self.assertEqual(launcher.requests, [])
        rows = [r for r in audit.records
                if r.get("kind") == "turnover_no_approved_successor"]
        self.assertEqual(len(rows), 1, audit.records)
        self.assertEqual(rows[0]["event_id"], "evt-1")
        self.assertEqual(rows[0]["current_model"], APPROVED_A)
        self.assertIn(am.APPROVED_MODELS_EMPTY, rows[0]["detail"])
        self.assertTrue(result.audit_record_id, "the row's id is surfaced on the outcome")
        self.assertFalse(audit.actioned, "a safe stop never consumes the dedup key")

    def test_an_unwritable_audit_never_turns_a_safe_stop_into_a_crash(self) -> None:
        class _DamagedAudit(self._Audit):
            def append(self, record):
                raise RuntimeError("the hash chain is forked")

        launcher = self._Launcher()
        controller = TurnoverController(
            launcher=launcher, lock=self._Lock(), audit=_DamagedAudit(),
            identity=self._Identity(), survivor_detected=lambda _c: False,
            successor=self._resolver(entries=()))
        result = controller.execute(self._verdict(), self._context())
        self.assertIs(result.status, TurnoverStatus.NO_APPROVED_SUCCESSOR)
        self.assertIn("unaudited", result.audit_record_id)
        self.assertEqual(launcher.requests, [])

    def test_an_exhausted_approved_chain_is_a_safe_stop(self) -> None:
        controller, launcher, _ = self._controller(self._resolver(probe=probe_none_ok))
        result = controller.execute(self._verdict(), self._context())
        self.assertIs(result.status, TurnoverStatus.NO_APPROVED_SUCCESSOR)
        self.assertIn("owner-approved", result.reason)
        self.assertEqual(launcher.requests, [])

    def test_a_caller_requesting_a_different_model_is_refused_before_the_lock(self) -> None:
        controller, launcher, _ = self._controller(self._resolver())
        result = controller.execute(self._verdict(),
                                    self._context(requested_model=UNAPPROVED))
        self.assertIs(result.status, TurnoverStatus.INVALID_MODEL_REFUSED)
        self.assertEqual(launcher.requests, [])

    def test_a_caller_requesting_a_different_effort_is_refused(self) -> None:
        controller, launcher, _ = self._controller(self._resolver())
        result = controller.execute(self._verdict(),
                                    self._context(requested_effort="low"))
        self.assertIs(result.status, TurnoverStatus.INVALID_MODEL_REFUSED)
        self.assertEqual(launcher.requests, [])

    def test_the_pinned_successor_constant_is_gone(self) -> None:
        from tools.agent_supervisor import turnover_controller as tc
        self.assertFalse(hasattr(tc, "ALLOWED_SUCCESSOR_MODEL_ID"))
        source = (REPO / "tools" / "agent_supervisor" / "turnover_controller.py").read_text(
            encoding="utf-8")
        self.assertNotIn("ALLOWED_SUCCESSOR_MODEL_ID", source)


# --------------------------------------------------------------------------
# AS-6: a model arriving from a NON-CONFIG path
# --------------------------------------------------------------------------


class IpcApprovedModelTests(unittest.TestCase):
    def _request(self, model: str, provider: str = "claude") -> ipc.ModelChangeRequest:
        return ipc.ModelChangeRequest(
            provider=provider, old_model=APPROVED_A, new_model=model,
            scope=ipc.SCOPE_PERSISTENT, run_id="run-1", task_id="M0-T080",
            before_selection_digest="x", after_selection_digest="y")

    def test_an_allowlisted_but_unapproved_model_is_refused(self) -> None:
        # UNAPPROVED is on `claude.allowed_models` and STILL refused: the
        # approved list is an independent gate, and a model arriving from the IPC
        # is held to it exactly like every other selection act (D-023-R013).
        config = FakeApprovedConfig()
        self.assertIn(UNAPPROVED, config.allowlist("claude"))
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_allowlisted(self._request(UNAPPROVED), config)
        self.assertEqual(raised.exception.code, "model_not_approved")

    def test_an_approved_and_allowlisted_model_passes_both_gates(self) -> None:
        ipc.assert_allowlisted(self._request(APPROVED_A), FakeApprovedConfig())

    def test_an_empty_approved_list_refuses_every_claude_change(self) -> None:
        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_allowlisted(self._request(APPROVED_A),
                                   FakeApprovedConfig(entries=()))
        self.assertEqual(raised.exception.code, "approved_models_empty")

    def test_a_config_without_an_approved_surface_refuses_rather_than_skips(self) -> None:
        class _NoApproved:
            def allowlist(self, _provider: str) -> tuple[str, ...]:
                return (APPROVED_A,)

        with self.assertRaises(ipc.IpcError) as raised:
            ipc.assert_allowlisted(self._request(APPROVED_A), _NoApproved())
        self.assertEqual(raised.exception.code, "approved_models_unavailable")

    def test_the_codex_provider_keeps_its_own_allowlist_unchanged(self) -> None:
        # The approved list is the CLAUDE session/model chain; a Codex change is
        # still governed by `codex.allowed_models` and nothing else.
        ipc.assert_allowlisted(self._request("codex-x", provider="codex"),
                               FakeApprovedConfig())

    def test_the_process_ancestry_gate_still_runs_first_and_unweakened(self) -> None:
        # The approved-models check must not be reachable at all for a
        # worker-originated caller: gate 1 denies before gate 3 is consulted.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = pathlib.Path(tmp.name).resolve()
        runtime = root / "runtime"
        worktree = root / "worktree"
        runtime.mkdir()
        worktree.mkdir()
        selection = root / "model_selection.toml"
        selection.write_text('[codex]\nreview_model = ""\nfallback_models = []\n'
                             '[claude]\nmodel = ""\nfallback_models = []\n',
                             encoding="utf-8")
        journal = DurableJournal(runtime / "journal.sqlite3").open()
        self.addCleanup(journal.close)
        endpoint = ipc.ModelChangeEndpoint(
            journal=journal, config=FakeApprovedConfig(entries=()),
            selection_path=selection, runtime_dir=runtime, checkout_key="k" * 64,
            controller_pid=os.getpid(), worker_writable_roots=(str(worktree),))
        ipc.record_worker_pid(journal, os.getpid(), role="worker")
        with self.assertRaises(ipc.IpcError) as raised:
            endpoint.request_change(
                caller=ipc.Caller(pid=os.getpid(), account="owner",
                                  channel=endpoint.plan.channel),
                provider="claude", new_model=APPROVED_A, old_model="",
                after_selection_digest="y", run_id="r", task_id="t",
                prompt=lambda _m: "y", at_checkpoint_boundary=True)
        self.assertEqual(raised.exception.code, "worker_origin_denied",
                         "the ancestry gate must deny before anything else is checked")


# --------------------------------------------------------------------------
# AS-7: the assembled loop, end to end (fake runner, no provider)
# --------------------------------------------------------------------------


class LoopLiveSeamTests(LoopTestBase):
    """The three seams now take the full path, and its gates really stop the run."""

    def _downgrade(self, *results) -> FakeRunner:
        return FakeRunner(
            run_result(model_mismatch=True, mismatch_detail="reported another model"),
            *results, model=PIN)

    def test_the_successor_receives_the_full_handoff_as_its_first_prompt(self) -> None:
        self.at_preflight()
        runner = self._downgrade(self.successor_result(checkpoint_id="cp-successor"))
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN, approval_gate=lambda _d, _p: True)
        loop.run("first unit")
        prompt = runner.prompts[1]
        self.assertIn(sc.REORIENTATION_HEADER, prompt)
        self.assertIn("REQUIRED FIRST RESPONSE", prompt)
        # The whole S11.3 handoff, not a digest or a pointer.
        self.assertIn("authoritative_shas", prompt)
        self.assertIn("forbidden_scope", prompt)
        self.assertIn("exact_next_action", prompt)
        # The forwarded unit prompt still reaches the successor after it.
        self.assertIn("FORWARDED UNIT PROMPT:", prompt)

    def test_a_successor_that_does_not_report_ready_forwards_nothing(self) -> None:
        self.at_preflight()
        # The post-rotation unit answers UNIT_COMPLETE instead of the S11.3 READY.
        runner = self._downgrade(run_result(
            checkpoint=make_checkpoint(checkpoint_id="cp-2",
                                       claude_session_id="sess-successor")))
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN, approval_gate=lambda _d, _p: True)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "rotation_ready_required")
        self.assertEqual(self.machine.current_state, sm.PAUSED_RECOVERY)
        # The rotation itself completed; what stopped is everything AFTER it.
        self.assertEqual(len(run.rotations), 1)
        self.assertEqual(len(run.forwarded_message_ids), 1,
                         "only the pre-rotation forward; nothing from the gated cycle")
        events = [r["event_type"] for r in self.audit.read_all()]
        self.assertIn("rotation_ready_gate_armed", events)
        self.assertIn("rotation_ready_gate_refused", events)

    def test_a_successor_on_the_wrong_model_stops_the_run_fail_closed(self) -> None:
        self.at_preflight()
        # READY, right task/branch/worktree/HEAD - but the stream reports a model
        # other than the one that was commanded.
        successor = self.successor_result(checkpoint_id="cp-successor",
                                          observed_models=("model-not-commanded",))
        runner = self._downgrade(successor)
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN, approval_gate=lambda _d, _p: True)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "successor_identity_mismatch")
        self.assertEqual(self.machine.current_state, sm.PAUSED_RECOVERY)
        events = [r for r in self.audit.read_all()
                  if r["event_type"] == "successor_identity_mismatch"]
        self.assertTrue(events)
        self.assertIn("model", events[0]["detail"]["reason"])

    def test_a_successor_in_the_wrong_worktree_stops_the_run(self) -> None:
        self.at_preflight()
        successor = run_result(
            session_id="sess-successor",
            checkpoint=make_checkpoint(
                status="READY", checkpoint_id="cp-successor",
                claude_session_id="sess-successor", starting_sha=HEAD_SHA,
                current_sha=HEAD_SHA, worktree="/somewhere/else"))
        loop = self.build(mode="supervised", runner=self._downgrade(successor),
                          max_cycles=2, pinned_model=PIN,
                          approval_gate=lambda _d, _p: True)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "successor_identity_mismatch")

    def test_an_unsafe_seam_refuses_the_turnover_and_pauses_for_the_owner(self) -> None:
        self.at_preflight()
        self.machine.transition(sm.START_CLAUDE, "preflight_pass")
        self.machine.transition(sm.CLAUDE_RUNNING, "claude_process_started")
        loop = self.build(mode="supervised", runner=self._downgrade(), max_cycles=2,
                          pinned_model=PIN, head_sha="")
        loop._last_checkpoint = None
        self.journal.set_state(rot.ROTATION_PENDING_KEY, True)
        seam = loop._rotate_at_seam(cycle=2)
        self.assertTrue(seam.paused)
        self.assertEqual(seam.stopped, "rotation_refused")
        self.assertEqual(seam.reason_code, "unsafe_seam")
        # Nothing durable about the rotation was written.
        self.assertIsNone(rot.RotationLedger(self.journal).stored_handoff())
        self.assertTrue(rot.rotation_pending(self.journal),
                        "the rotation is still pending; the run was not half-rotated")
        self.assertTrue(self.journal.open_asks(), "the owner must be notified")

    def test_the_provider_session_is_recorded_and_the_internal_key_is_not(self) -> None:
        self.at_preflight()
        runner = self._downgrade(self.successor_result(checkpoint_id="cp-successor"))
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN, approval_gate=lambda _d, _p: True)
        run = loop.run("first unit")
        record = run.rotations[0]
        self.assertTrue(record["rotation_record_key"].startswith("sup-rot-"))
        self.assertEqual(record["previous_provider_session_id"], "sess-1")
        # The successor's OWN provider id was captured from its stream afterwards.
        recorded = sc.recorded_provider_session(self.journal)
        self.assertEqual(recorded.session_id, "sess-successor")
        self.assertNotEqual(recorded.session_id, record["rotation_record_key"])

    def test_an_ambiguous_provider_session_is_dropped_not_recorded(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(session_id="sess-1",
                                       session_id_conflict="two ids seen"), model=PIN)
        loop = self.build(mode="supervised", runner=runner, max_cycles=1,
                          pinned_model=PIN, approval_gate=lambda _d, _p: True)
        loop.run("first unit")
        self.assertIsNone(sc.recorded_provider_session(self.journal))
        self.assertEqual(loop._provider_session_id, "")

    def test_a_resume_reaches_the_launch_or_the_seam_refuses(self) -> None:
        # The RESUME arm of the continuity decision, driven through the real
        # `_full_turnover`. `session_relaunch` is a same-model, non-context-shedding
        # reason: no trigger in the assembled loop produces one today (every live
        # rotation reason is context-shedding or cross-model, so production always
        # re-orients), but the path is real code and is proved here end to end.
        self.at_preflight()
        runner = FakeRunner(run_result(), model=PIN)
        runner.config = dataclasses.replace(runner.config,
                                            resume_capability_verified=True)
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN)
        loop._last_checkpoint = make_checkpoint(current_sha=HEAD_SHA)
        loop._last_checkpoint_id = "cp-1"
        sc.record_provider_session(self.journal, session_id="prov-1", model_id=PIN,
                                   run_id=self.run_id, cycle=1)
        loop._provider_session_id = "prov-1"
        result = loop._full_turnover(cycle=2, reason_code="session_relaunch",
                                     successor_model=PIN)
        self.assertTrue(result.continuity.resumed)
        self.assertEqual(result.continuity.provider_session_id, "prov-1")
        self.assertEqual(result.reorientation_prompt, "")
        # ACTUATION: the rebound runner really carries the id into its launch.
        self.assertEqual(loop.runner.config.resume_session_id, "prov-1")
        # And the outgoing session is NOT archived, so the resume stays legal.
        self.assertNotIn("prov-1", rot.RotationLedger(self.journal).archived_sessions())

    def test_a_crash_between_the_rotation_and_the_successor_still_checks_identity(self) -> None:
        # `_successor_expectation` is in-memory; the armed READY gate is DURABLE and
        # carries the same expectation. A restart in between must not skip the
        # identity check on exactly the cycle that needs it most.
        self.at_preflight()
        loop = self.build(mode="supervised", runner=FakeRunner(run_result(), model=PIN),
                          max_cycles=2, pinned_model=PIN)
        loop._last_checkpoint = make_checkpoint(current_sha=HEAD_SHA)
        loop._full_turnover(cycle=2, reason_code="context_threshold",
                            successor_model=PIN)
        self.assertIsNotNone(loop._seam.armed_gate())
        loop._successor_expectation = None  # the restart forgets it

        wrong = make_checkpoint(status="READY", checkpoint_id="cp-successor",
                                claude_session_id="sess-successor",
                                starting_sha=HEAD_SHA,
                                worktree=self.authority.worktree,
                                task_id="M0-T999")
        stop = loop._post_rotation_gates(
            wrong, run_result(observed_models=(PIN,)), cycle=2, touches=[])
        self.assertIsNotNone(stop)
        self.assertEqual(stop[0], "successor_identity_mismatch")
        self.assertIn("task_id", stop[1])

    def test_a_runner_that_cannot_resume_is_a_refusal_not_a_claimed_resume(self) -> None:
        self.at_preflight()

        class _NoResumeRunner(FakeRunner):
            with_resume = None

        runner = _NoResumeRunner(run_result(), model=PIN)
        runner.config = dataclasses.replace(runner.config,
                                            resume_capability_verified=True)
        loop = self.build(mode="supervised", runner=runner, max_cycles=2,
                          pinned_model=PIN)
        loop._last_checkpoint = make_checkpoint(current_sha=HEAD_SHA)
        # The run_id matters: since M0-T080 correction U14 the continuity read is
        # SCOPED to this run, so a session recorded under another run reads as
        # absent (and would reorient rather than resume).
        sc.record_provider_session(self.journal, session_id="prov-1", model_id=PIN,
                                   run_id=self.run_id)
        loop._provider_session_id = "prov-1"
        with self.assertRaises(lp.LoopError) as raised:
            loop._full_turnover(cycle=2, reason_code="session_relaunch",
                                successor_model=PIN)
        self.assertEqual(raised.exception.code, "resume_actuation_unavailable")


# --------------------------------------------------------------------------
# AS-8: the source-level guards, so a future edit cannot quietly undo this
# --------------------------------------------------------------------------


class NoCodeDefaultModelTests(unittest.TestCase):
    def test_no_supervisor_module_carries_a_default_model_chain(self) -> None:
        # Scanned at COLUMN 0, because that is where a module-level assignment
        # lives. Prose may still name the removed constants - `approved_models.py`
        # documents exactly what they were and why they went - and describing a
        # defect is not reintroducing it.
        package = REPO / "tools" / "agent_supervisor"
        import importlib
        for name in ("config", "loop", "turnover_controller", "turnover_adapters",
                     "approved_models"):
            with self.subTest(module=name):
                module = importlib.import_module(f"tools.agent_supervisor.{name}")
                self.assertFalse(hasattr(module, "DEFAULT_ORCHESTRATOR_MODEL_CHAIN"))
                self.assertFalse(hasattr(module, "ALLOWED_SUCCESSOR_MODEL_ID"))
                source = (package / f"{name}.py").read_text(encoding="utf-8")
                for banned in ("DEFAULT_ORCHESTRATOR_MODEL_CHAIN",
                               "ALLOWED_SUCCESSOR_MODEL_ID"):
                    self.assertFalse(
                        any(line.startswith(f"{banned} ") or line.startswith(f"{banned}:")
                            for line in source.splitlines()),
                        f"{banned} is assigned at module level in {name}.py")

    def test_the_cli_supplies_no_literal_current_model(self) -> None:
        source = (REPO / "tools" / "agent_supervisor" / "cli.py").read_text(
            encoding="utf-8")
        self.assertNotIn('or "claude-fable-5"', source)
        self.assertNotIn('current_model: str = "claude-fable-5"', source)

    def test_an_empty_chain_is_constructible_so_no_default_is_forced(self) -> None:
        self.assertEqual(cfg.ModelChain().entries, ())
        self.assertEqual(am.ApprovedModels().entries, ())
        self.assertFalse(am.ApprovedModels())

    def test_the_stale_limited_auto_note_was_corrected(self) -> None:
        # M0-T079 §8.7 flagged this as stale; the mode IS implemented and OFF.
        from tools.agent_supervisor import remote_approvals
        journal = MemoryJournal()
        record = remote_approvals.disable_limited_auto(journal, reason="test")
        self.assertIn("implemented", record["note"])
        self.assertNotIn("not implemented", record["note"])
        self.assertFalse(record["limited_auto_enabled"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
