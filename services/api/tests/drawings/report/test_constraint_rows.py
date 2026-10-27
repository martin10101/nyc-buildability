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
# M5-T167 (scope correction 2, R039/R136): the regenerated benchmark now carries the
# engine's 1.5.0 rear_yard block, so its page-3 rows take the results path and show the
# applied result. The reference case (docs/reference-cases/R6B/short-block-rear-yard.md,
# real-lot-z1/z2) says the rear yard is not known / Conditional, naming ZR 23-344(b) and
# (c)(3); never an unconditional "no rear yard". (The synthetic cases below still pin the
# 1.4.0 fall-back; a genuinely-1.4.0 document reaches them, not the benchmark.)
def test_s1_benchmark_rear_yard_row_shows_the_applied_conditional_result() -> None:
    doc = benchmark()
    assert constraint_text.has_results_rows(doc) is True
    combined = constraint_text.rear_yard_combined(doc)
    assert combined["state"] == "not_known"
    assert combined["way"] == "conditional"
    # the combined conditions name the short-block rule (b) and the adjoining-side-line rule
    # (c)(3), as the reference case requires - not a bare ZR 23-344.
    conds = " ".join(c["assumption"] for c in combined["conditions"])
    assert "23-344(b)" in conds and "23-344(c)(3)" in conds
    row = _row_by_title(doc, "Rear yard")
    assert row is not None
    _title, cell, chip = row
    assert combined["text"] in cell                       # the row's own text
    assert 'class="label-chip">Conditional</span>' in chip
    # ZR 23-344 is linked to its captured official text, and the row links its open item.
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in cell
    assert ">ZR 23-344</a>" in cell
    assert f'href="#issue-{_item_number(doc)["rear_yard"]}"' in cell
    # no rear-yard MEASUREMENT number is printed, and never an unconditional "no rear yard".
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(cell))
    low = _visible(cell).lower()
    assert "no rear yard" not in low or "no rear yard is required within 100 feet" in low


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


def test_s9_page_three_side_yard_links_its_numbered_open_item() -> None:
    # G4 advisory 4: page 3's side-yard row now carries the same "see item N" link the setback
    # and street-wall rows have (_ENVELOPE_CATEGORY maps side_yard to its own numbered open item).
    doc = rear_yard_1_5_0()
    number = _item_number(doc)["side_yard"]
    row = _row_by_title(doc, "Side yard")
    assert row is not None
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


def _other_basis_texts(html: str) -> list[str]:
    """Every OTHER-BASIS lot-dimension label drawn on the page-4 close frame (the input_facts
    overlay, ``data-role="other-basis-dimension"``). This excludes BOTH the scenario-sheet area
    caption (page 6) and the page-4 drawn-footprint clearance caption (M5-T173 part B), which both
    name the printed-tax-map basis in prose; scoping to the overlay labels keeps these tests on the
    page-4 overlay itself (carry item 2)."""
    return re.findall(r'<text[^>]*data-role="other-basis-dimension"[^>]*>([^<]*)</text>', html)


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
    # the rear-yard line now has its OWN legend entry (S13), so "Rear-yard 100 ft line"
    # appears TWICE on the close frame: the drawing label once and the legend entry once.
    assert html.count("Rear-yard 100 ft line") == 2
    assert "Rear-yard 100 ft line, established" in html   # the drawing label, once
    assert ">Rear-yard 100 ft line</text>" in html        # the legend names what is drawn
    assert ">Setback line</text>" not in html             # never the reused kind (S13)
    # neither the not_established line (geometry present) nor the not_known corner_area
    # draws (R017/R044; mutation 3 draws the not_established one).
    assert 'data-kind="setback_line"' not in html
    assert 'data-kind="corner_area"' not in html
    # the input_facts' other-basis lot dimensions draw beside the map outline, each basis
    # named (the printed-tax-map frontage and the recorded area) as page-4 overlay labels;
    # dropping the wiring (mutation 1) removes them. Scoped to the overlay labels so the
    # scenario-sheet / drawn-footprint prose captions cannot pass this for it (carry item 2).
    overlay_labels = _other_basis_texts(html)
    assert any("printed tax map" in t for t in overlay_labels)
    assert any("city record" in t for t in overlay_labels)


