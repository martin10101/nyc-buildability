"""M2-T021 acceptance pack for the Geoclient v2 /address connector (S1..S8).

Offline and deterministic: every test drives the connector through the
injected transport seam against the three RECORDED fixtures
(G01 happy path, G02 ambiguity EE, G03 rejection 42) or against clearly
labeled CONSTRUCTED variants of them. No test touches the network; no test
uses a real key (S6 uses a sentinel and asserts leak absence everywhere).

Anti-tautology rule (packet S1, the M5-T004 lesson): expected values are
LOADED FROM THE FIXTURE and compared, never restated as literals in the
assertions.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict
from pathlib import Path

import pytest

from app.connectors.geoclient_address import (
    ENDPOINT_URL,
    KEY_ENV_VAR,
    KEY_HEADER,
    SOURCE_ID,
    AuthFailedError,
    GeoclientConnectorError,
    InvalidInputError,
    KeyMissingError,
    MalformedResponseError,
    RateLimitedError,
    SourceTimeoutError,
    SourceUnavailableError,
    resolve_address,
)
from app.connectors.pluto_soda import canonical_json_digest
from app.resilience.transport import TransportResponse, TransportTimeout

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "geoclient"

# Clearly fake sentinel for the S6 leak-absence tests (the accepted
# test_pluto_soda pattern): never a real credential.
SENTINEL_KEY = "fake-geoclient-sentinel-key-leak-absence-test-only"

def _NO_SLEEP(_seconds: float) -> None:
    """Test shim: never actually sleep."""


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _fixture_body(name: str) -> str:
    return _fixture(name)["response_body_raw"]


def _fixture_address(name: str) -> dict:
    return json.loads(_fixture_body(name))["address"]


class RecordingTransport:
    """Injected seam: returns queued responses (or raises queued exceptions)
    and records every (url, headers, timeout) call."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls: list[tuple[str, dict, float]] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append((url, dict(headers), timeout))
        outcome = self.outcomes[0] if len(self.outcomes) == 1 else self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _resolve(transport, *, house_number="314", street="w 100 st", **overrides):
    kwargs = dict(
        borough="manhattan",
        key=SENTINEL_KEY,
        transport=transport,
        sleep=_NO_SLEEP,
    )
    kwargs.update(overrides)
    return resolve_address(house_number, street, **kwargs)


# ===========================================================================
# S1 - normal resolution against the recorded G01 fixture.
# ===========================================================================

def test_s1_resolved_fields_are_loaded_from_the_fixture_never_literals():
    addr = _fixture_address("G01_address_documented_example.json")
    transport = RecordingTransport(
        TransportResponse(200, _fixture_body("G01_address_documented_example.json"))
    )
    res = _resolve(transport)

    assert res.status == "resolved"
    # Every expected value comes from the fixture (anti-tautology rule).
    assert res.bbl == addr["bbl"]
    assert res.bin == addr["buildingIdentificationNumber"]
    assert res.street_name_normalized == addr["firstStreetNameNormalized"]
    assert res.borough_name == addr["firstBoroughName"]
    assert res.zip_code == addr["zipCode"]
    assert res.latitude == addr["latitude"]
    assert res.longitude == addr["longitude"]
    # Identifier types survive verbatim: strings in, strings out (S8 overlap).
    assert isinstance(res.bbl, str) and isinstance(res.bin, str)
    assert isinstance(res.zip_code, str)
    # The whole address object rides along verbatim.
    assert res.raw_fields == addr
    # Both GRC codes surfaced.
    assert res.grc == addr["geosupportReturnCode"]
    assert res.grc2 == addr["geosupportReturnCode2"]


