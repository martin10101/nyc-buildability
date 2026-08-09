"""Tests for the fail-closed PDF primitive lexer (M2-T015 unit 3i-3a-1b).

Covers every accepted token kind, the spec-mandated normalizations,
whitespace/comment skipping, ``end_offset`` resumption, and every refusal
path, asserting the ``PdfSyntaxError`` offset/expected/found diagnostics
and the ``to_payload()`` shape. The module under test is a pure function
of ``bytes``: no fixtures, no I/O, no mocks.
"""

import pytest

from app.documents.extraction.pdf_lexer import (
    MAX_NUMBER_BYTES,
    MAX_TOKEN_BYTES,
    LexedToken,
    PdfName,
    PdfSyntaxError,
    lex_primitive,
)


def _token(data: bytes, offset: int = 0) -> LexedToken:
    result = lex_primitive(data, offset)
    assert isinstance(result, LexedToken), f"expected token, got {result!r}"
    return result


def _refusal(data: bytes, offset: int = 0) -> PdfSyntaxError:
    result = lex_primitive(data, offset)
    assert isinstance(result, PdfSyntaxError), f"expected refusal, got {result!r}"
    return result


# ---------------------------------------------------------------- keywords


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"true", True, 4),
        (b"false", False, 5),
        (b"null", None, 4),
    ],
)
def test_boolean_and_null(data, expected, end):
    token = _token(data)
    assert token.value is expected
    assert token.end_offset == end


def test_keyword_terminated_by_delimiter_leaves_delimiter():
    token = _token(b"true)")
    assert token.value is True
    assert token.end_offset == 4


# ----------------------------------------------------------------- numbers


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"7", 7, 1),
        (b"123", 123, 3),
        (b"+17", 17, 3),
        (b"-98", -98, 3),
        (b"0", 0, 1),
        (b"-0", 0, 2),
        (b"00042", 42, 5),
    ],
)
def test_integers(data, expected, end):
    token = _token(data)
    assert type(token.value) is int
    assert token.value == expected
    assert token.end_offset == end


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"34.5", 34.5, 4),
        (b"-3.62", -3.62, 5),
        (b"+123.6", 123.6, 6),
        (b"4.", 4.0, 2),  # trailing-dot form
        (b".5", 0.5, 2),  # leading-dot form
        (b"-.002", -0.002, 5),
        (b"0.0", 0.0, 3),
    ],
)
def test_reals(data, expected, end):
    token = _token(data)
    assert type(token.value) is float
    assert token.value == expected
    assert token.end_offset == end


@pytest.mark.parametrize("data", [b"1e5", b"1E5", b"6.02e23"])
def test_exponent_reals_refused(data):
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == "number without exponent"
    assert err.found == data.decode("ascii")


@pytest.mark.parametrize("data", [b".", b"+", b"-", b"1.2.3", b"--1", b"1-2"])
def test_malformed_numbers_refused(data):
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == "number"
    assert err.found == data.decode("ascii")


def test_number_longer_than_max_number_bytes_refused():
    data = b"9" * (MAX_NUMBER_BYTES + 1)
    assert len(data) < MAX_TOKEN_BYTES  # the number bound trips, not the token bound
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == f"number of at most {MAX_NUMBER_BYTES} bytes"
    assert err.found.endswith("...")  # bounded diagnostic, not a raw echo


