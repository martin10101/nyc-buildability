"""M2-T012 PI-S6: per-defect fix evidence for the carried LOW defects folded
into this task. Each carried defect gets its own labeled test here.

- M2-T007 G1 D1  (out_fields footgun): an explicit outFields list omitting the
  object-id field is refused up front as a typed disallowed_request, instead of
  producing a page the envelope validator would blame on upstream.
- M2-T007 G3/G4 D1 (untested drift signals): missing_editing_info and
  page_missing_spatial_reference are now asserted emitted.
- M2-T007 G3/G4 D3 (count==cap default-page): a layer whose count equals its
  maxRecordCount extracts in ONE page at the DEFAULT page_size (no extra
  request, no truncation).
- M2-T008 G3/G4 D1 (check_columns_for_drift): doubly-malformed metadata (a
  column dict without a fieldName, alongside a real added column) no longer
  raises TypeError from sorted([None, str]).
- M2-T009 G4 D1 (top-level metadata spatialReference): a drifted TOP-LEVEL
  spatialReference is rejected even when extent.spatialReference is correct.
- M2-T009 metadata-TTL-cache option: the resilient client reuses validated
  metadata across lot fetches within the TTL (one metadata fetch, not one per
  lot).

M2-T007 G3/G4 D2 (test-name mismatch) and M2-T008 G3/G4 O2 (token hermeticity)
are fixed in place in the existing connector suites; see the producer report.

Offline + deterministic: fixture transports replay the committed 2026-07-20
captures; synthetic mutations are labeled in-test. No network I/O.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors import mappluto_geometry_arcgis as mpg
from app.connectors import zoning_features_arcgis as zf
from app.connectors.ztldb_soda import check_columns_for_drift
from app.resilience.config import ResilienceConfig
from app.resilience.transport import TransportResponse

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
ZF_FIX = FIXTURES / "zoning_features"
MPG_FIX = FIXTURES / "mappluto_geometry"
CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731


def _raw(directory: Path, name: str) -> str:
    return json.loads((directory / name).read_text(encoding="utf-8"))["response_body_raw"]


def _doc(directory: Path, name: str) -> dict:
    return json.loads(_raw(directory, name))


def _resp(body, status: int = 200) -> TransportResponse:
    text = body if isinstance(body, str) else json.dumps(body)
    return TransportResponse(status=status, body=text, headers={})


class FakeTransport:
    def __init__(self, script):
        self.script = list(script)
        self.calls: list[str] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append(url)
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def _kwargs(transport: FakeTransport) -> dict:
    return dict(
        transport=transport,
        sleep=lambda s: None,
        clock=CLOCK,
        rng=Random(1),
        correlation_id="defect-test",
    )


class _Monotonic:
    def __init__(self) -> None:
        self.value = 1000.0

    def __call__(self) -> float:
        return self.value


# --------------------------------------------------------------------------
# M2-T007 G1 D1 - out_fields footgun typed as disallowed_request
# --------------------------------------------------------------------------


def test_m2t007_g1d1_out_fields_omitting_object_id_is_disallowed_request() -> None:
    with pytest.raises(zf.DisallowedRequestError) as excinfo:
        zf.build_query_url(
            "nyzd",
            "1=1",
            out_fields=["ZONEDIST"],  # omits OBJECTID: the documented footgun
            order_by_field="OBJECTID",
            result_record_count=1,
            result_offset=0,
        )
    assert "object-id" in str(excinfo.value)
    # Including the object-id field is accepted (default '*' path is unaffected).
    url = zf.build_query_url(
        "nyzd",
        "1=1",
        out_fields=["OBJECTID", "ZONEDIST"],
        order_by_field="OBJECTID",
        result_record_count=1,
        result_offset=0,
    )
    assert "outFields=OBJECTID,ZONEDIST" in url


# --------------------------------------------------------------------------
# M2-T007 G3/G4 D1 - the two drift signals are asserted emitted
# --------------------------------------------------------------------------


def test_m2t007_g3d1_missing_editing_info_drift_signal_is_emitted() -> None:
    doc = _doc(ZF_FIX, "ZF01a_meta_nyzd.json")
    doc.pop("editingInfo", None)  # SYNTHETIC: source omits the freshness stamp
    meta = zf.fetch_layer_metadata("nyzd", **_kwargs(FakeTransport([_resp(doc)])))
    assert "missing_editing_info" in meta.drift_signals


def test_m2t007_g3d1_page_missing_spatial_reference_drift_signal_is_emitted() -> None:
    query = _doc(ZF_FIX, "ZF03_query_nyzd_single_R3-2.json")
    query.pop("spatialReference", None)  # SYNTHETIC: features present, SR absent
    transport = FakeTransport([_resp(_doc(ZF_FIX, "ZF01a_meta_nyzd.json")), _resp(query)])
    result = zf.query_features("nyzd", "ZONEDIST", "R3-2", **_kwargs(transport))
    assert "page_missing_spatial_reference" in result.drift_signals


# --------------------------------------------------------------------------
# M2-T007 G3/G4 D3 - count == maxRecordCount at DEFAULT page_size = one page
# --------------------------------------------------------------------------


def test_m2t007_g3d3_count_equals_cap_extracts_in_one_page_at_default_page_size() -> None:
    meta = _doc(ZF_FIX, "ZF01e_meta_nylh.json")  # nylh maxRecordCount == 14
    # Merge the three captured nylh pages (6 + 6 + 2 = 14) into the ONE page a
    # DEFAULT page_size (= maxRecordCount = 14) request returns for count == cap.
    features: list = []
    envelope: dict | None = None
    for name in (
        "ZF04a_page_nylh_offset0.json",
        "ZF04b_page_nylh_offset6.json",
        "ZF04c_page_nylh_offset12.json",
    ):
        page = _doc(ZF_FIX, name)
        if envelope is None:
            envelope = {k: v for k, v in page.items() if k != "features"}
        features.extend(page["features"])
    assert envelope is not None
    envelope["features"] = features
    envelope["exceededTransferLimit"] = False  # the complete set fits in one page
    transport = FakeTransport(
        [_resp(meta), _resp({"count": 14}), _resp(envelope)]
    )
    result = zf.extract_layer("nylh", **_kwargs(transport))
    assert result.expected_count == 14
    assert result.record_count == 14
    assert result.page_count == 1  # default page_size == cap -> a single page
    assert len(transport.calls) == 3  # metadata + count + one page (no extra request)


# --------------------------------------------------------------------------
# M2-T008 G3/G4 D1 - check_columns_for_drift tolerates doubly-malformed metadata
# --------------------------------------------------------------------------


def test_m2t008_g3d1_check_columns_for_drift_tolerates_doubly_malformed_metadata() -> None:
    # A column dict WITHOUT a fieldName (-> a None key) alongside a real added
    # column previously made sorted(set(live) - ZTLDB_COLUMNS) raise TypeError
    # (None vs str comparison). It must now degrade gracefully.
    metadata = {
        "columns": [
            {"dataTypeName": "text"},  # malformed: no fieldName
            {"fieldName": "unexpected_new_column", "dataTypeName": "text"},  # real add
        ]
    }
    result = check_columns_for_drift(metadata)  # must not raise
    assert "unexpected_new_column" in result["added"]
    assert None not in result["added"]  # the nameless column never becomes a key


# --------------------------------------------------------------------------
# M2-T009 G4 D1 - the TOP-LEVEL metadata spatialReference is asserted
# --------------------------------------------------------------------------


def test_m2t009_g4d1_wrong_top_level_spatial_reference_is_typed_wrong_crs() -> None:
    doc = _doc(MPG_FIX, "MPG01_meta.json")
    assert doc["extent"]["spatialReference"] == {"wkid": 102718, "latestWkid": 2263}
    # SYNTHETIC: drift ONLY the top-level SR; extent SR stays authoritative. The
    # pre-fix code (extent-only assertion) would have accepted this.
    doc["spatialReference"] = {"wkid": 4326, "latestWkid": 4326}
    with pytest.raises(mpg.WrongCRSError) as excinfo:
        mpg.fetch_layer_metadata(**_kwargs(FakeTransport([_resp(doc)])))
    assert "top-level" in str(excinfo.value)


# --------------------------------------------------------------------------
# M2-T009 - opt-in metadata TTL cache reuses metadata across lot fetches
# --------------------------------------------------------------------------


def test_m2t009_metadata_ttl_cache_reuses_metadata_across_lot_fetches() -> None:
    transport = FakeTransport(
        [
            _resp(_raw(MPG_FIX, "MPG01_meta.json")),  # metadata: fetched ONCE
            _resp(_raw(MPG_FIX, "MPG02_lot_single_1008350041.json")),  # lot 1
            _resp(_raw(MPG_FIX, "MPG04_lot_condo_billing_1000157501.json")),  # lot 2
        ]
    )
    client = mpg.ResilientMapPlutoGeometryClient(
        config=ResilienceConfig(
            cache_ttl_seconds=100.0,
            retry_max_attempts=2,
            backoff_base_seconds=0.01,
            backoff_cap_seconds=0.02,
        ),
        transport=transport,
        now=_Monotonic(),
        wall_clock=CLOCK,
        sleep=lambda s: None,
        rng=Random(7),
        metadata_cache_ttl_seconds=1000.0,  # opt-in metadata reuse
    )
    r1 = client.fetch_lot_geometry("1008350041")
    r2 = client.fetch_lot_geometry("1000157501")  # different BBL: result-cache miss
    assert r1.outcome == "single_feature"
    assert r2.requested_bbl == "1000157501"
    # metadata fetched once (call 1) + two lot queries (calls 2,3); the second
    # lot fetch reused the cached metadata instead of refetching it.
    assert len(transport.calls) == 3


def test_m2t009_metadata_ttl_cache_off_by_default_refetches_metadata() -> None:
    # Default (option unset): behavior is unchanged - metadata is fetched per
    # lot fetch, so two distinct BBLs cost four upstream requests.
    transport = FakeTransport(
        [
            _resp(_raw(MPG_FIX, "MPG01_meta.json")),
            _resp(_raw(MPG_FIX, "MPG02_lot_single_1008350041.json")),
            _resp(_raw(MPG_FIX, "MPG01_meta.json")),
            _resp(_raw(MPG_FIX, "MPG04_lot_condo_billing_1000157501.json")),
        ]
    )
    client = mpg.ResilientMapPlutoGeometryClient(
        config=ResilienceConfig(cache_ttl_seconds=100.0, retry_max_attempts=2),
        transport=transport,
        now=_Monotonic(),
        wall_clock=CLOCK,
        sleep=lambda s: None,
        rng=Random(7),
    )
    client.fetch_lot_geometry("1008350041")
    client.fetch_lot_geometry("1000157501")
    assert len(transport.calls) == 4  # metadata refetched per lot (unchanged)
