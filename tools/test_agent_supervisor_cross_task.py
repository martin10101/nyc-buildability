#!/usr/bin/env python3
"""Removal-sensitive LIVE-path tests for the Stage-3 cross-task wiring.

D-024 Amendment 25 (D-024-R400..R405). The exactly-once advancement + ordered
selection primitives were simulation-proven at M0-T126 but had ZERO production
callers (M0-T127 s7.4). This suite exercises the NEW live driver
``next_task.run_task_queue`` - the one that wires those primitives into the
limited-auto path behind the EXISTING bounded-mode owner gate - across the ten
removal-sensitive families the owner named (R404):

  1. live-path cross-task selection through the REAL loop with a fake runner
     (not the sim harness): a two-packet journey where the first task completes
     and the second is selected and dispatched;
  2. eligibility - every ineligible category is SKIPPED with an audited reason;
  3. dependency ordering - an unaccepted dependency is ineligible until accepted;
  4. isolated-worktree binding - a successor whose bound worktree does not match
     its packet refuses (an exit path, never silent);
  5. checkpoint + Codex-review completion required before ANY advancement;
  6. duplicate advancement refused (a task advances once across re-decisions and
     genuine restarts);
  7. crash BEFORE advancement (no advance) and AFTER advancement / BEFORE the
     next dispatch (resume selects correctly, no double-advance) - genuine
     journal reopen, not an in-process exception;
  8. stale campaign state - a packet changed between queueing and selection is
     refused;
  9. no eligible work lands NO_ELIGIBLE_WORK visibly;
 10. stop/pause/emergency/graceful intents between tasks stop before the next
     dispatch.

Every "Claude" and every "Codex" is an in-process fake; every runtime is a temp
directory (R401: the live journal and preserved evidence are never touched).
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import inspect
import json
import os
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import next_task as nt  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor import stop_intent  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.claude_runner import RunnerConfig, RunResult  # noqa: E402
from tools.agent_supervisor.codex_reviewer import (  # noqa: E402
    ReviewOutcome,
    map_decision_to_tier,
)
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import (  # noqa: E402
    ClaudeCheckpoint,
    CodexDecision,
    digest_of,
)
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

_FAKE_LAUNCH_CONFIG = RunnerConfig(executable="fake-claude")


# --------------------------------------------------------------------------
# In-process fakes (same shape as tools/test_agent_supervisor_loop.py)
# --------------------------------------------------------------------------


def _checkpoint(task_id: str, worktree: str, branch: str) -> ClaudeCheckpoint:
    return ClaudeCheckpoint(
        schema_version="1.0.0", run_id="run-xtask", checkpoint_id=f"cp-{task_id}",
        task_id=task_id, claude_session_id="sess-1", status="UNIT_COMPLETE",
        summary="unit complete", starting_sha="a" * 40, current_sha="b" * 40,
        branch=branch, worktree=worktree, proposed_next_action="done",
        usage="unknown", context_pressure="unknown")


def _complete_decision(task_id: str) -> CodexDecision:
    return CodexDecision(
        schema_version="1.0.0", decision="COMPLETE", reviewed_task_id=task_id,
        reviewed_checkpoint_id=f"cp-{task_id}", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="", evidence_refs=[{"path": "report.md"}])


class _FakeRunner:
    def __init__(self, result: RunResult) -> None:
        self.result = result
        self.config = dataclasses.replace(_FAKE_LAUNCH_CONFIG, model="", expected_model="")

    def run_unit(self, prompt: str, **_kwargs) -> RunResult:
        return self.result


class _FakeReviewer:
    def __init__(self, out: ReviewOutcome) -> None:
        self.out = out

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        return self.out


def _review_outcome(dec: CodexDecision) -> ReviewOutcome:
    return ReviewOutcome(
        decision=dec, model_used="fake-review-model", selection_digest="sel",
        attempts=1, decision_digest=digest_of(dec.to_dict()),
        tier=map_decision_to_tier(dec))


class _LoopRunner:
    """A fake ClaudeRunner for the REAL cli._run_loop wrapper (families that drive
    _run_loop / the real cli.py:3069 dispatch line). It adds the
    ``executable_identity()`` the wrapper calls before assembling the worker
    actuation channel, and returns a COMPLETE result for the task bound to its
    launch cwd (the worktree). The task id is resolved from the runner config's
    ``cwd`` so one factory serves every task in the journey."""

    def __init__(self, config: RunnerConfig, task_id: str, branch: str) -> None:
        self.config = config
        cp = _checkpoint(task_id, str(config.cwd), branch)
        self.result = RunResult(argv=("fake",), returncode=0, duration_seconds=0.1,
                                session_id="sess-1", checkpoint=cp,
                                containment="job_object")

    def run_unit(self, prompt: str, **_kwargs) -> RunResult:
        return self.result

    def executable_identity(self) -> dict:
        return {"digest": ""}


class _LoopReviewer:
    """A fake CodexReviewer that returns a COMPLETE decision for the task bound to
    its ``repo`` (the worktree)."""

    def __init__(self, task_id: str) -> None:
        self.out = _review_outcome(_complete_decision(task_id))

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        return self.out


# --------------------------------------------------------------------------
# Base harness
# --------------------------------------------------------------------------


class CrossTaskBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._handles: list[DurableJournal] = []
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self._close_all)
        self.root = pathlib.Path(self._tmp.name).resolve()
        self.tasks_dir = self.root / "project-control" / "tasks"
        self.tasks_dir.mkdir(parents=True)
        # The PRIMARY control checkout - a worker must never run here.
        self.checkout = self.root / "ctl24"
        self.checkout.mkdir()
        self.db = self.root / "journal.sqlite3"
        self.journal = self._track(DurableJournal(self.db).open())
        self.audit = AuditLog(self.root / "audit.jsonl", fsync=False)
        self.dispatched: list[str] = []

    def _track(self, journal: DurableJournal) -> DurableJournal:
        self._handles.append(journal)
        return journal

    def _close_all(self) -> None:
        for journal in self._handles:
            try:
                journal.close()
            except Exception:
                pass

    def reopen(self) -> DurableJournal:
        """Genuine crash/restart: close every handle, re-open the same file."""
        self._close_all()
        self._handles.clear()
        self.journal = self._track(DurableJournal(self.db).open())
        return self.journal

    def make_worktree(self, name: str) -> pathlib.Path:
        wt = self.root / name
        (wt / "tools").mkdir(parents=True, exist_ok=True)
        return wt

    def write_packet(self, task_id: str, *, status: str = "claimed",
                     dependencies=(), blockers=(), worktree_name: str | None = None,
                     **extra) -> pathlib.Path:
        packet = {
            "task_id": task_id, "status": status,
            "dependencies": list(dependencies), "blockers": list(blockers),
            "worktree": worktree_name or f"wt-{task_id.lower()}",
            "allowed_paths": ["tools/agent_supervisor/**",
                              "tools/test_agent_supervisor_*.py"],
            "forbidden_paths": [".github/**", ".claude/**"],
        }
        packet.update(extra)
        path = self.tasks_dir / f"{task_id}.json"
        path.write_text(json.dumps(packet, indent=1), encoding="utf-8")
        return path

    def entry(self, task_id: str, *, worktree_name: str | None = None,
              worktree: pathlib.Path | None = None,
              branch: str = "task/branch") -> nt.TaskQueueEntry:
        wt_name = worktree_name or f"wt-{task_id.lower()}"
        wt = worktree if worktree is not None else self.make_worktree(wt_name)
        return nt.TaskQueueEntry(
            task_id=task_id, packet_path=str(self.tasks_dir / f"{task_id}.json"),
            worktree=str(wt), branch=branch, repo=str(wt))

    def write_queue(self, entries: list[nt.TaskQueueEntry]) -> pathlib.Path:
        doc = {"tasks": [dataclasses.asdict(e) for e in entries]}
        path = self.root / "queue.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    def make_args(self, first_entry: nt.TaskQueueEntry, *, max_tasks: int,
                  packet_queue: pathlib.Path | None = None,
                  mode: str = "limited-auto") -> argparse.Namespace:
        return argparse.Namespace(
            task_packet=first_entry.packet_path, worktree=first_entry.worktree,
            branch=first_entry.branch, repo=first_entry.repo, mode=mode,
            run_id="run-xtask", max_tasks=max_tasks,
            packet_queue=str(packet_queue) if packet_queue else None)

    def audit_events(self) -> list[str]:
        text = (self.root / "audit.jsonl").read_text(encoding="utf-8")
        return [json.loads(line)["event_type"]
                for line in text.splitlines() if line.strip()]

    # -- run_one variants ---------------------------------------------------

    def real_run_one(self, args, checkout, journal, audit) -> dict:
        """Dispatch ONE task through the REAL SupervisedLoop with a fake provider.

        Mirrors cli._run_loop's state sequence exactly: close a resting COMPLETE
        run to IDLE via the existing run_closed edge, fire start_command
        IDLE->PREFLIGHT, then build and run the real loop. The provider (runner +
        reviewer) is the only fake - the state machine, journal, checkpoint
        handling, Codex-decision routing, COMPLETE transition, and LoopRun are all
        real. This is the "real loop path with a fake runner" the packet asks for.
        """
        packet = json.loads(pathlib.Path(args.task_packet).read_text(encoding="utf-8-sig"))
        task_id = str(packet["task_id"])
        self.dispatched.append(task_id)
        machine = StateMachine(journal, audit, "run-xtask")
        plan = nt.plan_close_run(machine.current_state)
        if plan.should_close:
            machine.transition(plan.to_state, plan.trigger,
                               detail={"operator_initiated": True})
        if machine.current_state == sm.IDLE:
            machine.transition(sm.PREFLIGHT, "start_command",
                               detail={"operator_initiated": True})
        authority = pol.TaskAuthority.from_packet(
            packet, repo_root=str(args.repo or args.worktree),
            worktree=str(args.worktree), branch=str(args.branch or "task/branch"),
            stage="phase4", documented_test_commands=())
        config = lp.LoopConfig(
            mode="supervised", task_id=task_id, stage="phase4",
            allowed_paths=authority.allowed_paths, stop_conditions=(),
            max_cycles=1, owner_touch_budget=8)
        cp = _checkpoint(task_id, str(args.worktree), authority.branch)
        result = RunResult(argv=("fake",), returncode=0, duration_seconds=0.1,
                           session_id="sess-1", checkpoint=cp, containment="job_object")
        loop = lp.SupervisedLoop(
            config=config, journal=journal, audit=audit, machine=machine,
            authority=authority, runner=_FakeRunner(result),
            reviewer=_FakeReviewer(_review_outcome(_complete_decision(task_id))),
            run_id="run-xtask", approval_gate=lambda _d, _p: True)
        return loop.run("do the authorized unit").to_dict()

    def scripted_run_one(self, script: dict[str, str], *, on_dispatch=None):
        """A controllable run_one for driver-decision families.

        ``script`` maps task_id -> "complete" | "incomplete". Returns a canned run
        dict (no real loop) so a test can control completion precisely. Records
        each dispatched task_id and optionally fires ``on_dispatch(task_id)`` to
        model a concurrent change (family 8).
        """
        def _run_one(args, checkout, journal, audit) -> dict:
            packet = json.loads(
                pathlib.Path(args.task_packet).read_text(encoding="utf-8-sig"))
            task_id = str(packet["task_id"])
            self.dispatched.append(task_id)
            if on_dispatch is not None:
                on_dispatch(task_id)
            kind = script.get(task_id, "complete")
            if kind == "complete":
                return {"run_id": "run-xtask", "mode": args.mode,
                        "final_state": sm.COMPLETE, "stopped": "stage_complete",
                        "cycles": [{"decision": "COMPLETE",
                                    "checkpoint_id": f"cp-{task_id}"}],
                        "provider_calls": 1, "run_budget": None,
                        "budget": {"counted": 0, "budget": 8, "within_budget": True},
                        "forwarded_message_ids": [], "rotations": [],
                        "limited_auto_enabled": True}
            return {"run_id": "run-xtask", "mode": args.mode,
                    "final_state": sm.PAUSED_RECOVERY, "stopped": "budget_exhausted",
                    "cycles": [{"decision": "", "checkpoint_id": ""}],
                    "provider_calls": 1, "run_budget": {"exhausted": True},
                    "budget": {"counted": 0, "budget": 8, "within_budget": False},
                    "forwarded_message_ids": [], "rotations": [],
                    "limited_auto_enabled": True}
        return _run_one


# --------------------------------------------------------------------------
# Family 1 - live cross-task selection through the REAL loop
# --------------------------------------------------------------------------


class LiveCrossTaskSelectionTests(CrossTaskBase):
    def test_two_task_journey_completes_and_advances_each_exactly_once(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        e_b = self.entry("M0-TB")
        queue = self.write_queue([e_b])
        args = self.make_args(e_a, max_tasks=2, packet_queue=queue)

        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.real_run_one)

        # Both tasks ran through the real loop, in order, no owner touch between.
        self.assertEqual(self.dispatched, ["M0-TA", "M0-TB"])
        # Each advanced exactly once, over the real durable CAS.
        self.assertTrue(nt.is_advanced(self.journal, "M0-TA"))
        self.assertTrue(nt.is_advanced(self.journal, "M0-TB"))
        tq = run["task_queue"]
        self.assertEqual(tq["advanced"], ["M0-TA", "M0-TB"])
        self.assertEqual(tq["dispatched"], 2)
        self.assertEqual(tq["stop_reason"], "queue_exhausted")
        # The last run really reached COMPLETE through the loop.
        self.assertEqual(run["final_state"], sm.COMPLETE)
        self.assertIn("cross_task_dispatch", self.audit_events())
        self.assertIn("cross_task_advancement", self.audit_events())

    def test_max_tasks_bound_stops_before_the_second_dispatch(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        queue = self.write_queue([self.entry("M0-TB")])
        # max_tasks 1 but a queue is present: the bound wins, B never dispatches.
        args = self.make_args(e_a, max_tasks=1, packet_queue=queue)
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.real_run_one)
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertFalse(nt.is_advanced(self.journal, "M0-TB"))
        self.assertEqual(run["task_queue"]["stop_reason"], "max_tasks_reached")


# --------------------------------------------------------------------------
# Family 2 - eligibility categories are SKIPPED with an audited reason
# --------------------------------------------------------------------------


class EligibilitySkipTests(CrossTaskBase):
    def _run_with_successor(self, successor: nt.TaskQueueEntry):
        self.write_packet("M0-TA")
        e_a = self.entry("M0-TA")
        queue = self.write_queue([successor])
        args = self.make_args(e_a, max_tasks=3, packet_queue=queue)
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        return run["task_queue"]

    def _skip_code(self, tq, task_id: str) -> str:
        for step in tq["steps"]:
            if step["task_id"] == task_id and step["outcome"] == "skipped":
                return step["detail"].split(":", 1)[0]
        self.fail(f"{task_id} was not recorded as skipped: {tq['steps']}")

    def test_owner_gated_via_blockers_is_skipped(self) -> None:
        self.write_packet("M0-TB", blockers=["needs owner decision"])
        tq = self._run_with_successor(self.entry("M0-TB"))
        self.assertEqual(self._skip_code(tq, "M0-TB"), "blocked")
        self.assertIn("cross_task_candidate_skipped", self.audit_events())

    def test_owner_gate_field_is_skipped(self) -> None:
        self.write_packet("M0-TB", owner_hold=True)
        tq = self._run_with_successor(self.entry("M0-TB"))
        self.assertEqual(self._skip_code(tq, "M0-TB"), "owner_gated")

    def test_wrong_status_is_skipped(self) -> None:
        self.write_packet("M0-TB", status="backlog")
        tq = self._run_with_successor(self.entry("M0-TB"))
        self.assertEqual(self._skip_code(tq, "M0-TB"), "ineligible_status")

    def test_accepted_status_is_not_re_run(self) -> None:
        # A task already accepted is not "claimed for this run" and is refused.
        self.write_packet("M0-TB", status="accepted")
        tq = self._run_with_successor(self.entry("M0-TB"))
        self.assertEqual(self._skip_code(tq, "M0-TB"), "ineligible_status")

    def test_missing_worktree_is_skipped(self) -> None:
        self.write_packet("M0-TB")
        missing = self.root / "does-not-exist"
        e_b = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                str(missing), "task/b", str(missing))
        tq = self._run_with_successor(e_b)
        self.assertEqual(self._skip_code(tq, "M0-TB"), "worktree_missing")

    def test_primary_checkout_worktree_is_skipped(self) -> None:
        self.write_packet("M0-TB")
        e_b = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                str(self.checkout), "task/b", str(self.checkout))
        tq = self._run_with_successor(e_b)
        self.assertEqual(self._skip_code(tq, "M0-TB"), "worktree_primary_checkout")

    def test_unparseable_packet_is_skipped(self) -> None:
        (self.tasks_dir / "M0-TB.json").write_text("{ not json", encoding="utf-8")
        wt = self.make_worktree("wt-m0-tb")
        e_b = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                str(wt), "task/b", str(wt))
        tq = self._run_with_successor(e_b)
        self.assertEqual(self._skip_code(tq, "M0-TB"), "packet_unparseable")

    def test_task_id_mismatch_is_skipped(self) -> None:
        # The packet on disk declares a DIFFERENT id than the queue entry names.
        self.write_packet("M0-TZ")  # file M0-TZ.json declares task_id M0-TZ
        wt = self.make_worktree("wt-m0-tb")
        e_b = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TZ.json"),
                                str(wt), "task/b", str(wt))
        tq = self._run_with_successor(e_b)
        self.assertEqual(self._skip_code(tq, "M0-TB"), "task_id_mismatch")

    def test_an_eligible_successor_after_skips_is_dispatched(self) -> None:
        # Ineligible ones are skipped (never silently), a later ELIGIBLE one runs.
        self.write_packet("M0-TA")
        self.write_packet("M0-TB", status="backlog")   # ineligible
        self.write_packet("M0-TC")                       # eligible
        e_a = self.entry("M0-TA")
        queue = self.write_queue([self.entry("M0-TB"), self.entry("M0-TC")])
        args = self.make_args(e_a, max_tasks=3, packet_queue=queue)
        nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                          self.scripted_run_one({}))
        self.assertEqual(self.dispatched, ["M0-TA", "M0-TC"])
        self.assertTrue(nt.is_advanced(self.journal, "M0-TC"))
        self.assertFalse(nt.is_advanced(self.journal, "M0-TB"))


# --------------------------------------------------------------------------
# Family 3 - dependency ordering
# --------------------------------------------------------------------------


class DependencyOrderingTests(CrossTaskBase):
    def _select(self, dep_status: str) -> nt.EligibilityVerdict:
        self.write_packet("M0-DEP", status=dep_status)
        self.write_packet("M0-TB", dependencies=["M0-DEP"])
        entry = self.entry("M0-TB")
        digest = nt.packet_digest(entry.packet_path)
        return nt.evaluate_eligibility(entry, queued_digest=digest,
                                       primary_checkout=str(self.checkout))

    def test_unaccepted_dependency_is_ineligible(self) -> None:
        verdict = self._select("claimed")
        self.assertFalse(verdict.eligible)
        self.assertEqual(verdict.code, "dependency_unaccepted")

    def test_accepted_dependency_is_eligible(self) -> None:
        verdict = self._select("accepted")
        self.assertTrue(verdict.eligible)

    def test_missing_dependency_packet_is_ineligible(self) -> None:
        self.write_packet("M0-TB", dependencies=["M0-GONE"])
        entry = self.entry("M0-TB")
        digest = nt.packet_digest(entry.packet_path)
        verdict = nt.evaluate_eligibility(entry, queued_digest=digest,
                                          primary_checkout=str(self.checkout))
        self.assertFalse(verdict.eligible)
        self.assertEqual(verdict.code, "dependency_unresolved")


# --------------------------------------------------------------------------
# Family 4 - isolated-worktree binding refuses (exit path, not silent)
# --------------------------------------------------------------------------


class WorktreeBindingTests(CrossTaskBase):
    def test_worktree_not_matching_packet_declaration_refuses(self) -> None:
        # The packet declares wt-m0-tb; the bound worktree basename is different.
        self.write_packet("M0-TB", worktree_name="wt-m0-tb")
        wrong = self.make_worktree("wt-somewhere-else")
        entry = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                  str(wrong), "task/b", str(wrong))
        digest = nt.packet_digest(entry.packet_path)
        verdict = nt.evaluate_eligibility(entry, queued_digest=digest,
                                          primary_checkout=str(self.checkout))
        self.assertFalse(verdict.eligible)
        self.assertTrue(verdict.code.startswith("binding_"))

    def test_binding_refusal_in_the_driver_is_a_visible_skip(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB", worktree_name="wt-m0-tb")
        wrong = self.make_worktree("wt-not-b")
        e_b = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                str(wrong), "task/b", str(wrong))
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=3, packet_queue=self.write_queue([e_b]))
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        self.assertNotIn("M0-TB", self.dispatched)
        skips = [s for s in run["task_queue"]["steps"]
                 if s["task_id"] == "M0-TB" and s["outcome"] == "skipped"]
        self.assertTrue(skips and skips[0]["detail"].startswith("binding_"))


# --------------------------------------------------------------------------
# Family 5 - checkpoint + Codex-review completion required before advancement
# --------------------------------------------------------------------------


class CompletionRequiredTests(CrossTaskBase):
    def test_a_run_that_did_not_complete_never_advances(self) -> None:
        self.write_packet("M0-TA")
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=3,
                              packet_queue=self.write_queue([self.entry("M0-TB")]))
        self.write_packet("M0-TB")
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({"M0-TA": "incomplete"}))
        self.assertFalse(nt.is_advanced(self.journal, "M0-TA"))
        self.assertNotIn("M0-TB", self.dispatched)  # never selected past a non-complete
        self.assertTrue(run["task_queue"]["stop_reason"].startswith("task_not_completed"))

    def test_run_reached_complete_requires_a_reviewed_checkpoint_id(self) -> None:
        no_ckpt = {"final_state": sm.COMPLETE, "stopped": "stage_complete",
                   "cycles": [{"decision": "COMPLETE", "checkpoint_id": ""}]}
        complete, cid, _ = nt.run_reached_complete(no_ckpt)
        self.assertFalse(complete)
        self.assertEqual(cid, "")

    def test_run_reached_complete_requires_the_complete_decision(self) -> None:
        wrong_decision = {"final_state": sm.COMPLETE, "stopped": "stage_complete",
                          "cycles": [{"decision": "CONTINUE", "checkpoint_id": "cp"}]}
        self.assertFalse(nt.run_reached_complete(wrong_decision)[0])

    def test_run_reached_complete_requires_the_complete_state(self) -> None:
        not_complete = {"final_state": "PREFLIGHT", "stopped": "max_cycles_reached",
                        "cycles": [{"decision": "COMPLETE", "checkpoint_id": "cp"}]}
        self.assertFalse(nt.run_reached_complete(not_complete)[0])


# --------------------------------------------------------------------------
# Family 6 - duplicate advancement refused
# --------------------------------------------------------------------------


class DuplicateAdvancementTests(CrossTaskBase):
    def test_already_advanced_task_is_not_re_dispatched(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        # Pre-advance A (as if a prior process already did it).
        nt.record_advancement(self.journal, task_id="M0-TA", run_id="r",
                              checkpoint_id="cp-M0-TA", from_state=sm.COMPLETE)
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=3,
                              packet_queue=self.write_queue([self.entry("M0-TB")]))
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        # A is NOT re-run; B is dispatched. A stays advanced exactly once.
        self.assertEqual(self.dispatched, ["M0-TB"])
        steps = {s["task_id"]: s["outcome"] for s in run["task_queue"]["steps"]}
        self.assertEqual(steps["M0-TA"], "already_advanced")
        self.assertTrue(nt.is_advanced(self.journal, "M0-TB"))


# --------------------------------------------------------------------------
# Family 7 - crash before / after advancement (genuine journal reopen)
# --------------------------------------------------------------------------


class CrashMatrixTests(CrossTaskBase):
    def test_crash_BEFORE_advancement_leaves_nothing_advanced(self) -> None:
        # The run is interrupted (returns non-complete); NOTHING advances, and a
        # genuine restart re-runs and advances exactly once.
        self.write_packet("M0-TA")
        e_a = self.entry("M0-TA")
        q = self.write_queue([])
        args = self.make_args(e_a, max_tasks=2, packet_queue=q)
        nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                          self.scripted_run_one({"M0-TA": "incomplete"}))
        self.assertFalse(nt.is_advanced(self.journal, "M0-TA"))

        journal = self.reopen()  # genuine restart
        self.dispatched.clear()
        args2 = self.make_args(e_a, max_tasks=2, packet_queue=q)
        nt.run_task_queue(args2, self.checkout, journal, self.audit,
                          self.scripted_run_one({"M0-TA": "complete"}))
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertTrue(nt.is_advanced(journal, "M0-TA"))

    def test_crash_AFTER_advancement_before_dispatch_resumes_without_doubling(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        # A advanced, then the process died BEFORE B was dispatched.
        nt.record_advancement(self.journal, task_id="M0-TA", run_id="r",
                              checkpoint_id="cp-M0-TA", from_state=sm.COMPLETE)
        journal = self.reopen()  # genuine restart
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=2,
                              packet_queue=self.write_queue([self.entry("M0-TB")]))
        run = nt.run_task_queue(args, self.checkout, journal, self.audit,
                                self.scripted_run_one({}))
        # A is not re-advanced; the restart selects B correctly.
        self.assertEqual(self.dispatched, ["M0-TB"])
        self.assertEqual(run["task_queue"]["advanced"], ["M0-TB"])
        self.assertTrue(nt.is_advanced(journal, "M0-TA"))


# --------------------------------------------------------------------------
# Family 8 - stale campaign state
# --------------------------------------------------------------------------


class StalePacketTests(CrossTaskBase):
    def test_packet_changed_after_queueing_is_refused_as_stale(self) -> None:
        entry = self.entry("M0-TB")
        self.write_packet("M0-TB")
        queued = nt.packet_digest(entry.packet_path)
        # The packet is edited AFTER it was queued.
        self.write_packet("M0-TB", status="claimed", objective="changed")
        verdict = nt.evaluate_eligibility(entry, queued_digest=queued,
                                          primary_checkout=str(self.checkout))
        self.assertFalse(verdict.eligible)
        self.assertEqual(verdict.code, "stale_packet")

    def test_driver_refuses_a_packet_edited_during_the_journey(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        e_b = self.entry("M0-TB")
        args = self.make_args(e_a, max_tasks=3, packet_queue=self.write_queue([e_b]))

        def edit_b_when_a_runs(task_id: str) -> None:
            if task_id == "M0-TA":
                self.write_packet("M0-TB", objective="edited mid-journey")

        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}, on_dispatch=edit_b_when_a_runs))
        self.assertEqual(self.dispatched, ["M0-TA"])  # B refused as stale
        skips = [s for s in run["task_queue"]["steps"]
                 if s["task_id"] == "M0-TB" and s["outcome"] == "skipped"]
        self.assertTrue(skips and "stale_packet" in skips[0]["detail"])
        self.assertEqual(run["task_queue"]["stop_reason"], nt.NO_ELIGIBLE_WORK)

    def test_the_queued_snapshot_survives_a_restart(self) -> None:
        # The snapshot is taken CAS-once at first queueing; a resume that re-reads
        # the (now edited) packet still compares against the ORIGINAL snapshot.
        self.write_packet("M0-TB")
        original = nt.packet_digest(str(self.tasks_dir / "M0-TB.json"))
        stored = nt.snapshot_queued_digest(self.journal, "M0-TB", original)
        self.assertEqual(stored, original)
        journal = self.reopen()
        # A different digest offered after restart does NOT overwrite the snapshot.
        again = nt.snapshot_queued_digest(journal, "M0-TB", "different-digest")
        self.assertEqual(again, original)


# --------------------------------------------------------------------------
# Family 9 - no eligible work lands NO_ELIGIBLE_WORK visibly
# --------------------------------------------------------------------------


class NoEligibleWorkTests(CrossTaskBase):
    def test_all_successors_ineligible_lands_no_eligible_work(self) -> None:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB", status="backlog")
        self.write_packet("M0-TC", blockers=["held"])
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=5,
                              packet_queue=self.write_queue(
                                  [self.entry("M0-TB"), self.entry("M0-TC")]))
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertEqual(run["task_queue"]["stop_reason"], nt.NO_ELIGIBLE_WORK)

    def test_empty_queue_after_the_first_task_is_exhausted_cleanly(self) -> None:
        self.write_packet("M0-TA")
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=3, packet_queue=self.write_queue([]))
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        self.assertEqual(run["task_queue"]["stop_reason"], "queue_exhausted")


# --------------------------------------------------------------------------
# Family 10 - stop/pause/emergency/graceful intents between tasks
# --------------------------------------------------------------------------


class BetweenTaskIntentTests(CrossTaskBase):
    def _journey_with_intent(self, setter) -> dict:
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=3,
                              packet_queue=self.write_queue([self.entry("M0-TB")]))

        def set_intent_after_a(task_id: str) -> None:
            if task_id == "M0-TA":
                setter(self.journal)

        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}, on_dispatch=set_intent_after_a))
        return run["task_queue"]

    def test_emergency_stop_between_tasks_halts_before_next_dispatch(self) -> None:
        from tools.agent_supervisor.resume_scheduler import EMERGENCY_STOP_KEY
        tq = self._journey_with_intent(
            lambda j: j.set_state(EMERGENCY_STOP_KEY, True))
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertEqual(tq["stop_reason"], f"owner_intent_{stop_intent.INTENT_EMERGENCY}")

    def test_manual_pause_between_tasks_halts_before_next_dispatch(self) -> None:
        from tools.agent_supervisor.resume_scheduler import MANUAL_PAUSE_KEY
        tq = self._journey_with_intent(
            lambda j: j.set_state(MANUAL_PAUSE_KEY, True))
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertEqual(tq["stop_reason"], f"owner_intent_{stop_intent.INTENT_PAUSE}")

    def test_graceful_stop_between_tasks_halts_before_next_dispatch(self) -> None:
        tq = self._journey_with_intent(
            lambda j: stop_intent.set_graceful_stop(j, reason="owner asked to land"))
        self.assertEqual(self.dispatched, ["M0-TA"])
        self.assertEqual(tq["stop_reason"], f"owner_intent_{stop_intent.INTENT_GRACEFUL}")

    def test_budget_exhaustion_between_tasks_halts_before_next_dispatch(self) -> None:
        # The between-task seam also reads the prior run's durable budget report.
        seam = nt.between_task_seam(
            self.journal, {"run_budget": {"exhausted": True,
                                          "exhausted_dimension": "wall_clock"}})
        self.assertEqual(seam, "budget_exhausted")

    def test_no_intent_proceeds(self) -> None:
        self.assertEqual(nt.between_task_seam(self.journal, {"run_budget": None}), "")


# --------------------------------------------------------------------------
# Driver envelope confinement (G3-C1): the multi-task driver runs ONLY under
# --mode limited-auto (the mode half; bounded_mode_gate enforces the enable half)
# --------------------------------------------------------------------------


class ModeConfinementTests(CrossTaskBase):
    def _refused(self, *, mode: str, max_tasks: int,
                 with_queue: bool) -> None:
        """A non-limited-auto multi-task start is refused BEFORE the body runs."""
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        e_b = self.entry("M0-TB")
        queue = self.write_queue([e_b]) if with_queue else None
        args = self.make_args(e_a, max_tasks=max_tasks, packet_queue=queue,
                              mode=mode)
        with self.assertRaises(nt.NextTaskError) as ctx:
            nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                              self.scripted_run_one({}))
        self.assertEqual(ctx.exception.code, "cross_task_mode_refused")
        # The driver body never ran: nothing dispatched, no successor snapshot
        # was taken, and the typed refusal was audited.
        self.assertEqual(self.dispatched, [])
        self.assertEqual(
            self.journal.get_state(nt.queued_digest_key("M0-TB"), ""), "")
        self.assertIn("cross_task_mode_refused", self.audit_events())
        self.assertNotIn("cross_task_dispatch", self.audit_events())

    def test_supervised_multi_task_via_queue_is_refused(self) -> None:
        # The exact escape G3-C1 named: --mode supervised --max-tasks 2
        # --packet-queue reaches the routing ternary but is refused by the driver.
        self._refused(mode="supervised", max_tasks=2, with_queue=True)

    def test_shadow_multi_task_via_max_tasks_is_refused(self) -> None:
        self._refused(mode="shadow", max_tasks=2, with_queue=False)

    def test_supervised_multi_task_via_max_tasks_only_is_refused(self) -> None:
        self._refused(mode="supervised", max_tasks=2, with_queue=False)

    def test_limited_auto_multi_task_proceeds(self) -> None:
        # The authorized envelope: limited-auto (the enable half is enforced
        # pre-dispatch by bounded_mode_gate; this harness is at driver altitude,
        # the same convention as every other family). The driver runs.
        self.write_packet("M0-TA")
        self.write_packet("M0-TB")
        e_a = self.entry("M0-TA")
        args = self.make_args(e_a, max_tasks=2,
                              packet_queue=self.write_queue([self.entry("M0-TB")]),
                              mode="limited-auto")
        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                self.scripted_run_one({}))
        self.assertEqual(self.dispatched, ["M0-TA", "M0-TB"])
        self.assertNotIn("cross_task_mode_refused", self.audit_events())
        self.assertEqual(run["task_queue"]["dispatched"], 2)


# --------------------------------------------------------------------------
# Category-1 (packet readability) sub-codes are individually distinct (G4-O2)
# --------------------------------------------------------------------------


class Category1SubCodeTests(CrossTaskBase):
    def _verdict(self, entry: nt.TaskQueueEntry) -> nt.EligibilityVerdict:
        return nt.evaluate_eligibility(entry, queued_digest="",
                                       primary_checkout=str(self.checkout))

    def test_a_file_io_error_is_packet_unreadable(self) -> None:
        # The packet file does not exist on disk (a read/IO error), distinct from
        # an unparseable-but-readable file.
        wt = self.make_worktree("wt-m0-tb")
        missing = self.tasks_dir / "M0-TB.json"  # never written
        entry = nt.TaskQueueEntry("M0-TB", str(missing), str(wt), "task/b", str(wt))
        verdict = self._verdict(entry)
        self.assertFalse(verdict.eligible)
        self.assertEqual(verdict.code, "packet_unreadable")

    def test_valid_json_that_is_not_an_object_is_packet_not_object(self) -> None:
        # Valid JSON, but a list rather than a JSON object.
        (self.tasks_dir / "M0-TB.json").write_text("[1, 2, 3]", encoding="utf-8")
        wt = self.make_worktree("wt-m0-tb")
        entry = nt.TaskQueueEntry("M0-TB", str(self.tasks_dir / "M0-TB.json"),
                                  str(wt), "task/b", str(wt))
        verdict = self._verdict(entry)
        self.assertFalse(verdict.eligible)
        self.assertEqual(verdict.code, "packet_not_object")


# --------------------------------------------------------------------------
# Real cli._run_loop altitude: shared run_id budget resume + close-run + D6
# across a multi-task journey (G3-C2), and the REAL cli.py:3069 dispatch line
# (G4 required-correction #1)
# --------------------------------------------------------------------------

_PIN = "claude-fable-5"
_CONFIG_TOML = f"""
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["{_PIN}"]

