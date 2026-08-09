"""Fail-closed page-tree walker and stream decoder (M2-T015 unit 3i-3a-3b).

Completes the strict-subset PDF reader: ``read_pdf_container`` turns raw
bytes into a ``PdfDocument`` of ordered pages, each carrying its resolved
``/MediaBox`` and fully decoded ``/Contents`` bytes. Pure function of
``bytes``: no I/O, no globals mutated, no clock, no randomness. Never
raises on any input; every refusal is a VALUE — a ``PdfSyntaxError`` for
malformed or self-contradictory structure, an ``UnsupportedPdfFeature``
for well-formed constructs this strict subset deliberately does not
implement. A refusal from ``read_object_table`` passes through unchanged.

Strict-subset fail-closed doctrine (continues ``pdf_xref``):

* **References resolve or refuse.** ``_resolve`` follows reference
  chains through the object table under a hard hop bound of
  ``_MAX_RESOLVE_HOPS``; a reference to an object the table does not
  list is refused as an unresolvable reference, and a chain that is
  still a reference after the bound (a cycle, or absurd depth) is
  refused — never silently nulled.
* **The page tree is walked, never trusted.** Iterative order-preserving
  depth-first walk; a page-tree node reference seen twice is a refused
  page tree cycle (any non-terminating walk must revisit one of the
  finitely many table keys, so the visited set is a complete guard —
  direct, non-reference kid dictionaries cannot alias an ancestor
  because parsed direct values are trees); more than ``MAX_PAGE_COUNT``
  leaves is a refused bound; a node whose ``/Type`` is neither
  ``/Pages`` nor ``/Page`` is refused. ``/MediaBox`` inherits from the
  nearest ancestor, is resolved element-by-element, and must be exactly
  4 numbers; missing everywhere is a refusal.
* **Streams decode inside bounds.** ``/Length`` consistency with the
  raw data was already enforced by ``pdf_objects`` when each stream was
  materialised; this module trusts that check and never re-reads it.
  The only supported filter is a single direct ``/FlateDecode``;
  decoded output is capped at ``MAX_DECODED_STREAM_BYTES``; filter
  arrays, other filter names, ``/DecodeParms`` of any kind, corrupt
  deflate data, and output beyond the cap are refused by name.

Structural refusals discovered after parsing carry byte offset 0: they
are properties of the resolved object graph, not of a byte position.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass

from .pdf_lexer import PdfName, PdfSyntaxError
from .pdf_objects import PdfRef, PdfStream
from .pdf_xref import PdfObjectTable, UnsupportedPdfFeature, read_object_table

__all__ = [
    "MAX_DECODED_STREAM_BYTES",
    "MAX_PAGE_COUNT",
    "PdfDocument",
    "PdfPage",
    "read_pdf_container",
]

MAX_PAGE_COUNT = 512
MAX_DECODED_STREAM_BYTES = 8_388_608

_MAX_RESOLVE_HOPS = 32
_MAX_DISPLAY_CHARS = 64

_ROOT_KEY = PdfName("Root")
_TYPE_KEY = PdfName("Type")
_CATALOG_TYPE = PdfName("Catalog")
# The /Pages token is both the catalog's page-tree key and the interior-node /Type.
_PAGES_NAME = PdfName("Pages")
_PAGE_TYPE = PdfName("Page")
_KIDS_KEY = PdfName("Kids")
_MEDIA_BOX_KEY = PdfName("MediaBox")
_CONTENTS_KEY = PdfName("Contents")
_FILTER_KEY = PdfName("Filter")
_DECODE_PARMS_KEY = PdfName("DecodeParms")
_FLATE_DECODE = PdfName("FlateDecode")

# Distinguishes "no /MediaBox anywhere on the ancestor path" from an explicit
# value of any kind (including a parsed PDF null, which is refused, not skipped).
_ABSENT = object()


@dataclass(frozen=True)
class PdfPage:
    """One page: depth-first index, resolved /MediaBox, decoded /Contents bytes."""

    index: int
    media_box: tuple[float, float, float, float]
    content: bytes


@dataclass(frozen=True)
class PdfDocument:
    """Every page of the document in page-tree (depth-first) order."""

    pages: tuple[PdfPage, ...]


def read_pdf_container(
    data: bytes,
) -> PdfDocument | UnsupportedPdfFeature | PdfSyntaxError:
    """Read the object table, resolve the catalog, and walk the page tree.

    Never raises; refusals are ``PdfSyntaxError`` or
    ``UnsupportedPdfFeature`` values as described in the module
    docstring, and any refusal from ``read_object_table`` is returned
    unchanged.
    """
    table = read_object_table(data)
    if not isinstance(table, PdfObjectTable):
        return table

    # read_object_table guarantees trailer /Root is a PdfRef.
    catalog = _resolve(table, table.trailer[_ROOT_KEY])
    if isinstance(catalog, PdfSyntaxError):
        return catalog
    if not isinstance(catalog, dict):
        return PdfSyntaxError(
            0, "document catalog dictionary via trailer /Root", _describe(catalog)
        )
    if _TYPE_KEY not in catalog:
        return PdfSyntaxError(0, "/Type /Catalog in the document catalog", "absent")
    catalog_type = _resolve(table, catalog[_TYPE_KEY])
    if isinstance(catalog_type, PdfSyntaxError):
        return catalog_type
    if catalog_type != _CATALOG_TYPE:
        return PdfSyntaxError(
            0, "/Type /Catalog in the document catalog", _describe(catalog_type)
        )
    if _PAGES_NAME not in catalog:
        return PdfSyntaxError(0, "/Pages in the document catalog", "absent")
    return _walk_page_tree(table, catalog[_PAGES_NAME])


def _walk_page_tree(
    table: PdfObjectTable, root: object
) -> PdfDocument | UnsupportedPdfFeature | PdfSyntaxError:
    """Depth-first, order-preserving iterative walk from the catalog's /Pages value.

    Each stack entry pairs an unresolved node value with the raw (possibly
    still-reference) ``/MediaBox`` of its nearest ancestor; the box is only
    resolved and validated at a leaf, where it is actually used.
    """
    pages: list[PdfPage] = []
    visited: set[tuple[int, int]] = set()
    stack: list[tuple[object, object]] = [(root, _ABSENT)]
    while stack:
        value, inherited_box = stack.pop()
        if isinstance(value, PdfRef):
            key = (value.number, value.generation)
            if key in visited:
                return PdfSyntaxError(
                    0,
                    "acyclic page tree",
                    f"page tree cycle at object {key[0]} {key[1]}",
                )
            visited.add(key)
        node = _resolve(table, value)
        if isinstance(node, PdfSyntaxError):
            return node
        if not isinstance(node, dict):
            return PdfSyntaxError(0, "page tree node dictionary", _describe(node))
        if _TYPE_KEY not in node:
            return PdfSyntaxError(
                0, "/Type /Pages or /Page on page tree node", "absent"
            )
        node_type = _resolve(table, node[_TYPE_KEY])
        if isinstance(node_type, PdfSyntaxError):
            return node_type
        own_box = node.get(_MEDIA_BOX_KEY, inherited_box)
        if node_type == _PAGES_NAME:
            if _KIDS_KEY not in node:
                return PdfSyntaxError(0, "/Kids array in /Pages node", "absent")
            kids = _resolve(table, node[_KIDS_KEY])
            if isinstance(kids, PdfSyntaxError):
                return kids
            if not isinstance(kids, list):
                return PdfSyntaxError(
                    0, "/Kids array in /Pages node", _describe(kids)
                )
            for kid in reversed(kids):
                stack.append((kid, own_box))
        elif node_type == _PAGE_TYPE:
            if len(pages) >= MAX_PAGE_COUNT:
                return UnsupportedPdfFeature(
                    "page count bound",
                    "the page tree yields more than"
                    f" MAX_PAGE_COUNT={MAX_PAGE_COUNT} leaf pages",
                )
            media_box = _media_box(table, own_box)
            if isinstance(media_box, PdfSyntaxError):
                return media_box
            content = _page_content(table, node)
            if not isinstance(content, bytes):
                return content
            pages.append(
                PdfPage(index=len(pages), media_box=media_box, content=content)
            )
        else:
            return PdfSyntaxError(
                0, "/Type /Pages or /Page on page tree node", _describe(node_type)
            )
    return PdfDocument(pages=tuple(pages))


def _media_box(
    table: PdfObjectTable, raw: object
) -> tuple[float, float, float, float] | PdfSyntaxError:
    """Resolve and validate a leaf's own or inherited /MediaBox value."""
    if raw is _ABSENT:
        return PdfSyntaxError(
            0, "/MediaBox on the page or an ancestor", "missing MediaBox"
        )
    box = _resolve(table, raw)
    if isinstance(box, PdfSyntaxError):
        return box
    if not isinstance(box, list) or len(box) != 4:
        return PdfSyntaxError(
            0, "/MediaBox array of exactly 4 numbers", _describe(box)
        )
    numbers: list[float] = []
    for element in box:
        resolved = _resolve(table, element)
        if isinstance(resolved, PdfSyntaxError):
            return resolved
        if not isinstance(resolved, (int, float)) or isinstance(resolved, bool):
            # bool is a number to isinstance() but not to PDF; refused explicitly
            return PdfSyntaxError(
                0, "/MediaBox array of exactly 4 numbers", _describe(resolved)
            )
        numbers.append(float(resolved))
    return (numbers[0], numbers[1], numbers[2], numbers[3])


