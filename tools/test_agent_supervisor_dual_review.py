#!/usr/bin/env python3
"""Dual-review conductor tests (owner directive D-091 TW2, M0-T172).

Stdlib `unittest` only (thin-client / CI / windows-latest safe). There is NO live
provider, NO network, and NO codex or claude process: the two reviewers are fake
CALLABLES, the combiner is the REAL `review_combiner.ReviewCombiner` driven by a fake
in-process model runner, and the slots are the REAL `review_slots.ReviewSlots` on a
temp directory. One test class per acceptance scenario:

  Scenario 1  default off -> the loop is byte-identical with/without the injection
  Scenario 2  enabled -> both reviewers run on the SAME frozen packet, neither sees
              the other, and the loop gets the combined (worst-of-two) verdict
  Scenario 3  a reviewer that raises / times out / returns malformed output ->
              combined FAIL/UNVERIFIED, NEVER PASS
  Scenario 4  a model not in its allowlist, or an unset combining model -> refused
              before any process (fail closed)
  Scenario 5  slots -> no slot available => wait or refuse; never a third concurrent
              review; a reserved slot is always released
  Scenario 6  disputed findings are surfaced in the loop's report for the human gate;
              the loop never records a gate (ADR-005)

The "never PASS" scenarios (3, 4, 5) each compute what a NAIVE conductor would return
and assert the real conductor differs, naming the catching assertion in the message.
"""
from __future__ import annotations

import contextlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import dual_review as dr  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewOutcome  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.evidence import CollectionResult  # noqa: E402
from tools.agent_supervisor.models import digest_of  # noqa: E402
from tools.agent_supervisor.process import ProcessResult  # noqa: E402
from tools.agent_supervisor.review_combiner import (  # noqa: E402
    FAIL,
    PASS,
    UNVERIFIED,
    ReviewCombiner,
    ReviewCombinerConfig,
)
from tools.agent_supervisor.review_slots import ReviewSlots  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

# The loop fixtures are reused verbatim so the byte-identical test drives the REAL
# loop against the SAME fakes the loop's own suite uses.
from tools.test_agent_supervisor_loop import (  # noqa: E402
    HEAD_SHA,
    FakeReviewer,
    FakeRunner,
    decision,
    outcome,
    run_result,
)

HEAD = HEAD_SHA  # "b" * 40, the head the loop fixtures pin


# --------------------------------------------------------------------------
# Fakes (reviewer callables + the combining-model runner; no process, no network)
# --------------------------------------------------------------------------


class _Resolution:
    """What a real CodexReviewer.resolve() returns, minimally: model + usability."""

    def __init__(self, model: str = "codex-r", usable: bool = True, reason: str = "") -> None:
        self.model = model
        self.usable = usable
        self.reason = reason


class FakeCodexReviewer:
    """A Codex reviewer callable: scripted outcome, model allowlist hooks, raise mode."""

    def __init__(self, result=None, *, model: str = "codex-r", usable: bool = True,
                 raises: Exception | None = None) -> None:
        self._result = result if result is not None else outcome()
        self.model = model
        self._usable = usable
        self._raises = raises
        self.calls = 0
        self.packets: list[dict] = []

    def resolve(self, **_kwargs) -> _Resolution:
        return _Resolution(model=self.model, usable=self._usable)

    def review(self, packet, *, expected_task_id="", expected_checkpoint_id="", **_):
        self.calls += 1
        self.packets.append(dict(packet))
        if self._raises is not None:
            raise self._raises
        return self._result


class FakeClaudeReviewer:
    """A Claude reviewer callable: records the frozen head it is handed; raise mode."""

    def __init__(self, result=None, *, model: str = "claude-r",
                 raises: Exception | None = None) -> None:
        self._result = result if result is not None else outcome()
        self.model = model
        self._raises = raises
        self.calls = 0
        self.packets: list[dict] = []
        self.frozen_heads: list[str] = []

    def review(self, packet, *, frozen_head, producer_identity, expected_task_id="",
               expected_checkpoint_id="", **_):
        self.calls += 1
        self.packets.append(dict(packet))
        self.frozen_heads.append(frozen_head)
        if self._raises is not None:
            raise self._raises
        return self._result


