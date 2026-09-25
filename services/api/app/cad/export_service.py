"""Pure CAD/3D export service - one massing option -> DXF, PDF site plan, or GLB
(task M5-T109, D-087 PKT-D; plan docs/design/d087-export-and-3d-viewer-plan.md §2).

This module is the single, route-free choke point that turns a proposed or generated
massing option (an EPSG:2263 lot ring, an optional building footprint ring, per-floor
heights, and provenance strings) into one of the three accepted export formats via the
already-accepted writers:

* ``dxf`` -> :func:`app.cad.dxf_writer.render_site_plan_dxf` (ASCII DXF text)
* ``pdf`` -> :func:`app.cad.pdf_sheet_writer.render_site_plan_pdf` (PDF 1.4 sheet)
* ``glb`` -> :func:`app.cad.glb_writer.write_glb` (glTF 2.0 binary massing)

It draws NO geometry itself except the GLB massing prism (a single extrusion built from
the accepted writer's public inputs); every byte that leaves the writers is theirs. It
computes NO zoning value and asserts NO legal conclusion.

Guarantees (deterministic, stdlib + already-admitted packages only, no I/O, no clock):

* CAPS BEFORE THE WRITERS. The RAW caller ring length is checked against the tightest
  cap for the requested format BEFORE any per-vertex normalization (DB-057 (d):
  ``dxf_writer._normalize_ring`` coerces the whole raw input to a list before its edge
  cap, so the service caps first). ``floors <= 2000``. Every caller text field is
  length-capped and then claim-word screened (the shared
  :func:`app.cad.claim_words.contains_claim_word`) BEFORE any writer runs.
* ONE RECONCILED, REDACTED REFUSAL. DXF and GLB writers RAISE typed errors; the PDF
  writer RETURNS a typed refusal. This service reconciles all three into one
  :class:`ExportRefusal` ``{reject_code, detail}`` (DB-059 (e)). The detail is built
  SERVER-SIDE from the writer's fixed ``reject_code`` and never echoes any caller value
  (DB-059 (h): the GLB/DXF writers interpolate the caller name/coordinate into their own
  message; this service discards those messages).
* MANDATORY FILENAME SAFETY (plan §2, M5-T099 G5 F1). The download token is built
  server-side from an allowlist (only ``[A-Za-z0-9._-]`` survives), length-capped, and
  derived from the validated bbl and the deterministic ``generated_at``. A token that
  allowlists down to nothing (or only ``.``/``-``/``_``) falls back to a caller-free
  server default (DB-065 (a)). Raw caller text NEVER reaches a header value; the ASCII
  ``filename`` is accompanied by the RFC 6266 / RFC 5987 ``filename*=UTF-8''`` form.
* GLB DEDUPE (DB-054 (m)). The GLB massing is a SINGLE extruded prism from the floor
  base to the roof; per-floor bands are NOT emitted as separate stacked prisms, so no
  coincident interface caps exist to dedupe. This choice is disclosed in the returned
  ``ExportResult.provenance['glb_massing']`` (NOT in the file's ``asset.extras``, whose
  extras carry only the origin / axis / label; M5-T109 G3 A4 / DB-082 (h)).
* CONCAVE-SAFE GLB CAPS (DB-082 (a)). The prism's bottom and top caps are triangulated
  by the ONE public concave-safe massing triangulator
  (:func:`app.scenario.massing_triangulation.triangulate_polygon`), NOT a naive vertex-0
  fan (wrong for an L-shaped or other concave footprint - fan triangles fall outside the
  footprint and over-count its area). Its PREPARED CCW ring is reused for the side walls,
  so caps and walls share ONE boundary and one outward winding (bottom cap facing -z, top
  +z). A non-simple / over-budget / out-of-range footprint is a typed refusal
  (:class:`~app.scenario.massing_guards.MassingModelError`) reconciled to the ONE redacted
  :class:`ExportRefusal` shape, never a malformed mesh. The ear-clipper only detects a
  DUPLICATE-vertex ring, so this service adds an explicit GEOS simplicity gate
  (:func:`_reject_non_simple_ring`) on the PREPARED ring, refusing a crossed 'bowtie' with
  DISTINCT vertices as ``self_intersection`` (G3 B1 / AS-2). Finiteness and the coordinate
  magnitude bound are checked inside the triangulator; the lot-only NYC range check is
  omitted there by design (M5-T112 G5 INFO-1 / DB-084 (d)) and the GLB writer re-validates
  finiteness, the local-coordinate bound and degeneracy.
* HONESTY (D-083 / D-073-R006 / D-076-R002). ``source`` is one of the two allowed
  labels ("Proposed - not a city record" / "Generated building option"); nothing is ever
  labelled permitted, approved, or "maximum allowed building".
"""

