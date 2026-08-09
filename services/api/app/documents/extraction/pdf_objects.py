"""Fail-closed PDF composite-object parser (M2-T015 unit 3i-3a-2).

Parses exactly ONE complete PDF object — primitive, array, dictionary,
stream, or indirect reference — from a byte buffer at a caller-supplied
offset, building on the primitive lexer (``pdf_lexer``). Pure function
of ``bytes``: no I/O, no globals, no clock, no randomness. Never raises
on any input; every refusal is a ``PdfSyntaxError`` VALUE (the lexer's
class, reused verbatim). Nothing here guesses, repairs, or coerces
suspect input into a usable value.

Grammar implemented (ISO 32000-1):

* Arrays ``[ ... ]`` (§7.3.6) — heterogeneous, nested objects allowed.
* Dictionaries ``<< ... >>`` (§7.3.7) — keys MUST be name tokens; a
  non-name key or a duplicate key is refused (the spec calls duplicate
  keys undefined behaviour; undefined means refuse here). Keys are
  stored as ``PdfName`` instances (hashable frozen dataclass), so key
  equality follows the spec's post-``#xx``-decoding name identity.
  ``null`` entries are preserved as ``None`` rather than dropped — the
  §7.3.7 null-equals-absent equivalence is a semantic rule for
  consumers, not a licence for the parser to discard input.
* Indirect references ``N G R`` (§7.3.10) — disambiguated by lookahead:
  two integer tokens followed by the bare keyword ``R`` collapse to
  ``PdfRef``; otherwise the integers stand alone as ordinary objects.
  A matched reference pattern with a negative integer is refused
  (object and generation numbers are non-negative).
* Streams (§7.3.8) — a dictionary followed by the keyword ``stream``
  becomes ``PdfStream``. The spec requires streams to be indirect-
  object values, so stream recognition applies only where the
  dictionary is the WHOLE object being parsed (the top level of
  ``parse_object`` — which is exactly where ``parse_indirect_object``
  parses its body); a ``stream`` keyword anywhere else is refused.
  ``/Length`` must be a DIRECT non-negative integer: an indirect
  ``/Length`` would require cross-reference resolution this pure
  parser does not have, and guessing the extent of attacker-controlled
  bytes is exactly what fail-closed forbids. After the ``stream``
  keyword the spec allows CRLF or LF only (never CR alone); exactly
  ``/Length`` bytes are consumed as ``raw_data`` — UNDECODED. Filter
  decoding belongs to the container unit, not here. Total stream /
  document size is bounded by the container's caller (the byte buffer
  it hands in): this module enforces only that the declared length
  fits inside ``data``.
* Indirect objects ``N G obj <object> endobj`` (§7.3.10) via
  ``parse_indirect_object``; N and G must be non-negative integer
  tokens (positivity of N is the cross-reference layer's rule).

Bounds (module constants; refusals name the bound):

* ``MAX_NESTING_DEPTH`` = 32 — real survey/DOB documents nest object
  structure a handful of levels deep; 32 is far above any legitimate
  document while keeping the recursive-descent stack two orders of
  magnitude below CPython's default recursion limit, so parsing can
  never raise ``RecursionError``.
* ``MAX_COLLECTION_ITEMS`` = 8192 — applies per single array (elements)
  and per single dictionary (entries). Large legitimate arrays (page
  ``/Kids``, ``TJ`` runs) sit in the hundreds to low thousands; 8192
  bounds per-collection memory and work without truncating real
  documents.

Lookahead note: when an integer's reference lookahead fails, the
lookahead tokens are re-lexed by the enclosing context on its next
iteration. At most two primitive tokens are re-lexed per attempt, so
parsing remains linear-time in the input. Trailing bytes after the
parsed object are never consumed; ``end_offset`` is where the next
parse should resume.
"""

from __future__ import annotations

from dataclasses import dataclass

from .pdf_lexer import LexedToken, PdfName, PdfSyntaxError, lex_primitive

__all__ = [
    "MAX_COLLECTION_ITEMS",
    "MAX_NESTING_DEPTH",
    "ParsedObject",
    "PdfIndirectObject",
    "PdfRef",
    "PdfStream",
    "PdfSyntaxError",
    "parse_indirect_object",
    "parse_object",
]

MAX_NESTING_DEPTH = 32
MAX_COLLECTION_ITEMS = 8192

_MAX_DISPLAY_CHARS = 64
_FOUND_PREVIEW_BYTES = 16

# Kept byte-for-byte identical to pdf_lexer's classification sets (§7.2.3).
_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")
_EOL = frozenset(b"\r\n")

_LENGTH_KEY = PdfName("Length")


@dataclass(frozen=True)
class PdfRef:
    """Indirect reference ``number generation R`` (§7.3.10); unresolved by design."""

    number: int
    generation: int


@dataclass(frozen=True)
class PdfIndirectObject:
    """One ``N G obj ... endobj`` wrapper around its parsed value."""

    number: int
    generation: int
    value: object


