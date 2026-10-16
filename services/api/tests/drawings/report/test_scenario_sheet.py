"""M5-T173 part B3 (M5-T193) - page-6 scenario-sheet acceptance scenarios S1-S7.

The sheet gains, per worked building: the two-zone area illustration with ONE
caption carrying the document's apartment / other / total floor-area figures and
the footprint basis; the floor-stack section with the permitted-envelope height
lines (part B2) when drawn; a floor schedule whose plate column reads as zoning
floor area per storey, reconciled to the running total; and the unresolved items
for this building linked to the appendix. Every drawn or placed claim takes an
explicit flag (``footprint_drawn`` and the embedded drawings).

Numbers are the reference-case values (docs/reference-cases/R6B/cases/
placement-building-b.json: area-allocation 12,090 / 8,060 / 20,150; plate 6,716.67
per storey; footprint on the printed-tax-map basis), never a program run. Prose
read from the engine fixture is read at test time (M5-T180 rewords it later), so
only the reference-case numbers are literal.
"""

from __future__ import annotations

import copy
import html as _html
import json
import re
from pathlib import Path

import pytest

from app.drawings.kit import area_allocation
from app.drawings.report import build_report_html, page_scenario_sheet, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_LANE_E = {"LANE_E_ENABLED": "1"}

_CAPTION_TOKEN = "Illustrative area allocation—not a floor plan"
_PLAIN_PAGE6_WORD_CAP = 260
_PLAIN_REPORT_WORD_CAP = 2448


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def render(doc: dict, **kwargs: object) -> str:
    return page_scenario_sheet.render(doc, {}, **kwargs)


def _building(doc: dict) -> dict:
    return doc["building_alternatives"][0]


def _one_four_zero() -> dict:
    """A 1.4.0-shaped document: no placement, no area_allocation, no floor plate
    and no unchecked items on the worked building (the minimal before/after case)."""
    doc = copy.deepcopy(benchmark())
    doc["contract_version"] = "1.4.0"
    building = _building(doc)
    building.pop("area_allocation", None)
    building.pop("placement", None)
    building["not_checked"] = []
    geometry = doc.get("geometry")
    if isinstance(geometry, dict):
        geometry.pop("floor_plates", None)
    return doc


# =========================================================================== S1
def test_s1_1_4_0_document_shows_no_illustration_and_only_the_schedule_changes() -> None:
    doc = _one_four_zero()
    text = visible_text(render(doc))  # drawings None, LANE_E off

    # NO new drawn/placed claim or caption (before: none; after: none).
    assert _CAPTION_TOKEN not in text
    assert "printed tax map" not in text
    assert "% apartment area" not in text
    assert "footprint on the" not in text
    assert "is worked out but is not drawn" not in text
    assert readers.NOT_PLACED_LINE not in text
    # No unresolved block (no not_checked, no placement): before showed "What was not
    # checked"; after there is simply nothing to list, so the block is omitted.
    assert "Unresolved for this building" not in text

    # The ONLY schedule wording changes, each listed before -> after:
    # (a) the plate column header:  "Plan area"  ->  "Zoning floor area per storey".
    assert "Zoning floor area per storey" in text
    assert "Plan area" not in text
    # (b) the reconciliation note is added (shown figures do not add to the shown total).
    assert "Storey areas are shown rounded; the running total adds the unrounded areas." in text


# =========================================================================== S2
def test_s2_fitted_benchmark_draws_zones_with_one_caption_and_one_percentage() -> None:
    html = render(benchmark(), env=_LANE_E)
    text = visible_text(html)

    # the kernel's zones sit inside the placement outline (zones, never the bar).
    assert 'data-role="area_zone_apartment"' in html
    assert 'data-role="area_zone_other"' in html
    assert 'data-role="area_bar_apartment"' not in html

    # exactly one stated percentage on the sheet, the kernel's "60% apartment area".
    assert text.count("%") == 1
    assert "60% apartment area" in text

    # the ONE caption carries the reference-case areas and the printed-tax-map basis.
    caption_values = ("12,090", "8,060", "20,150")
    for value in caption_values:
        assert value in text
    assert _CAPTION_TOKEN in text
    assert "footprint on the printed tax map" in text
    assert text.count(_CAPTION_TOKEN) == 1

    # the bare measure label, no "Measure:" prefix (that prefix is the web's, M5-T174).
    assert "Residential floor area" in html
    assert "Measure:" not in text

    # the drawn illustration shows no unit count, room, unit or stair words.
    illustration = html[html.index('data-drawing="area_allocation"'):]
    illustration = illustration[:illustration.index("</svg>")]
    illustration_text = visible_text(illustration).lower()
    for banned in ("room", "stair", "elevator", "dwelling", "unit"):
        assert banned not in illustration_text


