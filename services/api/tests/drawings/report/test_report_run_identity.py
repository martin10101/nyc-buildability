"""M5-T169 S7: the report's run identity (D-094 R028/R038/R058).

The appendix carries a document FINGERPRINT (stable for the same document, changing
when any value changes, and excluding the run id and timestamp), the deployed CODE
COMMIT (read from the environment, "unknown" when unset, or carried by the route) and
the result revision. One test per input state; every expected value is read from the
document or the module, never retyped from a program run.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, run_identity

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
