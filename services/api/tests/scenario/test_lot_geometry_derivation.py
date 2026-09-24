"""Unit pack for server-side lot-geometry derivation (task M5-T076, DB-050(a)).

Fully OFFLINE and deterministic. Two geometry sources, both run through the REAL
:func:`app.connectors.mappluto_geometry_arcgis.analyze_lot_geometry`, with a fixture-backed
provider returning a :class:`LotGeometryResult`; no network in any test:

* the RECORDED live-captured MapPLUTO packs in ``tests/fixtures/mappluto_geometry/`` - MPG02
  (Empire State Building, single lot), MPG06 (Governors Island, holed lot), MPG07 (Queens,
  true multipolygon) - which carry the real City geometry classes this route will meet first;
* a SYNTHETIC inline axis-aligned rectangle, used only where a clean textbook ring is what is
  under test (segment ordering, the provenance quintuple, the individual refusal classes).

- AS-1 (derivation correctness): the canonical 2263 exterior ring becomes lot-line segments in the
  shape the route validates, holes excluded (proven on the RECORDED holed lot); the provenance
  quintuple is carried. The coordinates are the large 2263 magnitudes - a display 4326 ring (tiny
  lon/lat) could never satisfy them (the mutation) - and the module's import list is asserted
  directly, so the display-only outline connector cannot creep in.
- AS-3 (fail-closed): every failure class returns ``segments = None`` with an honest reason - no
  feature, multiple features, invalid/review-required geometry, a degenerate ring, an over-cap
  ring (typed APART from invalid: the official data is fine, our cap binds), an unresolvable BBL,
  and a connector fault. NEVER a fabricated rectangle, NEVER a truncated ring.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import app.scenario.lot_geometry_derivation as derivation_mod
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

#: The accepted M2-T009 recorded fixture pack (live urllib GETs against the official keyless
#: ArcGIS service). These are the real captured City responses, not synthetic constructions.
_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "mappluto_geometry"

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


def _recorded_feature(fixture_name: str) -> dict:
    """The single feature of a RECORDED live-captured MapPLUTO fixture - the City's own geometry
    and attributes, byte-for-byte as captured. Fails loudly if the pack ever stops being a raw
    live capture, so a synthetic substitution can never masquerade as recorded evidence."""
    fixture = json.loads((_FIXTURE_DIR / fixture_name).read_text(encoding="utf-8"))
    assert fixture["classification"] == "raw"
    assert fixture["capture_method"].startswith("live ")
    features = json.loads(fixture["response_body_raw"])["features"]
    assert len(features) == 1
    return features[0]


def _recorded_result(fixture_name: str):
    """A :class:`LotGeometryResult` whose GEOMETRY, BBL and dataset version come from the recorded
    fixture (the surrounding envelope fields are the offline provider shape, as above)."""
    feature = _recorded_feature(fixture_name)
    attributes = feature["attributes"]
    return _result(
        esri=feature["geometry"],
        bbl=str(attributes["BBL"]),
        version=attributes.get("Version"),
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
    """Segment shape, id sequence and ring ordering on the SYNTHETIC textbook rectangle (a real
    recorded lot is exercised separately, below)."""
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

    # MUTATION GUARD (AS-1), INDIRECT by construction: these assert coordinate MAGNITUDES, not the
    # connector identity - swapping the source to the display-only 4326 outline connector would
    # yield tiny lon/lat values (~ -73.98 / 40.75) and redden them. The isolation itself is asserted
    # directly by test_module_never_imports_the_display_only_outline_connector below.
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


def test_module_never_imports_the_display_only_outline_connector():
    """AS-1 (DIRECT isolation proof): the derivation module's own import list is read from its
    source. ``mappluto_lot_outline`` is the DISPLAY-ONLY 4326 connector and must never appear - a
    future edit that imported it (even unused) reddens this immediately, where the coordinate
    magnitude guard above would only catch it once the values actually changed."""
    tree = ast.parse(Path(derivation_mod.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert not any("mappluto_lot_outline" in name for name in imported), sorted(imported)
    # The measurement-grade 2263 connector IS the source, and is imported.
    assert "app.connectors.mappluto_geometry_arcgis" in imported


# ---------------------------------------------------------------------------
# AS-1 over the RECORDED live-captured fixture packs (the real City geometry classes).
# ---------------------------------------------------------------------------


def test_recorded_single_lot_fixture_derives_its_real_exterior_ring():
    """MPG02 (Empire State Building, BBL 1008350041) - the recorded single-lot capture. Its real
    exterior ring is a 6-vertex NON-axis-aligned polygon, so it derives 6 segments carrying the
    City's own 2263 coordinates and the recorded ``Version``. (Whether the ENGINE can then fit a
    candidate to that ring is a separate question - it cannot; see the route pack.)"""
    derived = derive_lot_line_segments(
        "1008350041",
        provider=_provider_returning(_recorded_result("MPG02_lot_single_1008350041.json")),
    )

    assert derived.outcome is LotGeometryDerivationOutcome.DERIVED
    assert derived.segments is not None
    assert len(derived.segments) == 6

    # The segments close the recorded ring: each end meets the next start, the last wraps to the
    # first, and the coordinates are the recorded 2263 magnitudes (never display 4326 lon/lat).
    starts = [tuple(seg["start"]) for seg in derived.segments]
    ends = [tuple(seg["end"]) for seg in derived.segments]
    assert ends[:-1] == starts[1:]
    assert ends[-1] == starts[0]
    assert starts[0] == (987926.19, 211999.93)  # first canonical vertex of the recorded ring
    assert all(900_000.0 < x < 1_100_000.0 for x, _ in starts)
    assert all(150_000.0 < y < 300_000.0 for _, y in starts)

    assert derived.provenance is not None
    assert derived.provenance["dataset_version"] == "26v1"  # the RECORDED attribute, not a guess
    assert derived.provenance["bbl"] == "1008350041"


def test_recorded_holed_lot_excludes_every_hole_vertex():
    """AS-1 (holes excluded), on the RECORDED holed lot MPG06 (Governors Island): its canonical
    form is one 320-vertex exterior ring plus two hole rings totalling 143 vertices. The derivation
    cuts exactly the 320 exterior segments, and NOT ONE of the 143 hole vertices appears in any
    segment endpoint - a mutant that walked ``polygon`` instead of ``polygon[0]`` would both raise
    the count and land hole vertices in the output."""
    feature = _recorded_feature("MPG06_lot_holes_1000010010.json")
    assessment = analyze_lot_geometry(feature["geometry"], crs=dict(CRS_STAMP))
    assert assessment.status == "valid"
    polygon = assessment.canonical_geometry[0]
    exterior_vertices = {(float(x), float(y)) for x, y in polygon[0]}
    hole_vertices = {(float(x), float(y)) for ring in polygon[1:] for x, y in ring}
    assert len(exterior_vertices) == 320
    assert len(hole_vertices) == 143
    assert not (exterior_vertices & hole_vertices)  # the recorded rings are disjoint in vertices

    derived = derive_lot_line_segments(
        "1000010010",
        provider=_provider_returning(_recorded_result("MPG06_lot_holes_1000010010.json")),
    )
    assert derived.outcome is LotGeometryDerivationOutcome.DERIVED
    assert derived.segments is not None
    assert len(derived.segments) == 320

    endpoints = {
        point
        for seg in derived.segments
        for point in (tuple(seg["start"]), tuple(seg["end"]))
    }
    assert endpoints == exterior_vertices
    assert not (endpoints & hole_vertices)


def test_recorded_multipolygon_is_over_cap_never_invalid_official_data():
    """F4 / provenance honesty on the RECORDED multipolygon MPG07 (Queens, shoreline-clipped): the
    City's geometry assesses VALID (2 exterior rings, 3130 vertices), and it is OUR route cap (800)
    that blocks the derivation. The outcome is therefore ``geometry_over_cap``, NOT
    ``invalid_geometry``, and the detail says the official data is not at fault. Raising the cap
    above the real ring size derives it normally - proof that nothing is wrong with the source."""
    feature = _recorded_feature("MPG07_lot_multipolygon_4142600001.json")
    assessment = analyze_lot_geometry(feature["geometry"], crs=dict(CRS_STAMP))
    assert assessment.status == "valid"  # the official geometry is fine
    exterior_vertex_count = sum(len(polygon[0]) for polygon in assessment.canonical_geometry)
    assert len(assessment.canonical_geometry) == 2
    assert exterior_vertex_count == 3130

    result = _recorded_result("MPG07_lot_multipolygon_4142600001.json")
    over_cap = derive_lot_line_segments(
        "4142600001", provider=_provider_returning(result), max_segments=800
    )
    assert over_cap.outcome is LotGeometryDerivationOutcome.GEOMETRY_OVER_CAP
    assert over_cap.outcome is not LotGeometryDerivationOutcome.INVALID_GEOMETRY
    assert over_cap.segments is None  # never a truncated ring
    assert over_cap.provenance is None
    assert "valid" in over_cap.detail
    assert "our own cap is the binding constraint" in over_cap.detail
    assert "800" in over_cap.detail

    # Same recorded geometry, a cap above its real size: it derives every exterior segment.
    within_cap = derive_lot_line_segments(
        "4142600001", provider=_provider_returning(result), max_segments=4000
    )
    assert within_cap.outcome is LotGeometryDerivationOutcome.DERIVED
    assert within_cap.segments is not None
    assert len(within_cap.segments) == exterior_vertex_count


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


def test_over_cap_ring_is_fail_closed_and_typed_apart_from_invalid():
    """F4: an over-cap ring is its OWN outcome. The geometry is valid; our cap binds."""
    result = _result()  # a 4-segment ring
    derived = derive_lot_line_segments(
        "1008350041", provider=_provider_returning(result), max_segments=3
    )
    assert derived.outcome is LotGeometryDerivationOutcome.GEOMETRY_OVER_CAP
    assert derived.segments is None
    assert "cap" in derived.detail


def test_over_cap_and_unusable_geometry_never_conflate_the_two_causes():
    """F4: the two no-segment causes say opposite things about the official source, so their
    outcomes AND their details must differ. Unusable City geometry is a problem with the source;
    an over-cap ring is VALID City geometry against OUR ceiling - a caller must never be told the
    official data is bad when only our cap is in the way."""
    over_cap = derive_lot_line_segments(
        "1008350041", provider=_provider_returning(_result()), max_segments=3
    )
    unusable = derive_lot_line_segments(
        "1008350041", provider=_provider_returning(_result(esri=_EMPTY_RINGS_ESRI))
    )

    assert over_cap.outcome is LotGeometryDerivationOutcome.GEOMETRY_OVER_CAP
    assert unusable.outcome is LotGeometryDerivationOutcome.INVALID_GEOMETRY
    assert over_cap.detail != unusable.detail
    assert "is valid" in over_cap.detail and "not at fault" in over_cap.detail
    assert "not usable" in unusable.detail
    assert "cap" not in unusable.detail


def test_ring_cutter_reports_degenerate_and_over_cap_separately():
    """The defensive DEGENERATE branch of the ring cutter (a polygon the analyzer would normally
    have rejected upstream) is classified apart from the over-cap branch, which is what keeps the
    two caller-visible details from collapsing back into one string. Asserted on the private
    cutter because a canonical geometry that is BOTH assessment-valid and degenerate cannot be
    produced through the real analyzer."""
    from app.scenario.lot_geometry_derivation import (
        _RING_DEGENERATE,
        _RING_OVER_CAP,
        _exterior_ring_segments,
    )

    # canonical geometry = [polygon, ...]; polygon = [exterior_ring, *hole_rings]; ring = [[x, y]].
    triangle_ring = [["0", "0"], ["10", "0"], ["10", "10"]]
    two_vertex_ring = [["0", "0"], ["10", "0"]]

    segments, reason = _exterior_ring_segments([[triangle_ring]], max_segments=800)
    assert reason is None and segments is not None and len(segments) == 3
    assert _exterior_ring_segments([[triangle_ring]], max_segments=2) == (None, _RING_OVER_CAP)
    assert _exterior_ring_segments([[two_vertex_ring]], max_segments=800) == (
        None,
        _RING_DEGENERATE,
    )
    assert _exterior_ring_segments([[]], max_segments=800) == (None, _RING_DEGENERATE)
    assert _exterior_ring_segments([], max_segments=800) == (None, _RING_DEGENERATE)


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


# ---------------------------------------------------------------------------
# DB-039(i): the production provider constructs its resilient client ON RESOLUTION (event loop),
# never inside the returned closure (which the route runs in a threadpool).
# ---------------------------------------------------------------------------


def test_production_provider_builds_its_client_on_resolution_not_per_call(monkeypatch):
    """F5: the route resolves the provider on the event loop and then runs the RETURNED CLOSURE in
    a threadpool. So the client must be built during resolution and the closure must construct
    nothing - otherwise two concurrent worker threads can each see the global as ``None`` and build
    a second client, splitting cache, circuit-breaker state, last-known-good store and metrics.

    A mutant that moved the construction back inside the closure would leave ``built == 0`` after
    the two resolutions and then rise to 1 on first call, reddening both halves."""
    built: list[str] = []

    class _StubClient:
        def __init__(self, *args, **kwargs) -> None:
            built.append("constructed")

        def fetch_lot_geometry(self, canonical_bbl: str):
            return f"fetched:{canonical_bbl}"

    monkeypatch.setattr(derivation_mod, "_PRODUCTION_CLIENT", None)
    monkeypatch.setattr(derivation_mod, "ResilientMapPlutoGeometryClient", _StubClient)

    provider = derivation_mod.production_lot_geometry_provider()
    assert built == ["constructed"]  # built during resolution (on the event loop)

    again = derivation_mod.production_lot_geometry_provider()
    assert built == ["constructed"]  # the cached global is reused, never rebuilt

    # Calling either closure - what actually happens inside the threadpool - constructs NOTHING.
    assert provider("1008350041") == "fetched:1008350041"
    assert again("1000010010") == "fetched:1000010010"
    assert built == ["constructed"]


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
