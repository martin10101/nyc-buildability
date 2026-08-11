#!/usr/bin/env python3
"""Regression + hardening test suite for tools/project_control.py (ADR-005; M0-T014).

Runs against disposable temp projects (never the real ledger). Preserves every
check of the original 15-check workflow suite (extended, not weakened) and adds
the M0-T014 hardening scenarios:

  S1  progress transition enum: full legal lifecycle passes; every prohibited
      transition, `--status accepted`, unknown statuses, percent >= 100 and
      negative percent are rejected; terminal tasks are immutable.
  S2  accept preconditions: status must be awaiting_gate; every required gate
      PASS; every dependency accepted; zero open blockers referencing the task
      (affects + detail, fail-closed on missing status; resolved and
      resolved_temporary do not block).
  S3  gate classes: independent gates (G1/G3/G4/G5/G6) require a rostered
      reviewer different from the producer; G2 is recorded by the orchestrator
      with honest role "self_check" and can never satisfy an independent gate;
      G0/G7 are orchestrator-recorded administrative gates; no bypass flag.
  S4  containment: malformed task ids rejected on every subcommand; report
      paths must normalize into project-control/reports/ (../, absolute,
      drive-letter, drive-relative, UNC all rejected); gate ids restricted to
      G0..G7; checkpoint ids restricted to safe filenames.
  S5  atomicity: concurrent progress invocations never corrupt the task file;
      an interrupted write leaves the previous valid file intact and cleans
      its temp file; serialization failures never touch the file.
  S6  spoofing: producer accepting own task, producer gating own task,
      self-review via a renamed --agent, progress to 100, progress to
      accepted, and demoting terminal tasks via submit/gate/claim - all
      rejected.
  S7  backward compatibility: the real ledger (copied into a temp project)
      still parses and serves `status`; legacy gate records without a role
      field (G2/G0 by "orchestrator", G3 by an unrostered legacy reviewer)
      still satisfy acceptance - validation is write-time only. S7 asserts
      only invariants that are stable under any live ledger composition
      (M0-T017): counts that can only grow (files parsed, accepted tasks)
      may be floors, but exemplar records the checks need (e.g., a backlog
      task for the message-only progress probe) are SYNTHESIZED into the
      temp copy when the live ledger happens not to contain one, and a
      permanent zero-backlog sub-check simulates the composition that broke
      CI (job 87990690868: every task claimed or terminal).
  S8  M0-T016 hardening follow-up: (1) the reserved identity "orchestrator" is
      rejected in --reviewers at new-task and as --reviewer on an independent
      gate (even when a legacy packet lists it), while its legitimate G2
      self_check and G0/G7 administrative paths still work; (2) unknown --gates
      entries are rejected immediately, valid G0-G7 combinations accepted;
      (3) a blocked task with an empty/invalid producer/reviewer roster cannot
      transition out of blocked until the packet is amended, after which the
      unblock path works; canceling a blocked task is always allowed. No
      retro-rejection of stored ledger history.
  S10 M0-T033 governance-orchestrator unblock semantics: the reserved
      "orchestrator" may stand as producer_agent at the blocked-exit
      transition ONLY when all four conditions hold together - task_type is
      exactly "governance", required_gates contains at least one INDEPENDENT
      gate, reviewer_agents holds a usable independent reviewer, and nothing
      else about the packet's controls changes. Every prior default is
      re-proven: a non-governance orchestrator producer is still refused, an
      empty/orchestrator-only/producer-only roster is still refused, a
      governance packet with no independent gate is still refused, malformed
      packet data fails CLOSED with an explanatory refusal instead of a
      traceback or a silent allow, blocked -> canceled stays unconditional,
      and gate() is unchanged. Source-level proofs assert the correction is
      GENERAL: the guard's executable code (docstrings stripped, so prose
      provenance stays allowed) names no ledger task id, reuses the existing
      INDEPENDENT_GATES constant rather than re-listing gate ids, and carries
      no environment/bypass/override token; `progress` gains no new option.
  S11 M0-T034 governance acceptance semantics (D-004-R627..R633): (a) a
      requirement row whose sole unmet obligation is an ACCEPTANCE-ORDERING
      LIFECYCLE ACT is EVALUATED and DEFERRED rather than gating accept(), is
      never deleted/waived/silently passed, and is discharged at the FIRST
      post-accept opportunity (checkpoint refuses until then); each of the five
      conjunctive classification conditions is broken in turn and still blocks,
      with a positive control proving the refusals were not incidental.
      (b) a governance-shaped task (allowed_paths entirely under
      project-control/) gets a REAL staleness identity and a REAL dirt guard
      where both previously compared the empty-set hash with itself, and
      reviewed_sha is ACTUALLY compared. Source-level proofs assert no task-id
      allowlist, flag, or environment override exists, that neither module names
      any of the eight candidate rows (their classification is the independent
      verifier's call), and that the classification rule is STATED in the code.

Stdlib only. Run directly (`python tools/test_project_control.py`) or via
pytest. Exit code 0 = all assertions passed.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_PC = HERE.parent / "project-control"
sys.path.insert(0, str(HERE))
import directive_registry as _dr  # noqa: E402  (shared resolver: material_digest, git identity)


def run(tmp: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(tmp / "tools" / "project_control.py"), *args],
        capture_output=True, text=True,
    )


def make_temp_project(tmp: Path) -> None:
    (tmp / "tools").mkdir(parents=True)
    shutil.copy2(HERE / "project_control.py", tmp / "tools" / "project_control.py")
    pc = tmp / "project-control"
    pc.mkdir()
    (pc / "master_plan.json").write_text(json.dumps({
        "project": "regression-test", "current_milestone": "M0",
        "milestones": [{"id": "M0", "name": "test", "status": "active", "depends_on": []}],
    }), encoding="utf-8")
    (pc / "state.json").write_text(json.dumps({
        "project_status": "active", "current_milestone": "M0", "last_checkpoint": None,
        "accepted_tasks": [], "active_tasks": [], "blocked_tasks": [], "failed_gates": [],
    }), encoding="utf-8")
    (pc / "config.json").write_text(json.dumps({
        "required_gates_by_task_type": {"research": ["G0", "G3"]},
    }), encoding="utf-8")
    r = run(tmp, "init")
    assert r.returncode == 0, f"init failed: {r.stderr}"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def edit_task(tmp: Path, task_id: str, **fields) -> None:
    """Fixture helper simulating orchestrator packet authoring (the real
    packets are richer than new-task output)."""
    p = tmp / "project-control" / "tasks" / f"{task_id}.json"
    t = read_json(p)
    t.update(fields)
    p.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")


def write_report(tmp: Path, name: str, content: str = '{"evidence": "x"}') -> str:
    p = tmp / "project-control" / "reports" / name
    p.parent.mkdir(exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"project-control/reports/{name}"


def new_ready_task(tmp: Path, task_id: str, reviewers: str = "reviewer-y,reviewer-z",
                   gates: str = "G0,G3") -> str:
    r = run(tmp, "new-task", "--task-id", task_id, "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", gates,
            "--reviewers", reviewers)
    assert r.returncode == 0, f"new-task {task_id} failed: {r.stderr}"
    rep = write_report(tmp, f"{task_id}-g0.json", '{"gate": "G0"}')
    r = run(tmp, "gate", "--task-id", task_id, "--gate-id", "G0",
            "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
    assert r.returncode == 0, f"G0 gate for {task_id} failed: {r.stderr}"
    return rep


# ---------------------------------------------------------------------------
# Original 15-check workflow (preserved semantics, inputs updated for the
# hardened validation: ledger-format ids, rostered reviewers, relative report
# paths, and the claimed -> in_progress -> self_check chain).
# ---------------------------------------------------------------------------
def test_original_workflow() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-regression-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)                                   # check 1: init
        pc = tmp / "project-control"

        new_ready_task(tmp, "M9-T001")                           # checks 2+3

        # 1. Producer claims, progresses, submits
        r = run(tmp, "claim", "--task-id", "M9-T001", "--agent", "producer-x",
                "--worktree", "wt")
        assert r.returncode == 0, f"claim failed: {r.stderr}"    # check 4
        r = run(tmp, "progress", "--task-id", "M9-T001", "--agent", "producer-x",
                "--percent", "40", "--status", "in_progress", "--message", "core")
        assert r.returncode == 0, f"progress failed: {r.stderr}"
        r = run(tmp, "progress", "--task-id", "M9-T001", "--agent", "producer-x",
                "--percent", "75", "--status", "self_check", "--message", "done")
        assert r.returncode == 0, f"progress failed: {r.stderr}"  # check 5

        # 2a. Producer cannot set 100%
        r = run(tmp, "progress", "--task-id", "M9-T001", "--agent", "producer-x",
                "--percent", "100", "--message", "nope")
        assert r.returncode != 0, "producer setting 100% must be rejected"  # check 6

        rep = write_report(tmp, "M9-T001-producer.json", '{"evidence": "outputs embedded"}')
        r = run(tmp, "submit", "--task-id", "M9-T001", "--agent", "producer-x",
                "--report", rep, "--requested-status", "awaiting_gate")
        assert r.returncode == 0, f"submit failed: {r.stderr}"   # check 7

        # 2b. Producer cannot gate its own task
        r = run(tmp, "gate", "--task-id", "M9-T001", "--gate-id", "G3",
                "--reviewer", "producer-x", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "producer gating own task must be rejected"  # check 8

        # 3. Reviewer returns a report (write needs no CLI); orchestrator records it
        review = write_report(tmp, "M9-T001-g3-review.json",
                              '{"verdict": "PASS", "reviewer": "reviewer-y"}')
        r = run(tmp, "gate", "--task-id", "M9-T001", "--gate-id", "G3",
                "--reviewer", "reviewer-y", "--result", "PASS", "--report", review)
        assert r.returncode == 0, f"reviewer gate failed: {r.stderr}"  # check 9

        # 4. Non-orchestrator cannot accept
        r = run(tmp, "accept", "--task-id", "M9-T001", "--agent", "reviewer-y")
        assert r.returncode != 0, "non-orchestrator accept must be rejected"  # check 10

        # 5a. Acceptance blocked while a required gate is missing
        new_ready_task(tmp, "M9-T002", gates="G0,G3,G5")
        r = run(tmp, "accept", "--task-id", "M9-T002", "--agent", "orchestrator")
        assert r.returncode != 0, "accept with missing required gates must be rejected"  # 11

        # 5b. Orchestrator acceptance succeeds when all gates PASS
        r = run(tmp, "accept", "--task-id", "M9-T001", "--agent", "orchestrator")
        assert r.returncode == 0, f"orchestrator accept failed: {r.stderr}"  # check 12
        task = read_json(pc / "tasks" / "M9-T001.json")
        assert task["status"] == "accepted" and task["progress_percent"] == 100

        # state sync regression (bootstrap defect #2)
        state = read_json(pc / "state.json")
        assert "M9-T001" in state["accepted_tasks"], "sync_state must roster accepted tasks"  # 13

        # BOM tolerance regression (bootstrap defect #1)
        bom = pc / "reports" / "M9-T002-bom.json"
        bom.write_bytes(b'\xef\xbb\xbf{"gate": "G3"}')
        r = run(tmp, "gate", "--task-id", "M9-T002", "--gate-id", "G3",
                "--reviewer", "reviewer-y", "--result", "PASS",
                "--report", "project-control/reports/M9-T002-bom.json")
        assert r.returncode == 0, f"BOM report must be tolerated: {r.stderr}"  # check 14

        # gate history regression (bootstrap defect #3)
        r = run(tmp, "gate", "--task-id", "M9-T002", "--gate-id", "G3",
                "--reviewer", "reviewer-z", "--result", "FAIL",
                "--report", "project-control/reports/M9-T002-bom.json")
        assert r.returncode == 0
        gate_rec = read_json(pc / "gates" / "M9-T002-G3.json")
        assert gate_rec["result"] == "FAIL" and gate_rec["history"][0]["result"] == "PASS", \
            "gate records must preserve history"                 # check 15
        assert gate_rec["role"] == "independent_review"
        print("OK: original 15-check workflow preserved")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S1 - progress transition enum
# ---------------------------------------------------------------------------
def test_s1_transitions() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s1-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        run(tmp, "new-task", "--task-id", "M9-T101", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
            "--reviewers", "reviewer-y")

        def force(status):
            edit_task(tmp, "M9-T101", status=status, producer_agent="producer-x")

        def move(target, percent="50"):
            return run(tmp, "progress", "--task-id", "M9-T101", "--agent", "producer-x",
                       "--percent", percent, "--status", target, "--message", "m")

        legal = [
            ("backlog", "ready"), ("claimed", "in_progress"),
            ("in_progress", "self_check"), ("in_progress", "blocked"),
            ("self_check", "blocked"), ("awaiting_gate", "rework"),
            ("awaiting_gate", "blocked"), ("rework", "in_progress"),
            ("rework", "blocked"), ("blocked", "backlog"), ("blocked", "ready"),
            ("blocked", "in_progress"), ("blocked", "awaiting_gate"),
            ("ready", "blocked"), ("ready", "canceled"),
        ]
        for cur, target in legal:
            force(cur)
            r = move(target)
            assert r.returncode == 0, f"legal {cur}->{target} rejected: {r.stderr}"
            assert read_json(tmp / "project-control" / "tasks" / "M9-T101.json")[
                "status"] == target

        illegal = [
            ("backlog", "in_progress"), ("backlog", "self_check"),
            ("backlog", "awaiting_gate"), ("backlog", "rework"),
            ("ready", "in_progress"), ("ready", "self_check"),
            ("ready", "awaiting_gate"), ("ready", "backlog"),
            ("claimed", "self_check"), ("claimed", "awaiting_gate"),
            ("claimed", "ready"), ("in_progress", "awaiting_gate"),
            ("in_progress", "rework"), ("in_progress", "ready"),
            ("self_check", "in_progress"), ("self_check", "awaiting_gate"),
            ("self_check", "rework"), ("awaiting_gate", "in_progress"),
            ("awaiting_gate", "self_check"), ("awaiting_gate", "ready"),
            ("rework", "self_check"), ("rework", "awaiting_gate"),
            ("rework", "ready"), ("blocked", "self_check"), ("blocked", "rework"),
        ]
        for cur, target in illegal:
            force(cur)
            r = move(target)
            assert r.returncode != 0, f"illegal {cur}->{target} must be rejected"
            assert read_json(tmp / "project-control" / "tasks" / "M9-T101.json")[
                "status"] == cur, f"illegal {cur}->{target} must not change status"

        # claimed is set only by claim
        force("ready")
        r = move("claimed")
        assert r.returncode != 0, "progress must not set 'claimed'"

        # accepted is never settable by progress (argparse choices reject it)
        force("awaiting_gate")
        r = move("accepted")
        assert r.returncode != 0, "progress --status accepted must be rejected"
        assert "invalid choice" in r.stderr, f"expected argparse rejection: {r.stderr}"
        r = move("done")
        assert r.returncode != 0, "unknown status must be rejected"

        # percent bounds
        force("in_progress")
        r = move("in_progress", percent="-1")
        assert r.returncode != 0, "negative percent must be rejected"
        r = move("in_progress", percent="100")
        assert r.returncode != 0, "percent 100 must be rejected"
        r = move("in_progress", percent="99")
        assert r.returncode == 0, f"percent 99 must pass: {r.stderr}"

        # message-only update keeps status
        r = run(tmp, "progress", "--task-id", "M9-T101", "--agent", "producer-x",
                "--percent", "60", "--message", "note only")
        assert r.returncode == 0, f"message-only progress failed: {r.stderr}"
        assert read_json(tmp / "project-control" / "tasks" / "M9-T101.json")[
            "status"] == "in_progress"

        # terminal tasks are immutable via progress
        for terminal in ("accepted", "canceled"):
            force(terminal)
            r = run(tmp, "progress", "--task-id", "M9-T101", "--agent", "orchestrator",
                    "--percent", "50", "--message", "m")
            assert r.returncode != 0, f"progress on {terminal} task must be rejected"

        # claim transitions: only ready/rework are claimable
        for cur, want in [("ready", 0), ("rework", 0), ("backlog", 2), ("claimed", 2),
                          ("in_progress", 2), ("awaiting_gate", 2), ("blocked", 2),
                          ("accepted", 2), ("canceled", 2)]:
            force(cur)
            r = run(tmp, "claim", "--task-id", "M9-T101", "--agent", "producer-x",
                    "--worktree", "wt")
            assert (r.returncode == 0) == (want == 0), \
                f"claim from {cur}: expected {'pass' if want == 0 else 'reject'}: {r.stderr}"

        # submit transitions: only claimed/in_progress/self_check/rework
        rep = write_report(tmp, "M9-T101-r.json")
        for cur, ok in [("claimed", True), ("in_progress", True), ("self_check", True),
                        ("rework", True), ("backlog", False), ("ready", False),
                        ("awaiting_gate", False), ("blocked", False),
                        ("accepted", False), ("canceled", False)]:
            force(cur)
            r = run(tmp, "submit", "--task-id", "M9-T101", "--agent", "producer-x",
                    "--report", rep, "--requested-status", "awaiting_gate")
            assert (r.returncode == 0) == ok, \
                f"submit from {cur}: expected {'pass' if ok else 'reject'}: {r.stderr}"

        # submit requested-status blocked / needs_split
        force("in_progress")
        r = run(tmp, "submit", "--task-id", "M9-T101", "--agent", "producer-x",
                "--report", rep, "--requested-status", "blocked")
        assert r.returncode == 0
        assert read_json(tmp / "project-control" / "tasks" / "M9-T101.json")[
            "status"] == "blocked"
        force("in_progress")
        r = run(tmp, "submit", "--task-id", "M9-T101", "--agent", "producer-x",
                "--report", rep, "--requested-status", "needs_split")
        assert r.returncode == 0
        assert read_json(tmp / "project-control" / "tasks" / "M9-T101.json")[
            "status"] == "rework"
        print("OK: S1 transition enum (legal chain passes; every prohibited jump rejected)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S2 - accept preconditions
# ---------------------------------------------------------------------------
def test_s2_accept_preconditions() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s2-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"

        def ready_for_accept(task_id, deps=None):
            new_ready_task(tmp, task_id)
            rev = write_report(tmp, f"{task_id}-g3.json", '{"verdict": "PASS"}')
            edit_task(tmp, task_id, status="awaiting_gate", producer_agent="producer-x",
                      dependencies=deps or [])
            r = run(tmp, "gate", "--task-id", task_id, "--gate-id", "G3",
                    "--reviewer", "reviewer-y", "--result", "PASS", "--report", rev)
            assert r.returncode == 0, r.stderr

        # (a) status != awaiting_gate rejected even with all gates PASS
        ready_for_accept("M9-T201")
        edit_task(tmp, "M9-T201", status="in_progress")
        r = run(tmp, "accept", "--task-id", "M9-T201", "--agent", "orchestrator")
        assert r.returncode != 0 and "awaiting_gate" in r.stderr, \
            f"accept outside awaiting_gate must be rejected: {r.stderr}"
        edit_task(tmp, "M9-T201", status="awaiting_gate")
        r = run(tmp, "accept", "--task-id", "M9-T201", "--agent", "orchestrator")
        assert r.returncode == 0, f"happy-path accept failed: {r.stderr}"

        # (b) missing required gate rejected (also covered by original check 11)
        new_ready_task(tmp, "M9-T202", gates="G0,G3,G5")
        edit_task(tmp, "M9-T202", status="awaiting_gate", producer_agent="producer-x")
        r = run(tmp, "accept", "--task-id", "M9-T202", "--agent", "orchestrator")
        assert r.returncode != 0 and "G3" in r.stderr and "G5" in r.stderr

        # (c) dependency not accepted rejected; accepted dependency passes
        run(tmp, "new-task", "--task-id", "M9-T204", "--title", "dep", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0")
        ready_for_accept("M9-T203", deps=["M9-T204"])
        r = run(tmp, "accept", "--task-id", "M9-T203", "--agent", "orchestrator")
        assert r.returncode != 0 and "M9-T204" in r.stderr, \
            f"unaccepted dependency must block accept: {r.stderr}"
        edit_task(tmp, "M9-T204", status="accepted")
        r = run(tmp, "accept", "--task-id", "M9-T203", "--agent", "orchestrator")
        assert r.returncode == 0, f"accept with accepted dependency failed: {r.stderr}"
        # missing dependency file also rejected
        ready_for_accept("M9-T205", deps=["M9-T299"])
        r = run(tmp, "accept", "--task-id", "M9-T205", "--agent", "orchestrator")
        assert r.returncode != 0 and "M9-T299" in r.stderr

        # dependencies stored as null (legacy shape) are tolerated
        ready_for_accept("M9-T206", deps=None)
        edit_task(tmp, "M9-T206", dependencies=None)
        r = run(tmp, "accept", "--task-id", "M9-T206", "--agent", "orchestrator")
        assert r.returncode == 0, f"null dependencies must be tolerated: {r.stderr}"

        # (d) open blocker referencing the task blocks acceptance
        blocker = pc / "blockers" / "B-100-test.json"
        ready_for_accept("M9-T207")
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t", "status": "open",
            "affects": ["M9-T207 (hardening test)"], "detail": "credential missing",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T207", "--agent", "orchestrator")
        assert r.returncode != 0 and "B-100" in r.stderr, \
            f"open blocker in affects must block accept: {r.stderr}"
        # resolved blocker does not block
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t", "status": "resolved",
            "affects": ["M9-T207"], "detail": "",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T207", "--agent", "orchestrator")
        assert r.returncode == 0, f"resolved blocker must not block: {r.stderr}"

        # detail-only reference blocks; resolved_temporary does not (ledger B-002)
        ready_for_accept("M9-T208")
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t", "status": "open", "affects": [],
            "detail": "waiting on key before M9-T208 can ship",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T208", "--agent", "orchestrator")
        assert r.returncode != 0 and "B-100" in r.stderr, "detail reference must block"
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t", "status": "resolved_temporary",
            "affects": ["M9-T208"], "detail": "",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T208", "--agent", "orchestrator")
        assert r.returncode == 0, f"resolved_temporary must not block (ledger compat): {r.stderr}"

        # missing status field is fail-closed; unrelated task ids do not match
        ready_for_accept("M9-T209")
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t",
            "affects": ["M9-T209"], "detail": "",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T209", "--agent", "orchestrator")
        assert r.returncode != 0, "blocker with missing status must fail closed"
        blocker.write_text(json.dumps({
            "blocker_id": "B-100", "title": "t", "status": "open",
            "affects": ["M9-T290"], "detail": "mentions M9-T2099 only",
        }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T209", "--agent", "orchestrator")
        assert r.returncode == 0, f"unrelated blocker must not block: {r.stderr}"
        blocker.unlink()
        print("OK: S2 accept preconditions (status, gates, dependencies, blockers)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S3 - gate classes
# ---------------------------------------------------------------------------
def test_s3_gate_classes() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s3-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"
        run(tmp, "new-task", "--task-id", "M9-T301", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o",
            "--gates", "G0,G2,G3", "--reviewers", "rev-a,rev-b")
        edit_task(tmp, "M9-T301", status="awaiting_gate", producer_agent="backend-x")
        rep = write_report(tmp, "M9-T301-ev.json")

        # every independent gate: unrostered reviewer rejected, producer
        # rejected, rostered reviewer passes with role independent_review
        for gid in ("G1", "G3", "G4", "G5", "G6"):
            r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", gid,
                    "--reviewer", "stranger", "--result", "PASS", "--report", rep)
            assert r.returncode != 0 and "reviewer_agents" in r.stderr, \
                f"{gid}: unrostered reviewer must be rejected: {r.stderr}"
            r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", gid,
                    "--reviewer", "backend-x", "--result", "PASS", "--report", rep)
            assert r.returncode != 0, f"{gid}: producer self-gate must be rejected"
            r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", gid,
                    "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
            assert r.returncode == 0, f"{gid}: rostered reviewer failed: {r.stderr}"
            rec = read_json(pc / "gates" / f"M9-T301-{gid}.json")
            assert rec["role"] == "independent_review" and rec["reviewer"] == "rev-a"

        # reviewer == producer is rejected even when rostered (packet mistake)
        run(tmp, "new-task", "--task-id", "M9-T302", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o",
            "--gates", "G0,G3", "--reviewers", "backend-x,rev-a")
        edit_task(tmp, "M9-T302", status="awaiting_gate", producer_agent="backend-x")
        r = run(tmp, "gate", "--task-id", "M9-T302", "--gate-id", "G3",
                "--reviewer", "backend-x", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "rostered producer must still be rejected as reviewer"

        # empty roster: independent gate cannot be recorded at all
        run(tmp, "new-task", "--task-id", "M9-T303", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3")
        edit_task(tmp, "M9-T303", status="awaiting_gate", producer_agent="backend-x")
        r = run(tmp, "gate", "--task-id", "M9-T303", "--gate-id", "G3",
                "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
        assert r.returncode != 0 and "reviewer_agents" in r.stderr, \
            "empty roster must reject independent gates"

        # G2: orchestrator records it with honest role self_check; anyone else rejected
        r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", "G2",
                "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "G2 recorded by a non-orchestrator must be rejected"
        r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", "G2",
                "--reviewer", "backend-x", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "G2 recorded by the producer must be rejected"
        r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", "G2",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
        assert r.returncode == 0, f"G2 by orchestrator failed: {r.stderr}"
        rec = read_json(pc / "gates" / "M9-T301-G2.json")
        assert rec["role"] == "self_check" and rec["reviewer"] == "orchestrator", \
            "G2 record must store the honest self_check role"

        # G0/G7 administrative: orchestrator only
        r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", "G7",
                "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "G7 by non-orchestrator must be rejected"
        r = run(tmp, "gate", "--task-id", "M9-T301", "--gate-id", "G7",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
        assert r.returncode == 0, f"G7 by orchestrator failed: {r.stderr}"
        assert read_json(pc / "gates" / "M9-T301-G7.json")["role"] == "administrative"
        # producer literally named "orchestrator" cannot administer its own task
        run(tmp, "new-task", "--task-id", "M9-T304", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3")
        edit_task(tmp, "M9-T304", producer_agent="orchestrator")
        r = run(tmp, "gate", "--task-id", "M9-T304", "--gate-id", "G0",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "administrative gate on own task must be rejected"

        # a hand-forged self_check record can never satisfy an independent gate
        run(tmp, "new-task", "--task-id", "M9-T305", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o",
            "--gates", "G0,G3", "--reviewers", "rev-a")
        edit_task(tmp, "M9-T305", status="awaiting_gate", producer_agent="backend-x")
        (pc / "gates" / "M9-T305-G0.json").write_text(json.dumps({
            "task_id": "M9-T305", "gate_id": "G0", "reviewer": "orchestrator",
            "role": "administrative", "result": "PASS", "report_file": rep,
            "reviewed_at": "2026-07-17T00:00:00+00:00"}), encoding="utf-8")
        (pc / "gates" / "M9-T305-G3.json").write_text(json.dumps({
            "task_id": "M9-T305", "gate_id": "G3", "reviewer": "orchestrator",
            "role": "self_check", "result": "PASS", "report_file": rep,
            "reviewed_at": "2026-07-17T00:00:00+00:00"}), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T305", "--agent", "orchestrator")
        assert r.returncode != 0 and "self_check" in r.stderr, \
            f"self_check record satisfying an independent gate must be rejected: {r.stderr}"
        # ...nor can any other non-independent role (fail-closed on write-side forgery)
        (pc / "gates" / "M9-T305-G3.json").write_text(json.dumps({
            "task_id": "M9-T305", "gate_id": "G3", "reviewer": "orchestrator",
            "role": "administrative", "result": "PASS", "report_file": rep,
            "reviewed_at": "2026-07-17T00:00:00+00:00"}), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T305", "--agent", "orchestrator")
        assert r.returncode != 0, "non-independent role must not satisfy an independent gate"

        # no bypass flag exists on the gate subcommand
        r = run(tmp, "gate", "-h")
        for flag in ("--force", "--skip", "--override", "--no-check"):
            assert flag not in r.stdout, f"gate must not expose a bypass flag {flag}"
        print("OK: S3 gate classes (independent/self_check/administrative; no bypass)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S4 - containment (task ids, report paths, gate ids, checkpoint ids)
# ---------------------------------------------------------------------------
def test_s4_containment() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s4-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"
        new_ready_task(tmp, "M9-T401")
        edit_task(tmp, "M9-T401", status="awaiting_gate", producer_agent="producer-x")
        good_rep = write_report(tmp, "M9-T401-r.json")

        bad_ids = ["T-1", "M0-T14", "M0-T0140", "m0-t014", "M0-T014-R", "M0T014",
                   "../M9-T401", "M9-T401/../M9-T402", "M9-T401 ", "C:\\evil",
                   "..\\..\\evil", "M9-.json"]
        before = sorted(p.name for p in (pc / "tasks").glob("*"))
        for bad in bad_ids:
            for args in (
                ["new-task", "--task-id", bad, "--title", "t", "--task-type", "research",
                 "--milestone", "M0", "--objective", "o"],
                ["claim", "--task-id", bad, "--agent", "a", "--worktree", "w"],
                ["progress", "--task-id", bad, "--agent", "a", "--percent", "10",
                 "--message", "m"],
                ["submit", "--task-id", bad, "--agent", "a", "--report", good_rep,
                 "--requested-status", "awaiting_gate"],
                ["gate", "--task-id", bad, "--gate-id", "G3", "--reviewer", "reviewer-y",
                 "--result", "PASS", "--report", good_rep],
                ["accept", "--task-id", bad, "--agent", "orchestrator"],
            ):
                r = run(tmp, *args)
                assert r.returncode != 0, f"{args[0]} must reject task id {bad!r}"
        after = sorted(p.name for p in (pc / "tasks").glob("*"))
        assert before == after, "malformed ids must never create or remove task files"
        # dependency ids are validated too
        r = run(tmp, "new-task", "--task-id", "M9-T402", "--title", "t", "--task-type",
                "research", "--milestone", "M0", "--objective", "o",
                "--depends", "M9-T401,../evil")
        assert r.returncode != 0, "malformed dependency ids must be rejected"

        bad_reports = ["../r.md", "/tmp/r.md", "C:\\r.md", "C:r.md",
                       "\\\\srv\\share\\r.md", "project-control/reports/../../x.md",
                       "project-control\\..\\r.md", "docs/research/r.md",
                       "project-control/reports/./x.md", "project-control/tasks/M9-T401.json",
                       ""]
        for bad in bad_reports:
            r = run(tmp, "submit", "--task-id", "M9-T401", "--agent", "producer-x",
                    "--report", bad, "--requested-status", "awaiting_gate")
            assert r.returncode != 0, f"submit must reject report path {bad!r}"
            r = run(tmp, "gate", "--task-id", "M9-T401", "--gate-id", "G3",
                    "--reviewer", "reviewer-y", "--result", "PASS", "--report", bad)
            assert r.returncode != 0, f"gate must reject report path {bad!r}"

        # accepted report forms: forward slash, backslash, bare filename
        for good in ("project-control/reports/M9-T401-r.json",
                     "project-control\\reports\\M9-T401-r.json",
                     "M9-T401-r.json"):
            r = run(tmp, "gate", "--task-id", "M9-T401", "--gate-id", "G3",
                    "--reviewer", "reviewer-y", "--result", "PASS", "--report", good)
            assert r.returncode == 0, f"valid report form {good!r} rejected: {r.stderr}"
            rec = read_json(pc / "gates" / "M9-T401-G3.json")
            assert rec["report_file"] == "project-control/reports/M9-T401-r.json", \
                "stored report_file must be the normalized posix relative path"

        # gate ids restricted to the G0..G7 catalog
        for bad_gid in ("G9", "GX", "../../tasks/M9-T401", "g3"):
            r = run(tmp, "gate", "--task-id", "M9-T401", "--gate-id", bad_gid,
                    "--reviewer", "reviewer-y", "--result", "PASS", "--report", good_rep)
            assert r.returncode != 0 and "invalid choice" in r.stderr, \
                f"gate id {bad_gid!r} must be rejected"

        # checkpoint ids restricted to safe filenames
        for bad_cp in ("../CP-1", "a/b", "a\\b", "..", ".hidden", ""):
            r = run(tmp, "checkpoint", "--checkpoint-id", bad_cp, "--commit", "c",
                    "--branch", "b", "--summary", "s")
            assert r.returncode != 0, f"checkpoint id {bad_cp!r} must be rejected"
        r = run(tmp, "checkpoint", "--checkpoint-id", "CP-9001", "--commit", "c",
                "--branch", "b", "--summary", "s")
        assert r.returncode == 0, f"valid checkpoint failed: {r.stderr}"
        assert (pc / "checkpoints" / "CP-9001.json").exists()
        print("OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S5 - atomic, concurrency-safe writes
# ---------------------------------------------------------------------------
def test_s5_atomicity() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s5-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"
        new_ready_task(tmp, "M9-T501")
        r = run(tmp, "claim", "--task-id", "M9-T501", "--agent", "producer-x",
                "--worktree", "wt")
        assert r.returncode == 0, r.stderr

        # threaded harness: concurrent message-only progress invocations
        def one(i):
            return run(tmp, "progress", "--task-id", "M9-T501", "--agent", "producer-x",
                       "--percent", "50", "--message", f"concurrent-{i}")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(one, range(8)))
        for r in results:
            assert r.returncode == 0, f"concurrent progress failed: {r.stderr}"
        task = read_json(pc / "tasks" / "M9-T501.json")   # parses = not corrupt
        assert task["task_id"] == "M9-T501" and task["status"] == "claimed"
        assert len(task.get("progress_log", [])) >= 1
        state = read_json(pc / "state.json")              # concurrent sync_state too
        assert "M9-T501" in state["active_tasks"]
        leftovers = list((pc / "tasks").glob("*.tmp"))
        assert not leftovers, f"temp files must not survive: {leftovers}"

        # interrupted write leaves the previous valid file intact + cleans temp
        spec = importlib.util.spec_from_file_location(
            "pc_under_test", tmp / "tools" / "project_control.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        target = pc / "tasks" / "M9-T501.json"
        before = target.read_bytes()

        def boom(src, dst, **kw):
            raise RuntimeError("simulated crash during replace")
        original = mod._replace_with_retry
        mod._replace_with_retry = boom
        try:
            try:
                mod.save(target, {"task_id": "M9-T501", "status": "corrupted"})
                raise AssertionError("save must propagate the simulated crash")
            except RuntimeError:
                pass
        finally:
            mod._replace_with_retry = original
        assert target.read_bytes() == before, "interrupted write must leave previous file intact"
        assert not list((pc / "tasks").glob("*.tmp")), "failed write must clean its temp file"

        # serialization failure never touches the file
        try:
            mod.save(target, {"task_id": "M9-T501", "bad": {1, 2}})
            raise AssertionError("non-serializable data must raise")
        except TypeError:
            pass
        assert target.read_bytes() == before, "failed serialization must not touch the file"
        assert not list((pc / "tasks").glob("*.tmp"))
        print("OK: S5 atomic writes (concurrent invocations, interrupted write, "
              "serialization failure)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S6 - spoofing negatives
# ---------------------------------------------------------------------------
def test_s6_spoofing() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s6-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"
        new_ready_task(tmp, "M9-T601")
        edit_task(tmp, "M9-T601", status="awaiting_gate", producer_agent="producer-x")
        rep = write_report(tmp, "M9-T601-r.json")

        # producer accepting its own task
        r = run(tmp, "accept", "--task-id", "M9-T601", "--agent", "producer-x")
        assert r.returncode != 0, "producer accept must be rejected"

        # producer gating its own task
        r = run(tmp, "gate", "--task-id", "M9-T601", "--gate-id", "G3",
                "--reviewer", "producer-x", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "producer self-gate must be rejected"

        # self-review via a renamed --reviewer that is not on the roster
        r = run(tmp, "gate", "--task-id", "M9-T601", "--gate-id", "G3",
                "--reviewer", "producer-x-independent", "--result", "PASS", "--report", rep)
        assert r.returncode != 0, "renamed unrostered reviewer must be rejected"

        # progress jumping to 100 by a producer
        r = run(tmp, "progress", "--task-id", "M9-T601", "--agent", "producer-x",
                "--percent", "100", "--message", "done!")
        assert r.returncode != 0, "progress to 100 must be rejected"

        # progress claiming acceptance
        r = run(tmp, "progress", "--task-id", "M9-T601", "--agent", "producer-x",
                "--percent", "99", "--status", "accepted", "--message", "accept me")
        assert r.returncode != 0, "progress --status accepted must be rejected"
        assert read_json(pc / "tasks" / "M9-T601.json")["status"] == "awaiting_gate"

        # terminal tasks cannot be demoted or re-gated
        edit_task(tmp, "M9-T601", status="accepted", progress_percent=100)
        r = run(tmp, "submit", "--task-id", "M9-T601", "--agent", "producer-x",
                "--report", rep, "--requested-status", "awaiting_gate")
        assert r.returncode != 0, "submit must not demote an accepted task"
        r = run(tmp, "gate", "--task-id", "M9-T601", "--gate-id", "G3",
                "--reviewer", "reviewer-y", "--result", "FAIL", "--report", rep)
        assert r.returncode != 0, "gate must not touch an accepted task"
        r = run(tmp, "claim", "--task-id", "M9-T601", "--agent", "someone",
                "--worktree", "wt")
        assert r.returncode != 0, "claim must not touch an accepted task"
        t = read_json(pc / "tasks" / "M9-T601.json")
        assert t["status"] == "accepted" and t["progress_percent"] == 100
        print("OK: S6 spoofing attempts all rejected")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S7 - backward compatibility with the real ledger (validate-on-write only)
# ---------------------------------------------------------------------------
_SYNTHETIC_BACKLOG_ID = "M9-T700"


def _synthesize_backlog_exemplar(pc: Path) -> str:
    """Write a SYNTHETIC, clearly-labeled backlog task into a TEMP ledger copy
    (never the real ledger) and return its id.

    S7's message-only progress probe needs some pre-existing backlog record to
    write against, but the live ledger legitimately contains zero backlog tasks
    whenever every task is claimed, in flight, or terminal - exactly the
    composition that failed CI job 87990690868 (M0-T017). Test-required
    exemplars are therefore synthesized on demand instead of being assumed to
    exist in mutable live data.
    """
    task = {
        "task_id": _SYNTHETIC_BACKLOG_ID,
        "title": "SYNTHETIC S7 exemplar - test-only, never a real ledger task",
        "task_type": "research", "milestone_id": "M0",
        "objective": "backcompat probe target (synthesized by S7)",
        "business_reason": "", "inputs": [], "outputs": [], "dependencies": [],
        "allowed_paths": [], "forbidden_paths": [], "acceptance_scenarios": [],
        "required_gates": ["G0", "G3"], "producer_agent": None,
        "reviewer_agents": ["reviewer-y"], "status": "backlog",
        "progress_percent": 0, "risks": [], "blockers": [],
        "created_at": "2026-07-17T00:00:00+00:00",
        "updated_at": "2026-07-17T00:00:00+00:00",
    }
    (pc / "tasks" / f"{_SYNTHETIC_BACKLOG_ID}.json").write_text(
        json.dumps(task, indent=2) + "\n", encoding="utf-8")
    return _SYNTHETIC_BACKLOG_ID


def test_s7_backward_compatibility() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s7-")
    tmp = Path(tmpdir)
    try:
        assert REAL_PC.exists(), f"real ledger not found at {REAL_PC}"
        (tmp / "tools").mkdir(parents=True)
        shutil.copy2(HERE / "project_control.py", tmp / "tools" / "project_control.py")
        pc = tmp / "project-control"
        pc.mkdir()
        for f in ("master_plan.json", "state.json", "config.json"):
            shutil.copy2(REAL_PC / f, pc / f)
        for d in ("tasks", "gates", "blockers"):
            shutil.copytree(REAL_PC / d, pc / d)
        (pc / "reports").mkdir()
        (pc / "checkpoints").mkdir()
        # S7 tests legacy GATE-RECORD tolerance (no role field), which is orthogonal to the
        # directive regime (thoroughly covered by S9). The real config now enables the regime;
        # disable it in this stripped copy (no resolver/registry/migration manifest is copied)
        # so the synthesized legacy M9-T701 exercises the gate-role path, not regime migration.
        _cfg = read_json(pc / "config.json")
        _cfg.setdefault("directive_compliance_regime", {})["enabled"] = False
        (pc / "config.json").write_text(json.dumps(_cfg, indent=2), encoding="utf-8")

        # every real ledger file still parses
        parsed = 0
        for jf in pc.rglob("*.json"):
            json.loads(jf.read_text(encoding="utf-8-sig"))
            parsed += 1
        assert parsed >= 60, f"expected the full ledger, parsed only {parsed} files"

        # status runs over the entire real roster. NOTE (M0-T017): assert only
        # composition-stable invariants here. `accepted` is a terminal status
        # (S6: immutable), so its count can only grow; a floor is stable.
        r = run(tmp, "status")
        assert r.returncode == 0, f"status over real ledger failed: {r.stderr}"
        payload = json.loads(r.stdout)
        assert payload["task_counts"].get("accepted", 0) >= 21, \
            "the accepted tasks (>= 21 at M0-T014) must remain visible"

        # a write against a pre-existing backlog record (message-only
        # progress, which also drives sync_state across all real task files)
        # is not retro-rejected by the new validation. The live ledger may
        # legitimately have ZERO backlog tasks (all claimed/terminal), so do
        # not assert on live composition: use a real backlog task when one
        # exists, otherwise synthesize the exemplar into the temp copy.
        backlog = [t["id"] for t in payload["tasks"] if t["status"] == "backlog"]
        probe_id = backlog[0] if backlog else _synthesize_backlog_exemplar(pc)
        r = run(tmp, "progress", "--task-id", probe_id, "--agent", "orchestrator",
                "--percent", "0", "--message", "backcompat regression probe")
        assert r.returncode == 0, \
            f"message-only progress on backlog task {probe_id} failed: {r.stderr}"

        # permanent zero-backlog sub-check (regression for CI job 87990690868):
        # strip EVERY backlog task from the copy to reproduce the exact
        # composition that broke CI, prove `status` still serves it, then
        # prove the synthesis path keeps the probe green.
        for tf in (pc / "tasks").glob("*.json"):
            if read_json(tf).get("status") == "backlog":
                tf.unlink()
        r = run(tmp, "status")
        assert r.returncode == 0, f"status over zero-backlog ledger failed: {r.stderr}"
        drained = json.loads(r.stdout)
        assert not [t for t in drained["tasks"] if t["status"] == "backlog"], \
            "zero-backlog simulation must leave no backlog tasks in the copy"
        probe_id = _synthesize_backlog_exemplar(pc)
        r = run(tmp, "progress", "--task-id", probe_id, "--agent", "orchestrator",
                "--percent", "0", "--message", "zero-backlog backcompat probe")
        assert r.returncode == 0, \
            f"synthesized-exemplar progress on zero-backlog ledger failed: {r.stderr}"

        # legacy-shaped records (no role field; G0/G2 by orchestrator; G3 by an
        # unrostered legacy reviewer; empty reviewer_agents) still accept
        legacy = {
            "task_id": "M9-T701", "title": "legacy", "task_type": "research",
            "milestone_id": "M0", "objective": "o", "business_reason": "",
            "inputs": [], "outputs": [], "dependencies": None, "allowed_paths": [],
            "forbidden_paths": [], "acceptance_scenarios": [],
            "required_gates": ["G0", "G2", "G3"], "producer_agent": "backend-x",
            "reviewer_agents": [], "status": "awaiting_gate", "progress_percent": 85,
            "risks": [], "blockers": [], "created_at": "2026-07-14T00:00:00+00:00",
            "updated_at": "2026-07-14T00:00:00+00:00",
        }
        (pc / "tasks" / "M9-T701.json").write_text(json.dumps(legacy), encoding="utf-8")
        for gid, reviewer in (("G0", "orchestrator"), ("G2", "orchestrator"),
                              ("G3", "legacy-reviewer")):
            (pc / "gates" / f"M9-T701-{gid}.json").write_text(json.dumps({
                "task_id": "M9-T701", "gate_id": gid, "reviewer": reviewer,
                "result": "PASS",
                "report_file": "project-control\\reports\\M9-T701-legacy.md",
                "reviewed_at": "2026-07-15T00:00:00+00:00",
            }), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T701", "--agent", "orchestrator")
        assert r.returncode == 0, \
            f"legacy records (no role field) must still satisfy accept: {r.stderr}"
        print(f"OK: S7 backward compatibility ({parsed} real ledger files parse; "
              f"legacy records accepted; validation is write-time only; "
              f"zero-backlog composition survived via synthesized exemplar)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S8 - M0-T016 hardening follow-up (orchestrator roster prohibition, --gates
# enum validation, blocked-task roster precondition)
# ---------------------------------------------------------------------------
def test_s8_hardening_followup() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s8-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"

        # --- (1) orchestrator prohibited in --reviewers at new-task authoring ---
        for rev in ("orchestrator", "reviewer-y,orchestrator", "orchestrator,reviewer-z"):
            r = run(tmp, "new-task", "--task-id", "M9-T801", "--title", "t",
                    "--task-type", "research", "--milestone", "M0", "--objective", "o",
                    "--gates", "G0,G3", "--reviewers", rev)
            assert r.returncode != 0 and "reserved" in r.stderr, \
                f"orchestrator in --reviewers {rev!r} must be rejected: {r.stderr}"
            assert not (pc / "tasks" / "M9-T801.json").exists(), \
                "rejected authoring must not create the task file"
        # a legitimate roster still authors fine
        r = run(tmp, "new-task", "--task-id", "M9-T801", "--title", "t",
                "--task-type", "research", "--milestone", "M0", "--objective", "o",
                "--gates", "G0,G3", "--reviewers", "reviewer-y,reviewer-z")
        assert r.returncode == 0, f"legitimate roster must author: {r.stderr}"

        # --- (1b) orchestrator prohibited on an independent gate, even if a
        # legacy packet lists it in reviewer_agents (validate on write) ---
        run(tmp, "new-task", "--task-id", "M9-T802", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o",
            "--gates", "G0,G3", "--reviewers", "rev-a")
        # simulate a legacy packet that (wrongly) rostered orchestrator
        edit_task(tmp, "M9-T802", status="awaiting_gate", producer_agent="backend-x",
                  reviewer_agents=["orchestrator", "rev-a"])
        rep = write_report(tmp, "M9-T802-ev.json")
        for gid in ("G1", "G3", "G4", "G5", "G6"):
            r = run(tmp, "gate", "--task-id", "M9-T802", "--gate-id", gid,
                    "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
            assert r.returncode != 0 and "reserved" in r.stderr, \
                f"{gid}: orchestrator as independent reviewer must be rejected: {r.stderr}"
            assert not (pc / "gates" / f"M9-T802-{gid}.json").exists(), \
                f"{gid}: rejected independent gate must not write a record"
        # a real rostered reviewer still passes the independent gate
        r = run(tmp, "gate", "--task-id", "M9-T802", "--gate-id", "G3",
                "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
        assert r.returncode == 0, f"rostered reviewer must still pass: {r.stderr}"

        # --- (1c) orchestrator's legitimate self_check + administrative paths
        # STILL WORK (must not be broken by the prohibition) ---
        run(tmp, "new-task", "--task-id", "M9-T803", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o",
            "--gates", "G0,G2,G3", "--reviewers", "rev-a")
        edit_task(tmp, "M9-T803", status="awaiting_gate", producer_agent="backend-x")
        r = run(tmp, "gate", "--task-id", "M9-T803", "--gate-id", "G2",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
        assert r.returncode == 0, f"orchestrator G2 self_check must still work: {r.stderr}"
        assert read_json(pc / "gates" / "M9-T803-G2.json")["role"] == "self_check"
        for gid in ("G0", "G7"):
            r = run(tmp, "gate", "--task-id", "M9-T803", "--gate-id", gid,
                    "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
            assert r.returncode == 0, f"orchestrator {gid} admin must still work: {r.stderr}"
            assert read_json(pc / "gates" / f"M9-T803-{gid}.json")["role"] == "administrative"

        # --- (2) --gates enum validation ---
        for bad_gates in ("G9", "bogus", "G0,G9", "G3,bogus,G4", "g3", "G8", "G10"):
            r = run(tmp, "new-task", "--task-id", "M9-T810", "--title", "t",
                    "--task-type", "research", "--milestone", "M0", "--objective", "o",
                    "--gates", bad_gates, "--reviewers", "rev-a")
            assert r.returncode != 0, f"--gates {bad_gates!r} must be rejected"
            # the error names an offending entry and lists the canonical enum
            offending = [g for g in bad_gates.split(",") if g not in
                         ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7")]
            assert offending[0] in r.stderr, \
                f"error must name the offending entry {offending[0]!r}: {r.stderr}"
            assert "G0" in r.stderr and "G7" in r.stderr, \
                f"error must list the canonical enum: {r.stderr}"
            assert not (pc / "tasks" / "M9-T810.json").exists(), \
                "rejected --gates must not create the task file"
        # every valid single gate and a full combination are accepted unchanged
        r = run(tmp, "new-task", "--task-id", "M9-T810", "--title", "t", "--task-type",
                "research", "--milestone", "M0", "--objective", "o",
                "--gates", "G0,G1,G2,G3,G4,G5,G6,G7", "--reviewers", "rev-a")
        assert r.returncode == 0, f"valid full gate combination rejected: {r.stderr}"
        assert read_json(pc / "tasks" / "M9-T810.json")["required_gates"] == \
            ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"], \
            "valid --gates must be stored unchanged"

        # --- (3) blocked-task roster precondition ---
        # empty reviewer_agents: cannot leave blocked for any active status
        run(tmp, "new-task", "--task-id", "M9-T820", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3")
        edit_task(tmp, "M9-T820", status="blocked", producer_agent="backend-x",
                  reviewer_agents=[])
        for target in ("backlog", "ready", "in_progress", "awaiting_gate"):
            r = run(tmp, "progress", "--task-id", "M9-T820", "--agent", "orchestrator",
                    "--percent", "10", "--status", target, "--message", "unblock")
            assert r.returncode != 0 and "amend" in r.stderr, \
                f"blocked -> {target} without roster must be rejected: {r.stderr}"
            assert read_json(pc / "tasks" / "M9-T820.json")["status"] == "blocked", \
                f"rejected unblock must leave status blocked (target {target})"
        # producer set to the reserved orchestrator is also an invalid roster
        edit_task(tmp, "M9-T820", producer_agent="orchestrator",
                  reviewer_agents=["rev-a"])
        r = run(tmp, "progress", "--task-id", "M9-T820", "--agent", "orchestrator",
                "--percent", "10", "--status", "in_progress", "--message", "unblock")
        assert r.returncode != 0 and "amend" in r.stderr, \
            "producer == orchestrator is an invalid unblock roster"
        # reviewer roster that only names the producer is not usable
        edit_task(tmp, "M9-T820", producer_agent="backend-x",
                  reviewer_agents=["backend-x"])
        r = run(tmp, "progress", "--task-id", "M9-T820", "--agent", "orchestrator",
                "--percent", "10", "--status", "in_progress", "--message", "unblock")
        assert r.returncode != 0 and "amend" in r.stderr, \
            "reviewer roster equal to producer is not a usable independent reviewer"
        # a reviewer roster that only names orchestrator is not usable
        edit_task(tmp, "M9-T820", producer_agent="backend-x",
                  reviewer_agents=["orchestrator"])
        r = run(tmp, "progress", "--task-id", "M9-T820", "--agent", "orchestrator",
                "--percent", "10", "--status", "in_progress", "--message", "unblock")
        assert r.returncode != 0 and "amend" in r.stderr, \
            "reviewer roster of only orchestrator is not usable"
        # canceling a blocked task is always allowed (no roster required)
        edit_task(tmp, "M9-T820", producer_agent="backend-x", reviewer_agents=[],
                  status="blocked")
        r = run(tmp, "progress", "--task-id", "M9-T820", "--agent", "orchestrator",
                "--percent", "10", "--status", "canceled", "--message", "abandon")
        assert r.returncode == 0, f"canceling a blocked task must be allowed: {r.stderr}"
        assert read_json(pc / "tasks" / "M9-T820.json")["status"] == "canceled"
        # after a valid roster amendment, the unblock path works
        run(tmp, "new-task", "--task-id", "M9-T821", "--title", "t", "--task-type",
            "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3")
        edit_task(tmp, "M9-T821", status="blocked", producer_agent="backend-x",
                  reviewer_agents=[])
        r = run(tmp, "progress", "--task-id", "M9-T821", "--agent", "orchestrator",
                "--percent", "10", "--status", "in_progress", "--message", "still empty")
        assert r.returncode != 0, "unblock before amendment must fail"
        edit_task(tmp, "M9-T821", reviewer_agents=["rev-a"])  # orchestrator amends packet
        r = run(tmp, "progress", "--task-id", "M9-T821", "--agent", "orchestrator",
                "--percent", "10", "--status", "in_progress", "--message", "amended")
        assert r.returncode == 0, f"unblock after valid amendment must work: {r.stderr}"
        assert read_json(pc / "tasks" / "M9-T821.json")["status"] == "in_progress"

        # --- no retro-rejection: a message-only progress on a blocked task
        # (status unchanged) is never blocked by the roster precondition ---
        edit_task(tmp, "M9-T821", status="blocked", producer_agent="backend-x",
                  reviewer_agents=[])
        r = run(tmp, "progress", "--task-id", "M9-T821", "--agent", "orchestrator",
                "--percent", "10", "--message", "note only, no status change")
        assert r.returncode == 0, \
            f"message-only progress on a blocked task must not be blocked: {r.stderr}"
        assert read_json(pc / "tasks" / "M9-T821.json")["status"] == "blocked"
        print("OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, "
              "blocked-task roster precondition)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Honest documentation: --agent is caller-provided, not cryptographic identity
# ---------------------------------------------------------------------------
def test_docs_honesty() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-docs-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        r = run(tmp, "-h")
        assert r.returncode == 0
        assert "caller-provided" in r.stdout, "--help must state --agent is caller-provided"
        assert "cryptographic" in r.stdout, "--help must disclaim cryptographic identity"
        source = (HERE / "project_control.py").read_text(encoding="utf-8")
        assert "NOT CRYPTOGRAPHIC" in source, "module docstring must disclaim identity"
        assert "caller-provided" in source
        print("OK: docs honesty (--agent disclaimed in --help and module docstring)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S9  Owner Directive Compliance System (directive D-001): the CLI enforcement
#     lane. All checks are IN-REGIME-gated so legacy/pre-regime tasks are
#     grandfathered (no deadlock). Proves: claim requires valid refs; selective
#     citation refused; governance-path guard (s19); submit requires an evidence
#     map; content-manifest identity goes stale on relevant edits (s7/merge-
#     rebase-squash property); accept blocks until independent verification at the
#     matching content identity; and the migration table over every current status.
# ---------------------------------------------------------------------------
import hashlib as _hashlib


def _sha256_text(s: str) -> str:
    return _hashlib.sha256(s.encode("utf-8")).hexdigest()


def make_directive(pc: Path, did: str, slug: str, task_ids, task_types, milestones,
                   req_specs, paths=None, status="active") -> None:
    """Write a valid directive into a temp registry (correct source hash, locked ids).

    req_specs entries are (requirement_id, applicable_task_ids) or, for the M0-T034
    lifecycle-classification scenarios, (requirement_id, applicable_task_ids, overrides)
    where overrides may set `classification` and `lifecycle_events` on the row."""
    ddir = pc / "directives" / f"{did}-{slug}"
    ddir.mkdir(parents=True, exist_ok=True)
    src_text = f"Verbatim source for {did}.\n"
    (ddir / "source-001.md").write_text(src_text, encoding="utf-8", newline="\n")
    digest = _hashlib.sha256(src_text.encode("utf-8")).hexdigest()
    reqs, vers, ids = [], [], []
    for spec in req_specs:
        rid, applic_task_ids = spec[0], spec[1]
        over = spec[2] if len(spec) > 2 else {}
        ids.append(rid)
        reqs.append({
            "id": rid, "text": "req", "source_ref": "source-001.md#x",
            "classification": over.get("classification", "obligation"), "binding": True,
            "applicability": {"task_ids": applic_task_ids, "task_types": [],
                              "milestones": [], "paths": [],
                              "lifecycle_events": list(over.get("lifecycle_events",
                                                                ["claim"])),
                              "effective_date": "2026-07-23"},
            "dependencies": [], "required_harness": "", "required_evidence": "",
            "producer": "orchestrator", "independent_verifier": "reviewer-v",
            "status": "pending", "status_reason": "", "evidence_paths": [],
            "reviewed_sha": None, "maps_to": {"files": [], "tests": [], "tasks": []},
            "supersedes": None, "not_applicable_justification": None, "checklist": []})
        vers.append({"id": rid, "state": "pending", "evidence": [], "verified_at": None,
                     "verified_by": None, "reviewed_sha": None})
    manifest = {
        "schema": "directive_manifest/v1", "directive_id": did, "version": 1, "slug": slug,
        "title": did, "status": status, "issued_by": "owner", "issued_at": "2026-07-23",
        "captured_at": "2026-07-23T00:00:00+00:00", "channel": "owner_message",
        "frozen_baseline_sha": "1acb9b510541cfa87afff6b2dc197880e01a389b",
        "sources": [{"file": "source-001.md", "kind": "original", "sequence": 1,
                     "content_digest_sha256": digest}],
        "amendments": [], "supersedes": [], "superseded_by": None,
        "affected_tasks": task_ids, "affected_prs": [],
        "scope": {"task_ids": task_ids, "task_types": task_types,
                  "milestones": milestones, "paths": paths or []},
        "owner_approval": {"state": "approved_for_implementation"},
        "lifecycle_state": status, "requirements_file": "requirements.json",
        "verification_file": "verification.json", "final_reviewed_sha": None,
        "final_reviewed_manifest_sha256": None,
        "locked_requirement_ids": ids,
        "requirements_id_digest_sha256": _hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest(),
        "created_at": "2026-07-23T00:00:00+00:00", "updated_at": "2026-07-23T00:00:00+00:00",
        "audit_log": [{"at": "2026-07-23T00:00:00+00:00", "by": "orchestrator", "note": "x"}]}
    reqs_obj = {"schema": "directive_requirements/v1", "directive_id": did, "version": 1,
                "producer": "orchestrator", "requirement_count": len(reqs),
                "requirements": reqs, "updated_at": "2026-07-23T00:00:00+00:00"}
    (ddir / "requirements.json").write_text(json.dumps(reqs_obj, indent=2), encoding="utf-8")
    manifest["requirements_content_digest_sha256"] = _hashlib.sha256(
        (ddir / "requirements.json").read_bytes()).hexdigest()
    (ddir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ddir / "verification.json").write_text(json.dumps(
        {"schema": "directive_verification/v1", "directive_id": did, "producer": "orchestrator",
         "verifier": None, "reviewed_sha": None, "reviewed_manifest_sha256": None,
         "requirements": vers, "updated_at": "2026-07-23T00:00:00+00:00"}, indent=2),
        encoding="utf-8")
    idx_path = pc / "directives" / "index.json"
    idx = read_json(idx_path) if idx_path.exists() else {
        "schema": "directive_index/v1", "version": 1, "directives": [],
        "updated_at": "2026-07-23T00:00:00+00:00"}
    idx["directives"].append({
        "directive_id": did, "slug": slug, "title": did, "status": status,
        "issued_at": "2026-07-23", "issued_by": "owner", "supersedes": [],
        "superseded_by": None, "affected_tasks": task_ids,
        "manifest": f"{did}-{slug}/manifest.json"})
    idx_path.write_text(json.dumps(idx, indent=2), encoding="utf-8")


def _git(tmp: Path, *args, allow_fail=False):
    p = subprocess.run(["git", "-C", str(tmp), *args], capture_output=True)
    if not allow_fail and p.returncode != 0:
        raise RuntimeError(f"git {args} failed: {p.stderr.decode('utf-8', 'replace')}")
    return p


def git_init(tmp: Path) -> None:
    _git(tmp, "init", "-q")
    _git(tmp, "config", "user.email", "t@example.test")
    _git(tmp, "config", "user.name", "t")
    _git(tmp, "config", "commit.gpgsign", "false")
    (tmp / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")


def git_commit_all(tmp: Path, msg: str = "setup") -> str:
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "-q", "-m", msg, allow_fail=True)  # empty commit is fine
    return _git(tmp, "rev-parse", "HEAD").stdout.decode().strip()


def write_migration_manifest(tmp: Path, entries) -> None:
    """entries: iterable of (task_id, material_digest). Writes a valid migration manifest."""
    d = tmp / "project-control" / "directives"
    d.mkdir(parents=True, exist_ok=True)
    mm = {"schema": "directive_migration/v1", "version": 1, "governing_directive": "D-900",
          "frozen_baseline_sha": "1acb9b510541cfa87afff6b2dc197880e01a389b",
          "material_fields": list(_dr.MATERIAL_FIELDS),
          "tasks": [{"task_id": t, "material_digest": dig, "status_at_baseline": "backlog"}
                    for t, dig in entries],
          "task_count": len(list(entries)) if not isinstance(entries, list) else len(entries)}
    (d / "migration_manifest.json").write_text(json.dumps(mm, indent=2) + "\n", encoding="utf-8")


def material_digest_of(tmp: Path, task_id: str) -> str:
    return _dr.material_digest(read_json(tmp / "project-control" / "tasks" / f"{task_id}.json"))


def set_regime_enabled(tmp: Path, enabled: bool) -> None:
    pc = tmp / "project-control"
    cfg = read_json(pc / "config.json")
    cfg["directive_compliance_regime"]["enabled"] = enabled
    (pc / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def setup_regime(tmp: Path, governance_paths=None, enabled: bool = True) -> None:
    """Enable the directive regime in a temp project: copy the resolver, set config, create
    the schema dirs, write a valid (empty) migration manifest, and git-init so the git-
    canonical content identity (D-001 amendment 3, Section 3) can be computed."""
    shutil.copy2(HERE / "directive_registry.py", tmp / "tools" / "directive_registry.py")
    pc = tmp / "project-control"
    cfg = read_json(pc / "config.json")
    cfg["directive_compliance_regime"] = {
        "enabled": enabled, "version": "1.0", "effective_date": "2026-07-23",
        "governance_paths": governance_paths or ["tools/project_control.py",
                                                 "project-control/directives/"]}
    (pc / "config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    (pc / "directives" / "schema" / "v1").mkdir(parents=True, exist_ok=True)
    (pc / "directives" / "schema" / "v2").mkdir(parents=True, exist_ok=True)
    write_migration_manifest(tmp, [])
    git_init(tmp)


def _git_identity(tmp: Path, paths, sha):
    # Pure content identity at a specific commit (no clean-stamp semantics), mirroring the
    # manifest portion of frozen_git_identity so tests can compare identities across commits.
    ident, _entries, err = _dr.git_tree_manifest(tmp, sha, list(paths),
                                                 exclude_prefixes=("project-control/",))
    assert err is None, f"git identity error: {err}"
    return ident


def test_s9_directive_claim_and_governance() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-dc-claim-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        make_directive(pc, "D-900", "example", task_ids=["M9-T900", "M9-T902"],
                       task_types=["governance"], milestones=["M0"],
                       req_specs=[("D-900-R001", ["M9-T900"]), ("D-900-R002", ["M9-T900"])])
        make_directive(pc, "D-902", "prod", task_ids=["M9-T902"], task_types=[], milestones=[],
                       req_specs=[("D-902-R001", ["M9-T902"])])
        git_commit_all(tmp, "regime setup")

        # (a) in-regime task claimed WITH full refs succeeds; new-task stamps the regime.
        r = run(tmp, "new-task", "--task-id", "M9-T900", "--title", "t", "--task-type",
                "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
                "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-900:ALL")
        assert r.returncode == 0, f"new-task in-regime failed: {r.stderr}"
        assert read_json(pc / "tasks" / "M9-T900.json").get("directive_regime_version") == "1.0"
        # Give the task a real, committed scope so the in-regime G0 gate can stamp a NON-empty
        # content identity: the empty-identity guard (D-011 item 6/M0-T057) now fails closed on
        # a zero-file scope, which this claim/governance test never intended to exercise.
        (tmp / "probe.txt").write_text("scope\n", encoding="utf-8")
        edit_task(tmp, "M9-T900", allowed_paths=["probe.txt"])
        git_commit_all(tmp, "scope M9-T900")
        write_report(tmp, "m9t900-g0.json", '{"g":0}')
        run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer",
            "orchestrator", "--result", "PASS", "--report", "project-control/reports/m9t900-g0.json")
        r = run(tmp, "claim", "--task-id", "M9-T900", "--agent", "orchestrator", "--worktree", "wt")
        assert r.returncode == 0, f"claim with full refs must succeed: {r.stderr}"

        # (b) selective citation is refused at CREATION (new-task validates refs). D-901 has
        # two requirements applicable to M9-T901; citing only one is a selective-citation fail.
        make_directive(pc, "D-901", "sel", task_ids=["M9-T901"], task_types=[], milestones=[],
                       req_specs=[("D-901-R001", ["M9-T901"]), ("D-901-R002", ["M9-T901"])])
        r = run(tmp, "new-task", "--task-id", "M9-T901", "--title", "t", "--task-type",
                "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
                "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-901:D-901-R001")
        assert r.returncode != 0 and "selective citation" in (r.stderr + r.stdout).lower(), \
            f"selective citation must be refused: {r.stdout} {r.stderr}"

        # (c) governance-path guard (s19): an in-regime task touching a governance path but
        # citing only a NON-governance directive is refused; adding a governance ref allows it.
        r = run(tmp, "new-task", "--task-id", "M9-T902", "--title", "t", "--task-type",
                "backend", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
                "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-902:ALL")
        assert r.returncode == 0, f"in-regime new-task must succeed: {r.stderr}"
        edit_task(tmp, "M9-T902", allowed_paths=["tools/project_control.py"])  # governance path
        write_report(tmp, "m9t902-g0.json", '{"g":0}')
        run(tmp, "gate", "--task-id", "M9-T902", "--gate-id", "G0", "--reviewer",
            "orchestrator", "--result", "PASS", "--report", "project-control/reports/m9t902-g0.json")
        r = run(tmp, "claim", "--task-id", "M9-T902", "--agent", "orchestrator", "--worktree", "wt")
        assert r.returncode != 0 and "governance" in (r.stderr + r.stdout).lower(), \
            f"governance-path task without governance ref must be refused: {r.stdout} {r.stderr}"
        # cite BOTH the product directive (covers D-902-R001) AND the governance directive D-900.
        edit_task(tmp, "M9-T902", directive_refs=[{"directive_id": "D-902", "requirement_ids": "ALL"},
                                                   {"directive_id": "D-900", "requirement_ids": "ALL"}])
        r = run(tmp, "claim", "--task-id", "M9-T902", "--agent", "orchestrator", "--worktree", "wt")
        assert r.returncode == 0, f"governance-path task WITH covering governance ref must claim: {r.stderr}"
        print("OK: S9 directive claim enforcement (refs required, selective citation refused, "
              "governance-path guard)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s9_submit_evidence_and_git_identity() -> None:
    """Section 3: submit stamps the git-canonical identity (require_clean); a relevant-file
    change moves the identity; a dirty relevant file fails closed."""
    tmpdir = tempfile.mkdtemp(prefix="pc-dc-submit-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        (tmp / "probe.txt").write_text("original\n", encoding="utf-8")
        make_directive(pc, "D-900", "example", task_ids=["M9-T900"], task_types=[],
                       milestones=[], req_specs=[("D-900-R001", ["M9-T900"])])
        run(tmp, "new-task", "--task-id", "M9-T900", "--title", "t", "--task-type", "research",
            "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
            "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-900:ALL")
        edit_task(tmp, "M9-T900", allowed_paths=["probe.txt"])
        head = git_commit_all(tmp, "commit probe + task scaffolding")
        write_report(tmp, "g0.json", '{"g":0}')
        run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer", "orchestrator",
            "--result", "PASS", "--report", "project-control/reports/g0.json")
        run(tmp, "claim", "--task-id", "M9-T900", "--agent", "orchestrator", "--worktree", "wt")
        run(tmp, "progress", "--task-id", "M9-T900", "--agent", "orchestrator", "--percent",
            "40", "--status", "in_progress", "--message", "x")
        write_report(tmp, "final.json", '{"report": "x"}')

        # (a) in-regime submit WITHOUT an evidence map is refused.
        r = run(tmp, "submit", "--task-id", "M9-T900", "--agent", "orchestrator",
                "--report", "project-control/reports/final.json", "--requested-status", "awaiting_gate")
        assert r.returncode != 0 and "evidence-map" in (r.stderr + r.stdout), \
            f"in-regime submit without evidence map must fail: {r.stdout} {r.stderr}"

        # (b) evidence map + clean tree -> submit stamps the git-canonical identity + reviewed sha.
        write_report(tmp, "emap.json", json.dumps({"requirements": {"D-900-R001": ["final.json"]}}))
        r = run(tmp, "submit", "--task-id", "M9-T900", "--agent", "orchestrator",
                "--report", "project-control/reports/final.json", "--requested-status",
                "awaiting_gate", "--evidence-map", "project-control/reports/emap.json", "--sha", head)
        assert r.returncode == 0, f"submit with evidence map must succeed: {r.stderr}"
        rep = read_json(pc / "reports" / "M9-T900.json")
        assert rep.get("content_manifest_sha256") == _git_identity(tmp, ["probe.txt"], head), \
            "submit must stamp the git-canonical content identity"
        assert rep.get("reviewed_sha") == head, "submit must record and validate the reviewed commit sha"

        # (c) a DIRTY relevant file fails closed (untracked/dirty are never silently omitted).
        (tmp / "probe.txt").write_text("edited but not committed\n", encoding="utf-8")
        edit_task(tmp, "M9-T900", status="in_progress")  # reopen for the probe
        r = run(tmp, "submit", "--task-id", "M9-T900", "--agent", "orchestrator",
                "--report", "project-control/reports/final.json", "--requested-status",
                "awaiting_gate", "--evidence-map", "project-control/reports/emap.json", "--sha", head)
        assert r.returncode != 0 and "dirty" in (r.stderr + r.stdout).lower(), \
            f"a dirty relevant file must fail closed: {r.stdout} {r.stderr}"

        # (d) committing the edit moves the identity (stale-evidence property).
        head2 = git_commit_all(tmp, "edit probe")
        assert _git_identity(tmp, ["probe.txt"], head2) != _git_identity(tmp, ["probe.txt"], head), \
            "a committed relevant-file change must move the git-canonical identity"
        print("OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s9_accept_requires_per_task_verification() -> None:
    """Section 2+3: accept blocks until independent PER-TASK verification (v2) at the
    matching git identity; producer==verifier is refused."""
    tmpdir = tempfile.mkdtemp(prefix="pc-dc-accept-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        (tmp / "probe.txt").write_text("content\n", encoding="utf-8")
        make_directive(pc, "D-900", "example", task_ids=["M9-T900"], task_types=[],
                       milestones=[], req_specs=[("D-900-R001", ["M9-T900"])])
        run(tmp, "new-task", "--task-id", "M9-T900", "--title", "t", "--task-type", "research",
            "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
            "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-900:ALL")
        edit_task(tmp, "M9-T900", allowed_paths=["probe.txt"])
        head = git_commit_all(tmp, "commit probe")
        write_report(tmp, "g0.json", '{"g":0}')
        run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer", "orchestrator",
            "--result", "PASS", "--report", "project-control/reports/g0.json")
        run(tmp, "claim", "--task-id", "M9-T900", "--agent", "producer-p", "--worktree", "wt")
        run(tmp, "progress", "--task-id", "M9-T900", "--agent", "producer-p", "--percent", "40",
            "--status", "in_progress", "--message", "x")
        write_report(tmp, "final.json", '{"r": "x"}')
        write_report(tmp, "emap.json", json.dumps({"requirements": {"D-900-R001": ["final.json"]}}))
        run(tmp, "submit", "--task-id", "M9-T900", "--agent", "producer-p", "--report",
            "project-control/reports/final.json", "--requested-status", "awaiting_gate",
            "--evidence-map", "project-control/reports/emap.json", "--sha", head)
        write_report(tmp, "g3.json", '{"g":3}')
        run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G3", "--reviewer", "reviewer-v",
            "--result", "PASS", "--report", "project-control/reports/g3.json", "--sha", head)

        # (a) accept BLOCKED while the per-task verification is unsatisfied (pending).
        r = run(tmp, "accept", "--task-id", "M9-T900", "--agent", "orchestrator")
        assert r.returncode != 0 and "verification" in (r.stderr + r.stdout).lower(), \
            f"accept must block until independent verification: {r.stdout} {r.stderr}"

        # (b) write a v2 task_verification satisfied at the current git identity -> accept OK.
        ident = _git_identity(tmp, ["probe.txt"], head)
        vpath = pc / "directives" / "D-900-example" / "verification.json"
        v2 = {"schema": "directive_verification/v2", "directive_id": "D-900",
              "producer": "orchestrator",
              "task_verifications": [{
                  "directive_id": "D-900", "task_id": "M9-T900",
                  "applicable_requirement_ids": ["D-900-R001"], "reviewed_sha": head,
                  "reviewed_manifest_sha256": ident, "producer": "orchestrator",
                  "verifier": "reviewer-v", "schema_version": "directive_verification/v2",
                  "verified_at": "t", "requirements": [{"id": "D-900-R001", "state": "PASS",
                      "evidence": ["project-control/reports/g3.json"], "verified_by": "reviewer-v"}]}],
              "updated_at": "t"}
        vpath.write_text(json.dumps(v2, indent=2), encoding="utf-8")
        r = run(tmp, "accept", "--task-id", "M9-T900", "--agent", "orchestrator")
        assert r.returncode == 0, f"accept must succeed once per-task verification is satisfied: {r.stderr}"

        # (c) producer == verifier is refused (per-task self-verification).
        v2["task_verifications"][0]["verifier"] = "orchestrator"
        vpath.write_text(json.dumps(v2, indent=2), encoding="utf-8")
        edit_task(tmp, "M9-T900", status="awaiting_gate")
        r = run(tmp, "accept", "--task-id", "M9-T900", "--agent", "orchestrator")
        assert r.returncode != 0, "producer self-verification must be refused"
        print("OK: S9 accept requires independent per-task verification at the git identity")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _make_legacy_task(tmp, task_id, status, reviewers="rev-a,rev-b"):
    """Build a genuine pre-regime task (no stamp) with the regime OFF, drive it to `status`,
    then return. Regime is re-enabled by the caller. Used to exercise the migration table."""
    set_regime_enabled(tmp, False)
    new_ready_task(tmp, task_id, reviewers=reviewers, gates="G0,G3")
    if status in ("ready",):
        pass
    else:
        run(tmp, "claim", "--task-id", task_id, "--agent", "producer-p", "--worktree", "wt")
        if status in ("in_progress", "self_check", "awaiting_gate"):
            run(tmp, "progress", "--task-id", task_id, "--agent", "producer-p",
                "--percent", "40", "--status", "in_progress", "--message", "x")
        if status in ("awaiting_gate",):
            rep = write_report(tmp, f"{task_id}-r.json", '{"r":"x"}')
            run(tmp, "submit", "--task-id", task_id, "--agent", "producer-p", "--report",
                rep, "--requested-status", "awaiting_gate")
            write_report(tmp, f"{task_id}-g3.json", '{"g":3}')
            run(tmp, "gate", "--task-id", task_id, "--gate-id", "G3", "--reviewer", "rev-a",
                "--result", "PASS", "--report", f"project-control/reports/{task_id}-g3.json")
    set_regime_enabled(tmp, True)


def test_s9_regime_bypass_closed_and_migration() -> None:
    """D-001-R121..R133 (Section 1): the nine adversarial migration proofs."""
    tmpdir = tempfile.mkdtemp(prefix="pc-dc-bypass-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)  # regime ENABLED, empty migration manifest, git-init
        pc = tmp / "project-control"
        make_directive(pc, "D-900", "ex", task_ids=["M9-T801"], task_types=[], milestones=[],
                       req_specs=[("D-900-R001", ["M9-T801"])])
        git_commit_all(tmp, "setup")

        # PROOF 1 — a new product task WITHOUT directive references is rejected.
        r = run(tmp, "new-task", "--task-id", "M9-T800", "--title", "t", "--task-type", "backend",
                "--milestone", "M0", "--objective", "o", "--gates", "G0,G3", "--reviewers", "a,b")
        assert r.returncode != 0 and "directive-refs" in (r.stderr + r.stdout), \
            f"PROOF1 new-task without refs must fail closed: {r.stdout} {r.stderr}"

        # PROOF 3 — a new task WITH valid references succeeds.
        r = run(tmp, "new-task", "--task-id", "M9-T801", "--title", "t", "--task-type", "research",
                "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
                "--reviewers", "rev-a,rev-b", "--directive-refs", "D-900:ALL")
        assert r.returncode == 0, f"PROOF3 new-task with valid refs must succeed: {r.stderr}"

        # PROOF 2 — omitting the regime stamp cannot manufacture grandfathered status. Write a
        # legacy awaiting_gate task NOT in the migration manifest and try to accept it.
        _make_legacy_task(tmp, "M9-T802", "awaiting_gate")
        r = run(tmp, "accept", "--task-id", "M9-T802", "--agent", "orchestrator")
        assert r.returncode != 0 and "not in the frozen migration manifest" in (r.stderr + r.stdout), \
            f"PROOF2 a non-manifest legacy task must not be grandfathered: {r.stdout} {r.stderr}"

        # PROOF 4 — an already-active legacy task IN the manifest, material-unchanged, can finish.
        _make_legacy_task(tmp, "M9-T700", "awaiting_gate")
        write_migration_manifest(tmp, [("M9-T700", material_digest_of(tmp, "M9-T700"))])
        r = run(tmp, "accept", "--task-id", "M9-T700", "--agent", "orchestrator")
        assert r.returncode == 0, f"PROOF4 an active in-manifest legacy task must finish: {r.stderr}"

        # PROOF 6 — a lifecycle-only change does NOT count as a material amendment. Re-open a
        # fresh legacy task, register it, do a lifecycle-only progress, and confirm the digest
        # is unchanged and accept still works.
        _make_legacy_task(tmp, "M9-T703", "awaiting_gate")
        dig_before = material_digest_of(tmp, "M9-T703")
        write_migration_manifest(tmp, [("M9-T703", dig_before)])
        run(tmp, "progress", "--task-id", "M9-T703", "--agent", "producer-p", "--percent", "88",
            "--message", "lifecycle-only note")  # status/progress/timestamp only
        assert material_digest_of(tmp, "M9-T703") == dig_before, \
            "PROOF6 a lifecycle-only change must not alter the material digest"
        r = run(tmp, "accept", "--task-id", "M9-T703", "--agent", "orchestrator")
        assert r.returncode == 0, f"PROOF6 lifecycle-only change keeps grandfathering: {r.stderr}"

        # PROOF 5 — a MATERIAL amendment invalidates grandfathering (regime entry required).
        _make_legacy_task(tmp, "M9-T704", "awaiting_gate")
        write_migration_manifest(tmp, [("M9-T704", material_digest_of(tmp, "M9-T704"))])
        edit_task(tmp, "M9-T704", objective="materially different objective")  # material change
        r = run(tmp, "accept", "--task-id", "M9-T704", "--agent", "orchestrator")
        assert r.returncode != 0 and "material amendment" in (r.stderr + r.stdout), \
            f"PROOF5 a material amendment must require regime entry: {r.stdout} {r.stderr}"

        # PROOF 7 — a backlog/ready legacy task must provide refs at its next claim.
        _make_legacy_task(tmp, "M9-T750", "ready")
        write_migration_manifest(tmp, [("M9-T750", material_digest_of(tmp, "M9-T750"))])
        r = run(tmp, "claim", "--task-id", "M9-T750", "--agent", "producer-p", "--worktree", "wt")
        assert r.returncode != 0 and ("not in-regime" in (r.stderr + r.stdout).lower()
                                      or "regime-entry" in (r.stderr + r.stdout).lower()), \
            f"PROOF7 a ready legacy task must enter the regime at claim: {r.stdout} {r.stderr}"
        make_directive(pc, "D-905", "reclaim", task_ids=["M9-T750"], task_types=[], milestones=[],
                       req_specs=[("D-905-R001", ["M9-T750"])])
        r = run(tmp, "claim", "--task-id", "M9-T750", "--agent", "producer-p", "--worktree", "wt",
                "--directive-refs", "D-905:ALL")
        assert r.returncode == 0, f"PROOF7 claiming WITH refs must enter the regime: {r.stderr}"

        # PROOF 7b (G3 F1 regression) — a BLOCKED legacy task cannot be laundered into a
        # continuation status (awaiting_gate/in_progress) via `progress` to slip past the
        # claim-time regime-entry requirement; regime entry happens ONLY at claim.
        set_regime_enabled(tmp, False)
        new_ready_task(tmp, "M9-T760", reviewers="rev-a,rev-b", gates="G0,G3")
        run(tmp, "claim", "--task-id", "M9-T760", "--agent", "producer-p", "--worktree", "wt")
        run(tmp, "progress", "--task-id", "M9-T760", "--agent", "producer-p", "--percent", "40",
            "--status", "in_progress", "--message", "x")
        run(tmp, "progress", "--task-id", "M9-T760", "--agent", "producer-p", "--percent", "40",
            "--status", "blocked", "--message", "blocked pre-regime")
        set_regime_enabled(tmp, True)
        write_migration_manifest(tmp, [("M9-T760", material_digest_of(tmp, "M9-T760"))])
        r = run(tmp, "progress", "--task-id", "M9-T760", "--agent", "producer-p", "--percent", "50",
                "--status", "awaiting_gate", "--message", "launder attempt")
        assert r.returncode != 0 and "regime" in (r.stderr + r.stdout).lower(), \
            f"PROOF7b blocked legacy task must not be laundered to awaiting_gate via progress: {r.stdout} {r.stderr}"
        r = run(tmp, "accept", "--task-id", "M9-T760", "--agent", "orchestrator")
        assert r.returncode != 0, "PROOF7b a blocked legacy task must not be acceptable as grandfathered"

        # PROOF 7c (G3 F1 regression) — a REWORK legacy task likewise cannot be laundered
        # into in_progress via `progress`; it must re-enter the regime at its next claim.
        set_regime_enabled(tmp, False)
        new_ready_task(tmp, "M9-T761", reviewers="rev-a,rev-b", gates="G0,G3")
        run(tmp, "claim", "--task-id", "M9-T761", "--agent", "producer-p", "--worktree", "wt")
        run(tmp, "progress", "--task-id", "M9-T761", "--agent", "producer-p", "--percent", "40",
            "--status", "in_progress", "--message", "x")
        _rep = write_report(tmp, "m9t761.json", '{"r":"x"}')
        run(tmp, "submit", "--task-id", "M9-T761", "--agent", "producer-p", "--report", _rep,
            "--requested-status", "awaiting_gate")
        run(tmp, "progress", "--task-id", "M9-T761", "--agent", "producer-p", "--percent", "60",
            "--status", "rework", "--message", "sent to rework pre-regime")
        set_regime_enabled(tmp, True)
        write_migration_manifest(tmp, [("M9-T761", material_digest_of(tmp, "M9-T761"))])
        r = run(tmp, "progress", "--task-id", "M9-T761", "--agent", "producer-p", "--percent", "65",
                "--status", "in_progress", "--message", "launder attempt")
        assert r.returncode != 0 and "regime" in (r.stderr + r.stdout).lower(), \
            f"PROOF7c rework legacy task must not be laundered to in_progress via progress: {r.stdout} {r.stderr}"

        # PROOF 8 — accepted tasks remain immutable.
        for sub, extra in (("claim", ["--worktree", "wt"]),
                           ("submit", ["--report", "project-control/reports/M9-T700-r.json",
                                       "--requested-status", "awaiting_gate"])):
            r = run(tmp, sub, "--task-id", "M9-T700", "--agent", "producer-p", *extra)
            assert r.returncode != 0, f"PROOF8 accepted task must be immutable to {sub}"

        # PROOF 9 — malformed/unavailable registry state fails closed.
        mmp = pc / "directives" / "migration_manifest.json"
        mmp.write_text("{ this is not valid json", encoding="utf-8")
        r = run(tmp, "new-task", "--task-id", "M9-T809", "--title", "t", "--task-type", "research",
                "--milestone", "M0", "--objective", "o", "--gates", "G0", "--reviewers", "rev-a,rev-b",
                "--directive-refs", "D-900:ALL")
        assert r.returncode != 0 and "migration manifest" in (r.stderr + r.stdout), \
            f"PROOF9 corrupt migration manifest must fail new-task closed: {r.stdout} {r.stderr}"
        # a legacy accept also fails closed when the manifest is corrupt
        _make_legacy_task(tmp, "M9-T810", "awaiting_gate")
        r = run(tmp, "accept", "--task-id", "M9-T810", "--agent", "orchestrator")
        assert r.returncode != 0 and ("corrupt" in (r.stderr + r.stdout).lower()
                                      or "migration manifest" in (r.stderr + r.stdout)), \
            f"PROOF9 corrupt manifest must fail legacy accept closed: {r.stdout} {r.stderr}"
        print("OK: S9 regime-bypass closed + migration table (9 adversarial proofs)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S10 (M0-T033) — governance-orchestrator unblock-roster semantics.
# The ONE narrow case, its four conjunctive conditions, every preserved
# default, fail-closed malformed handling, and source-level generality proofs.
# ---------------------------------------------------------------------------
def test_s10_governance_orchestrator_unblock() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-s10-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"
        seq = [100]

        def blocked_task(**fields):
            """A fresh task forced into `blocked` with an arbitrary packet shape.
            edit_task writes raw JSON, so malformed shapes new-task would reject
            can still be staged - which is exactly the fail-closed surface."""
            seq[0] += 1
            tid = f"M9-T{seq[0]}"
            r = run(tmp, "new-task", "--task-id", tid, "--title", "t",
                    "--task-type", "research", "--milestone", "M0",
                    "--objective", "o", "--gates", "G0,G3")
            assert r.returncode == 0, f"new-task {tid} failed: {r.stderr}"
            fields.setdefault("status", "blocked")
            edit_task(tmp, tid, **fields)
            return tid

        def unblock(tid, target="in_progress"):
            return run(tmp, "progress", "--task-id", tid, "--agent", "orchestrator",
                       "--percent", "10", "--status", target, "--message", "unblock")

        def status_of(tid):
            return read_json(pc / "tasks" / f"{tid}.json")["status"]

        ACTIVE_TARGETS = ("backlog", "ready", "in_progress", "awaiting_gate")

        # D-004-R413/R414 execution proof. Each numbered block appends
        # (label, cases) only when control flow REACHES ITS END, so a block that
        # is skipped, short-circuited, or never invoked is detectable rather than
        # silently counting as "passing because the file contains it". The exact
        # expected label sequence is asserted at the end of this function and the
        # per-block case counts are printed with the group's OK line.
        executed = []

        def _rec(label, cases):
            assert cases > 0, f"S10 block {label!r} reached its end having executed ZERO cases"
            executed.append((label, cases))

        # --- (1) D-004-R362: a NON-governance task with an orchestrator producer
        # is still REFUSED, for several task types and every active target. ---
        n = 0
        for ttype in ("engineering", "research", "infrastructure", "documentation",
                      "Governance", "governance-extra", "gov", ""):
            tid = blocked_task(task_type=ttype, producer_agent="orchestrator",
                               required_gates=["G0", "G3"], reviewer_agents=["rev-a"])
            for target in ACTIVE_TARGETS:
                r = unblock(tid, target)
                assert r.returncode != 0, \
                    f"task_type {ttype!r} + orchestrator producer must not unblock to {target}"
                assert "amend" in r.stderr, f"refusal must ask for an amendment: {r.stderr}"
                assert "governance" in r.stderr, \
                    f"refusal must explain the governance condition: {r.stderr}"
                assert status_of(tid) == "blocked", \
                    f"refused unblock must leave status blocked ({ttype!r} -> {target})"
                n += 1
        _rec("1-non-governance-orchestrator-refused", n)

        # --- (2) D-004-R363: governance + orchestrator + an INDEPENDENT gate +
        # a usable independent reviewer CAN leave blocked. Every independent
        # gate id is exercised, and every active target. ---
        n = 0
        for gid in ("G1", "G3", "G4", "G5", "G6"):
            tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                               required_gates=["G0", gid], reviewer_agents=["rev-a"])
            r = unblock(tid, "in_progress")
            assert r.returncode == 0, \
                f"governance + orchestrator + {gid} + usable reviewer must unblock: {r.stderr}"
            assert status_of(tid) == "in_progress", \
                f"successful unblock must apply the target status ({gid})"
            n += 1
        assert n == 5, f"every independent gate id must be exercised, got {n}"
        for target in ACTIVE_TARGETS:
            tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                               required_gates=["G0", "G2", "G3", "G5"],
                               reviewer_agents=["code-reviewer", "security-reviewer"])
            r = unblock(tid, target)
            assert r.returncode == 0, f"governance unblock to {target} must work: {r.stderr}"
            assert status_of(tid) == target, f"status must become {target}"
            n += 1
        _rec("2-governance-orchestrator-unblocks", n)

        # --- (3) D-004-R364: governance + orchestrator + NO reviewers FAILS. ---
        n = 0
        for roster in ([], None):
            tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                               required_gates=["G0", "G3"], reviewer_agents=roster)
            r = unblock(tid)
            assert r.returncode != 0, f"empty roster {roster!r} must not unblock"
            assert "usable independent reviewer" in r.stderr, \
                f"refusal must name the missing reviewer: {r.stderr}"
            assert status_of(tid) == "blocked"
            n += 1
        _rec("3-governance-orchestrator-no-reviewers-refused", n)

        # --- (4) D-004-R365: a roster of only the reserved orchestrator FAILS. ---
        n = 0
        for roster in (["orchestrator"], ["orchestrator", "orchestrator"], ["", "orchestrator"]):
            tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                               required_gates=["G0", "G3"], reviewer_agents=roster)
            r = unblock(tid)
            assert r.returncode != 0, f"roster {roster!r} has no usable independent reviewer"
            assert "usable independent reviewer" in r.stderr, \
                f"refusal must name the missing reviewer: {r.stderr}"
            assert status_of(tid) == "blocked"
            n += 1
        _rec("4-orchestrator-only-roster-refused", n)

        # --- (5) D-004-R366: governance + orchestrator with NO independent gate
        # FAILS, and the refusal names the missing independent-gate class. ---
        n = 0
        for gates in ([], ["G0"], ["G2"], ["G7"], ["G0", "G2", "G7"], None):
            tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                               required_gates=gates, reviewer_agents=["rev-a"])
            r = unblock(tid)
            assert r.returncode != 0, f"required_gates {gates!r} has no independent gate"
            assert "no independent gate" in r.stderr, \
                f"refusal must name the missing independent gate: {r.stderr}"
            for gid in ("G1", "G3", "G4", "G5", "G6"):
                assert gid in r.stderr, \
                    f"refusal must list the independent gate class ({gid}): {r.stderr}"
            assert status_of(tid) == "blocked"
            n += 1
        _rec("5-governance-no-independent-gate-refused", n)

        # --- (6) D-004-R367: malformed packet data FAILS CLOSED - an explanatory
        # refusal, never a traceback and never a silent allow. ---
        malformed = []
        for bad in ("rev-a", {"a": 1}, 5, ["rev-a", None], [["rev-a"]], [{"n": "rev-a"}],
                    True, 3.5):
            malformed.append(("reviewer_agents", dict(
                task_type="governance", producer_agent="orchestrator",
                required_gates=["G0", "G3"], reviewer_agents=bad)))
            malformed.append(("reviewer_agents/normal-producer", dict(
                task_type="research", producer_agent="backend-x",
                required_gates=["G0", "G3"], reviewer_agents=bad)))
        for bad in ("G3", {"g": "G3"}, ["G3", None], [["G3"]], [{"g": "G3"}], 7):
            malformed.append(("required_gates", dict(
                task_type="governance", producer_agent="orchestrator",
                required_gates=bad, reviewer_agents=["rev-a"])))
        for bad in (5, None, {"t": "governance"}, ["governance"], 1.5):
            malformed.append(("task_type", dict(
                task_type=bad, producer_agent="orchestrator",
                required_gates=["G0", "G3"], reviewer_agents=["rev-a"])))
        for bad in (["orchestrator"], {"p": "x"}, 5, 2.5):
            malformed.append(("producer_agent", dict(
                task_type="governance", producer_agent=bad,
                required_gates=["G0", "G3"], reviewer_agents=["rev-a"])))
        n = 0
        for label, fields in malformed:
            tid = blocked_task(**fields)
            r = unblock(tid)
            assert r.returncode != 0, \
                f"malformed {label} {fields!r} must fail closed, not unblock"
            assert "Traceback" not in r.stderr, \
                f"malformed {label} must not raise: {r.stderr}"
            assert "amend" in r.stderr, \
                f"malformed {label} must return an explanatory refusal: {r.stderr}"
            assert status_of(tid) == "blocked", \
                f"malformed {label} must leave the task blocked"
            n += 1
        _rec("6-malformed-fails-closed", n)

        # --- (7) D-004-R368: a NON-orchestrator producer behaves exactly as before. ---
        # missing / blank producer still refused
        n = 0
        for bad_producer in (None, "", "   "):
            tid = blocked_task(task_type="research", producer_agent=bad_producer,
                               required_gates=["G0", "G3"], reviewer_agents=["rev-a"])
            r = unblock(tid)
            assert r.returncode != 0 and "producer" in r.stderr, \
                f"producer {bad_producer!r} must be refused: {r.stderr}"
            assert status_of(tid) == "blocked"
            n += 1
        # a roster naming only the producer is still refused
        tid = blocked_task(task_type="research", producer_agent="backend-x",
                           required_gates=["G0", "G3"], reviewer_agents=["backend-x"])
        r = unblock(tid)
        assert r.returncode != 0 and "usable independent reviewer" in r.stderr, \
            f"roster equal to the producer must be refused: {r.stderr}"
        n += 1
        # a real producer + a usable reviewer still unblocks, for governance and
        # non-governance, WITH and WITHOUT an independent gate. The without-case
        # is the deliberate scope boundary: required_gates is consulted ONLY on
        # the orchestrator-producer path, so normal producers are untouched.
        for ttype in ("research", "governance"):
            for gates in (["G0", "G3"], ["G0"], ["G2", "G7"], []):
                tid = blocked_task(task_type=ttype, producer_agent="backend-x",
                                   required_gates=gates, reviewer_agents=["rev-a"])
                r = unblock(tid)
                assert r.returncode == 0, \
                    f"normal producer ({ttype}, gates {gates}) must still unblock: {r.stderr}"
                assert status_of(tid) == "in_progress"
                n += 1
        _rec("7-normal-producer-unchanged", n)

        # --- (8) D-004-R369: blocked -> canceled is unconditional, and a
        # message-only progress on a blocked task is never roster-gated. ---
        cancel_shapes = [
            dict(producer_agent=None, reviewer_agents=[]),
            dict(producer_agent="orchestrator", reviewer_agents=["orchestrator"]),
            dict(producer_agent="orchestrator", reviewer_agents=[], task_type="engineering"),
            dict(producer_agent="backend-x", reviewer_agents=["backend-x"]),
            dict(producer_agent=["bad"], reviewer_agents="rev-a"),
            dict(producer_agent={"p": 1}, reviewer_agents={"r": 1}, required_gates="G3"),
        ]
        n = 0
        for shape in cancel_shapes:
            tid = blocked_task(**shape)
            r = unblock(tid, "canceled")
            assert r.returncode == 0, \
                f"blocked -> canceled must always be allowed ({shape!r}): {r.stderr}"
            assert status_of(tid) == "canceled"
            n += 1
        for shape in cancel_shapes:
            tid = blocked_task(**shape)
            r = run(tmp, "progress", "--task-id", tid, "--agent", "orchestrator",
                    "--percent", "10", "--message", "note only, no status change")
            assert r.returncode == 0, \
                f"message-only progress must not be roster-gated ({shape!r}): {r.stderr}"
            assert status_of(tid) == "blocked"
            n += 1
        _rec("8-cancel-and-message-only-ungated", n)

        # --- (9) D-004-R370: gate() is UNCHANGED on a task that used the new case. ---
        tid = blocked_task(task_type="governance", producer_agent="orchestrator",
                           required_gates=["G0", "G2", "G3", "G5"],
                           reviewer_agents=["rev-a", "rev-b"])
        assert unblock(tid, "awaiting_gate").returncode == 0
        rep = write_report(tmp, f"{tid}-g3.json", '{"verdict": "PASS"}')
        # the orchestrator producer still cannot record an independent gate...
        n = 0
        for gid in ("G1", "G3", "G4", "G5", "G6"):
            r = run(tmp, "gate", "--task-id", tid, "--gate-id", gid,
                    "--reviewer", "orchestrator", "--result", "PASS", "--report", rep)
            assert r.returncode != 0, \
                f"orchestrator must never record independent gate {gid}"
            assert "reserved" in r.stderr, f"refusal must cite the reserved identity: {r.stderr}"
            assert not (pc / "gates" / f"{tid}-{gid}.json").exists(), \
                f"a refused gate must write no record ({gid})"
            n += 1
        # ...an unrostered reviewer is still refused...
        r = run(tmp, "gate", "--task-id", tid, "--gate-id", "G3",
                "--reviewer", "stranger", "--result", "PASS", "--report", rep)
        assert r.returncode != 0 and "reviewer_agents" in r.stderr, \
            f"unrostered reviewer must be refused: {r.stderr}"
        assert not (pc / "gates" / f"{tid}-G3.json").exists()
        # ...and the rostered independent reviewer still succeeds, honestly labeled.
        r = run(tmp, "gate", "--task-id", tid, "--gate-id", "G3",
                "--reviewer", "rev-a", "--result", "PASS", "--report", rep)
        assert r.returncode == 0, f"rostered independent reviewer must succeed: {r.stderr}"
        assert read_json(pc / "gates" / f"{tid}-G3.json")["role"] == "independent_review"
        # a producer still cannot independently gate its own task
        tid2 = blocked_task(task_type="research", producer_agent="backend-x",
                            required_gates=["G0", "G3"],
                            reviewer_agents=["backend-x", "rev-a"])
        assert unblock(tid2, "awaiting_gate").returncode == 0
        r = run(tmp, "gate", "--task-id", tid2, "--gate-id", "G3",
                "--reviewer", "backend-x", "--result", "PASS", "--report", rep)
        assert r.returncode != 0 and "own task" in r.stderr, \
            f"producer must not independently gate its own task: {r.stderr}"
        n += 3  # unrostered-refused, rostered-succeeded, producer-refused
        _rec("9-gate-unchanged", n)

        # --- source-level proofs that the correction is GENERAL (D-004-R345/R346) ---
        src = (HERE / "project_control.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        guard_names = ("_roster_strings", "_orchestrator_governance_exception",
                       "invalid_unblock_roster")
        bodies = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in guard_names:
                body = list(node.body)
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    body = body[1:]  # strip docstring: prose provenance stays allowed
                bodies[node.name] = "\n".join(ast.unparse(s) for s in body)
        assert set(bodies) == set(guard_names), \
            f"every guard function must be present: found {sorted(bodies)}"
        code = "\n".join(bodies[n] for n in guard_names)
        assert not re.search(r"M\d+-T\d{3}", code), \
            f"guard executable code must name no ledger task id:\n{code}"
        assert "INDEPENDENT_GATES" in code, \
            "the guard must reuse the existing INDEPENDENT_GATES constant"
        assert "GOVERNANCE_TASK_TYPE" in code and "RESERVED_ORCHESTRATOR" in code, \
            "the guard must use the named constants, not bare literals"
        assert not re.search(r"""['"]G[0-7]['"]""", code), \
            f"the guard must not re-list gate-id literals:\n{code}"
        assert not re.search(r"""['"]governance['"]""", code), \
            f"the guard must not carry a bare governance literal:\n{code}"
        for tok in ("getenv", "environ", "force", "bypass", "override", "skip"):
            assert tok not in code.lower(), \
                f"guard executable code must carry no {tok!r} token:\n{code}"
        assert "os.environ" not in src and "getenv" not in src, \
            "project_control.py must never read the environment"
        assert "M0-T027" not in src, \
            "the correction must not name the motivating task anywhere in the module"
        # `progress` gains no new option: no flag, no override, no bypass argument.
        r = run(tmp, "progress", "-h")
        assert r.returncode == 0, f"progress -h failed: {r.stderr}"
        opts = set(re.findall(r"--[a-z][a-z0-9-]*", r.stdout))
        assert opts == {"--help", "--task-id", "--agent", "--percent", "--status",
                        "--message"}, \
            f"progress must expose exactly the pre-existing options: {sorted(opts)}"
        _rec("10-source-level-generality-proofs", len(guard_names))

        # --- D-004-R413/R414: prove every block above actually RAN, in order. ---
        # EXACT expected (label, case-count) pairs, in order. Exact counts rather
        # than a floor: a block that is skipped, reordered, short-circuited, or
        # silently loses cases then FAILS here instead of passing quietly. If a
        # case is deliberately added, this expectation must be updated with it -
        # that is the point (D-004-R413/R414: presence of code is not evidence of
        # execution).
        expected_blocks = [
            ("1-non-governance-orchestrator-refused", 32),   # 8 task types x 4 targets
            ("2-governance-orchestrator-unblocks", 9),       # 5 gate ids + 4 targets
            ("3-governance-orchestrator-no-reviewers-refused", 2),
            ("4-orchestrator-only-roster-refused", 3),
            ("5-governance-no-independent-gate-refused", 6),
            ("6-malformed-fails-closed", 31),                # 16 roster + 6 gates + 5 type + 4 producer
            ("7-normal-producer-unchanged", 12),             # 3 bad + 1 self-roster + 2x4 still-unblocks
            ("8-cancel-and-message-only-ungated", 12),       # 6 cancel + 6 message-only
            ("9-gate-unchanged", 8),                         # 5 reserved + 3 roster/producer
            ("10-source-level-generality-proofs", 3),        # 3 guard functions parsed
        ]
        assert executed == expected_blocks, \
            ("S10 did not execute every mandatory block, in order, with every "
             f"case.\n  expected: {expected_blocks}\n  actual:   {executed}")
        total = sum(cases for _, cases in executed)
        assert total == 118, f"S10 total executed cases changed: {total}"
        print("OK: S10 governance-orchestrator unblock semantics (4 conjunctive "
              "conditions, preserved defaults, fail-closed malformed data, "
              "gate() unchanged, source-level generality proofs)")
        print(f"    S10 [D-004-R413/R414]: {len(executed)}/{len(expected_blocks)} blocks "
              f"executed, {total} assertion cases")
        print("    S10 per-block case counts: "
              + ", ".join(f"{label}={cases}" for label, cases in executed))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# S11 (M0-T034 / D-004-R627..R633) — governance acceptance semantics.