def _page_content(
    table: PdfObjectTable, node: dict
) -> bytes | UnsupportedPdfFeature | PdfSyntaxError:
    """Decode a leaf's /Contents: absent → b'', one stream, or an array of streams."""
    if _CONTENTS_KEY not in node:
        return b""
    contents = _resolve(table, node[_CONTENTS_KEY])
    if isinstance(contents, PdfSyntaxError):
        return contents
    if isinstance(contents, PdfStream):
        return _decoded(contents)
    if isinstance(contents, list):
        parts: list[bytes] = []
        for element in contents:
            stream = _resolve(table, element)
            if isinstance(stream, PdfSyntaxError):
                return stream
            if not isinstance(stream, PdfStream):
                return PdfSyntaxError(
                    0, "content stream in /Contents array", _describe(stream)
                )
            decoded = _decoded(stream)
            if not isinstance(decoded, bytes):
                return decoded
            parts.append(decoded)
        return b"\n".join(parts)
    return PdfSyntaxError(
        0, "/Contents stream or array of streams", _describe(contents)
    )


def _decoded(stream: PdfStream) -> bytes | UnsupportedPdfFeature:
    """Return the stream's decoded bytes, or refuse any unsupported decoding.

    /Length consistency with ``raw_data`` was already enforced by
    ``pdf_objects`` when the stream was materialised; it is trusted here
    and never re-checked.
    """
    dictionary = stream.dictionary
    if _DECODE_PARMS_KEY in dictionary:
        return UnsupportedPdfFeature(
            "decode parameters",
            "stream dictionary carries /DecodeParms; predictors and"
            " parameterised decoding are outside the supported subset",
        )
    if _FILTER_KEY not in dictionary:
        return stream.raw_data
    filter_value = dictionary[_FILTER_KEY]
    if isinstance(filter_value, list):
        return UnsupportedPdfFeature(
            "stream filter array",
            f"/Filter is an array of {len(filter_value)} entries; only a"
            " single direct /FlateDecode name is supported",
        )
    if filter_value != _FLATE_DECODE:
        return UnsupportedPdfFeature(
            "stream filter",
            f"/Filter {_describe(filter_value)} is outside the supported"
            " subset; only a single direct /FlateDecode is implemented",
        )
    decompressor = zlib.decompressobj()
    try:
        decoded = decompressor.decompress(stream.raw_data, MAX_DECODED_STREAM_BYTES)
    except zlib.error as error:
        return UnsupportedPdfFeature(
            "corrupt flate stream",
            f"zlib refused the /FlateDecode stream data: {error}",
        )
    if decompressor.unconsumed_tail or not decompressor.eof:
        return UnsupportedPdfFeature(
            "flate output bound",
            "flate output exceeds"
            f" MAX_DECODED_STREAM_BYTES={MAX_DECODED_STREAM_BYTES} or the"
            " deflate data ends prematurely",
        )
    return decoded


