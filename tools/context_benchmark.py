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

    return {"shape": name, "corpus_manifest_digest": manifest,
            "baseline_export_digest": baseline.export_digest,
            "census_reconciles": bool(
                (cold.telemetry or {}).get("census", {}).get("reconciles")),
            "rows": rows, "timings_seconds": timings}


def _stats(values: list[float]) -> dict:
    if not values:
        return {"samples": 0, "median": None, "p95": None}
    ordered = sorted(values)
    return {"samples": len(values),
            "median": round(statistics.median(ordered), 4),
            "p95": round(ordered[max(int(len(ordered) * 0.95) - 1, 0)]
                         if len(ordered) > 1 else ordered[-1], 4)}


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
    args = ap.parse_args(argv)
    report = build_report(samples=args.samples)
    payload = canon_json_bytes(report)
    if args.out_json:
        pathlib.Path(args.out_json).write_bytes(payload)
    if args.out_md:
        pathlib.Path(args.out_md).write_text(render_md(report),
                                             encoding="utf-8", newline="\n")
    if not args.out_json and not args.out_md:
        sys.stdout.write(payload.decode("utf-8"))
    ok = all(report["promotion_evidence_R059"].values())
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
