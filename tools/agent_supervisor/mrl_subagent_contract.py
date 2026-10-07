#!/usr/bin/env python3
"""MRL bounded-subagent contract and restricted CLI profile
(M0-T136 Tranche B cluster C-B3; D-024-R566..R579).

Subagents are NOT permanently forbidden. Instead the controller issues a
``SubagentContract`` for the run and enforces it with THREE real mechanisms
that survive ``--restricted`` (which ignores user/project/local settings but
still applies ``--settings``):

1. **Controller-owned accounting** (``SubagentLedger``, a locked JSON file): every
   child gets a controller-issued id bound to its parent id; per-run concurrent
   and total limits, delegation depth one, foreground only, out-of-inventory and
   MCP denial are decided HERE, not by the model. The child's hook
   (``mrl_subagent_hook``) only asks the ledger and relays the answer.
2. **A restricted profile** composed from the real CLI mechanisms measured on
   Claude Code 2.1.252 (F14): ``--restricted``, ``--permission-mode dontAsk``,
   an explicit ``--tools`` inventory, exact ``--allowedTools``/
   ``--disallowedTools`` rules, ``--strict-mcp-config`` with NO MCP config, and a
   ``--settings`` profile carrying the accounting hooks and the same permission
   rules. ``--tools`` alone grants nothing: it is an inventory, and ``dontAsk``
   denies whatever the exact allow rules do not name (``effective_grants``).
3. **Managed policy accounting**: the managed settings file, present or absent,
   is hashed into the settings-profile identity the launch manifest pins
   (R559/R577), so an unaccounted managed policy changes the identity.

Whether the live CLI honours every flag exactly as modelled is proven only by
the owner-run Windows canary (R579); nothing here claims live capability.
Import direction: ``mrl_worker_result`` only; nothing imports back.
"""
from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import json
import os
import pathlib
import sys
import time
from typing import Any, Iterator, Mapping, Sequence

from .mrl_worker_result import ContractError

LEDGER_SCHEMA = "mrl_subagent_ledger/v1"
PROFILE_SCHEMA = "mrl_restricted_profile/v1"
MAX_DEPTH = 1
WRITER_POLICIES = ("single-writer",)   # "isolated-worktrees" is NOT implemented in Tranche B: refused.
_LOCK_TIMEOUT_S = 5.0


def _violation(message: str) -> ContractError:
    return ContractError("contract_violation", message)


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _violation(f"{label} must be a non-negative int, got {value!r}")
    return value


# ---------------------------------------------------------------- contract

@dataclasses.dataclass(frozen=True)
class SubagentContract:
    """Per-run subagent limits plus the identity every child inherits."""

    run_id: str
    task_id: str
    repo_root: str
    allowed_paths: tuple[str, ...]
    tools_inventory: tuple[str, ...]          # exact built-in tool names the child may see at all
    agent_inventory: tuple[str, ...]          # subagent types the child may spawn (nothing else)
    max_concurrent: int
    max_total: int
    writer_policy: str = "single-writer"
    max_depth: int = MAX_DEPTH
    foreground_only: bool = True

    def __post_init__(self) -> None:
        for label, value in (("run_id", self.run_id), ("task_id", self.task_id), ("repo_root", self.repo_root)):
            if not isinstance(value, str) or not value.strip():
                raise _violation(f"contract {label} is required")
        _positive_int(self.max_concurrent, "max_concurrent")
        _positive_int(self.max_total, "max_total")
        if self.max_concurrent > self.max_total:
            raise _violation("max_concurrent cannot exceed max_total")
        if self.max_depth != MAX_DEPTH:
            raise _violation(f"delegation depth is fixed at {MAX_DEPTH} (R568); got {self.max_depth}")
        if self.foreground_only is not True:
            raise _violation("subagents are foreground-only (R569)")
        if self.writer_policy not in WRITER_POLICIES:
            raise _violation(f"writer_policy {self.writer_policy!r} is not implemented; "
                             f"Tranche B supports {WRITER_POLICIES} only (R572)")
        if any(not isinstance(p, str) or not p for p in self.allowed_paths):
            raise _violation("allowed_paths must be non-empty strings")
        if any(not isinstance(t, str) or not t for t in self.tools_inventory):
            raise _violation("tools_inventory must be non-empty strings")

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "SubagentContract":
        try:
            return cls(
                run_id=raw["run_id"], task_id=raw["task_id"], repo_root=raw["repo_root"],
                allowed_paths=tuple(raw["allowed_paths"]), tools_inventory=tuple(raw["tools_inventory"]),
                agent_inventory=tuple(raw.get("agent_inventory", ())),
                max_concurrent=raw["max_concurrent"], max_total=raw["max_total"],
                writer_policy=raw.get("writer_policy", "single-writer"),
                max_depth=raw.get("max_depth", MAX_DEPTH), foreground_only=raw.get("foreground_only", True),
            )
        except (KeyError, TypeError) as exc:
            raise _violation(f"malformed subagent contract: {exc!r}") from exc


