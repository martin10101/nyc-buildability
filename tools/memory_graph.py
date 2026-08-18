#!/usr/bin/env python3
"""Session/task memory graph promotion (M0-T067 Unit D, D-013-R044..R048).

Two-pass promotion pipeline, all deterministic code (R009):

  validate  — the CLOSED digest schema refuses anything malformed (R044/R013).
  staleness — the digest's ontology stamp must match the CURRENT versioned
              resolver/map; a stale ontology quarantines the digest whole.
  pass 1    — the digest's claims become typed proposals (Unit C `propose`).
  pass 2    — Unit C `resolve_proposals` validates existence and derives every
              parent from authoritative indexes (R045/R046).
  grounding — existence alone is never enough: file/requirement links must be
              grounded in task scope/diff/evidence/owner-approved relation
              (R047); ungrounded or unresolved links are QUARANTINED with
              machine-readable reasons and never enter structural_links.
  promote   — the node is written into an external per-checkout generation
              store REUSING the accepted A2 `IndexCache` (single-writer lock,
              temp + validate + atomic os.replace, recovery, quarantine), so
              promotion is atomic, idempotent by digest content, replay-safe,
              and concurrency-safe (R048). The store never lives in the repo
              (R050/R011). Invalid advisory tags are discarded into a separate
              record; they never quarantine an otherwise valid digest (R048).

Nothing here embeds wall-clock time; the same digest against the same
repository state promotes to byte-identical generation payloads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import memory_grounding as grounding  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools import subsystem_entities as ents  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402
from tools.memory_digest import (  # noqa: E402
    DigestSchemaError, judge_advisory_tag, validate_digest)
from tools.subsystem_resolver import (  # noqa: E402
    SubsystemMapError, load_map, norm_path, version_stamp)

MEMORY_GRAPH_VERSION = "1.0.0"

#: Store namespace, separate from the index cache generations.
MEMORY_BASE_SUBDIR = "memory-graph"


class MemoryGraphError(Exception):
    """Fail-closed promotion error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def memory_store(repo_root: str, base: str | None = None) -> ric.IndexCache:
    """The external generation store for this checkout's memory graph.
    Reuses the accepted A2 IndexCache; refuses in-repo locations."""
    b = pathlib.Path(base) if base else ric.cache_base_dir() / MEMORY_BASE_SUBDIR
    return ric.IndexCache(repo_root, base=b)


