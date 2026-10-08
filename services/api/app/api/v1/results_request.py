"""Read and check the small caller body of the internal results route (task M5-T138).

Kept APART from the route (``app.api.v1.results_read``) so the route file stays small: this
module's one job is to validate the caller's body and turn it into ONE study option document.
It supplies NO fact and NO condition of the lot (R6B work order rule 1; D-090-R255). The route
sources every lot fact and every lot condition from the server-held evidence; the body carries
only the user's OPTION choices.

THE BODY CARRIES ONLY (R3 of the orchestrator's rulings; work order section 4 item 2):

* ``housing_program`` - the closed vocabulary the engine accepts
  (``standard_residence`` | ``qualifying_affordable_housing`` | ``qualifying_senior_housing``);
  REQUIRED, since the engine needs it to pick the floor-area and dwelling-unit rules.
* ``floor_to_floor_ft`` - OPTIONAL. A design choice (a visible, editable starting value, work
  order rule 2). When ABSENT the engine's stated starting value is used and is printed in the
  result; never a hidden default. A present value must be a positive number.
* ``special_density_statement`` - OPTIONAL. The user's statement about the special density area:
  a boolean (``true`` = the lot is NOT in a special density area, the one statement the program
  acts on), or absent (no statement). It is a STATEMENT, never a recorded fact, and the route
  never stores it or returns it as a fact (R255).

ANY OTHER FIELD IS REFUSED with a typed 422 (R3): so no lot area, frontage, depth, lot type,
district, overlay, special district, corner condition, geometry or attested fact can be sent
through this body. Every refusal names the offending field; no message echoes a caller value.

No truthiness test is run on a value that MAY be absent: presence is tested with ``in`` and the
type checked explicitly, so an absent optional value is distinct from a present ``0``/``false``.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.scenario.three_answers import DEFAULT_FLOOR_TO_FLOOR_FT

__all__ = [
    "ALLOWED_BODY_FIELDS",
    "HOUSING_PROGRAMS",
    "OPTION_NAME",
    "ResultsRequest",
    "ResultsRequestError",
    "build_option",
    "read_results_request",
]

#: The closed housing-program vocabulary the engine accepts (ThreeAnswerInputs.housing_program).
HOUSING_PROGRAMS: frozenset[str] = frozenset(
    {"standard_residence", "qualifying_affordable_housing", "qualifying_senior_housing"}
)

#: The ONLY fields the body may carry. Any other key is refused (R3).
ALLOWED_BODY_FIELDS: frozenset[str] = frozenset(
    {"housing_program", "floor_to_floor_ft", "special_density_statement"}
)

#: The neutral display name for the minted option (not a fact about the lot; R2). The route
#: returns only the results document (option_id, not name), so this is an internal, plain label.
OPTION_NAME = "Requested option"

# The option's `program` is the user's housing choice expressed in the option schema's own
# vocabulary (study.schema.json #/$defs/option `program`). It is NOT read by the engine (the
# engine reads `housing_program` directly); this correspondence keeps the option document a true
# record of the user's choice without inventing any lot fact. Smallest valid value: one entry.
_OPTION_PROGRAM_BY_HOUSING_PROGRAM = {
    "standard_residence": "market_rate_residential",
    "qualifying_affordable_housing": "affordable_residential",
    "qualifying_senior_housing": "senior_residential",
}


class ResultsRequestError(Exception):
    """The caller body is malformed or carries a field the route does not accept. Carries a
    bounded ``code``, a plain ``message`` and the offending ``field`` for a typed 422. The route
    maps this to ``(422, validation_error)``; the message never echoes a caller value."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field


