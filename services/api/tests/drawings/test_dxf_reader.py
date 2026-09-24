"""Strict-subset ASCII DXF reader tests (M5-T086, D-087 CAD-3).

Every fixture is a hand-written DXF group-code stream built with :func:`_dxf`, which always
emits an even (group-code, value) line count. The suite proves the parsed subset, units
honesty, the disclose-or-refuse rule, every fail-closed bound, and the two named mutations.
"""

from __future__ import annotations

import time
import tracemalloc

import pytest

from app.drawings import dxf_reader as _reader_mod
from app.drawings.dxf_reader import (
    DEFAULT_LIMITS,
    DxfDocument,
    DxfLimits,
    DxfRefusal,
    DxfRefusalReason,
    FacePrimitive,
    LinePrimitive,
    PolylinePrimitive,
    TextPrimitive,
    read_dxf,
)


def _dxf(*pairs: tuple[int | str, object]) -> str:
    """Assemble (group-code, value) pairs into an ASCII DXF string (always even lines)."""
    lines: list[str] = []
    for code, value in pairs:
        lines.append(str(code))
        lines.append(str(value))
    return "\n".join(lines) + "\n"


_HEADER_FEET = (
    (0, "SECTION"),
    (2, "HEADER"),
    (9, "$ACADVER"),
    (1, "AC1027"),
    (9, "$INSUNITS"),
    (70, 2),  # 2 = feet
    (0, "ENDSEC"),
)

_LWPOLY_LOT = (
    (0, "LWPOLYLINE"),
    (8, "LOT"),
    (90, 4),
    (70, 1),  # closed
    (10, 0.0), (20, 0.0),
    (10, 100.0), (20, 0.0),
    (10, 100.0), (20, 50.0),
    (10, 0.0), (20, 50.0),
)

_POLYLINE_BLDG = (
    (0, "POLYLINE"),
    (8, "BLDG"),
    (66, 1),
    (70, 1),  # closed
    (0, "VERTEX"), (8, "BLDG"), (10, 10.0), (20, 10.0), (30, 0.0),
    (0, "VERTEX"), (8, "BLDG"), (10, 40.0), (20, 10.0), (30, 0.0),
    (0, "VERTEX"), (8, "BLDG"), (10, 40.0), (20, 30.0), (30, 0.0),
    (0, "SEQEND"), (8, "BLDG"),
)

_FACE_WALL = (
    (0, "3DFACE"),
    (8, "WALLS"),
    (10, 0.0), (20, 0.0), (30, 0.0),
    (11, 10.0), (21, 0.0), (31, 0.0),
    (12, 10.0), (22, 0.0), (32, 12.0),
    (13, 0.0), (23, 0.0), (33, 12.0),
)

_TEXT_NOTE = (
    (0, "TEXT"),
    (8, "NOTES"),
    (10, 10.0), (20, 10.0), (30, 0.0),
    (40, 2.5),
    (1, "LOT A"),
)

_CIRCLE_UNKNOWN = (
    (0, "CIRCLE"),
    (8, "MISC"),
    (10, 5.0), (20, 5.0), (40, 2.0),
)


def _full_drawing() -> str:
    return _dxf(
        *_HEADER_FEET,
        (0, "SECTION"), (2, "ENTITIES"),
        *_LWPOLY_LOT,
        *_POLYLINE_BLDG,
        *_FACE_WALL,
        *_TEXT_NOTE,
        *_CIRCLE_UNKNOWN,
        (0, "ENDSEC"),
        (0, "EOF"),
    )


# ---------------------------------------------------------------- AS-1: subset primitives


def test_as1_full_drawing_yields_typed_primitives() -> None:
    result = read_dxf(_full_drawing())
    assert isinstance(result, DxfDocument)
    assert result.ok is True
    kinds = [type(p) for p in result.primitives]
    assert kinds == [PolylinePrimitive, PolylinePrimitive, FacePrimitive, TextPrimitive]

    lot = result.primitives[0]
    assert isinstance(lot, PolylinePrimitive)
    assert lot.entity_type == "LWPOLYLINE"
    assert lot.layer == "LOT"
    assert lot.closed is True
    assert lot.vertices == ((0.0, 0.0), (100.0, 0.0), (100.0, 50.0), (0.0, 50.0))

    bldg = result.primitives[1]
    assert isinstance(bldg, PolylinePrimitive)
    assert bldg.entity_type == "POLYLINE"
    assert bldg.layer == "BLDG"
    assert bldg.closed is True
    assert bldg.vertices == ((10.0, 10.0), (40.0, 10.0), (40.0, 30.0))

    wall = result.primitives[2]
    assert isinstance(wall, FacePrimitive)
    assert wall.layer == "WALLS"
    assert wall.corners == (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 0.0, 12.0),
        (0.0, 0.0, 12.0),
    )

    note = result.primitives[3]
    assert isinstance(note, TextPrimitive)
    assert note.layer == "NOTES"
    assert note.position == (10.0, 10.0, 0.0)
    assert note.text == "LOT A"
    assert note.height == 2.5


