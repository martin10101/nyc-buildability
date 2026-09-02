#!/usr/bin/env python3
"""Draft the MRL launch manifest with BOUND dispatch identities (M0-T136 C-B5; D-024-R585).

``mrl_launch_manifest observe`` prints a draft whose dispatch section is sixteen
``<fill>`` placeholders - among them two 64-hex chain digests and two versions
that nothing but the real executables can produce, and two model ids that must
equal the runtime model-selection file VERBATIM or the launch refuses
(``launch_manifest_mismatch`` / ``codex_model_mismatch``). Hand-typing those is
a typo hunt, not an operator launch path. This entrypoint fills them the SAME
way the launch later verifies them:

* ``resolve_chain`` + ``bind_chain_now`` (complete streaming SHA-256 of every
  link, no cache) and ``observe_version`` (the bound head's ``--version``) for
  each provider (C-B2);
* ``load_model_selection`` for ``claude_model`` / ``codex_model`` - the exact ids
  the launch cross-checks, never aliased;
* the operator's EXPLICIT ``--base-ref`` (never defaulted, R504/R505) and an
  explicit choice for ``claude_runtime_model`` (``--claude-runtime-model`` or
  ``--claude-runtime-model-from-selection``; the runtime-reported id is proven
  by the live canary, so the draft never guesses it);
* ``observe_profile_identity`` for ``expected.settings_profile_sha256`` once
  EVERY dispatch value is bound - the identical function PREFLIGHT runs.

Nothing here is proof. ``start --launch-manifest`` re-observes every expected
value at PREFLIGHT and re-hashes every chain link immediately before the spawn;
the draft only makes the saved manifest carry the identity the launch will
check. Anything the operator did not supply stays a ``<fill>`` placeholder and
is REPORTED (``remaining_placeholders``), never silently defaulted.

Child processes: exactly ``<claude> --version`` and ``<codex> --version``
(``run_version`` injectable). No provider contact, no journal, no git writes.

Import direction: ``mrl_launch_manifest``, ``mrl_exec_chain``, ``config``,
``mrl_worker_result``; nothing imports back.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import sys
import tempfile
from typing import Any

from .config import ConfigError, load_model_selection
from .mrl_exec_chain import RunVersion, bind_chain_now, observe_version, resolve_chain
from .mrl_launch_manifest import (
    AUTHORIZED_MODES,
    LaunchManifest,
    RunGit,
    draft_manifest,
    observe_profile_identity,
)
from .mrl_worker_result import ContractError

DEFAULT_MAX_TURNS = 12
DEFAULT_UNIT_TIMEOUT_SECONDS = 900
#: (dispatch key, DraftInputs attribute) - the absolute FILE paths the operator supplies.
_FILE_INPUTS: tuple[tuple[str, str], ...] = (
    ("config", "config"),
    ("model_selection", "model_selection"),
    ("controller_manifest", "controller_manifest"),
)


def _violation(message: str) -> ContractError:
    return ContractError("contract_violation", message)


@dataclasses.dataclass(frozen=True)
class DraftInputs:
    """Everything the operator may supply; an empty string means 'leave the placeholder'."""

    worktree: str
    task_packet: str
    mode: str = "supervised"
    claude_executable: str = ""
    codex_executable: str = ""
    config: str = ""
    model_selection: str = ""
    controller_manifest: str = ""
    base_ref: str = ""
    claude_runtime_model: str = ""
    runtime_model_from_selection: bool = False
    max_turns: int = DEFAULT_MAX_TURNS
    unit_timeout_seconds: int = DEFAULT_UNIT_TIMEOUT_SECONDS
    # Subagent contract (C-B3). ``None`` keeps the draft_manifest default; a value REPLACES it
    # wholesale so the manifest states the operator's exact choice (never a merged guess).
    tools_inventory: tuple[str, ...] | None = None
    allow_tools: tuple[str, ...] | None = None
    deny_tools: tuple[str, ...] | None = None
    agent_inventory: tuple[str, ...] | None = None
    max_concurrent: int | None = None
    max_total: int | None = None


def is_placeholder(value: Any) -> bool:
    """True for an unfilled ``<fill ...>`` draft value."""
    return isinstance(value, str) and value.startswith("<")


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise _violation(f"{name} must be a positive int, got {value!r}")
    return value


def _absolute_file(value: str, name: str) -> str:
    p = pathlib.Path(value)
    if not p.is_absolute():
        raise _violation(f"--{name.replace('_', '-')} must be an absolute path, got {value!r}")
    if not p.is_file():
        raise _violation(f"--{name.replace('_', '-')} {value!r} is not a file; fail closed")
    return str(p)


def bind_provider(executable: str, kind: str, *, run_version: RunVersion | None = None) -> dict[str, Any]:
    """Resolve, hash and version one provider chain exactly as the launch will.

    Returns ``executable`` (the wrapper the manifest names), ``chain_sha256`` (the
    combined identity ``verify_chain_now`` re-checks before the spawn), ``version``
    (what ``--version`` reported, compared verbatim at launch) plus the resolved
    ``shape`` and ``links`` for the operator's eyes. An executable that reports no
    parseable version is refused: the launch would refuse it too (R564).
    """
    chain = resolve_chain(executable, kind)
    identity = bind_chain_now(chain)
    version = observe_version(chain, run=run_version)
    if not version:
        raise _violation(f"{kind} executable {executable!r} reported no MAJOR.MINOR.PATCH version; "
                         f"the launch verifies it (R564), so the draft cannot pin it")
    return {
        "executable": str(pathlib.Path(executable)),
        "chain_sha256": identity.combined_sha256,
        "version": version,
        "shape": chain.shape,
        "links": [{"role": role, "path": path} for role, path in chain.links],
    }


def _names(values: tuple[str, ...], flag: str) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise _violation(f"--{flag} values must be non-empty names, got {value!r}")
        if value.strip() not in cleaned:
            cleaned.append(value.strip())
    return cleaned


def apply_subagent_choices(dispatch: dict[str, Any], inputs: DraftInputs) -> dict[str, Any]:
    """Apply the operator's subagent-contract choices to ``dispatch['subagents']``.

    Every supplied value replaces the draft default outright. The result is
    checked the way the launch checks it: ``allow_rules`` must name tools in
    ``tools_inventory`` (``build_restricted_profile`` refuses anything else),
    every inventory tool must be EXPLICITLY allow- or deny-ruled (M0-T142
    R688/R692: 2.1.252 dontAsk executes read-only commands for unlisted tools),
    and ``max_concurrent`` <= ``max_total`` (``SubagentContract``). ``Agent``
    fan-out needs BOTH ``Agent`` in the inventory and an ``Agent`` allow rule:
    the draft default grants Read/Grep/Glob only and denies the rest, so a
    canary that must fan out states both choices here.
    """
    sub = dict(dispatch["subagents"])
    for key, values, flag in (
        ("tools_inventory", inputs.tools_inventory, "tool"),
        ("allow_rules", inputs.allow_tools, "allow-tool"),
        ("deny_rules", inputs.deny_tools, "deny-tool"),
        ("agent_inventory", inputs.agent_inventory, "agent"),
    ):
        if values is not None:
            sub[key] = _names(tuple(values), flag)
    for key, value in (("max_concurrent", inputs.max_concurrent), ("max_total", inputs.max_total)):
        if value is not None:
            sub[key] = _positive_int(value, key)
    if sub["max_concurrent"] > sub["max_total"]:
        raise _violation(f"max_concurrent {sub['max_concurrent']} cannot exceed max_total {sub['max_total']}")
    inventory = set(sub["tools_inventory"])
    outside = [rule for rule in sub["allow_rules"] if rule.split("(", 1)[0] not in inventory]
    if outside:
        raise _violation(f"--allow-tool {outside} name tools outside the inventory {sorted(inventory)}; "
                         f"the restricted profile would refuse them (R574)")
    allows = {rule.split("(", 1)[0] for rule in sub["allow_rules"]}
    denies = {rule.split("(", 1)[0] for rule in sub["deny_rules"]}
    unpinned = [t for t in sub["tools_inventory"] if t not in allows and t not in denies]
    if unpinned:
        raise _violation(f"inventory tool(s) {unpinned} are neither --allow-tool nor --deny-tool; "
                         f"Claude Code 2.1.252 dontAsk EXECUTES read-only commands for unlisted "
                         f"tools, so the restriction must be explicit (R688/R692)")
    dispatch["subagents"] = sub
    return sub


def _load_models(path: str) -> tuple[str, str]:
    try:
        selection = load_model_selection(path)
    except ConfigError as exc:
        raise ContractError(exc.code, f"model selection {path!r} rejected: {exc.message}") from exc
    claude_model = selection.claude.primary
    codex_model = selection.codex.primary
    if not claude_model:
        raise _violation(f"model selection {path!r} has an empty claude.model; the launch cross-checks "
                         f"dispatch.claude_model against it, so nothing can be pinned")
    if not codex_model:
        raise _violation(f"model selection {path!r} has an empty codex.review_model; the reviewer "
                         f"cross-checks dispatch.codex_model against it, so nothing can be pinned")
    return claude_model, codex_model


def fill_draft(
    inputs: DraftInputs,
    *,
    run_git: RunGit | None = None,
    run_version: RunVersion | None = None,
    scratch: pathlib.Path | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Observe the draft and bind every dispatch value the operator supplied.

    Returns ``(draft, remaining_placeholders)``. ``expected.settings_profile_sha256``
    is computed (via ``observe_profile_identity``, the PREFLIGHT function) only when
    no dispatch placeholder remains; otherwise it stays a placeholder and is listed,
    because a manifest with a guessed identity would only refuse at PREFLIGHT.
    """
    if inputs.mode not in AUTHORIZED_MODES:
        raise _violation(f"mode {inputs.mode!r} is not an authorized mode {AUTHORIZED_MODES}")
    draft = draft_manifest(inputs.worktree, inputs.task_packet, mode=inputs.mode, run_git=run_git)
    dispatch = draft["dispatch"]
    dispatch["max_turns"] = _positive_int(inputs.max_turns, "max_turns")
    dispatch["unit_timeout_seconds"] = _positive_int(inputs.unit_timeout_seconds, "unit_timeout_seconds")
    apply_subagent_choices(dispatch, inputs)
    bindings: dict[str, Any] = {}
    for kind, executable in (("claude", inputs.claude_executable), ("codex", inputs.codex_executable)):
        if executable:
            bound = bind_provider(executable, kind, run_version=run_version)
            bindings[kind] = bound
            dispatch[f"{kind}_executable"] = bound["executable"]
            dispatch[f"{kind}_chain_sha256"] = bound["chain_sha256"]
            dispatch[f"{kind}_version"] = bound["version"]
    for key, attr in _FILE_INPUTS:
        value = getattr(inputs, attr)
        if value:
            dispatch[key] = _absolute_file(value, key)
    if inputs.model_selection:
        claude_model, codex_model = _load_models(dispatch["model_selection"])
        dispatch["claude_model"] = claude_model
        dispatch["codex_model"] = codex_model
        if inputs.runtime_model_from_selection:
            dispatch["claude_runtime_model"] = claude_model
    elif inputs.runtime_model_from_selection:
        raise _violation("--claude-runtime-model-from-selection needs --model-selection")
    if inputs.claude_runtime_model:
        if inputs.runtime_model_from_selection:
            raise _violation("choose ONE of --claude-runtime-model / --claude-runtime-model-from-selection")
        dispatch["claude_runtime_model"] = inputs.claude_runtime_model.strip()
    if inputs.base_ref:
        base = inputs.base_ref.strip()
        if not base or base.startswith("<"):
            raise ContractError("launch_manifest_base_ref_missing",
                                f"--base-ref {inputs.base_ref!r} does not name a remote ref (R504/R505)")
        dispatch["base_ref"] = base
    remaining = sorted(key for key, value in dispatch.items() if is_placeholder(value))
    if remaining:
        remaining.append("expected.settings_profile_sha256")
        draft["_draft_bindings"] = bindings
        return draft, remaining
    probe = dict(draft["expected"])
    probe["settings_profile_sha256"] = "0" * 64
    manifest = LaunchManifest.from_dict({"schema": draft["schema"], "expected": probe, "dispatch": dispatch},
                                        path="<draft>")
    scratch = scratch or pathlib.Path(tempfile.mkdtemp(prefix="mrl-draft-"))
    identity, _profile = observe_profile_identity(
        manifest, profile_dir=scratch / "profile", ledger_path=scratch / "subagent_ledger.json")
    draft["expected"]["settings_profile_sha256"] = identity
    draft["_draft_bindings"] = bindings
    return draft, []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.agent_supervisor.mrl_launch_draft",
        description="Draft the mrl_launch_manifest/v1 document with bound dispatch identities "
                    "(M0-T136 C-B5). Nothing here is proof: the launch re-observes everything.")
    parser.add_argument("--worktree", required=True, help="the clean task worktree to observe")
    parser.add_argument("--task-packet", required=True, help="the controlled task packet")
    parser.add_argument("--mode", choices=AUTHORIZED_MODES, default="supervised",
                        help="the mode the manifest pins; `start --mode` must equal it")
    parser.add_argument("--claude-executable", default="",
                        help="ABSOLUTE path to the Claude executable; its chain is hashed and versioned")
    parser.add_argument("--codex-executable", default="",
                        help="ABSOLUTE path to the Codex executable; its chain is hashed and versioned")
    parser.add_argument("--config", default="", help="ABSOLUTE path to the immutable config.toml")
    parser.add_argument("--model-selection", default="",
                        help="ABSOLUTE path to model_selection.toml; claude.model / codex.review_model are "
                             "pinned verbatim as dispatch.claude_model / dispatch.codex_model")
    parser.add_argument("--controller-manifest", default="",
                        help="ABSOLUTE path to the recorded controller manifest")
    parser.add_argument("--base-ref", default="",
                        help="the remote base ref the reviewer's decision binds to, e.g. refs/heads/main "
                             "(never defaulted, R504/R505)")
    runtime = parser.add_mutually_exclusive_group()
    runtime.add_argument("--claude-runtime-model", default="",
                         help="the model id the Claude RUNTIME reports (result modelUsage); pinned verbatim")
    runtime.add_argument("--claude-runtime-model-from-selection", action="store_true",
                         help="pin dispatch.claude_runtime_model equal to claude.model from --model-selection; "
                              "an explicit operator choice, verified by the launch, never a silent default")
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--unit-timeout-seconds", type=int, default=DEFAULT_UNIT_TIMEOUT_SECONDS)
    sub = parser.add_argument_group(
        "subagent contract", "each flag REPLACES the draft default outright (default: tools Read/Grep/Glob/Edit/"
        "Write/Bash/Agent, allow Read/Grep/Glob, deny Edit/Write/Bash/Agent, agents Explore, 2 concurrent / "
        "4 total; every inventory tool must be explicitly allowed or denied - R688/R692)")
    sub.add_argument("--tool", action="append", dest="tools_inventory", metavar="NAME",
                     help="a built-in tool the child may see at all (repeatable)")
    sub.add_argument("--allow-tool", action="append", dest="allow_tools", metavar="RULE",
                     help="an --allowedTools rule the child gets without asking (repeatable; must be in "
                          "the tool inventory; `Agent` is what permits subagent fan-out)")
    sub.add_argument("--deny-tool", action="append", dest="deny_tools", metavar="RULE",
                     help="an --disallowedTools rule (repeatable)")
    sub.add_argument("--agent", action="append", dest="agent_inventory", metavar="TYPE",
                     help="a subagent type the child may spawn (repeatable)")
    sub.add_argument("--max-concurrent", type=int, default=None, help="live subagents at once")
    sub.add_argument("--max-total", type=int, default=None, help="subagents per run, lifetime")
    parser.add_argument("--out", default="",
                        help="ABSOLUTE path to write the manifest to (refuses to overwrite without --force); "
                             "omitted, the draft is printed")
    parser.add_argument("--force", action="store_true", help="overwrite an existing --out file")
    parser.add_argument("--scratch", default="",
                        help="directory for the profile-identity computation (default: a temp dir)")
    return parser


