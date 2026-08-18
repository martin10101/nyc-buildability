#!/usr/bin/env python3
"""Deterministic entity existence validation + two-pass resolve (M0-T066 Unit C).

Implements the D-013-R046 two-pass shape for structural links:

  pass 1 — `propose()` (extraction proposes): normalize bounded candidate facts
  into typed proposals with evidence references. Deterministic here; a later
  authorized LLM extractor may only ever PROPOSE — it can never mint a link.

  pass 2 — `resolve_proposals()` (resolver validates/derives): every structural
  link is derived from authoritative repository facts — task→milestone via the
  task packet + master plan, requirement→directive via the directives registry,
  path→subsystem via the versioned map (tools/subsystem_resolver.py), files →
  existing code-graph nodes when indexed. Anything that cannot be validated
  lands in `unresolved_links[]` with a machine-readable reason; nothing is
  guessed, invented, or silently dropped (R009/R045).

Fail closed (R013-style): a missing or malformed authoritative index (master
plan, directives registry, a listed directive's requirements.json) raises
`EntityIndexError` — never a partial answer presented as complete.

Index digests: `AuthoritativeIndexes` exposes sha256 digests of the loaded
task and directive indexes so Unit D memory digests can bind them (R044).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_paths as cpaths  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402
from tools.subsystem_resolver import norm_path, resolve_path, version_stamp  # noqa: E402

_RX_MILESTONE = re.compile(r"^M\d+$")
_RX_TASK = re.compile(r"^M\d+-T\d+$")
_RX_DIRECTIVE = re.compile(r"^D-\d{3}$")
_RX_REQUIREMENT = re.compile(r"^D-\d{3}-R\d+$")


class EntityIndexError(Exception):
    """Fail-closed authoritative-index error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def _read_json(path: pathlib.Path, code: str) -> dict:
    try:
        return json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EntityIndexError(code, f"{path}: {exc}") from exc


class AuthoritativeIndexes:
    """Read-only deterministic view of the project-control entity indexes."""

    def __init__(self, milestones: set[str], tasks: dict[str, str],
                 directives: set[str], requirements: dict[str, str]):
        self.milestones = milestones
        self.tasks = tasks              # task_id -> milestone_id (from the packet)
        self.directives = directives
        self.requirements = requirements  # requirement_id -> directive_id

    @classmethod
    def load(cls, repo_root: str) -> "AuthoritativeIndexes":
        root = pathlib.Path(repo_root).resolve()
        plan = _read_json(root / "project-control" / "master_plan.json",
                          "master_plan_unreadable")
        try:
            milestones = {m["id"] for m in plan["milestones"]}
        except (KeyError, TypeError) as exc:
            raise EntityIndexError("master_plan_malformed", str(exc)) from exc

        tasks: dict[str, str] = {}
        tasks_dir = root / "project-control" / "tasks"
        if not tasks_dir.is_dir():
            raise EntityIndexError("task_index_unreadable", f"{tasks_dir} missing")
        for f in sorted(tasks_dir.glob("*.json")):
            doc = _read_json(f, "task_packet_unreadable")
            tid = doc.get("task_id")
            if isinstance(tid, str) and tid:
                tasks[tid] = str(doc.get("milestone_id") or "")

        reg_dir = root / "project-control" / "directives"
        index = _read_json(reg_dir / "index.json", "directive_index_unreadable")
        try:
            directive_ids = {d["directive_id"] for d in index["directives"]}
        except (KeyError, TypeError) as exc:
            raise EntityIndexError("directive_index_malformed", str(exc)) from exc

        requirements: dict[str, str] = {}
        for child in sorted(p for p in reg_dir.iterdir() if p.is_dir()):
            did = "-".join(child.name.split("-")[:2])  # D-013-... -> D-013
            if did not in directive_ids:
                continue
            reqs = _read_json(child / "requirements.json", "requirements_unreadable")
            for r in reqs.get("requirements", []):
                rid = r.get("id")
                if isinstance(rid, str) and rid:
                    requirements[rid] = did
        return cls(milestones, tasks, directive_ids, requirements)

    def digests(self) -> dict:
        """sha256 digests Unit D memory digests can bind (D-013-R044)."""
        return {
            "task_index_digest": hashlib.sha256(
                canon_json_bytes(self.tasks)).hexdigest(),
            "directive_index_digest": hashlib.sha256(canon_json_bytes({
                "directives": sorted(self.directives),
                "requirements": self.requirements})).hexdigest(),
        }


