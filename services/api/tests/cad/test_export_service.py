"""Acceptance pack for the pure CAD/3D export service (task M5-T109, D-087 PKT-D).

Fully OFFLINE and deterministic. Covers AS-1 (format dispatch + caps before the writers, each
bound with a reddening in-process mutation), AS-2 (one reconciled, redacted refusal), AS-3
(mandatory filename safety + a reddening mutation), and AS-5 (provenance + honesty + the GLB
single-extrusion dedupe, DB-054 (m)). The route-level AS-4 evidence lives in test_export_api.py.

In-process mutation drill (the consuming namespace): each guard is proven load-bearing by
rebinding the attribute the service resolves at call time (a cap constant, the shared claim-word
screen, or the token builder) and showing the refusal changes or disappears - no repository file
is edited.

M5-T116 (D-087 pre-mount hardening, DB-082 a/c/f/g/h) adds, at the end of this file:
(a) concave-safe GLB caps - L- and U-shaped footprints, with an area-sum + containment oracle
computed IN THIS TEST (not imported from the code under test), a convex case, a self-intersecting
refusal, and the mandatory vertex-0-fan mutation; (c) the fallback filename token re-allowlisted;
(f) the claim-word and length screens parametrized over ALL FOUR caller text fields; (g) the
floor-cap edge (2000 accepted, 2001 refused). Each new guard gets its reddening in-process mutant.

M5-T116 rework round 2 adds, at the very end: the explicit GEOS simplicity gate (a distinct-vertex
'bowtie' is a typed self_intersection refusal, G3 B1, with a gate-dropping mutant); the 1000/1001
GLB footprint vertex-cap edge (G3 A1); and a prepared-ring fixture where preparation reorders +
collapses the ring, pinning that the prism positions come from the PREPARED ring (G4 ADVISORY 2).
"""

from __future__ import annotations

import numbers
import re

import pytest

from app.cad import export_service as es
from app.scenario import massing_triangulation as mt

# --------------------------------------------------------------------------- #
# Fixtures: a small real-interior EPSG:2263 lot + building.
# --------------------------------------------------------------------------- #

_LOT = [
    [985000.0, 195000.0], [985080.0, 195000.0],
    [985080.0, 195100.0], [985000.0, 195100.0],
]
_BUILDING = [
    [985010.0, 195010.0], [985070.0, 195010.0],
    [985070.0, 195090.0], [985010.0, 195090.0],
]
_FLOORS = [10.0, 10.0, 10.0]


def _request(**overrides) -> es.ExportRequest:
    base = dict(
        format="dxf",
        source="proposed",
        lot_ring=_LOT,
        building_ring=_BUILDING,
        floor_heights=_FLOORS,
        address="12 MAIN ST",
        bbl="1-00123-0045",
        generated_at="2026-09-24T00:00:00Z",
        generator_version="site-plan-writer/1.0.0",
    )
    base.update(overrides)
    return es.ExportRequest(**base)


# --------------------------------------------------------------------------- #
# AS-1: each format dispatches to its accepted writer.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "fmt, media, prefix",
    [
        ("dxf", "image/vnd.dxf", b"0\nSECTION"),
        ("pdf", "application/pdf", b"%PDF-1.4"),
        ("glb", "model/gltf-binary", b"glTF"),
    ],
)
def test_each_format_dispatches_to_its_writer(fmt, media, prefix):
    result = es.build_export(_request(format=fmt), fallback_token="abc123")
    assert isinstance(result, es.ExportResult)
    assert result.media_type == media
    assert isinstance(result.body, bytes) and result.body.startswith(prefix)
    assert result.filename.endswith(f".{fmt}")


# --------------------------------------------------------------------------- #
# AS-1: caps BEFORE any writer / normalization, each with a reddening mutation.
# --------------------------------------------------------------------------- #

def test_geometry_over_the_tightest_cap_refuses_before_normalization():
    """A PDF export (tightest ring cap 1024) with an over-cap ring refuses on the RAW length
    BEFORE any per-vertex coercion - proven by seeding NON-NUMERIC vertices past the cap: the
    length check fires first, so the refusal is ring_cap_exceeded, never a coercion error."""
    over = [["not", "numeric"]] * (es._FORMAT_RING_CAP["pdf"] + 1)
    result = es.build_export(_request(format="pdf", lot_ring=over))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "ring_cap_exceeded"


def test_dxf_uses_its_own_looser_ring_cap():
    """The cap is the TIGHTEST for the format: a ring above the PDF cap but below the DXF cap is
    fine for a DXF export."""
    n = es._FORMAT_RING_CAP["pdf"] + 5  # over PDF's 1024, under DXF's 10_000
    ring = [[985000.0 + i * 0.01, 195000.0] for i in range(n)]  # collinear -> DXF refuses geometry
    result = es.build_export(_request(format="dxf", lot_ring=ring))
    # It is NOT refused for the ring cap (that cap did not fire); any refusal here is a
    # downstream geometry code, never ring_cap_exceeded.
    if isinstance(result, es.ExportRefusal):
        assert result.reject_code != "ring_cap_exceeded"


