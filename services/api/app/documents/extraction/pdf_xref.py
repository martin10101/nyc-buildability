"""Fail-closed classic cross-reference-table reader (M2-T015 unit 3i-3a-3a).

Reads the single classic ``xref`` section named by the file's final
``startxref`` pointer, validates its trailer, and materialises every
in-use object the table lists. Pure function of ``bytes``: no I/O, no
globals mutated, no clock, no randomness. Never raises on any input;
every refusal is a VALUE — a ``PdfSyntaxError`` (the lexer's class,
reused verbatim) for malformed bytes, or an ``UnsupportedPdfFeature``
for well-formed constructs this strict subset deliberately does not
implement.

Strict-subset fail-closed doctrine:

* **Single authority.** The one classic xref section reached from the
  last ``startxref`` in the final ``STARTXREF_WINDOW_BYTES`` bytes is
  the ONLY object authority. ``/Prev`` chains are never followed and
  the file is never scanned for stray ``N G obj`` headers — repair by
  scanning is exactly the guessing this pipeline forbids. An object a
  consumer needs but the table does not list surfaces later as a
  missing dictionary key, deliberately.
* **Refuse, don't degrade.** PDF 1.5+ cross-reference streams, hybrid-
  reference files (``/XRefStm``), incremental-update chains (``/Prev``),
  and encryption (``/Encrypt``) are refused by name via
  ``UnsupportedPdfFeature``, never partially handled.
* **Identity is verified.** Every in-use entry's target is parsed with
  ``parse_indirect_object`` and its ``N G`` header must equal the xref
  entry's object number and generation; a lying offset is refused, not
  tolerated.
* **Everything is bounded.** At most ``MAX_PDF_OBJECTS`` in-use entries
  are materialised; integers read here are capped at 10 digits (the
  classic xref offset width, and far below CPython's str→int digit
  limit, so ``int()`` can never raise); per-entry structure is exactly
  the 20-byte §7.5.4 layout.

Grammar implemented (ISO 32000-1 §7.5.4–§7.5.5):

* ``startxref`` — last occurrence within the final 1024 bytes, followed
  by a non-negative integer byte offset and then ``%%EOF``.
* ``xref`` — one or more subsections, each a ``start count`` header
  line followed by exactly ``count`` 20-byte entries
  ``nnnnnnnnnn ggggg n/f`` whose trailing two bytes are SP CR, SP LF,
  or CR LF. Line ends elsewhere tolerate ``\\r\\n``, ``\\r``, or
  ``\\n``. Free (``f``) entries are recorded nowhere; a repeated object
  number or an in-use object number 0 is refused (per ``pdf_objects``,
  positivity of in-use object numbers is this layer's rule).
* ``trailer`` — a dictionary parsed with ``parse_object``; ``/Size``
  must be a positive direct integer and ``/Root`` an indirect
  reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .pdf_lexer import PdfName, PdfSyntaxError
from .pdf_objects import (
    PdfIndirectObject,
    PdfRef,
    parse_indirect_object,
    parse_object,
)

__all__ = [
    "MAX_PDF_OBJECTS",
    "PdfObjectTable",
    "STARTXREF_WINDOW_BYTES",
    "UnsupportedPdfFeature",
    "read_object_table",
]

MAX_PDF_OBJECTS = 4096
STARTXREF_WINDOW_BYTES = 1024

_XREF_ENTRY_BYTES = 20
_MAX_UINT_DIGITS = 10
_MAX_DISPLAY_CHARS = 64
_FOUND_PREVIEW_BYTES = 16

# Kept byte-for-byte identical to pdf_lexer's classification sets (§7.2.3).
_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")
_DIGITS = frozenset(b"0123456789")

_ENTRY_EOL_FORMS = (b" \r", b" \n", b"\r\n")

_SIZE_KEY = PdfName("Size")
_ROOT_KEY = PdfName("Root")
_PREV_KEY = PdfName("Prev")
_XREFSTM_KEY = PdfName("XRefStm")
_ENCRYPT_KEY = PdfName("Encrypt")


@dataclass(frozen=True)
class UnsupportedPdfFeature:
    """A well-formed PDF construct outside the strict subset; refused by name."""

    feature: str
    detail: str

    reject_code: ClassVar[str] = "unsupported_pdf_feature"

    def to_payload(self) -> dict:
        return {
            "reject_code": self.reject_code,
            "feature": self.feature,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class PdfObjectTable:
    """The trailer dictionary plus every in-use object the xref section lists.

    ``objects`` maps ``(object_number, generation)`` to the parsed object
    VALUE (the body inside ``N G obj ... endobj``, not the wrapper).
    """

    trailer: dict
    objects: dict


def read_object_table(
    data: bytes,
) -> PdfObjectTable | UnsupportedPdfFeature | PdfSyntaxError:
    """Read the single classic xref section, its trailer, and all in-use objects.

    Never raises; refusals are ``PdfSyntaxError`` or
    ``UnsupportedPdfFeature`` values as described in the module
    docstring.
    """
    if not data.startswith(b"%PDF-1."):
        return PdfSyntaxError(0, "'%PDF-1.' header", _display_at(data, 0))

    located = _locate_startxref(data)
    if isinstance(located, PdfSyntaxError):
        return located
    xref_offset = located

    keyword_end = _keyword_end(data, xref_offset, b"xref")
    if keyword_end is None:
        if xref_offset < len(data) and data[xref_offset] in _DIGITS:
            return UnsupportedPdfFeature(
                "cross-reference stream",
                f"startxref offset {xref_offset} begins with an integer object"
                " header (a PDF 1.5+ cross-reference stream); only classic"
                " 'xref' tables are in the supported subset",
            )
        return PdfSyntaxError(
            xref_offset,
            "'xref' keyword at startxref offset",
            _display_at(data, xref_offset),
        )

    section = _read_xref_section(data, keyword_end)
    if isinstance(section, PdfSyntaxError):
        return section
    in_use_entries, trailer_keyword_end = section

    trailer_pos = _skip_whitespace(data, trailer_keyword_end)
    parsed_trailer = parse_object(data, trailer_keyword_end)
    if isinstance(parsed_trailer, PdfSyntaxError):
        return parsed_trailer
    trailer = parsed_trailer.value
    if not isinstance(trailer, dict):
        return PdfSyntaxError(
            trailer_pos, "trailer dictionary", _display_at(data, trailer_pos)
        )

    size = trailer.get(_SIZE_KEY)
    if type(size) is not int or size <= 0:  # bool is excluded: type(), not isinstance()
        return PdfSyntaxError(
            trailer_pos,
            "/Size positive integer in trailer",
            "absent" if _SIZE_KEY not in trailer else _display_text(repr(size)),
        )
    root = trailer.get(_ROOT_KEY)
    if not isinstance(root, PdfRef):
        return PdfSyntaxError(
            trailer_pos,
            "/Root indirect reference in trailer",
            "absent" if _ROOT_KEY not in trailer else _display_text(repr(root)),
        )
    if _PREV_KEY in trailer:
        return UnsupportedPdfFeature(
            "incremental update chain",
            "trailer /Prev names an earlier cross-reference section; this"
            " reader trusts exactly one xref section and never follows"
            " update chains",
        )
    if _XREFSTM_KEY in trailer:
        return UnsupportedPdfFeature(
            "hybrid-reference file",
            "trailer /XRefStm names a cross-reference stream alongside the"
            " classic table; hybrid-reference files are outside the"
            " supported subset",
        )
    if _ENCRYPT_KEY in trailer:
        return UnsupportedPdfFeature(
            "encryption",
            "trailer /Encrypt is present; encrypted documents are refused,"
            " never decrypted",
        )

    if len(in_use_entries) > MAX_PDF_OBJECTS:
        return UnsupportedPdfFeature(
            "object count bound",
            f"xref lists {len(in_use_entries)} in-use objects, above"
            f" MAX_PDF_OBJECTS={MAX_PDF_OBJECTS}",
        )

    objects: dict[tuple[int, int], object] = {}
    for number, generation, object_offset in in_use_entries:
        parsed = parse_indirect_object(data, object_offset)
        if isinstance(parsed, PdfSyntaxError):
            return parsed
        indirect = parsed.value
        if not isinstance(indirect, PdfIndirectObject):
            # parse_indirect_object's contract guarantees the wrapper; stay total anyway
            return PdfSyntaxError(
                object_offset,
                "indirect object wrapper",
                _display_text(repr(indirect)),
            )
        if (indirect.number, indirect.generation) != (number, generation):
            return PdfSyntaxError(
                object_offset,
                f"object {number} {generation} at its xref-recorded offset"
                " (xref/object identity mismatch)",
                f"object {indirect.number} {indirect.generation}",
            )
        objects[(number, generation)] = indirect.value
    return PdfObjectTable(trailer=trailer, objects=objects)


def _locate_startxref(data: bytes) -> int | PdfSyntaxError:
    """Return the byte offset named by the last ``startxref`` in the final window."""
    window_start = max(0, len(data) - STARTXREF_WINDOW_BYTES)
    found = data.rfind(b"startxref", window_start)
    if found == -1:
        return PdfSyntaxError(
            len(data),
            f"'startxref' in the final {STARTXREF_WINDOW_BYTES} bytes",
            "absent",
        )
    pos = _skip_whitespace(data, found + len(b"startxref"))
    number = _read_uint(data, pos)
    if number is None:
        return PdfSyntaxError(
            pos, "non-negative integer startxref offset", _display_at(data, pos)
        )
    offset, end = number
    eof_pos = _skip_whitespace(data, end)
    if data[eof_pos : eof_pos + 5] != b"%%EOF":
        return PdfSyntaxError(
            eof_pos, "'%%EOF' after startxref offset", _display_at(data, eof_pos)
        )
    return offset


def _read_xref_section(
    data: bytes, pos: int
) -> tuple[list[tuple[int, int, int]], int] | PdfSyntaxError:
    """Read subsections until ``trailer``; return in-use entries and the post-keyword offset.

    Each returned entry is ``(object_number, generation, byte_offset)``.
    Free entries are recorded nowhere.
    """
    in_use: list[tuple[int, int, int]] = []
    seen_numbers: set[int] = set()
    while True:
        pos = _skip_whitespace(data, pos)
        if pos >= len(data):
            return PdfSyntaxError(
                pos, "xref subsection header or 'trailer'", "end of data"
            )
        trailer_end = _keyword_end(data, pos, b"trailer")
        if trailer_end is not None:
            return (in_use, trailer_end)
        header = _read_subsection_header(data, pos)
        if isinstance(header, PdfSyntaxError):
            return header
        first_number, count, pos = header
        for index in range(count):
            entry = _parse_entry(data[pos : pos + _XREF_ENTRY_BYTES], pos)
            if isinstance(entry, PdfSyntaxError):
                return entry
            object_offset, generation, entry_in_use = entry
            number = first_number + index
            if number in seen_numbers:
                return PdfSyntaxError(
                    pos,
                    "unique object number per xref section",
                    f"object {number} listed twice",
                )
            seen_numbers.add(number)
            if entry_in_use:
                if number == 0:
                    return PdfSyntaxError(
                        pos,
                        "positive object number for in-use xref entry",
                        "object 0 marked 'n'",
                    )
                in_use.append((number, generation, object_offset))
            pos += _XREF_ENTRY_BYTES


def _read_subsection_header(
    data: bytes, pos: int
) -> tuple[int, int, int] | PdfSyntaxError:
    """Parse a ``start count`` header line; return (start, count, entries_offset)."""
    first = _read_uint(data, pos)
    if first is None:
        return PdfSyntaxError(
            pos,
            "xref subsection 'start count' line or 'trailer'",
            _display_at(data, pos),
        )
    start_value, cursor = first
    space_run = cursor
    while cursor < len(data) and data[cursor] == 0x20:
        cursor += 1
    if cursor == space_run:
        return PdfSyntaxError(
            cursor, "space between subsection start and count", _display_at(data, cursor)
        )
    second = _read_uint(data, cursor)
    if second is None:
        return PdfSyntaxError(
            cursor, "subsection entry count", _display_at(data, cursor)
        )
    count_value, cursor = second
    while cursor < len(data) and data[cursor] == 0x20:
        cursor += 1
    if data[cursor : cursor + 2] == b"\r\n":
        cursor += 2
    elif data[cursor : cursor + 1] in (b"\r", b"\n"):
        cursor += 1
    else:
        return PdfSyntaxError(
            cursor, "line end after subsection header", _display_at(data, cursor)
        )
    return (start_value, count_value, cursor)


def _parse_entry(
    raw: bytes, pos: int
) -> tuple[int, int, bool] | PdfSyntaxError:
    """Validate one exactly-20-byte §7.5.4 entry; return (offset, generation, in_use)."""
    if len(raw) < _XREF_ENTRY_BYTES:
        return PdfSyntaxError(pos, "20-byte xref entry", "end of data")
    if not (
        raw[0:10].isdigit()
        and raw[10] == 0x20
        and raw[11:16].isdigit()
        and raw[16] == 0x20
        and raw[17] in b"nf"
        and raw[18:20] in _ENTRY_EOL_FORMS
    ):
        return PdfSyntaxError(
            pos,
            "'nnnnnnnnnn ggggg n/f' 20-byte xref entry",
            _display_text(raw.decode("latin-1")),
        )
    return (int(raw[0:10]), int(raw[11:16]), raw[17:18] == b"n")


def _read_uint(data: bytes, pos: int) -> tuple[int, int] | None:
    """Read a run of at most 10 ASCII digits at ``pos``; None if absent or oversized."""
    end = pos
    while end < len(data) and data[end] in _DIGITS:
        end += 1
    if end == pos or end - pos > _MAX_UINT_DIGITS:
        return None
    return (int(data[pos:end]), end)


def _skip_whitespace(data: bytes, offset: int) -> int:
    n = len(data)
    pos = offset
    while pos < n and data[pos] in _WHITESPACE:
        pos += 1
    return pos


def _keyword_end(data: bytes, pos: int, keyword: bytes) -> int | None:
    """Return the offset past ``keyword`` at ``pos`` (on a token boundary), else None."""
    end = pos + len(keyword)
    if data[pos:end] != keyword:
        return None
    if end < len(data) and data[end] not in _WHITESPACE and data[end] not in _DELIMITERS:
        return None
    return end


def _display_text(text: str) -> str:
    printable = "".join(
        ch if " " <= ch <= "~" else f"\\x{ord(ch):02x}" for ch in text
    )
    if len(printable) > _MAX_DISPLAY_CHARS:
        return printable[: _MAX_DISPLAY_CHARS - 3] + "..."
    return printable


def _display_at(data: bytes, pos: int) -> str:
    if pos >= len(data):
        return "end of data"
    preview = data[pos : pos + _FOUND_PREVIEW_BYTES].decode("latin-1")
    return _display_text(preview)
