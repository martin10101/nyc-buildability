"""Path-construction state for the architect drawing-sheet content interpreter (M5-T120 split of
:mod:`app.drawings.sheet_interpreter`; DB-090 c).

The per-content-stream path group of :class:`~app.drawings.sheet_interpreter._StreamRun` lives here
as the :class:`_PathState` mixin the ``_StreamRun`` inherits, so the interpreter stays under the
750-line module ceiling before the next feature lands (the M5-T118 G3 A1 / DB-090 c review). This is
a pure module boundary: the mixin owns path construction (``m l c v y h re`` -> subpaths, cubic
flattening, close, paint), and defers the CTM map (``self._map``), operand typing (``self._take``),
and the per-page/per-document budgets (``self._interp.*``) to the ``_StreamRun`` / coordinator it is
mixed into. Every name a test or module reaches through :mod:`app.drawings.sheet_interpreter`
(``_StreamRun``, ``_IDENTITY``, ``_SKIP_SHADING``, ``read_inline_dict``, ``skip_inline_image``,
``_apply_matrix``, ``_is_finite_point``) stays where it was; ``_execute`` still reads
``_PATH_HANDLERS`` as a ``sheet_interpreter`` module global (imported below), so a monkeypatch of
``sheet_interpreter._PATH_HANDLERS`` still bites.

ISO 32000-1 path semantics are cited next to the code (§8.5.2 path construction, §8.5.3 painting,
Table 59); ``sh``/inline-image skipping and text/XObject handling stay in the interpreter.
"""

from __future__ import annotations

from app.drawings.sheet_objects import _refuse
from app.drawings.sheet_primitives import (
    Point,
    SheetPolyline,
    SheetRefusal,
)
from app.drawings.sheet_primitives import is_finite_point as _is_finite_point

# Painting operators, split by what they draw (§8.5.3). Consumed ONLY by :meth:`_PathState._paint`,
# so they live beside it; ``_PAINT_ALL`` (the dispatch set) stays in the interpreter with
# ``_execute``.
_PAINT_STROKE = frozenset({"S", "s", "B", "B*", "b", "b*"})
_PAINT_FILL = frozenset({"f", "F", "f*", "B", "B*", "b", "b*"})
_PAINT_CLOSE_FIRST = frozenset({"s", "b", "b*"})


class _PathState:
    """Path-construction mixin for :class:`~app.drawings.sheet_interpreter._StreamRun`.

    Owns the current point / subpath-start / open-subpath / painted-subpath state (all in DEVICE
    space, post-CTM) and the ``m l c v y h re`` + paint operators. The host ``_StreamRun`` supplies
    the instance state (``self._interp``, ``self._ctm``, ``self._current``, ``self._cur_points``,
    ``self._subpaths``, ``self._subpath_start``, ``self._operands``), the CTM map (``self._map``),
    and operand typing (``self._take``); this mixin never constructs a ``_StreamRun`` itself.
    """

    # -- path helpers -----------------------------------------------------------------
    def _flush_open(self) -> None:
        if self._cur_points is not None and len(self._cur_points) >= 1:
            self._subpaths.append((self._cur_points, False))
        self._cur_points = None

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
            return self._orphan_lineto(x, y)
        point = self._map(x, y)
        if isinstance(point, SheetRefusal):
            return point
        if self._cur_points is None:
            self._open_after_close()
        self._cur_points.append(point)  # type: ignore[union-attr]
        self._current = point
        return self._charge_points(1)

    def _orphan_lineto(self, x: float, y: float) -> SheetRefusal | None:
        """An ``l`` with NO current point — the current point is UNDEFINED after a painting operator
        (ISO 32000-1 §8.5.2 / §8.5.3, Table 59) — starts a NEW subpath AT ITS OWN end point: NO
        segment is drawn to it (never from the stale pre-paint point, which would INVENT a segment),
        and later segments draw FROM it. Counted per page in a disclosed field whose default keeps
        every existing golden byte-identical (M5-T120 / DB-090 i). This matches the reader-of-record
        leniency — the Canvas-2D "ensure there is a subpath" rule pdf.js relies on, and MuPDF's
        handling [recalled - verify]. Curves (``c``/``v``/``y``) with no current point STAY a typed
        refusal (see :meth:`_curveto` / :meth:`app.drawings.sheet_interpreter._StreamRun._op_v`)."""
        point = self._map(x, y)
        if isinstance(point, SheetRefusal):
            return point
        self._cur_points = [point]
        self._current = point
        self._subpath_start = point
        self._interp.page_orphan_subpaths += 1
        self._interp.orphan_subpaths += 1
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
        # Thread the TIGHTER of the page-remaining and document-remaining point budgets INTO
        # flattening (M5-T118): a degenerate curve stops and refuses at whichever budget is
        # closer instead of first materializing 2**MAX_FLATTEN_DEPTH points (G5 F1 / G3 F1).
        page_remaining = interp.limits.max_page_path_points - interp.page_point_count
        doc_remaining = interp.limits.max_document_path_points - interp.point_count
        remaining = min(page_remaining, doc_remaining)
        if remaining < 0:
            remaining = 0
        out: list[Point] = []
        completed = interp.flatten_cubic(p0, p1, p2, p3, interp.tolerance, out, 0, remaining)
        if not completed:
            if page_remaining <= doc_remaining:
                return _refuse(
                    "path points",
                    f"over {interp.limits.max_page_path_points} flattened points",
                )
            return _refuse(
                "path point ceiling",
                f"over {interp.limits.max_document_path_points} flattened points across "
                "the document",
            )
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
        interp.page_point_count += count
        if interp.page_point_count > interp.limits.max_page_path_points:
            return _refuse(
                "path points", f"over {interp.limits.max_page_path_points} flattened points"
            )
        if interp.point_count > interp.limits.max_document_path_points:
            return _refuse(
                "path point ceiling",
                f"over {interp.limits.max_document_path_points} flattened points across "
                "the document",
            )
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


_PATH_HANDLERS = {
    "m": _PathState._op_m,
    "l": _PathState._op_l,
    "c": _PathState._op_c,
    "v": _PathState._op_v,
    "y": _PathState._op_y,
    "h": _PathState._op_h,
}