def test_as1_line_entity_start_and_end() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "AXIS"),
        (10, 1.0), (20, 2.0), (30, 3.0),
        (11, 4.0), (21, 5.0), (31, 6.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    (line,) = result.primitives
    assert isinstance(line, LinePrimitive)
    assert line.layer == "AXIS"
    assert line.start == (1.0, 2.0, 3.0)
    assert line.end == (4.0, 5.0, 6.0)


def test_as1_missing_layer_defaults_to_zero() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.primitives[0].layer == "0"


# ------------------------------------------------------------------- AS-2: units honesty


def test_as2_feet_units_reported_with_code() -> None:
    result = read_dxf(_full_drawing())
    assert isinstance(result, DxfDocument)
    assert result.units.code == 2
    assert result.units.name == "feet"
    assert result.units.source == "header:$INSUNITS"
    assert result.acad_version == "AC1027"


def test_as2_no_units_header_is_unitless_never_feet() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.units.code is None
    assert result.units.name == "unitless"
    assert result.units.source == "absent"


def test_as2_explicit_unitless_distinguished_from_absent() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "HEADER"), (9, "$INSUNITS"), (70, 0), (0, "ENDSEC"),
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.units.code == 0
    assert result.units.name == "unitless"
    assert result.units.source == "header:$INSUNITS"


def test_as2_unknown_units_code_reported_verbatim_never_coerced() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "HEADER"), (9, "$INSUNITS"), (70, 99), (0, "ENDSEC"),
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.units.code == 99
    assert result.units.name == "unknown_insunits_99"


# --------------------------------------------------------- AS-3: disclose-or-refuse rule


def test_as3_unknown_entity_counted_and_disclosed_not_refused() -> None:
    result = read_dxf(_full_drawing())
    assert isinstance(result, DxfDocument)
    assert result.disclosed_unknown == (("CIRCLE", 1),)
    assert result.entity_count == 5  # 4 parsed + 1 disclosed


def test_as3_insert_reference_disclosed_as_unknown() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "INSERT"), (8, "REFS"), (2, "BLOCK_A"), (10, 0.0), (20, 0.0),
        (0, "INSERT"), (8, "REFS"), (2, "BLOCK_A"), (10, 5.0), (20, 5.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.primitives == ()
    assert result.disclosed_unknown == (("INSERT", 2),)


def test_as3_non_data_section_skipped_and_disclosed() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "BLOCKS"),
        (0, "BLOCK"), (8, "0"), (2, "BLOCK_A"),
        (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDBLK"),
        (0, "ENDSEC"),
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 0.0), (20, 0.0), (11, 2.0), (21, 2.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    assert result.skipped_sections == ("BLOCKS",)
    # The LINE inside BLOCKS is skipped with the section; only the ENTITIES LINE parses.
    assert len(result.primitives) == 1


def test_as3_binary_dxf_sentinel_refused() -> None:
    result = read_dxf(b"AutoCAD Binary DXF\r\n\x1a\x00\x00\x01\x02\x03")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BINARY_DXF


# ---------------------------------------------------- AS-4: fail-closed refusal VALUES


def test_as4_odd_pair_count_refused() -> None:
    src = _full_drawing() + "999\n"  # one dangling group-code line -> odd
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.ODD_PAIR_COUNT


def test_as4_non_numeric_coordinate_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, "not_a_number"), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BAD_COORDINATE


def test_as4_non_finite_coordinate_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, "inf"), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BAD_COORDINATE


def test_as4_bad_group_code_refused() -> None:
    result = read_dxf("not_an_int\nLINE\n")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BAD_GROUP_CODE


def test_as4_non_zero_bulge_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LWPOLYLINE"), (8, "LOT"), (90, 2), (70, 1),
        (10, 0.0), (20, 0.0), (42, 0.5),
        (10, 10.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.UNSUPPORTED_BULGE


def test_as4_file_too_large_refused() -> None:
    result = read_dxf(_full_drawing(), limits=DxfLimits(max_bytes=16))
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.FILE_TOO_LARGE


def test_as4_line_too_long_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "TEXT"), (8, "A"), (10, 0.0), (20, 0.0), (1, "X" * 50),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src, limits=DxfLimits(max_line_chars=10))
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.LINE_TOO_LONG