@dataclass(frozen=True)
class ResultsRequest:
    """The checked body: the user's option choices only. ``floor_to_floor_ft`` is None when the
    user supplied none (the engine's stated starting value is used and printed);
    ``special_density_statement`` is None when the user made no statement."""

    housing_program: str
    floor_to_floor_ft: float | None
    special_density_statement: bool | None


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def read_results_request(body: object) -> ResultsRequest:
    """Validate the caller body and return the checked :class:`ResultsRequest`.

    Raises :class:`ResultsRequestError` when the body is not an object, carries any field beyond
    the three allowed, is missing the housing program, or carries a malformed value for one of
    the three. Presence of each optional value is tested with ``in`` (never a truthiness test),
    so an absent value is never confused with a present ``0`` or ``false``."""
    if not isinstance(body, dict):
        raise ResultsRequestError(
            "invalid_body", "the request body must be a JSON object"
        )

    extra = sorted(set(body) - ALLOWED_BODY_FIELDS)
    if extra:
        field = extra[0]
        raise ResultsRequestError(
            "field_not_accepted",
            "this field is not accepted; the request carries only the housing program, an "
            "optional floor-to-floor height and an optional statement about the special "
            "density area. Facts about the lot come from the city's records, not the request",
            field=field,
        )

    if "housing_program" not in body:
        raise ResultsRequestError(
            "housing_program_required",
            "a housing program is required",
            field="housing_program",
        )
    housing_program = body["housing_program"]
    if housing_program not in HOUSING_PROGRAMS:
        raise ResultsRequestError(
            "housing_program_invalid",
            "the housing program is not one the program offers",
            field="housing_program",
        )

    floor_to_floor_ft: float | None = None
    if "floor_to_floor_ft" in body:
        raw = body["floor_to_floor_ft"]
        if not _is_number(raw) or raw <= 0:
            raise ResultsRequestError(
                "floor_to_floor_ft_invalid",
                "the floor-to-floor height must be a positive number of feet",
                field="floor_to_floor_ft",
            )
        floor_to_floor_ft = float(raw)

    special_density_statement: bool | None = None
    if "special_density_statement" in body:
        raw = body["special_density_statement"]
        if not isinstance(raw, bool):
            raise ResultsRequestError(
                "special_density_statement_invalid",
                "the statement about the special density area must be true or false",
                field="special_density_statement",
            )
        special_density_statement = raw

    return ResultsRequest(
        housing_program=housing_program,
        floor_to_floor_ft=floor_to_floor_ft,
        special_density_statement=special_density_statement,
    )


def _floor_to_floor_heights(request: ResultsRequest) -> dict:
    """The option's floor_to_floor_heights, built from the user's choice. When the user supplied
    a height the basis is ``entered``; when absent the engine's stated starting value is used
    with basis ``stated_default`` (a default is always stated in words, never silently applied).
    The engine reads the height from the building defaults, not from this block; this block keeps
    the option document a true record of the user's choice."""
    if request.floor_to_floor_ft is not None:
        height = request.floor_to_floor_ft
        basis = "entered"
        statement = f"Floor-to-floor height {height:g} ft (entered)."
    else:
        height = float(DEFAULT_FLOOR_TO_FLOOR_FT)
        basis = "stated_default"
        statement = f"Floor-to-floor height {height:g} ft (stated default; editable)."
    setting = {"height_ft": height, "basis": basis, "statement": statement}
    return {
        "ground_floor": dict(setting),
        "typical_floor": dict(setting),
        "per_floor_overrides": [],
    }


def build_option(request: ResultsRequest, *, option_id: str) -> dict:
    """Build ONE study option document (study.schema.json #/$defs/option) from the checked body.

    The housing program and the floor-to-floor height are the user's; every other field takes the
    smallest valid neutral value (nothing selected, no add-on, the schema's default goal, no
    existing building). NO field is a fact about the lot (R2). ``option_id`` is minted by the
    route; the engine reads the housing program from the route's call, not from ``program``."""
    return {
        "option_id": option_id,
        "name": OPTION_NAME,
        "addon_selection": [],
        "goal": {"kind": "most_residential_floor_area", "text": None},
        "program": [_OPTION_PROGRAM_BY_HOUSING_PROGRAM[request.housing_program]],
        "floor_to_floor_heights": _floor_to_floor_heights(request),
        "assumptions": [],
        "existing_building_plan": "no_existing_building",
    }
