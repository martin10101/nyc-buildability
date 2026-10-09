"""POST /api/v1/outline-bridge - map-drawn 4326 outline -> authoritative EPSG:2263
by CORRESPONDENCE, never projection math (task M5-T065, D-082-R001).

The architect draws a building-outline guess directly on the display-only 4326 lot
map (M5-T023 ``LotOutlineMap``). Those drawn positions must become EPSG:2263 feet to
enter the accepted numeric proposal draft (the measurement authority; M5-T060), and
the recorded doctrine is absolute: the 4326 display ring is DISPLAY-ONLY and NOTHING
is measured from it, all measurement lives server-side in EPSG:2263, and no
client-side transform exists. This route bridges the two WITHOUT a coordinate-system
library and WITHOUT hand-rolled Lambert/CRS math:

  * it fetches the SAME parcel's two ACCEPTED representations, read-only - the 4326
    display ring (``app.connectors.mappluto_lot_outline``) and the authoritative
    2263 geometry (``app.connectors.mappluto_geometry_arcgis``);
  * it treats the two rings as ground-control points and fits a 2D AFFINE
    correspondence between them by least squares (a 6-parameter linear solve - pure
    arithmetic, no CRS transform, no new dependency);
  * it maps the drawn 4326 vertices through that fit into 2263 and returns them WITH
    the fit residual surfaced honestly (RMS + max feet), the alignment used, the
    control-point count, and both source rings' identities.

Residual is NECESSARY but NOT SUFFICIENT, and the disclosure is honest about that.
Over a single NYC lot the true 4326->2263 relationship is locally affine to sub-inch,
so the CORRECT correspondence fits with a tiny residual and a non-corresponding ring
pair fits poorly and is REFUSED. But a small residual alone does NOT establish the
correspondence: with only 3 control points EVERY vertex alignment fits perfectly, and
a SYMMETRIC parcel admits several alignments that each fit perfectly yet map interior
points to DIFFERENT places. So the fit is trusted only when (a) there are at least
``BRIDGE_MIN_CONTROL_POINTS`` control points, (b) exactly one index alignment - tried
over both windings and all cyclic offsets, since the two official layers need not
start at the same vertex or wind the same way - fits within the residual bound, and
(c) it beats every other alignment by at least ``BRIDGE_AMBIGUITY_SEPARATION_FT``;
otherwise the correspondence is AMBIGUOUS and is refused, never guessed. The response
discloses the chosen alignment (winding + offset), the residual, AND the margin over
the runner-up alignment. The returned 2263 values are the BRIDGE's output with its
residual disclosed; they are NEVER presented as survey-grade, and the drawn shape is
PROPOSED input, never a city record (D-076-R002).

POSTURE. UNMOUNTED by design: this router is NOT added to ``app.main`` in this slice
(``services/api/app/main.py`` is out of scope and held by a live sibling lane); tests
mount it via ``TestClient`` and production wiring rides a later seam. It is ALSO
feature-flag gated OFF by default (reuses ``INTERNAL_RULE_EVAL_ENABLED``, the sibling
internal-route flag); absent/unknown -> a generic 404 byte-indistinguishable from an
unmounted path. The two ring sources are INJECTED seams (the M5-T020 pattern) so the
whole suite runs OFFLINE against fixtures.

``OUTLINE_BRIDGE_STATUS_STATE_MATRIX`` is the single source of truth for every emitted
(HTTP status, state) pair. Refusals are typed and DISTINCT: caller-input problems are
``invalid_request`` (with a ``reason``); a drawn vertex outside a bounded neighborhood
of the lot is ``out_of_neighborhood``; a ring pair that cannot be corresponded is
``correspondence_unavailable`` (with a ``reason``); a fit whose residual exceeds the
conservative bound is ``residual_too_high``; a connector fault is ``source_unavailable``.
"""

from __future__ import annotations

import json
import logging
import math
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.api.v1.proposal_checks_api import ROUTE_MAX_TOTAL_OUTLINE_POSITIONS
from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl

__all__ = [
    "BRIDGE_AMBIGUITY_SEPARATION_FT",
    "BRIDGE_MAX_CONTROL_POINTS",
    "BRIDGE_MAX_DRAWN_VERTICES",
    "BRIDGE_MAX_RMS_RESIDUAL_FT",
    "BRIDGE_MIN_CONTROL_POINTS",
    "BRIDGE_MIN_DRAWN_VERTICES",
    "BRIDGE_NEIGHBORHOOD_MARGIN",
    "OUTLINE_BRIDGE_STATUS_STATE_MATRIX",
    "AffineFit",
    "Correspondence",
    "ParcelRing",
    "RingUnavailable",
    "fit_correspondence",
    "get_authoritative_ring_provider",
    "get_display_ring_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.outline_bridge")

router = APIRouter(prefix="/api/v1", tags=["outline_bridge"])

# --- Bounds / conservative constants ----------------------------------------------------------
#: Cap on drawn outline vertices. MIRRORS the downstream proposal-checks outline cap so a shape
#: this route bridges can never exceed what the check route will then accept (single source).
BRIDGE_MAX_DRAWN_VERTICES = ROUTE_MAX_TOTAL_OUTLINE_POSITIONS
#: An outline is at least a triangle.
BRIDGE_MIN_DRAWN_VERTICES = 3
#: Minimum ground-control points for the RESIDUAL to carry correspondence information. THREE
#: non-collinear points fit a 2D affine EXACTLY for ANY correspondence, so a 3-vertex ring pair
#: can never be disambiguated by residual (it is inherently ambiguous - a triangle is refused).
#: At >= 4 the fit is over-determined, so a wrong index alignment leaves a visible residual.
BRIDGE_MIN_CONTROL_POINTS = 4
#: Upper bound on control points; the correspondence search is O(2N) affine solves, so a very
#: complex ring is refused (too_many_control_points) rather than searched unboundedly.
BRIDGE_MAX_CONTROL_POINTS = 64
#: Conservative RMS residual ceiling (EPSG:2263 feet). A genuine same-parcel affine fits far
#: below this; anything above means the two rings do not correspond and is refused, never shipped.
BRIDGE_MAX_RMS_RESIDUAL_FT = 2.0
#: The chosen alignment must beat the next-best index alignment by at least this RMS margin (feet).
#: A near-tie means a symmetric/indistinguishable parcel whose true corner correspondence cannot
#: be recovered from geometry alone; it is refused (ambiguous_correspondence), never guessed.
BRIDGE_AMBIGUITY_SEPARATION_FT = 2.0
#: Neighborhood margin: the drawn 4326 vertices must fall inside the display ring's bounding box
#: expanded by this fraction of its diagonal. Keeps a stray click from being EXTRAPOLATED through
#: the affine (the fit is only trustworthy near the control points).
BRIDGE_NEIGHBORHOOD_MARGIN = 0.5

# --- (status, state) matrix (single source of truth) ------------------------------------------
OUTLINE_BRIDGE_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # bridged 2263 vertices + correspondence provenance (NO state)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "invalid_request"),  # malformed/degenerate/over-cap caller input (carries reason)
        (422, "out_of_neighborhood"),  # a drawn vertex outside the lot's bounded neighborhood
        (422, "correspondence_unavailable"),  # rings not corresponded: too_few/too_many/mismatch/
        # degenerate/ambiguous control points (carries reason)
        (422, "residual_too_high"),  # affine fit residual over the conservative bound
        (502, "source_unavailable"),  # a connector fault fetching a source ring
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


# ---------------------------------------------------------------------------
# Injected source-ring seams. Each returns a normalized float ring for the SAME
# parcel in its own CRS; production adapters call the accepted connectors read-only,
# tests inject fixtures via ``app.dependency_overrides`` so the suite runs offline.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParcelRing:
    """One parcel's exterior ring as float coordinates in ``crs``, plus the source
    identity that provenance echoes. ``points`` is an OPEN cycle (no duplicate
    closing vertex) of at least 3 positions."""

    points: tuple[tuple[float, float], ...]
    crs: str
    source_id: str
    source_detail: dict = field(default_factory=dict)


