"""Acceptance + mutation tests for the M5-T120 P4 reader features (D-087 PDF-4; DB-090 a/c/i):

* AS-1 (split): the path-state group moved to :mod:`app.drawings.sheet_path_state` behind the
  unchanged ``_StreamRun`` interface. The byte-identical proof is the unchanged goldens +
  ``test_sheet_reader_split_equivalence.py``; here the SPLIT-FACADE positive controls prove the
  moved constants' mutation seam still bites at the NEW consuming namespace (``sheet_path_state``),
  so a post-split monkeypatch is not silently vacuous (the seq-130 facade trap).
* AS-2 (/DP dictionaries, DB-090 a): an inline image whose /DP (or /DecodeParms) value is a
  dictionary — or an array of dictionaries / nulls — is SKIPPED like any other inline image (one
  nested level, that key only, same byte cap, samples never decoded); the linework after it still
  draws. A nested dictionary under any OTHER key, and a SECOND nesting level, stay typed refusals.
* AS-4 (orphan lineto, DB-090 i): an ``l`` with no current point after a paint starts a NEW subpath
  AT ITS OWN end point (no segment from the undefined pre-paint point), counted per page; an orphan
  curve (``c``/``v``/``y``) STAYS a typed refusal.

Each new guard has a committed consuming-namespace mutation that flips the assertion
(reopen-at-last-point, drop-the-count, allow-any-nested-dict, disallow-dp-dict, raise-the-cap); the
explicit red/green mutant runs are recorded in the M5-T120 producer report. Synthetic fixtures
only; no network. Citations (AS-3) are a doc-only change verified by inspection / the G1 review;
the real six-file corpus (AS-5) is run out of tree and reported, not committed.
"""

from __future__ import annotations

import pytest

from app.drawings import (
    sheet_inline_image,
    sheet_interpreter,
    sheet_path_state,
)
from app.drawings.sheet_primitives import SheetDocument, SheetRefusal
from app.drawings.sheet_reader import read_sheet, sheet_refusal


# --------------------------------------------------------------------------- PDF byte builders
def _pdf(objects: list[bytes], root: bytes = b"1 0 R") -> bytes:
    out = bytearray(b"%PDF-1.7\n")
    offsets: list[int] = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % index + body + b"\nendobj\n"
    xref_offset = len(out)
    size = len(objects) + 1
    out += b"xref\n0 %d\n" % size + b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (size, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _stream(data: bytes) -> bytes:
    return b"<< /Length %d >>\nstream\n%s\nendstream" % (len(data), data)


def _one_page(content: bytes) -> bytes:
    return _pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 800 600] /Contents 4 0 R >>",
        _stream(content),
    ])


def _inline(dict_part: bytes, data: bytes) -> bytes:
    """A ``BI <dict> ID <data> EI`` inline image (a single whitespace after ID per §8.9.7)."""
    return b"BI " + dict_part + b" ID " + data + b" EI"


def _flat(points) -> list[float]:
    return [coord for point in points for coord in point]


# ================================================================= AS-4 orphan lineto (DB-090 i)
def test_as4_orphan_lineto_after_paint_opens_own_subpath():
    """After a paint the current point is UNDEFINED (§8.5.3); an ``l`` with no current point starts
    a new subpath AT ITS OWN point — no segment from the pre-paint (5,5) — later ``l`` draw from it.
    The pre-paint line stays (0,0)->(5,5); the orphan subpath is exactly (10,10)->(20,20)."""
    doc = read_sheet(_one_page(b"0 0 m 5 5 l S 10 10 l 20 20 l S"))
    assert isinstance(doc, SheetDocument)
    page = doc.pages[0]
    assert len(page.polylines) == 2
    assert _flat(page.polylines[0].points) == pytest.approx([0.0, 0.0, 5.0, 5.0])
    # the orphan subpath begins AT (10,10) — NOT a segment from the pre-paint point (5,5)
    assert _flat(page.polylines[1].points) == pytest.approx([10.0, 10.0, 20.0, 20.0])
    assert page.orphan_subpaths == 1
    assert doc.orphan_subpaths == 1


def test_as4_orphan_lineto_at_stream_start_opens_own_subpath():
    """No current point at stream start (no preceding ``m``) is the same case: the first ``l`` opens
    a subpath at its own point (counted once), and the next ``l`` continues it from there, so the
    subpath is exactly (5,5)->(6,6) — a read, never a refusal."""
    doc = read_sheet(_one_page(b"5 5 l 6 6 l S"))
    assert isinstance(doc, SheetDocument)
    page = doc.pages[0]
    assert _flat(page.polylines[0].points) == pytest.approx([5.0, 5.0, 6.0, 6.0])
    assert page.orphan_subpaths == 1


