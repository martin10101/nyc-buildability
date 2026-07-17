"""PreToolUse dispatch guard for the five 3D/UI expansion-pack agents (B-007).

Owner decision 2026-07-17 (disposition A for M0-T010): the five expansion agents must be
PROGRAMMATICALLY blocked from dispatch — a rules warning and blocker document are not
enough — until conformance task M0-T013 is accepted and blocker B-007 is closed.

Wired in the tracked .claude/settings.json as a PreToolUse hook on the subagent dispatch
tools (Agent / Task). Reads the B-007 blocker JSON live on every dispatch, so enforcement
lifts automatically (without touching this script) when the orchestrator sets the blocker
status to anything other than "open" at M0-T013 acceptance.

Behavior:
- tool_input.subagent_type (or agent_type/agentType alias) in BLOCKED_AGENTS and B-007
  status == "open"  -> exit 2 (blocking error; stderr message returned to the model).
- anything else (other agents, blocker resolved, blocker file absent = lifecycle complete,
  malformed input) -> exit 0 (allow). Absence of the blocker file is treated as closed
  because B-007 is orchestrator-resolved by status change, never by deletion, while open.

Tests: tools/test_agent_dispatch_guard.py (stdlib; run locally and in the CI
control-plane job). Do not rename the five agent names or the blocker path without
updating the tests and B-007 itself.
"""
import json
import sys
from pathlib import Path

BLOCKED_AGENTS = frozenset(
    {
        "3d-massing-engineer",
        "product-design-director",
        "visual-quality-reviewer",
        "financial-feasibility-engineer",
        "opportunity-search-engineer",
    }
)

# Hook commands run with cwd = project root; keep a script-relative fallback for tests.
BLOCKER_RELPATH = Path("project-control/blockers/B-007-expansion-agent-conformance.json")


def blocker_is_open(project_root: Path) -> bool:
    blocker_file = project_root / BLOCKER_RELPATH
    if not blocker_file.exists():
        return False
    try:
        data = json.loads(blocker_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # Unreadable blocker state: fail CLOSED for the five names (safer to block
        # dispatch than to allow non-conformant agents on a corrupted ledger).
        return True
    return str(data.get("status", "")).strip().lower() == "open"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0  # not a hook invocation we understand; never break other tools
    tool_input = payload.get("tool_input") or {}
    requested = (
        tool_input.get("subagent_type")
        or tool_input.get("agent_type")
        or tool_input.get("agentType")
        or ""
    ).strip()
    if requested not in BLOCKED_AGENTS:
        return 0
    project_root = Path(payload.get("cwd") or ".").resolve()
    if not blocker_is_open(project_root):
        return 0
    sys.stderr.write(
        "DISPATCH BLOCKED by B-007 (owner directive 2026-07-17, G5 M0-T010): agent "
        f"'{requested}' is one of the five 3D/UI expansion-pack agents that MUST NOT be "
        "dispatched until conformance task M0-T013 is accepted and blocker "
        "project-control/blockers/B-007-expansion-agent-conformance.json is closed. "
        "Its definition lacks the ADR-005 protocol sections; dispatching it would allow "
        "non-orchestrator ledger writes. Conformance is required — do not retry, do not "
        "work around this guard."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