def test_as4_too_many_vertices_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LWPOLYLINE"), (8, "LOT"), (90, 3), (70, 1),
        (10, 0.0), (20, 0.0),
        (10, 1.0), (20, 0.0),
        (10, 1.0), (20, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src, limits=DxfLimits(max_vertices=2))
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.TOO_MANY_VERTICES


def test_as4_stray_vertex_outside_polyline_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "VERTEX"), (8, "A"), (10, 0.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.MALFORMED_STRUCTURE


def test_as4_unterminated_polyline_refused() -> None:
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "POLYLINE"), (8, "A"), (70, 0),
        (0, "VERTEX"), (8, "A"), (10, 0.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.MALFORMED_STRUCTURE


def test_as4_no_section_markers_refused() -> None:
    result = read_dxf("8\nA\n10\n0.0\n")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.MALFORMED_STRUCTURE


def test_as4_never_raises_on_garbage() -> None:
    for blob in (b"", b"\x00\x01\x02\x80\x81", b"\xff\xfe", "random text no pairs", "1\n"):
        result = read_dxf(blob)
        assert isinstance(result, (DxfDocument, DxfRefusal))
        if isinstance(result, DxfDocument):  # none of these are valid DXF
            raise AssertionError("garbage unexpectedly parsed as a document")


def test_as4_non_ascii_bytes_refused() -> None:
    result = read_dxf(b"0\nSECTION\n2\nENTITIES\n0\nTEXT\n1\ncaf\xe9\n0\nEOF\n")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.NON_ASCII


# ------------------------------------------------------------------- AS-5: scope sanity


def test_as5_default_limits_are_the_reviewed_constants() -> None:
    # Guards against silent bound drift; production defaults must stay as reviewed.
    assert DEFAULT_LIMITS.max_bytes == 8 * 1024 * 1024
    assert DEFAULT_LIMITS.max_lines == 2_000_000
    assert DEFAULT_LIMITS.max_line_chars == 4096
    assert DEFAULT_LIMITS.max_entities == 200_000
    assert DEFAULT_LIMITS.max_vertices == 100_000


def test_as5_result_is_frozen_value() -> None:
    result = read_dxf(_full_drawing())
    assert isinstance(result, DxfDocument)
    try:
        result.entity_count = 0  # type: ignore[misc]
    except AttributeError:
        pass  # frozen dataclass - immutable value, as intended
    else:
        raise AssertionError("DxfDocument must be a frozen value")


# --------------------------------------------------------------- NAMED MUTATION PROBES


def test_mutation_entity_count_bound_reddens() -> None:
    """MUTATION #1: deleting the `entity_count > limits.max_entities` guard in
    `_handle_entity` makes this three-entity file parse instead of refuse -> reddens."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "LINE"), (8, "A"), (10, 1.0), (20, 1.0), (11, 2.0), (21, 2.0),
        (0, "LINE"), (8, "A"), (10, 2.0), (20, 2.0), (11, 3.0), (21, 3.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src, limits=DxfLimits(max_entities=2))
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.TOO_MANY_ENTITIES


def test_mutation_pair_parity_check_reddens() -> None:
    """MUTATION #2: the odd-line-count guard in `_to_pairs` (now a leftover unpaired code
    line after the streaming scan) turns an odd total line count into ODD_PAIR_COUNT;
    dropping it would silently ignore the trailing line, so this assertion reddens."""
    src = _full_drawing() + "0\n"  # single extra line -> odd total line count
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.ODD_PAIR_COUNT


# ===================================================================================
# M5-T097 (D-087 CAD-3) reader hardening + closed G4 probe gaps. New cases only; every
# test above is unchanged. Packet acceptance scenarios AS-1 (line splitting), AS-2
# (bounds), AS-3 (probe gaps). Named/required mutations are proved in-process by
# rebinding the CONSUMED module global (per the mutate-the-consuming-namespace rule).
# ===================================================================================


# --------------------------------------------------------- T097 AS-1: CR/LF-only splitting


def test_t097_as1_cr_lf_crlf_parse_identically() -> None:
    """CR, LF and CRLF line endings yield byte-identical primitives (the splitter treats
    all three, and only those three, as line terminators)."""
    codes: list[str] = []
    for code, value in (
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 1.0), (20, 2.0), (11, 3.0), (21, 4.0),
        (0, "ENDSEC"), (0, "EOF"),
    ):
        codes.append(str(code))
        codes.append(str(value))
    lf = read_dxf("\n".join(codes) + "\n")
    cr = read_dxf("\r".join(codes) + "\r")
    crlf = read_dxf("\r\n".join(codes) + "\r\n")
    assert isinstance(lf, DxfDocument)
    assert isinstance(cr, DxfDocument)
    assert isinstance(crlf, DxfDocument)
    assert lf.primitives == cr.primitives == crlf.primitives
    assert lf.primitives[0].start == (1.0, 2.0, 0.0)


def test_t097_as1_control_char_in_value_kept_verbatim() -> None:
    """DESIGN CHOICE (declared): a control char that ``str.splitlines`` WOULD split on
    (\\x0b \\x0c \\x1c-\\x1e) is kept VERBATIM inside the value, never used to break a line,
    so it cannot shift the (code, value) pairing. Here a form-feed inside a TEXT value
    survives the round trip; the drawing still parses."""
    for ctrl in ("\x0b", "\x0c", "\x1c", "\x1d", "\x1e"):
        src = _dxf(
            (0, "SECTION"), (2, "ENTITIES"),
            (0, "TEXT"), (8, "N"), (10, 0.0), (20, 0.0), (1, f"A{ctrl}B"),
            (0, "ENDSEC"), (0, "EOF"),
        )
        result = read_dxf(src)
        assert isinstance(result, DxfDocument), f"ctrl {ctrl!r} broke the parse: {result!r}"
        note = result.primitives[0]
        assert isinstance(note, TextPrimitive)
        assert note.text == f"A{ctrl}B"


def test_t097_as1_mutation_restoring_splitlines_reddens() -> None:
    """NAMED MUTATION (AS-1): restoring ``str.splitlines()`` splits a value on its embedded
    form-feed, shifting pairing, so the clean verbatim parse above no longer holds."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "TEXT"), (8, "N"), (10, 0.0), (20, 0.0), (1, "A\x0cB"),
        (0, "ENDSEC"), (0, "EOF"),
    )
    good = read_dxf(src)
    assert isinstance(good, DxfDocument)
    assert good.primitives[0].text == "A\x0cB"

    original = _reader_mod._iter_dxf_lines

    def _splitlines_mutant(text, limits):  # type: ignore[no-untyped-def]
        yield from text.splitlines()

    try:
        _reader_mod._iter_dxf_lines = _splitlines_mutant  # type: ignore[assignment]
        mutated = read_dxf(src)
    finally:
        _reader_mod._iter_dxf_lines = original
    # Under splitlines the form-feed forges an extra line -> not the clean "A\x0cB" document.
    assert not (
        isinstance(mutated, DxfDocument)
        and mutated.primitives
        and getattr(mutated.primitives[0], "text", None) == "A\x0cB"
    )