class FakeModelRunner:
    """The combining-model process stand-in. Returns scripted stdout; records calls."""

    def __init__(self, stdout: str = "", *, timed_out: bool = False,
                 raises: Exception | None = None) -> None:
        self.stdout = stdout
        self.timed_out = timed_out
        self._raises = raises
        self.calls = 0

    def __call__(self, argv, **_kwargs) -> ProcessResult:
        self.calls += 1
        if self._raises is not None:
            raise self._raises
        return ProcessResult(argv=tuple(argv), returncode=0, stdout=self.stdout,
                             stderr="", duration_seconds=0.0, timed_out=self.timed_out)


def _packet(head: str = HEAD, diff: str = "") -> dict:
    """An evidence packet dict shaped exactly like `evidence.build_packet` output
    (`sections.git.head.value`, `sections.git.diff_content.value`)."""
    git: dict = {"head": {"value": head, "digest": digest_of(head)}}
    if diff:
        git["diff_content"] = {"value": diff, "digest": digest_of(diff)}
    return {"sections": {"git": git}}


def _failed_outcome(code: str, message: str) -> ReviewOutcome:
    """A decision-less, not-ok review (malformed / timed-out / unavailable)."""
    return ReviewOutcome(None, "fake-review-model", "sel", 1,
                         error_code=code, error_message=message)


def _is_pass(outcome_obj: ReviewOutcome) -> bool:
    """The naive 'did the loop get a PASS it may continue on' predicate: an ok,
    approving decision with no blocking finding."""
    dec = getattr(outcome_obj, "decision", None)
    return bool(getattr(outcome_obj, "ok", False) and dec is not None
                and dec.decision in ("CONTINUE", "COMPLETE") and not dec.blocking_findings)


class ConductorBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.rt = pathlib.Path(self._tmp.name).resolve()

    def combiner(self, *, enabled: bool = True, model: str = "claude-c",
                 runner: FakeModelRunner | None = None) -> ReviewCombiner:
        return ReviewCombiner(
            "claude-exe",
            config=ReviewCombinerConfig(enabled=enabled, model=model),
            combiner_identity="combiner-1", repo="",
            runner=runner if runner is not None else FakeModelRunner())

    def slots(self, runtime_dir: pathlib.Path | None = None) -> ReviewSlots:
        return ReviewSlots(runtime_dir or self.rt, global_limit=2, lane_limit=1)

    def conductor(self, codex, claude, *, combiner=None, slots=None, allowed=None,
                  lane="lane-1", **kwargs) -> dr.DualReviewConductor:
        return dr.DualReviewConductor(
            codex_reviewer=codex, claude_reviewer=claude,
            combiner=combiner if combiner is not None else self.combiner(),
            slots=slots if slots is not None else self.slots(),
            lane=lane, producer_identity="producer-1",
            allowed_models=allowed or {"codex": {"codex-r"},
                                       "claude": {"claude-r", "claude-c"}},
            codex_identity="codex-1", claude_identity="claude-1", **kwargs)


# --------------------------------------------------------------------------
# Scenario 1 — default off: the loop is byte-identical with/without the injection
# --------------------------------------------------------------------------


