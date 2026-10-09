"""Corner-reach area (M5-T145 PART A): acceptance scenarios S1 to S8.

Offline and deterministic. The real benchmark lot (215-16 Northern Blvd, BBL 4073340070) is
replayed through the recorded pack (_northern_replay); the made-up shapes are built directly.
Every benchmark figure is PARSED from the independent reference case
(docs/reference-cases/R6B/cases/step-p6-worked.json) -- never retyped and never taken from the
module under test. The made-up S1/S2/S3 figures are the hand arithmetic written out in the
scenarios.

Benchmark tolerance (scenario S4, ruling C5): the two step-P6 readings differ by at most
0.14 sq ft on the corner portion and 0.13 sq ft on the interior strip, and agree on the outline
area (10,387.99). The test asserts the program's two areas are within 1.0 sq ft of BOTH
readings (about seven times the readings' own spread, ~0.01% of the lot) and that the two
portions sum to the readings' outline area within 0.01 sq ft. It pins no single figure. If the
program's area is not within 1.0 sq ft of both readings the builder STOPS and reports the gap;
the tolerance is never widened (ruling C5). The measured gap is recorded in the part-A report.
"""

from __future__ import annotations

import ast
import json
import math
import pathlib
import re

import pytest

from app.spatial import corner_reach_area
from app.spatial.corner_reach_area import (
    area_within_distance_of_both,
    measure_corner_reach_area,
)
from app.spatial.site_geometry import (
    LotOutline,
    StreetCenterline,
    StreetData,
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.labels import LABEL_TAX_MAP, LABEL_UNKNOWN
from app.spatial.site_geometry.outline import prepare_outline
from app.spatial.site_geometry.results import FRONTAGE_CONFIRMED

from ._northern_replay import DCM_ENVELOPE, replay_dcm_page, replay_lot_geometry

CRS = {"wkid": 102718, "latest_wkid": 2263}
ENVELOPE = (-1000.0, -1000.0, 1000.0, 1000.0)
DISTANCE_FT = 100.0
AREA_TOL_FT = 1.0  # ruling C5: within 1.0 sq ft of BOTH readings, never widened
SUM_TOL_FT = 0.01  # corner + interior == the readings' outline area

_CASE = (pathlib.Path(__file__).resolve().parents[4]
         / "docs" / "reference-cases" / "R6B" / "cases" / "step-p6-worked.json")


# --------------------------------------------------------------------------- reference parsing


def _rows() -> dict:
    data = json.loads(_CASE.read_text(encoding="utf-8"))
    return {row["row_id"]: row for row in data["rows"]}


def _num(text: str) -> float:
    return float(text.replace(",", ""))


def _coverage_readings() -> tuple[list[float], list[float], float]:
    """Both readings' corner and interior areas and the outline area, parsed from the
    independent case row real-lot-coverage-by-portion (never retyped)."""
    row = _rows()["real-lot-coverage-by-portion"]
    assert row["expected"]["kind"] == "not_known"
    reason = row["expected"]["reason"]
    corner_text = reason[reason.index("corner-lot portion"):reason.index("interior-lot portion")]
    interior_text = reason[reason.index("interior-lot portion"):]
    corner = [_num(m) for m in re.findall(r"measures ([\d,]+\.\d+) sq ft", corner_text)]
    interior = [_num(m) for m in re.findall(r"measures ([\d,]+\.\d+) sq ft", interior_text)]
    assert len(corner) == 2 and len(interior) == 2, (corner, interior)
    fact = next(f for f in row["facts_used"] if f["name"] == "Measured outline area")
    outline = _num(re.search(r"([\d,]+\.\d+) sq ft", fact["value"]).group(1))
    return corner, interior, outline


# --------------------------------------------------------------------------- offline builders


def _lot(points) -> LotOutline:
    return LotOutline(tuple(points), CRS, "synthetic tax-lot")


def _street_for_edge(key, a, b, width="60", *, extra_offset=0.0, extend=300.0) -> StreetCenterline:
    """A center line parallel to the counterclockwise lot edge a->b, half the mapped width
    outside it (the premise of app.spatial.site_geometry.adjacency; mirrors test_lot_reach)."""
    length = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = uy, -ux
    offset = float(width) / 2.0 + extra_offset
    start = (a[0] - ux * extend + nx * offset, a[1] - uy * extend + ny * offset)
    end = (b[0] + ux * extend + nx * offset, b[1] + uy * extend + ny * offset)
    return StreetCenterline(key, key, None, ((start, end),), width, True)


def _streets(*centerlines) -> StreetData:
    return StreetData(tuple(centerlines), ENVELOPE, CRS, "synthetic streets")


def _joined(first: StreetCenterline, second: StreetCenterline):
    """One bent center line: both pieces extended to where their lines meet (mirrors
    test_lot_reach's bent-frontage builder)."""
    (a0, a1), (b0, b1) = first.paths[0], second.paths[0]
    da = (a1[0] - a0[0], a1[1] - a0[1])
    db = (b1[0] - b0[0], b1[1] - b0[1])
    denom = da[0] * db[1] - da[1] * db[0]
    t = ((b0[0] - a0[0]) * db[1] - (b0[1] - a0[1]) * db[0]) / denom
    meet = (a0[0] + da[0] * t, a0[1] + da[1] * t)
    far_a = (a0[0] - da[0] * 5, a0[1] - da[1] * 5)
    far_b = (b1[0] + db[0] * 5, b1[1] + db[1] * 5)
    return (far_a, meet, far_b)


def _measure(points, *centerlines):
    lot = _lot(points)
    geometry = derive_site_geometry(lot, _streets(*centerlines))
    prepared, _reason = prepare_outline(lot)
    return geometry, measure_corner_reach_area(prepared, geometry, DISTANCE_FT)


# --------------------------------------------------------------------------- S1 right-angle lot


def test_s1_right_angle_corner_lot_wider_than_the_distance():
    # outline (0,0),(130,0),(130,80),(0,80); street line 1 = y=0; street line 2 = x=0.
    outline = [(0.0, 0.0), (130.0, 0.0), (130.0, 80.0), (0.0, 80.0)]
    line1 = ((0.0, 0.0), (1.0, 0.0))  # y = 0, the 130-ft frontage
    line2 = ((0.0, 0.0), (0.0, 1.0))  # x = 0, the 80-ft frontage
    corner, rest = area_within_distance_of_both(outline, line1, line2, 100.0)
    # Hand arithmetic (scenario S1): corner = [0,100]x[0,80] = 8,000; rest = 30 x 80 = 2,400.
    assert corner == pytest.approx(8000.0, abs=1e-6)
    assert rest == pytest.approx(2400.0, abs=1e-6)
    assert corner + rest == pytest.approx(10400.0, abs=1e-6)


# --------------------------------------------------------------------------- S2 measured zero


def test_s2_lot_wholly_inside_the_distance_has_a_measured_zero_rest():
    # Pure arithmetic (scenario S2): the whole 80x60 lot is within 100 ft of both lines.
    outline = [(0.0, 0.0), (80.0, 0.0), (80.0, 60.0), (0.0, 60.0)]
    corner, rest = area_within_distance_of_both(
        outline, ((0.0, 0.0), (1.0, 0.0)), ((0.0, 0.0), (0.0, 1.0)), 100.0)
    assert corner == pytest.approx(4800.0, abs=1e-6)
    assert rest == pytest.approx(0.0, abs=1e-6)
    # Through the measure path the measured zero is a KNOWN value, distinct from unknown.
    points = [(0.0, 0.0), (80.0, 0.0), (80.0, 60.0), (0.0, 60.0)]
    street_a = _street_for_edge("Street A", (0.0, 0.0), (80.0, 0.0))
    street_b = _street_for_edge("Street B", (0.0, 60.0), (0.0, 0.0))
    geometry, result = _measure(points, street_a, street_b)
    assert geometry.lot_type.kind == "corner"
    assert result.corner_portion.value == pytest.approx(4800.0, abs=SUM_TOL_FT)
    assert result.interior_portion.known is True
    assert result.interior_portion.value == pytest.approx(0.0, abs=SUM_TOL_FT)
    assert result.interior_portion.label == LABEL_TAX_MAP  # measured zero, not unknown


# --------------------------------------------------------------------------- S3 non-right angle


def test_s3_non_right_angle_corner_distance_is_perpendicular():
    # Parallelogram as written in scenario S3: 130-ft side on street line 1 (y=0) and an 80-ft
    # side leaving (0,0) at 60 degrees as street line 2.
    outline = [(0.0, 0.0), (130.0, 0.0), (170.0, 69.2820), (40.0, 69.2820)]
    line1 = ((0.0, 0.0), (1.0, 0.0))  # y = 0
    seg_len = math.hypot(40.0, 69.2820)
    line2 = ((0.0, 0.0), (40.0 / seg_len, 69.2820 / seg_len))  # 60 degrees from (0,0)
    corner, rest = area_within_distance_of_both(outline, line1, line2, 100.0)
    total = _polygon_area_of(outline)  # the parallelogram's own area (its vertices), ~9,006.66
    # Hand arithmetic (scenario S3): the corner portion is 80 x 100 = 8,000 measured
    # perpendicular to street line 2; the rest is the whole lot minus 8,000. The scenario's
    # vertex (40, 69.2820) makes the side 79.99998 ft, so the clip is 7999.997 -- 8,000.00 to
    # the 0.01 sq ft output precision; a wrong-axis measurement would be off by thousands.
    assert corner == pytest.approx(8000.0, abs=SUM_TOL_FT)
    assert rest == pytest.approx(total - 8000.0, abs=SUM_TOL_FT)
    assert corner + rest == pytest.approx(total, abs=1e-6)
    assert total == pytest.approx(9006.66, abs=1e-2)


def _polygon_area_of(ring) -> float:
    total = 0.0
    count = len(ring)
    for i in range(count):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % count]
        total += x0 * y1 - x1 * y0
    return abs(total) / 2.0


