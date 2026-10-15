"""The constraint-line overlay on the site frame (M5-T175; S4, S5, S6).

The overlay draws the results contract 1.5.0 ``geometry.constraint_lines`` ONLY
where a line's state is ``established`` (R017/R044); a not_established or not_known
line carries no geometry and draws nothing, and the legend lists only what is
drawn. The input_facts' other-basis lot dimensions sit BESIDE the map-outline ones,
each naming its own basis, nothing averaged or merged (R015; NB-04). Drawn labels
are at least 8.5 pt with no collisions (S6).

The constraint_lines/input_facts and their expected bases come from the committed
1.5.0 example; the map context is built in memory (no new fixture file; S8).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import style_for
from app.drawings.maps.close_frame_dimensions import (
    OTHER_BASIS_WORDS,
    draw_other_basis_dimensions,
    other_basis_label,
)
from app.drawings.maps.constraint_overlay import (
    ConstraintOverlayError,
    draw_constraint_overlay,
    overlay_offset,
)
from app.drawings.maps.context_scene import ViewFrame, fit_view, viewport
from app.drawings.maps.model import Polygon

from .context_support import cross_street_document

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)


def rear_yard_1_5_0() -> dict:
    return json.loads(
        (_FIXTURES / "synthetic_rear_yard_constraints_contract_1_5_0.json").read_text("utf-8"))


def constraint_lines() -> list[dict]:
    return rear_yard_1_5_0()["geometry"]["constraint_lines"]


def input_facts() -> list[dict]:
    return rear_yard_1_5_0()["input_facts"]


_OFFSET = (1_000_000.0, 200_000.0)  # a plausible EPSG:2263 base for the map lot


def _frame_and_rect(offset=_OFFSET) -> tuple[ViewFrame, tuple[float, float, float, float]]:
    """A ViewFrame + viewport covering the translated constraint geometry, so the
    overlay projects onto a real frame exactly as the site plan would."""
    region = (0.0, 0.0, 512.0, 392.0)
    ox, oy = offset
    window = (ox - 20.0, oy - 20.0, ox + 200.0, oy + 160.0)
    fr = fit_view(window, region, 18.0, alpha=0.0, top_band=0.0)
    return fr, viewport(region, top_band=0.0)


# =========================================================================== S4
def test_s4_only_established_lines_are_drawn() -> None:
    # The fixture carries an established rear_yard_100ft_line and a not_known
    # corner_area (no geometry). Only the established line is drawn; the legend
    # (sheet.kinds) lists only its style, never the not_known one.
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    drawn = draw_constraint_overlay(sheet, constraint_lines(), fr, rect, offset=_OFFSET)
    assert [d.kind for d in drawn] == ["rear_yard_100ft_line"]
    assert "corner_area" not in [d.kind for d in drawn]
    svg = "".join(sheet.parts)
    assert svg.count('data-kind="rear_yard_100ft_line"') >= 1
    assert 'data-kind="corner_area"' not in svg
    # the drawn line's style is in the legend kinds; nothing else was registered.
    assert drawn[0].style_kind in sheet.kinds


def test_s4_a_not_established_line_draws_nothing() -> None:
    # Even when geometry is present, a not_established line is NOT drawn: the state
    # guard (R017), not a missing geometry, is what rejects it (mutation 2).
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    lines = [{"kind": "setback_line", "state": "not_established", "basis": "derived",
              "zr_sections": ["ZR 23-433"], "geometry": [[10.0, 20.0], [70.0, 20.0]]}]
    drawn = draw_constraint_overlay(sheet, lines, fr, rect, offset=_OFFSET)
    assert drawn == []
    assert sheet.parts == [] and sheet.kinds == []


# =========================================================================== S5
def test_s5_drawn_endpoints_lie_on_the_document_vertices() -> None:
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    drawn = draw_constraint_overlay(sheet, constraint_lines(), fr, rect, offset=_OFFSET)
    line = drawn[0]
    # the source points are the document's OWN vertices, within 0.01 ft.
    doc_geometry = [tuple(p) for p in constraint_lines()[0]["geometry"]]
    assert len(line.source_points) == len(doc_geometry)
    for drawn_pt, doc_pt in zip(line.source_points, doc_geometry, strict=True):
        assert abs(drawn_pt[0] - doc_pt[0]) <= 0.01
        assert abs(drawn_pt[1] - doc_pt[1]) <= 0.01
    # the screen points are exactly fr.px(document vertex + offset): the overlay
    # draws the document geometry faithfully, never snapped to the lot outline.
    ox, oy = _OFFSET
    for screen_pt, doc_pt in zip(line.screen_points, doc_geometry, strict=True):
        expected = fr.px((doc_pt[0] + ox, doc_pt[1] + oy))
        assert abs(screen_pt[0] - expected[0]) <= 0.01
        assert abs(screen_pt[1] - expected[1]) <= 0.01


def test_s5_each_input_fact_names_its_own_basis_nothing_merged() -> None:
    facts = input_facts()
    # three facts on three bases: printed_tax_map, administrative_record, gis.
    assert {f["basis"] for f in facts} == {"printed_tax_map", "administrative_record", "gis"}
    words = set(OTHER_BASIS_WORDS.values())
    for fact in facts:
        label = other_basis_label(fact)
        present = [w for w in words if w in label]
        # exactly ONE basis word per label: two bases are never merged (mutation 3).
        assert len(present) == 1, f"{label!r} names {present}"
    # a GIS value reads "map outline", never "tax map".
    gis = next(f for f in facts if f["basis"] == "gis")
    gis_label = other_basis_label(gis)
    assert "map outline" in gis_label
    assert "tax map" not in gis_label


def test_s5_other_basis_dimensions_draw_beside_the_outline() -> None:
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    facts = draw_other_basis_dimensions(sheet, input_facts(), rect)
    assert len(facts) == len(input_facts())
    assert [f.basis for f in facts] == ["printed_tax_map", "administrative_record", "gis"]
    # each label is placed (a box), distinct, none merged.
    assert all(f.label_box is not None for f in facts)
    assert len({f.text for f in facts}) == len(facts)


# =========================================================================== S6
def test_s6_labels_are_at_least_8_5_pt_with_no_collisions() -> None:
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    draw_constraint_overlay(sheet, constraint_lines(), fr, rect, offset=_OFFSET)
    draw_other_basis_dimensions(sheet, input_facts(), rect)
    svg = "".join(sheet.parts)
    sizes = [float(s) for s in re.findall(
        r'data-role="(?:constraint-overlay-label|other-basis-dimension)"[^>]*?font-size="([\d.]+)"',
        svg)]
    # text_element may order attributes either way; also scan the reverse order.
    sizes += [float(s) for s in re.findall(
        r'font-size="([\d.]+)"[^>]*?data-role="(?:constraint-overlay-label|other-basis-dimension)"',
        svg)]
    assert sizes, "no overlay/other-basis labels were drawn"
    assert all(size >= 8.5 for size in sizes)
    # no two placed labels collide (place records a box per label).
    boxes = sheet.boxes
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not a.overlaps(b, 0.0)


def test_s6_an_established_area_is_distinguishable_by_its_hatch() -> None:
    # an established POLYGON constraint is drawn with a hatched area style, so a
    # grey/illustrative copy is distinguishable by hatching.
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    area = [{"kind": "corner_area", "state": "established", "basis": "derived",
             "zr_sections": ["ZR 23-344"],
             "geometry": [[[10.0, 10.0], [70.0, 10.0], [70.0, 60.0], [10.0, 60.0],
                           [10.0, 10.0]]]}]
    drawn = draw_constraint_overlay(sheet, area, fr, rect, offset=_OFFSET)
    assert drawn[0].is_polygon is True
    assert style_for(drawn[0].style_kind).hatch is not None  # it is hatched


def test_s6_a_label_that_cannot_be_placed_fails_rather_than_shrinks() -> None:
    # A rect with no room forces a collision; the overlay FAILS (never shrinks the
    # label below 8.5 pt or drops it).
    fr, rect = _frame_and_rect()
    tiny = (rect[0], rect[1], rect[0] + 1.0, rect[1] + 1.0)
    sheet = Sheet()
    try:
        draw_constraint_overlay(sheet, constraint_lines(), fr, tiny, offset=_OFFSET)
    except ConstraintOverlayError:
        pass
    else:  # pragma: no cover - the assertion documents the expected failure
        raise AssertionError("expected ConstraintOverlayError when no label fits")


# ================================================================ integration
def test_offset_places_results_geometry_on_the_map_lot() -> None:
    # The offset is the subject outline's minimum (x, y); it translates the
    # results-local geometry onto the map lot (never a reprojection).
    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.site_context_plan import draw_site_context_plan

    ctx = load_map_context(cross_street_document())
    ring = ctx.subject_lot.outline.exterior
    assert overlay_offset(ctx.subject_lot.outline) == (
        min(p[0] for p in ring), min(p[1] for p in ring))

    lines = [{"kind": "rear_yard_100ft_line", "state": "established", "basis": "derived",
              "zr_sections": ["ZR 23-344"], "geometry": [[10.0, 20.0], [70.0, 20.0]]}]
    # the large close frame carries the overlay geometry AND its label; the rear-yard
    # line now has its OWN style, so "Rear-yard 100 ft line" appears TWICE - once as the
    # drawing label and once as the legend entry that names what is drawn (S13).
    close = draw_site_context_plan(ctx, frame="close", constraint_lines=lines,
                                   input_facts=input_facts())
    assert 'data-role="constraint-overlay"' in close.svg
    assert close.svg.count("Rear-yard 100 ft line") == 2
    assert "Rear-yard 100 ft line, established" in close.svg  # the drawing label, once
    assert ">Rear-yard 100 ft line</text>" in close.svg       # the legend entry names it
    assert ">Setback line</text>" not in close.svg            # never the reused kind (S13)
    assert "printed tax map" in close.svg
    # the compact page-1 thumbnail carries the geometry but no overlay label (and the
    # summary frame has no legend), so the name appears nowhere there.
    compact = draw_site_context_plan(ctx, frame="summary_close", constraint_lines=lines,
                                     input_facts=input_facts())
    assert 'data-role="constraint-overlay"' in compact.svg
    assert compact.svg.count("Rear-yard 100 ft line") == 0
    # without the overlay args the frame draws no overlay (S1).
    assert 'data-role="constraint-overlay"' not in draw_site_context_plan(ctx, frame="close").svg


# =========================================================================== S13
def _lot_polygon() -> Polygon:
    """The committed 1.5.0 example's lot outline as a Polygon (results-local feet)."""
    ring = rear_yard_1_5_0()["geometry"]["lot_outline"][0]
    return Polygon(rings=(tuple((float(p[0]), float(p[1])) for p in ring),),
                   source="results:lot_outline")


