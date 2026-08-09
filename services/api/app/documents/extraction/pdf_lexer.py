"""Fail-closed PDF primitive-token lexer (M2-T015 unit 3i-3a-1a).

Lexes exactly ONE PDF primitive token — boolean, null, integer, real,
literal string, hexadecimal string, or name — from a byte buffer at a
caller-supplied offset. Pure function of ``bytes``: no I/O, no globals,
no clock, no randomness.

Fail-closed doctrine: every malformed, truncated, oversized, ambiguous,
or non-primitive construct is returned as a ``PdfSyntaxError`` refusal
VALUE. Nothing here raises, guesses, repairs, or coerces suspect input
into a usable value. Composite constructs (arrays ``[ ]``, dictionaries
``<< >>``, procedures ``{ }``) and the structural keywords ``obj`` /
``endobj`` / ``stream`` / ``R`` are refused by design: they belong to
the composite parser (next unit), which calls this lexer for the
primitives between them.

Deliberate strictness beyond ISO 32000-1 where the spec is permissive:

* Reals with an exponent (``1e5``) are refused — PDF numbers have none.
* An unknown escape in a literal string is refused rather than having
  its backslash silently dropped (the spec's recovery behaviour).
* The name escape ``#00`` is refused (prohibited by §7.3.5).
* Numeric tokens longer than ``MAX_NUMBER_BYTES`` are refused: Annex C
  implementation limits make them implausible, and the bound keeps
  integer conversion total on every interpreter.

Spec-mandated normalizations that ARE applied: an unescaped CR or CRLF
inside a literal string becomes LF (§7.3.4.2); an odd final hex digit
in a hexadecimal string implies a trailing ``0`` (§7.3.4.3); ``/`` with
no regular characters is the valid empty name (§7.3.5).

Bounds (module constants):

* ``MAX_TOKEN_BYTES`` — maximum raw source span of one token, measured
  from its first byte (including any opening ``(``, ``<``, or ``/``)
  through its last consumed byte; longer tokens are refused with a
  message naming the bound.
* ``MAX_NUMBER_BYTES`` — maximum length of a numeric token.

``expected`` / ``found`` strings in refusals are bounded diagnostics
(long or unprintable input is truncated/escaped), never raw echoes of
unbounded attacker-controlled bytes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

__all__ = [
    "MAX_NUMBER_BYTES",
    "MAX_TOKEN_BYTES",
    "LexedToken",
    "PdfName",
    "PdfSyntaxError",
    "lex_primitive",
]

MAX_TOKEN_BYTES = 65536
MAX_NUMBER_BYTES = 64

_MAX_DISPLAY_CHARS = 64

_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")
_EOL = frozenset(b"\r\n")
_DIGITS = frozenset(b"0123456789")
_OCTAL_DIGITS = frozenset(b"01234567")
_HEX_DIGITS = frozenset(b"0123456789abcdefABCDEF")
_NON_PRIMITIVE_KEYWORDS = frozenset({b"obj", b"endobj", b"stream", b"R"})
_STRING_SIMPLE_ESCAPES = {
    ord("n"): 0x0A,
    ord("r"): 0x0D,
    ord("t"): 0x09,
    ord("b"): 0x08,
    ord("f"): 0x0C,
    ord("("): 0x28,
    ord(")"): 0x29,
    ord("\\"): 0x5C,
}


@dataclass(frozen=True)
class PdfName:
    """A PDF name token; ``value`` holds the ``#xx``-decoded bytes as latin-1 text (lossless)."""

    value: str


@dataclass(frozen=True)
class PdfSyntaxError:
    """Refusal value for any input this lexer will not turn into a token."""

    offset: int
    expected: str
    found: str

    reject_code: ClassVar[str] = "pdf_syntax_error"

    def to_payload(self) -> dict[str, object]:
        return {
            "reject_code": self.reject_code,
            "offset": self.offset,
            "expected": self.expected,
            "found": self.found,
        }


@dataclass(frozen=True)
class LexedToken:
    """One lexed primitive. ``end_offset`` is the index just past the token's last byte."""

    value: object
    end_offset: int


