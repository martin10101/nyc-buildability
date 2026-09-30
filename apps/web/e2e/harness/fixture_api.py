"""RECORDED-OFFICIAL-FIXTURE API HARNESS for Playwright e2e (task M2-T001).

WHAT THIS IS: the REAL FastAPI application (services/api/app) with exactly
one seam overridden — the PLUTO fetcher dependency (the same
``get_pluto_fetcher`` FastAPI dependency-override seam the accepted
M1-T005 test suite uses). Every 200/404 response is produced by the REAL
connector + profile builder running over COMMITTED OFFICIAL live-capture
fixtures (services/api/tests/fixtures/pluto/*.json, accepted in M1-T002).

WHAT THIS IS NOT: a frontend mock. No response body is hand-written here;
route, connector, builder, validation, and error mapping are the production
code paths. Fixtures live only in tests/harness — the web application
itself contains no mocked success path (scenario S7).

This file lives OUTSIDE services/** (forbidden path for task M2-T001) and
only imports from the installed ``app`` package.

BBL routing table (all BBLs are format-valid; block/lot never all-zero):

  1000010010  F05 split-zone lot (Governors Island; S1 primary)
  1000010100  F01 single lot normal (S2 boundary values, D5 fallback join)
  1000010101  F04 null-field omission (S6 partial data: numfloors missing)
  1000041001  F02b condo unit lot -> 404 no_match with billing-lot text (S4)
  5999999999  F03b valid borough-5 BBL with no record -> 404 no_match (S2)
  1000010103  SYNTHETIC borocode-conflict variant of F01 (S6 conflict UI):
              identity columns rewritten to the requested control BBL, then
              borocode mutated "1" -> "3" — the exact synthetic-variant
              technique of the accepted M1-T005 S4 test. Clearly synthetic;
              never presented as official data.
  3000010001  upstream failure: rate_limited (F07 replayed x3)   -> 503
  3000010002  upstream failure: timeout (x3)                     -> 504
  3000010003  upstream failure: source_unavailable (x3)          -> 503
  3000010004  upstream failure: schema_drift (F13)               -> 502
  3000010005  fetcher raises -> documented generic 500

Any other (valid) BBL serves F03b's empty result -> 404 no_match.

CORS NOTE (test infrastructure, documented in the producer report): the
deployed API currently has no CORS policy, and services/** may not be
edited by this task. The browser page (127.0.0.1:3000) calls the API
(127.0.0.1:8000) cross-origin, so this harness adds CORSMiddleware for the
test origin only. A reviewed CORS/proxy decision is required before any
real cross-origin deployment; flagged as a follow-up in the report.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.address_resolution import get_address_resolver
from app.api.v1.lot_geometry import get_lot_outline_fetcher
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.config import (
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
)
from app.connectors.geoclient_address import AddressResolution
from app.connectors.mappluto_lot_outline import (
    LotOutlineTransport,
    build_outline_query_url,
)
from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
    fetch_by_bbl,
)
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "pluto"

# Deterministic clock (same instant the accepted M1-T005 tests use) so
# retrieved_at values in e2e assertions are stable.
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731

FIXTURE_BY_BBL = {
    "1000010010": "F05_split_zone_lot.json",
    "1000010100": "F01_single_lot_normal.json",
    "1000010101": "F04_null_field_omission.json",
    "1000041001": "F02b_condo_unit_lot_no_match.json",
    "5999999999": "F03b_no_match_valid_bbl.json",
}

SYNTHETIC_CONFLICT_BBL = "1000010103"
INTERNAL_ERROR_BBL = "3000010005"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_response(name: str) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


def synthetic_conflict_body(bbl: str) -> str:
    """Derive the labeled SYNTHETIC borocode-conflict record from F01.

    Derivation (documented; mirrors the accepted M1-T005 S4 test):
    1. Start from the committed official F01 record verbatim.
    2. Rewrite the identity columns (bbl, block, lot) to the requested
       control BBL so they stay self-consistent.
    3. Mutate borocode to "3", disagreeing with the BBL's borough digit 1.
    No other value is touched; no official value is invented.
    """
    record = json.loads(load_fixture("F01_single_lot_normal.json")["response_body_raw"])[0]
    record["bbl"] = f"{bbl}.00000000"
    record["block"] = str(int(bbl[1:6]))
    record["lot"] = str(int(bbl[6:10]))
    record["borocode"] = "3"
    return json.dumps([record])


def make_script(bbl: str) -> list:
    """Transport script (responses/exceptions) for one request of ``bbl``."""
    if bbl == "3000010001":
        return [fixture_response("F07_rate_limit_429_synthetic.json")] * 3
    if bbl == "3000010002":
        return [TransportTimeout("timeout after 10.0s")] * 3
    if bbl == "3000010003":
        return [TransportFailure("network failure: OSError")] * 3
    if bbl == "3000010004":
        return [fixture_response("F13_schema_drift_no_such_column_400.json")]
    if bbl == SYNTHETIC_CONFLICT_BBL:
        return [TransportResponse(200, synthetic_conflict_body(bbl))]
    name = FIXTURE_BY_BBL.get(bbl, "F03b_no_match_valid_bbl.json")
    return [fixture_response(name)]


class ScriptedTransport:
    """Replays a scripted sequence of responses/exceptions (test seam)."""

    def __init__(self, script: list):
        self.script = list(script)

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        if not self.script:
            raise AssertionError("harness transport script exhausted")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def harness_fetcher(bbl: str, correlation_id: str):
    if bbl == INTERNAL_ERROR_BBL:
        # Exercises the documented generic-500 contract (G3 D1 fix).
        raise RuntimeError("harness-injected unexpected failure")
    return fetch_by_bbl(
        bbl,
        transport=ScriptedTransport(make_script(bbl)),
        sleep=lambda seconds: None,  # no real backoff delays in e2e
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


# ---------------------------------------------------------------------------
# M4-T005 phase 3: server-side spatial substrate for the internal draft
# rule-evaluation endpoint. The endpoint rebuilds the profile SERVER-SIDE and
# runs the real deterministic evaluator; the ONLY seam is the substrate
# provider (never browser-supplied), overridden here with the SAME faithful
# M2-T013 substrate dicts the accepted phase-2 API acceptance pack uses
# (services/api/tests/api/test_rule_evaluation_api.py: _pair / _substrate). No
# rule-evaluation body is hand-written; route, builder, evaluator, serializer,
# and strict validation are the production code paths.
#
# Substrate routing (drives the six UI states through the REAL endpoint):
#   1000010100 (F01) -> confident single R5 district      -> applicable draft
#   1000010010 (F05) -> split lot R5/R6 with share RANGES  -> spatial uncertainty
#   any other BBL    -> None (no substrate wired)          -> professional-review
#                                                             fail-safe (missing
#                                                             evidence)
# ---------------------------------------------------------------------------

RULE_EVAL_CONFIDENT_BBL = "1000010100"
RULE_EVAL_SPLIT_LOT_BBL = "1000010010"


def _pair(label: str, pair_class: str, *, lot_area=10000.0, share=(1.0, 1.0, 1.0), minor=False):
    smin, spoint, smax = share
    return {
        "layer": "nyzd",
        "family": "base_zoning",
        "district_label": label,
        "pair_class": pair_class,
        "raw_intersection_sq_ft": lot_area * spoint,
        "firm_intersection_sq_ft": lot_area * spoint,
        "dilated_intersection_sq_ft": lot_area * smax,
        "distance_ft": 0.0,
        "lot_area_sq_ft": lot_area,
        "share_min": smin,
        "share_point": spoint,
        "share_max": smax,
        "minor_portion": minor,
    }


def _substrate(bbl: str, lot_overall_class: str, pairs: list, *, review: bool, review_reasons=None):
    return {
        "bbl": bbl,
        "lot_overall_class": lot_overall_class,
        "pairs": pairs,
        "coverage_audits": [{"family": "base_zoning", "status": "unknown"}],
        "crosscheck": None,
        "professional_review_required": review,
        "review_reasons": review_reasons or [],
        "unassigned_area": [],
        "overlap_area": [],
        "accuracy_records": [{"applies_to": "lot", "value_ft": 20.0, "basis": "documented"}],
        "policy": {"version": "policy-1"},
        "provenance": {
            "source_id": "nyc-dcp-mappluto-arcgis",
            "requested_bbl": bbl,
            "retrieved_at": "2026-07-16T12:00:00Z",
            "normalized_digest": "sha256:" + "e" * 64,
            "source_data_last_edited": "2026-07-15T00:00:00Z",
        },
        "coverage_note": "facts_with_uncertainty; not a Verified zoning determination",
        "notes": [],
    }


def harness_substrate_provider(canonical_bbl: str, correlation_id: str):
    if canonical_bbl == RULE_EVAL_CONFIDENT_BBL:
        return _substrate(
            canonical_bbl,
            "single_district_confident",
            [_pair("R5", "interior_confident")],
            review=False,
        )
    if canonical_bbl == RULE_EVAL_SPLIT_LOT_BBL:
        return _substrate(
            canonical_bbl,
            "split_lot_confident",
            [
                _pair("R5", "split_confident", share=(0.55, 0.60, 0.65)),
                _pair("R6", "split_confident", share=(0.35, 0.40, 0.45), minor=True),
            ],
            review=True,
            review_reasons=["lot_overall_class=split_lot_confident"],
        )
    return None


# ---------------------------------------------------------------------------
# M5-T023 (D-040-R001): display-only lot-outline surface on the address confirm
# card. TWO seams are overridden so the browser can walk the surface entirely
# OFFLINE against RECORDED OFFICIAL data:
#
#   1. get_lot_outline_fetcher -> a scripted transport that returns the VERBATIM
#      recorded official ArcGIS f=geojson&outSR=4326 fixtures
#      (services/api/tests/fixtures/mappluto_lot_outline, task M5-T020). The REAL
#      route + REAL builder (parse + contract validation) run over them, so the
#      served outline documents are production code paths — NO geometry byte is
#      hand-written here (the same recorded-official-fixture discipline the PLUTO
#      seam above uses). Distinct BBLs select the outcomes the walkthrough needs.
#   2. get_address_resolver -> a small SYNTHETIC test resolver (the same test-seam
#      pattern as harness_substrate_provider below) that maps a handful of test
#      street names to AddressResolution results carrying a canonical BBL. This
#      is scaffolding ONLY: no prior task wired an address-resolution seam, and
#      the confirm card (hence the lot-outline surface) is reachable only through
#      a resolved address. The resolver is clearly synthetic; the GEOMETRY it
#      leads to is the real recorded data from seam (1).
# ---------------------------------------------------------------------------

LOT_OUTLINE_FIXTURE_DIR = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "mappluto_lot_outline"
)
LOT_OUTLINE_RETRIEVED_AT = "2026-09-12T13:45:07Z"

# Canonical BBL -> recorded raw ArcGIS fixture. LOT80 (invalid_geometry) is NOT
# routable by a distinct BBL: its synthetic feature carries BBL 1008350041, and
# the builder's single-feature result-match check would raise result_mismatch
# for any other requested BBL - so invalid_geometry is proven in the offline
# vitest pack (via the contract fixture) rather than the browser walkthrough.
LOT_OUTLINE_BY_BBL = {
    "1008350041": "LOT01_single_1008350041.geojson",  # single_lot Polygon (S1)
    "5999999999": "LOT02_nofeature_5999999999.geojson",  # no_outline no_feature
    "1000157501": "LOT03_condo_billing_1000157501.geojson",  # single_lot condo billing
    "1000151001": "LOT04_condo_unit_1000151001.geojson",  # no_outline condo unit (S3)
    "1000010010": "LOT05_holes_1000010010.geojson",  # single_lot with holes
    "4142600001": "LOT06_multipolygon_4142600001.geojson",  # single_lot MultiPolygon
    "1008350096": "LOT96_multiple_features_synthetic.geojson",  # multiple_features (S3)
}
# A designated BBL that models an upstream transport fault (official service
# returned a non-200): the builder raises LotOutlineError and the route maps it
# to 502 upstream_error, exercising the client's typed error fallback (S4).
LOT_OUTLINE_UPSTREAM_FAIL_BBL = "2000020002"


def harness_lot_outline_fetcher(canonical_bbl: str, correlation_id: str) -> LotOutlineTransport:
    """Return a recorded-fixture transport for one canonical BBL (or a modeled
    upstream fault). The URL is the REAL bounded query URL; the body is verbatim
    recorded official bytes (or empty on the modeled fault)."""
    url = build_outline_query_url(canonical_bbl, correlation_id=correlation_id)
    if canonical_bbl == LOT_OUTLINE_UPSTREAM_FAIL_BBL:
        return LotOutlineTransport(
            url=url, status=500, body="{}", retrieved_at=LOT_OUTLINE_RETRIEVED_AT
        )
    name = LOT_OUTLINE_BY_BBL.get(canonical_bbl, "LOT02_nofeature_5999999999.geojson")
    body = (LOT_OUTLINE_FIXTURE_DIR / name).read_text(encoding="utf-8")
    return LotOutlineTransport(
        url=url, status=200, body=body, retrieved_at=LOT_OUTLINE_RETRIEVED_AT
    )


# Test street name -> canonical BBL the resolver returns. The e2e fills these
# exact street names to drive each lot-outline outcome through the real address
# confirm card. Any other street resolves to the single_lot outline BBL.
ADDRESS_BBL_BY_STREET = {
    "OUTLINE AVENUE": "1008350041",  # single_lot outline (S1 primary)
    "HOLES ISLAND": "1000010010",  # single_lot with interior holes
    "MULTIPART ROAD": "4142600001",  # single_lot MultiPolygon
    "CONDO UNIT WAY": "1000151001",  # condo unit -> honest-empty (S3)
    "REVIEW PLAZA": "1008350096",  # multiple_features -> review posture (S3)
    "OUTLINE FAIL ROAD": LOT_OUTLINE_UPSTREAM_FAIL_BBL,  # typed error fallback (S4)
}


def harness_address_resolver(
    house_number: str,
    street: str,
    *,
    borough: str | None = None,
    zip_code: str | None = None,
) -> AddressResolution:
    """SYNTHETIC test resolver: resolve a test street to a canonical BBL so the
    address confirm card renders. Clearly not official data; only the geometry
    the card then loads (seam 1) is recorded official data."""
    key = (street or "").strip().upper()
    bbl = ADDRESS_BBL_BY_STREET.get(key, "1008350041")
    correlation_id = uuid.uuid4().hex
    return AddressResolution(
        status="resolved",
        correlation_id=correlation_id,
        house_number_in=house_number,
        street_in=street,
        borough_in=borough,
        zip_in=zip_code,
        bbl=bbl,
        bin=None,
        street_name_normalized=key or "OUTLINE AVENUE",
        borough_name=(borough or "Manhattan").upper(),
        zip_code=None,
        grc="00",
        grc2="00",
        suggestions=[],
        raw_fields={"bbl": bbl},
        provenance={
            "source_id": "nyc-geoclient",
            "endpoint": "https://api.nyc.gov/geo/geoclient/v2/address",
            "request_params": {
                "houseNumber": house_number,
                "street": street,
                "borough": borough or "",
            },
            "retrieved_at": "2026-07-16T12:00:00Z",
            "http_status": 200,
            "geosupport_return_code": "00",
            "geosupport_return_code2": "00",
            "reason_code": None,
            "reason_code2": None,
            "response_digest": "sha256:" + "a" * 64,
            "digest_canonicalization": "canonical-json-1",
            "correlation_id": correlation_id,
        },
    )


def build_app():
    # M4-T005: enable the internal rule-evaluation endpoint's SERVER flag for
    # this test process only (independent of the frontend flag). The no-call
    # frontend spec still proves the browser issues no request when the surface
    # is not opted in, regardless of this server-side flag.
    os.environ[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR] = "1"
    # M5-T004 rework: enable the internal SCENARIO endpoint's server flag for
    # this test process too. Until now the harness enabled only the
    # rule-evaluation flag, so GET /api/v1/properties/{bbl}/scenario returned
    # the flag-off generic 404 and NO BROWSER COULD REACH /property/compare
    # anywhere in the repository — which is why G3 could not discharge its
    # browser-walkthrough step and no Playwright spec covered the screen.
    # Same seams as the rule-evaluation route: the scenario endpoint rebuilds
    # the profile and the rule evaluation server-side through get_pluto_fetcher
    # and get_spatial_substrate_provider, both already overridden below, so
    # enabling the flag is all that is required — no new mock and no new
    # fixture. Test process only; unset in production, where the route 404s.
    os.environ[INTERNAL_SCENARIO_ENABLED_ENV_VAR] = "1"
    app.dependency_overrides[get_pluto_fetcher] = lambda: harness_fetcher
    app.dependency_overrides[get_spatial_substrate_provider] = (
        lambda: harness_substrate_provider
    )
    # M5-T023: the lot-outline transport seam (recorded official fixtures through
    # the real builder) and the synthetic address resolver that makes the confirm
    # card reachable. Both are test-process only; production uses the live keyless
    # GET and the real Geoclient connector, and the route 404s when the flag is
    # off (INTERNAL_RULE_EVAL_ENABLED, enabled above for this process).
    app.dependency_overrides[get_lot_outline_fetcher] = (
        lambda: harness_lot_outline_fetcher
    )
    app.dependency_overrides[get_address_resolver] = (
        lambda: harness_address_resolver
    )
    # Test-origin CORS only (see module docstring CORS NOTE).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
        allow_methods=["GET"],
        allow_headers=["Accept"],
        expose_headers=["X-Correlation-ID"],
    )
    return app


if __name__ == "__main__":
    port = int(os.environ.get("HARNESS_PORT", "8000"))
    uvicorn.run(build_app(), host="127.0.0.1", port=port, log_level="warning")