# --------------------------------------------------------------------------- S4 benchmark lot


def test_s4_benchmark_lot_within_tolerance_of_both_readings():
    corner_readings, interior_readings, outline_area = _coverage_readings()
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    assert geometry.lot_type.kind == "corner"
    result = measure_corner_reach_area(prepared, geometry, DISTANCE_FT)

    assert result.corner_portion.label == LABEL_TAX_MAP
    assert result.interior_portion.label == LABEL_TAX_MAP
    got_corner = result.corner_portion.value
    got_interior = result.interior_portion.value
    for reading in corner_readings:
        assert got_corner == pytest.approx(reading, abs=AREA_TOL_FT), \
            f"corner portion {got_corner} not within {AREA_TOL_FT} of reading {reading}"
    for reading in interior_readings:
        assert got_interior == pytest.approx(reading, abs=AREA_TOL_FT), \
            f"interior portion {got_interior} not within {AREA_TOL_FT} of reading {reading}"
    assert got_corner + got_interior == pytest.approx(outline_area, abs=SUM_TOL_FT), \
        f"corner + interior {got_corner + got_interior} not within {SUM_TOL_FT} of {outline_area}"


# --------------------------------------------------------------------------- S5 no outline


def test_s5_no_outline_both_areas_unknown_never_zero():
    lot = _lot([(0.0, 0.0), (10.0, 0.0)])  # two points: the outline is refused
    geometry = derive_site_geometry(lot, _streets())
    prepared, reason = prepare_outline(lot)
    assert prepared is None and reason
    result = measure_corner_reach_area(prepared, geometry, DISTANCE_FT)
    assert result.corner_portion.value is None
    assert result.corner_portion.label == LABEL_UNKNOWN
    assert result.interior_portion.value is None
    assert result.interior_portion.label == LABEL_UNKNOWN
    assert result.corner_portion.reason


