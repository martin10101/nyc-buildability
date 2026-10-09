"""Scope-disclosure statements must FOLLOW the actual values they describe (D-090-R156,
extends DB-126).

The reviewer reproduced false disclosure text: ``app.contracts.engine_disclosures``
composed the overlay, special-district, within-100-feet and special-density scope
statements WITHOUT reading the actual input value, so a schema-valid results document
could say "no overlay applies" while ``overlay_present`` is true, say no special district
while ``special_district_present`` is true, or say the lot IS within 100 feet while the
flag is false. The Northern fixture's defaults (overlay true / recorded C2-2, special
district false, within-100 true, special density false) hid it.

These tests pin the fix on the RECORDED Northern study (the live corner read with the
recorded C2-2 commercial overlay and the lot's confirmed address, exactly as the C-07
journey test builds it) plus, for the overlay assumed path, a single-frontage study with
NO recorded overlay fact. For each flag-derived row the statement must match the value;
an overlay flag contradicting the recorded fact fails closed; and the journey defaults
still emit today's exact strings.
"""

from __future__ import annotations

import pytest

from app.api.v1.study_read import get_rate_limiter
from app.contracts.engine_disclosures import EngineDisclosureError
from app.contracts.evaluator_inputs import (
    build_evaluator_inputs,
    build_three_answer_inputs,
)
from app.contracts.study_setup_bridge import study_from_study_setup
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import _OPTION_ID as _EVI_OPTION_ID
from tests.contracts.test_evaluator_inputs import (
    _benchmark_city_facts,
    _benchmark_identity_address,
    _study,
)
from tests.contracts.test_study_setup_bridge import (
    _OPTION_ID,
    _REVISION,
    _northern_setup,
)

# The C-07 journey flags (Northern read defaults): overlay present (recorded C2-2),
# no special district, within 100 ft, square corner, no special density area.
_JOURNEY_FLAGS = {
    "housing_program": "standard_residence",
    "overlay_present": True,
    "special_district_present": False,
    "within_100_ft_of_street_line_intersection": True,
    "street_line_intersection_angle_degrees": 90.0,
    "special_density_area": False,
}

# Today's exact statements for the flag-derived rows at the journey defaults. Byte-equal
# to the strings the unfixed code emitted for these values (requirement d).
_DEFAULT_SPECIAL_DISTRICT = (
    "No special purpose district is assumed to apply; this run does not read the "
    "special-district layer."
)
_DEFAULT_SPECIAL_DENSITY = (
    "The lot is assumed not to lie in a special density area; this run does not read the "
    "special-density layer."
)
_DEFAULT_WITHIN_100 = (
    "The lot is assumed to lie within 100 feet of a street-line intersection."
)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The study-read route limiter is process-wide module state; reset it around every
    test (the same pattern the study-read suites use) so route calls never spuriously 429."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _overlay_fact(study: dict) -> dict:
    facts = [f for f in study["site"]["facts"] if f["key"] == "commercial_overlay"]
    assert len(facts) == 1, facts
    return facts[0]