def test_as4_orphan_lineto_no_segment_from_pre_paint_point_mutant(monkeypatch):
    """MUTANT 'reopen-at-last-point': a ``_paint`` that leaves the current point DEFINED (violating
    §8.5.3) makes the next ``l`` reopen at the stale pre-paint point (5,5), INVENTING a segment.
    REAL begins the orphan subpath at (10,10); the mutant begins it at (5,5)."""
    pdf = _one_page(b"0 0 m 5 5 l S 10 10 l 20 20 l S")
    real = read_sheet(pdf)
    assert isinstance(real, SheetDocument)
    assert _flat(real.pages[0].polylines[1].points) == pytest.approx([10.0, 10.0, 20.0, 20.0])

    real_paint = sheet_path_state._PathState._paint

    def _paint_keep_current(self, word):
        saved = self._current
        real_paint(self, word)
        self._current = saved  # MUTANT: current point NOT undefined after painting (§8.5.3)

    monkeypatch.setattr(sheet_interpreter._StreamRun, "_paint", _paint_keep_current)
    mutant = read_sheet(pdf)
    assert isinstance(mutant, SheetDocument)
    # the invented segment: the orphan subpath now begins at the stale pre-paint point (5,5)
    assert _flat(mutant.pages[0].polylines[1].points) == pytest.approx(
        [5.0, 5.0, 10.0, 10.0, 20.0, 20.0]
    )


def test_as4_orphan_subpath_count_is_load_bearing(monkeypatch):
    """MUTANT 'drop-the-count': an ``_orphan_lineto`` that opens the subpath but does not increment
    the count leaves the geometry identical yet drops the disclosure. REAL count 1, mutant count
    0."""
    pdf = _one_page(b"0 0 m 5 5 l S 10 10 l 20 20 l S")
    assert read_sheet(pdf).pages[0].orphan_subpaths == 1

    def _no_count(self, x, y):
        point = self._map(x, y)
        if isinstance(point, SheetRefusal):
            return point
        self._cur_points = [point]
        self._current = point
        self._subpath_start = point
        return self._charge_points(1)  # MUTANT: drops both count increments

    monkeypatch.setattr(sheet_interpreter._StreamRun, "_orphan_lineto", _no_count)
    mutant = read_sheet(pdf)
    assert isinstance(mutant, SheetDocument)
    assert mutant.pages[0].orphan_subpaths == 0            # geometry unchanged, count dropped
    assert _flat(mutant.pages[0].polylines[1].points) == pytest.approx([10.0, 10.0, 20.0, 20.0])


@pytest.mark.parametrize(
    "curve",
    [b"10 10 20 20 30 30 c", b"10 10 20 20 v", b"10 10 20 20 y"],
)
def test_as4_orphan_curve_still_refuses(curve):
    """Curves (``c``/``v``/``y``) with no current point STAY a typed refusal (this packet does not
    lenient-reopen curves — that would need a defined start tangent)."""
    ref = sheet_refusal(read_sheet(_one_page(b"0 0 m 5 5 l S " + curve + b" S")))
    assert ref is not None
    assert ref.feature in ("path", "v")
    assert "current point" in ref.detail


