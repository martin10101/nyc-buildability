#!/usr/bin/env python3
"""Vertical-integration evidence for the ONE context compiler (M0-T075).

Everything here is deterministic code feeding `context_pack_sources` under the
single shared budget (D-018-R010..R018):

* **Exact requirements** — the task's `directive_refs` (including "ALL") are
  resolved deterministically through the accepted directive registry; the
  packet carries the exact applicable requirement IDs AND their exact texts.
* **Real path seeding** — graph/source seeds come from changed files and the
  task's canonical implementation paths. Prose fields (outputs/inputs) are
  never used as literal paths; they pass through `extract_prose_paths`, a
  strict deterministic extractor whose every candidate is recorded as
  resolved or unresolved.
* **Reopened sources** — authoritative source excerpts and their tests are
  selected deterministically from task scope + changes + graph evidence and
  read ONLY through the shared containment rule (`tools/context_paths`).
* **Advisory memory** — bounded Unit D digests for the task, explicitly
  advisory; absence/quarantine stated honestly (never fabricated).
* **Ontology** — Unit C subsystem placement for the implementation paths,
  with the versioned resolver stamp.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_paths as cpaths  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402

#: Bounded selection constants (deterministic; recorded in provenance).
MAX_EXCERPT_FILES = 5
MAX_TEST_FILES = 3
WHOLE_FILE_BYTES = 40_000
EXCERPT_HEAD_LINES = 300
TEST_HEAD_LINES = 200
MAX_MEMORY_DIGESTS = 10

_RX_PATH_TOKEN = re.compile(r"[A-Za-z0-9_@][A-Za-z0-9_@.\-/]*/[A-Za-z0-9_@.\-/]*")

#: Task-scope prefixes that are CONTROL-PLANE/prose, not implementation code.
_NON_IMPL_PREFIXES = ("project-control/", "docs/")


# ==========================================================================
# Exact requirement IDs + texts (D-018-R011)
# ==========================================================================


def resolve_requirements(repo: str, task_obj: dict) -> dict:
    """Deterministically resolve the task's directive_refs (incl. "ALL") to
    the exact applicable requirement IDs and texts.

    Returns {"in_regime", "applicable": [{id,text}], "provenance", "error"}.
    A resolution failure for an in-regime task is an ERROR (the compiler's
    sufficiency layer fails closed on it); a task without directive_refs is
    honestly out-of-regime, never guessed.
    """
    refs = task_obj.get("directive_refs") or []
    if not refs:
        return {"in_regime": False, "applicable": [],
                "provenance": {"reason": "task carries no directive_refs "
                                         "(not in the directive regime)"},
                "error": None}
    directives_dir = pathlib.Path(repo) / "project-control" / "directives"
    try:
        from tools import directive_registry as dr
        reg = dr.load_registry(directives_dir)
        ev = reg.evaluate_task_refs(task_obj)
    except Exception as exc:
        return {"in_regime": True, "applicable": [], "provenance": {},
                "error": f"directive registry unavailable ({type(exc).__name__})"}
    if not ev.get("ok"):
        return {"in_regime": True, "applicable": [],
                "provenance": {"reasons": ev.get("reasons")},
                "error": "directive_refs did not resolve cleanly"}
    applicable = list(ev.get("applicable_ids") or [])
    texts: dict[str, str] = {}
    by_directive: dict[str, list[str]] = {}
    for rid in applicable:
        did = "-".join(rid.split("-")[:2])
        by_directive.setdefault(did, []).append(rid)
    for did, rids in sorted(by_directive.items()):
        req_file = None
        for child in sorted(p for p in directives_dir.iterdir() if p.is_dir()):
            if child.name.startswith(did + "-") or child.name == did:
                req_file = child / "requirements.json"
                break
        if req_file is None or not req_file.is_file():
            return {"in_regime": True, "applicable": [],
                    "provenance": {"directive": did},
                    "error": f"requirements.json for {did} not found"}
        try:
            rows = json.loads(req_file.read_bytes().decode("utf-8"))["requirements"]
        except Exception as exc:
            return {"in_regime": True, "applicable": [],
                    "provenance": {"directive": did},
                    "error": f"requirements.json for {did} unreadable "
                             f"({type(exc).__name__})"}
        for row in rows:
            if row.get("id") in rids:
                texts[row["id"]] = row.get("text", "")
    missing = [rid for rid in applicable if rid not in texts]
    if missing:
        return {"in_regime": True, "applicable": [],
                "provenance": {"missing_text_ids": missing[:10]},
                "error": f"{len(missing)} applicable requirement id(s) have no "
                         "resolvable text"}
    return {
        "in_regime": True,
        "applicable": [{"id": rid, "text": texts[rid]} for rid in applicable],
        "provenance": {"cited": sorted({str(r["directive_id"]) for r in refs
                                        if isinstance(r, dict)
                                        and isinstance(r.get("directive_id"), str)}),
                       "applicable_count": len(applicable),
                       "resolution": "directive_registry.evaluate_task_refs "
                                     "(deterministic, ALL expanded)"},
        "error": None,
    }


# ==========================================================================
# Real path seeding + strict prose extraction (D-018-R012..R014)
# ==========================================================================


def implementation_paths(task_obj: dict) -> list[str]:
    """Canonical implementation paths from task scope: allowed_paths entries
    that are canonical repo paths OUTSIDE the control-plane/docs prefixes."""
    out = []
    for p in task_obj.get("allowed_paths") or []:
        if (isinstance(p, str) and cpaths.is_canonical_repo_path(p)
                and not p.startswith(_NON_IMPL_PREFIXES)):
            out.append(p)
    return sorted(set(out))


def extract_prose_paths(repo: str, task_obj: dict,
                        fields: tuple[str, ...] = ("outputs", "inputs")) -> dict:
    """STRICT deterministic path extractor for prose fields (D-018-R013).

    A prose sentence is NEVER a seed. Candidate tokens must look like paths
    (contain '/'), pass the canonical rule, and EXIST in the tree; everything
    else is recorded as unresolved. Returns {"resolved": [...], "records":
    [{field, token, resolved}]} — every candidate is accounted for (R014)."""
    resolved: list[str] = []
    records: list[dict] = []
    seen: set[tuple] = set()
    for field in fields:
        for entry in task_obj.get(field) or []:
            if not isinstance(entry, str):
                continue
            for token in _RX_PATH_TOKEN.findall(entry):
                token = token.rstrip(".,;:)")
                key = (field, token)
                if key in seen:
                    continue
                seen.add(key)
                ok = (cpaths.is_canonical_repo_path(token)
                      and cpaths.contained_exists(repo, token))
                records.append({"field": field, "token": token, "resolved": ok})
                if ok:
                    resolved.append(token)
    return {"resolved": sorted(set(resolved)), "records": records}


# ==========================================================================
# Reopened source excerpts + tests (D-018-R017)
# ==========================================================================


def _bounded_text(repo: str, rel: str, head_lines: int) -> tuple[str, dict]:
    """Contained read with a deterministic bounded selection record."""
    data = cpaths.contained_read_bytes(repo, rel)
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if len(data) <= WHOLE_FILE_BYTES:
        return text, {"path": rel, "selection": "whole_file",
                      "bytes": len(data), "lines": len(lines)}
    kept = lines[:head_lines]
    body = "\n".join(kept) + (
        f"\n\n[bounded selection: first {head_lines} of {len(lines)} lines; "
        f"the full file remains authoritative at {rel}]")
    return body, {"path": rel, "selection": f"head_{head_lines}_lines",
                  "bytes": len(data), "lines": len(lines),
                  "included_lines": len(kept)}


def select_source_excerpts(repo: str, impl_paths: list[str], changed: list[str],
                           gi) -> tuple[list[dict], list[dict], dict]:
    """Deterministic reopened-source selection from scope + changes + graph.

    Returns (excerpts, tests, selection_provenance): excerpts are the
    implementation paths themselves (changed ones first), tests come from the
    graph's is_test importers plus the tools/test_<stem>.py convention."""
    changed_set = set(changed)
    ordered = ([p for p in impl_paths if p in changed_set]
               + [p for p in impl_paths if p not in changed_set])
    picked, skipped = [], []
    for rel in ordered:
        if len(picked) >= MAX_EXCERPT_FILES:
            skipped.append(rel)
            continue
        try:
            if not cpaths.contained_repo_path(repo, rel).is_file():
                skipped.append(rel)
                continue
        except cpaths.PathContainmentError:
            skipped.append(rel)
            continue
        picked.append(rel)
    excerpts, records = [], []
    for rel in picked:
        try:
            body, rec = _bounded_text(repo, rel, EXCERPT_HEAD_LINES)
        except cpaths.PathContainmentError as exc:
            records.append({"path": rel, "selection": "refused",
                            "reason": exc.code})
            continue
        excerpts.append({"path": rel, "content": body})
        records.append(rec)

    test_candidates: list[str] = []
    for rel in picked:
        stem = rel.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        conventional = f"tools/test_{stem}.py"
        if cpaths.contained_exists(repo, conventional):
            test_candidates.append(conventional)
        if gi is not None:
            for edge in gi.in_edges.get(rel, []):
                src = edge.get("from", "")
                node = gi.nodes.get(src) or {}
                if node.get("is_test"):
                    test_candidates.append(src)
    tests, test_records = [], []
    for rel in sorted(set(test_candidates))[:MAX_TEST_FILES]:
        try:
            body, rec = _bounded_text(repo, rel, TEST_HEAD_LINES)
        except cpaths.PathContainmentError as exc:
            test_records.append({"path": rel, "selection": "refused",
                                 "reason": exc.code})
            continue
        tests.append({"path": rel, "content": body})
        test_records.append(rec)
    provenance = {
        "method": ("implementation paths from task scope (changed first), "
                   "capped deterministic; tests from graph is_test importers "
                   "+ tools/test_<stem>.py convention"),
        "caps": {"excerpt_files": MAX_EXCERPT_FILES, "test_files": MAX_TEST_FILES,
                 "whole_file_bytes": WHOLE_FILE_BYTES,
                 "excerpt_head_lines": EXCERPT_HEAD_LINES},
        "excerpt_records": records,
        "test_records": test_records,
        "skipped_over_cap_or_missing": skipped,
    }
    return excerpts, tests, provenance


