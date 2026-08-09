"""Tests for the fail-closed PDF composite-object parser (M2-T015 unit 3i-3a-2).

Every refusal must be a PdfSyntaxError VALUE (the lexer's class, reused
verbatim) — parsing never raises on any byte input.
"""

from __future__ import annotations

from app.documents.extraction.pdf_lexer import PdfName, PdfSyntaxError
from app.documents.extraction.pdf_objects import (
    MAX_COLLECTION_ITEMS,
    MAX_NESTING_DEPTH,
    ParsedObject,
    PdfIndirectObject,
    PdfRef,
    PdfStream,
    parse_indirect_object,
    parse_object,
)


def ok(data: bytes, offset: int = 0) -> ParsedObject:
    result = parse_object(data, offset)
    assert isinstance(result, ParsedObject), result
    return result


def refuse(data: bytes, offset: int = 0) -> PdfSyntaxError:
    result = parse_object(data, offset)
    assert isinstance(result, PdfSyntaxError), result
    return result


def ok_indirect(data: bytes, offset: int = 0) -> ParsedObject:
    result = parse_indirect_object(data, offset)
    assert isinstance(result, ParsedObject), result
    return result


def refuse_indirect(data: bytes, offset: int = 0) -> PdfSyntaxError:
    result = parse_indirect_object(data, offset)
    assert isinstance(result, PdfSyntaxError), result
    return result


# --- primitives pass through -------------------------------------------------


def test_primitives_pass_through() -> None:
    assert ok(b"42").value == 42
    assert ok(b"-1.5").value == -1.5
    assert ok(b"(hi)").value == b"hi"
    assert ok(b"<4869>").value == b"Hi"
    assert ok(b"/Name").value == PdfName("Name")
    assert ok(b"true").value is True
    assert ok(b"null").value is None


def test_trailing_bytes_never_consumed() -> None:
    parsed = ok(b"42 junk")
    assert parsed.value == 42
    assert parsed.end_offset == 2


# --- arrays and dictionaries -------------------------------------------------


def test_empty_array_and_dict() -> None:
    assert ok(b"[]").value == []
    assert ok(b"[]").end_offset == 2
    assert ok(b"<<>>").value == {}
    assert ok(b"<<>>").end_offset == 4


def test_nested_arrays_round_trip() -> None:
    parsed = ok(b"[1 [2 [3 (x)]] /N]")
    assert parsed.value == [1, [2, [3, b"x"]], PdfName("N")]
    assert parsed.end_offset == 18


def test_nested_dict_round_trip() -> None:
    parsed = ok(b"<< /A << /B [1 2 (x)] >> /C /Name >>")
    assert parsed.value == {
        PdfName("A"): {PdfName("B"): [1, 2, b"x"]},
        PdfName("C"): PdfName("Name"),
    }


def test_dict_compact_without_spaces() -> None:
    assert ok(b"<</A/B>>").value == {PdfName("A"): PdfName("B")}
    assert ok(b"<</K<</K 1>>>>").value == {PdfName("K"): {PdfName("K"): 1}}


def test_dict_null_value_preserved() -> None:
    value = ok(b"<</A null>>").value
    assert value == {PdfName("A"): None}
    assert PdfName("A") in value


def test_dict_non_name_key_refused() -> None:
    error = refuse(b"<<(k) 1>>")
    assert error.expected.startswith("name key")


def test_dict_duplicate_key_refused() -> None:
    error = refuse(b"<</A 1 /A 2>>")
    assert error.expected == "unique dictionary key"


def test_dict_duplicate_key_after_hash_decoding_refused() -> None:
    # /A#42 decodes to /AB, so this is the same key twice (§7.3.5 identity).
    error = refuse(b"<</AB 1 /A#42 2>>")
    assert error.expected == "unique dictionary key"


# --- indirect-reference disambiguation ---------------------------------------


def test_top_level_reference() -> None:
    parsed = ok(b"1 0 R")
    assert parsed.value == PdfRef(1, 0)
    assert parsed.end_offset == 5


def test_three_integers_without_r_stand_alone() -> None:
    assert ok(b"[1 0 2]").value == [1, 0, 2]


def test_reference_inside_array() -> None:
    assert ok(b"[1 0 R]").value == [PdfRef(1, 0)]
    assert ok(b"[1 0 R 2 3 R]").value == [PdfRef(1, 0), PdfRef(2, 3)]
    assert ok(b"[1 0 2 3 R]").value == [1, 0, PdfRef(2, 3)]


