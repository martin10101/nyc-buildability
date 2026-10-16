"""The architect-entered-fact request channel (task M5-T178; directive D-094-R103, R285).

ONE responsibility: turn the results request's optional ``entered_facts`` block - an
architect's SURVEY measurement of a lot value (area, frontage or depth) - into
contract-valid ``survey_entered`` site facts merged BESIDE the city fact in a study, so
the already-accepted labelled-input channel (:mod:`app.contracts.evaluator_inputs`)
chooses the survey value as the governing engine input and keeps the city fact visible in
``displaced`` (never overwritten). Kept APART from the request reader
(:mod:`app.api.v1.results_request`) and the route (:mod:`app.api.v1.results_read`) so each
file keeps its own small responsibility (modularity policy).

THE CHANNEL SUPPLIES NO FACT OF ITS OWN and invents no value. Every survey fact it mints
carries the architect's number, rank ``survey_entered`` / label ``Survey (entered)``,
source kind ``survey`` (with a document reference and a plain statement), and the street +
tax lot of the EXISTING city fact it sits beside - so the two land in the SAME engine-input
group and the precedence rule (survey_entered governs, the city fact is displaced) applies
unchanged. The city fact is never edited in place (plan section 3 step 3; site_fact.schema
``editable``).

FAIL CLOSED, NEVER GUESS (CLAUDE.md principles 3 and 4; directive D-094-R285). When the lot
carries no single recorded value for an entered input - none at all, or several on different
streets or tax lots (a corner lot's two frontages) - the channel raises rather than guess
which recorded value the survey replaces: missing stays missing, a conflict stays visible.
The request reader catches a malformed block as a typed 422 at the body gate; the route maps
an unplaceable entered fact to the existing ``lot_conditions_unconfirmed`` 503 (fail safe,
nothing fabricated).

Scope of THIS increment (survey basis only): a survey value is already labelled correctly
("Survey measurements") by the accepted engine with no new wording. A plain (non-survey)
entered basis, the per-answer "rests on the architect's value" label, existing floor area and
the web wiring are named follow-ons (owner choices), deliberately out of scope here.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

__all__ = [
    "ENTERED_FACT_BASES",
    "ENTERED_FACT_INPUTS",
    "EnteredFact",
    "EnteredFactsError",
    "merge_entered_facts",
    "parse_entered_facts",
]

# Closed enum: the body ``input`` -> the site_fact key it becomes (which in turn maps to the
# engine key lot_area_sq_ft / lot_front_ft / lot_depth_ft in evaluator_inputs). CLOSED; a new
# input is added additively once its basis/label story is settled (follow-on).
_INPUT_TO_SITE_KEY = {
    "lot_area": "lot_area",
    "lot_frontage": "lot_frontage",
    "lot_depth": "lot_depth",
}

#: The lot measures an architect may enter through this channel (closed enum).
ENTERED_FACT_INPUTS: frozenset[str] = frozenset(_INPUT_TO_SITE_KEY)

#: The closed basis enum for this increment. Only a SURVEY value is admitted: the accepted
#: engine already labels a survey value "Survey measurements" with no new wording. A plain
#: ``entered`` basis needs the DB-114 status-chip wording decision (follow-on A), so it is
#: not admitted yet.
ENTERED_FACT_BASES: frozenset[str] = frozenset({"survey"})

#: The measurement block of a minted survey fact (site_fact.schema measurement_survey_entered).
_SURVEY_MEASUREMENT = {"rank": "survey_entered", "label": "Survey (entered)"}

#: The plain statement every minted survey fact carries (site_fact.schema source.statement).
_SURVEY_STATEMENT = (
    "Survey measurement entered by the architect; it governs this lot value and the city "
    "record it replaces stays visible."
)
#: The survey document reference (site_fact.schema requires a non-null document_ref for a
#: survey source). The architect entry is the reference until a survey reader (follow-on E)
#: supplies a document id.
_SURVEY_DOCUMENT_REF = "architect-entered survey (M5-T178)"


class EnteredFactsError(Exception):
    """An ``entered_facts`` block was malformed, or an entered survey value could not be placed
    beside a single recorded value for its input. Carries a bounded ``code``, a plain
    ``message`` and the offending ``field`` so the request reader can raise a typed 422 at the
    body gate and the route can map an unplaceable fact to a bounded 503. The message names the
    offending field/input (from the closed vocabulary) but never echoes a free-text caller
    value."""

    def __init__(self, code: str, message: str, *, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field


@dataclass(frozen=True)
class EnteredFact:
    """One checked architect-entered survey fact: which lot measure (closed ``input`` enum), the
    positive finite ``value``, and the ``basis`` (``survey`` only in this increment)."""

    input: str
    value: float
    basis: str


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def parse_entered_facts(raw: object) -> tuple[EnteredFact, ...]:
    """Validate the body's ``entered_facts`` block and return the checked facts.

    ``raw`` is the value of ``body["entered_facts"]`` (the caller tests presence with ``in``
    before calling, so an absent channel never reaches here). ``None`` or an empty list means
    the channel carries nothing and returns ``()`` (byte-identical to no channel). Otherwise it
    must be a list of objects ``{input, value, basis}``: ``input`` in the closed enum
    {lot_area, lot_frontage, lot_depth}; ``value`` a finite number > 0 (NaN/Infinity/<=0 are
    refused exactly as floor_to_floor_ft); ``basis`` the closed enum {survey}. A duplicate
    ``input`` is refused (a same-input conflict is made visible, never a silent pick). Raises
    :class:`EnteredFactsError` (a typed 422 at the body gate); the message names the offending
    field/input but never echoes a free-text caller value."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise EnteredFactsError(
            "entered_facts_invalid",
            "entered_facts must be a list of architect-entered survey facts",
            field="entered_facts",
        )

    facts: list[EnteredFact] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise EnteredFactsError(
                "entered_fact_invalid",
                "each entered fact must be an object carrying an input, a value and a basis",
                field="entered_facts",
            )
        extra = sorted(set(item) - {"input", "value", "basis"})
        if extra:
            raise EnteredFactsError(
                "entered_fact_field_not_accepted",
                "an entered fact carries only an input, a value and a basis",
                field=extra[0],
            )

        measure = item.get("input")
        if not isinstance(measure, str) or measure not in ENTERED_FACT_INPUTS:
            raise EnteredFactsError(
                "entered_fact_input_invalid",
                "the entered fact's input must be one of the lot measures this channel "
                "accepts: a lot area, a lot frontage or a lot depth",
                field="input",
            )

        basis = item.get("basis")
        if not isinstance(basis, str) or basis not in ENTERED_FACT_BASES:
            raise EnteredFactsError(
                "entered_fact_basis_invalid",
                "the entered fact's basis must be 'survey'; only a survey measurement is "
                "accepted through this channel yet",
                field="basis",
            )

        # Presence of value is tested with ``in`` (never a truthiness test) so a present 0 is a
        # value that is then refused, not an absent field. NaN/Infinity (JSON tokens the parser
        # admits) and non-positive values are refused, mirroring floor_to_floor_ft.
        if "value" not in item:
            raise EnteredFactsError(
                "entered_fact_value_invalid",
                "the entered fact must carry a value (a positive, finite number)",
                field="value",
            )
        value = item["value"]
        if not _is_number(value) or not math.isfinite(value) or value <= 0:
            raise EnteredFactsError(
                "entered_fact_value_invalid",
                "the entered fact's value must be a positive, finite number",
                field="value",
            )

        if measure in seen:
            raise EnteredFactsError(
                "entered_fact_duplicate_input",
                f"the lot measure {measure!r} is entered more than once; enter one survey "
                "value per lot measure so the value that governs is unambiguous",
                field="input",
            )
        seen.add(measure)
        facts.append(EnteredFact(input=measure, value=float(value), basis=basis))

    return tuple(facts)