def _resolve(table: PdfObjectTable, value: object) -> object:
    """Follow reference chains through the table; refuse missing targets and cycles.

    Returns the first non-reference value, or a ``PdfSyntaxError`` when a
    reference names an object the table does not list or the chain is
    still a reference after ``_MAX_RESOLVE_HOPS`` hops.
    """
    hops = 0
    while isinstance(value, PdfRef):
        if hops >= _MAX_RESOLVE_HOPS:
            return PdfSyntaxError(
                0,
                f"reference chain of at most {_MAX_RESOLVE_HOPS} hops",
                f"reference cycle or over-deep chain still at object"
                f" {value.number} {value.generation}",
            )
        hops += 1
        key = (value.number, value.generation)
        if key not in table.objects:
            return PdfSyntaxError(
                0,
                f"resolvable indirect reference {value.number} {value.generation}",
                f"unresolvable reference: object {value.number}"
                f" {value.generation} is not in the object table",
            )
        value = table.objects[key]
    return value


def _describe(value: object) -> str:
    """Printable, length-capped repr for refusal messages (mirrors pdf_xref)."""
    printable = "".join(
        ch if " " <= ch <= "~" else f"\\x{ord(ch):02x}" for ch in repr(value)
    )
    if len(printable) > _MAX_DISPLAY_CHARS:
        return printable[: _MAX_DISPLAY_CHARS - 3] + "..."
    return printable
