"""Acceptance scenarios ZT-S1..ZT-S12, ZT-S15, ZT-S16 for the ZTLDB SODA
connector (task M2-T008). ZT-S13/ZT-S14 (cross-source reconciliation) live
in tests/profile/test_ztldb_crosscheck.py; ZT-S17 is the full-suite run
recorded in the producer report.

Offline and deterministic: fixture transports replay the committed
2026-07-20 official captures (tests/fixtures/ztldb, raw) and the clearly
labeled synthetic derivations. No network I/O ever happens here.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.bbl import BBLValidationError
from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
)
from app.connectors.ztldb_soda import (
    API_VIEWS_URL,
    APPENDIX_C_OVERLAYS,
    APPENDIX_D_LIMITED_HEIGHT,
    BASE_URL,
    DATASET_ID,
    HARD_MAX_PAGES,
    NOT_APPLICABLE_WHEN_ABSENT,
    PARK_CAVEAT,
    RECORD_QUERY_LIMIT,
    SOURCE_ID,
    SOURCE_STALENESS_THRESHOLD_DAYS,
    ZT_CANONICALIZATION_SPEC,
    ZTLDB_COLUMN_TYPES,
    ZTLDB_COLUMNS,
    CircuitOpenError,
    DisallowedRequestError,
    MalformedResponseError,
    PagingPathologyError,
    RateLimitedError,
    RequestBudgetExceededError,
    ResilientZtldbFetcher,
    SchemaDriftError,
    SourceTimeoutError,
    UpstreamError,
    ZtldbConnectorError,
    build_page_url,
    build_record_url,
    check_columns_for_drift,
    fetch_by_bbl,
    fetch_source_freshness,
    scan_rows,
)
from app.resilience.budget import AnalysisBudget
from app.resilience.config import ResilienceConfig

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "ztldb"

# Retrieval-day clock: the captured dataset metadata (fixture ZT08) carries
# rowsUpdatedAt 1775414816 = 2026-04-05T18:46:56Z, ~105.7 days earlier.
FIXED_CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731
# A clock shortly after the dataset publication: the SAME fixture is a
# FRESH source publication from this vantage point.
APRIL_CLOCK = lambda: datetime(2026, 4, 10, 12, 0, 0, tzinfo=UTC)  # noqa: E731

# Cross-platform determinism anchor (ZT-S15): CI on another OS must
# reproduce this exact normalized digest from the committed ZT01 fixture.
ZT01_NORMALIZED_DIGEST = (
    "sha256:5ac370992b87ff2da5eeaf883d264b9b30658da0c5bdec555fe4a6482cfc2564"
)


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(fixture["http_status"], fixture["response_body_raw"])


class FakeTransport:
    """Scripted transport double; items are TransportResponse or transport
    exceptions to raise."""

    def __init__(self, items):
        self.items = list(items)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        item = self.items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class FakeMonotonic:
    def __init__(self):
        self.value = 0.0

    def advance(self, seconds: float) -> None:
        self.value += seconds

    def __call__(self) -> float:
        return self.value


def run_kwargs(transport, **overrides):
    kwargs = dict(
        transport=transport,
        sleep=SleepRecorder(),
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )
    kwargs.update(overrides)
    return kwargs


def make_freshness(clock=FIXED_CLOCK):
    transport = FakeTransport([fixture_response("ZT08_api_views_metadata.json")])
    return fetch_source_freshness(
        transport=transport, sleep=SleepRecorder(), clock=clock, rng=Random(1),
        app_token=None,
    )


def fetch_record(record_fixture: str, bbl: str, **overrides):
    """One-record fetch with an injected (fixture-derived) freshness."""
    transport = FakeTransport([fixture_response(record_fixture)])
    return fetch_by_bbl(
        bbl,
        freshness=make_freshness(overrides.pop("clock", FIXED_CLOCK)),
        **run_kwargs(transport, **overrides),
    )


def fetch_body(body: str, bbl: str, **overrides):
    transport = FakeTransport([TransportResponse(200, body)])
    return fetch_by_bbl(
        bbl, freshness=make_freshness(), **run_kwargs(transport, **overrides)
    )


def mutated_record_body(fixture: str, mutate) -> str:
    """SYNTHETIC in-test variant of a committed capture (exercises connector
    logic only; never presented as official data)."""
    records = json.loads(load_fixture(fixture)["response_body_raw"])
    mutate(records[0])
    return json.dumps(records)


CLIENT_CONFIG = ResilienceConfig(
    cache_ttl_seconds=100.0,
    cache_max_entries=10,
    retry_max_attempts=2,
    backoff_base_seconds=0.01,
    backoff_cap_seconds=0.02,
    retry_after_max_wait_seconds=120.0,
    breaker_failure_threshold=1,
    breaker_cooldown_seconds=60.0,
    lkg_max_age_seconds=1000.0,
    lkg_max_entries=10,
)


def make_client(script, config=CLIENT_CONFIG, clock=None):
    clock = clock or FakeMonotonic()
    transport = FakeTransport(script)
    client = ResilientZtldbFetcher(
        config=config,
        transport=transport,
        now=clock,
        wall_clock=FIXED_CLOCK,
        sleep=SleepRecorder(),
        rng=Random(1),
    )
    return client, transport, clock


def fresh_fetch_script():
    return [
        fixture_response("ZT08_api_views_metadata.json"),
        fixture_response("ZT01_record_single_lot.json"),
    ]


# --------------------------------------------------------------------------
# ZT-S1 - single-lot normal: 16-column contract, string-serialized numbers
# --------------------------------------------------------------------------


def test_s1_single_lot_maps_the_16_column_contract() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    assert result.status == "ok"
    assert result.record_count == 1
    assert result.bbl == "1000010100"
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert set(by_field) <= ZTLDB_COLUMNS
    # Number-typed columns arrive as JSON strings and are normalized with
    # the verbatim original preserved.
    assert by_field["borough_code"]["original_value"] == "1"
    assert by_field["borough_code"]["normalized_value"] == 1
    assert by_field["tax_block"]["normalized_value"] == 1
    assert by_field["tax_lot"]["normalized_value"] == 100
    assert by_field["bbl"]["original_value"] == "1000010100"
    assert by_field["bbl"]["normalized_value"] == "1000010100"
    assert by_field["zoning_district_1"]["normalized_value"] == "R3-2"
    assert by_field["special_district_1"]["normalized_value"] == "GI"
    assert result.request_url == (
        f"{BASE_URL}?bbl=1000010100&%24order=bbl&%24limit={RECORD_QUERY_LIMIT}"
    )


def test_s1_every_fact_carries_required_source_fact_fields() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    required = (
        "provenance_id", "source_id", "original_field_name", "original_value",
        "normalized_value", "retrieved_at", "dataset_version",
        "effective_date", "bbl", "confidence", "user_confirmed_or_overridden",
        "conflict_status",
    )
    for fact in result.facts:
        for key in required:
            assert key in fact, f"{fact['original_field_name']} missing {key}"
        assert fact["source_id"] == SOURCE_ID
        assert fact["dataset_id"] == DATASET_ID
        # No per-record version column exists: the official rowsUpdatedAt
        # timestamp is the (non-empty string) dataset version signal.
        assert fact["dataset_version"] == "socrata-rows-2026-04-05T18:46:56Z"
        assert fact["effective_date"] is None
        assert fact["fact_key"] == (
            f"fact:{SOURCE_ID}:{DATASET_ID}:1000010100:"
            f"{fact['original_field_name']}"
        )
        assert fact["observation_id"].startswith("obs:")
        assert fact["source_rows_updated_at"] == "2026-04-05T18:46:56Z"


def test_s1_column_type_snapshot_matches_the_committed_metadata_fixture() -> None:
    # Transcription-drift guard: the embedded 16-column contract constant
    # must equal the columns array of the committed api/views capture.
    metadata = json.loads(
        load_fixture("ZT08_api_views_metadata.json")["response_body_raw"]
    )
    live = {
        column["fieldName"]: column["dataTypeName"]
        for column in metadata["columns"]
    }
    assert live == ZTLDB_COLUMN_TYPES
    assert len(ZTLDB_COLUMN_TYPES) == 16


def test_s1_two_records_for_one_bbl_is_typed_schema_drift() -> None:
    transport = FakeTransport(
        [fixture_response("ZT93_record_duplicate_bbl_synthetic.json")]
    )
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_by_bbl(
            "1000010100", freshness=make_freshness(), **run_kwargs(transport)
        )
    assert excinfo.value.detail["record_count"] == 2


# --------------------------------------------------------------------------
# ZT-S2 - split lot: official ordering preserved, never resorted
# --------------------------------------------------------------------------


def test_s2_split_lot_ordering_preserved() -> None:
    result = fetch_record("ZT02_record_split_lot.json", "1000010010")
    districts = result.zoning_assignment["zoning_districts"]
    assert [(d["position"], d["value"]) for d in districts] == [
        (1, "R3-2"), (2, "C4-1"),
    ]
    assert "greatest" in result.zoning_assignment["ordering_semantics"].lower()
    assert "2019-12-31" in result.zoning_assignment["ordering_semantics"]


def test_s2_ordering_is_never_resorted() -> None:
    # SYNTHETIC: values that would swap under any lexicographic resort must
    # keep the official column order (the order IS the semantics).
    def swap(record: dict) -> None:
        record["zoning_district_1"] = "C4-1"
        record["zoning_district_2"] = "R3-2"

    result = fetch_body(
        mutated_record_body("ZT02_record_split_lot.json", swap), "1000010010"
    )
    districts = result.zoning_assignment["zoning_districts"]
    assert [(d["position"], d["value"]) for d in districts] == [
        (1, "C4-1"), (2, "R3-2"),
    ]


# --------------------------------------------------------------------------
# ZT-S3 - no-record RESULT vs malformed-response ERROR
# --------------------------------------------------------------------------


def test_s3_valid_bbl_without_row_is_a_typed_no_record_result() -> None:
    result = fetch_record("ZT03_no_record_valid_bbl.json", "5999999999")
    assert result.status == "no_record"
    assert result.record_count == 0
    assert result.facts == []
    assert "no-record RESULT" in result.no_record_explanation
    # The empty official response is itself evidence: digests present.
    assert result.raw_digest and result.response_digest
    assert result.source_freshness is not None


def test_s3_non_array_body_is_typed_malformed_never_empty() -> None:
    transport = FakeTransport(
        [fixture_response("ZT94_malformed_not_array_synthetic.json")]
    )
    with pytest.raises(MalformedResponseError):
        fetch_by_bbl(
            "1000010100", freshness=make_freshness(), **run_kwargs(transport)
        )


def test_s3_truncated_body_is_typed_malformed_never_empty() -> None:
    transport = FakeTransport(
        [fixture_response("ZT95_malformed_truncated_synthetic.json")]
    )
    with pytest.raises(MalformedResponseError) as excinfo:
        fetch_by_bbl(
            "1000010100", freshness=make_freshness(), **run_kwargs(transport)
        )
    assert excinfo.value.error_type == "malformed_response"


# --------------------------------------------------------------------------
# ZT-S4 - presence-state separation: absent vs not-applicable vs observed
#         null (never a confirmed null/zero/false/empty)
# --------------------------------------------------------------------------


def test_s4_omitted_keys_map_to_documented_absence_classes() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    by_column = {entry["column"]: entry for entry in result.absences}
    # No fact exists for any absent column - absence is never a value.
    fact_columns = {fact["original_field_name"] for fact in result.facts}
    assert not (set(by_column) & fact_columns)
    # Documented blanks carry the official semantics.
    for column in set(by_column) & NOT_APPLICABLE_WHEN_ABSENT:
        assert by_column[column]["classification"] == (
            "not_applicable_per_source_semantics"
        )
        assert by_column[column]["semantics"]
    # zoning_map_code has no documented blank semantics: unknown, stated.
    assert by_column["zoning_map_code"]["classification"] == "absent_undocumented"
    # Every one of the 16 columns is either a fact or an absence entry.
    assert fact_columns | set(by_column) == ZTLDB_COLUMNS


def test_s4_observed_explicit_null_is_a_distinct_state() -> None:
    result = fetch_record(
        "ZT92_record_observed_null_synthetic.json", "1000010100"
    )
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    fact = by_field["commercial_overlay_1"]
    assert fact["original_value"] is None
    assert fact["normalized_value"] is None
    assert "observed_null:commercial_overlay_1" in result.observations
    # NOT classified as an absence: the key was present.
    assert all(
        entry["column"] != "commercial_overlay_1" for entry in result.absences
    )


def test_s4_absent_zoning_district_1_is_surfaced_never_guessed() -> None:
    # Live-observed state (fixture ZT07b contains such rows, e.g. BBL
    # 1000010201): a lot with NO zoning_district_1 key.
    def drop_zd1(record: dict) -> None:
        record.pop("zoning_district_1")

    result = fetch_body(
        mutated_record_body("ZT01_record_single_lot.json", drop_zd1),
        "1000010100",
    )
    assert "zoning_district_1_absent" in result.observations
    by_column = {entry["column"]: entry for entry in result.absences}
    assert by_column["zoning_district_1"]["classification"] == "absent_undocumented"
    assert result.zoning_assignment["zoning_districts"] == []


# --------------------------------------------------------------------------
# ZT-S5 - advisory vocabulary: Appendix C overlays, Appendix D limited
#         height (typed observation, never invention or rejection)
# --------------------------------------------------------------------------


def test_s5_overlay_within_appendix_c_yields_no_observation() -> None:
    result = fetch_record("ZT04_record_overlay_lot.json", "1001110100")
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["commercial_overlay_1"]["normalized_value"] == "C1-5"
    assert "C1-5" in APPENDIX_C_OVERLAYS
    assert not any(
        signal.startswith("outside_documented_vocabulary:commercial_overlay_1")
        for signal in result.observations
    )


def test_s5_limited_height_within_appendix_d_yields_no_observation() -> None:
    result = fetch_record(
        "ZT06_record_limited_height_lot.json", "1013760011"
    )
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["limited_height_district"]["normalized_value"] == "LH-1A"
    assert "LH-1A" in APPENDIX_D_LIMITED_HEIGHT
    assert not any(
        signal.startswith("outside_documented_vocabulary:limited_height_district")
        for signal in result.observations
    )


@pytest.mark.parametrize(
    ("column", "value"),
    [("commercial_overlay_1", "C9-9"), ("limited_height_district", "LH-9")],
)
def test_s5_outside_vocabulary_is_advisory_observation_never_invention(
    column, value
) -> None:
    def mutate(record: dict) -> None:
        record[column] = value

    result = fetch_body(
        mutated_record_body("ZT01_record_single_lot.json", mutate), "1000010100"
    )
    assert result.status == "ok"  # never rejected
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field[column]["normalized_value"] == value  # never coerced
    assert f"outside_documented_vocabulary:{column}:{value}" in result.observations


# --------------------------------------------------------------------------
# ZT-S6 - slash-tie special district
# --------------------------------------------------------------------------


def test_s6_slash_tie_parses_to_two_appendix_a_codes_with_tie_semantics() -> None:
    result = fetch_record("ZT90_record_slash_tie_synthetic.json", "1000010100")
    entries = result.zoning_assignment["special_districts"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["value"] == "GI/WP"  # verbatim representation preserved
    assert entry["components"] == ["GI", "WP"]
    assert entry["tie"] is True
    assert "same percentage" in entry["tie_semantics"]
    assert "special_district_tie:special_district_1:GI/WP" in result.observations
    # The verbatim fact is untouched by the parse.
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["special_district_1"]["normalized_value"] == "GI/WP"


def test_s6_single_special_district_is_not_a_tie() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    entry = result.zoning_assignment["special_districts"][0]
    assert entry == {
        "position": 1,
        "column": "special_district_1",
        "value": "GI",
        "components": ["GI"],
        "tie": False,
    }


# --------------------------------------------------------------------------
# ZT-S7 - PARK caveat
# --------------------------------------------------------------------------


def test_s7_park_carries_the_official_open_space_caveat() -> None:
    result = fetch_record("ZT05_record_park_lot.json", "1000030001")
    caveat = result.zoning_assignment["park_caveat"]
    assert caveat["applies"] is True
    assert caveat["caveat"] == PARK_CAVEAT
    assert "should not be used to calculate the amount of open space" in PARK_CAVEAT
    assert "park_caveat:do_not_use_for_open_space" in result.observations
    assert any(note.startswith("park_caveat:") for note in result.notes)


def test_s7_non_park_lot_does_not_flag_the_caveat() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    assert result.zoning_assignment["park_caveat"]["applies"] is False


# --------------------------------------------------------------------------
# ZT-S8 - open zoning_district_1 value set (research G1 C4)
# --------------------------------------------------------------------------


def test_s8_zr_section_number_zd1_is_accepted_as_open_set_observation() -> None:
    result = fetch_record("ZT91_record_open_zd1_synthetic.json", "1000010100")
    assert result.status == "ok"  # never rejected
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["zoning_district_1"]["normalized_value"] == "107-42"
    assert "open_set_vocabulary:zoning_district_1:107-42" in result.observations
    # An unknown vocabulary value is an OBSERVATION, not schema drift.
    assert not any(
        "zoning_district_1" in signal for signal in result.drift_signals
    )
    districts = result.zoning_assignment["zoning_districts"]
    assert districts[0]["value"] == "107-42"  # never coerced


# --------------------------------------------------------------------------
# ZT-S9 - pagination: deterministic order, pathologies, budgets
# --------------------------------------------------------------------------


def scan_script():
    return [
        fixture_response("ZT07a_page_offset0.json"),
        fixture_response("ZT07b_page_offset5.json"),
        TransportResponse(200, "[]"),
    ]


def test_s9_two_page_scan_has_no_dupes_or_gaps() -> None:
    transport = FakeTransport(scan_script())
    result = scan_rows(page_size=5, max_pages=5, **run_kwargs(transport))
    assert result.record_count == 10
    assert result.page_count == 3
    assert result.bbls == sorted(result.bbls)
    assert len(set(result.bbls)) == 10
    assert [call["url"] for call in transport.calls] == [
        f"{BASE_URL}?%24order=bbl&%24limit=5&%24offset=0",
        f"{BASE_URL}?%24order=bbl&%24limit=5&%24offset=5",
        f"{BASE_URL}?%24order=bbl&%24limit=5&%24offset=10",
    ]


def test_s9_duplicate_page_is_typed_pathology() -> None:
    transport = FakeTransport(
        [
            fixture_response("ZT07a_page_offset0.json"),
            fixture_response("ZT96_page_duplicate_synthetic.json"),
        ]
    )
    with pytest.raises(PagingPathologyError) as excinfo:
        scan_rows(page_size=5, max_pages=5, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] in ("duplicate_page", "no_progress")


def test_s9_no_progress_page_is_typed_pathology() -> None:
    transport = FakeTransport(
        [
            fixture_response("ZT07a_page_offset0.json"),
            fixture_response("ZT97_page_no_progress_synthetic.json"),
        ]
    )
    with pytest.raises(PagingPathologyError) as excinfo:
        scan_rows(page_size=5, max_pages=5, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] == "no_progress"


def test_s9_page_budget_exhaustion_is_typed_never_silent_truncation() -> None:
    transport = FakeTransport([fixture_response("ZT07a_page_offset0.json")])
    with pytest.raises(PagingPathologyError) as excinfo:
        scan_rows(page_size=5, max_pages=1, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] == "page_budget_exhausted"


def test_s9_page_overflow_is_typed_pathology() -> None:
    # Request 3 rows; the (real) page holds 5: an upstream ignoring $limit
    # would silently corrupt paging - typed failure instead.
    transport = FakeTransport([fixture_response("ZT07a_page_offset0.json")])
    with pytest.raises(PagingPathologyError) as excinfo:
        scan_rows(page_size=3, max_pages=5, **run_kwargs(transport))
    assert excinfo.value.detail["reason"] == "page_overflow"


def test_s9_request_budget_is_consumed_pre_io_and_typed() -> None:
    budget = AnalysisBudget(1, analysis_id="analysis-zt")
    transport = FakeTransport(scan_script())
    with pytest.raises(RequestBudgetExceededError):
        scan_rows(
            page_size=5, max_pages=5, budget=budget, **run_kwargs(transport)
        )
    assert len(transport.calls) == 1  # second request refused BEFORE I/O
    assert budget.consumed == 1


def test_s9_scan_bounds_are_enforced() -> None:
    transport = FakeTransport([])
    for bad_pages in (0, -1, HARD_MAX_PAGES + 1, True, "5", None):
        with pytest.raises(DisallowedRequestError):
            scan_rows(page_size=5, max_pages=bad_pages, **run_kwargs(transport))
    for bad_limit in (0, -1, 1001, True, "5"):
        with pytest.raises(DisallowedRequestError):
            build_page_url(bad_limit, 0)
    for bad_offset in (-1, 1_000_001, True, "0"):
        with pytest.raises(DisallowedRequestError):
            build_page_url(5, bad_offset)
    assert transport.calls == []


# --------------------------------------------------------------------------
# ZT-S10 - source freshness guard (owner two-staleness rule)
# --------------------------------------------------------------------------


def test_s10_old_source_with_fresh_retrieval_reports_source_age_not_staleness() -> None:
    result = fetch_record("ZT01_record_single_lot.json", "1000010100")
    freshness = result.source_freshness
    assert freshness["rows_updated_at"] == "2026-04-05T18:46:56Z"
    assert freshness["rows_updated_at_raw"] == 1775414816
    assert freshness["age_days"] == pytest.approx(105.72, abs=0.01)
    assert freshness["threshold_days"] == SOURCE_STALENESS_THRESHOLD_DAYS
    assert freshness["source_stale_suspected"] is True
    # THE owner rule: a fresh retrieval of an old dataset is NOT a stale
    # serve. staleness (transport) stays the fresh marker.
    assert result.staleness is None
    assert any(note.startswith("source_freshness:") for note in result.notes)


def test_s10_fresh_source_from_an_earlier_vantage_is_not_suspected() -> None:
    # SAME official metadata fixture, earlier injected clock: the age
    # computation is clock-driven, never wall-clock-dependent.
    result = fetch_record(
        "ZT01_record_single_lot.json", "1000010100", clock=APRIL_CLOCK
    )
    freshness = result.source_freshness
    assert freshness["age_days"] == pytest.approx(4.72, abs=0.01)
    assert freshness["source_stale_suspected"] is False
    assert result.staleness is None
    assert not any(note.startswith("source_freshness:") for note in result.notes)


def test_s10_missing_rows_updated_at_is_typed_schema_drift() -> None:
    transport = FakeTransport(
        [fixture_response("ZT99_meta_missing_rows_updated_synthetic.json")]
    )
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_source_freshness(**run_kwargs(transport))
    assert "rowsUpdatedAt" in excinfo.value.message


def test_s10_cache_hit_stamps_transport_staleness_without_touching_source() -> None:
    client, transport, clock = make_client(fresh_fetch_script())
    fresh = client("1000010100", "c1")
    assert fresh.staleness is None
    calls_after_fresh = len(transport.calls)
    clock.advance(50.0)  # within the 100s TTL
    cached = client("1000010100", "c2")
    assert len(transport.calls) == calls_after_fresh  # no upstream I/O
    assert cached.staleness == {
        "served_from_cache": True,
        "stale": False,
        "original_retrieved_at": fresh.retrieved_at,
        "age_seconds": 50.0,
    }
    # Source freshness and retrieval provenance are copied verbatim.
    assert cached.source_freshness == fresh.source_freshness
    assert cached.retrieved_at == fresh.retrieved_at
    assert cached.normalized_digest == fresh.normalized_digest


def test_s10_lkg_serve_stamps_stale_transport_and_preserves_source() -> None:
    script = fresh_fetch_script() + [TransportTimeout(), TransportTimeout()]
    client, _, clock = make_client(script)
    fresh = client("1000010100", "c1")
    clock.advance(200.0)  # beyond cache TTL, within LKG max age
    stale = client("1000010100", "c2")
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
    # source dataset is old; source freshness is untouched.
    assert stale.source_freshness == fresh.source_freshness
    assert stale.source_freshness["source_stale_suspected"] is True
    assert stale.retrieved_at == fresh.retrieved_at


def test_s10_regression_the_two_staleness_dimensions_vary_independently() -> None:
    """Owner-required regression: all four (source-age x transport-serve)
    combinations are observable and neither dimension ever writes the
    other's fields."""
    observed: list[tuple[bool, bool]] = []

    # 1. OLD source + FRESH transport (fixture ZT08 seen from 2026-07-20).
    old_fresh = fetch_record("ZT01_record_single_lot.json", "1000010100")
    assert old_fresh.source_freshness["source_stale_suspected"] is True
    assert old_fresh.staleness is None
    observed.append((True, False))

    # 2. FRESH source + FRESH transport (same fixture, April vantage).
    fresh_fresh = fetch_record(
        "ZT01_record_single_lot.json", "1000010100", clock=APRIL_CLOCK
    )
    assert fresh_fresh.source_freshness["source_stale_suspected"] is False
    assert fresh_fresh.staleness is None
    observed.append((False, False))

    # 3. OLD source + CACHED transport serve (not stale: upstream fine).
    client, _, clock = make_client(fresh_fetch_script())
    first = client("1000010100", "c1")
    clock.advance(10.0)
    cached = client("1000010100", "c2")
    assert cached.source_freshness["source_stale_suspected"] is True
    assert cached.staleness["served_from_cache"] is True
    assert cached.staleness["stale"] is False
    observed.append((True, True))

    # 4. OLD source + STALE transport serve (upstream failed; LKG).
    script = fresh_fetch_script() + [TransportTimeout(), TransportTimeout()]
    client2, _, clock2 = make_client(script)
    client2("1000010100", "c1")
    clock2.advance(150.0)
    lkg = client2("1000010100", "c2")
    assert lkg.source_freshness["source_stale_suspected"] is True
    assert lkg.staleness["stale"] is True
    observed.append((True, True))

    # The matrix shows both dimensions moving independently; and the fresh
    # transport results carried NO staleness object at all (the source age
    # can never masquerade as a cache/stale serve).
    assert (True, False) in observed and (False, False) in observed
    assert first.staleness is None


