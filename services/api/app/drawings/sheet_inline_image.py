"""Bounded inline-image (``BI`` ... ``ID`` ... ``EI``) skip for the architect drawing-sheet
reader profile (M5-T118, D-087 PDF-3; DB-055 d).

ISO 32000-1 §8.9.7 (inline images): a content stream may embed a small image directly with the
``BI`` (begin image) / ``ID`` (image data) / ``EI`` (end image) operators, rather than as an image
XObject. Between ``BI`` and ``ID`` is an ABBREVIATED image dictionary (Table 92 key abbreviations,
Table 93 filter/colour-space abbreviations); after ``ID`` and a single whitespace byte comes the raw
sample data, terminated by ``EI``. An inline image is a raster, not drawing linework, so this reader
SKIPS it (never decodes the samples, never refuses the whole document for it — the M5-T113 corpus
blocker for item 4) and discloses a per-page count. The /DP (or /DecodeParms) value may itself be a
decode-parameters DICTIONARY, or an array of such dictionaries / nulls (the common CCITTFax /
Flate-predictor shape in scanned sheets, M5-T120 / DB-090 a); it is consumed for BALANCE only — one
nested ``<< >>`` level, that key only, under the same byte cap — so the image still skips instead
of refusing (any other key with a nested dictionary, or a second nesting level, stays a refusal).

The hard problem is skipping the data WITHOUT desynchronizing the content stream, because the raw
sample bytes are arbitrary and must not be lexed as operators. Two bounded strategies (§8.9.7):

* DETERMINABLE length — an UNFILTERED image with a known geometry: the data length is
  ``ceil(Width * components * BitsPerComponent / 8) * Height`` (each row byte-aligned, §8.9.3
  "Sample Representation"). ``components`` comes from the colour space (Table 93 abbreviations); an
  image mask is 1 component at 1 bit. We compute the length, then REQUIRE a whitespace-delimited
  ``EI`` exactly where the data ends. If ``EI`` is not there, the computed length disagrees with
  the stream, so we REFUSE (a typed :class:`SheetRefusal`) rather than guess.
* SCANNED length — a FILTERED image, or one whose geometry is not determinable (a named-resource
  colour space): the compressed length is not computable, so we scan forward for a
  whitespace-delimited ``EI`` under a byte cap. Over the cap, or no ``EI`` before the stream ends,
  is a typed refusal. (A binary ``<ws>EI<ws>`` inside filtered data could end the scan early; the
  reader never decodes the samples, so an early cut desynchronizes into a DOWNSTREAM typed refusal,
  never a silent wrong drawing — see the M5-T118 producer report.)

Doctrine (inherited from the sheet reader): refusal is a VALUE, never an exception; every bound is
declared; no byte is executed and no network is touched. Scalar tokens are lexed by the reused
strict :func:`app.documents.extraction.pdf_lexer.lex_primitive`; only ``[ ]`` arrays and the ``ID``
data marker are handled here. This module imports only downward (the strict lexer leaf +
:mod:`app.drawings.sheet_objects` for the shared refusal helper); the interpreter imports it.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.documents.extraction.pdf_lexer import (
    LexedToken,
    PdfName,
    PdfSyntaxError,
    lex_primitive,
)
from app.drawings.sheet_objects import _refuse
from app.drawings.sheet_primitives import SheetRefusal

__all__ = [
    "MAX_INLINE_IMAGE_DATA_BYTES",
    "MAX_INLINE_IMAGE_DICT_BYTES",
    "InlineImageSpan",
    "skip_inline_image",
]

# -- bounds (each over-limit is a typed refusal VALUE; threaded from the facade limits so patching
#    the facade constant still bites) ---------------------------------------------------------
MAX_INLINE_IMAGE_DICT_BYTES = 4_096        # abbreviated image dictionary span cap (BI..ID)
MAX_INLINE_IMAGE_DATA_BYTES = 8_388_608    # inline-image data cap (determinable len OR EI scan)

_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")
_OPEN_BRACKET = 0x5B   # '['
_CLOSE_BRACKET = 0x5D  # ']'
_LESS_THAN = 0x3C      # '<'  ('<<' opens a dictionary VALUE)
_GREATER_THAN = 0x3E   # '>'  ('>>' closes a dictionary VALUE)
_PERCENT = 0x25        # '%'
_CR = 0x0D
_LF = 0x0A
# §8.9.5.1 / Table 89 permitted /BitsPerComponent values (inline-image key alias in Table 92)
_VALID_BPC = frozenset({1, 2, 4, 8, 16})

# Sentinel for an array VALUE parsed only for dictionary balance (its contents never decide the
# data length: an array-valued colour space or a present /Filter both force the EI scan).
_ARRAY_VALUE = object()

# ISO 32000-1 §8.9.7 / §7.4.4: an inline image's /DP or /DecodeParms VALUE may be a decode-params
# DICTIONARY (the usual CCITTFax `/DP << /K -1 /Columns .. >>` or Flate-predictor shape), or an
# ARRAY of such dictionaries / nulls (one per filter). It carries decode parameters, NOT geometry,
# so it is consumed for BALANCE only: exactly ONE nested ``<< >>`` level, under the same dictionary
# byte cap, for these keys ONLY. A nested dictionary under any OTHER key, or a second nesting level,
# is a typed refusal; the samples are never decoded.
_DECODE_PARMS_KEYS = frozenset({"DP", "DecodeParms"})
_MAX_INLINE_DP_DICT_DEPTH = 1  # one nested << >> level for a /DP value; deeper nesting refuses
# Sentinel for a /DP dictionary VALUE parsed only for balance (contents never decide the length).
_DICT_VALUE = object()

# Table 92 key abbreviations -> the geometry keys this skip cares about. Only these decide the
# determinable-length arithmetic; every other key is parsed (for balance) and ignored.
_WIDTH_KEYS = frozenset({"W", "Width"})
_HEIGHT_KEYS = frozenset({"H", "Height"})
_BPC_KEYS = frozenset({"BPC", "BitsPerComponent"})
_CS_KEYS = frozenset({"CS", "ColorSpace"})
_FILTER_KEYS = frozenset({"F", "Filter"})
_IMAGEMASK_KEYS = frozenset({"IM", "ImageMask"})

# Table 93 colour-space abbreviations (+ full device/CIE names) -> component count. A colour space
# not listed here (e.g. a named /Properties resource, an ICCBased stream) has UNKNOWN components,
# so the image is treated as not-determinable and its data is located by the EI scan.
_COMPONENTS = {
    "G": 1, "DeviceGray": 1, "CalGray": 1,
    "RGB": 3, "DeviceRGB": 3, "CalRGB": 3, "Lab": 3,
    "CMYK": 4, "DeviceCMYK": 4,
    "I": 1, "Indexed": 1,
}


@dataclass(frozen=True)
class InlineImageSpan:
    """A skipped inline image (§8.9.7). ``end_offset`` is the index just past the closing ``EI``,
    so the scanner resumes with the operator that follows the image. ``determinable`` records
    whether the data length came from the geometry (True) or a whitespace-delimited ``EI`` scan
    (False); ``data_length`` is the located sample-byte count. No sample byte is ever decoded."""

    end_offset: int
    determinable: bool
    data_length: int


def skip_inline_image(
    data: bytes, start: int, *, max_dict_bytes: int, max_data_scan_bytes: int
) -> InlineImageSpan | SheetRefusal:
    """Skip a ``BI`` ... ``ID`` ... ``EI`` inline image whose ABBREVIATED dictionary begins at
    ``start`` (the byte just past the ``BI`` operator), returning an :class:`InlineImageSpan` (the
    offset just past ``EI``) or a typed :class:`SheetRefusal`. Never raises; never decodes samples;
    never desynchronizes silently (an undeterminable/over-cap/mismatched image is a refusal)."""
    parsed = _parse_dictionary(data, start, max_dict_bytes)
    if isinstance(parsed, SheetRefusal):
        return parsed
    dictionary, id_end = parsed  # id_end indexes the byte just past the ``ID`` keyword
    n = len(data)
    if id_end >= n or data[id_end] not in _WHITESPACE:
        return _refuse(
            "inline image", "ID is not followed by the required single whitespace byte (§8.9.7)"
        )
    data_start = id_end + 1  # the single whitespace after ID is consumed; samples begin here
    length = _determinable_length(dictionary)
    if isinstance(length, SheetRefusal):
        return length
    if length is not None:
        return _skip_determinable(data, data_start, length, max_data_scan_bytes)
    return _scan_for_ei(data, data_start, max_data_scan_bytes)


def _parse_dictionary(
    data: bytes, start: int, max_dict_bytes: int
) -> tuple[dict[str, object], int] | SheetRefusal:
    """Parse the abbreviated inline-image dictionary (§8.9.7) from ``start`` up to the ``ID``
    keyword, returning ``(dict, id_end)`` or a typed refusal. Keys are names; values are names,
    numbers, booleans, null, strings, ``[ ]`` arrays, or — for /DP // /DecodeParms ONLY — a single
    nested ``<< >>`` dictionary (or an array of such dictionaries / nulls). Bounded by
    ``max_dict_bytes``."""
    n = len(data)
    pos = start
    dictionary: dict[str, object] = {}
    pending_key: str | None = None
    while pos < n:
        if pos - start > max_dict_bytes:
            return _refuse(
                "inline image", f"inline-image dictionary over {max_dict_bytes} bytes"
            )
        pos = _skip_ws_comments(data, pos)
        if pos >= n:
            break
        byte = data[pos]
        if byte == _OPEN_BRACKET:  # an array VALUE (/Filter [/Fl], /D [0 1], /DP [<< >> null])
            if pending_key is None:
                return _refuse("inline image", "array where an inline-image key was expected")
            end = _skip_array(
                data, pos, max_dict_bytes - (pos - start),
                allow_dicts=_nested_dict_allowed(pending_key),
            )
            if isinstance(end, SheetRefusal):
                return end
            dictionary[pending_key] = _ARRAY_VALUE
            pending_key = None
            pos = end
            continue
        if byte == _LESS_THAN and pos + 1 < n and data[pos + 1] == _LESS_THAN:  # a '<<' dict VALUE
            if pending_key is None:
                return _refuse("inline image", "dictionary where an inline-image key was expected")
            if not _nested_dict_allowed(pending_key):
                return _refuse(
                    "inline image",
                    "a nested dictionary is only allowed as a /DP or /DecodeParms value",
                )
            end = _skip_dict(data, pos, max_dict_bytes - (pos - start))
            if isinstance(end, SheetRefusal):
                return end
            dictionary[pending_key] = _DICT_VALUE
            pending_key = None
            pos = end
            continue
        token = lex_primitive(data, pos)
        if isinstance(token, LexedToken):
            if pending_key is None:
                if not isinstance(token.value, PdfName):
                    return _refuse("inline image", "an inline-image key is not a name")
                pending_key = token.value.value
            else:
                dictionary[pending_key] = token.value
                pending_key = None
            pos = token.end_offset
            continue
        # a bare keyword the lexer rejects: only ``ID`` (the data marker) is valid here.
        word_end = pos
        while word_end < n and data[word_end] not in _WHITESPACE and (
            data[word_end] not in _DELIMITERS
        ):
            word_end += 1
        word = data[pos:word_end].decode("latin-1")
        if word == "ID":
            if pending_key is not None:
                return _refuse("inline image", "inline-image key with no value before ID")
            return dictionary, word_end
        return _refuse("inline image", "malformed inline-image dictionary before ID")
    return _refuse("inline image", "inline image has no ID marker before the stream ends")


def _determinable_length(dictionary: dict[str, object]) -> int | None | SheetRefusal:
    """The unfiltered inline-image data length from the geometry (§8.9.3 "Sample Representation"):
    ``ceil(Width * components * BitsPerComponent / 8) * Height`` with each row byte-aligned; or
    ``None`` when the length is NOT determinable (a filter is present, or the colour space /
    geometry is unknown) so the caller must scan for ``EI``; or a typed refusal on a present-but-
    invalid geometry value."""
    if _has_key(dictionary, _FILTER_KEYS):
        return None  # filtered: the compressed length is not computable from the geometry
    image_mask = _bool_value(dictionary, _IMAGEMASK_KEYS)
    if image_mask is True:
        components: int | None = 1
        bpc: int | None = 1  # §8.9.6.2: an image mask is 1 bit / 1 component
    else:
        components = _components(dictionary)
        bpc = _int_value(dictionary, _BPC_KEYS)
        if bpc is not None and bpc not in _VALID_BPC:
            return _refuse("inline image", f"/BitsPerComponent {bpc} is not 1, 2, 4, 8 or 16")
    width = _int_value(dictionary, _WIDTH_KEYS)
    height = _int_value(dictionary, _HEIGHT_KEYS)
    if components is None or bpc is None or width is None or height is None:
        return None  # some geometry input is unknown -> scan for EI instead of guessing
    if width < 1 or height < 1:
        return _refuse("inline image", "inline image has a non-positive /Width or /Height")
    row_bytes = (width * components * bpc + 7) // 8
    return row_bytes * height


def _skip_determinable(
    data: bytes, data_start: int, length: int, max_data_scan_bytes: int
) -> InlineImageSpan | SheetRefusal:
    """Skip ``length`` determinable data bytes, then REQUIRE a whitespace-delimited ``EI`` exactly
    where the data ends. A mismatch means the computed length disagrees with the stream, so we
    refuse rather than guess (never a silent desync)."""
    if length > max_data_scan_bytes:
        return _refuse(
            "inline image", f"inline-image data over {max_data_scan_bytes} bytes"
        )
    n = len(data)
    pos = data_start + length
    if pos > n:
        return _refuse("inline image", "inline-image data runs past the end of the stream")
    scan = _skip_ws_comments(data, pos)
    if not _ei_at(data, scan):
        return _refuse(
            "inline image",
            "the computed inline-image length does not end at a whitespace-delimited EI",
        )
    return InlineImageSpan(end_offset=scan + 2, determinable=True, data_length=length)


def _scan_for_ei(
    data: bytes, data_start: int, max_data_scan_bytes: int
) -> InlineImageSpan | SheetRefusal:
    """Locate the end of a not-determinable inline image by scanning for a whitespace-delimited
    ``EI`` under a byte cap (§8.9.7). Over the cap, or no ``EI`` before the stream ends, is a typed
    refusal — never an unbounded scan and never a guess."""
    n = len(data)
    limit = data_start + max_data_scan_bytes
    pos = data_start
    while pos < n:
        if pos > limit:
            return _refuse(
                "inline image",
                f"no whitespace-delimited EI within {max_data_scan_bytes} bytes",
            )
        if (
            data[pos] in _WHITESPACE
            and _ei_at(data, pos + 1)
        ):
            return InlineImageSpan(
                end_offset=pos + 3, determinable=False, data_length=pos - data_start
            )
        pos += 1
    return _refuse("inline image", "inline image is unterminated (no EI before the stream ends)")


def _ei_at(data: bytes, pos: int) -> bool:
    """True when ``EI`` sits at ``pos`` and is delimited by whitespace / a delimiter / EOF, so a
    stray ``EI`` inside a longer token (e.g. ``EIGHT``) does not falsely terminate the image."""
    n = len(data)
    if pos + 1 >= n or data[pos] != 0x45 or data[pos + 1] != 0x49:  # 'E' 'I'
        return False
    after = pos + 2
    return after >= n or data[after] in _WHITESPACE or data[after] in _DELIMITERS


def _nested_dict_allowed(key: str) -> bool:
    """Whether an inline-image key may carry a nested ``<< >>`` dictionary VALUE (or an array of
    them): ONLY /DP or /DecodeParms (§8.9.7 / §7.4.4). Any other key with a nested dictionary is a
    typed refusal. Kept a small module function so a mutation (allow-any / allow-none) can prove the
    /DP-only restriction is load-bearing without editing the tree."""
    return key in _DECODE_PARMS_KEYS


def _skip_array(
    data: bytes, start: int, remaining_bytes: int, *, allow_dicts: bool = False
) -> int | SheetRefusal:
    """Skip a bounded ``[ ... ]`` array VALUE (a filter, /Decode, or — when ``allow_dicts`` — a /DP
    array of decode-parameter dictionaries / nulls), returning the index just past ``]``. Nested
    arrays are refused (outside the inline-image subset); a nested ``<<`` is refused unless
    ``allow_dicts`` (the /DP case), and then only ONE dictionary level. Bounded by
    ``remaining_bytes`` so a runaway array cannot walk the whole stream."""
    n = len(data)
    pos = start + 1  # past '['
    while pos < n:
        if pos - start > remaining_bytes:
            return _refuse("inline image", "inline-image array value is too long")
        pos = _skip_ws_comments(data, pos)
        if pos >= n:
            break
        byte = data[pos]
        if byte == _CLOSE_BRACKET:
            return pos + 1
        if byte == _OPEN_BRACKET:
            return _refuse("inline image", "nested array in an inline-image value")
        if byte == _LESS_THAN and pos + 1 < n and data[pos + 1] == _LESS_THAN:  # a '<<' dict item
            if not allow_dicts:
                return _refuse(
                    "inline image", "a nested dictionary is only allowed in a /DP value array"
                )
            end = _skip_dict(data, pos, remaining_bytes - (pos - start))
            if isinstance(end, SheetRefusal):
                return end
            pos = end
            continue
        token = lex_primitive(data, pos)
        if isinstance(token, PdfSyntaxError):
            return _refuse("inline image", "malformed token in an inline-image array value")
        pos = token.end_offset
    return _refuse("inline image", "unclosed array in an inline-image value")


def _skip_dict(
    data: bytes, start: int, remaining_bytes: int, *, level: int = 1
) -> int | SheetRefusal:
    """Skip a balanced ``<< ... >>`` decode-parameters dictionary VALUE (a /DP or /DecodeParms
    value, §8.9.7 / §7.4.4) for BALANCE ONLY, returning the index just past ``>>``. Exactly ONE
    level: a nested ``<<`` beyond ``_MAX_INLINE_DP_DICT_DEPTH`` is a typed refusal; an array value
    inside is skipped for balance (scalars only, no dicts); every scalar is lexed and DISCARDED.
    Bounded by ``remaining_bytes``. Its contents never influence the skip (a /DP dict rides with a
    /F filter, which already forces the EI scan), and no sample byte is ever decoded."""
    n = len(data)
    pos = start + 2  # past '<<'
    while pos < n:
        if pos - start > remaining_bytes:
            return _refuse("inline image", "inline-image /DP dictionary is too long")
        pos = _skip_ws_comments(data, pos)
        if pos >= n:
            break
        byte = data[pos]
        if byte == _GREATER_THAN and pos + 1 < n and data[pos + 1] == _GREATER_THAN:
            return pos + 2  # past '>>'
        if byte == _OPEN_BRACKET:  # an array VALUE inside the /DP dict (e.g. a /Decode array)
            end = _skip_array(data, pos, remaining_bytes - (pos - start))
            if isinstance(end, SheetRefusal):
                return end
            pos = end
            continue
        if byte == _LESS_THAN and pos + 1 < n and data[pos + 1] == _LESS_THAN:  # a nested '<<'
            if level >= _MAX_INLINE_DP_DICT_DEPTH:
                return _refuse(
                    "inline image",
                    "an inline-image /DP value nests deeper than one dictionary level",
                )
            end = _skip_dict(data, pos, remaining_bytes - (pos - start), level=level + 1)
            if isinstance(end, SheetRefusal):
                return end
            pos = end
            continue
        token = lex_primitive(data, pos)
        if isinstance(token, PdfSyntaxError):
            return _refuse("inline image", "malformed token in an inline-image /DP dictionary")
        pos = token.end_offset
    return _refuse("inline image", "unclosed /DP dictionary in an inline-image value")


def _skip_ws_comments(data: bytes, pos: int) -> int:
    """Advance past whitespace and ``%`` comments (§7.2.3) between dictionary tokens."""
    n = len(data)
    while pos < n:
        byte = data[pos]
        if byte in _WHITESPACE:
            pos += 1
        elif byte == _PERCENT:
            pos += 1
            while pos < n and data[pos] not in (_CR, _LF):
                pos += 1
        else:
            return pos
    return pos


def _has_key(dictionary: dict[str, object], keys: frozenset[str]) -> bool:
    return any(key in dictionary for key in keys)


def _int_value(dictionary: dict[str, object], keys: frozenset[str]) -> int | None:
    for key in keys:
        if key in dictionary:
            value = dictionary[key]
            return value if type(value) is int else None
    return None


def _bool_value(dictionary: dict[str, object], keys: frozenset[str]) -> bool | None:
    for key in keys:
        if key in dictionary:
            value = dictionary[key]
            return value if isinstance(value, bool) else None
    return None


def _components(dictionary: dict[str, object]) -> int | None:
    """Component count from the inline-image colour space (Table 92), or ``None`` when the colour
    space is absent, an array/stream, or a name outside the known device/CIE set."""
    for key in _CS_KEYS:
        if key in dictionary:
            value = dictionary[key]
            if isinstance(value, PdfName):
                return _COMPONENTS.get(value.value)
            return None  # an array (e.g. Indexed base) or non-name -> not determinable here
    return None
