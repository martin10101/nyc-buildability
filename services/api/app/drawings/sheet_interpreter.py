"""Content-stream operator interpreter for the architect drawing-sheet profile
(M5-T094 split of the M5-T083 reader; DB-055 b). NO behaviour change.

:class:`_StreamRun` is the per-content-stream scanner/executor for the WIDER-than-survey
graphics subset: full affine CTM (rotation/shear), the ``q``/``Q`` graphics-state stack,
path construction with cubic-Bezier flattening under a declared chord error, stroke/fill
distinction, text-run placement under the text+CTM matrices, and Form XObject
re-interpretation with depth/cycle bounds (image XObjects counted, never decoded).

It composes object-graph/decode helpers from :mod:`app.drawings.sheet_objects` and is
driven by the :class:`~app.drawings.sheet_reader._SheetInterpreter` coordinator that the
facade builds. The profile bounds and the ``concat_matrix`` / ``flatten_cubic`` algebra
are THREADED IN via the coordinator (``self._interp.*``) so patching a facade constant or
function still bites; they are never read as this module's globals.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.documents.extraction.pdf_lexer import (
    LexedToken,
    PdfName,
    PdfSyntaxError,
    lex_primitive,
)
from app.documents.extraction.pdf_objects import PdfRef, PdfStream
from app.drawings.sheet_marked_content import read_inline_dict
from app.drawings.sheet_objects import (
    _ABSENT,
    _BPC_KEY,
    _COLORSPACE_KEY,
    _FORM,
    _HEIGHT_KEY,
    _IMAGE,
    _MATRIX_KEY,
    _RESOURCES_KEY,
    _SUBTYPE_KEY,
    _WIDTH_KEY,
    _XOBJECT_KEY,
    _preview,
    _refuse,
    _resolve,
    _resolved_int,
    _wrap_strict,
)
from app.drawings.sheet_primitives import (
    Matrix,
    Point,
    SheetImage,
    SheetPolyline,
    SheetRefusal,
    SheetTextRun,
)
from app.drawings.sheet_primitives import apply_matrix as _apply_matrix
from app.drawings.sheet_primitives import is_finite_point as _is_finite_point

if TYPE_CHECKING:  # type-only; the runtime dependency stays facade -> interpreter -> objects
    from app.drawings.sheet_reader import _SheetInterpreter

_IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

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


# The 2-D affine / Bezier algebra lives in :mod:`app.drawings.sheet_primitives`. The
# PATCHABLE ``concat_matrix`` / ``flatten_cubic`` are threaded onto the interpreter by the
# facade (``self._interp.concat_matrix`` / ``self._interp.flatten_cubic``), so a reviewer can
# install an in-process mutant by rebinding the attribute on the facade module
# (``sheet_reader._concat_matrix = ...``) without editing the tree — see the mutation tests.


# ================================================================= content-stream executor


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
        font_size: float | None = None,
        leading: float = 0.0,
    ) -> None:
        self._interp = interp
        self._data = content
        self._resources = resources
        self._ctm = ctm
        self._depth = depth
        self._stack = xobject_stack
        self._pos = 0
        self._operands: list[object] = []
        # graphics-state save stack: (CTM, font_size, leading) restored by Q
        self._gs_stack: list[tuple[Matrix, float | None, float]] = []
        # path state — the current point and subpath start are kept in DEVICE space
        # (post-CTM), so a mid-path cm/Q cannot re-derive a wrong curve start (G1 F6/G3 F3).
        self._current: Point | None = None
        self._subpath_start: Point | None = None
        self._subpaths: list[tuple[list[Point], bool]] = []
        self._cur_points: list[Point] | None = None
        # text state — inherited from the caller (a Form inherits the placing stream's
        # font/leading per ISO 32000-1 graphics state; G1 F3/G3 F2).
        self._in_text = False
        self._tm: Matrix = _IDENTITY
        self._tlm: Matrix = _IDENTITY
        self._leading = leading
        self._font_size: float | None = font_size

    # -- scan loop --------------------------------------------------------------------
    def run(self) -> SheetRefusal | None:
        data = self._data
        max_operators = self._interp.limits.max_content_operators
        while True:
            self._skip_ws()
            if self._pos >= len(data):
                break
            if data[self._pos] == 0x5B:  # '[' inline array operand (TJ, d)
                error = self._read_array()
                if error is not None:
                    return error
                continue
            if data[self._pos] == 0x3C and self._pos + 1 < len(data) and data[
                self._pos + 1
            ] == 0x3C:  # '<<' inline marked-content property-list operand (BDC/DP, §14.6)
                error = self._read_inline_dict()
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
            if self._interp.op_count > max_operators:
                return _refuse("operator count", f"over {max_operators} operators")
            error = self._execute(word, word_start)
            if error is not None:
                return error
        return self._finish()

    def _finish(self) -> SheetRefusal | None:
        if self._operands:
            return _refuse("dangling operands", f"{len(self._operands)} unconsumed operand(s)")
        if self._in_text:
            return _refuse("unclosed text", "content ends inside an open BT..ET")
        if self._gs_stack:
            return _refuse("unbalanced q", f"{len(self._gs_stack)} unrestored q save(s)")
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

    def _read_inline_dict(self) -> SheetRefusal | None:
        """Consume a balanced, bounded inline ``<< >>`` marked-content property list (§14.6) as a
        single DISCARDED operand, so ``BDC`` / ``DP`` accept it (they clear it via ``_IGNORED``);
        the property list paints nothing. Depth/length bounds come from the threaded facade limits
        so a patched bound still bites; an unbalanced/too-deep/too-long list is a typed refusal."""
        result = read_inline_dict(
            self._data,
            self._pos,
            max_depth=self._interp.limits.max_marked_content_depth,
            max_bytes=self._interp.limits.max_marked_content_bytes,
        )
        if isinstance(result, SheetRefusal):
            return result
        self._operands.append(result.value)
        self._pos = result.end_offset
        return None

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

    def _map(self, x: float, y: float) -> Point | SheetRefusal:
        """Map user point ``(x, y)`` through the current CTM into device space; refuse a
        non-finite result (CTM overflow to inf/nan — G5 F6)."""
        point = _apply_matrix(self._ctm, x, y)
        if not _is_finite_point(point):
            return _refuse("non-finite coordinate", "a coordinate is not finite after CTM math")
        return point

    def _open_after_close(self) -> None:
        """After ``h`` / ``re`` / a paint's close, a segment op with no intervening ``m``
        begins a NEW subpath at the current point (device space), per ISO 32000-1 Table 59
        (G1 F5), rather than being refused."""
        self._cur_points = [self._current]  # type: ignore[list-item]
        self._subpath_start = self._current

    def _moveto(self, x: float, y: float) -> SheetRefusal | None:
        self._flush_open()
        point = self._map(x, y)
        if isinstance(point, SheetRefusal):
            return point
        self._cur_points = [point]
        self._current = point          # device space (post-CTM)
        self._subpath_start = point
        return None

    def _lineto(self, x: float, y: float) -> SheetRefusal | None:
        if self._current is None:
            return _refuse("path", "'l' with no current point")
        point = self._map(x, y)
        if isinstance(point, SheetRefusal):
            return point
        if self._cur_points is None:
            self._open_after_close()
        self._cur_points.append(point)  # type: ignore[union-attr]
        self._current = point
        return self._charge_points(1)

    def _curveto(
        self, ctrl1: Point, ctrl2: Point, end: Point, *, ctrl1_is_current: bool = False
    ) -> SheetRefusal | None:
        if self._current is None:
            return _refuse("path", "curve with no current point")
        interp = self._interp
        p0 = self._current                       # device space; a mid-path cm cannot move it
        p1: Point | SheetRefusal = p0 if ctrl1_is_current else self._map(*ctrl1)
        if isinstance(p1, SheetRefusal):
            return p1
        p2 = self._map(*ctrl2)
        if isinstance(p2, SheetRefusal):
            return p2
        p3 = self._map(*end)
        if isinstance(p3, SheetRefusal):
            return p3
        if self._cur_points is None:
            self._open_after_close()
        max_points = interp.limits.max_path_points
        remaining = max_points - interp.point_count
        if remaining < 0:
            remaining = 0
        out: list[Point] = []
        # Thread the page's REMAINING point budget INTO flattening: a degenerate curve stops
        # and refuses at the budget instead of first materializing 2**MAX_FLATTEN_DEPTH points
        # (G5 F1 / G3 F1).
        completed = interp.flatten_cubic(p0, p1, p2, p3, interp.tolerance, out, 0, remaining)
        if not completed:
            return _refuse("path points", f"over {max_points} flattened points")
        for point in out:                        # de Casteljau midpoints can overflow to inf
            if not _is_finite_point(point):
                return _refuse("non-finite coordinate", "a flattened point is not finite")
        self._cur_points.extend(out)  # type: ignore[union-attr]
        self._current = p3
        return self._charge_points(len(out))

    def _close(self) -> None:
        if self._cur_points is not None and self._subpath_start is not None:
            self._subpaths.append((self._cur_points, True))
            self._cur_points = None
            self._current = self._subpath_start   # device space

    def _charge_points(self, count: int) -> SheetRefusal | None:
        interp = self._interp
        interp.point_count += count
        if interp.point_count > interp.limits.max_path_points:
            return _refuse("path points", f"over {interp.limits.max_path_points} flattened points")
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
            if len(self._gs_stack) >= self._interp.limits.max_q_depth:
                return _refuse(
                    "q depth",
                    f"graphics-state nesting over {self._interp.limits.max_q_depth}",
                )
            # Save the CTM AND the persistent text state (font size, leading), which are all
            # part of the graphics state per ISO 32000-1 Table 52 (G1 F3/G3 F2).
            self._gs_stack.append((self._ctm, self._font_size, self._leading))
            self._operands.clear()
            return None
        if word == "Q":
            if not self._gs_stack:
                return _refuse("unbalanced Q", "Q with no matching q")
            self._ctm, self._font_size, self._leading = self._gs_stack.pop()
            self._operands.clear()
            return None
        if word == "cm":
            values = self._take("nnnnnn")
            if values is None:
                return _refuse("cm", "cm needs 6 numbers")
            self._ctm = self._interp.concat_matrix(
                tuple(float(v) for v in values), self._ctm  # type: ignore[arg-type]
            )
            return None
        if word == "Do":
            return self._op_do()
        if word in _IGNORED:
            self._operands.clear()
            return None
        return _refuse(
            "unsupported operator",
            f"operator '{_preview(word)}' at offset {offset} is outside the architect-sheet subset",
        )

    # -- path operators ---------------------------------------------------------------
    def _op_m(self) -> SheetRefusal | None:
        values = self._take("nn")
        if values is None:
            return _refuse("m", "m needs 2 numbers")
        return self._moveto(float(values[0]), float(values[1]))

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
        # 'v': the first control point coincides with the current point (device space).
        return self._curveto((0.0, 0.0), (v[0], v[1]), (v[2], v[3]), ctrl1_is_current=True)

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
        move_err = self._moveto(x, y)
        if move_err is not None:
            return move_err
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
            self._tlm = self._interp.concat_matrix((1.0, 0.0, 0.0, 1.0, tx, ty), self._tlm)
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
            self._tlm = self._interp.concat_matrix(
                (1.0, 0.0, 0.0, 1.0, 0.0, -self._leading), self._tlm
            )
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
            self._tlm = self._interp.concat_matrix(
                (1.0, 0.0, 0.0, 1.0, 0.0, -self._leading), self._tlm
            )
            self._tm = self._tlm
        if self._font_size is None:
            return _refuse("text", "text shown before any Tf")
        trm = self._interp.concat_matrix(self._tm, self._ctm)
        origin = self._map_via(trm)
        if isinstance(origin, SheetRefusal):
            return origin
        x, y = origin
        self._interp.text_runs.append(
            SheetTextRun(raw.decode("latin-1", errors="replace"), x, y, self._font_size, trm)
        )
        return None

    def _map_via(self, matrix: Matrix) -> Point | SheetRefusal:
        """Map the text-space origin ``(0, 0)`` through ``matrix``; refuse a non-finite text
        origin (CTM/text-matrix overflow — G5 F6)."""
        point = _apply_matrix(matrix, 0.0, 0.0)
        if not _is_finite_point(point):
            return _refuse("non-finite coordinate", "text origin is not finite after CTM math")
        return point

    # -- XObjects ---------------------------------------------------------------------
    def _op_do(self) -> SheetRefusal | None:
        values = self._take("m")
        if values is None:
            return _refuse("Do", "Do needs one name operand")
        name = values[0].value
        table = self._interp.table
        if self._resources is _ABSENT or not isinstance(self._resources, dict):
            return _refuse("xobject", f"/{_preview(name)} Do with no /Resources dictionary")
        xobjects = _resolve(table, self._resources.get(_XOBJECT_KEY, _ABSENT))
        if isinstance(xobjects, SheetRefusal):
            return xobjects
        if not isinstance(xobjects, dict):
            return _refuse("xobject", "/Resources has no /XObject dictionary")
        entry = xobjects.get(PdfName(name), _ABSENT)
        if entry is _ABSENT:
            return _refuse("xobject", f"/XObject has no entry named /{_preview(name)}")
        ref_key = (entry.number, entry.generation) if isinstance(entry, PdfRef) else None
        stream = _resolve(table, entry)
        if isinstance(stream, SheetRefusal):
            return stream
        if not isinstance(stream, PdfStream):
            return _refuse("xobject", f"/{_preview(name)} does not resolve to a stream")
        subtype = _resolve(table, stream.dictionary.get(_SUBTYPE_KEY, _ABSENT))
        if subtype == _IMAGE:
            return self._place_image(name, stream)
        if subtype == _FORM:
            return self._place_form(name, stream, ref_key)
        return _refuse("xobject", f"/{_preview(name)} has unsupported /Subtype")

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
        """Re-interpret a Form XObject under its placement CTM. The form's ``/BBox`` clip is
        NOT applied (over-inclusion by design — see the facade docstring); the decoded content
        is memoized per ref key; and the form inherits the placing stream's text state
        (font size, leading)."""
        interp = self._interp
        if self._depth + 1 > interp.limits.max_xobject_depth:
            return _refuse(
                "xobject recursion", f"form nesting over depth {interp.limits.max_xobject_depth}"
            )
        if ref_key is not None and ref_key in self._stack:
            return _refuse(
                "xobject cycle", f"form /{_preview(name)} references an ancestor (cycle)"
            )
        table = interp.table
        content = interp.decoder.decode_form(stream, ref_key)
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
        form_ctm = interp.concat_matrix(form_matrix, self._ctm)
        form_res = _resolve(table, stream.dictionary.get(_RESOURCES_KEY, _ABSENT))
        if isinstance(form_res, SheetRefusal):
            return form_res
        if form_res is _ABSENT:
            form_res = self._resources
        new_stack = self._stack | ({ref_key} if ref_key is not None else set())
        result = interp.interpret(
            content,
            form_res,
            form_ctm,
            self._depth + 1,
            new_stack,
            font_size=self._font_size,
            leading=self._leading,
        )
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