# --------------------------------------------------------------------------
# ZT-S11 - schema drift: columns snapshot, no-such-column 400, unknown keys
# --------------------------------------------------------------------------


def test_s11_columns_diff_detects_rename_as_removed_plus_added() -> None:
    metadata = json.loads(
        load_fixture("ZT102_meta_renamed_column_synthetic.json")["response_body_raw"]
    )
    diff = check_columns_for_drift(metadata)
    assert diff["removed"] == ["zoning_district_1"]
    assert diff["added"] == ["zoning_district_1_renamed"]
    assert diff["type_changed"] == []


def test_s11_freshness_fails_typed_on_removed_or_retyped_column() -> None:
    transport = FakeTransport(
        [fixture_response("ZT102_meta_renamed_column_synthetic.json")]
    )
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_source_freshness(**run_kwargs(transport))
    assert excinfo.value.detail["removed"] == ["zoning_district_1"]

    metadata = json.loads(
        load_fixture("ZT08_api_views_metadata.json")["response_body_raw"]
    )
    for column in metadata["columns"]:
        if column["fieldName"] == "bbl":
            column["dataTypeName"] = "text"  # SYNTHETIC retype
    transport = FakeTransport([TransportResponse(200, json.dumps(metadata))])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_source_freshness(**run_kwargs(transport))
    assert excinfo.value.detail["type_changed"] == ["bbl"]