# -------------------------------------------------------------------- T097 AS-2: bounds


def test_t097_as2_max_lines_refused() -> None:
    """A line count over ``max_lines`` is a typed refusal VALUE (no existing test pinned
    the too-many-lines refusal itself)."""
    result = read_dxf("0\n" * 50, limits=DxfLimits(max_lines=10))
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.TOO_MANY_LINES


def test_t097_as2_max_lines_enforced_before_full_list_allocation_probe() -> None:
    """WORK/ALLOCATION PROBE (AS-2): ``max_lines`` is enforced WHILE scanning, so the full
    line list is never materialised. On a ~2 MB, one-million-line input capped at 1000 lines
    the streaming splitter's peak allocation is a small fraction of a ``splitlines``-based
    splitter that builds the whole list up front (the AS-2 mutation for this guard)."""
    text = "0\n" * 1_000_000
    limits = DxfLimits(max_lines=1000)

    def _run() -> None:
        assert isinstance(read_dxf(text, limits=limits), DxfRefusal)

    tracemalloc.start()
    try:
        _run()
        _cur, real_peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    result = read_dxf(text, limits=limits)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.TOO_MANY_LINES

    original = _reader_mod._iter_dxf_lines

    def _materialising_mutant(t, lim):  # type: ignore[no-untyped-def]
        lines = t.splitlines()  # builds the ENTIRE million-line list up front
        for i, line in enumerate(lines):
            if i + 1 > lim.max_lines:
                raise _reader_mod._Refuse(DxfRefusalReason.TOO_MANY_LINES, "over")
            yield line

    tracemalloc.start()
    try:
        _reader_mod._iter_dxf_lines = _materialising_mutant  # type: ignore[assignment]
        read_dxf(text, limits=limits)
        _cur, mutant_peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        _reader_mod._iter_dxf_lines = original

    assert real_peak < 2_000_000, f"streaming peak {real_peak} should stay small"
    assert mutant_peak > real_peak * 3, (
        f"materialising mutant peak {mutant_peak} should dwarf streaming {real_peak}"
    )