def test_reference_as_dict_value() -> None:
    assert ok(b"<</A 4 1 R>>").value == {PdfName("A"): PdfRef(4, 1)}


def test_reference_lookahead_across_comment() -> None:
    assert ok(b"1 % note\n0 R").value == PdfRef(1, 0)


def test_negative_reference_integers_refused() -> None:
    assert "non-negative" in refuse(b"[-1 0 R]").expected
    assert "non-negative" in refuse(b"[1 -2 R]").expected


def test_real_number_never_starts_reference() -> None:
    # 1.0 cannot begin a reference, so the bare R is hit and refused.
    refuse(b"[1.0 0 R]")


def test_r_glued_to_bytes_is_not_the_keyword() -> None:
    refuse(b"[1 0 R5]")


# --- streams ------------------------------------------------------------------


def test_stream_happy_path_crlf() -> None:
    raw = b"\x00\x01\xffAB\n"
    data = b"<</Length 6>> stream\r\n" + raw + b"\r\nendstream"
    parsed = ok(data)
    assert parsed.value == PdfStream({PdfName("Length"): 6}, raw)
    assert parsed.end_offset == len(data)


def test_stream_happy_path_lf() -> None:
    data = b"<</Length 5>> stream\nHELLO\nendstream"
    parsed = ok(data)
    assert parsed.value == PdfStream({PdfName("Length"): 5}, b"HELLO")
    assert parsed.end_offset == len(data)


def test_stream_raw_data_is_undecoded_exact_span() -> None:
    raw = b"(not) <a token> [stream"  # delimiters inside data must be untouched
    data = b"<</Length %d>>stream\n" % len(raw) + raw + b"\nendstream"
    assert ok(data).value.raw_data == raw


def test_stream_comment_between_dict_and_keyword() -> None:
    data = b"<</Length 1>> % c\nstream\nA\nendstream"
    assert ok(data).value == PdfStream({PdfName("Length"): 1}, b"A")


def test_stream_indirect_length_refused() -> None:
    error = refuse(b"<</Length 2 0 R>> stream\nAB\nendstream")
    assert error.expected == "direct /Length integer"
    assert error.found == "indirect reference"


def test_stream_missing_length_refused() -> None:
    error = refuse(b"<</A 1>> stream\nAB\nendstream")
    assert error.expected == "direct /Length integer"


def test_stream_negative_length_refused() -> None:
    error = refuse(b"<</Length -1>> stream\nAB\nendstream")
    assert error.expected == "direct /Length integer"


def test_stream_real_length_refused() -> None:
    error = refuse(b"<</Length 2.0>> stream\nAB\nendstream")
    assert error.expected == "direct /Length integer"


def test_stream_cr_alone_after_keyword_refused() -> None:
    error = refuse(b"<</Length 1>> stream\rA\nendstream")
    assert error.expected == "CRLF or LF after 'stream'"


def test_stream_space_after_keyword_refused() -> None:
    error = refuse(b"<</Length 1>> stream A\nendstream")
    assert error.expected == "CRLF or LF after 'stream'"


def test_stream_length_past_end_of_data_refused() -> None:
    error = refuse(b"<</Length 10>> stream\nAB")
    assert error.found == "end of data"


def test_stream_missing_endstream_refused() -> None:
    error = refuse(b"<</Length 2>> stream\nABjunk")
    assert error.expected == "'endstream'"
    error = refuse(b"<</Length 2>> stream\nAB")
    assert error.expected == "'endstream'"


def test_nested_dict_is_never_a_stream() -> None:
    # A dictionary inside an array is a plain dictionary...
    assert ok(b"[<</Length 1>>]").value == [{PdfName("Length"): 1}]
    # ...and a 'stream' keyword after it is refused, not consumed.
    refuse(b"[<</Length 1>> stream]")


# --- bounds --------------------------------------------------------------------


def test_nesting_depth_at_bound_parses() -> None:
    data = b"[" * MAX_NESTING_DEPTH + b"]" * MAX_NESTING_DEPTH
    parsed = ok(data)
    assert parsed.end_offset == len(data)


def test_nesting_depth_beyond_bound_refused() -> None:
    depth = MAX_NESTING_DEPTH + 1
    error = refuse(b"[" * depth + b"]" * depth)
    assert str(MAX_NESTING_DEPTH) in error.expected
    error = refuse(b"<</A " * depth + b"1" + b">>" * depth)
    assert str(MAX_NESTING_DEPTH) in error.expected