class RingUnavailable(Exception):
    """A source ring could not be obtained as a usable exterior ring (connector fault,
    a non-single-lot outcome, or an unusable geometry). Surfaced as ``source_unavailable``
    - NEVER a fabricated ring."""

    def __init__(self, message: str, *, source_id: str) -> None:
        super().__init__(message)
        self.message = message
        self.source_id = source_id


DisplayRingProvider = Callable[[str, str], "ParcelRing"]
AuthoritativeRingProvider = Callable[[str, str], "ParcelRing"]


def _is_finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _open_ring(points: list[tuple[float, float]]) -> tuple[tuple[float, float], ...]:
    """Drop a duplicate closing vertex if present (ring stored as a closed cycle), so two
    rings from different sources can be index-aligned by position, not by closure style."""
    if len(points) >= 2:
        first, last = points[0], points[-1]
        if math.isclose(first[0], last[0], abs_tol=1e-9) and math.isclose(
            first[1], last[1], abs_tol=1e-9
        ):
            points = points[:-1]
    return tuple(points)


def _exterior_ring_from_geojson(geometry: object) -> list[tuple[float, float]] | None:
    """Extract the exterior ring float positions from a GeoJSON Polygon / MultiPolygon
    (first polygon). Returns None for any other shape - the caller raises RingUnavailable."""
    if not isinstance(geometry, dict):
        return None
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if not isinstance(coords, list) or not coords:
        return None
    if gtype == "Polygon":
        shell = coords[0]
    elif gtype == "MultiPolygon" and coords[0]:
        shell = coords[0][0]
    else:
        return None
    if not isinstance(shell, list) or len(shell) < 3:
        return None
    out: list[tuple[float, float]] = []
    for pos in shell:
        if not (isinstance(pos, (list, tuple)) and len(pos) >= 2):
            return None
        x, y = pos[0], pos[1]
        if not (_is_finite_number(x) and _is_finite_number(y)):
            return None
        out.append((float(x), float(y)))
    return out


def _default_display_ring(canonical_bbl: str, correlation_id: str) -> ParcelRing:
    """Production 4326 display ring: the accepted lot-outline connector, read-only. A
    non-single-lot or unusable outcome is a RingUnavailable (never a fabricated ring)."""
    from app.connectors.mappluto_lot_outline import (
        SOURCE_ID,
        LotOutlineError,
        build_lot_outline,
    )

    try:
        doc = build_lot_outline(canonical_bbl, correlation_id=correlation_id)
    except LotOutlineError as exc:  # transport / parse / contract fault
        raise RingUnavailable(str(exc), source_id=SOURCE_ID) from exc
    if doc.get("outcome") != "single_lot":
        raise RingUnavailable(
            f"the lot-outline source returned outcome={doc.get('outcome')!r}, not a drawable lot",
            source_id=SOURCE_ID,
        )
    ring = _exterior_ring_from_geojson(doc.get("geometry"))
    if ring is None:
        raise RingUnavailable(
            "the 4326 display geometry had no usable exterior ring", source_id=SOURCE_ID
        )
    version = (doc.get("source") or {}).get("dataset_version")
    # NOTE (source identity): the lot-outline connector RE-EXPORTS the geometry connector's
    # SOURCE_ID (both are the same official MapPLUTO source), so this ``source_id`` equals the
    # authoritative ring's. ``representation`` + ``crs`` keep the two rings distinguishable in
    # provenance; the shared source_id is the honest official identity, never invented here.
    return ParcelRing(
        points=_open_ring(ring),
        crs="EPSG:4326",
        source_id=SOURCE_ID,
        source_detail={
            "outcome": "single_lot",
            "representation": "lot_outline_display",
            "dataset_version": version,
        },
    )