def test_s11_added_column_is_visible_typed_degradation() -> None:
    metadata = json.loads(
        load_fixture("ZT08_api_views_metadata.json")["response_body_raw"]
    )
    metadata["columns"].append(
        {"fieldName": "new_unexpected", "dataTypeName": "text"}  # SYNTHETIC
    )
    transport = FakeTransport(
        [
            TransportResponse(200, json.dumps(metadata)),
            fixture_response("ZT01_record_single_lot.json"),
        ]
    )
    result = fetch_by_bbl("1000010100", **run_kwargs(transport))
    assert "added_column:new_unexpected" in result.drift_signals


def test_s11_no_such_column_400_is_the_drift_signature() -> None:
    # Replays the LIVE-captured 400 body (fixture ZT10) on the record path.
    transport = FakeTransport([fixture_response("ZT10_no_such_column_400.json")])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_by_bbl(
            "1000010100", freshness=make_freshness(), **run_kwargs(transport)
        )
    assert excinfo.value.detail["error_code"] == "query.soql.no-such-column"
    assert excinfo.value.detail["http_status"] == 400


def test_s11_other_400_is_upstream_error_not_drift() -> None:
    transport = FakeTransport(
        [fixture_response("ZT100_type_mismatch_400_synthetic.json")]
    )
    with pytest.raises(UpstreamError) as excinfo:
        fetch_by_bbl(
            "1000010100", freshness=make_freshness(), **run_kwargs(transport)
        )
    assert excinfo.value.error_type == "upstream_error"
    assert excinfo.value.detail["error_code"] == "query.soql.type-mismatch"


