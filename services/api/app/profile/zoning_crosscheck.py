"""Cross-source lot-level zoning reconciliation (task M2-T008, safeguard 6).

Compares the lot-level zoning values of the accepted PLUTO connector
(``app.connectors.pluto_soda``), the ZTLDB connector
(``app.connectors.ztldb_soda``), and optional externally-supplied
observations (e.g. values read from the accepted M2-T007 zoning-features
fixtures - FIXTURE VALUES ONLY, no spatial intersection is computed here)
for the SAME property, and emits every disagreement through the EXISTING
contract-1.3.0 conflict shape (``field`` / ``values`` / ``resolution`` /
``reason``) consumed by ``app.profile.builder``.

Hard rules:

- DATA RECONCILIATION, NOT LEGAL ADJUDICATION: no value ever wins, no
  value is ever dropped, and both observations plus their provenance are
  preserved verbatim inside the conflict entry. ``resolution`` is always
  ``unresolved`` here.
- The three presentations are three VINTAGES of the same underlying facts
  (GIS Zoning Features -> ZTLDB -> PLUTO derivation chain, research
  section 3.3); disagreement is expected vintage/coverage skew and must be
  visible, never silently smoothed over.
- Formatting-only differences (pure letter-case, observed live: PLUTO
  ``zonemap`` '16a' vs ZTLDB ``zoning_map_number`` '16A' for the same lot)
  are typed UNCERTAINTY observations, not conflicts - both verbatim values
  are still preserved and reported.
- The documented ``zmcode``/``zoning_map_code`` representation mapping
  (PLUTO checkbox true <-> ZTLDB text 'Y'; both officially flag "may be on
  the border of two or more zoning maps") is a comparison predicate only -
  neither value is rewritten.
- A value present on one side while the documented not-applicable blank
  appears on the other IS a disagreement (coverage/vintage skew) and
  becomes a typed conflict with the absence stated explicitly.

The conflict entries feed the EXISTING analysis-readiness machinery
unchanged: an unresolved conflict on a critical column (``zonedist1``)
gates ``analysis_readiness`` exactly like any other conflict (M2-T004
policy). No contract-shape change is made anywhere in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.connectors.pluto_soda import (
    DATASET_ID as PLUTO_DATASET_ID,
)
from app.connectors.pluto_soda import (
    SOURCE_ID as PLUTO_SOURCE_ID,
)
from app.connectors.pluto_soda import (
    PlutoFetchResult,
)
from app.connectors.ztldb_soda import (
    DATASET_ID as ZTLDB_DATASET_ID,
)
from app.connectors.ztldb_soda import (
    SOURCE_ID as ZTLDB_SOURCE_ID,
)
from app.connectors.ztldb_soda import (
    ZtldbFetchResult,
)

__all__ = [
    "ZONING_CROSSCHECK_FIELD_MAP",
    "CrosscheckReport",
    "crosscheck_lot_zoning",
    "external_observation",
]

# Profile-canonical field (PLUTO column) -> ZTLDB column. The PLUTO column
# name is the conflict entry's ``field`` because the profile's fact values
# and the analysis-readiness gate (critical column 'zonedist1') use PLUTO
# column names; each side's ORIGINAL column name stays visible in the value
# derivation text.
ZONING_CROSSCHECK_FIELD_MAP: tuple[tuple[str, str], ...] = (
    ("zonedist1", "zoning_district_1"),
    ("zonedist2", "zoning_district_2"),
    ("zonedist3", "zoning_district_3"),
    ("zonedist4", "zoning_district_4"),
    ("overlay1", "commercial_overlay_1"),
    ("overlay2", "commercial_overlay_2"),
    ("spdist1", "special_district_1"),
    ("spdist2", "special_district_2"),
    ("spdist3", "special_district_3"),
    ("ltdheight", "limited_height_district"),
    ("zonemap", "zoning_map_number"),
    ("zmcode", "zoning_map_code"),
)

_ABSENT = object()  # sentinel: column not present on the source record

_REASON_PREFIX = (
    "cross-source lot-level zoning disagreement (data reconciliation, not "
    "legal zoning adjudication; both observations preserved, no winner "
    "chosen): "
)


@dataclass(frozen=True)
class _Observation:
    source_id: str
    value: object  # normalized value, or _ABSENT
    derivation: str


@dataclass
class CrosscheckReport:
    """Typed reconciliation output.

    ``conflicts`` are contract-1.3.0 conflict entries ready for the
    builder; ``uncertainties`` are formatting-level differences (both
    values preserved; not conflicts); ``agreements`` document what was
    compared and found consistent (evidence, not silence); ``notes`` are
    contract-safe non-empty strings for
    ``reproducibility.connector_notes``.
    """

    compared_fields: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    uncertainties: list[dict] = field(default_factory=list)
    agreements: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def external_observation(
    *, source_id: str, profile_field: str, value: object, derivation: str
) -> dict:
    """Build one externally-supplied observation (e.g. a value read from an
    accepted M2-T007 zoning-features FIXTURE for the same lot). The caller
    states the exact derivation; this module never computes geometry."""
    if not source_id or not derivation:
        raise ValueError("source_id and derivation are required")
    known = {pluto_field for pluto_field, _ in ZONING_CROSSCHECK_FIELD_MAP}
    if profile_field not in known:
        raise ValueError(
            f"profile_field {profile_field!r} is not a cross-checked zoning "
            f"field (known: {sorted(known)})"
        )
    return {
        "source_id": source_id,
        "profile_field": profile_field,
        "value": value,
        "derivation": derivation,
    }


def _pluto_observation(
    result: PlutoFetchResult, column: str
) -> _Observation:
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    fact = by_field.get(column)
    if fact is None:
        return _Observation(
            source_id=PLUTO_SOURCE_ID,
            value=_ABSENT,
            derivation=(
                f"PLUTO {PLUTO_DATASET_ID} column '{column}' omitted by the "
                "SODA record (null-omission semantics; version "
                f"{result.dataset_version}, retrieved {result.retrieved_at})"
            ),
        )
    return _Observation(
        source_id=PLUTO_SOURCE_ID,
        value=fact["normalized_value"],
        derivation=(
            f"PLUTO {PLUTO_DATASET_ID} column '{column}' normalized value "
            f"(version {result.dataset_version}, retrieved "
            f"{result.retrieved_at}, provenance {fact['provenance_id']})"
        ),
    )


def _ztldb_observation(
    result: ZtldbFetchResult, column: str
) -> _Observation:
    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    fact = by_field.get(column)
    if fact is None:
        absence = next(
            (entry for entry in result.absences if entry["column"] == column),
            None,
        )
        semantics = (
            absence["semantics"]
            if absence
            else "column absent from the record"
        )
        return _Observation(
            source_id=ZTLDB_SOURCE_ID,
            value=_ABSENT,
            derivation=(
                f"ZTLDB {ZTLDB_DATASET_ID} column '{column}' omitted by the "
                f"SODA record ({semantics}; dataset rows version "
                f"{result.dataset_version}, retrieved {result.retrieved_at})"
            ),
        )
    return _Observation(
        source_id=ZTLDB_SOURCE_ID,
        value=fact["normalized_value"],
        derivation=(
            f"ZTLDB {ZTLDB_DATASET_ID} column '{column}' normalized value "
            f"(dataset rows version {result.dataset_version}, retrieved "
            f"{result.retrieved_at}, provenance {fact['provenance_id']})"
        ),
    )


def _is_blankish(value: object) -> bool:
    """Absent, explicit null, or empty string: no assigned value on this
    side. The DISTINCTION between these states is preserved in each
    observation's derivation; for comparison they all mean 'no value'."""
    return value is _ABSENT or value is None or value == ""


