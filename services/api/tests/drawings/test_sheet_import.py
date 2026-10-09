"""Acceptance pack for the PKT-L PDF sheet import SERVICE (task M5-T121, D-087 phase C2/C3).

Fully offline and deterministic. Exercises :mod:`app.drawings.sheet_import` against
KEYWORD-CONSTRUCTED reader value types (``SheetDocument`` / ``SheetPage`` /
``SheetPolyline`` / ``SheetTextRun`` / ``SheetImage`` / ``SheetRefusal``) - the reader
modules are being edited by M5-T120 in parallel, so this pack imports ONLY the public
reader value types (never ``read_sheet``, so nothing pulls the ``app.documents`` 3.12
chain) and builds every fixture here by keyword so an appended defaulted reader field
cannot break it.

- AS-1 (candidates): closed rings only, addressed by their STABLE polyline index,
  bounded with the total disclosed, measured in SHEET units; the page disclosure; scale
  notes listed escaped and NEVER parsed; out-of-range page and no-closed-ring pages are
  honest typed results.
- AS-2 (scale): one user-named edge + its real length; the SERVICE measures the edge
  itself; scale = known feet / measured length (exact arithmetic asserted); invalid
  inputs refuse typed; there is NO client-measurement channel.
- AS-3 (draft): the ASSIGNED ring scaled with explicit closure through
  ``validate_proposed_massing``; kind stays 'proposed'; a contract violation is a typed
  ``draft_invalid`` refusal.
- AS-4 (honesty + provenance): input_class imported_pdf, the precision / label / frame
  note, the scale inputs and roles; no permit / approved / maximum-allowed wording;
  precision never upgraded; every drawing-derived string escaped and bounded.

Each guard has a reddening in-process MUTATION (mutating the CONSUMING namespace) that
proves the test constrains the guard.
"""

from __future__ import annotations

import math

from app.drawings import sheet_import as svc
from app.drawings.sheet_import import (
    DRAFT_INPUT_CLASS,
    DRAFT_INPUT_PRECISION,
    DRAFT_SOURCE_LABEL,
    FRAME_NOTE,
    SHEET_UNIT_NAME,
    Candidate,
    ImportRefusal,
    RoleAssignment,
    build_draft,
    list_candidates,
    measured_dimensions,
)
from app.drawings.sheet_primitives import (
    SheetDocument,
    SheetImage,
    SheetPage,
    SheetPolyline,
    SheetRefusal,
    SheetTextRun,
)

_IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

# Rings in real NYC EPSG:2263 (US survey feet) space so a draft can pass the contract.
_RING = [(985000.0, 195000.0), (985080.0, 195000.0), (985080.0, 195100.0), (985000.0, 195100.0)]
# Two DISTINCT closed in-bounds rings for the user-assigned-ring test. Ring A is the LARGER
# (200x200 vs 80x100), so BOTH an always-first-ring mutant AND a largest-ring mutant would
# wrongly pick ring A (stable index 0) instead of the user-assigned ring B (stable index 1).
_RING_A = [(985000.0, 195000.0), (985200.0, 195000.0), (985200.0, 195200.0), (985000.0, 195200.0)]
_RING_B = [(990000.0, 200000.0), (990080.0, 200000.0), (990080.0, 200100.0), (990000.0, 200100.0)]
# Half-scale ring: edge 0 measures 40 sheet units; known_length_ft=80 -> scale 2.0; scaled by
# 2.0 it becomes EXACTLY _RING (in NYC bounds). Proves scale = known / SERVICE-measured edge.
_HALF = [(492500.0, 97500.0), (492540.0, 97500.0), (492540.0, 97550.0), (492500.0, 97550.0)]
# A near-origin (local, ungeoreferenced) ring: the massing contract refuses it, never corrects.
_NEAR_ORIGIN = [(0.0, 0.0), (80.0, 0.0), (80.0, 100.0), (0.0, 100.0)]
# Individually finite but overflow the measured dimensions to inf.
_OVERFLOW = [(1e300, 1e300), (1e300, 2e300), (2e300, 2e300), (2e300, 1e300)]
# A closed ring whose edge 0 is zero-length (points[0] == points[1]) - a degenerate scale edge.
_DEGEN_EDGE = [(985000.0, 195000.0), (985000.0, 195000.0), (985080.0, 195100.0)]
# POSITIVE claim words that must never appear anywhere in a draft. "city record" is absent
# on purpose: the honest label legitimately reads "Proposed - not a city record" (a negation).
_FORBIDDEN_WORDS = (
    "permitted", "approved", "maximum allowed", "as of right", "demonstrated maximum",
)


