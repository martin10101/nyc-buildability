"""Engine disclosures: the corner-lot front-lot-line assumption (R138) and the
auto-filled scope disclosures (R139) for the study-to-engine bridge (directive
D-090-R138 / R139).

Split out of :mod:`app.contracts.evaluator_inputs` (modularity): the address-street
frontage selection and the :class:`~app.scenario.three_answers.scope.ScopeInputs`
auto-fill are their own responsibility - a focused seam with explicit inputs - so
``evaluator_inputs`` keeps its single job (choose one governing value per engine
input). This module depends on neither ``evaluator_inputs`` (no import cycle) nor the
engine runtime: ``evaluator_inputs`` passes the already-resolved governing frontages
in, and this module reads only a validated ``evaluator_inputs`` document, a validated
``study`` document, and the caller flags.

R138 - corner-lot front lot line (``select_address_street_frontage``)
---------------------------------------------------------------------
A corner lot carries ONE ``lot_frontage`` fact per street, so ``lot_front_ft``
resolves to more than one distinct fact and :func:`build_evaluator_inputs` fails
closed (collapsing frontages is the combined-outline rule, out of scope). When the
study's property ADDRESS names exactly one of those streets, that frontage is
selected as the governing ``lot_front_ft`` and the choice is recorded as a DISCLOSED
ASSUMPTION: the estimate uses the address-street frontage as the front lot line, the
corner condition and the other frontage(s) are disclosed in plain English, and which
street is legally the front lot line is left to a qualified reviewer. When NO street
matches the address, or the address is absent, this returns ``None`` and the caller
keeps today's fail-closed error - a frontage is never guessed.

Street-name matching reuses the matcher's own documented normalization
(:func:`app.rules.named_street_override._collapse`: strip, collapse internal
whitespace, casefold; no abbreviation expansion), so matching stays exact, never
fuzzy. The address "names" a street when the collapsed street name appears as a
whitespace-delimited run inside the collapsed address (so "215-16 Northern Boulevard"
names "Northern Boulevard" but not "215 Place").

R139 - scope auto-fill (``build_scope_inputs``)
-----------------------------------------------
Every assumed engine input the three-answer engine USES is disclosed (D-090-R119).
This builds the full :class:`ScopeInputs` from the bridge's own data: the lot's BBL
and, for each of the twelve assumed keys, a :class:`DisclosedAssumption` whose BASIS is
HONEST - it comes from the governing record's rank where the value is a sourced fact
(zoning district, lot type, frontage, depth), from the study's recorded commercial
overlay for ``overlay_present``, and is ``assumed`` / ``default`` only for the engine
defaults and the caller's assumed flags. No basis is ever invented: if a required
disclosure cannot be derived (a required engine input is missing), it fails closed with
:class:`EngineDisclosureError` naming the key. The assumption VALUES are not set here -
the engine reads each value from the real generator inputs (see
``three_answers/scope.py``); this module supplies only the basis and the plain-English
statement.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.rules.named_street_override import _collapse
from app.scenario.three_answers.scope import (
    ASSUMPTION_KEYS,
    DisclosedAssumption,
    ScopeInputs,
)

__all__ = [
    "EngineDisclosureError",
    "FrontageSelection",
    "build_scope_inputs",
    "select_address_street_frontage",
]

# A resolved frontage: the governing lot_frontage fact for one street and the facts it
# displaced (same-street overrides). Produced by evaluator_inputs._resolve_group and
# passed in, so this module never re-implements the source-order precedence.
ResolvedFrontage = tuple[dict, list[dict]]

# The site_fact key carrying the recorded commercial overlay (study.schema.json site
# facts); its presence as a KNOWN fact is what makes overlay_present a recorded value
# rather than an assumption.
_COMMERCIAL_OVERLAY_KEY = "commercial_overlay"

# Plain-words housing-program labels (study.schema.json housing_program vocabulary,
# mirroring apps/web). standard_residence is the app default; any other program is a
# deliberate selection, disclosed honestly as such.
_HOUSING_PROGRAM_DISPLAY = {
    "standard_residence": "Standard residence",
    "qualifying_affordable_housing": "Qualifying affordable housing",
    "qualifying_senior_housing": "Qualifying senior housing",
}


class EngineDisclosureError(Exception):
    """A scope disclosure could not be derived from the bridge's data. Raised
    server-side (fail closed): a required engine input with no governing record, or a
    missing lot identity, is surfaced with the key named, never papered over with an
    invented basis."""


@dataclass(frozen=True)
class FrontageSelection:
    """The outcome of the R138 address-street selection: the governing frontage fact
    for the address street, the facts it displaces (same-street overrides), and the
    OTHER streets' governing frontage facts (disclosed, never used as the front)."""

    governing: dict
    displaced: list[dict]
    others: tuple[dict, ...]