def test_t097_as2_limits_clamped_above_ceiling() -> None:
    """A caller cannot disable a protection: a bound above its hard ceiling is clamped down."""
    over = DxfLimits(
        max_bytes=10**18,
        max_lines=10**18,
        max_line_chars=10**12,
        max_entities=10**15,
        max_vertices=10**15,
    )
    assert over.max_bytes == 64 * 1024 * 1024
    assert over.max_lines == 8_000_000
    assert over.max_line_chars == 65_536
    assert over.max_entities == 2_000_000
    assert over.max_vertices == 1_000_000


def test_t097_as2_limit_ceilings_are_reviewed_constants() -> None:
    """Drift guard for the hard ceilings (mirrors the DEFAULT_LIMITS drift guard)."""
    assert _reader_mod._LIMIT_CEILINGS == {
        "max_bytes": 64 * 1024 * 1024,
        "max_lines": 8_000_000,
        "max_line_chars": 65_536,
        "max_entities": 2_000_000,
        "max_vertices": 1_000_000,
    }


def test_t097_as2_below_one_limit_still_raises() -> None:
    """The pre-existing lower-bound guard (< 1) still raises, for every field."""
    for field in ("max_bytes", "max_lines", "max_line_chars", "max_entities", "max_vertices"):
        with pytest.raises(ValueError):
            DxfLimits(**{field: 0})


def test_t097_as2_mutation_clamp_reddens() -> None:
    """MUTATION (AS-2, clamp guard): raising the ceiling so the clamp no longer bites lets
    the raw permissive value pass through -> the protection is disabled."""
    assert DxfLimits(max_bytes=10**18).max_bytes == 64 * 1024 * 1024

    original = dict(_reader_mod._LIMIT_CEILINGS)
    try:
        _reader_mod._LIMIT_CEILINGS["max_bytes"] = 10**30
        leaked = DxfLimits(max_bytes=10**18).max_bytes
    finally:
        _reader_mod._LIMIT_CEILINGS.clear()
        _reader_mod._LIMIT_CEILINGS.update(original)
    assert leaked == 10**18  # clamp defeated -> the ceiling/clamp is load-bearing


def test_t097_as2_str_non_ascii_refused() -> None:
    """DESIGN CHOICE (declared): a ``str`` input is CHECKED (not refused outright and not
    passed through leniently) - it goes through the same non-ASCII check as ``bytes``."""
    result = read_dxf("0\nSECTION\n2\nENTITIES\n0\nTEXT\n1\ncaf\xe9\n0\nEOF\n")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.NON_ASCII


def test_t097_as2_str_binary_sentinel_refused() -> None:
    """A ``str`` beginning with the binary-DXF sentinel is refused (previously only the
    bytes path checked it, G5-A3)."""
    result = read_dxf("AutoCAD Binary DXF\r\n\x1a\x00garbage")
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BINARY_DXF


def test_t097_as2_unsupported_input_type_refused() -> None:
    """Neither bytes nor str -> a typed refusal VALUE, never a raised TypeError."""
    result = read_dxf(12345)  # type: ignore[arg-type]
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.MALFORMED_STRUCTURE


def test_t097_as2_mutation_str_check_reddens() -> None:
    """MUTATION (AS-2, str-check guard): a lenient str path (the pre-hardening behaviour)
    passes a non-ASCII str straight through, so the NON_ASCII refusal disappears."""
    src = (
        "0\nSECTION\n2\nENTITIES\n0\nTEXT\n8\nN\n10\n0.0\n20\n0.0\n"
        "1\ncaf\xe9\n0\nENDSEC\n0\nEOF\n"
    )
    assert read_dxf(src).reason is DxfRefusalReason.NON_ASCII  # correct code refuses

    original = _reader_mod._decode

    def _lenient_decode(data, limits):  # type: ignore[no-untyped-def]
        if isinstance(data, bytes):
            return original(data, limits)
        return data  # OLD behaviour: str passes through unchecked

    try:
        _reader_mod._decode = _lenient_decode  # type: ignore[assignment]
        mutated = read_dxf(src)
    finally:
        _reader_mod._decode = original
    assert not (isinstance(mutated, DxfRefusal) and mutated.reason is DxfRefusalReason.NON_ASCII)


# ----------------------------------------------------------------- T097 AS-3: probe gaps


