#!/usr/bin/env python3
"""MRL launch manifest: the ONE canonical ``start --launch-manifest <absolute-path>``
entrance and its pre-dispatch verification (M0-T136 cluster C-B1; D-024-R557..R560).

The manifest SUPPLIES expected values; it is never proof. Immediately before any
provider contact the controller independently OBSERVES each value from git, the
filesystem, the task packet and the restricted-profile policy, and refuses the
launch if ANY of the twelve R559 fields disagrees:

  repo_root, origin_url (normalized), task_id, task_packet_sha256, worktree,
  branch, head_sha, tree_sha, clean_status, allowed_paths,
  settings_profile_sha256, mode.

Every mismatch is reported (not just the first), so an operator sees the whole
disagreement set at once. Nothing in this module spawns a provider; it is pure
observation plus comparison, with ``run_git`` injectable for tests.

The ``observe`` entrypoint (``python -m tools.agent_supervisor.mrl_launch_manifest
observe ...``) prints a manifest DRAFT from the same observers so the operator
can author the expected values, review them, and save the file; a later launch
still re-observes everything, so authoring never satisfies a check by itself.

Import direction: ``mrl_remote`` (URL normalizer), ``mrl_subagent_contract``,
``mrl_worker_result`` only; nothing imports back.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping, Sequence

from .mrl_remote import normalize_remote_url
from .mrl_subagent_contract import SubagentContract, build_restricted_profile
from .mrl_worker_result import ContractError

MANIFEST_SCHEMA = "mrl_launch_manifest/v1"
AUTHORIZED_MODES = ("shadow", "supervised", "limited-auto")
EXPECTED_FIELDS = (
    "repo_root", "origin_url", "task_id", "task_packet_sha256", "worktree", "branch",
    "head_sha", "tree_sha", "clean_status", "allowed_paths", "settings_profile_sha256", "mode",
)
DISPATCH_FIELDS = (
    "claude_executable", "claude_chain_sha256", "claude_model", "claude_runtime_model", "claude_version",
    "codex_executable", "codex_chain_sha256", "codex_model", "codex_version",
    "config", "model_selection", "controller_manifest", "task_packet_path",
    "max_turns", "unit_timeout_seconds", "subagents",
)
SUBAGENT_FIELDS = ("max_concurrent", "max_total", "agent_inventory", "tools_inventory", "allow_rules",
                   "deny_rules")
HOOK_SCRIPT = pathlib.Path(__file__).resolve().parent / "mrl_subagent_hook.py"

RunGit = Callable[[Sequence[str], str], str]


def _violation(message: str) -> ContractError:
    return ContractError("contract_violation", message)


def _default_run_git(argv: Sequence[str], cwd: str) -> str:
    proc = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise _violation(f"git {' '.join(argv)} failed rc={proc.returncode}: {proc.stderr.strip()[:300]}")
    return proc.stdout


def normalize_path(path: str) -> str:
    """Case-normalized, symlink-resolved, forward-slash path for comparison."""
    return os.path.normcase(os.path.realpath(str(path))).replace("\\", "/")


def default_managed_settings_path(sys_platform: str = sys.platform) -> pathlib.Path:
    """Claude Code's documented managed-settings location for the platform."""
    if sys_platform.startswith("win"):
        return pathlib.Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "ClaudeCode" / "managed-settings.json"
    if sys_platform == "darwin":
        return pathlib.Path("/Library/Application Support/ClaudeCode/managed-settings.json")
    return pathlib.Path("/etc/claude-code/managed-settings.json")


# ---------------------------------------------------------------- manifest model

