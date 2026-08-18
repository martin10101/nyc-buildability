#!/usr/bin/env python3
"""Baseline harness: reference digests + counts from the UNMODIFIED code-graph
generator, captured BEFORE any indexing behavior changes (M0-T063 Unit A1,
D-013-R049/R054/R055).

Why this exists: A2 (incremental indexing) must prove byte-identical output
against a clean full rebuild. That proof is only meaningful against a frozen
REFERENCE captured while the generator is still the accepted, unmodified one.
This module runs `tools/code_graph.generate.build_graph` as-is, serializes it
with the generator's own canonical serializer, and records:
  * the export digest (domain-separated) and node/edge/input counts;
  * the generator's own source fingerprint and version;
  * the A1 repository snapshot fingerprint for provenance (repo_fingerprint).

Two storage classes (D-013-R050):
  * COMMITTED EVIDENCE: a bounded, sanitized JSON + Markdown summary (digests and
    counts only - never the raw graph, never an absolute private path);
  * EXTERNAL TELEMETRY: an append-only, redacted JSONL run record in the accepted
    per-checkout cache directory OUTSIDE the repo. Unknown values are null,
    never fabricated as zero (D-013-R051).
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import sys
from typing import Any

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools import repo_fingerprint as rf  # noqa: E402
from tools import repo_index_cache as ric  # noqa: E402
from tools.code_graph import generate as codegraph  # noqa: E402

BASELINE_SCHEMA = "repo_index_baseline/v1"
TELEMETRY_FILENAME = "baseline_telemetry.jsonl"


def _export_digest(graph: dict[str, Any]) -> str:
    """Domain-separated digest over the generator's OWN canonical bytes, so the
    baseline digest tracks exactly what a full rebuild would serialize."""
    return rf.domain_hash("codegraph_export", codegraph.serialize(graph))


@dataclasses.dataclass
class BaselineResult:
    schema: str
    snapshot_fingerprint: str
    checkout_identity: str
    generator_version: str
    codegraph_schema_version: str
    source_fingerprint: str
    export_digest: str
    node_count: int
    edge_count: int
    input_file_count: int
    node_counts: dict[str, Any]
    edge_counts: dict[str, Any]
    census: dict[str, Any]

    def committed_summary(self) -> dict[str, Any]:
        """Bounded, sanitized - digests + counts only, no raw graph, no paths."""
        return {
            "schema": self.schema,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "checkout_identity": self.checkout_identity,
            "generator_version": self.generator_version,
            "codegraph_schema_version": self.codegraph_schema_version,
            "source_fingerprint": self.source_fingerprint,
            "export_digest": self.export_digest,
            "counts": {
                "nodes": self.node_count,
                "edges": self.edge_count,
                "input_files": self.input_file_count,
                "node_counts": self.node_counts,
                "edge_counts": self.edge_counts,
            },
            "census": self.census,
        }

    def telemetry_record(self, *, run_id: str | None,
                         elapsed_seconds: float | None) -> dict[str, Any]:
        """Redacted run record. Fields that a tool cannot report are null, never
        fabricated as zero (D-013-R051). No absolute paths, no raw content."""
        return {
            "schema": self.schema,
            "run_id": run_id,                     # nullable
            "kind": "baseline_full_build",
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "checkout_identity": self.checkout_identity,
            "generator_version": self.generator_version,
            "export_digest": self.export_digest,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "input_file_count": self.input_file_count,
            "eligible": self.census.get("eligible"),
            "indexed": self.census.get("indexed"),
            # measured-only fields; null when unavailable (never zero):
            "elapsed_seconds": elapsed_seconds,
            "provider_input_tokens": None,
            "provider_output_tokens": None,
            "context_window_occupancy": None,
        }


def capture_baseline(repo_root: str | os.PathLike[str]) -> BaselineResult:
    """Run the UNMODIFIED generator and the A1 fingerprint; record the reference.

    Deterministic: the generator's output and the fingerprint are both functions
    of the frozen snapshot, so the export_digest and counts are reproducible for
    a given checkout state (D-013-R055).
    """
    root = pathlib.Path(repo_root).resolve()
    fingerprint = rf.compute_fingerprint(root)
    graph, meta, input_files = codegraph.build_graph(str(root))
    return BaselineResult(
        schema=BASELINE_SCHEMA,
        snapshot_fingerprint=fingerprint.snapshot_fingerprint,
        checkout_identity=fingerprint.checkout_identity,
        generator_version=meta.get("generator_version", "unknown"),
        codegraph_schema_version=meta.get("schema_version", "unknown"),
        source_fingerprint=meta.get("source_fingerprint", ""),
        export_digest=_export_digest(graph),
        node_count=len(graph.get("nodes", [])),
        edge_count=len(graph.get("edges", [])),
        input_file_count=meta.get("input_file_count", len(input_files)),
        node_counts=meta.get("node_counts", {}),
        edge_counts=meta.get("edge_counts", {}),
        census=fingerprint.census.to_dict(),
    )


def write_committed_evidence(result: BaselineResult,
                             json_path: str | os.PathLike[str],
                             md_path: str | os.PathLike[str]) -> None:
    """Write the bounded, sanitized committed evidence (D-013-R050/R064)."""
    summary = result.committed_summary()
    jp = pathlib.Path(json_path)
    jp.parent.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8", newline="\n")
    md = pathlib.Path(md_path)
    md.write_text(_render_md(summary), encoding="utf-8", newline="\n")


def _render_md(summary: dict[str, Any]) -> str:
    c = summary["counts"]
    cen = summary["census"]
    return (
        "# M0-T063 Unit A1 baseline evidence\n\n"
        "Reference full-build captured from the UNMODIFIED code-graph generator "
        "before any A1 indexing behavior change (D-013-R049/R054/R055). Digests "
        "and counts only; no raw graph, no private absolute paths.\n\n"
        f"- snapshot_fingerprint: `{summary['snapshot_fingerprint']}`\n"
        f"- checkout_identity: `{summary['checkout_identity']}`\n"
        f"- generator_version: `{summary['generator_version']}` "
        f"(schema `{summary['codegraph_schema_version']}`)\n"
        f"- source_fingerprint: `{summary['source_fingerprint']}`\n"
        f"- **export_digest: `{summary['export_digest']}`**\n\n"
        "## Counts\n"
        f"- nodes: {c['nodes']}\n- edges: {c['edges']}\n"
        f"- input_files: {c['input_files']}\n\n"
        "## Census (reconciles: "
        f"{cen.get('reconciles')})\n"
        f"- eligible: {cen.get('eligible')}\n- indexed: {cen.get('indexed')}\n"
        f"- excluded: {cen.get('excluded')}\n- failed: {cen.get('failed')}\n"
    )


def append_telemetry(result: BaselineResult,
                     checkout_root: str | os.PathLike[str], *,
                     run_id: str | None = None,
                     elapsed_seconds: float | None = None,
                     base: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Append the redacted run record to the external per-checkout telemetry log
    (outside the repo; D-013-R031/R050)."""
    cache = ric.IndexCache(checkout_root, base=base)
    cache.root.mkdir(parents=True, exist_ok=True)
    log = cache.root / TELEMETRY_FILENAME
    record = result.telemetry_record(run_id=run_id, elapsed_seconds=elapsed_seconds)
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return log


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=str(pathlib.Path.cwd()))
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--md-out", default=None)
    args = ap.parse_args()
    result = capture_baseline(args.repo)
    if args.json_out and args.md_out:
        write_committed_evidence(result, args.json_out, args.md_out)
    print(json.dumps(result.committed_summary(), indent=2, sort_keys=True))