# --------------------------------------------------------------------------- S6 one frontage


def test_s6_one_confirmed_straight_frontage_split_unknown():
    # A corner lot whose First Avenue center line is 16 ft off: that side is uncertain, leaving
    # one confirmed straight frontage, so there is no corner to measure within the distance.
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    first = _street_for_edge("First Avenue", (0.0, 100.0), (0.0, 0.0), "80", extra_offset=16.0)
    _geometry, result = _measure(points, main, first)
    assert result.corner_portion.value is None and result.interior_portion.value is None
    assert result.corner_portion.label == LABEL_UNKNOWN
    assert "Only Main Street has a confirmed, straight frontage" in result.corner_portion.reason


# --------------------------------------------------------------------------- S7 not a corner


def test_s7_two_streets_not_meeting_at_a_corner_split_unknown():
    # A through lot: two confirmed straight frontages on opposite sides, no corner.
    points = [(0.0, 0.0), (25.0, 0.0), (25.0, 100.0), (0.0, 100.0)]
    main = _street_for_edge("Main Street", (0.0, 0.0), (25.0, 0.0))
    back = _street_for_edge("Back Street", (25.0, 100.0), (0.0, 100.0), "50")
    geometry, result = _measure(points, main, back)
    assert geometry.lot_type.kind == "through"
    assert result.corner_portion.value is None and result.interior_portion.value is None
    assert "do not meet at a corner" in result.corner_portion.reason


