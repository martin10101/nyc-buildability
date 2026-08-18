#!/usr/bin/env python3
"""Controller manifest: generation and verification (D-007 S13.1).

The active supervisor verifies a digest manifest covering its own code, policy
rules, schemas, review prompts, the immutable controller configuration, and
launcher scripts - at startup and before every forwarded action. ANY change
halts the run. Claude, Codex, repository text, hooks, tests, and task code may
never modify the active controller.

`model_selection.toml` is DELIBERATELY OUTSIDE the manifest (S3.1): its digest is
recorded with every decision and it changes only through the owner-authenticated
path, but editing it must never invalidate the controller. `EXCLUDED_NAMES`
enforces that, and a test asserts it.

Deviation note (S6 layout): S6's intended file list does not name a manifest
module, yet S13.1 requires manifest generation and verification. This module is
therefore an addition to the S6 shape, not a rename of anything in it.

Phase 1 scope note: generation, verification, and halt-on-change are complete.
The controller-update PROCESS around them (stop the controller, separate
controlled task, independent review, new version, replay corpus, explicit
operator restart, keep the old version for rollback) is an operational procedure
documented in README.md; it is not code and is not automated - S13.1 is explicit
that the supervisor never supervises its own live update.
"""
from __future__ import annotations

import dataclasses
import fnmatch
import json
import os
import pathlib
from typing import Any, Iterable, Sequence

from . import CONTROLLER_VERSION
from .models import digest_of, sha256_hex, to_utc_iso

MANIFEST_FILENAME = "controller_manifest.json"

#: The runtime model selection is never manifest-covered (S3.1).
MODEL_SELECTION_FILENAME = "model_selection.toml"

#: The stable logical manifest name for the ACTIVE immutable config, which lives
#: OUTSIDE the package directory (an operator-chosen protected location). The
#: manifest records this logical name and the file's digest - never its absolute
#: private path (M0-T072, D-017-R039/R040).
CONFIG_LOGICAL_NAME = "config.toml"

#: Glob patterns covered by the manifest, relative to the controller root.
COVERED_PATTERNS: tuple[str, ...] = (
    "*.py",
    "schemas/*.json",
    "prompts/*.md",
    "config.toml",
    "config.example.toml",
    "launchers/*.cmd",
    "launchers/*.ps1",
    "README.md",
)

#: Never covered, whatever the patterns say.
EXCLUDED_NAMES: frozenset[str] = frozenset({
    MODEL_SELECTION_FILENAME,
    MANIFEST_FILENAME,
})

EXCLUDED_DIR_PARTS: frozenset[str] = frozenset({"__pycache__", ".pytest_cache", ".git"})


class ManifestError(Exception):
    """The manifest could not be built or read."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class ManifestVerification:
    """Result of verifying a controller root against a recorded manifest."""

    ok: bool
    changed: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    unexpected: tuple[str, ...] = ()
    manifest_digest: str = ""
    message: str = ""
    #: Machine-readable failure class for the config-binding pre-checks
    #: (M0-T072): "" on success or ordinary content drift; otherwise one of
    #: manifest_stale | manifest_patterns_mismatch |
    #: config_duplicated_in_package | manifest_missing_config |
    #: config_path_missing (see verify_manifest_with_config's ordered contract).
    reason_code: str = ""

    def halt_reason(self) -> str:
        """A single operator-readable reason, or "" when nothing changed."""
        if self.ok:
            return ""
        parts: list[str] = []
        if self.changed:
            parts.append(f"changed: {list(self.changed)}")
        if self.missing:
            parts.append(f"missing: {list(self.missing)}")
        if self.unexpected:
            parts.append(f"unexpected: {list(self.unexpected)}")
        return "controller manifest verification failed - " + "; ".join(parts)


def _is_excluded(relative: pathlib.PurePath) -> bool:
    if relative.name in EXCLUDED_NAMES:
        return True
    return any(part in EXCLUDED_DIR_PARTS for part in relative.parts)


def covered_files(
    root: str | os.PathLike[str],
    *,
    patterns: Sequence[str] = COVERED_PATTERNS,
) -> list[pathlib.Path]:
    """Every file the manifest covers, sorted, relative paths resolved from `root`."""
    root_path = pathlib.Path(root).resolve()
    if not root_path.is_dir():
        raise ManifestError("missing_root", f"controller root not found: {root_path}")

    found: set[pathlib.Path] = set()
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root_path)
        if _is_excluded(relative):
            continue
        posix = relative.as_posix()
        if any(fnmatch.fnmatch(posix, pattern) for pattern in patterns):
            found.add(relative)
    return sorted(found)


def _hash_file(path: pathlib.Path) -> str:
    """SHA-256 of the file's bytes, with line endings normalized to LF.

    Normalizing means a CRLF checkout on Windows and an LF checkout in CI produce
    the same manifest, so the manifest detects real content changes rather than
    checkout settings. Binary files are not expected under the covered patterns.
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return sha256_hex(data)


