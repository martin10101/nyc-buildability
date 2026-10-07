"""The recorded city-record columns as sourced three-state facts (task M5-T130, Part 0 of
docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md).

This module gathers, from the SAME built property profile that
``app.profile.hidden_issue_flags.map_based_rules`` reads, the recorded PLUTO map-based columns
the merged decision module (:mod:`result_ways`) needs, each as a three-state ``Recorded`` fact
with its provenance. It reuses the one shared reader
(:func:`app.profile.site_facts.read_pluto_value`) and changes no existing file.

READING O14 (the orchestrator's, to be confirmed or corrected by the reviewers). "Recorded as
absent" and "not read" are told apart from the connector's own record of the fetch, which the
property profile carries through:

* The PLUTO connector (:mod:`app.connectors.pluto_soda`) asks for the whole record (no column
  projection) and records, in ``absent_columns``, every one of its 108 known columns the served
  row omitted (SODA's null-omission rule). The profile builder carries those omissions into the
  profile, and the shared reader surfaces a served-empty column as
  ``(None, <the PLUTO fetch's source>, "PLUTO has no <column> value for this lot.")`` - the
  source is the recorded fetch, present ONLY when a PLUTO fetch is in the profile's
  reproducibility record. So a served-empty column (a fetch happened and the row omitted it) is
  told from a column that was not read (no profile, no PLUTO fetch, a failed fetch or no row,
  where the reader returns the same sentence but with NO fetch source) by whether that fetch
  source is present.
* Therefore a served-empty column is carried as ``Recorded.ABSENT`` - the user wording is that
  the city's records list none, never that the lot has none (work order gap K10). No fetch, a
  failed fetch, no row, or a present-but-untrusted value (a conflict, a duplicate or a connector
  drift signal, which is never guessed at) is carried as ``Recorded.NOT_READ``.
* ``splitzone`` is a checkbox the dataset serves explicitly as ``true``/``false`` (not omitted),
  so a served ``false`` is a real recorded "not split" and is carried as ``Recorded.ABSENT``,
  exactly as :func:`map_based_rules._split_by_district_line` reads it.

A user's statement never enters a fact record here (owner rule 1; R255): this module reads only
the city's recorded data. No value is guessed and no default stands for a fact (owner rule 1;
L1): the three states are explicit and a missing value is always carried as "not read".
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.profile.site_facts import read_pluto_value

from .result_way_inputs import Recorded

__all__ = [
    "DATASET_LABEL",
    "RecordedConditions",
    "RecordedFact",
    "gather_recorded_facts",
]

# The dataset every one of these facts comes from, in plain words (provenance, never a claim
# about the law). The connector's dataset id is carried too, from the fetch record.
DATASET_LABEL = "New York City Department of City Planning PLUTO"
_DATASET_ID = "64uk-42ks"

# The exact sentence the shared reader returns for a column the served row omitted. Tying to it
# (documented in read_pluto_value's own contract) is how a served-empty column is recognised.
def _served_empty_sentence(column: str) -> str:
    return f"PLUTO has no {column} value for this lot."


class _ColState(Enum):
    """What one PLUTO column's reading is, before a condition is decided from it."""

    VALUE = "value"            # a usable recorded value was served
    SERVED_EMPTY = "served_empty"  # a fetch happened and the row omitted this column
    NOT_FETCHED = "not_fetched"    # no profile, no PLUTO fetch, a failed fetch or no row
    UNTRUSTED = "untrusted"        # a value was served but the trust rules reject it


@dataclass(frozen=True)
class _ColReading:
    state: _ColState
    value: Any
    problem: str | None


@dataclass(frozen=True)
class RecordedFact:
    """One recorded condition, as a three-state fact with where it came from.

    ``statement`` is the plain, true sentence shown beside the results (never "the lot has
    none"); ``state`` is the three-state value the decision module consumes. The provenance is
    the dataset, the columns read, the lot's id and the fetch record (retrieved time and the
    request), so a report can trace every fact to its source.
    """

    name: str
    state: Recorded
    statement: str
    columns: tuple[str, ...]
    bbl: str | None
    dataset: str | None
    dataset_id: str | None
    dataset_version: str | None
    retrieved_at: str | None
    query_ref: str | None
    code: str | None = None
    unusable_reason: str | None = None


