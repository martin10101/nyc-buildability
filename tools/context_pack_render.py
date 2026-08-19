#!/usr/bin/env python3
"""Context-pack rendering + meta serialization (M0-T065 Unit B).

Owns the Section-12.3 machine record and the human-readable ``context.md`` render
(source blocks, header/footer, the fail-closed split report, and the footer-aware
size fixpoint). The R040 emission is assembled here: included sources, omitted
categories with reasons, truncations, source digests, graph query parameters,
estimated tokens, actual bytes, the role-sufficiency verdict, PLUS the index
provenance/census block, the coverage mode, the single-total-budget marker, and
the adaptive-tier + amendment blocks. Pure formatting -- no external I/O beyond
hashing/JSON helpers.
"""
from __future__ import annotations

import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.context_pack_budget import BUDGET_AMENDMENT, estimate_tokens  # noqa: E402
from tools.context_pack_io import sha256_hex  # noqa: E402
from tools.context_pack_sources import DEFAULT_EXCLUSIONS, SUMMARY_HEAD_LINES  # noqa: E402
from tools.context_paths import CONTAINMENT_VERSION as _CONTAINMENT_VERSION  # noqa: E402


def _containment_version() -> str:
    return _CONTAINMENT_VERSION

SCHEMA_VERSION = "1.1"


def _safe_name(sid: str) -> str:
    out = []
    flattened = False
    for ch in sid:
        if ch.isalnum() or ch in "._-":
            out.append(ch)
        else:
            out.append("__")
            flattened = True
    name = "".join(out)
    # Collision-proofing (F6): flattening separators could map two distinct source
    # ids to the same evidence filename (e.g. `a/b` vs `a__b`). When any separator
    # was flattened, suffix a short deterministic sha256 of the ORIGINAL id so the
    # mapping is injective. Deterministic: same id -> same name across runs.
    if flattened:
        name += "-" + sha256_hex(sid.encode("utf-8"))[:8]
    return name


def _ext_for(lang: str) -> str:
    return {"json": "json", "python": "py", "markdown": "md",
            "typescript": "ts", "diff": "diff"}.get(lang, "txt")


def summarize_content(content: str) -> str:
    head = content.splitlines()[:SUMMARY_HEAD_LINES]
    return "\n".join(head)


def _render_source_block(src, digest: str, nbytes: int, truncation: dict | None) -> str:
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


def build_context_md(header: str, sources: list, digests: dict,
                     truncations: dict, footer: str) -> str:
    parts = [header]
    for src in sorted(sources, key=lambda s: s.sort_key()):
        nbytes = len(src.content_rendered.encode("utf-8"))
        parts.append(_render_source_block(src, digests[src.sid], nbytes,
                                          truncations.get(src.sid)))
    parts.append(footer)
    return "\n".join(parts).rstrip() + "\n"


def finalize_md(header: str, sources: list, digests: dict,
                truncations: dict, footer_fn) -> tuple[str, int]:
    """Render context.md, iterating the footer's self-referential size to a fixpoint.

    ``footer_fn(total_bytes)`` returns the REAL footer given the total context.md
    byte size shown inside it. This makes the emitted-size decision footer-aware:
    the bound is enforced against header + source blocks + the ACTUAL footer, not a
    placeholder (F1). Converges because the only self-reference is the decimal
    byte/token count, whose digit width stabilizes after one or two passes (the
    total is monotone and bounded). Deterministic: same inputs -> same iterations.
    Returns ``(md, byte_len)`` where ``byte_len == len(md.encode("utf-8"))``.
    """
    total = 0
    md = ""
    new_total = 0
    for _ in range(8):
        footer = footer_fn(total)
        md = build_context_md(header, sources, digests, truncations, footer)
        new_total = len(md.encode("utf-8"))
        if new_total == total:
            break
        total = new_total
    return md, new_total


def make_header(args, repo_sha, effective_bound_bytes, ceiling, tier) -> str:
    return "\n".join([
        f"# Context pack: {args.task}",
        "",
        f"- task_id: {args.task}",
        f"- role: {args.role}",
        f"- provider: {args.provider}",
        f"- model: {getattr(args, 'model', None)}",
        f"- repo_sha: {repo_sha}",
        f"- max_bytes: {args.max_bytes}",
        f"- effective_bound_bytes: {effective_bound_bytes}",
        f"- effective_ceiling_tokens: {ceiling['tokens']} (basis: {ceiling['basis']})",
        f"- budget_tier: {tier['tier']} (adaptive target {tier['target_tokens']} tokens; "
        f"hard ceiling unchanged: {str(tier['hard_ceiling_unchanged']).lower()})",
        "",
        "This packet is deterministic: the same repo state + args yields byte-identical output.",
        "The repository SHA is the only time anchor (no wall-clock timestamps).",
        "",
    ])