[controller]
default_mode = "shadow"

[model_chain]
orchestrator_preference = ["{_PIN}"]

[limits]
max_review_packet_bytes = 262144
"""
_SELECTION_TOML = f"""
[codex]
review_model = "codex-primary"
advisory_model = "codex-primary"
fallback_models = []

[claude]
model = "{_PIN}"
fallback_models = []
"""


class LiveLoopBase(CrossTaskBase):
    """Harness that drives the REAL ``cli._run_loop`` with a faked provider.

    ``cli._run_loop`` builds the runner and reviewer from the controller config,
    so we supply a real config + model_selection and monkeypatch ``cli.ClaudeRunner``
    / ``cli.CodexReviewer`` to the COMPLETE-returning loop fakes. Everything else in
    ``_run_loop`` runs for real: the launch-seam binding, the shared-run_id
    ``RunBudgetLedger.start()``, ``plan_close_run`` on the shared journal, and the
    real ``SupervisedLoop`` (with its D6 dispatch-intent record/reconcile)."""

    def setUp(self) -> None:
        super().setUp()
        self.config_path = self.root / "config.toml"
        self.config_path.write_text(_CONFIG_TOML, encoding="utf-8")
        self.selection_path = self.root / "model_selection.toml"
        self.selection_path.write_text(_SELECTION_TOML, encoding="utf-8")
        # cwd(worktree) -> (task_id, branch) for the provider factories.
        self._task_by_cwd: dict[str, tuple[str, str]] = {}

    def live_entry(self, task_id: str, *, branch: str = "task/branch") -> nt.TaskQueueEntry:
        """A queue entry whose worktree is registered for the provider factories."""
        self.write_packet(task_id)
        entry = self.entry(task_id, branch=branch)
        self._task_by_cwd[os.path.normcase(str(entry.worktree))] = (task_id, branch)
        return entry

    def patch_providers(self) -> None:
        """Route cli.ClaudeRunner / cli.CodexReviewer to the loop fakes."""
        from tools.agent_supervisor import cli

        def runner_factory(config: RunnerConfig, **_kwargs) -> _LoopRunner:
            task_id, branch = self._task_by_cwd[os.path.normcase(str(config.cwd))]
            return _LoopRunner(config, task_id, branch)

        def reviewer_factory(_executable, *, repo, **_kwargs) -> _LoopReviewer:
            task_id, _branch = self._task_by_cwd[os.path.normcase(str(repo))]
            return _LoopReviewer(task_id)

        orig_runner, orig_reviewer = cli.ClaudeRunner, cli.CodexReviewer
        cli.ClaudeRunner = runner_factory  # type: ignore[assignment]
        cli.CodexReviewer = reviewer_factory  # type: ignore[assignment]
        self.addCleanup(setattr, cli, "ClaudeRunner", orig_runner)
        self.addCleanup(setattr, cli, "CodexReviewer", orig_reviewer)

    def live_args(self, first: nt.TaskQueueEntry, *, max_tasks: int,
                  packet_queue: pathlib.Path | None,
                  run_wall_clock_seconds: float | None = 3600.0,
                  mode: str = "limited-auto") -> argparse.Namespace:
        """A fully-named Namespace with every field cli._run_loop reads."""
        return argparse.Namespace(
            task_packet=first.packet_path, worktree=first.worktree,
            branch=first.branch, repo=first.repo, mode=mode,
            owner_enable_bounded_auto=(mode == "limited-auto"), run_id="run-xtask",
            config=str(self.config_path), model_selection=str(self.selection_path),
            claude_executable="fake-claude", codex_executable="fake-codex",
            stage="phase4", max_cycles=1, max_turns=12, unit_timeout=60,
            owner_touch_budget=8, approve_prompt_digest=[],
            run_wall_clock_seconds=run_wall_clock_seconds, session_role="",
            expected_worker_model="", context_rotation_threshold=None,
            authorize_turnover_actuation=False, prompt="do the authorized unit",
            max_tasks=max_tasks,
            packet_queue=str(packet_queue) if packet_queue else None)

    def audit_records(self) -> list[dict]:
        text = (self.root / "audit.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]


class LiveRunLoopCrossTaskTests(LiveLoopBase):
    """G3-C2: the cross-task journey through the REAL cli._run_loop, asserting the
    per-journey shared-run_id budget semantics + close-run + D6 across the task
    boundary."""

    def test_two_task_journey_through_real_run_loop(self) -> None:
        from tools.agent_supervisor import cli

        e_a = self.live_entry("M0-TA", branch="task/a")
        e_b = self.live_entry("M0-TB", branch="task/b")
        queue = self.write_queue([e_b])
        args = self.live_args(e_a, max_tasks=2, packet_queue=queue)
        self.patch_providers()

        run = nt.run_task_queue(args, self.checkout, self.journal, self.audit,
                                cli._run_loop)

        tq = run["task_queue"]
        # Both tasks ran through the REAL _run_loop, each advanced exactly once.
        # (self.dispatched is only tracked by the harness' fake run_one variants;
        # the real cli._run_loop path proves dispatch through advancement.)
        self.assertEqual(tq["dispatched"], 2)
        self.assertEqual(tq["advanced"], ["M0-TA", "M0-TB"])
        self.assertEqual(tq["stop_reason"], "queue_exhausted")
        self.assertTrue(nt.is_advanced(self.journal, "M0-TA"))
        self.assertTrue(nt.is_advanced(self.journal, "M0-TB"))

        events = [r.get("event_type") for r in self.audit_records()]
        # (a) ONE owner-set run budget bounds the WHOLE journey: task 1 STARTS it,
        # task 2 (same run_id, same budget digest) takes the clean RESUME branch -
        # never a budget_conflict / refusal.
        self.assertEqual(events.count("run_budget_started"), 1)
        self.assertEqual(events.count("run_budget_resumed"), 1)
        self.assertNotIn("budget_conflict", events)
        self.assertNotIn("run_budget_refused", events)

        # (b) plan_close_run closes COMPLETE->IDLE on the SHARED journal between
        # tasks (task 2's _run_loop closes task 1's resting COMPLETE run).
        closes = [r for r in self.audit_records()
                  if r.get("event_type") == "state_transition"
                  and r.get("policy_result") == nt.RUN_CLOSED_TRIGGER]
        self.assertTrue(closes, "no run_closed transition was recorded")
        self.assertTrue(any(c.get("state_from") == sm.COMPLETE
                            and c.get("state_to") == sm.IDLE for c in closes),
                        f"no COMPLETE->IDLE close on the shared journal: {closes}")

        # (c) the D6 dispatch-intent record/reconcile cycle behaves across the task
        # boundary: nothing is left unreconciled after the completed journey.
        self.assertEqual(list(self.journal.pending_effects()), [])


class CmdStartDispatchTests(LiveLoopBase):
    """G4 required-correction #1: exercise the REAL cli.py:3069 dispatch line.

    Full ``cli.cmd_start`` cannot be driven in a focused unit test: its
    live-revalidation gauntlet (the ``auth`` and ``cli_capability_manifest``
    probes) requires a real launched provider process and a live capability
    manifest (golden-run altitude). So instead of an inline copy of the condition
    (the gap the G4 review named in ``DefaultShapeTests``), these tests execute the
    VERBATIM ``run = (...)`` expression extracted from ``cli.cmd_start``'s own
    source: a regression in the routing condition or in the arguments passed to
    ``run_task_queue`` changes the executed bytes and is caught here."""

    @staticmethod
    def dispatch_expression() -> str:
        """The verbatim cli.py:3069 assignment, read from cmd_start's source."""
        from tools.agent_supervisor import cli

        src = inspect.getsource(cli.cmd_start)
        module = ast.parse(src)
        func = module.body[0]
        for node in ast.walk(func):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "run"
                    and isinstance(node.value, ast.IfExp)):
                segment = ast.get_source_segment(src, node)
                if segment and "next_task.run_task_queue" in segment:
                    return segment
        raise AssertionError("the cli.py:3069 dispatch assignment was not found")

    def test_the_extracted_line_is_the_real_dispatch_expression(self) -> None:
        # Guard the extraction itself: it must be the routing ternary, not an
        # inline re-implementation.
        line = self.dispatch_expression()
        self.assertIn("next_task.run_task_queue(args, checkout, journal, audit, "
                      "_run_loop)", line)
        self.assertIn("_run_loop(args, checkout, journal, audit)", line)
        self.assertIn("max_tasks", line)
        self.assertIn("packet_queue", line)

    def test_multi_task_start_routes_to_the_driver_with_run_loop_injected(self) -> None:
        # The TRUE branch: --max-tasks 2 / --packet-queue set. Executing the REAL
        # line must call next_task.run_task_queue with cli._run_loop as the 5th
        # (run_one) argument, and drive the whole journey through it.
        from tools.agent_supervisor import cli

        e_a = self.live_entry("M0-TA", branch="task/a")
        e_b = self.live_entry("M0-TB", branch="task/b")
        queue = self.write_queue([e_b])
        args = self.live_args(e_a, max_tasks=2, packet_queue=queue)
        self.patch_providers()

        captured: dict[str, object] = {}
        real_rtq = nt.run_task_queue

        def spy_run_task_queue(args, checkout, journal, audit, run_one):
            captured["run_one"] = run_one
            return real_rtq(args, checkout, journal, audit, run_one)

        self.addCleanup(setattr, nt, "run_task_queue", real_rtq)
        nt.run_task_queue = spy_run_task_queue  # type: ignore[assignment]

        namespace = {"next_task": nt, "_run_loop": cli._run_loop, "args": args,
                     "checkout": self.checkout, "journal": self.journal,
                     "audit": self.audit}
        exec(compile(self.dispatch_expression(), "<cli-3069>", "exec"),  # noqa: S102
             namespace)

        # Dispatch reached run_task_queue with the REAL cli._run_loop injected.
        self.assertIs(captured.get("run_one"), cli._run_loop)
        run = namespace["run"]
        self.assertEqual(run["task_queue"]["dispatched"], 2)
        self.assertEqual(run["task_queue"]["advanced"], ["M0-TA", "M0-TB"])
        self.assertTrue(nt.is_advanced(self.journal, "M0-TA"))
        self.assertTrue(nt.is_advanced(self.journal, "M0-TB"))

    def test_default_start_calls_run_loop_directly_not_the_driver(self) -> None:
        # The FALSE branch: certified defaults (max_tasks=1, packet_queue=None). The
        # real line must call _run_loop DIRECTLY and never enter the driver.
        e_a = self.live_entry("M0-TA", branch="task/a")
        args = self.live_args(e_a, max_tasks=1, packet_queue=None, mode="supervised")

        driver_calls: list[object] = []
        real_rtq = nt.run_task_queue

        def spy_run_task_queue(*a, **k):
            driver_calls.append(a)
            return real_rtq(*a, **k)

        loop_calls: list[object] = []

        def spy_run_loop(args, checkout, journal, audit):
            loop_calls.append(args)
            return {"run_id": "run-xtask", "mode": args.mode,
                    "final_state": sm.COMPLETE, "cycles": [], "stopped": ""}

        self.addCleanup(setattr, nt, "run_task_queue", real_rtq)
        nt.run_task_queue = spy_run_task_queue  # type: ignore[assignment]

        namespace = {"next_task": nt, "_run_loop": spy_run_loop, "args": args,
                     "checkout": self.checkout, "journal": self.journal,
                     "audit": self.audit}
        exec(compile(self.dispatch_expression(), "<cli-3069>", "exec"),  # noqa: S102
             namespace)

        self.assertEqual(driver_calls, [], "the default start must not enter the driver")
        self.assertEqual(len(loop_calls), 1, "the default start must call _run_loop once")


# --------------------------------------------------------------------------
# The certified single-task command shape is unchanged (default bound = 1)
# --------------------------------------------------------------------------


class DefaultShapeTests(CrossTaskBase):
    def test_start_parser_defaults_keep_the_single_task_shape(self) -> None:
        from tools.agent_supervisor import cli
        parser = cli.build_parser()
        start = parser._subparsers._group_actions[0].choices["start"]
        dests = {a.dest: a for a in start._actions}
        self.assertEqual(dests["max_tasks"].default, 1)
        self.assertIsNone(dests["packet_queue"].default)

    def test_driver_is_not_entered_for_the_default_start(self) -> None:
        # The cli routing condition is (max_tasks>1 or packet_queue); with the
        # certified defaults it is False, so _run_loop runs exactly as today.
        args = argparse.Namespace(max_tasks=1, packet_queue=None)
        entered = int(getattr(args, "max_tasks", 1) or 1) > 1 or getattr(
            args, "packet_queue", None)
        self.assertFalse(bool(entered))


if __name__ == "__main__":
    unittest.main()