def test_s12_1_4_0_report_with_maps_draws_no_overlay() -> None:
    # The benchmark carries no ESTABLISHED constraint line, so the live report draws no
    # constraint overlay and no rear-yard line. It carries input_facts, so it DOES draw the
    # recorded-area / map-outline other-basis dimensions - but NOT a printed-tax-map frontage
    # one (it has no such fact). "printed tax map" is no longer checked absent in the whole
    # html: the placed footprint's drawn-state caption (M5-T173 part B) names the printed-tax-
    # map and city-map clearances in prose (owner standard - both bases named, neither hidden),
    # so the string legitimately appears. The overlay check scopes to the drawn overlay labels.
    html = _report_with_maps(benchmark())
    assert 'data-role="constraint-overlay"' not in html
    assert "Rear-yard 100 ft line" not in html
    assert not any("printed tax map" in t for t in _other_basis_texts(html))


def test_s12_page_one_uncertainty_reads_the_1_5_0_conditional_rear_yard() -> None:
    doc = rear_yard_1_5_0()
    combined = constraint_text.rear_yard_combined(doc)
    assert combined["way"] == "conditional"
    html = build_report_html(doc)  # the page-1 uncertainty text needs no map
    page1 = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    unc = page1[page1.index("What is still uncertain"):]
    unc = unc[:unc.index("</ul>")]
    # the page-1 rear-yard uncertainty shows the combined row's OWN reading (not the
    # open-check wording), labelled Conditional, with ZR 23-344 linked - the same reading
    # the page-3 row shows, from the one wording source (mutation 2 reverts this). On
    # page 1 the leading title is stripped (S16), so the body of the combined text shows
    # without the "Rear yard Rear yard:" stutter.
    assert "a conditional no-rear-yard reading under ZR 23-344(b)" in _visible(unc)
    assert "Rear yard Rear yard" not in _visible(unc)
    assert "23-344(b)" in _visible(unc)
    assert constraint_text.REAR_YARD_OPEN_CHECK not in _visible(page1)
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in unc
    assert 'class="label-chip">Conditional</span>' in unc
    # labelled Conditional, never the 1.4.0 Unresolved open-check label (mutation 2).
    assert 'class="label-chip">Unresolved</span>' not in unc
    # no rear-yard MEASUREMENT number is printed in the uncertainties.
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(unc))


def test_s1_benchmark_page_one_rear_yard_uncertainty_shows_the_conditional_reading() -> None:
    # M5-T167 (scope correction 2): the regenerated benchmark carries the 1.5.0 rear_yard
    # combined row, so the page-1 rear-yard uncertainty now shows that conditional reading
    # (R037/R136), labelled Conditional, with ZR 23-344 linked - no longer the 1.4.0
    # Unresolved open-check label. The expected result is the reference case's not-known /
    # Conditional real-lot answer, never an unconditional "no rear yard".
    doc = benchmark()
    combined = constraint_text.rear_yard_combined(doc)
    assert combined is not None and combined["way"] == "conditional"
    html = build_report_html(doc)
    page1 = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    unc = page1[page1.index("What is still uncertain"):]
    unc = unc[:unc.index("</ul>")]
    assert ">Rear yard</a>" in unc
    assert combined["text"] in unc                        # the combined row's own reading
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in unc
    assert 'class="label-chip">Conditional</span>' in unc
    # no longer the 1.4.0 Unresolved open-check label, nor the open-check wording.
    assert 'class="label-chip">Unresolved</span>' not in unc
    assert constraint_text.REAR_YARD_OPEN_CHECK not in _visible(page1)
    # never an unconditional "no rear yard"; no rear-yard measurement number printed.
    low = _visible(unc).lower()
    assert "no rear yard" not in low or "no rear yard is required within 100 feet" in low
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(unc))


# ========================================================================== S13
# The overlay adds a legend entry on the close frame; the frame grows so the whole
# legend, including 'No building placed', fits above the sources caption - a frame
# without the overlay stays byte-identical (visual G3 finding 1).
def _vb_height(svg: str) -> float:
    return float(re.search(r'viewBox="0 0 [\d.]+ ([\d.]+)"', svg).group(1))