def lex_primitive(data: bytes, offset: int) -> LexedToken | PdfSyntaxError:
    """Lex exactly one primitive token from ``data`` starting at ``offset``.

    Skips whitespace (``\\x00 \\t \\n \\x0c \\r`` space) and ``%`` comments,
    then lexes one primitive: ``true``/``false``/``null``, integer, real,
    literal string ``(...)`` (as ``bytes``), hex string ``<...>`` (as
    ``bytes``), or name ``/...`` (as ``PdfName``). Trailing bytes after
    the token are never consumed; ``end_offset`` is where the next call
    should resume. Everything else — including the composite delimiters
    ``[ ] << >> { }`` and the keywords ``obj``/``endobj``/``stream``/``R``
    — returns a ``PdfSyntaxError`` refusal value. Never raises.
    """
    if offset < 0:
        return PdfSyntaxError(offset, "non-negative offset", "negative offset")
    pos = _skip_whitespace_and_comments(data, offset)
    if pos >= len(data):
        return PdfSyntaxError(pos, "token", "end of data")
    byte = data[pos]
    if byte == 0x28:  # (
        return _lex_literal_string(data, pos)
    if byte == 0x3C:  # <
        if data[pos + 1 : pos + 2] == b"<":
            return PdfSyntaxError(pos, "primitive token", "<<")
        return _lex_hex_string(data, pos)
    if byte == 0x2F:  # /
        return _lex_name(data, pos)
    if byte == 0x3E:  # >
        found = ">>" if data[pos + 1 : pos + 2] == b">" else ">"
        return PdfSyntaxError(pos, "primitive token", found)
    if byte in b"[]{})":
        return PdfSyntaxError(pos, "primitive token", chr(byte))
    return _lex_regular_run(data, pos)


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


def _lex_regular_run(data: bytes, start: int) -> LexedToken | PdfSyntaxError:
    n = len(data)
    pos = start
    while pos < n and data[pos] not in _WHITESPACE and data[pos] not in _DELIMITERS:
        if pos - start >= MAX_TOKEN_BYTES:
            return _oversized(start)
        pos += 1
    run = data[start:pos]
    if run == b"true":
        return LexedToken(True, pos)
    if run == b"false":
        return LexedToken(False, pos)
    if run == b"null":
        return LexedToken(None, pos)
    if run in _NON_PRIMITIVE_KEYWORDS:
        return PdfSyntaxError(start, "primitive token", run.decode("ascii"))
    if run[0] in b"0123456789+-.":
        return _classify_number(run, start, pos)
    return PdfSyntaxError(start, "primitive token", _display(run))


def _classify_number(run: bytes, start: int, end: int) -> LexedToken | PdfSyntaxError:
    if len(run) > MAX_NUMBER_BYTES:
        return PdfSyntaxError(
            start, f"number of at most {MAX_NUMBER_BYTES} bytes", _display(run)
        )
    if 0x65 in run or 0x45 in run:  # e / E
        return PdfSyntaxError(start, "number without exponent", _display(run))
    body = run[1:] if run[:1] in (b"+", b"-") else run
    dots = body.count(b".")
    digit_count = sum(1 for char in body if char in _DIGITS)
    if not body or dots > 1 or digit_count == 0 or digit_count + dots != len(body):
        return PdfSyntaxError(start, "number", _display(run))
    text = run.decode("ascii")
    if dots:
        return LexedToken(float(text), end)
    return LexedToken(int(text), end)