# --------------------------------------------------------------------------- S8 bent frontage


def test_s8_bent_frontage_split_unknown():
    bend = math.radians(30.0)
    corner = (50.0 + 40.0 * math.cos(bend), 40.0 * math.sin(bend))
    back = (corner[0] - 80.0 * math.sin(bend), corner[1] + 80.0 * math.cos(bend))
    points = [(0.0, 0.0), (50.0, 0.0), corner, back, (0.0, 80.0)]
    first = _street_for_edge("Bend Street", (0.0, 0.0), (50.0, 0.0), extend=0.0)
    second = _street_for_edge("Bend Street", (50.0, 0.0), corner, extend=0.0)
    joined = StreetCenterline("Bend Street", "Bend Street", None, (_joined(first, second),),
                              "60", True)
    geometry, result = _measure(points, joined)
    assert geometry.frontage("Bend Street").status == FRONTAGE_CONFIRMED  # confirmed but bends
    assert result.corner_portion.value is None and result.interior_portion.value is None
    assert "not straight" in result.corner_portion.reason


# --------------------------------------------------------------------------- measurements only


def test_module_names_no_legal_rule_or_threshold():
    source = pathlib.Path(corner_reach_area.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    for token in ("100", "80", "135"):
        assert token not in source, f"the module names the legal constant {token!r}"
    for token in ("zr ", "zoning", "coverage", "12-10", "23-362", "yard"):
        assert token not in lowered, f"the module names {token!r}"
    assert "app.rules" not in source and "app.scenario" not in source
    # It may name lot_reach in prose (it stands beside it) but must not import it: check the
    # actual import statements, not the text, so the docstring reference does not false-match.
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imported.add(module)
            imported.update(f"{module}.{alias.name}" for alias in node.names)
    assert not any("lot_reach" in name for name in imported), "the module imports lot_reach"
    assert any("app.rules" not in name and "app.scenario" not in name for name in imported)
    assert imported  # sanity: the source really was read


def test_no_app_module_imports_corner_reach_area_yet():
    # Nothing this part adds is reachable from a reported result: no OTHER app module may name
    # corner_reach_area until the later wiring step connects it.
    app_root = pathlib.Path(corner_reach_area.__file__).resolve().parents[1]  # services/api/app
    offenders = [
        str(path) for path in app_root.rglob("*.py")
        if path.name != "corner_reach_area.py"
        and "corner_reach_area" in path.read_text(encoding="utf-8")
    ]
    assert offenders == [], f"these app modules already reference corner_reach_area: {offenders}"