def _poly(points, *, closed=True, stroked=True, filled=False) -> SheetPolyline:
    return SheetPolyline(points=tuple(points), closed=closed, stroked=stroked, filled=filled)


def _text(text, *, x=0.0, y=0.0, size=10.0) -> SheetTextRun:
    return SheetTextRun(text=text, x=x, y=y, font_size=size, matrix=_IDENT)


def _img(name="Im0") -> SheetImage:
    return SheetImage(
        name=name, matrix=_IDENT, width=100, height=100, bits_per_component=8,
        color_space="DeviceRGB",
    )


def _page(
    polylines=(), *, index=0, text_runs=(), images=(), shading_skips=0,
    inline_image_skips=0, user_unit=1.0,
) -> SheetPage:
    return SheetPage(
        index=index, media_box=(0.0, 0.0, 612.0, 792.0), user_unit=user_unit,
        flatten_tolerance=0.1, polylines=tuple(polylines), text_runs=tuple(text_runs),
        images=tuple(images), shading_skips=shading_skips,
        inline_image_skips=inline_image_skips,
    )


def _doc(*pages) -> SheetDocument:
    return SheetDocument(flatten_tolerance=0.1, pages=tuple(pages))


def _doc_single() -> SheetDocument:
    return _doc(_page([_poly(_RING)]))


def _doc_half() -> SheetDocument:
    return _doc(_page([_poly(_HALF)]))


def _doc_two() -> SheetDocument:
    return _doc(_page([_poly(_RING_A), _poly(_RING_B)]))


def _assign(**over) -> RoleAssignment:
    base = dict(
        building_outline=0, floors=5, floor_to_floor_ft=11.0, author="Jane Architect",
        scale_candidate=0, scale_edge=0, known_length_ft=80.0,
    )
    base.update(over)
    return RoleAssignment(**base)


# --------------------------------------------------------------------------- AS-1 candidates


def test_candidates_list_closed_rings_by_stable_index_measured_in_sheet_units():
    # polyline 0 open, 1 closed ring, 2 closed ring, 3 degenerate closed (2 points).
    page = _page(
        [_poly(_RING, closed=False), _poly(_RING_A), _poly(_RING_B),
         _poly([(1.0, 1.0), (2.0, 2.0)])]
    )
    result = list_candidates(_doc(page), 0)
    assert result.ok
    # candidates are the CLOSED rings addressed by STABLE polyline index (1 and 2), not 0..k.
    assert {c.index for c in result.candidates} == {1, 2}
    assert result.total_closed_rings == 2
    # largest area first: ring A (index 1, 200x200) precedes ring B (index 2, 80x100).
    assert result.candidates[0].index == 1
    cand = result.candidates[0]
    assert isinstance(cand, Candidate)
    assert cand.vertex_count == 4
    assert cand.measured["units"] == SHEET_UNIT_NAME
    assert cand.measured["bbox_width"] == 200.0
    assert cand.measured["area"] == 40000.0


def test_open_polyline_is_disclosed_not_a_candidate():
    result = list_candidates(_doc(_page([_poly(_RING, closed=False)])), 0)
    assert result.candidates == ()
    assert result.disclosure["open_polylines"] == 1


def test_degenerate_closed_ring_is_disclosed_not_silently_absent():
    result = list_candidates(_doc(_page([_poly([(1.0, 1.0), (2.0, 2.0)])])), 0)
    assert result.candidates == ()
    assert result.disclosure["open_polylines"] == 0  # it IS closed
    assert result.disclosure["degenerate_closed_rings"] == 1


def test_page_disclosure_counts_text_images_and_skip_counts():
    page = _page(
        [_poly(_RING)], text_runs=[_text("north elevation"), _text("plan")],
        images=[_img("Im0"), _img("Im1")], shading_skips=3, inline_image_skips=2,
    )
    result = list_candidates(_doc(page), 0)
    assert result.disclosure["text_runs"] == 2
    assert result.disclosure["images"] == 2
    assert result.disclosure["shading_skips"] == 3
    assert result.disclosure["inline_image_skips"] == 2


