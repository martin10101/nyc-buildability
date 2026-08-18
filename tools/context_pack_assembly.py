#!/usr/bin/env python3
"""Context-pack assembly: build, overflow resolution, emission (M0-T065 Unit B).

The domain orchestrator (Section 12.3/12.4). Gathers sources under ONE total
budget (the single effective byte bound), selects the adaptive TARGET tier from
the index's dependency-breadth signal WITHOUT touching the hard ceiling, resolves
overflow (summarize non-material logs; FAIL CLOSED with a split proposal when
material does not fit -- never a silent truncation), and writes context.md +
context.meta.json + evidence/ atomically. Role sufficiency lives here as the
policy that decides whether the packet is adequate for the role.
"""
from __future__ import annotations

import os
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_pack_render as render  # noqa: E402
from tools.context_pack_budget import (  # noqa: E402
    SPLIT_SUMMARIZE_GUIDANCE, effective_ceiling_tokens, estimate_tokens,
    select_tier, TierSignals,
)
from tools.context_pack_io import atomic_write, canon_json_bytes, run_git, sha256_hex  # noqa: E402
from tools.context_pack_render import SUMMARY_HEAD_LINES  # noqa: E402
from tools.context_pack_sources import gather_sources  # noqa: E402


# ==========================================================================
# Role sufficiency (Section 12.3)
# ==========================================================================

ROLE_REQUIRED = {
    "worker": ("task_packet", "routing_table"),
    "reviewer": ("task_packet", "git_diff"),
    "controller": ("task_packet", "ledger_state"),
}


def assess_sufficiency(role: str, present_groups: set) -> dict:
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
# Build (Section 12.4)
# ==========================================================================


def _index_opts(args) -> dict:
    return {
        "cache_base": getattr(args, "index_cache_base", None),
        "persist_telemetry": not getattr(args, "no_index_telemetry", False),
        "no_index": getattr(args, "no_index", False),
        "run_id": f"context_pack:{args.task}:{args.role}",
    }


