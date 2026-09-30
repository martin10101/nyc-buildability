"""A-03 acceptance pack: the C1 unused-floor-area section with the legacy
subtraction SET ASIDE (plan section 3 step 4, section 8, M2-07; check C-3;
set-aside list item 6).

"Existing floor area is never taken from DOF building area" (M2-07). By DEFAULT
(the ``INTERNAL_LEGACY_UNUSED_FLOOR_AREA_ENABLED`` flag absent, empty or unknown)
the section says "Not available - needs existing zoning floor area" with a
machine-readable reason, the draft allowance still shows, nothing is subtracted,
and no over-built / professional-review outcome is derived from the recorded
(DOF/PLUTO) building area. The recorded building area rides only as a
reference-only assumption record, never subtracted. The legacy behavior itself is
pinned (flag on) in ``test_unused_floor_area.py``; the contrast tests here prove
each default-off assertion would move if the flag were on.

Offline and deterministic; every number is derived from the fixture cap.
"""

from __future__ import annotations

import copy
import json
import re

import pytest

from app.scenario import (
    INTERNAL_LEGACY_UNUSED_FLOOR_AREA_ENABLED_ENV_VAR as FLAG,
)
from app.scenario import (
    UNUSED_FLOOR_AREA_LABEL,
    UNUSED_FLOOR_AREA_NOT_AVAILABLE_LABEL,
    build_scenario,
    build_unused_floor_area_section,
    legacy_unused_floor_area_enabled,
    validate_scenario_document,
)
from app.scenario import (
    UnusedFloorAreaNotComputableReason as Reason,
)
from app.scenario import (
    UnusedFloorAreaState as State,
)
from app.scenario import constants as C

from . import _support as S

PROV_ID = "prov-bldgarea"
SOURCE_ID = "nyc-dcp-mappluto-arcgis"
# The plan's own words (plan section 3 step 4), retyped here on purpose so a
# drift in the constant is caught.
NOT_AVAILABLE = "Not available — needs existing zoning floor area"
REASON_CODE = "needs_existing_zoning_floor_area"
BASIS_KEY = "unused_floor_area_not_available"
REFERENCE_KEY = "recorded_building_area_reference"

NO_CAP_FACTORIES = [
    S.unsupported_rule_evaluation,
    S.not_applicable_rule_evaluation,
    S.conflict_rule_evaluation,
    S.professional_review_rule_evaluation,
    S.missing_lot_area_rule_evaluation,
    S.integrity_disagreement_rule_evaluation,
]


@pytest.fixture(autouse=True)
def _flag_absent(monkeypatch):
    """The DEFAULT: the set-aside flag is absent from the environment."""
    monkeypatch.delenv(FLAG, raising=False)


def _profile(
    value,
    *,
    coverage_status: str = "conditional",
    units: str | None = "square_feet",
    with_fact: bool = True,
    with_provenance: bool = True,
    numbldgs: dict | None = None,
) -> dict:
    """The shared minimal profile plus an existing_building_facts.bldgarea fact whose
    provenance_ref resolves against the root provenance[] array (same shape as the
    legacy pack's helper)."""
    prof = S.profile()
    facts: dict = {}
    if with_fact:
        fact = {"value": value, "provenance_ref": PROV_ID, "coverage_status": coverage_status}
        if units is not None:
            fact["units"] = units
        facts["bldgarea"] = fact
    if numbldgs is not None:
        facts["numbldgs"] = numbldgs
    if facts:
        prof["existing_building_facts"] = facts
    if with_provenance:
        prof["provenance"].append(
            {
                "provenance_id": PROV_ID,
                "source_id": SOURCE_ID,
                "dataset_version": "26v1",
                "original_field_name": "bldgarea",
                "effective_date": None,
            }
        )
    return prof


def _section(document: dict) -> dict:
    return document["unused_draft_zoning_floor_area"]


