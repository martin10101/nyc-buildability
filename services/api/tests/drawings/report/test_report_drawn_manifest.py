"""Drawn-content manifest (M5-T173 part B4): every "drawn"/"shown"/"placed" claim
reads what was actually rendered, never a hard-coded constant (audit 2026-10-15c
section 3; H4 R1-R3; D-094 R050/R095/R098).

One case per input state; for each new behaviour the claim is asserted honest and then
the manifest input is flipped and the claim text is shown to move. Expected drawing
roles and the kernel's refusal reasons are read from the modules under test, never
retyped. The new keywords all default so an unwired caller is byte-identical.
"""

from __future__ import annotations

import app.drawings.kit.area_allocation as aa
from app.drawings.kit.model import Unavailable
from app.drawings.report import drawings_embed, page_evidence, page_option_comparison
from app.drawings.report.drawings_embed import Embedded
from app.drawings.report.manifest import DrawnManifest, build_manifest

_SVG_STUB = '<svg viewBox="0 0 10 10" width="10pt" height="10pt"></svg>'
_BUILDINGS = [{"building": "B", "scheduled_value": 20150.0, "scheduled_display": "20,150"}]
_PLACEMENT = {"status": "placed",
              "outline": [[[0.0, 0.0], [100.0, 0.0], [100.0, 66.0], [0.0, 66.0], [0.0, 0.0]]]}


def _valid_block(*, fitted: bool) -> dict:
    # Built from the kernel's OWN contract constants, never retyped literals.
    return {"label": aa._LABEL, "measure": aa._MEASURE, "conversion_statement": aa._CONVERSION,
            "share": 0.6, "apartment_area_sqft": 12090.0, "other_area_sqft": 8060.0,
            "total_sqft": 20150.0, "fitted": fitted}


def _doc_with_block(*, fitted: bool) -> dict:
    return {"building_alternatives": [{"area_allocation": _valid_block(fitted=fitted)}]}


def _chart(*, placed_on_site: bool, footprint_drawn):
    return drawings_embed.allowance_bar_chart_svg(
        "20,150", 20150.0, _BUILDINGS,
        placed_on_site=placed_on_site, footprint_drawn=footprint_drawn)


# ------------------------------------------------------------------ S1 byte-identical
def test_s1_new_keywords_default_to_byte_identical_output() -> None:
    # The chart status: omitting footprint_drawn (the default None, an unwired caller) is
    # byte-identical to passing footprint_drawn=None - both read as not drawn.
    legacy = drawings_embed.allowance_bar_chart_svg("20,150", 20150.0, _BUILDINGS,
                                                    placed_on_site=True)
    assert _chart(placed_on_site=True, footprint_drawn=None) == legacy
    # The option-comparison page and the appendix are byte-identical with the default kwarg.
    doc = _doc_with_block(fitted=True)
    env = {"LANE_E_ENABLED": "1"}
    assert (page_option_comparison.render(doc, {}, env=env)
            == page_option_comparison.render(doc, {}, env=env, footprint_drawn=None))
    assert (page_evidence.render(doc, {}, env=env)
            == page_evidence.render(doc, {}, env=env, illustration_state=None))
    # The appendix method itself is byte-identical for the default state.
    assert (str(page_evidence._area_illustration_method(doc))
            == str(page_evidence._area_illustration_method(doc, None)))