def test_scale_notes_are_listed_escaped_and_never_parsed():
    page = _page(
        [_poly(_RING)],
        text_runs=[_text('SCALE: 1/8"=1\'-0"'), _text("floor plan"), _text("scale bar\x01")],
    )
    result = list_candidates(_doc(page), 0)
    # only text runs containing "scale" (case-insensitive) are listed; "floor plan" is not.
    assert len(result.scale_notes) == 2
    assert any('1/8"=1' in n for n in result.scale_notes)
    # a control char inside a scale note is escaped, never emitted raw, and never parsed.
    assert any("\\x01" in n for n in result.scale_notes)
    assert all("\x01" not in n for n in result.scale_notes)
    # a note is a plain reference string; nothing consumed it into a scale.
    assert result.ok and isinstance(result.scale_notes, tuple)


def test_no_closed_ring_page_is_an_honest_typed_result():
    result = list_candidates(_doc(_page([_poly(_RING, closed=False)])), 0)
    assert result.ok
    assert result.candidates == ()
    assert "not joined" in result.disclosure["note"]


def test_page_out_of_range_is_an_honest_typed_result():
    r = list_candidates(_doc_single(), 5)
    assert isinstance(r, ImportRefusal) and r.reason == "page_out_of_range"
    neg = list_candidates(_doc_single(), -1)
    assert isinstance(neg, ImportRefusal) and neg.reason == "page_out_of_range"


def test_reader_refusal_maps_to_typed_import_refusal_escaped():
    refusal = SheetRefusal(
        reject_code="sheet_profile", feature="operator", detail="bad\x01value",
        origin="sheet_profile",
    )
    out = list_candidates(refusal, 0)
    assert isinstance(out, ImportRefusal) and out.reason == "unreadable_pdf"
    assert "\x01" not in out.detail
    assert "\\x01" in out.detail


def test_overflow_coordinates_refuse_typed_never_non_finite():
    result = list_candidates(_doc(_page([_poly(_OVERFLOW)])), 0)
    assert isinstance(result, ImportRefusal)
    assert result.reason == "coordinate_out_of_range"


def test_measured_dimensions_reused_from_dxf_import():
    # the reused public helper, measuring a ring's perimeter/area in a sheet unit label.
    m = measured_dimensions(tuple(_RING), SHEET_UNIT_NAME)
    assert m["perimeter"] == 360.0  # 80 + 100 + 80 + 100
    assert m["area"] == 8000.0
    assert m["units"] == SHEET_UNIT_NAME


# --------------------------------------------------------------------------- AS-2 scale


def test_scale_is_measured_from_geometry_exact_arithmetic():
    # _HALF edge 0 measures 40 sheet units; known_length_ft=80 -> scale EXACTLY 2.0; the
    # scaled outline is _RING. Proves the SERVICE measured the edge (40), not any supplied value.
    draft = build_draft(_doc_half(), 0, _assign())
    assert draft.ok
    assert draft.provenance["scale"]["measured_sheet_length"] == 40.0
    assert draft.provenance["scale"]["scale_ft_per_unit"] == 2.0
    assert draft.proposed_massing["outline"]["vertices"][0] == [985000.0, 195000.0]


def test_role_assignment_has_no_client_measurement_channel():
    # Structural proof the caller cannot supply the sheet measurement (the DXF path HAD a
    # client-supplied measured_length; this removes it - the service always measures).
    fields = RoleAssignment.__dataclass_fields__
    assert "measured_length" not in fields
    assert "client_measured_length" not in fields
    assert "known_length_ft" in fields  # the real-world length is supplied; the measurement is not


def test_invalid_known_length_refused_typed():
    for bad in (0.0, -5.0, float("nan"), float("inf"), svc.MAX_KNOWN_LENGTH_FT + 1.0):
        r = build_draft(_doc_single(), 0, _assign(known_length_ft=bad))
        assert isinstance(r, ImportRefusal), bad
        assert r.reason == "invalid_scale", bad


def test_bad_scale_edge_refused_typed():
    r = build_draft(_doc_single(), 0, _assign(scale_edge=99))
    assert isinstance(r, ImportRefusal) and r.reason == "bad_edge"


def test_degenerate_scale_edge_refused_typed():
    # scale_candidate 1 is a closed ring whose edge 0 is zero-length -> no scale.
    doc = _doc(_page([_poly(_RING), _poly(_DEGEN_EDGE)]))
    r = build_draft(doc, 0, _assign(scale_candidate=1, scale_edge=0))
    assert isinstance(r, ImportRefusal) and r.reason == "invalid_scale"


