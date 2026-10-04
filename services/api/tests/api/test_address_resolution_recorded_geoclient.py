"""D-090-R124 (Lane C W1-08): prove the REAL address->BBL path on RECORDED
official data.

The 2026-10-04 component-chain walkthrough drove the address step through a
SYNTHETIC harness resolver (``fixture_api.harness_address_resolver``), so it did
not exercise the real Geoclient connector at all. This pack closes that gap: it
runs the production, flag-gated route ``GET /api/v1/address-resolution``
(mounted in ``app.main``) over the REAL connector ``resolve_address``, bound to
a URL-KEYED fake transport that serves the RECORDED official Geoclient capture
bodies (G01/G02/G03) ONLY for the exact request_url each was captured with. The
only test-process concessions are the existing dependency-override seam, the
existing ``INTERNAL_RULE_EVAL_ENABLED`` flag enabled for this process, and a
DUMMY subscription key set in the test environment. Route, connector, parse,
classification, provenance and source-fact mapping are the production code
paths; no response byte is hand-written.

G01 is the Geoclient User Guide DOCUMENTED EXAMPLE address (314 W 100 St,
Manhattan -> BBL 1018887502), NOT the 215-16 Northern benchmark lot.

HARD LIMIT (Tier D, stated in the module docstring and the producer report):
recording the real Geoclient response for 215-16 Northern Boulevard needs the
GEOCLIENT_SUBSCRIPTION_KEY, which only the owner holds. Until the owner records
that capture, the real address->BBL path is proven here on the documented
example, and the benchmark journey still enters by BBL (not by address). This
module NEVER reads, requires, or prints the real key - the recorded path runs on
a dummy key injected only in the test environment.

Anti-tautology discipline (the M5-T004 lesson): every expected value - the
request inputs, the canonical fields, the request url - is LOADED FROM THE
FIXTURE (or derived by the real connector over the recorded body), never
restated as a literal.
"""

from __future__ import annotations

import http.client
import json
import socket
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from app.api.v1.address_resolution import get_address_resolver
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.geoclient_address import (
    KEY_ENV_VAR,
    KEY_HEADER,
    SOURCE_ID,
    resolve_address,
)
from app.main import app
from app.resilience.transport import TransportResponse

# test file: <root>/services/api/tests/api/test_address_resolution_recorded_geoclient.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "geoclient"

# The recorded official captures (services/api/tests/fixtures/geoclient). Their
# provenance (live capture by the owner holding the key) lives in each file.
G01 = "G01_address_documented_example.json"  # resolved documented example
G02 = "G02_address_ambiguous_ee.json"        # ambiguity (misspelled street, EE)
G03 = "G03_address_rejected_42.json"         # rejection (house 99999, GRC 42)

URL = "/api/v1/address-resolution"

# Clearly-fake dummy key injected ONLY into the test environment; words only so
# it is never key-shaped and never resembles the owner-held real secret.
DUMMY_KEY = "DUMMY-GEOCLIENT-KEY-RECORDED-DATA-TEST-ONLY"

# Import the e2e harness module so its OPT-IN recorded-Geoclient resolver (added
# in the same change) has direct unit coverage here - the harness cannot run
# under node and its vitest/Playwright suites run in CI only.
_HARNESS_DIR = _REPO_ROOT / "apps" / "web" / "e2e" / "harness"
if str(_HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(_HARNESS_DIR))
import fixture_api  # noqa: E402 (path set above)


