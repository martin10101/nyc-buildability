#!/usr/bin/env python3
"""Sync the runtime-bundled contract schemas from the CANONICAL source
(task M2-T003 rework — web-e2e/production packaging fix).

WHY THIS EXISTS
---------------
``services/api/app/profile/contract.py`` must load the four contract schemas
a property_profile ``$ref`` registry needs (property_profile, source_fact,
common, coverage_status) AT RUNTIME. When the API is installed non-editable
(``pip install ./services/api`` in the web-e2e CI job, and every production
image), ``app/`` lives in ``site-packages`` and the repo's ``packages/``
directory is NOT alongside it. Resolving the schema by a repo-relative
``Path(__file__).parents[4] / "packages" / ...`` walk therefore raised
``FileNotFoundError`` at import time (the exact web-e2e regression).

The deployable FastAPI service must be SELF-CONTAINED. So the four schema
files are shipped as PACKAGE DATA inside
``services/api/app/_contract_schemas/v1/`` and loaded via
``importlib.resources`` — which works identically from a source tree and from
site-packages.

AUTHORITY MODEL
---------------
``packages/contracts/schemas/v1/*.schema.json`` remains the SINGLE canonical
source of authority. The bundled copies under ``app/_contract_schemas/v1/``
are BUILD ARTIFACTS kept provably byte-identical to the canonical files by
this script and the ``contracts-schema-bundle`` CI drift check. The canonical
source is never forked; the bundle is regenerated, never hand-edited.

USAGE (also the exact CI command):
    python services/api/scripts/sync_contract_schemas.py --check   # diff only
    python services/api/scripts/sync_contract_schemas.py           # write

Stdlib only (thin-client policy, docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md);
no network, no new dependency.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# The four documents a property_profile $ref registry must load (README:
# "Consumers that build their own $ref registry ... must load all four").
SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)

# services/api/scripts/sync_contract_schemas.py
#   parents[0] = scripts, parents[1] = services/api, parents[2] = services,
#   parents[3] = repo root.
_REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_DIR = _REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
BUNDLED_DIR = _REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def check() -> int:
    """Exit non-zero if any bundled copy is missing or not byte-identical to
    its canonical source."""
    problems: list[str] = []
    for name in SCHEMA_FILES:
        canonical = CANONICAL_DIR / name
        bundled = BUNDLED_DIR / name
        if not canonical.exists():
            problems.append(f"canonical source missing: {canonical}")
            continue
        if not bundled.exists():
            problems.append(f"bundled copy missing: {bundled}")
            continue
        if _read_bytes(canonical) != _read_bytes(bundled):
            problems.append(
                f"bundled copy diverges from canonical: {name} "
                f"({bundled} != {canonical})"
            )
    if problems:
        sys.stderr.write(
            "ERROR: runtime-bundled contract schemas are out of sync with the "
            "canonical source.\n"
            + "".join(f"  - {p}\n" for p in problems)
            + "Run: python services/api/scripts/sync_contract_schemas.py\n"
            "and commit services/api/app/_contract_schemas/v1/*.schema.json.\n"
        )
        return 1
    sys.stdout.write(
        "OK: runtime-bundled contract schemas are byte-identical to the "
        "canonical source.\n"
    )
    return 0


def write() -> int:
    BUNDLED_DIR.mkdir(parents=True, exist_ok=True)
    for name in SCHEMA_FILES:
        canonical = CANONICAL_DIR / name
        if not canonical.exists():
            sys.stderr.write(f"ERROR: canonical source missing: {canonical}\n")
            return 1
        (BUNDLED_DIR / name).write_bytes(_read_bytes(canonical))
        sys.stdout.write(f"synced {name}\n")
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