def test_array_items_at_bound_parse() -> None:
    data = b"[" + b"0 " * MAX_COLLECTION_ITEMS + b"]"
    assert len(ok(data).value) == MAX_COLLECTION_ITEMS


def test_array_items_beyond_bound_refused() -> None:
    error = refuse(b"[" + b"0 " * (MAX_COLLECTION_ITEMS + 1) + b"]")
    assert str(MAX_COLLECTION_ITEMS) in error.expected


def test_dict_entries_beyond_bound_refused() -> None:
    entries = b"".join(
        b"/K%d 0 " % i for i in range(MAX_COLLECTION_ITEMS + 1)
    )
    error = refuse(b"<<" + entries + b">>")
    assert str(MAX_COLLECTION_ITEMS) in error.expected


# --- truncation at each construct ----------------------------------------------


def test_truncations_refused() -> None:
    assert refuse(b"").found == "end of data"
    assert refuse(b"[1 2").found == "end of data"
    assert refuse(b"<<").found == "end of data"
    assert refuse(b"<</A").found == "end of data"
    assert refuse(b"<</A 1").found == "end of data"
    assert refuse(b"(abc").found == "end of data"  # lexer refusal propagates
    assert refuse_indirect(b"1 0").found == "end of data"
    assert refuse_indirect(b"1 0 obj").found == "end of data"
    assert refuse_indirect(b"1 0 obj (x)").found == "end of data"


# --- indirect objects ------------------------------------------------------------


def test_indirect_object_happy_path() -> None:
    data = b"7 0 obj (hi) endobj"
    parsed = ok_indirect(data)
    assert parsed.value == PdfIndirectObject(7, 0, b"hi")
    assert parsed.end_offset == len(data)


def test_indirect_object_with_reference_body() -> None:
    assert ok_indirect(b"5 7 obj [1 0 R] endobj").value == PdfIndirectObject(
        5, 7, [PdfRef(1, 0)]
    )


def test_indirect_object_with_stream_body() -> None:
    data = b"12 3 obj <</Length 4>> stream\nABCD\nendstream endobj"
    parsed = ok_indirect(data)
    assert parsed.value == PdfIndirectObject(
        12, 3, PdfStream({PdfName("Length"): 4}, b"ABCD")
    )
    assert parsed.end_offset == len(data)


def test_indirect_object_zero_number_allowed_here() -> None:
    # Positivity of the object number is the cross-reference layer's rule.
    assert ok_indirect(b"0 0 obj null endobj").value == PdfIndirectObject(0, 0, None)


def test_indirect_object_negative_numbers_refused() -> None:
    assert "object number" in refuse_indirect(b"-1 0 obj null endobj").expected
    assert "generation" in refuse_indirect(b"1 -1 obj null endobj").expected


def test_indirect_object_non_integer_numbers_refused() -> None:
    assert "object number" in refuse_indirect(b"1.0 0 obj null endobj").expected
    assert "object number" in refuse_indirect(b"true 0 obj null endobj").expected


def test_indirect_object_wrong_keywords_refused() -> None:
    assert refuse_indirect(b"1 0 xobj null endobj").expected == "'obj'"
    assert refuse_indirect(b"1 0 obj null endobjx").expected == "'endobj'"
    assert refuse_indirect(b"1 0 obj null").expected == "'endobj'"


def test_indirect_object_empty_body_refused() -> None:
    # 'endobj' where the body should be is a keyword the lexer refuses.
    refuse_indirect(b"1 0 obj endobj")


# --- refusal contract --------------------------------------------------------------


def test_negative_offset_refused() -> None:
    assert refuse(b"1", -1).expected == "non-negative offset"
    assert refuse_indirect(b"1 0 obj null endobj", -1).expected == "non-negative offset"


def test_composite_leftovers_refused_not_raised() -> None:
    refuse(b"{ }")  # procedures stay refused
    refuse(b"stream")  # structural keyword alone
    refuse(b">>")
    refuse(b"]")


def test_refusals_are_the_lexer_error_type_with_payload() -> None:
    error = refuse(b"<</A 1 /A 2>>")
    payload = error.to_payload()
    assert payload["reject_code"] == "pdf_syntax_error"
    assert payload["expected"] == "unique dictionary key"
    assert isinstance(payload["offset"], int)