class _LoopEnv:
    """One fully independent loop environment (its own journal/audit/machine)."""

    def __init__(self, tmp: pathlib.Path) -> None:
        self.repo = tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.journal = DurableJournal(tmp / "journal.sqlite3").open()
        self.audit_path = tmp / "audit.jsonl"
        self.audit = AuditLog(self.audit_path, fsync=False)
        self.run_id = "run-loop"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T036",
             "allowed_paths": ["tools/agent_supervisor/**", "tools/test_agent_supervisor_*.py"],
             "forbidden_paths": [".github/**", ".claude/**"],
             "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T036-supervisor-bridge", stage="phase4",
            documented_test_commands=("python tools/test_agent_supervisor_dual_review.py",))

    def at_preflight(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")

    def close(self) -> None:
        self.journal.close()


@contextlib.contextmanager
def _frozen_clock():
    """Freeze every clock that reaches a CycleResult (ShadowPlan timestamp, owner
    touches, and the evidence packet's created_at_utc -> packet_digest) so two
    independent runs are byte-comparable."""
    const = "2026-10-02T00:00:00Z"
    with mock.patch.object(lp, "to_utc_iso", return_value=const), \
            mock.patch("tools.agent_supervisor.owner_touch.to_utc_iso", return_value=const), \
            mock.patch("tools.agent_supervisor.evidence.to_utc_iso", return_value=const):
        yield


class Scenario1DefaultOffByteIdentical(ConductorBase):
    def _run_once(self, tmp: pathlib.Path, *, pass_conductor_kwarg: bool):
        env = _LoopEnv(tmp)
        self.addCleanup(env.close)
        kwargs = dict(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T036", stage="phase4",
                                 allowed_paths=env.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=4, owner_touch_budget=2),
            journal=env.journal, audit=env.audit, machine=env.machine,
            authority=env.authority, runner=FakeRunner(run_result(), model=""),
            reviewer=FakeReviewer(outcome()), run_id=env.run_id, head_sha=HEAD_SHA)
        if pass_conductor_kwarg:
            # The injection, DISABLED: default-off means no conductor is supplied.
            kwargs["review_conductor"] = None
        loop = lp.SupervisedLoop(**kwargs)
        env.at_preflight()
        return loop.run_cycle("first unit", cycle=1)

    def test_single_cycle_is_byte_identical_with_and_without_the_injection(self) -> None:
        with _frozen_clock():
            without = self._run_once(self.rt / "a", pass_conductor_kwarg=False)
            with_none = self._run_once(self.rt / "b", pass_conductor_kwarg=True)
        self.assertEqual(without.to_dict(), with_none.to_dict())
        # And it really exercised the single-reviewer review seam (a CONTINUE that
        # shadow recorded as a would-forward), not a trivial early return.
        self.assertEqual(without.decision, "CONTINUE")
        self.assertIsNotNone(without.shadow_plan)


# --------------------------------------------------------------------------
# Scenario 2 — enabled: both reviewers run on the same frozen packet, neither sees
# the other, and the loop receives the combined (worst-of-two) verdict
# --------------------------------------------------------------------------


class Scenario2BothRunIndependentlyWorstOfTwo(ConductorBase):
    def test_both_reviewers_get_the_same_frozen_packet_and_verdict_is_worst(self) -> None:
        codex = FakeCodexReviewer(outcome(decision(decision="CONTINUE")))  # PASS
        claude = FakeClaudeReviewer(outcome(decision(
            decision="REVISE", next_claude_prompt="fix the thing",
            blocking_findings=[{"issue": "a real problem"}])))  # FAIL
        conductor = self.conductor(codex, claude)
        pkt = _packet()

        result = conductor.review(pkt, expected_task_id="M0-T036",
                                  expected_checkpoint_id="cp-1")

        # Both ran exactly once, on the SAME packet, each pinned to the frozen head.
        self.assertEqual((codex.calls, claude.calls), (1, 1))
        self.assertEqual(codex.packets[0], claude.packets[0])
        self.assertEqual(claude.frozen_heads, [HEAD])
        # Independence: neither packet was handed the other's review output.
        for seen in (codex.packets[0], claude.packets[0]):
            self.assertNotIn("codex_review", seen)
            self.assertNotIn("peer_review", seen)
        # The loop receives the worst-of-two verdict (PASS + FAIL -> FAIL), computed
        # in code by the real combiner.
        combined = result.combined_review
        self.assertEqual(combined.verdict, FAIL)
        self.assertEqual((combined.codex_verdict, combined.claude_verdict), (PASS, FAIL))
        self.assertTrue(result.ok)
        self.assertEqual(result.decision.decision, "REVISE")

    def test_both_pass_projects_the_cautious_approving_decision(self) -> None:
        codex = FakeCodexReviewer(outcome(decision(decision="COMPLETE",
                                                   evidence_refs=[{"ref": "done"}])))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        result = self.conductor(codex, claude).review(_packet())
        self.assertEqual(result.combined_review.verdict, PASS)
        self.assertTrue(result.ok)
        # CONTINUE ("keep working") is the more cautious of the two approvals.
        self.assertEqual(result.decision.decision, "CONTINUE")


