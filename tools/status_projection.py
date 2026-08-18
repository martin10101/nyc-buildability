#!/usr/bin/env python3
"""Deterministic initiative status projection (M0-T069 Unit F, D-013-R061..R063).

Generated ONLY from authoritative facts — the D-013 verification registry
(which defines the unit-task set), task packets, gate records, submission
records, the state file, and git — never a hand-maintained graph (R061).

R062 status mapping (existing control-plane semantics → compact view):
  backlog → planned; ready → ready; claimed/in_progress → in progress;
  awaiting_gate → awaiting independent review; rework → corrections required;
  submitted-with-gates-open → gates pending; accepted → accepted;
  blocked → blocked; superseded → superseded.

Each unit node carries the R063 fields: task id + exact applicable
requirement ids (from the independent verification), dependency ids, roles
(producer/reviewers), branch + current reviewed SHA, implementation files,
evidence location, the latest independent-review report digest (this
repository's review mechanism; the honest mapping of the 'latest decision
digest' field), required gates with state, accepted/blocked reason, and the
rollback point (the G0 contract commit — the pre-implementation checkpoint).
Values a record does not carry are null, never fabricated (R051).

The projection declares the repository SHA, branch, and the Unit C
task/directive index digests it was generated from; `check` exits 3 when the
current HEAD differs from the generating SHA (stale-marking, R063). The
Markdown and Mermaid renderings are produced FROM the same JSON document
(views, never sources of truth — R062). Two runs at identical repository
state are byte-identical. Unreadable inputs fail closed (R013).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.context_pack_io import canon_json_bytes  # noqa: E402
from tools.subsystem_entities import AuthoritativeIndexes, EntityIndexError  # noqa: E402

PROJECTION_SCHEMA = "d013_status_projection/v1"

_STATUS_MAP = {
    # ACTUAL project_control.py lifecycle statuses -> the directive's compact
    # meanings (M0-T075, D-018-R049). self_check = producer self-check done,
    # independent gates still outstanding; canceled maps to the compact
    # "superseded" meaning (the id is retired without acceptance).
    "backlog": "planned",
    "ready": "ready",
    "claimed": "in progress",
    "in_progress": "in progress",
    "self_check": "gates pending",
    "awaiting_gate": "awaiting independent review",
    "rework": "corrections required",
    "blocked": "blocked",
    "accepted": "accepted",
    "canceled": "superseded",
    "superseded": "superseded",
}


class ProjectionError(Exception):
    """Fail-closed projection error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


_INPUTS: list[tuple[str, str]] | None = None


def _record_input(rel: str, data: bytes) -> None:
    if _INPUTS is not None:
        _INPUTS.append((rel, hashlib.sha256(data).hexdigest()))


def _read_json(path: pathlib.Path, code: str) -> dict:
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ProjectionError(code, f"{path.name}: {type(exc).__name__}") from exc
    _record_input(path.name, data)
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectionError(code, f"{path.name}: {type(exc).__name__}") from exc


