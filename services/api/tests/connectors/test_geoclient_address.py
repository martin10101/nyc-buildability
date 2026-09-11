"""M2-T021 acceptance pack for the Geoclient v2 /address connector (S1..S8),
REWORKED after the G1/G3/G4/G5 gate wave at d4cdbe79.

Offline and deterministic: every test drives the connector through the
injected transport seam against the three RECORDED fixtures (G01 happy path,
G02 ambiguity EE, G03 rejection 42) or against clearly labeled CONSTRUCTED
variants of them. A module-wide socket guard makes network I/O mechanically
impossible, not merely unexercised. No test uses a real key (S6 uses a
sentinel with a positive control proving the sentinel actually reached the
auth header before leak absence is asserted).

Anti-tautology rule (packet S1, the M5-T004 lesson): expected values are
LOADED FROM THE FIXTURE and compared, never restated as literals in the
assertions.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import socket
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.geoclient_address import (
    ENDPOINT_URL,
    KEY_ENV_VAR,
    KEY_HEADER,
    MAX_STREET_CHARS,
    RESOLUTION_STATUSES,
    SOURCE_ID,
    AuthFailedError,
    GeoclientConnectorError,
    InvalidInputError,
    KeyMissingError,
    MalformedResponseError,
    RateLimitedError,
    RequestBudgetExceededError,
    SourceTimeoutError,
    SourceUnavailableError,
    resolve_address,
)
from app.connectors.pluto_soda import CANONICALIZATION_SPEC, canonical_json_digest
from app.resilience.budget import AnalysisBudget
from app.resilience.transport import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "geoclient"

G01 = "G01_address_documented_example.json"
G02 = "G02_address_ambiguous_ee.json"
G03 = "G03_address_rejected_42.json"

# Clearly fake sentinel for the S6 leak-absence tests (the accepted
# test_pluto_soda pattern): never a real credential.
SENTINEL_KEY = "fake-geoclient-sentinel-key-leak-absence-test-only"

_RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Mechanical no-network guard (G4 finding 16): any attempt to open a
    socket in any test of this module fails loudly."""

    def _blocked(*_args, **_kwargs):  # pragma: no cover - must never run
        raise AssertionError("network I/O attempted in an offline test module")

    monkeypatch.setattr(socket, "socket", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def _no_sleep(_seconds: float) -> None:
    """Test shim: never actually sleep."""


def _fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _fixture_body(name: str) -> str:
    return _fixture(name)["response_body_raw"]


def _fixture_address(name: str) -> dict:
    return json.loads(_fixture_body(name))["address"]


class RecordingTransport:
    """Injected seam: returns queued responses (or raises queued exceptions)
    and records every (url, headers, timeout) call. A single queued outcome
    repeats for every attempt; with several queued, over-consumption fails
    loudly rather than raising a bare IndexError (G4 finding 17)."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls: list[tuple[str, dict, float]] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append((url, dict(headers), timeout))
        if not self.outcomes:
            raise AssertionError("RecordingTransport queue over-consumed")
        outcome = self.outcomes[0] if len(self.outcomes) == 1 else self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _resolve(transport, *, house_number="314", street="w 100 st", **overrides):
    kwargs = dict(
        borough="manhattan",
        key=SENTINEL_KEY,
        transport=transport,
        sleep=_no_sleep,
    )
    kwargs.update(overrides)
    return resolve_address(house_number, street, **kwargs)


def _g01_variant(_remove=(), **field_overrides) -> str:
    """CONSTRUCTED fixture variant (clearly labeled, packet rule): the
    recorded G01 body with named address fields replaced or removed."""
    parsed = json.loads(_fixture_body(G01))
    for key in _remove:
        parsed["address"].pop(key, None)
    parsed["address"].update(field_overrides)
    return json.dumps(parsed)


# ===========================================================================
# S1 - normal resolution against the recorded G01 fixture.
# ===========================================================================

def test_s1_resolved_fields_are_loaded_from_the_fixture_never_literals():
    addr = _fixture_address(G01)
    res = _resolve(RecordingTransport(TransportResponse(200, _fixture_body(G01))))

    assert res.status == "resolved"
    # Every expected value comes from the fixture (anti-tautology rule).
    assert res.bbl == addr["bbl"]
    assert res.bin == addr["buildingIdentificationNumber"]
    assert res.street_name_normalized == addr["firstStreetNameNormalized"]
    assert res.borough_name == addr["firstBoroughName"]
    assert res.zip_code == addr["zipCode"]
    assert res.latitude == addr["latitude"]
    assert res.longitude == addr["longitude"]
    # Identifier and coordinate TYPES survive verbatim (S8 overlap): what the
    # source emitted as str stays str, its JSON numbers keep their own type.
    assert type(res.bbl) is type(addr["bbl"]) is str
    assert type(res.bin) is type(addr["buildingIdentificationNumber"]) is str
    assert type(res.zip_code) is str
    assert type(res.latitude) is type(addr["latitude"])
    assert type(res.longitude) is type(addr["longitude"])
    # The whole address object rides along verbatim. (Its deep copy is
    # deliberately NOT asserted here: every recorded value is a scalar and
    # the connector's own parse dies at return, so no external assertion can
    # observe the copy — the prior mutation assertion could not fail and was
    # removed rather than replaced with another tautology; G1/G3 re-review
    # N1/N2. The copy is labeled defense-in-depth at the dataclass field.)
    assert res.raw_fields == addr
    # Caller-echo fields (G4 finding 15).
    assert res.house_number_in == "314"
    assert res.street_in == "w 100 st"
    assert res.borough_in == "manhattan"
    assert res.zip_in is None


@pytest.mark.parametrize("name", [G01, G02, G03], ids=["G01", "G02", "G03"])
def test_s1_grc_fields_match_both_documented_forms(name):
    """The primary GRC names must agree with the documented 1e/1a aliases on
    every recorded fixture — the swap-proof assertion (G4 finding 1): the
    first sub-call code must equal returnCode1e, the second returnCode1a."""
    addr = _fixture_address(name)
    res = _resolve(RecordingTransport(TransportResponse(200, _fixture_body(name))))
    assert res.grc == addr["geosupportReturnCode"] == addr["returnCode1e"]
    assert res.grc2 == addr["geosupportReturnCode2"] == addr["returnCode1a"]


def test_s1_provenance_is_complete_and_key_free():
    body = _fixture_body(G01)
    addr = _fixture_address(G01)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))

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
    # The digest carries its own recomputation spec (G3 finding 5).
    assert prov["digest_canonicalization"] == CANONICALIZATION_SPEC
    assert prov["correlation_id"] == res.correlation_id
    assert _RFC3339_RE.match(prov["retrieved_at"])
    # The key appears NOWHERE in the outcome.
    assert SENTINEL_KEY not in json.dumps(asdict(res))


def test_s1_transport_receives_header_only_auth_and_key_free_url():
    transport = RecordingTransport(TransportResponse(200, _fixture_body(G01)))
    _resolve(transport)
    (url, headers, timeout), = transport.calls
    assert url.startswith(ENDPOINT_URL + "?")
    assert SENTINEL_KEY not in url
    assert headers[KEY_HEADER] == SENTINEL_KEY
    assert headers["Accept"] == "application/json"
    assert timeout > 0


def test_s1_constructed_url_equals_the_recorded_capture_url():
    """The emitted URL must be byte-identical to the URL each fixture was
    actually captured with — %20 percent-encoding, never '+' (G4 finding 5:
    the fixtures are the only evidence of live-accepted encoding)."""
    cases = [
        (G01, dict(house_number="314", street="w 100 st", borough="manhattan")),
        (G02, dict(house_number="314", street="w 100 sreet", borough="manhattan")),
        (G03, dict(house_number="99999", street="w 100 st", borough="manhattan")),
    ]
    for name, kwargs in cases:
        transport = RecordingTransport(TransportResponse(200, _fixture_body(name)))
        _resolve(transport, **kwargs)
        (url, _headers, _timeout), = transport.calls
        assert url == _fixture(name)["request_url"], name


def test_s1_default_transport_is_resolved_at_call_time(monkeypatch):
    """Omitting transport= uses the module's urllib transport, resolved at
    call time (monkeypatchable seam), and the sentinel reaches its headers."""
    import app.connectors.geoclient_address as mod

    recorder = RecordingTransport(TransportResponse(200, _fixture_body(G01)))
    monkeypatch.setattr(mod, "urllib_transport", recorder)
    res = resolve_address(
        "314", "w 100 st", borough="manhattan", key=SENTINEL_KEY, sleep=_no_sleep
    )
    assert res.status == "resolved"
    (_url, headers, _timeout), = recorder.calls
    assert headers[KEY_HEADER] == SENTINEL_KEY


def test_s1_zip_form_request():
    """The zip half of the documented endpoint contract (G4 finding 3):
    zip-only requests carry zip= (not borough=) in URL and provenance, and
    the zip echo field is populated. CONSTRUCTED: the recorded G01 body is
    reused as the response; only the request side is under test."""
    transport = RecordingTransport(TransportResponse(200, _fixture_body(G01)))
    res = resolve_address(
        "314", "w 100 st", zip_code="10025",
        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep,
    )
    (url, _headers, _timeout), = transport.calls
    assert "zip=10025" in url
    assert "borough=" not in url
    assert res.zip_in == "10025"
    assert res.borough_in is None
    assert res.provenance["request_params"] == {
        "houseNumber": "314", "street": "w 100 st", "zip": "10025",
    }


def test_s1_borough_and_zip_together_sends_both():
    transport = RecordingTransport(TransportResponse(200, _fixture_body(G01)))
    res = _resolve(transport, zip_code="10025")
    (url, _h, _t), = transport.calls
    assert "borough=manhattan" in url and "zip=10025" in url
    assert res.borough_in == "manhattan" and res.zip_in == "10025"


# ===========================================================================
# S2 - BOTH sub-call codes always count (constructed variants of G01).
# ===========================================================================

def test_s2_second_sub_call_failure_is_never_a_clean_success():
    body = _g01_variant(
        geosupportReturnCode2="42",
        message2="CONSTRUCTED SUB-CALL FAILURE (test variant of G01)",
    )
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "rejected"
    assert res.grc == "00"  # the first sub-call code is still surfaced
    assert res.grc2 == "42"
    assert res.grc2_message == "CONSTRUCTED SUB-CALL FAILURE (test variant of G01)"


def test_s2_sub_call_sides_are_never_swapped():
    """Swap-proof (G4 finding 1): an asymmetric CONSTRUCTED variant with
    DISTINCT codes, reasons and messages per side must land each element on
    its own side of the outcome."""
    body = _g01_variant(
        geosupportReturnCode="00",
        reasonCode="",
        message="CONSTRUCTED side-1 message",
        geosupportReturnCode2="EE",
        reasonCode2="1",
        message2="CONSTRUCTED side-2 message",
    )
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "ambiguous"
    assert (res.grc, res.grc_reason, res.grc_message) == (
        "00", "", "CONSTRUCTED side-1 message"
    )
    assert (res.grc2, res.grc2_reason, res.grc2_message) == (
        "EE", "1", "CONSTRUCTED side-2 message"
    )


@pytest.mark.parametrize(
    ("grc", "grc2", "expected_status"),
    [
        ("00", "00", "resolved"),
        ("00", "01", "resolved_with_warnings"),
        ("01", "00", "resolved_with_warnings"),
        ("01", "01", "resolved_with_warnings"),
    ],
    ids=["00-00", "00-01", "01-00", "01-01"],
)
def test_s2_clean_success_requires_both_codes_00(grc, grc2, expected_status):
    body = _g01_variant(geosupportReturnCode=grc, geosupportReturnCode2=grc2)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == expected_status
    assert (res.grc, res.grc2) == (grc, grc2)
    assert (res.status == "resolved") == (grc == "00" and grc2 == "00")


def test_s2_warning_outcome_surfaces_the_warning_message():
    """packet S2: 'both codes and both messages' — the warning class must
    carry its message and reason (G4 finding 7). CONSTRUCTED variant."""
    body = _g01_variant(
        geosupportReturnCode2="01",
        reasonCode2="V",
        message2="CONSTRUCTED WARNING (test variant of G01)",
    )
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "resolved_with_warnings"
    assert res.grc2_reason == "V"
    assert res.grc2_message == "CONSTRUCTED WARNING (test variant of G01)"


@pytest.mark.parametrize(
    ("grc", "grc2", "expected_status"),
    [
        ("00", "EE", "ambiguous"),
        ("EE", "00", "ambiguous"),
        ("42", "EE", "ambiguous"),
        ("00", "11", "not_found"),
        ("11", "00", "not_found"),
        ("11", "01", "not_found"),
        ("00", "42", "rejected"),
        ("42", "00", "rejected"),
        ("77", "77", "rejected"),
    ],
    ids=[
        "00-EE", "EE-00", "42-EE", "00-11", "11-00",
        "11-01", "00-42", "42-00", "77-77",
    ],
)
def test_s2_disagreement_matrix(grc, grc2, expected_status):
    """The mixed-code precedence table (G1 finding 7): ambiguity outranks
    not-found outranks reject; the 'valid for only one sub-call' cases are
    the documented common ones. CONSTRUCTED variants of G01."""
    body = _g01_variant(geosupportReturnCode=grc, geosupportReturnCode2=grc2)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == expected_status
    assert res.status in RESOLUTION_STATUSES


def test_s2_not_found_from_one_sub_call_still_transports_partial_fields():
    """The documented common case ('valid for only one sub-call'): a
    not_found outcome may legitimately carry a populated bbl from the valid
    sub-call — deliberate, documented on the result contract (G1 finding 7).
    CONSTRUCTED variant."""
    body = _g01_variant(geosupportReturnCode2="11")
    addr = _fixture_address(G01)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "not_found"
    assert res.bbl == addr["bbl"]  # populated, per the contract note


# ===========================================================================
# S3 - ambiguity (recorded G02) and not-found (constructed 11 variant).
# ===========================================================================

def test_s3_recorded_ee_response_is_ambiguous_with_verbatim_suggestions():
    addr = _fixture_address(G02)
    res = _resolve(
        RecordingTransport(TransportResponse(200, _fixture_body(G02))),
        street="w 100 sreet",
    )
    assert res.status == "ambiguous"
    # Suggestions loaded from the fixture's own slots, never restated.
    assert res.suggestions == [
        {"street_name": addr["streetName1"], "street_code": addr["streetCode1"]}
    ]
    assert type(res.suggestions[0]["street_code"]) is str
    # Messages and reason codes verbatim, both sub-calls.
    assert res.grc_message == addr["message"]
    assert res.grc2_message == addr["message2"]
    assert res.grc_reason == addr["reasonCode"]
    assert res.grc2_reason == addr["reasonCode2"]
    # The declared count is transported verbatim inside raw_fields.
    assert (
        res.raw_fields["numberOfStreetCodesAndNamesInList"]
        == addr["numberOfStreetCodesAndNamesInList"]
    )
    # Non-selection: the connector surfaces no canonical identity where the
    # source provided none, and no suggestion value is promoted anywhere.
    assert "bbl" not in res.raw_fields  # fixture fact, stated explicitly
    assert res.bbl is None and res.bin is None


def test_s3_multi_suggestion_walk_with_gaps_and_codeless_slots():
    """Multi-suggestion coverage (G4 finding 6; research reason codes 2-A):
    CONSTRUCTED variant of the recorded G02 with three populated slots, a
    missing middle slot, and one name-without-code slot."""
    parsed = json.loads(_fixture_body(G02))
    parsed["address"].update({
        "numberOfStreetCodesAndNamesInList": "04",
        "streetName2": "",              # blank slot: skipped, never fabricated
        "streetName3": "WEST 101 STREET",
        "streetCode3": "13577002",
        "streetName4": "WEST 102 STREET",  # name without a code
    })
    addr = parsed["address"]
    res = _resolve(RecordingTransport(TransportResponse(200, json.dumps(parsed))))
    assert res.status == "ambiguous"
    assert res.suggestions == [
        {"street_name": addr["streetName1"], "street_code": addr["streetCode1"]},
        {"street_name": "WEST 101 STREET", "street_code": "13577002"},
        {"street_name": "WEST 102 STREET"},
    ]


@pytest.mark.parametrize(
    "declared", ["00", "-3", "abc", "999999", None],
    ids=["zero", "negative", "nonnumeric", "huge", "absent"],
)
def test_s3_declared_count_is_ignored_suggestions_come_from_slots(declared):
    """The declared count is untrusted in BOTH directions (G1 finding 4): a
    hostile or absent count never hides populated slots and never invents
    empty ones. CONSTRUCTED variants of G02."""
    parsed = json.loads(_fixture_body(G02))
    if declared is None:
        parsed["address"].pop("numberOfStreetCodesAndNamesInList", None)
    else:
        parsed["address"]["numberOfStreetCodesAndNamesInList"] = declared
    addr = parsed["address"]
    res = _resolve(RecordingTransport(TransportResponse(200, json.dumps(parsed))))
    assert res.status == "ambiguous"
    assert res.suggestions == [
        {"street_name": addr["streetName1"], "street_code": addr["streetCode1"]}
    ]


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
    addr = _fixture_address(G03)
    res = _resolve(
        RecordingTransport(TransportResponse(200, _fixture_body(G03))),
        house_number="99999",
    )
    assert res.status == "rejected"
    # Both codes and both messages, verbatim (packet: GRC, reason code and
    # source message). G03 carries no reasonCode at all - null omission, so
    # the reason is None, not fabricated (G4 finding 14).
    assert res.grc == addr["geosupportReturnCode"]
    assert res.grc_message == addr["message"]
    assert "reasonCode" not in addr  # fixture fact, stated explicitly
    assert res.grc_reason is None
    assert res.grc2 == addr["geosupportReturnCode2"]
    assert res.grc2_message == addr["message2"]
    # A reject response still carries partial data; transported, never
    # promoted to success and never dropped.
    assert res.street_name_normalized == addr["firstStreetNameNormalized"]
    assert res.borough_name == addr["firstBoroughName"]
    assert res.bbl is None


# ===========================================================================
# S5 - transport and auth failures.
# ===========================================================================

def test_s5_timeout_persists_through_bounded_retry_budget():
    transport = RecordingTransport(TransportTimeout("connect timeout"))
    with pytest.raises(SourceTimeoutError):
        _resolve(transport, max_attempts=3)
    assert len(transport.calls) == 3  # bounded - no retry storm


def test_s5_network_failure_is_source_unavailable_with_sanitized_reason():
    """TransportFailure (DNS/TLS/network) drives the sanitizer path (G4
    finding 9): typed error, reason_kind network, bounded attempts."""
    transport = RecordingTransport(TransportFailure("dns failure\nCONSTRUCTED"))
    with pytest.raises(SourceUnavailableError) as excinfo:
        _resolve(transport, max_attempts=2)
    assert len(transport.calls) == 2
    detail = excinfo.value.detail
    assert detail.get("reason_kind") == "network"
    # The newline-bearing reason was repr()-sanitized: no detail value may
    # carry a literal newline (log-record splitting, G5 C1 class).
    assert not any(
        isinstance(v, str) and "\n" in v for v in detail.values()
    ), detail


@pytest.mark.parametrize("status", [401, 403], ids=["401", "403"])
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


@pytest.mark.parametrize("status", [302, 400, 404], ids=["302", "400", "404"])
def test_s5_unexpected_statuses_including_refused_redirects_fail_typed(status):
    """Refused 3xx redirects and other unexpected statuses (G4 finding 8):
    typed SourceUnavailableError, never AuthFailedError, never retried."""
    transport = RecordingTransport(TransportResponse(status, "CONSTRUCTED"))
    with pytest.raises(SourceUnavailableError) as excinfo:
        _resolve(transport)
    assert len(transport.calls) == 1
    assert excinfo.value.detail["http_status"] == status
    assert not isinstance(excinfo.value, AuthFailedError)


def test_s5_persistent_500_is_source_unavailable_after_budget():
    transport = RecordingTransport(TransportResponse(500, "oops"))
    with pytest.raises(SourceUnavailableError):
        _resolve(transport, max_attempts=2)
    assert len(transport.calls) == 2


def test_s5_persistent_429_is_rate_limited_with_bounded_attempts():
    transport = RecordingTransport(TransportResponse(429, "slow down"))
    with pytest.raises(RateLimitedError):
        _resolve(transport, max_attempts=2)
    assert len(transport.calls) == 2  # no retry storm on 429 either


def test_s5_retry_after_is_honored_on_429():
    """The jittered shared policy honors a parseable Retry-After within the
    cap (G1 finding 5): the sleep between 429 attempts is exactly the
    header's value, not the exponential fallback."""
    sleeps: list[float] = []
    transport = RecordingTransport(
        TransportResponse(429, "throttled", headers={"retry-after": "7"}),
        TransportResponse(200, _fixture_body(G01)),
    )
    res = _resolve(
        transport, max_attempts=3, sleep=sleeps.append, rng=Random(0)
    )
    assert res.status == "resolved"
    assert sleeps == [7.0]


def test_s5_request_budget_is_consumed_per_attempt_and_typed_on_exhaustion():
    """AnalysisBudget threading (G1 finding 9): one unit per attempt,
    consumed before I/O; exhaustion raises the typed budget error."""
    budget = AnalysisBudget(1, analysis_id="CONSTRUCTED-test")
    transport = RecordingTransport(TransportResponse(500, "oops"))
    with pytest.raises(RequestBudgetExceededError) as excinfo:
        _resolve(transport, max_attempts=3, budget=budget)
    assert len(transport.calls) == 1  # the second attempt was never paid for
    assert budget.consumed == 1
    assert excinfo.value.detail["analysis_id"] == "CONSTRUCTED-test"


@pytest.mark.parametrize(
    "body",
    [
        "this is not json",
        '{"weird": 1}',
        '{"address": "not a dict"}',
        "[]",
        # CONSTRUCTED hostile body, depth 600: json.loads's C scanner accepts
        # nesting this deep while pure-Python deepcopy/canonicalization blow
        # the recursion limit. Before the guard this ESCAPED as an untyped
        # RecursionError (G5 re-review N1); whichever layer breaks first on
        # a given interpreter, the outcome must be the typed error.
        '{"address": {"geosupportReturnCode": "00", '
        '"geosupportReturnCode2": "00", "a": ' + "[" * 600 + "]" * 600 + "}}",
    ],
    ids=["nonjson", "wrongkeys", "addressnotdict", "array", "deepnest600"],
)
def test_s5_malformed_200_bodies_fail_closed(body):
    with pytest.raises(MalformedResponseError):
        _resolve(RecordingTransport(TransportResponse(200, body)))


def test_s5_malformed_detail_is_bounded_and_body_value_free():
    """The malformed-shape diagnosis is capped and carries key NAMES only,
    never body values (G5 C3, G4 finding 13). CONSTRUCTED hostile body with
    60 keys."""
    hostile = json.dumps({f"k{i:03d}": "SECRET-VALUE" for i in range(60)})
    with pytest.raises(MalformedResponseError) as excinfo:
        _resolve(RecordingTransport(TransportResponse(200, hostile)))
    detail = excinfo.value.detail
    assert len(detail["top_level_keys"]) == 20
    assert detail["top_level_keys_truncated"] is True
    assert detail["top_level_key_count"] == 60
    assert "SECRET-VALUE" not in json.dumps(excinfo.value.to_payload())


def test_s5_invalid_input_raises_before_any_network_call():
    transport = RecordingTransport()
    with pytest.raises(InvalidInputError):
        resolve_address("", "w 100 st", borough="manhattan",
                        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep)
    with pytest.raises(InvalidInputError):
        resolve_address("314", "w 100 st",
                        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep)
    with pytest.raises(InvalidInputError):
        resolve_address("314", "w 100 st", borough="   ",
                        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep)
    assert transport.calls == []


@pytest.mark.parametrize(
    ("house_number", "street"),
    [(314, "w 100 st"), ("314", ["w", "100", "st"])],
    ids=["int-house-number", "list-street"],
)
def test_s5_non_string_input_is_typed_never_attribute_error(house_number, street):
    """G1 finding 2: a truthy non-string input must raise the typed
    InvalidInputError, never escape as AttributeError."""
    transport = RecordingTransport()
    with pytest.raises(InvalidInputError) as excinfo:
        resolve_address(house_number, street, borough="manhattan",
                        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep)
    assert excinfo.value.detail["received_type"] in ("int", "list")
    assert transport.calls == []


def test_s5_oversized_input_fails_closed_before_network():
    """G5 C4: length caps fail closed pre-I/O so oversized input can never
    inflate retry logs or error payloads."""
    transport = RecordingTransport()
    huge_street = "w " + "x" * MAX_STREET_CHARS
    with pytest.raises(InvalidInputError) as excinfo:
        resolve_address("314", huge_street, borough="manhattan",
                        key=SENTINEL_KEY, transport=transport, sleep=_no_sleep)
    assert excinfo.value.detail["max_chars"] == MAX_STREET_CHARS
    assert huge_street not in str(excinfo.value)  # value never echoed
    assert transport.calls == []


# ===========================================================================
# S6 - key hygiene.
# ===========================================================================

def test_s6_sentinel_never_leaks_from_any_path(caplog):
    """Success, ambiguity, rejection, and the 401/403/429/500/timeout/
    network/malformed failure paths, all exercised with the sentinel key.
    POSITIVE CONTROL first (G4 finding 4): every harvested run must have
    actually sent the sentinel in the auth header, every failure path must
    actually raise, and log records must actually be captured — only then
    does leak absence mean anything."""
    caplog.set_level(logging.DEBUG, logger="app.connectors.geoclient_address")
    harvested: list[str] = []
    transports: list[RecordingTransport] = []

    for body_name in (G01, G02, G03):
        transport = RecordingTransport(
            TransportResponse(200, _fixture_body(body_name))
        )
        transports.append(transport)
        res = _resolve(transport)
        harvested.append(json.dumps(asdict(res)))
        harvested.append(repr(res))

    failures = [
        TransportResponse(401, "no"),
        TransportResponse(403, "no"),
        TransportResponse(429, "slow"),
        TransportResponse(500, "oops"),
        TransportTimeout("t"),
        TransportFailure("dns CONSTRUCTED"),
        TransportResponse(200, "not json"),
    ]
    for failure in failures:
        transport = RecordingTransport(failure)
        transports.append(transport)
        try:
            _resolve(transport, max_attempts=2)
        except GeoclientConnectorError as err:
            harvested.append(str(err))
            harvested.append(json.dumps(err.to_payload()))
        else:  # pragma: no cover - the failure path must fail
            pytest.fail(f"failure outcome {failure!r} did not raise")

    # Typed pre-network errors are part of the leak surface too.
    for exc_check in (
        lambda: resolve_address("314", "w 100 st", borough="manhattan",
                                env={}, sleep=_no_sleep),
        lambda: resolve_address(314, "w 100 st", borough="manhattan",
                                key=SENTINEL_KEY, sleep=_no_sleep),
    ):
        try:
            exc_check()
        except GeoclientConnectorError as err:
            harvested.append(str(err))
            harvested.append(json.dumps(err.to_payload()))
        else:  # pragma: no cover
            pytest.fail("pre-network error path did not raise")

    # Positive controls.
    assert transports and all(t.calls for t in transports)
    for transport in transports:
        for _url, headers, _timeout in transport.calls:
            assert headers[KEY_HEADER] == SENTINEL_KEY
    assert caplog.records  # the log half of the sweep captured something

    harvested.append(caplog.text)  # names, levels and exc_text included
    assert SENTINEL_KEY not in "".join(harvested)


def test_s6_key_is_read_from_the_real_environment_at_call_time(monkeypatch):
    """The os.environ production branch itself (G4 finding 2, G1 finding 3):
    env defaults to the process environment, read AT CALL TIME — a changed
    variable is picked up by the next call with no re-import."""
    transport = RecordingTransport(
        TransportResponse(200, _fixture_body(G01)),
        TransportResponse(200, _fixture_body(G01)),
    )
    monkeypatch.setenv(KEY_ENV_VAR, SENTINEL_KEY)
    resolve_address("314", "w 100 st", borough="manhattan",
                    transport=transport, sleep=_no_sleep)
    second_key = SENTINEL_KEY + "-rotated"
    monkeypatch.setenv(KEY_ENV_VAR, second_key)
    resolve_address("314", "w 100 st", borough="manhattan",
                    transport=transport, sleep=_no_sleep)
    (first_call, second_call) = transport.calls
    assert first_call[1][KEY_HEADER] == SENTINEL_KEY
    assert second_call[1][KEY_HEADER] == second_key
    assert SENTINEL_KEY not in first_call[0]


def test_s6_injected_env_mapping_is_honored():
    transport = RecordingTransport(TransportResponse(200, _fixture_body(G01)))
    resolve_address("314", "w 100 st", borough="manhattan",
                    transport=transport, sleep=_no_sleep,
                    env={KEY_ENV_VAR: SENTINEL_KEY})
    (url, headers, _timeout), = transport.calls
    assert headers[KEY_HEADER] == SENTINEL_KEY
    assert SENTINEL_KEY not in url


def test_s6_missing_key_is_typed_and_attempts_no_network():
    transport = RecordingTransport()
    with pytest.raises(KeyMissingError) as excinfo:
        resolve_address("314", "w 100 st", borough="manhattan",
                        transport=transport, sleep=_no_sleep, env={})
    assert transport.calls == []
    payload = excinfo.value.to_payload()
    assert payload["detail"]["env_var"] == KEY_ENV_VAR


def test_s6_explicit_empty_key_never_falls_back_to_environment():
    """key='' is an explicit (bad) key, not an invitation to read the
    environment (G1 finding 14): typed KeyMissingError even when a valid
    key sits in the env mapping."""
    transport = RecordingTransport()
    with pytest.raises(KeyMissingError):
        resolve_address("314", "w 100 st", borough="manhattan",
                        key="   ", transport=transport, sleep=_no_sleep,
                        env={KEY_ENV_VAR: SENTINEL_KEY})
    assert transport.calls == []


# ===========================================================================
# S7 - offline discipline and fixture integrity.
# ===========================================================================

@pytest.mark.parametrize("name", [G01, G02, G03], ids=["G01", "G02", "G03"])
def test_s7_fixture_digest_matches_stored_sha256(name):
    fixture = _fixture(name)
    actual = hashlib.sha256(fixture["response_body_raw"].encode("utf-8")).hexdigest()
    assert actual == fixture["response_sha256"], f"fixture drift in {name}"


@pytest.mark.parametrize("name", [G01, G02, G03], ids=["G01", "G02", "G03"])
def test_s7_fixture_request_urls_are_key_free(name):
    fixture = _fixture(name)
    assert KEY_HEADER not in fixture["request_url"]
    assert "key=" not in fixture["request_url"].lower()


def test_s7_key_check_precedes_any_transport_use(monkeypatch):
    """With no key available, the DEFAULT transport is never invoked: the
    typed KeyMissingError fires before any network object is touched."""
    import app.connectors.geoclient_address as mod

    def _boom(*_args, **_kwargs):  # pragma: no cover - must never run
        raise AssertionError("network transport was invoked")

    monkeypatch.setattr(mod, "urllib_transport", _boom)
    with pytest.raises(KeyMissingError):
        resolve_address("314", "w 100 st", borough="manhattan", env={})


# ===========================================================================
# S8 - transport honesty: null omission, unknown GRC fail-closed, verbatim
# types, and the provenance contract on every status.
# ===========================================================================

@pytest.mark.parametrize(
    "absent_field", ["zipCode", "bbl", "buildingIdentificationNumber", "latitude"],
    ids=["zip", "bbl", "bin", "latitude"],
)
def test_s8_absent_fields_are_none_never_fabricated(absent_field):
    """CONSTRUCTED absence (null omission) for each canonical field class."""
    body = _g01_variant(_remove=(absent_field,))
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    attr = {
        "zipCode": "zip_code",
        "bbl": "bbl",
        "buildingIdentificationNumber": "bin",
        "latitude": "latitude",
    }[absent_field]
    assert getattr(res, attr) is None
    assert res.status == "resolved"  # absence of an attribute is not an error


def test_s8_empty_string_source_value_is_preserved_not_reinterpreted():
    """An empty-string SOURCE VALUE is data, not absence (G3 finding 6) —
    the mirror image of the fabrication rule. CONSTRUCTED variant."""
    body = _g01_variant(zipCode="")
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.zip_code == ""


@pytest.mark.parametrize(
    ("field_name", "hostile_value", "attr"),
    [
        ("bbl", 1018887502, "bbl"),
        ("latitude", "40.798178", "latitude"),
        ("latitude", True, "latitude"),
    ],
    ids=["numeric-bbl", "string-latitude", "bool-latitude"],
)
def test_s8_type_drift_is_never_coerced(field_name, hostile_value, attr):
    """The PLUTO decimal-BBL lesson (G4 finding 12): a source type change is
    never silently coerced — the canonical field goes None (documented
    fail-safe) while raw_fields preserves the drifted value verbatim for
    inspection. CONSTRUCTED variants."""
    body = _g01_variant(**{field_name: hostile_value})
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert getattr(res, attr) is None
    assert res.raw_fields[field_name] == hostile_value


def test_s8_integer_coordinate_stays_int():
    """Verbatim number transport: a JSON integer coordinate stays int —
    no float() coercion (G4 finding 12). CONSTRUCTED variant."""
    body = _g01_variant(latitude=40)
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.latitude == 40 and type(res.latitude) is int


@pytest.mark.parametrize("side", ["geosupportReturnCode", "geosupportReturnCode2"],
                         ids=["side1", "side2"])
@pytest.mark.parametrize("bad", ["ZZZ", "", "0", "0x", "00\n", None],
                         ids=["threechars", "empty", "onechar", "badchar",
                              "trailing-newline", "absent"])
def test_s8_invalid_shape_grc_fails_closed_on_either_side(side, bad):
    """CONSTRUCTED variants: shape-invalid or absent codes on EITHER
    sub-call side (G4 finding 11) — including the trailing-newline case the
    old $-anchored regex admitted (G1 finding 12) — are unrecognized_status,
    never success."""
    if bad is None:
        body = _g01_variant(_remove=(side,))
    else:
        body = _g01_variant(**{side: bad})
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == "unrecognized_status"


def test_s8_identifiers_stay_verbatim_strings():
    addr = _fixture_address(G01)
    res = _resolve(RecordingTransport(TransportResponse(200, _fixture_body(G01))))
    assert res.bbl == addr["bbl"] and type(res.bbl) is str
    assert res.raw_fields["bbl"] == addr["bbl"] and type(res.raw_fields["bbl"]) is str


def _status_bodies() -> list[tuple[str, str]]:
    """One response body per outcome status (recorded where one exists,
    CONSTRUCTED variants of G01 otherwise)."""
    return [
        ("resolved", _fixture_body(G01)),
        ("resolved_with_warnings", _g01_variant(geosupportReturnCode2="01")),
        ("ambiguous", _fixture_body(G02)),
        ("not_found", _g01_variant(geosupportReturnCode="11",
                                   geosupportReturnCode2="11")),
        ("rejected", _fixture_body(G03)),
        ("unrecognized_status", _g01_variant(_remove=("geosupportReturnCode",))),
    ]


def test_s8_every_status_is_reachable_and_the_status_set_is_closed():
    """RESOLUTION_STATUSES is the exhaustive contract (G1 finding 8): every
    member is produced by some response, and no response produces anything
    outside it."""
    seen = set()
    for expected, body in _status_bodies():
        res = _resolve(RecordingTransport(TransportResponse(200, body)))
        assert res.status == expected
        seen.add(res.status)
    assert seen == set(RESOLUTION_STATUSES)


@pytest.mark.parametrize(
    ("expected_status", "body"), _status_bodies(),
    ids=[s for s, _ in _status_bodies()],
)
def test_s8_provenance_is_complete_on_every_status(expected_status, body):
    """The packet's 'every outcome' provenance clause, asserted on all six
    statuses (G3 finding 7), including the unrecognized case where the GRC
    provenance fields are None rather than absent."""
    res = _resolve(RecordingTransport(TransportResponse(200, body)))
    assert res.status == expected_status
    prov = res.provenance
    for required in (
        "source_id", "endpoint", "request_params", "retrieved_at",
        "http_status", "response_digest", "digest_canonicalization",
        "correlation_id",
    ):
        assert required in prov, required
    assert "geosupport_return_code" in prov
    assert "geosupport_return_code2" in prov
    assert prov["response_digest"] == canonical_json_digest(json.loads(body))
    assert SENTINEL_KEY not in json.dumps(prov)


def test_s8_retrieved_at_comes_from_the_injected_clock():
    """The clock seam (G1 finding 6): retrieved_at is the injected clock's
    value, not an unverifiable wall read."""
    frozen = datetime(2026, 9, 11, 12, 34, 56, tzinfo=UTC)
    res = _resolve(
        RecordingTransport(TransportResponse(200, _fixture_body(G01))),
        clock=lambda: frozen,
    )
    assert res.provenance["retrieved_at"] == "2026-09-11T12:34:56Z"