# --------------------------------------------------------------------------
# Scenario 3 — a reviewer that raises / times out / returns malformed output makes
# the combined verdict FAIL/UNVERIFIED, NEVER PASS
# --------------------------------------------------------------------------


class Scenario3UntrustworthyReviewNeverPass(ConductorBase):
    def _assert_never_pass(self, codex, claude, *, naive_pass_outcome, expect_code):
        result = self.conductor(codex, claude).review(_packet())
        # NAIVE TRAP: an implementation that ignored the untrustworthy review and
        # returned the OTHER review's PASS would satisfy `_is_pass`. The combined
        # verdict must be UNVERIFIED and the outcome must NOT be a PASS.
        self.assertTrue(_is_pass(naive_pass_outcome),
                        "the naive single-review PASS is the trap this test guards")
        self.assertFalse(
            _is_pass(result),
            "NAIVE-IMPL CATCH: `assertFalse(_is_pass(result))` fails a conductor that "
            "returns the surviving review's PASS instead of failing closed")
        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, expect_code)
        self.assertEqual(result.combined_review.verdict, UNVERIFIED)

    def test_a_raised_reviewer_is_unverified_never_pass(self) -> None:
        # M0-T168 N1: a raised launch exception counts as FAIL, never an approval.
        codex = FakeCodexReviewer(raises=RuntimeError("binary missing"))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        self._assert_never_pass(
            codex, claude,
            naive_pass_outcome=outcome(decision(decision="CONTINUE")),
            expect_code="dual_review_unverified")

    def test_a_timed_out_reviewer_is_unverified_never_pass(self) -> None:
        codex = FakeCodexReviewer(_failed_outcome("review_timeout", "the reviewer timed out"))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        self._assert_never_pass(
            codex, claude,
            naive_pass_outcome=outcome(decision(decision="CONTINUE")),
            expect_code="dual_review_unverified")

    def test_a_malformed_reviewer_is_unverified_never_pass(self) -> None:
        codex = FakeCodexReviewer(_failed_outcome("empty_review_output", "no decision"))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        self._assert_never_pass(
            codex, claude,
            naive_pass_outcome=outcome(decision(decision="CONTINUE")),
            expect_code="dual_review_unverified")

    def test_a_raised_combiner_is_unverified_never_pass(self) -> None:
        # M0-T168 N1 at the combiner: a combiner that RAISES (here its independence
        # guard, because its identity collides with the producer) is caught by the
        # conductor and becomes UNVERIFIED, never a PASS.
        codex = FakeCodexReviewer(outcome(decision(decision="CONTINUE")))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        combiner = ReviewCombiner(
            "claude-exe",
            config=ReviewCombinerConfig(enabled=True, model="claude-c"),
            combiner_identity="producer-1", repo="", runner=FakeModelRunner())
        result = self.conductor(codex, claude, combiner=combiner).review(_packet())
        # Both reviews still ran (the raise is in the combine step), but the result is
        # a fail-closed UNVERIFIED outcome, not a PASS.
        self.assertEqual((codex.calls, claude.calls), (1, 1))
        self.assertFalse(_is_pass(result))
        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "combiner_raised")
        self.assertIsNone(result.combined_review)

    def test_a_raised_combining_model_is_failsafe_never_pass(self) -> None:
        # A combining MODEL launch that raises is caught INSIDE the combiner (fail-
        # safe: no dispute recorded), so the code-computed verdict stands and is never
        # weakened to PASS.
        codex = FakeCodexReviewer(outcome(decision(
            decision="CONTINUE", blocking_findings=[{"issue": "x"}])))  # FAIL, disputable
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))  # PASS
        runner = FakeModelRunner(raises=RuntimeError("model crashed"))
        result = self.conductor(codex, claude, combiner=self.combiner(runner=runner)).review(
            _packet())
        self.assertTrue(runner.calls >= 1)
        self.assertFalse(_is_pass(result))
        self.assertEqual(result.combined_review.verdict, FAIL)  # unchanged by the crash