# =========================================================================== S3
def test_s3_not_fitted_draws_the_bar_without_a_footprint_clause() -> None:
    doc = copy.deepcopy(benchmark())
    _building(doc)["area_allocation"]["fitted"] = False
    html = render(doc, env=_LANE_E)
    text = visible_text(html)
    assert 'data-role="area_bar_apartment"' in html
    assert 'data-role="area_zone_apartment"' not in html
    assert "60% apartment area" in text
    # no footprint is drawn for the bar, so the caption carries no footprint-basis clause.
    assert "footprint on the" not in text
    assert "12,090" in text and "8,060" in text and "20,150" in text


# one degenerate block per kernel refusal: the printed line equals the kernel's own
# reason, READ AT TEST TIME (no copied literal).
def _degenerate_share_out_of_range(doc: dict) -> None:
    _building(doc)["area_allocation"]["share"] = 0.9


def _degenerate_areas_do_not_add(doc: dict) -> None:
    _building(doc)["area_allocation"]["total_sqft"] = 99999.0


def _degenerate_fitted_but_not_placed(doc: dict) -> None:
    _building(doc)["placement"]["status"] = "proposed"


@pytest.mark.parametrize(
    "mutate",
    [_degenerate_share_out_of_range, _degenerate_areas_do_not_add,
     _degenerate_fitted_but_not_placed],
)
def test_s3_degenerate_block_prints_the_kernel_reason(mutate) -> None:
    doc = copy.deepcopy(benchmark())
    mutate(doc)
    building = _building(doc)
    reason = area_allocation.draw_area_allocation(
        building["area_allocation"], placement=building.get("placement"), caption=False
    ).reason
    assert reason  # the kernel refused with a reason
    text = visible_text(render(doc, env=_LANE_E))
    assert reason in text
    # nothing is drawn for a refused block.
    assert "60% apartment area" not in text


# =========================================================================== S4
def test_s4_footprint_drawn_none_keeps_todays_section_caption_and_no_placement_line() -> None:
    text = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=None))
    assert ("Floor-stack section (Illustrative): drawn from the schedule only, "
            "with no placement on the lot.") in text
    assert "is worked out but is not drawn" not in text


def test_s4_footprint_drawn_false_says_worked_out_but_not_drawn() -> None:
    text = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=False))
    assert "The footprint is worked out but is not drawn in this report." in text
    # the section caption keeps the "no placement" clause while the footprint is not drawn.
    assert "with no placement on the lot." in text


def test_s4_footprint_drawn_true_drops_the_no_placement_clause_and_says_nothing() -> None:
    text = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=True))
    assert "Floor-stack section (Illustrative): drawn from the schedule only." in text
    assert "with no placement on the lot" not in text
    assert "is worked out but is not drawn" not in text


def test_s4_not_placed_document_keeps_the_standing_not_placed_line() -> None:
    doc = copy.deepcopy(benchmark())
    doc["geometry"]["floor_plates"]["status"] = "not_available"
    text = visible_text(render(doc, env=_LANE_E, footprint_drawn=True))
    assert readers.NOT_PLACED_LINE in text


# =========================================================================== S5
def test_s5_schedule_reads_as_zoning_floor_area_per_storey_with_the_rounding_note() -> None:
    text = visible_text(render(benchmark(), env=_LANE_E))
    # the reference-case plate: 10/20/30 ft tops, 6,716.67 sq ft per storey, 20,150 total.
    for figure in ("10 ft", "20 ft", "30 ft", "6,716.67 sq ft", "20,150 sq ft"):
        assert figure in text
    assert "Zoning floor area per storey" in text
    # the shown 3 x 6,716.67 do not add to the shown 20,150, so the note is shown.
    assert "Storey areas are shown rounded; the running total adds the unrounded areas." in text


