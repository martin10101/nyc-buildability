#!/usr/bin/env python3
"""Context-pack source gathering (M0-T065 Unit B).

Owns the external-I/O + evidence-selection layer (Section 12.1): the ``Source``
value type, the default-exclusion catalogue, and ``gather_sources`` with its
per-category helpers. The code-graph neighborhood + census sources are produced
deterministically from the accepted A1/A2 index via ``context_pack_index`` (no
subprocess, no cache-rebuild side effect); everything else reads bounded evidence
from the repository/ledger.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_pack_evidence as cpe  # noqa: E402
from tools import context_pack_index as cpi  # noqa: E402
from tools import context_paths as cpaths  # noqa: E402
from tools.context_pack_io import (  # noqa: E402
    canon_json_bytes, load_json, read_text, rel_posix, run_git,
)

# ==========================================================================
# Section 12.2 default exclusions -- always recorded as omitted categories.
# ==========================================================================

DEFAULT_EXCLUSIONS = (
    ("entire_prd", "the whole PRD is excluded by default; include only the bounded excerpt a task needs"),
    ("entire_directive_registry", "the full directive registry is excluded; bind only the task's directive requirement rows"),
    ("all_historical_reports", "every historical report is excluded; include only the latest checkpoint and task-relevant reports"),
    ("old_session_transcripts", "old session transcripts are excluded; the latest handoff carries forward the needed state"),
    ("unrelated_task_packets", "task packets for other tasks are excluded; only this task's packet is included"),
    ("full_generated_artifacts", "full generated artifacts are excluded; reference them by path/digest instead of embedding"),
    ("full_city_datasets", "full NYC datasets are excluded (thin-client policy); connectors fetch bounded slices at runtime"),
    ("whole_code_graph", "the whole code-navigation graph is excluded; only bounded advisory queries are recorded"),
)

#: Source groups whose content may be summarized under overflow (NON-material
#: logs). Everything else is MATERIAL and is never silently truncated (AD-046).
#: memory_advisory is explicitly ADVISORY evidence (D-018-R016) — reducible.
REDUCIBLE_GROUPS = frozenset({"code_graph", "latest_ci", "previous_handoff",
                              "memory_advisory"})

SUMMARY_HEAD_LINES = 20


class Source:
    """One gathered context source that becomes a section + an evidence file."""

    __slots__ = ("sid", "group", "order", "title", "category", "origin", "lang",
                 "content", "content_rendered")

    def __init__(self, sid, group, order, title, category, origin, lang, content):
        self.sid = sid
        self.group = group
        self.order = order
        self.title = title
        self.category = category
        self.origin = origin
        self.lang = lang
        self.content = content
        # Rendered form placed in the packet (full pre-overflow content by
        # default; assembly may replace it with a summary). Initialized here so the
        # slot is never read unset (F5).
        self.content_rendered = content

    @property
    def material(self) -> bool:
        return self.group not in REDUCIBLE_GROUPS

    def sort_key(self):
        return (self.order, self.sid)


# ==========================================================================
# Input gathering (Section 12.1)
# ==========================================================================


def _pc(repo: str, *parts: str) -> str:
    return os.path.join(repo, "project-control", *parts)


def gather_sources(repo: str, task_id: str, diff_base: str, include: list[str],
                   ci_summary: str | None, graph_limit: int,
                   index_opts: dict | None = None) -> tuple[list[Source], list[dict], list[dict], dict, dict, dict]:
    """Returns (sources, conditional_omissions, graph_queries, task_packet_obj,
    index_provenance, extras). ``index_opts`` steers the deterministic index
    consumption (cache base, telemetry, and an escape hatch). ``extras``
    carries the M0-T075 vertical-integration provenance (requirements
    resolution, prose extraction, excerpt selection, ontology, memory
    status, implementation paths) consumed by sufficiency + the meta."""
    sources: list[Source] = []
    omissions: list[dict] = []
    graph_queries: list[dict] = []
    index_opts = index_opts or {}
    extras: dict = {}

    # 1. task packet ------------------------------------------------------
    task_path = _pc(repo, "tasks", f"{task_id}.json")
    task_obj = load_json(task_path)
    if task_obj is not None:
        sources.append(Source(
            "task_packet", "task_packet", 10, "Task packet", "task_packet",
            rel_posix(task_path, repo), "json",
            canon_json_bytes(task_obj).decode("utf-8")))
    else:
        omissions.append({"category": "task_packet", "default_exclusion": False,
                          "reason": f"task packet not found at {rel_posix(task_path, repo)}"})

    # 1b. exact applicable requirement IDs + texts (M0-T075, D-018-R011) --
    req_res = cpe.resolve_requirements(repo, task_obj if isinstance(task_obj, dict) else {})
    extras["requirements"] = {k: v for k, v in req_res.items() if k != "applicable"}
    extras["requirements"]["applicable_ids"] = [r["id"] for r in req_res["applicable"]]
    if req_res["error"]:
        omissions.append({"category": "requirements", "default_exclusion": False,
                          "reason": f"requirement evidence unavailable: {req_res['error']}"})
    elif req_res["in_regime"]:
        sources.append(Source(
            "requirements", "requirements", 15,
            "Applicable directive requirements (exact IDs + texts)",
            "requirements", "project-control/directives/", "json",
            cpe.requirements_content(req_res)))
    else:
        omissions.append({"category": "requirements", "default_exclusion": False,
                          "reason": "task carries no directive_refs (not in the "
                                    "directive regime); no requirement rows bind"})

    # 2. ledger state -----------------------------------------------------
    state_path = _pc(repo, "state.json")
    state_obj = load_json(state_path)
    if state_obj is not None:
        sources.append(Source(
            "ledger_state", "ledger_state", 20, "Current ledger state", "ledger_state",
            rel_posix(state_path, repo), "json",
            canon_json_bytes(state_obj).decode("utf-8")))
    else:
        omissions.append({"category": "ledger_state", "default_exclusion": False,
                          "reason": "state.json not found or unreadable"})

    # 3/4. git diff + changed paths --------------------------------------
    rc_diff, diff_out = run_git(repo, ["diff", diff_base])
    _, names_out = run_git(repo, ["diff", "--name-only", diff_base])
    changed = sorted(p for p in names_out.splitlines() if p.strip())
    if rc_diff == 0 and diff_out.strip():
        sources.append(Source(
            "git_diff", "git_diff", 30, f"Changed hunks (git diff {diff_base})",
            "git_diff", f"git diff {diff_base}", "diff", diff_out))
    else:
        omissions.append({"category": "git_diff", "default_exclusion": False,
                          "reason": f"no changed hunks against {diff_base} (clean tree or git unavailable)"})
    changed_body = "\n".join(changed) if changed else "(no changed paths)"
    sources.append(Source(
        "changed_paths", "changed_paths", 35, "Changed paths", "changed_paths",
        f"git diff --name-only {diff_base}", "text", changed_body))

    # 5. code graph + census -- from the deterministic A1/A2 index -------
    # SEEDING (M0-T075, D-018-R012..R014): seeds are REAL paths only —
    # changed files + the task's canonical implementation paths. Prose fields
    # (outputs/inputs) are never used literally; they pass through the strict
    # deterministic extractor, and every prose candidate is recorded as
    # resolved or unresolved.
    task_dict = task_obj if isinstance(task_obj, dict) else {}
    impl_paths = cpe.implementation_paths(task_dict)
    prose = cpe.extract_prose_paths(repo, task_dict)
    extras["implementation_paths"] = impl_paths
    extras["prose_extraction"] = prose["records"]
    seed_candidates = sorted(set(changed) | set(impl_paths) | set(prose["resolved"]))
    targets, refused_seeds = [], []
    for t in seed_candidates:
        if cpaths.is_canonical_repo_path(t):
            targets.append(t)
        else:
            refused_seeds.append({"seed": t, "reason": "non_canonical_path"})
    extras["refused_seeds"] = refused_seeds
    idx = cpi.gather_index_sources(repo, targets, graph_limit, index_opts)
    sources.extend(idx["sources"])
    omissions.extend(idx["omissions"])
    graph_queries.extend(idx["graph_queries"])
    index_provenance = idx["provenance"]
    extras["unresolved_seeds"] = [
        {"seed": q.get("seed"), "reason": "seed_not_in_graph"}
        for q in idx["graph_queries"] if not q.get("resolved")] + refused_seeds

    # 5b. Unit C ontology placement for the implementation paths (R015) ---
    ont = cpe.ontology_placement(repo, impl_paths)
    extras["subsystems_touched"] = int(ont.get("subsystems_touched") or 0)
    extras["ontology_status"] = ont.get("status")
    if ont.get("status") == "ok" and ont.get("placements"):
        sources.append(Source(
            "ontology", "ontology", 47, "Subsystem placement (Unit C resolver)",
            "ontology", "tools/subsystem_resolver.py", "json",
            canon_json_bytes({"version": ont["version"],
                              "placements": ont["placements"]}).decode("utf-8")))
    else:
        omissions.append({"category": "ontology", "default_exclusion": False,
                          "reason": (f"ontology placement unavailable "
                                     f"({ont.get('reason') or 'no implementation paths'})")})

    # 5c. reopened authoritative source + test excerpts (R017) ------------
    excerpts, test_excerpts, sel_prov = cpe.select_source_excerpts(
        repo, impl_paths, changed, idx.get("graph_index"))
    extras["selection"] = sel_prov
    for e in excerpts:
        sources.append(Source(
            f"source::{e['path']}", "source_excerpts", 55,
            f"Authoritative source: {e['path']}", "source_excerpt",
            e["path"], _lang_for(e["path"]), e["content"]))
    for t in test_excerpts:
        sources.append(Source(
            f"test::{t['path']}", "source_excerpts", 56,
            f"Relevant test: {t['path']}", "test_excerpt",
            t["path"], _lang_for(t["path"]), t["content"]))
    if impl_paths and not excerpts:
        omissions.append({"category": "source_excerpts", "default_exclusion": False,
                          "reason": "implementation paths are in scope but no "
                                    "authoritative source file resolved to reopen"})

    # 5d. bounded ADVISORY Unit D memory evidence (R016) ------------------
    mem = cpe.memory_advisory(repo, task_id, index_opts.get("memory_base"))
    extras["memory_status"] = mem.get("status")
    sources.append(Source(
        "memory_advisory", "memory_advisory", 85,
        "Session memory digests (ADVISORY only)", "memory_advisory",
        "external per-checkout memory store", "json",
        canon_json_bytes(mem).decode("utf-8")))

    # 6. authoritative routing table (CLAUDE.md) -------------------------
    routing = _extract_routing_table(repo)
    if routing is not None:
        sources.append(Source(
            "routing_table", "routing_table", 50, "Authoritative routing table",
            "routing_table", "CLAUDE.md#on-demand-routing", "markdown", routing))
    else:
        omissions.append({"category": "routing_table", "default_exclusion": False,
                          "reason": "CLAUDE.md routing section not found"})

    # 7. relevant contracts (only when the task's paths touch them) ------
    contract_sources, contract_omission = _gather_contracts(repo, task_obj)
    sources.extend(contract_sources)
    if contract_omission:
        omissions.append(contract_omission)

    # 8. latest checkpoint ------------------------------------------------
    cp_path = _latest_checkpoint(repo)
    if cp_path:
        cp_obj = load_json(cp_path)
        if cp_obj is not None:
            sources.append(Source(
                "latest_checkpoint", "latest_checkpoint", 70, "Latest checkpoint",
                "latest_checkpoint", rel_posix(cp_path, repo), "json",
                canon_json_bytes(cp_obj).decode("utf-8")))
    else:
        omissions.append({"category": "latest_checkpoint", "default_exclusion": False,
                          "reason": "no project-control/checkpoints/CP-*.json found"})

    # 9. relevant blockers (reference this task) -------------------------
    blocker_sources = _gather_blockers(repo, task_id)
    if blocker_sources:
        sources.extend(blocker_sources)
    else:
        omissions.append({"category": "relevant_blockers", "default_exclusion": False,
                          "reason": f"no blocker references {task_id}"})

    # 10. latest CI -- injectable only; never network --------------------
    if ci_summary:
        ci_text = read_text(ci_summary)
        if ci_text is not None:
            sources.append(Source(
                "latest_ci", "latest_ci", 90, "Latest CI summary (injected)",
                "latest_ci", rel_posix(ci_summary, repo), "text", ci_text))
        else:
            omissions.append({"category": "latest_ci", "default_exclusion": False,
                              "reason": f"--ci-summary path unreadable: {ci_summary}"})
    else:
        omissions.append({"category": "latest_ci", "default_exclusion": False,
                          "reason": "no --ci-summary injected; builder never calls the network for CI"})

    # 11. explicit source files (--include) ------------------------------
    # Reads go ONLY through the shared containment rule (M0-T075,
    # D-018-R031/R033): absolute/drive/traversal/escaping includes are
    # REFUSED with the machine-readable code; no absolute path is echoed.
    for inc in sorted(set(include)):
        rel = str(inc).replace("\\", "/")
        while rel.startswith("./"):
            rel = rel[2:]
        try:
            data = cpaths.contained_read_bytes(repo, rel)
        except cpaths.PathContainmentError as exc:
            omissions.append({"category": "explicit_source",
                              "default_exclusion": False,
                              "reason": f"--include refused ({exc.code}): {exc.detail}"})
            continue
        sources.append(Source(
            f"include::{rel}", "explicit_sources", 100, f"Explicit source: {rel}",
            "explicit_source", rel, _lang_for(rel),
            data.decode("utf-8", errors="replace")))

    # 12. previous handoff ------------------------------------------------
    handoff_src = _gather_handoff(repo)
    if handoff_src:
        sources.append(handoff_src)
    else:
        omissions.append({"category": "previous_handoff", "default_exclusion": False,
                          "reason": "no session-handoff-*.json and no docs/SESSION_HANDOFF.md"})

    return (sources, omissions, graph_queries,
            (task_obj if isinstance(task_obj, dict) else {}), index_provenance,
            extras)


def _extract_routing_table(repo: str) -> str | None:
    text = read_text(os.path.join(repo, "CLAUDE.md"))
    if text is None:
        return None
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        s = line.strip().lower()
        if s.startswith("## ") and "routing" in s:
            start = i
            break
    if start is None:
        return None
    out = [lines[start]]
    for line in lines[start + 1:]:
        if line.startswith("## ") or line.startswith("# "):
            break
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def _gather_contracts(repo: str, task_obj) -> tuple[list[Source], dict | None]:
    prefix = "packages/contracts"
    paths = []
    if isinstance(task_obj, dict):
        for key in ("allowed_paths", "outputs", "inputs"):
            for p in task_obj.get(key, []) or []:
                if isinstance(p, str):
                    paths.append(p.replace("\\", "/"))
    touched = sorted({p for p in paths if p.startswith(prefix)})
    if not touched:
        return [], {"category": "contracts", "default_exclusion": False,
                    "reason": "task paths do not touch packages/contracts; contracts omitted (12.1 relevant-only)"}
    sources: list[Source] = []
    for rel in touched:
        # task-derived paths read through the shared containment rule (R033)
        try:
            text = cpaths.contained_read_bytes(repo, rel).decode(
                "utf-8", errors="replace")
        except cpaths.PathContainmentError:
            continue
        sources.append(Source(
            f"contract::{rel}", "contracts", 60, f"Contract: {rel}", "contract",
            rel, _lang_for(rel), text))
    if not sources:
        return [], {"category": "contracts", "default_exclusion": False,
                    "reason": "task references packages/contracts but no readable contract file resolved"}
    return sources, None


def _latest_checkpoint(repo: str) -> str | None:
    cp_dir = _pc(repo, "checkpoints")
    try:
        names = [n for n in os.listdir(cp_dir)
                 if n.startswith("CP-") and n.endswith(".json")]
    except OSError:
        return None
    if not names:
        return None
    names.sort()
    return os.path.join(cp_dir, names[-1])


def _gather_blockers(repo: str, task_id: str) -> list[Source]:
    b_dir = _pc(repo, "blockers")
    try:
        names = sorted(n for n in os.listdir(b_dir) if n.endswith(".json"))
    except OSError:
        return []
    out: list[Source] = []
    for name in names:
        path = os.path.join(b_dir, name)
        text = read_text(path)
        if text is None:
            continue
        try:
            obj = json.loads(text)
        except ValueError:
            continue
        # A blocker is relevant when the task id appears anywhere in its record
        # (affects lists, detail, etc. are freeform strings).
        if task_id in json.dumps(obj, ensure_ascii=False):
            rel = rel_posix(path, repo)
            out.append(Source(
                f"blocker::{name}", "relevant_blockers", 80, f"Blocker: {name}",
                "blocker", rel, "json", canon_json_bytes(obj).decode("utf-8")))
    return out


def _gather_handoff(repo: str) -> Source | None:
    reports = _pc(repo, "reports")
    try:
        handoffs = sorted(n for n in os.listdir(reports)
                          if n.startswith("session-handoff-") and n.endswith(".json"))
    except OSError:
        handoffs = []
    if handoffs:
        path = os.path.join(reports, handoffs[-1])
        obj = load_json(path)
        if obj is not None:
            return Source("previous_handoff", "previous_handoff", 110,
                          "Previous handoff", "previous_handoff",
                          rel_posix(path, repo), "json",
                          canon_json_bytes(obj).decode("utf-8"))
    doc = os.path.join(repo, "docs", "SESSION_HANDOFF.md")
    text = read_text(doc)
    if text is not None:
        # Include only the current top block (first heading section) to stay bounded.
        block = _first_section(text)
        return Source("previous_handoff", "previous_handoff", 110,
                      "Previous handoff (docs/SESSION_HANDOFF.md current block)",
                      "previous_handoff", "docs/SESSION_HANDOFF.md", "markdown", block)
    return None


def _first_section(text: str) -> str:
    lines = text.splitlines()
    out = []
    seen_heading = False
    for line in lines:
        if line.startswith("# ") or line.startswith("## "):
            if seen_heading:
                break
            seen_heading = True
        out.append(line)
        if len(out) >= 120:
            break
    return "\n".join(out).rstrip() + "\n"


def _lang_for(rel: str) -> str:
    lower = rel.lower()
    if lower.endswith(".json"):
        return "json"
    if lower.endswith((".py",)):
        return "python"
    if lower.endswith((".md",)):
        return "markdown"
    if lower.endswith((".ts", ".tsx")):
        return "typescript"
    if lower.endswith((".diff", ".patch")):
        return "diff"
    return "text"