def _address_names_street(address: object, street: object) -> bool:
    """True when the property ``address`` names ``street`` under the matcher's
    documented normalization: the collapsed street name appears as a
    whitespace-delimited run inside the collapsed address. Empty inputs never match."""
    collapsed_street = _collapse(street)
    if not collapsed_street:
        return False
    padded_address = f" {_collapse(address)} "
    return f" {collapsed_street} " in padded_address


def select_address_street_frontage(
    address: object, resolved_frontages: Sequence[ResolvedFrontage]
) -> FrontageSelection | None:
    """Select the governing ``lot_front_ft`` frontage when the property ``address``
    names exactly one of the resolved frontages' streets; otherwise ``None``.

    ``resolved_frontages`` is the already-resolved governing frontage per street
    (``(governing_fact, displaced)`` from ``evaluator_inputs._resolve_group``). Returns
    a :class:`FrontageSelection` only when EXACTLY ONE street matches the address (never
    a guess: zero or two matches, or an absent address, give ``None``)."""
    matches = [
        frontage
        for frontage in resolved_frontages
        if _address_names_street(address, frontage[0].get("street"))
    ]
    if len(matches) != 1:
        return None
    governing, displaced = matches[0]
    others = tuple(
        frontage[0] for frontage in resolved_frontages if frontage is not matches[0]
    )
    return FrontageSelection(governing=governing, displaced=list(displaced), others=others)


def _record_by_key(evaluator_inputs: dict) -> dict[str, dict]:
    return {record["key"]: record for record in evaluator_inputs["inputs"]}


def _require_record(by_key: dict[str, dict], key: str) -> dict:
    record = by_key.get(key)
    if record is None:
        raise EngineDisclosureError(
            f"cannot disclose assumed input {key!r}: it has no governing record in the "
            "evaluator inputs, so its basis cannot be derived (never invented)."
        )
    return record


def _known_fact(study: dict, key: str) -> dict | None:
    """The one KNOWN site fact for ``key`` (rank != unknown), or None. Used for
    overlay_present, whose basis depends on whether the overlay is recorded."""
    known = [
        fact
        for fact in study["site"]["facts"]
        if fact["key"] == key and fact["measurement"]["rank"] != "unknown"
    ]
    return sorted(known, key=lambda f: f["fact_id"])[0] if known else None


def _front_lot_line_statement(front: dict, others: Sequence[dict]) -> str:
    """The R138 disclosed-assumption statement for a corner lot whose front lot line is
    assumed to be the address-street frontage. ``front`` is the governing frontage fact;
    ``others`` are the remaining streets' governing frontage facts, disclosed with their
    measured lengths."""
    other_text = "; ".join(
        f"{fact['street']} {float(fact['value']):g} ft" for fact in others
    )
    return (
        f"Front lot line assumed to be the {front['street']} frontage (the address "
        f"street); the lot is a corner lot with two frontages ({other_text}); which "
        "street is legally the front lot line is a qualified-review question."
    )


def _frontage_disclosure(
    front_record: dict, resolved_frontages: Sequence[ResolvedFrontage], address: object
) -> DisclosedAssumption:
    """The lot_front_ft disclosure. On a corner lot (more than one frontage) whose
    address street was selected, it carries the R138 front-lot-line statement; on a
    single-frontage lot it is an honest sourced-frontage statement. The basis is always
    the governing frontage record's own rank (never invented)."""
    basis = front_record["rank"]
    if len(resolved_frontages) > 1:
        selection = select_address_street_frontage(address, resolved_frontages)
        if selection is None:
            raise EngineDisclosureError(
                "cannot disclose assumed input 'lot_front_ft': the lot has several "
                "frontages but the address street selected none, so the front lot line "
                "is undetermined (never guessed)."
            )
        return DisclosedAssumption(
            basis=basis,
            statement=_front_lot_line_statement(selection.governing, selection.others),
        )
    value = float(front_record["value"])
    return DisclosedAssumption(
        basis=basis,
        statement=(
            f"The lot frontage of {value:g} feet comes from the lot's recorded "
            "measurement; it is used as the front lot line."
        ),
    )