def test_s11_unknown_record_key_yields_signal_and_no_fact() -> None:
    result = fetch_record(
        "ZT101_record_unknown_column_synthetic.json", "1000010100"
    )
    assert "unknown_column:mystery_column" in result.drift_signals
    assert all(
        fact["original_field_name"] != "mystery_column" for fact in result.facts
    )


def test_s11_record_bbl_mismatch_is_typed_drift() -> None:
    def wrong_bbl(record: dict) -> None:
        record["bbl"] = "3158287501"

    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_body(
            mutated_record_body("ZT01_record_single_lot.json", wrong_bbl),
            "1000010100",
        )
    assert excinfo.value.detail["record_bbl"] == "3158287501"


def test_s11_identifier_inconsistency_is_a_visible_conflict_not_a_fix() -> None:
    def wrong_borough(record: dict) -> None:
        record["borough_code"] = "3"  # disagrees with the Manhattan BBL

    result = fetch_body(
        mutated_record_body("ZT01_record_single_lot.json", wrong_borough),
        "1000010100",
    )
    assert result.conflicts
    conflict = result.conflicts[0]
    assert conflict["field"] == "borough_code"
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["borough_code"]["conflict_status"] == "conflicting"
    assert by_field["bbl"]["conflict_status"] == "conflicting"
    # The verbatim disagreeing value is preserved, never corrected.
    assert by_field["borough_code"]["original_value"] == "3"


