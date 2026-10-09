"""Server-side validation of the study contract set (task C-03, plan M1-09).

Done-when (M1-09): "Valid and invalid fixtures pass and fail". Every valid
fixture under packages/contracts/fixtures/valid/<stem>/ must pass
``validate_<stem>_document``; every invalid fixture under invalid/<stem>/ must
be rejected BY THE SCHEMA - its fixture-only ``_expected_failure`` annotation is
stripped first, so the rejection is the fixture's stated defect and not the
producer guard against the annotation itself.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.contracts import study_contracts
from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    STUDY_CONTRACT_STEMS,
    StudyContractError,
    validate_results_document,
    validate_site_fact_document,
    validate_study_contract_document,
    validate_study_document,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
BUNDLE_DIR = REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"


def _fixtures(kind: str) -> list[tuple[str, Path]]:
    return [
        (stem, path)
        for stem in STUDY_CONTRACT_STEMS
        for path in sorted((FIXTURE_ROOT / kind / stem).glob("*.json"))
    ]


VALID = _fixtures("valid")
INVALID = _fixtures("invalid")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture_id(item: tuple[str, Path]) -> str:
    return f"{item[0]}/{item[1].name}"


def test_every_stem_has_valid_and_invalid_fixtures() -> None:
    """Guard against a vacuous pass: each stem has at least one fixture of
    each kind (the three named in the queue row among them)."""
    for stem in STUDY_CONTRACT_STEMS:
        assert any(s == stem for s, _ in VALID), f"no valid fixture for {stem}"
        assert any(s == stem for s, _ in INVALID), f"no invalid fixture for {stem}"


@pytest.mark.parametrize("item", VALID, ids=_fixture_id)
def test_valid_fixture_passes(item: tuple[str, Path]) -> None:
    stem, path = item
    validate_study_contract_document(stem, _load(path))


@pytest.mark.parametrize("item", INVALID, ids=_fixture_id)
def test_invalid_fixture_fails_on_its_stated_defect(item: tuple[str, Path]) -> None:
    stem, path = item
    document = _load(path)
    assert isinstance(document.pop(FIXTURE_ONLY_KEY, None), str), "annotation missing"
    with pytest.raises(StudyContractError) as excinfo:
        validate_study_contract_document(stem, document)
    assert "failed canonical schema validation" in str(excinfo.value)
    assert excinfo.value.contract == stem


@pytest.mark.parametrize(
    ("stem", "validate"),
    [
        ("site_fact", validate_site_fact_document),
        ("study", validate_study_document),
        ("results", validate_results_document),
    ],
)
def test_named_validators_accept_valid_and_reject_invalid(stem, validate) -> None:
    for path in sorted((FIXTURE_ROOT / "valid" / stem).glob("*.json")):
        validate(_load(path))
    for path in sorted((FIXTURE_ROOT / "invalid" / stem).glob("*.json")):
        document = _load(path)
        document.pop(FIXTURE_ONLY_KEY)
        with pytest.raises(StudyContractError):
            validate(document)


def test_every_stem_has_a_named_validator() -> None:
    for stem in STUDY_CONTRACT_STEMS:
        assert callable(getattr(study_contracts, f"validate_{stem}_document"))


def _first_valid(stem: str) -> dict:
    return _load(sorted((FIXTURE_ROOT / "valid" / stem).glob("*.json"))[0])


def test_fixture_only_annotation_is_rejected_at_the_root() -> None:
    document = _first_valid("site_fact")
    document[FIXTURE_ONLY_KEY] = "leaked"
    with pytest.raises(StudyContractError, match="fixture-only") as excinfo:
        validate_site_fact_document(document)
    assert excinfo.value.location == FIXTURE_ONLY_KEY


def test_fixture_only_annotation_is_rejected_when_nested() -> None:
    document = _first_valid("study")
    document["site"]["facts"][0][FIXTURE_ONLY_KEY] = "leaked"
    with pytest.raises(StudyContractError, match="fixture-only") as excinfo:
        validate_study_document(document)
    assert excinfo.value.location == f"site/facts/0/{FIXTURE_ONLY_KEY}"


def test_non_strict_json_is_rejected() -> None:
    document = _first_valid("results")
    document["notices_count"] = float("nan")
    with pytest.raises(StudyContractError, match="strict-JSON"):
        validate_results_document(document)


def test_unknown_encoded_as_zero_is_rejected() -> None:
    """Plan section 9: an unknown is never 0. A known lot area of 0 fails."""
    document = next(
        _load(p) for p in sorted((FIXTURE_ROOT / "valid" / "site_fact").glob("*.json"))
        if _load(p)["key"] == "lot_area" and _load(p)["value"] is not None
    )
    document["value"] = 0
    with pytest.raises(StudyContractError, match="failed canonical schema validation"):
        validate_site_fact_document(document)


def test_non_object_and_unknown_stem_fail_closed() -> None:
    with pytest.raises(StudyContractError, match="must be a JSON object"):
        validate_study_document([])
    with pytest.raises(ValueError, match="unknown study contract"):
        validate_study_contract_document("scenario", {})


def test_validation_does_not_mutate_the_document() -> None:
    document = _first_valid("study")
    before = copy.deepcopy(document)
    validate_study_document(document)
    assert document == before


@pytest.mark.parametrize("stem", STUDY_CONTRACT_STEMS)
def test_bundled_schema_is_byte_identical_to_canonical(stem: str) -> None:
    name = f"{stem}.schema.json"
    assert (BUNDLE_DIR / name).read_bytes() == (SCHEMA_DIR / name).read_bytes(), (
        f"services/api/app/_contract_schemas/v1/{name} is out of sync; run "
        "python services/api/scripts/sync_contract_schemas.py and commit."
    )


def test_schema_error_message_is_bounded() -> None:
    """A root-level oneOf failure reprs the whole document; the raised message
    stays bounded so a large document is never dumped into a log line."""
    path = FIXTURE_ROOT / "invalid" / "results" / "draft_false_with_unreviewed_rules.json"
    document = _load(path)
    document.pop(FIXTURE_ONLY_KEY)
    with pytest.raises(StudyContractError) as excinfo:
        validate_results_document(document)
    assert excinfo.value.location == "<root>"
    assert len(str(excinfo.value)) < 400
