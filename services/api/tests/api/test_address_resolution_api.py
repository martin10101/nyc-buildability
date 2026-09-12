"""M2-T022 acceptance pack: GET /api/v1/address-resolution (S1-S8).

Offline end to end: every request runs the REAL connector
(``resolve_address``) over a FakeTransport replaying the RECORDED Geoclient
fixtures (G01 resolved / G02 ambiguous / G03 rejected) with a sentinel key -
the endpoint's resolver seam is dependency-overridden, the connector itself is
not mocked, so the pack proves the endpoint against the connector's true
contract. Failure paths are driven by resolvers raising the connector's own
typed errors (constructed directly, positive-controlled). A module-wide socket
guard makes real network I/O mechanically impossible.

Anti-tautology discipline (M5-T004 lesson): every expected value is LOADED
from the fixture (or recomputed, e.g. digests), never restated as a literal;
the source_fact records are validated against the REAL
packages/contracts/schemas/v1/source_fact.schema.json via jsonschema - the
consumability proof MVP_AGENDA C4 owes.
"""

from __future__ import annotations

import http.client
import json
import socket
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from app.api.v1 import address_resolution as address_resolution_module
from app.api.v1.address_resolution import (
    ADDRESS_RESOLUTION_CONTRACT_VERSION,
    DATASET_VERSION,
    STATUS_STATE_MATRIX,
    get_address_resolver,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.geoclient_address import (
    AuthFailedError,
    KeyMissingError,
    MalformedResponseError,
    RateLimitedError,
    SourceTimeoutError,
    SourceUnavailableError,
    resolve_address,
)
from app.connectors.pluto_soda import canonical_json_digest
from app.main import app
from app.resilience.transport import TransportResponse

# test file: <root>/services/api/tests/api/test_address_resolution_api.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "geoclient"
SCHEMA_DIR = _REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"

G01 = "G01_address_documented_example.json"
G02 = "G02_address_ambiguous_ee.json"
G03 = "G03_address_rejected_42.json"

URL = "/api/v1/address-resolution"
SENTINEL_KEY = "TEST-SENTINEL-KEY-OBVIOUSLY-FAKE"  # words only: never key-shaped


def _no_sleep(_seconds: float) -> None:
    return None


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Mechanical no-network guard at the EGRESS SEAMS (evidence-pack pattern:
    blocking socket CONSTRUCTION deadlocks the anyio portal the TestClient
    drives the app through, so egress is blocked where it actually happens -
    http.client's connect choke points and socket.create_connection)."""

    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in an offline test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def enable_flag(monkeypatch) -> None:
    # Reuses the rule-evaluation flag (address entry is the same internal
    # property flow's entry step; app.config is out of the packet's scope).
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_address(name: str) -> dict:
    return json.loads(load_fixture(name)["response_body_raw"])["address"]


class RecordingTransport:
    """Replays scripted TransportResponses; records (url, headers) per call."""

    def __init__(self, *script):
        self.script = list(script)
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append((url, dict(headers)))
        if not self.script:
            raise AssertionError("RecordingTransport script exhausted")
        return self.script.pop(0)


def install_resolver_for_body(body: str, status: int = 200):
    """Override the endpoint's resolver seam with the REAL connector over a
    fixture-replaying transport + sentinel key. Returns (transport, calls)."""
    transport = RecordingTransport(TransportResponse(status, body))
    calls: list[dict] = []

    def _resolver(house_number, street, *, borough=None, zip_code=None, **kwargs):
        calls.append(
            {
                "house_number": house_number,
                "street": street,
                "borough": borough,
                "zip_code": zip_code,
                "extra_kwargs": dict(kwargs),
            }
        )
        return resolve_address(
            house_number,
            street,
            borough=borough,
            zip_code=zip_code,
            key=SENTINEL_KEY,
            transport=transport,
            sleep=_no_sleep,
        )

    app.dependency_overrides[get_address_resolver] = lambda: _resolver
    return transport, calls


def install_raising_resolver(exc: Exception):
    raised: list[Exception] = []

    def _resolver(*_args, **_kwargs):
        raised.append(exc)
        raise exc

    app.dependency_overrides[get_address_resolver] = lambda: _resolver
    return raised


def _fact_validator() -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / "source_fact.schema.json").read_text("utf-8"))
    common = json.loads((SCHEMA_DIR / "common.schema.json").read_text("utf-8"))
    common_uri = schema["$id"].rsplit("/", 1)[0] + "/common.schema.json"
    registry = Registry().with_resources(
        [
            (schema["$id"], Resource.from_contents(schema)),
            (common_uri, Resource.from_contents(common)),
            ("common.schema.json", Resource.from_contents(common)),
        ]
    )
    return Draft202012Validator(schema, registry=registry)


