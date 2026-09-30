#!/usr/bin/env python3
"""Launch-seam enforcement tests (resume-path defect class; D-024 Amendment 19).

Covers M0-T123 rows R331-R344 / acceptance scenarios AS-1..AS-8. The reproduced
cycle-2 live defect (`project-control/reports/M0-T107-cycle2-live-journey.md`)
had BOTH failures at once: a durable `rotation_pending=context_threshold` set at
604,772 tokens was left unconsumed across the next START, which dispatched a unit
that ran to 640,224 tokens and died `returncode 1`; and every record of that
worker's transcript was stamped with the PRIMARY control checkout `...\\ctl24`
instead of the isolated worktree `wt-m0t107`.

The tests are grouped:

* `LaunchSeamUnit` / `SessionTelemetry` - the pure guards and the persisted
  ceiling telemetry (AS-2, AS-3).
* `RunnerChokepoint` - the ironclad pre-`Popen` guard in `ClaudeRunner.run_unit`
  (AS-1 at the runner, AS-3, AS-6 provider-failure-as-typed-refusal).
* `PreDispatchCeilingSeam` - the loop-level pre-first-dispatch shed that closes
  the reproduced gap (AS-1, AS-4), with a RED reproduction of the pre-fix path.
* `CliWorktreeGate` - the production `_run_loop` cwd-binding gate (AS-3, AS-6).
* `ReachabilitySweep` - the deterministic, removal-sensitive call-site sweep
  proving every worker-launch/resume path routes through the seam (AS-5,
  R339/R340).
* `FixtureRegression` - the committed regression fixture derived read-only from
  the preserved cycle-2 evidence reproduces the defect shape (AS-7, AS-8).

No live provider is ever launched and the preserved runtime dir and transcripts
are never written: every test uses a fake executable, a temp journal, or the
committed fixture copy.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import os
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
from tools.agent_supervisor import launch_seam as ls  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import rotation as rot  # noqa: E402
from tools.agent_supervisor import session_continuity as sc  # noqa: E402
from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DurableJournal,
    checkout_key,
    runtime_dir_for,
)
from tools.agent_supervisor.locking import LockError, SingleInstanceLock  # noqa: E402
from tools.agent_supervisor.models import ClaudeCheckpoint  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

FIXTURE = (REPO / "tools" / "agent_supervisor" / "fixtures"
           / "resume_path_defect_2026-08-30_m0t123.json")
CEILING = 400_000

WORKTREE = r"C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107"
PRIMARY = r"C:\Users\MLFLL\Downloads\nyc-zoning\ctl24"


# ==========================================================================
# AS-2 / AS-3: the pure guards
# ==========================================================================


class LaunchSeamUnit(unittest.TestCase):
    def test_ceiling_is_the_single_owner_policy_400k(self) -> None:
        # The seam ceiling is the SAME number the rotation policy uses; it is not
        # a second hard-coded copy that could drift.
        self.assertEqual(ls.CONTEXT_ROTATION_CEILING, 400_000)
        self.assertEqual(ls.CONTEXT_ROTATION_CEILING,
                         rot.RotationThresholds().context_rotation_threshold)

    # -- AS-2: the ceiling matrix ------------------------------------------

    def test_AS2_at_threshold_exactly_rotates_never_resumes(self) -> None:
        d = ls.evaluate_ceiling(True, 400_000, True)
        self.assertIsNotNone(d)
        self.assertEqual(d.action, ls.ROTATE)
        self.assertEqual(d.code, ls.OVER_CEILING_RESUME_FORBIDDEN)

    def test_AS2_above_threshold_rotates(self) -> None:
        d = ls.evaluate_ceiling(True, 640_224, True)  # the live cycle-2 value
        self.assertEqual(d.action, ls.ROTATE)
        self.assertEqual(d.code, ls.OVER_CEILING_RESUME_FORBIDDEN)

    def test_AS2_below_threshold_resume_permitted(self) -> None:
        self.assertIsNone(ls.evaluate_ceiling(True, 399_999, True))

    def test_AS2_missing_telemetry_fails_closed_never_assumed_below(self) -> None:
        # None tokens, or usage not known: fail closed, NOT an assumed-below zero.
        self.assertEqual(ls.evaluate_ceiling(True, None, False).code,
                         ls.CEILING_TELEMETRY_MISSING)
        self.assertEqual(ls.evaluate_ceiling(True, None, True).code,
                         ls.CEILING_TELEMETRY_MISSING)
        # usage_known False with a stale number present is still unknown.
        self.assertEqual(ls.evaluate_ceiling(True, 10, False).code,
                         ls.CEILING_TELEMETRY_MISSING)

    def test_AS2_fresh_launch_has_no_ceiling(self) -> None:
        # A fresh (non-resuming) launch cannot be an over-ceiling resume, even with
        # unknown telemetry.
        self.assertIsNone(ls.evaluate_ceiling(False, None, False))
        self.assertIsNone(ls.evaluate_ceiling(False, 999_999, True))

    # -- AS-3: cwd binding, Windows path forms -----------------------------

    def test_AS3_matching_worktree_proceeds(self) -> None:
        self.assertIsNone(ls.evaluate_cwd(WORKTREE, WORKTREE, PRIMARY))

    def test_AS3_windows_drive_case_and_slashes_still_match(self) -> None:
        # A drive-letter case difference and a slash-direction difference are the
        # SAME directory; a primary-checkout launch can never masquerade this way.
        alt = "c:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107"
        self.assertTrue(ls.same_path(WORKTREE, alt))
        self.assertIsNone(ls.evaluate_cwd(alt, WORKTREE, PRIMARY))

    def test_AS3_primary_checkout_cwd_fails_closed_named_specifically(self) -> None:
        d = ls.evaluate_cwd(PRIMARY, WORKTREE, PRIMARY)
        self.assertEqual(d.action, ls.REFUSE)
        self.assertEqual(d.code, ls.CWD_PRIMARY_CHECKOUT)

    def test_AS3_unexpected_cwd_fails_closed(self) -> None:
        d = ls.evaluate_cwd(r"C:\somewhere\else", WORKTREE, PRIMARY)
        self.assertEqual(d.code, ls.CWD_MISMATCH)

    def test_AS3_unbound_or_empty_cwd_fails_closed(self) -> None:
        self.assertEqual(ls.evaluate_cwd("", WORKTREE, PRIMARY).code, ls.CWD_UNBOUND)
        self.assertEqual(ls.evaluate_cwd(WORKTREE, "", PRIMARY).code, ls.CWD_UNBOUND)

    # -- packet worktree binding (the production CLI gate) -----------------

    def test_packet_relative_worktree_name_matches_basename(self) -> None:
        self.assertIsNone(ls.evaluate_packet_worktree_binding(
            WORKTREE, "wt-m0t107", PRIMARY))

    def test_packet_worktree_mismatch_on_primary_is_named(self) -> None:
        # The reproduced defect: packet declares wt-m0t107, launch bound to ctl24.
        d = ls.evaluate_packet_worktree_binding(PRIMARY, "wt-m0t107", PRIMARY)
        self.assertEqual(d.code, ls.CWD_PRIMARY_CHECKOUT)

    def test_packet_with_no_worktree_is_not_constrained_here(self) -> None:
        # single-checkout runs / older harnesses declare no worktree; the runner's
        # own cwd==expected guard still holds.
        self.assertIsNone(ls.evaluate_packet_worktree_binding(PRIMARY, "", PRIMARY))

    # -- item 4: UNC and 8.3 short-name cwd forms fail CLOSED --------------

    def test_unc_matching_worktree_proceeds_but_mismatch_fails_closed(self) -> None:
        unc = r"\\server\share\wt-m0t107"
        self.assertTrue(ls.same_path(unc, r"\\SERVER\share\wt-m0t107"))  # case-folded
        self.assertIsNone(ls.evaluate_cwd(unc, unc))
        # a UNC cwd that is not the expected worktree fails closed
        d = ls.evaluate_cwd(r"\\server\share\ctl24", unc)
        self.assertEqual(d.code, ls.CWD_MISMATCH)

    def test_8_3_short_name_cwd_fails_closed_against_long_name(self) -> None:
        # `os.path.normcase/normpath` do NOT expand an 8.3 short name, so a
        # short-name cwd cannot be PROVEN equal to the long-name worktree and is
        # refused (conservative fail-closed) rather than assumed equal.
        short = r"C:\Users\MLFLL\DOWNLO~1\nyc-zoning\wt-m0t107"
        long = r"C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t107"
        self.assertFalse(ls.same_path(short, long))
        self.assertEqual(ls.evaluate_cwd(short, long).code, ls.CWD_MISMATCH)

    # -- combined enforce_launch -------------------------------------------

    def test_enforce_launch_cwd_precedes_ceiling(self) -> None:
        # A bad cwd is reported even when the ceiling would also refuse.
        ctx = ls.WorkerLaunchContext(
            cwd=PRIMARY, expected_worktree=WORKTREE, primary_checkout=PRIMARY,
            resuming=True, session_context_tokens=None, session_usage_known=False)
        self.assertEqual(ls.enforce_launch(ctx).code, ls.CWD_PRIMARY_CHECKOUT)

    def test_enforce_launch_proceed_when_both_pass(self) -> None:
        ctx = ls.WorkerLaunchContext(
            cwd=WORKTREE, expected_worktree=WORKTREE, primary_checkout=PRIMARY,
            resuming=True, session_context_tokens=100, session_usage_known=True)
        self.assertTrue(ls.enforce_launch(ctx).ok)

    def test_enforce_or_raise_raises_on_refuse(self) -> None:
        ctx = ls.WorkerLaunchContext(cwd=PRIMARY, expected_worktree=WORKTREE,
                                     primary_checkout=PRIMARY)
        with self.assertRaises(ls.LaunchSeamError) as cm:
            ls.enforce_or_raise(ctx)
        self.assertEqual(cm.exception.code, ls.CWD_PRIMARY_CHECKOUT)


class SessionTelemetry(unittest.TestCase):
    def test_tokens_round_trip_when_usage_known(self) -> None:
        rec = sc.ProviderSession(session_id="s", context_tokens=604_772,
                                 usage_known=True)
        back = sc.ProviderSession.from_dict(rec.to_dict())
        self.assertEqual(back.context_tokens, 604_772)
        self.assertTrue(back.usage_known)

    def test_legacy_record_without_tokens_is_unknown_not_zero(self) -> None:
        # The preserved provider_session_continuity had NO context_tokens key.
        legacy = {"session_id": "798d2f00", "run_id": "run_x", "cycle": 1}
        back = sc.ProviderSession.from_dict(legacy)
        self.assertIsNone(back.context_tokens)
        self.assertFalse(back.usage_known)

    def test_record_provider_session_never_stores_unknown_as_zero(self) -> None:
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


# ==========================================================================
# AS-1 / AS-3 / AS-6: the ironclad runner chokepoint (real run_unit, fake exe)
# ==========================================================================


class RunnerChokepoint(unittest.TestCase):
    """`ClaudeRunner.run_unit` is the single provider-contact `Popen`. With a
    worktree bound, the seam refuses BEFORE the process starts. A fake executable
    that would print a session id proves the refusal happens pre-launch (the
    process never runs, so no session id is ever parsed)."""

    def _runner(self, **cfg) -> cr.ClaudeRunner:
        base = dict(executable=sys.executable, max_turns=2, timeout_seconds=30.0)
        base.update(cfg)
        return cr.ClaudeRunner(cr.RunnerConfig(**base))

    def test_AS3_cwd_primary_checkout_refuses_before_launch(self) -> None:
        runner = self._runner(cwd=PRIMARY, expected_worktree=WORKTREE,
                              primary_checkout=PRIMARY)
        with self.assertRaises(cr.RunnerError) as cm:
            runner.run_unit("hi")
        self.assertEqual(cm.exception.code, ls.CWD_PRIMARY_CHECKOUT)

    def test_AS3_cwd_mismatch_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            runner = self._runner(cwd=d, expected_worktree=WORKTREE,
                                  primary_checkout=PRIMARY)
            with self.assertRaises(cr.RunnerError) as cm:
                runner.run_unit("hi")
            self.assertEqual(cm.exception.code, ls.CWD_MISMATCH)

    def test_AS1_over_ceiling_resume_refuses_before_launch(self) -> None:
        # A --resume of an at/above-ceiling session must never reach Popen.
        with tempfile.TemporaryDirectory() as d:
            runner = self._runner(
                cwd=d, expected_worktree=d, resume_session_id="prov-1",
                resume_capability_verified=True,
                resume_context_tokens=640_224, resume_usage_known=True)
            with self.assertRaises(cr.RunnerError) as cm:
                runner.run_unit("hi")
            self.assertEqual(cm.exception.code, ls.OVER_CEILING_RESUME_FORBIDDEN)

    def test_AS1_resume_with_unknown_telemetry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            runner = self._runner(
                cwd=d, expected_worktree=d, resume_session_id="prov-1",
                resume_capability_verified=True,
                resume_context_tokens=None, resume_usage_known=False)
            with self.assertRaises(cr.RunnerError) as cm:
                runner.run_unit("hi")
            self.assertEqual(cm.exception.code, ls.CEILING_TELEMETRY_MISSING)

    def test_unbound_runner_defers_cwd_guard_to_the_loop_seam(self) -> None:
        # A runner with no expected_worktree (the many fake-executable tests) does
        # NOT enforce the cwd guard at this layer - it defers to the loop/CLI seam
        # that holds the packet worktree. The seam skips the cwd guard when no
        # worktree was bound, so a primary-checkout cwd here is not refused at the
        # runner layer (it is caught upstream by the CLI packet-binding gate).
        ctx = ls.WorkerLaunchContext(cwd=PRIMARY, expected_worktree="")
        self.assertTrue(ls.enforce_launch(ctx).ok)

    def test_R332_worktree_less_over_ceiling_resume_still_refuses(self) -> None:
        # The exact G5 SEC-MINOR hypothetical (owner row R332 "EVERY path"): a
        # resume-capable RunnerConfig with NO expected_worktree bound and 640k
        # telemetry must STILL refuse at the chokepoint. The ceiling guard runs
        # unconditionally (only the cwd guard defers when no worktree is bound), so
        # the over-ceiling --resume never reaches Popen even on an unbound runner.
        with tempfile.TemporaryDirectory() as d:
            runner = self._runner(
                cwd=d, resume_session_id="prov-1",  # NO expected_worktree
                resume_capability_verified=True,
                resume_context_tokens=640_224, resume_usage_known=True)
            self.assertEqual(runner.config.expected_worktree, "")
            with self.assertRaises(cr.RunnerError) as cm:
                runner.run_unit("hi")
            self.assertEqual(cm.exception.code, ls.OVER_CEILING_RESUME_FORBIDDEN)

    def test_R332_worktree_less_resume_unknown_telemetry_still_fails_closed(self) -> None:
        # The sibling: an unbound resume with UNKNOWN telemetry fails closed at the
        # chokepoint too (never assumed below the ceiling).
        with tempfile.TemporaryDirectory() as d:
            runner = self._runner(
                cwd=d, resume_session_id="prov-1",  # NO expected_worktree
                resume_capability_verified=True,
                resume_context_tokens=None, resume_usage_known=False)
            with self.assertRaises(cr.RunnerError) as cm:
                runner.run_unit("hi")
            self.assertEqual(cm.exception.code, ls.CEILING_TELEMETRY_MISSING)


# ==========================================================================
# AS-1 / AS-4: the loop-level pre-first-dispatch ceiling seam
# ==========================================================================


def _checkpoint(**kw) -> ClaudeCheckpoint:
    data = dict(schema_version="1.1", checkpoint_id="cp-1", status="UNIT_COMPLETE",
                task_id="M0-T107", run_id="run_33dfa57d54db",
                claude_session_id="sess-fresh",
                starting_sha="a" * 40, current_sha="a" * 40,
                branch="control/D-024-fable-codex-loop", worktree="wt",
                summary="did work", proposed_next_action="next",
                changed_files=(), tests=(), blockers=(),
                owner_decisions_required=())
    data.update(kw)
    return ClaudeCheckpoint.from_dict(data)


class _FakeRunner:
    """A runner that records prompts and its launch config, honouring with_resume."""

    def __init__(self) -> None:
        self.prompts: list[str] = []
        self.resumed: list[str] = []
        self.config = cr.RunnerConfig(executable="fake-claude")

    def with_model(self, model):  # pragma: no cover - not exercised here
        return self

    def with_resume(self, provider_session_id, *, context_tokens=None,
                    usage_known=False):
        self.resumed.append(provider_session_id)
        clone = _FakeRunner()
        clone.prompts = self.prompts
        clone.resumed = self.resumed
        clone.config = dataclasses.replace(
            self.config, resume_session_id=provider_session_id)
        return clone

    def run_unit(self, prompt, **_kw):
        self.prompts.append(prompt)
        return cr.RunResult(argv=("fake",), returncode=0, duration_seconds=0.1,
                            session_id="sess-fresh", checkpoint=_checkpoint(),
                            containment="job_object")


class PreDispatchCeilingSeam(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.journal = DurableJournal(self.tmp / "j.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run_33dfa57d54db"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T107",
             "allowed_paths": ["tools/agent_supervisor/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(self.tmp), worktree=str(self.tmp),
            branch="control/D-024-fable-codex-loop", stage="phase4")

    def _seed_over_ceiling(self, *, tokens_present: bool) -> None:
        """Reconstruct the durable cycle-2 START shape: rotation_pending set at a
        context crossing, a recorded provider session that would be carried
        forward. `tokens_present=False` models the live pre-fix record (no token
        field -> unknown telemetry)."""
        self.journal.set_state(rot.ROTATION_PENDING_KEY, True)
        self.journal.set_state(rot.ROTATION_REASON_KEY, "context_threshold")
        sc.record_provider_session(
            self.journal, session_id="798d2f00", run_id=self.run_id, cycle=1,
            context_tokens=(604_772 if tokens_present else None),
            usage_known=tokens_present)

    def _loop(self, runner) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T107",
                                 stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=2),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority, runner=runner,
            reviewer=None, run_id=self.run_id,
            context_rotation_threshold=CEILING)

    def test_AS1_pre_fix_path_would_carry_the_over_ceiling_session_forward(self) -> None:
        # RED reproduction WITHOUT a git write: the pre-fix run() had no
        # pre-first-dispatch seam, so at the first dispatch the recorded provider
        # session is still present and rotation_pending is still set - exactly the
        # cycle-2 state that dispatched a unit on the over-ceiling session.
        self._seed_over_ceiling(tokens_present=True)
        loop = self._loop(_FakeRunner())
        # The constructor restored the over-ceiling session id.
        self.assertEqual(loop._provider_session_id, "798d2f00")
        self.assertTrue(rot.rotation_pending(self.journal))

    def test_AS1_fixed_seam_sheds_before_first_dispatch(self) -> None:
        # GREEN: the pre-first-dispatch seam sheds the over-ceiling session and
        # consumes the durable rotation flag, so the first unit launches fresh.
        self._seed_over_ceiling(tokens_present=True)
        loop = self._loop(_FakeRunner())
        rotated = loop._rotate_over_ceiling_before_first_dispatch(cycle=1)
        self.assertTrue(rotated)
        self.assertEqual(loop._provider_session_id, "")           # shed
        self.assertIsNone(sc.recorded_provider_session(self.journal))
        self.assertFalse(rot.rotation_pending(self.journal))      # consumed
        # a first-class audit event names the shed
        events = [json.loads(line) for line in
                  (self.tmp / "audit.jsonl").read_text().splitlines()]
        self.assertIn("over_ceiling_session_shed", [e["event_type"] for e in events])

    def test_AS1_sheds_on_durable_flag_even_when_telemetry_unknown(self) -> None:
        # The live provider_session_continuity carried NO token field, yet the
        # durable rotation_pending(context_threshold) flag is enough to shed.
        self._seed_over_ceiling(tokens_present=False)
        loop = self._loop(_FakeRunner())
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertEqual(loop._provider_session_id, "")

    def test_AS4_a_below_ceiling_session_is_not_shed(self) -> None:
        # A recorded session below the ceiling with no pending flag is preserved.
        sc.record_provider_session(self.journal, session_id="ok-1",
                                   run_id=self.run_id, cycle=1,
                                   context_tokens=100, usage_known=True)
        loop = self._loop(_FakeRunner())
        self.assertFalse(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertEqual(loop._provider_session_id, "ok-1")

    def test_AS4_shed_is_idempotent_second_call_is_noop(self) -> None:
        self._seed_over_ceiling(tokens_present=True)
        loop = self._loop(_FakeRunner())
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertFalse(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))

    # -- R337: per-property preservation across the shed/rotation ----------
    #
    # Snapshot-before/after (the M0-T121 AS-8 pattern): the shed to a fresh
    # session must preserve EACH of the seven owner-named properties individually.

    def _audit_records(self) -> list[dict]:
        text = (self.tmp / "audit.jsonl").read_text() if (
            self.tmp / "audit.jsonl").exists() else ""
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def _loop_with_lineage(self) -> lp.SupervisedLoop:
        """A loop seeded with the over-ceiling shape AND checkpoint lineage."""
        self._seed_over_ceiling(tokens_present=True)
        loop = self._loop(_FakeRunner())
        loop._last_checkpoint_id = "cp-lineage-7"
        loop._last_checkpoint = _checkpoint(checkpoint_id="cp-lineage-7")
        return loop

    def test_R337_checkpoint_lineage_preserved(self) -> None:
        loop = self._loop_with_lineage()
        before_id, before_cp = loop._last_checkpoint_id, loop._last_checkpoint
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertEqual(loop._last_checkpoint_id, before_id)
        self.assertIs(loop._last_checkpoint, before_cp)

    def test_R337_task_identity_preserved(self) -> None:
        loop = self._loop_with_lineage()
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertEqual(loop.config.task_id, "M0-T107")
        self.assertEqual(loop.authority.task_id, "M0-T107")
        self.assertEqual(loop.run_id, self.run_id)

    def test_R337_branch_and_worktree_preserved(self) -> None:
        loop = self._loop_with_lineage()
        before_branch, before_wt = loop.authority.branch, loop.authority.worktree
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        self.assertEqual(loop.authority.branch, before_branch)
        self.assertEqual(loop.authority.worktree, before_wt)

    def test_R337_budgets_untouched(self) -> None:
        # The owner-touch budget counter is not spent by the shed, and no budget
        # state key changes: the ONLY durable keys the shed moves are the provider
        # session and the two rotation keys.
        loop = self._loop_with_lineage()
        touches_before = loop.touches.report()
        before = dict(self.journal.all_state())
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        after = dict(self.journal.all_state())
        changed = {k for k in set(before) | set(after)
                   if before.get(k) != after.get(k)}
        self.assertEqual(
            changed,
            {sc.PROVIDER_SESSION_KEY, rot.ROTATION_PENDING_KEY, rot.ROTATION_REASON_KEY},
            f"the shed moved unexpected durable state: {changed}")
        self.assertEqual(loop.touches.report(), touches_before)

    def test_R337_audit_history_verifies_and_only_grows(self) -> None:
        loop = self._loop_with_lineage()
        before = self._audit_records()
        before_keys = {(r.get("sequence"), r.get("event_type")) for r in before}
        self.assertTrue(self.audit.verify_chain().ok)
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        after = self._audit_records()
        after_keys = {(r.get("sequence"), r.get("event_type")) for r in after}
        # chain still verifies, NO prior record removed, exactly the shed appended
        self.assertTrue(self.audit.verify_chain().ok)
        self.assertTrue(before_keys.issubset(after_keys),
                        "a prior audit record was removed or altered")
        self.assertEqual(len(after), len(before) + 1)
        self.assertEqual(after[-1]["event_type"], "over_ceiling_session_shed")

    def test_R337_exactly_once_succession_no_duplicate_or_lost_unit(self) -> None:
        loop = self._loop_with_lineage()
        first = loop._rotate_over_ceiling_before_first_dispatch(cycle=1)
        second = loop._rotate_over_ceiling_before_first_dispatch(cycle=1)
        self.assertTrue(first)
        self.assertFalse(second)  # no second shed -> no duplicated succession
        sheds = [r for r in loop._rotations
                 if r.get("kind") == "over_ceiling_shed_pre_dispatch"]
        self.assertEqual(len(sheds), 1, "the shed must record exactly one succession")
        # the shed session id is captured (not lost), and the new session is distinct
        self.assertEqual(sheds[0]["shed_provider_session_id"], "798d2f00")
        self.assertEqual(loop._provider_session_id, "")  # fresh -> distinct id later


# ==========================================================================
# AS-3 / AS-6: the production CLI worktree-binding gate
# ==========================================================================


class CliWorktreeGate(unittest.TestCase):
    def test_packet_worktree_mismatch_is_a_typed_loop_refusal(self) -> None:
        # A packet that declares a worktree the bound cwd does not match is a
        # LaunchSeam refusal; `_run_loop` raises it as a LoopError, which cmd_start
        # renders as a typed refusal rather than a traceback.
        d = ls.evaluate_packet_worktree_binding(PRIMARY, "wt-m0t107", PRIMARY)
        self.assertIsNotNone(d)
        self.assertIn(d.code, (ls.CWD_PRIMARY_CHECKOUT, ls.CWD_MISMATCH))


class CliRepoBindingGateD2(unittest.TestCase):
    """M0-T126 (D-024-R372; defect D2): the evidence/review repo must not be the
    primary control checkout when the packet declares an isolated worktree."""

    def test_repo_on_primary_checkout_with_isolated_worktree_refuses(self) -> None:
        d = ls.evaluate_repo_binding(PRIMARY, "wt-m0t107", primary_checkout=PRIMARY)
        self.assertIsNotNone(d)
        self.assertEqual(d.code, ls.REPO_PRIMARY_CHECKOUT)
        self.assertFalse(d.ok)

    def test_repo_on_the_pack_repo_is_allowed(self) -> None:
        # The correct shape (runbook §11): repo = the pack repo, distinct from
        # both the control checkout and the worktree.
        self.assertIsNone(ls.evaluate_repo_binding(
            r"C:\repo\pack", "wt-m0t107", primary_checkout=PRIMARY))

    def test_no_packet_worktree_is_unconstrained(self) -> None:
        self.assertIsNone(ls.evaluate_repo_binding(PRIMARY, "", primary_checkout=PRIMARY))

    def test_repo_equal_to_worktree_is_allowed(self) -> None:
        self.assertIsNone(ls.evaluate_repo_binding(
            "wt-m0t107", "wt-m0t107", primary_checkout=PRIMARY))

    def test_repo_binding_code_is_registered(self) -> None:
        self.assertIn(ls.REPO_PRIMARY_CHECKOUT, ls.REFUSAL_CODES)


# ==========================================================================
# R342: dedicated tests for the four indirectly-covered matrix items
# ==========================================================================


class MatrixR342StaleSessionIdentity(unittest.TestCase):
    """(a) A stale/mismatched recorded session id is surfaced, never silently
    adopted. `recorded_provider_session` is scoped by run_id: a record from a
    DIFFERENT run reads as absent (the fail-closed continuity answer)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.journal = DurableJournal(
            pathlib.Path(self._tmp.name) / "j.sqlite3").open()
        self.addCleanup(self.journal.close)

    def test_a_foreign_run_session_is_not_adopted_by_this_run(self) -> None:
        sc.record_provider_session(self.journal, session_id="stale-A",
                                   run_id="run-A", cycle=3,
                                   context_tokens=100, usage_known=True)
        # This run (run-B) must NOT see run-A's leftover session.
        self.assertIsNone(sc.recorded_provider_session(self.journal, run_id="run-B"))
        # Its own run still reads it; the watchdog (no run_id) reads whoever's last.
        self.assertEqual(
            sc.recorded_provider_session(self.journal, run_id="run-A").session_id,
            "stale-A")
        self.assertEqual(
            sc.recorded_provider_session(self.journal).session_id, "stale-A")

    def test_the_loop_does_not_restore_a_foreign_run_session(self) -> None:
        sc.record_provider_session(self.journal, session_id="stale-A",
                                   run_id="run-A", cycle=3,
                                   context_tokens=999_999, usage_known=True)
        audit = AuditLog(pathlib.Path(self._tmp.name) / "audit.jsonl", fsync=False)
        authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T107", "allowed_paths": ["tools/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=self._tmp.name, worktree=self._tmp.name,
            branch="b", stage="phase4")
        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T107", stage="phase4",
                                 allowed_paths=authority.allowed_paths,
                                 stop_conditions=("x",), max_cycles=2,
                                 owner_touch_budget=2),
            journal=self.journal,
            audit=audit,
            machine=StateMachine(self.journal, audit, "run-B"),
            authority=authority, runner=_FakeRunner(), reviewer=None,
            run_id="run-B", context_rotation_threshold=CEILING)
        # run-B never adopts run-A's stale (over-ceiling) session id.
        self.assertEqual(loop._provider_session_id, "")
        self.assertIsNone(loop._recorded_session_tokens)


