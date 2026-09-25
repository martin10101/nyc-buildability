"""Object-graph resolution + stream decoding for the architect drawing-sheet profile
(M5-T094 split of the M5-T083 reader; DB-055 b). NO behaviour change.

This module owns the *document/object-graph* half of the reader profile: following
indirect references through the reused strict reader's object table, decoding a single
content/form stream under the strict single-``/FlateDecode`` subset, joining a page's
``/Contents``, memoizing decoded Form XObject bytes, charging the document-wide
decoded-bytes budget, reading a page's ``/MediaBox`` and finding the catalog's page
root, plus the profile's uniform refusal helpers. The operator interpreter (graphics /
text state, path construction, form placement) lives in
:mod:`app.drawings.sheet_interpreter`; the public entry, its bounds/backstop, and the
page-tree driver live in the compatibility facade :mod:`app.drawings.sheet_reader`.

Doctrine (inherited from the strict reader): refusal is a VALUE, never an exception;
untrusted input is bounded on stream size and per-document decoded bytes; no byte is
executed and no network is touched. This module imports only downward
(strict-reader leaf modules + :mod:`app.drawings.sheet_primitives`); the interpreter
and facade import from it.
"""

from __future__ import annotations

import zlib

from app.documents.extraction.pdf_lexer import PdfName, PdfSyntaxError
from app.documents.extraction.pdf_objects import PdfRef, PdfStream
from app.documents.extraction.pdf_xref import PdfObjectTable, UnsupportedPdfFeature
from app.drawings.sheet_primitives import SheetRefusal

# -- decode bounds (each over-limit is a typed refusal VALUE) -----------------------------
MAX_DECODED_STREAM_BYTES = 8_388_608  # decoded content/form-stream byte cap (per stream)
MAX_TOTAL_DECODED_BYTES = 134_217_728  # decoded bytes charged across the whole document
_DETAIL_PREVIEW_CHARS = 64  # attacker-derived tokens are truncated to this in a detail
_INFLATE_CHUNK = 65536  # bounded incremental-inflation chunk (caps materialized memory)

_ROOT_KEY = PdfName("Root")
_TYPE_KEY = PdfName("Type")
_CATALOG = PdfName("Catalog")
_PAGES = PdfName("Pages")
_PAGE = PdfName("Page")
_KIDS_KEY = PdfName("Kids")
_MEDIA_BOX_KEY = PdfName("MediaBox")
_CONTENTS_KEY = PdfName("Contents")
_RESOURCES_KEY = PdfName("Resources")
_USER_UNIT_KEY = PdfName("UserUnit")
_XOBJECT_KEY = PdfName("XObject")
_SUBTYPE_KEY = PdfName("Subtype")
_FORM = PdfName("Form")
_IMAGE = PdfName("Image")
_MATRIX_KEY = PdfName("Matrix")
_WIDTH_KEY = PdfName("Width")
_HEIGHT_KEY = PdfName("Height")
_BPC_KEY = PdfName("BitsPerComponent")
_COLORSPACE_KEY = PdfName("ColorSpace")
_FILTER_KEY = PdfName("Filter")
_DECODE_PARMS_KEY = PdfName("DecodeParms")
_FLATE = PdfName("FlateDecode")
_PREDICTOR_KEY = PdfName("Predictor")
_COLUMNS_KEY = PdfName("Columns")
_COLORS_KEY = PdfName("Colors")

_MAX_RESOLVE_HOPS = 32
_ABSENT = object()


# ================================================================================ refusals


def _wrap_strict(refusal: PdfSyntaxError | UnsupportedPdfFeature) -> SheetRefusal:
    """Wrap a strict-reader refusal value in the profile's uniform refusal type."""
    if isinstance(refusal, PdfSyntaxError):
        return SheetRefusal(
            reject_code=PdfSyntaxError.reject_code,
            feature="malformed pdf",
            detail=f"offset {refusal.offset}: expected {refusal.expected}, found {refusal.found}",
            origin=SheetRefusal.STRICT_READER,
        )
    return SheetRefusal(
        reject_code=refusal.reject_code,
        feature=refusal.feature,
        detail=refusal.detail,
        origin=SheetRefusal.STRICT_READER,
    )


def _refuse(feature: str, detail: str) -> SheetRefusal:
    """A profile-owned refusal value (a bound, cycle, or unsupported construct)."""
    return SheetRefusal(
        reject_code="sheet_reader_refusal",
        feature=feature,
        detail=detail,
        origin=SheetRefusal.SHEET_PROFILE,
    )


