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
      still satisfy acceptance - validation is write-time only.
  S8  M0-T016 hardening follow-up: (1) the reserved identity "orchestrator" is
      rejected in --reviewers at new-task and as --reviewer on an independent
      gate (even when a legacy packet lists it), while its legitimate G2
      self_check and G0/G7 administrative paths still work; (2) unknown --gates
      entries are rejected immediately, valid G0-G7 combinations accepted;
      (3) a blocked task with an empty/invalid producer/reviewer roster cannot
      transition out of blocked until the packet is amended, after which the
      unblock path works; canceling a blocked task is always allowed. No
      retro-rejection of stored ledger history.

Stdlib only. Run directly (`python tools/test_project_control.py`) or via
pytest. Exit code 0 = all assertions passed.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_PC = HERE.parent / "project-control"


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

        # every real ledger file still parses
        parsed = 0
        for jf in pc.rglob("*.json"):
            json.loads(jf.read_text(encoding="utf-8-sig"))
            parsed += 1
        assert parsed >= 60, f"expected the full ledger, parsed only {parsed} files"

        # status runs over the entire real roster
        r = run(tmp, "status")
        assert r.returncode == 0, f"status over real ledger failed: {r.stderr}"
        payload = json.loads(r.stdout)
        assert payload["task_counts"].get("accepted", 0) >= 21, \
            "the 21 accepted tasks must remain visible"

        # a write against a copied real task (message-only progress, which
        # also drives sync_state across all real task files) is not
        # retro-rejected by the new validation
        backlog = [t["id"] for t in payload["tasks"] if t["status"] == "backlog"]
        assert backlog, "expected at least one backlog task in the ledger copy"
        r = run(tmp, "progress", "--task-id", backlog[0], "--agent", "orchestrator",
                "--percent", "0", "--message", "backcompat regression probe")
        assert r.returncode == 0, f"message-only progress on real task failed: {r.stderr}"

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
              f"legacy records accepted; validation is write-time only)")
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
    test_docs_honesty,
]


if __name__ == "__main__":
    for fn in ALL_TESTS:
        fn()
    print(f"OK: all {len(ALL_TESTS)} project-control test groups passed")