def _numbers(node):
    """Every numeric leaf (bool excluded) anywhere under ``node``."""
    if isinstance(node, bool):
        return
    if isinstance(node, int | float):
        yield float(node)
    elif isinstance(node, dict):
        for child in node.values():
            yield from _numbers(child)
    elif isinstance(node, list):
        for child in node:
            yield from _numbers(child)


def _assumption_keys(section: dict) -> list[str]:
    return [a["key"] for a in section["assumptions"]]


# ---------------------------------------------------------------------------
# The flag reader is fail-safe: absent / empty / unknown -> OFF.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "env",
    [
        {},
        {FLAG: ""},
        {FLAG: " "},
        {FLAG: "0"},
        {FLAG: "false"},
        {FLAG: "off"},
        {FLAG: "no"},
        {FLAG: "enabled"},
        {FLAG: "2"},
        {FLAG: "legacy"},
        {FLAG: 1},  # a non-string value never enables
        {"INTERNAL_LEGACY_UNUSED_FLOOR_AREA": "1"},  # a near-miss name
    ],
)
def test_flag_reader_is_off_unless_explicit_true_token(env):
    assert legacy_unused_floor_area_enabled(env) is False


@pytest.mark.parametrize("token", ["1", "true", "TRUE", " yes ", "On"])
def test_flag_reader_accepts_only_the_closed_true_tokens(token):
    assert legacy_unused_floor_area_enabled({FLAG: token}) is True


def test_flag_reader_defaults_to_process_env_and_is_off_when_absent(monkeypatch):
    assert legacy_unused_floor_area_enabled() is False
    monkeypatch.setenv(FLAG, "1")
    assert legacy_unused_floor_area_enabled() is True


# ---------------------------------------------------------------------------
# Default: "Not available - needs existing zoning floor area"; allowance shows.
# ---------------------------------------------------------------------------


def test_default_is_not_available_with_machine_readable_reason_and_allowance_shows():
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap - 1234.5
    document = build_scenario(_profile(bldgarea), rule_evaluation)
    validate_scenario_document(document)

    # The draft allowance still shows, unchanged, at the document root.
    assert document["scenario_kind"] == "preliminary"
    assert document["draft_zoning_floor_area_cap_sq_ft"] == cap

    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None
    assert section["unit"] is None
    assert section["formula"] is None
    assert section["over_built_statement"] is None
    assert section["professional_review_required"] is False
    # Closest valid typed reason in the closed contract enum.
    assert section["not_computable_reason"] == Reason.MISSING_EXISTING_BUILDING_AREA.value

    # The plan's wording, verbatim, on the section label.
    assert section["label"] == UNUSED_FLOOR_AREA_NOT_AVAILABLE_LABEL
    assert NOT_AVAILABLE in section["label"]
    assert C.UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT == NOT_AVAILABLE
    assert section["scope_note"] == C.UNUSED_FLOOR_AREA_NOT_AVAILABLE_SCOPE_NOTE
    assert "never subtracted" in section["scope_note"]

    # The allowance is echoed verbatim with its provenance under inputs.
    cap_input = section["inputs"]["draft_zoning_floor_area_cap"]
    assert cap_input == {
        "value_sq_ft": cap,
        "unit": "square_feet",
        "provenance": document["cap_provenance"],
    }
    # The existing ZONING floor area has no source: the input is all-null (the
    # recorded building area is NOT placed here).
    assert section["inputs"]["existing_building_floor_area"] == {
        "value_sq_ft": None,
        "unit": None,
        "coverage_status": None,
        "provenance_ref": None,
        "provenance": None,
    }

    # Machine-readable reason token rides as the first assumption record.
    basis = section["assumptions"][0]
    assert basis == C.unused_floor_area_not_available_assumption()
    assert basis["key"] == BASIS_KEY
    assert basis["value"] == REASON_CODE == C.UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON_CODE
    assert basis["assumption_type"] == "not_computable_basis"
    assert NOT_AVAILABLE in basis["rationale"]

    # No legacy-only record (the ZR 12-10 zoning-lot assumption is only asserted
    # when a value is computed).
    assert "zoning_lot_extent" not in _assumption_keys(section)
    assert document["professional_review_required"] is False