def _g02_variant(**message_overrides) -> str:
    """CONSTRUCTED variant (clearly labeled): the recorded G02 body with named
    address fields replaced - used for the hostile reflected-text case."""
    parsed = json.loads(load_fixture(G02)["response_body_raw"])
    parsed["address"].update(message_overrides)
    return json.dumps(parsed)


def _g01_variant(**field_overrides) -> str:
    """CONSTRUCTED variant (clearly labeled) of the recorded G01 body."""
    parsed = json.loads(load_fixture(G01)["response_body_raw"])
    parsed["address"].update(field_overrides)
    return json.dumps(parsed)


# ---------------------------------------------------------------------------
# S1 - resolved end to end: fixture-anchored values + source_fact consumability.
# ---------------------------------------------------------------------------


def test_s1_resolved_transports_fixture_values_and_valid_source_facts(
    client, monkeypatch
):
    enable_flag(monkeypatch)
    fixture = load_fixture(G01)
    addr = fixture_address(G01)
    transport, calls = install_resolver_for_body(fixture["response_body_raw"])

    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc["contract_version"] == ADDRESS_RESOLUTION_CONTRACT_VERSION
    assert doc["document_kind"] == "address_resolution"
    assert doc["status"] == "resolved"
    # Correlation: header == body (HTTP-level id); the connector's own id is
    # distinct and travels in provenance.
    assert response.headers["X-Correlation-ID"] == doc["correlation_id"]
    assert doc["provenance"]["correlation_id"] != doc["correlation_id"]

    # Canonical fields equal values LOADED FROM THE FIXTURE (never literals).
    canonical = doc["canonical"]
    assert canonical["bbl"] == addr["bbl"]
    assert canonical["bin"] == addr["buildingIdentificationNumber"]
    assert canonical["street_name_normalized"] == addr["firstStreetNameNormalized"]
    assert canonical["borough_name"] == addr["firstBoroughName"]
    assert canonical["zip_code"] == addr["zipCode"]
    assert canonical["latitude"] == addr["latitude"]
    assert canonical["longitude"] == addr["longitude"]
    assert doc["grc"] == addr["geosupportReturnCode"]
    assert doc["grc2"] == addr["geosupportReturnCode2"]

    # source_facts: one per provided canonical field, each VALIDATING against
    # the real source_fact schema (the C4 consumability proof), values
    # byte-equal to the outcome fields.
    facts = doc["source_facts"]
    assert facts, "a resolved outcome must emit source facts"
    validator = _fact_validator()
    for fact in facts:
        errors = list(validator.iter_errors(fact))
        assert errors == [], [e.message for e in errors]
        assert fact["dataset_version"] == DATASET_VERSION
        assert fact["bbl"] == addr["bbl"]
        assert fact["normalized_value"] is not None
        # Transport-never-interpret: original == normalized for this connector.
        assert fact["original_value"] == fact["normalized_value"]
        assert fact["value_digest"] == canonical_json_digest(fact["original_value"])
        assert fact["response_digest"] == doc["provenance"]["response_digest"]
    by_field = {f["original_field_name"]: f for f in facts}
    assert by_field["bbl"]["normalized_value"] == addr["bbl"]
    assert by_field["buildingIdentificationNumber"]["normalized_value"] == (
        addr["buildingIdentificationNumber"]
    )
    assert "source_facts_not_emitted_reason" not in doc

    # The connector really ran: one transport call, sentinel in the header
    # (positive control), key-free URL.
    assert len(calls) == 1 and len(transport.calls) == 1
    called_url, called_headers = transport.calls[0]
    assert SENTINEL_KEY in called_headers.values().__str__()
    assert SENTINEL_KEY not in called_url
    # The route passed no extra kwargs to the resolver seam (S8 overlap).
    assert calls[0]["extra_kwargs"] == {}