def _northern_journey_doc(monkeypatch) -> tuple[dict, dict]:
    """The recorded Northern study (live corner read with the confirmed address) and its
    evaluator_inputs document - exactly the C-07 journey setup, so the disclosures run on
    the real recorded C2-2 overlay and the two frontages."""
    setup = _northern_setup(monkeypatch, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(
        setup, _TEST_ONLY_OPTION, study_id="study-northern-disclosures", revision=_REVISION
    )
    doc = build_evaluator_inputs(study, _OPTION_ID)
    return study, doc


def _scope_inputs(doc: dict, study: dict, **overrides):
    """The auto-filled scope_inputs for ``doc``/``study`` with the journey flags, overriding
    any flag under test. The scope statements are what ``build_scope_inputs`` composed."""
    flags = {**_JOURNEY_FLAGS, **overrides}
    inputs = build_three_answer_inputs(
        doc,
        results_id="res-disclosures",
        computed_at="2026-10-03T00:00:00Z",
        study=study,
        **flags,
    )
    assert inputs.scope_inputs is not None
    return inputs.scope_inputs


# ---------------------------------------------------------------------------
# Every flag-derived statement follows the actual value (not fixed text)
# ---------------------------------------------------------------------------
# (field, value, must_contain, must_not_contain): a phrase unique to the value, and a
# phrase unique to the OPPOSITE value, so the statement cannot silently disagree.
_FLAG_STATEMENT_CASES = [
    (
        "special_district_present", True,
        "A special purpose district is assumed to apply", "No special purpose district",
    ),
    (
        "special_district_present", False,
        "No special purpose district is assumed to apply", "A special purpose district",
    ),
    (
        "special_density_area", True,
        "assumed to lie in a special density area", "not to lie in a special density area",
    ),
    (
        "special_density_area", False,
        "assumed not to lie in a special density area", "assumed to lie in a special density area",
    ),
    (
        "within_100_ft_of_street_line_intersection", True,
        "assumed to lie within 100 feet", "not to lie within 100 feet",
    ),
    (
        "within_100_ft_of_street_line_intersection", False,
        "assumed not to lie within 100 feet", "assumed to lie within 100 feet",
    ),
]


@pytest.mark.parametrize("field,value,must_contain,must_not_contain", _FLAG_STATEMENT_CASES)
def test_flag_statement_follows_value_on_the_recorded_northern_study(
    monkeypatch, field, value, must_contain, must_not_contain
) -> None:
    study, doc = _northern_journey_doc(monkeypatch)
    scope = _scope_inputs(doc, study, **{field: value})
    disclosure = getattr(scope, field)
    assert must_contain in disclosure.statement, (field, value, disclosure.statement)
    assert must_not_contain not in disclosure.statement, (field, value, disclosure.statement)
    assert disclosure.basis == "assumed"  # these flags read no layer


# ---------------------------------------------------------------------------
# overlay_present: statement follows the flag AND agrees with the recorded fact
# ---------------------------------------------------------------------------
def test_overlay_present_true_names_the_recorded_overlay(monkeypatch) -> None:
    study, doc = _northern_journey_doc(monkeypatch)
    overlay_fact = _overlay_fact(study)
    disclosure = _scope_inputs(doc, study, overlay_present=True).overlay_present
    assert overlay_fact["value"] in disclosure.statement  # e.g. "C2-2"
    assert "is recorded for this lot in city data" in disclosure.statement
    assert "assumed" not in disclosure.statement
    assert disclosure.basis == overlay_fact["measurement"]["rank"]  # city data, not a guess


def test_overlay_flag_contradicting_the_recorded_c2_2_fact_fails_closed(monkeypatch) -> None:
    # A recorded commercial overlay (C2-2) with overlay_present=False is a disagreement:
    # the disclosure must NOT silently say "no overlay" while the fact records one. It fails
    # closed naming the key (CLAUDE.md principle 4), never a silent override.
    study, doc = _northern_journey_doc(monkeypatch)
    assert _overlay_fact(study)["value"] == "C2-2"  # the recorded fact (sanity)
    with pytest.raises(EngineDisclosureError, match="overlay_present"):
        _scope_inputs(doc, study, overlay_present=False)


@pytest.mark.parametrize(
    "flag,must_contain,must_not_contain",
    [
        (True, "A commercial overlay is assumed to apply", "No commercial overlay"),
        (False, "No commercial overlay is assumed to apply", "A commercial overlay is assumed"),
    ],
)
def test_overlay_assumed_statement_follows_flag_without_a_recorded_fact(
    flag, must_contain, must_not_contain
) -> None:
    # No recorded commercial_overlay fact (single-frontage benchmark facts): the statement
    # follows the caller flag with basis 'assumed', so it can never disagree with the value.
    study = _study(_benchmark_city_facts())
    doc = build_evaluator_inputs(study, _EVI_OPTION_ID)
    disclosure = _scope_inputs(doc, study, overlay_present=flag).overlay_present
    assert must_contain in disclosure.statement, (flag, disclosure.statement)
    assert must_not_contain not in disclosure.statement, (flag, disclosure.statement)
    assert disclosure.basis == "assumed"


# ---------------------------------------------------------------------------
# The journey defaults still emit today's exact statements (regression guard)
# ---------------------------------------------------------------------------
def test_journey_defaults_produce_todays_exact_statements(monkeypatch) -> None:
    study, doc = _northern_journey_doc(monkeypatch)
    scope = _scope_inputs(doc, study)  # the journey flags, unchanged
    overlay_fact = _overlay_fact(study)
    assert scope.overlay_present.statement == (
        f"A commercial overlay ({overlay_fact['value']}) is recorded for this lot in city "
        "data."
    )
    assert scope.special_district_present.statement == _DEFAULT_SPECIAL_DISTRICT
    assert scope.special_density_area.statement == _DEFAULT_SPECIAL_DENSITY
    assert scope.within_100_ft_of_street_line_intersection.statement == _DEFAULT_WITHIN_100