@dataclass(frozen=True)
class PdfStream:
    """Stream dictionary plus RAW undecoded data; filters are the container unit's job."""

    dictionary: dict
    raw_data: bytes


@dataclass(frozen=True)
class ParsedObject:
    """One parsed object. ``end_offset`` is the index just past its last consumed byte."""

    value: object
    end_offset: int


def parse_object(data: bytes, offset: int) -> ParsedObject | PdfSyntaxError:
    """Parse exactly one complete PDF object of any kind from ``data`` at ``offset``.

    Primitives come from ``lex_primitive``; arrays, dictionaries, indirect
    references, and streams are assembled here. A dictionary followed by
    the keyword ``stream`` (only when the dictionary is the whole object
    being parsed) becomes a ``PdfStream`` whose ``raw_data`` is the exact
    undecoded ``/Length``-byte span. Never raises; refusals are
    ``PdfSyntaxError`` values.
    """
    if offset < 0:
        return PdfSyntaxError(offset, "non-negative offset", "negative offset")
    parsed = _parse_value(data, offset, 0)
    if isinstance(parsed, PdfSyntaxError):
        return parsed
    value, end = parsed
    if isinstance(value, dict):
        stream = _try_parse_stream(data, end, value)
        if stream is not None:
            return stream
    return ParsedObject(value, end)


def parse_indirect_object(data: bytes, offset: int) -> ParsedObject | PdfSyntaxError:
    """Parse ``N G obj <object> endobj`` (§7.3.10) from ``data`` at ``offset``.

    N and G must be non-negative integer tokens. The body is parsed with
    ``parse_object`` (so a stream body is supported). Returns a
    ``ParsedObject`` wrapping a ``PdfIndirectObject``; ``end_offset`` is
    just past ``endobj``. Never raises; refusals are ``PdfSyntaxError``
    values.
    """
    if offset < 0:
        return PdfSyntaxError(offset, "non-negative offset", "negative offset")
    number_token = lex_primitive(data, offset)
    if isinstance(number_token, PdfSyntaxError):
        return number_token
    if type(number_token.value) is not int or number_token.value < 0:
        return PdfSyntaxError(
            offset,
            "non-negative integer object number",
            _display_text(repr(number_token.value)),
        )
    generation_token = lex_primitive(data, number_token.end_offset)
    if isinstance(generation_token, PdfSyntaxError):
        return generation_token
    if type(generation_token.value) is not int or generation_token.value < 0:
        return PdfSyntaxError(
            number_token.end_offset,
            "non-negative integer generation number",
            _display_text(repr(generation_token.value)),
        )
    probe = _skip_whitespace_and_comments(data, generation_token.end_offset)
    obj_end = _peek_keyword(data, probe, b"obj")
    if obj_end is None:
        return PdfSyntaxError(probe, "'obj'", _display_at(data, probe))
    inner = parse_object(data, obj_end)
    if isinstance(inner, PdfSyntaxError):
        return inner
    probe = _skip_whitespace_and_comments(data, inner.end_offset)
    endobj_end = _peek_keyword(data, probe, b"endobj")
    if endobj_end is None:
        return PdfSyntaxError(probe, "'endobj'", _display_at(data, probe))
    return ParsedObject(
        PdfIndirectObject(number_token.value, generation_token.value, inner.value),
        endobj_end,
    )


def _parse_value(
    data: bytes, offset: int, depth: int
) -> tuple[object, int] | PdfSyntaxError:
    pos = _skip_whitespace_and_comments(data, offset)
    if pos >= len(data):
        return PdfSyntaxError(pos, "object", "end of data")
    byte = data[pos]
    if byte == 0x5B:  # [
        return _parse_array(data, pos, depth)
    if byte == 0x3C and data[pos + 1 : pos + 2] == b"<":  # <<
        return _parse_dictionary(data, pos, depth)
    token = lex_primitive(data, pos)
    if isinstance(token, PdfSyntaxError):
        return token
    number = token.value
    if type(number) is not int:  # bool is excluded: type(), not isinstance()
        return (token.value, token.end_offset)
    return _collapse_reference(data, pos, number, token.end_offset)


def _collapse_reference(
    data: bytes, start: int, number: int, number_end: int
) -> tuple[object, int] | PdfSyntaxError:
    """Apply the §7.3.10 lookahead: ``int int R`` is a reference, else the int stands alone."""
    second = lex_primitive(data, number_end)
    if isinstance(second, PdfSyntaxError):
        return (number, number_end)
    generation = second.value
    if type(generation) is not int:
        return (number, number_end)
    probe = _skip_whitespace_and_comments(data, second.end_offset)
    keyword_end = _peek_keyword(data, probe, b"R")
    if keyword_end is None:
        return (number, number_end)
    if number < 0 or generation < 0:
        return PdfSyntaxError(
            start,
            "non-negative integers in indirect reference",
            f"{number} {generation} R",
        )
    return (PdfRef(number, generation), keyword_end)