def test_s13_legend_names_the_drawn_rear_yard_line_never_setback() -> None:
    # The legend is generated from the drawn kinds; the rear-yard line has its OWN
    # style, so the legend names "Rear-yard 100 ft line" and never the reused "Setback
    # line" that is not drawn (S13; visual G3 finding 2; mutation 2 reverts this).
    from app.drawings.maps.adapter import load_map_context
    from app.drawings.maps.site_context_plan import draw_site_context_plan

    ctx = load_map_context(cross_street_document())
    lines = [{"kind": "rear_yard_100ft_line", "state": "established", "basis": "derived",
              "zr_sections": ["ZR 23-344"], "geometry": [[10.0, 20.0], [70.0, 20.0]]}]
    close = draw_site_context_plan(ctx, frame="close", constraint_lines=lines)
    assert ">Rear-yard 100 ft line</text>" in close.svg
    assert ">Setback line</text>" not in close.svg


# =========================================================================== S14
def test_s14_established_line_is_drawn_only_inside_the_lot() -> None:
    # The committed example's rear-yard line runs x 0 -> 182.5 while the lot ends near
    # x 123; it is drawn only within the lot outline (the clipped ends lie on the
    # outline within 0.01 ft) and never reaches the far end across the street. Removing
    # the clip (mutation 1) lets the drawn line reach x 182.5.
    from shapely.geometry import Point as SPoint
    from shapely.geometry import Polygon as SPolygon

    fr, rect = _frame_and_rect(offset=(0.0, 0.0))
    poly = _lot_polygon()
    sheet = Sheet()
    drawn = draw_constraint_overlay(sheet, constraint_lines(), fr, rect,
                                    offset=(0.0, 0.0), clip_polygon=poly)
    assert [d.kind for d in drawn] == ["rear_yard_100ft_line"]
    pts = drawn[0].source_points
    xs = [p[0] for p in pts]
    assert max(xs) < 130.0          # stays inside the lot's x-extent, never 182.5
    sp = SPolygon([(p[0], p[1]) for p in poly.exterior])
    for p in pts:                    # every drawn point lies on or inside the lot
        assert sp.distance(SPoint(p)) <= 0.01
    # the clipped ends rest ON the lot boundary within 0.01 ft (S5/S14).
    assert sp.boundary.distance(SPoint(pts[0])) <= 0.01
    assert sp.boundary.distance(SPoint(pts[-1])) <= 0.01
    # without the clip the SAME line reaches the document's far endpoint (mutation 1).
    bare = Sheet()
    bare_drawn = draw_constraint_overlay(bare, constraint_lines(), fr, rect, offset=(0.0, 0.0))
    assert max(p[0] for p in bare_drawn[0].source_points) >= 182.0


