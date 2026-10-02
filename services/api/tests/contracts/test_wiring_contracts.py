"""Lane C packet W0 wiring contracts, validated against the canonical schemas.

The three W0 contracts - hidden_issue_flags, transit_parking and parity_data -
each carry valid and invalid fixtures. Every valid fixture must pass its
``validate_<stem>_document`` (the runtime path, built from the byte-identical
bundled schemas); every invalid fixture must be rejected BY THE SCHEMA once its
fixture-only ``_expected_failure`` annotation is stripped.

On top of schema validation this module pins the packet's honesty rules, so a
future fixture cannot quietly reintroduce a banned shape:

- parity_data is DATA, never a valuation: the not_a_valuation disclosure is
  present and there is no average or price-per-square-foot field anywhere.
- remaining development capacity reads ONLY "Not confirmed" (owner wording,
  D-090-R038) and no remaining-capacity / allowance / FAR number appears.
- transit_parking carries the zone only, never a parking OUTCOME (spaces, a
  waiver or an exemption).
- nothing claims a combined zoning lot is verified.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from app.connectors.dof_sales_soda import (
    build_by_bbl_url,
    build_candidates_url,
    fetch_comparable_candidates,
    fetch_sales_by_bbl,
)
from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    StudyContractError,
    validate_hidden_issue_flags_document,
    validate_parity_data_document,
    validate_transit_parking_document,
)
from app.profile.existing_floor_area import (
    ExistingFloorAreaEvidence,
    StatedAssumption,
    resolve_existing_zoning_floor_area,
)
from app.profile.hidden_issue_flags import AsOfRightAllowance, existing_building_group
from app.profile.parity.comparable_sales import (
    select_comparables,
    subject_spec_from_record,
)
from app.profile.parity.unused_floor_area import unused_floor_area_data
from app.resilience.transport import TransportResponse

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
DOF_PACK = REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "dof_sales_bayside"

W0_VALIDATORS = {
    "hidden_issue_flags": validate_hidden_issue_flags_document,
    "transit_parking": validate_transit_parking_document,
    "parity_data": validate_parity_data_document,
}

# The SPECIFIC schema location each invalid fixture must fail at (not a generic
# failure) - the fixture's stated defect, pinned (CODING_RULES caution).
EXPECTED_INVALID_DEFECT = {
    # zoning_lot_history group with status 'opportunity' -> the group/status oneOf
    # rejects the flag object.
    "zoning_lot_history_opportunity.json": ("groups/0/flags/0", None),
    # recorded status with transit_zone null -> the root status/zone oneOf.
    "recorded_without_transit_zone.json": ("<root>", None),
    # unused_floor_area.status not the const 'not_confirmed'.
    "unused_floor_area_confirmed.json": (
        "unused_floor_area/status",
        "'not_confirmed' was expected",
    ),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_paths(stem: str) -> list[Path]:
    return sorted((FIXTURE_ROOT / "valid" / stem).glob("*.json"))


def _invalid_paths(stem: str) -> list[Path]:
    return sorted((FIXTURE_ROOT / "invalid" / stem).glob("*.json"))


VALID = [(stem, path) for stem in W0_VALIDATORS for path in _valid_paths(stem)]
INVALID = [(stem, path) for stem in W0_VALIDATORS for path in _invalid_paths(stem)]


def _fixture_id(item: tuple[str, Path]) -> str:
    return f"{item[0]}/{item[1].name}"


def _iter_keys(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _iter_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_keys(item)


def _iter_strings(node: Any) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_strings(item)


# ---- schema validation ---------------------------------------------------------------------


def test_every_w0_stem_has_valid_and_invalid_fixtures() -> None:
    for stem in W0_VALIDATORS:
        assert _valid_paths(stem), f"no valid fixture for {stem}"
        assert _invalid_paths(stem), f"no invalid fixture for {stem}"


@pytest.mark.parametrize("item", VALID, ids=_fixture_id)
def test_valid_fixture_passes_canonical_schema(item: tuple[str, Path]) -> None:
    stem, path = item
    W0_VALIDATORS[stem](_load(path))


@pytest.mark.parametrize("item", INVALID, ids=_fixture_id)
def test_invalid_fixture_fails_on_its_stated_defect(item: tuple[str, Path]) -> None:
    stem, path = item
    document = _load(path)
    assert isinstance(document.pop(FIXTURE_ONLY_KEY, None), str), "annotation missing"
    with pytest.raises(StudyContractError) as excinfo:
        W0_VALIDATORS[stem](document)
    assert "failed canonical schema validation" in str(excinfo.value)
    assert excinfo.value.contract == stem
    # The SPECIFIC stated defect, not just a generic failure.
    expected_location, expected_detail = EXPECTED_INVALID_DEFECT[path.name]
    assert excinfo.value.location == expected_location, excinfo.value.location
    if expected_detail is not None:
        assert expected_detail in str(excinfo.value)


# ---- honesty rules -------------------------------------------------------------------------

# Derived-valuation field names a parity document must never carry.
_VALUATION_KEYS = {
    "average",
    "avg",
    "mean",
    "price_per_square_foot",
    "price_per_sq_ft",
    "ppsf",
    "dollars_per_square_foot",
    "estimate",
    "estimated_value",
    "valuation",
}
# Remaining-capacity / zoning-math field names an unused-floor-area doc must never carry.
_CAPACITY_KEYS = {
    "capacity",
    "remaining",
    "remaining_floor_area",
    "remaining_development_capacity",
    "allowance",
    "floor_area_allowance",
    "far",
    "unused_floor_area_sq_ft",
    "air_rights",
}
# Parking-OUTCOME field names a transit/parking doc must never carry.
_PARKING_OUTCOME_KEYS = {
    "parking_spaces",
    "spaces",
    "required_spaces",
    "parking_required",
    "parking_outcome",
    "waiver",
    "exemption",
    "parking_ratio",
}


@pytest.mark.parametrize("path", _valid_paths("parity_data"))
def test_parity_data_is_not_a_valuation_and_has_no_derived_price(path: Path) -> None:
    document = _load(path)
    keys = {key.lower() for key in _iter_keys(document)}
    assert not (keys & _VALUATION_KEYS), sorted(keys & _VALUATION_KEYS)
    comparable_sales = document["comparable_sales"]
    assert comparable_sales["not_a_valuation"].startswith(
        "These are recorded sales selected by a simple, disclosed filter, not a valuation"
    )


@pytest.mark.parametrize("path", _valid_paths("parity_data"))
def test_unused_floor_area_reads_only_not_confirmed_with_no_capacity_number(path: Path) -> None:
    unused = _load(path)["unused_floor_area"]
    assert unused["status"] == "not_confirmed"
    assert unused["label"] == "Remaining development capacity: Not confirmed"
    assert unused["reason"] == (
        "Needs verified zoning-lot boundaries and existing zoning floor area."
    )
    keys = {key.lower() for key in _iter_keys(unused)}
    assert not (keys & _CAPACITY_KEYS), sorted(keys & _CAPACITY_KEYS)


@pytest.mark.parametrize("path", _valid_paths("transit_parking"))
def test_transit_parking_carries_the_zone_only_never_a_parking_outcome(path: Path) -> None:
    keys = {key.lower() for key in _iter_keys(_load(path))}
    assert not (keys & _PARKING_OUTCOME_KEYS), sorted(keys & _PARKING_OUTCOME_KEYS)


@pytest.mark.parametrize(
    "stem", ["hidden_issue_flags", "transit_parking", "parity_data"]
)
def test_no_w0_fixture_claims_a_verified_or_combined_zoning_lot(stem: str) -> None:
    banned = ("verified zoning lot", "zoning lot is verified", "combined zoning lot is verified")
    for path in _valid_paths(stem):
        for text in _iter_strings(_load(path)):
            lowered = text.lower()
            for phrase in banned:
                assert phrase not in lowered, f"{path.name}: claims {phrase!r}"


def test_zoning_lot_history_flags_are_flag_or_check_needed_only() -> None:
    for path in _valid_paths("hidden_issue_flags"):
        for group in _load(path)["groups"]:
            if group["group_id"] != "zoning_lot_history":
                continue
            for flag in group["flags"]:
                assert flag["status"] in ("flag", "check_needed"), flag["status"]


# ---- real module output validates against the canonical schema -----------------------------
# The schema must admit the ACTUAL serialized output of the modules it wraps, including the
# engine-provenance evidence source and the DOF-shaped comparable-sales provenance that the
# synthetic fixtures alone would not exercise (PR #319 review, blocking item 1 + note A).

_BBL = "1000010100"
_AT = "2026-09-30T12:00:00Z"
# Engine-result provenance, verbatim from test_hidden_issue_flags.py.
_ALLOWANCE_SOURCE = {"kind": "rule_evaluation", "statement": "R6B as-of-right, rule v1"}


def _efa(value: int, bbl: str = _BBL):
    return resolve_existing_zoning_floor_area(
        bbl,
        ExistingFloorAreaEvidence(
            assumption=StatedAssumption(value, "architect's stated assumption", _AT)
        ),
    )


def test_real_existing_building_group_with_engine_allowance_validates() -> None:
    """existing_building_group(... as_of_right_allowance=AsOfRightAllowance(...)) puts the
    ENGINE allowance provenance in a flag's evidence source; the schema must admit it."""
    group = existing_building_group(
        _BBL,
        existing_floor_area=_efa(40000),
        as_of_right_allowance=AsOfRightAllowance(10000, _ALLOWANCE_SOURCE),
    )
    document = {"contract_version": "1.0.0", "groups": [group.to_dict()]}
    validate_hidden_issue_flags_document(document)  # raises on any defect
    larger = document["groups"][0]["flags"][0]
    assert larger["status"] == "flag"
    # The engine-provenance source is carried verbatim and is NOT a site_fact source.
    assert larger["evidence"][-1]["source"] == _ALLOWANCE_SOURCE
    assert larger["evidence"][-1]["source"]["kind"] == "rule_evaluation"