class MatrixR342ControllerRestart(unittest.TestCase):
    """(b) End-to-end shape: a HALTED-lineage journal that an owner-restart moved
    to a restartable state -> the START path hits the shed/seam BEFORE the first
    dispatch, so the first unit runs on a fresh session (no --resume)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.journal = DurableJournal(self.tmp / "j.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run_33dfa57d54db"
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T107", "allowed_paths": ["tools/agent_supervisor/**"],
             "forbidden_paths": [".github/**"], "status": "in_progress"},
            repo_root=str(self.tmp), worktree=str(self.tmp),
            branch="control/D-024-fable-codex-loop", stage="phase4")

    def test_restart_start_path_sheds_then_dispatches_fresh(self) -> None:
        # HALTED-lineage shape an owner-restart left restartable: over-ceiling
        # session recorded + unconsumed context rotation flag.
        self.journal.set_state(rot.ROTATION_PENDING_KEY, True)
        self.journal.set_state(rot.ROTATION_REASON_KEY, "context_threshold")
        sc.record_provider_session(self.journal, session_id="798d2f00",
                                   run_id=self.run_id, cycle=1,
                                   context_tokens=604_772, usage_known=True)
        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="supervised", task_id="M0-T107", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("x",), max_cycles=2,
                                 owner_touch_budget=2),
            journal=self.journal, audit=self.audit,
            machine=StateMachine(self.journal, self.audit, self.run_id),
            authority=self.authority, runner=_FakeRunner(), reviewer=None,
            run_id=self.run_id, context_rotation_threshold=CEILING)
        # This is what run() does at the top before the first cycle.
        self.assertTrue(loop._rotate_over_ceiling_before_first_dispatch(cycle=1))
        # Now the first dispatch: it carries NO resume binding (fresh session).
        self.assertEqual(loop._provider_session_id, "")
        self.assertEqual(loop.runner.config.resume_session_id, "")
        result = loop.runner.run_unit("first unit after restart")
        self.assertEqual(loop.runner.prompts, ["first unit after restart"])
        self.assertEqual(loop.runner.resumed, [])  # with_resume never called
        # the shed left a durable, chain-verified audit record of the succession
        self.assertTrue(self.audit.verify_chain().ok)
        self.assertEqual(result.session_id, "sess-fresh")


class MatrixR342ConcurrentControllers(unittest.TestCase):
    """(c) One supervisor per checkout: with the single-instance lock held by a
    LIVE foreign pid, a second controller's launch path fails closed
    (`lock_held`) - the restart_channel lock-contention pattern applied at launch."""

    def setUp(self) -> None:
        self._co = tempfile.TemporaryDirectory()
        self._base = tempfile.TemporaryDirectory()
        self.addCleanup(self._co.cleanup)
        self.addCleanup(self._base.cleanup)
        self.checkout = pathlib.Path(self._co.name).resolve()
        self.base = pathlib.Path(self._base.name).resolve()
        self.runtime = runtime_dir_for(self.checkout, base=self.base)
        self.runtime.mkdir(parents=True)

    def _lock(self, pid=None) -> SingleInstanceLock:
        return SingleInstanceLock(self.runtime,
                                  checkout_key=checkout_key(self.checkout),
                                  controller_version="0.3.0-test", pid=pid)

    def test_live_foreign_lock_refuses_a_second_launch(self) -> None:
        foreign = self._lock(pid=os.getppid())  # a live, different pid
        foreign.acquire()
        try:
            with self.assertRaises(LockError) as cm:
                self._lock().acquire()
            self.assertEqual(getattr(cm.exception, "code", ""), "lock_held")
        finally:
            foreign.release()

    def test_a_stale_lock_is_taken_over_not_refused(self) -> None:
        stale = self._lock(pid=999_999_998)  # not a live pid
        stale.acquire()
        # a legitimate second controller takes over a dead holder's lock
        self._lock().acquire()


class MatrixR342ProviderFailureAtLaunch(unittest.TestCase):
    """(d) A provider failure at launch never becomes a crash-with-half-record.
    A seam refusal at launch is a TYPED RunnerError and records NO child; a raw
    Popen failure (missing executable) records NO child either (the launch-record
    is written only AFTER Popen returns), so there is never a half-recorded
    launch. NOTE (honest): the raw Popen OSError itself is not yet re-typed as a
    RunnerError - production preflight guards a missing binary upstream, and
    typing it is a candidate follow-up outside this bounded round's one-line
    production unwrap."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.journal = DurableJournal(self.tmp / "j.sqlite3").open()
        self.addCleanup(self.journal.close)

    def _runner(self, **cfg) -> cr.ClaudeRunner:
        base = dict(executable=str(self.tmp / "missing.exe"), max_turns=2,
                    timeout_seconds=30.0, cwd=str(self.tmp))
        base.update(cfg)
        return cr.ClaudeRunner(cr.RunnerConfig(**base), journal=self.journal,
                               run_id="run-x")

    def test_seam_refusal_at_launch_is_typed_and_records_no_child(self) -> None:
        runner = self._runner(
            expected_worktree=str(self.tmp), resume_session_id="prov-1",
            resume_capability_verified=True,
            resume_context_tokens=640_224, resume_usage_known=True)
        with self.assertRaises(cr.RunnerError) as cm:
            runner.run_unit("hi")
        self.assertEqual(cm.exception.code, ls.OVER_CEILING_RESUME_FORBIDDEN)
        self.assertEqual(len(rec.account_for_children(self.journal)), 0,
                         "a refused launch must not half-record a child")

    def test_raw_popen_failure_records_no_child(self) -> None:
        # A missing executable raises an OSError (current behavior) but leaves NO
        # recorded child, so there is never a half-recorded launch.
        runner = self._runner()  # no worktree, no resume -> seam passes, Popen fails
        with self.assertRaises(OSError):
            runner.run_unit("hi")
        self.assertEqual(len(rec.account_for_children(self.journal)), 0,
                         "a crashed launch must not half-record a child")


