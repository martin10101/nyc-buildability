"""M5-T152 (S2, S3, S6): the report frame of the site plan, the massing and the floor-stack
section.

S2 - render_site_plan(frame='report'): no notes column; the legend only for what is drawn; street
names beside their frontages; the outline's edge dimensions; north and scale bar; at most 182 mm by
150 mm; every label at least 7 pt at that size; no two labels overlap; the default (sheet) frame
stays byte-identical.
S3 - render_floor_stack: one band per scheduled storey; every number drawn is in the schedule; the
minimum base height line only where the document gives it; the caption says it is drawn from the
schedule with no placement on the lot.
S6 - no text in the report-frame drawings holds a field or code word (any snake_case word).
"""

from __future__ import annotations

import re

import pytest

from app.drawings.kit import (
    Drawing,
    Unavailable,
    render_floor_stack,
    render_massing,
    render_site_plan,
)

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    SVG_NS,
    fixture_paths,
    label_problems,
    load,
    numbers_in,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    texts,
)

# A4 at 14 mm margins: a report drawing is at most 182 mm (515.9 pt) wide by 150 mm (425.2 pt) high.
MAX_W_PT = 515.9
MAX_H_PT = 425.2
MIN_LABEL_PT = 7.0
_SNAKE = re.compile(r"[A-Za-z]+_[A-Za-z_]+")

FIXTURES = fixture_paths()
IDS = [p.stem for p in FIXTURES]
_TWO_BUILDING = [
    "recorded_215_16_northern_journey",
    "synthetic_building_alternatives_contract_1_4_0",
    "synthetic_coverage_by_portion_available_contract_1_4_0",
]


def _size(svg: str) -> tuple[float, float]:
    root = parse(svg)
    return float(root.get("width")), float(root.get("height"))


def labels_below(svg: str, min_pt: float) -> list[tuple[str, float]]:
    """Every printed text whose font-size is below ``min_pt`` points (1 user unit = 1 pt at the
    printed size). The report-frame label-legibility check and its mutation probe."""
    bad = []
    for el, text in texts(parse(svg)):
        size = float(el.get("font-size"))
        if size < min_pt:
            bad.append((text, size))
    return bad


def snake_case_texts(svg: str) -> list[str]:
    """Printed texts that hold a snake_case field or code word (S6)."""
    return [text for _el, text in texts(parse(svg)) if _SNAKE.search(text)]


# =========================================================================== S2 (site plan)
@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_s2_site_plan_report_fits_a4_and_is_legible(path):
    doc = load(path)
    drawing = render_site_plan(doc, frame="report", env=ENV_ON)
    assert isinstance(drawing, Drawing)
    w, h = _size(drawing.svg)
    assert w <= MAX_W_PT and h <= MAX_H_PT, (w, h)
    assert labels_below(drawing.svg, MIN_LABEL_PT) == []
    assert overlapping_labels(drawing.svg) == []
    # No notes column: the report-frame site plan draws no 'note' text.
    assert [t for el, t in texts(parse(drawing.svg)) if el.get("data-role") == "note"] == []
    # Every number is read from the results (dimensions are the outline's edge lengths).
    assert label_problems(drawing.svg, doc) == []
    assert numbers_not_in_input(drawing.svg, doc) == []


@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_s2_site_plan_default_frame_is_byte_identical_to_sheet(path):
    doc = load(path)
    assert render_site_plan(doc, env=ENV_ON) == render_site_plan(doc, frame="sheet", env=ENV_ON)


def test_s2_mutation_a_label_shrunk_below_7pt_is_caught():
    """MUTATION PROOF (S2): a report-frame label shrunk below 7 pt is caught by ``labels_below``."""
    drawing = render_site_plan(load(FIXTURES[0]), frame="report", env=ENV_ON)
    assert labels_below(drawing.svg, MIN_LABEL_PT) == []
    shrunk = drawing.svg.replace('font-size="9.00"', 'font-size="6.50"', 1)
    if shrunk == drawing.svg:  # a fixture with no 9 pt street label: shrink a legend label
        shrunk = drawing.svg.replace('font-size="8.00"', 'font-size="6.50"', 1)
    assert labels_below(shrunk, MIN_LABEL_PT)


# =========================================================================== S2 (massing)
@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_s2_massing_report_fits_a4_and_is_legible(path):
    doc = load(path)
    drawing = render_massing(doc, frame="report", env=ENV_ON)
    if isinstance(drawing, Unavailable):
        return  # this fixture has no floor plates to mass (the benchmark: no placement worked)
    w, h = _size(drawing.svg)
    assert w <= MAX_W_PT and h <= MAX_H_PT, (w, h)
    assert labels_below(drawing.svg, MIN_LABEL_PT) == []
    assert overlapping_labels(drawing.svg) == []
    assert [t for el, t in texts(parse(drawing.svg)) if el.get("data-role") == "note"] == []


# =========================================================================== S6
@pytest.mark.parametrize("path", FIXTURES, ids=IDS)
def test_s6_no_field_or_code_word_in_the_report_drawings(path):
    doc = load(path)
    for drawing in (render_site_plan(doc, frame="report", env=ENV_ON),
                    render_massing(doc, frame="report", env=ENV_ON)):
        if isinstance(drawing, Drawing):
            assert snake_case_texts(drawing.svg) == []


# =========================================================================== S3 (floor stack)
def _alternatives():
    cases = []
    for stem in _TWO_BUILDING:
        doc = load(CONTRACT_FIXTURES / f"{stem}.json")
        for alt in doc.get("building_alternatives", []):
            cases.append((f"{stem}:{alt['building']}", alt))
    return cases


ALT_CASES = _alternatives()
ALT_IDS = [cid for cid, _ in ALT_CASES]


@pytest.mark.parametrize(("_id", "alternative"), ALT_CASES, ids=ALT_IDS)
def test_s3_floor_stack_one_band_per_storey_from_the_schedule(_id, alternative):
    drawing = render_floor_stack(alternative, env=ENV_ON)
    assert isinstance(drawing, Drawing)
    root = parse(drawing.svg)
    w, h = _size(drawing.svg)
    assert w <= MAX_W_PT and h <= MAX_H_PT, (w, h)
    assert labels_below(drawing.svg, MIN_LABEL_PT) == []
    assert overlapping_labels(drawing.svg) == []

    # One storey band per scheduled storey.
    bands = [p for p in root.iter(f"{SVG_NS}path") if p.get("data-storey")]
    assert len(bands) == len(alternative["floor_schedule"])

    # Every number drawn is a figure of this building's schedule (S3 / check C-4 for the section).
    schedule_numbers = {round(float(v), 2)
                        for row in alternative["floor_schedule"] for v in row.values()}
    for _el, text in texts(root):
        for value in numbers_in(text):
            assert any(abs(value - s) <= 0.01 for s in schedule_numbers), (text, value)

    # The caption says it is drawn from the schedule with no placement on the lot.
    captions = [t for el, t in texts(root) if el.get("data-role") == "caption"]
    assert captions == ["Drawn from the floor schedule; no placement on the lot."]

    # The minimum base height line appears ONLY where the document gives it (a to_min_base building
    # reaches the minimum base height at its building height); a 'widest' building draws none.
    min_base = [t for el, t in texts(root) if el.get("data-role") == "floor_stack_min_base"]
    assert bool(min_base) == (alternative["fill_rule"] == "to_min_base")


def test_s3_floor_stack_unavailable_without_a_schedule():
    assert isinstance(render_floor_stack({"floor_schedule": []}, env=ENV_ON), Unavailable)
