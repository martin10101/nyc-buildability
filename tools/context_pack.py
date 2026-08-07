#!/usr/bin/env python3
"""Bounded, deterministic context-pack builder (D-010 Section 12; 0A.4 budgets).

Produces the SMALLEST COMPLETE packet for one task/role/provider under explicit
byte and estimated-token bounds. Given the same repository state and the same
arguments it emits BYTE-IDENTICAL ``context.md`` and ``context.meta.json`` (the
repository SHA is the only time anchor; there are no wall-clock timestamps and
every list/dict is ordered deterministically).

Output (Section 12.3):

    <out>/context.md         the packet, human-readable, deterministic order
    <out>/context.meta.json  the machine record (all 12.3 fields)
    <out>/evidence/          copied source excerpts / changed hunks / artifacts

Budgets (0A.4 / D-010-R085): a deterministic bytes->tokens estimate governs a
three-tier ceiling -- a <=32,000-token target, a <=64,000-token ordinary hard
ceiling, and a <=20%-of-model-window relative hard ceiling; the EFFECTIVE ceiling
is the lower of the ordinary and relative ceilings. These are engineering-policy
numbers, not claims about any provider's billing. The constants and the estimate
are mirrored from tools/agent_supervisor/review_packet.py (the frozen shadow-only
supervisor implements the identical budget for review packets); a drift-lock test
in tools/test_context_pack.py asserts the two never diverge. This module keeps a
LOCAL copy so the runtime is decoupled from that shadow-only tree.

Overflow (Section 12.4 / D-010-R046 / AD-046): when the assembled packet exceeds
the effective bound the builder first replaces large NON-material logs with
deterministic summaries plus exact artifact references (the full original is kept
under evidence/ and its digest recorded). A MATERIAL source is NEVER silently
truncated: if the material still does not fit, the builder FAILS CLOSED with a
deterministic split proposal (exact source lists per sub-packet) and a non-zero
exit -- it never emits a quietly smaller packet.

Trust model for graph-derived hints: the code-navigation graph is ADVISORY. Its
bounded query output points at likely locations; the packet records the exact
queries used but never embeds the whole graph, and the actual source excerpts --
not the graph -- are the authority a reviewer verifies against.

STDLIB ONLY. Python 3.11+ compatible. Path-safe on Windows and POSIX.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys

SCHEMA_VERSION = "1.0"

# ==========================================================================
# 0A.4 budget -- LOCAL mirror of tools/agent_supervisor/review_packet.py.
# The drift-lock test asserts constant + estimate equality with that module.
# ==========================================================================

DEFAULT_TARGET_TOKENS = 32_000
DEFAULT_ORDINARY_CEILING_TOKENS = 64_000
DEFAULT_RELATIVE_CEILING_RATIO = 0.20
#: Deterministic bytes-per-token estimate. Four bytes/token is the conventional
#: rough English heuristic; POLICY, not a tokenizer, and configurable.
DEFAULT_BYTES_PER_TOKEN = 4.0

#: 0A.4 rules 1-4/6 overflow response, emitted with every over-ceiling refusal.
SPLIT_SUMMARIZE_GUIDANCE = (
    "split the task or the review into smaller bounded units",
    "replace full logs with deterministic summaries and exact artifact references",
    "include only the relevant changed hunks and authoritative source excerpts",
    "use bounded code-graph queries instead of any full dump",
    "never silently omit a material requirement to fit the budget",
    "never solve the overflow by opening a giant persistent conversation",
)


def estimate_tokens(size_bytes: int, bytes_per_token: float = DEFAULT_BYTES_PER_TOKEN) -> int:
    """Deterministic byte->token estimate (ceil). An ESTIMATE, not billing."""
    return math.ceil(max(0, size_bytes) / bytes_per_token)


def effective_ceiling_tokens(
    ordinary_ceiling_tokens: int,
    relative_ratio: float,
    model_context_window: int | None,
) -> dict:
    """The 0A.4 effective ceiling: the LOWER of ordinary and relative.

    When the model context window is unknown/unreported the relative ceiling
    cannot be computed and is NOT applied -- the ordinary ceiling stands and the
    record says so honestly (a window is never fabricated).
    """
    if not model_context_window or model_context_window <= 0:
        return {
            "tokens": ordinary_ceiling_tokens,
            "basis": "ordinary_only",
            "ordinary_ceiling_tokens": ordinary_ceiling_tokens,
            "relative_ceiling_tokens": None,
            "relative_applied": False,
            "model_context_window": None,
        }
    relative = int(model_context_window * relative_ratio)
    tokens = min(ordinary_ceiling_tokens, relative)
    basis = "relative_model_window" if relative < ordinary_ceiling_tokens else "ordinary"
    return {
        "tokens": tokens,
        "basis": basis,
        "ordinary_ceiling_tokens": ordinary_ceiling_tokens,
        "relative_ceiling_tokens": relative,
        "relative_applied": True,
        "model_context_window": model_context_window,
    }


# ==========================================================================
# Deterministic helpers
# ==========================================================================


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
REDUCIBLE_GROUPS = frozenset({"code_graph", "latest_ci", "previous_handoff"})

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
                   ci_summary: str | None, graph_limit: int) -> tuple[list[Source], list[dict], list[dict], dict]:
    """Returns (sources, conditional_omissions, graph_queries, task_packet_obj)."""
    sources: list[Source] = []
    omissions: list[dict] = []
    graph_queries: list[dict] = []

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
    rc_names, names_out = run_git(repo, ["diff", "--name-only", diff_base])
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

    # 5. code graph -- BOUNDED advisory queries only ---------------------
    query_py = os.path.join(repo, "tools", "code_graph", "query.py")
    graph_lines: list[str] = []
    if os.path.exists(query_py):
        # Deterministic bounded query set: file-summaries for changed paths and
        # the task's declared outputs, sorted and de-duplicated, capped.
        targets = list(changed)
        for out_path in (task_obj or {}).get("outputs", []) if isinstance(task_obj, dict) else []:
            if isinstance(out_path, str):
                targets.append(out_path)
        seen = []
        for t in sorted(set(targets)):
            if t and t not in seen:
                seen.append(t)
        for target in seen[:5]:
            rc_q, out_q = _run_graph_query(repo, query_py, "file", target, graph_limit)
            entry = {"subcommand": "file", "arg": target, "limit": graph_limit,
                     "ok": rc_q == 0, "lines_returned": len(out_q.splitlines())}
            graph_queries.append(entry)
            graph_lines.append(f"$ query.py file {target} --limit {graph_limit}")
            graph_lines.append(out_q.strip() if out_q.strip() else "(no result / advisory miss)")
            graph_lines.append("")
        if not seen:
            omissions.append({"category": "code_graph_no_targets", "default_exclusion": False,
                              "reason": "no changed paths or task outputs to derive bounded graph queries from"})
    else:
        omissions.append({"category": "code_graph_unavailable", "default_exclusion": False,
                          "reason": "tools/code_graph/query.py not present in this repo; graph hints omitted"})
    if graph_lines:
        header = ("Advisory only: the code graph points at likely locations; the "
                  "source excerpts below, not these hints, are authoritative.\n\n")
        sources.append(Source(
            "code_graph", "code_graph", 40, "Code-graph advisory hints (bounded)",
            "code_graph", "tools/code_graph/query.py", "text", header + "\n".join(graph_lines)))

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
    for inc in sorted(set(include)):
        abspath = inc if os.path.isabs(inc) else os.path.join(repo, inc)
        text = read_text(abspath)
        rel = rel_posix(abspath, repo)
        if text is None:
            omissions.append({"category": "explicit_source", "default_exclusion": False,
                              "reason": f"--include not readable: {rel}"})
            continue
        sources.append(Source(
            f"include::{rel}", "explicit_sources", 100, f"Explicit source: {rel}",
            "explicit_source", rel, _lang_for(rel), text))

    # 12. previous handoff ------------------------------------------------
    handoff_src = _gather_handoff(repo)
    if handoff_src:
        sources.append(handoff_src)
    else:
        omissions.append({"category": "previous_handoff", "default_exclusion": False,
                          "reason": "no session-handoff-*.json and no docs/SESSION_HANDOFF.md"})

    return sources, omissions, graph_queries, (task_obj if isinstance(task_obj, dict) else {})


def _run_graph_query(repo: str, query_py: str, sub: str, arg: str, limit: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            [sys.executable, query_py, "--repo", repo, sub, arg, "--limit", str(limit)],
            cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    return proc.returncode, proc.stdout.decode("utf-8", errors="replace")


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
        abspath = os.path.join(repo, *rel.split("/"))
        text = read_text(abspath)
        if text is None:
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


# ==========================================================================
# Role sufficiency (Section 12.3)
# ==========================================================================

ROLE_REQUIRED = {
    "worker": ("task_packet", "routing_table"),
    "reviewer": ("task_packet", "git_diff"),
    "controller": ("task_packet", "ledger_state"),
}


def assess_sufficiency(role: str, present_groups: set[str]) -> dict:
    required = ROLE_REQUIRED[role]
    missing = [r for r in required if r not in present_groups]
    reason_parts = []
    sufficient = not missing
    if role == "reviewer":
        # A reviewer packet must carry PRIMARY SOURCE (changed hunks), never the
        # worker's summary alone (Section 12.3).
        if "git_diff" not in present_groups:
            sufficient = False
            reason_parts.append(
                "reviewer packet lacks primary-source changed hunks (git_diff); "
                "a worker claim cannot be verified from a summary alone")
    if missing:
        reason_parts.append("missing required source groups: " + ", ".join(missing))
    if sufficient and not reason_parts:
        reason_parts.append(
            f"all required source groups for role '{role}' are present: "
            + ", ".join(required))
    return {
        "role": role,
        "sufficient": sufficient,
        "reason": " ; ".join(reason_parts),
        "required_source_groups": list(required),
        "present_source_groups": sorted(present_groups),
        "missing_source_groups": missing,
    }


# ==========================================================================
# Packet assembly + overflow (Section 12.4 / AD-046)
# ==========================================================================


def _render_source_block(src: Source, digest: str, nbytes: int, truncation: dict | None) -> str:
    lines = [
        f"## {src.order}. {src.title}",
        "",
        f"- source_id: `{src.sid}`",
        f"- category: {src.category}",
        f"- origin: `{src.origin}`",
        f"- sha256: `{digest}`",
        f"- bytes: {nbytes}",
        f"- estimated_tokens: {estimate_tokens(nbytes)}",
        f"- material: {str(src.material).lower()}",
    ]
    if truncation:
        lines.append(
            f"- SUMMARIZED: original {truncation['original_bytes']} bytes "
            f"(sha256 `{truncation['original_sha256']}`) preserved at "
            f"`evidence/{truncation['artifact']}`")
    lines.append("")
    lines.append(f"```{src.lang}")
    lines.append(src.content_rendered)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def build_context_md(header: str, sources: list[Source], digests: dict,
                     truncations: dict, footer: str) -> str:
    parts = [header]
    for src in sorted(sources, key=lambda s: s.sort_key()):
        nbytes = len(src.content_rendered.encode("utf-8"))
        parts.append(_render_source_block(src, digests[src.sid], nbytes,
                                          truncations.get(src.sid)))
    parts.append(footer)
    return "\n".join(parts).rstrip() + "\n"


def summarize_content(content: str) -> str:
    head = content.splitlines()[:SUMMARY_HEAD_LINES]
    return "\n".join(head)


def build(args) -> dict:
    """Assemble the packet. Returns a result dict (no files written yet)."""
    repo = os.path.abspath(args.repo)
    rc, head_out = run_git(repo, ["rev-parse", "HEAD"])
    repo_sha = head_out.strip() if rc == 0 and head_out.strip() else "UNKNOWN"

    sources, omissions, graph_queries, task_obj = gather_sources(
        repo, args.task, args.diff_base, args.include, args.ci_summary, args.graph_limit)

    # Bounds -----------------------------------------------------------------
    ceiling = effective_ceiling_tokens(
        args.ordinary_ceiling_tokens, args.relative_ratio, args.context_window)
    ceiling_bytes = int(ceiling["tokens"] * args.bytes_per_token)
    effective_bound_bytes = min(args.max_bytes, ceiling_bytes)

    # Attach the rendered content (full, pre-overflow) to each source.
    for src in sources:
        src.content_rendered = src.content

    present_groups = {s.group for s in sources}
    sufficiency = assess_sufficiency(args.role, present_groups)

    def digests_and_size():
        digests = {}
        for s in sources:
            digests[s.sid] = sha256_hex(s.content_rendered.encode("utf-8"))
        header = _make_header(args, repo_sha, effective_bound_bytes, ceiling)
        footer = "PLACEHOLDER_FOOTER"
        md = build_context_md(header, sources, digests, {}, footer)
        return digests, len(md.encode("utf-8"))

    # First pass: full content.
    truncations: dict[str, dict] = {}
    original_digests = {s.sid: sha256_hex(s.content.encode("utf-8")) for s in sources}
    digests, full_bytes = digests_and_size()

    overflow = {"triggered": False, "resolved": "within_bound", "guidance": [],
                "split_proposal": None}

    if full_bytes > effective_bound_bytes:
        overflow["triggered"] = True
        # Step 1: summarize NON-material reducible logs, preserving originals.
        for src in sources:
            if not src.material and len(src.content.encode("utf-8")) > 0:
                summary = summarize_content(src.content)
                artifact = _safe_name(src.sid) + ".orig." + _ext_for(src.lang)
                truncations[src.sid] = {
                    "source_id": src.sid,
                    "original_bytes": len(src.content.encode("utf-8")),
                    "original_sha256": original_digests[src.sid],
                    "summarized_bytes": len(summary.encode("utf-8")),
                    "method": f"head_{SUMMARY_HEAD_LINES}_lines_plus_artifact_reference",
                    "artifact": artifact,
                }
                src.content_rendered = (
                    summary + "\n\n[summarized: full original preserved at "
                    f"evidence/{artifact}; sha256 {original_digests[src.sid]}]")
        digests = {s.sid: sha256_hex(s.content_rendered.encode("utf-8")) for s in sources}
        header = _make_header(args, repo_sha, effective_bound_bytes, ceiling)
        md_probe = build_context_md(header, sources, digests, truncations, "PLACEHOLDER_FOOTER")
        after_bytes = len(md_probe.encode("utf-8"))

        if after_bytes <= effective_bound_bytes:
            overflow["resolved"] = "summarized"
            overflow["guidance"] = list(SPLIT_SUMMARIZE_GUIDANCE)
        else:
            # Step 2: material still too big -> FAIL CLOSED with a split proposal.
            overflow["resolved"] = "split_required"
            overflow["guidance"] = list(SPLIT_SUMMARIZE_GUIDANCE)
            overflow["split_proposal"] = _make_split_proposal(
                sources, effective_bound_bytes, original_digests)

    # Recompute final digests/size with truncations applied.
    final_digests = {s.sid: sha256_hex(s.content_rendered.encode("utf-8")) for s in sources}

    return {
        "repo": repo,
        "repo_sha": repo_sha,
        "sources": sources,
        "omissions": omissions,
        "graph_queries": graph_queries,
        "sufficiency": sufficiency,
        "ceiling": ceiling,
        "ceiling_bytes": ceiling_bytes,
        "effective_bound_bytes": effective_bound_bytes,
        "truncations": truncations,
        "original_digests": original_digests,
        "final_digests": final_digests,
        "overflow": overflow,
        "task_obj": task_obj,
    }


def _make_split_proposal(sources, bound_bytes, original_digests) -> dict:
    material = sorted((s for s in sources if s.material), key=lambda s: s.sort_key())
    bins: list[dict] = []
    oversize: list[dict] = []
    current: dict | None = None
    for s in material:
        b = len(s.content.encode("utf-8"))
        if b > bound_bytes:
            oversize.append({
                "source_id": s.sid,
                "bytes": b,
                "original_sha256": original_digests[s.sid],
                "advice": ("this single material source exceeds the effective bound "
                           "on its own; split the TASK so this source is smaller "
                           "(it must not be silently truncated)"),
            })
            continue
        if current is None or current["bytes"] + b > bound_bytes:
            current = {"sub_packet": len(bins) + 1, "sources": [], "bytes": 0}
            bins.append(current)
        current["sources"].append(s.sid)
        current["bytes"] += b
    return {
        "effective_bound_bytes": bound_bytes,
        "sub_packets": bins,
        "oversize_material_sources": oversize,
        "note": ("fail-closed: a material source does not fit. Build these sub-packets "
                 "separately (each within the bound) and/or split the task; never emit "
                 "a quietly smaller packet."),
    }


def _make_header(args, repo_sha, effective_bound_bytes, ceiling) -> str:
    return "\n".join([
        f"# Context pack: {args.task}",
        "",
        f"- task_id: {args.task}",
        f"- role: {args.role}",
        f"- provider: {args.provider}",
        f"- repo_sha: {repo_sha}",
        f"- max_bytes: {args.max_bytes}",
        f"- effective_bound_bytes: {effective_bound_bytes}",
        f"- effective_ceiling_tokens: {ceiling['tokens']} (basis: {ceiling['basis']})",
        "",
        "This packet is deterministic: the same repo state + args yields byte-identical output.",
        "The repository SHA is the only time anchor (no wall-clock timestamps).",
        "",
    ])


def _make_footer(result, actual_bytes, estimated, args) -> str:
    lines = ["---", "", "## Omitted categories (default exclusions + conditional)", ""]
    for cat, reason in DEFAULT_EXCLUSIONS:
        lines.append(f"- `{cat}` (default): {reason}")
    for om in sorted(result["omissions"], key=lambda o: o["category"]):
        lines.append(f"- `{om['category']}`: {om['reason']}")
    lines += ["", "## Role sufficiency", "",
              f"- sufficient: {str(result['sufficiency']['sufficient']).lower()}",
              f"- reason: {result['sufficiency']['reason']}", ""]
    ov = result["overflow"]
    lines += ["## Overflow", "",
              f"- triggered: {str(ov['triggered']).lower()}",
              f"- resolved: {ov['resolved']}",
              f"- actual_bytes: {actual_bytes}",
              f"- estimated_tokens: {estimated}",
              f"- effective_bound_bytes: {result['effective_bound_bytes']}", ""]
    if ov["resolved"] == "split_required":
        lines.append("- FAIL-CLOSED: material does not fit. Split proposal:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(ov["split_proposal"], sort_keys=True, indent=2))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def _safe_name(sid: str) -> str:
    out = []
    for ch in sid:
        out.append(ch if (ch.isalnum() or ch in "._-") else "__")
    return "".join(out)


def _ext_for(lang: str) -> str:
    return {"json": "json", "python": "py", "markdown": "md",
            "typescript": "ts", "diff": "diff"}.get(lang, "txt")


# ==========================================================================
# Meta record (Section 12.3) + file emission
# ==========================================================================


def make_meta(result, args, actual_bytes, estimated) -> dict:
    ceiling = result["ceiling"]
    included = []
    for s in sorted(result["sources"], key=lambda s: s.sort_key()):
        nbytes = len(s.content_rendered.encode("utf-8"))
        included.append({
            "source_id": s.sid,
            "group": s.group,
            "category": s.category,
            "origin": s.origin,
            "sha256": result["final_digests"][s.sid],
            "bytes": nbytes,
            "estimated_tokens": estimate_tokens(nbytes),
            "material": s.material,
            "truncated": s.sid in result["truncations"],
            "truncation": result["truncations"].get(s.sid),
            "evidence_path": f"evidence/{_safe_name(s.sid)}.{_ext_for(s.lang)}",
        })
    omitted = []
    for cat, reason in DEFAULT_EXCLUSIONS:
        omitted.append({"category": cat, "default_exclusion": True, "reason": reason})
    omitted.extend(sorted(result["omissions"], key=lambda o: o["category"]))
    truncated_any = bool(result["truncations"])
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": args.task,
        "repo_sha": result["repo_sha"],
        "role": args.role,
        "provider": args.provider,
        "generated_from": {
            "repo": rel_posix(result["repo"], result["repo"]) or ".",
            "diff_base": args.diff_base,
            "include": sorted(set(args.include)),
            "ci_summary": args.ci_summary,
            "graph_limit": args.graph_limit,
        },
        "budget": {
            "target_tokens": args.target_tokens,
            "ordinary_ceiling_tokens": args.ordinary_ceiling_tokens,
            "relative_ceiling_ratio": args.relative_ratio,
            "bytes_per_token": args.bytes_per_token,
            "model_context_window": args.context_window,
        },
        "bounds": {
            "max_bytes": args.max_bytes,
            "target_tokens": args.target_tokens,
            "ordinary_ceiling_tokens": ceiling["ordinary_ceiling_tokens"],
            "relative_ceiling_tokens": ceiling["relative_ceiling_tokens"],
            "effective_ceiling_tokens": ceiling["tokens"],
            "effective_ceiling_basis": ceiling["basis"],
            "relative_applied": ceiling["relative_applied"],
            "effective_bound_bytes": result["effective_bound_bytes"],
        },
        "actuals": {
            "context_md_bytes": actual_bytes,
            "estimated_tokens": estimated,
            "within_max_bytes": actual_bytes <= args.max_bytes,
            "within_effective_bound": actual_bytes <= result["effective_bound_bytes"],
            "within_target": estimated <= args.target_tokens,
            "within_effective_ceiling": estimated <= ceiling["tokens"],
        },
        "included_files": included,
        "omitted_categories": omitted,
        "graph_queries": result["graph_queries"],
        "truncated_any": truncated_any,
        "truncations": [result["truncations"][k] for k in sorted(result["truncations"])],
        "sufficiency": result["sufficiency"],
        "overflow": result["overflow"],
    }


def emit(result, args) -> tuple[dict, int]:
    """Write context.md, context.meta.json, evidence/. Returns (meta, exit_code)."""
    out = os.path.abspath(args.out)
    evidence = os.path.join(out, "evidence")
    os.makedirs(evidence, exist_ok=True)

    header = _make_header(args, result["repo_sha"], result["effective_bound_bytes"],
                          result["ceiling"])

    # Compute context.md with a placeholder footer first, then finalize with the
    # real footer (footer content does not depend on md size beyond the numbers
    # we already resolved during build()).
    split_required = result["overflow"]["resolved"] == "split_required"

    if split_required:
        # FAIL CLOSED: never emit the giant material packet. Emit a bounded
        # overflow report (digests + split plan), and the full material stays in
        # evidence/ for the split follow-up -- nothing is silently dropped.
        md_body = _render_split_report(result, args, header)
        actual_bytes = len(md_body.encode("utf-8"))
        estimated = estimate_tokens(actual_bytes, args.bytes_per_token)
        meta = make_meta(result, args, actual_bytes, estimated)
        _write_evidence(evidence, result)
        _atomic_write(os.path.join(out, "context.md"), md_body.encode("utf-8"))
        _atomic_write(os.path.join(out, "context.meta.json"), canon_json_bytes(meta))
        return meta, 2

    # Normal / summarized path.
    footer = _make_footer_two_pass(result, args, header)
    _write_evidence(evidence, result)
    _atomic_write(os.path.join(out, "context.md"), footer.encode("utf-8"))
    actual_bytes = len(footer.encode("utf-8"))
    estimated = estimate_tokens(actual_bytes, args.bytes_per_token)
    meta = make_meta(result, args, actual_bytes, estimated)
    _atomic_write(os.path.join(out, "context.meta.json"), canon_json_bytes(meta))
    return meta, 0


def _make_footer_two_pass(result, args, header) -> str:
    # Two-pass: build once with placeholder numbers to learn the byte size, then
    # rebuild the footer with the true byte/token totals so context.md is
    # self-consistent and deterministic.
    md0 = build_context_md(header, result["sources"], result["final_digests"],
                           result["truncations"], "PLACEHOLDER_FOOTER")
    size0 = len(md0.replace("PLACEHOLDER_FOOTER",
                            _make_footer(result, 0, 0, args)).encode("utf-8"))
    est0 = estimate_tokens(size0, args.bytes_per_token)
    footer = _make_footer(result, size0, est0, args)
    return build_context_md(header, result["sources"], result["final_digests"],
                            result["truncations"], footer)


def _render_split_report(result, args, header) -> str:
    lines = [header, "## OVERFLOW: fail-closed (material does not fit)", "",
             "This packet was NOT emitted in full: a material source exceeds the "
             "effective bound and must never be silently truncated (AD-046). "
             "Build the sub-packets below separately and/or split the task. "
             "The full material is preserved under evidence/.", "",
             "### Material source digests", ""]
    for s in sorted((s for s in result["sources"] if s.material), key=lambda s: s.sort_key()):
        b = len(s.content.encode("utf-8"))
        lines.append(f"- `{s.sid}` — {b} bytes — sha256 `{result['original_digests'][s.sid]}` "
                     f"— evidence/{_safe_name(s.sid)}.{_ext_for(s.lang)}")
    lines += ["", "### Split proposal", "", "```json",
              json.dumps(result["overflow"]["split_proposal"], sort_keys=True, indent=2),
              "```", "", "### Guidance", ""]
    for g in result["overflow"]["guidance"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _write_evidence(evidence_dir: str, result) -> None:
    for s in result["sources"]:
        name = _safe_name(s.sid) + "." + _ext_for(s.lang)
        _atomic_write(os.path.join(evidence_dir, name),
                      s.content_rendered.encode("utf-8"))
        # Preserve full originals for summarized sources (exact artifact ref).
        if s.sid in result["truncations"]:
            art = result["truncations"][s.sid]["artifact"]
            _atomic_write(os.path.join(evidence_dir, art), s.content.encode("utf-8"))


def _atomic_write(path: str, data: bytes) -> None:
    with open(path, "wb") as fh:
        fh.write(data)


# ==========================================================================
# CLI
# ==========================================================================


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bounded, deterministic context-pack builder (D-010 Section 12).")
    p.add_argument("--task", required=True, help="task id, e.g. M0-T043")
    p.add_argument("--role", required=True, choices=("worker", "reviewer", "controller"))
    p.add_argument("--provider", required=True, choices=("claude", "codex"))
    p.add_argument("--max-bytes", required=True, type=int, dest="max_bytes")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--repo", default=".", help="repository root (default .)")
    p.add_argument("--context-window", type=int, default=None, dest="context_window",
                   help="reported model context window (for the 20%% relative ceiling)")
    p.add_argument("--include", action="append", default=[],
                   help="explicit source file (repeatable)")
    p.add_argument("--ci-summary", default=None, dest="ci_summary",
                   help="path to an injected CI summary (never fetched from network)")
    p.add_argument("--diff-base", default="HEAD", dest="diff_base",
                   help="git ref to diff against (default HEAD)")
    p.add_argument("--graph-limit", type=int, default=20, dest="graph_limit",
                   help="per-query line cap for bounded code-graph queries")
    p.add_argument("--target-tokens", type=int, default=DEFAULT_TARGET_TOKENS,
                   dest="target_tokens")
    p.add_argument("--ordinary-ceiling-tokens", type=int,
                   default=DEFAULT_ORDINARY_CEILING_TOKENS,
                   dest="ordinary_ceiling_tokens")
    p.add_argument("--relative-ratio", type=float, default=DEFAULT_RELATIVE_CEILING_RATIO,
                   dest="relative_ratio")
    p.add_argument("--bytes-per-token", type=float, default=DEFAULT_BYTES_PER_TOKEN,
                   dest="bytes_per_token")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_bytes <= 0:
        print("error: --max-bytes must be positive", file=sys.stderr)
        return 2
    result = build(args)
    meta, code = emit(result, args)
    summary = {
        "task_id": meta["task_id"],
        "role": meta["role"],
        "repo_sha": meta["repo_sha"],
        "context_md_bytes": meta["actuals"]["context_md_bytes"],
        "estimated_tokens": meta["actuals"]["estimated_tokens"],
        "included_count": len(meta["included_files"]),
        "sufficient": meta["sufficiency"]["sufficient"],
        "overflow": meta["overflow"]["resolved"],
    }
    stream = sys.stderr if code != 0 else sys.stdout
    print(json.dumps(summary, sort_keys=True), file=stream)
    if code != 0:
        print("FAIL-CLOSED: material does not fit the effective bound; see "
              "context.md split proposal.", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
