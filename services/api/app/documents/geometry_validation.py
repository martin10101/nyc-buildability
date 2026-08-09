"""Deterministic cross-field geometry/location validation for survey facts (application-level; M2-T015).

Enforces the ``location`` relationships of
``packages/contracts/schemas/v1/survey_evidence.schema.json`` (contract 1.0.0) that the
wire contract deliberately leaves to deterministic code — its bounding-box ``$comment``
states verbatim that "x_min <= x_max and y_min <= y_max are enforced by the
deterministic validation code (cross-field numeric comparison is outside this
contract's keyword subset)". This module is that code. Each invariant is grounded in a
locator shape the schema states, never invented:

1. extent ordering — ``x_min <= x_max`` and ``y_min <= y_max``; equality is allowed
   because the contract itself states ``<=``, and an inverted extent is contradictory
   location evidence, never silently swapped;
2. finite numeric coordinates — every coordinate must be a JSON number that is finite;
   ``NaN``/``inf``, strings, ``bool``, and every other shape are refused, never coerced
   or parsed;
3. coordinates valid FOR the declared space — ``raster_pixels`` coordinates are pixel
   positions of the decoded page/frame image (origin top-left) and can never be
   negative; ``pdf_user_space_points`` coordinates are sign-unrestricted because the
   contract does not bound the page box;
4. one closed coordinate-space vocabulary — exactly ``pdf_user_space_points`` or
   ``raster_pixels``; "Page coordinates are NEVER survey/world coordinates" (schema,
   verbatim), so a survey/world CRS or any other coordinate system is refused, never
   interpreted or converted;
5. locator-kind consistency — kind ``bounding_box`` requires the rectangle and refuses
   an ``object_reference`` (the schema states an object reference is "Meaningful only
   for the vector-object extraction path", so its presence on a bounding-box locator
   is malformed mixing of the two locator shapes); kind ``vector_object`` requires a
   meaningful non-empty ``object_reference``, MAY additionally carry a display
   ``bounding_box`` which must itself satisfy every rule above, and is contradictory
   with any ``extraction_method`` other than ``vector_object_extraction`` (same schema
   sentence — no other path can have produced an object reference);
6. closed shapes — an unknown key on ``location`` or ``bounding_box`` (e.g. a smuggled
   ``crs``/``epsg`` marker) mirrors the wire ``additionalProperties:false`` and is
   refused, never ignored, so raster/PDF-page/survey-world/other coordinate systems
   can never be mixed through a side channel.

NOTHING here changes the wire contract: no wire field, type, enum, or pattern moves.
This module is the application-level authority on locator relationships — exactly the
role :mod:`app.documents.units` plays for normalized values and stated units, whose
typed-result pattern (frozen value results, refusal-as-value, exact match only) it
reuses.

Fail-closed rule: invalid or contradictory location/geometry evidence yields the
typed, visible :class:`UnresolvedLocation` RESULT — a value, deliberately not an
exception and never raised — carrying only the verbatim submission and a stated
reason, and no coordinates, reference, kind, or locator of any sort, so downstream
code has nothing it could ever promote. Exact match only: kind, coordinate-space, and
extraction-method strings get no trimming, case-folding, or alias/abbreviation
interpretation, and coordinates are never converted between spaces. Even a RESOLVED
result is only a validated page locator: it says WHERE evidence sits on a page of the
immutable original and is never itself canonical geometry — promotion still runs
through the deterministic checks and qualified-human confirmation.
"""

from __future__ import annotations

import enum
import math
from collections.abc import Iterable
from dataclasses import dataclass

__all__ = [
    "BOUNDING_BOX_KEYS",
    "CoordinateSpace",
    "ExtractionMethod",
    "LOCATION_KEYS",
    "LocationValidation",
    "LocatorKind",
    "UnresolvedLocation",
    "ValidatedBoundingBox",
    "ValidatedBoundingBoxLocation",
    "ValidatedVectorObjectLocation",
    "validate_location",
]


@enum.unique
class LocatorKind(enum.Enum):
    """Closed wire locator discriminator (survey_evidence ``location.kind``, verbatim)."""

    BOUNDING_BOX = "bounding_box"
    VECTOR_OBJECT = "vector_object"