def classify(value: str) -> str:
    """Deterministic kind classification for untyped candidates."""
    if _RX_MILESTONE.match(value):
        return "milestone"
    if _RX_TASK.match(value):
        return "task"
    if _RX_DIRECTIVE.match(value):
        return "directive"
    if _RX_REQUIREMENT.match(value):
        return "requirement"
    return "path"


def propose(candidates: list) -> list[dict]:
    """Pass 1 (extraction proposes): normalize + dedupe candidate facts.

    Accepts strings (kind classified deterministically) or dicts with
    {"kind","value","evidence"}. Output is deterministically ordered.
    """
    out: dict[tuple[str, str], dict] = {}
    for c in candidates:
        if isinstance(c, str):
            value, kind, evidence = c, classify(c), None
        elif isinstance(c, dict) and isinstance(c.get("value"), str):
            value = c["value"]
            kind = c.get("kind") or classify(value)
            evidence = c.get("evidence")
        else:
            continue  # non-fact input shapes are not proposals
        value = norm_path(value) if kind == "path" else value.strip()
        if not value:
            continue
        key = (kind, value)
        if key not in out:
            out[key] = {"kind": kind, "value": value, "evidence": evidence}
    return [out[k] for k in sorted(out)]


def _resolve_one(p: dict, idx: AuthoritativeIndexes, root: pathlib.Path,
                 loaded_map: dict, graph_index) -> tuple[dict | None, dict | None]:
    """Returns (link, None) when validated or (None, unresolved-entry)."""
    kind, value = p["kind"], p["value"]

    def bad(reason: str) -> tuple[None, dict]:
        return None, {"kind": kind, "value": value, "reason": reason,
                      "evidence": p.get("evidence")}

    if kind == "milestone":
        if value not in idx.milestones:
            return bad("unknown_milestone_id")
        return {"kind": kind, "value": value, "parents": {}}, None
    if kind == "task":
        if value not in idx.tasks:
            return bad("unknown_task_id")
        mid = idx.tasks[value]
        if mid not in idx.milestones:
            return bad("milestone_not_in_master_plan")
        return {"kind": kind, "value": value, "parents": {"milestone": mid}}, None
    if kind == "directive":
        if value not in idx.directives:
            return bad("unknown_directive_id")
        return {"kind": kind, "value": value, "parents": {}}, None
    if kind == "requirement":
        if value not in idx.requirements:
            return bad("unknown_requirement_id")
        return {"kind": kind, "value": value,
                "parents": {"directive": idx.requirements[value]}}, None
    if kind == "path":
        # Ontology resolution inputs read through THE shared containment rule
        # (D-018-R031/R033): non-canonical or checkout-escaping paths refuse
        # with the containment code, never a filesystem probe.
        try:
            exists = cpaths.contained_repo_path(str(root), value).exists()
        except cpaths.PathContainmentError as exc:
            return bad(exc.code)
        if not exists:
            return bad("path_not_in_source_tree")
        r = resolve_path(value, loaded_map)
        if not r["resolved"]:
            return bad(r["reason"] or "no_matching_subsystem_rule")
        node_id = None
        indexed = None
        if graph_index is not None:
            indexed = value in graph_index.nodes
            node_id = value if indexed else None
        return {"kind": kind, "value": value,
                "parents": {"subsystem": r["subsystem"]},
                "graph_node": node_id, "graph_indexed": indexed}, None
    if kind == "symbol":
        if graph_index is None:
            return bad("graph_not_provided")
        if value not in graph_index.nodes:
            return bad("symbol_not_in_graph")
        return {"kind": kind, "value": value,
                "parents": {"graph_node": value}}, None
    return bad("unsupported_kind")


def resolve_proposals(proposals: list[dict], repo_root: str, loaded_map: dict,
                      graph_index=None,
                      indexes: AuthoritativeIndexes | None = None) -> dict:
    """Pass 2 (resolver validates/derives). Deterministic, fail-closed loads."""
    root = pathlib.Path(repo_root).resolve()
    idx = indexes or AuthoritativeIndexes.load(repo_root)
    links: list[dict] = []
    unresolved: list[dict] = []
    for p in proposals:
        link, bad = _resolve_one(p, idx, root, loaded_map, graph_index)
        if link is not None:
            if p.get("evidence") is not None:
                link["evidence"] = p["evidence"]
            links.append(link)
        elif bad is not None:
            unresolved.append(bad)
    return {
        "version": version_stamp(loaded_map),
        "index_digests": idx.digests(),
        "links": links,
        "unresolved_links": unresolved,
    }
