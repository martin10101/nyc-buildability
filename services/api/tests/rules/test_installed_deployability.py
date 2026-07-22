"""Regression guard: the API must remain installable+runnable as a wheel.

The rule engine reads three kinds of runtime resource from disk at first use:
the bundled contract schemas, the bundled ZR section snapshots, and the rule
DSL rulesets. All three live under ``app/`` but are DATA files, so setuptools
only ships them when they are declared as ``[tool.setuptools.package-data]``.
Omitting any one silently breaks the INSTALLED wheel (web-e2e + the real Render
deploy) with a ``FileNotFoundError``/``SnapshotError`` at first rule evaluation,
while every source-tree test still passes (the files exist relative to the repo).

This test pins those declarations so a future edit to ``pyproject.toml`` cannot
regress installed-context deployability without turning this test red in the
``api`` CI job. It also asserts each declared source directory actually holds the
files the glob promises, so the wheel cannot ship an empty directory.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_API_ROOT = Path(__file__).resolve().parents[2]  # services/api
_APP = _API_ROOT / "app"

# (package-data key, glob, on-disk directory the glob resolves against)
_REQUIRED_PACKAGE_DATA = [
    ("app._contract_schemas.v1", "*.schema.json", _APP / "_contract_schemas" / "v1"),
    ("app._zr_snapshots.v1", "*.snapshot.json", _APP / "_zr_snapshots" / "v1"),
    ("app.rules", "rulesets/*.rule.json", _APP / "rules"),
]


def _package_data() -> dict:
    data = tomllib.loads((_API_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["tool"]["setuptools"]["package-data"]


def test_pyproject_declares_every_runtime_resource_as_package_data() -> None:
    declared = _package_data()
    for key, glob, _ in _REQUIRED_PACKAGE_DATA:
        assert key in declared, (
            f"pyproject package-data is missing {key!r}; the installed wheel would "
            f"omit these files and 500 at first rule evaluation"
        )
        assert glob in declared[key], f"{key!r} must ship {glob!r}, got {declared[key]!r}"


def test_each_declared_glob_actually_matches_shipped_files() -> None:
    for key, glob, base_dir in _REQUIRED_PACKAGE_DATA:
        matches = sorted(base_dir.glob(glob))
        assert matches, (
            f"package-data {key} = [{glob!r}] resolves to no files under {base_dir}; "
            f"the wheel would ship an empty/absent directory"
        )
