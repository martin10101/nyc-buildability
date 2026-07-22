#!/usr/bin/env python3
"""Sync the runtime-bundled ZR section snapshots from the CANONICAL source
(task M4-T005 phase 2b — web-e2e/production packaging fix; mirrors the accepted
``sync_contract_schemas.py`` pattern).

WHY THIS EXISTS
---------------
``app/rules/snapshots.py`` (``SnapshotStore.load``) must read the section-level
Zoning Resolution snapshots AT RUNTIME to build a rule-evaluation trace's
provenance. When the API is installed non-editable (``pip install ./services/api``
in the web-e2e CI job, and every production image), ``app/`` lives in
``site-packages`` and the repo's ``docs/`` directory is NOT alongside it.
Resolving the snapshot directory by a repo-relative
``Path(__file__).parents[4] / "docs" / "research" / "zr-snapshots" / "v1"`` walk
therefore pointed at a non-existent path, and ``RuleRegistry.load()`` raised
``SnapshotError`` on first use → the rule-evaluation endpoint 500'd in web-e2e
and would break the real Render deploy.

The deployable FastAPI service must be SELF-CONTAINED. So every snapshot file is
shipped as PACKAGE DATA inside ``services/api/app/_zr_snapshots/v1/`` and loaded
via ``importlib.resources`` — which works identically from a source tree and
from site-packages. (Rulesets already live under ``app/rules/rulesets/`` and
were always packaged; only the ZR snapshots under ``docs/`` were unpackaged.)

AUTHORITY MODEL
---------------
``docs/research/zr-snapshots/v1/*.snapshot.json`` remains the SINGLE canonical
source of authority (declared in docs/RULES_ENGINE_ARCHITECTURE.md). The bundled
copies under ``app/_zr_snapshots/v1/`` are BUILD ARTIFACTS kept provably
byte-identical to the canonical files by this script and the
``test_zr_snapshot_bundle`` pytest guard (which runs inside the existing ``api``
CI job — no new CI job). The canonical source is never forked; the bundle is
regenerated, never hand-edited.

USAGE (also the exact guard command):
    python services/api/scripts/sync_zr_snapshots.py --check   # diff only
    python services/api/scripts/sync_zr_snapshots.py           # write

Stdlib only (thin-client policy, docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md);
no network, no new dependency.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# services/api/scripts/sync_zr_snapshots.py
#   parents[0] = scripts, parents[1] = services/api, parents[2] = services,
#   parents[3] = repo root.
_REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
BUNDLED_DIR = _REPO_ROOT / "services" / "api" / "app" / "_zr_snapshots" / "v1"

_GLOB = "*.snapshot.json"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _canonical_names() -> list[str]:
    return sorted(p.name for p in CANONICAL_DIR.glob(_GLOB))


def _bundled_names() -> list[str]:
    return sorted(p.name for p in BUNDLED_DIR.glob(_GLOB)) if BUNDLED_DIR.is_dir() else []


def check() -> int:
    """Exit non-zero if the bundle and the canonical source are not a
    byte-identical, same-membership set of snapshot files."""
    problems: list[str] = []
    if not CANONICAL_DIR.is_dir():
        sys.stderr.write(f"ERROR: canonical snapshot source missing: {CANONICAL_DIR}\n")
        return 1

    canonical = _canonical_names()
    bundled = _bundled_names()
    if not canonical:
        problems.append(f"no canonical snapshots found under {CANONICAL_DIR}")

    # Orphan bundled copies (a snapshot removed from the source but left behind).
    for name in bundled:
        if name not in canonical:
            problems.append(f"bundled copy has no canonical source (orphan): {name}")

    for name in canonical:
        src = CANONICAL_DIR / name
        dst = BUNDLED_DIR / name
        if not dst.exists():
            problems.append(f"bundled copy missing: {dst}")
            continue
        if _read_bytes(src) != _read_bytes(dst):
            problems.append(
                f"bundled copy diverges from canonical: {name} ({dst} != {src})"
            )

    if problems:
        sys.stderr.write(
            "ERROR: runtime-bundled ZR snapshots are out of sync with the "
            "canonical source.\n"
            + "".join(f"  - {p}\n" for p in problems)
            + "Run: python services/api/scripts/sync_zr_snapshots.py\n"
            "and commit services/api/app/_zr_snapshots/v1/*.snapshot.json.\n"
        )
        return 1
    sys.stdout.write(
        "OK: runtime-bundled ZR snapshots are byte-identical to the canonical "
        f"source ({len(canonical)} file(s)).\n"
    )
    return 0


def write() -> int:
    if not CANONICAL_DIR.is_dir():
        sys.stderr.write(f"ERROR: canonical snapshot source missing: {CANONICAL_DIR}\n")
        return 1
    BUNDLED_DIR.mkdir(parents=True, exist_ok=True)

    canonical = _canonical_names()
    if not canonical:
        sys.stderr.write(f"ERROR: no canonical snapshots found under {CANONICAL_DIR}\n")
        return 1

    for name in canonical:
        (BUNDLED_DIR / name).write_bytes(_read_bytes(CANONICAL_DIR / name))
        sys.stdout.write(f"synced {name}\n")

    # Remove orphan bundled copies so the bundle mirrors the source exactly.
    for name in _bundled_names():
        if name not in canonical:
            (BUNDLED_DIR / name).unlink()
            sys.stdout.write(f"removed orphan {name}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if a bundled copy is missing or stale",
    )
    args = parser.parse_args()
    return check() if args.check else write()


if __name__ == "__main__":
    raise SystemExit(main())
