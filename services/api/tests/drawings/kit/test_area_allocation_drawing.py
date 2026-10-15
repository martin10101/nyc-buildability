"""Area-illustration drawing kernel tests (task M5-T183; D-094 R087-R098, R024/R092).

Renders the two committed synthetic 1.5.0 fixtures (reading ONLY their
``area_allocation`` and ``placement`` blocks) and pins two byte-stable snapshots,
and drives every state and refusal from small literal blocks. It asserts the
state switch (bar vs zones vs Unavailable), the verbatim token labels and the one
caption, the share-driven proportion and the one stated percentage, the no-plan-
detail invariant, the carried measure and conversion statement, the 8.5 pt
readability floor with hatch-not-colour separation, the fail-closed paths and
determinism.
"""

from __future__ import annotations

import json
import math
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from app.drawings.kit.area_allocation import _MAX_OUTLINE_VERTICES, draw_area_allocation
from app.drawings.kit.model import Drawing, Unavailable
from app.drawings.kit.presentation_tokens import WORDING

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIXTURES = REPO / "packages" / "contracts" / "fixtures" / "valid" / "results"
SNAPSHOTS = HERE / "snapshots"
SVG_NS = "{http://www.w3.org/2000/svg}"

PLACED = "synthetic_placed_building_contract_1_5_0"
REAR_YARD = "synthetic_rear_yard_constraints_contract_1_5_0"

# The 82x82 placed outline carried by synthetic_placed (read from the fixture; the
# literal-block tests reuse the same shape without depending on the file).
SQUARE = [[[0.0, 0.0], [82.0, 0.0], [82.0, 82.0], [0.0, 82.0], [0.0, 0.0]]]
_CONVERSION = (
    "plate = zoning floor area per storey; no gross-up, exclusions or "
    "wall-thickness conversion worked"
)


def blocks(stem: str) -> tuple[dict, dict | None]:
    """ONLY the ``area_allocation`` and ``placement`` blocks of a fixture's first
    worked building - the test depends on no other block."""
    doc = json.loads((FIXTURES / f"{stem}.json").read_text(encoding="utf-8"))
    alt = doc["building_alternatives"][0]
    return alt["area_allocation"], alt.get("placement")


def allocation(share: float, *, fitted: bool, total: float = 20000.0) -> dict:
    """A sound literal area_allocation block at ``share`` (apartment = share x total)."""
    apartment = round(share * total, 2)
    return {
        "label": "Illustrative",
        "share": share,
        "measure": "residential_floor_area",
        "conversion_statement": _CONVERSION,
        "apartment_area_sqft": apartment,
        "other_area_sqft": round(total - apartment, 2),
        "total_sqft": total,
        "fitted": fitted,
    }


def placement(outline=SQUARE, status: str = "placed") -> dict:
    block = {
        "status": status,
        "label": "Illustrative",
        "method": "Illustrative only.",
        "basis": "derived",
        "measure": "residential_floor_area",
        "conversion_statement": _CONVERSION,
    }
    if outline is not None:
        block["outline"] = outline
    return block


def root(drawing: Drawing) -> ET.Element:
    return ET.fromstring(drawing.svg)


def roles(drawing: Drawing) -> list[str]:
    return [el.get("data-role") for el in root(drawing).iter() if el.get("data-role")]


def texts(drawing: Drawing) -> list[tuple[str, str]]:
    """(role, text) of every ``<text>``."""
    out = []
    for el in root(drawing).iter(f"{SVG_NS}text"):
        out.append((el.get("data-role"), " ".join((el.text or "").split())))
    return out


def group(drawing: Drawing) -> ET.Element:
    return root(drawing).find(f".//{SVG_NS}g[@data-drawing-part='area_allocation']")


# -- a trivial passing seed so the suite is never empty while editing --


def test_module_imports() -> None:
    assert callable(draw_area_allocation)


# -- S1: the state switch -----------------------------------------------------


def test_s1_unfitted_draws_a_bar_no_zone() -> None:
    alloc, place = blocks(REAR_YARD)
    drawing = draw_area_allocation(alloc, placement=place)
    assert isinstance(drawing, Drawing)
    present = roles(drawing)
    assert "area_bar_apartment" in present and "area_bar_other" in present
    assert "area_zone_apartment" not in present
    assert "area_zone_other" not in present
    assert "area_division" not in present
    assert "area_footprint" not in present