def test_bad_scale_candidate_refused_typed():
    r = build_draft(_doc_single(), 0, _assign(scale_candidate=7))
    assert isinstance(r, ImportRefusal) and r.reason == "bad_candidate"


# --------------------------------------------------------------------------- AS-3 draft


def test_draft_built_from_assigned_ring_scaled_with_explicit_closure():
    draft = build_draft(_doc_single(), 0, _assign())
    assert draft.ok
    block = draft.proposed_massing
    verts = block["outline"]["vertices"]
    assert verts[0] == verts[-1]  # closure made EXPLICIT
    assert block["outline"]["srid"] == 2263
    assert block["levels"][0]["floor_count"] == 5
    assert block["provenance"]["kind"] == "proposed"  # contract kind stays 'proposed'


def test_draft_uses_the_user_assigned_ring_not_first_or_largest():
    # TWO distinct closed in-bounds rings; the user assigns building_outline=1, so the draft
    # MUST be built from ring B (stable index 1), not ring A (index 0, larger).
    draft = build_draft(_doc_two(), 0, _assign(building_outline=1, scale_candidate=1))
    assert draft.ok
    assert draft.proposed_massing["outline"]["vertices"][0] == [990000.0, 200000.0]
    assert draft.provenance["assigned_roles"]["building_outline"] == 1


def test_out_of_bounds_local_ring_refused_by_the_contract():
    # a near-origin (local, ungeoreferenced) ring fails the NYC-bounds contract; the service
    # surfaces the field, never auto-corrects / georeferences.
    r = build_draft(_doc(_page([_poly(_NEAR_ORIGIN)])), 0, _assign())
    assert isinstance(r, ImportRefusal) and r.reason == "draft_invalid"
    assert r.field and r.field.startswith("proposed_massing.outline")


def test_bad_building_outline_index_refused_typed():
    r = build_draft(_doc_single(), 0, _assign(building_outline=7))
    assert isinstance(r, ImportRefusal) and r.reason == "bad_candidate"


# --------------------------------------------------------------------------- AS-4 honesty


def test_provenance_block_is_complete_and_honest():
    draft = build_draft(_doc_half(), 0, _assign(property_line=None, street_frontage=None))
    prov = draft.provenance
    assert prov["input_class"] == DRAFT_INPUT_CLASS == "imported_pdf"
    assert prov["precision"] == DRAFT_INPUT_PRECISION
    assert prov["label"] == DRAFT_SOURCE_LABEL
    assert prov["page_index"] == 0
    assert prov["frame_note"] == FRAME_NOTE
    assert "not aligned to the mapped lot" in prov["frame_note"]
    assert prov["scale"]["known_length_ft"] == 80.0
    assert prov["scale"]["edge_index"] == 0
    assert prov["assigned_roles"]["building_outline"] == 0
    blob = str(prov).lower() + str(draft.proposed_massing).lower()
    for word in _FORBIDDEN_WORDS:
        assert word not in blob


def test_author_drawing_string_is_escaped_in_provenance():
    draft = build_draft(_doc_half(), 0, _assign(author="Jane\x01Architect"))
    assert "\x01" not in draft.provenance["author"]
    assert "\\x01" in draft.provenance["author"]


# --------------------------------------------------------------------------- AS-5 scope


def test_no_persistence_two_identical_calls_are_equal():
    a = build_draft(_doc_half(), 0, _assign())
    b = build_draft(_doc_half(), 0, _assign())
    assert a.proposed_massing == b.proposed_massing
    assert a.provenance == b.provenance


# --------------------------------------------------------------------------- reddening mutations
# Each guard: mutate the CONSUMING namespace and prove the protected behaviour flips.


def test_mutation_closed_flag_gates_candidates(monkeypatch):
    # Neuter the closed-ring gate so EVERY polyline becomes a candidate -> an open ring now
    # lists, proving the real gate excludes it (AS-1).
    monkeypatch.setattr(
        svc, "_closed_ring_candidates", lambda page: list(enumerate(page.polylines))
    )
    result = list_candidates(_doc(_page([_poly(_RING, closed=False)])), 0)
    assert len(result.candidates) == 1  # reddens test_open_polyline_is_disclosed_not_a_candidate