def generate_manifest(
    root: str | os.PathLike[str],
    *,
    patterns: Sequence[str] = COVERED_PATTERNS,
    extra_files: Iterable[tuple[str, str | os.PathLike[str]]] = (),
    controller_version: str = CONTROLLER_VERSION,
) -> dict[str, Any]:
    """Build a manifest over `root`, plus any externally located covered files.

    `extra_files` carries `(logical_name, path)` pairs - used for the active
    `config.toml` when it lives outside the package directory. A logical name
    equal to `model_selection.toml` is refused outright.
    """
    root_path = pathlib.Path(root).resolve()
    entries: dict[str, str] = {}

    for relative in covered_files(root_path, patterns=patterns):
        entries[relative.as_posix()] = _hash_file(root_path / relative)

    for logical_name, path in extra_files:
        if pathlib.PurePath(logical_name).name in EXCLUDED_NAMES:
            raise ManifestError(
                "excluded_file_offered",
                f"{logical_name!r} is deliberately outside the controller manifest; "
                f"covering it would make an authenticated model change invalidate the "
                f"controller (S3.1)")
        file_path = pathlib.Path(path)
        if not file_path.is_file():
            raise ManifestError("missing_extra_file", f"covered file not found: {file_path}")
        entries[logical_name] = _hash_file(file_path)

    manifest = {
        "manifest_version": 1,
        "controller_version": controller_version,
        "generated_at_utc": to_utc_iso(),
        "root": root_path.name,
        "patterns": list(patterns),
        "excluded": sorted(EXCLUDED_NAMES),
        "files": dict(sorted(entries.items())),
    }
    # M0-T072 G4-C1: `patterns` is inside the recorded digest. It defines what
    # the manifest COVERS; leaving it outside let an edited manifest narrow its
    # own coverage to nothing while staying self-consistent.
    manifest["manifest_digest"] = digest_of(
        {"files": manifest["files"], "controller_version": controller_version,
         "patterns": manifest["patterns"]})
    return manifest