from __future__ import annotations

import math
import urllib.parse
from collections.abc import Sequence
from dataclasses import dataclass, field

from shapely.errors import ShapelyError
from shapely.geometry import LinearRing

from app.cad import dxf_writer, glb_writer, pdf_sheet_writer
from app.cad.claim_words import contains_claim_word
from app.scenario.massing_guards import MassingModelError
from app.scenario.massing_triangulation import triangulate_polygon

__all__ = [
    "DXF_MEDIA_TYPE",
    "GLB_MEDIA_TYPE",
    "MAX_FLOORS",
    "MAX_TEXT_CHARS",
    "MAX_TOKEN_LEN",
    "PDF_MEDIA_TYPE",
    "SUPPORTED_FORMATS",
    "ExportRefusal",
    "ExportRequest",
    "ExportResult",
    "build_export",
    "build_filename_token",
    "content_disposition",
]

# --------------------------------------------------------------------------- #
# Per-format media types (plan §2) and the supported format / source vocab.
# --------------------------------------------------------------------------- #

DXF_MEDIA_TYPE = "image/vnd.dxf"
PDF_MEDIA_TYPE = "application/pdf"
GLB_MEDIA_TYPE = glb_writer.GLB_MEDIA_TYPE  # "model/gltf-binary"

SUPPORTED_FORMATS: frozenset[str] = frozenset({"dxf", "pdf", "glb"})

_FORMAT_EXT: dict[str, str] = {"dxf": "dxf", "pdf": "pdf", "glb": "glb"}
_FORMAT_MEDIA: dict[str, str] = {
    "dxf": DXF_MEDIA_TYPE,
    "pdf": PDF_MEDIA_TYPE,
    "glb": GLB_MEDIA_TYPE,
}

#: Honesty labels (D-083). The ONLY two source values a caller may declare.
_SOURCE_LABELS: dict[str, str] = {
    "proposed": "Proposed - not a city record",
    "generated_option": "Generated building option",
}

# --------------------------------------------------------------------------- #
# Caps. Every cap is taken from the accepted writer's own constant so the two can
# never drift; the ring cap is the TIGHTEST that applies to the format.
# --------------------------------------------------------------------------- #

#: Per-format RAW ring-vertex cap, checked BEFORE normalization (DB-057 (d)). PDF is the
#: tightest (1024) so it is the binding cap for a PDF export; DXF (10_000) also bounds the
#: single-prism GLB build (2*n verts, 12*n-12 indices stays far under the GLB writer's
#: 500_000-vertex / 1_500_000-index budget). NOTE (G3 A1): for the GLB FOOTPRINT the
#: EFFECTIVE cap is the concave-safe triangulator's ``MAX_OUTLINE_VERTICES`` = 1000, not
#: this raw 10_000 - a 1001..10_000-vertex footprint is refused ``over_cap_vertices`` INSIDE
#: the triangulator (``_prepare_ring``, before the ear scan); this raw 10_000 gate still
#: bounds the GLB request's (never-rendered) lot ring.
_FORMAT_RING_CAP: dict[str, int] = {
    "pdf": pdf_sheet_writer._MAX_RING_VERTICES,   # 1024
    "dxf": dxf_writer.MAX_RING_VERTICES,          # 10_000
    "glb": dxf_writer.MAX_RING_VERTICES,          # 10_000 raw; effective footprint cap 1000
}

#: Floor-stack ceiling (mirrors the accepted DXF/massing cap): floors <= 2000.
MAX_FLOORS = dxf_writer.MAX_FLOORS  # 2000