# ---------------------------------------------------------------- ledger (controller-owned accounting)

@dataclasses.dataclass(frozen=True)
class Decision:
    allowed: bool
    child_id: str
    reason: str


@contextlib.contextmanager
def _exclusive(path: pathlib.Path) -> Iterator[None]:
    """Cross-process exclusive section via an O_EXCL lock file; fail closed on timeout."""
    lock = path.with_suffix(path.suffix + ".lock")
    deadline = time.monotonic() + _LOCK_TIMEOUT_S
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise _violation(f"ledger lock {lock} held past {_LOCK_TIMEOUT_S}s; refusing (fail closed)")
            time.sleep(0.02)
    try:
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(OSError):
            lock.unlink()


class SubagentLedger:
    """Controller-issued parent/child ids with global per-run accounting (R571, R582).

    The file is the single source of truth shared by the controller process and the
    child's hook; every mutation runs under an exclusive lock and is written whole.
    """

    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)

    # -- lifecycle -------------------------------------------------------
    @classmethod
    def create(cls, path: pathlib.Path, contract: SubagentContract, *, primary_id: str) -> "SubagentLedger":
        if not primary_id or not isinstance(primary_id, str):
            raise _violation("primary_id is required")
        ledger = cls(path)
        ledger.path.parent.mkdir(parents=True, exist_ok=True)
        ledger._write({
            "schema": LEDGER_SCHEMA,
            "contract": contract.to_dict(),
            "primary_id": primary_id,
            "issued": [],
            "denials": [],
            "closed": False,
        })
        return ledger

    def _read(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise _violation(f"ledger {self.path} unreadable: {exc!r}") from exc
        if data.get("schema") != LEDGER_SCHEMA:
            raise _violation(f"ledger {self.path} has schema {data.get('schema')!r}, expected {LEDGER_SCHEMA}")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.path)

    @property
    def contract(self) -> SubagentContract:
        return SubagentContract.from_dict(self._read()["contract"])

    # -- accounting ------------------------------------------------------
    @staticmethod
    def _live(data: Mapping[str, Any]) -> list[dict[str, Any]]:
        return [row for row in data["issued"] if row.get("ended_at") is None]

    def request(self, *, parent_id: str, subagent_type: str, description: str,
                depth: int, background: bool, isolation: str = "", mcp: bool = False) -> Decision:
        """Decide one spawn request under the contract; record the outcome either way."""
        with _exclusive(self.path):
            data = self._read()
            contract = SubagentContract.from_dict(data["contract"])
            reason = self._deny_reason(data, contract, parent_id, subagent_type, depth, background,
                                       isolation, mcp)
            if reason:
                data["denials"].append({"parent_id": parent_id, "subagent_type": subagent_type,
                                        "description": description, "reason": reason,
                                        "at": time.time()})
                self._write(data)
                return Decision(False, "", reason)
            child_id = f"{data['primary_id']}.c{len(data['issued']) + 1:03d}"
            data["issued"].append({"child_id": child_id, "parent_id": parent_id,
                                   "subagent_type": subagent_type, "description": description,
                                   "depth": depth, "started_at": time.time(), "ended_at": None,
                                   "status": "running"})
            self._write(data)
            return Decision(True, child_id, "issued")

    @staticmethod
    def _deny_reason(data, contract, parent_id, subagent_type, depth, background, isolation, mcp) -> str:
        if data.get("closed"):
            return "run is closed; no further subagents"
        if parent_id != data["primary_id"]:
            return f"parent {parent_id!r} is not the primary worker {data['primary_id']!r}: depth>1 (R568)"
        if depth != 1:
            return f"delegation depth {depth} exceeds the fixed depth {MAX_DEPTH} (R568)"
        if background:
            return "background subagents are prohibited; foreground only (R569)"
        if isolation:
            return f"isolation={isolation!r} would create a git worktree from a subagent (R572/R573)"
        if mcp:
            return "MCP access is denied to every subagent (R575)"
        if subagent_type not in contract.agent_inventory:
            return f"subagent type {subagent_type!r} is outside the controller inventory {list(contract.agent_inventory)} (R575)"
        live = len(SubagentLedger._live(data))
        if live >= contract.max_concurrent:
            return f"concurrent limit {contract.max_concurrent} reached ({live} live) (R567)"
        if len(data["issued"]) >= contract.max_total:
            return f"total limit {contract.max_total} reached ({len(data['issued'])} issued) (R567)"
        return ""

    def release(self, child_id: str, *, status: str = "completed") -> None:
        with _exclusive(self.path):
            data = self._read()
            for row in data["issued"]:
                if row["child_id"] == child_id and row.get("ended_at") is None:
                    row["ended_at"] = time.time()
                    row["status"] = status
                    self._write(data)
                    return
            raise _violation(f"child {child_id!r} is not a live issued subagent")

    def release_latest_live(self, *, status: str = "completed") -> str:
        """Release the most recently issued live child (PostToolUse carries no child id)."""
        with _exclusive(self.path):
            data = self._read()
            live = self._live(data)
            if not live:
                raise _violation("no live subagent to release")
            row = live[-1]
            row["ended_at"] = time.time()
            row["status"] = status
            self._write(data)
            return row["child_id"]

    def close(self) -> dict[str, Any]:
        """Close the run: no further issuance; report the accounting (R582)."""
        with _exclusive(self.path):
            data = self._read()
            data["closed"] = True
            self._write(data)
        return self.accounting()

    def accounting(self) -> dict[str, Any]:
        data = self._read()
        live = self._live(data)
        return {
            "primary_id": data["primary_id"],
            "processes_total": 1 + len(data["issued"]),       # primary + every issued subagent
            "subagents_issued": len(data["issued"]),
            "subagents_live": len(live),
            "subagents_denied": len(data["denials"]),
            "unreleased_child_ids": [row["child_id"] for row in live],
            "closed": bool(data.get("closed")),
        }


