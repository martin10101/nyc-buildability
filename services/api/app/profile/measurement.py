"""Measurement ranks, their labels, and the weakest-input label (queue item B-02).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md``:

- task M1-07: "Input statuses: survey, city records, approximate, entered, assumed,
  unknown" - done when "Every input shows its status and source";
- section 4 source order: survey (entered) > city records > approximate - tax map >
  unknown, and "Each result carries the label of its weakest input".

The six ranks and their labels are the ``measurement`` vocabulary of the site_fact v1
contract (``packages/contracts/schemas/v1/site_fact.schema.json`` ``$defs``), copied
exactly; a test pins this module to the schema so they cannot drift apart.

Weakest-input ORDER used here (strongest first):

    survey_entered > city_records > approximate_tax_map > entered > assumed > unknown

The first three and ``unknown`` are the plan section 4 order. The plan does not place
``entered`` (typed by the architect, not from a survey) or ``assumed`` (a stated
assumption). They sit below every documented source so a result's label never
overstates its inputs, and ``assumed`` is the weakest known rank because the results
contract counts the assumed width of a "Needs street width" case as an 'assumed' input
(``results.schema.json`` street_width_case): the case must then read "Assumed" whatever
its other inputs are. This placement is a conservative default recorded for owner
confirmation (B-02 report), not a plan decision.

An answer whose weakest input is unknown is not available (``site_fact.schema.json``
``measurement_known``): :func:`answer_measurement` returns ``None`` for it.

Pure, deterministic code: no I/O, no legal logic.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Any

__all__ = [
    "MEASUREMENT_LABELS",
    "MEASUREMENT_ORDER",
    "RANK_APPROXIMATE_TAX_MAP",
    "RANK_ASSUMED",
    "RANK_CITY_RECORDS",
    "RANK_ENTERED",
    "RANK_SURVEY_ENTERED",
    "RANK_UNKNOWN",
    "answer_measurement",
    "measurement",
    "weakest_measurement",
]

RANK_SURVEY_ENTERED = "survey_entered"
RANK_CITY_RECORDS = "city_records"
RANK_APPROXIMATE_TAX_MAP = "approximate_tax_map"
RANK_ENTERED = "entered"
RANK_ASSUMED = "assumed"
RANK_UNKNOWN = "unknown"

# Rank -> display label (site_fact.schema.json $defs measurement_*: ranks 1-3 and
# 'unknown' are the plan section 4 wording; 'Entered' / 'Assumed' are the M1-07 names).
MEASUREMENT_LABELS: Mapping[str, str] = MappingProxyType({
    RANK_SURVEY_ENTERED: "Survey (entered)",
    RANK_CITY_RECORDS: "City records",
    RANK_APPROXIMATE_TAX_MAP: "Approximate — tax map",
    RANK_ENTERED: "Entered",
    RANK_ASSUMED: "Assumed",
    RANK_UNKNOWN: "Unknown — enter",
})

# Strongest first; the LAST rank present among a result's inputs is its label.
MEASUREMENT_ORDER: tuple[str, ...] = (
    RANK_SURVEY_ENTERED,
    RANK_CITY_RECORDS,
    RANK_APPROXIMATE_TAX_MAP,
    RANK_ENTERED,
    RANK_ASSUMED,
    RANK_UNKNOWN,
)


def measurement(rank: str) -> dict[str, str]:
    """The contract ``measurement`` object for ``rank``: ``{"rank", "label"}``.

    Raises:
        ValueError: ``rank`` is not one of the six ranks (never coerced).
    """
    if rank not in MEASUREMENT_LABELS:
        raise ValueError(
            f"unknown measurement rank {rank!r}; expected one of {list(MEASUREMENT_ORDER)}"
        )
    return {"rank": rank, "label": MEASUREMENT_LABELS[rank]}


def _rank_of(item: Any) -> str:
    """Rank of one input: a site_fact document, a measurement object, or a rank string.

    A measurement whose label does not belong to its rank is rejected, so a mislabeled
    input can never pass through as a stronger one."""
    if isinstance(item, str):
        rank = item
        label = None
    elif isinstance(item, Mapping):
        block = item.get("measurement", item)
        if not isinstance(block, Mapping):
            raise ValueError("input carries no measurement object")
        rank = block.get("rank")
        label = block.get("label")
    else:
        raise ValueError(
            f"cannot read a measurement rank from a {type(item).__name__}; pass a "
            "site_fact, a measurement object or a rank string"
        )
    if not isinstance(rank, str) or rank not in MEASUREMENT_LABELS:
        raise ValueError(
            f"unknown measurement rank {rank!r}; expected one of {list(MEASUREMENT_ORDER)}"
        )
    if label is not None and label != MEASUREMENT_LABELS[rank]:
        raise ValueError(
            f"measurement label {label!r} does not match rank {rank!r} "
            f"(expected {MEASUREMENT_LABELS[rank]!r})"
        )
    return rank


def weakest_measurement(inputs: Iterable[Any]) -> dict[str, str]:
    """The measurement of the weakest input (plan section 4 "How labels carry through").

    ``inputs`` holds site_fact documents, measurement objects or rank strings. An
    ``unknown`` input makes the result ``unknown``.

    Raises:
        ValueError: no inputs (a result with no inputs has no label), or an input with
            an unknown rank or a label that does not match its rank.
    """
    ranks = [_rank_of(item) for item in inputs]
    if not ranks:
        raise ValueError("no inputs: a result must name the inputs its label comes from")
    return measurement(max(ranks, key=MEASUREMENT_ORDER.index))


def answer_measurement(inputs: Iterable[Any]) -> dict[str, str] | None:
    """The label an available answer carries (results ``measurement_known``), or
    ``None`` when its weakest input is unknown - the answer is then not available and
    the caller shows the reason instead of a number (plan section 5a item 3)."""
    weakest = weakest_measurement(inputs)
    return None if weakest["rank"] == RANK_UNKNOWN else weakest
