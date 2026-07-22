"""Runtime-bundled ZR section snapshots (package data).

These ``*.snapshot.json`` files are BUILD ARTIFACTS copied byte-for-byte from
the canonical source ``docs/research/zr-snapshots/v1/*.snapshot.json`` by
``services/api/scripts/sync_zr_snapshots.py`` and kept provably in sync by the
``test_zr_snapshot_bundle`` pytest guard (runs inside the existing ``api`` CI
job). They are shipped inside the installed ``app`` package so a non-editable
install (web-e2e CI, production image) can load them via ``importlib.resources``
WITHOUT a sibling ``docs/`` directory — the exact deployability gap this fixes:
``docs/`` is not part of the ``app`` wheel, so the former repo-relative
``Path(__file__).parents[4] / "docs/..."`` walk resolved to a non-existent path
in site-packages and ``RuleRegistry.load()`` raised ``SnapshotError`` on first
use. Do not hand-edit; regenerate with the sync script.
"""