#   (a) lifecycle-aware acceptance: an acceptance-ordering row is EVALUATED and
#       DEFERRED, never deleted or waived, and is verified at the first
#       post-accept opportunity (checkpoint);
#   (b) the vacuous-guard gap: a governance-shaped task (allowed_paths entirely
#       under project-control/) gets a real staleness identity, a real dirt
#       guard, and an actual reviewed_sha comparison.
# Every negative default is re-proven: any unmet NON-lifecycle row still blocks.
# ---------------------------------------------------------------------------
EMPTY_SET_IDENTITY = _hashlib.sha256(b"").hexdigest()  # e3b0c442..., 0 manifest entries
_CP = ("project-control/",)


def head_of(tmp: Path) -> str:
    return _git(tmp, "rev-parse", "HEAD").stdout.decode().strip()


def gov_identity(tmp: Path, paths, sha) -> str:
    """The identity accept()/submit() compute for a scope, at a specific commit."""
    ident, _sha, err = _dr.frozen_git_identity(
        list(paths), reviewed_sha=sha, root=tmp, exclude_prefixes=_CP,
        require_clean=False, control_plane_prefixes=_CP)
    assert err is None, f"gov identity error: {err}"
    return ident


def vrow_pass(rid: str) -> dict:
    return {"id": rid, "state": "PASS", "evidence": ["e"], "verified_by": "reviewer-v"}


