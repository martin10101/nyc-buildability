"""Attach source.version_check to assessed site facts (queue item B-06 follow-up).

The bridge ``app.profile.fact_version_check.attach_version_check`` carries the B-06
version status (``app.profile.data_versions``) into the B-02 site facts through the
site_fact 1.1.0 ``source.version_check`` slot that Lane C added for request
``docs/lanes/requests/B-1.md``.

Offline and deterministic. Recorded official data only:

- the M1-T002 PLUTO fixtures (``tests/fixtures/pluto``): F01 (a lot record, 26v1) and
  F09 (the ``$select=version`` probe, 26v1), captured 2026-07-16;
- the B-01 215-16 Northern Blvd pack (``tests/fixtures/benchmark_215_16_northern``):
  PLUTO 26v2, captured 2026-09-30.

Inputs marked SYNTHETIC are hand-made to exercise the fail-closed edge.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path

import pytest

from app.connectors import pluto_soda
from app.profile.builder import build_property_profile
from app.profile.data_versions import (
    STATUS_CURRENT,
    STATUS_OUT_OF_DATE,
    STATUS_VERSION_UNKNOWN,
    DataVersionReport,
    PublishedVersion,
    SourceVersionStatus,
    assess_data_versions,
    pins_from_site_facts,
    published_from_pins,
)
from app.profile.fact_version_check import (
    SITE_FACT_CONTRACT_VERSION_WITH_VERSION_CHECK,
    VERSION_CHECK_KEYS,
    attach_version_check,
    version_check_projection,
)
from app.profile.site_facts import PLUTO_DATASET_NAME, build_site_facts
from app.resilience.transport import TransportResponse
from tests.profile.site_fact_contract import assert_valid_site_fact, schema_errors
from tests.spatial._northern_replay import BBL, MANIFEST, PACK

PLUTO_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"


def _pluto_site_facts(body: str, bbl: str, retrieved_at: str):
    moment = datetime.fromisoformat(retrieved_at)
    result = pluto_soda.fetch_by_bbl(
        bbl, transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda _s: None, clock=lambda: moment,
        correlation_id="b06fv", observation_event_id="b06fv")
    return build_site_facts(build_property_profile(result, clock=lambda: moment))


def _pluto_fixture(name: str) -> dict:
    return json.loads((PLUTO_FIXTURES / name).read_text("utf-8"))


@pytest.fixture(scope="module")
def f01_facts():
    fixture = _pluto_fixture("F01_single_lot_normal.json")
    return _pluto_site_facts(fixture["response_body_raw"], "1000010100",
                             fixture["retrieval_timestamp_utc"])


@pytest.fixture(scope="module")
def f09_probe() -> PublishedVersion:
    fixture = _pluto_fixture("F09_version_select.json")
    (row,) = json.loads(fixture["response_body_raw"])
    return PublishedVersion(PLUTO_DATASET_NAME, row["version"],
                            fixture["retrieval_timestamp_utc"], fixture["request_url"])


@pytest.fixture(scope="module")
def benchmark_pluto_facts():
    entry = MANIFEST[PLUTO_FILE]
    body = (PACK / PLUTO_FILE).read_bytes().decode("utf-8")
    return _pluto_site_facts(body, BBL, entry["retrieved_at"])


def _sourced_ids(facts) -> list[str]:
    return [fact["fact_id"] for fact in facts if fact["source"]]


def _unsourced_ids(facts) -> list[str]:
    return [fact["fact_id"] for fact in facts if not fact["source"]]


def _by_id(facts) -> dict:
    return {fact["fact_id"]: fact for fact in facts}


# --- each status attaches correctly -----------------------------------------------------


def test_out_of_date_attaches_version_check_and_stamps_1_1_0(
        f01_facts, benchmark_pluto_facts, f09_probe) -> None:
    published = published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts))
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), (*published, f09_probe))
    (source,) = report.sources
    assert source.status == STATUS_OUT_OF_DATE  # guard: the scenario is an out-of-date one

    out = attach_version_check(f01_facts.facts, report)
    assert len(out) == len(f01_facts.facts)
    by_id = _by_id(out)
    for fact_id in _sourced_ids(f01_facts.facts):
        fact = by_id[fact_id]
        assert fact["contract_version"] == SITE_FACT_CONTRACT_VERSION_WITH_VERSION_CHECK
        check = fact["source"]["version_check"]
        assert tuple(check) == VERSION_CHECK_KEYS  # exactly the six keys, in order
        assert check == {
            "status": STATUS_OUT_OF_DATE, "label": "Out of date",
            "latest_known_version": "26v2",
            "latest_known_seen_at": source.latest_known_seen_at,
            "latest_known_query_ref": source.latest_known_query_ref,
            "reason": source.reason}
        assert_valid_site_fact(fact)


def test_current_attaches_version_check(f01_facts, f09_probe) -> None:
    # 26v1 pinned, 26v1 the newest on record -> current (the plan gives no age threshold).
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [f09_probe])
    (source,) = report.sources
    assert source.status == STATUS_CURRENT

    out = attach_version_check(f01_facts.facts, report)
    for fact_id in _sourced_ids(f01_facts.facts):
        check = _by_id(out)[fact_id]["source"]["version_check"]
        assert (check["status"], check["label"]) == (STATUS_CURRENT, "Current")
        assert check["latest_known_version"] == "26v1"
    for fact in out:
        assert_valid_site_fact(fact)


def test_version_unknown_attaches_and_stays_valid(f01_facts) -> None:
    # Nothing on record to compare the 26v1 pin with -> version_unknown. The fact's source
    # still has dataset_version "26v1", and version_unknown needs no latest_known_version.
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [])
    (source,) = report.sources
    assert source.status == STATUS_VERSION_UNKNOWN

    out = attach_version_check(f01_facts.facts, report)
    for fact_id in _sourced_ids(f01_facts.facts):
        fact = _by_id(out)[fact_id]
        assert fact["contract_version"] == "1.1.0"
        check = fact["source"]["version_check"]
        assert (check["status"], check["label"]) == (STATUS_VERSION_UNKNOWN, "Version unknown")
        assert check["latest_known_version"] is None
        assert fact["source"]["dataset_version"] == "26v1"
        assert_valid_site_fact(fact)


# --- untouched facts stay byte-identical ------------------------------------------------


def test_facts_with_no_assessed_source_stay_byte_identical(f01_facts, f09_probe) -> None:
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [f09_probe])
    out = attach_version_check(f01_facts.facts, report)
    by_id_in = _by_id(f01_facts.facts)
    by_id_out = _by_id(out)
    unsourced = _unsourced_ids(f01_facts.facts)
    assert unsourced, "the existing-zoning-floor-area fact has no source to assess"
    for fact_id in unsourced:
        assert json.dumps(by_id_out[fact_id]) == json.dumps(by_id_in[fact_id])
        assert by_id_out[fact_id]["contract_version"] == "1.0.0"
        assert "version_check" not in (by_id_out[fact_id]["source"] or {})


def test_order_and_count_are_preserved(f01_facts, f09_probe) -> None:
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [f09_probe])
    out = attach_version_check(f01_facts.facts, report)
    assert [f["fact_id"] for f in out] == [f["fact_id"] for f in f01_facts.facts]


# --- inputs are never mutated -----------------------------------------------------------


def test_inputs_are_not_mutated(f01_facts, benchmark_pluto_facts, f09_probe) -> None:
    published = published_from_pins(pins_from_site_facts(benchmark_pluto_facts.facts))
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), (*published, f09_probe))
    before = copy.deepcopy(list(f01_facts.facts))
    out = attach_version_check(f01_facts.facts, report)
    assert list(f01_facts.facts) == before  # nothing in the input changed
    # and the returned dicts are independent of the inputs
    out[0]["source"]["version_check"]["reason"] = "mutated"
    assert list(f01_facts.facts) == before


# --- the 215-16 Northern recorded pack, end to end --------------------------------------


def test_benchmark_215_16_northern_pack_produces_valid_facts_end_to_end(
        benchmark_pluto_facts, f09_probe) -> None:
    facts = benchmark_pluto_facts.facts
    pins = pins_from_site_facts(facts)
    # The capture (26v2) is the newest on record; F09's older 26v1 changes nothing.
    report = assess_data_versions(pins, (*published_from_pins(pins), f09_probe))
    (source,) = report.sources
    assert (source.pinned_version, source.status) == ("26v2", STATUS_CURRENT)

    out = attach_version_check(facts, report)
    assert len(out) == len(facts)
    for fact in out:
        assert_valid_site_fact(fact)
    by_id = _by_id(out)
    for fact_id in _sourced_ids(facts):
        check = by_id[fact_id]["source"]["version_check"]
        assert (check["status"], check["latest_known_version"]) == (STATUS_CURRENT, "26v2")
        assert by_id[fact_id]["contract_version"] == "1.1.0"
    for fact_id in _unsourced_ids(facts):
        assert by_id[fact_id]["contract_version"] == "1.0.0"


# --- fail closed: never emit an invalid fact, never invent a status ---------------------


def _one_sourced_fact(facts) -> dict:
    return copy.deepcopy(next(fact for fact in facts if fact["source"]))


def test_fail_closed_when_out_of_date_but_fact_has_no_dataset_version(f01_facts) -> None:
    # SYNTHETIC inconsistency: the assessor says out_of_date (latest_known_version set), but
    # the fact's source records no dataset_version. The contract co-requires a non-null
    # dataset_version for that status, so attaching would be invalid -> leave byte-identical.
    fact = _one_sourced_fact(f01_facts.facts)
    fact["source"]["dataset_version"] = None
    assert not schema_errors(fact)  # a null-version 1.0.0 fact is valid on its own
    status = SourceVersionStatus(
        dataset=PLUTO_DATASET_NAME, pinned_version=None, version_basis=None,
        retrieved_at="2026-01-01T00:00:00Z", query_ref="synthetic://pin",
        fact_ids=(fact["fact_id"],), status=STATUS_OUT_OF_DATE,
        latest_known_version="26v2", latest_known_seen_at="2026-09-30T00:00:00Z",
        latest_known_query_ref="synthetic://published", reason="SYNTHETIC out of date")

    (out,) = attach_version_check([fact], DataVersionReport((status,)))
    assert json.dumps(out) == json.dumps(fact)  # byte-identical: not emitted invalid
    assert out["contract_version"] == "1.0.0"
    assert "version_check" not in out["source"]


def test_fail_closed_when_status_has_no_latest_known_version(f01_facts) -> None:
    # SYNTHETIC inconsistency: out_of_date but latest_known_version null. version_check's
    # own co-requirement forbids that, so attaching would be invalid -> leave byte-identical.
    fact = _one_sourced_fact(f01_facts.facts)
    assert fact["source"]["dataset_version"] == "26v1"
    status = SourceVersionStatus(
        dataset=PLUTO_DATASET_NAME, pinned_version="26v1", version_basis="release",
        retrieved_at="2026-01-01T00:00:00Z", query_ref="synthetic://pin",
        fact_ids=(fact["fact_id"],), status=STATUS_OUT_OF_DATE,
        latest_known_version=None, latest_known_seen_at=None,
        latest_known_query_ref=None, reason="SYNTHETIC missing latest")

    (out,) = attach_version_check([fact], DataVersionReport((status,)))
    assert json.dumps(out) == json.dumps(fact)
    assert out["contract_version"] == "1.0.0"
    assert "version_check" not in out["source"]


def test_version_check_projection_drops_the_non_contract_keys(f01_facts) -> None:
    report = assess_data_versions(pins_from_site_facts(f01_facts.facts), [])
    (source,) = report.sources
    projection = version_check_projection(source)
    assert tuple(projection) == VERSION_CHECK_KEYS
    # the wider to_dict() keys never leak into the contract slot
    assert set(source.to_dict()) - set(projection) == {
        "dataset", "pinned_version", "version_basis", "retrieved_at", "query_ref",
        "fact_ids", "exception_label"}