#: Every caller text field is length-capped before the claim-word screen and any writer
#: (mirrors the accepted PDF writer's caller-text bound; DB-059 (a) defense in depth).
MAX_TEXT_CHARS = pdf_sheet_writer._MAX_TEXT_CHARS  # 120

# --------------------------------------------------------------------------- #
# Filename-safety token (MANDATORY; plan §2, M5-T099 G5 F1).
# --------------------------------------------------------------------------- #

#: The ONLY bytes that may appear in the server-built download token.
_TOKEN_CHARS: frozenset[str] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
)
#: Hard cap on the token length after allowlisting.
MAX_TOKEN_LEN = 80
#: A server default used when the allowlisted token has no usable character
#: (DB-065 (a)); the route overrides it with the request correlation id.
_DEFAULT_TOKEN = "export"


# --------------------------------------------------------------------------- #
# Public dataclasses.
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ExportRequest:
    """One validated export request. Geometry is EPSG:2263 (US survey feet).

    ``lot_ring`` and ``building_ring`` are open rings of ``(x, y)`` pairs;
    ``floor_heights`` is one positive height per floor. ``generated_at`` and
    ``generator_version`` are provenance strings supplied by the caller (never a clock),
    so identical inputs yield byte-identical output.
    """

    format: str
    source: str
    lot_ring: Sequence[Sequence[float]]
    building_ring: Sequence[Sequence[float]] | None
    floor_heights: Sequence[float]
    address: str
    bbl: str
    generated_at: str
    generator_version: str
    base_elevation: float = 0.0


@dataclass(frozen=True)
class ExportRefusal:
    """The ONE uniform, redacted refusal shape reconciling all three writers.

    ``reject_code`` is a fixed enum-like token (a writer's own code or a service code);
    ``detail`` is built server-side and NEVER contains any caller value.
    """

    reject_code: str
    detail: str

    def to_payload(self) -> dict[str, str]:
        return {"reject_code": self.reject_code, "detail": self.detail}


@dataclass(frozen=True)
class ExportResult:
    """A successful export: the file bytes plus the safe response metadata."""

    format: str
    media_type: str
    body: bytes
    filename: str
    content_disposition: str
    source_label: str
    provenance: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Filename safety.
# --------------------------------------------------------------------------- #

def _allowlist_token(raw: str) -> str:
    """Keep ONLY :data:`_TOKEN_CHARS` from ``raw`` and length-cap the result. The single
    choke point BOTH the bbl/generated_at token and the caller-supplied fallback token pass
    through (DB-082 (c) / M5-T109 G5 A1), so the two allowlist paths can never drift."""
    return "".join(ch for ch in str(raw) if ch in _TOKEN_CHARS)[:MAX_TOKEN_LEN]


def build_filename_token(bbl: str, generated_at: str) -> str | None:
    """Return the server-built, allowlisted download token, or ``None`` when nothing
    usable survives.

    Only ``[A-Za-z0-9._-]`` from ``bbl`` and ``generated_at`` survives; every quote,
    ``;``, CR/LF and non-ASCII byte is DROPPED (never escaped-and-kept). The result is
    length-capped. A token that reduces to nothing, or to only ``.``/``-``/``_``, returns
    ``None`` so the caller substitutes a caller-free default (DB-065 (a))."""
    kept = _allowlist_token(f"{bbl}-{generated_at}")
    if not kept.strip("._-"):
        return None
    return kept


def _sanitize_fallback_token(fallback: str) -> str:
    """Pass the caller-supplied fallback token through the SAME allowlist + length cap
    before it reaches :func:`content_disposition` (DB-082 (c) / M5-T109 G5 A1, defence in
    depth). Even though the route passes a safe correlation id, this choke point re-
    allowlists so no caller value is trusted; a fallback that reduces to nothing (or only
    ``.``/``-``/``_``) uses the caller-free server default :data:`_DEFAULT_TOKEN`."""
    kept = _allowlist_token(fallback)
    if not kept.strip("._-"):
        return _DEFAULT_TOKEN
    return kept


