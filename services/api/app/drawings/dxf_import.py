"""D-087 PKT-F DXF import service (pure; no route, no persistence).

Turns an accepted strict-subset DXF read (:func:`app.drawings.dxf_reader.read_dxf`)
into two things, and NOTHING else - it does no I/O, opens no socket, and persists
nothing (plan section 4 (e)):

* a CANDIDATE listing - the closed rings, each with its layer, vertex count and
  measured dimensions in the drawing's DECLARED units - plus a disclosure of the
  non-candidate primitives the reader saw; and
* a proposed_massing DRAFT built ONLY from the roles the USER assigns
  (building outline / property line / street frontage) and the units the USER
  confirms (a feet-family unit, or a scale derived from a known real-world
  dimension), run through the SAME :func:`app.scenario.proposal.
  validate_proposed_massing` contract that governs every proposed building.

Honesty and provenance (D-076-R002 / D-083-R006):

* nothing is ever labelled a city record, a permit, "approved", or a "maximum
  allowed building"; a proposal-derived geometry is only ``"Proposed - not a city
  record"``;
* the draft carries INPUT-PRECISION provenance - ``"imported drawing - not
  survey-confirmed"`` - and this module upgrades it nowhere;
* a declared/confirmed UNIT mismatch (or any other discrepancy) is SHOWN, never
  silently reconciled - the service uses the user's confirmed units and reports
  the conflict so the user can verify the drawing.

Untrusted drawing text (DB-070 (a),(b)): the reader deliberately KEEPS ASCII
control characters inside TEXT values, layer names and ``$ACADVER`` for
provenance. This module escapes every drawing-derived string on output with
:func:`_escape_drawing_text` and bounds its length, so a route emits no raw
control byte and reflects no unbounded raw content. The service raises nothing to
a caller: every failure is a typed :class:`ImportRefusal` VALUE.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from dataclasses import field as dc_field

from app.drawings.dxf_reader import (
    DxfDocument,
    DxfReadResult,
    DxfRefusal,
    DxfUnits,
    PolylinePrimitive,
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
    "FEET_PER_UNIT",
    "MAX_DRAWING_TEXT_CHARS",
    "Candidate",
    "CandidatesResult",
    "DraftResult",
    "ImportRefusal",
    "RoleAssignment",
    "build_draft",
    "list_candidates",
    "measured_dimensions",
    "sniff_dxf_media",
]

# --- honesty vocabulary (D-076-R002 / D-083; NEVER "permitted"/"approved"/"maximum") ---
DRAFT_SOURCE_LABEL = "Proposed - not a city record"
DRAFT_INPUT_PRECISION = "imported drawing - not survey-confirmed"
DRAFT_INPUT_CLASS = "imported_drawing"

# --- role names the user may assign to a candidate ring ---
BUILDING_OUTLINE = "building_outline"
PROPERTY_LINE = "property_line"
STREET_FRONTAGE = "street_frontage"

# The proposed_massing contract requires EPSG:2263 (NYC, US survey feet). The draft
# is expressed in that frame; a drawing that is not georeferenced to NY state plane
# simply fails the contract's NYC-bounds check and the failure is surfaced, never
# auto-corrected (no georeferencing is implied - SURVEY_DOCUMENT_FORMAT_POLICY).
_REQUIRED_SRID = 2263
EDITOR_VERSION = "dxf-import/1"

# Feet-per-unit scale for the units a user may confirm. FEET FAMILY ONLY, all EXACT
# rational conversions: a metre/other-unit conversion into a frame labelled US survey
# feet would assert a CRS/units interpretation this phase does not prove, so it is
# refused (see build_draft). us_survey_feet vs international feet differ by ~2 ppm;
# treated as 1.0 for a draft (disclosed as a known limitation in the producer report).
FEET_PER_UNIT: dict[str, float] = {
    "feet": 1.0,
    "us_survey_feet": 1.0,
    "inches": 1.0 / 12.0,
    "us_survey_inches": 1.0 / 12.0,
    "yards": 3.0,
}

# Every drawing-derived string emitted or embedded is escaped AND bounded to this.
MAX_DRAWING_TEXT_CHARS = 200


@dataclass(frozen=True)
class RoleAssignment:
    """The user's role/unit confirmation for a draft. Built by the route from
    validated query parameters, never from raw drawing content.

    Exactly ONE unit-confirmation mechanism must be supplied: either
    ``confirmed_units`` (a feet-family unit name) OR both ``known_length_ft`` and
    ``measured_length`` (a scale derived from a real-world dimension the user read
    off a candidate). Neither/both is ambiguous and refuses typed.
    """

    building_outline: int
    floors: int
    floor_to_floor_ft: float
    author: str
    property_line: int | None = None
    street_frontage: int | None = None
    confirmed_units: str | None = None
    known_length_ft: float | None = None
    measured_length: float | None = None


@dataclass(frozen=True)
class Candidate:
    """A closed-ring candidate the user may assign a role to."""

    index: int
    entity_type: str
    layer: str
    vertex_count: int
    measured: dict[str, float | str]


@dataclass(frozen=True)
class CandidatesResult:
    """Successful candidate listing (``ok = True``)."""

    ok: bool
    declared_units: dict[str, object]
    acad_version: str | None
    candidates: tuple[Candidate, ...]
    disclosure: dict[str, object]


@dataclass(frozen=True)
class DraftResult:
    """A validated proposed_massing DRAFT (``ok = True``).

    ``proposed_massing`` has already passed :func:`validate_proposed_massing`;
    ``provenance`` carries the input-precision honesty block; ``discrepancies`` are
    SHOWN, not reconciled.
    """

    ok: bool
    proposed_massing: dict
    provenance: dict
    discrepancies: tuple[dict, ...]


@dataclass(frozen=True)
class ImportRefusal:
    """Typed refusal VALUE (``ok = False``); never a raised exception.

    ``reason`` is a short closed-vocabulary token; ``detail`` is a bounded human
    string; ``field`` names the offending field when one applies. ``discrepancies``
    carries any conflicts detected before the refusal so they are still shown.
    """

    ok: bool
    reason: str
    detail: str
    field: str | None = None
    discrepancies: tuple[dict, ...] = dc_field(default_factory=tuple)


# --------------------------------------------------------------------------- helpers


def _escape_drawing_text(value: str | None, *, max_len: int = MAX_DRAWING_TEXT_CHARS) -> str | None:
    """Escape a drawing-derived string for safe output and bound its length.

    ASCII control characters (``ord < 32`` or ``0x7f``) are rendered as ``\\xNN`` so
    no raw control byte reaches a client or a log; the result is then capped with an
    explicit truncation marker (DB-070 (a),(b)). ``None`` passes through unchanged.
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


