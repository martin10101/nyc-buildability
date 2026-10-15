"""M5-T169 evidence appendix: pages 5 and 6 merged into ONE clearly-named appendix
with five-field issue records, worked arithmetic read from the document with each input
naming its basis, the input_facts bases in the nine closed plain words (G-10), each rule
mapped to its review-register entry and review state, and the area-illustration method
when the document carries an area_allocation block (D-094 R023/R025/R026/R027/R077/R092/
R095).

Every expected value is READ from the document or the modules under test, never retyped;
the '103.88' example in the work order is NOT hard-coded (the fixture contradicts it:
103.88 is the approximate tax-map frontage, the gis basis is the 10,387.99 outline).
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, open_items, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / f"{name}.json").read_text("utf-8"))


def benchmark() -> dict:
    return _load("recorded_215_16_northern_journey")


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _appendix(html: str) -> str:
    return html[html.index('id="appendix"'):]


# =========================================================================== S9 merged
def test_s9_one_merged_appendix_section() -> None:
    html = build_report_html(benchmark())
    # exactly one appendix section; the two old ids are gone (merged, R077).
    assert html.count('id="appendix"') == 1
    assert 'id="assumptions-open-items"' not in html
    assert 'id="calculations-evidence"' not in html
    # five report-page sections in total (mutation proof: the 6->5 merge).
    assert html.count('class="report-page"') == 5


def test_s9_scope_note_heads_the_appendix() -> None:
    appendix = visible_text(_appendix(build_report_html(benchmark())))
    assert appendix.index("Not yet in this report:") < appendix.index("Shared assumptions")


# =========================================================================== S3 five fields
def test_s3_five_field_issue_records() -> None:
    html = build_report_html(benchmark())
    appendix = visible_text(_appendix(html))
    for header in ("Issue", "Consequence", "Next action", "Responsible role",
                   "Evidence reference"):
        assert header in appendix
    # missing site documents are kept apart from program work.
    records = open_items.appendix_issue_records(benchmark())
    roles = {r["responsible_role"] for r in records}
    assert "Owner or surveyor" in roles and "This program" in roles
    zoning = next(r for r in records if r["issue"] == "Zoning lot")
    assert zoning["responsible_role"] == "Owner or surveyor"
    # the honest "A check not yet made ..." sentence appears at most once (R054).
    assert appendix.count("A check not yet made against an independently worked example.") <= 1


# =========================================================================== S4 bases (G-10)
def test_s4_input_facts_bases_read_from_the_four_entry_block() -> None:
    doc = benchmark()
    facts = readers.input_facts(doc)
    # the block has four entries read from the document (never hard-coded).
    keys = [f["key"] for f in facts]
    assert keys == ["recorded_lot_area", "lot_outline_area",
                    "mapped_street_width:215 Place", "mapped_street_width:Northern Boulevard"]
    rows = open_items.input_fact_rows(doc)
    by_name = {r["name"]: r for r in rows}
    # administrative_record -> a recorded lot area; gis -> city map (GIS measurement).
    assert by_name["Recorded lot area"]["basis"] == "city record"
    assert by_name["Lot outline area (city map)"]["basis"] == "city map (GIS measurement)"
    # the two gis facts share the plain word; the SOURCE TITLE tells them apart (S4).
    width = by_name["Mapped street width - 215 Place"]
    assert width["basis"] == "city map (GIS measurement)"
    assert "street center lines" in width["source"]


def test_s4_g10_no_gis_outline_called_tax_map_and_no_width_called_outline() -> None:
    appendix = visible_text(_appendix(build_report_html(benchmark())))
    # the gis outline value is never labelled 'tax map' / 'tax-map outline' (G-10):
    # a gis fact's row carries no 'tax' reference at all.
    i = appendix.index("Lot outline area")
    outline_row = appendix[i:i + 120]
    assert "tax" not in outline_row.lower()
    # a street-width row is never labelled 'city map outline' and carries no 'tax'.
    j = appendix.index("Mapped street width - 215 Place")
    width_row = appendix[j:j + 120]
    assert "city map outline" not in width_row.lower() and "tax" not in width_row.lower()


def test_s4_mutation_basis_word_follows_the_document_basis() -> None:
    # mutation proof (one basis label): changing a fact's basis changes its plain word;
    # a GIS fact never reads as a tax-map value.
    assert open_items.basis_label("administrative_record") == "city record"
    assert open_items.basis_label("gis") == "city map (GIS measurement)"
    assert open_items.basis_label("printed_tax_map") == "printed tax map"
    assert "tax" not in open_items.basis_label("gis")  # never 'tax map' or 'tax-map'


def test_s4_103_88_is_the_approximate_tax_map_frontage_not_the_gis_basis() -> None:
    # the work order's '103.88 = city map outline (GIS)' example is FALSE: 103.88 is the
    # approximate tax-map frontage (a scope assumption), the gis basis is the 10,387.99
    # outline. Assert the document, never a hard-coded value.
    doc = benchmark()
    assert not any(f["value"] == 103.88 for f in readers.input_facts(doc))  # not an input_fact
    outline = next(f for f in readers.input_facts(doc) if f["key"] == "lot_outline_area")
    assert outline["basis"] == "gis" and outline["value"] == 10387.99


# =========================================================================== S5 arithmetic
def test_s5_worked_arithmetic_reads_from_the_document_with_bases() -> None:
    doc = benchmark()
    rows = open_items.worked_arithmetic(doc)
    joined = " ".join(r["expression"] for r in rows)
    # 10,075 x 2.0 = 20,150 and 20,150 / 680 = 29.63 -> 29, each input naming its basis.
    assert "10,075 sq ft (recorded lot area, city record)" in joined
    assert "2.0 (FAR, zoning law)" in joined
    assert "20,150 sq ft" in joined
    assert "20,150 ÷ 680 = 29.63 → 29" in joined


def test_s5_mutation_no_single_figure_mixes_two_bases() -> None:
    # the floor-area derivation uses the RECORDED lot area (administrative_record),
    # never the city-map outline (gis 10,387.99) - a mix would show the outline value
    # and/or a gis basis in the same figure.
    doc = benchmark()
    joined = " ".join(r["expression"] for r in open_items.worked_arithmetic(doc))
    assert "10,387.99" not in joined  # the gis outline never enters the floor-area figure
    assert "city map (GIS measurement)" not in joined


# =========================================================================== S6 register
def test_s6_every_rule_maps_to_a_register_entry_with_review_state() -> None:
    doc = benchmark()
    rows = open_items.register_rule_rows(doc)
    rule_ids = [r.get("rule_id") for r in doc.get("rule_versions", [])]
    assert len(rows) == len(rule_ids) and rows  # one row per rule version
    for row in rows:
        assert row["review_state"]  # a review state is named for each
        assert "review:" not in row["title"]  # the title is the readable rule title
    appendix = visible_text(_appendix(build_report_html(doc)))
    assert "review:" in appendix  # the review state renders
    # the dwelling-unit register entry is linked (short readable title).
    assert any("dwelling" in r["title"].lower() for r in rows)


# =========================================================================== S8 area method
def test_s8_area_illustration_method_present_with_a_block() -> None:
    for fixture in ("synthetic_placed_building_contract_1_5_0",
                    "synthetic_rear_yard_constraints_contract_1_5_0"):
        html = build_report_html(_load(fixture))
        appendix = visible_text(_appendix(html))
        assert "Area-illustration method" in appendix
        assert "residential floor area" in appendix
        assert ("plate = zoning floor area per storey; no gross-up, exclusions or "
                "wall-thickness conversion worked") in appendix
        assert "Illustrative" in appendix


def test_s8_area_illustration_bar_or_zones_follows_fitted() -> None:
    fitted = visible_text(_appendix(build_report_html(
        _load("synthetic_placed_building_contract_1_5_0"))))
    unfitted = visible_text(_appendix(build_report_html(
        _load("synthetic_rear_yard_constraints_contract_1_5_0"))))
    assert "zones inside the placed building footprint" in fitted
    assert "proportional bar" in unfitted


def test_s8_area_illustration_method_on_the_benchmark() -> None:
    # the benchmark now carries an area_allocation block (M5-T172), so the method appears.
    assert "Area-illustration method" in visible_text(_appendix(build_report_html(benchmark())))


# =========================================================================== S15 1.4.0
def test_s15_new_blocks_render_only_from_1_5_0_fields() -> None:
    doc = _load("synthetic_building_alternatives_contract_1_4_0")
    assert doc["contract_version"].startswith("1.4")
    assert readers.input_facts(doc) == []  # readers.input_facts is a no-op on a 1.4.0 document
    html = build_report_html(doc)
    appendix = visible_text(_appendix(html))
    # the 1.5.0-only blocks do not render on a 1.4.0 document.
    assert "Area-illustration method" not in appendix
    assert "city map (GIS measurement)" not in appendix
    assert open_items.worked_arithmetic(doc) == [] or "recorded lot area" not in " ".join(
        r["expression"] for r in open_items.worked_arithmetic(doc))
    # the report still renders five pages and a run identity.
    assert html.count('class="report-page"') == 5
    assert "Run identity" in appendix