# ---------------------------------------------------------------- restricted profile

MCP_DENY_RULE = "mcp__*"


@dataclasses.dataclass(frozen=True)
class RestrictedProfile:
    """The composed child launch profile: real flags + the --settings document."""

    argv_flags: tuple[str, ...]
    settings: dict[str, Any]
    agents: dict[str, Any]
    profile_path: str
    identity_sha256: str

    def effective_grants(self) -> frozenset[str]:
        """Tools a child may actually use without a prompt: inventory ∩ exact allows − denies.

        ``--tools`` alone grants nothing (R578): a tool in the inventory with no exact
        allow rule is prompted-for, and ``dontAsk`` turns that prompt into a denial.
        """
        inventory = set(self.settings["mrl"]["tools_inventory"])
        allows = {rule.split("(", 1)[0] for rule in self.settings["permissions"]["allow"]}
        denies = {rule.split("(", 1)[0] for rule in self.settings["permissions"]["deny"]}
        return frozenset((inventory & allows) - denies)


def settings_profile_identity(policy_bytes: bytes, managed_settings_path: "pathlib.Path | None") -> "tuple[str, dict[str, Any]]":
    """SHA-256 over the POLICY document + the managed policy (present or accounted-absent).

    The policy document is the profile minus its per-run hook command strings (which
    embed the run's ledger path) plus the hook script's own bytes, so the launch
    manifest can pin the identity before the run directory exists (R559) while a
    changed rule, inventory, agent definition, hook script, or managed policy
    still changes it.
    """
    digest = hashlib.sha256(policy_bytes)
    managed: dict[str, Any] = {"path": str(managed_settings_path) if managed_settings_path else None,
                               "present": False, "sha256": None}
    if managed_settings_path and pathlib.Path(managed_settings_path).is_file():
        managed_bytes = pathlib.Path(managed_settings_path).read_bytes()
        managed["present"] = True
        managed["sha256"] = hashlib.sha256(managed_bytes).hexdigest()
        digest.update(b"\nmanaged:" + managed_bytes)
    else:
        digest.update(b"\nmanaged:absent")
    return digest.hexdigest(), managed


