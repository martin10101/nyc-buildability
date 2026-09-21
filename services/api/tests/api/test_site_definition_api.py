"""Unmounted site-definition confirmation API acceptance pack (M5-T059, D-078).

FIRST local-FastAPI test precedent in this suite. The site-definition write router
is DELIBERATELY UNMOUNTED (main.py is held by the live M5-T057 lane and
production-unreachable is the safe state for a write-shaped endpoint whose store is
ephemeral and whose identity is self-attested), so it cannot be reached through
``app.main``. Each test builds a LOCAL ``FastAPI()``, includes the router, and
overrides the injected resolver + store with recorded doubles - fully offline, no
network, no ``main.py`` change. ``app.dependency_overrides`` works identically on a
locally-built app.

Coverage:
- AS-5 route discipline: flag off -> generic 404 (no correlation leak); malformed
  BBL -> 422; over-ceiling body -> 413; a non-multi-lot resolution -> 422.
- AS-1 create: the exact resolver parcel set -> 201 with the self-attested,
  refused-for-calculation record and byte-copied provenance; the attestation is
  server-set (an untrusted body cannot claim authentication).
- AS-2 strict binding: a divergent parcel set -> typed 422 parcel_set_mismatch.
- AS-3 append-only: duplicate active -> 409; supersede/revoke require a reason
  (missing -> 422); supersede chains a new active; revoke is terminal; list returns
  the whole chain newest-first.
- Router UNMOUNTED: app.main exposes no site-definition route (main.py untouched).
- Shared-store integration: a confirmation created through the (unmounted) write
  route surfaces on the condo-records read document through the ONE shared store -
  proven on a local app that mounts BOTH routers over a single store.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.condo_records import (
    get_condo_billing_resolver,
    get_condo_site_definition_store,
    get_condo_unit_resolver,
)
from app.api.v1.condo_records import router as condo_router
from app.api.v1.site_definition import (
    MAX_BODY_BYTES,
    SITE_DEFINITION_STATUS_STATE_MATRIX,
    SITE_DEFINITION_WRITE_ENABLED_ENV_VAR,
    get_site_definition_resolver,
    get_site_definition_store,
    site_definition_write_enabled,
)
from app.api.v1.site_definition import router as sd_router
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.condo_base_lot import (
    OUTCOME_ERROR,
    OUTCOME_MULTI_LOT,
    OUTCOME_RESOLVED_SINGLE,
    OUTCOME_UNRESOLVED,
    CondoResolution,
)
from app.main import app as main_app
from app.main import create_app
from app.site_definition import InMemorySiteDefinitionStore

CONDO_KEY = "103344"
BILLING_BBL = "1003037502"  # lot 7502 -> billing class
PARCELS = ("1003030019", "1003030025")
DIVERGENT_NOTICE = "Divergent zoning across a condo's base lots is a legal question."


def _multi_lot(
    base_bbls: tuple[str, ...] = PARCELS,
    condo_key: str | None = CONDO_KEY,
) -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_MULTI_LOT,
        input_bbl=BILLING_BBL,
        correlation_id="test-corr",
        base_bbls=base_bbls,
        resolved_base_bbl=None,
        condo_key=condo_key,
        condo_number="3344",
        resolution_path="billing",
        source_id="nyc-dof-dtm-condo-soda",
        dataset_ids=("p8u6-a6it",),
        retrieved_at="2026-09-01T14:05:56.732000Z",
        provenance=(
            {"dataset_id": "p8u6-a6it", "query_kind": "condo_billing_bbl"},
        ),
        divergent_zoning_notice=DIVERGENT_NOTICE,
        notes=("multi-lot condo: 2 base lots resolved; never collapsed.",),
    )


def _single() -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_RESOLVED_SINGLE,
        input_bbl=BILLING_BBL,
        correlation_id="test-corr",
        base_bbls=("1003030019",),
        resolved_base_bbl="1003030019",
        condo_key=CONDO_KEY,
        condo_number="3344",
        resolution_path="billing",
        source_id="nyc-dof-dtm-condo-soda",
        dataset_ids=("p8u6-a6it",),
        retrieved_at="2026-09-01T14:05:56Z",
    )


def _sd_app(store: InMemorySiteDefinitionStore, resolution: CondoResolution) -> FastAPI:
    application = FastAPI()
    application.include_router(sd_router)
    application.dependency_overrides[get_site_definition_resolver] = lambda: (
        lambda bbl, cid: resolution
    )
    application.dependency_overrides[get_site_definition_store] = lambda: store
    return application


def enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


def _confirmer() -> dict:
    return {"name": "Dana Reviewer", "role": "qualified_professional"}


def _create_body(parcels: tuple[str, ...] = PARCELS, **extra: object) -> dict:
    body: dict = {"parcels": list(parcels), "confirmer": _confirmer()}
    body.update(extra)
    return body


def _url(bbl: str = BILLING_BBL) -> str:
    return f"/api/v1/properties/{bbl}/site-definition-confirmations"


# ---------------------------------------------------------------------------
# AS-5: route discipline
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404_with_no_correlation_leak():
    # No flag set -> the create route is byte-indistinguishable from an unmounted
    # path: generic 404, no correlation id.
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_malformed_bbl_is_typed_422(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(_url("not-a-bbl"), json=_create_body())
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"


def test_over_ceiling_body_is_413(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    oversized = b"{\"x\":\"" + b"9" * (MAX_BODY_BYTES + 1) + b"\"}"
    resp = client.post(
        _url(), content=oversized, headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 413
    assert resp.json()["state"] == "payload_too_large"


def test_non_multi_lot_resolution_is_422(monkeypatch):
    # A resolution that is not multi-lot has no site to confirm.
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _single()))
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 422
    assert "multi-lot" in resp.json()["message"]


# ---------------------------------------------------------------------------
# AS-1: create carries the self-attested, refused-for-calculation record
# ---------------------------------------------------------------------------
def test_create_succeeds_and_is_self_attested_and_refused(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 201
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    assert body["status"] == "active"
    assert body["condo_key"] == CONDO_KEY
    assert body["parcels"] == list(PARCELS)
    assert body["confirmer"]["role"] == "qualified_professional"
    assert body["attestation_status"] == "unauthenticated_self_attested"
    assert body["refused_for_calculation"] is True
    # Provenance is byte-copied from the resolution the route re-read.
    assert body["provenance"]["source_id"] == "nyc-dof-dtm-condo-soda"
    assert body["provenance"]["dataset_ids"] == ["p8u6-a6it"]
    # confirmed_at is a server-set tz-aware instant (parses as tz-aware).
    parsed = datetime.fromisoformat(body["confirmed_at"])
    assert parsed.tzinfo is not None


def test_attestation_is_server_set_an_untrusted_body_cannot_claim_authentication(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    # A hostile body claiming authentication (top-level AND inside confirmer) is
    # ignored: attestation is set server-side and stays self-attested/refused.
    body = _create_body(
        attestation_status="authenticated",
        refused_for_calculation=False,
        confirmer={
            "name": "Dana Reviewer",
            "role": "qualified_professional",
            "attestation_status": "authenticated",
        },
    )
    resp = client.post(_url(), json=body)
    assert resp.status_code == 201
    assert resp.json()["attestation_status"] == "unauthenticated_self_attested"
    assert resp.json()["refused_for_calculation"] is True


# ---------------------------------------------------------------------------
# AS-2: strict parcel binding
# ---------------------------------------------------------------------------
def test_divergent_parcel_set_is_typed_422(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(_url(), json=_create_body(parcels=("1003030019", "1003039999")))
    assert resp.status_code == 422
    body = resp.json()
    assert body["state"] == "validation_error"
    assert body["reject_code"] == "parcel_set_mismatch"


def test_reordered_parcel_set_still_succeeds(monkeypatch):
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(_url(), json=_create_body(parcels=(PARCELS[1], PARCELS[0])))
    assert resp.status_code == 201


# ---------------------------------------------------------------------------
# AS-3: append-only lifecycle over the route
# ---------------------------------------------------------------------------
def test_duplicate_active_create_is_409(monkeypatch):
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(_sd_app(store, _multi_lot()))
    assert client.post(_url(), json=_create_body()).status_code == 201
    dup = client.post(_url(), json=_create_body())
    assert dup.status_code == 409
    assert dup.json()["reject_code"] == "duplicate_active_confirmation"


def test_supersede_requires_a_reason_then_chains_a_new_active(monkeypatch):
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(_sd_app(store, _multi_lot()))
    created = client.post(_url(), json=_create_body()).json()
    old_id = created["record_id"]
    # No reason -> typed 422.
    no_reason = client.post(f"{_url()}/{old_id}/supersede", json=_create_body())
    assert no_reason.status_code == 422
    assert no_reason.json()["reject_code"] == "transition_reason_required"
    # With a reason -> a NEW active record chained to the old.
    ok = client.post(
        f"{_url()}/{old_id}/supersede",
        json=_create_body(reason="corrected the recorded confirmer"),
    )
    assert ok.status_code == 200
    new_body = ok.json()
    assert new_body["status"] == "active"
    assert new_body["supersedes_id"] == old_id
    assert new_body["record_id"] != old_id


def test_revoke_requires_a_reason_and_is_terminal(monkeypatch):
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(_sd_app(store, _multi_lot()))
    created = client.post(_url(), json=_create_body()).json()
    record_id = created["record_id"]
    # No reason -> 422.
    no_reason = client.post(
        f"{_url()}/{record_id}/revoke", json={"confirmer": _confirmer()}
    )
    assert no_reason.status_code == 422
    assert no_reason.json()["reject_code"] == "transition_reason_required"
    # With a reason -> revoked (terminal).
    ok = client.post(
        f"{_url()}/{record_id}/revoke",
        json={"confirmer": _confirmer(), "reason": "no longer treated as one site"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "revoked"
    # Revoking again is a conflict (not active).
    again = client.post(
        f"{_url()}/{record_id}/revoke",
        json={"confirmer": _confirmer(), "reason": "again"},
    )
    assert again.status_code == 409


def test_list_returns_the_whole_chain_newest_first(monkeypatch):
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(_sd_app(store, _multi_lot()))
    created = client.post(_url(), json=_create_body()).json()
    old_id = created["record_id"]
    superseded = client.post(
        f"{_url()}/{old_id}/supersede",
        json=_create_body(reason="corrected"),
    ).json()
    listing = client.get(_url())
    assert listing.status_code == 200
    block = listing.json()
    assert block["status"] == "confirmed"
    assert block["active_confirmation"]["record_id"] == superseded["record_id"]
    ids = [c["record_id"] for c in block["confirmations"]]
    assert ids == [superseded["record_id"], old_id]


# ---------------------------------------------------------------------------
# Router DEFAULT-OFF: the module-level app (no SITE_DEFINITION_WRITE_ENABLED)
# exposes no site-definition route (M5-T062 makes the mount flag-gated, default
# off; AS-5 exercises the on/off registration below).
# ---------------------------------------------------------------------------
def test_router_is_not_mounted_in_main_app_by_default():
    paths = {getattr(route, "path", "") for route in main_app.routes}
    assert not any("site-definition-confirmations" in path for path in paths)


# ---------------------------------------------------------------------------
# Shared-store integration: write route -> condo-records read document
# ---------------------------------------------------------------------------
def _unit_landmine():
    def _resolve(bbl: str, cid: str):
        raise AssertionError("unit resolver must not run for a billing BBL")

    return _resolve


def _shared_app(store: InMemorySiteDefinitionStore, resolution: CondoResolution) -> FastAPI:
    """A local app mounting BOTH routers over ONE shared store, so a confirmation
    created through the (unmounted) write route surfaces on the condo-records read
    document - the ``default_site_definition_store`` binding proven end to end."""
    application = FastAPI()
    application.include_router(sd_router)
    application.include_router(condo_router)
    application.dependency_overrides[get_site_definition_resolver] = lambda: (
        lambda bbl, cid: resolution
    )
    application.dependency_overrides[get_site_definition_store] = lambda: store
    application.dependency_overrides[get_condo_site_definition_store] = lambda: store
    application.dependency_overrides[get_condo_billing_resolver] = lambda: (
        lambda bbl, cid: resolution
    )
    application.dependency_overrides[get_condo_unit_resolver] = _unit_landmine
    return application


def test_created_confirmation_surfaces_on_the_condo_records_document(monkeypatch):
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(_shared_app(store, _multi_lot()))
    # Before any confirmation: the multi-lot document is honestly UNCONFIRMED.
    before = client.get(f"/api/v1/properties/{BILLING_BBL}/condo-records").json()
    assert before["outcome"] == OUTCOME_MULTI_LOT
    assert before["site_definition"]["status"] == "unconfirmed"
    assert before["site_definition"]["active_confirmation"] is None
    # Create through the write route...
    created = client.post(_url(), json=_create_body())
    assert created.status_code == 201
    # ...and it surfaces on the read document through the ONE shared store.
    after = client.get(f"/api/v1/properties/{BILLING_BBL}/condo-records").json()
    block = after["site_definition"]
    assert block["status"] == "confirmed"
    assert block["active_confirmation"]["record_id"] == created.json()["record_id"]
    assert block["active_confirmation"]["refused_for_calculation"] is True
    # AS-4 prohibition: surfacing a confirmation NEVER changes the outcome, the
    # base-lot records, or introduces any allowance - it is additive only.
    assert after["outcome"] == before["outcome"]
    assert after["base_lots"] == before["base_lots"]
    assert after["substitution"] is None
    # [T059 A-8] a precise structural guard replaces the brittle "far" substring
    # scan: the whole document EXCEPT the site_definition block is byte-identical
    # before/after, so ANY leakage into the rest of the document is caught (not
    # only a word that happens to contain "far").
    before_rest = {k: v for k, v in before.items() if k != "site_definition"}
    after_rest = {k: v for k, v in after.items() if k != "site_definition"}
    assert after_rest == before_rest


# ---------------------------------------------------------------------------
# [ORCH-CORRECTED per T059 G3-C1 / G5-F1] rework binding (seq 122)
# ---------------------------------------------------------------------------
def test_cross_condo_revoke_is_a_typed_refusal_and_leaves_the_record_active(
    monkeypatch,
):
    """A revoke addressed at a property whose condo differs from the record's is
    a typed not-found (mirroring supersede's binding) and the record stays
    ACTIVE - the G5-F1 cross-property class cannot terminate another condo's
    site definition."""
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    app_a = _sd_app(store, _multi_lot())
    app_b = _sd_app(store, _multi_lot(condo_key="999999"))
    client_a = TestClient(app_a, raise_server_exceptions=False)
    client_b = TestClient(app_b, raise_server_exceptions=False)

    created = client_a.post(
        f"/api/v1/properties/{BILLING_BBL}/site-definition-confirmations",
        json={
            "parcels": list(PARCELS),
            "confirmer": {"name": "Dana Reviewer", "role": "qualified_professional"},
        },
    )
    assert created.status_code == 201, created.json()
    record_id = created.json()["record_id"]

    crossed = client_b.post(
        f"/api/v1/properties/{BILLING_BBL}/site-definition-confirmations/"
        f"{record_id}/revoke",
        json={
            "confirmer": {"name": "Mallory", "role": "user"},
            "reason": "cross-condo attempt",
        },
    )
    assert crossed.status_code == 404, crossed.json()
    assert crossed.json()["state"] == "not_found"

    still = client_a.get(
        f"/api/v1/properties/{BILLING_BBL}/site-definition-confirmations"
    )
    assert still.status_code == 200
    assert still.json()["status"] == "confirmed"
    assert still.json()["active_confirmation"]["record_id"] == record_id

    bound = client_a.post(
        f"/api/v1/properties/{BILLING_BBL}/site-definition-confirmations/"
        f"{record_id}/revoke",
        json={
            "confirmer": {"name": "Dana Reviewer", "role": "qualified_professional"},
            "reason": "legitimate revocation at the addressed property",
        },
    )
    assert bound.status_code == 200, bound.json()


# ===========================================================================
# M5-T062 — DB-040 mount-precondition route hardening + the flag-gated mount
# ===========================================================================
WALLABOUT_BILLING = "3022647515"  # the DB-040 named 298-Wallabout condo fixture
WALLABOUT_PARCELS = ("3022640032", "3022640033")
WALLABOUT_CONDO_KEY = "3022643344"  # synthetic condo grouping for the fixture


def _wallabout_multi_lot() -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_MULTI_LOT,
        input_bbl=WALLABOUT_BILLING,
        correlation_id="test-corr",
        base_bbls=WALLABOUT_PARCELS,
        resolved_base_bbl=None,
        condo_key=WALLABOUT_CONDO_KEY,
        condo_number="3344",
        resolution_path="billing",
        source_id="nyc-dof-dtm-condo-soda",
        dataset_ids=("p8u6-a6it",),
        retrieved_at="2026-09-01T14:05:56.732000Z",
        provenance=({"dataset_id": "p8u6-a6it", "query_kind": "condo_billing_bbl"},),
        divergent_zoning_notice=DIVERGENT_NOTICE,
        notes=("multi-lot condo: 2 base lots resolved; never collapsed.",),
    )


def _unresolved() -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_UNRESOLVED,
        input_bbl=BILLING_BBL,
        correlation_id="test-corr",
        condo_key=None,
        source_id="nyc-dof-dtm-condo-soda",
        dataset_ids=("p8u6-a6it",),
    )


def _error_outcome() -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_ERROR,
        input_bbl=BILLING_BBL,
        correlation_id="test-corr",
        error_type="unavailable",
        source_id="nyc-dof-dtm-condo-soda",
    )


def _degraded_resolvers() -> dict:
    def _raises(bbl, cid):
        raise RuntimeError("resolver down")

    return {
        "single": lambda bbl, cid: _single(),
        "unresolved": lambda bbl, cid: _unresolved(),
        "multi_lot_null_condo_key": lambda bbl, cid: _multi_lot(condo_key=None),
        "error": lambda bbl, cid: _error_outcome(),
        "raises": _raises,
    }


# ---------------------------------------------------------------------------
# AS-2: degraded-safe revoke over the route (D-051 fail-direction)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "label", ["single", "unresolved", "multi_lot_null_condo_key", "error", "raises"]
)
def test_revoke_survives_each_degraded_resolver_class_over_the_route(monkeypatch, label):
    # [DB-040(b) / T059 G3-delta F-10 + G4-delta A-9] revoke is the ONLY human
    # withdrawal path, so a degraded resolver must NEVER block it. Create with a
    # healthy resolver, then revoke under each degraded class - the withdrawal
    # still succeeds via the record's own addressed BBL.
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    app = _sd_app(store, _multi_lot())  # healthy for create
    client = TestClient(app, raise_server_exceptions=False)
    created = client.post(_url(), json=_create_body())
    assert created.status_code == 201, created.json()
    record_id = created.json()["record_id"]
    degraded = _degraded_resolvers()[label]
    app.dependency_overrides[get_site_definition_resolver] = lambda: degraded
    revoked = client.post(
        f"{_url()}/{record_id}/revoke",
        json={"confirmer": _confirmer(), "reason": f"withdraw under {label}"},
    )
    assert revoked.status_code == 200, revoked.json()
    assert revoked.json()["status"] == "revoked"


def test_degraded_revoke_over_the_route_still_refuses_a_foreign_property_probe(
    monkeypatch,
):
    # A degraded resolver does NOT open a cross-property bypass: a probe addressed
    # at a DIFFERENT property is still a typed 404 and the record stays active.
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    app = _sd_app(store, _multi_lot())
    client = TestClient(app, raise_server_exceptions=False)
    created = client.post(_url(), json=_create_body())
    record_id = created.json()["record_id"]
    app.dependency_overrides[get_site_definition_resolver] = lambda: (
        lambda bbl, cid: _single()
    )
    foreign = client.post(
        f"/api/v1/properties/1003030019/site-definition-confirmations/"
        f"{record_id}/revoke",
        json={"confirmer": _confirmer(), "reason": "foreign probe, degraded resolver"},
    )
    assert foreign.status_code == 404, foreign.json()
    assert foreign.json()["state"] == "not_found"
    still = client.get(_url())
    assert still.json()["active_confirmation"]["record_id"] == record_id


# ---------------------------------------------------------------------------
# AS-3 / AS-4: typed shape refusals, matrix enforcement, condo_key-None write
# ---------------------------------------------------------------------------
def test_malformed_parcels_refuse_under_the_parcel_shape_code_not_invalid_confirmer(
    monkeypatch,
):
    # [DB-040(i) / T059 G3-F-2/A-6] a malformed parcels value refuses under its OWN
    # reject_code (parcel_set_shape), never mislabelled invalid_confirmer.
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    resp = client.post(
        _url(), json={"parcels": "not-a-list", "confirmer": _confirmer()}
    )
    assert resp.status_code == 422
    assert resp.json()["reject_code"] == "parcel_set_shape"


def test_a_multi_lot_resolution_with_no_condo_key_refuses_create(monkeypatch):
    # [DB-040(j) / T059 G3-F-4] the write side closes the condo_key-None asymmetry:
    # a multi-lot resolution with no condo key cannot be KEYED, so a confirmation
    # recorded for it could never surface on the read document (which keys on
    # condo_key). The write REFUSES rather than record an un-surfaceable record.
    enable_flag(monkeypatch)
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot(condo_key=None)))
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 422
    assert resp.json()["state"] == "validation_error"
    assert "condo key" in resp.json()["message"]


def test_status_state_matrix_contains_the_documented_pairs():
    # [DB-040(k)] the exact (status, state) pairs every emission path may use.
    for pair in (
        (200, None),
        (201, None),
        (404, None),
        (404, "not_found"),
        (409, "conflict"),
        (413, "payload_too_large"),
        (422, "validation_error"),
        (500, "internal_error"),
    ):
        assert pair in SITE_DEFINITION_STATUS_STATE_MATRIX


def test_emission_matrix_is_enforced_not_decorative(monkeypatch):
    # [DB-040(k) / T059 G3-F-5] _json ASSERTS every (status, state) pair against the
    # matrix and FAILS CLOSED to (500, internal_error) on an off-matrix pair.
    # Neutralize the matrix (drop the success pair) and a create that would emit
    # (201, None) is forced to 500 - proving the matrix is enforced, not decorative.
    enable_flag(monkeypatch)
    monkeypatch.setattr(
        "app.api.v1.site_definition.SITE_DEFINITION_STATUS_STATE_MATRIX",
        frozenset({(500, "internal_error")}),
    )
    client = TestClient(
        _sd_app(InMemorySiteDefinitionStore(), _multi_lot()),
        raise_server_exceptions=False,
    )
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 500
    assert resp.json()["state"] == "internal_error"


# ---------------------------------------------------------------------------
# AS-5 (route discipline): flag-off sentinel on ALL routes + streaming 413
# ---------------------------------------------------------------------------
def test_flag_off_all_routes_are_generic_404_with_no_correlation_leak():
    # [T059 A-1] the handler flag-off sentinel is byte-identical to an unmounted
    # path on EVERY route (list / supersede / revoke), not only create.
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    listing = client.get(_url())
    supersede = client.post(f"{_url()}/rec/supersede", json=_create_body(reason="r"))
    revoke = client.post(
        f"{_url()}/rec/revoke", json={"confirmer": _confirmer(), "reason": "r"}
    )
    for resp in (listing, supersede, revoke):
        assert resp.status_code == 404
        assert resp.json() == {"detail": "Not Found"}
        assert "X-Correlation-ID" not in resp.headers


def test_streaming_accumulation_catches_an_under_reporting_body(monkeypatch):
    # [T059 A-2] the STREAMING guard exists for a chunked / under-reporting
    # Content-Length. Neutralize the declared-length guard (simulate an
    # under-reporting body) and the streaming accumulation must still refuse the
    # instant the aggregate exceeds the ceiling - proving the guard is load-bearing
    # (deleting it would let the oversized body through the declared branch).
    enable_flag(monkeypatch)
    monkeypatch.setattr(
        "app.api.v1.site_definition._declared_content_length", lambda request: None
    )
    client = TestClient(_sd_app(InMemorySiteDefinitionStore(), _multi_lot()))
    oversized = b'{"x":"' + b"9" * (MAX_BODY_BYTES + 1) + b'"}'
    resp = client.post(
        _url(), content=oversized, headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 413
    assert resp.json()["state"] == "payload_too_large"


# ---------------------------------------------------------------------------
# AS-5 (mount): the flag-gated, default-OFF main.py mount
# ---------------------------------------------------------------------------
def test_production_default_leaves_the_write_mount_flag_off():
    # [AS-5] production sets nothing -> the write mount flag is OFF (fail safe);
    # only an explicit true token turns it on.
    assert site_definition_write_enabled({}) is False
    assert site_definition_write_enabled({SITE_DEFINITION_WRITE_ENABLED_ENV_VAR: ""}) is False
    assert site_definition_write_enabled({SITE_DEFINITION_WRITE_ENABLED_ENV_VAR: "maybe"}) is False
    for token in ("1", "true", "TRUE", "yes", "on"):
        assert (
            site_definition_write_enabled({SITE_DEFINITION_WRITE_ENABLED_ENV_VAR: token})
            is True
        )


def test_flag_off_the_app_registers_no_site_definition_route(monkeypatch):
    # [AS-5] with the mount flag OFF (default), create_app() registers NO
    # site-definition route: any path hits FastAPI's generic unmounted 404.
    monkeypatch.delenv(SITE_DEFINITION_WRITE_ENABLED_ENV_VAR, raising=False)
    application = create_app()
    paths = {getattr(r, "path", "") for r in application.routes}
    assert not any("site-definition-confirmations" in p for p in paths)
    client = TestClient(application)
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


def test_flag_on_the_app_mounts_the_site_definition_routes_and_they_serve(monkeypatch):
    # [AS-5] with the mount flag ON, create_app() registers the routes; with the
    # handler flag ALSO on and the deps overridden, they serve.
    monkeypatch.setenv(SITE_DEFINITION_WRITE_ENABLED_ENV_VAR, "1")
    enable_flag(monkeypatch)  # INTERNAL_RULE_EVAL_ENABLED for the handler
    application = create_app()
    paths = {getattr(r, "path", "") for r in application.routes}
    assert any("site-definition-confirmations" in p for p in paths)
    store = InMemorySiteDefinitionStore()
    application.dependency_overrides[get_site_definition_resolver] = lambda: (
        lambda bbl, cid: _multi_lot()
    )
    application.dependency_overrides[get_site_definition_store] = lambda: store
    client = TestClient(application)
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 201, resp.json()


def test_mount_flag_on_but_handler_flag_off_is_still_a_generic_404(monkeypatch):
    # [AS-5] the write route needs BOTH flags: registered (mount flag) AND the
    # handler flag. With the mount flag on but INTERNAL_RULE_EVAL_ENABLED off, the
    # route is registered but every path is the generic sentinel 404 - so turning
    # on the general internal flag alone can never expose the write route.
    monkeypatch.setenv(SITE_DEFINITION_WRITE_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, raising=False)
    application = create_app()
    application.dependency_overrides[get_site_definition_resolver] = lambda: (
        lambda bbl, cid: _multi_lot()
    )
    application.dependency_overrides[get_site_definition_store] = lambda: (
        InMemorySiteDefinitionStore()
    )
    client = TestClient(application)
    resp = client.post(_url(), json=_create_body())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


# ---------------------------------------------------------------------------
# AS-1: the named 298-Wallabout condo fixture exercised END TO END
# ---------------------------------------------------------------------------
def test_named_wallabout_condo_confirmation_end_to_end(monkeypatch):
    # [DB-040(n) / T059 A-5] the owner-cited named class (billing 3022647515 ->
    # base lots 3022640032/3022640033), not only a synthetic Manhattan stand-in:
    # create -> list -> revoke through the route.
    enable_flag(monkeypatch)
    store = InMemorySiteDefinitionStore()
    client = TestClient(
        _sd_app(store, _wallabout_multi_lot()), raise_server_exceptions=False
    )
    url = f"/api/v1/properties/{WALLABOUT_BILLING}/site-definition-confirmations"
    created = client.post(
        url, json={"parcels": list(WALLABOUT_PARCELS), "confirmer": _confirmer()}
    )
    assert created.status_code == 201, created.json()
    body = created.json()
    assert body["parcels"] == list(WALLABOUT_PARCELS)
    assert body["condo_key"] == WALLABOUT_CONDO_KEY
    assert body["refused_for_calculation"] is True
    record_id = body["record_id"]
    listing = client.get(url)
    assert listing.json()["status"] == "confirmed"
    assert listing.json()["active_confirmation"]["record_id"] == record_id
    revoked = client.post(
        f"{url}/{record_id}/revoke",
        json={"confirmer": _confirmer(), "reason": "withdraw the Wallabout assembly"},
    )
    assert revoked.status_code == 200, revoked.json()
    assert revoked.json()["status"] == "revoked"