def test_mutation_overflow_finiteness_guard(monkeypatch):
    # Drop the finiteness guard -> the overflow ring lists a non-finite measured value,
    # proving the real guard is what refuses it typed (AS-1).
    monkeypatch.setattr(svc, "_measured_is_finite", lambda measured: True)
    result = list_candidates(_doc(_page([_poly(_OVERFLOW)])), 0)
    assert result.ok  # reddens test_overflow_coordinates_refuse_typed_never_non_finite
    assert not math.isfinite(result.candidates[0].measured["area"])


def test_mutation_scale_note_escaping(monkeypatch):
    # Neuter the escaper -> a raw control char reaches a scale note, proving the real escaper
    # removes it (AS-1 / AS-4).
    monkeypatch.setattr(svc, "_escape_drawing_text", lambda v, **k: v)
    page = _page([_poly(_RING)], text_runs=[_text("scale bar\x01")])
    result = list_candidates(_doc(page), 0)
    # reddens test_scale_notes_are_listed_escaped_and_never_parsed
    assert any("\x01" in n for n in result.scale_notes)


def test_mutation_edge_is_service_measured_not_supplied(monkeypatch):
    # Force _measure_edge to return a fixed value (as if a client-supplied measurement were
    # accepted) -> the scale/outline change, proving the SERVICE geometric measurement is
    # load-bearing (AS-2).
    monkeypatch.setattr(svc, "_measure_edge", lambda prim, edge_index: 80.0)
    result = build_draft(_doc_half(), 0, _assign())
    # scale becomes 80/80 = 1.0 -> the _HALF ring is left unscaled (~492500) -> out of NYC
    # bounds -> draft_invalid; reddens test_scale_is_measured_from_geometry_exact_arithmetic.
    assert isinstance(result, ImportRefusal) and result.reason == "draft_invalid"


def test_mutation_known_length_guard(monkeypatch):
    # Drop the known_length validity check in the scale resolver -> known_length_ft=0 is
    # accepted (scale forced 1.0), proving the real guard is what refuses it (AS-2).
    def _lax(page, assignment):
        ring = svc._rings_by_index(page)[assignment.scale_candidate]
        measured = svc._measure_edge(ring, assignment.scale_edge)
        return (1.0, measured, ring)

    monkeypatch.setattr(svc, "_resolve_scale", _lax)
    r = build_draft(_doc_single(), 0, _assign(known_length_ft=0.0))
    assert r.ok  # reddens test_invalid_known_length_refused_typed


def test_mutation_ring_selection_always_first(monkeypatch):
    # A regression that ALWAYS selects the first ring -> the draft is built from ring A, not
    # the user-assigned ring B, proving the selection seam honours the assignment (AS-3).
    monkeypatch.setattr(svc, "_select_ring", lambda rings, index: rings[0][1])
    draft = build_draft(_doc_two(), 0, _assign(building_outline=1, scale_candidate=1))
    # reddens test_draft_uses_the_user_assigned_ring_not_first_or_largest
    assert draft.proposed_massing["outline"]["vertices"][0] == [985000.0, 195000.0]


def test_mutation_ring_selection_largest(monkeypatch):
    # A regression that auto-picks the LARGEST-area ring -> the draft is built from ring A
    # (the larger), not the user-assigned ring B, proving the selection uses the assignment.
    def _largest(rings, index):
        return max(
            (p for _, p in rings),
            key=lambda p: measured_dimensions(p.points, "sheet")["area"],
        )

    monkeypatch.setattr(svc, "_select_ring", _largest)
    draft = build_draft(_doc_two(), 0, _assign(building_outline=1, scale_candidate=1))
    # reddens test_draft_uses_the_user_assigned_ring_not_first_or_largest
    assert draft.proposed_massing["outline"]["vertices"][0] == [985000.0, 195000.0]


def test_mutation_precision_not_upgraded(monkeypatch):
    # Upgrade the precision constant -> the draft would carry a survey-confirmed precision,
    # proving the honesty test asserts the literal (AS-4; precision never upgraded).
    monkeypatch.setattr(svc, "DRAFT_INPUT_PRECISION", "survey-confirmed - authoritative")
    draft = build_draft(_doc_half(), 0, _assign())
    # reddens test_provenance_block_is_complete_and_honest
    assert draft.provenance["precision"] == "survey-confirmed - authoritative"
