"""M5-T192 (part B2 of M5-T173): the section height-limit lines.

The floor-stack section gains the STANDARD height limits (minimum base, maximum base, maximum
building height) the document carries in ``answers.permitted_envelope``, drawn as dashed reference
lines through an opt-in keyword. Nothing is computed; nothing is compared with the building; nothing
is read from ``envelope_rows``. Without the keyword the section is byte-identical to today's.

The expected HEIGHTS are literals grounded in the reference case ``real-lot.json`` row L3 and the
ZR 23-432 capture (``zr-23-432.snapshot.json``), never a program run. The label PROSE is read from
the fixture at test time (a later wording pass may reword it; the numbers stay literal).
"""

from __future__ import annotations

import math
import re

import pytest

from app.drawings.kit import render_floor_stack
from app.drawings.kit.section import draw_floor_stack
from app.drawings.kit.section_legal_lines import LegalLine, section_legal_lines

from .kit_support import (
    CONTRACT_FIXTURES,
    ENV_ON,
    SVG_NS,
    load,
    numbers_in,
    numbers_not_in_input,
    overlapping_labels,
    parse,
    resolve,
    texts,
)

BENCHMARK = CONTRACT_FIXTURES / "recorded_215_16_northern_journey.json"
DOC_1_4_0 = CONTRACT_FIXTURES / "synthetic_building_alternatives_contract_1_4_0.json"

MAX_W_PT = 515.9
MAX_H_PT = 260.0
MIN_LABEL_PT = 7.0

# The STANDARD R6B heights, in feet, from reference case real-lot.json row L3 (ZR 23-432 table,
# snapshot zr-23-432): minimum base 30 ft, maximum base 45 ft, maximum building 55 ft. Independent
# of any program output.
EXPECTED_HEIGHT_FT = {
    "min_base_height": 30.0,
    "max_base_height": 45.0,
    "max_building_height": 55.0,
}


def _point_ys(path_d: str) -> list[float]:
    return [float(y) for _, y in re.findall(r"[ML]([\d.-]+) ([\d.-]+)", path_d)]


def _legal_texts(root) -> list[tuple[str, str]]:
    """(data-source, text) of every drawn legal-line label."""
    return [
        (el.get("data-source"), "".join(el.itertext()))
        for el in root.iter(f"{SVG_NS}text")
        if el.get("data-role") == "floor_stack_legal_line"
    ]


# --------------------------------------------------------------------------- S1
def test_s1_default_render_is_byte_identical_without_results():
    """render_floor_stack / draw_floor_stack without ``results``/``legal_lines`` is unchanged."""
    doc = load(BENCHMARK)
    alt = doc["building_alternatives"][0]
    assert render_floor_stack(alt, env=ENV_ON).svg == draw_floor_stack(alt, caption=False).svg


def test_s1_legal_lines_none_is_byte_identical():
    doc = load(BENCHMARK)
    alt = doc["building_alternatives"][0]
    assert draw_floor_stack(alt, caption=False, legal_lines=None).svg == draw_floor_stack(
        alt, caption=False
    ).svg


# --------------------------------------------------------------------------- S2
def test_s2_benchmark_draws_the_three_standard_height_lines():
    doc = load(BENCHMARK)
    alt = doc["building_alternatives"][0]
    drawing = render_floor_stack(alt, env=ENV_ON, results=doc)
    root = parse(drawing.svg)

    # The document's own label prose (read at test time), with the reference-case number appended.
    entries = {v["key"]: v for v in doc["answers"]["permitted_envelope"]["values"]}
    expected = {
        f"{entries[key]['label']} {int(ft)} ft"
        for key, ft in EXPECTED_HEIGHT_FT.items()
    }
    drawn = {text for _src, text in _legal_texts(root)}
    assert drawn == expected
    assert drawn == {
        "Minimum base height 30 ft",
        "Maximum base height 45 ft",
        "Maximum building height 55 ft",
    }

    # Every number printed is a document number (check C-4); the storey tops stay.
    assert numbers_not_in_input(drawing.svg, doc) == []
    tops = {t for el, t in texts(root) if el.get("data-role") == "floor_stack_top"}
    assert tops == {"10 ft", "20 ft", "30 ft"}

    # Compact: at most 260 pt tall, at most 515.9 pt wide.
    w, h = float(root.get("width")), float(root.get("height"))
    assert w <= MAX_W_PT and h <= MAX_H_PT, (w, h)

    # Every label at least 7 pt, and none overlaps another.
    assert min(float(el.get("font-size")) for el in root.iter(f"{SVG_NS}text")) >= MIN_LABEL_PT
    assert overlapping_labels(drawing.svg) == []


def test_s2_every_line_number_is_the_document_value_at_its_source():
    """Provenance: each legal line's data-source resolves to exactly the number it prints."""
    doc = load(BENCHMARK)
    alt = doc["building_alternatives"][0]
    root = parse(render_floor_stack(alt, env=ENV_ON, results=doc).svg)
    seen = []
    for source, text in _legal_texts(root):
        assert source is not None
        printed = numbers_in(text)
        assert len(printed) == 1
        assert math.isclose(printed[0], float(resolve(doc, source)), abs_tol=1e-9)
        seen.append(printed[0])
    assert sorted(seen) == [30.0, 45.0, 55.0]