def _no_sleep(_seconds: float) -> None:
    return None


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Mechanical no-network guard at the EGRESS SEAMS (the accepted
    test_address_resolution_api pattern: blocking socket CONSTRUCTION deadlocks
    the anyio portal the TestClient drives the app through, so egress is blocked
    where it actually happens - http.client's connect choke points and
    socket.create_connection). Any real network attempt fails loudly."""

    def _blocked(*_args, **_kwargs):
        raise AssertionError("network I/O attempted in an offline test")

    monkeypatch.setattr(http.client.HTTPConnection, "connect", _blocked)
    monkeypatch.setattr(http.client.HTTPSConnection, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


def enable_flag(monkeypatch) -> None:
    # The route reuses the rule-evaluation flag (address entry is the same
    # internal property flow's entry step); production ships it unset -> 404.
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


def set_dummy_key(monkeypatch) -> None:
    """A dummy subscription key present ONLY in the test environment. The route's
    default resolver reads the key from this variable at call time (the
    production key-read branch), so the recorded path exercises that branch
    without ever touching the owner-held real key."""
    monkeypatch.setenv(KEY_ENV_VAR, DUMMY_KEY)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def recorded_request(name: str) -> dict:
    """One recorded capture: the exact house/street/borough it was recorded with
    (parsed from its own request_url, never restated), its request_url, its
    verbatim response body, and the parsed ``address`` object."""
    fixture = _load_fixture(name)
    query = parse_qs(urlparse(fixture["request_url"]).query)
    return {
        "house_number": query["houseNumber"][0],
        "street": query["street"][0],
        "borough": query["borough"][0],
        "request_url": fixture["request_url"],
        "body": fixture["response_body_raw"],
        "address": json.loads(fixture["response_body_raw"])["address"],
    }


class RecordedUrlTransport:
    """URL-keyed fake transport over the recorded Geoclient captures. It serves
    each recorded body ONLY for the exact request_url that fixture was captured
    with, and RAISES on any other url - so a request the recorded data cannot
    answer can never silently fall through to the network. Records every call so
    the test can assert the connector built exactly the recorded url."""

    def __init__(self, bodies_by_url: dict[str, str]):
        self._by_url = dict(bodies_by_url)
        self.calls: list[tuple[str, dict, float]] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append((url, dict(headers), timeout))
        if url not in self._by_url:
            raise AssertionError(
                f"no recorded Geoclient capture for url {url!r}; serving it "
                "would require a live network call"
            )
        return TransportResponse(200, self._by_url[url])


def recorded_transport() -> RecordedUrlTransport:
    bodies_by_url = {}
    for name in (G01, G02, G03):
        req = recorded_request(name)
        bodies_by_url[req["request_url"]] = req["body"]
    return RecordedUrlTransport(bodies_by_url)


def install_recorded_resolver(transport: RecordedUrlTransport) -> None:
    """Override the route's resolver seam with the REAL connector over the
    recorded-url transport. The key is NOT passed here: the connector reads the
    dummy value from the test environment at call time (the production branch)."""

    def _resolver(house_number, street, *, borough=None, zip_code=None):
        return resolve_address(
            house_number,
            street,
            borough=borough,
            zip_code=zip_code,
            transport=transport,
            sleep=_no_sleep,
        )

    app.dependency_overrides[get_address_resolver] = lambda: _resolver


def _single_body_transport(body: str):
    def _transport(_url: str, _headers: dict, _timeout: float) -> TransportResponse:
        return TransportResponse(200, body)

    return _transport


# ---------------------------------------------------------------------------
# The real route + real connector, on the recorded documented-example capture.
# ---------------------------------------------------------------------------


def test_g01_documented_example_resolves_through_real_connector_and_route(
    client, monkeypatch
):
    """The documented-example address (314 W 100 St, Manhattan) resolves end to
    end through the REAL route and REAL connector over the recorded G01 body.
    The route value equals what the connector derives from the SAME recorded
    body equals the fixture's own field (triple anti-tautology)."""
    enable_flag(monkeypatch)
    set_dummy_key(monkeypatch)
    req = recorded_request(G01)
    addr = req["address"]
    transport = recorded_transport()
    install_recorded_resolver(transport)

    response = client.get(
        URL,
        params={
            "house_number": req["house_number"],
            "street": req["street"],
            "borough": req["borough"],
        },
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "resolved"

    # What the REAL connector derives from the SAME recorded body, computed
    # independently offline (not restated as literals).
    direct = resolve_address(
        req["house_number"],
        req["street"],
        borough=req["borough"],
        key=DUMMY_KEY,
        transport=_single_body_transport(req["body"]),
        sleep=_no_sleep,
    )
    canonical = doc["canonical"]
    assert canonical["bbl"] == direct.bbl == addr["bbl"]
    assert canonical["bin"] == direct.bin == addr["buildingIdentificationNumber"]
    assert (
        canonical["street_name_normalized"]
        == direct.street_name_normalized
        == addr["firstStreetNameNormalized"]
    )
    assert canonical["borough_name"] == direct.borough_name == addr["firstBoroughName"]
    assert canonical["zip_code"] == direct.zip_code == addr["zipCode"]
    assert canonical["latitude"] == direct.latitude == addr["latitude"]
    assert canonical["longitude"] == direct.longitude == addr["longitude"]

    # The REAL Geoclient connector ran (its own source id in provenance), not a
    # synthetic stand-in.
    assert doc["provenance"]["source_id"] == SOURCE_ID

    # Positive control: the connector built EXACTLY the recorded capture url and
    # sent the dummy key only in the auth header, never in the url.
    assert [call[0] for call in transport.calls] == [req["request_url"]]
    url_called, headers_sent, _timeout = transport.calls[0]
    assert headers_sent[KEY_HEADER] == DUMMY_KEY
    assert DUMMY_KEY not in url_called


def test_g02_documented_misspelling_yields_typed_ambiguous(client, monkeypatch):
    """The recorded EE capture (misspelled street) is the route's typed ambiguous
    outcome: suggestions surfaced verbatim from the fixture's own slots, nothing
    selected, no source facts."""
    enable_flag(monkeypatch)
    set_dummy_key(monkeypatch)
    req = recorded_request(G02)
    addr = req["address"]
    transport = recorded_transport()
    install_recorded_resolver(transport)

    response = client.get(
        URL,
        params={
            "house_number": req["house_number"],
            "street": req["street"],
            "borough": req["borough"],
        },
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "ambiguous"
    assert doc["selection_policy"] == "caller_selects"
    assert doc["source_facts"] == []
    assert doc["canonical"]["bbl"] is None  # nothing fabricated
    assert doc["suggestions"] == [
        {"street_name": addr["streetName1"], "street_code": addr["streetCode1"]}
    ]
    assert [call[0] for call in transport.calls] == [req["request_url"]]


def test_g03_documented_out_of_range_yields_typed_rejection(client, monkeypatch):
    """The recorded out-of-range capture (house 99999, GRC 42) is the route's
    typed rejection: both GRCs surfaced verbatim, partial data transported, no
    source facts."""
    enable_flag(monkeypatch)
    set_dummy_key(monkeypatch)
    req = recorded_request(G03)
    addr = req["address"]
    transport = recorded_transport()
    install_recorded_resolver(transport)

    response = client.get(
        URL,
        params={
            "house_number": req["house_number"],
            "street": req["street"],
            "borough": req["borough"],
        },
    )
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "rejected"
    assert doc["grc"] == addr["geosupportReturnCode"]
    assert doc["grc2"] == addr["geosupportReturnCode2"]
    assert doc["grc_message"] == addr.get("message")
    assert doc["source_facts"] == []
    # Partial data still transports per the connector contract (populated on a
    # non-resolved status; consumers branch on status, never on presence).
    assert doc["canonical"]["street_name_normalized"] == addr.get(
        "firstStreetNameNormalized"
    )
    assert [call[0] for call in transport.calls] == [req["request_url"]]


def test_flag_off_route_is_a_generic_404_unchanged(client, monkeypatch):
    """With the flag OFF the route is a generic 404 byte-indistinguishable from
    an unmounted path - no correlation header, no hint the feature exists. The
    dummy key and resolver seam are present but must not change this."""
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    set_dummy_key(monkeypatch)
    install_recorded_resolver(recorded_transport())
    req = recorded_request(G01)

    response = client.get(
        URL,
        params={
            "house_number": req["house_number"],
            "street": req["street"],
            "borough": req["borough"],
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in response.headers


def test_recorded_transport_refuses_any_non_recorded_url():
    """No network call is made: the fake transport raises on any url other than a
    recorded capture. Together with the autouse socket guard this is the
    mechanical proof that an address the recorded data does not cover can never
    reach the network."""
    transport = recorded_transport()
    bogus = (
        "https://api.nyc.gov/geoclient/v2/address"
        "?houseNumber=1&street=nowhere%20st&borough=manhattan"
    )
    with pytest.raises(AssertionError):
        transport(bogus, {}, 1.0)
    assert transport.calls == [(bogus, {}, 1.0)]  # it recorded the refused attempt


def test_route_only_ever_calls_recorded_urls_across_all_three_captures(
    client, monkeypatch
):
    """Drive all three recorded captures through the route on one shared
    transport and prove the ONLY urls the connector ever requested are the three
    recorded request_urls - no live-shaped request leaked out."""
    enable_flag(monkeypatch)
    set_dummy_key(monkeypatch)
    transport = recorded_transport()
    install_recorded_resolver(transport)
    expected_urls = []
    for name in (G01, G02, G03):
        req = recorded_request(name)
        expected_urls.append(req["request_url"])
        response = client.get(
            URL,
            params={
                "house_number": req["house_number"],
                "street": req["street"],
                "borough": req["borough"],
            },
        )
        assert response.status_code == 200
    assert [call[0] for call in transport.calls] == expected_urls


# ---------------------------------------------------------------------------
# The e2e harness OPT-IN recorded-Geoclient resolver (requirement b). The
# default harness resolver stays synthetic; this proves the opt-in runs the real
# connector for the documented example and delegates everything else unchanged.
# ---------------------------------------------------------------------------


def test_harness_recorded_resolver_runs_real_connector_for_the_documented_example():
    req = recorded_request(G01)
    addr = req["address"]
    outcome = fixture_api.harness_recorded_geoclient_resolver(
        req["house_number"], req["street"], borough=req["borough"]
    )
    assert outcome.status == "resolved"
    assert outcome.bbl == addr["bbl"]
    # The REAL connector's own source id proves this is not the synthetic path.
    assert outcome.provenance["source_id"] == SOURCE_ID


def test_harness_recorded_resolver_delegates_to_synthetic_for_other_addresses():
    """Every non-G01 address keeps today's synthetic behaviour byte-for-byte:
    same mapped BBL, same (synthetic) source id, same status as a direct call to
    the synthetic resolver."""
    street = "OUTLINE AVENUE"  # a street the synthetic harness map knows
    synthetic = fixture_api.harness_address_resolver("1", street, borough="manhattan")
    via_opt_in = fixture_api.harness_recorded_geoclient_resolver(
        "1", street, borough="manhattan"
    )
    assert (
        via_opt_in.bbl
        == synthetic.bbl
        == fixture_api.ADDRESS_BBL_BY_STREET[street]
    )
    assert via_opt_in.status == synthetic.status == "resolved"
    assert (
        via_opt_in.provenance["source_id"]
        == synthetic.provenance["source_id"]
        == "nyc-geoclient"
    )
    # The real connector's source id must NOT appear on the synthetic path.
    assert via_opt_in.provenance["source_id"] != SOURCE_ID


def test_harness_default_resolver_selection_is_unchanged():
    """Guard against accidentally flipping the e2e default (which runs in CI
    only): build_app must still wire the SYNTHETIC resolver as the default, and
    must NOT wire the recorded opt-in as the default."""
    source = Path(fixture_api.__file__).read_text(encoding="utf-8")
    normalized = " ".join(source.split())
    assert (
        "app.dependency_overrides[get_address_resolver] = ( "
        "lambda: harness_address_resolver )" in normalized
    )
    assert (
        "app.dependency_overrides[get_address_resolver] = ( "
        "lambda: harness_recorded_geoclient_resolver" not in normalized
    )
