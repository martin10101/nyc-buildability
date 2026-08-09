"""Deterministic tests for the tax-lot (MapPLUTO) reference cross-checks
(M2-T015 SB-S4): :mod:`app.documents.crosscheck`.

Covers, per cross-check: one PASS, one FAIL carrying the exact verbatim compared
values, and every UNEVALUABLE refusal condition — plus the structural doctrine tests:
the reference model is frozen and fully required (mutation raises; no field is ever
defaulted) and the crosscheck module imports no state/storage machinery (asserted by
module attribute inspection), so there is deliberately no code path that could write
survey state. A discrepancy is a visible typed FAIL routed to professional review; it
never mutates, corrects, replaces, or suppresses a survey fact.
"""

from __future__ import annotations

import dataclasses
import types

import pytest

import app.documents.crosscheck as crosscheck
from app.documents.checks import CheckFailed, CheckPassed, CheckUnevaluable
from app.documents.crosscheck import (
    TaxLotReference,
    tax_lot_area_crosscheck,
    tax_lot_bbl_crosscheck,
)
from app.documents.taxonomy import SurveyFactType
from app.documents.units import AreaUnit, ValidatedArea, ValidatedUnitlessText

_REFERENCE_FIELDS = {
    "bbl": "1000470001",
    "lot_area_square_feet": 2500.0,
    "source_dataset": "mappluto",
    "source_version": "24v4",
    "retrieved_at": "2026-08-01T00:00:00Z",
}


def _reference(**overrides: object) -> TaxLotReference:
    fields = dict(_REFERENCE_FIELDS)
    fields.update(overrides)
    return TaxLotReference(**fields)


def _bbl_fact(text: str = "1000470001") -> ValidatedUnitlessText:
    return ValidatedUnitlessText(fact_type=SurveyFactType.BBL_TEXT, text=text)


def _area_fact(
    value: float = 2500.0,
    unit: AreaUnit = AreaUnit.SQUARE_FEET,
    fact_type: SurveyFactType = SurveyFactType.STATED_LOT_AREA,
) -> ValidatedArea:
    return ValidatedArea(fact_type=fact_type, value=value, unit=unit)


# ------------------------------------------------------------ tax_lot_bbl_crosscheck


def test_tax_lot_bbl_crosscheck_passes_on_exact_string_equality():
    result = tax_lot_bbl_crosscheck(_bbl_fact("1000470001"), _reference())
    assert isinstance(result, CheckPassed)
    assert result.check_name == "tax_lot_bbl_crosscheck"
    assert result.unit is None
    assert result.tolerance == 0
    assert result.computed["compared_fact_count"] == 1
    assert result.computed["mismatched_fact_count"] == 0
    assert result.computed["bbl.survey_fact[1000470001]"] == 1
    assert result.computed["bbl.tax_lot_reference[1000470001]"] == 1


def test_tax_lot_bbl_crosscheck_fails_on_mismatch_carrying_both_verbatim():
    survey = _bbl_fact("1000470001")
    reference = _reference(bbl="1000470002")
    result = tax_lot_bbl_crosscheck(survey, reference)
    assert isinstance(result, CheckFailed)
    assert result.check_name == "tax_lot_bbl_crosscheck"
    assert result.computed["bbl.survey_fact[1000470001]"] == 0
    assert result.computed["bbl.tax_lot_reference[1000470002]"] == 0
    assert result.computed["mismatched_fact_count"] == 1
    assert result.promotable is False
    # doctrine: the discrepancy routes to review; neither input was mutated,
    # corrected, replaced, or suppressed
    assert survey == _bbl_fact("1000470001")
    assert reference == _reference(bbl="1000470002")


def test_tax_lot_bbl_crosscheck_unevaluable_on_unresolved_survey_input():
    result = tax_lot_bbl_crosscheck("1000470001", _reference())  # type: ignore[arg-type]
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "tax_lot_bbl_crosscheck"
    assert "resolved ValidatedUnitlessText" in result.reason


def test_tax_lot_bbl_crosscheck_unevaluable_on_wrong_fact_type():
    address = ValidatedUnitlessText(
        fact_type=SurveyFactType.ADDRESS_TEXT, text="1000470001"
    )
    result = tax_lot_bbl_crosscheck(address, _reference())
    assert isinstance(result, CheckUnevaluable)
    assert "never re-labeled" in result.reason


# ----------------------------------------------------------- tax_lot_area_crosscheck


def test_tax_lot_area_crosscheck_passes_within_tolerance():
    result = tax_lot_area_crosscheck(
        _area_fact(value=2500.0),
        _reference(lot_area_square_feet=2512.5),
        tolerance=12.5,
    )
    assert isinstance(result, CheckPassed)
    assert result.check_name == "tax_lot_area_crosscheck"
    assert result.unit == "square_feet"
    assert result.tolerance == 12.5
    assert result.computed["survey_area"] == 2500.0
    assert result.computed["tax_lot_reference_area"] == 2512.5
    assert result.computed["difference"] == -12.5


def test_tax_lot_area_crosscheck_accepts_calculated_lot_area_at_zero_tolerance():
    result = tax_lot_area_crosscheck(
        _area_fact(fact_type=SurveyFactType.CALCULATED_LOT_AREA),
        _reference(),
        tolerance=0,
    )
    assert isinstance(result, CheckPassed)


def test_tax_lot_area_crosscheck_fails_beyond_tolerance_carrying_verbatim_values():
    survey = _area_fact(value=2500.0)
    reference = _reference(lot_area_square_feet=2612.5)
    result = tax_lot_area_crosscheck(survey, reference, tolerance=5)
    assert isinstance(result, CheckFailed)
    assert result.check_name == "tax_lot_area_crosscheck"
    assert result.unit == "square_feet"
    assert result.tolerance == 5
    assert result.computed["survey_area"] == 2500.0
    assert result.computed["tax_lot_reference_area"] == 2612.5
    assert result.computed["difference"] == -112.5
    assert result.promotable is False
    # doctrine: the discrepancy routes to review; the survey fact is untouched
    assert survey == _area_fact(value=2500.0)
    assert reference == _reference(lot_area_square_feet=2612.5)


