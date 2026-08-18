#!/usr/bin/env python3
"""Deterministic grounding for memory-graph structural links (M0-T067, D-013-R047).

Existence alone is NEVER enough: a claimed file/requirement link must be
grounded in authoritative task scope, the provided diff, the digest's own
evidence references, or an explicit owner-approved relationship. Grounding is
default-deny — anything not positively grounded gets a machine-readable
reason and is quarantined by the promotion pipeline, never silently admitted.

Fail closed: an unreadable task packet raises `GroundingError` (the digest
cannot be grounded against a packet that cannot be read).
"""
from __future__ import annotations

import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.memory_digest import is_canonical_repo_path  # noqa: E402
from tools.subsystem_resolver import norm_path  # noqa: E402


class GroundingError(Exception):
    """Fail-closed grounding-context error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _prefix_match(path: str, prefix: str) -> bool:
    """Whole-segment prefix match; a file prefix also matches itself."""
    p, q = norm_path(path).split("/"), norm_path(prefix).split("/")
    return p[:len(q)] == q


def grounding_facts(repo_root: str, task_id: str) -> dict:
    """Authoritative grounding context from the task packet (read-only)."""
    packet_path = (pathlib.Path(repo_root) / "project-control" / "tasks"
                   / f"{task_id}.json")
    try:
        packet = json.loads(packet_path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GroundingError("task_packet_unreadable", f"{packet_path}: {exc}") from exc
    refs = packet.get("directive_refs") or []
    return {
        "task_id": task_id,
        "allowed_paths": [norm_path(p) for p in packet.get("allowed_paths") or []],
        "cited_directives": sorted({str(r["directive_id"]) for r in refs
                                    if isinstance(r, dict)
                                    and isinstance(r.get("directive_id"), str)}),
    }


def ground_file_link(path: str, facts: dict, diff_files: list[str],
                     evidence_refs: list[str],
                     approved_relations: list[str]) -> dict:
    """Default-deny file grounding. Returns {grounded, basis|reason}.

    Evidence matching is EXACT normalized equality, never substring (a digest
    author must name the path, not merely mention it — G3 round-1 B1). A
    non-canonical path ('..'/'.' segments, absolute, drive, backslash) is
    refused here as defense-in-depth even though the closed schema already
    rejects it upstream.
    """
    p = norm_path(path)
    if not is_canonical_repo_path(p):
        return {"grounded": False, "reason": "non_canonical_path"}
    for prefix in facts["allowed_paths"]:
        if _prefix_match(p, prefix):
            return {"grounded": True, "basis": "task_allowed_paths"}
    if p in {norm_path(d) for d in diff_files}:
        return {"grounded": True, "basis": "diff"}
    if any(p == norm_path(ref) for ref in evidence_refs):
        return {"grounded": True, "basis": "evidence_ref"}
    if p in {norm_path(a) for a in approved_relations}:
        return {"grounded": True, "basis": "owner_approved_relation"}
    return {"grounded": False, "reason": "ungrounded_file_link"}


def ground_requirement_link(directive_id: str, facts: dict) -> dict:
    """A requirement link is grounded only when its directive is cited by the
    digest's task packet (authoritative scope), never by mere existence."""
    if directive_id in facts["cited_directives"]:
        return {"grounded": True, "basis": "task_directive_refs"}
    return {"grounded": False, "reason": "ungrounded_requirement_link"}
