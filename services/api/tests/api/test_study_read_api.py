"""GET /api/v1/properties/{bbl}/study - internal study-read route (lane C, request
D-1 slice 1).

Offline and deterministic. The route is driven through its INJECTED study-inputs
provider (``get_study_inputs_provider`` override), so no network is touched:

- the 200 path replays the RECORDED 215-16 Northern benchmark PLUTO body through
  the accepted connector + the real B-02/B-07 pipeline (``assemble_study_inputs``),
  proving the setup is produced from recorded official data;
- the multi-lot refusal path builds two cross-block lots directly, proving B-07's
  combination ``not_offered`` reason reaches the response VERBATIM;
- the contract-guard path injects an invalid fact and proves the route refuses to
  ship it (500 ``internal_contract_error``), never a partial or invalid 200.

Every emitted (HTTP status, state) pair is asserted to be in the route's single
source of truth ``STUDY_READ_STATUS_STATE_MATRIX``, and the suite drives every
pair in it (exhaustive).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.study_inputs import (
    StudyInputs,
    StudyInputsUnavailableError,
    assemble_study_inputs,
    default_study_inputs_provider,
    pluto_study_inputs_provider,
)
from app.api.v1.study_read import (
    STUDY_READ_STATUS_STATE_MATRIX,
    get_rate_limiter,
    get_study_inputs_provider,
)
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.connectors.pluto_soda import (
    DATASET_ID,
    SOURCE_ID,
    SourceUnavailableError,
    TransportResponse,
    fetch_by_bbl,
)
from app.connectors.pluto_version_probe import PlutoPublishedVersion
from app.contracts.study_contracts import validate_study_document
from app.main import create_app
from app.spatial.multi_lot_site import (
    SiteLot,
    build_lot_choice,
    derive_multi_lot_site,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}

# A TEST-ONLY option used solely to compose a FULL study from the setup so it can
# be validated against study.schema.json. It is never emitted by the route; its
# values are explicitly test-fixture-synthetic (the backend invents no option -
# plan M1-06; the study store takes option inputs from its caller).
_TEST_ONLY_OPTION = {
    "option_id": "opt-test",
    "name": "Option test (test-fixture-synthetic)",
    "addon_selection": [],
    "goal": {"kind": "most_residential_floor_area", "text": None},
    "program": ["market_rate_residential"],
    "floor_to_floor_heights": {
        "ground_floor": {
            "height_ft": 12,
            "basis": "stated_default",
            "statement": "Test fixture ground-floor height 12 ft (test-fixture-synthetic)",
        },
        "typical_floor": {
            "height_ft": 10,
            "basis": "stated_default",
            "statement": "Test fixture typical floor height 10 ft (test-fixture-synthetic)",
        },
        "per_floor_overrides": [],
    },
    "assumptions": [],
    "existing_building_plan": "no_existing_building",
}


def _northern_pluto_body() -> str:
    return (FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(encoding="utf-8")


def _northern_fetcher(bbl: str, correlation_id: str):
    body = _northern_pluto_body()
    return fetch_by_bbl(
        bbl,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _northern_provider():
    return pluto_study_inputs_provider(_northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON)


def _f09_probe(correlation_id: str) -> PlutoPublishedVersion:
    """A PLUTO version probe returning the recorded F09 release (26v1). The Northern
    pin (26v2) is newer, so facts stay ``current`` while proving the probe path and
    the contract guard both run."""
    return PlutoPublishedVersion(
        dataset_id=DATASET_ID,
        version="26v1",
        seen_at="2026-09-30T12:00:00Z",
        query_ref="https://example/probe",
        source_id=SOURCE_ID,
        correlation_id=correlation_id,
    )


def _failing_probe(correlation_id: str) -> PlutoPublishedVersion:
    raise SourceUnavailableError("version probe down", correlation_id=correlation_id)


def _northern_provider_with_probe(probe):
    return pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON, version_probe=probe
    )


def _client(provider=None) -> TestClient:
    app = create_app()
    if provider is not None:
        app.dependency_overrides[get_study_inputs_provider] = lambda: provider
    return TestClient(app)


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")


def _assert_pair_documented(response) -> None:
    body = response.json()
    state = body.get("state") if isinstance(body, dict) else None
    assert (response.status_code, state) in STUDY_READ_STATUS_STATE_MATRIX, (
        response.status_code,
        state,
    )


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The per-route limiter is MODULE-level state keyed by the shared TestClient
    host; reset its windows around every test so cases do not accumulate stamps
    into a spurious 429. ``max_requests`` is mutated (and auto-restored) by
    monkeypatch only in the dedicated 429 test."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _unavailable_provider(reason: str = "no_match"):
    """An offline provider that fails safe (no network), for the typed-503 path.
    Accepts the optional ``selected`` keyword so it is a valid provider."""

    def provider(bbl: str, correlation_id: str, *, selected=None):
        raise StudyInputsUnavailableError("withheld (test)", reason=reason)

    return provider


# ---------------------------------------------------------------------------
# Flag gating
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, raising=False)
    response = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # Byte-indistinguishable from an unmounted path: no correlation id, no hint.
    assert "X-Correlation-ID" not in response.headers
    _assert_pair_documented(response)


@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_non_true_flag_tokens_stay_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, token)
    response = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# BBL validation (typed 422 before any provider call)
# ---------------------------------------------------------------------------
def test_malformed_bbl_is_typed_422_before_provider(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl: str, correlation_id: str) -> StudyInputs:
        raise AssertionError("the provider must not be called for a malformed BBL")

    response = _client(exploding_provider).get("/api/v1/properties/NOT-A-BBL/study")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    assert "code" in body["detail"] and "raw_value" in body["detail"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# 200 success - recorded 215-16 Northern pack through the real B-02/B-07 pipeline
# ---------------------------------------------------------------------------
def test_study_setup_200_from_recorded_pack(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    # A 200 carries NO ``state`` (the document speaks for itself).
    body = response.json()
    assert "state" not in body
    assert body["document_kind"] == "study_setup"
    assert body["bbl"] == NORTHERN_BBL
    assert body["property"] == {"bbl": NORTHERN_BBL, "address": None}
    _assert_pair_documented(response)


def test_study_setup_lots_and_selection_are_b07_verbatim(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    # One tax lot, selected, size from City records (benchmark: 10,075 sq ft).
    assert len(body["lots"]) == 1
    lot = body["lots"][0]
    assert lot["bbl"] == NORTHERN_BBL
    assert lot["selected"] is True
    assert lot["approximate_lot_area_sq_ft"] == 10075
    assert lot["size_measurement"] == {"rank": "city_records", "label": "City records"}
    # lot_selection is B-07's: default "use all", the exact statement, single_lot.
    selection = body["lot_selection"]
    assert selection["mode"] == "all"
    assert selection["statement"] == (
        "Based on the lots you selected — the app does not verify the zoning lot"
    )
    assert selection["combination"] == {"status": "single_lot", "reason": None}


def test_study_setup_site_facts_carry_rank_label_and_source(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    facts = {fact["key"]: fact for fact in body["site"]["facts"]}
    # lot_area: a City-records number with its label and a city_dataset source.
    lot_area = facts["lot_area"]
    assert lot_area["value"] == 10075 and lot_area["unit"] == "square_feet"
    assert lot_area["measurement"] == {"rank": "city_records", "label": "City records"}
    assert lot_area["source"]["kind"] == "city_dataset"
    assert lot_area["blocks"] == []
    # zoning_district: the recorded R6B value (benchmark).
    assert facts["zoning_district"]["value"] == "R6B"
    assert facts["commercial_overlay"]["value"] == "C2-2"
    # existing_zoning_floor_area is UNKNOWN - it is never taken from PLUTO building
    # area (plan section 3 step 4); it names what it blocks.
    ezfa = facts["existing_zoning_floor_area"]
    assert ezfa["value"] is None and ezfa["measurement"]["rank"] == "unknown"
    assert ezfa["blocks"]


def test_site_facts_carry_version_check_current_for_recorded_pack(monkeypatch) -> None:
    """B-3: each PLUTO-sourced site fact carries ``source.version_check`` (the B-06
    status) and is stamped contract 1.1.0. For the recorded 215-16 Northern pack the
    status is ``current``, since the only published version on record is the
    retrieval itself (published versions = the retrievals; a version probe is a later
    slice). A fact with no dataset version stays 1.0.0 with no key. The route already
    passed its own contract guard to return this 200, so these facts are contract-valid."""
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    facts = {fact["key"]: fact for fact in body["site"]["facts"]}

    # A PLUTO-sourced fact: current version_check, label "Current", contract 1.1.0.
    lot_area = facts["lot_area"]
    assert lot_area["contract_version"] == "1.1.0"
    version_check = lot_area["source"]["version_check"]
    assert version_check["status"] == "current"
    assert version_check["label"] == "Current"
    # The reason names the retrieval time, so the "current as of this retrieval"
    # scope is explicit (studies are assembled per request; no durable store yet).
    assert lot_area["source"]["retrieved_at"] in version_check["reason"]

    # Every PLUTO-sourced fact is current and 1.1.0 (one PLUTO pin for the pack).
    for key in ("lot_area", "lot_depth", "lot_type", "zoning_district", "commercial_overlay"):
        assert facts[key]["contract_version"] == "1.1.0"
        assert facts[key]["source"]["version_check"]["status"] == "current"

    # A fact with no dataset version (existing_zoning_floor_area is UNKNOWN, no
    # city source) stays 1.0.0 and carries no version_check key.
    ezfa = facts["existing_zoning_floor_area"]
    assert ezfa["contract_version"] == "1.0.0"
    assert "version_check" not in (ezfa.get("source") or {})


def test_route_200_with_version_probe_still_passes_contract_guard(monkeypatch) -> None:
    """B-4: with the PLUTO version probe injected (offline), the 200 still passes
    its own contract guard and the PLUTO facts carry version_check. The benchmark
    pin (26v2) is newer than the probe (26v1), so the status stays ``current``."""
    _enable(monkeypatch)
    response = _client(_northern_provider_with_probe(_f09_probe)).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study"
    )
    assert response.status_code == 200
    facts = {fact["key"]: fact for fact in response.json()["site"]["facts"]}
    assert facts["lot_area"]["source"]["version_check"]["status"] == "current"
    _assert_pair_documented(response)


def test_route_200_with_version_unknown_on_probe_failure(monkeypatch) -> None:
    """B-4 fail-closed: a probe failure does NOT 5xx the route. The study still
    assembles (200) but the PLUTO facts read ``version_unknown`` - never a
    probe-masked ``current`` - and the document still passes its contract guard."""
    _enable(monkeypatch)
    response = _client(_northern_provider_with_probe(_failing_probe)).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study"
    )
    assert response.status_code == 200
    facts = {fact["key"]: fact for fact in response.json()["site"]["facts"]}
    assert facts["lot_area"]["source"]["version_check"]["status"] == "version_unknown"
    _assert_pair_documented(response)


def test_setup_composes_into_a_contract_valid_study(monkeypatch) -> None:
    """The real parts (property, lots, lot_selection, site.facts) slot into a
    full study.schema.json Study - proven by composing one with a TEST-ONLY
    option and validating it server-side."""
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    study = {
        "contract_version": "1.0.0",
        "study_id": "test-fixture-synthetic-study-northern",
        "property": body["property"],
        "lots": body["lots"],
        "lot_selection": body["lot_selection"],
        "site": body["site"],
        "options": [_TEST_ONLY_OPTION],
        "selected_option_id": "opt-test",
        "revision": {"number": 1, "created_at": "2026-09-30T12:00:00Z", "parent": None},
        "origin": {"kind": "new", "export_id": None},
    }
    validate_study_document(study)  # raises on any defect


SITE_FACT_KEYS = frozenset(
    {
        "lot_area",
        "lot_frontage",
        "lot_depth",
        "lot_type",
        "zoning_district",
        "commercial_overlay",
        "street_width",
        "existing_zoning_floor_area",
    }
)


def test_no_zoning_math_in_the_response(monkeypatch) -> None:
    """The study setup carries the selection + B-07's check + sourced facts, and
    NOTHING computed (no allowance/capacity/FAR/rule output). Proven by the
    SHAPE: no key beyond the setup half, and every site fact is a site_fact
    ``key`` (never a results/allowance field). The site_fact ``blocks`` list does
    name outputs like ``permitted_envelope`` - that is the contract's "name what
    they block", not a computed value, and stays inside the fact."""
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study").json()
    assert set(body) == {"document_kind", "bbl", "property", "lots", "lot_selection", "site"}
    assert set(body["site"]) == {"facts"}
    for fact in body["site"]["facts"]:
        assert fact["key"] in SITE_FACT_KEYS
    for lot in body["lots"]:
        assert set(lot) == {"bbl", "approximate_lot_area_sq_ft", "size_measurement", "selected"}


