"""Approved SVG snapshots and determinism (task E-01; plan M1-27).

Each fixture's site plan and massing must be byte-identical to the approved
snapshot under ``snapshots/``. After an intended drawing change, regenerate
with ``UPDATE_DRAWING_SNAPSHOTS=1 python -m pytest tests/drawings/kit`` and
review the SVG diff like code.
"""

from __future__ import annotations

import json
import os

import pytest

from app.drawings.kit import Drawing, render_massing, render_site_plan

from .kit_support import ENV_ON, SNAPSHOTS, fixture_paths, load

RENDERERS = {"site_plan": render_site_plan, "massing": render_massing}
CASES = [(path, name) for path in fixture_paths() for name in RENDERERS]


def _render(path, name):
    return RENDERERS[name](load(path), env=ENV_ON)


@pytest.mark.parametrize(("path", "name"), CASES, ids=[f"{p.stem}-{n}" for p, n in CASES])
def test_matches_approved_snapshot(path, name):
    result = _render(path, name)
    snapshot = SNAPSHOTS / f"{path.stem}.{name}.svg"
    if not isinstance(result, Drawing):
        assert not snapshot.exists(), f"{snapshot.name} exists but nothing was drawn"
        return
    if os.environ.get("UPDATE_DRAWING_SNAPSHOTS") == "1":
        snapshot.write_bytes(result.svg.encode("utf-8"))
    assert snapshot.exists(), f"no approved snapshot {snapshot.name}"
    # LF-normalize the checkout copy (a Windows autocrlf checkout smudges CRLF).
    assert result.svg.encode("utf-8") == snapshot.read_bytes().replace(b"\r\n", b"\n")


@pytest.mark.parametrize(("path", "name"), CASES, ids=[f"{p.stem}-{n}" for p, n in CASES])
def test_same_input_gives_byte_identical_svg(path, name):
    first = _render(path, name)
    again = _render(path, name)
    assert first == again
    reordered = json.loads(json.dumps(load(path), sort_keys=True))  # key order must not matter
    assert RENDERERS[name](reordered, env=ENV_ON) == first