def test_s1_production_wiring_default_resolver_reaches_the_connector(
    client, monkeypatch
):
    """G1 HIGH-1 regression pin: the REAL get_address_resolver() dependency (NO
    override) must accept the route's positional call and reach
    resolve_address. The module-global resolve_address is monkeypatched with a
    recorder that drives the real connector over the fixture transport, so
    production wiring (route -> _default_resolver -> resolve_address) is
    exercised end to end. Before the rework this returned 500 on EVERY real
    request (the **kwargs-only default rejected the positional call), masked
    because every override accepted positionals."""
    enable_flag(monkeypatch)
    app.dependency_overrides.clear()  # PRODUCTION wiring - no seam override
    fixture_body = load_fixture(G01)["response_body_raw"]
    transport = RecordingTransport(TransportResponse(200, fixture_body))
    recorded: dict = {}

    def _recording_resolve_address(
        house_number, street, *, borough=None, zip_code=None, **kwargs
    ):
        recorded.update(
            house_number=house_number,
            street=street,
            borough=borough,
            zip_code=zip_code,
            extra=dict(kwargs),
        )
        return resolve_address(
            house_number, street, borough=borough, zip_code=zip_code,
            key=SENTINEL_KEY, transport=transport, sleep=_no_sleep,
        )

    monkeypatch.setattr(
        address_resolution_module, "resolve_address", _recording_resolve_address
    )
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    # The default resolver forwarded the route's inputs faithfully and added
    # NOTHING (no budget, no transport - C4 duty 3 at the production seam).
    assert recorded["house_number"] == "314"
    assert recorded["street"] == "w 100 st"
    assert recorded["borough"] == "manhattan"
    assert recorded["zip_code"] is None
    assert recorded["extra"] == {}
    assert len(transport.calls) == 1


# ---------------------------------------------------------------------------
# S2 - ambiguity surfaces suggestions verbatim; never selects; no facts.
# ---------------------------------------------------------------------------


def test_s2_ambiguous_surfaces_suggestions_never_selects(client, monkeypatch):
    enable_flag(monkeypatch)
    fixture = load_fixture(G02)
    install_resolver_for_body(fixture["response_body_raw"])

    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 stt", "borough": "manhattan"}
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "ambiguous"
    assert doc["selection_policy"] == "caller_selects"
    assert doc["source_facts"] == []
    assert doc["canonical"]["bbl"] is None  # nothing fabricated

    # Suggestions verbatim from the recorded body, in source slot order,
    # reconstructed in the CONNECTOR's documented shape (street_name +
    # optional street_code; no slot field) so the endpoint's transport is
    # compared against the fixture, never against itself.
    addr = fixture_address(G02)
    slots = []
    for index in range(1, 33):
        name = addr.get(f"streetName{index}")
        if isinstance(name, str) and name:
            entry = {"street_name": name}
            code = addr.get(f"streetCode{index}")
            if code is not None:
                entry["street_code"] = code
            slots.append(entry)
    assert doc["suggestions"] == slots
    assert slots, "the recorded EE fixture must carry at least one suggestion"


# ---------------------------------------------------------------------------
# S3 - rejected / not_found are VISIBLE 200 outcomes with both GRCs.
# ---------------------------------------------------------------------------


