"""Tests for the strict fail-closed content-stream interpreter (SB-S1 part 5).

M2-T015 unit 3i-3b-tests. The module under test is read-only for this unit;
every expected number below is hand-computed from the documented
translate+scale model in ``app.documents.extraction.pdf_content``.
"""

from __future__ import annotations

import pytest

import app.documents.extraction.pdf_content as pdf_content
from app.documents.extraction.pdf_content import (
    PageContent,
    TextRun,
    VectorRect,
    VectorSegment,
    interpret_content,
)
from app.documents.extraction.pdf_lexer import PdfSyntaxError
from app.documents.extraction.pdf_xref import UnsupportedPdfFeature


def _ok(content: bytes) -> PageContent:
    result = interpret_content(content)
    assert isinstance(result, PageContent), f"expected PageContent, got {result!r}"
    return result


def _syntax_error(content: bytes) -> PdfSyntaxError:
    result = interpret_content(content)
    assert isinstance(result, PdfSyntaxError), f"expected PdfSyntaxError, got {result!r}"
    return result


def _unsupported(content: bytes) -> UnsupportedPdfFeature:
    result = interpret_content(content)
    assert isinstance(
        result, UnsupportedPdfFeature
    ), f"expected UnsupportedPdfFeature, got {result!r}"
    return result


# -- path geometry ---------------------------------------------------------


def test_empty_content_yields_empty_page():
    assert interpret_content(b"") == PageContent((), (), ())


def test_comments_and_whitespace_skipped():
    page = _ok(b"% setup\r\n 0 0 m 1 0 l S % done")
    assert page.segments == (VectorSegment(0.0, 0.0, 1.0, 0.0),)


def test_rectangle_m_l_l_l_h_stroke_emits_four_segments_closing_to_start():
    page = _ok(b"0 0 m 10 0 l 10 5 l 0 5 l h S")
    assert page.rects == ()
    assert page.text_runs == ()
    assert page.segments == (
        VectorSegment(0.0, 0.0, 10.0, 0.0),
        VectorSegment(10.0, 0.0, 10.0, 5.0),
        VectorSegment(10.0, 5.0, 0.0, 5.0),
        VectorSegment(0.0, 5.0, 0.0, 0.0),
    )


def test_re_emits_vector_rect():
    page = _ok(b"2 3 10 20 re f")
    assert page.segments == ()
    assert page.rects == (VectorRect(2.0, 3.0, 10.0, 20.0),)


def test_multiple_subpaths_under_one_paint():
    page = _ok(b"0 0 m 1 0 l 5 5 m 6 5 l S")
    assert page.segments == (
        VectorSegment(0.0, 0.0, 1.0, 0.0),
        VectorSegment(5.0, 5.0, 6.0, 5.0),
    )


_OPEN_TRIANGLE = b"0 0 m 4 0 l 4 3 l "


@pytest.mark.parametrize("op", [b"S", b"f", b"F", b"f*", b"B", b"B*", b"n"])
def test_non_closing_painting_operators_equivalent_geometry(op):
    page = _ok(_OPEN_TRIANGLE + op)
    assert page.segments == (
        VectorSegment(0.0, 0.0, 4.0, 0.0),
        VectorSegment(4.0, 0.0, 4.0, 3.0),
    )


@pytest.mark.parametrize("op", [b"s", b"b", b"b*"])
def test_closing_painting_operators_imply_h(op):
    page = _ok(_OPEN_TRIANGLE + op)
    assert page.segments == (
        VectorSegment(0.0, 0.0, 4.0, 0.0),
        VectorSegment(4.0, 0.0, 4.0, 3.0),
        VectorSegment(4.0, 3.0, 0.0, 0.0),
    )


# -- transforms ------------------------------------------------------------


def test_cm_translate_scale_transforms_segments_and_rects():
    page = _ok(b"2 0 0 3 10 20 cm 1 1 m 2 4 l S 1 1 4 5 re f")
    assert page.segments == (VectorSegment(12.0, 23.0, 14.0, 32.0),)
    assert page.rects == (VectorRect(12.0, 23.0, 8.0, 15.0),)


def test_nested_q_Q_restores_ctm():
    page = _ok(
        b"q 2 0 0 2 0 0 cm "
        b"q 1 0 0 1 5 5 cm 0 0 m 1 0 l S Q "
        b"0 0 m 1 0 l S Q "
        b"0 0 m 1 0 l S"
    )
    assert page.segments == (
        VectorSegment(10.0, 10.0, 12.0, 10.0),
        VectorSegment(0.0, 0.0, 2.0, 0.0),
        VectorSegment(0.0, 0.0, 1.0, 0.0),
    )


