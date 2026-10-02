"""Shared support for the location/zoning map tests: fixtures, rendering with
the Lane E flag on, SVG parsing, the check-C-4 label-traceability checker, and
an independent re-measurement of the drawn geometry.

Generic SVG parsing helpers (``resolve``, ``parse``, ``pieces``, ``numbers_in``,
``text_boxes``, ``overlapping_labels``) are reused from the drawing-kit test
support so both suites read SVG the same way. Fixtures under ``fixtures/`` are
schema-valid synthetic map-context documents shaped like the recorded city open
data (lot outline, DCP ``nyzd`` districts, OTI building footprints); they carry
the official attribution, accuracy and use-limitation text but no live call is
ever made.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ..kit.kit_support import (
    SVG_NS,
    TOL,
    load,
    numbers_in,
    overlapping_labels,
    parse,
    pieces,
    resolve,
    text_boxes,
)

__all__ = [
    "ENV_ON",
    "SNAPSHOTS",
    "SVG_NS",
    "TOL",
    "base_paths",
    "fixture_paths",
    "label_problems",
    "load",
    "numbers_not_in_input",
    "overlapping_labels",
    "parse",
    "path_area",
    "pieces",
    "resolve",
    "scale_px_per_ft",
    "subpaths",
    "text_boxes",
]

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
SNAPSHOTS = HERE / "snapshots"
ENV_ON = {"LANE_E_ENABLED": "1"}

_POINT = re.compile(r"[ML](-?[\d.]+) (-?[\d.]+)")


def fixture_paths() -> list[Path]:
    return sorted(FIXTURES.glob("*.json"))


def label_problems(svg: str, doc: dict) -> list[str]:
    """Check C-4 for the maps: every printed piece either carries no number, or
    names a source in the data (a string) and ends with exactly that string,
    with no number in the text before it (e.g. ``BBL 100...`` ends with the BBL,
    ``C4-4A`` is the ZONEDIST symbol verbatim)."""
    problems = []
    for source, text, _role in pieces(parse(svg)):
        if source is None:
            if any(ch.isdigit() for ch in text):
                problems.append(f"unsourced number in {text!r}")
            continue
        if source == "scale":
            continue  # scale-bar furniture checked against the bar geometry
        expected = resolve(doc, source)
        if not isinstance(expected, str):
            problems.append(f"{text!r}: source {source} is not a string")
            continue
        value = " ".join(expected.split())
        head = text[: len(text) - len(value)]
        if not text.endswith(value) or any(ch.isdigit() for ch in head):
            problems.append(f"{text!r} does not end with {source} = {value!r}")
    return problems


def _all_numbers(node) -> list[float]:
    if isinstance(node, bool):
        return []
    if isinstance(node, int | float):
        return [float(node)]
    if isinstance(node, dict):
        return [n for v in node.values() for n in _all_numbers(v)]
    if isinstance(node, list):
        return [n for v in node for n in _all_numbers(v)]
    if isinstance(node, str):
        return numbers_in(node)
    return []


def numbers_not_in_input(svg: str, doc: dict) -> list[str]:
    """Every printed number (scale bar aside) is a number present in the data."""
    allowed = _all_numbers(doc)
    missing = []
    root = parse(svg)
    for el in root.iter(f"{SVG_NS}text"):
        if el.get("data-source") == "scale":
            continue
        spans = el.findall(f"{SVG_NS}tspan")
        text = " ".join(s.text or "" for s in spans) if spans else (el.text or "")
        for value in numbers_in(text):
            if not any(abs(value - a) <= TOL for a in allowed):
                missing.append(f"{value} in {text!r}")
    return missing


def subpaths(d: str) -> list[list[tuple[float, float]]]:
    return [[(float(x), float(y)) for x, y in _POINT.findall(part)]
            for part in d.split("Z") if _POINT.search(part)]


def _ring_area(points) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(points, points[1:] + points[:1], strict=True))) / 2.0


def path_area(d: str) -> float:
    """Exterior minus holes (first sub-path is the exterior)."""
    rings = subpaths(d)
    return _ring_area(rings[0]) - sum(_ring_area(r) for r in rings[1:])


def base_paths(root: ET.Element) -> list[ET.Element]:
    """Fill paths only - the hatch overlays (``fill="url(...)"``) are skipped."""
    return [p for p in root.iter(f"{SVG_NS}path") if not p.get("fill", "").startswith("url(")]


def scale_px_per_ft(root: ET.Element) -> float:
    bar = next(g for g in root.iter(f"{SVG_NS}g") if g.get("data-role") == "scale-bar")
    return float(bar.get("data-px-per-ft"))


def world_area(doc: dict, pointer: str) -> float:
    ring = resolve(doc, pointer)[0]
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(ring, ring[1:] + ring[:1], strict=True))) / 2.0


def _d(el: ET.Element) -> str:
    return el.get("d") or ""


def drawn_world_area(svg: str, data_source: str) -> float | None:
    """Area (sq ft) of the drawn polygon with ``data-source``, read back through
    the map's scale - independent of the renderer's own code."""
    root = parse(svg)
    k = scale_px_per_ft(root)
    for path in base_paths(root):
        if path.get("data-source") == data_source:
            return path_area(_d(path)) / k ** 2
    return None


def base_sources(svg: str) -> list[str]:
    return [p.get("data-source") for p in base_paths(parse(svg)) if p.get("data-source")]


__all__ += ["base_sources", "drawn_world_area", "world_area"]
