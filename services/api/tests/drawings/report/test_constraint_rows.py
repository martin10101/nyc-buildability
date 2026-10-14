"""Page-3 "What constrains the design?" rows read from the results contract 1.5.0
document, with a byte-identical fall-back to the 1.4.0 output (M5-T175; S1-S3, S7,
S9). The report reads the engine's OWN rear-yard combined row and envelope rows,
each with its state/way/text, its ZR sections linked and its numbered open item
linked; a 1.4.0 (and earlier) document renders exactly today's output.

Expected values come from the committed 1.5.0 example
(``synthetic_rear_yard_constraints_contract_1_5_0.json``), the design contract and
the schema - never from a program run.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, constraint_text, page_site_context, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
# The benchmark's recorded map context (the same window pack the constraints-page and
# location-sheet tests use); the live S12 path renders the report WITH it (M5-T175 rw1).
_WINDOW_PACK = Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
_LANE_E = {"LANE_E_ENABLED": "1"}


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text("utf-8"))


def benchmark() -> dict:
    return _load("recorded_215_16_northern_journey.json")


def rear_yard_1_5_0() -> dict:
    return _load("synthetic_rear_yard_constraints_contract_1_5_0.json")


def placed_1_5_0() -> dict:
    return _load("synthetic_placed_building_contract_1_5_0.json")


def map_context() -> dict:
    """The benchmark's recorded map context; its subject outline matches both the
    benchmark and the 1.5.0 rear-yard fixtures' lot outline (same bbl 4073340070), so
    the one-outline check passes and the report draws the surroundings (S12)."""
    from app.api.v1.report_context import recorded_pack_provider

    doc = recorded_pack_provider(_WINDOW_PACK)("4073340070", "test")
    assert doc is not None
    return doc


def _item_number(doc: dict) -> dict:
    return {item["category"]: item["number"] for item in readers.open_items(doc)}


def _rows_markup(doc: dict) -> list[list[str]]:
    return [[str(cell) for cell in row]
            for row in page_site_context._constraint_rows(doc, _item_number(doc))]


def _row_by_title(doc: dict, title: str) -> list[str] | None:
    for row in _rows_markup(doc):
        if row[0] == title:
            return row
    return None


def _visible(markup: str) -> str:
    return _html.unescape(re.sub(r"<[^>]+>", " ", markup))


# =========================================================================== S1
# A 1.4.0 (and earlier) document falls back to today's output UNCHANGED. The
# benchmark carries no 1.5.0 block; its four page-3 rows are byte-for-byte the
# 1.4.0 strings (mutation 1: a changed fall-back text reddens this).
def test_s1_benchmark_1_4_0_rows_are_the_fallback_unchanged() -> None:
    doc = benchmark()
    assert constraint_text.has_results_rows(doc) is False
    assert _rows_markup(doc) == [
        ["Rear yard", "Not known (see item 4)",
         '<span class="label-chip">Unresolved</span>'],
        ["Setback above the base", "Not worked out yet (see item 7)",
         '<span class="label-chip">Pending verification</span>'],
        ["Maximum lot coverage", "Not a single figure; by portion (see item 3)",
         '<span class="label-chip">Unresolved</span>'],
        ["Street wall", "Not checked (see item 8)",
         '<span class="label-chip">Pending verification</span>'],
    ]


def test_s1_a_1_5_0_document_with_no_rear_yard_or_envelope_falls_back() -> None:
    # The placed-building 1.5.0 fixture carries building_alternatives but NO
    # rear_yard / envelope_rows block, so the page-3 rows take the 1.4.0 path.
    doc = placed_1_5_0()
    assert constraint_text.has_results_rows(doc) is False


# =========================================================================== S2
# A conditional rear yard shows the combined row's OWN text, labelled Conditional,
# with ZR 23-344 linked and no number printed.
def test_s2_conditional_rear_yard_shows_combined_text_labelled_conditional() -> None:
    doc = rear_yard_1_5_0()
    assert constraint_text.has_results_rows(doc) is True
    combined = constraint_text.rear_yard_combined(doc)
    assert combined["way"] == "conditional"
    row = _row_by_title(doc, "Rear yard")
    assert row is not None
    title, cell, chip = row
    assert combined["text"] in cell                       # the row's own text
    assert "23-344(b)" in cell                             # names the short-block provision
    assert 'class="label-chip">Conditional</span>' in chip
    # ZR 23-344 is linked to its captured official text.
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in cell
    assert ">ZR 23-344</a>" in cell
    # no rear-yard MEASUREMENT is printed (the combined row carries no number): the
    # visible text has no "ft"/"sq ft" figure of its own.
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(cell))


# =========================================================================== S3
# A not_known row shows no number, only its own reason/text (the side-yard
# envelope row is not_known in the fixture).
def test_s3_not_known_envelope_row_shows_text_no_number() -> None:
    doc = rear_yard_1_5_0()
    side = constraint_text.envelope_row(doc, "side_yard")
    assert side["state"] == "not_known"
    assert "values" not in side  # a not_known row carries no values (schema)
    row = _row_by_title(doc, "Side yard")
    assert row is not None
    _title, cell, chip = row
    assert side["text"] in cell
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(cell))
    assert 'class="label-chip">Pending verification</span>' in chip


# =========================================================================== S7
# The envelope rows render through the same reader, so M5-T170's later output needs
# no further report change.
def test_s7_envelope_rows_render_through_the_same_reader() -> None:
    doc = rear_yard_1_5_0()
    setback = _row_by_title(doc, "Setback above the base")
    street_wall = _row_by_title(doc, "Street wall")
    assert setback is not None and street_wall is not None
    assert constraint_text.envelope_row(doc, "setback")["text"] in setback[1]
    assert constraint_text.envelope_row(doc, "street_wall")["text"] in street_wall[1]
    # the setback reading rests on a stated assumption, so it is Conditional; the
    # street wall is a plain applies reading, so it is Provisional.
    assert 'class="label-chip">Conditional</span>' in setback[2]
    assert 'class="label-chip">Provisional</span>' in street_wall[2]


# =========================================================================== S9
# Every internal #issue-<n> href the report emits resolves to a page_assumptions
# id="issue-<n>" anchor (and the estimate link resolves too).
def test_s9_every_issue_href_resolves_to_an_anchor() -> None:
    html = build_report_html(rear_yard_1_5_0())
    anchors = re.findall(r'href="#([^"]+)"', html)
    assert anchors
    issue_links = [a for a in anchors if a.startswith("issue-")]
    assert issue_links  # the 1.5.0 page-3 rows emit issue links
    for anchor in anchors:
        assert f'id="{anchor}"' in html, f"dangling link #{anchor}"


def test_s9_page_three_rear_yard_links_its_numbered_open_item() -> None:
    doc = rear_yard_1_5_0()
    number = _item_number(doc)["rear_yard"]
    row = _row_by_title(doc, "Rear yard")
    assert f'href="#issue-{number}"' in row[1]
    html = build_report_html(doc)
    assert f'id="issue-{number}"' in html


# =============================================================== fall-back home
# The 1.4.0 State strings have one home in constraint_text (the hard-coded dict
# left page_site_context), so the fall-back and its wording cannot drift apart.
def test_fallback_state_strings_live_in_constraint_text() -> None:
    assert constraint_text.PAGE3_FALLBACK_STATE == {
        "rear_yard": "Not known", "setback": "Not worked out yet"}
    assert constraint_text.PAGE3_DEFAULT_STATE == "Not shown"
    # effect_for (read by the appendix open-item list, which this task does not
    # change) still returns the open-check wording for the rear yard.
    assert constraint_text.effect_for("rear_yard") == constraint_text.REAR_YARD_OPEN_CHECK


# ========================================================================== S12
# The LIVE report path (build_report_html WITH the map embed) draws exactly what the
# unit tests of constraint_overlay.py and close_frame_dimensions.py prove: the
# established constraint lines and the other-basis dimensions on the site frames,
# nothing for a line that is not established, and the page-1 uncertainty reads the
# 1.5.0 combined rear-yard row. Expected values come from the committed 1.5.0 example
# and the benchmark's recorded map context, never from a program run.
def _report_with_maps(doc: dict) -> str:
    return build_report_html(doc, map_context=map_context(), env=_LANE_E)


def test_s12_live_report_draws_only_established_lines_and_other_basis_dimensions() -> None:
    doc = rear_yard_1_5_0()
    # Add a not_established line that DOES carry geometry: R017 (the state guard), not a
    # missing geometry, is what must reject it on the live path (mutation 3).
    doc["geometry"]["constraint_lines"].append({
        "kind": "setback_line", "state": "not_established", "basis": "derived",
        "zr_sections": ["ZR 23-433"], "geometry": [[10.0, 30.0], [90.0, 30.0]]})
    html = _report_with_maps(doc)
    # the established rear_yard_100ft_line is drawn on the live report's site frame, and
    # the large close frame labels it once (the compact page-1 thumbnail draws geometry
    # only). Dropping the wiring (mutation 1) removes both.
    assert 'data-role="constraint-overlay"' in html
    assert 'data-kind="rear_yard_100ft_line"' in html
    assert html.count("Rear-yard 100 ft line") == 1
    # neither the not_established line (geometry present) nor the not_known corner_area
    # draws (R017/R044; mutation 3 draws the not_established one).
    assert 'data-kind="setback_line"' not in html
    assert 'data-kind="corner_area"' not in html
    # the input_facts' other-basis lot dimensions draw beside the map outline, each basis
    # named (the printed-tax-map frontage and the recorded area); dropping the wiring
    # (mutation 1) removes them.
    assert "printed tax map" in html
    assert "city record" in html


def test_s12_1_4_0_report_with_maps_draws_no_overlay() -> None:
    # The benchmark is 1.4.0: it carries no constraint_lines / input_facts, so the live
    # report draws no overlay and no other-basis dimension - byte-identical (S1).
    html = _report_with_maps(benchmark())
    assert 'data-role="constraint-overlay"' not in html
    assert "Rear-yard 100 ft line" not in html
    assert "printed tax map" not in html


def test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard() -> None:
    doc = rear_yard_1_5_0()
    combined = constraint_text.rear_yard_combined(doc)
    assert combined["way"] == "conditional"
    html = build_report_html(doc)  # the page-1 uncertainty text needs no map
    page1 = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    unc = page1[page1.index("What is still uncertain"):]
    unc = unc[:unc.index("</ul>")]
    # the page-1 rear-yard uncertainty shows the combined row's OWN text (not the
    # open-check wording), labelled Conditional, with ZR 23-344 linked - the same reading
    # the page-3 row shows, from the one wording source (mutation 2 reverts this).
    assert combined["text"] in _visible(unc)
    assert "23-344(b)" in _visible(unc)
    assert constraint_text.REAR_YARD_OPEN_CHECK not in _visible(page1)
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in unc
    assert 'class="label-chip">Conditional</span>' in unc
    # labelled Conditional, never the 1.4.0 Unresolved open-check label (mutation 2).
    assert 'class="label-chip">Unresolved</span>' not in unc
    # no rear-yard MEASUREMENT number is printed in the uncertainties.
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(unc))


def test_s1_benchmark_page_one_rear_yard_uncertainty_is_unchanged() -> None:
    # A 1.4.0 document keeps the page-1 rear-yard uncertainty byte-identical: the title
    # linked to its issue record, ZR 23-344 linked, labelled Unresolved (the open-check
    # reference). The 1.5.0 reading never reaches it (no combined row); mutation 2's
    # open-check path is exactly this 1.4.0 output.
    doc = benchmark()
    assert constraint_text.rear_yard_combined(doc) is None
    html = build_report_html(doc)
    page1 = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    unc = page1[page1.index("What is still uncertain"):]
    unc = unc[:unc.index("</ul>")]
    assert ">Rear yard</a>" in unc
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in unc
    assert 'class="label-chip">Unresolved</span>' in unc
    # the engine's 1.5.0 combined-row text never appears on a 1.4.0 page 1.
    assert "A labelled draft reading, not a DOB determination." not in _visible(unc)