def test_tax_lot_area_crosscheck_unevaluable_on_acres_never_converted():
    result = tax_lot_area_crosscheck(
        _area_fact(value=0.25, unit=AreaUnit.ACRES), _reference(), tolerance=1.0
    )
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "tax_lot_area_crosscheck"
    assert "never converted" in result.reason


def test_tax_lot_area_crosscheck_unevaluable_on_unresolved_survey_input():
    result = tax_lot_area_crosscheck(2500.0, _reference(), tolerance=1.0)  # type: ignore[arg-type]
    assert isinstance(result, CheckUnevaluable)
    assert "resolved ValidatedArea" in result.reason


def test_tax_lot_area_crosscheck_unevaluable_on_non_lot_area_fact_type():
    elevation_labeled = ValidatedArea(
        fact_type=SurveyFactType.ELEVATION_VALUE,
        value=2500.0,
        unit=AreaUnit.SQUARE_FEET,
    )
    result = tax_lot_area_crosscheck(elevation_labeled, _reference(), tolerance=1.0)
    assert isinstance(result, CheckUnevaluable)
    assert "never re-labeled" in result.reason


@pytest.mark.parametrize(
    "tolerance",
    ["12.5", True, float("inf"), float("nan"), -1],
    ids=["string", "bool", "infinite", "nan", "negative"],
)
def test_tax_lot_area_crosscheck_unevaluable_on_unusable_tolerance(tolerance):
    result = tax_lot_area_crosscheck(_area_fact(), _reference(), tolerance=tolerance)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "tax_lot_area_crosscheck"


# ------------------------------------------- shared reference-field refusal coverage

_REFERENCE_DEFECTS = [
    pytest.param(dict(_REFERENCE_FIELDS), id="not-a-TaxLotReference"),
    pytest.param(_reference(bbl="12345"), id="malformed-bbl"),
    pytest.param(_reference(bbl=1000470001), id="non-string-bbl"),
    pytest.param(_reference(lot_area_square_feet="2500"), id="non-numeric-lot-area"),
    pytest.param(_reference(lot_area_square_feet=True), id="boolean-lot-area"),
    pytest.param(
        _reference(lot_area_square_feet=float("inf")), id="non-finite-lot-area"
    ),
    pytest.param(_reference(lot_area_square_feet=float("nan")), id="nan-lot-area"),
    pytest.param(_reference(lot_area_square_feet=0), id="non-positive-lot-area"),
    pytest.param(_reference(source_dataset="   "), id="blank-source-dataset"),
    pytest.param(_reference(source_version=None), id="missing-source-version"),
    pytest.param(_reference(retrieved_at=""), id="empty-retrieved-at"),
]


@pytest.mark.parametrize("reference", _REFERENCE_DEFECTS)
def test_tax_lot_bbl_crosscheck_unevaluable_on_unusable_reference(reference):
    result = tax_lot_bbl_crosscheck(_bbl_fact(), reference)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "tax_lot_bbl_crosscheck"


@pytest.mark.parametrize("reference", _REFERENCE_DEFECTS)
def test_tax_lot_area_crosscheck_unevaluable_on_unusable_reference(reference):
    result = tax_lot_area_crosscheck(_area_fact(), reference, tolerance=1.0)
    assert isinstance(result, CheckUnevaluable)
    assert result.check_name == "tax_lot_area_crosscheck"


# ------------------------------------------------------------- structural doctrine


def test_tax_lot_reference_is_frozen_mutation_raises():
    reference = _reference()
    with pytest.raises(dataclasses.FrozenInstanceError):
        reference.bbl = "5000010001"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        reference.lot_area_square_feet = 1.0  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        del reference.source_dataset  # type: ignore[misc]


@pytest.mark.parametrize("omitted", sorted(_REFERENCE_FIELDS))
def test_tax_lot_reference_requires_every_field_never_defaulted(omitted):
    fields = dict(_REFERENCE_FIELDS)
    del fields[omitted]
    with pytest.raises(TypeError):
        TaxLotReference(**fields)


def test_crosscheck_module_imports_write_nothing():
    """Structural doctrine: the crosscheck module has no code path that writes survey
    state — it imports no state, storage, session, repository, or database machinery.
    Asserted by inspecting the module's attributes, not by convention.
    """
    imported_modules = {
        name
        for name, value in vars(crosscheck).items()
        if isinstance(value, types.ModuleType)
    }
    assert imported_modules <= {"math"}, imported_modules

    allowed_origins = {
        "__future__",
        "app.documents.checks",
        "app.documents.crosscheck",
        "app.documents.models",
        "app.documents.taxonomy",
        "app.documents.units",
        "builtins",
        "dataclasses",
        "re",
        "types",
        "typing",
    }
    forbidden_markers = (
        "sqlalchemy",
        "psycopg",
        "supabase",
        "postgres",
        "sqlite",
        "redis",
        "boto",
        "httpx",
        "requests",
        "storage",
        "repository",
        "session",
        "database",
    )
    for name, value in vars(crosscheck).items():
        if name.startswith("__") or isinstance(value, types.ModuleType):
            continue
        origin = getattr(value, "__module__", None)
        if origin is not None:
            assert origin in allowed_origins, (name, origin)
        haystack = f"{name} {origin}".lower()
        assert not any(marker in haystack for marker in forbidden_markers), (
            name,
            origin,
        )
