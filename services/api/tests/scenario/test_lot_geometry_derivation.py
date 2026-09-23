"""Unit pack for server-side lot-geometry derivation (task M5-T076, DB-050(a)).

Fully OFFLINE and deterministic: the canonical EPSG:2263 exterior ring is produced by the REAL
:func:`app.connectors.mappluto_geometry_arcgis.analyze_lot_geometry` over an inline esri geometry
(the accepted connector-test pattern), and a fixture-backed provider returns a
:class:`LotGeometryResult`. No network in any test.

- AS-1 (derivation correctness): the canonical 2263 exterior ring becomes lot-line segments in the
  shape the route validates; the provenance quintuple is carried. The coordinates are the large
  2263 magnitudes - a display 4326 ring (tiny lon/lat) could never satisfy them (the mutation).
- AS-3 (fail-closed): every failure class returns ``segments = None`` with an honest reason - no
  feature, multiple features, invalid/review-required geometry, an over-cap ring, an unresolvable
  BBL, and a connector fault. NEVER a fabricated rectangle.
"""

from __future__ import annotations

from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP,
    OUTCOME_MULTIPLE,
    OUTCOME_NONE,
    OUTCOME_SINGLE,
    SOURCE_ID,
    MalformedResponseError,
    analyze_lot_geometry,
)
from app.scenario.lot_geometry_derivation import (
    DerivedLotGeometry,
    LotGeometryDerivationOutcome,
    derive_lot_line_segments,
)

# A clean axis-aligned rectangular tax lot in EPSG:2263 (80 x 100 = 8000 sq ft) at a real interior
# NYC SW corner. Rings are esri-CLOCKWISE for an exterior (the connector's convention); the
# canonicalizer re-orients to CCW + rotates to the SW corner deterministically.
_RECT_ESRI = {
    "rings": [
        [
            [985000, 195000],
            [985000, 195100],
            [985080, 195100],
            [985080, 195000],
            [985000, 195000],
        ]
    ]
}
_EMPTY_RINGS_ESRI: dict = {"rings": []}


def _assessment(esri: object):
    return analyze_lot_geometry(esri, crs=dict(CRS_STAMP))


def _result(
    *,
    outcome: str = OUTCOME_SINGLE,
    esri: object | None = _RECT_ESRI,
    review_required: bool = False,
    bbl: str = "1008350041",
    version: str | None = "26v1",
):
    """Build a :class:`LotGeometryResult` for one BBL from an inline esri geometry (offline)."""
    assessment = _assessment(esri) if esri is not None else None
    from app.connectors.mappluto_geometry_arcgis import LotGeometryResult

    return LotGeometryResult(
        status="ok",
        outcome=outcome,
        review_required=review_required,
        requested_bbl=bbl,
        borough=1,
        block=835,
        lot=41,
        condo={"classification": "standard_lot", "condo_no": None, "note": None},
        identifier_conflicts=[],
        attributes=({"BBL": int(bbl), "Version": version} if version else {"BBL": int(bbl)}),
        features=[],
        geometry=assessment,
        area_sq_ft=(assessment.area_sq_ft if assessment is not None else None),
        shape_area_attribute_sq_ft=None,
        exceeded_transfer_limit=False,
        correlation_id="c-fixture",
        request_url="https://example/query",
        metadata_request_url="https://example/meta",
        retrieved_at="2026-07-20T00:00:00Z",
        crs=dict(CRS_STAMP),
        source_data_last_edited_ms=None,
        source_data_last_edited="2026-06-01T00:00:00Z",
        raw_digest="sha256:raw",
        metadata_raw_digest="sha256:meta",
        normalized_digest="sha256:features",
        digest_canonicalization="spec",
        shapely_version="2.0.7",
        geos_version="3.11.4",
    )


def _provider_returning(result):
    return lambda canonical_bbl: result


def _provider_never_called():
    def _p(canonical_bbl: str):  # pragma: no cover - asserted never invoked
        raise AssertionError("provider must not be called")

    return _p


# ---------------------------------------------------------------------------
# AS-1: derivation correctness + provenance.
# ---------------------------------------------------------------------------


def test_derives_axis_aligned_rectangle_segments():
    result = _result()
    derived = derive_lot_line_segments("1008350041", provider=_provider_returning(result))

    assert derived.outcome is LotGeometryDerivationOutcome.DERIVED
    assert derived.ok is True
    assert derived.segments is not None
    assert len(derived.segments) == 4
    for index, seg in enumerate(derived.segments):
        assert seg["id"] == f"derived-lot-line-{index}"
        assert isinstance(seg["start"], list) and len(seg["start"]) == 2
        assert isinstance(seg["end"], list) and len(seg["end"]) == 2

    # The segments reproduce the canonical exterior ring, CCW from the SW corner.
    assert derived.segments[0]["start"] == [985000.0, 195000.0]
    assert derived.segments[0]["end"] == [985080.0, 195000.0]

    # MUTATION GUARD (AS-1): the coordinates are the large EPSG:2263 magnitudes taken from the
    # measurement-grade canonical ring. Swapping the source to the display-only 4326 outline
    # connector would yield tiny lon/lat values (~ -73.98 / 40.75), reddening these assertions.
    xs = {coord for seg in derived.segments for coord in (seg["start"][0], seg["end"][0])}
    ys = {coord for seg in derived.segments for coord in (seg["start"][1], seg["end"][1])}
    assert xs == {985000.0, 985080.0}
    assert ys == {195000.0, 195100.0}


