"""M5-T169 S7 / M5-T190: the report's run identity (D-094 R028/R038/R058).

The appendix carries a document FINGERPRINT (stable for the same document, changing
when any value changes, and excluding the four per-run metadata fields the live route
mints fresh each run -- the run id, the run timestamp, the option id and the study id),
the deployed CODE COMMIT (read from the environment, "unknown" when unset, or carried
by the route) and the result revision. One test per input state; every expected value
is read from the document or the module, never retyped from a program run.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import INTERNAL_RESULTS_ENABLED_ENV_VAR
from app.drawings.report import build_report_html, run_identity
from tests.api.test_results_read_api import (
    NORTHERN_BBL,
    _no_network,
    app_with,
    benchmark_provider,
)

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _appendix(html: str) -> str:
    return html[html.index('id="appendix"'):]


# ---------------------------------------------------------------- fingerprint stability
def test_s7_fingerprint_stable_excluding_run_id_and_timestamp() -> None:
    doc = benchmark()
    other = {**doc, "results_id": "a-different-run-id", "computed_at": "2027-01-01T00:00:00Z"}
    assert run_identity.document_fingerprint(doc) == run_identity.document_fingerprint(other)


def test_s7_fingerprint_changes_when_any_value_changes() -> None:
    doc = benchmark()
    changed = json.loads(json.dumps(doc))
    changed["answers"]["floor_area_allowance"]["values"][1]["value"] = 20151.0  # was 20,150
    assert run_identity.document_fingerprint(doc) != run_identity.document_fingerprint(changed)


def test_s7_fingerprint_is_hex_and_short() -> None:
    fp = run_identity.document_fingerprint(benchmark())
    assert re.fullmatch(r"[0-9a-f]{12}", fp)


# ------------------------------------- M5-T190 (DB-282): the two per-run ids are excluded too
def test_t190_s1_fingerprint_stable_across_all_four_run_fields() -> None:
    """S1: two documents that differ only in the four per-run metadata fields
    (results_id, computed_at, option_id, study_id) share a fingerprint. The live route
    mints option_id and study_id as fresh uuids each run (results_read.py), so this is
    the drift the module must exclude; the older test only tweaked results_id/computed_at
    and did not catch it."""
    doc = benchmark()
    other = {
        **doc,
        "results_id": "a-different-run-id",
        "computed_at": "2027-01-01T00:00:00Z",
        "option_id": "a-different-option-id",
        "study_id": "a-different-study-id",
    }
    assert run_identity.document_fingerprint(doc) == run_identity.document_fingerprint(other)


def test_t190_s3_document_without_option_or_study_id_behaves_as_before() -> None:
    """S3: an older document or synthetic fixture that never carried option_id or
    study_id fingerprints exactly as the full document. The two ids are excluded run
    metadata, so their absence changes nothing: dropping them leaves the fingerprint
    unmoved."""
    doc = benchmark()
    assert "option_id" in doc and "study_id" in doc  # the benchmark carries both
    older = {k: v for k, v in doc.items() if k not in ("option_id", "study_id")}
    assert run_identity.document_fingerprint(older) == run_identity.document_fingerprint(doc)


def test_t190_s4_live_route_two_runs_share_a_fingerprint(monkeypatch) -> None:
    """S4: the live results route, run twice through the TestClient with the benchmark
    providers, mints fresh per-run ids each run yet produces the SAME fingerprint. This
    catches the real drift the recorded fixture (with fixed placeholder ids) never saw.
    Mutation: with the old two-field exclude tuple the two fingerprints differ and this
    test (and S1) go red."""
    _no_network(monkeypatch)
    monkeypatch.setenv(INTERNAL_RESULTS_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv("LANE_A_ENABLED", "1")
    provider = benchmark_provider(with_zoning_lot=True, street_on=True)
    body = {"housing_program": "standard_residence"}

    def one() -> dict:
        resp = TestClient(app_with(provider)).post(
            f"/api/v1/properties/{NORTHERN_BBL}/results", json=body)
        assert resp.status_code == 200
        return resp.json()

    d1, d2 = one(), one()
    # the route really mints fresh per-run ids each run, so the test is not vacuous.
    assert d1["option_id"] != d2["option_id"]
    assert d1["study_id"] != d2["study_id"]
    assert d1["results_id"] != d2["results_id"]
    # yet no real value differs, so the fingerprint is reproducible across the two runs.
    assert run_identity.document_fingerprint(d1) == run_identity.document_fingerprint(d2)


# ---------------------------------------------------------------- deployed commit states
def test_s7_commit_unknown_when_env_unset() -> None:
    assert run_identity.deployed_commit({}) == run_identity.UNKNOWN_COMMIT


def test_s7_commit_read_from_render_then_generic_env() -> None:
    sha = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
    assert run_identity.deployed_commit({"RENDER_GIT_COMMIT": sha}) == sha
    assert run_identity.deployed_commit({"GIT_COMMIT_SHA": sha}) == sha
    # a non-hex value is ignored (fail-safe to "unknown").
    assert run_identity.deployed_commit({"RENDER_GIT_COMMIT": "not-a-sha"}) \
        == run_identity.UNKNOWN_COMMIT


# ---------------------------------------------------------------- rendered in the appendix
def test_s7_run_identity_renders_in_the_appendix() -> None:
    doc = benchmark()
    appendix = visible_text(_appendix(build_report_html(doc)))
    assert "Run identity" in appendix
    assert f"Document fingerprint: {run_identity.document_fingerprint(doc)}" in appendix
    # the env is unset in the test, so the commit tolerates "unknown".
    assert "Code commit: unknown" in appendix
    assert f"Results revision: {doc['revision']}" in appendix
    assert "Computed: 2026-10-03" in appendix


def test_s7_route_carries_the_commit_into_the_run_identity() -> None:
    sha = "0123456789abcdef0123456789abcdef01234567"
    html = build_report_html(benchmark(), identity={"commit": sha})
    assert f"Code commit: {sha}" in visible_text(_appendix(html))


def test_s7_status_label_key_is_the_only_verified() -> None:
    # the status-label key is the only place "Verified" appears (R028).
    assert visible_text(build_report_html(benchmark())).count("Verified") == 1