def _preview(token: str) -> str:
    """Bound an attacker-derived token to a short preview for a refusal detail, so a
    hostile input cannot inflate ``detail`` to the full decoded-stream size (§ G5 F5)."""
    if len(token) <= _DETAIL_PREVIEW_CHARS:
        return token
    return token[:_DETAIL_PREVIEW_CHARS] + "...(truncated)"


def sheet_refusal(result: object) -> SheetRefusal | None:
    """Return the :class:`SheetRefusal` carried by a read result, else None."""
    return result if isinstance(result, SheetRefusal) else None


# ============================================================================ object graph


def _resolve(table: PdfObjectTable, value: object) -> object | SheetRefusal:
    """Follow indirect references through the object table under a hop bound; refuse a
    missing target or a reference cycle."""
    hops = 0
    while isinstance(value, PdfRef):
        if hops >= _MAX_RESOLVE_HOPS:
            return _refuse("reference chain", f"over {_MAX_RESOLVE_HOPS} hops from a reference")
        hops += 1
        key = (value.number, value.generation)
        if key not in table.objects:
            return _refuse(
                "unresolvable reference",
                f"object {value.number} {value.generation} is not in the object table",
            )
        value = table.objects[key]
    return value


def _resolved_int(table: PdfObjectTable, value: object) -> int | None:
    resolved = _resolve(table, value)
    return resolved if isinstance(resolved, int) and not isinstance(resolved, bool) else None


def _decode_stream(
    table: PdfObjectTable, stream: PdfStream, decoder: _StreamDecoder
) -> bytes | SheetRefusal:
    """Decode a content/form stream under the strict single-``/FlateDecode`` subset;
    refuse ``/DecodeParms``, filter arrays, other filters, corrupt deflate, or over-cap
    output. Mirrors the container's decode doctrine without mutating it. EVERY decode charges
    the document-wide decoded-bytes budget (``decoder.charge_decoded``), so many small decodes
    (e.g. repeated Form ``Do``) cannot amplify total decompression without bound.

    ``decoder`` supplies the (facade-threaded, hence patchable) per-stream and document byte
    caps and the charge counter; keeping the ``(table, stream, decoder)`` signature preserves
    the in-process mutant seam the existing suite relies on."""
    dictionary = stream.dictionary
    cap = decoder.max_decoded_stream_bytes
    if _DECODE_PARMS_KEY in dictionary:
        return _refuse("decode parameters", "stream carries /DecodeParms (unsupported)")
    if _FILTER_KEY not in dictionary:
        raw = stream.raw_data
        if len(raw) > cap:
            return _refuse("stream size", f"raw stream over {cap} bytes")
        charged = decoder.charge_decoded(len(raw))
        return charged if charged is not None else raw
    filter_value = _resolve(table, dictionary[_FILTER_KEY])
    if isinstance(filter_value, SheetRefusal):
        return filter_value
    if isinstance(filter_value, list):
        return _refuse("stream filter array", f"/Filter is an array of {len(filter_value)}")
    if filter_value != _FLATE:
        name = filter_value.value if isinstance(filter_value, PdfName) else repr(filter_value)
        return _refuse(
            "stream filter", f"/Filter /{_preview(name)} is outside the supported subset"
        )
    decompressor = zlib.decompressobj()
    try:
        decoded = decompressor.decompress(stream.raw_data, cap)
    except zlib.error as error:
        return _refuse("corrupt flate stream", f"zlib refused the stream: {error}")
    if decompressor.unconsumed_tail or not decompressor.eof:
        return _refuse("flate output bound", f"flate output over {cap} bytes")
    charged = decoder.charge_decoded(len(decoded))
    return charged if charged is not None else decoded


def _media_box(
    table: PdfObjectTable, raw: object
) -> tuple[float, float, float, float] | SheetRefusal:
    if raw is _ABSENT:
        return _refuse("media box", "no /MediaBox on the page or any ancestor")
    box = _resolve(table, raw)
    if isinstance(box, SheetRefusal):
        return box
    if not isinstance(box, list) or len(box) != 4:
        return _refuse("media box", "/MediaBox is not an array of exactly 4 numbers")
    numbers: list[float] = []
    for element in box:
        resolved = _resolve(table, element)
        if isinstance(resolved, SheetRefusal):
            return resolved
        if not isinstance(resolved, (int, float)) or isinstance(resolved, bool):
            return _refuse("media box", "/MediaBox contains a non-number")
        numbers.append(float(resolved))
    return (numbers[0], numbers[1], numbers[2], numbers[3])


