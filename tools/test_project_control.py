#!/usr/bin/env python3
"""Regression test for the project-control workflow (ADR-005).

Proves, against a disposable temp project (never the real ledger):
  1. a producer can claim, report progress, and submit work;
  2. a producer cannot set 100% and cannot gate its own task;
  3. a reviewer's report, recorded by the orchestrator, gates the task;
  4. a non-orchestrator cannot accept;
  5. orchestrator acceptance requires every required gate to PASS.

Stdlib only. Run directly (`python tools/test_project_control.py`) or via
pytest. Exit code 0 = all assertions passed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


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


def test_workflow() -> None:
    tmpdir = tempfile.mkdtemp(prefix="pc-regression-")
    tmp = Path(tmpdir)
    try:
        make_temp_project(tmp)
        pc = tmp / "project-control"

        r = run(tmp, "init")
        assert r.returncode == 0, f"init failed: {r.stderr}"

        r = run(tmp, "new-task", "--task-id", "T-1", "--title", "t", "--task-type",
                "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3")
        assert r.returncode == 0, f"new-task failed: {r.stderr}"

        # Orchestrator records G0 readiness (reviewer=orchestrator) -> ready
        ev = pc / "reports" / "T-1-g0.json"
        ev.parent.mkdir(exist_ok=True)
        ev.write_text('{"gate":"G0"}', encoding="utf-8")
        r = run(tmp, "gate", "--task-id", "T-1", "--gate-id", "G0",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", str(ev))
        assert r.returncode == 0, f"G0 gate failed: {r.stderr}"

        # 1. Producer claims, progresses, submits
        r = run(tmp, "claim", "--task-id", "T-1", "--agent", "producer-x", "--worktree", "wt")
        assert r.returncode == 0, f"claim failed: {r.stderr}"
        r = run(tmp, "progress", "--task-id", "T-1", "--agent", "producer-x",
                "--percent", "75", "--status", "self_check", "--message", "done")
        assert r.returncode == 0, f"progress failed: {r.stderr}"

        # 2a. Producer cannot set 100%
        r = run(tmp, "progress", "--task-id", "T-1", "--agent", "producer-x",
                "--percent", "100", "--message", "nope")
        assert r.returncode != 0, "producer setting 100% must be rejected"

        rep = pc / "reports" / "T-1-producer.json"
        rep.write_text('{"evidence":"outputs embedded"}', encoding="utf-8")
        r = run(tmp, "submit", "--task-id", "T-1", "--agent", "producer-x",
                "--report", str(rep), "--requested-status", "awaiting_gate")
        assert r.returncode == 0, f"submit failed: {r.stderr}"

        # 2b. Producer cannot gate its own task
        r = run(tmp, "gate", "--task-id", "T-1", "--gate-id", "G3",
                "--reviewer", "producer-x", "--result", "PASS", "--report", str(rep))
        assert r.returncode != 0, "producer gating own task must be rejected"

        # 3. Reviewer returns a report (write needs no CLI); orchestrator records it
        review = pc / "reports" / "T-1-g3-review.json"
        review.write_text('{"verdict":"PASS","reviewer":"reviewer-y"}', encoding="utf-8")
        r = run(tmp, "gate", "--task-id", "T-1", "--gate-id", "G3",
                "--reviewer", "reviewer-y", "--result", "PASS", "--report", str(review))
        assert r.returncode == 0, f"reviewer gate failed: {r.stderr}"

        # 4. Non-orchestrator cannot accept
        r = run(tmp, "accept", "--task-id", "T-1", "--agent", "reviewer-y")
        assert r.returncode != 0, "non-orchestrator accept must be rejected"

        # 5a. Acceptance blocked while a required gate is missing: new task w/ extra gate
        r = run(tmp, "new-task", "--task-id", "T-2", "--title", "t2", "--task-type",
                "research", "--milestone", "M0", "--objective", "o", "--gates", "G0,G3,G5")
        assert r.returncode == 0
        r = run(tmp, "gate", "--task-id", "T-2", "--gate-id", "G0",
                "--reviewer", "orchestrator", "--result", "PASS", "--report", str(ev))
        assert r.returncode == 0
        r = run(tmp, "accept", "--task-id", "T-2", "--agent", "orchestrator")
        assert r.returncode != 0, "accept with missing required gates must be rejected"

        # 5b. Orchestrator acceptance succeeds when all gates PASS
        r = run(tmp, "accept", "--task-id", "T-1", "--agent", "orchestrator")
        assert r.returncode == 0, f"orchestrator accept failed: {r.stderr}"
        task = json.loads((pc / "tasks" / "T-1.json").read_text(encoding="utf-8-sig"))
        assert task["status"] == "accepted" and task["progress_percent"] == 100

        # state sync regression (bootstrap defect #2)
        state = json.loads((pc / "state.json").read_text(encoding="utf-8-sig"))
        assert "T-1" in state["accepted_tasks"], "sync_state must roster accepted tasks"

        # BOM tolerance regression (bootstrap defect #1)
        bom_rep = pc / "reports" / "T-2-bom.json"
        bom_rep.write_bytes(b'\xef\xbb\xbf{"gate":"G3"}')
        r = run(tmp, "gate", "--task-id", "T-2", "--gate-id", "G3",
                "--reviewer", "reviewer-y", "--result", "PASS", "--report", str(bom_rep))
        assert r.returncode == 0, f"BOM report must be tolerated: {r.stderr}"

        # gate history regression (bootstrap defect #3)
        r = run(tmp, "gate", "--task-id", "T-2", "--gate-id", "G3",
                "--reviewer", "reviewer-z", "--result", "FAIL", "--report", str(bom_rep))
        assert r.returncode == 0
        gate_rec = json.loads((pc / "gates" / "T-2-G3.json").read_text(encoding="utf-8-sig"))
        assert gate_rec["result"] == "FAIL" and gate_rec["history"][0]["result"] == "PASS", \
            "gate records must preserve history"

        print("OK: all project-control workflow regressions passed")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    test_workflow()