def _overlay_disclosure(study: dict, overlay_present: bool) -> DisclosedAssumption:
    """overlay_present: the statement ALWAYS follows the actual flag value, and a recorded
    commercial_overlay fact must AGREE with it. When a fact is recorded (basis = its own
    record rank, city data) a recorded overlay (non-null value) requires the flag true and
    the statement names it, while a recorded 'none' (null value) requires the flag false. A
    flag that disagrees fails closed naming the key (never a silent override; CLAUDE.md
    principle 4). With no recorded fact the statement follows the flag with basis 'assumed'."""
    overlay = _known_fact(study, _COMMERCIAL_OVERLAY_KEY)
    if overlay is not None:
        fact_present = overlay["value"] is not None
        if fact_present != overlay_present:
            raise EngineDisclosureError(
                "cannot disclose assumed input 'overlay_present': the caller flag "
                f"({overlay_present}) disagrees with the recorded commercial_overlay fact "
                f"(records {'an overlay' if fact_present else 'none'}); resolve the conflict "
                "(never a silent override)."
            )
        statement = (
            f"A commercial overlay ({overlay['value']}) is recorded for this lot in city data."
            if fact_present
            else "No commercial overlay is recorded for this lot in city data."
        )
        return DisclosedAssumption(basis=overlay["measurement"]["rank"], statement=statement)
    return DisclosedAssumption(
        basis="assumed",
        statement=(
            "A commercial overlay is assumed to apply; none is recorded for this lot."
            if overlay_present
            else "No commercial overlay is assumed to apply; none is recorded for this lot."
        ),
    )


def _housing_program_disclosure(housing_program: str) -> DisclosedAssumption:
    """housing_program: standard_residence is the app default (basis default); any other
    program was deliberately selected (basis entered), disclosed as such."""
    display = _HOUSING_PROGRAM_DISPLAY.get(housing_program, housing_program)
    if housing_program == "standard_residence":
        return DisclosedAssumption(
            basis="default",
            statement="Standard residence is used as the default housing program.",
        )
    return DisclosedAssumption(
        basis="entered",
        statement=f"{display} was selected as the housing program.",
    )


def _assumed_flag_disclosure(
    present: bool, present_statement: str, absent_statement: str
) -> DisclosedAssumption:
    """An assumed boolean-flag disclosure whose statement follows the ACTUAL value: the
    present wording when the flag is true, the absent wording when false, so the statement
    can never disagree with the row's emitted value. Basis is always ``assumed`` - this run
    reads no layer for these flags; they are caller-supplied assumptions."""
    return DisclosedAssumption(
        basis="assumed",
        statement=present_statement if present else absent_statement,
    )