def content_disposition(token: str, ext: str) -> str:
    """Build an ``attachment`` Content-Disposition value for ``site-plan-<token>.<ext>``.

    ``token`` is already allowlisted to ``[A-Za-z0-9._-]`` and ``ext`` is a fixed literal,
    so the ASCII ``filename`` can carry no quote/``;``/CR-LF; the RFC 6266 / RFC 5987
    ``filename*=UTF-8''`` companion is percent-encoded for maximally-safe client handling
    (RFC 6266 §4.1 / RFC 5987 §3.2 [recalled - verify])."""
    ascii_name = f"site-plan-{token}.{ext}"
    encoded = urllib.parse.quote(ascii_name, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded}"


# --------------------------------------------------------------------------- #
# Screens run BEFORE any writer.
# --------------------------------------------------------------------------- #

_TEXT_FIELDS = ("address", "bbl", "generated_at", "generator_version")


def _screen_caller_text(request: ExportRequest) -> ExportRefusal | None:
    """Type-check, length-cap, then claim-word screen every caller text field, in that
    order, BEFORE any writer. A refusal names the FIELD (and, for a claim word, the barred
    canonical word) - never the caller's own text."""
    for name in _TEXT_FIELDS:
        value = getattr(request, name)
        if not isinstance(value, str):
            return ExportRefusal("invalid_text", f"{name} must be a string")
        if len(value) > MAX_TEXT_CHARS:
            return ExportRefusal(
                "text_too_long", f"{name} exceeds the {MAX_TEXT_CHARS}-character limit"
            )
        barred = contains_claim_word(value)
        if barred is not None:
            return ExportRefusal(
                "claim_class_word",
                f"{name} contains the barred claim-class word {barred!r}",
            )
    return None


def _raw_ring_length(ring: object, label: str, cap: int) -> ExportRefusal | None:
    """Cap the RAW ring length BEFORE any per-vertex normalization (DB-057 (d)). A ring
    must be a sized, non-text sequence; anything longer than the format's tightest cap is
    refused (never truncated)."""
    if isinstance(ring, (str, bytes, bytearray)) or not isinstance(ring, Sequence):
        return ExportRefusal("invalid_geometry", f"{label} ring must be a sequence of (x, y) pairs")
    if len(ring) > cap:
        return ExportRefusal(
            "ring_cap_exceeded",
            f"{label} ring has {len(ring)} vertices, above the {cap}-vertex cap for this format",
        )
    return None


def _raw_floor_count(floor_heights: object) -> ExportRefusal | None:
    """Cap the RAW floor count (floors <= 2000) BEFORE any writer, with a cheap ``len``."""
    if isinstance(floor_heights, (str, bytes, bytearray)) or not isinstance(
        floor_heights, Sequence
    ):
        return ExportRefusal("invalid_geometry", "floor_heights must be a sequence of numbers")
    if len(floor_heights) > MAX_FLOORS:
        return ExportRefusal(
            "floor_cap_exceeded",
            f"{len(floor_heights)} floors exceed the {MAX_FLOORS}-floor cap",
        )
    return None


# --------------------------------------------------------------------------- #
# Refusal reconciliation - one redacted shape for all three writers.
# --------------------------------------------------------------------------- #

def _reconcile(code: str, fmt: str) -> ExportRefusal:
    """Build the ONE redacted refusal from a writer's fixed ``code``. The writers'
    own messages interpolate the caller name/coordinate; this discards them and states a
    server-built detail that carries only the (fixed) code and the format (DB-059 (h))."""
    return ExportRefusal(
        code, f"the {fmt} export was refused by its writer (reject_code={code})"
    )


def _reconcile_triangulation(reason: str) -> ExportRefusal:
    """Reconcile the concave-safe triangulator's typed
    :class:`~app.scenario.massing_guards.MassingModelError` into the ONE redacted refusal
    shape (DB-082 (a)). The triangulator's own message can echo a caller coordinate or
    vertex; this keeps ONLY its fixed ``reason`` code and a server-built detail, echoing no
    caller value (DB-059 (h))."""
    return ExportRefusal(
        reason, f"the glb footprint could not be triangulated (reject_code={reason})"
    )


