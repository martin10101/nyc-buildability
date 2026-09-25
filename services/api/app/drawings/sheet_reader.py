"""Architect drawing-sheet PDF interpretation profile — public facade (M5-T083, D-087
PDF-1; split into focused modules at M5-T094 / DB-055 b, NO behaviour change).

A SEPARATE interpretation profile for architect drawing sheets. It reuses the in-repo
strict-subset reader's lexer / object parser / cross-reference reader READ-ONLY (via
:func:`~app.documents.extraction.pdf_xref.read_object_table`, which itself composes
``pdf_lexer`` and ``pdf_objects``) and then interprets each page's content stream under a
WIDER graphics subset than the survey pipeline's
:mod:`~app.documents.extraction.pdf_content`, which by design refuses curves, XObjects,
and rotated/sheared transforms. This module imports nothing FROM this package into the
survey pipeline and relaxes none of the survey decoder's refusals; it is a standalone,
read-only consumer.

Implementation modules (this file is the compatibility facade and the page-tree driver):

* :mod:`app.drawings.sheet_objects` — object-graph resolution, single-stream decoding,
  ``/Contents`` joining, the Form-decode memo, and the document-wide decoded-bytes budget.
* :mod:`app.drawings.sheet_interpreter` — the content-stream operator interpreter
  (graphics/text state, path construction with Bezier flattening, form placement).
* :mod:`app.drawings.sheet_primitives` — the frozen output value types and the pure
  affine / Bezier algebra.

This facade owns the public entry (:func:`read_sheet`), the profile bounds (each a
module-level constant so a reviewer can install an in-process mutant by rebinding it —
the bounds are THREADED into the interpreter/decoder at read time so a patch here still
bites), the page-tree walk (page/pages nodes, inherited MediaBox/Resources, the 512-page
cap), and the top-level backstop that turns any unexpected error into a refusal VALUE.

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

Clipping is NOT modelled: ``W`` / ``W*`` clip operators and a Form XObject's ``/BBox`` are
deliberately NOT applied, so surfaced geometry may INCLUDE content a clip would have removed
(over-inclusion by design — a drawing-sheet reader prefers to disclose more geometry than to
silently drop it). A later consumer that needs true clipped extents adds clip-region tracking.

Doctrine (inherited from the strict reader): refusal is a VALUE, never an exception (a
top-level backstop in :func:`read_sheet` turns any unexpected error into a refusal too); a
refusal on any page fails the whole document (all-or-nothing, no partial); untrusted input
is bounded on stream size, per-document decoded bytes, operator count, path points (bounded
DURING Bezier flattening, not after), ``q`` depth, XObject recursion, and Bezier subdivision;
each page's primitives are isolated to that page; no byte is executed and no network is
touched.

The emitted coordinates are page-scoped PDF USER SPACE (the page's default user space after
CTM concatenation), never auto-trusted as world coordinates — each page also carries its
``media_box`` and ``user_unit`` for a later unit-confirmation stage.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.documents.extraction.pdf_objects import PdfRef
from app.documents.extraction.pdf_xref import (
    PdfObjectTable,
    UnsupportedPdfFeature,
    read_object_table,
)
from app.drawings.pdf_object_streams import (
    XREF_STREAM_FEATURES,
    resolve_object_table,
)
from app.drawings.sheet_inline_image import (
    MAX_INLINE_IMAGE_DATA_BYTES,
    MAX_INLINE_IMAGE_DICT_BYTES,
)
from app.drawings.sheet_interpreter import _IDENTITY, _StreamRun
from app.drawings.sheet_marked_content import (
    MAX_MARKED_CONTENT_BYTES,
    MAX_MARKED_CONTENT_DEPTH,
)
from app.drawings.sheet_objects import (
    _ABSENT,
    _KIDS_KEY,
    _MEDIA_BOX_KEY,
    _PAGE,
    _PAGES,
    _RESOURCES_KEY,
    _TYPE_KEY,
    _USER_UNIT_KEY,
    MAX_DECODED_STREAM_BYTES,
    MAX_PAGE_DECODED_BYTES,
    MAX_TOTAL_DECODED_BYTES,
    _catalog_pages_root,
    _decode_stream,
    _media_box,
    _refuse,
    _resolve,
    _StreamDecoder,
    _wrap_strict,
    sheet_refusal,
)
from app.drawings.sheet_primitives import (
    Matrix,
    SheetDocument,
    SheetImage,
    SheetPage,
    SheetPolyline,
    SheetRefusal,
    SheetTextRun,
)
from app.drawings.sheet_primitives import concat_matrix as _concat_matrix
from app.drawings.sheet_primitives import flatten_cubic as _flatten_cubic

__all__ = [
    "DEFAULT_FLATTEN_TOLERANCE",
    "MAX_CONTENT_OPERATORS",
    "MAX_DECODED_STREAM_BYTES",
    "MAX_DOCUMENT_OPERATORS",
    "MAX_DOCUMENT_PATH_POINTS",
    "MAX_INLINE_IMAGE_DATA_BYTES",
    "MAX_INLINE_IMAGE_DICT_BYTES",
    "MAX_MARKED_CONTENT_BYTES",
    "MAX_MARKED_CONTENT_DEPTH",
    "MAX_PAGE_DECODED_BYTES",
    "MAX_PATH_POINTS",
    "MAX_Q_DEPTH",
    "MAX_TOTAL_DECODED_BYTES",
    "MAX_XOBJECT_DEPTH",
    "read_sheet",
    "sheet_refusal",
]

# -- profile bounds (each over-limit is a typed refusal VALUE; threaded into the interpreter
#    and decoder at read time, so patching one of these still changes the running read) -----
#
# PER-PAGE budgets bound the work of interpreting ONE page (operators/points executed while
# building that page, INCLUDING the Form XObjects it places), reset at the start of each page.
# A real multi-sheet vector CAD set (M5-T113 corpus items 1-2: 88- and 94-page HVAC details)
# has a large operator/point SUM across pages but a modest per-page count; the pre-M5-T118
# reader charged one DOCUMENT-wide operator budget and refused those files on the sum (DB-055 c).
MAX_CONTENT_OPERATORS = 200_000   # executed operators on ONE page (name kept; now per-page)
MAX_PATH_POINTS = 500_000         # flattened path points emitted on ONE page (name kept; per-page)
# PER-DOCUMENT ceilings bound the whole read regardless of page count, so a many-page document
# whose pages are each just under the per-page cap still cannot run unbounded work. They are set
# to 100x the per-page cap: comfortably above a real 88/94-page vector set (measured in the
# M5-T118 corpus run) yet a hard bound (see the producer report's worst-case arithmetic).
MAX_DOCUMENT_OPERATORS = 20_000_000    # executed operators summed across all pages + nested forms
MAX_DOCUMENT_PATH_POINTS = 50_000_000  # flattened path points summed across all pages
MAX_Q_DEPTH = 128                 # saved graphics states in one content stream
MAX_XOBJECT_DEPTH = 8             # Form XObject recursion depth (page content is depth 0)
# MAX_DECODED_STREAM_BYTES / MAX_PAGE_DECODED_BYTES / MAX_TOTAL_DECODED_BYTES are re-exported from
# sheet_objects, MAX_MARKED_CONTENT_DEPTH / MAX_MARKED_CONTENT_BYTES from sheet_marked_content, and
# MAX_INLINE_IMAGE_DICT_BYTES / MAX_INLINE_IMAGE_DATA_BYTES from sheet_inline_image (their canonical
# homes) so the public names and the patch surface stay at this location; all are threaded into the
# interpreter/decoder at read time so patching one here still changes the running read.
DEFAULT_FLATTEN_TOLERANCE = 0.25  # declared maximum chord error, user-space units


# ==================================================================== document coordinator


@dataclass(frozen=True)
class _InterpreterLimits:
    """Operator/geometry bounds, captured from the facade constants at read time so a
    patched facade constant reaches the running interpreter. Operator and path-point budgets
    come in a PER-PAGE pair (reset each page) and a PER-DOCUMENT ceiling (M5-T118, DB-055 c)."""

    max_page_operators: int
    max_document_operators: int
    max_page_path_points: int
    max_document_path_points: int
    max_q_depth: int
    max_xobject_depth: int
    max_marked_content_depth: int
    max_marked_content_bytes: int
    max_inline_image_dict_bytes: int
    max_inline_image_data_bytes: int


class _SheetInterpreter:
    """Per-document interpretation coordinator, built by :func:`read_sheet` and driven by the
    page walk. Table / tolerance / limits / algebra hooks / decoder are constant for the read;
    ``op_count`` / ``point_count`` are DOCUMENT-WIDE (across pages AND nested Form recursion);
    the output lists are PER-PAGE (reset at each depth-0 :meth:`interpret`) so one page's
    geometry never leaks into another :class:`SheetPage`. The decoded-bytes budget and Form
    memo live on the composed :class:`~app.drawings.sheet_objects._StreamDecoder`; the
    per-content-stream operator execution lives in
    :class:`~app.drawings.sheet_interpreter._StreamRun`.

    ``op_count`` / ``point_count`` are DOCUMENT-WIDE (never reset), checked against the document
    ceilings; ``page_op_count`` / ``page_point_count`` are PER-PAGE (reset by :meth:`begin_page`),
    checked against the per-page budgets (M5-T118). ``shading_skips`` / ``inline_image_skips`` /
    ``orphan_subpaths`` are document totals; their ``page_*`` counterparts hold the current page's
    counts so :func:`_build_page` can stamp them onto each :class:`SheetPage`."""

    def __init__(
        self,
        table: PdfObjectTable,
        tolerance: float,
        *,
        limits: _InterpreterLimits,
        flatten_cubic,
        concat_matrix,
        decoder: _StreamDecoder,
    ) -> None:
        self.table = table
        self.tolerance = tolerance
        self.limits = limits
        self.flatten_cubic = flatten_cubic  # patchable (facade _flatten_cubic)
        self.concat_matrix = concat_matrix  # patchable (facade _concat_matrix)
        self.decoder = decoder
        self.polylines: list[SheetPolyline] = []
        self.text_runs: list[SheetTextRun] = []
        self.images: list[SheetImage] = []
        self.op_count = 0  # document-wide
        self.point_count = 0  # document-wide
        self.shading_skips = 0  # document-wide (sh operators skipped)
        self.inline_image_skips = 0  # document-wide (BI/ID/EI images skipped)
        self.orphan_subpaths = 0  # document-wide (post-paint 'l' subpaths opened at own point)
        self.page_op_count = 0  # reset per page by begin_page
        self.page_point_count = 0  # reset per page by begin_page
        self.page_shading_skips = 0  # reset per page by begin_page
        self.page_inline_image_skips = 0  # reset per page by begin_page
        self.page_orphan_subpaths = 0  # reset per page by begin_page

    def begin_page(self) -> None:
        """Reset every PER-PAGE counter (operators, points, non-geometry skips, orphan subpaths)
        and the decoder's per-page decoded-bytes budget at the start of a page (M5-T118, DB-055 c;
        M5-T120, DB-090 i). Extracted as a seam so a mutation defeating the reset proves the
        per-page budgets are load-bearing."""
        self.page_op_count = 0
        self.page_point_count = 0
        self.page_shading_skips = 0
        self.page_inline_image_skips = 0
        self.page_orphan_subpaths = 0
        self.decoder.begin_page()

    def interpret(
        self,
        content: bytes,
        resources: object,
        ctm: Matrix,
        depth: int,
        xobject_stack: frozenset[tuple[int, int]],
        *,
        font_size: float | None = None,
        leading: float = 0.0,
    ) -> tuple[
        tuple[SheetPolyline, ...], tuple[SheetTextRun, ...], tuple[SheetImage, ...]
    ] | SheetRefusal:
        """Interpret one content stream (page or form). At depth 0 the per-page output lists
        are RESET first and the frozen page primitives are returned; a nested form returns an
        empty triple (its primitives were appended to the current page) and inherits the
        caller's text state (``font_size`` / ``leading``) per ISO 32000-1 graphics state."""
        if depth == 0:
            self.polylines = []
            self.text_runs = []
            self.images = []
        error = _StreamRun(
            self, content, resources, ctm, depth, xobject_stack, font_size, leading
        ).run()
        if isinstance(error, SheetRefusal):
            return error
        if depth == 0:
            return tuple(self.polylines), tuple(self.text_runs), tuple(self.images)
        return ((), (), ())


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

    A top-level backstop (mirroring the sibling DXF reader) converts ANY unexpected
    exception from a helper into a typed :class:`SheetRefusal`, so "refusal is a VALUE" holds
    even on an unforeseen edge; the detail carries only the exception TYPE, never attacker
    content.
    """
    try:
        return _read_sheet(data, flatten_tolerance=flatten_tolerance)
    except Exception as error:  # noqa: BLE001 - fail-closed backstop; refusal is a VALUE
        return _refuse("unexpected error", f"unexpected {type(error).__name__} during read")


def _read_sheet(
    data: bytes | bytearray | memoryview,
    *,
    flatten_tolerance: float,
) -> SheetDocument | SheetRefusal:
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

    # Classic-xref path (unchanged): the strict reader is the authority. Only when it refuses
    # a PDF 1.5+ cross-reference-stream-family file does the NEW resolver take over (M5-T103),
    # so a classic file behaves byte-for-byte as before and the resolver never widens the
    # shared strict reader. ``decoded_seed`` carries the resolver's already-charged bytes into
    # the content-stream decoder so both phases share ONE decoded-bytes budget.
    data_bytes = bytes(data)
    raw_table = read_object_table(data_bytes)
    decoded_seed = 0
    used_resolver = False
    if isinstance(raw_table, PdfObjectTable):
        table = raw_table
    elif (
        isinstance(raw_table, UnsupportedPdfFeature)
        and raw_table.feature in XREF_STREAM_FEATURES
    ):
        resolved = resolve_object_table(
            data_bytes, max_total_decoded_bytes=MAX_TOTAL_DECODED_BYTES
        )
        if resolved is None:
            return _wrap_strict(raw_table)  # not a file this resolver handles
        if isinstance(resolved, SheetRefusal):
            return resolved
        table = resolved.table
        decoded_seed = resolved.decoded_bytes
        used_resolver = True
    else:
        return _wrap_strict(raw_table)

    root = _catalog_pages_root(table)
    if isinstance(root, SheetRefusal):
        return root

    # Capture the (patchable) facade bounds and algebra hooks into the read's interpreter and
    # decoder; monkeypatching a facade constant/function before read_sheet therefore reaches
    # the running interpreter (the split preserves the pre-split in-process mutant seam).
    interpreter = _SheetInterpreter(
        table,
        tolerance,
        limits=_InterpreterLimits(
            max_page_operators=MAX_CONTENT_OPERATORS,
            max_document_operators=MAX_DOCUMENT_OPERATORS,
            max_page_path_points=MAX_PATH_POINTS,
            max_document_path_points=MAX_DOCUMENT_PATH_POINTS,
            max_q_depth=MAX_Q_DEPTH,
            max_xobject_depth=MAX_XOBJECT_DEPTH,
            max_marked_content_depth=MAX_MARKED_CONTENT_DEPTH,
            max_marked_content_bytes=MAX_MARKED_CONTENT_BYTES,
            max_inline_image_dict_bytes=MAX_INLINE_IMAGE_DICT_BYTES,
            max_inline_image_data_bytes=MAX_INLINE_IMAGE_DATA_BYTES,
        ),
        flatten_cubic=_flatten_cubic,
        concat_matrix=_concat_matrix,
        decoder=_StreamDecoder(
            table,
            max_decoded_stream_bytes=MAX_DECODED_STREAM_BYTES,
            max_page_decoded_bytes=MAX_PAGE_DECODED_BYTES,
            max_total_decoded_bytes=MAX_TOTAL_DECODED_BYTES,
            decode_stream=_decode_stream,
            decoded_bytes=decoded_seed,
        ),
    )
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
    scan_only = _scan_only_refusal(pages, used_resolver=used_resolver)
    if scan_only is not None:
        return scan_only
    return SheetDocument(flatten_tolerance=tolerance, pages=tuple(pages))


def _scan_only_refusal(
    pages: list[SheetPage], *, used_resolver: bool
) -> SheetRefusal | None:
    """Return the scan-only refusal for a document that parsed but surfaces ZERO vector geometry,
    else ``None``. Extracted as a module-level seam (M5-T113) so a mutation can defeat the gate
    and prove it is load-bearing (DB-076 c).

    Scoped to the NEW resolver path (DB-055 l) so the classic-xref synthetic suites are unchanged.
    Now that content-stream predictors (DB-076 a) and marked-content inline dictionaries
    (DB-076 b) let a real scanned page parse to completion instead of refusing at its ``<<`` or
    predictor, this gate is REACHABLE on real scanned files (DB-076 c): a scanned/OCR sheet is a
    full-page raster image with no vector linework, which is exactly zero polylines here.

    DB-076 (e) records two KNOWN inconsistencies this packet DISCLOSES rather than fixes (see the
    M5-T113 producer report for the rationale): (1) the ``"scan only"`` label also fires on a
    text-only page set — its feature is pinned to ``"scan only"`` by the read-only
    tests/drawings/test_pdf_object_streams.py::test_scan_only_page_is_typed_refusal, so the label
    cannot change here without breaking a must-pass-unchanged suite; the detail below names the
    text-only case honestly; (2) an image-only page succeeds on the classic path (this gate is
    resolver-scoped) but refuses here — immaterial for the real corpus, every item of which is a
    PDF 1.5+ cross-reference-stream file that takes the resolver path (M5-T093). Unifying the two
    paths would flip accepted classic behaviour and revise goldens beyond this packet's scope."""
    if not used_resolver:
        return None
    if any(page.polylines for page in pages):
        return None
    return _refuse(
        "scan only",
        "the document parsed but yields zero vector geometry (scan-only raster or text-only "
        "page set; no drawing linework)",
    )


def _build_page(
    interpreter: _SheetInterpreter,
    table: object,
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
    # Reset every PER-PAGE budget (operators, points, decoded bytes, non-geometry skips) BEFORE
    # decoding this page's content, so the page's decode + interpret work is charged fresh
    # against the per-page budgets while the document ceilings keep accumulating (M5-T118).
    interpreter.begin_page()
    content = interpreter.decoder.decode_contents(node)
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
        shading_skips=interpreter.page_shading_skips,
        inline_image_skips=interpreter.page_inline_image_skips,
        orphan_subpaths=interpreter.page_orphan_subpaths,
    )