# --------------------------------------------------------------------------
# Scenario 4 — a model not in its allowlist, or an unset combining model, is refused
# BEFORE any process starts (fail closed)
# --------------------------------------------------------------------------


class Scenario4ModelAllowlistRefusedBeforeAnyProcess(ConductorBase):
    def _assert_refused_before_process(self, conductor, codex, claude, combiner_runner,
                                       expect_code):
        result = conductor.review(_packet())
        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, expect_code)
        # NAIVE-IMPL CATCH: a conductor that defaulted/ran anyway would have called a
        # reviewer or the combining model. `assertEqual(..., 0)` fails such an impl.
        self.assertEqual(codex.calls, 0, "no Codex review may start on a refusal")
        self.assertEqual(claude.calls, 0, "no Claude review may start on a refusal")
        self.assertEqual(combiner_runner.calls, 0, "no combining model may start")
        # And no slot was consumed (nothing was reserved).
        self.assertEqual(len(self.slots().active()), 0)

    def test_unset_combining_model_refuses_fail_closed(self) -> None:
        codex, claude = FakeCodexReviewer(), FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude,
                                   combiner=self.combiner(model="", runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "combiner_model_unset")

    def test_combining_model_not_in_allowlist_refuses(self) -> None:
        codex, claude = FakeCodexReviewer(), FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude,
                                   combiner=self.combiner(model="claude-x", runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "combiner_model_not_allowlisted")

    def test_claude_reviewer_model_not_in_allowlist_refuses(self) -> None:
        codex = FakeCodexReviewer()
        claude = FakeClaudeReviewer(model="claude-x")
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude, combiner=self.combiner(runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "claude_reviewer_model_not_allowlisted")

    def test_codex_reviewer_model_not_in_allowlist_refuses(self) -> None:
        codex = FakeCodexReviewer(model="codex-x")
        claude = FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude, combiner=self.combiner(runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "codex_reviewer_model_not_allowlisted")

    def test_combiner_default_off_refuses(self) -> None:
        codex, claude = FakeCodexReviewer(), FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(
            codex, claude, combiner=self.combiner(enabled=False, runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "combiner_disabled")


# --------------------------------------------------------------------------
# Scenario 5 — slots: no slot available => wait or refuse; never a third concurrent
# review; a reserved slot is always released
# --------------------------------------------------------------------------


class Scenario5SlotsNeverThirdConcurrentReview(ConductorBase):
    def test_a_full_box_refuses_before_running_a_third_review(self) -> None:
        # Fill both global review-or-combine slots from this live process.
        filler = self.slots()
        g1 = filler.try_reserve("busy-lane-1")
        g2 = filler.try_reserve("busy-lane-2")
        self.addCleanup(lambda: filler.release(g1.reservation))
        self.addCleanup(lambda: filler.release(g2.reservation))
        self.assertTrue(g1.admitted and g2.admitted)
        self.assertEqual(len(self.slots().active()), 2)

        codex, claude = FakeCodexReviewer(), FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude, combiner=self.combiner(runner=runner),
                                   lane="lane-3", slot_wait_seconds=0.0)
        result = conductor.review(_packet())

        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, "review_slot_unavailable")
        # NAIVE-IMPL CATCH: a conductor that skipped the TW1 reservation would have
        # run the reviewers -> calls > 0, and could have taken a THIRD slot.
        self.assertEqual(codex.calls, 0, "no review runs when the box is full")
        self.assertEqual(claude.calls, 0)
        self.assertEqual(runner.calls, 0)
        self.assertEqual(len(self.slots().active()), 2,
                         "the box still holds exactly two reservations; never a third")

    def test_a_reserved_slot_is_released_after_the_review(self) -> None:
        codex = FakeCodexReviewer(outcome(decision(decision="CONTINUE")))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        slots = self.slots()
        result = self.conductor(codex, claude, slots=slots).review(_packet())
        self.assertTrue(result.ok)
        self.assertEqual(len(slots.active()), 0,
                         "the conductor releases its slot when the review finishes")