def _lex_literal_string(data: bytes, start: int) -> LexedToken | PdfSyntaxError:
    n = len(data)
    pos = start + 1
    depth = 1
    out = bytearray()
    while True:
        if pos - start >= MAX_TOKEN_BYTES:
            return _oversized(start)
        if pos >= n:
            return PdfSyntaxError(start, "')'", "end of data")
        byte = data[pos]
        if byte == 0x5C:  # backslash
            if pos + 1 >= n:
                return PdfSyntaxError(start, "')'", "end of data")
            escape = data[pos + 1]
            if escape in _STRING_SIMPLE_ESCAPES:
                out.append(_STRING_SIMPLE_ESCAPES[escape])
                pos += 2
            elif escape in _OCTAL_DIGITS:
                value = escape - 0x30
                consumed = 1
                while (
                    consumed < 3
                    and pos + 1 + consumed < n
                    and data[pos + 1 + consumed] in _OCTAL_DIGITS
                ):
                    value = value * 8 + (data[pos + 1 + consumed] - 0x30)
                    consumed += 1
                out.append(value & 0xFF)  # high-order overflow ignored per spec
                pos += 1 + consumed
            elif escape == 0x0D:  # backslash-EOL line continuation (CR or CRLF)
                pos += 2
                if pos < n and data[pos] == 0x0A:
                    pos += 1
            elif escape == 0x0A:  # backslash-LF line continuation
                pos += 2
            else:
                return PdfSyntaxError(pos, "string escape", "\\" + _display_byte(escape))
        elif byte == 0x28:  # (
            depth += 1
            out.append(byte)
            pos += 1
        elif byte == 0x29:  # )
            depth -= 1
            if depth == 0:
                return LexedToken(bytes(out), pos + 1)
            out.append(byte)
            pos += 1
        elif byte == 0x0D:  # unescaped CR / CRLF normalizes to LF per spec
            out.append(0x0A)
            pos += 1
            if pos < n and data[pos] == 0x0A:
                pos += 1
        else:
            out.append(byte)
            pos += 1


def _lex_hex_string(data: bytes, start: int) -> LexedToken | PdfSyntaxError:
    n = len(data)
    pos = start + 1
    digits = bytearray()
    while True:
        if pos - start >= MAX_TOKEN_BYTES:
            return _oversized(start)
        if pos >= n:
            return PdfSyntaxError(start, "'>'", "end of data")
        byte = data[pos]
        if byte == 0x3E:  # >
            pos += 1
            break
        if byte in _WHITESPACE:
            pos += 1
            continue
        if byte in _HEX_DIGITS:
            digits.append(byte)
            pos += 1
            continue
        return PdfSyntaxError(pos, "hexadecimal digit", _display_byte(byte))
    if len(digits) % 2:
        digits.append(0x30)  # odd final digit implies trailing 0 per spec
    return LexedToken(bytes.fromhex(digits.decode("ascii")), pos)


def _lex_name(data: bytes, start: int) -> LexedToken | PdfSyntaxError:
    n = len(data)
    pos = start + 1
    out = bytearray()
    while pos < n and data[pos] not in _WHITESPACE and data[pos] not in _DELIMITERS:
        if pos - start >= MAX_TOKEN_BYTES:
            return _oversized(start)
        byte = data[pos]
        if byte == 0x23:  # #
            pair = data[pos + 1 : pos + 3]
            if len(pair) != 2 or pair[0] not in _HEX_DIGITS or pair[1] not in _HEX_DIGITS:
                found = "#" + _display(pair) if pair else "end of data"
                return PdfSyntaxError(pos, "two hexadecimal digits after '#'", found)
            value = int(pair.decode("ascii"), 16)
            if value == 0:
                return PdfSyntaxError(pos, "non-NUL name escape", "#00")
            out.append(value)
            pos += 3
        else:
            out.append(byte)
            pos += 1
    if pos - start > MAX_TOKEN_BYTES:
        return _oversized(start)
    return LexedToken(PdfName(out.decode("latin-1")), pos)


def _oversized(start: int) -> PdfSyntaxError:
    return PdfSyntaxError(
        start, f"token of at most {MAX_TOKEN_BYTES} bytes", "oversized token"
    )


def _display(raw: bytes) -> str:
    text = raw.decode("latin-1")
    if len(text) > _MAX_DISPLAY_CHARS:
        return text[: _MAX_DISPLAY_CHARS - 3] + "..."
    return text


def _display_byte(byte: int) -> str:
    if 0x20 <= byte <= 0x7E:
        return chr(byte)
    return f"\\x{byte:02x}"
