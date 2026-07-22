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
from datetime import UTC, datetime
from pathlib import Path

import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.properties import get_pluto_fetcher
from app.api.v1.rule_evaluation import get_spatial_substrate_provider
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
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


def build_app():
    # M4-T005: enable the internal rule-evaluation endpoint's SERVER flag for
    # this test process only (independent of the frontend flag). The no-call
    # frontend spec still proves the browser issues no request when the surface
    # is not opted in, regardless of this server-side flag.
    os.environ[INTERNAL_RULE_EVAL_ENABLED_ENV_VAR] = "1"
    app.dependency_overrides[get_pluto_fetcher] = lambda: harness_fetcher
    app.dependency_overrides[get_spatial_substrate_provider] = (
        lambda: harness_substrate_provider
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