def test_default_carries_recorded_building_area_for_reference_only():
    rule_evaluation = S.canonical_rule_evaluation()
    bldgarea = S.trace_cap(rule_evaluation) - 1234.5
    section = _section(build_scenario(_profile(bldgarea), rule_evaluation))

    assert _assumption_keys(section) == [BASIS_KEY, REFERENCE_KEY]
    reference = section["assumptions"][1]
    assert set(reference) == {"key", "assumption_type", "value", "unit", "rationale"}
    assert reference["assumption_type"] == "reference_only_not_zoning_floor_area"
    assert reference["value"] == bldgarea
    assert reference["unit"] == "square_feet"  # echoed verbatim from the fact
    rationale = reference["rationale"]
    lowered = rationale.lower()
    assert "reference only" in lowered
    assert "not zoning floor area" in lowered
    assert "never subtracted" in lowered
    # Provenance is named: source, dataset, original field, provenance_ref.
    for token in (SOURCE_ID, "26v1", "bldgarea", PROV_ID):
        assert token in rationale


def test_default_reference_unit_is_echoed_never_guessed():
    rule_evaluation = S.canonical_rule_evaluation()
    section = _section(build_scenario(_profile(9000.0, units=None), rule_evaluation))
    reference = section["assumptions"][1]
    assert reference["key"] == REFERENCE_KEY
    assert reference["unit"] is None


@pytest.mark.parametrize(
    "bldgarea_offset",
    [-1234.5, 4321.25, -0.5, 0.0],
)
def test_default_never_subtracts_recorded_building_area(bldgarea_offset):
    """No number in the section is cap - bldgarea, whatever the relation of the two
    (below, above, just below, equal)."""
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap + bldgarea_offset
    section = _section(build_scenario(_profile(bldgarea), rule_evaluation))

    assert section["unused_draft_zoning_floor_area_sq_ft"] is None
    assert section["formula"] is None
    assert (cap - bldgarea) not in set(_numbers(section))
    assert section["state"] == State.NOT_COMPUTABLE.value


def test_default_derives_no_over_built_from_recorded_building_area(monkeypatch):
    """Recorded building area above the draft cap: the legacy code would say
    over_built and force professional review. By default neither happens."""
    rule_evaluation = S.canonical_rule_evaluation()
    bldgarea = S.trace_cap(rule_evaluation) + 5000.0

    default_doc = build_scenario(_profile(bldgarea), rule_evaluation)
    validate_scenario_document(default_doc)
    section = _section(default_doc)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["state"] != State.OVER_BUILT.value
    assert section["over_built_statement"] is None
    assert section["professional_review_required"] is False
    assert default_doc["professional_review_required"] is False

    # Contrast (the assertions above are discriminating): flag on -> legacy over_built.
    monkeypatch.setenv(FLAG, "1")
    legacy_doc = build_scenario(_profile(bldgarea), S.canonical_rule_evaluation())
    assert _section(legacy_doc)["state"] == State.OVER_BUILT.value
    assert legacy_doc["professional_review_required"] is True


def test_default_zero_with_buildings_raises_no_review_and_carries_no_zero(monkeypatch):
    """A recorded bldgarea of 0 with a positive building count: the legacy code
    escalates to professional review. By default bldgarea is not an input at all,
    so nothing escalates, and the ambiguous zero is not carried for reference."""
    rule_evaluation = S.canonical_rule_evaluation()
    numbldgs = {"value": 1.0, "coverage_status": "conditional"}

    document = build_scenario(_profile(0.0, numbldgs=numbldgs), rule_evaluation)
    validate_scenario_document(document)
    section = _section(document)
    assert section["not_computable_reason"] == Reason.MISSING_EXISTING_BUILDING_AREA.value
    assert section["professional_review_required"] is False
    assert document["professional_review_required"] is False
    assert _assumption_keys(section) == [BASIS_KEY]

    monkeypatch.setenv(FLAG, "1")
    legacy_doc = build_scenario(_profile(0.0, numbldgs=numbldgs), S.canonical_rule_evaluation())
    assert legacy_doc["professional_review_required"] is True