def test_t097_as3_nan_coordinate_refused() -> None:
    """Finiteness was pinned only for ``inf`` (G4-F1); a ``nan`` coordinate is equally
    refused. This kills the M3 survivor (``not isfinite`` -> ``isinf``)."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, "nan"), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.BAD_COORDINATE


def test_t097_as3_nan_probe_kills_finiteness_half_guard() -> None:
    """Teeth for the nan probe: an ``isinf``-only finiteness check (M3) would let nan reach
    a primitive, so the refusal above vanishes."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, "nan"), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    import math as _math

    original = _reader_mod._to_float

    def _half_guard(value):  # type: ignore[no-untyped-def]
        parsed = float(value)
        if _math.isinf(parsed):  # M3: only inf, not nan
            raise _reader_mod._Refuse(DxfRefusalReason.BAD_COORDINATE, "non-finite")
        return parsed

    try:
        _reader_mod._to_float = _half_guard  # type: ignore[assignment]
        mutated = read_dxf(src)
    finally:
        _reader_mod._to_float = original
    reddened = isinstance(mutated, DxfRefusal) and mutated.reason is DxfRefusalReason.BAD_COORDINATE
    assert not reddened


def test_t097_as3_negative_lwpolyline_bulge_refused() -> None:
    """A NEGATIVE bulge is just as much an arc as a positive one (G4-F2); refused. This
    kills the M4a survivor (``!= 0`` -> ``> 0``)."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LWPOLYLINE"), (8, "LOT"), (90, 2), (70, 1),
        (10, 0.0), (20, 0.0), (42, -0.5),
        (10, 10.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.UNSUPPORTED_BULGE


def test_t097_as3_negative_vertex_bulge_refused() -> None:
    """The old-style POLYLINE/VERTEX bulge path had NO test at all (G4-F2); a negative
    VERTEX bulge is refused. This kills the M4b survivor."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "POLYLINE"), (8, "B"), (70, 1),
        (0, "VERTEX"), (8, "B"), (10, 0.0), (20, 0.0), (42, -0.3),
        (0, "VERTEX"), (8, "B"), (10, 10.0), (20, 0.0),
        (0, "SEQEND"), (8, "B"),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.UNSUPPORTED_BULGE