def _routed_transport(url: str, file: str):
    body = (DOF_PACK / file).read_text(encoding="utf-8")
    response = TransportResponse(200, body, {"x-soda2-truth-last-modified": "2026-09-01"})

    def transport(requested: str, headers: dict, timeout: float) -> TransportResponse:
        assert requested == url, (requested, url)
        return response

    return transport


def _fixed_clock() -> datetime:
    return datetime(2026, 10, 2, 11, 0, 0, tzinfo=UTC)


def _sale_to_dict(record) -> dict:
    """Minimal serializer (W4 builds the real one): SaleRecord -> comparable_sale.
    SaleRecord.source (the DOF provenance) is carried VERBATIM, never re-shaped."""
    return {
        "bbl": record.bbl, "borough": record.borough, "neighborhood": record.neighborhood,
        "block": record.block, "lot": record.lot, "address": record.address,
        "zip_code": record.zip_code, "building_class_category": record.building_class_category,
        "building_class_at_time_of_sale": record.building_class_at_time_of_sale,
        "residential_units": record.residential_units,
        "commercial_units": record.commercial_units, "total_units": record.total_units,
        "year_built": record.year_built, "land_square_feet": record.land_square_feet,
        "gross_square_feet": record.gross_square_feet, "sale_price": record.sale_price,
        "sale_date": record.sale_date, "source": record.source,
    }


