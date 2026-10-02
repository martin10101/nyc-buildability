"""Approved SVG snapshots and determinism (task E-07; plan section 5c item 2).

Each fixture's location map and zoning map must be byte-identical to the
approved snapshot under ``snapshots/``. A fixture whose layer is
``not_available`` renders :class:`Unavailable`, and no snapshot exists for it.
After an intended change, regenerate with
``UPDATE_DRAWING_SNAPSHOTS=1 python -m pytest tests/drawings/maps`` and review
the SVG diff like code.
"""

from __future__ import annotations

import json
import os

import pytest

from app.drawings.maps import Drawing, render_location_map, render_zoning_map

from .maps_support import ENV_ON, SNAPSHOTS, fixture_paths, load

RENDERERS = {"location_map": render_location_map, "zoning_map": render_zoning_map}
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
