#!/usr/bin/env python3
"""MRL executable-chain resolution and immediately-before-spawn binding
(M0-T136 Tranche B cluster C-B2; D-024-R561..R565).

Tranche A (``mrl_exec_identity``) proved the pure primitives: complete streaming
SHA-256 with no size/mtime shortcut, ordered-chain binding, updater-env assertion
and runtime model/version comparison. This module adds what the dispatch path
was missing (failure surface F7-F11, F30):

* **Chain resolution** for the shapes that really exist on the owner's machine,
  measured, not assumed: a native executable (one link: the file IS wrapper,
  runtime and entrypoint); an npm ``.cmd`` shim that calls a native binary
  (``claude.cmd`` -> ``claude.exe``); and an npm shim that runs ``node`` on a
  JavaScript entrypoint (``codex.cmd`` -> ``node.exe`` -> ``codex.js``) whose
  entrypoint delegates to a platform vendor binary resolved exactly the way
  ``codex.js`` does it (``require.resolve`` ancestor walk, then ``<pkg>/vendor``).
  The shim text is PARSED; nothing is inferred from a filename alone.
* **Binding now**: every link of the resolved chain is fully re-hashed at the
  moment of the call (``bind_executable_chain`` streams the whole file; there is
  no cache anywhere in this module), and compared to the manifest-pinned combined
  identity. A same-size, restored-mtime replacement, a retargeted wrapper, or a
  replaced entrypoint therefore changes the identity and refuses the spawn.
* **Child-env verification** on the exact mapping handed to ``Popen``.
* **Runtime-reported identity**: version parsed from the bound chain's own
  ``--version`` output, model from the one-shot result's ``modelUsage`` keys;
  absence never counts as a match (fail closed).

Import direction: ``mrl_exec_identity`` and ``mrl_worker_result`` only; nothing
imports back. No third-party dependency.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import platform as _platform
import re
import shutil
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence

from .mrl_exec_identity import (
    ExecutableIdentity,
    assert_updater_disabled,
    bind_executable_chain,
    verify_executable_chain,
    verify_runtime_reported,
)
from .mrl_worker_result import ContractError

CHAIN_KINDS = ("claude", "codex")

#: Shapes this resolver can PROVE from the filesystem (recorded in the launch record).
SHAPE_NATIVE = "native"
SHAPE_SHIM_NATIVE = "npm-shim->native"
SHAPE_SHIM_NODE = "npm-shim->node->entrypoint"
SHAPE_SHIM_NODE_VENDOR = "npm-shim->node->entrypoint->vendor"

_DP0_REF = re.compile(r'"%dp0%\\([^"]+)"')
_PROG_NODE = re.compile(r'SET\s+"_prog=%dp0%\\node\.exe"', re.IGNORECASE)
_VERSION = re.compile(r"(\d+\.\d+\.\d+)")

#: Mirrors PLATFORM_PACKAGE_BY_TARGET in @openai/codex/bin/codex.js (measured 0.146.0).
_CODEX_TRIPLES = {
    ("win32", "x64"): "x86_64-pc-windows-msvc",
    ("win32", "arm64"): "aarch64-pc-windows-msvc",
    ("darwin", "x64"): "x86_64-apple-darwin",
    ("darwin", "arm64"): "aarch64-apple-darwin",
    ("linux", "x64"): "x86_64-unknown-linux-musl",
    ("linux", "arm64"): "aarch64-unknown-linux-musl",
}
_CODEX_PLATFORM_PKG = {
    "x86_64-pc-windows-msvc": "@openai/codex-win32-x64",
    "aarch64-pc-windows-msvc": "@openai/codex-win32-arm64",
    "x86_64-apple-darwin": "@openai/codex-darwin-x64",
    "aarch64-apple-darwin": "@openai/codex-darwin-arm64",
    "x86_64-unknown-linux-musl": "@openai/codex-linux-x64",
    "aarch64-unknown-linux-musl": "@openai/codex-linux-arm64",
}


@dataclasses.dataclass(frozen=True)
class ResolvedChain:
    """The ordered (role, path) chain a provider spawn really executes."""

    kind: str
    shape: str
    links: tuple[tuple[str, str], ...]

    @property
    def executable(self) -> str:
        return self.links[0][1]


def _violation(message: str) -> ContractError:
    return ContractError("contract_violation", message)


def _node_arch(machine: str) -> str:
    m = machine.lower()
    if m in ("amd64", "x86_64", "x64"):
        return "x64"
    if m in ("arm64", "aarch64"):
        return "arm64"
    raise _violation(f"unsupported machine architecture {machine!r} for the codex vendor binary")


def codex_target_triple(sys_platform: str = sys.platform, machine: str = "") -> str:
    """The codex.js target triple for this host (fail closed on unsupported hosts)."""
    key = (sys_platform, _node_arch(machine or _platform.machine()))
    triple = _CODEX_TRIPLES.get(key)
    if triple is None:
        raise _violation(f"unsupported platform/arch {key} for the codex vendor binary")
    return triple


def parse_npm_shim(text: str) -> "tuple[list[str], bool]":
    """Return (dp0-relative references in order, runtime-is-node) from an npm .cmd shim.

    A ``.cmd`` that carries no ``"%dp0%\\..."`` reference is not an npm shim and
    is refused (the chain would otherwise be guessed).
    """
    refs = _DP0_REF.findall(text)
    if not refs:
        raise _violation("wrapper .cmd carries no %dp0% target reference; not a parseable npm shim")
    return refs, bool(_PROG_NODE.search(text))


def _resolve_codex_vendor(entrypoint: pathlib.Path, triple: str) -> pathlib.Path:
    """Locate the vendor binary the way codex.js does: require.resolve ancestor walk,
    then ``<package>/vendor``. Fail closed when neither exists."""
    pkg = _CODEX_PLATFORM_PKG[triple]
    name = "codex.exe" if triple.endswith("windows-msvc") else "codex"
    tail = pathlib.Path(triple) / "bin" / name
    for ancestor in entrypoint.parents:
        candidate = ancestor / "node_modules" / pkg / "package.json"
        if candidate.is_file():
            vendor = candidate.parent / "vendor" / tail
            if vendor.is_file():
                return vendor
            raise _violation(f"codex platform package {pkg} found at {candidate.parent} but its vendor "
                             f"binary {vendor} is missing; refusing to guess")
    fallback = entrypoint.parent.parent / "vendor" / tail
    if fallback.is_file():
        return fallback
    raise _violation(f"codex vendor binary not found for {triple} from entrypoint {entrypoint}")


def _entrypoint_delegates_to_codex(entrypoint: pathlib.Path) -> bool:
    manifest = entrypoint.parent.parent / "package.json"
    if not manifest.is_file():
        return False
    try:
        return json.loads(manifest.read_text(encoding="utf-8-sig")).get("name") == "@openai/codex"
    except (OSError, ValueError):
        return False


def resolve_chain(
    executable: str,
    kind: str,
    *,
    which: Callable[[str], "str | None"] = shutil.which,
    sys_platform: str = sys.platform,
    machine: str = "",
) -> ResolvedChain:
    """Resolve the real wrapper -> runtime -> entrypoint (-> vendor) chain of ``executable``.

    Every link must exist as a file at resolution time; any unresolvable step
    raises ``ContractError`` rather than falling back to a partial chain.
    """
    if kind not in CHAIN_KINDS:
        raise _violation(f"unknown chain kind {kind!r}; expected one of {CHAIN_KINDS}")
    if not isinstance(executable, str) or not executable.strip():
        raise _violation(f"{kind} executable path is required")
    head = pathlib.Path(executable)
    if not head.is_absolute():
        raise _violation(f"{kind} executable must be an absolute path, got {executable!r}")
    if not head.is_file():
        raise _violation(f"{kind} executable {executable!r} is not a file; fail closed")
    suffix = head.suffix.lower()
    if suffix in (".cmd", ".bat"):
        refs, runtime_is_node = parse_npm_shim(head.read_text(encoding="utf-8", errors="replace"))
        dp0 = head.parent
        targets = [dp0 / ref for ref in refs if ref.lower() != "node.exe"]
        if len(targets) != 1:
            raise _violation(f"npm shim {head} references {len(targets)} targets; expected exactly one")
        target = targets[0]
        if not target.is_file():
            raise _violation(f"npm shim {head} targets missing file {target}")
        if not runtime_is_node:
            return ResolvedChain(kind, SHAPE_SHIM_NATIVE, ((f"{kind}-wrapper", str(head)),
                                                            (f"{kind}-runtime", str(target))))
        local_node = dp0 / "node.exe"
        if local_node.is_file():
            node = local_node
        else:
            found = which("node")
            if not found:
                raise _violation(f"npm shim {head} needs `node` on PATH and none was found")
            node = pathlib.Path(found)
        links = [(f"{kind}-wrapper", str(head)), (f"{kind}-runtime", str(node)),
                 (f"{kind}-entrypoint", str(target))]
        shape = SHAPE_SHIM_NODE
        if _entrypoint_delegates_to_codex(target):
            vendor = _resolve_codex_vendor(target, codex_target_triple(sys_platform, machine))
            links.append((f"{kind}-vendor", str(vendor)))
            shape = SHAPE_SHIM_NODE_VENDOR
        return ResolvedChain(kind, shape, tuple(links))
    if suffix in (".exe", "") or sys_platform != "win32":
        return ResolvedChain(kind, SHAPE_NATIVE, ((f"{kind}-executable", str(head)),))
    raise _violation(f"{kind} executable {executable!r} has unsupported suffix {suffix!r}")


def bind_chain_now(chain: ResolvedChain) -> ExecutableIdentity:
    """Hash every link of the chain NOW (complete streaming SHA-256, no cache)."""
    return bind_executable_chain(chain.links)


def verify_chain_now(chain: ResolvedChain, expected_combined_sha256: str) -> ExecutableIdentity:
    """Re-hash the whole chain immediately before a spawn and refuse on any mismatch."""
    if not isinstance(expected_combined_sha256, str) or len(expected_combined_sha256) != 64:
        raise _violation(f"{chain.kind} chain has no pinned 64-hex combined identity to verify against")
    return verify_executable_chain(chain.links, expected_combined_sha256)


def chain_record(chain: ResolvedChain, identity: ExecutableIdentity) -> dict[str, Any]:
    """Serializable launch-record entry (roles, paths, complete digests, sizes)."""
    return {
        "kind": chain.kind,
        "shape": chain.shape,
        "combined_sha256": identity.combined_sha256,
        "links": [dataclasses.asdict(link) for link in identity.chain],
    }


def verify_child_env(env: Mapping[str, str]) -> None:
    """Assert the EXACT environment mapping that will be passed to Popen disables the
    auto-updater (D-024-R563). Call it on the same object handed to ``env=``."""
    if not isinstance(env, Mapping):
        raise _violation("child env must be the mapping passed to Popen, not None/inherited")
    assert_updater_disabled(env)


RunVersion = Callable[[Sequence[str]], "tuple[int, str, str]"]


def _default_run_version(argv: Sequence[str]) -> "tuple[int, str, str]":  # pragma: no cover - live spawn
    proc = subprocess.run(list(argv), capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


def parse_version(text: str) -> str:
    """Extract ``MAJOR.MINOR.PATCH`` from ``--version`` output; empty when absent."""
    match = _VERSION.search(text or "")
    return match.group(1) if match else ""


def observe_version(chain: ResolvedChain, *, run: RunVersion | None = None) -> str:
    """Ask the BOUND chain head for its version (``<executable> --version``).

    Returns the parsed version string; a non-zero exit or unparseable output
    yields "" so that ``verify_runtime_reported`` fails closed.
    """
    run = run or _default_run_version
    try:
        returncode, stdout, stderr = run([chain.executable, "--version"])
    except (OSError, subprocess.SubprocessError):
        return ""
    if returncode != 0:
        return ""
    return parse_version(stdout) or parse_version(stderr)


def observed_model_from_result(result: Mapping[str, Any]) -> str:
    """The model the one-shot RUNTIME reports having used (result ``modelUsage`` keys).

    Exactly one distinct model must appear; zero or several models yield "" so the
    caller's ``verify_runtime_reported`` fails closed (a run that touched a second
    model is not the pinned run).
    """
    if not isinstance(result, Mapping):
        return ""
    usage = result.get("modelUsage")
    if not isinstance(usage, Mapping):
        return ""
    models = sorted(str(k) for k in usage.keys() if str(k).strip())
    return models[0] if len(models) == 1 else ""


def verify_runtime_identity(
    *, expected_model: str, expected_version: str, observed_model: str, observed_version: str
) -> None:
    """Runtime model AND version must equal what the launch manifest pinned (R564)."""
    verify_runtime_reported(expected_model, expected_version, observed_model, observed_version)


__all__ = [
    "CHAIN_KINDS", "SHAPE_NATIVE", "SHAPE_SHIM_NATIVE", "SHAPE_SHIM_NODE", "SHAPE_SHIM_NODE_VENDOR",
    "ResolvedChain", "resolve_chain", "parse_npm_shim", "codex_target_triple",
    "bind_chain_now", "verify_chain_now", "chain_record", "verify_child_env",
    "observe_version", "parse_version", "observed_model_from_result", "verify_runtime_identity",
]