def measured_dimensions(
    vertices: tuple[tuple[float, float], ...], unit_name: str
) -> dict[str, float | str]:
    """Bounding box, perimeter and area of a closed ring in its DECLARED units.

    ``vertices`` are the distinct ring points (the DXF closed flag implies closure;
    the first point is NOT repeated). Values are reported verbatim in ``unit_name``;
    the drawing units are never coerced to feet here.
    """
    xs = [x for x, _ in vertices]
    ys = [y for _, y in vertices]
    n = len(vertices)
    perimeter = 0.0
    area2 = 0.0
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]  # closing edge included (ring)
        perimeter += math.hypot(x1 - x0, y1 - y0)
        area2 += x0 * y1 - x1 * y0
    return {
        "units": unit_name,
        "bbox_width": (max(xs) - min(xs)) if xs else 0.0,
        "bbox_height": (max(ys) - min(ys)) if ys else 0.0,
        "perimeter": perimeter,
        "area": abs(area2) / 2.0,
    }


def sniff_dxf_media(content_type: str | None, raw: bytes) -> ImportRefusal | None:
    """Content-type + magic-byte gate at the seam (plan section 4 (d)): ASCII DXF
    only, the binary-DXF sentinel refused. Returns an :class:`ImportRefusal` when the
    upload is not acceptable, else ``None`` (only then do the exact bytes reach
    ``read_dxf``). Pure and cheap - it inspects a bounded prefix.
    """
    # Binary DXF is refused before anything else, on the raw bytes (most specific).
    if raw[:18] == b"AutoCAD Binary DXF":
        return ImportRefusal(
            ok=False,
            reason="unsupported_media_type",
            detail="binary DXF is not accepted; ASCII DXF only",
        )
    media = (content_type or "").split(";", 1)[0].strip().lower()
    allowed = {
        "application/dxf",
        "image/vnd.dxf",
        "image/x-dxf",
        "application/octet-stream",
        "text/plain",
    }
    if media and media not in allowed:
        return ImportRefusal(
            ok=False,
            reason="unsupported_media_type",
            detail=f"content-type {media!r} is not an accepted DXF upload type",
        )
    prefix = raw[:4096]
    try:
        text = prefix.decode("ascii")
    except UnicodeDecodeError:
        return ImportRefusal(
            ok=False,
            reason="unsupported_media_type",
            detail="upload is not ASCII; this reader accepts ASCII DXF only",
        )
    # An ASCII DXF always carries a SECTION marker; its absence means "not a DXF".
    if "SECTION" not in text:
        return ImportRefusal(
            ok=False,
            reason="unsupported_media_type",
            detail="upload has no DXF SECTION marker; not an ASCII DXF file",
        )
    return None


