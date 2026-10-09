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
edited by this task. The browser pages (127.0.0.1:3000 flag-off and, for
D-1 slice 2, 127.0.0.1:3001 flag-on) call the API (127.0.0.1:8000)
cross-origin, so this harness adds CORSMiddleware for those test origins
only. A reviewed CORS/proxy decision is required before any real
cross-origin deployment; flagged as a follow-up in the report.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from random import Random
from urllib.parse import parse_qs, urlparse

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.address_resolution import get_address_resolver
from app.api.v1.hidden_issue_flags_inputs import pluto_hidden_issue_flag_inputs_provider
from app.api.v1.hidden_issue_flags_read import get_hidden_issue_flag_inputs_provider
from app.api.v1.lot_geometry import get_lot_outline_fetcher, get_tax_map_outline_fetcher
from app.api.v1.parity_read import (
    CANDIDATE_ROW_LIMIT,
    SUBJECT_SALES_ROW_LIMIT,
    get_dof_transport,
)
from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.results_read import get_results_study_inputs_provider
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.api.v1.study_inputs import (
    StudyInputsUnavailableError,
    assemble_study_inputs,
    pluto_study_inputs_provider,
)
from app.api.v1.study_read import get_study_inputs_provider
from app.api.v1.transit_parking_read import (
    get_transit_parking_provider,
    pluto_transit_parking_provider,
)
from app.config import (
    INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR,
    INTERNAL_PARITY_READ_ENABLED_ENV_VAR,
    INTERNAL_RESULTS_ENABLED_ENV_VAR,
    INTERNAL_RULE_EVAL_ENABLED_ENV_VAR,
    INTERNAL_SCENARIO_ENABLED_ENV_VAR,
    INTERNAL_STUDY_READ_ENABLED_ENV_VAR,
    INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR,
    LANE_FLAG_ENV_VARS,
)
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import parse_segment_geometry_page
from app.connectors.dof_sales_soda import build_by_bbl_url, build_candidates_url
from app.connectors.dtm_lot_outline import build_outline_query_url as dtm_outline_query_url
from app.connectors.geoclient_address import AddressResolution, resolve_address
from app.connectors.mappluto_geometry_arcgis import fetch_lot_geometry
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
from app.connectors.pluto_version_probe import (
    VERSION_PROBE_URL,
    fetch_published_version,
)
from app.main import app
from app.resilience.transport import TransportResponse as DofTransportResponse
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
    street_envelope_for_lot,
)
from app.spatial.site_geometry.outline import prepare_outline

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
#      leads to is the real recorded data from seam (1). The DEFAULT stays this
#      synthetic resolver (so every existing e2e is byte-identical); an OPT-IN
#      recorded-Geoclient resolver (``harness_recorded_geoclient_resolver``,
#      defined below, NOT wired as the default) runs the REAL Geoclient
#      connector over the recorded G01 documented-example body for a caller that
#      wants the real address->BBL path (D-090-R124; Tier-D note there).
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


