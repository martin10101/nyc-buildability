"""Regression guard for the M4-T005 phase-2b deployability fix: the rules
engine must load its ZR section snapshots from PACKAGE DATA
(``app/_zr_snapshots/v1/*.snapshot.json`` via ``importlib.resources``), NOT from
a repo-relative ``docs/`` filesystem walk.

The original defect (would surface in the CI web-e2e job / real Render deploy):
the API is installed non-editable (``pip install --no-deps ./services/api``);
``app/`` then lives in site-packages with no sibling ``docs/`` directory, so
``Path(__file__).parents[4] / "docs" / ...`` pointed at a non-existent path and
``RuleRegistry.load()`` -> ``SnapshotStore.load`` raised ``SnapshotError`` on
first use, 500-ing the rule-evaluation endpoint.

These tests prove:
 1. every bundled snapshot is byte-identical to its canonical ``docs`` source
    (and membership matches — no orphan bundled copy, no un-bundled source);
 2. ``sync_zr_snapshots.py --check`` passes (the same byte-identity contract the
    accepted contract-schema bundle uses);
 3. the snapshot package is discoverable via ``importlib.resources`` — the exact
    path an installed wheel uses — so the wheel will carry the data;
 4. ``SnapshotStore()`` with no explicit directory resolves to the PACKAGED
    location, so source and installed runs behave identically.

This runs inside the existing ``api`` CI job (mirroring how the Phase-1 contract
test guards the schema bundle); it adds NO new CI job.
"""

from __future__ import annotations

import subprocess
import sys
from importlib import resources
from pathlib import Path

from app.rules import snapshots as snapshots_module
from app.rules.snapshots import SnapshotStore

# test file: <root>/services/api/tests/rules/test_zr_snapshot_bundle.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
_CANONICAL_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
_BUNDLED_PACKAGE = "app._zr_snapshots.v1"
_SYNC_SCRIPT = _REPO_ROOT / "services" / "api" / "scripts" / "sync_zr_snapshots.py"
_GLOB = "*.snapshot.json"


def _canonical_names() -> list[str]:
    return sorted(p.name for p in _CANONICAL_DIR.glob(_GLOB))


def test_canonical_snapshots_exist() -> None:
    """Guard the guard: there is at least one canonical snapshot to bundle."""
    assert _CANONICAL_DIR.is_dir(), f"canonical snapshot source missing: {_CANONICAL_DIR}"
    assert _canonical_names(), f"no *.snapshot.json under {_CANONICAL_DIR}"


def test_every_bundled_snapshot_is_byte_identical_to_canonical() -> None:
    """Each bundled ``app/_zr_snapshots/v1/*.snapshot.json`` must be
    byte-for-byte identical to its ``docs/research/zr-snapshots/v1/`` source,
    and the two sets must have identical membership."""
    root = resources.files(_BUNDLED_PACKAGE)
    canonical = _canonical_names()

    bundled = sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_file() and entry.name.endswith(".snapshot.json")
    )
    assert bundled == canonical, (
        "bundled snapshot set differs from canonical source: "
        f"bundled={bundled} canonical={canonical}"
    )

    for name in canonical:
        src_bytes = (_CANONICAL_DIR / name).read_bytes()
        bundled_bytes = root.joinpath(name).read_bytes()
        assert bundled_bytes == src_bytes, (
            f"bundled snapshot {name} is not byte-identical to its canonical "
            "source; run: python services/api/scripts/sync_zr_snapshots.py"
        )


def test_sync_check_passes() -> None:
    """``sync_zr_snapshots.py --check`` exits 0 — the exact byte-identity
    contract, invoked the same way a drift check would be."""
    proc = subprocess.run(
        [sys.executable, str(_SYNC_SCRIPT), "--check"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"sync_zr_snapshots.py --check failed (exit {proc.returncode})\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_snapshot_package_discoverable_via_importlib_resources() -> None:
    """Load a snapshot the way the INSTALLED package does — through the
    importlib.resources traversable, not a repo-relative path. This is the path
    the wheel/production runtime uses; if it works here it works in
    site-packages."""
    root = resources.files(_BUNDLED_PACKAGE)
    for name in _canonical_names():
        text = root.joinpath(name).read_text(encoding="utf-8")
        assert text.strip().startswith("{"), f"{name} is not JSON"


def test_default_store_resolves_to_packaged_location() -> None:
    """A ``SnapshotStore`` built with no explicit directory must resolve to the
    PACKAGED snapshot directory (``app/_zr_snapshots/v1``), proving the default
    no longer depends on a repo-relative ``docs/`` walk that an installed wheel
    lacks."""
    packaged_dir = Path(str(resources.files(_BUNDLED_PACKAGE)))
    assert snapshots_module.DEFAULT_SNAPSHOT_DIR == packaged_dir

    store = SnapshotStore()
    assert store.directory == packaged_dir
    # It actually loads (the canonical failure mode was SnapshotError here).
    store.load()
    assert store.ids(), "default SnapshotStore loaded no snapshots"


def test_explicit_directory_override_is_unaffected(tmp_path) -> None:
    """The explicit-directory override path the test suite relies on must keep
    working unchanged: a directory arg wins over the packaged default."""
    name = _canonical_names()[0]
    (tmp_path / name).write_bytes((_CANONICAL_DIR / name).read_bytes())
    store = SnapshotStore(tmp_path).load()
    assert store.directory == tmp_path
    assert store.ids()