def test_ring_cap_mutation_reddens(monkeypatch):
    """Disable the service ring cap (consuming namespace): the over-cap PDF ring now reaches the
    PDF writer, whose own 1024 cap refuses with a DIFFERENT code (oversize_input)."""
    over = [[float(i), 0.0] for i in range(es._FORMAT_RING_CAP["pdf"] + 1)]
    real = es.build_export(_request(format="pdf", lot_ring=over))
    assert isinstance(real, es.ExportRefusal) and real.reject_code == "ring_cap_exceeded"

    monkeypatch.setitem(es._FORMAT_RING_CAP, "pdf", 10_000_000)
    mutant = es.build_export(_request(format="pdf", lot_ring=over))
    assert isinstance(mutant, es.ExportRefusal)
    assert mutant.reject_code != "ring_cap_exceeded"  # caught downstream, different code


def test_floors_over_cap_refuse():
    result = es.build_export(_request(format="glb", floor_heights=[1.0] * (es.MAX_FLOORS + 1)))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "floor_cap_exceeded"


def test_floor_cap_mutation_reddens(monkeypatch):
    """Disable the floor cap: a GLB export (whose single-prism build has no writer floor cap)
    with over-cap floors now SUCCEEDS instead of refusing."""
    over = _request(format="glb", floor_heights=[1.0] * (es.MAX_FLOORS + 1))
    assert isinstance(es.build_export(over), es.ExportRefusal)  # real: refused
    monkeypatch.setattr(es, "MAX_FLOORS", es.MAX_FLOORS * 100)
    assert isinstance(es.build_export(over), es.ExportResult)  # mutant: no cap -> a file


def test_over_long_caller_text_refuses_before_the_writer():
    long_addr = "A" * (es.MAX_TEXT_CHARS + 1)
    result = es.build_export(_request(format="dxf", address=long_addr))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "text_too_long"


def test_text_cap_mutation_reddens(monkeypatch):
    """Disable the text cap: a DXF export (whose annotation uses FIXED labels, not the caller
    address) with an over-long address now SUCCEEDS."""
    req = _request(format="dxf", address="A" * (es.MAX_TEXT_CHARS + 1))
    assert isinstance(es.build_export(req), es.ExportRefusal)  # real: refused
    monkeypatch.setattr(es, "MAX_TEXT_CHARS", 10 ** 9)
    assert isinstance(es.build_export(req), es.ExportResult)  # mutant: over-long text renders


def test_claim_word_in_caller_text_refuses_before_the_writer():
    result = es.build_export(_request(format="dxf", address="APPROVED_HOSTILE_MARKER tower"))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "claim_class_word"
    # Redaction: the barred canonical word may be named, the caller's own text may not.
    assert "APPROVED" in result.detail
    assert "HOSTILE_MARKER" not in result.detail


def test_claim_word_screen_mutation_reddens(monkeypatch):
    """Disable the shared claim-word screen (consuming namespace): a DXF export (whose annotation
    does not carry the caller address) now SUCCEEDS with a claim word in the address."""
    req = _request(format="dxf", address="APPROVED tower")
    assert isinstance(es.build_export(req), es.ExportRefusal)  # real: refused
    monkeypatch.setattr(es, "contains_claim_word", lambda *texts: None)
    assert isinstance(es.build_export(req), es.ExportResult)  # mutant: screen off -> a file


# --------------------------------------------------------------------------- #
# AS-2: one reconciled, redacted refusal.
# --------------------------------------------------------------------------- #

def test_glb_raise_and_pdf_return_map_to_the_same_shape():
    """A GLB writer RAISE and a PDF writer RETURNED refusal both surface as {reject_code,
    detail}, with the same payload keys."""
    huge = [[0.0, 0.0], [2.0e9, 0.0], [2.0e9, 1.0]]  # GLB writer raises coordinate_out_of_range
    glb = es.build_export(_request(format="glb", building_ring=huge))
    flat = [[0.0, 0.0], [0.0, 5.0], [0.0, 10.0]]  # PDF writer RETURNS a refusal (zero width)
    pdf = es.build_export(_request(format="pdf", lot_ring=flat, building_ring=None))
    assert isinstance(glb, es.ExportRefusal) and isinstance(pdf, es.ExportRefusal)
    assert set(glb.to_payload()) == {"reject_code", "detail"} == set(pdf.to_payload())


def test_reconciled_refusal_never_echoes_a_hostile_coordinate():
    """The GLB writer's own message interpolates the offending coordinate; the reconciled
    refusal must not carry it (DB-059 (h) redact)."""
    huge = [[0.0, 0.0], [2.0e9, 0.0], [2.0e9, 1.0]]
    result = es.build_export(_request(format="glb", building_ring=huge))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "coordinate_out_of_range"
    assert "2000000000" not in result.detail and "2.0e" not in result.detail


def test_dxf_writer_raise_is_reconciled():
    """A DXF writer raise (a non-finite base coordinate is refused by the writer) surfaces as one
    redacted refusal, not an exception."""
    result = es.build_export(_request(format="dxf", floor_heights=[-1.0]))
    assert isinstance(result, es.ExportRefusal)  # negative floor height -> DXF raise -> reconciled


