"""Shared support for the site-context / block / neighbourhood map tests
(M5-T155).

These build the 1.1.0 ``map_context`` documents the new drawings consume, BY
HAND, to the shape of ruling Y2 - the other builder (M5-T154) produces the same
shape from the recorded pack at the same time, so these tests do not wait on it.
The benchmark document is built from the RECORDED official geometry in
``tests/fixtures/benchmark_215_16_northern`` and ``..._block_7334_lots_1_70``
(lot 70's outline, lot 1's outline, the 6 recorded street centre lines with
names and widths, lot 70's two recorded building footprints). The two south
neighbours (lot 11 and lot 61) are CONSTRUCTED from the recorded adjacency the
orchestrator supplied (they share lot 70's south edges) because the pack carries
no outline for them; their BBLs and addresses are the real values. The synthetic
cross-street document is four lots around a cross street, for the clean
street-area test.

These documents are NOT written as ``fixtures/*.json`` on purpose: the location
and zoning map suites glob that folder, and a 1.1.0 document would pull them into
those snapshots. They live here in code instead (the brief: "build 1.1.0
documents by hand").
"""

from __future__ import annotations

import copy
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ..kit.kit_support import TOL, numbers_in, parse, pieces, resolve

SVG_NS = "{http://www.w3.org/2000/svg}"
# Raw source tokens that must NEVER appear in a drawn label (ruling Y7/X6; S5):
# URLs, the document's JSON pointers, dataset four-by-fours, ArcGIS field names.
FORBIDDEN_TOKENS = (
    "http", "://", "www.", ".json", "/map_context", "5zhs", "2jue", "nyzd", "nyco",
    "Streetwidth", "Street_NM", "ZONEDIST", "Shape__", "esri", "OBJECTID", "mapped_width_ft",
    "data-source", "EPSG", "DOITT", "BASE_BBL",
)

HERE = Path(__file__).resolve().parent
TESTS = HERE.parents[1]  # services/api/tests
BENCH = TESTS / "fixtures" / "benchmark_215_16_northern"
BLOCK = TESTS / "fixtures" / "benchmark_block_7334_lots_1_70"

MEASUREMENT = {"rank": "approximate_tax_map", "label": "Approximate — tax map"}
TAX_LOT_ATTR = ("Lot outlines from NYC Department of City Planning MapPLUTO 26v2; "
                "source edit date 2026-09-09.")
STREET_ATTR = ("Street centre lines from the NYC Digital City Map; "
               "source edit date 2025-12-01.")
BUILDING_ATTR = ("Building footprints from NYC Office of Technology and Innovation; "
                 "source edit date 2026-09-27.")
ZONING_UNAVAILABLE = {
    "status": "not_available",
    "reason": "Zoning-district boundaries are not drawn on the site-context plan.",
    "reason_kind": "source_unavailable",
}


def recorded_document() -> dict:
    """The REAL 1.1.0 ``map_context`` document for 215-16 Northern, assembled by
    the production provider from the recorded window pack (200 neighbouring lots,
    263 buildings, 35 street segments) - the data the report actually draws. The
    tests read the provider and the recorded pack; they never edit them."""
    from app.api.v1.report_context import recorded_pack_provider
    provider = recorded_pack_provider(
        TESTS / "fixtures" / "benchmark_215_16_northern_window",
        base_pack_dir=TESTS / "fixtures" / "benchmark_215_16_northern")
    doc = provider("4073340070", "test")
    assert doc is not None, "recorded pack provider returned None"
    return doc