def test_s14_a_line_wholly_outside_the_lot_draws_nothing() -> None:
    # An established line entirely outside the lot (beyond its max x ~123, max y ~121)
    # draws nothing - no geometry, no legend entry (S5/S14).
    fr, rect = _frame_and_rect(offset=(0.0, 0.0))
    poly = _lot_polygon()
    sheet = Sheet()
    lines = [{"kind": "rear_yard_100ft_line", "state": "established", "basis": "derived",
              "zr_sections": ["ZR 23-344"], "geometry": [[200.0, 200.0], [300.0, 200.0]]}]
    drawn = draw_constraint_overlay(sheet, lines, fr, rect, offset=(0.0, 0.0), clip_polygon=poly)
    assert drawn == []
    assert sheet.parts == [] and sheet.kinds == []


# =================================================================== S1 (DB-263 A1)
def _established_line() -> list[dict]:
    """A constructed inline established rear-yard line (NOT the shared synthetic
    fixture, which M5-T170 regenerates): three collinear vertices so the label
    anchor is a true interior vertex."""
    return [{"kind": "rear_yard_100ft_line", "state": "established", "basis": "derived",
             "zr_sections": ["ZR 23-344"],
             "geometry": [[10.0, 20.0], [40.0, 20.0], [70.0, 20.0]]}]


