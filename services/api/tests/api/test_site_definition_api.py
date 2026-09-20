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
    get_site_definition_resolver,
    get_site_definition_store,
)
from app.api.v1.site_definition import router as sd_router
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.condo_base_lot import (
    OUTCOME_MULTI_LOT,
    OUTCOME_RESOLVED_SINGLE,
    CondoResolution,
)
from app.main import app as main_app
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
# Router UNMOUNTED: main.py exposes no site-definition route
# ---------------------------------------------------------------------------
def test_router_is_not_mounted_in_main_app():
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
    assert "far" not in str(after).lower()