def _border_flag(observation: _Observation) -> object:
    """Comparison predicate for the zoning-map border flag ONLY (values are
    never rewritten): PLUTO ``zmcode`` is a Socrata checkbox (True/False);
    ZTLDB ``zoning_map_code`` is text where 'Y' is the only documented
    value. Both officially mean "the tax lot may be on the border of two or
    more zoning maps"."""
    value = observation.value
    if _is_blankish(value) or value is False:
        return False
    if value is True or value == "Y":
        return True
    return value  # unmappable representation: compares unequal to booleans


def _values_disagree(field_name: str, a: _Observation, b: _Observation) -> str | None:
    """Return None on agreement, 'conflict' or 'case_only' otherwise."""
    a_blank, b_blank = _is_blankish(a.value), _is_blankish(b.value)
    if field_name == "zmcode":
        return None if _border_flag(a) == _border_flag(b) else "conflict"
    if a_blank and b_blank:
        return None
    if a_blank != b_blank:
        return "conflict"
    if a.value == b.value:
        return None
    if (
        isinstance(a.value, str)
        and isinstance(b.value, str)
        and a.value.casefold() == b.value.casefold()
    ):
        return "case_only"
    return "conflict"


def _value_entry(observation: _Observation) -> dict:
    return {
        "source_id": observation.source_id,
        "value": None if observation.value is _ABSENT else observation.value,
        "derivation": observation.derivation,
    }