def build_scope_inputs(
    evaluator_inputs: dict,
    study: dict,
    *,
    resolved_frontages: Sequence[ResolvedFrontage],
    housing_program: str,
    overlay_present: bool,
    special_district_present: bool,
    special_density_area: bool,
    within_100_ft_of_street_line_intersection: bool,
    street_line_intersection_angle_degrees: float,
    floor_to_floor_ft: float,
) -> ScopeInputs:
    """Build the full :class:`ScopeInputs` for one option from the bridge's own data
    (R139). Every assumed engine input the engine uses is disclosed once, with an HONEST
    basis: the governing record's rank for the sourced facts (zoning district, lot type,
    frontage, depth), the recorded commercial overlay for ``overlay_present``, and
    ``assumed`` / ``default`` (or ``entered``) for the engine defaults and caller flags.
    The lot's BBL identifies the lot; the engine derives the lot display from it.

    Every flag-derived row's STATEMENT follows the actual value passed to the engine, so a
    disclosure can never disagree with the row it describes (``overlay_present``,
    ``special_district_present``, ``special_density_area``,
    ``within_100_ft_of_street_line_intersection``). For ``overlay_present`` the caller flag
    must additionally agree with any recorded commercial_overlay fact (DB-126).

    ``resolved_frontages`` is the per-street governing frontage (from
    ``evaluator_inputs._resolve_group``); it decides whether lot_front_ft carries the
    R138 corner statement. Raises :class:`EngineDisclosureError` naming the key when a
    required disclosure cannot be derived (a missing governing record or lot identity), or
    when ``overlay_present`` contradicts the recorded commercial_overlay fact."""
    property_obj = study.get("property")
    if not isinstance(property_obj, dict) or not property_obj.get("bbl"):
        raise EngineDisclosureError(
            "cannot build scope disclosures: the study has no property BBL to identify "
            "the lot."
        )
    by_key = _record_by_key(evaluator_inputs)
    zoning = _require_record(by_key, "zoning_district")
    lot_type = _require_record(by_key, "lot_type")
    front = _require_record(by_key, "lot_front_ft")
    depth = _require_record(by_key, "lot_depth_ft")
    angle = float(street_line_intersection_angle_degrees)

    disclosures = {
        "zoning_district": DisclosedAssumption(
            basis=zoning["rank"],
            statement=(
                f"Zoning district {zoning['value']} is read from recorded city data."
            ),
        ),
        "overlay_present": _overlay_disclosure(study, overlay_present),
        "special_district_present": _assumed_flag_disclosure(
            special_district_present,
            "A special purpose district is assumed to apply; this run does not read the "
            "special-district layer.",
            "No special purpose district is assumed to apply; this run does not read the "
            "special-district layer.",
        ),
        "special_density_area": _assumed_flag_disclosure(
            special_density_area,
            "The lot is assumed to lie in a special density area; this run does not read "
            "the special-density layer.",
            "The lot is assumed not to lie in a special density area; this run does not "
            "read the special-density layer.",
        ),
        "lot_type": DisclosedAssumption(
            basis=lot_type["rank"],
            statement=(
                f"The lot type ({lot_type['value']}) is read from the approximate city "
                "tax-map outline."
            ),
        ),
        "lot_front_ft": _frontage_disclosure(
            front, resolved_frontages, property_obj.get("address")
        ),
        "lot_depth_ft": DisclosedAssumption(
            basis=depth["rank"],
            statement=(
                f"The lot depth of {float(depth['value']):g} feet is read from recorded "
                "city data."
            ),
        ),
        "site_measurement_rank": DisclosedAssumption(
            basis="default",
            statement=(
                "The results carry the label of their weakest input; no survey or "
                "entered measurement was supplied, so the weakest recorded source sets "
                "the label."
            ),
        ),
        "within_100_ft_of_street_line_intersection": _assumed_flag_disclosure(
            within_100_ft_of_street_line_intersection,
            "The lot is assumed to lie within 100 feet of a street-line intersection.",
            "The lot is assumed not to lie within 100 feet of a street-line intersection.",
        ),
        "street_line_intersection_angle_degrees": DisclosedAssumption(
            basis="assumed",
            statement=f"The street lines are assumed to meet at a {angle:g}-degree angle.",
        ),
        "housing_program": _housing_program_disclosure(housing_program),
        "floor_to_floor_ft": DisclosedAssumption(
            basis="default",
            statement=(
                f"A {float(floor_to_floor_ft):g}-foot floor-to-floor height is used as "
                "the default."
            ),
        ),
    }
    # The disclosure set must be exactly the emitter's assumed-key set: a drift (a new
    # assumed input, or a typo) fails closed here rather than at ScopeInputs construction.
    if set(disclosures) != set(ASSUMPTION_KEYS):
        missing = sorted(set(ASSUMPTION_KEYS) - set(disclosures))
        extra = sorted(set(disclosures) - set(ASSUMPTION_KEYS))
        raise EngineDisclosureError(
            f"scope disclosures do not match the emitter's assumed keys "
            f"(missing={missing}, extra={extra})."
        )
    return ScopeInputs(bbl=property_obj["bbl"], **disclosures)
