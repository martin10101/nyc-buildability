"""Acceptance pack for the pure CAD/3D export service (task M5-T109, D-087 PKT-D).

Fully OFFLINE and deterministic. Covers AS-1 (format dispatch + caps before the writers, each
bound with a reddening in-process mutation), AS-2 (one reconciled, redacted refusal), AS-3
(mandatory filename safety + a reddening mutation), and AS-5 (provenance + honesty + the GLB
single-extrusion dedupe, DB-054 (m)). The route-level AS-4 evidence lives in test_export_api.py.

In-process mutation drill (the consuming namespace): each guard is proven load-bearing by
rebinding the attribute the service resolves at call time (a cap constant, the shared claim-word
screen, or the token builder) and showing the refusal changes or disappears - no repository file
is edited.
"""

from __future__ import annotations

import numbers
import re

import pytest

from app.cad import export_service as es

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
