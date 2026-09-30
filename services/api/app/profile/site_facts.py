"""Property-profile values -> site_fact v1 records (queue item B-02; plan M1-07, section 4).

Maps the site values the profile builder (``app.profile.builder``) already produces to
records shaped by ``packages/contracts/schemas/v1/site_fact.schema.json``: each record
has a value and unit, or an explicit unknown; its measurement rank and label
(``app.profile.measurement``); and its source, taken from the PLUTO ``source_fact``
record that the builder put in ``profile["provenance"]``.

Library only. Nothing calls it yet: no route, and no change to the property_profile
contract or its output. A later Lane C task wires it in behind a flag.

Rules (plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md``):

- A known PLUTO value is rank ``city_records`` (section 4 rank 2: "City-recorded
  dimensions and area (PLUTO, DOF)"). Its source records the dataset, the dataset
  version, ``retrieved_at``, the exact request URL (``query_ref``) and the
  ``provenance_id`` of the source record (``provenance_refs``). That record also holds
  the PLUTO field name. The contract's source object has no field slot, so the field
  name is also given in the note.
- Unknown stays unknown: value and unit are null, the rank is ``unknown``, and
  ``blocks`` names what the value blocks (section 9). It is never 0. A zero PLUTO
  dimension is unknown, because a lot has no zero area, frontage or depth. For
  example, the official fixture F05 records lotfront and lotdepth as 0.
- A value is also unknown when:
  - PLUTO has no value for it;
  - the value is not a positive number, or its unit is not the documented one;
  - the connector flagged drift on it;
  - a conflict entry names its field (the note repeats the disagreeing values, so the
    conflict stays visible);
  - the lot's identity fields conflict, which means the profile may describe two lots.
- Lot type: the PLUTO LotType code list is not verified in this repository
  (``docs/research/pluto-mappluto-2026-07-16.md`` OQ-5 residual), and a tax-lot code
  is not the zoning lot type. Lot type therefore stays unknown here. It comes from the
  tax-map outline (queue item B-03, task M1-13) or from an entry.
- Frontage: PLUTO LotFront is one number for the whole lot, and it names no street.
  The contract records frontage per street, so LotFront is returned only as a recorded
  reference. Each street the caller names gets an unknown frontage.
- Existing zoning floor area may come only from a Buildings Department filing, a
  certificate of occupancy, an entry, or a stated assumption. It is never taken from
  PLUTO/DOF building area (section 3 step 4, task M2-07). The builder reads no filing
  yet, so the value is unknown. PLUTO BldgArea is returned only as a reference.
- Zoning districts and commercial overlays: one fact for each PLUTO zonedist1-4 and
  overlay1-2 value that is present. A missing zonedist1 gives an unknown district. A
  missing zonedist2-4 or overlay gives no fact, because SODA omits null fields, so its
  absence means "none or unknown". The builder leaves these columns out of
  completeness for the same reason.

Pure, deterministic code: no I/O, no legal logic, and the profile is never mutated.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from app.connectors.pluto_soda import DATASET_ID as PLUTO_DATASET_ID
from app.connectors.pluto_soda import SOURCE_ID as PLUTO_SOURCE_ID
from app.profile.measurement import RANK_CITY_RECORDS, RANK_UNKNOWN, measurement

__all__ = [
    "BLOCKS",
    "PLUTO_DATASET_NAME",
    "SITE_FACT_CONTRACT_VERSION",
    "SiteFactSet",
    "build_site_facts",
]

SITE_FACT_CONTRACT_VERSION = "1.0.0"
PLUTO_DATASET_NAME = f"PLUTO ({PLUTO_DATASET_ID})"

# What each value blocks while it is unknown (site_fact ``blocked_output`` vocabulary).
# This is a conservative platform dependency map: it blocks more rather than less. It
# makes no rule claim; Lane A's rule engine owns the exact dependencies.
# existing_zoning_floor_area follows plan section 3 step 4: without it, the remaining
# capacity is not available, but the full-site allowance still shows.
_ZONING_OUTPUTS = (
    "floor_area_allowance",
    "remaining_floor_area",
    "permitted_envelope",
    "building_option",
    "existing_building_paths",
    "unit_estimate",
)
BLOCKS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "lot_area": (
        "floor_area_allowance",
        "remaining_floor_area",
        "permitted_envelope",
        "building_option",
        "unit_estimate",
    ),
    "lot_frontage": ("permitted_envelope", "building_option", "geometry"),
    "lot_depth": ("permitted_envelope", "building_option", "geometry"),
    "lot_type": ("permitted_envelope", "building_option"),
    "zoning_district": _ZONING_OUTPUTS,
    "commercial_overlay": _ZONING_OUTPUTS,
    "existing_zoning_floor_area": ("remaining_floor_area", "existing_building_paths"),
})

# PLUTO unit strings (connector FIELD_UNITS, data dictionary p.21-22 and p.29) -> the
# contract unit. A value whose recorded unit differs is not used.
_UNITS: Mapping[str, tuple[str, str]] = MappingProxyType({
    "lotarea": ("square feet", "square_feet"),
    "bldgarea": ("square feet", "square_feet"),
    "lotfront": ("feet", "feet"),
    "lotdepth": ("feet", "feet"),
})

_IDENTITY_FIELDS = frozenset({"bbl", "borocode", "block", "lot"})
_ZONING_DISTRICT_COLUMNS = ("zonedist1", "zonedist2", "zonedist3", "zonedist4")
_OVERLAY_COLUMNS = ("overlay1", "overlay2")
_MAX_NOTE_VALUES_CHARS = 300


@dataclass(frozen=True)
class SiteFactSet:
    """The site_fact records for one lot, plus the city-recorded reference values.

    ``facts`` are site_fact v1 documents. ``references`` are NOT contract documents:
    they hold city-recorded values that are shown for reference only (PLUTO building
    area and whole-lot frontage), each with a measurement and a site_fact-shaped
    source, and marked ``"use": "reference_only"``."""

    bbl: str
    facts: tuple[dict, ...]
    references: tuple[dict, ...]

    def of_key(self, key: str) -> tuple[dict, ...]:
        return tuple(fact for fact in self.facts if fact["key"] == key)

    def unknown_facts(self) -> tuple[dict, ...]:
        return tuple(fact for fact in self.facts if fact["measurement"]["rank"] == RANK_UNKNOWN)


@dataclass(frozen=True)
class _ProfileView:
    bbl: str
    pluto: Mapping[str, Mapping[str, Any]]
    duplicated: frozenset[str]
    drift_columns: frozenset[str]
    conflicts: Mapping[str, tuple[Mapping[str, Any], ...]]
    coverage: Mapping[str, Any]
    request_url: str | None
    checked_source: dict | None

    @property
    def identity_conflict(self) -> bool:
        return any(field in self.conflicts for field in _IDENTITY_FIELDS)


@dataclass(frozen=True)
class _Reading:
    value: Any
    source: dict | None
    problem: str | None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _pluto_source(
    *,
    dataset_version: Any,
    retrieved_at: Any,
    query_ref: Any,
    provenance_id: Any = None,
) -> dict | None:
    """A site_fact ``city_dataset`` source for PLUTO, or None when the retrieval time
    or the request is not recorded (a known value is never given an incomplete
    source)."""
    if _text(retrieved_at) is None or _text(query_ref) is None:
        return None
    source = {
        "kind": "city_dataset",
        "dataset": PLUTO_DATASET_NAME,
        "dataset_version": _text(dataset_version),
        "retrieved_at": retrieved_at,
        "query_ref": query_ref,
        "document_ref": None,
        "statement": None,
    }
    if _text(provenance_id) is not None:
        source["provenance_refs"] = [provenance_id]
    return source


def _view(profile: Any) -> _ProfileView:
    if not isinstance(profile, Mapping):
        raise ValueError("build_site_facts needs a built property-profile document")
    bbl = _text(_mapping(profile.get("identity")).get("bbl"))
    if bbl is None:
        raise ValueError("the property profile has no identity.bbl")

    pluto: dict[str, Mapping[str, Any]] = {}
    duplicated: set[str] = set()
    for record in profile.get("provenance") or ():
        if not isinstance(record, Mapping) or record.get("source_id") != PLUTO_SOURCE_ID:
            continue
        if record.get("bbl") != bbl:
            continue
        field = record.get("original_field_name")
        if field in pluto:
            duplicated.add(field)
        pluto[field] = record

    reproducibility = _mapping(profile.get("reproducibility"))
    drift_columns = frozenset(
        signal.split(":", 1)[1]
        for signal in reproducibility.get("drift_signals") or ()
        if isinstance(signal, str) and ":" in signal
    )
    conflicts: dict[str, list[Mapping[str, Any]]] = {}
    for conflict in profile.get("conflicts") or ():
        if isinstance(conflict, Mapping) and isinstance(conflict.get("field"), str):
            conflicts.setdefault(conflict["field"], []).append(conflict)
    coverage = {
        column: _mapping(fact_value).get("coverage_status")
        for section in ("lot_facts", "existing_building_facts")
        for column, fact_value in _mapping(profile.get(section)).items()
    }
    request_url = _text(reproducibility.get("request_url"))
    checked_source = None
    if reproducibility.get("source_id") == PLUTO_SOURCE_ID:
        checked_source = _pluto_source(
            dataset_version=reproducibility.get("dataset_version"),
            retrieved_at=reproducibility.get("retrieved_at"),
            query_ref=request_url,
        )
    return _ProfileView(
        bbl=bbl,
        pluto=MappingProxyType(pluto),
        duplicated=frozenset(duplicated),
        drift_columns=drift_columns,
        conflicts=MappingProxyType({k: tuple(v) for k, v in conflicts.items()}),
        coverage=MappingProxyType(coverage),
        request_url=request_url,
        checked_source=checked_source,
    )


def _conflict_text(column: str, conflicts: Sequence[Mapping[str, Any]]) -> str:
    parts = []
    for conflict in conflicts:
        values = ", ".join(
            f"{_mapping(entry).get('source_id')}={_mapping(entry).get('value')!r}"
            for entry in conflict.get("values") or ()
        )
        parts.append(f"{values} (resolution: {conflict.get('resolution')})")
    text = "; ".join(parts)
    if len(text) > _MAX_NOTE_VALUES_CHARS:
        text = text[:_MAX_NOTE_VALUES_CHARS] + "..."
    return f"Sources disagree on PLUTO {column}: {text}."


def _problem(view: _ProfileView, column: str, record: Mapping[str, Any]) -> str | None:
    """Why a present PLUTO value cannot be used, or None when it can."""
    if view.identity_conflict:
        return (
            "The lot's identity fields (BBL, borough, block, lot) conflict, so this "
            "profile may describe two lots."
        )
    if column in view.duplicated:
        return f"PLUTO returned more than one {column} value."
    if column in view.drift_columns or view.coverage.get(column) == "unsupported":
        return f"The PLUTO {column} value could not be read (connector drift signal)."
    if column in view.conflicts:
        return _conflict_text(column, view.conflicts[column])
    status = record.get("conflict_status")
    if status != "none" or view.coverage.get(column) == "data_conflict":
        return f"PLUTO {column} has conflict status {status!r}."
    return None


def _is_positive_number(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _read(view: _ProfileView, column: str, *, numeric: bool) -> _Reading:
    """One PLUTO column read as a usable value, or with the plain reason it is not."""
    record = view.pluto.get(column)
    if record is None:
        return _Reading(None, view.checked_source, f"PLUTO has no {column} value for this lot.")
    source = _pluto_source(
        dataset_version=record.get("dataset_version"),
        retrieved_at=record.get("retrieved_at"),
        query_ref=record.get("request_url") or view.request_url,
        provenance_id=record.get("provenance_id"),
    )
    problem = _problem(view, column, record)
    if problem is None and source is None:
        problem = f"The PLUTO {column} record has no retrieval time or request."
    value = record.get("normalized_value")
    if problem is None and numeric:
        if not _is_positive_number(value):
            problem = (
                f"PLUTO {column} is {value!r}, not a positive number; a zero or missing "
                "dimension is unknown, never 0."
            )
        elif record.get("units") != _UNITS[column][0]:
            problem = f"PLUTO {column} unit {record.get('units')!r} is not the documented unit."
    if problem is None and not numeric and _text(value) is None:
        problem = f"PLUTO {column} is empty."
    if problem is not None:
        return _Reading(None, source, problem)
    return _Reading(value, source, None)


def _record(
    view: _ProfileView,
    key: str,
    fact_id: str,
    *,
    value: Any,
    unit: str | None,
    source: dict | None,
    note: str,
    street: str | None = None,
) -> dict:
    known = value is not None
    return {
        "contract_version": SITE_FACT_CONTRACT_VERSION,
        "fact_id": fact_id,
        "key": key,
        "lot_bbl": view.bbl,
        "street": street,
        "value": value,
        "unit": unit if known else None,
        "measurement": measurement(RANK_CITY_RECORDS if known else RANK_UNKNOWN),
        "source": source,
        "blocks": [] if known else list(BLOCKS[key]),
        # Plan section 3 step 3: each site value "can be edited"; an edit becomes a new
        # 'entered' / 'survey_entered' fact, never an in-place change of this one.
        "editable": True,
        "note": note,
    }


def _dimension(view: _ProfileView, key: str, column: str) -> dict:
    reading = _read(view, column, numeric=True)
    if reading.problem is None:
        note = f"From PLUTO field '{column}'."
    else:
        note = reading.problem
    return _record(
        view,
        key,
        f"{view.bbl}:{key}",
        value=reading.value,
        unit=_UNITS[column][1],
        source=reading.source,
        note=note,
    )


def _frontages(view: _ProfileView, streets: Sequence[str]) -> list[dict]:
    reading = _read(view, "lotfront", numeric=True)
    if reading.problem is None:
        recorded = (
            f"City records give one lot frontage ({reading.value} ft, PLUTO field "
            "'lotfront') without naming a street"
        )
    else:
        recorded = f"No usable city-recorded frontage ({reading.problem.rstrip('.')})"
    return [
        _record(
            view,
            "lot_frontage",
            f"{view.bbl}:lot_frontage:{street}",
            value=None,
            unit=None,
            source=reading.source,
            note=(
                f"{recorded}, so the frontage on {street} is not taken from city "
                "records; it comes from the tax-map outline or an entry."
            ),
            street=street,
        )
        for street in streets
    ]


def _lot_type(view: _ProfileView) -> dict:
    record = view.pluto.get("lottype")
    if record is None:
        source = view.checked_source
        recorded = "PLUTO has no lottype value for this lot."
    else:
        source = _pluto_source(
            dataset_version=record.get("dataset_version"),
            retrieved_at=record.get("retrieved_at"),
            query_ref=record.get("request_url") or view.request_url,
            provenance_id=record.get("provenance_id"),
        )
        recorded = (
            f"PLUTO records LotType code {record.get('normalized_value')!r}; its code "
            "list is not verified here and a tax-lot code is not the zoning lot type."
        )
    return _record(
        view,
        "lot_type",
        f"{view.bbl}:lot_type",
        value=None,
        unit=None,
        source=source,
        note=f"{recorded} Lot type comes from the tax-map outline or an entry.",
    )


def _text_facts(
    view: _ProfileView, key: str, columns: Sequence[str], *, first_required: bool
) -> list[dict]:
    facts = []
    for index, column in enumerate(columns, start=1):
        if column not in view.pluto and not (first_required and index == 1):
            continue
        reading = _read(view, column, numeric=False)
        facts.append(
            _record(
                view,
                key,
                f"{view.bbl}:{key}:{index}",
                value=reading.value,
                unit=None,
                source=reading.source,
                note=reading.problem or f"From PLUTO field '{column}'.",
            )
        )
    return facts


def _existing_zoning_floor_area(view: _ProfileView) -> dict:
    return _record(
        view,
        "existing_zoning_floor_area",
        f"{view.bbl}:existing_zoning_floor_area",
        value=None,
        unit=None,
        # The contract admits only a filing, an entry or an assumption here, never a
        # city dataset, so no source was checked and none is named.
        source=None,
        note=(
            "Needs existing zoning floor area: from a Buildings Department filing or "
            "certificate of occupancy, or entered as a stated assumption. City-recorded "
            "building area is never used for it."
        ),
    )


def _references(view: _ProfileView) -> list[dict]:
    references = []
    for key, column, note in (
        (
            "recorded_building_area",
            "bldgarea",
            "City-recorded building area (PLUTO field 'bldgarea'), for reference only: "
            "it is not zoning floor area and is never subtracted.",
        ),
        (
            "recorded_lot_frontage",
            "lotfront",
            "City-recorded lot frontage (PLUTO field 'lotfront'), for reference only: "
            "it names no street, so it is not a per-street frontage.",
        ),
    ):
        reading = _read(view, column, numeric=True)
        if reading.problem is not None:
            continue
        references.append({
            "key": key,
            "lot_bbl": view.bbl,
            "value": reading.value,
            "unit": _UNITS[column][1],
            "measurement": measurement(RANK_CITY_RECORDS),
            "source": reading.source,
            "use": "reference_only",
            "note": note,
        })
    return references


def _checked_streets(frontage_streets: Sequence[str]) -> tuple[str, ...]:
    if isinstance(frontage_streets, str):
        raise ValueError("frontage_streets must be a sequence of street names, not one string")
    streets = tuple(frontage_streets)
    for street in streets:
        if _text(street) is None:
            raise ValueError(f"frontage street names must be non-empty text, got {street!r}")
    if len(set(streets)) != len(streets):
        raise ValueError("frontage street names must be unique")
    return streets


def build_site_facts(
    profile: Mapping[str, Any], *, frontage_streets: Sequence[str] = ()
) -> SiteFactSet:
    """site_fact v1 records for the lot a built property profile describes.

    Args:
        profile: a document built by ``app.profile.builder.build_property_profile``.
            It is read, never changed.
        frontage_streets: street names the lot fronts (from a later geometry step).
            Each gets a ``lot_frontage`` fact, which is unknown because city records
            give no per-street frontage.

    Returns:
        A :class:`SiteFactSet` with facts in a fixed order: lot area, frontages, lot
        depth, lot type, zoning districts, commercial overlays, and existing zoning
        floor area. It also carries the reference-only values.

    Raises:
        ValueError: the profile has no ``identity.bbl``, or a street name is blank or
            repeated.
    """
    streets = _checked_streets(frontage_streets)
    view = _view(profile)
    facts = [
        _dimension(view, "lot_area", "lotarea"),
        *_frontages(view, streets),
        _dimension(view, "lot_depth", "lotdepth"),
        _lot_type(view),
        *_text_facts(view, "zoning_district", _ZONING_DISTRICT_COLUMNS, first_required=True),
        *_text_facts(view, "commercial_overlay", _OVERLAY_COLUMNS, first_required=False),
        _existing_zoning_floor_area(view),
    ]
    return SiteFactSet(bbl=view.bbl, facts=tuple(facts), references=tuple(_references(view)))