def test_s1_provenance_is_complete_and_key_free():
    body = _fixture_body("G01_address_documented_example.json")
    addr = _fixture_address("G01_address_documented_example.json")
    transport = RecordingTransport(TransportResponse(200, body))
    res = _resolve(transport)

    prov = res.provenance
    assert prov["source_id"] == SOURCE_ID
    assert prov["endpoint"] == ENDPOINT_URL
    assert prov["request_params"] == {
        "houseNumber": "314", "street": "w 100 st", "borough": "manhattan",
    }
    assert prov["http_status"] == 200
    assert prov["geosupport_return_code"] == addr["geosupportReturnCode"]
    assert prov["geosupport_return_code2"] == addr["geosupportReturnCode2"]
    assert prov["response_digest"] == canonical_json_digest(json.loads(body))
    assert prov["correlation_id"] == res.correlation_id
    # RFC3339 Zulu shape.
    import re
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", prov["retrieved_at"])
    # The key appears NOWHERE in the outcome.
    assert SENTINEL_KEY not in json.dumps(asdict(res))


def test_s1_transport_receives_header_only_auth_and_key_free_url():
    transport = RecordingTransport(
        TransportResponse(200, _fixture_body("G01_address_documented_example.json"))
    )
    _resolve(transport)
    (url, headers, timeout), = transport.calls
    assert url.startswith(ENDPOINT_URL + "?")
    assert "houseNumber=314" in url and "borough=manhattan" in url
    assert SENTINEL_KEY not in url
    assert headers[KEY_HEADER] == SENTINEL_KEY
    assert headers["Accept"] == "application/json"
    assert timeout > 0


# ===========================================================================
# S2 - BOTH sub-call codes always count (constructed variants of G01).
# ===========================================================================

def _g01_variant(**field_overrides) -> str:
    """CONSTRUCTED fixture variant: the recorded G01 body with named address
    fields replaced (clearly labeled constructed, packet S2)."""
    parsed = json.loads(_fixture_body("G01_address_documented_example.json"))
    parsed["address"].update(field_overrides)
    return json.dumps(parsed)


def test_s2_second_sub_call_failure_is_never_a_clean_success():
    body = _g01_variant(
        geosupportReturnCode2="42",
        message2="CONSTRUCTED SUB-CALL FAILURE (test variant of G01)",
    )
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "rejected"
    assert res.grc2 == "42"
    assert res.grc2_message == "CONSTRUCTED SUB-CALL FAILURE (test variant of G01)"


@pytest.mark.parametrize(
    ("grc", "grc2", "expected_status"),
    [
        ("00", "00", "resolved"),
        ("00", "01", "resolved_with_warnings"),
        ("01", "00", "resolved_with_warnings"),
        ("01", "01", "resolved_with_warnings"),
    ],
)
def test_s2_clean_success_requires_both_codes_00(grc, grc2, expected_status):
    body = _g01_variant(geosupportReturnCode=grc, geosupportReturnCode2=grc2)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == expected_status
    assert (res.status == "resolved") == (grc == "00" and grc2 == "00")


# ===========================================================================
# S3 - ambiguity (recorded G02) and not-found (constructed 11 variant).
# ===========================================================================

def test_s3_recorded_ee_response_is_ambiguous_with_verbatim_suggestions():
    addr = _fixture_address("G02_address_ambiguous_ee.json")
    res = _resolve(
        RecordingTransport(
            TransportResponse(200, _fixture_body("G02_address_ambiguous_ee.json"))
        ),
        street="w 100 sreet",
    )
    assert res.status == "ambiguous"
    # Suggestions loaded from the fixture's own slots, never restated.
    assert res.suggestions == [
        {"street_name": addr["streetName1"], "street_code": addr["streetCode1"]}
    ]
    # Messages and reason codes verbatim, both sub-calls.
    assert res.grc_message == addr["message"]
    assert res.grc2_message == addr["message2"]
    assert res.grc_reason == addr["reasonCode"]
    # The connector never picks a suggestion: no canonical BBL is fabricated.
    assert res.bbl is None


def test_s3_constructed_grc_11_is_not_found_with_no_suggestions():
    body = _g01_variant(
        geosupportReturnCode="11",
        geosupportReturnCode2="11",
        message="CONSTRUCTED: NOT RECOGNIZED. THERE ARE NO SIMILAR NAMES",
    )
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "not_found"
    assert res.suggestions == []


# ===========================================================================
# S4 - rejection (recorded G03).
# ===========================================================================