# ---------------------------------------------------------------------------
# Multi-lot refusal - B-07's combination reason reaches the response verbatim
# ---------------------------------------------------------------------------
def _cross_block_inputs() -> StudyInputs:
    lots = {
        "1000010001": SiteLot("1000010001", None, "no outline supplied (test)"),
        "1000020001": SiteLot("1000020001", None, "no outline supplied (test)"),
    }
    choice = build_lot_choice(list(lots), lots)
    site = derive_multi_lot_site(choice)  # two blocks -> not offered
    return StudyInputs(lot_choice=choice, site=site, site_facts=(), address=None)


def test_multi_lot_not_offered_reason_is_verbatim(monkeypatch) -> None:
    _enable(monkeypatch)
    inputs = _cross_block_inputs()
    provider = lambda bbl, cid: inputs  # noqa: E731
    body = _client(provider).get("/api/v1/properties/1000010001/study").json()
    assert body["lot_selection"]["mode"] == "all"
    combination = body["lot_selection"]["combination"]
    assert combination["status"] == "not_offered"
    # The reason is B-07's own text, carried verbatim (not re-derived here).
    assert combination["reason"] == inputs.site.combination.reason
    assert combination["reason"]
    # Both lots listed and selected; an empty facts list is still contract-valid.
    assert [lot["bbl"] for lot in body["lots"]] == ["1000010001", "1000020001"]
    assert all(lot["selected"] for lot in body["lots"])
    assert body["site"]["facts"] == []