def test_missing_building_geometry_refuses_for_dxf_and_glb():
    for fmt in ("dxf", "glb"):
        result = es.build_export(_request(format=fmt, building_ring=None))
        assert isinstance(result, es.ExportRefusal)
        assert result.reject_code == "missing_building_geometry"


# --------------------------------------------------------------------------- #
# AS-3: mandatory filename safety.
# --------------------------------------------------------------------------- #

_HOSTILE_HEADER_VALUES = [
    '1"; DROP TABLE',           # a quote + ; break/spoof attempt
    "1-0045\r\nSet-Cookie: x",  # CR/LF response splitting attempt
    "1-0045é中",       # non-ASCII
    "1-0045; filename=evil",    # header-parameter injection
]
#: Filenames are STRICTLY the safe token grammar; the builder controls the rest of the header.
_SAFE_FILENAME = re.compile(r"^site-plan-[A-Za-z0-9._-]+\.dxf$")


@pytest.mark.parametrize("hostile", _HOSTILE_HEADER_VALUES)
def test_hostile_caller_value_cannot_break_the_header(hostile):
    result = es.build_export(_request(bbl=hostile), fallback_token="cafef00d")
    assert isinstance(result, es.ExportResult)
    cd = result.content_disposition
    # The filename is exactly the allowlisted token grammar: no quote, ';', CR/LF or non-ASCII
    # byte of the caller can appear (they were DROPPED, not escaped-and-kept).
    assert _SAFE_FILENAME.match(result.filename), result.filename
    # No CR/LF or non-ASCII byte of the caller reaches the header at all.
    for dangerous in ("\r", "\n", "é", "中"):
        assert dangerous not in cd
    # The ONLY quotes/semicolons are the STRUCTURAL ones the builder writes: exactly the pair of
    # quotes around the ASCII filename and the two ';' separators - no caller byte survived.
    assert cd.count('"') == 2
    assert cd.count(";") == 2


def test_token_is_the_allowlist_only():
    token = es.build_filename_token('1"; a\r\nbé', "2026-09-24T00:00:00Z")
    assert token is not None
    assert all(ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
               for ch in token)


def test_token_length_is_capped():
    token = es.build_filename_token("A" * 500, "B" * 500)
    assert token is not None and len(token) <= es.MAX_TOKEN_LEN


def test_empty_token_falls_back_to_server_default(monkeypatch):
    """DB-065 (a): a bbl/generated_at that allowlists to nothing (or only ./-/_) falls back to a
    caller-free server default (the route passes the correlation id)."""
    assert es.build_filename_token("!!!", "///") is None
    assert es.build_filename_token("...", "---") is None
    result = es.build_export(_request(bbl=":::", generated_at="///"), fallback_token="deadbeef99")
    assert isinstance(result, es.ExportResult)
    assert result.filename == "site-plan-deadbeef99.dxf"


def test_content_disposition_carries_both_ascii_and_rfc5987_forms():
    result = es.build_export(_request(), fallback_token="x")
    cd = result.content_disposition
    assert cd.startswith('attachment; filename="site-plan-')
    assert "filename*=UTF-8''site-plan-" in cd


def test_filename_token_mutation_reddens(monkeypatch):
    """The MANDATORY mutation: bypass the allowlist by passing the RAW caller value into the
    token. The real header is clean; the mutant leaks the hostile bytes into the filename."""
    hostile = '1"; DROP'
    real = es.build_export(_request(bbl=hostile), fallback_token="x")
    assert isinstance(real, es.ExportResult) and '"' not in real.filename

    monkeypatch.setattr(es, "build_filename_token", lambda bbl, ga: f"{bbl}-{ga}")
    mutant = es.build_export(_request(bbl=hostile), fallback_token="x")
    assert isinstance(mutant, es.ExportResult)
    assert '"' in mutant.filename  # the raw quote leaked -> the guard is load-bearing


# --------------------------------------------------------------------------- #
# AS-5: provenance + honesty + GLB dedupe (DB-054 (m)).
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "source, label",
    [("proposed", "Proposed - not a city record"),
     ("generated_option", "Generated building option")],
)
def test_source_labels_are_honest(source, label):
    result = es.build_export(_request(source=source))
    assert isinstance(result, es.ExportResult)
    assert result.source_label == label
    assert result.provenance["source_label"] == label


def test_unsupported_source_is_refused():
    for bad in ("approved", "permitted", "maximum_allowed", "as_of_right"):
        result = es.build_export(_request(source=bad))
        assert isinstance(result, es.ExportRefusal)
        assert result.reject_code == "unsupported_source"


def test_unsupported_format_is_refused():
    result = es.build_export(_request(format="dwg"))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "unsupported_format"


@pytest.mark.parametrize("fmt", ["dxf", "pdf", "glb"])
def test_output_is_deterministic_no_clock(fmt):
    a = es.build_export(_request(format=fmt), fallback_token="x")
    b = es.build_export(_request(format=fmt), fallback_token="x")
    assert a.body == b.body  # identical inputs -> byte-identical output (no clock)