@dataclass(frozen=True)
class RecordedConditions:
    """Every recorded condition the decision module needs, each a three-state fact with its
    provenance. The decision module reads the ``Recorded`` states; a report reads the facts."""

    special_purpose_district: RecordedFact
    split_by_district_line: RecordedFact
    commercial_overlay: RecordedFact
    inclusionary_housing_area: RecordedFact
    flood_zone: RecordedFact
    landmark_or_historic: RecordedFact

    def facts(self) -> tuple[RecordedFact, ...]:
        return (
            self.special_purpose_district, self.split_by_district_line,
            self.commercial_overlay, self.inclusionary_housing_area,
            self.flood_zone, self.landmark_or_historic,
        )


def _bbl_of(profile: Mapping[str, Any] | None) -> str | None:
    if not isinstance(profile, Mapping):
        return None
    identity = profile.get("identity")
    return identity.get("bbl") if isinstance(identity, Mapping) else None


def _read_column(
    profile: Mapping[str, Any] | None, column: str,
) -> tuple[_ColReading, Mapping | None]:
    """Read one PLUTO column and classify it (reading O14). Returns the reading and the fetch
    source (the city_dataset provenance object, or None when nothing was read)."""
    if profile is None:
        return _ColReading(_ColState.NOT_FETCHED, None, "No property profile was read."), None
    value, source, problem = read_pluto_value(profile, column)
    if problem is None:
        return _ColReading(_ColState.VALUE, value, None), source
    if problem == _served_empty_sentence(column):
        if source is not None:
            # A PLUTO fetch happened and the served row omitted this column.
            return _ColReading(_ColState.SERVED_EMPTY, None, None), source
        # The same sentence with no fetch source means no PLUTO was read for this lot.
        return _ColReading(_ColState.NOT_FETCHED, None, "The city records were not read."), None
    # A value was served but could not be used (a conflict, a duplicate, a drift signal); it is
    # never guessed at, so the condition is treated as not read.
    return _ColReading(_ColState.UNTRUSTED, None, problem), source


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _truthy_flag(value: Any) -> bool:
    """A checkbox (``mih_opt``) counts as present only on a real true, never on False/None."""
    return value is True


def _nonzero_number(value: Any) -> bool:
    """A numeric flag (``firm07_flag``) counts as present only on a real non-zero value."""
    return value not in (None, 0, 0.0, False) and not isinstance(value, str)


def _state_from_readings(
    readings: list[tuple[_ColReading, Mapping | None]], present_of: Callable[[Any], bool],
) -> Recorded:
    """Fold the per-column readings into one three-state condition (reading O14).

    PRESENT when any column serves a usable value the condition recognises; NOT_READ when any
    column was not read or was served but unusable (never guessed); otherwise ABSENT (every
    column was served empty, or served a value that does not indicate the condition, after a
    real fetch)."""
    if any(r.state is _ColState.VALUE and present_of(r.value) for r, _ in readings):
        return Recorded.PRESENT
    if any(r.state in (_ColState.NOT_FETCHED, _ColState.UNTRUSTED) for r, _ in readings):
        return Recorded.NOT_READ
    return Recorded.ABSENT


def _first_source(readings: list[tuple[_ColReading, Mapping | None]]) -> Mapping | None:
    for _reading, source in readings:
        if source is not None:
            return source
    return None


def _code_of(
    readings: list[tuple[_ColReading, Mapping | None]], present_of: Callable[[Any], bool],
) -> str | None:
    for reading, _source in readings:
        if reading.state is _ColState.VALUE and present_of(reading.value):
            return str(reading.value)
    return None


def _unusable_reason(readings: list[tuple[_ColReading, Mapping | None]]) -> str | None:
    for reading, _source in readings:
        if reading.state is _ColState.UNTRUSTED:
            return reading.problem
    return None


