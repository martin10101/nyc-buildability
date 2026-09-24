"""Architect drawing-sheet PDF interpretation profile (M5-T083, D-087 PDF-1).

A SEPARATE interpretation profile for architect drawing sheets. It reuses the in-repo
strict-subset reader's lexer / object parser / cross-reference reader READ-ONLY (via
:func:`~app.documents.extraction.pdf_xref.read_object_table`, which itself composes
``pdf_lexer`` and ``pdf_objects``) and then interprets each page's content stream under a
WIDER graphics subset than the survey pipeline's
:mod:`~app.documents.extraction.pdf_content`, which by design refuses curves, XObjects,
and rotated/sheared transforms. This module imports nothing FROM this package into the
survey pipeline and relaxes none of the survey decoder's refusals; it is a standalone,
read-only consumer.

What this profile interprets, beyond the survey subset (ISO 32000-1 / PDF 1.7 operator
semantics; per-operator section citations are marked ``[recalled - verify]`` for the G1
data-contract review):

* Path construction ``m l c v y h re`` (§8.5.2) — cubic Beziers (``c v y``) are flattened
  to polylines under a DECLARED maximum chord error, recorded on every page and document.
* The FULL affine CTM via ``cm`` (§8.3.4) — rotation and shear included (``b``/``c`` non-
  zero), which the survey profile refuses.
* A depth-bounded ``q``/``Q`` graphics-state stack (§8.4.4) saving/restoring the CTM.
* Stroke vs. fill painting distinguished (§8.5.3); text-run positions under the full text
  and CTM matrices (§9.4), rotation allowed.
* Form XObjects (``Do``, §8.10) re-interpreted under each placement's CTM, with recursion
  depth <= ``MAX_XOBJECT_DEPTH`` and cycle refusal; image XObjects COUNTED and disclosed
  (name, placement, declared dimensions) but NEVER decoded.

Doctrine (inherited from the strict reader): refusal is a VALUE, never an exception; a
refusal on any page fails the whole document (all-or-nothing, no partial); untrusted input
is bounded on stream size, operator count, path points, ``q`` depth, XObject recursion, and
Bezier subdivision; no byte is executed and no network is touched.

The emitted coordinates are page-scoped PDF USER SPACE (the page's default user space after
CTM concatenation), never auto-trusted as world coordinates — each page also carries its
``media_box`` and ``user_unit`` for a later unit-confirmation stage.
"""

from __future__ import annotations

import math
import zlib

from app.documents.extraction.pdf_lexer import (
    LexedToken,
    PdfName,
    PdfSyntaxError,
    lex_primitive,
)
from app.documents.extraction.pdf_objects import PdfRef, PdfStream
from app.documents.extraction.pdf_xref import (
    PdfObjectTable,
    UnsupportedPdfFeature,
    read_object_table,
)
from app.drawings.sheet_primitives import (
    Matrix,
    Point,
    SheetDocument,
    SheetImage,
    SheetPage,
    SheetPolyline,
    SheetRefusal,
    SheetTextRun,
)
from app.drawings.sheet_primitives import apply_matrix as _apply_matrix
from app.drawings.sheet_primitives import concat_matrix as _concat_matrix
from app.drawings.sheet_primitives import flatten_cubic as _flatten_cubic

__all__ = [
    "DEFAULT_FLATTEN_TOLERANCE",
    "MAX_CONTENT_OPERATORS",
    "MAX_DECODED_STREAM_BYTES",
    "MAX_PATH_POINTS",
    "MAX_Q_DEPTH",
    "MAX_XOBJECT_DEPTH",
    "read_sheet",
    "sheet_refusal",
]

# -- profile bounds (each over-limit is a typed refusal VALUE) ----------------------------
MAX_CONTENT_OPERATORS = 200_000   # executed operators, summed across all nested forms
MAX_PATH_POINTS = 500_000         # flattened path points emitted, summed across the page
MAX_Q_DEPTH = 128                 # saved graphics states in one content stream
MAX_XOBJECT_DEPTH = 8             # Form XObject recursion depth (page content is depth 0)
MAX_DECODED_STREAM_BYTES = 8_388_608  # decoded content/form-stream byte cap
DEFAULT_FLATTEN_TOLERANCE = 0.25  # declared maximum chord error, user-space units

_IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

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

_MAX_RESOLVE_HOPS = 32
_ABSENT = object()

_WHITESPACE = frozenset(b"\x00\t\n\x0c\r ")
_DELIMITERS = frozenset(b"()<>[]{}/%")

_PAINT_STROKE = frozenset({"S", "s", "B", "B*", "b", "b*"})
_PAINT_FILL = frozenset({"f", "F", "f*", "B", "B*", "b", "b*"})
_PAINT_ALL = frozenset({"S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"})
_PAINT_CLOSE_FIRST = frozenset({"s", "b", "b*"})
_TEXT_SHOW_OR_MOVE = frozenset({"Td", "TD", "Tm", "T*", "Tj", "TJ", "'", '"'})
# No-effect-on-geometry operators consumed and ignored (operands cleared).
_IGNORED = frozenset(
    {
        # graphics/colour/style state (§8.4, §8.6)
        "w", "J", "j", "M", "d", "ri", "i", "gs",
        "g", "G", "rg", "RG", "k", "K",
        "cs", "CS", "sc", "scn", "SC", "SCN",
        # marked content (§14.6) and compatibility (§8.10 BX/EX)
        "BMC", "BDC", "EMC", "MP", "DP", "BX", "EX",
        # clipping-path operators (§8.5.4): the path is kept and painted by the next op
        "W", "W*",
        # text state not affecting the modelled origin (§9.3): TL handled explicitly
        "Tc", "Tw", "Tz", "Ts", "Tr", "d0", "d1",
    }
)


# The 2-D affine / Bezier algebra lives in :mod:`app.drawings.sheet_primitives`; it is
# imported here as the module-level names ``_concat_matrix`` / ``_apply_matrix`` /
# ``_flatten_cubic``. Those names are resolved from THIS module's globals at call time, so a
# reviewer can install an in-process mutant by rebinding the attribute on this module
# (``sheet_reader._concat_matrix = ...``) without editing the tree — see the mutation tests.


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


def sheet_refusal(result: object) -> SheetRefusal | None:
    """Return the :class:`SheetRefusal` carried by a :func:`read_sheet` result, else None."""
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


def _decode_stream(table: PdfObjectTable, stream: PdfStream) -> bytes | SheetRefusal:
    """Decode a content/form stream under the strict single-``/FlateDecode`` subset;
    refuse ``/DecodeParms``, filter arrays, other filters, corrupt deflate, or over-cap
    output. Mirrors the container's decode doctrine without mutating it."""
    dictionary = stream.dictionary
    if _DECODE_PARMS_KEY in dictionary:
        return _refuse("decode parameters", "stream carries /DecodeParms (unsupported)")
    if _FILTER_KEY not in dictionary:
        raw = stream.raw_data
        if len(raw) > MAX_DECODED_STREAM_BYTES:
            return _refuse("stream size", f"raw stream over {MAX_DECODED_STREAM_BYTES} bytes")
        return raw
    filter_value = _resolve(table, dictionary[_FILTER_KEY])
    if isinstance(filter_value, SheetRefusal):
        return filter_value
    if isinstance(filter_value, list):
        return _refuse("stream filter array", f"/Filter is an array of {len(filter_value)}")
    if filter_value != _FLATE:
        name = filter_value.value if isinstance(filter_value, PdfName) else repr(filter_value)
        return _refuse("stream filter", f"/Filter /{name} is outside the supported subset")
    decompressor = zlib.decompressobj()
    try:
        decoded = decompressor.decompress(stream.raw_data, MAX_DECODED_STREAM_BYTES)
    except zlib.error as error:
        return _refuse("corrupt flate stream", f"zlib refused the stream: {error}")
    if decompressor.unconsumed_tail or not decompressor.eof:
        return _refuse("flate output bound", f"flate output over {MAX_DECODED_STREAM_BYTES} bytes")
    return decoded