def vrow_lifecycle(rid: str, state: str = "pending", identity: str = "", **over) -> dict:
    """A verification row carrying an independent verifier's per-row acceptance-ordering
    attestation. `identity` is the reviewed CONTENT IDENTITY the attestation is made at,
    which condition (6) requires it to name exactly; the default is the unusable empty
    string, so a caller that forgets it gets a refusal rather than a release. `over`
    mutates the attestation so each condition can be broken."""
    claim = {"act_class": "accept", "classified_by": "reviewer-v",
             "classified_at": "2026-07-31T00:00:00+00:00",
             "classified_at_identity": identity,
             "justification": "the obligation is discharged at acceptance itself"}
    claim.update(over)
    return {"id": rid, "state": state, "evidence": [], "verified_by": None,
            "lifecycle_classification": claim}


def write_v2_verification(pc: Path, did: str, slug: str, task_id: str, applicable, rows,
                          identity: str, sha: str, verifier: str = "reviewer-v",
                          producer: str = "orchestrator") -> None:
    v2 = {"schema": "directive_verification/v2", "directive_id": did, "producer": producer,
          "task_verifications": [{
              "directive_id": did, "task_id": task_id,
              "applicable_requirement_ids": sorted(applicable), "reviewed_sha": sha,
              "reviewed_manifest_sha256": identity, "producer": producer,
              "verifier": verifier, "schema_version": "directive_verification/v2",
              "verified_at": "t", "requirements": list(rows)}],
          "updated_at": "t"}
    (pc / "directives" / f"{did}-{slug}" / "verification.json").write_text(
        json.dumps(v2, indent=2), encoding="utf-8")


