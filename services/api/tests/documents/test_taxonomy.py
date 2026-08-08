"""Unit tests for the canonical survey fact-type taxonomy (M2-T015 unit 3d-1).

Proves:

1. the canonical closed set is EXACTLY the grounded eleven wire strings, transcribed
   independently here (contract sections 1/4.3/4.5; architecture sections 8.4/9) so a
   silently drifting taxonomy — added, removed, or renamed members — fails this suite;
2. every supported wire string validates to the typed SUPPORTED result carrying its
   resolved enum member;
3. unknown, misspelled, case-varying, whitespace-varying, empty, and non-string
   submissions each yield the typed ``UnsupportedFactType`` RESULT — visible, with the
   submission preserved and a stated reason — never an exception, never silent
   acceptance of a material buildability input;
4. the refusal payload is metadata-only and JSON-serializable with the stable
   ``reject_code``, mirroring the ``errors.py`` payload convention;
5. v1 wire compat: the canonical schema's ``fact_type`` stays an OPEN non-empty string
   (no enum/const/pattern) — this taxonomy is application-level only and changed
   nothing on the wire.
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path

import pytest

from app.documents.taxonomy import (
    SUPPORTED_FACT_TYPES,
    SupportedFactType,
    SurveyFactType,
    UnsupportedFactType,
    validate_fact_type,
)

#: Transcribed INDEPENDENTLY of taxonomy.py, from the grounding documents themselves,
#: so drift between the module and its grounding fails here.
EXPECTED_FACT_TYPES = frozenset(
    {
        # Detected facts (contract sections 1 and 4.3; architecture section 9).
        "boundary_segment_distance",
        "boundary_bearing",
        "stated_lot_area",
        "scale_statement",
        "north_arrow_orientation",
        "elevation_value",
        "address_text",
        "bbl_text",
        # Derived facts (architecture section 8.4).
        "computed_closure",
        "calculated_lot_area",
        "reconstructed_boundary_polygon",
    }
)

#: Canonical wire contract, at its packages/contracts source of truth (repo checkout).
SCHEMA_PATH = (
    Path(__file__).resolve().parents[4]
    / "packages"
    / "contracts"
    / "schemas"
    / "v1"
    / "survey_evidence.schema.json"
)


# ------------------------------------------------------------------- canonical set


def test_canonical_set_is_exactly_the_grounded_eleven() -> None:
    assert {member.value for member in SurveyFactType} == EXPECTED_FACT_TYPES
    assert SUPPORTED_FACT_TYPES == EXPECTED_FACT_TYPES


def test_wire_values_are_unique_snake_case() -> None:
    values = [member.value for member in SurveyFactType]
    assert len(values) == len(set(values))
    for value in values:
        assert re.fullmatch(r"[a-z][a-z0-9]*(_[a-z0-9]+)*", value), value


# ------------------------------------------------------------------ supported path


@pytest.mark.parametrize("member", list(SurveyFactType), ids=lambda m: m.value)
def test_every_supported_type_validates_supported(member: SurveyFactType) -> None:
    result = validate_fact_type(member.value)
    assert isinstance(result, SupportedFactType)
    assert result.fact_type is member
    assert result.supported is True
    assert not isinstance(result, Exception)


# ------------------------------------------------------------------- refused path


UNKNOWN_STRINGS = [
    "lot_frontage",  # plausible but ungrounded — not silently accepted
    "boundry_segment_distance",  # misspelling of a supported type
    "BOUNDARY_SEGMENT_DISTANCE",  # exact match only: no case folding
    "Stated_Lot_Area",
    " stated_lot_area ",  # no trimming/cleanup — silent cleanup is silent acceptance
    "stated_lot_area\n",
    "boundary segment distance",
    "",  # wire requires non-empty; the application refuses it too
    "   ",
]


@pytest.mark.parametrize("submitted", UNKNOWN_STRINGS, ids=[repr(s) for s in UNKNOWN_STRINGS])
def test_unknown_and_malformed_strings_yield_typed_unsupported(submitted: str) -> None:
    result = validate_fact_type(submitted)
    assert isinstance(result, UnsupportedFactType)
    assert result.supported is False
    assert result.submitted_fact_type == submitted  # preserved verbatim
    assert result.reason.strip()
    assert not isinstance(result, Exception)


NON_STRINGS = [
    None,
    42,
    3.5,
    True,
    b"stated_lot_area",
    ["stated_lot_area"],
    {"fact_type": "stated_lot_area"},
    SurveyFactType.STATED_LOT_AREA,  # the wire boundary takes strings, not members
]


@pytest.mark.parametrize("submitted", NON_STRINGS, ids=[repr(s) for s in NON_STRINGS])
def test_non_string_submissions_refused_typed_never_crash(submitted: object) -> None:
    result = validate_fact_type(submitted)  # type: ignore[arg-type]  # deliberate wrong type
    assert isinstance(result, UnsupportedFactType)
    assert result.supported is False
    assert result.submitted_fact_type == repr(submitted)
    assert "string" in result.reason


def test_unsupported_payload_is_json_serializable_metadata_only() -> None:
    result = validate_fact_type("boundry_segment_distance")
    assert isinstance(result, UnsupportedFactType)
    assert result.reject_code == "unsupported_fact_type"
    payload = result.to_payload()
    assert payload["reject_code"] == "unsupported_fact_type"
    assert payload["submitted_fact_type"] == "boundry_segment_distance"
    assert payload["reason"]
    assert set(payload) == {"reject_code", "submitted_fact_type", "reason"}
    json.dumps(payload)  # serializable into an API response / audit record


def test_results_are_immutable_values() -> None:
    supported = validate_fact_type("stated_lot_area")
    unsupported = validate_fact_type("lot_frontage")
    with pytest.raises(dataclasses.FrozenInstanceError):
        supported.fact_type = SurveyFactType.ADDRESS_TEXT  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        unsupported.reason = "rewritten"  # type: ignore[misc]


# ---------------------------------------------------------------- v1 wire compat


def test_wire_contract_fact_type_stays_open_string() -> None:
    assert SCHEMA_PATH.is_file(), f"canonical schema missing from checkout: {SCHEMA_PATH}"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fact_type = schema["properties"]["fact_type"]
    # OPEN-WITH-FLAG (contract section 4.3): open non-empty string, no closed set on
    # the wire in v1 — the taxonomy lands there only as a future additive enum.
    assert fact_type["$ref"] == "common.schema.json#/$defs/non_empty_string"
    assert "enum" not in fact_type
    assert "const" not in fact_type
    assert "pattern" not in fact_type