def _default_authoritative_ring(canonical_bbl: str, correlation_id: str) -> ParcelRing:
    """Production 2263 authoritative ring: the accepted MapPLUTO geometry connector, read-only.
    Uses the connector's own canonical geometry (list of polygons; each ring a list of
    [x, y] coordinate strings) - no shapely import, no re-parsing of raw ArcGIS rings."""
    from app.connectors.mappluto_geometry_arcgis import (
        SOURCE_ID,
        MapPlutoGeometryConnectorError,
        fetch_lot_geometry,
    )

    try:
        result = fetch_lot_geometry(canonical_bbl, correlation_id=correlation_id)
    except MapPlutoGeometryConnectorError as exc:
        raise RingUnavailable(str(exc), source_id=SOURCE_ID) from exc
    assessment = result.geometry
    if (
        result.outcome != "single_feature"
        or assessment is None
        or not assessment.canonical_geometry
    ):
        raise RingUnavailable(
            f"the authoritative geometry source returned outcome={result.outcome!r}",
            source_id=SOURCE_ID,
        )
    try:
        shell = assessment.canonical_geometry[0][0]  # first polygon, exterior ring
        ring = [(float(x), float(y)) for x, y in shell]
    except (IndexError, TypeError, ValueError) as exc:
        raise RingUnavailable(
            "the authoritative canonical geometry had no usable exterior ring",
            source_id=SOURCE_ID,
        ) from exc
    if len(ring) < 3:
        raise RingUnavailable(
            "the authoritative exterior ring had fewer than 3 vertices", source_id=SOURCE_ID
        )
    return ParcelRing(
        points=_open_ring(ring),
        crs="EPSG:2263",
        source_id=SOURCE_ID,
        source_detail={
            "outcome": "single_feature",
            "representation": "lot_geometry_authoritative",
            "normalized_digest": assessment.normalized_digest,
        },
    )


def get_display_ring_provider() -> DisplayRingProvider:
    """Dependency returning the 4326 display-ring seam (override point for tests)."""
    return _default_display_ring


def get_authoritative_ring_provider() -> AuthoritativeRingProvider:
    """Dependency returning the 2263 authoritative-ring seam (override point for tests)."""
    return _default_authoritative_ring


# ---------------------------------------------------------------------------
# Affine correspondence - pure arithmetic (NO CRS math, NO new dependency).
#
# MODULE BOUNDARY. This file keeps three responsibilities in three non-overlapping
# sections and never entangles them:
#   1. connector I/O adapters (above): fetch the two accepted parcel rings read-only
#      and normalize them to ``ParcelRing`` - the ONLY code here that does I/O.
#   2. correspondence computation (this section): pure, side-effect-free arithmetic
#      over two float rings - no I/O, no FastAPI, no logging, no globals - so it is
#      unit-testable in isolation (``fit_correspondence`` is exported for that).
#   3. HTTP handling (below): body parsing, the (status, state) matrix, and response
#      assembly - it owns NO geometry math and NO connector calls.
# The affine math never imports a CRS library and never hand-rolls Lambert/CRS math
# (D-082-R001): it recovers whatever LOCAL affine relates the two accepted rings.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AffineFit:
    """A fitted 2D affine (X = a*u + b*v + c ; Y = d*u + e*v + f) with its RMS and max
    residual in the destination CRS (feet), and the index alignment that produced it:
    ``winding`` ("forward"/"reversed") and the cyclic ``offset`` applied to the
    destination ring."""

    coeffs: tuple[float, float, float, float, float, float]
    rms_residual: float
    max_residual: float
    winding: str
    offset: int
    control_point_count: int

    @property
    def alignment(self) -> str:
        return f"{self.winding}+offset{self.offset}"


@dataclass(frozen=True)
class Correspondence:
    """The chosen affine plus the EVIDENCE that it is uniquely the best index
    alignment: the runner-up alignment's RMS residual (``math.inf`` when only one
    candidate solved) and how many candidate alignments were evaluated. A small
    ``separation`` means the correspondence is AMBIGUOUS (a symmetric parcel) and the
    HTTP layer refuses it - a low residual alone never establishes correspondence."""

    fit: AffineFit
    runner_up_rms_residual: float
    candidates_evaluated: int

    @property
    def separation(self) -> float:
        return self.runner_up_rms_residual - self.fit.rms_residual