# ---------------------------------------------------------- literal strings


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"(hello)", b"hello", 7),
        (b"()", b"", 2),
        (b"(a(b(c))d)", b"a(b(c))d", 10),  # nested balanced parens kept verbatim
        (b"(()())", b"()()", 6),
    ],
)
def test_literal_strings_basic_and_nested(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


def test_literal_string_every_simple_escape():
    token = _token(rb"(\n\r\t\b\f\(\)\\)")
    assert token.value == b"\n\r\t\b\f()\\"
    assert token.end_offset == 18


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (rb"(\0)", b"\x00", 4),  # 1-digit octal
        (rb"(\53)", b"+", 5),  # 2-digit octal
        (rb"(\053)", b"+", 6),  # 3-digit octal
        (rb"(\0053)", b"\x053", 7),  # octal stops at 3 digits; '3' is literal
        (rb"(\18)", b"\x018", 5),  # octal stops at non-octal digit
        (rb"(\777)", b"\xff", 6),  # high-order overflow wraps to one byte
    ],
)
def test_literal_string_octal_escape_edges(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"(a\\\nb)", b"ab", 6),  # backslash-LF continuation
        (b"(a\\\rb)", b"ab", 6),  # backslash-CR continuation
        (b"(a\\\r\nb)", b"ab", 7),  # backslash-CRLF continuation
    ],
)
def test_literal_string_line_continuation(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"(a\rb)", b"a\nb", 5),
        (b"(a\r\nb)", b"a\nb", 6),
    ],
)
def test_literal_string_unescaped_eol_normalizes_to_lf(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


def test_literal_string_unknown_escape_refused():
    err = _refusal(rb"(\z)")
    assert err.offset == 1  # position of the backslash
    assert err.expected == "string escape"
    assert err.found == "\\z"


@pytest.mark.parametrize("data", [b"(abc", b"(abc\\", b"(a(b)"])
def test_literal_string_unterminated_refused(data):
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == "')'"
    assert err.found == "end of data"


# --------------------------------------------------------------- hex strings


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"<901FA3>", b"\x90\x1f\xa3", 8),
        (b"<90 1F\nA3>", b"\x90\x1f\xa3", 10),  # interior whitespace ignored
        (b"<901FA>", b"\x90\x1f\xa0", 7),  # odd final digit implies trailing 0
        (b"<>", b"", 2),
        (b"<9a0B>", b"\x9a\x0b", 6),  # mixed case digits
    ],
)
def test_hex_strings(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


def test_hex_string_bad_digit_refused():
    err = _refusal(b"<90G1>")
    assert err.offset == 3  # position of the bad byte
    assert err.expected == "hexadecimal digit"
    assert err.found == "G"


def test_hex_string_bad_unprintable_digit_is_escaped_in_diagnostic():
    err = _refusal(b"<9\x01>")
    assert err.offset == 2
    assert err.expected == "hexadecimal digit"
    assert err.found == "\\x01"


@pytest.mark.parametrize("data", [b"<90", b"<AB CD"])
def test_hex_string_unterminated_refused(data):
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == "'>'"
    assert err.found == "end of data"


# --------------------------------------------------------------------- names


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"/Name", "Name", 5),
        (b"/", "", 1),  # bare '/' is the valid empty name
        (b"/1.2", "1.2", 4),  # numeric-looking names stay names
        (b"/A#20B", "A B", 6),  # #xx hex escape
        (b"/paired#28#29parens", "paired()parens", 19),
        (b"/caf#E9", "caf\xe9", 7),  # decoded byte kept losslessly as latin-1
    ],
)
def test_names(data, expected, end):
    token = _token(data)
    assert token.value == PdfName(expected)
    assert token.end_offset == end


def test_adjacent_names_resume_by_end_offset():
    first = _token(b"/Type/Subtype")
    assert first.value == PdfName("Type")
    assert first.end_offset == 5
    second = _token(b"/Type/Subtype", first.end_offset)
    assert second.value == PdfName("Subtype")
    assert second.end_offset == 13


@pytest.mark.parametrize(
    ("data", "offset", "found"),
    [
        (b"/A#G1", 2, "#G1"),  # non-hex digits after '#'
        (b"/A#4", 2, "#4"),  # only one digit before end of data
        (b"/A#", 2, "end of data"),  # '#' with nothing after it
    ],
)
def test_name_bad_hash_escape_refused(data, offset, found):
    err = _refusal(data)
    assert err.offset == offset
    assert err.expected == "two hexadecimal digits after '#'"
    assert err.found == found


def test_name_nul_escape_refused():
    err = _refusal(b"/A#00")
    assert err.offset == 2
    assert err.expected == "non-NUL name escape"
    assert err.found == "#00"