def _parse_array(
    data: bytes, start: int, depth: int
) -> tuple[list, int] | PdfSyntaxError:
    if depth >= MAX_NESTING_DEPTH:
        return PdfSyntaxError(
            start, f"nesting depth of at most {MAX_NESTING_DEPTH}", "'['"
        )
    items: list[object] = []
    pos = start + 1
    while True:
        probe = _skip_whitespace_and_comments(data, pos)
        if probe >= len(data):
            return PdfSyntaxError(probe, "']'", "end of data")
        if data[probe] == 0x5D:  # ]
            return (items, probe + 1)
        if len(items) >= MAX_COLLECTION_ITEMS:
            return PdfSyntaxError(
                probe,
                f"array of at most {MAX_COLLECTION_ITEMS} items",
                "oversized array",
            )
        item = _parse_value(data, probe, depth + 1)
        if isinstance(item, PdfSyntaxError):
            return item
        value, pos = item
        items.append(value)


def _parse_dictionary(
    data: bytes, start: int, depth: int
) -> tuple[dict, int] | PdfSyntaxError:
    if depth >= MAX_NESTING_DEPTH:
        return PdfSyntaxError(
            start, f"nesting depth of at most {MAX_NESTING_DEPTH}", "'<<'"
        )
    entries: dict[PdfName, object] = {}
    pos = start + 2
    while True:
        probe = _skip_whitespace_and_comments(data, pos)
        if probe >= len(data):
            return PdfSyntaxError(probe, "'>>' or name key", "end of data")
        if data[probe : probe + 2] == b">>":
            return (entries, probe + 2)
        if data[probe] != 0x2F:  # /
            return PdfSyntaxError(
                probe, "name key ('/...') in dictionary", _display_at(data, probe)
            )
        key_token = lex_primitive(data, probe)
        if isinstance(key_token, PdfSyntaxError):
            return key_token
        key = key_token.value
        if not isinstance(key, PdfName):  # a '/' start guarantees a name; stay total anyway
            return PdfSyntaxError(
                probe, "name key ('/...') in dictionary", _display_at(data, probe)
            )
        if key in entries:
            return PdfSyntaxError(
                probe,
                "unique dictionary key",
                _display_text("/" + key.value) + " duplicated",
            )
        if len(entries) >= MAX_COLLECTION_ITEMS:
            return PdfSyntaxError(
                probe,
                f"dictionary of at most {MAX_COLLECTION_ITEMS} entries",
                "oversized dictionary",
            )
        parsed = _parse_value(data, key_token.end_offset, depth + 1)
        if isinstance(parsed, PdfSyntaxError):
            return parsed
        value, pos = parsed
        entries[key] = value


def _try_parse_stream(
    data: bytes, dict_end: int, dictionary: dict
) -> ParsedObject | PdfSyntaxError | None:
    """Return the stream continuation after a top-level dictionary, or None if there is none."""
    probe = _skip_whitespace_and_comments(data, dict_end)
    keyword_end = _peek_keyword(data, probe, b"stream")
    if keyword_end is None:
        return None
    if _LENGTH_KEY not in dictionary:
        return PdfSyntaxError(probe, "direct /Length integer", "missing /Length")
    length = dictionary[_LENGTH_KEY]
    if isinstance(length, PdfRef):
        return PdfSyntaxError(probe, "direct /Length integer", "indirect reference")
    if type(length) is not int:
        return PdfSyntaxError(
            probe, "direct /Length integer", _display_text(repr(length))
        )
    if length < 0:
        return PdfSyntaxError(
            probe, "direct /Length integer", f"negative integer {length}"
        )
    # §7.3.8.1: the keyword shall be followed by CRLF or LF, never CR alone.
    if data[keyword_end : keyword_end + 2] == b"\r\n":
        data_start = keyword_end + 2
    elif data[keyword_end : keyword_end + 1] == b"\n":
        data_start = keyword_end + 1
    else:
        return PdfSyntaxError(
            keyword_end, "CRLF or LF after 'stream'", _display_at(data, keyword_end)
        )
    data_end = data_start + length
    if data_end > len(data):
        return PdfSyntaxError(data_start, f"{length} stream data bytes", "end of data")
    pos = data_end
    while pos < len(data) and data[pos] in _WHITESPACE:
        pos += 1
    endstream_end = _peek_keyword(data, pos, b"endstream")
    if endstream_end is None:
        return PdfSyntaxError(pos, "'endstream'", _display_at(data, pos))
    return ParsedObject(
        PdfStream(dictionary, data[data_start:data_end]), endstream_end
    )


def _skip_whitespace_and_comments(data: bytes, offset: int) -> int:
    n = len(data)
    pos = offset
    while pos < n:
        byte = data[pos]
        if byte in _WHITESPACE:
            pos += 1
        elif byte == 0x25:  # %
            pos += 1
            while pos < n and data[pos] not in _EOL:
                pos += 1
        else:
            break
    return pos


def _peek_keyword(data: bytes, pos: int, keyword: bytes) -> int | None:
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
