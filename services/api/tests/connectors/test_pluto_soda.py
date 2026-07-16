"""PLUTO SODA connector tests (task M1-T002, scenarios S1-S7).

Offline, fixture-driven, deterministic: every HTTP interaction is replayed
from the live-captured fixture pack in services/api/tests/fixtures/pluto/
through an injected fake transport. No test touches the network.

Where a test needs a record variant the official API cannot politely provide
on demand (e.g. numfloors omitted with numbldgs > 0, or a conflicting
borocode), the test derives a clearly-labeled SYNTHETIC variant from a real
fixture record inside the test body. Synthetic variants exercise connector
logic only and are never presented as official data.
"""

import io
import json
import logging
import re
import socket
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors import pluto_soda
from app.connectors.bbl import BBLValidationError
from app.connectors.pluto_soda import (
    BASE_URL,
    DATASET_ID,
    PLUTO_COLUMN_TYPES,
    PLUTO_COLUMNS,
    SOURCE_ID,
    VERSION_RE,
    VINTAGE_DATE_COLUMNS,
    PlutoConnectorError,
    RateLimitedError,
    SchemaDriftError,
    SourceTimeoutError,
    SourceUnavailableError,
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    build_page_url,
    check_columns_for_drift,
    fetch_by_bbl,
    urllib_transport,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


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


@pytest.fixture(scope="module")
def source_fact_validator():
    """jsonschema validator for source_fact.schema.json v1 with common.schema
    resolved, mirroring .github/scripts/validate_contracts.py."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((SCHEMA_DIR / "source_fact.schema.json").read_text(encoding="utf-8"))
    common = json.loads((SCHEMA_DIR / "common.schema.json").read_text(encoding="utf-8"))
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in (schema, common)]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in (schema, common)},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


def fetch_fixture(name: str, bbl: str, **kwargs):
    transport = FakeTransport([fixture_response(name)])
    result = fetch_by_bbl(
        bbl, transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK, **kwargs
    )
    return result, transport


# --------------------------------------------------------------------------
# S1 - normal: single-lot record, facts validate against source_fact v1
# --------------------------------------------------------------------------


def test_s1_normal_fetch_returns_one_canonical_record() -> None:
    result, transport = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    assert result.status == "ok"
    assert result.record_count == 1
    assert result.bbl == "1000010100"
    assert result.dataset_version == "26v1"
    assert result.request_url.endswith("?bbl=1000010100")
    assert transport.calls[0]["url"] == result.request_url
    assert result.facts  # non-empty
    assert result.drift_signals == []  # all record keys are known 26v1 columns


def test_s1_every_fact_validates_against_source_fact_v1(source_fact_validator) -> None:
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    for fact in result.facts:
        errors = list(source_fact_validator.iter_errors(fact))
        assert errors == [], f"{fact['original_field_name']}: {[e.message for e in errors]}"


def test_s1_provenance_fields_on_a_concrete_fact() -> None:
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    lotarea = by_field["lotarea"]
    assert lotarea["source_id"] == SOURCE_ID
    assert lotarea["dataset_id"] == DATASET_ID
    assert lotarea["request_url"] == result.request_url
    assert lotarea["original_value"] == "23121"  # verbatim (F1 capture)
    assert lotarea["normalized_value"] == 23121
    assert lotarea["units"] == "square feet"  # dictionary p.21
    assert lotarea["dataset_version"] == "26v1"
    assert lotarea["retrieved_at"] == "2026-07-16T12:00:00Z"
    assert lotarea["bbl"] == "1000010100"
    assert lotarea["confidence"] == 1.0
    assert lotarea["conflict_status"] == "none"
    # FAR columns arrive as informational facts (never rule outputs).
    assert by_field["residfar"]["normalized_value"] == 0.75
    assert by_field["residfar"]["units"] is None
    # Booleans (Socrata checkbox) survive verbatim.
    assert by_field["splitzone"]["original_value"] is False
    assert by_field["splitzone"]["normalized_value"] is False
    # calendar_date normalizes to the date part only.
    assert by_field["appdate"]["original_value"] == "2026-03-16T00:00:00.000"
    assert by_field["appdate"]["normalized_value"] == "2026-03-16"


# --------------------------------------------------------------------------
# S2 - boundary: decimal serialization, component limits, condo semantics
# --------------------------------------------------------------------------


def test_s2a_record_bbl_decimal_serialization_normalized_with_raw_preserved() -> None:
    # F1 full record serializes bbl as "1000010100.00000000" (F12 hazard).
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    bbl_fact = next(f for f in result.facts if f["original_field_name"] == "bbl")
    assert bbl_fact["original_value"] == "1000010100.00000000"
    assert bbl_fact["normalized_value"] == "1000010100"
    appbbl_fact = next(f for f in result.facts if f["original_field_name"] == "appbbl")
    assert appbbl_fact["original_value"] == "1000010010.00000000"
    assert appbbl_fact["normalized_value"] == "1000010010"


def test_s2c_condo_billing_lot_returns_complex_record() -> None:
    result, _ = fetch_fixture("F02a_condo_billing_lot.json", "1000047501")
    assert result.status == "ok"
    assert result.bbl == "1000047501"
    condono = next(f for f in result.facts if f["original_field_name"] == "condono")
    assert condono["original_value"] == "835"  # complex record carries condono
    assert condono["normalized_value"] == 835


def test_s2c_condo_unit_lot_is_no_match_with_condo_explanation() -> None:
    result, _ = fetch_fixture("F02b_condo_unit_lot_no_match.json", "1000041001")
    assert result.status == "no_match"
    assert result.facts == []
    assert result.no_match_explanation is not None
    assert "billing" in result.no_match_explanation.lower()
    assert "condominium" in result.no_match_explanation.lower()


# --------------------------------------------------------------------------
# S3 - missing/null: no_match, null-field omission, numfloors rule
# --------------------------------------------------------------------------


def test_s3a_valid_nonexistent_bbl_is_explicit_no_match_not_error() -> None:
    result, _ = fetch_fixture("F03b_no_match_valid_bbl.json", "5999999999")
    assert result.status == "no_match"
    assert result.record_count == 0
    assert result.facts == []  # never an invented record
    assert result.no_match_explanation
    assert result.dataset_version is None  # nothing fabricated


def test_s3a_packet_bbl_9999999999_is_rejected_before_any_network_call() -> None:
    # 9999999999 violates the accepted canonical pattern ^[1-5][0-9]{9}$
    # (common.schema.json), so validation fires client-side; the raw API's []
    # behavior for it is documented in fixture F03.
    transport = FakeTransport([])
    with pytest.raises(BBLValidationError) as excinfo:
        fetch_by_bbl("9999999999", transport=transport, sleep=SleepRecorder())
    assert excinfo.value.code == "invalid_borough"
    assert transport.calls == []  # no network call was made


def test_s3b_null_field_omission_yields_absent_columns_never_fabrication() -> None:
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    emitted = {fact["original_field_name"] for fact in result.facts}
    # Facts exist ONLY for keys present on the record.
    assert emitted <= PLUTO_COLUMNS
    # Known 26v1 columns omitted on this record surface as absent/unknown.
    for expected_absent in ("zonedist2", "overlay1", "landmark", "numfloors"):
        assert expected_absent in result.absent_columns
        assert expected_absent not in emitted
    assert set(result.absent_columns) == PLUTO_COLUMNS - emitted


def test_s3b_f04_fixture_record_keys_are_subset_of_inventory() -> None:
    fixture = load_fixture("F04_null_field_omission.json")
    record = json.loads(fixture["response_body_raw"])[0]
    assert set(record) <= PLUTO_COLUMNS


def test_s3c_numfloors_absent_with_buildings_is_flagged_not_available() -> None:
    # The REAL F04 record (BBL 1000010101) has numfloors omitted while
    # numbldgs=10 - exactly the dictionary p.28 "not available" case.
    result, _ = fetch_fixture("F04_null_field_omission.json", "1000010101")
    assert any("numfloors_not_available" in note for note in result.notes)
    assert not any(f["original_field_name"] == "numfloors" for f in result.facts)
    numbldgs = next(f for f in result.facts if f["original_field_name"] == "numbldgs")
    assert numbldgs["normalized_value"] == 10


# --------------------------------------------------------------------------
# S4 - ambiguous/conflicting: malformed inputs, identifier conflicts
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_input",
    ["100001010", "10000101001", "6000010100", "not-a-bbl", "-1000010100", "1000010100.5"],
)
def test_s4a_malformed_bbl_rejected_typed_with_no_network_call(bad_input) -> None:
    transport = FakeTransport([])
    with pytest.raises(BBLValidationError):
        fetch_by_bbl(bad_input, transport=transport, sleep=SleepRecorder())
    assert transport.calls == []


def test_s4b_identifier_conflict_flagged_never_silently_resolved() -> None:
    # SYNTHETIC variant of the real F1 record: borocode contradicts the bbl.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["borocode"] = "2"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict["field"] == "borocode"
    assert conflict["bbl_derived_value"] == 1
    assert conflict["component_value_raw"] == "2"
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    # Provenance-level conflict flags on the identifier facts...
    assert by_field["bbl"]["conflict_status"] == "conflicting"
    assert by_field["borocode"]["conflict_status"] == "conflicting"
    # ...and the conflicting value is still emitted verbatim, not corrected.
    assert by_field["borocode"]["original_value"] == "2"
    # Unrelated facts stay unflagged.
    assert by_field["lotarea"]["conflict_status"] == "none"


# --------------------------------------------------------------------------
# S5 - failure: 429, schema drift, timeout, network down, 5xx
# --------------------------------------------------------------------------


def test_s5a_429_bounded_retry_with_backoff_then_typed_rate_limited() -> None:
    throttle = fixture_response("F07_rate_limit_429_synthetic.json")
    transport = FakeTransport([throttle, throttle, throttle])
    sleeper = SleepRecorder()
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_by_bbl(
            "1000010100", transport=transport, sleep=sleeper,
            max_attempts=3, backoff_base=0.5,
        )
    assert len(transport.calls) == 3  # bounded, not infinite
    assert sleeper.delays == [0.5, 1.0]  # exponential backoff between attempts
    payload = excinfo.value.to_payload()
    assert payload["error_type"] == "rate_limited"
    assert payload["detail"]["max_attempts"] == 3


def test_s5a_429_then_success_recovers() -> None:
    transport = FakeTransport(
        [fixture_response("F07_rate_limit_429_synthetic.json"),
         fixture_response("F01_single_lot_normal.json")]
    )
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert result.status == "ok"
    assert len(transport.calls) == 2


def test_s5b_no_such_column_400_is_schema_drift_and_never_retried() -> None:
    transport = FakeTransport([fixture_response("F13_schema_drift_no_such_column_400.json")])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())
    assert len(transport.calls) == 1  # never blindly retried
    payload = excinfo.value.to_payload()
    assert payload["error_type"] == "schema_drift"
    assert payload["detail"]["error_code"] == "query.soql.no-such-column"


def test_s5b_other_400_is_distinct_from_schema_drift() -> None:
    transport = FakeTransport([fixture_response("F13b_non_drift_400_type_mismatch.json")])
    with pytest.raises(SourceUnavailableError) as excinfo:
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())
    assert len(transport.calls) == 1
    payload = excinfo.value.to_payload()
    assert payload["error_type"] == "source_unavailable"
    assert payload["detail"]["error_code"] == "query.soql.type-mismatch"


def test_s5c_timeout_bounded_retry_then_typed_timeout_error() -> None:
    transport = FakeTransport(
        [TransportTimeout("t"), TransportTimeout("t"), TransportTimeout("t")]
    )
    with pytest.raises(SourceTimeoutError) as excinfo:
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())
    assert len(transport.calls) == 3
    assert excinfo.value.to_payload()["error_type"] == "timeout"


def test_s5d_network_unavailable_is_typed_source_unavailable() -> None:
    transport = FakeTransport(
        [TransportFailure("network failure: gaierror")] * 3
    )
    with pytest.raises(SourceUnavailableError) as excinfo:
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())
    assert excinfo.value.to_payload()["error_type"] == "source_unavailable"


def test_s5e_5xx_bounded_retry_then_recovery_on_second_attempt() -> None:
    transport = FakeTransport(
        [TransportResponse(503, "Service Unavailable"),
         fixture_response("F01_single_lot_normal.json")]
    )
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert result.status == "ok"
    assert len(transport.calls) == 2


def test_s5_no_partial_facts_on_failure() -> None:
    # A failure raises; there is no result object and therefore no fact list.
    transport = FakeTransport([TransportResponse(500, "boom")] * 3)
    with pytest.raises(SourceUnavailableError):
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())


def test_s5_error_payloads_never_contain_token_or_stack_trace(
    monkeypatch, caplog
) -> None:
    token = "secret-token-value-12345"  # secretscan:allow fake token for leak-absence test
    monkeypatch.setenv("SOCRATA_APP_TOKEN", token)
    transport = FakeTransport([TransportResponse(500, "boom")] * 3)
    with caplog.at_level(logging.DEBUG, logger="app.connectors.pluto_soda"):
        with pytest.raises(SourceUnavailableError) as excinfo:
            fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())
    # Token was sent as the X-App-Token header...
    assert transport.calls[0]["headers"]["X-App-Token"] == token
    # ...but appears nowhere in the error payload or the logs.
    serialized = json.dumps(excinfo.value.to_payload())
    assert token not in serialized
    assert "Traceback" not in serialized
    assert token not in caplog.text
    # And the URL never carries the token (header-only, per E7).
    assert token not in transport.calls[0]["url"]


def test_s5_tokenless_operation_sends_no_token_header(monkeypatch) -> None:
    monkeypatch.delenv("SOCRATA_APP_TOKEN", raising=False)
    result, transport = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    assert result.status == "ok"
    assert "X-App-Token" not in transport.calls[0]["headers"]


def test_s5_malformed_json_200_is_source_unavailable() -> None:
    transport = FakeTransport([TransportResponse(200, "<html>not json</html>")])
    with pytest.raises(SourceUnavailableError):
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())


def test_s5_non_array_json_200_is_schema_drift() -> None:
    transport = FakeTransport([TransportResponse(200, '{"unexpected": "object"}')])
    with pytest.raises(SchemaDriftError):
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())


def test_s5_multiple_records_for_one_bbl_is_schema_drift() -> None:
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    transport = FakeTransport([TransportResponse(200, json.dumps([record, record]))])
    with pytest.raises(SchemaDriftError):
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())


# --------------------------------------------------------------------------
# S6 - retry/idempotency: identical canonical output for identical input
# --------------------------------------------------------------------------


def test_s6_same_input_twice_yields_identical_canonical_output() -> None:
    first, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    second, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    # With a fixed clock the outputs are exactly equal apart from the
    # correlation id (unique per request by design).
    assert first.facts == second.facts
    assert first.bbl == second.bbl
    assert first.dataset_version == second.dataset_version
    assert first.absent_columns == second.absent_columns
    # Fact ordering is stable (sorted by field name).
    fields = [fact["original_field_name"] for fact in first.facts]
    assert fields == sorted(fields)
    # Provenance ids are deterministic keys and unique within the result.
    ids = [fact["provenance_id"] for fact in first.facts]
    assert len(ids) == len(set(ids))
    assert ids == [fact["provenance_id"] for fact in second.facts]


def test_s6_retry_after_transient_failure_produces_same_facts() -> None:
    clean, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    transport = FakeTransport(
        [TransportResponse(503, "unavailable"),
         fixture_response("F01_single_lot_normal.json")]
    )
    retried = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert retried.facts == clean.facts  # no duplicate or divergent facts


# --------------------------------------------------------------------------
# S7 - provenance completeness
# --------------------------------------------------------------------------


def test_s7_no_normalized_value_without_full_provenance() -> None:
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    required = {
        "provenance_id", "source_id", "original_field_name", "original_value",
        "normalized_value", "retrieved_at", "dataset_version", "effective_date",
        "bbl", "confidence", "user_confirmed_or_overridden", "conflict_status",
        "dataset_id", "request_url", "input_vintages",
    }
    for fact in result.facts:
        assert required <= set(fact), fact["original_field_name"]
        assert VERSION_RE.match(fact["dataset_version"])


def test_s7_version_regex_enforced_f9() -> None:
    fixture = load_fixture("F09_version_select.json")
    version = json.loads(fixture["response_body_raw"])[0]["version"]
    assert VERSION_RE.match(version)
    assert version == "26v1"


def test_s7_malformed_version_is_schema_drift() -> None:
    # SYNTHETIC variant: version mangled to a non-release string.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["version"] = "v26-nonsense"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    with pytest.raises(SchemaDriftError):
        fetch_by_bbl("1000010100", transport=transport, sleep=SleepRecorder())


def test_s7_vintage_columns_absent_on_f1_record_yields_empty_vintages() -> None:
    # F01v proves all eight vintage columns are NULL for this record (SODA
    # omits them even under $select) - so input_vintages must be empty, never
    # fabricated.
    fixture = load_fixture("F01v_vintage_columns_projection.json")
    projected = json.loads(fixture["response_body_raw"])[0]
    assert set(projected) == {"bbl"}  # only bbl came back
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    for fact in result.facts:
        assert fact["input_vintages"] == {}


def test_s7_vintage_columns_captured_when_present() -> None:
    # SYNTHETIC variant: vintage dates added to a real record to prove the
    # capture path (no live-captured record carried them; see F01v).
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["zoningdate"] = "2026-03-31"
    record["rpaddate"] = "2026-03-30"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    for fact in result.facts:
        assert fact["input_vintages"] == {
            "rpaddate": "2026-03-30", "zoningdate": "2026-03-31"
        }


def test_s7_unknown_column_yields_drift_signal_and_no_fact() -> None:
    # SYNTHETIC variant: a column not in the 108-column inventory appears.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["brand_new_column"] = "surprise"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert "unknown_column:brand_new_column" in result.drift_signals
    assert not any(
        fact["original_field_name"] == "brand_new_column" for fact in result.facts
    )


# --------------------------------------------------------------------------
# Contract snapshot / drift check (F8) and supporting fixtures (F5, F6, F10, F14)
# --------------------------------------------------------------------------


def test_f8_embedded_inventory_matches_api_views_snapshot() -> None:
    fixture = load_fixture("F08_api_views_columns_snapshot.json")
    metadata = json.loads(fixture["response_body_raw"])
    live_types = {c["fieldName"]: c["dataTypeName"] for c in metadata["columns"]}
    assert live_types == PLUTO_COLUMN_TYPES  # transcription drift fails here
    assert len(PLUTO_COLUMNS) == 108
    report = check_columns_for_drift(metadata)
    assert report == {"added": [], "removed": [], "type_changed": []}


def test_f8_drift_check_detects_added_removed_and_type_changes() -> None:
    fixture = load_fixture("F08_api_views_columns_snapshot.json")
    metadata = json.loads(fixture["response_body_raw"])
    metadata["columns"] = [
        c for c in metadata["columns"] if c["fieldName"] != "lotarea"
    ] + [{"fieldName": "new_col", "dataTypeName": "text"}]
    for column in metadata["columns"]:
        if column["fieldName"] == "numfloors":
            column["dataTypeName"] = "text"
    report = check_columns_for_drift(metadata)
    assert report["added"] == ["new_col"]
    assert report["removed"] == ["lotarea"]
    assert report["type_changed"] == ["numfloors"]


def test_f5_split_zone_record_carries_zonedist2() -> None:
    fixture = load_fixture("F05_split_zone_lot.json")
    record = json.loads(fixture["response_body_raw"])[0]
    bbl = record["bbl"].split(".")[0]
    transport = FakeTransport([TransportResponse(200, fixture["response_body_raw"])])
    result = fetch_by_bbl(bbl, transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK)
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    assert by_field["splitzone"]["normalized_value"] is True
    assert "zonedist2" in by_field


def test_f10_marble_hill_borough_idiosyncrasy_preserved_verbatim() -> None:
    result, _ = fetch_fixture("F10_marble_hill.json", "1022150001")
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    # Legally Manhattan (borocode 1) but Bronx-serviced (sanitboro 2) -
    # both facts emitted verbatim, no "correction" applied (README 26v1).
    assert by_field["borocode"]["normalized_value"] == 1
    assert by_field["sanitboro"]["normalized_value"] == 2
    assert by_field["zipcode"]["normalized_value"] == 10463
    assert result.conflicts == []  # bbl/borocode/block/lot agree


def test_f6_pagination_fixtures_stable_order_no_dupes_no_gaps() -> None:
    page1 = json.loads(load_fixture("F06a_pagination_page1.json")["response_body_raw"])
    page2 = json.loads(load_fixture("F06b_pagination_page2.json")["response_body_raw"])
    assert len(page1) == 5 and len(page2) == 5
    bbls = [record["bbl"] for record in page1 + page2]
    assert bbls == sorted(bbls)  # $order=bbl stable ordering
    assert len(set(bbls)) == len(bbls)  # no duplicates across the boundary
    assert build_page_url(5, 5).endswith("$order=bbl&$limit=5&$offset=5")
    with pytest.raises(ValueError):
        build_page_url(0, 0)


def test_f14_change_file_companion_record_shape() -> None:
    fixture = load_fixture("F14_change_file_qt5r_nqxp.json")
    assert fixture["dataset_id"] == "qt5r-nqxp"
    record = json.loads(fixture["response_body_raw"])[0]
    assert {"bbl", "field", "old_value", "new_value", "version"} <= set(record)
    assert VERSION_RE.match(record["version"])


# --------------------------------------------------------------------------
# Fixture pack hygiene: every fixture carries its capture provenance
# --------------------------------------------------------------------------


def test_every_fixture_embeds_url_timestamp_and_capture_method() -> None:
    fixture_files = sorted(FIXTURE_DIR.glob("F*.json"))
    assert len(fixture_files) >= 17
    for path in fixture_files:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        assert fixture["request_url"].startswith("https://data.cityofnewyork.us/"), path.name
        assert "capture_method" in fixture, path.name
        assert "response_body_raw" in fixture, path.name
        if fixture["capture_method"].startswith("synthetic"):
            # F7: constructed from the official doc, clearly labeled, never
            # captured by bursting the shared pool.
            assert "synthetic-from-official-doc" == fixture["capture_method"], path.name
            assert fixture["retrieval_timestamp_utc"] is None
        else:
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
                fixture["retrieval_timestamp_utc"],
            ), path.name


# --------------------------------------------------------------------------
# Fixup pass 2026-07-16: G3 D1/D2/D3, G1 C1, G3 F5
# --------------------------------------------------------------------------


def test_d1_unparseable_record_bbl_is_schema_drift_not_validation_error() -> None:
    # SYNTHETIC variant (G3 D1): the record's OWN bbl cannot parse. That is
    # source-shape drift; validation_error is reserved for caller input
    # rejected before any network call.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["bbl"] = "0000000000.00000000"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_by_bbl(
            "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
        )
    assert not isinstance(excinfo.value, BBLValidationError)
    payload = excinfo.value.to_payload()
    assert payload["error_type"] == "schema_drift"
    assert payload["detail"]["validation_code"] == "invalid_borough"
    assert payload["detail"]["record_bbl_raw"] == repr("0000000000.00000000")
    assert len(transport.calls) == 1  # drift is never retried


@pytest.mark.parametrize("bad_value", ["NaN", "Infinity", "-Infinity"])
def test_d2_non_finite_number_is_drift_signal_with_raw_preserved(bad_value) -> None:
    # SYNTHETIC variant (G3 D2): float() accepts "NaN"/"Infinity" but they are
    # not usable numeric facts and break RFC-8259 JSON serialization.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["lotarea"] = bad_value
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert "non_finite_number_value:lotarea" in result.drift_signals
    lotarea = next(f for f in result.facts if f["original_field_name"] == "lotarea")
    assert lotarea["original_value"] == bad_value  # verbatim raw preserved
    assert lotarea["normalized_value"] == bad_value  # string passthrough...
    assert isinstance(lotarea["normalized_value"], str)  # ...never float nan/inf
    json.dumps(result.facts, allow_nan=False)  # RFC-8259-clean serialization


def test_d3_retrieved_at_stamped_after_successful_response() -> None:
    # G3 D3: the provenance timestamp must reflect the actual retrieval
    # moment, not a pre-request stamp that retries could skew by ~30s.
    events: list[str] = []
    tick = {"n": 0}

    def stepping_clock() -> datetime:
        tick["n"] += 1
        events.append("clock")
        return datetime(2026, 7, 16, 12, 0, tick["n"], tzinfo=UTC)

    inner = FakeTransport(
        [TransportResponse(503, "unavailable"),
         fixture_response("F01_single_lot_normal.json")]
    )

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        events.append("request")
        return inner(url, headers, timeout)

    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=stepping_clock
    )
    # The clock fires exactly once, AFTER the last (successful) attempt.
    assert events == ["request", "request", "clock"]
    assert result.retrieved_at == "2026-07-16T12:00:01Z"
    assert all(f["retrieved_at"] == result.retrieved_at for f in result.facts)


def test_c1_yearbuilt_zero_is_unknown_not_confident_zero() -> None:
    # The REAL F01 record carries yearbuilt "0"; dictionary p.34-35: 0/null
    # means the year built is UNKNOWN (G1 C1).
    result, _ = fetch_fixture("F01_single_lot_normal.json", "1000010100")
    yearbuilt = next(f for f in result.facts if f["original_field_name"] == "yearbuilt")
    assert yearbuilt["original_value"] == "0"  # verbatim raw preserved
    assert yearbuilt["normalized_value"] is None  # unknown, never year 0
    assert any(note.startswith("yearbuilt_unknown") for note in result.notes)


def test_c1_yearbuilt_absent_is_flagged_unknown() -> None:
    # SYNTHETIC variant: yearbuilt omitted entirely (SODA null-omission).
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    del record["yearbuilt"]
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    assert any(note.startswith("yearbuilt_unknown") for note in result.notes)
    assert "yearbuilt" in result.absent_columns
    assert not any(f["original_field_name"] == "yearbuilt" for f in result.facts)


def test_c1_real_construction_year_stays_a_normal_numeric_fact() -> None:
    # SYNTHETIC variant: a genuine construction year is untouched and no
    # unknown note fires.
    fixture = load_fixture("F01_single_lot_normal.json")
    record = json.loads(fixture["response_body_raw"])[0]
    record["yearbuilt"] = "1970"
    transport = FakeTransport([TransportResponse(200, json.dumps([record]))])
    result = fetch_by_bbl(
        "1000010100", transport=transport, sleep=SleepRecorder(), clock=FIXED_CLOCK
    )
    yearbuilt = next(f for f in result.facts if f["original_field_name"] == "yearbuilt")
    assert yearbuilt["normalized_value"] == 1970
    assert not any(note.startswith("yearbuilt_unknown") for note in result.notes)


class _FakeUrlopenResponse:
    """Minimal stand-in for the http.client.HTTPResponse context manager."""

    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self, amt: int | None = None) -> bytes:
        # Mirrors http.client.HTTPResponse.read(amt): bounded reads (G5 F1)
        # pass an explicit byte cap.
        if amt is None:
            return self._body
        return self._body[:amt]

    def __enter__(self) -> "_FakeUrlopenResponse":
        return self

    def __exit__(self, *exc_info) -> bool:
        return False


class _FakeOpener:
    """Stand-in for pluto_soda._OPENER (the no-redirect opener, G5 F3). The
    transport calls _OPENER.open(request, timeout=...), so transport tests
    monkeypatch the module-level opener rather than urllib.request.urlopen."""

    def __init__(self, fn):
        self._fn = fn

    def open(self, request, timeout=None):
        return self._fn(request, timeout=timeout)


def test_urllib_transport_success_returns_status_and_decoded_body(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["accept"] = request.get_header("Accept")
        return _FakeUrlopenResponse(200, b'[{"version": "26v1"}]')

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_urlopen))
    response = urllib_transport(
        f"{BASE_URL}?bbl=1000010100", {"Accept": "application/json"}, 10.0
    )
    assert response == TransportResponse(200, '[{"version": "26v1"}]')
    assert captured["url"] == f"{BASE_URL}?bbl=1000010100"
    assert captured["timeout"] == 10.0
    assert captured["accept"] == "application/json"


def test_urllib_transport_http_error_body_passes_through_as_response(monkeypatch) -> None:
    # G3 F5: HTTPError must NOT propagate - its status/body become a normal
    # TransportResponse so the caller can classify 400/429/5xx itself.
    body = b'{"errorCode": "query.soql.no-such-column"}'

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", None, io.BytesIO(body)
        )

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_urlopen))
    response = urllib_transport(BASE_URL, {}, 10.0)
    assert response.status == 400
    assert json.loads(response.body)["errorCode"] == "query.soql.no-such-column"


def test_urllib_transport_timeout_error_maps_to_transport_timeout(monkeypatch) -> None:
    def fake_urlopen(request, timeout=None):
        raise TimeoutError("timed out")

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_urlopen))
    with pytest.raises(TransportTimeout) as excinfo:
        urllib_transport(BASE_URL, {}, 2.5)
    assert "2.5" in str(excinfo.value)


def test_urllib_transport_urlerror_timeout_reason_maps_to_transport_timeout(
    monkeypatch,
) -> None:
    def fake_urlopen(request, timeout=None):
        raise urllib.error.URLError(TimeoutError("timed out"))

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_urlopen))
    with pytest.raises(TransportTimeout):
        urllib_transport(BASE_URL, {}, 2.5)


@pytest.mark.parametrize(
    "reason",
    [ConnectionRefusedError("refused"), socket.gaierror(11001, "getaddrinfo failed")],
    ids=["connection_refused", "dns_gaierror"],
)
def test_urllib_transport_urlerror_network_reason_maps_to_transport_failure(
    monkeypatch, reason
) -> None:
    def fake_urlopen(request, timeout=None):
        raise urllib.error.URLError(reason)

    monkeypatch.setattr(pluto_soda, "_OPENER", _FakeOpener(fake_urlopen))
    with pytest.raises(TransportFailure) as excinfo:
        urllib_transport(BASE_URL, {}, 10.0)
    # Message carries only the failure type name - no URL, no reason detail
    # that could embed secrets.
    assert str(excinfo.value) == f"network failure: {type(reason).__name__}"


def test_connector_error_hierarchy_and_taxonomy() -> None:
    taxonomy = {
        RateLimitedError: "rate_limited",
        SchemaDriftError: "schema_drift",
        SourceTimeoutError: "timeout",
        SourceUnavailableError: "source_unavailable",
    }
    for cls, error_type in taxonomy.items():
        assert issubclass(cls, PlutoConnectorError)
        assert cls.error_type == error_type
    assert BBLValidationError.error_type == "validation_error"
    assert len(VINTAGE_DATE_COLUMNS) == 8
    assert pluto_soda.SOURCE_ID == "nyc-dcp-pluto-soda"
