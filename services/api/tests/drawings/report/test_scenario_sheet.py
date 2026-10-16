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
from app.drawings.report import (
    build_report_html,
    page_scenario_sheet,
    readers,
    scenario_figures,
)

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
# Part B2 (render_floor_stack with results=) is landed at this head, so the benchmark
# section draws the permitted-envelope height lines; the "drawn from the schedule only"
# caption with its footprint_drawn clause is the NO-height-lines branch, so these tests
# use a document whose permitted envelope carries no heights (it keeps the placed
# building and its floor plates, so the placement line is unchanged).
def _no_height_lines_doc() -> dict:
    doc = copy.deepcopy(benchmark())
    doc["answers"]["permitted_envelope"] = {"status": "not_available"}
    return doc


def test_s4_footprint_drawn_none_keeps_todays_section_caption_and_no_placement_line() -> None:
    text = visible_text(render(_no_height_lines_doc(), env=_LANE_E, footprint_drawn=None))
    assert ("Floor-stack section (Illustrative): drawn from the schedule only, "
            "with no placement on the lot.") in text
    assert "is worked out but is not drawn" not in text


def test_s4_footprint_drawn_false_says_worked_out_but_not_drawn() -> None:
    text = visible_text(render(_no_height_lines_doc(), env=_LANE_E, footprint_drawn=False))
    assert "The footprint is worked out but is not drawn in this report." in text
    # the section caption keeps the "no placement" clause while the footprint is not drawn.
    assert "with no placement on the lot." in text


def test_s4_footprint_drawn_true_drops_the_no_placement_clause_and_says_nothing() -> None:
    text = visible_text(render(_no_height_lines_doc(), env=_LANE_E, footprint_drawn=True))
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


def test_s7_without_height_lines_the_section_keeps_todays_caption_and_does_not_error() -> None:
    # Part B2 is landed (render_floor_stack has results=), but a document whose
    # permitted envelope carries no heights draws no lines: the section keeps today's
    # schedule-only caption and does not error.
    text = visible_text(render(_no_height_lines_doc(), env=_LANE_E))
    assert "Floor-stack section (Illustrative): drawn from the schedule only" in text
    assert "height limits from the permitted envelope" not in text


def test_s7_with_part_b2_landed_the_benchmark_section_names_the_height_lines() -> None:
    # the REAL render_floor_stack (part B2) draws the benchmark's standard heights.
    text = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=None))
    assert ("Section (Illustrative): storeys from the floor schedule; height limits "
            "from the permitted envelope (Conditional).") in text
    assert "Floor-stack section (Illustrative)" not in text


# ==================================================================== ROUND 2
# The review items that live in this part's files (returns T193-G1/G3/G3v/G4 and the
# section reviews T192-G1/G3v). Each test pins one item; its mutation proof is in the
# producer report's Round 2 section.


def _schedule_header_cells(html: str) -> list[str]:
    anchor = html.index("Floor schedule for this building")
    thead = html[html.index("<thead", anchor):html.index("</thead>", anchor)]
    return [visible_text(cell).strip() for cell in re.findall(r"<th>(.*?)</th>", thead, flags=re.S)]


# item (a) - G1 advisory: the caption is one sentence; the figures follow the token
# after a colon, never a second sentence beginning lower-case.
def test_r2_area_caption_joins_the_token_with_a_colon() -> None:
    caption = page_scenario_sheet._area_caption(_building(benchmark()))
    assert caption.startswith(f"{_CAPTION_TOKEN}: apartment area")
    assert ". apartment area" not in caption


# item (b) - G3v advisory 1: the duplicate plate column is gone. plan_area_sqft and
# floor_area_sqft are the same measure under two field names (the engine sets them
# equal in every path), so ONE "Zoning floor area per storey" column reading
# floor_area_sqft remains; every body row now has five cells, not six.
def test_r2_schedule_drops_the_duplicate_plate_column() -> None:
    html = render(benchmark(), env=_LANE_E)
    headers = _schedule_header_cells(html)
    assert headers == ["Storey", "Floor-to-floor", "Top of floor",
                       "Zoning floor area per storey", "Running total"]
    assert "Floor area" not in headers
    anchor = html.index("Floor schedule for this building")
    tbody = html[html.index("<tbody>", anchor):html.index("</tbody>", anchor)]
    rows = re.findall(r"<tr>(.*?)</tr>", tbody, flags=re.S)
    assert rows
    for row in rows:
        assert len(re.findall(r"<td>.*?</td>", row, flags=re.S)) == 5


