#!/usr/bin/env python3
"""The ``start --launch-manifest`` entrance: manifest -> launch inputs -> PREFLIGHT
verification, kept out of ``cli.py`` (M0-T136 C-B1; D-024-R557..R560).

Two seams, both fail-closed and both typed (a refusal is a report, never a
traceback):

* ``apply_launch_manifest`` runs BEFORE the runtime opens. It loads the manifest,
  supplies every dispatch input the operator did not type (executables, packet,
  config, model selection, controller manifest, worktree/repo/branch, bounds) and
  REFUSES a typed flag that disagrees with the manifest - two sources of truth for
  one launch are an ambiguity, not a preference. ``--mode`` is never filled: the
  operator types it and the manifest's ``expected.mode`` verifies it.
* ``preflight_launch`` runs inside ``_run_loop`` at PREFLIGHT, immediately before the
  runner is built: it builds the restricted profile the child will really use,
  observes every R559 field independently, records the whole comparison, and
  raises ``LoopError('launch_manifest_mismatch')`` on ANY disagreement - which
  ``cmd_start`` reports through its existing typed-refusal path.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
from typing import Any

from . import refusals
from .errors import LoopError
from .mrl_launch_manifest import (
    LaunchManifest,
    LaunchVerification,
    normalize_path,
    observe_profile_identity,
    verify_launch,
)
from .mrl_worker_result import ContractError

LOADED_ATTR = "mrl_launch_manifest_loaded"
#: (args attribute, manifest section, manifest key) - path-valued launch inputs the
#: manifest supplies when the operator did not type them.
PATH_FILLS: tuple[tuple[str, str, str], ...] = (
    ("claude_executable", "dispatch", "claude_executable"),
    ("codex_executable", "dispatch", "codex_executable"),
    ("task_packet", "dispatch", "task_packet_path"),
    ("config", "dispatch", "config"),
    ("model_selection", "dispatch", "model_selection"),
    ("manifest", "dispatch", "controller_manifest"),
    ("worktree", "expected", "worktree"),
    ("repo", "expected", "worktree"),
)
#: (args attribute, manifest key, the `start` parser default) - numeric bounds. A
#: typed value equal to neither the parser default nor the manifest is a conflict.
BOUND_FILLS: tuple[tuple[str, str, Any], ...] = (
    ("max_turns", "max_turns", 12),
    ("unit_timeout", "unit_timeout_seconds", 900.0),
)


@dataclasses.dataclass(frozen=True)
class LaunchPreflight:
    manifest: LaunchManifest
    verification: LaunchVerification
    profile: Any
    run_dir: pathlib.Path
    ledger_path: pathlib.Path


def _refusal(reason_code: str, message: str, path: Any) -> refusals.Refusal:
    return refusals.refusal(refusals.UNSAFE, reason_code=reason_code, message=message,
                            detail={"launch_manifest": str(path or "")})


def apply_launch_manifest(args: argparse.Namespace) -> "tuple[LaunchManifest | None, refusals.Refusal | None]":
    """Load ``--launch-manifest`` and make it the launch's single source of inputs.

    Returns ``(None, None)`` when the flag is absent (the legacy explicit-flag path
    is untouched), ``(manifest, None)`` when applied, or ``(None, refusal)``.
    """
    path = getattr(args, "launch_manifest", None)
    if not path:
        return None, None
    try:
        manifest = LaunchManifest.load(path)
    except ContractError as exc:
        return None, _refusal("launch_manifest_invalid", str(exc), path)
    if getattr(args, "packet_queue", None) or int(getattr(args, "max_tasks", 1) or 1) > 1:
        return None, _refusal("launch_manifest_single_task",
                              "a launch manifest binds exactly ONE task to ONE fresh process (R581); "
                              "--max-tasks>1 / --packet-queue are not accepted with it", path)
    conflicts: list[str] = []
    for attr, section, key in PATH_FILLS:
        value = str(getattr(manifest, section)[key])
        current = getattr(args, attr, None)
        if current in (None, ""):
            setattr(args, attr, value)
        elif normalize_path(str(current)) != normalize_path(value):
            conflicts.append(f"--{attr.replace('_', '-')}={current!r} vs manifest {value!r}")
    branch = str(manifest.expected["branch"])
    if getattr(args, "branch", None) in (None, ""):
        args.branch = branch
    elif args.branch != branch:
        conflicts.append(f"--branch={args.branch!r} vs manifest {branch!r}")
    for attr, key, default in BOUND_FILLS:
        current = getattr(args, attr, None)
        value = manifest.dispatch[key]
        if current is not None and current != default and current != value:
            conflicts.append(f"--{attr.replace('_', '-')}={current!r} vs manifest {value!r}")
        setattr(args, attr, type(default)(value))
    if conflicts:
        return None, _refusal("launch_manifest_conflict",
                              "typed flags disagree with the launch manifest (one launch, one source of "
                              "inputs): " + "; ".join(conflicts), path)
    setattr(args, LOADED_ATTR, manifest)
    return manifest, None


def preflight_launch(args: argparse.Namespace, *, run_id: str, audit: Any,
                     run_git: Any = None) -> LaunchPreflight:
    """Verify the launch at PREFLIGHT; raise a typed LoopError on any mismatch (R560).

    ``run_git`` is the observation seam (real git when None); tests inject a fake
    observer, production never does.
    """
    manifest = getattr(args, LOADED_ATTR, None)
    if manifest is None:
        raise LoopError("launch_manifest_missing", "preflight_launch called without an applied launch manifest")
    run_dir = pathlib.Path(audit.path).parent / "mrl" / run_id
    ledger_path = run_dir / "subagent_ledger.json"
    try:
        identity, profile = observe_profile_identity(
            manifest, profile_dir=run_dir / "profile", ledger_path=ledger_path, run_id=run_id)
        verification = verify_launch(manifest, cli_mode=str(args.mode), profile_identity=identity,
                                     run_git=run_git)
    except ContractError as exc:
        audit.append("launch_manifest_refused", run_id=run_id, policy_result="REFUSED",
                     detail={"reason": "unobservable", "error": str(exc)})
        raise LoopError("launch_manifest_unobservable", str(exc)) from exc
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "launch_verification.json").write_text(
        json.dumps({"schema": "mrl_launch_verification/v1", "run_id": run_id, "manifest": manifest.path,
                    **verification.to_dict()}, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if not verification.ok:
        audit.append("launch_manifest_refused", run_id=run_id, policy_result="REFUSED",
                     detail={"reason": "mismatch",
                             "mismatches": [dataclasses.asdict(c) for c in verification.mismatches]})
        raise LoopError("launch_manifest_mismatch", verification.refusal_message())
    audit.append("launch_manifest_verified", run_id=run_id, policy_result="VERIFIED",
                 detail={"manifest": manifest.path, "fields": [c.field for c in verification.checks],
                         "head_sha": verification.observed["head_sha"],
                         "tree_sha": verification.observed["tree_sha"],
                         "settings_profile_sha256": identity})
    return LaunchPreflight(manifest=manifest, verification=verification, profile=profile,
                           run_dir=run_dir, ledger_path=ledger_path)
