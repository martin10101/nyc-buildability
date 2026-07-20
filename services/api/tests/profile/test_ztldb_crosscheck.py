"""Acceptance scenarios ZT-S13 / ZT-S14 (task M2-T008): cross-source
lot-level zoning reconciliation through the EXISTING contract-1.3.0
conflict / analysis-readiness machinery.

- ZT-S13: ZTLDB vs PLUTO disagreements become typed conflicts with BOTH
  observations and their provenance preserved; neither value wins; no
  legal adjudication.
- ZT-S14: an externally supplied observation derived from the accepted
  M2-T007 zoning-features FIXTURES (fixture values only - no spatial
  intersection) flows through the same typed path.
- Profile integration: the additive builder parameters append ZTLDB facts
  to ``provenance`` and cross-check conflicts to ``conflicts`` WITHIN
  contract 1.3.0; an unresolved conflict on the critical ``zonedist1``
  gates ``analysis_readiness`` through the existing M2-T004 policy.

Offline and deterministic: fixture transports replay the accepted M1-T002
PLUTO captures and the M2-T008 ZTLDB captures; synthetic variants are
clearly labeled and derived in-test.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.pluto_soda import (
    TransportResponse,
)
from app.connectors.pluto_soda import (
    fetch_by_bbl as pluto_fetch_by_bbl,
)
from app.connectors.ztldb_soda import (
    fetch_by_bbl as ztldb_fetch_by_bbl,
)
from app.connectors.ztldb_soda import (
    fetch_source_freshness,
)
from app.profile.builder import build_property_profile
from app.profile.zoning_crosscheck import (
    ZONING_CROSSCHECK_FIELD_MAP,
    crosscheck_lot_zoning,
    external_observation,
)

TESTS_DIR = Path(__file__).resolve().parents[1]
PLUTO_FIXTURES = TESTS_DIR / "fixtures" / "pluto"
ZTLDB_FIXTURES = TESTS_DIR / "fixtures" / "ztldb"
ZF_FIXTURES = TESTS_DIR / "fixtures" / "zoning_features"
SCHEMA_DIR = (
    TESTS_DIR.parents[2] / "packages" / "contracts" / "schemas" / "v1"
)

FIXED_CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731

ZONING_FEATURES_SOURCE_ID = "nyc-dcp-zoning-features-arcgis"


def _body(directory: Path, name: str) -> str:
    fixture = json.loads((directory / name).read_text(encoding="utf-8"))
    return fixture["response_body_raw"]


def _transport(*bodies_or_responses):
    items = [
        item if isinstance(item, TransportResponse) else TransportResponse(200, item)
        for item in bodies_or_responses
    ]

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return items.pop(0)

    return transport


def pluto_result(fixture: str, bbl: str, mutate=None):
    records = json.loads(_body(PLUTO_FIXTURES, fixture))
    if mutate is not None:
        mutate(records[0])  # SYNTHETIC in-test variant, clearly labeled
    return pluto_fetch_by_bbl(
        bbl,
        transport=_transport(json.dumps(records)),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id="crosscheck-pluto",
    )


def _freshness():
    return fetch_source_freshness(
        transport=_transport(_body(ZTLDB_FIXTURES, "ZT08_api_views_metadata.json")),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )


def ztldb_result(fixture: str, bbl: str, mutate=None):
    records = json.loads(_body(ZTLDB_FIXTURES, fixture))
    if mutate is not None:
        mutate(records[0])  # SYNTHETIC in-test variant, clearly labeled
    return ztldb_fetch_by_bbl(
        bbl,
        freshness=_freshness(),
        transport=_transport(json.dumps(records)),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        correlation_id="crosscheck-ztldb",
        app_token=None,
    )


def zoning_features_fixture_district() -> str:
    """District value read from the accepted M2-T007 fixture ZF03 (a real
    nyzd feature with ZONEDIST 'R3-2'). FIXTURE VALUE ONLY - no spatial
    intersection is computed (owner scope exclusion)."""
    doc = json.loads(_body(ZF_FIXTURES, "ZF03_query_nyzd_single_R3-2.json"))
    return doc["features"][0]["attributes"]["ZONEDIST"]


@pytest.fixture(scope="module")
def profile_validator():
    """jsonschema validator for property_profile.schema.json v1 (same
    resolution pattern as tests/profile/test_data_semantics.py)."""
    jsonschema = pytest.importorskip("jsonschema")
    docs = [
        json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in (
            "property_profile.schema.json",
            "source_fact.schema.json",
            "common.schema.json",
            "coverage_status.schema.json",
        )
    ]
    schema = docs[0]
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in docs},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


# --------------------------------------------------------------------------
# ZT-S13 - ZTLDB vs PLUTO
# --------------------------------------------------------------------------


def test_s13_official_captures_for_the_same_lot_reconcile_cleanly() -> None:
    # Real pair: PLUTO F01 and ZTLDB ZT01 both describe BBL 1000010100.
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result("ZT01_record_single_lot.json", "1000010100")
    report = crosscheck_lot_zoning(pluto, ztldb)
    assert report.conflicts == []
    consistent = {
        entry["field"]
        for entry in report.agreements
        if entry["status"] == "consistent"
    }
    assert {"zonedist1", "spdist1"} <= consistent
    assert len(report.compared_fields) == len(ZONING_CROSSCHECK_FIELD_MAP)


def test_s13_case_only_difference_is_uncertainty_not_conflict() -> None:
    # REAL formatting difference observed live: PLUTO zonemap '16a' vs
    # ZTLDB zoning_map_number '16A' for the same lot.
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result("ZT01_record_single_lot.json", "1000010100")
    report = crosscheck_lot_zoning(pluto, ztldb)
    assert [entry["field"] for entry in report.uncertainties] == ["zonemap"]
    uncertainty = report.uncertainties[0]
    assert uncertainty["kind"] == "case_only_difference"
    values = {entry["source_id"]: entry["value"] for entry in uncertainty["values"]}
    assert values["nyc-dcp-pluto-soda"] == "16a"
    assert values["nyc-dcp-ztldb-soda"] == "16A"
    # Uncertainties surface as contract-safe notes.
    assert any("zonemap" in note for note in report.notes)


def test_s13_split_lot_and_border_flag_mapping_reconcile() -> None:
    # Real pair: PLUTO F05 (zonedist2 C4-1, zmcode checkbox True) and ZTLDB
    # ZT02 (zoning_district_2 C4-1, zoning_map_code text 'Y').
    pluto = pluto_result("F05_split_zone_lot.json", "1000010010")
    ztldb = ztldb_result("ZT02_record_split_lot.json", "1000010010")
    report = crosscheck_lot_zoning(pluto, ztldb)
    consistent = {
        entry["field"]
        for entry in report.agreements
        if entry["status"] == "consistent"
    }
    assert {"zonedist1", "zonedist2", "spdist1", "zmcode"} <= consistent
    assert report.conflicts == []


def test_s13_value_disagreement_is_a_typed_conflict_with_both_sides() -> None:
    def ztldb_says_r4(record: dict) -> None:
        record["zoning_district_1"] = "R4"  # SYNTHETIC disagreement

    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result(
        "ZT01_record_single_lot.json", "1000010100", mutate=ztldb_says_r4
    )
    report = crosscheck_lot_zoning(pluto, ztldb)
    assert [conflict["field"] for conflict in report.conflicts] == ["zonedist1"]
    conflict = report.conflicts[0]
    assert conflict["resolution"] == "unresolved"  # never adjudicated
    values = {entry["source_id"]: entry for entry in conflict["values"]}
    # BOTH observations preserved with provenance in the derivation text.
    assert values["nyc-dcp-pluto-soda"]["value"] == "R3-2"
    assert "provenance" in values["nyc-dcp-pluto-soda"]["derivation"]
    assert values["nyc-dcp-ztldb-soda"]["value"] == "R4"
    assert "provenance" in values["nyc-dcp-ztldb-soda"]["derivation"]
    assert "not legal zoning adjudication" in conflict["reason"]


def test_s13_present_vs_documented_blank_is_a_conflict_with_absence_stated() -> None:
    def drop_zd2(record: dict) -> None:
        record.pop("zoning_district_2")  # SYNTHETIC vintage-skew shape

    pluto = pluto_result("F05_split_zone_lot.json", "1000010010")
    ztldb = ztldb_result(
        "ZT02_record_split_lot.json", "1000010010", mutate=drop_zd2
    )
    report = crosscheck_lot_zoning(pluto, ztldb)
    assert [conflict["field"] for conflict in report.conflicts] == ["zonedist2"]
    values = {
        entry["source_id"]: entry for entry in report.conflicts[0]["values"]
    }
    assert values["nyc-dcp-pluto-soda"]["value"] == "C4-1"
    assert values["nyc-dcp-ztldb-soda"]["value"] is None
    # The absence is STATED with its documented source semantics.
    assert "not divided by a zoning boundary line" in (
        values["nyc-dcp-ztldb-soda"]["derivation"]
    )


def test_s13_cross_property_comparison_is_refused() -> None:
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result("ZT02_record_split_lot.json", "1000010010")
    with pytest.raises(ValueError, match="same property"):
        crosscheck_lot_zoning(pluto, ztldb)


def test_s13_no_record_ztldb_result_is_refused() -> None:
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    no_record = ztldb_fetch_by_bbl(
        "1000010100",
        freshness=_freshness(),
        transport=_transport("[]"),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )
    with pytest.raises(ValueError, match="no_record"):
        crosscheck_lot_zoning(pluto, no_record)


# --------------------------------------------------------------------------
# ZT-S14 - external (zoning-features fixture) observations
# --------------------------------------------------------------------------


def test_s14_zoning_features_fixture_value_reconciles_consistently() -> None:
    district = zoning_features_fixture_district()
    assert district == "R3-2"  # accepted M2-T007 fixture ZF03
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result("ZT01_record_single_lot.json", "1000010100")
    report = crosscheck_lot_zoning(
        pluto,
        ztldb,
        [
            external_observation(
                source_id=ZONING_FEATURES_SOURCE_ID,
                profile_field="zonedist1",
                value=district,
                derivation=(
                    "value read from accepted M2-T007 fixture "
                    "ZF03_query_nyzd_single_R3-2.json attribute ZONEDIST "
                    "(fixture-value cross-check; no spatial intersection "
                    "computed - owner scope exclusion)"
                ),
            )
        ],
    )
    assert report.conflicts == []
    zonedist1 = next(
        entry for entry in report.agreements if entry["field"] == "zonedist1"
    )
    assert {value["source_id"] for value in zonedist1["values"]} == {
        "nyc-dcp-pluto-soda",
        "nyc-dcp-ztldb-soda",
        ZONING_FEATURES_SOURCE_ID,
    }


def test_s14_external_disagreement_produces_the_same_typed_conflict_path() -> None:
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result("ZT01_record_single_lot.json", "1000010100")
    report = crosscheck_lot_zoning(
        pluto,
        ztldb,
        [
            external_observation(
                source_id=ZONING_FEATURES_SOURCE_ID,
                profile_field="zonedist1",
                value="R4",  # SYNTHETIC disagreement
                derivation=(
                    "SYNTHETIC test observation labeled as derived from a "
                    "zoning-features fixture; exercises the typed conflict "
                    "path only"
                ),
            )
        ],
    )
    assert [conflict["field"] for conflict in report.conflicts] == ["zonedist1"]
    values = {
        entry["source_id"]: entry["value"]
        for entry in report.conflicts[0]["values"]
    }
    # ALL THREE observations preserved; no winner chosen.
    assert values == {
        "nyc-dcp-pluto-soda": "R3-2",
        "nyc-dcp-ztldb-soda": "R3-2",
        ZONING_FEATURES_SOURCE_ID: "R4",
    }
    assert report.conflicts[0]["resolution"] == "unresolved"


def test_s14_external_observation_inputs_are_validated() -> None:
    with pytest.raises(ValueError):
        external_observation(
            source_id="", profile_field="zonedist1", value="R4", derivation="d"
        )
    with pytest.raises(ValueError, match="not a cross-checked"):
        external_observation(
            source_id="x", profile_field="lotarea", value=1, derivation="d"
        )


# --------------------------------------------------------------------------
# Profile integration (existing machinery, contract 1.3.0)
# --------------------------------------------------------------------------


def _build_integrated_profile(mutate_ztldb=None, validator=None):
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    ztldb = ztldb_result(
        "ZT01_record_single_lot.json", "1000010100", mutate=mutate_ztldb
    )
    report = crosscheck_lot_zoning(pluto, ztldb)
    profile = build_property_profile(
        pluto,
        clock=FIXED_CLOCK,
        additional_provenance=list(ztldb.facts),
        additional_conflicts=report.conflicts,
        additional_notes=report.notes,
    )
    if validator is not None:
        errors = list(validator.iter_errors(profile))
        assert errors == [], [error.message for error in errors]
    return pluto, ztldb, report, profile


def test_integration_ztldb_facts_join_provenance_with_full_lineage(
    profile_validator,
) -> None:
    pluto, ztldb, _, profile = _build_integrated_profile(
        validator=profile_validator
    )
    assert len(profile["provenance"]) == len(pluto.facts) + len(ztldb.facts)
    ztldb_records = [
        record
        for record in profile["provenance"]
        if record["source_id"] == "nyc-dcp-ztldb-soda"
    ]
    assert len(ztldb_records) == len(ztldb.facts)
    for record in ztldb_records:
        assert record["dataset_version"] == "socrata-rows-2026-04-05T18:46:56Z"
        assert record["fact_key"].startswith("fact:nyc-dcp-ztldb-soda:fdkv-4t4z:")
        assert record["response_digest"] == ztldb.response_digest
    # Cross-check notes are visible in the served reproducibility block.
    assert any(
        note.startswith("ztldb_crosscheck:")
        for note in profile["reproducibility"]["connector_notes"]
    )


def test_integration_critical_conflict_gates_analysis_readiness(
    profile_validator,
) -> None:
    def ztldb_says_r4(record: dict) -> None:
        record["zoning_district_1"] = "R4"  # SYNTHETIC disagreement

    _, _, report, profile = _build_integrated_profile(
        mutate_ztldb=ztldb_says_r4, validator=profile_validator
    )
    assert report.conflicts
    fields = [conflict["field"] for conflict in profile["conflicts"]]
    assert "zonedist1" in fields
    # EXISTING M2-T004 machinery: unresolved conflict on the critical
    # zonedist1 blocks analysis readiness - no new mechanism.
    dims = profile["status_dimensions"]
    assert dims["analysis_readiness"] == "blocked_data_conflict"
    # Both observations remain visible in the served conflict entry.
    entry = next(c for c in profile["conflicts"] if c["field"] == "zonedist1")
    assert {value["source_id"] for value in entry["values"]} == {
        "nyc-dcp-pluto-soda",
        "nyc-dcp-ztldb-soda",
    }


def test_integration_noncritical_conflict_stays_visible_without_blocking(
    profile_validator,
) -> None:
    def ztldb_adds_overlay(record: dict) -> None:
        record["commercial_overlay_1"] = "C1-3"  # SYNTHETIC vintage skew

    _, _, report, profile = _build_integrated_profile(
        mutate_ztldb=ztldb_adds_overlay, validator=profile_validator
    )
    assert [conflict["field"] for conflict in report.conflicts] == ["overlay1"]
    assert any(c["field"] == "overlay1" for c in profile["conflicts"])
    # overlay1 is not an identity/critical column: visible, not blocking.
    assert profile["status_dimensions"]["analysis_readiness"] == "ready"


def test_integration_defaults_leave_existing_builder_behavior_unchanged() -> None:
    pluto = pluto_result("F01_single_lot_normal.json", "1000010100")
    baseline = build_property_profile(pluto, clock=FIXED_CLOCK)
    explicit_defaults = build_property_profile(
        pluto,
        clock=FIXED_CLOCK,
        additional_provenance=None,
        additional_conflicts=None,
        additional_notes=None,
    )
    assert baseline == explicit_defaults  # regression: pure additive change