def test_s4_recorded_rejection_is_typed_and_transports_partial_data():
    addr = _fixture_address("G03_address_rejected_42.json")
    res = _resolve(
        RecordingTransport(
            TransportResponse(200, _fixture_body("G03_address_rejected_42.json"))
        ),
        house_number="99999",
    )
    assert res.status == "rejected"
    assert res.grc == addr["geosupportReturnCode"]
    assert res.grc_message == addr["message"]
    # A reject response still carries partial data; it is transported, never
    # promoted to success and never dropped.
    assert res.street_name_normalized == addr["firstStreetNameNormalized"]
    assert res.bbl is None


# ===========================================================================
# S5 - transport and auth failures.
# ===========================================================================

def test_s5_timeout_persists_through_bounded_retry_budget():
    transport = RecordingTransport(TransportTimeout("connect timeout"))
    with pytest.raises(SourceTimeoutError):
        _resolve(transport, max_attempts=3)
    assert len(transport.calls) == 3  # bounded - no retry storm


@pytest.mark.parametrize("status", [401, 403])
def test_s5_auth_failure_is_typed_immediate_and_key_free(status):
    transport = RecordingTransport(TransportResponse(status, "gateway says no"))
    with pytest.raises(AuthFailedError) as excinfo:
        _resolve(transport)
    assert len(transport.calls) == 1  # never retried
    err = excinfo.value
    assert err.detail["http_status"] == status
    combined = str(err) + json.dumps(err.to_payload())
    assert SENTINEL_KEY not in combined
    assert "gateway says no" not in combined  # body never echoed


def test_s5_persistent_500_is_source_unavailable_after_budget():
    transport = RecordingTransport(TransportResponse(500, "oops"))
    with pytest.raises(SourceUnavailableError):
        _resolve(transport, max_attempts=2)
    assert len(transport.calls) == 2


def test_s5_persistent_429_is_rate_limited():
    transport = RecordingTransport(TransportResponse(429, "slow down"))
    with pytest.raises(RateLimitedError):
        _resolve(transport, max_attempts=2)


@pytest.mark.parametrize(
    "body", ["this is not json", '{"weird": 1}', '{"address": "not a dict"}', "[]"]
)
def test_s5_malformed_200_bodies_fail_closed(body):
    with pytest.raises(MalformedResponseError):
        _resolve(RecordingTransport(TransportResponse(200, body)))


def test_s5_invalid_input_raises_before_any_network_call():
    transport = RecordingTransport()
    with pytest.raises(InvalidInputError):
        resolve_address("", "w 100 st", borough="manhattan",
                        key=SENTINEL_KEY, transport=transport, sleep=_NO_SLEEP)
    with pytest.raises(InvalidInputError):
        resolve_address("314", "w 100 st",
                        key=SENTINEL_KEY, transport=transport, sleep=_NO_SLEEP)
    assert transport.calls == []


# ===========================================================================
# S6 - key hygiene.
# ===========================================================================

def test_s6_sentinel_never_leaks_from_any_path(caplog):
    """Success, ambiguity, rejection, auth failure, timeout and malformed
    paths all exercised with the sentinel key; the sentinel must appear in
    no outcome, no exception, no payload, and no captured log record."""
    caplog.set_level(logging.DEBUG, logger="app.connectors.geoclient_address")
    caplog.set_level(logging.DEBUG, logger="app.resilience.transport")
    harvested: list[str] = []

    for body_name in (
        "G01_address_documented_example.json",
        "G02_address_ambiguous_ee.json",
        "G03_address_rejected_42.json",
    ):
        res = _resolve(RecordingTransport(TransportResponse(200, _fixture_body(body_name))))
        harvested.append(json.dumps(asdict(res)))
        harvested.append(repr(res))

    for failure in (
        TransportResponse(401, "no"),
        TransportTimeout("t"),
        TransportResponse(200, "not json"),
    ):
        try:
            _resolve(RecordingTransport(failure, failure, failure))
        except GeoclientConnectorError as err:
            harvested.append(str(err))
            harvested.append(json.dumps(err.to_payload()))

    harvested.extend(record.getMessage() for record in caplog.records)
    assert SENTINEL_KEY not in "".join(harvested)


