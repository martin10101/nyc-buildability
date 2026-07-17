"""Stdlib regression test for the B-007 agent dispatch guard (owner directive 2026-07-17).

Proves, per the owner's acceptance requirement:
  1. every one of the five expansion agents is REJECTED (exit 2) with a
     B-007/conformance-required message while B-007 is open;
  2. an unrelated accepted roster agent (code-reviewer) remains dispatchable (exit 0);
  3. enforcement lifts automatically when B-007 status != open (exit 0);
  4. absent blocker file (lifecycle complete) allows (exit 0);
  5. corrupted blocker file fails CLOSED for the five names (exit 2);
  6. malformed hook input never breaks tooling (exit 0).

Run: python tools/test_agent_dispatch_guard.py   (also wired into the CI control-plane job)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / ".claude" / "hooks" / "agent_dispatch_guard.py"
BLOCKER_REL = Path("project-control/blockers/B-007-expansion-agent-conformance.json")

FIVE = [
    "3d-massing-engineer",
    "product-design-director",
    "visual-quality-reviewer",
    "financial-feasibility-engineer",
    "opportunity-search-engineer",
]

FAILURES = []


def run_guard(stdin_text: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD)],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=30,
    )


def check(name: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"{status}  {name}" + (f"  [{detail}]" if detail and not condition else ""))
    if not condition:
        FAILURES.append(f"{name}: {detail}")


def hook_payload(agent: str, cwd: Path) -> str:
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Agent",
            "tool_input": {"subagent_type": agent, "prompt": "test", "description": "test"},
            "cwd": str(cwd),
        }
    )


def make_root(blocker_status) -> Path:
    """Create an isolated fake project root; blocker_status None = no blocker file,
    'CORRUPT' = unparseable file, else the given status string."""
    root = Path(tempfile.mkdtemp(prefix="guardtest-"))
    if blocker_status is not None:
        target = root / BLOCKER_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        if blocker_status == "CORRUPT":
            target.write_text("{ not json", encoding="utf-8")
        else:
            target.write_text(
                json.dumps({"blocker_id": "B-007", "status": blocker_status}),
                encoding="utf-8",
            )
    return root


def main() -> int:
    roots = []

    # 1. All five rejected while open, with the required message content.
    root_open = make_root("open")
    roots.append(root_open)
    for agent in FIVE:
        r = run_guard(hook_payload(agent, root_open))
        check(
            f"open blocker rejects {agent}",
            r.returncode == 2 and "B-007" in r.stderr and "conformance" in r.stderr.lower(),
            f"exit={r.returncode} stderr={r.stderr[:120]!r}",
        )

    # 2. Unrelated accepted roster agent remains dispatchable while open.
    r = run_guard(hook_payload("code-reviewer", root_open))
    check("open blocker allows code-reviewer", r.returncode == 0 and r.stderr == "",
          f"exit={r.returncode} stderr={r.stderr[:120]!r}")

    # 3. Resolved blocker lifts enforcement for all five.
    root_resolved = make_root("resolved")
    roots.append(root_resolved)
    for agent in FIVE:
        r = run_guard(hook_payload(agent, root_resolved))
        check(f"resolved blocker allows {agent}", r.returncode == 0,
              f"exit={r.returncode} stderr={r.stderr[:120]!r}")

    # 4. Absent blocker file allows (lifecycle complete).
    root_absent = make_root(None)
    roots.append(root_absent)
    r = run_guard(hook_payload(FIVE[0], root_absent))
    check("absent blocker file allows", r.returncode == 0,
          f"exit={r.returncode} stderr={r.stderr[:120]!r}")

    # 5. Corrupted blocker file fails CLOSED for the five.
    root_corrupt = make_root("CORRUPT")
    roots.append(root_corrupt)
    r = run_guard(hook_payload(FIVE[0], root_corrupt))
    check("corrupt blocker file blocks (fail closed)", r.returncode == 2,
          f"exit={r.returncode}")

    # 6. Malformed stdin never breaks tooling.
    r = run_guard("this is not json")
    check("malformed input allows (exit 0)", r.returncode == 0, f"exit={r.returncode}")

    # 7. Live repo state: whatever B-007 currently says governs the five in THIS repo.
    live_blocker = REPO / BLOCKER_REL
    if live_blocker.exists():
        live_status = json.loads(live_blocker.read_text(encoding="utf-8")).get("status")
        r = run_guard(hook_payload(FIVE[0], REPO))
        expected = 2 if str(live_status).lower() == "open" else 0
        check(
            f"live repo blocker (status={live_status}) yields exit {expected}",
            r.returncode == expected,
            f"exit={r.returncode}",
        )

    for root in roots:
        shutil.rmtree(root, ignore_errors=True)

    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S)")
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