def _git(repo_root: str, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=repo_root, check=True,
                             capture_output=True, text=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ProjectionError("git_unavailable", f"git {args[0]}: {exc}") from exc


def _sha256_file(path: pathlib.Path) -> str | None:
    try:
        return hashlib.sha256(
            path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return None


def _gates(repo_root: pathlib.Path, task_id: str) -> list[dict]:
    rows = []
    for gp in sorted((repo_root / "project-control" / "gates").glob(f"{task_id}-G*.json")):
        doc = _read_json(gp, "gate_record_unreadable")
        rows.append({"gate_id": doc.get("gate_id"), "result": doc.get("result"),
                     "reviewer": doc.get("reviewer"),
                     "reviewed_sha": doc.get("reviewed_sha")})
    return rows


def _review_digest(repo_root: pathlib.Path, task_id: str) -> dict:
    """Digest of the LATEST independent-review report (honest mapping of the
    'latest decision digest' field for this repository's review mechanism)."""
    candidates = sorted((repo_root / "project-control" / "reports").glob(
        f"{task_id}-review-*.md"))
    if not candidates:
        return {"report": None, "sha256": None,
                "note": "no independent-review report on file"}
    latest = candidates[-1]  # deterministic: lexicographic; PASS rounds sort last
    digest = _sha256_file(latest)
    if digest:
        _record_input(latest.name, digest.encode())
    return {"report": f"project-control/reports/{latest.name}",
            "sha256": digest}


def _node(repo_root: pathlib.Path, task_id: str, verification_entry: dict) -> dict:
    packet = _read_json(repo_root / "project-control" / "tasks" / f"{task_id}.json",
                        "task_packet_unreadable")
    gates = _gates(repo_root, task_id)
    g0 = next((g for g in gates if g["gate_id"] == "G0"), None)
    latest_reviewed = next(
        (g["reviewed_sha"] for g in reversed(gates) if g.get("reviewed_sha")), None)
    submit = repo_root / "project-control" / "reports" / f"{task_id}.json"
    submit_doc = _read_json(submit, "submission_record_unreadable") \
        if submit.is_file() else {}
    status = packet.get("status")
    impl_files = [p for p in packet.get("allowed_paths") or []
                  if not p.startswith("project-control/")]
    return {
        "task_id": task_id,
        "title": packet.get("title"),
        "requirement_ids": verification_entry.get("applicable_requirement_ids") or [],
        "dependency_ids": packet.get("dependencies") or [],
        "roles": {"producer": packet.get("producer_agent"),
                  "reviewers": packet.get("reviewer_agents") or []},
        "branch": None,  # not recorded in the control plane after merge (null, R051)
        "reviewed_sha": (verification_entry.get("reviewed_sha")
                         or submit_doc.get("reviewed_sha") or latest_reviewed),
        "implementation_files": impl_files,
        "evidence_location": f"project-control/reports/{task_id}-*",
        "review_decision_digest": _review_digest(repo_root, task_id),
        "required_gates": packet.get("required_gates") or [],
        "gates": gates,
        "control_plane_status": status,
        "status": _STATUS_MAP.get(str(status), f"unknown:{status}"),
        "accepted_or_blocked_reason": (
            f"accepted by {packet.get('accepted_by')} at {packet.get('accepted_at')}"
            if status == "accepted" else
            (packet.get("blockers") or None) if status == "blocked" else None),
        "rollback_point": (g0 or {}).get("reviewed_sha"),
    }


def build_projection(repo_root: str) -> dict:
    global _INPUTS
    root = pathlib.Path(repo_root).resolve()
    _INPUTS = []
    try:
        return _build_projection_collected(root)
    finally:
        _INPUTS = None


def _build_projection_collected(root: pathlib.Path) -> dict:
    verification = _read_json(
        root / "project-control" / "directives"
        / "D-013-context-intelligence-pipeline" / "verification.json",
        "verification_registry_unreadable")
    # The unit-task set comes from the directive's own verification registry —
    # authoritative, never a hand-maintained list (R061).
    entries = {t["task_id"]: t for t in verification.get("task_verifications", [])}
    try:
        digests = AuthoritativeIndexes.load(str(root)).digests()
    except EntityIndexError as exc:
        raise ProjectionError(exc.code, exc.detail) from exc
    nodes = [_node(root, tid, entries[tid]) for tid in sorted(entries)]
    # Deterministic INPUT-MANIFEST digest (M0-T075, D-018-R048): every material
    # input that can change this projection — task packets (all, via the task
    # index digest), the verification registry, gate records, submission
    # records, review reports, task/directive indexes, and the Git identity —
    # is hashed; the check subcommand recomputes and compares, so an
    # UNCOMMITTED control-plane edit marks the projection stale (HEAD alone
    # cannot).
    manifest_rows = sorted(set(_INPUTS or []))
    manifest_rows.append(("git:HEAD", _git(str(root), "rev-parse", "HEAD")))
    manifest_rows.append(("index:tasks", digests["task_index_digest"]))
    manifest_rows.append(("index:directives", digests["directive_index_digest"]))
    input_manifest_digest = hashlib.sha256(
        ";".join(f"{name}|{dig}" for name, dig in manifest_rows).encode()
    ).hexdigest()
    return {
        "schema": PROJECTION_SCHEMA,
        "projection_kind": "generated_current",
        "generated_from": {
            "repo_sha": _git(str(root), "rev-parse", "HEAD"),
            "branch": _git(str(root), "rev-parse", "--abbrev-ref", "HEAD"),
            "task_index_digest": digests["task_index_digest"],
            "directive_index_digest": digests["directive_index_digest"],
            "input_manifest_digest": input_manifest_digest,
            "input_manifest_entries": len(manifest_rows),
            "stale_when": ("ANY material input changes: the check subcommand "
                           "regenerates the projection live and compares the "
                           "deterministic input-manifest digest (task packets/"
                           "statuses, verification registry, gates, submission "
                           "records, review reports, task/directive indexes, "
                           "git HEAD); exit 3 = stale"),
        },
        "status_mapping": dict(_STATUS_MAP),
        "nodes": nodes,
    }


def render_md(projection: dict) -> str:
    gen = projection["generated_from"]
    lines = ["# D-013 context-intelligence status projection", "",
             "A VIEW generated deterministically from control-plane facts — "
             "never source of truth. Regenerate rather than edit.", "",
             f"- generated from: `{gen['repo_sha']}` on `{gen['branch']}`",
             f"- task index digest: `{gen['task_index_digest'][:16]}…`",
             f"- directive index digest: `{gen['directive_index_digest'][:16]}…`",
             f"- staleness: {gen['stale_when']}", "",
             "| unit task | status | reviewed SHA | gates | rollback point |",
             "|---|---|---|---|---|"]
    for n in projection["nodes"]:
        gates = ", ".join(f"{g['gate_id']}:{g['result']}" for g in n["gates"]) or "—"
        lines.append(
            f"| {n['task_id']} | {n['status']} | "
            f"`{(n['reviewed_sha'] or '—')[:9]}` | {gates} | "
            f"`{(n['rollback_point'] or '—')[:9]}` |")
    lines += ["", "```mermaid", "graph LR"]
    for n in projection["nodes"]:
        for dep in n["dependency_ids"]:
            lines.append(f"  {dep} --> {n['task_id']}")
    lines += ["```", "",
              "(The Mermaid graph above is rendered FROM the same JSON "
              "projection — a view, never a source of truth.)", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic D-013 status projection")
    ap.add_argument("--repo", default=str(_ROOT))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--out-json", default=None)
    p_gen.add_argument("--out-md", default=None)
    p_chk = sub.add_parser("check", help="exit 3 when a projection is stale")
    p_chk.add_argument("projection_json")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "generate":
            projection = build_projection(args.repo)
            payload = canon_json_bytes(projection)
            if args.out_json:
                pathlib.Path(args.out_json).write_bytes(payload)
            if args.out_md:
                pathlib.Path(args.out_md).write_text(
                    render_md(projection), encoding="utf-8", newline="\n")
            if not args.out_json and not args.out_md:
                sys.stdout.write(payload.decode("utf-8"))
            return 0
        if args.cmd == "check":
            doc = _read_json(pathlib.Path(args.projection_json),
                             "projection_unreadable")
            gen = doc.get("generated_from") or {}
            recorded_sha = gen.get("repo_sha")
            recorded_manifest = gen.get("input_manifest_digest")
            kind = doc.get("projection_kind") or "committed_or_historical_snapshot"
            live = build_projection(args.repo)
            live_gen = live["generated_from"]
            stale = (recorded_sha != live_gen["repo_sha"]
                     or recorded_manifest != live_gen["input_manifest_digest"])
            out_doc = {
                "stale": stale,
                "checked_projection_kind": kind,
                "note": ("a file on disk is a COMMITTED/HISTORICAL SNAPSHOT of "
                         "the moment it was generated; regenerate for the "
                         "current projection (D-018-R050)"),
                "recorded": {"repo_sha": recorded_sha,
                             "input_manifest_digest": recorded_manifest},
                "current": {"repo_sha": live_gen["repo_sha"],
                            "input_manifest_digest": live_gen["input_manifest_digest"]},
            }
            sys.stdout.write(canon_json_bytes(out_doc).decode("utf-8"))
            return 3 if stale else 0
    except ProjectionError as exc:
        sys.stdout.write(canon_json_bytes(exc.doc()).decode("utf-8"))
        return 2
    return 2  # pragma: no cover — argparse enforces the subcommand set


if __name__ == "__main__":
    raise SystemExit(main())