def harness_tax_map_outline_fetcher(canonical_bbl: str, correlation_id: str) -> LotOutlineTransport:
    """Recorded DOF bytes through the real parser/route; never live test I/O."""
    fixture_dir = REPO_ROOT / "services/api/tests/fixtures/dtm_lot_outline"
    manifest = json.loads((fixture_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    capture = next((item for item in manifest["captures"] if item["bbl"] == canonical_bbl), None)
    body = (
        (fixture_dir / capture["file"]).read_text(encoding="utf-8") if capture
        else '{"type":"FeatureCollection","features":[]}'
    )
    return LotOutlineTransport(
        url=dtm_outline_query_url(canonical_bbl), status=200, body=body,
        retrieved_at=capture["retrieved_at"] if capture else "2026-09-26T20:22:01Z",
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


# ---------------------------------------------------------------------------
# D-090-R124 (Lane C W1-08): an OPT-IN recorded-Geoclient resolver beside the
# synthetic one above. It is NOT the harness default - the build_app override
# below stays ``harness_address_resolver``, so every existing e2e is
# byte-identical. It exists so the address->BBL step can be driven through the
# REAL Geoclient connector over RECORDED OFFICIAL data when a caller opts in.
#
# For the ONE documented-example address the G01 fixture records (314 W 100 St,
# Manhattan -> BBL 1018887502 - the Geoclient User Guide example, NOT the
# 215-16 Northern benchmark lot) it runs the production ``resolve_address`` over
# the recorded response body through a url-keyed fake transport + a dummy
# offline key, so route/connector/parse/provenance are the real code paths and
# no response byte is hand-written. EVERY other address falls through to the
# synthetic ``harness_address_resolver`` unchanged.
#
# HARD LIMIT (Tier D): recording the real Geoclient response for 215-16 Northern
# Boulevard needs the subscription key, which only the owner holds, so until
# then the real path is proven on the documented example above and the benchmark
# journey still enters by BBL.
# ---------------------------------------------------------------------------

GEOCLIENT_FIXTURE_DIR = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "geoclient"
)
GEOCLIENT_G01_FIXTURE = "G01_address_documented_example.json"
# Clearly-fake offline key; the real GEOCLIENT_SUBSCRIPTION_KEY is owner-only
# (Tier D) and is never read, required, or printed here.
RECORDED_GEOCLIENT_DUMMY_KEY = "DUMMY-GEOCLIENT-KEY-HARNESS-OFFLINE-ONLY"


def _g01_recorded_capture() -> dict:
    """The G01 documented-example capture: the exact house/street/borough it was
    recorded with (parsed from its own ``request_url``, never restated here),
    its recorded ``request_url`` and its verbatim response body."""
    fixture = json.loads(
        (GEOCLIENT_FIXTURE_DIR / GEOCLIENT_G01_FIXTURE).read_text(encoding="utf-8")
    )
    query = parse_qs(urlparse(fixture["request_url"]).query)
    return {
        "house_number": query["houseNumber"][0],
        "street": query["street"][0],
        "borough": query["borough"][0],
        "request_url": fixture["request_url"],
        "body": fixture["response_body_raw"],
    }


def harness_recorded_geoclient_resolver(
    house_number: str,
    street: str,
    *,
    borough: str | None = None,
    zip_code: str | None = None,
) -> AddressResolution:
    """OPT-IN resolver (never the harness default). For the recorded G01
    documented-example address it resolves through the REAL Geoclient connector
    over the recorded official body + a dummy offline key; any other address
    keeps the synthetic ``harness_address_resolver`` behaviour byte-for-byte.
    See the block comment above for the Tier-D hard limit on the benchmark lot."""
    capture = _g01_recorded_capture()
    asked = (house_number, street, borough or "")
    recorded = (capture["house_number"], capture["street"], capture["borough"])
    if asked != recorded:
        return harness_address_resolver(
            house_number, street, borough=borough, zip_code=zip_code
        )

    def _recorded_transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        if url != capture["request_url"]:
            raise AssertionError(
                f"unexpected Geoclient url {url!r}; only the recorded G01 "
                "documented-example capture is served offline"
            )
        return TransportResponse(200, capture["body"])

    return resolve_address(
        house_number,
        street,
        borough=borough,
        zip_code=zip_code,
        key=RECORDED_GEOCLIENT_DUMMY_KEY,
        transport=_recorded_transport,
        sleep=lambda _seconds: None,
    )


# ---------------------------------------------------------------------------
# D-1 slice 2 (lane C): the study-setup read behind the flag-on lot-&-site-setup
# journey. ONE seam is overridden — the study-inputs provider — and TWO flags are
# enabled FOR THIS HARNESS PROCESS ONLY: INTERNAL_STUDY_READ_ENABLED (so the route
# is reachable at all) and LANE_B_ENABLED (so the lot choice, Lane B behaviour, is
# produced rather than withheld). The provider replays the RECORDED 215-16
# Northern benchmark PLUTO body (services/api/tests/fixtures/benchmark_215_16_northern,
# queue item B-01) through the REAL connector and the REAL B-02/B-07 pipeline
# (app.api.v1.study_inputs.pluto_study_inputs_provider) — the SAME offline pattern
# the accepted slice-1 route tests use (tests/api/test_study_read_api.py). The
# PLUTO published-version probe (request B-4) is injected into that provider and
# served the recorded F09 observation through a routed fake transport
# (harness_version_probe) — never the network. NO study document byte is
# hand-written here; route, connector, builder, probe, contract guard and
# serialization are the production code paths. Served for the single Northern BBL
# only: any other requested BBL fails the connector's own result-match and becomes
# the route's fail-safe 503 (never a fabricated study). Production sets NEITHER
# flag, so the route stays a generic 404.
# ---------------------------------------------------------------------------

STUDY_FIXTURE_DIR = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "benchmark_215_16_northern"
)
NORTHERN_STUDY_BBL = "4073340070"


def harness_study_fetcher(bbl: str, correlation_id: str):
    """Replay the recorded 215-16 Northern PLUTO body through the real connector
    (the accepted slice-1 test's ``_northern_fetcher``). The requested ``bbl`` is
    validated by the connector's own result-match, so only the Northern BBL yields
    an ``ok`` record; any other BBL resolves to ``no_match`` -> the route's 503."""
    body = (STUDY_FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(
        encoding="utf-8"
    )
    return fetch_by_bbl(
        bbl,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,  # no real backoff delays in e2e
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def harness_version_probe(correlation_id: str):
    """Serve the recorded F09 PLUTO published-version probe (26v1) through a ROUTED
    fake transport (request B-4) - the same recorded-fixture discipline the parity
    DOF transport uses, never the network. The transport answers ONLY the exact
    VERSION_PROBE_URL the probe issues; any other url raises, so no live-shaped
    request is silently served. The REAL fetch_published_version (parse +
    VERSION_RE + provenance) runs over the recorded bytes, so no observation byte is
    hand-written here. For the Northern pin (26v2) this leaves the PLUTO facts
    ``current`` (26v2 is newer than the probe's 26v1), so the flag-on journey is
    unchanged; the probe wiring just makes an out-of-date lot observable."""
    f09 = fixture_response("F09_version_select.json")

    def transport(url, headers, timeout):
        if url != VERSION_PROBE_URL:
            raise AssertionError(f"unexpected version-probe url {url!r}")
        return f09

    return fetch_published_version(
        transport=transport,
        sleep=lambda seconds: None,  # no real backoff delays in e2e
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


# ---------------------------------------------------------------------------
# W5 (lane C): the three W2/W3/W4 internal reads mounted in app.main, served
# offline for the harness process from recorded official packs — mirroring the
# study-read seam above. hidden-issue-flags (W2) and transit-parking (W3) replay
# the SAME recorded 215-16 Northern PLUTO body through ``harness_study_fetcher``
# (a plain PLUTO fetcher); parity (W4) replays the recorded Bayside DOF pack.
# ---------------------------------------------------------------------------

PARITY_DOF_PACK = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "dof_sales_bayside"
)
PARITY_NEIGHBORHOOD = "BAYSIDE"
PARITY_BUILDING_CLASS = "22 STORE BUILDINGS"


def harness_parity_dof_transport():
    """A routed DOF transport serving the recorded Bayside pack for the exact two
    request urls the parity route builds for the Northern subject; any other url
    raises, so no live-shaped request is ever silently served."""
    by_bbl_url = build_by_bbl_url(NORTHERN_STUDY_BBL, row_limit=SUBJECT_SALES_ROW_LIMIT)
    candidates_url = build_candidates_url(
        PARITY_NEIGHBORHOOD, PARITY_BUILDING_CLASS, row_limit=CANDIDATE_ROW_LIMIT
    )
    routes = {
        by_bbl_url: (PARITY_DOF_PACK / "dof_sales_w2pb-icbu_bbl_4073340070.json").read_text(
            encoding="utf-8"
        ),
        candidates_url: (
            PARITY_DOF_PACK / "dof_sales_w2pb-icbu_bayside_22_store_buildings.json"
        ).read_text(encoding="utf-8"),
    }
    vintage = {"x-soda2-truth-last-modified": "2026-09-01"}

    def transport(url, headers, timeout):
        if url not in routes:
            raise AssertionError(f"unexpected url {url!r}")
        return DofTransportResponse(200, routes[url], dict(vintage))

    return transport


# M5-T141: the results route's study-inputs provider replays the recorded 215-16 Northern
# benchmark pack through the REAL connectors, reading the pack files BY PATH and importing
# nothing from the server's test tree, so the harness starts where only the installed ``app``
# package is on the Python path (GitHub's web-e2e job installs the server with
# ``pip install --no-deps .``, which packages ``app`` only). It reproduces the canonical
# recorded-Northern replay the server's own tests use (tests/spatial/_northern_replay.py
# and the results-route test's ``benchmark_provider``) with the SAME fixed clock, seed and
# correlation arguments, so the built inputs are equal (proven by the server test
# services/api/tests/api/test_e2e_harness_results_inputs.py). No response byte is hand-written and
# no recorded value is retyped: every byte is served from the pack files, the confirmed address is
# read from the benchmark-lot fixture, and the DCM query envelope is DERIVED from the lot geometry
# by the production helper ``street_envelope_for_lot`` (never restated).

RESULTS_DCM_FILE = "dcm_street_centerline_lot_envelope_4073340070.json"
RESULTS_BENCHMARK_LOT_FIXTURE = (
    REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
# The fixed replay clock _northern_replay uses (distinct from the harness FIXED_CLOCK above), so
# the connectors' retrieved_at / provenance stamps match the test tree's replay byte-for-byte.
RESULTS_REPLAY_CLOCK = lambda: datetime(2026, 9, 30, 6, 20, tzinfo=UTC)  # noqa: E731


def _results_pack_manifest() -> dict:
    """The recorded Northern pack's MANIFEST entries keyed by file name (read by path)."""
    raw = json.loads((STUDY_FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    return {entry["file"]: entry for entry in raw["files"]}


def _results_pack_transport(url: str, headers: dict, timeout: float) -> TransportResponse:
    """Serve one recorded pack file to a connector's own fetch code, matched by URL (no network) -
    the same recorded-bytes-by-URL replay ``_northern_replay._transport`` performs."""
    by_url = {entry["url"]: name for name, entry in _results_pack_manifest().items()}
    body = (STUDY_FIXTURE_DIR / by_url[url]).read_bytes().decode("utf-8")
    return TransportResponse(200, body)


def _results_replay_lot_geometry():
    """The recorded MapPLUTO lot geometry through the real connector (replay_lot_geometry)."""
    return fetch_lot_geometry(
        NORTHERN_STUDY_BBL, transport=_results_pack_transport, sleep=lambda _s: None,
        clock=RESULTS_REPLAY_CLOCK, rng=Random(0), correlation_id="b03-benchmark",
    )


def _results_replay_pluto():
    """The recorded PLUTO body through the real connector (replay_pluto)."""
    return fetch_by_bbl(
        NORTHERN_STUDY_BBL, transport=_results_pack_transport, sleep=lambda _s: None,
        clock=RESULTS_REPLAY_CLOCK, correlation_id="b03-benchmark",
        observation_event_id="b03-benchmark",
    )


def _results_replay_dcm_page():
    """The recorded DCM street page parsed by the real connector (replay_dcm_page)."""
    entry = _results_pack_manifest()[RESULTS_DCM_FILE]
    body = (STUDY_FIXTURE_DIR / RESULTS_DCM_FILE).read_bytes().decode("utf-8")
    transport = DcmTransport(
        url=entry["url"], status=200, body=body, retrieved_at=entry["retrieved_at"]
    )
    return parse_segment_geometry_page(transport, correlation_id="b03-benchmark")


def _results_confirmed_address() -> str:
    """The lot's confirmed address, read from the benchmark-lot fixture's ``identity.address`` (the
    same file and field the test tree's ``_benchmark_identity_address`` reads; never retyped)."""
    doc = json.loads(RESULTS_BENCHMARK_LOT_FIXTURE.read_text(encoding="utf-8"))
    return doc["identity"]["address"]


def harness_results_inputs_provider():
    """The results route's study-inputs provider over the recorded 215-16 Northern benchmark pack
    (M5-T140 Part B). It mirrors the accepted results-route test's ``benchmark_provider``:
    ``assemble_study_inputs`` builds the property profile from the recorded PLUTO body and threads
    the recorded B-03 site geometry, the prepared tax-map outline and the benchmark lot's confirmed
    identity address (a corner lot needs it to pick the front lot line). Built offline through the
    REAL connectors from the recorded pack read BY PATH - no response byte is hand-written and the
    module imports nothing from the server's test tree, so the harness starts in CI (M5-T141).
    Served for the Northern subject only; any other BBL is the route's fail-safe 503."""
    lot, _unused = lot_outline_from_mappluto(_results_replay_lot_geometry())
    envelope = street_envelope_for_lot(lot)
    streets = street_data_from_pages([_results_replay_dcm_page()], envelope=envelope)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    address = _results_confirmed_address()

    def provide(bbl: str, correlation_id: str, *, selected=None):
        if bbl != NORTHERN_STUDY_BBL:
            raise StudyInputsUnavailableError(
                "the recorded harness serves the Northern benchmark lot only",
                reason="not_served",
            )
        return assemble_study_inputs(
            _results_replay_pluto(),
            env={"LANE_B_ENABLED": "1"},
            address=address,
            site_geometry=geometry,
            prepared_outline=prepared,
        )

    return provide


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
    app.dependency_overrides[get_tax_map_outline_fetcher] = (
        lambda: harness_tax_map_outline_fetcher
    )
    app.dependency_overrides[get_address_resolver] = (
        lambda: harness_address_resolver
    )
    # D-1 slice 2: enable the study-read route and the Lane B lot-choice gate for
    # THIS harness process only, and serve the study inputs from the recorded
    # 215-16 Northern pack through the real B-02/B-07 pipeline. The flags gate only
    # this process (production sets neither, so the route 404s); the override is the
    # single seam, so route/connector/builder/contract are the production paths.
    os.environ[INTERNAL_STUDY_READ_ENABLED_ENV_VAR] = "1"
    os.environ[LANE_FLAG_ENV_VARS["B"]] = "1"
    study_inputs_provider = pluto_study_inputs_provider(
        harness_study_fetcher, clock=FIXED_CLOCK, version_probe=harness_version_probe
    )
    app.dependency_overrides[get_study_inputs_provider] = lambda: study_inputs_provider
    # M5-T140 Part B: the results route (POST /api/v1/properties/{bbl}/results), mounted in
    # app.main (self-gated, default off). Enable its reachability flag INTERNAL_RESULTS_ENABLED
    # and the engine's Lane A gate LANE_A_ENABLED FOR THIS HARNESS PROCESS ONLY, and inject a
    # recorded-Northern study-inputs provider that threads the B-03 site geometry, the prepared
    # tax-map outline and the confirmed identity address the engine chain needs (the results route
    # derives the lot's five conditions from that evidence). Route / engine chain / contract guard
    # are the production code paths and no response byte is hand-written. Production sets neither
    # flag, so the route stays a generic 404. Served for the Northern subject only; any other BBL
    # is the route's fail-safe 503. The website switch INTERNAL_RESULTS_UI_ENABLED is set on the
    # :3001 Next server only (playwright.config.ts), never here.
    os.environ[INTERNAL_RESULTS_ENABLED_ENV_VAR] = "1"
    os.environ[LANE_FLAG_ENV_VARS["A"]] = "1"
    results_inputs_provider = harness_results_inputs_provider()
    app.dependency_overrides[get_results_study_inputs_provider] = lambda: results_inputs_provider
    # W5: the three W2/W3/W4 internal reads, mounted in app.main (self-gated and
    # default off). Enable each flag FOR THIS PROCESS ONLY and inject the one
    # provider per route from a recorded official pack, so route/connector/builder/
    # contract guard are the production paths and no response byte is hand-written.
    # LANE_B_ENABLED is already on (study block above), so the Lane-B-behaviour data
    # is produced rather than withheld. Production sets none of these flags, so each
    # route stays a generic 404. Served for the Northern subject only (the shared
    # fetcher/pack match that BBL); any other BBL is the route's fail-safe 503.
    os.environ[INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR] = "1"
    hidden_provider = pluto_hidden_issue_flag_inputs_provider(
        harness_study_fetcher, clock=FIXED_CLOCK
    )
    app.dependency_overrides[get_hidden_issue_flag_inputs_provider] = lambda: hidden_provider
    os.environ[INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR] = "1"
    transit_provider = pluto_transit_parking_provider(harness_study_fetcher, clock=FIXED_CLOCK)
    app.dependency_overrides[get_transit_parking_provider] = lambda: transit_provider
    os.environ[INTERNAL_PARITY_READ_ENABLED_ENV_VAR] = "1"
    parity_transport = harness_parity_dof_transport()
    app.dependency_overrides[get_dof_transport] = lambda: parity_transport
    # Test-origin CORS only (see module docstring CORS NOTE). Both e2e web servers
    # are allowed: :3000 (flag-off) and :3001 (D-1 slice 2 flag-on). The browser
    # fetches the API cross-origin (NEXT_PUBLIC_API_BASE_URL -> :8000), so the
    # flag-on page on :3001 needs its origin here to reach the study endpoint.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:3000", "http://localhost:3000",
            "http://127.0.0.1:3001", "http://localhost:3001",
        ],
        # GET for the read routes; POST for the M5-T140 results route, whose JSON body makes the
        # browser send a Content-Type the preflight must allow.
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type"],
        expose_headers=["X-Correlation-ID"],
    )
    return app


if __name__ == "__main__":
    port = int(os.environ.get("HARNESS_PORT", "8000"))
    uvicorn.run(build_app(), host="127.0.0.1", port=port, log_level="warning")