# ---------------------------------------------------------------------------
# Inputs unavailable - fail-safe 503, nothing fabricated
# ---------------------------------------------------------------------------
def test_inputs_unavailable_is_fail_safe_503(monkeypatch) -> None:
    # A provider that cannot produce inputs (upstream no-match/outage) -> a
    # bounded 503, nothing fabricated. Offline: the live default is proven in
    # tests/api/test_study_inputs_live.py.
    _enable(monkeypatch)
    response = _client(_unavailable_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "inputs_unavailable"
    assert body["correlation_id"]
    _assert_pair_documented(response)


def test_upstream_connector_failure_is_503(monkeypatch) -> None:
    _enable(monkeypatch)

    def failing_fetcher(bbl: str, correlation_id: str):
        raise SourceUnavailableError("down", correlation_id=correlation_id)

    provider = pluto_study_inputs_provider(failing_fetcher, env=LANE_B_ON)
    response = _client(provider).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


def test_lane_b_gate_off_is_503(monkeypatch) -> None:
    """Lot choice is Lane B behaviour: with LANE_B_ENABLED off, the inputs are
    withheld (fail safe), never fabricated."""
    _enable(monkeypatch)
    provider = pluto_study_inputs_provider(_northern_fetcher, clock=FIXED_CLOCK, env={})
    response = _client(provider).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


# ---------------------------------------------------------------------------
# Contract guard - an invalid built document is refused (never an invalid 200)
# ---------------------------------------------------------------------------
def test_invalid_site_fact_is_refused_as_internal_contract_error(monkeypatch) -> None:
    _enable(monkeypatch)
    good = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    # Displace a real field: a zero lot_area is never a real area (site_fact.schema
    # forbids it). Reverting this mutation restores the 200, so the guard is the
    # thing under test (red/green).
    bad_fact = dict(good.site_facts[0])
    assert bad_fact["key"] == "lot_area"
    bad_fact["value"] = 0
    broken = StudyInputs(
        lot_choice=good.lot_choice,
        site=good.site,
        site_facts=(bad_fact, *good.site_facts[1:]),
        address=good.address,
    )
    response = _client(lambda bbl, cid: broken).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 500
    assert response.json()["state"] == "internal_contract_error"
    _assert_pair_documented(response)


def test_unexpected_provider_error_is_generic_500(monkeypatch) -> None:
    _enable(monkeypatch)

    def boom(bbl: str, correlation_id: str) -> StudyInputs:
        raise RuntimeError("unexpected")

    response = _client(boom).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_error"
    # No upstream text leaks into the bounded body.
    assert "unexpected" not in body["message"] or "internal error" in body["message"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# The route default is the deferred fail-safe provider (not a live fetch yet).
# ---------------------------------------------------------------------------
def test_route_default_provider_is_the_live_binding() -> None:
    # The route default is the LIVE PLUTO path (slice 2). Its offline wiring to
    # the properties resilient fetcher is proven in test_study_inputs_live.py;
    # here we only pin that the dependency still resolves to it.
    assert get_study_inputs_provider() is default_study_inputs_provider


# ---------------------------------------------------------------------------
# The (status, state) matrix is exhaustive: every documented pair is driven, and
# nothing outside it is emitted.
# ---------------------------------------------------------------------------
def test_status_state_matrix_is_exhaustively_driven(monkeypatch) -> None:
    observed: set[tuple[int, str | None]] = set()

    def record(response) -> None:
        body = response.json()
        state = body.get("state") if isinstance(body, dict) else None
        observed.add((response.status_code, state))

    # (404, None): flag off
    monkeypatch.delenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, raising=False)
    record(_client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))

    _enable(monkeypatch)
    # (422, validation_error)
    record(_client(_northern_provider()).get("/api/v1/properties/NOPE/study"))
    # (200, None)
    record(_client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))
    # (503, inputs_unavailable)
    record(_client(_unavailable_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))
    # (500, internal_contract_error)
    good = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    bad_fact = dict(good.site_facts[0])
    bad_fact["value"] = 0
    broken = StudyInputs(good.lot_choice, good.site, (bad_fact, *good.site_facts[1:]), None)
    record(_client(lambda bbl, cid: broken).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))

    # (500, internal_error)
    def boom(bbl: str, correlation_id: str) -> StudyInputs:
        raise RuntimeError("x")

    record(_client(boom).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))

    # (429, rate_limited): refuse every caller, then one request trips the limit.
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    record(_client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study"))

    assert observed == STUDY_READ_STATUS_STATE_MATRIX


# ---------------------------------------------------------------------------
# Per-caller rate limit (NB1) - a typed 429 consistent with the sibling routes.
# ---------------------------------------------------------------------------
def test_rate_limit_returns_typed_429(monkeypatch) -> None:
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 2)
    limiter.reset()
    client = _client(_northern_provider())
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/study").status_code == 200
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/study").status_code == 200
    limited = client.get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert limited.status_code == 429
    body = limited.json()
    assert body["state"] == "rate_limited"
    assert limited.headers["X-Correlation-ID"] == body["correlation_id"]
    _assert_pair_documented(limited)
    # Mutation (loosen the CONSUMING limiter): a large limit removes the 429.
    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/study").status_code == 200