# --------------------------------------------------------------------------
# ZT-S12 - resilience: 429, timeout, circuit, budget - all distinguishable
# --------------------------------------------------------------------------


def test_s12_429_persisted_is_typed_rate_limited() -> None:
    transport = FakeTransport(
        [fixture_response("ZT98_rate_limited_429_synthetic.json")] * 2
    )
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_source_freshness(**run_kwargs(transport, max_attempts=2))
    assert excinfo.value.error_type == "rate_limited"
    assert len(transport.calls) == 2


def test_s12_retry_after_honored_exactly_then_success() -> None:
    transport = FakeTransport(
        [
            TransportResponse(429, "", headers={"retry-after": "7"}),
            fixture_response("ZT08_api_views_metadata.json"),
        ]
    )
    sleeps = SleepRecorder()
    freshness = fetch_source_freshness(
        **run_kwargs(transport, sleep=sleeps, max_attempts=2)
    )
    assert freshness.rows_updated_at == "2026-04-05T18:46:56Z"
    assert sleeps.delays == [7.0]  # honored EXACTLY, no jitter


def test_s12_retry_after_beyond_cap_fails_typed_without_blocking() -> None:
    transport = FakeTransport(
        [TransportResponse(429, "", headers={"retry-after": "999"})]
    )
    sleeps = SleepRecorder()
    with pytest.raises(RateLimitedError):
        fetch_source_freshness(
            **run_kwargs(
                transport, sleep=sleeps, max_attempts=3, retry_after_cap=120.0
            )
        )
    assert sleeps.delays == []  # never blocked a thread for minutes
    assert len(transport.calls) == 1