def _file_digest(path: pathlib.Path) -> str:
    """CRLF-normalized sha256 (A1 convention) of a working-tree file."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _proposals_from_digest(doc: dict) -> list[dict]:
    cands: list[dict] = [{"kind": "task", "value": doc["task_id"]}]
    cands += [{"kind": "requirement", "value": rid} for rid in doc["requirement_ids"]]
    cands += [{"kind": "path", "value": f["path"]} for f in doc["files"]]
    return ents.propose(cands)


def _quarantine_digest(store: ric.IndexCache, doc: dict, reasons: list[dict]) -> dict:
    """Digest-level quarantine record (external, atomic tmp+replace)."""
    qdir = store.root / "digest-quarantine"
    qdir.mkdir(parents=True, exist_ok=True)
    record = {"digest_id": doc.get("digest_id"), "task_id": doc.get("task_id"),
              "reasons": reasons, "memory_graph_version": MEMORY_GRAPH_VERSION}
    tmp = qdir / f"{doc.get('digest_id', 'unknown')}.json.tmp"
    tmp.write_bytes(canon_json_bytes(record))
    tmp.replace(qdir / f"{doc.get('digest_id', 'unknown')}.json")
    return {"status": "quarantined", "digest_id": doc.get("digest_id"),
            "reasons": reasons}


def _ground_links(doc: dict, resolved: dict, repo_root: str,
                  diff_files: list[str], approved_relations: list[str]) -> tuple[list, list]:
    facts = grounding.grounding_facts(repo_root, doc["task_id"])
    file_digests = {norm_path(f["path"]): f.get("content_digest")
                    for f in doc["files"]}
    valid: list[dict] = []
    quarantined: list[dict] = [
        {"kind": u["kind"], "value": u["value"], "reason": u["reason"]}
        for u in resolved["unresolved_links"]]
    for link in resolved["links"]:
        kind, value = link["kind"], link["value"]
        if kind == "task":
            valid.append(link)  # the digest's own packet: grounded by identity
            continue
        if kind == "requirement":
            g = grounding.ground_requirement_link(link["parents"]["directive"], facts)
        elif kind == "path":
            claimed = file_digests.get(value)
            if claimed is not None:
                try:
                    current = _file_digest(pathlib.Path(repo_root) / value)
                except OSError:
                    quarantined.append({"kind": kind, "value": value,
                                        "reason": "file_digest_unreadable"})
                    continue
                if current != claimed:
                    quarantined.append({"kind": kind, "value": value,
                                        "reason": "stale_file_link"})
                    continue
            g = grounding.ground_file_link(value, facts, diff_files,
                                           doc["evidence_refs"], approved_relations)
        else:
            g = {"grounded": False, "reason": "ungrounded_link_kind"}
        if g["grounded"]:
            valid.append({**link, "grounding_basis": g["basis"]})
        else:
            quarantined.append({"kind": kind, "value": value, "reason": g["reason"]})
    return valid, quarantined


def promote_digest(doc: dict, repo_root: str, *, diff_files: list[str] | None = None,
                   approved_relations: list[str] | None = None,
                   base: str | None = None, map_path: str | None = None,
                   graph_index=None, indexes=None) -> dict:
    """Validate → resolve → ground → quarantine-or-promote. Deterministic."""
    diff_files = diff_files or []
    approved_relations = approved_relations or []
    validate_digest(doc, repo_root)
    store = memory_store(repo_root, base=base)

    loaded_map = load_map(repo_root, map_path)
    stamp = version_stamp(loaded_map)
    if (doc["resolver_version"], doc["map_version"], doc["map_digest"]) != (
            stamp["resolver_version"], stamp["map_version"], stamp["map_digest"]):
        return _quarantine_digest(store, doc, [
            {"kind": "digest", "value": doc["digest_id"],
             "reason": "stale_ontology_version"}])

    resolved = ents.resolve_proposals(
        _proposals_from_digest(doc), repo_root, loaded_map,
        graph_index=graph_index, indexes=indexes)
    # The task parent is the digest's anchor: if pass 2 could not resolve it,
    # the WHOLE digest is quarantined before grounding (its packet is the
    # grounding authority, so nothing else can be grounded either).
    if not any(link["kind"] == "task" for link in resolved["links"]):
        return _quarantine_digest(store, doc, [
            {"kind": "task", "value": doc["task_id"],
             "reason": "digest_task_unresolved"}])
    valid, quarantined = _ground_links(doc, resolved, repo_root,
                                       diff_files, approved_relations)

    advisory_valid: list[str] = []
    advisory_discarded: list[dict] = []
    for tag in doc["advisory_tags"]:
        why = judge_advisory_tag(tag)
        if why is None:
            advisory_valid.append(tag)
        else:  # discarded separately; NEVER quarantines the digest (R048)
            advisory_discarded.append({"tag": repr(tag)[:80], "reason": why})

    node = {
        "digest": {k: v for k, v in doc.items() if k != "advisory_tags"},
        "structural_links": sorted(valid, key=lambda x: (x["kind"], x["value"])),
        "quarantined_links": sorted(quarantined, key=lambda x: (x["kind"], x["value"])),
        "advisory_tags": sorted(advisory_valid),
        "discarded_advisory_tags": sorted(advisory_discarded,
                                          key=lambda x: (x["tag"], x["reason"])),
        "ontology": stamp,
        "index_digests": resolved["index_digests"],
        "memory_graph_version": MEMORY_GRAPH_VERSION,
    }

    current = store.load_current()
    payload = (current.load_payload() if current
               else {"memory_graph_version": MEMORY_GRAPH_VERSION, "nodes": {}})
    existing = payload["nodes"].get(doc["digest_id"])
    if existing is not None:
        assert current is not None  # a node can only come from a loaded generation
        if existing == node:
            return {"status": "already_promoted", "digest_id": doc["digest_id"],
                    "generation_fingerprint": current.fingerprint,
                    "nodes": len(payload["nodes"])}
        raise MemoryGraphError(
            "digest_id_conflict",
            f"digest {doc['digest_id'][:16]}... already promoted with different content")
    payload["nodes"][doc["digest_id"]] = node
    fingerprint = hashlib.sha256(canon_json_bytes(payload)).hexdigest()
    gen = store.write_generation(fingerprint, payload)
    return {"status": "promoted", "digest_id": doc["digest_id"],
            "generation_fingerprint": gen.fingerprint,
            "quarantined_links": len(node["quarantined_links"]),
            "discarded_advisory_tags": len(node["discarded_advisory_tags"]),
            "nodes": len(payload["nodes"])}


def _emit(doc: dict) -> None:
    sys.stdout.write(canon_json_bytes(doc).decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Memory-graph promotion (D-013 Unit D). Deterministic, "
                    "fail-closed; the store lives OUTSIDE the repository.")
    ap.add_argument("--repo", default=str(_ROOT))
    ap.add_argument("--base", default=None, help="override store base (tests only)")
    ap.add_argument("--map", default=None, help="override map path (tests only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_pro = sub.add_parser("promote", help="validate + promote one digest JSON file")
    p_pro.add_argument("digest_file")
    p_pro.add_argument("--diff-file", action="append", default=[],
                       help="a changed file grounding file links (repeatable)")
    sub.add_parser("show", help="print the current graph generation summary")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "promote":
            doc = json.loads(pathlib.Path(args.digest_file).read_bytes().decode("utf-8"))
            out = promote_digest(doc, args.repo, diff_files=args.diff_file,
                                 base=args.base, map_path=args.map)
            _emit(out)
            return 0 if out["status"] in ("promoted", "already_promoted") else 2
        if args.cmd == "show":
            store = memory_store(args.repo, base=args.base)
            cur = store.load_current()
            if cur is None:
                _emit({"nodes": 0, "generation_fingerprint": None})
                return 0
            payload = cur.load_payload()
            _emit({"nodes": len(payload["nodes"]),
                   "digest_ids": sorted(payload["nodes"]),
                   "generation_fingerprint": cur.fingerprint,
                   "memory_graph_version": payload["memory_graph_version"]})
            return 0
    except (DigestSchemaError, MemoryGraphError, SubsystemMapError) as exc:
        _emit(exc.doc())
        return 2
    except ric.CacheError as exc:
        _emit({"error": {"code": exc.code, "detail": exc.message}})
        return 2
    except (ents.EntityIndexError, grounding.GroundingError) as exc:
        _emit({"error": {"code": exc.code, "detail": exc.detail}})
        return 2
    except (OSError, ValueError) as exc:  # unreadable digest file etc.
        _emit({"error": {"code": "input_unreadable",
                         "detail": f"{type(exc).__name__}: {exc}"}})
        return 2
    return 2  # pragma: no cover — argparse enforces the subcommand set


if __name__ == "__main__":
    raise SystemExit(main())
