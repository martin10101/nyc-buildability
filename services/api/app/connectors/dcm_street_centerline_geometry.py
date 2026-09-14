"""DCM Street Center Line polyline-geometry sibling module (task M4-T020,
D-045 A2 geometry lane item B3; pinned research
``project-control/reports/M4-T016-a2-geometry-mechanics-research.md`` Parts
2.3, 3.1, and 4.3 item 1).

MEASUREMENT-GRADE GEOMETRY VIEW over the SAME wire bytes the accepted
M4-T015 transport (:mod:`app.connectors.dcm_street_centerline_arcgis`)
already fetches: ``returnGeometry`` defaults TRUE on this endpoint, so every
segment-query page body already carries ``features[].geometry.paths``; the
accepted ``parse_segment_page`` deliberately reads attributes only and stays
byte-immutable. This sibling module (the ``mappluto_lot_outline.py``-beside-
``mappluto_geometry_arcgis.py`` precedent, here on the measurement side)
parses, CRS-validates, and TYPES that polyline geometry WITHOUT modifying
the accepted module and WITHOUT ever issuing a second fetch for the same
page.

REUSE DISCIPLINE (packet contract item 1): every transport surface -
fetching, URL building, paging with its loop-safety guarantees, HTTP-status
and ArcGIS-error handling, attribute typing, and the raw-body digest - is
reused by READ-ONLY import from the accepted module. This module builds no
URL, opens no socket of its own, and re-implements no validation the
accepted module already owns. ``parse_segment_geometry_page`` consumes the
exact :class:`DcmTransport` the accepted fetch produced;
``fetch_street_segment_geometries`` drives the accepted
``fetch_street_segments`` through a pass-through recording seam so each page
body is transported ONCE and then parsed on both the attribute side
(accepted module) and the geometry side (this module).

CRS FAIL-CLOSED (packet contract item 2; research Part 2.3): the query-page
``spatialReference`` must be exactly wkid 102718 / latestWkid 2263
(EPSG:2263, NAD83 New York Long Island, US survey feet - the live-verified
value on the recorded fixtures). Anything else, or an absent/mistyped
spatial reference, raises the typed ``wrong_crs`` error naming expected vs
received. There is NO assumed-CRS path, NO reprojection path, and NO unit
conversion anywhere in this module. This is the measurement-grade sibling;
display-only EPSG:4326 remains ``mappluto_lot_outline``'s job and this
module never serves display.

GEOMETRY-VALIDITY TAXONOMY (packet contract item 3, the
``mappluto_geometry_arcgis`` precedent): a feature whose geometry is
null/missing, malformed, empty, degenerate (a path with fewer than two
points), or carries non-numeric or non-finite coordinates is a DISTINCT
typed state on a visible entry - never a silent drop and never an exception
that hides the rest of the page. Downstream buffer correctness (B4) depends
on absence being visible. There is no partial-polyline repair and no
coordinate coercion: one defective path or vertex refuses the WHOLE
feature's geometry with the specific typed reason (first defect in document
order), while the feature itself - identity and attributes - stays in the
result.

PASSTHROUGH INTEGRITY (packet contract item 4): coordinate values are
exposed exactly as parsed from the wire JSON - no rounding, simplification,
averaging, or unit conversion. Multi-path segments (real on this layer: the
accepted West 100 Street fixture carries three paths per segment) are
preserved as distinct paths in wire order.

Deterministic code only: no AI, no legal interpretation. The official DCP
disclaimer applies (informational purposes only).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite

from app.connectors.dcm_street_centerline_arcgis import (
    ATTRIBUTION,
    CRS_STAMP,
    DCP_DISCLAIMER,
    EXPECTED_LATEST_WKID,
    EXPECTED_WKID,
    LAYER_NAME,
    MAX_RESULT_RECORD_COUNT,
    SERVICE_ROOT,
    SOURCE_ID,
    DcmTransport,
    MalformedResponseError,
    SchemaDriftError,
    StreetSegment,
    WrongCRSError,
    build_metadata_url,
    default_fetch,
    fetch_street_segments,
    parse_segment_page,
    raw_body_digest,
)

__all__ = [
    "EXPECTED_PAGE_GEOMETRY_TYPE",
    "GEOMETRY_CONTRACT_VERSION",
    "GEOMETRY_DEGENERATE_PATH",
    "GEOMETRY_EMPTY_PATHS",
    "GEOMETRY_MALFORMED_COORDINATE",
    "GEOMETRY_MALFORMED_OBJECT",
    "GEOMETRY_NONFINITE_COORDINATE",
    "GEOMETRY_NULL",
    "GEOMETRY_OK",
    "GEOMETRY_STATUSES",
    "GEOMETRY_UNEXPECTED_KIND",
    "SegmentGeometryPage",
    "SegmentGeometryQueryResult",
    "SegmentPolyline",
    "fetch_street_segment_geometries",
    "parse_segment_geometry_page",
]

GEOMETRY_CONTRACT_VERSION = "1.0.0"

# The layer's documented geometry type; a query page declaring anything else
# (or declaring nothing - e.g. an attribute-only page this module must never
# be fed) is typed schema drift, never guessed around.
EXPECTED_PAGE_GEOMETRY_TYPE = "esriGeometryPolyline"

# Per-feature geometry-validity taxonomy (packet contract item 3; the
# mappluto_geometry_arcgis findings-code precedent). Each condition the
# packet names is a DISTINCT status; ``findings`` carries the path/vertex
# coordinates of the first defect in document order.
GEOMETRY_OK = "ok"
GEOMETRY_NULL = "null_geometry"
GEOMETRY_MALFORMED_OBJECT = "malformed_geometry_object"
GEOMETRY_UNEXPECTED_KIND = "unexpected_geometry_kind"
GEOMETRY_EMPTY_PATHS = "empty_paths"
GEOMETRY_DEGENERATE_PATH = "degenerate_path"
GEOMETRY_MALFORMED_COORDINATE = "malformed_coordinate"
GEOMETRY_NONFINITE_COORDINATE = "nonfinite_coordinate"

GEOMETRY_STATUSES = (
    GEOMETRY_OK,
    GEOMETRY_NULL,
    GEOMETRY_MALFORMED_OBJECT,
    GEOMETRY_UNEXPECTED_KIND,
    GEOMETRY_EMPTY_PATHS,
    GEOMETRY_DEGENERATE_PATH,
    GEOMETRY_MALFORMED_COORDINATE,
    GEOMETRY_NONFINITE_COORDINATE,
)

TypedPaths = tuple[tuple[tuple[float, float], ...], ...]


# ---------------------------------------------------------------------------
# CRS gate (fail closed, BEFORE any coordinate is interpreted)
# ---------------------------------------------------------------------------


def _describe_spatial_reference(spatial_reference: object) -> str:
    if spatial_reference is None:
        return "absent"
    return repr(spatial_reference)[:200]


def _require_page_crs(
    spatial_reference: object, *, url: str, correlation_id: str
) -> None:
    """The page-level CRS gate: geometry is interpreted ONLY under the
    authoritative EPSG:2263 spatial reference (wkid 102718 / latestWkid
    2263, US survey feet - research Part 2.3). Anything else or absent is
    the typed ``wrong_crs`` refusal naming expected vs received; there is
    no assumed-CRS path and no reprojection path."""
    if (
        isinstance(spatial_reference, dict)
        and spatial_reference.get("wkid") == EXPECTED_WKID
        and spatial_reference.get("latestWkid") == EXPECTED_LATEST_WKID
    ):
        return
    raise WrongCRSError(
        "segment-query page spatialReference is not the authoritative "
        f"EPSG:2263 (expected wkid {EXPECTED_WKID} / latestWkid "
        f"{EXPECTED_LATEST_WKID}; received "
        f"{_describe_spatial_reference(spatial_reference)}); geometry in an "
        "unknown or unexpected CRS is never interpreted, assumed, or "
        "reprojected",
        correlation_id=correlation_id,
        detail={
            "url": url,
            "expected": {"wkid": EXPECTED_WKID, "latestWkid": EXPECTED_LATEST_WKID},
            "received": _describe_spatial_reference(spatial_reference),
        },
    )


# ---------------------------------------------------------------------------
# Per-feature geometry extraction (typed taxonomy, no repair, no coercion)
# ---------------------------------------------------------------------------


def _extract_paths(
    geometry_present: bool, geometry: object
) -> tuple[str, list[str], TypedPaths | None]:
    """Extract and type one feature's ``geometry.paths``. Returns
    ``(status, findings, paths)``: ``paths`` is populated ONLY on
    ``GEOMETRY_OK``; every refusal is the whole geometry (no partial
    salvage) with the first defect in document order typed in ``findings``.
    Values pass through untouched - the only transformation is the numeric
    JSON value becoming a Python float, which preserves the parsed value
    bit-for-bit."""
    if not geometry_present:
        return GEOMETRY_NULL, ["geometry_key_missing"], None
    if geometry is None:
        return GEOMETRY_NULL, ["geometry_json_null"], None
    if not isinstance(geometry, dict):
        return (
            GEOMETRY_MALFORMED_OBJECT,
            [f"geometry_not_an_object:{type(geometry).__name__}"],
            None,
        )
    if "paths" not in geometry:
        other_kind_keys = [
            key for key in ("rings", "points", "x", "y") if key in geometry
        ]
        if other_kind_keys:
            # A polygon/multipoint/point payload where the layer contracts
            # polylines: typed visibly, never coerced (the
            # mappluto_geometry_arcgis geometry-collection precedent).
            return (
                GEOMETRY_UNEXPECTED_KIND,
                ["non_polyline_geometry_keys:" + ",".join(other_kind_keys)],
                None,
            )
        return GEOMETRY_MALFORMED_OBJECT, ["paths_key_missing"], None
    raw_paths = geometry["paths"]
    if not isinstance(raw_paths, list):
        return (
            GEOMETRY_MALFORMED_OBJECT,
            [f"paths_not_a_list:{type(raw_paths).__name__}"],
            None,
        )
    if not raw_paths:
        return GEOMETRY_EMPTY_PATHS, ["paths_empty"], None

    findings: list[str] = []
    typed_paths: list[tuple[tuple[float, float], ...]] = []
    for path_index, raw_path in enumerate(raw_paths):
        if not isinstance(raw_path, list):
            return (
                GEOMETRY_MALFORMED_OBJECT,
                [f"path_{path_index}_not_a_list:{type(raw_path).__name__}"],
                None,
            )
        if len(raw_path) < 2:
            return (
                GEOMETRY_DEGENERATE_PATH,
                [
                    f"path_{path_index}_has_{len(raw_path)}_point(s);"
                    "_a_polyline_path_needs_at_least_2"
                ],
                None,
            )
        typed_vertices: list[tuple[float, float]] = []
        for vertex_index, vertex in enumerate(raw_path):
            if not isinstance(vertex, list | tuple) or len(vertex) < 2:
                return (
                    GEOMETRY_MALFORMED_COORDINATE,
                    [f"path_{path_index}_vertex_{vertex_index}_is_not_an_xy_pair"],
                    None,
                )
            for axis, component in (("x", vertex[0]), ("y", vertex[1])):
                if isinstance(component, bool) or not isinstance(
                    component, int | float
                ):
                    return (
                        GEOMETRY_MALFORMED_COORDINATE,
                        [
                            f"path_{path_index}_vertex_{vertex_index}_{axis}"
                            f"_non_numeric:{type(component).__name__}"
                        ],
                        None,
                    )
            x, y = float(vertex[0]), float(vertex[1])
            if not (isfinite(x) and isfinite(y)):
                return (
                    GEOMETRY_NONFINITE_COORDINATE,
                    [
                        f"path_{path_index}_vertex_{vertex_index}"
                        f"_nonfinite:({vertex[0]!r},{vertex[1]!r})"
                    ],
                    None,
                )
            if len(vertex) > 2:
                # Extra components (z/m) are outside the typed (x, y)
                # contract: recorded VISIBLY, never silently discarded
                # without a trace, never coerced into the pair.
                findings.append(
                    f"path_{path_index}_vertex_{vertex_index}"
                    f"_extra_components:{len(vertex) - 2}"
                )
            typed_vertices.append((x, y))
        typed_paths.append(tuple(typed_vertices))
    return GEOMETRY_OK, findings, tuple(typed_paths)


# ---------------------------------------------------------------------------
# Typed results
# ---------------------------------------------------------------------------


@dataclass
class SegmentPolyline:
    """One feature from a segment-query page: the accepted transport's
    typed :class:`StreetSegment` (identity + attributes, parsed from the
    SAME page body) paired with this module's typed geometry view.
    ``paths`` is populated only when ``status`` is ``GEOMETRY_OK``; a
    feature with attributes but no usable geometry stays VISIBLE here with
    its distinct typed status - never silently dropped."""

    feature_index: int
    segment: StreetSegment
    status: str
    findings: list[str]
    paths: TypedPaths | None
    path_count: int
    vertex_count: int

    @property
    def object_id(self) -> int | None:
        return self.segment.object_id

    @property
    def has_usable_geometry(self) -> bool:
        return self.status == GEOMETRY_OK


@dataclass
class SegmentGeometryPage:
    """One parsed segment-query page on the geometry side, with per-page
    provenance (retrieval identity + raw-body digest passthrough)."""

    entries: list[SegmentPolyline]
    exceeded_transfer_limit: bool
    features_total: int
    usable_geometry_count: int
    refused_geometry_count: int
    geometry_type: str
    units: str | None
    wkid: int
    latest_wkid: int
    crs: dict
    correlation_id: str
    request_url: str
    retrieved_at: str
    raw_digest: str
    source_id: str = SOURCE_ID
    service_root: str = SERVICE_ROOT
    layer: str = LAYER_NAME
    attribution: str = ATTRIBUTION
    disclaimer: str = DCP_DISCLAIMER
    contract_version: str = GEOMETRY_CONTRACT_VERSION


@dataclass
class SegmentGeometryQueryResult:
    """Complete result of one bounded, possibly-paged geometry query:
    flattened typed entries, the per-page parses, and the provenance the
    accepted transport exposes (source freshness fields, retrieval
    identity, per-page raw-body digests, drift signals)."""

    entries: list[SegmentPolyline]
    pages: list[SegmentGeometryPage]
    exceeded_transfer_limit_on_last_page: bool
    pages_fetched: int
    page_urls: list[str]
    raw_digests: list[str]
    correlation_id: str
    retrieved_at: str
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    metadata_request_url: str
    drift_signals: list[str]
    crs: dict
    source_id: str = SOURCE_ID
    service_root: str = SERVICE_ROOT
    layer: str = LAYER_NAME
    attribution: str = ATTRIBUTION
    disclaimer: str = DCP_DISCLAIMER
    contract_version: str = GEOMETRY_CONTRACT_VERSION


# ---------------------------------------------------------------------------
# Page-level parse (the core parse-and-expose surface)
# ---------------------------------------------------------------------------


def parse_segment_geometry_page(
    transport: DcmTransport, *, correlation_id: str
) -> SegmentGeometryPage:
    """Parse ONE already-transported query page on the geometry side.

    Order of operations: (1) the accepted ``parse_segment_page`` runs first
    - reusing, not re-implementing, the HTTP-status check, the
    ArcGIS-error-object classification, the malformed-body refusals, and
    the attribute typing; (2) the CRS gate runs BEFORE any coordinate is
    interpreted; (3) the page's declared ``geometryType`` must be the
    documented polyline type (else typed schema drift); (4) each feature's
    geometry is extracted under the typed validity taxonomy and paired by
    document position with its :class:`StreetSegment` from the SAME body.
    """
    segments, exceeded = parse_segment_page(transport, correlation_id=correlation_id)
    # parse_segment_page just proved the body is a well-formed JSON object
    # with a well-formed features list; this second parse of the same bytes
    # is deterministic and involves no I/O (single-fetch guarantee).
    doc = json.loads(transport.body)
    _require_page_crs(
        doc.get("spatialReference"), url=transport.url, correlation_id=correlation_id
    )
    geometry_type = doc.get("geometryType")
    if geometry_type != EXPECTED_PAGE_GEOMETRY_TYPE:
        raise SchemaDriftError(
            "segment-query page does not declare the documented polyline "
            f"geometry type (expected {EXPECTED_PAGE_GEOMETRY_TYPE!r}, "
            f"received {repr(geometry_type)[:200]}); an attribute-only or "
            "non-polyline page is never interpreted as geometry",
            correlation_id=correlation_id,
            detail={
                "url": transport.url,
                "expected": EXPECTED_PAGE_GEOMETRY_TYPE,
                "received": repr(geometry_type)[:200],
            },
        )
    features = doc.get("features")
    if not isinstance(features, list) or len(features) != len(segments):
        # Unreachable in practice (parse_segment_page builds exactly one
        # segment per feature of this same body); kept as a typed guard so
        # a pairing break can never pass silently.
        raise MalformedResponseError(
            "geometry-side feature walk does not line up with the accepted "
            "attribute-side parse of the same page body (pairing guard)",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )

    entries: list[SegmentPolyline] = []
    for index, (feature, segment) in enumerate(zip(features, segments, strict=True)):
        status, findings, paths = _extract_paths(
            "geometry" in feature, feature.get("geometry")
        )
        entries.append(
            SegmentPolyline(
                feature_index=index,
                segment=segment,
                status=status,
                findings=findings,
                paths=paths,
                path_count=len(paths) if paths is not None else 0,
                vertex_count=(
                    sum(len(path) for path in paths) if paths is not None else 0
                ),
            )
        )
    usable = sum(1 for entry in entries if entry.status == GEOMETRY_OK)

    geometry_properties = doc.get("geometryProperties")
    raw_units = (
        geometry_properties.get("units")
        if isinstance(geometry_properties, dict)
        else None
    )
    units = raw_units if isinstance(raw_units, str) else None

    return SegmentGeometryPage(
        entries=entries,
        exceeded_transfer_limit=exceeded,
        features_total=len(entries),
        usable_geometry_count=usable,
        refused_geometry_count=len(entries) - usable,
        geometry_type=geometry_type,
        units=units,
        wkid=EXPECTED_WKID,
        latest_wkid=EXPECTED_LATEST_WKID,
        crs=dict(CRS_STAMP),
        correlation_id=correlation_id,
        request_url=transport.url,
        retrieved_at=transport.retrieved_at,
        raw_digest=raw_body_digest(transport.body),
    )


# ---------------------------------------------------------------------------
# Paged public entry point (accepted transport drives; this module parses)
# ---------------------------------------------------------------------------


def fetch_street_segment_geometries(
    *,
    borough: str | None = None,
    street_name: str | None = None,
    object_id: int | None = None,
    object_id_in: list[int] | None = None,
    page_size: int = MAX_RESULT_RECORD_COUNT,
    max_pages: int | None = None,
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
    correlation_id: str | None = None,
) -> SegmentGeometryQueryResult:
    """Fetch typed segment geometries for exactly one predicate style.

    The accepted ``fetch_street_segments`` performs ALL transport work -
    metadata gate, URL building, paging, loop safety - through a
    pass-through recording seam, so every page body is transported exactly
    ONCE and then parsed here on the geometry side. Provenance from the
    accepted result (source freshness fields, retrieval identity, per-page
    raw digests, drift signals) is carried through unchanged.
    """
    recorded: list[DcmTransport] = []

    def _recording_fetch(url: str, cid: str) -> DcmTransport:
        transport = fetch(url, cid)
        recorded.append(transport)
        return transport

    attribute_result = fetch_street_segments(
        borough=borough,
        street_name=street_name,
        object_id=object_id,
        object_id_in=object_id_in,
        page_size=page_size,
        max_pages=max_pages,
        fetch=_recording_fetch,
        correlation_id=correlation_id,
    )

    metadata_url = build_metadata_url()
    page_transports = [t for t in recorded if t.url != metadata_url]
    if [t.url for t in page_transports] != attribute_result.page_urls:
        # Unreachable in practice (the recording seam sees exactly the
        # calls the accepted loop makes); typed so a transport-pairing
        # break can never pass silently.
        raise MalformedResponseError(
            "recorded page transports do not line up with the accepted "
            "transport's page_urls (single-fetch pairing guard)",
            correlation_id=attribute_result.correlation_id,
            detail={
                "recorded_urls": [t.url for t in page_transports],
                "page_urls": attribute_result.page_urls,
            },
        )

    pages = [
        parse_segment_geometry_page(
            transport, correlation_id=attribute_result.correlation_id
        )
        for transport in page_transports
    ]
    entries = [entry for page in pages for entry in page.entries]
    if len(entries) != len(attribute_result.segments):
        raise MalformedResponseError(
            "geometry-side entry count does not match the accepted "
            "transport's segment count for the same pages (pairing guard)",
            correlation_id=attribute_result.correlation_id,
            detail={
                "geometry_entries": len(entries),
                "attribute_segments": len(attribute_result.segments),
            },
        )

    return SegmentGeometryQueryResult(
        entries=entries,
        pages=pages,
        exceeded_transfer_limit_on_last_page=(
            attribute_result.exceeded_transfer_limit_on_last_page
        ),
        pages_fetched=attribute_result.pages_fetched,
        page_urls=list(attribute_result.page_urls),
        raw_digests=list(attribute_result.raw_digests),
        correlation_id=attribute_result.correlation_id,
        retrieved_at=attribute_result.retrieved_at,
        source_data_last_edited_ms=attribute_result.source_data_last_edited_ms,
        source_data_last_edited=attribute_result.source_data_last_edited,
        metadata_request_url=attribute_result.metadata_request_url,
        drift_signals=list(attribute_result.drift_signals),
        crs=dict(CRS_STAMP),
    )
