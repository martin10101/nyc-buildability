"""Acceptance pack for the PKT-F DXF import SERVICE (task M5-T108, D-087).

Fully offline and deterministic. Exercises :mod:`app.drawings.dxf_import` against the
accepted reader :func:`app.drawings.dxf_reader.read_dxf`:

- AS-2 (candidates -> user roles -> draft): closed rings are listed with layer and
  measured dimensions in the DECLARED units; a draft is built ONLY from user-assigned
  roles and user-confirmed units through ``validate_proposed_massing``; discrepancies
  are shown, never auto-reconciled; an out-of-range / open / ambiguous input refuses typed.
- AS-3 (honesty + provenance): nothing is labelled a city record or permitted; the draft
  carries input-precision provenance no later step upgrades.
- AS-4 (untrusted drawing text): drawing strings are escaped on output; refusal details
  are bounded; only ASCII DXF (binary sentinel refused).

Each guard has a reddening in-process MUTATION (mutating the CONSUMING namespace) that
proves the test constrains the guard.
"""

from __future__ import annotations

from app.drawings import dxf_import as svc
from app.drawings.dxf_import import (
    DRAFT_INPUT_PRECISION,
    DRAFT_SOURCE_LABEL,
    ImportRefusal,
    RoleAssignment,
    build_draft,
    list_candidates,
    measured_dimensions,
    sniff_dxf_media,
)
from app.drawings.dxf_reader import read_dxf

# A ring in real NYC EPSG:2263 (US survey feet) space so a draft can pass the contract.
_RING = [(985000.0, 195000.0), (985080.0, 195000.0), (985080.0, 195100.0), (985000.0, 195100.0)]
# POSITIVE claim words that must never appear. "city record" is deliberately absent: the
# honest label legitimately reads "Proposed - not a city record" (a negation, not a claim).
_FORBIDDEN_WORDS = (
    "permitted", "approved", "maximum allowed", "as of right", "demonstrated maximum",
)