def test_rate_limit_precedes_validation_and_io(monkeypatch) -> None:
    """The limiter refuses BEFORE validation/I-O: an over-limit caller with a
    malformed BBL still gets the 429, never the 422."""
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()

    def exploding_provider(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not run when rate limited")

    resp = _client(exploding_provider).get("/api/v1/properties/NOT-A-BBL/study")
    assert resp.status_code == 429
    assert resp.json()["state"] == "rate_limited"


def test_rate_limit_is_after_the_flag_off_404(monkeypatch) -> None:
    """Hard rule: the flag-off 404 is unchanged - even an over-limit caller gets
    the generic 404 (byte-identical to an unmounted path), never a 429."""
    monkeypatch.delenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, raising=False)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    resp = _client(_northern_provider()).get(f"/api/v1/properties/{NORTHERN_BBL}/study")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


# ---------------------------------------------------------------------------
# Re-pick: an optional `selected` query, validated before any I/O, passed to
# B-07 verbatim. The route never computes geometry/adjacency itself.
# ---------------------------------------------------------------------------
def test_selected_single_lot_matches_use_all(monkeypatch) -> None:
    _enable(monkeypatch)
    url = f"/api/v1/properties/{NORTHERN_BBL}/study?selected={NORTHERN_BBL}"
    response = _client(_northern_provider()).get(url)
    assert response.status_code == 200
    body = response.json()
    assert [lot["bbl"] for lot in body["lots"]] == [NORTHERN_BBL]
    # One entered lot, re-picked explicitly: B-07 still reports the "all" mode.
    assert body["lot_selection"]["mode"] == "all"
    _assert_pair_documented(response)