def _catalog_pages_root(table: PdfObjectTable) -> object | SheetRefusal:
    catalog = _resolve(table, table.trailer[_ROOT_KEY])
    if isinstance(catalog, SheetRefusal):
        return catalog
    if not isinstance(catalog, dict):
        return _refuse("catalog", "trailer /Root does not resolve to a dictionary")
    if _TYPE_KEY not in catalog:
        return _refuse("catalog", "document catalog has no /Type")
    catalog_type = _resolve(table, catalog[_TYPE_KEY])
    if catalog_type != _CATALOG:
        return _refuse("catalog", "document catalog /Type is not /Catalog")
    if _PAGES not in catalog:
        return _refuse("catalog", "document catalog has no /Pages")
    return catalog[_PAGES]


# ==================================================================== decode budget + memo


class _StreamDecoder:
    """Document-wide stream-decode coordinator: the decoded-bytes budget and the Form
    XObject decode memo (DB-055 b: "decode budgets, form memo").

    ONE instance per document is shared across pages AND nested Form recursion, so the
    ``decoded_bytes`` accounting and the per-``(number, generation)`` form cache bound the
    whole read. ``_decode_stream`` is the (facade-threaded, patchable) decode hook; the byte
    caps are likewise threaded so patching the facade constants still bites."""

    def __init__(
        self,
        table: PdfObjectTable,
        *,
        max_decoded_stream_bytes: int,
        max_total_decoded_bytes: int,
        decode_stream,
        decoded_bytes: int = 0,
    ) -> None:
        self.table = table
        self.max_decoded_stream_bytes = max_decoded_stream_bytes
        self.max_total_decoded_bytes = max_total_decoded_bytes
        self._decode_stream = decode_stream  # patchable hook (facade sheet_reader._decode_stream)
        # document-wide; seeded with the bytes a PDF 1.5+ xref/object-stream resolve already
        # charged, so the two phases share ONE decoded-bytes budget (M5-T103).
        self.decoded_bytes = decoded_bytes
        self.form_cache: dict[tuple[int, int], bytes] = {}  # decoded Form content by ref key

    def charge_decoded(self, count: int) -> SheetRefusal | None:
        """Charge ``count`` bytes against the document-wide decoded-bytes budget; refuse
        once the running total would exceed the (threaded) total cap."""
        self.decoded_bytes += count
        if self.decoded_bytes > self.max_total_decoded_bytes:
            return _refuse(
                "decoded bytes budget",
                f"over {self.max_total_decoded_bytes} decoded bytes across the document",
            )
        return None

    def decode_stream(self, stream: PdfStream) -> bytes | SheetRefusal:
        """Decode one stream via the patchable hook (charges the byte budget)."""
        return self._decode_stream(self.table, stream, self)

    def decode_form(
        self, stream: PdfStream, ref_key: tuple[int, int] | None
    ) -> bytes | SheetRefusal:
        """Decode a Form XObject stream, MEMOIZED per ``(number, generation)`` for the
        document: a form placed N times decodes (and charges the byte budget) ONCE; later
        placements reuse the cached bytes. A form with no stable ref key is not cached."""
        if ref_key is not None and ref_key in self.form_cache:
            return self.form_cache[ref_key]
        decoded = self.decode_stream(stream)
        if isinstance(decoded, SheetRefusal):
            return decoded
        if ref_key is not None:
            self.form_cache[ref_key] = decoded
        return decoded

    def decode_contents(self, node: dict) -> bytes | SheetRefusal:
        """Decode a leaf page's ``/Contents``: absent -> ``b''``; one stream or an array of
        streams (concatenated with a newline)."""
        table = self.table
        if _CONTENTS_KEY not in node:
            return b""
        contents = _resolve(table, node[_CONTENTS_KEY])
        if isinstance(contents, SheetRefusal):
            return contents
        if isinstance(contents, PdfStream):
            return self.decode_stream(contents)
        if isinstance(contents, list):
            parts: list[bytes] = []
            for element in contents:
                stream = _resolve(table, element)
                if isinstance(stream, SheetRefusal):
                    return stream
                if not isinstance(stream, PdfStream):
                    return _refuse("contents array", "a /Contents array element is not a stream")
                decoded = self.decode_stream(stream)
                if isinstance(decoded, SheetRefusal):
                    return decoded
                parts.append(decoded)
            return b"\n".join(parts)
        return _refuse("contents", "/Contents is neither a stream nor an array of streams")


# ============== PDF 1.5+ stream-decode primitives (shared with the object-stream resolver)
#
# These serve the M5-T103 cross-reference/object-stream resolver (:mod:`pdf_object_streams`),
# which composes them; they are not on the classic content-stream path, so the 62-case split
# golden is unaffected. Bounds are threaded in as plain ints so the resolver's patchable
# module constants (its mutation surface) still drive them.