def build(args) -> dict:
    """Assemble the packet. Returns a result dict (no files written yet)."""
    repo = os.path.abspath(args.repo)
    rc, head_out = run_git(repo, ["rev-parse", "HEAD"])
    repo_sha = head_out.strip() if rc == 0 and head_out.strip() else "UNKNOWN"

    sources, omissions, graph_queries, task_obj, index_provenance = gather_sources(
        repo, args.task, args.diff_base, args.include, args.ci_summary,
        args.graph_limit, _index_opts(args))

    # Adaptive tier -- sets the TARGET only; the hard ceiling is untouched.
    signals = TierSignals(
        dependency_breadth=int(index_provenance.get("dependency_breadth") or 0),
        changed_files=int(index_provenance.get("changed_targets") or 0),
        subsystems_touched=0,
        architectural=bool(getattr(args, "architectural", False)),
        explicit_tier=getattr(args, "tier", None),
        justification=getattr(args, "tier_justification", None))
    tier = select_tier(args.task, args.role, signals)
    effective_target_tokens = (args.target_tokens if args.target_tokens is not None
                               else tier.target_tokens)

    # Bounds -- ONE total budget; the effective byte bound is UNCHANGED by the tier.
    ceiling = effective_ceiling_tokens(
        args.ordinary_ceiling_tokens, args.relative_ratio, args.context_window)
    ceiling_bytes = int(ceiling["tokens"] * args.bytes_per_token)
    effective_bound_bytes = min(args.max_bytes, ceiling_bytes)

    for src in sources:
        src.content_rendered = src.content

    present_groups = {s.group for s in sources}
    sufficiency = assess_sufficiency(args.role, present_groups)

    tier_dict = tier.to_dict()
    header = render.make_header(args, repo_sha, effective_bound_bytes, ceiling, tier_dict)

    def _footer_for(overflow_state: dict, total_bytes: int) -> str:
        partial = {
            "omissions": omissions,
            "sufficiency": sufficiency,
            "overflow": overflow_state,
            "effective_bound_bytes": effective_bound_bytes,
            "tier_decision": tier_dict,
        }
        estimated = estimate_tokens(total_bytes, args.bytes_per_token)
        return render.make_footer(partial, total_bytes, estimated, args)

    def _emitted_bytes(cur_digests: dict, cur_truncations: dict,
                       overflow_state: dict) -> int:
        _, total = render.finalize_md(
            header, sources, cur_digests, cur_truncations,
            lambda tb: _footer_for(overflow_state, tb))
        return total

    truncations: dict = {}
    original_digests = {s.sid: sha256_hex(s.content.encode("utf-8")) for s in sources}
    digests = {s.sid: sha256_hex(s.content_rendered.encode("utf-8")) for s in sources}

    overflow = {"triggered": False, "resolved": "within_bound", "guidance": [],
                "split_proposal": None}
    full_bytes = _emitted_bytes(digests, truncations, overflow)

    if full_bytes > effective_bound_bytes:
        overflow = {"triggered": True, "resolved": "summarized",
                    "guidance": list(SPLIT_SUMMARIZE_GUIDANCE), "split_proposal": None}
        for src in sources:
            if not src.material and len(src.content.encode("utf-8")) > 0:
                summary = render.summarize_content(src.content)
                artifact = render._safe_name(src.sid) + ".orig." + render._ext_for(src.lang)
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
        after_bytes = _emitted_bytes(digests, truncations, overflow)

        if after_bytes > effective_bound_bytes:
            overflow = {"triggered": True, "resolved": "split_required",
                        "guidance": list(SPLIT_SUMMARIZE_GUIDANCE),
                        "split_proposal": _make_split_proposal(
                            sources, effective_bound_bytes, original_digests)}

    final_digests = {s.sid: sha256_hex(s.content_rendered.encode("utf-8")) for s in sources}

    return {
        "repo": repo,
        "repo_sha": repo_sha,
        "sources": sources,
        "omissions": omissions,
        "graph_queries": graph_queries,
        "index_provenance": index_provenance,
        "tier_decision": tier_dict,
        "effective_target_tokens": effective_target_tokens,
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
    bins: list = []
    oversize: list = []
    current = None
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


# ==========================================================================
# Emission
# ==========================================================================


def emit(result, args) -> tuple[dict, int]:
    """Write context.md, context.meta.json, evidence/. Returns (meta, exit_code)."""
    out = os.path.abspath(args.out)
    evidence = os.path.join(out, "evidence")
    os.makedirs(evidence, exist_ok=True)

    header = render.make_header(args, result["repo_sha"], result["effective_bound_bytes"],
                                result["ceiling"], result["tier_decision"])

    split_required = result["overflow"]["resolved"] == "split_required"

    if split_required:
        md_body = render.render_split_report(result, args, header)
        actual_bytes = len(md_body.encode("utf-8"))
        estimated = estimate_tokens(actual_bytes, args.bytes_per_token)
        meta = render.make_meta(result, args, actual_bytes, estimated)
        _write_evidence(evidence, result)
        atomic_write(os.path.join(out, "context.md"), md_body.encode("utf-8"))
        atomic_write(os.path.join(out, "context.meta.json"), canon_json_bytes(meta))
        return meta, 2

    def _footer_for(total_bytes: int) -> str:
        estimated = estimate_tokens(total_bytes, args.bytes_per_token)
        partial = dict(result)
        return render.make_footer(partial, total_bytes, estimated, args)

    md, actual_bytes = render.finalize_md(
        header, result["sources"], result["final_digests"],
        result["truncations"], _footer_for)
    estimated = estimate_tokens(actual_bytes, args.bytes_per_token)
    _write_evidence(evidence, result)
    atomic_write(os.path.join(out, "context.md"), md.encode("utf-8"))
    meta = render.make_meta(result, args, actual_bytes, estimated)
    atomic_write(os.path.join(out, "context.meta.json"), canon_json_bytes(meta))
    return meta, 0


def _write_evidence(evidence_dir: str, result) -> None:
    for s in result["sources"]:
        name = render._safe_name(s.sid) + "." + render._ext_for(s.lang)
        atomic_write(os.path.join(evidence_dir, name),
                     s.content_rendered.encode("utf-8"))
        if s.sid in result["truncations"]:
            art = result["truncations"][s.sid]["artifact"]
            atomic_write(os.path.join(evidence_dir, art), s.content.encode("utf-8"))