# ------------------------------------------------- S2 build_manifest feeds the chart
def test_s2_manifest_footprint_flag_drives_the_placed_on_site_status() -> None:
    # (1) placement data WITH the footprint kind drawn -> "Shown on the site plan".
    sp_footprint = Embedded(svg=_SVG_STUB, kinds_drawn=("illustrative_footprint",))
    m1 = build_manifest(site_plan=sp_footprint)
    assert m1.site_plan_drawn and m1.site_plan_draws_footprint
    shown = _chart(placed_on_site=True, footprint_drawn=m1.site_plan_draws_footprint)
    assert "Shown on the site plan" in shown and "Worked out; not drawn" not in shown
    # (2) drawn WITHOUT the kind -> "Worked out; not drawn".
    sp_nokind = Embedded(svg=_SVG_STUB, kinds_drawn=())
    m2 = build_manifest(site_plan=sp_nokind)
    assert m2.site_plan_drawn and not m2.site_plan_draws_footprint
    worked = _chart(placed_on_site=True, footprint_drawn=m2.site_plan_draws_footprint)
    assert "Worked out; not drawn" in worked and "Shown on the site plan" not in worked
    # (3) not drawn at all (a short line) -> placed reads "Worked out; not drawn"; not placed
    #     reads "Not demonstrated".
    sp_absent = Embedded(short_line="The site plan is not available for this report.")
    m3 = build_manifest(site_plan=sp_absent)
    assert not m3.site_plan_drawn and not m3.site_plan_draws_footprint
    placed = _chart(placed_on_site=True, footprint_drawn=m3.site_plan_draws_footprint)
    assert "Worked out; not drawn" in placed
    not_placed = _chart(placed_on_site=False, footprint_drawn=m3.site_plan_draws_footprint)
    assert "Not demonstrated" in not_placed
    # site_plan None -> both flags False.
    assert build_manifest(site_plan=None) == DrawnManifest(False, False, False, None)
    # MUTATION: removing the kind flips the chart claim from "Shown" to "Worked out; not drawn".
    reverted = build_manifest(site_plan=Embedded(svg=_SVG_STUB, kinds_drawn=()))
    reverted_chart = _chart(placed_on_site=True, footprint_drawn=reverted.site_plan_draws_footprint)
    assert "Shown on the site plan" not in reverted_chart
    assert "Worked out; not drawn" in reverted_chart


# --------------------------------------------- S3 the appendix method reads the state
def test_s3_appendix_method_reads_the_manifest_illustration_state() -> None:
    bar = drawings_embed._from_result(draw := aa.draw_area_allocation(
        _valid_block(fitted=False), caption=False))
    assert not isinstance(draw, Unavailable)
    zones = drawings_embed._from_result(aa.draw_area_allocation(
        _valid_block(fitted=True), placement=_PLACEMENT, caption=False))
    short = drawings_embed._from_result(aa.draw_area_allocation({}, caption=False))
    assert not short.is_drawing
    # the manifest state is read from the drawn illustration's own data-roles.
    assert build_manifest(site_plan=None, area_illustrations=[zones]).area_illustration_state \
        == "zones"
    assert build_manifest(site_plan=None, area_illustrations=[bar]).area_illustration_state == "bar"
    assert build_manifest(site_plan=None,
                          area_illustrations=[short]).area_illustration_state is None
    assert build_manifest(site_plan=None, area_illustrations=[]).area_illustration_state is None
    # the method text follows the state; never "shown" without a drawn SVG.
    doc = _doc_with_block(fitted=True)
    zones_html = str(page_evidence._area_illustration_method(doc, "zones"))
    assert "it is shown as zones inside the placed building footprint on the scenario sheet" \
        in zones_html
    bar_html = str(page_evidence._area_illustration_method(doc, "bar"))
    assert "it is shown as a proportional bar on the scenario sheet" in bar_html
    none_html = str(page_evidence._area_illustration_method(doc, None))
    assert "it is not yet drawn in this report" in none_html and "it is shown " not in none_html
    # no block -> no method section at all (regardless of any state).
    assert page_evidence._area_illustration_method({"building_alternatives": []}, "bar") is None


def test_s3_not_drawn_state_reads_only_the_manifest_no_legacy_predicate() -> None:
    # M5-T173 part W DELETES the legacy _area_illustration_drawn predicate, so the drawing clause
    # reads ONLY the manifest state: None (an unwired caller) and any explicit not-drawn state both
    # give the "not yet drawn" clause, never a hard-coded "it is shown".
    doc = _doc_with_block(fitted=True)
    assert not hasattr(page_evidence, "_area_illustration_drawn")  # the predicate is gone
    for state in (None, "not_drawn"):
        clause = str(page_evidence._area_illustration_method(doc, state))
        assert "it is not yet drawn in this report" in clause and "it is shown " not in clause