# --------------------------------------------------------------------------- #
# GLB massing geometry - a SINGLE extruded prism (DB-054 (m) dedupe by construction).
# --------------------------------------------------------------------------- #

def _coerce_footprint(
    ring: Sequence[Sequence[float]],
) -> tuple[list[tuple[float, float]], ExportRefusal | None]:
    """Coerce a footprint ring to finite ``(x, y)`` float pairs (dropping a repeated
    closing vertex) so the GLB prism can be localized; a shape/number problem is a typed
    refusal. The GLB writer re-validates finiteness, bounds and degeneracy."""
    not_pair = ExportRefusal("invalid_geometry", "building ring vertex is not a pair")
    pts: list[tuple[float, float]] = []
    for vertex in ring:
        if isinstance(vertex, (str, bytes, bytearray)) or not isinstance(vertex, Sequence):
            return [], not_pair
        if len(vertex) != 2:
            return [], not_pair
        try:
            x, y = float(vertex[0]), float(vertex[1])
        except (TypeError, ValueError, OverflowError):
            return [], ExportRefusal(
                "non_numeric_coordinate", "building ring has a non-numeric coordinate"
            )
        pts.append((x, y))
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return [], ExportRefusal(
            "invalid_geometry", "building ring needs at least 3 distinct vertices"
        )
    return pts, None


def _roof_height(floor_heights: Sequence[float]) -> tuple[float, ExportRefusal | None]:
    """Sum finite, positive floor heights into the roof height; refuse otherwise."""
    if len(floor_heights) == 0:
        return 0.0, ExportRefusal("no_floors", "at least one floor height is required")
    total = 0.0
    for height in floor_heights:
        try:
            value = float(height)
        except (TypeError, ValueError, OverflowError):
            return 0.0, ExportRefusal("invalid_floor_height", "a floor height is non-numeric")
        if not math.isfinite(value) or value <= 0.0:
            return 0.0, ExportRefusal(
                "invalid_floor_height", "a floor height is not finite and > 0"
            )
        total += value
    return total, None


def _reject_non_simple_ring(ring: Sequence[tuple[float, float]]) -> None:
    """Refuse a self-intersecting (non-simple) footprint as a typed ``self_intersection``
    :class:`~app.scenario.massing_guards.MassingModelError` (reconciled to the ONE redacted
    :class:`ExportRefusal` by the caller; G3 B1 / AS-2).

    The ear-clipping triangulator only refuses a DUPLICATE-vertex ring; a crossed 'bowtie'
    with DISTINCT vertices (its edges cross) ear-clips to completion and would otherwise
    yield a valid-but-self-overlapping mesh. This explicit GEOS simplicity gate closes that
    gap. It runs on the PREPARED ring ``triangulate_polygon`` returns - whose preparation
    already proved finiteness, the coordinate magnitude bound and the 1000-vertex cap - so
    shapely/GEOS never sees a non-finite or over-cap coordinate. Any GEOS/shapely error is
    mapped to the SAME typed refusal (fail closed)."""
    try:
        is_simple = LinearRing(ring).is_simple
    except (ShapelyError, ValueError) as exc:
        raise MassingModelError(
            "building_ring failed the GEOS simplicity check",
            reason="self_intersection", field="building_ring",
        ) from exc
    if not is_simple:
        raise MassingModelError(
            "building_ring is a self-intersecting (non-simple) polygon",
            reason="self_intersection", field="building_ring",
        )