def _units_block(doc: DxfDocument) -> dict[str, object]:
    return {"code": doc.units.code, "name": doc.units.name, "source": doc.units.source}


def _refusal_from_read(refusal: DxfRefusal) -> ImportRefusal:
    """Map a reader :class:`DxfRefusal` to a typed :class:`ImportRefusal`, bounding
    the reader detail (which may embed repr-escaped raw content, DB-070 (b))."""
    return ImportRefusal(
        ok=False,
        reason="unreadable_dxf",
        detail=_escape_drawing_text(f"{refusal.reason.value}: {refusal.detail}") or "",
    )


def _closed_ring_candidates(doc: DxfDocument) -> list[tuple[int, PolylinePrimitive]]:
    out: list[tuple[int, PolylinePrimitive]] = []
    for prim in doc.primitives:
        if isinstance(prim, PolylinePrimitive) and prim.closed and len(prim.vertices) >= 3:
            out.append((len(out), prim))
    return out


def list_candidates(doc: DxfReadResult) -> CandidatesResult | ImportRefusal:
    """List the closed-ring candidates and disclose the non-candidate primitives.

    A reader refusal is returned as a typed :class:`ImportRefusal`; nothing is
    labelled a record or a permitted value.
    """
    if isinstance(doc, DxfRefusal):
        return _refusal_from_read(doc)

    rings = _closed_ring_candidates(doc)
    candidates = tuple(
        Candidate(
            index=idx,
            entity_type=prim.entity_type,
            layer=_escape_drawing_text(prim.layer) or "0",
            vertex_count=len(prim.vertices),
            measured=measured_dimensions(prim.vertices, doc.units.name),
        )
        for idx, prim in rings
    )
    # Disclose everything that was NOT a candidate so the user sees the full picture.
    open_polylines = sum(
        1 for p in doc.primitives if isinstance(p, PolylinePrimitive) and not p.closed
    )
    kinds = {"LINE": 0, "3DFACE": 0, "TEXT": 0}
    for p in doc.primitives:
        if type(p).__name__ == "LinePrimitive":
            kinds["LINE"] += 1
        elif type(p).__name__ == "FacePrimitive":
            kinds["3DFACE"] += 1
        elif type(p).__name__ == "TextPrimitive":
            kinds["TEXT"] += 1
    disclosure = {
        "open_polylines": open_polylines,
        "lines": kinds["LINE"],
        "faces": kinds["3DFACE"],
        "text": kinds["TEXT"],
        "disclosed_unknown": [
            [_escape_drawing_text(name), count] for name, count in doc.disclosed_unknown
        ],
        "skipped_sections": [_escape_drawing_text(s) for s in doc.skipped_sections],
        "entity_count": doc.entity_count,
    }
    return CandidatesResult(
        ok=True,
        declared_units=_units_block(doc),
        acad_version=_escape_drawing_text(doc.acad_version),
        candidates=candidates,
        disclosure=disclosure,
    )