def _features(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def _rings(path: Path) -> list[list[list[float]]]:
    return _features(path)[0]["geometry"]["rings"]


def _unit_south_normal(a: list[float], b: list[float]) -> tuple[float, float]:
    """Unit normal of edge a-b whose y points down (toward the street side south
    of lot 70's south edges)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    nx, ny = dy / length, -dx / length
    return (nx, ny) if ny < 0 else (-nx, -ny)


def _offset_quad(a: list[float], b: list[float], depth: float) -> list[list[float]]:
    """A closed parallelogram ring with top edge a-b and the far edge ``depth``
    feet to the south."""
    nx, ny = _unit_south_normal(a, b)
    c = [b[0] + nx * depth, b[1] + ny * depth]
    d = [a[0] + nx * depth, a[1] + ny * depth]
    return [list(a), list(b), c, d, list(a)]


def _bbox(ring: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def _window(ring: list[list[float]], pad: float) -> dict:
    xmin, ymin, xmax, ymax = _bbox(ring)
    return {"xmin": xmin - pad, "ymin": ymin - pad, "xmax": xmax + pad, "ymax": ymax + pad}


def _streets_entries() -> list[dict]:
    entries = []
    for feat in _features(BENCH / "dcm_street_centerline_lot_envelope_4073340070.json"):
        attrs = feat["attributes"]
        width_text = attrs["Streetwidth"]
        mapped = float(width_text) if width_text and width_text.isdigit() else None
        entries.append({
            "name": attrs["Street_NM"],
            "width_text": width_text,
            "mapped_width_ft": mapped,
            "paths": feat["geometry"]["paths"],
        })
    return entries


def _building_entries() -> list[dict]:
    feats = _features(BENCH / "building_footprints_lot_polygon_4073340070.json")
    return [{"outline": f["geometry"]["rings"]} for f in feats]


def benchmark_document() -> dict:
    """The recorded 215-16 Northern 1.1.0 document (ruling Y2), built by hand from
    the recorded pack plus the two constructed south neighbours."""
    lot70 = _rings(BENCH / "mappluto_lot_4073340070_epsg2263.json")
    lot1 = _rings(BLOCK / "mappluto_lot_4073340001_epsg2263.json")
    ext70 = lot70[0]
    # lot 70 south edges: P3->P4 (101.7 ft, shared with lot 11) and P4->P0 (2.22 ft,
    # near lot 61). Build lot 11 south of P3->P4 and lot 61 south of lot 1's south
    # edge (which ends at the shared P0 corner).
    p3, p4 = ext70[3], ext70[4]
    ext1 = lot1[0]
    q1 = ext1[1]  # lot 1 south-west corner
    lot11 = [_offset_quad(p3, p4, 92.0)]
    lot61 = [_offset_quad(q1, p4, 92.0)]
    streets_window = _window(ext70, 1000.0)
    context_window = _window(ext70, 400.0)
    return {
        "contract_version": "1.1.0",
        "document_kind": "map_context",
        "map_context": {
            "crs": "EPSG:2263",
            "units": "feet",
            "measurement": dict(MEASUREMENT),
            "subject_lot": {"bbl": "4073340070", "outline": lot70},
            "zoning_districts": dict(ZONING_UNAVAILABLE),
            "building_footprints": {
                "status": "available",
                "attribution": BUILDING_ATTR,
                "entries": _building_entries(),
            },
            "context_window": context_window,
            "tax_lots": {
                "status": "available",
                "attribution": TAX_LOT_ATTR,
                "entries": [
                    {"bbl": "4073340001", "address": "215-10 Northern Boulevard",
                     "outline": lot1},
                    {"bbl": "4073340011", "address": "45-12 215 Place", "outline": lot11},
                    {"bbl": "4073340061", "address": "45-11 215 Street", "outline": lot61},
                ],
            },
            "streets": {
                "status": "available",
                "attribution": STREET_ATTR,
                "window": streets_window,
                "entries": _streets_entries(),
            },
        },
    }


def _ring(pts: list[tuple[float, float]]) -> list[list[float]]:
    ring = [list(p) for p in pts]
    ring.append(list(pts[0]))
    return ring


def cross_street_document() -> dict:
    """Four lots around a cross street (S1): a horizontal street (y 90-110, named
    Cross Street, 60 ft) and a vertical one (x 90-110, Main Avenue, 50 ft). A
    fifth lot leaves a small gap no centre line runs through (drawn unnamed). A
    neighbour building sits on the north-west lot (so a building fill is drawn)."""
    nw = _ring([(10, 110), (90, 110), (90, 200), (10, 200)])
    ne = _ring([(110, 110), (190, 110), (190, 200), (110, 200)])
    sw = _ring([(10, 0), (90, 0), (90, 90), (10, 90)])
    se = _ring([(110, 0), (190, 0), (190, 90), (110, 90)])
    nw_building = _ring([(24, 124), (76, 124), (76, 186), (24, 186)])
    return {
        "contract_version": "1.1.0",
        "document_kind": "map_context",
        "map_context": {
            "crs": "EPSG:2263",
            "units": "feet",
            "measurement": dict(MEASUREMENT),
            "subject_lot": {"bbl": "4000010001", "outline": [ne]},
            "zoning_districts": dict(ZONING_UNAVAILABLE),
            "building_footprints": {
                "status": "available",
                "attribution": BUILDING_ATTR,
                "entries": [{"outline": [nw_building]}],
            },
            "context_window": {"xmin": 0, "ymin": 0, "xmax": 200, "ymax": 200},
            "tax_lots": {
                "status": "available",
                "attribution": TAX_LOT_ATTR,
                "entries": [
                    {"bbl": "4000010010", "address": "1 Cross Street", "outline": [nw]},
                    {"bbl": "4000010061", "address": "61 Main Avenue", "outline": [sw]},
                    {"bbl": "4000010011", "address": "11 Main Avenue", "outline": [se]},
                ],
            },
            "streets": {
                "status": "available",
                "attribution": STREET_ATTR,
                "window": {"xmin": -50, "ymin": -50, "xmax": 250, "ymax": 250},
                "entries": [
                    {"name": "Cross Street", "width_text": "60", "mapped_width_ft": 60.0,
                     "paths": [[[0, 100], [200, 100]]]},
                    {"name": "Main Avenue", "width_text": "60-75", "mapped_width_ft": None,
                     "paths": [[[100, 0], [100, 200]]]},
                ],
            },
        },
    }


def with_layer_unavailable(doc: dict, layer: str) -> dict:
    """A copy of ``doc`` with ``layer`` marked not_available (S6)."""
    out = copy.deepcopy(doc)
    out["map_context"][layer] = {
        "status": "not_available",
        "reason": f"The {layer.replace('_', ' ')} could not be retrieved for this area.",
        "reason_kind": "source_unavailable",
    }
    return out


def as_legacy(doc: dict) -> dict:
    """A copy of ``doc`` as a 1.0.0-shaped document: every optional 1.1.0 member
    removed, so the new drawings are honestly Unavailable (S6)."""
    out = copy.deepcopy(doc)
    out["contract_version"] = "1.0.0"
    for member in ("context_window", "tax_lots", "streets"):
        out["map_context"].pop(member, None)
    return out


def without_member(doc: dict, member: str) -> dict:
    """A copy of ``doc`` with an optional 1.1.0 member removed (e.g. to make a
    1.0.0-shaped document)."""
    out = copy.deepcopy(doc)
    out["map_context"].pop(member, None)
    return out


def legacy_1_0_0_document() -> dict:
    """A 1.0.0-shaped document: the benchmark with every optional 1.1.0 member
    removed, so the new drawings are honestly Unavailable and the location/zoning
    maps would be unchanged (S6)."""
    doc = benchmark_document()
    doc["contract_version"] = "1.0.0"
    for member in ("context_window", "tax_lots", "streets"):
        doc["map_context"].pop(member, None)
    # a 1.0.0 document carries real zoning + buildings; buildings stay available
    return doc


# --------------------------------------------------------------------------- #
# SVG checks (reused across the context-drawing tests).
# --------------------------------------------------------------------------- #
def drawn_texts(svg: str) -> list[str]:
    """Every drawn <text>'s content (tspans joined)."""
    out = []
    for el in parse(svg).iter(f"{SVG_NS}text"):
        out.append("".join(el.itertext()))
    return out


def texts_by_role(svg: str, role: str) -> list[str]:
    out = []
    for el in parse(svg).iter(f"{SVG_NS}text"):
        if el.get("data-role") == role:
            out.append("".join(el.itertext()))
    return out


def forbidden_tokens(svg: str) -> list[str]:
    """Any raw URL / field name / code word that leaked into a drawn label."""
    bad = []
    for text in drawn_texts(svg):
        for token in FORBIDDEN_TOKENS:
            if token in text:
                bad.append(f"{token!r} in {text!r}")
    return bad


def label_problems(svg: str, doc: dict) -> list[str]:
    """Check C-4 for the context drawings: every printed piece is either a
    no-number literal, or its number/value traces to the data via its source."""
    problems = []
    for source, text, role in pieces(parse(svg)):
        if source is None:
            if any(ch.isdigit() for ch in text):
                problems.append(f"unsourced number in {text!r}")
            continue
        if source == "scale":
            continue
        if source.startswith("edge:"):
            problems += _check_number(text, _edge_length(doc, source), source)
            continue
        value = resolve(doc, source)
        if role == "title":
            # the subtitle 'Queens, Block 7334, lot 70' derives its numbers from
            # the subject BBL (borough-block-lot); every number must match.
            bbl = str(value)
            allowed = {float(int(bbl[1:6])), float(int(bbl[6:]))} if len(bbl) == 10 else set()
            for n in numbers_in(text):
                if not any(abs(n - a) <= TOL for a in allowed):
                    problems.append(f"{text!r}: number {n} not from bbl {bbl!r}")
        elif role == "lot_number":
            expected = f"Lot {int(str(value)[-4:])}"
            if text != expected:
                problems.append(f"{text!r} is not {expected!r} for bbl {value!r}")
        elif isinstance(value, bool):
            problems.append(f"{text!r}: boolean source {source}")
        elif isinstance(value, int | float):
            problems += _check_number(text, float(value), source)
        else:  # a string source (street name in CAPS, address, bbl in the title)
            flat = " ".join(str(value).split())
            if text in (flat, flat.upper()):
                continue
            head = text[: len(text) - len(flat)]
            if not text.endswith(flat) or any(ch.isdigit() for ch in head):
                problems.append(f"{text!r} does not match source {source} = {flat!r}")
    return problems


def _check_number(text: str, expected: float, source: str) -> list[str]:
    printed = numbers_in(text)
    if len(printed) != 1 or abs(printed[0] - expected) > max(TOL, 0.01 * abs(expected)):
        return [f"{text!r} does not print {expected} ({source})"]
    return []


def _edge_length(doc: dict, source: str) -> float:
    pointer, index = source[len("edge:"):].split("#")
    ring = resolve(doc, pointer)
    (ax, ay), (bx, by) = ring[int(index)], ring[int(index) + 1]
    return math.hypot(bx - ax, by - ay)


def note_labels(drawing) -> list:
    return [lbl for lbl in drawing.labels if lbl.role == "note"]


def report_too_big(svg: str) -> bool:
    root = ET.fromstring(svg)
    return float(root.get("width")) > 515.9 or float(root.get("height")) > 425.2


def summary_too_big(svg: str) -> bool:
    """True if the summary frame exceeds 88 mm by 72 mm (249.45 pt by 204.09 pt)."""
    root = ET.fromstring(svg)
    return float(root.get("width")) > 249.5 or float(root.get("height")) > 204.1


# Source names / dates / dataset ids that the SUMMARY notes must NOT carry (the
# report composes those from the provenance; the summary notes are plain).
SOURCE_TOKENS = ("MapPLUTO", "Digital City Map", "Building footprints", "Open Data", "OTI",
                 "5zhs", "2026-", "2025-", "edit date", "Department of City Planning")


def summary_note_leaks(drawing) -> list[str]:
    joined = " ".join(lbl.text for lbl in note_labels(drawing))
    return [tok for tok in SOURCE_TOKENS if tok in joined]


_SVG_POINT = re.compile(r"[ML](-?[\d.]+) (-?[\d.]+)")


def street_area_polys(svg: str) -> list[list[tuple[float, float]]]:
    """The screen-space exterior rings of every drawn STREET-AREA fill (the fill
    path carrying a '#gap-' data-source; the hatch overlay fill='url(...)' is
    skipped)."""
    out = []
    for el in parse(svg).iter(f"{SVG_NS}path"):
        src = el.get("data-source") or ""
        if "#gap-" not in src or (el.get("fill") or "").startswith("url("):
            continue
        for part in (el.get("d") or "").split("Z"):
            pts = _SVG_POINT.findall(part)
            if len(pts) >= 3:
                out.append([(float(x), float(y)) for x, y in pts])
    return out


def labels_below(svg: str, min_pt: float) -> list[tuple[str, float]]:
    bad = []
    for el in parse(svg).iter(f"{SVG_NS}text"):
        if float(el.get("font-size")) < min_pt:
            bad.append(("".join(el.itertext()), float(el.get("font-size"))))
    return bad
