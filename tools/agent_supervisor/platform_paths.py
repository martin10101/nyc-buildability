#!/usr/bin/env python3
"""Platform-correct default locations for the controller (D-091 T1).

The loop was built for the owner's Windows PC; D-091 moves it to a Linux cloud
server. The runbook and B-026 name three Windows-only locations:

    config      C:\\Program Files\\SupervisorConfig\\config.toml   (admin-owned)
    activation  %LOCALAPPDATA%\\NYCBuildabilitySupervisor\\ctl24-activation\\
                  controller_manifest.json                         (outside the repo)
    runtime     %LOCALAPPDATA%\\NYCBuildabilitySupervisor\\<sha256-of-checkout>\\

This module is the ONE resolver for those defaults, so a Linux deployment,
launcher, or runbook step resolves a Linux path instead of hardcoding a Windows
one. No Windows path (no ``C:\\``, no ``%LOCALAPPDATA%``) is ever returned on a
POSIX platform, and the Windows branch is byte-identical to the existing runbook
locations, so Windows behavior is unchanged.

The runtime base is NOT reimplemented here: it already resolves cross-platform in
`durable_state.runtime_base_dir` (keyed by the checkout-path hash), so this module
delegates to it to keep a single source of truth that cannot drift.

Callers still pass an explicit ``--config`` / ``--manifest``; these are the
DEFAULTS a platform-aware caller resolves, not a new implicit search path. The
platform decision and the environment are injectable (`os_name`, `environ`) so
both branches are testable on either host.

Stdlib only. No third-party dependency.
"""
from __future__ import annotations

import os
import pathlib
from typing import Mapping

#: Windows: the protected config lives under %ProgramFiles%\<dir>\<file>.
WINDOWS_CONFIG_DIR_NAME = "SupervisorConfig"
CONFIG_FILENAME = "config.toml"

#: POSIX: the protected config lives in a root-owned system directory, verified by
#: `posix_acl` (root-owned, not group/world-writable, not a symlink).
POSIX_CONFIG_DIR = "/etc/nyc-supervisor"

#: The activation directory (holds controller_manifest.json) lives OUTSIDE the
#: repo tree on both platforms, so the certified git tree stays clean.
ACTIVATION_SUBDIR = "ctl24-activation"
#: POSIX activation lives under the per-user config home; this is its app folder.
POSIX_APP_DIR_NAME = "nyc-supervisor"


def _is_windows(os_name: str | None) -> bool:
    """Resolve the platform decision, injectable for tests on any host. Only
    ``nt`` is Windows; every other platform resolves POSIX paths, so a Windows
    path is never emitted off Windows."""
    return (os.name if os_name is None else os_name) == "nt"


def _env(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def _home(environ: Mapping[str, str] | None) -> pathlib.Path:
    env = _env(environ)
    home = env.get("HOME")
    return pathlib.Path(home) if home else pathlib.Path.home()


def default_config_path(*, os_name: str | None = None,
                        environ: Mapping[str, str] | None = None) -> pathlib.Path:
    """Default location of the IMMUTABLE controller config.

    Windows -> %ProgramFiles%\\SupervisorConfig\\config.toml (admin-owned).
    POSIX   -> /etc/nyc-supervisor/config.toml (root-owned).
    """
    if _is_windows(os_name):
        program_files = _env(environ).get("ProgramFiles", r"C:\Program Files")
        return pathlib.Path(program_files) / WINDOWS_CONFIG_DIR_NAME / CONFIG_FILENAME
    return pathlib.Path(POSIX_CONFIG_DIR) / CONFIG_FILENAME


def default_activation_dir(*, os_name: str | None = None,
                           environ: Mapping[str, str] | None = None) -> pathlib.Path:
    """Default activation directory (where controller_manifest.json is recorded),
    OUTSIDE the repo tree.

    Windows -> %LOCALAPPDATA%\\NYCBuildabilitySupervisor\\ctl24-activation.
    POSIX   -> ($XDG_CONFIG_HOME or ~/.config)/nyc-supervisor/ctl24-activation.
    """
    if _is_windows(os_name):
        from .durable_state import APP_DIR_NAME
        local = _env(environ).get("LOCALAPPDATA")
        if not local:
            raise ValueError(
                "LOCALAPPDATA is not set; cannot locate the activation directory")
        return pathlib.Path(local) / APP_DIR_NAME / ACTIVATION_SUBDIR
    env = _env(environ)
    config_home = env.get("XDG_CONFIG_HOME")
    base = pathlib.Path(config_home) if config_home else _home(environ) / ".config"
    return base / POSIX_APP_DIR_NAME / ACTIVATION_SUBDIR


def default_manifest_path(*, os_name: str | None = None,
                          environ: Mapping[str, str] | None = None) -> pathlib.Path:
    """Default controller_manifest.json path inside the activation directory. The
    filename comes from `manifest.MANIFEST_FILENAME` so it cannot drift."""
    from .manifest import MANIFEST_FILENAME
    return default_activation_dir(os_name=os_name, environ=environ) / MANIFEST_FILENAME


def runtime_base_dir() -> pathlib.Path:
    """The per-user runtime base directory, delegated to `durable_state` (one
    source of truth; already cross-platform and keyed by the checkout-path hash).
    POSIX -> ($XDG_STATE_HOME or ~/.local/state)/NYCBuildabilitySupervisor."""
    from .durable_state import runtime_base_dir as _runtime_base_dir
    return _runtime_base_dir()
