"""Task M2-T004 acceptance scenarios S1-S6: data-semantics separation and
snapshot lineage.

- S1: the feasibility-relevant column basis (builder FEASIBILITY_COLUMNS,
  grounded in the official PLUTO 26v1 data dictionary via
  docs/research/pluto-mappluto-2026-07-16.md) drives completeness; the
  108-column denominator is gone.
- S2: the five status dimensions are INDEPENDENT - a complete source record
  with missing geometry reports both truths simultaneously.
- S3: stable fact_key vs immutable per-retrieval observation_id.
- S4: canonical digests - deterministic across identical responses, flipped
  by any value change, recorded per response and per fact.
- S5: snapshot lineage observation -> source version -> request URL/timestamp
  with no gaps on any fact.
- S6: additive contract evolution - pre-M2-T004 shapes remain valid. The
  builder's declared version was resolved to the canonical 1.2.0 by task
  M2-T003 (which owns the declaration/validation decision); this test asserts
  the resolved declaration.

Offline and deterministic: fixture transports replay the accepted M1-T002
official captures; synthetic variants (clearly labeled) are derived in-test.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.connectors.pluto_soda import (
    CANONICALIZATION_SPEC,
    PLUTO_COLUMNS,
    TransportResponse,
    build_fact_key,
    canonical_json_digest,
    fetch_by_bbl,
)
from app.profile.builder import (
    CRITICAL_COLUMNS,
    FEASIBILITY_COLUMNS,
    GEOMETRY_COLUMNS,
    PROFILE_CONTRACT_VERSION,
    build_property_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"

FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731

# Columns F01 lacks a usable value for (numfloors absent with numbldgs > 0;
# yearbuilt 0 = unknown per dictionary p.34-35) - the two REAL feasibility
# gaps of the official capture.
F01_FEASIBILITY_GAPS = {"numfloors", "yearbuilt"}


def load_fixture_body(name: str) -> str:
    fixture = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    return fixture["response_body_raw"]


def fetch_from_body(
    body: str,
    bbl: str = "1000010100",
    *,
    correlation_id: str = "m2t004-test",
    observation_event_id: str | None = None,
):
    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, body)

    return fetch_by_bbl(
        bbl,
        transport=transport,
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
        observation_event_id=observation_event_id,
    )


def synthetic_body(mutate) -> str:
    """SYNTHETIC variant of the official F01 capture (exercises builder logic
    only; never presented as official data)."""
    record = json.loads(load_fixture_body("F01_single_lot_normal.json"))[0]
    mutate(record)
    return json.dumps([record])


def complete_record(record: dict) -> None:
    """SYNTHETIC: make every FEASIBILITY_COLUMNS member usable. F01 carries
    all basis columns except numfloors (absent, numbldgs > 0) and yearbuilt
    (0 = unknown); give both plausible non-official values."""
    record["numfloors"] = "3.0"
    record["yearbuilt"] = "1931"


def build_profile(body: str, **fetch_kwargs) -> dict:
    return build_property_profile(fetch_from_body(body, **fetch_kwargs), clock=FIXED_CLOCK)


@pytest.fixture(scope="module")
def profile_validator():
    """jsonschema validator for property_profile.schema.json v1 with all
    referenced contracts resolved (mirrors validate_contracts.py)."""
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
# S1 - the feasibility-relevant basis drives completeness; 108-column
#      denominator is gone
# --------------------------------------------------------------------------


def test_s1_basis_is_explicit_and_inside_the_official_inventory() -> None:
    # Every basis column exists in the official 108-column SODA inventory
    # (fixture F08 contract constant) - the set cannot silently drift.
    assert FEASIBILITY_COLUMNS <= PLUTO_COLUMNS
    assert CRITICAL_COLUMNS <= FEASIBILITY_COLUMNS
    assert CRITICAL_COLUMNS == {"lotarea", "zonedist1"}
    assert len(FEASIBILITY_COLUMNS) == 19
    # Geometry columns are excluded from the basis BY DESIGN (independence).
    assert not FEASIBILITY_COLUMNS & GEOMETRY_COLUMNS


def test_s1_non_feasibility_absence_no_longer_degrades_completeness() -> None:
    # SYNTHETIC: all 19 basis columns usable; ~38 non-basis columns of the
    # official record remain ABSENT (F01 has 67 of 108 keys). Pre-M2-T004
    # this profile was 'missing_noncritical' purely because of columns like
    # sanborn/firecomp/zonedist2 - the owner-audit defect.
    profile = build_profile(synthetic_body(complete_record))
    assert profile["data_completeness"] == "complete"
    assert profile["status_dimensions"]["source_record_completeness"] == "complete"
    # The absent non-basis columns are STILL visible - nothing is hidden -
    # they just no longer drive the label.
    non_basis = [e for e in profile["missing_inputs"] if not e["feasibility_relevant"]]
    assert len(non_basis) >= 30
    assert all(e["criticality"] == "noncritical" for e in non_basis)


def test_s1_official_f01_gaps_are_exactly_the_basis_gaps() -> None:
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    flagged = {e["field"] for e in profile["missing_inputs"] if e["feasibility_relevant"]}
    assert flagged == F01_FEASIBILITY_GAPS
    assert profile["data_completeness"] == "missing_noncritical"
    assert profile["status_dimensions"]["source_record_completeness"] == "partial"


def test_s1_feasibility_absence_still_degrades_completeness() -> None:
    def drop_lotfront(record: dict) -> None:
        complete_record(record)
        record.pop("lotfront")

    profile = build_profile(synthetic_body(drop_lotfront))
    assert profile["data_completeness"] == "missing_noncritical"
    assert profile["status_dimensions"]["source_record_completeness"] == "partial"
    entry = next(e for e in profile["missing_inputs"] if e["field"] == "lotfront")
    assert entry["feasibility_relevant"] is True
    assert entry["criticality"] == "noncritical"


def test_s1_every_missing_input_entry_carries_the_membership_flag() -> None:
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    assert profile["missing_inputs"]
    for entry in profile["missing_inputs"]:
        assert entry["feasibility_relevant"] is (entry["field"] in FEASIBILITY_COLUMNS)


# --------------------------------------------------------------------------
# S2 - dimension independence (never collapsed into one label)
# --------------------------------------------------------------------------


def test_s2_complete_record_with_missing_geometry_reports_both_truths() -> None:
    def complete_but_no_geometry(record: dict) -> None:
        complete_record(record)
        for column in ("latitude", "longitude", "xcoord", "ycoord"):
            record.pop(column, None)

    profile = build_profile(synthetic_body(complete_but_no_geometry))
    dims = profile["status_dimensions"]
    # The owner's S2 fixture: complete source record AND missing geometry
    # SIMULTANEOUSLY - proof the dimensions never collapse.
    assert dims["source_record_completeness"] == "complete"
    assert dims["geometry_validity"] == "missing"
    assert dims["analysis_readiness"] == "ready"
    assert "geometry" not in profile["identity"]


def test_s2_missing_critical_blocks_analysis_but_not_geometry() -> None:
    def geometry_but_no_lotarea(record: dict) -> None:
        complete_record(record)
        record.pop("lotarea")

    profile = build_profile(synthetic_body(geometry_but_no_lotarea))
    dims = profile["status_dimensions"]
    # Inverse independence: geometry present while the record is partial and
    # analysis is blocked on the critical gap.
    assert dims["geometry_validity"] == "not_computed"
    assert dims["source_record_completeness"] == "partial"
    assert dims["analysis_readiness"] == "blocked_missing_critical"
    assert profile["data_completeness"] == "missing_critical"


def test_s2_identity_conflict_blocks_analysis_independently() -> None:
    def conflicting_borocode(record: dict) -> None:
        complete_record(record)
        record["borocode"] = "3"  # disagrees with the Manhattan BBL digits

    profile = build_profile(synthetic_body(conflicting_borocode))
    dims = profile["status_dimensions"]
    assert dims["analysis_readiness"] == "blocked_data_conflict"
    # The record itself is complete - readiness and completeness are
    # different questions with different answers.
    assert dims["source_record_completeness"] == "complete"
    assert profile["conflicts"], "the blocking conflict stays visible"


def test_s2_not_yet_computable_dimensions_are_declared_never_inferred() -> None:
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    dims = profile["status_dimensions"]
    # No rule engine before M4; no financial engine before GDS Phase C:
    # 'not_computed' is DECLARED - the platform never invents coverage.
    assert dims["rule_coverage"] == "not_computed"
    assert dims["financial_readiness"] == "not_computed"
    assert set(dims) == {
        "source_record_completeness", "analysis_readiness", "rule_coverage",
        "geometry_validity", "financial_readiness", "policy",
    }
    assert dims["policy"].startswith("status_dimensions are derived")


# --------------------------------------------------------------------------
# S3 - stable fact_key vs immutable per-retrieval observation_id
# --------------------------------------------------------------------------


def test_s3_reobservation_preserves_fact_key_and_issues_new_observation_id() -> None:
    body = load_fixture_body("F01_single_lot_normal.json")
    first = fetch_from_body(body, observation_event_id="event-A")
    second = fetch_from_body(body, observation_event_id="event-B")
    for fact_a, fact_b in zip(first.facts, second.facts, strict=True):
        assert fact_a["fact_key"] == fact_b["fact_key"]
        assert fact_a["observation_id"] != fact_b["observation_id"]
    # Observation ids are unique within a retrieval as well.
    ids = [fact["observation_id"] for fact in first.facts]
    assert len(ids) == len(set(ids))


def test_s3_fact_key_is_stable_across_dataset_versions() -> None:
    # SYNTHETIC: the same lot observed under a NEWER PLUTO release. The
    # logical fact identity must survive; the version-scoped provenance_id
    # must not (that is exactly the difference between the two).
    body_v1 = synthetic_body(complete_record)

    def next_release(record: dict) -> None:
        complete_record(record)
        record["version"] = "26v2"

    body_v2 = synthetic_body(next_release)
    facts_v1 = {f["original_field_name"]: f for f in fetch_from_body(body_v1).facts}
    facts_v2 = {f["original_field_name"]: f for f in fetch_from_body(body_v2).facts}
    lot_v1, lot_v2 = facts_v1["lotarea"], facts_v2["lotarea"]
    assert lot_v1["fact_key"] == lot_v2["fact_key"] == build_fact_key(
        "1000010100", "lotarea"
    )
    assert lot_v1["provenance_id"] != lot_v2["provenance_id"]


def test_s3_both_identities_persist_in_profile_provenance() -> None:
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    assert profile["provenance"]
    for record in profile["provenance"]:
        assert record["fact_key"].startswith("fact:nyc-dcp-pluto-soda:64uk-42ks:")
        assert record["observation_id"].startswith("obs:")
        assert record["original_field_name"] in record["fact_key"]


# --------------------------------------------------------------------------
# S4 - canonical digests: deterministic, sensitive, recorded per response
#      and per fact
# --------------------------------------------------------------------------


def test_s4_digest_is_deterministic_and_key_order_independent() -> None:
    assert canonical_json_digest({"a": 1, "b": "x"}) == canonical_json_digest(
        {"b": "x", "a": 1}
    )
    assert canonical_json_digest([1, "2", None, True]) == canonical_json_digest(
        [1, "2", None, True]
    )


def test_s4_identical_responses_digest_equal_despite_byte_differences() -> None:
    body = load_fixture_body("F01_single_lot_normal.json")
    # Same parsed content, different bytes (whitespace + key order changes).
    reserialized = json.dumps(json.loads(body), indent=2, sort_keys=True)
    assert fetch_from_body(body).response_digest == fetch_from_body(
        reserialized
    ).response_digest


def test_s4_any_value_change_flips_the_digests() -> None:
    base = fetch_from_body(synthetic_body(complete_record))

    def one_value_changed(record: dict) -> None:
        complete_record(record)
        record["lotarea"] = "23122"  # was 23121

    changed = fetch_from_body(synthetic_body(one_value_changed))
    assert base.response_digest != changed.response_digest
    by_field_base = {f["original_field_name"]: f for f in base.facts}
    by_field_changed = {f["original_field_name"]: f for f in changed.facts}
    assert (
        by_field_base["lotarea"]["value_digest"]
        != by_field_changed["lotarea"]["value_digest"]
    )
    # Untouched values keep their value_digest - the flip is exactly scoped.
    assert (
        by_field_base["lotfront"]["value_digest"]
        == by_field_changed["lotfront"]["value_digest"]
    )


def test_s4_digests_recorded_per_response_and_per_fact() -> None:
    result = fetch_from_body(load_fixture_body("F01_single_lot_normal.json"))
    profile = build_property_profile(result, clock=FIXED_CLOCK)
    assert result.response_digest
    assert profile["reproducibility"]["response_digest"] == result.response_digest
    assert profile["reproducibility"]["digest_canonicalization"] == CANONICALIZATION_SPEC
    for record in profile["provenance"]:
        assert record["response_digest"] == result.response_digest
        # Every value digest is independently recomputable from the verbatim
        # original_value under the recorded canonicalization.
        assert record["value_digest"] == canonical_json_digest(record["original_value"])


# --------------------------------------------------------------------------
# S5 - snapshot lineage without gaps
# --------------------------------------------------------------------------

LINEAGE_KEYS = (
    # observation -> source version -> request, per M2-T004 S5.
    "observation_id", "fact_key", "value_digest", "response_digest",
    "retrieved_at", "dataset_version", "source_id", "dataset_id", "request_url",
)


def test_s5_every_fact_traces_observation_version_request_no_gaps() -> None:
    result = fetch_from_body(load_fixture_body("F01_single_lot_normal.json"))
    profile = build_property_profile(result, clock=FIXED_CLOCK)
    assert profile["provenance"]
    for record in profile["provenance"]:
        for key in LINEAGE_KEYS:
            assert record.get(key), f"lineage gap: {record['original_field_name']}.{key}"
        assert record["retrieved_at"] == result.retrieved_at
        assert record["dataset_version"] == result.dataset_version
        assert record["request_url"] == result.request_url


def test_s5_no_match_snapshot_also_carries_the_response_digest() -> None:
    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, "[]")

    result = fetch_by_bbl(
        "5999999999",
        transport=transport,
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
    )
    assert result.status == "no_match"
    # The empty official response IS the evidence of absence; its digest
    # makes even a no-match reproducible.
    assert result.response_digest == canonical_json_digest([])


def test_s5_builder_refuses_a_result_without_response_digest() -> None:
    result = fetch_from_body(load_fixture_body("F01_single_lot_normal.json"))
    result.response_digest = None  # simulate a pre-M2-T004 constructed result
    with pytest.raises(ValueError, match="response_digest"):
        build_property_profile(result, clock=FIXED_CLOCK)


# --------------------------------------------------------------------------
# S6 - additive contract evolution
# --------------------------------------------------------------------------


def test_s6_new_profile_validates_against_evolved_contract(profile_validator) -> None:
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    errors = list(profile_validator.iter_errors(profile))
    assert errors == [], [error.message for error in errors]


def test_s6_pre_m2t004_shape_remains_valid(profile_validator) -> None:
    # Strip every M2-T004 key (and the M2-T006 staleness key): what remains is
    # the accepted M1-T005/M1-T006 shape, which MUST still validate (additive
    # evolution, nothing retyped). Schema-level check only - the declared
    # version stays the builder's; declared-vs-emitted is validate_profile's
    # job, proven in tests/api/test_property_contract.py.
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    profile.pop("status_dimensions")
    profile["reproducibility"].pop("response_digest")
    profile["reproducibility"].pop("digest_canonicalization")
    profile["reproducibility"].pop("staleness")
    for entry in profile["missing_inputs"]:
        entry.pop("feasibility_relevant")
    for record in profile["provenance"]:
        for key in ("fact_key", "observation_id", "value_digest", "response_digest"):
            record.pop(key)
    errors = list(profile_validator.iter_errors(profile))
    assert errors == [], [error.message for error in errors]


def test_s6_builder_declares_resolved_canonical_contract_version() -> None:
    # M2-T003 established declare-what-you-emit; M2-T006 advanced it to 1.3.0;
    # M2-T012 advanced the declaration to 1.4.0 (the builder can now emit the
    # optional wave/spatial-integration keys). (Backward compatibility -
    # 1.0.0/1.1.0/1.2.0/1.3.0 instances remain valid and served - is proven in
    # tests/api/test_property_contract.)
    assert PROFILE_CONTRACT_VERSION == "1.4.0"
    profile = build_profile(load_fixture_body("F01_single_lot_normal.json"))
    assert profile["profile_version"]["contract_version"] == "1.4.0"
    # Direct builder path = fresh retrieval: the truthful fresh marker with
    # ONLY the two required booleans (no invented age/error values).
    assert profile["reproducibility"]["staleness"] == {
        "served_from_cache": False,
        "stale": False,
    }