def test_s12_timeout_persisted_is_typed() -> None:
    transport = FakeTransport([TransportTimeout()] * 3)
    sleeps = SleepRecorder()
    with pytest.raises(SourceTimeoutError):
        fetch_source_freshness(
            **run_kwargs(transport, sleep=sleeps, max_attempts=3)
        )
    assert len(transport.calls) == 3
    assert len(sleeps.delays) == 2  # jittered backoff between attempts


def test_s12_network_failure_persisted_is_typed_upstream() -> None:
    transport = FakeTransport([TransportFailure("network failure: gaierror")] * 2)
    with pytest.raises(UpstreamError) as excinfo:
        fetch_source_freshness(**run_kwargs(transport, max_attempts=2))
    assert excinfo.value.detail["reason_kind"] == "network"


def test_s12_circuit_open_is_typed_and_makes_no_upstream_call() -> None:
    client, transport, _ = make_client([TransportTimeout(), TransportTimeout()])
    with pytest.raises(SourceTimeoutError):
        client("1000010100", "c1")
    calls_after_first = len(transport.calls)
    with pytest.raises(CircuitOpenError) as excinfo:
        client("1000010100", "c2")
    assert excinfo.value.error_type == "circuit_open"
    assert len(transport.calls) == calls_after_first  # zero upstream I/O
    assert client.metrics.count("breaker_fast_reject") == 1