def policy_document_bytes(settings: Mapping[str, Any], agents: Mapping[str, Any],
                          hook_script: pathlib.Path) -> bytes:
    """Canonical bytes of everything policy-relevant in a profile (see settings_profile_identity)."""
    hook_sha = hashlib.sha256(pathlib.Path(hook_script).read_bytes()).hexdigest()
    hooks_shape = {event: [{"matcher": h["matcher"], "n": len(h["hooks"])} for h in rows]
                   for event, rows in settings.get("hooks", {}).items()}
    mrl = {k: v for k, v in settings["mrl"].items() if k not in ("run_id", "managed_policy")}
    doc = {"permissions": settings["permissions"], "hooks": hooks_shape, "hook_script_sha256": hook_sha,
           "mrl": mrl, "agents": agents}
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_restricted_profile(
    contract: SubagentContract,
    *,
    ledger_path: pathlib.Path,
    hook_script: pathlib.Path,
    allow_rules: Sequence[str],
    deny_rules: Sequence[str] = (),
    profile_dir: pathlib.Path,
    model: str,
    managed_settings_path: "pathlib.Path | None" = None,
    python_executable: str = sys.executable,
) -> RestrictedProfile:
    """Compose the restricted child profile from the real CLI mechanisms (R577).

    Writes ``<profile_dir>/mrl_settings_profile.json`` (the ``--settings`` document)
    and returns the flags to append to the one-shot argv plus the identity the launch
    manifest pins. Refuses an allow rule outside the tools inventory, a missing hook
    script, and any MCP allowance.
    """
    hook_script = pathlib.Path(hook_script)
    if not hook_script.is_file():
        raise _violation(f"subagent accounting hook {hook_script} is not a file")
    if not isinstance(model, str) or not model.strip():
        raise _violation("exactly one model is required for the restricted profile")
    inventory = tuple(dict.fromkeys(contract.tools_inventory))
    for rule in allow_rules:
        base = str(rule).split("(", 1)[0]
        if base not in inventory:
            raise _violation(f"allow rule {rule!r} names a tool outside the inventory {list(inventory)}")
        if base.startswith("mcp__"):
            raise _violation(f"allow rule {rule!r} would grant MCP; strictly denied (R575)")
    denies = tuple(dict.fromkeys([*deny_rules, MCP_DENY_RULE]))
    # M0-T142 (D-024-R688/R689/R692, measured live on 2.1.252): a tool that is in the
    # inventory but in NEITHER the allow nor the deny rules is NOT blocked - under
    # dontAsk the CLI executed read-only Bash commands for exactly that shape
    # (canary-b5-02r1). The restriction must be EXPLICIT: every inventory tool is
    # either allow-ruled or deny-ruled, or the profile refuses to build.
    allow_bases = {str(rule).split("(", 1)[0] for rule in allow_rules}
    deny_bases = {str(rule).split("(", 1)[0] for rule in denies}
    unpinned = [t for t in inventory if t not in allow_bases and t not in deny_bases]
    if unpinned:
        raise _violation(
            f"inventory tool(s) {unpinned} are neither allow-ruled nor deny-ruled; "
            f"Claude Code 2.1.252 dontAsk EXECUTES read-only commands for unlisted tools, "
            f"so the restriction must be explicit (deny them or allow them; R688/R692)")
    hook_cmd = (f'"{python_executable}" "{hook_script}" --ledger "{pathlib.Path(ledger_path)}" '
                f'--parent "{contract.run_id}.primary"')
    agents = {
        name: {"description": f"MRL inventory subagent {name} (read-only, depth 1, foreground)",
               "prompt": "You are a read-only MRL subagent. Report findings; never edit, commit, push, "
                         "open PRs, merge, accept tasks, spawn agents, or use MCP.",
               "tools": ["Read", "Grep", "Glob"], "model": model}
        for name in contract.agent_inventory
    }
    settings = {
        "$schema_note": PROFILE_SCHEMA,
        "permissions": {"allow": list(allow_rules), "deny": list(denies), "defaultMode": "dontAsk"},
        "hooks": {
            "PreToolUse": [{"matcher": "Agent|Task",
                            "hooks": [{"type": "command", "command": hook_cmd + " --event pre"}]}],
            "PostToolUse": [{"matcher": "Agent|Task",
                             "hooks": [{"type": "command", "command": hook_cmd + " --event post"}]}],
        },
        "mrl": {"run_id": contract.run_id, "task_id": contract.task_id, "repo_root": contract.repo_root,
                "allowed_paths": list(contract.allowed_paths), "tools_inventory": list(inventory),
                "agent_inventory": list(contract.agent_inventory),
                "max_concurrent": contract.max_concurrent, "max_total": contract.max_total,
                "max_depth": contract.max_depth, "foreground_only": True, "mcp": "denied"},
    }
    profile_dir = pathlib.Path(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_path = profile_dir / "mrl_settings_profile.json"
    profile_bytes = json.dumps(settings, indent=2, sort_keys=True).encode("utf-8")
    profile_path.write_bytes(profile_bytes)
    identity, managed = settings_profile_identity(
        policy_document_bytes(settings, agents, hook_script), managed_settings_path)
    settings["mrl"]["managed_policy"] = managed
    flags: list[str] = [
        "--restricted",
        "--permission-mode", "dontAsk",
        "--tools", ",".join(inventory),
        "--strict-mcp-config",
        "--settings", str(profile_path),
        "--agents", json.dumps(agents, sort_keys=True),
    ]
    if allow_rules:
        flags += ["--allowedTools", *[str(r) for r in allow_rules]]
    flags += ["--disallowedTools", *denies]
    return RestrictedProfile(argv_flags=tuple(flags), settings=settings, agents=agents,
                             profile_path=str(profile_path), identity_sha256=identity)


__all__ = [
    "LEDGER_SCHEMA", "PROFILE_SCHEMA", "MAX_DEPTH", "WRITER_POLICIES", "MCP_DENY_RULE",
    "SubagentContract", "Decision", "SubagentLedger", "RestrictedProfile",
    "settings_profile_identity", "policy_document_bytes", "build_restricted_profile",
]
