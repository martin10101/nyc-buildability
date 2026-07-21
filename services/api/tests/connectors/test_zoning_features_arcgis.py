"""GIS Zoning Features connector tests (task M2-T007, scenarios ZF-S1..S13).

Offline, fixture-driven, deterministic: every HTTP interaction is replayed
from the fixture pack in services/api/tests/fixtures/zoning_features/
(captured live from the six official DCP_GIS ArcGIS services on 2026-07-20 UTC,
plus clearly-labeled synthetic derivations) through an injected fake
transport. No test touches the network.

Where a test needs a shape the official API cannot politely provide on
demand (e.g. an inconsistent count), the test derives a clearly-labeled
SYNTHETIC variant from a real fixture inside the test body. Synthetic
variants exercise connector logic only and are never presented as official
data.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
)
from app.connectors.zoning_features_arcgis import (
    LAYER_SPECS,
    SERVICE_ROOT,
    SOURCE_ID,
    ZF_CANONICALIZATION_SPEC,
    CircuitOpenError,
    DisallowedRequestError,
    MalformedResponseError,
    PagingPathologyError,
    RateLimitedError,
    RequestBudgetExceededError,
    ResilientZoningFeaturesClient,
    SchemaDriftError,
    SourceTimeoutError,
    UpstreamError,
    ZoningFeaturesConnectorError,
    build_attribute_where,
    build_count_url,
    build_metadata_url,
    build_query_url,
    extract_layer,
    fetch_layer_count,
    fetch_layer_metadata,
    query_features,
    raw_body_digest,
)
from app.resilience import AnalysisBudget, ResilienceConfig

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "zoning_features"

FIXED_CLOCK = lambda: datetime(2026, 7, 18, 12, 0, 0, tzinfo=UTC)  # noqa: E731

# Live-captured expectations (2026-07-20 UTC capture; identical to the
# G1-corrected research values of 2026-07-16 - the source was last edited
# 2026-07-01 in both windows).
EXPECTED_MAX_RECORD_COUNT = {
    "nyzd": 2000, "nyco": 2000, "nysp": 92, "nysp_sd": 317,
    "nylh": 14, "nyzma": 1292,
}
EXPECTED_COUNTS = {
    "nyzd": 5416, "nyco": 9623, "nysp": 95, "nysp_sd": 336,
    "nylh": 14, "nyzma": 1414,
}
EXPECTED_DATA_LAST_EDITED_MS = {
    "nyzd": 1782912288115, "nyco": 1782912829636, "nysp": 1782912605345,
    "nysp_sd": 1782912514806, "nylh": 1782912700015, "nyzma": 1782912214592,
}
META_FIXTURES = {
    "nyzd": "ZF01a_meta_nyzd.json", "nyco": "ZF01b_meta_nyco.json",
    "nysp": "ZF01c_meta_nysp.json", "nysp_sd": "ZF01d_meta_nysp_sd.json",
    "nylh": "ZF01e_meta_nylh.json", "nyzma": "ZF01f_meta_nyzma.json",
}
COUNT_FIXTURES = {
    "nyzd": "ZF02a_count_nyzd.json", "nyco": "ZF02b_count_nyco.json",
    "nysp": "ZF02c_count_nysp.json", "nysp_sd": "ZF02d_count_nysp_sd.json",
    "nylh": "ZF02e_count_nylh.json", "nyzma": "ZF02f_count_nyzma.json",
}
NYLH_PAGES = [
    "ZF04a_page_nylh_offset0.json",
    "ZF04b_page_nylh_offset6.json",
    "ZF04c_page_nylh_offset12.json",
]

# Cross-platform determinism anchors (ZF-S10): CI on a different OS must
# reproduce these exact canonical-normalized digests from the committed
# fixtures, or the digesting pipeline is not deterministic.
NYLH_EXTRACT_NORMALIZED_DIGEST = (
    "sha256:aa48af94d1c66d8ab567107b454cd307da8a15313f32efcfdccc23fbae54c947"
)
ZF03_QUERY_NORMALIZED_DIGEST = (
    "sha256:a7570d138d4cbac178be036a7d7401eb5ffd092eeb323d65c929aa5a6fa2c0da"
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str, headers: dict | None = None) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(
        status=fixture["http_status"],
        body=fixture["response_body_raw"],
        headers=headers or {},
    )


class FakeTransport:
    """Replays a scripted sequence of responses/exceptions and records calls."""

    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted - unexpected extra request")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class FakeMonotonic:
    def __init__(self):
        self.value = 1000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def run_kwargs(transport: FakeTransport, **overrides):
    kwargs = dict(
        transport=transport,
        sleep=SleepRecorder(),
        clock=FIXED_CLOCK,
        rng=Random(42),
        correlation_id="test-corr",
    )
    kwargs.update(overrides)
    return kwargs


def nylh_extract_script() -> list[TransportResponse]:
    return [
        fixture_response(META_FIXTURES["nylh"]),
        fixture_response(COUNT_FIXTURES["nylh"]),
        *[fixture_response(name) for name in NYLH_PAGES],
    ]


def make_client(script: list, config: ResilienceConfig, clock: FakeMonotonic):
    transport = FakeTransport(script)
    client = ResilientZoningFeaturesClient(
        config=config,
        transport=transport,
        now=clock,
        wall_clock=FIXED_CLOCK,
        sleep=SleepRecorder(),
        rng=Random(7),
    )
    return client, transport


CLIENT_CONFIG = ResilienceConfig(
    cache_ttl_seconds=100.0,
    retry_max_attempts=2,
    backoff_base_seconds=0.01,
    backoff_cap_seconds=0.02,
    breaker_failure_threshold=1,
    breaker_cooldown_seconds=60.0,
    lkg_max_age_seconds=86_400.0,
)


# --------------------------------------------------------------------------
# ZF-S1 - schema snapshot x6 + typed negatives
# --------------------------------------------------------------------------


@pytest.mark.parametrize("layer", sorted(LAYER_SPECS))
def test_s1_metadata_snapshot_validates_all_six_layers(layer) -> None:
    transport = FakeTransport([fixture_response(META_FIXTURES[layer])])
    meta = fetch_layer_metadata(layer, **run_kwargs(transport))
    assert meta.layer == layer
    assert meta.object_id_field == "OBJECTID"
    assert meta.max_record_count == EXPECTED_MAX_RECORD_COUNT[layer]
    assert meta.wkid == 102718 and meta.latest_wkid == 2263
    assert meta.geometry_type == "esriGeometryPolygon"
    assert meta.supports_pagination and meta.supports_order_by
    assert meta.source_data_last_edited_ms == EXPECTED_DATA_LAST_EDITED_MS[layer]
    assert meta.drift_signals == []
    # Connector constants must mirror the live-captured schema EXACTLY
    # (transcription drift between constant and fixture fails the build).
    assert meta.fields == LAYER_SPECS[layer].fields
    # URL builder reproduces the capture URL byte-identically.
    fixture = load_fixture(META_FIXTURES[layer])
    assert meta.request_url == fixture["request_url"] == build_metadata_url(layer)
    assert transport.calls[0]["url"] == meta.request_url


def test_s1_all_six_data_last_edited_decode_to_2026_07_01() -> None:
    for layer in LAYER_SPECS:
        transport = FakeTransport([fixture_response(META_FIXTURES[layer])])
        meta = fetch_layer_metadata(layer, **run_kwargs(transport))
        assert meta.source_data_last_edited.startswith("2026-07-01T"), layer


@pytest.mark.parametrize(
    ("fixture", "expected_fragment"),
    [
        ("ZF90_meta_nyzd_missing_objectid_synthetic.json", "objectIdField"),
        ("ZF91_meta_nyzd_wrong_crs_synthetic.json", "EPSG:2263"),
        ("ZF92_meta_nyzd_missing_maxrecordcount_synthetic.json", "maxRecordCount"),
    ],
)
def test_s1_metadata_negatives_fail_typed(fixture, expected_fragment) -> None:
    transport = FakeTransport([fixture_response(fixture)])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_layer_metadata("nyzd", **run_kwargs(transport))
    assert excinfo.value.error_type == "schema_drift"
    assert expected_fragment in str(excinfo.value)
    payload = excinfo.value.to_payload()
    assert payload["source_id"] == SOURCE_ID
    assert payload["correlation_id"] == "test-corr"


# --------------------------------------------------------------------------
# ZF-S2 - count baseline x6 with provenance
# --------------------------------------------------------------------------


@pytest.mark.parametrize("layer", sorted(LAYER_SPECS))
def test_s2_count_baselines_with_provenance(layer) -> None:
    transport = FakeTransport([fixture_response(COUNT_FIXTURES[layer])])
    result = fetch_layer_count(layer, **run_kwargs(transport))
    assert result.count == EXPECTED_COUNTS[layer]
    fixture = load_fixture(COUNT_FIXTURES[layer])
    assert result.request_url == fixture["request_url"] == build_count_url(layer)
    assert result.retrieved_at == "2026-07-18T12:00:00Z"
    assert result.raw_digest == raw_body_digest(fixture["response_body_raw"])


def test_s2_cap_exceedance_hazard_is_real_in_fixtures() -> None:
    """Documents research C3: unpaged reads WOULD truncate three layers and
    nylh sits exactly at its cap - the reason paging is mandatory."""
    for layer in ("nysp", "nysp_sd", "nyzma"):
        assert EXPECTED_COUNTS[layer] > EXPECTED_MAX_RECORD_COUNT[layer], layer
    assert EXPECTED_COUNTS["nylh"] == EXPECTED_MAX_RECORD_COUNT["nylh"]


def test_s2_count_malformed_body_is_typed_not_zero() -> None:
    transport = FakeTransport([TransportResponse(200, '{"nocount": true}')])
    with pytest.raises(MalformedResponseError):
        fetch_layer_count("nyzd", **run_kwargs(transport))


# --------------------------------------------------------------------------
# ZF-S3 - bounded single-feature query with full provenance stamps
# --------------------------------------------------------------------------


def test_s3_single_feature_query_nyzd_r3_2() -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nyzd"]),
            fixture_response("ZF03_query_nyzd_single_R3-2.json"),
        ]
    )
    result = query_features(
        "nyzd", "ZONEDIST", "R3-2", result_record_count=1,
        **run_kwargs(transport),
    )
    assert result.status == "ok"
    assert result.record_count == 1
    feature = result.features[0]
    assert feature["object_id"] == 86
    assert feature["attributes"]["ZONEDIST"] == "R3-2"
    assert feature["geometry"]["rings"]  # polygon rings preserved verbatim
    assert result.crs["wkid"] == 102718 and result.crs["latest_wkid"] == 2263
    assert result.crs["authority"].startswith("EPSG:2263")
    # Provenance stamps: endpoint, layer, retrieval + source edit timestamps.
    fixture = load_fixture("ZF03_query_nyzd_single_R3-2.json")
    assert result.request_url == fixture["request_url"]
    assert result.retrieved_at == "2026-07-18T12:00:00Z"
    assert result.source_data_last_edited == "2026-07-01T13:24:48Z"
    assert result.source_data_last_edited_ms == 1782912288115
    assert result.raw_digest == raw_body_digest(fixture["response_body_raw"])
    assert result.normalized_digest == ZF03_QUERY_NORMALIZED_DIGEST
    assert result.digest_canonicalization == ZF_CANONICALIZATION_SPEC
    # Bounded query hit the transfer limit: noted, not a pathology.
    assert result.exceeded_transfer_limit is True
    assert any(note.startswith("exceeded_transfer_limit") for note in result.notes)
    assert result.staleness is None  # fresh retrieval (two-staleness rule)


def test_s3_url_builder_reproduces_captured_query_url() -> None:
    where = build_attribute_where("nyzd", "ZONEDIST", "R3-2")
    url = build_query_url(
        "nyzd", where, out_fields="*", order_by_field="OBJECTID",
        result_record_count=1, result_offset=0,
    )
    assert url == load_fixture("ZF03_query_nyzd_single_R3-2.json")["request_url"]


def test_s3_nyzma_date_field_preserved_verbatim() -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nyzma"]),
            fixture_response("ZF07_query_nyzma_single.json"),
        ]
    )
    result = query_features("nyzma", "STATUS", "Adopted", **run_kwargs(transport))
    attrs = result.features[0]["attributes"]
    assert attrs["STATUS"] == "Adopted"
    # esriFieldTypeDate EFFECTIVE is null on this live record: preserved as
    # None, never fabricated (observed live 2026-07-20 UTC).
    assert attrs["EFFECTIVE"] is None
    assert attrs["ULURPNO"] == "810449zmk"


# --------------------------------------------------------------------------
# ZF-S4 - complete multi-page extraction (real captured pages)
# --------------------------------------------------------------------------


def test_s4_paged_extraction_complete_no_skip_no_duplicate() -> None:
    transport = FakeTransport(nylh_extract_script())
    result = extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert result.status == "ok"
    assert result.expected_count == 14
    assert result.record_count == 14
    assert result.page_count == 3
    oids = [feature["object_id"] for feature in result.features]
    assert oids == list(range(1, 15))  # complete, ordered, no skip, no dup
    # Deterministic URL sequence reproduces the capture byte-identically.
    assert result.page_request_urls == [
        load_fixture(name)["request_url"] for name in NYLH_PAGES
    ]
    assert [call["url"] for call in transport.calls] == [
        result.metadata_request_url,
        result.count_request_url,
        *result.page_request_urls,
    ]
    assert len(transport.calls) == 5  # bounded: exactly meta + count + 3 pages
    assert result.page_raw_digests == [
        raw_body_digest(load_fixture(name)["response_body_raw"]) for name in NYLH_PAGES
    ]
    assert len(set(result.page_raw_digests)) == 3
    assert result.count_raw_digest != result.metadata_raw_digest
    assert result.source_data_last_edited == "2026-07-01T13:31:40Z"
    assert result.crs["authority"].startswith("EPSG:2263")
    assert result.staleness is None


def test_s4_exceeded_transfer_limit_respected_across_boundaries() -> None:
    """Pages 1-2 carry exceededTransferLimit=true (verified live, resolving
    research OQ-11); the connector keeps paging until the short final page."""
    page1 = json.loads(load_fixture(NYLH_PAGES[0])["response_body_raw"])
    page3 = json.loads(load_fixture(NYLH_PAGES[2])["response_body_raw"])
    assert page1["exceededTransferLimit"] is True
    assert "exceededTransferLimit" not in page3


# --------------------------------------------------------------------------
# ZF-S5 - paging pathologies: typed failures, never loops or truncation
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("page2_fixture", "reason"),
    [
        ("ZF96_page_nylh_duplicate_page_synthetic.json", "duplicate_page"),
        ("ZF97_page_nylh_repeated_oid_synthetic.json", "repeated_object_id"),
        ("ZF98_page_nylh_zero_progress_synthetic.json", "zero_progress"),
    ],
)
def test_s5_paging_pathologies_fail_typed(page2_fixture, reason) -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            fixture_response(COUNT_FIXTURES["nylh"]),
            fixture_response(NYLH_PAGES[0]),
            fixture_response(page2_fixture),
        ]
    )
    with pytest.raises(PagingPathologyError) as excinfo:
        extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert excinfo.value.error_type == "paging_pathology"
    assert excinfo.value.detail["reason"] == reason
    assert transport.script == []  # aborted typed exactly at the bad page


def test_s5_page_budget_exhaustion_bounds_requests() -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            fixture_response(COUNT_FIXTURES["nylh"]),
            fixture_response(NYLH_PAGES[0]),
            fixture_response(NYLH_PAGES[1]),
        ]
    )
    with pytest.raises(PagingPathologyError) as excinfo:
        extract_layer("nylh", page_size=6, max_pages=2, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] == "page_budget_exhausted"
    # Test-enforced upper bound: meta + count + exactly max_pages requests.
    assert len(transport.calls) == 4


def test_s5_count_mismatch_is_typed_never_silent() -> None:
    """SYNTHETIC variant: official count inflated to 15 in the test body -
    complete extraction of 14 must fail typed, never serve silently."""
    count_fixture = load_fixture(COUNT_FIXTURES["nylh"])
    inflated = TransportResponse(200, '{"count":15}')
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            inflated,
            *[fixture_response(name) for name in NYLH_PAGES],
        ]
    )
    assert json.loads(count_fixture["response_body_raw"])["count"] == 14
    with pytest.raises(PagingPathologyError) as excinfo:
        extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] == "count_mismatch"
    assert excinfo.value.detail["extracted"] == 14
    assert excinfo.value.detail["expected_count"] == 15


# --------------------------------------------------------------------------
# ZF-S6 - well-formed empty result vs malformed response
# --------------------------------------------------------------------------


def test_s6_well_formed_no_match_is_valid_empty_result() -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nyzd"]),
            fixture_response("ZF05_query_nyzd_nomatch_XX.json"),
        ]
    )
    result = query_features("nyzd", "ZONEDIST", "XX", **run_kwargs(transport))
    assert result.status == "ok"
    assert result.record_count == 0
    assert result.features == []
    assert any(note.startswith("empty_result") for note in result.notes)


def test_s6_empty_layer_count_zero_makes_no_page_requests() -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            TransportResponse(200, '{"count":0}'),  # SYNTHETIC empty layer
        ]
    )
    result = extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert result.record_count == 0 and result.page_count == 0
    assert len(transport.calls) == 2
    assert any(note.startswith("empty_layer") for note in result.notes)


@pytest.mark.parametrize(
    "fixture",
    [
        "ZF99_malformed_truncated_synthetic.json",
        "ZF100_malformed_missing_features_key_synthetic.json",
    ],
)
def test_s6_malformed_page_is_typed_never_empty_result(fixture) -> None:
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            fixture_response(COUNT_FIXTURES["nylh"]),
            fixture_response(fixture),
        ]
    )
    with pytest.raises(MalformedResponseError) as excinfo:
        extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert excinfo.value.error_type == "malformed_response"


def test_s6_feature_without_object_id_is_malformed() -> None:
    page = json.loads(load_fixture(NYLH_PAGES[0])["response_body_raw"])
    del page["features"][0]["attributes"]["OBJECTID"]  # SYNTHETIC variant
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            TransportResponse(200, json.dumps(page)),
        ]
    )
    with pytest.raises(MalformedResponseError):
        query_features("nylh", "LHLBL", "LH-1", **run_kwargs(transport))


# --------------------------------------------------------------------------
# ZF-S7 - ArcGIS error object with HTTP 200 is a typed upstream error
# --------------------------------------------------------------------------


def test_s7_live_captured_error_with_http_200_is_upstream_error() -> None:
    fixture = load_fixture("ZF06_arcgis_error_bad_field.json")
    assert fixture["http_status"] == 200  # live-verified AGOL behavior
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nyzd"]),
            fixture_response("ZF06_arcgis_error_bad_field.json"),
        ]
    )
    with pytest.raises(UpstreamError) as excinfo:
        query_features("nyzd", "ZONEDIST", "R3-2", **run_kwargs(transport))
    assert excinfo.value.error_type == "upstream_error"
    assert excinfo.value.detail["arcgis_error_code"] == 400
    # Distinguishable from a transport-level failure: no http_status detail,
    # an explicit arcgis_error_code instead.
    assert "http_status" not in excinfo.value.detail


def test_s7_error_envelope_variant_and_metadata_path() -> None:
    transport = FakeTransport(
        [fixture_response("ZF102_arcgis_error_http200_synthetic.json")]
    )
    with pytest.raises(UpstreamError) as excinfo:
        fetch_layer_metadata("nylh", **run_kwargs(transport))
    assert excinfo.value.detail["arcgis_error_code"] == 400


# --------------------------------------------------------------------------
# ZF-S8 - resilience via the M1-T009 framework
# --------------------------------------------------------------------------


def test_s8_timeout_persists_to_typed_timeout_with_bounded_retries() -> None:
    transport = FakeTransport([TransportTimeout(), TransportTimeout(), TransportTimeout()])
    sleeps = SleepRecorder()
    with pytest.raises(SourceTimeoutError) as excinfo:
        fetch_layer_metadata(
            "nyzd", **run_kwargs(transport, sleep=sleeps, max_attempts=3),
        )
    assert excinfo.value.error_type == "timeout"
    assert len(transport.calls) == 3
    assert len(sleeps.delays) == 2  # jittered backoff between attempts


def test_s8_429_retry_after_honored_exactly_then_success() -> None:
    transport = FakeTransport(
        [
            TransportResponse(429, "", headers={"retry-after": "7"}),
            fixture_response(META_FIXTURES["nyzd"]),
        ]
    )
    sleeps = SleepRecorder()
    meta = fetch_layer_metadata(
        "nyzd", **run_kwargs(transport, sleep=sleeps, max_attempts=2),
    )
    assert meta.max_record_count == 2000
    assert sleeps.delays == [7.0]  # honored EXACTLY, no jitter


def test_s8_429_persisted_is_typed_rate_limited() -> None:
    transport = FakeTransport(
        [fixture_response("ZF101_rate_limited_429_synthetic.json")] * 2
    )
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_layer_metadata("nyzd", **run_kwargs(transport, max_attempts=2))
    assert excinfo.value.error_type == "rate_limited"


def test_s8_retry_after_beyond_cap_fails_typed_without_blocking() -> None:
    transport = FakeTransport(
        [TransportResponse(429, "", headers={"retry-after": "999"})]
    )
    sleeps = SleepRecorder()
    with pytest.raises(RateLimitedError):
        fetch_layer_metadata(
            "nyzd",
            **run_kwargs(transport, sleep=sleeps, max_attempts=3, retry_after_cap=120.0),
        )
    assert sleeps.delays == []  # never blocked a thread for minutes
    assert len(transport.calls) == 1


def test_s8_network_failure_persists_to_typed_upstream_error() -> None:
    transport = FakeTransport([TransportFailure("network failure: gaierror")] * 2)
    with pytest.raises(UpstreamError) as excinfo:
        fetch_layer_metadata("nyzd", **run_kwargs(transport, max_attempts=2))
    assert excinfo.value.detail["reason_kind"] == "network"


def test_s8_request_budget_exhaustion_is_typed_and_pre_io() -> None:
    budget = AnalysisBudget(2, analysis_id="analysis-1")
    transport = FakeTransport(nylh_extract_script())
    with pytest.raises(RequestBudgetExceededError) as excinfo:
        extract_layer("nylh", page_size=6, budget=budget, **run_kwargs(transport))
    assert excinfo.value.error_type == "budget_exhausted"
    assert len(transport.calls) == 2  # meta + count consumed; page refused pre-I/O
    assert budget.consumed == 2


def test_s8_circuit_open_is_typed_and_makes_no_upstream_call() -> None:
    clock = FakeMonotonic()
    # retry_max_attempts=2: two timeouts exhaust the first call's retries.
    client, transport = make_client(
        [TransportTimeout(), TransportTimeout()], CLIENT_CONFIG, clock
    )
    with pytest.raises(SourceTimeoutError):
        client.extract_layer("nylh", correlation_id="c1")
    calls_after_first = len(transport.calls)
    with pytest.raises(CircuitOpenError) as excinfo:
        client.extract_layer("nylh", correlation_id="c2")
    assert excinfo.value.error_type == "circuit_open"
    assert len(transport.calls) == calls_after_first  # zero upstream I/O
    assert client.metrics.count("breaker_fast_reject") == 1


def test_s8_last_known_good_serve_stamps_transport_staleness_truthfully() -> None:
    clock = FakeMonotonic()
    script = nylh_extract_script() + [TransportTimeout(), TransportTimeout()]
    client, transport = make_client(script, CLIENT_CONFIG, clock)
    fresh = client.extract_layer("nylh", page_size=6, correlation_id="c1")
    assert fresh.staleness is None  # fresh retrieval: no transport staleness
    clock.advance(200.0)  # beyond cache TTL (100s), within LKG max age
    stale = client.extract_layer("nylh", page_size=6, correlation_id="c2")
    assert stale.staleness == {
        "served_from_cache": True,
        "stale": True,
        "upstream_error_type": "timeout",
        "original_retrieved_at": fresh.retrieved_at,
        "age_seconds": 200.0,
    }
    assert any(
        note.startswith("served_from_last_known_good:") for note in stale.notes
    )
    # The stale serve is because the UPSTREAM failed - never because the
    # source dataset is old; source provenance is untouched (ZF-S12 pairs).
    assert stale.source_data_last_edited == fresh.source_data_last_edited
    assert stale.retrieved_at == fresh.retrieved_at


def test_s8_error_taxonomy_states_are_distinguishable() -> None:
    taxonomy = {
        UpstreamError: "upstream_error",
        MalformedResponseError: "malformed_response",
        SchemaDriftError: "schema_drift",
        RequestBudgetExceededError: "budget_exhausted",
        CircuitOpenError: "circuit_open",
        SourceTimeoutError: "timeout",
        RateLimitedError: "rate_limited",
        DisallowedRequestError: "disallowed_request",
        PagingPathologyError: "paging_pathology",
    }
    assert len(set(taxonomy.values())) == len(taxonomy)  # all distinguishable
    for cls, error_type in taxonomy.items():
        exc = cls("m", correlation_id="c")
        assert exc.error_type == error_type
        assert isinstance(exc, ZoningFeaturesConnectorError)
        assert exc.to_payload()["error_type"] == error_type


# --------------------------------------------------------------------------
# ZF-S9 - schema drift: renamed field fails loud, added field degrades typed
# --------------------------------------------------------------------------


def test_s9_renamed_field_fails_typed_never_guessed() -> None:
    transport = FakeTransport(
        [fixture_response("ZF93_meta_nyzd_renamed_field_synthetic.json")]
    )
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_layer_metadata("nyzd", **run_kwargs(transport))
    assert excinfo.value.detail["missing_fields"] == ["ZONEDIST"]


def test_s9_added_field_is_visible_typed_degradation() -> None:
    transport = FakeTransport(
        [fixture_response("ZF94_meta_nyzd_added_field_synthetic.json")]
    )
    meta = fetch_layer_metadata("nyzd", **run_kwargs(transport))
    assert "added_field:NEW_UNEXPECTED" in meta.drift_signals


def test_s9_added_field_signal_propagates_into_query_result() -> None:
    # M2-T007 G3/G4 D2 cleanup: named for the path it actually exercises
    # (query_features, which re-validates the metadata it fetches), not
    # extraction; the prior name implied extract_layer and the test carried a
    # dead unused page load. The added_field drift signal from the ZF94
    # synthetic metadata propagates into the query result's drift_signals.
    transport = FakeTransport(
        [
            fixture_response("ZF94_meta_nyzd_added_field_synthetic.json"),
            fixture_response("ZF03_query_nyzd_single_R3-2.json"),
        ]
    )
    result = query_features("nyzd", "ZONEDIST", "R3-2", **run_kwargs(transport))
    assert "added_field:NEW_UNEXPECTED" in result.drift_signals


def test_s9_response_object_id_field_mismatch_is_drift() -> None:
    page = json.loads(load_fixture(NYLH_PAGES[0])["response_body_raw"])
    page["objectIdFieldName"] = "FID"  # SYNTHETIC drift variant
    transport = FakeTransport(
        [
            fixture_response(META_FIXTURES["nylh"]),
            TransportResponse(200, json.dumps(page)),
        ]
    )
    with pytest.raises(SchemaDriftError):
        query_features("nylh", "LHLBL", "LH-1", **run_kwargs(transport))


def test_s9_retyped_field_fails_typed() -> None:
    meta = json.loads(load_fixture(META_FIXTURES["nylh"])["response_body_raw"])
    for entry in meta["fields"]:
        if entry["name"] == "LHNAME":
            entry["type"] = "esriFieldTypeInteger"  # SYNTHETIC drift variant
    transport = FakeTransport([TransportResponse(200, json.dumps(meta))])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_layer_metadata("nylh", **run_kwargs(transport))
    assert "LHNAME" in excinfo.value.detail["retyped"]


# --------------------------------------------------------------------------
# ZF-S10 - determinism: separate raw and normalized digests
# --------------------------------------------------------------------------


def test_s10_extraction_digests_reproduce_across_runs() -> None:
    results = []
    for _ in range(2):
        transport = FakeTransport(nylh_extract_script())
        results.append(extract_layer("nylh", page_size=6, **run_kwargs(transport)))
    first, second = results
    assert first.normalized_digest == second.normalized_digest
    assert first.page_raw_digests == second.page_raw_digests
    # Cross-platform anchor: CI on another OS must reproduce this exact
    # value from the committed fixtures.
    assert first.normalized_digest == NYLH_EXTRACT_NORMALIZED_DIGEST


def test_s10_normalized_digest_is_independent_of_response_order() -> None:
    """Shuffled-fixture proof: same features in a different upstream order
    produce the SAME canonical-normalized digest but a DIFFERENT raw digest
    (raw pins bytes; normalized pins content)."""
    fixture = load_fixture(NYLH_PAGES[0])
    page = json.loads(fixture["response_body_raw"])
    shuffled = json.loads(fixture["response_body_raw"])
    Random(99).shuffle(shuffled["features"])
    assert [f["attributes"]["OBJECTID"] for f in shuffled["features"]] != [
        f["attributes"]["OBJECTID"] for f in page["features"]
    ]
    results = []
    for body in (json.dumps(page), json.dumps(shuffled)):
        transport = FakeTransport(
            [
                fixture_response(META_FIXTURES["nylh"]),
                TransportResponse(200, body),
            ]
        )
        results.append(
            query_features("nylh", "LHLBL", "LH-1", **run_kwargs(transport))
        )
    original, reordered = results
    assert original.normalized_digest == reordered.normalized_digest
    assert original.raw_digest != reordered.raw_digest
    assert [f["object_id"] for f in reordered.features] == sorted(
        f["object_id"] for f in reordered.features
    )


def test_s10_raw_and_normalized_digests_are_kept_separately() -> None:
    transport = FakeTransport(nylh_extract_script())
    result = extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert result.normalized_digest not in result.page_raw_digests
    assert result.metadata_raw_digest not in result.page_raw_digests
    assert all(d.startswith("sha256:") for d in result.page_raw_digests)
    assert result.normalized_digest.startswith("sha256:")
    assert "raw_digest" in ZF_CANONICALIZATION_SPEC
    assert "normalized_digest" in ZF_CANONICALIZATION_SPEC


def test_s10_manifest_digests_match_committed_fixture_bytes() -> None:
    """Manifest integrity: every committed fixture's body hashes to the
    manifest's recorded digest, and every ZF fixture file is in the manifest."""
    manifest = json.loads((FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    by_file = {entry["file"]: entry for entry in manifest["fixtures"]}
    fixture_files = sorted(
        p.name for p in FIXTURE_DIR.glob("ZF*.json")
    )
    assert fixture_files == sorted(by_file)
    for name in fixture_files:
        body = load_fixture(name)["response_body_raw"]
        expected = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        assert by_file[name]["response_body_sha256"] == expected, name
        assert by_file[name]["classification"] in ("raw", "synthetic")
        assert by_file[name]["retrieval_timestamp_utc"], name
        assert by_file[name]["official_endpoint"].startswith(SERVICE_ROOT), name


# --------------------------------------------------------------------------
# ZF-S11 - allowlist security: refusal before network, bounded parameters
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_layer",
    [
        "nyzd/../../evil",
        "https://evil.example/arcgis/rest/services/nyzd/FeatureServer",
        "v_Zoning_Districts_NYZD",
        "NYZD",
        "nyzd ",
        "",
        None,
        123,
    ],
)
def test_s11_non_allowlisted_layer_refused_before_network(bad_layer) -> None:
    transport = FakeTransport([])
    with pytest.raises(DisallowedRequestError) as excinfo:
        extract_layer(bad_layer, **run_kwargs(transport))
    assert excinfo.value.error_type == "disallowed_request"
    assert transport.calls == []  # refusal happens BEFORE any network I/O


def test_s11_resilient_client_refuses_before_cache_and_network() -> None:
    clock = FakeMonotonic()
    client, transport = make_client([], CLIENT_CONFIG, clock)
    with pytest.raises(DisallowedRequestError):
        client.extract_layer("nyzd; DROP TABLE", correlation_id="c1")
    assert transport.calls == []
    assert client.metrics.count("cache_miss") == 0


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("NOSUCHFIELD", "R3-2"),
        ("Shape__Area", "1"),  # real field but not in the queryable allowlist
        ("ZONEDIST;DROP", "R3-2"),
        ("ZONEDIST", "R3-2'; DROP TABLE zoning; --"),  # ';' not allowlisted
        ("ZONEDIST", "value%00"),
        ("ZONEDIST", "a" * 121),
        ("ZONEDIST", ""),
        ("ZONEDIST", None),
    ],
)
def test_s11_bounded_where_refuses_unsafe_input(field_name, value) -> None:
    with pytest.raises(DisallowedRequestError):
        build_attribute_where("nyzd", field_name, value)