# --------------------------------------------------------------------------
# Scenario 6 — disputed findings surfaced in the loop's report for the human gate;
# the loop never records a gate (ADR-005)
# --------------------------------------------------------------------------

# A unified diff whose only new-side line is file.py:5, so a file_line dispute citing
# the finding's own location (file.py:5) is both finding-bound and present-in-diff.
_DIFF = "--- a/file.py\n+++ b/file.py\n@@ -4,0 +5,1 @@\n+db.execute(user_sql)\n"
_DISPUTE_STDOUT = json.dumps({"disputes": [{
    "finding_id": "codex:blocking:0",
    "evidence": {"type": "file_line", "file": "file.py", "line": 5},
    "rationale": "the call is parameterized elsewhere"}]})


class Scenario6DisputesSurfacedNoGate(ConductorBase):
    def test_a_recorded_dispute_is_surfaced_and_the_finding_still_stands(self) -> None:
        codex = FakeCodexReviewer(outcome(decision(
            decision="CONTINUE",
            blocking_findings=[{"file": "file.py", "line": 5, "issue": "SQLi"}])))  # FAIL
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))  # PASS
        runner = FakeModelRunner(_DISPUTE_STDOUT)
        conductor = self.conductor(codex, claude, combiner=self.combiner(runner=runner))

        result = conductor.review(_packet(diff=_DIFF))

        combined = result.combined_review
        self.assertEqual(combined.verdict, FAIL)  # verdict unchanged by the dispute
        self.assertEqual(combined.disputes_recorded, 1)
        disputed = combined.disputed_findings
        self.assertEqual([f.finding_id for f in disputed], ["codex:blocking:0"])
        # Surfaced for the human gate via the outcome's notify_events (the loop's
        # report channel) AND the attached combined review.
        self.assertIn("dual_review:disputed_finding=codex:blocking:0", result.notify_events)
        self.assertIn("dual_review:verdict=FAIL", result.notify_events)
        # The disputed finding REMAINS on the projected decision (advisory only).
        blocking = result.decision.blocking_findings
        self.assertTrue(any(b.get("disputed") for b in blocking),
                        "the dispute annotates the finding; it is never removed")
        self.assertEqual(result.decision.decision, "REVISE")

    def test_loop_surfaces_the_combined_verdict_and_records_no_gate(self) -> None:
        env = _LoopEnv(self.rt / "loopenv")
        self.addCleanup(env.close)
        codex = FakeCodexReviewer(outcome(decision(decision="CONTINUE")))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")))
        conductor = self.conductor(codex, claude)
        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T036", stage="phase4",
                                 allowed_paths=env.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",), max_cycles=4),
            journal=env.journal, audit=env.audit, machine=env.machine,
            authority=env.authority, runner=FakeRunner(run_result(), model=""),
            reviewer=FakeReviewer(outcome()), review_conductor=conductor,
            run_id=env.run_id, head_sha=HEAD_SHA,
            collector=_HeadCollector(HEAD_SHA))
        env.at_preflight()
        result = loop.run_cycle("first unit", cycle=1)

        # The conductor really ran (its reviewers were invoked through the loop seam).
        self.assertEqual((codex.calls, claude.calls), (1, 1))
        # The combined-verdict surfacing reached the loop's cycle report.
        self.assertIn("dual_review:verdict=PASS", result.notify_events)
        self.assertIn("dual_review:verdict=PASS", result.to_dict()["notify_events"])
        # ADR-005: the loop recorded NO gate. The audit log carries no gate event.
        events = [json.loads(line)["event_type"]
                  for line in env.audit_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
        self.assertTrue(events, "the cycle produced audit events")
        self.assertFalse([e for e in events if "gate" in e.lower()],
                         "the loop never records a gate (ADR-005)")


# --------------------------------------------------------------------------
# Scenario 7 (DB-103 / D-091-R001,R007) — the combining model MUST differ from the
# Claude reviewer model: equal models, or either empty, are refused before any
# process (no slot reserved); two different allowlisted models proceed unchanged.
# --------------------------------------------------------------------------


class Scenario7CombinerDiffersFromClaudeReviewer(ConductorBase):
    def _assert_refused_before_process(self, conductor, codex, claude, runner,
                                       expect_code):
        result = conductor.review(_packet())
        self.assertFalse(result.ok)
        self.assertEqual(result.error_code, expect_code)
        # NAIVE-IMPL CATCH: a conductor that combined equal models anyway would have
        # called a reviewer or the combining model. `assertEqual(..., 0)` fails it.
        self.assertEqual(codex.calls, 0, "no Codex review may start on a refusal")
        self.assertEqual(claude.calls, 0, "no Claude review may start on a refusal")
        self.assertEqual(runner.calls, 0, "no combining model may start")
        # And no slot was reserved (the refusal is before `_acquire_slot`).
        self.assertEqual(len(self.slots().active()), 0,
                         "no review-or-combine slot may be reserved on a refusal")

    def test_equal_combiner_and_claude_models_refused_before_any_process(self) -> None:
        # Both models are 'claude-r' (both ON the claude allowlist, so neither the
        # combiner nor the reviewer allowlist check fires first): the distinctness
        # guard is what refuses — before any slot or process.
        codex = FakeCodexReviewer()
        claude = FakeClaudeReviewer(model="claude-r")
        runner = FakeModelRunner()
        conductor = self.conductor(
            codex, claude, combiner=self.combiner(model="claude-r", runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "review_models_not_distinct")

    def test_empty_combining_model_refused_before_any_process(self) -> None:
        # DB-103 'either empty' — combiner side (caught at `combiner_model_unset`).
        codex, claude = FakeCodexReviewer(), FakeClaudeReviewer()
        runner = FakeModelRunner()
        conductor = self.conductor(
            codex, claude, combiner=self.combiner(model="", runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "combiner_model_unset")

    def test_empty_claude_reviewer_model_refused_before_any_process(self) -> None:
        # DB-103 'either empty' — reviewer side (caught at `claude_reviewer_model_unset`).
        codex = FakeCodexReviewer()
        claude = FakeClaudeReviewer(model="")
        runner = FakeModelRunner()
        conductor = self.conductor(codex, claude, combiner=self.combiner(runner=runner))
        self._assert_refused_before_process(conductor, codex, claude, runner,
                                            "claude_reviewer_model_unset")

    def test_different_allowlisted_models_proceed_unchanged(self) -> None:
        # combiner 'claude-c' != reviewer 'claude-r', both on the claude allowlist:
        # the distinctness guard lets them through and both reviews run as before.
        codex = FakeCodexReviewer(outcome(decision(decision="CONTINUE")))
        claude = FakeClaudeReviewer(outcome(decision(decision="CONTINUE")),
                                    model="claude-r")
        runner = FakeModelRunner()
        result = self.conductor(
            codex, claude, combiner=self.combiner(runner=runner)).review(_packet())
        self.assertTrue(result.ok)
        self.assertEqual((codex.calls, claude.calls), (1, 1),
                         "different allowlisted models proceed: both reviews run")
        self.assertEqual(result.combined_review.verdict, PASS)
        self.assertEqual(result.decision.decision, "CONTINUE")


class _HeadCollector:
    """A minimal evidence collector that yields a git section with a frozen head
    (and an optional diff) so the loop's real packet carries a 40-char head."""

    def __init__(self, head: str, diff: str = "") -> None:
        self._head = head
        self._diff = diff

    def collect_git_facts(self):
        facts = {"head": CollectionResult(name="head", ok=True, value=self._head,
                                          digest=digest_of(self._head))}
        if self._diff:
            facts["diff_content"] = CollectionResult(
                name="diff_content", ok=True, value=self._diff, digest=digest_of(self._diff))
        return facts

    def collect_project_control(self):
        return {}

    def collect_completeness(self, task_id, git_facts, commands):
        return None, {}


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
