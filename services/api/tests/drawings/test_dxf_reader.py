"""Strict-subset ASCII DXF reader tests (M5-T086, D-087 CAD-3).

Every fixture is a hand-written DXF group-code stream built with :func:`_dxf`, which always
emits an even (group-code, value) line count. The suite proves the parsed subset, units
honesty, the disclose-or-refuse rule, every fail-closed bound, and the two named mutations.
"""

from __future__ import annotations

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
    """MUTATION #2: deleting the odd-line-count guard in `_to_pairs` makes the pairing
    loop read past the final line (IndexError -> MALFORMED_STRUCTURE), so the reason is no
    longer ODD_PAIR_COUNT -> this assertion reddens."""
    src = _full_drawing() + "0\n"  # single extra line -> odd total line count
    result = read_dxf(src)
    assert isinstance(result, DxfRefusal)
    assert result.reason is DxfRefusalReason.ODD_PAIR_COUNT