# One sentence per state, per condition, in plain words that are true of the city's records -
# never "the lot has none" (reading O14), never an internal name or a claim about the law (L3).
_STATEMENTS = {
    "special_purpose_district": {
        Recorded.PRESENT: "City records record a special purpose district for this lot.",
        Recorded.ABSENT: "City records list no special purpose district for this lot.",
        Recorded.NOT_READ: "The special-purpose-district record was not read for this lot.",
    },
    "split_by_district_line": {
        Recorded.PRESENT: "City records record this lot as split by a district line.",
        Recorded.ABSENT: "City records record this lot as not split by a district line.",
        Recorded.NOT_READ: "The split-lot record was not read for this lot.",
    },
    "commercial_overlay": {
        Recorded.PRESENT: "City records record a commercial overlay for this lot.",
        Recorded.ABSENT: "City records list no commercial overlay for this lot.",
        Recorded.NOT_READ: "The commercial-overlay record was not read for this lot.",
    },
    "inclusionary_housing_area": {
        Recorded.PRESENT: "City records record an inclusionary-housing area for this lot.",
        Recorded.ABSENT: "City records list no inclusionary-housing area for this lot.",
        Recorded.NOT_READ: "The inclusionary-housing record was not read for this lot.",
    },
    "flood_zone": {
        Recorded.PRESENT: "City records record a flood zone for this lot.",
        Recorded.ABSENT: "City records list no flood zone for this lot.",
        Recorded.NOT_READ: "The flood-zone record was not read for this lot.",
    },
    "landmark_or_historic": {
        Recorded.PRESENT: "City records record a landmark or historic district for this lot.",
        Recorded.ABSENT: "City records list no landmark or historic district for this lot.",
        Recorded.NOT_READ: "The landmark / historic-district record was not read for this lot.",
    },
}


def _fact(
    name: str, columns: tuple[str, ...], present_of: Callable[[Any], bool],
    profile: Mapping[str, Any] | None, bbl: str | None, *, carry_code: bool = False,
) -> RecordedFact:
    readings = [_read_column(profile, column) for column in columns]
    state = _state_from_readings(readings, present_of)
    source = _first_source(readings)
    code = _code_of(readings, present_of) if (carry_code and state is Recorded.PRESENT) else None
    return RecordedFact(
        name=name,
        state=state,
        statement=_STATEMENTS[name][state],
        columns=columns,
        bbl=bbl,
        dataset=DATASET_LABEL if source is not None else None,
        dataset_id=_DATASET_ID if source is not None else None,
        dataset_version=source.get("dataset_version") if isinstance(source, Mapping) else None,
        retrieved_at=source.get("retrieved_at") if isinstance(source, Mapping) else None,
        query_ref=source.get("query_ref") if isinstance(source, Mapping) else None,
        code=code,
        unusable_reason=_unusable_reason(readings),
    )


def gather_recorded_facts(profile: Mapping[str, Any] | None) -> RecordedConditions:
    """Gather the recorded map-based conditions for one lot as three-state facts (reading O14).

    ``profile`` is a built property-profile document (``app.profile.builder``) for the lot, read
    and never changed; None means no profile was read, so every condition is "not read". Each
    fact carries its dataset, the columns read, the lot's id and the fetch record.
    """
    bbl = _bbl_of(profile)
    return RecordedConditions(
        special_purpose_district=_fact(
            "special_purpose_district", ("spdist1", "spdist2", "spdist3"),
            _nonempty_text, profile, bbl),
        split_by_district_line=_fact(
            "split_by_district_line", ("splitzone",), _truthy_flag, profile, bbl),
        commercial_overlay=_fact(
            "commercial_overlay", ("overlay1", "overlay2"), _nonempty_text, profile, bbl,
            carry_code=True),
        inclusionary_housing_area=_fact(
            "inclusionary_housing_area", ("mih_opt1", "mih_opt2", "mih_opt3", "mih_opt4"),
            _truthy_flag, profile, bbl),
        flood_zone=_fact(
            "flood_zone", ("firm07_flag", "pfirm15_flag"), _nonzero_number, profile, bbl),
        landmark_or_historic=_fact(
            "landmark_or_historic", ("landmark", "histdist"), _nonempty_text, profile, bbl),
    )
