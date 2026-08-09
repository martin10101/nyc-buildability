"""Strict fail-closed interpreter for decoded PDF page content streams.

SB-S1 survey-reader part 5. Interprets the bytes of a page's decoded
``Contents`` stream into flat, device-space geometry and text
(:class:`PageContent`) for downstream survey-dimension extraction.

Doctrine — strict fail-closed subset
------------------------------------
Survey and plat PDFs this pipeline may auto-process are drawn with straight
boundary lines, axis-aligned rectangles, translate+scale transforms, and
horizontal text. This module interprets exactly that subset and nothing
more. Any content outside it — curve operators (``c``/``v``/``y``: survey
boundaries are straight, so curves mean the document is not a plain survey
plat), XObjects (``Do``), inline images (``BI``), shading (``sh``), rotated
or sheared matrices, or any operator not listed below — stops
interpretation and returns :class:`UnsupportedPdfFeature` naming the
feature, so the document routes to human review. Malformed content returns
:class:`PdfSyntaxError`. Errors are returned as frozen values, never
raised, and no partial :class:`PageContent` accompanies an error.

Supported operators
-------------------
Path: ``m l re h``; painting ``S s f F f* B B* b b* n`` (``s b b*`` imply
``h`` first; fill/stroke style is irrelevant to extraction, so every
painting operator simply ends the path). Text: ``BT ET Tf Td TD Tm T* Tj
TJ '``. State: ``q Q cm`` plus the no-effect style/color operators
``w J j M d ri i gs g G rg RG k K cs CS sc scn SC SCN``, which are
consumed (operands cleared) and ignored.

Strictness
----------
* Supported operators demand their exact operand count and types; any
  mismatch is a :class:`PdfSyntaxError` with ``expected``/``found``.
* ``Tj Td TD T* Tm '`` outside ``BT..ET``, nested ``BT``, ``ET`` without
  ``BT``, ``Q`` without ``q``, ``l`` without a current point, and text
  shown before any ``Tf`` are each a :class:`PdfSyntaxError`.
* At end of content, leftover operands, an unclosed ``BT``, or unrestored
  ``q`` saves are :class:`PdfSyntaxError` (fail closed, no silent repair).
* Bounds, each returned as :class:`UnsupportedPdfFeature` naming the
  bound: ``MAX_CONTENT_OPERATORS`` executed operators, ``MAX_PRIMITIVES``
  lexed operands (inline-array elements count; each completed array also
  counts once), ``MAX_Q_DEPTH`` saved graphics states.

Geometry and transform model
----------------------------
The CTM is restricted to translation+scale, held as ``(sx, sy, tx, ty)``
mapping user ``(x, y)`` to device ``(x*sx + tx, y*sy + ty)``. ``cm`` with
nonzero ``b`` or ``c`` is :class:`UnsupportedPdfFeature`
"rotated/sheared graphics" (likewise ``Tm`` → "rotated/sheared text").
All emitted coordinates are device-space: path points, rectangle
origin/extent, and text positions are transformed through the CTM in
effect when the emitting operator runs. ``q``/``Q`` save/restore the CTM
only.

Documented simplifications
--------------------------
* Shown text bytes are decoded ``latin-1`` with ``errors="replace"`` — no
  font encodings, CMaps, or ToUnicode handling. Survey dimension labels
  are ASCII digits/punctuation, for which latin-1 is exact.
* ``TJ`` kerning numbers are ignored; the array's strings are concatenated
  into one run. Positions come from the text matrix, not glyph metrics.
* Text showing does not advance the text position (no font metrics in this
  subset); every ``Tj``/``TJ``/``'`` emits exactly one :class:`TextRun`
  (possibly empty) anchored at the current line origin.
* ``Td``/``TD`` translate the line origin through the ``Tm`` scale
  (``e += tx*a``, ``f += ty*d``); ``TD`` sets leading to ``-ty``; ``T*``
  advances ``f`` by ``-leading*d`` (PDF semantics, scale-composed).
* Reported ``font_size`` is ``abs(Tf size × Tm d)``; the CTM scales
  positions but not the reported font size. Leading and font size persist
  across ``BT..ET`` blocks (``BT`` resets only the text matrix).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.documents.extraction.pdf_lexer import (
    LexedToken,
    PdfName,
    PdfSyntaxError,
    lex_primitive,
)
from app.documents.extraction.pdf_xref import UnsupportedPdfFeature

MAX_CONTENT_OPERATORS = 100000
MAX_PRIMITIVES = 50000
MAX_Q_DEPTH = 64

_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")

_PAINTING_OPERATORS = frozenset({"S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"})
_CLOSE_BEFORE_PAINT = frozenset({"s", "b", "b*"})
_TEXT_OBJECT_OPERATORS = frozenset({"Td", "TD", "Tm", "T*", "Tj", "TJ", "'"})
_IGNORED_OPERATORS = frozenset(
    {
        "w", "J", "j", "M", "d", "ri", "i", "gs",
        "g", "G", "rg", "RG", "k", "K",
        "cs", "CS", "sc", "scn", "SC", "SCN",
    }
)


@dataclass(frozen=True)
class VectorSegment:
    """One straight line segment, endpoints in device space."""

    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True)
class VectorRect:
    """One ``re`` rectangle: origin and extent transformed to device space."""

    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class TextRun:
    """One shown text run anchored at its device-space line origin."""

    text: str
    x: float
    y: float
    font_size: float


@dataclass(frozen=True)
class PageContent:
    """Everything extracted from one content stream, in execution order."""

    segments: tuple[VectorSegment, ...]
    rects: tuple[VectorRect, ...]
    text_runs: tuple[TextRun, ...]


def interpret_content(content: bytes) -> PageContent | PdfSyntaxError | UnsupportedPdfFeature:
    """Interpret one decoded content stream under the strict survey subset.

    Returns :class:`PageContent` on success, or the first
    :class:`PdfSyntaxError` / :class:`UnsupportedPdfFeature` encountered
    (returned, never raised).
    """
    return _Interpreter(content).run()


class _Interpreter:
    """Mutable scanner/executor state for a single :func:`interpret_content` call."""

    def __init__(self, content: bytes) -> None:
        self._data = content
        self._pos = 0
        self._operands: list[object] = []
        self._primitive_count = 0
        self._operator_count = 0
        # Translate+scale CTM: (sx, sy, tx, ty) maps (x, y) -> (x*sx+tx, y*sy+ty).
        self._ctm: tuple[float, float, float, float] = (1.0, 1.0, 0.0, 0.0)
        self._ctm_stack: list[tuple[float, float, float, float]] = []
        self._current: tuple[float, float] | None = None
        self._subpath_start: tuple[float, float] | None = None
        self._in_text = False
        self._tm_a = 1.0
        self._tm_d = 1.0
        self._tm_e = 0.0
        self._tm_f = 0.0
        self._leading = 0.0
        self._font_size: float | None = None
        self._segments: list[VectorSegment] = []
        self._rects: list[VectorRect] = []
        self._text_runs: list[TextRun] = []

    def run(self) -> PageContent | PdfSyntaxError | UnsupportedPdfFeature:
        data = self._data
        while True:
            self._skip_whitespace_and_comments()
            if self._pos >= len(data):
                break
            if data[self._pos] == 0x5B:  # '[' — inline array operand (for TJ, d)
                error = self._read_inline_array()
                if error is not None:
                    return error
                continue
            token = lex_primitive(data, self._pos)
            if isinstance(token, LexedToken):
                error = self._push_operand(token.value)
                if error is not None:
                    return error
                self._pos = token.end_offset
                continue
            # Not a primitive: try an operator word (run of regular characters).
            word_start = self._pos
            word_end = word_start
            while word_end < len(data) and self._is_regular(data[word_end]):
                word_end += 1
            if word_end == word_start:
                # Neither primitive nor operator: surface the lexer's diagnosis.
                return token
            word = data[word_start:word_end].decode("latin-1")
            self._pos = word_end
            self._operator_count += 1
            if self._operator_count > MAX_CONTENT_OPERATORS:
                return UnsupportedPdfFeature(
                    "MAX_CONTENT_OPERATORS",
                    f"content stream exceeds MAX_CONTENT_OPERATORS={MAX_CONTENT_OPERATORS}"
                    " operators",
                )
            error = self._execute(word, word_start)
            if error is not None:
                return error
        end = len(data)
        if self._operands:
            return PdfSyntaxError(
                end,
                "an operator consuming the pending operands",
                f"end of content with {len(self._operands)} unconsumed operand(s)",
            )
        if self._in_text:
            return PdfSyntaxError(end, "ET closing the open text object", "end of content")
        if self._ctm_stack:
            return PdfSyntaxError(
                end,
                "Q restoring every saved graphics state",
                f"end of content with {len(self._ctm_stack)} unrestored q save(s)",
            )
        return PageContent(
            tuple(self._segments), tuple(self._rects), tuple(self._text_runs)
        )

    # -- scanning ---------------------------------------------------------

    def _skip_whitespace_and_comments(self) -> None:
        data = self._data
        while self._pos < len(data):
            byte = data[self._pos]
            if byte in _WHITESPACE:
                self._pos += 1
            elif byte == 0x25:  # '%' comment runs to end of line
                while self._pos < len(data) and data[self._pos] not in (0x0D, 0x0A):
                    self._pos += 1
            else:
                return

    @staticmethod
    def _is_regular(byte: int) -> bool:
        return byte not in _WHITESPACE and byte not in _DELIMITERS

    def _count_primitive(self) -> UnsupportedPdfFeature | None:
        self._primitive_count += 1
        if self._primitive_count > MAX_PRIMITIVES:
            return UnsupportedPdfFeature(
                "MAX_PRIMITIVES",
                f"content stream exceeds MAX_PRIMITIVES={MAX_PRIMITIVES} operands",
            )
        return None

    def _push_operand(self, value: object) -> UnsupportedPdfFeature | None:
        error = self._count_primitive()
        if error is not None:
            return error
        self._operands.append(value)
        return None

    def _read_inline_array(self) -> PdfSyntaxError | UnsupportedPdfFeature | None:
        data = self._data
        self._pos += 1  # consume '['
        items: list[object] = []
        while True:
            self._skip_whitespace_and_comments()
            if self._pos >= len(data):
                return PdfSyntaxError(
                    len(data), "']' closing the inline array", "end of content"
                )
            byte = data[self._pos]
            if byte == 0x5D:  # ']'
                self._pos += 1
                return self._push_operand(tuple(items))
            if byte == 0x5B:  # nested '[' — outside the subset
                return PdfSyntaxError(
                    self._pos, "a primitive or ']' in the inline array", "nested '['"
                )
            token = lex_primitive(data, self._pos)
            if isinstance(token, PdfSyntaxError):
                return token
            error = self._count_primitive()
            if error is not None:
                return error
            items.append(token.value)
            self._pos = token.end_offset

    # -- operand consumption ----------------------------------------------

    def _take(
        self, offset: int, word: str, kinds: str, shape: str
    ) -> tuple[tuple[object, ...] | None, PdfSyntaxError | None]:
        """Consume exactly the operands ``kinds`` describes, else diagnose.

        ``kinds`` is one code per required operand: ``n`` number,
        ``s`` string, ``m`` name, ``a`` array.
        """
        if kinds:
            expected = f"'{word}' with {len(kinds)} operand(s): {shape}"
        else:
            expected = f"'{word}' with no operands"
        ops = self._operands
        if len(ops) != len(kinds):
            return None, PdfSyntaxError(offset, expected, f"{len(ops)} operand(s)")
        for value, kind in zip(ops, kinds, strict=False):
            if not self._matches_kind(value, kind):
                found = "operand types " + ", ".join(self._type_name(v) for v in ops)
                return None, PdfSyntaxError(offset, expected, found)
        values = tuple(ops)
        ops.clear()
        return values, None

    @staticmethod
    def _matches_kind(value: object, kind: str) -> bool:
        if kind == "n":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if kind == "s":
            return isinstance(value, bytes)
        if kind == "m":
            return isinstance(value, PdfName)
        return isinstance(value, tuple)  # "a"

    @staticmethod
    def _type_name(value: object) -> str:
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, bytes):
            return "string"
        if isinstance(value, PdfName):
            return "name"
        if isinstance(value, tuple):
            return "array"
        return type(value).__name__

    # -- geometry helpers --------------------------------------------------

    def _to_device(self, x: float, y: float) -> tuple[float, float]:
        sx, sy, tx, ty = self._ctm
        return (float(x) * sx + tx, float(y) * sy + ty)

    def _emit_segment(self, p0: tuple[float, float], p1: tuple[float, float]) -> None:
        x0, y0 = self._to_device(p0[0], p0[1])
        x1, y1 = self._to_device(p1[0], p1[1])
        self._segments.append(VectorSegment(x0, y0, x1, y1))

    def _close_subpath(self) -> None:
        if self._current is None or self._subpath_start is None:
            return
        if self._current != self._subpath_start:
            self._emit_segment(self._current, self._subpath_start)
        self._current = self._subpath_start

    def _show_text(self, offset: int, raw: bytes) -> PdfSyntaxError | None:
        if self._font_size is None:
            return PdfSyntaxError(
                offset,
                "Tf setting a font before text is shown",
                "text shown with no font set",
            )
        x, y = self._to_device(self._tm_e, self._tm_f)
        size = abs(self._font_size * self._tm_d)
        self._text_runs.append(
            TextRun(raw.decode("latin-1", errors="replace"), x, y, size)
        )
        return None

    # -- operator execution ------------------------------------------------

    def _execute(
        self, word: str, offset: int
    ) -> PdfSyntaxError | UnsupportedPdfFeature | None:
        # Path construction.
        if word == "m":
            values, error = self._take(offset, word, "nn", "x y (numbers)")
            if error is not None:
                return error
            x, y = values
            self._current = (float(x), float(y))
            self._subpath_start = self._current
            return None
        if word == "l":
            values, error = self._take(offset, word, "nn", "x y (numbers)")
            if error is not None:
                return error
            if self._current is None:
                return PdfSyntaxError(
                    offset,
                    "a current point ('m' or 're' before 'l')",
                    "'l' with no current point",
                )
            x, y = values
            new_point = (float(x), float(y))
            self._emit_segment(self._current, new_point)
            self._current = new_point
            return None
        if word == "re":
            values, error = self._take(offset, word, "nnnn", "x y w h (numbers)")
            if error is not None:
                return error
            x, y, w, h = values
            sx, sy, tx, ty = self._ctm
            self._rects.append(
                VectorRect(
                    float(x) * sx + tx, float(y) * sy + ty, float(w) * sx, float(h) * sy
                )
            )
            self._current = (float(x), float(y))
            self._subpath_start = self._current
            return None
        if word == "h":
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            self._close_subpath()
            return None
        if word in _PAINTING_OPERATORS:
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            if word in _CLOSE_BEFORE_PAINT:
                self._close_subpath()
            self._current = None
            self._subpath_start = None
            return None

        # Text objects and text state.
        if word == "BT":
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            if self._in_text:
                return PdfSyntaxError(offset, "ET before another BT", "nested BT")
            self._in_text = True
            self._tm_a = 1.0
            self._tm_d = 1.0
            self._tm_e = 0.0
            self._tm_f = 0.0
            return None
        if word == "ET":
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            if not self._in_text:
                return PdfSyntaxError(
                    offset, "BT opening a text object before ET", "ET outside BT..ET"
                )
            self._in_text = False
            return None
        if word == "Tf":
            values, error = self._take(
                offset, word, "mn", "font name and size (name, number)"
            )
            if error is not None:
                return error
            self._font_size = float(values[1])
            return None
        if word in _TEXT_OBJECT_OPERATORS:
            if not self._in_text:
                return PdfSyntaxError(
                    offset,
                    f"'{word}' inside a BT..ET text object",
                    f"'{word}' outside BT..ET",
                )
            if word in ("Td", "TD"):
                values, error = self._take(offset, word, "nn", "tx ty (numbers)")
                if error is not None:
                    return error
                tx, ty = values
                self._tm_e += float(tx) * self._tm_a
                self._tm_f += float(ty) * self._tm_d
                if word == "TD":
                    self._leading = -float(ty)
                return None
            if word == "Tm":
                values, error = self._take(offset, word, "nnnnnn", "a b c d e f (numbers)")
                if error is not None:
                    return error
                a, b, c, d, e, f = values
                if b != 0 or c != 0:
                    return UnsupportedPdfFeature(
                        "rotated/sheared text",
                        f"Tm with b={b} c={c} at offset {offset}",
                    )
                self._tm_a = float(a)
                self._tm_d = float(d)
                self._tm_e = float(e)
                self._tm_f = float(f)
                return None
            if word == "T*":
                _, error = self._take(offset, word, "", "")
                if error is not None:
                    return error
                self._tm_f -= self._leading * self._tm_d
                return None
            if word == "Tj":
                values, error = self._take(offset, word, "s", "one string")
                if error is not None:
                    return error
                return self._show_text(offset, values[0])
            if word == "'":
                values, error = self._take(offset, word, "s", "one string")
                if error is not None:
                    return error
                self._tm_f -= self._leading * self._tm_d
                return self._show_text(offset, values[0])
            # word == "TJ"
            values, error = self._take(
                offset, word, "a", "one array of strings and kerning numbers"
            )
            if error is not None:
                return error
            pieces: list[bytes] = []
            for element in values[0]:
                if isinstance(element, bytes):
                    pieces.append(element)
                elif isinstance(element, (int, float)) and not isinstance(element, bool):
                    continue  # kerning adjustment — ignored (documented simplification)
                else:
                    return PdfSyntaxError(
                        offset,
                        "TJ array elements that are strings or kerning numbers",
                        f"element of type {self._type_name(element)}",
                    )
            return self._show_text(offset, b"".join(pieces))

        # Graphics state.
        if word == "q":
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            if len(self._ctm_stack) >= MAX_Q_DEPTH:
                return UnsupportedPdfFeature(
                    "MAX_Q_DEPTH",
                    f"graphics state nesting exceeds MAX_Q_DEPTH={MAX_Q_DEPTH}",
                )
            self._ctm_stack.append(self._ctm)
            return None
        if word == "Q":
            _, error = self._take(offset, word, "", "")
            if error is not None:
                return error
            if not self._ctm_stack:
                return PdfSyntaxError(
                    offset, "a matching q before Q", "Q with no saved graphics state"
                )
            self._ctm = self._ctm_stack.pop()
            return None
        if word == "cm":
            values, error = self._take(offset, word, "nnnnnn", "a b c d e f (numbers)")
            if error is not None:
                return error
            a, b, c, d, e, f = values
            if b != 0 or c != 0:
                return UnsupportedPdfFeature(
                    "rotated/sheared graphics",
                    f"cm with b={b} c={c} at offset {offset}",
                )
            sx, sy, tx, ty = self._ctm
            self._ctm = (
                float(a) * sx,
                float(d) * sy,
                float(e) * sx + tx,
                float(f) * sy + ty,
            )
            return None
        if word in _IGNORED_OPERATORS:
            self._operands.clear()
            return None

        # Everything else — including curves c/v/y, Do, BI, sh — fails closed.
        return UnsupportedPdfFeature(
            f"content operator '{word}'",
            f"operator '{word}' at offset {offset} is outside the strict survey subset"
            " (curves and images are unsupported: survey boundaries are straight;"
            " documents using them route to manual review)",
        )
