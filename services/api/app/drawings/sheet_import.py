"""D-087 PKT-L (phase C2/C3) PDF sheet import service (pure; no route, no persistence).

The PDF counterpart of the accepted DXF import service
(:mod:`app.drawings.dxf_import`, M5-T108 - the precedent this module MIRRORS; it is
READ-ONLY here and never modified). Given a :class:`~app.drawings.sheet_primitives.
SheetDocument` from :func:`app.drawings.sheet_reader.read_sheet` and a page index, this
module turns a read architect PDF page into two things and NOTHING else - it does no
I/O, opens no socket, and persists nothing:

* a CANDIDATE listing - the CLOSED polylines of the chosen page, each addressed by its
  STABLE polyline index on that page, with its vertex count and measured dimensions in
  SHEET units (the page's PDF user space) - bounded (:data:`MAX_LISTED_CANDIDATES`,
  largest area first, the total disclosed), plus a disclosure of what else the page
  holds (open polylines, degenerate closed rings, text runs, images, the reader's
  shading / inline-image skip counts) and the page's text runs containing the word
  ``"scale"`` LISTED escaped + length-bounded as reference notes only, NEVER parsed; and
* a proposed_massing DRAFT (C3) built ONLY from the roles the USER assigns (building
  outline / property line / street frontage) and a scale the SERVICE measures itself
  from ONE user-named edge (a candidate index + an edge index + the edge's real length
  in feet). The draft runs through the SAME :func:`app.scenario.proposal.
  validate_proposed_massing` contract that governs every proposed building (the
  contract's ``provenance.kind`` stays ``"proposed"``), and carries a SEPARATE
  provenance block with ``input_class = "imported_pdf"``.

Honesty and provenance (D-076-R002 / D-083-R006):

* nothing is ever labelled a city record, a permit, "approved", or a "maximum allowed
  building"; a proposal-derived geometry is only ``"Proposed - not a city record"``;
* the draft carries INPUT-PRECISION provenance - ``"imported drawing - not
  survey-confirmed"`` - and this module upgrades it nowhere;
* the outline is in a LOCAL scaled sheet frame, disclosed as such - it is NOT aligned to
  the mapped lot (alignment is a later C2 step), never silently georeferenced.

Untrusted drawing text (the M5-T108 G5 lesson DB-070 (a),(b)): every drawing-derived
string in any output (scale notes, anything from the file) is escaped so no raw control
byte reaches a caller or a log, and length-bounded. The DXF escape helper is private, so
the SAME rule is implemented here as :func:`_escape_drawing_text` with its own tests.

Reused from :mod:`app.drawings.dxf_import` (PUBLIC names only; that module is never
modified): :func:`~app.drawings.dxf_import.measured_dimensions` (the ring geometry fits
verbatim), the honesty label constants ``DRAFT_SOURCE_LABEL`` /
``DRAFT_INPUT_PRECISION``, the role-name constants ``BUILDING_OUTLINE`` /
``PROPERTY_LINE`` / ``STREET_FRONTAGE``, and the ``MAX_DRAWING_TEXT_CHARS`` bound. The
typed value shapes below MIRROR the DXF ones but are defined locally (their fields
differ: a page index, a service-measured edge scale, and NO client-supplied
measurement). The service raises nothing to a caller: every failure is a typed
:class:`ImportRefusal` VALUE.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.drawings.dxf_import import (
    BUILDING_OUTLINE,
    DRAFT_INPUT_PRECISION,
    DRAFT_SOURCE_LABEL,
    MAX_DRAWING_TEXT_CHARS,
    PROPERTY_LINE,
    STREET_FRONTAGE,
    measured_dimensions,
)
from app.drawings.sheet_primitives import (
    SheetDocument,
    SheetPage,
    SheetPolyline,
    SheetRefusal,
)
from app.scenario.proposal import ProposedMassingError, validate_proposed_massing

__all__ = [
    "BUILDING_OUTLINE",
    "PROPERTY_LINE",
    "STREET_FRONTAGE",
    "DRAFT_INPUT_CLASS",
    "DRAFT_INPUT_PRECISION",
    "DRAFT_SOURCE_LABEL",
    "EDITOR_VERSION",
    "FRAME_NOTE",
    "MAX_DRAWING_TEXT_CHARS",
    "MAX_LISTED_CANDIDATES",
    "MAX_SCALE_NOTES",
    "MAX_KNOWN_LENGTH_FT",
    "MAX_SCALE_FT_PER_UNIT",
    "SHEET_UNIT_NAME",
    "Candidate",
    "CandidatesResult",
    "DraftResult",
    "ImportRefusal",
    "RoleAssignment",
    "build_draft",
    "list_candidates",
    "measured_dimensions",
]

# --- honesty vocabulary --------------------------------------------------------------
# DRAFT_SOURCE_LABEL / DRAFT_INPUT_PRECISION are REUSED from dxf_import (identical
# vocabulary). The input CLASS is this module's own - a PDF sheet, not a DXF drawing.
DRAFT_INPUT_CLASS = "imported_pdf"
EDITOR_VERSION = "pdf-sheet-import/1"
FRAME_NOTE = (
    "outline is in a LOCAL scaled sheet frame, not aligned to the mapped lot; "
    "alignment to the mapped lot is a later step"
)

# The proposed_massing contract requires EPSG:2263 (NYC, US survey feet). The draft is
# EXPRESSED in that frame exactly as the DXF precedent does; a LOCAL sheet frame whose
# scaled coordinates do not fall inside NY state plane simply fails the contract's
# NYC-bounds check and the failure is surfaced typed, NEVER auto-corrected (no
# georeferencing is implied - alignment to the mapped lot is a separate C2 step).
_REQUIRED_SRID = 2263

# The unit label reported on measured dimensions. Values are in the page's PDF user
# space (1 unit = 1/72 inch, scaled by the page ``/UserUnit``); they are NOT converted to
# feet here - the user-named edge + known length is what establishes real-world scale.
SHEET_UNIT_NAME = "pdf_user_space"

# --- bounds (declared; fail-closed) --------------------------------------------------
# A page with more closed rings than this still DISCLOSES the total; only the LISTED
# candidates are capped (largest area first). Assignment in build_draft validates against
# EVERY closed ring by stable index, so the display cap never hides an assignable ring.
MAX_LISTED_CANDIDATES = 200
# Scale reference notes (text runs containing "scale") are listed as reference only; the
# count is capped and each note is escaped + length-bounded. NEVER parsed into a scale.
MAX_SCALE_NOTES = 50
# A user-named real-world edge length must be finite, strictly positive and below this
# absurd ceiling (a paste / unit error above it fails closed).
MAX_KNOWN_LENGTH_FT = 1_000_000.0
# The resolved feet-per-unit scale must be finite, strictly positive and within these
# generous bounds; outside is a degenerate / garbage scale and refuses typed.
MIN_SCALE_FT_PER_UNIT = 1e-9
MAX_SCALE_FT_PER_UNIT = 1e9


@dataclass(frozen=True)
class RoleAssignment:
    """The user's role + scale confirmation for a draft. Built by a route from validated
    query parameters, NEVER from raw drawing content.

    The scale is a SINGLE user-named edge (``scale_candidate`` + ``scale_edge``) and its
    real-world ``known_length_ft``; the SERVICE measures that edge on the sheet itself and
    computes ``scale = known_length_ft / measured_length``. There is DELIBERATELY no
    ``measured_length`` / client-measurement field: a caller cannot supply the sheet
    measurement (mirrors the DXF known-dimension path but removes its client-supplied
    ``measured_length``).
    """

    building_outline: int
    floors: int
    floor_to_floor_ft: float
    author: str
    scale_candidate: int
    scale_edge: int
    known_length_ft: float
    property_line: int | None = None
    street_frontage: int | None = None


@dataclass(frozen=True)
class Candidate:
    """A closed-ring candidate the user may assign a role to, addressed by its STABLE
    polyline index on the page (its position in ``SheetPage.polylines``)."""

    index: int
    vertex_count: int
    measured: dict[str, float | str]


@dataclass(frozen=True)
class CandidatesResult:
    """Successful candidate listing for one page (``ok = True``)."""

    ok: bool
    page_index: int
    page_count: int
    user_unit: float
    unit_name: str
    total_closed_rings: int
    candidates: tuple[Candidate, ...]
    scale_notes: tuple[str, ...]
    disclosure: dict[str, object]


@dataclass(frozen=True)
class DraftResult:
    """A validated proposed_massing DRAFT (``ok = True``).

    ``proposed_massing`` has already passed :func:`validate_proposed_massing`;
    ``provenance`` carries the input-precision honesty block, the page index, the named
    edge + known length + measured length + scale, the assigned roles and the LOCAL-frame
    note.
    """

    ok: bool
    proposed_massing: dict
    provenance: dict


@dataclass(frozen=True)
class ImportRefusal:
    """Typed refusal VALUE (``ok = False``); never a raised exception.

    ``reason`` is a short closed-vocabulary token; ``detail`` is a bounded human string;
    ``field`` names the offending field when one applies.
    """

    ok: bool
    reason: str
    detail: str
    field: str | None = None


# --------------------------------------------------------------------------- helpers


def _escape_drawing_text(
    value: str | None, *, max_len: int = MAX_DRAWING_TEXT_CHARS
) -> str | None:
    """Escape a drawing-derived string for safe output and bound its length.

    ASCII control characters (``ord < 0x20`` or ``0x7f``) are rendered as ``\\xNN`` so no
    raw control byte reaches a client or a log; the result is then capped with an explicit
    truncation marker (DB-070 (a),(b)). ``None`` passes through unchanged. This is the
    LOCAL implementation of the same rule the DXF module keeps private.
    """
    if value is None:
        return None
    out: list[str] = []
    for ch in value:
        code = ord(ch)
        if code < 0x20 or code == 0x7F:
            out.append(f"\\x{code:02x}")
        else:
            out.append(ch)
    escaped = "".join(out)
    if len(escaped) > max_len:
        return escaped[:max_len] + f"...<truncated; {len(escaped)} chars>"
    return escaped


def _measured_is_finite(measured: dict[str, float | str]) -> bool:
    """Whether every NUMERIC measured value is finite. A coordinate that is individually
    finite but huge (e.g. ``1e300``) makes the shoelace products / bbox span OVERFLOW to
    ``inf`` (the M5-T108 G5 MEDIUM 1 lesson); such a value is JSON-non-compliant under
    ``allow_nan=False`` and would otherwise render an untyped 500. The service refuses it
    as a typed ``coordinate_out_of_range`` instead."""
    return all(
        math.isfinite(v) for v in measured.values() if isinstance(v, (int, float))
    )


def _refusal_from_read(refusal: SheetRefusal) -> ImportRefusal:
    """Map a reader :class:`SheetRefusal` to a typed :class:`ImportRefusal`, escaping and
    bounding the reader detail (which may reflect file-derived content)."""
    detail = (
        f"{refusal.reject_code}/{refusal.feature}: {refusal.detail} "
        f"(origin {refusal.origin})"
    )
    return ImportRefusal(
        ok=False,
        reason="unreadable_pdf",
        detail=_escape_drawing_text(detail) or "",
    )


def _page_from_doc(
    doc: SheetDocument, page_index: int
) -> SheetPage | ImportRefusal:
    """Resolve the chosen page, or a typed ``page_out_of_range`` refusal. A non-integer or
    out-of-range index is an honest typed result, never an IndexError to the caller."""
    n = len(doc.pages)
    if not isinstance(page_index, int) or isinstance(page_index, bool):
        return ImportRefusal(
            ok=False,
            reason="page_out_of_range",
            detail="page_index must be an integer",
            field="page_index",
        )
    if not (0 <= page_index < n):
        return ImportRefusal(
            ok=False,
            reason="page_out_of_range",
            detail=f"page_index {page_index} is out of range (0..{n - 1})",
            field="page_index",
        )
    return doc.pages[page_index]


def _closed_ring_candidates(page: SheetPage) -> list[tuple[int, SheetPolyline]]:
    """The page's CLOSED polylines with >= 3 points, each paired with its STABLE polyline
    index (its position in ``page.polylines``), in stable-index order. This is the full
    ADDRESSABLE set; the display listing caps and re-orders a copy of it."""
    out: list[tuple[int, SheetPolyline]] = []
    for stable_index, poly in enumerate(page.polylines):
        if poly.closed and len(poly.points) >= 3:
            out.append((stable_index, poly))
    return out


def _rings_by_index(page: SheetPage) -> dict[int, SheetPolyline]:
    """Stable-index -> closed ring lookup for role / scale resolution."""
    return {idx: poly for idx, poly in _closed_ring_candidates(page)}


def _disclosure(page: SheetPage, rings: list[tuple[int, SheetPolyline]]) -> dict[str, object]:
    """Disclose everything the page holds that is NOT a listed closed-ring candidate, so
    the user sees the full picture (open polylines, degenerate closed rings, text runs,
    images, the reader's disclosed skip counts)."""
    open_polylines = 0
    degenerate_closed_rings = 0
    for poly in page.polylines:
        if not poly.closed:
            open_polylines += 1
        elif len(poly.points) < 3:
            # A CLOSED subpath with < 3 points is not a candidate AND not an open
            # polyline; disclose it so it is never silently absent from both counts.
            degenerate_closed_rings += 1
    note = ""
    if not rings:
        # The no-closed-ring case: honest about WHY there are no candidates.
        note = (
            "no closed rings on this page; an outline drawn as separate line segments "
            "is not joined into a closed ring yet"
        )
    return {
        "open_polylines": open_polylines,
        "degenerate_closed_rings": degenerate_closed_rings,
        "text_runs": len(page.text_runs),
        "images": page.image_count,
        "shading_skips": page.shading_skips,
        "inline_image_skips": page.inline_image_skips,
        "media_box": list(page.media_box),
        "flatten_tolerance": page.flatten_tolerance,
        "note": note,
    }


def _scale_notes(page: SheetPage) -> tuple[str, ...]:
    """Text runs whose text contains ``"scale"`` (case-insensitive), LISTED escaped and
    length-bounded as reference notes ONLY. They are NEVER parsed into a scale - the scale
    comes exclusively from the user-named edge the service measures."""
    notes: list[str] = []
    for run in page.text_runs:
        text = run.text
        if isinstance(text, str) and "scale" in text.lower():
            escaped = _escape_drawing_text(text)
            if escaped is not None:
                notes.append(escaped)
            if len(notes) >= MAX_SCALE_NOTES:
                break
    return tuple(notes)


def list_candidates(
    doc: SheetDocument | SheetRefusal, page_index: int
) -> CandidatesResult | ImportRefusal:
    """List the chosen page's closed-ring candidates and disclose the rest of the page.

    A reader refusal is returned as a typed :class:`ImportRefusal`; an out-of-range page
    or a page with no closed ring is an honest typed result; nothing is labelled a record
    or a permitted value.
    """
    if isinstance(doc, SheetRefusal):
        return _refusal_from_read(doc)

    page = _page_from_doc(doc, page_index)
    if isinstance(page, ImportRefusal):
        return page

    rings = _closed_ring_candidates(page)
    built: list[Candidate] = []
    for stable_index, poly in rings:
        measured = measured_dimensions(poly.points, SHEET_UNIT_NAME)
        # A huge-but-finite ring overflows the measured dimensions to inf; refuse typed
        # here so a route never emits a non-finite value that breaks JSON render.
        if not _measured_is_finite(measured):
            return ImportRefusal(
                ok=False,
                reason="coordinate_out_of_range",
                detail=(
                    f"candidate ring at polyline index {stable_index} has coordinates so "
                    "large its measured dimensions overflow to a non-finite value; the "
                    "page is out of the representable range"
                ),
                field="building_outline",
            )
        built.append(
            Candidate(
                index=stable_index,
                vertex_count=len(poly.points),
                measured=measured,
            )
        )
    # Bounded display: largest area first, capped; the TOTAL is disclosed separately so
    # the cap never hides that more closed rings exist on the page.
    built.sort(key=lambda c: (-_area_of(c), c.index))
    listed = tuple(built[:MAX_LISTED_CANDIDATES])
    return CandidatesResult(
        ok=True,
        page_index=page_index,
        page_count=len(doc.pages),
        user_unit=page.user_unit,
        unit_name=SHEET_UNIT_NAME,
        total_closed_rings=len(rings),
        candidates=listed,
        scale_notes=_scale_notes(page),
        disclosure=_disclosure(page, rings),
    )


def _area_of(candidate: Candidate) -> float:
    """The candidate's measured area as a finite float for ordering (0.0 if absent)."""
    value = candidate.measured.get("area", 0.0)
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else 0.0


def _measure_edge(prim: SheetPolyline, edge_index: int) -> float | ImportRefusal:
    """Measure the length of ONE edge of a closed ring on the sheet, in sheet units.

    A closed ring's edges are ``(points[i], points[(i + 1) % n])`` for ``i`` in
    ``0..n-1`` (the closing edge included). The SERVICE measures the edge itself from the
    geometry - a caller can never supply this measurement. A degenerate (zero-length) or
    non-finite edge refuses typed.
    """
    n = len(prim.points)
    if not isinstance(edge_index, int) or isinstance(edge_index, bool) or not (
        0 <= edge_index < n
    ):
        return ImportRefusal(
            ok=False,
            reason="bad_edge",
            detail=f"scale_edge {edge_index} is out of range (0..{n - 1})",
            field="scale_edge",
        )
    x0, y0 = prim.points[edge_index]
    x1, y1 = prim.points[(edge_index + 1) % n]
    length = math.hypot(x1 - x0, y1 - y0)
    if not math.isfinite(length) or length <= 0.0:
        return ImportRefusal(
            ok=False,
            reason="invalid_scale",
            detail=(
                f"the named edge (candidate edge {edge_index}) has a non-finite or "
                "zero measured length; it cannot establish a scale"
            ),
            field="scale_edge",
        )
    return length


def _resolve_scale(
    page: SheetPage, assignment: RoleAssignment
) -> tuple[float, float, SheetPolyline] | ImportRefusal:
    """Resolve the feet-per-sheet-unit scale from the user-named edge the service
    measures. Returns ``(scale, measured_length, scale_ring)`` or a typed refusal."""
    rings = _rings_by_index(page)
    scale_ring = rings.get(assignment.scale_candidate)
    if scale_ring is None:
        return ImportRefusal(
            ok=False,
            reason="bad_candidate",
            detail=(
                f"scale_candidate {assignment.scale_candidate} is not a closed ring on "
                "this page"
            ),
            field="scale_candidate",
        )
    known = assignment.known_length_ft
    if (
        isinstance(known, bool)
        or not isinstance(known, (int, float))
        or not math.isfinite(known)
        or known <= 0.0
        or known > MAX_KNOWN_LENGTH_FT
    ):
        return ImportRefusal(
            ok=False,
            reason="invalid_scale",
            detail=(
                "known_length_ft must be a finite, strictly-positive number of feet "
                f"within (0, {MAX_KNOWN_LENGTH_FT}]"
            ),
            field="known_length_ft",
        )
    measured = _measure_edge(scale_ring, assignment.scale_edge)
    if isinstance(measured, ImportRefusal):
        return measured
    scale = float(known) / measured
    if (
        not math.isfinite(scale)
        or scale < MIN_SCALE_FT_PER_UNIT
        or scale > MAX_SCALE_FT_PER_UNIT
    ):
        return ImportRefusal(
            ok=False,
            reason="invalid_scale",
            detail=(
                f"the resolved scale ({scale}) ft per sheet unit is non-finite or "
                f"outside the plausible range [{MIN_SCALE_FT_PER_UNIT}, "
                f"{MAX_SCALE_FT_PER_UNIT}]"
            ),
            field="known_length_ft",
        )
    return scale, measured, scale_ring


def _select_ring(rings: list[tuple[int, SheetPolyline]], index: int) -> SheetPolyline:
    """Return the ring the USER assigned to a role, addressed by its STABLE polyline
    ``index``.

    A dedicated seam so a test can prove the draft is built from the user-assigned ring
    and NOT silently from the first ring or the largest ring (the M5-T108 G4 F1 lesson):
    ``rings`` is ordered by stable index, so this searches for the tuple whose stable
    index equals ``index`` rather than positionally indexing the list.
    """
    for stable_index, poly in rings:
        if stable_index == index:
            return poly
    raise KeyError(index)  # unreachable: build_draft validates the index first


def _outline_vertices(prim: SheetPolyline, scale: float) -> list[list[float]]:
    """Scale the ring and make its closure EXPLICIT (proposal outlines repeat the first
    vertex). This surfaces the reader's flag-implied closure; it is not a geometric
    reconciliation of the drawing."""
    pts = [[x * scale, y * scale] for x, y in prim.points]
    if pts and pts[0] == pts[-1]:  # defensive: drop an already-present closing dup
        pts = pts[:-1]
    pts.append([pts[0][0], pts[0][1]])
    return pts


def build_draft(
    doc: SheetDocument | SheetRefusal, page_index: int, assignment: RoleAssignment
) -> DraftResult | ImportRefusal:
    """Build a proposed_massing DRAFT from the user's role assignment and the
    service-measured edge scale, validated through :func:`validate_proposed_massing`.

    Nothing is labelled a record or a permitted value; the draft carries input-precision
    provenance no later step upgrades (D-083-R006); the outline is disclosed as a LOCAL
    scaled sheet frame, never silently georeferenced.
    """
    if isinstance(doc, SheetRefusal):
        return _refusal_from_read(doc)

    page = _page_from_doc(doc, page_index)
    if isinstance(page, ImportRefusal):
        return page

    rings = _closed_ring_candidates(page)
    by_index = _rings_by_index(page)

    for idx, fname in (
        (assignment.building_outline, "building_outline"),
        (assignment.property_line, "property_line"),
        (assignment.street_frontage, "street_frontage"),
    ):
        if idx is None:
            continue
        if idx not in by_index:
            return ImportRefusal(
                ok=False,
                reason="bad_candidate",
                detail=f"{fname} {idx} is not a closed ring on this page",
                field=fname,
            )

    scale_res = _resolve_scale(page, assignment)
    if isinstance(scale_res, ImportRefusal):
        return scale_res
    scale, measured_length, _scale_ring = scale_res

    outline_prim = _select_ring(rings, assignment.building_outline)
    author = _escape_drawing_text(assignment.author) or ""
    block = {
        "outline": {
            "srid": _REQUIRED_SRID,
            "vertices": _outline_vertices(outline_prim, scale),
        },
        "levels": [
            {
                "level_index": 0,
                "floor_count": assignment.floors,
                "floor_to_floor_ft": assignment.floor_to_floor_ft,
            }
        ],
        "exterior_walls": [],
        "provenance": {"author": author, "editor_version": EDITOR_VERSION, "kind": "proposed"},
    }
    try:
        validate_proposed_massing(block)
    except ProposedMassingError as exc:
        return ImportRefusal(
            ok=False,
            reason="draft_invalid",
            detail=_escape_drawing_text(str(exc)) or "",
            field=exc.field,
        )

    provenance = {
        "input_class": DRAFT_INPUT_CLASS,
        "precision": DRAFT_INPUT_PRECISION,
        "label": DRAFT_SOURCE_LABEL,
        "page_index": page_index,
        "scale": {
            "candidate_index": assignment.scale_candidate,
            "edge_index": assignment.scale_edge,
            "known_length_ft": assignment.known_length_ft,
            "measured_sheet_length": measured_length,
            "scale_ft_per_unit": scale,
            "sheet_unit": SHEET_UNIT_NAME,
        },
        "assigned_roles": {
            BUILDING_OUTLINE: assignment.building_outline,
            PROPERTY_LINE: assignment.property_line,
            STREET_FRONTAGE: assignment.street_frontage,
        },
        "frame_note": FRAME_NOTE,
        "author": author,
        "editor_version": EDITOR_VERSION,
    }
    return DraftResult(ok=True, proposed_massing=block, provenance=provenance)