# ==========================================================================
# AS-5 / R339 / R340: the deterministic, removal-sensitive reachability sweep
# ==========================================================================


class ReachabilitySweep(unittest.TestCase):
    """Every worker-launch/resume path routes through the launch seam. The sweep
    derives its facts from source ASTs (nothing hand-listed), so REMOVING a seam
    call from any site turns the relevant assertion RED. Each check ships with its
    own RED reproduction against a bypass shape."""

    # -- helpers -----------------------------------------------------------

    def _func_src(self, fn) -> str:
        return textwrap.dedent(inspect.getsource(fn))

    def _call_linenos(self, src: str, dotted: str) -> list[int]:
        """Line numbers of every call whose function is the given dotted name
        (e.g. 'launch_seam.enforce_launch' or 'subprocess.Popen')."""
        tree = ast.parse(src)
        out: list[int] = []
        want = tuple(dotted.split("."))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = self._dotted(node.func)
                if name and tuple(name.split("."))[-len(want):] == want:
                    out.append(node.lineno)
        return sorted(out)

    def _dotted(self, node) -> str:
        parts: list[str] = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))

    def _names_called(self, src: str) -> set[str]:
        tree = ast.parse(src)
        return {self._dotted(n.func) for n in ast.walk(tree)
                if isinstance(n, ast.Call) and self._dotted(n.func)}

    def _strip_stmts(self, src: str, dotted_substr: str) -> str:
        """Remove every top-level-or-nested STATEMENT whose subtree contains a call
        to a function whose dotted name ends with `dotted_substr`, then unparse.

        Removing the whole statement (not a single line) keeps a multi-line call
        from leaving a syntax fragment behind, so the resulting bypass source is
        valid Python the same checker can be run against - a faithful, deterministic
        removal-sensitivity probe."""
        tree = ast.parse(textwrap.dedent(src))

        def contains(node) -> bool:
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    name = self._dotted(n.func)
                    if name and name.endswith(dotted_substr):
                        return True
            return False

        class Pruner(ast.NodeTransformer):
            def visit(self, node):
                node = self.generic_visit(node)
                if isinstance(node, ast.stmt) and contains(node):
                    return None
                return node

        pruned = Pruner().visit(tree)
        ast.fix_missing_locations(pruned)
        return ast.unparse(pruned)

    def _dispatchers(self) -> dict[str, set[str]]:
        """Every package function that BOTH builds the worker argv (`build_argv`)
        and launches a `subprocess.Popen`, mapped to the call-names it makes."""
        pkg_dir = REPO / "tools" / "agent_supervisor"
        out: dict[str, set[str]] = {}
        for path in sorted(pkg_dir.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = ast.get_source_segment(text, node) or ""
                    names = self._names_called(body)
                    builds = any(n.endswith("build_argv") for n in names)
                    pops = any(n.endswith("Popen") for n in names)
                    if builds and pops:
                        out[f"{path.name}:{node.name}"] = names
        return out

    # -- run_unit: the ironclad Popen chokepoint ---------------------------

    def test_run_unit_seam_precedes_the_only_worker_popen(self) -> None:
        src = self._func_src(cr.ClaudeRunner.run_unit)
        seam = self._call_linenos(src, "launch_seam.enforce_launch")
        popen = self._call_linenos(src, "subprocess.Popen")
        self.assertTrue(seam, "run_unit must call the launch seam")
        self.assertEqual(len(popen), 1, "run_unit must have exactly one worker Popen")
        self.assertLess(min(seam), popen[0],
                        "the launch seam must run BEFORE the worker Popen")

    def _enforce_nested_under_expected_worktree_if(self, src: str) -> bool:
        """True when the `enforce_launch` call sits inside the body of an `if` whose
        test references `expected_worktree` - i.e. the seam is CONDITIONALLY skipped
        for unbound runners (the pre-hardening wrapper). The seam must run
        UNCONDITIONALLY (owner row R332 "EVERY path"), so this must be False."""
        tree = ast.parse(textwrap.dedent(src))
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            test_names = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name)}
            test_attrs = {n.attr for n in ast.walk(node.test)
                          if isinstance(n, ast.Attribute)}
            if "expected_worktree" not in (test_names | test_attrs):
                continue
            for stmt in node.body:
                for n in ast.walk(stmt):
                    if (isinstance(n, ast.Call)
                            and (self._dotted(n.func) or "").endswith("enforce_launch")):
                        return True
        return False

    def test_R332_seam_is_not_nested_under_an_expected_worktree_guard(self) -> None:
        # The unwrap invariant: the chokepoint seam runs unconditionally, NOT inside
        # `if self.config.expected_worktree:`. Re-wrapping it turns this RED.
        src = self._func_src(cr.ClaudeRunner.run_unit)
        self.assertFalse(self._enforce_nested_under_expected_worktree_if(src),
                         "run_unit's enforce_launch must not be nested under an "
                         "`if ... expected_worktree` guard (R332: EVERY path)")

    def test_RED_re_wrapping_the_seam_under_the_guard_is_detected(self) -> None:
        # Removal/regression sensitivity: a synthetic run_unit whose seam call is
        # re-wrapped under `if self.config.expected_worktree:` is caught by the check.
        rewrapped = textwrap.dedent('''
            def run_unit(self):
                argv = build_argv(self.config)
                if self.config.expected_worktree:
                    _decision = launch_seam.enforce_launch(x)
                    if not _decision.ok:
                        raise RunnerError(_decision.code, _decision.message)
                process = subprocess.Popen(argv)
        ''')
        self.assertTrue(
            self._enforce_nested_under_expected_worktree_if(rewrapped),
            "the check must flag a seam re-wrapped under the expected_worktree guard")

    def test_the_only_worker_dispatch_popen_is_run_unit_and_it_is_seam_guarded(self) -> None:
        # Two package functions build the worker argv and Popen: the WORKER
        # DISPATCH (`run_unit`, which brokers permissions and extracts a
        # checkpoint) and the model-availability PROBE (`probe_model_launch`, a
        # bounded capability check that runs no work, brokers no permission, and
        # resumes nothing). Only the dispatch carries or resumes a worker unit, so
        # only it must route through the launch seam - and it does.
        dispatchers = self._dispatchers()
        self.assertEqual(set(dispatchers),
                         {"claude_runner.py:run_unit",
                          "claude_runner.py:probe_model_launch"},
                         f"unexpected worker-argv+Popen sites: {sorted(dispatchers)}")
        worker = dispatchers["claude_runner.py:run_unit"]
        probe = dispatchers["claude_runner.py:probe_model_launch"]
        # the WORKER dispatch is the seam-guarded one that appends the S8.3
        # checkpoint contract to a work prompt; it routes through the launch seam.
        self.assertIn("launch_seam.enforce_launch", worker)
        self.assertTrue(any(n.endswith("with_checkpoint_contract") for n in worker),
                        "the worker dispatch appends the checkpoint contract")
        # the availability PROBE is not seam-guarded and appends no work contract:
        # it launches a bounded capability check, never a worker unit, and resumes
        # nothing - so the ceiling and cwd-binding guards do not apply to it.
        self.assertNotIn("launch_seam.enforce_launch", probe)
        self.assertFalse(any(n.endswith("with_checkpoint_contract") for n in probe))

    def test_RED_removing_the_seam_statement_uncovers_run_unit(self) -> None:
        # Removal sensitivity: prune the seam STATEMENT from run_unit and the
        # 'seam precedes Popen' invariant must fail while Popen still runs.
        bypass = self._strip_stmts(self._func_src(cr.ClaudeRunner.run_unit),
                                   "enforce_launch")
        seam = self._call_linenos(bypass, "launch_seam.enforce_launch")
        popen = self._call_linenos(bypass, "subprocess.Popen")
        self.assertEqual(seam, [], "the bypass shape has no seam call")
        self.assertTrue(popen, "but still reaches Popen -> RED (bypass detected)")

    # -- _run_loop: the production cwd wiring ------------------------------

    def test_run_loop_wires_expected_worktree_and_packet_binding(self) -> None:
        # M0-T126 (D2): the worktree binding and the new repo binding are enforced
        # together through launch_seam.enforce_launch_bindings, which internally
        # calls evaluate_packet_worktree_binding then evaluate_repo_binding.
        src = self._func_src(cli._run_loop)
        names = self._names_called(src)
        self.assertIn("launch_seam.enforce_launch_bindings", names,
                      "_run_loop must gate the packet worktree + repo bindings")
        self.assertIn("expected_worktree", src,
                      "_run_loop must bind the runner's expected_worktree")
        # The combined entry point itself must still call BOTH seam checks.
        seam_src = self._func_src(ls.enforce_launch_bindings)
        seam_names = self._names_called(seam_src)
        self.assertIn("evaluate_packet_worktree_binding", seam_names)
        self.assertIn("evaluate_repo_binding", seam_names)

    def test_RED_run_loop_without_the_gate_is_a_bypass(self) -> None:
        bypass = self._strip_stmts(self._func_src(cli._run_loop),
                                  "enforce_launch_bindings")
        self.assertNotIn("launch_seam.enforce_launch_bindings",
                         self._names_called(bypass))

    # -- loop.run: the pre-first-dispatch ceiling wiring -------------------

    def test_run_wires_the_pre_first_dispatch_ceiling_seam(self) -> None:
        names = self._names_called(self._func_src(lp.SupervisedLoop.run))
        leaves = {n.split(".")[-1] for n in names}
        self.assertIn("_rotate_over_ceiling_before_first_dispatch", leaves,
                      "run() must invoke the pre-first-dispatch ceiling seam")

    def test_the_shed_routes_through_the_launch_seam(self) -> None:
        src = self._func_src(lp.SupervisedLoop._rotate_over_ceiling_before_first_dispatch)
        self.assertIn("launch_seam.evaluate_ceiling", self._names_called(src),
                      "the ceiling decision must route through the single seam")

    def test_RED_run_without_the_shed_statement_is_a_bypass(self) -> None:
        bypass = self._strip_stmts(self._func_src(lp.SupervisedLoop.run),
                                  "_rotate_over_ceiling_before_first_dispatch")
        leaves = {n.split(".")[-1] for n in self._names_called(bypass)}
        self.assertNotIn("_rotate_over_ceiling_before_first_dispatch", leaves)