# ==========================================================================
# Advisory Unit D memory (D-018-R016) + Unit C ontology (R015)
# ==========================================================================


def memory_advisory(repo: str, task_id: str, memory_base: str | None = None) -> dict:
    """Bounded ADVISORY memory evidence for the task; absence/quarantine
    honest. Never raises: memory is advisory, its failure is a labeled state."""
    out = {"advisory": True, "status": "ok", "digests": [],
           "quarantined_digests": 0,
           "note": ("ADVISORY evidence only (D-013-R038/D-018-R016): memory "
                    "digests never substitute for authoritative sources")}
    try:
        from tools import memory_graph as mg
        store = mg.memory_store(repo, base=memory_base)
        cur = store.load_current()
        qdir = store.root / "digest-quarantine"
        out["quarantined_digests"] = (len(list(qdir.glob("*.json")))
                                      if qdir.is_dir() else 0)
    except Exception as exc:
        out["status"] = "store_unavailable"
        out["reason"] = type(exc).__name__
        return out
    if cur is None:
        out["status"] = "store_empty"
        return out
    rows = []
    for did, node in sorted(cur.load_payload()["nodes"].items()):
        digest = node.get("digest") or {}
        if digest.get("task_id") != task_id:
            continue
        rows.append({"digest_id": did, "outcome": digest.get("outcome"),
                     "agent": digest.get("agent"),
                     "quarantined_links": len(node.get("quarantined_links") or [])})
    out["digests"] = rows[:MAX_MEMORY_DIGESTS]
    out["truncated"] = len(rows) > MAX_MEMORY_DIGESTS
    if not rows:
        out["status"] = "no_digests_for_task"
    return out


def ontology_placement(repo: str, impl_paths: list[str]) -> dict:
    """Unit C subsystem placement for the implementation paths (bounded)."""
    try:
        from tools.subsystem_resolver import load_map, resolve_path, version_stamp
        loaded = load_map(repo)
    except Exception as exc:
        return {"status": "ontology_unavailable", "reason": type(exc).__name__,
                "placements": [], "subsystems_touched": 0}
    placements = []
    subs = set()
    for rel in impl_paths[:25]:
        r = resolve_path(rel, loaded)
        placements.append({"path": rel, "subsystem": r["subsystem"],
                           "resolved": r["resolved"], "reason": r["reason"]})
        if r["resolved"]:
            subs.add(r["subsystem"])
    return {"status": "ok", "version": version_stamp(loaded),
            "placements": placements, "subsystems_touched": len(subs)}


def requirements_content(res: dict) -> str:
    """Canonical packet body for the requirements source."""
    return canon_json_bytes({
        "applicable_requirements": res["applicable"],
        "provenance": res["provenance"],
    }).decode("utf-8")