def make_footer(result, actual_bytes, estimated, args) -> str:
    lines = ["---", "", "## Omitted categories (default exclusions + conditional)", ""]
    for cat, reason in DEFAULT_EXCLUSIONS:
        lines.append(f"- `{cat}` (default): {reason}")
    for om in sorted(result["omissions"], key=lambda o: o["category"]):
        lines.append(f"- `{om['category']}`: {om['reason']}")
    lines += ["", "## Role sufficiency", "",
              f"- sufficient: {str(result['sufficiency']['sufficient']).lower()}",
              f"- reason: {result['sufficiency']['reason']}", ""]
    tier = result["tier_decision"]
    lines += ["## Budget", "",
              "- single_total_budget: true",
              f"- tier: {tier['tier']}",
              f"- adaptive_target_tokens: {tier['target_tokens']}",
              f"- hard_ceiling_unchanged: {str(tier['hard_ceiling_unchanged']).lower()}",
              f"- amendment: {BUDGET_AMENDMENT['amendment_id']} "
              f"(changes_constants: {str(BUDGET_AMENDMENT['changes_constants']).lower()})", ""]
    if tier.get("withheld_larger_target"):
        lines.append(f"- withheld_larger_target: {tier['withheld_reason']}")
        lines.append("")
    ov = result["overflow"]
    lines += ["## Overflow", "",
              f"- triggered: {str(ov['triggered']).lower()}",
              f"- resolved: {ov['resolved']}",
              f"- actual_bytes: {actual_bytes}",
              f"- estimated_tokens: {estimated}",
              f"- effective_bound_bytes: {result['effective_bound_bytes']}", ""]
    # Note: make_footer is only ever rendered on the non-split path
    # (resolved in {within_bound, summarized}); the split_required path renders via
    # render_split_report and never reaches here, so no split branch belongs here (F3).
    return "\n".join(lines)


def render_split_report(result, args, header) -> str:
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
              json.dumps(result["overflow"]["split_proposal"], sort_keys=True,
                         indent=2, ensure_ascii=False),
              "```", "", "### Guidance", ""]
    for g in result["overflow"]["guidance"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def make_meta(result, args, actual_bytes, estimated) -> dict:
    ceiling = result["ceiling"]
    tier = result["tier_decision"]
    effective_target = result["effective_target_tokens"]
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
    extras = result.get("extras") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": args.task,
        "repo_sha": result["repo_sha"],
        "role": args.role,
        "provider": args.provider,
        "model": getattr(args, "model", None),
        # generated_from records ONLY disclosure-safe references: accepted
        # (canonical, contained) --include values and a redacted view of the
        # --ci-summary request. A refused absolute/traversal value is never
        # repeated here (M0-T076, D-019-R024) — its raw string stays out of the
        # packet metadata entirely; the refusal is recorded, redacted, below.
        "generated_from": {
            "repo": ".",
            "diff_base": getattr(args, "diff_base", None),
            "include": (extras.get("explicit_reads") or {}).get("include_accepted",
                                                                []),
            "include_refused": (extras.get("explicit_reads") or {}).get(
                "include_refused", []),
            "ci_summary": (extras.get("explicit_reads") or {}).get(
                "ci_summary", {"requested": bool(getattr(args, "ci_summary", None))}),
            "graph_limit": args.graph_limit,
        },
        # M0-T075 vertical-integration provenance (D-018-R011..R018) --------
        "integration": {
            "containment_version": _containment_version(),
            "requirements": extras.get("requirements"),
            "implementation_paths": extras.get("implementation_paths"),
            "prose_extraction": extras.get("prose_extraction"),
            "seed_selection": extras.get("seed_selection"),
            "unresolved_seeds": extras.get("unresolved_seeds"),
            "selection": extras.get("selection"),
            "unit_e_primitive": "repo_views.neighborhood_edges",
            "ontology_status": extras.get("ontology_status"),
            "memory_status": extras.get("memory_status"),
            "subsystems_touched": extras.get("subsystems_touched"),
        },
        "budget": {
            "single_total_budget": True,
            "target_tokens": effective_target,
            "ordinary_ceiling_tokens": args.ordinary_ceiling_tokens,
            "relative_ceiling_ratio": args.relative_ratio,
            "bytes_per_token": args.bytes_per_token,
            "model_context_window": args.context_window,
            "tier": tier,
            "amendment": BUDGET_AMENDMENT,
        },
        "bounds": {
            "max_bytes": args.max_bytes,
            "target_tokens": effective_target,
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
            "within_target": estimated <= effective_target,
            "within_effective_ceiling": estimated <= ceiling["tokens"],
        },
        "included_files": included,
        "omitted_categories": omitted,
        "graph_queries": result["graph_queries"],
        "provenance": result["index_provenance"],
        "truncated_any": truncated_any,
        "truncations": [result["truncations"][k] for k in sorted(result["truncations"])],
        "sufficiency": result["sufficiency"],
        "overflow": result["overflow"],
    }
