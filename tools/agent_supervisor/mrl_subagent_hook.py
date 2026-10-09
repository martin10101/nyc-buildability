#!/usr/bin/env python3
"""PreToolUse/PostToolUse hook that runs INSIDE the restricted MRL child and asks the
controller-owned ``SubagentLedger`` whether one ``Agent``/``Task`` spawn may proceed
(M0-T136 C-B3; D-024-R567..R575).

Wired by ``mrl_subagent_contract.build_restricted_profile`` into the child's
``--settings`` profile (which ``--restricted`` still honours). The hook decides
nothing itself: it extracts the request, and the ledger applies the contract.
Conventions (repo precedent ``.claude/hooks/agent_dispatch_guard.py``): exit 2 +
stderr = deny. Unlike that guard, unparseable or unexpected input here is a DENY
(fail closed) - an MRL child never fans out on ambiguity.

Depth detection uses the measured hook-payload shape: the primary session carries
no ``agent_id``/``agent_type`` key, a spawned subagent does. A request that arrives
with either key is therefore depth 2 and is refused (R568).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

if __package__ in (None, ""):  # invoked by absolute path from the child's hook command
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from tools.agent_supervisor.mrl_subagent_contract import SubagentLedger  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

_DEPTH_KEYS = ("agent_id", "agent_type", "agentId", "agentType")


def _deny(reason: str) -> int:
    sys.stderr.write(f"MRL SUBAGENT DENIED: {reason}\n")
    return 2


def decide(payload: object, ledger: SubagentLedger, parent: str, event: str) -> int:
    if not isinstance(payload, dict):
        return _deny("hook payload is not a JSON object (fail closed)")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return _deny("hook payload has no tool_input object (fail closed)")
    if event == "post":
        try:
            ledger.release_latest_live()
        except ContractError as exc:
            sys.stderr.write(f"MRL SUBAGENT accounting warning: {exc}\n")
        return 0
    depth = 2 if any(k in payload for k in _DEPTH_KEYS) else 1
    subagent_type = str(tool_input.get("subagent_type") or tool_input.get("agent_type")
                        or tool_input.get("agentType") or "").strip()
    tool_name = str(payload.get("tool_name") or "")
    try:
        decision = ledger.request(
            parent_id=parent,
            subagent_type=subagent_type,
            description=str(tool_input.get("description") or "")[:200],
            depth=depth,
            background=bool(tool_input.get("run_in_background")),
            isolation=str(tool_input.get("isolation") or ""),
            mcp=tool_name.startswith("mcp__") or subagent_type.startswith("mcp__"),
        )
    except ContractError as exc:
        return _deny(f"ledger refused: {exc}")
    if not decision.allowed:
        return _deny(decision.reason)
    sys.stdout.write(json.dumps({"mrl_child_id": decision.child_id}) + "\n")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--parent", required=True)
    parser.add_argument("--event", choices=("pre", "post"), required=True)
    args = parser.parse_args(argv)
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return _deny("hook stdin is not valid JSON (fail closed)")
    return decide(payload, SubagentLedger(pathlib.Path(args.ledger)), args.parent, args.event)


if __name__ == "__main__":
    sys.exit(main())
