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
from pathlib import Path
from typing import Any

import pytest

from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    StudyContractError,
    validate_hidden_issue_flags_document,
    validate_parity_data_document,
    validate_transit_parking_document,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"

W0_VALIDATORS = {
    "hidden_issue_flags": validate_hidden_issue_flags_document,
    "transit_parking": validate_transit_parking_document,
    "parity_data": validate_parity_data_document,
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