def test_s6_key_is_read_from_env_at_call_time_header_only():
    transport = RecordingTransport(
        TransportResponse(200, _fixture_body("G01_address_documented_example.json"))
    )
    resolve_address(
        "314", "w 100 st", borough="manhattan",
        transport=transport, sleep=_NO_SLEEP,
        env={KEY_ENV_VAR: SENTINEL_KEY},
    )
    (url, headers, _), = transport.calls
    assert headers[KEY_HEADER] == SENTINEL_KEY
    assert SENTINEL_KEY not in url


def test_s6_missing_key_is_typed_and_attempts_no_network():
    transport = RecordingTransport()
    with pytest.raises(KeyMissingError) as excinfo:
        resolve_address("314", "w 100 st", borough="manhattan",
                        transport=transport, sleep=_NO_SLEEP, env={})
    assert transport.calls == []
    payload = excinfo.value.to_payload()
    assert payload["detail"]["env_var"] == KEY_ENV_VAR


# ===========================================================================
# S7 - offline discipline and fixture integrity.
# ===========================================================================

@pytest.mark.parametrize(
    "name",
    [
        "G01_address_documented_example.json",
        "G02_address_ambiguous_ee.json",
        "G03_address_rejected_42.json",
    ],
)
def test_s7_fixture_digest_matches_stored_sha256(name):
    fixture = _fixture(name)
    actual = hashlib.sha256(fixture["response_body_raw"].encode("utf-8")).hexdigest()
    assert actual == fixture["response_sha256"], f"fixture drift in {name}"


def test_s7_key_check_precedes_any_transport_use(monkeypatch):
    """With no key available, the DEFAULT transport is unreachable: the typed
    KeyMissingError fires before any network object is touched."""
    import app.connectors.geoclient_address as mod

    def _boom(*_a, **_k):  # pragma: no cover - must never run
        raise AssertionError("network transport was invoked")

    monkeypatch.setattr(mod, "urllib_transport", _boom)
    with pytest.raises(KeyMissingError):
        resolve_address("314", "w 100 st", borough="manhattan", env={})


# ===========================================================================
# S8 - transport honesty: null omission, unknown GRC fail-closed, verbatim
# identifiers.
# ===========================================================================

def test_s8_absent_fields_are_none_never_fabricated():
    parsed = json.loads(_fixture_body("G01_address_documented_example.json"))
    del parsed["address"]["zipCode"]  # CONSTRUCTED absence (null omission)
    res = _resolve(RecordingTransport(TransportResponse(200, json.dumps(parsed))))
    assert res.zip_code is None
    assert res.status == "resolved"  # absence of an attribute is not an error


@pytest.mark.parametrize("bad", ["ZZZ", "", "0", "0x", None])
def test_s8_invalid_shape_grc_fails_closed_as_unrecognized(bad):
    overrides = {"geosupportReturnCode": bad} if bad is not None else {}
    parsed = json.loads(_fixture_body("G01_address_documented_example.json"))
    if bad is None:
        del parsed["address"]["geosupportReturnCode"]
    else:
        parsed["address"].update(overrides)
    res = _resolve(RecordingTransport(TransportResponse(200, json.dumps(parsed))))
    assert res.status == "unrecognized_status"


def test_s8_valid_shape_unknown_code_is_the_documented_reject_class():
    body = _g01_variant(geosupportReturnCode="77", geosupportReturnCode2="77")
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "rejected"


def test_s8_identifiers_stay_verbatim_strings():
    addr = _fixture_address("G01_address_documented_example.json")
    res = _resolve(
        RecordingTransport(
            TransportResponse(200, _fixture_body("G01_address_documented_example.json"))
        )
    )
    # The PLUTO decimal-BBL lesson: no numeric coercion anywhere.
    assert res.bbl == addr["bbl"] and type(res.bbl) is str
    assert res.raw_fields["bbl"] == addr["bbl"] and type(res.raw_fields["bbl"]) is str