def test_q_depth_at_bound_succeeds():
    depth = pdf_content.MAX_Q_DEPTH
    assert interpret_content(b"q " * depth + b"Q " * depth) == PageContent((), (), ())


def test_q_depth_beyond_bound_refused():
    err = _unsupported(b"q " * (pdf_content.MAX_Q_DEPTH + 1))
    assert err.feature == "MAX_Q_DEPTH"


def test_Q_without_q_refused():
    err = _syntax_error(b"Q")
    assert err.expected == "a matching q before Q"
    assert err.found == "Q with no saved graphics state"


def test_unrestored_q_at_end_refused():
    err = _syntax_error(b"q")
    assert err.expected == "Q restoring every saved graphics state"
    assert err.found == "end of content with 1 unrestored q save(s)"


def test_rotated_cm_refused():
    err = _unsupported(b"0 1 -1 0 0 0 cm")
    assert err.feature == "rotated/sheared graphics"


# -- text ------------------------------------------------------------------


def test_BT_Tf_Td_Tj_emits_text_run_at_exact_position_and_size():
    page = _ok(b"BT /F1 12 Tf 100 200 Td (25.50') Tj ET")
    assert page.text_runs == (TextRun("25.50'", 100.0, 200.0, 12.0),)


def test_TD_sets_leading_and_T_star_advances():
    page = _ok(b"BT /F1 10 Tf 72 720 Td (A) Tj 0 -14 TD (B) Tj T* (C) Tj ET")
    assert page.text_runs == (
        TextRun("A", 72.0, 720.0, 10.0),
        TextRun("B", 72.0, 706.0, 10.0),
        TextRun("C", 72.0, 692.0, 10.0),
    )


def test_Tm_scale_affects_font_size_and_positions():
    page = _ok(b"BT /F1 10 Tf 2 0 0 3 50 60 Tm (X) Tj 5 7 Td (Y) Tj ET")
    assert page.text_runs == (
        TextRun("X", 50.0, 60.0, 30.0),
        TextRun("Y", 60.0, 81.0, 30.0),
    )


def test_cm_transforms_text_position_but_not_font_size():
    page = _ok(b"2 0 0 2 10 20 cm BT /F1 12 Tf 5 5 Td (Z) Tj ET")
    assert page.text_runs == (TextRun("Z", 20.0, 30.0, 12.0),)


def test_TJ_concatenates_strings_ignoring_kerning_numbers():
    page = _ok(b"BT /F1 12 Tf [(25.) -120 (50) 30 (')] TJ ET")
    assert page.text_runs == (TextRun("25.50'", 0.0, 0.0, 12.0),)


def test_quote_operator_advances_line_then_shows():
    page = _ok(b"BT /F1 10 Tf 0 -12 TD (A) Tj (B) ' ET")
    assert page.text_runs == (
        TextRun("A", 0.0, -12.0, 10.0),
        TextRun("B", 0.0, -24.0, 10.0),
    )


def test_high_byte_decodes_via_latin1():
    page = _ok(b"BT /F1 8 Tf (45" + bytes([0xB0]) + b") Tj ET")
    assert page.text_runs == (TextRun("45°", 0.0, 0.0, 8.0),)


def test_sheared_Tm_refused():
    err = _unsupported(b"BT 1 0.5 0 1 0 0 Tm ET")
    assert err.feature == "rotated/sheared text"


def test_text_shown_without_font_refused():
    err = _syntax_error(b"BT (A) Tj ET")
    assert err.expected == "Tf setting a font before text is shown"
    assert err.found == "text shown with no font set"


def test_TJ_array_with_name_element_refused():
    err = _syntax_error(b"BT /F1 10 Tf [(A) /Bad] TJ ET")
    assert err.expected == "TJ array elements that are strings or kerning numbers"
    assert err.found == "element of type name"


# -- text-object structure refusals ---------------------------------------


@pytest.mark.parametrize(
    ("content", "word"),
    [
        (b"(A) Tj", "Tj"),
        (b"1 2 Td", "Td"),
        (b"1 0 0 1 0 0 Tm", "Tm"),
        (b"T*", "T*"),
        (b"(A) '", "'"),
    ],
)
def test_text_operators_outside_BT_refused(content, word):
    err = _syntax_error(content)
    assert err.expected == f"'{word}' inside a BT..ET text object"
    assert err.found == f"'{word}' outside BT..ET"


