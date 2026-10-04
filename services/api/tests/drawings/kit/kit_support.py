"""Shared support for the drawing-kit tests: fixtures, rendering with the Lane E
flag on, SVG parsing, and the check C-4 label-traceability checker.

Fixtures: every valid ``results`` contract fixture (six today) plus the Lane E kit
fixtures under ``fixtures/`` (schema-valid synthetic results documents). The
``zr_sections`` values in the kit fixtures are placeholders copied from the
contract fixture; the kit never prints them and they are not legal claims.
"""

from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from app.drawings.kit.labels import YARD_KIND_NAMES, Box, text_box
from app.drawings.kit.scope import ASSUMPTION_KEY_NAMES, FLAG_WORDS

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CONTRACT_FIXTURES = REPO / "packages" / "contracts" / "fixtures" / "valid" / "results"
KIT_FIXTURES = HERE / "fixtures"
SNAPSHOTS = HERE / "snapshots"
ENV_ON = {"LANE_E_ENABLED": "1"}
SVG_NS = "{http://www.w3.org/2000/svg}"
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
TOL = 0.005 + 1e-9  # labels carry at most two decimals


def fixture_paths() -> list[Path]:
    return sorted(CONTRACT_FIXTURES.glob("*.json")) + sorted(KIT_FIXTURES.glob("*.json"))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(doc, pointer: str):
    node = doc
    for part in pointer.lstrip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def parse(svg: str) -> ET.Element:
    return ET.fromstring(svg)


def texts(root: ET.Element) -> list[tuple[ET.Element, str]]:
    """Every ``<text>`` with its full text (tspan lines joined by one space)."""
    found = []
    for el in root.iter(f"{SVG_NS}text"):
        spans = el.findall(f"{SVG_NS}tspan")
        raw = " ".join(s.text or "" for s in spans) if spans else (el.text or "")
        found.append((el, " ".join(raw.split())))
    return found


def numbers_in(text: str) -> list[float]:
    return [float(m.replace(",", "")) for m in NUMBER.findall(text)]


def edge_length(doc, source: str) -> float:
    pointer, index = source[len("edge:"):].split("#")
    ring = resolve(doc, pointer)
    (ax, ay), (bx, by) = ring[int(index)], ring[int(index) + 1]
    return math.hypot(bx - ax, by - ay)


def pieces(root: ET.Element) -> list[tuple[str | None, str, str | None]]:
    """(source, text, role) of every printed piece: a whole ``<text>``, or - when
    its ``<tspan>`` parts carry sources - each run of consecutive tspans that
    share one source (a note part wrapped over several lines)."""
    found: list[tuple[str | None, str, str | None]] = []
    for el in root.iter(f"{SVG_NS}text"):
        role = el.get("data-role")
        spans = el.findall(f"{SVG_NS}tspan")
        if not any(span.get("data-source") for span in spans):
            raw = " ".join(s.text or "" for s in spans) if spans else (el.text or "")
            found.append((el.get("data-source"), " ".join(raw.split()), role))
            continue
        groups: list[tuple[str | None, list[str]]] = []
        for span in spans:
            source = span.get("data-source")
            if groups and groups[-1][0] == source:
                groups[-1][1].append(span.text or "")
            else:
                groups.append((source, [span.text or ""]))
        found += [(source, " ".join(" ".join(parts).split()), role) for source, parts in groups]
    return found


def label_problems(svg: str, doc: dict) -> list[str]:
    """Check C-4: every printed piece either carries no number, or names its
    source in the results and prints exactly that value."""
    problems = []
    for source, text, role in pieces(parse(svg)):
        if source is None:
            if any(ch.isdigit() for ch in text):
                problems.append(f"unsourced number in {text!r}")
            continue
        if source == "scale":
            continue  # scale-bar furniture: checked against the bar geometry
        if source.startswith("/scope/assumptions/") and source.endswith("/key"):
            key = resolve(doc, source)  # a fixed plain-words name per document key
            if ASSUMPTION_KEY_NAMES.get(key) != text:
                problems.append(f"{text!r} is not the scope key name for {key!r}")
            continue
        if source.startswith("/scope/assumptions/") and source.endswith("/value"):
            value = resolve(doc, source)
            if isinstance(value, bool):  # a flag: a fixed word per document boolean
                if FLAG_WORDS[value] != text:
                    problems.append(f"{text!r} is not the flag word for {value!r}")
                continue  # a numeric or string value falls through to the generic checks
        if source.startswith("edge:"):
            expected: object = edge_length(doc, source)
        else:
            expected = resolve(doc, source)
        if isinstance(expected, bool):
            problems.append(f"{text!r}: boolean source {source}")
        elif isinstance(expected, int | float):
            printed = numbers_in(text)
            if len(printed) != 1 or abs(printed[0] - expected) > TOL:
                problems.append(f"{text!r} does not print {expected} ({source})")
        elif role == "yard_kind":
            if text != YARD_KIND_NAMES[expected]:
                problems.append(f"{text!r} is not the yard kind {expected!r}")
        else:
            value = " ".join(str(expected).split())
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


def _all_edge_lengths(node) -> list[float]:
    """Edge lengths of every coordinate ring or line anywhere in ``node``."""
    if isinstance(node, list) and node and all(
        isinstance(p, list) and len(p) == 2 and all(isinstance(c, int | float) for c in p)
        for p in node
    ):
        return [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(node, node[1:], strict=False)]
    if isinstance(node, dict):
        return [n for v in node.values() for n in _all_edge_lengths(v)]
    if isinstance(node, list):
        return [n for v in node for n in _all_edge_lengths(v)]
    return []


def numbers_not_in_input(svg: str, doc: dict) -> list[str]:
    """Source-independent C-4 check: every number printed (scale bar aside) is
    a number of the results document or a length of one of its geometry edges."""
    allowed = _all_numbers(doc) + _all_edge_lengths(doc["geometry"])
    missing = []
    for el, text in texts(parse(svg)):
        if el.get("data-source") == "scale":
            continue
        for value in numbers_in(text):
            if not any(abs(value - a) <= TOL for a in allowed):
                missing.append(f"{value} in {text!r}")
    return missing


def _rotation(el: ET.Element) -> float:
    match = re.match(r"rotate\((-?[\d.]+)", el.get("transform") or "")
    return float(match.group(1)) if match else 0.0


def text_boxes(svg: str) -> list[tuple[str, Box]]:
    """Collision boxes of every single-line text (notes are wrapped blocks)."""
    boxes = []
    for el, text in texts(parse(svg)):
        if el.findall(f"{SVG_NS}tspan"):
            continue
        box = text_box(float(el.get("x")), float(el.get("y")), text,
                       float(el.get("font-size")), el.get("text-anchor", "start"),
                       _rotation(el))
        boxes.append((text, box))
    return boxes


def overlapping_labels(svg: str) -> list[tuple[str, str]]:
    boxes = text_boxes(svg)
    return [
        (a, b)
        for i, (a, box_a) in enumerate(boxes)
        for b, box_b in boxes[i + 1:]
        if box_a.overlaps(box_b, pad=0.0)
    ]


def point_in_or_on(p, ring, tol: float = 1e-6) -> bool:
    """Independent even-odd containment with a boundary tolerance."""
    x, y = p
    inside = False
    for (ax, ay), (bx, by) in zip(ring, ring[1:], strict=False):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        if math.hypot(x - (ax + t * dx), y - (ay + t * dy)) <= tol:
            return True
        if (ay > y) != (by > y) and ax + (y - ay) * dx / dy > x:
            inside = not inside
    return inside