def build_governance_task(tmp: Path, tid: str, did: str, slug: str, rids,
                          producer: str = "producer-p"):
    """Drive a GOVERNANCE-SHAPED task (allowed_paths entirely under project-control/)
    to awaiting_gate with every gate PASS and a stamped content identity.
    Returns (head_sha, allowed_paths)."""
    report_md = f"project-control/reports/{tid}-producer-report.md"
    allowed = [f"project-control/tasks/{tid}.json", report_md]
    r = run(tmp, "new-task", "--task-id", tid, "--title", "t", "--task-type", "governance",
            "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
            "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", f"{did}:ALL")
    assert r.returncode == 0, f"new-task {tid} failed: {r.stderr}"
    edit_task(tmp, tid, allowed_paths=allowed)
    (tmp / report_md).parent.mkdir(parents=True, exist_ok=True)
    (tmp / report_md).write_text(f"# {tid} producer report\noriginal\n", encoding="utf-8")
    head = git_commit_all(tmp, f"scaffold {tid}")
    write_report(tmp, f"{tid}-g0.json", '{"g":0}')
    r = run(tmp, "gate", "--task-id", tid, "--gate-id", "G0", "--reviewer", "orchestrator",
            "--result", "PASS", "--report", f"project-control/reports/{tid}-g0.json")
    assert r.returncode == 0, f"G0 {tid}: {r.stderr}"
    r = run(tmp, "claim", "--task-id", tid, "--agent", producer, "--worktree", "wt")
    assert r.returncode == 0, f"claim {tid}: {r.stderr}"
    run(tmp, "progress", "--task-id", tid, "--agent", producer, "--percent", "40",
        "--status", "in_progress", "--message", "x")
    write_report(tmp, f"{tid}-final.json", '{"r":"x"}')
    write_report(tmp, f"{tid}-emap.json",
                 json.dumps({"requirements": {rid: ["e"] for rid in rids}}))
    r = run(tmp, "submit", "--task-id", tid, "--agent", producer, "--report",
            f"project-control/reports/{tid}-final.json", "--requested-status",
            "awaiting_gate", "--evidence-map", f"project-control/reports/{tid}-emap.json",
            "--sha", head)
    assert r.returncode == 0, f"submit {tid}: {r.stdout} {r.stderr}"
    write_report(tmp, f"{tid}-g3.json", '{"g":3}')
    r = run(tmp, "gate", "--task-id", tid, "--gate-id", "G3", "--reviewer", "reviewer-v",
            "--result", "PASS", "--report", f"project-control/reports/{tid}-g3.json",
            "--sha", head)
    assert r.returncode == 0, f"G3 {tid}: {r.stderr}"
    return head, allowed