def _point_in_box(box, px: float, py: float) -> bool:
    return box.x0 <= px <= box.x1 and box.y0 <= py <= box.y1


def test_s1_the_line_label_sits_off_the_line_so_the_line_stays_visible() -> None:
    # A1: the established LINE label's first candidate is a perpendicular offset OFF
    # the line, so the white-halo label box sits BESIDE the drawn line and a measurable
    # part of the line stays visible. The label anchor (screen_points[mid]) lies OUTSIDE
    # the placed label box. REAL geometry, no monkeypatch (A4).
    # Mutation: revert the first candidate to (0, 0) -> the box sits on the anchor
    # (anchor inside the box) and this test fails.
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    drawn = draw_constraint_overlay(sheet, _established_line(), fr, rect, offset=_OFFSET)
    dc = drawn[0]
    box = dc.label_box
    assert box is not None
    mid = len(dc.screen_points) // 2
    ax, ay = dc.screen_points[mid]
    assert not _point_in_box(box, ax, ay), "the label box sits on the line anchor (line hidden)"
    # a measurable portion of the drawn polyline lies outside every placed label box.
    outside = [p for p in dc.screen_points if not _point_in_box(box, p[0], p[1])]
    assert outside, "the whole drawn line is hidden under the label box"


# =================================================================== S2 (DB-263 A1)
def test_s2_the_label_offset_keeps_the_fit_and_collision_guarantee() -> None:
    # The perpendicular first candidate is only the FIRST candidate; the full grid
    # fallback (and the fail-rather-than-shrink raise) is unchanged (S6). On a normal
    # rect the label places at >= 8.5 pt with no collision; on a rect with no room it
    # still raises ConstraintOverlayError (never shrinks or drops the label).
    fr, rect = _frame_and_rect()
    sheet = Sheet()
    drawn = draw_constraint_overlay(sheet, _established_line(), fr, rect, offset=_OFFSET)
    assert drawn[0].label_box is not None
    boxes = sheet.boxes
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not a.overlaps(b, 0.0)
    tiny = (rect[0], rect[1], rect[0] + 1.0, rect[1] + 1.0)
    try:
        draw_constraint_overlay(Sheet(), _established_line(), fr, tiny, offset=_OFFSET)
    except ConstraintOverlayError:
        pass
    else:  # pragma: no cover - the assertion documents the expected failure
        raise AssertionError("expected ConstraintOverlayError when no label fits")