def test_generated_at_is_load_bearing_in_the_pdf_title_block():
    """The caller ``generated_at`` reaches the writer that embeds it (the PDF title block); a
    different value yields different bytes. (The byte-frozen DXF/GLB writers embed their own fixed
    provenance and take no generated_at - see the producer report.)"""
    a = es.build_export(_request(format="pdf"), fallback_token="x")
    c = es.build_export(_request(format="pdf", generated_at="2099-01-01T00:00:00Z"),
                        fallback_token="x")
    assert a.body != c.body


def test_glb_is_a_single_extrusion_dedupe():
    """DB-054 (m): per-floor bands are collapsed into ONE extrusion, so the GLB depends only on
    the footprint and the TOTAL height - two floor stacks with the same sum give identical bytes,
    and the provenance discloses the dedupe."""
    one = es.build_export(_request(format="glb", floor_heights=[30.0]), fallback_token="x")
    three = es.build_export(_request(format="glb", floor_heights=[10.0, 10.0, 10.0]),
                            fallback_token="x")
    assert isinstance(one, es.ExportResult) and isinstance(three, es.ExportResult)
    assert one.body == three.body  # floor COUNT does not add coincident interface caps
    assert "DB-054" in three.provenance["glb_massing"]


def test_glb_provenance_records_the_source_and_floors():
    result = es.build_export(_request(format="glb"))
    assert result.provenance["format"] == "glb"
    assert result.provenance["floors"] == len(_FLOORS)


# --------------------------------------------------------------------------- #
# Defensive: DB-075-class hostile numbers reach the GLB path as a typed refusal too.
# --------------------------------------------------------------------------- #

def test_hostile_float_in_glb_footprint_is_a_typed_refusal():
    @numbers.Real.register
    class _Hostile:
        def __float__(self):
            raise ValueError("boom")

    ring = [[0.0, 0.0], [_Hostile(), 0.0], [30.0, 0.0], [0.0, 30.0]]
    result = es.build_export(_request(format="glb", building_ring=ring))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "non_numeric_coordinate"


# =========================================================================== #
# M5-T116 (DB-082 a/c/f/g/h) - concave-safe GLB caps, fallback token, four-field
# screens, floor-cap edge. The geometry oracles below are computed IN THIS TEST
# (shoelace area, triangle signed area, ray-cast point-in-polygon) so nothing is
# imported from the code under test.
# =========================================================================== #

# An L-shaped footprint (EPSG:2263-scale). The prepared ring starts at the SE corner so a
# naive vertex-0 fan crosses the reflex notch (proven wrong by the mutation below); the
# concave-safe triangulator is correct for ANY start.
_L_FOOTPRINT = [
    (985060.0, 195000.0), (985060.0, 195030.0), (985030.0, 195030.0),
    (985030.0, 195060.0), (985000.0, 195060.0), (985000.0, 195000.0),
]
# A U-shaped footprint (notch in the top edge): two reflex corners.
_U_FOOTPRINT = [
    (985000.0, 195000.0), (985060.0, 195000.0), (985060.0, 195060.0),
    (985040.0, 195060.0), (985040.0, 195030.0), (985020.0, 195030.0),
    (985020.0, 195060.0), (985000.0, 195060.0),
]
# A plain convex rectangle (the AS-1 convex case).
_CONVEX_FOOTPRINT = [
    (985010.0, 195010.0), (985070.0, 195010.0),
    (985070.0, 195090.0), (985010.0, 195090.0),
]


def _shoelace_area(ring):
    """Absolute shoelace area of a ring of (x, y) pairs - computed in the test."""
    n = len(ring)
    total = 0.0
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        total += x0 * y1 - x1 * y0
    return abs(total) / 2.0


def _tri_signed_area(p, q, r):
    """Signed area of triangle p q r (> 0 counter-clockwise) - computed in the test."""
    return ((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])) / 2.0


def _point_in_ring(pt, ring):
    """Ray-cast point-in-polygon (odd crossings = inside) - computed in the test."""
    x, y = pt
    inside = False
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            x_int = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if x < x_int:
                inside = not inside
    return inside


def _caps_from_mesh(mesh):
    """Split the prism mesh into (local_ring, bottom_cap_tris, top_cap_tris). A cap
    triangle is one whose three vertices all sit on the same ring (all < n = bottom, all
    >= n = top); the walls mix the two rings. The bottom ring's xy IS the localized
    prepared footprint the caller renders."""
    positions = mesh.positions
    n = len(positions) // 2
    local_ring = [(positions[i][0], positions[i][1]) for i in range(n)]
    tris = [tuple(mesh.indices[k:k + 3]) for k in range(0, len(mesh.indices), 3)]
    bottom = [t for t in tris if all(idx < n for idx in t)]
    top = [t for t in tris if all(idx >= n for idx in t)]
    return positions, n, local_ring, bottom, top