# The five row shapes every S11 scenario needs. Deliberately generic: the shapes are
# named for the STRUCTURAL property under test, never for any ledger requirement id.
_S11_REQ_SPECS = lambda tid: [                                    # noqa: E731
    ("D-900-R001", [tid], {"classification": "obligation", "lifecycle_events": ["gate"]}),
    ("D-900-R002", [tid], {"classification": "obligation", "lifecycle_events": ["accept"]}),
    ("D-900-R003", [tid], {"classification": "obligation",
                           "lifecycle_events": ["gate", "accept"]}),
    ("D-900-R004", [tid], {"classification": "prohibition", "lifecycle_events": ["accept"]}),
    ("D-900-R005", [tid], {"classification": "sequencing", "lifecycle_events": ["accept"]}),
]
_S11_RIDS = ["D-900-R001", "D-900-R002", "D-900-R003", "D-900-R004", "D-900-R005"]


def test_s11_lifecycle_aware_acceptance_and_post_accept_verification() -> None:
    """AS-1 + AS-4: an acceptance-ordering row is EVALUATED and deferred (never deleted,
    waived, or silently passed), and the deferral is discharged at the FIRST post-accept
    opportunity, which refuses to proceed until then."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-accept-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T340"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        ident = gov_identity(tmp, allowed, head)

        # The guard is no longer vacuous: the stamped identity is a real manifest.
        rep = read_json(pc / "reports" / f"{tid}.json")
        assert rep["content_manifest_sha256"] == ident, "submit must stamp the new identity"
        assert ident != EMPTY_SET_IDENTITY, \
            "a governance-shaped scope must no longer stamp the empty-set hash"

        # R002 (obligation @ accept) and R005 (sequencing @ accept) are attested
        # acceptance-ordering acts; every other applicable row is genuinely PASS.
        rows = [vrow_pass("D-900-R001"), vrow_lifecycle("D-900-R002", identity=ident),
                vrow_pass("D-900-R003"), vrow_pass("D-900-R004"),
                vrow_lifecycle("D-900-R005", identity=ident, act_class="stop_after")]
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident,
                              head_of(tmp))
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, f"AS-1 lifecycle-aware accept must succeed: {r.stdout} {r.stderr}"
        assert "deferred" in r.stdout, f"accept must DISCLOSE the deferrals: {r.stdout}"

        t = read_json(pc / "tasks" / f"{tid}.json")
        assert t["status"] == "accepted"
        block = t["post_accept_verification"]
        assert block["state"] == "pending" and block["first_opportunity"] == "checkpoint"
        deferred = {d["requirement_id"]: d for d in block["deferred_requirements"]}
        assert set(deferred) == {"D-900-R002", "D-900-R005"}, \
            f"exactly the attested acceptance-ordering rows are deferred: {sorted(deferred)}"
        assert deferred["D-900-R002"]["act_class"] == "accept"
        assert deferred["D-900-R005"]["act_class"] == "stop_after"
        for d in deferred.values():
            assert d["classified_by"] == "reviewer-v" and d["justification"], \
                "the deferral record must carry the independent classification + reason"
            assert d["deferred_at_identity"] == ident and d["deferred_at_sha"] == head_of(tmp)
            assert d["classified_at_identity"] == ident, \
                "the attestation must be BOUND to the identity it was granted at (cond. 6)"

        # NEVER deleted, waived, or silently passed: the registry row is untouched.
        v = read_json(pc / "directives" / "D-900-gov" / "verification.json")
        vrows = {r_["id"]: r_ for r_ in v["task_verifications"][0]["requirements"]}
        assert vrows["D-900-R002"]["state"] == "pending", \
            "a deferred row must NOT be rewritten to PASS by acceptance"
        assert "lifecycle_classification" in vrows["D-900-R002"]

        # AS-4: the FIRST post-accept opportunity refuses until the rows are verified.
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp1", "--commit", "abc",
                "--branch", "b", "--summary", "s")
        assert r.returncode != 0, "checkpoint must refuse while a deferral is unverified"
        assert "D-900-R002" in r.stderr and "post-accept" in r.stderr, \
            f"the refusal must name the deferred row: {r.stderr}"
        assert not (pc / "checkpoints" / "cp1.json").exists(), \
            "a refused checkpoint must write no record"

        # Verify ONE row post-accept: still refused (the other remains).
        vrows["D-900-R002"]["state"] = "PASS"
        v["task_verifications"][0]["requirements"] = list(vrows.values())
        (pc / "directives" / "D-900-gov" / "verification.json").write_text(
            json.dumps(v, indent=2), encoding="utf-8")
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp1", "--commit", "abc",
                "--branch", "b", "--summary", "s")
        assert r.returncode != 0 and "D-900-R005" in r.stderr, \
            f"a partially-verified deferral set must still refuse: {r.stderr}"

        # Verify BOTH -> the checkpoint records the closure as durable evidence.
        vrows["D-900-R005"]["state"] = "PASS"
        v["task_verifications"][0]["requirements"] = list(vrows.values())
        (pc / "directives" / "D-900-gov" / "verification.json").write_text(
            json.dumps(v, indent=2), encoding="utf-8")
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp1", "--commit", "abc",
                "--branch", "b", "--summary", "s")
        assert r.returncode == 0, f"checkpoint must proceed once verified: {r.stderr}"
        cp = read_json(pc / "checkpoints" / "cp1.json")
        assert cp["post_accept_verifications_confirmed"][tid] == \
            ["D-900-R002", "D-900-R005"], f"closure must be recorded: {cp}"

        # NOT_APPLICABLE with justification + independent approver also discharges it;
        # NOT_APPLICABLE without them does not.
        vrows["D-900-R005"]["state"] = "NOT_APPLICABLE"
        v["task_verifications"][0]["requirements"] = list(vrows.values())
        (pc / "directives" / "D-900-gov" / "verification.json").write_text(
            json.dumps(v, indent=2), encoding="utf-8")
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp2", "--commit", "a", "--branch",
                "b", "--summary", "s")
        assert r.returncode != 0, "unjustified NOT_APPLICABLE must not discharge a deferral"
        vrows["D-900-R005"]["not_applicable_justification"] = "policy requires no checkpoint"
        vrows["D-900-R005"]["not_applicable_approved_by"] = "reviewer-z"
        v["task_verifications"][0]["requirements"] = list(vrows.values())
        (pc / "directives" / "D-900-gov" / "verification.json").write_text(
            json.dumps(v, indent=2), encoding="utf-8")
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp2", "--commit", "a", "--branch",
                "b", "--summary", "s")
        assert r.returncode == 0, f"justified+approved NOT_APPLICABLE discharges it: {r.stderr}"
        print("OK: S11 lifecycle-aware acceptance + first-post-accept verification "
              "(AS-1, AS-4)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_non_lifecycle_rows_still_block_acceptance() -> None:
    """AS-2 (negative, the one that matters most): ANY unmet non-lifecycle row still
    fails accept() exactly as today. Each of the five conjunctive conditions is broken
    in turn, and a positive control proves the refusals were not incidental."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-block-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T341"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        ident = gov_identity(tmp, allowed, head)
        tpath = pc / "tasks" / f"{tid}.json"

        def attempt(rows, label):
            write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident,
                                  head_of(tmp))
            r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
            t = read_json(tpath)
            assert r.returncode != 0, f"AS-2 {label}: accept must still be refused"
            assert t["status"] == "awaiting_gate", \
                f"AS-2 {label}: a refused accept must not move the task"
            assert "post_accept_verification" not in t, \
                f"AS-2 {label}: a refused accept must register no deferral"
            return r.stderr

        base = {rid: vrow_pass(rid) for rid in _S11_RIDS}
        cases = 0

        # (i) an ordinary unmet row with NO lifecycle claim at all.
        rows = dict(base); rows["D-900-R001"] = {"id": "D-900-R001", "state": "pending"}
        err = attempt(list(rows.values()), "plain unmet row")
        assert "not PASS" in err, err
        cases += 1

        # (ii) condition (3): the row also binds a PRE-acceptance lifecycle event.
        rows = dict(base)
        rows["D-900-R003"] = vrow_lifecycle("D-900-R003", identity=ident)
        err = attempt(list(rows.values()), "mixed lifecycle binding")
        assert "outside acceptance ordering" in err and "not PASS" in err, err
        cases += 1

        # (iii) condition (4): a prohibition bound to acceptance is a BAR, never an act.
        rows = dict(base)
        rows["D-900-R004"] = vrow_lifecycle("D-900-R004", identity=ident)
        err = attempt(list(rows.values()), "prohibition")
        assert "acceptance-ordering ACT" in err, err
        cases += 1

        # (iv) condition (2): the producer cannot classify its own row.
        rows = dict(base)
        rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident,
                                            classified_by="orchestrator")
        err = attempt(list(rows.values()), "producer self-classification")
        assert "INDEPENDENT" in err, err
        cases += 1

        # (v) condition (2): an unreasoned classification.
        rows = dict(base)
        rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident, justification="")
        err = attempt(list(rows.values()), "no justification")
        assert "justification" in err, err
        cases += 1

        # (vi) condition (1): an act class outside the owner's closed enumeration.
        rows = dict(base)
        rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident, act_class="merge")
        err = attempt(list(rows.values()), "act class outside the enumeration")
        assert "act_class" in err, err
        cases += 1

        # (vii) condition (5) is an ALLOWLIST: ONLY an explicitly pending row may be
        # deferred. The probe deliberately reaches OUTSIDE the old {FAIL, BLOCKED}
        # denylist, because a denylist certifies only the values it enumerated. The
        # unbounded case is UNVERIFIABLE -- schema-valid, validator-valid, and reachable
        # through a clean registry with green CI: the independent verifier stating it
        # COULD NOT verify the obligation must never read as permission to defer it.
        for st in ("UNVERIFIABLE", "FAIL", "BLOCKED", "fail", "blocked", "FAIL ",
                   "Pending", "pending ", "PASSED", "", "wat", None, 0, 1, False, True,
                   [], ["pending"], {}, {"state": "pending"}):
            rows = dict(base)
            rows["D-900-R002"] = vrow_lifecycle("D-900-R002", state=st, identity=ident)
            err = attempt(list(rows.values()), f"non-pending state {st!r}")
            assert "not an explicitly pending row" in err, f"state {st!r}: {err}"
            assert "Traceback" not in err, \
                f"state {st!r} must fail closed, never raise: {err}"
            cases += 1
        # ...and an ABSENT state key is refused rather than defaulted into deferral.
        row = vrow_lifecycle("D-900-R002", identity=ident)
        row.pop("state")
        rows = dict(base)
        rows["D-900-R002"] = row
        err = attempt(list(rows.values()), "absent state key")
        assert "not an explicitly pending row" in err, err
        cases += 1

        # (viii) condition (2): an undated attestation is not a point-in-time act.
        for ts in ("t", "", None, "2026-07-31", "2026-13-99T99:99:99+00:00"):
            rows = dict(base)
            rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident,
                                                classified_at=ts)
            err = attempt(list(rows.values()), f"undated attestation {ts!r}")
            assert "classified_at" in err, err
            cases += 1

        # (ix) condition (2): independence is case- and whitespace-insensitive.
        rows = dict(base)
        rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident,
                                            classified_by=" ORCHESTRATOR ")
        err = attempt(list(rows.values()), "re-spelled producer self-classification")
        assert "INDEPENDENT" in err, err
        cases += 1

        # (x) a MISSING verification row can never be deferred (no attestation exists).
        rows = [v for k, v in base.items() if k != "D-900-R002"]
        err = attempt(rows, "missing row")
        assert "missing rows" in err, err
        cases += 1

        # (xi) condition (6): the attestation must be BOUND to the identity the deferral
        # is granted at. THE SCENARIO THAT MATTERS is the first one: the RECORD is
        # refreshed to the current identity while the per-row attestation is carried
        # forward from an earlier review -- a judgment about content that is no longer
        # the content being accepted. Every near-miss keeps the row gating too: a
        # case-variant, a whitespace-padded variant, a truncation, an empty or
        # whitespace-only value, a non-string, and (below) an absent key.
        stale_identity = "b" * 64          # the identity an earlier review was made at
        for stamp in (stale_identity, ident.upper(), " " + ident, ident + " ", ident[:-1],
                      "", "   ", None, 7, [], {}, True):
            rows = dict(base)
            rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident,
                                                classified_at_identity=stamp)
            label = ("attestation carried forward from an earlier identity"
                     if stamp == stale_identity else f"classified_at_identity {stamp!r}")
            err = attempt(list(rows.values()), label)
            assert "classified_at_identity" in err, f"{stamp!r}: {err}"
            assert "not PASS" in err, f"{stamp!r} must fall back to ordinary gating: {err}"
            assert "Traceback" not in err, f"{stamp!r} must fail closed, never raise: {err}"
            cases += 1
        # ...and an attestation with NO identity stamp at all is refused, never defaulted
        # into deferral (this is the shape every attestation had before condition (6)).
        row = vrow_lifecycle("D-900-R002", identity=ident)
        row["lifecycle_classification"].pop("classified_at_identity")
        rows = dict(base)
        rows["D-900-R002"] = row
        err = attempt(list(rows.values()), "unstamped attestation")
        assert "classified_at_identity" in err, err
        cases += 1

        # POSITIVE CONTROL: with a well-formed attestation on the same fixture, accept
        # succeeds -- so every refusal above was caused by the broken condition, not by
        # some unrelated precondition of this fixture.
        rows = dict(base)
        rows["D-900-R002"] = vrow_lifecycle("D-900-R002", identity=ident)
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, list(rows.values()),
                              ident, head_of(tmp))
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, f"AS-2 positive control must accept: {r.stdout} {r.stderr}"
        cases += 1
        assert cases == 48, f"AS-2 executed {cases} cases, expected 48"
        print(f"OK: S11 unmet NON-lifecycle rows still block acceptance "
              f"(AS-2, {cases} cases incl. positive control)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_governance_identity_and_dirt_guards() -> None:
    """AS-5 + AS-6: a governance-shaped task gets a REAL staleness identity and a REAL
    dirt guard where both previously compared a constant with itself."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-ident-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T342"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        report_md = tmp / allowed[1]
        tpath = pc / "tasks" / f"{tid}.json"

        # (a) the OLD guard was provably vacuous for exactly this shape.
        old_ident, old_entries, err = _dr.git_tree_manifest(tmp, head, allowed,
                                                            exclude_prefixes=_CP)
        assert err is None and old_entries == [] and old_ident == EMPTY_SET_IDENTITY, \
            "the pre-fix identity for a governance-shaped scope was the empty-set hash"
        old_dirty, err = _dr.relevant_working_tree_dirty(tmp, allowed, exclude_prefixes=_CP)
        assert err is None and old_dirty == [], "the pre-fix dirt guard dropped every candidate"

        # (b) the NEW identity is a real 2-entry manifest.
        ident = gov_identity(tmp, allowed, head)
        assert ident != EMPTY_SET_IDENTITY
        entries, err = _dr.control_plane_entries(tmp, head, allowed, _CP)
        assert err is None and len(entries) == 2, entries

        # (c) AS-6: a DIRTY file in scope is now DETECTED and fails accept closed.
        rows = [vrow_pass(r) for r in _S11_RIDS]
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, head_of(tmp))
        original_md = report_md.read_text(encoding="utf-8")
        report_md.write_text("uncommitted edit\n", encoding="utf-8")
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "dirty" in r.stderr.lower(), \
            f"AS-6 a dirty control-plane file must fail closed: {r.stderr}"
        assert allowed[1] in r.stderr, f"the refusal must name the file: {r.stderr}"
        report_md.write_text(original_md, encoding="utf-8")

        # (d) AS-6: a MATERIAL uncommitted packet edit is dirt; a LIFECYCLE-only one is
        # not (the control plane rewrites lifecycle fields on every transition, so a
        # literal dirt rule would deadlock every acceptance).
        t = read_json(tpath)
        edit_task(tmp, tid, objective="materially different objective")
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "dirty" in r.stderr.lower(), \
            f"AS-6 a material packet edit must fail closed: {r.stderr}"
        edit_task(tmp, tid, objective=t["objective"], progress_percent=86)
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, \
            f"a lifecycle-only packet delta must NOT be dirt: {r.stdout} {r.stderr}"

        # (e) AS-6: an UNTRACKED file inside allowed_paths fails closed.
        extra = f"project-control/reports/{tid}-extra.md"
        edit_task(tmp, tid, allowed_paths=allowed + [extra], status="awaiting_gate")
        head2 = git_commit_all(tmp, "widen allowed_paths")
        (tmp / extra).write_text("untracked evidence\n", encoding="utf-8")
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "dirty or untracked" in r.stderr, \
            f"AS-6 an untracked file in scope must fail closed: {r.stderr}"
        (tmp / extra).unlink()
        edit_task(tmp, tid, allowed_paths=allowed)
        head2 = git_commit_all(tmp, "restore allowed_paths")

        # (f) AS-5: a COMMITTED change to a file inside allowed_paths MOVES the identity,
        # so the frozen evidence goes stale and acceptance is refused.
        ident_before = gov_identity(tmp, allowed, head_of(tmp))
        report_md.write_text("REVISED report body\n", encoding="utf-8")
        head3 = git_commit_all(tmp, "edit the report in scope")
        ident_after = gov_identity(tmp, allowed, head3)
        assert ident_after != ident_before, \
            "AS-5 a committed in-scope change must move the identity"
        edit_task(tmp, tid, status="awaiting_gate")
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident_after, head3)
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "frozen-evidence identity mismatch" in r.stderr, \
            f"AS-5 a moved identity must make the frozen evidence stale: {r.stderr}"

        # (g) AS-5: a MATERIAL packet amendment also moves it; a LIFECYCLE-ONLY packet
        # change deliberately does NOT. The recorded resolution, proven both ways.
        base_sha = git_commit_all(tmp, "settle")
        id0 = gov_identity(tmp, allowed, base_sha)
        edit_task(tmp, tid, objective="a materially amended objective")
        sha_material = git_commit_all(tmp, "material amendment")
        assert gov_identity(tmp, allowed, sha_material) != id0, \
            "AS-5 a material packet amendment must move the identity"
        id1 = gov_identity(tmp, allowed, sha_material)
        before_packet = read_json(tpath)
        edit_task(tmp, tid, status="rework", progress_percent=60)
        sha_lifecycle = git_commit_all(tmp, "lifecycle-only transition")
        after_packet = read_json(tpath)
        differing = {k for k in set(before_packet) | set(after_packet)
                     if before_packet.get(k) != after_packet.get(k)}
        assert differing <= {"status", "progress_percent", "updated_at"}, \
            f"the probe must be lifecycle-only, differing keys were {sorted(differing)}"
        assert _dr.material_digest(before_packet) == _dr.material_digest(after_packet)
        assert gov_identity(tmp, allowed, sha_lifecycle) == id1, \
            ("a lifecycle-only packet change must NOT read as content staleness -- "
             "including it would make every acceptance structurally impossible")
        print("OK: S11 governance-shaped staleness identity + dirt guard (AS-5, AS-6)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_reviewed_sha_compared_and_no_regression() -> None:
    """AS-7 + AS-8: reviewed_sha is ACTUALLY compared and fails closed when stale, and
    nothing outside the control-plane tree changes value or behavior."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-sha-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T343"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        ident = gov_identity(tmp, allowed, head)
        rows = [vrow_pass(r) for r in _S11_RIDS]

        # (a) a STALE reviewed_sha fails closed (this comparison did not exist before).
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, "0" * 40)
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "reviewed_sha is stale" in r.stderr, \
            f"AS-7 a stale reviewed_sha must fail closed: {r.stderr}"

        # (b) an ABSENT reviewed_sha fails closed too (no silent skip).
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, None)
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "reviewed_sha is stale" in r.stderr, \
            f"AS-7 an absent reviewed_sha must fail closed: {r.stderr}"

        # (c) the matching reviewed_sha accepts.
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, head_of(tmp))
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, f"AS-7 a matching reviewed_sha must accept: {r.stderr}"

        # (d) AS-8: a scope with NO control-plane paths keeps its pre-existing identity
        # value exactly -- the raw-blob manifest, byte for byte.
        (tmp / "probe.txt").write_text("p\n", encoding="utf-8")
        sha = git_commit_all(tmp, "probe")
        raw, _e, err = _dr.git_tree_manifest(tmp, sha, ["probe.txt"], exclude_prefixes=_CP)
        assert err is None
        assert gov_identity(tmp, ["probe.txt"], sha) == raw, \
            "AS-8 an ordinary scope's identity value is unchanged by this task"

        # (e) AS-8: stored history is not retro-rejected and the accepted task is terminal.
        r = run(tmp, "status")
        assert r.returncode == 0 and json.loads(r.stdout)["task_counts"].get("accepted") == 1
        r = run(tmp, "progress", "--task-id", tid, "--agent", "x", "--percent", "50",
                "--message", "m")
        assert r.returncode != 0 and "terminal" in r.stderr

        # (f) AS-8: a checkpoint with no registered deferrals still works unchanged.
        r = run(tmp, "checkpoint", "--checkpoint-id", "cp-plain", "--commit", "c",
                "--branch", "b", "--summary", "s")
        assert r.returncode == 0, f"AS-8 an ordinary checkpoint is unaffected: {r.stderr}"
        cp = read_json(pc / "checkpoints" / "cp-plain.json")
        assert "post_accept_verifications_confirmed" not in cp
        print("OK: S11 reviewed_sha comparison + no-regression (AS-7, AS-8)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_deferral_is_not_waiver_at_the_first_post_accept_opportunity() -> None:
    """AS-1/AS-4 hardened: DEFERRAL IS NOT WAIVER must be true IN CODE. Discharging a
    deferred acceptance-ordering row demands the SAME standards as the gate that deferred
    it -- independent verifier, the deferral's content identity, and its reviewed commit
    -- so a deferred obligation is never held to a LOWER bar than an ordinary one. The
    obligation is also re-derived from the registry, so deleting the packet record does
    not erase it."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-waiver-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T344"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        ident = gov_identity(tmp, allowed, head)
        vpath = pc / "directives" / "D-900-gov" / "verification.json"
        tpath = pc / "tasks" / f"{tid}.json"

        rows = [vrow_pass(r) for r in _S11_RIDS]
        rows[1] = vrow_lifecycle("D-900-R002", identity=ident)   # the one deferred row
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, head_of(tmp))
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, f"the fixture must accept with one deferral: {r.stderr}"
        dfr = read_json(tpath)["post_accept_verification"]["deferred_requirements"][0]
        assert dfr["requirement_id"] == "D-900-R002"

        def rewrite(mutate):
            v = read_json(vpath)
            tv = v["task_verifications"][0]
            row = [x for x in tv["requirements"] if x["id"] == "D-900-R002"][0]
            mutate(tv, row)
            vpath.write_text(json.dumps(v, indent=2), encoding="utf-8")

        def cp(label, cid="cpx"):
            r_ = run(tmp, "checkpoint", "--checkpoint-id", cid, "--commit", "c",
                     "--branch", "b", "--summary", "s")
            return r_

        attempts = 0
        # (a) THE DEFECT: a bare PASS, with NO independent verifier, discharged the row.
        def _bare_pass(tv, row):
            row["state"] = "PASS"
            tv["verifier"] = ""
        rewrite(_bare_pass)
        r = cp("bare PASS")
        assert r.returncode != 0 and "no independent verifier" in r.stderr, \
            f"a bare PASS must NOT discharge a deferral: {r.stderr}"
        assert "NOT discharged" in r.stderr, r.stderr
        attempts += 1

        # (b) the PRODUCER cannot discharge its own deferral, however it re-spells itself.
        rewrite(lambda tv, row: tv.__setitem__("verifier", " ORCHESTRATOR "))
        r = cp("producer self-discharge")
        assert r.returncode != 0 and "equals producer" in r.stderr, r.stderr
        attempts += 1

        # (c) a discharge recorded at ANOTHER content identity is refused.
        def _other_identity(tv, row):
            tv["verifier"] = "reviewer-v"
            tv["reviewed_manifest_sha256"] = "f" * 64
        rewrite(_other_identity)
        r = cp("other identity")
        assert r.returncode != 0 and "content identity" in r.stderr, r.stderr
        attempts += 1

        # (d) a discharge recorded at ANOTHER reviewed commit is refused.
        def _other_sha(tv, row):
            tv["reviewed_manifest_sha256"] = dfr["deferred_at_identity"]
            tv["reviewed_sha"] = "0" * 40
        rewrite(_other_sha)
        r = cp("other reviewed commit")
        assert r.returncode != 0 and "reviewed commit" in r.stderr, r.stderr
        attempts += 1

        # (e) DELETING the verification row does not discharge the obligation.
        def _delete_row(tv, row):
            tv["reviewed_sha"] = dfr["deferred_at_sha"]
            tv["requirements"] = [x for x in tv["requirements"] if x["id"] != "D-900-R002"]
        rewrite(_delete_row)
        r = cp("deleted row")
        assert r.returncode != 0 and "no verification row" in r.stderr, r.stderr
        attempts += 1

        # (f) a PROPER discharge -- independent verifier, same identity, same commit,
        # PASS -- does proceed. The positive control for (a)-(e).
        v = read_json(vpath)
        tv = v["task_verifications"][0]
        tv["verifier"] = "reviewer-v"
        tv["reviewed_manifest_sha256"] = dfr["deferred_at_identity"]
        tv["reviewed_sha"] = dfr["deferred_at_sha"]
        tv["requirements"] = [x for x in tv["requirements"] if x["id"] != "D-900-R002"] + [
            {"id": "D-900-R002", "state": "PASS", "evidence": ["post-accept"],
             "verified_by": "reviewer-v",
             "lifecycle_classification": vrow_lifecycle("D-900-R002", identity=ident)[
                 "lifecycle_classification"]}]
        vpath.write_text(json.dumps(v, indent=2), encoding="utf-8")
        r = cp("proper discharge", cid="cp-ok")
        assert r.returncode == 0, f"a properly standard discharge must proceed: {r.stderr}"
        attempts += 1

        # (g) RE-DERIVATION: put the row back to pending and DELETE the packet's deferral
        # record entirely. The obligation lives in the registry too, so erasing the single
        # mutable packet key does not erase it.
        rewrite(lambda tv_, row_: row_.__setitem__("state", "pending"))
        t = read_json(tpath)
        t.pop("post_accept_verification")
        tpath.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
        assert "post_accept_verification" not in read_json(tpath)
        r = cp("packet record deleted", cid="cp-rederived")
        assert r.returncode != 0, "deleting the packet key must NOT discharge the obligation"
        assert "re-derived from the registry" in r.stderr, r.stderr
        assert "D-900-R002" in r.stderr, r.stderr
        attempts += 1

        # (h) the re-derived obligation closes the same way an ordinary one does.
        rewrite(lambda tv_, row_: row_.__setitem__("state", "PASS"))
        r = cp("re-derived then satisfied", cid="cp-rederived")
        assert r.returncode == 0, f"a satisfied re-derived claim must proceed: {r.stderr}"
        attempts += 1

        # (i) an UNVERIFIABLE post-accept verdict is not a discharge either.
        rewrite(lambda tv_, row_: row_.__setitem__("state", "UNVERIFIABLE"))
        r = cp("unverifiable", cid="cp-unver")
        assert r.returncode != 0 and "re-derived from the registry" in r.stderr, r.stderr
        attempts += 1
        rewrite(lambda tv_, row_: row_.__setitem__("state", "PASS"))

        assert attempts == 9, f"executed {attempts} discharge cases, expected 9"
        print(f"OK: S11 deferral is not waiver -- post-accept discharge held to the gate's "
              f"own standard ({attempts} cases incl. positive control)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_missing_producer_identity_fails_closed() -> None:
    """An EMPTY producer silently disabled BOTH the pre-existing verifier-independence
    check and the classifier's independent-attestation condition: `x and y == x` is never
    true when x is empty. Independence that cannot be evaluated must refuse."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-producer-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        tid = "M9-T345"
        make_directive(pc, "D-900", "gov", task_ids=[tid], task_types=[], milestones=[],
                       req_specs=_S11_REQ_SPECS(tid))
        head, allowed = build_governance_task(tmp, tid, "D-900", "gov", _S11_RIDS)
        ident = gov_identity(tmp, allowed, head)
        vpath = pc / "directives" / "D-900-gov" / "verification.json"
        rpath = pc / "directives" / "D-900-gov" / "requirements.json"
        rows = [vrow_pass(r) for r in _S11_RIDS]

        def blank_producers():
            """Blank the producer EVERYWHERE the resolver looks for it."""
            v = read_json(vpath)
            v["producer"] = ""
            v["task_verifications"][0]["producer"] = ""
            vpath.write_text(json.dumps(v, indent=2), encoding="utf-8")
            rq = read_json(rpath)
            rq["producer"] = ""
            rpath.write_text(json.dumps(rq, indent=2), encoding="utf-8")

        # (a) all rows PASS, but the verifier could be anyone: with no producer identity
        # the independence check is unevaluable and must refuse, not pass silently.
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows, ident, head_of(tmp))
        blank_producers()
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0 and "no producer identity" in r.stderr, \
            f"an unknown producer must fail closed: {r.stderr}"
        assert read_json(pc / "tasks" / f"{tid}.json")["status"] == "awaiting_gate"

        # (b) the same emptiness must not let a producer classify its own row either:
        # the verification's verifier IS the classifier, and nothing distinguishes them.
        rows2 = [vrow_pass(r_) for r_ in _S11_RIDS]
        rows2[1] = vrow_lifecycle("D-900-R002", identity=ident,
                                  classified_by="reviewer-v")
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows2, ident,
                              head_of(tmp), verifier="reviewer-v")
        blank_producers()
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode != 0, "a self-classified row under an unknown producer must refuse"
        assert "no producer identity" in r.stderr, r.stderr
        assert "post_accept_verification" not in read_json(pc / "tasks" / f"{tid}.json")

        # (c) positive control: restore the producer and the SAME fixture accepts.
        write_v2_verification(pc, "D-900", "gov", tid, _S11_RIDS, rows2, ident,
                              head_of(tmp))
        r = run(tmp, "accept", "--task-id", tid, "--agent", "orchestrator")
        assert r.returncode == 0, f"positive control must accept: {r.stdout} {r.stderr}"
        print("OK: S11 an unknown producer identity fails closed (independence is never inert)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s11_no_special_casing_source_proofs() -> None:
    """AS-3 + AS-12: the lifecycle mechanism is derived from row semantics only -- no
    task-id allowlist, no bypass flag, no environment override -- and its rule is
    STATED IN THE CODE. Matches the standard set by invalid_unblock_roster."""
    tmpdir = tempfile.mkdtemp(prefix="pc-s11-general-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        src = (HERE / "project_control.py").read_text(encoding="utf-8")
        reg_src = (HERE / "directive_registry.py").read_text(encoding="utf-8")
        names = ("_directive_accept_reasons", "_post_accept_verification_blockers",
                 "_confirmed_post_accept_verifications", "accept", "checkpoint",
                 "_task_git_identity")
        bodies = {}
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.FunctionDef) and node.name in names:
                body = list(node.body)
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    body = body[1:]  # strip docstring: prose provenance stays allowed
                bodies[node.name] = "\n".join(ast.unparse(s) for s in body)
        assert set(bodies) == set(names), f"missing functions: {sorted(set(names) - set(bodies))}"
        code = "\n".join(bodies[n] for n in names)
        assert not re.search(r"M\d+-T\d{3}", code), \
            f"lifecycle/identity code must name no ledger task id:\n{code}"
        assert not re.search(r"D-\d{3}-R\d{3}", code), \
            f"lifecycle/identity code must name no specific requirement id:\n{code}"
        for tok in ("getenv", "environ", "force", "bypass", "override", "allowlist"):
            assert tok not in code.lower(), f"code must carry no {tok!r} token:\n{code}"
        assert "os.environ" not in src and "getenv" not in src, \
            "project_control.py must never read the environment"
        # the eight candidate rows are the INDEPENDENT verifier's call (AS-10): neither
        # module may name one and thereby pre-classify it.
        for rid in ("D-004-R322", "D-004-R323", "D-004-R388", "D-004-R389",
                    "D-004-R486", "D-004-R487", "D-004-R488", "D-004-R501"):
            assert rid not in src and rid not in reg_src, \
                f"{rid} must not be named in the implementation"
        assert "M0-T027" not in src and "M0-T027" not in reg_src, \
            "the correction must not name the motivating task"
        # AS-12: the rule is stated where a reviewer will read it.
        assert "ACCEPTANCE-ORDERING LIFECYCLE CLASSIFICATION" in reg_src
        assert "no special-cased task id, no flag, and no environment override" in reg_src
        assert "LIFECYCLE-AWARE ACCEPTANCE" in src and "CONTROL-PLANE CONTENT IDENTITY" in src
        # accept and checkpoint gain NO new option: no flag, no override, no bypass.
        r = run(tmp, "accept", "-h")
        assert r.returncode == 0
        assert set(re.findall(r"--[a-z][a-z0-9-]*", r.stdout)) == {"--help", "--task-id",
                                                                   "--agent"}, r.stdout
        r = run(tmp, "checkpoint", "-h")
        assert r.returncode == 0
        assert set(re.findall(r"--[a-z][a-z0-9-]*", r.stdout)) == {
            "--help", "--checkpoint-id", "--commit", "--branch", "--summary"}, r.stdout
        print("OK: S11 no special-casing; classification rule stated in code (AS-3, AS-12)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_s12_empty_identity_guard() -> None:
    """D-011 item 6 / M0-T057: the shared submit/gate/accept identity path (_task_git_identity)
    refuses an in-regime task whose allowed_paths resolve to ZERO tracked files (which would
    otherwise stamp the empty-set content identity, binding no code). A real pathspec still
    stamps a real identity."""
    tmpdir = tempfile.mkdtemp(prefix="pc-empty-ident-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        setup_regime(tmp)
        pc = tmp / "project-control"
        (tmp / "probe.txt").write_text("content\n", encoding="utf-8")
        make_directive(pc, "D-900", "example", task_ids=["M9-T900"], task_types=[],
                       milestones=[], req_specs=[("D-900-R001", ["M9-T900"])])
        run(tmp, "new-task", "--task-id", "M9-T900", "--title", "t", "--task-type", "research",
            "--milestone", "M0", "--objective", "o", "--gates", "G0,G3",
            "--reviewers", "reviewer-v,reviewer-z", "--directive-refs", "D-900:ALL")

        # (a) positive control: a real pathspec stamps a real (non-empty) identity.
        edit_task(tmp, "M9-T900", allowed_paths=["probe.txt"])
        git_commit_all(tmp, "commit probe + real allowed_paths")
        write_report(tmp, "g0.json", '{"g":0}')
        r = run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer",
                "orchestrator", "--result", "PASS", "--report", "project-control/reports/g0.json")
        assert r.returncode == 0, f"a real pathspec must gate cleanly: {r.stdout} {r.stderr}"
        rec = read_json(pc / "gates" / "M9-T900-G0.json")
        assert rec.get("content_manifest_sha256") not in (None, _dr.EMPTY_MANIFEST_IDENTITY), \
            "the stamped identity must be a real manifest hash, not the empty-set hash"

        # (b) PROSE allowed_paths (git matches them literally -> nothing) fail closed.
        edit_task(tmp, "M9-T900", allowed_paths=["apps/web/src/** (survey review feature areas)"])
        git_commit_all(tmp, "prose allowed_paths")
        r = run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer",
                "orchestrator", "--result", "PASS", "--report", "project-control/reports/g0.json")
        assert r.returncode != 0 and "ZERO tracked files" in (r.stdout + r.stderr), \
            f"prose allowed_paths must fail the identity closed: {r.stdout} {r.stderr}"

        # (c) a MALFORMED path-free opt-in (marker without justification) fails closed too.
        edit_task(tmp, "M9-T900", path_free_governance=True)  # no path_free_justification
        git_commit_all(tmp, "malformed opt-in")
        r = run(tmp, "gate", "--task-id", "M9-T900", "--gate-id", "G0", "--reviewer",
                "orchestrator", "--result", "PASS", "--report", "project-control/reports/g0.json")
        assert r.returncode != 0 and "path_free_justification" in (r.stdout + r.stderr), \
            f"a half-declared opt-in must fail closed: {r.stdout} {r.stderr}"
        print("OK: S12 empty-identity guard (prose + malformed opt-in fail closed; real path stamps real identity)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


ALL_TESTS = [
    test_original_workflow,
    test_s1_transitions,
    test_s2_accept_preconditions,
    test_s3_gate_classes,
    test_s4_containment,
    test_s5_atomicity,
    test_s6_spoofing,
    test_s7_backward_compatibility,
    test_s8_hardening_followup,
    test_s10_governance_orchestrator_unblock,
    test_docs_honesty,
    test_s9_directive_claim_and_governance,
    test_s9_submit_evidence_and_git_identity,
    test_s9_accept_requires_per_task_verification,
    test_s9_regime_bypass_closed_and_migration,
    test_s11_lifecycle_aware_acceptance_and_post_accept_verification,
    test_s11_non_lifecycle_rows_still_block_acceptance,
    test_s11_governance_identity_and_dirt_guards,
    test_s11_reviewed_sha_compared_and_no_regression,
    test_s11_deferral_is_not_waiver_at_the_first_post_accept_opportunity,
    test_s11_missing_producer_identity_fails_closed,
    test_s11_no_special_casing_source_proofs,
    test_s12_empty_identity_guard,
]


if __name__ == "__main__":
    for fn in ALL_TESTS:
        fn()
    print(f"OK: all {len(ALL_TESTS)} project-control test groups passed")