def _dxf(
    rings=((_RING, "BUILDING", True),), *, insunits=21, acadver="AC1027", extra=""
) -> bytes:
    """Build a minimal ASCII DXF: a HEADER ($INSUNITS, $ACADVER) + ENTITIES rings."""
    lines = ["0", "SECTION", "2", "HEADER"]
    lines += ["9", "$ACADVER", "1", acadver]
    lines += ["9", "$INSUNITS", "70", str(insunits)]
    lines += ["0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for verts, layer, closed in rings:
        lines += ["0", "LWPOLYLINE", "8", layer, "70", "1" if closed else "0"]
        for x, y in verts:
            lines += ["10", str(x), "20", str(y)]
    lines += ["0", "ENDSEC", "0", "EOF"]
    body = "\r\n".join(lines) + "\r\n" + extra
    return body.encode("ascii")


def _assign(**over) -> RoleAssignment:
    base = dict(
        building_outline=0, floors=5, floor_to_floor_ft=11.0, author="Jane Architect",
        confirmed_units="us_survey_feet",
    )
    base.update(over)
    return RoleAssignment(**base)


# --------------------------------------------------------------------------- AS-2 candidates


def test_candidates_list_closed_rings_with_measured_dimensions():
    doc = read_dxf(_dxf())
    result = list_candidates(doc)
    assert result.ok
    assert result.declared_units["name"] == "us_survey_feet"
    assert len(result.candidates) == 1
    cand = result.candidates[0]
    assert cand.layer == "BUILDING"
    assert cand.vertex_count == 4
    assert cand.measured["units"] == "us_survey_feet"
    assert cand.measured["bbox_width"] == 80.0
    assert cand.measured["area"] == 8000.0


def test_open_polyline_is_disclosed_not_a_candidate():
    doc = read_dxf(_dxf(rings=((_RING, "OUTLINE", False),)))
    result = list_candidates(doc)
    assert result.candidates == ()
    assert result.disclosure["open_polylines"] == 1


def test_measured_dimensions_perimeter_and_area():
    m = measured_dimensions(tuple(_RING), "feet")
    assert m["perimeter"] == 360.0  # 80 + 100 + 80 + 100
    assert m["area"] == 8000.0


def test_reader_refusal_maps_to_typed_import_refusal():
    result = list_candidates(read_dxf(b"not a dxf at all"))
    assert isinstance(result, ImportRefusal)
    assert result.reason == "unreadable_dxf"


# --------------------------------------------------------------------------- AS-2 draft


def test_draft_built_from_roles_and_confirmed_units():
    draft = build_draft(read_dxf(_dxf()), _assign())
    assert draft.ok
    block = draft.proposed_massing
    # closure is made EXPLICIT (proposal outlines repeat the first vertex)
    assert block["outline"]["vertices"][0] == block["outline"]["vertices"][-1]
    assert block["outline"]["srid"] == 2263
    assert block["levels"][0]["floor_count"] == 5
    assert draft.provenance["assigned_roles"]["building_outline"] == 0


def test_units_mismatch_is_shown_never_reconciled():
    # drawing declares meters; user confirms feet -> discrepancy shown, feet used.
    draft = build_draft(read_dxf(_dxf(insunits=6)), _assign())
    assert draft.ok
    assert draft.provenance["unit_scale_ft_per_unit"] == 1.0  # confirmed feet, NOT converted
    assert draft.discrepancies
    disc = draft.discrepancies[0]
    assert disc["type"] == "units_mismatch"
    assert disc["declared"] == "meters" and disc["confirmed"] == "us_survey_feet"


def test_known_dimension_scale_path():
    draft = build_draft(
        read_dxf(_dxf()),
        _assign(confirmed_units=None, known_length_ft=80.0, measured_length=80.0),
    )
    assert draft.ok
    assert draft.provenance["scale_source"] == "known_dimension"
    assert draft.provenance["unit_scale_ft_per_unit"] == 1.0


def test_ambiguous_units_refused():
    both = build_draft(read_dxf(_dxf()), _assign(known_length_ft=80.0, measured_length=80.0))
    assert isinstance(both, ImportRefusal) and both.reason == "ambiguous_units"
    neither = build_draft(read_dxf(_dxf()), _assign(confirmed_units=None))
    assert isinstance(neither, ImportRefusal) and neither.reason == "ambiguous_units"


def test_unsupported_units_refused():
    r = build_draft(read_dxf(_dxf()), _assign(confirmed_units="meters"))
    assert isinstance(r, ImportRefusal) and r.reason == "unsupported_units"


def test_bad_candidate_index_refused():
    r = build_draft(read_dxf(_dxf()), _assign(building_outline=7))
    assert isinstance(r, ImportRefusal) and r.reason == "bad_candidate"


def test_out_of_bounds_ring_refused_by_the_contract():
    # near-origin ring is not georeferenced to NY state plane -> the massing contract
    # refuses; the service surfaces the field, never auto-corrects.
    near_origin = [(0.0, 0.0), (80.0, 0.0), (80.0, 100.0), (0.0, 100.0)]
    r = build_draft(read_dxf(_dxf(rings=((near_origin, "B", True),))), _assign())
    assert isinstance(r, ImportRefusal) and r.reason == "draft_invalid"
    assert r.field and r.field.startswith("proposed_massing.outline")


# --------------------------------------------------------------------------- AS-3 honesty


def test_draft_provenance_is_honest_and_not_upgraded():
    draft = build_draft(read_dxf(_dxf()), _assign())
    assert draft.provenance["precision"] == DRAFT_INPUT_PRECISION
    assert draft.provenance["label"] == DRAFT_SOURCE_LABEL
    blob = str(draft.provenance).lower() + str(draft.proposed_massing).lower()
    for word in _FORBIDDEN_WORDS:
        assert word not in blob


# --------------------------------------------------------------------------- AS-4 escaping + media


def test_drawing_text_is_escaped_on_output():
    doc = read_dxf(_dxf(rings=((_RING, "LAY\x01ER", True),), acadver="AC\x1b1027"))
    result = list_candidates(doc)
    assert "\x01" not in result.candidates[0].layer
    assert "\\x01" in result.candidates[0].layer
    assert "\x1b" not in (result.acad_version or "")


def test_sniff_accepts_ascii_dxf_and_refuses_binary_and_junk():
    assert sniff_dxf_media("application/dxf", _dxf()) is None
    assert sniff_dxf_media(None, _dxf()) is None  # missing content-type is fine
    binary = sniff_dxf_media(None, b"AutoCAD Binary DXF\r\n\x1a\x00rest")
    assert binary is not None and binary.reason == "unsupported_media_type"
    bad_ct = sniff_dxf_media("application/json", _dxf())
    assert bad_ct is not None
    non_ascii = sniff_dxf_media(None, "0\r\nSECTION\r\n\xff".encode("latin-1"))
    assert non_ascii is not None
    no_marker = sniff_dxf_media(None, b"hello world, no dxf markers here")
    assert no_marker is not None


# --------------------------------------------------------------------------- reddening mutations
# Each guard: mutate the CONSUMING namespace and prove the protected behaviour flips.


def test_mutation_validate_contract_is_actually_called(monkeypatch):
    # If validate_proposed_massing is neutered, the out-of-bounds ring would pass -
    # proving the real guard is what refuses it (AS-2 draft validation).
    monkeypatch.setattr(svc, "validate_proposed_massing", lambda block: None)
    near_origin = [(0.0, 0.0), (80.0, 0.0), (80.0, 100.0), (0.0, 100.0)]
    r = build_draft(read_dxf(_dxf(rings=((near_origin, "B", True),))), _assign())
    assert r.ok  # reddens test_out_of_bounds_ring_refused_by_the_contract


def test_mutation_escape_is_actually_applied(monkeypatch):
    # Neuter the escaper -> a raw control char reaches the candidate layer, proving the
    # real escaper is what removes it (AS-4).
    monkeypatch.setattr(svc, "_escape_drawing_text", lambda v, **k: v)
    doc = read_dxf(_dxf(rings=((_RING, "LAY\x01ER", True),)))
    result = list_candidates(doc)
    assert "\x01" in result.candidates[0].layer  # reddens test_drawing_text_is_escaped_on_output


def test_mutation_closed_flag_gates_candidates(monkeypatch):
    # Neuter the closed-flag gate (consuming namespace) so EVERY polyline becomes a
    # candidate -> an open ring now lists, proving the real gate excludes it (AS-2).
    monkeypatch.setattr(
        svc,
        "_closed_ring_candidates",
        lambda doc: [(i, p) for i, p in enumerate(doc.primitives)],
    )
    doc = read_dxf(_dxf(rings=((_RING, "OUTLINE", False),)))
    result = list_candidates(doc)
    # reddens test_open_polyline_is_disclosed_not_a_candidate
    assert len(result.candidates) == 1


def test_mutation_ambiguous_units_guard(monkeypatch):
    # Force the scale resolver to accept any assignment -> the both-mechanisms case no
    # longer refuses, proving the real ambiguity guard is what rejects it (AS-2).
    monkeypatch.setattr(svc, "_resolve_scale", lambda a, d: (1.0, "confirmed_units", ()))
    r = build_draft(read_dxf(_dxf()), _assign(known_length_ft=80.0, measured_length=80.0))
    assert r.ok  # reddens test_ambiguous_units_refused
