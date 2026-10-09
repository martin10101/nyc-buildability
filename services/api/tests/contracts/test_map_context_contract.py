"""Contract tests for map_context v1 (maps connection step 2, D-090-R124).

The map_context document is the ONE input the E-07 location and zoning map
renderers consume (app.drawings.maps.adapter.load_map_context). This suite
proves the schema and the adapter AGREE:

* every valid fixture validates against the canonical schema AND loads through
  the adapter into a MapContext;
* every invalid fixture is rejected by BOTH - the schema at the stated path and
  the adapter with the stated code/location (an open ring the schema catches by
  its >= 4-point rule and the adapter by its explicit closure check);
* the schema's pinned constants (CRS, caps, coordinate bounds) are imported
  read-only from the adapter and compared, so the two can never drift.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    STUDY_CONTRACT_STEMS,
    StudyContractError,
    validate_map_context_document,
)
from app.drawings.maps.adapter import (
    MAX_ABS_COORD_FT,
    MAX_MAP_FEATURES,
    MAX_RING_POINTS,
    SUPPORTED_CRS,
    load_map_context,
)
from app.drawings.maps.errors import MapInputError
from app.drawings.maps.model import MapContext

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "packages/contracts/schemas/v1/map_context.schema.json"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
VALID_DIR = FIXTURE_ROOT / "valid" / "map_context"
INVALID_DIR = FIXTURE_ROOT / "invalid" / "map_context"

VALID = sorted(VALID_DIR.glob("*.json"))
INVALID = sorted(INVALID_DIR.glob("*.json"))


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema() -> dict:
    return _load(SCHEMA_PATH)


def test_stem_registered() -> None:
    assert "map_context" in STUDY_CONTRACT_STEMS


def test_fixtures_present() -> None:
    """Guard against a vacuous pass: the four E-07 shapes and the three named
    single-defect invalid fixtures."""
    assert len(VALID) == 4, [p.name for p in VALID]
    assert {p.name for p in INVALID} == {
        "wrong_crs.json",
        "open_ring.json",
        "missing_use_limitation.json",
    }


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_fixture_passes_schema_and_adapter(path: Path) -> None:
    doc = _load(path)
    validate_map_context_document(doc)  # schema validator: no raise
    result = load_map_context(doc)  # the adapter agrees
    assert isinstance(result, MapContext)
    assert result.crs == SUPPORTED_CRS


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.name)
def test_invalid_fixture_fails_schema_on_its_stated_defect(path: Path) -> None:
    doc = _load(path)
    # Repo convention: an invalid fixture carries a string _expected_failure;
    # strip it so the rejection is the stated defect, not the annotation guard.
    assert isinstance(doc.pop(FIXTURE_ONLY_KEY, None), str), "annotation missing"
    with pytest.raises(StudyContractError) as exc:
        validate_map_context_document(doc)
    assert "failed canonical schema validation" in str(exc.value)
    assert exc.value.contract == "map_context"


def test_wrong_crs_fails_adapter_at_crs() -> None:
    with pytest.raises(MapInputError) as exc:
        load_map_context(_load(INVALID_DIR / "wrong_crs.json"))
    assert exc.value.code == "unsupported_crs"
    assert exc.value.location == "/map_context/crs"


def test_open_ring_fails_adapter_at_the_ring() -> None:
    with pytest.raises(MapInputError) as exc:
        load_map_context(_load(INVALID_DIR / "open_ring.json"))
    assert exc.value.code == "ring_not_closed"
    assert exc.value.location == "/map_context/subject_lot/outline/0"


def test_missing_use_limitation_fails_adapter_building_the_zoning_layer() -> None:
    with pytest.raises(KeyError) as exc:
        load_map_context(_load(INVALID_DIR / "missing_use_limitation.json"))
    assert "use_limitation" in str(exc.value)


# --- the schema's constants must equal the adapter's, so they cannot drift ----


def test_crs_const_matches_adapter() -> None:
    crs = _schema()["$defs"]["map_context"]["properties"]["crs"]
    assert crs["const"] == SUPPORTED_CRS


def test_document_kind_and_version_are_pinned() -> None:
    props = _schema()["properties"]
    assert props["document_kind"]["const"] == "map_context"
    assert props["contract_version"]["enum"] == ["1.0.0"]


def test_entry_cap_matches_adapter_max_map_features() -> None:
    defs = _schema()["$defs"]
    assert defs["zoning_available"]["properties"]["entries"]["maxItems"] == MAX_MAP_FEATURES
    assert defs["buildings_available"]["properties"]["entries"]["maxItems"] == MAX_MAP_FEATURES


def test_ring_cap_matches_adapter_max_ring_points() -> None:
    assert _schema()["$defs"]["ring"]["maxItems"] == MAX_RING_POINTS


def test_coordinate_bounds_match_adapter_max_abs_coord() -> None:
    point = _schema()["$defs"]["point"]["items"]
    assert point["maximum"] == MAX_ABS_COORD_FT
    assert point["minimum"] == -MAX_ABS_COORD_FT
