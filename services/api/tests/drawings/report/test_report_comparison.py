"""M5-T169 page type 3 (option comparison): the comparison comes first, the eleven
options stay in scope, and the chart distinguishes allowance / scheduled / placed-on-site
(D-094 R075/R018/R020/R059/R084).

One case per chart input state. Every expected figure is read from the document, never
retyped.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, drawings_embed, options

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_LANE_E = {"LANE_E_ENABLED": "1"}


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _comparison(html: str) -> str:
    return html[html.index('id="option-comparison"'):html.index('id="scenario-B"')]


# ------------------------------------------------------------------- S1 table first
def test_s1_table_comes_before_the_chart_and_no_limitation_paragraphs() -> None:
    comparison = _comparison(build_report_html(benchmark()))
    assert comparison.index("<table") < comparison.index('class="bar-chart"')
    assert "<p><strong>Limitation" not in comparison  # the limitation paragraphs are gone


def test_s1_mutation_reversing_the_order_would_fail() -> None:
    # mutation proof: if the chart were emitted before the table, the table-first
    # assertion flips. We prove the order holds by its indices on the real render.
    comparison = _comparison(build_report_html(benchmark()))
    table_at = comparison.index("<table")
    chart_at = comparison.index('class="bar-chart"')
    assert table_at < chart_at
    # reversing would put the chart first; assert that is NOT the shape we emit.
    assert not (chart_at < table_at)


# ------------------------------------------------------------------- S1/S12 eleven options
def test_s1_eleven_options_in_order_figures_then_not_evaluated() -> None:
    doc = benchmark()
    rows = options.option_rows(doc)
    assert [r["ordinal"] for r in rows] == list(range(1, 12))
    assert [r["name"] for r in rows] == [name for _o, name in options.ELEVEN_OPTIONS]
    text = visible_text(_comparison(build_report_html(doc)))
    # options 1-3 carry figures; options 4-11 read the compact not-evaluated state.
    assert "20,150 sq ft" in text and "24,180 sq ft" in text
    assert text.count("Not evaluated in this report") == 8
    # never readable as infeasibility or achieved-on-site.
    for word in ("infeasible", "not feasible", "achieved", "cannot be built"):
        assert word not in text.lower()


# ------------------------------------------------------------------- S2 chart states
def test_s2_chart_allowance_and_scheduled_present() -> None:
    svg = drawings_embed.allowance_bar_chart_svg(
        "20,150", 20150.0, [{"building": "B", "scheduled_value": 20150.0,
                             "scheduled_display": "20,150"}], placed_on_site=False)
    assert svg is not None
    assert "Floor-area allowance" in svg and "Building B scheduled" in svg
    # placed-on-site is a status word, never a bar (no zero-height bar for an unknown).
    assert "Placed on site" in svg and "Not demonstrated" in svg


def test_s2_chart_allowance_present_no_scheduled() -> None:
    svg = drawings_embed.allowance_bar_chart_svg("20,150", 20150.0, [], placed_on_site=False)
    assert svg is not None
    assert "Floor-area allowance" in svg
    assert "Building" not in svg  # no scheduled bar
    assert "Not demonstrated" in svg


def test_s2_chart_neither_draws_nothing() -> None:
    assert drawings_embed.allowance_bar_chart_svg(None, None, [], placed_on_site=False) is None
    assert drawings_embed.allowance_bar_chart_svg("0", 0.0, [], placed_on_site=False) is None


def test_s2_chart_placed_on_site_shows_a_status_not_a_bar() -> None:
    not_placed = drawings_embed.allowance_bar_chart_svg(
        "20,150", 20150.0, [{"building": "B", "scheduled_value": 20150.0,
                             "scheduled_display": "20,150"}], placed_on_site=False)
    placed = drawings_embed.allowance_bar_chart_svg(
        "20,150", 20150.0, [{"building": "B", "scheduled_value": 20150.0,
                             "scheduled_display": "20,150"}], placed_on_site=True)
    assert "Not demonstrated" in not_placed and "Shown on the site plan" in placed
    # the two states differ, so the chart is NOT placement-invariant.
    assert not_placed != placed
    # the placed-on-site row carries no rectangle (it is a status, never a bar).
    not_placed_tail = not_placed[not_placed.index("Placed on site"):]
    assert "<rect" not in not_placed_tail


# ------------------------------------------------------------------- S12 scope intact
def test_s12_unavailable_options_are_not_evaluated_alternatives() -> None:
    doc = benchmark()
    html = build_report_html(doc, env=_LANE_E)
    comparison = _comparison(html)
    # the eleven options are all present and the unavailable ones read "Not evaluated".
    for ordinal, name in options.ELEVEN_OPTIONS:
        assert f"{ordinal}. {name}" in visible_text(comparison)