def test_s3_rejected_is_visible_with_partial_fields(client, monkeypatch):
    enable_flag(monkeypatch)
    fixture = load_fixture(G03)
    addr = fixture_address(G03)
    install_resolver_for_body(fixture["response_body_raw"])

    response = client.get(
        URL, params={"house_number": "999999", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "rejected"
    assert doc["grc"] == addr["geosupportReturnCode"]
    assert doc["grc2"] == addr["geosupportReturnCode2"]
    assert doc["grc_message"] == addr.get("message")
    # Partial fields transport per the connector contract (populated on
    # non-resolved statuses; consumers branch on status, never presence).
    assert doc["canonical"]["street_name_normalized"] == (
        addr.get("firstStreetNameNormalized")
    )
    assert doc["source_facts"] == []


def test_s3_constructed_not_found_is_visible(client, monkeypatch):
    enable_flag(monkeypatch)
    # CONSTRUCTED variant: both sub-calls 11 (not recognized, no suggestions).
    body = _g01_variant(
        geosupportReturnCode="11", geosupportReturnCode2="11", bbl=None
    )
    install_resolver_for_body(body)
    response = client.get(
        URL, params={"house_number": "314", "street": "nowhere st", "borough": "manhattan"}
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "not_found"
    assert doc["source_facts"] == []


# ---------------------------------------------------------------------------
# S4 - typed failure mapping: exact matrix, bounded payloads, key-free, with
# the local Retry-After guard.
# ---------------------------------------------------------------------------

_FAILURES = [
    (
        "key_missing",
        503,
        # Typed-error construction: "key missing" is the taxonomy name; no
        # credential exists on this line.
        KeyMissingError("no key available", correlation_id="c-km"),  # gitleaks:allow
    ),
    (
        "auth_failed",
        502,
        AuthFailedError(
            "gateway rejected the subscription key",
            correlation_id="c-af",
            detail={
                "http_status": 401,
                "url": "https://api.nyc.gov/geoclient/v2/address?houseNumber=314",
            },
        ),
    ),
    (
        "rate_limited",
        503,
        RateLimitedError(
            "rate limited after bounded retries",
            correlation_id="c-rl",
            detail={"retry_after": "7", "attempts": 3},
        ),
    ),
    (
        "source_unavailable",
        503,
        SourceUnavailableError("upstream 500 after retries", correlation_id="c-su"),
    ),
    ("timeout", 504, SourceTimeoutError("timed out after retries", correlation_id="c-to")),
    (
        "malformed_response",
        502,
        MalformedResponseError("200 outside the documented shape", correlation_id="c-mr"),
    ),
]


@pytest.mark.parametrize(
    ("state", "status_code", "exc"),
    _FAILURES,
    ids=[f[0] for f in _FAILURES],
)
def test_s4_typed_failures_map_to_documented_pairs(
    client, monkeypatch, caplog, state, status_code, exc
):
    enable_flag(monkeypatch)
    raised = install_raising_resolver(exc)
    with caplog.at_level("DEBUG"):
        response = client.get(
            URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
        )
    assert raised, "positive control: the failure path must actually raise"
    assert response.status_code == status_code
    doc = response.json()
    assert doc["state"] == state
    assert doc["error"]["error_type"] == state
    assert (status_code, state) in STATUS_STATE_MATRIX
    assert response.headers["X-Correlation-ID"] == doc["correlation_id"]
    # Bounded + key-free (the sentinel never entered these constructed errors,
    # so this asserts the endpoint added nothing secret-shaped of its own; the
    # full sentinel harvest is test_s4_leak_absence_harvest).
    assert len(response.content) < 4096
    assert "Ocp-Apim" not in response.text


def test_s4_invalid_input_is_422_via_the_connector_validator(client, monkeypatch):
    enable_flag(monkeypatch)
    transport, _calls = install_resolver_for_body(load_fixture(G01)["response_body_raw"])
    # Empty house_number: the CONNECTOR is the single validation authority.
    response = client.get(URL, params={"house_number": "", "street": "w 100 st", "borough": "m"})
    assert response.status_code == 422
    doc = response.json()
    assert doc["state"] == "invalid_input"
    assert (422, "invalid_input") in STATUS_STATE_MATRIX
    assert transport.calls == []  # rejected before any transport use


@pytest.mark.parametrize(
    "hostile",
    ["7\n", "Fri, 17 Jul 2026 08:00:00 GMT\n", "x" * 200, 7],
    ids=["trailing-newline", "date-with-newline", "oversized", "non-string"],
)
def test_s4_hostile_retry_after_is_dropped_never_echoed(client, monkeypatch, hostile):
    """The local C4 guard: a retry_after that fails the conservative
    fullmatch/length bound is DROPPED from the response entirely."""
    enable_flag(monkeypatch)
    install_raising_resolver(
        RateLimitedError("rate limited", correlation_id="c-rl2", detail={"retry_after": hostile})
    )
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 503
    assert "retry_after" not in response.json()["error"]
    assert "\n7" not in response.text and "GMT" not in response.text


def test_s4_wellformed_retry_after_is_surfaced_bounded(client, monkeypatch):
    enable_flag(monkeypatch)
    install_raising_resolver(
        RateLimitedError("rate limited", correlation_id="c-rl3", detail={"retry_after": "7"})
    )
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.json()["error"]["retry_after"] == "7"


def test_s4_leak_absence_harvest(client, monkeypatch, caplog):
    """The sentinel key appears in NO response body and NO log line across the
    success path and a real auth-failure path driven through the REAL
    connector (positive controls: transport called with the sentinel header;
    the failure actually raised; log records captured)."""
    enable_flag(monkeypatch)
    responses = []
    with caplog.at_level("DEBUG"):
        params = {"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
        # Success path through the real connector.
        transport_ok, _ = install_resolver_for_body(load_fixture(G01)["response_body_raw"])
        responses.append(client.get(URL, params=params))
        # Auth-failure path through the real connector (upstream 401).
        transport_401, _ = install_resolver_for_body(
            json.dumps({"detail": "gateway says no"}), status=401
        )
        responses.append(client.get(URL, params=params))
    assert [r.status_code for r in responses] == [200, 502]
    # Positive controls.
    assert transport_ok.calls and transport_401.calls
    for _url, headers in transport_ok.calls + transport_401.calls:
        assert SENTINEL_KEY in list(headers.values())
    assert caplog.records
    # The harvest itself.
    combined = "||".join(r.text for r in responses) + "||" + caplog.text
    assert SENTINEL_KEY not in combined
    assert "gateway says no" not in combined  # upstream body never passes through


# ---------------------------------------------------------------------------
# S5 - flag-gated internal-only.
# ---------------------------------------------------------------------------


def test_s5_flag_unset_is_a_generic_404_without_correlation(client, monkeypatch):
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    response = client.get(URL, params={"house_number": "314", "street": "w 100 st"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in response.headers


def test_s5_flag_set_serves(client, monkeypatch):
    enable_flag(monkeypatch)
    install_resolver_for_body(load_fixture(G01)["response_body_raw"])
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# S6 - reflected text transports verbatim + the machine-readable warning.
# ---------------------------------------------------------------------------


def test_s6_recorded_reflected_message_travels_verbatim(client, monkeypatch):
    enable_flag(monkeypatch)
    fixture = load_fixture(G02)
    addr = fixture_address(G02)
    install_resolver_for_body(fixture["response_body_raw"])
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 stt", "borough": "manhattan"}
    )
    doc = response.json()
    assert doc["grc_message"] == addr.get("message")  # fixture-loaded, verbatim
    warning = doc["unsanitized_reflected_input"]
    assert "grc_message" in warning["fields"]
    assert "suggestions" in warning["fields"]
    assert "escape on render" in warning["warning"]


def test_s6_input_echo_is_a_named_reflected_surface(client, monkeypatch):
    """G3 rework pin: input_echo transports raw caller-typed input verbatim
    and MUST be named in the machine-readable escape contract - a consumer
    escaping exactly the listed fields must be safe. The source_facts values
    that carry the same reflected source text are named too."""
    enable_flag(monkeypatch)
    hostile = "<script>alert(1)</script>"
    install_resolver_for_body(load_fixture(G01)["response_body_raw"])
    response = client.get(
        URL, params={"house_number": "7<b>7", "street": hostile, "borough": "manhattan"}
    )
    doc = response.json()
    assert doc["input_echo"]["street"] == hostile  # byte-exact reflection
    assert doc["input_echo"]["house_number"] == "7<b>7"
    fields = doc["unsanitized_reflected_input"]["fields"]
    assert "input_echo" in fields
    assert any(field.startswith("source_facts[]") for field in fields)


def test_s6_hostile_reflected_text_arrives_byte_exact_and_never_logged(
    client, monkeypatch, caplog
):
    enable_flag(monkeypatch)
    hostile = "<script>alert('314 w 100 st')</script>"
    body = _g02_variant(message=hostile)  # CONSTRUCTED variant, clearly labeled
    install_resolver_for_body(body)
    with caplog.at_level("DEBUG"):
        response = client.get(
            URL, params={"house_number": "314", "street": "w 100 stt", "borough": "manhattan"}
        )
    doc = response.json()
    assert doc["grc_message"] == hostile  # transported verbatim (JSON-encoded)
    assert hostile not in caplog.text  # never a log line
    assert hostile not in "".join(f"{k}{v}" for k, v in response.headers.items())


# ---------------------------------------------------------------------------
# S7 - offline, stateless, per-request correlation.
# ---------------------------------------------------------------------------


def test_s7_two_identical_requests_are_two_connector_calls(client, monkeypatch):
    enable_flag(monkeypatch)
    fixture_body = load_fixture(G01)["response_body_raw"]
    transport = RecordingTransport(
        TransportResponse(200, fixture_body), TransportResponse(200, fixture_body)
    )

    def _resolver(house_number, street, *, borough=None, zip_code=None, **_kwargs):
        return resolve_address(
            house_number, street, borough=borough, zip_code=zip_code,
            key=SENTINEL_KEY, transport=transport, sleep=_no_sleep,
        )

    app.dependency_overrides[get_address_resolver] = lambda: _resolver
    params = {"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    first = client.get(URL, params=params)
    second = client.get(URL, params=params)
    assert len(transport.calls) == 2  # no cache, no state
    assert (
        first.headers["X-Correlation-ID"] != second.headers["X-Correlation-ID"]
    )
    assert (
        first.json()["provenance"]["correlation_id"]
        != second.json()["provenance"]["correlation_id"]
    )


# ---------------------------------------------------------------------------
# S8 - no request-derived budget, pinned at the seam and in source.
# ---------------------------------------------------------------------------


def test_s8_route_passes_no_budget_and_constructs_none(client, monkeypatch):
    enable_flag(monkeypatch)
    _transport, calls = install_resolver_for_body(load_fixture(G01)["response_body_raw"])
    client.get(URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"})
    assert calls and calls[0]["extra_kwargs"] == {}  # no budget=, no transport=

    from app.api.v1 import address_resolution as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "AnalysisBudget(" not in source  # never constructed
    assert "budget=" not in source  # never passed


# ---------------------------------------------------------------------------
# Matrix exhaustiveness: every pair this pack drives is documented, and every
# documented pair is drivable (200 outcomes + 7 error states + internal 500).
# ---------------------------------------------------------------------------


def test_matrix_internal_error_pair_via_unexpected_exception(client, monkeypatch):
    enable_flag(monkeypatch)
    install_raising_resolver(RuntimeError("boom - not a connector error"))
    response = client.get(
        URL, params={"house_number": "314", "street": "w 100 st", "borough": "manhattan"}
    )
    assert response.status_code == 500
    doc = response.json()
    assert doc["state"] == "internal_error"
    assert (500, "internal_error") in STATUS_STATE_MATRIX
    assert "boom" not in response.text  # untyped internals never leak


def test_matrix_documented_pairs_are_exactly_the_emitted_set():
    emitted = {
        (200, None),
        (422, "invalid_input"),
        (503, "key_missing"),
        (502, "auth_failed"),
        (503, "rate_limited"),
        (503, "source_unavailable"),
        (504, "timeout"),
        (502, "malformed_response"),
        # Unreachable by construction (no budget is ever passed - S8) but
        # documented: the connector-error handler WOULD emit it at the default
        # 503 if a budget were ever introduced (G1 LOW-1).
        (503, "request_budget_exceeded"),
        (500, "internal_error"),
    }
    assert emitted == set(STATUS_STATE_MATRIX)