def test_s11_quote_in_value_is_escaped_not_injected() -> None:
    where = build_attribute_where("nysp", "SDNAME", "O'Neill District")
    assert where == "SDNAME='O''Neill District'"


def test_s11_out_fields_and_paging_parameters_are_bounded() -> None:
    with pytest.raises(DisallowedRequestError):
        build_query_url(
            "nyzd", "1=1", out_fields=["ZONEDIST", "EVIL"],
            result_record_count=1, result_offset=0,
        )
    with pytest.raises(DisallowedRequestError):
        build_query_url(
            "nyzd", "1=1", order_by_field="EVIL",
            result_record_count=1, result_offset=0,
        )
    for bad_count in (0, -1, 2001, True, "10"):
        with pytest.raises(DisallowedRequestError):
            build_query_url(
                "nyzd", "1=1", result_record_count=bad_count, result_offset=0,
            )
    for bad_offset in (-1, 1_000_001, False, "0"):
        with pytest.raises(DisallowedRequestError):
            build_query_url(
                "nyzd", "1=1", result_record_count=1, result_offset=bad_offset,
            )
    with pytest.raises(DisallowedRequestError):
        build_count_url("nyzd", "1=1 OR OBJECTID>0")


def test_s11_every_built_url_targets_the_pinned_official_root() -> None:
    urls = [
        build_metadata_url("nyzd"),
        build_count_url("nyco"),
        build_query_url(
            "nysp", build_attribute_where("nysp", "SDLBL", "GI"),
            result_record_count=1, result_offset=0,
        ),
    ]
    for url in urls:
        assert url.startswith(
            "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/"
        )