@pytest.mark.parametrize(
    "footprint, ids", [(_L_FOOTPRINT, "L"), (_U_FOOTPRINT, "U"), (_CONVEX_FOOTPRINT, "convex")],
)
def test_glb_caps_lie_inside_the_footprint_and_sum_to_its_area(footprint, ids):
    """AS-1: for L, U and convex footprints every cap triangle lies inside the footprint,
    the cap triangle areas sum to the footprint area (BOTH caps), and the outward winding
    is kept (bottom cap faces -z, top +z). Oracles computed in this test."""
    mesh, _frame = es._build_prism_mesh(list(footprint), 30.0, 0.0)
    positions, n, local_ring, bottom, top = _caps_from_mesh(mesh)
    foot_area = _shoelace_area(local_ring)
    expected_tris = n - 2  # a simple polygon triangulates into exactly n-2 triangles
    assert len(bottom) == expected_tris and len(top) == expected_tris
    # area-sum oracle (a fan across a concavity over-counts |area|)
    b_area = sum(abs(_tri_signed_area(positions[a][:2], positions[b][:2], positions[c][:2]))
                 for a, b, c in bottom)
    t_area = sum(abs(_tri_signed_area(positions[a][:2], positions[b][:2], positions[c][:2]))
                 for a, b, c in top)
    assert b_area == pytest.approx(foot_area, rel=1e-9)
    assert t_area == pytest.approx(foot_area, rel=1e-9)
    # containment oracle: every cap-triangle centroid is inside the footprint
    for a, b, c in bottom + top:
        cx = (positions[a][0] + positions[b][0] + positions[c][0]) / 3.0
        cy = (positions[a][1] + positions[b][1] + positions[c][1]) / 3.0
        assert _point_in_ring((cx, cy), local_ring), ids
    # outward winding: bottom faces -z (CW seen from above -> negative), top faces +z
    for a, b, c in bottom:
        assert _tri_signed_area(positions[a][:2], positions[b][:2], positions[c][:2]) < 0
    for a, b, c in top:
        assert _tri_signed_area(positions[a][:2], positions[b][:2], positions[c][:2]) > 0


def test_convex_prepared_ring_is_unchanged_so_only_the_triangulation_differs():
    """AS-5 disclosure: a CCW convex footprint's prepared ring equals its input order, so
    the prism POSITIONS (and thus the walls) are unchanged from the vertex-0-fan build -
    only the cap triangulation differs. This pins the 'convex output may change only where
    the triangulation differs' claim."""
    mesh, _frame = es._build_prism_mesh(list(_CONVEX_FOOTPRINT), 30.0, 0.0)
    _positions, n, local_ring, _bottom, _top = _caps_from_mesh(mesh)
    ox = min(x for x, _ in _CONVEX_FOOTPRINT)
    oy = min(y for _, y in _CONVEX_FOOTPRINT)
    assert local_ring == [(x - ox, y - oy) for x, y in _CONVEX_FOOTPRINT]
    assert n == len(_CONVEX_FOOTPRINT)


def test_vertex0_fan_mutation_reddens_for_a_concave_footprint(monkeypatch):
    """The MANDATORY AS-1 mutation: restore the naive vertex-0 fan by patching the
    consuming namespace (es.triangulate_polygon) to return a fan over the SAME prepared
    ring. For the concave L footprint the fan's cap triangles fall outside the footprint
    and over-count its area, so the containment + area oracle reddens."""
    mesh, _frame = es._build_prism_mesh(list(_L_FOOTPRINT), 30.0, 0.0)  # real: correct
    _positions, n, local_ring, bottom, _top = _caps_from_mesh(mesh)
    foot_area = _shoelace_area(local_ring)
    real_area = sum(abs(_tri_signed_area(_positions[a][:2], _positions[b][:2], _positions[c][:2]))
                    for a, b, c in bottom)
    assert real_area == pytest.approx(foot_area, rel=1e-9)  # correct build is exact

    real_fn = es.triangulate_polygon

    def _fan(points, field="polygon", **kwargs):
        prepared = real_fn(points, field, **kwargs)
        m = len(prepared.ring)
        fan = tuple((0, i, i + 1) for i in range(1, m - 1))
        return mt.Triangulation(ring=prepared.ring, triangles=fan)

    monkeypatch.setattr(es, "triangulate_polygon", _fan)
    m_mesh, _mf = es._build_prism_mesh(list(_L_FOOTPRINT), 30.0, 0.0)  # mutant: vertex-0 fan
    m_pos, _mn, _mring, m_bottom, _mt = _caps_from_mesh(m_mesh)
    m_area = sum(abs(_tri_signed_area(m_pos[a][:2], m_pos[b][:2], m_pos[c][:2]))
                 for a, b, c in m_bottom)
    outside = any(
        not _point_in_ring(
            ((m_pos[a][0] + m_pos[b][0] + m_pos[c][0]) / 3.0,
             (m_pos[a][1] + m_pos[b][1] + m_pos[c][1]) / 3.0),
            local_ring,
        )
        for a, b, c in m_bottom
    )
    assert m_area > foot_area + 1e-6 or outside  # the fan is geometrically wrong here


def test_concave_footprint_export_produces_valid_glb():
    """AS-1 end-to-end: the L footprint now yields a valid glTF via build_export (before
    the fix it silently produced a wrong-cap mesh; it was never refused)."""
    L = [list(v) for v in _L_FOOTPRINT]
    result = es.build_export(_request(format="glb", building_ring=L), fallback_token="x")
    assert isinstance(result, es.ExportResult)
    assert result.body.startswith(b"glTF")