def test_s12_budget_exhaustion_is_never_masked_by_lkg() -> None:
    client, transport, clock = make_client(fresh_fetch_script())
    client("1000010100", "c1")  # populates LKG
    clock.advance(150.0)  # cache expired
    budget = AnalysisBudget(0, analysis_id="analysis-zt")
    with pytest.raises(RequestBudgetExceededError):
        client("1000010100", "c2", budget=budget)


def test_s12_error_taxonomy_states_are_distinguishable() -> None:
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
    assert len(set(taxonomy.values())) == len(taxonomy)
    for cls, error_type in taxonomy.items():
        exc = cls("m", correlation_id="c")
        assert exc.error_type == error_type
        assert isinstance(exc, ZtldbConnectorError)
        payload = exc.to_payload()
        assert payload["error_type"] == error_type
        assert payload["source_id"] == SOURCE_ID
    # no_record is a RESULT status, deliberately NOT an error class.
    result = fetch_record("ZT03_no_record_valid_bbl.json", "5999999999")
    assert result.status == "no_record"


# --------------------------------------------------------------------------
# ZT-S15 - determinism: separate raw/response/normalized digests
# --------------------------------------------------------------------------


def test_s15_digests_reproduce_across_runs_and_match_the_anchor() -> None:
    results = [
        fetch_record("ZT01_record_single_lot.json", "1000010100")
        for _ in range(2)
    ]
    first, second = results
    assert first.raw_digest == second.raw_digest
    assert first.response_digest == second.response_digest
    assert first.normalized_digest == second.normalized_digest
    # Cross-platform anchor: CI on another OS must reproduce this exact
    # value from the committed fixture.
    assert first.normalized_digest == ZT01_NORMALIZED_DIGEST
    assert first.digest_canonicalization == ZT_CANONICALIZATION_SPEC


def test_s15_normalized_digest_is_independent_of_serialization_order() -> None:
    """Shuffled-fixture proof: same record content with reordered keys and
    different whitespace produces the SAME response/normalized digests but
    a DIFFERENT raw digest (raw pins bytes; normalized pins content)."""
    body = load_fixture("ZT01_record_single_lot.json")["response_body_raw"]
    record = json.loads(body)[0]
    reordered = {key: record[key] for key in sorted(record, reverse=True)}
    assert list(reordered) != list(record)
    shuffled_body = json.dumps([reordered], indent=2)
    original = fetch_body(body, "1000010100")
    shuffled = fetch_body(shuffled_body, "1000010100")
    assert original.raw_digest != shuffled.raw_digest
    assert original.response_digest == shuffled.response_digest
    assert original.normalized_digest == shuffled.normalized_digest


def test_s15_any_value_change_flips_the_normalized_digest() -> None:
    def change(record: dict) -> None:
        record["zoning_district_1"] = "R4"

    base = fetch_record("ZT01_record_single_lot.json", "1000010100")
    changed = fetch_body(
        mutated_record_body("ZT01_record_single_lot.json", change), "1000010100"
    )
    assert base.normalized_digest != changed.normalized_digest
    assert base.response_digest != changed.response_digest


