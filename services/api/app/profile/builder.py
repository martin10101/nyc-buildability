"""Connector facts -> canonical property-profile document (task M1-T005).

Builds the ONE canonical property-profile contract
(``packages/contracts/schemas/v1/property_profile.schema.json``, PRD section
32.3) from an accepted-connector :class:`~app.connectors.pluto_soda.PlutoFetchResult`.

Hard rules implemented here:

- Every fact value carries a ``provenance_ref`` that resolves to a
  ``provenance_id`` in the profile's ``provenance`` array (PRD sections 9/19;
  the schema description requires the backend to enforce this for live data,
  so the builder re-verifies referential integrity before returning).
- Coverage statuses (PRD section 12) are derived ONLY from review status and
  conflict/drift state. Connector ``confidence`` is NEVER mapped to a
  coverage label (M1-T002 G3 carry-forward F7). Nothing built from an
  unreviewed source fact may be labeled ``verified``.
- Absent columns surface as explicit ``missing_inputs`` (unknown, never
  fabricated); connector conflicts stay visible and unresolved; connector
  drift signals/notes persist into the document (M1-T002 G3 carry-forwards).
- Deterministic code only: no AI, no legal interpretation. Column bucketing
  below is presentation grouping, not legal logic.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.connectors.pluto_soda import DATASET_ID, SOURCE_ID, PlutoFetchResult

__all__ = [
    "PROFILE_CONTRACT_VERSION",
    "build_property_profile",
]

PROFILE_CONTRACT_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Deterministic PLUTO column buckets (presentation grouping only). Columns not
# listed remain fully available through the provenance array; nothing is lost.
# ---------------------------------------------------------------------------

LOT_FACT_COLUMNS: tuple[str, ...] = (
    # Lot identity columns first: bbl/borocode/borough/block/lot are lot-level
    # facts, and bucketing them here keeps identifier conflicts visible as
    # data_conflict coverage on concrete fact values (scenario S4), not only
    # in the conflicts array.
    "bbl", "borocode", "borough", "block", "lot",
    "lotarea", "lotfront", "lotdepth", "lottype", "irrlotcode", "easements",
    "landuse", "ownertype", "ownername", "assessland", "assesstot",
    "exempttot",
)

BUILDING_FACT_COLUMNS: tuple[str, ...] = (
    "bldgarea", "comarea", "resarea", "officearea", "retailarea",
    "garagearea", "strgearea", "factryarea", "otherarea", "areasource",
    "numbldgs", "numfloors", "unitsres", "unitstotal", "bldgfront",
    "bldgdepth", "bldgclass", "ext", "proxcode", "bsmtcode", "yearbuilt",
    "yearalter1", "yearalter2", "builtfar",
)

ZONING_DISTRICT_COLUMNS: tuple[str, ...] = (
    "zonedist1", "zonedist2", "zonedist3", "zonedist4",
)
OVERLAY_COLUMNS: tuple[str, ...] = ("overlay1", "overlay2")
SPECIAL_DISTRICT_COLUMNS: tuple[str, ...] = ("spdist1", "spdist2", "spdist3")

# Mapped zoning/regulatory features surfaced individually with provenance
# (PRD section 32.3: zoning districts and mapped features; landmark/flood
# flags). Values pass through verbatim-normalized; no legal meaning is
# attached here - rule applicability belongs to the rule engine (M4).
MAPPED_FEATURE_COLUMNS: tuple[str, ...] = (
    "splitzone", "ltdheight", "landmark", "histdist", "edesignum",
    "firm07_flag", "pfirm15_flag", "transitzone", "zonemap", "zmcode",
)

# Data-completeness policy (PRD section 12): lot area and the primary zoning
# district are prerequisites for ANY feasibility calculation, so their absence
# is critical; every other absent PLUTO column is missing_noncritical. This is
# a platform completeness policy, not a legal interpretation.
CRITICAL_COLUMNS: frozenset[str] = frozenset({"lotarea", "zonedist1"})

_BOROUGH_NAMES: dict[int, str] = {
    # common.schema.json borough_code grounding (Geoclient User Guide v2.0.4
    # section 2.2.1): Manhattan=1, Bronx=2, Brooklyn=3, Queens=4,
    # Staten Island=5.
    1: "Manhattan",
    2: "Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island",
}

_COVERAGE_POLICY = (
    "coverage_status is derived only from review status and conflict/drift "
    "state: unreviewed official source facts are 'conditional', facts with "
    "connector drift signals are 'unsupported', conflicting facts are "
    "'data_conflict'. Connector confidence is NEVER mapped to a coverage "
    "label and no unreviewed fact is 'verified' (PRD section 12)."
)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _drift_columns(drift_signals: list[str]) -> set[str]:
    """Column names referenced by connector drift signals of the form
    ``<kind>:<column>`` (e.g. ``non_finite_number_value:lotarea``)."""
    return {signal.split(":", 1)[1] for signal in drift_signals if ":" in signal}


def _coverage_status(fact: dict, drift_columns: set[str]) -> str:
    """PRD section 12 coverage for a single unreviewed source fact.

    NEVER derived from ``fact['confidence']`` (G3 carry-forward F7): a
    deterministic official retrieval carries confidence 1.0 and is STILL only
    'conditional' until a published rule/reviewer pipeline exists.
    """
    if fact["conflict_status"] == "conflicting":
        return "data_conflict"
    if fact["original_field_name"] in drift_columns:
        # The connector could not normalize this value (drift signal); the
        # verbatim raw value is preserved in provenance but the platform
        # cannot support calculations on it.
        return "unsupported"
    return "conditional"


def _fact_value(fact: dict, drift_columns: set[str]) -> dict:
    """property_profile fact_value: value + provenance_ref (+units), plus the
    additive coverage_status key (schema-permitted additional property)."""
    value = {
        "value": fact["normalized_value"],
        "provenance_ref": fact["provenance_id"],
        "coverage_status": _coverage_status(fact, drift_columns),
    }
    if fact.get("units") is not None:
        # fact_value.units is typed string in the contract; omit when unitless.
        value["units"] = fact["units"]
    return value


def _string_or_none(fact: dict | None) -> str | None:
    if fact is None:
        return None
    value = fact["normalized_value"]
    return value if isinstance(value, str) and value else None


def _identity(result: PlutoFetchResult, by_field: dict[str, dict]) -> dict:
    """Identity block. Only fields backed by connector facts (all present in
    the provenance array) or by the canonical BBL itself are emitted; nothing
    is guessed."""
    identity: dict = {"bbl": result.bbl}
    address: dict = {}

    normalized_address = _string_or_none(by_field.get("address"))
    if normalized_address:
        address["normalized_address"] = normalized_address

    borocode_fact = by_field.get("borocode")
    if borocode_fact is not None and borocode_fact["conflict_status"] != "conflicting":
        # A borocode that disagrees with the BBL is NEVER silently used to
        # derive identity fields: the conflict stays visible in conflicts[]
        # and as data_conflict coverage on the lot_facts entries instead.
        code = borocode_fact["normalized_value"]
        if isinstance(code, int) and not isinstance(code, bool) and code in _BOROUGH_NAMES:
            address["borough_code"] = code
            address["borough"] = _BOROUGH_NAMES[code]

    zipcode_fact = by_field.get("zipcode")
    if zipcode_fact is not None:
        zip_value = zipcode_fact["normalized_value"]
        if isinstance(zip_value, int) and not isinstance(zip_value, bool) \
                and 0 <= zip_value <= 99999:
            # Deterministic inverse of Socrata's number typing (leading zeros
            # are stripped by the source type, mirroring the BBL decimal-tail
            # rule); the verbatim raw value stays in provenance.
            address["zip_code"] = f"{zip_value:05d}"

    if address:
        identity["address"] = address

    latitude = by_field.get("latitude")
    longitude = by_field.get("longitude")
    if latitude is not None and longitude is not None:
        lat, lon = latitude["normalized_value"], longitude["normalized_value"]
        if isinstance(lat, int | float) and isinstance(lon, int | float) \
                and not isinstance(lat, bool) and not isinstance(lon, bool):
            # GeoJSON position order is [longitude, latitude].
            identity["geometry"] = {"type": "Point", "coordinates": [lon, lat]}
    return identity


def _zoning(by_field: dict[str, dict], drift_columns: set[str]) -> dict:
    def collect(columns: tuple[str, ...]) -> list[str]:
        values = []
        for column in columns:
            value = _string_or_none(by_field.get(column))
            if value is not None:
                values.append(value)
        return values

    mapped_features = []
    for column in MAPPED_FEATURE_COLUMNS:
        fact = by_field.get(column)
        if fact is None:
            continue
        feature = {"feature": column, **_fact_value(fact, drift_columns)}
        mapped_features.append(feature)

    return {
        "districts": collect(ZONING_DISTRICT_COLUMNS),
        "commercial_overlays": collect(OVERLAY_COLUMNS),
        "special_districts": collect(SPECIAL_DISTRICT_COLUMNS),
        "mapped_features": mapped_features,
    }


def _missing_inputs(result: PlutoFetchResult) -> list[dict]:
    """Absent columns and connector unknown-value notes become explicit
    missing inputs - unknown is stated, never fabricated (PRD section 9)."""
    entries: dict[str, dict] = {}
    for column in result.absent_columns:
        entries[column] = {
            "field": column,
            "criticality": "critical" if column in CRITICAL_COLUMNS else "noncritical",
            "reason": (
                "column absent from the SODA record (null-omission semantics): "
                "the value is unknown for this tax lot and is never fabricated"
            ),
        }
    for note in result.notes:
        # Connector notes carry official data-dictionary semantics for
        # present-but-unknown values (e.g. yearbuilt 0 = unknown).
        note_field = note.split(":", 1)[0].strip()
        field_map = {"numfloors_not_available": "numfloors", "yearbuilt_unknown": "yearbuilt"}
        field_name = field_map.get(note_field)
        if field_name is None:
            continue
        entries[field_name] = {
            "field": field_name,
            "criticality": "critical" if field_name in CRITICAL_COLUMNS else "noncritical",
            "reason": note,
        }
    return [entries[key] for key in sorted(entries)]


def _conflicts(result: PlutoFetchResult) -> list[dict]:
    """Connector identifier conflicts -> contract conflict entries. Both
    values stay visible verbatim; resolution is always 'unresolved' here -
    the platform never silently resolves official-data disagreement."""
    conflicts = []
    for conflict in result.conflicts:
        conflicts.append(
            {
                "field": conflict["field"],
                "values": [
                    {
                        "source_id": SOURCE_ID,
                        "value": conflict["bbl_derived_value"],
                        "derivation": "derived from the canonical BBL digits",
                    },
                    {
                        "source_id": SOURCE_ID,
                        "value": conflict["component_value_raw"],
                        "derivation": f"record field '{conflict['field']}' verbatim",
                    },
                ],
                "resolution": "unresolved",
                "reason": conflict.get("reason"),
            }
        )
    return conflicts


def _assert_provenance_integrity(profile: dict) -> None:
    """Backend-side enforcement of the schema's referential-integrity rule:
    every provenance_ref must resolve to a provenance_id (PRD sections 9/19).
    By construction this cannot fail; if it ever does, failing loudly beats
    exporting a fact without provenance."""
    provenance_ids = {record["provenance_id"] for record in profile["provenance"]}
    refs = [
        fact["provenance_ref"]
        for section in ("lot_facts", "existing_building_facts")
        for fact in profile[section].values()
    ]
    refs.extend(
        feature["provenance_ref"] for feature in profile["zoning"]["mapped_features"]
    )
    dangling = sorted(set(refs) - provenance_ids)
    if dangling:
        raise RuntimeError(
            f"property profile has dangling provenance_ref(s): {dangling}; "
            "refusing to emit a fact without resolvable provenance"
        )


def build_property_profile(
    result: PlutoFetchResult,
    *,
    clock: Callable[[], datetime] = _utc_now,
) -> dict:
    """Build the canonical property-profile document for a successful fetch.

    Args:
        result: connector result with ``status == "ok"``. ``no_match`` and
            typed failures are HTTP-layer states, not profiles.
        clock: injectable UTC clock for deterministic tests.

    Returns:
        A dict that validates against property_profile.schema.json v1. The
        additive keys ``data_completeness``, ``reproducibility``, and
        per-fact ``coverage_status`` are schema-permitted additional
        properties (same additive-extension pattern the accepted M1-T002
        connector uses on source_fact); the required v1 field set is complete
        and unchanged.
    """
    if result.status != "ok":
        raise ValueError(
            f"build_property_profile requires a status='ok' result, got "
            f"{result.status!r}; no_match/failure states are handled by the API layer"
        )

    by_field = {fact["original_field_name"]: fact for fact in result.facts}
    drift_columns = _drift_columns(result.drift_signals)

    def facts_for(columns: tuple[str, ...]) -> dict:
        section = {}
        for column in columns:
            fact = by_field.get(column)
            if fact is not None:
                section[column] = _fact_value(fact, drift_columns)
        return section

    missing_inputs = _missing_inputs(result)
    if any(entry["criticality"] == "critical" for entry in missing_inputs):
        data_completeness = "missing_critical"
    elif missing_inputs:
        data_completeness = "missing_noncritical"
    else:
        data_completeness = "complete"

    profile = {
        "profile_version": {
            "contract_version": PROFILE_CONTRACT_VERSION,
            # Stateless build: profile persistence (and with it a monotonic
            # per-property revision counter) arrives with the analysis-run
            # tables in M2; until then every response is revision 1 of a
            # freshly built document.
            "profile_revision": 1,
            "generated_at": _rfc3339(clock()),
        },
        "identity": _identity(result, by_field),
        "lot_facts": facts_for(LOT_FACT_COLUMNS),
        "existing_building_facts": facts_for(BUILDING_FACT_COLUMNS),
        "zoning": _zoning(by_field, drift_columns),
        "project_intent": {
            "objectives": [],
            "notes": (
                "Development objectives are selected at analysis creation "
                "(PRD section 5); this profile endpoint returns official-"
                "source facts only."
            ),
        },
        # Every connector fact goes into provenance verbatim (source_fact v1
        # records), including identity/zoning source fields that also feed
        # derived sections above.
        "provenance": list(result.facts),
        "missing_inputs": missing_inputs,
        "conflicts": _conflicts(result),
        "user_confirmations": [],
        # ------------------------------------------------------------------
        # Additive (schema-permitted) extensions:
        # ------------------------------------------------------------------
        "data_completeness": data_completeness,
        "reproducibility": {
            "correlation_id": result.correlation_id,
            "source_id": SOURCE_ID,
            "dataset_id": DATASET_ID,
            "dataset_version": result.dataset_version,
            "request_url": result.request_url,
            "retrieved_at": result.retrieved_at,
            "record_count": result.record_count,
            "drift_signals": list(result.drift_signals),
            "connector_notes": list(result.notes),
            "coverage_policy": _COVERAGE_POLICY,
        },
    }
    _assert_provenance_integrity(profile)
    return profile
