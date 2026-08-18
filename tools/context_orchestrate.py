#!/usr/bin/env python3
"""Canonical orchestrator-facing context entry point (M0-T075, D-018-R022..R026).

THE command future Claude operation invokes to prepare a grounded, bounded
work packet and (optionally) a model-routing decision for one task/role:

    python tools/context_orchestrate.py prepare --task M0-Txxx --role worker \
        --provider claude --max-bytes 400000 --out <dir> [--route]

It calls the INTEGRATED compiler (`tools/context_pack.py` build/emit — never
a second packet builder), then, when routing is requested, derives
`model_routing.Signals` FROM THE COMPILED EVIDENCE (task packet scope, diff,
graph, ontology, sufficiency). Missing or unresolved evidence sets
`ambiguity_or_missing_evidence` — a complex task is never silently defaulted
LOW (R024). The bounded routing/dispatch manifest is written next to the
packet and the decision is recorded through the accepted external runtime
convention (`model_routing.decisions_path` JSONL, bounded by rotation).

BOUNDARY (stated honestly, R026): automatic controller/supervisor consumption
of this packet would require changing protected supervisor files
(`tools/agent_supervisor/**`), which is prohibited. This entry point is the
canonical NON-protected command; the supervisor keeps building its own review
packets until the owner authorizes an integration change. Nothing here claims
automatic supervisor integration.

STDLIB ONLY. Reads the protected controller config READ-ONLY for the model
allowlist; never writes any protected file.
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_pack as cp  # noqa: E402
from tools import model_routing as mr  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402

MANIFEST_SCHEMA = "context_dispatch_manifest/v1"

#: Deterministic prefix rules for packet-derived risk flags (R023).
_CONTROL_PLANE_PREFIXES = ("project-control/", ".github/", ".claude/")
_SECURITY_PREFIXES = ("tools/agent_supervisor/", ".github/workflows/")
_SCHEMA_PREFIXES = ("packages/contracts/", "supabase/")


def derive_signals(meta: dict, compile_exit: int) -> tuple["mr.Signals", list[str]]:
    """model_routing.Signals FROM the compiled evidence (D-018-R023/R024).

    Returns (signals, notes). Every non-derivable or unresolved input is a
    note AND sets ambiguity_or_missing_evidence=True so the band can only go
    UP on unknown-ness — never a silent LOW default."""
    notes: list[str] = []
    integ = meta.get("integration") or {}
    prov = meta.get("provenance") or {}
    suff = meta.get("sufficiency") or {}
    task_paths = list((integ.get("implementation_paths") or []))
    packet = {}
    for f in meta.get("included_files") or []:
        if f.get("group") == "task_packet":
            packet = {"present": True}
    ambiguity = False
    if compile_exit != 0:
        ambiguity = True
        notes.append(f"compiler exited {compile_exit} (insufficient/split)")
    if not suff.get("sufficient", False):
        ambiguity = True
        notes.append("packet sufficiency is false")
    req = integ.get("requirements") or {}
    if req.get("in_regime") and req.get("error"):
        ambiguity = True
        notes.append("requirement evidence unresolved")
    if suff.get("code_evidence_required") and not suff.get("code_evidence_resolved"):
        ambiguity = True
        notes.append("code evidence required but unresolved")
    if integ.get("ontology_status") not in ("ok", None):
        ambiguity = True
        notes.append(f"ontology {integ.get('ontology_status')}")
    if integ.get("memory_status") == "store_unavailable":
        notes.append("memory store unavailable (advisory only; not fatal)")
    if not packet:
        ambiguity = True
        notes.append("task packet source absent")

    def _flag(prefixes: tuple[str, ...]) -> bool:
        return any(p.startswith(prefixes) for p in task_paths)

    all_scope = task_paths + [
        r.get("seed") or "" for r in (integ.get("unresolved_seeds") or [])]
    signals = mr.Signals(
        files_affected=int(prov.get("changed_targets") or 0) or len(task_paths),
        subsystems_affected=int(integ.get("subsystems_touched") or 0),
        dependency_graph_spread=int(prov.get("dependency_breadth") or 0),
        security_or_authorization_impact=_flag(_SECURITY_PREFIXES),
        protected_configuration_impact=any(
            "config.toml" in p or "model_selection" in p for p in all_scope),
        destructive_operations=False,
        control_plane_change=_flag(_CONTROL_PLANE_PREFIXES),
        legal_or_numeric_correctness=any(
            p.startswith(("services/api/app/", "packages/contracts/"))
            for p in task_paths),
        external_side_effects=False,
        schema_or_migration_impact=_flag(_SCHEMA_PREFIXES),
        concurrency_or_performance=False,
        ambiguity_or_missing_evidence=ambiguity,
        prior_failed_attempts=0,
        required_reviewer_roles=(),
        estimated_context_tokens=(meta.get("actuals") or {}).get("estimated_tokens"),
        packet_risk_classification=None,
    )
    return signals, notes


def _emit(doc: dict) -> None:
    sys.stdout.write(canon_json_bytes(doc).decode("utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Canonical context entry point: integrated compile + "
                    "grounded routing (D-018).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--task", required=True)
    p.add_argument("--role", required=True, choices=("worker", "reviewer", "controller"))
    p.add_argument("--provider", required=True, choices=("claude", "codex"))
    p.add_argument("--max-bytes", required=True, type=int, dest="max_bytes")
    p.add_argument("--out", required=True)
    p.add_argument("--repo", default=".")
    p.add_argument("--model", default=None)
    p.add_argument("--diff-base", default="HEAD", dest="diff_base")
    p.add_argument("--route", action="store_true",
                   help="derive Signals from the compiled evidence and record "
                        "a model-routing decision")
    p.add_argument("--model-config", default=None, dest="model_config",
                   help="path to the PROTECTED controller config (read-only; "
                        "required with --route)")
    p.add_argument("--decisions-path", default=None, dest="decisions_path",
                   help="override the routing-decision JSONL (tests only)")
    p.add_argument("--index-cache-base", default=None, dest="index_cache_base")
    p.add_argument("--no-index-telemetry", action="store_true",
                   dest="no_index_telemetry")
    args = ap.parse_args(argv)

    # THE integrated compiler — same parser, same build/emit, one packet.
    pack_argv = ["--task", args.task, "--role", args.role,
                 "--provider", args.provider, "--max-bytes", str(args.max_bytes),
                 "--out", args.out, "--repo", args.repo,
                 "--diff-base", args.diff_base]
    if args.model:
        pack_argv += ["--model", args.model]
    if args.index_cache_base:
        pack_argv += ["--index-cache-base", args.index_cache_base]
    if args.no_index_telemetry:
        pack_argv += ["--no-index-telemetry"]
    pack_args = cp.build_parser().parse_args(pack_argv)
    result = cp.build(pack_args)
    meta, compile_exit = cp.emit(result, pack_args)

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "task_id": args.task,
        "role": args.role,
        "provider": args.provider,
        "compile": {
            "exit": compile_exit,
            "sufficient": meta["sufficiency"]["sufficient"],
            "sufficiency_reason": meta["sufficiency"]["reason"],
            "overflow": meta["overflow"]["resolved"],
            "context_md_bytes": meta["actuals"]["context_md_bytes"],
            "estimated_tokens": meta["actuals"]["estimated_tokens"],
            "repo_sha": meta["repo_sha"],
            "out": "context.md + context.meta.json + evidence/ in --out",
        },
        "routing": {"requested": bool(args.route), "status": "not_requested"},
        "supervisor_boundary": (
            "automatic controller/supervisor consumption remains OWNER-GATED: "
            "wiring it requires changes to protected tools/agent_supervisor/** "
            "which D-018 prohibits; this manifest + packet are the canonical "
            "non-protected handoff (D-018-R026)"),
    }

    exit_code = compile_exit
    if args.route:
        signals, notes = derive_signals(meta, compile_exit)
        manifest["routing"]["signals"] = dataclasses.asdict(signals)
        manifest["routing"]["signal_notes"] = notes
        if not args.model_config:
            manifest["routing"]["status"] = "config_path_required"
            exit_code = exit_code or 2
        else:
            try:
                permitted = mr.load_permitted_models(args.model_config)
                decision = mr.route(
                    args.task, args.provider, signals, permitted,
                    role=args.role,
                    estimated_context_tokens=signals.estimated_context_tokens)
                dp = pathlib.Path(args.decisions_path) if args.decisions_path \
                    else mr.decisions_path(pathlib.Path(args.repo).resolve())
                ric.rotate_jsonl_if_needed(dp)  # bounded retention (R036)
                mr.append_decision(decision, dp)
                manifest["routing"]["status"] = "recorded"
                manifest["routing"]["decision"] = decision
                manifest["routing"]["recorded_to"] = "external runtime "\
                    "model_routing.jsonl (accepted convention; rotated)"
            except (mr.RoutingError, OSError, ImportError) as exc:
                manifest["routing"]["status"] = "routing_unavailable"
                manifest["routing"]["reason"] = f"{type(exc).__name__}: {exc}"
                exit_code = exit_code or 2

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dispatch_manifest.json").write_bytes(canon_json_bytes(manifest))
    _emit({"task_id": args.task, "compile_exit": compile_exit,
           "sufficient": meta["sufficiency"]["sufficient"],
           "routing_status": manifest["routing"]["status"],
           "manifest": "dispatch_manifest.json"})
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