def test_s15_manifest_digests_match_committed_fixture_bytes() -> None:
    manifest = json.loads(
        (FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8")
    )
    by_file = {entry["file"]: entry for entry in manifest["fixtures"]}
    fixture_files = sorted(p.name for p in FIXTURE_DIR.glob("ZT*.json"))
    assert fixture_files == sorted(by_file)
    assert manifest["task"] == "M2-T008"
    for name in fixture_files:
        entry = by_file[name]
        body = load_fixture(name)["response_body_raw"]
        digest = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        assert entry["response_body_sha256"] == digest, name
        assert entry["classification"] in ("raw", "synthetic")
        if entry["classification"] == "synthetic":
            assert entry["derived_from"], name  # lineage mandatory
        assert entry["retrieval_timestamp_utc"], name
        assert entry["official_endpoint"].startswith(
            "https://data.cityofnewyork.us/"
        ), name
        assert entry["supports_scenarios"], name


# --------------------------------------------------------------------------
# ZT-S16 - query safety: validation before construction, pinned origin,
#          secret discipline
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_bbl",
    [
        "1' OR '1'='1",
        "1000010100&$where=1=1",
        "1000010100;DROP",
        "abc",
        "10000101001",
        "",
        None,
        True,
        -1000010100,
        "0000010100",
    ],
)
def test_s16_injection_shaped_bbl_rejected_before_any_network(bad_bbl) -> None:
    transport = FakeTransport([])
    with pytest.raises(BBLValidationError):
        fetch_by_bbl(bad_bbl, freshness=make_freshness(), **run_kwargs(transport))
    with pytest.raises(BBLValidationError):
        build_record_url(bad_bbl)
    assert transport.calls == []


def test_s16_resilient_fetcher_validates_before_cache_and_network() -> None:
    client, transport, _ = make_client([])
    with pytest.raises(BBLValidationError):
        client("1000010100'; DROP TABLE lots; --", "c1")
    assert transport.calls == []


def test_s16_every_built_url_targets_the_pinned_official_dataset() -> None:
    assert build_record_url("1000010100").startswith(
        f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json?"
    )
    assert build_page_url(5, 0).startswith(
        f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json?"
    )
    assert API_VIEWS_URL == (
        f"https://data.cityofnewyork.us/api/views/{DATASET_ID}.json"
    )
    # The canonical BBL digits are the ONLY caller input in the URL.
    assert build_record_url(" 1000010100 ") == build_record_url("1000010100")


def test_s16_app_token_is_header_only_and_never_logged_or_leaked(caplog) -> None:
    token = "in-test-credential-value"  # secretscan:allow fake token for leak-absence test
    transport = FakeTransport(fresh_fetch_script())
    with caplog.at_level(logging.DEBUG, logger="app.connectors.ztldb_soda"):
        result = fetch_by_bbl(
            "1000010100", **run_kwargs(transport, app_token=token)
        )
    assert result.status == "ok"
    # Sent as a header on every request...
    for call in transport.calls:
        assert call["headers"]["X-App-Token"] == token
        assert token not in call["url"]
    # ...but never logged and never in any payload or result field.
    assert token not in caplog.text
    dumped = json.dumps(
        {
            "facts": result.facts,
            "freshness": result.source_freshness,
            "notes": result.notes,
            "request_url": result.request_url,
        }
    )
    assert token not in dumped


def test_s16_app_token_absent_from_typed_error_payloads() -> None:
    token = "in-test-credential-value"  # secretscan:allow fake token for leak-absence test
    transport = FakeTransport(
        [fixture_response("ZT98_rate_limited_429_synthetic.json")] * 2
    )
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_source_freshness(
            **run_kwargs(transport, app_token=token, max_attempts=2)
        )
    assert token not in json.dumps(excinfo.value.to_payload())


def test_s16_fixture_pack_contains_no_credential_material() -> None:
    # M2-T007 G5 O4 carry-forward: WIDER secret-scan needle set.
    needles = (
        "token", "apikey", "api_key", "authorization", "bearer",
        "password", "secret",
    )
    for path in sorted(FIXTURE_DIR.glob("*.json")) + [
        FIXTURE_DIR / "MANIFEST.json"
    ]:
        text = path.read_text(encoding="utf-8").lower()
        for needle in needles:
            assert needle not in text, f"{path.name} contains {needle!r}"


def test_s16_requests_without_token_carry_only_the_accept_header() -> None:
    transport = FakeTransport(fresh_fetch_script())
    fetch_by_bbl("1000010100", **run_kwargs(transport))
    for call in transport.calls:
        assert call["headers"] == {"Accept": "application/json"}


# --------------------------------------------------------------------------
# Regression guards (ZT-S17 full-suite greenness is proven by the recorded
# pytest run; these assert non-interference)
# --------------------------------------------------------------------------


def test_regression_no_pluto_module_state_is_modified() -> None:
    import app.connectors.pluto_soda as pluto

    assert pluto.SOURCE_ID == "nyc-dcp-pluto-soda"
    assert pluto.DATASET_ID == "64uk-42ks"
    assert SOURCE_ID == "nyc-dcp-ztldb-soda"
    assert DATASET_ID == "fdkv-4t4z"
    assert SOURCE_ID != pluto.SOURCE_ID


def test_regression_correlation_id_minted_when_absent() -> None:
    transport = FakeTransport(fresh_fetch_script())
    result = fetch_by_bbl(
        "1000010100",
        transport=transport,
        sleep=SleepRecorder(),
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )
    assert result.correlation_id
    assert len(result.correlation_id) == 32
