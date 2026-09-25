"""PDF 1.5+ cross-reference-stream and object-stream resolver for the architect
drawing-sheet profile (M5-T103, D-087 PKT-K / C1).

The reused strict object-table reader
(:func:`app.documents.extraction.pdf_xref.read_object_table`, shared READ-ONLY with the
accepted survey pipeline) implements exactly ONE classic ``xref`` section and refuses PDF
1.5+ cross-reference streams, hybrid-reference files, and ``/Prev`` chains by name. Every
real architect drawing in the corpus
(``docs/research/architect-corpus-reader-trial-2026-09.md`` items 1-6) uses a
cross-reference STREAM plus object streams, so the strict reader reads none of them.

This module is a SEPARATE, profile-level resolver that builds an equivalent
:class:`~app.documents.extraction.pdf_xref.PdfObjectTable` for those files WITHOUT widening
the shared reader (DB-055 (k)). It composes the strict reader's leaf parsers
(:func:`parse_indirect_object`, :func:`parse_object`) READ-ONLY and is invoked by the
:mod:`app.drawings.sheet_reader` facade only after the strict reader has refused a
cross-reference-stream-family file, so a classic-``xref`` file still takes the old path
unchanged.

Grammar implemented (ISO 32000-1):

* §7.5.8 cross-reference streams — ``/Type /XRef``, the ``/W`` field widths, ``/Index``
  subsections (default ``[0 /Size]``), entry types 0/1/2, and bounded ``/Prev`` chains with
  a cycle guard.
* §7.5.8.4 hybrid-reference files — a classic ``xref`` table whose trailer names a
  cross-reference stream via ``/XRefStm``; the stream's entries take precedence and the
  classic table's type-1 entries fill the rest.
* §7.5.7 object streams — ``/Type /ObjStm``, ``/N``, ``/First``; compressed objects are
  parsed at ``/First + offset`` and their generation number is 0.
* §7.4.4.4 predictors — the PNG predictors (10-15; per-row filter tag byte) real producers
  apply to xref streams; the TIFF predictor (2) is a typed refusal, not implemented here.

Every unsupported construct (encryption, other stream filters, the TIFF predictor, an
``/Extends`` object-stream chain, an indirect ``/Length``, a broken offset, an over-bound
document) is a typed refusal VALUE, never a guess and never an exception.

MANDATORY decompression guard (the accepted M5-T099 plan's PKT-K criterion): every
cross-reference and object stream is inflated by BOUNDED INCREMENTAL decompression (never an
unbounded :func:`zlib.decompress`), charged against the document-wide decoded-bytes budget
BEFORE each chunk is materialized, under an absolute inflated-bytes cap AND an
inflate-ratio guard; ``/Prev`` depth, the object-stream count, and each object stream's
``/N`` are bounded. Each guard has an in-process mutation that reddens (see
``tests/drawings/test_pdf_object_streams.py``).

Doctrine (inherited from the strict reader): refusal is a VALUE; untrusted input is bounded
on inflated bytes, inflate ratio, ``/Prev`` depth, object-stream count, ``/N``, per-stream
xref entries, and total objects; no byte is executed and no network is touched. This module
imports only downward (strict-reader leaf modules + :mod:`app.drawings.sheet_objects` /
:mod:`app.drawings.sheet_primitives`); the facade imports from it.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.documents.extraction.pdf_lexer import PdfName, PdfSyntaxError
from app.documents.extraction.pdf_objects import (
    PdfIndirectObject,
    PdfRef,
    PdfStream,
    parse_indirect_object,
    parse_object,
)
from app.documents.extraction.pdf_xref import (
    MAX_PDF_OBJECTS,
    STARTXREF_WINDOW_BYTES,
    PdfObjectTable,
)
from app.drawings.sheet_objects import (
    _preview,
    _refuse,
    _wrap_strict,
    apply_predictor,
    inflate_guarded,
)
from app.drawings.sheet_primitives import SheetRefusal

__all__ = [
    "MAX_INFLATED_STREAM_BYTES",
    "MAX_INFLATE_RATIO",
    "MAX_OBJSTM_OBJECTS",
    "MAX_OBJECT_STREAMS",
    "MAX_PREV_DEPTH",
    "MAX_XREF_ENTRIES",
    "ResolvedTable",
    "XREF_STREAM_FEATURES",
    "resolve_object_table",
]

# -- guard bounds (each over-limit is a typed refusal VALUE; read from the module at resolve
#    time via _ResolverLimits.from_globals so an in-process mutant that rebinds one of these
#    still bites the running resolve) ------------------------------------------------------
MAX_INFLATED_STREAM_BYTES = 8_388_608  # absolute inflated-bytes cap per xref/object stream
MAX_INFLATE_RATIO = 512                # inflated:compressed ratio guard (zip-bomb defence)
MAX_PREV_DEPTH = 32                    # §7.5.8.4 bounded /Prev (and /XRefStm) chain hops
MAX_OBJECT_STREAMS = 4096             # §7.5.7 distinct object streams decoded per document
MAX_OBJSTM_OBJECTS = 8192            # §7.5.7 /N compressed objects in one object stream
MAX_XREF_ENTRIES = 131_072          # entries decoded from one cross-reference stream

_MAX_FIELD_WIDTH = 8               # §7.5.8.2 max bytes for one /W field (big-endian int)
_WHITESPACE = b"\x00\t\n\x0c\r "

# The strict reader refuses these three cross-reference-stream-family features by name; the
# facade retries THIS resolver only for them, so any other strict refusal stands unchanged.
XREF_STREAM_FEATURES = frozenset(
    {"cross-reference stream", "hybrid-reference file", "incremental update chain"}
)

_TYPE_KEY = PdfName("Type")
_XREF = PdfName("XRef")
_OBJSTM = PdfName("ObjStm")
_W_KEY = PdfName("W")
_INDEX_KEY = PdfName("Index")
_SIZE_KEY = PdfName("Size")
_PREV_KEY = PdfName("Prev")
_ROOT_KEY = PdfName("Root")
_ENCRYPT_KEY = PdfName("Encrypt")
_XREFSTM_KEY = PdfName("XRefStm")
_N_KEY = PdfName("N")
_FIRST_KEY = PdfName("First")
_FILTER_KEY = PdfName("Filter")
_FLATE = PdfName("FlateDecode")
_DECODE_PARMS_KEY = PdfName("DecodeParms")


@dataclass(frozen=True)
class ResolvedTable:
    """A resolved PDF 1.5+ object table plus the decoded-byte total the resolve charged, so
    the facade can seed the content-stream decoder's budget with the SAME running total (the
    xref/object-stream and content-stream phases share one document-wide budget)."""

    table: PdfObjectTable
    decoded_bytes: int


@dataclass(frozen=True)
class _ResolverLimits:
    """Guard bounds captured from the module globals at resolve time (patch surface)."""

    max_inflated: int
    max_inflate_ratio: int
    max_prev_depth: int
    max_object_streams: int
    max_objstm_objects: int
    max_xref_entries: int
    max_total_decoded: int

    @classmethod
    def from_globals(cls, max_total_decoded: int) -> _ResolverLimits:
        return cls(
            max_inflated=MAX_INFLATED_STREAM_BYTES,
            max_inflate_ratio=MAX_INFLATE_RATIO,
            max_prev_depth=MAX_PREV_DEPTH,
            max_object_streams=MAX_OBJECT_STREAMS,
            max_objstm_objects=MAX_OBJSTM_OBJECTS,
            max_xref_entries=MAX_XREF_ENTRIES,
            max_total_decoded=max_total_decoded,
        )


class _DecodeBudget:
    """Document-wide decoded-bytes budget, charged BEFORE each inflated chunk is retained so
    the running total can never overshoot the cap (DB-064 (d): no post-increment overshoot).
    The facade seeds a :class:`~app.drawings.sheet_objects._StreamDecoder` with ``used`` so
    the later content-stream decoding continues against the same cap."""

    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.used = 0

    def charge(self, count: int) -> SheetRefusal | None:
        if self.used + count > self.cap:
            return _refuse(
                "decoded bytes budget",
                f"over {self.cap} decoded bytes across the document",
            )
        self.used += count
        return None


# ================================================================================ entry API


def resolve_object_table(
    data: bytes, *, max_total_decoded_bytes: int
) -> ResolvedTable | SheetRefusal | None:
    """Resolve a PDF 1.5+ cross-reference-stream / hybrid file into a
    :class:`~app.documents.extraction.pdf_xref.PdfObjectTable`.

    Returns a :class:`ResolvedTable` on success, a :class:`SheetRefusal` VALUE for any
    unsupported construct or bound, or ``None`` when the file is not one this resolver
    handles (so the caller keeps the strict reader's original refusal). Never raises;
    ``max_total_decoded_bytes`` is threaded from the facade so patching the facade constant
    still bounds this resolve.
    """
    offset = _locate_startxref(data)
    if offset is None:
        return None
    kind = _classify(data, offset)
    if kind is None:
        return None
    limits = _ResolverLimits.from_globals(max_total_decoded_bytes)
    budget = _DecodeBudget(max_total_decoded_bytes)
    if kind == "stream":
        result = _resolve_stream_chain(data, offset, limits, budget)
    else:  # "classic" -> only a /XRefStm hybrid is handled; anything else defers (None)
        result = _resolve_hybrid(data, offset, limits, budget)
    return result


def _locate_startxref(data: bytes) -> int | None:
    """Return the byte offset named by the last ``startxref`` in the final window, or None."""
    window = max(0, len(data) - STARTXREF_WINDOW_BYTES)
    idx = data.rfind(b"startxref", window)
    if idx == -1:
        return None
    pos = _skip_ws(data, idx + 9)
    start = pos
    while pos < len(data) and 0x30 <= data[pos] <= 0x39:
        pos += 1
    if pos == start or pos - start > 10:
        return None
    return int(data[start:pos])


def _classify(data: bytes, offset: int) -> str | None:
    """'stream' if ``offset`` begins an ``N G obj`` header (a cross-reference stream),
    'classic' if it begins an ``xref`` keyword (classic table / hybrid), else None."""
    if offset < 0 or offset >= len(data):
        return None
    if data[offset : offset + 4] == b"xref" and (
        offset + 4 >= len(data) or data[offset + 4] in _WHITESPACE
    ):
        return "classic"
    if 0x30 <= data[offset] <= 0x39:
        return "stream"
    return None


# ============================================================== cross-reference stream chain


def _resolve_stream_chain(
    data: bytes, offset: int, limits: _ResolverLimits, budget: _DecodeBudget
) -> ResolvedTable | SheetRefusal:
    collected = _collect_stream_entries(data, offset, limits, budget)
    if isinstance(collected, SheetRefusal):
        return collected
    entries_map, trailer, _seen = collected
    return _materialize(data, entries_map, trailer, limits, budget)


def _collect_stream_entries(
    data: bytes, first_offset: int, limits: _ResolverLimits, budget: _DecodeBudget
) -> tuple[dict, dict, set] | SheetRefusal:
    """Follow the ``/Prev`` chain from ``first_offset``, newest first. Return the merged
    entry map (first-seen object number wins, including a free entry that deletes it), the
    NEWEST stream's trailer dict, and the set of every object number the chain mentioned."""
    entries_map: dict[int, tuple[int, int, int]] = {}
    seen: set[int] = set()
    trailer: dict | None = None
    visited: set[int] = set()
    depth = 0
    cur: int | None = first_offset
    while cur is not None:
        if depth > limits.max_prev_depth:
            return _refuse("xref /Prev depth", f"/Prev chain over {limits.max_prev_depth} hops")
        if cur in visited:
            return _refuse("xref /Prev cycle", f"/Prev returns to offset {cur}")
        visited.add(cur)
        one = _read_one_xref_stream(data, cur, limits, budget)
        if isinstance(one, SheetRefusal):
            return one
        dct, entries, prev = one
        if trailer is None:
            trailer = dct
        for number, entry_type, field2, field3 in entries:
            if number in seen:
                continue
            seen.add(number)
            if entry_type in (1, 2):
                entries_map[number] = (entry_type, field2, field3)
        cur = prev
        depth += 1
    if trailer is None:  # unreachable (first_offset always yields a stream) - stay total
        return _refuse("xref stream", "no cross-reference stream found")
    return (entries_map, trailer, seen)


def _read_one_xref_stream(
    data: bytes, offset: int, limits: _ResolverLimits, budget: _DecodeBudget
) -> tuple[dict, list, int | None] | SheetRefusal:
    """Parse and decode ONE cross-reference stream at ``offset``. Return its trailer dict,
    its decoded entries as ``(object_number, type, field2, field3)``, and its ``/Prev``."""
    parsed = parse_indirect_object(data, offset)
    if isinstance(parsed, PdfSyntaxError):
        return _wrap_strict(parsed)
    indirect = parsed.value
    if not isinstance(indirect, PdfIndirectObject) or not isinstance(indirect.value, PdfStream):
        return _refuse("xref stream", "startxref target is not an indirect stream object")
    stream = indirect.value
    dct = stream.dictionary
    if dct.get(_TYPE_KEY) != _XREF:
        return _refuse("xref stream", "cross-reference stream /Type is not /XRef")
    if _ENCRYPT_KEY in dct:
        return _refuse("encryption", "/Encrypt present; encrypted documents are refused")
    size = _dint(dct, _SIZE_KEY)
    if size is None or size < 0:
        return _refuse("xref stream", "/Size is not a non-negative integer")
    widths = _read_w(dct)
    if isinstance(widths, SheetRefusal):
        return widths
    index = _read_index(dct, size)
    if isinstance(index, SheetRefusal):
        return index
    decoded = _decode_stream(stream, dct, limits, budget)
    if isinstance(decoded, SheetRefusal):
        return decoded
    entries = _parse_entries(decoded, widths, index, limits)
    if isinstance(entries, SheetRefusal):
        return entries
    prev: int | None = None
    if _PREV_KEY in dct:
        prev = _dint(dct, _PREV_KEY)
        if prev is None or prev < 0:
            return _refuse("xref stream", "/Prev is not a non-negative integer")
    return (dct, entries, prev)


def _read_w(dct: dict) -> tuple[int, int, int] | SheetRefusal:
    """Read the required ``/W`` field widths: exactly three integers, the middle one
    positive, none over the byte-width bound (§7.5.8.2)."""
    raw = dct.get(_W_KEY)
    if not isinstance(raw, list) or len(raw) != 3:
        return _refuse("xref stream", "/W is not an array of three integers")
    out: list[int] = []
    for element in raw:
        if type(element) is not int or element < 0 or element > _MAX_FIELD_WIDTH:
            return _refuse("xref stream", "/W element is not a bounded non-negative integer")
        out.append(element)
    if out[1] < 1 or out[0] + out[1] + out[2] == 0:
        return _refuse("xref stream", "/W field widths are degenerate")
    return (out[0], out[1], out[2])


def _read_index(dct: dict, size: int) -> list[int] | SheetRefusal:
    """Read the optional ``/Index`` subsection pairs; default ``[0 /Size]`` (§7.5.8.2)."""
    raw = dct.get(_INDEX_KEY)
    if raw is None:
        return [0, size]
    if not isinstance(raw, list) or len(raw) == 0 or len(raw) % 2 != 0:
        return _refuse("xref stream", "/Index is not an even-length array")
    for element in raw:
        if type(element) is not int or element < 0:
            return _refuse("xref stream", "/Index contains a non-integer")
    return raw


def _parse_entries(
    decoded: bytes, widths: tuple[int, int, int], index: list[int], limits: _ResolverLimits
) -> list[tuple[int, int, int, int]] | SheetRefusal:
    """Decode the fixed-width entry table into ``(object_number, type, field2, field3)``.

    A zero-width field takes its §7.5.8.2 default: type field -> 1, third field -> 0."""
    w0, w1, w2 = widths
    entry_width = w0 + w1 + w2
    if len(decoded) % entry_width != 0:
        return _refuse("xref stream", "decoded entries are not a whole multiple of the width")
    rows = len(decoded) // entry_width
    if rows > limits.max_xref_entries:
        return _refuse("xref stream", f"over {limits.max_xref_entries} cross-reference entries")
    total = sum(index[i] for i in range(1, len(index), 2))
    if total != rows:
        return _refuse("xref stream", "/Index subsection counts do not match the entry table")
    out: list[tuple[int, int, int, int]] = []
    pos = 0
    for sub in range(0, len(index), 2):
        start, count = index[sub], index[sub + 1]
        for k in range(count):
            field1 = int.from_bytes(decoded[pos : pos + w0], "big") if w0 else 1
            field2 = int.from_bytes(decoded[pos + w0 : pos + w0 + w1], "big")
            field3 = int.from_bytes(decoded[pos + w0 + w1 : pos + entry_width], "big") if w2 else 0
            out.append((start + k, field1, field2, field3))
            pos += entry_width
    return out


# ============================================================================= hybrid files


def _resolve_hybrid(
    data: bytes, offset: int, limits: _ResolverLimits, budget: _DecodeBudget
) -> ResolvedTable | SheetRefusal | None:
    """Resolve a §7.5.8.4 hybrid file: a classic ``xref`` table whose trailer names a
    cross-reference stream via ``/XRefStm``. The stream's entries take precedence; the
    classic type-1 entries fill objects the stream did not mention. A classic table without
    ``/XRefStm`` is not handled here (returns None -> the strict refusal stands)."""
    classic = _read_classic_table(data, offset)
    if classic is None or isinstance(classic, SheetRefusal):
        return classic
    class_entries, trailer = classic
    if _ENCRYPT_KEY in trailer:
        return _refuse("encryption", "/Encrypt present; encrypted documents are refused")
    if _XREFSTM_KEY not in trailer:
        return None
    xrefstm = _dint(trailer, _XREFSTM_KEY)
    if xrefstm is None or xrefstm < 0:
        return _refuse("hybrid xref", "/XRefStm is not a non-negative integer")
    collected = _collect_stream_entries(data, xrefstm, limits, budget)
    if isinstance(collected, SheetRefusal):
        return collected
    entries_map, _stream_trailer, seen = collected
    for number, generation, entry_offset in class_entries:
        if number in seen:
            continue
        seen.add(number)
        entries_map[number] = (1, entry_offset, generation)
    return _materialize(data, entries_map, trailer, limits, budget)


def _read_classic_table(
    data: bytes, offset: int
) -> tuple[list[tuple[int, int, int]], dict] | SheetRefusal | None:
    """Read a classic ``xref`` table's in-use entries and trailer dict (a compact,
    module-local reader; it never widens the shared strict reader). Return None if the bytes
    are not a parseable classic table (defer to the strict refusal)."""
    pos = _skip_ws(data, offset + 4)
    in_use: list[tuple[int, int, int]] = []
    while True:
        pos = _skip_ws(data, pos)
        if data[pos : pos + 7] == b"trailer":
            parsed = parse_object(data, pos + 7)
            if isinstance(parsed, PdfSyntaxError):
                return _wrap_strict(parsed)
            if not isinstance(parsed.value, dict):
                return _refuse("classic xref", "trailer is not a dictionary")
            return (in_use, parsed.value)
        header = _read_two_uints(data, pos)
        if header is None:
            return None
        start, count, pos = header
        for k in range(count):
            entry = data[pos : pos + 20]
            if len(entry) < 20 or not (
                entry[0:10].isdigit() and entry[11:16].isdigit() and entry[17] in b"nf"
            ):
                return _refuse("classic xref", "malformed 20-byte xref entry")
            if entry[17] == 0x6E:  # 'n' in-use
                in_use.append((start + k, int(entry[11:16]), int(entry[0:10])))
            pos += 20


def _read_two_uints(data: bytes, pos: int) -> tuple[int, int, int] | None:
    """Read a ``start count`` subsection header line; return (start, count, next_pos)."""
    first = _read_uint(data, pos)
    if first is None:
        return None
    start, pos = first
    if pos >= len(data) or data[pos] != 0x20:
        return None
    pos += 1
    second = _read_uint(data, pos)
    if second is None:
        return None
    count, pos = second
    while pos < len(data) and data[pos] in b" \r\n":
        pos += 1
    return (start, count, pos)


def _read_uint(data: bytes, pos: int) -> tuple[int, int] | None:
    end = pos
    while end < len(data) and 0x30 <= data[end] <= 0x39:
        end += 1
    if end == pos or end - pos > 10:
        return None
    return (int(data[pos:end]), end)


# =================================================================== object materialization


def _materialize(
    data: bytes,
    entries_map: dict[int, tuple[int, int, int]],
    trailer: dict,
    limits: _ResolverLimits,
    budget: _DecodeBudget,
) -> ResolvedTable | SheetRefusal:
    """Materialise every in-use object named by the merged entry map into a
    :class:`PdfObjectTable`: type-1 objects at their byte offset, type-2 objects out of
    their (bounded, once-decoded) object stream."""
    if _ENCRYPT_KEY in trailer:
        return _refuse("encryption", "/Encrypt present; encrypted documents are refused")
    if not isinstance(trailer.get(_ROOT_KEY), PdfRef):
        return _refuse("trailer", "trailer /Root is not an indirect reference")
    if len(entries_map) > MAX_PDF_OBJECTS:
        return _refuse("object count bound", f"over {MAX_PDF_OBJECTS} in-use objects")
    objects: dict[tuple[int, int], object] = {}
    objstm_cache: dict[int, tuple[bytes, int, list[tuple[int, int]]]] = {}
    for number in sorted(entries_map):
        entry_type, field2, field3 = entries_map[number]
        if entry_type == 1:
            materialized = _materialize_uncompressed(data, number, field2, field3)
        else:
            materialized = _materialize_compressed(
                data, number, field2, field3, entries_map, objstm_cache, limits, budget
            )
        if isinstance(materialized, SheetRefusal):
            return materialized
        key, value = materialized
        objects[key] = value
    return ResolvedTable(PdfObjectTable(trailer=trailer, objects=objects), budget.used)


def _materialize_uncompressed(
    data: bytes, number: int, offset: int, generation: int
) -> tuple[tuple[int, int], object] | SheetRefusal:
    parsed = parse_indirect_object(data, offset)
    if isinstance(parsed, PdfSyntaxError):
        return _wrap_strict(parsed)
    indirect = parsed.value
    if not isinstance(indirect, PdfIndirectObject):
        return _refuse("object", f"object {number} did not parse to an indirect object")
    if (indirect.number, indirect.generation) != (number, generation):
        return _refuse(
            "object identity",
            f"xref says {number} {generation} but the object at its offset is"
            f" {indirect.number} {indirect.generation}",
        )
    return ((number, generation), indirect.value)


def _materialize_compressed(
    data: bytes,
    number: int,
    objstm_number: int,
    index: int,
    entries_map: dict[int, tuple[int, int, int]],
    objstm_cache: dict[int, tuple[bytes, int, list[tuple[int, int]]]],
    limits: _ResolverLimits,
    budget: _DecodeBudget,
) -> tuple[tuple[int, int], object] | SheetRefusal:
    if objstm_number not in objstm_cache:
        container = entries_map.get(objstm_number)
        if container is None or container[0] != 1:
            return _refuse(
                "object stream", f"object stream {objstm_number} is not an in-use type-1 object"
            )
        if len(objstm_cache) >= limits.max_object_streams:
            return _refuse(
                "object stream count", f"over {limits.max_object_streams} object streams"
            )
        loaded = _load_object_stream(data, container[1], limits, budget)
        if isinstance(loaded, SheetRefusal):
            return loaded
        objstm_cache[objstm_number] = loaded
    decoded, first, header = objstm_cache[objstm_number]
    if index < 0 or index >= len(header):
        return _refuse("object stream", f"compressed index {index} is out of range")
    header_number, local_offset = header[index]
    if header_number != number:
        return _refuse(
            "object identity",
            f"object stream slot {index} holds object {header_number}, not {number}",
        )
    parsed = parse_object(decoded, first + local_offset)
    if isinstance(parsed, PdfSyntaxError):
        return _wrap_strict(parsed)
    return ((number, 0), parsed.value)  # §7.5.7: compressed objects have generation 0


def _load_object_stream(
    data: bytes, offset: int, limits: _ResolverLimits, budget: _DecodeBudget
) -> tuple[bytes, int, list[tuple[int, int]]] | SheetRefusal:
    """Decode a ``/Type /ObjStm`` stream and parse its ``/N`` header pairs (§7.5.7)."""
    parsed = parse_indirect_object(data, offset)
    if isinstance(parsed, PdfSyntaxError):
        return _wrap_strict(parsed)
    indirect = parsed.value
    if not isinstance(indirect, PdfIndirectObject) or not isinstance(indirect.value, PdfStream):
        return _refuse("object stream", "object stream is not an indirect stream object")
    stream = indirect.value
    dct = stream.dictionary
    if dct.get(_TYPE_KEY) != _OBJSTM:
        return _refuse("object stream", "object stream /Type is not /ObjStm")
    # /Extends (§7.5.7) only records the numbering-order relationship to a base object stream;
    # it never changes which objects THIS stream's own header describes, and every compressed
    # object is reached by the xref type-2 entry's direct (objstm, index) pair, checked against
    # this stream's header below. It is therefore safe to ignore for random-access resolution.
    count = _dint(dct, _N_KEY)
    first = _dint(dct, _FIRST_KEY)
    if count is None or first is None or count < 0 or first < 0:
        return _refuse("object stream", "/N or /First is not a non-negative integer")
    if count > limits.max_objstm_objects:
        return _refuse("object stream", f"/N over {limits.max_objstm_objects} objects")
    decoded = _decode_stream(stream, dct, limits, budget)
    if isinstance(decoded, SheetRefusal):
        return decoded
    if first > len(decoded):
        return _refuse("object stream", "/First is past the decoded object-stream end")
    header: list[tuple[int, int]] = []
    pos = 0
    for _ in range(count):
        number_token = parse_object(decoded, pos)
        if isinstance(number_token, PdfSyntaxError) or type(number_token.value) is not int:
            return _refuse("object stream", "object-stream header is not integer pairs")
        offset_token = parse_object(decoded, number_token.end_offset)
        if isinstance(offset_token, PdfSyntaxError) or type(offset_token.value) is not int:
            return _refuse("object stream", "object-stream header is not integer pairs")
        if offset_token.value < 0 or first + offset_token.value > len(decoded):
            return _refuse("object stream", "an object-stream offset is out of range")
        header.append((number_token.value, offset_token.value))
        pos = offset_token.end_offset
        if pos > first:
            return _refuse("object stream", "object-stream header overruns /First")
    return (decoded, first, header)


# =============================================================== stream decode (guard + PNG)


def _decode_stream(
    stream: PdfStream, dct: dict, limits: _ResolverLimits, budget: _DecodeBudget
) -> bytes | SheetRefusal:
    """Decode a cross-reference / object stream: single ``/FlateDecode`` (or absent) under the
    shared bounded incremental guard, then the §7.4.4.4 predictor from ``/DecodeParms``. The
    inflation and predictor primitives live in :mod:`app.drawings.sheet_objects` (the decode
    module); this composes them under the resolver's patchable bounds."""
    filt = dct.get(_FILTER_KEY)
    if isinstance(filt, list):
        if len(filt) != 1:
            return _refuse("stream filter array", f"/Filter is an array of {len(filt)}")
        filt = filt[0]
    if filt is None:
        raw = stream.raw_data
        if len(raw) > limits.max_inflated:
            return _refuse("inflated bytes cap", f"raw stream over {limits.max_inflated} bytes")
        charged = budget.charge(len(raw))
        if charged is not None:
            return charged
        decoded: bytes = raw
    elif filt == _FLATE:
        result = inflate_guarded(
            stream.raw_data,
            absolute_cap=limits.max_inflated,
            ratio_multiplier=limits.max_inflate_ratio,
            charge=budget.charge,
        )
        if isinstance(result, SheetRefusal):
            return result
        decoded = result
    else:
        name = filt.value if isinstance(filt, PdfName) else repr(filt)
        return _refuse(
            "stream filter", f"/Filter /{_preview(name)} is outside the supported subset"
        )
    parms = dct.get(_DECODE_PARMS_KEY)
    if isinstance(parms, list):
        if len(parms) != 1:
            return _refuse("decode parameters", f"/DecodeParms is an array of {len(parms)}")
        parms = parms[0]
    if not isinstance(parms, dict):
        return decoded
    return apply_predictor(decoded, parms)


# ================================================================================== helpers


def _dint(dct: dict, key: PdfName, default: int | None = None) -> int | None:
    """A DIRECT non-bool integer at ``key`` (all structural xref/objstm values are direct),
    else ``default`` when the key is absent or None when it is present but not an integer."""
    if key not in dct:
        return default
    value = dct[key]
    return value if type(value) is int else None


def _skip_ws(data: bytes, pos: int) -> int:
    while pos < len(data) and data[pos] in _WHITESPACE:
        pos += 1
    return pos