# =========================================================== AS-2 /DP dictionaries (DB-090 a)
def test_as2_dp_dictionary_inline_image_skipped_line_after_draws():
    """A filtered inline image whose /DP value is a decode-parameters DICTIONARY is skipped (the /F
    forces the EI scan; the /DP dict is consumed for balance only); the line after still draws."""
    img = _inline(
        b"/W 2 /H 2 /CS /G /F /Fl /DP << /Predictor 12 /Columns 2 >>", bytes([0x9C, 0x01])
    )
    doc = read_sheet(_one_page(b"q " + img + b" Q 0 0 m 10 10 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([0.0, 0.0, 10.0, 10.0])


def test_as2_dp_decodeparms_full_name_dictionary_skipped():
    """The full key name /DecodeParms (not just /DP) also carries the dictionary value."""
    img = _inline(
        b"/W 2 /H 2 /CS /G /F /Fl /DecodeParms << /Predictor 12 /Columns 2 >>", bytes([0x9C, 0x01])
    )
    doc = read_sheet(_one_page(img + b" 0 0 m 1 1 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1 and len(doc.pages[0].polylines) == 1


def test_as2_dp_array_of_dictionaries_and_nulls_skipped():
    """An /DP whose value is an ARRAY of decode-parameter dictionaries / nulls (one per filter) is
    parsed for balance and skipped; the line after draws."""
    img = _inline(
        b"/W 2 /H 2 /CS /G /F [/Fl] /DP [ << /Predictor 12 /Columns 2 >> null ]",
        bytes([0x9C, 0x01]),
    )
    doc = read_sheet(_one_page(b"q " + img + b" Q 5 5 m 6 6 l S"))
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1
    assert _flat(doc.pages[0].polylines[0].points) == pytest.approx([5.0, 5.0, 6.0, 6.0])


def test_as2_dp_dictionary_skip_is_load_bearing(monkeypatch):
    """REAL: the /DP-dictionary image is skipped and the document reads. MUTANT 'disallow-dp-dict':
    no key may carry a nested dictionary, so the /DP dict is refused and the whole document refuses,
    proving the new dictionary acceptance (not a silent drop) is what lets it read."""
    img = _inline(
        b"/W 2 /H 2 /CS /G /F /Fl /DP << /Predictor 12 /Columns 2 >>", bytes([0x9C, 0x01])
    )
    pdf = _one_page(b"q " + img + b" Q 0 0 m 10 10 l S")
    assert isinstance(read_sheet(pdf), SheetDocument)

    monkeypatch.setattr(sheet_inline_image, "_nested_dict_allowed", lambda key: False)
    ref = sheet_refusal(read_sheet(pdf))
    assert ref is not None and ref.feature == "inline image"


def test_as2_non_dp_nested_dictionary_refuses():
    """A nested dictionary under any key OTHER than /DP // /DecodeParms is a typed refusal (only the
    decode-parameters keys carry a dictionary value; every other value stays a scalar/array)."""
    img = _inline(b"/W 2 /H 2 /CS << /Foo 1 >> /BPC 8", bytes([1, 2, 3, 4]))
    ref = sheet_refusal(read_sheet(_one_page(b"q " + img + b" Q")))
    assert ref is not None and ref.feature == "inline image"


def test_as2_non_dp_nested_dictionary_restriction_is_load_bearing(monkeypatch):
    """REAL: a nested dictionary under /CS refuses. MUTANT 'allow-any-nested-dict': every key may
    carry a nested dictionary, so /CS << >> is now accepted and skipped — proving the /DP-only
    restriction is load-bearing (not merely that dicts parse)."""
    img = _inline(b"/W 2 /H 2 /CS << /Foo 1 >> /F /Fl", bytes([0x9C, 0x01]))
    pdf = _one_page(b"q " + img + b" Q 0 0 m 10 10 l S")
    assert isinstance(read_sheet(pdf), SheetRefusal)

    monkeypatch.setattr(sheet_inline_image, "_nested_dict_allowed", lambda key: True)
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1


def test_as2_second_nesting_level_refuses():
    """Exactly ONE nested dictionary level: a dictionary INSIDE the /DP dictionary (a second
    level) is a typed refusal."""
    img = _inline(b"/W 2 /H 2 /CS /G /F /Fl /DP << /X << /Y 1 >> >>", bytes([0x9C, 0x01]))
    ref = sheet_refusal(read_sheet(_one_page(b"q " + img + b" Q")))
    assert ref is not None and ref.feature == "inline image"


def test_as2_one_level_depth_cap_is_load_bearing(monkeypatch):
    """REAL: a second dictionary level inside /DP refuses. MUTANT 'raise-the-depth-cap': allowing
    two levels accepts and skips it — proving the one-level cap is load-bearing."""
    img = _inline(b"/W 2 /H 2 /CS /G /F /Fl /DP << /X << /Y 1 >> >>", bytes([0x9C, 0x01]))
    pdf = _one_page(b"q " + img + b" Q 0 0 m 10 10 l S")
    assert isinstance(read_sheet(pdf), SheetRefusal)

    monkeypatch.setattr(sheet_inline_image, "_MAX_INLINE_DP_DICT_DEPTH", 2)
    doc = read_sheet(pdf)
    assert isinstance(doc, SheetDocument)
    assert doc.pages[0].inline_image_skips == 1


# ============================================ AS-1 split-facade positive controls (seq-130 trap)
def test_split_paint_flag_sets_bite_at_new_namespace(monkeypatch):
    """The stroke/fill/close-first sets moved to :mod:`app.drawings.sheet_path_state` with
    ``_paint``. Emptying each at the NEW namespace flips exactly its facet — proving a post-split
    monkeypatch of these constants is not silently vacuous (patch the CONSUMING namespace)."""
    stroked = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l S")).pages[0].polylines[0]
    assert stroked.stroked and not stroked.filled and not stroked.closed
    monkeypatch.setattr(sheet_path_state, "_PAINT_STROKE", frozenset())
    assert not read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l S")).pages[0].polylines[0].stroked
    monkeypatch.undo()

    filled = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l f")).pages[0].polylines[0]
    assert filled.filled
    monkeypatch.setattr(sheet_path_state, "_PAINT_FILL", frozenset())
    assert not read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l f")).pages[0].polylines[0].filled
    monkeypatch.undo()

    closed = read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l b")).pages[0].polylines[0]
    assert closed.closed
    monkeypatch.setattr(sheet_path_state, "_PAINT_CLOSE_FIRST", frozenset())
    assert not read_sheet(_one_page(b"0 0 m 10 0 l 10 10 l b")).pages[0].polylines[0].closed


def test_split_path_handlers_bite_at_new_namespace(monkeypatch):
    """``_PATH_HANDLERS`` moved to sheet_path_state; ``_execute`` reads it as a sheet_interpreter
    global (imported). Emptying it there makes ``m``/``l`` unsupported — proving the dispatch
    table's monkeypatch seam still bites through the facade after the split."""
    assert isinstance(read_sheet(_one_page(b"0 0 m 10 10 l S")), SheetDocument)
    monkeypatch.setattr(sheet_interpreter, "_PATH_HANDLERS", {})
    ref = sheet_refusal(read_sheet(_one_page(b"0 0 m 10 10 l S")))
    assert ref is not None and ref.feature == "unsupported operator"
