"""Live single-lot street data from the EXISTING envelope-intersects fetch (D-090-R124).

LIVE-BINDING SEAM. This module composes the ALREADY-ACCEPTED street-centerline stack into
one call, :func:`street_data_for_lot`, that turns a single lot outline into the
:class:`~app.spatial.site_geometry.inputs.StreetData` the pure B-03 derivation
(:func:`~app.spatial.site_geometry.derive.derive_site_geometry`) consumes -- so lot type,
frontages and depth can be derived LIVE for a lot outline. It introduces NO new connector and
re-implements no URL building, transport, retry/paging loop-safety, CRS check or geometry
parsing: each of those is the accepted connector's
(:mod:`app.connectors.dcm_street_centerline_arcgis` /
:mod:`app.connectors.dcm_street_centerline_geometry`) and the accepted adapter's
(:func:`~app.spatial.site_geometry.adapters.street_data_from_pages`).

Pipeline (orchestration only):

    LotOutline (EPSG:2263)
      -> street_envelope_for_lot: lot bounds (canonical 0.01-ft precision) + buffer_ft
      -> fetch_street_segment_geometries(envelope=...): the accepted paged envelope-intersects
         fetch (metadata freshness/drift gate, loop-safety, page CRS gate, geometry taxonomy)
      -> street_data_from_pages(pages, envelope=...): the accepted adapter (its coverage check
         binds the result to the lot's neighbourhood)

The query envelope is the SAME lot-bbox-plus-padding the accepted
:mod:`app.spatial.wide_street_live_provider` derives and the recorded 215-16 Northern benchmark
pack pins. The padding defaults to ``SEARCH_RADIUS_FT`` (150 ft = the wide-street ``BUFFER_FT``
100 + that provider's ``ENVELOPE_MARGIN_FT`` 50), which is exactly the coverage
:func:`~app.spatial.site_geometry.street_data.check_street_data` demands around the lot, so the
gathered candidate set is a safe SUPERSET and the exact proximity is still decided downstream.

LANE C ATTACH POINT (PR #390 seam; NOT wired here -- do not touch Lane C files). Lane C's study
read injects a geometry provider
``app.api.v1.study_inputs.GeometryProvider = (canonical_bbl, correlation_id) -> SiteGeometry |
None``. Behind the live spatial flag (``LIVE_SPATIAL_PROVIDER_ENABLED``) a live provider will
fetch the MapPLUTO lot geometry, build a ``LotOutline`` via
:func:`~app.spatial.site_geometry.adapters.lot_outline_from_mappluto`, call
:func:`street_data_for_lot` here, and pass the result to
``derive_site_geometry(lot, streets, city_records)``. This module is that provider's street-data
seam and stays Lane-C-free; it closes the "no live binding produces the envelope-intersects DCM
geometry pages" gap documented in ``study_inputs._live_study_inputs_provider``.

Fail-closed (D-051 honest absence; uncertainty never collapsed): a non-EPSG:2263 or otherwise
unusable outline, or an invalid buffer, raises :class:`UnusableLotOutlineError` BEFORE any
network I/O, and the caller routes it to ``refused_site_geometry`` (the same gate
``derive_site_geometry`` applies). A non-2263 geometry page is refused by the accepted parser
(``WrongCRSError``). Incomplete coverage stays visible in the returned ``StreetData``.
"""

from __future__ import annotations

import math
from collections.abc import Callable

from app.connectors.dcm_street_centerline_arcgis import DcmTransport, default_fetch
from app.connectors.dcm_street_centerline_geometry import fetch_street_segment_geometries

from .adapters import street_data_from_pages
from .inputs import LotOutline, StreetData
from .outline import prepare_outline
from .parameters import SEARCH_RADIUS_FT

__all__ = [
    "UnusableLotOutlineError",
    "street_data_for_lot",
    "street_envelope_for_lot",
]

# Canonical EPSG:2263 coordinate precision: 0.01 ft (half-even), the precision the accepted
# MapPLUTO connector quantizes its canonical geometry to (MPG_CANONICALIZATION_SPEC) and the
# precision the recorded DCM query envelope was derived at. Rounding the lot bounds to it before
# padding makes the built query URL byte-identical to the recorded one.
_CANONICAL_COORD_DECIMALS = 2


class UnusableLotOutlineError(Exception):
    """The lot outline cannot be used to build a street-query envelope (not EPSG:2263,
    non-finite/degenerate/invalid shape, or an invalid buffer). Raised BEFORE any network I/O;
    the caller routes it to ``refused_site_geometry`` -- the same outline gate
    ``derive_site_geometry`` applies, so the refusal reason matches."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def street_envelope_for_lot(
    lot: LotOutline, buffer_ft: float = SEARCH_RADIUS_FT
) -> tuple[float, float, float, float]:
    """The EPSG:2263 ``(xmin, ymin, xmax, ymax)`` DCM query envelope for one lot: the lot's
    bounding box at canonical 0.01-ft precision, padded by ``buffer_ft`` on every side.

    Pure, no I/O. ``buffer_ft`` defaults to ``SEARCH_RADIUS_FT`` (150 ft) -- the padding the
    accepted ``wide_street_live_provider`` uses (``BUFFER_FT`` 100 + ``ENVELOPE_MARGIN_FT`` 50)
    and the recorded benchmark pins, and exactly the coverage ``check_street_data`` demands
    around the lot. The outline is validated through the accepted
    :func:`~app.spatial.site_geometry.outline.prepare_outline` gate (CRS, finiteness, validity);
    an unusable outline or invalid buffer fails closed with :class:`UnusableLotOutlineError`."""
    if (
        isinstance(buffer_ft, bool)
        or not isinstance(buffer_ft, int | float)
        or not math.isfinite(buffer_ft)
        or buffer_ft < 0
    ):
        raise UnusableLotOutlineError("buffer_ft must be a non-negative finite number")
    prepared, refusal = prepare_outline(lot)
    if prepared is None:
        raise UnusableLotOutlineError(refusal or "The lot outline cannot be used.")
    xs = [round(x, _CANONICAL_COORD_DECIMALS) for x, _ in prepared.vertices]
    ys = [round(y, _CANONICAL_COORD_DECIMALS) for _, y in prepared.vertices]
    pad = float(buffer_ft)
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def street_data_for_lot(
    lot: LotOutline,
    *,
    correlation_id: str,
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
    buffer_ft: float = SEARCH_RADIUS_FT,
) -> StreetData:
    """Live ``StreetData`` for one lot outline, composed entirely from accepted pieces.

    1. :func:`street_envelope_for_lot` -> the EPSG:2263 query envelope (lot bounds + buffer).
    2. The accepted ``fetch_street_segment_geometries(envelope=...)`` fetches and pages the
       envelope-intersecting polyline pages through the injected/default transport (metadata
       gate, loop-safety, page CRS gate and geometry taxonomy all reused unchanged).
    3. The accepted ``street_data_from_pages`` turns those pages into ``StreetData`` with the
       SAME envelope, so its coverage check binds the result to the lot's neighbourhood.

    No URL building, transport, retry/paging, CRS check or geometry parsing is re-implemented
    here. Raises :class:`UnusableLotOutlineError` on an unusable/non-2263 outline before any
    I/O; a non-2263 geometry page is refused by the accepted parser (``WrongCRSError``)."""
    envelope = street_envelope_for_lot(lot, buffer_ft)
    geometries = fetch_street_segment_geometries(
        envelope=envelope, fetch=fetch, correlation_id=correlation_id
    )
    return street_data_from_pages(geometries.pages, envelope=envelope)