@pytest.mark.parametrize(
    "profile_kwargs",
    [
        {"value": None, "with_fact": False},
        {"value": None},
        {"value": 9000.0, "coverage_status": "data_conflict"},
        {"value": 9000.0, "coverage_status": "unsupported"},
        {"value": "9000"},
        {"value": float("nan")},
        {"value": -1.0},
        {"value": 9000.0, "with_provenance": False},
    ],
    ids=[
        "no_fact",
        "null_value",
        "data_conflict",
        "unsupported",
        "string_value",
        "nan",
        "negative",
        "unresolved_provenance",
    ],
)
def test_default_reference_omitted_when_not_usable(profile_kwargs):
    """The reference record is optional and never carries an absent, unusable,
    or unsourced value; the reason and the basis record are unchanged."""
    rule_evaluation = S.canonical_rule_evaluation()
    kwargs = dict(profile_kwargs)
    value = kwargs.pop("value")
    document = build_scenario(_profile(value, **kwargs), rule_evaluation)
    validate_scenario_document(document)
    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.MISSING_EXISTING_BUILDING_AREA.value
    assert _assumption_keys(section) == [BASIS_KEY]
    assert section["professional_review_required"] is False
    json.dumps(document, allow_nan=False)


@pytest.mark.parametrize("rule_evaluation_factory", NO_CAP_FACTORIES)
def test_default_no_cap_paths_keep_no_draft_far_cap(rule_evaluation_factory):
    document = build_scenario(_profile(9000.0), rule_evaluation_factory())
    validate_scenario_document(document)
    section = _section(document)
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] is None
    assert section["inputs"]["draft_zoning_floor_area_cap"] == {
        "value_sq_ft": None,
        "unit": None,
        "provenance": None,
    }
    assert section["label"] == UNUSED_FLOOR_AREA_NOT_AVAILABLE_LABEL
    assert _assumption_keys(section) == [BASIS_KEY, REFERENCE_KEY]
    assert section["professional_review_required"] is False


def test_default_on_degenerate_empty_inputs():
    document = build_scenario({}, {})
    validate_scenario_document(document)
    section = _section(document)
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value
    assert _assumption_keys(section) == [BASIS_KEY]


@pytest.mark.parametrize("bad_cap", [0.0, -5.0, None, float("nan"), "x"])
def test_direct_default_without_positive_cap(bad_cap):
    section = build_unused_floor_area_section(
        property_profile=_profile(9000.0),
        cap_value=bad_cap,
        cap_provenance={"echoed": "only with a cap"},
        env={},
    )
    assert section["not_computable_reason"] == Reason.NO_DRAFT_FAR_CAP.value
    assert section["inputs"]["draft_zoning_floor_area_cap"]["provenance"] is None
    assert section["inputs"]["draft_zoning_floor_area_cap"]["value_sq_ft"] is None


# ---------------------------------------------------------------------------
# Unknown flag values fall back to the default; the flag on restores legacy.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["", "0", "false", "off", "enabled", "2"])
def test_unknown_flag_values_keep_the_default(monkeypatch, raw):
    monkeypatch.setenv(FLAG, raw)
    rule_evaluation = S.canonical_rule_evaluation()
    bldgarea = S.trace_cap(rule_evaluation) - 1234.5
    section = _section(build_scenario(_profile(bldgarea), rule_evaluation))
    assert section["state"] == State.NOT_COMPUTABLE.value
    assert section["label"] == UNUSED_FLOOR_AREA_NOT_AVAILABLE_LABEL