def test_s2_one_line_where_the_minimum_base_coincides_with_the_building_top():
    """The to_min_base building tops out at 30 ft and the minimum base height is 30 ft, so ONE
    dashed line sits at 30 ft, carrying the document value; no bare 'Minimum base height' label."""
    doc = load(BENCHMARK)
    alt = doc["building_alternatives"][0]
    assert alt["fill_rule"] == "to_min_base"
    root = parse(render_floor_stack(alt, env=ENV_ON, results=doc).svg)

    bare = [t for el, t in texts(root) if el.get("data-role") == "floor_stack_min_base"]
    assert bare == []  # the bare reference line is not drawn a second time

    dashed = [
        p for p in root.iter(f"{SVG_NS}path") if p.get("stroke-dasharray") == "4.00 2.00"
    ]
    assert len(dashed) == 3  # exactly the three legal lines, not four (no duplicate at 30 ft)

    # The 30 ft line sits at the grade-nearest y (a dashed line is horizontal, so one y per line);
    # exactly one dashed line sits there.
    line_ys = [_point_ys(p.get("d"))[0] for p in dashed]
    at_building_top = max(line_ys)  # nearest grade = largest y = the 30 ft line
    assert sum(1 for y in line_ys if math.isclose(y, at_building_top, abs_tol=1e-6)) == 1


# --------------------------------------------------------------------------- S3
def _value(**overrides) -> dict:
    base = {
        "key": "min_base_height",
        "label": "Minimum base height",
        "value": 30.0,
        "unit": "feet",
        "zr_sections": ["ZR 23-432"],
        "sources": [{"kind": "rule_table", "ref": "r6b-height@0.1.0-draft"}],
        "exception_label": None,
    }
    base.update(overrides)
    return base


def _doc(values: list[dict], status: str = "available") -> dict:
    return {"answers": {"permitted_envelope": {"status": status, "values": values}}}


# One state per row (S3): each must DROP the offending line, never default it.
_DROP_STATES = [
    ("whole answer not available", _doc([_value()], status="not_available")),
    ("no answers block", {}),
    ("no permitted_envelope", {"answers": {}}),
    ("values not a list", {"answers": {"permitted_envelope": {"status": "available"}}}),
    ("value is NaN", _doc([_value(value=float("nan"))])),
    ("value is +inf", _doc([_value(value=float("inf"))])),
    ("value is negative", _doc([_value(value=-10.0)])),
    ("value is a string", _doc([_value(value="30")])),
    ("value is a boolean", _doc([_value(value=True)])),
    ("unit is not feet", _doc([_value(unit="stories")])),
    ("label is empty", _doc([_value(label="  ")])),
    (
        "only qualifying-housing keys",
        _doc(
            [
                _value(key="min_base_height_qualifying_affordable_or_senior"),
                _value(
                    key="max_building_height_qualifying_affordable_or_senior", value=65.0,
                    label="Maximum building height with qualifying affordable or senior housing",
                ),
            ]
        ),
    ),
]


@pytest.mark.parametrize(("name", "doc"), _DROP_STATES, ids=[n for n, _ in _DROP_STATES])
def test_s3_malformed_or_absent_state_yields_no_line(name, doc):
    assert section_legal_lines(doc) is None


def test_s3_a_single_bad_key_drops_only_that_line():
    doc = _doc(
        [
            _value(value=float("nan")),  # min_base dropped
            _value(key="max_base_height", label="Maximum base height", value=45.0),
            _value(key="max_building_height", label="Maximum building height", value=55.0),
        ]
    )
    lines = section_legal_lines(doc)
    assert lines is not None
    assert [line.key for line in lines] == ["max_base_height", "max_building_height"]
    assert all(line.value_ft in (45.0, 55.0) for line in lines)


def test_s3_reader_returns_the_document_label_zr_sections_and_source():
    doc = load(BENCHMARK)
    lines = section_legal_lines(doc)
    assert lines is not None
    assert [line.key for line in lines] == [
        "min_base_height",
        "max_base_height",
        "max_building_height",
    ]
    by_key = {line.key: line for line in lines}
    for key, ft in EXPECTED_HEIGHT_FT.items():
        assert by_key[key].value_ft == ft
        assert by_key[key].zr_sections == ("ZR 23-432",)
        assert resolve(doc, by_key[key].source) == ft
    assert all(isinstance(line, LegalLine) for line in lines)


# --------------------------------------------------------------------------- S4
def test_s4_envelope_rows_never_become_a_line():
    """envelope_rows carry street-wall / setback / side-yard STATES, not heights: the reader reads
    only permitted_envelope and no rule is evaluated."""
    doc = _doc([_value(), _value(key="max_base_height", label="Maximum base height", value=45.0)])
    doc["envelope_rows"] = [
        {"kind": "setback", "state": "applies", "above_ft": 60.0},
        {"kind": "setback", "state": "not_applicable"},
        {"kind": "street_wall", "state": "applies", "height_ft": 40.0},
        {"kind": "side_yard", "state": "not_applicable"},
    ]
    lines = section_legal_lines(doc)
    assert [line.key for line in lines] == ["min_base_height", "max_base_height"]
    assert all(line.value_ft in (30.0, 45.0) for line in lines)  # never 40 or 60 from the rows


def test_s4_envelope_rows_alone_draw_no_line():
    doc = {
        "answers": {"permitted_envelope": {"status": "not_available", "reason": "x",
                                           "reason_kind": "missing_input"}},
        "envelope_rows": [{"kind": "setback", "state": "applies", "above_ft": 60.0}],
    }
    assert section_legal_lines(doc) is None


# --------------------------------------------------------------------------- S5
def test_s5_a_1_4_0_document_renders_identically():
    """A 1.4.0 document has no available permitted_envelope here, so results= changes nothing."""
    doc = load(DOC_1_4_0)
    assert doc["contract_version"] == "1.4.0"
    assert section_legal_lines(doc) is None
    alt = doc["building_alternatives"][0]
    with_results = render_floor_stack(alt, env=ENV_ON, results=doc).svg
    without = render_floor_stack(alt, env=ENV_ON).svg
    assert with_results == without