def crosscheck_lot_zoning(
    pluto_result: PlutoFetchResult,
    ztldb_result: ZtldbFetchResult,
    external_observations: list[dict] | tuple[dict, ...] = (),
) -> CrosscheckReport:
    """Compare ZTLDB lot-level zoning values against PLUTO facts (and any
    externally supplied fixture-derived observations) for the same BBL.

    Returns a :class:`CrosscheckReport`; disagreements are contract-shape
    conflict entries with ``resolution='unresolved'``. Raises ``ValueError``
    when the two results describe different properties (comparing across
    lots would fabricate a conflict).
    """
    if pluto_result.bbl != ztldb_result.bbl:
        raise ValueError(
            f"cross-check requires the same property: PLUTO result is for "
            f"BBL {pluto_result.bbl}, ZTLDB result for {ztldb_result.bbl}"
        )
    if ztldb_result.status != "ok":
        raise ValueError(
            "cross-check requires a status='ok' ZTLDB result; a no_record "
            "result carries no lot-level values to compare"
        )

    external_by_field: dict[str, list[dict]] = {}
    for entry in external_observations:
        external_by_field.setdefault(entry["profile_field"], []).append(entry)

    report = CrosscheckReport()
    for pluto_column, ztldb_column in ZONING_CROSSCHECK_FIELD_MAP:
        observations = [
            _pluto_observation(pluto_result, pluto_column),
            _ztldb_observation(ztldb_result, ztldb_column),
        ]
        for entry in external_by_field.get(pluto_column, ()):
            observations.append(
                _Observation(
                    source_id=entry["source_id"],
                    value=entry["value"],
                    derivation=entry["derivation"],
                )
            )
        report.compared_fields.append(pluto_column)

        # Skip fields absent everywhere: nothing to reconcile.
        if all(_is_blankish(obs.value) for obs in observations) and (
            pluto_column != "zmcode"
        ):
            report.agreements.append(
                {"field": pluto_column, "status": "no_value_on_any_source"}
            )
            continue

        verdicts = [
            _values_disagree(pluto_column, observations[i], observations[j])
            for i in range(len(observations))
            for j in range(i + 1, len(observations))
        ]
        if any(verdict == "conflict" for verdict in verdicts):
            report.conflicts.append(
                {
                    "field": pluto_column,
                    "values": [_value_entry(obs) for obs in observations],
                    "resolution": "unresolved",
                    "reason": (
                        _REASON_PREFIX
                        + f"sources disagree on '{pluto_column}' "
                        f"(ZTLDB column '{ztldb_column}'). The three "
                        "official presentations are distinct vintages of "
                        "the same underlying zoning facts (GIS Zoning "
                        "Features -> ZTLDB -> PLUTO); skew must stay "
                        "visible."
                    ),
                }
            )
        elif any(verdict == "case_only" for verdict in verdicts):
            report.uncertainties.append(
                {
                    "field": pluto_column,
                    "kind": "case_only_difference",
                    "values": [_value_entry(obs) for obs in observations],
                    "note": (
                        "values differ only by letter case (formatting "
                        "difference between official presentations, e.g. "
                        "'16a' vs '16A' observed live); both verbatim "
                        "values preserved; not adjudicated"
                    ),
                }
            )
        else:
            report.agreements.append(
                {
                    "field": pluto_column,
                    "status": "consistent",
                    "values": [_value_entry(obs) for obs in observations],
                }
            )

    report.notes.append(
        "ztldb_crosscheck: compared "
        f"{len(report.compared_fields)} lot-level zoning fields across "
        f"{2 + (1 if external_by_field else 0)} official presentations for "
        f"BBL {ztldb_result.bbl}: {len(report.agreements)} consistent, "
        f"{len(report.uncertainties)} formatting-only difference(s), "
        f"{len(report.conflicts)} conflict(s). Data reconciliation only - "
        "no value was adjudicated, overwritten, or dropped."
    )
    for uncertainty in report.uncertainties:
        values = ", ".join(
            f"{entry['source_id']}={entry['value']!r}"
            for entry in uncertainty["values"]
            if entry["value"] is not None
        )
        report.notes.append(
            f"ztldb_crosscheck_uncertainty: field={uncertainty['field']} "
            f"kind={uncertainty['kind']} ({values}); both verbatim values "
            "preserved; formatting-level difference, not adjudicated."
        )
    return report