def test_self_intersecting_footprint_is_a_reconciled_typed_refusal():
    """AS-2: a non-simple footprint of the DUPLICATE-VERTEX subclass is the triangulator's
    own self_intersection refusal, reconciled to the ONE {reject_code, detail} shape and
    never echoing a caller coordinate (DB-059 (h)). The DISTINCT-vertex 'bowtie' subclass -
    which the ear-clipper does NOT detect - is covered by the explicit simplicity gate in
    test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal below (G3 B1)."""
    dup = [[985000.0, 195000.0], [985060.0, 195000.0],
           [985000.0, 195000.0], [985060.0, 195060.0]]
    result = es.build_export(_request(format="glb", building_ring=dup))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "self_intersection"
    assert set(result.to_payload()) == {"reject_code", "detail"}
    assert "985000" not in result.detail and "985060" not in result.detail


def test_triangulator_refusal_reason_is_reconciled_without_caller_text(monkeypatch):
    """AS-2: ANY triangulator MassingModelError reason (e.g. the work-budget refusal, which
    the 1000-vertex outline cap makes unreachable on the real path) maps to the reconciled
    shape carrying only the fixed code - the coordinate/vertex in the error is discarded."""
    def _raise(points, field="polygon", **kwargs):
        raise mt.MassingModelError(
            "building_ring vertex (985060.0, 195030.0) blew the budget",
            reason="triangulation_budget_exceeded", field="building_ring")

    monkeypatch.setattr(es, "triangulate_polygon", _raise)
    result = es.build_export(_request(format="glb"))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "triangulation_budget_exceeded"
    assert "985060" not in result.detail and "985030" not in result.detail


def test_glb_triangulation_refusal_mutation_reddens(monkeypatch):
    """The AS-2 mutation: drop the reconcile and re-raise the raw MassingModelError - the
    caller now sees an untyped exception with the caller coordinate, not a redacted
    refusal, proving the reconcile is load-bearing."""
    def _raise(points, field="polygon", **kwargs):
        raise mt.MassingModelError(
            "building_ring vertex (985060.0, 195030.0) is not simple",
            reason="self_intersection", field="building_ring")

    monkeypatch.setattr(es, "triangulate_polygon", _raise)
    # real path reconciles to a refusal (no raise):
    assert isinstance(es.build_export(_request(format="glb")), es.ExportRefusal)

    def _no_reconcile(reason):  # mutant: the reconcile no longer returns a refusal
        raise mt.MassingModelError("raw", reason=reason, field="building_ring")

    monkeypatch.setattr(es, "_reconcile_triangulation", _no_reconcile)
    with pytest.raises(mt.MassingModelError):
        es.build_export(_request(format="glb"))


def test_fallback_token_is_re_allowlisted_before_content_disposition():
    """AS-3: the caller-supplied fallback token passes the SAME allowlist + length cap
    (DB-082 (c) / M5-T109 G5 A1). A hostile fallback (used because bbl/generated_at
    allowlist to nothing) cannot put a quote/semicolon/CRLF into the header."""
    hostile = '"; DROP TABLE\r\nSet-Cookie: x'
    result = es.build_export(_request(format="dxf", bbl=":::", generated_at="///"),
                             fallback_token=hostile)
    assert isinstance(result, es.ExportResult)
    assert _SAFE_FILENAME.match(result.filename), result.filename
    cd = result.content_disposition
    # the ONLY structural quotes/semicolons are the 2 the builder writes; no caller byte survived
    assert cd.count('"') == 2 and cd.count(";") == 2
    assert "\r" not in cd and "\n" not in cd


def test_fallback_token_re_allowlist_mutation_reddens(monkeypatch):
    """The MANDATORY AS-3 mutation: skip the fallback allowlist (pass the raw fallback
    straight through). The real header is clean; the mutant leaks the raw quote into the
    filename - the re-allowlist is load-bearing."""
    hostile = 'a"; DROP'
    real = es.build_export(_request(format="dxf", bbl=":::", generated_at="///"),
                           fallback_token=hostile)
    assert isinstance(real, es.ExportResult) and '"' not in real.filename

    monkeypatch.setattr(es, "_sanitize_fallback_token", lambda fallback: fallback)
    mutant = es.build_export(_request(format="dxf", bbl=":::", generated_at="///"),
                             fallback_token=hostile)
    assert isinstance(mutant, es.ExportResult)
    assert '"' in mutant.filename  # the raw quote leaked -> the guard is load-bearing


def test_empty_fallback_uses_the_server_default():
    """AS-3: a fallback that itself allowlists to nothing falls back to the caller-free
    server default, never an empty token."""
    result = es.build_export(_request(format="dxf", bbl=":::", generated_at="///"),
                             fallback_token='"""///')
    assert isinstance(result, es.ExportResult)
    assert result.filename == f"site-plan-{es._DEFAULT_TOKEN}.dxf"