# item (c) - section F3 / owner R021: the fixed "schematic, not to scale" label sits
# once near the section when it is drawn, and never when there is no drawing.
def test_r2_section_caption_carries_the_schematic_label_once_when_drawn() -> None:
    drawn = visible_text(render(benchmark(), env=_LANE_E))
    assert page_scenario_sheet._SCHEMATIC_NOTE in drawn
    assert drawn.count(page_scenario_sheet._SCHEMATIC_NOTE) == 1
    assert "schematic, not to scale" in drawn
    plain = visible_text(render(benchmark()))  # no section drawn -> no label
    assert page_scenario_sheet._SCHEMATIC_NOTE not in plain


def _settled_heights_doc() -> dict:
    doc = copy.deepcopy(benchmark())
    states = doc["answers"]["permitted_envelope"]["value_states"]
    for key in ("min_base_height", "max_base_height", "max_building_height"):
        states[key] = {"way": "settled"}
    return doc


# item (d) - section G1 REQUIRED: whether the drawn height lines are marked
# (Conditional) is READ from the document's value_states, never hard-coded. Part B2
# is landed, so the real render_floor_stack draws the lines for both documents.
def test_r2_conditional_marker_is_read_from_value_states() -> None:
    # benchmark: the three standard heights are conditional -> the caption marks it.
    conditional = visible_text(render(benchmark(), env=_LANE_E, footprint_drawn=None))
    assert "height limits from the permitted envelope (Conditional)." in conditional
    # settled value_states -> the height-line caption stays but is NOT marked conditional.
    settled = visible_text(render(_settled_heights_doc(), env=_LANE_E, footprint_drawn=None))
    assert "height limits from the permitted envelope." in settled
    assert "(Conditional)" not in settled


# item (e) - section G3 / visual F2: the embedded section's smallest label prints at
# or above the contract's 8.5 pt, while the stamped point size still equals the
# viewBox (the D1/D2 embed invariant the benchmark pins enforce).
def test_r2_embedded_section_labels_print_at_least_8_5_pt() -> None:
    emb = scenario_figures.embed_section(_building(benchmark()), benchmark(), env=_LANE_E)
    assert emb.is_drawing
    svg = emb.svg
    vb = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([-\d.]+) ([-\d.]+)"', svg)
    width = re.search(r'width="([-\d.]+)pt"', svg)
    height = re.search(r'height="([-\d.]+)pt"', svg)
    assert vb and width and height
    assert abs(float(width.group(1)) - float(vb.group(1))) < 0.01
    assert abs(float(height.group(1)) - float(vb.group(2))) < 0.01
    scale = re.search(r'<g transform="scale\(([\d.]+)\)"', svg)
    factor = float(scale.group(1)) if scale else 1.0
    fonts = [float(size) for size in re.findall(r'font-size="([\d.]+)"', svg)]
    assert fonts
    smallest_printed = min(fonts) * factor
    assert smallest_printed >= 8.5, f"smallest section label prints at {smallest_printed} pt"


def _reconciling_schedule_doc() -> dict:
    doc = copy.deepcopy(benchmark())
    running = 0.0
    for floor in _building(doc)["floor_schedule"]:
        floor["floor_area_sqft"] = 6000.0
        floor["plan_area_sqft"] = 6000.0
        running += 6000.0
        floor["running_total_sqft"] = running
    return doc


# item (f) - G3 code advisory 2: no reconciliation note when the shown storey figures
# add exactly to the shown total (the positive counterpart of S5's note-shown case).
def test_r2_no_rounding_note_when_the_schedule_reconciles_exactly() -> None:
    text = visible_text(render(_reconciling_schedule_doc(), env=_LANE_E))
    assert "6,000 sq ft" in text  # the schedule rendered
    assert page_scenario_sheet._ROUNDING_NOTE not in text
