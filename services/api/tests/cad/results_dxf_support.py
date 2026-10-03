"""Shared support for the results-DXF tests (task E-03): fixtures, rendering
with the Lane E flag on, and a small group-code reader that is independent of
the writer (it parses the emitted text back into header values, layers and
entities)."""

from __future__ import annotations

import copy
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from app.cad.results_dxf import ResultsDxf, level_layer, render_results_dxf
from app.drawings.kit.styles import style_for

from ..drawings.kit.kit_support import CONTRACT_FIXTURES, KIT_FIXTURES, fixture_paths, load

__all__ = [
    "BASE",
    "CONTRACT_FIXTURES",
    "ENV_ON",
    "KIT_FIXTURES",
    "LOT_ONLY",
    "NARROW",
    "SNAPSHOTS",
    "Entity",
    "ParsedDxf",
    "expected_counts",
    "fixture_paths",
    "load",
    "mutated",
    "open_ring",
    "parse_dxf",
    "render",
    "set_at",
]

HERE = Path(__file__).resolve().parent
SNAPSHOTS = HERE / "snapshots" / "results_dxf"
ENV_ON = {"LANE_E_ENABLED": "1"}
BASE = load(CONTRACT_FIXTURES / "synthetic_all_answers_available.json")
LOT_ONLY = load(CONTRACT_FIXTURES / "synthetic_envelope_not_available_existing_building.json")
NARROW = load(CONTRACT_FIXTURES / "synthetic_needs_street_width_narrow_case.json")


def render(doc: dict) -> ResultsDxf:
    result = render_results_dxf(doc, env=ENV_ON)
    assert isinstance(result, ResultsDxf), result
    return result


def mutated(doc: dict, *mutations) -> dict:
    changed = copy.deepcopy(doc)
    for mutate in mutations:
        mutate(changed)
    return changed


def set_at(pointer: str, value):
    def mutate(doc):
        node = doc
        parts = pointer.strip("/").split("/")
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        node[int(parts[-1]) if isinstance(node, list) else parts[-1]] = value
    return mutate


@dataclass
class Entity:
    kind: str
    layer: str = ""
    points: list[tuple[float, float, float]] = field(default_factory=list)
    closed: bool = False
    text: str = ""
    height: float = 0.0


@dataclass
class ParsedDxf:
    header: dict[str, list[tuple[int, str]]]
    layers: list[tuple[str, int]]
    entities: list[Entity]

    def counts(self) -> dict[str, Counter]:
        """{layer: Counter(entity kind)}."""
        by_layer: dict[str, Counter] = {}
        for entity in self.entities:
            by_layer.setdefault(entity.layer, Counter())[entity.kind] += 1
        return by_layer

    def on(self, layer: str, kind: str | None = None) -> list[Entity]:
        return [e for e in self.entities if e.layer == layer and kind in (None, e.kind)]


def _pairs(text: str) -> list[tuple[int, str]]:
    lines = text.split("\n")
    assert lines[-1] == "", "the DXF ends with a newline"
    lines.pop()
    assert len(lines) % 2 == 0, "group codes and values alternate"
    return [(int(lines[i]), lines[i + 1]) for i in range(0, len(lines), 2)]


def _sections(pairs):
    sections, i = {}, 0
    order = []
    while i < len(pairs):
        if pairs[i] == (0, "SECTION"):
            name, j = pairs[i + 1][1], i + 2
            inner = []
            while pairs[j] != (0, "ENDSEC"):
                inner.append(pairs[j])
                j += 1
            sections[name] = inner
            order.append(name)
            i = j + 1
        else:
            assert pairs[i] == (0, "EOF") and i == len(pairs) - 1
            i += 1
    assert order == ["HEADER", "TABLES", "ENTITIES"]
    return sections


def _records(pairs) -> list[list[tuple[int, str]]]:
    """Split a pair stream at every group-0 pair."""
    records: list[list[tuple[int, str]]] = []
    for code, value in pairs:
        if code == 0:
            records.append([(code, value)])
        elif records:
            records[-1].append((code, value))
    return records


def _xyz(record, first: int = 10) -> tuple[float, float, float]:
    values = dict(record)
    return (float(values[first]), float(values[first + 10]), float(values[first + 20]))


def parse_dxf(text: str) -> ParsedDxf:
    sections = _sections(_pairs(text))
    header: dict[str, list[tuple[int, str]]] = {}
    for code, value in sections["HEADER"]:
        if code == 9:
            header[value] = []
            current = value
        else:
            header[current].append((code, value))
    layers = []
    for record in _records(sections["TABLES"]):
        if record[0] == (0, "LAYER"):
            values = dict(record)
            layers.append((values[2], int(values[62])))
    entities: list[Entity] = []
    polyline: Entity | None = None
    for record in _records(sections["ENTITIES"]):
        kind, values = record[0][1], dict(record)
        if kind == "POLYLINE":
            polyline = Entity("POLYLINE", values[8], closed=bool(int(values[70]) & 1))
        elif kind == "VERTEX":
            assert polyline is not None and values[8] == polyline.layer
            polyline.points.append(_xyz(record))
        elif kind == "SEQEND":
            assert polyline is not None
            entities.append(polyline)
            polyline = None
        elif kind == "LINE":
            entities.append(Entity("LINE", values[8], [_xyz(record), _xyz(record, 11)]))
        elif kind == "TEXT":
            entities.append(Entity("TEXT", values[8], [_xyz(record)], text=values[1],
                                   height=float(values[40])))
        else:
            entities.append(Entity(kind, values.get(8, "")))
    return ParsedDxf(header, layers, entities)


def open_ring(ring):
    return [tuple(float(v) for v in p) for p in ring[:-1]]


def expected_counts(doc: dict, notes: int) -> dict[str, Counter]:
    """Entity counts per layer, derived from the raw results JSON."""
    geometry = doc["geometry"]
    expected: dict[str, Counter] = {}

    def add(layer, kind, n):
        if n:
            expected.setdefault(layer, Counter())[kind] += n

    add("C-PROP-LINE", "POLYLINE", len(geometry["lot_outline"]))
    if geometry["yards"]["status"] == "available":
        for entry in geometry["yards"]["entries"]:
            if entry["status"] != "not_required":
                add("A-ZONE-YARD", "POLYLINE", len(entry["outline"]))
    if geometry["setback_lines_per_level"]["status"] == "available":
        for entry in geometry["setback_lines_per_level"]["entries"]:
            for line in entry["lines"]:
                segments = sum(1 for a, b in zip(line, line[1:], strict=False) if a != b)
                add(level_layer(entry["floor"]), "LINE", segments)
    if geometry["envelope"]["status"] == "available":
        for tier in geometry["envelope"]["tiers"]:
            add("A-ZONE-ENVL", "POLYLINE", 2 * len(tier["outline"]))
            add("A-ZONE-ENVL", "LINE", sum(len(ring) - 1 for ring in tier["outline"]))
    if geometry["floor_plates"]["status"] == "available":
        for plate in geometry["floor_plates"]["entries"]:
            add(style_for(plate["use"]).cad_layer, "POLYLINE", len(plate["outline"]))
    add("A-ANNO-NOTE", "TEXT", notes)
    return expected