def inflate_guarded(
    raw: bytes, *, absolute_cap: int, ratio_multiplier: int, charge
) -> bytes | SheetRefusal:
    """Inflate ``raw`` by BOUNDED INCREMENTAL decompression (never an unbounded
    ``zlib.decompress``): each chunk is charged via ``charge`` and checked against the
    absolute inflated-bytes cap and the inflate-ratio guard BEFORE it is retained, so a zip
    bomb refuses with memory bounded to one chunk plus the output so far (the M5-T103
    mandatory guard). ``charge(n)`` returns a :class:`SheetRefusal` when the shared
    document-wide budget would overflow, else None."""
    decompressor = zlib.decompressobj()
    out = bytearray()
    ratio_cap = len(raw) * ratio_multiplier
    src = raw
    while True:
        try:
            chunk = decompressor.decompress(src, _INFLATE_CHUNK)
        except zlib.error:
            return _refuse("corrupt flate stream", "zlib refused a cross-reference/object stream")
        src = decompressor.unconsumed_tail
        if chunk:
            projected = len(out) + len(chunk)
            if projected > absolute_cap:
                return _refuse("inflated bytes cap", f"over {absolute_cap} inflated bytes")
            if projected > ratio_cap:
                return _refuse(
                    "inflate ratio", f"inflated:compressed ratio over {ratio_multiplier}"
                )
            charged = charge(len(chunk))
            if charged is not None:
                return charged
            out += chunk
        if decompressor.eof:
            break
        if not chunk and not src:
            return _refuse("corrupt flate stream", "flate stream ended before its terminator")
    return bytes(out)


def apply_predictor(data: bytes, parms: dict) -> bytes | SheetRefusal:
    """Apply the §7.4.4.4 predictor named by ``/DecodeParms``: 1/absent = none; 2 = TIFF
    (typed refusal, not implemented); 10-15 = PNG (per-row filter tag byte)."""
    predictor = _parm_int(parms, _PREDICTOR_KEY, 1)
    if predictor is None:
        return _refuse("predictor", "/Predictor is not an integer")
    if predictor == 1:
        return data
    if predictor == 2:
        return _refuse("predictor", "TIFF predictor 2 is not implemented")
    if predictor < 10 or predictor > 15:
        return _refuse("predictor", f"unsupported /Predictor {predictor}")
    columns = _parm_int(parms, _COLUMNS_KEY, 1)
    colors = _parm_int(parms, _COLORS_KEY, 1)
    bpc = _parm_int(parms, _BPC_KEY, 8)
    if None in (columns, colors, bpc) or columns < 1 or colors < 1 or bpc < 1:  # type: ignore[operator]
        return _refuse("predictor", "/DecodeParms has a non-positive geometry parameter")
    row_len = (columns * colors * bpc + 7) // 8
    return _png_unfilter(data, row_len, max(1, (colors * bpc + 7) // 8))


def _parm_int(parms: dict, key: PdfName, default: int) -> int | None:
    if key not in parms:
        return default
    value = parms[key]
    return value if type(value) is int else None


def _png_unfilter(data: bytes, row_len: int, bpp: int) -> bytes | SheetRefusal:
    """Reverse the PNG per-row filters (§7.4.4.4 / RFC 2083 [recalled - verify], corroborated
    by decoding the real corpus xref streams): each row is a 1-byte filter tag then
    ``row_len`` bytes; the tag selects None/Sub/Up/Average/Paeth."""
    stride = row_len + 1
    if row_len <= 0 or len(data) % stride != 0:
        return _refuse("predictor", "PNG-predicted rows are misaligned with /Columns")
    out = bytearray()
    previous = bytearray(row_len)
    pos = 0
    for _ in range(len(data) // stride):
        tag = data[pos]
        current = bytearray(data[pos + 1 : pos + stride])
        pos += stride
        if tag == 0:
            pass
        elif tag == 1:
            for i in range(bpp, row_len):
                current[i] = (current[i] + current[i - bpp]) & 0xFF
        elif tag == 2:
            for i in range(row_len):
                current[i] = (current[i] + previous[i]) & 0xFF
        elif tag == 3:
            for i in range(row_len):
                left = current[i - bpp] if i >= bpp else 0
                current[i] = (current[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif tag == 4:
            for i in range(row_len):
                left = current[i - bpp] if i >= bpp else 0
                upper_left = previous[i - bpp] if i >= bpp else 0
                current[i] = (current[i] + _paeth(left, previous[i], upper_left)) & 0xFF
        else:
            return _refuse("predictor", f"unsupported PNG row filter {tag}")
        out += current
        previous = current
    return bytes(out)


def _paeth(a: int, b: int, c: int) -> int:
    """The PNG Paeth predictor of left (a), up (b), upper-left (c) (§7.4.4.4 [recalled])."""
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c