def write_manifest(manifest: dict[str, Any], path: str | os.PathLike[str]) -> pathlib.Path:
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def read_manifest(path: str | os.PathLike[str]) -> dict[str, Any]:
    source = pathlib.Path(path)
    if not source.exists():
        raise ManifestError("missing_manifest", f"manifest not found: {source}")
    try:
        data = json.loads(source.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ManifestError("invalid_manifest", f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or "files" not in data:
        raise ManifestError("invalid_manifest", "manifest has no `files` map")
    return data


def verify_manifest(
    root: str | os.PathLike[str],
    manifest: dict[str, Any],
    *,
    extra_files: Iterable[tuple[str, str | os.PathLike[str]]] = (),
) -> ManifestVerification:
    """Recompute digests and compare. ANY difference means halt (S13.1)."""
    root_path = pathlib.Path(root).resolve()
    recorded: dict[str, str] = dict(manifest.get("files", {}))
    patterns = tuple(manifest.get("patterns", COVERED_PATTERNS))

    observed: dict[str, str] = {}
    for relative in covered_files(root_path, patterns=patterns):
        observed[relative.as_posix()] = _hash_file(root_path / relative)
    for logical_name, path in extra_files:
        file_path = pathlib.Path(path)
        if file_path.is_file():
            observed[logical_name] = _hash_file(file_path)

    changed = sorted(
        name for name, digest in recorded.items()
        if name in observed and observed[name] != digest)
    missing = sorted(name for name in recorded if name not in observed)
    unexpected = sorted(name for name in observed if name not in recorded)

    ok = not (changed or missing or unexpected)
    verification = ManifestVerification(
        ok=ok,
        changed=tuple(changed),
        missing=tuple(missing),
        unexpected=tuple(unexpected),
        manifest_digest=str(manifest.get("manifest_digest", "")),
    )
    return dataclasses.replace(verification, message=verification.halt_reason())


def require_verified(
    root: str | os.PathLike[str],
    manifest: dict[str, Any],
    *,
    extra_files: Iterable[tuple[str, str | os.PathLike[str]]] = (),
) -> ManifestVerification:
    """Verify and raise on any change. Callers use this before a forwarded action."""
    verification = verify_manifest(root, manifest, extra_files=extra_files)
    if not verification.ok:
        raise ManifestError("manifest_changed", verification.halt_reason())
    return verification


def _failure(reason_code: str, message: str, manifest: dict[str, Any]) -> ManifestVerification:
    return ManifestVerification(
        ok=False,
        manifest_digest=str(manifest.get("manifest_digest", "")),
        message=message,
        reason_code=reason_code,
    )


def manifest_is_stale(
    manifest: dict[str, Any],
    *,
    running_controller_version: str = CONTROLLER_VERSION,
) -> str:
    """Deterministic staleness verdict for a recorded manifest.

    A manifest is STALE when (a) it was recorded for a different controller
    version than the one running, or (b) its recorded `manifest_digest` no
    longer matches the digest recomputed over its own recorded files and
    version - an internally inconsistent (edited) manifest. Returns "" when
    fresh, else a human-readable reason (M0-T072, D-017-R045).
    """
    recorded_version = manifest.get("controller_version")
    if recorded_version != running_controller_version:
        return (f"manifest was recorded for controller version {recorded_version!r} "
                f"but {running_controller_version!r} is running")
    expected = digest_of(
        {"files": dict(manifest.get("files", {})),
         "controller_version": recorded_version,
         "patterns": list(manifest.get("patterns", []))})
    recorded_digest = manifest.get("manifest_digest")
    if recorded_digest != expected:
        # A self-consistency check, not an authenticity control: it catches
        # accidental or partial edits, while a deliberate edit that recomputes
        # the digest passes. Authenticity comes from the digests matching the
        # live tree plus review of any manifest change.
        return (f"manifest_digest {str(recorded_digest)[:16]}... does not match the digest "
                f"recomputed over the manifest's own recorded files/version/patterns "
                f"({expected[:16]}...); the manifest was edited after recording")
    return ""


def verify_manifest_with_config(
    root: str | os.PathLike[str],
    manifest: dict[str, Any],
    config_path: str | os.PathLike[str] | None,
    *,
    running_controller_version: str = CONTROLLER_VERSION,
) -> ManifestVerification:
    """The PRODUCTION manifest check: package tree AND the external immutable config.

    Fail-closed order (M0-T072, D-017-R042..R045); `reason_code` values:
    1. `manifest_stale`               - wrong controller version, or the recorded
                                        digest no longer matches the manifest's own
                                        recorded files/version/patterns;
    2. `manifest_patterns_mismatch`   - the manifest does not carry the canonical
                                        COVERED_PATTERNS, so it could attest to a
                                        narrowed (even empty) coverage;
    3. `config_duplicated_in_package` - a config.toml inside the package tree
                                        would shadow the external binding;
    4. `manifest_missing_config`      - the manifest does not bind `config.toml`;
    5. `config_path_missing`          - no external config path was supplied, so
                                        the recorded binding cannot be verified;
    6. ordinary content verification with the external config bound under its
       stable logical name (a missing file reports `missing`, a byte change
       reports `changed` - both halt).

    `model_selection.toml` stays outside the manifest by design (S3.1): a model
    change never invalidates the controller.
    """
    stale = manifest_is_stale(
        manifest, running_controller_version=running_controller_version)
    if stale:
        return _failure("manifest_stale", f"stale manifest - {stale}", manifest)
    if tuple(manifest.get("patterns", ())) != tuple(COVERED_PATTERNS):
        return _failure(
            "manifest_patterns_mismatch",
            f"the manifest's coverage patterns {manifest.get('patterns')!r} are not "
            f"the canonical COVERED_PATTERNS; a production manifest may never narrow "
            f"its own coverage (G4-C1). Re-record it with `record-manifest`",
            manifest)
    package_root = pathlib.Path(root).resolve()
    duplicates = [p for p in package_root.rglob(CONFIG_LOGICAL_NAME)
                  if not any(part in EXCLUDED_DIR_PARTS for part in
                             p.relative_to(package_root).parts)]
    if duplicates:
        return _failure(
            "config_duplicated_in_package",
            f"a {CONFIG_LOGICAL_NAME!r} exists INSIDE the package tree "
            f"({duplicates[0]}); it would shadow the external binding. The "
            f"active immutable config must live outside the package "
            f"(D-017-R048) - remove the in-package copy",
            manifest)
    if CONFIG_LOGICAL_NAME not in manifest.get("files", {}):
        return _failure(
            "manifest_missing_config",
            f"the manifest does not bind the active immutable config: no "
            f"{CONFIG_LOGICAL_NAME!r} entry. Production dispatch never accepts a "
            f"manifest that fails to bind its config; re-record it with "
            f"`record-manifest --config <path>`",
            manifest)
    if config_path is None:
        return _failure(
            "config_path_missing",
            f"the manifest binds {CONFIG_LOGICAL_NAME!r} but no --config path was "
            f"supplied, so the binding cannot be verified. Supply the active "
            f"immutable config path",
            manifest)
    return verify_manifest(
        root, manifest, extra_files=((CONFIG_LOGICAL_NAME, config_path),))
