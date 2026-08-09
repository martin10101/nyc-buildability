"""Unit tests for cross-field geometry/location validation (M2-T015 unit 3e-1).

Proves:

1. every consistent locator resolves to its typed RESOLVED result — coordinates,
   coordinate space, and object reference preserved exactly as submitted, never
   converted, re-ordered, or re-spaced (bounding-box locators in both page spaces,
   vector-object locators with and without a display rectangle);
2. every locator invariant fails closed: inverted extents, non-finite or non-numeric
   coordinates, coordinates invalid for their declared space, unknown or survey/world
   coordinate systems, kind-inconsistent locator parts, malformed raster/PDF-page/
   other-system mixing (including smuggled keys), and contradictory locator-kind /
   extraction-method pairings each yield the typed ``UnresolvedLocation`` RESULT,
   visible, with the submission preserved and a stated reason, never an exception and
   never a silent swap, clamp, default, or coercion;
3. the unresolved result can never become canonical geometry: it carries no
   coordinates, rectangle, reference, or kind at all, and its ``promotable`` flag is
   permanently ``False``;
4. the refusal payload is metadata-only and JSON-serializable with the stable
   ``reject_code``, mirroring the ``errors.py`` payload convention;
5. v1 wire compat: this module is application-level only — the closed kind,
   coordinate-space, and extraction-method vocabularies match the wire contract
   verbatim, and validating changed nothing on the wire.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from app.documents.geometry_validation import (
    BOUNDING_BOX_KEYS,
    LOCATION_KEYS,
    CoordinateSpace,
    ExtractionMethod,
    LocatorKind,
    UnresolvedLocation,
    ValidatedBoundingBox,
    ValidatedBoundingBoxLocation,
    ValidatedVectorObjectLocation,
    validate_location,
)

# ------------------------------------------------------------------- builders


def pdf_box(**overrides: object) -> dict:
    box: dict = {
        "x_min": 100.5,
        "y_min": 200.0,
        "x_max": 150.25,
        "y_max": 240.0,
        "coordinate_space": "pdf_user_space_points",
    }
    box.update(overrides)
    return box


def raster_box(**overrides: object) -> dict:
    box: dict = {
        "x_min": 0,
        "y_min": 12,
        "x_max": 640,
        "y_max": 480,
        "coordinate_space": "raster_pixels",
    }
    box.update(overrides)
    return box


def without(box: dict, key: str) -> dict:
    return {k: v for k, v in box.items() if k != key}


def bbox_location(box: object) -> dict:
    return {"kind": "bounding_box", "bounding_box": box}


def vector_location(reference: object = "page/1/content/12", box: object = None) -> dict:
    location: dict = {"kind": "vector_object", "object_reference": reference}
    if box is not None:
        location["bounding_box"] = box
    return location


# -------------------------------------------------------------- resolved path

#: (case id, location, extraction_method, expected result type). One passing case per
#: invariant, covering every extraction path and both coordinate spaces; the
#: preservation assertions prove the stated submission is kept exactly.
VALID_CASES = [
    (
        "pdf-embedded-text-box",
        bbox_location(pdf_box()),
        "embedded_text_extraction",
        ValidatedBoundingBoxLocation,
    ),
    ("raster-ocr-box", bbox_location(raster_box()), "ocr_text", ValidatedBoundingBoxLocation),
    (
        "raster-line-symbol-box",
        bbox_location(raster_box()),
        "line_symbol_detection",
        ValidatedBoundingBoxLocation,
    ),
    (
        "ai-classified-region",
        bbox_location(pdf_box()),
        "ai_assisted_classification",
        ValidatedBoundingBoxLocation,
    ),
    (
        "reconstruction-derived-box",
        bbox_location(pdf_box()),
        "deterministic_geometry_reconstruction",
        ValidatedBoundingBoxLocation,
    ),
    (
        # PDF user space is sign-unrestricted: the contract does not bound the page box.
        "pdf-negative-user-space",
        bbox_location(pdf_box(x_min=-10.0, x_max=-2.5)),
        "embedded_text_extraction",
        ValidatedBoundingBoxLocation,
    ),
    (
        # The contract states '<=', so a degenerate zero-extent edge is in-contract.
        "degenerate-equal-extent",
        bbox_location(pdf_box(x_min=100.5, x_max=100.5, y_min=240.0, y_max=240.0)),
        "embedded_text_extraction",
        ValidatedBoundingBoxLocation,
    ),
    (
        "raster-zero-origin",
        bbox_location(raster_box(x_min=0, y_min=0)),
        "ocr_text",
        ValidatedBoundingBoxLocation,
    ),
    (
        "vector-object-plain",
        vector_location(),
        "vector_object_extraction",
        ValidatedVectorObjectLocation,
    ),
    (
        "vector-object-display-box",
        vector_location(box=pdf_box()),
        "vector_object_extraction",
        ValidatedVectorObjectLocation,
    ),
]


@pytest.mark.parametrize(
    ("case_id", "location", "extraction_method", "expected_type"),
    VALID_CASES,
    ids=[case[0] for case in VALID_CASES],
)
def test_every_consistent_locator_resolves(
    case_id: str, location: dict, extraction_method: str, expected_type: type
) -> None:
    result = validate_location(location, extraction_method)
    assert isinstance(result, expected_type)
    assert not isinstance(result, UnresolvedLocation)
    assert result.resolved is True
    assert not isinstance(result, Exception)
    if isinstance(result, ValidatedBoundingBoxLocation):
        assert result.kind is LocatorKind.BOUNDING_BOX
        submitted = location["bounding_box"]
        box = result.bounding_box
        # Preserved exactly — never converted, re-ordered, or re-spaced.
        assert (box.x_min, box.y_min, box.x_max, box.y_max) == (
            submitted["x_min"],
            submitted["y_min"],
            submitted["x_max"],
            submitted["y_max"],
        )
        assert box.coordinate_space is CoordinateSpace(submitted["coordinate_space"])
    else:
        assert result.kind is LocatorKind.VECTOR_OBJECT
        assert result.object_reference == location["object_reference"]


def test_display_bounding_box_is_optional_and_typed() -> None:
    plain = validate_location(vector_location(), "vector_object_extraction")
    assert isinstance(plain, ValidatedVectorObjectLocation)
    assert plain.display_bounding_box is None
    highlighted = validate_location(vector_location(box=pdf_box()), "vector_object_extraction")
    assert isinstance(highlighted, ValidatedVectorObjectLocation)
    assert isinstance(highlighted.display_bounding_box, ValidatedBoundingBox)
    assert highlighted.display_bounding_box.coordinate_space is (
        CoordinateSpace.PDF_USER_SPACE_POINTS
    )


def test_negative_coordinates_are_space_conditional() -> None:
    # The SAME negative extent is valid PDF user space but impossible raster pixels.
    negative = {"x_min": -10.0, "y_min": 200.0, "x_max": -2.5, "y_max": 240.0}
    pdf = validate_location(
        bbox_location(dict(negative, coordinate_space="pdf_user_space_points")),
        "embedded_text_extraction",
    )
    assert isinstance(pdf, ValidatedBoundingBoxLocation)
    raster = validate_location(
        bbox_location(dict(negative, coordinate_space="raster_pixels")), "ocr_text"
    )
    assert isinstance(raster, UnresolvedLocation)
    assert "negative" in raster.reason


def test_degenerate_equality_is_in_contract_but_inversion_is_not() -> None:
    # The contract's own comment states '<=': equality resolves, epsilon-inversion fails.
    assert isinstance(
        validate_location(
            bbox_location(pdf_box(x_min=100.5, x_max=100.5)), "embedded_text_extraction"
        ),
        ValidatedBoundingBoxLocation,
    )
    inverted = validate_location(
        bbox_location(pdf_box(x_min=100.5001, x_max=100.5)), "embedded_text_extraction"
    )
    assert isinstance(inverted, UnresolvedLocation)
    assert "x_min" in inverted.reason


# ------------------------------------------------------------ unresolved path

#: (case id, location, extraction_method) — at least one failing case per invariant:
#: extent ordering, finite numeric coordinates, space-conditional validity, the closed
#: coordinate-space vocabulary, closed shapes (no smuggled coordinate-system keys),
#: locator-kind consistency, the vector-kind/extraction-path pairing, the closed kind
#: and extraction-method vocabularies, and non-object locators.
UNRESOLVED_CASES = [
    # extent ordering — never silently swapped
    ("x-inverted", bbox_location(pdf_box(x_min=150.25, x_max=100.5)), "embedded_text_extraction"),
    ("y-inverted", bbox_location(raster_box(y_min=480, y_max=12)), "ocr_text"),
    # finite numeric coordinates — never coerced or parsed
    ("nan-coordinate", bbox_location(pdf_box(x_min=float("nan"))), "embedded_text_extraction"),
    ("inf-coordinate", bbox_location(pdf_box(y_max=float("inf"))), "embedded_text_extraction"),
    ("string-coordinate", bbox_location(pdf_box(x_min="100.5")), "embedded_text_extraction"),
    ("bool-coordinate", bbox_location(pdf_box(x_max=True)), "embedded_text_extraction"),
    ("null-coordinate", bbox_location(raster_box(y_min=None)), "ocr_text"),
    # coordinates valid for the declared space
    ("negative-raster-pixel", bbox_location(raster_box(x_min=-5)), "ocr_text"),
    # closed coordinate-space vocabulary — page coordinates are never survey/world
    (
        "alias-space",
        bbox_location(pdf_box(coordinate_space="pdf_points")),
        "embedded_text_extraction",
    ),
    ("case-folded-space", bbox_location(raster_box(coordinate_space="RASTER_PIXELS")), "ocr_text"),
    (
        "survey-world-crs",
        bbox_location(pdf_box(coordinate_space="epsg:2263")),
        "embedded_text_extraction",
    ),
    (
        "survey-world-name",
        bbox_location(pdf_box(coordinate_space="survey_world")),
        "embedded_text_extraction",
    ),
    ("non-string-space", bbox_location(pdf_box(coordinate_space=72)), "embedded_text_extraction"),
    (
        "missing-space",
        bbox_location(without(pdf_box(), "coordinate_space")),
        "embedded_text_extraction",
    ),
    # closed shapes — no smuggled coordinate-system side channel, no partial rectangles
    ("smuggled-crs-key", bbox_location(pdf_box(crs="EPSG:2263")), "embedded_text_extraction"),
    ("missing-y-max", bbox_location(without(pdf_box(), "y_max")), "embedded_text_extraction"),
    (
        "unknown-location-key",
        dict(bbox_location(pdf_box()), page_rotation=90),
        "embedded_text_extraction",
    ),
    ("box-not-an-object", bbox_location([100.5, 200.0, 150.25, 240.0]), "embedded_text_extraction"),
    # locator-kind consistency
    ("bounding-box-kind-missing-box", {"kind": "bounding_box"}, "embedded_text_extraction"),
    (
        "bounding-box-kind-with-object-reference",
        dict(bbox_location(pdf_box()), object_reference="page/1/content/12"),
        "embedded_text_extraction",
    ),
    ("vector-kind-missing-reference", {"kind": "vector_object"}, "vector_object_extraction"),
    ("vector-kind-empty-reference", vector_location(reference=""), "vector_object_extraction"),
    (
        "vector-kind-whitespace-reference",
        vector_location(reference="   "),
        "vector_object_extraction",
    ),
    ("vector-kind-non-string-reference", vector_location(reference=12), "vector_object_extraction"),
    ("vector-kind-non-vector-method", vector_location(), "ocr_text"),
    (
        "vector-kind-invalid-display-box",
        vector_location(box=pdf_box(x_min=150.25, x_max=100.5)),
        "vector_object_extraction",
    ),
    # closed kind vocabulary
    ("missing-kind", {"bounding_box": pdf_box()}, "embedded_text_extraction"),
    (
        "case-folded-kind",
        dict(bbox_location(pdf_box()), kind="BOUNDING_BOX"),
        "embedded_text_extraction",
    ),
    ("unknown-kind", dict(bbox_location(pdf_box()), kind="polygon"), "embedded_text_extraction"),
    ("non-string-kind", dict(bbox_location(pdf_box()), kind=None), "embedded_text_extraction"),
    # non-object locators
    ("location-not-an-object", [{"kind": "bounding_box"}], "embedded_text_extraction"),
    ("location-string", "page 1, upper left", "ocr_text"),
    # closed extraction-method vocabulary
    ("unapproved-path", bbox_location(pdf_box()), "dwg_native_parsing"),
    ("case-folded-method", bbox_location(pdf_box()), "OCR_TEXT"),
    ("non-string-method", bbox_location(pdf_box()), None),
]


@pytest.mark.parametrize(
    ("case_id", "location", "extraction_method"),
    UNRESOLVED_CASES,
    ids=[case[0] for case in UNRESOLVED_CASES],
)
def test_contradictory_or_malformed_location_evidence_fails_closed(
    case_id: str, location: object, extraction_method: object
) -> None:
    result = validate_location(location, extraction_method)
    assert isinstance(result, UnresolvedLocation)
    assert result.resolved is False
    assert result.promotable is False
    assert result.reject_code == "unresolved_location"
    assert result.reason.strip()
    assert result.submitted_location == repr(location)  # submission preserved, visible
    assert not isinstance(result, Exception)
    # Nothing to promote: no coordinates, rectangle, reference, or kind at all.
    assert not hasattr(result, "bounding_box")
    assert not hasattr(result, "display_bounding_box")
    assert not hasattr(result, "object_reference")
    assert not hasattr(result, "kind")
    assert not hasattr(result, "x_min")


def test_survey_world_refusal_states_the_page_rule() -> None:
    result = validate_location(
        bbox_location(pdf_box(coordinate_space="epsg:2263")), "embedded_text_extraction"
    )
    assert isinstance(result, UnresolvedLocation)
    assert "survey/world" in result.reason


def test_smuggled_coordinate_system_key_is_named_in_the_refusal() -> None:
    result = validate_location(
        bbox_location(pdf_box(crs="EPSG:2263")), "embedded_text_extraction"
    )
    assert isinstance(result, UnresolvedLocation)
    assert "crs" in result.reason


def test_object_reference_on_bounding_box_kind_is_malformed_mixing() -> None:
    result = validate_location(
        dict(bbox_location(pdf_box()), object_reference="page/1/content/12"),
        "embedded_text_extraction",
    )
    assert isinstance(result, UnresolvedLocation)
    assert "vector-object" in result.reason


def test_vector_kind_with_non_vector_path_is_contradictory() -> None:
    result = validate_location(vector_location(), "ocr_text")
    assert isinstance(result, UnresolvedLocation)
    assert "vector-object extraction path" in result.reason
    assert "'ocr_text'" in result.reason


def test_non_string_dict_key_never_raises() -> None:
    # A non-string key must fail closed as an unknown key, never crash the refusal.
    result = validate_location(
        {**bbox_location(pdf_box()), 7: "seven"}, "embedded_text_extraction"
    )
    assert isinstance(result, UnresolvedLocation)
    assert "unknown key" in result.reason


def test_unresolved_payload_is_json_serializable_metadata_only() -> None:
    result = validate_location("page 1, upper left", "ocr_text")
    assert isinstance(result, UnresolvedLocation)
    payload = result.to_payload()
    assert payload["reject_code"] == "unresolved_location"
    assert payload["submitted_location"] == "'page 1, upper left'"
    assert payload["submitted_extraction_method"] == "ocr_text"
    assert payload["reason"]
    assert set(payload) == {
        "reject_code",
        "submitted_location",
        "submitted_extraction_method",
        "reason",
    }
    json.dumps(payload)  # serializable into an API response / audit record


def test_non_string_extraction_method_preserved_as_repr_or_null() -> None:
    numeric = validate_location(bbox_location(pdf_box()), 12)
    assert isinstance(numeric, UnresolvedLocation)
    assert numeric.submitted_extraction_method == "12"
    stated_absent = validate_location(bbox_location(pdf_box()), None)
    assert isinstance(stated_absent, UnresolvedLocation)
    assert stated_absent.submitted_extraction_method is None
    json.dumps(numeric.to_payload())
    json.dumps(stated_absent.to_payload())


def test_results_are_immutable_values() -> None:
    resolved = validate_location(bbox_location(pdf_box()), "embedded_text_extraction")
    assert isinstance(resolved, ValidatedBoundingBoxLocation)
    unresolved = validate_location(bbox_location(pdf_box(x_min=999.0)), "embedded_text_extraction")
    assert isinstance(unresolved, UnresolvedLocation)
    with pytest.raises(dataclasses.FrozenInstanceError):
        resolved.kind = LocatorKind.VECTOR_OBJECT  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        resolved.bounding_box.x_min = 0.0  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        unresolved.reason = "rewritten"  # type: ignore[misc]


# ---------------------------------------------------------------- wire compat


def test_closed_vocabularies_match_the_wire_contract_verbatim() -> None:
    assert frozenset(member.value for member in LocatorKind) == frozenset(
        {"bounding_box", "vector_object"}
    )
    assert frozenset(member.value for member in CoordinateSpace) == frozenset(
        {"pdf_user_space_points", "raster_pixels"}
    )
    assert frozenset(member.value for member in ExtractionMethod) == frozenset(
        {
            "vector_object_extraction",
            "embedded_text_extraction",
            "ocr_text",
            "line_symbol_detection",
            "ai_assisted_classification",
            "deterministic_geometry_reconstruction",
        }
    )
    assert BOUNDING_BOX_KEYS == frozenset(
        {"x_min", "y_min", "x_max", "y_max", "coordinate_space"}
    )
    assert LOCATION_KEYS == frozenset({"kind", "bounding_box", "object_reference"})
