#!/usr/bin/env python3
"""Promotion benchmark for the context-intelligence pipeline (M0-T069 Unit F).

Correctness first, efficiency second (D-013-R054). The frozen corpus is a
DETERMINISTIC fixture generator covering the five directive-named task shapes:
single-file bug, cross-module change, frontend/backend boundary, schema
change, and control-plane-only. For every shape and change class the
REFERENCE is a clean full rebuild by the unmodified builder (a fresh-cache
`build_incremental` cold run degenerates to exactly that builder — the same
generator the accepted A1 baseline froze), and the NEW path is the warm
incremental build over the SAME snapshot at the SAME SHA — which removes the
implementation-SHA confound (R056 method): both sides execute the identical
accepted code over identical bytes; only the cache state differs.

Verdicts compare the EXPORT BYTES (strongest form of the R059 byte-identity
guarantee), plus: warm no-change must reparse zero files; a local change must
NOT trigger a full rebuild unless a documented global invalidator changed
(config/schema); delete/rename must leave no stale nodes; corrupt-cache and
orphaned-temp (interrupted write) recovery must preserve validity; a held
lock must refuse (`concurrent_writer`) without corruption.

Honest reporting (R057/R012/R053): timings are wall-clock MEASUREMENTS with
recorded sample counts and median/p95, in a section labeled measured_runtime;
deterministic reuse metrics are separate; provider token savings are labeled
UNMEASURED; no combined savings number exists. Thresholds are PROPOSED with
rationale and the promotion decision is PENDING the owner/control-plane
decision (R060) — this module changes no behavior flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_index_baseline as rib  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools import repo_index_incremental as inc  # noqa: E402
from tools.context_pack_io import canon_json_bytes  # noqa: E402

BENCHMARK_SCHEMA = "context_benchmark/v1"

METHOD_STATEMENT = (
    "Reference = clean full rebuild by the unmodified builder (fresh-cache "
    "cold build; identical to the A1-frozen generator). New = warm "
    "incremental build over the SAME snapshot at the SAME implementation "
    "SHA. Both sides run identical accepted code over identical bytes; only "
    "cache state differs, so the implementation-SHA confound is removed "
    "(D-013-R056). Verdicts compare raw export bytes.")

_GIT_ENV = {"GIT_AUTHOR_NAME": "B", "GIT_AUTHOR_EMAIL": "b@b.b",
            "GIT_COMMITTER_NAME": "B", "GIT_COMMITTER_EMAIL": "b@b.b",
            "GIT_CONFIG_NOSYSTEM": "1"}


def _write(root: str, rel: str, content: str) -> None:
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(content.encode("utf-8"))


def _git(root: str, *args: str) -> None:
    env = dict(os.environ)
    env.update(_GIT_ENV)
    subprocess.run(["git", *args], cwd=root, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---- the frozen corpus: five deterministic task shapes (R054) ----------------

def _shape_single_file_bug(root: str) -> dict:
    _write(root, "services/api/calc.py", "def add(a, b):\n    return a - b\n")
    _write(root, "services/api/other.py", "def noop():\n    return None\n")
    return {"change_file": "services/api/calc.py",
            "change_content": "def add(a, b):\n    return a + b\n",
            "dependency_file": None}


def _shape_cross_module(root: str) -> dict:
    _write(root, "services/api/core.py", "VALUE = 1\n")
    _write(root, "services/api/user.py",
           "from services.api.core import VALUE\n\ndef get():\n    return VALUE\n")
    return {"change_file": "services/api/user.py",
            "change_content": "from services.api.core import VALUE\n\n"
                              "def get():\n    return VALUE + 1\n",
            "dependency_file": "services/api/core.py"}


def _shape_frontend_backend(root: str) -> dict:
    _write(root, "services/api/api.py", "def endpoint():\n    return {}\n")
    _write(root, "apps/web/src/lib/api.ts",
           "export function callApi(): number { return 1; }\n")
    _write(root, "apps/web/src/page.ts",
           "import { callApi } from './lib/api';\nexport const x = callApi();\n")
    return {"change_file": "apps/web/src/lib/api.ts",
            "change_content": "export function callApi(): number { return 2; }\n",
            "dependency_file": None,
            "config_file": "apps/web/tsconfig.json",
            "config_content": '{"compilerOptions": {"paths": {"@/*": ["./src/*"]}}}\n'}


def _shape_schema_change(root: str) -> dict:
    _write(root, "packages/contracts/schemas/thing.schema.json",
           '{"$id": "thing.schema.json", "type": "object"}\n')
    _write(root, "services/api/uses_schema.py",
           "# reads thing.schema.json\ndef load():\n    return None\n")
    return {"change_file": "packages/contracts/schemas/thing.schema.json",
            "change_content": '{"$id": "thing.schema.json", "type": "object", '
                              '"title": "Thing"}\n',
            "dependency_file": None}


def _shape_control_plane_only(root: str) -> dict:
    _write(root, "services/api/stable.py", "def stable():\n    return 0\n")
    _write(root, "project-control/tasks/M0-T900.json",
           '{"task_id": "M0-T900", "status": "backlog"}\n')
    return {"change_file": "project-control/tasks/M0-T900.json",
            "change_content": '{"task_id": "M0-T900", "status": "ready"}\n',
            "dependency_file": None, "non_eligible_change": True}


SHAPES = {
    "single_file_bug": _shape_single_file_bug,
    "cross_module_change": _shape_cross_module,
    "frontend_backend_boundary": _shape_frontend_backend,
    "schema_change": _shape_schema_change,
    "control_plane_only": _shape_control_plane_only,
}


def build_corpus_shape(name: str, root: str) -> dict:
    meta = SHAPES[name](root)
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "corpus baseline")
    return meta


def corpus_manifest_digest(root: str) -> str:
    """Deterministic digest of the corpus snapshot (sorted path+content)."""
    h = hashlib.sha256()
    base = pathlib.Path(root)
    for p in sorted(q for q in base.rglob("*") if q.is_file()
                    and ".git" not in q.parts):
        h.update(str(p.relative_to(base)).replace("\\", "/").encode())
        h.update(b"\0")
        h.update(p.read_bytes().replace(b"\r\n", b"\n"))
        h.update(b"\n")
    return h.hexdigest()


# ---- reference vs new ---------------------------------------------------------

def _reference_full(root: str) -> bytes:
    """Clean full rebuild: fresh empty cache -> the unmodified builder runs."""
    with tempfile.TemporaryDirectory() as fresh:
        return inc.build_incremental(root, cache_base=fresh,
                                     persist_telemetry=False).export_bytes


def _case(shape: str, case: str, res, ref_bytes: bytes, **extra) -> dict:
    row = {"shape": shape, "case": case,
           "byte_identical": res.export_bytes == ref_bytes,
           "mode": res.mode, "rebuild_reason": res.rebuild_reason,
           "files_parsed": res.files_parsed, "files_reused": res.files_reused}
    row.update(extra)
    return row


def run_shape(name: str, *, samples: int = 1) -> dict:
    """All change classes for one corpus shape. Returns rows + evidence."""
    rows: list[dict] = []
    timings: dict[str, list[float]] = {"reference_full": [], "warm_no_change": []}
    with tempfile.TemporaryDirectory() as root, \
         tempfile.TemporaryDirectory() as cache:
        meta = build_corpus_shape(name, root)
        manifest = corpus_manifest_digest(root)
        baseline = rib.capture_baseline(root)  # A1 reference provenance

        # cold (full) --------------------------------------------------------
        t0 = time.perf_counter()
        ref = _reference_full(root)
        timings["reference_full"].append(time.perf_counter() - t0)
        cold = inc.build_incremental(root, cache_base=cache,
                                     persist_telemetry=False)
        rows.append(_case(name, "cold_build", cold, ref))

        # warm no-change: zero reparse (R059) --------------------------------
        warm = cold
        for _ in range(max(samples, 1)):
            t0 = time.perf_counter()
            warm = inc.build_incremental(root, cache_base=cache,
                                         persist_telemetry=False)
            timings["warm_no_change"].append(time.perf_counter() - t0)
        rows.append(_case(name, "warm_no_change", warm, ref,
                          zero_reparse=warm.files_parsed == 0))

        # one-file change (or control-plane-only non-eligible change) --------
        _write(root, meta["change_file"], meta["change_content"])
        ref2 = _reference_full(root)
        changed = inc.build_incremental(root, cache_base=cache,
                                        persist_telemetry=False)
        if meta.get("non_eligible_change"):
            # A control-plane edit is NOT an eligible-source change: the
            # snapshot fingerprint (which covers uncommitted tree state)
            # moves, the eligible change set is empty, and the accepted A2
            # path conservatively rebuilds full with its documented fallback
            # reason. Correctness (byte-identity) is what R059 demands here;
            # the incremental-contract clause applies to SOURCE changes.
            rows.append(_case(
                name, "non_eligible_change", changed, ref2,
                conservative_full_rebuild_on_non_source_change=(
                    changed.mode == "full"),
                documented_fallback_reason=changed.rebuild_reason or None))
        else:
            is_invalidator = name in ("frontend_backend_boundary",
                                      "schema_change") and changed.mode == "full"
            rows.append(_case(
                name, "one_file_change", changed, ref2,
                no_full_rebuild=changed.mode != "full" or is_invalidator,
                documented_invalidator=(changed.rebuild_reason
                                        if changed.mode == "full" else None)))

        # dependency change --------------------------------------------------
        if meta.get("dependency_file"):
            _write(root, meta["dependency_file"], "VALUE = 2\n")
            ref3 = _reference_full(root)
            dep = inc.build_incremental(root, cache_base=cache,
                                        persist_telemetry=False)
            rows.append(_case(name, "dependency_change", dep, ref3,
                              no_full_rebuild=dep.mode != "full"))

        # config change (frontend shape): documented global invalidator ------
        if meta.get("config_file"):
            _write(root, meta["config_file"], meta["config_content"])
            ref4 = _reference_full(root)
            cfg = inc.build_incremental(root, cache_base=cache,
                                        persist_telemetry=False)
            rows.append(_case(name, "config_change", cfg, ref4,
                              documented_invalidator=cfg.rebuild_reason))

        # delete + rename: no stale nodes (R059) -----------------------------
        victim = meta["change_file"] if not meta.get("non_eligible_change") \
            else "services/api/stable.py"
        renamed = victim.rsplit(".", 1)[0] + "_renamed." + victim.rsplit(".", 1)[1]
        os.replace(os.path.join(root, *victim.split("/")),
                   os.path.join(root, *renamed.split("/")))
        ref5 = _reference_full(root)
        ren = inc.build_incremental(root, cache_base=cache,
                                    persist_telemetry=False)
        ren_ids = {n["id"] for n in json.loads(ren.export_bytes.decode())["nodes"]}
        rows.append(_case(name, "rename", ren, ref5,
                          stale_nodes=victim in ren_ids))
        os.remove(os.path.join(root, *renamed.split("/")))
        ref6 = _reference_full(root)
        dele = inc.build_incremental(root, cache_base=cache,
                                     persist_telemetry=False)
        gone = renamed not in {n["id"] for n in
                               json.loads(dele.export_bytes.decode())["nodes"]}
        rows.append(_case(name, "delete", dele, ref6, stale_nodes=not gone))

        # corrupt cache: recovery preserves validity + parity ----------------
        store = ric.IndexCache(root, base=cache)
        cur = store.load_current()
        if cur is not None:
            (cur.path / "payload.json").write_text("{corrupt", encoding="utf-8")
        corrupt = inc.build_incremental(root, cache_base=cache,
                                        persist_telemetry=False)
        rows.append(_case(name, "corrupt_cache_recovery", corrupt, ref6))

        # interrupted write: orphan temp generation is quarantined -----------
        orphan = store.tmp_dir / "deadfingerprint.999999"
        orphan.mkdir(parents=True, exist_ok=True)
        (orphan / "payload.json").write_text("{half", encoding="utf-8")
        interrupted = inc.build_incremental(root, cache_base=cache,
                                            persist_telemetry=False)
        rows.append(_case(name, "interrupted_write_recovery", interrupted, ref6,
                          orphan_quarantined=not orphan.exists()))

        # concurrent writer: held lock refuses, store stays valid ------------
        lock = ric.SingleWriterLock(store.root)
        lock.acquire()
        try:
            _write(root, "services/api/late.py", "def late():\n    return 9\n")
            try:
                inc.build_incremental(root, cache_base=cache,
                                      persist_telemetry=False)
                refused = False
            except ric.CacheError as exc:
                refused = exc.code == "concurrent_writer"
        finally:
            lock.release()
        after = inc.build_incremental(root, cache_base=cache,
                                      persist_telemetry=False)
        rows.append(_case(name, "concurrent_writer", after,
                          _reference_full(root), lock_refused=refused))

        # DISTINCT parser-version case (M0-T075, D-018-R043): bump a parser-
        # class config version over the SAME snapshot — the REAL global-
        # invalidator path must force a documented full rebuild, byte-identical
        # to the clean reference.
        ref7 = _reference_full(root)
        inc.build_incremental(root, cache_base=cache, persist_telemetry=False,
                              extra_config_versions={"parser_probe": "1"})
        pv = inc.build_incremental(root, cache_base=cache, persist_telemetry=False,
                                   extra_config_versions={"parser_probe": "2"})
        rows.append(_case(
            name, "parser_version_change", pv, ref7,
            documented_invalidator=pv.rebuild_reason or None,
            parser_version_full_rebuild=(
                pv.mode == "full" and "parser_probe" in pv.rebuild_reason)))

    return {"shape": name, "corpus_manifest_digest": manifest,
            "baseline_export_digest": baseline.export_digest,
            "census_reconciles": bool(
                (cold.telemetry or {}).get("census", {}).get("reconciles")),
            "rows": rows, "timings_seconds": timings}


def _stats(values: list[float]) -> dict:
    if not values:
        return {"samples": 0, "median": None, "p95": None}
    ordered = sorted(values)
    # Nearest-rank p95 (M0-T075 correction, D-018-R045): ceil(0.95*n)-1. The
    # prior formula int(n*0.95)-1 returned the MEDIAN at small n (e.g. n=3),
    # understating the label.
    rank = max(math.ceil(0.95 * len(ordered)) - 1, 0)
    return {"samples": len(values),
            "median": round(statistics.median(ordered), 4),
            "p95": round(ordered[rank], 4)}


def build_report(*, samples: int = 1) -> dict:
    shapes = [run_shape(name, samples=samples) for name in SHAPES]
    all_rows = [r for s in shapes for r in s["rows"]]
    evidence = {
        "census_accounts_every_eligible_file": all(
            s["census_reconciles"] for s in shapes),
        "incremental_matches_clean_full": all(r["byte_identical"] for r in all_rows),
        "warm_no_change_reparses_zero": all(
            r.get("zero_reparse", True) for r in all_rows
            if r["case"] == "warm_no_change"),
        "local_change_no_full_rebuild_without_documented_invalidator": all(
            r.get("no_full_rebuild", True) for r in all_rows
            if r["case"] == "one_file_change" or "no_full_rebuild" in r),
        "delete_rename_leave_no_stale_nodes": not any(
            r.get("stale_nodes") for r in all_rows),
        "corruption_crash_concurrency_preserve_validity": all(
            r["byte_identical"] for r in all_rows
            if r["case"] in ("corrupt_cache_recovery",
                             "interrupted_write_recovery", "concurrent_writer")),
    }
    # Actual refusal/quarantine behavior as PASS predicates (D-018-R044) and
    # the distinct parser-version case (R043): absence of a case FAILS.
    lock_rows = [r for r in all_rows if r["case"] == "concurrent_writer"]
    orphan_rows = [r for r in all_rows if r["case"] == "interrupted_write_recovery"]
    parser_rows = [r for r in all_rows if r["case"] == "parser_version_change"]
    evidence["lock_refusal_enforced"] = bool(lock_rows) and all(
        r.get("lock_refused") for r in lock_rows)
    evidence["orphan_temp_quarantined"] = bool(orphan_rows) and all(
        r.get("orphan_quarantined") for r in orphan_rows)
    evidence["parser_version_change_documented_full_rebuild"] = bool(
        parser_rows) and all(
        r.get("parser_version_full_rebuild") and r["byte_identical"]
        for r in parser_rows)
    timing_summary = {
        shape["shape"]: {k: _stats(v) for k, v in shape["timings_seconds"].items()}
        for shape in shapes}
    return {
        "schema": BENCHMARK_SCHEMA,
        "method": METHOD_STATEMENT,
        "correctness_first": True,
        "corpus": [{"shape": s["shape"],
                    "corpus_manifest_digest": s["corpus_manifest_digest"],
                    "baseline_export_digest": s["baseline_export_digest"]}
                   for s in shapes],
        "correctness": all_rows,
        "promotion_evidence_R059": evidence,
        "measured_runtime": {
            "label": ("measured wall-clock seconds; measurement evidence, "
                      "never byte-identity content"),
            "per_shape": timing_summary,
        },
        "efficiency": {
            "deterministic_reuse": {
                "warm_no_change_files_parsed": [
                    r["files_parsed"] for r in all_rows
                    if r["case"] == "warm_no_change"],
                "note": "deterministic packet/index reuse only (R057)",
            },
            "provider_token_savings": ("UNMEASURED — no provider-reported "
                                       "usage is available in this offline "
                                       "benchmark; a byte estimate is never "
                                       "presented as token savings "
                                       "(D-013-R012/R053/R057)"),
        },
        "threshold_proposal": {
            "proposed_before_owner_decision": True,
            "thresholds": [
                {"metric": "incremental_vs_full_byte_identity",
                 "threshold": "100% of benchmark cases",
                 "rationale": "correctness is absolute: any divergence means "
                              "the index lies about the source (R054/R059)"},
                {"metric": "warm_no_change_files_parsed",
                 "threshold": "0 files",
                 "rationale": "a no-change run that reparses anything defeats "
                              "the incremental contract (R059)"},
                {"metric": "recovery_validity",
                 "threshold": "100% of corruption/crash/concurrency cases "
                              "end with a valid generation",
                 "rationale": "fail-closed storage is a hard precondition for "
                              "trusting the cache (R036/R059)"},
            ],
        },
        "promotion_decision": ("PENDING owner/control-plane decision "
                               "(D-013-R060). This benchmark changes no "
                               "behavior flag; the pipeline remains exactly "
                               "as accepted by its unit gates."),
    }


# ==========================================================================
# END-TO-END compiler benchmark (M0-T075, D-018-R041/R042): the five shapes
# invoke the ACTUAL integrated compiler with the same task packet, diff base,
# role, provider/model, reasoning setting (none — recorded honestly), and
# source snapshot, cold + warm.
# ==========================================================================

E2E_SCHEMA = "context_benchmark_e2e/v1"
_E2E_MODEL = "claude-fable-5"

_REAL_MAP_PREFIXES = ("services/api", "apps/web", "packages/contracts",
                      "tools/code_graph", "tools/agent_supervisor", "tools",
                      "docs", "project-control", "supabase", ".github", ".claude")


def _e2e_control_plane(root: str, change_file: str, in_regime: bool) -> None:
    """Minimal authoritative control plane for the fixture task M0-T900."""
    packet = {"task_id": "M0-T900", "title": "E2E fixture task",
              "task_type": "infrastructure", "milestone_id": "M0",
              "status": "claimed", "allowed_paths": [change_file],
              "outputs": [f"deliver the corrected {change_file} behavior"]}
    if in_regime:
        packet["directive_refs"] = [{"directive_id": "D-900",
                                     "requirement_ids": "ALL"}]
        for prefix in _REAL_MAP_PREFIXES:  # let the REAL subsystem map load
            os.makedirs(os.path.join(root, *prefix.split("/")), exist_ok=True)
        d = os.path.join(root, "project-control", "directives")
        os.makedirs(os.path.join(d, "D-900-test"), exist_ok=True)
        _write(root, "project-control/directives/index.json", json.dumps(
            {"directives": [{"directive_id": "D-900", "status": "active",
                             "manifest": "D-900-test/manifest.json"}]}))
        _write(root, "project-control/directives/D-900-test/requirements.json",
               json.dumps({"requirements": [
                   {"id": "D-900-R001", "text": "the fixture change must keep "
                                                "the calculator correct",
                    "applicability": {"task_ids": ["M0-T900"], "task_types": [],
                                      "milestones": [], "paths": [],
                                      "lifecycle_events": [],
                                      "effective_date": "2026-01-01"},
                    "classification": "obligation", "binding": True}]}))
        _write(root, "project-control/directives/D-900-test/manifest.json",
               json.dumps({"directive_id": "D-900", "status": "active",
                           "slug": "test", "requirements_file": "requirements.json",
                           "verification_file": "verification.json", "sources": [],
                           "locked_requirement_ids": ["D-900-R001"]}))
        _write(root, "project-control/directives/D-900-test/verification.json",
               json.dumps({"task_verifications": []}))
    _write(root, "project-control/tasks/M0-T900.json", json.dumps(packet))
    _write(root, "project-control/state.json", json.dumps(
        {"project_status": "active", "accepted_tasks": [],
         "active_tasks": ["M0-T900"]}))
    _write(root, "CLAUDE.md", "# CLAUDE.md\n\n## On-demand routing\n\n"
                              "| a | b |\n|---|---|\n\n## Next\n")


def _e2e_compile(root: str, cache: str, out: str, *, role: str = "worker",
                 max_bytes: int = 400_000) -> tuple[dict, int]:
    from tools import context_pack as cp
    argv = ["--task", "M0-T900", "--role", role, "--provider", "claude",
            "--model", _E2E_MODEL, "--max-bytes", str(max_bytes), "--out", out,
            "--repo", root, "--index-cache-base", cache, "--no-index-telemetry"]
    args = cp.build_parser().parse_args(argv)
    result = cp.build(args)
    return cp.emit(result, args)


def _e2e_shape(name: str) -> dict:
    in_regime = name == "single_file_bug"
    with tempfile.TemporaryDirectory() as root, \
         tempfile.TemporaryDirectory() as cache:
        meta_fixture = SHAPES[name](root)
        _e2e_control_plane(root, meta_fixture["change_file"], in_regime)
        _git(root, "init", "-q")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "e2e baseline")
        _write(root, meta_fixture["change_file"], meta_fixture["change_content"])
        snapshot = corpus_manifest_digest(root)

        out_a = os.path.join(root, "out_a")
        out_b = os.path.join(root, "out_b")
        meta_a, exit_a = _e2e_compile(root, cache, out_a)   # cold
        _, exit_b = _e2e_compile(root, cache, out_b)        # warm
        md_a = open(os.path.join(out_a, "context.md"), "rb").read()
        md_b = open(os.path.join(out_b, "context.md"), "rb").read()
        mj_a = open(os.path.join(out_a, "context.meta.json"), "rb").read()
        mj_b = open(os.path.join(out_b, "context.meta.json"), "rb").read()

        integ = meta_a.get("integration") or {}
        groups = {f["group"] for f in meta_a.get("included_files") or []}
        row = {
            "shape": name, "in_regime": in_regime,
            "conditions": {"task": "M0-T900", "role": "worker",
                           "provider": "claude", "model": _E2E_MODEL,
                           "reasoning_setting": None,
                           "diff_base": "HEAD", "max_bytes": 400_000,
                           "snapshot_manifest_digest": snapshot},
            "exit_cold": exit_a, "exit_warm": exit_b,
            "cold_warm_byte_identical": md_a == md_b and mj_a == mj_b,
            "within_budget": bool((meta_a.get("actuals") or {}).get(
                "within_effective_bound")),
            "sufficient": meta_a["sufficiency"]["sufficient"],
            "provenance_complete": all(
                k in integ for k in ("requirements", "implementation_paths",
                                     "prose_extraction", "unresolved_seeds",
                                     "selection", "memory_status")),
            "source_excerpt_present": "source_excerpts" in groups,
            "code_evidence_required": bool(
                meta_a["sufficiency"].get("code_evidence_required")),
            "graph_or_source_evidence_resolved": bool(
                meta_a["sufficiency"].get("code_evidence_resolved")),
            "memory_status_honest": integ.get("memory_status") in (
                "store_empty", "no_digests_for_task", "ok", "store_unavailable"),
        }
        if in_regime:
            req = integ.get("requirements") or {}
            row["requirement_ids_present"] = req.get("applicable_ids") == ["D-900-R001"]
            row["requirements_group_present"] = "requirements" in groups

        # split refusal (nonzero) under a tiny budget — once, on the regime shape
        if in_regime:
            out_c = os.path.join(root, "out_c")
            _, exit_c = _e2e_compile(root, cache, out_c, max_bytes=500)
            row["tiny_budget_split_exit"] = exit_c
            # reviewer on a CLEAN tree: no diff -> enforceable insufficiency
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "apply change")
            out_d = os.path.join(root, "out_d")
            _, exit_d = _e2e_compile(root, cache, out_d, role="reviewer")
            row["reviewer_insufficiency_exit"] = exit_d
        return row


def build_e2e_report(baseline_path: str | None = None) -> dict:
    shapes = [_e2e_shape(name) for name in SHAPES]
    regime = [s for s in shapes if s["in_regime"]][0]
    checks = {
        "cold_warm_deterministic": all(s["cold_warm_byte_identical"] for s in shapes),
        "global_budget_or_split_refusal": (
            all(s["within_budget"] for s in shapes)
            and regime.get("tiny_budget_split_exit") == 2),
        "required_evidence_completeness": all(
            s["sufficient"] and s["exit_cold"] == 0 for s in shapes)
            and regime.get("reviewer_insufficiency_exit") == 3,
        "exact_provenance": all(s["provenance_complete"] for s in shapes),
        "graph_source_evidence_resolved": all(
            s["graph_or_source_evidence_resolved"] for s in shapes
            if s["code_evidence_required"]),
        "advisory_memory_handled": all(s["memory_status_honest"] for s in shapes),
        "requirement_texts_end_to_end": bool(
            regime.get("requirement_ids_present")
            and regime.get("requirements_group_present")),
    }
    report = {
        "schema": E2E_SCHEMA,
        "method": ("the ACTUAL integrated compiler (context_pack build/emit) "
                   "invoked per shape with the same task packet, diff base, "
                   "role, provider/model, reasoning setting (none recorded — "
                   "the compiler takes no reasoning argument), and source "
                   "snapshot, cold then warm"),
        "shapes": shapes,
        "checks": checks,
        "baseline_comparison": _baseline_comparison(baseline_path),
        "provider_token_savings": ("UNMEASURED — no provider-reported usage "
                                   "exists in this offline benchmark "
                                   "(D-013-R012/R057)"),
    }
    return report


def _baseline_comparison(baseline_path: str | None) -> dict:
    """Representative-task correctness vs the captured G0 baseline (R042):
    rerun the INTEGRATED compiler on the same real tasks and require every
    baseline-included source id to still be present with sufficiency true."""
    if not baseline_path or not os.path.isfile(baseline_path):
        return {"status": "baseline_not_provided"}
    from tools import context_pack as cp
    baseline = json.loads(open(baseline_path, encoding="utf-8").read())
    rows = []
    for run in baseline.get("compiler_runs", []):
        with tempfile.TemporaryDirectory() as out, \
             tempfile.TemporaryDirectory() as cache:
            argv = ["--task", run["task"], "--role", run["role"],
                    "--provider", run["provider"],
                    "--max-bytes", str(run["max_bytes"]), "--out", out,
                    "--index-cache-base", cache, "--no-index-telemetry"]
            args = cp.build_parser().parse_args(argv)
            meta, code = cp.emit(cp.build(args), args)
            now_ids = {f["source_id"] for f in meta["included_files"]}
            missing = sorted(set(run.get("included_source_ids") or []) - now_ids)
            rows.append({"task": run["task"], "exit": code,
                         "baseline_sources": len(run.get("included_source_ids") or []),
                         "integrated_sources": len(now_ids),
                         "baseline_sources_missing_now": missing,
                         "sufficient": meta["sufficiency"]["sufficient"],
                         "no_worse_than_baseline": not missing
                                                   and meta["sufficiency"]["sufficient"]
                                                   and code == 0})
    return {"status": "compared", "runs": rows,
            "no_worse_than_baseline": all(r["no_worse_than_baseline"] for r in rows)}


def render_e2e_md(report: dict) -> str:
    lines = ["# End-to-end compiler benchmark (M0-T075)", "",
             "## Method", "", report["method"], "", "## Checks", ""]
    for key, val in report["checks"].items():
        lines.append(f"- **{key}**: {'PASS' if val else 'FAIL'}")
    lines += ["", "## Shapes", "",
              "| shape | cold==warm | budget | sufficient | provenance | evidence |",
              "|---|---|---|---|---|---|"]
    for s in report["shapes"]:
        lines.append(
            f"| {s['shape']} | {s['cold_warm_byte_identical']} | "
            f"{s['within_budget']} | {s['sufficient']} | "
            f"{s['provenance_complete']} | "
            f"{s['graph_or_source_evidence_resolved']} |")
    bc = report["baseline_comparison"]
    lines += ["", "## Baseline comparison (G0, R042)", "",
              f"- status: {bc.get('status')}"]
    for r in bc.get("runs", []):
        lines.append(f"- {r['task']}: integrated {r['integrated_sources']} "
                     f"sources vs baseline {r['baseline_sources']}; missing "
                     f"{r['baseline_sources_missing_now'] or 'none'}; "
                     f"no-worse={r['no_worse_than_baseline']}")
    lines += ["", f"- provider token savings: {report['provider_token_savings']}", ""]
    return "\n".join(lines)


def render_md(report: dict) -> str:
    lines = ["# Context-pipeline promotion benchmark (M0-T069 Unit F)", "",
             f"Schema: `{report['schema']}` — correctness first.", "",
             "## Method", "", report["method"], "",
             "## Promotion evidence (D-013-R059)", ""]
    for key, val in report["promotion_evidence_R059"].items():
        lines.append(f"- **{key}**: {'PASS' if val else 'FAIL'}")
    lines += ["", "## Correctness cases", "",
              "| shape | case | byte-identical | mode | parsed | reused |",
              "|---|---|---|---|---|---|"]
    for r in report["correctness"]:
        lines.append(f"| {r['shape']} | {r['case']} | "
                     f"{'yes' if r['byte_identical'] else 'NO'} | {r['mode']} | "
                     f"{r['files_parsed']} | {r['files_reused']} |")
    lines += ["", "## Measured runtime",
              "", report["measured_runtime"]["label"], ""]
    for shape, stats in report["measured_runtime"]["per_shape"].items():
        for metric, s in stats.items():
            lines.append(f"- {shape} / {metric}: samples={s['samples']} "
                         f"median={s['median']}s p95={s['p95']}s")
    lines += ["", "## Efficiency",
              "", f"- provider token savings: "
                  f"{report['efficiency']['provider_token_savings']}", "",
              "## Threshold proposal (before the owner decision)", ""]
    for t in report["threshold_proposal"]["thresholds"]:
        lines.append(f"- **{t['metric']}** — {t['threshold']}: {t['rationale']}")
    lines += ["", "## Promotion decision", "", report["promotion_decision"], ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Context-pipeline promotion benchmark")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    ap.add_argument("--e2e", action="store_true",
                    help="run the END-TO-END compiler benchmark instead of "
                         "the index-parity benchmark")
    ap.add_argument("--baseline", default=None,
                    help="path to the captured G0 baseline JSON (e2e mode)")
    args = ap.parse_args(argv)
    if args.e2e:
        report = build_e2e_report(args.baseline)
        ok = (all(report["checks"].values())
              and report["baseline_comparison"].get("status") == "compared"
              and report["baseline_comparison"].get("no_worse_than_baseline"))
        renderer = render_e2e_md
    else:
        report = build_report(samples=args.samples)
        ok = all(report["promotion_evidence_R059"].values())
        renderer = render_md
    payload = canon_json_bytes(report)
    if args.out_json:
        pathlib.Path(args.out_json).write_bytes(payload)
    if args.out_md:
        pathlib.Path(args.out_md).write_text(renderer(report),
                                             encoding="utf-8", newline="\n")
    if not args.out_json and not args.out_md:
        sys.stdout.write(payload.decode("utf-8"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