class _CorrespondenceError(Exception):
    """The two rings could not be corresponded. ``reason`` is a machine code."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.message = message
        self.reason = reason


def _solve_affine(
    src: tuple[tuple[float, float], ...],
    dst: tuple[tuple[float, float], ...],
) -> tuple[tuple[float, float, float, float, float, float], float, float] | None:
    """Least-squares 2D affine from index-aligned ``src`` -> ``dst``, returning
    ``(coeffs, rms_residual, max_residual)`` or ``None`` if the control points are
    (near-)collinear (the centered scatter matrix is singular).

    The coordinates are CENTERED on their centroids before the 2x2 scatter system is
    solved, then the translation is recovered from the centroids. Centering is
    essential, not cosmetic: 4326 values (~-74 / ~40 with a per-lot spread of ~1e-3)
    fed raw into un-centered normal equations against 2263 feet (~1e6) are
    catastrophically ill-conditioned; centering makes the same pure-arithmetic fit
    stable."""
    n = len(src)
    mu_u = sum(p[0] for p in src) / n
    mu_v = sum(p[1] for p in src) / n
    mu_x = sum(p[0] for p in dst) / n
    mu_y = sum(p[1] for p in dst) / n
    suu = svv = suv = 0.0
    sux = svx = suy = svy = 0.0
    for (u, v), (x, y) in zip(src, dst, strict=True):
        du, dv = u - mu_u, v - mu_v
        dx, dy = x - mu_x, y - mu_y
        suu += du * du
        svv += dv * dv
        suv += du * dv
        sux += du * dx
        svx += dv * dx
        suy += du * dy
        svy += dv * dy
    det = suu * svv - suv * suv
    if det <= 1e-12 * (suu * svv + 1e-30):  # collinear / degenerate control points
        return None
    a = (svv * sux - suv * svx) / det
    b = (suu * svx - suv * sux) / det
    d = (svv * suy - suv * svy) / det
    e = (suu * svy - suv * suy) / det
    c = mu_x - a * mu_u - b * mu_v
    f = mu_y - d * mu_u - e * mu_v
    sq_sum = 0.0
    max_r = 0.0
    for (u, v), (x, y) in zip(src, dst, strict=True):
        px = a * u + b * v + c
        py = d * u + e * v + f
        r = math.hypot(px - x, py - y)
        sq_sum += r * r
        max_r = max(max_r, r)
    return (a, b, c, d, e, f), math.sqrt(sq_sum / n), max_r


def fit_correspondence(display: ParcelRing, authoritative: ParcelRing) -> Correspondence:
    """Find the affine carrying the 4326 display ring onto the 2263 authoritative ring
    by trying EVERY index alignment a genuine same-parcel pair could take - both
    windings and all cyclic offsets, because the two official layers need not start at
    the same vertex or wind the same way - and returning the lowest-residual one
    together with the runner-up's residual as ambiguity evidence.

    Residual alone does NOT establish correspondence: with exactly 3 control points
    every alignment fits perfectly, and a SYMMETRIC parcel admits several equally good
    alignments that map interior points to DIFFERENT places. So this requires
    ``BRIDGE_MIN_CONTROL_POINTS`` control points for the residual to carry any signal,
    caps the search at ``BRIDGE_MAX_CONTROL_POINTS``, and hands the caller the runner-up
    residual so it can refuse an AMBIGUOUS (near-tie) best. Raises
    :class:`_CorrespondenceError` (typed reason) when no countable correspondence
    exists."""
    src = display.points
    dst = authoritative.points
    if len(src) < BRIDGE_MIN_CONTROL_POINTS or len(dst) < BRIDGE_MIN_CONTROL_POINTS:
        raise _CorrespondenceError(
            "a source ring has fewer than the minimum control points; with so few "
            "vertices the fit residual cannot establish which correspondence is correct",
            reason="too_few_control_points",
        )
    if len(src) > BRIDGE_MAX_CONTROL_POINTS or len(dst) > BRIDGE_MAX_CONTROL_POINTS:
        raise _CorrespondenceError(
            f"a source ring has more than the {BRIDGE_MAX_CONTROL_POINTS} control points "
            "this bounded correspondence search supports",
            reason="too_many_control_points",
        )
    if len(src) != len(dst):
        raise _CorrespondenceError(
            f"the display ring ({len(src)} vertices) and authoritative ring "
            f"({len(dst)} vertices) cannot be index-corresponded",
            reason="vertex_count_mismatch",
        )
    n = len(src)
    candidates: list[AffineFit] = []
    for winding, base in (("forward", dst), ("reversed", tuple(reversed(dst)))):
        for offset in range(n):
            aligned = base[offset:] + base[:offset]
            solved = _solve_affine(src, aligned)
            if solved is None:
                continue
            coeffs, rms, max_r = solved
            candidates.append(AffineFit(coeffs, rms, max_r, winding, offset, n))
    if not candidates:
        raise _CorrespondenceError(
            "the control points are collinear/degenerate; a 2D affine cannot be fitted",
            reason="degenerate_control_points",
        )
    candidates.sort(key=lambda fit: fit.rms_residual)
    best = candidates[0]
    runner_up = candidates[1].rms_residual if len(candidates) > 1 else math.inf
    return Correspondence(best, runner_up, len(candidates))


# ---------------------------------------------------------------------------
# Neighborhood + input helpers.
# ---------------------------------------------------------------------------
def _ring_bbox(points: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _outside_neighborhood(drawn: list[tuple[float, float]], display: ParcelRing) -> int | None:
    """Return the index of the first drawn vertex that falls outside the display ring's
    bbox expanded by ``BRIDGE_NEIGHBORHOOD_MARGIN`` of its diagonal, else None."""
    min_x, min_y, max_x, max_y = _ring_bbox(display.points)
    diag = math.hypot(max_x - min_x, max_y - min_y)
    margin = diag * BRIDGE_NEIGHBORHOOD_MARGIN
    lo_x, lo_y, hi_x, hi_y = min_x - margin, min_y - margin, max_x + margin, max_y + margin
    for i, (x, y) in enumerate(drawn):
        if x < lo_x or x > hi_x or y < lo_y or y > hi_y:
            return i
    return None


class _RequestRefusal(Exception):
    """A caller-input refusal -> (422, invalid_request) with a machine ``reason``."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.message = message
        self.reason = reason