@enum.unique
class CoordinateSpace(enum.Enum):
    """Closed wire page coordinate spaces (survey_evidence ``coordinate_space``, verbatim).

    Page coordinates are never survey/world coordinates: no CRS, EPSG code, datum, or
    any other coordinate system is a member, and none is ever interpreted here —
    geo-interpretation is a deterministic-check concern, not a locator concern.
    """

    PDF_USER_SPACE_POINTS = "pdf_user_space_points"
    RASTER_PIXELS = "raster_pixels"


@enum.unique
class ExtractionMethod(enum.Enum):
    """Closed wire extraction paths (survey_evidence ``extraction_method``, verbatim).

    Mirrored here because locator-kind consistency is cross-field: a ``vector_object``
    locator is meaningful only for the vector-object extraction path. An unapproved
    path (e.g. native DWG parsing — format policy row 7, DEFERRED) is rejected at
    ingestion and is refused here the same way, never interpreted.
    """

    VECTOR_OBJECT_EXTRACTION = "vector_object_extraction"
    EMBEDDED_TEXT_EXTRACTION = "embedded_text_extraction"
    OCR_TEXT = "ocr_text"
    LINE_SYMBOL_DETECTION = "line_symbol_detection"
    AI_ASSISTED_CLASSIFICATION = "ai_assisted_classification"
    DETERMINISTIC_GEOMETRY_RECONSTRUCTION = "deterministic_geometry_reconstruction"


#: The wire bounding-box shape is closed (additionalProperties:false): exactly these
#: keys, all required. An extra key is refused, never ignored.
BOUNDING_BOX_KEYS: frozenset[str] = frozenset(
    {"x_min", "y_min", "x_max", "y_max", "coordinate_space"}
)

#: The wire location shape is closed (additionalProperties:false): ``kind`` plus the
#: two kind-conditional locator keys. An extra key is refused, never ignored.
LOCATION_KEYS: frozenset[str] = frozenset({"kind", "bounding_box", "object_reference"})

_COORDINATE_KEYS = ("x_min", "y_min", "x_max", "y_max")


# ------------------------------------------------------------------ typed results


@dataclass(frozen=True)
class ValidatedBoundingBox:
    """Typed RESOLVED page rectangle: the stated coordinates in their stated space,
    exactly as submitted — never converted between spaces, never re-ordered."""

    x_min: int | float
    y_min: int | float
    x_max: int | float
    y_max: int | float
    coordinate_space: CoordinateSpace

    resolved = True


@dataclass(frozen=True)
class ValidatedBoundingBoxLocation:
    """Typed RESOLVED ``bounding_box``-kind locator: the fact is located by a
    consistent page-region rectangle. A validated page locator only — never itself
    canonical geometry."""

    kind: LocatorKind
    bounding_box: ValidatedBoundingBox

    resolved = True


@dataclass(frozen=True)
class ValidatedVectorObjectLocation:
    """Typed RESOLVED ``vector_object``-kind locator: the fact is located by a stable
    vector content-object reference, optionally with a display-highlighting rectangle
    that itself satisfied every bounding-box rule."""

    kind: LocatorKind
    object_reference: str
    display_bounding_box: ValidatedBoundingBox | None

    resolved = True


@dataclass(frozen=True)
class UnresolvedLocation:
    """Typed refusal of location/geometry evidence that is invalid or contradictory —
    a visible RESULT that can NEVER become canonical geometry.

    Deliberately a value, not a ``DocumentIngestionError`` subclass and never raised:
    an inverted extent, a non-finite coordinate, a mixed or unknown coordinate system,
    or a locator whose parts contradict its kind is a routine fail-closed outcome the
    caller must handle and surface — typed rejection, route to review — not a crash.
    The result carries ONLY the verbatim submission (``repr``) and the stated reason:
    it has no coordinates, no rectangle, no reference, and no kind, so there is
    nothing downstream code could promote into a material buildability input. The
    payload is metadata only — mirroring the ``errors.py`` payload convention — and
    safe to serialize into an API response or audit record.
    """

    submitted_location: str
    submitted_extraction_method: str | None
    reason: str

    resolved = False
    promotable = False
    reject_code = "unresolved_location"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "submitted_location": self.submitted_location,
            "submitted_extraction_method": self.submitted_extraction_method,
            "reason": self.reason,
        }


LocationValidation = (
    ValidatedBoundingBoxLocation | ValidatedVectorObjectLocation | UnresolvedLocation
)


