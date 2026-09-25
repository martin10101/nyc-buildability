"""Bounded inline ``<< >>`` marked-content property-list dictionary operand lexer for the
architect drawing-sheet reader profile (M5-T113, D-087 PDF-2; DB-076 b).

ISO 32000-1 §14.6 (marked content): the ``BDC`` (begin marked-content sequence with a
property list) and ``DP`` (marked-content point with a property list) operators take a tag
name plus a property-list operand that is EITHER a name (a key into the page's ``/Properties``
resource sub-dictionary) or an INLINE ``<< >>`` dictionary. Real architect PDFs (corpus items
3-6) wrap their content in ``/OC << ... >> BDC`` … ``EMC`` marked-content sequences, so the
sheet reader must consume that inline dictionary instead of refusing it as an unsupported
token. This module consumes it as a BALANCED, DEPTH- and LENGTH-BOUNDED token span and returns
a discarded sentinel: a marked-content property list carries NO drawing geometry (§8.2 lists
the content-stream operators; ``BDC``/``DP`` paint nothing), so the interpreter records the
operand only to keep the operator's operand arity balanced and NEVER interprets its contents as
a path, transform, text run, or XObject. Inline IMAGES (``BI``/``ID``/``EI``, §8.9.7) are a
different construct and stay refused (DB-055 d); this module handles ONLY the ``<< >>`` operand.

Doctrine (inherited from the sheet reader): refusal is a VALUE, never an exception; an
unbalanced, too-deeply-nested, or too-long property list is a typed :class:`SheetRefusal` with a
bounded detail — never a partial read; no byte is executed and no network is touched. Scalar
tokens (names, numbers, strings, booleans, null) are lexed by the reused strict
:func:`app.documents.extraction.pdf_lexer.lex_primitive`; only the structural delimiters
``<< >> [ ]`` are handled here (that lexer refuses them by design), so there is exactly one
primitive lexer. This module imports only downward (the strict lexer leaf +
:mod:`app.drawings.sheet_objects` for the shared refusal helper); the interpreter imports it.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.documents.extraction.pdf_lexer import PdfSyntaxError, lex_primitive
from app.drawings.sheet_objects import _refuse
from app.drawings.sheet_primitives import SheetRefusal

__all__ = [
    "MAX_MARKED_CONTENT_BYTES",
    "MAX_MARKED_CONTENT_DEPTH",
    "InlineDictSpan",
    "MarkedContentDict",
    "read_inline_dict",
]

# -- bounds (each over-limit is a typed refusal VALUE; threaded into the interpreter at read
#    time via the facade limits, so patching the facade constant still bites) ---------------
MAX_MARKED_CONTENT_DEPTH = 16       # ``<< >>`` / ``[ ]`` nesting depth cap for one property list
MAX_MARKED_CONTENT_BYTES = 65_536   # total source-span cap for one property list (§14.6)

_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_OPEN_ANGLE = 0x3C   # '<'
_CLOSE_ANGLE = 0x3E  # '>'
_OPEN_BRACKET = 0x5B  # '['
_CLOSE_BRACKET = 0x5D  # ']'
_PERCENT = 0x25       # '%'
_CR = 0x0D
_LF = 0x0A


@dataclass(frozen=True)
class MarkedContentDict:
    """A parsed-and-discarded marked-content property list operand (§14.6). It carries ONLY its
    source ``byte_length`` and the maximum nesting ``max_depth`` reached (both bounded); its
    contents are never interpreted as drawing, since a marked-content sequence paints nothing."""

    byte_length: int
    max_depth: int


@dataclass(frozen=True)
class InlineDictSpan:
    """The consumed inline dictionary: the discarded ``value`` operand plus ``end_offset`` (the
    index just past the closing ``>>``), so the scanner resumes after the property list."""

    value: MarkedContentDict
    end_offset: int


def read_inline_dict(
    data: bytes, start: int, *, max_depth: int, max_bytes: int
) -> InlineDictSpan | SheetRefusal:
    """Consume the balanced inline ``<< ... >>`` property list beginning at ``start`` (which
    must index the opening ``<<``), returning an :class:`InlineDictSpan` (a discarded sentinel
    and the offset just past the closing ``>>``), or a typed :class:`SheetRefusal` when the list
    is unbalanced, nests past ``max_depth`` (``<< >>`` and ``[ ]`` both count toward depth), or
    spans more than ``max_bytes`` bytes. Never raises; never interprets the contents as drawing.

    Scalar tokens are consumed by :func:`lex_primitive`; only ``<< >> [ ]`` are handled here.
    A single ``<`` (a hex-string operand) is left to :func:`lex_primitive` — the interpreter
    only routes a leading ``<<`` here, so a hex-string value inside the list is lexed normally.
    """
    n = len(data)
    depth = 0
    max_reached = 0
    pos = start
    while pos < n:
        if pos - start > max_bytes:
            return _refuse(
                "marked-content dictionary", f"property list over {max_bytes} bytes"
            )
        pos = _skip_ws_comments(data, pos)
        if pos >= n:
            break
        byte = data[pos]
        if byte == _OPEN_ANGLE and pos + 1 < n and data[pos + 1] == _OPEN_ANGLE:  # '<<'
            depth += 1
            max_reached = max(max_reached, depth)
            if depth > max_depth:
                return _refuse(
                    "marked-content dictionary",
                    f"property list nested over depth {max_depth}",
                )
            pos += 2
            continue
        if byte == _CLOSE_ANGLE and pos + 1 < n and data[pos + 1] == _CLOSE_ANGLE:  # '>>'
            depth -= 1
            pos += 2
            if depth == 0:
                length = pos - start
                if length > max_bytes:
                    return _refuse(
                        "marked-content dictionary", f"property list over {max_bytes} bytes"
                    )
                return InlineDictSpan(MarkedContentDict(length, max_reached), pos)
            if depth < 0:  # a '>>' with no matching '<<' (unreachable: we start on '<<')
                return _refuse(
                    "marked-content dictionary", "unbalanced '>>' in a property list"
                )
            continue
        if byte == _OPEN_BRACKET:  # '[' array open
            depth += 1
            max_reached = max(max_reached, depth)
            if depth > max_depth:
                return _refuse(
                    "marked-content dictionary",
                    f"property list nested over depth {max_depth}",
                )
            pos += 1
            continue
        if byte == _CLOSE_BRACKET:  # ']' array close
            depth -= 1
            if depth < 0:
                return _refuse(
                    "marked-content dictionary", "unbalanced ']' in a property list"
                )
            pos += 1
            continue
        token = lex_primitive(data, pos)
        if isinstance(token, PdfSyntaxError):
            return _refuse(
                "marked-content dictionary",
                "a property-list token is malformed or unsupported",
            )
        pos = token.end_offset
    return _refuse(
        "marked-content dictionary", "property list is not balanced before the stream ends"
    )


def _skip_ws_comments(data: bytes, pos: int) -> int:
    """Advance past whitespace and ``%`` comments (§7.2.3) between property-list tokens."""
    n = len(data)
    while pos < n:
        byte = data[pos]
        if byte in _WHITESPACE:
            pos += 1
        elif byte == _PERCENT:  # comment to end of line
            pos += 1
            while pos < n and data[pos] not in (_CR, _LF):
                pos += 1
        else:
            return pos
    return pos