def _inputs_from_args(args: argparse.Namespace) -> DraftInputs:
    return DraftInputs(
        worktree=args.worktree, task_packet=args.task_packet, mode=args.mode,
        claude_executable=args.claude_executable, codex_executable=args.codex_executable,
        config=args.config, model_selection=args.model_selection,
        controller_manifest=args.controller_manifest, base_ref=args.base_ref,
        claude_runtime_model=args.claude_runtime_model,
        runtime_model_from_selection=bool(args.claude_runtime_model_from_selection),
        max_turns=args.max_turns, unit_timeout_seconds=args.unit_timeout_seconds,
        tools_inventory=_tuple_or_none(args.tools_inventory),
        allow_tools=_tuple_or_none(args.allow_tools),
        deny_tools=_tuple_or_none(args.deny_tools),
        agent_inventory=_tuple_or_none(args.agent_inventory),
        max_concurrent=args.max_concurrent, max_total=args.max_total,
    )


def _tuple_or_none(values: "list[str] | None") -> "tuple[str, ...] | None":
    return None if values is None else tuple(values)


def _write_out(path: str, draft: dict[str, Any], *, force: bool) -> str:
    out = pathlib.Path(path)
    if not out.is_absolute():
        raise _violation(f"--out must be an absolute path, got {path!r}")
    if out.exists() and not force:
        raise _violation(f"--out {out} already exists; pass --force to overwrite it")
    out.parent.mkdir(parents=True, exist_ok=True)
    document = {k: v for k, v in draft.items() if not k.startswith("_")}
    out.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(out)


def main(argv: "list[str] | None" = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        scratch = pathlib.Path(args.scratch) if args.scratch else None
        draft, remaining = fill_draft(_inputs_from_args(args), scratch=scratch)
        if not args.out:
            print(json.dumps({k: v for k, v in draft.items() if not k.startswith("_")}, indent=2))
            return 0
        written = _write_out(args.out, draft, force=bool(args.force))
        print(json.dumps({
            "written": written,
            "task_id": draft["expected"]["task_id"],
            "head_sha": draft["expected"]["head_sha"],
            "mode": draft["expected"]["mode"],
            "settings_profile_sha256": draft["expected"]["settings_profile_sha256"],
            "remaining_placeholders": remaining,
            "bindings": draft.get("_draft_bindings", {}),
        }, indent=2))
        return 0
    except ContractError as exc:
        sys.stderr.write(f"{exc}\n")
        return 3


if __name__ == "__main__":
    sys.exit(main())