@pytest.mark.parametrize("field", es._TEXT_FIELDS)
def test_claim_word_screen_covers_every_caller_text_field(field):
    """AS-4 / (f): the claim-word screen fires on ALL FOUR caller text fields, not only
    address (M5-T109 G4 A1 / DCV F2). The FIELD is named, the caller text is not."""
    result = es.build_export(_request(format="dxf", **{field: "APPROVED tower"}))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "claim_class_word"
    assert field in result.detail and "APPROVED" in result.detail


@pytest.mark.parametrize("field", es._TEXT_FIELDS)
def test_length_screen_covers_every_caller_text_field(field):
    """AS-4 / (f): the length cap fires on ALL FOUR caller text fields."""
    result = es.build_export(_request(format="dxf", **{field: "A" * (es.MAX_TEXT_CHARS + 1)}))
    assert isinstance(result, es.ExportRefusal)
    assert result.reject_code == "text_too_long"
    assert field in result.detail


def test_text_field_set_narrowing_reddens_the_non_address_fields(monkeypatch):
    """The MANDATORY (f) mutation: narrow the screened field set to only address (the exact
    former coverage gap). The three other fields' claim words then slip through to a
    rendered DXF - proving the four-field screen is load-bearing (M5-T109 G4 A1)."""
    for field in ("bbl", "generated_at", "generator_version"):
        req = _request(format="dxf", **{field: "APPROVED"})
        assert isinstance(es.build_export(req), es.ExportRefusal)  # real: refused
    monkeypatch.setattr(es, "_TEXT_FIELDS", ("address",))
    for field in ("bbl", "generated_at", "generator_version"):
        req = _request(format="dxf", **{field: "APPROVED"})
        assert isinstance(es.build_export(req), es.ExportResult)  # mutant: slips through


def test_floor_cap_edge_2000_accepted_2001_refused():
    """AS-4 / (g): pin the exact floor-cap boundary - MAX_FLOORS (2000) is accepted, 2001
    is refused (M5-T109 G4 A2)."""
    assert es.MAX_FLOORS == 2000
    ok = es.build_export(_request(format="glb", floor_heights=[1.0] * es.MAX_FLOORS),
                         fallback_token="x")
    assert isinstance(ok, es.ExportResult)  # exactly 2000 renders
    over = es.build_export(_request(format="glb", floor_heights=[1.0] * (es.MAX_FLOORS + 1)))
    assert isinstance(over, es.ExportRefusal) and over.reject_code == "floor_cap_exceeded"


def test_floor_cap_edge_mutation_reddens(monkeypatch):
    """The (g) mutation: an off-by-one cap (refuse AT the cap) would reject the legal
    2000-floor export. Lower MAX_FLOORS to 1999 (consuming namespace): the exactly-2000
    export that MUST pass now refuses - the edge is load-bearing."""
    exactly = _request(format="glb", floor_heights=[1.0] * 2000)
    assert isinstance(es.build_export(exactly, fallback_token="x"), es.ExportResult)  # real
    monkeypatch.setattr(es, "MAX_FLOORS", 1999)
    mutant = es.build_export(exactly)
    assert isinstance(mutant, es.ExportRefusal) and mutant.reject_code == "floor_cap_exceeded"


# =========================================================================== #
# M5-T116 rework round 2 - the explicit GEOS simplicity gate (G3 B1 / AS-2), the
# 1000/1001 GLB footprint cap edge (G3 A1), and a prepared-ring fixture (G4 ADVISORY 2).
# =========================================================================== #

# Crossed 'bowtie' footprints with DISTINCT vertices (edges cross, no repeated vertex).
# The ear-clipper does NOT stall on these, so before the simplicity gate they yielded a
# valid-but-self-overlapping glTF instead of a refusal.
_BOWTIES = [
    ([[0.0, 0.0], [60.0, 60.0], [60.0, 0.0], [0.0, 60.0]], "origin"),
    ([[985000.0, 195000.0], [985060.0, 195060.0],
      [985060.0, 195000.0], [985000.0, 195060.0]], "nyc-scale"),
    ([[0.0, 0.0], [40.0, 0.0], [0.0, 40.0], [40.0, 40.0]], "figure-eight"),
]


@pytest.mark.parametrize("bowtie, ids", _BOWTIES)
def test_distinct_vertex_bowtie_is_a_reconciled_typed_refusal(bowtie, ids):
    """G3 B1 / AS-2: a crossed bowtie with DISTINCT vertices is the reconciled
    self_intersection refusal (never a self-overlapping mesh), echoing no caller
    coordinate. The ear-clipper misses this class; the explicit GEOS simplicity gate on the
    prepared ring catches it."""
    result = es.build_export(_request(format="glb", building_ring=bowtie), fallback_token="x")
    assert isinstance(result, es.ExportRefusal), ids
    assert result.reject_code == "self_intersection"
    assert set(result.to_payload()) == {"reject_code", "detail"}
    # the detail is EXACTLY the server-built template - no caller coordinate echoed (DB-059 (h))
    assert result.detail == (
        "the glb footprint could not be triangulated (reject_code=self_intersection)"
    )