def test_selected_unknown_lot_is_typed_422(monkeypatch) -> None:
    """A BBL not in this property's lot choice is B-07's rejection, surfaced as a
    typed 422 (not a 500/503). The caller's BBLs are not echoed into the body."""
    _enable(monkeypatch)
    url = f"/api/v1/properties/{NORTHERN_BBL}/study?selected=1000010001"
    response = _client(_northern_provider()).get(url)
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == "invalid_lot_selection"
    assert "1000010001" not in body["message"]
    _assert_pair_documented(response)


def test_selected_malformed_bbl_is_422_before_io(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not be called for a malformed selected BBL")

    url = f"/api/v1/properties/{NORTHERN_BBL}/study?selected=NOT-A-BBL"
    response = _client(exploding_provider).get(url)
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert "code" in body["detail"]
    _assert_pair_documented(response)


def test_selected_empty_value_is_422(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not be called for an empty selected value")

    response = _client(exploding_provider).get(
        f"/api/v1/properties/{NORTHERN_BBL}/study?selected="
    )
    assert response.status_code == 422
    assert response.json()["state"] == "validation_error"


def test_selected_duplicate_is_422(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not be called for a duplicate selection")

    url = (
        f"/api/v1/properties/{NORTHERN_BBL}/study"
        f"?selected={NORTHERN_BBL}&selected={NORTHERN_BBL}"
    )
    response = _client(exploding_provider).get(url)
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["detail"]["code"] == "duplicate_selection"


def test_422_message_is_length_capped_server_side(monkeypatch) -> None:
    """Security review NB3: the 422 message is length-capped server-side."""
    from app.api.v1.study_read import _RAW_VALUE_TRUNCATION_MARKER, MAX_MESSAGE_CHARS

    _enable(monkeypatch)
    response = _client(_northern_provider()).get("/api/v1/properties/NOT-A-BBL/study")
    assert response.status_code == 422
    assert len(response.json()["message"]) <= MAX_MESSAGE_CHARS + len(_RAW_VALUE_TRUNCATION_MARKER)