def test_s1_fitted_with_outline_draws_zones_no_bar() -> None:
    alloc, place = blocks(PLACED)
    drawing = draw_area_allocation(alloc, placement=place)
    assert isinstance(drawing, Drawing)
    present = roles(drawing)
    assert "area_zone_apartment" in present and "area_zone_other" in present
    assert present.count("area_division") == 1
    assert "area_footprint" in present
    assert "area_bar_apartment" not in present
    assert "area_bar_other" not in present


def test_s1_fitted_without_outline_is_unavailable_never_a_bar() -> None:
    alloc = allocation(0.70, fitted=True)
    for place in (None, placement(outline=None, status="withheld"), placement(status="withheld")):
        result = draw_area_allocation(alloc, placement=place)
        assert isinstance(result, Unavailable)
        assert result.reason_kind == "not_placed"


# -- S2: labels and caption verbatim from the tokens --------------------------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s2_labels_and_caption_are_the_tokens_verbatim(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    printed = {role: text for role, text in texts(drawing)}
    assert printed["area_label_apartment"] == WORDING["area_zone_apartment"] == "Apartment area"
    assert printed["area_label_other"] == WORDING["area_zone_other"]
    assert printed["area_label_other"] == (
        "Other building area: core, circulation, walls and services"
    )
    assert printed["caption"] == WORDING["area_illustration_caption"]
    assert printed["caption"] == "Illustrative area allocation—not a floor plan"
    assert not printed["caption"].endswith(".")
    assert [role for role, _ in texts(drawing)].count("caption") == 1


def test_s2_caption_can_be_omitted_for_the_report_frame() -> None:
    alloc, place = blocks(PLACED)
    drawing = draw_area_allocation(alloc, placement=place, caption=False)
    assert "caption" not in [role for role, _ in texts(drawing)]


# -- S3: the drawn proportion comes from the share ----------------------------


def _bar_fraction(drawing: Drawing) -> float:
    widths = {}
    for el in root(drawing).iter(f"{SVG_NS}rect"):
        role = el.get("data-role")
        if role in ("area_bar_apartment", "area_bar_other"):
            widths[role] = float(el.get("width"))
    return widths["area_bar_apartment"] / (
        widths["area_bar_apartment"] + widths["area_bar_other"]
    )


def test_s3_bar_proportion_equals_share_within_half_percent() -> None:
    for share in (0.60, 0.65, 0.70, 0.75):
        drawing = draw_area_allocation(allocation(share, fitted=False))
        assert abs(_bar_fraction(drawing) - share) <= 0.005
        assert abs(float(group(drawing).get("data-apartment-fraction")) - share) <= 0.005


def test_s3_zone_proportion_equals_share_within_half_percent() -> None:
    for share in (0.60, 0.65, 0.70, 0.75):
        drawing = draw_area_allocation(allocation(share, fitted=True), placement=placement())
        assert abs(float(group(drawing).get("data-apartment-fraction")) - share) <= 0.005