# -------------------------------------------- S4 a refused kernel is never called drawn
def test_s4_nonfinite_share_kernel_refuses_manifest_none_no_inf_nan() -> None:
    bad = dict(_valid_block(fitted=False), share=float("inf"))
    refused = aa.draw_area_allocation(bad, caption=False)
    assert isinstance(refused, Unavailable)
    emb = drawings_embed._from_result(refused)
    assert not emb.is_drawing
    assert "inf" not in emb.short_line.lower() and "nan" not in emb.short_line.lower()
    manifest = build_manifest(site_plan=None, area_illustrations=[emb])
    assert manifest.area_illustration_state is None
    # the appendix method makes no drawn claim for this not-drawn state, and prints no inf/nan.
    method = str(page_evidence._area_illustration_method(
        _doc_with_block(fitted=False), manifest.area_illustration_state))
    assert "it is shown " not in method
    assert "inf" not in method.lower() and "nan" not in method.lower()


# ----------------------------------------------- S5 a zero allowance charts nothing
def test_s5_zero_allowance_is_not_a_zero_bar_pinned() -> None:
    # R020 (DB open question, recorded not changed): an unknown or zero allowance yields no
    # chart, like a missing one - never a zero-height bar. Pinned WITH the new kwarg present.
    assert _chart(placed_on_site=True, footprint_drawn=True) is not None  # a real allowance charts
    assert drawings_embed.allowance_bar_chart_svg("0", 0.0, _BUILDINGS,
                                                  placed_on_site=True, footprint_drawn=True) is None
    assert drawings_embed.allowance_bar_chart_svg(None, None, _BUILDINGS,
                                                  placed_on_site=True,
                                                  footprint_drawn=False) is None


# ------------------------------------ S6 embed_map keeps the map when the footprint fails
class _FakeMap:
    svg = '<svg viewBox="0 0 10 10" width="10" height="10"></svg>'


def test_s6_embed_map_footprint_failure_keeps_map_with_a_note(monkeypatch) -> None:
    import app.drawings.maps as maps
    from app.drawings.report import map_caption

    monkeypatch.setattr(map_caption, "figure_caption", lambda *a, **k: "Sources: tax map")
    calls: list[dict] = []

    def render(mc, *, frame, env=None, **overlay):
        calls.append(dict(overlay))
        if "placed_footprint" in overlay:
            raise ValueError("the footprint label cannot be placed")
        return _FakeMap()

    monkeypatch.setattr(maps, "render_site_context_plan", render, raising=False)
    em = drawings_embed.embed_map(
        "render_site_context_plan", {"map_context": {}}, layers=("tax_lots",), frame="close",
        placed_footprint=[[(0.0, 0.0), (100.0, 0.0), (100.0, 66.0)]])
    # the map is KEPT (not dropped to a short line), with one note naming the footprint.
    assert em.is_drawing
    assert drawings_embed._FOOTPRINT_DROPPED_NOTE in " ".join(em.notes)
    # the first call forwarded the footprint; the retry dropped it.
    assert "placed_footprint" in calls[0] and calls[-1] == {}

    # placed_footprint None gives today's call EXACTLY (no placed_footprint kwarg forwarded).
    calls.clear()
    em2 = drawings_embed.embed_map(
        "render_site_context_plan", {"map_context": {}}, layers=("tax_lots",), frame="close")
    assert em2.is_drawing and em2.notes == ()
    assert calls == [{}]


# ----------------------------------------------- the section flag reads what was drawn
def test_section_drawn_reads_the_embedded_sections() -> None:
    drawn = Embedded(svg=_SVG_STUB)
    absent = Embedded(short_line="The floor-stack section is not available for this report.")
    assert build_manifest(site_plan=None, sections=[absent, drawn]).section_drawn is True
    assert build_manifest(site_plan=None, sections=[absent]).section_drawn is False
    assert build_manifest(site_plan=None, sections=[]).section_drawn is False
