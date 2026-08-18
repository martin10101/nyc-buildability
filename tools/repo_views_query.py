#!/usr/bin/env python3
"""Question-oriented retrieval over the bounded views (M0-T068 Unit E).

Typed, deterministic question forms — never semantic guessing (R009):

  about_file PATH       — card + bounded neighborhood + advisory memory digests
  about_task TASK_ID    — packet summary, derived milestone, scoped files,
                          advisory memory digests for the task
  about_requirement RID — directive parent + tasks citing that directive
  who_imports PATH      — bounded downstream importers
  what_changed          — the changed view

Every answer carries the shared R024 coverage record; unresolvable inputs
return machine-readable no-answers; memory-graph reads are ADVISORY and an
absent/empty store is labeled, never fabricated (R051). The CLI `check`
subcommand self-proves determinism by building views twice and byte-comparing
the deterministic sections (content + coverage), excluding only the labeled
non-identity cache-state section.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_views as rv  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402
from tools.subsystem_resolver import norm_path  # noqa: E402

MAX_MEMORY_DIGESTS = 10
MAX_TASKS_LISTED = 10
MAX_FILES_LISTED = 25


def _memory_digests(repo_root: str, *, task_id: str | None = None,
                    path: str | None = None, base: str | None = None) -> dict:
    """ADVISORY read of the Unit D store; absence is labeled, never invented."""
    from tools import memory_graph as mg
    out = {"advisory": True, "status": "ok", "digests": []}
    try:
        cur = mg.memory_store(repo_root, base=base).load_current()
    except Exception as exc:
        return {"advisory": True, "status": "store_unavailable",
                "reason": f"{type(exc).__name__}: {exc}", "digests": []}
    if cur is None:
        return {"advisory": True, "status": "store_empty", "digests": []}
    rows = []
    for did, node in sorted(cur.load_payload()["nodes"].items()):
        digest = node.get("digest") or {}
        if task_id is not None and digest.get("task_id") != task_id:
            continue
        if path is not None:
            hits = {li["value"] for li in node.get("structural_links", [])
                    if li.get("kind") == "path"}
            if norm_path(path) not in hits:
                continue
        rows.append({"digest_id": did, "task_id": digest.get("task_id"),
                     "outcome": digest.get("outcome"), "agent": digest.get("agent")})
    kept, marker = rv._truncate(rows, MAX_MEMORY_DIGESTS)
    out["digests"] = kept
    out["truncation"] = marker
    return out


def _answer(question: dict, content: dict, res, loaded_map, limits: dict) -> dict:
    return {"question": question, "answer": content,
            "coverage": rv.coverage_record(res, loaded_map, question, limits),
            "runtime": rv.cache_state(res)}


def about_file(repo_root: str, path: str, *, cache_base: str | None = None,
               memory_base: str | None = None,
               map_path: str | None = None) -> dict:
    res, gi, loaded_map = rv.build_index(repo_root, cache_base, map_path)
    card = rv.card_view(res, gi, loaded_map, repo_root, path)
    return _answer(
        {"kind": "about_file", "value": norm_path(path)},
        {"card": card["content"],
         "memory": _memory_digests(repo_root, path=path, base=memory_base)},
        res, loaded_map, {"edge_limit": 10, "memory_limit": MAX_MEMORY_DIGESTS})


_RX_TASK_ID = re.compile(r"^M\d+-T\d+$")


def about_task(repo_root: str, task_id: str, *, cache_base: str | None = None,
               memory_base: str | None = None,
               map_path: str | None = None) -> dict:
    # The id is a path component: anything but the exact ledger pattern
    # refuses BEFORE any filesystem access (G3 round-1 finding 2 — a
    # traversal id must never read outside the repository).
    if not _RX_TASK_ID.match(task_id or ""):
        raise rv.ViewsError("invalid_task_id",
                            f"{task_id!r} is not a ledger task id (M<n>-T<n>)")
    res, _gi, loaded_map = rv.build_index(repo_root, cache_base, map_path)
    packet_path = (pathlib.Path(repo_root) / "project-control" / "tasks"
                   / f"{task_id}.json")
    try:
        packet = json.loads(packet_path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        # detail stays repo-relative: no absolute paths in error documents
        raise rv.ViewsError(
            "task_packet_unreadable",
            f"project-control/tasks/{task_id}.json: {type(exc).__name__}") from exc
    files, files_marker = rv._truncate(
        sorted(packet.get("allowed_paths") or []), MAX_FILES_LISTED)
    content = {
        "task_id": task_id, "title": packet.get("title"),
        "status": packet.get("status"), "milestone_id": packet.get("milestone_id"),
        "dependencies": packet.get("dependencies"),
        "allowed_paths": files, "allowed_paths_truncation": files_marker,
        "memory": _memory_digests(repo_root, task_id=task_id, base=memory_base),
    }
    return _answer({"kind": "about_task", "value": task_id}, content,
                   res, loaded_map,
                   {"file_limit": MAX_FILES_LISTED,
                    "memory_limit": MAX_MEMORY_DIGESTS})


def about_requirement(repo_root: str, requirement_id: str,
                      *, cache_base: str | None = None,
                      map_path: str | None = None) -> dict:
    from tools.subsystem_entities import AuthoritativeIndexes
    res, _gi, loaded_map = rv.build_index(repo_root, cache_base, map_path)
    idx = AuthoritativeIndexes.load(repo_root)
    if requirement_id not in idx.requirements:
        content = {"requirement_id": requirement_id, "resolved": False,
                   "reason": "unknown_requirement_id"}
        return _answer({"kind": "about_requirement", "value": requirement_id},
                       content, res, loaded_map, {})
    directive = idx.requirements[requirement_id]
    citing = []
    tasks_dir = pathlib.Path(repo_root) / "project-control" / "tasks"
    for f in sorted(tasks_dir.glob("*.json")):
        try:
            doc = json.loads(f.read_bytes().decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue  # census of citers is advisory; packet integrity is CI's job
        refs = {r.get("directive_id") for r in doc.get("directive_refs") or []
                if isinstance(r, dict)}
        if directive in refs:
            citing.append(doc.get("task_id"))
    kept, marker = rv._truncate(citing, MAX_TASKS_LISTED)
    content = {"requirement_id": requirement_id, "resolved": True,
               "directive_id": directive, "citing_tasks": kept,
               "citing_tasks_truncation": marker}
    return _answer({"kind": "about_requirement", "value": requirement_id},
                   content, res, loaded_map, {"task_limit": MAX_TASKS_LISTED})


def who_imports(repo_root: str, path: str, *, cache_base: str | None = None,
                edge_limit: int = 25, map_path: str | None = None) -> dict:
    res, gi, loaded_map = rv.build_index(repo_root, cache_base, map_path)
    view = rv.neighborhood_view(res, gi, loaded_map, path, edge_limit=edge_limit)
    c = view["content"]
    content = ({"path": path, "resolved": False, "reason": c["reason"]}
               if not c.get("resolved") else
               {"path": path, "resolved": True,
                "importers": c["in_edges"], "truncation": c["in_truncation"]})
    return _answer({"kind": "who_imports", "value": norm_path(path)}, content,
                   res, loaded_map, {"edge_limit": edge_limit})


def what_changed(repo_root: str, *, cache_base: str | None = None,
                 since_fingerprint: str | None = None,
                 map_path: str | None = None) -> dict:
    res, _gi, loaded_map = rv.build_index(repo_root, cache_base, map_path)
    view = rv.changed_view(res, loaded_map, since_fingerprint=since_fingerprint)
    return _answer({"kind": "what_changed", "since": since_fingerprint},
                   view["content"], res, loaded_map, {})


def _det_sections(doc: dict) -> bytes:
    """The byte-identity part of any view/answer: everything but runtime."""
    return canon_json_bytes({k: v for k, v in doc.items() if k != "runtime"})


def _emit(doc: dict) -> None:
    sys.stdout.write(canon_json_bytes(doc).decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Bounded repository-intelligence views (D-013 Unit E). "
                    "Advisory navigation; source files remain authoritative.")
    ap.add_argument("--repo", default=str(_ROOT))
    ap.add_argument("--cache-base", default=None, help="index cache base (tests)")
    ap.add_argument("--map", default=None, help="override map path (tests only)")
    ap.add_argument("--limit", type=int, default=25)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("census")
    p_ch = sub.add_parser("changed")
    p_ch.add_argument("--since", default=None)
    for name in ("card", "neighborhood"):
        p = sub.add_parser(name)
        p.add_argument("seed")
    p_deep = sub.add_parser("deep")
    p_deep.add_argument("path")
    p_deep.add_argument("start", type=int)
    p_deep.add_argument("end", type=int)
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("kind", choices=["about_file", "about_task",
                                        "about_requirement", "who_imports",
                                        "what_changed"])
    p_ask.add_argument("value", nargs="?", default=None)
    sub.add_parser("check", help="two-run byte-identity proof of the "
                                 "deterministic sections")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "check":
            # The changed view is deliberately EXCLUDED: its content is
            # base-relative (prior cache generation), disclosed by its `base`
            # label — cache-relative by design, not a determinism defect.
            runs = []
            for _ in range(2):
                res, gi, loaded_map = rv.build_index(args.repo, args.cache_base,
                                                     args.map)
                sample = gi.file_ids()[:1]
                docs = [rv.census_view(res, gi, loaded_map)]
                if sample:
                    docs.append(rv.card_view(res, gi, loaded_map, args.repo,
                                             sample[0]))
                    docs.append(rv.neighborhood_view(res, gi, loaded_map,
                                                     sample[0]))
                runs.append(b"".join(_det_sections(d) for d in docs))
            if runs[0] != runs[1]:
                _emit({"error": {"code": "nondeterministic_views",
                                 "detail": "two runs produced different "
                                           "deterministic sections"}})
                return 2
            _emit({"check": "PASS", "bytes": len(runs[0])})
            return 0

        res, gi, loaded_map = rv.build_index(args.repo, args.cache_base,
                                             args.map)
        if args.cmd == "census":
            _emit(rv.census_view(res, gi, loaded_map, file_limit=args.limit))
        elif args.cmd == "changed":
            _emit(rv.changed_view(res, loaded_map, since_fingerprint=args.since))
        elif args.cmd == "card":
            _emit(rv.card_view(res, gi, loaded_map, args.repo, args.seed,
                               edge_limit=args.limit))
        elif args.cmd == "neighborhood":
            _emit(rv.neighborhood_view(res, gi, loaded_map, args.seed,
                                       edge_limit=args.limit))
        elif args.cmd == "deep":
            _emit(rv.deep_view(res, loaded_map, args.repo, args.path,
                               args.start, args.end))
        elif args.cmd == "ask":
            fns = {"about_file": lambda: about_file(args.repo, args.value,
                                                    cache_base=args.cache_base, map_path=args.map),
                   "about_task": lambda: about_task(args.repo, args.value,
                                                    cache_base=args.cache_base, map_path=args.map),
                   "about_requirement": lambda: about_requirement(
                       args.repo, args.value, cache_base=args.cache_base, map_path=args.map),
                   "who_imports": lambda: who_imports(args.repo, args.value,
                                                      cache_base=args.cache_base, map_path=args.map),
                   "what_changed": lambda: what_changed(
                       args.repo, cache_base=args.cache_base, map_path=args.map)}
            if args.kind != "what_changed" and not args.value:
                _emit({"error": {"code": "missing_question_value",
                                 "detail": f"{args.kind} needs a value"}})
                return 2
            _emit(fns[args.kind]())
        return 0
    except rv.ViewsError as exc:
        _emit(exc.doc())
        return 2
    except Exception as exc:  # fail closed, machine-readable, no traceback leak
        _emit({"error": {"code": "view_failed",
                         "detail": f"{type(exc).__name__}: {exc}"}})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
