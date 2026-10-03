"""Approved DXF snapshots and determinism for the results DXF (task E-03).

Each fixture's DXF must be byte-identical to the approved file under
``snapshots/results_dxf/``. After an intended change, regenerate with
``UPDATE_DXF_SNAPSHOTS=1 python -m pytest tests/cad/test_results_dxf_snapshots.py``
and review the diff like code.
"""

from __future__ import annotations

import json
import os

import pytest

from app.cad.results_dxf import render_results_dxf

from .results_dxf_support import ENV_ON, SNAPSHOTS, fixture_paths, load, render

PATHS = fixture_paths()
IDS = [p.stem for p in PATHS]


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_matches_approved_snapshot(path):
    data = render(load(path)).text.encode("ascii")
    snapshot = SNAPSHOTS / f"{path.stem}.dxf"
    if os.environ.get("UPDATE_DXF_SNAPSHOTS") == "1":
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
    assert snapshot.exists(), f"no approved snapshot {snapshot.name}"
    # LF-normalize the checkout copy (a Windows autocrlf checkout smudges CRLF).
    assert data == snapshot.read_bytes().replace(b"\r\n", b"\n")


@pytest.mark.parametrize("path", PATHS, ids=IDS)
def test_same_results_give_byte_identical_dxf(path):
    doc = load(path)
    first = render(doc)
    assert render(doc) == first
    reordered = json.loads(json.dumps(doc, sort_keys=True))  # key order must not matter
    assert render_results_dxf(reordered, env=ENV_ON) == first


def test_snapshots_are_ascii_with_lf_line_ends():
    for path in PATHS:
        data = (SNAPSHOTS / f"{path.stem}.dxf").read_bytes().replace(b"\r\n", b"\n")
        assert data.isascii() and b"\r" not in data
        assert data.endswith(b"0\nEOF\n")