@dataclasses.dataclass(frozen=True)
class LaunchManifest:
    path: str
    expected: dict[str, Any]
    dispatch: dict[str, Any]

    @classmethod
    def load(cls, path: "str | os.PathLike[str]") -> "LaunchManifest":
        p = pathlib.Path(path)
        if not p.is_absolute():
            raise _violation(f"--launch-manifest must be an absolute path, got {path!r} (R557)")
        if not p.is_file():
            raise _violation(f"launch manifest {p} is not a file")
        try:
            raw = json.loads(p.read_text(encoding="utf-8-sig"))
        except ValueError as exc:
            raise _violation(f"launch manifest {p} is not valid JSON: {exc}") from exc
        return cls.from_dict(raw, path=str(p))

    @classmethod
    def from_dict(cls, raw: Any, *, path: str = "<memory>") -> "LaunchManifest":
        if not isinstance(raw, Mapping):
            raise _violation("launch manifest must be a JSON object")
        if raw.get("schema") != MANIFEST_SCHEMA:
            raise _violation(f"launch manifest schema {raw.get('schema')!r} != {MANIFEST_SCHEMA!r}")
        expected = raw.get("expected")
        dispatch = raw.get("dispatch")
        if not isinstance(expected, Mapping) or not isinstance(dispatch, Mapping):
            raise _violation("launch manifest needs 'expected' and 'dispatch' objects")
        missing = [f for f in EXPECTED_FIELDS if f not in expected]
        if missing:
            raise _violation(f"launch manifest expected.* missing {missing}")
        missing = [f for f in DISPATCH_FIELDS if f not in dispatch]
        if missing:
            raise _violation(f"launch manifest dispatch.* missing {missing}")
        sub = dispatch["subagents"]
        if not isinstance(sub, Mapping) or any(f not in sub for f in SUBAGENT_FIELDS):
            raise _violation(f"launch manifest dispatch.subagents needs {list(SUBAGENT_FIELDS)}")
        cls._check_shapes(expected, dispatch)
        return cls(path=path, expected=dict(expected), dispatch=dict(dispatch))

    @staticmethod
    def _check_shapes(expected: Mapping[str, Any], dispatch: Mapping[str, Any]) -> None:
        for key in ("head_sha", "tree_sha"):
            v = expected[key]
            if not isinstance(v, str) or len(v) != 40 or any(c not in "0123456789abcdef" for c in v):
                raise _violation(f"expected.{key} must be a 40-hex sha, got {v!r}")
        for key, holder in (("task_packet_sha256", expected), ("settings_profile_sha256", expected),
                            ("claude_chain_sha256", dispatch), ("codex_chain_sha256", dispatch)):
            v = holder[key]
            if not isinstance(v, str) or len(v) != 64:
                raise _violation(f"{key} must be a 64-hex sha256, got {v!r}")
        if expected["clean_status"] is not True:
            raise _violation("expected.clean_status must be true: the MRL never launches on a dirty tree (R559)")
        if expected["mode"] not in AUTHORIZED_MODES:
            raise _violation(f"expected.mode {expected['mode']!r} is not an authorized mode {AUTHORIZED_MODES}")
        if not isinstance(expected["allowed_paths"], list) or not expected["allowed_paths"]:
            raise _violation("expected.allowed_paths must be a non-empty list")
        for key in ("repo_root", "worktree"):
            if not pathlib.Path(str(expected[key])).is_absolute():
                raise _violation(f"expected.{key} must be an absolute path")
        for key in ("claude_executable", "codex_executable", "config", "model_selection",
                    "controller_manifest", "task_packet_path"):
            if not pathlib.Path(str(dispatch[key])).is_absolute():
                raise _violation(f"dispatch.{key} must be an absolute path")
        for key in ("max_turns", "unit_timeout_seconds"):
            v = dispatch[key]
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise _violation(f"dispatch.{key} must be a positive int")

    def managed_settings_path(self) -> "pathlib.Path | None":
        """The managed (enterprise) policy file the identity must account for.

        Optional ``dispatch.managed_settings_path``; absent, the platform's canonical
        location is used so a policy installed there can never be silently outside
        the pinned identity. An explicit empty string means "none" (recorded absent).
        """
        raw = self.dispatch.get("managed_settings_path")
        if raw is None:
            return default_managed_settings_path()
        if raw == "":
            return None
        p = pathlib.Path(str(raw))
        if not p.is_absolute():
            raise _violation("dispatch.managed_settings_path must be absolute or empty")
        return p

    def subagent_contract(self, run_id: str) -> SubagentContract:
        sub = self.dispatch["subagents"]
        return SubagentContract(
            run_id=run_id, task_id=str(self.expected["task_id"]), repo_root=str(self.expected["repo_root"]),
            allowed_paths=tuple(self.expected["allowed_paths"]),
            tools_inventory=tuple(sub["tools_inventory"]), agent_inventory=tuple(sub["agent_inventory"]),
            max_concurrent=int(sub["max_concurrent"]), max_total=int(sub["max_total"]),
        )


