"""M2-T012 acceptance scenarios PI-S1 .. PI-S8: the ONE coordinated contract
1.4.0 integration of the accepted connector wave + spatial-intersection results
into the canonical property profile.

- PI-S1 primary: a BBL with complete wave data yields a 1.4.0 profile carrying
  zoning-features facts, lot-geometry facts, and the intersection record with
  provenance; it validates against the canonical schema.
- PI-S2 uncertainty preservation: a near-boundary lot's profile shows the
  uncertainty classification AND the exact geometric result; no definitive
  single-district assignment appears anywhere in the payload.
- PI-S3 conflict: a geometric assignment disagreeing with ZTLDB produces the
  typed conflict entry (resolution 'unresolved') through the EXISTING conflict
  shape and gates analysis_readiness on the critical column.
- PI-S4 compatibility: the builder declares 1.4.0; a PLUTO-only build emits no
  1.4.0 key and validates; a wave payload that misdeclares 1.3.0 is rejected;
  1.0.0-1.3.0 payloads still validate (the last is proven in
  tests/api/test_property_contract.py backward-compat cases, re-asserted here).
- PI-S5 drift tooling: 1.4.0 flows through the M2-T010 derivation (live
  SUPPORTED_CONTRACT_VERSIONS + VERSION_INTRODUCED); a payload emitting a wave
  key below its declared version is the red path.
- PI-S6 carried defects: each enumerated carry-forward is fixed with its own
  test evidence in the connector/tooling suites (see the producer report's
  per-defect list); this file covers the integration scenarios.
- PI-S7 missing data: absent spatial results or absent connector facts degrade
  to typed missing/conditional/not_applicable statuses, never invented values.
- PI-S8 regression: the whole suite staying green (this file adds to it).

Offline and deterministic: the same fixture-transport seam the accepted
M1-T005 / M2-T004 / M2-T008 suites use; no test touches the network.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.pluto_soda import TransportResponse
from app.connectors.pluto_soda import fetch_by_bbl as pluto_fetch_by_bbl
from app.connectors.ztldb_soda import fetch_by_bbl as ztldb_fetch_by_bbl
from app.connectors.ztldb_soda import fetch_source_freshness
from app.profile import contract as contract_module
from app.profile.builder import PROFILE_CONTRACT_VERSION, build_property_profile
from app.profile.contract import (
    SUPPORTED_CONTRACT_VERSIONS,
    VERSION_INTRODUCED,
    ContractValidationError,
    validate_profile,
)
from app.profile.zoning_crosscheck import (
    GEOMETRIC_SOURCE_ID,
    crosscheck_lot_zoning,
    geometric_zoning_observations,
)

TESTS_DIR = Path(__file__).resolve().parents[1]
PLUTO_FIXTURES = TESTS_DIR / "fixtures" / "pluto"
ZTLDB_FIXTURES = TESTS_DIR / "fixtures" / "ztldb"

FIXED_CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"
_DIGEST = "sha256:" + "0" * 64
_CRS = {"wkid": 102718, "latest_wkid": 2263, "authority": "EPSG:2263"}


# --------------------------------------------------------------------------
# Result builders (same fixture-transport seam as the accepted suites)
# --------------------------------------------------------------------------


def _body(directory: Path, name: str) -> str:
    return json.loads((directory / name).read_text(encoding="utf-8"))["response_body_raw"]


def _transport(*bodies):
    items = [
        b if isinstance(b, TransportResponse) else TransportResponse(200, b) for b in bodies
    ]

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return items.pop(0)

    return transport


def pluto_result(fixture: str = "F01_single_lot_normal.json", bbl: str = BBL):
    return pluto_fetch_by_bbl(
        bbl,
        transport=_transport(_body(PLUTO_FIXTURES, fixture)),
        sleep=lambda s: None,
        clock=FIXED_CLOCK,
        correlation_id="wave-pluto",
    )


def _freshness():
    return fetch_source_freshness(
        transport=_transport(_body(ZTLDB_FIXTURES, "ZT08_api_views_metadata.json")),
        sleep=lambda s: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )


def ztldb_result(fixture: str = "ZT01_record_single_lot.json", bbl: str = BBL):
    return ztldb_fetch_by_bbl(
        bbl,
        freshness=_freshness(),
        transport=_transport(_body(ZTLDB_FIXTURES, fixture)),
        sleep=lambda s: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        correlation_id="wave-ztldb",
        app_token=None,
    )


def _pluto_field(result, field: str):
    for fact in result.facts:
        if fact["original_field_name"] == field:
            return fact["normalized_value"]
    return None


# --------------------------------------------------------------------------
# Wave input builders (dict form of the accepted connector/engine results)
# --------------------------------------------------------------------------


def lot_geometry(*, outcome="single_feature", status="valid", area=12345.6, review=False):
    return {
        "outcome": outcome,
        "review_required": review,
        "geometry": (
            {"status": status, "original_geometry_digest": "sha256:" + "a" * 64}
            if status is not None
            else None
        ),
        "area_sq_ft": area,
        "shape_area_attribute_sq_ft": area,
        "normalized_digest": "sha256:" + "b" * 64,
        "crs": dict(_CRS),
        "source_data_last_edited": "2026-07-15T00:00:00Z",
        "retrieved_at": "2026-07-20T12:00:00Z",
        "shapely_version": "2.0.7",
        "geos_version": "3.11.4",
        "drift_signals": [],
        "identifier_conflicts": [],
    }


def zoning_features(*, with_drift=True):
    layers = [
        {
            "layer": "nyzd",
            "record_count": 1,
            "normalized_digest": "sha256:" + "c" * 64,
            "source_data_last_edited": "2026-07-14T00:00:00Z",
            "retrieved_at": "2026-07-20T12:00:00Z",
            "crs": dict(_CRS),
            "drift_signals": [],
        }
    ]
    if with_drift:
        layers.append(
            {
                "layer": "nyco",
                "record_count": 0,
                "normalized_digest": "sha256:" + "d" * 64,
                "retrieved_at": "2026-07-20T12:00:00Z",
                "drift_signals": ["added_field:FOO"],
            }
        )
    return layers


def intersection_record(
    *, lot_overall_class="boundary_uncertain", geometric_label=None, review=True
):
    crosscheck = None
    if geometric_label is not None:
        crosscheck = {
            "outcome": "ordering_disagreement",
            "geometric_ordered_districts": [{"label": geometric_label, "share_point": 0.99}],
            "ztldb_ordered_districts": [],
            "display_upgrade": "conditional",
        }
    return {
        "bbl": BBL,
        "lot_overall_class": lot_overall_class,
        "pairs": [
            {
                "layer": "nyzd",
                "family": "base_zoning",
                "district_label": "R6",
                "pair_class": "near_boundary_uncertain",
                "raw_intersection_sq_ft": 6000.0,
                "firm_intersection_sq_ft": 5000.0,
                "dilated_intersection_sq_ft": 6500.0,
                "distance_ft": 3.2,
                "lot_area_sq_ft": 12345.6,
                "share_min": 0.40,
                "share_point": 0.55,
                "share_max": 0.70,
                "minor_portion": False,
            }
        ],
        "coverage_audits": [{"family": "base_zoning", "status": "unknown"}],
        "crosscheck": crosscheck,
        "professional_review_required": review,
        "review_reasons": (
            ["lot_overall_class=boundary_uncertain (advisory 2.6.1/2.6.2)"] if review else []
        ),
        "unassigned_area": [],
        "overlap_area": [],
        "accuracy_records": [{"applies_to": "lot", "value_ft": 20.0, "basis": "documented"}],
        "policy": {"version": "policy-1"},
        "provenance": {
            "source_id": "nyc-dcp-mappluto-arcgis",
            "requested_bbl": BBL,
            "retrieved_at": "2026-07-20T12:00:00Z",
            "normalized_digest": "sha256:" + "e" * 64,
            "source_data_last_edited": "2026-07-15T00:00:00Z",
            "crs": dict(_CRS),
            "shapely_version": "2.0.7",
            "geos_version": "3.11.4",
        },
        "coverage_note": "facts_with_uncertainty; not a Verified zoning determination",
        "notes": [],
    }


def _prov_ids(profile: dict) -> set[str]:
    return {record["provenance_id"] for record in profile["provenance"]}


# ==========================================================================
# PI-S1 primary
# ==========================================================================


def test_pi_s1_complete_wave_profile_carries_all_streams_with_provenance() -> None:
    profile = build_property_profile(
        pluto_result(),
        clock=FIXED_CLOCK,
        lot_geometry=lot_geometry(),
        zoning_features=zoning_features(),
        spatial_intersection=intersection_record(),
    )
    validate_profile(profile)  # canonical schema + consistency, must not raise
    assert profile["profile_version"]["contract_version"] == "1.4.0"

    ids = _prov_ids(profile)
    # zoning_features: two layers, each with a resolvable provenance record.
    layers = profile["zoning_features"]["layers"]
    assert [entry["layer"] for entry in layers] == ["nyzd", "nyco"]
    assert layers[0]["coverage_status"] == "conditional"
    assert layers[1]["coverage_status"] == "unsupported"  # nyco carried a drift signal
    for entry in layers:
        assert entry["provenance_ref"] in ids

    # lot_geometry: resolvable provenance, validity taxonomy preserved.
    lg = profile["lot_geometry"]
    assert lg["outcome"] == "single_feature"
    assert lg["geometry_status"] == "valid"
    assert lg["provenance_ref"] in ids

    # spatial_intersection: engine-internal coverage_audits EXCLUDED; refs resolve.
    si = profile["spatial_intersection"]
    assert "coverage_audits" not in si
    assert si["bbl"] == BBL
    assert si["provenance_refs"] and all(ref in ids for ref in si["provenance_refs"])


# ==========================================================================
# PI-S2 uncertainty preservation
# ==========================================================================


def test_pi_s2_uncertainty_class_and_exact_result_both_present_never_collapsed() -> None:
    profile = build_property_profile(
        pluto_result(),
        clock=FIXED_CLOCK,
        lot_geometry=lot_geometry(),
        spatial_intersection=intersection_record(lot_overall_class="boundary_uncertain"),
    )
    validate_profile(profile)
    si = profile["spatial_intersection"]

    # The uncertainty classification is present ...
    assert si["lot_overall_class"] == "boundary_uncertain"
    assert si["pairs"][0]["pair_class"] == "near_boundary_uncertain"
    assert si["professional_review_required"] is True
    # ... AND the exact geometric result, with the share RANGE not collapsed.
    pair = si["pairs"][0]
    assert pair["raw_intersection_sq_ft"] == 6000.0
    assert pair["distance_ft"] == 3.2
    assert pair["share_min"] < pair["share_point"] < pair["share_max"]

    # No definitive single-district assignment anywhere in the payload: the only
    # "Verified" mention is the coverage_note explicitly disclaiming it.
    assert si["coverage_note"] == "facts_with_uncertainty; not a Verified zoning determination"
    blob = json.dumps(si)
    assert "assigned_district" not in blob
    assert "single_district_confident" not in blob  # this lot is uncertain, not confident
    # The note's disclaimer is the ONLY occurrence of the word "Verified".
    assert blob.count("Verified") == 1


# ==========================================================================
# PI-S3 conflict (fourth geometric evidence stream)
# ==========================================================================


def test_pi_s3_geometric_disagreement_with_ztldb_is_a_typed_unresolved_conflict() -> None:
    pluto = pluto_result()
    ztldb = ztldb_result()
    pluto_zonedist1 = _pluto_field(pluto, "zonedist1")
    assert isinstance(pluto_zonedist1, str) and pluto_zonedist1

    # A confident geometric single-district assignment that DISAGREES with the
    # PLUTO/ZTLDB zonedist1 (deliberately a different, clearly-labelled value).
    disagreeing = f"{pluto_zonedist1}-GEOMETRIC-DIFFERENT"
    record = intersection_record(
        lot_overall_class="single_district_confident", geometric_label=disagreeing
    )
    observations = geometric_zoning_observations(record)
    assert len(observations) == 1
    assert observations[0]["source_id"] == GEOMETRIC_SOURCE_ID
    assert observations[0]["value"] == disagreeing

    report = crosscheck_lot_zoning(pluto, ztldb, external_observations=observations)
    zonedist1_conflicts = [c for c in report.conflicts if c["field"] == "zonedist1"]
    assert len(zonedist1_conflicts) == 1
    conflict = zonedist1_conflicts[0]
    assert conflict["resolution"] == "unresolved"  # never adjudicated
    sources = {v["source_id"]: v["value"] for v in conflict["values"]}
    assert sources[GEOMETRIC_SOURCE_ID] == disagreeing  # geometric value preserved
    assert "nyc-dcp-pluto-soda" in sources  # PLUTO value preserved too

    # The unresolved conflict on the CRITICAL zonedist1 column gates readiness
    # through the existing M2-T004 machinery (no new mechanism).
    profile = build_property_profile(
        pluto,
        clock=FIXED_CLOCK,
        additional_conflicts=report.conflicts,
        spatial_intersection=record,
        lot_geometry=lot_geometry(),
    )
    validate_profile(profile)
    assert profile["status_dimensions"]["analysis_readiness"] == "blocked_data_conflict"


def test_pi_s3_geometric_agreement_is_not_a_conflict() -> None:
    pluto = pluto_result()
    ztldb = ztldb_result()
    agreeing = _pluto_field(pluto, "zonedist1")
    record = intersection_record(
        lot_overall_class="single_district_confident", geometric_label=agreeing
    )
    report = crosscheck_lot_zoning(
        pluto, ztldb, external_observations=geometric_zoning_observations(record)
    )
    assert [c for c in report.conflicts if c["field"] == "zonedist1"] == []


def test_pi_s3_uncertain_geometry_emits_no_collapsing_observation() -> None:
    # Only single_district_confident contributes a zonedist1 value; every other
    # class preserves uncertainty by emitting nothing.
    for klass in (
        "boundary_uncertain",
        "split_lot_confident",
        "sliver_ambiguous",
        "data_conflict",
        "invalid_geometry_review",
    ):
        record = intersection_record(lot_overall_class=klass, geometric_label="R6")
        assert geometric_zoning_observations(record) == []


# ==========================================================================
# PI-S4 compatibility
# ==========================================================================


def test_pi_s4_pluto_only_build_declares_1_4_0_and_emits_no_wave_keys() -> None:
    profile = build_property_profile(pluto_result(), clock=FIXED_CLOCK)
    validate_profile(profile)
    assert PROFILE_CONTRACT_VERSION == "1.4.0"
    assert profile["profile_version"]["contract_version"] == "1.4.0"
    assert "zoning_features" not in profile
    assert "lot_geometry" not in profile
    assert "spatial_intersection" not in profile


def test_pi_s4_wave_payload_misdeclaring_1_3_0_is_rejected() -> None:
    profile = build_property_profile(
        pluto_result(), clock=FIXED_CLOCK, lot_geometry=lot_geometry()
    )
    assert "lot_geometry" in profile
    profile["profile_version"]["contract_version"] = "1.3.0"  # stale declaration
    with pytest.raises(ContractValidationError) as excinfo:
        validate_profile(profile)
    assert excinfo.value.reason == "declared_version_below_emitted_keys"


def test_pi_s4_pre_1_4_0_fixtures_still_validate() -> None:
    # A 1.0.0 instance with no additive keys and a 1.3.0 LKG instance both
    # remain valid against the 1.4.0-published schema (additive-only proof;
    # the full matrix lives in tests/api/test_property_contract.py).
    fixtures = TESTS_DIR.parents[2] / "packages" / "contracts" / "fixtures" / "valid"
    v100 = json.loads((fixtures / "property_profile" / "full_example.json").read_text("utf-8"))
    assert v100["profile_version"]["contract_version"] == "1.0.0"
    validate_profile(v100)
    v130 = json.loads(
        (fixtures / "property_profile" / "staleness_lkg_m2_t006.json").read_text("utf-8")
    )
    assert v130["profile_version"]["contract_version"] == "1.3.0"
    validate_profile(v130)


# ==========================================================================
# PI-S5 drift tooling / derivation
# ==========================================================================


def test_pi_s5_supported_versions_and_version_introduced_carry_the_wave_keys() -> None:
    # SUPPORTED_CONTRACT_VERSIONS is derived LIVE from the bundled schema enum.
    assert "1.4.0" in SUPPORTED_CONTRACT_VERSIONS
    assert SUPPORTED_CONTRACT_VERSIONS[-1] == "1.4.0"
    for key in ("zoning_features", "lot_geometry", "spatial_intersection"):
        assert VERSION_INTRODUCED[key] == "1.4.0"


@pytest.mark.parametrize(
    "key",
    ["zoning_features", "lot_geometry", "spatial_intersection"],
)
def test_pi_s5_declaring_below_an_emitted_wave_key_is_the_red_path(key: str) -> None:
    # The declared-vs-emitted consistency check treats every wave key exactly
    # like the earlier additive keys: emitting it while declaring 1.3.0 fails.
    kwargs = {
        "zoning_features": {"zoning_features": zoning_features()},
        "lot_geometry": {"lot_geometry": lot_geometry()},
        "spatial_intersection": {"spatial_intersection": intersection_record()},
    }[key]
    profile = build_property_profile(pluto_result(), clock=FIXED_CLOCK, **kwargs)
    assert key in profile
    profile["profile_version"]["contract_version"] = "1.3.0"
    with pytest.raises(ContractValidationError) as excinfo:
        contract_module._assert_declared_matches_emitted(profile)
    assert excinfo.value.reason == "declared_version_below_emitted_keys"


# ==========================================================================
# PI-S7 missing data degrades to typed statuses, never invented values
# ==========================================================================


def test_pi_s7_no_feature_lot_geometry_degrades_to_typed_status() -> None:
    profile = build_property_profile(
        pluto_result(),
        clock=FIXED_CLOCK,
        lot_geometry=lot_geometry(outcome="no_feature", status=None, area=None),
    )
    validate_profile(profile)
    lg = profile["lot_geometry"]
    assert lg["outcome"] == "no_feature"
    assert lg["geometry_status"] is None  # stated, not invented
    assert lg["coverage_status"] == "not_applicable"
    assert lg["area_sq_ft"] is None


def test_pi_s7_review_required_geometry_is_professional_review_required() -> None:
    profile = build_property_profile(
        pluto_result(),
        clock=FIXED_CLOCK,
        lot_geometry=lot_geometry(outcome="multiple_features", status=None, review=True),
    )
    validate_profile(profile)
    assert profile["lot_geometry"]["coverage_status"] == "professional_review_required"


def test_pi_s7_absent_wave_data_invents_nothing() -> None:
    # No wave inputs at all: the profile is exactly the PLUTO-only shape - no
    # empty wave sections, no placeholder values.
    profile = build_property_profile(pluto_result(), clock=FIXED_CLOCK)
    for key in ("zoning_features", "lot_geometry", "spatial_intersection"):
        assert key not in profile