def _parse_drawn_vertices(raw: object) -> list[tuple[float, float]]:
    """Validate the caller's ``drawn_vertices`` into a list of finite (lng, lat) tuples.
    Raises :class:`_RequestRefusal` (typed reason) on any shape/finiteness/cap violation."""
    if not isinstance(raw, list):
        raise _RequestRefusal(
            "drawn_vertices must be an array of [lng, lat] positions",
            reason="drawn_vertices_type",
        )
    if len(raw) < BRIDGE_MIN_DRAWN_VERTICES:
        raise _RequestRefusal(
            f"a drawn outline needs at least {BRIDGE_MIN_DRAWN_VERTICES} vertices; got {len(raw)}",
            reason="too_few_vertices",
        )
    if len(raw) > BRIDGE_MAX_DRAWN_VERTICES:
        raise _RequestRefusal(
            f"drawn_vertices has {len(raw)} positions, above the cap "
            f"BRIDGE_MAX_DRAWN_VERTICES ({BRIDGE_MAX_DRAWN_VERTICES})",
            reason="over_cap",
        )
    out: list[tuple[float, float]] = []
    for i, pos in enumerate(raw):
        ok = (
            isinstance(pos, list)
            and len(pos) == 2
            and _is_finite_number(pos[0])
            and _is_finite_number(pos[1])
        )
        if not ok:
            raise _RequestRefusal(
                f"drawn_vertices[{i}] must be a finite [lng, lat] pair",
                reason="vertex_non_finite",
            )
        out.append((float(pos[0]), float(pos[1])))
    return out