def test_t097_as3_closed_flag_128_is_open() -> None:
    """Only bit 1 of the 70 flags means closed (G4-F3); flag 128 (bit 7) is NOT closed.
    This kills the M5 survivor (``& 1`` -> ``bool(flags)``)."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LWPOLYLINE"), (8, "LOT"), (90, 2), (70, 128),
        (10, 0.0), (20, 0.0),
        (10, 10.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    poly = result.primitives[0]
    assert isinstance(poly, PolylinePrimitive)
    assert poly.closed is False


def test_t097_as3_closed_flag_129_is_closed() -> None:
    """Flag 129 (bit 7 + bit 1) IS closed - bit 1 is set."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LWPOLYLINE"), (8, "LOT"), (90, 2), (70, 129),
        (10, 0.0), (20, 0.0),
        (10, 10.0), (20, 0.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    result = read_dxf(src)
    assert isinstance(result, DxfDocument)
    poly = result.primitives[0]
    assert isinstance(poly, PolylinePrimitive)
    assert poly.closed is True


def test_t097_as3_insunits_survey_inch_yard_mile_reported() -> None:
    """The official US survey inch/yard/mile codes 22/23/24 are now reported as named units
    instead of ``unknown_insunits_N`` (G1 advisory / DB-057 (n))."""
    for code, name in ((22, "us_survey_inches"), (23, "us_survey_yards"), (24, "us_survey_miles")):
        src = _dxf(
            (0, "SECTION"), (2, "HEADER"), (9, "$INSUNITS"), (70, code), (0, "ENDSEC"),
            (0, "SECTION"), (2, "ENTITIES"),
            (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
            (0, "ENDSEC"), (0, "EOF"),
        )
        result = read_dxf(src)
        assert isinstance(result, DxfDocument)
        assert result.units.code == code
        assert result.units.name == name


def test_t097_as3_mutation_insunits_codes_reddens() -> None:
    """MUTATION: removing 22/23/24 from the unit map returns them to
    ``unknown_insunits_N`` -> the named-unit assertion above reddens."""
    src = _dxf(
        (0, "SECTION"), (2, "HEADER"), (9, "$INSUNITS"), (70, 22), (0, "ENDSEC"),
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (10, 0.0), (20, 0.0), (11, 1.0), (21, 1.0),
        (0, "ENDSEC"), (0, "EOF"),
    )
    assert read_dxf(src).units.name == "us_survey_inches"  # correct map

    original = dict(_reader_mod._INSUNITS_NAMES)
    try:
        for code in (22, 23, 24):
            _reader_mod._INSUNITS_NAMES.pop(code, None)
        mutated = read_dxf(src)
    finally:
        _reader_mod._INSUNITS_NAMES.clear()
        _reader_mod._INSUNITS_NAMES.update(original)
    assert mutated.units.name == "unknown_insunits_22"


# ---------------------------------------- T097 round 2: G3-B1 / G5-F1 splitter complexity


_SUBQUADRATIC_RATIO_CEIL = 8.0  # linear ~4x per 4x input; the old double-find is ~12-16x


def _splitter_scaling_ratio(
    term: str, n: int, *, reps_small: int = 3, reps_large: int = 2
) -> float:
    """Consume the CONSUMED splitter on ``n`` and ``4n`` single-char lines terminated by
    ``term`` and return the 4x-input time ratio (min over reps to damp scheduler noise). A
    linear scan is ~4x; the reviewed round-1 per-line double-find is O(n^2) and ~12-16x. The
    ratio is machine-speed-independent, so no tight absolute wall-clock is asserted."""
    limits = DxfLimits(max_lines=8_000_000, max_line_chars=65_536)
    small = ("0" + term) * n
    large = ("0" + term) * (4 * n)

    def _best(text: str, reps: int) -> float:
        best = float("inf")
        total = 0
        for _ in range(reps):
            t0 = time.perf_counter()
            total = sum(1 for _ in _reader_mod._iter_dxf_lines(text, limits))
            best = min(best, time.perf_counter() - t0)
        assert total == text.count(term)  # every line consumed, no over/under count
        return best

    return _best(large, reps_large) / _best(small, reps_small)


def test_t097_b1_splitter_time_subquadratic_pure_lf_and_cr() -> None:
    """G3-B1 / G5-F1 GUARD: the line splitter must be ~linear, not O(n^2), on pure-LF (our own
    writer's output) and pure-CR input. Parse N and 4N lines; a linear scan scales ~4x, the old
    per-line double-find ~16x. Require the 4x ratio < 8 (2x margin over linear, generous for a
    loaded CI runner). The mutation test below rebinds the consumed splitter to that double-find
    and shows this ceiling reddens."""
    for term in ("\n", "\r"):
        ratio = _splitter_scaling_ratio(term, 30_000)
        assert ratio < _SUBQUADRATIC_RATIO_CEIL, (
            f"term {term!r} scaling {ratio:.1f}x looks quadratic "
            f"(linear ~4x, quadratic ~16x, ceiling {_SUBQUADRATIC_RATIO_CEIL})"
        )


def test_t097_b1_mutation_double_find_reddens_time_guard() -> None:
    """MUTATION (G3-B1 / G5-F1): rebinding the consumed splitter to the reviewed round-1
    double-find (both ``find('\\n')`` AND ``find('\\r')`` every line) restores the O(n^2)
    rescan-to-EOF for an absent terminator, so the sub-quadratic ceiling reddens. Must-stay-PASS:
    the real splitter passes the same check at the same size."""
    original = _reader_mod._iter_dxf_lines

    def _double_find_mutant(text, limits):  # type: ignore[no-untyped-def]
        n = len(text)
        pos = 0
        count = 0
        while pos < n:
            nl = text.find("\n", pos)
            cr = text.find("\r", pos)
            if nl == -1 and cr == -1:
                end = nxt = n
            elif cr == -1 or (nl != -1 and nl < cr):
                end, nxt = nl, nl + 1
            else:
                end = cr
                nxt = cr + 2 if (cr + 1 < n and text[cr + 1] == "\n") else cr + 1
            line = text[pos:end]
            count += 1
            if count > limits.max_lines:
                raise _reader_mod._Refuse(DxfRefusalReason.TOO_MANY_LINES, "over")
            if len(line) > limits.max_line_chars:
                raise _reader_mod._Refuse(DxfRefusalReason.LINE_TOO_LONG, "over")
            yield line
            pos = nxt

    try:
        _reader_mod._iter_dxf_lines = _double_find_mutant  # type: ignore[assignment]
        mutant_ratio = _splitter_scaling_ratio("\n", 30_000, reps_small=3, reps_large=1)
    finally:
        _reader_mod._iter_dxf_lines = original

    assert mutant_ratio >= _SUBQUADRATIC_RATIO_CEIL, (
        f"the double-find should scale quadratically (>= {_SUBQUADRATIC_RATIO_CEIL}x); "
        f"measured {mutant_ratio:.1f}x - the guard did not redden"
    )
    # must-stay-PASS: the real splitter is comfortably sub-quadratic at the same size.
    assert _splitter_scaling_ratio("\n", 30_000) < _SUBQUADRATIC_RATIO_CEIL


# ---------------------------------------- T097 round 2: G4 ADVISORY-1 exact-edge cap probes


def test_t097_as2_max_lines_exact_edge_refuses_at_limit_plus_one() -> None:
    """G4 ADVISORY-1: pin ``max_lines`` at the EXACT edge so the off-by-one mutant
    (``count > max`` -> ``count > max + 1``, G4 B6) dies. The fixture is a valid 20-line DXF:
    ``max_lines=20`` (exactly at the limit) parses; ``max_lines=19`` (the file is limit+1 lines)
    refuses TOO_MANY_LINES. The correct code refuses at line ``max_lines+1``; a +1 mutant would
    not, so the limit-1 assertion reddens under it."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 1.0), (20, 2.0), (11, 3.0), (21, 4.0),
        (0, "ENDSEC"), (0, "EOF"),
    )  # 10 pairs -> exactly 20 lines
    assert sum(1 for _ in _reader_mod._iter_dxf_lines(src, DEFAULT_LIMITS)) == 20
    at_limit = read_dxf(src, limits=DxfLimits(max_lines=20))
    assert isinstance(at_limit, DxfDocument)  # exactly at the limit still passes
    over_by_one = read_dxf(src, limits=DxfLimits(max_lines=19))
    assert isinstance(over_by_one, DxfRefusal)
    assert over_by_one.reason is DxfRefusalReason.TOO_MANY_LINES


def test_t097_as2_max_line_chars_exact_edge_refuses_at_limit_plus_one() -> None:
    """G4 ADVISORY-1: pin ``max_line_chars`` at the EXACT edge so the off-by-one mutant
    (``len(line) > max`` -> ``len(line) > max + 1``, G4 B7) dies. The longest line is a 30-char
    TEXT value: ``max_line_chars=30`` (at the limit) parses; ``max_line_chars=29`` (the line is
    limit+1 chars) refuses LINE_TOO_LONG."""
    src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "TEXT"), (8, "A"), (10, 0.0), (20, 0.0), (1, "X" * 30),
        (0, "ENDSEC"), (0, "EOF"),
    )  # longest line is the 30-char TEXT value
    at_limit = read_dxf(src, limits=DxfLimits(max_line_chars=30))
    assert isinstance(at_limit, DxfDocument)  # exactly at the limit still passes
    over_by_one = read_dxf(src, limits=DxfLimits(max_line_chars=29))
    assert isinstance(over_by_one, DxfRefusal)
    assert over_by_one.reason is DxfRefusalReason.LINE_TOO_LONG


def test_t097_as2_mutation_off_by_one_line_caps_reddens() -> None:
    """MUTATION (G4 B6/B7): shifting BOTH caps by one (``> max`` -> ``> max + 1``) makes the
    limit+1 file/line slip through, so both exact-edge probes above redden. Must-stay-PASS: the
    real splitter refuses at limit+1 (asserted as the baseline)."""
    lines_src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "LINE"), (8, "A"), (10, 1.0), (20, 2.0), (11, 3.0), (21, 4.0),
        (0, "ENDSEC"), (0, "EOF"),
    )  # 20 lines
    chars_src = _dxf(
        (0, "SECTION"), (2, "ENTITIES"),
        (0, "TEXT"), (8, "A"), (10, 0.0), (20, 0.0), (1, "X" * 30),
        (0, "ENDSEC"), (0, "EOF"),
    )
    # baseline: the real code refuses at limit+1
    assert isinstance(read_dxf(lines_src, limits=DxfLimits(max_lines=19)), DxfRefusal)
    assert isinstance(read_dxf(chars_src, limits=DxfLimits(max_line_chars=29)), DxfRefusal)

    original = _reader_mod._iter_dxf_lines

    def _off_by_one_mutant(text, limits):  # type: ignore[no-untyped-def]
        n = len(text)
        pos = 0
        count = 0
        search = _reader_mod._LINE_TERMINATOR.search
        while pos < n:
            match = search(text, pos)
            end, nxt = (n, n) if match is None else (match.start(), match.end())
            line = text[pos:end]
            count += 1
            if count > limits.max_lines + 1:  # B6 off-by-one
                raise _reader_mod._Refuse(DxfRefusalReason.TOO_MANY_LINES, "over")
            if len(line) > limits.max_line_chars + 1:  # B7 off-by-one
                raise _reader_mod._Refuse(DxfRefusalReason.LINE_TOO_LONG, "over")
            yield line
            pos = nxt

    try:
        _reader_mod._iter_dxf_lines = _off_by_one_mutant  # type: ignore[assignment]
        lines_mut = read_dxf(lines_src, limits=DxfLimits(max_lines=19))
        chars_mut = read_dxf(chars_src, limits=DxfLimits(max_line_chars=29))
    finally:
        _reader_mod._iter_dxf_lines = original

    # Under the off-by-one the limit+1 file/line is no longer refused -> the edge probes redden.
    assert isinstance(lines_mut, DxfDocument)
    assert isinstance(chars_mut, DxfDocument)