def _resolve_scale(
    assignment: RoleAssignment, declared: DxfUnits
) -> tuple[float, str, tuple[dict, ...]] | ImportRefusal:
    """Resolve the feet-per-unit scale and record any unit discrepancy (SHOWN, never
    reconciled). Exactly one confirmation mechanism must be supplied."""
    by_name = assignment.confirmed_units is not None
    by_dim = assignment.known_length_ft is not None or assignment.measured_length is not None
    if by_name == by_dim:
        return ImportRefusal(
            ok=False,
            reason="ambiguous_units",
            detail=(
                "confirm units EITHER by a feet-family unit name OR by a known "
                "dimension (known_length_ft + measured_length), not neither and not both"
            ),
            field="confirmed_units",
        )
    discrepancies: list[dict] = []
    if by_name:
        name = assignment.confirmed_units or ""
        if name not in FEET_PER_UNIT:
            return ImportRefusal(
                ok=False,
                reason="unsupported_units",
                detail=(
                    f"confirmed_units {name!r} is not a supported feet-family unit "
                    f"({sorted(FEET_PER_UNIT)}); convert the drawing or use a known dimension"
                ),
                field="confirmed_units",
            )
        # A drawing that DECLARED any real unit differing from the confirmed one is a
        # DISCREPANCY: shown, never auto-reconciled - the confirmed unit drives the scale.
        if declared.code is not None and declared.name != "unitless" and declared.name != name:
            discrepancies.append(
                {
                    "type": "units_mismatch",
                    "declared": declared.name,
                    "confirmed": name,
                    "detail": (
                        "the drawing declares a different unit than you confirmed; the "
                        "confirmed unit is used - verify the drawing (not auto-reconciled)"
                    ),
                }
            )
        return FEET_PER_UNIT[name], "confirmed_units", tuple(discrepancies)
    # Known-dimension path: scale = known real-world feet / measured drawing length.
    known = assignment.known_length_ft
    measured = assignment.measured_length
    if known is None or measured is None:
        return ImportRefusal(
            ok=False,
            reason="ambiguous_units",
            detail="known_length_ft and measured_length must BOTH be supplied together",
            field="known_length_ft",
        )
    if not (math.isfinite(known) and math.isfinite(measured)) or known <= 0 or measured <= 0:
        return ImportRefusal(
            ok=False,
            reason="unsupported_units",
            detail="known_length_ft and measured_length must be finite and strictly positive",
            field="known_length_ft",
        )
    return known / measured, "known_dimension", tuple(discrepancies)


def _outline_vertices(prim: PolylinePrimitive, scale: float) -> list[list[float]]:
    """Scale the ring and make its closure EXPLICIT (proposal outlines repeat the
    first vertex). This surfaces the reader's flag-implied closure; it is not a
    geometric reconciliation of the drawing."""
    pts = [[x * scale, y * scale] for x, y in prim.vertices]
    if pts and pts[0] == pts[-1]:  # defensive: drop an already-present closing dup
        pts = pts[:-1]
    pts.append([pts[0][0], pts[0][1]])
    return pts


def build_draft(doc: DxfReadResult, assignment: RoleAssignment) -> DraftResult | ImportRefusal:
    """Build a proposed_massing DRAFT from the user's assignment and confirmed units,
    validated through :func:`validate_proposed_massing`. Discrepancies are shown, never
    reconciled; nothing is labelled a record or a permitted value; the draft carries
    input-precision provenance no later step upgrades (D-083-R006)."""
    if isinstance(doc, DxfRefusal):
        return _refusal_from_read(doc)

    rings = _closed_ring_candidates(doc)
    n = len(rings)

    def _in_range(idx: int | None, field_name: str) -> ImportRefusal | None:
        if idx is None:
            return None
        if not (0 <= idx < n):
            return ImportRefusal(
                ok=False,
                reason="bad_candidate",
                detail=f"{field_name} candidate {idx} is out of range (0..{n - 1})",
                field=field_name,
            )
        return None

    for idx, fname in (
        (assignment.building_outline, "building_outline"),
        (assignment.property_line, "property_line"),
        (assignment.street_frontage, "street_frontage"),
    ):
        refusal = _in_range(idx, fname)
        if refusal is not None:
            return refusal

    scale_res = _resolve_scale(assignment, doc.units)
    if isinstance(scale_res, ImportRefusal):
        return scale_res
    scale, scale_source, discrepancies = scale_res

    outline_prim = rings[assignment.building_outline][1]
    author = _escape_drawing_text(assignment.author) or ""
    block = {
        "outline": {"srid": _REQUIRED_SRID, "vertices": _outline_vertices(outline_prim, scale)},
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
            discrepancies=discrepancies,
        )

    provenance = {
        "input_class": DRAFT_INPUT_CLASS,
        "precision": DRAFT_INPUT_PRECISION,
        "label": DRAFT_SOURCE_LABEL,
        "declared_units": _units_block(doc),
        "confirmed_units": assignment.confirmed_units,
        "unit_scale_ft_per_unit": scale,
        "scale_source": scale_source,
        "assigned_roles": {
            BUILDING_OUTLINE: assignment.building_outline,
            PROPERTY_LINE: assignment.property_line,
            STREET_FRONTAGE: assignment.street_frontage,
        },
        "acad_version": _escape_drawing_text(doc.acad_version),
        "author": author,
    }
    return DraftResult(
        ok=True, proposed_massing=block, provenance=provenance, discrepancies=discrepancies
    )