def test_flag_on_restores_the_legacy_subtraction(monkeypatch):
    monkeypatch.setenv(FLAG, "true")
    rule_evaluation = S.canonical_rule_evaluation()
    cap = S.trace_cap(rule_evaluation)
    bldgarea = cap - 1234.5
    document = build_scenario(_profile(bldgarea), rule_evaluation)
    validate_scenario_document(document)
    section = _section(document)
    assert section["state"] == State.COMPUTED.value
    assert section["unused_draft_zoning_floor_area_sq_ft"] == cap - bldgarea
    assert section["label"] == UNUSED_FLOOR_AREA_LABEL
    assert section["formula"] == C.UNUSED_FLOOR_AREA_FORMULA


def test_direct_env_injection_selects_the_path():
    """``env`` is honored over the process environment in both directions."""
    kwargs = {
        "property_profile": _profile(4000.0),
        "cap_value": 10000.0,
        "cap_provenance": {"echoed": "verbatim"},
    }
    default = build_unused_floor_area_section(**kwargs, env={})
    assert default["state"] == State.NOT_COMPUTABLE.value
    assert default["inputs"]["draft_zoning_floor_area_cap"]["value_sq_ft"] == 10000.0
    assert default["inputs"]["draft_zoning_floor_area_cap"]["provenance"] == {
        "echoed": "verbatim"
    }
    legacy = build_unused_floor_area_section(**kwargs, env={FLAG: "1"})
    assert legacy["state"] == State.COMPUTED.value
    assert legacy["unused_draft_zoning_floor_area_sq_ft"] == 6000.0


# ---------------------------------------------------------------------------
# Contract / JSON safety / determinism / wording discipline on the default.
# ---------------------------------------------------------------------------


def _default_documents():
    re_ = S.canonical_rule_evaluation
    cap = S.trace_cap(re_())
    return [
        ("below_cap", build_scenario(_profile(cap - 100.0), re_())),
        ("above_cap", build_scenario(_profile(cap + 100.0), re_())),
        ("no_fact", build_scenario(_profile(None, with_fact=False), re_())),
        ("no_cap", build_scenario(_profile(1.0), S.conflict_rule_evaluation())),
    ]


def test_default_documents_are_contract_valid_and_strict_json():
    for label, document in _default_documents():
        validate_scenario_document(document)
        assert json.dumps(document, allow_nan=False), label
        encoded = json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
        assert encoded, label


def test_default_assumption_keys_are_display_safe_tokens():
    """The web contract rejects assumption keys it cannot show unaltered
    (A-Z a-z 0-9 . _ -, at most 64 characters)."""
    for label, document in _default_documents():
        for key in _assumption_keys(_section(document)):
            assert re.fullmatch(r"[A-Za-z0-9._-]{1,64}", key), (label, key)


def test_default_is_deterministic_and_profile_untouched():
    prof = _profile(9000.0)
    snapshot = copy.deepcopy(prof)
    first = build_scenario(prof, S.canonical_rule_evaluation())
    second = build_scenario(_profile(9000.0), S.canonical_rule_evaluation())
    assert json.dumps(first) == json.dumps(second)
    assert prof == snapshot


def test_default_wording_has_no_forbidden_nouns_or_verified_language():
    forbidden = ("maximum buildable area", "remaining development rights", "remaining capacity")
    reference = _section(build_scenario(_profile(9000.0), S.canonical_rule_evaluation()))[
        "assumptions"
    ][1]
    strings = [
        C.UNUSED_FLOOR_AREA_NOT_AVAILABLE_LABEL,
        C.UNUSED_FLOOR_AREA_NOT_AVAILABLE_SCOPE_NOTE,
        C.unused_floor_area_not_available_assumption()["rationale"],
        reference["rationale"],
    ]
    for text in strings:
        low = text.lower()
        for phrase in forbidden:
            assert phrase not in low, (phrase, text)
        assert "verified" not in low, text
        assert "compliant" not in low, text