def test_simplicity_gate_dropped_lets_a_bowtie_through(monkeypatch):
    """The MANDATORY AS-2 mutation: drop the simplicity gate (consuming namespace). A
    distinct-vertex bowtie - a typed self_intersection refusal on the real path - now
    ear-clips to a valid-but-self-overlapping glTF, proving the gate is load-bearing."""
    bowtie = [[0.0, 0.0], [60.0, 60.0], [60.0, 0.0], [0.0, 60.0]]
    real = es.build_export(_request(format="glb", building_ring=bowtie), fallback_token="x")
    assert isinstance(real, es.ExportRefusal) and real.reject_code == "self_intersection"

    monkeypatch.setattr(es, "_reject_non_simple_ring", lambda ring: None)
    mutant = es.build_export(_request(format="glb", building_ring=bowtie), fallback_token="x")
    assert isinstance(mutant, es.ExportResult)  # gate off -> a self-overlapping mesh renders
    assert mutant.body.startswith(b"glTF")


def _circle_ring(k, radius=400.0, cx=985000.0, cy=195000.0):
    """k distinct, strictly-convex (non-collinear) EPSG:2263 vertices on a circle."""
    import math
    return [[cx + radius * math.cos(2 * math.pi * i / k),
             cy + radius * math.sin(2 * math.pi * i / k)] for i in range(k)]


def test_glb_footprint_vertex_cap_1000_accepted_1001_refused():
    """G3 A1: the EFFECTIVE GLB footprint cap is the triangulator's MAX_OUTLINE_VERTICES
    (1000), NOT the raw 10_000 _FORMAT_RING_CAP['glb']. Exactly 1000 vertices triangulate to
    a valid glTF; 1001 is refused over_cap_vertices INSIDE the triangulator (before the ear
    scan), reconciled to the ONE refusal shape."""
    assert es._FORMAT_RING_CAP["glb"] == 10_000  # the raw gate is looser than the real cap
    ok = es.build_export(_request(format="glb", building_ring=_circle_ring(1000)),
                         fallback_token="x")
    assert isinstance(ok, es.ExportResult) and ok.body.startswith(b"glTF")
    over = es.build_export(_request(format="glb", building_ring=_circle_ring(1001)),
                           fallback_token="x")
    assert isinstance(over, es.ExportRefusal)
    assert over.reject_code == "over_cap_vertices"


# A CW-ordered rectangle with a COLLINEAR midpoint on the bottom edge: preparation both
# reverses it to CCW and collapses the midpoint, so the prepared ring differs from the
# localized raw input in BOTH order and vertex count (unlike the L/U/convex fixtures).
_CW_COLLINEAR_FOOTPRINT = [
    (985000.0, 195000.0), (985000.0, 195060.0), (985060.0, 195060.0),
    (985060.0, 195000.0), (985030.0, 195000.0),
]


def test_prism_positions_come_from_the_prepared_ring_not_the_raw_input(monkeypatch):
    """G4 ADVISORY 2: for a footprint where preparation reorders (CW->CCW) and collapses a
    collinear midpoint, the prism positions must come from the PREPARED ring - the one the
    cap triangles index and the walls share. A raw-ring build (positions from the input
    order/count while the caps index the prepared ring) reddens the cap-count oracle."""
    raw = list(_CW_COLLINEAR_FOOTPRINT)
    mesh, _frame = es._build_prism_mesh(raw, 30.0, 0.0)
    positions, n, local_ring, bottom, top = _caps_from_mesh(mesh)
    ox = min(x for x, _ in raw)
    oy = min(y for _, y in raw)
    # preparation changed the ring: fewer vertices than raw (the midpoint collapsed) ...
    assert n < len(raw)
    assert local_ring != [(x - ox, y - oy) for x, y in raw]
    # ... and the positions equal the REAL prepared ring (localized), not the raw input.
    prepared = es.triangulate_polygon(raw, field="building_ring").ring
    pox = min(x for x, _ in prepared)
    poy = min(y for _, y in prepared)
    assert local_ring == [(x - pox, y - poy) for x, y in prepared]
    # the caps tile the footprint with the correct count and area.
    foot_area = _shoelace_area(local_ring)
    assert len(bottom) == n - 2 == len(top)
    b_area = sum(abs(_tri_signed_area(positions[a][:2], positions[b][:2], positions[c][:2]))
                 for a, b, c in bottom)
    assert b_area == pytest.approx(foot_area, rel=1e-9)

    # raw-ring mutant: positions built from the RAW order/count while the cap triangles
    # still index the prepared ring -> the caps no longer tile the footprint.
    real_fn = es.triangulate_polygon

    def _raw_ring(points, field="polygon", **kwargs):
        prepared_t = real_fn(points, field, **kwargs)
        raw_pts = tuple((float(x), float(y)) for x, y in points)
        return mt.Triangulation(ring=raw_pts, triangles=prepared_t.triangles)

    monkeypatch.setattr(es, "triangulate_polygon", _raw_ring)
    m_mesh, _mf = es._build_prism_mesh(raw, 30.0, 0.0)
    _mpos, m_n, _mring, m_bottom, m_top = _caps_from_mesh(m_mesh)
    assert len(m_bottom) != m_n - 2 or len(m_top) != m_n - 2  # caps no longer tile