def test_nested_BT_refused():
    err = _syntax_error(b"BT BT")
    assert err.expected == "ET before another BT"
    assert err.found == "nested BT"


def test_ET_without_BT_refused():
    err = _syntax_error(b"ET")
    assert err.expected == "BT opening a text object before ET"
    assert err.found == "ET outside BT..ET"


def test_unclosed_BT_at_end_refused():
    err = _syntax_error(b"BT")
    assert err.expected == "ET closing the open text object"
    assert err.found == "end of content"


# -- unsupported-operator refusals ----------------------------------------


@pytest.mark.parametrize(
    ("content", "feature"),
    [
        (b"0 0 m 1 1 2 2 3 3 c", "content operator 'c'"),
        (b"0 0 m 1 1 2 2 v", "content operator 'v'"),
        (b"0 0 m 1 1 2 2 y", "content operator 'y'"),
        (b"/Img1 Do", "content operator 'Do'"),
        (b"BI", "content operator 'BI'"),
        (b"/Sh1 sh", "content operator 'sh'"),
        (b"frobnicate", "content operator 'frobnicate'"),
    ],
)
def test_unsupported_operators_refused(content, feature):
    err = _unsupported(content)
    assert err.feature == feature


# -- operand-shape refusals ------------------------------------------------


@pytest.mark.parametrize(
    ("content", "expected", "found"),
    [
        (b"1 m", "'m' with 2 operand(s): x y (numbers)", "1 operand(s)"),
        (b"0 0 m 1 l", "'l' with 2 operand(s): x y (numbers)", "1 operand(s)"),
        (b"1 2 3 re", "'re' with 4 operand(s): x y w h (numbers)", "3 operand(s)"),
        (
            b"1 0 0 1 5 cm",
            "'cm' with 6 operand(s): a b c d e f (numbers)",
            "5 operand(s)",
        ),
        (
            b"BT 1 0 0 1 0 Tm ET",
            "'Tm' with 6 operand(s): a b c d e f (numbers)",
            "5 operand(s)",
        ),
        (
            b"/F1 Tf",
            "'Tf' with 2 operand(s): font name and size (name, number)",
            "1 operand(s)",
        ),
    ],
)
def test_wrong_operand_counts_refused(content, expected, found):
    err = _syntax_error(content)
    assert err.expected == expected
    assert err.found == found


def test_wrong_operand_types_reported():
    err = _syntax_error(b"(a) (b) m")
    assert err.expected == "'m' with 2 operand(s): x y (numbers)"
    assert err.found == "operand types string, string"


def test_l_without_current_point_refused():
    err = _syntax_error(b"1 2 l")
    assert err.expected == "a current point ('m' or 're' before 'l')"
    assert err.found == "'l' with no current point"


def test_leftover_operands_at_end_refused():
    err = _syntax_error(b"1 2")
    assert err.expected == "an operator consuming the pending operands"
    assert err.found == "end of content with 2 unconsumed operand(s)"


def test_ignored_style_operators_consume_operands():
    page = _ok(b"0.5 g 1 0 0 RG 2 w [] 0 d")
    assert page == PageContent((), (), ())


# -- resource bounds (module globals read at call time) --------------------


def test_max_content_operators_bound(monkeypatch):
    monkeypatch.setattr(pdf_content, "MAX_CONTENT_OPERATORS", 4)
    assert isinstance(interpret_content(b"q Q q Q"), PageContent)
    err = _unsupported(b"q Q q Q q Q")
    assert err.feature == "MAX_CONTENT_OPERATORS"


def test_max_primitives_bound(monkeypatch):
    monkeypatch.setattr(pdf_content, "MAX_PRIMITIVES", 4)
    assert isinstance(interpret_content(b"1 2 3 4 re f"), PageContent)
    monkeypatch.setattr(pdf_content, "MAX_PRIMITIVES", 3)
    err = _unsupported(b"1 2 3 4 re f")
    assert err.feature == "MAX_PRIMITIVES"


def test_inline_array_elements_and_completed_array_each_count(monkeypatch):
    monkeypatch.setattr(pdf_content, "MAX_PRIMITIVES", 2)
    err = _unsupported(b"[(A) (B)]")
    assert err.feature == "MAX_PRIMITIVES"