def _survey_fact(
    *, site_key: str, value: float, street: str | None, lot_bbl: object, retrieved_at: str
) -> dict:
    """Mint ONE contract-valid ``survey_entered`` site fact (site_fact.schema.json) for one
    entered survey value. It sits beside the city fact (same ``street`` and ``lot_bbl``), so
    build_evaluator_inputs groups them together and the survey value governs."""
    unit = "square_feet" if site_key == "lot_area" else "feet"
    fact_id = f"{lot_bbl}:{site_key}"
    if street:
        fact_id = f"{fact_id}:{street}"
    fact_id = f"{fact_id}:survey_entered"
    return {
        "contract_version": "1.0.0",
        "fact_id": fact_id,
        "key": site_key,
        "lot_bbl": lot_bbl,
        "street": street,
        "value": value,
        "unit": unit,
        "measurement": dict(_SURVEY_MEASUREMENT),
        "source": {
            "kind": "survey",
            "dataset": None,
            "dataset_version": None,
            "retrieved_at": retrieved_at,
            "query_ref": None,
            "document_ref": _SURVEY_DOCUMENT_REF,
            "statement": _SURVEY_STATEMENT,
        },
        "blocks": [],
        "editable": True,
    }


def merge_entered_facts(
    study: dict, entered_facts: tuple[EnteredFact, ...], *, retrieved_at: str
) -> dict:
    """Return a study with a ``survey_entered`` site fact merged beside the matching city fact
    for each entered fact. Never mutates ``study``.

    When ``entered_facts`` is empty the SAME ``study`` object is returned unchanged (the
    no-channel path is byte-identical to today). Otherwise, for each entered fact, the study's
    KNOWN facts for that input are grouped by (street, tax lot); the survey fact is minted with
    that group's street and tax lot so it joins the group and governs. Raises
    :class:`EnteredFactsError` (fail closed) when the input has no single recorded group to sit
    beside: zero recorded values (nothing to replace), or several on different streets or tax
    lots (which recorded value the survey replaces is not settled - a corner lot's two
    frontages). ``retrieved_at`` is the RFC3339 time the value was entered (the caller mints it,
    so nothing is invented here)."""
    if not entered_facts:
        return study

    merged = copy.deepcopy(study)
    facts = merged["site"]["facts"]
    for entered in entered_facts:
        site_key = _INPUT_TO_SITE_KEY[entered.input]
        groups: dict[tuple[object, object], dict] = {}
        for fact in facts:
            if fact["key"] == site_key and fact["measurement"]["rank"] != "unknown":
                groups.setdefault((fact["street"], fact["lot_bbl"]), fact)
        if len(groups) != 1:
            raise EnteredFactsError(
                "entered_fact_not_placeable",
                f"the entered survey value for the {entered.input} cannot be applied: the lot "
                f"has {len(groups)} recorded value(s) for it, so which value the survey "
                "replaces is not settled. Enter the survey value on the lot's site-facts "
                "screen, where the street and tax lot are chosen.",
                field="entered_facts",
            )
        (street, lot_bbl), _city_fact = next(iter(groups.items()))
        facts.append(
            _survey_fact(
                site_key=site_key,
                value=entered.value,
                street=street,
                lot_bbl=lot_bbl,
                retrieved_at=retrieved_at,
            )
        )
    return merged