def _build_prism_mesh(
    footprint: list[tuple[float, float]], roof_height: float, base_elevation: float
) -> tuple[glb_writer.GlbMesh, glb_writer.GlbLocalFrame]:
    """Build ONE closed extruded prism (bottom cap + walls + top cap) for the footprint,
    localized to its own SW-min origin so the offsets stay inside the GLB local-coordinate
    bound. Per-floor bands are collapsed into this single extrusion, so there are NO
    coincident stacked-prism interface caps to dedupe (DB-054 (m)).

    The caps are triangulated by the ONE public concave-safe triangulator
    :func:`app.scenario.massing_triangulation.triangulate_polygon` (DB-082 (a)) - NOT a
    vertex-0 fan, which is wrong for a concave (e.g. L-shaped) footprint. It returns the
    PREPARED CCW ring (closing duplicate dropped, exactly-collinear vertices collapsed,
    oriented CCW) and CCW triangle indices INTO that ring; the side walls are built from
    the SAME prepared ring so caps and walls share one boundary and one winding. The bottom
    cap faces -z (its CCW-from-above triangles are reversed) and the top cap faces +z
    (kept), the outward winding :mod:`app.cad.glb_writer` expects. A non-simple /
    over-budget / out-of-range footprint raises a typed
    :class:`~app.scenario.massing_guards.MassingModelError`, reconciled by the caller;
    :func:`_reject_non_simple_ring` runs an explicit GEOS simplicity gate on the prepared
    ring so a crossed 'bowtie' with DISTINCT vertices (which the ear-clipper misses) is that
    same ``self_intersection`` refusal, never a self-overlapping mesh (G3 B1 / AS-2).
    Finiteness and the coordinate magnitude bound are checked inside the triangulator
    (``_prepare_ring``); the lot-only NYC range check is omitted there by design (M5-T112
    G5 INFO-1) and the GLB writer re-validates finiteness, the local bound and degeneracy.
    """
    triangulation = triangulate_polygon(footprint, field="building_ring")
    ring = triangulation.ring
    _reject_non_simple_ring(ring)  # G3 B1 / AS-2: the ear-clipper misses a distinct-vertex bowtie
    cap_triangles = triangulation.triangles
    n = len(ring)
    origin_x = min(x for x, _ in ring)
    origin_y = min(y for _, y in ring)
    local = [(x - origin_x, y - origin_y) for x, y in ring]
    # bottom ring at local z = 0 (indices 0..n-1), top ring at z = roof_height (n..2n-1).
    positions: list[tuple[float, float, float]] = [(x, y, 0.0) for x, y in local]
    positions += [(x, y, roof_height) for x, y in local]
    indices: list[int] = []
    for i in range(n):  # side walls, in the prepared-ring order (shared boundary)
        j = (i + 1) % n
        b_i, b_j, t_i, t_j = i, j, n + i, n + j
        indices += [b_i, b_j, t_j, b_i, t_j, t_i]  # two wall triangles
    for a, b, c in cap_triangles:  # bottom cap faces -z: reverse the CCW-from-above winding
        indices += [a, c, b]
    for a, b, c in cap_triangles:  # top cap faces +z: keep the CCW winding, on the top ring
        indices += [n + a, n + b, n + c]
    mesh = glb_writer.GlbMesh(
        name="massing",
        positions=positions,
        indices=indices,
        base_color=(0.72, 0.76, 0.82),
    )
    frame = glb_writer.GlbLocalFrame(
        origin_easting_ft=origin_x,
        origin_northing_ft=origin_y,
        origin_elevation_ft=float(base_elevation),
    )
    return mesh, frame


# --------------------------------------------------------------------------- #
# Per-format dispatch.
# --------------------------------------------------------------------------- #

def _render_dxf(request: ExportRequest) -> bytes | ExportRefusal:
    try:
        text = dxf_writer.render_site_plan_dxf(
            request.lot_ring,
            request.building_ring,
            request.floor_heights,
            base_elevation=request.base_elevation,
        )
    except dxf_writer.DxfWriterError as exc:
        return _reconcile(getattr(exc, "code", "writer_error"), "dxf")
    return text.encode("ascii")


def _render_pdf(request: ExportRequest) -> bytes | ExportRefusal:
    spec = pdf_sheet_writer.SitePlanInput(
        lot_ring=request.lot_ring,
        building_ring=request.building_ring,
        address=request.address,
        bbl=request.bbl,
        generated_at=request.generated_at,
        generator_version=request.generator_version,
    )
    result = pdf_sheet_writer.render_site_plan_pdf(spec)
    if isinstance(result, pdf_sheet_writer.SitePlanRefusal):
        return _reconcile(result.reject_code, "pdf")
    return result