def _decode_contents(table: PdfObjectTable, node: dict) -> bytes | SheetRefusal:
    """Decode a leaf page's ``/Contents``: absent -> ``b''``; one stream or an array of
    streams (concatenated with a newline)."""
    if _CONTENTS_KEY not in node:
        return b""
    contents = _resolve(table, node[_CONTENTS_KEY])
    if isinstance(contents, SheetRefusal):
        return contents
    if isinstance(contents, PdfStream):
        return _decode_stream(table, contents)
    if isinstance(contents, list):
        parts: list[bytes] = []
        for element in contents:
            stream = _resolve(table, element)
            if isinstance(stream, SheetRefusal):
                return stream
            if not isinstance(stream, PdfStream):
                return _refuse("contents array", "a /Contents array element is not a stream")
            decoded = _decode_stream(table, stream)
            if isinstance(decoded, SheetRefusal):
                return decoded
            parts.append(decoded)
        return b"\n".join(parts)
    return _refuse("contents", "/Contents is neither a stream nor an array of streams")


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


# =============================================================================== page walk


def read_sheet(
    data: bytes | bytearray | memoryview,
    *,
    flatten_tolerance: float = DEFAULT_FLATTEN_TOLERANCE,
) -> SheetDocument | SheetRefusal:
    """Interpret ``data`` as an architect drawing sheet, returning a :class:`SheetDocument`
    on success or a :class:`SheetRefusal` VALUE on ANY failure (never raises).

    All-or-nothing per document: a refusal on any page fails the whole read and no partial
    document is produced. ``flatten_tolerance`` is the DECLARED maximum chord error (user
    units) used to flatten Bezier curves; it is recorded on every page and the document.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        return _refuse("input", f"expected raw bytes, got {type(data).__name__}")
    if (
        not isinstance(flatten_tolerance, (int, float))
        or isinstance(flatten_tolerance, bool)
        or not math.isfinite(flatten_tolerance)
        or flatten_tolerance <= 0.0
    ):
        return _refuse("flatten tolerance", "flatten_tolerance must be a positive finite number")
    tolerance = float(flatten_tolerance)

    table = read_object_table(bytes(data))
    if isinstance(table, (PdfSyntaxError, UnsupportedPdfFeature)):
        return _wrap_strict(table)

    root = _catalog_pages_root(table)
    if isinstance(root, SheetRefusal):
        return root

    interpreter = _SheetInterpreter(table, tolerance)
    pages: list[SheetPage] = []
    visited: set[tuple[int, int]] = set()
    stack: list[tuple[object, object, object]] = [(root, _ABSENT, _ABSENT)]
    while stack:
        value, inherited_box, inherited_res = stack.pop()
        if isinstance(value, PdfRef):
            key = (value.number, value.generation)
            if key in visited:
                return _refuse("page tree", f"page tree cycle at object {key[0]} {key[1]}")
            visited.add(key)
        node = _resolve(table, value)
        if isinstance(node, SheetRefusal):
            return node
        if not isinstance(node, dict):
            return _refuse("page tree", "a page tree node is not a dictionary")
        if _TYPE_KEY not in node:
            return _refuse("page tree", "a page tree node has no /Type")
        node_type = _resolve(table, node[_TYPE_KEY])
        own_box = node.get(_MEDIA_BOX_KEY, inherited_box)
        own_res = node.get(_RESOURCES_KEY, inherited_res)
        if node_type == _PAGES:
            if _KIDS_KEY not in node:
                return _refuse("page tree", "/Pages node has no /Kids")
            kids = _resolve(table, node[_KIDS_KEY])
            if isinstance(kids, SheetRefusal):
                return kids
            if not isinstance(kids, list):
                return _refuse("page tree", "/Kids is not an array")
            for kid in reversed(kids):
                stack.append((kid, own_box, own_res))
        elif node_type == _PAGE:
            if len(pages) >= 512:
                return _refuse("page count", "more than 512 leaf pages")
            page = _build_page(interpreter, table, node, own_box, own_res, len(pages), tolerance)
            if isinstance(page, SheetRefusal):
                return page
            pages.append(page)
        else:
            return _refuse("page tree", "a page tree node /Type is neither /Pages nor /Page")
    return SheetDocument(flatten_tolerance=tolerance, pages=tuple(pages))


def _build_page(
    interpreter: _SheetInterpreter,
    table: PdfObjectTable,
    node: dict,
    own_box: object,
    own_res: object,
    index: int,
    tolerance: float,
) -> SheetPage | SheetRefusal:
    media_box = _media_box(table, own_box)
    if isinstance(media_box, SheetRefusal):
        return media_box
    user_unit = 1.0
    if _USER_UNIT_KEY in node:
        resolved = _resolve(table, node[_USER_UNIT_KEY])
        if isinstance(resolved, SheetRefusal):
            return resolved
        if isinstance(resolved, (int, float)) and not isinstance(resolved, bool) and resolved > 0:
            user_unit = float(resolved)
        else:
            return _refuse("user unit", "/UserUnit is not a positive number")
    resources = _ABSENT if own_res is _ABSENT else _resolve(table, own_res)
    if isinstance(resources, SheetRefusal):
        return resources
    content = _decode_contents(table, node)
    if isinstance(content, SheetRefusal):
        return content
    result = interpreter.interpret(content, resources, _IDENTITY, 0, frozenset())
    if isinstance(result, SheetRefusal):
        return result
    polylines, text_runs, images = result
    return SheetPage(
        index=index,
        media_box=media_box,
        user_unit=user_unit,
        flatten_tolerance=tolerance,
        polylines=polylines,
        text_runs=text_runs,
        images=images,
    )


# ============================================================================ interpreter


class _SheetInterpreter:
    """Page-wide interpretation state: the object table, the declared tolerance, and the
    output/budget counters that are SHARED across nested Form XObject recursion."""

    def __init__(self, table: PdfObjectTable, tolerance: float) -> None:
        self.table = table
        self.tolerance = tolerance
        self.polylines: list[SheetPolyline] = []
        self.text_runs: list[SheetTextRun] = []
        self.images: list[SheetImage] = []
        self.op_count = 0
        self.point_count = 0

    def interpret(
        self,
        content: bytes,
        resources: object,
        ctm: Matrix,
        depth: int,
        xobject_stack: frozenset[tuple[int, int]],
    ) -> tuple[
        tuple[SheetPolyline, ...], tuple[SheetTextRun, ...], tuple[SheetImage, ...]
    ] | SheetRefusal:
        """Interpret one content stream (page or form) and, at depth 0, return the frozen
        page primitives; a nested form returns an empty tuple triple on success (its
        primitives are already appended to the shared output)."""
        error = _StreamRun(self, content, resources, ctm, depth, xobject_stack).run()
        if isinstance(error, SheetRefusal):
            return error
        if depth == 0:
            return tuple(self.polylines), tuple(self.text_runs), tuple(self.images)
        return ((), (), ())


class _StreamRun:
    """Mutable scanner/executor for a single content stream. Owns the per-stream path,
    text, and CTM-stack state; defers budgets and output to the shared interpreter."""

    def __init__(
        self,
        interp: _SheetInterpreter,
        content: bytes,
        resources: object,
        ctm: Matrix,
        depth: int,
        xobject_stack: frozenset[tuple[int, int]],
    ) -> None:
        self._interp = interp
        self._data = content
        self._resources = resources
        self._ctm = ctm
        self._depth = depth
        self._stack = xobject_stack
        self._pos = 0
        self._operands: list[object] = []
        self._ctm_stack: list[Matrix] = []
        # path state (current point kept in user space; subpaths in user space post-CTM)
        self._current: Point | None = None
        self._subpath_start: Point | None = None
        self._subpaths: list[tuple[list[Point], bool]] = []
        self._cur_points: list[Point] | None = None
        # text state
        self._in_text = False
        self._tm: Matrix = _IDENTITY
        self._tlm: Matrix = _IDENTITY
        self._leading = 0.0
        self._font_size: float | None = None

    # -- scan loop --------------------------------------------------------------------
    def run(self) -> SheetRefusal | None:
        data = self._data
        while True:
            self._skip_ws()
            if self._pos >= len(data):
                break
            if data[self._pos] == 0x5B:  # '[' inline array operand (TJ, d)
                error = self._read_array()
                if error is not None:
                    return error
                continue
            token = lex_primitive(data, self._pos)
            if isinstance(token, LexedToken):
                self._operands.append(token.value)
                self._pos = token.end_offset
                continue
            word_start = self._pos
            word_end = word_start
            while word_end < len(data) and self._is_regular(data[word_end]):
                word_end += 1
            if word_end == word_start:
                return _wrap_strict(token)
            word = data[word_start:word_end].decode("latin-1")
            self._pos = word_end
            self._interp.op_count += 1
            if self._interp.op_count > MAX_CONTENT_OPERATORS:
                return _refuse("operator count", f"over {MAX_CONTENT_OPERATORS} operators")
            error = self._execute(word, word_start)
            if error is not None:
                return error
        return self._finish()

    def _finish(self) -> SheetRefusal | None:
        if self._operands:
            return _refuse("dangling operands", f"{len(self._operands)} unconsumed operand(s)")
        if self._in_text:
            return _refuse("unclosed text", "content ends inside an open BT..ET")
        if self._ctm_stack:
            return _refuse("unbalanced q", f"{len(self._ctm_stack)} unrestored q save(s)")
        return None

    def _skip_ws(self) -> None:
        data = self._data
        while self._pos < len(data):
            byte = data[self._pos]
            if byte in _WHITESPACE:
                self._pos += 1
            elif byte == 0x25:  # '%' comment to end of line
                while self._pos < len(data) and data[self._pos] not in (0x0D, 0x0A):
                    self._pos += 1
            else:
                return

    @staticmethod
    def _is_regular(byte: int) -> bool:
        return byte not in _WHITESPACE and byte not in _DELIMITERS

    def _read_array(self) -> SheetRefusal | None:
        data = self._data
        self._pos += 1
        items: list[object] = []
        while True:
            self._skip_ws()
            if self._pos >= len(data):
                return _refuse("inline array", "content ends inside an inline array")
            byte = data[self._pos]
            if byte == 0x5D:  # ']'
                self._pos += 1
                self._operands.append(tuple(items))
                return None
            if byte == 0x5B:  # nested '['
                return _refuse("inline array", "nested inline array is outside the subset")
            token = lex_primitive(data, self._pos)
            if isinstance(token, PdfSyntaxError):
                return _wrap_strict(token)
            items.append(token.value)
            self._pos = token.end_offset

    # -- operand typing ---------------------------------------------------------------
    def _take(self, kinds: str) -> tuple[object, ...] | None:
        ops = self._operands
        if len(ops) != len(kinds):
            return None
        for value, kind in zip(ops, kinds, strict=True):
            if not _matches(value, kind):
                return None
        values = tuple(ops)
        ops.clear()
        return values

    # -- path helpers -----------------------------------------------------------------
    def _flush_open(self) -> None:
        if self._cur_points is not None and len(self._cur_points) >= 1:
            self._subpaths.append((self._cur_points, False))
        self._cur_points = None

    def _moveto(self, x: float, y: float) -> None:
        self._flush_open()
        self._cur_points = [_apply_matrix(self._ctm, x, y)]
        self._current = (x, y)
        self._subpath_start = (x, y)

    def _lineto(self, x: float, y: float) -> SheetRefusal | None:
        if self._current is None or self._cur_points is None:
            return _refuse("path", "'l' with no current point")
        self._cur_points.append(_apply_matrix(self._ctm, x, y))
        self._current = (x, y)
        return self._charge_points(1)

    def _curveto(self, ctrl1: Point, ctrl2: Point, end: Point) -> SheetRefusal | None:
        if self._current is None or self._cur_points is None:
            return _refuse("path", "curve with no current point")
        p0 = _apply_matrix(self._ctm, *self._current)
        p1 = _apply_matrix(self._ctm, *ctrl1)
        p2 = _apply_matrix(self._ctm, *ctrl2)
        p3 = _apply_matrix(self._ctm, *end)
        out: list[Point] = []
        _flatten_cubic(p0, p1, p2, p3, self._interp.tolerance, out, 0)
        self._cur_points.extend(out)
        self._current = end
        return self._charge_points(len(out))

    def _close(self) -> None:
        if self._cur_points is not None and self._subpath_start is not None:
            self._subpaths.append((self._cur_points, True))
            self._cur_points = None
            self._current = self._subpath_start

    def _charge_points(self, count: int) -> SheetRefusal | None:
        self._interp.point_count += count
        if self._interp.point_count > MAX_PATH_POINTS:
            return _refuse("path points", f"over {MAX_PATH_POINTS} flattened points")
        return None

    def _paint(self, word: str) -> None:
        if word in _PAINT_CLOSE_FIRST:
            self._close()
        self._flush_open()
        stroked = word in _PAINT_STROKE
        filled = word in _PAINT_FILL
        for points, closed in self._subpaths:
            if len(points) >= 2:
                self._interp.polylines.append(
                    SheetPolyline(tuple(points), closed, stroked, filled)
                )
        self._subpaths = []
        self._current = None
        self._subpath_start = None

    # -- operator dispatch ------------------------------------------------------------
    def _execute(self, word: str, offset: int) -> SheetRefusal | None:
        if word in _PATH_HANDLERS:
            return _PATH_HANDLERS[word](self)
        if word == "re":
            return self._op_re()
        if word in _PAINT_ALL:
            self._paint(word)
            return None
        if word in _TEXT_STATE_OR_OBJECT:
            return self._text(word, offset)
        if word == "q":
            if len(self._ctm_stack) >= MAX_Q_DEPTH:
                return _refuse("q depth", f"graphics-state nesting over {MAX_Q_DEPTH}")
            self._ctm_stack.append(self._ctm)
            self._operands.clear()
            return None
        if word == "Q":
            if not self._ctm_stack:
                return _refuse("unbalanced Q", "Q with no matching q")
            self._ctm = self._ctm_stack.pop()
            self._operands.clear()
            return None
        if word == "cm":
            values = self._take("nnnnnn")
            if values is None:
                return _refuse("cm", "cm needs 6 numbers")
            self._ctm = _concat_matrix(tuple(float(v) for v in values), self._ctm)  # type: ignore[arg-type]
            return None
        if word == "Do":
            return self._op_do()
        if word in _IGNORED:
            self._operands.clear()
            return None
        return _refuse(
            "unsupported operator",
            f"operator '{word}' at offset {offset} is outside the architect-sheet subset",
        )

    # -- path operators ---------------------------------------------------------------
    def _op_m(self) -> SheetRefusal | None:
        values = self._take("nn")
        if values is None:
            return _refuse("m", "m needs 2 numbers")
        self._moveto(float(values[0]), float(values[1]))
        return None

    def _op_l(self) -> SheetRefusal | None:
        values = self._take("nn")
        if values is None:
            return _refuse("l", "l needs 2 numbers")
        return self._lineto(float(values[0]), float(values[1]))

    def _op_c(self) -> SheetRefusal | None:
        values = self._take("nnnnnn")
        if values is None:
            return _refuse("c", "c needs 6 numbers")
        v = [float(x) for x in values]
        return self._curveto((v[0], v[1]), (v[2], v[3]), (v[4], v[5]))

    def _op_v(self) -> SheetRefusal | None:
        values = self._take("nnnn")
        if values is None or self._current is None:
            return _refuse("v", "v needs 4 numbers and a current point")
        v = [float(x) for x in values]
        return self._curveto(self._current, (v[0], v[1]), (v[2], v[3]))

    def _op_y(self) -> SheetRefusal | None:
        values = self._take("nnnn")
        if values is None:
            return _refuse("y", "y needs 4 numbers")
        v = [float(x) for x in values]
        return self._curveto((v[0], v[1]), (v[2], v[3]), (v[2], v[3]))

    def _op_h(self) -> SheetRefusal | None:
        if self._operands:
            return _refuse("h", "h takes no operands")
        self._close()
        return None

    def _op_re(self) -> SheetRefusal | None:
        values = self._take("nnnn")
        if values is None:
            return _refuse("re", "re needs 4 numbers")
        x, y, w, h = (float(v) for v in values)
        self._moveto(x, y)
        for err in (self._lineto(x + w, y), self._lineto(x + w, y + h), self._lineto(x, y + h)):
            if err is not None:
                return err
        self._close()
        return None

    # -- text operators ---------------------------------------------------------------
    def _text(self, word: str, offset: int) -> SheetRefusal | None:
        if word == "BT":
            if self._in_text:
                return _refuse("text", "nested BT")
            self._in_text = True
            self._tm = _IDENTITY
            self._tlm = _IDENTITY
            self._operands.clear()
            return None
        if word == "ET":
            if not self._in_text:
                return _refuse("text", "ET outside BT..ET")
            self._in_text = False
            self._operands.clear()
            return None
        if word == "Tf":
            values = self._take("mn")
            if values is None:
                return _refuse("Tf", "Tf needs a name and a number")
            self._font_size = float(values[1])
            return None
        if word == "TL":
            values = self._take("n")
            if values is None:
                return _refuse("TL", "TL needs a number")
            self._leading = float(values[0])
            return None
        if word in _TEXT_SHOW_OR_MOVE and not self._in_text:
            return _refuse("text", f"'{word}' outside BT..ET")
        return self._text_body(word)

    def _text_body(self, word: str) -> SheetRefusal | None:
        if word in ("Td", "TD"):
            values = self._take("nn")
            if values is None:
                return _refuse(word, f"{word} needs 2 numbers")
            tx, ty = float(values[0]), float(values[1])
            if word == "TD":
                self._leading = -ty
            self._tlm = _concat_matrix((1.0, 0.0, 0.0, 1.0, tx, ty), self._tlm)
            self._tm = self._tlm
            return None
        if word == "Tm":
            values = self._take("nnnnnn")
            if values is None:
                return _refuse("Tm", "Tm needs 6 numbers")
            self._tm = tuple(float(v) for v in values)  # type: ignore[assignment]
            self._tlm = self._tm
            return None
        if word == "T*":
            if self._operands:
                return _refuse("T*", "T* takes no operands")
            self._tlm = _concat_matrix((1.0, 0.0, 0.0, 1.0, 0.0, -self._leading), self._tlm)
            self._tm = self._tlm
            return None
        return self._show(word)

    def _show(self, word: str) -> SheetRefusal | None:
        if word == "Tj" or word == "'":
            values = self._take("s")
            if values is None:
                return _refuse(word, f"{word} needs one string")
            raw = values[0]
        elif word == '"':
            values = self._take("nns")
            if values is None:
                return _refuse('"', '" needs aw ac and a string')
            raw = values[2]
        else:  # TJ
            values = self._take("a")
            if values is None:
                return _refuse("TJ", "TJ needs one array")
            pieces: list[bytes] = []
            for element in values[0]:
                if isinstance(element, bytes):
                    pieces.append(element)
                elif isinstance(element, (int, float)) and not isinstance(element, bool):
                    continue
                else:
                    return _refuse("TJ", "TJ array element is neither string nor number")
            raw = b"".join(pieces)
        if word in ("'", '"'):
            self._tlm = _concat_matrix((1.0, 0.0, 0.0, 1.0, 0.0, -self._leading), self._tlm)
            self._tm = self._tlm
        if self._font_size is None:
            return _refuse("text", "text shown before any Tf")
        trm = _concat_matrix(self._tm, self._ctm)
        x, y = _apply_matrix(trm, 0.0, 0.0)
        self._interp.text_runs.append(
            SheetTextRun(raw.decode("latin-1", errors="replace"), x, y, self._font_size, trm)
        )
        return None

    # -- XObjects ---------------------------------------------------------------------
    def _op_do(self) -> SheetRefusal | None:
        values = self._take("m")
        if values is None:
            return _refuse("Do", "Do needs one name operand")
        name = values[0].value
        table = self._interp.table
        if self._resources is _ABSENT or not isinstance(self._resources, dict):
            return _refuse("xobject", f"/{name} Do with no /Resources dictionary")
        xobjects = _resolve(table, self._resources.get(_XOBJECT_KEY, _ABSENT))
        if isinstance(xobjects, SheetRefusal):
            return xobjects
        if not isinstance(xobjects, dict):
            return _refuse("xobject", "/Resources has no /XObject dictionary")
        entry = xobjects.get(PdfName(name), _ABSENT)
        if entry is _ABSENT:
            return _refuse("xobject", f"/XObject has no entry named /{name}")
        ref_key = (entry.number, entry.generation) if isinstance(entry, PdfRef) else None
        stream = _resolve(table, entry)
        if isinstance(stream, SheetRefusal):
            return stream
        if not isinstance(stream, PdfStream):
            return _refuse("xobject", f"/{name} does not resolve to a stream")
        subtype = _resolve(table, stream.dictionary.get(_SUBTYPE_KEY, _ABSENT))
        if subtype == _IMAGE:
            return self._place_image(name, stream)
        if subtype == _FORM:
            return self._place_form(name, stream, ref_key)
        return _refuse("xobject", f"/{name} has unsupported /Subtype")

    def _place_image(self, name: str, stream: PdfStream) -> SheetRefusal | None:
        table = self._interp.table
        dictionary = stream.dictionary
        color_space = None
        cs = _resolve(table, dictionary.get(_COLORSPACE_KEY, _ABSENT))
        if isinstance(cs, PdfName):
            color_space = cs.value
        self._interp.images.append(
            SheetImage(
                name=name,
                matrix=self._ctm,
                width=_resolved_int(table, dictionary.get(_WIDTH_KEY, _ABSENT)),
                height=_resolved_int(table, dictionary.get(_HEIGHT_KEY, _ABSENT)),
                bits_per_component=_resolved_int(table, dictionary.get(_BPC_KEY, _ABSENT)),
                color_space=color_space,
            )
        )
        return None  # raw_data is NEVER decoded

    def _place_form(
        self, name: str, stream: PdfStream, ref_key: tuple[int, int] | None
    ) -> SheetRefusal | None:
        if self._depth + 1 > MAX_XOBJECT_DEPTH:
            return _refuse("xobject recursion", f"form nesting over depth {MAX_XOBJECT_DEPTH}")
        if ref_key is not None and ref_key in self._stack:
            return _refuse("xobject cycle", f"form /{name} references itself (cycle)")
        table = self._interp.table
        content = _decode_stream(table, stream)
        if isinstance(content, SheetRefusal):
            return content
        form_matrix = _IDENTITY
        raw_matrix = _resolve(table, stream.dictionary.get(_MATRIX_KEY, _ABSENT))
        if raw_matrix is not _ABSENT:
            if not isinstance(raw_matrix, list) or len(raw_matrix) != 6:
                return _refuse("xobject matrix", "form /Matrix is not 6 numbers")
            nums: list[float] = []
            for element in raw_matrix:
                resolved = _resolve(table, element)
                if not isinstance(resolved, (int, float)) or isinstance(resolved, bool):
                    return _refuse("xobject matrix", "form /Matrix contains a non-number")
                nums.append(float(resolved))
            form_matrix = tuple(nums)  # type: ignore[assignment]
        form_ctm = _concat_matrix(form_matrix, self._ctm)
        form_res = _resolve(table, stream.dictionary.get(_RESOURCES_KEY, _ABSENT))
        if isinstance(form_res, SheetRefusal):
            return form_res
        if form_res is _ABSENT:
            form_res = self._resources
        new_stack = self._stack | ({ref_key} if ref_key is not None else set())
        result = self._interp.interpret(content, form_res, form_ctm, self._depth + 1, new_stack)
        return result if isinstance(result, SheetRefusal) else None


def _matches(value: object, kind: str) -> bool:
    if kind == "n":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "s":
        return isinstance(value, bytes)
    if kind == "m":
        return isinstance(value, PdfName)
    return isinstance(value, tuple)  # "a"


_PATH_HANDLERS = {
    "m": _StreamRun._op_m,
    "l": _StreamRun._op_l,
    "c": _StreamRun._op_c,
    "v": _StreamRun._op_v,
    "y": _StreamRun._op_y,
    "h": _StreamRun._op_h,
}
_TEXT_STATE_OR_OBJECT = frozenset(
    {"BT", "ET", "Tf", "TL", "Td", "TD", "Tm", "T*", "Tj", "TJ", "'", '"'}
)