def test_s13_overlay_legend_fits_and_the_plain_frame_is_unchanged() -> None:
    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.site_context_plan import draw_site_context_plan

    ctx = load_map_context(map_context())
    doc = rear_yard_1_5_0()
    with_overlay = draw_site_context_plan(
        ctx, frame="close", constraint_lines=doc["geometry"]["constraint_lines"],
        input_facts=doc["input_facts"])
    plain = draw_site_context_plan(ctx, frame="close")
    over_h, plain_h = _vb_height(with_overlay.svg), _vb_height(plain.svg)
    # the overlay adds a legend row, so the frame grows (it was clipped at 470 before).
    assert over_h > plain_h
    # the 'No building placed' legend row sits fully WITHIN the grown frame height.
    ny = float(re.search(
        r'<text[^>]*\sy="([\d.]+)"[^>]*>No building placed', with_overlay.svg).group(1))
    assert ny + 2.0 <= over_h
    # the frame without the overlay is byte-identical to today (height unchanged at 470).
    assert plain_h == 470.0


# ========================================================================== S15
# When the overlay cannot be drawn (a label that cannot be placed at 8.5 pt raises by
# design, or a malformed established geometry), the site map is kept WITHOUT the overlay
# and carries one short note; the whole map is never dropped (code-review advisories).
_S15_NOTE = "A zoning line could not be drawn on this map; page 3 lists it."


class _FakeMap:
    svg = '<svg viewBox="0 0 10 10" width="10" height="10"></svg>'


def _fake_render(exc):
    """A site-context map fn that raises ``exc`` when the overlay is requested and
    draws the plain map otherwise - i.e. the overlay is what fails, not the map."""
    def render(mc, *, frame, env=None, **overlay):
        if overlay:
            raise exc
        return _FakeMap()
    return render


def test_s15_overlay_failure_keeps_the_map_with_a_note(monkeypatch) -> None:
    import app.drawings.maps as maps
    from app.drawings.maps.constraint_overlay import ConstraintOverlayError
    from app.drawings.report import drawings_embed, map_caption

    monkeypatch.setattr(map_caption, "figure_caption", lambda *a, **k: "Sources: tax map")
    # both overlay-failure kinds: a label that cannot be placed, and a malformed geometry.
    for exc in (ConstraintOverlayError("no room"), ValueError("malformed geometry")):
        monkeypatch.setattr(maps, "render_site_context_plan", _fake_render(exc), raising=False)
        em = drawings_embed.embed_map(
            "render_site_context_plan", {"map_context": {}}, layers=("tax_lots",),
            frame="close", constraint_lines=[{"kind": "x"}], input_facts=[{"key": "y"}])
        assert em.is_drawing  # the map is KEPT (not dropped to a short line)
        assert _S15_NOTE in " ".join(em.notes)


def test_s15_report_keeps_the_site_map_when_overlay_geometry_is_malformed() -> None:
    doc = rear_yard_1_5_0()
    # a malformed established geometry (non-numeric) makes the overlay raise; the live
    # report keeps the site map (drawn without the overlay) and page 3 carries the note.
    doc["geometry"]["constraint_lines"] = [{
        "kind": "rear_yard_100ft_line", "state": "established", "basis": "derived",
        "zr_sections": ["ZR 23-344"], "geometry": [[0.0, "bad"], [10.0, 10.0]]}]
    html = _report_with_maps(doc)
    assert "A zoning line could not be drawn on this map; page 3 lists it." in html
    assert 'data-drawing="site_context_plan"' in html  # the base map is still drawn
    assert 'data-role="constraint-overlay"' not in html  # the overlay itself is absent


# ========================================================================== S16
def test_s16_page_one_rear_yard_uncertainty_does_not_repeat_its_title() -> None:
    doc = rear_yard_1_5_0()
    html = build_report_html(doc)
    page1 = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    unc = page1[page1.index("What is still uncertain"):]
    unc = unc[:unc.index("</ul>")]
    vis = _visible(unc)
    # the title (the link label) is NOT repeated by the combined text (mutation: not
    # stripping the leading title produces "Rear yard Rear yard:").
    assert "Rear yard Rear yard" not in vis
    # the reading still shows (its body after the stripped title).
    assert "a conditional no-rear-yard reading under ZR 23-344(b)" in vis


def test_s16_not_known_rear_yard_check_prints_no_number() -> None:
    doc = rear_yard_1_5_0()
    c3 = next(c for c in constraint_text.rear_yard_checks(doc)
              if c.get("provision") == "23-344(c)(3)")
    assert c3["state"] == "not_known"
    assert "inputs" not in c3           # a not_known check carries no measured value
    assert c3.get("text")               # it has its own reason text
    # the check's text prints no ft / sq ft figure of its own.
    assert not re.search(r"\d+(\.\d+)?\s*(ft|sq ft)", _visible(str(c3["text"])))
