"""GET /api/v1/properties/{bbl}/hidden-issue-flags - internal §8a hidden-issue
flags route (lane C, packet W2; plan section 8a, queue item B-09).

Offline and deterministic. The route is NOT mounted in ``app.main`` yet (packet
W5 mounts the W2-W4 routes), so these tests build a LOCAL FastAPI app with the
router (the #316 study-setup pattern) and drive it through its INJECTED
flag-inputs provider (``get_hidden_issue_flag_inputs_provider`` override), so no
network is touched:

- the 200 path replays the RECORDED 215-16 Northern benchmark PLUTO body through
  the accepted connector + the real profile / B-07 pipeline
  (``assemble_hidden_issue_flag_inputs``), proving the four §8a groups are
  produced from recorded official data and wrapped in the W0 contract envelope;
- the contract-guard path forces a built document the contract rejects and proves
  the route refuses to ship it (500 ``internal_contract_error``), never an invalid
  200 - with the mutation reverted the same inputs return 200 (red/green);
- the "no legal claim" path asserts the whole response makes no verified- or
  combined-zoning-lot claim and decides no rule.

Every emitted (HTTP status, state) pair is asserted to be in the route's single
source of truth ``HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX``, and the suite drives
every pair in it (exhaustive).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import hidden_issue_flags_read as mod
from app.api.v1.hidden_issue_flags_inputs import (
    HiddenIssueFlagInputsUnavailableError,
    assemble_hidden_issue_flag_inputs,
    default_hidden_issue_flag_inputs_provider,
    pluto_hidden_issue_flag_inputs_provider,
)
from app.api.v1.hidden_issue_flags_read import (
    CONTRACT_VERSION,
    HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX,
    get_hidden_issue_flag_inputs_provider,
    get_rate_limiter,
    router,
)
from app.config import INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR
from app.connectors.pluto_soda import (
    SourceUnavailableError,
    TransportResponse,
    fetch_by_bbl,
)
from app.contracts.study_contracts import validate_hidden_issue_flags_document
from app.profile.hidden_issue_flags import (
    FlagGroup,
    HiddenIssueFlag,
    zoning_lot_history_group,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}

# The four §8a group ids, in the route's build order (plan section 8a).
EXPECTED_GROUP_IDS = [
    "existing_building",
    "zoning_lot_history",
    "map_based_rules",
    "site_shape_and_street",
]


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
    return pluto_hidden_issue_flag_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON
    )


def _client(provider=None) -> TestClient:
    """A LOCAL FastAPI app with just the W2 router (the route is not mounted in
    app.main yet). The flag-inputs provider is injected so the suite is offline."""
    app = FastAPI()
    app.include_router(router)
    if provider is not None:
        app.dependency_overrides[get_hidden_issue_flag_inputs_provider] = lambda: provider
    return TestClient(app)


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, "1")


def _assert_pair_documented(response) -> None:
    body = response.json()
    state = body.get("state") if isinstance(body, dict) else None
    assert (response.status_code, state) in HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX, (
        response.status_code,
        state,
    )


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The per-route limiter is MODULE-level state keyed by the shared TestClient
    host; reset its windows around every test so cases do not accumulate stamps
    into a spurious 429."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _unavailable_provider(reason: str = "no_match"):
    """An offline provider that fails safe (no network), for the typed-503 path."""

    def provider(bbl: str, correlation_id: str, *, selected=None):
        raise HiddenIssueFlagInputsUnavailableError("withheld (test)", reason=reason)

    return provider


# ---------------------------------------------------------------------------
# Flag gating
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, raising=False)
    response = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # Byte-indistinguishable from an unmounted path: no correlation id, no hint.
    assert "X-Correlation-ID" not in response.headers
    _assert_pair_documented(response)


@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_non_true_flag_tokens_stay_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, token)
    response = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# BBL validation (typed 422 before any provider call)
# ---------------------------------------------------------------------------
def test_malformed_bbl_is_typed_422_before_provider(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl: str, correlation_id: str, *, selected=None):
        raise AssertionError("the provider must not be called for a malformed BBL")

    response = _client(exploding_provider).get("/api/v1/properties/NOT-A-BBL/hidden-issue-flags")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    assert "code" in body["detail"] and "raw_value" in body["detail"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# 200 success - recorded 215-16 Northern pack through the real profile pipeline
# ---------------------------------------------------------------------------
def test_flags_200_from_recorded_pack(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    # A 200 carries NO ``state`` (the document speaks for itself).
    assert "state" not in body
    # The W0 envelope: version + the four §8a groups, in build order.
    assert set(body) == {"contract_version", "groups"}
    assert body["contract_version"] == CONTRACT_VERSION == "1.0.0"
    assert [g["group_id"] for g in body["groups"]] == EXPECTED_GROUP_IDS
    # Every group describes the one entered lot.
    assert all(g["lot_bbl"] == NORTHERN_BBL for g in body["groups"])
    # The server would never ship a document its own guard rejects.
    validate_hidden_issue_flags_document(body)
    _assert_pair_documented(response)


def test_flags_200_surfaces_recorded_map_based_issues(monkeypatch) -> None:
    """The §8a layer is not vacuous: the recorded PLUTO columns produce at least
    one real flag and one recorded 'No flag' (splitzone false) for this pack, so
    the response reports what the sourced data already shows."""
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    ).json()
    map_based = next(g for g in body["groups"] if g["group_id"] == "map_based_rules")
    statuses = {f["status"] for f in map_based["flags"]}
    assert "flag" in statuses  # commercial overlay C2-2 is recorded for this lot
    assert "not_flagged" in statuses  # splitzone recorded false -> "No flag"
    # Every flag's display label is tied one-to-one to its status.
    label_for = {"flag": "Flag", "opportunity": "Opportunity",
                 "check_needed": "Check needed", "not_flagged": "No flag"}
    for group in body["groups"]:
        for flag in group["flags"]:
            assert flag["status_label"] == label_for[flag["status"]]


# ---------------------------------------------------------------------------
# No legal claim: the §8a data layer never verifies a zoning lot, never claims a
# combined one, and decides no rule (platform principle 1; plan P-2; schema).
# ---------------------------------------------------------------------------
def test_no_text_claims_verified_or_combined_zoning_lot_or_decides_a_rule(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    ).json()

    # 1. The zoning-lot-history group is flag-only (plan P-2): its items are only
    #    'flag' or 'check_needed', never 'opportunity'/'not_flagged', so it never
    #    verifies or clears a zoning lot. With no recorded documents fed in this
    #    slice, every item is 'check_needed' (a reviewer must check it).
    zlh = next(g for g in body["groups"] if g["group_id"] == "zoning_lot_history")
    assert {f["status"] for f in zlh["flags"]} <= {"flag", "check_needed"}
    assert all(f["status"] == "check_needed" for f in zlh["flags"])

    # 2. No text anywhere claims a VERIFIED or COMBINED zoning lot, and nothing
    #    asserts a rule determination (a decided permission/compliance).
    texts: list[str] = []
    for group in body["groups"]:
        texts.append(group["title"])
        for flag in group["flags"]:
            texts.append(flag["title"])
            texts.append(flag["detail"])
            texts.append(flag["status_label"])
    blob = " ".join(texts).lower()
    for banned in (
        "verified zoning lot",
        "combined zoning lot",
        "the zoning lot is",
        "is a valid zoning lot",
        "as-of-right allowance is",  # no allowance is decided (engine off)
        "is permitted",
        "is non-conforming use",  # a decided legal conclusion (vs "whether ...")
        "does not comply",
    ):
        assert banned not in blob, banned

    # 3. The existing-building 'larger than today' item is never decided: with no
    #    allowance supplied (engine off) it is 'check_needed', never a 'flag' that
    #    the building exceeds today's rules.
    existing = next(g for g in body["groups"] if g["group_id"] == "existing_building")
    larger = next(f for f in existing["flags"] if f["item_id"].endswith("larger_than_today"))
    assert larger["status"] == "check_needed"


def test_flag_inputs_pass_b07_geometry(monkeypatch) -> None:
    """B-09 open question (a): lane C passes the B-07 combined SiteGeometry. For
    this recorded single-lot pack B-07 produces a geometry, so the site-shape
    group reads it (its through-lot item carries a B-03 lot-type evidence or a
    reasoned 'Check needed', never a silent default)."""
    inputs = assemble_hidden_issue_flag_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    assert inputs.site_geometry is not None
    assert inputs.bbl == NORTHERN_BBL


# ---------------------------------------------------------------------------
# Inputs unavailable - fail-safe 503, nothing fabricated
# ---------------------------------------------------------------------------
def test_inputs_unavailable_is_fail_safe_503(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_unavailable_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "inputs_unavailable"
    assert body["correlation_id"]
    _assert_pair_documented(response)


def test_upstream_connector_failure_is_503(monkeypatch) -> None:
    _enable(monkeypatch)

    def failing_fetcher(bbl: str, correlation_id: str):
        raise SourceUnavailableError("down", correlation_id=correlation_id)

    provider = pluto_hidden_issue_flag_inputs_provider(failing_fetcher, env=LANE_B_ON)
    response = _client(provider).get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


def test_lane_b_gate_off_is_503(monkeypatch) -> None:
    """The flag inputs are Lane B behaviour: with LANE_B_ENABLED off the combined
    site is not produced, so the inputs are withheld (fail safe), never
    fabricated."""
    _enable(monkeypatch)
    provider = pluto_hidden_issue_flag_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env={}
    )
    response = _client(provider).get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


# ---------------------------------------------------------------------------
# Contract guard - an invalid built document is refused (never an invalid 200)
# ---------------------------------------------------------------------------
def _bad_zoning_lot_history_group(bbl, **kwargs):
    """A zoning-lot-history group carrying an 'opportunity' flag. The dataclass
    permits the status, but the W0 contract restricts this group to
    flag|check_needed (plan P-2), so the built document fails its contract. A
    stand-in for any future producer defect the guard must catch."""
    return FlagGroup(
        "zoning_lot_history",
        "Zoning-lot history",
        bbl,
        (
            HiddenIssueFlag(
                "zoning_lot_history.bad",
                "zoning_lot_history",
                "Bad item",
                "opportunity",  # forbidden for this group by the contract
                "detail",
                "typical source",
            ),
        ),
    )


def test_invalid_group_is_refused_as_internal_contract_error(monkeypatch) -> None:
    _enable(monkeypatch)
    # Baseline: the same inputs return a valid 200 (the mutation is what breaks it).
    assert _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    ).status_code == 200

    # Displace a real group with one the contract rejects -> the guard refuses to
    # ship it. Reverting (the baseline above) restores the 200: red/green.
    monkeypatch.setattr(mod, "zoning_lot_history_group", _bad_zoning_lot_history_group)
    response = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert response.status_code == 500
    assert response.json()["state"] == "internal_contract_error"
    _assert_pair_documented(response)


def test_unexpected_provider_error_is_generic_500(monkeypatch) -> None:
    _enable(monkeypatch)

    def boom(bbl: str, correlation_id: str, *, selected=None):
        raise RuntimeError("UPSTREAM_SECRET_TOKEN")

    response = _client(boom).get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_error"
    # The body is a FIXED bounded message; no upstream exception text leaks.
    assert "UPSTREAM_SECRET_TOKEN" not in body["message"]
    assert body["message"] == "unexpected internal error; see server logs by correlation id"
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# The route default is the live PLUTO binding (proven offline in the inputs seam).
# ---------------------------------------------------------------------------
def test_route_default_provider_is_the_live_binding() -> None:
    assert get_hidden_issue_flag_inputs_provider() is default_hidden_issue_flag_inputs_provider


# ---------------------------------------------------------------------------
# Per-caller rate limit - a typed 429 consistent with the sibling routes.
# ---------------------------------------------------------------------------
def test_rate_limit_returns_typed_429(monkeypatch) -> None:
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 2)
    limiter.reset()
    client = _client(_northern_provider())
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags").status_code == 200
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags").status_code == 200
    limited = client.get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags")
    assert limited.status_code == 429
    body = limited.json()
    assert body["state"] == "rate_limited"
    assert limited.headers["X-Correlation-ID"] == body["correlation_id"]
    _assert_pair_documented(limited)
    # Mutation (loosen the CONSUMING limiter): a large limit removes the 429.
    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    assert client.get(f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags").status_code == 200


def test_rate_limit_precedes_validation_and_io(monkeypatch) -> None:
    """The limiter refuses BEFORE validation/I-O: an over-limit caller with a
    malformed BBL still gets the 429, never the 422."""
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()

    def exploding_provider(bbl, correlation_id, *, selected=None):
        raise AssertionError("provider must not run when rate limited")

    resp = _client(exploding_provider).get("/api/v1/properties/NOT-A-BBL/hidden-issue-flags")
    assert resp.status_code == 429
    assert resp.json()["state"] == "rate_limited"


def test_rate_limit_is_after_the_flag_off_404(monkeypatch) -> None:
    """Hard rule: the flag-off 404 is unchanged - even an over-limit caller gets
    the generic 404 (byte-identical to an unmounted path), never a 429."""
    monkeypatch.delenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, raising=False)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    resp = _client(_northern_provider()).get(
        f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


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

    base = f"/api/v1/properties/{NORTHERN_BBL}/hidden-issue-flags"

    # (404, None): flag off
    monkeypatch.delenv(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, raising=False)
    record(_client(_northern_provider()).get(base))

    _enable(monkeypatch)
    # (422, validation_error)
    record(_client(_northern_provider()).get("/api/v1/properties/NOPE/hidden-issue-flags"))
    # (200, None)
    record(_client(_northern_provider()).get(base))
    # (503, inputs_unavailable)
    record(_client(_unavailable_provider()).get(base))

    # (500, internal_contract_error)
    monkeypatch.setattr(mod, "zoning_lot_history_group", _bad_zoning_lot_history_group)
    record(_client(_northern_provider()).get(base))
    # Restore the real group for the remaining cases (leave the flag enabled).
    monkeypatch.setattr(mod, "zoning_lot_history_group", zoning_lot_history_group)

    # (500, internal_error)
    def boom(bbl: str, correlation_id: str, *, selected=None):
        raise RuntimeError("x")

    record(_client(boom).get(base))

    # (429, rate_limited): refuse every caller, then one request trips the limit.
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    record(_client(_northern_provider()).get(base))

    assert observed == HIDDEN_ISSUE_FLAGS_STATUS_STATE_MATRIX