def _render_glb(request: ExportRequest) -> bytes | ExportRefusal:
    footprint, refusal = _coerce_footprint(request.building_ring)  # type: ignore[arg-type]
    if refusal is not None:
        return refusal
    roof_height, refusal = _roof_height(request.floor_heights)
    if refusal is not None:
        return refusal
    try:
        mesh, frame = _build_prism_mesh(footprint, roof_height, request.base_elevation)
    except MassingModelError as exc:
        return _reconcile_triangulation(getattr(exc, "reason", "triangulation_error"))
    try:
        return glb_writer.write_glb([mesh], frame)
    except glb_writer.GlbWriterError as exc:
        return _reconcile(getattr(exc, "code", "writer_error"), "glb")


_DISPATCH = {"dxf": _render_dxf, "pdf": _render_pdf, "glb": _render_glb}
#: Formats whose massing requires a building footprint ring.
_REQUIRES_BUILDING = frozenset({"dxf", "glb"})


# --------------------------------------------------------------------------- #
# The one public entry.
# --------------------------------------------------------------------------- #

def build_export(
    request: ExportRequest, *, fallback_token: str = _DEFAULT_TOKEN
) -> ExportResult | ExportRefusal:
    """Validate and render ``request`` into one export file, or return one reconciled,
    redacted :class:`ExportRefusal`.

    Order (fail closed, every screen BEFORE any writer): format vocab -> source vocab ->
    caller-text type/length/claim-word screen -> RAW ring-length + floor-count caps ->
    the format's accepted writer -> the server-built filename. ``fallback_token`` (the
    route passes the request correlation id) is a caller-free default for the download
    token when the allowlisted bbl/generated_at reduce to nothing."""
    if request.format not in SUPPORTED_FORMATS:
        return ExportRefusal("unsupported_format", "format must be one of dxf, pdf, glb")
    fmt = request.format
    if request.source not in _SOURCE_LABELS:
        return ExportRefusal(
            "unsupported_source", "source must be one of proposed, generated_option"
        )

    text_refusal = _screen_caller_text(request)
    if text_refusal is not None:
        return text_refusal

    ring_cap = _FORMAT_RING_CAP[fmt]
    lot_refusal = _raw_ring_length(request.lot_ring, "lot", ring_cap)
    if lot_refusal is not None:
        return lot_refusal
    if request.building_ring is None:
        if fmt in _REQUIRES_BUILDING:
            return ExportRefusal(
                "missing_building_geometry", f"a building footprint is required for a {fmt} export"
            )
    else:
        building_refusal = _raw_ring_length(request.building_ring, "building", ring_cap)
        if building_refusal is not None:
            return building_refusal
    floor_refusal = _raw_floor_count(request.floor_heights)
    if floor_refusal is not None:
        return floor_refusal

    if isinstance(request.base_elevation, bool) or not isinstance(
        request.base_elevation, (int, float)
    ):
        return ExportRefusal("invalid_geometry", "base_elevation must be a number")
    if not math.isfinite(float(request.base_elevation)):
        return ExportRefusal("invalid_geometry", "base_elevation must be a finite number")

    rendered = _DISPATCH[fmt](request)
    if isinstance(rendered, ExportRefusal):
        return rendered

    token = build_filename_token(request.bbl, request.generated_at)
    if token is None:  # re-allowlist the fallback too (DB-082 (c)); never trust a caller token
        token = _sanitize_fallback_token(fallback_token)
    ext = _FORMAT_EXT[fmt]
    filename = f"site-plan-{token}.{ext}"
    source_label = _SOURCE_LABELS[request.source]
    provenance: dict[str, object] = {
        "format": fmt,
        "source": request.source,
        "source_label": source_label,
        "generated_at": request.generated_at,
        "generator_version": request.generator_version,
        "floors": len(request.floor_heights),
        "filename_token": token,
    }
    if fmt == "glb":
        provenance["glb_massing"] = (
            "single extrusion (base..roof); per-floor interface caps not emitted (DB-054 m)"
        )
    return ExportResult(
        format=fmt,
        media_type=_FORMAT_MEDIA[fmt],
        body=rendered,
        filename=filename,
        content_disposition=content_disposition(token, ext),
        source_label=source_label,
        provenance=provenance,
    )