# ---------------------------------------------------------------- observation

def read_task_packet(path: pathlib.Path) -> "tuple[dict[str, Any], str]":
    """Read the packet ONCE, returning (parsed, sha256 of the exact bytes read)."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise _violation(f"task packet {path} unreadable: {exc}") from exc
    try:
        parsed = json.loads(data.decode("utf-8-sig"))
    except ValueError as exc:
        raise _violation(f"task packet {path} is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise _violation(f"task packet {path} is not a JSON object")
    return parsed, hashlib.sha256(data).hexdigest()


def observe(worktree: str, task_packet: str, *, run_git: RunGit | None = None) -> dict[str, Any]:
    """Independently observe every expected.* value (git + filesystem + packet)."""
    runner = run_git or _default_run_git

    def git(argv: Sequence[str], cwd: str) -> str:
        # A git that cannot run (missing binary, timeout, I/O error) is an UNOBSERVABLE
        # launch: a typed violation, never a traceback and never a pass.
        try:
            return runner(argv, cwd)
        except (OSError, subprocess.SubprocessError) as exc:
            raise _violation(f"git {' '.join(argv)} could not run in {cwd}: {exc!r}") from exc

    wt = pathlib.Path(worktree)
    if not wt.is_dir():
        raise _violation(f"worktree {worktree!r} is not a directory")
    cwd = str(wt)
    toplevel = git(["rev-parse", "--show-toplevel"], cwd).strip()
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd).strip()
    packet, packet_sha = read_task_packet(pathlib.Path(task_packet))
    status = git(["status", "--porcelain", "--untracked-files=all"], cwd)
    return {
        "repo_root": str(pathlib.Path(common).parent),
        "origin_url": normalize_remote_url(git(["remote", "get-url", "origin"], cwd).strip()),
        "task_id": str(packet.get("task_id", "")),
        "task_packet_sha256": packet_sha,
        "worktree": toplevel,
        "branch": git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).strip(),
        "head_sha": git(["rev-parse", "HEAD"], cwd).strip(),
        "tree_sha": git(["rev-parse", "HEAD^{tree}"], cwd).strip(),
        "clean_status": status.strip() == "",
        "allowed_paths": sorted(str(p) for p in packet.get("allowed_paths", []) or []),
        "_status_lines": [line for line in status.splitlines() if line.strip()],
    }


def observe_profile_identity(manifest: LaunchManifest, *, profile_dir: pathlib.Path, ledger_path: pathlib.Path,
                             run_id: str = "preflight") -> "tuple[str, Any]":
    """Build the restricted profile the run will really use and report its policy identity.

    The profile written under ``profile_dir`` IS the one the one-shot launch passes as
    ``--settings`` (C-B4), so the identity compared here is the identity that governs
    the child - never a separately computed stand-in.
    """
    sub = manifest.dispatch["subagents"]
    profile = build_restricted_profile(
        manifest.subagent_contract(run_id), ledger_path=ledger_path, hook_script=HOOK_SCRIPT,
        allow_rules=tuple(sub["allow_rules"]), deny_rules=tuple(sub["deny_rules"]), profile_dir=profile_dir,
        model=str(manifest.dispatch["claude_model"]), managed_settings_path=manifest.managed_settings_path(),
    )
    return profile.identity_sha256, profile


# ---------------------------------------------------------------- verification

@dataclasses.dataclass(frozen=True)
class FieldCheck:
    field: str
    expected: Any
    observed: Any
    match: bool


@dataclasses.dataclass(frozen=True)
class LaunchVerification:
    ok: bool
    checks: tuple[FieldCheck, ...]
    observed: dict[str, Any]

    @property
    def mismatches(self) -> tuple[FieldCheck, ...]:
        return tuple(c for c in self.checks if not c.match)

    def refusal_message(self) -> str:
        lines = [f"LAUNCH REFUSED before provider launch: {len(self.mismatches)} field(s) disagree (R560)"]
        for c in self.mismatches:
            lines.append(f"  - {c.field}: expected {c.expected!r}, observed {c.observed!r}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "checks": [dataclasses.asdict(c) for c in self.checks],
                "observed": {k: v for k, v in self.observed.items() if not k.startswith("_")}}


def _same(field: str, expected: Any, observed: Any) -> bool:
    if field in ("repo_root", "worktree"):
        return normalize_path(str(expected)) == normalize_path(str(observed))
    if field == "origin_url":
        return normalize_remote_url(str(expected)) == str(observed)
    if field == "allowed_paths":
        return sorted(str(p) for p in expected) == list(observed)
    return expected == observed


def verify_launch(
    manifest: LaunchManifest,
    *,
    cli_mode: str,
    profile_identity: str,
    run_git: RunGit | None = None,
) -> LaunchVerification:
    """Compare every expected field with an independent observation; refuse on any mismatch.

    ``cli_mode`` is the ``--mode`` the operator actually invoked; ``profile_identity``
    is the identity of the restricted profile the run will really use
    (``observe_profile_identity``). The manifest's own values are never used as
    observations.
    """
    observed = observe(str(manifest.expected["worktree"]), str(manifest.dispatch["task_packet_path"]),
                       run_git=run_git)
    observed["settings_profile_sha256"] = profile_identity
    observed["mode"] = cli_mode
    checks = tuple(FieldCheck(field, manifest.expected[field], observed.get(field),
                              _same(field, manifest.expected[field], observed.get(field)))
                   for field in EXPECTED_FIELDS)
    return LaunchVerification(ok=all(c.match for c in checks), checks=checks, observed=observed)


def require_verified(verification: LaunchVerification) -> None:
    if not verification.ok:
        raise _violation(verification.refusal_message())


# ---------------------------------------------------------------- operator entrypoint (draft authoring)

def draft_manifest(worktree: str, task_packet: str, *, mode: str, run_git: RunGit | None = None) -> dict[str, Any]:
    """A manifest draft from live observation; dispatch values are left for the operator."""
    obs = observe(worktree, task_packet, run_git=run_git)
    if not obs["clean_status"]:
        raise _violation("cannot draft a launch manifest on a dirty tree: " + "; ".join(obs["_status_lines"][:5]))
    expected = {k: obs[k] for k in EXPECTED_FIELDS if k in obs}
    expected["settings_profile_sha256"] = "<fill from `observe --profile` after choosing dispatch.subagents>"
    expected["mode"] = mode
    dispatch: dict[str, Any] = {k: "<fill>" for k in DISPATCH_FIELDS}
    dispatch["task_packet_path"] = str(pathlib.Path(task_packet).resolve())
    dispatch["max_turns"] = 12
    dispatch["unit_timeout_seconds"] = 900
    dispatch["subagents"] = {"max_concurrent": 2, "max_total": 4, "agent_inventory": ["Explore"],
                             "tools_inventory": ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Agent"],
                             "allow_rules": ["Read", "Grep", "Glob"], "deny_rules": []}
    return {"schema": MANIFEST_SCHEMA, "expected": expected, "dispatch": dispatch}


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="mrl_launch_manifest")
    sub = parser.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("observe", help="print a launch-manifest draft from live observation")
    o.add_argument("--worktree", required=True)
    o.add_argument("--task-packet", required=True)
    o.add_argument("--mode", choices=AUTHORIZED_MODES, default="supervised")
    o.add_argument("--profile", help="an existing manifest whose dispatch.subagents identity to compute")
    o.add_argument("--scratch", default=None, help="directory for the identity computation (default: temp)")
    args = parser.parse_args(argv)
    try:
        if args.profile:
            manifest = LaunchManifest.load(args.profile)
            scratch = pathlib.Path(args.scratch) if args.scratch else pathlib.Path(tempfile.mkdtemp(prefix="mrl-"))
            identity, _ = observe_profile_identity(manifest, profile_dir=scratch, ledger_path=scratch / "ledger.json")
            print(json.dumps({"settings_profile_sha256": identity,
                              "managed_settings_path": str(manifest.managed_settings_path() or "")}, indent=2))
            return 0
        print(json.dumps(draft_manifest(args.worktree, args.task_packet, mode=args.mode), indent=2))
        return 0
    except ContractError as exc:
        sys.stderr.write(f"{exc}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