def test_real_dof_comparable_sales_validate_with_dof_source() -> None:
    """A real ComparableSalesResult built from the recorded DOF Bayside fixture, serialized
    by a minimal mapping, validates - its DOF-shaped source (SaleRecord.source) is admitted
    without losing provenance (note A)."""
    subject = fetch_sales_by_bbl(
        "4073340070",
        transport=_routed_transport(
            build_by_bbl_url("4073340070", row_limit=50),
            "dof_sales_w2pb-icbu_bbl_4073340070.json",
        ),
        row_limit=50, clock=_fixed_clock, correlation_id="c",
    ).records[0]
    candidates = fetch_comparable_candidates(
        "BAYSIDE", "22 STORE BUILDINGS",
        transport=_routed_transport(
            build_candidates_url("BAYSIDE", "22 STORE BUILDINGS", row_limit=12),
            "dof_sales_w2pb-icbu_bayside_22_store_buildings.json",
        ),
        row_limit=12, clock=_fixed_clock, correlation_id="c",
    ).records
    result = select_comparables(subject_spec_from_record(subject), candidates)
    assert result.selected, "fixture should yield at least one comparable"

    comparable_sales = {
        "subject": {
            "bbl": result.subject.bbl,
            "building_class_category": result.subject.building_class_category,
            "gross_square_feet": result.subject.gross_square_feet,
        },
        "criteria": {
            "size_tolerance_fraction": result.criteria.size_tolerance_fraction,
            "exclude_zero_price": result.criteria.exclude_zero_price,
            "require_recorded_size": result.criteria.require_recorded_size,
        },
        "criteria_text": result.criteria_text,
        "not_a_valuation": result.not_a_valuation,
        "selected": [_sale_to_dict(record) for record in result.selected],
        "excluded": list(result.excluded),
        "source": result.source,
    }
    unused = unused_floor_area_data(_efa(50000, bbl="4073340070")).to_dict()
    document = {
        "contract_version": "1.0.0",
        "comparable_sales": comparable_sales,
        "unused_floor_area": unused,
    }
    validate_parity_data_document(document)  # raises on any defect
    # The real DOF source carries the connector's own provenance shape, not site_fact's.
    dof_source = comparable_sales["selected"][0]["source"]
    assert dof_source["kind"] == "city_dataset"
    assert set(dof_source) == {
        "kind", "source_id", "dataset_id", "dataset",
        "request_url", "retrieved_at", "dataset_last_modified",
    }