# ------------------------------------------- whitespace and comment skipping


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"   true", True, 7),
        (b"\x00\t\n\x0c\r 7", 7, 7),  # every whitespace byte class
        (b"% comment\n42", 42, 12),  # comment to LF, then token
        (b"% c\r7", 7, 5),  # comment ended by CR
        (b"%a\r%b\n  123", 123, 11),  # consecutive comments and whitespace
    ],
)
def test_whitespace_and_comments_skipped(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


@pytest.mark.parametrize(
    ("data", "offset"),
    [
        (b"", 0),
        (b"   ", 3),
        (b"% only a comment", 16),  # comment runs to end of data
    ],
)
def test_end_of_data_refused(data, offset):
    err = _refusal(data)
    assert err.offset == offset
    assert err.expected == "token"
    assert err.found == "end of data"


# ------------------------------------------------- end_offset advance walks


def test_sequential_lexing_advances_by_end_offset():
    data = b"12 3.5 (ab) <CD> /N true null"
    expected = [
        (12, 2),
        (3.5, 6),
        (b"ab", 11),
        (b"\xcd", 16),
        (PdfName("N"), 19),
        (True, 24),
        (None, 29),
    ]
    offset = 0
    for value, end in expected:
        token = _token(data, offset)
        assert token.value == value
        assert token.end_offset == end
        offset = token.end_offset
    err = _refusal(data, offset)
    assert err.offset == len(data)
    assert err.found == "end of data"


@pytest.mark.parametrize(
    ("data", "expected", "end"),
    [
        (b"12]", 12, 2),  # trailing delimiter never consumed
        (b"true%c", True, 4),  # '%' is a delimiter, not part of the token
        (b"(ab)(cd)", b"ab", 4),
        (b"/A/B", PdfName("A"), 2),
    ],
)
def test_trailing_bytes_never_consumed(data, expected, end):
    token = _token(data)
    assert token.value == expected
    assert token.end_offset == end


# ----------------------------------------------------------- refusal paths


def test_negative_offset_refused():
    err = _refusal(b"true", -1)
    assert err.offset == -1
    assert err.expected == "non-negative offset"
    assert err.found == "negative offset"


@pytest.mark.parametrize(
    "found",
    ["[", "]", "<<", ">>", "{", "}", ")", ">"],
)
def test_composite_delimiters_refused(found):
    err = _refusal(found.encode("ascii"))
    assert err.offset == 0
    assert err.expected == "primitive token"
    assert err.found == found


@pytest.mark.parametrize("keyword", ["obj", "endobj", "stream", "R"])
def test_structural_keywords_refused(keyword):
    err = _refusal(keyword.encode("ascii"))
    assert err.offset == 0
    assert err.expected == "primitive token"
    assert err.found == keyword


def test_keyword_refusal_offset_after_skipped_whitespace():
    err = _refusal(b"  stream")
    assert err.offset == 2
    assert err.expected == "primitive token"
    assert err.found == "stream"


def test_unknown_bareword_refused_with_bounded_diagnostic():
    err = _refusal(b"z" * 100)
    assert err.offset == 0
    assert err.expected == "primitive token"
    assert err.found.endswith("...")
    assert len(err.found) < 100  # truncated, never a raw echo


@pytest.mark.parametrize(
    "data",
    [
        b"(" + b"a" * MAX_TOKEN_BYTES + b")",
        b"<" + b"0" * MAX_TOKEN_BYTES + b">",
        b"/" + b"a" * MAX_TOKEN_BYTES,
    ],
    ids=["literal-string", "hex-string", "name"],
)
def test_max_token_bytes_bound_refused(data):
    err = _refusal(data)
    assert err.offset == 0
    assert err.expected == f"token of at most {MAX_TOKEN_BYTES} bytes"
    assert err.found == "oversized token"


# ------------------------------------------------------- refusal payloads


def test_refusal_payload_for_composite_delimiter():
    err = _refusal(b"  <<")
    assert err.to_payload() == {
        "reject_code": "pdf_syntax_error",
        "offset": 2,
        "expected": "primitive token",
        "found": "<<",
    }


def test_refusal_payload_for_unterminated_literal_string():
    err = _refusal(b"(x")
    assert err.to_payload() == {
        "reject_code": "pdf_syntax_error",
        "offset": 0,
        "expected": "')'",
        "found": "end of data",
    }


def test_reject_code_is_stable_class_attribute():
    assert PdfSyntaxError.reject_code == "pdf_syntax_error"
    assert _refusal(b"").reject_code == "pdf_syntax_error"