# ==========================================================================
# AS-7 / AS-8: the committed regression fixture (derived read-only)
# ==========================================================================


class FixtureRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_AS7_source_hashes_are_the_recorded_baselines(self) -> None:
        h = self.fx["source_sha256"]
        self.assertEqual(h["supervisor_journal.sqlite3"],
                         "a4acb370f3a23fd5193c27d16e729a6b6035c53c368a10c52673de8b5de29255")
        self.assertEqual(h["audit.jsonl"],
                         "e80c057cabc24478ab67d785e2f903696f6cc1fcf7cbf782db9fd6f284430c83")
        self.assertEqual(h["transcript_cycle1"],
                         "3a0d1f30664b1deba7b6cd47a0a69bdc84906332eb3ed180aea5e74e2f8b9b17")
        self.assertEqual(h["transcript_cycle2"],
                         "3c9185687f12e86a2e066b18e8347a15840be94f981a52af3965f01394adbfaf")

    def test_AS7_durable_state_reproduces_the_over_ceiling_shape(self) -> None:
        st = self.fx["durable_journal_state_at_cycle2_start"]
        self.assertTrue(st["rotation_pending"])
        self.assertEqual(st["rotation_pending_reason"], "context_threshold")
        # the live provider_session_continuity carried NO token field -> unknown
        self.assertFalse(st["provider_session_continuity"]["context_tokens_present"])

    def test_AS7_audit_excerpt_carries_the_defect_values(self) -> None:
        by = {e["sequence"]: e for e in self.fx["audit_excerpt"]}
        self.assertEqual(by[24]["detail"]["reason_code"], "context_threshold")
        self.assertIn("604772", by[24]["detail"]["detail"])
        # seq 40: the resumed unit ran to 640,224 tokens and died rc=1
        self.assertEqual(by[40]["detail"]["context_tokens"], 640_224)
        self.assertEqual(by[40]["detail"]["returncode"], 1)
        self.assertTrue(by[40]["detail"]["usage_known"])

    def test_AS3_transcripts_show_the_cwd_isolation_defect(self) -> None:
        t = self.fx["worker_transcripts"]
        c1 = t["cycle_1_correct_worktree"]["cwds"]
        c2 = t["cycle_2_primary_checkout_defect"]["cwds"]
        self.assertTrue(any("wt-m0t107" in c for c in c1))
        self.assertTrue(all("wt-m0t107" not in c for c in c2))
        self.assertTrue(any(c.rstrip("\\").endswith("ctl24") for c in c2))

    def test_AS8_cycle2_transcript_has_no_terminal_result_record(self) -> None:
        # R343/R344: the CLI exited rc=1 with NO result record in the transcript.
        c2 = self.fx["worker_transcripts"]["cycle_2_primary_checkout_defect"]
        self.assertFalse(c2["has_result_record"])

    def test_AS8_recovered_terminal_event_is_max_turns_not_a_provider_rejection(self) -> None:
        # R343/R344 honesty: the ACTUAL terminal event recovered from the primary
        # transcript is `max_turns_reached` (maxTurns 12, turnCount 13) - the worker
        # exhausted its turn budget re-orienting in the primary checkout before it
        # could checkpoint. This CONTRADICTS the earlier "probable provider
        # context-limit rejection" inference: that hypothesis is NOT what the
        # primary evidence shows and remains unproven.
        c2 = self.fx["worker_transcripts"]["cycle_2_primary_checkout_defect"]
        term = c2["recovered_terminal_event"]
        self.assertIsNotNone(term)
        self.assertEqual(term["kind"], "max_turns_reached")
        self.assertEqual(term["maxTurns"], 12)
        self.assertEqual(term["turnCount"], 13)
        # the wrong-cwd mechanism is corroborated: the worker loaded the primary
        # checkout's own .claude rules (a nested_memory attachment), never the
        # isolated worktree's.
        self.assertIn("nested_memory", c2["attachment_subtypes"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