# =================================================================== S5 (DB-263 A2)
def test_s5_expand_frame_for_overlay_is_gone() -> None:
    # A2 deleted the fragile post-hoc SVG string rewrite: it is defined, exported,
    # imported and called nowhere (the grep check in the producer report is 0 hits).
    from app.drawings.maps import constraint_overlay as co

    assert not hasattr(co, "expand_frame_for_overlay")
    assert "expand_frame_for_overlay" not in co.__all__


# =================================================================== S10 (DB-275)
def _lot_band_rect() -> tuple[float, float, float, float]:
    return (0.0, 0.0, 420.0, 300.0)


def test_s10_street_width_facts_are_not_drawn_in_the_other_basis_band() -> None:
    # DB-275: the two mapped street widths (basis gis since M5-T170) are already drawn
    # on each frontage as '<n> ft mapped width'; they are NOT lot dimensions, so they
    # are excluded from the other-basis LOT-dimension band - no '100 ft, map outline' /
    # '60 ft, map outline' duplicate chips. Mutation: drop the mapped_street_width:*
    # filter -> both chips are drawn and this test fails.
    rect = _lot_band_rect()
    sheet = Sheet()
    facts = [
        {"key": "mapped_street_width:Northern Boulevard", "value": 100.0, "unit": "ft",
         "basis": "gis"},
        {"key": "mapped_street_width:215 Place", "value": 60.0, "unit": "ft", "basis": "gis"},
        {"key": "recorded_lot_area", "value": 9800.0, "unit": "sq_ft",
         "basis": "administrative_record"},
    ]
    drawn = draw_other_basis_dimensions(sheet, facts, rect)
    assert [f.key for f in drawn] == ["recorded_lot_area"]  # only the lot dimension
    svg = "".join(sheet.parts)
    assert "100 ft, map outline" not in svg
    assert "60 ft, map outline" not in svg


def test_s10_without_street_width_facts_the_lot_band_is_unchanged() -> None:
    # The lot's own other-basis figures are unchanged whether or not street widths are
    # present: the filtered band draws the same lot facts, in the same order, same text.
    rect = _lot_band_rect()
    only_lot = [{"key": "recorded_lot_area", "value": 9800.0, "unit": "sq_ft",
                 "basis": "administrative_record"}]
    a = draw_other_basis_dimensions(Sheet(), only_lot, rect)
    with_street = [
        {"key": "mapped_street_width:Northern Boulevard", "value": 100.0, "unit": "ft",
         "basis": "gis"},
        *only_lot,
    ]
    b = draw_other_basis_dimensions(Sheet(), with_street, rect)
    assert [f.key for f in b] == [f.key for f in a] == ["recorded_lot_area"]
    assert [f.text for f in b] == [f.text for f in a]


def test_s10_a_lot_gis_fact_still_reads_map_outline() -> None:
    # The filter keys on the KEY (mapped_street_width:*), not the gis basis: a lot's
    # OWN gis dimension (a different key) is still drawn and still reads 'map outline'.
    rect = _lot_band_rect()
    facts = [
        {"key": "mapped_street_width:Northern Boulevard", "value": 100.0, "unit": "ft",
         "basis": "gis"},
        {"key": "outline_lot_area", "value": 10075.0, "unit": "sq_ft", "basis": "gis"},
    ]
    drawn = draw_other_basis_dimensions(Sheet(), facts, rect)
    assert [f.key for f in drawn] == ["outline_lot_area"]
    assert drawn[0].basis_label == "map outline"
    assert "map outline" in drawn[0].text
