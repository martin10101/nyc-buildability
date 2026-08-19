#!/usr/bin/env python3
"""THE shared canonical repository-path + real-path containment rule (M0-T075).

One rule for every context-related file read (D-018-R031..R034): compiler
--include and task-derived paths, deep source views, graph/view seeds,
ontology resolution inputs, and memory evidence paths all validate here.

Two layers, both mandatory for a read:

  1. **Canonical form** (`is_canonical_repo_path`): a repo-relative POSIX
     path with no absolute/drive form, no backslashes, no empty or '.'/'..'
     segments, no doubled separators, no leading '/'. Anything else refuses
     with `non_canonical_path`.
  2. **Real-path containment** (`contained_repo_path`): the candidate's
     resolved real path (symlinks/junctions followed) must remain inside the
     resolved repository root; a link whose target leaves the checkout
     refuses with `path_escapes_repository`.

Error discipline (R034): a `PathContainmentError` NEVER carries an absolute
path — only the bounded repo-relative input string the caller supplied.

STDLIB ONLY. Windows + POSIX. `memory_digest.is_canonical_repo_path` remains
the public compatibility name and delegates here (single source of truth).
"""
from __future__ import annotations

import os
import pathlib

CONTAINMENT_VERSION = "1.0.0"

_MAX_ERR_CHARS = 120


class PathContainmentError(Exception):
    """Fail-closed containment refusal with a machine-readable code.

    `detail` NEVER repeats a private absolute/drive/traversal path (M0-T076 /
    D-019-R024): a caller-supplied string is echoed ONLY when it is a canonical
    repo-relative path (safe to disclose, e.g. a symlink that escapes at resolve
    time); any non-canonical supplied string — an absolute path, a drive path,
    a `..` traversal, backslashes — is redacted to a fixed marker so the error
    (and any packet/omission/stderr carrying it) cannot leak it.
    """

    def __init__(self, code: str, supplied: object):
        self.code = code
        if is_canonical_repo_path(supplied):
            shown = repr(str(supplied))[:_MAX_ERR_CHARS]
            self.detail = f"refused context path {shown}"
        else:
            self.detail = f"refused non-canonical context path [redacted:{code}]"
        super().__init__(f"{code}: {self.detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def redact_context_ref(p: object) -> str:
    """A disclosure-safe rendering of a caller-supplied context reference.

    Returns the canonical repo-relative string unchanged (safe to record) or a
    fixed redaction marker for any non-canonical/absolute/traversal input, so
    error details, omission reasons, and packet metadata never repeat a private
    absolute path (D-019-R024)."""
    return str(p) if is_canonical_repo_path(p) else "[redacted:non_canonical_path]"


def is_canonical_repo_path(p: object) -> bool:
    """True only for a canonical repo-relative POSIX path (D-018-R032)."""
    if not isinstance(p, str) or not p:
        return False
    if "\\" in p or ":" in p or p.startswith("/"):
        return False
    if any(ord(c) < 32 for c in p):
        return False
    return all(seg not in ("", ".", "..") for seg in p.split("/"))


def contained_repo_path(repo_root: str | os.PathLike[str], p: object) -> pathlib.Path:
    """Validate + contain one repo-relative path; return the joined Path.

    Raises PathContainmentError(`non_canonical_path`) on any non-canonical
    form and (`path_escapes_repository`) when the REAL resolved target —
    following symlinks/junctions on any component — leaves the resolved
    repository root. The returned Path is the plain join (callers read
    through it normally; the escape check has already been done on the real
    path).
    """
    if not is_canonical_repo_path(p):
        raise PathContainmentError("non_canonical_path", p)
    root_real = os.path.realpath(os.fspath(repo_root))
    candidate = os.path.join(root_real, *str(p).split("/"))
    cand_real = os.path.realpath(candidate)
    base = os.path.normcase(root_real).rstrip("\\/")
    target = os.path.normcase(cand_real)
    if not (target == base or target.startswith(base + os.sep)):
        raise PathContainmentError("path_escapes_repository", p)
    return pathlib.Path(candidate)


def contained_read_bytes(repo_root: str | os.PathLike[str], p: object,
                         max_bytes: int | None = None) -> bytes:
    """Contained bounded read. Missing/unreadable files raise
    PathContainmentError(`path_not_readable`) with the bounded detail only."""
    path = contained_repo_path(repo_root, p)
    try:
        data = path.read_bytes()
    except OSError:
        raise PathContainmentError("path_not_readable", p) from None
    if max_bytes is not None and len(data) > max_bytes:
        return data[:max_bytes]
    return data


def contained_exists(repo_root: str | os.PathLike[str], p: object) -> bool:
    """Contained existence check; a refused path simply does not exist for
    the caller (used where existence feeds an honest no-answer, not an error)."""
    try:
        return contained_repo_path(repo_root, p).exists()
    except PathContainmentError:
        return False