_CONVERSION = (
    "plate = zoning floor area per storey; no gross-up, exclusions or "
    "wall-thickness conversion worked"
)


def test_s5_conversion_statement_appears_once_on_the_page_when_drawn() -> None:
    page = visible_text(render(benchmark(), env=_LANE_E))  # illustration drawn
    assert page.count(_CONVERSION) == 1


def test_s5_conversion_statement_appears_once_on_the_page_when_not_drawn() -> None:
    page = visible_text(render(benchmark()))  # LANE_E off: no illustration -> footnote
    assert page.count(_CONVERSION) == 1


# =========================================================================== S6
def test_s6_unresolved_list_is_six_items_parking_once_in_document_order() -> None:
    html = render(benchmark(), env=_LANE_E)
    block = html[html.index("Unresolved for this building"):]
    items = re.findall(r"<li>(.*?)</li>", block, flags=re.S)
    items = [visible_text(i).strip() for i in items]
    building = _building(benchmark())
    expected = list(building["not_checked"]) + list(building["placement"]["not_checked"])
    seen: set[str] = set()
    deduped: list[str] = []
    for text in expected:
        key = text.strip().lower()
        if key not in seen:
            seen.add(key)
            deduped.append(text.strip())
    assert items == deduped
    assert len(items) == 6
    # parking appears once (the capitalised building item wins over the placement's).
    assert sum("parking" in i.lower() for i in items) == 1


def test_s6_one_linked_line_resolves_to_appendix_open_item_anchors() -> None:
    results = benchmark()
    html = render(results, env=_LANE_E)
    numbers = [it["number"] for it in readers.open_items(results)]
    for number in numbers:
        assert f'href="#issue-{number}"' in html


def test_s6_plain_render_page_6_within_the_word_cap() -> None:
    words = len(visible_text(render(benchmark())).split())
    assert words <= _PLAIN_PAGE6_WORD_CAP, f"page 6 has {words} words (cap {_PLAIN_PAGE6_WORD_CAP})"


def test_s6_plain_report_within_the_word_cap_and_no_repeats() -> None:
    html = build_report_html(benchmark())  # plain render, LANE_E off
    flat = " ".join(visible_text(html).split())
    assert len(flat.split()) <= _PLAIN_REPORT_WORD_CAP
    parts = re.split(r"(?<=[.!?])\s+", flat)
    longs = [" ".join(p.split()) for p in parts if len(p.split()) >= 8]
    repeated = {s for s in longs if longs.count(s) >= 2}
    assert repeated == set(), f"new repeated sentences: {repeated}"


# =========================================================================== S7
class _FakeDrawing:
    def __init__(self, svg: str) -> None:
        self.svg = svg
        self.kinds_drawn = ("section",)


def _fake_render_floor_stack(alternative, *, frame="report", env=None, results=None):
    # part B2's signature: carries the ``results=`` keyword and draws the height lines.
    return _FakeDrawing(
        '<svg viewBox="0 0 100 100"><text>Minimum base height 30 ft</text>'
        '<text>Maximum building height 55 ft</text></svg>'
    )


def test_s7_with_part_b2_the_section_caption_names_the_height_lines(monkeypatch) -> None:
    import app.drawings.kit as kit

    monkeypatch.setattr(kit, "render_floor_stack", _fake_render_floor_stack, raising=True)
    text = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=None))
    assert ("Section (Illustrative): storeys from the floor schedule; height limits "
            "from the permitted envelope (Conditional).") in text
    # with the height-line caption the old floor-stack caption is gone.
    assert "Floor-stack section (Illustrative)" not in text


def test_s7_without_part_b2_the_section_keeps_todays_caption_and_does_not_error() -> None:
    # the real render_floor_stack carries no results= keyword at this head.
    text = visible_text(render(benchmark(), env=_LANE_E))
    assert "Floor-stack section (Illustrative): drawn from the schedule only" in text
    assert "height limits from the permitted envelope" not in text
