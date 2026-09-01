#!/usr/bin/env python3
"""MRL executable-chain identity (M0-T134 / D-024 Amendment 39 R511; C3 core).

Path-only pinning already failed during this campaign, so the MRL binds a COMPLETE
SHA-256 of the FULL dispatch chain - wrapper (e.g. ``codex.cmd``/``claude.cmd``),
the actual runtime executable it invokes (e.g. ``node.exe``), and the actual
JavaScript/package entrypoint - computed immediately before every spawn, with NO
size/mtime cache in this security-critical check (a cache is exactly what a
same-size, restored-mtime replacement would defeat). It also asserts the child
environment disables the auto-updater (``DISABLE_AUTOUPDATER=1``, never the
prohibited ``DISABLE_UPDATES`` - D-024-R280) and verifies the runtime-reported
model/version against what was pinned.

Tranche A builds and unit-proves these pure functions; the live probe that supplies
the runtime-reported model/version is Tranche B (no live launch here).
"""
from __future__ import annotations

import dataclasses
import hashlib
import pathlib
from typing import Mapping, Sequence

from .mrl_worker_result import ContractError

_CHUNK = 1 << 20  # 1 MiB streaming read; the WHOLE file is always hashed


@dataclasses.dataclass(frozen=True)
class ChainLink:
    role: str
    path: str
    sha256: str
    size: int


@dataclasses.dataclass(frozen=True)
class ExecutableIdentity:
    chain: tuple[ChainLink, ...]
    combined_sha256: str


def sha256_file_complete(path: pathlib.Path) -> "tuple[str, int]":
    """Stream a COMPLETE sha256 over the entire file. No size/mtime shortcut, ever.

    Returns (hexdigest, size). The size is reported for the record only; it is
    NEVER used to decide whether to recompute the digest.
    """
    digest = hashlib.sha256()
    size = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def bind_executable_chain(links: Sequence["tuple[str, str]"]) -> ExecutableIdentity:
    """Resolve and hash the ordered dispatch chain (wrapper -> runtime -> entrypoint).

    ``links`` is an ordered list of (role, filesystem-path) pairs. Every link must
    be an existing file; each is fully hashed and the combined identity is the
    sha256 over the ordered ``role:digest`` lines, so a change to ANY link (or a
    reordering) changes the combined identity.
    """
    if not links:
        raise ContractError("contract_violation", "empty dispatch chain (nothing to bind)")
    resolved: list[ChainLink] = []
    for role, path in links:
        if not role or not str(role).strip():
            raise ContractError("contract_violation", "each chain link needs a role")
        p = pathlib.Path(path)
        if not p.is_file():
            raise ContractError("contract_violation",
                                f"dispatch-chain link {role!r} path {path!r} is not a file; fail closed")
        digest, size = sha256_file_complete(p)
        resolved.append(ChainLink(role=str(role), path=str(p), sha256=digest, size=size))
    combined = hashlib.sha256(
        "\n".join(f"{link.role}:{link.sha256}" for link in resolved).encode("utf-8")
    ).hexdigest()
    return ExecutableIdentity(chain=tuple(resolved), combined_sha256=combined)


def verify_executable_chain(
    links: Sequence["tuple[str, str]"], expected_combined_sha256: str
) -> ExecutableIdentity:
    """Re-bind the chain now and fail closed unless it matches the pinned identity.

    This is the immediately-before-spawn check: it recomputes the complete digests
    (no cache) and compares to the manifest-pinned combined identity, so a binary
    swapped after admission - even at the same size with a restored mtime - is
    rejected here.
    """
    identity = bind_executable_chain(links)
    if identity.combined_sha256 != expected_combined_sha256:
        raise ContractError(
            "contract_violation",
            f"executable-chain identity {identity.combined_sha256[:12]}.. does not match the "
            f"pinned {str(expected_combined_sha256)[:12]}..; refusing to dispatch (R511)")
    return identity


def assert_updater_disabled(child_env: Mapping[str, str]) -> None:
    """Require DISABLE_AUTOUPDATER=1 in the actual child env; refuse DISABLE_UPDATES.

    R511 requires the auto-updater be provably off in the child; R280 prohibits the
    blunt DISABLE_UPDATES switch, so its presence is itself a failure.
    """
    if "DISABLE_UPDATES" in child_env:
        raise ContractError("contract_violation",
                            "DISABLE_UPDATES is prohibited (D-024-R280); use DISABLE_AUTOUPDATER=1")
    if str(child_env.get("DISABLE_AUTOUPDATER", "")) != "1":
        raise ContractError("contract_violation",
                            "child environment must set DISABLE_AUTOUPDATER=1 before dispatch (R511)")


def verify_runtime_reported(
    expected_model: str, expected_version: str,
    observed_model: str, observed_version: str,
) -> None:
    """Fail closed unless the runtime-reported model AND version match what was pinned.

    Empty observed values fail closed (existence is never assumed to be a match).
    """
    for label, expected, observed in (("model", expected_model, observed_model),
                                       ("version", expected_version, observed_version)):
        if not str(observed).strip():
            raise ContractError("contract_violation",
                                f"runtime reported no {label}; fail closed (never assume a match)")
        if observed != expected:
            raise ContractError("contract_violation",
                                f"runtime-reported {label} {observed!r} != pinned {expected!r} (R511)")
