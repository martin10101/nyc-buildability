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
import os
import re
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import context_pack as cp  # noqa: E402
from tools import model_routing as mr  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools.context_pack_io import canon_json_bytes, load_json, run_git  # noqa: E402

MANIFEST_SCHEMA = "context_dispatch_manifest/v1"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _git_head(repo: str) -> str:
    rc, out = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if rc == 0 else "UNKNOWN"


def _git_dirty(repo: str) -> bool:
    rc, out = run_git(repo, ["status", "--porcelain"])
    return rc != 0 or bool(out.strip())


def _rev_resolvable(repo: str, ref: str) -> str | None:
    """The resolved 40-hex commit for `ref`, or None if git can't resolve it."""
    rc, out = run_git(repo, ["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
    sha = out.strip()
    return sha if rc == 0 and _SHA40.match(sha) else None


def _frozen_g0_sha(repo: str, task_id: str) -> str | None:
    """The task's frozen G0 reviewed head SHA, read from its recorded G0 gate."""
    gate = load_json(os.path.join(repo, "project-control", "gates",
                                  f"{task_id}-G0.json"))
    if isinstance(gate, dict):
        sha = str(gate.get("sha") or gate.get("reviewed_sha") or "").strip()
        if _SHA40.match(sha):
            return sha
    return None


def resolve_diff_base(repo: str, task_id: str, role: str,
                      explicit: str | None) -> tuple[str | None, dict]:
    """Resolve the diff base for a worker/reviewer packet WITHOUT silently using
    HEAD (M0-T076 / D-019-R026/R027).

    Precedence: an explicit trusted `--diff-base` wins; otherwise the task's
    frozen G0 reviewed SHA is used; if neither is available the caller is REFUSED
    (must pass an explicit trusted base) rather than defaulting to HEAD. Returns
    (base_or_None, provenance)."""
    head = _git_head(repo)
    dirty = _git_dirty(repo)
    prov = {"role": role, "head_sha": head, "dirty": dirty,
            "chosen_base_sha": None, "resolution": None, "diff_command": None,
            "error": None}
    if explicit is not None:
        resolved = _rev_resolvable(repo, explicit)
        if resolved is None:
            prov["resolution"] = "explicit_unresolvable"
            prov["error"] = ("explicit --diff-base could not be resolved to a "
                             "commit in this repository")
            return None, prov
        prov.update(chosen_base_sha=resolved, resolution="explicit_trusted_diff_base",
                    diff_command=f"git diff {resolved}")
        return resolved, prov
    frozen = _frozen_g0_sha(repo, task_id)
    if frozen and _rev_resolvable(repo, frozen):
        prov.update(chosen_base_sha=frozen, resolution="frozen_g0_gate_sha",
                    diff_command=f"git diff {frozen}")
        return frozen, prov
    prov["resolution"] = "unresolved_require_explicit"
    prov["error"] = (
        "no frozen G0 base is available for this task and no explicit trusted "
        "--diff-base was given; refusing to silently diff against HEAD (a "
        "committed reviewer packet would see no change). Pass --diff-base <sha>.")
    return None, prov

#: Deterministic prefix rules for packet-derived risk flags (R023).
_CONTROL_PLANE_PREFIXES = ("project-control/", ".github/", ".claude/")
_SECURITY_PREFIXES = ("tools/agent_supervisor/", ".github/workflows/")
_SCHEMA_PREFIXES = ("packages/contracts/", "supabase/")


def derive_signals(meta: dict, compile_exit: int
                   ) -> tuple["mr.Signals", list[str], dict]:
    """model_routing.Signals FROM the compiled evidence (D-018-R023/R024;
    M0-T076 / D-019-R032/R033).

    Returns (signals, notes, provenance). EVERY field is either derived from
    authoritative structured compiled evidence (paths/counts/graph) or marked
    UNDETERMINED — and an undetermined RISK-BEARING signal raises
    ambiguity_or_missing_evidence so the band can only go UP on unknown-ness,
    never a silent False. A concurrency/security/schema/destructive/external/
    protected-config impact that cannot be structurally proven ABSENT is never
    reported as a confident False (D-019-R032). `provenance` records the value
    AND basis of every field."""
    notes: list[str] = []
    prov_sig: dict[str, dict] = {}
    integ = meta.get("integration") or {}
    prov = meta.get("provenance") or {}
    suff = meta.get("sufficiency") or {}
    task_paths = list((integ.get("implementation_paths") or []))
    changed_targets = int(prov.get("changed_targets") or 0)
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

    # A task with NO code in scope (pure docs/control-plane) lets us AFFIRM the
    # absence of runtime-behavioral impact from structured evidence; a task that
    # touches code cannot have those impacts proven absent from paths alone.
    code_in_scope = bool(task_paths) or changed_targets > 0

    def _structured_flag(name: str, prefixes: tuple[str, ...]) -> bool:
        val = _flag(prefixes)
        prov_sig[name] = {"value": val,
                          "basis": "structured_paths:" + ",".join(prefixes)}
        return val

    def _risk_or_undetermined(name: str) -> bool:
        """A behavioral risk signal we cannot compute structurally. Affirmed
        False only when there is NO code in scope; otherwise UNDETERMINED ->
        raise ambiguity (never a confident silent False, D-019-R032)."""
        nonlocal ambiguity
        if not code_in_scope:
            prov_sig[name] = {"value": False, "basis": "structured:no_code_scope"}
            return False
        prov_sig[name] = {"value": False, "basis": "undetermined_no_structured_basis",
                          "undetermined": True}
        ambiguity = True
        notes.append(f"{name} undetermined from compiled evidence -> ambiguity raised")
        return False

    security = _structured_flag("security_or_authorization_impact", _SECURITY_PREFIXES)
    control_plane = _structured_flag("control_plane_change", _CONTROL_PLANE_PREFIXES)
    schema = _structured_flag("schema_or_migration_impact", _SCHEMA_PREFIXES)
    protected_cfg = any("config.toml" in p or "model_selection" in p for p in all_scope)
    prov_sig["protected_configuration_impact"] = {
        "value": protected_cfg, "basis": "structured_paths:config.toml,model_selection"}
    legal = any(p.startswith(("services/api/app/", "packages/contracts/"))
                for p in task_paths)
    prov_sig["legal_or_numeric_correctness"] = {
        "value": legal, "basis": "structured_paths:services/api/app,packages/contracts"}
    prov_sig["files_affected"] = {"value": changed_targets or len(task_paths),
                                  "basis": "structured_counts"}
    prov_sig["subsystems_affected"] = {"value": int(integ.get("subsystems_touched") or 0),
                                       "basis": "structured_counts"}
    prov_sig["dependency_graph_spread"] = {"value": int(prov.get("dependency_breadth") or 0),
                                           "basis": "structured_graph"}

    destructive = _risk_or_undetermined("destructive_operations")
    external = _risk_or_undetermined("external_side_effects")
    concurrency = _risk_or_undetermined("concurrency_or_performance")
    prov_sig["ambiguity_or_missing_evidence"] = {"value": ambiguity,
                                                 "basis": "derived"}

    signals = mr.Signals(
        files_affected=changed_targets or len(task_paths),
        subsystems_affected=int(integ.get("subsystems_touched") or 0),
        dependency_graph_spread=int(prov.get("dependency_breadth") or 0),
        security_or_authorization_impact=security,
        protected_configuration_impact=protected_cfg,
        destructive_operations=destructive,
        control_plane_change=control_plane,
        legal_or_numeric_correctness=legal,
        external_side_effects=external,
        schema_or_migration_impact=schema,
        concurrency_or_performance=concurrency,
        ambiguity_or_missing_evidence=ambiguity,
        prior_failed_attempts=0,
        required_reviewer_roles=(),
        estimated_context_tokens=(meta.get("actuals") or {}).get("estimated_tokens"),
        packet_risk_classification=None,
    )
    return signals, notes, prov_sig


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
    # Default is the SENTINEL None: the orchestrator resolves the task's frozen
    # G0 base rather than silently diffing against HEAD (M0-T076, D-019-R026).
    # An explicit value (even "HEAD") is treated as a trusted operator override.
    p.add_argument("--diff-base", default=None, dest="diff_base")
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

    # Resolve the diff base BEFORE compiling: a worker/reviewer packet must diff
    # against the task's frozen G0 base (or an explicit trusted base), never a
    # silent HEAD that would hide committed work (M0-T076, D-019-R026/R027).
    repo_abs = str(pathlib.Path(args.repo).resolve())
    diff_base, diff_prov = resolve_diff_base(repo_abs, args.task, args.role,
                                             args.diff_base)
    if diff_base is None:
        manifest = {"schema": MANIFEST_SCHEMA, "task_id": args.task,
                    "role": args.role, "provider": args.provider,
                    "diff_base_resolution": diff_prov,
                    "compile": {"exit": 3, "sufficient": False,
                                "sufficiency_reason": diff_prov["error"]},
                    "routing": {"requested": bool(args.route),
                                "status": "not_attempted_unresolved_diff_base"}}
        out_dir = pathlib.Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "dispatch_manifest.json").write_bytes(canon_json_bytes(manifest))
        _emit({"task_id": args.task, "compile_exit": 3, "sufficient": False,
               "routing_status": manifest["routing"]["status"],
               "diff_base_error": diff_prov["error"],
               "manifest": "dispatch_manifest.json"})
        return 3

    # THE integrated compiler — same parser, same build/emit, one packet.
    pack_argv = ["--task", args.task, "--role", args.role,
                 "--provider", args.provider, "--max-bytes", str(args.max_bytes),
                 "--out", args.out, "--repo", args.repo,
                 "--diff-base", diff_base]
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
        "diff_base_resolution": diff_prov,
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
        signals, notes, signal_prov = derive_signals(meta, compile_exit)
        manifest["routing"]["signals"] = dataclasses.asdict(signals)
        manifest["routing"]["signal_notes"] = notes
        manifest["routing"]["signal_provenance"] = signal_prov
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