# ---------------------------------------------------------------------- helpers


def _unresolved(location: object, extraction_method: object, reason: str) -> UnresolvedLocation:
    return UnresolvedLocation(
        submitted_location=repr(location),
        submitted_extraction_method=(
            extraction_method
            if extraction_method is None or isinstance(extraction_method, str)
            else repr(extraction_method)
        ),
        reason=reason,
    )


def _key_list(keys: Iterable[object]) -> str:
    # repr-sort so a non-string dict key can never make the refusal itself raise.
    return ", ".join(sorted(repr(key) for key in keys))


def _validate_bounding_box(box: object, role: str) -> ValidatedBoundingBox | str:
    """The consistent rectangle itself, or the refusal reason string.

    The union discriminates cleanly (mirrors ``units._as_number``): an acceptable
    result is never a ``str``, so a ``str`` result is always the reason.
    """
    if not isinstance(box, dict):
        return (
            f"{role} must be a JSON object with exactly the keys "
            f"{sorted(BOUNDING_BOX_KEYS)}, got {type(box).__name__} — a rectangle is "
            "never reconstructed from any other shape"
        )
    missing = BOUNDING_BOX_KEYS - box.keys()
    if missing:
        return (
            f"{role} is missing required key(s) {_key_list(missing)}; a partial "
            "rectangle is never completed by default or inference"
        )
    unknown = box.keys() - BOUNDING_BOX_KEYS
    if unknown:
        return (
            f"{role} carries unknown key(s) {_key_list(unknown)}; the wire shape is "
            "closed (additionalProperties:false), and an undocumented key — e.g. a "
            "smuggled crs/epsg coordinate-system marker — is never ignored, so "
            "coordinate systems can never be mixed through a side channel"
        )
    space_value = box["coordinate_space"]
    if not isinstance(space_value, str):
        return (
            f"{role} coordinate_space must be the stated wire enum string, got "
            f"{type(space_value).__name__} — a non-string space cannot be matched exactly"
        )
    try:
        space = CoordinateSpace(space_value)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in CoordinateSpace))
        return (
            f"{space_value!r} is not a supported page coordinate space (supported: "
            f"{supported}); page coordinates are never survey/world coordinates, and "
            "no other coordinate system is ever interpreted or converted here — exact "
            "match required, no alias, case, or whitespace interpretation"
        )
    for key in _COORDINATE_KEYS:
        value = box[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return (
                f"{role} coordinate {key} must be a number, got {type(value).__name__} "
                "— a non-numeric coordinate is never coerced or parsed here"
            )
        if not math.isfinite(value):
            return f"{role} coordinate {key} must be a finite number, got {value!r}"
    if space is CoordinateSpace.RASTER_PIXELS:
        negative = [key for key in _COORDINATE_KEYS if box[key] < 0]
        if negative:
            return (
                f"{role} declares raster_pixels, whose coordinates are pixel positions "
                "of the decoded page/frame image (origin top-left) and can never be "
                f"negative; negative: {_key_list(negative)} — never clamped or shifted"
            )
    if box["x_min"] > box["x_max"]:
        return (
            f"{role} violates x_min <= x_max (x_min={box['x_min']!r} > "
            f"x_max={box['x_max']!r}); an inverted extent is contradictory location "
            "evidence and is never silently swapped"
        )
    if box["y_min"] > box["y_max"]:
        return (
            f"{role} violates y_min <= y_max (y_min={box['y_min']!r} > "
            f"y_max={box['y_max']!r}); an inverted extent is contradictory location "
            "evidence and is never silently swapped"
        )
    return ValidatedBoundingBox(
        x_min=box["x_min"],
        y_min=box["y_min"],
        x_max=box["x_max"],
        y_max=box["y_max"],
        coordinate_space=space,
    )


# --------------------------------------------------------------------- validator


def validate_location(location: object, extraction_method: object) -> LocationValidation:
    """Validate one fact's ``location`` locator against its ``extraction_method``.

    Both parameters are the wire values and deliberately have NO defaults — a caller
    must state the extraction path explicitly because locator-kind consistency is
    cross-field (an object reference can only come from the vector-object path).
    Returns the kind's typed RESOLVED locator when every cross-field relationship
    holds, else the typed :class:`UnresolvedLocation`. Never raises — every malformed,
    mixed, inverted, non-finite, or contradictory submission becomes the typed
    refusal, so invalid location evidence can neither crash ingestion nor slip
    through toward canonical geometry.
    """
    if not isinstance(extraction_method, str):
        return _unresolved(
            location,
            extraction_method,
            (
                "extraction_method must be the stated wire enum string, got "
                f"{type(extraction_method).__name__} — a non-string path cannot be "
                "matched exactly"
            ),
        )
    try:
        method = ExtractionMethod(extraction_method)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in ExtractionMethod))
        return _unresolved(
            location,
            extraction_method,
            (
                f"{extraction_method!r} is not an authorized extraction path (closed "
                f"wire enum: {supported}); an unapproved path is rejected, never "
                "interpreted — exact match required"
            ),
        )
    if not isinstance(location, dict):
        return _unresolved(
            location,
            extraction_method,
            (
                f"location must be a JSON object, got {type(location).__name__} — a "
                "locator is never reconstructed from any other shape"
            ),
        )
    unknown = location.keys() - LOCATION_KEYS
    if unknown:
        return _unresolved(
            location,
            extraction_method,
            (
                f"location carries unknown key(s) {_key_list(unknown)}; the wire shape "
                "is closed (additionalProperties:false), and an undocumented key is "
                "never ignored"
            ),
        )
    if "kind" not in location:
        return _unresolved(
            location,
            extraction_method,
            (
                "location must state its locator kind explicitly; a missing kind is "
                "never defaulted or inferred from which locator keys happen to be present"
            ),
        )
    kind_value = location["kind"]
    if not isinstance(kind_value, str):
        return _unresolved(
            location,
            extraction_method,
            (
                "location kind must be the stated wire enum string, got "
                f"{type(kind_value).__name__} — a non-string kind cannot be matched exactly"
            ),
        )
    try:
        kind = LocatorKind(kind_value)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in LocatorKind))
        return _unresolved(
            location,
            extraction_method,
            (
                f"{kind_value!r} is not a supported locator kind (supported: "
                f"{supported}); exact match required — no alias, case, or whitespace "
                "interpretation"
            ),
        )
    if kind is LocatorKind.BOUNDING_BOX:
        if "object_reference" in location:
            return _unresolved(
                location,
                extraction_method,
                (
                    "an object_reference is meaningful only for the vector-object "
                    "extraction path; its presence on a 'bounding_box' locator "
                    "malformedly mixes the two locator shapes and is contradictory "
                    "location evidence"
                ),
            )
        if "bounding_box" not in location:
            return _unresolved(
                location,
                extraction_method,
                (
                    "a 'bounding_box' locator requires its bounding_box rectangle; a "
                    "missing rectangle is never defaulted or reconstructed"
                ),
            )
        box = _validate_bounding_box(location["bounding_box"], "the bounding_box locator")
        if isinstance(box, str):
            return _unresolved(location, extraction_method, box)
        return ValidatedBoundingBoxLocation(kind=kind, bounding_box=box)
    # kind is LocatorKind.VECTOR_OBJECT
    if method is not ExtractionMethod.VECTOR_OBJECT_EXTRACTION:
        return _unresolved(
            location,
            extraction_method,
            (
                "a 'vector_object' locator is meaningful only for the vector-object "
                f"extraction path; extraction_method {extraction_method!r} cannot have "
                "produced a stable content-object reference, so this pairing is "
                "contradictory location evidence"
            ),
        )
    if "object_reference" not in location:
        return _unresolved(
            location,
            extraction_method,
            (
                "a 'vector_object' locator requires object_reference; a missing "
                "reference is never defaulted or reconstructed"
            ),
        )
    reference = location["object_reference"]
    if not isinstance(reference, str) or not reference.strip():
        return _unresolved(
            location,
            extraction_method,
            (
                "object_reference must be a non-empty string naming a stable vector "
                f"content object of the stored immutable original, got {reference!r} — "
                "never coerced, trimmed into existence, or reconstructed"
            ),
        )
    display_box: ValidatedBoundingBox | None = None
    if "bounding_box" in location:
        box = _validate_bounding_box(location["bounding_box"], "the display bounding_box")
        if isinstance(box, str):
            return _unresolved(location, extraction_method, box)
        display_box = box
    return ValidatedVectorObjectLocation(
        kind=kind, object_reference=reference, display_bounding_box=display_box
    )
