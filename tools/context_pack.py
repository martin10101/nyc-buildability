#!/usr/bin/env python3
"""Bounded, deterministic context-pack builder (D-010 Section 12; 0A.4 budgets).

THIN ORCHESTRATOR + COMPATIBILITY FACADE (M0-T065 Unit B). The implementation is
decomposed into focused modules for modularity; this module preserves the public
import surface and the CLI contract other code depends on:

    context_pack_io        deterministic hashing / JSON / git / file helpers
    context_pack_budget    0A.4 budget primitives (drift-locked) + adaptive tier
    context_pack_index     consumption of the deterministic A1/A2 index
    context_pack_sources   Section 12.1 source gathering
    context_pack_render    Section 12.3 meta + context.md rendering
    context_pack_assembly  build / overflow / emit + role sufficiency

Produces the SMALLEST COMPLETE packet for one task/role/provider under explicit
byte and estimated-token bounds, BYTE-IDENTICAL for the same repo state + args
(the repository SHA is the only time anchor). The budget constants and estimate
are mirrored from tools/agent_supervisor/review_packet.py (frozen shadow-only);
a drift-lock test asserts they never diverge. The adaptive tier (owner decision 7)
sets only the TARGET and never rewrites that contract; the hard ceiling stays the
lower of the ordinary and relative ceilings.

STDLIB ONLY. Python 3.11+ compatible. Path-safe on Windows and POSIX.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# --- compatibility facade: preserve the historical public import surface -------
from tools.context_pack_budget import (  # noqa: E402,F401
    DEFAULT_BYTES_PER_TOKEN,
    DEFAULT_ORDINARY_CEILING_TOKENS,
    DEFAULT_RELATIVE_CEILING_RATIO,
    DEFAULT_TARGET_TOKENS,
    SPLIT_SUMMARIZE_GUIDANCE,
    effective_ceiling_tokens,
    estimate_tokens,
    select_tier,
)
from tools.context_pack_assembly import (  # noqa: E402,F401
    ROLE_REQUIRED, assess_sufficiency, build, emit,
)
from tools.context_pack_io import (  # noqa: E402,F401
    canon_json_bytes, rel_posix, sha256_hex,
)
from tools.context_pack_render import SCHEMA_VERSION, make_meta  # noqa: E402,F401
from tools.context_pack_sources import (  # noqa: E402,F401
    DEFAULT_EXCLUSIONS, REDUCIBLE_GROUPS, Source, gather_sources,
)

_TIERS = ("small", "normal", "medium", "large")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Bounded, deterministic context-pack builder (D-010 Section 12).")
    p.add_argument("--task", required=True, help="task id, e.g. M0-T043")
    p.add_argument("--role", required=True, choices=("worker", "reviewer", "controller"))
    p.add_argument("--provider", required=True, choices=("claude", "codex"))
    p.add_argument("--max-bytes", required=True, type=int, dest="max_bytes")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--repo", default=".", help="repository root (default .)")
    p.add_argument("--model", default=None, help="model id (recorded in provenance)")
    p.add_argument("--context-window", type=int, default=None, dest="context_window",
                   help="reported model context window (for the 20%% relative ceiling)")
    p.add_argument("--include", action="append", default=[],
                   help="explicit source file (repeatable)")
    p.add_argument("--ci-summary", default=None, dest="ci_summary",
                   help="path to an injected CI summary (never fetched from network)")
    p.add_argument("--diff-base", default="HEAD", dest="diff_base",
                   help="git ref to diff against (default HEAD)")
    p.add_argument("--graph-limit", type=int, default=20, dest="graph_limit",
                   help="per-query line cap for bounded code-graph neighborhoods")
    # Budget contract (accepted; unchanged by the tier amendment) -----------------
    p.add_argument("--target-tokens", type=int, default=None, dest="target_tokens",
                   help="explicit target override; default = the adaptive tier target")
    p.add_argument("--ordinary-ceiling-tokens", type=int,
                   default=DEFAULT_ORDINARY_CEILING_TOKENS,
                   dest="ordinary_ceiling_tokens")
    p.add_argument("--relative-ratio", type=float, default=DEFAULT_RELATIVE_CEILING_RATIO,
                   dest="relative_ratio")
    p.add_argument("--bytes-per-token", type=float, default=DEFAULT_BYTES_PER_TOKEN,
                   dest="bytes_per_token")
    # Adaptive tier amendment (D-013-R041 / owner decision 7) ---------------------
    p.add_argument("--tier", default=None, choices=_TIERS,
                   help="explicit tier request (medium/large need --tier-justification)")
    p.add_argument("--tier-justification", default=None, dest="tier_justification",
                   help="justification required to grant a medium/large larger target")
    p.add_argument("--architectural", action="store_true",
                   help="architectural change: prefer split-first (large tier)")
    # Index consumption controls --------------------------------------------------
    p.add_argument("--index-cache-base", default=None, dest="index_cache_base",
                   help="base dir for the deterministic index cache (default: platform)")
    p.add_argument("--no-index-telemetry", action="store_true", dest="no_index_telemetry",
                   help="do not append the external index run-record JSONL")
    p.add_argument("--no-index", action="store_true", dest="no_index",
                   help="escape hatch: skip index consumption (records a coverage omission)")
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
        "budget_tier": meta["budget"]["tier"]["tier"],
    }
    stream = sys.stderr if code != 0 else sys.stdout
    print(json.dumps(summary, sort_keys=True), file=stream)
    if code == 2:
        print("FAIL-CLOSED: material does not fit the effective bound; see "
              "context.md split proposal.", file=sys.stderr)
    elif code == 3:
        print("FAIL-CLOSED: packet is INSUFFICIENT for the role — "
              + meta["sufficiency"]["reason"], file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
