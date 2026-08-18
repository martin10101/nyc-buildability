#!/usr/bin/env python3
"""Deterministic I/O primitives for the context-pack builder (M0-T065 Unit B).

The low-level, side-effect-bounded helpers shared by the source, render, and
assembly layers: content hashing, canonical JSON, repo-relative paths, tolerant
file reads, and a bounded git invocation. Kept in one leaf module (imports
nothing else in the package) so every layer shares ONE implementation and there
is no import cycle. Deterministic: no wall-clock, stable ordering, UTF-8.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon_json_bytes(obj) -> bytes:
    """Canonical, human-readable JSON: sorted keys, UTF-8, trailing newline."""
    text = json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def rel_posix(path: str, repo: str) -> str:
    """Repo-relative path with POSIX separators (stable across Win/Linux)."""
    try:
        rel = os.path.relpath(path, repo)
    except ValueError:
        rel = path
    return rel.replace(os.sep, "/")


def read_text(path: str) -> str | None:
    try:
        with open(path, "rb") as fh:
            return fh.read().decode("utf-8", errors="replace")
    except OSError:
        return None


def load_json(path: str):
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return None


def run_git(repo: str, args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return proc.returncode, proc.stdout.decode("utf-8", errors="replace")


def atomic_write(path: str, data: bytes) -> None:
    with open(path, "wb") as fh:
        fh.write(data)