def test_derived_carries_the_provenance_quintuple():
    result = _result()
    derived = derive_lot_line_segments("1008350041", provider=_provider_returning(result))

    prov = derived.provenance
    assert prov is not None
    assert prov["source_id"] == SOURCE_ID
    assert prov["bbl"] == "1008350041"
    assert prov["retrieved_at"] == "2026-07-20T00:00:00Z"
    assert prov["dataset_version"] == "26v1"
    # The geometry digest pins the exact canonical ring the segments came from.
    assert prov["geometry_digest"] == _assessment(_RECT_ESRI).normalized_digest
    assert prov["geometry_digest"].startswith("sha256:")


def test_missing_dataset_version_stays_none_never_guessed():
    result = _result(version=None)
    derived = derive_lot_line_segments("1008350041", provider=_provider_returning(result))
    assert derived.provenance is not None
    assert derived.provenance["dataset_version"] is None


# ---------------------------------------------------------------------------
# AS-3: every failure class is a fail-closed honest gap (segments None).
# ---------------------------------------------------------------------------


def test_no_feature_is_fail_closed():
    result = _result(outcome=OUTCOME_NONE, esri=None)
    derived = derive_lot_line_segments("5999999999", provider=_provider_returning(result))
    assert derived.outcome is LotGeometryDerivationOutcome.NO_FEATURE
    assert derived.ok is False
    assert derived.segments is None
    assert derived.provenance is None
    assert "no feature" in derived.detail


def test_multiple_features_is_fail_closed():
    result = _result(outcome=OUTCOME_MULTIPLE, esri=None)
    derived = derive_lot_line_segments("1000010010", provider=_provider_returning(result))
    assert derived.outcome is LotGeometryDerivationOutcome.MULTIPLE_FEATURES
    assert derived.segments is None
    assert "multiple features" in derived.detail


def test_review_required_single_is_fail_closed():
    result = _result(review_required=True)
    derived = derive_lot_line_segments("1008350041", provider=_provider_returning(result))
    assert derived.outcome is LotGeometryDerivationOutcome.INVALID_GEOMETRY
    assert derived.segments is None
    assert "review" in derived.detail.lower()


def test_unusable_geometry_is_fail_closed():
    result = _result(esri=_EMPTY_RINGS_ESRI)  # analyze -> invalid_geometry, canonical None
    assert result.geometry is not None and result.geometry.canonical_geometry is None
    derived = derive_lot_line_segments("1008350041", provider=_provider_returning(result))
    assert derived.outcome is LotGeometryDerivationOutcome.INVALID_GEOMETRY
    assert derived.segments is None
    assert "not usable" in derived.detail


def test_over_cap_ring_is_fail_closed():
    result = _result()  # a 4-segment ring
    derived = derive_lot_line_segments(
        "1008350041", provider=_provider_returning(result), max_segments=3
    )
    assert derived.outcome is LotGeometryDerivationOutcome.INVALID_GEOMETRY
    assert derived.segments is None
    assert "cap" in derived.detail


def test_unresolvable_bbl_is_fail_closed_without_calling_provider():
    derived = derive_lot_line_segments("not-a-bbl", provider=_provider_never_called())
    assert derived.outcome is LotGeometryDerivationOutcome.BBL_UNRESOLVABLE
    assert derived.segments is None
    assert derived.provenance is None


def test_connector_fault_is_fail_closed():
    def _faulting(canonical_bbl: str):
        raise MalformedResponseError("boom", correlation_id="c")

    derived = derive_lot_line_segments("1008350041", provider=_faulting)
    assert derived.outcome is LotGeometryDerivationOutcome.CONNECTOR_FAULT
    assert derived.segments is None
    assert "could not be reached" in derived.detail


def test_as_response_block_is_strict_json_shaped():
    derived = derive_lot_line_segments(
        "1008350041", provider=_provider_returning(_result())
    )
    block = derived.as_response_block()
    assert set(block) == {"outcome", "detail", "provenance"}
    assert block["outcome"] == "derived"
    assert isinstance(block["detail"], str)
    assert isinstance(block["provenance"], dict)

    failed = DerivedLotGeometry(
        outcome=LotGeometryDerivationOutcome.NO_FEATURE, detail="x"
    ).as_response_block()
    assert failed["provenance"] is None