# ---------------------------------------------------------------------------
# Response helpers (mirror the sibling internal routes).
# ---------------------------------------------------------------------------
def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to an unmounted path (fail-safe disable): no correlation id,
    no body hint the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _payload_too_large(correlation_id: str) -> JSONResponse:
    return _json(
        413,
        {
            "state": "payload_too_large",
            "message": f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _refusal(
    state: str, message: str, correlation_id: str, *, reason: str | None = None
) -> JSONResponse:
    body: dict[str, Any] = {
        "state": state,
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if reason is not None:
        body["reason"] = reason
    return _json(422, body, correlation_id)


def _source_unavailable(message: str, source_id: str, correlation_id: str) -> JSONResponse:
    return _json(
        502,
        {
            "state": "source_unavailable",
            "message": _bounded_message(message),
            "source_id": source_id,
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send (the M5-T012
    render-parity guard): reject NaN/Infinity and unpaired surrogates, failing closed to
    a typed 500 rather than an untyped ASGI 500."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


@router.post("/outline-bridge", include_in_schema=False)
async def post_outline_bridge(
    request: Request,
    display_ring: DisplayRingProvider = Depends(get_display_ring_provider),  # noqa: B008
    authoritative_ring: AuthoritativeRingProvider = Depends(  # noqa: B008
        get_authoritative_ring_provider
    ),
) -> JSONResponse:
    """Bridge a map-drawn 4326 outline onto authoritative 2263 by correspondence. Feature-flag
    gated OFF by default (reuses INTERNAL_RULE_EVAL_ENABLED) and UNMOUNTED in this slice."""
    # Fail-safe disable FIRST, before a correlation id is minted or the body is read.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Raw body ceiling BEFORE parse (declared fast-path + streamed accumulator).
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        return _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        return _payload_too_large(correlation_id)

    if not raw or not raw.strip():
        return _refusal(
            "invalid_request", "request body must be a JSON object", correlation_id,
            reason="not_object",
        )
    try:
        body = json.loads(raw)
    except Exception:
        return _refusal(
            "invalid_request", "request body is not valid JSON", correlation_id, reason="not_json"
        )
    if not isinstance(body, dict):
        return _refusal(
            "invalid_request", "request body must be a JSON object", correlation_id,
            reason="not_object",
        )
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _refusal(
            "invalid_request",
            "request body is not strict-JSON serializable (NaN/Infinity or non-encodable text)",
            correlation_id,
            reason="non_finite",
        )

    # SRID: the drawn positions are display 4326; anything else is a caller error (no transform).
    srid = body.get("srid", 4326)
    if srid not in (4326, "4326"):
        return _refusal(
            "invalid_request",
            "srid must be 4326 (the display CRS); this route does not transform other CRS",
            correlation_id,
            reason="srid_unsupported",
        )

    # BBL: validated BEFORE any connector call (typed refusal, zero I/O).
    try:
        normalized = normalize_bbl(body.get("bbl"))
    except BBLValidationError as exc:
        payload = exc.to_payload()
        return _refusal("invalid_request", payload["message"], correlation_id, reason="bbl_invalid")

    # Drawn vertices: shape/finiteness/cap.
    try:
        drawn = _parse_drawn_vertices(body.get("drawn_vertices"))
    except _RequestRefusal as exc:
        return _refusal("invalid_request", exc.message, correlation_id, reason=exc.reason)

    # Fetch the two source rings read-only through the injected seams. A connector fault or a
    # non-single-lot outcome is a typed source_unavailable, never a fabricated ring.
    try:
        display = display_ring(normalized.canonical, correlation_id)
        authoritative = authoritative_ring(normalized.canonical, correlation_id)
    except RingUnavailable as exc:
        logger.warning(
            "outline_bridge source_unavailable source_id=%s correlation_id=%s",
            exc.source_id, correlation_id,
        )
        return _source_unavailable(exc.message, exc.source_id, correlation_id)
    except Exception:
        logger.error(
            "outline_bridge unexpected_error stage=fetch correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    if display.crs != "EPSG:4326" or authoritative.crs != "EPSG:2263":
        logger.error("outline_bridge ring_crs_mismatch correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)

    # Neighborhood gate: refuse a drawn vertex that would be EXTRAPOLATED far outside the lot.
    outside = _outside_neighborhood(drawn, display)
    if outside is not None:
        return _refusal(
            "out_of_neighborhood",
            f"drawn vertex {outside} falls outside the bounded neighborhood of the lot; "
            "draw the outline over the shown parcel",
            correlation_id,
        )

    # Fit the correspondence, then gate on BOTH the disclosed residual AND the margin
    # over the next-best alignment (a low residual alone never establishes correspondence).
    try:
        correspondence = fit_correspondence(display, authoritative)
    except _CorrespondenceError as exc:
        return _refusal(
            "correspondence_unavailable", exc.message, correlation_id, reason=exc.reason
        )
    fit = correspondence.fit

    if fit.rms_residual > BRIDGE_MAX_RMS_RESIDUAL_FT:
        return _json(
            422,
            {
                "state": "residual_too_high",
                "message": _bounded_message(
                    f"the parcel correspondence fit residual ({fit.rms_residual:.4f} ft RMS) "
                    f"exceeds the conservative bound ({BRIDGE_MAX_RMS_RESIDUAL_FT} ft); "
                    "the drawn outline was not bridged"
                ),
                "rms_residual_ft": fit.rms_residual,
                "residual_bound_ft": BRIDGE_MAX_RMS_RESIDUAL_FT,
                "correlation_id": correlation_id,
            },
            correlation_id,
        )

    # Uniqueness gate. A genuine correspondence must be the SINGLE best alignment by a
    # clear margin; a near-tie means a symmetric/indistinguishable parcel whose true
    # corner-to-corner correspondence cannot be recovered from geometry alone. Emitting a
    # guessed alignment would ship silently-wrong (e.g. 90-degree-rotated) coordinates.
    separation = correspondence.separation
    if not math.isinf(separation) and separation < BRIDGE_AMBIGUITY_SEPARATION_FT:
        return _refusal(
            "correspondence_unavailable",
            f"the parcel's two rings admit more than one equally good vertex correspondence "
            f"(best {fit.rms_residual:.4f} ft RMS vs runner-up "
            f"{correspondence.runner_up_rms_residual:.4f} ft, a {separation:.4f} ft gap below "
            f"the {BRIDGE_AMBIGUITY_SEPARATION_FT} ft minimum); the outline was not bridged "
            "because the correct correspondence is ambiguous",
            correlation_id,
            reason="ambiguous_correspondence",
        )

    # Map the drawn 4326 vertices through the fitted affine into 2263.
    a, b, c, d, e, f = fit.coeffs
    vertices = [{"x": a * u + b * v + c, "y": d * u + e * v + f} for (u, v) in drawn]

    runner_up_ft = (
        None
        if math.isinf(correspondence.runner_up_rms_residual)
        else correspondence.runner_up_rms_residual
    )
    separation_ft = None if math.isinf(separation) else separation
    display_identity = {"crs": display.crs, "source_id": display.source_id, **display.source_detail}
    auth_identity = {
        "crs": authoritative.crs,
        "source_id": authoritative.source_id,
        **authoritative.source_detail,
    }
    document = {
        "document_kind": "outline_bridge",
        "bbl": normalized.canonical,
        "srid": 2263,
        "vertices": vertices,
        "correspondence": {
            "method": "affine_least_squares_2d",
            "alignment": fit.alignment,
            "alignment_winding": fit.winding,
            "alignment_offset": fit.offset,
            "control_point_count": fit.control_point_count,
            "candidates_evaluated": correspondence.candidates_evaluated,
            "rms_residual_ft": fit.rms_residual,
            "max_residual_ft": fit.max_residual,
            "residual_bound_ft": BRIDGE_MAX_RMS_RESIDUAL_FT,
            "runner_up_rms_residual_ft": runner_up_ft,
            "alignment_separation_ft": separation_ft,
            "alignment_separation_min_ft": BRIDGE_AMBIGUITY_SEPARATION_FT,
            "source_display_ring": display_identity,
            "source_authoritative_ring": auth_identity,
        },
        "disclosure": (
            "These EPSG:2263 vertices are bridged from your map drawing by an affine "
            "correspondence to the official parcel geometry. The fit residual AND the margin "
            "over the next-best alignment are disclosed above: a low residual alone does not "
            "establish the correspondence, so an ambiguous or indistinguishable parcel is "
            "refused rather than guessed. They are approximate PROPOSED input for editing, not "
            "a survey and not a city record."
        ),
        "correlation_id": correlation_id,
    }
    try:
        _assert_json_safe(document)
    except Exception:
        logger.error("outline_bridge serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    return _json(200, document, correlation_id)