def test_s11_no_tokens_or_secrets_in_requests_fixtures_or_manifest() -> None:
    # Requests carry ONLY the Accept header (keyless official services).
    transport = FakeTransport([fixture_response(META_FIXTURES["nyzd"])])
    fetch_layer_metadata("nyzd", **run_kwargs(transport))
    assert transport.calls[0]["headers"] == {"Accept": "application/json"}
    # Fixture request URLs and the manifest carry no credential material.
    manifest_text = (FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8")
    for needle in ("token=", "apikey", "api_key", "authorization"):
        assert needle not in manifest_text.lower()
    for path in FIXTURE_DIR.glob("ZF*.json"):
        request_url = json.loads(path.read_text(encoding="utf-8"))["request_url"]
        assert "token" not in request_url.lower(), path.name


# --------------------------------------------------------------------------
# ZF-S12 - two-staleness rule: source age is provenance, never serve state
# --------------------------------------------------------------------------


def test_s12_old_source_with_fresh_retrieval_is_not_stale() -> None:
    """Owner directive 2026-07-17: dataLastEditDate is source-dataset
    freshness PROVENANCE. A 2020-vintage source retrieved FRESH must carry
    staleness=None (the builder-side fresh marker), never served_from_cache
    or stale."""
    transport = FakeTransport(
        [
            fixture_response("ZF95_meta_nylh_old_edit_date_synthetic.json"),
            fixture_response(COUNT_FIXTURES["nylh"]),
            *[fixture_response(name) for name in NYLH_PAGES],
        ]
    )
    result = extract_layer("nylh", page_size=6, **run_kwargs(transport))
    assert result.source_data_last_edited == "2020-01-01T00:00:00Z"  # old source
    assert result.source_data_last_edited_ms == 1577836800000
    assert result.staleness is None  # fresh transport: NOT stale, NOT cached
    assert not any("stale" in note.lower() for note in result.notes)


def test_s12_old_source_fresh_retrieval_via_resilient_client() -> None:
    clock = FakeMonotonic()
    script = [
        fixture_response("ZF95_meta_nylh_old_edit_date_synthetic.json"),
        fixture_response(COUNT_FIXTURES["nylh"]),
        *[fixture_response(name) for name in NYLH_PAGES],
    ]
    client, _ = make_client(script, CLIENT_CONFIG, clock)
    result = client.extract_layer("nylh", page_size=6, correlation_id="c1")
    assert result.source_data_last_edited == "2020-01-01T00:00:00Z"
    assert result.staleness is None  # source age NEVER sets transport staleness


def test_s12_cache_hit_serve_does_not_alter_source_timestamps() -> None:
    clock = FakeMonotonic()
    client, transport = make_client(nylh_extract_script(), CLIENT_CONFIG, clock)
    fresh = client.extract_layer("nylh", page_size=6, correlation_id="c1")
    calls_after_fresh = len(transport.calls)
    clock.advance(50.0)  # within the 100s TTL
    cached = client.extract_layer("nylh", page_size=6, correlation_id="c2")
    assert len(transport.calls) == calls_after_fresh  # no upstream I/O
    assert cached.staleness == {
        "served_from_cache": True,
        "stale": False,  # upstream did NOT fail; within-TTL cache serve
        "original_retrieved_at": fresh.retrieved_at,
        "age_seconds": 50.0,
    }
    # Source provenance is copied verbatim - never altered by the serve path.
    assert cached.source_data_last_edited == fresh.source_data_last_edited
    assert cached.source_data_last_edited_ms == fresh.source_data_last_edited_ms
    assert cached.retrieved_at == fresh.retrieved_at
    assert cached.normalized_digest == fresh.normalized_digest


def test_s12_lkg_serve_preserves_source_timestamps_and_flags_transport() -> None:
    clock = FakeMonotonic()
    script = [
        fixture_response("ZF95_meta_nylh_old_edit_date_synthetic.json"),
        fixture_response(COUNT_FIXTURES["nylh"]),
        *[fixture_response(name) for name in NYLH_PAGES],
        TransportTimeout(),
        TransportTimeout(),
    ]
    client, _ = make_client(script, CLIENT_CONFIG, clock)
    fresh = client.extract_layer("nylh", page_size=6, correlation_id="c1")
    clock.advance(150.0)  # cache expired; LKG still valid
    stale = client.extract_layer("nylh", page_size=6, correlation_id="c2")
    assert stale.staleness["stale"] is True
    assert stale.staleness["upstream_error_type"] == "timeout"
    # The OLD source date did not cause the staleness (the timeout did), and
    # the serve did not touch the source timestamps.
    assert stale.source_data_last_edited == "2020-01-01T00:00:00Z"
    assert stale.source_data_last_edited == fresh.source_data_last_edited
    assert stale.retrieved_at == fresh.retrieved_at


# --------------------------------------------------------------------------
# ZF-S13 - regression guards (full-suite greenness is proven by the pytest
# run recorded in the producer report; these assert non-interference)
# --------------------------------------------------------------------------


def test_s13_no_pluto_module_state_is_modified() -> None:
    import app.connectors.pluto_soda as pluto

    assert pluto.SOURCE_ID == "nyc-dcp-pluto-soda"
    assert pluto.DATASET_ID == "64uk-42ks"
    assert SOURCE_ID == "nyc-dcp-zoning-features-arcgis"
    assert SOURCE_ID != pluto.SOURCE_ID


def test_s13_correlation_id_minted_when_absent() -> None:
    transport = FakeTransport([fixture_response(META_FIXTURES["nyzd"])])
    meta = fetch_layer_metadata(
        "nyzd", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK,
        rng=Random(1),
    )
    assert meta.correlation_id  # minted uuid hex
    assert len(meta.correlation_id) == 32