def test_s3_changing_only_the_share_moves_the_drawn_ratio() -> None:
    low = draw_area_allocation(allocation(0.65, fitted=True), placement=placement())
    high = draw_area_allocation(allocation(0.70, fitted=True), placement=placement())
    f_low = float(group(low).get("data-apartment-fraction"))
    f_high = float(group(high).get("data-apartment-fraction"))
    assert f_low < f_high
    assert abs(f_low - 0.65) <= 0.005 and abs(f_high - 0.70) <= 0.005


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s3_fixture_fraction_equals_apartment_over_total(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    drawn = float(group(drawing).get("data-apartment-fraction"))
    assert abs(drawn - alloc["apartment_area_sqft"] / alloc["total_sqft"]) <= 0.005
    assert abs(drawn - alloc["share"]) <= 0.005


def test_s3_inconsistent_split_is_unavailable() -> None:
    bad_total = allocation(0.70, fitted=False)
    bad_total["other_area_sqft"] = bad_total["other_area_sqft"] + 500.0  # apartment+other != total
    assert isinstance(draw_area_allocation(bad_total), Unavailable)

    bad_share = allocation(0.70, fitted=False)
    bad_share["share"] = 0.62  # share now disagrees with apartment/total
    result = draw_area_allocation(bad_share)
    assert isinstance(result, Unavailable)
    assert result.reason_kind == "inconsistent"


# -- S4: the one stated percentage --------------------------------------------


def test_s4_percentage_is_round_share_times_100_not_hardcoded() -> None:
    for share, expected in ((0.60, "60%"), (0.65, "65%"), (0.70, "70%")):
        drawing = draw_area_allocation(allocation(share, fitted=False))
        printed = {role: text for role, text in texts(drawing)}
        assert printed["area_percentage"] == f"{expected} apartment area"


# -- S5: no plan detail -------------------------------------------------------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s5_only_the_expected_texts_and_one_number(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    printed = sorted(text for _, text in texts(drawing))
    pct = round(alloc["share"] * 100)
    assert printed == sorted([
        f"{pct}% apartment area",
        WORDING["area_zone_apartment"],
        WORDING["area_zone_other"],
        "Residential floor area",
        _CONVERSION,
        WORDING["area_illustration_caption"],
    ])
    numbers = [int(m) for _, text in texts(drawing) for m in re.findall(r"\d+", text)]
    assert numbers == [pct]  # the one stated percentage; no apartment count, no room number


def test_s5_fitted_has_exactly_one_line_inside_the_footprint() -> None:
    alloc, place = blocks(PLACED)
    present = roles(draw_area_allocation(alloc, placement=place))
    assert present.count("area_division") == 1


# -- S6: the measure and the conversion statement -----------------------------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s6_carries_measure_and_exact_conversion_statement(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    printed = {role: text for role, text in texts(drawing)}
    assert printed["area_conversion"] == alloc["conversion_statement"] == _CONVERSION
    assert printed["area_measure"] == "Residential floor area"
    # ZFA / apartment area are never equated: the one percentage is the only number.
    assert "zoning floor area" not in printed["area_measure"].lower()


# -- S7: readability floor and hatch-not-colour -------------------------------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s7_every_label_is_at_least_8_5_pt(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    sizes = [float(el.get("font-size")) for el in root(drawing).iter(f"{SVG_NS}text")]
    assert sizes and all(size >= 8.5 for size in sizes)


def test_s7_zones_told_apart_by_hatch_not_colour() -> None:
    alloc, place = blocks(PLACED)
    drawing = draw_area_allocation(alloc, placement=place)
    fills = {}
    for el in root(drawing).iter(f"{SVG_NS}path"):
        role = el.get("data-role")
        if role in ("area_zone_apartment", "area_zone_other"):
            fills[role] = el.get("fill")
    assert fills["area_zone_apartment"] == fills["area_zone_other"]  # same colour
    patterns = root(drawing).findall(f".//{SVG_NS}pattern")
    transforms = {p.get("patternTransform") for p in patterns}
    assert len(patterns) == 2 and len(transforms) == 2  # two distinct hatches


# -- S8: the fail-closed paths ------------------------------------------------


def test_s8_unavailable_paths() -> None:
    assert isinstance(draw_area_allocation(None), Unavailable)  # type: ignore[arg-type]
    assert isinstance(draw_area_allocation({}), Unavailable)

    nonfinite = allocation(0.70, fitted=False)
    nonfinite["share"] = float("nan")
    assert isinstance(draw_area_allocation(nonfinite), Unavailable)

    for bad in (0.50, 0.80):
        out_of_range = allocation(0.70, fitted=False)
        out_of_range["share"] = bad
        assert isinstance(draw_area_allocation(out_of_range), Unavailable)

    garbled = allocation(0.70, fitted=False)
    garbled["conversion_statement"] = "something else"
    assert isinstance(draw_area_allocation(garbled), Unavailable)

    not_bool = allocation(0.70, fitted=False)
    not_bool["fitted"] = "yes"
    result = draw_area_allocation(not_bool)
    assert isinstance(result, Unavailable)
    assert result.reason and isinstance(result.reason, str)


def test_s8_reasons_are_plain_words_no_internal_names() -> None:
    forbidden = ("area_allocation", "fitted", "sqft", "placement", "outline", "/", "_")
    for block in (None, {}, allocation(0.90, fitted=False)):
        result = draw_area_allocation(block)  # type: ignore[arg-type]
        assert isinstance(result, Unavailable)
        assert not any(token in result.reason for token in forbidden)


# -- S9: determinism ----------------------------------------------------------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_s9_same_input_and_reordered_keys_give_identical_svg(stem: str) -> None:
    alloc, place = blocks(stem)
    first = draw_area_allocation(alloc, placement=place)
    again = draw_area_allocation(alloc, placement=place)
    assert isinstance(first, Drawing) and first.svg == again.svg
    reordered_alloc = json.loads(json.dumps(alloc, sort_keys=True))
    reordered_place = json.loads(json.dumps(place, sort_keys=True)) if place else None
    reordered = draw_area_allocation(reordered_alloc, placement=reordered_place)
    assert isinstance(reordered, Drawing) and reordered.svg == first.svg


# -- snapshots (byte-stable; regenerate with UPDATE_DRAWING_SNAPSHOTS=1) -------


@pytest.mark.parametrize("stem", [PLACED, REAR_YARD])
def test_matches_approved_snapshot(stem: str) -> None:
    alloc, place = blocks(stem)
    drawing = draw_area_allocation(alloc, placement=place)
    assert isinstance(drawing, Drawing)
    snapshot = SNAPSHOTS / f"{stem}.area_allocation.svg"
    if os.environ.get("UPDATE_DRAWING_SNAPSHOTS") == "1":
        snapshot.write_bytes(drawing.svg.encode("utf-8"))
    assert snapshot.exists(), f"no approved snapshot {snapshot.name}"
    assert drawing.svg.encode("utf-8") == snapshot.read_bytes().replace(b"\r\n", b"\n")


# -- round 2: a hostile placement.outline fails closed (G5 F1/F2/F3) ----------
# The kernel's contract is to fail CLOSED: a footprint it cannot draw truthfully
# yields Unavailable, never a malformed drawing (a literal 'nan' in a path) and
# never an unhandled ZeroDivisionError or ValueError from the svg helpers. One
# test per input state; the two valid fixtures keep drawing byte-identically
# (test_matches_approved_snapshot, unchanged).


def _fitted_outline(outline) -> object:
    """draw_area_allocation for a fitted block with the given placement.outline."""
    return draw_area_allocation(allocation(0.70, fitted=True), placement=placement(outline=outline))


@pytest.mark.parametrize(
    "bad_coord", [float("nan"), float("inf"), float("-inf"), 1e308]
)
def test_f1_nonfinite_or_overlarge_outline_coord_is_unavailable(bad_coord: float) -> None:
    outline = [[[0.0, 0.0], [82.0, 0.0], [82.0, bad_coord], [0.0, 82.0], [0.0, 0.0]]]
    result = _fitted_outline(outline)
    assert isinstance(result, Unavailable)
    assert result.reason_kind == "outline_invalid"
    assert "nan" not in (result.reason or "").lower()


def test_f2_zero_area_collinear_ring_is_unavailable_no_zerodivision() -> None:
    # a flat (collinear) ring: finite small points, zero area -> would divide by zero
    result = _fitted_outline([[[0.0, 0.0], [40.0, 0.0], [80.0, 0.0], [0.0, 0.0]]])
    assert isinstance(result, Unavailable)
    assert result.reason_kind == "outline_invalid"


def test_f2_zero_width_spike_clips_to_nothing_is_unavailable() -> None:
    # a vertical spike with no width: there is no area to split into two zones
    result = _fitted_outline([[[10.0, 0.0], [10.0, 40.0], [10.0, 80.0], [10.0, 0.0]]])
    assert isinstance(result, Unavailable)
    assert result.reason_kind == "outline_invalid"


def test_f3_outline_above_the_vertex_cap_is_unavailable() -> None:
    n = _MAX_OUTLINE_VERTICES
    circle = [[50.0 + 40.0 * math.cos(2 * math.pi * i / n),
               50.0 + 40.0 * math.sin(2 * math.pi * i / n)] for i in range(n)]
    over_cap = [circle + [circle[0]]]  # cap + 1 raw vertices (1001)
    result = _fitted_outline(over_cap)
    assert isinstance(result, Unavailable)
    assert result.reason_kind == "outline_invalid"
    at_cap = [circle[:n - 1] + [circle[0]]]  # exactly cap raw vertices (1000) still draws
    assert isinstance(_fitted_outline(at_cap), Drawing)


def test_f1_f2_outline_reasons_are_plain_words_no_internal_names() -> None:
    forbidden = ("area_allocation", "fitted", "sqft", "placement", "outline", "/", "_")
    for outline in (
        [[[0.0, 0.0], [82.0, 0.0], [82.0, float("nan")], [0.0, 82.0]]],
        [[[0.0, 0.0], [40.0, 0.0], [80.0, 0.0], [0.0, 0.0]]],
    ):
        result = _fitted_outline(outline)
        assert isinstance(result, Unavailable)
        assert not any(token in result.reason for token in forbidden)


def test_valid_fitted_outline_still_draws_without_a_nan_token() -> None:
    alloc, place = blocks(PLACED)
    drawing = draw_area_allocation(alloc, placement=place)
    assert isinstance(drawing, Drawing)
    assert "nan" not in drawing.svg.lower()
